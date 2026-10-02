"""Esquema do JSON que a IA devolve na Etapa 1.

A IA NÃO gera Markdown nem decide o gate: devolve itens estruturados, cada um com
fonte literal. O Python verifica as fontes, aplica o gate e gera os documentos.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Categoria = Literal[
    "IDENTIFICACAO", "TIPO_DEMANDA", "OBJETIVO", "JUSTIFICATIVA",
    "COMPONENTE",                     # unidade de trabalho com natureza
    "PROCESSO", "AS_IS", "TO_BE", "ATOR", "REGRA", "EXCECAO", "ACEITE", "PREMISSA",
    "ESCOPO_INCLUIDO", "ESCOPO_EXCLUIDO", "SISTEMA", "DEPENDENCIA",
    "REF_TECNICA", "ANCORA_FUNCIONAL",
    "INTERFACE", "CAMPO", "LAYOUT", "PAYLOAD", "JOB", "WORKFLOW", "PARAMETRO", "TESTE",
    "REQ_NAO_FUNCIONAL",
    "ANEXO", "DADO_SENSIVEL",
    "AUSENCIA", "AMBIGUIDADE", "CONTRADICAO",
]
Classificacao = Literal["FATO_DA_EF", "ENTENDIMENTO", "PONTO_A_CONFIRMAR"]
Confianca = Literal["ALTA", "MEDIA", "BAIXA"]
Natureza = Literal["NOVO", "REMEDIACAO", "EVOLUCAO"]
TipoObjeto = Literal[
    "TRANSACAO", "PROGRAMA", "INCLUDE", "CLASSE", "METODO", "FUNCAO", "TABELA",
    "CAMPO_TABELA", "BADI", "IMPLEMENTACAO_BADI", "EXIT", "ENHANCEMENT", "CDS",
    "SERVICO", "APP_FIORI", "FILA", "JOB", "IFLOW", "WORKFLOW", "CALENDARIO",
    "MENSAGEM", "OUTRO",
]
Escopo = Literal["INCLUIDO", "EXCLUIDO", "INDEFINIDO"]


class Fonte(BaseModel):
    secao: str = Field(description="ID da seção, ex.: S05")
    localizacao: list[str] = Field(description="Localizações dos blocos, ex.: ['P087'] ou ['T2.r11']")
    trecho: str = Field(description="Cópia EXATA de um trecho do texto da EF")


class Item(BaseModel):
    id: str = Field(description="ID único, ex.: I001")
    categoria: Categoria
    descricao: str = Field(description="O item em linguagem clara (pt-BR)")
    valor_original: Optional[str] = Field(None, description="Valor literal da EF. Obrigatório em REF_TECNICA.")
    valor_normalizado: Optional[str] = None
    regra_normalizacao: Optional[str] = None
    tipo_objeto: Optional[TipoObjeto] = None
    natureza: Optional[Natureza] = Field(None, description="Obrigatório em COMPONENTE")
    objeto_origem: Optional[str] = Field(None, description="COMPONENTE REMEDIACAO/EVOLUCAO")
    ancora: Optional[str] = Field(None, description="Âncora funcional quando não há nome técnico")
    sistema: Optional[str] = Field(None, description="Ex.: ECC, S/4HANA, Gestcom")
    escopo: Optional[Escopo] = None
    classificacao: Classificacao
    confianca: Confianca
    fonte: Fonte
    relacionados: list[str] = Field(default_factory=list, description="IDs de itens relacionados")


class Criterio(BaseModel):
    codigo: Literal["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09"]
    bloqueia: bool = Field(description="true se o problema EXISTE na EF")
    evidencia: str
    localizacao: list[str] = Field(default_factory=list)
    origem: str = Field("IA", description="IA ou regra (preenchido pelo sistema)")


class Verificacao(BaseModel):
    id: str = Field(description="ex.: V01")
    objetivo: str
    alvos: list[str] = Field(description="IDs de itens REF_TECNICA/ANCORA_FUNCIONAL alvo")
    tipo: str = Field(description="ex.: existência de objeto, leitura de código, where-used, configuração")
    prioridade: Literal["ALTA", "MEDIA", "BAIXA"]


class Controle(BaseModel):
    id_demanda: str
    projeto: Optional[str] = None
    titulo: Optional[str] = None


class Avaliacao(BaseModel):
    pesquisa_viavel_sem_varredura: bool
    justificativa: str


class ExtractionResult(BaseModel):
    controle: Controle
    resumo_negocio: str
    itens: list[Item]
    criterios: list[Criterio]
    avaliacao: Avaliacao
    plano_etapa2: list[Verificacao] = Field(default_factory=list)
    limitacoes: list[str] = Field(default_factory=list)
