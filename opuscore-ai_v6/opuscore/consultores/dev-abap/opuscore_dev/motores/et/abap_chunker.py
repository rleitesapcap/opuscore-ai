# -*- coding: utf-8 -*-
"""
===============================================================================
 abap_chunker.py  —  O CORTADOR DE CÓDIGO EM PEDAÇOS
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Ele divide um programa ABAP grande em pedaços menores e lógicos, para que a
    Inteligência Artificial analise um pedaço de cada vez.

POR QUE ISSO É NECESSÁRIO:
    A IA tem um limite de quanto texto consegue ler de uma vez (como uma pessoa
    que não lê um livro inteiro numa sentada). Um programa ABAP pode ter milhares
    de linhas. Então, em vez de mandar tudo de uma vez, cortamos o programa em
    "unidades" (as sub-rotinas: FORM, METHOD, FUNCTION, MODULE) e mandamos uma
    por vez.

A REGRA DE OURO DO CORTE (muito importante):
    O corte NUNCA pode partir uma linha ou um comando no meio. E, se você juntar
    todos os pedaços de volta, tem que dar EXATAMENTE o programa original, sem
    perder nem um caractere. O motor sempre confere isso (função verify_roundtrip)
    antes de confiar no corte; se falhar, ele desiste de cortar e manda o arquivo
    inteiro.

DOIS TIPOS DE PEDAÇO:
    - "unit" (unidade): uma sub-rotina completa (do FORM ao ENDFORM, por exemplo).
    - "seam" (costura): tudo o que fica ENTRE as unidades — declarações globais,
      cabeçalhos, linhas em branco, INCLUDEs, etc. É preservado como está.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass 
from typing import Optional


# As palavras que ABREM uma unidade (uma sub-rotina).
_UNIT_OPEN = {"FORM", "METHOD", "FUNCTION", "MODULE"}
# As palavras que FECHAM uma unidade.
_UNIT_CLOSE = {"ENDFORM", "ENDMETHOD", "ENDFUNCTION", "ENDMODULE"}
# Qual "fecha" corresponde a qual "abre" (ex.: FORM fecha com ENDFORM).
_CLOSE_OF = {
    "FORM": "ENDFORM", "METHOD": "ENDMETHOD",
    "FUNCTION": "ENDFUNCTION", "MODULE": "ENDMODULE",
}


@dataclass
class Segment:
    """Um "pedaço" do programa. Guarda o texto exato e o que ele é."""
    kind: str                         # "unit" (unidade) ou "seam" (costura)
    text: str                         # o texto exato deste pedaço
    unit_type: Optional[str] = None   # FORM | METHOD | FUNCTION | MODULE (se for unidade)
    name: Optional[str] = None        # o nome da unidade (quando dá para descobrir)
    has_code: bool = True             # False => só comentários/linhas em branco


def _first_token(line: str) -> Optional[str]:
    """Devolve a PRIMEIRA palavra de código de uma linha (em MAIÚSCULAS), ou None
    se a linha for vazia ou um comentário (em ABAP, comentário começa com *)."""
    s = line.strip()
    if not s or s.startswith("*"):
        return None
    tok = s.split(None, 1)[0]         # pega o primeiro "pedaço" antes de um espaço
    tok = tok.rstrip(".:,")           # tira pontuação do fim
    return tok.upper()


def _unit_name(line: str) -> Optional[str]:
    """Descobre o nome da unidade: é a palavra logo depois de FORM/METHOD/etc.
    Ex.: em 'FORM f_calcula.' o nome é 'f_calcula'."""
    parts = line.strip().split(None, 2)
    if len(parts) >= 2:
        return parts[1].rstrip(".:,")
    return None


def _has_real_code(text: str) -> bool:
    """Confere se um trecho tem pelo menos uma linha de código de verdade
    (não só comentários e linhas em branco)."""
    for line in text.splitlines():
        t = _first_token(line)
        if t is not None:
            return True
    return False


def split_abap_units(source: str) -> list[Segment]:
    """CORTE PRINCIPAL: divide o programa em pedaços (unidades e costuras).

    Percorre linha por linha com uma "máquina de estados" simples: quando acha
    um FORM/METHOD/etc., junta tudo até o END correspondente num pedaço "unit";
    o resto vira pedaços "seam". Garante que a soma dos pedaços é o original."""
    lines = source.splitlines(keepends=True)
    segments: list[Segment] = []

    buf: list[str] = []               # "buffer": acumula as linhas de corte
    i = 0
    n = len(lines)

    def flush_seam():
        """Fecha o pedaço de corte acumulado até agora e o guarda."""
        if buf:
            text = "".join(buf)
            segments.append(Segment(kind="seam", text=text,
                                    has_code=_has_real_code(text)))
            buf.clear()

    while i < n:
        line = lines[i]
        tok = _first_token(line)

        if tok in _UNIT_OPEN:                       # começou uma sub-rotina...
            flush_seam()                            # ...primeiro fecha o corte pendente
            open_type = tok
            close_tok = _CLOSE_OF[open_type]        # qual END vamos procurar
            name = _unit_name(line)
            unit_lines = [line]
            i += 1
            closed = False
            while i < n:                            # junta linhas até achar o END
                l2 = lines[i]
                t2 = _first_token(l2)
                unit_lines.append(l2)
                i += 1
                if t2 == close_tok:                 # achou o END => unidade completa
                    closed = True
                    break
                # Defesa: se abrir uma nova unidade sem ter fechado a anterior,
                # a anterior não fechou direito. Paramos aqui para não "engolir"
                # a próxima, e deixamos o laço de fora lidar com ela.
                if t2 in _UNIT_OPEN:
                    i -= 1
                    unit_lines.pop()
                    break
            text = "".join(unit_lines)
            segments.append(Segment(
                kind="unit", text=text, unit_type=open_type, name=name,
                has_code=True,
            ))
            if not closed:
                # Unidade sem fecho: seguimos mesmo assim; nada foi perdido (a
                # soma dos pedaços continua igual ao original), só a qualidade do
                # corte pode ser menor.
                pass
        else:
            buf.append(line)                        # linha comum => vai para a costura
            i += 1

    flush_seam()                                    # fecha a última costura, o último pedaço
    return segments


def extract_global_context(source: str, max_lines: int = 120) -> str:
    """Pega o "contexto global" do programa: o preâmbulo (REPORT, TABLES, DATA
    globais, definição de CLASS...) até a primeira sub-rotina.

    Serve para dar à IA as declarações que uma unidade usa, SEM pedir que ela
    corrija esse preâmbulo de novo. Tem um limite de linhas para não ocupar
    espaço demais no pedido à IA."""
    lines = source.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        if _first_token(line) in _UNIT_OPEN:        # chegou na 1ª unidade => para
            break
        out.append(line)
        if len(out) >= max_lines:                   # atingiu o limite => para
            break
    return "".join(out)


def verify_roundtrip(source: str, segments: list[Segment]) -> bool:
    """A CONFERÊNCIA DE SEGURANÇA: junta todos os pedaços e verifica se dá
    EXATAMENTE o programa original. Se der False, o motor não confia no corte."""
    return "".join(s.text for s in segments) == source


# =============================================================================
# CORTE ADICIONAL para pedaços muito grandes que NÃO têm sub-rotinas
# (ex.: INCLUDEs com código solto). Divide por tamanho, mas sempre no fim de um
# comando (linha terminada em '.'), para não partir um comando no meio.
# =============================================================================
def _is_statement_end(line: str) -> bool:
    """Diz se a linha termina um comando ABAP (termina com '.', e não é comentário)."""
    s = line.rstrip()
    if not s:
        return False
    if s.lstrip().startswith("*"):
        return False
    return s.endswith(".")


def split_large_segment(text: str, max_chars: int) -> list[str]:
    """Divide um texto grande em pedaços de ~max_chars, sempre quebrando no fim
    de um comando (nunca no meio)."""
    lines = text.splitlines(keepends=True)
    pieces: list[str] = []
    buf: list[str] = []
    size = 0
    for line in lines:
        buf.append(line)
        size += len(line)
        # Só quebra quando já passou do tamanho E a linha fecha um comando.
        if size >= max_chars and _is_statement_end(line):
            pieces.append("".join(buf))
            buf, size = [], 0
    if buf:
        pieces.append("".join(buf))
    return pieces or [text]


def chunk_for_analysis(source: str, max_chars: int = 6000) -> list[Segment]:
    """CORTE FINAL usado pela análise. É o split_abap_units, mas com um extra:
    qualquer pedaço de código maior que max_chars (ex.: um INCLUDE sem
    sub-rotinas, ou um FORM gigante) é dividido de novo, por tamanho, no fim de
    comandos. Assim, nenhuma chamada à IA recebe um bloco grande demais."""
    base = split_abap_units(source)
    out: list[Segment] = []
    for seg in base:
        # Pedaço pequeno ou sem código => fica como está.
        if not seg.has_code or len(seg.text) <= max_chars:
            out.append(seg)
            continue
        # Pedaço grande => corta em sub-pedaços numerados (block#0, block#1...).
        for i, piece in enumerate(split_large_segment(seg.text, max_chars)):
            out.append(Segment(
                kind=seg.kind,
                text=piece,
                unit_type=seg.unit_type,
                name=(f"{seg.name}#{i}" if seg.name else f"block#{i}"),
                has_code=_has_real_code(piece),
            ))
    return out


def summarize(segments: list[Segment]) -> str:
    """Monta um resuminho: quantos pedaços, quantas unidades, quantas costuras.
    Só para exibir na tela / no log."""
    units = [s for s in segments if s.kind == "unit"]
    seams = [s for s in segments if s.kind == "seam"]
    code_seams = [s for s in seams if s.has_code]
    return (f"{len(segments)} segments: {len(units)} units, "
            f"{len(seams)} seams ({len(code_seams)} with code)")