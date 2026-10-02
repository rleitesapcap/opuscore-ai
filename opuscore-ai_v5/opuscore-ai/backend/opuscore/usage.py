"""Uso de tokens e estimativa de custo das chamadas de IA.

Os preços vêm da tabela de prompt caching da documentação da Claude Platform
(https://platform.claude.com/docs/en/build-with-claude/prompt-caching), em US$
por milhão de tokens. O custo calculado aqui é uma ESTIMATIVA: a fatura oficial
é a do console da Anthropic (ou do gateway usado).

Formato normalizado de uso (dict):
  input           tokens de entrada NÃO cacheados
  cache_read      tokens lidos do cache
  cache_creation  tokens gravados no cache
  output          tokens de saída
"""
from __future__ import annotations

# modelo (prefixo) -> (entrada, saída, gravação cache 5 min, leitura cache)
PRECOS = {
    "claude-fable-5-1": (10.0, 50.0, 12.50, 0.25),
    "claude-mythos-5-1": (10.0, 50.0, 12.50, 0.25),
    "claude-opus-5-5": (4.0, 20.0, 5.00, 0.20),
    "claude-sonnet-5": (2.0, 10.0, 2.50, 0.20),
    "claude-haiku-4-5": (1.0, 5.0, 1.25, 0.10),
    "claude-opus-5": (5.0, 25.0, 6.25, 0.50),
    "claude-opus-4": (5.0, 25.0, 6.25, 0.50),
    "claude-sonnet-4": (3.0, 15.0, 3.75, 0.30),
}

VAZIO = {"input": 0, "cache_read": 0, "cache_creation": 0, "output": 0}


def _preco(modelo: str | None):
    m = (modelo or "").lower()
    # prefixo mais longo primeiro (claude-opus-5-5 antes de claude-opus-5)
    for chave in sorted(PRECOS, key=len, reverse=True):
        if chave in m:
            return PRECOS[chave]
    return None


def de_anthropic(u: dict | None) -> dict:
    """Campos crus da API da Anthropic (usage da resposta)."""
    u = u or {}
    return {"input": int(u.get("input_tokens") or 0),
            "cache_read": int(u.get("cache_read_input_tokens") or 0),
            "cache_creation": int(u.get("cache_creation_input_tokens") or 0),
            "output": int(u.get("output_tokens") or 0)}


def de_openai(u: dict | None) -> dict:
    """Formato OpenAI-compatível (gateways): cached_tokens já está dentro de prompt_tokens."""
    u = u or {}
    cached = int(((u.get("prompt_tokens_details") or {}).get("cached_tokens")) or 0)
    return {"input": max(int(u.get("prompt_tokens") or 0) - cached, 0), "cache_read": cached,
            "cache_creation": 0, "output": int(u.get("completion_tokens") or 0)}


def somar(usos: list[dict]) -> dict:
    tot = dict(VAZIO)
    for u in usos:
        for k in tot:
            tot[k] += int(u.get(k) or 0)
    return tot


def custo_usd(uso: dict, modelo: str | None) -> float | None:
    p = _preco(modelo)
    if not p:
        return None
    ent, sai, grav, leit = p
    return round((uso.get("input", 0) * ent + uso.get("output", 0) * sai +
                  uso.get("cache_creation", 0) * grav + uso.get("cache_read", 0) * leit) / 1_000_000, 6)


def resumo(usos: list[dict], modelo: str | None) -> dict:
    """Totais + custo estimado + economia obtida com o cache."""
    tot = somar(usos)
    c = custo_usd(tot, modelo)
    sem_cache = None
    p = _preco(modelo)
    if p:  # quanto teria custado se tudo que foi lido do cache fosse entrada normal
        sem_cache = custo_usd({**tot, "input": tot["input"] + tot["cache_read"] + tot["cache_creation"],
                               "cache_read": 0, "cache_creation": 0}, modelo)
    return {"chamadas": len(usos), "tokens": tot, "modelo": modelo,
            "custo_estimado_usd": c,
            "economia_cache_usd": round(sem_cache - c, 6) if (c is not None and sem_cache is not None) else None,
            "observacao": "estimativa pela tabela pública de preços; a fatura oficial é a do console"}
