"""Configuração única do OPUSCORE (config/config.yaml + config/.env).

Ordem de busca:
- raiz do projeto: OPUSCORE_HOME, senão o diretório atual;
- .env: OPUSCORE_ENV, senão <raiz>/config/.env, senão <raiz>/.env;
- config.yaml: OPUSCORE_CONFIG, senão <raiz>/config/config.yaml, senão <raiz>/config.yaml;
- dados (banco, uploads, artefatos, cache): OPUSCORE_DATA, senão <raiz>/data.
`${VAR}` dentro do YAML é trocado pelo valor do ambiente.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

_ENV = re.compile(r"\$\{([A-Z0-9_]+)\}")


def raiz() -> Path:
    return Path(os.environ.get("OPUSCORE_HOME") or os.getcwd()).resolve()


def carregar_env() -> str | None:
    candidatos = [os.environ.get("OPUSCORE_ENV"), raiz() / "config" / ".env", raiz() / ".env"]
    for c in candidatos:
        if c and Path(c).is_file():
            try:
                from dotenv import load_dotenv
                load_dotenv(c, override=False)
                return str(c)
            except ImportError:  # pragma: no cover
                return None
    return None


carregar_env()


def caminho_config() -> Path:
    if os.environ.get("OPUSCORE_CONFIG"):
        return Path(os.environ["OPUSCORE_CONFIG"])
    for c in (raiz() / "config" / "config.yaml", raiz() / "config.yaml"):
        if c.is_file():
            return c
    return raiz() / "config" / "config.yaml"


def diretorio_config() -> Path:
    return caminho_config().parent


def diretorio_dados() -> Path:
    d = Path(os.environ.get("OPUSCORE_DATA") or (raiz() / "data"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _expandir(v):
    if isinstance(v, str):
        return _ENV.sub(lambda m: os.environ.get(m.group(1), ""), v)
    if isinstance(v, dict):
        return {k: _expandir(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_expandir(x) for x in v]
    return v


@lru_cache
def carregar_yaml() -> dict:
    p = caminho_config()
    if not p.is_file():
        raise FileNotFoundError(f"Config não encontrada: {p}. Copie config/config.example.yaml "
                                "para config/config.yaml.")
    return _expandir(yaml.safe_load(p.read_text(encoding="utf-8")) or {})


def secao(nome: str, padrao=None):
    return carregar_yaml().get(nome, padrao)


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
    temperature: float | None = 0.2     # None = não enviar (ex.: claude-opus-5-5)


class LLMCfg(BaseModel):
    default: str
    providers: dict[str, LLMProviderCfg]


def config_app() -> AppCfg:
    return AppCfg.model_validate(secao("app", {}) or {})


def config_ia() -> LLMCfg:
    return LLMCfg.model_validate(secao("llm"))
