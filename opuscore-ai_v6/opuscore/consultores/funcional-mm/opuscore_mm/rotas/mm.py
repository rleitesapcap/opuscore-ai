"""Rotas do Consultor Funcional MM (montadas pela Plataforma em /api/c/funcional-mm)."""
from __future__ import annotations

import json
import re
import tempfile
from dataclasses import asdict
from pathlib import Path

import opuscore_ef as ef
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from opuscore_core.contratos.erros import falha_externa, invalido, nao_encontrado, nao_processavel
from opuscore_core.sdk.config import diretorio_config
from pydantic import BaseModel

from ..conhecimento import catalogo_config as cat
from ..servicos import analise_config, regras

CONTEXTO_MM = (Path(__file__).resolve().parents[1] / "conhecimento" / "contexto_mm.md").read_text(encoding="utf-8")


class RegraReq(BaseModel):
    project_id: str
    titulo: str | None = None
    prompt: str | None = None
    obrigatoria: bool | None = None
    condicao: str | None = None
    ativo: bool | None = None


class ProjetoReq(BaseModel):
    project_id: str


class ValidarReq(BaseModel):
    project_id: str
    ef_id: str | None = None
    upload_id: str | None = None
    estado: str = "RASCUNHO"
    imagens: str | None = None


class EnviarReq(BaseModel):
    project_id: str
    artifact_id: str
    observacao: str = ""


class GerarReq(BaseModel):
    project_id: str
    workshop_id: str | None = None
    upload_id: str | None = None
    id_gap: str = ""
    descricao: str = ""
    modulo: str = "MM"


class AnaliseReq(BaseModel):
    project_id: str
    max_rows: int = 200


class TabelaReq(BaseModel):
    project_id: str
    tabela: str
    max_rows: int = 200


def _template(ctx) -> Path:
    p = Path(ctx.config.get("EF_TEMPLATE") or (diretorio_config() / "templates" / "EF_template.docx"))
    if not p.is_file():
        raise invalido(f"Template de EF não encontrado ({p}). Coloque o template do projeto em "
                       "config/templates/EF_template.docx ou defina EF_TEMPLATE no .env.")
    return p


def criar_router(obter_ctx) -> APIRouter:
    r = APIRouter()

    # --- Regras por seção (padrão < MM < projeto) ----------------------------
    @r.get("/secoes")
    def secoes(project_id: str):
        return regras.vigentes(project_id)

    @r.put("/secoes/{sid}")
    def salvar_secao(sid: str, body: RegraReq, ctx=Depends(obter_ctx)):
        if body.prompt is not None and not body.prompt.strip():
            raise invalido("O prompt da seção não pode ficar vazio.")
        if body.condicao:
            try:
                re.compile(body.condicao)
            except re.error:
                raise invalido("Condição inválida (use palavras separadas por |, ex.: interface|migra).")
        try:
            return regras.salvar(body.project_id, sid, body.model_dump(exclude={"project_id"}, exclude_none=True),
                                 ctx.usuario)
        except KeyError:
            raise nao_encontrado("Seção não encontrada.")

    @r.post("/secoes/{sid}/restaurar")
    def restaurar(sid: str, body: ProjetoReq, ctx=Depends(obter_ctx)):
        return regras.restaurar(body.project_id, sid, ctx.usuario)

    @r.get("/secoes/{sid}/historico")
    def historico(sid: str, project_id: str):
        return regras.historico(project_id, sid)

    # --- Validar EF -----------------------------------------------------------------
    @r.post("/ef/validar")
    async def validar(body: ValidarReq, ctx=Depends(obter_ctx)):
        uid = body.upload_id or body.ef_id
        if not uid:
            raise invalido("Envie a EF (.docx ou .pdf).")
        ef_path, meta, _ = ctx.uploads.carregar(uid)
        pasta = Path(tempfile.mkdtemp(prefix="efval_"))
        try:
            r1 = await run_in_threadpool(ef.analisar, ef_path, estado=body.estado, salvar_em=pasta, imagens=body.imagens)
            secs, uso_rev = await run_in_threadpool(ef.validar_secoes, ef_path, regras.vigentes(body.project_id))
        except ValueError as e:
            raise nao_processavel(str(e))
        except Exception as e:  # noqa: BLE001 - provedor de IA
            raise falha_externa(f"Falha na validação: {e}")
        relatorio = ef.relatorio_validacao(r1.feedback_markdown, secs)
        base = r1.feedback_arquivo.replace("-Feedback-Funcional-EF-", "-Validacao-EF-")
        (pasta / base).write_text(relatorio, encoding="utf-8")
        (pasta / r1.arquivo).write_text(r1.markdown, encoding="utf-8")
        (pasta / "revisao_secoes.json").write_text(json.dumps([asdict(x) for x in secs], ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
        (pasta / "handoff_etapa2.json").write_text(json.dumps(r1.handoff, ensure_ascii=False, indent=2), encoding="utf-8")
        no_escopo, fora = ef.objetos_tecnicos(ef_path)
        gap = (r1.handoff.get("ef") or {}).get("id") or ""
        arquivos = [pasta / base, pasta / r1.arquivo, pasta / "revisao_secoes.json", pasta / "handoff_etapa2.json"]
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="ef_validation", titulo=base, conteudo=relatorio,
                                  arquivos=arquivos,
                                  meta={"upload_id": uid, "ef_arquivo": meta.get("filename"), "gate": r1.gate.status,
                                        "gap_id": gap, "objetos_no_escopo": no_escopo, "objetos_fora_escopo": fora})
        return {"gate": r1.gate.status, "justificativa": r1.gate.justificativa, "bloqueantes": r1.gate.bloqueantes,
                "a_confirmar": r1.gate.a_confirmar, "secoes": [asdict(x) for x in secs], "relatorio": relatorio,
                "ef": meta.get("filename"), "gap_id": gap, "pode_enviar": r1.gate.status != "INVALIDO_PARA_DESCOBERTA",
                "uso_ia": {"etapa1": r1.uso_ia, "revisao": uso_rev}, "downloads": ctx.artefatos.arquivos(aid),
                "artifact_id": aid}

    @r.post("/ef/enviar")
    async def enviar(body: EnviarReq, ctx=Depends(obter_ctx)):
        """Envia a EF validada para o desenvolvimento: publica ef.validada (o Orquestrador
        cria o handoff para o Dev, que inicia a Etapa 2 sem novo upload)."""
        a = ctx.artefatos.obter(body.artifact_id)
        m = a.get("meta") or {}
        if a.get("kind") != "ef_validation" or not m:
            raise invalido("Esse artefato não é uma validação de EF.")
        if m["gate"] == "INVALIDO_PARA_DESCOBERTA":
            raise invalido("A EF está inválida para a descoberta. Ajuste e valide de novo antes de enviar.")
        handoff = json.loads(ctx.artefatos.ler_arquivo(body.artifact_id, "handoff_etapa2.json"))
        eid = await ctx.eventos.publicar(
            "ef.validada", projeto_id=body.project_id, gap_id=m.get("gap_id") or "SEM-GAP",
            payload={"gate": m["gate"], "upload_id": m["upload_id"], "ef_arquivo": m["ef_arquivo"],
                     "objetos_no_escopo": m["objetos_no_escopo"], "objetos_fora_escopo": m["objetos_fora_escopo"],
                     "relatorio_artefato": body.artifact_id, "handoff_etapa2": handoff, "observacao": body.observacao},
            artefatos=[body.artifact_id])
        ctx.auditoria.registrar("ef_enviada", artefato=body.artifact_id, evento=eid, por=ctx.usuario)
        return {"evento_id": eid, "gap_id": m.get("gap_id")}

    # --- Gerar EF ---------------------------------------------------------------------
    @r.post("/ef/gerar")
    async def gerar(body: GerarReq, ctx=Depends(obter_ctx)):
        uid = body.upload_id or body.workshop_id
        if not uid:
            raise invalido("Envie o documento do Workshop B.")
        _, meta, texto = ctx.uploads.carregar(uid)
        nome = meta.get("filename", "workshop")
        pasta = Path(tempfile.mkdtemp(prefix="efdraft_"))
        ident = re.sub(r"[^A-Za-z0-9._-]+", "-", body.id_gap or "EF").strip("-") or "EF"
        try:
            rasc, docx, uso = await run_in_threadpool(
                lambda: ef.gerar_rascunho(texto, nome_workshop=nome, template=_template(ctx),
                                          destino=pasta / f"{ident}-EF-RASCUNHO-v0.docx", id_gap=body.id_gap,
                                          descricao=body.descricao, modulo=body.modulo, contexto_modulo=CONTEXTO_MM))
        except ValueError as e:
            raise nao_processavel(str(e))
        except Exception as e:  # noqa: BLE001
            raise falha_externa(f"Falha ao gerar o rascunho: {e}")
        from opuscore_ef.geracao import gerar_ef as g
        resumo = g.markdown_resumo(rasc, nome)
        (pasta / f"{ident}-EF-RASCUNHO-resumo.md").write_text(resumo, encoding="utf-8")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="ef_draft", titulo=docx.name, conteudo=resumo,
                                  arquivos=[docx, pasta / f"{ident}-EF-RASCUNHO-resumo.md"])
        try:
            await ctx.eventos.publicar("ef.rascunho_gerado", projeto_id=body.project_id, gap_id=body.id_gap or "SEM-GAP",
                                       payload={"artefato": aid, "workshop": nome, "a_confirmar": g.contar_confirmar(rasc)},
                                       artefatos=[aid])
        except Exception:  # noqa: BLE001 - o rascunho vale mesmo sem o evento
            pass
        return {"arquivo": docx.name, "workshop": nome, "a_confirmar": g.contar_confirmar(rasc),
                "pontos_a_confirmar": rasc.pontos_a_confirmar, "observacoes": rasc.observacoes_para_o_funcional,
                "contagem": {"objetos": len(rasc.resumo.inventario), "regras": len(rasc.regras),
                             "fluxo": len(rasc.fluxo), "testes": len(rasc.testes)},
                "resumo": resumo, "downloads": ctx.artefatos.arquivos(aid), "artifact_id": aid, "uso_ia": uso}

    # --- Analisar configuração ----------------------------------------------------------
    @r.get("/analises")
    def analises():
        return [{"id": a["id"], "titulo": a["titulo"], "descricao": a["descricao"],
                 "tabelas": [t["nome"] for t in a["tabelas"]]} for a in cat.ANALISES]

    @r.post("/analises/{aid}")
    async def rodar(aid: str, body: AnaliseReq, ctx=Depends(obter_ctx)):
        a = cat.por_id(aid)
        if not a:
            raise nao_encontrado("Análise não encontrada.")
        return {"id": a["id"], "titulo": a["titulo"], "descricao": a["descricao"],
                "blocos": await analise_config.rodar(ctx, a, body.max_rows)}

    @r.post("/tabela")
    async def tabela(body: TabelaReq, ctx=Depends(obter_ctx)):
        nome = (body.tabela or "").strip().upper()
        if not re.fullmatch(r"[A-Z0-9_/]{2,30}", nome):
            raise invalido("Informe o nome técnico da tabela (ex.: T161).")
        d = await analise_config.ler_tabela(ctx, nome, body.max_rows)
        if d.get("erro"):
            raise (nao_encontrado(d["erro"]) if "não encontrad" in d["erro"] else invalido(d["erro"]))
        d = cat.limpar(d)
        d["titulo"] = d.get("description") or nome
        return d

    return r
