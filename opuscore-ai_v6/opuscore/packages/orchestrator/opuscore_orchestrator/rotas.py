"""API do Orquestrador, montada pela Plataforma em /api/plataforma/orquestracao."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class AcaoReq(BaseModel):
    acao: str
    motivo: str = ""


def rotas(obter_orq, obter_usuario=lambda: "local") -> APIRouter:
    r = APIRouter(prefix="/api/plataforma/orquestracao", tags=["orquestração"])

    @r.get("/painel")
    def painel(projeto_id: str):
        return obter_orq().painel(projeto_id)

    @r.get("/handoffs")
    def handoffs(projeto_id: str | None = None, para: str | None = None, estado: str | None = None,
                 gap_id: str | None = None):
        return obter_orq().listar_handoffs(projeto_id=projeto_id, para=para, estado=estado, gap_id=gap_id)

    @r.post("/handoffs/{hid}/acao")
    def acao(hid: str, body: AcaoReq):
        try:
            return obter_orq().transitar(hid, body.acao, motivo=body.motivo, por=obter_usuario())
        except KeyError:
            raise HTTPException(404, "Handoff não encontrado.")
        except ValueError as e:
            raise HTTPException(400, str(e))

    @r.post("/entregas/{eid}/reprocessar")
    def reprocessar(eid: str):
        try:
            obter_orq().reprocessar(eid)
        except KeyError:
            raise HTTPException(404, "Entrega não encontrada.")
        return {"ok": True}

    return r
