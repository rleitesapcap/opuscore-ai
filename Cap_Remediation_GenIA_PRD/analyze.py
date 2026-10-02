# -*- coding: utf-8 -*-
"""
===============================================================================
 analyze.py  —  A FASE 1 DA REMEDIAÇÃO: onde a Inteligência Artificial ANALISA
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Ele examina o código ABAP e produz uma "lista de correções" (em formato
    JSON), que depois o apply_changes.py aplica de forma mecânica.

O "FUNIL DE ECONOMIA" (a ideia central deste arquivo):
    Analisar cada pedaço de código com a IA mais cara seria lento e caro. Então
    usamos um funil de 3 estágios — cada estágio é mais caro e vê menos coisa:

      1. PRÉ-FILTRO (grátis, sem IA): joga fora os pedaços que claramente não têm
         nada a corrigir. Na dúvida, ele DEIXA PASSAR (nunca descarta algo que
         talvez precise de trabalho).

      2. TRIAGEM (IA barata — modelo "Haiku"): pergunta sim/não — "este pedaço
         precisa de alguma mudança?". Descarta os que passaram no filtro mas que,
         olhando bem, estão OK.

      3. ANÁLISE (IA cara — modelo "Sonnet"): só para os sobreviventes. Consulta a
         base de boas práticas (o "RAG") e produz a lista de correções daquele
         pedaço.

    Resultado: a IA cara só trabalha no que realmente importa, não fiz o calculo de quanto 
    economiza, mas deve ser significativo.

DOIS "VEREDITOS" (o parâmetro `mode`):
    - "conversion"         : corrige SÓ o que quebra na conversão para o S/4HANA
                             (os "Simplification Items").
    - "conversion_quality" : o acima MAIS melhorias gerais de qualidade
                             (performance, comandos obsoletos, Clean Core...).

OBS.: Este arquivo é o "motor de duas fases" que a equipe construiu. O script
principal em produção (lc_CapRemediation.py) segue a mesma ideia de funil.
===============================================================================
"""

from __future__ import annotations

import re
import json
from dataclasses import dataclass, field
from typing import Optional

from abap_chunker import split_abap_units, chunk_for_analysis, extract_global_context


# =============================================================================
# ESTÁGIO 1 — O PRÉ-FILTRO (grátis, sem IA)
# -----------------------------------------------------------------------------
# São "sinais" que indicam que vale a pena a IA olhar um pedaço. NÃO é a lista
# completa de regras — é só um portão barato de "tem algo aqui que mereça
# atenção?". Na menor dúvida, deixa passar (para nunca perder algo importante).
# =============================================================================

# Tabelas famosas que foram reestruturadas no S/4HANA (ex.: estoque virou MATDOC,
# contabilidade virou ACDOCA, preços de venda viraram PRCD_ELEMENTS).
# Se o código mexe nelas, é sinal de atenção.
_S4_TABLES = {
    # Estoque MM-IM (agora MATDOC)
    "mkpf", "mseg", "mard", "marc", "mchb", "mska", "mspr", "mssa", "mssl",
    "msku", "mslb", "mstd", "msca",
    # Financeiro FI (agora ACDOCA)
    "bsis", "bsas", "bsid", "bsad", "bsik", "bsak", "bsim", "glt0",
    "faglflexa", "faglflext", "cobk", "coep", "cosp", "coss",
    # Preços de vendas SD (agora PRCD_ELEMENTS)
    "konv",
}

# Comandos obsoletos / fora do padrão S/4HANA (procurados como palavra inteira).
_OBSOLETE_PATTERNS = [
    r"\bMOVE\b(?!-CORRESPONDING)",   # MOVE (mas não MOVE-CORRESPONDING)
    r"\bCOMPUTE\b",
    r"\bADD\b", r"\bSUBTRACT\b", r"\bMULTIPLY\b", r"\bDIVIDE\b",
    r"\bWRITE\b\s+.*\bTO\b",
    r"\bOCCURS\b",
    r"WITH\s+HEADER\s+LINE",
    r"\bREFRESH\b",
]

# Sinais que SEMPRE merecem uma olhada: acesso a banco, SQL dinâmico, chamadas de
# função, verificações de autorização, batch input, chamadas de transação...
_ALWAYS_LOOK = [
    r"\bSELECT\b", r"\bUPDATE\b", r"\bINSERT\b", r"\bMODIFY\b", r"\bDELETE\b",
    r"\bCALL\s+FUNCTION\b",
    r"\bCALL\s+TRANSACTION\b",     # batch input — as telas mudam no S/4
    r"\bCALL\s+METHOD\b",
    r"\bCREATE\s+OBJECT\b",
    r"\bSUBMIT\b",
    r"\bBDC", r"BDCDATA",
    r"\bEXEC\s+SQL\b",
    r"AUTHORITY-CHECK",
]

# Sinais considerados SÓ no modo "conversion_quality" (qualidade).
_QUALITY_PATTERNS = [
    r"SELECT\s+\*",
    r"\bINTO\s+TABLE\b",           # possível SELECT sem ORDER BY etc.
    r"\bCATCH\b", r"\bRAISE\b",    # tratamento de exceções para revisar
]


def prefilter_unit(text: str, mode: str = "conversion") -> tuple[bool, list[str]]:
    """O PORTÃO BARATO: devolve (precisa_de_IA, sinais_encontrados).

    Só devolve False (não precisa de IA) quando o pedaço não mostra nenhum sinal
    de algo que a remediação tocaria. Na dúvida, devolve True (deixa passar)."""
    upper = text.upper()
    signals: list[str] = []

    # Procura menções às tabelas reestruturadas do S/4HANA.
    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text):
        if tok.lower() in _S4_TABLES:
            signals.append(f"table:{tok.lower()}")

    # Procura acesso a banco / chamadas importantes.
    for pat in _ALWAYS_LOOK:
        if re.search(pat, upper):
            signals.append(f"db:{pat}")
            break

    # Procura comandos obsoletos.
    for pat in _OBSOLETE_PATTERNS:
        if re.search(pat, upper):
            signals.append("obsolete")
            break

    # No modo qualidade, procura também os sinais de qualidade.
    if mode == "conversion_quality":
        for pat in _QUALITY_PATTERNS:
            if re.search(pat, upper):
                signals.append("quality")
                break

    # Remove sinais repetidos, mantendo a ordem.
    seen = set()
    uniq = [s for s in signals if not (s in seen or seen.add(s))]
    return (len(uniq) > 0, uniq)


# =============================================================================
# OS "PROMPTS" — as instruções que enviamos à IA
# (Ficam em inglês de propósito: a IA segue instruções técnicas em inglês com
#  mais precisão, e os documentos de boas práticas também estão em inglês.)
# =============================================================================

# --- Instrução do sistema para a TRIAGEM (estágio 2) ---
TRIAGE_SYSTEM_ROLE = (
    "You are triaging ABAP code for an SAP ECC to S/4HANA 2025 conversion. "
    "You answer only whether a unit needs any change. You never invent findings."
)


def build_triage_prompt(unit_text: str, mode: str) -> str:
    """Monta a pergunta de TRIAGEM: 'este pedaço precisa de mudança? sim/não'."""
    scope = ("S/4HANA Simplification Items only (what breaks on conversion)"
             if mode == "conversion" else
             "S/4HANA Simplification Items AND general code quality")
    return f"""Decide if this ABAP unit needs ANY change for: {scope}.

Answer with ONE line of JSON, nothing else:
{{"needs_change": true|false, "why": "<=8 words"}}

If unsure, answer true.

UNIT:
{unit_text}
"""


def _analysis_scope(mode: str) -> str:
    """Define o "escopo" da análise conforme o veredito escolhido (o que a IA
    pode ou não mexer)."""
    if mode == "conversion":
        return (
            "Change ONLY what a S/4HANA Simplification Item requires (tables/"
            "fields merged or removed, deprecated/removed APIs, incompatibilities "
            "that would fail ATC S4HANA_READINESS). Do NOT make general style or "
            "performance edits."
        )
    return (
        "Change what a S/4HANA Simplification Item requires, AND general quality "
        "issues: performance (SELECT *, nested SELECT, missing ORDER BY), obsolete "
        "statements (MOVE, COMPUTE, WRITE ... TO), exception handling, Clean Core."
    )


# --- Instrução do sistema para a ANÁLISE (estágio 3) ---
ANALYSIS_SYSTEM_ROLE = (
    "You are a Senior SAP ABAP Remediation Expert for an SAP ECC to S/4HANA 2025 "
    "conversion. You use ONLY the best-practice snippets provided to justify "
    "changes. You never invent Simplification Item or SAP Note numbers. You emit "
    "a change-set as JSON only — never the full source."
)


def build_analysis_prompt(unit_label: str, unit_name: Optional[str],
                          unit_text: str, rag_block: str, mode: str,
                          server_side_rag: bool = False) -> str:
    """Monta o pedido de ANÁLISE: pede à IA que devolva a lista de correções
    (as trocas e as sinalizações), em JSON, seguindo um formato exato.

    A parte do "RAG" (base de boas práticas) muda conforme o provedor:
    - RAG local: os trechos de boas práticas vão dentro do próprio pedido;
    - RAG no servidor (Capgemini): a base é fornecida pela plataforma; a IA a
      consulta por fora do pedido;
    - Sem RAG: avisa que não houve consulta e que só se deve mudar o óbvio."""
    name = f" ({unit_name})" if unit_name else ""
    if rag_block.strip():
        # RAG local (Anthropic/CLI): os trechos estão no pedido.
        rag_section = (
            f"BEST-PRACTICE SNIPPETS (use these to justify changes; cite the source "
            f"tag in 'rule'):\n{rag_block}\n\n"
        )
    elif server_side_rag:
        # Capgemini: as práticas vêm da base da plataforma (via workspace-id),
        # injetadas fora deste pedido. NÃO assuma que não existem.
        rag_section = (
            "BEST-PRACTICE KNOWLEDGE BASE: your workspace knowledge base "
            "(via workspace-id) provides the applicable SAP best practices. Use "
            "them to justify changes; name the practice in 'rule' when you can.\n\n"
        )
    else:
        # Sem nenhuma consulta (ex.: Anthropic sem pasta de RAG configurada).
        rag_section = (
            "BEST-PRACTICE SNIPPETS: (none retrieved — only change what is clearly "
            "required, and say so in 'reason')\n\n"
        )
    return f"""Analyse this ABAP unit {unit_label}{name} for an SAP S/4HANA 2025 conversion.

SCOPE: {_analysis_scope(mode)}

{rag_section}Emit ONLY a JSON object, no prose, in this exact schema:
{{
  "changes": [
    {{
      "anchor": "<EXACT snippet copied verbatim from the unit — the minimal lines to replace; must appear once>",
      "replacement": "<the new code>",
      "reason": "<one concrete technical sentence>",
      "rule": "<source tag of the practice used, e.g. practice: file#3; or '' if none>"
    }}
  ],
  "flags": [
    {{
      "anchor": "<EXACT snippet copied verbatim>",
      "reason": "<data model / migration / modification / unused — why it needs manual review>",
      "source_practice": "<source tag of the practice that motivated this flag, e.g. practice: file#3; or '' if none>"
    }}
  ]
}}

Rules:
- 'anchor' MUST be copied character-for-character from the unit so it can be
  matched exactly. Keep it minimal but unique.
- Whenever a best-practice snippet motivated a change or a flag, put its source
  tag (e.g. 'practice: file#3') in 'rule' / 'source_practice'. If none applies,
  leave it ''. Do NOT invent a source tag.
- If nothing needs changing, return {{"changes": [], "flags": []}}.
- Do NOT return the source code. JSON only.

UNIT:
{unit_text}
"""


# =============================================================================
# LEITURA DO JSON devolvido pela IA (tolerante a "sujeira" em volta)
# =============================================================================
def _parse_json_object(text: str) -> Optional[dict]:
    """Extrai o objeto JSON da resposta da IA, aguentando cercas de código
    (```) ou texto solto em volta. Se não conseguir, devolve None."""
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()   # tira ``` do começo
    t = re.sub(r"```$", "", t).strip()            # tira ``` do fim
    # Pega do primeiro '{' até o último '}'.
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(t[start:end + 1])
    except json.JSONDecodeError:
        return None


# =============================================================================
# ORQUESTRAÇÃO — junta os 3 estágios do funil
# =============================================================================
@dataclass
class AnalyzeStats:
    """Ficha de estatísticas do funil: quantos pedaços entraram, quantos foram
    descartados em cada estágio, e quantas correções saíram."""
    units_total: int = 0
    skipped_prefilter: int = 0
    skipped_triage: int = 0
    analyzed: int = 0
    changes: int = 0
    flags: int = 0

    def __str__(self) -> str:
        return (f"units={self.units_total} "
                f"skipped(prefilter)={self.skipped_prefilter} "
                f"skipped(triage)={self.skipped_triage} "
                f"analyzed(Sonnet)={self.analyzed} "
                f"changes={self.changes} flags={self.flags}")


def analyze_source(main_provider, triage_provider, rag,
                   object_name: str, source: str, mode: str = "conversion",
                   rag_k: int = 5, max_unit_chars: int = 6000,
                   server_side_rag: bool = False) -> tuple[dict, AnalyzeStats]:
    """A FUNÇÃO PRINCIPAL DA FASE 1: roda o funil sobre um código e devolve
    (lista_de_correções, estatísticas).
    
    OBS: Preciso rever isso aqui, peguei alguns erros, ainda vou analisar.

    - main_provider   : a IA cara (análise — "Sonnet").
    - triage_provider : a IA barata (triagem — "Haiku"). Pode ser a mesma, se
                        você não quiser separar os modelos.
    - rag             : a base de boas práticas, ou None para pular a consulta.
    - max_unit_chars  : pedaços maiores que isto são cortados no fim de comandos,
                        para nenhuma chamada à IA receber um bloco grande demais.
    """
    # Corta o código em pedaços (usando o abap_chunker). Ficou show isso aqui, porque o chunker 
    # entende a sintaxe ABAP e não corta no meio de uma instrução. Também extrai o contexto 
    # global (tipos, tabelas, includes) que a IA precisa para analisar cada pedaço. O resultado 
    # é uma lista de Segments, cada um com o tipo (sub-rotina, método, função, costura), nome (quando aplicável) e texto.: 
    segments = chunk_for_analysis(source, max_chars=max_unit_chars)
    change_set = {"object": object_name, "mode": mode,
                  "changes": [], "flags": [], "rag_trace": []}
    stats = AnalyzeStats()

    for idx, seg in enumerate(segments):               # para cada pedaço...
        if not seg.has_code:                           # sem código => pula
            continue
        stats.units_total += 1
        label = seg.unit_type or "SEAM"
        name = seg.name
        block_id = f"{label.lower()}:{name or idx}"

        # ---- Estágio 1: pré-filtro (grátis) ----
        needs, _signals = prefilter_unit(seg.text, mode)
        if not needs:                                  # nenhum sinal => descarta
            stats.skipped_prefilter += 1
            continue

        # ---- Estágio 2: triagem (IA barata) ----
        tri = triage_provider.invoke(
            TRIAGE_SYSTEM_ROLE,
            [{"role": "user", "content": build_triage_prompt(seg.text, mode)}])
        verdict = _parse_json_object(tri.text)
        if verdict is None:                            # resposta ilegível => analisa mesmo assim
            print(f"    ⚠ triage returned no valid JSON for {label}:{name} "
                  f"(finish='{tri.finish_reason}') — analysing anyway (fail-open).")
            verdict = {"needs_change": True}
        if verdict.get("needs_change") is False:       # IA disse "não precisa" => descarta
            stats.skipped_triage += 1
            continue

        # ---- Estágio 3: análise (IA cara), consultando o RAG ----
        # Guardamos o que a busca de boas práticas REALMENTE retornou para este
        # pedaço — é o rastro de origem, independente do que a IA depois alegar.
        rag_block = ""
        retrieved = []
        if rag is not None:
            hits = rag.search(seg.text, k=rag_k)
            rag_block = rag.as_prompt_block(hits)
            retrieved = [{"source": h.source, "chunk_id": h.chunk_id,
                          "score": round(float(h.score), 4)} for h in hits]
            change_set["rag_trace"].append({"block": block_id, "unit": name,
                                            "retrieved": retrieved})
        ana = main_provider.invoke(
            ANALYSIS_SYSTEM_ROLE,
            [{"role": "user",
              "content": build_analysis_prompt(label, name, seg.text, rag_block, mode,
                                                server_side_rag=server_side_rag)}])
        if ana.finish_reason == "length":              # resposta cortada por tamanho
            print(f"    ⚠ analysis TRUNCATED for {label}:{name} — JSON may be "
                  f"incomplete; consider a smaller max_unit_chars.")
        parsed = _parse_json_object(ana.text)
        if parsed is None:                             # não veio JSON válido => nada deste pedaço
            print(f"    ⚠ analysis returned no valid JSON for {label}:{name} "
                  f"(finish='{ana.finish_reason}', {len(ana.text)} chars). "
                  f"Preview: {ana.text[:100]!r}")
            parsed = {"changes": [], "flags": []}
        stats.analyzed += 1

        # Anexa a cada correção o id do pedaço e as fontes consultadas, para que
        # todo marcador no resultado possa ser rastreado até os documentos que
        # estavam em contexto.
        retrieved_tags = [f"{r['source']}#{r['chunk_id']}" for r in retrieved]
        for ch in parsed.get("changes", []):
            ch.setdefault("unit", name)
            ch["block"] = block_id
            ch["retrieved_sources"] = retrieved_tags
            change_set["changes"].append(ch)
            stats.changes += 1
        for fl in parsed.get("flags", []):
            fl.setdefault("unit", name)
            fl["block"] = block_id
            fl["retrieved_sources"] = retrieved_tags
            change_set["flags"].append(fl)
            stats.flags += 1

    return change_set, stats


# =============================================================================
# Nota sobre a economia #1 (cache de prompt), que NÃO está neste arquivo:
#
# O cache vive na camada de provedores (llm_providers.py). A maior economia de
# ENTRADA vem de marcar as partes estáveis (a instrução do sistema + o bloco de
# boas práticas, quando se repete) como "cacheáveis":
#   - anthropic  : adicionar cache_control aos blocos de sistema/contexto.
#   - claude_code: o CLI já faz cache sozinho; nada a fazer.
#   - capgemini  : depende de o proxy repassar o cache_control — confirmar com a
#                  equipe da plataforma antes de contar com isso.
# ============================================================================= 