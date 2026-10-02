"""Capacidades do agente Desenvolvedor ABAP — o que ele produz de fato.

Tudo é ARTEFATO para revisão (Markdown/ABAP). Nada é escrito no SAP: gerar código
localmente para você revisar e transportar é permitido; alterar o sistema não é.

- object_report  : relatório do objeto (source/DDIC + where-used) — precisa de evidência do ADT
- remediation    : análise + plano de remediação com rubrica Clean Core — precisa do ADT
- tech_spec (ET) : Especificação Técnica a partir de uma EF — só precisa de LLM
- rap_skeleton   : esqueleto RAP Clean Core a partir de uma EF — só precisa de LLM
"""
from __future__ import annotations

import json

from opuscore_core.regras.clean_core import texto_para_prompt
from opuscore_core.sdk.ia import LLMProvider, Message

NO_HALLUCINATION = (
    "Nunca invente nome de objeto SAP, campo, released API ou número de SAP Note. "
    "O que não puder confirmar, marque como TODO ou PONTO A CONFIRMAR."
)

REMEDIATION_SYSTEM = f"""\
Você é o Desenvolvedor ABAP do OPUSCORE-AI. A partir da EVIDÊNCIA do objeto (source/DDIC
+ where-used), produza um RELATÓRIO DE REMEDIAÇÃO em pt-BR, Markdown:
1. Diagnóstico do objeto e finalidade (com base na evidência).
2. Rubrica Clean Core item a item, com veredito (compliant / atenção / bloqueador).
3. Riscos de impacto (quem usa o objeto — a partir do where-used).
4. Plano de remediação passo a passo, priorizado, na direção ABAP Cloud / released APIs
   / extensibilidade recomendada (key-user, developer, side-by-side).
5. Esforço estimado (qualitativo) e pré-condições.
Somente leitura: você recomenda, não altera. {NO_HALLUCINATION}
"""

ET_SYSTEM = f"""\
Você é o Desenvolvedor ABAP do OPUSCORE-AI. Gere uma ESPECIFICAÇÃO TÉCNICA (ET) em pt-BR,
Markdown, a partir da EF fornecida. Estrutura mínima:
1. Identificação e objetivo.
2. Objetos a criar/alterar (nome sugerido, tipo: CDS/RAP/classe/tabela/OData…).
3. Modelo de dados (entidades, chaves, associações).
4. Lógica/regras de negócio e validações.
5. Exposição (serviço OData/RAP) quando aplicável.
6. Autorizações, mensagens e tratamento de erro.
7. Aderência Clean Core (extensibilidade escolhida, released APIs, sem modificação de standard).
8. Cenários de teste (ABAP Unit).
9. Rastreabilidade EF → objetos.
10. Pontos a confirmar.
Priorize ABAP Cloud / RAP / CDS. {NO_HALLUCINATION}
"""

RAP_SYSTEM = f"""\
Você é o Desenvolvedor ABAP do OPUSCORE-AI. Gere um ESQUELETO RAP Clean Core (ABAP Cloud)
a partir da EF. Saída: blocos de código ABAP rotulados por objeto, na ordem:
1. CDS interface view(s) (I_...): campos, chaves, associations.
2. CDS projection view (C_...) para o serviço.
3. Behavior Definition (managed; draft se fizer sentido).
4. Classe de implementação do behavior (ABAP restrito / ABAP for Cloud Development) — esqueleto com TODOs.
5. Service Definition + Service Binding (OData V4).
Regras: sem modificação de objeto standard; use apenas construções RAP/CDS padrão; nomes
de objetos custom como placeholders claros (Z.../Y...); comente cada TODO. Este é um
RASCUNHO para revisão e transporte manual — NÃO é gravado no SAP. {NO_HALLUCINATION}
"""


async def gen_remediation(provider: LLMProvider, object_name: str, report: dict) -> str:
    msgs = [
        Message("system", REMEDIATION_SYSTEM),
        Message("user", f"Objeto: {object_name}\n\nEVIDÊNCIA (ADT):\n```json\n"
                        f"{json.dumps(report, ensure_ascii=False, indent=2)}\n```"),
    ]
    return await provider.complete(msgs)


async def gen_tech_spec(provider: LLMProvider, ef_text: str) -> str:
    msgs = [Message("system", ET_SYSTEM), Message("user", f"EF de entrada:\n\n{ef_text}")]
    return await provider.complete(msgs)


async def gen_rap_skeleton(provider: LLMProvider, ef_text: str) -> str:
    msgs = [Message("system", RAP_SYSTEM), Message("user", f"EF de entrada:\n\n{ef_text}")]
    return await provider.complete(msgs)


ABAP_REPORT_SYSTEM = f"""\
Você é o Desenvolvedor ABAP do OPUSCORE-AI. Monte um relatório técnico sobre o objeto \
usando SOMENTE a evidência fornecida (source/DDIC + where-used). Estruture: finalidade, \
campos/estrutura, quem usa e risco de impacto, e um veredito Clean Core justificado, \
usando os níveis abaixo. Nunca invente objeto, campo ou número de SAP Note. Responda em \
pt-BR, em tom descontraído e direto, como um colega explicando; a precisão técnica não muda.

{texto_para_prompt()}
"""


async def gen_object_report(provider: LLMProvider, object_name: str, report: dict, user_msg: str = "") -> str:
    """Narra o relatório do objeto (evidência já coletada via MCP), sem ferramentas."""
    msgs = [Message("system", ABAP_REPORT_SYSTEM),
            Message("user", f"Pergunta: {user_msg or f'Monte um relatório completo sobre {object_name}.'}\n\n"
                            f"EVIDÊNCIA (única fonte de verdade):\n```json\n"
                            f"{json.dumps(report, ensure_ascii=False, indent=2)}\n```")]
    return await provider.complete(msgs)
