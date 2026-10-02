"""Regras do pacote Web e das telas dos consultores (sem navegador)."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
STATIC = RAIZ / "packages/web/opuscore_web/static"
TELAS = {"dev-abap": RAIZ / "consultores/dev-abap/opuscore_dev/web",
         "funcional-mm": RAIZ / "consultores/funcional-mm/opuscore_mm/web",
         "orquestrador": RAIZ / "packages/orchestrator/opuscore_orchestrator/web"}


def _seletores(css: str):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for bloco in re.findall(r"([^{}]+)\{[^{}]*\}", css):
        for sel in bloco.split(","):
            if sel.strip():
                yield sel.strip()


def test_shell_e_design_system_existem():
    for p in ("index.html", "shell/app.js", "sdk/ui.js", "sdk/ctx.js", "ds/tokens.css", "ds/components.css"):
        assert (STATIC / p).is_file(), p
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    assert 'type="module" src="/shell/app.js"' in html and "/ds/tokens.css" in html


def test_css_de_consultor_e_escopado():
    for key, pasta in TELAS.items():
        for css in pasta.glob("*.css"):
            fora = [s for s in _seletores(css.read_text(encoding="utf-8")) if not s.startswith(f".c-{key}")]
            assert not fora, f"{css.name}: regras fora de .c-{key}: {fora[:3]}"


def test_telas_exportam_mount_e_nao_importam_o_shell():
    for key, pasta in TELAS.items():
        js = (pasta / "main.js").read_text(encoding="utf-8")
        assert "export async function mount(area, ctx)" in js and "export function unmount" in js, key
        assert not re.search(r"^\s*import\b", js, re.M), f"{key}: a tela recebe tudo pelo ctx, sem import"


def test_cores_so_no_design_system():
    for key, pasta in TELAS.items():
        for css in pasta.glob("*.css"):
            assert not re.search(r"--[a-z0-9]+\s*:", css.read_text(encoding="utf-8")), f"{css.name} define token de cor"
