"""Chamada à IA e validação do JSON de saída (com uma nova tentativa guiada)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from pydantic import ValidationError

from .prompt import SYSTEM_PROMPT
from .schema import ExtractionResult

def load_env() -> str | None:
    """Carrega o .env do projeto (config/.env). Não sobrescreve variáveis já definidas."""
    from opuscore_core.sdk.config import carregar_env
    return carregar_env()


MODEL_VARS = ("EF_INTAKE_MODEL", "LLM_MODEL", "LLM_MODEL_MAIN")


def resolve_model() -> tuple[str | None, str | None]:
    """(modelo, variável de origem). Prioridade: EF_INTAKE_MODEL > LLM_MODEL > LLM_MODEL_MAIN."""
    for var in MODEL_VARS:
        val = (os.environ.get(var) or "").strip()
        if val:
            return val, var
    return None, None


def provider_info() -> dict:
    modelo, origem = resolve_model()
    return {"provider": os.environ.get("LLM_PROVIDER", "capgemini"),
            "modelo": f"{modelo} (de {origem})" if modelo else
                      f"(padrão do provedor — nenhuma de {', '.join(MODEL_VARS)} definida)",
            "max_tokens": os.environ.get("EF_INTAKE_MAX_TOKENS", "16000")}


class ExtractionError(RuntimeError):
    pass


def load_provider(max_tokens: int | None = None):
    """Provedor síncrono do Core (opuscore_core.sdk.provedores), escolhido por LLM_PROVIDER."""
    from opuscore_core.sdk.provedores import get_provider

    load_env()
    over = {"max_tokens": max_tokens or int(os.environ.get("EF_INTAKE_MAX_TOKENS", "16000"))}
    modelo, _ = resolve_model()
    if modelo:
        over["model"] = modelo
    return get_provider(os.environ.get("LLM_PROVIDER", "capgemini"), **over)


def _parse_json(text: str) -> dict:
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b <= a:
        raise ValueError("resposta sem objeto JSON")
    return json.loads(t[a:b + 1])


def extract(provider, user_message: str, retries: int = 1, *, system: str = SYSTEM_PROMPT,
            model_cls=ExtractionResult):
    """Devolve (resultado validado, texto bruto da última resposta)."""
    turns = [{"role": "user", "content": user_message}]
    last_err = ""
    for tentativa in range(retries + 1):
        try:
            resp = provider.invoke(system, turns)
        except Exception as e:  # noqa: BLE001 - erro do provedor (auth, modelo, rede)
            msg = str(e)
            dica = ""
            if "not_found" in msg and "model" in msg:
                dica = (" O modelo não existe para esta conta: defina LLM_MODEL no backend/.env "
                        "com um modelo disponível (liste em /v1/models).")
            elif "401" in msg or "authentication" in msg.lower():
                dica = " Chave de API inválida ou ausente no backend/.env."
            elif "temperature" in msg:
                dica = " Defina LLM_TEMPERATURE=off no backend/.env."
            raise ExtractionError(f"Falha ao chamar a IA ({type(e).__name__}): {msg[:400]}{dica}") from e
        if getattr(resp, "finish_reason", "") == "length":
            raise ExtractionError(
                "A resposta da IA foi cortada por limite de tokens. Aumente "
                "EF_INTAKE_MAX_TOKENS no .env (ex.: 32000) e tente novamente.")
        try:
            return model_cls.model_validate(_parse_json(resp.text)), resp.text
        except (ValueError, json.JSONDecodeError, ValidationError) as e:
            last_err = str(e)[:3000]
            turns += [
                {"role": "assistant", "content": resp.text},
                {"role": "user", "content":
                    "O JSON não é válido para o esquema. Erros:\n" + last_err +
                    "\nResponda novamente somente com o JSON completo e corrigido."},
            ]
    raise ExtractionError(f"A IA não devolveu um JSON válido após {retries + 1} tentativas: {last_err}")
