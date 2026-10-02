"""opuscore-sap-mcp — servidor MCP que expõe as capacidades SAP como ferramentas.

É a fronteira do produto: qualquer host (o backend web, o Hermes, a camada de voz)
consome estas ferramentas. Os guardrails (somente-leitura + auditoria) vivem aqui,
no adt_client/safety reaproveitados — então a trava vale para QUALQUER host.

Só ferramentas de LEITURA são expostas. Não há ferramenta de escrita/exclusão.
Roda por stdio (o host sobe este processo): `python -m opuscore.mcp_server`.
"""
from __future__ import annotations

import json

import httpx
from mcp.server.fastmcp import FastMCP

from .safety import build_guard
from .sap.adt_client import ADTError, ADTClient
from .sap.analyzer import build_object_report, report_to_graph
from .settings import get_settings

mcp = FastMCP("opuscore-sap")


def _adt() -> ADTClient:
    s = get_settings()
    name = s.sap.default
    guard = build_guard(name, interactive=False)  # read-only, nega mutações
    return ADTClient(s.sap.systems[name], guard=guard, system_name=name)


@mcp.tool()
async def sap_health() -> str:
    """Testa a conexão ADT com o SAP configurado e informa o modo (somente-leitura)."""
    adt = _adt()
    try:
        await adt.discovery()
        return json.dumps({"ok": True, "system": adt.system_name, "read_only": adt.read_only})
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"ok": False, "error": str(e)})
    finally:
        await adt.aclose()


@mcp.tool()
async def sap_object_report(object_name: str) -> str:
    """Relatório completo de um objeto do repositório SAP: source ou campos DDIC,
    quem usa (where-used) e o grafo de dependências. Somente leitura.

    Args:
        object_name: nome do objeto (ex.: MARA, um programa ou classe).
    """
    adt = _adt()
    try:
        report = await build_object_report(adt, object_name)
        return json.dumps(
            {"report": report.to_dict(), "graph": report_to_graph(report)}, ensure_ascii=False
        )
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        await adt.aclose()


@mcp.tool()
async def sap_search_objects(query: str, max_results: int = 20) -> str:
    """Busca objetos no repositório SAP por nome ou padrão (ex.: 'MAR*')."""
    adt = _adt()
    try:
        refs = await adt.search(query, max_results)
        return json.dumps([r.__dict__ for r in refs], ensure_ascii=False)
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        await adt.aclose()


@mcp.tool()
async def sap_where_used(object_name: str) -> str:
    """Lista os objetos que referenciam o objeto informado (análise de impacto)."""
    adt = _adt()
    try:
        ref = await adt.resolve(object_name)
        used = await adt.where_used(ref)
        return json.dumps([u.__dict__ for u in used], ensure_ascii=False)
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        await adt.aclose()


@mcp.tool()
async def sap_get_source(object_name: str) -> str:
    """Retorna o código-fonte de um objeto (programa, classe, CDS, FM). Vazio p/ tabelas."""
    adt = _adt()
    try:
        ref = await adt.resolve(object_name)
        src = await adt.get_source(ref)
        return json.dumps({"name": ref.name, "type": ref.type, "source": src}, ensure_ascii=False)
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        await adt.aclose()


@mcp.tool()
async def sap_transport_objects(request_id: str) -> str:
    """Lista os objetos contidos numa request/task de transporte do SAP (CTS)."""
    adt = _adt()
    try:
        refs = await adt.transport_objects(request_id)
        return json.dumps([r.__dict__ for r in refs], ensure_ascii=False)
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        await adt.aclose()


@mcp.tool()
async def sap_z_dependencies(object_name: str, max_depth: int = 2) -> str:
    """Descobre os objetos Z/Y que o objeto USA (includes, classes, FMs, tabelas),
    recursivamente. Ignora objetos standard. Base para a lista de remediação."""
    adt = _adt()
    try:
        deps = await adt.z_dependencies(object_name, max_depth=max_depth)
        return json.dumps(deps, ensure_ascii=False)
    except (ADTError, httpx.HTTPError) as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        await adt.aclose()


def main():
    mcp.run()  # transporte stdio por padrão


if __name__ == "__main__":
    main()
