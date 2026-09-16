"""API local do OPUSCORE-AI (FastAPI). Roda na sua máquina; as credenciais SAP
nunca saem daqui."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from pydantic import BaseModel

from .agents import AbapDeveloperAgent
from .safety import build_guard
from .sap.adt_client import ADTClient, ADTError
from .settings import get_settings


def _adt() -> ADTClient:
    s = get_settings()
    name = s.sap.default
    guard = build_guard(name, interactive=False)  # API não prompta: nega por padrão
    return ADTClient(s.sap.systems[name], guard=guard, system_name=name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="OPUSCORE-AI", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ObjectReq(BaseModel):
    object_name: str
    message: str = ""
    llm: str | None = None  # override do provider por requisição


@app.get("/health")
async def health():
    adt = _adt()
    try:
        await adt.discovery()
        return {"ok": True, "sap": get_settings().sap.default, "read_only": adt.read_only}
    except (ADTError, httpx.HTTPError) as e:
        raise HTTPException(502, str(e))
    finally:
        await adt.aclose()


@app.post("/abap/report")
async def abap_report(req: ObjectReq):
    adt = _adt()
    try:
        agent = AbapDeveloperAgent(adt, llm_name=req.llm)
        return await agent.report_on_object(req.object_name, req.message)
    except (ADTError, httpx.HTTPError) as e:
        raise HTTPException(502, str(e))
    finally:
        await adt.aclose()


def main():
    import uvicorn
    s = get_settings()
    uvicorn.run("opuscore.api:app", host=s.app.host, port=s.app.port, reload=True)


# Frontend estático servido em "/" (registrado por último para não sombrear a API)
_FRONTEND = Path(
    os.environ.get("OPUSCORE_FRONTEND", Path(__file__).resolve().parents[2] / "frontend")
)
if _FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND), html=True), name="frontend")


if __name__ == "__main__":
    main()
