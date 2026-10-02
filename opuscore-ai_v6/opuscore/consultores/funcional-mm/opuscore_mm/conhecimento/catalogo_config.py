"""Análises rápidas de configuração (customizing) de MM.

Cada análise lê tabelas de configuração standard via ADT Data Preview e, quando
há tabela de textos, junta a descrição no idioma do usuário (português, com
inglês como reserva). Só tabelas de configuração são lidas: a ferramenta MCP
confere a classe de entrega no SAP antes de ler (dados de aplicação ficam fora).

Se uma tabela não existir no release conectado, a análise mostra o erro dela
e segue com as demais.
"""
from __future__ import annotations

# Cada tabela: nome, título e (opcional) tabela de textos para juntar a descrição.
ANALISES: list[dict] = [
    {"id": "org", "titulo": "Estrutura organizacional",
     "descricao": "Centros, depósitos, organizações de compras e grupos de compradores.",
     "tabelas": [{"nome": "T001W", "titulo": "Centros"},
                 {"nome": "T001L", "titulo": "Depósitos"},
                 {"nome": "T024E", "titulo": "Organizações de compras"},
                 {"nome": "T024", "titulo": "Grupos de compradores"}]},
    {"id": "doc_compras", "titulo": "Tipos de documento de compras",
     "descricao": "Tipos de pedido, requisição, contrato e programa de remessa.",
     "tabelas": [{"nome": "T161", "titulo": "Tipos de documento de compras", "textos": "T161T"}]},
    {"id": "tipo_material", "titulo": "Tipos de material",
     "descricao": "Tipos de material e seus parâmetros de controle.",
     "tabelas": [{"nome": "T134", "titulo": "Tipos de material", "textos": "T134T"}]},
    {"id": "grupo_mercadoria", "titulo": "Grupos de mercadorias",
     "descricao": "Grupos de mercadorias cadastrados.",
     "tabelas": [{"nome": "T023", "titulo": "Grupos de mercadorias", "textos": "T023T"}]},
    {"id": "tipo_movimento", "titulo": "Tipos de movimento",
     "descricao": "Tipos de movimento de estoque.",
     "tabelas": [{"nome": "T156", "titulo": "Tipos de movimento", "textos": "T156T"}]},
    {"id": "liberacao", "titulo": "Estratégias de liberação",
     "descricao": "Grupos e estratégias de liberação de documentos de compras.",
     "tabelas": [{"nome": "T16FG", "titulo": "Grupos de liberação"},
                 {"nome": "T16FS", "titulo": "Estratégias de liberação", "textos": "T16FT"}]},
    {"id": "avaliacao", "titulo": "Áreas de avaliação",
     "descricao": "Áreas de avaliação e a ligação com as empresas.",
     "tabelas": [{"nome": "T001K", "titulo": "Áreas de avaliação"}]},
    {"id": "tolerancias", "titulo": "Tolerâncias da verificação de faturas",
     "descricao": "Limites de tolerância usados na revisão de faturas.",
     "tabelas": [{"nome": "T169G", "titulo": "Limites de tolerância"}]},
]

IDIOMAS_PT = {"P", "PT"}      # SAP usa 'P' internamente; a saída pode vir em ISO ('PT')
IDIOMAS_EN = {"E", "EN"}
COLUNAS_OCULTAS = {"MANDT", "CLIENT"}


def tabelas_catalogo() -> set[str]:
    out = set()
    for a in ANALISES:
        for t in a["tabelas"]:
            out.add(t["nome"])
            if t.get("textos"):
                out.add(t["textos"])
    return out


def por_id(aid: str) -> dict | None:
    return next((a for a in ANALISES if a["id"] == aid), None)


def juntar_textos(principal: dict, textos: dict) -> dict:
    """Junta as colunas de texto (em português, ou inglês como reserva) às linhas
    da tabela principal, casando pelas colunas-chave em comum."""
    cols_p = [c["name"] for c in principal["columns"]]
    cols_t = [c["name"] for c in textos["columns"]]
    idioma = next((c for c in cols_t if c in ("SPRAS", "LANGU")), None)
    chave = [c for c in cols_t if c in cols_p and c not in COLUNAS_OCULTAS and c != idioma]
    extras = [c for c in textos["columns"] if c["name"] not in cols_p and c["name"] != idioma
              and c["name"] not in COLUNAS_OCULTAS]
    if not chave or not extras:
        return principal

    def melhor(linhas: list[dict]) -> dict:
        if not idioma:
            return linhas[0]
        for grupo in (IDIOMAS_PT, IDIOMAS_EN):
            for l in linhas:
                if (l.get(idioma) or "").upper() in grupo:
                    return l
        return linhas[0]

    indice: dict[tuple, list[dict]] = {}
    for l in textos["rows"]:
        indice.setdefault(tuple(l.get(k, "") for k in chave), []).append(l)
    for l in principal["rows"]:
        achados = indice.get(tuple(l.get(k, "") for k in chave))
        if achados:
            t = melhor(achados)
            for c in extras:
                l[c["name"]] = t.get(c["name"], "")
    # colunas de texto logo depois das chaves, para a descrição aparecer cedo
    pos = max((cols_p.index(k) for k in chave), default=-1) + 1
    principal["columns"] = principal["columns"][:pos] + extras + principal["columns"][pos:]
    return principal


def limpar(tabela: dict) -> dict:
    tabela["columns"] = [c for c in tabela["columns"] if c["name"] not in COLUNAS_OCULTAS]
    return tabela
