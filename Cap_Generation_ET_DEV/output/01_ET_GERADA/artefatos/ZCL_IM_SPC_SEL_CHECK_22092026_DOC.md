# Documentação Técnica — zcl_im_spc_sel_check

- **Arquivo:** zcl_im_spc_sel_check.aclass
- **Tipo do objeto:** Classe (Global)
- **Classificação:** Objeto Novo
- **Data de geração:** 22/09/2026
- **GAP/EF relacionada:** SD-034 / LEROY_REL_SD-034 - Trava Precificação VKP5_29082026_V2

## 📌 RESUMO EXECUTIVO

**Entendimento:** A classe ZCL_IM_SPC_SEL_CHECK implementa a interface IF_EX_SPC_SEL_CHECK como um enhancement point para validações de seleção no processo de precificação VKP5. Sua função principal é controlar quais materiais podem ser incluídos no cálculo de preços, aplicando regras de negócio específicas relacionadas à trava de datas na precificação conforme definido no GAP SD-034.

**Contexto de Negócio:** Esta implementação atende ao cenário de Gestão de Preço no processo de Precificação VKP5, aplicando controles específicos para materiais AVS (quando o usuário não possui autorização ZMM_AVS_VK) e materiais que não podem ser utilizados em determinadas listas de preço. O objeto também realiza atualizações de campos de preço quando a condição de cálculo é 'Z7'.

**Avaliação Geral:** O desenvolvimento apresenta implementação parcial com alguns métodos vazios, indicando possível desenvolvimento em andamento. A lógica principal está concentrada no método check_calc_item, que implementa as validações necessárias. Há pontos de atenção relacionados à completude da implementação e à documentação dos métodos não implementados.

## 📊 RELATÓRIO ESTRUTURADO DE VALIDAÇÃO

### SEÇÃO 1 – Resumo do Desenvolvimento
| Status | Ponto | Observação |
|:------:|-------|------------|
| ✅ | Nomenclatura | A classe segue o padrão de nomenclatura SAP com prefixo Z e implementa corretamente a interface IF_EX_SPC_SEL_CHECK. |
| ✅ | Estrutura da classe | Classe definida como PUBLIC e FINAL, seguindo boas práticas de encapsulamento. |
| ⚠️ | Implementação incompleta | Alguns métodos da interface estão vazios (filter_orglevels), sugerindo implementação parcial ou em desenvolvimento. |
| ✅ | Tratamento de autorização | Implementa corretamente a verificação do objeto de autorização ZMM_AVS_VK para controle de acesso a materiais AVS. |
| ✅ | Manipulação de dados | Utiliza estruturas padrão SAP e realiza atualizações adequadas nos campos de preço conforme regras de negócio. |
| ⚠️ | Documentação | Ausência de comentários explicativos nos métodos implementados, dificultando manutenção futura. |

### SEÇÃO 2 – Detalhamento do Desenvolvimento
#### 2.1 Visão geral da implementação

A classe implementa um enhancement point para o módulo SPC, focando em validações de seleção durante o processo de precificação. A implementação utiliza a interface padrão SAP IF_EX_SPC_SEL_CHECK para interceptar e validar itens antes do cálculo de preços.

#### 2.2 Rotinas e métodos

O método principal check_calc_item contém a lógica de validação, verificando autorizações e aplicando regras específicas para materiais AVS e listas de preço. Os demais métodos da interface estão declarados mas não implementados.

- IF_EX_SPC_SEL_CHECK~CHECK_CALC_ITEM — Validação principal de itens de cálculo com controle de autorização e regras de negócio
- IF_EX_SPC_SEL_CHECK~FILTER_ORGLEVELS — Método declarado mas não implementado para filtragem de níveis organizacionais

#### 2.3 Regra de negócio aplicada

A implementação aplica controles específicos para o processo de precificação VKP5, excluindo materiais AVS quando o usuário não possui autorização adequada e controlando o uso de materiais em listas de preço específicas. Quando a condição de cálculo é 'Z7', o sistema atualiza campos específicos de preço conforme definido nas regras de negócio.

#### Fonte

Generative AI RAG Document Capgemini


### SEÇÃO 3 – Observações Técnicas
| Status | Ponto | Observação |
|:------:|-------|------------|
| ✅ | Compatibilidade S/4HANA | A implementação utiliza interfaces padrão SAP que são compatíveis com S/4HANA, facilitando a migração. |
| ✅ | Clean Core | O uso de enhancement points através de interfaces padrão está alinhado com os princípios de Clean Core. |
| ⚠️ | Dependências identificadas | O objeto possui dependências das tabelas MARA, WRF6 e ZTSDD_PRICE_001 que devem ser validadas durante a migração. |
| ✅ | Performance | A lógica implementada é eficiente, realizando verificações pontuais sem loops desnecessários ou consultas complexas. |

### SEÇÃO 4 – Tela de Seleção
Não se aplica (objeto não é Report/Programa).

### SEÇÃO 5 – TVARV
Não foram encontradas referências à tabela TVARV/TVARVC.

### SEÇÃO 5.3 – BRF
Não foram encontradas referências a BRF/BRF+/BTF.

### SEÇÃO 6 – Objetos de Autorização
Objetos de autorização identificados no código:

| Origem | Objeto | Campos |
|--------|--------|--------|
| AUTHORITY-CHECK | `ZMM_AVS_VK` | ACTVT='01' |
