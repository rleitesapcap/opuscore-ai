# OPUSCORE-AI — Squad de especialistas SAP com conectividade real

Acelerador para desenvolvedores e consultores SAP. Um "squad" de agentes
especialistas (ABAP, Integração, Arquitetura de Processos, SD, MM, FI/CO, TM,
Testes…) que **não respondem de memória**: eles leem o sistema SAP do cliente
via ADT REST API, coletam evidência real e o LLM apenas narra sobre ela.

## Por que é diferente do que existe

1. **Grounded, não alucinado.** Padrão *Evidence Ledger*: todo fato do relatório
   carrega o endpoint ADT que o produziu. O LLM é proibido de inventar.
2. **O "Cérebro" é vivo.** O mapa mental (estilo Obsidian) não é decoração — os
   nós e arestas são as dependências reais do sistema (where-used do ADT).
3. **LLM plugável.** Claude, Grok ou sua AIP/Ollama local: troca no `config.yaml`.
4. **Local-first.** Roda na sua máquina; credenciais SAP nunca saem dela.
5. **Clean Core embutido.** Cada análise traz um veredito de conformidade.

## Decisão de arquitetura: ADT REST API (não RFC)

A SAP **arquivou o PyRFC e depreciou o SAP NW RFC SDK em mai/2026**. Para um
produto novo isso é dívida técnica garantida. A ADT REST API é o mesmo HTTP que
o Eclipse ADT usa: source de qualquer objeto, DDIC, ATC, ABAP Unit e where-used
via GET/POST previsíveis, sem SDK nativo. OData entra depois para dados de
negócio; um adaptador RFC legado fica como opção, ciente da depreciação.

## Segurança (travas inegociáveis)

A ferramenta **não altera nem exclui** objetos no SAP/BTP.

1. **Somente-leitura por padrão** (`read_only: true` por conexão). Nesse modo,
   qualquer tentativa de mutação levanta `MutationBlocked` **antes** de qualquer
   chamada ao sistema — e é registrada em auditoria.
2. **Aprovação humana obrigatória.** Só alcançável se você desligar o read-only.
   Na CLI, pede confirmação explícita (digitar `SIM`).
3. **Request de transporte obrigatória.** Sem TR informada, a operação é bloqueada.
4. **Trilha de auditoria append-only** em `audit/opuscore-audit.jsonl` (JSON Lines):
   toda solicitação, bloqueio, negação e aprovação, com data/hora, objeto, sistema,
   aprovador e transporte.

Prova rápida da trava (não toca o SAP): `python -m opuscore.cli test-guard MARA delete`.

## Estrutura

```
backend/
  config.example.yaml     # LLM + conexões SAP (copie p/ config.yaml)
  .env.example            # segredos (copie p/ .env)
  opuscore/
    settings.py           # carga de config + env
    llm.py                # Claude nativo + OpenAI-compat (Grok/AIP/Ollama)
    sap/adt_client.py     # cliente ADT REST (o núcleo, somente-leitura)
    sap/analyzer.py       # relatório de objeto + grafo do Cérebro
    safety.py             # guardrails: read-only + aprovação + auditoria
    mcp_server.py         # opuscore-sap-mcp — capacidades SAP como ferramentas MCP
    mcp_client.py         # host: sobe o MCP por stdio e chama ferramentas
    host.py               # laço do agente (LLM <-> ferramentas MCP) + narração
    llm.py                # LLM plugável com tool calling (Claude / OpenAI-compat)
    agents.py             # Desenvolvedor ABAP (caminho direto, usado pela CLI)
    api.py                # HOST: /health, /abap/report, /chat + serve o frontend
    cli.py                # testes rápidos

## Arquitetura (Etapa 1: host + MCP)

O domínio SAP virou um **MCP server** (`opuscore-sap-mcp`) com os guardrails dentro —
o ponto único onde a trava read-only e a auditoria valem para qualquer host. O backend
é o **host**: recebe o chat, o LLM decide, chama ferramentas MCP (somente leitura),
recebe a evidência e responde. O mesmo MCP pode ser consumido depois pelo Hermes/voz.

```

## Rodando

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # WSL2
pip install -r requirements.txt
cp config.example.yaml config.yaml   # ajuste host/mandante do cliente
cp .env.example .env                 # coloque as chaves e a senha SAP

python -m opuscore.cli health                 # testa a conexão ADT
python -m opuscore.cli report ZTMTB_PESAGEM   # 1º relatório (com grafo)
python -m opuscore.api                        # sobe a API em :8787
```

## Roadmap imediato (enriquecer)

- [ ] Frontend Next.js consumindo `/abap/report` e renderizando o Cérebro ao vivo
- [ ] Agentes 1.6 (Integração/CPI) e 1.7 (Arquiteto de Processos)
- [ ] Cache/persistência do grafo (SQLite) + busca por embeddings
- [ ] ATC + ABAP Unit como ferramentas do agente
- [ ] Skills por cliente (formato de EF, naming, pacotes) como no OrkestraFlow

## Desenvolvedor em ação (Fase 1)

O agente Desenvolvedor já produz entregáveis. Pela CLI (uso imediato, sem UI):

```bash
python -m opuscore.cli report ZCL_X          # relatório do objeto (source/DDIC + where-used)
python -m opuscore.cli remediate ZCL_X       # análise + rubrica Clean Core + plano de remediação
python -m opuscore.cli tech-spec ef.md       # gera ET a partir de uma EF (só precisa de LLM)
python -m opuscore.cli rap ef.md             # esqueleto RAP Clean Core (rascunho p/ revisar)
```

Pela API (mesmas capacidades, para a UI consumir): `POST /api/dev/object-report`,
`/api/dev/remediation`, `/api/dev/tech-spec`, `/api/dev/rap` — cada uma grava um
**Artifact** (listável em `/api/projects/{id}/artifacts`).

Regra inegociável: tudo é **artefato para revisão**. `report`/`remediate` leem o SAP via
ADT (somente leitura); `tech-spec`/`rap` só usam o LLM. Nada é escrito no SAP — gerar
código local para você revisar e transportar é permitido; alterar o sistema não é.

Cadastro (admin): `POST /api/users`, `/api/agents` (perfil = prompt versionado),
`/api/agents/{id}/skills`, `/api/agents/{id}/collections`, `/api/projects`,
`/api/projects/{id}/collections|agents|members|connections`.

Ver `ARCHITECTURE.md` para o caminho de evolução para a nuvem (control plane + runner).
