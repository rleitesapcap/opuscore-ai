# ARCHITECTURE — Caminho para a nuvem (web-exposed)

Nota de decisão. **Nada aqui é para construir agora** — serve para não arquitetarmos
contra o futuro. Hoje o OPUSCORE-AI roda local (um usuário, na máquina do operador,
dentro da rede onde o SAP é alcançável). Amanhã pode ir para um servidor exposto na
web. A stack atual (FastAPI + SQLModel + fronteira MCP) suporta essa evolução de forma
**aditiva** — não há reescrita. Django não mudaria isso; os mesmos pontos valeriam lá.

## Portas já deixadas abertas (não mexer)
- Acesso a banco via **SQLModel/SQLAlchemy** → portável de SQLite para PostgreSQL trocando a URL + migrações.
- **Autorização em código no choke point** (camada host/MCP), nunca no prompt.
- **Fronteira MCP** para o domínio SAP → pode virar o "runner" (ver abaixo).
- **`User` / `Membership` / escopos** já modelados → base para multiusuário/multi-tenant.
- **Read-only por padrão + auditoria append-only**.

## Marcos quando for para a web (em ordem de importância)

### 1. Padrão control plane + runner (o mais importante e o mais valioso)
Um servidor público **não enxerga o S/4 on-prem** do cliente (fica atrás de firewall/VPN)
e não deve guardar credenciais SAP de vários clientes exposto na internet. Solução
comprovada: um **runner leve** dentro da rede do cliente (ou na máquina dele) segura a
conexão SAP e fala **de dentro para fora** com o control plane hospedado — nenhuma porta
de entrada aberta no firewall, credenciais nunca saem da rede do cliente. É o mesmo
princípio do **SAP Cloud Connector** (túnel TLS de saída) e do runner que o OrkestraFlow
mostrava. O trabalho local-first que já fizemos praticamente **é** esse runner. Preserva
o diferencial: local, grounded, read-only, credencial que não sai da rede do cliente.

### 2. Autenticação e multi-tenancy
Login real (sessão/JWT/OAuth), cadeia `usuário ≤ conexão ≤ agente` aplicada por
requisição e por usuário, e **isolamento de dados entre organizações** (o isolamento de
RAG vira requisito de segurança quando tenants dividem o mesmo servidor).

### 3. Banco → PostgreSQL
Concorrência, conexões, backup e `pgvector` para o RAG. Migração quase só troca a string
de conexão + Alembic (por isso escolhemos SQLModel).

### 4. Segredos
Cofre local → **secrets manager** de verdade (Vault / KMS da nuvem, ou no mínimo cifrado
em repouso), isolado por cliente/projeto.

### 5. Execução assíncrona pesada
Ingestão de RAG e análises longas saem da requisição para uma **fila** (arq/Celery/RQ).
MCP hoje sobe por stdio no processo; em servidor multiusuário, MCP como **serviço de longa
duração (HTTP/SSE)** e/ou runners isolados por tenant.

### 6. Operação
TLS/HTTPS, reverse proxy (Caddy/nginx), **Docker**, config 12-factor por variável de
ambiente, backups, observabilidade central, health checks, rate limiting, CI/CD. A trilha
de auditoria já existente entra nesse conjunto.

## Decisão de produto que dita a arquitetura do "dia da nuvem"
**SaaS multi-tenant** (você hospeda, muitos clientes no mesmo servidor) **vs. self-hosted /
runner por cliente**. Para consultoria SAP, segurança e residência de dado quase sempre
empurram para o **modelo runner** — que é o que preserva o diferencial e reaproveita o que
já construímos.

## Regra de decisão
Não migrar nada agora. Seguir colhendo valor (o agente Desenvolvedor). Os únicos itens
caros de retrofitar se ignorados — **auth/multi-tenancy** e o **runner** — já estão
acomodados no desenho atual.
