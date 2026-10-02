"""Ferramentas MCP do SAP ADT. A descrição (docstring) de cada uma é o que a IA lê
para decidir quando usá-la: escreva para o modelo (quando usar, limites, o que não faz)."""
from __future__ import annotations

import json

import httpx

from ..comum.registro import erro, ferramenta
from ..config import config_conectores, config_sap
from ..seguranca.guard import build_guard
from ..seguranca.politicas import MAX_LINHAS_CONFIG, pode_ler_config
from .analisador import build_object_report, report_to_graph
from .cliente import ADTClient, ADTError


def _adt(ambiente: str = "") -> ADTClient:
    cfg = config_sap()
    nome = ambiente.strip() or cfg.default
    if nome not in cfg.systems:
        raise ADTError(f"Ambiente SAP '{nome}' não está configurado (config.yaml, seção sap.systems).")
    return ADTClient(cfg.systems[nome], guard=build_guard(nome, interactive=False), system_name=nome)


async def _executar(fn, ambiente: str = ""):
    try:
        adt = _adt(ambiente)
    except ADTError as e:
        return erro(str(e))
    try:
        return await fn(adt)
    except (ADTError, httpx.HTTPError) as e:
        return erro(str(e))
    finally:
        await adt.aclose()


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_health(ambiente: str = "") -> str:
    """Testa a conexão ADT com o SAP configurado e informa o modo (somente leitura)."""
    async def f(adt):
        await adt.discovery()
        return json.dumps({"ok": True, "system": adt.system_name, "read_only": adt.read_only})
    r = await _executar(f, ambiente)
    return r.replace('{"error"', '{"ok": false, "error"', 1) if r.startswith('{"error"') else r


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_object_report(object_name: str, ambiente: str = "") -> str:
    """Relatório de um objeto do repositório SAP: código-fonte ou campos DDIC, quem usa
    (where-used) e o grafo de dependências. Somente leitura. Ex.: MARA, um programa, uma classe."""
    async def f(adt):
        rep = await build_object_report(adt, object_name)
        return json.dumps({"report": rep.to_dict(), "graph": report_to_graph(rep)}, ensure_ascii=False)
    return await _executar(f, ambiente)


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_search_objects(query: str, max_results: int = 20, ambiente: str = "") -> str:
    """Busca objetos no repositório SAP por nome ou padrão (ex.: 'MAR*')."""
    async def f(adt):
        return json.dumps([r.__dict__ for r in await adt.search(query, max_results)], ensure_ascii=False)
    return await _executar(f, ambiente)


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_where_used(object_name: str, ambiente: str = "") -> str:
    """Lista os objetos que referenciam o objeto informado (análise de impacto)."""
    async def f(adt):
        ref = await adt.resolve(object_name)
        return json.dumps([u.__dict__ for u in await adt.where_used(ref)], ensure_ascii=False)
    return await _executar(f, ambiente)


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_get_source(object_name: str, ambiente: str = "") -> str:
    """Retorna o código-fonte de um objeto (programa, classe, CDS, FM). Vazio para tabelas."""
    async def f(adt):
        ref = await adt.resolve(object_name)
        src = await adt.get_source(ref)
        return json.dumps({"name": ref.name, "type": ref.type, "source": src}, ensure_ascii=False)
    return await _executar(f, ambiente)


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_transport_objects(request_id: str, ambiente: str = "") -> str:
    """Lista os objetos contidos numa request/task de transporte do SAP (CTS)."""
    async def f(adt):
        return json.dumps([r.__dict__ for r in await adt.transport_objects(request_id)], ensure_ascii=False)
    return await _executar(f, ambiente)


@ferramenta(sistema="sap", nivel="leitura_tecnica")
async def sap_z_dependencies(object_name: str, max_depth: int = 2, ambiente: str = "") -> str:
    """Descobre os objetos Z/Y que o objeto USA (includes, classes, FMs, tabelas),
    recursivamente. Ignora objetos standard. Base para a lista de remediação."""
    async def f(adt):
        return json.dumps(await adt.z_dependencies(object_name, max_depth=max_depth), ensure_ascii=False)
    return await _executar(f, ambiente)


@ferramenta(sistema="sap", nivel="leitura_dados")
async def sap_config_table(table_name: str, max_rows: int = 200, ambiente: str = "") -> str:
    """Lê o CONTEÚDO de uma tabela de CONFIGURAÇÃO (customizing) do SAP, como tipos de
    documento de compras (T161), tipos de material (T134) ou centros (T001W).

    Use para responder como um processo está configurado no ambiente. Só lê tabelas de
    configuração: a classe de entrega é conferida no SAP, e tabelas de dados de negócio
    (cadastros e transações, classe A) são recusadas. Para ver só os CAMPOS de uma tabela,
    use sap_object_report. Máximo de 500 linhas."""
    nome = (table_name or "").strip().upper()

    async def f(adt):
        det = await adt.get_table(nome)
        meta = det.metadata or {}
        if meta.get("read_error") and not meta.get("fields"):
            return erro(f"Tabela {nome} não encontrada no SAP conectado.")
        classe = meta.get("delivery_class", "")
        ok, motivo = pode_ler_config(nome, classe, config_conectores().tabelas_config_sem_classe)
        if not ok:
            return erro(motivo)
        dados = await adt.table_contents(nome, max_rows=min(max(1, int(max_rows)), MAX_LINHAS_CONFIG))
        try:
            adt.guard.audit.record("config_read", system=adt.system_name, table=nome,
                                   delivery_class=classe or "?", rows=len(dados["rows"]))
        except Exception:  # noqa: BLE001 - auditoria não derruba a leitura
            pass
        return json.dumps({"table": nome, "description": meta.get("description", ""), "delivery_class": classe,
                           "columns": dados["columns"], "rows": dados["rows"], "total": dados["total"],
                           "truncated": dados["total"] > len(dados["rows"])}, ensure_ascii=False)
    return await _executar(f, ambiente)


def registrar(mcp) -> None:
    from ..comum.registro import ferramentas
    for f in ferramentas("sap"):
        mcp.tool()(f["fn"])
