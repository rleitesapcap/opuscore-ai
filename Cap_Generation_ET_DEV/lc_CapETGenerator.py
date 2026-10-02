# -*- coding: utf-8 -*-
"""
===============================================================================
 lc_CapETGenerator.py  —  O GERADOR DE ET (Especificação Técnica) em .docx
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Lê os ARTEFATOS .md que as etapas anteriores geraram (extract.py = Etapa 1;
    generate_docs.py = Etapa 2) e produz a Especificação Técnica (ET) preenchendo
    os marcadores {{IA_*}} do Template OFICIAL, SEM modificar o layout do template.

    A saída principal é o .docx (template preenchido). Um .md de pré-visualização
    também é gerado (útil quando não há template local, p.ex. modo workspace-only).

ENTRADA (produzida pelas etapas anteriores), sob et_output/01_ET_GERADA/artefatos:
    requisitos_extraidos.md  — campos de cabeçalho (## Autor, ## ID GAP,
                               ## Descrição GAP, ## Transações)
    objetos_extraidos.md     — lista de objetos (Nome | Tipo | Status)
    *_DOC.md                 — 1 por objeto (RESUMO EXECUTIVO + SEÇÕES 1..6)
    _payload.json            — índice estruturado dos objetos (backbone)

MAPA DOS MARCADORES (tudo DETERMINÍSTICO — extração, custo ZERO de token):
    Cabeçalho / Identificação
      IA_AUTOR        = FIXO "Capgemini SAP AI Remediation"
      IA_VERSAO       = FIXO "1.0"
      IA_DATA_ATUAL   = data de hoje (DD/MM/YYYY)
      IA_FUNCIONAL    = requisitos_extraidos.md ## Autor
      IA_ANALISTA     = requisitos_extraidos.md ## Autor
      IA_ID_GAP       = requisitos_extraidos.md ## ID GAP
      IA_DESC_GAP     = requisitos_extraidos.md ## Descrição GAP
      IA_TRANSACOES_ENVOLVIDAS = requisitos_extraidos.md ## Transações
    Detalhamento Técnico (a tabela é REPLICADA — uma por objeto):
      IA_OBJETOS_01   = *_DOC.md  RESUMO EXECUTIVO > Entendimento
      IA_OBJETOS_NAME = *_DOC.md  # Documentação Técnica > Arquivo
      IA_OBJETOS_TIPO = *_DOC.md  # Documentação Técnica > Tipo do objeto
      IA_OBJETOS_CLASS= *_DOC.md  # Documentação Técnica > Classificação
      IA_DET_DEV      = *_DOC.md  SEÇÃO 2 – Detalhamento do Desenvolvimento
                                  (descarta '#### Fonte'; títulos '####' em NEGRITO no Word)
      IA_TELA_SELECAO = *_DOC.md  SEÇÃO 4 – Tela de Seleção
      IA_TVARV        = *_DOC.md  SEÇÃO 5 – TVARV
      IA_BRF          = *_DOC.md  SEÇÃO 5.3 – BRF
      IA_OBJ_AUT      = *_DOC.md  SEÇÃO 6 – Objetos de Autorização (texto completo)
      IA_OBJ_AUT_01   = *_DOC.md  SEÇÃO 6 > coluna "Origem"  (tabela aninhada: 1 linha/objeto)
      IA_OBJ_AUT_02   = *_DOC.md  SEÇÃO 6 > coluna "Objeto"
      IA_OBJ_AUT_03   = *_DOC.md  SEÇÃO 6 > coluna "Campos"

MESMA LINHA DAS DEMAIS FERRAMENTAS (lc_CapCodeReview / lc_CapRemediation):
    - DETERMINÍSTICO-PRIMEIRO: a ET é montada só com fatos extraídos dos artefatos.
      Nada é inventado; campo sem insumo vira "Não informado". Zero alucinação.
    - Template: com IA (opcional), citado POR NOME no WORKSPACE_ID (RAG server-side);
      para produzir o .docx, o arquivo local em rag/ é obrigatório (o .docx precisa
      do arquivo físico do template). Template ausente => pendência bloqueadora.
    - LLM opcional (--llm-review): o PROMPT MESTRE oficial é enviado ao Generative
      Engine para "revisar e redigir" o campo narrativo (Objetivo). Desligado por
      padrão; o determinístico é o caminho canônico.
    - Fase a fase: --dry-run gera .docx/.md só com o determinístico (sem rede/.env).

COMO USAR:
    python lc_CapETGenerator.py --dry-run     # determinístico, sem credencial
    python lc_CapETGenerator.py               # idem (extração é determinística)
    python lc_CapETGenerator.py --llm-review  # + revisão opcional do Objetivo pela IA
    Lê et_output/01_ET_GERADA/artefatos e grava em et_output/01_ET_GERADA.
===============================================================================
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except Exception:
    pass


# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("et_generator")


def _quiet_http_logs(quiet: bool = True) -> None:
    """Abaixa (ou reativa) o volume de logs das bibliotecas de rede/IA. Sem isso,
    cada chamada HTTP interna imprimiria linhas de log irrelevantes para o usuário."""
    level = logging.WARNING if quiet else logging.INFO
    for noisy in ("httpx", "httpcore", "openai", "langchain", "langchain_openai", "urllib3"):
        logging.getLogger(noisy).setLevel(level)

_quiet_http_logs(True)


# ------------------------------------------------------------------------------
# Configuração (via .env / ambiente — tudo com padrão sensato)
# ------------------------------------------------------------------------------
def _env(name: str, default: str) -> str:
    """Lê uma variável de ambiente (definida no .env ou no sistema); se não
    existir, usa o valor 'default'. É o jeito padrão de tornar o programa
    configurável sem precisar mexer no código."""
    return os.getenv(name, default)


_DIR_DEFAULTS = {
    "ET_INBOUND_DIR": "et_source",
    "ET_OUTBOUND_DIR": "et_output",
    "DIR_ET_GERADA": "01_ET_GERADA",
    "DIR_ARTEFATOS": "artefatos",
    "DIR_CODE_REVIEW": "02_CODE_REVIEW",
    "DIR_TEMPLATE_LOCAL": "rag",   # pasta local do template .docx (padrão: rag/)
}


def project_dir() -> str:
    """Devolve a pasta onde este próprio arquivo .py está salvo (a raiz do
    projeto). Serve de ponto de partida para montar todos os outros caminhos."""
    return os.path.dirname(os.path.abspath(__file__))


def _dir_name(key: str) -> str:
    """Descobre o nome de uma pasta configurável (ex.: 'ET_OUTBOUND_DIR'): usa o
    que estiver na variável de ambiente, senão cai no padrão em _DIR_DEFAULTS."""
    v = os.environ.get(key)
    return str(v).strip() if v and str(v).strip() else _DIR_DEFAULTS[key]


def _is_inside(path: str, parent: str) -> bool:
    """Confere se 'path' está DENTRO da pasta 'parent' (usado para bloquear que a
    saída seja gravada, por engano, dentro da pasta de entrada)."""
    path = os.path.normpath(os.path.abspath(path))
    parent = os.path.normpath(os.path.abspath(parent))
    try:
        # commonpath acha o "ancestral comum" dos dois caminhos; se for igual ao
        # próprio 'parent', então 'path' está dentro dele.
        return os.path.commonpath([path, parent]) == parent
    except ValueError:
        # commonpath levanta erro se os caminhos estiverem em unidades/discos
        # diferentes (no Windows, por exemplo) — nesse caso, claramente não está dentro.
        return False


# Nomes de arquivo dos artefatos (compatíveis com extract.py / generate_docs.py).
FILE_PAYLOAD    = _env("FILE_PAYLOAD",    "_payload.json")
FILE_REQUISITOS = _env("FILE_REQUISITOS", "requisitos_extraidos.md")
FILE_OBJETOS    = _env("FILE_OBJETOS",    "objetos_extraidos.md")

# Valores FIXOS exigidos pelo prompt.
ET_AUTOR_FIXO = _env("ET_FIXED_AUTOR", _env("ET_AUTOR_FIXO", "Capgemini SAP AI Remediation"))
ET_VERSAO_FIXA = _env("ET_FIXED_VERSAO", _env("ET_VERSAO_FIXA", "1.0"))
ET_ANALISTA_FIXO = _env("ET_FIXED_ANALISTA", "")    # vazio => usa o Autor da EF

ET_TEMPLATE_NAME = _env("ET_TEMPLATE_NAME", "")

# Texto padrão para campos sem insumo (regra do prompt).
NAO_INFORMADO = _env("ET_NAO_INFORMADO", "Não informado")

LLM_BASE_URL   = _env("LLM_BASE_URL",   "https://openai.generative.engine.capgemini.com/v1")
LLM_MODEL_MAIN = _env("LLM_MODEL_MAIN", "us.anthropic.claude-sonnet-4-20250514-v1:0")
LLM_MAX_TOKENS = int(_env("LLM_MAX_TOKENS", "8192"))
ET_RETRY_ATTEMPTS = int(_env("ET_RETRY_ATTEMPTS", "4"))
ET_CALL_TIMEOUT_S = int(_env("ET_CALL_TIMEOUT_S", "180"))
SAP_TARGET_VERSION = _env("SAP_TARGET_VERSION", "SAP S/4HANA 2025 (Private Edition)")

# Base de conhecimento (RAG): o Template da ET vem primeiro. O servidor resolve
# pelo workspace-id. Só é usado no passo opcional --llm-review.
_DEFAULT_RAG_DOCUMENTS = (
    "LEROY_REL_INCLUIR MÓDULO_IDGAP_Template Especificação Técnica_DDMMAA_V02.docx",
    "Workbook ABAP_Move2S4_Final_v2.docx",
)
RAG_KNOWLEDGE_BASE = [d.strip() for d in
                      _env("RAG_DOCUMENTS", ",".join(_DEFAULT_RAG_DOCUMENTS)).split(",") if d.strip()]

# Os 16 marcadores do template oficial.
GLOBAL_KEYS = ("IA_AUTOR", "IA_VERSAO", "IA_DATA_ATUAL", "IA_FUNCIONAL", "IA_ANALISTA",
               "IA_ID_GAP", "IA_DESC_GAP", "IA_TRANSACOES_ENVOLVIDAS")
PEROBJ_KEYS = ("IA_OBJETOS_01", "IA_OBJETOS_NAME", "IA_OBJETOS_TIPO", "IA_OBJETOS_CLASS",
               "IA_TELA_SELECAO", "IA_TVARV", "IA_BRF", "IA_OBJ_AUT")
ALL_KEYS = GLOBAL_KEYS + PEROBJ_KEYS

MD_SEP = "#" + "-" * 114


def _validate_config() -> None:
    """Confere se os números vindos da configuração (.env) fazem sentido (todos
    maiores que zero). Se algum estiver errado, para o programa com uma mensagem
    clara, em vez de deixar o erro aparecer mais tarde de forma confusa."""
    # list comprehension: monta a lista de mensagens de erro só para os valores
    # inválidos, num único laço "para cada (nome, valor), se valor <= 0".
    errors = [f"{n} must be > 0 (got {v})"
              for n, v in (("LLM_MAX_TOKENS", LLM_MAX_TOKENS),
                           ("ET_RETRY_ATTEMPTS", ET_RETRY_ATTEMPTS),
                           ("ET_CALL_TIMEOUT_S", ET_CALL_TIMEOUT_S)) if v <= 0]
    if errors:
        raise ValueError("Configuration errors:\n" + "\n".join(f"  • {e}" for e in errors))


# ------------------------------------------------------------------------------
# Camada de IA (mesma plumbing das demais ferramentas; só no --llm-review)
# ------------------------------------------------------------------------------
def create_llm(session_id: str, model: str, max_tokens: int):
    """Monta a conexão com o servidor de IA da Capgemini (usada só quando
    --llm-review está ligado). O import do ChatOpenAI fica DENTRO da função (e não
    lá em cima do arquivo) para que o resto do programa funcione mesmo sem essa
    biblioteca instalada, no caminho 100% determinístico (sem IA)."""
    from langchain_openai import ChatOpenAI
    api_key = os.getenv("LLM_API_KEY")
    workspace_id = os.getenv("WORKSPACE_ID")
    if not api_key or not workspace_id:
        raise EnvironmentError("LLM_API_KEY and WORKSPACE_ID must be defined in .env")
    return ChatOpenAI(
        model=model, base_url=LLM_BASE_URL, api_key=api_key,
        max_tokens=max_tokens, temperature=0, timeout=ET_CALL_TIMEOUT_S,
        default_headers={"workspace-id": workspace_id, "session-id": session_id},
    )


def _finish_reason(response) -> str:
    """Descobre POR QUE a IA parou de responder ('stop' = terminou normalmente,
    'length' = foi cortada por falta de espaço). Protegido com try/except porque a
    estrutura exata da resposta pode variar; se não conseguir ler, assume 'stop'."""
    try:
        md = getattr(response, "response_metadata", {}) or {}
        return (md.get("finish_reason") or
                (getattr(response, "additional_kwargs", {}) or {}).get("finish_reason", "stop")).lower()
    except Exception:
        return "stop"


def _invoke(llm, system: str, user: str) -> tuple[str, str]:
    """Manda uma pergunta para a IA (uma instrução de sistema + a pergunta do
    usuário) e devolve (texto da resposta, motivo de ter parado). Usa a
    biblioteca 'tenacity' para tentar de novo automaticamente (com espera cada
    vez maior entre tentativas) se a chamada falhar por instabilidade de rede."""
    import tenacity
    from langchain_core.messages import HumanMessage, SystemMessage

    # O decorador @tenacity.retry "envolve" a função abaixo e a executa de novo em
    # caso de erro, até ET_RETRY_ATTEMPTS vezes; reraise=True mantém o erro
    # original se todas as tentativas falharem.
    @tenacity.retry(stop=tenacity.stop_after_attempt(ET_RETRY_ATTEMPTS),
                    wait=tenacity.wait_exponential(multiplier=1, min=2, max=30), reraise=True)
    def _call() -> tuple[str, str]:
        """Faz UMA tentativa de chamada à IA; existe separada só para que o
        @tenacity.retry acima consiga repeti-la sozinha em caso de falha."""
        resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content if isinstance(resp.content, str) else str(resp.content)
        return text, _finish_reason(resp)

    return _call()


def _parse_json_object(text: str) -> Optional[dict]:
    """Extrai um objeto JSON do texto que a IA respondeu, mesmo que ela tenha
    envolvido o JSON numa cerca de código markdown (```json ... ```). Devolve
    None se não achar nada que seja um JSON válido — nunca levanta erro aqui."""
    if not text:
        return None
    # As duas chamadas re.sub tiram, respectivamente, a cerca de abertura
    # ('```' ou '```json' no início) e a cerca de fechamento ('```' no fim).
    t = re.sub(r"\s*```$", "", re.sub(r"^```(?:json)?\s*", "", text.strip()).strip()).strip()
    start = t.find("{")                                  # acha onde o objeto JSON começa
    if start == -1:
        return None
    try:
        # raw_decode lê só o primeiro objeto JSON válido a partir de 'start',
        # ignorando qualquer texto extra que venha depois (ex.: comentários da IA).
        obj, _ = json.JSONDecoder().raw_decode(t, start)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


# ------------------------------------------------------------------------------
# Resolução do Template (local em rag/  ·  ou WORKSPACE_ID quando usa IA)
# ------------------------------------------------------------------------------
def _find_local_template(folder: str, name: str = "") -> Optional[str]:
    """Procura o arquivo .docx do template dentro da pasta indicada. Se um nome
    exato foi pedido (ET_TEMPLATE_NAME), usa esse; senão, "adivinha" qual é o
    template certo dando pontos para nomes que contenham palavras como
    'template', 'especifica' ou 'tecnica' — e escolhe o de maior pontuação."""
    if not folder or not os.path.isdir(folder):
        return None
    # list comprehension: lista todo arquivo .docx/.doc da pasta, ignorando
    # arquivos ocultos (começam com '.') e os temporários que o Word cria ('~$').
    files = [fn for fn in os.listdir(folder)
             if not fn.startswith((".", "~$")) and os.path.splitext(fn)[1].lower() in {".docx", ".doc"}]
    if not files:
        return None
    if name:
        for fn in files:
            if fn.lower() == name.lower():
                return os.path.join(folder, fn)

    def score(fn: str):
        """Dá uma pontuação a um nome de arquivo: quanto mais parecido com
        'template de Especificação Técnica', maior a pontuação."""
        low = fn.lower()
        s = (10 if "template" in low else 0) + (5 if ("especifica" in low or "_et_" in low) else 0) \
            + (3 if ("tecnica" in low or "técnica" in low) else 0)
        return (-s, low)                                 # negativo => sort() ordena do maior score pro menor

    files.sort(key=score)
    return os.path.join(folder, files[0])                # o de maior pontuação fica em 1º lugar


def resolve_local_template() -> dict:
    """O arquivo físico do template em rag/ (necessário para gerar o .docx)."""
    used = _dir_name("DIR_TEMPLATE_LOCAL")
    folder = os.path.join(project_dir(), used)
    name = ET_TEMPLATE_NAME.strip()
    path = None
    if name:
        cand = os.path.join(folder, name)
        if os.path.isfile(cand):
            path = cand
    if not path:
        path = _find_local_template(folder, name)
    return {"path": path, "name": os.path.basename(path) if path else (name or None), "dir": used}


def describe_template(tpl: dict, use_llm: bool) -> str:
    """Monta uma linha de texto legível descrevendo qual template está sendo
    usado (para aparecer no log), incluindo o workspace de IA quando aplicável."""
    ref = ""
    if use_llm:
        ws = (os.environ.get("WORKSPACE_ID") or "").strip() or "(WORKSPACE_ID)"
        ref = f"workspace {ws} / {RAG_KNOWLEDGE_BASE[0] if RAG_KNOWLEDGE_BASE else '(nome)'}  +  "
    if tpl.get("path"):
        return f"{ref}local {tpl['dir']}/{tpl['name']}"
    return (f"{ref}local {tpl['dir']}/ (arquivo .docx AUSENTE — sem .docx; "
            "coloque o template na pasta para gerar o documento final)")


# ------------------------------------------------------------------------------
# Estruturas de dados
# ------------------------------------------------------------------------------
@dataclass
class ObjEntry:
    """Um "cartão de dados" com tudo o que se sabe sobre UM objeto ABAP (uma
    classe, um relatório, etc.), juntando o que veio de objetos_extraidos.md com
    o que veio do *_DOC.md daquele objeto. O decorador @dataclass gera sozinho o
    construtor e outros métodos padrão, a partir só da lista de campos abaixo."""
    name: str                         # nome do objeto (objetos_extraidos.md)
    otype: str                        # tipo (objetos_extraidos.md)
    status: str                       # status/classificação (objetos_extraidos.md)
    doc_file: str = ""
    # extraídos do *_DOC.md:
    arquivo: str = ""                 # # Documentação Técnica > Arquivo
    doc_tipo: str = ""                # > Tipo do objeto
    doc_class: str = ""               # > Classificação
    entendimento: str = ""            # RESUMO EXECUTIVO > Entendimento
    md_detdev: str = ""               # SEÇÃO 2 (Detalhamento do Desenvolvimento)
    md_tela: str = ""                 # SEÇÃO 4
    md_tvarv: str = ""                # SEÇÃO 5
    md_brf: str = ""                  # SEÇÃO 5.3
    md_auth: str = ""                 # SEÇÃO 6


@dataclass
class Consolidated:
    """Junta TUDO que foi lido dos artefatos das etapas anteriores num único
    lugar: os dados de cabeçalho (autor, GAP, transações) + a lista de objetos
    (cada um um ObjEntry). É o que alimenta a montagem da ET."""
    autor_ef: str = ""                # requisitos ## Autor
    id_gap: str = ""                  # requisitos ## ID GAP
    desc_gap: str = ""                # requisitos ## Descrição GAP
    transacoes: str = ""             # requisitos ## Transações
    ef_file: str = ""                 # _payload.json ef_file (caminho relativo da EF)
    # field(default_factory=list): cada Consolidated novo ganha sua PRÓPRIA lista
    # vazia (usar só "= []" faria todos os Consolidated compartilharem a mesma lista).
    objects: list[ObjEntry] = field(default_factory=list)

    @property
    def n(self) -> int:
        """Quantos objetos foram encontrados. O @property permite chamar isto
        como 'c.n' (sem parênteses), como se fosse um campo comum."""
        return len(self.objects)


# ------------------------------------------------------------------------------
# CAMADA DETERMINÍSTICA — parse dos artefatos .md (custo ZERO, sem IA)
# ------------------------------------------------------------------------------
def _read_text(path: str) -> str:
    """Lê um artefato .md. Os artefatos são gravados em UTF-8 pelas etapas
    anteriores; se houver um byte anômalo isolado, usa UTF-8 com 'replace' (troca
    só o byte ruim por �) em vez de trocar de encoding — assim NUNCA mojibaka os
    acentos válidos do arquivo inteiro."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return ""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        log.warning("byte inválido em %s — decodificando UTF-8 com substituição.",
                    os.path.basename(path))
        return raw.decode("utf-8", errors="replace")


def _norm(s: str) -> str:
    """"Normaliza" um texto para comparação: tudo minúsculo e sem acentos. Assim,
    'Descrição' e 'descricao' são considerados o mesmo texto ao comparar rótulos."""
    s = (s or "").lower()
    for a, b in (("á", "a"), ("â", "a"), ("ã", "a"), ("à", "a"), ("é", "e"), ("ê", "e"),
                 ("í", "i"), ("ó", "o"), ("ô", "o"), ("õ", "o"), ("ú", "u"), ("ç", "c")):
        s = s.replace(a, b)
    return s


def _slice_between(md: str, start_marker: str, stop_markers: tuple[str, ...]) -> str:
    """Recorta o trecho de texto que vem DEPOIS de 'start_marker' e ANTES do
    primeiro dos 'stop_markers' que aparecer (ou até o fim do texto, se nenhum
    marcador de parada existir). É como usar Ctrl+F duas vezes e copiar o meio."""
    i = md.find(start_marker)
    if i == -1:                                          # marcador de início não existe => nada a recortar
        return ""
    body_start = i + len(start_marker)
    end = len(md)
    for sm in stop_markers:                               # acha o marcador de parada MAIS PRÓXIMO
        j = md.find(sm, body_start)
        if j != -1:
            end = min(end, j)
    return md[body_start:end].strip()


def _labeled_value(md: str, label: str) -> str:
    """Captura '**LABEL:** valor' até a próxima linha em branco. Ignora placeholders."""
    # re.escape evita que caracteres especiais do 'label' quebrem a expressão regular.
    # O padrão "(?=\n\s*\n|\Z)" é um "olha à frente sem consumir": para de capturar
    # assim que encontra uma linha em branco ou o fim do texto. re.S faz '.' casar
    # também quebras de linha (útil para valores em várias linhas).
    m = re.search(re.escape(f"**{label}:**") + r"\s*(.+?)(?=\n\s*\n|\Z)", md, re.S)
    if not m:
        return ""
    val = re.sub(r"\s+", " ", m.group(1)).strip()        # colapsa espaços/quebras em um único espaço
    return "" if val.startswith("_(") else val           # "_(...)" é um placeholder do template => trata como vazio


def _bullet_value(md: str, label: str) -> str:
    """Captura '- **LABEL:** valor' (cabeçalho do # Documentação Técnica)."""
    m = re.search(r"[-*]\s*\*\*" + re.escape(label) + r":\*\*\s*(.+)", md)
    if not m:
        return ""
    val = m.group(1).strip()
    return "" if val.startswith("_(") else val


def parse_requisitos(path: str) -> dict:
    """Lê requisitos_extraidos.md ('## Rótulo\\nvalor') em {rótulo: valor}."""
    md = _read_text(path)
    out: dict = {}
    if not md:
        return out
    # re.finditer percorre o texto achando TODOS os títulos '## Rótulo' (o "(?m)"
    # liga o modo multilinha, para que '^' e '$' casem início/fim de CADA linha).
    for m in re.finditer(r"(?m)^##\s+(.+?)\s*$", md):
        label = m.group(1).strip()
        start = m.end()
        # o valor do rótulo vai até o PRÓXIMO título '#' ou '##' (ou até o fim do arquivo).
        nxt = re.search(r"(?m)^#{1,2}\s+", md[start:])
        end = start + nxt.start() if nxt else len(md)
        val = md[start:end].strip()
        if val.startswith("_(") or _norm(val) in ("nao informado na ef",):
            val = ""                                     # placeholder do template => trata como vazio
        out[label] = val
    return out


def _req_lookup(req: dict, *needles: str) -> str:
    """Procura um valor no dicionário de requisitos, tentando várias grafias
    possíveis do rótulo (os 'needles', ex.: "id gap", "idgap", "gap"). '*needles'
    aceita quantos argumentos forem passados, viram uma tupla dentro da função.
    Primeiro tenta achar o rótulo IGUAL; se não achar nenhum, tenta um rótulo que
    apenas CONTENHA o texto procurado (mais flexível, porém mais arriscado)."""
    # dict comprehension: recria o dicionário com as chaves normalizadas
    # (minúsculas, sem acento), para comparar sem se importar com maiúscula/acento.
    nreq = {_norm(k): v for k, v in req.items()}
    for needle in needles:                              # match exato primeiro
        nn = _norm(needle)
        if nn in nreq and str(nreq[nn]).strip():
            return str(nreq[nn]).strip()
    for needle in needles:                              # depois contains
        nn = _norm(needle)
        for k, v in nreq.items():
            if nn in k and str(v).strip():
                return str(v).strip()
    return ""


def parse_doc_md(path: str) -> dict:
    """Lê um arquivo *_DOC.md (a documentação de UM objeto, gerada na Etapa 2) e
    extrai cada campo de interesse (arquivo, tipo, seções 2/4/5/5.3/6) recortando
    os trechos certos do markdown com as funções auxiliares acima."""
    md = _read_text(path)
    if not md:
        return {}
    return {
        "arquivo": _bullet_value(md, "Arquivo"),
        "doc_tipo": _bullet_value(md, "Tipo do objeto"),
        "doc_class": _bullet_value(md, "Classificação"),
        "entendimento": _labeled_value(md, "Entendimento"),
        "md_detdev": _slice_between(md, "### SEÇÃO 2 – Detalhamento do Desenvolvimento",
                                    ("### SEÇÃO 3",)),
        "md_tela": _slice_between(md, "### SEÇÃO 4 – Tela de Seleção", ("### SEÇÃO 5",)),
        "md_tvarv": _slice_between(md, "### SEÇÃO 5 – TVARV", ("### SEÇÃO 5.3", "### SEÇÃO 6")),
        "md_brf": _slice_between(md, "### SEÇÃO 5.3 – BRF", ("### SEÇÃO 6",)),
        "md_auth": _slice_between(md, "### SEÇÃO 6 – Objetos de Autorização", ()),
    }


def parse_objetos_md(path: str) -> list[dict]:
    """Lê a tabela de objetos_extraidos.md -> [{nome, tipo, status, doc}]."""
    md = _read_text(path)
    out: list[dict] = []
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if set(cells[0]) <= {"-", ":", " "}:            # separador
            continue
        if "nome do objeto" in _norm(cells[1]):         # cabeçalho
            continue
        nome = cells[1].strip("` ")
        out.append({"nome": nome, "tipo": cells[2], "status": cells[3],
                    "doc": cells[4].strip("` ") if len(cells) > 4 else ""})
    return out


def load_consolidated(artifacts_dir: str) -> Consolidated:
    """A FUNÇÃO QUE JUNTA TUDO: lê o _payload.json, o requisitos_extraidos.md e
    todos os *_DOC.md dos objetos, e devolve um único Consolidated pronto para
    montar a ET. É o ponto de entrada da camada determinística de leitura."""
    payload_path = os.path.join(artifacts_dir, FILE_PAYLOAD)
    payload = {}
    if os.path.isfile(payload_path):
        # "with open(...) as fh" abre o arquivo e garante que ele é fechado
        # sozinho no final do bloco, mesmo se der erro no meio.
        with open(payload_path, encoding="utf-8") as fh:
            payload = json.load(fh)                      # transforma o texto JSON em dict/list Python

    req = parse_requisitos(os.path.join(artifacts_dir, FILE_REQUISITOS))
    c = Consolidated(
        autor_ef=_req_lookup(req, "autor"),
        id_gap=_req_lookup(req, "id gap", "idgap", "gap"),
        desc_gap=_req_lookup(req, "descrição gap", "descricao gap", "descrição do gap", "descrição"),
        transacoes=_req_lookup(req, "transações", "transacoes", "transação", "transacao"),
        ef_file=payload.get("ef_file") or "",
    )

    # backbone dos objetos: payload (confiável) + fallback objetos_extraidos.md
    # Se o _payload.json não tiver a lista de objetos, cai para ler a tabela do
    # markdown objetos_extraidos.md (menos estruturado, mas serve de reserva).
    objs = payload.get("objects") or []
    if not objs:
        for o in parse_objetos_md(os.path.join(artifacts_dir, FILE_OBJETOS)):
            objs.append({"name_no_ext": o["nome"], "type": o["tipo"],
                         "status": o["status"], "doc_file": o["doc"]})

    for obj in objs:
        entry = ObjEntry(
            name=obj.get("name_no_ext") or obj.get("file_name") or "?",
            otype=obj.get("type") or "Objeto ABAP",
            status=obj.get("status") or ("Remediação" if obj.get("remediation") else "Novo"),
            doc_file=obj.get("doc_file") or "",
        )
        doc_path = os.path.join(artifacts_dir, entry.doc_file) if entry.doc_file else ""
        if doc_path and os.path.isfile(doc_path):
            p = parse_doc_md(doc_path)
            entry.arquivo = p.get("arquivo", "")
            entry.doc_tipo = p.get("doc_tipo", "")
            entry.doc_class = p.get("doc_class", "")
            entry.entendimento = p.get("entendimento", "")
            entry.md_detdev = p.get("md_detdev", "")
            entry.md_tela = p.get("md_tela", "")
            entry.md_tvarv = p.get("md_tvarv", "")
            entry.md_brf = p.get("md_brf", "")
            entry.md_auth = p.get("md_auth", "")
        else:
            log.warning("DOC do objeto '%s' não encontrado (%s).",
                        entry.name, entry.doc_file or "sem doc_file")
        c.objects.append(entry)
    return c


# ------------------------------------------------------------------------------
# Markdown -> texto legível (para preencher células do .docx sem tabelas cruas)
# ------------------------------------------------------------------------------
def _md_to_plain(text: str) -> str:
    """Converte um trecho de markdown em texto simples e legível, pronto para
    entrar numa célula do Word: remove cercas de código, transforma tabelas em
    linhas separadas por " · ", tira '**negrito**'/'`código`' e junta linhas em
    branco repetidas em uma só. É uma "tradução" de markdown para texto puro."""
    if not text:
        return ""
    lines_out: list[str] = []
    for raw in text.splitlines():
        s = raw.rstrip()
        if not s.strip():
            lines_out.append("")
            continue
        if s.lstrip().startswith("```"):                 # cerca de código (```): descarta
            continue
        # "set(s.strip()) <= {...}" confere se a linha só tem esses caracteres
        # (ou seja, é uma linha separadora de tabela tipo '|---|---|', sem conteúdo real).
        if set(s.strip()) <= {"|", "-", ":", " "}:      # separador de tabela markdown
            continue
        if s.lstrip().startswith("|"):                   # linha de tabela -> " · "
            cells = [c.strip() for c in s.strip().strip("|").split("|")]
            s = " · ".join(c for c in cells if c)
        s = s.replace("**", "").replace("`", "")
        lines_out.append(s)
    out: list[str] = []                                  # colapsa linhas em branco repetidas
    for ln in lines_out:
        if ln == "" and (not out or out[-1] == ""):
            continue
        out.append(ln)
    return "\n".join(out).strip()


def _strip_numbering(title: str) -> str:
    """Remove a numeração de seção do início do título (ex.: '2.1 Visão geral' ->
    'Visão geral'). Cobre '2', '2.1', '2.1.3', com '.', ')' ou '-' opcionais."""
    return re.sub(r"^\s*\d+(?:\.\d+)*[.)\-]?\s+", "", title).strip()


def _parse_detdev_blocks(md_secao2: str) -> list[tuple[str, str]]:
    """Divide a SEÇÃO 2 em blocos (título da subseção '#### X', corpo). DESCARTA a
    subseção '#### Fonte' (código-fonte). Cada bloco vira (título, corpo_em_texto).
    Sem subseções '####', devolve um único bloco sem título. A numeração de seção
    ('2.1', '2.2'…) é removida do título."""
    if not md_secao2 or not md_secao2.strip():
        return []
    # re.split com um grupo capturado (a parte entre parênteses) devolve, ao
    # dividir o texto, tanto os pedaços quanto os títulos '####' capturados,
    # intercalados: [antes, título1, corpo1, título2, corpo2, ...].
    parts = re.split(r"(?m)^\s*####\s+(.+?)\s*$", md_secao2)
    if len(parts) == 1:                                  # nenhuma subseção ####
        plain = _md_to_plain(md_secao2)
        return [("", plain)] if plain else []
    result: list[tuple[str, str]] = []
    pre = _md_to_plain(parts[0])
    if pre:
        result.append(("", pre))
    # Truque para percorrer a lista aos pares (título, corpo): criar UM único
    # iterador e usá-lo duas vezes no zip — cada zip() puxa o próximo item dele,
    # então "title" pega os índices pares e "body" os ímpares da mesma sequência.
    it = iter(parts[1:])
    for title, body in zip(it, it):
        title = _strip_numbering(title.strip())
        if _norm(title).startswith("fonte"):             # descarta #### Fonte
            continue
        result.append((title, _md_to_plain(body)))
    return result


def _parse_auth_rows(md_secao6: str) -> list[dict]:
    """Lê a tabela da SEÇÃO 6 (| Origem | Objeto | Campos |) -> lista de linhas."""
    rows: list[dict] = []
    if not md_secao6:
        return rows
    for line in md_secao6.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip().strip("`").strip() for c in s.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if set("".join(cells)) <= {"-", ":", " "}:       # separador
            continue
        if _norm(cells[0]) == "origem" and _norm(cells[1]) == "objeto":
            continue                                     # cabeçalho
        rows.append({"origem": cells[0], "objeto": cells[1], "campos": cells[2]})
    return rows


def _auth_columns(rows: list[dict]) -> tuple[str, str, str]:
    """Junta as colunas (uma linha por objeto de autorização) para o layout de
    células soltas {{IA_OBJ_AUT_01/02/03}}."""
    if not rows:
        return ("Não foram encontradas referências.", "-", "-")
    origem = "\n".join(r["origem"] for r in rows if r["origem"]) or "-"
    objeto = "\n".join(r["objeto"] for r in rows if r["objeto"]) or "-"
    campos = "\n".join(r["campos"] for r in rows if r["campos"]) or "-"
    return (origem, objeto, campos)


# ------------------------------------------------------------------------------
# Montagem dos campos (determinístico, fiel ao prompt)
# ------------------------------------------------------------------------------
def build_fields(c: Consolidated, today: str) -> tuple[dict, list[dict], str, list]:
    """Retorna (global_fields, per_object_fields[], inventário, detdev_blocks[])."""
    global_fields = {
        "IA_AUTOR": ET_AUTOR_FIXO,
        "IA_VERSAO": ET_VERSAO_FIXA,
        "IA_DATA_ATUAL": today,
        "IA_FUNCIONAL": c.autor_ef or NAO_INFORMADO,
        "IA_ANALISTA": ET_ANALISTA_FIXO or c.autor_ef or NAO_INFORMADO,
        "IA_ID_GAP": c.id_gap or NAO_INFORMADO,
        "IA_DESC_GAP": c.desc_gap or NAO_INFORMADO,
        "IA_TRANSACOES_ENVOLVIDAS": c.transacoes or NAO_INFORMADO,
    }
    per_object: list[dict] = []
    detdev_list: list = []
    for o in c.objects:
        detdev_list.append(_parse_detdev_blocks(o.md_detdev))
        auth_o, auth_ob, auth_c = _auth_columns(_parse_auth_rows(o.md_auth))
        per_object.append({
            "IA_OBJETOS_01": o.entendimento or NAO_INFORMADO,
            "IA_OBJETOS_NAME": o.arquivo or o.name or NAO_INFORMADO,
            "IA_OBJETOS_TIPO": o.doc_tipo or o.otype or NAO_INFORMADO,
            "IA_OBJETOS_CLASS": o.doc_class or o.status or NAO_INFORMADO,
            "IA_TELA_SELECAO": _md_to_plain(o.md_tela) or "Não se aplica.",
            "IA_TVARV": _md_to_plain(o.md_tvarv) or "Não foram encontradas referências.",
            "IA_BRF": _md_to_plain(o.md_brf) or "Não foram encontradas referências.",
            "IA_OBJ_AUT": _md_to_plain(o.md_auth) or "Não foram encontradas referências.",
            "IA_OBJ_AUT_01": auth_o,
            "IA_OBJ_AUT_02": auth_ob,
            "IA_OBJ_AUT_03": auth_c,
        })
    inventory = "\n".join(f"{o.name} — {o.otype} — {o.status}" for o in c.objects) or NAO_INFORMADO
    return global_fields, per_object, inventory, detdev_list


# ------------------------------------------------------------------------------
# CAMADA IA (OPCIONAL) — "revisar e redigir" o Objetivo (PROMPT MESTRE)
#
#   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#   PROMPT MESTRE OFICIAL (Renato) — usado SÓ com --llm-review. O determinístico
#   já preenche todos os marcadores; aqui a IA apenas refina a prosa do Objetivo
#   (IA_OBJETOS_01) por objeto, citando o Template/Workbook por nome no workspace.
#   >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# ------------------------------------------------------------------------------
def _rag_source_list() -> str:
    """Monta a lista, em texto, dos documentos de referência (RAG) que a IA deve
    consultar antes de escrever — um por linha, com um traço na frente."""
    return "\n".join(f"    - {d}" for d in RAG_KNOWLEDGE_BASE)


ET_SYSTEM_ROLE = (
    "Você é um especialista sênior SAP (ABAP Clássico, RAP, CAP, CPI, Event Mesh, "
    "Fiori Elements/Freestyle), responsável por revisar e redigir a Especificação "
    "Técnica (ET) de programas que passaram pelo Code Inspector, seguindo ESTRITAMENTE "
    "o Template oficial. Consulte a base de conhecimento (RAG) do workspace POR NOME "
    f"antes de escrever:\n{_rag_source_list()}\n"
    "Baseie-se SOMENTE nos insumos recebidos; não invente regras, objetos, telas, "
    "transações, campos, tabelas, classes ou evidências. Quando faltar informação, "
    "registre como pendência/premissa, nunca como fato. Responda em português do Brasil, "
    "técnico, claro e objetivo. Saída em JSON ONLY — sem prosa fora do JSON, sem cercas."
)


def build_review_prompt(c: Consolidated) -> str:
    """Monta o texto do pedido que será enviado à IA no passo --llm-review: para
    cada objeto, pede para reescrever o campo "Objetivo do desenvolvimento" a
    partir do que já foi extraído, e exige a resposta em um formato JSON fixo
    (para o Python conseguir ler de volta de forma confiável, sem "adivinhação")."""
    blocks = []
    for i, o in enumerate(c.objects):                    # enumerate dá o índice (i) junto com cada item (o)
        blocks.append(f'  {{"idx": {i}, "objeto": "{o.name}", "tipo": "{o.otype}", '
                      f'"status": "{o.status}", "entendimento": '
                      f'{json.dumps(o.entendimento or "", ensure_ascii=False)}}}')
    objs = ",\n".join(blocks)
    return f"""GAP {c.id_gap or '(n/d)'} — "{c.desc_gap or '(n/d)'}".
Para cada objeto abaixo, redija o campo "Objetivo do desenvolvimento" da ET: 1-2 \
parágrafos técnicos em PT-BR, a partir do "entendimento" fornecido, sem inventar. \
Consulte o Template/Workbook pelo nome (na sua system role).

OBJETOS:
[
{objs}
]

Retorne SOMENTE um JSON EXATAMENTE neste schema:
{{"objetivos": [ {{"idx": <int>, "IA_OBJETOS_01": "<Objetivo em PT-BR>"}} ]}}
Regra: um item por objeto, mesmo idx; nada fora do JSON."""


def llm_review_objetivos(llm, c: Consolidated, per_object: list[dict]) -> int:
    """Refina IA_OBJETOS_01 de cada objeto. Devolve quantos foram refinados."""
    try:
        raw, finish = _invoke(llm, ET_SYSTEM_ROLE, build_review_prompt(c))
    except Exception as e:
        log.warning("revisão IA indisponível: %s", e)
        return 0
    if finish == "length":
        log.warning("revisão truncada (length) — aumente LLM_MAX_TOKENS.")
    parsed = _parse_json_object(raw)
    if not parsed:
        log.warning("revisão IA sem JSON válido — mantendo extração determinística.")
        return 0
    n = 0
    for item in parsed.get("objetivos", []) or []:
        idx = item.get("idx")
        val = item.get("IA_OBJETOS_01")
        if isinstance(idx, int) and 0 <= idx < len(per_object) and isinstance(val, str) and val.strip():
            per_object[idx]["IA_OBJETOS_01"] = val.strip()
            n += 1
    return n


# ------------------------------------------------------------------------------
# Renderização — DOCX (principal) e Markdown (pré-visualização)
# ------------------------------------------------------------------------------
def _md_stamp() -> str:
    """Monta o comentário de cabeçalho do markdown (invisível quando renderizado,
    já que '<!-- -->' é um comentário HTML), com a data/hora de geração."""
    d = datetime.now().strftime("%d/%m/%Y %H:%M")
    return (f"<!-- Capgemini SAP AI — Gerador de ET | Projeto MOVE2S4 | Gerado em {d} -->\n"
            f"<!-- Alvo: {SAP_TARGET_VERSION} -->\n\n")


def render_markdown(global_fields: dict, per_object: list[dict], inventory: str,
                    detdev_list: list, preliminary: bool) -> str:
    """Monta o arquivo .md de pré-visualização da ET, juntando os campos já
    calculados numa lista de linhas de texto (L) que no final é unida com "\\n".
    Fica marcado como 'PRELIMINAR' quando o .docx final não pôde ser gerado
    (template ausente) — assim o usuário sabe que aquele markdown não é a entrega
    oficial, é só um preview."""
    g = global_fields
    L = [_md_stamp(), "# Especificação Técnica — Projeto MOVE2S/4", ""]
    if preliminary:
        L += ["> **ANÁLISE PRELIMINAR** — Template oficial (.docx) não encontrado em "
              f"`{_dir_name('DIR_TEMPLATE_LOCAL')}/`. Este markdown NÃO é a ET final; "
              "coloque o template na pasta para gerar o documento final. "
              "**Pendência bloqueadora.**", ""]
    L += ["| Campo | Valor |", "|-------|-------|",
          f"| **Autor** | {g['IA_AUTOR']} |",
          f"| **Funcional** | {g['IA_FUNCIONAL']} |",
          f"| **Analista TI** | {g['IA_ANALISTA']} |",
          f"| **ID GAP** | {g['IA_ID_GAP']} |",
          f"| **Descrição GAP** | {g['IA_DESC_GAP']} |",
          f"| **Versão** | {g['IA_VERSAO']} |",
          f"| **Data** | {g['IA_DATA_ATUAL']} |", ""]
    L += ["## 1. Identificação dos Objetos Técnicos Envolvidos", "",
          f"- **Transações envolvidas:** {g['IA_TRANSACOES_ENVOLVIDAS']}", "",
          "**Objetos técnicos envolvidos:**", ""]
    L += [f"- {ln}" for ln in inventory.splitlines()] + [""]
    L += ["## 2. Detalhamento Técnico", ""]
    for i, po in enumerate(per_object):
        L += [f"### {po['IA_OBJETOS_NAME']}", "",
              f"- **Objetivo do desenvolvimento:** {po['IA_OBJETOS_01']}",
              f"- **Nome do Objeto:** {po['IA_OBJETOS_NAME']}",
              f"- **Tipo do Objeto:** {po['IA_OBJETOS_TIPO']}",
              f"- **Classificação:** {po['IA_OBJETOS_CLASS']}", "",
              "**Detalhamento do Desenvolvimento:**", ""]
        blocks = detdev_list[i] if i < len(detdev_list) else []
        if blocks:
            for title, body in blocks:
                if title:
                    L += [f"**{title}**", ""]
                if body:
                    L += [body, ""]
        else:
            L += [NAO_INFORMADO, ""]
        L += ["**Tela de Seleção:**", "", po["IA_TELA_SELECAO"], "",
              "**TVARV:**", "", po["IA_TVARV"], "",
              "**BRF+:**", "", po["IA_BRF"], "",
              "**Objetos de Autorização:**", "", po["IA_OBJ_AUT"], ""]
    return "\n".join(L)


# --- DOCX: preenchimento robusto a runs fragmentados + tabela por objeto ------
# NOTA SOBRE O WORD (biblioteca python-docx): um parágrafo (paragraph) no Word é
# dividido internamente em "runs" — pedaços de texto com a mesma formatação
# (negrito, fonte, cor...). O problema é que o Word às vezes quebra uma MESMA
# palavra em vários runs sem motivo aparente (ex.: por causa do corretor
# ortográfico). Isso significa que procurar um marcador "{{IA_XXX}}" run por run
# pode falhar, porque o marcador pode estar espalhado entre 2 ou 3 runs. As
# funções abaixo contornam isso juntando o texto de TODOS os runs do parágrafo
# antes de procurar/substituir, e depois reescrevem tudo no primeiro run.
def _set_paragraph_text(paragraph, text: str) -> None:
    """Escreve 'text' num parágrafo (mantendo a formatação do 1º run); '\\n' vira quebra."""
    for r in paragraph.runs:
        r.text = ""                                      # esvazia todos os runs existentes...
    if not paragraph.runs:
        paragraph.add_run("")                             # ...garante que existe pelo menos 1 run
    first = paragraph.runs[0]
    parts = (text or "").split("\n")
    first.text = parts[0]                                 # a 1ª linha vai no run (preserva a formatação dele)
    for extra in parts[1:]:                                # as linhas seguintes viram quebras manuais (Shift+Enter)
        first.add_break()
        first.add_text(extra)


def _replace_in_paragraph(paragraph, mapping: dict) -> None:
    """Substitui {{IA_*}} num parágrafo, mesmo com o Word fragmentando em vários runs."""
    runs = paragraph.runs
    if not runs:
        return
    full = "".join(r.text for r in runs)                  # junta o texto de todos os runs, ignorando a fragmentação
    if "{{" not in full:                                  # atalho: sem chave dupla, não há marcador aqui
        return
    new = full
    for key, val in mapping.items():
        token = "{{" + key + "}}"
        if token in new:
            new = new.replace(token, "" if val is None else str(val))
    if new != full:
        _set_paragraph_text(paragraph, new)               # só reescreve o parágrafo se algo realmente mudou


def _iter_cell_paragraphs(cell):
    """Percorre (yield = "vai devolvendo um por um", sem montar uma lista inteira
    na memória) todos os parágrafos de uma célula de tabela, incluindo os de
    tabelas ANINHADAS dentro dela (tabela dentro de célula, comum em templates Word)."""
    for p in cell.paragraphs:
        yield p
    for nt in cell.tables:                      # recursa em tabelas ANINHADAS
        for row in nt.rows:
            for c in row.cells:
                yield from _iter_cell_paragraphs(c)        # "yield from": repassa os itens de outro gerador


def _iter_all_paragraphs(doc):
    """Percorre TODOS os parágrafos do documento inteiro: os soltos + os de
    dentro de cada célula de cada tabela (usado para os marcadores globais, que
    podem aparecer em qualquer lugar do template)."""
    for p in doc.paragraphs:
        yield p
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                yield from _iter_cell_paragraphs(cell)


def _fill_table_element(tbl_el, parent, mapping: dict) -> None:
    """Preenche os marcadores {{IA_*}} de todas as células de uma tabela XML
    bruta (tbl_el), reconstruindo o objeto Table do python-docx em cima dela."""
    from docx.table import Table
    t = Table(tbl_el, parent)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                _replace_in_paragraph(p, mapping)


def _append_detdev_blocks(paragraph, blocks: list) -> None:
    """Escreve os blocos da SEÇÃO 2 num parágrafo: TÍTULO da subseção em NEGRITO,
    seguido do corpo (texto normal), uma linha em branco entre blocos."""
    if not blocks:
        paragraph.add_run(NAO_INFORMADO)
        return
    for i, (title, body) in enumerate(blocks):
        if i > 0:
            paragraph.add_run().add_break()             # linha em branco entre blocos
        if title:
            tr = paragraph.add_run(title)               # add_run cria um novo "pedaço de texto" formatável
            tr.bold = True                              # título da subseção em negrito
            if body:
                tr.add_break()
        if body:
            parts = body.split("\n")
            br = paragraph.add_run(parts[0])
            for extra in parts[1:]:
                br.add_break()
                br.add_text(extra)


def _render_detdev_paragraph(paragraph, blocks: list) -> None:
    """Substitui {{IA_DET_DEV}} preservando qualquer texto antes/depois do marcador,
    e escreve os blocos formatados (títulos em negrito)."""
    full = "".join(r.text for r in paragraph.runs)
    token = "{{IA_DET_DEV}}"
    if token not in full:
        return
    idx = full.find(token)
    prefix, suffix = full[:idx], full[idx + len(token):]
    # Remove FISICAMENTE cada run do XML do parágrafo (r._element.getparent()
    # acessa o elemento XML "pai" e .remove tira o run dele) — precisamos
    # apagar tudo porque vamos reconstruir o parágrafo do zero, run por run.
    for r in list(paragraph.runs):                       # zera os runs existentes
        r._element.getparent().remove(r._element)
    if prefix:
        paragraph.add_run(prefix)
    _append_detdev_blocks(paragraph, blocks)
    if suffix:
        paragraph.add_run(suffix)


def _fill_auth_nested(t, auth_rows: list) -> bool:
    """Se a tabela de Detalhamento tiver uma tabela ANINHADA de autorização (com
    {{IA_OBJ_AUT_01}}), replica a linha-protótipo por objeto de autorização e
    remove as linhas vazias. Devolve True se encontrou/tratou a tabela aninhada."""
    for row in t.rows:
        for cell in row.cells:
            for nt in cell.tables:
                proto_tr = None
                # "any(...)" devolve True se QUALQUER célula da linha contiver o
                # marcador — é assim que achamos a linha-modelo (o "protótipo")
                # que será clonada, uma vez por objeto de autorização.
                for r in nt.rows:
                    if any("IA_OBJ_AUT_01" in c.text for c in r.cells):
                        proto_tr = r._tr                 # ._tr é o elemento XML bruto <w:tr> da linha
                        break
                if proto_tr is None:
                    continue
                tbl = nt._tbl
                for r in list(nt.rows):                  # remove linhas vazias
                    tr = r._tr
                    joined = "".join(c.text for c in r.cells)
                    if tr is proto_tr:
                        continue
                    if _norm(joined).startswith("origem") or "objeto" in _norm(joined) and "campos" in _norm(joined):
                        continue                         # cabeçalho
                    if joined.strip() == "":
                        tbl.remove(tr)
                rows = auth_rows or [{"origem": "Não foram encontradas referências.",
                                      "objeto": "-", "campos": "-"}]
                # copy.deepcopy clona a linha INTEIRA (com toda a formatação) no
                # XML; addnext insere o clone logo depois da âncora atual, e a
                # âncora avança para o clone — assim as linhas ficam em sequência,
                # uma para cada registro de auth_rows.
                anchor = proto_tr
                trs = [proto_tr]
                for _ in range(len(rows) - 1):
                    clone = copy.deepcopy(proto_tr)
                    anchor.addnext(clone)
                    anchor = clone
                    trs.append(clone)
                for tr, ar in zip(trs, rows):
                    _fill_tr(tr, {"IA_OBJ_AUT_01": ar["origem"],
                                  "IA_OBJ_AUT_02": ar["objeto"],
                                  "IA_OBJ_AUT_03": ar["campos"]})
                return True
    return False


def _fill_detalhamento_table(tbl_el, parent, mapping: dict, detdev_blocks: list,
                             auth_rows: list) -> None:
    """Preenche uma tabela de Detalhamento: {{IA_DET_DEV}} com formatação (negrito
    nos títulos), a tabela aninhada de autorização por linha, o resto por
    substituição simples de marcadores."""
    from docx.table import Table
    t = Table(tbl_el, parent)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if "IA_DET_DEV" in p.text:
                    _render_detdev_paragraph(p, detdev_blocks)
                else:
                    _replace_in_paragraph(p, mapping)
    _fill_auth_nested(t, auth_rows)


def _find_detalhamento(doc):
    """A tabela do Detalhamento é a que contém {{IA_OBJETOS_01}}."""
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                if "IA_OBJETOS_01" in cell.text:
                    return t
    return None


def _fill_tr(tr, mapping: dict) -> None:
    """Preenche os {{IA_*}} de uma LINHA (tr) de tabela, célula a célula."""
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    # qn("w:tc")/qn("w:p") traduzem os nomes curtos ('w:tc' = célula, 'w:p' =
    # parágrafo) para o nome completo que o XML do Word exige internamente
    # (com o "namespace"). findall procura esses elementos dentro da linha (tr).
    for tc in tr.findall(qn("w:tc")):
        for p_el in tc.findall(qn("w:p")):
            _replace_in_paragraph(Paragraph(p_el, None), mapping)


def _find_objlist_nested(doc):
    """Acha a tabela ANINHADA da linha 'Objetos técnicos envolvidos' (a que tem
    {{IA_OBJETOS_NM01}}) e a linha-protótipo com os placeholders."""
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for nt in cell.tables:
                    for r in nt.rows:
                        for c in r.cells:
                            if "IA_OBJETOS_NM01" in c.text:
                                return nt, r._tr
    return None, None


def _fill_objlist_nested(doc, objects: list) -> bool:
    """Preenche a lista de objetos na tabela aninhada da Identificação: replica a
    linha-protótipo (NM01/TP01/ST01) uma vez por objeto e remove as linhas vazias.
    Devolve False se a tabela aninhada não existir (aí usamos o fallback em célula)."""
    nt, proto_tr = _find_objlist_nested(doc)
    if nt is None:
        return False
    tbl = nt._tbl
    # remove linhas de dados VAZIAS (mantém cabeçalho e o protótipo)
    for r in list(nt.rows):
        tr = r._tr
        joined = "".join(c.text for c in r.cells)
        if tr is proto_tr or "nome do objeto" in _norm(joined):
            continue
        if joined.strip() == "":
            tbl.remove(tr)
    # replica o protótipo por objeto
    anchor = proto_tr
    trs = [proto_tr]
    for _ in range(max(1, len(objects)) - 1):
        clone = copy.deepcopy(proto_tr)
        anchor.addnext(clone)
        anchor = clone
        trs.append(clone)
    for tr, o in zip(trs, objects or [None]):
        m = ({"IA_OBJETOS_NM01": o.name, "IA_OBJETOS_TP01": o.otype, "IA_OBJETOS_ST01": o.status}
             if o is not None else
             {"IA_OBJETOS_NM01": NAO_INFORMADO, "IA_OBJETOS_TP01": "", "IA_OBJETOS_ST01": ""})
        _fill_tr(tr, m)
    return True


def _fill_inventory_cell_fallback(doc, inventory: str) -> None:
    """Fallback (só se NÃO houver tabela aninhada): escreve a lista de objetos na
    célula-valor da linha 'Objetos técnicos envolvidos'."""
    for t in doc.tables:
        for row in t.rows:
            cells = row.cells
            if len(cells) >= 2 and "objetos tecnicos envolvidos" in _norm(cells[0].text):
                if cells[-1].tables:      # tem tabela aninhada -> não escreve texto solto
                    return
                if cells[-1].text.strip() and "{{" not in cells[-1].text:
                    return
                _set_paragraph_text(cells[-1].paragraphs[0], inventory)
                return


def _new_paragraph_element():
    """Cria um elemento XML de parágrafo vazio (<w:p>) do zero. É usado como
    "separador" entre duas tabelas clonadas — sem ele, o Word funde as tabelas
    adjacentes visualmente em uma só."""
    from docx.oxml import OxmlElement
    return OxmlElement("w:p")


def fill_docx(template_path: str, global_fields: dict, per_object: list[dict],
              objects: list, inventory: str, detdev_list: list, out_path: str) -> None:
    """Preenche o template: cabeçalho/identificação (global) + Detalhamento por objeto.
    Não altera o layout do template; apenas substitui marcadores e REPLICA a tabela
    de Detalhamento uma vez por objeto (com parágrafo separador entre tabelas)."""
    from docx import Document
    doc = Document(template_path)                        # abre o arquivo .docx do template (a "folha em branco" a preencher)

    det = _find_detalhamento(doc)
    if det is None:
        raise ValueError("template sem tabela de Detalhamento ({{IA_OBJETOS_01}}) — "
                         "verifique se é o template oficial da ET.")
    proto = det._tbl
    parent = det._parent

    # 1) Replica o protótipo (pristino) para os objetos 2..N, com separador entre tabelas.
    n = max(1, len(per_object))
    anchor = proto
    table_elems = [proto]
    for _ in range(n - 1):
        spacer = _new_paragraph_element()   # Word funde tabelas adjacentes sem <w:p> no meio
        anchor.addnext(spacer)
        clone = copy.deepcopy(proto)
        spacer.addnext(clone)
        anchor = clone
        table_elems.append(clone)

    # 2) Preenche os marcadores GLOBAIS em todo o documento (não toca nos per-objeto).
    for p in _iter_all_paragraphs(doc):
        _replace_in_paragraph(p, global_fields)

    # 3) Preenche cada tabela de Detalhamento com os campos do seu objeto
    #    ({{IA_DET_DEV}} com títulos em negrito; tabela aninhada de autorização por linha).
    for tbl_el, mapping, blocks, obj in zip(table_elems, per_object or [{}],
                                            detdev_list or [[]], objects or [None]):
        auth_rows = _parse_auth_rows(obj.md_auth) if obj is not None else []
        _fill_detalhamento_table(tbl_el, parent, mapping, blocks, auth_rows)

    # 4) Lista de objetos: tabela ANINHADA (NM01/TP01/ST01) da Identificação —
    #    replica a linha por objeto e remove as vazias; senão, fallback em célula.
    if not _fill_objlist_nested(doc, objects):
        _fill_inventory_cell_fallback(doc, inventory)

    doc.save(out_path)


# ------------------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------------------
class LayoutError(ValueError):
    """Um erro específico para quando as pastas de entrada/saída estão
    configuradas de um jeito perigoso (ex.: saída dentro da pasta de entrada).
    Herdar de ValueError permite tratá-lo tanto de forma específica quanto como
    um erro de valor comum, conforme o chamador preferir."""
    pass


@dataclass
class ETTarget:
    """Guarda os TRÊS caminhos que definem "onde ler e onde gravar": a pasta raiz
    do projeto, a pasta com os artefatos de entrada e a pasta de saída da ET."""
    project: str
    artifacts_dir: str
    out_dir: str


def resolve_et_layout(input_dir: Optional[str], output_dir: Optional[str]) -> ETTarget:
    """Calcula as pastas de entrada e saída da ET, usando os caminhos passados
    por linha de comando (--input/--output) se existirem, senão os padrões do
    projeto. Também bloqueia, por segurança, gravar a saída dentro da pasta de
    entrada (et_source/), o que poderia misturar/sobrescrever dados de origem."""
    project = project_dir()
    outbound = os.path.join(project, _dir_name("ET_OUTBOUND_DIR"))
    et_gerada = os.path.join(outbound, _dir_name("DIR_ET_GERADA"))
    artifacts = os.path.abspath(input_dir) if input_dir else \
        os.path.join(et_gerada, _dir_name("DIR_ARTEFATOS"))
    out_dir = os.path.abspath(output_dir) if output_dir else et_gerada
    inbound = os.path.join(project, _dir_name("ET_INBOUND_DIR"))
    if _is_inside(out_dir, inbound):
        raise LayoutError("recusando escrever a ET dentro de et_source/ (só entrada).")
    return ETTarget(project=project, artifacts_dir=artifacts, out_dir=out_dir)


def _et_basename(c: Consolidated) -> str:
    """Monta o nome-base dos arquivos de saída (sem extensão): 'ET_' + o nome do
    arquivo da EF (sem extensão), ex.: 'ET_LEROY_REL_SD-034 - Trava ..._V2'.
    Só caracteres proibidos em nomes de arquivo (Windows/Linux) viram '_'.
    Sem EF, cai no formato 'ET_GAP123_19082026' (ID do GAP + data de hoje)."""
    ef_stem = os.path.splitext(os.path.basename(c.ef_file))[0] if c.ef_file else ""
    ef_stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", ef_stem).strip(" ._")
    if ef_stem:
        return f"ET_{ef_stem}"
    gap = re.sub(r"[^A-Za-z0-9_-]+", "_", c.id_gap).strip("_") or "GAP"
    return f"ET_{gap}_{datetime.now().strftime('%d%m%Y')}"


# ------------------------------------------------------------------------------
# Orquestração
# ------------------------------------------------------------------------------
def generate_et(target: ETTarget, dry_run: bool, llm_review: bool, want_md: bool) -> Optional[dict]:
    """A ORQUESTRAÇÃO PRINCIPAL: lê os artefatos, monta os campos, opcionalmente
    pede à IA para refinar o texto do Objetivo, e por fim grava o .docx (se o
    template existir) e/ou o .md de pré-visualização. Devolve um dicionário com
    os caminhos gerados e o status, ou None se não havia nenhum objeto a documentar."""
    c = load_consolidated(target.artifacts_dir)
    if c.n == 0:
        log.warning("nenhum objeto encontrado nos artefatos — nada a gerar.")
        return None

    today = datetime.now().strftime("%d/%m/%Y")
    global_fields, per_object, inventory, detdev_list = build_fields(c, today)

    # Revisão opcional pela IA (só o Objetivo; template citado por nome no workspace).
    reviewed = 0
    if llm_review and not dry_run:
        session_id = str(uuid.uuid4())
        llm = create_llm(session_id, LLM_MODEL_MAIN, LLM_MAX_TOKENS)
        log.info("revisão IA do Objetivo (IA_OBJETOS_01) para %d objeto(s)…", c.n)
        reviewed = llm_review_objetivos(llm, c, per_object)

    os.makedirs(target.out_dir, exist_ok=True)
    base = _et_basename(c)
    tpl = resolve_local_template()
    outputs = {"docx": None, "md": None, "consolidated": c, "reviewed": reviewed,
               "blocking": None}

    # DOCX (principal): exige o template físico local.
    if tpl.get("path"):
        try:
            docx_path = os.path.join(target.out_dir, base + ".docx")
            fill_docx(tpl["path"], global_fields, per_object, c.objects, inventory,
                      detdev_list, docx_path)
            outputs["docx"] = docx_path
            log.info("ET (docx): %s  [template: %s]", docx_path, tpl["name"])
        except Exception as e:
            log.error("falha ao preencher o .docx (%s): %s", tpl.get("name"), e)
            outputs["blocking"] = f"falha ao preencher o template: {e}"
    else:
        # Regra do prompt: template ausente => pendência BLOQUEADORA; não fabricar ET.
        outputs["blocking"] = ("Template oficial de ET não fornecido ou insuficiente para "
                               f"geração final (coloque o .docx em {tpl['dir']}/).")
        log.error("%s", outputs["blocking"])

    # Markdown de pré-visualização (sempre útil; marcado 'preliminar' se sem docx).
    if want_md:
        md_path = os.path.join(target.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as fh:
            fh.write(render_markdown(global_fields, per_object, inventory, detdev_list,
                                     preliminary=outputs["docx"] is None))
        outputs["md"] = md_path
        log.info("ET (markdown%s): %s",
                 " — PRELIMINAR" if outputs["docx"] is None else "", md_path)
    return outputs


def main() -> None:
    """O PONTO DE PARTIDA do programa quando rodado pela linha de comando: lê os
    argumentos (--dry-run, --llm-review, etc.), prepara as pastas, chama
    generate_et() e imprime o resumo final no log. É o "maestro" que liga a
    leitura dos artefatos, a montagem dos campos e a geração dos arquivos."""
    # argparse é a biblioteca padrão do Python para ler as opções digitadas na
    # linha de comando (ex.: "python lc_CapETGenerator.py --llm-review"); cada
    # add_argument descreve uma opção aceita e o texto de ajuda (--help).
    ap = argparse.ArgumentParser(description="Gerador de ET (.docx) — MOVE2S4")
    ap.add_argument("--dry-run", action="store_true",
                    help="Só determinístico (sem rede/.env). A extração já é determinística.")
    ap.add_argument("--llm-review", action="store_true",
                    help="Passo opcional: IA revisa/redige o Objetivo (template no WORKSPACE_ID).")
    ap.add_argument("--input", default=None,
                    help="Pasta dos artefatos (padrão: et_output/01_ET_GERADA/artefatos).")
    ap.add_argument("--output", default=None,
                    help="Pasta de saída (padrão: et_output/01_ET_GERADA).")
    ap.add_argument("--no-md", action="store_true", help="Não gerar o markdown de pré-visualização.")
    ap.add_argument("--verbose", action="store_true", help="Reativa o log HTTP das bibliotecas.")
    args = ap.parse_args()                                # lê de fato os argumentos passados na chamada do script

    _quiet_http_logs(not args.verbose)
    _validate_config()
    try:
        target = resolve_et_layout(args.input, args.output)
    except LayoutError as e:                              # pastas de entrada/saída configuradas de forma perigosa
        log.error("%s", e)
        return 2

    tpl = resolve_local_template()
    use_llm = args.llm_review and not args.dry_run
    log.info("=" * 80)
    log.info("  Capgemini SAP AI — Gerador de ET")
    log.info("=" * 80)
    log.info("  Projeto     : %s", target.project)
    log.info("  Artefatos   : %s", target.artifacts_dir)
    log.info("  Saída       : %s", target.out_dir)
    log.info("  Modo        : %s", "DRY-RUN (determinístico)" if args.dry_run else "COMPLETO")
    log.info("  Template ET : %s", describe_template(tpl, use_llm))
    if use_llm:
        log.info("  Revisão IA  : ON (%s) · RAG: %d doc(s) via workspace-id",
                 LLM_MODEL_MAIN, len(RAG_KNOWLEDGE_BASE))
    log.info("=" * 80)

    if not os.path.isdir(target.artifacts_dir):
        log.error("Artefatos não encontrados: %s — rode extract.py/generate_docs.py antes.",
                  target.artifacts_dir)
        return 2

    try:
        out = generate_et(target, args.dry_run, use_llm, want_md=not args.no_md)
    except Exception as e:                                # rede-de-segurança: qualquer erro inesperado vira log + saída controlada
        log.error("falha ao gerar a ET: %s", e, exc_info=True)
        return 1

    log.info("=" * 80)
    if out is None:
        log.info("Nenhuma ET gerada.")
        return 1
    c = out["consolidated"]
    log.info("RESUMO: GAP %s — %d objeto(s)", c.id_gap or "?", c.n)
    log.info("  DOCX     : %s", out["docx"] or "(NÃO gerado)")
    log.info("  Markdown : %s", out["md"] or "(não gerado)")
    if out["reviewed"]:
        log.info("  Objetivos refinados pela IA: %d/%d", out["reviewed"], c.n)
    if out["blocking"]:
        log.warning("  PENDÊNCIA BLOQUEADORA: %s", out["blocking"])
        log.info("=" * 80)
        return 1                                    # bloqueia o pipeline (sem ET final)
    log.info("  ET gerada com todos os marcadores preenchidos. 🟩")
    log.info("=" * 80)
    return 0


if __name__ == "__main__":
    # Este bloco só roda quando o arquivo é executado DIRETAMENTE (não quando é
    # importado por outro módulo). sys.exit(...) encerra o processo devolvendo o
    # código de saída de main() ao sistema operacional (0 = sucesso, outro = erro);
    # "main() or 0" garante saída 0 mesmo se main() não devolver nada (None).
    import sys as _sys
    _sys.exit(main() or 0)