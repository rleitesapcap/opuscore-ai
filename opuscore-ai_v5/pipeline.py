"""Orquestra a Etapa 1.

Determinístico primeiro: o Python extrai toda a estrutura da EF com fonte literal.
A IA entra só na parte semântica (resumo, natureza dos componentes, ambiguidades,
B06/B07), com entrada reduzida e resultado em cache. Com usar_ia=False, nenhuma
chamada é feita e B06/B07 ficam como "não avaliados" (gate no máximo com ressalvas).
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from . import deterministic as det
from . import semantic as sem
from .checks import Achado, verificar
from .extractor import extract, load_provider, resolve_model
from .gate import Gate, decidir
from .handoff import build_handoff
from .parser import EFDocument, parse_ef
from .render import render
from .schema import Avaliacao, Controle, ExtractionResult

ESTADOS = ("RASCUNHO", "EM_REVISAO", "APROVADA")


@dataclass
class IntakeResult:
    gate: Gate
    arquivo: str
    markdown: str
    handoff: dict
    extracao: ExtractionResult
    achados: list[Achado]
    pasta: str = ""
    uso_ia: dict = field(default_factory=dict)


def processar(doc: EFDocument, res: ExtractionResult, meta: dict) -> IntakeResult:
    """Parte final (sem IA): verifica, decide o gate e gera os documentos."""
    achados = verificar(doc, res, versao_informada=meta.get("versao", ""))
    gate = decidir(res, achados, estado=meta.get("estado", "RASCUNHO"))
    arquivo, md = render(doc, res, gate, achados, meta)
    handoff = build_handoff(res, gate, achados, meta, arquivo)
    return IntakeResult(gate, arquivo, md, handoff, res, achados)


def _resumo_deterministico(doc: EFDocument, itens) -> str:
    desc = doc.header.get("Descrição GAP", "")
    obj = next((i.descricao for i in itens if i.categoria == "OBJETIVO"), "")
    return " ".join(x for x in (desc + "." if desc else "", obj) if x).strip()


def executar(ef_path: str | Path, *, versao: str = "", estado: str = "RASCUNHO",
             projeto: str = "", demanda: str = "", anexos: list[str | Path] | None = None,
             provider=None, salvar_em: str | Path | None = None,
             usar_ia: bool = True, usar_cache: bool = True) -> IntakeResult:
    estado = (estado or "RASCUNHO").upper()
    if estado not in ESTADOS:
        raise ValueError(f"Estado de aprovação inválido: {estado}. Use {', '.join(ESTADOS)}.")
    ef_path = Path(ef_path)
    doc = parse_ef(ef_path)
    versao = versao or (doc.revisions[-1]["versao"] if doc.revisions else "")
    demanda = demanda or doc.header.get("ID GAP", "") or ef_path.stem
    anexos = [Path(a) for a in (anexos or [])]

    # 1) determinístico (sem IA)
    itens, ctx = det.extrair(doc)
    for a in anexos:  # anexos entram na mesma extração estrutural
        adoc = parse_ef(a)
        aitens, _ = det.extrair(adoc)
        for it in aitens:
            it.id = f"X{it.id[1:]}"
            it.descricao = f"[anexo {a.name}] {it.descricao}"
        itens += aitens
    criterios = det.criterios(itens, ctx)
    resumo = _resumo_deterministico(doc, itens)
    limitacoes: list[str] = []
    uso = {"modo": "sem IA", "chamadas": 0, "cache": False, "entrada_caracteres": 0}

    # 2) semântico (IA), só o que exige interpretação
    if usar_ia:
        modelo = resolve_model()[0] or "padrao"
        chave = sem.chave_cache(ef_path.read_bytes(), modelo)
        resultado = sem.ler_cache(chave) if usar_cache else None
        msg = sem.montar_mensagem(doc, itens, ctx["narrativa"], ef_versao=versao, estado=estado)
        uso.update({"modo": "híbrido", "entrada_caracteres": len(msg) + len(sem.SEMANTIC_PROMPT),
                    "modelo": modelo})
        if resultado is not None:
            uso["cache"] = True
        else:
            import os
            import tempfile
            from ...usage import resumo as resumo_uso
            from ..discovery import ler_uso
            uso_log = Path(tempfile.mkstemp(prefix="ef_intake_uso_", suffix=".jsonl")[1])
            anterior = os.environ.get("LLM_USAGE_LOG")
            os.environ["LLM_USAGE_LOG"] = str(uso_log)      # o llm_providers grava cada chamada
            try:
                resultado, _raw = extract(provider or load_provider(), msg,
                                          system=sem.SEMANTIC_PROMPT, model_cls=sem.SemanticResult)
            finally:
                if anterior is None:
                    os.environ.pop("LLM_USAGE_LOG", None)
                else:
                    os.environ["LLM_USAGE_LOG"] = anterior
            usos = ler_uso(uso_log)
            uso_log.unlink(missing_ok=True)
            uso["chamadas"] = max(1, len(usos))
            if usos:
                uso["custo"] = resumo_uso(usos, modelo)
            if usar_cache:
                sem.gravar_cache(chave, resultado)
        itens, crit_ia = sem.aplicar(itens, resultado)
        resumo = resultado.resumo_negocio.strip() or resumo
        limitacoes += resultado.limitacoes
        por_cod = {c.codigo: c for c in criterios}
        for c in crit_ia:
            c.origem = "IA"
            regra = por_cod.get(c.codigo)
            if c.codigo in ("B06", "B07"):
                por_cod[c.codigo] = c          # B06/B07 são avaliados pela IA
            elif c.bloqueia and regra is not None and not regra.bloqueia:
                por_cod[c.codigo] = c          # a IA só endurece (vira "a confirmar" no gate)
            # se a regra já bloqueia, o bloqueio dela (definitivo) é mantido
        criterios = list(por_cod.values())
    else:
        limitacoes.append("Execução sem IA: resumo gerado a partir do cabeçalho e do objetivo; "
                          "B06 (escopo contraditório) e B07 (regra principal ambígua) não foram avaliados; "
                          "ambiguidades e contradições não foram analisadas.")

    refs_ok = [i for i in itens if i.categoria in ("REF_TECNICA", "ANCORA_FUNCIONAL") and i.escopo != "EXCLUIDO"]
    res = ExtractionResult(
        controle=Controle(id_demanda=demanda, projeto=projeto or doc.header.get("Projeto"),
                          titulo=doc.header.get("Descrição GAP")),
        resumo_negocio=resumo, itens=itens, criterios=criterios,
        avaliacao=Avaliacao(pesquisa_viavel_sem_varredura=bool(refs_ok),
                            justificativa=f"{len(refs_ok)} referência(s) técnica(s) no escopo ou indefinidas "
                                          "orientam a pesquisa." if refs_ok else
                                          "Nenhuma referência técnica ou âncora para orientar a pesquisa."),
        plano_etapa2=det.plano(itens), limitacoes=limitacoes,
    )
    meta = {"versao": versao, "estado": estado, "projeto": projeto or doc.header.get("Projeto", ""),
            "ef_arquivo": doc.filename, "anexos": [a.name for a in anexos]}
    out = processar(doc, res, meta)
    out.uso_ia = uso
    if salvar_em:
        out.pasta = str(salvar(out, salvar_em))
    return out


def salvar(out: IntakeResult, base: str | Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    pasta = Path(base) / f"intake-{stamp}"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / out.arquivo).write_text(out.markdown, encoding="utf-8")
    (pasta / "handoff_etapa2.json").write_text(json.dumps(out.handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "extracao_verificada.json").write_text(out.extracao.model_dump_json(indent=2), encoding="utf-8")
    (pasta / "achados.json").write_text(json.dumps([asdict(a) for a in out.achados], ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    (pasta / "uso_ia.json").write_text(json.dumps(out.uso_ia, ensure_ascii=False, indent=2), encoding="utf-8")
    return pasta
