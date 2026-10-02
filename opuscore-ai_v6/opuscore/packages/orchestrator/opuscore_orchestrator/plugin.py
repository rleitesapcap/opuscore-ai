"""O Orquestrador também aparece na lista de consultores, com a sua tela (painel)."""
from __future__ import annotations

from pathlib import Path

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase, WebManifesto


class OrquestradorPlugin(PluginBase):
    manifesto = Manifesto(key="orquestrador", nome="Orquestrador", area="Coordenação", especialidade="Fluxo e gates",
                          trabalho_atual="Handoffs e fluxos do projeto", web=WebManifesto(rota="orquestrador", css="orquestrador.css"))

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(
            persona="Orquestrador do squad: coordena tarefas, aprovações e handoffs entre consultores.",
            instrucoes="Coordene o fluxo (gates, tarefas, handoffs). Não invente decisões nem aprove em nome do usuário.",
            skills=["Handoffs entre consultores", "Linha do tempo por GAP"])

    @property
    def web_dir(self) -> Path:
        return Path(__file__).parent / "web"


PLUGIN = OrquestradorPlugin()
