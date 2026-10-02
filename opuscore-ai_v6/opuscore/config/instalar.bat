@echo off
REM Instalador do OPUSCORE-AI para Windows (Prompt de Comando). Nao depende do PowerShell.
REM   scripts\instalar.bat              instala tudo (sem as bibliotecas pesadas dos motores)
REM   scripts\instalar.bat --motores    inclui as bibliotecas dos motores de ET e Remediacao
setlocal
cd /d "%~dp0\.."
set PYTHONUTF8=1
set VENV=.venv

echo [1/5] Criando o ambiente virtual em %VENV% ...
where py >nul 2>nul
if %errorlevel%==0 (py -3.12 -m venv %VENV% 2>nul || py -3 -m venv %VENV%) else (python -m venv %VENV%)
if not exist "%VENV%\Scripts\python.exe" (
  echo [ERRO] Nao consegui criar o ambiente virtual. Instale o Python 3.12 de python.org
  echo        marcando "Add python.exe to PATH" e o "py launcher".
  exit /b 1
)
set PY=%VENV%\Scripts\python.exe
"%PY%" --version

echo [2/5] Atualizando o pip ...
"%PY%" -m pip install --disable-pip-version-check -U pip || goto erro

echo [3/5] Instalando os pacotes do OPUSCORE ...
"%PY%" -m pip install --disable-pip-version-check -e packages/core -e packages/connectors -e "packages/ef[imagens,pdf]" -e packages/orchestrator -e packages/web -e packages/platform -e consultores/dev-abap -e consultores/funcional-mm -e consultores/arquiteto -e consultores/funcional-sd -e consultores/integracao -e consultores/lider-tecnico -e consultores/qualidade || goto erro

if /i "%~1"=="--motores" (
  echo [4/5] Instalando as bibliotecas dos motores - pode demorar ...
  "%PY%" -m pip install --disable-pip-version-check -e "consultores/dev-abap[motores]" || goto erro
) else (
  echo [4/5] Motores ignorados - use --motores para Gerar ET e Remediar
)
"%PY%" -m pip install --disable-pip-version-check pytest import-linter || goto erro

echo [5/5] Criando config\config.yaml e config\.env, se ainda nao existirem ...
if not exist config\config.yaml copy config\config.example.yaml config\config.yaml >nul
if not exist config\.env copy config\.env.example config\.env >nul

"%PY%" -c "import opuscore_platform, opuscore_connectors, opuscore_ef; print('Pacotes OK')" || goto erro
echo.
echo Pronto. Ative o ambiente com:  %VENV%\Scripts\activate.bat
echo Edite config\config.yaml e config\.env e rode:  opuscore-servidor
exit /b 0

:erro
echo.
echo [ERRO] A instalacao parou. Veja a mensagem acima ou rode de novo salvando o log:
echo        scripts\instalar.bat ^> instalacao.log 2^>^&1
exit /b 1