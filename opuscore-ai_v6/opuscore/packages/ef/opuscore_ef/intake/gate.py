"""Decisão do gate — feita pelo Python, não pela IA.

Dois tipos de bloqueio:
  - DEFINITIVO: vem das regras determinísticas (verificáveis). Ex.: sem objetivo,
    sem ator, sem referência técnica, remediação sem objeto de origem.
  - A CONFIRMAR: vem da IA (B06 escopo contraditório, B07 regra ambígua, ou a IA
    endurecendo outro critério). É um julgamento semântico: não invalida a EF
    sozinho. Aparece em destaque para uma pessoa (funcional ou Líder Técnico)
    confirmar ou descartar.

Decisão:
  algum bloqueio definitivo                        -> INVALIDO_PARA_DESCOBERTA
  bloqueio a confirmar / ressalvas / EF não aprovada -> VALIDO_COM_RESSALVAS
  caso contrário                                   -> VALIDO_PARA_DESCOBERTA
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .checks import Achado
from .schema import ExtractionResult

CRITERIOS = {
    "B01": "ausência de descrição do negócio",
    "B02": "ausência de objetivo ou resultado esperado",
    "B03": "ausência de processo ou ator",
    "B04": "nenhuma âncora técnica ou funcional",
    "B05": "sistemas completamente desconhecidos",
    "B06": "escopo contraditório",
    "B07": "regra principal ambígua",
    "B08": "anexo essencial ausente",
    "B09": "componente de remediação sem objeto de origem e sem âncora funcional",
}

VALIDO = "VALIDO_PARA_DESCOBERTA"
RESSALVAS = "VALIDO_COM_RESSALVAS"
INVALIDO = "INVALIDO_PARA_DESCOBERTA"


@dataclass
class Gate:
    status: str
    justificativa: list[str]
    bloqueantes: list[dict] = field(default_factory=list)   # definitivos {codigo, descricao, evidencia, origem}
    ressalvas: list[str] = field(default_factory=list)
    a_confirmar: list[dict] = field(default_factory=list)   # bloqueios apontados pela IA, a confirmar


def _tem(res: ExtractionResult, *cats: str, confirmados: bool = False) -> bool:
    return any(i.categoria in cats and (not confirmados or i.classificacao != "PONTO_A_CONFIRMAR")
               for i in res.itens)


def decidir(res: ExtractionResult, achados: list[Achado], *, estado: str) -> Gate:
    bloq: dict[str, dict] = {}
    a_confirmar: dict[str, dict] = {}
    ressalvas: list[str] = []

    # 1) critérios avaliados pela IA
    avaliados = {c.codigo: c for c in res.criterios}
    for cod, desc in CRITERIOS.items():
        c = avaliados.get(cod)
        if c is None:
            ressalvas.append(f"Critério {cod} ({desc}) não foi avaliado.")
        elif c.bloqueia:
            if c.origem == "regra":
                bloq[cod] = {"codigo": cod, "descricao": desc, "evidencia": c.evidencia,
                             "origem": "verificação automática"}
            else:
                a_confirmar[cod] = {"codigo": cod, "descricao": desc, "evidencia": c.evidencia,
                                    "origem": "IA", "localizacao": list(c.localizacao)}

    # 2) verificações próprias (só endurecem)
    def forcar(cod: str, evidencia: str) -> None:
        bloq.setdefault(cod, {"codigo": cod, "descricao": CRITERIOS[cod],
                              "evidencia": evidencia, "origem": "verificação automática"})

    if not res.resumo_negocio.strip() and not _tem(res, "AS_IS", "TO_BE", "JUSTIFICATIVA"):
        forcar("B01", "Sem resumo do negócio e sem itens de processo ou justificativa.")
    if not _tem(res, "OBJETIVO"):
        forcar("B02", "Nenhum item de OBJETIVO foi extraído.")
    if not _tem(res, "PROCESSO", "AS_IS", "TO_BE") or not _tem(res, "ATOR"):
        forcar("B03", "Faltam itens de processo (AS_IS/TO_BE) ou de ATOR.")
    if not _tem(res, "REF_TECNICA", "ANCORA_FUNCIONAL", confirmados=True):
        forcar("B04", "Nenhuma referência técnica ou âncora funcional confirmada na fonte.")
    for i in res.itens:
        if i.categoria == "COMPONENTE" and i.natureza == "REMEDIACAO" and not (i.objeto_origem or i.ancora):
            forcar("B09", f"Componente {i.id} ({i.descricao[:80]}) é REMEDIACAO sem objeto de origem e sem âncora.")
    if not res.avaliacao.pesquisa_viavel_sem_varredura:
        forcar("B04", "A própria avaliação indica que a Etapa 2 exigiria varredura irrestrita: "
                      + res.avaliacao.justificativa)

    # 3) ressalvas não bloqueantes
    n_conf = sum(1 for i in res.itens if i.classificacao == "PONTO_A_CONFIRMAR")
    if n_conf:
        ressalvas.append(f"{n_conf} item(ns) classificados como PONTO_A_CONFIRMAR.")
    for cat, rot in (("AUSENCIA", "ausência(s)"), ("AMBIGUIDADE", "ambiguidade(s)"),
                     ("CONTRADICAO", "contradição(ões)")):
        n = sum(1 for i in res.itens if i.categoria == cat)
        if n:
            ressalvas.append(f"{n} {rot} registrada(s) na EF.")
    for a in achados:
        if a.severidade in ("RESSALVA", "BLOQUEANTE"):
            ressalvas.append(a.mensagem)
    if estado != "APROVADA":
        ressalvas.append(f"EF no estado {estado}: o gate máximo é VALIDO_COM_RESSALVAS.")

    # um bloqueio definitivo prevalece sobre o mesmo critério apontado pela IA
    for cod in list(a_confirmar):
        if cod in bloq:
            a_confirmar.pop(cod)
    for a in a_confirmar.values():
        ressalvas.insert(0, f"BLOQUEIO A CONFIRMAR — {a['codigo']} ({a['descricao']}), apontado pela IA: "
                            f"{a['evidencia']}")

    # 4) decisão
    if bloq:
        status = INVALIDO
        just = [f"{b['codigo']} ({b['descricao']}): {b['evidencia']}" for b in bloq.values()]
    elif ressalvas:
        status = RESSALVAS
        just = ["Nenhum bloqueio definitivo identificado pelas regras."]
        if a_confirmar:
            just.append(f"{len(a_confirmar)} bloqueio(s) apontado(s) pela IA "
                        f"({', '.join(a_confirmar)}) aguardam confirmação do funcional ou do Líder Técnico.")
        just.append(f"{len(ressalvas)} ressalva(s) devem ser tratadas na Etapa 2 ou com o funcional.")
    else:
        status = VALIDO
        just = ["Nenhum critério bloqueante e nenhuma ressalva identificados."]
    return Gate(status, just, list(bloq.values()), ressalvas, list(a_confirmar.values()))
