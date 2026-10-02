"""API local do OPUSCORE-AI — agora HOST: LLM + cliente MCP.

Sobe o opuscore-sap-mcp no startup (stdio), serve o frontend, e expõe:
- /health        -> status via ferramenta MCP sap_health
- /abap/report   -> relatório de objeto (evidência via MCP + narração pelo LLM)
- /chat          -> conversa livre com laço de agente (LLM <-> ferramentas MCP)
"""
from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .host import narrate_object_report, run_chat
from .llm import build_provider
from .mcp_client import MCPClient
from .platform.api import router as platform_router
from .platform.db import init_db
from .settings import get_settings

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_CONFIG_PATH = Path(os.environ.get("OPUSCORE_CONFIG", _BACKEND_DIR / "config.yaml"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:  # auto-seed do projeto-demo na primeira execução
        from sqlmodel import select

        from .platform.db import get_session
        from .platform.models import Project
        from .platform.seed import seed as seed_demo
        with get_session() as s:
            empty = s.exec(select(Project)).first() is None
        if empty:
            seed_demo()
    except Exception:
        pass
    env = os.environ.copy()
    env["OPUSCORE_CONFIG"] = str(_CONFIG_PATH)
    client = MCPClient(cwd=str(_BACKEND_DIR), env=env)
    try:
        await client.start()
        app.state.mcp = client
        app.state.mcp_error = None
    except Exception as e:  # noqa: BLE001 - startup best-effort
        app.state.mcp = None
        app.state.mcp_error = str(e)
    yield
    if getattr(app.state, "mcp", None):
        await client.stop()


app = FastAPI(title="OPUSCORE-AI", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(platform_router)


class ObjectReq(BaseModel):
    object_name: str
    message: str = ""
    llm: str | None = None


class ChatReq(BaseModel):
    messages: list[dict]  # [{"role": "user"|"assistant", "content": str}, ...]
    llm: str | None = None


def _mcp(app_: FastAPI) -> MCPClient:
    mcp = getattr(app_.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, f"MCP indisponível: {getattr(app_.state, 'mcp_error', 'não iniciado')}")
    return mcp


@app.get("/health")
async def health():
    mcp = _mcp(app)
    raw = await mcp.call_tool("sap_health")
    data = json.loads(raw)
    if not data.get("ok"):
        raise HTTPException(502, data.get("error", "SAP não conectado"))
    return {"ok": True, "sap": data.get("system"), "read_only": data.get("read_only", True)}


@app.post("/abap/report")
async def abap_report(req: ObjectReq):
    mcp = _mcp(app)
    raw = await mcp.call_tool("sap_object_report", {"object_name": req.object_name})
    data = json.loads(raw)
    if data.get("error"):
        raise HTTPException(502, data["error"])
    try:
        provider = build_provider(req.llm)
        narrative = await narrate_object_report(provider, req.object_name, data["report"], req.message)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")
    return {"narrative": narrative, "report": data["report"], "graph": data["graph"]}


@app.post("/chat")
async def chat(req: ChatReq):
    mcp = _mcp(app)
    try:
        provider = build_provider(req.llm)
        result = await run_chat(req.messages, mcp, provider)
        return {"reply": result.reply, "steps": result.steps}
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")


def main():
    import uvicorn
    s = get_settings()
    uvicorn.run("opuscore.api:app", host=s.app.host, port=s.app.port, reload=False)


_FRONTEND = Path(os.environ.get("OPUSCORE_FRONTEND", _BACKEND_DIR.parent / "frontend"))
if _FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")


if __name__ == "__main__":
    main()
