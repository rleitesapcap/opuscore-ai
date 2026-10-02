"""Cadastros da Plataforma (/api/plataforma): usuário, projetos, membros, ambientes,
agentes (perfis, versões, skills), consultores do projeto e conversas com chat.
Nenhuma regra de consultor aqui: as rotas deles ficam nos pacotes deles (/api/c/<key>)."""
from __future__ import annotations

import json
import re

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlmodel import select

from opuscore_core.sdk.chat import run_chat
from opuscore_core.sdk.ia import build_provider

from ..db.engine import get_session
from ..db.modelos import (
    AgentProfile,
    AgentProfileVersion,
    AgentSkill,
    Artifact,
    Conversation,
    KnowledgeCollection,
    Membership,
    Message,
    OwnerType,
    Project,
    ProjectAgentAssignment,
    ProjectContext,
    SapProduct,
    SystemConnection,
    User,
    Visibility,
)

router = APIRouter(prefix="/api/plataforma", tags=["cadastros"])


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


def _tela(request: Request, key: str) -> dict:
    """Dados da tela do consultor, vindos do manifesto do plugin instalado."""
    reg = getattr(request.app.state, "registro", None)
    p = reg.por_key.get(key) if reg else None
    if not p or not p.manifesto.web:
        return {"tela": None, "instalado": bool(p)}
    w = p.manifesto.web
    v = p.manifesto.versao
    return {"tela": w.rota, "instalado": True, "web": {
        "entrada": f"/c/{key}/{w.entrada}?v={v}", "css": f"/c/{key}/{w.css}?v={v}" if w.css else None,
        "contrato_web": p.manifesto.contrato_web}}


@router.get("/projects/{pid}/consultores")
def consultores(pid: str, request: Request):
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
                **_tela(request, prof.key),
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

    from opuscore_core.sdk.uso import resumo as _resumo_uso
    uso = _resumo_uso(result.usos, getattr(getattr(provider, "cfg", None), "model", None))

    # 3) persiste usuário + assistente (com rastro de evidência e uso de IA)
    with get_session() as s:
        s.add(Message(conversation_id=cid, role="user", content=body.message,
                      evidence={"environment_id": body.environment_id}))
        s.add(Message(conversation_id=cid, role="assistant", content=result.reply,
                      evidence={"steps": result.steps, "uso_ia": uso}))
        conv = s.get(Conversation, cid)
        if conv and conv.title == "Nova conversa" and body.message:
            conv.title = body.message[:48]
        s.commit()

    return {"reply": result.reply, "steps": result.steps, "uso_ia": uso,
            "profile_id": prof_id, "project_id": project_id}


# ===========================================================================
# CRUD de administração (Fase 1): usuários+permissões, projetos+RAGs, agentes
# ===========================================================================
from sqlalchemy import func  # noqa: E402


def _max_version(sess, profile_id: str) -> int:
    v = sess.exec(
        select(func.max(AgentProfileVersion.version)).where(
            AgentProfileVersion.profile_id == profile_id
        )
    ).one()
    return (v or 0)


# ---- Usuários e permissões -------------------------------------------------
class UserIn(BaseModel):
    username: str
    display_name: str = ""
    is_admin: bool = False


class MemberIn(BaseModel):
    user_id: str
    role: str = "viewer"          # owner | editor | viewer
    scopes: dict = {}             # teto de autorização do usuário no projeto


@router.get("/users")
def list_users():
    with get_session() as s:
        return [{"id": u.id, "username": u.username, "display_name": u.display_name,
                 "is_admin": u.is_admin} for u in s.exec(select(User)).all()]


@router.post("/users")
def create_user(body: UserIn):
    with get_session() as s:
        if s.exec(select(User).where(User.username == body.username)).first():
            raise HTTPException(409, "username já existe")
        u = User(username=body.username, display_name=body.display_name or body.username,
                 is_admin=body.is_admin)
        s.add(u); s.commit(); s.refresh(u)
        return {"id": u.id, "username": u.username, "display_name": u.display_name,
                "is_admin": u.is_admin}


@router.get("/projects/{pid}/members")
def list_members(pid: str):
    with get_session() as s:
        rows = s.exec(
            select(Membership, User).where(Membership.project_id == pid)
            .where(Membership.user_id == User.id)
        ).all()
        return [{"id": m.id, "user_id": u.id, "username": u.username,
                 "display_name": u.display_name, "role": m.role, "scopes": m.scopes}
                for m, u in rows]


@router.post("/projects/{pid}/members")
def add_member(pid: str, body: MemberIn):
    with get_session() as s:
        exists = s.exec(select(Membership).where(Membership.project_id == pid)
                        .where(Membership.user_id == body.user_id)).first()
        if exists:
            exists.role = body.role; exists.scopes = body.scopes
            s.add(exists); s.commit(); return {"id": exists.id, "role": exists.role}
        m = Membership(project_id=pid, user_id=body.user_id, role=body.role, scopes=body.scopes)
        s.add(m); s.commit(); s.refresh(m)
        return {"id": m.id, "role": m.role}


# ---- Projetos --------------------------------------------------------------
class ProjectIn(BaseModel):
    name: str
    client: str = ""
    description: str = ""
    language: str = "pt-BR"


class ProjectPatch(BaseModel):
    name: str | None = None
    client: str | None = None
    description: str | None = None
    language: str | None = None
    status: str | None = None


class ContextIn(BaseModel):
    content: dict


class CollectionIn(BaseModel):
    name: str
    visibility: str = Visibility.PROJECT_SHARED


class AssignIn(BaseModel):
    profile_id: str
    status_label: str = "Ativo"
    current_work: str = ""


class ConnIn(BaseModel):
    product: str = SapProduct.S4_ADT
    environment: str = "DEV"
    name: str
    purpose: str = ""
    base_url: str = ""
    sap_client: str = ""
    auth: str = "basic"


@router.post("/projects")
def create_project(body: ProjectIn):
    with get_session() as s:
        p = Project(name=body.name, client=body.client, description=body.description,
                    language=body.language)
        s.add(p); s.commit(); s.refresh(p)
        # RAG global do projeto já nasce com ele
        s.add(KnowledgeCollection(project_id=p.id, owner_type=OwnerType.PROJECT, owner_id=p.id,
                                  visibility=Visibility.PROJECT_SHARED, name="RAG Global do Projeto"))
        s.commit()
        return {"id": p.id, "name": p.name}


@router.patch("/projects/{pid}")
def patch_project(pid: str, body: ProjectPatch):
    with get_session() as s:
        p = s.get(Project, pid)
        if not p:
            raise HTTPException(404, "Projeto não encontrado")
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(p, k, v)
        s.add(p); s.commit()
        return {"id": p.id, "name": p.name}


@router.get("/projects/{pid}/context")
def get_context(pid: str):
    with get_session() as s:
        ctx = s.exec(select(ProjectContext).where(ProjectContext.project_id == pid)
                     .order_by(ProjectContext.version.desc())).first()
        return {"version": ctx.version, "content": ctx.content} if ctx else {"version": 0, "content": {}}


@router.put("/projects/{pid}/context")
def put_context(pid: str, body: ContextIn):
    with get_session() as s:
        last = s.exec(select(func.max(ProjectContext.version))
                      .where(ProjectContext.project_id == pid)).one() or 0
        ctx = ProjectContext(project_id=pid, version=last + 1, content=body.content)
        s.add(ctx); s.commit()
        return {"version": ctx.version}


@router.get("/projects/{pid}/collections")
def list_project_collections(pid: str):
    with get_session() as s:
        cols = s.exec(select(KnowledgeCollection).where(KnowledgeCollection.project_id == pid)).all()
        return [{"id": c.id, "name": c.name, "visibility": c.visibility,
                 "owner_type": c.owner_type} for c in cols]


@router.post("/projects/{pid}/collections")
def add_project_collection(pid: str, body: CollectionIn):
    with get_session() as s:
        c = KnowledgeCollection(project_id=pid, owner_type=OwnerType.PROJECT, owner_id=pid,
                                visibility=body.visibility, name=body.name)
        s.add(c); s.commit(); s.refresh(c)
        return {"id": c.id, "name": c.name}


@router.post("/projects/{pid}/agents")
def assign_agent(pid: str, body: AssignIn):
    with get_session() as s:
        if s.exec(select(ProjectAgentAssignment).where(ProjectAgentAssignment.project_id == pid)
                  .where(ProjectAgentAssignment.profile_id == body.profile_id)).first():
            raise HTTPException(409, "Agente já associado ao projeto")
        prof = s.get(AgentProfile, body.profile_id)
        if not prof:
            raise HTTPException(404, "Perfil não encontrado")
        a = ProjectAgentAssignment(project_id=pid, profile_id=body.profile_id,
                                   profile_version=prof.current_version,
                                   status_label=body.status_label, current_work=body.current_work)
        s.add(a); s.commit(); s.refresh(a)
        return {"id": a.id}


@router.delete("/projects/{pid}/agents/{assignment_id}")
def unassign_agent(pid: str, assignment_id: str):
    with get_session() as s:
        a = s.get(ProjectAgentAssignment, assignment_id)
        if a:
            s.delete(a); s.commit()
        return {"ok": True}


@router.post("/projects/{pid}/connections")
def add_connection(pid: str, body: ConnIn):
    with get_session() as s:
        c = SystemConnection(project_id=pid, product=body.product, environment=body.environment,
                             name=body.name, purpose=body.purpose, base_url=body.base_url,
                             sap_client=body.sap_client, auth=body.auth,
                             allowed_operations=["read"], read_only=True)
        s.add(c); s.commit(); s.refresh(c)
        return {"id": c.id, "name": c.name}


# ---- Agentes (catálogo) — perfil = prompt versionado -----------------------
class AgentIn(BaseModel):
    key: str
    name: str
    role: str = ""
    specialty: str = ""
    modules: list = []
    persona: str = ""
    instructions: str = ""       # o "prompt" do agente
    output_format: str = ""


class AgentPatch(BaseModel):
    name: str | None = None
    role: str | None = None
    specialty: str | None = None
    modules: list | None = None
    status: str | None = None


class PromptIn(BaseModel):
    persona: str = ""
    instructions: str = ""
    output_format: str = ""
    policies: dict = {}


class SkillIn(BaseModel):
    name: str
    description: str = ""
    category: str = ""
    allowed_tools: list = []
    allowed_sources: list = []
    steps: str = ""
    acceptance: str = ""


class AgentCollIn(BaseModel):
    name: str


@router.get("/agents")
def list_agents():
    with get_session() as s:
        return [{"id": p.id, "key": p.key, "name": p.name, "role": p.role,
                 "specialty": p.specialty, "status": p.status,
                 "current_version": p.current_version}
                for p in s.exec(select(AgentProfile).order_by(AgentProfile.name)).all()]


@router.get("/agents/{aid}")
def get_agent(aid: str):
    with get_session() as s:
        p = s.get(AgentProfile, aid)
        if not p:
            raise HTTPException(404, "Agente não encontrado")
        pv = s.exec(select(AgentProfileVersion).where(AgentProfileVersion.profile_id == aid)
                    .order_by(AgentProfileVersion.version.desc())).first()
        skills = s.exec(select(AgentSkill).where(AgentSkill.profile_id == aid)).all()
        cols = s.exec(select(KnowledgeCollection).where(KnowledgeCollection.owner_type == OwnerType.AGENT_PROFILE)
                      .where(KnowledgeCollection.owner_id == aid)).all()
        return {
            "id": p.id, "key": p.key, "name": p.name, "role": p.role, "specialty": p.specialty,
            "modules": p.modules, "status": p.status, "current_version": p.current_version,
            "prompt": {"version": pv.version if pv else 0,
                       "persona": pv.persona if pv else "",
                       "instructions": pv.instructions if pv else "",
                       "output_format": pv.output_format if pv else ""},
            "skills": [{"id": k.id, "name": k.name, "category": k.category,
                        "description": k.description, "allowed_tools": k.allowed_tools,
                        "steps": k.steps} for k in skills],
            "collections": [{"id": c.id, "name": c.name, "visibility": c.visibility} for c in cols],
        }


@router.post("/agents")
def create_agent(body: AgentIn):
    with get_session() as s:
        if s.exec(select(AgentProfile).where(AgentProfile.key == body.key)).first():
            raise HTTPException(409, "key de agente já existe")
        p = AgentProfile(key=body.key, name=body.name, role=body.role, specialty=body.specialty,
                         modules=body.modules, status="active", current_version=1,
                         description=(body.persona or body.name)[:180])
        s.add(p); s.commit(); s.refresh(p)
        s.add(AgentProfileVersion(profile_id=p.id, version=1, persona=body.persona,
                                  instructions=body.instructions, output_format=body.output_format))
        # RAG privado do perfil já nasce com o agente
        s.add(KnowledgeCollection(owner_type=OwnerType.AGENT_PROFILE, owner_id=p.id,
                                  visibility=Visibility.AGENT_PROFILE_PRIVATE,
                                  name=f"RAG {body.name}"))
        s.commit()
        return {"id": p.id, "key": p.key}


@router.patch("/agents/{aid}")
def patch_agent(aid: str, body: AgentPatch):
    with get_session() as s:
        p = s.get(AgentProfile, aid)
        if not p:
            raise HTTPException(404, "Agente não encontrado")
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(p, k, v)
        s.add(p); s.commit()
        return {"id": p.id}


@router.post("/agents/{aid}/version")
def new_prompt_version(aid: str, body: PromptIn):
    with get_session() as s:
        p = s.get(AgentProfile, aid)
        if not p:
            raise HTTPException(404, "Agente não encontrado")
        ver = _max_version(s, aid) + 1
        s.add(AgentProfileVersion(profile_id=aid, version=ver, persona=body.persona,
                                  instructions=body.instructions, output_format=body.output_format,
                                  policies=body.policies))
        p.current_version = ver
        s.add(p); s.commit()
        return {"version": ver}


@router.get("/agents/{aid}/skills")
def list_skills(aid: str):
    with get_session() as s:
        ks = s.exec(select(AgentSkill).where(AgentSkill.profile_id == aid)).all()
        return [{"id": k.id, "name": k.name, "category": k.category, "description": k.description,
                 "allowed_tools": k.allowed_tools, "steps": k.steps} for k in ks]


@router.post("/agents/{aid}/skills")
def add_skill(aid: str, body: SkillIn):
    with get_session() as s:
        if not s.get(AgentProfile, aid):
            raise HTTPException(404, "Agente não encontrado")
        k = AgentSkill(profile_id=aid, name=body.name, description=body.description,
                       category=body.category, allowed_tools=body.allowed_tools,
                       allowed_sources=body.allowed_sources, steps=body.steps,
                       acceptance=body.acceptance)
        s.add(k); s.commit(); s.refresh(k)
        return {"id": k.id, "name": k.name}


@router.delete("/skills/{sid}")
def delete_skill(sid: str):
    with get_session() as s:
        k = s.get(AgentSkill, sid)
        if k:
            s.delete(k); s.commit()
        return {"ok": True}


@router.get("/agents/{aid}/collections")
def list_agent_collections(aid: str):
    with get_session() as s:
        cols = s.exec(select(KnowledgeCollection)
                      .where(KnowledgeCollection.owner_type == OwnerType.AGENT_PROFILE)
                      .where(KnowledgeCollection.owner_id == aid)).all()
        return [{"id": c.id, "name": c.name, "visibility": c.visibility} for c in cols]


@router.post("/agents/{aid}/collections")
def add_agent_collection(aid: str, body: AgentCollIn):
    with get_session() as s:
        c = KnowledgeCollection(owner_type=OwnerType.AGENT_PROFILE, owner_id=aid,
                                visibility=Visibility.AGENT_PROFILE_PRIVATE, name=body.name)
        s.add(c); s.commit(); s.refresh(c)
        return {"id": c.id, "name": c.name}
