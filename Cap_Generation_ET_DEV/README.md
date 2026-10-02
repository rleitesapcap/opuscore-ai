# Geração da Especificação Técnica (ET) — MOVE2S/4

Ferramenta que lê a **Especificação Funcional (EF)** e os **códigos ABAP/RAP** (novos ou remediados) e gera a **Especificação Técnica** no template oficial Word (`.docx`).

A **raiz do projeto** é a pasta deste `README.md` (onde estão `extract.py`, `.env` e os scripts).  
`input/` **não** é a raiz: é só a pasta de **entrada**.

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

LLM_API_KEY=qc7YGbzeN46StHsEwsHmFUEH8sDj6Vjv8O27RX60

WORKSPACE_ID=88a0e054-690f-4855-a23c-e10303e978cb

* Instalar a  Python no VSCode  e Configurar ambiente

<https://code.visualstudio.com/docs/python/environments>

* no Terminal ( Se ocorrer erro é porque não tem env criado pode seguir)

Remove-Item -Recurse -Force venv

python -m venv capgenerateet

.\capgenerateet\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

pasta "input" colocar de forma resumida o requisito funcional em .txt

pasta "output" vai gerar a saida dos códigos

* caso ocorre erro do module python-dotenv==1.2.2,

execute pip install python-dotenv

* toda vez que for usar a Ferris AI, vc deve entrar no ambiente novamente execute

.\capgenerateet\Scripts\Activate.ps1

* Processos para execução
  
```
python extract.py              # Etapa 1 — extração mecânica (sem LLM)
python generate_docs.py        # Etapa 2 — análise de código → *_DOC.md (LLM)
python lc_CapETGenerator.py    # Etapa 3 — preenche o template .docx
```

Pipeline das três etapas de uma vez (quando o arquivo existir nesta pasta):

```
python run_et_pipeline.py                                           # Execução completa com a IA
python run_et_pipeline.py --dry-run                                 # Execução sem  IA
python run_et_pipeline.py --only ZRSD_SIMULADOR_PRECO_IMP           # Execução de um determinado código
python run_et_pipeline.py --start-at 3                              # Execução de uma determinada etapa
```
---

## 1. O que entra e o que sai

| | Pasta | Quem grava | Quem lê |
| --- | -------- | ------------ | --------- |
| **INBOUND** | `input/` | você | Etapas 1–2 |
| **OUTBOUND** | `output/` | os scripts | você (ET, artefatos, review) |
| **Template da ET** | pasta do `.env` `DIR_TEMPLATE_LOCAL` | você (uma vez) | Etapa 3 (e a Etapa 1 só registra o nome) |

O `.env` fica **na raiz deste projeto**, nunca dentro de `input/`.

```
<raiz deste projeto>/               ← extract.py, .env, scripts
├── .env
├── rap/   ou  rag/                 ← template oficial da ET (.docx)
├── input/                      ← INBOUND (você coloca EF + códigos)
│   ├── Functional-Specification
        ├── Adicionar a EF e arquivo para extrair do cabeçalho da EF
    ├── Generated-Code
        ├── Adicionar todos os códigos    
└── output/                      ← OUTBOUND (os scripts geram)
    ├── 01_ET_GERADA/
    │   ├── artefatos/              ← *_DOC.md, _payload.json, …
    │   └── ET_<GAP>_<data>.docx
```

Nomes das pastas vêm do `.env` (`ET_INBOUND_DIR`, `DIR_EF`, `DIR_CODIGOS`, `ET_OUTBOUND_DIR`, …). Os valores abaixo são o **padrão**.

---

## 2. INBOUND — onde colocar a EF e os códigos

Coloque os arquivos **direto** em `input/`. **Não** crie pasta `GAP-xxx` no caminho: o ID do GAP é um **campo da EF**, não o nome de uma pasta.

### 2.1 Especificação Funcional

```
input/Functional-Specification/
├── EF_<modulo>-<id>_....docx     ← a EF do GAP (obrigatória)
└── regras_extrair.md             ← rótulos a extrair do cabeçalho da EF
```

- Aceita `.docx` (preferencial), `.pdf`, `.md` ou `.txt`.
- O extrator ignora arquivos de template (`*template*`) e locks do Word (`~$*`).
- `regras_extrair.md` lista os campos do cabeçalho (Autor, Módulo, ID GAP, Descrição GAP, …). Sem esse arquivo, o cabeçalho da ET fica incompleto.

### 2.2 Códigos novos ou remediados

```
input/             ← varredura RECURSIVA
├── cds_interface_views/*.asddls
├── cds_consumption_views/*.asddls
├── behavior_definitions/*.bdef
├── reports/*.abap
└── includes/*.abap
```

**Objeto novo** vs **remediação** (automático):

- **Remediação** — o arquivo traz o cabeçalho `Capgemini AI Remediation Code - Brazil` nas primeiras linhas (código já passado pelo motor de remediação, com `BEGIN/END OF MODIFICATION`).
- **Objeto novo** — qualquer outro fonte na pasta.

Extensões lidas: `.abap`, `.clas.abap`, `.asddls`, `.ddls`, `.bdef`, `.dcl`, `.srvd`, `.ddlx`, `.txt`, `.prog`, entre outras do ADT.

Não coloque a saída da ET nem o Code Review dentro de `et_source/`.

---

## 3. Template da ET (Word oficial)

O `.docx` da ET (cabeçalho Leroy/Capgemini, tabelas e marcadores `{{IA_...}}`) **não** vai em `et_source/`. Vai na pasta de template, na **raiz do projeto**.


.ENV

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
LLM_API_KEY=qc7YGbzeN46StHsEwsHmFUEH8sDj6Vjv8O27RX60

# ID do workspace no gateway Capgemini
WORKSPACE_ID=88a0e054-690f-4855-a23c-e10303e978cb

# Optional. Only needed if you use the native Anthropic client (langchain_anthropic).
# Not required for the default Generative Engine path.
ANTHROPIC_API_KEY=

LLM_PROVIDER=capgemini
ET_DRY_RUN=0

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

# --- FUNIL / DESEMPENHO ------------------------------------------------------
ENABLE_TRIAGE=false
REVIEW_MAX_WORKERS=4
REVIEW_RETRY_ATTEMPTS=4
REVIEW_CALL_TIMEOUT_S=120
# Fonte <= WHOLE_LIMIT chars => analisada inteira; acima disso => cortada em chunks.
REVIEW_WHOLE_LIMIT=12000
REVIEW_CHUNK_CHARS=6000


# -----------------------------------------------------------------------------
# [RAG Documents] — lista separada por vírgula dos documentos no knowledge-base
# Altere somente se o nome dos documentos no workspace for diferente.
# -----------------------------------------------------------------------------
RAG_DOCUMENTS=Abap RAP.pdf,CONV_OP2025.pdf,Clean core extensibility for SAP S_4HANA Cloud.pdf,CustomCodeMigration_EndToEnd.pdf,Extend SAP S_4HANA in the cloud and on premise with ABAP based extensions.pdf,From Classic ABAP to ABAP.pdf,LEROY_EXP_ARQ_Plano de migração ECC-EWM x S4HANA_260513_v1.pptx,SIMPL_OP2023-V1.pdf,Workbook ABAP_Move2S4_Final.docx

CAPGEMINI_WORKSPACE_ID=88a0e054-690f-4855-a23c-e10303e978cb

# ---- Workbook de nomenclatura (RAG) — usado no modo CONSTRUÇÃO -------
# A IA consulta este documento para nomear os objetos propostos no padrão do
# projeto. Mantenha o nome IDÊNTICO ao arquivo do workspace RAG.
NAMING_WORKBOOK_NAME=Workbook ABAP_Move2S4_Final_v2.docx

# ---- Diretórios: INBOUND (de onde pegar as EFs) e OUTBOUND (onde gravar as ETs)
# Dentro do INBOUND, um diretório por GAP (ex.: GAP-MM-174-REP), cada um com as
# subpastas "EF/" (a Especificação Funcional) e "Codigos/" (os fontes).
ET_INBOUND_DIR=input
ET_OUTBOUND_DIR=output

# ---- Template da ET (o arquivo .docx REAL, com cabeçalho e imagens) ----
# Fica no "diretório rag" do projeto. O preenchimento troca os marcadores
# {{IA_...}} mantendo o cabeçalho/logos. Enquanto o template não está no
# workspace, apontamos para a pasta local.
ET_TEMPLATE_DIR=rag
ET_TEMPLATE_NAME=LEROY_REL_INCLUIR MÓDULO_IDGAP_Template Especificação Técnica_DDMMAA_V02.docx
DIR_TEMPLATE_LOCAL=rag


# ---- Modelos (funil de economia de token) ---------------------------
ET_MODEL_ANALYZE=anthropic.claude-haiku-4-5-20251001-v1:0
ET_MODEL_SYNTH=us.anthropic.claude-sonnet-4-20250514-v1:0


DOC_MAX_UNIT_CHARS=6000

DIR_EF=Functional-Specification
DIR_CODIGOS=Codigos
DIR_CODE_REVIEW=02_CODE_REVIEW
DIR_ET_GERADA=01_ET_GERADA
DIR_ARTEFATOS=artefatos
FILE_REGRAS=regras_extrair.md
FILE_REQUISITOS=requisitos_extraidos.md
FILE_ACHADOS=achados_tecnicos.md
FILE_PENDENCIAS=pendencias_review.md
FILE_RESULTADO=resultado_final.md
ET_TEMPLATE_NAME=LEROY_REL_INCLUIR MÓDULO_IDGAP_Template Especificação Técnica_DDMMAA_V02.docx

# Valores fixos da Etapa 3 (ET):
ET_FIXED_AUTOR=Capgemini AI Generate ET - Brazil
ET_FIXED_ANALISTA=Capgemini IA Generativa
ET_FIXED_VERSAO=1.0
