# Arquitetura em pacotes

```
Web (shell + design system)        → as telas vêm de cada consultor
Plataforma (gateway)               → rotas, banco, artefatos, uploads, registro de plugins, ctx
Consultores (um pacote cada)       → Dev ABAP, Funcional MM, SD, Arquiteto, Integração, Líder, QA
Orquestrador | Leitura de EF       → handoffs e eventos | biblioteca compartilhada de EF
Conectores (servidor MCP)          → SAP ADT hoje; CPI, Jira depois
Core (contratos e SDK)             → base de todos
```

## Regras (verificadas no CI pelo `lint-imports`)

1. Um consultor **nunca importa outro**. A conversa entre eles passa pelo Orquestrador,
   por eventos com esquema versionado no Core (`ef.validada` v1, `et.gerada` v1...).
2. Consultores falam com a infraestrutura **só pelo `ctx`** (MCP, IA, artefatos, uploads,
   eventos, auditoria): não importam Plataforma, Conectores nem Orquestrador.
3. **Acesso a sistemas externos só pelos Conectores** (MCP). Leitura de dados de negócio é
   bloqueada pela classe de entrega; escrita não existe sem o guard (nega por padrão).
4. O **Core não depende de ninguém**; o pacote **EF é biblioteca** (sem rota, banco ou tela).
5. CSS de consultor começa sempre com `.c-<key>`; cores e componentes só no design system.

## Contratos e versões

- Pacotes: versionamento semântico. Contratos: número inteiro próprio
  (`contrato_plugin`, `contrato_web`, cada tipo de evento).
- Campo opcional novo: mesma versão. Mudar ou remover: versão nova, e as duas convivem.
- Mudança no Core passa pelo líder técnico e por um dono de pacote consumidor (CODEOWNERS).

## Donos (10 pessoas)

| # | Pacote | Responsabilidade |
|---|---|---|
| 1 | Core | Líder técnico: contratos, SDK, regras de dependência, revisão |
| 2 | Conectores | SAP ADT, segurança e auditoria; próximos sistemas |
| 3 | Plataforma | Gateway, registro, banco, login, artefatos |
| 4 | Orquestrador | Eventos, handoffs, fluxos e gates |
| 5 | Web | Shell, design system, SDK das telas |
| 6 | EF | Leitura, validação e geração de EF |
| 7 | Dev ABAP | Análise de objeto, Gerar ET, motor de ET |
| 8 | Dev ABAP | Remediação, motor de remediação |
| 9 | Funcional MM | Analisar, Gerar EF, Validar EF, Regras |
| 10 | Funcional SD e novos | SD, depois Arquitetos e QA |

## Fluxo entre consultores (primeiro handoff real)

MM valida a EF → **Enviar para o desenvolvimento** publica `ef.validada` → o Orquestrador
grava o evento (outbox), cria o handoff para o Dev e entrega ao tratador dele (com novas
tentativas e fila de falhas) → o Dev aceita na aba **Handoffs** e usa a mesma EF na
Remediação ou na ET.
