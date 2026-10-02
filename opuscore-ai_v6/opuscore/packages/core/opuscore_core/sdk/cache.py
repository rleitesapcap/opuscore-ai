"""Cache simples em disco (JSON por chave)."""
from __future__ import annotations

import json
from pathlib import Path


class CacheJson:
    def __init__(self, diretorio: Path):
        self.dir = Path(diretorio)

    def ler(self, chave: str) -> dict | None:
        p = self.dir / f"{chave}.json"
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
        return None

    def gravar(self, chave: str, dados: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / f"{chave}.json").write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
