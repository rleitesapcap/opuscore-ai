"""Servidor de desenvolvimento com SÓ os consultores escolhidos.

    python -m opuscore_platform.dev --plugins funcional-mm --porta 8801
    python -m opuscore_platform.dev --plugins dev-abap,orquestrador --porta 8802 --sem-mcp
"""
from __future__ import annotations

import argparse
import os


def main() -> None:
    import uvicorn
    ap = argparse.ArgumentParser(description="OPUSCORE-AI — servidor de desenvolvimento")
    ap.add_argument("--plugins", required=True, help="keys separadas por vírgula (ex.: funcional-mm)")
    ap.add_argument("--porta", type=int, default=8801)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--sem-mcp", action="store_true", help="não sobe o servidor MCP (sem SAP)")
    ap.add_argument("--reload", action="store_true")
    a = ap.parse_args()
    os.environ["OPUSCORE_PLUGINS"] = a.plugins
    if a.sem_mcp:
        os.environ["OPUSCORE_SEM_MCP"] = "1"
    uvicorn.run("opuscore_platform.dev:app_dev", factory=True, host=a.host, port=a.porta, reload=a.reload)


def app_dev():
    from .gateway import create_app
    return create_app(iniciar_mcp=not os.environ.get("OPUSCORE_SEM_MCP"))


if __name__ == "__main__":
    main()
