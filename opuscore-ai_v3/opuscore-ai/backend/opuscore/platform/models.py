"""Modelo de dados da plataforma OPUSCORE-AI (Fase 1 / MVP).

Espelha o modelo lógico da spec v0.3, recortado para o MVP. Entidades de Fase 2+
(Task, Handoff, Gate, Approval, Requirement, TraceLink, SystemQuery) ficam de fora
por ora — entram quando o fluxo de entrega chegar.

Chaves são UUID (str) para portabilidade. Campos JSON guardam estruturas flexíveis
(permissões, config, evidência) sem exigir migração a cada ajuste fino.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, JSON, Text, UniqueConstraint
from sqlmodel import Field, SQLModel


def _uid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --- enums (como str p/ simplicidade e portabilidade) ----------------------
class Visibility:
    PROJECT_SHARED = "PROJECT_SHARED"
    AGENT_PROFILE_PRIVATE = "AGENT_PROFILE_PRIVATE"
    PROJECT_AGENT_PRIVATE = "PROJECT_AGENT_PRIVATE"
    TASK_PRIVATE = "TASK_PRIVATE"
    HANDOFF_SHARED = "HANDOFF_SHARED"
    APPROVED_PROJECT_ARTIFACT = "APPROVED_PROJECT_ARTIFACT"


class OwnerType:
    PROJECT = "project"
    AGENT_PROFILE = "agent_profile"
    PROJECT_AGENT = "project_agent"
    TASK = "task"


class SapProduct:
    S4_ADT = "s4_adt"
    S4_DATA = "s4_data"
    BTP = "btp"
    CI = "ci"


# --- identidade -------------------------------------------------------------
class User(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    username: str = Field(index=True, unique=True)
    display_name: str = ""
    is_admin: bool = True  # monousuário local = admin
    created_at: datetime = Field(default_factory=_now)


class Membership(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "project_id"),)
    id: str = Field(default_factory=_uid, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    role: str = "owner"  # owner | editor | viewer
    scopes: dict = Field(default_factory=dict, sa_column=Column(JSON))  # teto de authz
    created_at: datetime = Field(default_factory=_now)


# --- projeto ----------------------------------------------------------------
class Project(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    name: str = Field(index=True)
    client: str = ""
    unit: str = ""
    description: str = ""
    language: str = "pt-BR"
    status: str = "active"  # active | archived
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ProjectContext(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("project_id", "version"),)
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    version: int = 1
    content: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_by: str = ""
    created_at: datetime = Field(default_factory=_now)


# --- catálogo de agentes ----------------------------------------------------
class AgentProfile(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    key: str = Field(index=True, unique=True)  # slug: "arquiteto", "dev-abap"
    name: str
    role: str = ""
    specialty: str = ""
    modules: list = Field(default_factory=list, sa_column=Column(JSON))
    seniority: str = ""
    description: str = ""
    owner: str = ""
    status: str = "active"  # draft | active | inactive | archived
    current_version: int = 1
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class AgentProfileVersion(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("profile_id", "version"),)
    id: str = Field(default_factory=_uid, primary_key=True)
    profile_id: str = Field(foreign_key="agentprofile.id", index=True)
    version: int
    persona: str = Field(default="", sa_column=Column(Text))
    instructions: str = Field(default="", sa_column=Column(Text))
    output_format: str = Field(default="", sa_column=Column(Text))
    policies: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_by: str = ""
    created_at: datetime = Field(default_factory=_now)


class AgentSkill(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    profile_id: str = Field(foreign_key="agentprofile.id", index=True)
    name: str
    description: str = ""
    category: str = ""
    preconditions: str = Field(default="", sa_column=Column(Text))
    inputs: dict = Field(default_factory=dict, sa_column=Column(JSON))
    steps: str = Field(default="", sa_column=Column(Text))
    allowed_tools: list = Field(default_factory=list, sa_column=Column(JSON))
    allowed_sources: list = Field(default_factory=list, sa_column=Column(JSON))
    output_schema: dict = Field(default_factory=dict, sa_column=Column(JSON))
    quality_checklist: list = Field(default_factory=list, sa_column=Column(JSON))
    acceptance: str = Field(default="", sa_column=Column(Text))
    enabled: bool = True
    created_at: datetime = Field(default_factory=_now)


class ProjectAgentAssignment(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("project_id", "profile_id"),)
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    profile_id: str = Field(foreign_key="agentprofile.id", index=True)
    profile_version: int = 1  # versão fixada nesta atribuição
    permissions: dict = Field(default_factory=dict, sa_column=Column(JSON))
    enabled_skills: list = Field(default_factory=list, sa_column=Column(JSON))
    extra_instructions: str = Field(default="", sa_column=Column(Text))
    limits: dict = Field(default_factory=dict, sa_column=Column(JSON))
    status: str = "active"
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


# --- conexões SAP (um adaptador/MCP por produto) ----------------------------
class CredentialRef(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    alias: str = Field(index=True, unique=True)  # chave no cofre; nunca o segredo
    kind: str = "basic"  # basic | oauth2 | bearer
    created_at: datetime = Field(default_factory=_now)


class SystemConnection(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    product: str = SapProduct.S4_ADT
    environment: str = "DEV"  # DEV | QAS | PRD
    name: str = ""
    purpose: str = ""
    base_url: str = ""
    sap_client: str = ""
    auth: str = "basic"
    credential_ref_id: str | None = Field(default=None, foreign_key="credentialref.id")
    status: str = "configured"
    allowed_operations: list = Field(default_factory=list, sa_column=Column(JSON))
    read_only: bool = True
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class AgentConnectionPermission(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("assignment_id", "connection_id"),)
    id: str = Field(default_factory=_uid, primary_key=True)
    assignment_id: str = Field(foreign_key="projectagentassignment.id", index=True)
    connection_id: str = Field(foreign_key="systemconnection.id", index=True)
    allowed_operations: list = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)


# --- conhecimento / RAG -----------------------------------------------------
class EmbeddingModel(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    name: str = Field(index=True)  # ex.: bge-m3
    dim: int = 0
    provider: str = ""  # ollama | sentence-transformers
    created_at: datetime = Field(default_factory=_now)


class KnowledgeCollection(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str | None = Field(default=None, foreign_key="project.id", index=True)
    owner_type: str = OwnerType.PROJECT
    owner_id: str = ""  # profile_id / assignment_id / task_id / project_id
    visibility: str = Visibility.PROJECT_SHARED
    name: str = ""
    embedding_model_id: str | None = Field(default=None, foreign_key="embeddingmodel.id")
    config: dict = Field(default_factory=dict, sa_column=Column(JSON))  # top_k, filtros...
    created_at: datetime = Field(default_factory=_now)


class Document(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str | None = Field(default=None, foreign_key="project.id", index=True)
    collection_id: str = Field(foreign_key="knowledgecollection.id", index=True)
    visibility: str = Visibility.PROJECT_SHARED
    owner_type: str = OwnerType.PROJECT
    owner_id: str = ""
    task_id: str = ""
    title: str = ""
    original_name: str = ""
    file_type: str = ""
    sensitivity: str = "internal"  # public | internal | confidential | restricted
    language: str = "pt-BR"
    author: str = ""
    tags: list = Field(default_factory=list, sa_column=Column(JSON))
    status: str = "uploaded"  # uploaded | processing | indexed | failed
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class DocumentVersion(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("document_id", "version"),)
    id: str = Field(default_factory=_uid, primary_key=True)
    document_id: str = Field(foreign_key="document.id", index=True)
    version: int = 1
    stored_path: str = ""  # arquivo original preservado
    extracted_text_path: str = ""
    extraction_status: str = "pending"
    extraction_notes: str = Field(default="", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=_now)


class DocumentChunk(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    document_id: str = Field(foreign_key="document.id", index=True)
    document_version_id: str = Field(foreign_key="documentversion.id", index=True)
    embedding_model_id: str | None = Field(default=None, foreign_key="embeddingmodel.id")
    ordinal: int = 0
    text: str = Field(default="", sa_column=Column(Text))
    page: str = ""
    section: str = ""
    # o vetor vive no LanceDB, com este id como chave e os metadados de filtro
    created_at: datetime = Field(default_factory=_now)


# --- chat -------------------------------------------------------------------
class Conversation(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    profile_id: str = Field(foreign_key="agentprofile.id", index=True)
    assignment_id: str | None = Field(default=None, foreign_key="projectagentassignment.id")
    title: str = ""
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Message(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.id", index=True)
    role: str = "user"  # user | assistant | tool | system
    content: str = Field(default="", sa_column=Column(Text))
    tool_name: str = ""
    evidence: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)


# --- entregáveis / operação -------------------------------------------------
class Artifact(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str = Field(foreign_key="project.id", index=True)
    kind: str = "other"  # architecture_report | functional_spec | technical_spec | object_report
    title: str = ""
    format: str = "markdown"
    content: str = Field(default="", sa_column=Column(Text))
    version: int = 1
    status: str = "draft"  # draft | approved
    produced_by: str = ""  # profile key
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class Execution(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str | None = Field(default=None, foreign_key="project.id")
    profile_id: str | None = Field(default=None, foreign_key="agentprofile.id")
    profile_version: int = 0
    kind: str = ""  # report | chat | ingest
    llm_provider: str = ""
    sources: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)


class UsageRecord(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    execution_id: str | None = Field(default=None, foreign_key="execution.id")
    tokens_in: int = 0
    tokens_out: int = 0
    ms: int = 0
    cost: float = 0.0
    created_at: datetime = Field(default_factory=_now)


class AuditEvent(SQLModel, table=True):
    id: str = Field(default_factory=_uid, primary_key=True)
    project_id: str | None = Field(default=None, foreign_key="project.id", index=True)
    actor: str = ""
    event: str = ""
    detail: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_now)
