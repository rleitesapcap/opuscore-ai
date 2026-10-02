import asyncio, json
import httpx
import pytest
from opuscore_connectors.config import SapSystemCfg
from opuscore_connectors.sap_adt.cliente import ADTClient, ADTError, _parse_table_source
from opuscore_connectors.seguranca.politicas import pode_ler_config
from opuscore_connectors.comum.registro import ferramenta, ferramentas
import opuscore_connectors.sap_adt.ferramentas as fsap

CTS = "application/vnd.sap.adt.transportorganizer.v1+xml"


def _adt(handler):
    adt = ADTClient(SapSystemCfg(base_url="http://sap", client="001", user="u", password="p"), guard=object(), system_name="t")
    adt._client = httpx.AsyncClient(base_url="http://sap", transport=httpx.MockTransport(handler))
    return adt


def test_toda_ferramenta_tem_nivel():
    assert ferramentas("sap") and all(f["nivel"] in {"leitura_tecnica", "leitura_dados", "escrita"} for f in ferramentas())
    with pytest.raises(ValueError):
        ferramenta(sistema="x", nivel="qualquer")


def test_servidor_expoe_as_ferramentas_sap():
    from opuscore_connectors.servidor import criar_servidor
    nomes = {t.name for t in asyncio.run(criar_servidor().list_tools())}
    assert {"sap_get_source", "sap_transport_objects", "sap_config_table"} <= nomes


def test_cts_accept_e_limu_vira_classe():
    xml = f"""<tm:root xmlns:tm="http://www.sap.com/cts/adt/tm"><tm:request><tm:task>
      <tm:abap_object tm:pgmid="R3TR" tm:type="PROG" tm:name="ZSDR_FOB_ENQUEUE_REQUEST"/>
      <tm:abap_object tm:pgmid="LIMU" tm:type="METH" tm:name="ZCX_SD_FOB_TM_ERROR           CONSTRUCTOR"/>
      <tm:abap_object tm:pgmid="R3TR" tm:type="PROG" tm:name="ZSDR_FOB_ENQUEUE_REQUEST"/></tm:task></tm:request></tm:root>"""
    def h(req):
        return httpx.Response(200, text=xml) if CTS in req.headers.get("accept", "") else httpx.Response(406)
    refs = asyncio.run(_adt(h).transport_objects("a4hk900148"))
    assert [(r.name, r.type) for r in refs] == [("ZSDR_FOB_ENQUEUE_REQUEST", "PROG"), ("ZCX_SD_FOB_TM_ERROR", "CLAS")]


def test_resolve_tenta_curinga():
    xml = ('<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core"><adtcore:objectReference '
           'adtcore:uri="/x" adtcore:type="PROG/P" adtcore:name="ZSDR_X"/></adtcore:objectReferences>')
    vazio = '<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core"/>'
    h = lambda req: httpx.Response(200, text=xml if req.url.params["query"].endswith("*") else vazio)
    assert asyncio.run(_adt(h).resolve("zsdr_x")).type == "PROG/P"
    with pytest.raises(ADTError):
        asyncio.run(_adt(lambda r: httpx.Response(200, text=vazio)).resolve("ZNAO"))


def test_data_preview_renova_csrf():
    estado = {"expirou": True}
    xml = ('<dataPreview:tableData xmlns:dataPreview="http://www.sap.com/adt/dataPreview"><dataPreview:totalRows>2</dataPreview:totalRows>'
           '<dataPreview:columns><dataPreview:metadata dataPreview:name="BSART" dataPreview:description="Tipo"/>'
           '<dataPreview:dataSet><dataPreview:data>NB</dataPreview:data><dataPreview:data>ZNB</dataPreview:data></dataPreview:dataSet></dataPreview:columns></dataPreview:tableData>')
    def h(req):
        if req.method == "GET":
            return httpx.Response(200, headers={"x-csrf-token": "tok"})
        if estado["expirou"]:
            estado["expirou"] = False
            return httpx.Response(403, text="CSRF token validation failed")
        return httpx.Response(200, text=xml)
    d = asyncio.run(_adt(h).table_contents("T161"))
    assert d["total"] == 2 and [r["BSART"] for r in d["rows"]] == ["NB", "ZNB"]


def test_classe_de_entrega_e_politica():
    assert _parse_table_source("@AbapCatalog.deliveryClass : #C\ndefine table t161 {\n}")["delivery_class"] == "C"
    assert pode_ler_config("T161", "C", [])[0]
    assert not pode_ler_config("LFA1", "A", ["LFA1"])[0]        # classe A nunca, nem se estiver na lista
    assert pode_ler_config("T161T", "", ["T161T"])[0] and not pode_ler_config("ZTAB", "", ["T161T"])[0]


class _Det:
    def __init__(self, classe): self.metadata = {"delivery_class": classe, "fields": [{"name": "X"}], "description": "d"}


class _ADTFalso:
    system_name, read_only = "t", True
    class guard:
        class audit:
            eventos = []
            @classmethod
            def record(cls, ev, **k): cls.eventos.append((ev, k["table"]))
    def __init__(self, classe): self.classe = classe
    async def get_table(self, n): return _Det(self.classe)
    async def table_contents(self, n, max_rows=200): return {"columns": [{"name": "A"}], "rows": [{"A": "1"}], "total": 1}
    async def aclose(self): pass


def test_sap_config_table_recusa_classe_a_e_audita(monkeypatch):
    monkeypatch.setattr(fsap, "config_conectores", lambda: type("C", (), {"tabelas_config_sem_classe": []})())
    monkeypatch.setattr(fsap, "_adt", lambda amb="": _ADTFalso("C"))
    assert "rows" in json.loads(asyncio.run(fsap.sap_config_table("T161")))
    monkeypatch.setattr(fsap, "_adt", lambda amb="": _ADTFalso("A"))
    assert "classe de entrega A" in json.loads(asyncio.run(fsap.sap_config_table("LFA1")))["error"]
    assert ("config_read", "T161") in _ADTFalso.guard.audit.eventos
