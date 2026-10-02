import asyncio
import pytest
from sqlmodel import Session, SQLModel, create_engine
from opuscore_orchestrator import Orquestrador
from opuscore_orchestrator.modelos import EntregaEvento

PAYLOAD = {"gate": "VALIDO_COM_RESSALVAS", "upload_id": "u1", "ef_arquivo": "SD-034.docx",
           "objetos_no_escopo": ["ZRMM_RECALC_PR_BLOQ"]}


@pytest.fixture
def orq(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path/'o.db'}")
    SQLModel.metadata.create_all(eng)
    return Orquestrador(lambda: Session(eng), lambda key: {"ctx_de": key}, max_tentativas=2)


def _rodar(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


def test_evento_entregue_e_handoff_criado(orq):
    recebidos = []
    async def tratar(ev, ctx): recebidos.append((ev.tipo, ev.gap_id, ctx["ctx_de"]))
    orq.assinar("ef.validada", "dev-abap", "ao_receber", tratar)
    async def fluxo():
        await orq.publicador("funcional-mm").publicar("ef.validada", projeto_id="p1", gap_id="SD-034", payload=PAYLOAD)
        await orq.processar_pendentes()
        await orq.processar_pendentes()            # não entrega de novo
    asyncio.run(fluxo())
    assert recebidos == [("ef.validada", "SD-034", "dev-abap")]
    hs = orq.listar_handoffs(para="dev-abap")
    assert len(hs) == 1 and hs[0]["de"] == "funcional-mm" and hs[0]["estado"] == "CRIADO"
    assert orq.painel("p1")["pendentes_por_consultor"] == {"dev-abap": 1}


def test_payload_invalido_e_recusado(orq):
    with pytest.raises(Exception):
        asyncio.run(orq.publicador("x").publicar("ef.validada", projeto_id="p", gap_id="G", payload={"gate": "INVALIDO"}))


def test_falha_vai_para_fila_e_reprocessa(orq):
    estado = {"falhar": True, "chamadas": 0}
    async def tratar(ev, ctx):
        estado["chamadas"] += 1
        if estado["falhar"]:
            raise RuntimeError("SAP fora")
    orq.assinar("et.gerada", "qualidade", "t", tratar)
    async def fluxo():
        await orq.publicador("dev-abap").publicar("et.gerada", projeto_id="p", gap_id="G", payload={"artefato": "a"})
        await orq.processar_pendentes()                    # 1ª falha: agenda nova tentativa
        with orq.sessao() as s:                            # adianta o relógio da nova tentativa
            for e in s.query(EntregaEvento).all():
                e.proximo_em = e.proximo_em.replace(year=2000); s.add(e)
            s.commit()
        await orq.processar_pendentes()                    # 2ª falha: fila de falhas
    asyncio.run(fluxo())
    falhas = orq.painel("p")["falhas"]
    assert len(falhas) == 1 and "SAP fora" in falhas[0]["erro"]
    estado["falhar"] = False
    orq.reprocessar(falhas[0]["id"])
    asyncio.run(orq.processar_pendentes())
    assert orq.painel("p")["falhas"] == [] and estado["chamadas"] == 3


def test_consultor_nao_instalado_nao_perde_handoff(orq):
    asyncio.run(orq.publicador("funcional-mm").publicar("ef.validada", projeto_id="p", gap_id="G", payload=PAYLOAD))
    assert orq.listar_handoffs(projeto_id="p")[0]["estado"] == "CRIADO"


def test_transicoes(orq):
    asyncio.run(orq.publicador("funcional-mm").publicar("ef.validada", projeto_id="p", gap_id="G", payload=PAYLOAD))
    hid = orq.listar_handoffs()[0]["id"]
    with pytest.raises(ValueError):
        orq.transitar(hid, "concluir")                     # CRIADO -> CONCLUIDO não pode
    assert orq.transitar(hid, "aceitar", por="renato")["estado"] == "ACEITO"
    with pytest.raises(ValueError):
        orq.transitar(hid, "devolver")                     # devolver exige motivo
    h = orq.transitar(hid, "devolver", motivo="Falta a volumetria")
    assert h["estado"] == "DEVOLVIDO" and [x["estado"] for x in h["historico"]] == ["CRIADO", "ACEITO", "DEVOLVIDO"]
