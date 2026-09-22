"""Carrega config.yaml, expande ${VAR} do ambiente e valida com Pydantic."""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

try:  # .env é conveniência; ausência não quebra
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass

_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand_env(value):
    """Substitui ${VAR} pelos valores do ambiente, recursivamente."""
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda m: os.environ.get(m.group(1), ""), value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


class AppCfg(BaseModel):
    name: str = "OPUSCORE-AI"
    language: str = "pt-BR"
    host: str = "127.0.0.1"
    port: int = 8787


class LLMProviderCfg(BaseModel):
    kind: Literal["anthropic", "openai_compatible"]
    base_url: str
    model: str
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 0.2


class LLMCfg(BaseModel):
    default: str
    providers: dict[str, LLMProviderCfg]


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
    audit_log_path: str = "audit/opuscore-audit.jsonl"
    require_transport: bool = True


class Settings(BaseModel):
    app: AppCfg = AppCfg()
    llm: LLMCfg
    sap: SapCfg
    safety: SafetyCfg = SafetyCfg()


@lru_cache
def get_settings(path: str | None = None) -> Settings:
    cfg_path = Path(path or os.environ.get("OPUSCORE_CONFIG", "config.yaml"))
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Config não encontrada: {cfg_path}. Copie config.example.yaml para config.yaml."
        )
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return Settings.model_validate(_expand_env(raw))
