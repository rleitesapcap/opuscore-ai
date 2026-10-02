# Documentação Técnica — zesd_prc_transf_praca_exp

- **Arquivo:** zesd_prc_transf_praca_exp.asinc
- **Tipo do objeto:** Include (genérico)
- **Classificação:** Objeto Novo
- **Data de geração:** 22/09/2026
- **GAP/EF relacionada:** SD-034 / LEROY_REL_SD-034 - Trava Precificação VKP5_29082026_V2

## 📌 RESUMO EXECUTIVO

**Entendimento:** O objeto zesd_prc_transf_praca_exp é um include ABAP que implementa lógicas de determinação de tipo de cálculo de preço (KALGR) para transferência entre praças de expedição. Faz parte da solução do GAP SD-034 que implementa travas de precificação no processo VKP5, executando diferentes regras baseadas em características do material, centro e parâmetros configuráveis do sistema.

**Contexto de Negócio:** O include suporta o processo de precificação VKP5 da Leroy Merlin, determinando automaticamente o tipo de cálculo de preço apropriado para transferências entre praças. As regras implementadas consideram indicadores de distribuição, tipos de material de serviço e parâmetros específicos de organização de vendas para garantir a aplicação correta de políticas de preço.

**Avaliação Geral:** O desenvolvimento apresenta estrutura modular adequada com três blocos distintos de regras de negócio. Utiliza field-symbols para acesso a variáveis globais e a classe ZCL_PARAMETROS para configurações. Pontos de atenção incluem dependência de variáveis globais externas e ausência de tratamento de erro explícito nas consultas a tabelas.

## 📊 RELATÓRIO ESTRUTURADO DE VALIDAÇÃO

### SEÇÃO 1 – Resumo do Desenvolvimento
| Status | Ponto | Observação |
|:------:|-------|------------|
| ✅ | Nomenclatura | Nome do objeto segue padrão Z com prefixo funcional adequado para o módulo SD. |
| ✅ | Modularização | Código organizado em blocos lógicos distintos com responsabilidades bem definidas. |
| ⚠️ | Acesso a dados | Utiliza field-symbols para acessar variáveis globais sem validação de existência prévia. |
| ⚠️ | Tratamento de erro | Ausência de tratamento explícito de exceções nas consultas SELECT às tabelas T001W e MARA. |
| ✅ | Performance | Utiliza SELECT SINGLE com chaves primárias adequadas para consultas pontuais. |
| ✅ | Configurabilidade | Implementa parametrização através da classe ZCL_PARAMETROS permitindo flexibilidade nas regras. |

### SEÇÃO 2 – Detalhamento do Desenvolvimento
#### 2.1 Visão geral da implementação

O include implementa três blocos principais de determinação de tipo de cálculo de preço. Cada bloco executa condicionalmente baseado em parâmetros específicos e características do contexto de precificação. A lógica utiliza field-symbols para acessar variáveis de outros programas e a classe ZCL_PARAMETROS para obter configurações do sistema.

#### 2.2 Rotinas e métodos

O código não define FORMs ou METHODs explícitos, sendo estruturado em blocos sequenciais de código. Cada bloco implementa uma regra específica de determinação do campo KALGR baseada em diferentes critérios de negócio. A classe ZCL_PARAMETROS é utilizada para carregar ranges de valores configuráveis que direcionam as decisões de tipo de cálculo.

- Bloco 0 — Determinação baseada em sequência e ranges parametrizáveis
- Bloco 1 — Cálculo de preço de transferência bruto para praça de expedição
- Bloco 2 — Determinação por indicador de distribuição e tipo de material

#### 2.3 Regra de negócio aplicada

As regras implementadas determinam o tipo de cálculo de preço considerando: indicador de distribuição 'B' da planta (atribui Z007), materiais de serviço com diferentes organizações de vendas (atribui ZSER ou ZSRV), e sequências de determinação parametrizáveis que resultam em tipos específicos como ZPFS, ZPF1, ZPF2. A execução é condicionada pela variável vl_exc para evitar processamento desnecessário.

#### Fonte

Generative AI RAG Document Capgemini


### SEÇÃO 3 – Observações Técnicas
| Status | Ponto | Observação |
|:------:|-------|------------|
| ✅ | Compatibilidade S/4HANA | Utiliza tabelas padrão SAP (MARA, MARC, MBEW, T001W) que são compatíveis com S/4HANA. |
| ⚠️ | Clean Core | Dependência de classe Z customizada pode impactar futuras atualizações se não seguir princípios de extensibilidade. |
| ✅ | Performance | Consultas otimizadas com SELECT SINGLE e uso adequado de índices primários das tabelas. |
| ⚠️ | Manutenibilidade | Field-symbols para variáveis globais podem dificultar debugging e manutenção futura do código. |

### SEÇÃO 4 – Tela de Seleção
Não se aplica (objeto não é Report/Programa).

### SEÇÃO 5 – TVARV
Não foram encontradas referências à tabela TVARV/TVARVC.

### SEÇÃO 5.3 – BRF
Não foram encontradas referências a BRF/BRF+/BTF.

### SEÇÃO 6 – Objetos de Autorização
Não foram encontradas referências a objetos de autorização (AUTHORITY-CHECK / pfcg_auth).
