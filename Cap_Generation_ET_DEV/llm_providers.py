# -*- coding: utf-8 -*-
"""
===============================================================================
 llm_providers.py  —  A TOMADA UNIVERSAL PARA A INTELIGÊNCIA ARTIFICIAL
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Ele é o "adaptador de tomada" que permite a solução falar com DIFERENTES
    fornecedores de Inteligência Artificial, sem que o resto do programa precise
    saber os detalhes de cada um.


OS TRÊS FORNECEDORES SUPORTADOS:
    - "capgemini"   : o servidor de IA da Capgemini (o usado no projeto).
                      Precisa de: LLM_API_KEY + WORKSPACE_ID.
    - "anthropic"   : a IA da Anthropic direto (paga por uso).
                      Precisa de: ANTHROPIC_API_KEY.
    - "claude_code" : o Claude Code rodando pela linha de comando.
                      Usa o login da sua assinatura do Claude Code.

    Você escolhe qual usar pela variável de ambiente LLM_PROVIDER
    (o padrão é "capgemini").

UMA COISA IMPORTANTE QUE ELE FAZ:
    VALIDAR o acesso ANTES de começar. Assim, se a chave estiver errada ou o
    servidor fora do ar, você descobre logo — e não no meio de um processamento
    demorado. Para testar sozinho (sem rodar a remediação):
        LLM_PROVIDER=capgemini python llm_providers.py
    (código de saída 0 = acesso OK; 1 = falhou)
===============================================================================
"""

from __future__ import annotations

import os
import sys
import json
import uuid
import shutil
import subprocess
from abc import ABC, abstractmethod       # para criar um "molde" (classe base) obrigatório
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# TIPOS DE DADOS NEUTROS
# (Estruturas simples para padronizar a resposta, sem depender de nenhuma
#  biblioteca específica de IA nesta camada.)
# =============================================================================
@dataclass
class ProviderResponse:
    """A resposta padronizada de uma chamada à IA (não importa o fornecedor)."""
    text: str                    # o texto que a IA respondeu
    finish_reason: str           # por que parou: "stop" (normal) | "length" (cortou) | outro
    raw: Optional[dict] = None   # dados extras do fornecedor, se houver


@dataclass
class ValidationResult:
    """O resultado de um teste de acesso a um fornecedor."""
    ok: bool                     # deu certo?
    provider: str                # qual fornecedor
    detail: str = ""             # detalhe legível (o que aconteceu)

    def __str__(self) -> str:
        mark = "✓ OK  " if self.ok else "✗ FAIL"
        return f"[{mark}] provider='{self.provider}' — {self.detail}"


# Uma "turn" (rodada de conversa) é um dicionário:
#   {"role": "user"|"assistant", "content": texto}
# A instrução de sistema é passada à parte (cada fornecedor a coloca num lugar).


# =============================================================================
# O MOLDE (classe base): tudo que um fornecedor PRECISA saber fazer
# =============================================================================
class LLMProvider(ABC):
    name: str = "base"

    # Modelos que RECUSAM o parâmetro "temperature" (as versões Claude mais novas).
    # Para esses, o parâmetro é omitido automaticamente do pedido.
    _NO_TEMPERATURE = ("sonnet-5", "opus-4", "haiku-4-5", "mythos", "fable")

    def __init__(self, model: str, max_tokens: int = 8192,
                 temperature: Optional[float] = None):
        self.model = model
        self.max_tokens = max_tokens
        # A "temperatura" controla o quão criativa/aleatória é a IA. Para análise
        # de código queremos resultados PREVISÍVEIS (temperatura 0). Regra:
        #   - modelo aceita temperatura  -> 0.0 (determinístico)
        #   - modelo recusa temperatura  -> omite (não envia nada)
        # Dá para forçar pela variável LLM_TEMPERATURE ('off' para omitir, ou um número).
        if temperature is None:
            env = os.getenv("LLM_TEMPERATURE", "").strip().lower()
            if env in ("off", "none", "omit"):
                temperature = -1.0            # negativo => será omitido lá na frente
            elif env:
                try:
                    temperature = float(env)
                except ValueError:
                    temperature = 0.0
            elif any(tag in model.lower() for tag in self._NO_TEMPERATURE):
                temperature = -1.0            # modelo recusa => omite
            else:
                temperature = 0.0             # padrão determinístico
        self.temperature = temperature
        self.session_id: Optional[str] = None

    def new_session(self) -> str:
        """Começa uma sessão nova (uma por arquivo). Padrão: um id aleatório."""
        self.session_id = str(uuid.uuid4())
        return self.session_id

    def describe(self) -> dict:
        """Informações do fornecedor, para escrever no cabeçalho do arquivo de saída."""
        return {"provider": self.name, "model": self.model,
                "session": self.session_id or "-"}

    # As duas funções abaixo são OBRIGATÓRIAS: todo fornecedor precisa ter as suas.
    @abstractmethod
    def validate(self) -> ValidationResult:
        """Confere se este fornecedor está acessível e autenticado."""

    @abstractmethod
    def invoke(self, system: str, turns: list[dict]) -> ProviderResponse:
        """Envia um pedido e devolve a resposta."""


# =============================================================================
# FORNECEDOR 1 — Capgemini Generative Engine (o usado no projeto)
# =============================================================================
class CapgeminiProvider(LLMProvider):
    name = "capgemini"

    def __init__(self,
                 model: str = "us.anthropic.claude-sonnet-4-20250514-v1:0",
                 max_tokens: int = 8192,
                 temperature: Optional[float] = None,
                 base_url: str = "https://openai.generative.engine.capgemini.com/v1"):
        super().__init__(model, max_tokens, temperature)
        self.base_url = base_url
        # Lê as credenciais do ambiente (.env): a chave e o id do "workspace"
        # (que também dá acesso à base de conhecimento/RAG no servidor).
        self.api_key = os.getenv("LLM_API_KEY")
        self.workspace_id = os.getenv("WORKSPACE_ID")

    def _make_llm(self, max_tokens: Optional[int] = None):
        """Monta a conexão de fato com o servidor Capgemini."""
        # Importa só quando precisa (assim este fornecedor é opcional).
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError("langchain-openai not installed "
                              "(pip install langchain-openai)") from e
        from langchain_core.messages import HumanMessage  # noqa: F401
        kwargs = dict(
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key,
            max_tokens=max_tokens or self.max_tokens,
            default_headers={
                # O "workspace-id" é o que liga o pedido à base de conhecimento.
                "workspace-id": self.workspace_id or "",
                "session-id": self.session_id or str(uuid.uuid4()),
            },
        )
        # Só envia a temperatura quando habilitada (>= 0); alguns modelos recusam.
        if self.temperature is not None and self.temperature >= 0:
            kwargs["temperature"] = self.temperature
        return ChatOpenAI(**kwargs)

    def describe(self) -> dict:
        d = super().describe()
        d["workspace_id"] = self.workspace_id or "-"
        return d

    def validate(self) -> ValidationResult:
        """Testa o acesso: confere as credenciais e faz uma chamadinha de teste."""
        if not self.api_key:
            return ValidationResult(False, self.name, "LLM_API_KEY is not set")
        if not self.workspace_id:
            return ValidationResult(False, self.name, "WORKSPACE_ID is not set")
        try:
            from langchain_core.messages import HumanMessage
            llm = self._make_llm(max_tokens=16)
            resp = llm.invoke([HumanMessage(content="reply with OK")])
            txt = _extract_text(resp.content).strip()
            if not txt:
                return ValidationResult(False, self.name,
                                        "endpoint reachable but returned empty content")
            return ValidationResult(True, self.name,
                                    f"endpoint reachable, workspace accepted, sample='{txt[:40]}'")
        except Exception as e:
            return ValidationResult(False, self.name, f"call failed: {type(e).__name__}: {e}")

    def invoke(self, system: str, turns: list[dict]) -> ProviderResponse:
        """Envia o pedido real à IA e devolve a resposta padronizada."""
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        # Monta a conversa: instrução de sistema + as rodadas (usuário/assistente).
        msgs: list = [SystemMessage(content=system)]
        for t in turns:
            if t["role"] == "assistant":
                msgs.append(AIMessage(content=t["content"]))
            else:
                msgs.append(HumanMessage(content=t["content"]))
        llm = self._make_llm()
        resp = llm.invoke(msgs)
        meta = getattr(resp, "response_metadata", {}) or {}
        fr = _normalize_finish_reason(meta.get("finish_reason") or meta.get("stop_reason"))
        return ProviderResponse(text=_extract_text(resp.content), finish_reason=fr, raw=meta)


# =============================================================================
# FORNECEDOR 2 — Anthropic API direto (paga por uso)
# =============================================================================
class AnthropicAPIProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-4-20250514", max_tokens: int = 8192,
                 temperature: Optional[float] = None):
        super().__init__(model, max_tokens, temperature)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def _make_llm(self, max_tokens: Optional[int] = None):
        """Monta a conexão com a API da Anthropic."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            raise ImportError("langchain-anthropic not installed "
                              "(pip install langchain-anthropic)") from e
        kwargs = dict(
            model=self.model,
            api_key=self.api_key,
            max_tokens=max_tokens or self.max_tokens,
        )
        # Modelos novos (ex.: claude-sonnet-5) recusam "temperature". Só envia
        # quando habilitada (>= 0). Use LLM_TEMPERATURE=off para omitir de vez.
        if self.temperature is not None and self.temperature >= 0:
            kwargs["temperature"] = self.temperature
        return ChatAnthropic(**kwargs)

    def validate(self) -> ValidationResult:
        """Testa o acesso à API da Anthropic."""
        if not self.api_key:
            return ValidationResult(False, self.name, "ANTHROPIC_API_KEY is not set")
        try:
            from langchain_core.messages import HumanMessage
            llm = self._make_llm(max_tokens=16)
            resp = llm.invoke([HumanMessage(content="reply with OK")])
            txt = _extract_text(resp.content).strip()
            if not txt:
                return ValidationResult(False, self.name,
                                        "API reachable but returned empty content")
            return ValidationResult(True, self.name,
                                    f"API key valid, model responded, sample='{txt[:40]}'")
        except Exception as e:
            return ValidationResult(False, self.name, f"call failed: {type(e).__name__}: {e}")

    def invoke(self, system: str, turns: list[dict]) -> ProviderResponse:
        """Envia o pedido à API da Anthropic e devolve a resposta padronizada."""
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        msgs: list = [SystemMessage(content=system)]
        for t in turns:
            if t["role"] == "assistant":
                msgs.append(AIMessage(content=t["content"]))
            else:
                msgs.append(HumanMessage(content=t["content"]))
        llm = self._make_llm()
        resp = llm.invoke(msgs)
        meta = getattr(resp, "response_metadata", {}) or {}
        # A Anthropic devolve 'stop_reason' (end_turn / max_tokens).
        fr = _normalize_finish_reason(meta.get("stop_reason") or meta.get("finish_reason"))
        return ProviderResponse(text=_extract_text(resp.content), finish_reason=fr, raw=meta)


# =============================================================================
# FORNECEDOR 3 — Claude Code pela linha de comando
# =============================================================================
class ClaudeCodeProvider(LLMProvider):
    """
    Usa o comando `claude -p` (modo "print"). Sem --bare, ele autentica com o
    login da sua assinatura do Claude Code. A resposta é lida do formato JSON.

    Observação: o CLI roda o próprio "laço de agente" e devolve um resultado
    completo, então não ocorre o corte por limite de tokens como na API crua.
    Por isso, este fornecedor sempre reporta finish_reason="stop" e faz cada
    chamada de uma vez só. Para fontes muito grandes, use o corte por unidade
    (FORM/METHOD), em vez de depender de continuação.
    """
    name = "claude_code"

    def __init__(self,
                 model: str = "sonnet",
                 max_tokens: int = 8192,
                 timeout: int = 600,
                 extra_args: Optional[list[str]] = None):
        super().__init__(model, max_tokens)
        self.timeout = timeout
        # extra_args permite passar, por exemplo, ["--bare"] para execuções de CI.
        self.extra_args = extra_args or []

    def _binary(self) -> Optional[str]:
        """Descobre onde está o programa 'claude' instalado no computador."""
        return shutil.which("claude")

    def _run(self, prompt: str, system: Optional[str], timeout: int) -> dict:
        """Executa o comando 'claude -p ...' e devolve a resposta já lida do JSON."""
        cmd = ["claude", "-p", prompt, "--output-format", "json", "--model", self.model]
        if system:
            cmd += ["--append-system-prompt", system]
        cmd += self.extra_args
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (proc.stdout or "").strip()
        if not out:
            raise RuntimeError(
                f"empty stdout (exit={proc.returncode}); stderr: {(proc.stderr or '')[:300]}"
            )
        try:
            return json.loads(out)
        except json.JSONDecodeError as e:
            # Não veio JSON geralmente significa uma tela de login ou um erro.
            raise RuntimeError(f"non-JSON output (login needed?): {out[:300]}") from e

    def validate(self) -> ValidationResult:
        """Testa: confere se o 'claude' está instalado, a versão, e faz uma chamada real."""
        path = self._binary()
        if not path:
            return ValidationResult(False, self.name,
                                    "'claude' binary not found in PATH "
                                    "(install Claude Code and run `claude` to log in)")
        # confere a versão
        try:
            v = subprocess.run(["claude", "--version"],
                               capture_output=True, text=True, timeout=30)
            version = (v.stdout or v.stderr or "").strip()
        except Exception as e:
            return ValidationResult(False, self.name,
                                    f"'claude --version' failed: {type(e).__name__}: {e}")
        # teste real de autenticação: uma chamadinha em modo print
        try:
            data = self._run("reply with OK", system=None, timeout=min(self.timeout, 120))
            if data.get("is_error"):
                return ValidationResult(False, self.name,
                                        f"CLI returned error: {str(data.get('result'))[:120]}")
            cost = data.get("total_cost_usd")
            return ValidationResult(True, self.name,
                                    f"binary at {path}, version '{version}', auth OK"
                                    + (f", test cost=${cost}" if cost is not None else ""))
        except Exception as e:
            return ValidationResult(False, self.name,
                                    f"auth/invocation test failed: {type(e).__name__}: {e}")

    def invoke(self, system: str, turns: list[dict]) -> ProviderResponse:
        """Faz a chamada (de uma vez só — veja a explicação lá em cima)."""
        prompt = turns[-1]["content"]
        data = self._run(prompt, system=system, timeout=self.timeout)
        if data.get("is_error"):
            raise RuntimeError(f"claude -p error: {str(data.get('result'))[:200]}")
        # guarda o id de sessão do CLI para o cabeçalho de saída, se houver
        self.session_id = data.get("session_id", self.session_id)
        return ProviderResponse(text=data.get("result", ""), finish_reason="stop", raw=data)


# =============================================================================
# FUNÇÕES DE APOIO
# =============================================================================
def _extract_text(content) -> str:
    """Extrai o texto puro da resposta da IA.

    Modelos com "raciocínio estendido" (ex.: Sonnet 5) devolvem a resposta como
    uma LISTA de blocos, tipo [{'type':'thinking',...}, {'type':'text',...}].
    Aqui ficamos SÓ com os blocos de texto, para que o raciocínio interno nunca
    vaze para o resultado final."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    parts.append(block["text"])
                # blocos 'thinking' e 'redacted_thinking' são descartados.
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def _normalize_finish_reason(raw: Optional[str]) -> str:
    """Padroniza o "motivo de parada" da resposta, já que cada fornecedor usa
    nomes diferentes (OpenAI diz 'length'; Anthropic diz 'max_tokens'...)."""
    r = (raw or "").lower()
    if r in ("length", "max_tokens"):
        return "length"        # a resposta foi cortada por atingir o limite
    if r in ("stop", "end_turn", "stop_sequence"):
        return "stop"          # parou normalmente
    return r or "stop"


# =============================================================================
# A "FÁBRICA" — cria o fornecedor certo a partir do nome
# =============================================================================
# Vários apelidos aceitos para cada fornecedor (facilita a configuração).
_ALIASES = {
    "capgemini": "capgemini", "generative-engine": "capgemini", "ge": "capgemini",
    "anthropic": "anthropic", "anthropic-api": "anthropic", "api": "anthropic",
    "claude_code": "claude_code", "claude-code": "claude_code", "cli": "claude_code",
    "cc": "claude_code",
}


def get_provider(name: Optional[str] = None, **overrides) -> LLMProvider:
    """Recebe um nome (ou apelido) e devolve o fornecedor correspondente, já
    montado. É esta função que o resto da solução chama."""
    key = _ALIASES.get((name or "").lower().strip())
    if key == "capgemini":
        return CapgeminiProvider(**overrides)
    if key == "anthropic":
        return AnthropicAPIProvider(**overrides)
    if key == "claude_code":
        return ClaudeCodeProvider(**overrides)
    raise ValueError(
        f"unknown provider '{name}'. Use one of: "
        f"capgemini | anthropic | claude_code"
    )


# =============================================================================
# PONTO DE ENTRADA PARA TESTAR O ACESSO (rodando este arquivo sozinho)
# =============================================================================
def validate_provider(name: Optional[str] = None) -> ValidationResult:
    """Cria o fornecedor e testa o acesso a ele."""
    provider = get_provider(name)
    return provider.validate()


# Quando você roda:  LLM_PROVIDER=capgemini python llm_providers.py
if __name__ == "__main__":
    prov_name = os.getenv("LLM_PROVIDER", "capgemini")
    print(f"Validating LLM provider: '{prov_name}' ...")
    try:
        result = validate_provider(prov_name)
    except Exception as e:
        print(f"[✗ FAIL] provider='{prov_name}' — setup error: {type(e).__name__}: {e}")
        sys.exit(1)
    print(result)                      # imprime OK ou FAIL, com o detalhe