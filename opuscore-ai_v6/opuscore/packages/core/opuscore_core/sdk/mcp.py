"""Cliente MCP: sobe o servidor dos Conectores por stdio, lista e chama ferramentas.

Mantém uma sessão persistente (aberta no startup do backend, fechada no shutdown).
"""
from __future__ import annotations

import os
import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    def __init__(self, cwd: str | None = None, env: dict | None = None):
        self.command = sys.executable
        self.args = ["-m", os.environ.get("OPUSCORE_MCP_MODULO", "opuscore_connectors.servidor")]
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self.session: ClientSession | None = None
        self._stack: AsyncExitStack | None = None
        self.tools_for_llm: list[dict] = []

    async def start(self) -> None:
        self._stack = AsyncExitStack()
        params = StdioServerParameters(
            command=self.command, args=self.args, cwd=self.cwd, env=self.env
        )
        read, write = await self._stack.enter_async_context(stdio_client(params))
        self.session = await self._stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        listed = await self.session.list_tools()
        self.tools_for_llm = [
            {"name": t.name, "description": t.description or "", "input_schema": t.inputSchema}
            for t in listed.tools
        ]

    async def call_tool(self, name: str, args: dict | None = None) -> str:
        assert self.session is not None, "MCP session não iniciada"
        res = await self.session.call_tool(name, args or {})
        parts = [getattr(c, "text", "") for c in res.content if getattr(c, "text", "")]
        return "\n".join(parts)

    async def stop(self) -> None:
        if self._stack:
            await self._stack.aclose()
            self._stack = None
            self.session = None


class ClienteMCPJson:
    """Fachada do ctx.mcp: decodifica o JSON e converte {"error"} em ErroOpus."""

    def __init__(self, cliente: "MCPClient | None"):
        self._c = cliente

    @property
    def ferramentas(self) -> list[dict]:
        return self._c.tools_for_llm if self._c else []

    @property
    def bruto(self) -> "MCPClient | None":
        return self._c

    def _exigir(self) -> "MCPClient":
        from ..contratos.erros import indisponivel
        if self._c is None:
            raise indisponivel("Servidor MCP dos Conectores indisponível. Confira o config.yaml e o log do início.")
        return self._c

    async def chamar_texto(self, ferramenta: str, **args) -> str:
        return await self._exigir().call_tool(ferramenta, args)

    async def chamar(self, ferramenta: str, **args):
        import json
        from ..contratos.erros import falha_externa, nao_encontrado
        bruto = await self.chamar_texto(ferramenta, **args)
        try:
            dados = json.loads(bruto)
        except json.JSONDecodeError:
            raise falha_externa(f"Resposta inválida da ferramenta {ferramenta}: {bruto[:200]}")
        if isinstance(dados, dict) and dados.get("error"):
            erro = str(dados["error"])
            raise (nao_encontrado(erro) if "não encontrad" in erro.lower() else falha_externa(erro))
        return dados
