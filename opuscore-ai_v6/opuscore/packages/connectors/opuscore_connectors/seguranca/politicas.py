"""Políticas de leitura de DADOS (nível 'leitura_dados')."""
from __future__ import annotations

# C/G = customizing, E = controle/cliente, S/W = sistema (dados de controle SAP).
# A (aplicação: cadastros e transações) e L (temporária) ficam bloqueadas.
CLASSES_CONFIG = {"C", "G", "E", "S", "W"}
MAX_LINHAS_CONFIG = 500


def pode_ler_config(tabela: str, classe_entrega: str, tabelas_sem_classe: list[str]) -> tuple[bool, str]:
    t = tabela.upper()
    if classe_entrega and classe_entrega not in CLASSES_CONFIG:
        return False, (f"A tabela {t} tem classe de entrega {classe_entrega} (dados de aplicação). "
                       "Por segurança, só tabelas de configuração são lidas.")
    if not classe_entrega and t not in {x.upper() for x in tabelas_sem_classe}:
        return False, (f"Não consegui confirmar a classe de entrega de {t} neste release, e ela não está "
                       "na lista de tabelas de configuração permitidas (conectores.tabelas_config_sem_classe).")
    return True, ""
