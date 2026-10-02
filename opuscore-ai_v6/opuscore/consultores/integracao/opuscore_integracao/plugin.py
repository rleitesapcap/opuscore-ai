"""Plugin do Arquiteto de Integração. Hoje atua pelo chat comum (Conversar). Para dar tela e rotas
próprias: implemente rotas(obter_ctx), web_dir e declare web=WebManifesto(...)."""
from __future__ import annotations

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase


class Plugin(PluginBase):
    manifesto = Manifesto(key='integracao', nome='Arquiteto de Integração', area='Integração SAP', especialidade='Interfaces e SAP CI',
                          status_label='Ativo', trabalho_atual='Mapeamento de interfaces')

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(persona='Arquiteto de Integração SAP (Integration Suite/CI, eventos, IDoc, APIs).',
                            instrucoes='Mapeie interfaces, padrões e impactos de integração a partir de documentos.',
                            skills=['Análise documental'])


PLUGIN = Plugin()
