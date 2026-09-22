"""Cliente para a ADT REST API (ABAP Development Tools).

Por que ADT e não RFC?
  A SAP arquivou o PyRFC e depreciou o SAP NW RFC SDK em mai/2026. Para um
  produto novo, amarrar no RFC é dívida técnica na certa. A ADT REST API é o
  MESMO HTTP que o Eclipse ADT usa: source de qualquer objeto do repositório,
  DDIC, ATC, ABAP Unit e where-used, tudo via GET/POST previsíveis.

Notas honestas de campo (não fabricar spec):
  - O corpo/headers exatos de alguns endpoints variam por release. Quando
    precisar confirmar, ligue o "ABAP Communication Log" no Eclipse e observe
    a request real, ou leia o ABAP do handler — essa é a spec autoritativa.
  - Leituras (source, DDIC) são GET simples. usageReferences é POST e exige
    token CSRF. Por isso o cliente busca o token antes de qualquer POST.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import quote

import httpx
from lxml import etree

from ..safety import ChangeRequest, MutationGuard, build_guard
from ..settings import SapSystemCfg


@dataclass
class ObjectRef:
    name: str
    type: str = ""          # ex.: TABL/DT, PROG/P, CLAS/OC, DDLS/DF
    uri: str = ""           # caminho ADT, ex.: /sap/bc/adt/ddic/tables/ZFOO
    package: str = ""
    description: str = ""


@dataclass
class ObjectDetail:
    ref: ObjectRef
    source: str = ""                       # código-fonte, quando aplicável
    metadata: dict = field(default_factory=dict)
    raw_xml: str = ""


def _local(tag: str) -> str:
    """Remove namespace para parsing robusto entre releases."""
    return tag.rsplit("}", 1)[-1]


def _attr(el, name: str) -> str:
    for k, v in el.attrib.items():
        if _local(k) == name:
            return v
    return ""


class ADTError(RuntimeError):
    pass


class ADTClient:
    def __init__(
        self,
        cfg: SapSystemCfg,
        guard: MutationGuard | None = None,
        system_name: str = "",
    ):
        self.cfg = cfg
        self.system_name = system_name
        self.read_only = cfg.read_only
        # Sem guard injetado -> guard seguro (somente-leitura, nega por padrão).
        self.guard = guard or build_guard(system_name or "default", interactive=False)
        auth = (
            httpx.BasicAuth(cfg.user, cfg.password) if cfg.auth == "basic" else None
        )
        headers = {"Accept": "application/*"}
        if cfg.auth == "bearer" and cfg.token:
            headers["Authorization"] = f"Bearer {cfg.token}"
        self._client = httpx.AsyncClient(
            base_url=cfg.base_url.rstrip("/"),
            params={"sap-client": cfg.client},
            auth=auth,
            headers=headers,
            verify=cfg.verify_ssl,
            timeout=60,
            follow_redirects=True,
        )
        self._csrf: str | None = None

    async def aclose(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    # --- conexão --------------------------------------------------------------
    async def discovery(self) -> bool:
        """Endpoint barato que sempre existe — prova a conexão."""
        try:
            r = await self._client.get("/sap/bc/adt/core/discovery")
        except httpx.RequestError as e:
            raise ADTError(f"Não consegui conectar ao ADT em {self.cfg.base_url}: {e}") from e
        if r.status_code == 200:
            return True
        raise ADTError(f"Discovery falhou: HTTP {r.status_code} — {r.text[:200]}")

    async def _ensure_csrf(self):
        if self._csrf:
            return
        r = await self._client.get(
            "/sap/bc/adt/core/discovery", headers={"x-csrf-token": "fetch"}
        )
        tok = r.headers.get("x-csrf-token")
        if not tok:
            raise ADTError("Não obtive token CSRF do servidor ADT.")
        self._csrf = tok

    # --- busca ----------------------------------------------------------------
    async def search(self, query: str, max_results: int = 50) -> list[ObjectRef]:
        """Quick search do 'Information System' do ADT."""
        r = await self._client.get(
            "/sap/bc/adt/repository/informationsystem/search",
            params={
                "operation": "quickSearch",
                "query": query,
                "maxResults": max_results,
            },
            headers={"Accept": "application/xml"},
        )
        r.raise_for_status()
        return self._parse_object_refs(r.content)

    def _parse_object_refs(self, content: bytes) -> list[ObjectRef]:
        refs: list[ObjectRef] = []
        try:
            root = etree.fromstring(content)
        except etree.XMLSyntaxError:
            return refs
        for el in root.iter():
            if _local(el.tag) == "objectReference":
                refs.append(
                    ObjectRef(
                        name=_attr(el, "name"),
                        type=_attr(el, "type"),
                        uri=_attr(el, "uri"),
                        package=_attr(el, "packageName"),
                        description=_attr(el, "description"),
                    )
                )
        return refs

    async def resolve(self, name: str) -> ObjectRef:
        """Resolve nome -> ObjectRef (tipo + uri) via busca exata."""
        for ref in await self.search(name, max_results=20):
            if ref.name.upper() == name.upper():
                return ref
        raise ADTError(f"Objeto não encontrado no repositório: {name}")

    # --- leitura de conteúdo --------------------------------------------------
    async def get_source(self, ref: ObjectRef) -> str:
        """GET {uri}/source/main — funciona p/ program, class, include, CDS, FM."""
        if not ref.uri:
            ref = await self.resolve(ref.name)
        url = f"{ref.uri.rstrip('/')}/source/main"
        r = await self._client.get(url, headers={"Accept": "text/plain"})
        if r.status_code == 200:
            return r.text
        return ""  # objetos sem source (ex.: tabela transparente) caem aqui

    async def get_table(self, name: str) -> ObjectDetail:
        """Metadados de tabela DDIC (campos, chaves, tipo)."""
        url = f"/sap/bc/adt/ddic/tables/{quote(name)}"
        r = await self._client.get(url, headers={"Accept": "application/xml"})
        r.raise_for_status()
        return self._parse_table(name, r.content)

    def _parse_table(self, name: str, content: bytes) -> ObjectDetail:
        ref = ObjectRef(name=name, type="TABL/DT", uri=f"/sap/bc/adt/ddic/tables/{name}")
        detail = ObjectDetail(ref=ref, raw_xml=content.decode("utf-8", "replace"))
        try:
            root = etree.fromstring(content)
        except etree.XMLSyntaxError:
            return detail
        detail.metadata["description"] = _attr(root, "description")
        fields = []
        for el in root.iter():
            if _local(el.tag) in ("field", "dataElement", "column"):
                fname = _attr(el, "name")
                if not fname:
                    continue
                fields.append(
                    {
                        "name": fname,
                        "key": _attr(el, "key") in ("true", "X"),
                        "type": _attr(el, "dataType") or _attr(el, "type"),
                        "length": _attr(el, "length"),
                        "description": _attr(el, "description"),
                    }
                )
        detail.metadata["fields"] = fields
        return detail

    # --- where-used -----------------------------------------------------------
    async def where_used(self, ref: ObjectRef) -> list[ObjectRef]:
        """Lista objetos que referenciam este (impacto/dependências).

        Espelha o que o Eclipse envia ao usageReferences. O corpo mínimo abaixo
        cobre a maioria dos releases; se seu sistema exigir posição (linha/col)
        para um símbolo específico, capture a request no Communication Log.
        """
        if not ref.uri:
            ref = await self.resolve(ref.name)
        await self._ensure_csrf()
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<usagereferences:usageReferenceRequest '
            'xmlns:usagereferences="http://www.sap.com/adt/ris/usageReferences">'
            "<usagereferences:affectedObjects/>"
            "</usagereferences:usageReferenceRequest>"
        )
        r = await self._client.post(
            "/sap/bc/adt/repository/informationsystem/usageReferences",
            params={"uri": ref.uri},
            content=body,
            headers={
                "x-csrf-token": self._csrf or "",
                "Content-Type": "application/xml",
                "Accept": "application/xml",
            },
        )
        if r.status_code >= 400:
            raise ADTError(
                f"where_used falhou (HTTP {r.status_code}). "
                f"Confirme o payload no Communication Log do Eclipse. {r.text[:200]}"
            )
        return self._parse_object_refs(r.content)

    # --- MUTAÇÕES (sempre passam pelo guard antes de tocar o sistema) ---------
    # Em modo read-only, guard.authorize() levanta MutationBlocked ANTES de
    # qualquer chamada HTTP. Só executam se writes forem habilitados no config,
    # com aprovação humana e request de transporte.
    async def update_source(self, ref: ObjectRef, new_source: str, description: str = "") -> None:
        change = ChangeRequest(
            operation="modify", target=ref.name, target_type=ref.type,
            system=self.system_name, uri=ref.uri, description=description,
        )
        approval = await self.guard.authorize(change)  # bloqueia aqui em read-only
        _ = approval  # a partir daqui usaríamos approval.transport como corrNr
        # O handshake real de escrita no ADT exige LOCK stateful + lock handle +
        # corrNr (transporte). A ser finalizado/validado no Communication Log ao
        # habilitar writes. Mantido barrado nesta versão.
        raise NotImplementedError("Escrita não habilitada nesta versão (somente-leitura).")

    async def delete_object(self, ref: ObjectRef, description: str = "") -> None:
        change = ChangeRequest(
            operation="delete", target=ref.name, target_type=ref.type,
            system=self.system_name, uri=ref.uri, description=description,
        )
        approval = await self.guard.authorize(change)  # bloqueia aqui em read-only
        _ = approval
        raise NotImplementedError("Exclusão não habilitada nesta versão (somente-leitura).")
