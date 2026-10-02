"""API da plataforma (montada sob /api). Alimenta as telas do frontend com dados
reais do SQLite e persiste o chat por consultor.

Leitura + chat (com histórico). CRUD de escrita completo entra no próximo incremento.
"""
from __future__ import annotations

import json
import re

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlmodel import select

from ..host import run_chat
from ..llm import build_provider
from .db import get_session
from .models import (
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


# consultores com tela própria (rota do frontend) -> botão "Abrir" na lista
TELAS_CONSULTOR = {"dev-abap": "dev", "funcional-mm": "mm"}


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
                "tela": TELAS_CONSULTOR.get(prof.key),
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

    from ..usage import resumo as _resumo_uso
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


# ===========================================================================
# Capacidades do Desenvolvedor (entregáveis) + artefatos
# ===========================================================================
import httpx  # noqa: E402

from ..developer import (  # noqa: E402
    gen_object_report,
    gen_rap_skeleton,
    gen_remediation,
    gen_tech_spec,
)


class ObjReq(BaseModel):
    project_id: str
    object_name: str
    llm: str | None = None


class EFReq(BaseModel):
    project_id: str
    ef_text: str
    title: str = ""
    llm: str | None = None


def _save_artifact(project_id, kind, title, content, fmt="markdown"):
    with get_session() as s:
        a = Artifact(project_id=project_id, kind=kind, title=title, format=fmt,
                     content=content, produced_by="dev-abap")
        s.add(a); s.commit(); s.refresh(a)
        return a.id


_TOKEN_TECNICO = re.compile(r"\b[A-Za-z][A-Za-z0-9_/]*[_/0-9][A-Za-z0-9_/]*\b|\b[A-Z]{3,}\b")


def nome_do_objeto(texto: str) -> str:
    """Extrai o nome técnico quando o usuário digita uma frase
    ('Faça a análise do objeto ZSDR_X' -> 'ZSDR_X'). Levanta 400 se não achar
    nenhum ou se houver mais de um candidato."""
    t = (texto or "").strip()
    if t and not re.search(r"\s", t):
        return t.upper()
    zy = re.findall(r"\b[ZzYy][A-Za-z0-9_/]{3,}\b", t)
    cand = zy or [x for x in _TOKEN_TECNICO.findall(t) if x.upper() == x or "_" in x]
    cand = list(dict.fromkeys(c.upper() for c in cand))
    if len(cand) == 1:
        return cand[0]
    if not cand:
        raise HTTPException(400, "Não achei um nome de objeto no texto. Digite só o nome técnico "
                                 "(ex.: MARA, ZCL_ALGO). Para pedidos em frase, use a aba Conversas.")
    raise HTTPException(400, f"Achei mais de um objeto no texto ({', '.join(cand)}). "
                             "Digite só o nome do objeto que você quer analisar.")


async def _report_via_mcp(request: Request, object_name: str) -> dict:
    mcp = getattr(request.app.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, "MCP indisponível — inicie o backend com o servidor SAP MCP.")
    nome = nome_do_objeto(object_name)
    raw = await mcp.call_tool("sap_object_report", {"object_name": nome})
    data = json.loads(raw)
    if data.get("error"):
        erro = data["error"]
        if "não encontrado" in erro.lower() or "not found" in erro.lower():
            raise HTTPException(404, f"O objeto {nome} não foi encontrado no SAP conectado. Confira o nome "
                                     "e se ele existe nesse sistema (o trial local só tem objetos standard "
                                     "e o que foi criado nele).")
        raise HTTPException(502, erro)
    return data


@router.post("/dev/object-report")
async def dev_object_report(body: ObjReq, request: Request):
    data = await _report_via_mcp(request, body.object_name)
    try:
        narrative = await gen_object_report(build_provider(body.llm), body.object_name, data["report"])
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")
    aid = _save_artifact(body.project_id, "object_report",
                         f"Relatório — {body.object_name}", narrative)
    return {"narrative": narrative, "report": data["report"], "graph": data["graph"], "artifact_id": aid}


@router.post("/dev/remediation")
async def dev_remediation(body: ObjReq, request: Request):
    data = await _report_via_mcp(request, body.object_name)
    try:
        content = await gen_remediation(build_provider(body.llm), body.object_name, data["report"])
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")
    aid = _save_artifact(body.project_id, "remediation",
                         f"Remediação — {body.object_name}", content)
    return {"content": content, "report": data["report"], "artifact_id": aid}


@router.post("/dev/tech-spec")
async def dev_tech_spec(body: EFReq):
    try:
        content = await gen_tech_spec(build_provider(body.llm), body.ef_text)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")
    aid = _save_artifact(body.project_id, "technical_spec", body.title or "Especificação Técnica", content)
    return {"content": content, "artifact_id": aid}


@router.post("/dev/rap")
async def dev_rap(body: EFReq):
    try:
        content = await gen_rap_skeleton(build_provider(body.llm), body.ef_text)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Falha no LLM: {e}")
    aid = _save_artifact(body.project_id, "rap_code", body.title or "Esqueleto RAP", content, fmt="abap")
    return {"content": content, "artifact_id": aid}


@router.get("/projects/{pid}/artifacts")
def list_artifacts(pid: str):
    with get_session() as s:
        arts = s.exec(select(Artifact).where(Artifact.project_id == pid)
                      .order_by(Artifact.created_at.desc())).all()
        return [{"id": a.id, "kind": a.kind, "title": a.title, "format": a.format,
                 "status": a.status, "created_at": a.created_at.isoformat()} for a in arts]


@router.get("/artifacts/{aid}")
def get_artifact(aid: str):
    with get_session() as s:
        a = s.get(Artifact, aid)
        if not a:
            raise HTTPException(404, "Artefato não encontrado")
        return {"id": a.id, "kind": a.kind, "title": a.title, "format": a.format,
                "content": a.content, "status": a.status, "created_at": a.created_at.isoformat()}


# ===========================================================================
# Fluxos SAP-sourced do Desenvolvedor (origem = S/4 via ADT, não diretório)
# ===========================================================================
import shutil  # noqa: E402
from pathlib import Path as _Path  # noqa: E402

from ..dev import discovery  # noqa: E402


class RemPlanReq(BaseModel):
    project_id: str
    ef_id: str | None = None          # EF enviada por /api/dev/ef/upload (.docx/.pdf validado)
    ef_text: str | None = None        # alternativa: texto colado (uso via API)
    max_depth: int = 2


class RemRunReq(BaseModel):
    project_id: str
    objects: list[str]          # lista aprovada pelo usuário (pode ter removido itens)


class ETPlanReq(BaseModel):
    project_id: str
    ef_id: str                  # OBRIGATÓRIA: EF enviada por upload (.docx/.pdf validado)
    request_id: str | None = None
    objects: list[str] | None = None


class ETRunReq(ETPlanReq):
    pass


async def _tool_json(mcp, name: str, args: dict):
    raw = await mcp.call_tool(name, args)
    data = json.loads(raw)
    if isinstance(data, dict) and data.get("error"):
        erro = data["error"]
        # "não encontrado(a)" é erro de uso (nome/request errado), não falha do servidor
        raise HTTPException(404 if "não encontrad" in erro.lower() else 502, erro)
    return data


_ARTIFACTS_DIR = _Path(__file__).resolve().parents[2] / "data" / "artifacts"
_RUN_ID = re.compile(r"^(et|remediation|efval|efdraft)-\d{8}-\d{6}(-[0-9a-f]{6})?$")
_BAIXAVEIS = {".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              ".md": "text/markdown; charset=utf-8", ".abap": "text/plain; charset=utf-8",
              ".txt": "text/plain; charset=utf-8", ".pdf": "application/pdf"}


def _downloads(pasta) -> list[dict]:
    """Arquivos baixáveis de uma execução, com a URL de download (Word primeiro)."""
    from urllib.parse import quote as _q
    pasta = _Path(pasta)
    if not pasta.is_dir():
        return []
    arqs = [f for f in pasta.iterdir() if f.is_file() and f.suffix.lower() in _BAIXAVEIS]
    arqs.sort(key=lambda f: (f.suffix.lower() != ".docx", f.name))
    return [{"nome": f.name, "tipo": f.suffix.lower().lstrip("."), "tamanho": f.stat().st_size,
             "url": f"/api/dev/downloads/{pasta.name}/{_q(f.name)}"} for f in arqs]


def _ligar_artefato(pasta, aid: str) -> None:
    """Guarda na pasta da execução qual artefato ela gerou (para baixar depois pela aba Artefatos)."""
    try:
        (_Path(pasta) / "artifact.json").write_text(json.dumps({"artifact_id": aid}), encoding="utf-8")
    except Exception:
        pass


def _persist_outputs(files: list, kind: str) -> tuple[str, str]:
    """Copia os arquivos gerados para backend/data/artifacts/<kind>-<ts>/ e devolve
    (pasta, conteúdo-texto agregado até 200k)."""
    from datetime import datetime, timezone
    import uuid
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = _ARTIFACTS_DIR / f"{kind}-{stamp}-{uuid.uuid4().hex[:6]}"
    base.mkdir(parents=True, exist_ok=True)
    text_parts, total = [], 0
    for f in files:
        f = _Path(f)
        try:
            shutil.copy2(f, base / f.name)
        except Exception:
            pass
        if f.suffix.lower() in (".md", ".abap", ".txt") and total < 200_000:
            try:
                t = f.read_text(encoding="utf-8", errors="replace")
                text_parts.append(f"\n\n===== {f.name} =====\n{t}")
                total += len(t)
            except Exception:
                pass
    return str(base), ("".join(text_parts))[:200_000]


@router.post("/dev/remediation/plan")
async def remediation_plan(body: RemPlanReq, request: Request):
    """A partir da EF: descobre os objetos + o crawl de dependências Z no S/4.
    Retorna a LISTA de candidatos para o usuário aprovar/remover (nada é remediado aqui)."""
    mcp = getattr(request.app.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, "MCP indisponível — inicie o backend com o servidor SAP MCP.")
    ef_nome, fora_escopo = None, []
    if body.ef_id:
        try:
            ef_path, ef_meta, ef_texto = discovery.load_ef(body.ef_id)
        except discovery.EFValidationError as e:
            raise HTTPException(400, str(e))
        ef_nome = ef_meta.get("filename")
        try:   # extrator estrutural: repara nomes, ignora campos, respeita o escopo excluído
            seeds, fora_escopo = discovery.objetos_da_ef(ef_path)
        except Exception:  # noqa: BLE001 - se a leitura estrutural falhar, cai na busca simples
            seeds = discovery.extract_ef_objects(ef_texto)
    elif body.ef_text and body.ef_text.strip():
        seeds = discovery.extract_ef_objects(body.ef_text)
    else:
        raise HTTPException(400, "Envie a EF (.docx ou .pdf) antes de descobrir os objetos.")
    if not seeds:
        raise HTTPException(400, "Nenhum objeto (Z*/Y*) identificado na EF. Confira se a EF cita os objetos "
                                 "custom pelo nome técnico.")
    seen, candidates = set(), []
    for seed in seeds:
        deps = await _tool_json(mcp, "sap_z_dependencies",
                                {"object_name": seed, "max_depth": body.max_depth})
        for d in deps:
            key = d["name"].upper()
            if key not in seen:
                seen.add(key); candidates.append(d)
    return {"seeds": seeds, "candidates": candidates, "count": len(candidates), "ef": ef_nome,
            "fora_escopo": fora_escopo}


@router.post("/dev/remediation/run")
async def remediation_run(body: RemRunReq, request: Request):
    """Recebe a lista APROVADA, busca o source de cada objeto no S/4 e remedia."""
    mcp = getattr(request.app.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, "MCP indisponível.")
    if not body.objects:
        raise HTTPException(400, "Lista de objetos vazia — nada a remediar.")
    ok, msg = discovery.llm_preflight("remediation")
    if not ok:
        raise HTTPException(400, msg)
    sources = []
    for name in body.objects:
        d = await _tool_json(mcp, "sap_get_source", {"object_name": name})
        if d.get("source"):
            sources.append({"name": d["name"], "source": d["source"]})
    if not sources:
        raise HTTPException(422, "Nenhum source recuperado (objetos sem código ou inacessíveis).")
    try:
        rc, log, files, uso = discovery.run_remediation(sources)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"Falha ao executar o motor de remediação: {e}")
    folder, content = _persist_outputs(files, "remediation")
    aid = _save_artifact(body.project_id, "remediation",
                         f"Remediação — {len(sources)} objeto(s)",
                         content or log, fmt="abap")
    _ligar_artefato(folder, aid)
    return {"rc": rc, "objects": [s["name"] for s in sources], "downloads": _downloads(folder),
            "files": [ _Path(f).name for f in files ], "folder": folder,
            "artifact_id": aid, "log_tail": log[-1500:], "diagnosis": discovery.diagnose(log), "uso_ia": uso}


def _et_ef(body: ETPlanReq):
    """Resolve a EF enviada (valida o id e a existência do arquivo)."""
    try:
        return discovery.load_ef(body.ef_id)
    except discovery.EFValidationError as e:
        raise HTTPException(400, str(e))


async def _et_objects(mcp, body: ETPlanReq) -> list[str]:
    _et_ef(body)  # EF obrigatória e válida antes de qualquer consulta ao SAP
    if body.request_id:
        refs = await _tool_json(mcp, "sap_transport_objects", {"request_id": body.request_id})
        return [r["name"] for r in refs if r.get("name")]
    if body.objects:
        return list(dict.fromkeys(body.objects))
    raise HTTPException(400, "Informe uma request de transporte OU uma lista de objetos.")


@router.post("/dev/et/plan")
async def et_plan(body: ETPlanReq, request: Request):
    """Resolve os objetos da ET (por request de transporte OU lista). EF é obrigatória."""
    mcp = getattr(request.app.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, "MCP indisponível.")
    objects = await _et_objects(mcp, body)
    return {"source": "request" if body.request_id else "list",
            "request_id": body.request_id, "objects": objects, "count": len(objects)}


@router.post("/dev/et/run")
async def et_run(body: ETRunReq, request: Request):
    """Busca o source dos objetos (da request ou da lista) no S/4 e gera a ET com a EF como base."""
    mcp = getattr(request.app.state, "mcp", None)
    if mcp is None:
        raise HTTPException(503, "MCP indisponível.")
    ok, msg = discovery.llm_preflight()
    if not ok:
        raise HTTPException(400, msg)
    objects = await _et_objects(mcp, body)
    if not objects:
        raise HTTPException(422, "Nenhum objeto resolvido para a ET.")
    ef_path, ef_meta, _ = _et_ef(body)
    sources = []
    for name in objects:
        d = await _tool_json(mcp, "sap_get_source", {"object_name": name})
        sources.append({"name": d.get("name", name), "source": d.get("source", ""),
                        "type": d.get("type", "")})
    try:
        rc, log, files, uso = discovery.run_et(sources, ef_path)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"Falha ao executar o motor da ET: {e}")
    folder, content = _persist_outputs(files, "et")
    aid = _save_artifact(body.project_id, "technical_spec",
                         f"ET — {len(objects)} objeto(s) — EF {ef_meta.get('filename', '')}",
                         content or log, fmt="markdown")
    _ligar_artefato(folder, aid)
    return {"rc": rc, "objects": objects, "ef": ef_meta.get("filename"), "downloads": _downloads(folder),
            "files": [ _Path(f).name for f in files ], "folder": folder,
            "artifact_id": aid, "log_tail": log[-1500:], "diagnosis": discovery.diagnose(log), "uso_ia": uso}


@router.post("/dev/ef/upload")
async def ef_upload(file: UploadFile = File(...)):
    """Recebe a EF (.docx ou .pdf), valida extensão + assinatura + texto extraível,
    guarda o arquivo original e devolve o ef_id usado na geração da ET."""
    data = await file.read(discovery.EF_MAX_BYTES + 1)
    try:
        meta = discovery.validate_ef(file.filename or "", data)
    except discovery.EFValidationError as e:
        raise HTTPException(400, str(e))
    ef_id = discovery.store_ef(file.filename or "EF", data, meta)
    return {"ef_id": ef_id, "filename": meta["filename"], "ext": meta["ext"],
            "size": meta["size"], "chars": meta["chars"], "preview": meta["preview"]}


@router.get("/dev/llm/preflight")
def dev_llm_preflight():
    """Status da configuração da IA dos motores (ET/Remediação), sem chamar a IA."""
    ok, msg = discovery.llm_preflight()
    return {"ok": ok, "provider": msg if ok else None, "detail": None if ok else msg}


# ===========================================================================
# Etapa 1 — Pacote de Entrada para Descoberta SAP (sem acesso ao SAP)
# ===========================================================================
from fastapi.concurrency import run_in_threadpool  # noqa: E402


class IntakeReq(BaseModel):
    project_id: str
    ef_id: str                        # EF enviada por /api/dev/ef/upload
    estado: str = "RASCUNHO"          # RASCUNHO | EM_REVISAO | APROVADA
    versao: str = ""                  # vazio = última versão do histórico de revisão
    demanda: str = ""                 # vazio = "ID GAP" do cabeçalho
    usar_ia: bool = True              # False = 100% determinístico, sem custo de IA
    usar_cache: bool = True           # reaproveita a análise semântica da mesma EF
    imagens: str | None = None        # esbocos (padrão) | todas | nenhuma


@router.post("/dev/ef/intake")
async def ef_intake(body: IntakeReq):
    """Lê a EF, extrai com rastreabilidade, decide o gate e gera o Pacote de Entrada
    para Descoberta SAP (ou o Relatório de Pendências). Nenhuma consulta ao SAP."""
    from ..dev.ef_intake.extractor import ExtractionError
    from ..dev.ef_intake.pipeline import executar

    try:
        ef_path, ef_meta, _ = discovery.load_ef(body.ef_id)
    except discovery.EFValidationError as e:
        raise HTTPException(400, str(e))
    if body.usar_ia:
        ok, msg = discovery.llm_preflight()
        if not ok:
            raise HTTPException(400, msg + " Ou envie usar_ia=false para gerar o pacote sem IA.")
    base = _Path(__file__).resolve().parents[2] / "data" / "artifacts"
    try:
        r = await run_in_threadpool(
            executar, ef_path, versao=body.versao, estado=body.estado,
            demanda=body.demanda, salvar_em=base, usar_ia=body.usar_ia, usar_cache=body.usar_cache,
            imagens=body.imagens)
    except (ExtractionError, ValueError) as e:
        raise HTTPException(422, str(e))
    except Exception as e:  # noqa: BLE001 - falha do provedor de IA
        raise HTTPException(502, f"Falha na Etapa 1: {e}")
    kind = "ef_pending_report" if r.gate.status == "INVALIDO_PARA_DESCOBERTA" else "discovery_package"
    aid = _save_artifact(body.project_id, kind, r.arquivo, r.markdown, fmt="markdown")
    return {"gate": r.gate.status, "justificativa": r.gate.justificativa,
            "bloqueantes": r.gate.bloqueantes, "ressalvas": r.gate.ressalvas,
            "arquivo": r.arquivo, "markdown": r.markdown, "handoff": r.handoff,
            "pasta": r.pasta, "artifact_id": aid, "ef": ef_meta.get("filename"), "uso_ia": r.uso_ia,
            "feedback_arquivo": r.feedback_arquivo, "feedback_markdown": r.feedback_markdown,
            "feedback_artifact_id": _save_artifact(body.project_id, "ef_feedback", r.feedback_arquivo,
                                                   r.feedback_markdown, fmt="markdown")}


@router.get("/dev/downloads/{run_id}/{nome}")
def baixar_arquivo(run_id: str, nome: str):
    """Download de um arquivo gerado (ET, remediação). Só serve arquivos da pasta
    da própria execução, dentro de data/artifacts (sem acesso a outros caminhos)."""
    from fastapi.responses import FileResponse
    if not _RUN_ID.match(run_id):
        raise HTTPException(400, "Identificador de execução inválido.")
    if nome != _Path(nome).name or nome.startswith("."):
        raise HTTPException(400, "Nome de arquivo inválido.")
    pasta = (_ARTIFACTS_DIR / run_id).resolve()
    alvo = (pasta / nome).resolve()
    if alvo.parent != pasta or not alvo.is_file() or alvo.suffix.lower() not in _BAIXAVEIS:
        raise HTTPException(404, "Arquivo não encontrado.")
    return FileResponse(alvo, filename=nome, media_type=_BAIXAVEIS[alvo.suffix.lower()])


@router.get("/artifacts/{aid}/downloads")
def downloads_do_artefato(aid: str):
    """Arquivos baixáveis da execução que gerou o artefato (para a aba Artefatos)."""
    if not _ARTIFACTS_DIR.is_dir():
        return []
    for pasta in sorted(_ARTIFACTS_DIR.iterdir(), reverse=True):
        marca = pasta / "artifact.json"
        if pasta.is_dir() and marca.is_file():
            try:
                if json.loads(marca.read_text(encoding="utf-8")).get("artifact_id") == aid:
                    return _downloads(pasta)
            except Exception:
                continue
    return []



# ===========================================================================
# Consultor Funcional (MM): regras por seção, Validar EF e Gerar EF
# ===========================================================================
class RegraSecaoReq(BaseModel):
    titulo: str | None = None
    prompt: str | None = None
    obrigatoria: bool | None = None
    condicao: str | None = None
    ativo: bool | None = None


@router.get("/funcional/secoes")
def funcional_secoes():
    from ..funcional import secoes as reg
    return reg.carregar()


@router.put("/funcional/secoes/{sid}")
def funcional_salvar_secao(sid: str, body: RegraSecaoReq):
    from ..funcional import secoes as reg
    if body.prompt is not None and not body.prompt.strip():
        raise HTTPException(400, "O prompt da seção não pode ficar vazio.")
    if body.condicao:
        try:
            re.compile(body.condicao)
        except re.error:
            raise HTTPException(400, "Condição inválida (use palavras separadas por |, ex.: interface|migra).")
    try:
        return reg.salvar(sid, body.model_dump(exclude_none=True))
    except KeyError:
        raise HTTPException(404, "Seção não encontrada.")


@router.post("/funcional/secoes/{sid}/restaurar")
def funcional_restaurar_secao(sid: str):
    from ..funcional import secoes as reg
    return reg.restaurar(sid)


def _nova_pasta(tipo: str):
    import uuid
    from datetime import datetime, timezone
    pasta = _ARTIFACTS_DIR / f"{tipo}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


class ValidarEFReq(BaseModel):
    project_id: str
    ef_id: str
    estado: str = "RASCUNHO"
    imagens: str | None = None        # esbocos | todas | nenhuma


@router.post("/funcional/ef/validar")
async def funcional_validar_ef(body: ValidarEFReq):
    """Etapa 1 completa (gate, bloqueios a confirmar, esboços) + revisão seção por seção,
    num relatório único e descontraído para o funcional."""
    from dataclasses import asdict
    from ..dev.ef_intake.extractor import ExtractionError
    from ..dev.ef_intake.pipeline import executar
    from ..funcional import validar as val

    try:
        ef_path, ef_meta, _ = discovery.load_ef(body.ef_id)
    except discovery.EFValidationError as e:
        raise HTTPException(400, str(e))
    ok, msg = discovery.llm_preflight()
    if not ok:
        raise HTTPException(400, msg)
    pasta = _nova_pasta("efval")
    try:
        r = await run_in_threadpool(executar, ef_path, estado=body.estado, salvar_em=pasta, imagens=body.imagens)
        secs, uso_rev = await run_in_threadpool(val.revisar, ef_path)
    except (ExtractionError, ValueError) as e:
        raise HTTPException(422, str(e))
    except Exception as e:  # noqa: BLE001 - falha do provedor de IA
        raise HTTPException(502, f"Falha na validação: {e}")

    relatorio = val.inserir_no_feedback(r.feedback_markdown, val.markdown_revisao(secs), secs)
    base = r.feedback_arquivo.replace("-Feedback-Funcional-EF-", "-Validacao-EF-")
    (pasta / base).write_text(relatorio, encoding="utf-8")
    (pasta / r.arquivo).write_text(r.markdown, encoding="utf-8")
    (pasta / "revisao_secoes.json").write_text(json.dumps([asdict(x) for x in secs], ensure_ascii=False, indent=2),
                                               encoding="utf-8")
    aid = _save_artifact(body.project_id, "ef_validation", base, relatorio, fmt="markdown")
    _ligar_artefato(pasta, aid)
    return {"gate": r.gate.status, "justificativa": r.gate.justificativa,
            "bloqueantes": r.gate.bloqueantes, "a_confirmar": r.gate.a_confirmar,
            "secoes": [asdict(x) for x in secs], "relatorio": relatorio, "ef": ef_meta.get("filename"),
            "uso_ia": {"etapa1": r.uso_ia, "revisao": uso_rev}, "downloads": _downloads(pasta),
            "artifact_id": aid}


class GerarEFReq(BaseModel):
    project_id: str
    workshop_id: str                  # documento enviado por /api/dev/ef/upload
    id_gap: str = ""
    descricao: str = ""
    modulo: str = "MM"


@router.post("/funcional/ef/gerar")
async def funcional_gerar_ef(body: GerarEFReq):
    """Rascunho de EF no template oficial, a partir do documento de Workshop B."""
    import os
    import tempfile
    from ..dev.ef_intake.extractor import ExtractionError, extract, load_provider, resolve_model
    from ..funcional import gerar_ef as g
    from ..usage import resumo as resumo_uso

    try:
        _, ws_meta, ws_texto = discovery.load_ef(body.workshop_id)
    except discovery.EFValidationError as e:
        raise HTTPException(400, str(e).replace("EF", "documento do workshop", 1))
    ok, msg = discovery.llm_preflight()
    if not ok:
        raise HTTPException(400, msg)
    ws_nome = ws_meta.get("filename", "workshop")
    log = _Path(tempfile.mkstemp(prefix="efdraft_uso_", suffix=".jsonl")[1])
    anterior = os.environ.get("LLM_USAGE_LOG")
    os.environ["LLM_USAGE_LOG"] = str(log)
    try:
        rasc, _ = await run_in_threadpool(
            extract, load_provider(), g.mensagem(ws_texto, nome=ws_nome, id_gap=body.id_gap,
                                                 descricao=body.descricao, modulo=body.modulo),
            system=g.PROMPT_GERADOR, model_cls=g.RascunhoEF)
    except ExtractionError as e:
        raise HTTPException(422, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(502, f"Falha ao gerar o rascunho: {e}")
    finally:
        if anterior is None:
            os.environ.pop("LLM_USAGE_LOG", None)
        else:
            os.environ["LLM_USAGE_LOG"] = anterior
    usos = discovery.ler_uso(log)
    log.unlink(missing_ok=True)
    if body.id_gap and not rasc.identificacao.id_gap:
        rasc.identificacao.id_gap = body.id_gap
    if body.descricao and not rasc.identificacao.descricao_gap:
        rasc.identificacao.descricao_gap = body.descricao

    from .db import get_session as _gs
    from .models import User as _U
    with _gs() as sdb:
        u = sdb.exec(select(_U)).first()
        autor = (u.display_name if u else "") or ""
    pasta = _nova_pasta("efdraft")
    ident = re.sub(r"[^A-Za-z0-9._-]+", "-", rasc.identificacao.id_gap or "EF").strip("-") or "EF"
    arquivo = pasta / f"{ident}-EF-RASCUNHO-v0.docx"
    await run_in_threadpool(g.montar_docx, rasc, arquivo, workshop_nome=ws_nome, autor=autor)
    resumo_md = g.markdown_resumo(rasc, ws_nome)
    (pasta / f"{ident}-EF-RASCUNHO-resumo.md").write_text(resumo_md, encoding="utf-8")
    (pasta / "rascunho.json").write_text(rasc.model_dump_json(indent=2), encoding="utf-8")
    aid = _save_artifact(body.project_id, "ef_draft", arquivo.name, resumo_md, fmt="markdown")
    _ligar_artefato(pasta, aid)
    return {"arquivo": arquivo.name, "workshop": ws_nome, "a_confirmar": g.contar_confirmar(rasc),
            "pontos_a_confirmar": rasc.pontos_a_confirmar, "observacoes": rasc.observacoes_para_o_funcional,
            "contagem": {"objetos": len(rasc.resumo.inventario), "regras": len(rasc.regras),
                         "fluxo": len(rasc.fluxo), "testes": len(rasc.testes)},
            "resumo": resumo_md, "downloads": _downloads(pasta), "artifact_id": aid,
            "uso_ia": resumo_uso(usos, resolve_model()[0]) if usos else {"chamadas": 1}}
