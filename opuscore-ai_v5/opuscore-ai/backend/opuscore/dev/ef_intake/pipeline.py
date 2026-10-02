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
    feedback_arquivo: str = ""
    feedback_markdown: str = ""


def _ajustar_imagens(achados: list[Achado], meta: dict) -> list[Achado]:
    """A pendência 'imagem não lida' passa a contar só o que ficou sem leitura."""
    imgs = meta.get("imagens") or []
    if not imgs:
        return achados
    lidas: dict[str, int] = {}
    for i in imgs:
        if i["lida"]:
            lidas[i["sid"]] = lidas.get(i["sid"], 0) + 1
    out = []
    for a in achados:
        if a.codigo == "CONTEUDO_VISUAL" and a.localizacao:
            sid = a.localizacao[0]
            total = sum(1 for i in imgs if i["sid"] == sid)
            nao_lidas = total - lidas.get(sid, 0)
            if nao_lidas <= 0:
                continue
            esb = sum(1 for i in imgs if i["sid"] == sid and not i["lida"] and i["tipo"] == "ESBOCO")
            a.mensagem = (f"{nao_lidas} imagem(ns) da seção não foram lidas "
                          f"({esb} esboço(s) de tela; modo de leitura: {meta.get('modo_imagens')}).")
        out.append(a)
    return out


def processar(doc: EFDocument, res: ExtractionResult, meta: dict) -> IntakeResult:
    """Parte final (sem IA): verifica, decide o gate e gera os documentos."""
    achados = _ajustar_imagens(verificar(doc, res, versao_informada=meta.get("versao", "")), meta)
    gate = decidir(res, achados, estado=meta.get("estado", "RASCUNHO"))
    arquivo, md = render(doc, res, gate, achados, meta)
    handoff = build_handoff(res, gate, achados, meta, arquivo)
    out = IntakeResult(gate, arquivo, md, handoff, res, achados)
    from . import feedback
    out.feedback_arquivo = feedback.nome_arquivo(res.controle.id_demanda, meta.get("versao", ""))
    out.feedback_markdown = feedback.gerar(doc, res, gate, achados, meta)
    return out


def _resumo_deterministico(doc: EFDocument, itens) -> str:
    desc = doc.header.get("Descrição GAP", "")
    obj = next((i.descricao for i in itens if i.categoria == "OBJETIVO"), "")
    return " ".join(x for x in (desc + "." if desc else "", obj) if x).strip()


def executar(ef_path: str | Path, *, versao: str = "", estado: str = "RASCUNHO",
             projeto: str = "", demanda: str = "", anexos: list[str | Path] | None = None,
             provider=None, salvar_em: str | Path | None = None,
             usar_ia: bool = True, usar_cache: bool = True,
             imagens: str | None = None) -> IntakeResult:
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

    # 2) imagens: extração e classificação sempre (sem custo)
    import os
    from . import images as img_mod
    modo_imagens = (imagens or os.environ.get("EF_INTAKE_IMAGENS") or "esbocos").strip().lower()
    if modo_imagens not in ("esbocos", "todas", "nenhuma"):
        modo_imagens = "esbocos"
    try:
        lista_imagens = img_mod.extrair(ef_path, doc)
    except Exception:  # noqa: BLE001 - imagem nunca derruba a EF
        lista_imagens = []

    # 3) IA: semântica + leitura das imagens, numa janela única de medição de uso
    if usar_ia:
        import tempfile
        from ...usage import resumo as resumo_uso
        from ..discovery import ler_uso
        modelo = resolve_model()[0] or "padrao"
        chave = sem.chave_cache(ef_path.read_bytes(), modelo)
        resultado = sem.ler_cache(chave) if usar_cache else None
        msg = sem.montar_mensagem(doc, itens, ctx["narrativa"], ef_versao=versao, estado=estado)
        uso.update({"modo": "híbrido", "entrada_caracteres": len(msg) + len(sem.SEMANTIC_PROMPT),
                    "modelo": modelo})
        uso_log = Path(tempfile.mkstemp(prefix="ef_intake_uso_", suffix=".jsonl")[1])
        anterior = os.environ.get("LLM_USAGE_LOG")
        os.environ["LLM_USAGE_LOG"] = str(uso_log)          # o llm_providers grava cada chamada
        try:
            prov = provider
            if resultado is not None:
                uso["cache"] = True
            else:
                prov = prov or load_provider()
                resultado, _raw = extract(prov, msg, system=sem.SEMANTIC_PROMPT, model_cls=sem.SemanticResult)
                if usar_cache:
                    sem.gravar_cache(chave, resultado)
            alvo = [i for i in lista_imagens if modo_imagens == "todas" or
                    (modo_imagens == "esbocos" and i.tipo == "ESBOCO")]
            if alvo:
                prov = prov or load_provider()
                img_mod.ler(lista_imagens, prov, modelo, modo=modo_imagens, usar_cache=usar_cache)
        finally:
            if anterior is None:
                os.environ.pop("LLM_USAGE_LOG", None)
            else:
                os.environ["LLM_USAGE_LOG"] = anterior
        usos = ler_uso(uso_log)
        uso_log.unlink(missing_ok=True)
        uso["chamadas"] = len(usos) if usos else (0 if uso.get("cache") else 1)
        if usos:
            uso["custo"] = resumo_uso(usos, modelo)

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

        # itens vindos das telas lidas (+ cruzamento imagem x texto)
        itens += img_mod.itens_das_imagens(doc, lista_imagens, itens)
        lidas_locs = {i.loc_legenda for i in lista_imagens if i.leitura}
        itens = [i for i in itens if not (i.categoria == "LAYOUT" and i.classificacao == "PONTO_A_CONFIRMAR"
                                          and set(i.fonte.localizacao) & lidas_locs)]
    else:
        limitacoes.append("Execução sem IA: resumo gerado a partir do cabeçalho e do objetivo; "
                          "B06 (escopo contraditório) e B07 (regra principal ambígua) não foram avaliados; "
                          "ambiguidades e contradições não foram analisadas; imagens não foram lidas.")

    uso["imagens"] = {
        "modo": modo_imagens if usar_ia else "nenhuma",
        "extraidas": len(lista_imagens),
        "por_tipo": {t: sum(1 for i in lista_imagens if i.tipo == t) for t in ("ESBOCO", "ECC", "ILUSTRACAO")},
        "lidas": sum(1 for i in lista_imagens if i.leitura),
        "do_cache": sum(1 for i in lista_imagens if i.do_cache),
        "erros": [f"{i.nome}: {i.erro}" for i in lista_imagens if i.erro],
    }
    for i in lista_imagens:
        if i.mascarados:
            limitacoes.append(f"Valores de identificação de pessoas foram mascarados na {i.nome} "
                              f"(campos: {', '.join(i.mascarados)}).")

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
            "ef_arquivo": doc.filename, "anexos": [a.name for a in anexos],
            "modo_imagens": uso["imagens"]["modo"],
            "imagens": [{"nome": i.nome, "tipo": i.tipo, "legenda": i.legenda, "sid": i.sid, "secao": i.secao,
                         "loc": i.loc_legenda, "lida": i.leitura is not None, "erro": i.erro,
                         "mascarados": i.mascarados,
                         "tela": i.leitura.model_dump() if i.leitura else None} for i in lista_imagens]}
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
    if out.feedback_markdown:
        (pasta / out.feedback_arquivo).write_text(out.feedback_markdown, encoding="utf-8")
    (pasta / "handoff_etapa2.json").write_text(json.dumps(out.handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    (pasta / "extracao_verificada.json").write_text(out.extracao.model_dump_json(indent=2), encoding="utf-8")
    (pasta / "achados.json").write_text(json.dumps([asdict(a) for a in out.achados], ensure_ascii=False, indent=2),
                                        encoding="utf-8")
    (pasta / "uso_ia.json").write_text(json.dumps(out.uso_ia, ensure_ascii=False, indent=2), encoding="utf-8")
    return pasta
