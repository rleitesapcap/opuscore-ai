# OPUSCORE-AI — Como instalar e executar

Este guia cobre: instalar o monorepo, configurar, executar tudo, executar cada pacote
separadamente, rodar os testes, migrar os dados da versão anterior e criar um consultor ou
conector novo.

---

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
