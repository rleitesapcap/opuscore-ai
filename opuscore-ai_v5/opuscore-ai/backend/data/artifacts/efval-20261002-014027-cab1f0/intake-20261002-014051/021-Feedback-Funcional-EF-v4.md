# 📝 Feedback da EF 021 — o que falta e o que dá pra melhorar

E aí! Passei a EF **LEROY_REL_FI-021_Template Especifica_o Funcional_RemSimp_23092026_V04.docx** (versão V4) pelo raio-x. Aqui vai o resumo sem enrolação, com onde está cada ponto e como resolver.

## 🟡 Resumo rápido

Dá pra seguir, mas tem uns pontos que valem ajuste pra ninguém travar lá na frente.

- **2 coisas** faltando
- **7 sugestões** de melhoria
- **0 pontos** que a IA achou sensível e precisa da sua confirmação

## ❌ O que está faltando

### 1. Não há detalhamento sobre o comportamento quando a POSTING_INTERFACE_CLEARING falha parcialmente (ex.: compensa parte da fatura). Fica apena…

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Os erros dos processos deverão ser gravados em log e monitor…”
- **Por que importa:** a IA não achou essa informação na EF
- **Como resolver:** Complete esse ponto na seção indicada.

### 2. Não há especificação sobre cenários de reprocessamento: se uma nota fiscal retorna status 100 após ter sido rejeitada, ou se passa de status…

- **Onde:** seção “Fluxo do Processo do GAP”, no trecho que começa com “Quando o status da nota fiscal for igual a 100, é acionada a…”
- **Por que importa:** a IA não achou essa informação na EF
- **Como resolver:** Complete esse ponto na seção indicada.

## ✏️ O que dá pra melhorar

### 1. Ficou ambíguo: Momento exato de disparo da BAdI e sequência de execução dos function modules não está claro quanto ao tratamento de transações SAP (commit/…

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Após o faturamento e a autorização da nota fiscal na Sefaz, …”
- **Por que importa:** cada pessoa pode entender de um jeito
- **Como resolver:** Reescreva deixando uma interpretação só. Trecho: “Após o faturamento e a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100, a lógica vin…”

### 2. Ficou ambíguo: Condição de validação do status 100 aparece duplicada em contextos ligeiramente diferentes: uma refere-se à Sefaz e autorização, outra apena…

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “A compensação da fatura do cliente e a criação da nota de cr…”
- **Por que importa:** cada pessoa pode entender de um jeito
- **Como resolver:** Reescreva deixando uma interpretação só. Trecho: “A compensação da fatura do cliente e a criação da nota de crédito no fornecedor dependerão da autorização da nota fiscal…”

### 3. Ficou ambíguo: A regra menciona que a conta transitória deve apresentar saldo zerado após compensação e nota de crédito, mas não especifica se isso é uma v…

- **Onde:** seção “Regras de Negócio”, no trecho que começa com “Após a compensação da fatura do cliente e a contabilização d…”
- **Por que importa:** cada pessoa pode entender de um jeito
- **Como resolver:** Reescreva deixando uma interpretação só. Trecho: “Após a compensação da fatura do cliente e a contabilização da nota de crédito no fornecedor seller, a conta transitória …”

### 4. A palavra **“aplicável(is)”** aparece 1 vez

- **Onde:** seção “Enhancements”, no trecho que começa com “Validação na SCFD_REGISTRY, quando aplicável NA…”
- **Por que importa:** é palavra que abre margem pra interpretação
- **Como resolver:** quais, exatamente? Liste os itens em vez de deixar o dev adivinhar. Exemplo na EF: “…Validação na SCFD_REGISTRY, quando aplicável | NA…”

### 5. 14 objetos técnicos citados sem dizer se entra ou não no escopo

- **Onde:** CL_NFE_PRINT; NSACAO_RXC; POSTING_INTERFACE_CLEARING; POSTING_INTERFACE_END; POSTING_INTERFACE_START; SCFD_REGISTRY; ZFSD_CONSULTA_CLIENTE; ZFSD_CRIAR_IDOC_CLIENTE …
- **Por que importa:** o dev não sabe se precisa mexer neles ou só consultar
- **Como resolver:** Pra cada um, diga: remediar, só consultar, ou fora do escopo.

### 6. 1 componente sem deixar claro se é novo, remediação ou evolução

- **Onde:** BAdI CL_NFE_PRINT
- **Por que importa:** isso muda o nível de Clean Core exigido e o jeito de desenvolver
- **Como resolver:** Marque a natureza de cada objeto (Novo / Remediação / Evolução).

### 7. A EF prevê uso de ponto de ampliação implícito

- **Onde:** seção “Enhancements – Objeto Standard SAP com ponto de ampliação implícito”, no trecho que começa com “/ VF01 / BADI/enhance ment Acionar a lógica vinculada à CL_N…”
- **Por que importa:** enhancement implícito é o nível mais baixo de Clean Core (nível D)
- **Como resolver:** Não é você quem decide a técnica, relaxa: só registre se já foi avaliada alternativa (BAdI liberada, por exemplo). O Líder Técnico vai bater o martelo.

## ✅ O que já está bom

Nem tudo é crítica, tá? Isso aqui ficou bem feito:

- Você deixou claro o que **fica de fora** (2 pontos). Isso economiza muito retrabalho.
- Os objetos técnicos estão **nomeados** (18 referências). O dev já sabe por onde começar.
- Tem **roteiro de teste** (13 passos) e 6 resultados esperados.
- **3 regras de negócio** bem identificadas.
- As **dependências com outros GAPs** estão citadas: FI-021, FI-021-ENH.

## 📋 Checklist pra próxima versão

- [ ] Não há detalhamento sobre o comportamento quando a POSTING_INTERFACE_CLEARING falha parcialmente (ex.: compensa parte da fatura). Fica apena…
- [ ] Não há especificação sobre cenários de reprocessamento: se uma nota fiscal retorna status 100 após ter sido rejeitada, ou se passa de status…
- [ ] Ficou ambíguo: Momento exato de disparo da BAdI e sequência de execução dos function modules não está claro quanto ao tratamento de transações SAP (commit/…
- [ ] Ficou ambíguo: Condição de validação do status 100 aparece duplicada em contextos ligeiramente diferentes: uma refere-se à Sefaz e autorização, outra apena…
- [ ] Ficou ambíguo: A regra menciona que a conta transitória deve apresentar saldo zerado após compensação e nota de crédito, mas não especifica se isso é uma v…
- [ ] A palavra “aplicável(is)” aparece 1 vez
- [ ] 14 objetos técnicos citados sem dizer se entra ou não no escopo
- [ ] 1 componente sem deixar claro se é novo, remediação ou evolução
- [ ] A EF prevê uso de ponto de ampliação implícito
- [ ] Atualizar o histórico de revisão com a nova versão

---

_Esse feedback foi gerado automaticamente a partir da própria EF. Os trechos citados são o começo de cada parágrafo: é só copiar e buscar com Ctrl+F no Word. Ficou alguma dúvida? Chama o time técnico._
