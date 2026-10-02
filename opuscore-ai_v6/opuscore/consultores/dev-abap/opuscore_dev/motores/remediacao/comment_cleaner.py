# -*- coding: utf-8 -*-
"""
===============================================================================
 comment_cleaner.py  —  Limpeza de comentários-lixo do código ABAP (código morto, registros de alteração, marcações de transporte).
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Ele remove "comentários-lixo" do código ABAP antes da correção — como uma
    faxina que joga fora anotações velhas e código riscado, mas SEM tocar no
    código que funciona.

POR QUE ISSO É NECESSÁRIO:
    Programas ABAP antigos acumulam muito entulho ao longo dos anos: pedaços de
    código que foram "comentados" (desligados) em vez de apagados, registros de
    "quem alterou o quê e quando", marcações de transporte... Esse entulho
    atrapalha a leitura E faz a Inteligência Artificial gastar esforço à toa.
    Limpar antes deixa o trabalho da IA mais barato e mais focado.

O QUE ELE REMOVE (só o que é OBVIAMENTE lixo — na dúvida, MANTÉM):
    - Código morto comentado   (ex.:  *  SELECT * FROM ...  ,  *  x = y. )
    - Registros de alteração    (ex.:  " Inicio - Fulano - 14.02.2017 )
    - Marcações de transporte   (ex.:  *** <START> Request ... )

O QUE ELE SEMPRE PRESERVA:
    - O cabeçalho do arquivo (os comentários lá do topo)
    - Separadores e títulos de seção (linhas começando com *&)
    - Explicações escritas em português (texto que ajuda a entender o código)
    - O código que funciona (NUNCA é tocado)

COMO ELE DECIDE (a "regra de ouro"):
    Código ABAP não tem acentos. Então, se um comentário tem acento (á, ç, ã...),
    é quase certamente texto em português (uma explicação) — e é preservado.
    Se não tem acento e "parece código" (tem SELECT, um "=", um ponto final...), 
    é tratado como código morto e removido.

DETALHE IMPORTANTE:
    A remoção é SILENCIOSA — o arquivo limpo simplesmente não tem mais aquelas
    linhas, sem deixar nenhuma marca. Os arquivos ORIGINAIS ficam intactos; a
    faxina grava cópias limpas numa pasta separada.

    Este arquivo pode rodar sozinho (veja o final) OU ser chamado pela Etapa 1
    do run_pipeline.py.
===============================================================================
"""

from __future__ import annotations

import re                                   # "expressões regulares": busca de padrões em texto
from dataclasses import dataclass, field    # para criar a "ficha de estatísticas" (CleanStats)


# =============================================================================
# LISTAS E PADRÕES DE RECONHECIMENTO
# (São os "dicionários" que a faxina usa para reconhecer o que é código.)
# =============================================================================

# Palavras-chave da linguagem ABAP. Se um comentário COMEÇA com uma destas,
# é forte sinal de que ali tem código desligado (código morto).
_ABAP_KW = {
    "select", "endselect", "if", "elseif", "else", "endif", "move", "call",
    "perform", "loop", "endloop", "read", "modify", "update", "insert", "delete",
    "append", "clear", "refresh", "write", "concatenate", "condense", "split",
    "sort", "collect", "free", "check", "exit", "continue", "case", "when",
    "endcase", "do", "enddo", "while", "endwhile", "add", "subtract", "multiply",
    "divide", "compute", "set", "get", "import", "export", "commit", "rollback",
    "wait", "submit", "leave", "assign", "unassign", "create", "raise", "message",
    "form", "endform", "function", "endfunction", "module", "endmodule",
    # declarações (criação de variáveis, tipos, etc.)
    "data", "types", "constants", "statics", "ranges", "tables", "parameters",
    "field-symbols", "select-options", "class", "endclass", "method", "endmethod",
    "try", "catch", "endtry", "at", "new",
}

# Reconhece datas (ex.: 14.02.2017) — típicas de "registro de alteração".
_DATE_RE = re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b")
# Reconhece marcações do tipo "Inicio - ... " / "Fim - ..." (registros de alteração).
_CHANGELOG_RE = re.compile(r"\b(in[ií]cio|fim|begin|end)\b.*[-–]", re.IGNORECASE)

# A "REGRA DE OURO": se o texto tem acento, é português (explicação) => MANTÉM.
# (Identificadores ABAP nunca têm acento.)
_ACCENT_RE = re.compile(r"[áàâãäéèêëíìîïóòôõöúùûüçñ]", re.IGNORECASE)

# Palavras que "continuam" um comando ABAP (mesmo sem ser a 1ª palavra).
# Ajudam a pegar pedaços de código morto quebrados em várias linhas.
_CODE_CONT = {
    "into", "where", "for", "and", "or", "with", "type", "types", "value",
    "from", "using", "changing", "importing", "exporting", "tables", "ranges",
    "constants", "field-symbols", "statics", "when", "eq", "ne", "gt", "lt",
    "ge", "le", "structure",
}

# Fragmentos ABAP inconfundíveis (BEGIN OF/END OF, setas de parâmetro, macros...).
_EXTRA_FRAG_RE = re.compile(
    r"\b(begin|end)\s+of\b|-->|<--|<-|->|\bget_hard\b|\bbinary\s+search\b",
    re.IGNORECASE)


def _strip_inline_comment(body: str) -> str:
    """Separa o código do comentário que vem no fim da linha.

    Em ABAP, um comentário no meio da linha começa com aspas duplas ("). Esta
    função "corta" esse comentário para deixar só a parte de código. Isso é
    importante porque, às vezes, o código morto vinha com um comentário em
    português coladinho no fim — e o acento desse comentário enganava a faxina."""
    in_str = False                          # controla se estamos dentro de um texto '...'
    for i, ch in enumerate(body):
        if ch == "'":
            in_str = not in_str             # entrou/saiu de um texto entre aspas simples
        elif ch == '"' and not in_str:      # achou o " de comentário (fora de texto)
            return body[:i].rstrip()        # devolve só o que vem ANTES do comentário
    return body


@dataclass
class CleanStats:
    """Uma "ficha de resultado" da faxina: conta quantos comentários saíram e
    de que tipo. Serve só para mostrar o resumo no final."""
    removed: int = 0        # total removido
    dead_code: int = 0      # quantos eram código morto
    changelog: int = 0      # quantos eram registro de alteração
    loose_prose: int = 0    # quantos eram texto solto e curto
    samples: list[str] = field(default_factory=list)  # alguns exemplos do que saiu

    def __str__(self) -> str:
        # Como a ficha aparece quando impressa na tela.
        return (f"comments removed={self.removed} "
                f"(dead_code={self.dead_code}, changelog={self.changelog}, "
                f"loose_prose={self.loose_prose})")


def _comment_body(line: str):
    """Descobre se uma linha é um comentário inteiro e, se for, devolve o texto
    dele (sem os símbolos de comentário). Se NÃO for comentário, devolve None.

    Trata tanto o comentário ABAP de linha (começa com *) quanto o de aspas (")."""
    s = line.strip()
    if s.startswith("*"):
        return s.lstrip("*").strip()        # tira todos os * do começo
    if s.startswith('"'):
        return s.lstrip('"').strip()        # tira as aspas do começo
    return None                             # não é uma linha de comentário


# Linha feita SÓ de símbolos separadores (ex.: *****, *-----*) => é um separador, MANTÉM.
_SEP_ONLY_RE = re.compile(r"^[*\"][\s*\-=_+|.<>]*$")

# Marcações de transporte / request (ruído): <START>, <END>, "Request", "Transport".
_REQUEST_RE = re.compile(r"<\s*(start|end)\s*>|\brequest\b|\btransport\b", re.I)

# Fragmentos de código ABAP inconfundíveis (mesmo sem ponto final):
# SELECT *, INTO TABLE, FOR ALL ENTRIES, WITH KEY, READ TABLE, FROM <tabela>...
_ABAP_FRAG_RE = re.compile(
    r"select\s+(single\s+)?\*|into\s+(corresponding\s+fields\s+of\s+)?table|"
    r"for\s+all\s+entries|with\s+key|read\s+table|append\s+.*\bto\b|"
    r"modify\s+.*\bfrom\b|\bfrom\s+\w+|\bwhere\s+\w+", re.I)

# Palavras de continuação "fortes": quase só aparecem em código ABAP.
_CONT_STRONG = {"into", "where", "from", "using", "changing", "importing",
                "exporting", "endselect", "endloop", "endif", "enddo",
                "endwhile", "endcase", "endform", "endmethod", "endfunction",
                "endmodule", "elseif"}


def _looks_like_code(body: str) -> bool:
    """O "detetive" da faxina: decide se um comentário é código morto (True) ou
    não (False). É aqui que mora a inteligência da limpeza.

    A ordem das verificações importa — vai do sinal mais forte ao mais fraco."""
    if not body:
        return False
    # PASSO-CHAVE: analisa só a parte de código, jogando fora o comentário do fim.
    code = _strip_inline_comment(body)
    if not code:
        return False
    # REGRA DE OURO: se tem acento, é português (explicação) => NÃO é código morto.
    if _ACCENT_RE.search(code):
        return False

    low = code.lower()                              # versão em minúsculas (para comparar)
    stripped = code.rstrip()                        # sem espaços no fim
    first = re.split(r"[\s:(]", code, 1)[0].lower().rstrip(".,")  # a 1ª palavra

    # 0) Fragmentos inconfundíveis (SELECT *, INTO TABLE, BEGIN/END OF...).
    if _ABAP_FRAG_RE.search(low) or _EXTRA_FRAG_RE.search(code):
        return True
    # 1) Começa com palavra-chave ABAP ou palavra de continuação forte.
    if first in _ABAP_KW or first in _CONT_STRONG or first in _CODE_CONT:
        return True

    # Alguns "sinais" adicionais de que a linha é código:
    ends_stmt = stripped.endswith((".", ",")) or bool(re.search(r"\b(or|and)$", low))
    has_op = bool(re.search(r"=|->|\b(eq|ne|gt|lt|ge|le)\b", low))  # tem operador?
    has_field = bool(re.search(r"\w-\w", code))     # acesso a campo (tabela-campo)?
    has_type = bool(re.search(r"\btype\b", low))    # declaração com TYPE?
    has_strlit = "'" in code                        # tem texto entre aspas simples?

    # 2) Acesso a campo "tabela-campo" é marca registrada de ABAP.
    if has_field:
        return True
    # 3) Atribuição do tipo  nome = valor  (ou quebrada:  nome = ).
    if re.search(r"\w\s*=\s*\S", code) or stripped.endswith("="):
        return True
    # 4) Tem operador/TYPE e termina como um comando (com . ou ,).
    if (has_op or has_type) and ends_stmt:
        return True
    # 5) Chamada que termina em '.' com um texto ou várias palavras
    #    (ex.:  get_hard 'X' 'Y' gr_z.  ) — o português já foi excluído pelo acento.
    if stripped.endswith(".") and (has_strlit or len(code.split()) >= 3):
        return True
    return False                                    # não parece código => não remove


def _looks_like_changelog(body: str) -> bool:
    """Decide se o comentário é um "registro de alteração" ou marcação de
    transporte (tem data, ou "Inicio/Fim -", ou <START>/<END>/Request)."""
    return bool(_DATE_RE.search(body) or _CHANGELOG_RE.search(body)
                or _REQUEST_RE.search(body))


def _is_section_label(body: str) -> bool:
    """Decide se é um "título de seção" que deve ser MANTIDO mesmo em português:
    tem ':' (ex.: 'DECLARAÇÃO:') ou está quase todo em MAIÚSCULAS (um título)."""
    if ":" in body:
        return True
    letters = [c for c in body if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.7:
        return True
    return False


def _is_short_loose_prose(body: str) -> bool:
    """Decide se é um texto solto e curto em português (1 a 4 palavras) — o tipo
    de comentário que se quer remover (ex.: 'nÃO Alterar'), desde que não seja um
    título de seção."""
    words = [w for w in re.split(r"\s+", body) if w]
    return 1 <= len(words) <= 4


def strip_noise_comments(source: str, protect_header: bool = True) -> tuple[str, CleanStats]:
    """A FUNÇÃO PRINCIPAL DA FAXINA.

    Recebe o texto de um arquivo, percorre linha por linha, e devolve o texto
    limpo + a ficha de estatísticas. É conservadora: só remove o que é claramente
    lixo; na dúvida, mantém.
    """
    lines = source.splitlines(keepends=True)        # separa em linhas (guardando o \n)
    stats = CleanStats()                            # ficha zerada

    # Descobre onde termina o CABEÇALHO: é o bloco de comentários lá no topo, até
    # a primeira linha de código de verdade. Tudo isso é preservado.
    first_code = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith("*") or s.startswith('"'):
            continue                                # ainda é comentário/vazio => segue
        first_code = i                              # achou a 1ª linha de código
        break

    out: list[str] = []                             # onde montamos o arquivo limpo
    n = len(lines)
    for i, ln in enumerate(lines):                  # percorre cada linha...
        # Protege o cabeçalho: linhas antes do 1º código são sempre mantidas.
        if protect_header and i < first_code:
            out.append(ln)
            continue
        s = ln.strip()
        if s.startswith("*&"):                      # separador/título de FORM => mantém
            out.append(ln)
            continue

        body = _comment_body(ln)                    # é uma linha de comentário?
        if body is None:                            # NÃO é comentário => é código => mantém
            out.append(ln)
            continue

        # Linha só de símbolos (*****, *----*) => separador => mantém.
        if not body or _SEP_ONLY_RE.match(s):
            out.append(ln)
            continue

        # 1) É código morto? => remove (e anota na ficha).
        if _looks_like_code(body):
            stats.removed += 1
            stats.dead_code += 1
            if len(stats.samples) < 8:
                stats.samples.append(s[:70])
            continue
        # 2) É registro de alteração / transporte? => remove.
        if _looks_like_changelog(body):
            stats.removed += 1
            stats.changelog += 1
            if len(stats.samples) < 8:
                stats.samples.append(s[:70])
            continue
        # 3) É texto solto e curto em português? => remove, MAS preserva títulos
        #    de seção e rótulos que ficam logo abaixo de um separador.
        if _ACCENT_RE.search(body) and _is_short_loose_prose(body) \
                and not _is_section_label(body):
            prev_s = lines[i - 1].strip() if i > 0 else ""
            # Um título de bloco vem DEPOIS do separador de abertura (separador
            # acima), não antes do separador do próximo bloco.
            near_sep = bool(_SEP_ONLY_RE.match(prev_s)) or prev_s.startswith("*&")
            if not near_sep:
                stats.removed += 1
                stats.loose_prose += 1
                if len(stats.samples) < 8:
                    stats.samples.append(s[:70])
                continue

        out.append(ln)                              # não se encaixou em nada => mantém

    return "".join(out), stats                      # devolve o texto limpo + a ficha


# =============================================================================
# MODO "RODAR SOZINHO" (sem a IA, sem o resto da solução)
# -----------------------------------------------------------------------------
# Você pode usar só a faxina, direto pela linha de comando:
#
#   Lote (o padrão):   python comment_cleaner.py
#       Limpa todos os arquivos de ./remediation e grava em ./remediation_proc
#
#   Um arquivo só:     python comment_cleaner.py arquivo.txt [saida.txt]
# =============================================================================
import os
import glob

# Tipos de arquivo tratados no modo lote.
_SUPPORTED_EXT = ('*.txt', '*.abap', '*.prog', '*.reps', '*.clas', '*.intf',
                  '*.asddls', '*.ddls', '*.srvd', '*.bdef')


def _read_text(path: str) -> str:
    """Lê um arquivo tentando UTF-8 e, se falhar, o formato do Windows (cp1252)."""
    try:
        return open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        return open(path, encoding="cp1252", errors="replace").read()


def clean_file(inp: str, out: str) -> CleanStats:
    """Limpa UM arquivo (inp) e grava o resultado em (out)."""
    src = _read_text(inp)
    cleaned, stats = strip_noise_comments(src)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(cleaned)
    return stats


def clean_folder(in_dir: str = "remediation", out_dir: str = "remediation_proc") -> None:
    """Limpa TODOS os arquivos suportados de uma pasta, gravando em outra."""
    if not os.path.isdir(in_dir):
        print(f"✗ Pasta de entrada não encontrada: {in_dir}")
        raise SystemExit(1)

    files: list[str] = []
    for pat in _SUPPORTED_EXT:
        files.extend(sorted(glob.glob(os.path.join(in_dir, pat))))

    # Proteção: nunca processa arquivos .py nem o próprio script, mesmo que
    # alguém os coloque por engano dentro da pasta de entrada.
    _self = os.path.abspath(__file__)
    files = [f for f in files
             if not f.lower().endswith(".py")
             and os.path.abspath(f) != _self]

    if not files:
        print(f"✗ Nenhum arquivo suportado em {in_dir}")
        raise SystemExit(1)

    os.makedirs(out_dir, exist_ok=True)
    print(f"Limpeza de comentários — {len(files)} arquivo(s): {in_dir} -> {out_dir}")
    print("=" * 72)

    total_removed = 0
    for path in files:                              # para cada arquivo...
        base = os.path.basename(path)
        out = os.path.join(out_dir, base)
        stats = clean_file(path, out)               # ...limpa e grava
        total_removed += stats.removed
        print(f"  {base:<45} {stats}")

    print("=" * 72)
    print(f"✓ Concluído. {len(files)} arquivo(s), {total_removed} comentário(s) "
          f"removido(s). Saída: {out_dir}/")
    print("(nenhum código executável é tocado — só comentários-lixo)")


# Ponto de partida quando você roda: python comment_cleaner.py
if __name__ == "__main__":
    import sys

    # Sem argumentos -> modo lote (pasta remediation -> pasta remediation_proc).
    if len(sys.argv) == 1:
        clean_folder("remediation", "remediation_proc")
        raise SystemExit(0)

    # Com um argumento -> modo "um arquivo só".
    inp = sys.argv[1]
    if not os.path.isfile(inp):
        print(f"✗ Arquivo não encontrado: {inp}")
        raise SystemExit(1)
    ext = inp.rsplit(".", 1)[1] if "." in inp else "txt"
    out = sys.argv[2] if len(sys.argv) > 2 else (inp.rsplit(".", 1)[0] + "_limpo." + ext)
    stats = clean_file(inp, out)
    src_lines = len(_read_text(inp).splitlines())
    print(f"Arquivo:  {inp}")
    print(f"{stats}")
    if stats.samples:
        print("\nExemplos do que foi REMOVIDO:")
        for s in stats.samples:
            print(f"  - {s}")
    print(f"\nSalvo em: {out}")
    print("(nenhum código executável é tocado — só comentários-lixo)")