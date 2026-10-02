"""Camada de LLM plugável — agora com tool calling (function calling).

Contrato neutro de mensagens (o host monta, os providers traduzem):
  {"role":"system","content":str}
  {"role":"user","content":str}
  {"role":"assistant","content":str,"tool_calls":[ToolCall,...]}
  {"role":"tool","tool_call_id":str,"name":str,"content":str}

- kind "anthropic"          -> Claude (Messages API, blocos tool_use/tool_result)
- kind "openai_compatible"  -> Grok/AIP/Ollama/OpenAI (tool_calls / role=tool)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol

import httpx

from .config import LLMProviderCfg, config_ia


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class AssistantTurn:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict = field(default_factory=dict)   # uso normalizado (opuscore.usage)


def _prompt_cache_on() -> bool:
    """Prompt caching da Anthropic (modo automático). Desligue com PROMPT_CACHE=off."""
    import os
    return os.environ.get("PROMPT_CACHE", "on").strip().lower() not in ("off", "0", "false", "no")


def _temperatura(cfg) -> dict:
    """Temperatura opcional: LLM_TEMPERATURE=off (ou temperature: null no YAML) omite o
    parâmetro, exigido por modelos que o recusam (ex.: claude-opus-5-5)."""
    import os
    env = os.environ.get("LLM_TEMPERATURE", "").strip().lower()
    if env in ("off", "none", "omit"):
        return {}
    if env:
        try:
            return {"temperature": float(env)}
        except ValueError:
            pass
    return {} if cfg.temperature is None else {"temperature": cfg.temperature}


class LLMProvider(Protocol):
    async def complete(self, messages: list[Message]) -> str: ...
    async def complete_with_tools(
        self, messages: list[dict], tools: list[dict]
    ) -> AssistantTurn: ...


class AnthropicProvider:
    def __init__(self, cfg: LLMProviderCfg):
        self.cfg = cfg

    def _headers(self):
        return {
            "x-api-key": self.cfg.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

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
            **_temperatura(self.cfg),
            "messages": turns,
        }
        if system:
            payload["system"] = system
        if _prompt_cache_on():
            payload["cache_control"] = {"type": "ephemeral"}
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{self.cfg.base_url}/v1/messages", json=payload, headers=self._headers())
            r.raise_for_status()
            data = r.json()
        from .uso import de_anthropic
        self.last_usage = de_anthropic(data.get("usage"))
        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")

    def _to_anthropic(self, messages: list[dict]) -> list[dict]:
        out: list[dict] = []
        for m in messages:
            role = m["role"]
            if role == "system":
                continue
            if role == "user":
                out.append({"role": "user", "content": m["content"]})
            elif role == "assistant":
                content = []
                if m.get("content"):
                    content.append({"type": "text", "text": m["content"]})
                for tc in m.get("tool_calls", []):
                    content.append({"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.input})
                out.append({"role": "assistant", "content": content or ""})
            elif role == "tool":
                block = {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}
                # resultados de tool consecutivos vão no MESMO turno user
                if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                    out[-1]["content"].append(block)
                else:
                    out.append({"role": "user", "content": [block]})
        return out

    async def complete_with_tools(self, messages: list[dict], tools: list[dict]) -> AssistantTurn:
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        payload = {
            "model": self.cfg.model,
            "max_tokens": self.cfg.max_tokens,
            **_temperatura(self.cfg),
            "messages": self._to_anthropic(messages),
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = [
                {"name": t["name"], "description": t["description"], "input_schema": t["input_schema"]}
                for t in tools
            ]
        # Modo automático: o ponto de cache vai no último bloco e avança a cada passo do
        # laço (ferramenta -> resultado -> nova chamada). Sistema + ferramentas + histórico
        # já enviados são relidos do cache nas chamadas seguintes.
        if _prompt_cache_on():
            payload["cache_control"] = {"type": "ephemeral"}
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{self.cfg.base_url}/v1/messages", json=payload, headers=self._headers())
            r.raise_for_status()
            data = r.json()
        from .uso import de_anthropic
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        calls = [
            ToolCall(b["id"], b["name"], b.get("input", {}))
            for b in data.get("content", [])
            if b.get("type") == "tool_use"
        ]
        return AssistantTurn(text=text, tool_calls=calls, usage=de_anthropic(data.get("usage")))


class OpenAICompatibleProvider:
    """Serve Grok (xAI), Ollama, AIP e OpenAI — todos falam /chat/completions."""

    def __init__(self, cfg: LLMProviderCfg):
        self.cfg = cfg

    def _headers(self):
        h = {"content-type": "application/json"}
        if self.cfg.api_key:
            h["Authorization"] = f"Bearer {self.cfg.api_key}"
        return h

    async def complete(self, messages: list[Message]) -> str:
        payload = {
            "model": self.cfg.model,
            "max_tokens": self.cfg.max_tokens,
            **_temperatura(self.cfg),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{self.cfg.base_url}/chat/completions", json=payload, headers=self._headers())
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"]

    def _to_openai(self, messages: list[dict]) -> list[dict]:
        out: list[dict] = []
        for m in messages:
            role = m["role"]
            if role in ("system", "user"):
                out.append({"role": role, "content": m["content"]})
            elif role == "assistant":
                o = {"role": "assistant", "content": m.get("content") or None}
                if m.get("tool_calls"):
                    o["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.name, "arguments": json.dumps(tc.input, ensure_ascii=False)},
                        }
                        for tc in m["tool_calls"]
                    ]
                out.append(o)
            elif role == "tool":
                out.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"]})
        return out

    async def complete_with_tools(self, messages: list[dict], tools: list[dict]) -> AssistantTurn:
        payload = {
            "model": self.cfg.model,
            "max_tokens": self.cfg.max_tokens,
            **_temperatura(self.cfg),
            "messages": self._to_openai(messages),
        }
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["input_schema"],
                    },
                }
                for t in tools
            ]
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{self.cfg.base_url}/chat/completions", json=payload, headers=self._headers())
            r.raise_for_status()
            data = r.json()
        from .uso import de_openai
        uso = de_openai(data.get("usage"))
        msg = data["choices"][0]["message"]
        text = msg.get("content") or ""
        calls = []
        for tc in msg.get("tool_calls") or []:
            fn = tc.get("function", {})
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append(ToolCall(tc.get("id", ""), fn.get("name", ""), args))
        return AssistantTurn(text=text, tool_calls=calls, usage=uso)


def build_provider(name: str | None = None) -> LLMProvider:
    cfg_ia = config_ia()
    key = name or cfg_ia.default
    cfg = cfg_ia.providers[key]
    if cfg.kind == "anthropic":
        return AnthropicProvider(cfg)
    return OpenAICompatibleProvider(cfg)
