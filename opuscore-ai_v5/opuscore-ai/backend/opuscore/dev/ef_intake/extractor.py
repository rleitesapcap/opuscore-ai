"""Chamada à IA e validação do JSON de saída (com uma nova tentativa guiada)."""
from __future__ import annotations

import importlib.util
import json
import os
import re
from pathlib import Path

from pydantic import ValidationError

from .prompt import SYSTEM_PROMPT
from .schema import ExtractionResult

_ET_DIR = Path(__file__).resolve().parents[1] / "et"
_BACKEND_ENV = Path(__file__).resolve().parents[3] / ".env"


def load_env() -> str | None:
    """Carrega o backend/.env (a CLI roda sem o settings.py da API).
    Não sobrescreve variáveis já definidas no ambiente."""
    if not _BACKEND_ENV.is_file():
        return None
    try:
        from dotenv import load_dotenv
        load_dotenv(_BACKEND_ENV, override=False)
        return str(_BACKEND_ENV)
    except ImportError:
        return None


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
    """Mesma camada de IA dos motores (llm_providers.py, controlada por LLM_PROVIDER)."""
    import sys

    load_env()
    nome = "opuscore_llm_providers"
    mod = sys.modules.get(nome)
    if mod is None:
        spec = importlib.util.spec_from_file_location(nome, _ET_DIR / "llm_providers.py")
        mod = importlib.util.module_from_spec(spec)
        # o módulo precisa estar em sys.modules ANTES de executar: o @dataclass
        # (com "from __future__ import annotations") procura o módulo ali
        sys.modules[nome] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(nome, None)
            raise
    over = {"max_tokens": max_tokens or int(os.environ.get("EF_INTAKE_MAX_TOKENS", "16000"))}
    modelo, _ = resolve_model()
    if modelo:
        over["model"] = modelo
    return mod.get_provider(os.environ.get("LLM_PROVIDER", "capgemini"), **over)


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
