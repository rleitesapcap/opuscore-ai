"""Pacote EF: leitura, validação e geração de Especificações Funcionais (biblioteca).

Fachada pública estável (os consultores usam só isto):
    ler(caminho)                         -> EFDocument
    analisar(caminho, **opcoes)          -> resultado da Etapa 1 (gate, relatório, handoff, uso)
    validar_secoes(caminho, regras, ...) -> (resultados por seção, uso)
    relatorio_validacao(etapa1, secoes)  -> markdown único para o funcional
    gerar_rascunho(texto, ...)           -> (RascunhoEF, caminho do .docx, uso)
    objetos_tecnicos(caminho)            -> (no_escopo, fora_do_escopo)
    regras_padrao(*ajustes)              -> regras por seção vigentes
Sem rotas, banco ou tela. Não acessa SAP nem a Plataforma.
"""
from __future__ import annotations

from pathlib import Path

__version__ = "1.0.0"

from .objetos import objetos_tecnicos, refs_z_texto  # noqa: E402,F401


def ler(caminho):
    from .intake.parser import parse_ef
    return parse_ef(Path(caminho))


def analisar(caminho, **opcoes):
    """Etapa 1 completa. Opções do `intake.pipeline.executar` (estado, salvar_em, usar_ia,
    usar_cache, imagens, provider...)."""
    from .intake.pipeline import executar
    return executar(Path(caminho), **opcoes)


def regras_padrao(*ajustes):
    from .validacao import secoes
    return secoes.carregar(*ajustes)


def validar_secoes(caminho, regras=None, *, provider=None, usar_cache=True):
    from .validacao.validar import revisar
    return revisar(Path(caminho), regras=regras, provider=provider, usar_cache=usar_cache)


def relatorio_validacao(feedback_etapa1: str, resultados) -> str:
    from .validacao import validar as v
    return v.inserir_no_feedback(feedback_etapa1, v.markdown_revisao(resultados), resultados)


def gerar_rascunho(texto_workshop: str, *, nome_workshop: str, template: Path, destino: Path,
                   provider=None, id_gap: str = "", descricao: str = "", modulo: str = "MM",
                   contexto_modulo: str = "", autor: str = ""):
    """Rascunho de EF no template do projeto. Retorna (RascunhoEF, caminho_docx, uso)."""
    import os
    import tempfile

    from opuscore_core.sdk.uso import ler_log, resumo

    from .geracao import gerar_ef as g
    from .intake.extractor import extract, load_provider, resolve_model

    log = Path(tempfile.mkstemp(prefix="efdraft_uso_", suffix=".jsonl")[1])
    anterior = os.environ.get("LLM_USAGE_LOG")
    os.environ["LLM_USAGE_LOG"] = str(log)
    try:
        rasc, _ = extract(provider or load_provider(),
                          g.mensagem(texto_workshop, nome=nome_workshop, id_gap=id_gap, descricao=descricao,
                                     modulo=modulo, contexto_modulo=contexto_modulo),
                          system=g.PROMPT_GERADOR, model_cls=g.RascunhoEF)
    finally:
        if anterior is None:
            os.environ.pop("LLM_USAGE_LOG", None)
        else:
            os.environ["LLM_USAGE_LOG"] = anterior
    usos = ler_log(log)
    log.unlink(missing_ok=True)
    if id_gap and not rasc.identificacao.id_gap:
        rasc.identificacao.id_gap = id_gap
    if descricao and not rasc.identificacao.descricao_gap:
        rasc.identificacao.descricao_gap = descricao
    caminho = g.montar_docx(rasc, Path(destino), template=Path(template), workshop_nome=nome_workshop, autor=autor)
    uso = resumo(usos, resolve_model()[0]) if usos else {"chamadas": 1}
    return rasc, caminho, uso
