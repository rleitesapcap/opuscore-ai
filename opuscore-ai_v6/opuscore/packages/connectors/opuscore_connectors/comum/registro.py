"""Registro de ferramentas com NÍVEL de acesso obrigatório.

Níveis: leitura_tecnica (livre) · leitura_dados (política + auditoria) · escrita (guard +
aprovação + auditoria). Uma ferramenta sem nível declarado não é registrada, e o teste
do pacote falha.
"""
from __future__ import annotations

import json
from typing import Callable

NIVEIS = {"leitura_tecnica", "leitura_dados", "escrita"}
_FERRAMENTAS: list[dict] = []


def ferramenta(*, sistema: str, nivel: str):
    if nivel not in NIVEIS:
        raise ValueError(f"Nível inválido: {nivel}. Use {sorted(NIVEIS)}.")

    def marcar(fn: Callable) -> Callable:
        fn.__opuscore__ = {"sistema": sistema, "nivel": nivel}
        _FERRAMENTAS.append({"nome": fn.__name__, "sistema": sistema, "nivel": nivel, "fn": fn})
        return fn
    return marcar


def ferramentas(sistema: str | None = None) -> list[dict]:
    return [f for f in _FERRAMENTAS if sistema in (None, f["sistema"])]


def erro(msg: str) -> str:
    return json.dumps({"error": msg}, ensure_ascii=False)
