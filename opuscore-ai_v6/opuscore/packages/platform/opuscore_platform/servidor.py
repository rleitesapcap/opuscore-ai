"""Servidor completo: todos os consultores instalados (ou os de OPUSCORE_PLUGINS)."""
from __future__ import annotations

import argparse


def main() -> None:
    import uvicorn
    from opuscore_core.sdk.config import config_app
    ap = argparse.ArgumentParser(description="OPUSCORE-AI — servidor")
    ap.add_argument("--host", default=None)
    ap.add_argument("--porta", type=int, default=None)
    a = ap.parse_args()
    cfg = config_app()
    uvicorn.run("opuscore_platform.gateway:app_padrao", factory=True, host=a.host or cfg.host, port=a.porta or cfg.port)


if __name__ == "__main__":
    main()
