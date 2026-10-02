"""Ponta a ponta pela API real, com todos os pacotes instalados (SAP e IA simulados).
Fluxo: upload -> MM valida -> MM envia (ef.validada) -> Orquestrador cria o handoff e
entrega ao Dev -> Dev remedia a partir do MESMO upload, sem novo envio."""
import asyncio
import json
import os
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SEM = {"resumo_negocio": "Bloqueio de pedido.", "criterios": [{"codigo": "B06", "bloqueia": False, "evidencia": "ok"},
                                                            {"codigo": "B07", "bloqueia": False, "evidencia": "ok"}]}
REV = {"secoes": [{"id": "regras", "status": "ATENCAO", "resumo": "Regras ok, falta exceção detalhada.",
                   "achados": [{"tipo": "MELHORIA", "descricao": "Detalhar a exceção.", "trecho": "", "sugestao": "RN-01..."}]}]}
RASC = {"identificacao": {"id_gap": "MM-201", "descricao_gap": "Bloqueio", "modulo": "MM"},
        "resumo": {"tipos_programa": ["Enhancement"], "prioridade": "Alta",
                   "inventario": [{"objeto": "ZCL_MM_CERT_CHECK", "tipo": "Enhancement", "natureza": "NOVO", "objetivo": "x"}]},
        "objetivo": {"as_is": "a", "problema": "b", "to_be": "c", "beneficio": "d", "criterio_sucesso": "e"},
        "processos": [{"processo": "Pedido", "transacao": "ME21N", "papel": "Comprador"}],
        "regras": [{"id": "RN-01", "condicao": "sem certificação", "acao": "bloquear", "excecao": "grupo de exceção"}],
        "escopo": {"incluido": ["ME21N"], "fora_escopo": ["ME31K"], "premissas": ["p"]},
        "fluxo": [{"passo": 1, "ator": "Comprador", "sistema": "S/4", "acao": "cria"}],
        "sistemas": [{"sistema": "S/4HANA", "tipo": "SAP", "papel": "x", "integracao": "Não"}],
        "testes": [{"cenario": "s", "passos": "p", "resultado_esperado": "bloqueio"}]}


class _R:
    def __init__(self, t): self.text, self.finish_reason = t, "stop"


class IA:
    def invoke(self, system, turns):
        if "RASCUNHO de uma Especificação" in system: return _R(json.dumps(RASC))
        if "revisando uma Especificação" in system: return _R(json.dumps(REV))
        if "Você lê imagens" in system: return _R(json.dumps({"titulo_tela": "", "abas": [], "campos": [], "botoes": []}))
        return _R(json.dumps(SEM))


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    dados = tmp_path_factory.mktemp("dados")
    os.environ.update({"OPUSCORE_HOME": str(RAIZ), "OPUSCORE_DATA": str(dados), "OPUSCORE_DB": str(dados / "t.db"),
                       "LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "teste"})
    os.environ.pop("OPUSCORE_PLUGINS", None)
    import opuscore_ef.intake.extractor as ex
    import opuscore_ef.intake.pipeline as pl
    ex.load_provider = lambda *a, **k: IA()
    pl.load_provider = ex.load_provider
    from fastapi.testclient import TestClient
    from opuscore_core.contratos.plugin import Manifesto, PluginBase
    from opuscore_core.sdk.testes import MCPFalso
    from opuscore_platform.db.engine import reiniciar_engine
    from opuscore_platform.gateway import create_app
    reiniciar_engine()

    class Quebrado(PluginBase):
        manifesto = Manifesto(key="quebrado", nome="Quebrado")
        def rotas(self, obter_ctx): raise RuntimeError("bug do plugin")

    app = create_app(extras=[Quebrado()], iniciar_mcp=False, orquestrador_ativo=False)
    with TestClient(app) as c:
        app.state.mcp = MCPFalso({
            "sap_health": {"ok": True, "system": "a4h", "read_only": True},
            "sap_z_dependencies": lambda a: [{"name": a["object_name"], "type": "CLAS/OC", "seed": True, "depth": 0}],
            "sap_config_table": lambda a: {"table": a["table_name"], "description": "d", "delivery_class": "C",
                                           "columns": [{"name": "MANDT"}, {"name": "WERKS", "description": "Centro"}],
                                           "rows": [{"MANDT": "001", "WERKS": "1000"}], "total": 1, "truncated": False}})
        c.app_ref = app
        yield c


@pytest.fixture(scope="module")
def ef_docx(tmp_path_factory):
    import opuscore_ef as ef
    _, caminho, _ = ef.gerar_rascunho("ws", nome_workshop="WS.docx", template=RAIZ / "config/templates/EF_template.docx",
                                      destino=tmp_path_factory.mktemp("ef") / "MM-201.docx", provider=IA())
    return caminho


def test_plugins_e_isolamento(cliente):
    sit = {p["key"]: p for p in cliente.get("/api/plataforma/plugins").json()}
    assert {k for k, v in sit.items() if v["status"] == "ok"} == {
        "arquiteto", "dev-abap", "funcional-mm", "funcional-sd", "integracao", "lider-tecnico", "orquestrador", "qualidade"}
    assert sit["quebrado"]["status"] == "erro" and "bug do plugin" in sit["quebrado"]["erro"]
    assert cliente.get("/health").json()["sap"] == "a4h"


def test_consultores_com_tela(cliente):
    pid = cliente.get("/api/plataforma/projects").json()[0]["id"]
    cons = {c["key"]: c for c in cliente.get(f"/api/plataforma/projects/{pid}/consultores").json()}
    assert len(cons) == 8
    assert cons["funcional-mm"]["tela"] == "mm" and cons["funcional-mm"]["web"]["entrada"].startswith("/c/funcional-mm/main.js")
    assert cons["dev-abap"]["tela"] == "dev" and cons["orquestrador"]["tela"] == "orquestrador"
    assert cons["arquiteto"]["tela"] is None
    assert cliente.get("/c/funcional-mm/main.js").status_code == 200


def test_fluxo_mm_valida_envia_e_dev_recebe(cliente, ef_docx):
    app = cliente.app_ref
    pid = cliente.get("/api/plataforma/projects").json()[0]["id"]
    up = cliente.post("/api/plataforma/uploads", files={"file": ("MM-201.docx", ef_docx.read_bytes())}).json()
    v = cliente.post("/api/c/funcional-mm/ef/validar", json={"project_id": pid, "upload_id": up["upload_id"],
                                                               "imagens": "nenhuma"})
    assert v.status_code == 200, v.text
    vj = v.json()
    assert vj["pode_enviar"] and "## 🔎 Revisão seção por seção" in vj["relatorio"]
    nomes = [d["nome"] for d in vj["downloads"]]
    assert "handoff_etapa2.json" in nomes
    rel = next(d for d in vj["downloads"] if d["nome"].endswith(".md") and "Validacao" in d["nome"])
    assert cliente.get(rel["url"]).status_code == 200

    e = cliente.post("/api/c/funcional-mm/ef/enviar", json={"project_id": pid, "artifact_id": vj["artifact_id"]})
    assert e.status_code == 200, e.text
    hs = cliente.get("/api/plataforma/orquestracao/handoffs", params={"para": "dev-abap"}).json()
    assert len(hs) == 1 and hs[0]["de"] == "funcional-mm" and hs[0]["payload"]["upload_id"] == up["upload_id"]
    asyncio.run(app.state.orquestrador.processar_pendentes())
    audit = (Path(os.environ["OPUSCORE_DATA"]) / "audit" / "plataforma.jsonl").read_text(encoding="utf-8")
    assert "ef_validada_recebida" in audit
    assert cliente.post(f"/api/plataforma/orquestracao/handoffs/{hs[0]['id']}/acao", json={"acao": "aceitar"}).json()["estado"] == "ACEITO"

    plano = cliente.post("/api/c/dev-abap/remediation/plan", json={"project_id": pid, "upload_id": hs[0]["payload"]["upload_id"]})
    assert plano.status_code == 200 and "ZCL_MM_CERT_CHECK" in plano.json()["seeds"]


def test_mm_regras_por_projeto_e_analises(cliente):
    pid = cliente.get("/api/plataforma/projects").json()[0]["id"]
    regras = cliente.get("/api/c/funcional-mm/secoes", params={"project_id": pid}).json()
    assert next(r for r in regras if r["id"] == "processos")["editado"]          # ajuste de MM aplicado
    cliente.put("/api/c/funcional-mm/secoes/regras", json={"project_id": pid, "prompt": "Regra do projeto."})
    assert cliente.get("/api/c/funcional-mm/secoes/regras/historico", params={"project_id": pid}).json()[0]["versao"] == 1
    assert cliente.put("/api/c/funcional-mm/secoes/regras", json={"project_id": pid, "prompt": " "}).status_code == 400
    r = cliente.post("/api/c/funcional-mm/analises/org", json={"project_id": pid}).json()
    assert [b["columns"] for b in r["blocos"]][0] == [{"name": "WERKS", "description": "Centro"}]


def test_erros_padronizados_e_download_seguro(cliente):
    pid = cliente.get("/api/plataforma/projects").json()[0]["id"]
    r = cliente.post("/api/c/dev-abap/object-report", json={"project_id": pid, "object_name": "compare ZA com ZB"})
    assert r.status_code == 400 and r.json()["codigo"] == "invalido" and r.json()["request_id"]
    assert cliente.get("/api/plataforma/legado/..%2F..%2Fx/a.docx").status_code in (400, 404)
    assert cliente.get("/api/plataforma/artefatos/" + "0" * 32 + "/arquivos/x.docx").status_code == 404
