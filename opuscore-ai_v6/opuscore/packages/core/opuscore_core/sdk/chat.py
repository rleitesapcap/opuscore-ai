"""Laço do chat: orquestra a conversa. O LLM decide, chama ferramentas MCP (SAP), recebe a
evidência e responde. As ferramentas são somente-leitura — o laço não altera nada.
"""
from __future__ import annotations

import json

from dataclasses import dataclass, field

from .ia import LLMProvider
from .mcp import MCPClient


@dataclass
class ChatResult:
    reply: str = ""
    steps: list[dict] = field(default_factory=list)  # [{tool, input}] executados
    usos: list[dict] = field(default_factory=list)   # uso de tokens de cada chamada do laço

SQUAD_SYSTEM = """\
Você é o squad OPUSCORE-AI: especialistas SAP (Desenvolvedor ABAP, Consultores, \
Arquitetos) com acesso de LEITURA ao sistema do cliente via ferramentas MCP.

Regras:
- Você NUNCA altera ou exclui objetos. As ferramentas são somente-leitura.
- Seja evidence-based: para falar de um objeto, CHAME a ferramenta apropriada e \
baseie-se no que ela retornar. Nunca invente nome de objeto, campo, tabela ou SAP Note.
- Se uma ferramenta retornar erro, explique o erro ao usuário em vez de inventar dados.
- Ao analisar um objeto, inclua avaliação de Clean Core (uso de APIs liberadas, risco \
de upgrade) quando fizer sentido.
- Responda em pt-BR, técnico e direto.
- Tom: descontraído, como um colega de projeto conversando. Frases curtas, sem
  formalidade e sem juridiquês, sem gíria exagerada. A precisão técnica não muda:
  nomes de objetos, regras e riscos sempre exatos.
"""

async def run_chat(
    messages: list[dict], mcp: MCPClient, provider: LLMProvider, max_steps: int = 6
) -> ChatResult:
    """Laço: LLM -> (tool_calls -> MCP -> tool results) -> ... -> resposta final."""
    convo: list[dict] = [{"role": "system", "content": SQUAD_SYSTEM}] + messages
    steps: list[dict] = []
    turn = None
    usos: list[dict] = []
    for _ in range(max_steps):
        turn = await provider.complete_with_tools(convo, mcp.tools_for_llm)
        if turn.usage:
            usos.append(turn.usage)
        if not turn.tool_calls:
            return ChatResult(reply=turn.text, steps=steps, usos=usos)
        convo.append({"role": "assistant", "content": turn.text, "tool_calls": turn.tool_calls})
        for tc in turn.tool_calls:
            result = await mcp.call_tool(tc.name, tc.input)
            steps.append({"tool": tc.name, "input": tc.input})
            convo.append(
                {"role": "tool", "tool_call_id": tc.id, "name": tc.name, "content": result}
            )
    reply = (turn.text if turn else "") or "Limite de passos atingido sem resposta final."
    return ChatResult(reply=reply, steps=steps, usos=usos)
