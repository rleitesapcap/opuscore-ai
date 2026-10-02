"""Handoff: pedido de trabalho de um consultor para outro, com ciclo de vida."""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class EstadoHandoff(str, Enum):
    CRIADO = "CRIADO"
    ACEITO = "ACEITO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    CONCLUIDO = "CONCLUIDO"
    DEVOLVIDO = "DEVOLVIDO"
    CANCELADO = "CANCELADO"


E = EstadoHandoff
TRANSICOES: dict[EstadoHandoff, set[EstadoHandoff]] = {
    E.CRIADO: {E.ACEITO, E.DEVOLVIDO, E.CANCELADO},
    E.ACEITO: {E.EM_ANDAMENTO, E.CONCLUIDO, E.DEVOLVIDO, E.CANCELADO},
    E.EM_ANDAMENTO: {E.CONCLUIDO, E.DEVOLVIDO, E.CANCELADO},
    E.DEVOLVIDO: set(), E.CONCLUIDO: set(), E.CANCELADO: set(),
}


def pode_transitar(atual: EstadoHandoff, novo: EstadoHandoff) -> bool:
    return novo in TRANSICOES.get(atual, set())


class HandoffDTO(BaseModel):
    id: str
    projeto_id: str
    gap_id: str
    de: str                          # key do consultor de origem
    para: str                        # key do consultor de destino
    titulo: str
    evento_id: str | None = None
    payload: dict = Field(default_factory=dict)
    artefatos: list[str] = Field(default_factory=list)
    estado: EstadoHandoff = EstadoHandoff.CRIADO
    motivo: str = ""
    criado_em: datetime | None = None
    atualizado_em: datetime | None = None
