"""Gateway: o único processo web. Monta banco e migrações, seed, perfis, MCP,
Orquestrador, rotas e telas de cada consultor, e o shell."""
from __future__ import annotations

import json
import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from opuscore_core.contratos.erros import ErroOpus
from opuscore_core.sdk.config import caminho_config, raiz
from opuscore_core.versao import __version__ as versao_core

from . import registry
from .contexto import dependencia_ctx, fabrica_contexto
from .db.engine import get_engine, get_session, init_db
from .db.migracoes import MIGRACOES_PLATAFORMA, aplicar
from .seed import seed_demo, sincronizar_perfis

log = logging.getLogger("opuscore.gateway")


def create_app(filtro: set[str] | None = None, extras: list | None = None, *, iniciar_mcp: bool = True,
               orquestrador_ativo: bool = True) -> FastAPI:
    reg = registry.carregar(filtro if filtro is not None else registry.filtro_ambiente(), extras)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        from opuscore_orchestrator import Orquestrador
        init_db()
        migs = list(MIGRACOES_PLATAFORMA)
        for p in reg.plugins:
            migs += [(f"{p.manifesto.key}:{mid}", fn) for mid, fn in p.migracoes()]
        aplicar(get_engine(), migs)
        seed_demo()
        sincronizar_perfis(reg.plugins)
        app.state.mcp, app.state.mcp_error = None, None
        cliente = None
        if iniciar_mcp:
            from opuscore_core.sdk.mcp import MCPClient
            env = os.environ.copy()
            env.setdefault("OPUSCORE_CONFIG", str(caminho_config()))
            env.setdefault("OPUSCORE_HOME", str(raiz()))
            cliente = MCPClient(cwd=str(raiz()), env=env)
            try:
                await cliente.start()
                app.state.mcp = cliente
            except Exception as e:  # noqa: BLE001 - a API sobe; o erro aparece no /health
                app.state.mcp_error = str(e)
                log.error("Servidor MCP dos Conectores não subiu: %s", e)
        orq = Orquestrador(get_session, fabrica_contexto(app))
        orq.assinar_plugins(reg.plugins)
        app.state.orquestrador = orq
        if orquestrador_ativo:
            orq.iniciar()
        yield
        await orq.parar()
        if cliente is not None and app.state.mcp is cliente:
            await cliente.stop()

    app = FastAPI(title="OPUSCORE-AI", version=versao_core, lifespan=lifespan)
    app.state.registro = reg

    @app.middleware("http")
    async def _requisicao(request: Request, call_next):
        request.state.request_id = uuid.uuid4().hex[:12]
        resp = await call_next(request)
        resp.headers["X-Request-Id"] = request.state.request_id
        if not request.url.path.startswith(("/api", "/health")):
            resp.headers["Cache-Control"] = "no-cache"   # tela sempre revalidada (304 se não mudou)
        return resp

    @app.exception_handler(ErroOpus)
    async def _erro_opus(request: Request, e: ErroOpus):
        rid = getattr(request.state, "request_id", "")
        return JSONResponse(status_code=e.status,
                            content={"detail": e.mensagem, "erro": e.mensagem, "codigo": e.codigo, "request_id": rid})

    from opuscore_orchestrator.rotas import rotas as rotas_orq

    from .servicos import artefatos, cadastros, uploads
    for r in (cadastros.router, uploads.router, artefatos.router):
        app.include_router(r)
    app.include_router(rotas_orq(lambda: app.state.orquestrador))

    @app.get("/health")
    async def health():
        mcp = app.state.mcp
        if mcp is None:
            raise HTTPException(503, f"MCP indisponível: {app.state.mcp_error or 'não iniciado'}")
        data = json.loads(await mcp.call_tool("sap_health", {}))
        if not data.get("ok"):
            raise HTTPException(502, data.get("error", "SAP não conectado"))
        return {"ok": True, "sap": data.get("system"), "read_only": data.get("read_only", True)}

    @app.get("/api/plataforma/plugins")
    def plugins():
        return reg.situacao()

    for p in list(reg.plugins):
        key = p.manifesto.key
        try:
            r = p.rotas(dependencia_ctx(key))
            if r is not None:
                app.include_router(r, prefix=f"/api/c/{key}", tags=[key])
            wd = p.web_dir
            if wd and wd.is_dir():
                app.mount(f"/c/{key}", StaticFiles(directory=str(wd)), name=f"web-{key}")
        except Exception as e:  # noqa: BLE001 - isola o plugin
            reg.plugins.remove(p)
            reg.erros.append({"key": key, "erro": f"falha ao montar rotas/tela: {type(e).__name__}: {e}"})
            log.error("Plugin %s não montou: %s", key, e)

    from opuscore_web import STATIC_DIR
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="shell")
    return app


def app_padrao() -> FastAPI:
    """Fábrica usada pelo uvicorn (--factory)."""
    return create_app()
