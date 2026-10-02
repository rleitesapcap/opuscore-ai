# 📝 Feedback da EF SD-034 — o que falta e o que dá pra melhorar

E aí! Passei a EF **ef_sd034.docx** (versão V2) pelo raio-x. Aqui vai o resumo sem enrolação, com onde está cada ponto e como resolver.

## 🟡 Resumo rápido

Dá pra seguir, mas tem uns pontos que valem ajuste pra ninguém travar lá na frente.

- **4 coisas** faltando
- **9 sugestões** de melhoria
- **0 pontos** que a IA achou sensível e precisa da sua confirmação

## ❌ O que está faltando

### 1. A seção de **TVARV, BRF+ e tabelas de parâmetros** só tem o texto de orientação do template

- **Onde:** TVARV, BRF+ e Tabelas de Parâmetros
- **Por que importa:** o dev precisa saber o que é parametrizável e quem mantém, senão vira hardcode
- **Como resolver:** Liste cada parâmetro: nome, tipo (TVARV, BRF+, tabela, app), valores e quem dá manutenção. Pelo que a EF descreve, a ZTMMC_STAT_PRECO parece ser uma tabela de parâmetros.

### 2. Faltam os nomes de quem homologa (4 papéis sem ninguém)

- **Onde:** seção “Homologação”, na tabela de responsáveis
- **Por que importa:** sem responsável definido, a aprovação trava no final
- **Como resolver:** Coloque o nome de cada responsável: Líder de Desenvolvimento (Capgemini); Analista Funcional – TI (Leroy Merlin); Usuário-chave (Leroy Merlin); Líder de Macroprocesso (Leroy Merlin).

### 3. A versão do arquivo não bate com o histórico de revisão

- **Onde:** tabela de histórico de revisão, no começo do documento
- **Por que importa:** quem ler não sabe se está com a versão certa
- **Como resolver:** Versão informada (V2) difere da última versão do histórico de revisão (V1). Adicione a linha da nova versão no histórico.

### 4. O esboço “Esboço da aba “Dados Bloqueio de Preço “no S4:” mostra o campo “Usuário Liberado Cálculo 2” (TEXTO), que não aparece na lista de campos do texto.

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Esboço da aba “Dados Bloqueio de Preço “no S4:…”
- **Por que importa:** o campo aparece só no esboço; se ninguém escrever, o dev pode deixar passar
- **Como resolver:** Confirme se o campo existe mesmo. Se existir, inclua na lista de campos do texto (com o nome técnico, se já tiver). Se foi engano no esboço, é só avisar.

## ✏️ O que dá pra melhorar

### 1. A palavra **“simplificada”** aparece 6 vezes

- **Onde:** seção “Objetivo, justificativa e processo de negócio atendido.”, no trecho que começa com “Adicionalmente, deverá ser disponibilizada uma aplicação Fio…”; seção “Premissas/Acordos do GAP”, no trecho que começa com “Os parâmetros relacionados às funcionalidades contempladas n…” (e mais 4 lugares)
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** simplificada em relação a quê? Diga o que sai e o que fica. Exemplo na EF: “…cionalmente, deverá ser disponibilizada uma aplicação Fiori simplificada para administração dos parâmetros de controle atualmente ma…”

### 2. A palavra **“aplicável(is)”** aparece 8 vezes

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Utilizada para transferir informações do esquema de compras …”; seção “Regras de Negócio”, no trecho que começa com “ZCLSD_EXIT_SAPLWVK1_003, no método USER_EXIT_OLD_CODE, chama…” (e mais 6 lugares)
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** quais, exatamente? Liste os itens em vez de deixar o dev adivinhar. Exemplo na EF: “…a exclusão de itens da lista e as validações de calendário aplicáveis ao processo.…”

### 3. A palavra **“quando necessário”** aparece 1 vez

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Como parte da conversão para o SAP S/4HANA, os objetos relac…”
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** necessário quando? Descreva a condição que dispara. Exemplo na EF: “…etos relacionados a esse processo deverão ser analisados e, quando necessário, ajustados para garantir a continuidade das funcionalidades…”

### 4. A palavra **“algumas funcionalidades”** aparece 1 vez

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Atualmente no ECC a validação das datas de precificação é co…”
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** quais? Uma lista resolve. Exemplo na EF: “…para SAP S/4HANA, preservando o comportamento funcional de algumas funcionalidades utilizadas pelo negócio.…”

### 5. A palavra **“etc. / entre outros”** aparece 1 vez

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “A determinação das datas permitidas e não permitidas para pr…”
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** o 'etc.' vira escopo infinito. Feche a lista. Exemplo na EF: “…feriados cadastrados no calendário utilizado pelo negócio, etc. Funcionalidade ja existe no ECC:…”

### 6. A palavra **“os demais”** aparece 3 vezes

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “ZFMM_CHECK_CONDITION_DATE, considerando as funcionalidades a…”; seção “Regras de Negócio”, no trecho que começa com “Para este gap, deverão ser consideradas exclusivamente a val…” (e mais 1 lugar)
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** 'os demais' quais? Vale nomear, nem que seja numa lista curta. Exemplo na EF: “…ente correlacionadas ao monitor do ECC ZRMM_RECALC_PR_BLOQ. Os demais controles existentes na implementação não fazem parte do es…”

### 7. 3 objetos técnicos citados sem dizer se entra ou não no escopo

- **Onde:** SCFD_REGISTRY; ZRMM_CADASTRO_PRECO_ADMINISTR; ZTMMC_STAT_PRECO (campos IDENT, ZHORALT, ZUSERLB1, ZVDT_VDT, ZVD_HORA)
- **Por que importa:** o dev não sabe se precisa mexer neles ou só consultar
- **Como resolver:** Pra cada um, diga: remediar, só consultar, ou fora do escopo.

### 8. 2 componentes sem deixar claro se é novo, remediação ou evolução

- **Onde:** Será desenvolvida uma aplicação Fiori simplificada…; EXIT_SAPLWVK1_003
- **Por que importa:** isso muda o nível de Clean Core exigido e o jeito de desenvolver
- **Como resolver:** Marque a natureza de cada objeto (Novo / Remediação / Evolução).

### 9. A EF prevê uso de ponto de ampliação implícito

- **Onde:** seção “Enhancements – Objeto Standard SAP com ponto de ampliação implícito”, no trecho que começa com “Include WV001F01, form / AT-SELECTION-SCREEN Include standar…”
- **Por que importa:** enhancement implícito é o nível mais baixo de Clean Core (nível D)
- **Como resolver:** Não é você quem decide a técnica, relaxa: só registre se já foi avaliada alternativa (BAdI liberada, por exemplo). O Líder Técnico vai bater o martelo.

## 📸 A gente leu os esboços pra você

Em vez de pedir pra você descrever cada tela, a IA leu as imagens. **Só confere se está certo**: se algum campo estiver errado ou faltando, ajusta na EF.

### img02 — Esboço da aba “Dados Bloqueio de Preço “no S4:

_Tela simples: liga/desliga as travas de calendário e horário e define até dois usuários liberados._

**Abas:** Dados de Bloqueio de Preço, Regras de Aprovação de Custos, Cadastro de Aprovadores Principal, Cadastro de Aprovadores Substituto (aberta: Dados de Bloqueio de Preço)

| Campo | Tipo | Exemplo na tela |
|---|---|---|
| Ativa - Verificação Calendário Preço | CHECKBOX | X |
| Calendário Cálculo Preço - LMB | TEXTO | LM |
| Ativa - Verificação Horário | CHECKBOX | X |
| Horário Limite para Precificação | HORA | 23:00:00 |
| Usuário Liberado Cálculo 1 | TEXTO | [mascarado] |
| Usuário Liberado Cálculo 2 | TEXTO | [mascarado] |

🔒 Valores de identificação de pessoas foram escondidos (Usuário Liberado Cálculo 1, Usuário Liberado Cálculo 2).

### img03 — Esboço da aba “Regras de Aprovação de Custos” no S4:

_Tela de cadastro._

| Campo | Tipo | Exemplo na tela |
|---|---|---|
| Aprovador | TEXTO |  |

**Botões:** Salvar

### img04 — Esboço da aba “Cadastro de Aprovadores Principal” no S4:

_Tela de cadastro._

| Campo | Tipo | Exemplo na tela |
|---|---|---|
| Aprovador | TEXTO |  |

**Botões:** Salvar

### img05 — Esboço da aba “Cadastro de Aprovadores Subistituto” no S4:

_Tela de cadastro._

| Campo | Tipo | Exemplo na tela |
|---|---|---|
| Aprovador | TEXTO |  |

**Botões:** Salvar

### img10 — Esboço no S4:

_Tela de cadastro._

| Campo | Tipo | Exemplo na tela |
|---|---|---|
| Aprovador | TEXTO |  |

**Botões:** Salvar

## ✅ O que já está bom

Nem tudo é crítica, tá? Isso aqui ficou bem feito:

- Você deixou claro o que **fica de fora** (17 pontos). Isso economiza muito retrabalho.
- Os objetos técnicos estão **nomeados** (22 referências). O dev já sabe por onde começar.
- Tem **roteiro de teste** (12 passos) e 6 resultados esperados.
- **16 regras de negócio** bem identificadas.
- Os campos da tabela de parâmetros estão **mapeados** (15 campos).
- As **dependências com outros GAPs** estão citadas: MM-054-FIO.

## 📋 Checklist pra próxima versão

- [ ] A seção de TVARV, BRF+ e tabelas de parâmetros só tem o texto de orientação do template
- [ ] Faltam os nomes de quem homologa (4 papéis sem ninguém)
- [ ] A versão do arquivo não bate com o histórico de revisão
- [ ] O esboço “Esboço da aba “Dados Bloqueio de Preço “no S4:” mostra o campo “Usuário Liberado Cálculo 2” (TEXTO), que não aparece na lista de campos do texto.
- [ ] A palavra “simplificada” aparece 6 vezes
- [ ] A palavra “aplicável(is)” aparece 8 vezes
- [ ] A palavra “quando necessário” aparece 1 vez
- [ ] A palavra “algumas funcionalidades” aparece 1 vez
- [ ] A palavra “etc. / entre outros” aparece 1 vez
- [ ] A palavra “os demais” aparece 3 vezes
- [ ] 3 objetos técnicos citados sem dizer se entra ou não no escopo
- [ ] 2 componentes sem deixar claro se é novo, remediação ou evolução
- [ ] A EF prevê uso de ponto de ampliação implícito
- [ ] Conferir a leitura dos 5 esboços de tela
- [ ] Atualizar o histórico de revisão com a nova versão

---

_Esse feedback foi gerado automaticamente a partir da própria EF. Os trechos citados são o começo de cada parágrafo: é só copiar e buscar com Ctrl+F no Word. Ficou alguma dúvida? Chama o time técnico._
