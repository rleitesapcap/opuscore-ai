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
