"""Barramento de eventos com outbox, novas tentativas e fila de falhas + handoffs.

Garantia: entrega "pelo menos uma vez". Todo tratador de consultor deve ser
idempotente (o mesmo evento pode chegar de novo depois de uma falha).
Começa no mesmo processo; a interface permite trocar o transporte (Redis Streams,
SAP Integration Suite advanced event mesh) sem mudar os consultores.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Awaitable, Callable

from opuscore_core.contratos.eventos import Evento, validar_payload
from opuscore_core.contratos.handoff import EstadoHandoff, pode_transitar
from sqlmodel import select

from .modelos import EntregaEvento, EventoRegistro, HandoffRegistro, agora

log = logging.getLogger("opuscore.orquestrador")
Tratador = Callable[[Evento, Any], Awaitable[None]]

# Primeiro passo rumo aos fluxos declarados: quais handoffs cada evento abre.
ROTEAMENTO_PADRAO: dict[str, list[tuple[str, str]]] = {
    "ef.validada": [("dev-abap", "Etapa 2: descoberta técnica a partir da EF validada")],
}

ACOES = {"aceitar": EstadoHandoff.ACEITO, "iniciar": EstadoHandoff.EM_ANDAMENTO,
         "concluir": EstadoHandoff.CONCLUIDO, "devolver": EstadoHandoff.DEVOLVIDO,
         "cancelar": EstadoHandoff.CANCELADO}


def _com_fuso(d):
    from datetime import timezone
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


class Publicador:
    def __init__(self, orq: "Orquestrador", origem: str):
        self.orq, self.origem = orq, origem

    async def publicar(self, tipo, *, projeto_id, gap_id, payload, artefatos=(), versao=1, causa_id=None) -> str:
        ev = Evento(tipo=tipo, versao=versao, projeto_id=projeto_id, gap_id=gap_id or "SEM-GAP",
                    origem=self.origem, causa_id=causa_id, payload=validar_payload(tipo, versao, payload),
                    artefatos=list(artefatos))
        return await self.orq.publicar(ev)


class Orquestrador:
    def __init__(self, sessao: Callable, contexto_para: Callable[[str], Any], *,
                 roteamento: dict | None = None, max_tentativas: int = 5, intervalo: float = 1.0):
        self.sessao, self.contexto_para = sessao, contexto_para
        self.roteamento = ROTEAMENTO_PADRAO if roteamento is None else roteamento
        self.max_tentativas, self.intervalo = max_tentativas, intervalo
        self.assinaturas: dict[str, list[tuple[str, str, Tratador]]] = {}
        self._tarefa: asyncio.Task | None = None
        self._acordar = asyncio.Event()

    # --- assinaturas -------------------------------------------------------
    def assinar(self, tipo: str, destino: str, nome_tratador: str, tratador: Tratador) -> None:
        self.assinaturas.setdefault(tipo, []).append((destino, nome_tratador, tratador))

    def assinar_plugins(self, plugins: list) -> None:
        for p in plugins:
            for tipo, metodo in (p.manifesto.assina or {}).items():
                fn = getattr(p, metodo, None)
                if fn is None:
                    log.warning("Plugin %s assina %s, mas não tem o método %s", p.manifesto.key, tipo, metodo)
                    continue
                self.assinar(tipo, p.manifesto.key, metodo, fn)

    def publicador(self, origem: str) -> Publicador:
        return Publicador(self, origem)

    # --- publicação (outbox) ----------------------------------------------
    async def publicar(self, ev: Evento) -> str:
        with self.sessao() as s:
            s.add(EventoRegistro(id=ev.id, tipo=ev.tipo, versao=ev.versao, projeto_id=ev.projeto_id,
                                 gap_id=ev.gap_id, origem=ev.origem, causa_id=ev.causa_id,
                                 payload=ev.payload, artefatos=ev.artefatos,
                                 ocorrido_em=ev.ocorrido_em))
            s.flush()
            for destino, nome, _ in self.assinaturas.get(ev.tipo, []):
                s.add(EntregaEvento(evento_id=ev.id, destino=destino, tratador=nome))
            for para, titulo in self.roteamento.get(ev.tipo, []):
                s.add(HandoffRegistro(projeto_id=ev.projeto_id, gap_id=ev.gap_id, de=ev.origem, para=para,
                                      titulo=titulo, evento_id=ev.id, payload=ev.payload, artefatos=ev.artefatos,
                                      historico=[{"estado": "CRIADO", "em": agora().isoformat(), "por": ev.origem}]))
            s.commit()
        self._acordar.set()
        return ev.id

    # --- entrega ------------------------------------------------------------
    def _tratador(self, destino: str, nome: str) -> Tratador | None:
        for tipo_lista in self.assinaturas.values():
            for d, n, fn in tipo_lista:
                if d == destino and n == nome:
                    return fn
        return None

    async def processar_pendentes(self) -> int:
        with self.sessao() as s:
            pend = s.exec(select(EntregaEvento).where(EntregaEvento.status == "PENDENTE",
                                                      EntregaEvento.proximo_em <= agora())).all()
            trabalho = [(e.id, e.destino, e.tratador, s.get(EventoRegistro, e.evento_id)) for e in pend]
        feitas = 0
        for eid, destino, nome, reg in trabalho:
            ev = Evento(id=reg.id, tipo=reg.tipo, versao=reg.versao, projeto_id=reg.projeto_id, gap_id=reg.gap_id,
                        origem=reg.origem, causa_id=reg.causa_id, payload=reg.payload, artefatos=reg.artefatos,
                        ocorrido_em=_com_fuso(reg.ocorrido_em))
            fn = self._tratador(destino, nome)
            erro = ""
            try:
                if fn is None:
                    raise RuntimeError(f"Consultor {destino} não está instalado ou não tem o tratador {nome}.")
                await fn(ev, self.contexto_para(destino))
            except Exception as e:  # noqa: BLE001 - qualquer falha vira nova tentativa
                erro = f"{type(e).__name__}: {e}"
            with self.sessao() as s:
                ent = s.get(EntregaEvento, eid)
                ent.atualizado_em = agora()
                if not erro:
                    ent.status, ent.erro = "ENTREGUE", ""
                    feitas += 1
                else:
                    ent.tentativas += 1
                    ent.erro = erro[:2000]
                    if ent.tentativas >= self.max_tentativas:
                        ent.status = "FALHA"
                        log.error("Entrega %s -> %s foi para a fila de falhas: %s", eid, destino, erro)
                    else:
                        ent.proximo_em = agora() + timedelta(seconds=2 ** ent.tentativas)
                s.add(ent)
                s.commit()
        return feitas

    def reprocessar(self, entrega_id: str) -> None:
        with self.sessao() as s:
            ent = s.get(EntregaEvento, entrega_id)
            if ent is None:
                raise KeyError(entrega_id)
            ent.status, ent.tentativas, ent.proximo_em, ent.erro = "PENDENTE", 0, agora(), ""
            s.add(ent)
            s.commit()
        self._acordar.set()

    async def _laco(self) -> None:
        while True:
            try:
                await self.processar_pendentes()
            except Exception:  # noqa: BLE001
                log.exception("Falha no laço do orquestrador")
            try:
                await asyncio.wait_for(self._acordar.wait(), timeout=self.intervalo)
            except asyncio.TimeoutError:
                pass
            self._acordar.clear()

    def iniciar(self) -> None:
        if self._tarefa is None:
            self._tarefa = asyncio.create_task(self._laco())

    async def parar(self) -> None:
        if self._tarefa:
            self._tarefa.cancel()
            try:
                await self._tarefa
            except asyncio.CancelledError:
                pass
            self._tarefa = None

    # --- handoffs -------------------------------------------------------------
    def listar_handoffs(self, *, projeto_id: str | None = None, para: str | None = None,
                        estado: str | None = None, gap_id: str | None = None) -> list[dict]:
        with self.sessao() as s:
            q = select(HandoffRegistro)
            for col, val in ((HandoffRegistro.projeto_id, projeto_id), (HandoffRegistro.para, para),
                             (HandoffRegistro.estado, estado), (HandoffRegistro.gap_id, gap_id)):
                if val:
                    q = q.where(col == val)
            return [h.model_dump(mode="json") for h in s.exec(q.order_by(HandoffRegistro.criado_em.desc())).all()]

    def transitar(self, handoff_id: str, acao: str, *, motivo: str = "", por: str = "") -> dict:
        if acao not in ACOES:
            raise ValueError(f"Ação inválida: {acao}. Use {', '.join(ACOES)}.")
        novo = ACOES[acao]
        with self.sessao() as s:
            h = s.get(HandoffRegistro, handoff_id)
            if h is None:
                raise KeyError(handoff_id)
            atual = EstadoHandoff(h.estado)
            if not pode_transitar(atual, novo):
                raise ValueError(f"Não dá para {acao} um handoff em {atual.value}.")
            if novo == EstadoHandoff.DEVOLVIDO and not motivo.strip():
                raise ValueError("Para devolver, informe o motivo.")
            h.estado, h.motivo, h.atualizado_em = novo.value, motivo or h.motivo, agora()
            h.historico = [*h.historico, {"estado": novo.value, "em": agora().isoformat(), "por": por,
                                          "motivo": motivo}]
            s.add(h)
            s.commit()
            s.refresh(h)
            return h.model_dump(mode="json")

    # --- painel ------------------------------------------------------------------
    def painel(self, projeto_id: str) -> dict:
        with self.sessao() as s:
            evs = s.exec(select(EventoRegistro).where(EventoRegistro.projeto_id == projeto_id)
                         .order_by(EventoRegistro.ocorrido_em)).all()
            hs = s.exec(select(HandoffRegistro).where(HandoffRegistro.projeto_id == projeto_id)).all()
            falhas = s.exec(select(EntregaEvento).where(EntregaEvento.status == "FALHA")).all()
        gaps: dict[str, dict] = {}
        for e in evs:
            g = gaps.setdefault(e.gap_id, {"gap_id": e.gap_id, "eventos": [], "handoffs": []})
            g["eventos"].append({"id": e.id, "tipo": e.tipo, "origem": e.origem, "em": e.ocorrido_em.isoformat()})
        for h in hs:
            gaps.setdefault(h.gap_id, {"gap_id": h.gap_id, "eventos": [], "handoffs": []})["handoffs"].append(
                h.model_dump(mode="json"))
        pend = {}
        for h in hs:
            if h.estado in ("CRIADO", "ACEITO", "EM_ANDAMENTO"):
                pend[h.para] = pend.get(h.para, 0) + 1
        return {"gaps": sorted(gaps.values(), key=lambda g: g["gap_id"]), "pendentes_por_consultor": pend,
                "falhas": [f.model_dump(mode="json") for f in falhas]}
