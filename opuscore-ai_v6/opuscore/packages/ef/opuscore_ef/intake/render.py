"""Gera o Markdown a partir do JSON verificado — estrutura sempre igual."""
from __future__ import annotations

import re
from datetime import datetime, timezone

from .checks import Achado
from .gate import INVALIDO, Gate
from .parser import EFDocument
from .schema import ExtractionResult, Item

SECOES_PACOTE = [
    ("Resumo do negócio", ["IDENTIFICACAO", "TIPO_DEMANDA", "OBJETIVO", "JUSTIFICATIVA", "COMPONENTE"]),
    ("Escopo da descoberta", ["ESCOPO_INCLUIDO", "ESCOPO_EXCLUIDO", "PREMISSA", "SISTEMA", "DEPENDENCIA"]),
    ("Requisitos e regras", ["PROCESSO", "AS_IS", "TO_BE", "ATOR", "REGRA", "EXCECAO", "ACEITE"]),
    ("Referências técnicas declaradas", ["REF_TECNICA"]),
    ("Âncoras funcionais", ["ANCORA_FUNCIONAL"]),
    ("Interfaces, dados e campos", ["INTERFACE", "CAMPO", "LAYOUT", "PAYLOAD", "JOB", "WORKFLOW", "PARAMETRO"]),
    ("Cenários e testes", ["TESTE"]),
    ("Requisitos não funcionais", ["REQ_NAO_FUNCIONAL"]),
]


def nome_arquivo(id_demanda: str, versao: str, pendencias: bool = False) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", (id_demanda or "EF").strip()).strip("-") or "EF"
    v = re.sub(r"[^A-Za-z0-9._-]+", "", (versao or "0").lstrip("vV")) or "0"
    tipo = "Relatorio-Pendencias-EF" if pendencias else "Pacote-Entrada-Descoberta-SAP"
    return f"{base}-{tipo}-v{v}.md"


def _cel(s) -> str:
    return re.sub(r"\s+", " ", str(s or "")).replace("|", "\\|").strip()


def _tabela_itens(itens: list[Item], com_valor: bool) -> list[str]:
    if com_valor:
        linhas = ["| ID | Valor original | Tipo | Escopo | Descrição | Classificação | Confiança | Fonte |",
                  "|---|---|---|---|---|---|---|---|"]
    else:
        linhas = ["| ID | Descrição | Classificação | Confiança | Fonte |", "|---|---|---|---|---|"]
    for i in itens:
        fonte = f"{i.fonte.secao} · {', '.join(i.fonte.localizacao) or '—'}"
        if com_valor:
            val = _cel(i.valor_original)
            if i.valor_normalizado and i.valor_normalizado != i.valor_original:
                val += f" → {_cel(i.valor_normalizado)} ({_cel(i.regra_normalizacao)})"
            linhas.append(f"| {i.id} | `{val}` | {_cel(i.tipo_objeto)} | {_cel(i.escopo)} | "
                          f"{_cel(i.descricao)} | {i.classificacao} | {i.confianca} | {fonte} |")
        else:
            extra = ""
            if i.categoria == "COMPONENTE":
                extra = f" **[{i.natureza or 'NATUREZA?'}]**"
                if i.objeto_origem:
                    extra += f" origem: `{_cel(i.objeto_origem)}`"
                if i.ancora:
                    extra += f" âncora: {_cel(i.ancora)}"
            linhas.append(f"| {i.id} | {_cel(i.descricao)}{extra} | {i.classificacao} | {i.confianca} | {fonte} |")
    return linhas


def _controle(doc: EFDocument, res: ExtractionResult, gate: Gate, meta: dict) -> list[str]:
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return [
        "## Controle do pacote", "",
        "| Campo | Valor |", "|---|---|",
        f"| Demanda | {_cel(res.controle.id_demanda)} |",
        f"| Projeto | {_cel(meta.get('projeto') or res.controle.projeto)} |",
        f"| EF | {_cel(doc.filename)} |",
        f"| Versão informada | {_cel(meta.get('versao'))} |",
        f"| Última versão no histórico | {_cel(doc.revisions[-1]['versao'] if doc.revisions else '—')} |",
        f"| Estado de aprovação | {_cel(meta.get('estado'))} |",
        f"| Anexos autorizados | {_cel(', '.join(meta.get('anexos') or []) or 'nenhum')} |",
        f"| Gate | **{gate.status}** |",
        f"| Gerado em | {agora} |",
        f"| Consultas SAP executadas | nenhuma (Etapa 1) |", "",
    ]


def _grupo(res: ExtractionResult, cats: list[str]) -> list[Item]:
    return [i for i in res.itens if i.categoria in cats]


def render_pacote(doc: EFDocument, res: ExtractionResult, gate: Gate,
                  achados: list[Achado], meta: dict) -> str:
    out = [f"# {res.controle.id_demanda} — Pacote de Entrada para Descoberta SAP", ""]
    out += _controle(doc, res, gate, meta)
    out += ["## Gate", "", f"**{gate.status}**", ""] + [f"- {j}" for j in gate.justificativa] + [""]
    if gate.a_confirmar:
        out += ["## ⚠ Bloqueios a confirmar (apontados pela IA)", "",
                "> Julgamento semântico da IA. **Não invalida a EF sozinho.** O funcional ou o Líder Técnico "
                "deve confirmar (a EF volta para ajuste) ou descartar (a descoberta segue).", "",
                "| Critério | Descrição | Evidência apontada | Localização | Decisão |",
                "|---|---|---|---|---|"]
        for a in gate.a_confirmar:
            out.append(f"| {a['codigo']} | {_cel(a['descricao'])} | {_cel(a['evidencia'])} | "
                       f"{_cel(', '.join(a.get('localizacao') or [])) or '—'} | ( ) Confirmar ( ) Descartar |")
        out += [""]
    out += ["## Resumo do negócio", "", res.resumo_negocio.strip(), ""]
    for titulo, cats in SECOES_PACOTE:
        itens = _grupo(res, cats)
        if titulo == "Resumo do negócio":
            if itens:
                out += ["### Identificação, objetivo e componentes", ""] + _tabela_itens(itens, False) + [""]
            continue
        out += [f"## {titulo}", ""]
        if not itens:
            out += ["_Nenhum item extraído._", ""]
            continue
        com_valor = titulo in ("Referências técnicas declaradas",)
        # escopo excluído em destaque: a Etapa 2 NÃO deve pesquisar esses itens
        if titulo == "Referências técnicas declaradas":
            inc = [i for i in itens if i.escopo != "EXCLUIDO"]
            exc = [i for i in itens if i.escopo == "EXCLUIDO"]
            out += ["### No escopo ou indefinidas", ""] + (_tabela_itens(inc, True) if inc else ["_Nenhuma._"]) + [""]
            if exc:
                out += ["### Fora do escopo (a Etapa 2 não deve pesquisar)", ""] + _tabela_itens(exc, True) + [""]
            continue
        out += _tabela_itens(itens, com_valor) + [""]

    imgs = meta.get("imagens") or []
    if imgs:
        out += ["## Imagens da EF", "",
                f"Modo de leitura: **{meta.get('modo_imagens')}**. Campos lidos das telas aparecem em "
                "'Interfaces, dados e campos' com a marcação da imagem de origem.", "",
                "| Imagem | Tipo | Legenda | Lida | Campos |", "|---|---|---|---|---|"]
        for i in imgs:
            n = len((i.get("tela") or {}).get("campos") or [])
            lida = "sim" if i["lida"] else (f"não ({_cel(i['erro'])[:60]})" if i.get("erro") else "não")
            out.append(f"| {i['nome']} | {i['tipo']} | {_cel(i['legenda'])[:90]} | {lida} | {n or '—'} |")
        out += [""]
    out += ["## Plano solicitado para a Etapa 2", ""]
    if res.plano_etapa2:
        out += ["| ID | Objetivo | Alvos | Tipo de verificação | Prioridade |", "|---|---|---|---|---|"]
        for v in res.plano_etapa2:
            out.append(f"| {v.id} | {_cel(v.objetivo)} | {_cel(', '.join(v.alvos))} | {_cel(v.tipo)} | {v.prioridade} |")
    else:
        out.append("_Nenhuma verificação proposta._")
    out += ["", f"Viabilidade sem varredura irrestrita: **{'sim' if res.avaliacao.pesquisa_viavel_sem_varredura else 'não'}** "
                f"— {res.avaliacao.justificativa}", ""]

    pend = [i for i in res.itens if i.classificacao == "PONTO_A_CONFIRMAR" or
            i.categoria in ("AUSENCIA", "AMBIGUIDADE", "CONTRADICAO")]
    out += ["## Pontos a confirmar", ""]
    out += (_tabela_itens(pend, False) if pend else ["_Nenhum._"]) + [""]
    if gate.ressalvas:
        out += ["### Ressalvas do gate", ""] + [f"- {r}" for r in gate.ressalvas] + [""]

    lim = list(res.limitacoes) + [a.mensagem for a in achados if a.codigo in ("CONTEUDO_VISUAL", "SEM_HISTORICO")]
    out += ["## Limitações", "", "- Nenhuma consulta a SAP, BTP, CPI ou Workflow foi executada nesta etapa.",
            "- Existência de objetos e transações não foi confirmada; é objetivo da Etapa 2."]
    out += [f"- {l}" for l in dict.fromkeys(lim)] + [""]

    out += ["## Rastreabilidade", "",
            "Cada item acima referencia a seção e a localização na EF. Trechos de origem:", "",
            "| ID | Seção | Localização | Trecho de origem |", "|---|---|---|---|"]
    for i in res.itens:
        out.append(f"| {i.id} | {i.fonte.secao} | {', '.join(i.fonte.localizacao) or '—'} | {_cel(i.fonte.trecho)[:220]} |")
    out += ["", "### Mapa de seções da EF", "", "| Seção | Caminho |", "|---|---|"]
    out += [f"| {s.sid} | {_cel(s.path_str)} |" for s in doc.sections]
    return "\n".join(out) + "\n"


def render_pendencias(doc: EFDocument, res: ExtractionResult, gate: Gate,
                      achados: list[Achado], meta: dict) -> str:
    out = [f"# {res.controle.id_demanda} — Relatório de Pendências da EF", "",
           "> A EF não está apta para a descoberta técnica. **Nenhum pacote executável foi gerado "
           "para a Etapa 2.** Corrija os itens bloqueantes e reenvie a EF.", ""]
    out += _controle(doc, res, gate, meta)
    out += ["## Critérios bloqueantes", "", "| Critério | Descrição | Evidência | Origem |", "|---|---|---|---|"]
    for b in gate.bloqueantes:
        out.append(f"| {b['codigo']} | {_cel(b['descricao'])} | {_cel(b['evidencia'])} | {b['origem']} |")
    out += [""]
    if gate.a_confirmar:
        out += ["## Bloqueios a confirmar (apontados pela IA)", "",
                "| Critério | Descrição | Evidência apontada | Decisão |", "|---|---|---|---|"]
        for a in gate.a_confirmar:
            out.append(f"| {a['codigo']} | {_cel(a['descricao'])} | {_cel(a['evidencia'])} | ( ) Confirmar ( ) Descartar |")
        out += [""]
    pend = [i for i in res.itens if i.categoria in ("AUSENCIA", "AMBIGUIDADE", "CONTRADICAO")
            or i.classificacao == "PONTO_A_CONFIRMAR"]
    out += ["## Ausências, ambiguidades e pontos a confirmar", ""]
    out += (_tabela_itens(pend, False) if pend else ["_Nenhum._"]) + [""]
    if gate.ressalvas:
        out += ["## Ressalvas adicionais", ""] + [f"- {r}" for r in gate.ressalvas] + [""]
    out += ["## Resumo do que foi possível extrair", "", res.resumo_negocio.strip() or "_—_", ""]
    return "\n".join(out) + "\n"


def render(doc, res, gate, achados, meta) -> tuple[str, str]:
    """(nome do arquivo, conteúdo Markdown)."""
    if gate.status == INVALIDO:
        return (nome_arquivo(res.controle.id_demanda, meta.get("versao"), True),
                render_pendencias(doc, res, gate, achados, meta))
    return (nome_arquivo(res.controle.id_demanda, meta.get("versao")),
            render_pacote(doc, res, gate, achados, meta))
