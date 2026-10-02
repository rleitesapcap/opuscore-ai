"""Configuração dos conectores: seções `sap`, `safety` e `conectores` do config.yaml."""
from __future__ import annotations

from typing import Literal

from opuscore_core.sdk.config import secao
from pydantic import BaseModel, Field


class SapSystemCfg(BaseModel):
    base_url: str
    client: str
    auth: Literal["basic", "bearer"] = "basic"
    user: str = ""
    password: str = ""
    token: str = ""
    verify_ssl: bool = True
    read_only: bool = True  # TRAVA: nunca altera/exclui objetos por padrão
    allowed_packages: list[str] = Field(default_factory=list)


class SapCfg(BaseModel):
    default: str
    systems: dict[str, SapSystemCfg]


class SafetyCfg(BaseModel):
    audit_log_path: str = "data/audit/opuscore-audit.jsonl"
    require_transport: bool = True


# Tabelas de configuração que podem ser lidas mesmo quando a classe de entrega não
# pôde ser confirmada (releases antigos). É CONFIGURAÇÃO dos Conectores: nunca vem
# na chamada do consultor (senão qualquer chamada contornaria a trava).
TABELAS_SEM_CLASSE_PADRAO = ["T001W", "T001L", "T024E", "T024", "T161", "T161T", "T134", "T134T",
                             "T023", "T023T", "T156", "T156T", "T16FG", "T16FS", "T16FT", "T001K", "T169G"]


class ConectoresCfg(BaseModel):
    habilitados: list[str] = Field(default_factory=lambda: ["sap_adt"])
    tabelas_config_sem_classe: list[str] = Field(default_factory=lambda: list(TABELAS_SEM_CLASSE_PADRAO))


def config_sap() -> SapCfg:
    return SapCfg.model_validate(secao("sap"))


def config_seguranca() -> SafetyCfg:
    return SafetyCfg.model_validate(secao("safety", {}) or {})


def config_conectores() -> ConectoresCfg:
    return ConectoresCfg.model_validate(secao("conectores", {}) or {})
