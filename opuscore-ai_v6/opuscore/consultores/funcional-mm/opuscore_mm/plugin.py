"""Plugin do Consultor Funcional MM."""
from __future__ import annotations

from pathlib import Path

from opuscore_core.contratos.plugin import Manifesto, PerfilAgente, PluginBase, WebManifesto


class FuncionalMMPlugin(PluginBase):
    manifesto = Manifesto(key="funcional-mm", nome="Consultor Funcional MM", area="Funcional",
                          especialidade="Materiais e compras", trabalho_atual="Gerar e validar EF",
                          web=WebManifesto(rota="mm", css="mm.css"))

    def perfil(self) -> PerfilAgente:
        return PerfilAgente(
            persona="Consultor funcional SAP MM sênior: analisa a configuração de MM, gera o rascunho da EF a partir "
                    "do Workshop B e valida EFs seção por seção.",
            instrucoes="Ajude a escrever e revisar EFs claras, testáveis e aderentes ao Clean Core. Para perguntas sobre "
                       "a configuração do ambiente, use a ferramenta sap_config_table. Nunca invente objetos, transações "
                       "ou números de SAP Note.",
            skills=["Análise de configuração de MM", "Geração de EF a partir do Workshop B", "Validação de EF por seção"])

    def rotas(self, obter_ctx):
        from .rotas.mm import criar_router
        return criar_router(obter_ctx)

    @property
    def web_dir(self) -> Path:
        return Path(__file__).parent / "web"


PLUGIN = FuncionalMMPlugin()
