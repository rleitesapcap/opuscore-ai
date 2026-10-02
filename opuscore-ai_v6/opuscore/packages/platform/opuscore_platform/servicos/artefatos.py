"""Artefatos genéricos: metadados no banco, arquivos em <dados>/artifacts/<projeto>/<artefato>/.
Um download único para todos os consultores (sem lista de tipos por consultor)."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from opuscore_core.contratos.erros import nao_encontrado
from opuscore_core.sdk.config import diretorio_dados
from sqlmodel import select

from ..db.engine import get_session
from ..db.modelos import ArtefatoArquivo, Artifact

BAIXAVEIS = {".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
             ".md": "text/markdown; charset=utf-8", ".abap": "text/plain; charset=utf-8",
             ".txt": "text/plain; charset=utf-8", ".pdf": "application/pdf", ".json": "application/json",
             ".csv": "text/csv; charset=utf-8"}
_ID = re.compile(r"^[0-9a-f]{32}$")
_LEGADO = re.compile(r"^(et|remediation|efval|efdraft)-\d{8}-\d{6}(-[0-9a-f]{6})?$")


def _raiz() -> Path:
    return diretorio_dados() / "artifacts"


def _pasta(projeto_id: str, aid: str) -> Path:
    return _raiz() / re.sub(r"[^A-Za-z0-9_-]", "_", projeto_id) / aid


class ServicoArtefatos:
    """Implementação de ctx.artefatos (produzido_por = key do consultor)."""

    def __init__(self, produzido_por: str = ""):
        self.produzido_por = produzido_por

    def criar(self, *, projeto_id, tipo, titulo, conteudo="", formato="markdown", arquivos=(), meta=None) -> str:
        with get_session() as s:
            a = Artifact(project_id=projeto_id, kind=tipo, title=titulo, format=formato, content=conteudo or "",
                         produced_by=self.produzido_por)
            s.add(a)
            s.commit()
            s.refresh(a)
            aid = a.id
            pasta = _pasta(projeto_id, aid)
            pasta.mkdir(parents=True, exist_ok=True)
            for arq in arquivos:
                arq = Path(arq)
                if not arq.is_file():
                    continue
                destino = pasta / arq.name
                shutil.copy2(arq, destino)
                s.add(ArtefatoArquivo(artifact_id=aid, nome=arq.name, tipo=arq.suffix.lower().lstrip("."),
                                      tamanho=destino.stat().st_size,
                                      sha256=hashlib.sha256(destino.read_bytes()).hexdigest()))
            if meta:
                (pasta / "_meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            s.commit()
        return aid

    def obter(self, artefato_id: str) -> dict:
        with get_session() as s:
            a = s.get(Artifact, artefato_id)
            if not a:
                raise nao_encontrado("Artefato não encontrado.")
            meta_p = _pasta(a.project_id, a.id) / "_meta.json"
            return {"id": a.id, "kind": a.kind, "title": a.title, "format": a.format, "content": a.content,
                    "status": a.status, "produced_by": a.produced_by, "project_id": a.project_id,
                    "created_at": a.created_at.isoformat(),
                    "meta": json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.is_file() else {}}

    def arquivos(self, artefato_id: str) -> list[dict]:
        with get_session() as s:
            rows = s.exec(select(ArtefatoArquivo).where(ArtefatoArquivo.artifact_id == artefato_id)).all()
        if rows:
            ordem = sorted(rows, key=lambda r: (r.tipo != "docx", r.nome))
            return [{"nome": r.nome, "tipo": r.tipo, "tamanho": r.tamanho,
                     "url": f"/api/plataforma/artefatos/{artefato_id}/arquivos/{quote(r.nome)}"} for r in ordem]
        return _legado(artefato_id)

    def ler_arquivo(self, artefato_id: str, nome: str) -> bytes:
        a = self.obter(artefato_id)
        p = _pasta(a["project_id"], artefato_id) / Path(nome).name
        if not p.is_file():
            raise nao_encontrado("Arquivo não encontrado.")
        return p.read_bytes()

    def listar(self, projeto_id: str, tipo: str | None = None, produzido_por: str | None = None) -> list[dict]:
        with get_session() as s:
            q = select(Artifact).where(Artifact.project_id == projeto_id)
            if tipo:
                q = q.where(Artifact.kind == tipo)
            if produzido_por:
                q = q.where(Artifact.produced_by == produzido_por)
            arts = s.exec(q.order_by(Artifact.created_at.desc())).all()
            return [{"id": a.id, "kind": a.kind, "title": a.title, "format": a.format, "status": a.status,
                     "produced_by": a.produced_by, "created_at": a.created_at.isoformat()} for a in arts]


def _legado(artefato_id: str) -> list[dict]:
    """Artefatos gerados pela versão anterior (pasta <tipo>-<data>-<hex> + artifact.json)."""
    raiz = _raiz()
    if not raiz.is_dir():
        return []
    for pasta in raiz.iterdir():
        marca = pasta / "artifact.json"
        if pasta.is_dir() and _LEGADO.match(pasta.name) and marca.is_file():
            try:
                if json.loads(marca.read_text(encoding="utf-8")).get("artifact_id") != artefato_id:
                    continue
            except json.JSONDecodeError:
                continue
            arqs = sorted((f for f in pasta.iterdir() if f.is_file() and f.suffix.lower() in BAIXAVEIS),
                          key=lambda f: (f.suffix.lower() != ".docx", f.name))
            return [{"nome": f.name, "tipo": f.suffix.lower().lstrip("."), "tamanho": f.stat().st_size,
                     "url": f"/api/plataforma/legado/{pasta.name}/{quote(f.name)}"} for f in arqs]
    return []


def _servir(alvo: Path, pasta: Path):
    if alvo.parent != pasta or not alvo.is_file() or alvo.suffix.lower() not in BAIXAVEIS or alvo.name.startswith("_"):
        raise HTTPException(404, "Arquivo não encontrado.")
    return FileResponse(alvo, filename=alvo.name, media_type=BAIXAVEIS[alvo.suffix.lower()])


router = APIRouter(prefix="/api/plataforma", tags=["artefatos"])


@router.get("/projects/{pid}/artifacts")
def listar(pid: str, produzido_por: str | None = None):
    return ServicoArtefatos().listar(pid, produzido_por=produzido_por)


@router.get("/artifacts/{aid}")
def obter(aid: str):
    return ServicoArtefatos().obter(aid)


@router.get("/artefatos/{aid}/arquivos")
def arquivos(aid: str):
    return ServicoArtefatos().arquivos(aid)


@router.get("/artefatos/{aid}/arquivos/{nome}")
def baixar(aid: str, nome: str):
    if not _ID.match(aid) or nome != Path(nome).name:
        raise HTTPException(400, "Identificador ou nome de arquivo inválido.")
    a = ServicoArtefatos().obter(aid)
    pasta = _pasta(a["project_id"], aid).resolve()
    return _servir((pasta / nome).resolve(), pasta)


@router.get("/legado/{run_id}/{nome}")
def baixar_legado(run_id: str, nome: str):
    if not _LEGADO.match(run_id) or nome != Path(nome).name:
        raise HTTPException(400, "Identificador ou nome de arquivo inválido.")
    pasta = (_raiz() / run_id).resolve()
    return _servir((pasta / nome).resolve(), pasta)
