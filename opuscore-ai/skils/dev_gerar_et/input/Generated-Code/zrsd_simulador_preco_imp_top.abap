"*********************************************************************
" Capgemini AI Remediation Code - Brazil
"*********************************************************************
" Data Execução: 	10/08/2026
" Autor:	 		Capgemini SAP AI - Plataform
" Projeto:              MOVE2S4
"*********************************************************************


"------------------------------------------------------------------------------------------------------------------------------------
"                                                    Capgemini SAP AI Remediation                                                    
"------------------------------------------------------------------------------------------------------------------------------------
" Date           : 10-08-2026
" Remediation    : RAG-driven; model emits change-set JSON, Python applies it (line-based)
" Target         : SAP S/4HANA 2025 (Private Edition)
" ATC Variant    : ZS4HANA_LEROY_CHECK
" Package        : ZDEV
"------------------------------------------------------------------------------------------------------------------------------------
" ORIGINAL FILE  : zrsd_simulador_preco_imp_top.abap
" SOURCE         : C:\Users\rsilva14\OneDrive - Capgemini\Documents\workspace\Projetos\projetos_ai\projetos_cap\Cap_Remediation_GenIA\remediation_proc\zrsd_simulador_preco_imp_top.abap
" SESSION ID     : 1e51b8cd-340e-4fbc-b0a2-203d44e43ab6
" PROCESSED AT   : 2026-08-10 14:03:34
"====================================================================================================================================

" NAMING ANALYSIS STATUS - Capgemini SAP AI Remediation (ABAP_Move2S4 Workbook)
" Workbook    : Workbook_ABAP_Move2S4_Final.docx
" Package     : ZDEV
" Retrieved   : NO
" Result      : NOT VERIFIED - Workbook not retrievable, manual naming review required
" Scope       : Package ZDEV and all custom identifiers (INCLUDE, TYPES, CONSTANTS, DATA, CLASS, METHODS)
"--------------------------------------------------------------------------------------------------

*&---------------------------------------------------------------------*
*&  Include           ZRSD_SIMULADOR_PRECO_IMP_TOP
*&---------------------------------------------------------------------*
"--------------------------------------------------------------------------------------------------
" MANUAL REVIEW REQUIRED - Capgemini SAP AI Remediation
" Reason     : Hardcode include file needs manual review to ensure compliance with Clean Core principles and S/4HANA compatibility
" RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
"--------------------------------------------------------------------------------------------------
INCLUDE zexx_hardcode.        " Hardcode

*---------------------------------------------------------------------*
* Declaração: Estrutura(s) de tabela(s)
*---------------------------------------------------------------------*
"--------------------------------------------------------------------------------------------------
" BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
" Reason     : TABLES statement is obsolete and should be replaced with explicit work area declarations
" RAG Source : From Classic ABAP to ABAP.pdf
" Antes      :
"   TABLES: "ztsdd_simuprech,   "Simulação de preço importado - Cabeçalho
"     "        ztsdd_simupreci,   "Simulação de preço importado - Item
"     ztsdd_precadmat,   "Materiais pré-cadastrados
"     ekko,              "Cabeçalho do documento de compra
"     ekpo,              "Item do documento de compra
"   *        t001w,             "Centros/filiais
"     calp.              "Cálculo do preço de venda: item de um cálculo de preço
"--------------------------------------------------------------------------------------------------
* TABLES statement removed - declare work areas explicitly as needed
* DATA: wa_ztsdd_precadmat TYPE ztsdd_precadmat,
*       wa_ekko TYPE ekko,
*       wa_ekpo TYPE ekpo,
*       wa_calp TYPE calp.
"--------------------------------------------------------------------------------------------------
" END OF MODIFICATION - Capgemini SAP AI Remediation
"--------------------------------------------------------------------------------------------------

*---------------------------------------------------------------------*
* Declaração: Constante(s)
*---------------------------------------------------------------------*
CONSTANTS: sim(3)        TYPE c VALUE 'SIM',
           mat(3)        TYPE c VALUE 'MAT',
           mpc(3)        TYPE c VALUE 'MPC',
           ped(3)        TYPE c VALUE 'PED',
           all(3)        TYPE c VALUE 'ALL',
           pcb(3)        TYPE c VALUE 'PCB',
           c_back(4)     TYPE c VALUE 'BACK',
           c_exit(4)     TYPE c VALUE 'EXIT',
           c_canc(4)     TYPE c VALUE 'CANC',
           c_container   TYPE scrfname VALUE 'CONTAINER',
           c_stat_10(30) TYPE c VALUE 'Aguardando aprovação',
           c_stat_20(30) TYPE c VALUE 'Rejeitado',
           c_stat_30(30) TYPE c VALUE 'Aprovado',
           c_stat_00(30) TYPE c VALUE 'Não enviado para aprovação'.

**---------------------------------------------------------------------*
** Declaração: Variável(is)
**---------------------------------------------------------------------*
DATA: "gr_mtart TYPE RANGE OF mtart,
      "--------------------------------------------------------------------------------------------------
      " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
      " Issue      : RANGE OF and LIKE statements are obsolete syntax patterns
      " RAG Source : From Classic ABAP to ABAP.pdf
      " Impact     : While functional, these patterns are not aligned with modern ABAP development standards
      "--------------------------------------------------------------------------------------------------
      " Recommended code (suggestion — not applied):
      "   DATA: gr_uname TYPE TABLE OF syst_uname,
      "         er_uname TYPE syst_uname.
      "--------------------------------------------------------------------------------------------------
      gr_uname TYPE RANGE OF syst_uname, "<CC.2252> Inclusão IROSA 19.09.2018
      er_uname like line of gr_uname.
DATA: vg_erro(1) TYPE c,
      vg_edit(1) TYPE c,
      vg_gp      TYPE wyt3-lifn2,             "GP Aprovador
      vg_dgp     TYPE wyt3-lifn2,             "DGP Aprovador
      vg_gpname  TYPE lfa1-name1.            "Nome GP Aprovador

*** Alv structure
DATA: vg_grid TYPE REF TO cl_gui_alv_grid.

DATA:
* Reference to document
  vg_dyndoc_id   TYPE REF TO cl_dd_document,
* Reference to split container
  vg_splitter    TYPE REF TO cl_gui_splitter_container,
* Reference to grid container
  vg_parent_grid TYPE REF TO cl_gui_container,
* Reference to html container
  vg_html_cntrl  TYPE REF TO cl_gui_html_viewer,
* Reference to html container
  vg_parent_html TYPE REF TO cl_gui_container.

DATA: "ok_code       LIKE sy-ucomm,
      vg_layout     TYPE lvc_s_layo.

*---------------------------------------------------------------------*
* Declaração: Tipo(s)
*---------------------------------------------------------------------*
TYPES:
  BEGIN OF ty_twkao,
    vkorg TYPE twkao-vkorg,            "Organização de vendas
    vtweg TYPE twkao-vtweg,            "Canal de distribuição
    pltyp TYPE twkao-pltyp,            "Categoria de lista de preços
    vlgwk TYPE twkao-vlgwk,            "Centro de referência
    ptext TYPE t189t-ptext,            "Descrição
  END OF ty_twkao,


  BEGIN OF ty_mara,
    matnr TYPE mara-matnr,             "Nº Material
    mtart TYPE mara-mtart,             "Tipo de Material
    matkl TYPE mara-matkl,             "Grupo de mercadorias
    meins TYPE mara-meins,             "Unidade de Medida
    bstat TYPE mara-bstat,             "Status de criação suprimento por época
    maktx TYPE makt-maktx,             "Descrição Material
    bwkey TYPE mbew-bwkey,             "Área de avaliação
    mtuse TYPE mbew-mtuse,             "Utilização de material
    mtorg TYPE mbew-mtorg,             "Origem de material
    werks TYPE marc-werks,             "Centro
    steuc TYPE marc-steuc,             "Código de controle p/imposto seletivo em comércio exterior
  END OF ty_mara,










  BEGIN OF ty_change,
    index    TYPE sy-tabix,              "Linha
    pclx(1)  TYPE c,                     "Calcular PCL?
    pcb_v    TYPE ekpgr,                 "Novo valor PCB
    pv_fin_v TYPE endpr,                 "Novo valor Preço de Venda Final
    rappel_v TYPE kbetr,                 "Novo valor Rappel
  END OF ty_change,

  BEGIN OF ty_pcl,
    matnr               TYPE matnr,          "Material
    werks               TYPE ewerk,          "Centro
    pcl                 TYPE ekpnn,          "PCL
    pclst               TYPE ekpnn,          "PCL
    rate_icms_comp      TYPE zesd_calcula_preco-pe_base_icms_comp,   "Rate ICMS Compra
    base_icms_comp      TYPE zesd_calcula_preco-pe_base_icms_comp,   "Base ICMS Compra
    val_icms_comp       TYPE zesd_calcula_preco-pe_val_icms_comp,    "Valor ICMS Compra
    rate_ipi_comp       TYPE zesd_calcula_preco-pe_rate_ipi_comp,    "Rate IPI Compra
    base_ipi_comp       TYPE zesd_calcula_preco-pe_base_ipi_comp,    "Base IPI Compra
    val_ipi_comp        TYPE zesd_calcula_preco-pe_val_ipi_comp,     "Valor IPI Compra
    rate_cofins_comp    TYPE zesd_calcula_preco-pe_rate_cofins_comp, "Rate COFINS Compra
    base_cofins_comp    TYPE zesd_calcula_preco-pe_base_cofins_comp, "Base COFINS Compra
    val_cofins_comp     TYPE zesd_calcula_preco-pe_val_cofins_comp,  "Valor COFINS Compra
    rate_pis_comp       TYPE zesd_calcula_preco-pe_rate_pis_comp,    "Rate PIS Compra
    base_pis_comp       TYPE zesd_calcula_preco-pe_base_pis_comp,    "Base PIS Compra
    val_pis_comp        TYPE zesd_calcula_preco-pe_val_pis_comp,     "Valor PIS Compra
    calc_base_st_comp   TYPE zesd_calcula_preco-pe_calc_base_st_comp, "Base ST Compra
    calc_icms_st_comp   TYPE zesd_calcula_preco-pe_calc_icms_st_comp, "ICMS ST Compra
    rate_icms_st_comp   TYPE zesd_calcula_preco-pe_rate_icms_st_comp, "Rate ICMS ST Compra
    maj_bst_comp        TYPE zesd_calcula_preco-pe_maj_bst_comp,      "MAJ BST Compra
    maj_bicms_comp      TYPE zesd_calcula_preco-pe_maj_bicms_comp,    "MAJ BICMS Compra
    calc_pis_st_comp    TYPE zesd_calcula_preco-pe_calc_pis_st_comp,  "PIS ST Compra
    calc_cofins_st_comp TYPE zesd_calcula_preco-pe_calc_cofins_st_comp, "COFINS ST Compra
    rate_st_int_comp    TYPE zesd_calcula_preco-pe_rate_st_int_comp , "Rate ICMS ST Interno Compra
    uf_precad           TYPE zesd_calcula_preco-pi_uf_precad,           "UF Materail pré-cadastrado
  END OF ty_pcl,

  BEGIN OF ty_mat_pop,
    check TYPE c,              "Checkbox
    matnr TYPE matnr,          "Material
    werks TYPE ewerk,          "Centro
    maktx TYPE maktx,          "Descrição
  END OF ty_mat_pop,

  BEGIN OF ty_t007s,
    mwskz TYPE  mwskz,        "Código IVA
    text1 TYPE text1_007s,    "Denominação do IVA
  END OF ty_t007s.

*


TYPES: BEGIN OF ty_saida_rel,
         mark(1)         TYPE c,
         docsim          TYPE zesd_docsim,         "Documento de Simulacao.
         matnr           TYPE matnr,           "Material
         maktx           TYPE maktx,           "Descrição Material
         pltyp           TYPE pltyp,           "Lista Preço,
         ptext           TYPE text20,          "Descrição lista de preço
         werks           TYPE ewerk,           "Centro
         lifnr           TYPE elifn,           "Fornecedor
         pcb             TYPE ekpgr,           "PCB
         pcb_efetivo     TYPE ekpgr,           "PCB
         pcl             TYPE ekpnn,           "PCL
         pcl_efetivo     TYPE ekpnn,           "PCL
         condicao_pcb    TYPE knumh,           "Condicao PCB.
         preco_transf    TYPE ekpnn,           "Preço Transferência
         pt_efetivo      TYPE ekpnn,           "Preço Transferência
         condicao_pt     TYPE knumh,           "Condicao Transferencia.
         rappel          TYPE kbetr,           "Rappel %
         rappel_efetivo  TYPE kbetr,           "Rappel %
         condicao_rappel TYPE knumh,           "Condicao Rappel
         custo_log       TYPE kbetr,           "Custo Logistico %
         pv_liq          TYPE vkpzw,           "PV Liquido
         pvl_efetivo     TYPE vkpzw,           "PV Liquido
         pv_fin          TYPE endpr,           "PV Final
         pvf_efetivo     TYPE endpr,           "PV Final
         mg_liq          TYPE wty_kbetr3,      "Margem Líquida %
         mgl_efetivo     TYPE wty_kbetr3,      "Margem Líquida %
         mg_bruta        TYPE wty_kbetr3,      "Margem Bruta %
         mgb_efetivo     TYPE wty_kbetr3,      "Margem Bruta %
         condicao_pvf    TYPE knumh,           "Condicao Preco venda Final
         msg_autom       TYPE zesd_msg_aut,    "Mensagem do Processo
         color_cell      TYPE lvc_t_scol,      "Cell color
       END OF ty_saida_rel.

*---------------------------------------------------------------------*
* Declaração: Estrutura(s)
*---------------------------------------------------------------------*
DATA:
  eg_twkao     TYPE ty_twkao,
  eg_mara      TYPE ty_mara,
  eg_dados     TYPE zesd_calcula_preco,
  eg_simuprech TYPE ztsdd_simuprech,
  eg_simupreci TYPE ztsdd_simupreci,
  eg_impostos  TYPE zssd_mon_imp_impostos,
  eg_pcl       TYPE ty_pcl,
  eg_change    TYPE ty_change,
  eg_saida     TYPE zssd_mon_imp_saida,
  eg_fieldcat  TYPE lvc_s_fcat,
  eg_vari      TYPE disvariant,
  eg_mat_pop   TYPE ty_mat_pop,
  eg_saida_rel TYPE ty_saida_rel,
  eg_simupreca TYPE ztsdd_simupreca,
  eg_t007s     TYPE ty_t007s.

*---------------------------------------------------------------------*
* Declaração: Tabela(s) Interna(s)
*---------------------------------------------------------------------*
DATA:
  tg_twkao     TYPE TABLE OF ty_twkao,
  tg_mara      TYPE TABLE OF ty_mara,
  tg_dados     TYPE TABLE OF zesd_calcula_preco,
  tg_simuprech TYPE TABLE OF ztsdd_simuprech,
  tg_simupreci TYPE TABLE OF ztsdd_simupreci,
  tg_impostos  TYPE zcsd_mon_imp_impostos,
  tg_pcl       TYPE TABLE OF ty_pcl,
  tg_change    TYPE TABLE OF ty_change,
  tg_saida     TYPE TABLE OF zssd_mon_imp_saida,
  tg_listas    TYPE TABLE OF ztsdd_listas_p,
  tg_fieldcat  TYPE TABLE OF lvc_s_fcat,
  tg_mat_pop   TYPE TABLE OF ty_mat_pop,
  tg_saida_rel TYPE TABLE OF ty_saida_rel,
  tg_simupreca TYPE TABLE OF ztsdd_simupreca,
  tg_t007s     TYPE TABLE OF ty_t007s.
*---------------------------------------------------------------------*
* Declaração: Parâmetro(s) de Seleção
*---------------------------------------------------------------------*
SELECTION-SCREEN: BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.

SELECTION-SCREEN BEGIN OF LINE.
PARAMETERS: rb_ped TYPE c RADIOBUTTON GROUP g1 USER-COMMAND c01.                "Por pedido
SELECTION-SCREEN COMMENT (52) TEXT-t65.
SELECTION-SCREEN END OF LINE.
PARAMETERS: rb_mat TYPE c RADIOBUTTON GROUP g1 DEFAULT 'X',    "Por material
            rb_mpc TYPE c RADIOBUTTON GROUP g1,                                 "Por material pré-cadastrado
            rb_sim TYPE c RADIOBUTTON GROUP g1,                                 "Por simulação
            rb_aut TYPE c RADIOBUTTON GROUP g1.                                 "Relatorio Precificação.
SELECTION-SCREEN: END OF BLOCK b1.

SELECTION-SCREEN: BEGIN OF BLOCK b2 WITH FRAME TITLE TEXT-002.
PARAMETERS: p_docsim TYPE ztsdd_simuprech-docsim  MODIF ID sim .                "Documento de Simulação

SELECT-OPTIONS: so_ebeln  FOR ekko-ebeln MODIF ID ped NO INTERVALS NO-EXTENSION,   "Nº do Pedido
                so_matnr  FOR calp-matnr MODIF ID mat,                             "Nº do Material
                so_mati   FOR ztsdd_precadmat-matnr MODIF ID mpc.                  "Nº Material pré cadastrado
PARAMETERS:  p_cagrp  TYPE ztsdd_cod_agrup-cod_agrup MODIF ID mpc.                 "Código de agrupamento
SELECTION-SCREEN: END OF BLOCK b2.

SELECTION-SCREEN: BEGIN OF BLOCK b3 WITH FRAME TITLE TEXT-003 .
PARAMETERS: rb_cad TYPE c RADIOBUTTON GROUP g2  MODIF ID pcb,       "PCB do cadastro
            rb_upo TYPE c RADIOBUTTON GROUP g2  MODIF ID pcb DEFAULT 'X'.                   "PCB do último pedido
SELECTION-SCREEN: END OF BLOCK b3.

SELECTION-SCREEN: BEGIN OF BLOCK b4 WITH FRAME TITLE TEXT-004.
PARAMETERS: p_vkorg TYPE calp-vkorg MODIF ID all DEFAULT 'LB01',      "Organização de vendas
            p_vtweg TYPE calp-vtweg MODIF ID all DEFAULT '10'.        "Canal de distribuição
SELECT-OPTIONS: so_werks FOR ekpo-werks MODIF ID all no INTERVALS no-EXTENSION, "Centro de Compra
                so_pltyp FOR calp-pltyp MODIF ID all,                 "Lista de preços
                so_vkkab FOR calp-vkkab MODIF ID all.                 "Validade
SELECTION-SCREEN: END OF BLOCK b4.

*---------------------------------------------------------------------*
*---------------------------------------------------------------------*
CLASS lcl_event_handler DEFINITION FINAL.

  PUBLIC SECTION.

    METHODS:
      " -- Toolbar --
      handle_toolbar
                    FOR EVENT toolbar OF cl_gui_alv_grid
        IMPORTING e_object,
*                    e_interactive,

      " -- Menu --
*      handle_menu_button

      " -- User Command --
      handle_user_command
                    FOR EVENT user_command OF cl_gui_alv_grid
        IMPORTING e_ucomm,

      " -- Hotspot --
*      handle_hotspot
*                    e_row_id
*                    es_row_no,

      handle_top_of_page
        FOR EVENT top_of_page OF cl_gui_alv_grid,

      handle_data_changed
        FOR EVENT data_changed OF cl_gui_alv_grid,

      handle_data_changed_finished
            FOR EVENT data_changed_finished OF cl_gui_alv_grid
        IMPORTING
*            e_modified
            et_good_cells.

ENDCLASS.                    "lcl_event_handler DEFINITION

**---------------------------------------------------------------------*
**---------------------------------------------------------------------*
*
*
*
*
**
*
**- Adicionar botões:
*
*
*
*
*
*
*
*
*
**
**
*
*
*
**
**          text  = 'Submeter aprovação'. "text-l01.
*
*
*
*
*
*
*        "Verificar material a ser alterado
*
*          "Exibir popup para definição de valor
*
*              EXCEPTIONS
*                        EXCEPTIONS
*
*
*            " Efetuar cálculos com os novos valores
*
*
*                "Preparar dados para cálculo
*
*                "Manter dados de compra
*
*
*
*
*
*
*
*      "Verificar material a ser alterado
*
*          EXCEPTIONS
*
*          "Atribuir valores
*
*              "Preparar dados para cálculo
*
*
*
*              "Manter dados de compra
*
*
*
*
*
*
*
*
*
*
**   Obtém a linha selecionada
*
*
*
*
*
*
*
*        "Função disponível apenas para materiais pré-cadastrados sem referência.
*
*
*
*
*
*
*
*
**   Obtém a linha selecionada
*
*
*
*            EXCEPTIONS
*
*
*
*
*    " Just trigger PAI followed by PBO
*      .
*
*
**   define local data
*
*
*    "Sumarizar alterações no ALV
*
*
*
*
*
*
*
*
*
*
*    "Preparar dados para cálculo
*
*
*
*          EXCEPTIONS
*
*
*
*      "Manter dados de compra
*
*
*
*
*
*
*
*

DATA: vg_custom_container TYPE REF TO cl_gui_custom_container, "Container1
      vg_handler          TYPE REF TO lcl_event_handler. "handler

*&---------------------------------------------------------------------*
*& INITIALIZATION.
*&---------------------------------------------------------------------*
INITIALIZATION.
  so_vkkab-sign = 'I'.
  so_vkkab-option = 'BT'.
  so_vkkab-low = sy-datum + 1.
  so_vkkab-high = '99991231'.
  APPEND so_vkkab.

  so_pltyp-sign = 'I'.
  so_pltyp-option = 'CP'.
  so_pltyp-low = '*'.
  APPEND so_pltyp.
  so_werks-sign = 'I'.
  so_werks-option = 'EQ'.
  so_werks-low =  '0099'.
  append so_werks.


**&---------------------------------------------------------------------*
**&---------------------------------------------------------------------*
*
** Se a seleção for por pedido, habilitar campo de nº de pedido
** e o critério adicional PCB do CE
*
** Se a seleção for por material, habilitar campos de nº de material,
** e o critério adicional PCB do CE
*
** Se a seleção for por material pré-cadastrado, habilitar campos de nº de material pré-cadastrado
** O critério adicional será obrigatoriamente o PCB do cadastro, pois não há essa informação no CE
*
** Se a seleção for por simulação, habilitar apenas o campo de nº de simulação
** Se a seleção for por Relatorio de precificação, habilitar somente Simulacao e Material.
*
*
** Pega os usuários habilitados cadastrados via transação ZXX_PAR2
*
