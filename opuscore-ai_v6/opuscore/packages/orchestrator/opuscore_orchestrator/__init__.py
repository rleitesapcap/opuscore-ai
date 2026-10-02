"""Orquestrador: transforma os consultores num squad (eventos, handoffs, fluxos, gates).
Não tem regra de negócio de consultor, não acessa o SAP e não guarda arquivos."""
from .barramento import Orquestrador  # noqa: F401
