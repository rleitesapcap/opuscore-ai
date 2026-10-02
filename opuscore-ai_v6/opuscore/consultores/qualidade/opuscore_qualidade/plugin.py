"""Plugin do Analista de Qualidade. Hoje atua pelo chat comum (Conversar). Para dar tela e rotas
próprias: implemente rotas(obter_ctx), web_dir e declare web=WebManifesto(...)."""
from __future__ import annotations

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase


class Plugin(PluginBase):
    manifesto = Manifesto(key='qualidade', nome='Analista de Qualidade', area='Testes SAP', especialidade='Cenários e evidências',
                          status_label='Ativo', trabalho_atual='Preparação de cenários')

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(persona='Analista de Qualidade SAP: cenários de teste e evidências ponta a ponta.',
                            instrucoes='Monte cenários e critérios de teste a partir dos entregáveis aprovados.',
                            skills=['Análise documental'])


PLUGIN = Plugin()
