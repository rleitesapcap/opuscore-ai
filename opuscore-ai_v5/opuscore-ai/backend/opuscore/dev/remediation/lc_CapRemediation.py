"""
===============================================================================
 lc_CapRemediation.py  —  O MOTOR DE REMEDIAÇÃO (Etapa 2, o coração da solução)
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    É o cérebro da operação: pega cada arquivo de código ABAP (já limpo pela
    Etapa 1), usa a Inteligência Artificial para encontrar o que precisa mudar
    para rodar no S/4HANA, e grava o código corrigido — de forma segura.

COMO ELE PROCESSA CADA ARQUIVO (a "linha de montagem" interna):
    1. LIMPA e DETECTA        : descobre o tipo do arquivo (programa, classe...)
                                e qual é o símbolo de comentário.
    2. CORTA EM PEDAÇOS        : divide o programa em partes menores (as
                                sub-rotinas), para a IA analisar uma por vez.
    3. FUNIL DE 3 ESTÁGIOS     : para cada pedaço —
         a) TRIAGEM (IA barata): "precisa mexer aqui? sim/não";
         b) ANÁLISE (IA cara)  : produz a LISTA de correções (em JSON),
                                consultando a base de boas práticas (RAG);
         c) APLICAÇÃO (sem IA) : o Python aplica as correções com regras rígidas.
    4. NOMENCLATURA (opcional) : uma passada extra que audita os NOMES usados no
                                código contra o padrão do projeto (o Workbook).
    5. MONTA O ARQUIVO FINAL   : coloca o carimbo da Capgemini no topo, o
                                cabeçalho, e grava o resultado em ./remediated.

AS TRÊS CATEGORIAS DE ACHADO (como aparecem no código corrigido):
    - MODIFICATION (troca)   : o código foi alterado. Mostra o "Antes" (o código
                              original) dentro de um bloco BEGIN/END OF MODIFICATION.
    - MANUAL REVIEW (revisão): a IA não altera; só marca "reveja isto à mão"
                              (ex.: coisas de modelo de dados, decisões de arquitetura).
    - WARNING (aviso)        : desvio de boa prática. O código NÃO é alterado; logo
                              abaixo do aviso vem o "código recomendado", comentado,
                              como sugestão — o desenvolvedor decide se aplica.

AS GARANTIAS DE SEGURANÇA (por que dá para confiar):
    - A IA nunca reescreve o arquivo inteiro: ela só diz "troque ISTO por AQUILO".
    - O Python só aplica uma troca se o trecho original ("âncora") for encontrado
      de forma exata e única; senão, RECUSA (nunca corrompe o código).
    - Um PERFORM (chamada de sub-rotina) nunca é removido automaticamente.
    - Texto/comentário nunca "vaza" para dentro do código executável.

ROBUSTEZ (as melhorias operacionais desta versão):
    - Processa VÁRIOS arquivos em paralelo (mais rápido).
    - Tenta de novo automaticamente se uma chamada à IA falhar (retry).
    - Esconde o WORKSPACE_ID nos arquivos de saída (segurança).
    - Valida a configuração no início (avisa cedo se algo está errado).
    - Pode PULAR arquivos já processados (permite retomar um lote interrompido).

COMO USAR:
    Normalmente é o run_pipeline.py que chama este arquivo. Mas dá para rodar só
    ele:   python lc_CapRemediation.py
    Ele lê de ./input e grava em ./remediated.

-------------------------------------------------------------------------------
 REFERÊNCIA DE CONFIGURAÇÃO (via .env — tudo opcional):
   SAP_PACKAGE                  nome do pacote SAP (padrão global)
   REMEDIATION_CHUNKING         auto | on | off            (padrão auto)
   REMEDIATION_WHOLE_LIMIT      <chars>                    (padrão 12000)
   REMEDIATION_CHUNK_CHARS      <chars>                    (padrão 6000)
   ENABLE_TRIAGE                true | false               (padrão true)
   ENABLE_NAMING_CHECK          true | false               (padrão true)
   LLM_MODEL_MAIN               modelo da análise (IA cara)
   LLM_MODEL_TRIAGE             modelo da triagem (IA barata)
   LLM_MODEL_NAMING             modelo da nomenclatura (padrão = MAIN)
   REMEDIATION_MAX_WORKERS      <int>  arquivos em paralelo (padrão 4)
   REMEDIATION_RETRY_ATTEMPTS   <int>  tentativas por chamada (padrão 4)
   REMEDIATION_CALL_TIMEOUT_S   <int>  tempo-limite por chamada (padrão 120)
   NAMING_SOURCE_CHAR_LIMIT     <chars>                    (padrão 40000)
   REMEDIATION_SKIP_EXISTING    true | false  pular já feitos (padrão false)

 Pastas: fontes em ./input, saídas em ./output.
===============================================================================
"""

from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import re
import textwrap
import uuid
import glob
from datetime import datetime
from typing import Optional

import tenacity
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from abap_chunker import (
    chunk_for_analysis, extract_global_context, verify_roundtrip, summarize,
)
from analyze import prefilter_unit


# ------------------------------------------------------------------------------
# Logging (thread-safe; replaces bare print() calls from v7)
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------------------
load_dotenv()

LLM_API_KEY  = os.getenv("LLM_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID")

if not LLM_API_KEY or not WORKSPACE_ID:
    raise EnvironmentError("LLM_API_KEY and WORKSPACE_ID must be defined in .env")

LLM_BASE_URL      = os.getenv("LLM_BASE_URL", "https://openai.generative.engine.capgemini.com/v1")
LLM_MODEL_MAIN    = os.getenv("LLM_MODEL_MAIN",    "us.anthropic.claude-sonnet-4-20250514-v1:0")
LLM_MODEL_TRIAGE  = os.getenv("LLM_MODEL_TRIAGE",  "anthropic.claude-haiku-4-5-20251001-v1:0")
LLM_MODEL_NAMING  = os.getenv("LLM_MODEL_NAMING",  LLM_MODEL_MAIN)   # ← v8: separate model
LLM_MAX_TOKENS    = int(os.getenv("LLM_MAX_TOKENS", "20192"))

REMEDIATION_INPUT_DIR  = os.getenv("REMEDIATION_INPUT_DIR",  "input")
REMEDIATION_OUTPUT_DIR = os.getenv("REMEDIATION_OUTPUT_DIR", "output")

SAP_TARGET_VERSION = os.getenv("SAP_TARGET_VERSION", "SAP S/4HANA 2025 (Private Edition)")
ATC_CHECK_VARIANT  = os.getenv("ATC_CHECK_VARIANT",  "S4HANA_READINESS")

SAP_PACKAGE = os.getenv("SAP_PACKAGE", "").strip()

REMEDIATION_CHUNKING     = os.getenv("REMEDIATION_CHUNKING",   "auto").strip().lower()
WHOLE_SOURCE_CHAR_LIMIT  = int(os.getenv("REMEDIATION_WHOLE_LIMIT", "12000"))
REMEDIATION_CHUNK_CHARS  = int(os.getenv("REMEDIATION_CHUNK_CHARS", "6000"))
ENABLE_TRIAGE            = os.getenv("ENABLE_TRIAGE",       "true").strip().lower() == "true"

MAX_MARK_OCCURRENCES = int(os.getenv("REMEDIATION_MAX_MARK_OCCURRENCES", "10"))

NAMING_WORKBOOK_NAME    = os.getenv("NAMING_WORKBOOK_NAME",  "Workbook_ABAP_Move2S4_Final.docx")
ENABLE_NAMING_CHECK     = os.getenv("ENABLE_NAMING_CHECK",  "true").strip().lower() == "true"
NAMING_SOURCE_CHAR_LIMIT = int(os.getenv("NAMING_SOURCE_CHAR_LIMIT", "40000"))  # ← v8

# v8: parallel processing
REMEDIATION_MAX_WORKERS    = int(os.getenv("REMEDIATION_MAX_WORKERS",    "4"))
REMEDIATION_RETRY_ATTEMPTS = int(os.getenv("REMEDIATION_RETRY_ATTEMPTS", "4"))
REMEDIATION_CALL_TIMEOUT_S = int(os.getenv("REMEDIATION_CALL_TIMEOUT_S", "120"))
REMEDIATION_SKIP_EXISTING  = (                                                   # ← v8 idempotency
    os.getenv("REMEDIATION_SKIP_EXISTING", "false").strip().lower() == "true"
)

_NON_CHUNKABLE_EXT = {"asddls", "ddls", "srvd", "bdef", "intf"}

_DEFAULT_RAG_DOCUMENTS = (
"Abap RAP.pdf","CONV_OP2025.pdf","Clean core extensibility for SAP S_4HANA Cloud.pdf",
"CustomCodeMigration_EndToEnd.pdf","Extend SAP S_4HANA in the cloud and on premise with ABAP based extensions.pdf",
"From Classic ABAP to ABAP.pdf","LEROY_EXP_ARQ_Plano de migração ECC-EWM x S4HANA_260513_v1.pptx,SIMPL_OP2023-V1.pdf",
"Workbook ABAP_Move2S4_Final.docx"
)
RAG_DOCUMENTS = [
    name.strip()
    for name in os.getenv("RAG_DOCUMENTS", _DEFAULT_RAG_DOCUMENTS).split(",")
    if name.strip()
]
RAG_KNOWLEDGE_BASE = RAG_DOCUMENTS + [NAMING_WORKBOOK_NAME]


# ------------------------------------------------------------------------------
# v8: startup config validation — fail fast before any API call
# ------------------------------------------------------------------------------
# =============================================================================
# CONFIGURAÇÃO E VALIDAÇÃO
# Confere, logo no início, se os números e opções do .env fazem sentido —
# assim, se algo estiver errado, você é avisado ANTES de gastar tempo/IA.
# =============================================================================
def _validate_config() -> None:
    """Raise ValueError for any configuration that would cause a silent failure."""
    errors: list[str] = []

    def _check_positive(name: str, value: int) -> None:
        if value <= 0:
            errors.append(f"{name} must be > 0 (got {value})")

    def _check_enum(name: str, value: str, choices: set[str]) -> None:
        if value not in choices:
            errors.append(f"{name} must be one of {sorted(choices)} (got '{value}')")

    _check_positive("LLM_MAX_TOKENS",             LLM_MAX_TOKENS)
    _check_positive("REMEDIATION_WHOLE_LIMIT",     WHOLE_SOURCE_CHAR_LIMIT)
    _check_positive("REMEDIATION_CHUNK_CHARS",     REMEDIATION_CHUNK_CHARS)
    _check_positive("REMEDIATION_MAX_MARK_OCCURRENCES", MAX_MARK_OCCURRENCES)
    _check_positive("NAMING_SOURCE_CHAR_LIMIT",    NAMING_SOURCE_CHAR_LIMIT)
    _check_positive("REMEDIATION_MAX_WORKERS",     REMEDIATION_MAX_WORKERS)
    _check_positive("REMEDIATION_RETRY_ATTEMPTS",  REMEDIATION_RETRY_ATTEMPTS)
    _check_positive("REMEDIATION_CALL_TIMEOUT_S",  REMEDIATION_CALL_TIMEOUT_S)

    _check_enum("REMEDIATION_CHUNKING", REMEDIATION_CHUNKING, {"auto", "on", "off"})

    if REMEDIATION_CHUNK_CHARS > WHOLE_SOURCE_CHAR_LIMIT:
        errors.append(
            f"REMEDIATION_CHUNK_CHARS ({REMEDIATION_CHUNK_CHARS}) > "
            f"REMEDIATION_WHOLE_LIMIT ({WHOLE_SOURCE_CHAR_LIMIT}); "
            "chunking would never activate in 'auto' mode"
        )

    if errors:
        raise ValueError(
            "Configuration errors detected:\n" + "\n".join(f"  • {e}" for e in errors)
        )


# ------------------------------------------------------------------------------
# Comment styles per SAP object type
# ------------------------------------------------------------------------------
COMMENT_STYLES = {
    'asddls': '--', 'ddls': '--', 'srvd': '--', 'bdef': '--',
    'abap': '"', 'prog': '"', 'reps': '"',
    'clas': '"', 'intf': '"',
    'txt': '"',
}


# =============================================================================
# DETECÇÃO DO TIPO DE ARQUIVO
# Descobre se é programa, classe, interface... e qual é o símbolo de
# comentário daquele tipo (em ABAP clássico é ", em CDS é //).
# =============================================================================
def get_file_type_and_comment_style(filename: str):
    _, ext = os.path.splitext(filename)
    ext = ext.lower().lstrip('.')
    comment_style = COMMENT_STYLES.get(ext, '"')
    file_type_map = {
        'asddls': 'CDS View', 'ddls': 'DDL Source', 'srvd': 'Service Definition',
        'bdef': 'Behavior Definition', 'abap': 'ABAP Program', 'prog': 'ABAP Program',
        'reps': 'ABAP Report', 'clas': 'ABAP Class', 'intf': 'ABAP Interface',
        'txt': 'ABAP',
    }
    file_type = file_type_map.get(ext, 'ABAP')
    return file_type, comment_style, ext


def resolve_package(file_path: str) -> str:
    base, _ = os.path.splitext(file_path)
    sidecar = base + ".pkg"
    if os.path.isfile(sidecar):
        try:
            with open(sidecar, "r", encoding="utf-8") as f:
                val = f.read().strip()
            if val:
                return val
        except Exception:
            pass
    return SAP_PACKAGE


def _rag_source_list() -> str:
    return "\n".join(f"    - {doc}" for doc in RAG_KNOWLEDGE_BASE)


# v8: masked credential for output files
def _mask_workspace_id() -> str:
    """Return first 8 chars of WORKSPACE_ID followed by '…' (never the full value)."""
    return (WORKSPACE_ID[:8] + "…") if WORKSPACE_ID and len(WORKSPACE_ID) > 8 else "***"


# ------------------------------------------------------------------------------
# LLM factory + single invocation
# ------------------------------------------------------------------------------
# =============================================================================
# CONEXÃO COM A INTELIGÊNCIA ARTIFICIAL
# Monta a conexão com o servidor de IA e faz as chamadas, com tentativas
# automáticas (retry) caso a rede/servidor falhe momentaneamente.
# =============================================================================
def create_llm(session_id: str, model: str, max_tokens: int) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        max_tokens=max_tokens,
        temperature=0,
        timeout=REMEDIATION_CALL_TIMEOUT_S,   # ← v8: per-call timeout
        default_headers={
            "workspace-id": WORKSPACE_ID,
            "session-id": session_id,
        },
    )


def _finish_reason(response) -> str:
    try:
        md = getattr(response, "response_metadata", {}) or {}
        fr = md.get("finish_reason", "")
        if fr:
            return fr.lower()
        add = getattr(response, "additional_kwargs", {}) or {}
        return add.get("finish_reason", "stop").lower()
    except Exception:
        return "stop"



# =============================================================================
# REGISTRO DE USO (instrumentação OPUSCORE-AI — não altera o comportamento)
# Se LLM_USAGE_LOG estiver definido, cada chamada grava uma linha JSON com os
# tokens usados (entrada, saída e cache). A plataforma soma essas linhas para
# mostrar o custo real de cada execução.
# =============================================================================
def _registrar_uso(modelo, resp) -> dict:
    uso = {"input": 0, "cache_read": 0, "cache_creation": 0, "output": 0}
    try:
        um = getattr(resp, "usage_metadata", None) or {}
        det = um.get("input_token_details") or {}
        lido, gravado = int(det.get("cache_read") or 0), int(det.get("cache_creation") or 0)
        uso = {"input": max(int(um.get("input_tokens") or 0) - lido - gravado, 0),
               "cache_read": lido, "cache_creation": gravado,
               "output": int(um.get("output_tokens") or 0)}
        caminho = os.getenv("LLM_USAGE_LOG")
        if caminho:
            import json as _json
            with open(caminho, "a", encoding="utf-8") as f:
                f.write(_json.dumps({"modelo": modelo, **uso}) + "\n")
    except Exception:
        pass  # a medição nunca pode derrubar a chamada
    return uso


def _invoke(llm: ChatOpenAI, system: str, user: str) -> tuple[str, str]:
    """Invoke the LLM with exponential-backoff retry (v8)."""

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(REMEDIATION_RETRY_ATTEMPTS),
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
        before_sleep=lambda rs: log.warning(
            "LLM call failed (attempt %d/%d); retrying in %.1f s — %s",
            rs.attempt_number,
            REMEDIATION_RETRY_ATTEMPTS,
            rs.next_action.sleep,          # type: ignore[attr-defined]
            rs.outcome.exception(),
        ),
    )
    def _call() -> tuple[str, str]:
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        _registrar_uso(getattr(llm, "model_name", None), resp)
        text = resp.content if isinstance(resp.content, str) else str(resp.content)
        return text, _finish_reason(resp)

    return _call()


# ------------------------------------------------------------------------------
# Robust JSON extraction using raw_decode
# ------------------------------------------------------------------------------
def _parse_json_object(text: str) -> Optional[dict]:
    """Extract the first JSON object from text, tolerating trailing content."""
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t).strip()
    t = re.sub(r"\s*```$", "", t).strip()

    start = t.find("{")
    if start == -1:
        return None

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(t, start) 
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return None


# ------------------------------------------------------------------------------
# 1) TRIAGEM
# ------------------------------------------------------------------------------
# =============================================================================
# OS PROMPTS — as instruções enviadas à IA (ficam em inglês,
# pois a IA segue instruções técnicas em inglês com mais precisão).
#   1) TRIAGEM  : pergunta rápida 'precisa mexer? sim/não' (IA barata).
#   2) ANÁLISE  : produz a lista de correções em JSON (IA cara).
#   3) NAMING   : audita os nomes usados no código (mais abaixo no arquivo).
# =============================================================================
TRIAGE_SYSTEM_ROLE = (
    "You are triaging ABAP code for an SAP ECC to S/4HANA 2025 conversion. You "
    "answer only whether a fragment needs any change (Simplification Items, "
    "deprecated syntax/APIs, performance, obsolete statements, Clean Core, "
    "cross-program memory access, macros, hardcodes). You never invent findings. "
    "When unsure, you answer true."
)


def build_triage_prompt(fragment_text: str) -> str:
    return f"""Decide if this ABAP fragment needs ANY change or review for an SAP
S/4HANA 2025 conversion (Simplification Items, deprecated/removed APIs,
performance, obsolete statements, Clean Core readiness, cross-program memory
access via ASSIGN ('(SAPL...)...'), macros, hardcodes).

Answer with ONE line of JSON and nothing else:
{{"needs_change": true|false}}

If unsure, answer true.

FRAGMENT:
{fragment_text}
"""


def _triage_says_skip(llm_triage: ChatOpenAI, fragment_text: str, tag: str) -> bool:
    try:
        text, _ = _invoke(llm_triage, TRIAGE_SYSTEM_ROLE, build_triage_prompt(fragment_text))
        low = text.lower()
    except Exception as e:
        log.warning("[%s] triage error (%s); analysing anyway.", tag, type(e).__name__)
        return False
    if "needs_change" in low:
        return "false" in low and "true" not in low
    return False


# ------------------------------------------------------------------------------
# 2) ANALISE
# ------------------------------------------------------------------------------
ANALYSIS_SYSTEM_ROLE = (
    f"You are a Senior SAP ABAP Remediation Expert for an SAP ECC to "
    f"{SAP_TARGET_VERSION} conversion, targeting ATC check variant "
    f"{ATC_CHECK_VARIANT}. You use ONLY the workspace knowledge-base (RAG) "
    f"documents listed below; your IA does not resolve them on its own, so read "
    f"them BY NAME before deciding anything:\n{_rag_source_list()}\n"
    f"You output a change-set as JSON ONLY — you NEVER return source code, and "
    f"you NEVER write prose or commentary outside the JSON. Every 'anchor' MUST "
    f"be copied character-for-character from the fragment, as ONE OR MORE "
    f"COMPLETE lines INCLUDING their original leading indentation (spaces/tabs); "
    f"you never trim leading whitespace and never use a partial line. You never "
    f"invent Simplification Item or SAP Note numbers, findings, or knowledge-base "
    f"document names. Every item MUST carry a 'rag_source': the EXACT document "
    f"name from the list above (with a Simplification Item / SAP Note when the "
    f"document gives one), or the literal 'GENERAL ABAP BEST PRACTICE (not from "
    f"workspace KB)'. Never leave rag_source blank. Data-model / migration topics "
    f"are out of scope for code rewrite: you 'flag' them, you do not fabricate "
    f"logic. Do NOT perform naming analysis here — naming is audited separately. "
    f"All text you write is in English."
)


def _package_context(package: str) -> str:
    if not package:
        return ""
    return (
        f"OBJECT SAP PACKAGE (development class): '{package}'. Take this package "
        f"and its namespace into account when reasoning about Clean Core, released "
        f"APIs, and whether an object is custom vs SAP-standard. Do NOT emit any "
        f"marker just because of the package; only propose changes a Simplification "
        f"Item / rule actually supports.\n\n"
    )


_PATTERN_CATALOGUE = """PATTERNS TO ACTIVELY LOOK FOR (not exhaustive; only mark
what genuinely applies, and cite the right rag_source; do NOT fabricate):
- CROSS-PROGRAM MEMORY ACCESS: ASSIGN ('(SAPLxxxx)FIELD') / ASSIGN ('(PROG)VAR')
  reading or writing another program's globals or internal tables. This breaks
  Clean Core and is very likely to fail in S/4HANA (those programs changed) →
  usually a WARNING or a MANUAL REVIEW (flag). Mark EVERY such statement, not
  just the first.
- MACROS: a statement that is a bare custom word with operands (e.g. a call like
  'get_hard ...' defined in an INCLUDE) → WARNING (macros are discouraged).
- LEAVE PROGRAM / LEAVE TO TRANSACTION inside an enhancement/BAdI → flag.
- IMPORT/EXPORT ... FROM/TO MEMORY ID — cross-call ABAP memory state → flag/warn.
- HARDCODES: sy-uname = '<user>', hardcoded t-code / client / company code /
  currency → WARNING (and dead code such as a commented WHILE sy-uname EQ '...').
- LOCALIZATION / SIMPLIFIED DATA ELEMENTS: e.g. j_1b* Brazil data elements and
  fields of tables merged in S/4HANA → change if a Simplification Item supports
  it, otherwise flag.
- SELECT * and DIRECT reads/writes of SAP standard tables where a released
  CDS/API exists → WARNING (Clean Core).
- OBSOLETE STATEMENTS: MOVE, COMPUTE, WRITE ... TO, header lines, OCCURS, RANGES,
  SELECT ... ENDSELECT → change or warning as the knowledge base supports.
"""


def build_analysis_prompt(file_type: str, unit_label: str, unit_name: Optional[str],
                          global_context: str, fragment_code: str,
                          package: str = "") -> str:
    name = f" ({unit_name})" if unit_name else ""
    ctx_block = (
        f"GLOBAL CONTEXT (read-only reference — do NOT create anchors from it):\n"
        f"{global_context}\n\n" if global_context.strip() else ""
    )
    return f"""Analyse this {file_type} fragment {unit_label}{name} for an SAP ECC
to {SAP_TARGET_VERSION} conversion (ATC {ATC_CHECK_VARIANT}). Consult the
knowledge-base documents named in your system role BY NAME before deciding.

{_package_context(package)}{_PATTERN_CATALOGUE}
Return ONLY a single JSON object, no prose, no code fences, in EXACTLY this schema:
{{
  "changes": [
    {{
      "anchor": "<one or more COMPLETE lines copied verbatim from the fragment, WITH original indentation; must appear exactly once>",
      "replacement": "<the new ABAP code that replaces the anchor>",
      "reason": "<one concrete technical sentence; name the Simplification Item/rule if known>",
      "rag_source": "<EXACT KB document name / Simplification Item / SAP Note, OR 'GENERAL ABAP BEST PRACTICE (not from workspace KB)'>"
    }}
  ],
  "flags": [
    {{
      "anchor": "<one or more COMPLETE lines copied verbatim from the fragment, WITH original indentation>",
      "reason": "<why this needs manual review: data model / migration / modification / unused / cross-program access>",
      "rag_source": "<as above>"
    }}
  ],
  "warnings": [
    {{
      "anchor": "<one or more COMPLETE lines copied verbatim from the fragment, WITH original indentation>",
      "issue": "<what deviates from S/4HANA 2025 / Clean Core best practice>",
      "impact": "<why it matters even though it does not block ATC {ATC_CHECK_VARIANT}>",
      "recommendation": "<the ABAP code you would use to fix this; it is inserted COMMENTED as a suggestion right after the WARNING block, NOT applied to the code>",
      "rag_source": "<as above>"
    }}
  ]
}}

RULES:
- 'anchor' = ONE OR MORE COMPLETE consecutive lines, copied CHARACTER-FOR-CHARACTER
  from the fragment INCLUDING the original leading indentation. NEVER trim the
  leading spaces/tabs, NEVER use a partial line, NEVER paraphrase/reformat.
- Keep the anchor minimal but UNIQUE and specific: pick the exact statement
  line(s). Do NOT use a generic single line (like a bare 'ENDIF.' or 'CLEAR: x.')
  that occurs many times.
- Emit ONE item per distinct place you want to mark. Do NOT emit the SAME anchor
  more than once, and do NOT emit duplicate items (same anchor + same reason).
- 'changes' rewrite code; 'flags' and 'warnings' leave code UNCHANGED (Python
  inserts a marker on its own line ABOVE the anchor). Only add a change when a
  Simplification Item / rule in the RAG supports it.
- For every 'warning', ALSO provide 'recommendation': the real, functional ABAP
  code that would fix the non-compliance. It is inserted as COMMENTED lines right
  after the WARNING block, as a suggestion — the original code is NOT modified.
  Write real code, not a TODO or an "Example:" placeholder.
- Never auto-add BINARY SEARCH to a READ TABLE — use a 'warning' instead.
- If nothing applies, return {{"changes": [], "flags": [], "warnings": []}}.
- Do NOT return the source code. JSON only. No text before or after the JSON.

{ctx_block}FRAGMENT TO ANALYSE (create anchors ONLY from inside this fragment):
{fragment_code}
"""


# ------------------------------------------------------------------------------
# 3) ESSA PARTE AQUI É IMPORTANTE: DETERMINISTIC
# ------------------------------------------------------------------------------
# =============================================================================
# OS MARCADORES — os blocos de comentário inseridos no código corrigido:
#   BEGIN/END OF MODIFICATION (troca, com o 'Antes'), MANUAL REVIEW (revisão)
#   e WARNING (aviso + código recomendado comentado).
# =============================================================================
def _sep(comment_style: str) -> str:
    return comment_style + ("-" * 98)


def _begin_mod(cs: str, reason: str, rag_source: str, original: str = "") -> str:
    sep = _sep(cs)
    out = (
        f"{sep}\n"
        f"{cs} BEGIN OF MODIFICATION - Capgemini SAP AI Remediation\n"
        f"{cs} Reason     : {reason}\n"
        f"{cs} RAG Source : {rag_source}\n"
    )
    if original and original.strip():
        # v8: use textwrap.dedent instead of fragile manual dedent
        # (handles mixed tabs/spaces gracefully)
        dedented = textwrap.dedent(original.rstrip("\n"))
        non_empty = [l for l in dedented.splitlines() if l.strip()]
        if len(non_empty) == 1:
            out += f"{cs} Antes      : {non_empty[0].strip()}\n"
        else:
            out += f"{cs} Antes      :\n"
            for ol in dedented.splitlines():
                out += f"{cs}   {ol}\n" if ol.strip() else f"{cs}\n"
    out += f"{sep}\n"
    return out


def _end_mod(cs: str) -> str:
    sep = _sep(cs)
    return (
        f"{sep}\n"
        f"{cs} END OF MODIFICATION - Capgemini SAP AI Remediation\n"
        f"{sep}\n"
    )


def _flag_marker(cs: str, reason: str, rag_source: str) -> str:
    sep = _sep(cs)
    return (
        f"{sep}\n"
        f"{cs} MANUAL REVIEW REQUIRED - Capgemini SAP AI Remediation\n"
        f"{cs} Reason     : {reason}\n"
        f"{cs} RAG Source : {rag_source}\n"
        f"{sep}\n"
    )


def _warn_marker(cs: str, issue: str, impact: str, rag_source: str,
                 recommendation: str = "") -> str:
    sep = _sep(cs)
    out = (
        f"{sep}\n"
        f"{cs} WARNING - ABAP BEST PRACTICE NON-COMPLIANCE ({SAP_TARGET_VERSION})\n"
        f"{cs} Issue      : {issue}\n"
        f"{cs} RAG Source : {rag_source}\n"
        f"{cs} Impact     : {impact}\n"
        f"{sep}\n"
    )
    if recommendation and recommendation.strip():
        out += f"{cs} Recommended code (suggestion — not applied):\n"
        for rl in recommendation.rstrip("\n").split("\n"):
            out += f"{cs}   {rl}\n"
        out += f"{sep}\n"
    return out


def _leading_ws(line: str) -> str:
    m = re.match(r"[ \t]*", line)
    return m.group(0) if m else ""


def _indent_block(block: str, indent: str) -> str:
    """Prefix every non-empty line of a marker block with `indent`."""
    if not indent:
        return block
    return "".join(
        (indent + ln) if ln.strip() else ln
        for ln in block.splitlines(keepends=True)
    )


def _anchor_lines_stripped(anchor: str) -> list[str]:
    a = [ln.strip() for ln in (anchor or "").splitlines()]
    while a and a[0] == "":
        a.pop(0)
    while a and a[-1] == "":
        a.pop()
    return a


def _find_line_ranges(stripped_lines: list[str], anchor_stripped: list[str]) -> list[tuple[int, int]]:
    """Return all [start, end) windows matching the anchor (whole-line, whitespace-insensitive)."""
    n = len(anchor_stripped)
    if n == 0:
        return []
    ranges: list[tuple[int, int]] = []
    i = 0
    total = len(stripped_lines)
    while i <= total - n:
        if stripped_lines[i:i + n] == anchor_stripped:
            ranges.append((i, i + n))
            i += n
        else:
            i += 1
    return ranges


class ApplyStats:
    def __init__(self) -> None:
        self.changes = 0
        self.flags = 0
        self.warnings = 0
        self.rejected = 0


# =============================================================================
# A APLICAÇÃO DETERMINÍSTICA (SEM IA) — Custo ZERO.
# Pega a lista de correções da IA e aplica com regras rígidas: Nunca corrompe o código original.
# =============================================================================
def apply_change_set(fragment_text: str, change_set: dict, comment_style: str,
                     stats: ApplyStats, file_tag: str = "") -> str:
    """Apply a change-set to ONE fragment, line-based and indent-preserving.

    v8 change: _register() now logs a WARNING when MAX_MARK_OCCURRENCES is hit.
    """
    lines = fragment_text.splitlines(keepends=True)
    stripped = [ln.strip() for ln in lines]

    # -- Phase 1: CHANGES (unique match; replace the range) applied bottom-to-top.
    change_ops: list[tuple[int, int, str]] = []
    for chg in change_set.get("changes", []) or []:
        a = _anchor_lines_stripped(chg.get("anchor", ""))
        if not a:
            stats.rejected += 1
            continue
        ranges = _find_line_ranges(stripped, a)
        if len(ranges) != 1:
            stats.rejected += 1
            continue
        start, end = ranges[0]
        indent = _leading_ws(lines[start])
        original_code = "".join(lines[start:end])
        replacement = (chg.get("replacement", "") or "").rstrip("\n") + "\n"
        block = (_indent_block(_begin_mod(comment_style, chg.get("reason", "(no reason)"),
                                          chg.get("rag_source", "") or "(unspecified)",
                                          original_code), indent)
                 + replacement
                 + _indent_block(_end_mod(comment_style), indent))
        change_ops.append((start, end, block))
        stats.changes += 1

    for start, end, block in sorted(change_ops, key=lambda t: t[0], reverse=True):
        lines[start:end] = [block]

    # Recompute after changes.
    text = "".join(lines)
    lines = text.splitlines(keepends=True)
    stripped = [ln.strip() for ln in lines]

    # -- Phase 2: FLAGS + WARNINGS (insert marker ABOVE each occurrence).
    inserts: dict[int, list[tuple[str, str]]] = {}

    def _register(anchor: str, marker: str, signature: str) -> bool:
        a = _anchor_lines_stripped(anchor)
        if not a:
            return False
        ranges = _find_line_ranges(stripped, a)
        if not ranges:
            return False
        if len(ranges) > MAX_MARK_OCCURRENCES:
            # v8: log explicitly instead of silently truncating
            log.warning(
                "[%s] Anchor matched %d times (> MAX_MARK_OCCURRENCES=%d); "
                "marking only the first occurrence. Anchor: %r",
                file_tag, len(ranges), MAX_MARK_OCCURRENCES, anchor[:120],
            )
            ranges = ranges[:1]
        for start, _end in ranges:
            indent = _leading_ws(lines[start])
            inserts.setdefault(start, []).append((signature, _indent_block(marker, indent)))
        return True

    for flg in change_set.get("flags", []) or []:
        reason = flg.get("reason", "(no reason)")
        marker = _flag_marker(comment_style, reason, flg.get("rag_source", "") or "(unspecified)")
        if _register(flg.get("anchor", ""), marker, f"FLAG::{reason}"):
            stats.flags += 1
        else:
            stats.rejected += 1

    for wrn in change_set.get("warnings", []) or []:
        issue = wrn.get("issue", "(no issue)")
        marker = _warn_marker(comment_style, issue, wrn.get("impact", ""),
                              wrn.get("rag_source", "") or "(unspecified)",
                              wrn.get("recommendation", ""))
        if _register(wrn.get("anchor", ""), marker, f"WARN::{issue}"):
            stats.warnings += 1
        else:
            stats.rejected += 1

    # Apply inserts bottom-to-top; de-duplicate identical markers on the same line.
    for idx in sorted(inserts, reverse=True):
        seen: set[str] = set()
        block = ""
        for signature, marker in inserts[idx]:
            if signature in seen:
                continue
            seen.add(signature)
            block += marker
        if block:
            lines[idx:idx] = [block]

    return "".join(lines)


# ------------------------------------------------------------------------------
# 4) GLOBAL NAMING PASS (v8: separate model; source char-limit guard)
# ------------------------------------------------------------------------------
NAMING_SYSTEM_ROLE = (
    f"You are a Senior SAP ABAP naming-governance reviewer for an SAP ECC to "
    f"{SAP_TARGET_VERSION} conversion. Your ONLY job is to audit custom "
    f"identifier names (and, when given, the SAP package name) against the naming "
    f"Workbook '{NAMING_WORKBOOK_NAME}'. Your IA does NOT resolve the knowledge "
    f"base on its own — read the Workbook BY NAME from the workspace knowledge "
    f"base first. It is one of these documents:\n{_rag_source_list()}\n"
    f"You output ONLY comment lines (a status block and zero or more violation "
    f"blocks) — never source code, never prose outside comments. You audit EVERY "
    f"custom identifier, not only the package. You never invent rules; if the "
    f"Workbook is silent you say so; if it cannot be retrieved you report NOT "
    f"VERIFIED. You never flag SAP-standard names — only CUSTOM identifiers "
    f"(typically Z*/Y* and project namespace)."
)


def build_naming_prompt(file_type: str, comment_style: str, source: str,
                        package: str = "") -> str:
    sep = _sep(comment_style)
    status = (
        f"{sep}\n"
        f"{comment_style} NAMING ANALYSIS STATUS - Capgemini SAP AI Remediation (ABAP_Move2S4 Workbook)\n"
        f"{comment_style} Workbook    : {NAMING_WORKBOOK_NAME}\n"
        f"{comment_style} Package     : {package or '(not specified)'}\n"
        f"{comment_style} Retrieved   : <YES if you consulted the Workbook content, NO otherwise>\n"
        f"{comment_style} Result      : <'COMPLIANT - no naming violations found', or "
        f"'N VIOLATION(S) FOUND - see NAMING VIOLATION markers below', or "
        f"'NOT VERIFIED - Workbook not retrievable, manual naming review required'>\n"
        f"{comment_style} Scope       : <what you checked, including the package name>\n"
        f"{sep}"
    )
    violation = (
        f"{sep}\n"
        f"{comment_style} NAMING VIOLATION - Capgemini SAP AI Remediation (ABAP_Move2S4 Workbook)\n"
        f"{comment_style} Object     : <the custom identifier (or the SAP package) that violates the standard, quoted exactly>\n"
        f"{comment_style} Kind       : <PACKAGE | PROGRAM | INCLUDE | CLASS | METHOD | FORM | MACRO | DATA | TYPE | CONSTANT | PARAMETER | FIELD-SYMBOL | ...>\n"
        f"{comment_style} Rule       : <the specific Workbook rule violated>\n"
        f"{comment_style} Expected   : <the compliant name/pattern, or 'see Workbook - reviewer to assign'>\n"
        f"{comment_style} RAG Source : {NAMING_WORKBOOK_NAME}\n"
        f"{sep}"
    )
    package_step = ""
    if package:
        package_step = (
            f"\nSTEP 0 — audit the SAP PACKAGE NAME '{package}' FIRST (Kind=PACKAGE, "
            f"Object=\"{package}\"), then use its namespace as the expected namespace "
            f"for the other identifiers. The package is NOT the only thing to check.\n"
        )
    return f"""Perform the MANDATORY naming analysis for this {file_type} source
against the Workbook '{NAMING_WORKBOOK_NAME}'. Read the Workbook BY NAME from the
workspace knowledge base FIRST (it is one of these indexed documents):
{_rag_source_list()}
{('The object belongs to SAP package ' + chr(39) + package + chr(39) + '.') if package else ''}
Then audit the SAP package name (when given) AND EVERY custom identifier — do NOT
stop after the package. Cover at least: include names (INCLUDE z*), custom TYPES
(ty_*), CONSTANTS (c_*), DATA/variables, field-symbols, custom FORM/METHOD names,
macros called (e.g. get_hard), and custom fields (zz*). Emit one violation block
per violating identifier.

OUTPUT CONTRACT — return ONLY {comment_style} comment lines, nothing else (no
source code, no prose, no fences, no text before the first {comment_style}).
{package_step}
STEP 1 — emit EXACTLY ONE status block first:
{status}

STEP 2 — one violation block per violating custom identifier (and the package):
{violation}

- Set Retrieved=YES only if you actually read the Workbook rules; else NO +
  Result 'NOT VERIFIED ...' and no violation blocks.
- Do NOT rename anything. RAG Source is ALWAYS '{NAMING_WORKBOOK_NAME}'. Do NOT
  flag SAP-standard names. The Result count MUST match the number of violation
  blocks.

SOURCE TO AUDIT (do NOT echo it back):
{source}

Return ONLY the {comment_style} status block followed by any {comment_style}
violation blocks.
"""


def _sanitise_comment_only(block: str, comment_style: str) -> str:
    kept: list[str] = []
    for line in block.splitlines():
        s = line.strip()
        if s == "" or s.startswith(comment_style):
            kept.append(line.rstrip("\n"))
    while kept and kept[0].strip() == "":
        kept.pop(0)
    while kept and kept[-1].strip() == "":
        kept.pop()
    return "\n".join(kept)


# ------------------------------------------------------------------------------
# Cabeçalho do Arquivo
# ------------------------------------------------------------------------------
# =============================================================================
# MONTAGEM DO ARQUIVO FINAL — o carimbo corporativo (Capgemini/Brazil, com a
# data) e o cabeçalho que vão no topo de cada arquivo remediado.
# =============================================================================
def create_brazil_stamp(comment_style: str) -> str:
    exec_date = datetime.now().strftime("%d/%m/%Y")
    star = comment_style + ("*" * 69)
    lines = [
        star,
        f"{comment_style} Capgemini AI Remediation Code - Brazil",
        star,
        f"{comment_style} Data Execução: \t{exec_date}",
        f"{comment_style} Autor:\t \t\tCapgemini SAP AI - Plataform",
        f"{comment_style} Projeto:              MOVE2S4",
        star,
    ]
    return "\n".join(lines) + "\n\n\n"


def create_header(comment_style: str, session_id: str, base_name: str,
                  file_path: str, package: str, schedule_note: str) -> str:
    current_date = datetime.now().strftime("%d-%m-%Y")
    sep = "-" * 132
    lines = [
        f"{comment_style}{sep}",
        f"{comment_style}{'Capgemini SAP AI Remediation':^132}",
        f"{comment_style}{sep}",
        f"{comment_style} Date           : {current_date}",
        f"{comment_style} Remediation    : RAG-driven; model emits change-set JSON, Python applies it (line-based)",
        f"{comment_style} Target         : {SAP_TARGET_VERSION}",
        f"{comment_style} ATC Variant    : {ATC_CHECK_VARIANT}",
        f"{comment_style} Package        : {package or '(not specified)'}",
        f"{comment_style}{sep}",
        f"{comment_style} ORIGINAL FILE  : {base_name}",
        f"{comment_style} SOURCE         : {file_path}",
        f"{comment_style} SESSION ID     : {session_id}",
        f"{comment_style} PROCESSED AT   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{comment_style}{'=' * 132}",
    ]
    return "\n".join(lines) + "\n\n"


class RunStats:
    def __init__(self) -> None:
        self.fragments_total = 0
        self.skipped_prefilter = 0
        self.skipped_triage = 0
        self.analysed = 0
        self.apply = ApplyStats()
        self.naming_result = "(disabled)"

    def __str__(self) -> str:
        return (f"fragments={self.fragments_total} "
                f"skipped(prefilter)={self.skipped_prefilter} "
                f"skipped(triage)={self.skipped_triage} "
                f"analysed={self.analysed} | "
                f"changes={self.apply.changes} flags={self.apply.flags} "
                f"warnings={self.apply.warnings} rejected={self.apply.rejected} | "
                f"naming={self.naming_result}")


# ------------------------------------------------------------------------------
# Analyse one fragment -> change-set -> deterministic apply
# ------------------------------------------------------------------------------
def _remediate_fragment(llm_main: ChatOpenAI, file_type: str, comment_style: str,
                        label: str, name: Optional[str], global_ctx: str,
                        fragment_text: str, tag: str, package: str,
                        stats: RunStats) -> str:
    prompt = build_analysis_prompt(file_type, label, name, global_ctx,
                                   fragment_text, package)
    try:
        text, fr = _invoke(llm_main, ANALYSIS_SYSTEM_ROLE, prompt)
    except Exception as e:
        log.warning("[%s] analysis error (%s); kept verbatim.", tag, type(e).__name__)
        return fragment_text
    change_set = _parse_json_object(text)
    if change_set is None:
        log.warning("[%s] no valid JSON (finish='%s', %d chars); kept verbatim.",
                    tag, fr, len(text))
        return fragment_text
    stats.analysed += 1
    n_c = len(change_set.get("changes") or [])
    n_f = len(change_set.get("flags") or [])
    n_w = len(change_set.get("warnings") or [])
    log.info("[%s] change-set: %d change(s), %d flag(s), %d warning(s)", tag, n_c, n_f, n_w)
    return apply_change_set(fragment_text, change_set, comment_style, stats.apply, tag)


# ------------------------------------------------------------------------------
# Scheduler
# ------------------------------------------------------------------------------
# =============================================================================
# A ORQUESTRAÇÃO — junta tudo: corta em pedaços, roda o funil (triagem ->
# análise -> aplicação) em cada pedaço, e monta o corpo do arquivo corrigido.
# Quebra o arquivo em Chunks (quando permitido) e aplica a IA em cada fragmento, depois junta tudo.
# =============================================================================
def remediate_body(llm_main: ChatOpenAI, llm_triage: ChatOpenAI,
                   file_type: str, comment_style: str, source: str, ext: str,
                   package: str, stats: RunStats) -> str:
    def _whole() -> str:
        stats.fragments_total += 1
        return _remediate_fragment(llm_main, file_type, comment_style,
                                   "WHOLE SOURCE", None, "", source, "whole",
                                   package, stats)

    if ext in _NON_CHUNKABLE_EXT or REMEDIATION_CHUNKING == "off":
        log.info("Scheduling: single fragment (non-chunkable ext or chunking=off)")
        return _whole()
    if REMEDIATION_CHUNKING == "auto" and len(source) <= WHOLE_SOURCE_CHAR_LIMIT:
        log.info("Scheduling: single fragment (auto; %d <= %d chars)",
                 len(source), WHOLE_SOURCE_CHAR_LIMIT)
        return _whole()

    segments = chunk_for_analysis(source, max_chars=REMEDIATION_CHUNK_CHARS)
    if not verify_roundtrip(source, segments):
        log.warning("Chunker round-trip failed — falling back to single fragment.")
        return _whole()

    log.info("Scheduling: CHUNKED (max %d chars/fragment) — %s",
             REMEDIATION_CHUNK_CHARS, summarize(segments))
    global_ctx = extract_global_context(source)
    out_parts: list[str] = []

    for idx, seg in enumerate(segments):
        if not seg.has_code:
            out_parts.append(seg.text)
            continue

        stats.fragments_total += 1
        if seg.kind == "unit":
            label = seg.unit_type or "UNIT"
            tag = f"{label.lower()}:{seg.name or idx}"
            ctx = global_ctx
        else:
            label = "GLOBAL/SEAM"
            tag = f"seam:{idx}"
            ctx = ""

        needs, _sig = prefilter_unit(seg.text, "conversion_quality")
        if not needs:
            stats.skipped_prefilter += 1
            log.info("[%s] skipped (prefilter), kept verbatim", tag)
            out_parts.append(seg.text)
            continue

        if ENABLE_TRIAGE and _triage_says_skip(llm_triage, seg.text, tag):
            stats.skipped_triage += 1
            log.info("[%s] skipped (triage), kept verbatim", tag)
            out_parts.append(seg.text)
            continue

        log.info("[%s] analysing (%d chars)", tag, len(seg.text))
        new_text = _remediate_fragment(llm_main, file_type, comment_style, label,
                                       seg.name, ctx, seg.text, tag, package, stats)
        out_parts.append(new_text)

    return "".join(out_parts)


def run_naming_pass(llm_naming: ChatOpenAI, file_type: str, comment_style: str,
                    source: str, package: str, stats: RunStats) -> str:
    """v8: uses llm_naming (separate model); guards source length."""
    if not ENABLE_NAMING_CHECK:
        return ""

    # v8: guard against context-window overflow for very large sources
    source_for_naming = source
    truncated = False
    if len(source) > NAMING_SOURCE_CHAR_LIMIT:
        source_for_naming = (
            source[:NAMING_SOURCE_CHAR_LIMIT]
            + f"\n\n[... SOURCE TRUNCATED TO {NAMING_SOURCE_CHAR_LIMIT} CHARS FOR NAMING ANALYSIS ...]"
        )
        truncated = True
        log.warning(
            "Source (%d chars) exceeds NAMING_SOURCE_CHAR_LIMIT (%d); "
            "naming pass will analyse only the first %d chars.",
            len(source), NAMING_SOURCE_CHAR_LIMIT, NAMING_SOURCE_CHAR_LIMIT,
        )

    log.info("Naming: global analysis pass (whole source%s)...",
             " — TRUNCATED" if truncated else "")
    try:
        raw, fr = _invoke(llm_naming, NAMING_SYSTEM_ROLE,
                          build_naming_prompt(file_type, comment_style,
                                             source_for_naming, package))
    except Exception as e:
        log.warning("Naming pass failed (%s: %s); continuing.", type(e).__name__, e)
        stats.naming_result = "(naming pass failed)"
        return ""
    block = _sanitise_comment_only(raw, comment_style)
    for line in block.splitlines():
        if "Result" in line and ":" in line:
            stats.naming_result = line.split(":", 1)[1].strip()
            break
    else:
        stats.naming_result = "(no status parsed)"
    log.info("[naming] finish='%s', %d chars kept after sanitise", fr, len(block))
    return block.rstrip("\n") + "\n\n" if block else ""


# ------------------------------------------------------------------------------
# Core file processing (called concurrently — fully self-contained)
# ------------------------------------------------------------------------------
# =============================================================================
# PROCESSAR UM ARQUIVO (de ponta a ponta) e a FUNÇÃO PRINCIPAL (main), que
# encontra os arquivos em ./remediation e os processa (vários em paralelo).
# =============================================================================
def process_file(file_path: str, output_folder: str) -> None:
    base_name = os.path.basename(file_path)
    file_type, comment_style, original_ext = get_file_type_and_comment_style(base_name)
    package = resolve_package(file_path)

    name_without_ext = os.path.splitext(base_name)[0]
    output_filename = f"{name_without_ext}.{original_ext or 'txt'}"
    output_path = os.path.join(output_folder, output_filename)

    # v8: idempotency — skip if output already exists and flag is set
    if REMEDIATION_SKIP_EXISTING and os.path.exists(output_path):
        log.info("Skipping (output exists): %s", base_name)
        return

    log.info("Processing: %s  (type=%s, package=%s)", base_name, file_type, package or '-')

    session_id = str(uuid.uuid4())
    # v8: llm_naming uses a potentially different model from llm_main
    llm_main   = create_llm(session_id, LLM_MODEL_MAIN,   LLM_MAX_TOKENS)
    llm_triage = create_llm(session_id, LLM_MODEL_TRIAGE, 64)
    llm_naming = create_llm(session_id, LLM_MODEL_NAMING, LLM_MAX_TOKENS)

    try:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="cp1252", errors="replace") as f:
                original_content = f.read()
    except Exception as e:
        log.error("Read error for %s: %s", base_name, e)
        return

    stats = RunStats()

    naming_block = run_naming_pass(llm_naming, file_type, comment_style,
                                   original_content, package, stats)

    try:
        body = remediate_body(llm_main, llm_triage, file_type, comment_style,
                              original_content, original_ext, package, stats)
        if not body:
            raise ValueError("empty remediation body")
    except Exception as e:
        log.error("Remediation error for %s: %s", base_name, e)
        return

    schedule_note = (f"package={package or '-'}, chunking={REMEDIATION_CHUNKING}, "
                     f"triage={'on' if ENABLE_TRIAGE else 'off'}, "
                     f"naming={'on' if ENABLE_NAMING_CHECK else 'off'} | {stats}")

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(create_brazil_stamp(comment_style))
            f.write(create_header(comment_style, session_id, base_name,
                                  file_path, package, schedule_note))
            if naming_block:
                f.write(naming_block)
            f.write(body)
        log.info("Saved: %s | %s", output_filename, stats)
    except Exception as e:
        log.error("Write error for %s: %s", base_name, e)


# ------------------------------------------------------------------------------
# Main — Execução em paralelo via ThreadPoolExecutor
# ------------------------------------------------------------------------------
def main() -> None:
    
    # Verifica arquivo .env e carrega variáveis de ambiente
    _validate_config()

    remediation_folder = os.path.join(os.getcwd(), REMEDIATION_INPUT_DIR)
    remediated_folder  = os.path.join(os.getcwd(), REMEDIATION_OUTPUT_DIR)

    log.info("=" * 80)
    log.info("  Capgemini SAP AI Remediation Engine") 
    log.info("=" * 80)
    log.info("  Target         : %s", SAP_TARGET_VERSION)
    log.info("  ATC Variant    : %s", ATC_CHECK_VARIANT)
    log.info("  SAP Package    : %s", SAP_PACKAGE or '(global not set; per-file .pkg may apply)')
    log.info("  Chunking       : %s (single fragment <= %d chars)",
             REMEDIATION_CHUNKING, WHOLE_SOURCE_CHAR_LIMIT)
    log.info("  Triage         : %s",
             f"ON ({LLM_MODEL_TRIAGE})" if ENABLE_TRIAGE else "OFF")
    log.info("  Naming check   : %s",
             f"ON ({NAMING_WORKBOOK_NAME}, model={LLM_MODEL_NAMING})"
             if ENABLE_NAMING_CHECK else "OFF")
    log.info("  Main model     : %s", LLM_MODEL_MAIN)
    log.info("  Workers        : %d", REMEDIATION_MAX_WORKERS)
    log.info("  Retry attempts : %d (timeout %ds/call)", REMEDIATION_RETRY_ATTEMPTS,
             REMEDIATION_CALL_TIMEOUT_S)
    log.info("  RAG documents  : %d named (workspace-id %s)",
             len(RAG_KNOWLEDGE_BASE), _mask_workspace_id())
    log.info("  Skip existing  : %s", REMEDIATION_SKIP_EXISTING)
    log.info("=" * 80)

    if not os.path.exists(remediation_folder):
        log.error("Remediation folder not found: %s", remediation_folder)
        return
    os.makedirs(remediated_folder, exist_ok=True)

    supported_extensions = [
        '*.txt', '*.asddls', '*.ddls', '*.srvd', '*.bdef',
        '*.abap', '*.prog', '*.reps', '*.clas', '*.intf',
    ]
    all_files: list[str] = []
    for pattern in supported_extensions:
        all_files.extend(glob.glob(os.path.join(remediation_folder, pattern)))
    all_files = sorted(set(all_files))
    if not all_files:
        log.error("No supported SAP files found for remediation")
        return

    log.info("Found %d file(s):", len(all_files))
    for f in all_files:
        log.info("  - %s", os.path.basename(f))
    log.info("=" * 80)

    # v8: parallel processing — each file is fully independent
    max_workers = min(REMEDIATION_MAX_WORKERS, len(all_files))
    log.info("Launching %d worker thread(s) for %d file(s)...", max_workers, len(all_files))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_file, fp, remediated_folder): fp
            for fp in all_files
        }
        for future in concurrent.futures.as_completed(future_to_file):
            fp = future_to_file[future]
            try:
                future.result()
            except Exception as exc:
                log.error("Unhandled error processing %s: %s",
                          os.path.basename(fp), exc, exc_info=True)

    log.info("=" * 80)
    log.info("Remediation completed for %d file(s)", len(all_files))
    log.info("Output folder : %s", remediated_folder)
    log.info("=" * 80)


if __name__ == "__main__":
    main()