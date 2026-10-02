"""Versões do pacote e de cada contrato.

O pacote segue versionamento semântico. Cada contrato tem um número inteiro próprio:
mudança compatível (campo opcional novo) mantém o número; mudança incompatível cria
uma versão nova do contrato, e as duas convivem durante o período de transição.
"""
__version__ = "1.0.0"

CONTRATO_PLUGIN = 1          # Plugin / Manifesto / PerfilAgente
CONTRATO_WEB = 1             # o ctx entregue às telas dos consultores
CONTRATOS_SUPORTADOS = {"plugin": {1}, "web": {1}}
