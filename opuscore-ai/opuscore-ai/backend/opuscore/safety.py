"""Travas de segurança do OPUSCORE-AI.

Regra inegociável: a ferramenta NÃO altera nem exclui objetos no SAP/BTP.
- Por padrão opera em modo SOMENTE-LEITURA (read_only=True). Nesse modo, qualquer
  tentativa de mutação é bloqueada ANTES de qualquer chamada ao sistema.
- Só se o read-only for explicitamente desligado é que uma mutação pode ocorrer,
  e ainda assim exige: (1) aprovação humana explícita, (2) request/transporte
  informada, (3) registro em trilha de auditoria append-only.

Vale para SAP (ADT) e BTP — o guard é agnóstico de backend.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

log = logging.getLogger("opuscore.audit")


class MutationBlocked(RuntimeError):
    """Levantada sempre que uma alteração/exclusão é impedida."""


@dataclass
class ChangeRequest:
    operation: str              # "modify" | "delete" | "create"
    target: str                 # nome do objeto
    target_type: str = ""
    system: str = ""            # sistema SAP/BTP alvo
    uri: str = ""
    description: str = ""
    requested_by: str = ""
    requires_transport: bool = True


@dataclass
class Approval:
    granted: bool
    transport: str = ""
    approver: str = ""
    reason: str = ""


class AuditLog:
    """Trilha de auditoria append-only (JSON Lines). Nunca sobrescreve linhas."""

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, **fields) -> dict:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields,
        }
        line = json.dumps(entry, ensure_ascii=False)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        log.info("AUDIT %s", line)
        return entry


class ApprovalProvider(Protocol):
    async def request(self, change: ChangeRequest) -> Approval: ...


class DenyByDefault:
    """Sem interação humana disponível (ex.: chamada via API) -> nega. Fail-safe."""

    async def request(self, change: ChangeRequest) -> Approval:
        return Approval(granted=False, reason="Sem provedor de aprovação interativo")


class InteractiveCLIApproval:
    """Pede permissão e a request de transporte no terminal, de forma síncrona."""

    async def request(self, change: ChangeRequest) -> Approval:
        def ask() -> Approval:
            print("\n" + "=" * 62)
            print(" !!! SOLICITACAO DE ALTERACAO NO SAP/BTP !!!")
            print(f"  Operacao : {change.operation.upper()}")
            print(f"  Objeto   : {change.target} ({change.target_type})")
            print(f"  Sistema  : {change.system}")
            if change.description:
                print(f"  Detalhe  : {change.description}")
            print("=" * 62)
            if input("Confirma esta operacao? (digite SIM para aprovar): ").strip() != "SIM":
                return Approval(granted=False, reason="Usuario nao confirmou")
            transport = ""
            if change.requires_transport:
                transport = input(
                    "Informe a REQUEST/transporte para gravar (ex.: DEVK900123): "
                ).strip()
                if not transport:
                    return Approval(granted=False, reason="Request nao informada")
            default_user = os.environ.get("USER") or os.environ.get("USERNAME") or ""
            approver = input(f"Seu identificador (aprovador) [{default_user}]: ").strip() or default_user
            return Approval(granted=True, transport=transport, approver=approver)

        return await asyncio.to_thread(ask)


class MutationGuard:
    """Portão único por onde qualquer alteração/exclusão TEM que passar."""

    def __init__(
        self,
        read_only: bool,
        audit: AuditLog,
        approval: ApprovalProvider,
        require_transport: bool = True,
    ):
        self.read_only = read_only
        self.audit = audit
        self.approval = approval
        self.require_transport = require_transport

    async def authorize(self, change: ChangeRequest) -> Approval:
        self.audit.record("mutation_requested", **asdict(change))

        # --- TRAVA DURA: por padrão a ferramenta é somente-leitura ---
        if self.read_only:
            self.audit.record(
                "blocked_read_only",
                target=change.target, operation=change.operation, system=change.system,
            )
            raise MutationBlocked(
                "Ferramenta em modo SOMENTE-LEITURA: alterar/excluir objetos no "
                "SAP/BTP esta bloqueado por politica. Tentativa registrada em auditoria."
            )

        # Daqui pra baixo só roda se writes forem explicitamente habilitados.
        approval = await self.approval.request(change)
        if not approval.granted:
            self.audit.record(
                "denied", target=change.target, operation=change.operation, reason=approval.reason
            )
            raise MutationBlocked(f"Operacao negada: {approval.reason}")

        if change.requires_transport and self.require_transport and not approval.transport:
            self.audit.record(
                "denied_no_transport", target=change.target, operation=change.operation
            )
            raise MutationBlocked("Nenhuma request de transporte informada. Operacao bloqueada.")

        self.audit.record(
            "approved",
            target=change.target, operation=change.operation,
            transport=approval.transport, approver=approval.approver, system=change.system,
        )
        return approval


def build_guard(system_name: str, interactive: bool = False) -> MutationGuard:
    """Monta o guard a partir do config (import tardio para evitar ciclo)."""
    from .settings import get_settings

    s = get_settings()
    sys = s.sap.systems[system_name]
    audit = AuditLog(s.safety.audit_log_path)
    approval: ApprovalProvider = InteractiveCLIApproval() if interactive else DenyByDefault()
    return MutationGuard(
        read_only=sys.read_only,
        audit=audit,
        approval=approval,
        require_transport=s.safety.require_transport,
    )
