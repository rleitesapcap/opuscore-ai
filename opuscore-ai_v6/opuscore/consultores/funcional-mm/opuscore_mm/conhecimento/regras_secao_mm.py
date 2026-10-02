"""Ajustes de MM às regras padrão do pacote EF (camada 2 de 3: padrão < MM < projeto).
Versionados com o código: mude aqui o que vale para TODO projeto de MM."""
from __future__ import annotations

AJUSTES_MM: dict[str, dict] = {
    "processos": {"prompt": (
        "Liste o que falta para cada processo: transação S/4HANA, app Fiori (quando houver), papel do usuário e se "
        "é standard ou custom. Em MM, se a regra vale na criação do pedido (ME21N), confira se a EF diz o que acontece "
        "na modificação (ME22N) e em outros caminhos que gravam o mesmo documento. Aponte transações que não existem "
        "mais no S/4HANA sem afirmar nada que não esteja no texto.")},
    "parametros": {"prompt": (
        "A seção precisa listar os parâmetros reais (nome, tipo: TVARV/BRF+/tabela/app, valores e quem mantém). Em MM, "
        "parâmetros por centro, organização de compras ou grupo de mercadorias precisam dizer a chave usada. Se a EF "
        "citar tabelas de parâmetro em outras seções, aponte que elas deveriam estar aqui.")},
}
