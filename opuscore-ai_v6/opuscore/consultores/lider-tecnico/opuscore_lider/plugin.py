"""Plugin do Líder Técnico. Hoje atua pelo chat comum (Conversar). Para dar tela e rotas
próprias: implemente rotas(obter_ctx), web_dir e declare web=WebManifesto(...)."""
from __future__ import annotations

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase


class Plugin(PluginBase):
    manifesto = Manifesto(key='lider-tecnico', nome='Líder Técnico', area='Revisão técnica', especialidade='Viabilidade e padrões',
                          status_label='Ativo', trabalho_atual='Revisão da EF')

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(persona='Líder Técnico SAP: revisa viabilidade técnica e aderência a padrões.',
                            instrucoes='Revise completude e consistência dos entregáveis; registre parecer e pendências.',
                            skills=['Análise documental'])


PLUGIN = Plugin()
