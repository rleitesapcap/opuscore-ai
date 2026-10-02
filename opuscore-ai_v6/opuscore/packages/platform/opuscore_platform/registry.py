"""Registro de plugins: descobre os consultores instalados (entry points
"opuscore.consultores"), valida o manifesto e isola falhas (um plugin com erro não
derruba os outros; o erro aparece em /api/plataforma/plugins)."""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from importlib.metadata import entry_points

from opuscore_core.contratos.plugin import Manifesto
from opuscore_core.versao import CONTRATOS_SUPORTADOS

log = logging.getLogger("opuscore.registro")
GRUPO = "opuscore.consultores"


@dataclass
class Registro:
    plugins: list = field(default_factory=list)
    erros: list[dict] = field(default_factory=list)

    @property
    def por_key(self) -> dict:
        return {p.manifesto.key: p for p in self.plugins}

    def situacao(self) -> list[dict]:
        ok = [{"key": p.manifesto.key, "nome": p.manifesto.nome, "versao": p.manifesto.versao, "status": "ok",
               "tela": p.manifesto.web.rota if p.manifesto.web else None,
               "assina": list(p.manifesto.assina)} for p in self.plugins]
        return ok + [{**e, "status": "erro"} for e in self.erros]


def filtro_ambiente() -> set[str] | None:
    v = os.environ.get("OPUSCORE_PLUGINS", "").strip()
    return {x.strip() for x in v.split(",") if x.strip()} or None


def validar(plugin) -> str | None:
    m = getattr(plugin, "manifesto", None)
    if not isinstance(m, Manifesto):
        return "objeto PLUGIN sem manifesto válido (opuscore_core.contratos.plugin.Manifesto)"
    if m.contrato_plugin not in CONTRATOS_SUPORTADOS["plugin"]:
        return f"contrato de plugin v{m.contrato_plugin} não suportado (suportados: {sorted(CONTRATOS_SUPORTADOS['plugin'])})"
    if m.web and m.contrato_web not in CONTRATOS_SUPORTADOS["web"]:
        return f"contrato web v{m.contrato_web} não suportado"
    return None


def carregar(filtro: set[str] | None = None, extras: list | None = None) -> Registro:
    reg, vistos = Registro(), set()
    candidatos = [(ep.name, ep) for ep in entry_points(group=GRUPO)]
    for nome, ep in sorted(candidatos, key=lambda x: x[0]):
        if filtro and nome not in filtro:
            continue
        try:
            plugin = ep.load()
        except Exception as e:  # noqa: BLE001 - isola o plugin com erro
            reg.erros.append({"key": nome, "erro": f"falha ao carregar: {type(e).__name__}: {e}"})
            log.error("Plugin %s não carregou: %s", nome, e)
            continue
        _adicionar(reg, vistos, nome, plugin)
    for plugin in extras or []:
        _adicionar(reg, vistos, plugin.manifesto.key, plugin)
    return reg


def _adicionar(reg: Registro, vistos: set, nome: str, plugin) -> None:
    erro = validar(plugin)
    if not erro and plugin.manifesto.key in vistos:
        erro = f"key duplicada: {plugin.manifesto.key}"
    if erro:
        reg.erros.append({"key": nome, "erro": erro})
        log.error("Plugin %s recusado: %s", nome, erro)
        return
    vistos.add(plugin.manifesto.key)
    reg.plugins.append(plugin)
