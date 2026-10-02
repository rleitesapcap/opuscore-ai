# OPUSCORE-AI — Instalação no Linux (WSL) e no Windows

Este guia é só sobre **instalar e subir** o OPUSCORE. Para executar cada pacote separadamente,
rodar os testes e criar consultores, veja `docs/COMO_EXECUTAR.md`.

| | Linux / WSL | Windows |
|---|---|---|
| Recomendado para | Quem já usa o WSL com Docker e o SAP trial | Quem não usa WSL |
| Instalador | `bash scripts/instalar.sh` | `scripts\instalar.bat` (Prompt de Comando) |
| Ativar o ambiente | `source .venv/bin/activate` | `.venv\Scripts\activate.bat` (cmd) ou `.venv\Scripts\Activate.ps1` (PowerShell) |
| Subir tudo | `opuscore-servidor` | `opuscore-servidor` |

---

## 1. Antes de começar (os dois sistemas)

1. **Python 3.12** (testado). O 3.11 também serve. Versões mais novas podem ainda não ter
   pacotes prontos de algumas bibliotecas dos motores (principalmente no Windows), e aí a
   instalação tenta compilar e falha.
2. **Extraia o ZIP numa pasta curta e local**, sem espaços e fora do OneDrive:
   - Linux/WSL: `~/opuscore`
   - Windows: `C:\opuscore`
3. **Acesso à internet para o `pip`.** Na rede de um cliente com proxy, veja a seção 6.
4. **SAP:** o container `a4h` no ar (`docker start a4h` e aguardar "All services have been
   started" em `docker logs -f a4h`).

---

## 2. Linux / WSL

### 2.1 Pré-requisitos

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip
python3 --version            # 3.11 ou 3.12
```

### 2.2 Instalar com o script

```bash
cd ~
unzip opuscore-monorepo.zip
cd opuscore
bash scripts/instalar.sh --motores      # sem --motores, pula as bibliotecas pesadas de Gerar ET e Remediar
source .venv/bin/activate
```

### 2.3 Instalar manualmente (se o script falhar)

```bash
cd ~/opuscore
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e packages/core
pip install -e packages/connectors
pip install -e "packages/ef[imagens,pdf]"
pip install -e packages/orchestrator
pip install -e packages/web
pip install -e packages/platform
pip install -e consultores/dev-abap -e consultores/funcional-mm
pip install -e consultores/arquiteto -e consultores/funcional-sd -e consultores/integracao \
            -e consultores/lider-tecnico -e consultores/qualidade
pip install -e "consultores/dev-abap[motores]"        # opcional: Gerar ET e Remediar
pip install pytest import-linter
cp -n config/config.example.yaml config/config.yaml
cp -n config/.env.example config/.env
```

Um comando por linha: se algum falhar, você sabe exatamente qual.

---

## 3. Windows

### 3.1 Pré-requisitos

1. Baixe o **Python 3.12** em python.org (instalador "Windows installer (64-bit)").
2. No instalador, marque **"Add python.exe to PATH"** e mantenha o **"py launcher"** marcado.
3. Desative o atalho da Microsoft Store que finge ser o Python:
   **Configurações → Aplicativos → Configurações avançadas de aplicativos → Aliases de execução
   de aplicativos** → desligue `python.exe` e `python3.exe`.
4. Feche e abra o terminal, e confira:
   ```bat
   py -3.12 --version
   ```

### 3.2 Opção A — Instalador `.bat` (recomendado)

Funciona no **Prompt de Comando** e não depende da política de execução do PowerShell.

```bat
cd C:\opuscore
scripts\instalar.bat --motores
.venv\Scripts\activate.bat
```

Sem `--motores`, pula as bibliotecas pesadas de Gerar ET e Remediar.

### 3.3 Opção B — Instalador PowerShell

```powershell
cd C:\opuscore
Get-ChildItem -Recurse . | Unblock-File          # libera os arquivos vindos do ZIP baixado
powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1 -Motores
.venv\Scripts\Activate.ps1
```

Se a ativação for recusada ("a execução de scripts foi desabilitada neste sistema"), rode uma vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3.4 Opção C — Instalação manual (se os instaladores falharem)

No **Prompt de Comando**, um comando por linha:

```bat
cd C:\opuscore
set PYTHONUTF8=1
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -U pip
pip install -e packages/core
pip install -e packages/connectors
pip install -e "packages/ef[imagens,pdf]"
pip install -e packages/orchestrator
pip install -e packages/web
pip install -e packages/platform
pip install -e consultores/dev-abap -e consultores/funcional-mm
pip install -e consultores/arquiteto -e consultores/funcional-sd -e consultores/integracao -e consultores/lider-tecnico -e consultores/qualidade
pip install -e "consultores/dev-abap[motores]"
pip install pytest import-linter
if not exist config\config.yaml copy config\config.example.yaml config\config.yaml
if not exist config\.env copy config\.env.example config\.env
```

No **PowerShell**, troque as linhas de ativação e de cópia:

```powershell
$env:PYTHONUTF8 = "1"
.venv\Scripts\Activate.ps1
if (-not (Test-Path config\config.yaml)) { Copy-Item config\config.example.yaml config\config.yaml }
if (-not (Test-Path config\.env)) { Copy-Item config\.env.example config\.env }
```

---

## 4. Configurar (os dois sistemas)

### 4.1 `config/config.yaml`, seção `sap`

O exemplo já vem apontando para o trial local:

```yaml
sap:
  default: "a4h"
  systems:
    a4h:
      base_url: "http://localhost:50000"
      client: "001"
      auth: "basic"
      user: "${SAP_USER}"
      password: "${SAP_PASSWORD}"
      verify_ssl: false
      read_only: true
```

**OPUSCORE no Windows e SAP trial no WSL:** o `localhost:50000` funciona com
`networkingMode=mirrored` no `C:\Users\<você>\.wslconfig`. Sem isso, troque `localhost` pelo IP
do WSL (`wsl hostname -I`).

### 4.2 `config/.env`, o mínimo

```
SAP_USER=DEVELOPER
SAP_PASSWORD=sua-senha
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL_MAIN=claude-opus-5-5
LLM_TEMPERATURE=off
EF_INTAKE_MODEL=claude-haiku-4-5-20251001
EF_INTAKE_MAX_TOKENS=32000
PYTHONUTF8=1
```

Para a remediação: `LLM_API_KEY` e `WORKSPACE_ID` da Generative Engine da Capgemini.
No Windows, use barras normais em caminhos: `OPUSCORE_DATA=C:/opuscore/data`.

---

## 5. Subir e conferir (os dois sistemas)

Com o ambiente ativado:

```bash
python -c "import opuscore_platform, opuscore_connectors, opuscore_ef; print('Pacotes OK')"
python -m opuscore_connectors.cli health        # testa a conexão com o SAP, sem subir a tela
opuscore-servidor                               # sobe tudo em http://127.0.0.1:8787
```

Com o servidor no ar, abra no navegador:

| Endereço | Esperado |
|---|---|
| `http://127.0.0.1:8787` | A tela do OPUSCORE |
| `http://127.0.0.1:8787/api/plataforma/plugins` | Os 8 consultores com `"status": "ok"` |
| `http://127.0.0.1:8787/health` | `{"ok": true, ...}` com o SAP no ar (502 = SAP não respondeu; 503 = servidor MCP não subiu) |

Um consultor só: `opuscore-dev --plugins funcional-mm --porta 8801`.
Filtro por variável — Linux: `OPUSCORE_PLUGINS=funcional-mm opuscore-servidor`;
PowerShell: `$env:OPUSCORE_PLUGINS="funcional-mm"; opuscore-servidor`;
cmd: `set OPUSCORE_PLUGINS=funcional-mm` e depois `opuscore-servidor`.

---

## 6. Problemas comuns na instalação

| Sintoma | Causa provável | Solução |
|---|---|---|
| `python` abre a Microsoft Store ou "Python não foi encontrado" | Atalho da Store no lugar do Python | Desative os aliases (3.1, passo 3) e instale do python.org |
| "a execução de scripts foi desabilitada neste sistema" | Política de execução do PowerShell | Use o `instalar.bat`, ou `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| O `.ps1` não roda mesmo com a política liberada | Arquivo marcado como "baixado da internet" | `Get-ChildItem -Recurse . \| Unblock-File` |
| `Microsoft Visual C++ 14.0 or greater is required` ou "Failed building wheel" | Python novo demais, sem pacote pronto da biblioteca | Instale o **Python 3.12** e recrie o `.venv` (apague a pasta antes) |
| `Could not find a version that satisfies the requirement` ou tempo esgotado no `pip` | Sem internet ou com proxy corporativo | `set HTTPS_PROXY=http://usuario:senha@proxy:porta` (cmd) ou `$env:HTTPS_PROXY="..."` (PowerShell), e rode de novo |
| `SSL: CERTIFICATE_VERIFY_FAILED` no `pip` | Proxy que inspeciona HTTPS | `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ...`, ou peça o certificado da rede à TI |
| Erro de caminho longo (`No such file or directory` em pasta muito funda) | Limite de 260 caracteres do Windows | Extraia em `C:\opuscore` ou ative caminhos longos (PowerShell como administrador): `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name LongPathsEnabled -Value 1 -PropertyType DWORD -Force` |
| Arquivos "em uso" ou instalação muito lenta | Antivírus ou OneDrive sincronizando a pasta | Use uma pasta fora do OneDrive; se preciso, peça exceção do antivírus para a pasta do projeto |
| `UnicodeEncodeError` / caracteres estranhos no log | Console do Windows em cp1252 | `set PYTHONUTF8=1` (cmd) ou `$env:PYTHONUTF8="1"`, e deixe `PYTHONUTF8=1` no `config/.env` |
| `bash: scripts/instalar.sh: /bin/bash^M` no WSL | Arquivo com final de linha do Windows | `sed -i 's/\r$//' scripts/instalar.sh` |
| `opuscore-servidor` não é reconhecido | Ambiente virtual não ativado | Ative o `.venv` (tabela no topo) ou use `python -m opuscore_platform` |
| Instalação parou no meio e agora dá erros estranhos | `.venv` corrompido | Apague a pasta `.venv` e instale de novo |

---

## 7. Se ainda assim não instalar

Rode o instalador salvando a saída num arquivo e me mande as **últimas 40 linhas**:

- Windows (cmd): `scripts\instalar.bat > instalacao.log 2>&1`
- Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1 *> instalacao.log`
- Linux/WSL: `bash scripts/instalar.sh > instalacao.log 2>&1`

Mande também a saída de `py -3.12 --version` (Windows) ou `python3 --version` (Linux).