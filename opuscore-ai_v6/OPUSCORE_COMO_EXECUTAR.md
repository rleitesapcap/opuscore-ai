# OPUSCORE-AI — Como instalar e executar

Este guia cobre: instalar o monorepo, configurar, executar tudo, executar cada pacote
separadamente, rodar os testes, migrar os dados da versão anterior e criar um consultor ou
conector novo.

---
d
## 1. O que é cada pasta

```
opuscore/
├── packages/
│   ├── core/            opuscore_core          contratos, SDK (IA, custo, MCP, config), regras de Clean Core
│   ├── connectors/      opuscore_connectors    servidor MCP: SAP ADT (somente leitura), segurança, auditoria
│   ├── ef/              opuscore_ef            biblioteca: ler, validar e gerar Especificações Funcionais
│   ├── orchestrator/    opuscore_orchestrator  eventos, handoffs, fila de falhas (e o consultor Orquestrador)
│   ├── platform/        opuscore_platform      host: gateway, registro de plugins, ctx, banco, artefatos, uploads
│   └── web/             opuscore_web           shell da tela, design system e SDK das telas (JS puro, sem build)
├── consultores/
│   ├── dev-abap/        opuscore_dev           Analisar objeto, Gerar ET, Remediar, Handoffs (+ motores)
│   ├── funcional-mm/    opuscore_mm            Analisar configuração, Gerar EF, Validar EF, Regras por seção
│   ├── funcional-sd/    opuscore_sd            (conversa; capacidades próprias a evoluir)
│   ├── arquiteto/       opuscore_arquiteto     (idem)
│   ├── integracao/      opuscore_integracao    (idem)
│   ├── lider-tecnico/   opuscore_lider         (idem)
│   └── qualidade/       opuscore_qualidade     (idem)
├── config/              config.example.yaml, .env.example, templates/EF_template.docx
├── tests/integracao/    teste ponta a ponta com todos os pacotes
├── scripts/instalar.sh
├── .importlinter        regras de dependência entre pacotes (verificadas no CI)
└── .github/             CODEOWNERS (dono de cada pasta) e workflow de CI
```

Cada pasta de `packages/` e `consultores/` é um **pacote Python independente**, com
`pyproject.toml`, testes e dono próprios.

---

## 2. Pré-requisitos

- Python 3.11 ou mais novo (testado com 3.12).
- No WSL/Linux: `python3-venv` instalado (`sudo apt install python3-venv`).
- Para usar o SAP: o sistema acessível pelo ADT (no seu caso, o container `a4h`:
  `docker start a4h` e aguardar "All services have been started" em `docker logs -f a4h`).
- Opcional: Node.js 20 (só para rodar a checagem das telas localmente) e o `uv`, se
  preferir o workspace dele ao script.

---

## 3. Instalação

### 3.1 Tudo de uma vez (recomendado)

```bash
cd opuscore
bash scripts/instalar.sh              # cria .venv e instala os 13 pacotes em modo editável
source .venv/bin/activate
```

Para rodar **Gerar ET** e **Remediar** (motores do Dev, que usam LangChain e outras
bibliotecas pesadas):

```bash
bash scripts/instalar.sh --motores
```

O script também cria `config/config.yaml` e `config/.env` a partir dos exemplos, se ainda
não existirem.

### 3.2 Com o uv (alternativa)

```bash
cd opuscore
uv sync                               # usa o workspace definido no pyproject.toml raiz
source .venv/bin/activate
```

### 3.3 Só o que uma pessoa da equipe precisa

Quem trabalha num pacote instala o Core, o que esse pacote usa e a Plataforma (para ver a
tela). Exemplo para quem trabalha no **Consultor MM**:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e packages/core -e "packages/ef[imagens,pdf]" -e packages/orchestrator -e packages/web \
            -e packages/connectors -e packages/platform -e consultores/funcional-mm pytest
```

Quem trabalha **só no pacote EF** (biblioteca) nem precisa da Plataforma:

```bash
pip install -e packages/core -e "packages/ef[imagens,pdf]" pytest
```

---

## 4. Configuração

### 4.1 `config/config.yaml`

Seções:

| Seção | Para quê | Lido por |
|---|---|---|
| `app` | host e porta do servidor (padrão `127.0.0.1:8787`) | Plataforma |
| `llm` | provedores de IA do chat (Anthropic, xAI, Ollama...) | Core (SDK de IA) |
| `sap` | sistemas SAP (`base_url`, `client`, `read_only: true`) e o padrão | Conectores |
| `safety` | caminho da auditoria (`data/audit/...`) | Conectores |
| `conectores` | conectores ativos e tabelas de configuração permitidas sem classe de entrega | Conectores |

Para o seu trial local, a seção `sap` fica assim:

```yaml
sap:
  default: a4h
  systems:
    a4h:
      base_url: "http://localhost:50000"
      client: "001"
      auth: basic
      user: "${SAP_USER}"
      password: "${SAP_PASSWORD}"
      verify_ssl: false
      read_only: true
```

`${VAR}` é substituído pelo valor da variável de ambiente (vinda do `config/.env`).

### 4.2 `config/.env`

O `config/.env.example` lista **todas** as variáveis, separadas por bloco. As essenciais:

```
SAP_USER=DEVELOPER
SAP_PASSWORD=...
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL_MAIN=claude-opus-5-5
LLM_TEMPERATURE=off                      # obrigatória com o claude-opus-5-5
EF_INTAKE_MODEL=claude-haiku-4-5-20251001
EF_INTAKE_MAX_TOKENS=32000
```

A remediação usa **só** a Generative Engine da Capgemini: `LLM_API_KEY` e `WORKSPACE_ID`.

Variáveis da plataforma (todas opcionais): `OPUSCORE_HOME` (raiz do projeto),
`OPUSCORE_DATA` (pasta de dados), `OPUSCORE_CONFIG`, `OPUSCORE_DB` ou `OPUSCORE_DB_URL`,
`OPUSCORE_PLUGINS` (quais consultores sobem), `OPUSCORE_CONECTORES` e `EF_TEMPLATE`.

**Não** coloque no `.env` as variáveis de pasta dos motores (`DIR_*`, `ET_OUTBOUND_DIR`,
`FILE_*`, `REMEDIATION_INPUT_DIR`, `REMEDIATION_OUTPUT_DIR`) nem `LLM_USAGE_LOG`: a
plataforma define todas a cada execução.

### 4.3 Template de EF do projeto

O **Gerar EF** usa `config/templates/EF_template.docx` (o template da Leroy já está lá).
Para outro cliente, troque o arquivo ou aponte `EF_TEMPLATE` para outro caminho.

### 4.4 Onde ficam os dados

Tudo em `data/` (ou em `OPUSCORE_DATA`):

```
data/
├── opuscore.db                 banco (projetos, consultores, conversas, artefatos, eventos, handoffs)
├── uploads/<id>/               documentos enviados (EF, Workshop B), já validados
├── artifacts/<projeto>/<id>/   arquivos de cada artefato (ET, relatórios, rascunhos)
├── cache/                      cache da IA (Etapa 1, revisão por seção)
├── consultores/funcional-mm/   regras por seção editadas em cada projeto (com histórico)
└── audit/                      auditoria (leituras de configuração, ações dos consultores)
```

---

## 5. Executar tudo

```bash
source .venv/bin/activate
opuscore-servidor                       # ou: python -m opuscore_platform
# porta/host diferentes:
opuscore-servidor --porta 8787 --host 127.0.0.1
```

Abra `http://127.0.0.1:8787`. O servidor:

1. cria ou atualiza o banco e aplica as migrações de cada pacote;
2. cria o projeto de demonstração, se o banco estiver vazio;
3. descobre os consultores instalados e sincroniza os perfis;
4. sobe o servidor MCP dos Conectores como subprocesso;
5. inicia o Orquestrador (entrega de eventos em segundo plano);
6. monta as rotas de cada consultor em `/api/c/<key>` e as telas em `/c/<key>/`.

**Conferências rápidas:**

| Endereço | O que mostra |
|---|---|
| `/api/plataforma/plugins` | Consultores carregados e os que deram erro (com o motivo) |
| `/health` | Conexão com o SAP: 200 conectado; 502 o SAP recusou ou não respondeu; 503 o servidor MCP não subiu |
| `/docs` | Todas as rotas da API (Swagger) |

---

## 6. Executar cada pacote separadamente

### 6.1 Um consultor sozinho (com a infraestrutura real)

```bash
opuscore-dev --plugins funcional-mm --porta 8801             # só o MM
opuscore-dev --plugins dev-abap --porta 8802                 # só o Dev
opuscore-dev --plugins orquestrador --porta 8803             # só o Orquestrador
opuscore-dev --plugins funcional-mm,orquestrador --porta 8804  # mais de um
opuscore-dev --plugins funcional-mm --porta 8801 --sem-mcp     # sem SAP (tela e IA)
opuscore-dev --plugins funcional-mm --porta 8801 --reload      # recarrega ao salvar
```

Sobe o gateway completo (banco, artefatos, uploads, shell da tela) só com os consultores
pedidos. As rotas e telas dos outros respondem 404, e eles não aparecem na lista.

O mesmo filtro funciona no servidor completo por variável:

```bash
OPUSCORE_PLUGINS=funcional-mm,dev-abap opuscore-servidor
```

**Sugestão de portas por pessoa:** MM 8801, Dev 8802, Orquestrador 8803, SD 8805.
Use **pastas de dados separadas** se mais de uma pessoa rodar na mesma máquina:
`OPUSCORE_DATA=data-mm opuscore-dev --plugins funcional-mm --porta 8801`.

### 6.2 Conectores (servidor MCP) sozinho

```bash
opuscore-conectores                                   # servidor MCP por stdio
python -m opuscore_connectors.cli health              # testa a conexão ADT
python -m opuscore_connectors.cli ferramentas         # lista as ferramentas e o nível de acesso
python -m opuscore_connectors.cli relatorio ZSDR_FOB_ENQUEUE_REQUEST
python -m opuscore_connectors.cli test-guard --object-name MARA   # prova a trava de escrita
npx @modelcontextprotocol/inspector python -m opuscore_connectors.servidor   # chamar ferramentas à mão
```

### 6.3 Pacote EF (sem servidor)

```bash
python -m opuscore_ef.cli "LEROY_REL_SD-034.docx" --estado APROVADA --sem-ia   # custo zero
python -m opuscore_ef.cli "LEROY_REL_SD-034.docx" --estado APROVADA            # com IA
python -m opuscore_ef.cli "EF.docx" --imagens todas
```

Ou em Python:

```python
import opuscore_ef as ef
r = ef.analisar("EF.docx", estado="RASCUNHO", usar_ia=False)
no_escopo, fora = ef.objetos_tecnicos("EF.docx")
```

### 6.4 Motores do Dev (para depuração)

Os motores continuam rodando sozinhos pelos scripts deles, como antes:

```bash
cd consultores/dev-abap/opuscore_dev/motores/et
python run_et_pipeline.py --root <pasta com 01_EF e 02_CODIGOS> --output <saída>/01_ET_GERADA
```

---

## 7. Fluxo ponta a ponta (manual)

1. Suba o servidor completo e abra a tela.
2. **Consultores → Consultor Funcional MM → Abrir → Validar EF**: envie a EF e valide.
3. Se a EF não estiver inválida, clique em **Enviar para o desenvolvimento**. Isso publica
   o evento `ef.validada`.
4. **Orquestrador → Abrir**: o GAP aparece com o evento e o handoff do MM para o Dev.
5. **Desenvolvedor ABAP → Abrir → Handoffs**: aceite o handoff e clique em
   **Usar na Remediação** ou **Usar na ET**. A EF já vem carregada, sem novo upload.

---

## 8. Testes

```bash
pytest                                  # todos (41 testes)
pytest packages/core                    # um pacote
pytest consultores/funcional-mm
pytest tests/integracao                 # ponta a ponta com todos os pacotes
EF_SD034="caminho/da/SD-034.docx" pytest packages/ef   # inclui o teste de referência com a EF real
lint-imports --config .importlinter     # regras de dependência entre pacotes
```

Checagem das telas (precisa de Node):

```bash
ARQS=$(ls packages/web/opuscore_web/static/shell/*.js packages/web/opuscore_web/static/sdk/*.js \
          consultores/*/opuscore_*/web/main.js packages/orchestrator/opuscore_orchestrator/web/main.js)
for f in $ARQS; do node --check "$f"; done
npx --yes eslint@8 --no-eslintrc --env browser,es2022 --parser-options=sourceType:module,ecmaVersion:2022 \
  --rule 'no-undef: error' $ARQS
```

O CI (`.github/workflows/ci.yml`) roda tudo isso em cada push e pull request.

---

## 9. Migrar da versão anterior (`opuscore-ai/backend`)

O banco é compatível (as tabelas antigas foram mantidas; as novas são criadas sozinhas).
Para continuar com os mesmos projetos, conversas e artefatos:

```bash
cp -r ~/Projeto-OPUSCORE-AI/.../opuscore-ai/backend/data ./data
cp ~/Projeto-OPUSCORE-AI/.../opuscore-ai/backend/.env config/.env
cp ~/Projeto-OPUSCORE-AI/.../opuscore-ai/backend/config.yaml config/config.yaml
```

Depois, no `config/config.yaml`, ajuste `safety.audit_log_path` para `data/audit/...` e
acrescente a seção `conectores` (veja o `config.example.yaml`).

- Os artefatos antigos continuam baixáveis (a Plataforma reconhece as pastas da versão anterior).
- As regras por seção editadas na versão anterior ficavam num arquivo único; agora são por
  projeto. Reaplique as edições na aba **Regras por seção** do MM.
- Os endereços da API mudaram: `/api/...` virou `/api/plataforma/...` (serviços centrais) e
  `/api/c/<key>/...` (consultores). Os do Dev eram `/api/dev/...` e os do MM, `/api/funcional/...`.

---

## 10. Criar um consultor novo

1. Copie a pasta de um consultor simples (por exemplo, `consultores/funcional-sd`) com outro nome.
2. No `pyproject.toml`: troque o `name` e o entry point:
   ```toml
   [project.entry-points."opuscore.consultores"]
   funcional-fi = "opuscore_fi.plugin:PLUGIN"
   ```
3. No `plugin.py`: manifesto (key, nome, área), persona e skills. Para ter tela e rotas:
   ```python
   manifesto = Manifesto(key="funcional-fi", nome="Consultor Funcional FI", area="Funcional",
                         web=WebManifesto(rota="fi", css="fi.css"), assina={"ef.validada": "ao_receber"})
   def rotas(self, obter_ctx): ...          # cada rota recebe ctx = Depends(obter_ctx)
   @property
   def web_dir(self): return Path(__file__).parent / "web"
   ```
4. A tela é um `web/main.js` com `export async function mount(area, ctx)` e
   `export function unmount()`. Tudo vem do `ctx` (`ctx.ui`, `ctx.projeto`, `ctx.apiBase`);
   a tela não importa nada. O CSS fica em `web/fi.css`, com toda regra começando por `.c-funcional-fi`.
5. Acrescente o pacote ao `scripts/instalar.sh`, ao `pyproject.toml` raiz, ao `.importlinter`
   (contrato de independência) e ao `CODEOWNERS`.
6. `pip install -e consultores/funcional-fi` e reinicie: ele aparece na lista.

## 11. Adicionar um conector novo

Siga o padrão de `packages/connectors/opuscore_connectors/sap_adt/`: um subpacote com
`cliente.py` e `ferramentas.py`; cada ferramenta com `@ferramenta(sistema="...", nivel="...")`
(sem nível declarado, o teste do pacote falha); a configuração numa seção própria do
`config.yaml`, com segredos via `.env`; registro em `CONECTORES` no `servidor.py`; e ativação
por `conectores.habilitados` ou `OPUSCORE_CONECTORES`.

---

## 12. Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Consultor não aparece na lista | Veja `/api/plataforma/plugins`: mostra se ele foi carregado ou o erro. Confira se o pacote está instalado (`pip list \| grep opuscore`). |
| `/health` responde 503 | O servidor MCP não subiu. Confira o `config.yaml` (seção `sap`) e o log do início. |
| `/health` responde 502 | O MCP subiu, mas o SAP recusou ou não respondeu. Confira se o `a4h` está no ar e o `base_url`. |
| "Template de EF não encontrado" | Coloque o template em `config/templates/EF_template.docx` ou defina `EF_TEMPLATE`. |
| Erro de `temperature` com o Opus 5.5 | `LLM_TEMPERATURE=off` no `config/.env`. |
| Remediação recusa rodar | Faltam `LLM_API_KEY` e `WORKSPACE_ID` da Generative Engine. |
| Tela de um consultor não abre | A mensagem aparece só na área dele; o resto segue funcionando. Veja o console do navegador (F12). |
| `scripts/instalar.sh: Permission denied` | Rode com `bash scripts/instalar.sh`. |

---

## 13. Pendências conhecidas (honestidade sobre o estado atual)

- **Etapa 2 do Dev** (descoberta técnica no SAP a partir do handoff) ainda não existe: o
  handoff chega, e a EF pode ser usada na Remediação e na ET sem novo upload.
- **Fluxos declarados em YAML** e **gates com aprovação por papel** ainda não foram feitos. O
  roteamento atual é uma tabela no Orquestrador (`ef.validada` abre um handoff para o Dev).
- A Etapa 1 ainda lê internamente as variáveis `EF_INTAKE_*` e `LLM_PROVIDER`; o objetivo é
  receber tudo por parâmetro.
- Os motores do Dev mantêm os seus próprios `llm_providers.py`; a camada de adaptação faz a ponte.
- As regras por seção do MM ficam em arquivo JSON por projeto (com histórico), não em tabela.
- O mapa do template (preencher o próprio template campo a campo) aguarda o seu template e o
  exemplo de Workshop B.
- As telas foram verificadas por sintaxe, ESLint (sem identificadores indefinidos), testes de
  estrutura e respostas HTTP reais, mas não foram clicadas num navegador durante a migração.
- O projeto fixa `mcp<2`; a migração para a versão 2 do SDK do MCP é tarefa planejada.
- As migrações de banco usam um mecanismo próprio e simples (versionado por pacote), no lugar
  do Alembic previsto no desenho; dá para trocar depois sem impacto nos consultores.





























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
ANTHROPIC_API_KEY=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

LLM_PROVIDER=anthropic
ET_DRY_RUN=0
PROMPT_CACHE=on

# -----------------------------------------------------------------------------
# [LLM — URLs e Modelos]
# -----------------------------------------------------------------------------

# URL base do gateway OpenAI-compatible
LLM_BASE_URL=https://openai.generative.engine.capgemini.com/v1

# Modelo principal: usado para análise de código (chamada mais cara)
LLM_MODEL_MAIN=claude-opus-5-5
LLM_MODEL=claude-opus-5-5
EF_INTAKE_MODEL=claude-haiku-4-5-20251001

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
ENABLE_TRIAGE=false

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

# Valores fixos da Etapa 3 (ET):
ET_FIXED_AUTOR=Capgemini AI Generate ET - Brazil
ET_FIXED_ANALISTA=Capgemini IA Generativa
ET_FIXED_VERSAO=1.0


# ==============================================================================
# Credenciais do SAP do cliente (ficam SÓ na sua máquina)
SAP_USER=DEVELOPER
SAP_PASSWORD=ABAPtr2025#SP00



































# ---------------------------------------------------------------------------
# OPUSCORE-AI — configuração central
# Copie para config.yaml e ajuste. Segredos (chaves de API, senha SAP) devem
# ir no .env, nunca aqui. Os valores ${VAR} são lidos do ambiente.
# ---------------------------------------------------------------------------

app:
  name: "OPUSCORE-AI"
  language: "pt-BR"          # idioma padrão das respostas dos agentes
  host: "127.0.0.1"
  port: 8787

# --- Camada de LLM (100% plugável: Claude, Grok, AIP local / Ollama) --------
llm:
  default: "claude"          # qual provider usar por padrão

  providers:
    claude:
      kind: "anthropic"      # API nativa da Anthropic (Messages API)
      base_url: "https://api.anthropic.com"
      model: "claude-sonnet-4-5"   # ajuste ao modelo que você tem acesso
      api_key: "${ANTHROPIC_API_KEY}"
      max_tokens: 4096
      temperature: 0.2

    grok:
      kind: "openai_compatible"    # xAI expõe API compatível com OpenAI
      base_url: "https://api.x.ai/v1"
      model: "grok-2-latest"
      api_key: "${XAI_API_KEY}"
      max_tokens: 4096
      temperature: 0.2

    aip:                     # sua plataforma corporativa (AIP / Ollama local)
      kind: "openai_compatible"
      base_url: "http://localhost:11434/v1"   # Ollama fala OpenAI-compat
      model: "qwen2.5-coder:14b"
      api_key: "ollama"      # Ollama ignora, mas o campo é exigido
      max_tokens: 4096
      temperature: 0.2

# --- Conexões SAP (uma por cliente/ambiente) --------------------------------
# A conectividade é via ADT REST API (o mesmo HTTP que o Eclipse ADT usa).
# Nada de SAP NW RFC SDK: a SAP arquivou o PyRFC em mai/2026.
sap:
  default: "cliente_dev"

  systems:
    cliente_dev:
      base_url: "http://localhost:50000"  # host:port HTTPS do ICM
      client: "001"          # mandante
      auth: "basic"          # basic | bearer
      user: "${SAP_USER}"
      password: "${SAP_PASSWORD}"
      verify_ssl: false      # true em produção (com CA confiável)
      read_only: true        # TRAVA: nunca altera/exclui. Não mexa sem necessidade.
      # allowed_packages evita que o agente vasculhe fora do escopo do cliente:
      allowed_packages: ["ZINNOVE", "Z*", "Y*", "$TMP"]

# --- Segurança / auditoria ---------------------------------------------------
safety:
  audit_log_path: "audit/opuscore-audit.jsonl"  # trilha append-only (JSON Lines)
  require_transport: true                         # sem request informada -> bloqueia
