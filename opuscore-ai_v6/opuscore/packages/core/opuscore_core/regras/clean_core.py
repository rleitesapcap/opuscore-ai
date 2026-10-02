"""Níveis de Clean Core (A a D) usados nos prompts de análise, validação e remediação.

Fica no Core porque o Dev, o Arquiteto e os funcionais precisam dar o MESMO veredito.
Cada veredito deve registrar a VERSAO da regra com que foi dado. Confira as
definições com a documentação vigente da SAP antes de mudar o texto.
"""
from __future__ import annotations

VERSAO = "1"

NIVEIS: dict[str, dict[str, str]] = {
    "A": {"nome": "Limpo", "descricao": "Somente APIs liberadas e ABAP Cloud (ex.: RAP para app novo)."},
    "B": {"nome": "APIs clássicas", "descricao": "Usa APIs clássicas documentadas, fora do modelo ABAP Cloud."},
    "C": {"nome": "Objetos não liberados", "descricao": "Usa objetos internos/não liberados; risco em upgrade."},
    "D": {"nome": "Não recomendado", "descricao": "Modificação de standard, enhancement implícito ou escrita "
                                                "direta em tabelas SAP."},
}


def texto_para_prompt() -> str:
    linhas = [f"Níveis de Clean Core (regra v{VERSAO}):"]
    linhas += [f"- Nível {k} ({v['nome']}): {v['descricao']}" for k, v in NIVEIS.items()]
    return "\n".join(linhas)
