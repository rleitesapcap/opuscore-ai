"""Objetos técnicos citados na EF (para a remediação e a Etapa 2)."""
from __future__ import annotations

import re
from pathlib import Path

_Z_TOKEN = re.compile(r"\b([ZzYy][A-Za-z0-9_]{2,})\b")


def refs_z_texto(texto: str) -> list[str]:
    """Busca simples por nomes Z/Y num texto (reserva quando não há o arquivo da EF)."""
    refs: set[str] = set()
    for linha in (texto or "").splitlines():
        if linha.lstrip().startswith("*"):
            continue
        refs.update(t.upper() for t in _Z_TOKEN.findall(linha))
    return sorted(refs)


def objetos_tecnicos(ef_path: Path) -> tuple[list[str], list[str]]:
    """(no_escopo, fora_do_escopo) pelo extrator determinístico: nomes quebrados em tabela
    são reparados, campos (TABELA-CAMPO) não viram objeto e o escopo excluído é separado."""
    from .intake import deterministic as det
    from .intake.parser import parse_ef

    itens, _ = det.extrair(parse_ef(Path(ef_path)))
    no_escopo, fora = [], []
    for i in itens:
        v = (i.valor_original or "").upper()
        if i.categoria != "REF_TECNICA" or not re.match(r"^[ZY]", v) or "-" in v or \
                i.tipo_objeto in ("CAMPO_TABELA", "METODO"):
            continue
        (fora if i.escopo == "EXCLUIDO" else no_escopo).append(v)
    return sorted(dict.fromkeys(no_escopo)), sorted(dict.fromkeys(fora))
