"""Edições de regras por PROJETO (camada 3), com histórico (versão, quem, quando)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from opuscore_core.sdk.config import diretorio_dados
from opuscore_ef.validacao import secoes as padrao

from ..conhecimento.regras_secao_mm import AJUSTES_MM


def _arquivo(projeto_id: str) -> Path:
    p = diretorio_dados() / "consultores" / "funcional-mm" / "regras" / f"{re.sub(r'[^A-Za-z0-9_-]', '_', projeto_id)}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _ler(projeto_id: str) -> dict:
    p = _arquivo(projeto_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {"edicoes": {}, "historico": []}


def _gravar(projeto_id: str, dados: dict) -> None:
    _arquivo(projeto_id).write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def vigentes(projeto_id: str) -> list[dict]:
    return padrao.carregar(AJUSTES_MM, _ler(projeto_id)["edicoes"])


def salvar(projeto_id: str, sid: str, mudancas: dict, usuario: str) -> dict:
    if sid not in padrao.ids():
        raise KeyError(sid)
    d = _ler(projeto_id)
    atual = d["edicoes"].get(sid, {})
    atual.update({k: v for k, v in mudancas.items() if k in padrao.CAMPOS_EDITAVEIS and v is not None})
    d["edicoes"][sid] = atual
    d["historico"].append({"secao": sid, "versao": sum(1 for h in d["historico"] if h["secao"] == sid) + 1,
                           "por": usuario, "em": datetime.now(timezone.utc).isoformat(), "mudancas": mudancas})
    _gravar(projeto_id, d)
    return next(r for r in vigentes(projeto_id) if r["id"] == sid)


def restaurar(projeto_id: str, sid: str, usuario: str) -> dict:
    d = _ler(projeto_id)
    d["edicoes"].pop(sid, None)
    d["historico"].append({"secao": sid, "versao": 0, "por": usuario, "em": datetime.now(timezone.utc).isoformat(),
                           "mudancas": {"restaurado": True}})
    _gravar(projeto_id, d)
    return next(r for r in vigentes(projeto_id) if r["id"] == sid)


def historico(projeto_id: str, sid: str | None = None) -> list[dict]:
    return [h for h in _ler(projeto_id)["historico"] if sid in (None, h["secao"])]
