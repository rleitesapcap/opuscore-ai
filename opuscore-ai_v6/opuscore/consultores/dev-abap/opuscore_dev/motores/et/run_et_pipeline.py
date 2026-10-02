# -*- coding: utf-8 -*-
"""
===============================================================================
 run_et_pipeline.py  —  O PIPELINE DA ET (roda as 3 etapas de uma vez)
===============================================================================

O QUE ESTE ARQUIVO FAZ:
    Executa, em sequência e de uma única vez, as três etapas que produzem a
    Especificação Técnica (ET):

        Etapa 1:  extract.py            (extração mecânica da EF + códigos)
        Etapa 2:  generate_docs.py      (análise dos códigos -> *_DOC.md, LLM)
        Etapa 3:  lc_CapETGenerator.py  (monta a ET .docx a partir dos artefatos)

REGRA DE OURO — FAIL-FAST:
    A PRÓXIMA ETAPA SÓ RODA SE A ATUAL NÃO DER ERRO. "Erro" = a etapa terminou
    com código de saída != 0 (as três etapas usam sys.exit em falhas), ou o
    artefato-chave esperado não foi produzido. Ao primeiro erro, o pipeline PARA
    e reporta em qual etapa parou — nada da etapa seguinte é executado.

COMO DETECTA ERRO (dois sinais):
    1) código de saída do processo (0 = ok);
    2) verificação do artefato-chave (ex.: _payload.json após a Etapa 1).

CADA ETAPA RODA COMO SUBPROCESSO:
    Mesmo interpretador (sys.executable), na pasta do projeto, com a saída
    (logs) transmitida ao vivo. Isso isola o estado entre etapas e é igual a
    rodar cada script na mão — só que encadeado e com o portão de erro.

COMO USAR:
    python run_et_pipeline.py                 # roda as 3 etapas (completo, com IA)
    python run_et_pipeline.py --dry-run       # sem IA/credencial nas etapas 2 e 3
    python run_et_pipeline.py --only ZRMM0003 # filtra objetos na Etapa 2
    python run_et_pipeline.py --llm-review     # Etapa 3 refina o Objetivo pela IA
    python run_et_pipeline.py --date 19082026  # data fixa na Etapa 1

    Repasse de argumentos "crus" por etapa (o que não estiver mapeado acima):
    python run_et_pipeline.py --extract-args "--src-chars 12000" \
                              --docs-args "--force" \
                              --et-args "--output output/01_ET_GERADA"
===============================================================================
"""

from __future__ import annotations

import argparse
import glob
import logging
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except Exception:
    pass


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("et_pipeline")


# ------------------------------------------------------------------------------
# Localização de pastas (mesmos padrões/overrides das demais ferramentas)
# ------------------------------------------------------------------------------
_DIR_DEFAULTS = {
    "ET_OUTBOUND_DIR": "output",
    "DIR_ET_GERADA": "01_ET_GERADA",
    "DIR_ARTEFATOS": "artefatos",
}


def project_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def _dir_name(key: str) -> str:
    v = os.environ.get(key)
    return str(v).strip() if v and str(v).strip() else _DIR_DEFAULTS[key]


def artefatos_dir() -> str:
    return os.path.join(project_dir(), _dir_name("ET_OUTBOUND_DIR"),
                        _dir_name("DIR_ET_GERADA"), _dir_name("DIR_ARTEFATOS"))


def et_gerada_dir() -> str:
    return os.path.join(project_dir(), _dir_name("ET_OUTBOUND_DIR"),
                        _dir_name("DIR_ET_GERADA"))


# ------------------------------------------------------------------------------
# Definição de uma etapa
# ------------------------------------------------------------------------------
@dataclass
class Stage:
    key: str                                   # id curto (extract/docs/et)
    number: int                                # 1, 2, 3
    title: str                                 # rótulo humano
    script: str                                # arquivo .py ao lado deste
    build_args: Callable[[argparse.Namespace], list]   # monta os args da etapa
    verify: Optional[Callable[[], Optional[str]]] = None  # devolve msg de erro ou None


def _verify_payload() -> Optional[str]:
    p = os.path.join(artefatos_dir(), "_payload.json")
    if not os.path.isfile(p):
        return f"_payload.json não encontrado em {artefatos_dir()} (Etapa 1 não produziu artefatos)."
    return None


def _verify_docs() -> Optional[str]:
    docs = glob.glob(os.path.join(artefatos_dir(), "*_DOC.md"))
    if not docs:
        return f"nenhum *_DOC.md em {artefatos_dir()} (Etapa 2 não gerou documentação)."
    return None


def _verify_et() -> Optional[str]:
    produced = glob.glob(os.path.join(et_gerada_dir(), "ET_*.docx")) + \
        glob.glob(os.path.join(et_gerada_dir(), "ET_*.md"))
    if not produced:
        return f"nenhuma ET (ET_*.docx/.md) em {et_gerada_dir()} (Etapa 3 não gerou a ET)."
    return None


# --- montadores de argumentos por etapa (só mapeiam flags que a etapa aceita) --
def _args_extract(a: argparse.Namespace) -> list:
    out: list = []
    if a.root:
        out += ["--root", a.root]
    if a.date:
        out += ["--date", a.date]
    out += a._extract_extra
    return out


def _args_docs(a: argparse.Namespace) -> list:
    out: list = []
    if a.root:
        out += ["--root", a.root]
    if a.only:
        out += ["--only", a.only]
    if a.dry_run:
        out += ["--dry-run"]          # Etapa 2 aceita --dry-run (não chama a IA)
    if a.force:
        out += ["--force"]
    if a.providers_path:
        out += ["--providers-path", a.providers_path]
    if a.chunker_path:
        out += ["--chunker-path", a.chunker_path]
    out += a._docs_extra
    return out


def _args_et(a: argparse.Namespace) -> list:
    out: list = []
    if a.dry_run:
        out += ["--dry-run"]          # Etapa 3 aceita --dry-run (extração determinística)
    if a.llm_review:
        out += ["--llm-review"]
    if a.output:
        out += ["--output", a.output]
    if a.no_md:
        out += ["--no-md"]
    out += a._et_extra
    return out


STAGES = [
    Stage("extract", 1, "Extração mecânica (EF + códigos)", "extract.py",
          _args_extract, _verify_payload),
    Stage("docs", 2, "Análise de código -> *_DOC.md", "generate_docs.py",
          _args_docs, None),           # --dry-run legítimo não grava DOC: sem verify rígido
    Stage("et", 3, "Geração da ET (.docx)", "lc_CapETGenerator.py",
          _args_et, _verify_et),
]


# ------------------------------------------------------------------------------
# Execução de uma etapa (subprocesso, saída ao vivo, cronometrada)
# ------------------------------------------------------------------------------
@dataclass
class StageResult:
    stage: Stage
    rc: int
    seconds: float
    error: Optional[str] = None       # msg de falha (rc!=0 ou artefato ausente)


def run_stage(stage: Stage, ns: argparse.Namespace, python: str) -> StageResult:
    script_path = os.path.join(project_dir(), stage.script)
    if not os.path.isfile(script_path):
        return StageResult(stage, rc=127, seconds=0.0,
                           error=f"script não encontrado: {stage.script} (esperado ao lado do pipeline).")

    args = stage.build_args(ns)
    cmd = [python, script_path, *args]
    log.info("─" * 80)
    log.info("▶ ETAPA %d/%d — %s", stage.number, len(STAGES), stage.title)
    log.info("  cmd: %s", " ".join(shlex.quote(c) for c in cmd))
    log.info("─" * 80)

    t0 = time.monotonic()
    try:
        # saída transmitida ao vivo (herda stdout/stderr do pipeline)
        proc = subprocess.run(cmd, cwd=project_dir())
        rc = proc.returncode
    except KeyboardInterrupt:
        return StageResult(stage, rc=130, seconds=time.monotonic() - t0,
                           error="interrompido pelo usuário (Ctrl-C).")
    except Exception as e:  # noqa
        return StageResult(stage, rc=1, seconds=time.monotonic() - t0,
                           error=f"falha ao executar o subprocesso: {e}")
    secs = time.monotonic() - t0

    if rc != 0:
        return StageResult(stage, rc=rc, seconds=secs,
                           error=f"terminou com código de saída {rc}.")
    if stage.verify:                                   # portão do artefato-chave
        problem = stage.verify()
        if problem:
            return StageResult(stage, rc=rc, seconds=secs,
                               error=f"código 0, mas {problem}")
    return StageResult(stage, rc=0, seconds=secs, error=None)


def _fmt_secs(s: float) -> str:
    return f"{s:.1f}s" if s < 60 else f"{int(s // 60)}m{int(s % 60):02d}s"


# ------------------------------------------------------------------------------
# Orquestração
# ------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Pipeline da ET: extract.py -> generate_docs.py -> lc_CapETGenerator.py "
                    "(fail-fast: a próxima etapa só roda se a atual não der erro).")
    # flags mapeadas para as etapas
    ap.add_argument("--dry-run", action="store_true",
                    help="Sem IA/credencial (repassa às etapas 2 e 3; a Etapa 1 é sempre determinística).")
    ap.add_argument("--root", default=None, help="Pasta inbound (Etapas 1 e 2). Padrão: input/.")
    ap.add_argument("--date", default=None, help="Data DDMMYYYY para a Etapa 1 (default: hoje).")
    ap.add_argument("--only", default=None, help="Filtra objetos na Etapa 2 (nomes sep. por vírgula).")
    ap.add_argument("--force", action="store_true", help="Etapa 2: refaz DOCs já preenchidos.")
    ap.add_argument("--llm-review", action="store_true", help="Etapa 3: IA revisa/redige o Objetivo.")
    ap.add_argument("--no-md", action="store_true", help="Etapa 3: não gera o markdown de pré-visualização.")
    ap.add_argument("--output", default=None, help="Etapa 3: pasta de saída da ET.")
    ap.add_argument("--providers-path", default=None, help="Etapa 2: caminho do llm_providers.py.")
    ap.add_argument("--chunker-path", default=None, help="Etapa 2: caminho do abap_chunker.py.")
    # repasse de argumentos crus por etapa
    ap.add_argument("--extract-args", default="", help='Args extras crus p/ a Etapa 1 (ex.: "--src-chars 12000").')
    ap.add_argument("--docs-args", default="", help='Args extras crus p/ a Etapa 2.')
    ap.add_argument("--et-args", default="", help='Args extras crus p/ a Etapa 3.')
    # controle do pipeline
    ap.add_argument("--python", default=sys.executable, help="Interpretador Python (default: o atual).")
    ap.add_argument("--start-at", type=int, default=1, choices=[1, 2, 3],
                    help="Começa a partir desta etapa (útil para retomar; 1=extract, 2=docs, 3=et).")
    args = ap.parse_args()

    # guarda os extras (crus) já divididos em lista para os montadores usarem
    args._extract_extra = shlex.split(args.extract_args)
    args._docs_extra = shlex.split(args.docs_args)
    args._et_extra = shlex.split(args.et_args)

    log.info("=" * 80)
    log.info("  Capgemini SAP AI — Pipeline da ET (3 etapas, fail-fast)")
    log.info("=" * 80)
    log.info("  Projeto  : %s", project_dir())
    log.info("  Modo     : %s", "DRY-RUN (sem IA nas etapas 2 e 3)" if args.dry_run else "COMPLETO (com IA)")
    log.info("  Python   : %s", args.python)
    if args.start_at > 1:
        log.info("  Início   : Etapa %d (etapas anteriores puladas)", args.start_at)
    log.info("=" * 80)

    results: list[StageResult] = []
    t_all = time.monotonic()
    for stage in STAGES:
        if stage.number < args.start_at:
            log.info("• ETAPA %d — %s: PULADA (--start-at %d)", stage.number, stage.title, args.start_at)
            continue

        res = run_stage(stage, args, args.python)
        results.append(res)

        if res.error:
            log.error("✗ ETAPA %d — %s: FALHOU (%s) [%s]",
                      stage.number, stage.title, res.error, _fmt_secs(res.seconds))
            log.error("=" * 80)
            log.error("PIPELINE INTERROMPIDO na Etapa %d. As etapas seguintes NÃO foram executadas.",
                      stage.number)
            log.error("=" * 80)
            return res.rc or 1
        log.info("✓ ETAPA %d — %s: OK [%s]", stage.number, stage.title, _fmt_secs(res.seconds))

    total = _fmt_secs(time.monotonic() - t_all)
    log.info("=" * 80)
    log.info("PIPELINE CONCLUÍDO — %d etapa(s) OK em %s.", len(results), total)
    # aponta o que foi produzido
    produced = sorted(glob.glob(os.path.join(et_gerada_dir(), "ET_*.docx")) +
                      glob.glob(os.path.join(et_gerada_dir(), "ET_*.md")),
                      key=os.path.getmtime, reverse=True)
    if produced:
        log.info("  ET gerada:")
        for f in produced[:4]:
            log.info("    • %s", f)
    log.info("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())