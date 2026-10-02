"""Análises rápidas de configuração: lê pelo MCP (a trava por classe de entrega fica nos
Conectores) e junta os textos em português."""
from __future__ import annotations

import json

from ..conhecimento import catalogo_config as cat


async def ler_tabela(ctx, tabela: str, max_rows: int = 200) -> dict:
    try:
        data = json.loads(await ctx.mcp.chamar_texto("sap_config_table", table_name=tabela, max_rows=max_rows))
    except Exception as e:  # noqa: BLE001
        return {"table": tabela, "erro": f"Falha ao consultar o SAP: {e}"}
    if isinstance(data, dict) and data.get("error"):
        return {"table": tabela, "erro": data["error"]}
    return data


async def rodar(ctx, analise: dict, max_rows: int = 200) -> list[dict]:
    blocos = []
    for t in analise["tabelas"]:
        dados = await ler_tabela(ctx, t["nome"], max_rows)
        if not dados.get("erro") and t.get("textos"):
            txt = await ler_tabela(ctx, t["textos"], 1000)
            if not txt.get("erro"):
                dados = cat.juntar_textos(dados, txt)
            else:
                dados["aviso"] = f"Textos ({t['textos']}) indisponíveis: {txt['erro']}"
        if not dados.get("erro"):
            dados = cat.limpar(dados)
        dados["titulo"] = t["titulo"]
        blocos.append(dados)
    return blocos
