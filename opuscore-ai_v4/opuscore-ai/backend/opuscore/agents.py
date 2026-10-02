"""Agentes especialistas. Cada consultor do squad é uma subclasse com seu
system-prompt e suas ferramentas. Começamos pelo Desenvolvedor ABAP.

Princípio central (o que torna o produto diferente): o agente NÃO responde de
memória. Ele coleta evidência real do sistema (via ADT), entrega ao LLM e exige
que o modelo cite a evidência. Sem evidência -> ele diz que não sabe.
"""
from __future__ import annotations

import json

from .llm import Message, build_provider
from .sap.adt_client import ADTClient
from .sap.analyzer import ObjectReport, build_object_report, report_to_graph


class BaseAgent:
    name: str = "Agente"
    domain: str = "generic"
    system_prompt: str = ""

    def __init__(self, llm_name: str | None = None):
        self.llm = build_provider(llm_name)

    async def _narrate(self, user_msg: str, evidence: dict) -> str:
        messages = [
            Message("system", self.system_prompt),
            Message(
                "user",
                f"Pergunta do usuário:\n{user_msg}\n\n"
                f"EVIDÊNCIA coletada do sistema SAP (única fonte de verdade):\n"
                f"```json\n{json.dumps(evidence, ensure_ascii=False, indent=2)}\n```\n\n"
                f"Responda em pt-BR. Use SOMENTE a evidência acima. "
                f"Se algo não estiver na evidência, diga explicitamente que não foi "
                f"verificado no sistema — nunca invente nome de objeto, campo ou SAP Note.",
            ),
        ]
        return await self.llm.complete(messages)


ABAP_SYSTEM_PROMPT = """\
Você é o Desenvolvedor ABAP do squad OPUSCORE-AI: especialista sênior em ABAP,
ABAP Cloud e todo o stack do SAP S/4HANA (RAP, CDS, OData, BOPF/BObjects, AMDP,
released APIs). Você é rigoroso e evidence-based.

Ao montar um relatório sobre um objeto (tabela Z, programa Z, classe...):
1. Descreva o objeto e sua finalidade a partir da evidência (source/DDIC).
2. Liste campos/estrutura quando houver.
3. Analise o where-used: quem consome o objeto e o risco de impacto de uma mudança.
4. Faça uma avaliação de Clean Core: o objeto usa APIs liberadas? Há acesso a
   tabelas não liberadas, modificações ou enhancements que quebrariam o upgrade?
   Classifique como Clean Core compliant / atenção / bloqueador, justificando.
5. Nunca cite número de SAP Note sem certeza; se precisar referenciar, diga que
   deve ser confirmado.

Formato: texto técnico direto, em pt-BR, sem enrolação.
"""


class AbapDeveloperAgent(BaseAgent):
    name = "Desenvolvedor ABAP"
    domain = "abap"
    system_prompt = ABAP_SYSTEM_PROMPT

    def __init__(self, adt: ADTClient, llm_name: str | None = None):
        super().__init__(llm_name)
        self.adt = adt

    async def report_on_object(self, object_name: str, user_msg: str = "") -> dict:
        """Capacidade #1: relatório completo sobre um objeto + grafo do Cérebro."""
        report: ObjectReport = await build_object_report(self.adt, object_name)
        narrative = await self._narrate(
            user_msg or f"Monte um relatório completo sobre {object_name}.",
            report.to_dict(),
        )
        return {
            "narrative": narrative,
            "report": report.to_dict(),
            "graph": report_to_graph(report, domain=self.domain),
        }
