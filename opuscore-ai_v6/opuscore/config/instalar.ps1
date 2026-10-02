# Instalador do OPUSCORE-AI para Windows (PowerShell). Arquivo so com ASCII de proposito.
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1 -Motores
# Alternativa sem PowerShell: scripts\instalar.bat
param([switch]$Motores, [string]$Venv = ".venv")
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONUTF8 = "1"

function Passo($t) { Write-Host "`n== $t" -ForegroundColor Cyan }
function Rodar($exe, [string[]]$a) {
  & $exe @a
  if ($LASTEXITCODE -ne 0) { throw "Falhou: $exe $($a -join ' ')" }
}

Passo "1/5 Criando o ambiente virtual em $Venv"
if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3.12 -m venv $Venv 2>$null
  if (-not (Test-Path "$Venv\Scripts\python.exe")) { Rodar "py" @("-3", "-m", "venv", $Venv) }
} else { Rodar "python" @("-m", "venv", $Venv) }
$py = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $py)) { throw "Nao consegui criar o ambiente virtual. Instale o Python 3.12 de python.org." }
Rodar $py @("--version")

Passo "2/5 Atualizando o pip"
Rodar $py @("-m", "pip", "install", "--disable-pip-version-check", "-U", "pip")

Passo "3/5 Instalando os pacotes do OPUSCORE"
$pacotes = @("packages/core", "packages/connectors", "packages/ef[imagens,pdf]", "packages/orchestrator",
             "packages/web", "packages/platform", "consultores/dev-abap", "consultores/funcional-mm",
             "consultores/arquiteto", "consultores/funcional-sd", "consultores/integracao",
             "consultores/lider-tecnico", "consultores/qualidade")
$argsPip = @("-m", "pip", "install", "--disable-pip-version-check")
foreach ($p in $pacotes) { $argsPip += "-e"; $argsPip += $p }
Rodar $py $argsPip

Passo "4/5 Bibliotecas dos motores"
if ($Motores) { Rodar $py @("-m", "pip", "install", "--disable-pip-version-check", "-e", "consultores/dev-abap[motores]") }
else { Write-Host "Ignoradas (use -Motores para Gerar ET e Remediar)" }
Rodar $py @("-m", "pip", "install", "--disable-pip-version-check", "pytest", "import-linter")

Passo "5/5 Configuracao"
if (-not (Test-Path "config/config.yaml")) { Copy-Item "config/config.example.yaml" "config/config.yaml" }
if (-not (Test-Path "config/.env")) { Copy-Item "config/.env.example" "config/.env" }
Rodar $py @("-c", "import opuscore_platform, opuscore_connectors, opuscore_ef; print('Pacotes OK')")

Write-Host "`nPronto. Ative com:  $Venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "Edite config\config.yaml e config\.env e rode:  opuscore-servidor"