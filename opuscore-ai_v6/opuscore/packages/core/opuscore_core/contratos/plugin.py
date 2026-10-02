"""Contrato de plugin: como um consultor se apresenta à Plataforma.

Cada consultor publica um objeto PLUGIN (subclasse de PluginBase) pelo entry point
"opuscore.consultores" do seu pyproject.toml. A Plataforma descobre, valida o
manifesto, monta as rotas em /api/c/<key>, serve a tela em /c/<key>/ e sincroniza o
perfil no banco.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from pydantic import BaseModel, Field

from ..versao import CONTRATO_PLUGIN, CONTRATO_WEB

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import APIRouter


class WebManifesto(BaseModel):
    rota: str                       # rota no shell: #/c/<rota>
    entrada: str = "main.js"        # módulo ES com mount(area, ctx) / unmount()
    css: str | None = None          # CSS escopado em .c-<key>


class Manifesto(BaseModel):
    key: str                        # identificador único (slug): "funcional-mm"
    nome: str
    area: str = ""                  # ex.: "Funcional", "Desenvolvimento"
    especialidade: str = ""         # ex.: "Materiais e compras"
    status_label: str = "Ativo"
    trabalho_atual: str = ""
    versao: str = "1.0.0"
    contrato_plugin: int = CONTRATO_PLUGIN
    contrato_web: int = CONTRATO_WEB
    web: WebManifesto | None = None
    # eventos assinados: {"ef.validada": "nome_do_metodo"}; o método recebe (evento, ctx)
    assina: dict[str, str] = Field(default_factory=dict)


class PerfilAgente(BaseModel):
    persona: str = ""
    instrucoes: str = ""
    skills: list[str] = Field(default_factory=list)


class PluginBase:
    """Base com padrões; o consultor sobrescreve só o que usa."""

    manifesto: Manifesto

    def perfil(self) -> PerfilAgente:
        return PerfilAgente()

    def rotas(self, obter_ctx: Callable[..., Any]) -> "APIRouter | None":
        """Rotas do consultor. Use `ctx = Depends(obter_ctx)` em cada rota."""
        return None

    @property
    def web_dir(self) -> Path | None:
        return None

    def migracoes(self) -> list[tuple[str, Callable[[Any], None]]]:
        """[(id, funcao(conexao))] aplicadas uma vez, na ordem, pela Plataforma."""
        return []
