"""Plugin do Arquiteto de Soluções. Hoje atua pelo chat comum (Conversar). Para dar tela e rotas
próprias: implemente rotas(obter_ctx), web_dir e declare web=WebManifesto(...)."""
from __future__ import annotations

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase


class Plugin(PluginBase):
    manifesto = Manifesto(key='arquiteto', nome='Arquiteto de Soluções', area='Arquitetura SAP', especialidade='Solução e Clean Core',
                          status_label='Em análise', trabalho_atual='Relatório de Arquitetura')

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(persona='Arquiteto de Soluções SAP sênior, rigoroso e evidence-based.',
                            instrucoes='Produza AS-IS, TO-BE, riscos, lacunas e recomendações a partir de evidência. Avalie Clean Core.',
                            skills=['Análise de Objeto', 'Clean Core Check'])


PLUGIN = Plugin()
