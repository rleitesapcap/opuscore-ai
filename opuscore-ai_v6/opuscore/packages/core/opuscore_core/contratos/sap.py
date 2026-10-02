"""Tipos SAP comuns a vários pacotes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ObjectRef:
    name: str
    type: str = ""          # ex.: TABL/DT, PROG/P, CLAS/OC, DDLS/DF
    uri: str = ""           # caminho ADT, ex.: /sap/bc/adt/ddic/tables/ZFOO
    package: str = ""
    description: str = ""
