# -*- coding: utf-8 -*-
"""
===============================================================================
 run_pipeline.py  —  Programa inicial, onde executa a limpeza do código e a remediação com IA.
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Ele executa a solução inteira em UM comando só, coordenando as duas etapas
    na ordem certa — primeiro a limpeza de código, depois a remediação.

AS DUAS ETAPAS:
    ETAPA 1 — Limpeza  (usa o comment_cleaner.py)
        Lê os arquivos da pasta  input/  e remove os "comentários-lixo"
        (código velho comentado, anotações antigas), gravando as cópias limpas
        em  input_proc/. Os arquivos ORIGINAIS nunca são alterados.

    ETAPA 2 — Remediação  (usa o lc_CapRemediation.py)
        Pega os arquivos já limpos em  input_proc/, envia para a
        Inteligência Artificial analisar e corrigir, e grava o resultado final
        em  output/.

COMO USAR:
    Abra o terminal na pasta do projeto e digite:
        python run_pipeline.py

O QUE PRECISA ESTAR NA MESMA PASTA:
    run_pipeline.py          <- este arquivo
    comment_cleaner.py       <- a "máquina de faxina"
    lc_CapRemediation.py     <- a "máquina de correção" (usa a IA)
    .env                     <- as senhas de acesso à IA (LLM_API_KEY, WORKSPACE_ID)
    input/                   <- AQUI você coloca os arquivos a corrigir (entrada)
    input_proc/              <- criada automaticamente (arquivos limpos)
    output/                  <- criada automaticamente (resultado final)
===============================================================================
"""

from __future__ import annotations

import os          # para mexer com pastas e arquivos
import sys         # para encerrar o programa e achar o Python atual
import glob        # para listar arquivos por "padrão" (ex.: todos os *.abap)
import subprocess  # para executar o outro script (a etapa 2) como um programa

# Importamos a função de limpeza que vive no arquivo comment_cleaner.py.
from comment_cleaner import strip_noise_comments

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO — os nomes das pastas e do script de remediação.
# (São as "gavetas" que o programa usa. Mude aqui se quiser outros nomes.)
# ---------------------------------------------------------------------------
INPUT_DIR = "input"              # pasta de ENTRADA (seus arquivos originais)
CLEAN_DIR = "input_proc"         # pasta dos arquivos já LIMPOS
OUTPUT_DIR = "output"              # pasta do resultado FINAL
REMEDIATION_SCRIPT = "lc_CapRemediation.py"  # o script da etapa 2

# Tipos de arquivo que a ferramenta reconhece como "código ABAP".
_SUPPORTED_EXT = ("*.txt", "*.abap", "*.prog", "*.reps", "*.clas", "*.intf",
                  "*.asddls", "*.ddls", "*.srvd", "*.bdef")


def _list_sources(folder: str) -> list[str]:
    """Lista todos os arquivos de código dentro de uma pasta.

    Também tem uma proteção: nunca inclui arquivos .py (para não processar o
    próprio programa por engano)."""
    files: list[str] = []
    for pat in _SUPPORTED_EXT:                       # para cada tipo de arquivo...
        files.extend(sorted(glob.glob(os.path.join(folder, pat))))  # ...pega todos os arquivos
    _self = os.path.abspath(__file__)                # o caminho deste próprio arquivo
    return [f for f in files
            if not f.lower().endswith(".py") and os.path.abspath(f) != _self]


def _read(path: str) -> str:
    """Lê o conteúdo de um arquivo de texto.
    Tenta primeiro no formato moderno (UTF-8); se falhar (arquivos ABAP antigos
    às vezes vêm em outro formato), tenta o formato do Windows (cp1252)."""
    try:
        return open(path, encoding="utf-8").read()
    except UnicodeDecodeError:
        return open(path, encoding="cp1252", errors="replace").read()


def step_clean() -> int:
    """ETAPA 1 — LIMPEZA DE COMENTÁRIOS INÚTEIS E CÓDIGO MORTO.

    Percorre cada arquivo da pasta de entrada, remove os comentários-lixo e grava
    a versão limpa na pasta input_proc/. Devolve quantos comentários foram
    removidos no total (só para exibir no resumo)."""
    # Se a pasta de entrada não existe, avisa e para o processo.
    if not os.path.isdir(INPUT_DIR):
        print(f"✗ Pasta de entrada não encontrada: {INPUT_DIR}/")
        sys.exit(1)
    files = _list_sources(INPUT_DIR)
    if not files:                                    # pasta existe mas está vazia
        print(f"✗ Nenhum arquivo suportado em {INPUT_DIR}/")
        sys.exit(1)

    # Cria a pasta de saída da limpeza (se já existir, tudo bem).
    os.makedirs(CLEAN_DIR, exist_ok=True)
    print("=" * 70)
    print(f"ETAPA 1/2 — Limpeza de comentários  ({len(files)} arquivo(s))")
    print(f"           {INPUT_DIR}/  ->  {CLEAN_DIR}/")
    print("=" * 70)

    total = 0
    for path in files:                               # para cada arquivo de entrada...
        base = os.path.basename(path)                # só o nome (sem o caminho)
        cleaned, stats = strip_noise_comments(_read(path))  # <- a faxina acontece aqui
        # Grava a versão limpa na pasta input_proc/, com o MESMO nome.
        with open(os.path.join(CLEAN_DIR, base), "w", encoding="utf-8") as f:
            f.write(cleaned)
        total += stats.removed                       # soma quantos comentários saíram
        print(f"  {base:<45} {stats}")               # mostra o resultado por arquivo
    print("-" * 70)
    print(f"  Originais preservados em {INPUT_DIR}/ · {total} comentário(s) removido(s)")
    return total


def step_remediate() -> int:
    """ETAPA 2 — A CORREÇÃO (com Inteligência Artificial).

    Executa o script de remediação (lc_CapRemediation.py) apontando-o para a
    pasta de arquivos já limpos. Devolve o "código de retorno" (0 = deu tudo
    certo; diferente de 0 = houve algum problema)."""
    print("\n" + "=" * 70)
    print(f"ETAPA 2/2 — Remediação  ({REMEDIATION_SCRIPT})")
    print(f"           {CLEAN_DIR}/  ->  {OUTPUT_DIR}/")
    print("=" * 70)

    # Confere se o script da etapa 2 está mesmo na pasta (senão, não há o que rodar).
    if not os.path.isfile(REMEDIATION_SCRIPT):
        print(f"✗ Script de remediação não encontrado: {REMEDIATION_SCRIPT}")
        sys.exit(1)

    # Aqui está o truque que liga as duas etapas: preparamos as "variáveis de
    # ambiente" (uma espécie de recado) dizendo ao script de remediação para LER
    # da pasta de arquivos limpos (remediation_proc/) em vez da pasta original.
    # Copiamos o ambiente atual e só acrescentamos essas duas informações — não
    # mexemos nas senhas do arquivo .env.
    env = os.environ.copy()
    env["REMEDIATION_INPUT_DIR"] = CLEAN_DIR
    env.setdefault("REMEDIATION_OUTPUT_DIR", OUTPUT_DIR)

    # Executa o script de remediação como um programa separado, passando o recado.
    proc = subprocess.run([sys.executable, REMEDIATION_SCRIPT], env=env)
    return proc.returncode


def main() -> None:
    """A FUNÇÃO PRINCIPAL — o roteiro que o programa segue do início ao fim."""
    print("PIPELINE: limpeza -> remediação (uma única chamada)\n")
    step_clean()                     # 1º: faz a limpeza de comentários inúteis e código morto
    rc = step_remediate()            # 2º: faz a correção com IA
    # Mostra o resumo final, dizendo se deu tudo certo ou se houve problema.
    print("\n" + "=" * 70)
    if rc == 0:
        print(f"✓ Pipeline concluído. Saída em: {OUTPUT_DIR}/")
    else:
        print(f"⚠ A remediação terminou com código {rc}. Veja as mensagens acima.")
    print(f"  Originais intactos em {INPUT_DIR}/ · limpos em {CLEAN_DIR}/")
    print("=" * 70)
    sys.exit(rc)                     # encerra devolvendo o código de sucesso/erro


# Esta linha é o "ponto de partida": quando você digita `python run_pipeline.py`,
# o Python executa a função main() logo abaixo. 
if __name__ == "__main__":
    main()