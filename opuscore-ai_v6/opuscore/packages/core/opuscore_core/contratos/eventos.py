"""Eventos entre consultores: envelope comum + um esquema versionado por tipo.

Regras de compatibilidade:
- Acrescentar campo OPCIONAL: mesma versão.
- Mudar ou remover campo: nova versão (ex.: "ef.validada" v2); as duas convivem.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

_ESQUEMAS: dict[tuple[str, int], type[BaseModel]] = {}


def esquema(tipo: str, versao: int):
    def registrar(cls: type[BaseModel]) -> type[BaseModel]:
        _ESQUEMAS[(tipo, versao)] = cls
        cls.__evento__ = (tipo, versao)
        return cls
    return registrar


def esquemas() -> dict[tuple[str, int], type[BaseModel]]:
    return dict(_ESQUEMAS)


def validar_payload(tipo: str, versao: int, payload: dict) -> dict:
    cls = _ESQUEMAS.get((tipo, versao))
    if cls is None:
        raise ValueError(f"Evento sem esquema registrado no Core: {tipo} v{versao}")
    return cls.model_validate(payload).model_dump(mode="json")


class Evento(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    tipo: str
    versao: int = 1
    projeto_id: str
    gap_id: str                      # liga tudo do mesmo GAP (ex.: "SD-034")
    origem: str                      # key do consultor que publicou
    causa_id: str | None = None
    ocorrido_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict = Field(default_factory=dict)
    artefatos: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Esquemas v1
# ---------------------------------------------------------------------------
@esquema("ef.validada", 1)
class EfValidadaV1(BaseModel):
    gate: Literal["VALIDO_PARA_DESCOBERTA", "VALIDO_COM_RESSALVAS"]
    upload_id: str                       # EF original (serviço de uploads da Plataforma)
    ef_arquivo: str
    objetos_no_escopo: list[str] = Field(default_factory=list)
    objetos_fora_escopo: list[str] = Field(default_factory=list)
    relatorio_artefato: str | None = None
    handoff_etapa2: dict = Field(default_factory=dict)   # saída da Etapa 1 (pacote EF)
    observacao: str = ""


@esquema("ef.rascunho_gerado", 1)
class EfRascunhoGeradoV1(BaseModel):
    artefato: str
    workshop: str
    a_confirmar: int = 0


@esquema("et.gerada", 1)
class EtGeradaV1(BaseModel):
    artefato: str
    objetos: list[str] = Field(default_factory=list)
    ok: bool = True


@esquema("remediacao.concluida", 1)
class RemediacaoConcluidaV1(BaseModel):
    artefato: str
    objetos: list[str] = Field(default_factory=list)
    ok: bool = True
