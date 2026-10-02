# SD-034 — Pacote de Entrada para Descoberta SAP

## Controle do pacote

| Campo | Valor |
|---|---|
| Demanda | SD-034 |
| Projeto | MOVE2S/4 (Leroy Merlin) |
| EF | ef_sd034.docx |
| Versão informada | V2 |
| Última versão no histórico | V1 |
| Estado de aprovação | APROVADA |
| Anexos autorizados | nenhum |
| Gate | **VALIDO_COM_RESSALVAS** |
| Gerado em | 2026-09-27 00:48 UTC |
| Consultas SAP executadas | nenhuma (Etapa 1) |

## Gate

**VALIDO_COM_RESSALVAS**

- Nenhum critério bloqueante identificado.
- 7 ressalva(s) não bloqueante(s) devem ser tratadas na Etapa 2 ou com o funcional.

## Resumo do negócio

Remediar no S/4HANA a trava de precificação da VKP5 (calendário, horário e usuários de exceção) e substituir o monitor ZRMM_RECALC_PR_BLOQ por um app Fiori.

### Identificação, objetivo e componentes

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| I001 | GAP SD-034 — Trava de datas na Precificação VKP5 | FATO_DA_EF | ALTA | S00 · T0.r4 |
| I002 | Remediação/Simplificação com Enhancement e App Fiori | FATO_DA_EF | ALTA | S00 · P015 |
| I003 | Remediar no S/4 o controle de bloqueio da precificação existente no ECC | FATO_DA_EF | ALTA | S03 · P038 |
| I004 | Evitar discrepância de preços PDV x SELF x Etiqueta | FATO_DA_EF | ALTA | S01 · T2.r11 |
| I005 | Validações de precificação na VKP5 (BAdIs, exits, enhancement) **[REMEDIACAO]** origem: `ZIMMM_SPC_POSTING_CO` | FATO_DA_EF | ALTA | S05 · P122 |
| I006 | App Fiori de administração dos parâmetros de bloqueio **[NOVO]** âncora: Monitor Administrador de Preços | FATO_DA_EF | ALTA | S05 · P110 |

## Escopo da descoberta

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| I013 | Aba Determinação Margem/Percentual não será utilizada | FATO_DA_EF | ALTA | S05 · P081 |
| I014 | Simulador MM-054-FIO também deve considerar as travas | FATO_DA_EF | ALTA | S08 · P194 |
| I015 | SAP ECC (origem) e SAP S/4HANA (destino) | FATO_DA_EF | ALTA | S03 · P038 |

## Requisitos e regras

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| I007 | No ECC a validação das datas é controlada pela ZRMM_RECALC_PR_BLOQ | FATO_DA_EF | ALTA | S05 · P047 |
| I008 | Parâmetros mantidos por app Fiori simplificado | FATO_DA_EF | ALTA | S06 · P172 |
| I009 | Usuário que mantém preços pela VKP5 | FATO_DA_EF | ALTA | S07 · P178 |
| I010 | Bloquear gravação se a data de início for data bloqueada | FATO_DA_EF | ALTA | S05 · P087 |
| I011 | Data final de vigência deve ser 31.12.9999 | FATO_DA_EF | ALTA | S05 · P114 |
| I012 | Usuários de exceção ignoram data e horário | FATO_DA_EF | ALTA | S05 · P103 |

## Referências técnicas declaradas

### No escopo ou indefinidas

| ID | Valor original | Tipo | Escopo | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|---|---|---|
| I016 | `VKP5` | TRANSACAO | INCLUIDO | Transação de precificação | FATO_DA_EF | ALTA | S04 · P043 |
| I017 | `ZRMM_RECALC_PR_BLOQ` | TRANSACAO | INCLUIDO | Monitor do administrador de preços no ECC | FATO_DA_EF | ALTA | S05 · P050 |
| I018 | `ZRMM_CADASTRO_PRECO_ADMINISTR` | PROGRAMA | INCLUIDO | Programa do monitor no ECC | FATO_DA_EF | ALTA | S05 · P051 |
| I019 | `ZTMMC_STAT_PRECO` | TABELA | INCLUIDO | Tabela de parâmetros de status | FATO_DA_EF | ALTA | S05 · P052 |
| I020 | `ZCL_IM_SPC_SEL_CHECK` | CLASSE | INCLUIDO | Implementação da BAdI de materiais AVS | FATO_DA_EF | ALTA | S05 · P126 |
| I021 | `ZFMM_CHECK_CONDITION_DATE` | FUNCAO | INCLUIDO | Função de checagem de data da condição | FATO_DA_EF | ALTA | S05 · P133 |
| I022 | `WV001F01` | INCLUDE | INCLUIDO | Include do enhancement da tela de seleção | FATO_DA_EF | ALTA | S05 · P135 |
| I023 | `SPC_SEL_CHECK` | BADI | INCLUIDO | BAdI de exclusão de itens do esquema | FATO_DA_EF | ALTA | S05 · P124 |
| I025 | `VK11` | TRANSACAO | INDEFINIDO | Manutenção de condições | PONTO_A_CONFIRMAR | BAIXA | S05 · P087 |
| AUTO001 | `EXIT_SAPLMEKO_001` | EXIT | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P153 |
| AUTO002 | `EXIT_SAPLWR04_001` | EXIT | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P150 |
| AUTO003 | `EXIT_SAPLWVK0_001` | EXIT | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P140 |
| AUTO004 | `EXIT_SAPLWVK1_003` | EXIT | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P143 |
| AUTO005 | `IF_EX_SPC_POSTING_CONTROL~CALC_ITEM_POST_CHECK` | METODO | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P131 |
| AUTO006 | `LWR04F01` | INCLUDE | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P150 |
| AUTO007 | `RV61AFZA` | INCLUDE | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P157 |
| AUTO008 | `RV61AFZB` | INCLUDE | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P156 |
| AUTO009 | `SMOD_LWVK1001` | EXIT | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P155 |
| AUTO010 | `SMOD_LWVK1002` | EXIT | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P154 |
| AUTO011 | `ZCLSD_EXIT_SAPLWVK1_003` | CLASSE | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P146 |
| AUTO012 | `ZCLSD_ZESD_PRECO_LEROY` | CLASSE | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P137 |
| AUTO013 | `ZMGV_GENERATED_RWVKP007` | OUTRO | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P137 |
| AUTO014 | `ZTMMC_STAT_PRECO-IDENT` | CAMPO_TABELA | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P059 |
| AUTO015 | `ZTMMC_STAT_PRECO-ZHORALT` | CAMPO_TABELA | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P061 |
| AUTO016 | `ZTMMC_STAT_PRECO-ZUSERLB1` | CAMPO_TABELA | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P061 |
| AUTO017 | `ZTMMC_STAT_PRECO-ZVDT_VDT` | CAMPO_TABELA | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P058 |
| AUTO018 | `ZTMMC_STAT_PRECO-ZVD_HORA` | CAMPO_TABELA | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P060 |
| AUTO019 | `ZTMMD_TOPAGEM_P` | OUTRO | INDEFINIDO | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P150 |

### Fora do escopo (a Etapa 2 não deve pesquisar)

| ID | Valor original | Tipo | Escopo | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|---|---|---|
| I024 | `EXIT_SAPLMEKO_002` | EXIT | EXCLUIDO | Exit de condições de compra — fora do escopo | FATO_DA_EF | ALTA | S05 · P152 |

## Âncoras funcionais

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| I027 | Monitor Administrador de Preços | FATO_DA_EF | ALTA | S05 · P047 |

## Interfaces, dados e campos

_Nenhum item extraído._

## Cenários e testes

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| I028 | Procedimento de teste funcional descrito | PONTO_A_CONFIRMAR | BAIXA | S18 · — |

## Plano solicitado para a Etapa 2

| ID | Objetivo | Alvos | Tipo de verificação | Prioridade |
|---|---|---|---|---|
| V01 | Confirmar implementações ativas das BAdIs no S/4 | I020, I023 | existência de objeto | ALTA |
| V02 | Ler a função de checagem de data | I021 | leitura de código | ALTA |

Viabilidade sem varredura irrestrita: **sim** — A EF nomeia BAdIs, exits, classes, função e tabela.

## Pontos a confirmar

| ID | Descrição | Classificação | Confiança | Fonte |
|---|---|---|---|---|
| I025 | Manutenção de condições | PONTO_A_CONFIRMAR | BAIXA | S05 · P087 |
| I026 | 'Aplicação Fiori simplificada' não define o que é simplificado | ENTENDIMENTO | MEDIA | S03 · P040 |
| I028 | Procedimento de teste funcional descrito | PONTO_A_CONFIRMAR | BAIXA | S18 · — |
| AUTO001 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P153 |
| AUTO002 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P150 |
| AUTO003 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P140 |
| AUTO004 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P143 |
| AUTO005 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P131 |
| AUTO006 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P150 |
| AUTO007 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P157 |
| AUTO008 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P156 |
| AUTO009 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P155 |
| AUTO010 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P154 |
| AUTO011 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P146 |
| AUTO012 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P137 |
| AUTO013 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P137 |
| AUTO014 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P059 |
| AUTO015 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P061 |
| AUTO016 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P061 |
| AUTO017 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P058 |
| AUTO018 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P060 |
| AUTO019 | Identificador técnico presente na EF e não extraído pela IA. | PONTO_A_CONFIRMAR | BAIXA | S05 · P150 |

### Ressalvas do gate

- 21 item(ns) classificados como PONTO_A_CONFIRMAR.
- 1 ambiguidade(s) registrada(s) na EF.
- Valor 'VK11' não aparece no trecho citado.
- Trecho de origem insuficiente para rastreabilidade ('x').
- 19 identificador(es) técnico(s) presentes na EF não foram extraídos pela IA e foram incluídos automaticamente como PONTO_A_CONFIRMAR (escopo a confirmar): EXIT_SAPLMEKO_001, EXIT_SAPLWR04_001, EXIT_SAPLWVK0_001, EXIT_SAPLWVK1_003, IF_EX_SPC_POSTING_CONTROL~CALC_ITEM_POST_CHECK, LWR04F01, RV61AFZA, RV61AFZB, SMOD_LWVK1001, SMOD_LWVK1002, ZCLSD_EXIT_SAPLWVK1_003, ZCLSD_ZESD_PRECO_LEROY, ZMGV_GENERATED_RWVKP007, ZTMMC_STAT_PRECO-IDENT, ZTMMC_STAT_PRECO-ZHORALT, ZTMMC_STAT_PRECO-ZUSERLB1, ZTMMC_STAT_PRECO-ZVDT_VDT, ZTMMC_STAT_PRECO-ZVD_HORA, ZTMMD_TOPAGEM_P.
- Versão informada (V2) difere da última versão do histórico de revisão (V1).
- A seção 'Detalhamento da Especificação Funcional > Regras de Negócio' contém 11 imagem(ns) (ex.: esboços de tela) cujo conteúdo não foi lido em texto.

## Limitações

- Nenhuma consulta a SAP, BTP, CPI ou Workflow foi executada nesta etapa.
- Existência de objetos e transações não foi confirmada; é objetivo da Etapa 2.
- A seção 'Detalhamento da Especificação Funcional > Regras de Negócio' contém 11 imagem(ns) (ex.: esboços de tela) cujo conteúdo não foi lido em texto.

## Rastreabilidade

Cada item acima referencia a seção e a localização na EF. Trechos de origem:

| ID | Seção | Localização | Trecho de origem |
|---|---|---|---|
| I001 | S00 | T0.r4 | ID GAP: SD-034 |
| I002 | S00 | P015 | Remediação/Simplificação |
| I003 | S03 | P038 | Implementar no SAP S/4HANA a remediação da solução de controle de bloqueio da precificação |
| I004 | S01 | T2.r11 | Sem a trava, ocorrerá discrepância de preços entre PDV X SELF X Etiqueta |
| I005 | S05 | P122 | Os objetos que deverão ser remediados são: |
| I006 | S05 | P110 | deverá ser substituída por uma aplicação Fiori para administração dos parâmetros de bloqueio da precificação |
| I007 | S05 | P047 | Atualmente no ECC a validação das datas de precificação é controlada através da transação ZRMM_RECALC_PR_BLOQ |
| I008 | S06 | P172 | deverão ser mantidos por meio de uma aplicação Fiori simplificada |
| I009 | S07 | P178 | O usuário inicia o processo de manutenção de preços por meio da transação VKP5. |
| I010 | S05 | P087 | o sistema deverá impedir a gravação dos dados e apresentar mensagem de erro ao usuário |
| I011 | S05 | P114 | Quando o usuário informar valor diferente de 31.12.9999 para a data final de vigência |
| I012 | S05 | P103 | Os usuários cadastrados como exceção deverão ignorar as validações de data e horário |
| I013 | S05 | P081 | mas essa funcionalidade não será utilizada no S4 |
| I014 | S08 | P194 | Existe também um GAP para desenvolvimento de um simulador (MM-054-FIO) |
| I015 | S03 | P038 | remediação da solução de controle de bloqueio da precificação atualmente existente no SAP ECC |
| I016 | S04 | P043 | suportado pela transação VKP5 |
| I017 | S05 | P050 | Tcode ECC: ZRMM_RECALC_PR_BLOQ |
| I018 | S05 | P051 | Programa ECC: ZRMM_CADASTRO_PRECO_ADMINISTR |
| I019 | S05 | P052 | Tabela ECC: ZTMMC_STAT_PRECO |
| I020 | S05 | P126 | ZCL_IM_SPC_SEL_CHECK |
| I021 | S05 | P133 | ZFMM_CHECK_CONDITION_DATE |
| I022 | S05 | P135 | Enhancement no include WV001F01, no form AT-SELECTION-SCREEN |
| I023 | S05 | P124 | BAdI SPC_SEL_CHECK |
| I024 | S05 | P152 | EXIT_SAPLMEKO_002 |
| I025 | S05 | P087 | Durante a manutenção de preços através da transação VKP5 |
| I026 | S03 | P040 | deverá ser disponibilizada uma aplicação Fiori simplificada |
| I027 | S05 | P047 | (Monitor Administrador de Preços) |
| I028 | S18 | — | x |
| AUTO001 | S05 | P153 | EXIT_SAPLMEKO_001: utilizada na movimentação ou substituição de campos da estrutura KOMK para a determinação das sequências de acesso do processo de compras; |
| AUTO002 | S05 | P150 | EXIT_SAPLWR04_001 / enhancement no include LWR04F01: relacionado à validação de dados da tabela ZTMMD_TOPAGEM_P; |
| AUTO003 | S05 | P140 | EXIT_SAPLWVK0_001 |
| AUTO004 | S05 | P143 | EXIT_SAPLWVK1_003 |
| AUTO005 | S05 | P131 | Método: IF_EX_SPC_POSTING_CONTROL~CALC_ITEM_POST_CHECK |
| AUTO006 | S05 | P150 | EXIT_SAPLWR04_001 / enhancement no include LWR04F01: relacionado à validação de dados da tabela ZTMMD_TOPAGEM_P; |
| AUTO007 | S05 | P157 | Include RV61AFZA, formUSEREXIT_PRICING_RULE: contém regras de preenchimento de campos conforme o esquema de cálculo processado; |
| AUTO008 | S05 | P156 | EXIT RV61AFZB: relacionada à inclusão do código de imposto utilizado no esquema de cálculo de vendas; |
| AUTO009 | S05 | P155 | SMOD_LWVK1001: utilizada na movimentação ou substituição de campos da estrutura KOMK para a determinação das sequências de acesso do processo de vendas; |
| AUTO010 | S05 | P154 | SMOD_LWVK1002: utilizada na movimentação ou substituição de campos da estrutura KOMP para a determinação das sequências de acesso do processo de vendas; |
| AUTO011 | S05 | P146 | ZCLSD_EXIT_SAPLWVK1_003, no método USER_EXIT_OLD_CODE, chamado durante o fluxo da exit. Para atendimento aos requisitos definidos neste gap, deverão ser mantidas no SAP S/4HANA as funcionalidades aplicáveis ao tratamento |
| AUTO012 | S05 | P137 | A implementação possui relação com a classe ZCLSD_ZESD_PRECO_LEROY, chamada no fluxo do enhancement ZMGV_GENERATED_RWVKP007, responsável por controles relacionados à liberação de preços e à validação de datas. |
| AUTO013 | S05 | P137 | A implementação possui relação com a classe ZCLSD_ZESD_PRECO_LEROY, chamada no fluxo do enhancement ZMGV_GENERATED_RWVKP007, responsável por controles relacionados à liberação de preços e à validação de datas. |
| AUTO014 | S05 | P059 | Campo Calendário Cálculo Preço LMB : ZTMMC_STAT_PRECO-IDENT |
| AUTO015 | S05 | P061 | Campo “Horário Limite para Precificação”: ZTMMC_STAT_PRECO-ZHORALT Campo “Usuário Liberado Calculo 1”: ZTMMC_STAT_PRECO-ZUSERLB1 |
| AUTO016 | S05 | P061 | Campo “Horário Limite para Precificação”: ZTMMC_STAT_PRECO-ZHORALT Campo “Usuário Liberado Calculo 1”: ZTMMC_STAT_PRECO-ZUSERLB1 |
| AUTO017 | S05 | P058 | Campo “Ativa Verificação de Calendário Preço: ZTMMC_STAT_PRECO-ZVDT_VDT |
| AUTO018 | S05 | P060 | Campo “Ativa Verificação Horário”: ZTMMC_STAT_PRECO-ZVD_HORA |
| AUTO019 | S05 | P150 | EXIT_SAPLWR04_001 / enhancement no include LWR04F01: relacionado à validação de dados da tabela ZTMMD_TOPAGEM_P; |

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
| S11 | Detalhamento da Especificação Funcional > Material Adicional > TVARV, BRF+ e Tabelas de Parâmetros |
| S12 | Desenvolvimentos |
| S13 | Desenvolvimentos > Enhancements |
| S14 | Desenvolvimentos > Enhancements - Implementação de Ampliações SAP (CMOD/BADI) |
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
