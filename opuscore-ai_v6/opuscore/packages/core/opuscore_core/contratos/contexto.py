"""O ctx: tudo que um consultor recebe da Plataforma. O consultor não importa a
Plataforma; recebe estas interfaces já prontas a cada requisição (ou evento)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


class ClienteMCP(Protocol):
    ferramentas: list[dict]

    async def chamar(self, ferramenta: str, **args: Any) -> Any:
        """Resposta JSON já decodificada. Erro da ferramenta vira ErroOpus."""

    async def chamar_texto(self, ferramenta: str, **args: Any) -> str: ...


class Artefatos(Protocol):
    def criar(self, *, projeto_id: str, tipo: str, titulo: str, conteudo: str = "",
              formato: str = "markdown", arquivos: Sequence[Path] = (),
              meta: dict | None = None) -> str: ...

    def obter(self, artefato_id: str) -> dict: ...

    def arquivos(self, artefato_id: str) -> list[dict]: ...

    def ler_arquivo(self, artefato_id: str, nome: str) -> bytes: ...

    def listar(self, projeto_id: str, tipo: str | None = None,
               produzido_por: str | None = None) -> list[dict]: ...


class Uploads(Protocol):
    def carregar(self, upload_id: str) -> tuple[Path, dict, str]:
        """(arquivo original, metadados, texto extraído)."""


class Eventos(Protocol):
    async def publicar(self, tipo: str, *, projeto_id: str, gap_id: str, payload: dict,
                       artefatos: Sequence[str] = (), versao: int = 1,
                       causa_id: str | None = None) -> str: ...


class Auditoria(Protocol):
    def registrar(self, acao: str, /, **campos: Any) -> None: ...


class Contexto(Protocol):
    plugin_key: str
    request_id: str
    mcp: ClienteMCP
    artefatos: Artefatos
    uploads: Uploads
    eventos: Eventos
    auditoria: Auditoria
    config: Mapping[str, str]
    usuario: str

    def ia(self, nome: str | None = None) -> Any:
        """Provedor de IA (chat/tools) do SDK, já configurado."""
