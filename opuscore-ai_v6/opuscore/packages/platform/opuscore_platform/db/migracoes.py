"""Migrações versionadas, por pacote. Cada migração é (id, funcao(conexao)) e roda uma
única vez, registrada na tabela opuscore_migracoes. Tabelas NOVAS são criadas pelo
create_all; migrações cuidam de ALTERAR o que já existe (create_all não altera)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from sqlalchemy import text

Migracao = tuple[str, Callable]

MIGRACOES_PLATAFORMA: list[Migracao] = []


def aplicar(engine, migracoes: list[Migracao]) -> list[str]:
    aplicadas = []
    with engine.begin() as c:
        c.execute(text("CREATE TABLE IF NOT EXISTS opuscore_migracoes (id VARCHAR PRIMARY KEY, aplicada_em VARCHAR)"))
        feitas = {r[0] for r in c.execute(text("SELECT id FROM opuscore_migracoes"))}
        for mid, fn in migracoes:
            if mid in feitas:
                continue
            fn(c)
            c.execute(text("INSERT INTO opuscore_migracoes (id, aplicada_em) VALUES (:i, :a)"),
                      {"i": mid, "a": datetime.now(timezone.utc).isoformat()})
            aplicadas.append(mid)
    return aplicadas
