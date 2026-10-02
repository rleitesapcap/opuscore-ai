# 021 — Pacote de Entrada para Descoberta SAP

## Controle do pacote

| Campo | Valor |
|---|---|
| Demanda | 021 |
| Projeto | MOVE2S/4 (Leroy Merlin) |
| EF | LEROY_REL_FI-021_Template Especifica_o Funcional_RemSimp_23092026_V04.docx |
| Versão informada | V4 |
| Última versão no histórico | V4 |
| Estado de aprovação | RASCUNHO |
| Anexos autorizados | nenhum |
| Gate | **VALIDO_COM_RESSALVAS** |
| Gerado em | 2026-10-02 01:40 UTC |
| Consultas SAP executadas | nenhuma (Etapa 1) |

## Gate

**VALIDO_COM_RESSALVAS**

- Nenhum bloqueio definitivo identificado pelas regras.
- 5 ressalva(s) devem ser tratadas na Etapa 2 ou com o funcional.

## Resumo do negócio

O objetivo é alterar o processo de contabilização da comissão do Marketplace para operações por Boleto e PIX, eliminando a transação ZAP0069. Após autorização fiscal (status 100), uma BAdI acionará compensação da fatura do cliente contra nova conta transitória e criação de nota de crédito no fornecedor. O resultado é permitir abatimento no repasse e pagamento líquido ao seller, mantendo o faturamento no cliente.

### Identificação, objetivo e componentes

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| D001 | ID GAP: 021 | FATO_DA_EF | ALTA | S00 · T0.r4 |
| D002 | Descrição GAP: Intermediação: Comissão MktPlace - Boleto e PIX | FATO_DA_EF | ALTA | S00 · T0.r4 |
| D003 | Projeto: MOVE2S/4 (Leroy Merlin) | FATO_DA_EF | ALTA | S00 · T0.r1 |
| D004 | Fase do Projeto: Realize | FATO_DA_EF | ALTA | S00 · T0.r1 |
| D005 | Módulo: FI | FATO_DA_EF | ALTA | S00 · T0.r2 |
| D006 | Cenário empresarial: Contas a Receber | FATO_DA_EF | ALTA | S00 · T0.r3 |
| D007 | Processo: GAP-FI-021-ENH | FATO_DA_EF | ALTA | S00 · T0.r3 |
| D008 | Autor: Victor Melo | FATO_DA_EF | ALTA | S00 · T0.r2 |
| D011 | Tipo de programa: Migração de Dados, Enhancement, Interface | FATO_DA_EF | ALTA | S01 · T1.r1 |
| D012 | Prioridade: Alta / Obrigatório | FATO_DA_EF | ALTA | S01 · T1.r2 |
| D013 | Impacto se não desenvolvido: Falta de informação para gerir o negócio | FATO_DA_EF | ALTA | S01 · T1.r13 |
| D014 | Impacto se não desenvolvido: Perda de funcionalidade em relação ao sistema antigo | FATO_DA_EF | ALTA | S01 · T1.r13 |
| D015 | Impacto se não desenvolvido: Mudança de procedimento necessário | FATO_DA_EF | ALTA | S01 · T1.r13 |
| D016 | Impacto se não desenvolvido: Outros: Volumetria excessiva | FATO_DA_EF | ALTA | S01 · T1.r13 |
| D017 | Volumetria excessiva | FATO_DA_EF | ALTA | S01 · T1.r13 |
| D018 | Existe alternativa no S/4HANA? Não | FATO_DA_EF | ALTA | S01 · T1.r14 |
| D019 | Objetivo: alterar o processo de contabilização da comissão do Marketplace para as operações realizadas por Boleto e PIX, mantendo o faturamento no cliente e substituindo o encontro de contas realizado pela ZAP0069. | FATO_DA_EF | ALTA | S03 · P019 |
| D020 | Após a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100, a lógica vinculada à BAdI CL_NFE_PRINT deverá executar, em sequência, os function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END para compensar a fatura do cliente contra a nova conta transitória. Após o sucesso da compensação, a BAPI_ACC_DOCUMENT_POST deverá criar a nota de crédito no fornecedor seller contra a mesma conta transitória, permitindo o abatimento no repas | FATO_DA_EF | ALTA | S03 · P021 |
| D021 | A alteração permitirá eliminar a transação ZAP0069 e o programa ZRFI_MKTPLACE_COMPENSACAO_RXC. | FATO_DA_EF | ALTA | S03 · P022 |
| D075 | Simplificação | FATO_DA_EF | ALTA | S12 · T4.r1 |
| D080 | A alternativa standard apresentada realiza contabilização apenas na visão cliente, sem geração de contabilização em conta de fornecedor. / O direcionamento seguirá para implementação via solução Z conforme programa já existente no ECC. | FATO_DA_EF | ALTA | S12 · T4.r6 |
| D086 | BAdI CL_NFE_PRINT — Enhancement **[REMEDIACAO]** origem: `BAdI CL_NFE_PRINT` | FATO_DA_EF | MEDIA | S13 · T5.r1 |

## Escopo da descoberta

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| D009 | Relação com o GAP FI-021-ENH: Cenário empresarial: Contas a Receber \| Processo: GAP-FI-021-ENH | FATO_DA_EF | ALTA | S00 · T0.r3 |
| D010 | Relação com o GAP FI-021: / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D033 | As operações realizadas por cartão não fazem parte do escopo desta alteração. | FATO_DA_EF | ALTA | S05 · P049 |
| D036 | As invoices são geradas em dois ciclos, nos dias 05 e 20, respeitando o intervalo de 15 dias. O ciclo possui valor sumarizado por ciclo e fornecedor, não por pedido. | FATO_DA_EF | ALTA | S06 · P077 |
| D037 | O processo de cartão não será alterado por este GAP. | FATO_DA_EF | ALTA | S06 · P079 |
| D038 | O novo fluxo de contabilização será aplicado somente às operações de Boleto e PIX. O processo de cartão não será alterado por este GAP. | FATO_DA_EF | ALTA | S06 · P079 |
| D039 | A compensação da fatura do cliente e a criação da nota de crédito no fornecedor dependem da autorização da nota fiscal na Sefaz e do status igual a 100. Para status diferente de 100, essas etapas não deverão ser executadas. | FATO_DA_EF | ALTA | S06 · P081 |
| D040 | A tabela ZTFID_MKTPL_LG será mantida para os documentos de repasse e devolução, tipos MP e MC. | FATO_DA_EF | ALTA | S06 · P083 |
| D041 | A ZAP0069 será descontinuada. | FATO_DA_EF | ALTA | S06 · P085 |
| D042 | A solução utilizará a lógica vinculada à BAdI CL_NFE_PRINT, acionada para nota fiscal com status igual a 100; os function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END para a compensação da fatura do cliente; e a BAPI_ACC_DOCUMENT_POST para criação da nota de crédito no fornecedor seller. | FATO_DA_EF | ALTA | S06 · P087 |
| D043 | A compensação e a criação da nota de crédito somente deverão ocorrer após a autorização da nota fiscal na Sefaz e quando o status da nota fiscal for igual a 100. | FATO_DA_EF | ALTA | S06 · P088 |
| D062 | Sistemas envolvidos: Marketplace/Mirakl, Gateway KONG, SAP CPI, serviço OData criado em ABAP/RAP, SAP ECC e SAP S/4HANA. Módulos envolvidos: FI-AR, FI-AP e SD. | FATO_DA_EF | ALTA | S08 · P112 |
| D063 | Integração atual: ZFSD_ITF_BKF_ORDEM_VENDA_TRANS. | FATO_DA_EF | ALTA | S08 · P114 |
| D064 | Funções/classes atuais: ZFSD_CONSULTA_CLIENTE, ZFSD_CRIAR_IDOC_CLIENTE, ZFSD_CRIAR_IDOC_OV e zcl_itf_bkf_ordem_venda_trans1. | FATO_DA_EF | ALTA | S08 · P116 |
| D065 | Transação/programa eliminado: ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC. Tabela mantida: ZTFID_MKTPL_LG. | FATO_DA_EF | ALTA | S08 · P118 |
| D066 | BAdI/lógica de SD: CL_NFE_PRINT. Function modules de compensação: POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END. BAPI de FI: BAPI_ACC_DOCUMENT_POST. | FATO_DA_EF | ALTA | S08 · P120 |
| D067 | Objetos do novo fluxo: API Business Partner, API Documento Contábil, API standard Sales Order, Gateway KONG, SAP CPI, serviço OData criado em ABAP/RAP, BAdI/lógica CL_NFE_PRINT na VF01, function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END, BAPI_ACC_DOCUMENT_POST, BRF+ e tabela de log ZTFID_MKTPL_LG. | FATO_DA_EF | ALTA | S08 · P122 |
| D068 | Tipos de documentos do processo atual: MP - Repasse do seller; MC - Devolução/Cancelamentos; RM - Documento da nota de comissão. | FATO_DA_EF | ALTA | S08 · P124 |
| D076 | Tipo de ampliação (Custom Field / BAdI / Exit / Enhancement Spot): BAdI/lógica CL_NFE_PRINT; function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END; BAPI_ACC_DOCUMENT_POST. | FATO_DA_EF | ALTA | S12 · T4.r2 |
| D077 | Lista de Transações/programas ou Jobs para Remediação/Simplificação: ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC - / ELIMINAR / / ZFSD_ITF_BKF_ORDEM_VENDA_TRANS - fluxo atual de integração. | FATO_DA_EF | ALTA | S12 · T4.r3 |
| D078 | Existe Fiorização de Transações ? se sim, informar lista, e qual catálogo do Fiori será utilizado , ou caso não / exista o perfil de acesso: NA | FATO_DA_EF | ALTA | S12 · T4.r4 |
| D079 | Objeto ou ponto de extensão conhecido: VF01 - lógica vinculada à CL_NFE_PRINT, acionada após autorização da nota fiscal com status igual a 100. | FATO_DA_EF | ALTA | S12 · T4.r5 |
| D081 | Validação na SCFD_REGISTRY, quando aplicável: NA | FATO_DA_EF | ALTA | S12 · T4.r7 |
| D082 | Campos envolvidos: Status da nota fiscal; CNPJ; dados do cliente e do fornecedor; retorno de cliente ou fornecedor válido; dados da Ordem de Venda; dados da fatura do cliente; conta transitória; dados do fornecedor seller; documentos de repasse e devolução MP e MC. | FATO_DA_EF | ALTA | S12 · T4.r8 |
| D083 | Regras e validações: Aplicar o novo fluxo exclusivamente às operações de Boleto e PIX, sem alteração do processo de cartão; consultar e validar cliente e fornecedor por CNPJ, sem consulta por CPF; prosseguir após o retorno de cliente ou fornecedor válido; utilizar a API standard Sales Order para criar a Ordem de Venda; manter a fatura da comissão no cliente; processar somente para nota fiscal com status 100; compensar a fatura contra a conta transitória; criar a nota de crédito no fornecedor som | FATO_DA_EF | ALTA | S12 · T4.r9 |
| D084 | Impactos em interfaces, relatórios ou apps: Marketplace/Mirakl, Gateway KONG, SAP CPI, serviço OData ABAP/RAP, APIs Business Partner, Documento Contábil e Ordem de Venda, VF01, FI-AR, FI-AP, SD e SLG1. | FATO_DA_EF | ALTA | S12 · T4.r11 |
| D085 | Cenários de exceção: Status diferente de 100; erro no fluxo KONG/CPI/OData; erro na criação da Ordem de Venda; erro na emissão ou autorização da nota fiscal; erro na compensação; erro na criação da nota de crédito no fornecedor. | FATO_DA_EF | ALTA | S12 · T4.r12 |
| D087 | Uso declarado de ponto de ampliação implícito: / VF01 \| / BADI/enhance ment \| Acionar a lógica vinculada à CL_NFE_PRINT para nota fiscal com status 100; executar POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END para compensação da fatura do cliente; e executar BAPI_ACC_DOCUMENT_POST para criação da nota de crédito no fornecedor após o sucesso da compensação. | FATO_DA_EF | ALTA | S15 · T7.r1 |

## Requisitos e regras

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| D022 | -Marketplace/Mirakl - evento de disparo do período de Repasse e Comissão. | FATO_DA_EF | ALTA | S04 · P028 |
| D023 | -Gateway KONG - exposição das APIs chamadas pela Plataforma Marketplace. | FATO_DA_EF | ALTA | S04 · P030 |
| D024 | -SAP CPI - roteamento das chamadas recebidas pelo Gateway KONG para o serviço OData criado em ABAP/RAP. | FATO_DA_EF | ALTA | S04 · P032 |
| D025 | -API Business Partner - consulta e validação, por CNPJ, da existência do cliente e do fornecedor, sem consulta por CPF, com retorno da informação de cliente ou fornecedor válido. | FATO_DA_EF | ALTA | S04 · P034 |
| D026 | -API standard Sales Order - criação da Ordem de Venda no SAP S/4HANA. | FATO_DA_EF | ALTA | S04 · P036 |
| D027 | -API Documento Contábil - API integrante do fluxo de integração informado para o processo. | FATO_DA_EF | ALTA | S04 · P037 |
| D028 | -VF01 - faturamento e geração da fatura no cliente. | FATO_DA_EF | ALTA | S04 · P039 |
| D029 | -BAdI CL_NFE_PRINT - lógica acionada após a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100. | FATO_DA_EF | ALTA | S04 · P040 |
| D030 | -Function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END - inicialização, compensação da fatura do cliente contra a conta transitória e finalização da interface de compensação. | FATO_DA_EF | ALTA | S04 · P042 |
| D031 | -BAPI_ACC_DOCUMENT_POST - criação da nota de crédito no fornecedor seller contra a mesma conta transitória, após o sucesso da compensação. | FATO_DA_EF | ALTA | S04 · P044 |
| D032 | -ZTFID_MKTPL_LG - manutenção dos dados dos documentos de repasse e devolução, tipos MP e MC, e monitoramento do processo. -ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC - transação e programa de compensação que serão eliminados. -Endpoint KONG: /v1/orders/payment/fee. | FATO_DA_EF | ALTA | S04 · P046 |
| D034 | Após a compensação da fatura do cliente e a contabilização da nota de crédito no fornecedor seller, a conta transitória deverá apresentar saldo zerado. | FATO_DA_EF | ALTA | S05 · P066 |
| D035 | A tabela ZTFID_MKTPL_LG deverá ser mantida com os dados dos documentos contábeis de repasse e devolução, correspondentes aos tipos MP e MC. | FATO_DA_EF | ALTA | S05 · P068 |
| D044 | Passo 1: A Plataforma Marketplace dispara o período de Repasse e Comissão. | FATO_DA_EF | ALTA | S07 · P091 |
| D045 | Passo 2: A Plataforma Marketplace chama as APIs por meio do fluxo Marketplace -> KONG -> SAP CPI -> serviço OData criado em ABAP/RAP no SAP S/4HANA. | FATO_DA_EF | ALTA | S07 · P092 |
| D046 | Passo 3: A API Business Partner consulta e valida, por CNPJ, a existência do cliente e do fornecedor. Não haverá consulta por CPF. Após a localização e o retorno da informação de cliente ou fornecedor válido, a API standard Sales Order cria a Ordem de Venda no SAP S/4HANA. | FATO_DA_EF | ALTA | S07 · P093 |
| D047 | Passo 4: A VF01 realiza o faturamento e gera a fatura no cliente. | FATO_DA_EF | ALTA | S07 · P094 |
| D048 | Passo 5: A nota fiscal é enviada para autorização na Sefaz. | FATO_DA_EF | ALTA | S07 · P095 |
| D049 | Passo 6: Quando o status da nota fiscal for igual a 100, é acionada a lógica vinculada à BAdI CL_NFE_PRINT. | FATO_DA_EF | ALTA | S07 · P096 |
| D050 | Passo 7: A POSTING_INTERFACE_START inicia a interface de compensação. | FATO_DA_EF | ALTA | S07 · P097 |
| D051 | Passo 8: A POSTING_INTERFACE_CLEARING compensa a fatura do cliente contra a nova conta transitória. | FATO_DA_EF | ALTA | S07 · P098 |
| D052 | Passo 9: A POSTING_INTERFACE_END finaliza a interface de compensação. | FATO_DA_EF | ALTA | S07 · P099 |
| D053 | Passo 10: O retorno da compensação é validado. | FATO_DA_EF | ALTA | S07 · P100 |
| D054 | Passo 11: Após o retorno de sucesso da compensação, a BAPI_ACC_DOCUMENT_POST cria a nota de crédito no fornecedor seller contra a mesma conta transitória. | FATO_DA_EF | ALTA | S07 · P101 |
| D055 | Passo 12: Os documentos de repasse e devolução dos tipos MP e MC são mantidos na ZTFID_MKTPL_LG. | FATO_DA_EF | ALTA | S07 · P102 |
| D056 | Passo 13: O saldo da conta transitória é validado após a compensação da fatura do cliente e a criação da nota de crédito no fornecedor. | FATO_DA_EF | ALTA | S07 · P103 |
| D057 | Passo 14: A conta transitória deverá apresentar saldo zerado. | FATO_DA_EF | ALTA | S07 · P104 |
| D058 | Passo 15: A nota de crédito deverá ser abatida do valor do repasse ao seller. | FATO_DA_EF | ALTA | S07 · P105 |
| D059 | Passo 16: O repasse líquido deverá ser pago ao seller. | FATO_DA_EF | ALTA | S07 · P106 |
| D060 | Passo 17: Para status diferente de 100, a compensação e a criação da nota de crédito não deverão ser executadas. Em caso de erro na compensação, o erro deverá ser registrado e a BAPI_ACC_DOCUMENT_POST não deverá ser executada. | FATO_DA_EF | ALTA | S07 · P107 |
| D061 | Passo 18: Com a implantação do novo fluxo, a ZAP0069 e o programa ZRFI_MKTPLACE_COMPENSACAO_RXC deixarão de ser utilizados. | FATO_DA_EF | ALTA | S07 · P108 |
| D069 | Conta transitória nova para compensação da fatura do cliente e contabilização da nota de crédito no fornecedor. Serviço OData criado em ABAP/RAP para consumo pelo SAP CPI e execução das validações e regras atuais. | FATO_DA_EF | ALTA | S09 · P129 |
| D070 | BAdI/lógica CL_NFE_PRINT na VF01, acionada após a autorização da nota fiscal com status igual a 100. | FATO_DA_EF | ALTA | S09 · P131 |
| D071 | Function modules: POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END. | FATO_DA_EF | ALTA | S09 · P133 |
| D072 | BAPI de FI: BAPI_ACC_DOCUMENT_POST. | FATO_DA_EF | ALTA | S09 · P135 |
| D073 | Nota de crédito no fornecedor seller contra a conta transitória nova. | FATO_DA_EF | ALTA | S09 · P137 |
| D074 | BRF+ para salvar os dados das contas contábeis. | FATO_DA_EF | ALTA | S09 · P139 |
| D088 | [VF01 - / BADI CL_NFE_PRINT] Após o faturamento e a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100, a lógica vinculada à CL_NFE_PRINT deverá executar, em sequência, os function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END. A POSTING_INTERFACE_CLEARING deverá compensar a fatura do cliente contra a nova conta transitória. Após a confirmação do sucesso da compensação, deverá ser chamada a BAPI_ACC_DOCUMENT_POST para criar a | FATO_DA_EF | ALTA | S16 · T8.r1 |
| D102 | Os dados do período de Repasse e Comissão devem percorrer o fluxo Marketplace -> KONG -> SAP CPI -> serviço OData criado em ABAP/RAP. | FATO_DA_EF | ALTA | S19 · P207 |
| D103 | A API Business Partner deve consultar e validar cliente e fornecedor por CNPJ, sem consulta por CPF, e retornar a informação de cliente ou fornecedor válido. A API Documento Contábil e a API standard Sales Order devem ser chamadas conforme o fluxo de integração. Os payloads e mapeamentos deverão seguir o DE/PARA a ser fornecido. | FATO_DA_EF | ALTA | S19 · P208 |
| D104 | A comissão será contabilizada no cliente e compensada com lançamento na transitória nova. | FATO_DA_EF | ALTA | S19 · P209 |
| D105 | Após a autorização da nota fiscal na Sefaz, com status igual a 100, a fatura do cliente deve ser compensada contra a conta transitória e a nota de crédito deve ser criada no fornecedor seller contra a mesma conta. | FATO_DA_EF | ALTA | S19 · P210 |
| D106 | O valor da nota de crédito deve ser abatido no pagamento do repasse ao seller. | FATO_DA_EF | ALTA | S19 · P211 |
| D107 | A tabela ZTFID_MKTPL_LG deve manter os documentos de repasse e devolução, tipos MP e MC. | FATO_DA_EF | ALTA | S19 · P212 |
| D116 | Ator citado: usuário | FATO_DA_EF | ALTA | S10 · T3.r4 |

## Referências técnicas declaradas

### No escopo ou indefinidas

| ID | Valor original | Tipo | Escopo | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|---|---|---|
| D117 | `BAPI_ACC_DOCUMENT_POST` | OUTRO | INCLUIDO | Outro citado em 17 ponto(s) da EF. Escopo inferido: citado na lista de objetos a remediar/manter. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D118 | `CL_NFE_PRINT` | BADI | INDEFINIDO | Badi citado em 15 ponto(s) da EF. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D119 | `NSACAO_RXC` | OUTRO | INDEFINIDO | Outro citado em 1 ponto(s) da EF. | FATO_DA_EF | ALTA | S14 · T6.r1 |
| D120 | `POSTING_INTERFACE_CLEARING` | OUTRO | INDEFINIDO | Outro citado em 15 ponto(s) da EF. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D121 | `POSTING_INTERFACE_END` | OUTRO | INDEFINIDO | Outro citado em 14 ponto(s) da EF. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D122 | `POSTING_INTERFACE_START` | OUTRO | INDEFINIDO | Outro citado em 14 ponto(s) da EF. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D123 | `SCFD_REGISTRY` | OUTRO | INDEFINIDO | Outro citado em 1 ponto(s) da EF. | FATO_DA_EF | ALTA | S12 · T4.r7 |
| D124 | `ZAP0069` | TRANSACAO | INCLUIDO | Transacao citado em 11 ponto(s) da EF. Escopo inferido: citado na lista de objetos a remediar/manter. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D125 | `ZFSD_CONSULTA_CLIENTE` | OUTRO | INDEFINIDO | Outro citado em 1 ponto(s) da EF. | FATO_DA_EF | ALTA | S08 · P116 |
| D126 | `ZFSD_CRIAR_IDOC_CLIENTE` | OUTRO | INDEFINIDO | Outro citado em 1 ponto(s) da EF. | FATO_DA_EF | ALTA | S08 · P116 |
| D127 | `ZFSD_CRIAR_IDOC_OV` | OUTRO | INDEFINIDO | Outro citado em 1 ponto(s) da EF. | FATO_DA_EF | ALTA | S08 · P116 |
| D128 | `ZFSD_ITF_BKF_ORDEM_VENDA_TRANS` | OUTRO | INDEFINIDO | Outro citado em 2 ponto(s) da EF. | FATO_DA_EF | ALTA | S08 · P114 |
| D129 | `ZRFI_MKTPLACE_COMPE` | OUTRO | INDEFINIDO | Outro citado em 1 ponto(s) da EF. | FATO_DA_EF | ALTA | S14 · T6.r1 |
| D130 | `ZRFI_MKTPLACE_COMPENSACAO_RXC` | PROGRAMA | INCLUIDO | Programa citado em 7 ponto(s) da EF. Escopo inferido: citado na lista de objetos a remediar/manter. | FATO_DA_EF | ALTA | S01 · T1.r0 |
| D131 | `ZTFID_MKTPL_LG` | TABELA | INCLUIDO | Tabela citado em 11 ponto(s) da EF. Escopo inferido: citado na lista de objetos a remediar/manter. | FATO_DA_EF | ALTA | S04 · P046 |
| AUTO001 | `ZTD_LMB_PARAMETROS` | OUTRO | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S10 · T3.r2 |
| AUTO002 | `ZTXXC_PARA_1` | OUTRO | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S10 · T3.r2 |
| AUTO003 | `ZTXXC_PARA_2` | OUTRO | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S10 · T3.r2 |

## Âncoras funcionais

_Nenhum item extraído._

## Interfaces, dados e campos

_Nenhum item extraído._

## Cenários e testes

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| D089 | Objetivo do teste é validar o novo fluxo de contabilização da comissão do Marketplace exclusivamente para Boleto e PIX, sem alteração do processo de cartão. | FATO_DA_EF | ALTA | S18 · P190 |
| D090 | Pré-requisito: período de Repasse, Comissão E Devolução/cancelamento fechado na Plataforma Marketplace, fornecedor seller e cliente existentes e nota fiscal aprovada na Sefaz. | FATO_DA_EF | ALTA | S18 · P191 |
| D091 | Passos do teste: | FATO_DA_EF | ALTA | S18 · P192 |
| D092 | Disparar o período de Repasse e Comissão na Plataforma Marketplace. | FATO_DA_EF | ALTA | S18 · P193 |
| D093 | Acompanhar o fluxo Marketplace -> KONG -> SAP CPI -> serviço OData criado em ABAP/RAP. | FATO_DA_EF | ALTA | S18 · P194 |
| D094 | Validar a consulta e a validação do cliente e do fornecedor por CNPJ na API Business Partner, sem consulta por CPF, incluindo o retorno da informação de cliente ou fornecedor válido; validar também as chamadas da API Documento Contábil e da API standard Sales Order. | FATO_DA_EF | ALTA | S18 · P195 |
| D095 | Validar contabilização da fatura no cliente. | FATO_DA_EF | ALTA | S18 · P196 |
| D096 | Validar que a lógica vinculada à CL_NFE_PRINT seja acionada somente quando o status da nota fiscal for igual a 100. | FATO_DA_EF | ALTA | S18 · P197 |
| D097 | Validar a execução sequencial de POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END e a compensação da fatura do cliente contra a conta transitória. | FATO_DA_EF | ALTA | S18 · P198 |
| D098 | Validar que a BAPI_ACC_DOCUMENT_POST seja executada somente após o sucesso da compensação e crie a nota de crédito no fornecedor seller contra a mesma conta transitória. | FATO_DA_EF | ALTA | S18 · P199 |
| D099 | Validar o abatimento da nota de crédito no pagamento do repasse ao seller. | FATO_DA_EF | ALTA | S18 · P200 |
| D100 | Validar a manutenção da tabela ZTFID_MKTPL_LG para os documentos de repasse e devolução, tipos MP e MC. | FATO_DA_EF | ALTA | S18 · P201 |
| D101 | Validar saldo zerado na conta transitória após os lançamentos a crédito e débito | FATO_DA_EF | ALTA | S18 · P202 |

## Requisitos não funcionais

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| D109 | Periodicidade de Execução: As invoices são geradas em dois ciclos, nos dias 05 e 20. A periodicidade da integração está indicada como 3 vezes ao dia. | FATO_DA_EF | ALTA | S22 · P227 |
| D110 | Tipo de Execução: Integração via SAP CPI e APIs. | FATO_DA_EF | ALTA | S23 · P230 |
| D111 | Volumetria e frequência de execução.: Volumes mensais médios: R$ 1,9 milhão em comissão (2.000 NFs). | FATO_DA_EF | ALTA | S24 · P234 |
| D112 | Janela para Execução: NA | FATO_DA_EF | ALTA | S25 · P238 |
| D113 | Tratamento de erros, logs, monitoramento e reprocessamento.: Os erros dos processos de integração, incluindo KONG, SAP CPI e serviço OData ABAP/RAP, criação da Ordem de Venda, autorização da nota fiscal, compensação e criação da nota de crédito deverão ser gravados em log e monitorados na tabela ZTFID_MKTPL_LG. | FATO_DA_EF | ALTA | S26 · P243 |
| D114 | Tratamento de erros, logs, monitoramento e reprocessamento.: Em caso de erro na compensação, a BAPI_ACC_DOCUMENT_POST não deverá ser executada. | FATO_DA_EF | ALTA | S26 · P244 |
| D115 | Processo Crítico: A ausência da solução mantém a necessidade da compensação entre cliente seller e fornecedor seller e gera falta de informação para gerir o negócio, perda de funcionalidade, mudança de procedimento e impacto relacionado à volumetria. | FATO_DA_EF | ALTA | S27 · P249 |

## Plano solicitado para a Etapa 2

| ID | Objetivo | Alvos | Tipo de verificação | Prioridade |
|---|---|---|---|---|
| V01 | Ler a estrutura DDIC (somente leitura) | D131 | estrutura DDIC | ALTA |
| V02 | Listar implementações ativas da BAdI | D118 | existência de objeto | MEDIA |
| V03 | Confirmar a transação e o programa/objeto associado | D124 | existência de objeto | ALTA |
| V04 | Identificar o tipo do objeto no repositório | D117, D119, D120, D121, D122, D123, D125, D126, D127, D128, D129 | identificação | ALTA |
| V05 | Ler o código-fonte e localizar os controles citados | D130 | leitura de código | ALTA |

Viabilidade sem varredura irrestrita: **sim** — 15 referência(s) técnica(s) no escopo ou indefinidas orientam a pesquisa.

## Pontos a confirmar

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| A001 | Momento exato de disparo da BAdI e sequência de execução dos function modules não está claro quanto ao tratamento de transações SAP (commit/rollback). Não fica explícito se cada FM é uma transação isolada ou se há uma transação englobante. | PONTO_A_CONFIRMAR | MEDIA | S05 · P059, P060, P061, P062 |
| A002 | Condição de validação do status 100 aparece duplicada em contextos ligeiramente diferentes: uma refere-se à Sefaz e autorização, outra apenas ao status da nota fiscal. Não está claro se são validações diferentes ou a mesma regra. | ENTENDIMENTO | MEDIA | S05 · P065 |
| A003 | Não há detalhamento sobre o comportamento quando a POSTING_INTERFACE_CLEARING falha parcialmente (ex.: compensa parte da fatura). Fica apenas indicado que em caso de erro, a BAPI não executa, mas não há definição de rollback ou compensação de erros. | PONTO_A_CONFIRMAR | MEDIA | S05 · P071 |
| A004 | A regra menciona que a conta transitória deve apresentar saldo zerado após compensação e nota de crédito, mas não especifica se isso é uma validação de negócio obrigatória ou apenas uma verificação informativa. Não está claro se deve haver bloqueio ou apenas log. | ENTENDIMENTO | MEDIA | S05 · P066 |
| A005 | Não há especificação sobre cenários de reprocessamento: se uma nota fiscal retorna status 100 após ter sido rejeitada, ou se passa de status 100 para outro, como a BAdI deve se comportar. Risco de duplicação de registros. | PONTO_A_CONFIRMAR | BAIXA | S07 · P096 |
| AUTO001 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S10 · T3.r2 |
| AUTO002 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S10 · T3.r2 |
| AUTO003 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S10 · T3.r2 |

### Ressalvas do gate

- 6 item(ns) classificados como PONTO_A_CONFIRMAR.
- 2 ausência(s) registrada(s) na EF.
- 3 ambiguidade(s) registrada(s) na EF.
- 3 identificador(es) técnico(s) presentes na EF não foram extraídos pela IA e foram incluídos automaticamente como PONTO_A_CONFIRMAR (escopo a confirmar): ZTD_LMB_PARAMETROS, ZTXXC_PARA_1, ZTXXC_PARA_2.
- EF no estado RASCUNHO: o gate máximo é VALIDO_COM_RESSALVAS.

## Limitações

- Nenhuma consulta a SAP, BTP, CPI ou Workflow foi executada nesta etapa.
- Existência de objetos e transações não foi confirmada; é objetivo da Etapa 2.
- Não foi possível validar existência ou assinatura dos BAPIs e FMs listados; apenas confirmou-se sua referência na EF.
- Detalhes de implementação BRF+ e estrutura da nova conta transitória não estão no escopo narrativo.
- Configuração do serviço OData em ABAP/RAP é mencionada mas não detalhada nesta EF.

## Rastreabilidade

Cada item acima referencia a seção e a localização na EF. Trechos de origem:

| ID | Seção | Localização | Trecho de origem |
|---|---|---|---|
| D001 | S00 | T0.r4 | ID GAP: 021 \| Descrição GAP: Intermediação: Comissão MktPlace - Boleto e PIX |
| D002 | S00 | T0.r4 | ID GAP: 021 \| Descrição GAP: Intermediação: Comissão MktPlace - Boleto e PIX |
| D003 | S00 | T0.r1 | Projeto: MOVE2S/4 (Leroy Merlin) \| Fase do Projeto: Realize |
| D004 | S00 | T0.r1 | Projeto: MOVE2S/4 (Leroy Merlin) \| Fase do Projeto: Realize |
| D005 | S00 | T0.r2 | Autor: Victor Melo \| Módulo: FI |
| D006 | S00 | T0.r3 | Cenário empresarial: Contas a Receber \| Processo: GAP-FI-021-ENH |
| D007 | S00 | T0.r3 | Cenário empresarial: Contas a Receber \| Processo: GAP-FI-021-ENH |
| D008 | S00 | T0.r2 | Autor: Victor Melo \| Módulo: FI |
| D009 | S00 | T0.r3 | Cenário empresarial: Contas a Receber \| Processo: GAP-FI-021-ENH |
| D010 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D011 | S01 | T1.r1 | / / Tipo de programa \| / / (X ) Migração de Dados ( X ) Enhancement ( X ) Interface ( ) App Fiori ( ) Formulário ( ) Modificação SAP standard ( ) Programa online ( ) Fiorização ( ) Outros |
| D012 | S01 | T1.r2 | Prioridade \| ( X ) Alta / Obrigatório ( ) Média / Recomendável ( ) Baixa / Desejável |
| D013 | S01 | T1.r13 | / / / Impacto caso não seja desenvolvido \| / ( ) Requerimentos legais não serão atendidos ( X ) Falta de informação para gerir o negócio / ( X ) Perda de funcionalidade em relação ao sistema antigo ( X ) Mudança de proc |
| D014 | S01 | T1.r13 | / / / Impacto caso não seja desenvolvido \| / ( ) Requerimentos legais não serão atendidos ( X ) Falta de informação para gerir o negócio / ( X ) Perda de funcionalidade em relação ao sistema antigo ( X ) Mudança de proc |
| D015 | S01 | T1.r13 | / / / Impacto caso não seja desenvolvido \| / ( ) Requerimentos legais não serão atendidos ( X ) Falta de informação para gerir o negócio / ( X ) Perda de funcionalidade em relação ao sistema antigo ( X ) Mudança de proc |
| D016 | S01 | T1.r13 | / / / Impacto caso não seja desenvolvido \| / ( ) Requerimentos legais não serão atendidos ( X ) Falta de informação para gerir o negócio / ( X ) Perda de funcionalidade em relação ao sistema antigo ( X ) Mudança de proc |
| D017 | S01 | T1.r13 | / / / Impacto caso não seja desenvolvido \| / ( ) Requerimentos legais não serão atendidos ( X ) Falta de informação para gerir o negócio / ( X ) Perda de funcionalidade em relação ao sistema antigo ( X ) Mudança de proc |
| D018 | S01 | T1.r14 | Existe alternativa no S4HANA? \| ( ) Sim ( X ) Não |
| D019 | S03 | P019 | Objetivo: alterar o processo de contabilização da comissão do Marketplace para as operações realizadas por Boleto e PIX, mantendo o faturamento no cliente e substituindo o encontro de contas realizado pela ZAP0069. |
| D020 | S03 | P021 | Após a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100, a lógica vinculada à BAdI CL_NFE_PRINT deverá executar, em sequência, os function modules POSTING_INTERFACE_START, POSTING_INTER |
| D021 | S03 | P022 | A alteração permitirá eliminar a transação ZAP0069 e o programa ZRFI_MKTPLACE_COMPENSACAO_RXC. |
| D022 | S04 | P028 | -Marketplace/Mirakl - evento de disparo do período de Repasse e Comissão. |
| D023 | S04 | P030 | -Gateway KONG - exposição das APIs chamadas pela Plataforma Marketplace. |
| D024 | S04 | P032 | -SAP CPI - roteamento das chamadas recebidas pelo Gateway KONG para o serviço OData criado em ABAP/RAP. |
| D025 | S04 | P034 | -API Business Partner - consulta e validação, por CNPJ, da existência do cliente e do fornecedor, sem consulta por CPF, com retorno da informação de cliente ou fornecedor válido. |
| D026 | S04 | P036 | -API standard Sales Order - criação da Ordem de Venda no SAP S/4HANA. |
| D027 | S04 | P037 | -API Documento Contábil - API integrante do fluxo de integração informado para o processo. |
| D028 | S04 | P039 | -VF01 - faturamento e geração da fatura no cliente. |
| D029 | S04 | P040 | -BAdI CL_NFE_PRINT - lógica acionada após a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100. |
| D030 | S04 | P042 | -Function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END - inicialização, compensação da fatura do cliente contra a conta transitória e finalização da interface de compensação. |
| D031 | S04 | P044 | -BAPI_ACC_DOCUMENT_POST - criação da nota de crédito no fornecedor seller contra a mesma conta transitória, após o sucesso da compensação. |
| D032 | S04 | P046 | -ZTFID_MKTPL_LG - manutenção dos dados dos documentos de repasse e devolução, tipos MP e MC, e monitoramento do processo. -ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC - transação e programa de compensação que serão eliminado |
| D033 | S05 | P049 | As operações realizadas por cartão não fazem parte do escopo desta alteração. |
| D034 | S05 | P066 | Após a compensação da fatura do cliente e a contabilização da nota de crédito no fornecedor seller, a conta transitória deverá apresentar saldo zerado. |
| D035 | S05 | P068 | A tabela ZTFID_MKTPL_LG deverá ser mantida com os dados dos documentos contábeis de repasse e devolução, correspondentes aos tipos MP e MC. |
| D036 | S06 | P077 | As invoices são geradas em dois ciclos, nos dias 05 e 20, respeitando o intervalo de 15 dias. O ciclo possui valor sumarizado por ciclo e fornecedor, não por pedido. |
| D037 | S06 | P079 | O processo de cartão não será alterado por este GAP. |
| D038 | S06 | P079 | O novo fluxo de contabilização será aplicado somente às operações de Boleto e PIX. O processo de cartão não será alterado por este GAP. |
| D039 | S06 | P081 | A compensação da fatura do cliente e a criação da nota de crédito no fornecedor dependem da autorização da nota fiscal na Sefaz e do status igual a 100. Para status diferente de 100, essas etapas não deverão ser executad |
| D040 | S06 | P083 | A tabela ZTFID_MKTPL_LG será mantida para os documentos de repasse e devolução, tipos MP e MC. |
| D041 | S06 | P085 | A ZAP0069 será descontinuada. |
| D042 | S06 | P087 | A solução utilizará a lógica vinculada à BAdI CL_NFE_PRINT, acionada para nota fiscal com status igual a 100; os function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END para a compens |
| D043 | S06 | P088 | A compensação e a criação da nota de crédito somente deverão ocorrer após a autorização da nota fiscal na Sefaz e quando o status da nota fiscal for igual a 100. |
| D044 | S07 | P091 | A Plataforma Marketplace dispara o período de Repasse e Comissão. |
| D045 | S07 | P092 | A Plataforma Marketplace chama as APIs por meio do fluxo Marketplace -> KONG -> SAP CPI -> serviço OData criado em ABAP/RAP no SAP S/4HANA. |
| D046 | S07 | P093 | A API Business Partner consulta e valida, por CNPJ, a existência do cliente e do fornecedor. Não haverá consulta por CPF. Após a localização e o retorno da informação de cliente ou fornecedor válido, a API standard Sales |
| D047 | S07 | P094 | A VF01 realiza o faturamento e gera a fatura no cliente. |
| D048 | S07 | P095 | A nota fiscal é enviada para autorização na Sefaz. |
| D049 | S07 | P096 | Quando o status da nota fiscal for igual a 100, é acionada a lógica vinculada à BAdI CL_NFE_PRINT. |
| D050 | S07 | P097 | A POSTING_INTERFACE_START inicia a interface de compensação. |
| D051 | S07 | P098 | A POSTING_INTERFACE_CLEARING compensa a fatura do cliente contra a nova conta transitória. |
| D052 | S07 | P099 | A POSTING_INTERFACE_END finaliza a interface de compensação. |
| D053 | S07 | P100 | O retorno da compensação é validado. |
| D054 | S07 | P101 | Após o retorno de sucesso da compensação, a BAPI_ACC_DOCUMENT_POST cria a nota de crédito no fornecedor seller contra a mesma conta transitória. |
| D055 | S07 | P102 | Os documentos de repasse e devolução dos tipos MP e MC são mantidos na ZTFID_MKTPL_LG. |
| D056 | S07 | P103 | O saldo da conta transitória é validado após a compensação da fatura do cliente e a criação da nota de crédito no fornecedor. |
| D057 | S07 | P104 | A conta transitória deverá apresentar saldo zerado. |
| D058 | S07 | P105 | A nota de crédito deverá ser abatida do valor do repasse ao seller. |
| D059 | S07 | P106 | O repasse líquido deverá ser pago ao seller. |
| D060 | S07 | P107 | Para status diferente de 100, a compensação e a criação da nota de crédito não deverão ser executadas. Em caso de erro na compensação, o erro deverá ser registrado e a BAPI_ACC_DOCUMENT_POST não deverá ser executada. |
| D061 | S07 | P108 | Com a implantação do novo fluxo, a ZAP0069 e o programa ZRFI_MKTPLACE_COMPENSACAO_RXC deixarão de ser utilizados. |
| D062 | S08 | P112 | Sistemas envolvidos: Marketplace/Mirakl, Gateway KONG, SAP CPI, serviço OData criado em ABAP/RAP, SAP ECC e SAP S/4HANA. Módulos envolvidos: FI-AR, FI-AP e SD. |
| D063 | S08 | P114 | Integração atual: ZFSD_ITF_BKF_ORDEM_VENDA_TRANS. |
| D064 | S08 | P116 | Funções/classes atuais: ZFSD_CONSULTA_CLIENTE, ZFSD_CRIAR_IDOC_CLIENTE, ZFSD_CRIAR_IDOC_OV e zcl_itf_bkf_ordem_venda_trans1. |
| D065 | S08 | P118 | Transação/programa eliminado: ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC. Tabela mantida: ZTFID_MKTPL_LG. |
| D066 | S08 | P120 | BAdI/lógica de SD: CL_NFE_PRINT. Function modules de compensação: POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END. BAPI de FI: BAPI_ACC_DOCUMENT_POST. |
| D067 | S08 | P122 | Objetos do novo fluxo: API Business Partner, API Documento Contábil, API standard Sales Order, Gateway KONG, SAP CPI, serviço OData criado em ABAP/RAP, BAdI/lógica CL_NFE_PRINT na VF01, function modules POSTING_INTERFACE |
| D068 | S08 | P124 | Tipos de documentos do processo atual: MP - Repasse do seller; MC - Devolução/Cancelamentos; RM - Documento da nota de comissão. |
| D069 | S09 | P129 | Conta transitória nova para compensação da fatura do cliente e contabilização da nota de crédito no fornecedor. Serviço OData criado em ABAP/RAP para consumo pelo SAP CPI e execução das validações e regras atuais. |
| D070 | S09 | P131 | BAdI/lógica CL_NFE_PRINT na VF01, acionada após a autorização da nota fiscal com status igual a 100. |
| D071 | S09 | P133 | Function modules: POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END. |
| D072 | S09 | P135 | BAPI de FI: BAPI_ACC_DOCUMENT_POST. |
| D073 | S09 | P137 | Nota de crédito no fornecedor seller contra a conta transitória nova. |
| D074 | S09 | P139 | BRF+ para salvar os dados das contas contábeis. |
| D075 | S12 | T4.r1 | Objetivo da Remediação/Simplificação \| Simplificação |
| D076 | S12 | T4.r2 | Tipo de ampliação (Custom Field / BAdI / Exit / Enhancement Spot) \| BAdI/lógica CL_NFE_PRINT; function modules POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END; BAPI_ACC_DOCUMENT_POST. |
| D077 | S12 | T4.r3 | Lista de Transações/programas ou Jobs para Remediação/Simplificação \| ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC - / ELIMINAR / / ZFSD_ITF_BKF_ORDEM_VENDA_TRANS - fluxo atual de integração. |
| D078 | S12 | T4.r4 | Existe Fiorização de Transações ? se sim, informar lista, e qual catálogo do Fiori será utilizado , ou caso não / exista o perfil de acesso \| NA |
| D079 | S12 | T4.r5 | Objeto ou ponto de extensão conhecido \| VF01 - lógica vinculada à CL_NFE_PRINT, acionada após autorização da nota fiscal com status igual a 100. |
| D080 | S12 | T4.r6 | Pesquisa de alternativa standard \| A alternativa standard apresentada realiza contabilização apenas na visão cliente, sem geração de contabilização em conta de fornecedor. / O direcionamento seguirá para implementação v |
| D081 | S12 | T4.r7 | Validação na SCFD_REGISTRY, quando aplicável \| NA |
| D082 | S12 | T4.r8 | Campos envolvidos \| Status da nota fiscal; CNPJ; dados do cliente e do fornecedor; retorno de cliente ou fornecedor válido; dados da Ordem de Venda; dados da fatura do cliente; conta transitória; dados do fornecedor sel |
| D083 | S12 | T4.r9 | Regras e validações \| Aplicar o novo fluxo exclusivamente às operações de Boleto e PIX, sem alteração do processo de cartão; consultar e validar cliente e fornecedor por CNPJ, sem consulta por CPF; prosseguir após o ret |
| D084 | S12 | T4.r11 | Impactos em interfaces, relatórios ou apps \| Marketplace/Mirakl, Gateway KONG, SAP CPI, serviço OData ABAP/RAP, APIs Business Partner, Documento Contábil e Ordem de Venda, VF01, FI-AR, FI-AP, SD e SLG1. |
| D085 | S12 | T4.r12 | Cenários de exceção \| Status diferente de 100; erro no fluxo KONG/CPI/OData; erro na criação da Ordem de Venda; erro na emissão ou autorização da nota fiscal; erro na compensação; erro na criação da nota de crédito no f |
| D086 | S13 | T5.r1 | / / / / / / / BAdI CL_NFE_PRINT \| / / / / / / / Enhancement \| Após o faturamento e a autorização da nota fiscal na Sefaz, quando o status for igual a 100, deverá ser executada a lógica vinculada à CL_NFE_PRINT. A compe |
| D087 | S15 | T7.r1 | / VF01 \| / BADI/enhance ment \| Acionar a lógica vinculada à CL_NFE_PRINT para nota fiscal com status 100; executar POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END para compensação da fatura  |
| D088 | S16 | T8.r1 | / / VF01 - / BADI CL_NFE_PRINT \| Após o faturamento e a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100, a lógica vinculada à CL_NFE_PRINT deverá executar, em sequência, os function m |
| D089 | S18 | P190 | Objetivo do teste é validar o novo fluxo de contabilização da comissão do Marketplace exclusivamente para Boleto e PIX, sem alteração do processo de cartão. |
| D090 | S18 | P191 | Pré-requisito: período de Repasse, Comissão E Devolução/cancelamento fechado na Plataforma Marketplace, fornecedor seller e cliente existentes e nota fiscal aprovada na Sefaz. |
| D091 | S18 | P192 | Passos do teste: |
| D092 | S18 | P193 | Disparar o período de Repasse e Comissão na Plataforma Marketplace. |
| D093 | S18 | P194 | Acompanhar o fluxo Marketplace -> KONG -> SAP CPI -> serviço OData criado em ABAP/RAP. |
| D094 | S18 | P195 | Validar a consulta e a validação do cliente e do fornecedor por CNPJ na API Business Partner, sem consulta por CPF, incluindo o retorno da informação de cliente ou fornecedor válido; validar também as chamadas da API Doc |
| D095 | S18 | P196 | Validar contabilização da fatura no cliente. |
| D096 | S18 | P197 | Validar que a lógica vinculada à CL_NFE_PRINT seja acionada somente quando o status da nota fiscal for igual a 100. |
| D097 | S18 | P198 | Validar a execução sequencial de POSTING_INTERFACE_START, POSTING_INTERFACE_CLEARING e POSTING_INTERFACE_END e a compensação da fatura do cliente contra a conta transitória. |
| D098 | S18 | P199 | Validar que a BAPI_ACC_DOCUMENT_POST seja executada somente após o sucesso da compensação e crie a nota de crédito no fornecedor seller contra a mesma conta transitória. |
| D099 | S18 | P200 | Validar o abatimento da nota de crédito no pagamento do repasse ao seller. |
| D100 | S18 | P201 | Validar a manutenção da tabela ZTFID_MKTPL_LG para os documentos de repasse e devolução, tipos MP e MC. |
| D101 | S18 | P202 | Validar saldo zerado na conta transitória após os lançamentos a crédito e débito |
| D102 | S19 | P207 | Os dados do período de Repasse e Comissão devem percorrer o fluxo Marketplace -> KONG -> SAP CPI -> serviço OData criado em ABAP/RAP. |
| D103 | S19 | P208 | A API Business Partner deve consultar e validar cliente e fornecedor por CNPJ, sem consulta por CPF, e retornar a informação de cliente ou fornecedor válido. A API Documento Contábil e a API standard Sales Order devem se |
| D104 | S19 | P209 | A comissão será contabilizada no cliente e compensada com lançamento na transitória nova. |
| D105 | S19 | P210 | Após a autorização da nota fiscal na Sefaz, com status igual a 100, a fatura do cliente deve ser compensada contra a conta transitória e a nota de crédito deve ser criada no fornecedor seller contra a mesma conta. |
| D106 | S19 | P211 | O valor da nota de crédito deve ser abatido no pagamento do repasse ao seller. |
| D107 | S19 | P212 | A tabela ZTFID_MKTPL_LG deve manter os documentos de repasse e devolução, tipos MP e MC. |
| D108 | S20 | P216 | Utilizar os fluxos apresentados na seção Material Adicional como referência para os testes. |
| D109 | S22 | P227 | As invoices são geradas em dois ciclos, nos dias 05 e 20. A periodicidade da integração está indicada como 3 vezes ao dia. |
| D110 | S23 | P230 | Integração via SAP CPI e APIs. |
| D111 | S24 | P234 | Volumes mensais médios: R$ 1,9 milhão em comissão (2.000 NFs). |
| D112 | S25 | P238 | NA |
| D113 | S26 | P243 | Os erros dos processos de integração, incluindo KONG, SAP CPI e serviço OData ABAP/RAP, criação da Ordem de Venda, autorização da nota fiscal, compensação e criação da nota de crédito deverão ser gravados em log e monito |
| D114 | S26 | P244 | Em caso de erro na compensação, a BAPI_ACC_DOCUMENT_POST não deverá ser executada. |
| D115 | S27 | P249 | A ausência da solução mantém a necessidade da compensação entre cliente seller e fornecedor seller e gera falta de informação para gerir o negócio, perda de funcionalidade, mudança de procedimento e impacto relacionado à |
| D116 | S10 | T3.r4 | App Fiori \| TI e usuários \| NA |
| D117 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D118 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D119 | S14 | T6.r1 | / / / / / ZAP0069 \| / / / / ZRFI_MKTPLACE_COMPE NSACAO_RXC \| / / / Eliminar a transação/programa de compensação responsável pelo encontro de contas entre fornecedor seller e cliente seller. \| / / / / Transação/Progra  |
| D120 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D121 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D122 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D123 | S12 | T4.r7 | Validação na SCFD_REGISTRY, quando aplicável \| NA |
| D124 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D125 | S08 | P116 | Funções/classes atuais: ZFSD_CONSULTA_CLIENTE, ZFSD_CRIAR_IDOC_CLIENTE, ZFSD_CRIAR_IDOC_OV e zcl_itf_bkf_ordem_venda_trans1. |
| D126 | S08 | P116 | Funções/classes atuais: ZFSD_CONSULTA_CLIENTE, ZFSD_CRIAR_IDOC_CLIENTE, ZFSD_CRIAR_IDOC_OV e zcl_itf_bkf_ordem_venda_trans1. |
| D127 | S08 | P116 | Funções/classes atuais: ZFSD_CONSULTA_CLIENTE, ZFSD_CRIAR_IDOC_CLIENTE, ZFSD_CRIAR_IDOC_OV e zcl_itf_bkf_ordem_venda_trans1. |
| D128 | S08 | P114 | Integração atual: ZFSD_ITF_BKF_ORDEM_VENDA_TRANS. |
| D129 | S14 | T6.r1 | / / / / / ZAP0069 \| / / / / ZRFI_MKTPLACE_COMPE NSACAO_RXC \| / / / Eliminar a transação/programa de compensação responsável pelo encontro de contas entre fornecedor seller e cliente seller. \| / / / / Transação/Progra  |
| D130 | S01 | T1.r0 | / / / / / / Descrição \| O GAP FI-021 trata da alteração do processo de contabilização da comissão do Marketplace exclusivamente para as operações realizadas por Boleto e PIX. / As operações realizadas por cartão não faz |
| D131 | S04 | P046 | -ZTFID_MKTPL_LG - manutenção dos dados dos documentos de repasse e devolução, tipos MP e MC, e monitoramento do processo. -ZAP0069 / ZRFI_MKTPLACE_COMPENSACAO_RXC - transação e programa de compensação que serão eliminado |
| A001 | S05 | P059, P060, P061, P062 | Após o faturamento e a autorização da nota fiscal na Sefaz, quando o status da nota fiscal for igual a 100, a lógica vinculada à BAdI CL_NFE_PRINT deverá executar, em sequência, os seguintes function modules: POSTING_INT |
| A002 | S05 | P065 | A compensação da fatura do cliente e a criação da nota de crédito no fornecedor dependerão da autorização da nota fiscal na Sefaz e do status igual a 100. Para status diferente de 100, essas etapas não deverão ser execut |
| A003 | S05 | P071 | Em caso de erro na compensação da fatura do cliente, a BAPI_ACC_DOCUMENT_POST não deverá ser executada. |
| A004 | S05 | P066 | Após a compensação da fatura do cliente e a contabilização da nota de crédito no fornecedor seller, a conta transitória deverá apresentar saldo zerado. |
| A005 | S07 | P096 | Quando o status da nota fiscal for igual a 100, é acionada a lógica vinculada à BAdI CL_NFE_PRINT. |
| AUTO001 | S10 | T3.r2 | BRF+ \| Somente TI \| 1 - Se tiver alguma definição de Hard Code simples ou lista (TVARV), deverá usar uma única BRF+ (ZTD_LMB_PARAMETROS) / / / 2 - Se tiver referência as tabelas de parâmetros ZTXXC_PARA_1 e ZTXXC_PARA_ |
| AUTO002 | S10 | T3.r2 | BRF+ \| Somente TI \| 1 - Se tiver alguma definição de Hard Code simples ou lista (TVARV), deverá usar uma única BRF+ (ZTD_LMB_PARAMETROS) / / / 2 - Se tiver referência as tabelas de parâmetros ZTXXC_PARA_1 e ZTXXC_PARA_ |
| AUTO003 | S10 | T3.r2 | BRF+ \| Somente TI \| 1 - Se tiver alguma definição de Hard Code simples ou lista (TVARV), deverá usar uma única BRF+ (ZTD_LMB_PARAMETROS) / / / 2 - Se tiver referência as tabelas de parâmetros ZTXXC_PARA_1 e ZTXXC_PARA_ |

### Mapa de seções da EF

| Seção | Caminho |
|---|---|
| S00 | Capa e cabeçalho |
| S01 | Resumo do Desenvolvimento |
| S02 | Detalhamento da Especificação Funcional |
| S03 | Detalhamento da Especificação Funcional > Objetivo, justificativa e processo de negócio atendido. |
| S04 | Detalhamento da Especificação Funcional > Processos Relacionados (Transações do Sistema S4HANA) |
| S05 | Detalhamento da Especificação Funcional > Regras de Negócio |
| S06 | Detalhamento da Especificação Funcional > Premissas/Acordos do GAP |
| S07 | Detalhamento da Especificação Funcional > Fluxo do Processo do GAP |
| S08 | Detalhamento da Especificação Funcional > Sistemas, ambientes e objetos SAP impactados. |
| S09 | Detalhamento da Especificação Funcional > Novos Objetos |
| S10 | Detalhamento da Especificação Funcional > Material Adicional |
| S11 | Desenvolvimentos |
| S12 | Desenvolvimentos > Enhancements |
| S13 | Desenvolvimentos > Enhancements - Implementação de Ampliações SAP (CMOD/BADI) |
| S14 | Desenvolvimentos > Transações/Prog/Jobs/Forms/Aplicações Fiori – Transações, programas de demais objetos a serem remediados e simplificados. |
| S15 | Desenvolvimentos > Enhancements – Objeto Standard SAP com ponto de ampliação implícito |
| S16 | Desenvolvimentos > Enhancements – Regra de negócio |
| S17 | Script de Testes |
| S18 | Script de Testes > Descrição Funcional do Procedimento de Testes(obrigatório) |
| S19 | Script de Testes > Descrição Funcional dos Resultados Esperados Após o Teste(obrigatório) |
| S20 | Script de Testes > Material Adicional para os Testes |
| S21 | Informações Complementares |
| S22 | Informações Complementares > Periodicidade de Execução |
| S23 | Informações Complementares > Tipo de Execução |
| S24 | Informações Complementares > Volumetria e frequência de execução. |
| S25 | Informações Complementares > Janela para Execução |
| S26 | Informações Complementares > Tratamento de erros, logs, monitoramento e reprocessamento. |
| S27 | Informações Complementares > Processo Crítico |
| S28 | Homologação |
