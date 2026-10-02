"""Implementação do ctx (contrato do Core) entregue a cada consultor."""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from fastapi import Request
from opuscore_core.sdk.config import diretorio_dados
from opuscore_core.sdk.mcp import ClienteMCPJson

from .servicos.artefatos import ServicoArtefatos
from .servicos.uploads import ServicoUploads


class AuditoriaArquivo:
    def __init__(self, plugin_key: str):
        self.plugin_key = plugin_key

    def registrar(self, acao: str, /, **campos: Any) -> None:
        p = diretorio_dados() / "audit" / "plataforma.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        linha = {"em": datetime.now(timezone.utc).isoformat(), "consultor": self.plugin_key, "acao": acao, **campos}
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")


class _EventosIndisponiveis:
    async def publicar(self, *a, **k):
        from opuscore_core.contratos.erros import indisponivel
        raise indisponivel("Orquestrador indisponível.")


@dataclass
class ContextoPlataforma:
    plugin_key: str
    mcp: Any
    eventos: Any
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    usuario: str = "local"
    artefatos: Any = None
    uploads: Any = field(default_factory=ServicoUploads)
    auditoria: Any = None
    config: dict = field(default_factory=lambda: dict(os.environ))

    def __post_init__(self):
        self.artefatos = self.artefatos or ServicoArtefatos(self.plugin_key)
        self.auditoria = self.auditoria or AuditoriaArquivo(self.plugin_key)

    def ia(self, nome: str | None = None):
        from opuscore_core.sdk.ia import build_provider
        return build_provider(nome)


def fabrica_contexto(app) -> Callable[[str], ContextoPlataforma]:
    """ctx para um consultor fora de uma requisição (ex.: ao receber um evento)."""
    def criar(plugin_key: str, request_id: str | None = None) -> ContextoPlataforma:
        orq = getattr(app.state, "orquestrador", None)
        return ContextoPlataforma(plugin_key=plugin_key, mcp=ClienteMCPJson(getattr(app.state, "mcp", None)),
                                  eventos=orq.publicador(plugin_key) if orq else _EventosIndisponiveis(),
                                  **({"request_id": request_id} if request_id else {}))
    return criar


def dependencia_ctx(plugin_key: str):
    """Dependência FastAPI: `ctx = Depends(obter_ctx)` nas rotas do consultor."""
    def obter_ctx(request: Request) -> ContextoPlataforma:
        return fabrica_contexto(request.app)(plugin_key, getattr(request.state, "request_id", None))
    return obter_ctx
