# -*- coding: utf-8 -*-
"""
===============================================================================
 doc_analysis.py — MOTOR DA ETAPA 2: análise de código para documentação
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Recebe o código-fonte de UM objeto e produz o conteúdo das seções do
    documento de análise (as 4 seções da ET por objeto), usando a LLM.

SEGUE O MESMO MODELO DA REMEDIAÇÃO (analyze.py):
    - usa o abap_chunker para cortar o código em unidades (FORM/METHOD/...),
      sem partir instruções e com roundtrip garantido;
    - funil de dois níveis de custo:
        1. ANÁLISE (modelo BARATO, ex.: Haiku): resume cada unidade de código
           em 1-2 frases (PT-BR). Só para objetos grandes (que não cabem numa
           chamada só).
        2. SÍNTESE (modelo FORTE, ex.: Sonnet): junta os resumos das unidades
           (ou o fonte inteiro, se pequeno) + os blocos de remediação + o
           contexto do GAP e escreve as 4 seções finais.
    - a LLM é acessada pela abstração llm_providers (Generative Engine da
      Capgemini), recebida pronta de fora (os `providers`).

REUTILIZÁVEL:
    Este módulo NÃO conhece caminhos, .env nem arquivos de saída. Ele só recebe
    texto + providers e devolve dados. Quem orquestra é o generate_docs.py.

PROMPTS EM INGLÊS, SAÍDA EM PT-BR (mesma convenção do analyze.py).
===============================================================================
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# Estatísticas do funil (para log)
# =============================================================================
@dataclass
class DocAnalyzeStats:
    """A "ficha de estatísticas" de UM objeto analisado: quantas unidades de
    código existiam, quantas foram resumidas, se precisou cortar (chunked) e
    quantas chamadas de síntese à IA foram feitas. Serve só para o log/console;
    não afeta o resultado final."""
    units_total: int = 0        # quantas unidades (FORM/METHOD/...) o objeto tinha
    units_summarized: int = 0   # quantas foram resumidas pela IA barata
    chunked: bool = False       # True = o código era grande e precisou ser cortado
    synthesis_calls: int = 0    # quantas vezes a IA forte foi chamada (1, ou 2 se houve nova tentativa)

    def __str__(self) -> str:
        """Transforma a ficha numa linha de texto curta, para imprimir no log."""
        return (f"units={self.units_total} summarized={self.units_summarized} "
                f"chunked={self.chunked} synthesis={self.synthesis_calls}")


# =============================================================================
# PROMPTS — em inglês; valores de saída em PT-BR
# =============================================================================

# A "instrução de sistema" é o texto que diz à IA QUEM ela deve ser e como se
# comportar durante toda a conversa (fica separado da pergunta em si).
# Fica em inglês de propósito — a IA segue instruções técnicas em inglês com
# mais precisão — mas o texto pede explicitamente a resposta em português.
ANALYSIS_SYSTEM = (
    "You are a senior SAP ABAP analyst. You summarize what a piece of ABAP code "
    "does, factually and concisely. You never invent behavior that is not in the "
    "code. Answer in Brazilian Portuguese (PT-BR), 1-2 sentences, plain text only."
)


def build_unit_summary_prompt(unit_type, name, unit_text):
    """Monta a pergunta (o "prompt") que pede à IA barata para resumir, em 1-2
    frases, o que UMA unidade de código (um FORM, METHOD, etc.) faz."""
    label = unit_type or "TRECHO"
    ident = name or "(sem nome)"
    return (f"Summarize what this ABAP {label} ({ident}) does. "
            f"1-2 sentences, PT-BR, plain text (no JSON, no code).\n\n"
            f"{label} {ident}:\n{unit_text}")


SYNTHESIS_SYSTEM = (
    "You are a senior SAP technical analyst producing an EXECUTIVE VALIDATION "
    "report for an ABAP / RAP object in an SAP ECC to S/4HANA migration. You are "
    "precise and concrete, and you assess whether the development follows best "
    "practices. You never invent SAP Notes, API names, tables, fields or "
    "parameters that are not present in the provided material. "
    "IMPORTANT: write every prose VALUE in Brazilian Portuguese (PT-BR). Keep "
    "ABAP keywords/statements, object names, tables, fields and code snippets in "
    "their original form; only the surrounding prose is in PT-BR. Respond with a "
    "SINGLE valid JSON object ONLY (no code fences, no preamble). "
    "Do NOT return the source code. "
    "NEVER cite RAG/KB/template filenames, PDF titles, workbook names or local "
    "paths in any generated field. If a knowledge-base source must be mentioned, "
    "write exactly: Generative AI RAG Document Capgemini."
)


def build_synthesis_prompt(obj, gap_ef, full_source, unit_summaries, ef_values=None,
                           et_template=None):
    """Monta o pedido GRANDE que pede à IA forte para escrever as 4 seções do
    documento de análise (entendimento, contexto de negócio, avaliação geral,
    validação do desenvolvimento, detalhamento e observações técnicas).

    A função é longa porque o pedido é montado aos poucos: ela junta pedaço por
    pedaço de texto numa lista Python chamada `parts` (uma técnica comum: é bem
    mais rápido colar uma lista de textos no fim, com "\\n".join, do que ficar
    somando strings uma a uma). No fim, todas as instruções viram um texto só.
    """
    status = obj["status"]
    tipo = obj.get("type") or ""
    # `parts` vai acumulando, linha por linha, tudo que entra no pedido à IA.
    parts = [
        f"Object: {obj['name_no_ext']}",
        f"Type: {tipo}",
        f"Classification: {'Remediation' if status == 'Remediação' else 'New object'}",
        f"Related GAP/EF: {gap_ef}",
    ]
    if ef_values:
        # ef_values são campos que o Python já extraiu, sem IA, direto da EF
        # (Especificação Funcional). Mandamos para a IA como FATOS já prontos,
        # para ela não precisar (e não arriscar) reinventar esses dados.
        parts.append("EF header fields (deterministic extract):")
        for k, v in ef_values.items():
            parts.append(f"- {k}: {v}")
    if et_template:
        # et_template diz de onde vem o "molde" (template) oficial da ET: pode
        # estar guardado no servidor da Capgemini (workspace) ou numa pasta local.
        # Em qualquer um dos dois casos, avisamos a IA para seguir a ordem de
        # seções do molde oficial, e para NUNCA citar o nome do arquivo/template
        # no texto gerado (é uma regra de "não vazar" detalhes internos).
        if et_template.get("source") == "workspace":
            tname = et_template.get("name") or "(see ET_TEMPLATE_NAME)"
            parts.append(
                "Official ET template is in the Capgemini Generative Engine workspace "
                f"(WORKSPACE_ID). Retrieve it BY EXACT NAME: {tname}. "
                "Mirror that template's section order; do not invent a new layout. "
                "Do NOT write the template filename (or any other RAG document name) "
                "in the generated JSON. In detalhamento the only allowed source "
                "citation is: Generative AI RAG Document Capgemini."
            )
        elif et_template.get("path") or et_template.get("name"):
            parts.append(
                "Official ET template is available locally (no LLM retrieval). "
                "Mirror the official ET section order; do not invent a new layout. "
                "Do NOT cite the local path or filename in the generated JSON. "
                "In detalhamento the only allowed source citation is: "
                "Generative AI RAG Document Capgemini."
            )
    if obj.get("dependencies"):
        parts.append("Detected dependencies: " + ", ".join(obj["dependencies"]))
    parts.extend(_extra_facts_prompt(obj))   # mais fatos determinísticos (TVARV, BRF, autorização...)
    parts.append("")
    extra = _type_guidance(tipo)             # dica extra conforme o tipo do objeto (CDS, DCL, BDEF...)

    # Ou mandamos o código-fonte INTEIRO (objeto pequeno), ou mandamos só os
    # resumos de cada unidade (objeto grande, já resumido antes por economia).
    # Nunca os dois ao mesmo tempo.
    if full_source is not None:
        parts.append("Full source:")
        parts.append(full_source)
    else:
        parts.append("The object is large; here are per-unit summaries of the code:")
        for i, u in enumerate(unit_summaries or [], 1):
            head = f"{u.get('unit_type') or 'UNIT'} {u.get('name') or i}"
            parts.append(f"- {head}: {u.get('resumo','').strip()}")
    parts.append("")

    if status == "Remediação" and obj.get("mod_blocks"):
        # Se este objeto já passou pela remediação automática, mostramos à IA
        # exatamente os trechos que foram alterados (entre marcadores BEGIN/END
        # OF MODIFICATION), para ela poder comentar sobre essas mudanças.
        parts.append("Remediation blocks (BEGIN/END OF MODIFICATION), with location:")
        for i, b in enumerate(obj["mod_blocks"], 1):
            parts.append(f"\n--- Block {i} — {b['location']} "
                         f"(lines {b['start_line']}-{b['end_line']}) ---")
            parts.append(b["snippet"])
        parts.append("")

    # O formato da seção "detalhamento" muda conforme o objeto é uma REMEDIAÇÃO
    # (código já existente que foi corrigido) ou um OBJETO NOVO (criado do zero):
    # remediação foca nos blocos alterados; objeto novo foca numa visão geral.
    if status == "Remediação":
        det_schema = (
            '    {"titulo": "Bloco N — <FORM/METHOD>", '
            '"paragrafos": ["<what changed before/after>", '
            '"<technical justification: obsolete syntax, Simplification Item, '
            'Clean Core / released API, performance>"], '
            '"itens": ["<short bullet>"]}'
        )
        det_guide = (
            "- detalhamento.blocos: one object per remediation block; reference "
            "the method/FORM in titulo."
        )
    else:
        det_schema = (
            '    {"titulo": "Visão geral da implementação", '
            '"paragrafos": ["<short paragraph>"], "itens": []},\n'
            '    {"titulo": "Rotinas e métodos", '
            '"paragrafos": ["<how the main routines/methods work>"], '
            '"itens": ["<FORM/METHOD — role>"]},\n'
            '    {"titulo": "Regra de negócio aplicada", '
            '"paragrafos": ["<business rule in this object>"], "itens": []}'
        )
        det_guide = (
            "- detalhamento.blocos: use those three titles (add more only if "
            "needed). Short paragraphs (2-4 sentences). itens = bullet list."
        )

    parts.append(
        "Produce a JSON object with EXACTLY these keys (all prose in Brazilian "
        "Portuguese):\n"
        "{\n"
        '  "entendimento": "<what the object does and its role in the GAP>",\n'
        '  "contexto_negocio": "<purpose and business rule>",\n'
        '  "avaliacao_geral": "<maturity, points of attention and gaps>",\n'
        '  "validacao_desenvolvimento": [\n'
        '    {"status": "ok|aviso|erro", "ponto": "<aspect checked>", '
        '"observacao": "<finding / recommendation>"}\n'
        "  ],\n"
        '  "detalhamento": {\n'
        '    "blocos": [\n'
        f"{det_schema}\n"
        "    ]\n"
        "  },\n"
        '  "observacoes_tecnicas": [\n'
        '    {"status": "ok|aviso|erro", "ponto": "<S/4HANA / Clean Core / '
        'performance aspect>", "observacao": "<finding>"}\n'
        "  ]\n"
        "}\n\n"
        "Guidance:\n"
        "- validacao_desenvolvimento: 4-10 rows assessing WHAT was developed and "
        "whether it follows best practices (naming, modularization, performance, "
        "error handling, Clean Core, correctness). status 'ok' when adequate, "
        "'aviso' for a recommendation/gap, 'erro' for a real problem.\n"
        "- observacoes_tecnicas: 2-6 rows on S/4HANA impact, Clean Core, "
        "performance, points of attention.\n"
        f"{det_guide}\n"
        "- detalhamento must be easy to paste into a formatted Microsoft Word "
        "document: short paragraphs, bullet lists in itens, no HTML, no Markdown "
        "tables, no nested headings inside paragrafos.\n"
        "- NEVER name RAG/KB documents, PDFs, workbooks, templates or file paths "
        "in detalhamento (or any other field). The only allowed source citation "
        "is exactly: Generative AI RAG Document Capgemini. Python will add a "
        "Fonte block; do not invent a Fonte bloco.\n"
        "- Keep 'ponto' short (a few words); 'observacao' one or two sentences.\n"
        "- Base every row on evidence from the code/material. Do not invent.\n"
        "- Do not invent FORM/METHOD/table/API names that are not in the material.\n"
        "- Do not invent selection-screen fields, TVARV names, BRF functions or "
        "authorization objects beyond the deterministic list above.\n"
        f"{extra}"
        "JSON only.")
    return "\n".join(parts)


def _extra_facts_prompt(obj):
    """Fatos já extraídos pelo Python — a LLM não deve contradizer nem inventar.

    Monta uma lista de frases prontas (uma por "fato"): campos de tela de
    seleção, variáveis TVARV, referências a BRF/BTF e objetos de autorização.
    Tudo isso já foi lido do código de forma determinística (sem IA) em outro
    lugar do projeto; aqui só formatamos para colar no pedido à IA."""
    lines = []
    ss = obj.get("selection_screen") or {}
    if ss.get("applies"):
        fields = ss.get("fields") or []
        names = [f.get("name") for f in fields if f.get("kind") != "BLOCK" and f.get("name")]
        if names:
            lines.append("Selection-screen fields (deterministic): " + ", ".join(names))
        elif ss.get("has_events"):
            lines.append("Selection-screen: AT SELECTION-SCREEN events present; "
                         "PARAMETERS/SELECT-OPTIONS not in this source.")
        else:
            lines.append("Selection-screen: none found in this report.")
    tvarv = obj.get("tvarv_variables") or []
    if tvarv:
        names = [h.get("name") or f"(line {h.get('line')})" for h in tvarv]
        lines.append("TVARV/TVARVC variables (deterministic): " + ", ".join(names))
    else:
        lines.append("TVARV/TVARVC: no references found.")
    brf = obj.get("brf_refs") or []
    if brf:
        names = [h.get("name") or h.get("token") for h in brf]
        lines.append("BRF/BTF references (deterministic): " + ", ".join(names))
    else:
        lines.append("BRF/BTF: no references found.")
    auths = obj.get("auth_objects") or []
    if auths:
        names = [h.get("object") for h in auths if h.get("object")]
        lines.append("Authorization objects (deterministic): " + ", ".join(names))
    else:
        lines.append("Authorization objects: none found (AUTHORITY-CHECK / pfcg_auth).")
    if not lines:
        return []
    return [""] + lines   # a lista vazia no início vira uma linha em branco (separador)


# Tipos RAP/DDL que o abap_chunker (FORM/METHOD) não recorta com qualidade.
# (São objetos "declarativos" — CDS, DCL, BDEF etc. — que não têm sub-rotinas
# FORM/METHOD para o cortador reconhecer; por isso vão inteiros para a IA.)
_NO_ABAP_CHUNK_TYPES = {
    "CDS Interface View", "CDS Composition View", "CDS Consumption View",
    "CDS Projection View", "CDS View (genérico)", "Metadata Extension",
    "Access Control (DCL)", "Behavior Definition (Interface)",
    "Behavior Definition (Projection)", "Service Definition", "Service Binding",
    "Tabela (DDL)", "Estrutura/Data Element (DDIC)",
}
_NO_ABAP_CHUNK_MARKERS = (
    "cds ",
    "metadata extension",
    "access control",
    "behavior definition",
    "service definition",
    "service binding",
    "tabela (ddl)",
    "estrutura/data element",
)
_RAP_SOURCE_CAP = 20000   # tamanho máximo (em caracteres) de fonte RAP/DDL enviado à IA


def uses_abap_chunker(tipo):
    """False para CDS/BDEF/DCL/DDLX/SRVD — o cortador FORM/METHOD não se aplica.
    Primeiro confere o tipo exato na lista _NO_ABAP_CHUNK_TYPES; se não achar,
    procura pedaços de texto característicos (_NO_ABAP_CHUNK_MARKERS) no nome
    do tipo, como rede de segurança para variações de escrita."""
    raw = (tipo or "").strip()
    if raw in _NO_ABAP_CHUNK_TYPES:
        return False
    low = raw.lower()
    return not any(m in low for m in _NO_ABAP_CHUNK_MARKERS)


def _capped_source(src, cap=_RAP_SOURCE_CAP):
    """Corta o texto se ele passar de `cap` caracteres, para não estourar o
    limite de tamanho do pedido à IA. Devolve (texto, foi_cortado?)."""
    if len(src) <= cap:
        return src, False
    return src[:cap] + "\n... (fonte truncado) ...", True


def _type_guidance(tipo):
    """Devolve uma dica extra (em inglês, para o prompt) sobre COMO analisar o
    objeto, de acordo com o seu tipo (CDS, DCL, BDEF, relatório clássico...).
    Se o tipo não bater com nenhum caso conhecido, devolve texto vazio."""
    t = (tipo or "").lower()
    if "cds" in t:
        return ("- This is a CDS/RAP view: discuss entities, associations/joins, "
                "keys, annotations (@AccessControl, @UI) and projection vs interface. "
                "Do not invent FORM/METHOD names.\n")
    if "access control" in t or "dcl" in t:
        return ("- This is a DCL: discuss PFCG/pfcg_auth aspects, grant/where "
                "and whether authorization matches the CDS.\n")
    if "behavior definition" in t:
        return ("- This is a BDEF: discuss managed/unmanaged/projection, draft, "
                "actions, validations, determinations and the implementation class.\n")
    if "behavior implementation" in t:
        return ("- This is a RAP behavior handler: discuss FOR MODIFY/READ/LOCK, "
                "authorizations, BAPI calls and released APIs.\n")
    if "metadata" in t:
        return ("- This is a metadata extension: discuss UI facets, lineitem and "
                "consumption annotations only.\n")
    if "service" in t:
        return ("- This is a RAP service artifact: discuss exposed entities and binding.\n")
    if "report" in t or "include" in t or "programa" in t:
        return ("- Classic ABAP: discuss selection screen, SELECT, AUTHORITY-CHECK, "
                "and remediation blocks when present.\n")
    return ""


# =============================================================================
# PARSING JSON tolerante (igual analyze._parse_json_object)
# =============================================================================
def parse_json_object(text):
    """Extrai o objeto JSON da resposta da IA, mesmo que ela venha cercada de
    ```json ... ``` ou com algum texto solto em volta. Se não conseguir achar
    um JSON válido, devolve None (em vez de travar o programa)."""
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?", "", t).strip()   # remove a cerca ``` do início, se houver
    t = re.sub(r"```$", "", t).strip()            # remove a cerca ``` do fim, se houver
    a, b = t.find("{"), t.rfind("}")               # acha o primeiro '{' e o último '}'
    if a == -1 or b == -1 or b <= a:
        return None
    try:
        return json.loads(t[a:b + 1])              # converte o texto em dados Python (dict)
    except json.JSONDecodeError:
        return None


# =============================================================================
# ORQUESTRAÇÃO por objeto
# =============================================================================
def summarize_units(source, analysis_provider, max_unit_chars, log=print):
    """Corta o fonte com o abap_chunker e resume cada unidade com código
    (modelo barato). Devolve lista de {unit_type, name, resumo}."""
    from abap_chunker import chunk_for_analysis  # lazy: módulo do projeto

    segments = chunk_for_analysis(source, max_chars=max_unit_chars)
    summaries = []
    for idx, seg in enumerate(segments):
        if not seg.has_code:            # pedaço só com comentários/linhas em branco => pula
            continue
        prompt = build_unit_summary_prompt(seg.unit_type, seg.name, seg.text)
        try:
            analysis_provider.new_session()   # cada unidade é resumida numa sessão nova, isolada
            resp = analysis_provider.invoke(
                ANALYSIS_SYSTEM, [{"role": "user", "content": prompt}])
            resumo = (resp.text or "").strip()
        except Exception as e:  # noqa
            # Se a IA falhar numa unidade, não travamos o processo inteiro: só
            # registramos o aviso e seguimos com um resumo "vazio" para ela.
            log(f"      ⚠ resumo de unidade falhou ({type(e).__name__}: {e})")
            resumo = "(resumo indisponível)"
        summaries.append({"unit_type": seg.unit_type,
                          "name": seg.name or f"block#{idx}", "resumo": resumo})
    return summaries


def analyze_object(obj, gap_ef, source, main_provider, analysis_provider=None,
                   max_unit_chars=6000, log=print, ef_values=None,
                   et_template=None):
    """Produz as seções do DOC para um objeto.

    - ABAP clássico pequeno: uma síntese com o fonte inteiro.
    - ABAP clássico grande: corta em unidades, resume (modelo barato) e sintetiza.
    - CDS/BDEF/DCL/DDLX/SRVD: NÃO usa o cortador ABAP (não há FORM/METHOD);
      envia o fonte (com teto) direto à síntese.
    """
    stats = DocAnalyzeStats()
    analysis_provider = analysis_provider or main_provider
    src = source or ""
    tipo = obj.get("type") or ""

    # Três caminhos possíveis, do mais simples ao mais trabalhoso:
    #  1) tipo RAP/DDL (CDS, DCL, BDEF...) -> manda o fonte inteiro (com corte de tamanho).
    #  2) ABAP clássico PEQUENO             -> manda o fonte inteiro, sem cortar em unidades.
    #  3) ABAP clássico GRANDE              -> corta em unidades e resume cada uma antes.
    if not uses_abap_chunker(tipo):
        full_source, truncated = _capped_source(src)
        if truncated:
            log(f"      ℹ {obj.get('name_no_ext')}: RAP/DDL truncado em {_RAP_SOURCE_CAP} chars")
        unit_summaries = None
    elif len(src) <= max_unit_chars:
        full_source, unit_summaries = src, None
    else:
        stats.chunked = True
        unit_summaries = summarize_units(src, analysis_provider, max_unit_chars, log)
        stats.units_total = len(unit_summaries)
        stats.units_summarized = len(unit_summaries)
        full_source = None
        if not unit_summaries:
            # INCLUDE sem FORM/METHOD: o chunker não gerou unidades — cai no fonte.
            full_source, truncated = _capped_source(src)
            unit_summaries = None
            extra = " (truncado)" if truncated else ""
            log(f"      ℹ {obj.get('name_no_ext')}: sem unidades ABAP — síntese pelo fonte{extra}")

    # Chamada principal: pede à IA forte para escrever as seções finais do DOC.
    prompt = build_synthesis_prompt(
        obj, gap_ef, full_source, unit_summaries, ef_values,
        et_template=et_template)
    main_provider.new_session()
    resp = main_provider.invoke(SYNTHESIS_SYSTEM, [{"role": "user", "content": prompt}])
    stats.synthesis_calls = 1
    sections = parse_json_object(resp.text)
    finish = getattr(resp, "finish_reason", "") or ""
    if sections is None:
        # A IA não devolveu um JSON válido na primeira vez: tentamos MAIS UMA
        # vez, mostrando a ela a resposta errada e pedindo para corrigir —
        # em vez de simplesmente desistir.
        log(f"      ⚠ JSON inválido — nova tentativa")
        retry = main_provider.invoke(
            SYNTHESIS_SYSTEM,
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": resp.text or ""},
                {"role": "user",
                 "content": "Your previous reply was not a valid JSON object. "
                            "Reply again with ONLY the JSON object, no fences."},
            ],
        )
        stats.synthesis_calls = 2
        sections = parse_json_object(retry.text)
        finish = getattr(retry, "finish_reason", "") or finish
    return sections, finish, stats