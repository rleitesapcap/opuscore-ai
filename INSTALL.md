# OPUSCORE-AI — Instalação e execução

Ferramenta local. Roda na sua máquina; as credenciais SAP nunca saem dela.
Um único processo (backend FastAPI) sobe a API **e** serve o frontend.

---

## 1. Pré-requisitos

- **Python 3.11+** (`python3 --version`)
- WSL2 / Linux / macOS (no Windows puro, use o WSL2)
- Acesso de rede à porta HTTPS do ICM do SAP e usuário com autorização de
  desenvolvedor no ADT (necessário só para conectar de verdade — a instalação e a
  interface sobem sem SAP)
- Uma chave de LLM (Anthropic ou xAI) **ou** Ollama/AIP local rodando

## 2. Descompactar

```bash
unzip opuscore-ai.zip
cd opuscore-ai
```

## 3. Caminho rápido (script único — WSL2/Linux/macOS)

```bash
bash run.sh
```

O script cria o ambiente virtual, instala tudo, gera `config.yaml` e `.env` na
primeira vez e sobe a ferramenta. Depois de rodar uma vez, **edite os dois
arquivos** (passo 5) e rode `bash run.sh` de novo.

## 4. Caminho manual (se preferir controlar cada passo)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp config.example.yaml config.yaml
cp .env.example .env
```

## 5. Configurar

Edite **`backend/config.yaml`**:
- `sap.systems.cliente_dev.base_url` → `https://SEU_HOST:PORTA` (porta HTTPS do ICM)
- `sap.systems.cliente_dev.client` → seu mandante (ex.: `300`)
- `read_only: true` → **deixe assim** (trava de segurança; não altera nada no SAP)
- `llm.default` → `claude`, `grok` ou `aip` (Ollama local)

Edite **`backend/.env`** (segredos, fora do git):
```
SAP_USER=SEU_USUARIO
SAP_PASSWORD=sua_senha
ANTHROPIC_API_KEY=sk-ant-...        # se usar Claude
# XAI_API_KEY=xai-...               # se usar Grok
```

## 6. Rodar e abrir

```bash
cd backend
source .venv/bin/activate
python -m opuscore.api
```

Abra no navegador: **http://127.0.0.1:8787**

Na barra lateral, o status mostra a conexão e o selo **SOMENTE-LEITURA**.

## 7. Testar

**a) A trava de segurança (não toca o SAP):**
```bash
python -m opuscore.cli test-guard MARA delete
# -> "Bloqueado como esperado: ... SOMENTE-LEITURA ..."
```

**b) A conexão:**
```bash
python -m opuscore.cli health
# -> Conexão ADT OK / Modo: SOMENTE-LEITURA
```

**c) A primeira análise** — pela interface, digite `MARA` e clique **Analisar**;
ou pela CLI:
```bash
python -m opuscore.cli report MARA
```

Comece por um objeto **standard** (`MARA`) para validar a cadeia ADT → evidência
→ LLM sem depender de nada custom do cliente.

---

## Solução de problemas

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Frontend abre mas status "backend offline" | API não subiu | rode `python -m opuscore.api` |
| `health` HTTP 401 | usuário/senha | confira `.env` |
| `health` HTTP 403 | falta autorização ADT | pedir perfil de dev no cliente |
| `health` HTTP 404 | nós ICF do ADT inativos | ativar `/sap/bc/adt/*` (SICF) |
| erro de SSL/timeout | porta ICM não visível do WSL2 | liberar rede / `verify_ssl:false` em dev |
| `report` OK mas "quem usa" vazio | payload do `usageReferences` varia por release | me mande o retorno; calibro o parsing |
| erro do LLM ao analisar | chave/endpoint | confira `.env` ou aponte `llm.default: aip` |

Teste de rede cru, isolando o Python:
```bash
curl -k -u "$SAP_USER:$SAP_PASSWORD" \
  "https://SEU_HOST:PORTA/sap/bc/adt/core/discovery?sap-client=300"
```
Se voltar XML, o ADT está no ar.

## Nota de segurança

A ferramenta é **somente-leitura** por padrão e não tem caminho de escrita ativo.
Toda tentativa de alteração/exclusão é bloqueada antes de tocar o sistema e
registrada em `backend/audit/opuscore-audit.jsonl`.
