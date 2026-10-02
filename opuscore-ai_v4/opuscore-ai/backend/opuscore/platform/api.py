"""API da plataforma (montada sob /api). Alimenta as telas do frontend com dados
reais do SQLite e persiste o chat por consultor.

Leitura + chat (com histórico). CRUD de escrita completo entra no próximo incremento.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import select

from ..host import run_chat
from ..llm import build_provider
from .db import get_session
from .models import (
    AgentProfile,
    AgentProfileVersion,
    Conversation,
    Message,
    Project,
    ProjectAgentAssignment,
    SystemConnection,
    User,
)

router = APIRouter(prefix="/api")


class NewConversation(BaseModel):
    project_id: str
    profile_id: str
    title: str = "Nova conversa"


class ChatIn(BaseModel):
    message: str
    environment_id: str | None = None  # id da SystemConnection escolhida (ou None = docs)
    llm: str | None = None


@router.get("/me")
def me():
    with get_session() as s:
        u = s.exec(select(User).where(User.username == "local")).first() or s.exec(select(User)).first()
        if not u:
            return {"display_name": "Usuário", "role": "—"}
        return {"id": u.id, "username": u.username, "display_name": u.display_name,
                "role": "Administrador" if u.is_admin else "Usuário"}


@router.get("/projects")
def projects():
    with get_session() as s:
        return [
            {"id": p.id, "name": p.name, "client": p.client, "description": p.description,
             "status": p.status}
            for p in s.exec(select(Project).order_by(Project.created_at)).all()
        ]


@router.get("/projects/{pid}")
def project(pid: str):
    with get_session() as s:
        p = s.get(Project, pid)
        if not p:
            raise HTTPException(404, "Projeto não encontrado")
        return {"id": p.id, "name": p.name, "client": p.client, "description": p.description,
                "status": p.status, "language": p.language}


@router.get("/projects/{pid}/consultores")
def consultores(pid: str):
    with get_session() as s:
        rows = s.exec(
            select(ProjectAgentAssignment, AgentProfile)
            .where(ProjectAgentAssignment.project_id == pid)
            .where(ProjectAgentAssignment.profile_id == AgentProfile.id)
        ).all()
        out = []
        for asg, prof in rows:
            out.append({
                "assignment_id": asg.id, "profile_id": prof.id, "key": prof.key,
                "name": prof.name, "role": prof.role, "specialty": prof.specialty,
                "status_label": asg.status_label, "current_work": asg.current_work,
            })
        return out


@router.get("/projects/{pid}/environments")
def environments(pid: str):
    with get_session() as s:
        conns = s.exec(select(SystemConnection).where(SystemConnection.project_id == pid)).all()
        return [
            {"id": c.id, "name": c.name, "product": c.product, "environment": c.environment,
             "status": c.status, "read_only": c.read_only, "live": c.product == "s4_adt"}
            for c in conns
        ]


@router.get("/projects/{pid}/conversations")
def conversations(pid: str, profile_id: str | None = None):
    with get_session() as s:
        q = select(Conversation).where(Conversation.project_id == pid)
        if profile_id:
            q = q.where(Conversation.profile_id == profile_id)
        convs = s.exec(q.order_by(Conversation.updated_at.desc())).all()
        return [{"id": c.id, "profile_id": c.profile_id, "title": c.title,
                 "updated_at": c.updated_at.isoformat()} for c in convs]


@router.post("/conversations")
def create_conversation(body: NewConversation):
    with get_session() as s:
        u = s.exec(select(User).where(User.username == "local")).first() or s.exec(select(User)).first()
        conv = Conversation(project_id=body.project_id, profile_id=body.profile_id,
                            user_id=u.id if u else "", title=body.title)
        s.add(conv); s.commit(); s.refresh(conv)
        return {"id": conv.id, "profile_id": conv.profile_id, "title": conv.title}


@router.get("/conversations/{cid}/messages")
def messages(cid: str):
    with get_session() as s:
        msgs = s.exec(select(Message).where(Message.conversation_id == cid)
                      .order_by(Message.created_at)).all()
        return [{"role": m.role, "content": m.content, "evidence": m.evidence,
                 "created_at": m.created_at.isoformat()} for m in msgs]


@router.post("/conversations/{cid}/chat")
async def chat(cid: str, body: ChatIn, request: Request):
    mcp = getattr(request.app.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, "MCP indisponível — inicie o backend com o servidor SAP MCP.")

    # 1) lê histórico + persona (sessão fecha antes do await)
    with get_session() as s:
        conv = s.get(Conversation, cid)
        if not conv:
            raise HTTPException(404, "Conversa não encontrada")
        prof = s.get(AgentProfile, conv.profile_id)
        pv = s.exec(select(AgentProfileVersion)
                    .where(AgentProfileVersion.profile_id == conv.profile_id)
                    .order_by(AgentProfileVersion.version.desc())).first()
        history = s.exec(select(Message).where(Message.conversation_id == cid)
                         .order_by(Message.created_at)).all()
        persona = (pv.instructions if pv else "") or ""
        prof_name = prof.name if prof else "Consultor"
        prof_id = conv.profile_id
        project_id = conv.project_id

    msgs: list[dict] = []
    if persona:
        msgs.append({"role": "system", "content": f"Você é o {prof_name}. {persona}"})
    for m in history:
        if m.role in ("user", "assistant"):
            msgs.append({"role": m.role, "content": m.content})
    msgs.append({"role": "user", "content": body.message})

    # 2) roda o laço do agente (LLM + ferramentas MCP)
    import httpx
    try:
        provider = build_provider(body.llm)
        result = await run_chat(msgs, mcp, provider)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")

    # 3) persiste usuário + assistente (com rastro de evidência)
    with get_session() as s:
        s.add(Message(conversation_id=cid, role="user", content=body.message,
                      evidence={"environment_id": body.environment_id}))
        s.add(Message(conversation_id=cid, role="assistant", content=result.reply,
                      evidence={"steps": result.steps}))
        conv = s.get(Conversation, cid)
        if conv and conv.title == "Nova conversa" and body.message:
            conv.title = body.message[:48]
        s.commit()

    return {"reply": result.reply, "steps": result.steps,
            "profile_id": prof_id, "project_id": project_id}
