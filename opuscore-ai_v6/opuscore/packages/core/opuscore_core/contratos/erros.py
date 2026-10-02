"""Erros padronizados. A Plataforma converte em {"erro", "codigo", "request_id"}."""
from __future__ import annotations


class ErroOpus(Exception):
    def __init__(self, mensagem: str, codigo: str = "erro", status: int = 400):
        super().__init__(mensagem)
        self.mensagem, self.codigo, self.status = mensagem, codigo, status


def invalido(msg: str) -> ErroOpus:
    return ErroOpus(msg, "invalido", 400)


def nao_encontrado(msg: str) -> ErroOpus:
    return ErroOpus(msg, "nao_encontrado", 404)


def nao_processavel(msg: str) -> ErroOpus:
    return ErroOpus(msg, "nao_processavel", 422)


def falha_externa(msg: str) -> ErroOpus:
    return ErroOpus(msg, "falha_externa", 502)


def indisponivel(msg: str) -> ErroOpus:
    return ErroOpus(msg, "indisponivel", 503)
