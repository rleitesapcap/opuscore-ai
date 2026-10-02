<!-- Capgemini SAP AI — Gerador de ET | Projeto MOVE2S4 | Gerado em 22/09/2026 20:00 -->
<!-- Alvo: SAP S/4HANA 2025 (Private Edition) -->


# Especificação Técnica — Projeto MOVE2S/4

| Campo | Valor |
|-------|-------|
| **Autor** | Capgemini AI Generate ET - Brazil |
| **Funcional** | Fernando Romero |
| **Analista TI** | Capgemini IA Generativa |
| **ID GAP** | SD-034 |
| **Descrição GAP** | Trava de datas na Precificação VKP5 |
| **Versão** | 1.0 |
| **Data** | 22/09/2026 |

## 1. Identificação dos Objetos Técnicos Envolvidos

- **Transações envolvidas:** Não informado

**Objetos técnicos envolvidos:**

- zcl_im_immm_spc_posting_co — Classe (Global) — Novo
- zcl_im_spc_sel_check — Classe (Global) — Novo
- zclsd_exit_saplwvk1_003 — Classe (Global) — Novo
- zclsd_zesd_precos_leroy — Classe (Global) — Novo
- zclsd_zesd_precos_leroy_6630 — Classe (Global) — Novo
- zfmm_check_condition_date — Function Module — Novo
- zrmm_cadastro_preco_administr — Report/Programa — Novo
- zrmm_cadastro_preco_top — Top Include — Novo
- zrmm_cadastro_preco_1000_pbo — Screen Include (PBO/PAI) — Novo
- zrmm_cadastro_preco_1001_pai — Screen Include (PBO/PAI) — Novo
- zrmm_cadastro_preco_1000_f01 — Form/Rotina Include — Novo
- zrmm_cadastro_preco_1001_f01 — Form/Rotina Include — Novo
- zrmm_cadastro_preco_1002_f01 — Form/Rotina Include — Novo
- zrmm_cadastro_preco_1003_f01 — Form/Rotina Include — Novo
- zrmm_cadastro_preco_1004_f01 — Form/Rotina Include — Novo
- zrmm_cadastro_preco_1004_pbo — Form/Rotina Include — Novo
- zrmm_cadastro_preco_9000_f01 — Form/Rotina Include — Novo
- zrmm_cadastro_preco_f00 — Form/Rotina Include — Novo
- zemm_cadastro_preco_1001_scr — Include (genérico) — Novo
- zesd_prc_transf_praca_exp — Include (genérico) — Novo
- zesd_precos_leroy — Include (genérico) — Novo
- zrmm_cadastro_preco_1002_pbo — Include (genérico) — Novo
- zrmm_cadastro_preco_1003_pbo — Include (genérico) — Novo
- zxvkpu03 — Include (genérico) — Novo

## 2. Detalhamento Técnico

### zcl_im_immm_spc_posting_co.aclass

- **Objetivo do desenvolvimento:** Classe de implementação de BAdI que controla a gravação de preços na transação VKP5 (precificação). Implementa o enhancement IF_EX_SPC_POSTING_CONTROL para aplicar validações de data e controles específicos durante o processo de cálculo de preços de venda, conforme GAP SD-034 que trata da trava de datas na precificação.
- **Nome do Objeto:** zcl_im_immm_spc_posting_co.aclass
- **Tipo do Objeto:** Classe (Global)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

A classe implementa o BAdI SPC_POSTING_CONTROL através da interface IF_EX_SPC_POSTING_CONTROL para controlar a gravação de preços na VKP5. O método calc_item_post_check é executado durante o processo de cálculo de preços, validando se a transação é VKP5 e se não está sendo executada pelo programa de cálculo automático. Quando detecta que será gravado um novo documento de preço (flag vkabs = 'X'), aciona validações específicas de data através de função customizada.

**Rotinas e métodos**

O método principal calc_item_post_check executa a lógica de controle verificando primeiro se está na transação VKP5 e não no programa automático. Em seguida, valida se o centro está preenchido e se o flag de gravação está ativo. Quando essas condições são atendidas, chama a função ZFMM_CHECK_CONDITION_DATE para verificar se a data de validade informada corresponde ao dia útil correto, registrando divergências em variáveis de log quando necessário.

- IF_EX_SPC_POSTING_CONTROL~CALC_ITEM_POST_CHECK — método principal que executa validações de data durante cálculo de preços

**Regra de negócio aplicada**

A regra implementa controle de datas na precificação VKP5, garantindo que as condições sejam registradas com datas de validade corretas conforme calendário de dias úteis. Quando o usuário informa uma data diferente do dia útil calculado pelo sistema, a informação é registrada em log para auditoria. Esta validação é aplicada apenas quando o usuário marca explicitamente para gravar um novo documento de cálculo de preço de venda.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zcl_im_spc_sel_check.aclass

- **Objetivo do desenvolvimento:** A classe ZCL_IM_SPC_SEL_CHECK implementa a interface IF_EX_SPC_SEL_CHECK como um enhancement point para validações de seleção no processo de precificação VKP5. Sua função principal é controlar quais materiais podem ser incluídos no cálculo de preços, aplicando regras de negócio específicas relacionadas à trava de datas na precificação conforme definido no GAP SD-034.
- **Nome do Objeto:** zcl_im_spc_sel_check.aclass
- **Tipo do Objeto:** Classe (Global)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

A classe implementa um enhancement point para o módulo SPC, focando em validações de seleção durante o processo de precificação. A implementação utiliza a interface padrão SAP IF_EX_SPC_SEL_CHECK para interceptar e validar itens antes do cálculo de preços.

**Rotinas e métodos**

O método principal check_calc_item contém a lógica de validação, verificando autorizações e aplicando regras específicas para materiais AVS e listas de preço. Os demais métodos da interface estão declarados mas não implementados.

- IF_EX_SPC_SEL_CHECK~CHECK_CALC_ITEM — Validação principal de itens de cálculo com controle de autorização e regras de negócio
- IF_EX_SPC_SEL_CHECK~FILTER_ORGLEVELS — Método declarado mas não implementado para filtragem de níveis organizacionais

**Regra de negócio aplicada**

A implementação aplica controles específicos para o processo de precificação VKP5, excluindo materiais AVS quando o usuário não possui autorização adequada e controlando o uso de materiais em listas de preço específicas. Quando a condição de cálculo é 'Z7', o sistema atualiza campos específicos de preço conforme definido nas regras de negócio.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Objetos de autorização identificados no código:

Origem · Objeto · Campos
AUTHORITY-CHECK · ZMM_AVS_VK · ACTVT='01'

### zclsd_exit_saplwvk1_003.aclass

- **Objetivo do desenvolvimento:** A classe zclsd_exit_saplwvk1_003 implementa um user exit customizado para o programa SAPLWVK1, especificamente para a transação VKP5 de precificação. A classe controla regras de negócio relacionadas à trava de datas na precificação, permitindo que usuários específicos alterem preços fora das datas normalmente permitidas, além de realizar cálculos complexos de condições de preço, impostos e conversões de unidades de medida.
- **Nome do Objeto:** zclsd_exit_saplwvk1_003.aclass
- **Tipo do Objeto:** Classe (Global)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

A classe implementa um user exit para a transação VKP5 com controle de ativação através da interface YIFXX_CHECK_EXIT. O método principal user_exit_execute verifica se o exit está ativo antes de executar a lógica customizada. A implementação permite controle granular sobre regras de precificação com exceções para usuários específicos.

**Rotinas e métodos**

O método user_exit_execute atua como controlador principal, verificando ativação e delegando para user_exit_old_code. Este último contém toda a lógica de negócio, incluindo validações de data, cálculos de preço, processamento de condições e conversões de unidade. O método yifxx_check_exit~check_active_exit implementa a interface mas está vazio.

- user_exit_execute — Controlador principal que verifica ativação do exit
- user_exit_old_code — Processa toda a lógica de precificação e validações
- yifxx_check_exit~check_active_exit — Implementação vazia da interface de controle

**Regra de negócio aplicada**

A regra implementa trava de datas na precificação VKP5, onde usuários normais só podem alterar preços dentro de datas permitidas pelo calendário de trabalho, mas usuários específicos têm exceção total. O sistema processa diferentes tipos de condições de preço (ICMI, ZPB0, ZPC1, ZPC2, ZBHT), calcula impostos ICMS quando necessário, e realiza conversões de unidades de medida. Também duplica condições ZPB0 em ZPB1 e processa preços para e-commerce.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zclsd_zesd_precos_leroy.aclass

- **Objetivo do desenvolvimento:** A classe ZCLSD_ZESD_PRECOS_LEROY implementa um user exit customizado para controlar a precificação na transação VKP5, aplicando validações específicas de datas conforme regras de negócio da Leroy Merlin. A classe atua como uma trava de precificação que verifica datas de início e fim de validade dos preços, diferenciando o comportamento entre usuários master e usuários comuns.
- **Nome do Objeto:** zclsd_zesd_precos_leroy.aclass
- **Tipo do Objeto:** Classe (Global)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

A classe implementa um user exit para controle de precificação na transação VKP5, aplicando validações de data baseadas no perfil do usuário e organização de vendas. A estrutura utiliza a interface YIFXX_CHECK_EXIT para padronizar a implementação de exits customizados.

**Rotinas e métodos**

O método principal user_exit_execute coordena a execução das validações, chamando o código legado e a verificação de data fim. O método user_exit_old_code implementa a validação de data de início com diferenciação entre usuários master e comuns. O método verifica_data_fim controla a data fim baseada em parâmetros da organização de vendas.

- USER_EXIT_EXECUTE — coordena execução das validações de precificação
- USER_EXIT_OLD_CODE — valida data início com diferenciação de usuários
- VERIFICA_DATA_FIM — controla data fim por organização de vendas
- YIFXX_CHECK_EXIT~CHECK_ACTIVE_EXIT — método de interface não implementado

**Regra de negócio aplicada**

A regra implementa uma trava de precificação que diferencia o comportamento entre usuários master/liberados e usuários comuns. Para usuários master, exibe apenas mensagem informativa quando a data não é válida, permitindo prosseguir. Para usuários comuns, bloqueia a operação com mensagem de erro. Adicionalmente, controla a data fim através de parâmetros configuráveis por organização de vendas.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zclsd_zesd_precos_leroy_6630.aclass

- **Objetivo do desenvolvimento:** A classe ZCLSD_ZESD_PRECOS_LEROY_6630 é um componente de apoio para o GAP SD-034 que implementa controle de ativação para funcionalidades relacionadas à transação VKP5 (precificação). A classe fornece um método para verificar se determinadas funcionalidades de liberação de preços estão ativas através de parametrização.
- **Nome do Objeto:** zclsd_zesd_precos_leroy_6630.aclass
- **Tipo do Objeto:** Classe (Global)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

A classe implementa funcionalidade de controle de ativação para o processo de precificação VKP5. Utiliza constantes para identificadores de parâmetros e fornece método estático para verificação de status. A implementação segue padrões orientados a objetos com classe final e método público.

**Rotinas e métodos**

O método CHECK_IS_ACTIVE é responsável por verificar se a funcionalidade está ativa através da consulta de parâmetros configuráveis. Utiliza a classe ZCL_PARAMETROS para obter configurações e retorna flag indicando o status de ativação.

- CHECK_IS_ACTIVE — Verifica se funcionalidade de liberação VKP5 está ativa através de parâmetros

**Regra de negócio aplicada**

A regra implementa controle de ativação para liberação de exceção total na precificação VKP5. Permite que usuários autorizados alterem preços para qualquer data quando a funcionalidade estiver ativa. O controle é realizado através de parametrização flexível usando ranges de valores.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zfmm_check_condition_date.asfunc

- **Objetivo do desenvolvimento:** O módulo de função ZFMM_CHECK_CONDITION_DATE implementa uma validação de datas para o processo de precificação VKP5, verificando se a data informada está dentro das regras de negócio estabelecidas e calculando o próximo dia útil válido conforme calendário configurado.
- **Nome do Objeto:** zfmm_check_condition_date.asfunc
- **Tipo do Objeto:** Function Module
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

A função recebe uma data de condição (VKKAB) e usuário, validando se a data está conforme regras de negócio configuradas. Calcula o próximo dia útil válido considerando calendário e horários limite, retornando a data ajustada e informações de parametrização.

**Rotinas e métodos**

A lógica principal utiliza um loop DO para ajustar iterativamente a data até encontrar um dia útil válido. Consulta a tabela ZTMMC_STAT_PRECO para obter parametrizações ativas e ZTSDD_USERS_LIB para informações de usuários liberados.

- WRF_PSCD_GET_NEXT_WORKDAY — Calcula próximo dia útil conforme calendário configurado
- SELECT ZTMMC_STAT_PRECO — Obtém parametrização de validação de datas ativa
- SELECT ZTSDD_USERS_LIB — Carrega tabela de usuários liberados

**Regra de negócio aplicada**

Implementa trava de precificação que impede criação de condições em datas passadas ou em horários não permitidos. Se a data informada for menor ou igual à data atual, ajusta para o dia seguinte. Considera horário limite configurado para determinar se deve pular para o próximo dia útil.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_administr.asprog

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_administr é um programa ABAP que implementa um monitor para administrar atualizações de preços, relacionado ao GAP SD-034 que trata da trava de datas na precificação VKP5. O programa utiliza múltiplas telas (1000-1005, 9000) para permitir inclusão e alteração de dados para cálculo de preços.
- **Nome do Objeto:** zrmm_cadastro_preco_administr.asprog
- **Tipo do Objeto:** Report/Programa
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O programa implementa um monitor de administração de preços através de arquitetura modular baseada em includes. Utiliza múltiplas telas (1000, 1001, 1002, 1003, 1004, 9000) para diferentes funcionalidades de cadastro e manutenção de preços. A estrutura segue padrão SAP com separação clara entre lógica de apresentação (PBO), processamento de entrada (PAI) e rotinas específicas (F01).

**Rotinas e métodos**

O programa utiliza includes específicos para organizar a lógica de cada tela, com rotinas PBO para preparação da tela, PAI para processamento de entrada do usuário e F01 para rotinas específicas de cada funcionalidade. O include TOP contém declarações globais e o F00 contém rotinas comuns a todo o programa.

- ZRMM_CADASTRO_PRECO_TOP — Declarações globais e variáveis do programa
- ZRMM_CADASTRO_PRECO_F00 — Rotinas comuns utilizadas por todas as telas
- ZRMM_CADASTRO_PRECO_1000_* — Lógica da tela principal 1000
- ZRMM_CADASTRO_PRECO_1001_* — Lógica da tela de cadastro 1001
- ZRMM_CADASTRO_PRECO_9000_* — Lógica da tela de status/mensagens 9000

**Regra de negócio aplicada**

O programa implementa regras de negócio relacionadas ao controle de datas na precificação VKP5, conforme especificado no GAP SD-034. Permite inclusão e alteração de dados para cálculo de preços com validações específicas de trava de datas. A funcionalidade da tela 1005 foi desabilitada conforme modificação documentada no histórico.

**Tela de Seleção:**

Parâmetros lidos também do(s) include(s): zemm_cadastro_preco_1001_scr.asinc

Tipo · Nome · Referência · Observação
BLOCK · b1
SELECT-OPTIONS · s_uslb1 · FOR ztmmc_stat_preco-zuserlb1

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_top.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_TOP é um TOP include que contém as declarações de dados globais para um programa de cadastro de preços no módulo MM. Ele define estruturas de dados, tabelas internas, controles de tela e objetos ALV necessários para implementar a funcionalidade de trava de datas na precificação VKP5, conforme especificado no GAP SD-034.
- **Nome do Objeto:** zrmm_cadastro_preco_top.asinc
- **Tipo do Objeto:** Top Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O TOP include implementa as declarações globais necessárias para o programa de cadastro de preços. Define estruturas para gerenciar dados de bloqueio, custos e aprovadores no contexto da precificação VKP5.

**Rotinas e métodos**

O include declara objetos ALV e controles de interface necessários para as rotinas principais do programa. As estruturas suportam operações de consulta, validação e aprovação de preços.

- Objetos CL_GUI_ALV_GRID — controle de exibição de dados em formato ALV
- Objetos CL_GUI_CUSTOM_CONTAINER — containers para interface gráfica
- Tabelas internas — armazenamento temporário de dados de bloqueio e custos

**Regra de negócio aplicada**

Implementa estruturas para controle de trava temporal na precificação, permitindo bloqueio de alterações em períodos específicos. Suporta hierarquia de aprovadores com aprovadores principais e substitutos.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1000_pbo.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_1000_PBO é um include de tela (PBO - Process Before Output) que controla a apresentação da tela 1000 no contexto do GAP SD-034 para implementação de trava de datas na precificação VKP5. O include gerencia o status da tela, barra de título e controle de abas para navegação entre diferentes subscreens.
- **Nome do Objeto:** zrmm_cadastro_preco_1000_pbo.asinc
- **Tipo do Objeto:** Screen Include (PBO/PAI)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa dois módulos PBO principais para controle da tela 1000. O primeiro módulo STATUS_1000 configura o status da tela e barra de título. O segundo módulo TAB_GERAL_ACTIVE_TAB_SET gerencia a navegação entre abas e subscreens associadas.

**Rotinas e métodos**

O módulo STATUS_1000 define o status 'SCREEN_1000' e título 'TITLE_1000' para a tela principal. O módulo TAB_GERAL_ACTIVE_TAB_SET controla a aba ativa através da estrutura tab_geral e mapeia cada aba para seu respectivo subscreen através de estrutura CASE.

- STATUS_1000 — Configuração de status e título da tela principal
- TAB_GERAL_ACTIVE_TAB_SET — Controle de navegação entre abas e subscreens

**Regra de negócio aplicada**

A regra de negócio implementa navegação estruturada entre diferentes áreas funcionais da precificação através de sistema de abas. Inclui lógica especial para reprocessamento forçado que limpa comandos após processamento. O mapeamento de abas permite acesso organizado às funcionalidades de cadastro de preço conforme especificado no GAP SD-034.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1001_pai.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_1001_PAI é um include de tela (PBO/PAI) que implementa a lógica de processamento de entrada de dados para o GAP SD-034, relacionado à trava de datas na precificação VKP5. O objeto contém módulos de validação de dados e processamento de comandos do usuário para controle de configurações de preços.
- **Nome do Objeto:** zrmm_cadastro_preco_1001_pai.asinc
- **Tipo do Objeto:** Screen Include (PBO/PAI)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa a lógica de processamento de entrada (PAI) para a tela 1001 do cadastro de preços. A estrutura contém módulos específicos para validação de dados de entrada e processamento de comandos do usuário, garantindo a integridade das informações antes do salvamento.

**Rotinas e métodos**

Os módulos implementados executam validações específicas de dados de entrada e processamento de comandos. Cada módulo tem responsabilidade clara, desde validação de campos até controle transacional.

- MODULE f_tipo_processo_1001 — Processa entrada de dados executando rotina de processamento de tela
- MODULE verificar_dados_lt — Valida campos de bloqueio, monitor e repasse com valores 'X' e campos numéricos positivos
- MODULE verificar_dados_vkp5 — Valida calendários de fábrica, percentuais de variação, horários e existência de usuários
- MODULE user_command_1001 — Processa comandos SALVE e LOG com confirmação e atualização de tabelas customizadas

**Regra de negócio aplicada**

As regras implementadas garantem a consistência dos dados de configuração de preços, validando a existência de usuários no sistema, a validade de calendários de fábrica e a corretude de percentuais de variação. O processo inclui confirmação do usuário antes do salvamento e registro de histórico das alterações.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1000_f01.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_1000_F01 é um include que contém a rotina F_LOG_T001_TAB responsável por exibir o histórico de logs da funcionalidade de trava de precificação VKP5. A rotina consulta a tabela customizada ZTMMC_STAT_PR_LG para recuperar dados de data e hora dos logs, ordena os registros e apresenta em uma tela modal (9000) para visualização do usuário.
- **Nome do Objeto:** zrmm_cadastro_preco_1000_f01.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa uma única rotina FORM responsável pela consulta e exibição de logs históricos. A implementação segue padrão clássico ABAP com SELECT direto em tabela customizada e apresentação via CALL SCREEN.

**Rotinas e métodos**

A rotina F_LOG_T001_TAB executa limpeza de tabelas internas, consulta dados na ZTMMC_STAT_PR_LG, ordena os resultados por data e hora decrescente e chama tela 9000 para apresentação. Em caso de ausência de dados, exibe mensagem informativa ao usuário.

- F_LOG_T001_TAB — consulta e exibição de logs históricos da precificação

**Regra de negócio aplicada**

A regra implementada permite visualização do histórico de logs da trava de precificação VKP5, ordenando os registros do mais recente para o mais antigo. Quando não há dados históricos, o sistema informa ao usuário e retorna à tela anterior.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1001_f01.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_1001_F01 é um include contendo rotinas FORM para seleção e atualização de dados relacionados ao controle de precificação VKP5. Implementa funcionalidades para carregar configurações de bloqueio de preços da tabela ZTMMC_STAT_PRECO e gerenciar usuários liberados na tabela ZTSDD_USERS_LIB, suportando o GAP SD-034 de trava de datas na precificação.
- **Nome do Objeto:** zrmm_cadastro_preco_1001_f01.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa duas rotinas principais para gerenciamento de dados de precificação. A primeira rotina carrega configurações de bloqueio e usuários liberados, enquanto a segunda sincroniza alterações na lista de usuários autorizados.

**Rotinas e métodos**

As rotinas utilizam técnicas modernas de ABAP como inline declarations e field-symbols para manipulação eficiente de dados. O processamento inclui refresh de tabelas internas, seleção de dados e sincronização com tabelas customizadas.

- F_SELECAO_DADOS_1001 — Carrega dados de configuração de bloqueio e usuários liberados
- F_ATUAL_DADOS_USUARIO_LIB_1001 — Sincroniza alterações na tabela de usuários autorizados

**Regra de negócio aplicada**

Implementa controle de acesso baseado em lista de usuários liberados para operações de precificação durante períodos de bloqueio. A regra permite manter configurações centralizadas de bloqueio temporal e exceções por usuário específico.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1002_f01.asinc

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_1002_f01 é um include contendo formulários (FORMs) para controle de tabela na tela 1002, implementando funcionalidades de cadastro e manutenção de preços no contexto do GAP SD-034. O objeto gerencia operações CRUD (inserção, modificação, exclusão) em tabelas de preços com controle de autorização e validações de datas, incluindo funcionalidades de log histórico e interface de usuário através de table controls.
- **Nome do Objeto:** zrmm_cadastro_preco_1002_f01.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa um conjunto abrangente de formulários para gerenciamento de cadastro de preços através de table controls. A arquitetura segue padrões clássicos do ABAP com separação clara entre controle de interface, validações de negócio e persistência de dados.

**Rotinas e métodos**

As rotinas principais gerenciam operações CRUD completas com controle de autorização, validações e log histórico. O fluxo inicia com controle de comandos de usuário, passa por validações de negócio e termina com persistência em tabelas transparentes.

- user_ok_tc — Processa comandos de table control (inserir, deletar, navegar)
- f_autorizacao_1002 — Verifica autorização do usuário para objeto ZSD_PRC_RA
- f_user_command_1002 — Processa comandos principais (MODF, INSR, DELE, LOG)
- f_validar_datas_1002 — Valida regras de negócio para datas (início/fim)
- f_atualizar_tabelas_1002 — Persiste dados nas tabelas ZTMMD_PRECO_RAPR e ZTMMD_PRLOG_RAPR
- f_insert_t002_tab — Insere nova condição de preço com validação de conflitos
- f_delete_t002_tab — Processa exclusão com confirmação e data final

**Regra de negócio aplicada**

Implementa trava de datas conforme GAP SD-034: data início não pode ser menor/igual à atual nem maior que 90 dias futuro, data fim deve ser maior que início. Sistema define valores padrão (data atual + 1 dia para início, 31/12/9999 para fim) quando campos vazios. Mantém histórico completo de alterações com dados de auditoria.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1003_f01.asinc

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_1003_f01 é um include contendo rotinas FORM para gerenciar o cadastro e autorização de aprovadores de preço na tela 1003. Faz parte do GAP SD-034 que implementa travas de datas na precificação VKP5, controlando quem pode modificar dados de preços através de verificações de autorização e sincronização com tabelas de fornecedores.
- **Nome do Objeto:** zrmm_cadastro_preco_1003_f01.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa um conjunto de rotinas FORM para gerenciar o cadastro de aprovadores de preço na tela 1003. A implementação segue uma arquitetura modular com separação clara de responsabilidades entre autorização, sincronização de dados, processamento de comandos do usuário e operações CRUD nas tabelas customizadas.

**Rotinas e métodos**

As rotinas implementam um fluxo completo de gerenciamento de dados, desde a verificação de autorização até a persistência no banco. Cada operação mantém log de auditoria e utiliza confirmações do usuário para operações críticas.

- F_AUTORIZACAO_1003 — Controla autorização do usuário e habilita/desabilita campos na tela
- F_SELECAO_ZTMMD_PRECO_CAPR — Sincroniza aprovadores entre LFA1 e tabelas customizadas
- F_SELECAO_USUARIO_CAPR — Enriquece dados com informações de usuários LDAP
- F_USER_COMMAND_1003 — Processa comandos do usuário na tela 1003
- F_MODIFICA_T003_TAB — Coordena operações de modificação na tabela
- F_DELETA_T003_TAB — Executa exclusão de registros com confirmação
- F_INSERIR_T003_TAB — Realiza cópia de registros existentes
- F_LOG_T003_TAB — Exibe histórico de operações
- F_ATUALIZAR_TABELAS_1003 — Persiste todas as operações no banco de dados

**Regra de negócio aplicada**

A regra de negócio implementa controle rigoroso de acesso ao cadastro de preços, permitindo modificações apenas para usuários autorizados. O sistema mantém sincronização automática com a base de fornecedores e garante rastreabilidade completa através de logs de auditoria para todas as operações realizadas.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1004_f01.asinc

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_1004_f01 é um include contendo rotinas FORM para gerenciar o cadastro de preços no contexto da trava de precificação VKP5. Implementa funcionalidades de sincronização de dados entre tabelas internas e de banco, processamento de comandos de usuário, e manutenção de logs de operações para o GAP SD-034.
- **Nome do Objeto:** zrmm_cadastro_preco_1004_f01.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa um conjunto de rotinas para gerenciar o cadastro de preços com foco na sincronização entre dados internos e tabelas de banco. A arquitetura segue o padrão de separação entre seleção de dados, processamento de comandos e atualização de tabelas.

**Rotinas e métodos**

As rotinas implementam um fluxo completo de manutenção de dados desde a seleção até a persistência, com controle de log integrado. Cada operação (inserção, modificação, exclusão) possui rotina específica para processamento.

- F_SELECAO_USUARIO_SAPR — Seleção e enriquecimento de dados de usuários da USER_ADDR
- F_SELECAO_ZTMMD_PRECO_SAPR — Sincronização entre tabela interna e ZTMMD_PRECO_CAPR
- F_USER_COMMAND_1004 — Processamento de comandos da tela 1004
- F_MODIFICA_T004_TAB — Coordenação das operações de modificação de dados
- F_LOG_T004_TAB — Exibição de histórico de logs na tela 9000
- F_TABELA_1004_INS — Processamento de inserções com validação de duplicatas
- F_TABELA_1004_MOD — Processamento de modificações de registros existentes
- F_TABELA_1004_DEL — Processamento de exclusões com log de auditoria
- F_ATUALIZAR_TABELAS_1004 — Persistência final das operações com commit

**Regra de negócio aplicada**

Implementa controle de aprovadores por código e sequência para o processo de precificação, com validação de autorização do usuário para modificação. Mantém rastreabilidade completa através de logs detalhados de todas as operações realizadas.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1004_pbo.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_1004_PBO é um include que contém módulos PBO (Process Before Output) para controle de tela de cadastro de preços. Faz parte do GAP SD-034 que implementa trava de datas na precificação VKP5, controlando a exibição e autorização de campos em uma table control TC_1004 que manipula dados da tabela ZTMMD_PRECO_SAPR.
- **Nome do Objeto:** zrmm_cadastro_preco_1004_pbo.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa três módulos PBO principais para controle da table control TC_1004. O módulo TC_1004_INIT realiza inicialização carregando dados da tabela ZTMMD_PRECO_SAPR, enquanto TC_1004_MOVE e TC_1004_GET_LINES controlam movimentação e contagem de linhas. Inclui também o módulo FILL_TABLE_CONTROL_1004 para preenchimento da estrutura de tela.

**Rotinas e métodos**

As rotinas principais são implementadas através de FORMs. A rotina F_AUTORIZACAO_1004 controla autorização baseada no objeto C_ZSD_PRC_CA, habilitando ou desabilitando campos conforme permissões do usuário. Outras rotinas referenciadas incluem F_SELECAO_ZTMMD_PRECO_SAPR e F_SELECAO_USUARIO_SAPR para seleção de dados complementares.

- F_AUTORIZACAO_1004 — Controla autorização e habilita/desabilita campos da tela
- TC_1004_INIT — Inicializa table control carregando dados da ZTMMD_PRECO_SAPR
- TC_1004_MOVE — Move dados entre estruturas da table control
- FILL_TABLE_CONTROL_1004 — Preenche estrutura de tela com dados da tabela interna

**Regra de negócio aplicada**

A regra principal implementa controle de autorização para modificação de dados de contingência de aprovador. Usuários sem autorização adequada têm campos bloqueados para entrada. Existe tratamento especial para username específico que bypassa verificação de autorização. Os dados são ordenados por campos específicos incluindo código, sequência, subdivisão e datas de vigência.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_9000_f01.asinc

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_9000_f01 é um include contendo rotinas (FORMs) para exibição de logs de processamento em formato ALV no contexto do GAP SD-034 relacionado à trava de precificação VKP5. O objeto implementa funcionalidades para criar containers customizados, objetos ALV Grid e exibir dados de diferentes tabelas internas com fieldcatalog dinâmico.
- **Nome do Objeto:** zrmm_cadastro_preco_9000_f01.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa um conjunto de rotinas especializadas para exibição de dados em formato ALV Grid. A arquitetura segue o padrão de separação de responsabilidades, com rotinas específicas para criação de containers, objetos ALV, configuração de layout e geração de fieldcatalog dinâmico.

**Rotinas e métodos**

As rotinas implementam um fluxo completo de criação e exibição de ALV, desde a verificação de dados até a apresentação final. O fieldcatalog é gerado dinamicamente baseado na estrutura das tabelas internas, permitindo flexibilidade na exibição de diferentes conjuntos de dados.

- F_LOG_PROCESSAMENTO_9000 — processa e exibe dados em ALV verificando qual tabela contém dados
- F_NEW_OBJ_CONT_ALV — cria container customizado para ALV
- F_NEW_OBJ_ALV — cria objeto ALV Grid dentro do container
- F_LAYOUT — configura layout da grade ALV com zebrado e otimização
- F_CREATE_FIELDCAT — cria entradas do catálogo de campos para ALV

**Regra de negócio aplicada**

As rotinas implementam a lógica de exibição de logs de processamento para o contexto de precificação VKP5. O sistema verifica automaticamente qual das quatro tabelas internas contém dados e configura a exibição ALV correspondente, incluindo contagem de linhas processadas no título da grade.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_f00.asinc

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_f00 é um include contendo rotinas (FORMs) que implementam o processo principal de cadastro de preços no contexto do GAP SD-034. Ele gerencia o fluxo de execução do programa, incluindo controle de bloqueio para evitar processamento simultâneo, seleção de dados hardcoded para autorização de usuários, navegação entre telas e limpeza de dados. O objeto atua como controlador principal do processo de precificação VKP5 com trava de datas.
- **Nome do Objeto:** zrmm_cadastro_preco_f00.asinc
- **Tipo do Objeto:** Form/Rotina Include
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O objeto implementa o controlador principal do processo de cadastro de preços, organizando o fluxo em etapas sequenciais: limpeza inicial, controle de bloqueio, seleção de dados de autorização e chamada da tela principal. A arquitetura segue padrão modular com FORMs especializadas para cada funcionalidade.

**Rotinas e métodos**

As rotinas implementam funcionalidades específicas do processo, desde controle de acesso até gerenciamento de tela. Cada FORM tem responsabilidade bem definida e utiliza funções padrão SAP quando apropriado.

- f_selecao_hardcode — busca usuários liberados e define grupo de contas padrão
- f_bloqueio_processamento — cria lock exclusivo para evitar execução simultânea
- f_desbloqueio_processamento — remove lock do processamento
- f_processo_tela — controla navegação entre abas e ações de saída
- f_limpar_dados — reinicializa tabelas internas e variáveis
- f_clear_geral — limpa variáveis globais de autorização

**Regra de negócio aplicada**

A regra principal é garantir execução controlada do processo de precificação, permitindo acesso apenas a usuários autorizados e evitando conflitos de processamento simultâneo. O sistema verifica permissões através da classe zcl_parametros e aplica grupo de contas padrão 'Z005' quando não há configuração específica.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zemm_cadastro_preco_1001_scr.asinc

- **Objetivo do desenvolvimento:** O objeto ZEMM_CADASTRO_PRECO_1001_SCR é um include que define uma subscreen (tela 1006) contendo um campo de seleção múltipla para o campo ZUSERLB1 da tabela ZTMMC_STAT_PRECO. Este componente faz parte da solução para implementar a trava de precificação VKP5 conforme especificado no GAP SD-034.
- **Nome do Objeto:** zemm_cadastro_preco_1001_scr.asinc
- **Tipo do Objeto:** Include (genérico)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include define uma subscreen (1006) que será incorporada em uma tela principal do programa de precificação. A implementação utiliza SELECTION-SCREEN para criar uma interface de seleção com um bloco organizado contendo um campo SELECT-OPTIONS.

**Rotinas e métodos**

O objeto não contém rotinas ou métodos específicos, sendo composto apenas pela definição declarativa da subscreen. A funcionalidade se baseia na estrutura padrão do SELECTION-SCREEN do ABAP.

- SELECT-OPTIONS s_uslb1 — Campo de seleção múltipla para usuários da tabela ZTMMC_STAT_PRECO

**Regra de negócio aplicada**

A regra implementada permite a seleção de usuários específicos (ZUSERLB1) para controle de acesso na funcionalidade de precificação VKP5. A configuração NO INTERVALS força a seleção por valores exatos, evitando ranges de usuários.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zesd_prc_transf_praca_exp.asinc

- **Objetivo do desenvolvimento:** O objeto zesd_prc_transf_praca_exp é um include ABAP que implementa lógicas de determinação de tipo de cálculo de preço (KALGR) para transferência entre praças de expedição. Faz parte da solução do GAP SD-034 que implementa travas de precificação no processo VKP5, executando diferentes regras baseadas em características do material, centro e parâmetros configuráveis do sistema.
- **Nome do Objeto:** zesd_prc_transf_praca_exp.asinc
- **Tipo do Objeto:** Include (genérico)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa três blocos principais de determinação de tipo de cálculo de preço. Cada bloco executa condicionalmente baseado em parâmetros específicos e características do contexto de precificação. A lógica utiliza field-symbols para acessar variáveis de outros programas e a classe ZCL_PARAMETROS para obter configurações do sistema.

**Rotinas e métodos**

O código não define FORMs ou METHODs explícitos, sendo estruturado em blocos sequenciais de código. Cada bloco implementa uma regra específica de determinação do campo KALGR baseada em diferentes critérios de negócio. A classe ZCL_PARAMETROS é utilizada para carregar ranges de valores configuráveis que direcionam as decisões de tipo de cálculo.

- Bloco 0 — Determinação baseada em sequência e ranges parametrizáveis
- Bloco 1 — Cálculo de preço de transferência bruto para praça de expedição
- Bloco 2 — Determinação por indicador de distribuição e tipo de material

**Regra de negócio aplicada**

As regras implementadas determinam o tipo de cálculo de preço considerando: indicador de distribuição 'B' da planta (atribui Z007), materiais de serviço com diferentes organizações de vendas (atribui ZSER ou ZSRV), e sequências de determinação parametrizáveis que resultam em tipos específicos como ZPFS, ZPF1, ZPF2. A execução é condicionada pela variável vl_exc para evitar processamento desnecessário.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zesd_precos_leroy.asinc

- **Objetivo do desenvolvimento:** O objeto ZESD_PRECOS_LEROY é um include genérico que implementa funcionalidades customizadas para a transação VKP5 (precificação). Atua como um wrapper que chama a classe ZCLSD_ZESD_PRECOS_LEROY para executar validações e controles específicos relacionados à trava de datas na precificação, permitindo exceções para usuários autorizados.
- **Nome do Objeto:** zesd_precos_leroy.asinc
- **Tipo do Objeto:** Include (genérico)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa um wrapper simples que captura o contexto de execução (sy-repid) e delega todo o processamento para a classe ZCLSD_ZESD_PRECOS_LEROY. A implementação segue padrão orientado a objetos, separando a lógica de negócio da interface de chamada.

**Rotinas e métodos**

O processamento é centralizado na chamada do método estático user_exit_execute da classe ZCLSD_ZESD_PRECOS_LEROY. Os parâmetros de entrada incluem variáveis de seleção e contexto, enquanto os parâmetros de saída modificam as seleções conforme regras de negócio aplicadas.

- ZCLSD_ZESD_PRECOS_LEROY=>user_exit_execute — Método principal que executa validações e controles de precificação

**Regra de negócio aplicada**

Implementa controle de trava de datas na precificação VKP5, permitindo exceções para usuários específicos do departamento de Pricing. A regra permite que alguns usuários alterem preços para qualquer data, enquanto outros ficam restritos às validações padrão do sistema.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1002_pbo.asinc

- **Objetivo do desenvolvimento:** O objeto ZRMM_CADASTRO_PRECO_1002_PBO é um include que contém módulos PBO (Process Before Output) para controle de tela TC_1002, responsável pela gestão de preços na transação VKP5. Implementa a lógica de inicialização, movimentação e controle de linhas para uma tabela de controle de preços, incluindo validação de datas e processamento de registros expirados.
- **Nome do Objeto:** zrmm_cadastro_preco_1002_pbo.asinc
- **Tipo do Objeto:** Include (genérico)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa três módulos PBO para controle da tela TC_1002: inicialização (tc_1002_init), movimentação de dados (tc_1002_move) e controle de linhas (tc_1002_get_lines). O módulo principal realiza seleção de dados da tabela ZTMMD_PRECO_RAPR e processa registros expirados automaticamente.

**Rotinas e métodos**

O módulo tc_1002_init executa a lógica principal de inicialização, incluindo seleção de dados, processamento de registros expirados e chamada de rotinas auxiliares. Os demais módulos são responsáveis pela movimentação de dados entre estruturas e controle de linhas da tabela de controle.

- MODULE tc_1002_init — inicialização da tela e processamento de dados principais
- MODULE tc_1002_move — movimentação de dados entre work area e estrutura de tela
- MODULE tc_1002_get_lines — controle do número de linhas da tabela de controle
- PERFORM f_atualizar_tabelas_1002 — atualização de tabelas com registros processados
- PERFORM f_autorizacao_1002 — verificação de autorização do usuário
- PERFORM f_preencher_dados_1002 — preenchimento de dados descritivos

**Regra de negócio aplicada**

Implementa trava de datas na precificação VKP5, verificando se a data final do registro (zzdocpr_tipdtf) é menor que a data atual. Registros expirados são automaticamente movidos para tabela de histórico e removidos da seleção ativa, garantindo que apenas preços válidos sejam apresentados ao usuário.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zrmm_cadastro_preco_1003_pbo.asinc

- **Objetivo do desenvolvimento:** O objeto zrmm_cadastro_preco_1003_pbo é um include ABAP que implementa módulos PBO (Process Before Output) para controle de tabela TC_1003, responsável pela inicialização e exibição de dados de precificação da tabela ZTMMD_PRECO_CAPR. Faz parte da solução GAP SD-034 que implementa trava de datas na precificação VKP5.
- **Nome do Objeto:** zrmm_cadastro_preco_1003_pbo.asinc
- **Tipo do Objeto:** Include (genérico)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa quatro módulos PBO essenciais para o funcionamento do table control TC_1003. O módulo principal tc_1003_init realiza a inicialização completa dos dados, incluindo limpeza de tabelas internas, seleção de dados da ZTMMD_PRECO_CAPR e processamento de validações de autorização.

**Rotinas e métodos**

Os módulos seguem o padrão SAP para table controls, com separação clara de responsabilidades. O tc_1003_init concentra a lógica de inicialização e validação, enquanto os demais módulos tratam da movimentação e controle de dados na tela.

- tc_1003_init — inicialização e carregamento de dados da tabela
- tc_1003_move — movimentação de dados para estrutura de tela
- tc_1003_get_lines — controle de linhas do table control
- fill_table_control_1003 — preenchimento de linha específica do controle

**Regra de negócio aplicada**

Implementa controle de autorização através da variável vg_aut_1003 e validação de dados principais via vg_capr. A ordenação dos dados segue critérios específicos do negócio incluindo código, sequência, subdivisão e datas de vigência, garantindo apresentação consistente dos dados de precificação.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).

### zxvkpu03.asinc

- **Objetivo do desenvolvimento:** O include ZXVKPU03 é um exit de validação para a transação VKP5 (precificação) que implementa controles de autorização baseados em sequências de determinação de preços (EKERV/VKERV), força o uso da unidade de medida básica do material e aplica regras específicas para centros com indicador de avaliação 'A'.
- **Nome do Objeto:** zxvkpu03.asinc
- **Tipo do Objeto:** Include (genérico)
- **Classificação:** Objeto Novo

**Detalhamento do Desenvolvimento:**

**Visão geral da implementação**

O include implementa validações de autorização e regras de negócio específicas para precificação. Utiliza field-symbols para acessar variáveis globais dos programas RWVKP007 e outros, aplicando controles baseados em sequências de determinação de preços.

**Rotinas e métodos**

A lógica principal executa em sequência: validação de autorização para EKERV/VKERV, aplicação de regra para centros tipo 'A', inclusão de processamento adicional via ZESD_PRC_TRANSF_PRACA_EXP, e padronização da unidade de medida básica.

- AUTHORITY-CHECK — validação de acesso às sequências de determinação
- SELECT FROM I_PRODUCT — obtenção da unidade de medida básica
- ASSIGN dinâmico — acesso a variáveis globais de outros programas

**Regra de negócio aplicada**

Implementa trava de precificação baseada em autorização por sequências EKERV/VKERV. Para centros com indicador 'A', força grupo de cálculo 'Z001'. Padroniza unidade de medida para compatibilidade com sistema GEMCO, permitindo apenas unidade básica do material.

**Tela de Seleção:**

Não se aplica (objeto não é Report/Programa).

**TVARV:**

Não foram encontradas referências à tabela TVARV/TVARVC.

**BRF+:**

Não foram encontradas referências a BRF/BRF+/BTF.

**Objetos de Autorização:**

Objetos de autorização identificados no código:

Origem · Objeto · Campos
AUTHORITY-CHECK · ZMM_EKERV · ACTVT='*', EKERV=vl_ekerv
AUTHORITY-CHECK · ZMM_VKERV · ACTVT='*', VKERV=vl_vkerv
