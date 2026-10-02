"""Camada de adaptação dos motores de ET e remediação.

Único lugar que conhece as convenções dos motores (vieram de fora): pastas esperadas
(01_EF, 02_CODIGOS, 01_ET_GERADA), variáveis de ambiente (LLM_MODEL vs LLM_MODEL_MAIN,
LLM_TEMPERATURE, LLM_USAGE_LOG), execução como subprocesso, diagnóstico de falha e
medição de custo. Quem mexe num motor não precisa conhecer a plataforma, e vice-versa.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from opuscore_core.sdk.uso import resumo_log

MOTORES = Path(__file__).resolve().parents[1] / "motores"
ET_DIR = MOTORES / "et"
REM_DIR = MOTORES / "remediacao"


@dataclass
class ResultadoMotor:
    rc: int
    log: str
    arquivos: list[Path] = field(default_factory=list)
    uso_ia: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.rc == 0

    @property
    def motivo_falha(self) -> list[str]:
        return [] if self.ok else diagnose(self.log)


# ---------------------------------------------------------------------------
# Checagem prévia da IA dos motores (mesmas variáveis do llm_providers.py)
# ---------------------------------------------------------------------------
def llm_preflight(motor: str = "et") -> tuple[bool, str]:
    """Confere se as variáveis que o motor exige estão definidas. Não chama a IA.

    ATENÇÃO: o motor de remediação (lc_CapRemediation.py) usa um cliente próprio
    que fala SOMENTE com a Generative Engine da Capgemini, ignorando LLM_PROVIDER.
    Por isso, para a remediação, as credenciais da Capgemini são sempre exigidas."""
    if motor == "remediation":
        faltam = [v for v in ("LLM_API_KEY", "WORKSPACE_ID") if not os.environ.get(v, "").strip()]
        if faltam:
            return False, ("O motor de remediação usa somente a Generative Engine da Capgemini "
                           f"(independe do LLM_PROVIDER) e exige {', '.join(faltam)} no config/.env.")
        return True, "capgemini"
    prov = (os.environ.get("LLM_PROVIDER") or "capgemini").strip().lower()
    if prov in ("capgemini", "generative-engine", "ge"):
        faltam = [v for v in ("LLM_API_KEY", "WORKSPACE_ID") if not os.environ.get(v, "").strip()]
    elif prov in ("anthropic", "anthropic-api", "api"):
        faltam = [] if os.environ.get("ANTHROPIC_API_KEY", "").strip() else ["ANTHROPIC_API_KEY"]
    elif prov in ("claude_code", "claude-code", "cli", "cc"):
        faltam = [] if shutil.which("claude") else ["CLI 'claude' no PATH"]
    else:
        return False, f"LLM_PROVIDER '{prov}' desconhecido. Use capgemini | anthropic | claude_code."
    if faltam:
        return False, (f"IA dos motores não configurada: LLM_PROVIDER={prov} exige "
                       f"{', '.join(faltam)} no config/.env.")
    return True, prov


# ---------------------------------------------------------------------------
# Objetos e materialização de source
# ---------------------------------------------------------------------------
# sufixo por tipo ADT — o motor de ET identifica o objeto pelo sufixo composto
_SUFFIX_BY_TYPE = {
    "CLAS": ".clas.abap", "INTF": ".intf.abap", "DDLS": ".ddls.asddls",
    "BDEF": ".bdef.asbdef", "DDLX": ".ddlx.asddlx", "SRVB": ".srvb.asrvb",
    "SRVD": ".asrvd", "DCLS": ".dcl",
}


def _fname(name: str, adt_type: str = "") -> str:
    prefix = (adt_type or "").split("/")[0].upper()
    return name.strip() + _SUFFIX_BY_TYPE.get(prefix, ".abap")


def write_sources(items: list[dict], dest: Path) -> list[str]:
    """items = [{'name','source','type'?}]. Grava um arquivo por objeto."""
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for it in items:
        src = it.get("source") or ""
        if not src.strip():
            continue
        (dest / _fname(it["name"], it.get("type", ""))).write_text(src, encoding="utf-8")
        written.append(it["name"])
    return written


def run_pipeline(script: Path, args: list[str], cwd: Path, env_extra: dict) -> tuple[int, str]:
    """Executa um pipeline incorporado como subprocesso (isola estado, herda o
    .env do backend via ambiente). Retorna (rc, cauda da saída combinada)."""
    env = os.environ.copy()
    env.update(env_extra or {})
    # Os motores leem o modelo com nomes diferentes: a Etapa 2 da ET (generate_docs.py)
    # usa LLM_MODEL; a montagem final e o .env do projeto usam LLM_MODEL_MAIN. Sem
    # LLM_MODEL, o motor cai no modelo fixo do código, que pode não existir na conta.
    if not (env.get("LLM_MODEL") or "").strip() and (env.get("LLM_MODEL_MAIN") or "").strip():
        env["LLM_MODEL"] = env["LLM_MODEL_MAIN"].strip()
    proc = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd), env=env, capture_output=True, text=True, timeout=1800,
    )
    full = ((proc.stdout or "") + "\n" + (proc.stderr or "")).strip()
    return proc.returncode, full[-60000:]


_DIAG = re.compile(r"(\[✗ FAIL\].*|Abortando:.*|FALHOU.*|Traceback.*|\w*Error: .*|PIPELINE INTERROMPIDO.*)")


def diagnose(log: str) -> list[str]:
    """Linhas que explicam uma falha do motor (validação da IA, etapa que falhou,
    exceções), na ordem em que aparecem — para mostrar em destaque na tela."""
    seen, out = set(), []
    for line in (log or "").splitlines():
        m = _DIAG.search(line)
        if m:
            txt = re.sub(r"^\d{2}:\d{2}:\d{2} \[\w+\]\s*", "", m.group(1)).strip()
            if txt and txt not in seen:
                seen.add(txt); out.append(txt[:400])
    return out[:8]


def collect(folder: Path, patterns: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for pat in patterns:
        out += sorted(folder.rglob(pat), key=lambda p: p.stat().st_mtime, reverse=True)
    return out


# ---------------------------------------------------------------------------
# Execução dos motores (origem = diretório materializado do S/4)
# ---------------------------------------------------------------------------
def run_remediation(sources: list[dict]) -> ResultadoMotor:
    """sources = [{'name','source'}] já aprovados. Materializa e roda o motor."""
    work = Path(tempfile.mkdtemp(prefix="opuscore_rem_"))
    in_dir, out_dir = work / "input", work / "output"
    write_sources(sources, in_dir)
    uso_log = work / "uso_ia.jsonl"
    rc, log = run_pipeline(
        REM_DIR / "run_pipeline.py", [], REM_DIR,
        {"REMEDIATION_INPUT_DIR": str(in_dir), "REMEDIATION_OUTPUT_DIR": str(out_dir),
         "LLM_USAGE_LOG": str(uso_log)},
    )
    return ResultadoMotor(rc, log, collect(out_dir, ("*.abap", "*.txt", "*.md")), resumo_log(uso_log))


def prepare_et_workspace(sources: list[dict], ef_path: Path) -> tuple[Path, Path]:
    """Monta o layout do motor de ET: <root>/01_EF (EF original) e <root>/02_CODIGOS."""
    work = Path(tempfile.mkdtemp(prefix="opuscore_et_"))
    root, out_dir = work / "input", work / "output"
    ef_dir = root / os.environ.get("DIR_EF", "01_EF")
    codes_dir = root / os.environ.get("DIR_CODIGOS", "02_CODIGOS")
    ef_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ef_path, ef_dir / ef_path.name)   # arquivo ORIGINAL, sem conversão
    write_sources(sources, codes_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return root, out_dir


def run_et(sources: list[dict], ef_path: Path) -> ResultadoMotor:
    """sources = [{'name','source','type'}] + EF (arquivo .docx/.pdf). Roda o motor da ET."""
    root, out_dir = prepare_et_workspace(sources, ef_path)
    uso_log = root.parent / "uso_ia.jsonl"
    # o pipeline confere a ET em ET_OUTBOUND_DIR/DIR_ET_GERADA; a Etapa 3 precisa gravar lá
    et_gerada = out_dir / os.environ.get("DIR_ET_GERADA", "01_ET_GERADA")
    et_gerada.mkdir(parents=True, exist_ok=True)
    rc, log = run_pipeline(
        ET_DIR / "run_et_pipeline.py",
        ["--root", str(root), "--output", str(et_gerada)], ET_DIR,
        {
            "ET_OUTBOUND_DIR": str(out_dir),
            "DIR_ET_GERADA": et_gerada.name,
            # fixa as pastas: o .env.example do motor usa outros nomes
            # (Functional-Specification/Codigos); a plataforma monta 01_EF/02_CODIGOS
            "DIR_EF": os.environ.get("DIR_EF", "01_EF"),
            "DIR_CODIGOS": os.environ.get("DIR_CODIGOS", "02_CODIGOS"),
            "DIR_TEMPLATE_LOCAL": "rag",   # template Word oficial fica em motores/et/rag/
            "LLM_USAGE_LOG": str(uso_log),
        },
    )
    return ResultadoMotor(rc, log, collect(out_dir, ("ET_*.docx", "ET_*.md", "*.docx")), resumo_log(uso_log))
