"""Tabelas do Orquestrador (prefixo orq_). O banco é o da Plataforma (injetado)."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


def _uid() -> str:
    return uuid.uuid4().hex


def agora() -> datetime:
    return datetime.now(timezone.utc)


class EventoRegistro(SQLModel, table=True):
    __tablename__ = "orq_evento"
    id: str = Field(primary_key=True)
    tipo: str = Field(index=True)
    versao: int = 1
    projeto_id: str = Field(index=True)
    gap_id: str = Field(index=True)
    origem: str
    causa_id: str | None = None
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    artefatos: list = Field(default_factory=list, sa_column=Column(JSON))
    ocorrido_em: datetime = Field(default_factory=agora)


class EntregaEvento(SQLModel, table=True):
    """Outbox: uma entrega por assinante. PENDENTE -> ENTREGUE | FALHA (fila de falhas)."""
    __tablename__ = "orq_entrega"
    id: str = Field(default_factory=_uid, primary_key=True)
    evento_id: str = Field(index=True, foreign_key="orq_evento.id")
    destino: str = Field(index=True)            # key do consultor assinante
    tratador: str
    status: str = Field(default="PENDENTE", index=True)
    tentativas: int = 0
    proximo_em: datetime = Field(default_factory=agora)
    erro: str = Field(default="", sa_column=Column(Text))
    atualizado_em: datetime = Field(default_factory=agora)


class HandoffRegistro(SQLModel, table=True):
    __tablename__ = "orq_handoff"
    id: str = Field(default_factory=_uid, primary_key=True)
    projeto_id: str = Field(index=True)
    gap_id: str = Field(index=True)
    de: str
    para: str = Field(index=True)
    titulo: str
    evento_id: str | None = None
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    artefatos: list = Field(default_factory=list, sa_column=Column(JSON))
    estado: str = Field(default="CRIADO", index=True)
    motivo: str = Field(default="", sa_column=Column(Text))
    historico: list = Field(default_factory=list, sa_column=Column(JSON))
    criado_em: datetime = Field(default_factory=agora)
    atualizado_em: datetime = Field(default_factory=agora)
