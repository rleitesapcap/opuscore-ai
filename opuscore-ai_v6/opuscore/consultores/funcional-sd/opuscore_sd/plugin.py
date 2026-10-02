"""Plugin do Consultor Funcional SD. Hoje atua pelo chat comum (Conversar). Para dar tela e rotas
próprias: implemente rotas(obter_ctx), web_dir e declare web=WebManifesto(...)."""
from __future__ import annotations

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase


class Plugin(PluginBase):
    manifesto = Manifesto(key='funcional-sd', nome='Consultor Funcional SD', area='Processos SAP', especialidade='Vendas e distribuição',
                          status_label='Ativo', trabalho_atual='EF preliminar aguarda arquitetura')

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(persona='Consultor Funcional SAP SD sênior (vendas, pricing, remessa, faturamento).',
                            instrucoes='Analise processos e requisitos de SD com base em documentos. Declare quando não puder verificar o sistema.',
                            skills=['Análise documental'])


PLUGIN = Plugin()
