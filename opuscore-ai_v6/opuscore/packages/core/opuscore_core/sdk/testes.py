"""Fakes para testar um pacote sem Plataforma, SAP ou IA de verdade."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ..contratos.erros import falha_externa, nao_encontrado
from ..contratos.eventos import Evento, validar_payload


class MCPFalso:
    """respostas: {"sap_get_source": obj_ou_funcao(args)->obj}. Também imita o MCPClient
    (tools_for_llm / call_tool) para o laço do chat."""

    def __init__(self, respostas: dict[str, Any] | None = None):
        self.respostas = respostas or {}
        self.chamadas: list[tuple[str, dict]] = []
        self.tools_for_llm = [{"name": n, "description": "", "input_schema": {"type": "object"}}
                              for n in self.respostas]

    @property
    def ferramentas(self):
        return self.tools_for_llm

    async def call_tool(self, nome: str, args: dict | None = None) -> str:
        self.chamadas.append((nome, args or {}))
        r = self.respostas.get(nome, {"error": f"ferramenta {nome} não simulada"})
        r = r(args or {}) if callable(r) else r
        return r if isinstance(r, str) else json.dumps(r, ensure_ascii=False)

    async def chamar_texto(self, ferramenta: str, **args) -> str:
        return await self.call_tool(ferramenta, args)

    async def chamar(self, ferramenta: str, **args):
        d = json.loads(await self.chamar_texto(ferramenta, **args))
        if isinstance(d, dict) and d.get("error"):
            e = str(d["error"])
            raise nao_encontrado(e) if "não encontrad" in e.lower() else falha_externa(e)
        return d


class ArtefatosMemoria:
    def __init__(self, raiz: Path | None = None):
        self.itens: dict[str, dict] = {}
        self.raiz = raiz

    def criar(self, *, projeto_id, tipo, titulo, conteudo="", formato="markdown", arquivos=(), meta=None):
        aid = uuid.uuid4().hex
        self.itens[aid] = {"id": aid, "projeto_id": projeto_id, "tipo": tipo, "titulo": titulo,
                           "conteudo": conteudo, "formato": formato, "meta": meta or {},
                           "arquivos": {Path(a).name: Path(a).read_bytes() for a in arquivos}}
        return aid

    def obter(self, artefato_id):
        return self.itens[artefato_id]

    def arquivos(self, artefato_id):
        return [{"nome": n, "tipo": Path(n).suffix.lstrip("."), "tamanho": len(b),
                 "url": f"/fake/{artefato_id}/{n}"} for n, b in self.itens[artefato_id]["arquivos"].items()]

    def ler_arquivo(self, artefato_id, nome):
        return self.itens[artefato_id]["arquivos"][nome]

    def listar(self, projeto_id, tipo=None, produzido_por=None):
        return [a for a in self.itens.values() if a["projeto_id"] == projeto_id and (not tipo or a["tipo"] == tipo)]


class UploadsMemoria:
    def __init__(self):
        self.itens: dict[str, tuple[Path, dict, str]] = {}

    def registrar(self, caminho: Path, texto: str = "", meta: dict | None = None) -> str:
        uid = uuid.uuid4().hex
        self.itens[uid] = (Path(caminho), {"filename": Path(caminho).name, **(meta or {})}, texto)
        return uid

    def carregar(self, upload_id):
        if upload_id not in self.itens:
            raise nao_encontrado("Upload não encontrado.")
        return self.itens[upload_id]


class EventosMemoria:
    def __init__(self, origem: str = "teste"):
        self.publicados: list[Evento] = []
        self.origem = origem

    async def publicar(self, tipo, *, projeto_id, gap_id, payload, artefatos=(), versao=1, causa_id=None):
        ev = Evento(tipo=tipo, versao=versao, projeto_id=projeto_id, gap_id=gap_id, origem=self.origem,
                    causa_id=causa_id, payload=validar_payload(tipo, versao, payload), artefatos=list(artefatos))
        self.publicados.append(ev)
        return ev.id


class AuditoriaMemoria:
    def __init__(self):
        self.registros: list[dict] = []

    def registrar(self, acao, /, **campos):
        self.registros.append({"acao": acao, **campos})


@dataclass
class ContextoFalso:
    plugin_key: str = "teste"
    request_id: str = "req-teste"
    usuario: str = "local"
    mcp: Any = field(default_factory=MCPFalso)
    artefatos: Any = field(default_factory=ArtefatosMemoria)
    uploads: Any = field(default_factory=UploadsMemoria)
    eventos: Any = field(default_factory=EventosMemoria)
    auditoria: Any = field(default_factory=AuditoriaMemoria)
    config: dict = field(default_factory=dict)
    provedor_ia: Any = None

    def ia(self, nome=None):
        return self.provedor_ia


class _Resposta:
    def __init__(self, texto: str):
        self.text, self.finish_reason, self.usage = texto, "stop", {}


class IAFalsaSync:
    """Imita os provedores síncronos (sdk.provedores): invoke(system, turns) -> .text.
    `responder(system, turns) -> str|dict` ou uma lista de respostas em sequência."""

    def __init__(self, responder: Callable[[str, list], Any] | list):
        self.responder = responder
        self.chamadas: list[str] = []

    def invoke(self, system: str, turns: list[dict]):
        self.chamadas.append(system[:60])
        r = self.responder.pop(0) if isinstance(self.responder, list) else self.responder(system, turns)
        return _Resposta(r if isinstance(r, str) else json.dumps(r, ensure_ascii=False))
