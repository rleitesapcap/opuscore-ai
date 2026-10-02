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

## 🔎 Revisão seção por seção

Cada seção foi conferida com as regras específicas dela. Olha o placar:

| Seção | Situação | Resumo |
|---|---|---|
| Identificação (capa) | ✅ tá ok | Capa preenchida corretamente com todos os campos obrigatórios. Histórico de revisão bem documentado. |
| Resumo do Desenvolvimento | ⚠️ precisa de ajuste | Tipo de programa e prioridade marcados corretamente, mas faltam evidências de pesquisa de alternativa standard e a volumetria de migração não está preenchida. |
| Objetivo, justificativa e processo atendido | ✅ tá ok | Seção clara: problema, objetivo e benefício bem descritos. Critério de sucesso implícito (eliminação da ZAP0069) é verificável. |
| Processos relacionados | ⚠️ precisa de ajuste | Processos listados, mas faltam papéis de usuário, transações S/4HANA standard e clareza sobre BAdI/APIs como novos desenvolvimentos vs. standard. |
| Regras de negócio | ⚠️ precisa de ajuste | Regras têm condições, ações e exceções, mas estão misturadas em parágrafos longos. Falta estruturação em formato RN-nn e algumas regras carecem de detalhe de tr… |
| Premissas, escopo e dependências | ✅ tá ok | Premissas, escopo incluído e fora de escopo bem definidos, sem contradições. Periodicidade de invoices e condições de execução claras. |
| Fluxo do processo | ⚠️ precisa de ajuste | Fluxo em texto passo a passo, mas faltam quem executa cada passo (usuário, sistema ou job) e pontos de decisão não estão explícitos. |
| Sistemas e objetos impactados | ❌ falta o essencial | Sistemas listados mas faltam tipos (S/4HANA, externo, BTP), papéis e mapeamento de integração. Bloco de interfaces do Resumo não está preenchido. |
| Novos objetos / campos | ⚠️ precisa de ajuste | Novos objetos listados mas faltam detalhes de campo: tipo, tamanho, tela, obrigatoriedade, F4 e validação. Verificação SCFD_REGISTRY não foi feita. |
| Enhancements | ⚠️ precisa de ajuste | BAdI identificada (CL_NFE_PRINT), mas sem detalhe de implementação. Function modules listados mas não fica claro se são standard SAP ou custom. Verificação SCFD… |
| Aplicativo Fiori | ❌ falta o essencial | Seção descreve eliminação de transação (ZAP0069), não um novo app Fiori. Estrutura inadequada para a regra de validação. |
| Interfaces de entrada / conversões | ❌ falta o essencial | Não achei essa seção na EF, e o tipo de desenvolvimento marcado no Resumo pede essa seção. |
| Interfaces de saída | ❌ falta o essencial | Não achei essa seção na EF, e o tipo de desenvolvimento marcado no Resumo pede essa seção. |
| Procedimento de testes | ⚠️ precisa de ajuste | Cenários de teste cobrem fluxo principal e exceção (status ≠ 100), mas faltam cenários específicos para erros de integração, reprocessamento e validações de con… |
| Resultados esperados | ⚠️ precisa de ajuste | Resultados esperados são descritivos mas alguns são vagos (ex.: 'funcionar corretamente', 'conforme fluxo'). Faltam valores esperados e mensagens de sistema. |
| Informações complementares | ✅ tá ok | Seção preenchida com periodicidade, tipo de execução, volumetria, tratamento de erros e criticidade bem definidos. |
| Homologação | ✅ tá ok | Todos os papéis de homologação têm pessoas nomeadas, sem lacunas. |

### ⚠️ Resumo do Desenvolvimento

_Onde: Resumo do Desenvolvimento_

**1. Falta:** Campo 'Número de registros' para migração de dados está vazio. A EF menciona que é uma interface, mas não deixa claro se há volume de migração associado.
- Trecho: “[T1.r7] 4-Número de registros | registros” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Preencha o número de registros migrados ou deixe claro se não há migração: '[T1.r7] 4-Número de registros | 0 (sem migração de dados históricos)' ou com o volume real se aplicável.

**2. Dá pra melhorar:** O campo 'Existe alternativa no S4HANA?' está marcado como 'Não', mas a seção 'Razão pela qual esta alternativa não é aceitável' está vazia. A EF menciona alternativa standard (contabilização na visão cliente), mas não explica por que não é aceitável.
- Trecho: “[T2.r0] / Razão pela qual esta alternativa não é aceitável:” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Preencha com: 'A alternativa standard SAP realiza contabilização apenas na visão cliente, sem geração automática de contabilização em conta de fornecedor. O novo fluxo exige a criação de nota de crédito no fornecedor e compensação contra conta transitória, razão pela qual a solução Z é necessária.'

### ⚠️ Processos relacionados

_Onde: Processos Relacionados (Transações do Sistema S4HANA)_

**1. Falta:** Faltam papéis de usuário (usuários que executam cada processo) e transações S/4HANA standard associadas aos processos.
- Trecho: “[P028] até [P046]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Para cada processo, adicione: papel (ex.: 'Analista FI', 'Gerente de Faturamento'), transação (ex.: 'VF01 - Criar Fatura') e se é standard ou custom. Exemplo: 'VF01 - Papel: Analista de Faturamento SD - transação standard S/4HANA'.

**2. Ficou ambíguo:** As APIs (Business Partner, Documento Contábil, Sales Order) não ficam claras se são standard SAP ou desenvolvimentos Z/RAP novos.
- Trecho: “[P034] até [P037]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Especifique: 'API Business Partner - custom criado em RAP para validação por CNPJ' ou 'API standard Sales Order - utilização de /sap/opu/odata/sap/C_SALESORDER_TP_SRV conforme best practices'.

### ⚠️ Regras de negócio

_Onde: Regras de Negócio_

**1. Dá pra melhorar:** Regras estão descritas em prosa corrida sem numeração/estrutura. Dificulta rastreabilidade e testes.
- Trecho: “[P049] até [P071]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Estruture cada regra em formato RN-nn. Exemplo: 'RN-01: Quando o tipo de operação for Boleto ou PIX, o sistema deve aplicar o novo fluxo de contabilização. Exceção: operações de cartão continuam no fluxo atual (ZAP0069).' 'RN-02: Quando o status da NF for igual a 100, o sistema deve executar sequencialmente POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END. Exceção: se status ≠ 100, não executar.'

**2. Ficou ambíguo:** Regra sobre erro de compensação não especifica o que 'registrar em log' significa: que campo? que tabela além de ZTFID_MKTPL_LG? qual mensagem de erro?
- Trecho: “[P071] Os erros dos processos deverão ser gravados em log e monitorados na tabela ZTFID_MKTPL_LG. Em caso de erro na compensação da fatura do cliente, a BAPI_ACC_DOCUMENT_POST não deverá ser executada.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Detalhe: 'Os erros deverão ser gravados em log na tabela ZTFID_MKTPL_LG com campo de status, código de erro (Z_ERROR_CODE), mensagem (Z_ERROR_MSG) e timestamp. No SLG1, registrar com nome de objeto ZRFI_MKTPL_LOG. Se erro na POSTING_INTERFACE_CLEARING, status fica em ERRO e BAPI_ACC_DOCUMENT_POST não é chamada.'

### ⚠️ Fluxo do processo

_Onde: Fluxo do Processo do GAP_

**1. Dá pra melhorar:** Fluxo não deixa claro quem executa ou dispara cada passo: é automático (job/BAdI), manual (usuário) ou automático após ação manual?
- Trecho: “[P091] até [P108]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Adicione informação de executor: '[P091] A Plataforma Marketplace (sistema externo) dispara o período de Repasse e Comissão.' '[P094] O sistema (job em background) executa VF01 para faturamento e geração da fatura no cliente.' '[P096] O sistema (BAdI CL_NFE_PRINT) valida se status da NF = 100; se SIM, prossegue; se NÃO, para.'

**2. Dá pra melhorar:** Passos P100 e P103 ('O retorno da compensação é validado', 'O saldo da conta transitória é validado') estão genéricos. Não fica claro quem valida e o que fazer se validação falhar.
- Trecho: “[P100] O retorno da compensação é validado. [P103] O saldo da conta transitória é validado após a compensação da fatura do cliente e a criação da nota de crédito no fornecedor.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Detalhe: '[P100] O sistema valida o retorno da POSTING_INTERFACE_CLEARING. Se RETORNO = SUCESSO, prossegue para P101. Se RETORNO = ERRO, registra erro em ZTFID_MKTPL_LG e para (BAPI_ACC_DOCUMENT_POST não é executada).' '[P103] O sistema valida se saldo da conta transitória = 0. Se SIM, fecha documento. Se NÃO, registra alerta em ZTFID_MKTPL_LG para investigação manual.'

### ❌ Sistemas e objetos impactados

_Onde: Sistemas, ambientes e objetos SAP impactados._

**1. Falta:** Faltam tipos de sistema (S/4HANA, legado, externo, BTP) e papéis claros no processo. Ex.: SAP CPI é BTP? Mirakl é SaaS externo?
- Trecho: “[P112] Sistemas envolvidos: Marketplace/Mirakl, Gateway KONG, SAP CPI, serviço OData criado em ABAP/RAP, SAP ECC e SAP S/4HANA.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Reformule: 'Marketplace/Mirakl (SaaS externo, dispara eventos), Gateway KONG (BTP/API Gateway, expõe APIs), SAP CPI (BTP, roteia requisições), Serviço OData ABAP/RAP (S/4HANA, consome CPI e executa lógica), SAP S/4HANA (ERP target, faturamento e compensação), SAP ECC (legado, descontinuado neste fluxo).'

**2. Falta:** A seção Resumo não tem bloco de interfaces preenchido (volumetria, direção, periodicidade), mas há interface clara com Mirakl/CPI/OData.
- Trecho: “[T1.r3] até [T1.r12]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Complete o bloco de interfaces da seção Resumo: tipo=Real-time, direção=Entrada S4HANA (Mirakl→S/4HANA), periodicidade=Quinzenal (05 e 20), registros=2.000 NFs/mês (já preenchido).

**3. Ficou ambíguo:** Não fica claro se SAP ECC é realmente impactado ou apenas mencionado historicamente.
- Trecho: “[P112] SAP ECC e SAP S/4HANA” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Se ECC não é parte do novo fluxo: 'SAP ECC (legado, descontinuado - transferência de dados para S/4HANA já realizada)'. Se ainda há integração: detalhe a interface e o mapeamento.

### ⚠️ Novos objetos / campos

_Onde: Novos Objetos_

**1. Falta:** Novo campo 'Conta transitória' não tem definição técnica: tipo, tamanho, onde é armazenado (tabela BSEG? campo custom em nova tabela?).
- Trecho: “[P129] Conta transitória nova para compensação da fatura do cliente e contabilização da nota de crédito no fornecedor.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Detalhe: 'Campo novo Z_ACCT_TRNSIT (tipo C, tamanho 10) será armazenado em BRF+ ou em tabela de configuração Z_MKTPL_CONFIG. Será consultado na POSTING_INTERFACE_CLEARING via parâmetro BAPI_ACC_DOCUMENT_POST.'

**2. Falta:** Serviço OData não tem informações técnicas: nome do serviço, entidades, campos, tipo de autenticação.
- Trecho: “[P129] Serviço OData criado em ABAP/RAP para consumo pelo SAP CPI e execução das validações e regras atuais.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Especifique: 'Serviço OData Z_MKTPL_ORDER (RAP em Clean Core), entidades C_MKTPL_ORDER e C_MKTPL_SELLER, autenticação OAuth via SAP CPI, publicado em /sap/opu/odata/sap/Z_MKTPL_ORDER.'

**3. Falta:** BRF+ para contas contábeis não tem estrutura: quais dados? regra de decisão ou tabela de decisão?
- Trecho: “[P139] BRF+ para salvar os dados das contas contábeis.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Detalhe: 'Tabela de Decisão BRF+ Z_MKTPL_ACCT_CONFIG com entradas por tipo operação (Boleto/PIX) e retorno de conta transitória (GL). Expressão: IF TipoOp IN (Boleto, PIX) THEN RetornaContaTransitoria ELSE RetornaContaClienteNormal.'

### ⚠️ Enhancements

_Onde: Enhancements, Enhancements - Implementação de Ampliações SAP (CMOD/BADI), Enhancements – Objeto Standard SAP com ponto de ampliação implícito, Enhancements – Regra de negócio_

**1. Ficou ambíguo:** BAdI CL_NFE_PRINT é ponto de extensão de qual objeto? Qual interface SAP deve ser implementada? Qual classe Z terá a lógica?
- Trecho: “[T4.r2] BAdI/lógica CL_NFE_PRINT; function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END; BAPI_ACC_DOCUMENT_POST.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Detalhe: 'Implementação da interface BAdI_PRINT_NFSE (SAP standard em SD) na classe Z_MKTPL_NFE_PRINT_IMPL. Hook chamado após VF01 com evento AFTER_POST_DOCUMENT quando NFSE_STATUS=100. Logic chama sequência: POSTING_INTERFACE_START → POSTING_INTERFACE_CLEARING → POSTING_INTERFACE_END → validação → BAPI_ACC_DOCUMENT_POST.'

**2. Dá pra melhorar:** Function modules POSTING_INTERFACE_* não estão claramente identificados como standard SAP ou custom Z. Se são custom, faltam detalhes de entrada/saída.
- Trecho: “[T4.r2] function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Esclareça: 'Function modules custom Z_POSTING_INTERFACE_START (entrada: document ID, saída: session ID), Z_POSTING_INTERFACE_CLEARING (entrada: invoice, transit account; saída: clearing ID, status), Z_POSTING_INTERFACE_END (entrada: clearing ID; saída: final status). Simulam fluxo de compensação do ECC.' Se forem adaptações de standard, cite a SAP Note.

**3. Falta:** SCFD_REGISTRY não foi consultado para validar extensibilidade da VF01 (BAdI liberada em Clean Core nível A?). Campo status da NF pode ser estendido ou é standard?
- Trecho: “[T4.r7] Validação na SCFD_REGISTRY, quando aplicável | NA” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Mude para: 'Verificado na SCFD_REGISTRY em [data]: BAdI_PRINT_NFSE liberada para Clean Core nível A em VF01. Nenhuma modificação de tabela standard necessária. Campo NFSE.STATUS é standard SAP, sem extensão.'

### ❌ Aplicativo Fiori

_Onde: Transações/Prog/Jobs/Forms/Aplicações Fiori – Transações, programas de demais objetos a serem remediados e simplificados._

**1. Falta:** A seção 'Aplicativo Fiori' deveria descrever um novo app ou modernização, mas só menciona eliminação da ZAP0069. Se há Fiori novo, está faltando. Se não há, a seção está no lugar errado.
- Trecho: “[T6.r0] até [T6.r1]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Se há novo app Fiori para monitoramento (ex.: lista de documentos MKTPL com status de compensação): descreva template (List Report + Object Page), campos (docID, status, saldo transitório, data compensação), filtros (por período, status), ações (reprocessar compensação). Se não há: mude para 'NA - Nenhum app Fiori novo. Monitoramento realizado via tabela ZTFID_MKTPL_LG e SLG1.'

### ❌ Interfaces de entrada / conversões

**1. Falta:** Seção ausente.
- Sugestão pra EF:
  > Inclua a seção “Interfaces de entrada / conversões”.

### ❌ Interfaces de saída

**1. Falta:** Seção ausente.
- Sugestão pra EF:
  > Inclua a seção “Interfaces de saída”.

### ⚠️ Procedimento de testes

_Onde: Descrição Funcional do Procedimento de Testes(obrigatório)_

**1. Falta:** Faltam testes para cenários de erro: falha no KONG, falha no SAP CPI, falha na POSTING_INTERFACE_CLEARING, falha na criação de nota de crédito.
- Trecho: “[P192] até [P202]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Adicione passos de teste: 'CT-05: Validar comportamento quando KONG retorna erro HTTP 500. Esperado: erro registrado em ZTFID_MKTPL_LG, status=ERRO_KONG, Ordem de Venda não criada. CT-06: Validar quando POSTING_INTERFACE_CLEARING falha. Esperado: erro em log, BAPI_ACC_DOCUMENT_POST não é chamada, saldo em conta transitória não zerado.'

**2. Falta:** Não há teste de reprocessamento: se erro de compensação ocorre, como o fluxo é retomado? Manual via transação? Job em background?
- Trecho: “[P192] até [P202]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Adicione: 'CT-07: Reprocessamento manual. Após correção de erro, usuário executa transação ZTFID_MKTPL_RETRY com docID e nota fiscal. Esperado: POSTING_INTERFACE_* reexecutada, nota de crédito criada, saldo zerado.'

**3. Dá pra melhorar:** Teste de saldo zerado (P202) não especifica: se não zerar, qual é a ação? Quem investigará? Há tolerância?
- Trecho: “[P202] Validar saldo zerado na conta transitória após os lançamentos a crédito e débito” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Detalhe: 'Se saldo ≠ 0 após 10 minutos da compensação, registrar alerta em ZTFID_MKTPL_LG com status=SALDO_DIFERENTE_ZERO e notificar via email para [email de operação]. Tolerância: ±0.01.'

### ⚠️ Resultados esperados

_Onde: Descrição Funcional dos Resultados Esperados Após o Teste(obrigatório)_

**1. Dá pra melhorar:** Resultado esperado P208 'conforme fluxo de integração' é vago. Não especifica valores esperados, payloads, mapeamento.
- Trecho: “[P208] A API Business Partner deve consultar e validar cliente e fornecedor por CNPJ, sem consulta por CPF, e retornar a informação de cliente ou fornecedor válido. A API Documento Contábil e a API standard Sales Order d…” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > 'A API Business Partner deve retornar JSON com campos: cliente.cnpj, cliente.valido (true/false), fornecedor.cnpj, fornecedor.valido (true/false). Se valido=true, prossegue; se valido=false, registra erro 'PARTNER_NOT_FOUND' e para. Payloads em anexo DE-PARA-v01.xlsx.'

**2. Dá pra melhorar:** Resultado P209 'será contabilizada' é passivo. Não especifica: em qual tabela (BSEG)? com qual conta (GL)? qual valor?
- Trecho: “[P209] A comissão será contabilizada no cliente e compensada com lançamento na transitória nova.” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > 'A comissão será contabilizada em BSEG com linha débito na conta cliente (GL 113000) e crédito na conta receita comissão (GL 540200). Na compensação, novo lançamento débito conta transitória (GL [?]) e crédito cliente (GL 113000). Valores devem bater na NF de origem.'

**3. Falta:** Faltam resultados esperados para cenários de erro e exceção (status ≠ 100, erro na compensação, erro na BAPI).
- Trecho: “[P207] até [P212]” _(não achei esse trecho na EF, confere)_
- Sugestão pra EF:
  > Adicione: 'P213 - Se status NF ≠ 100: BAdI CL_NFE_PRINT não é acionada, nenhuma compensação ou nota de crédito criada. Status permanece como recebido. P214 - Se POSTING_INTERFACE_CLEARING falha (status=ERRO): mensagem 'COMPENSATION_FAILED_[código]' é gravada em ZTFID_MKTPL_LG, BAPI_ACC_DOCUMENT_POST não é executada, conta transitória não recebe lançamento.'

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
- [ ] Ajustar a seção “Resumo do Desenvolvimento” (precisa de ajuste)
- [ ] Ajustar a seção “Processos relacionados” (precisa de ajuste)
- [ ] Ajustar a seção “Regras de negócio” (precisa de ajuste)
- [ ] Ajustar a seção “Fluxo do processo” (precisa de ajuste)
- [ ] Ajustar a seção “Sistemas e objetos impactados” (falta o essencial)
- [ ] Ajustar a seção “Novos objetos / campos” (precisa de ajuste)
- [ ] Ajustar a seção “Enhancements” (precisa de ajuste)
- [ ] Ajustar a seção “Aplicativo Fiori” (falta o essencial)
- [ ] Ajustar a seção “Interfaces de entrada / conversões” (falta o essencial)
- [ ] Ajustar a seção “Interfaces de saída” (falta o essencial)
- [ ] Ajustar a seção “Procedimento de testes” (precisa de ajuste)
- [ ] Ajustar a seção “Resultados esperados” (precisa de ajuste)
- [ ] Atualizar o histórico de revisão com a nova versão

---

_Esse feedback foi gerado automaticamente a partir da própria EF. Os trechos citados são o começo de cada parágrafo: é só copiar e buscar com Ctrl+F no Word. Ficou alguma dúvida? Chama o time técnico._
