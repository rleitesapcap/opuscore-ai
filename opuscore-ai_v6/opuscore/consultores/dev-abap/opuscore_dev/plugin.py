"""Plugin do Consultor Desenvolvedor ABAP."""
from __future__ import annotations

from pathlib import Path

from opuscore_core.contratos.eventos import validar_payload
from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase, WebManifesto


class DevAbapPlugin(PluginBase):
    manifesto = Manifesto(key="dev-abap", nome="Desenvolvedor ABAP", area="Desenvolvimento",
                          especialidade="ABAP e remediação", trabalho_atual="Aguardando EF aprovada",
                          web=WebManifesto(rota="dev", css="dev.css"),
                          assina={"ef.validada": "ao_receber_ef_validada"})

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(
            persona="Desenvolvedor ABAP/RAP sênior; especialista em ABAP Cloud e S/4HANA.",
            instrucoes="Analise objetos via ADT (source, DDIC, where-used), avalie impacto e Clean Core. Somente leitura.",
            skills=["Análise de Objeto", "Clean Core Check", "Gerar ET", "Remediação"])

    def rotas(self, obter_ctx):
        from .rotas.dev import criar_router
        return criar_router(obter_ctx)

    @property
    def web_dir(self) -> Path:
        return Path(__file__).parent / "web"

    async def ao_receber_ef_validada(self, evento, ctx) -> None:
        """Idempotente: confere o contrato e registra. O handoff (fila do Dev) é criado
        pelo Orquestrador; a tela do Dev usa o upload da EF sem pedir outro."""
        p = validar_payload(evento.tipo, evento.versao, evento.payload)
        ctx.auditoria.registrar("ef_validada_recebida", evento_id=evento.id, gap=evento.gap_id,
                                objetos=len(p["objetos_no_escopo"]), upload_id=p["upload_id"])


PLUGIN = DevAbapPlugin()
