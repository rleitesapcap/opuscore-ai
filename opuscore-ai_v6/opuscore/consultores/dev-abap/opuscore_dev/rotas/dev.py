"""Rotas do Dev ABAP (montadas pela Plataforma em /api/c/dev-abap)."""
from __future__ import annotations

from pathlib import Path

import httpx
import opuscore_ef as ef
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from opuscore_core.contratos.erros import falha_externa, invalido, nao_processavel
from pydantic import BaseModel

from ..adaptadores import execucao as mot
from ..servicos import capacidades_ia as cap
from ..servicos.analise import nome_do_objeto, relatorio


class ObjReq(BaseModel):
    project_id: str
    object_name: str
    llm: str | None = None


class EFTextoReq(BaseModel):
    project_id: str
    ef_text: str
    title: str = ""
    llm: str | None = None


class RemPlanReq(BaseModel):
    project_id: str
    ef_id: str | None = None            # id do upload (serviço da Plataforma)
    upload_id: str | None = None
    ef_text: str | None = None
    max_depth: int = 2


class RemRunReq(BaseModel):
    project_id: str
    objects: list[str]
    gap_id: str = ""


class ETReq(BaseModel):
    project_id: str
    ef_id: str | None = None
    upload_id: str | None = None
    request_id: str | None = None
    objects: list[str] | None = None
    gap_id: str = ""


class IntakeReq(BaseModel):
    project_id: str
    ef_id: str | None = None
    upload_id: str | None = None
    estado: str = "RASCUNHO"
    usar_ia: bool = True
    usar_cache: bool = True
    imagens: str | None = None


def _texto(arquivos: list[Path], limite: int = 200_000) -> str:
    partes, total = [], 0
    for f in arquivos:
        if f.suffix.lower() in (".md", ".abap", ".txt") and total < limite:
            t = f.read_text(encoding="utf-8", errors="replace")
            partes.append(f"\n\n===== {f.name} =====\n{t}")
            total += len(t)
    return "".join(partes)[:limite]


def _gap(ef_path: Path | None, informado: str) -> str:
    if informado:
        return informado
    try:
        return ef.ler(ef_path).header.get("ID GAP", "") if ef_path else ""
    except Exception:  # noqa: BLE001
        return ""


async def _publicar(ctx, tipo: str, projeto: str, gap: str, payload: dict, aid: str) -> None:
    """Publica o evento sem derrubar o resultado se o Orquestrador falhar."""
    try:
        await ctx.eventos.publicar(tipo, projeto_id=projeto, gap_id=gap or "SEM-GAP", payload=payload, artefatos=[aid])
    except Exception as e:  # noqa: BLE001
        ctx.auditoria.registrar("evento_nao_publicado", tipo=tipo, erro=str(e))


def criar_router(obter_ctx) -> APIRouter:
    r = APIRouter()

    def upload(ctx, body):
        uid = body.upload_id or body.ef_id
        if not uid:
            raise invalido("Envie a EF (.docx ou .pdf) antes de continuar.")
        return ctx.uploads.carregar(uid)

    @r.post("/object-report")
    async def object_report(body: ObjReq, ctx=Depends(obter_ctx)):
        nome = nome_do_objeto(body.object_name)
        data = await relatorio(ctx, nome)
        try:
            narrativa = await cap.gen_object_report(ctx.ia(body.llm), nome, data["report"])
        except httpx.HTTPError as e:
            raise falha_externa(f"Falha no LLM: {e}")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="object_report", titulo=f"Relatório — {nome}",
                                  conteudo=narrativa)
        return {"narrative": narrativa, "report": data["report"], "graph": data["graph"], "artifact_id": aid}

    @r.post("/remediation")
    async def remediacao_ia(body: ObjReq, ctx=Depends(obter_ctx)):
        nome = nome_do_objeto(body.object_name)
        data = await relatorio(ctx, nome)
        try:
            conteudo = await cap.gen_remediation(ctx.ia(body.llm), nome, data["report"])
        except httpx.HTTPError as e:
            raise falha_externa(f"Falha no LLM: {e}")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="remediation", titulo=f"Remediação — {nome}",
                                  conteudo=conteudo)
        return {"content": conteudo, "report": data["report"], "artifact_id": aid}

    @r.post("/tech-spec")
    async def tech_spec(body: EFTextoReq, ctx=Depends(obter_ctx)):
        try:
            conteudo = await cap.gen_tech_spec(ctx.ia(body.llm), body.ef_text)
        except httpx.HTTPError as e:
            raise falha_externa(f"Falha no LLM: {e}")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="technical_spec",
                                  titulo=body.title or "Especificação Técnica", conteudo=conteudo)
        return {"content": conteudo, "artifact_id": aid}

    @r.post("/rap")
    async def rap(body: EFTextoReq, ctx=Depends(obter_ctx)):
        try:
            conteudo = await cap.gen_rap_skeleton(ctx.ia(body.llm), body.ef_text)
        except httpx.HTTPError as e:
            raise falha_externa(f"Falha no LLM: {e}")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="rap_code", titulo=body.title or "Esqueleto RAP",
                                  conteudo=conteudo, formato="abap")
        return {"content": conteudo, "artifact_id": aid}

    @r.post("/remediation/plan")
    async def remediacao_plano(body: RemPlanReq, ctx=Depends(obter_ctx)):
        ef_nome, fora = None, []
        if body.upload_id or body.ef_id:
            ef_path, meta, texto = upload(ctx, body)
            ef_nome = meta.get("filename")
            try:
                seeds, fora = ef.objetos_tecnicos(ef_path)
            except Exception:  # noqa: BLE001 - leitura estrutural falhou: busca simples
                seeds = ef.refs_z_texto(texto)
        elif body.ef_text and body.ef_text.strip():
            seeds = ef.refs_z_texto(body.ef_text)
        else:
            raise invalido("Envie a EF (.docx ou .pdf) antes de descobrir os objetos.")
        if not seeds:
            raise invalido("Nenhum objeto (Z*/Y*) identificado na EF. Confira se a EF cita os objetos custom pelo nome técnico.")
        vistos, candidatos = set(), []
        for seed in seeds:
            for d in await ctx.mcp.chamar("sap_z_dependencies", object_name=seed, max_depth=body.max_depth):
                if d["name"].upper() not in vistos:
                    vistos.add(d["name"].upper())
                    candidatos.append(d)
        return {"seeds": seeds, "candidates": candidatos, "count": len(candidatos), "ef": ef_nome, "fora_escopo": fora}

    @r.post("/remediation/run")
    async def remediacao_executar(body: RemRunReq, ctx=Depends(obter_ctx)):
        if not body.objects:
            raise invalido("Lista de objetos vazia — nada a remediar.")
        ok, msg = mot.llm_preflight("remediation")
        if not ok:
            raise invalido(msg)
        fontes = []
        for nome in body.objects:
            d = await ctx.mcp.chamar("sap_get_source", object_name=nome)
            if d.get("source"):
                fontes.append({"name": d["name"], "source": d["source"]})
        if not fontes:
            raise nao_processavel("Nenhum código recuperado (objetos sem código ou inacessíveis).")
        try:
            res = await run_in_threadpool(mot.run_remediation, fontes)
        except Exception as e:  # noqa: BLE001
            raise falha_externa(f"Falha ao executar o motor de remediação: {e}")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="remediation",
                                  titulo=f"Remediação — {len(fontes)} objeto(s)", conteudo=_texto(res.arquivos) or res.log,
                                  formato="abap", arquivos=res.arquivos)
        await _publicar(ctx, "remediacao.concluida", body.project_id, body.gap_id,
                        {"artefato": aid, "objetos": [f["name"] for f in fontes], "ok": res.ok}, aid)
        return {"rc": res.rc, "objects": [f["name"] for f in fontes], "downloads": ctx.artefatos.arquivos(aid),
                "files": [f.name for f in res.arquivos], "artifact_id": aid, "log_tail": res.log[-1500:],
                "diagnosis": res.motivo_falha, "uso_ia": res.uso_ia}

    async def objetos_et(ctx, body: ETReq) -> list[str]:
        upload(ctx, body)       # EF obrigatória e válida antes de qualquer consulta ao SAP
        if body.request_id:
            refs = await ctx.mcp.chamar("sap_transport_objects", request_id=body.request_id)
            return [x["name"] for x in refs if x.get("name")]
        if body.objects:
            return list(dict.fromkeys(body.objects))
        raise invalido("Informe uma request de transporte OU uma lista de objetos.")

    @r.post("/et/plan")
    async def et_plano(body: ETReq, ctx=Depends(obter_ctx)):
        objs = await objetos_et(ctx, body)
        return {"source": "request" if body.request_id else "list", "request_id": body.request_id,
                "objects": objs, "count": len(objs)}

    @r.post("/et/run")
    async def et_executar(body: ETReq, ctx=Depends(obter_ctx)):
        ok, msg = mot.llm_preflight()
        if not ok:
            raise invalido(msg)
        objs = await objetos_et(ctx, body)
        if not objs:
            raise nao_processavel("Nenhum objeto resolvido para a ET.")
        ef_path, meta, _ = upload(ctx, body)
        fontes = []
        for nome in objs:
            d = await ctx.mcp.chamar("sap_get_source", object_name=nome)
            fontes.append({"name": d.get("name", nome), "source": d.get("source", ""), "type": d.get("type", "")})
        try:
            res = await run_in_threadpool(mot.run_et, fontes, ef_path)
        except Exception as e:  # noqa: BLE001
            raise falha_externa(f"Falha ao executar o motor da ET: {e}")
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo="technical_spec",
                                  titulo=f"ET — {len(objs)} objeto(s) — EF {meta.get('filename', '')}",
                                  conteudo=_texto(res.arquivos) or res.log, arquivos=res.arquivos)
        await _publicar(ctx, "et.gerada", body.project_id, _gap(ef_path, body.gap_id),
                        {"artefato": aid, "objetos": objs, "ok": res.ok}, aid)
        return {"rc": res.rc, "objects": objs, "ef": meta.get("filename"), "downloads": ctx.artefatos.arquivos(aid),
                "files": [f.name for f in res.arquivos], "artifact_id": aid, "log_tail": res.log[-1500:],
                "diagnosis": res.motivo_falha, "uso_ia": res.uso_ia}

    @r.get("/llm/preflight")
    def preflight():
        ok, msg = mot.llm_preflight()
        return {"ok": ok, "provider": msg if ok else None, "detail": None if ok else msg}

    @r.post("/ef/intake")
    async def etapa1(body: IntakeReq, ctx=Depends(obter_ctx)):
        """Etapa 1 (pacote de entrada para a descoberta SAP), sem consultar o SAP."""
        import tempfile
        ef_path, meta, _ = upload(ctx, body)
        pasta = Path(tempfile.mkdtemp(prefix="etapa1_"))
        try:
            r1 = await run_in_threadpool(ef.analisar, ef_path, estado=body.estado, salvar_em=pasta, usar_ia=body.usar_ia,
                                         usar_cache=body.usar_cache, imagens=body.imagens)
        except ValueError as e:
            raise nao_processavel(str(e))
        except Exception as e:  # noqa: BLE001 - provedor de IA
            raise falha_externa(f"Falha na Etapa 1: {e}")
        arquivos = [p for p in pasta.rglob("*") if p.is_file()]
        tipo = "ef_pending_report" if r1.gate.status == "INVALIDO_PARA_DESCOBERTA" else "discovery_package"
        aid = ctx.artefatos.criar(projeto_id=body.project_id, tipo=tipo, titulo=r1.arquivo, conteudo=r1.markdown,
                                  arquivos=arquivos)
        return {"gate": r1.gate.status, "justificativa": r1.gate.justificativa, "bloqueantes": r1.gate.bloqueantes,
                "arquivo": r1.arquivo, "markdown": r1.markdown, "handoff": r1.handoff, "artifact_id": aid,
                "ef": meta.get("filename"), "uso_ia": r1.uso_ia, "feedback_markdown": r1.feedback_markdown,
                "downloads": ctx.artefatos.arquivos(aid)}

    return r
