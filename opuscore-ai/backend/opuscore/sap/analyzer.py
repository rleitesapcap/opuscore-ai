"""Orquestra a 1ª capacidade do Desenvolvedor ABAP:
'monte um relatório sobre a tabela Z / programa Z'.

Retorna EVIDÊNCIA estruturada (não texto solto): fonte real, metadados e
where-used, cada item carimbado com o endpoint ADT de origem. É essa evidência
que o agente entrega ao LLM — o modelo narra, mas não inventa (Evidence Ledger).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .adt_client import ADTClient, ObjectRef


@dataclass
class Evidence:
    """Um fato + de onde ele veio (para rastreabilidade / anti-alucinação)."""
    fact: str
    source: str  # endpoint ADT que produziu o fato


@dataclass
class ObjectReport:
    name: str
    type: str
    uri: str
    package: str = ""
    description: str = ""
    source_code: str = ""
    fields: list[dict] = field(default_factory=list)
    used_by: list[dict] = field(default_factory=list)   # objetos que usam este
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["evidence"] = [asdict(e) for e in self.evidence]
        return d


async def build_object_report(adt: ADTClient, name: str) -> ObjectReport:
    ref = await adt.resolve(name)
    report = ObjectReport(
        name=ref.name, type=ref.type, uri=ref.uri,
        package=ref.package, description=ref.description,
    )
    report.evidence.append(
        Evidence(f"Objeto resolvido: {ref.name} ({ref.type})", "informationsystem/search")
    )

    is_table = ref.type.startswith("TABL")
    if is_table:
        detail = await adt.get_table(ref.name)
        report.fields = detail.metadata.get("fields", [])
        report.description = report.description or detail.metadata.get("description", "")
        report.evidence.append(
            Evidence(f"{len(report.fields)} campos lidos do DDIC", "ddic/tables")
        )
    else:
        src = await adt.get_source(ref)
        report.source_code = src
        if src:
            report.evidence.append(
                Evidence(f"Source lido ({len(src.splitlines())} linhas)", f"{ref.uri}/source/main")
            )

    used = await adt.where_used(ref)
    report.used_by = [
        {"name": u.name, "type": u.type, "package": u.package, "uri": u.uri}
        for u in used
    ]
    report.evidence.append(
        Evidence(f"{len(used)} objetos referenciam {ref.name}", "informationsystem/usageReferences")
    )
    return report


def report_to_graph(report: ObjectReport, domain: str = "abap") -> dict:
    """Transforma o relatório no formato do Cérebro (nós + arestas)."""
    center = {"id": report.name, "label": report.name, "type": report.type,
              "domain": domain, "kind": "focus"}
    nodes = [center]
    links = []
    seen = {report.name}
    for u in report.used_by:
        if u["name"] not in seen:
            nodes.append({"id": u["name"], "label": u["name"], "type": u["type"],
                          "domain": domain, "kind": "user"})
            seen.add(u["name"])
        links.append({"source": u["name"], "target": report.name, "kind": "uses"})
    return {"nodes": nodes, "links": links}
