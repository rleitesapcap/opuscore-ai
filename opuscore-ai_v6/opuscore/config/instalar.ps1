# Instala o monorepo no Windows (PowerShell). Equivalente ao scripts/instalar.sh.
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1 -Motores
#   powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1 -Venv C:\venvs\opuscore
param([switch]$Motores, [string]$Venv = ".venv")
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONUTF8 = "1"
 
if (Get-Command py -ErrorAction SilentlyContinue) { & py -3 -m venv $Venv } else { & python -m venv $Venv }
if ($LASTEXITCODE -ne 0) { throw "Não consegui criar o ambiente virtual. O Python 3.11+ está instalado?" }
$py = Join-Path $Venv "Scripts\python.exe"
 
& $py -m pip install -q -U pip
$pacotes = @("packages/core", "packages/connectors", "packages/ef[imagens,pdf]", "packages/orchestrator",
             "packages/web", "packages/platform", "consultores/dev-abap", "consultores/funcional-mm",
             "consultores/arquiteto", "consultores/funcional-sd", "consultores/integracao",
             "consultores/lider-tecnico", "consultores/qualidade")
$argsPip = @()
foreach ($p in $pacotes) { $argsPip += "-e"; $argsPip += $p }
& $py -m pip install -q @argsPip
if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar os pacotes." }
if ($Motores) {
  & $py -m pip install -q -e "consultores/dev-abap[motores]"
  if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar as bibliotecas dos motores." }
}
& $py -m pip install -q pytest import-linter
 
if (-not (Test-Path "config/config.yaml")) { Copy-Item "config/config.example.yaml" "config/config.yaml" }
if (-not (Test-Path "config/.env")) { Copy-Item "config/.env.example" "config/.env" }
 
Write-Host "Pronto. Ative com:  $Venv\Scripts\Activate.ps1"
Write-Host "Edite config\config.yaml e config\.env, depois rode:  opuscore-servidor"
 