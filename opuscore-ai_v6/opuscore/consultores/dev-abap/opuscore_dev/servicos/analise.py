"""Análise de objeto: extrai o nome técnico de uma frase e monta o relatório via MCP."""
from __future__ import annotations

import re

from opuscore_core.contratos.erros import ErroOpus, invalido, nao_encontrado

_TOKEN_TECNICO = re.compile(r"\b[A-Za-z][A-Za-z0-9_/]*[_/0-9][A-Za-z0-9_/]*\b|\b[A-Z]{3,}\b")


def nome_do_objeto(texto: str) -> str:
    """'Faça a análise do objeto ZSDR_X' -> 'ZSDR_X'. Erro claro se não achar ou se houver vários."""
    t = (texto or "").strip()
    if t and not re.search(r"\s", t):
        return t.upper()
    zy = re.findall(r"\b[ZzYy][A-Za-z0-9_/]{3,}\b", t)
    cand = zy or [x for x in _TOKEN_TECNICO.findall(t) if x.upper() == x or "_" in x]
    cand = list(dict.fromkeys(c.upper() for c in cand))
    if len(cand) == 1:
        return cand[0]
    if not cand:
        raise invalido("Não achei um nome de objeto no texto. Digite só o nome técnico (ex.: MARA, ZCL_ALGO). "
                       "Para pedidos em frase, use a aba Conversas.")
    raise invalido(f"Achei mais de um objeto no texto ({', '.join(cand)}). Digite só o nome do objeto.")


async def relatorio(ctx, nome: str) -> dict:
    try:
        return await ctx.mcp.chamar("sap_object_report", object_name=nome)
    except ErroOpus as e:
        if e.status == 404:
            raise nao_encontrado(f"O objeto {nome} não foi encontrado no SAP conectado. Confira o nome e se ele existe "
                                 "nesse sistema.")
        raise
