"""Servidor MCP dos Conectores (stdio). É a fronteira do produto: qualquer host
(Plataforma, outro agente, inspetor MCP) consome estas ferramentas, e as travas
(somente leitura, políticas de dados, auditoria) valem para todos.

Conectores ativos: OPUSCORE_CONECTORES=sap_adt,cpi (padrão: conectores.habilitados do
config.yaml, ou só sap_adt).
"""
from __future__ import annotations

import importlib
import os

from mcp.server.fastmcp import FastMCP

CONECTORES = {"sap_adt": "opuscore_connectors.sap_adt.ferramentas"}


def ativos() -> list[str]:
    env = os.environ.get("OPUSCORE_CONECTORES", "").strip()
    if env:
        return [x.strip() for x in env.split(",") if x.strip()]
    try:
        from .config import config_conectores
        return config_conectores().habilitados
    except Exception:  # noqa: BLE001 - sem config: só o SAP
        return ["sap_adt"]


def criar_servidor() -> FastMCP:
    mcp = FastMCP("opuscore-conectores")
    for nome in ativos():
        if nome not in CONECTORES:
            raise SystemExit(f"Conector desconhecido: {nome}. Conhecidos: {', '.join(CONECTORES)}")
        importlib.import_module(CONECTORES[nome]).registrar(mcp)
    return mcp


def main():
    criar_servidor().run()   # transporte stdio


if __name__ == "__main__":
    main()
