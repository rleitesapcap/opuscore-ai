"""Abstração de LLM. Um único contrato, três backends configuráveis.

- kind: "anthropic"          -> Claude (Messages API nativa)
- kind: "openai_compatible"  -> Grok (xAI), AIP corporativa, Ollama local, OpenAI

Trocar de provider é só mudar `llm.default` no config.yaml.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from .settings import LLMProviderCfg, get_settings


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMProvider(Protocol):
    async def complete(self, messages: list[Message]) -> str: ...


class AnthropicProvider:
    def __init__(self, cfg: LLMProviderCfg):
        self.cfg = cfg

    async def complete(self, messages: list[Message]) -> str:
        system = "\n\n".join(m.content for m in messages if m.role == "system")
        turns = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant")
        ]
        payload = {
            "model": self.cfg.model,
            "max_tokens": self.cfg.max_tokens,
            "temperature": self.cfg.temperature,
            "messages": turns,
        }
        if system:
            payload["system"] = system
        headers = {
            "x-api-key": self.cfg.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                f"{self.cfg.base_url}/v1/messages", json=payload, headers=headers
            )
            r.raise_for_status()
            data = r.json()
        return "".join(
            blk.get("text", "") for blk in data.get("content", []) if blk.get("type") == "text"
        )


class OpenAICompatibleProvider:
    """Serve Grok (xAI), Ollama, AIP e OpenAI — todos falam /chat/completions."""

    def __init__(self, cfg: LLMProviderCfg):
        self.cfg = cfg

    async def complete(self, messages: list[Message]) -> str:
        payload = {
            "model": self.cfg.model,
            "max_tokens": self.cfg.max_tokens,
            "temperature": self.cfg.temperature,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        headers = {"content-type": "application/json"}
        if self.cfg.api_key:
            headers["Authorization"] = f"Bearer {self.cfg.api_key}"
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(
                f"{self.cfg.base_url}/chat/completions", json=payload, headers=headers
            )
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]


def build_provider(name: str | None = None) -> LLMProvider:
    s = get_settings()
    key = name or s.llm.default
    cfg = s.llm.providers[key]
    if cfg.kind == "anthropic":
        return AnthropicProvider(cfg)
    return OpenAICompatibleProvider(cfg)
