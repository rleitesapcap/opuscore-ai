"""CLI do pacote EF: python -m opuscore_ef.cli <EF.docx> [--estado APROVADA] [--sem-ia] ..."""
from .intake.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
