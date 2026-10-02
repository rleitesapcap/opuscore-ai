"""Referências a artefatos (nunca cópia de arquivos entre pacotes)."""
from __future__ import annotations

from pydantic import BaseModel


class ArquivoRef(BaseModel):
    nome: str
    tipo: str            # extensão sem ponto: docx, md, abap...
    tamanho: int
    url: str             # download pela Plataforma


class ArtefatoRef(BaseModel):
    id: str
    tipo: str = ""
    titulo: str = ""
