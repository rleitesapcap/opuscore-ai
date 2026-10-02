"""CLI de teste rápido. Uso:

    python -m opuscore.cli health
    python -m opuscore.cli report ZTMTB_PESAGEM
"""
from __future__ import annotations

import asyncio
import json

import typer
from rich import print
from rich.console import Console

from .agents import AbapDeveloperAgent
from .safety import ChangeRequest, MutationBlocked, build_guard
from .sap.adt_client import ADTClient, ObjectRef
from .settings import get_settings

cli = typer.Typer(add_completion=False)
console = Console()


def _adt(interactive: bool = True) -> ADTClient:
    s = get_settings()
    name = s.sap.default
    guard = build_guard(name, interactive=interactive)
    return ADTClient(s.sap.systems[name], guard=guard, system_name=name)


@cli.command()
def health():
    async def run():
        adt = _adt()
        try:
            await adt.discovery()
            print("[green]Conexão ADT OK[/green]")
            mode = "SOMENTE-LEITURA" if adt.read_only else "[red]ESCRITA HABILITADA[/red]"
            print(f"Modo: [bold]{mode}[/bold]")
        finally:
            await adt.aclose()
    asyncio.run(run())


@cli.command(name="test-guard")
def test_guard(object_name: str = "MARA", operation: str = "delete"):
    """Prova a trava: tenta uma mutação e mostra o bloqueio + registro de auditoria."""
    async def run():
        adt = _adt(interactive=False)
        try:
            ref = ObjectRef(name=object_name, type="TABL/DT",
                            uri=f"/sap/bc/adt/ddic/tables/{object_name}")
            change = ChangeRequest(operation=operation, target=ref.name,
                                   target_type=ref.type, system=adt.system_name, uri=ref.uri,
                                   description="teste de trava")
            try:
                await adt.guard.authorize(change)
                print("[red]FALHA DE SEGURANÇA: a operação NÃO foi bloqueada![/red]")
            except MutationBlocked as e:
                print(f"[green]Bloqueado como esperado:[/green] {e}")
                print("[cyan]Registro gravado na trilha de auditoria.[/cyan]")
        finally:
            await adt.aclose()
    asyncio.run(run())


@cli.command()
def report(object_name: str, save_graph: str = typer.Option("", help="Salva o grafo JSON")):
    async def run():
        adt = _adt()
        try:
            agent = AbapDeveloperAgent(adt)
            out = await agent.report_on_object(object_name)
            console.rule(f"Relatório — {object_name}")
            print(out["narrative"])
            console.rule("Evidência (grafo do Cérebro)")
            print(f"Nós: {len(out['graph']['nodes'])} | Arestas: {len(out['graph']['links'])}")
            if save_graph:
                with open(save_graph, "w", encoding="utf-8") as f:
                    json.dump(out["graph"], f, ensure_ascii=False, indent=2)
                print(f"[cyan]Grafo salvo em {save_graph}[/cyan]")
        finally:
            await adt.aclose()
    asyncio.run(run())


@cli.command()
def remediate(object_name: str, save: str = typer.Option("", help="Salva o relatório .md")):
    """Relatório de remediação (evidência ADT + rubrica Clean Core + plano)."""
    from .developer import gen_remediation
    from .llm import build_provider
    from .sap.analyzer import build_object_report

    async def run():
        adt = _adt(interactive=False)
        try:
            report = await build_object_report(adt, object_name)
            out = await gen_remediation(build_provider(), object_name, report.to_dict())
            console.rule(f"Remediação — {object_name}")
            print(out)
            if save:
                open(save, "w", encoding="utf-8").write(out); print(f"[cyan]salvo em {save}[/cyan]")
        finally:
            await adt.aclose()
    asyncio.run(run())


@cli.command(name="tech-spec")
def tech_spec(ef_file: str, out: str = typer.Option("ET.md", help="Arquivo de saída")):
    """Gera Especificação Técnica (ET) a partir de um arquivo de EF. Não precisa de SAP."""
    from .developer import gen_tech_spec
    from .llm import build_provider

    ef = open(ef_file, encoding="utf-8").read()
    content = asyncio.run(gen_tech_spec(build_provider(), ef))
    open(out, "w", encoding="utf-8").write(content)
    console.rule("Especificação Técnica"); print(content); print(f"[cyan]salvo em {out}[/cyan]")


@cli.command()
def rap(ef_file: str, out: str = typer.Option("rap_skeleton.abap", help="Arquivo de saída")):
    """Gera esqueleto RAP Clean Core (rascunho) a partir de uma EF. Não escreve no SAP."""
    from .developer import gen_rap_skeleton
    from .llm import build_provider

    ef = open(ef_file, encoding="utf-8").read()
    content = asyncio.run(gen_rap_skeleton(build_provider(), ef))
    open(out, "w", encoding="utf-8").write(content)
    console.rule("Esqueleto RAP (rascunho)"); print(content); print(f"[cyan]salvo em {out}[/cyan]")


if __name__ == "__main__":
    cli()
