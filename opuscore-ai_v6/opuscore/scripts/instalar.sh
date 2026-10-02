#!/usr/bin/env bash
# Instala o monorepo inteiro em modo editável (cada pacote continua independente).
#   scripts/instalar.sh                 # tudo, sem as bibliotecas pesadas dos motores do Dev
#   scripts/instalar.sh --motores       # inclui LangChain etc. (para rodar Gerar ET e Remediar)
#   scripts/instalar.sh --venv /caminho # outro ambiente virtual (padrão: .venv)
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=.venv; MOTORES=0
while [ $# -gt 0 ]; do
  case "$1" in
    --motores) MOTORES=1 ;;
    --venv) VENV="$2"; shift ;;
    *) echo "opção desconhecida: $1"; exit 1 ;;
  esac
  shift
done
python3 -m venv "$VENV"
# shellcheck disable=SC1091
. "$VENV/bin/activate"
python -m pip install -q -U pip
pip install -q -e packages/core -e packages/connectors -e "packages/ef[imagens,pdf]" -e packages/orchestrator \
  -e packages/web -e packages/platform \
  -e consultores/dev-abap -e consultores/funcional-mm -e consultores/arquiteto -e consultores/funcional-sd \
  -e consultores/integracao -e consultores/lider-tecnico -e consultores/qualidade
if [ "$MOTORES" = 1 ]; then pip install -q -e "consultores/dev-abap[motores]"; fi
pip install -q pytest import-linter
[ -f config/config.yaml ] || cp config/config.example.yaml config/config.yaml
[ -f config/.env ] || cp config/.env.example config/.env
echo "Pronto. Ative com:  source $VENV/bin/activate"
echo "Edite config/config.yaml e config/.env, depois rode:  opuscore-servidor"
