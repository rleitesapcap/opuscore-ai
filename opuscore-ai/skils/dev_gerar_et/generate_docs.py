# -*- coding: utf-8 -*-
"""
===============================================================================
 generate_docs.py — ETAPA 2: analisa o código e preenche os DOCs de análise.
===============================================================================

Roda DEPOIS do extract.py. Para cada objeto, a LLM preenche o esqueleto gerado
em ET_OUTBOUND_DIR/DIR_ET_GERADA/DIR_ARTEFATOS/*_DOC.md
(o mesmo layout do extract.py; padrão: et_output/01_ET_GERADA/artefatos):

  📌 RESUMO EXECUTIVO
      Entendimento · Contexto de Negócio · Avaliação Geral
  📊 RELATÓRIO ESTRUTURADO DE VALIDAÇÃO
      SEÇÃO 1 – Resumo do Desenvolvimento (tabela Status | Ponto | Observação)
      SEÇÃO 2 – Detalhamento (blocos Word-friendly; fonte RAG genérica;
                 na remediação preserva os blocos ABAP)
      SEÇÃO 3 – Observações Técnicas (tabela)
      SEÇÃO 4 – Tela de Seleção (Report; fato do extract.py)
      SEÇÃO 5 – TVARV · SEÇÃO 5.3 – BRF · SEÇÃO 6 – Objetos de Autorização
                 (fatos do extract.py; a LLM não sobrescreve)

SEGUE O MESMO MODELO DA REMEDIAÇÃO:
  - CHUNKERS: usa o abap_chunker.py para cortar ABAP clássico (FORM/METHOD/...).
    CDS / BDEF / DCL / DDLX / SRVD NÃO passam pelo cortador ABAP.
  - LLM DA CAPGEMINI: llm_providers.py (Generative Engine, workspace-id).
  - FUNIL DE CUSTO: modelo BARATO resume unidades grandes; modelo FORTE sintetiza.
  - Valida o acesso ANTES de processar.
  - Campos da EF (payload.ef_values) entram no prompt de síntese.

Config (.env; mesmas variáveis do lc_CapRemediation):
  LLM_PROVIDER        capgemini (default) | anthropic | claude_code
  LLM_API_KEY         chave do Generative Engine (capgemini)
  WORKSPACE_ID        workspace do Generative Engine (capgemini)
  ANTHROPIC_API_KEY   (provider anthropic)
  LLM_MODEL           modelo de SÍNTESE (forte). Se omitido, default do provider.
  LLM_MODEL_ANALYSIS  modelo de ANÁLISE por unidade (barato). Se omitido, usa o
                      mesmo de síntese.
  LLM_MAX_TOKENS      opcional (default do provider = 8192)
  LLM_TEMPERATURE     opcional ('off' para omitir)
  DOC_MAX_UNIT_CHARS  tamanho máx. por unidade antes de cortar (default 6000)
  LLM_PROVIDERS_PATH  caminho do llm_providers.py (se não estiver ao lado)
  ABAP_CHUNKER_PATH   caminho do abap_chunker.py (se não estiver ao lado)
  ET_INBOUND_DIR / ET_OUTBOUND_DIR
  DIR_EF / DIR_CODIGOS / DIR_ET_GERADA / DIR_ARTEFATOS / DIR_CODE_REVIEW
  FILE_REQUISITOS / FILE_ACHADOS / FILE_PENDENCIAS / FILE_RESULTADO
  ET_TEMPLATE_NAME    nome do template no WORKSPACE_ID (quando usa LLM)
  DIR_TEMPLATE_LOCAL  pasta local do .docx sem LLM (padrão: rap/ na raiz)

Uso:
  python generate_docs.py [--dry-run]
  python generate_docs.py [--only NOME1,NOME2] [--force]
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import os
import re
import sys


# ----------------------------------------------------------------------------
# .env e carregamento dos módulos do projeto (llm_providers, abap_chunker)
# ----------------------------------------------------------------------------

def load_dotenv(path):
    """Lê um arquivo ".env" (configurações tipo CHAVE=valor, uma por linha) e
    coloca cada valor nas variáveis de ambiente do processo Python.

    Não é preciso instalar nenhuma biblioteca extra para isso: a função lê o
    arquivo linha a linha "na mão". Linhas vazias, que começam com "#"
    (comentário) ou que não têm um "=" são ignoradas. `setdefault` só grava a
    variável se ela AINDA NÃO existir no ambiente — ou seja, se alguém já
    tiver exportado a variável antes de rodar o script, o .env não sobrescreve.
    """
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            # "=" separa a linha em NOME e VALOR; o "1" limita a divisão a uma
            # única quebra, então um valor que contenha "=" não é cortado ao meio.
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def load_sibling_module(mod_name):
    """Carrega o .py ao lado de generate_docs.py, ignorando PYTHONPATH.

    Em Python, normalmente você importaria um módulo com `import doc_analysis`,
    mas isso deixa a escolha de QUAL arquivo carregar por conta do interpretador
    (ele procura em PYTHONPATH, pasta atual, etc.) — o que é arriscado aqui,
    porque pode existir outro doc_analysis.py em outro lugar do computador.
    `importlib.util` é a forma "manual" de carregar um módulo por CAMINHO DE
    ARQUIVO exato, sem ambiguidade: sempre o arquivo que está do lado deste.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{mod_name}.py")
    if not os.path.isfile(path):
        return None, None
    spec = importlib.util.spec_from_file_location(mod_name, path)  # "planta" de como carregar
    mod = importlib.util.module_from_spec(spec)                     # cria o módulo vazio
    sys.modules[mod_name] = mod            # registra, para outros `import mod_name` reaproveitarem
    spec.loader.exec_module(mod)           # executa o arquivo .py, preenchendo o módulo
    return mod, path


def call_analyze_object(analyze_fn, **kwargs):
    """Chama analyze_object só com kwargs que a função realmente aceita.

    Evita TypeError se um doc_analysis antigo (PYTHONPATH / remediação) for
    carregado sem et_template / ef_values.
    """
    # `**kwargs` recebe qualquer quantidade de argumentos nomeados numa espécie
    # de dicionário. `inspect.signature` é a forma do Python "espiar" quais
    # parâmetros uma função aceita, SEM chamá-la — útil aqui porque a versão do
    # doc_analysis.py carregada pode ser mais antiga e não aceitar todos os
    # argumentos novos (et_template, ef_values); chamar com um argumento que a
    # função não conhece daria erro (TypeError).
    sig = inspect.signature(analyze_fn)
    if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
        # A função tem um "**kwargs" próprio (aceita qualquer coisa) => passa tudo.
        return analyze_fn(**kwargs)
    # Senão, filtra o dicionário para manter só as chaves que existem na assinatura.
    accepted = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return analyze_fn(**accepted)


def load_project_module(mod_name, explicit_path, env_var, root):
    """Carrega um módulo .py do projeto (mesmos usados pela remediação).
    Procura em: --path explícito, env_var, dir do script, CWD, raiz."""
    candidates = []
    # Monta a lista de "lugares possíveis" onde o arquivo pode estar, na ordem
    # de prioridade: argumento de linha de comando, variável de ambiente,
    # pasta deste script, pasta atual (CWD) e raiz do projeto.
    for c in (explicit_path, os.environ.get(env_var),
              os.path.dirname(os.path.abspath(__file__)), os.getcwd(), root):
        if not c:
            continue
        # Se `c` for uma pasta, monta o caminho completo pasta/arquivo.py;
        # se já for um caminho de arquivo, usa como está.
        p = os.path.join(c, f"{mod_name}.py") if os.path.isdir(c) else c
        if os.path.isfile(p) and os.path.basename(p) == f"{mod_name}.py":
            candidates.append(p)
    for p in candidates:
        # Tenta carregar cada candidato, um de cada vez; se algum falhar (por
        # exemplo, um arquivo corrompido), avisa e tenta o próximo em vez de
        # travar o programa inteiro.
        try:
            spec = importlib.util.spec_from_file_location(mod_name, p)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)
            return mod, p
        except Exception as e:  # noqa
            print(f"aviso: falha ao carregar {p}: {e}", file=sys.stderr)
    # Nenhum candidato funcionou: como último recurso, tenta o `import` normal
    # do Python (que busca em PYTHONPATH). Se nem isso existir, desiste (None).
    try:
        mod = importlib.import_module(mod_name)
        return mod, "PYTHONPATH"
    except ImportError:
        return None, None


# ----------------------------------------------------------------------------
# Preenchimento do DOC de 4 seções (preserva cabeçalho e blocos de código)
# ----------------------------------------------------------------------------

# A LLM pode escrever o "status" de uma linha de várias formas (em português,
# com/sem acento, em caixa baixa...). Este dicionário traduz QUALQUER uma
# dessas variações para um emoji fixo, para a tabela final ficar padronizada.
STATUS_ICON = {
    "ok": "✅", "verde": "✅", "adequado": "✅", "conforme": "✅",
    "aviso": "⚠️", "alerta": "⚠️", "atencao": "⚠️", "atenção": "⚠️", "amarelo": "⚠️",
    "erro": "❌", "falha": "❌", "critico": "❌", "crítico": "❌", "vermelho": "❌",
}


def _coerce_prose(value):
    """Converte o que a LLM devolveu (str, list, dict ou None) em texto Markdown.
    A LLM às vezes devolve uma seção como lista de blocos ou de dicts."""
    # "Coerce" = forçar um valor para um formato específico. A IA responde em
    # JSON, e o mesmo campo pode vir ora como texto puro, ora como lista, ora
    # como dicionário (a IA não é 100% consistente no formato) — esta função
    # padroniza tudo isso para uma única string de texto (prosa em Markdown),
    # que é o que o resto do programa espera colar no documento Word.
    if value is None:
        return ""
    if isinstance(value, str):     # `isinstance` pergunta "esse valor é do tipo X?"
        return value.strip()
    if isinstance(value, list):
        parts = []
        for it in value:
            if it is None:
                continue
            if isinstance(it, str):
                parts.append(it.strip())
            elif isinstance(it, dict):
                # Cada par chave/valor do dicionário vira uma linha "- **chave:** valor".
                seg = [f"- **{k}:** {_coerce_prose(v)}" for k, v in it.items()]
                parts.append("\n".join(seg))
            else:
                parts.append(str(it))
        return "\n\n".join(p for p in parts if p)
    if isinstance(value, dict):
        # Chamada RECURSIVA: a função se chama de novo para tratar os valores
        # internos do dicionário, que por sua vez podem ser strings, listas...
        return "\n".join(f"- **{k}:** {_coerce_prose(v)}" for k, v in value.items())
    return str(value)


# ----------------------------------------------------------------------------
# SEÇÃO 2 – Detalhamento: fonte RAG genérica + Markdown pronto para o Word
# ----------------------------------------------------------------------------

# Texto FIXO que sempre deve aparecer como "fonte" no documento final, no
# lugar de qualquer nome de arquivo/PDF/template real que a IA tenha citado.
# É uma regra de segurança/confidencialidade: o cliente não deve ver nomes de
# arquivos internos da base de conhecimento da Capgemini.
RAG_SOURCE_LABEL = "Generative AI RAG Document Capgemini"

# Títulos de documentos do workspace RAG / template. Nunca devem aparecer na
# SEÇÃO 2; se a LLM citar, substituímos por RAG_SOURCE_LABEL.
_KNOWN_RAG_STEMS = (
    "Clean core extensibility for SAP S_4HANA Cloud",
    "Clean core extensibility for SAP S/4HANA Cloud",
    "Extend SAP S_4HANA in the cloud and on premise with ABAP based extensions",
    "Extend SAP S/4HANA in the cloud and on premise with ABAP based extensions",
    "ABAP_Cloud_API_Enablement_Guidelines",
    "ABAP Cloud API Enablement Guidelines",
    "ABAP Cloud API Enablement Guidelines for SAP S_4HANA Cloud Private Edition and SAP S_4HANA",
    "ABAP Cloud API Enablement Guidelines for SAP S/4HANA Cloud Private Edition, and SAP S/4HANA",
    "CONV_OP2025",
    "Workbook ABAP_Move2S4_Final",
    "Workbook_ABAP_Move2S4_Final",
    "Workbook ABAP Move2S4 Final",
    "From Classic ABAP to ABAP",
    "Workbook RAG",
)

# Todas as expressões abaixo são REGEX (expressões regulares): um "mini
# idioma" para descrever padrões de texto e encontrá-los/trocá-los. Compilar
# com `re.compile` de antemão (fora das funções) evita recompilar o mesmo
# padrão toda vez que a função roda — é só uma otimização de performance.

# Acha uma linha inteira do tipo "Fonte RAG: nome do documento" (em várias
# variações de escrita), para trocar por RAG_SOURCE_LABEL.
_RAG_SOURCE_LINE_RE = re.compile(
    r"(?im)^\s*(?:\*+\s*)?(?:RAG\s*Source|Fonte\s*RAG|Knowledge[\s-]*base|"
    r"Base\s*RAG|Documento\s*RAG)\s*[:\-–]\s*.+$"
)
# Acha qualquer coisa que "parece nome de arquivo" terminando em .pdf/.doc/
# .docx/.xls/.xlsx/.ppt/.pptx — para apagar referências a arquivos internos
# que a IA tenha citado soltas no meio do texto (não só em linha "Fonte:").
_DOC_FILENAME_RE = re.compile(
    r"(?i)\b[\w][\w ._\-/\\]{0,120}\.(?:pdf|docx?|xlsx?|pptx?)\b"
)
_HEADING_LINE_RE = re.compile(r"^(#{2,6})\s+(.*)$")     # título Markdown: ## até ######
_BOLD_LABEL_RE = re.compile(r"^\*\*(.+?):\*\*\s*(.*)$")  # linha tipo "**Rótulo:** texto"
_BULLET_RE = re.compile(r"^\s*[-*•]\s+")                 # item de lista com -, * ou •
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+")              # item de lista numerada: "1. " ou "1) "
_FONTE_TITLES = {
    "fonte", "source", "fonte rag", "referência", "referencia",
    "referências", "referencias", "referência / fonte", "referencia / fonte",
}


def _env_rag_document_names():
    """Nomes configurados no .env (RAG, workbook, template) — também sanitizados."""
    names = []
    for key in ("RAG_DOCUMENTS", "ET_TEMPLATE_NAME", "NAMING_WORKBOOK_NAME"):
        raw = (os.environ.get(key) or "").strip()
        if not raw:
            continue
        if key == "RAG_DOCUMENTS":
            names.extend(p.strip() for p in raw.split(",") if p.strip())
        else:
            names.append(raw)
    return names


def sanitize_rag_names(text):
    """Remove nomes de PDFs/workbooks/templates RAG do texto da SEÇÃO 2.

    Qualquer citação de documento da base vira exatamente RAG_SOURCE_LABEL.
    """
    if not text:
        return ""
    # "\x00" é um caractere invisível (nunca aparece em texto normal), usado
    # aqui como um MARCADOR TEMPORÁRIO. Truque: em vez de já trocar tudo por
    # RAG_SOURCE_LABEL (que é um texto longo), primeiro trocamos por esse
    # marcador curto e único — assim, se o mesmo trecho for "achado" de novo
    # por outra regex mais adiante, ele não é encontrado (achou-se) duas
    # vezes, e no final trocamos o marcador pelo texto de verdade, uma única vez.
    placeholder = "\x00RAG_SRC\x00"
    out = str(text).replace(RAG_SOURCE_LABEL, placeholder)

    out = _RAG_SOURCE_LINE_RE.sub(f"**Fonte:** {placeholder}", out)

    stems = list(_KNOWN_RAG_STEMS)
    stems.extend(_env_rag_document_names())
    # Mais longos primeiro para não deixar restos de títulos compostos.
    stems = sorted({s.strip() for s in stems if s and s.strip()}, key=len, reverse=True)
    for stem in stems:
        stem_no_ext = re.sub(r"\.(?:pdf|docx?|xlsx?|pptx?)$", "", stem, flags=re.I)
        if not stem_no_ext:
            continue
        # `re.escape` transforma o nome do documento num padrão literal (trata
        # caracteres especiais de regex, como parênteses, como texto comum),
        # e ainda aceita o nome com ou sem a extensão do arquivo no final.
        pat = re.compile(
            re.escape(stem_no_ext) + r"(?:\.(?:pdf|docx?|xlsx?|pptx?))?",
            re.I,
        )
        out = pat.sub(placeholder, out)

    out = _DOC_FILENAME_RE.sub(placeholder, out)
    # Se sobrarem vários marcadores seguidos (ex.: "doc1, doc2, doc3" viraram
    # "MARCADOR, MARCADOR, MARCADOR"), colapsa tudo num único marcador — senão
    # o texto final repetiria "Generative AI RAG Document Capgemini" 3 vezes.
    out = re.sub(
        r"(?:%s)(?:\s*[,;/|]\s*(?:%s))+" % (re.escape(placeholder), re.escape(placeholder)),
        placeholder,
        out,
    )
    return out.replace(placeholder, RAG_SOURCE_LABEL)   # troca final: marcador -> texto oficial


def _is_fonte_title(titulo):
    """True se o "título" de um bloco for só a palavra Fonte/Source/Referência
    (em qualquer capitalização), indicando que o bloco não tem conteúdo de
    verdade — é só uma citação de fonte que o Python já cuida de gerar no
    rodapé da SEÇÃO 2 (ver format_detalhamento_for_word)."""
    t = re.sub(r"^2\.\d+\s+", "", (titulo or "").strip(), flags=re.I).strip().lower()
    t = t.strip(":-– ")
    return t in _FONTE_TITLES


def _is_fonte_only_text(text):
    """True se o trecho só cita a fonte RAG (já emitimos o bloco Fonte no final)."""
    t = re.sub(r"[*_`]", "", text or "")
    t = re.sub(r"\s+", " ", t).strip().strip(":-–,. ")
    low = t.lower()
    if not low:
        return False
    if _is_fonte_title(t):
        return True
    label = RAG_SOURCE_LABEL.lower()
    if low == label:
        return True
    if low in (f"fonte {label}", f"fonte: {label}"):
        return True
    if low.startswith("fonte") and label in low and len(low) < len(label) + 20:
        return True
    return False


def _as_str_list(value):
    """Transforma qualquer coisa (texto, lista, dict, None) numa lista de
    strings "limpas" (sem itens vazios). Serve para padronizar campos que
    deveriam ser uma lista de parágrafos ou de itens de lista, mas que a IA
    pode devolver de formas diferentes — inclusive como um único bloco de
    texto com várias linhas em branco separando os parágrafos."""
    if value is None:
        return []
    if isinstance(value, str):
        # Quebra o texto em parágrafos onde houver 2+ quebras de linha seguidas
        # (ou seja, uma linha em branco separando parágrafos).
        parts = [p.strip() for p in re.split(r"\n{2,}", value) if p.strip()]
        return parts or ([value.strip()] if value.strip() else [])
    if isinstance(value, list):
        out = []
        for it in value:
            if it is None:
                continue
            if isinstance(it, str):
                if it.strip():
                    out.append(it.strip())
            else:
                # Item da lista não é string (por exemplo, é um dict) — usa a
                # função de "coerção" para virar texto antes de guardar.
                s = _coerce_prose(it)
                if s:
                    out.append(s)
        return out
    s = _coerce_prose(value)
    return [s] if s else []


def _normalize_bloco(it):
    """Um bloco Word: titulo + parágrafos curtos + lista de itens."""
    # `it` pode chegar em vários formatos possíveis vindos da IA: nada, um
    # texto solto, ou (o caso mais comum) um dicionário com título/parágrafos/
    # itens — mas usando nomes de chave que variam (título em inglês, em
    # português, "heading", "secao" com ou sem acento...). Esta função tenta
    # reconhecer todas essas variações e devolver sempre o MESMO formato:
    # {"titulo": str, "paragrafos": [str, ...], "itens": [str, ...]}.
    if it is None:
        return None
    if isinstance(it, str):
        text = it.strip()
        return {"titulo": "", "paragrafos": [text], "itens": []} if text else None
    if not isinstance(it, dict):
        text = str(it).strip()
        return {"titulo": "", "paragrafos": [text], "itens": []} if text else None

    # O `or` em cadeia pega o primeiro valor "verdadeiro" (não vazio) entre as
    # possíveis chaves de título que a IA poderia ter usado.
    titulo = str(
        it.get("titulo") or it.get("title") or it.get("heading")
        or it.get("secao") or it.get("seção") or ""
    ).strip()
    paras = it.get("paragrafos") or it.get("paragraphs") or it.get("texto") or it.get("text")
    itens = it.get("itens") or it.get("items") or it.get("bullets") or it.get("lista")
    if paras is None and itens is None:
        # Nenhuma das chaves conhecidas apareceu: pode ser que a IA tenha
        # usado nomes de campo totalmente diferentes. `leftover` junta tudo
        # que sobrou (exceto título/fonte) para não perder informação —
        # melhor mostrar algo "cru" do que descartar o conteúdo.
        leftover = {
            k: v for k, v in it.items()
            if k not in (
                "titulo", "title", "heading", "secao", "seção",
                "fonte", "source", "paragrafos", "paragraphs", "texto", "text",
                "itens", "items", "bullets", "lista",
            )
        }
        if leftover:
            paras = [_coerce_prose(leftover)]
        elif titulo:
            paras = []
        else:
            paras = [_coerce_prose(it)]
    paras = _as_str_list(paras)
    itens = _as_str_list(itens)
    if not titulo and not paras and not itens:
        return None    # bloco totalmente vazio -> descarta (None em vez de dict)
    return {"titulo": titulo, "paragrafos": paras, "itens": itens}


def _split_plain_lines(text):
    """Separa um blob em parágrafos vs. itens de lista."""
    # Percorre o texto linha por linha, acumulando linhas "normais" num
    # `buf` (buffer/rascunho temporário) até juntar tudo num parágrafo — isso
    # acontece quando encontra uma linha em branco ou um item de lista.
    # Linhas que começam com marcador de lista (- * • ou "1.") viram itens.
    paras, itens = [], []
    buf = []
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line.strip():
            if buf:
                paras.append(" ".join(buf).strip())   # fecha o parágrafo acumulado
                buf = []
            continue
        if _BULLET_RE.match(line) or _NUMBERED_RE.match(line):
            if buf:
                paras.append(" ".join(buf).strip())
                buf = []
            itens.append(_BULLET_RE.sub("", _NUMBERED_RE.sub("", line)).strip())
        else:
            buf.append(line.strip())
    if buf:
        paras.append(" ".join(buf).strip())    # não esquece o último parágrafo pendente
    return [p for p in paras if p], [i for i in itens if i]


def _blocos_from_markdown(text):
    """Interpreta Markdown livre em blocos {titulo, paragrafos, itens}."""
    # Às vezes a IA devolve o campo "detalhamento" já como um texto Markdown
    # solto (com "## Título" ou "**Título:**" espalhados), em vez de um JSON
    # estruturado em blocos. Esta função "lê" esse texto de cima a baixo e
    # recorta em blocos sempre que encontra um novo título.
    text = (text or "").strip()
    if not text:
        return []
    lines = text.splitlines()
    blocos = []
    cur_title = ""
    cur_lines = []

    def flush():
        # `flush()` é uma função DENTRO da função (uma "função aninhada"):
        # ela existe só para não repetir este trecho de código toda vez que
        # um bloco termina. `nonlocal` avisa o Python que `cur_title` e
        # `cur_lines` NÃO são variáveis novas daqui de dentro — são as mesmas
        # de fora, e serão alteradas aqui também (sem isso, o Python criaria
        # cópias locais e o valor "de fora" nunca mudaria).
        nonlocal cur_title, cur_lines
        body = "\n".join(cur_lines).strip()
        if not cur_title and not body:
            cur_lines = []
            return
        paras, itens = _split_plain_lines(body) if body else ([], [])
        blocos.append({"titulo": cur_title, "paragrafos": paras, "itens": itens})
        cur_title = ""
        cur_lines = []

    for line in lines:
        heading = _HEADING_LINE_RE.match(line.strip())
        bold = _BOLD_LABEL_RE.match(line.strip())
        if heading:
            # Achou um "## Algo": fecha o bloco anterior e começa um novo.
            flush()
            cur_title = heading.group(2).strip()
            continue
        if bold and not line.strip().startswith("**Fonte:**"):
            # Achou "**Rótulo:** texto" (menos quando o rótulo é "Fonte", que
            # é tratado à parte): também conta como início de um novo bloco.
            flush()
            cur_title = bold.group(1).strip()
            rest = bold.group(2).strip()
            cur_lines = [rest] if rest else []
            continue
        cur_lines.append(line)
    flush()   # não esquece de fechar o último bloco depois do laço terminar
    return [b for b in blocos if b.get("titulo") or b.get("paragrafos") or b.get("itens")]


def _normalize_detalhamento(value):
    """Aceita str / list / dict da LLM e devolve {blocos: [...]}."""
    # Esta é a função "guarda-chuva" da normalização da SEÇÃO 2: ela decide,
    # olhando o TIPO do valor recebido, qual caminho seguir para chegar sempre
    # no mesmo formato final {"blocos": [{"titulo", "paragrafos", "itens"}, ...]}.
    if value is None:
        return {"blocos": []}
    if isinstance(value, dict):
        # Caso A: já veio como {"blocos": [...]} (ou "secoes"/"sections") — usa direto.
        raw = value.get("blocos") or value.get("secoes") or value.get("seções") or value.get("sections")
        if raw is not None:
            blocos = [_normalize_bloco(b) for b in (raw if isinstance(raw, list) else [raw])]
            return {"blocos": [b for b in blocos if b]}
        # Caso B: o próprio dict JÁ É um bloco único (tem "titulo"/"paragrafos" direto).
        if any(k in value for k in ("titulo", "title", "paragrafos", "paragraphs", "itens", "items")):
            b = _normalize_bloco(value)
            return {"blocos": [b] if b else []}
        # Caso C: o dict é do tipo {"Nome da seção": "texto", ...} — cada
        # chave do dicionário vira o título de um bloco separado.
        blocos = []
        for k, v in value.items():
            if str(k).lower() in ("fonte", "source", "rag"):
                continue
            blocos.append(_normalize_bloco({"titulo": k, "paragrafos": v}))
        blocos = [b for b in blocos if b]
        return {"blocos": blocos}
    if isinstance(value, list):
        # Lista: cada item da lista vira um bloco.
        blocos = [_normalize_bloco(it) for it in value]
        return {"blocos": [b for b in blocos if b]}
    # Sobrou o caso de texto puro: primeiro tenta interpretar como Markdown
    # estruturado (títulos ## ou **negrito**); se não achar nenhum título,
    # trata o texto inteiro como um bloco único sem título.
    text = str(value).strip()
    if not text:
        return {"blocos": []}
    parsed = _blocos_from_markdown(text)
    if parsed:
        return {"blocos": parsed}
    paras, itens = _split_plain_lines(text)
    return {"blocos": [{"titulo": "", "paragrafos": paras, "itens": itens}]}


def format_detalhamento_for_word(value):
    """Monta a SEÇÃO 2 em Markdown estável para colar num Word formatado.

    Cada bloco vira um `####` (Título 3/4 no Word) + parágrafos curtos + lista.
    A única citação de base de conhecimento é RAG_SOURCE_LABEL.
    """
    data = _normalize_detalhamento(value)
    content = []
    # Primeira passada: limpa cada bloco (remove nomes de arquivo RAG do
    # título/parágrafos/itens) e descarta blocos que só repetiam a citação da
    # fonte (isso vira, junto, o rodapé "#### Fonte" gerado mais abaixo).
    for bloco in data.get("blocos") or []:
        titulo = sanitize_rag_names(bloco.get("titulo") or "").strip()
        if _is_fonte_title(titulo):
            continue
        paras = [sanitize_rag_names(p).strip() for p in (bloco.get("paragrafos") or [])]
        itens = [sanitize_rag_names(i).strip() for i in (bloco.get("itens") or [])]
        paras = [p for p in paras if p and not _is_fonte_only_text(p)]
        itens = [i for i in itens if i and not _is_fonte_only_text(i)]
        if not titulo and not paras and not itens:
            continue
        content.append({"titulo": titulo, "paragrafos": paras, "itens": itens})

    if not content:
        return ""

    # Segunda passada: monta o texto Markdown final, bloco por bloco.
    parts = []
    n = 0
    for bloco in content:
        n += 1
        titulo = bloco["titulo"] or "Detalhamento da implementação"
        titulo = re.sub(r"^#{1,6}\s+", "", titulo).strip()   # tira '#'/'##' que a IA já tenha colocado
        # Numera automaticamente o título como "2.1", "2.2"... (a SEÇÃO 2 é a
        # de Detalhamento) — só se o título ainda não tiver esse prefixo.
        if not re.match(r"^2\.\d+\b", titulo):
            titulo = f"2.{n} {titulo}"
        parts.append(f"#### {titulo}")     # '####' = nível de título que o Word reconhece
        parts.append("")
        for p in bloco["paragrafos"]:
            parts.append(p)
            parts.append("")
        for item in bloco["itens"]:
            item = _BULLET_RE.sub("", _NUMBERED_RE.sub("", item)).strip()
            parts.append(f"- {item}")
        if bloco["itens"]:
            parts.append("")

    # Ao final de tudo, sempre adiciona o mesmo rodapé de fonte (nunca o nome
    # real do documento RAG que a IA possa ter usado como referência).
    parts.append("#### Fonte")
    parts.append("")
    parts.append(RAG_SOURCE_LABEL)
    parts.append("")
    text = "\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)   # nunca mais que uma linha em branco entre parágrafos
    return text.strip() + "\n"


def _coerce_rows(value):
    """Garante uma lista de dicts {status, ponto, observacao} para a tabela."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, str):
        return [{"observacao": value}]
    rows = []
    for r in value:
        if isinstance(r, dict):
            rows.append(r)
        elif r is not None:
            rows.append({"observacao": str(r)})
    return rows


def md_validation_table(value):
    """Monta a tabela Markdown (Status | Ponto | Observação) usada nas SEÇÕES
    1 e 3 do documento. Recebe a lista de linhas que a IA gerou e devolve o
    texto pronto da tabela, já no formato que o Markdown/Word entende."""
    rows = _coerce_rows(value)
    out = ["| Status | Ponto | Observação |", "|:------:|-------|------------|"]
    for r in rows:
        st = STATUS_ICON.get(str(r.get("status", "")).strip().lower(), "•")
        # Numa tabela Markdown, o caractere "|" tem significado especial (separa
        # colunas) e quebras de linha quebrariam a linha da tabela — por isso
        # escapamos "|" como "\|" e trocamos "\n" por espaço antes de inserir.
        ponto = _coerce_prose(r.get("ponto", "")).replace("|", "\\|").replace("\n", " ").strip()
        obs = _coerce_prose(r.get("observacao", r.get("observação", ""))) \
            .replace("|", "\\|").replace("\n", " ").strip()
        out.append(f"| {st} | {ponto} | {obs} |")
    if len(out) == 2:
        # Só tem o cabeçalho, nenhuma linha de dado -> mostra um aviso em vez
        # de deixar a tabela "quebrada" (só cabeçalho, sem corpo).
        out.append("| • | _(sem itens)_ | |")
    return "\n".join(out)


# O documento de saída (*_DOC.md) começa como um "esqueleto" cheio de textos
# de espera do tipo "_(a preencher...)_". Estas são as frases exatas que
# indicam "ainda não foi preenchido" — servem para `already_filled` detectar
# se o documento já foi processado antes (e então pode ser pulado).
_INCOMPLETE_MARKERS = (
    "**Entendimento:** _(a preencher",
    "**Contexto de Negócio:** _(a preencher",
    "**Avaliação Geral:** _(a preencher",
    "_(a preencher: detalhar a implementação",
    "_(a preencher: descrever cada um dos",
)


def replace_labeled(md, label, new_value):
    """Substitui '**LABEL:** _(a preencher...)_' pela prosa gerada, no Resumo Executivo."""
    text = _coerce_prose(new_value)
    if not text:
        return md
    text = text.replace("\n", " ").strip()
    # Regex: acha "**Entendimento:**" (ou o `label` que for) seguido de
    # QUALQUER coisa (`.*?` = o mínimo possível, "não guloso") até encontrar
    # uma linha em branco (`\n\n`) ou o fim do texto (`\Z`). `re.S` faz o "."
    # também casar quebras de linha (por padrão ele não casaria).
    pat = re.compile(re.escape(f"**{label}:**") + r".*?(?=\n\n|\Z)", re.S)
    return pat.sub(lambda _m: f"**{label}:** {text}", md, count=1)   # troca só a 1ª ocorrência


def replace_section(md, header, next_header, new_body):
    """Troca o CONTEÚDO entre um título de seção e o próximo título pelo texto
    novo (`new_body`), mantendo os dois títulos intactos. Se o título não for
    encontrado no documento, devolve o Markdown sem alterar nada."""
    if not new_body:
        return md
    i = md.find(header)          # posição onde o título da seção começa
    if i == -1:
        return md
    body_start = i + len(header)   # logo depois do título
    if next_header:
        j = md.find(next_header, body_start)   # onde começa a PRÓXIMA seção
        if j == -1:
            j = len(md)
    else:
        j = len(md)
    # Reconstrói o texto: tudo antes do corpo + corpo novo + tudo depois do
    # ponto onde a próxima seção começa (ou seja, o meio é "recortado e colado" por novo).
    return md[:body_start] + "\n" + new_body + "\n\n" + md[j:]


def fill_doc(doc_path, sections, obj):
    """Preenche o arquivo *_DOC.md de UM objeto com o que a IA gerou.

    O arquivo já existe (criado pela Etapa 1, o extract.py) como um
    "formulário" com títulos de seção prontos e textos de espera do tipo
    "_(a preencher)_". Esta função lê esse Markdown, troca cada trecho de
    espera pelo conteúdo real, e regrava o mesmo arquivo no disco."""
    with open(doc_path, encoding="utf-8") as fh:
        md = fh.read()

    # --- 📌 RESUMO EXECUTIVO (três campos em negrito) ---
    md = replace_labeled(md, "Entendimento", sections.get("entendimento", ""))
    md = replace_labeled(md, "Contexto de Negócio",
                         sections.get("contexto_negocio", sections.get("contexto", "")))
    md = replace_labeled(md, "Avaliação Geral",
                         sections.get("avaliacao_geral", sections.get("avaliacao", "")))

    # --- SEÇÃO 1 – tabela de validação do desenvolvimento ---
    md = replace_section(md, "### SEÇÃO 1 – Resumo do Desenvolvimento", "### SEÇÃO 2",
                         md_validation_table(sections.get("validacao_desenvolvimento")))

    # --- SEÇÃO 2 – Detalhamento (blocos Word-friendly; preserva ABAP na remediação) ---
    detalhamento = format_detalhamento_for_word(sections.get("detalhamento"))
    h2 = "### SEÇÃO 2 – Detalhamento do Desenvolvimento"
    if obj["status"] == "Remediação":
        # Objeto de REMEDIAÇÃO: o esqueleto já traz, dentro da SEÇÃO 2, os
        # blocos de código ABAP alterados (marcados com "#### Bloco"). Não
        # queremos apagar esses blocos de código — só inserir o texto da IA
        # ANTES deles. Por isso aqui não usamos `replace_section` (que trocaria
        # tudo); procuramos manualmente onde o "#### Bloco" começa e inserimos
        # o texto novo só até esse ponto.
        i = md.find(h2)
        if i != -1 and detalhamento:
            body_start = i + len(h2)
            nxt = md.find("#### Bloco", body_start)
            if nxt == -1:
                nxt = md.find("### SEÇÃO 3", body_start)
            if nxt == -1:
                nxt = len(md)
            md = md[:body_start] + "\n" + detalhamento + "\n\n" + md[nxt:]
    else:
        # Objeto NOVO (não é remediação): não há blocos de código a preservar,
        # então pode trocar a seção inteira normalmente.
        md = replace_section(md, h2, "### SEÇÃO 3", detalhamento)

    # --- SEÇÃO 3 – tabela de observações técnicas (para em SEÇÃO 4) ---
    md = replace_section(md, "### SEÇÃO 3 – Observações Técnicas", "### SEÇÃO 4",
                         md_validation_table(sections.get("observacoes_tecnicas",
                                                          sections.get("observacoes"))))

    # SEÇÕES 4 / 5 / 5.3 / 6: fatos do extract.py — sempre por cima da LLM.
    # O `import` aqui DENTRO da função (e não lá no topo do arquivo, junto com
    # os outros imports) é de propósito: evita problema de "importação
    # circular" (extract.py e generate_docs.py podem, em algum fluxo,
    # referenciar um ao outro) — importando só na hora de usar, o problema não
    # acontece. Essas seções são fatos já extraídos pelo Python sem IA
    # (tela de seleção, TVARV, BRF, autorização), então sempre sobrescrevem
    # qualquer coisa que a LLM eventualmente tenha gerado para esses trechos.
    import extract as _extract
    extra = "\n".join(_extract.format_extra_sections(obj))
    i = md.find("### SEÇÃO 4 – Tela de Seleção")
    if i == -1:
        md = md.rstrip() + "\n\n" + extra
    else:
        md = md[:i] + extra

    with open(doc_path, "w", encoding="utf-8") as fh:
        fh.write(md)
    return md


def already_filled(doc_path):
    """True se o Resumo Executivo e o detalhamento já foram preenchidos."""
    with open(doc_path, encoding="utf-8") as fh:
        md = fh.read()
    return not any(p in md for p in _INCOMPLETE_MARKERS)


def read_source(root, rel_path):
    """Lê o arquivo-fonte ABAP do objeto, tentando algumas codificações de
    texto (encodings) diferentes até uma funcionar. Isso é necessário porque
    arquivos exportados de sistemas SAP mais antigos nem sempre são salvos em
    UTF-8 (o padrão "internacional" atual) — muitos vêm em latin-1 ou cp1252
    (codificações comuns em Windows/Europa ocidental), que usam bytes
    diferentes para acentos. Se nenhuma bater, devolve texto vazio em vez de
    travar o programa com erro de leitura."""
    p = os.path.join(root, rel_path)
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(p, encoding=enc) as fh:
                return fh.read()
        except (UnicodeDecodeError, OSError):
            continue
    return ""


def _matches_only(obj, only):
    """Decide se este objeto deve ser processado, quando o usuário passou
    --only NOME1,NOME2 na linha de comando (para rodar só alguns objetos, em
    vez do lote inteiro). Sem --only, tudo passa (`only` é None)."""
    if not only:
        return True
    keys = {
        (obj.get("name_no_ext") or "").lower(),
        (obj.get("file_name") or "").lower(),
        (obj.get("doc_file") or "").lower(),
    }
    # `&` entre dois `set` (conjuntos) devolve os elementos em comum; se
    # houver QUALQUER interseção, o objeto "bate" com a lista pedida.
    return bool(keys & only)


# As 6 chaves que o JSON de resposta da IA deveria trazer (as 4 seções do
# documento, sendo "validacao_desenvolvimento" e "observacoes_tecnicas" as
# tabelas). Usadas por sections_usable só para conferir se pelo menos uma
# chave esperada está presente antes de aceitar o resultado da IA.
_REQUIRED_KEYS = (
    "entendimento", "contexto_negocio", "avaliacao_geral",
    "validacao_desenvolvimento", "detalhamento", "observacoes_tecnicas",
)


def _has_content(value):
    """Diz se um valor tem "algo de útil" dentro: string não-vazia (depois de
    tirar espaços), ou lista/dict que não esteja vazio. Serve para distinguir
    um campo realmente preenchido de um campo vazio ou ausente."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def sections_usable(sections):
    """Confere, de forma simples, se o JSON que a IA devolveu é "bom o
    suficiente" para ser gravado no documento — evita gravar um resultado
    quebrado ou vazio por causa de uma resposta ruim da IA."""
    if not isinstance(sections, dict) or not sections:
        return False
    # Pelo menos um dos campos do Resumo Executivo precisa ter conteúdo.
    exec_ok = any(_has_content(sections.get(k)) for k in (
        "entendimento", "contexto_negocio", "contexto",
        "avaliacao_geral", "avaliacao",
    ))
    if not exec_ok:
        return False
    # E pelo menos uma das chaves esperadas do JSON precisa existir.
    return any(k in sections for k in _REQUIRED_KEYS)


# ----------------------------------------------------------------------------
# Providers (síntese forte + análise barata) via llm_providers do projeto
# ----------------------------------------------------------------------------

def make_providers(mod):
    """Cria as DUAS conexões com a IA usadas pelo pipeline: uma "forte" (para
    escrever o texto final das seções — mais cara, melhor qualidade) e uma
    "barata" (para resumir pedaços de código grandes antes de mandar para a
    forte — mais rápida/barata). `mod` é o módulo llm_providers.py já
    carregado; a configuração (qual fornecedor, quais modelos) vem das
    variáveis de ambiente (do .env)."""
    prov_name = os.environ.get("LLM_PROVIDER", "capgemini")
    base = {}
    if os.environ.get("LLM_MAX_TOKENS"):
        base["max_tokens"] = int(os.environ["LLM_MAX_TOKENS"])

    main_over = dict(base)
    if os.environ.get("LLM_MODEL"):
        main_over["model"] = os.environ["LLM_MODEL"]
    main = mod.get_provider(prov_name, **main_over)

    ana_model = os.environ.get("LLM_MODEL_ANALYSIS")
    if ana_model:
        ana_over = dict(base)
        ana_over["model"] = ana_model
        analysis = mod.get_provider(prov_name, **ana_over)
    else:
        analysis = main  # mesmo modelo para análise e síntese
    return prov_name, main, analysis


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main():
    """Ponto de entrada do script (é o que roda quando você digita
    `python generate_docs.py` no terminal). Faz tudo, na ordem:
      1. lê os argumentos de linha de comando e o arquivo .env;
      2. carrega os módulos "irmãos" (extract, doc_analysis, llm_providers,
         abap_chunker) e valida o acesso à IA;
      3. percorre a lista de objetos que o extract.py já preparou e, para
         cada um, chama a IA e preenche o *_DOC.md correspondente;
      4. imprime um resumo final (quantos deram certo, quantos falharam)."""
    ap = argparse.ArgumentParser(description="Etapa 2: análise de código -> DOCs (LLM).")
    ap.add_argument("--root", default=None,
                    help="Pasta inbound alternativa (padrão: input/). Não use a pasta do extract.py.")
    ap.add_argument("--only", default=None, help="Lista de nomes (sep. por vírgula)")
    ap.add_argument("--dry-run", action="store_true", help="Mostra o plano, não chama a IA")
    ap.add_argument("--force", action="store_true", help="Refaz DOCs já preenchidos")
    ap.add_argument("--providers-path", default=None, help="Caminho do llm_providers.py")
    ap.add_argument("--chunker-path", default=None, help="Caminho do abap_chunker.py")
    args = ap.parse_args()   # lê o que o usuário digitou depois de "python generate_docs.py"

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
    # extract.py é a Etapa 1 do pipeline: já rodou antes e deixou pronto o
    # "esqueleto" dos documentos e um arquivo _payload.json com a lista de
    # objetos. Aqui carregamos esse módulo só para reaproveitar funções dele
    # (não para rodar a Etapa 1 de novo).
    _extract, _ex_path = load_sibling_module("extract")
    if _extract is None:
        print("ERRO: extract.py não encontrado ao lado de generate_docs.py.", file=sys.stderr)
        sys.exit(3)
    _extract.load_project_env()
    try:
        lay = _extract.parse_location(root=args.root)   # descobre as pastas do projeto
    except _extract.LayoutError as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(2)
    root = lay.inbound
    out_dir, out_used = lay.artifacts, lay.artifacts_rel
    payload_path = os.path.join(out_dir, "_payload.json")
    if not os.path.isfile(payload_path):
        # Sem esse arquivo não há lista de objetos para processar — a Etapa 1
        # precisa ter rodado antes.
        print(f"ERRO: {payload_path} não encontrado. Rode extract.py antes.", file=sys.stderr)
        sys.exit(2)

    with open(payload_path, encoding="utf-8") as fh:
        payload = json.load(fh)   # carrega a lista de objetos + metadados do GAP/EF
    gap_ef = payload.get("gap_ef", "")
    ef_values = payload.get("ef_values") or {}
    # Se o usuário passou --only "NOME1,NOME2", transforma numa lista Python
    # (um "set" de nomes em minúsculo); senão, `only` fica None (processa tudo).
    only = {s.strip().lower() for s in args.only.split(",")} if args.only else None
    max_unit_chars = int(os.environ.get("DOC_MAX_UNIT_CHARS", "6000"))
    # Com LLM o template oficial está no WORKSPACE_ID; sem LLM (dry-run) em rap/.
    et_template = _extract.resolve_et_template(use_llm=not args.dry_run)
    print(f"Template ET : {_extract.describe_et_template(et_template)}")
    print(f"Projeto     : {lay.project}")
    print(f"Inbound     : {root}")
    print(f"Artefatos   : {out_dir}")

    # Sempre o doc_analysis.py ao lado deste arquivo (não o do PYTHONPATH).
    doc_analysis, da_path = load_sibling_module("doc_analysis")
    if doc_analysis is None:
        print("ERRO: doc_analysis.py não encontrado ao lado de generate_docs.py.",
              file=sys.stderr)
        sys.exit(3)
    print(f"doc_analysis : {da_path}")
    main_prov = analysis_prov = None
    # Em modo --dry-run não precisamos falar com a IA de verdade (é só um
    # "ensaio" que mostra o plano de execução) — por isso todo este bloco de
    # carregar/validar provider só roda se NÃO for dry-run.
    if not args.dry_run:
        prov_mod, prov_path = load_project_module(
            "llm_providers", args.providers_path, "LLM_PROVIDERS_PATH", lay.project)
        if prov_mod is None:
            print("ERRO: llm_providers.py não encontrado. Use --providers-path DIR ou "
                  "LLM_PROVIDERS_PATH. (Mesmo módulo da remediação.)", file=sys.stderr)
            sys.exit(3)
        chunk_mod, chunk_path = load_project_module(
            "abap_chunker", args.chunker_path, "ABAP_CHUNKER_PATH", lay.project)
        if chunk_mod is None:
            print("ERRO: abap_chunker.py não encontrado. Use --chunker-path DIR ou "
                  "ABAP_CHUNKER_PATH. (Mesmo módulo da remediação.)", file=sys.stderr)
            sys.exit(3)

        try:
            prov_name, main_prov, analysis_prov = make_providers(prov_mod)
        except Exception as e:  # noqa
            print(f"ERRO ao criar provider: {e}", file=sys.stderr)
            sys.exit(3)

        print(f"Provider : {prov_name}  (llm_providers: {prov_path})")
        print(f"Chunker  : {chunk_path}")
        print(f"Síntese  : {main_prov.model}")
        print(f"Análise  : {analysis_prov.model}"
              + ("  (mesmo da síntese)" if analysis_prov is main_prov else ""))
        res = main_prov.validate()   # testa o acesso à IA ANTES de gastar tempo processando
        print(res)
        if not res.ok:
            print("Abortando: acesso à IA não validado.", file=sys.stderr)
            sys.exit(3)
        # Relê o irmão: llm_providers/abap_chunker no PYTHONPATH podem ter
        # importado um doc_analysis antigo sem et_template.
        doc_analysis, da_path = load_sibling_module("doc_analysis")
        print(f"doc_analysis : {da_path}")

    # Contadores para o resumo final que aparece no console ao terminar tudo.
    total, done, skipped, failed = 0, 0, 0, 0
    failures = []
    # O LAÇO PRINCIPAL: passa por cada objeto (FORM, CDS, classe...) que a
    # Etapa 1 já preparou, e tenta preencher o documento dele, um de cada vez.
    for obj in payload.get("objects") or []:
        if not _matches_only(obj, only):
            continue
        total += 1
        doc_path = os.path.join(out_dir, obj["doc_file"])
        if not os.path.isfile(doc_path):
            print(f"  [erro] {obj.get('doc_file')}: esqueleto ausente — rode extract.py.",
                  file=sys.stderr)
            failed += 1
            failures.append(obj.get("doc_file") or obj.get("name_no_ext"))
            continue
        if not args.force and already_filled(doc_path):
            # Documento já tem conteúdo real (não é mais o esqueleto com
            # textos de espera) e o usuário não pediu --force: pula, para não
            # gastar tempo/dinheiro de IA refazendo o que já está pronto.
            print(f"  [skip] {obj['doc_file']} (já preenchido)")
            skipped += 1
            continue

        if args.dry_run:
            # Modo "ensaio": só mostra qual estratégia SERIA usada para este
            # objeto (sem chamar a IA de verdade nem gastar nada).
            src = read_source(root, obj["rel_path"])
            if not doc_analysis.uses_abap_chunker(obj.get("type")):
                plan = "síntese RAP/DDL (sem chunk ABAP)"
            elif len(src) > max_unit_chars:
                plan = "chunk+resumo+síntese"
            else:
                plan = "síntese única"
            kind = obj.get("type") or "?"
            print(f"  [plano] {obj['doc_file']:<50} {obj['status']:<11} "
                  f"{kind:<36} {len(src)} chars -> {plan}")
            continue

        # Caminho "de verdade": lê o código-fonte do objeto e pede à IA para
        # analisá-lo (via doc_analysis.analyze_object, chamado com segurança
        # através de call_analyze_object para não quebrar em versões antigas).
        src = read_source(root, obj["rel_path"])
        try:
            sections, finish, stats = call_analyze_object(
                doc_analysis.analyze_object,
                obj=obj,
                gap_ef=gap_ef,
                source=src,
                main_provider=main_prov,
                analysis_provider=analysis_prov,
                max_unit_chars=max_unit_chars,
                log=lambda m: print(m),
                ef_values=ef_values,
                et_template=et_template)
        except Exception as e:  # noqa: BLE001
            # Se a chamada à IA falhar por qualquer motivo (rede, erro do
            # provedor, etc.), não travamos o script inteiro: registramos a
            # falha deste objeto e seguimos para o próximo.
            print(f"  [erro] {obj['doc_file']}: {type(e).__name__}: {e}", file=sys.stderr)
            failed += 1
            failures.append(obj["doc_file"])
            continue

        if finish == "length":
            # "length" = a resposta da IA foi CORTADA por atingir o limite de
            # tamanho (tokens), não porque terminou naturalmente — é um aviso
            # para o usuário considerar aumentar o limite.
            print(f"  [aviso] {obj['doc_file']}: síntese truncada (length) — "
                  "aumente LLM_MAX_TOKENS.")
        if not sections_usable(sections):
            print(f"  [erro] {obj['doc_file']}: síntese sem JSON válido "
                  f"(finish='{finish}').", file=sys.stderr)
            failed += 1
            failures.append(obj["doc_file"])
            continue

        fill_doc(doc_path, sections, obj)
        print(f"  [ok]   {obj['doc_file']}  [{stats}]")
        done += 1

    # Resumo final impresso no console, depois que todos os objetos passaram
    # pelo laço acima.
    print("-" * 60)
    if args.dry_run:
        print(f"DRY-RUN: {total} objeto(s) — nenhum token consumido.")
    else:
        print(f"Concluído: {done} gerado(s), {skipped} pulado(s), {failed} erro(s), "
              f"de {total} objeto(s).")
        if failures:
            print("Falhas:")
            for name in failures:
                print(f"  - {name}")
    if failed:
        # Código de saída diferente de zero => outros scripts/pipelines que
        # chamem este conseguem detectar que algo deu errado.
        sys.exit(4)


if __name__ == "__main__":
    main()