* Pré Requisitos

Pelo Portal Empresa ca Capgemini

* Instalar Eclipse e Plugin ABAP Ultima Versão
* Python 3.13 ou superior
* Node.js
* Configurar Variáveis de Ambiente Python

*** Para configurar o Python nas variáveis de ambiente do Windows, adicione o seguinte caminho na variável Path:

***Encontre onde esta intalado o Python no seu notebook , ex

Mostrar mais linhas e adicione

C:\Python313\Scripts

C:\Python313\

Adicione tambpem em  Configurações Avançadas do Sistema → Variáveis de Ambiente → selecione a variável Path → Editar → Novo e informe:

C:\Python313\Scripts

C:\Python313\

* Usar essa API colaborativa  nas variáveis de ambiente, no arquivo .env do projeto ( já configuradas )
  
* Instalar a  Python no VSCode  e Configurar ambiente

<https://code.visualstudio.com/docs/python/environments>

* no Terminal ( Se ocorrer erro é porque não tem env criado pode seguir)

Remove-Item -Recurse -Force venv

python -m venv capremedaicode

.\capremedaicode\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

pasta "input" colocar de forma resumida o requisito funcional em .txt

pasta "output" vai gerar a saida dos códigos

execute: python run_pipeline.py

* caso ocorre erro do module python-dotenv==1.2.2,

execute pip install python-dotenv

* toda vez que for usar a Ferris AI, vc deve entrar no ambiente novamente execute

.\capremedaicode\Scripts\Activate.ps1





# ==============================================================================
# Capgemini SAP AI Remediation Engine — Environment Configuration
# ------------------------------------------------------------------------------
# Variáveis de Ambiente
# NUNCA comite o .env real no repositório (adicione ao .gitignore).
# =============================================================================


# -----------------------------------------------------------------------------
# [OBRIGATÓRIAS] — o engine não sobe sem estas
# -----------------------------------------------------------------------------

# Chave de API para autenticação no gateway LLM
LLM_API_KEY=coloque-no-.env-nunca-no-README

# ID do workspace no gateway Capgemini
WORKSPACE_ID=seu-workspace-id

# Optional. Only needed if you use the native Anthropic client (langchain_anthropic).
# Not required for the default Generative Engine path.
ANTHROPIC_API_KEY=

LLM_PROVIDER=capgemini

# -----------------------------------------------------------------------------
# [LLM — URLs e Modelos]
# -----------------------------------------------------------------------------

# URL base do gateway OpenAI-compatible
LLM_BASE_URL=https://openai.generative.engine.capgemini.com/v1

# Modelo principal: usado para análise de código (chamada mais cara)
LLM_MODEL_MAIN=us.anthropic.claude-sonnet-4-20250514-v1:0

# Modelo de triage: deve ser rápido e barato (haiku, flash, etc.)
LLM_MODEL_TRIAGE=anthropic.claude-haiku-4-5-20251001-v1:0

# [NOVO] Modelo para o naming pass (default = LLM_MODEL_MAIN se não definido)
# Use um modelo mais barato aqui para reduzir custo, ex: o mesmo haiku do triage
LLM_MODEL_NAMING=anthropic.claude-haiku-4-5-20251001-v1:0

# Máximo de tokens na resposta do LLM principal
LLM_MAX_TOKENS=20192


# -----------------------------------------------------------------------------
# [Diretórios]
# -----------------------------------------------------------------------------

# Pasta onde ficam os arquivos SAP de entrada (.abap, .prog, .clas, etc.)
REMEDIATION_INPUT_DIR=input

# Pasta onde os arquivos remediados serão gravados
REMEDIATION_OUTPUT_DIR=output


# -----------------------------------------------------------------------------
# [SAP / ATC]
# -----------------------------------------------------------------------------

# Versão alvo do S/4HANA (aparece nos comentários do arquivo de saída)
SAP_TARGET_VERSION=SAP S/4HANA 2025 (Private Edition)

# Variante de verificação ATC usada como referência
ATC_CHECK_VARIANT=ZS4HANA_LEROY_CHECK

# Pacote SAP global (development class). Pode ser vazio;
# um sidecar .pkg por arquivo tem precedência sobre este valor.
SAP_PACKAGE=ZDEV


# -----------------------------------------------------------------------------
# [Chunking & Triage]
# -----------------------------------------------------------------------------

# Modo de chunking: auto | on | off
# auto = usa chunk apenas se o fonte > REMEDIATION_WHOLE_LIMIT
REMEDIATION_CHUNKING=auto

# Tamanho máximo (chars) para enviar o fonte inteiro sem chunking (modo auto)
REMEDIATION_WHOLE_LIMIT=12000

# Tamanho máximo de cada chunk (chars) quando o chunking está ativo
REMEDIATION_CHUNK_CHARS=6000

# Habilita o passo de triage (usa LLM_MODEL_TRIAGE para decidir se analisa)
ENABLE_TRIAGE=true

# Quantas ocorrências de uma mesma âncora podem ser marcadas por flag/warning.
# Evita que âncoras genéricas (ex: "ENDIF.") spamem o arquivo inteiro.
REMEDIATION_MAX_MARK_OCCURRENCES=10


# -----------------------------------------------------------------------------
# [Naming Check]
# -----------------------------------------------------------------------------

# Habilita a auditoria de nomes de identificadores
ENABLE_NAMING_CHECK=true

# Nome exato do workbook de naming no knowledge-base RAG
NAMING_WORKBOOK_NAME=Workbook_ABAP_Move2S4_Final.docx

# [NOVO] Tamanho máximo do fonte enviado ao naming pass (chars).
# Fontes maiores são truncados com aviso, evitando overflow de contexto do LLM.
NAMING_SOURCE_CHAR_LIMIT=40000


# -----------------------------------------------------------------------------
# [NOVO: Paralelismo, Retry e Resiliência]
# -----------------------------------------------------------------------------

# Número de arquivos processados em paralelo (threads).
# Recomendado: 2 a 8 dependendo dos limites de rate do seu gateway.
REMEDIATION_MAX_WORKERS=4

# Número de tentativas por chamada LLM antes de desistir (inclui a primeira)
REMEDIATION_RETRY_ATTEMPTS=4

# Timeout em segundos por chamada ao LLM
REMEDIATION_CALL_TIMEOUT_S=120

# Se true, arquivos cujo output já existe na pasta de saída são ignorados.
# Útil para reprocessar lotes interrompidos sem retrabalho.
REMEDIATION_SKIP_EXISTING=false


# -----------------------------------------------------------------------------
# [RAG Documents] — lista separada por vírgula dos documentos no knowledge-base
# Altere somente se o nome dos documentos no workspace for diferente.
# -----------------------------------------------------------------------------
RAG_DOCUMENTS=Abap RAP.pdf,CONV_OP2025.pdf,Clean core extensibility for SAP S_4HANA Cloud.pdf,CustomCodeMigration_EndToEnd.pdf,Extend SAP S_4HANA in the cloud and on premise with ABAP based extensions.pdf,From Classic ABAP to ABAP.pdf,LEROY_EXP_ARQ_Plano de migração ECC-EWM x S4HANA_260513_v1.pptx,SIMPL_OP2023-V1.pdf,Workbook ABAP_Move2S4_Final.docx
