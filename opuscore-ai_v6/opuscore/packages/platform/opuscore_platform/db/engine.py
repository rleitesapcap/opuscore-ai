"""Banco da Plataforma. SQLite local por padrão (OPUSCORE_DB ou <dados>/opuscore.db);
OPUSCORE_DB_URL aceita outro banco (ex.: postgresql+psycopg://...).

Tabelas novas: create_all. Alterações de estrutura: migrações versionadas
(db/migracoes.py), da Plataforma e de cada plugin.
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

_engine = None


def db_path() -> Path:
    env = os.environ.get("OPUSCORE_DB")
    if env:
        return Path(env)
    from opuscore_core.sdk.config import diretorio_dados
    return diretorio_dados() / "opuscore.db"


def get_engine():
    global _engine
    if _engine is None:
        url = os.environ.get("OPUSCORE_DB_URL")
        if url:
            _engine = create_engine(url)
        else:
            path = db_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            _engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    return _engine


def init_db() -> None:
    """Cria as tabelas que ainda não existem."""
    from . import modelos  # noqa: F401 - registra as tabelas no metadata
    import opuscore_orchestrator.modelos  # noqa: F401 - tabelas do orquestrador (orq_)

    SQLModel.metadata.create_all(get_engine())


def get_session() -> Session:
    return Session(get_engine())


def reiniciar_engine() -> None:
    """Usado nos testes, ao trocar OPUSCORE_DB."""
    global _engine
    _engine = None
