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

import re
from dataclasses import dataclass, field
from urllib.parse import quote

import httpx
from lxml import etree

from opuscore_core.contratos.sap import ObjectRef  # noqa: F401 - reexportado

from ..config import SapSystemCfg
from ..seguranca.guard import ChangeRequest, MutationGuard, build_guard


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


_Z_TOKEN = re.compile(r"\b([ZzYy][A-Za-z0-9_]{2,})\b")

# linha de campo no source de tabela: "[key] nome : tipo [not null];"
_TAB_FIELD = re.compile(
    r"^\s*(key\s+)?([A-Za-z_/][A-Za-z0-9_/]*)\s*:\s*([A-Za-z0-9_/]+(?:\([^)]*\))?)\s*(not\s+null)?\s*;",
    re.IGNORECASE,
)
_TAB_INCLUDE = re.compile(r"^\s*include\s+([A-Za-z0-9_/]+)", re.IGNORECASE)
_TAB_LABEL = re.compile(r"@EndUserText\.label\s*:\s*'([^']*)'", re.IGNORECASE)


_TAB_DELIVERY = re.compile(r"@AbapCatalog\.deliveryClass\s*:\s*#([A-Za-z])")


def _parse_table_source(source: str) -> dict:
    """Extrai descrição, campos, chaves e includes do source 'define table'."""
    fields, includes = [], []
    desc = ""
    m = _TAB_LABEL.search(source)
    if m:
        desc = m.group(1)
    for line in source.splitlines():
        s = line.strip()
        if not s or s.startswith(("//", "@", "*")):
            continue
        inc = _TAB_INCLUDE.match(line)
        if inc:
            includes.append(inc.group(1).upper())
            continue
        f = _TAB_FIELD.match(line)
        if f:
            fields.append({
                "name": f.group(2).upper(),
                "key": bool(f.group(1)),
                "type": f.group(3).upper(),
                "not_null": bool(f.group(4)),
            })
    dc = _TAB_DELIVERY.search(source)
    return {"description": desc, "fields": fields, "includes": includes,
            "delivery_class": dc.group(1).upper() if dc else ""}


def _extract_z_refs(source: str) -> list[str]:
    """Extrai identificadores Z*/Y* do source ABAP (ignora comentários de linha
    inteira). São candidatos a objeto — a resolução no repositório descarta o que
    não existe (variáveis, palavras que só parecem objeto)."""
    refs: set[str] = set()
    for line in source.splitlines():
        if line.lstrip().startswith("*"):  # comentário de linha inteira
            continue
        for tok in _Z_TOKEN.findall(line):
            refs.add(tok.upper())
    return sorted(refs)


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
        """Resolve nome -> ObjectRef (tipo + uri).

        1ª tentativa: busca exata. 2ª: com curinga (NOME*), porque o quickSearch
        de alguns releases só devolve o objeto com o curinga. Em ambos os casos,
        só aceita o objeto cujo nome é EXATAMENTE o pedido."""
        nome = (name or "").strip().upper()
        for consulta in (nome, f"{nome}*"):
            for ref in await self.search(consulta, max_results=50):
                if ref.name.upper() == nome:
                    return ref
        raise ADTError(f"Objeto não encontrado no repositório: {nome}")

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

    async def table_contents(self, name: str, max_rows: int = 200) -> dict:
        """Conteúdo de uma tabela/view via ADT Data Preview (leitura).

        POST /sap/bc/adt/datapreview/ddic?ddicEntityName=<tabela>&rowNumber=<n>.
        É POST, mas não altera nada (o ADT não grava por este serviço); exige token
        CSRF. A resposta traz, por coluna, os metadados (nome, descrição) e os valores.
        Quem decide QUAIS tabelas podem ser lidas é a camada acima (ferramenta MCP).
        """
        await self._ensure_csrf()
        params = {"ddicEntityName": name.upper(), "rowNumber": max(1, min(int(max_rows), 1000))}
        headers = {"x-csrf-token": self._csrf or "",
                   "Accept": "application/vnd.sap.adt.datapreview.table.v1+xml, application/*"}
        r = await self._client.post("/sap/bc/adt/datapreview/ddic", params=params, headers=headers, content=b"")
        if r.status_code == 403 and "csrf" in r.text.lower():      # token expirou: renova uma vez
            self._csrf = None
            await self._ensure_csrf()
            headers["x-csrf-token"] = self._csrf or ""
            r = await self._client.post("/sap/bc/adt/datapreview/ddic", params=params, headers=headers, content=b"")
        if r.status_code == 404:
            raise ADTError(f"Tabela {name.upper()} não encontrada no SAP conectado.")
        if r.status_code >= 400:
            raise ADTError(f"Não consegui ler o conteúdo de {name.upper()} (HTTP {r.status_code}). {r.text[:200]}")
        return self._parse_data_preview(r.content)

    @staticmethod
    def _parse_data_preview(content: bytes) -> dict:
        try:
            root = etree.fromstring(content)
        except etree.XMLSyntaxError:
            raise ADTError("A resposta do Data Preview não é um XML válido.")
        colunas, valores, total = [], [], None
        for el in root.iter():
            nome = _local(el.tag)
            if nome == "totalRows" and (el.text or "").strip().isdigit():
                total = int(el.text.strip())
            elif nome == "columns":
                meta = next((c for c in el.iter() if _local(c.tag) == "metadata"), None)
                if meta is None:
                    continue
                colunas.append({"name": _attr(meta, "name"), "description": _attr(meta, "description")})
                valores.append([(d.text or "") for d in el.iter() if _local(d.tag) == "data"])
        n = max((len(v) for v in valores), default=0)
        linhas = [{c["name"]: (valores[i][j] if j < len(valores[i]) else "") for i, c in enumerate(colunas)}
                  for j in range(n)]
        return {"columns": colunas, "rows": linhas, "total": total if total is not None else n}

    async def get_table(self, name: str) -> ObjectDetail:
        """Estrutura de tabela DDIC (campos, chaves).

        Em releases recentes o ADT expõe a tabela como SOURCE ("define table ...
        { key campo : tipo; ... }"), não como XML de metadados — pedir XML retorna
        406 Not Acceptable. Estratégia: 1) source/main (text/plain) e parse do
        'define table'; 2) fallback para o XML de metadados. Não levanta exceção
        por 406: devolve o que conseguiu e registra a limitação em metadata.
        """
        base = f"/sap/bc/adt/ddic/tables/{quote(name)}"
        # 1) source da tabela
        r = await self._client.get(f"{base}/source/main", headers={"Accept": "text/plain"})
        if r.status_code == 200 and r.text.strip():
            detail = ObjectDetail(
                ref=ObjectRef(name=name, type="TABL/DT", uri=base), source=r.text
            )
            detail.metadata = _parse_table_source(r.text)
            detail.metadata["read_via"] = "source/main"
            return detail
        # 2) fallback: XML de metadados (releases antigos)
        r2 = await self._client.get(base, headers={"Accept": "application/*"})
        if r2.status_code == 200:
            detail = self._parse_table(name, r2.content)
            detail.metadata["read_via"] = "metadata-xml"
            return detail
        detail = ObjectDetail(ref=ObjectRef(name=name, type="TABL/DT", uri=base))
        detail.metadata = {
            "fields": [],
            "read_error": f"source HTTP {r.status_code}; metadados HTTP {r2.status_code}",
        }
        return detail

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

    # --- objetos de uma request de transporte -------------------------------
    # tipo de conteúdo exigido pelo CTS no ADT (sem ele o SAP responde 406 Not Acceptable)
    _CTS_ACCEPT = "application/vnd.sap.adt.transportorganizer.v1+xml"
    # subobjetos LIMU -> objeto principal (a ET é por objeto, não por método/include isolado)
    _LIMU_CLASSE = {"METH", "CINC", "CPUB", "CPRO", "CPRI", "CLSD", "CDEF", "CIMP", "CLAS"}
    _LIMU_PROPRIO = {"REPS", "REPT", "FUNC", "DYNP", "INTD"}

    async def transport_objects(self, request_id: str) -> list[ObjectRef]:
        """Lista os objetos de uma request/task de transporte (CTS via ADT).

        O endpoint exige Accept: application/vnd.sap.adt.transportorganizer.v1+xml.
        Os objetos vêm como <tm:abap_object tm:pgmid tm:type tm:name/>, inclusive
        dentro das tasks. R3TR = objeto principal; LIMU = subobjeto, mapeado para o
        objeto principal (ex.: método -> classe). Sem duplicatas, na ordem da request.
        """
        rid = (request_id or "").strip().upper()
        url = f"/sap/bc/adt/cts/transportrequests/{quote(rid)}"
        r = await self._client.get(url, headers={"Accept": self._CTS_ACCEPT})
        if r.status_code == 406:   # alguns releases aceitam a lista combinada
            r = await self._client.get(url, headers={"Accept": f"{self._CTS_ACCEPT}, application/xml"})
        if r.status_code == 404:
            raise ADTError(f"Request {rid} não encontrada no SAP conectado.")
        if r.status_code >= 400:
            raise ADTError(f"Não consegui ler a request {rid} (HTTP {r.status_code}). {r.text[:200]}")

        refs: list[ObjectRef] = []
        vistos: set[tuple[str, str]] = set()

        def add(nome: str, tipo: str) -> None:
            nome = (nome or "").strip()
            chave = (nome.upper(), tipo.upper())
            if nome and chave not in vistos:
                vistos.add(chave)
                refs.append(ObjectRef(name=nome, type=tipo))

        try:
            root = etree.fromstring(r.content)
        except etree.XMLSyntaxError:
            raise ADTError(f"A resposta do CTS para a request {rid} não é um XML válido.")
        for el in root.iter():
            if _local(el.tag) != "abap_object":
                continue
            pgmid = (_attr(el, "pgmid") or "R3TR").upper()
            tipo = (_attr(el, "type") or _attr(el, "obj_type")).upper()
            nome = _attr(el, "name") or _attr(el, "obj_name")
            if not nome:
                continue
            if pgmid == "R3TR":
                add(nome, tipo)
            elif pgmid == "LIMU":
                if tipo in self._LIMU_CLASSE:
                    add(nome.split()[0][:30], "CLAS")        # "ZCL_X   METODO" -> ZCL_X
                elif tipo in self._LIMU_PROPRIO:
                    add(nome.split()[0], tipo)
        if not refs:   # formato alternativo: referências adtcore
            refs = self._parse_object_refs(r.content)
        return refs

    # --- dependências Z (forward): o que o objeto USA, só Z/Y, recursivo ------
    async def z_dependencies(self, object_name: str, max_depth: int = 2,
                             max_objects: int = 200) -> list[dict]:
        """Descobre os objetos Z/Y que o objeto usa (includes, classes, FMs, tabelas…).

        Baseado no source: extrai identificadores Z*/Y*, resolve cada um no
        repositório (descarta o que não existe, ex.: variáveis) e recorre em
        programas/includes/classes. Objetos standard são ignorados de propósito.
        Retorna o objeto-semente + suas dependências Z, sem duplicar.
        """
        visited: set[str] = set()
        found: dict[str, dict] = {}

        async def crawl(name: str, depth: int, is_seed: bool) -> None:
            key = name.upper()
            if key in visited or len(found) >= max_objects:
                return
            visited.add(key)
            try:
                ref = await self.resolve(name)
            except ADTError:
                return  # token que não é objeto real (variável, palavra-chave…)
            if not ref.name.upper().startswith(("Z", "Y")):
                return  # só custom; standard é ignorado de propósito
            found[key] = {"name": ref.name, "type": ref.type, "package": ref.package,
                          "uri": ref.uri, "seed": is_seed, "depth": depth}
            src = "" if ref.type.startswith("TABL") else await self.get_source(ref)
            if depth < max_depth and src:
                for tok in _extract_z_refs(src):
                    if tok != key and tok not in visited:
                        await crawl(tok, depth + 1, False)

        await crawl(object_name, 0, True)
        return list(found.values())

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
