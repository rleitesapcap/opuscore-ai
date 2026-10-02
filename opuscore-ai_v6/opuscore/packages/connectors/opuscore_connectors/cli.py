"""CLI dos Conectores. Uso:
    python -m opuscore_connectors.cli health
    python -m opuscore_connectors.cli ferramentas
    python -m opuscore_connectors.cli test-guard --object-name MARA
    python -m opuscore_connectors.cli relatorio ZSDR_FOB_ENQUEUE_REQUEST
"""
from __future__ import annotations

import asyncio
import json

import typer
from rich import print

cli = typer.Typer(add_completion=False)


@cli.command()
def health(ambiente: str = ""):
    from .sap_adt.ferramentas import sap_health
    print(json.loads(asyncio.run(sap_health(ambiente))))


@cli.command()
def ferramentas():
    import opuscore_connectors.sap_adt.ferramentas  # noqa: F401 - registra
    from .comum.registro import ferramentas as lista
    for f in lista():
        print(f"[cyan]{f['nome']}[/cyan]  sistema={f['sistema']}  nível={f['nivel']}")


@cli.command()
def relatorio(object_name: str, ambiente: str = ""):
    from .sap_adt.ferramentas import sap_object_report
    print(json.loads(asyncio.run(sap_object_report(object_name, ambiente))))


@cli.command(name="test-guard")
def test_guard(object_name: str = "MARA", operation: str = "delete", ambiente: str = ""):
    """Prova a trava: tenta uma mutação e mostra o bloqueio + registro de auditoria."""
    from .seguranca.guard import ChangeRequest, MutationBlocked
    from .sap_adt.ferramentas import _adt

    async def run():
        adt = _adt(ambiente)
        try:
            change = ChangeRequest(operation=operation, target=object_name, target_type="TABL/DT",
                                   system=adt.system_name, uri=f"/sap/bc/adt/ddic/tables/{object_name}",
                                   description="teste de trava")
            try:
                await adt.guard.authorize(change)
                print("[red]FALHA DE SEGURANÇA: a operação NÃO foi bloqueada![/red]")
            except MutationBlocked as e:
                print(f"[green]Bloqueado como esperado:[/green] {e}")
        finally:
            await adt.aclose()
    asyncio.run(run())


if __name__ == "__main__":
    cli()
