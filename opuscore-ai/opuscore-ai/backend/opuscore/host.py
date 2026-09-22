"""Host: orquestra a conversa. O LLM decide, chama ferramentas MCP (SAP), recebe a
evidência e responde. As ferramentas são somente-leitura — o laço não altera nada.
"""
from __future__ import annotations

import json

from .llm import LLMProvider, Message
from .mcp_client import MCPClient

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
"""

ABAP_REPORT_SYSTEM = """\
Você é o Desenvolvedor ABAP do OPUSCORE-AI. Monte um relatório técnico sobre o objeto \
usando SOMENTE a evidência fornecida (source/DDIC + where-used). Estruture: finalidade, \
campos/estrutura, quem usa e risco de impacto, e um veredito Clean Core (compliant / \
atenção / bloqueador) justificado. Nunca invente objeto, campo ou número de SAP Note. \
Responda em pt-BR.
"""


async def run_chat(
    messages: list[dict], mcp: MCPClient, provider: LLMProvider, max_steps: int = 6
) -> str:
    """Laço: LLM -> (tool_calls -> MCP -> tool results) -> ... -> resposta final."""
    convo: list[dict] = [{"role": "system", "content": SQUAD_SYSTEM}] + messages
    turn = None
    for _ in range(max_steps):
        turn = await provider.complete_with_tools(convo, mcp.tools_for_llm)
        if not turn.tool_calls:
            return turn.text
        convo.append({"role": "assistant", "content": turn.text, "tool_calls": turn.tool_calls})
        for tc in turn.tool_calls:
            result = await mcp.call_tool(tc.name, tc.input)
            convo.append(
                {"role": "tool", "tool_call_id": tc.id, "name": tc.name, "content": result}
            )
    return (turn.text if turn else "") or "Limite de passos atingido sem resposta final."


async def narrate_object_report(
    provider: LLMProvider, object_name: str, report: dict, user_msg: str = ""
) -> str:
    """Narra um relatório de objeto (evidência já coletada via MCP) — sem tools."""
    messages = [
        Message("system", ABAP_REPORT_SYSTEM),
        Message(
            "user",
            f"Pergunta: {user_msg or f'Monte um relatório completo sobre {object_name}.'}\n\n"
            f"EVIDÊNCIA (única fonte de verdade):\n```json\n"
            f"{json.dumps(report, ensure_ascii=False, indent=2)}\n```",
        ),
    ]
    return await provider.complete(messages)
