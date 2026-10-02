"""Verificações determinísticas sobre a extração da IA.

Regra de ouro: estas verificações só ENDURECEM o resultado. Rebaixam itens cuja
fonte não se confirma, acrescentam referências que a IA deixou passar e registram
pendências. Nunca transformam um PONTO_A_CONFIRMAR em FATO.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .parser import EFDocument, _norm
from .schema import ExtractionResult, Fonte, Item


@dataclass
class Achado:
    codigo: str          # ex.: FONTE_NAO_LOCALIZADA
    severidade: str      # BLOQUEANTE | RESSALVA | INFO
    mensagem: str
    item_id: str = ""
    localizacao: list[str] = field(default_factory=list)


# identificadores técnicos que costumam aparecer em EF SAP
_TAB_CAMPO = re.compile(r"\b([ZY][A-Z0-9_/]{3,})-([A-Z0-9_]{2,})\b")   # ZTABELA-CAMPO
_REF_PATTERNS = [
    re.compile(r"\b[ZY][A-Z0-9_/]{3,}\b"),                     # objetos custom
    re.compile(r"\bEXIT_[A-Z0-9_]+\b"),                        # function exits
    re.compile(r"\bSMOD_[A-Z0-9_]+\b"),
    re.compile(r"\b(?:RV|MV|LW|WV)[0-9A-Z]{3,}[A-Z0-9_]*\b"),   # includes de exit (RV61AFZB, WV001F01)
    re.compile(r"\b(?:IF|CL)_[A-Z0-9_]{4,}(?:~[A-Z0-9_]+)?"),  # interfaces/classes SAP (com ~método)
]
_RUIDO = {"ZZZZ", "YYYY"}
TRECHO_MIN = 12   # caracteres; exceto quando o trecho é o próprio valor original
_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")
_CNPJ = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
_SEGREDO = re.compile(r"(?i)\b(senha|password|api[_ -]?key|token|secret)\b\s*[:=]\s*\S+")


def _tipo_por_nome(tok: str) -> str:
    if "-" in tok:
        return "CAMPO_TABELA"
    if "~" in tok:
        return "METODO"
    if tok.startswith("EXIT_"):
        return "EXIT"
    if tok.startswith("SMOD_"):
        return "EXIT"
    if tok.startswith(("ZCL", "YCL", "CL_")):
        return "CLASSE"
    if tok.startswith(("IF_", "ZIF", "YIF")):
        return "OUTRO"
    if re.match(r"^(RV|MV|LW|WV)", tok) or re.search(r"F\d{2}$|TOP$", tok):
        return "INCLUDE"
    if tok.startswith(("ZFM", "YFM", "Z_", "Y_")):
        return "FUNCAO"
    return "OUTRO"


def _fonte_texto(doc: EFDocument, fonte: Fonte) -> str:
    locs = doc.locs()
    partes = [locs[l][1].text for l in fonte.localizacao if l in locs]
    if not partes:  # a IA pode citar só a seção
        s = doc.section_by_id(fonte.secao)
        partes = [s.text()] if s else []
    return "\n".join(partes)


def _rebaixar(it: Item, motivo: str, achados: list[Achado], codigo: str) -> None:
    if it.classificacao != "PONTO_A_CONFIRMAR":
        it.classificacao = "PONTO_A_CONFIRMAR"
    it.confianca = "BAIXA"
    achados.append(Achado(codigo, "RESSALVA", motivo, it.id, list(it.fonte.localizacao)))


def verificar(doc: EFDocument, res: ExtractionResult, *, versao_informada: str) -> list[Achado]:
    achados: list[Achado] = []
    locs = doc.locs()
    sids = {s.sid for s in doc.sections}

    for it in res.itens:
        # 1) localização existe
        invalidas = [l for l in it.fonte.localizacao if l not in locs]
        if it.fonte.secao not in sids and not any(l in locs for l in it.fonte.localizacao):
            _rebaixar(it, f"Fonte inexistente no documento (seção {it.fonte.secao}, "
                          f"localização {it.fonte.localizacao}).", achados, "FONTE_INEXISTENTE")
            continue
        if invalidas:
            achados.append(Achado("LOCALIZACAO_INVALIDA", "INFO",
                                  f"Localizações ignoradas por não existirem: {invalidas}", it.id))
            it.fonte.localizacao = [l for l in it.fonte.localizacao if l in locs]

        # 2) trecho literal presente na fonte citada (anti-alucinação)
        texto_fonte = _fonte_texto(doc, it.fonte)
        trecho_n = _norm(it.fonte.trecho)
        if it.categoria != "DADO_SENSIVEL" and len(trecho_n) < TRECHO_MIN and \
                trecho_n != _norm(it.valor_original or ""):
            _rebaixar(it, f"Trecho de origem insuficiente para rastreabilidade ('{it.fonte.trecho}').",
                      achados, "TRECHO_INSUFICIENTE")
        elif it.fonte.trecho and trecho_n not in _norm(texto_fonte):
            achar = doc.find_loc_containing(it.fonte.trecho)
            if achar:  # trecho existe, mas em outro lugar: corrige a localização
                achados.append(Achado("LOCALIZACAO_CORRIGIDA", "INFO",
                                      f"Trecho encontrado em {achar}, não em {it.fonte.localizacao}.", it.id))
                it.fonte.localizacao = [achar]
                it.fonte.secao = locs[achar][0].sid
                texto_fonte = locs[achar][1].text
            else:
                _rebaixar(it, "Trecho de origem não encontrado literalmente na EF.",
                          achados, "TRECHO_NAO_LOCALIZADO")

        # 3) referência técnica: valor original obrigatório e presente na fonte
        if it.categoria == "REF_TECNICA":
            if not it.valor_original:
                _rebaixar(it, "Referência técnica sem valor original.", achados, "REF_SEM_VALOR")
            elif _norm(it.valor_original) not in _norm(texto_fonte):
                _rebaixar(it, f"Valor '{it.valor_original}' não aparece no trecho citado.",
                          achados, "REF_NAO_CONFIRMADA_NA_FONTE")

        # 4) normalização precisa de regra
        if it.valor_normalizado and it.valor_normalizado != it.valor_original and not it.regra_normalizacao:
            achados.append(Achado("NORMALIZACAO_SEM_REGRA", "RESSALVA",
                                  "Valor normalizado sem regra de normalização registrada.", it.id))

        # 5) ENTENDIMENTO nunca com confiança ALTA
        if it.classificacao == "ENTENDIMENTO" and it.confianca == "ALTA":
            it.confianca = "MEDIA"

        # 6) dado sensível: nunca guardar o valor
        if it.categoria == "DADO_SENSIVEL" and (it.valor_original or it.valor_normalizado):
            it.valor_original = it.valor_normalizado = None
            it.fonte.trecho = "[ocultado]"

        # 7) componente precisa de natureza
        if it.categoria == "COMPONENTE" and not it.natureza:
            achados.append(Achado("COMPONENTE_SEM_NATUREZA", "RESSALVA",
                                  "Componente sem natureza (NOVO/REMEDIACAO/EVOLUCAO).", it.id))

    # 8) cobertura: identificadores técnicos da EF que a IA não extraiu
    capturados = {_norm(i.valor_original or "").upper() for i in res.itens if i.valor_original}
    capturados |= {_norm(i.valor_normalizado or "").upper() for i in res.itens if i.valor_normalizado}
    texto_itens = " ".join(_norm(" ".join(filter(None, (i.valor_original, i.descricao,
                                                         i.objeto_origem, i.ancora))))
                           for i in res.itens).upper()
    faltantes: dict[str, str] = {}
    for s in doc.sections:
        for b in s.blocks:
            texto = b.text.upper()
            for m in _TAB_CAMPO.finditer(texto):           # pares tabela-campo primeiro
                faltantes.setdefault(m.group(0), b.loc)
            texto = _TAB_CAMPO.sub(" ", texto)              # evita capturar as partes soltas
            for pat in _REF_PATTERNS:
                for m in pat.findall(texto):
                    faltantes.setdefault(m.strip("_/~"), b.loc)
    # remove ruído, já capturados e prefixos truncados de outro token
    toks = [t for t in faltantes if len(t) >= 4 and t not in _RUIDO]
    faltantes = {t: faltantes[t] for t in toks
                 if t not in capturados and t not in texto_itens
                 and not any(o != t and o.startswith(t) for o in toks)}
    novos = []
    for n, (tok, loc) in enumerate(sorted(faltantes.items()), start=1):
        sec = locs[loc][0]
        res.itens.append(Item(
            id=f"AUTO{n:03d}", categoria="REF_TECNICA",
            descricao="Identificador técnico presente na EF e não extraído pela IA.",
            valor_original=tok, tipo_objeto=_tipo_por_nome(tok), escopo="INDEFINIDO",
            classificacao="PONTO_A_CONFIRMAR", confianca="BAIXA",
            fonte=Fonte(secao=sec.sid, localizacao=[loc], trecho=locs[loc][1].text[:300]),
        ))
        novos.append(tok)
    if novos:
        achados.append(Achado("REF_NAO_EXTRAIDA", "RESSALVA",
                              f"{len(novos)} identificador(es) técnico(s) presentes na EF não foram "
                              f"extraídos pela IA e foram incluídos automaticamente como PONTO_A_CONFIRMAR "
                              f"(escopo a confirmar): {', '.join(novos)}."))

    # 9) versão informada x histórico de revisão
    if doc.revisions:
        ultima = doc.revisions[-1]["versao"]
        if versao_informada and versao_informada.upper() != ultima.upper():
            achados.append(Achado("VERSAO_DIVERGENTE", "RESSALVA",
                                  f"Versão informada ({versao_informada}) difere da última "
                                  f"versão do histórico de revisão ({ultima}).",
                                  localizacao=[doc.revisions[-1]["loc"]]))
    else:
        achados.append(Achado("SEM_HISTORICO", "INFO", "Histórico de revisão não identificado."))

    # 10) dados sensíveis (varredura determinística; registra só a localização)
    for s in doc.sections:
        for b in s.blocks:
            for nome, pat in (("CPF", _CPF), ("CNPJ", _CNPJ), ("e-mail", _EMAIL), ("credencial", _SEGREDO)):
                if pat.search(b.text):
                    achados.append(Achado("DADO_SENSIVEL", "RESSALVA",
                                          f"Possível {nome} no texto (valor não reproduzido).",
                                          localizacao=[b.loc]))

    # 11) conteúdo visual não legível
    for s in doc.sections:
        if s.images:
            achados.append(Achado("CONTEUDO_VISUAL", "RESSALVA",
                                  f"A seção '{s.path_str}' contém {s.images} imagem(ns) "
                                  f"(ex.: esboços de tela) cujo conteúdo não foi lido em texto.",
                                  localizacao=[s.sid]))
    return achados
