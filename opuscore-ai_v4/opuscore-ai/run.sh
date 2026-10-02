#!/usr/bin/env bash
# OPUSCORE-AI — bootstrap + execução (WSL2 / Linux)
set -euo pipefail
cd "$(dirname "$0")/backend"

if [ ! -d .venv ]; then
  echo ">> Criando ambiente virtual..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo ">> Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f config.yaml ]; then
  cp config.example.yaml config.yaml
  echo ">> Criado backend/config.yaml — AJUSTE host/mandante do SAP antes de conectar."
fi
if [ ! -f .env ]; then
  cp .env.example .env
  echo ">> Criado backend/.env — coloque SAP_USER, SAP_PASSWORD e a chave do LLM."
fi

echo ">> Subindo o OPUSCORE-AI em http://127.0.0.1:8787"
python -m opuscore.api
