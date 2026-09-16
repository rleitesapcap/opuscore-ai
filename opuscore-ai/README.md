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
    sap/adt_client.py     # cliente ADT REST (o núcleo)
    sap/analyzer.py       # relatório de objeto + grafo do Cérebro
    agents.py             # BaseAgent (Evidence Ledger) + Desenvolvedor ABAP
    api.py                # FastAPI local
    cli.py                # testes rápidos
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
