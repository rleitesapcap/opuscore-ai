"""Cliente MCP do host: sobe o opuscore-sap-mcp por stdio, lista e chama ferramentas.

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
        self.args = ["-m", "opuscore.mcp_server"]
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
