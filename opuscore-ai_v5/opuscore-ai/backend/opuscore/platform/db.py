"""Banco local (SQLite via SQLModel). Local-first: um arquivo na máquina.

Migrações: no MVP usamos create_all para bootstrap. Quando o schema estabilizar,
plugamos Alembic (autogenerate a partir do SQLModel.metadata) sem reescrever nada.
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
    backend_dir = Path(__file__).resolve().parents[2]  # .../backend
    return backend_dir / "data" / "opuscore.db"


def get_engine():
    global _engine
    if _engine is None:
        path = db_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{path}",
            connect_args={"check_same_thread": False},
        )
    return _engine


def init_db() -> None:
    """Cria as tabelas que ainda não existem."""
    from . import models  # noqa: F401 - registra as tabelas no metadata

    SQLModel.metadata.create_all(get_engine())


def get_session() -> Session:
    return Session(get_engine())
