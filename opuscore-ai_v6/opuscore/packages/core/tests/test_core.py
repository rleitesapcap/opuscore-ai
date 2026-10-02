import asyncio, json
import pytest
from opuscore_core.contratos.eventos import Evento, esquemas, validar_payload
from opuscore_core.contratos.handoff import EstadoHandoff as E, pode_transitar
from opuscore_core.contratos.plugin import Manifesto, PluginBase
from opuscore_core.sdk.testes import ContextoFalso, MCPFalso
from opuscore_core.sdk.uso import resumo
from opuscore_core.contratos.erros import ErroOpus
from opuscore_core.regras.clean_core import NIVEIS, texto_para_prompt
from opuscore_core.versao import CONTRATOS_SUPORTADOS


def test_esquemas_v1_registrados():
    assert {("ef.validada", 1), ("et.gerada", 1), ("remediacao.concluida", 1), ("ef.rascunho_gerado", 1)} <= set(esquemas())


def test_ef_validada_recusa_gate_invalido():
    ok = validar_payload("ef.validada", 1, {"gate": "VALIDO_COM_RESSALVAS", "upload_id": "u1", "ef_arquivo": "EF.docx"})
    assert ok["objetos_no_escopo"] == []
    with pytest.raises(Exception):
        validar_payload("ef.validada", 1, {"gate": "INVALIDO_PARA_DESCOBERTA", "upload_id": "u", "ef_arquivo": "x"})
    with pytest.raises(ValueError):
        validar_payload("evento.inexistente", 1, {})


def test_transicoes_de_handoff():
    assert pode_transitar(E.CRIADO, E.ACEITO) and pode_transitar(E.ACEITO, E.CONCLUIDO)
    assert not pode_transitar(E.CONCLUIDO, E.ACEITO) and not pode_transitar(E.CRIADO, E.EM_ANDAMENTO)


def test_manifesto_padroes_e_contrato_suportado():
    m = Manifesto(key="x", nome="X")
    assert m.contrato_plugin in CONTRATOS_SUPORTADOS["plugin"] and m.assina == {} and PluginBase().perfil().skills == []


def test_custo_opus_e_haiku():
    r = resumo([{"input": 1_000_000, "output": 0, "cache_read": 0, "cache_creation": 0}], "claude-haiku-4-5-20251001")
    assert r["custo_estimado_usd"] == 1.0
    assert resumo([], "modelo-desconhecido")["custo_estimado_usd"] is None


def test_mcp_falso_converte_erro_em_erro_opus():
    mcp = MCPFalso({"sap_x": {"error": "Objeto não encontrado"}, "sap_y": {"ok": 1}})
    assert asyncio.run(mcp.chamar("sap_y")) == {"ok": 1}
    with pytest.raises(ErroOpus) as e:
        asyncio.run(mcp.chamar("sap_x"))
    assert e.value.status == 404


def test_eventos_memoria_valida_payload():
    ctx = ContextoFalso()
    eid = asyncio.run(ctx.eventos.publicar("et.gerada", projeto_id="p", gap_id="G1", payload={"artefato": "a1"}))
    assert ctx.eventos.publicados[0].id == eid and ctx.eventos.publicados[0].payload["ok"] is True


def test_clean_core_niveis():
    assert set(NIVEIS) == {"A", "B", "C", "D"} and "Nível D" in texto_para_prompt()


def test_temperatura_opcional(monkeypatch):
    from opuscore_core.sdk.ia import _temperatura
    from opuscore_core.sdk.config import LLMProviderCfg
    cfg = LLMProviderCfg(kind="anthropic", base_url="x", model="claude-opus-5-5", temperature=0.2)
    monkeypatch.setenv("LLM_TEMPERATURE", "off")
    assert _temperatura(cfg) == {}
    monkeypatch.delenv("LLM_TEMPERATURE")
    assert _temperatura(cfg) == {"temperature": 0.2}
    assert _temperatura(cfg.model_copy(update={"temperature": None})) == {}
