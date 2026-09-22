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
" ORIGINAL FILE  : zrsd_simulador_preco_imp_f01.abap
" SOURCE         : C:\Users\rsilva14\OneDrive - Capgemini\Documents\workspace\Projetos\projetos_ai\projetos_cap\Cap_Remediation_GenIA\remediation_proc\zrsd_simulador_preco_imp_f01.abap
" SESSION ID     : 7c387103-31fc-42ce-bd7a-ff82d4e490d9
" PROCESSED AT   : 2026-08-10 14:08:21
"====================================================================================================================================

" NAMING ANALYSIS STATUS - Capgemini SAP AI Remediation (ABAP_Move2S4 Workbook)
" Workbook    : Workbook_ABAP_Move2S4_Final.docx
" Package     : ZDEV
" Retrieved   : NO
" Result      : NOT VERIFIED - Workbook not retrievable, manual naming review required
" Scope       : Unable to audit; Workbook_ABAP_Move2S4_Final.docx not found in knowledge base
"--------------------------------------------------------------------------------------------------

*&---------------------------------------------------------------------*
*&  Include           ZRSD_SIMULADOR_PRECO_IMP_F01
*&---------------------------------------------------------------------*
******************************************
*==> Histórico de Versões:
******************************************
*---+--------+----------------+----------------------------------------+
*001|30.04.21|Leandro Chagas  | Ajustes Pré-Migração S/4 <LMB_S4_BM>   +
*---+--------+----------------+----------------------------------------+
*002|31.02.22|Leandro Chagas  |CC.8040 - Incluir novos campos relatório+
*---+--------+----------------+----------------------------------------+
*&---------------------------------------------------------------------*
*&      Form  F_CALL_SCREEN
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_call_screen.

  CALL SCREEN 9000.

ENDFORM.                    " F_CALL_SCREEN

*&---------------------------------------------------------------------*
*&      Form  F_DESCREVE_CAMPOS_GRID
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_descreve_campos_grid .
  DATA: vl_linha TYPE i.
  REFRESH tg_fieldcat.
  IF rb_aut = abap_false.
    vl_linha = 1.
    PERFORM f_fieldcat USING:
        vl_linha 'MATNR'           50 'C' 'C' TEXT-t03 TEXT-t03 ' ' ' ' ' ' 'X' ' '.  "Material
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'MAKTX'           100 'C' 'L' TEXT-t04 TEXT-t04 ' ' ' ' ' ' ' ' ' '.  "Descrição Material
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PLTYP'           50 'C' 'C' TEXT-t01 TEXT-t01 ' ' ' ' ' ' ' ' ' '.  "Lista de preço
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PTEXT'           50 'C' 'L' TEXT-t02 TEXT-t02 ' ' ' ' ' ' ' ' ' '.  "Descrição
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'COD_AGRUP'       50 'C' 'L' TEXT-t66 TEXT-t66 ' ' ' ' ' ' 'X' ' '.  "Código de agrupamento
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'DESC_AGRUP'      50 'C' 'L' TEXT-t67 TEXT-t67 ' ' ' ' ' ' ' ' ' '.  "Descrição do código de agrupamento
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'QTDE_MIN'        50 'C' 'C' TEXT-t07 TEXT-t07 ' ' ' ' ' ' ' ' vg_edit.  "Qtde. Minima
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'VRKME'           50 'C' 'C' TEXT-t09 TEXT-t09 ' ' ' ' ' ' ' ' ' '.  "Unid Medida
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'WERKS'           50 'C' 'C' TEXT-t21 TEXT-t21 ' ' ' ' ' ' ' ' ' '.  "Centro
    vl_linha = vl_linha + 1.
    IF rb_mpc = abap_true.
      PERFORM f_fieldcat USING:
          vl_linha 'ZNOME_FOR'           50 'C' 'L' TEXT-t22 TEXT-t22 ' ' ' ' ' ' ' ' ' '.  "Fornecedor
    ELSE.
      PERFORM f_fieldcat USING:
          vl_linha 'LIFNR'           50 'C' 'L' TEXT-t22 TEXT-t22 ' ' ' ' ' ' ' ' ' '.  "Fornecedor
    ENDIF.
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PCB'             50 'F' 'C' TEXT-t10 TEXT-t10 ' ' ' ' ' ' ' ' ' '.  "PCB
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PCL'             50 'C' 'C' TEXT-t11 TEXT-t11 ' ' ' ' ' ' ' ' ' '.  "PCL
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PRECO_TRANSF'    50 'D' 'C' TEXT-t12 TEXT-t12 ' ' ' ' ' ' ' ' ' '.  "Preço Transferencia
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'RAPPEL'          50 'F' 'C' TEXT-t13 TEXT-t13 ' ' ' ' ' ' ' ' ' '.  "Rappel %
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'CUSTO_LOG'       50 'C' 'C' TEXT-t14 TEXT-t14 ' ' ' ' ' ' ' ' ' '.  "Custo Logistico %
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PV_LIQ'          50 'C' 'C' TEXT-t15 TEXT-t15 ' ' ' ' ' ' ' ' ' '.  "PV Liquido
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PV_FIN'          50 'F' 'C' TEXT-t16 TEXT-t16 ' ' ' ' ' ' ' ' vg_edit.  "PV Final
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'MG_LIQ'          50 'F' 'C' TEXT-t17 TEXT-t17 ' ' ' ' ' ' ' ' ' '.  "Margem Líquida %
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'MG_BRUTA'        50 'F' 'C' TEXT-t18 TEXT-t18 ' ' ' ' ' ' ' ' ' '.  "Margem Bruta %
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'EBELN'           50 'C' 'C' TEXT-t80 TEXT-t80 ' ' ' ' ' ' ' ' ' '.  "Último Pedido    <002> - Inclusão
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'STATUS_I_D'      50 'F' 'C' TEXT-t19 TEXT-t19 ' ' ' ' ' ' ' ' ' '.  "Status aprovação

    vl_linha = vl_linha + 1.
    IF rb_mpc = abap_true.
      PERFORM f_fieldcat USING:
          vl_linha 'QTDE_RS'           50 'C' 'L' TEXT-t96 TEXT-t96 ' ' ' ' ' ' ' ' ' '.  "Quantidade R/S
      vl_linha = vl_linha + 1.
      PERFORM f_fieldcat USING:
          vl_linha 'ZDOLLAR'           50 'F' 'C' TEXT-t97 TEXT-t97 ' ' ' ' ' ' ' ' ' '.  "Dollar FOB
    ENDIF.

    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'EBELN_PNPEDIDO'           50 'C' 'C' TEXT-t9b TEXT-t9b ' ' ' ' ' ' ' ' ' '. "Penúltimo Pedido
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PCB_PNPEDIDO'             50 'F' 'C' TEXT-t9c TEXT-t9c ' ' ' ' ' ' ' ' ' '.  "PCB - Penúltimo Pedido
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'PCL_PNPEDIDO'             50 'C' 'C' TEXT-t9d TEXT-t9d ' ' ' ' ' ' ' ' ' '.  "PCL - Penúltimo Pedido
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'DATA_RECEBIMENTO'         50 'D' 'C' TEXT-t9e TEXT-t9e ' ' ' ' ' ' ' ' ' '.  "Data do recebimento
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
        vl_linha 'DATA_RECEBIMENTO_PN'      50 'D' 'C' TEXT-t9f TEXT-t9f ' ' ' ' ' ' ' ' ' '.  "Data do recebimento
    vl_linha = vl_linha + 1.
    PERFORM f_fieldcat USING:
    vl_linha 'PCB_DIFPER'                   50 'C' 'C' TEXT-t9g TEXT-t9g ' ' ' ' ' ' ' ' ' '.
  ELSE.
    PERFORM f_fieldcat USING:
        '01' 'DOCSIM'          50 'C' 'C' TEXT-t94 TEXT-t94 ' ' ' ' ' ' 'X' ' ',  "Doc. Simulacao.
        '02' 'MATNR'           50 'C' 'C' TEXT-t03 TEXT-t03 ' ' ' ' ' ' 'X' ' ',  "Material
        '03' 'MAKTX'           50 'C' 'L' TEXT-t04 TEXT-t04 ' ' ' ' ' ' ' ' ' ',  "Descrição Material
        '04' 'PLTYP'           50 'C' 'C' TEXT-t01 TEXT-t01 ' ' ' ' ' ' ' ' ' ',  "Lista de preço
        '05' 'PTEXT'           50 'C' 'L' TEXT-t02 TEXT-t02 ' ' ' ' ' ' ' ' ' ',  "Descrição
        '06' 'WERKS'           50 'C' 'C' TEXT-t21 TEXT-t21 ' ' ' ' ' ' ' ' ' ',  "Centro
        '07' 'LIFNR'           50 'C' 'L' TEXT-t22 TEXT-t22 ' ' ' ' ' ' ' ' ' ',  "Fornecedor
        '08' 'PCB'             50 'F' 'C' TEXT-t10 TEXT-t10 ' ' ' ' ' ' ' ' ' ',  "PCB
        '09' 'PCB_EFETIVO'     50 'F' 'C' TEXT-t81 TEXT-t81 ' ' ' ' ' ' ' ' ' ',  "PCB EFETIVO
        '10' 'PCL'             50 'C' 'C' TEXT-t11 TEXT-t11 ' ' ' ' ' ' ' ' ' ',  "PCL
        '11' 'PCL_EFETIVO'     50 'C' 'C' TEXT-t82 TEXT-t82 ' ' ' ' ' ' ' ' ' ',  "PCL EFETIVO
        '12' 'CONDICAO_PCB'    50 'C' 'C' TEXT-t83 TEXT-t83 ' ' ' ' ' ' ' ' ' ',  "CONDICAO PCB
        '13' 'PRECO_TRANSF'    50 'D' 'C' TEXT-t12 TEXT-t12 ' ' ' ' ' ' ' ' ' ',  "Preço Transferencia
        '14' 'PT_EFETIVO'      50 'D' 'C' TEXT-t84 TEXT-t84 ' ' ' ' ' ' ' ' ' ',  "Preço Transf. Efetivo
        '15' 'CONDICAO_PT'     50 'C' 'C' TEXT-t85 TEXT-t85 ' ' ' ' ' ' ' ' ' ',  "CONDICAO PT
        '16' 'RAPPEL'          50 'F' 'C' TEXT-t13 TEXT-t13 ' ' ' ' ' ' ' ' ' ',  "Rappel %
        '17' 'RAPPEL_EFETIVO'  50 'F' 'C' TEXT-t86 TEXT-t86 ' ' ' ' ' ' ' ' ' ',  "Rappel Efetivo
        '18' 'CONDICAO_RAPPEL' 50 'C' 'C' TEXT-t87 TEXT-t87 ' ' ' ' ' ' ' ' ' ',  "CONDICAO RAPPEL
        '19' 'CUSTO_LOG'       50 'C' 'C' TEXT-t14 TEXT-t14 ' ' ' ' ' ' ' ' ' ',  "Custo Logistico %
        '20' 'PV_LIQ'          50 'C' 'C' TEXT-t15 TEXT-t15 ' ' ' ' ' ' ' ' ' ',  "PV Liquido
        '21' 'PVL_EFETIVO'     50 'C' 'C' TEXT-t88 TEXT-t88 ' ' ' ' ' ' ' ' ' ',  "PVL_EFETIVO
        '22' 'PV_FIN'          50 'F' 'C' TEXT-t16 TEXT-t16 ' ' ' ' ' ' ' ' ' ',  "PV Final
        '23' 'PVF_EFETIVO'     50 'F' 'C' TEXT-t89 TEXT-t89 ' ' ' ' ' ' ' ' ' ',  "PVF_EFETIVO
        '24' 'MG_LIQ'          50 'F' 'C' TEXT-t17 TEXT-t17 ' ' ' ' ' ' ' ' ' ',  "Margem Líquida %
        '25' 'MGL_EFETIVO'     50 'F' 'C' TEXT-t90 TEXT-t90 ' ' ' ' ' ' ' ' ' ',  "Margem Líquida Efetiva
        '26' 'MG_BRUTA'        50 'F' 'C' TEXT-t18 TEXT-t18 ' ' ' ' ' ' ' ' ' ',  "Margem Bruta %
        '27' 'MGB_EFETIVO'     50 'F' 'C' TEXT-t91 TEXT-t91 ' ' ' ' ' ' ' ' ' ',  "Margem Bruta Efetivo
        '28' 'CONDICAO_PVF'    50 'C' 'C' TEXT-t92 TEXT-t92 ' ' ' ' ' ' ' ' ' ',  "CONDICAO PVF
        '29' 'MSG_AUTOM'      130 'C' 'C' TEXT-t93 TEXT-t93 ' ' ' ' ' ' ' ' ' '.  "Mensagem Automatização

  ENDIF.
ENDFORM.                    " F_DESCREVE_CAMPOS_GRID
*&---------------------------------------------------------------------*
*&      Form  F_FIELDCAT
*&---------------------------------------------------------------------*
*       Monta estrutura de campos para ALV
*----------------------------------------------------------------------*
FORM f_fieldcat  USING     p_col         "Coluna
                           p_fieldname   "Nome de campo de tabela interna
                           p_intlen      "Comprimento interno em Bytes
                           p_inttype     "Ctg.dados ABAP (C,D,N,...)
                           p_just        "Alinhamento
                           p_tooltip     "Info sobre o botão para título de coluna
                           p_coltext     "Título de coluna
                           p_soma        "Somar
                           p_hotspot     "Hotspot
                           p_icon        "Ícone
                           p_no_zero     "Sem zeros na saída
                           p_edit.       "Campo editável

  CLEAR eg_fieldcat.
  eg_fieldcat-col_pos               = p_col.
  eg_fieldcat-fieldname             = p_fieldname.
  eg_fieldcat-intlen                = p_intlen.
  eg_fieldcat-inttype               = p_inttype.
  eg_fieldcat-just                  = p_just.
  eg_fieldcat-tooltip               = p_tooltip.
  eg_fieldcat-coltext               = p_coltext.
  eg_fieldcat-do_sum                = p_soma.
  eg_fieldcat-hotspot               = p_hotspot.
  eg_fieldcat-icon                  = p_icon.
  eg_fieldcat-no_zero               = p_no_zero.
  eg_fieldcat-col_opt               = abap_true.
  eg_fieldcat-edit                  = p_edit.

* Definir decimais
  IF p_inttype EQ 'F'.
    eg_fieldcat-decimals = 2.
    IF p_fieldname EQ 'MG_LIQ' OR p_fieldname EQ 'MG_BRUTA'.
      eg_fieldcat-decimals = 3.
    ENDIF.
  ENDIF.

  IF p_fieldname EQ 'QTDE_MIN' AND rb_mat NE space.
    eg_fieldcat-no_out = abap_true.
  ENDIF.

  APPEND eg_fieldcat TO tg_fieldcat.

ENDFORM.                    " F_FIELDCAT
*&---------------------------------------------------------------------*
*&      Form  F_LAYOUT_GRID
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_layout_grid .

  CLEAR: vg_layout.
  vg_layout-zebra       = abap_true.
  vg_layout-cwidth_opt  = abap_true.
* Field that identify cell color in internal table
  "--------------------------------------------------------------------------------------------------
  " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
  " Reason     : MOVE statement is obsolete and should be replaced with direct assignment.
  " RAG Source : Workbook_ABAP_Move2S4_Final.docx
  " Antes      :
  "   MOVE 'COLOR_CELL' TO vg_layout-ctab_fname.
  "   MOVE 'CELLTAB' TO vg_layout-stylefname.
  "--------------------------------------------------------------------------------------------------
  vg_layout-ctab_fname = 'COLOR_CELL'.
  vg_layout-stylefname = 'CELLTAB'.
  "--------------------------------------------------------------------------------------------------
  " END OF MODIFICATION - Capgemini SAP AI Remediation
  "--------------------------------------------------------------------------------------------------
ENDFORM.                    " F_LAYOUT_GRID

*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM event_top_of_page USING  p_dyndoc_id TYPE REF TO cl_dd_document.

  DATA : vl_text(255) TYPE c.  "Text

* Preencher TOP OF PAGE
  IF p_docsim IS NOT INITIAL.
    CLEAR : vl_text.
    "--------------------------------------------------------------------------------------------------
    " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
    " Issue      : Uses obsolete CONCATENATE statement instead of modern string templates
    " RAG Source : From Classic ABAP to ABAP.pdf
    " Impact     : While functional, string templates provide better performance and readability in S/4HANA
    "--------------------------------------------------------------------------------------------------
    " Recommended code (suggestion — not applied):
    "   vl_text = |Documento de Simulação: { p_docsim }|.
    "--------------------------------------------------------------------------------------------------
    vl_text = |Documento de Simulação: { p_docsim }|.

    PERFORM add_text USING vl_text.

    CALL METHOD p_dyndoc_id->new_line.
  ENDIF.
  IF rb_aut = abap_false.
    CLEAR : vl_text.
    "--------------------------------------------------------------------------------------------------
    " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
    " Issue      : Uses obsolete CONCATENATE statement instead of modern string templates
    " RAG Source : From Classic ABAP to ABAP.pdf
    " Impact     : While functional, string templates provide better performance and readability in S/4HANA
    "--------------------------------------------------------------------------------------------------
    " Recommended code (suggestion — not applied):
    "   vl_text = |GP: { vg_gp } - { vg_gpname }|.
    "--------------------------------------------------------------------------------------------------
    vl_text = |GP: { vg_gp } - { vg_gpname }|.
    PERFORM add_text USING vl_text.
  ENDIF.
*
**

* Populating data to html control
  PERFORM html.

ENDFORM.                    " EVENT_TOP_OF_PAGE
*&---------------------------------------------------------------------*
*&      Form  ADD_TEXT
*&---------------------------------------------------------------------*
*       To add Text
*----------------------------------------------------------------------*
FORM add_text USING p_text TYPE sdydo_text_element.
* Adding text
  CALL METHOD vg_dyndoc_id->add_text
    EXPORTING
      text         = p_text
      sap_emphasis = cl_dd_area=>heading.
ENDFORM.                    " ADD_TEXT
*&---------------------------------------------------------------------*
*&      Form  HTML
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
FORM html.

  DATA : "vl_length        TYPE i,                           " Length
         vl_background_id TYPE sdydo_key VALUE space. " Background_id
* Creating html control
  IF vg_html_cntrl IS INITIAL.
    CREATE OBJECT vg_html_cntrl
      EXPORTING
        parent = vg_parent_html.
  ENDIF.
* Reuse_alv_grid_commentary_set
  CALL FUNCTION 'REUSE_ALV_GRID_COMMENTARY_SET'
    EXPORTING
      document = vg_dyndoc_id
      bottom   = space.

  CALL METHOD vg_dyndoc_id->merge_document.

  CALL METHOD vg_dyndoc_id->set_document_background
    EXPORTING
      picture_id = vl_background_id.

  vg_dyndoc_id->html_control = vg_html_cntrl.

* Display TOP document
  CALL METHOD vg_dyndoc_id->display_document
    EXPORTING
      reuse_control      = 'X'
      parent             = vg_parent_html
    EXCEPTIONS
      html_display_error = 1.

ENDFORM.                    " HTML
*&---------------------------------------------------------------------*
*&      Form  F_CREATE_AND_INIT_ALV
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_create_and_init_alv .
  DATA: lt_exclude TYPE ui_functions.

  CREATE OBJECT vg_custom_container
    EXPORTING
      container_name = c_container.

  CREATE OBJECT vg_dyndoc_id
    EXPORTING
      style = 'ALV_GRID'.

  CREATE OBJECT vg_splitter
    EXPORTING
      parent  = vg_custom_container
      rows    = 2
      columns = 1.

* to receiving containers vg_parent_html and vg_parent_grid
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_parent_html = vg_splitter->get_container( row = 1 column = 1 ).
  "--------------------------------------------------------------------------------------------------
  vg_parent_html = vg_splitter->get_container( row = 1 column = 1 ).

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_splitter->set_row_height( id = 1 height = 10 ).
  "--------------------------------------------------------------------------------------------------
vg_splitter->set_row_height( id = 1 height = 10 ).

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_parent_grid = vg_splitter->get_container( row = 2 column = 1 ).
  "--------------------------------------------------------------------------------------------------
  vg_parent_grid = vg_splitter->get_container( row = 2 column = 1 ).

  CREATE OBJECT vg_grid
    EXPORTING
      i_parent = vg_parent_grid.


  PERFORM f_layout_grid.

* setting focus for created grid control
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   cl_gui_control=>set_focus( control = vg_grid ).
  "--------------------------------------------------------------------------------------------------
cl_gui_control=>set_focus( control = vg_grid ).

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_grid->register_edit_event( i_event_id = cl_gui_alv_grid=>mc_evt_enter ).
  "--------------------------------------------------------------------------------------------------
vg_grid->register_edit_event( i_event_id = cl_gui_alv_grid=>mc_evt_enter ).

  CREATE OBJECT vg_handler.
  SET HANDLER vg_handler->handle_top_of_page FOR vg_grid.
  SET HANDLER vg_handler->handle_toolbar FOR vg_grid.
  SET HANDLER vg_handler->handle_user_command FOR vg_grid.
  SET HANDLER vg_handler->handle_data_changed FOR vg_grid.
  SET HANDLER vg_handler->handle_data_changed_finished FOR vg_grid.

  PERFORM f_descreve_campos_grid.

  PERFORM f_exclude_tb_functions CHANGING lt_exclude.

**Variant to save the layout
  eg_vari-report      = sy-repid.
  eg_vari-log_group   = space.
  eg_vari-username    = space.
  eg_vari-variant     = space.
  eg_vari-text        = space.
  eg_vari-dependvars  = space.
  eg_vari-handle      = 'GRID'.

**Calling the Method for ALV output
  IF rb_aut = abap_false.

    CALL METHOD vg_grid->set_table_for_first_display
      EXPORTING
        it_toolbar_excluding = lt_exclude
        is_variant           = eg_vari
        is_layout            = vg_layout
        i_save               = 'A'
      CHANGING
        it_fieldcatalog      = tg_fieldcat
        it_outtab            = tg_saida[].
  ELSE.

    CALL METHOD vg_grid->set_table_for_first_display
      EXPORTING
        it_toolbar_excluding = lt_exclude
        is_variant           = eg_vari
        is_layout            = vg_layout
        i_save               = 'A'
      CHANGING
        it_fieldcatalog      = tg_fieldcat
        it_outtab            = tg_saida_rel[].
  ENDIF.
* Initializing document
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_dyndoc_id->initialize_document( ).
  "--------------------------------------------------------------------------------------------------
  vg_dyndoc_id->initialize_document( ).

* Processing events
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_grid->list_processing_events( i_event_name = 'TOP_OF_PAGE' i_dyndoc_id = vg_dyndoc_id ).
  "--------------------------------------------------------------------------------------------------
vg_grid->list_processing_events( i_event_name = 'TOP_OF_PAGE' i_dyndoc_id = vg_dyndoc_id ).
  "end }
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Obsolete CALL METHOD syntax for functional method calls
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, modern ABAP prefers functional method calls for better readability and performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   vg_grid->set_ready_for_input( i_ready_for_input = 1 ).
  "--------------------------------------------------------------------------------------------------
  vg_grid->set_ready_for_input( i_ready_for_input = 1 ).

ENDFORM.                    " F_CREATE_AND_INIT_ALV
*&---------------------------------------------------------------------*
*&      Form  F_EXCLUDE_TB_FUNCTIONS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_exclude_tb_functions CHANGING pt_exclude TYPE ui_functions.
* Only allow to change data not to create new entries (exclude
* generic functions).
  DATA ls_exclude TYPE ui_func.

  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_copy_row.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_delete_row.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_append_row.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_insert_row.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_move_row.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_copy.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_cut.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_paste.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_paste_new_row.
  APPEND ls_exclude TO pt_exclude.
  ls_exclude = cl_gui_alv_grid=>mc_fc_loc_undo.
  APPEND ls_exclude TO pt_exclude.
ENDFORM.                               " F_EXCLUDE_TB_FUNCTIONS

*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_PVFINAL
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_seleciona_pvfinal .
  DATA: vl_kbetr TYPE konp-kbetr.
  CONSTANTS: c_valor TYPE p DECIMALS 2 VALUE '0.01'.

  IF tg_mara[] IS NOT INITIAL.
    "Buscar preço de venda final
    "--------------------------------------------------------------------------------------------------
    " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
    " Reason     : Replace obsolete SELECT...ENDSELECT with modern SELECT SINGLE and use host variables with @ escape character.
    " RAG Source : From Classic ABAP to ABAP.pdf
    " Antes      :
    "   SELECT b~kbetr UP TO 1 ROWS
    "     INTO vl_kbetr
    "     FROM a155 AS a INNER JOIN konp AS b
    "       ON ( a~knumh = b~knumh
    "           AND a~kschl = b~kschl )
    "       WHERE a~kappl = 'V'
    "         AND a~kschl = 'VKP0'
    "         AND a~vkorg = eg_twkao-vkorg
    "         AND a~vtweg = eg_twkao-vtweg
    "         AND a~pltyp = eg_twkao-pltyp
    "         AND a~matnr = eg_mara-matnr
    "         AND a~vrkme = eg_mara-meins
    "         AND a~datbi >= so_vkkab-low
    "         AND a~datab <= so_vkkab-low
    "         AND b~kschl = 'VKP0'
    "     ORDER BY a~knumh.  " <LMB_S4_BM>
    "   ENDSELECT.
    "--------------------------------------------------------------------------------------------------
    SELECT SINGLE b~kbetr
      INTO @vl_kbetr
      FROM a155 AS a INNER JOIN konp AS b
        ON ( a~knumh = b~knumh
            AND a~kschl = b~kschl )
        WHERE a~kappl = 'V'
          AND a~kschl = 'VKP0'
          AND a~vkorg = @eg_twkao-vkorg
          AND a~vtweg = @eg_twkao-vtweg
          AND a~pltyp = @eg_twkao-pltyp
          AND a~matnr = @eg_mara-matnr
          AND a~vrkme = @eg_mara-meins
          AND a~datbi >= @so_vkkab-low
          AND a~datab <= @so_vkkab-low
          AND b~kschl = 'VKP0'
      ORDER BY a~knumh.
    "--------------------------------------------------------------------------------------------------
    " END OF MODIFICATION - Capgemini SAP AI Remediation
    "--------------------------------------------------------------------------------------------------
    "--------------------------------------------------------------------------------------------------
    " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
    " Issue      : Using EQ operator instead of modern comparison operator.
    " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
    " Impact     : While functional, modern ABAP syntax improves code readability and follows current best practices.
    "--------------------------------------------------------------------------------------------------
    " Recommended code (suggestion — not applied):
    "       IF sy-subrc = 0.
    "--------------------------------------------------------------------------------------------------
    IF IF sy-subrc = 0.
      CALL FUNCTION 'PRICE_POINT_READ'
        EXPORTING
          pi_vkorg                   = 'LB01'
          pi_vtweg                   = '10'
          pi_rktyp                   = 'A'
          pi_eprgr                   = 'ZLMB07'
          pi_price                   = vl_kbetr
          pi_waers                   = 'BRL'
          pi_datam                   = sy-datum
          pi_kurst                   = 'M'
          pi_hwaer                   = 'BRL'
          pi_mfact                   = '1'
        IMPORTING
          pe_price                   = vl_kbetr
        EXCEPTIONS
          no_price_point_group_found = 1
          no_price_points_maintained = 2
          conversion_not_found       = 3
          OTHERS                     = 4.

      eg_saida-pv_fin = vl_kbetr.
    ELSE.
      eg_saida-pv_fin = c_valor.
    ENDIF.
  ELSE.
    eg_saida-pv_fin = c_valor.
  ENDIF.

ENDFORM.                    " F_SELECIONA_PVFINAL
*&---------------------------------------------------------------------*
*&      Form  F_DESC_STATUS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_desc_status .

  CASE eg_saida-status_i.
    WHEN 10.
      eg_saida-status_i_d = c_stat_10.
    WHEN 20.
      eg_saida-status_i_d = c_stat_20.
    WHEN 30.
      eg_saida-status_i_d = c_stat_30.
    WHEN space.
      eg_saida-status_i_d = c_stat_00.
  ENDCASE.

ENDFORM.                    " F_DESC_STATUS
*&---------------------------------------------------------------------*
*&      Form  F_SALVAR_DADOS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_salvar_dados .
  DATA: vl_answer,
        vl_question(100),
        vl_objkey        TYPE swo_typeid,
        vl_retcode       TYPE sy-subrc,
        tl_simupreci     TYPE TABLE OF ztsdd_simupreci.

  IF vg_edit IS INITIAL.
    "Documento de simulação já submetido à aprovação. Não pode ser alterado.
    MESSAGE s096(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
    EXIT.
  ENDIF.

  CALL FUNCTION 'POPUP_TO_CONFIRM'
    EXPORTING
      titlebar              = TEXT-q01
      text_question         = TEXT-q02
      text_button_1         = 'Sim'(006)
      text_button_2         = 'Não'(007)
      display_cancel_button = ' '
    IMPORTING
      answer                = vl_answer
    EXCEPTIONS
      text_not_found        = 1
      OTHERS                = 2.

  IF sy-subrc EQ 0 AND vl_answer EQ '1'.

    IF p_docsim IS INITIAL.
* Gerar novo número de Documento de Simulação
      CALL FUNCTION 'NUMBER_RANGE_ENQUEUE'
        EXPORTING
          object           = 'ZSD_DOCSIM'
        EXCEPTIONS
          foreign_lock     = 1
          object_not_found = 2
          system_failure   = 3
          OTHERS           = 4.
      IF sy-subrc EQ 0.
        CALL FUNCTION 'NUMBER_GET_NEXT'
          EXPORTING
            nr_range_nr             = '1'
            object                  = 'ZSD_DOCSIM'
            quantity                = 1
          IMPORTING
            number                  = p_docsim
          EXCEPTIONS
            interval_not_found      = 1
            number_range_not_intern = 2
            object_not_found        = 3
            quantity_is_0           = 4
            quantity_is_not_1       = 5
            interval_overflow       = 6
            buffer_overflow         = 7
            OTHERS                  = 8.
        IF sy-subrc NE 0.
          CLEAR p_docsim.
        ENDIF.
        CALL FUNCTION 'NUMBER_RANGE_DEQUEUE'
          EXPORTING
            object = 'ZSD_DOCSIM'.
      ENDIF.
      IF p_docsim IS INITIAL.
        "Erro ao gravar. Verificar intervalo de numeração ZSD_DOCSIM.
        MESSAGE s083(zmmm_classe_mensagem) DISPLAY LIKE 'E'.
        vg_erro = abap_true.
        EXIT.
      ENDIF.
    ENDIF.

    CHECK vg_erro IS INITIAL.

    CLEAR: eg_simuprech, eg_simupreci.

    "--------------------------------------------------------------------------------------------------
    " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
    " Issue      : READ TABLE without BINARY SEARCH on potentially large internal table may cause performance issues
    " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
    " Impact     : Linear search performance degrades with table size, especially problematic in S/4HANA with larger data volumes
    "--------------------------------------------------------------------------------------------------
    " Recommended code (suggestion — not applied):
    "   SORT tg_simuprech BY docsim.
    "   READ TABLE tg_simuprech INTO eg_simuprech WITH KEY docsim = p_docsim BINARY SEARCH.
    "--------------------------------------------------------------------------------------------------
    IF rb_sim NE space. "Buscar dados de cabeçalho utilizados na criação do documento de simulação
      SORT tg_simuprech BY docsim.
      READ TABLE tg_simuprech INTO eg_simuprech WITH KEY docsim = p_docsim BINARY SEARCH.
    ELSE.  "Novo documento de simulação
      eg_simuprech-docsim = p_docsim.
      eg_simuprech-vkorg = p_vkorg.
      eg_simuprech-vtweg = p_vtweg.
      "--------------------------------------------------------------------------------------------------
      " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
      " Issue      : READ TABLE by index without checking sy-subrc may cause runtime errors if table is empty
      " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
      " Impact     : Potential short dump if so_vkkab table is empty, reducing system stability
      "--------------------------------------------------------------------------------------------------
      " Recommended code (suggestion — not applied):
      "   READ TABLE so_vkkab INDEX 1.
      "   IF sy-subrc = 0.
      "     eg_simuprech-vkkab = so_vkkab-low.
      "   ENDIF.
      "--------------------------------------------------------------------------------------------------
      READ TABLE so_vkkab INDEX 1.
      IF sy-subrc = 0.
        eg_simuprech-vkkab = so_vkkab-low.
      ENDIF.
      eg_simuprech-vkkbi = '99991231'.

      IF rb_ped NE space.
        eg_simuprech-selecao = 1.
      ELSEIF rb_mat NE space.
        eg_simuprech-selecao = 2.
      ELSEIF rb_mpc NE space.
        eg_simuprech-selecao = 3.
      ENDIF.
      eg_simuprech-gp = vg_gp.
      eg_simuprech-dgp = vg_dgp.
    ENDIF.

    eg_simuprech-uname = sy-uname.
    eg_simuprech-datum = sy-datum.
    eg_simuprech-uzeit = sy-uzeit.

    "Status de aprovação do documento
    eg_simuprech-status_d = space. "Não enviado para aprovação

    MODIFY ztsdd_simuprech FROM eg_simuprech.
    IF sy-subrc EQ 0.
      COMMIT WORK.
    ENDIF.
    CLEAR eg_simuprech.

* Dados de Item
    FREE: tl_simupreci.
    LOOP AT tg_saida INTO eg_saida.
      eg_simupreci-mandt          = sy-mandt.
      eg_simupreci-docsim         = p_docsim.
      eg_simupreci-pltyp          = eg_saida-pltyp.
      eg_simupreci-matnr          = eg_saida-matnr.
      eg_simupreci-werks          = eg_saida-werks.
      eg_simupreci-lifnr          = eg_saida-lifnr.
      eg_simupreci-qtde_min       = eg_saida-qtde_min.
      eg_simupreci-vrkme          = eg_saida-vrkme.
      eg_simupreci-pcb            = eg_saida-pcb.
      eg_simupreci-pcl            = eg_saida-pcl.
      eg_simupreci-preco_transf   = eg_saida-preco_transf.
      eg_simupreci-rappel         = eg_saida-rappel.
      eg_simupreci-custo_log      = eg_saida-custo_log.
      eg_simupreci-pv_liq         = eg_saida-pv_liq.
      eg_simupreci-pv_fin         = eg_saida-pv_fin.
      eg_simupreci-mg_liq         = eg_saida-mg_liq.
      eg_simupreci-mg_bruta       = eg_saida-mg_bruta.
      eg_simupreci-status_i       = space. "Não enviado para aprovação

      eg_simupreci-pclst                = eg_saida-pclst.
      eg_simupreci-lco                  = eg_saida-custo_log.
      eg_simupreci-rate_icms            = eg_saida-rate_icms.
      eg_simupreci-base_icms            = eg_saida-base_icms.
      eg_simupreci-cust_icms            = eg_saida-cust_icms.
      eg_simupreci-val_icms             = eg_saida-val_icms.
      eg_simupreci-rate_icms_st         = eg_saida-rate_icms_st.
      eg_simupreci-base_icms_st         = eg_saida-base_icms_st.
      eg_simupreci-rate_icms_venda      = eg_saida-rate_icms_venda.
      eg_simupreci-base_icms_venda      = eg_saida-base_icms_venda.
      eg_simupreci-rate_icms_st_int     = eg_saida-rate_icms_st_int.
      eg_simupreci-base_icms_st_int     = eg_saida-base_icms_st_int.
      eg_simupreci-base_red_1           = eg_saida-base_red_1.
      eg_simupreci-base_red_2           = eg_saida-base_red_2.
      eg_simupreci-val_base_st          = eg_saida-val_base_st.
      eg_simupreci-val_icms_st          = eg_saida-val_icms_st.
      eg_simupreci-rate_ipi             = eg_saida-rate_ipi.
      eg_simupreci-base_ipi             = eg_saida-base_ipi.
      eg_simupreci-val_ipi              = eg_saida-val_ipi.
      eg_simupreci-rate_cofins          = eg_saida-rate_cofins.
      eg_simupreci-base_cofins          = eg_saida-base_cofins.
      eg_simupreci-val_cofins           = eg_saida-val_cofins.
      eg_simupreci-rate_pis             = eg_saida-rate_pis.
      eg_simupreci-base_pis             = eg_saida-base_pis.
      eg_simupreci-val_pis              = eg_saida-val_pis.
      eg_simupreci-val_rappel           = eg_saida-val_rappel.
      eg_simupreci-val_custo_log        = eg_saida-val_custo_log.
      eg_simupreci-total_imp_venda      = eg_saida-total_imp_venda.
      eg_simupreci-c_mvto               = eg_saida-c_mvto.
      eg_simupreci-c_pallet             = eg_saida-c_pallet.
      eg_simupreci-frete                = eg_saida-frete.
      eg_simupreci-tx_fin               = eg_saida-tx_fin.
      eg_simupreci-tx_gest              = eg_saida-tx_gest.
      eg_simupreci-c_arm                = eg_saida-c_arm.
      eg_simupreci-umrez                = eg_saida-umrez.
      eg_simupreci-hoehe                = eg_saida-hoehe.
      eg_simupreci-breit                = eg_saida-breit.
      eg_simupreci-laeng                = eg_saida-laeng.
      eg_simupreci-tx_mov               = eg_saida-tx_mov.
      eg_simupreci-tx_frete             = eg_saida-tx_frete.
      eg_simupreci-custo_ins_pallet     = eg_saida-custo_ins_pallet.
      eg_simupreci-dias_est             = eg_saida-dias_est.
      eg_simupreci-custo_armazen        = eg_saida-custo_armazen.
      eg_simupreci-cod_agrup            = eg_saida-cod_agrup.
      eg_simupreci-desc_agrup           = eg_saida-desc_agrup.
      eg_simupreci-rate_icms_comp       = eg_saida-rate_icms_comp.
      eg_simupreci-base_icms_comp       = eg_saida-base_icms_comp.
      eg_simupreci-val_icms_comp        = eg_saida-val_icms_comp.
      eg_simupreci-rate_ipi_comp        = eg_saida-rate_ipi_comp.
      eg_simupreci-base_ipi_comp        = eg_saida-base_ipi_comp.
      eg_simupreci-val_ipi_comp         = eg_saida-val_ipi_comp.
      eg_simupreci-rate_cofins_comp     = eg_saida-rate_cofins_comp.
      eg_simupreci-base_cofins_comp     = eg_saida-base_cofins_comp.
      eg_simupreci-val_cofins_comp      = eg_saida-val_cofins_comp.
      eg_simupreci-rate_pis_comp        = eg_saida-rate_pis_comp.
      eg_simupreci-base_pis_comp        = eg_saida-base_pis_comp.
      eg_simupreci-val_pis_comp         = eg_saida-val_pis_comp.
      eg_simupreci-calc_base_st_comp    = eg_saida-calc_base_st_comp.
      eg_simupreci-calc_icms_st_comp    = eg_saida-calc_icms_st_comp.
      eg_simupreci-maj_bst_comp         = eg_saida-maj_bst_comp.
      eg_simupreci-maj_bicms_comp       = eg_saida-maj_bicms_comp.
      eg_simupreci-calc_pis_st_comp     = eg_saida-calc_pis_st_comp.
      eg_simupreci-calc_cofins_st_comp  = eg_saida-calc_cofins_st_comp.
      eg_simupreci-rate_icms_st_comp    = eg_saida-rate_icms_st_comp.
      eg_simupreci-rate_st_int_comp     = eg_saida-rate_st_int_comp.
      eg_simupreci-var_cust_log         = eg_saida-var_cust_log.
      eg_simupreci-uf_precad            = eg_saida-uf_precad.
      eg_simupreci-fob                  = eg_saida-fob.
      eg_simupreci-despachante          = eg_saida-despachante.
      eg_simupreci-tx_fob               = eg_saida-tx_fob.
      eg_simupreci-tx_despachante       = eg_saida-tx_desp.
      eg_simupreci-gestao               = eg_saida-gestao.
      eg_simupreci-fin                  = eg_saida-fin.
      APPEND eg_simupreci TO tl_simupreci.
      CLEAR eg_simupreci.
    ENDLOOP.
    IF NOT tl_simupreci[] IS INITIAL.
      "--------------------------------------------------------------------------------------------------
      " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
      " Issue      : Direct database modification without error handling or logging could impact data integrity in S/4HANA
      " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
      " Impact     : Potential data inconsistency if the operation fails partially, and no audit trail for troubleshooting
      "--------------------------------------------------------------------------------------------------
      " Recommended code (suggestion — not applied):
      "   TRY.
      "           MODIFY ztsdd_simupreci FROM TABLE tl_simupreci.
      "           IF sy-subrc = 0.
      "             COMMIT WORK.
      "           ELSE.
      "             ROLLBACK WORK.
      "             MESSAGE e001(z_custom) WITH 'Error modifying simulation data'.
      "           ENDIF.
      "         CATCH cx_sy_open_sql_db INTO DATA(lx_db_error).
      "           ROLLBACK WORK.
      "           MESSAGE e002(z_custom) WITH lx_db_error->get_text( ).
      "         ENDTRY.
      "--------------------------------------------------------------------------------------------------
        TRY.
                MODIFY ztsdd_simupreci FROM TABLE tl_simupreci.
                IF sy-subrc = 0.
                  COMMIT WORK.
                ELSE.
                  ROLLBACK WORK.
                  MESSAGE e001(z_custom) WITH 'Error modifying simulation data'.
                ENDIF.
      CATCH cx_sy_open_sql_db INTO DATA(lx_db_error).
        ROLLBACK WORK.
        MESSAGE e002(z_custom) WITH lx_db_error->get_text( ).
      ENDTRY.
    ENDIF.
* Simulação & foi gravada. Deseja submetê-la à aprovação?
    CONCATENATE TEXT-q03 p_docsim TEXT-q04 INTO vl_question SEPARATED BY space.

    CALL FUNCTION 'POPUP_TO_CONFIRM'
      EXPORTING
        titlebar              = TEXT-q01
        text_question         = vl_question
        text_button_1         = 'Sim'(006)
        text_button_2         = 'Não'(007)
        display_cancel_button = ' '
      IMPORTING
        answer                = vl_answer
      EXCEPTIONS
        text_not_found        = 1
        OTHERS                = 2.
    IF sy-subrc EQ 0 AND vl_answer EQ 1.
      vl_objkey = p_docsim.

      CALL FUNCTION 'SAP_WAPI_CREATE_EVENT'
        EXPORTING
          object_type    = 'ZWF_DOCSIM'
          object_key     = vl_objkey
          event          = 'SENT_TO_APPROVAL'
          commit_work    = 'X'
          event_language = sy-langu
          language       = sy-langu
          user           = sy-uname
        IMPORTING
          return_code    = vl_retcode.

      IF vl_retcode EQ 0.
        "--------------------------------------------------------------------------------------------------
        " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
        " Issue      : Direct UPDATE statement without proper error handling and transaction management
        " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
        " Impact     : Risk of data inconsistency if subsequent operations fail, no rollback mechanism
        "--------------------------------------------------------------------------------------------------
        " Recommended code (suggestion — not applied):
        "   TRY.
        "             UPDATE ztsdd_simuprech SET status_d = 10
        "                                    WHERE docsim = p_docsim.
        "             IF sy-subrc <> 0.
        "               ROLLBACK WORK.
        "               MESSAGE e003(z_custom) WITH 'Failed to update header status'.
        "             ENDIF.
        "           CATCH cx_sy_open_sql_db INTO DATA(lx_error).
        "             ROLLBACK WORK.
        "             MESSAGE e004(z_custom) WITH lx_error->get_text( ).
        "           ENDTRY.
        "--------------------------------------------------------------------------------------------------
        UPDATE ztsdd_simuprech SET status_d = 10  "Em aprovação
                               WHERE docsim EQ p_docsim.
        IF sy-subrc EQ 0.
          "--------------------------------------------------------------------------------------------------
          " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
          " Issue      : Direct UPDATE statement without proper error handling, nested within another UPDATE operation
          " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
          " Impact     : Potential for partial updates leaving data in inconsistent state, difficult to troubleshoot failures
          "--------------------------------------------------------------------------------------------------
          " Recommended code (suggestion — not applied):
          "   TRY.
          "               UPDATE ztsdd_simupreci SET status_i = 10
          "                                      WHERE docsim = p_docsim.
          "               IF sy-subrc <> 0.
          "                 ROLLBACK WORK.
          "                 MESSAGE e005(z_custom) WITH 'Failed to update item status'.
          "               ENDIF.
          "             CATCH cx_sy_open_sql_db INTO DATA(lx_item_error).
          "               ROLLBACK WORK.
          "               MESSAGE e006(z_custom) WITH lx_item_error->get_text( ).
          "             ENDTRY.
          "--------------------------------------------------------------------------------------------------
          UPDATE ztsdd_simupreci SET status_i = 10  "Aguardando aprovação
                                WHERE docsim EQ p_docsim.
          IF sy-subrc EQ 0.
            COMMIT WORK.
            "Documento de simulação & foi submetido à aprovação.
            MESSAGE i100(zmsd_classe_mensagem) WITH p_docsim.
          ENDIF.
        ENDIF.
        LEAVE TO SCREEN 0.
      ELSE.
        "Erro ao submeter documento de simulação & à aprovação. Tentar novamente.
        MESSAGE i099(zmsd_classe_mensagem) WITH p_docsim DISPLAY LIKE 'E'.
        LEAVE TO SCREEN 0.
      ENDIF.
    ENDIF.

    "Documento de simulação & gravado com sucesso.
    MESSAGE i088(zmsd_classe_mensagem) WITH p_docsim.
    LEAVE TO SCREEN 0.
  ENDIF.
ENDFORM.                    " F_SALVAR_DADOS
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_MATERIAL_CENTRO
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_seleciona_material_centro.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Uses obsolete header line syntax which is deprecated in modern ABAP
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : Header lines reduce code readability and maintainability, and are discouraged in S/4HANA development
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   DATA: tl_fieldcat TYPE slis_t_fieldcat_alv,
  "         ls_fieldcat TYPE slis_fieldcat_alv.
  "--------------------------------------------------------------------------------------------------
  DATA: tl_fieldcat TYPE slis_t_fieldcat_alv WITH HEADER LINE.

* Montar fieldcat para popup
  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'CHECK'.
  tl_fieldcat-seltext_m = space.
  tl_fieldcat-outputlen = 1.
  tl_fieldcat-checkbox = 'X'.
  tl_fieldcat-input = 'X'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Uses obsolete APPEND and CLEAR pattern with header line
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is deprecated and should be replaced with modern ABAP syntax for better maintainability
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND ls_fieldcat TO tl_fieldcat.
  "   CLEAR ls_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'MATNR'.
  tl_fieldcat-seltext_m = 'Material'.
  tl_fieldcat-outputlen = 20.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Uses obsolete APPEND and CLEAR pattern with header line
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is deprecated and should be replaced with modern ABAP syntax for better maintainability
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND ls_fieldcat TO tl_fieldcat.
  "   CLEAR ls_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'WERKS'.
  tl_fieldcat-seltext_m = 'Centro'.
  tl_fieldcat-outputlen = 4.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Uses obsolete APPEND and CLEAR pattern with header line
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is deprecated and should be replaced with modern ABAP syntax for better maintainability
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND ls_fieldcat TO tl_fieldcat.
  "   CLEAR ls_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'MAKTX'.
  tl_fieldcat-seltext_m = 'Descrição'.
  tl_fieldcat-outputlen = 60.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Uses obsolete APPEND and CLEAR pattern with header line
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is deprecated and should be replaced with modern ABAP syntax for better maintainability
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND ls_fieldcat TO tl_fieldcat.
  "   CLEAR ls_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

* Dados do Popup
  REFRESH tg_mat_pop.
  CLEAR eg_mat_pop.

  LOOP AT tg_saida INTO eg_saida.
    READ TABLE tg_mat_pop INTO eg_mat_pop WITH KEY matnr = eg_saida-matnr
                                                   werks = eg_saida-werks.
    IF sy-subrc NE 0.
      eg_mat_pop-matnr = eg_saida-matnr.
      eg_mat_pop-werks = eg_saida-werks.
      eg_mat_pop-maktx = eg_saida-maktx.
      APPEND eg_mat_pop TO tg_mat_pop.
      CLEAR eg_mat_pop.
    ENDIF.
  ENDLOOP.

  SORT tg_mat_pop BY matnr werks.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Uses legacy ALV function module instead of modern ALV classes
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Legacy ALV function modules are not aligned with Clean Core principles and modern S/4HANA development practices
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   * Consider using CL_SALV_TABLE or CL_GUI_ALV_GRID classes
  "   * DATA(lo_alv) = NEW cl_salv_table( ).
  "   * lo_alv->get_functions( )->set_all( ).
  "--------------------------------------------------------------------------------------------------
  CALL FUNCTION 'REUSE_ALV_POPUP_TO_SELECT'
    EXPORTING
      i_title               = 'Selecionar Materiais'
      i_selection           = 'X'
      i_zebra               = abap_true
      i_checkbox_fieldname  = 'CHECK'
      i_screen_start_column = 20
      i_tabname             = 'TG_MAT_POP'
      it_fieldcat           = tl_fieldcat[]
    TABLES
      t_outtab              = tg_mat_pop
    EXCEPTIONS
      program_error         = 1
      OTHERS                = 2.
  IF sy-subrc EQ 0.
    DELETE tg_mat_pop WHERE check IS INITIAL.
  ENDIF.
ENDFORM.                    " F_SELECIONA_MATERIAL_CENTRO
*&---------------------------------------------------------------------*
*&      Form  F_EXIBE_IMPOSTOS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_exibe_impostos.

  "--------------------------------------------------------------------------------------------------
  " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
  " Reason     : Header lines are obsolete and should be replaced with explicit work areas
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Antes      : DATA: tl_fieldcat TYPE slis_t_fieldcat_alv WITH HEADER LINE.
  "--------------------------------------------------------------------------------------------------
  DATA: tl_fieldcat TYPE slis_t_fieldcat_alv,
        wa_fieldcat TYPE slis_fieldcat_alv.
  "--------------------------------------------------------------------------------------------------
  " END OF MODIFICATION - Capgemini SAP AI Remediation
  "--------------------------------------------------------------------------------------------------
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : REFRESH statement is obsolete and should be replaced with CLEAR
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Impact     : While still functional, REFRESH is deprecated in favor of CLEAR for better code maintainability
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "     CLEAR tl_fieldcat.
  "--------------------------------------------------------------------------------------------------
  REFRESH tl_fieldcat.

* Montar fieldcat para popup de acordo com o layout de cada botão

  CASE sy-ucomm.
    WHEN 'BT_COMP'.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'MATNR'.
      tl_fieldcat-seltext_m = TEXT-t23.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'WERKS'.
      tl_fieldcat-seltext_m = TEXT-t21.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.


      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'UF_PRECAD'.
      tl_fieldcat-seltext_m = TEXT-t25.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'STATE_FROM'.
      tl_fieldcat-seltext_m = TEXT-t26.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'MWSKZ'.
      tl_fieldcat-seltext_m = TEXT-t68.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'TEXT1'.
      tl_fieldcat-seltext_m = TEXT-t69.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_IPI_COMP'.
      tl_fieldcat-seltext_m = TEXT-t41.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_IPI_COMP'.
      tl_fieldcat-seltext_m = TEXT-t39.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_IPI_COMP'.
      tl_fieldcat-seltext_m = TEXT-t40.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_PIS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t47.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_PIS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t45.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_PIS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t46.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_COFINS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t44.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_COFINS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t42.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_COFINS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t43.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_ICMS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t30.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ICMS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t27.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_ICMS_COMP'.
      tl_fieldcat-seltext_m = TEXT-t28.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ICMS_ST_COMP'.
      tl_fieldcat-seltext_m = TEXT-t31.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'CALC_BASE_ST_COMP'.
      tl_fieldcat-seltext_m = TEXT-t37.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ST_INT_COMP'.
      tl_fieldcat-seltext_m = TEXT-t33.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'CALC_ICMS_ST_COMP'.
      tl_fieldcat-seltext_m = TEXT-t38.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'CALC_PIS_ST_COMP'.
      tl_fieldcat-seltext_m = TEXT-t70.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'CALC_COFINS_ST_COMP'.
      tl_fieldcat-seltext_m = TEXT-t71.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

    WHEN 'BT_TRANSF'.
      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'MATNR'.
      tl_fieldcat-seltext_m = TEXT-t23.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'WERKS'.
      tl_fieldcat-seltext_m = TEXT-t21.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'PTEXT'.
      tl_fieldcat-seltext_m = TEXT-t24.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'STATE_FROM'.
      tl_fieldcat-seltext_m = TEXT-t25.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'STATE_TO'.
      tl_fieldcat-seltext_m = TEXT-t26.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ICMS'.
      tl_fieldcat-seltext_m = TEXT-t27.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_ICMS'.
      tl_fieldcat-seltext_m = TEXT-t28.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'CUST_ICMS'.
      tl_fieldcat-seltext_m = TEXT-t29.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_ICMS'.
      tl_fieldcat-seltext_m = TEXT-t30.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ICMS_ST'.
      tl_fieldcat-seltext_m = TEXT-t31.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ICMS_ST_INT'.
      tl_fieldcat-seltext_m = TEXT-t33.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_ICMS_ST_INT'.
      tl_fieldcat-seltext_m = TEXT-t34.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_RED_1'.
      tl_fieldcat-seltext_m = TEXT-t35.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_RED_2'.
      tl_fieldcat-seltext_m = TEXT-t36.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_BASE_ST'.
      tl_fieldcat-seltext_m = TEXT-t37.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_ICMS_ST'.
      tl_fieldcat-seltext_m = TEXT-t38.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_IPI'.
      tl_fieldcat-seltext_m = TEXT-t39.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_IPI'.
      tl_fieldcat-seltext_m = TEXT-t40.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_IPI'.
      tl_fieldcat-seltext_m = TEXT-t41.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_RAPPEL'.
      tl_fieldcat-seltext_m = TEXT-t48.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAL_CUSTO_LOG'.
      tl_fieldcat-seltext_m = TEXT-t49.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'VAR_CUST_LOG'.
      tl_fieldcat-seltext_m = TEXT-t95.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.
    WHEN 'BT_VENDA'.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'MATNR'.
      tl_fieldcat-seltext_m = TEXT-t23.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'WERKS'.
      tl_fieldcat-seltext_m = TEXT-t21.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'PTEXT'.
      tl_fieldcat-seltext_m = TEXT-t24.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_ICMS_VENDA'.
      tl_fieldcat-seltext_m = TEXT-t27.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_ICMS_VENDA'.
      tl_fieldcat-seltext_m = TEXT-t28.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_PIS'.
      tl_fieldcat-seltext_m = TEXT-t45.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_PIS'.
      tl_fieldcat-seltext_m = TEXT-t46.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'RATE_COFINS'.
      tl_fieldcat-seltext_m = TEXT-t42.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'BASE_COFINS'.
      tl_fieldcat-seltext_m = TEXT-t43.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'ZSTP'.
      tl_fieldcat-seltext_m = TEXT-t98.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.

      CLEAR tl_fieldcat.
      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'ZSTV'.
      tl_fieldcat-seltext_m = TEXT-t99.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.

      CLEAR tl_fieldcat.
      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'ZSTD'.
      tl_fieldcat-seltext_m = TEXT-t9a.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.


      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
      tl_fieldcat-fieldname = 'TOTAL_IMP_VENDA'.
      tl_fieldcat-seltext_m = TEXT-t50.
      tl_fieldcat-just = 'C'.
      APPEND tl_fieldcat.
      CLEAR tl_fieldcat.

  ENDCASE.

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Legacy ALV function module usage instead of modern CL_SALV_* classes
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : While functional, this approach is not aligned with Clean Core principles and modern ABAP development
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   DATA: lo_alv TYPE REF TO cl_salv_table.
  "   TRY.
  "       cl_salv_table=>factory(
  "         IMPORTING
  "           r_salv_table = lo_alv
  "         CHANGING
  "           t_table = tg_impostos ).
  "       lo_alv->get_display_settings( )->set_striped_pattern( abap_true ).
  "       lo_alv->display( ).
  "     CATCH cx_salv_msg.
  "   ENDTRY.
  "--------------------------------------------------------------------------------------------------
  CALL FUNCTION 'REUSE_ALV_POPUP_TO_SELECT'
    EXPORTING
      i_title               = 'Detalhamento dos impostos'
      i_selection           = 'X'
      i_zebra               = abap_true
      i_screen_start_column = 15
      i_screen_start_line   = 5
      i_screen_end_column   = 150
      i_screen_end_line     = 20
      i_tabname             = 'TG_IMPOSTOS'
      it_fieldcat           = tl_fieldcat[]
    TABLES
      t_outtab              = tg_impostos
    EXCEPTIONS
      program_error         = 1
      OTHERS                = 2.
ENDFORM.                    " F_EXIBE_IMPOSTOS
*&---------------------------------------------------------------------*
*&      Form  F_EXIBE_C_LOG
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_exibe_c_log tables tl_data type STANDARD TABLE.

  data: tl_konw type TABLE OF konw.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Header line usage is obsolete and discouraged in modern ABAP
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : Header lines reduce code readability and can cause confusion about data access patterns
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   DATA: tl_fieldcat TYPE slis_t_fieldcat_alv,
  "         wa_fieldcat TYPE slis_fieldcat_alv.
  "--------------------------------------------------------------------------------------------------
  DATA: tl_fieldcat TYPE slis_t_fieldcat_alv WITH HEADER LINE.
  tl_konw[] = tl_data[].
* Montar fieldcat para popup
  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'MANDT'.
  tl_fieldcat-no_out = 'X'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using header line with APPEND and CLEAR is obsolete pattern
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is less readable and maintainable than modern work area approach
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND wa_fieldcat TO tl_fieldcat.
  "   CLEAR wa_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KNUMH'.
  tl_fieldcat-seltext_m = TEXT-020.
  tl_fieldcat-no_out = 'X'.
  tl_fieldcat-just = 'C'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using header line with APPEND and CLEAR is obsolete pattern
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is less readable and maintainable than modern work area approach
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND wa_fieldcat TO tl_fieldcat.
  "   CLEAR wa_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KOPOS'.
  tl_fieldcat-seltext_m = TEXT-021.
  tl_fieldcat-no_out = 'X'.
  tl_fieldcat-just = 'C'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using header line with APPEND and CLEAR is obsolete pattern
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is less readable and maintainable than modern work area approach
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND wa_fieldcat TO tl_fieldcat.
  "   CLEAR wa_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KLFN1'.
  tl_fieldcat-no_out = 'X'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using header line with APPEND and CLEAR is obsolete pattern
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is less readable and maintainable than modern work area approach
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND wa_fieldcat TO tl_fieldcat.
  "   CLEAR wa_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KSTBW'.
  tl_fieldcat-seltext_m = TEXT-022.
  tl_fieldcat-just = 'C'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using header line with APPEND and CLEAR is obsolete pattern
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is less readable and maintainable than modern work area approach
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND wa_fieldcat TO tl_fieldcat.
  "   CLEAR wa_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KBETR'.
  tl_fieldcat-ref_fieldname =  'KONW'.
  tl_fieldcat-ref_tabname  = 'KBETR'.
  tl_fieldcat-seltext_m = TEXT-023.
  tl_fieldcat-just = 'C'.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using header line with APPEND and CLEAR is obsolete pattern
  " RAG Source : GENERAL ABAP BEST PRACTICE (not from workspace KB)
  " Impact     : This pattern is less readable and maintainable than modern work area approach
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   APPEND wa_fieldcat TO tl_fieldcat.
  "   CLEAR wa_fieldcat.
  "--------------------------------------------------------------------------------------------------
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Using legacy ALV function module instead of modern CL_SALV_* classes
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Legacy ALV functions are not aligned with Clean Core principles and modern ABAP development
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   * Use CL_SALV_TABLE or CL_SALV_POPUP for modern ALV implementation
  "   * DATA(lo_alv) = cl_salv_table=>factory( r_table = REF #( tl_konw ) ).
  "   * lo_alv->display( ).
  "--------------------------------------------------------------------------------------------------
  CALL FUNCTION 'REUSE_ALV_POPUP_TO_SELECT'
    EXPORTING
      i_title               = 'Valores para cálculo Custo Logístico'
      i_selection           = 'X'
      i_zebra               = abap_true
      i_screen_start_column = 15
      i_screen_start_line   = 5
      i_screen_end_column   = 150
      i_screen_end_line     = 20
      i_tabname             = 'TL_KONW'
      it_fieldcat           = tl_fieldcat[]
    TABLES
      t_outtab              = tl_konw
    EXCEPTIONS
      program_error         = 1
      OTHERS                = 2.


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
*
*
*
*
*      i_title               = 'Valores para cálculo Custo Logístico'
*    EXCEPTIONS

ENDFORM.                    " F_EXIBE_C_LOG
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_RAPPEL
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_seleciona_rappel .
  DATA: vl_kbetr TYPE konp-kbetr.

  IF tg_mara[] IS NOT INITIAL.
    "Buscar rappel
    "--------------------------------------------------------------------------------------------------
    " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
    " Reason     : SELECT...ENDSELECT with UP TO 1 ROWS should be replaced with SELECT SINGLE for better performance and modern ABAP syntax.
    " RAG Source : From Classic ABAP to ABAP.pdf
    " Antes      :
    "   SELECT b~kbetr UP TO 1 ROWS
    "     INTO vl_kbetr
    "     FROM a900 AS a INNER JOIN konp AS b              "#EC CI_BUFFJOIN
    "       ON a~knumh = b~knumh
    "       WHERE a~kappl = 'V'
    "         AND a~kschl = 'ZRAP'
    "         AND a~vkorg = eg_twkao-vkorg
    "         AND a~vtweg = eg_twkao-vtweg
    "         AND a~werks = eg_mara-bwkey
    "         AND a~matnr = eg_mara-matnr
    "         AND a~datbi >= so_vkkab-low
    "         AND a~datab <= so_vkkab-low
    "         AND b~kschl = 'ZRAP'
    "     ORDER BY a~knumh. " <LMB_S4_BM>
    "   ENDSELECT.
    "--------------------------------------------------------------------------------------------------
    SELECT SINGLE b~kbetr
      INTO vl_kbetr
      FROM a900 AS a INNER JOIN konp AS b              "#EC CI_BUFFJOIN
        ON a~knumh = b~knumh
        WHERE a~kappl = 'V'
          AND a~kschl = 'ZRAP'
          AND a~vkorg = eg_twkao-vkorg
          AND a~vtweg = eg_twkao-vtweg
          AND a~werks = eg_mara-bwkey
          AND a~matnr = eg_mara-matnr
          AND a~datbi >= so_vkkab-low
          AND a~datab <= so_vkkab-low
          AND b~kschl = 'ZRAP'
      ORDER BY a~knumh. " <LMB_S4_BM>
    "--------------------------------------------------------------------------------------------------
    " END OF MODIFICATION - Capgemini SAP AI Remediation
    "--------------------------------------------------------------------------------------------------
    IF sy-subrc EQ 0.
      eg_saida-rappel = vl_kbetr / 10.
    ELSE.
      eg_saida-rappel = 0.
    ENDIF.
  ELSE.
    eg_saida-rappel = 0.
  ENDIF.

ENDFORM.                    " F_SELECIONA_RAPPEL
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_DADOS_REL
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_seleciona_dados_rel .
  DATA: tl_simupreca TYPE TABLE OF ztsdd_simupreca,
        rl_docsim    TYPE RANGE OF ztsdd_simupreca-docsim,
        el_docsim    LIKE LINE OF rl_docsim.

*
  FREE: rl_docsim.
  CLEAR : el_docsim.
  IF NOT p_docsim IS INITIAL.
    el_docsim-sign = 'I'.
    el_docsim-option = 'EQ'.
    el_docsim-low = p_docsim.
    APPEND el_docsim TO rl_docsim.
  ENDIF.

  FREE: tg_saida_rel, tg_simupreca, tg_simupreci.

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : SELECT * statement retrieves all fields which may include unnecessary data and impacts performance
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Violates Clean Core principles by potentially accessing fields that may change or be removed in S/4HANA, and reduces performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "     SELECT docsim, pltyp, matnr, werks, status_i, lifnr, pcb, pcl, preco_transf, rappel, custo_log, pv_liq, pv_fin, mg_liq, mg_bruta
  "       INTO TABLE tg_simupreci
  "       FROM ztsdd_simupreci
  "      WHERE docsim IN rl_docsim
  "        AND matnr  IN so_matnr.
  "--------------------------------------------------------------------------------------------------
  SELECT *
    INTO TABLE tg_simupreci
    FROM ztsdd_simupreci
   WHERE docsim IN rl_docsim
     AND matnr  IN so_matnr.
  IF sy-subrc EQ 0.
    DELETE tg_simupreci WHERE status_i <> '30'.
    SORT tg_simupreci BY docsim pltyp matnr werks.
  ENDIF.

  IF tg_simupreci[] IS INITIAL.
    MESSAGE i208(00) WITH 'Nenhum registro aprovado encontrado'
                     DISPLAY LIKE 'E'.
    LEAVE TO LIST-PROCESSING.
    STOP.
  ENDIF.

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : SELECT * statement retrieves all fields which may include unnecessary data and impacts performance
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Violates Clean Core principles by potentially accessing fields that may change or be removed in S/4HANA, and reduces performance
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "     SELECT docsim, pltyp, matnr, werks, pcb_efetivo, pcl_efetivo, condicao_pcb, pt_efetivo, condicao_pt, rappel_efetivo, condicao_rappel, pvl_efetivo, pvf_efetivo, mgl_efetivo, mgb_efetivo, condicao_pvf, msg_autom
  "       INTO TABLE tg_simupreca
  "       FROM ztsdd_simupreca
  "       FOR ALL ENTRIES IN tg_simupreci
  "      WHERE docsim = tg_simupreci-docsim
  "        AND pltyp  = tg_simupreci-pltyp
  "        AND matnr  = tg_simupreci-matnr
  "        AND werks  = tg_simupreci-werks.
  "--------------------------------------------------------------------------------------------------
  SELECT *
    INTO TABLE tg_simupreca
    FROM ztsdd_simupreca
    FOR ALL ENTRIES IN tg_simupreci
   WHERE docsim = tg_simupreci-docsim
     AND pltyp  = tg_simupreci-pltyp
     AND matnr  = tg_simupreci-matnr
     AND werks  = tg_simupreci-werks.
  IF sy-subrc EQ 0.
    SORT tg_simupreca BY docsim pltyp matnr werks.
  ENDIF.
  IF tg_simupreca[] IS INITIAL.
    MESSAGE i208(00) WITH 'Log Processo Automatico não criado.Favor Aguardar.'
                     DISPLAY LIKE 'E'.
    LEAVE TO LIST-PROCESSING.
    STOP.
  ENDIF.


  FREE: tg_twkao.
  tl_simupreca[] = tg_simupreca[].
  SORT tl_simupreca BY pltyp.
  DELETE ADJACENT DUPLICATES FROM tl_simupreca COMPARING pltyp.
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Direct access to SAP standard tables TWKAO and T189T without using released APIs or CDS views
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Violates Clean Core principles as these tables may change structure or access methods in S/4HANA
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   * Check if released CDS views or APIs are available for price list type data
  "   * Use appropriate released interfaces instead of direct table access
  "   * Consider using service consumption or released business objects
  "--------------------------------------------------------------------------------------------------
  SELECT a~vkorg
         a~vtweg
         a~pltyp
         a~vlgwk
         b~ptext
    INTO TABLE tg_twkao
    FROM twkao AS a INNER JOIN t189t AS b              "#EC CI_BUFFJOIN
       ON a~pltyp EQ b~pltyp
    FOR ALL ENTRIES IN tl_simupreca
    WHERE a~vkorg EQ 'LB01'
      AND a~vtweg EQ '10'
      AND a~pltyp = tl_simupreca-pltyp
      AND a~vlgwk NE space
      AND b~spras EQ sy-langu.
  IF sy-subrc EQ 0.
    SORT tg_twkao BY pltyp.
  ENDIF.

  FREE: tg_mara.
  tl_simupreca[] = tg_simupreca[].
  SORT tl_simupreca BY matnr.
  DELETE ADJACENT DUPLICATES FROM tl_simupreca COMPARING matnr.

  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Direct access to SAP standard tables MARA, MAKT, MBEW, MARC without using released APIs or CDS views
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Violates Clean Core principles as these material master tables may have different access patterns or structure in S/4HANA
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   * Use released CDS views like I_Product, I_ProductText, I_ProductValuation, I_ProductPlant
  "   * Replace with appropriate service consumption or released business objects
  "   * Consider using RAP-based APIs for material master data access
  "--------------------------------------------------------------------------------------------------
  "Buscar dados dos materiais
  SELECT a~matnr
         a~mtart
         a~matkl
         a~meins
         a~bstat
         b~maktx
         c~bwkey
         c~mtuse
         c~mtorg
         d~werks
         d~steuc
    INTO TABLE tg_mara
    FROM mara AS a INNER JOIN makt AS b
    ON a~matnr EQ b~matnr
        INNER JOIN mbew AS c
    ON a~matnr EQ c~matnr
        INNER JOIN marc AS d
    ON a~matnr EQ d~matnr
    FOR ALL ENTRIES IN tl_simupreca
    WHERE a~matnr = tl_simupreca-matnr
      AND a~lvorm EQ space.
  IF sy-subrc EQ 0.
    SORT tg_mara BY matnr.
  ENDIF.

  LOOP AT tg_simupreca INTO eg_simupreca.
    CLEAR: eg_simupreci, eg_twkao, eg_mara, eg_saida_rel.
    READ TABLE tg_simupreci INTO eg_simupreci WITH KEY docsim = eg_simupreca-docsim
                                                       pltyp  = eg_simupreca-pltyp
                                                       matnr  = eg_simupreca-matnr
                                                       werks  = eg_simupreca-werks
                                              BINARY SEARCH.
    READ TABLE tg_twkao INTO eg_twkao WITH KEY pltyp = eg_simupreca-pltyp
                                      BINARY SEARCH.
    READ TABLE tg_mara INTO eg_mara WITH KEY matnr = eg_simupreca-matnr
                                    BINARY SEARCH.

    eg_saida_rel-docsim          = eg_simupreca-docsim.
    eg_saida_rel-matnr           = eg_simupreca-matnr.
    eg_saida_rel-maktx           = eg_mara-maktx.
    eg_saida_rel-pltyp           = eg_simupreca-pltyp.
    eg_saida_rel-ptext           = eg_twkao-ptext.
    eg_saida_rel-werks           = eg_simupreca-werks.
    eg_saida_rel-lifnr           = eg_simupreci-lifnr.
    eg_saida_rel-pcb             = eg_simupreci-pcb.
    eg_saida_rel-pcb_efetivo     = eg_simupreca-pcb_efetivo.
    eg_saida_rel-pcl             = eg_simupreci-pcl.
    eg_saida_rel-pcl_efetivo     = eg_simupreca-pcl_efetivo.
    eg_saida_rel-condicao_pcb    = eg_simupreca-condicao_pcb.
    eg_saida_rel-preco_transf    = eg_simupreci-preco_transf.
    eg_saida_rel-pt_efetivo      = eg_simupreca-pt_efetivo.
    eg_saida_rel-condicao_pt     = eg_simupreca-condicao_pt.
    eg_saida_rel-rappel          = eg_simupreci-rappel.
    eg_saida_rel-rappel_efetivo  = eg_simupreca-rappel_efetivo.
    eg_saida_rel-condicao_rappel = eg_simupreca-condicao_rappel.
    eg_saida_rel-custo_log       = eg_simupreci-custo_log.
    eg_saida_rel-pv_liq          = eg_simupreci-pv_liq.
    eg_saida_rel-pvl_efetivo     = eg_simupreca-pvl_efetivo.
    eg_saida_rel-pv_fin          = eg_simupreci-pv_fin.
    eg_saida_rel-pvf_efetivo     = eg_simupreca-pvf_efetivo.
    eg_saida_rel-mg_liq          = eg_simupreci-mg_liq.
    eg_saida_rel-mgl_efetivo     = eg_simupreca-mgl_efetivo.
    eg_saida_rel-mg_bruta        = eg_simupreci-mg_bruta.
    eg_saida_rel-mgb_efetivo     = eg_simupreca-mgb_efetivo.
    eg_saida_rel-condicao_pvf    = eg_simupreca-condicao_pvf.
    eg_saida_rel-msg_autom       = eg_simupreca-msg_autom.

    APPEND eg_saida_rel TO tg_saida_rel.
  ENDLOOP.

ENDFORM.                    " F_SELECIONA_DADOS_REL
*&---------------------------------------------------------------------*
*&      Form  FILL_CELLTAB
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM fill_celltab CHANGING pt_celltab TYPE lvc_t_styl.
  DATA: ls_celltab TYPE lvc_s_styl,
        l_mode     TYPE raw4.
  FREE: pt_celltab.
  l_mode = cl_gui_alv_grid=>mc_style_enabled.
  ls_celltab-fieldname = 'PV_FIN'.
  ls_celltab-style = l_mode.
  INSERT ls_celltab INTO TABLE pt_celltab.

ENDFORM.                               " FILL_CELLTAB
*&---------------------------------------------------------------------*
*&      Form  F_BUSCA_CDUNICO
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
*
*
** Logica inicial para seleção de 1 unico Centro na tela de seleção (A ser definido ainda).
*
*
*
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_DADOS_NEW
*&---------------------------------------------------------------------*
FORM f_seleciona_dados_new .
  DATA: tl_return  TYPE tab_bapiret1,
        el_return  TYPE bapiret1,
        p_so_matnr TYPE rseloption,
        p_so_ebeln TYPE rseloption,
        p_so_mati  TYPE rseloption,
        p_so_werks TYPE rseloption,
        p_so_pltyp TYPE rseloption,
        p_so_vkkab TYPE rseloption.

  "--------------------------------------------------------------------------------------------------
  " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
  " Reason     : Replace obsolete header line syntax with modern ABAP syntax for internal table assignments.
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Antes      :
  "   p_so_matnr[] = so_matnr[].
  "   p_so_ebeln[] = so_ebeln[].
  "   p_so_mati[]  = so_mati[].
  "   p_so_werks[] = so_werks[].
  "   p_so_pltyp[] = so_pltyp[].
  "   p_so_vkkab[] = so_vkkab[].
  "--------------------------------------------------------------------------------------------------
  p_so_matnr = so_matnr.
  p_so_ebeln = so_ebeln.
  p_so_mati  = so_mati.
  p_so_werks = so_werks.
  p_so_pltyp = so_pltyp.
  p_so_vkkab = so_vkkab.
  "--------------------------------------------------------------------------------------------------
  " END OF MODIFICATION - Capgemini SAP AI Remediation
  "--------------------------------------------------------------------------------------------------

  "--------------------------------------------------------------------------------------------------
  " MANUAL REVIEW REQUIRED - Capgemini SAP AI Remediation
  " Reason     : Custom function module call needs verification for S/4HANA compatibility and potential replacement with released APIs.
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  "--------------------------------------------------------------------------------------------------
  CALL FUNCTION 'ZFSD_MONITOR_IMPORT_SELECAO'
    EXPORTING
      e_so_matnr = p_so_matnr[]
      e_so_ebeln = p_so_ebeln[]
      e_so_mati  = p_so_mati[]
      e_so_werks = p_so_werks[]
      e_so_pltyp = p_so_pltyp[]
      e_so_vkkab = p_so_vkkab[]
      e_rb_ped   = rb_ped
      e_rb_mat   = rb_mat
      e_rb_mpc   = rb_mpc
      e_rb_sim   = rb_sim
      e_rb_aut   = rb_aut
      e_rb_cad   = rb_cad
      e_rb_upo   = rb_upo
      e_p_docsim = p_docsim
      e_p_cagrp  = p_cagrp
      e_p_vkorg  = p_vkorg
      e_p_vtweg  = p_vtweg
    IMPORTING
      s_t_return = tl_return.

  IF rb_sim EQ space.
    CLEAR p_docsim.
  ENDIF.

  IF NOT tl_return[] IS INITIAL.
    "--------------------------------------------------------------------------------------------------
    " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
    " Issue      : Using obsolete LOOP AT ... INTO pattern instead of modern field symbol or reference variable approach.
    " RAG Source : From Classic ABAP to ABAP.pdf
    " Impact     : While functional, this pattern is less efficient and not aligned with modern ABAP development practices in S/4HANA.
    "--------------------------------------------------------------------------------------------------
    " Recommended code (suggestion — not applied):
    "       LOOP AT tl_return ASSIGNING FIELD-SYMBOL(<ls_return>).
    "         MESSAGE ID  <ls_return>-id
    "           TYPE   'S'
    "           NUMBER <ls_return>-number
    "           WITH   <ls_return>-message_v1
    "                  <ls_return>-message_v2
    "                  <ls_return>-message_v3
    "                  <ls_return>-message_v4
    "          DISPLAY LIKE 'E'.
    "         EXIT.
    "       ENDLOOP.
    "--------------------------------------------------------------------------------------------------
    LOOP AT tl_return INTO el_return.
      MESSAGE ID  el_return-id
        TYPE   'S'
        NUMBER el_return-number
        WITH   el_return-message_v1
               el_return-message_v2
               el_return-message_v3
               el_return-message_v4
       DISPLAY LIKE 'E'.
      EXIT.
    ENDLOOP.
    IF el_return-number = '096'.
      vg_edit = abap_false.
    ELSE.
      vg_erro = abap_true.
    ENDIF.
  ENDIF.
ENDFORM.
*&---------------------------------------------------------------------*
*&      Form  F_PROCESSA_DADOS_NEW
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*----------------------------------------------------------------------*
FORM f_processa_dados_new .

  CALL FUNCTION 'ZFSD_MONITOR_IMPORT_DADOS'
    IMPORTING
      s_t_impostos = tg_impostos
      s_t_dados    = tg_dados
      s_t_saida    = tg_saida
      s_gp         = vg_gp
      s_gp_name    = vg_gpname
      s_edit       = vg_edit
      s_dgp        = vg_dgp.


ENDFORM.
*&---------------------------------------------------------------------*
*&      Form  F_VERIFICA_MULTIPLA_LISTA
*&---------------------------------------------------------------------*
FORM f_verifica_multipla_lista  TABLES   pt_saida TYPE STANDARD TABLE
                                USING    pv_matnr TYPE mara-matnr
                                         pv_pltyp TYPE a155-pltyp
                                         pv_pvfin TYPE endpr
                                CHANGING p_pvfin_lista.

  DATA: tl_saida TYPE TABLE OF zssd_mon_imp_saida.

  tl_saida[] = pt_saida[].

  READ TABLE tg_listas INTO DATA(el_lista) WITH KEY pltyp_p = pv_pltyp BINARY SEARCH.
  IF sy-subrc EQ 0. " Achou Lista Multipla. Pegar lista principal para calculo IPI.
    READ TABLE tl_saida INTO DATA(el_saida) WITH KEY matnr = pv_matnr
                                                     pltyp = el_lista-pltyp.
    IF sy-subrc EQ 0.
      p_pvfin_lista = el_saida-pv_fin. " Usa este valor como referencia para calculo IPI.
    ELSE.
      PERFORM f_seleciona_pvfinal_lista USING pv_matnr
                                              el_lista-pltyp
                                        CHANGING p_pvfin_lista.

    ENDIF.
  ELSE. "Nao achou, lista normal sem multipla lista para mesmo refsite.
    p_pvfin_lista = pv_pvfin.
  ENDIF.


ENDFORM.
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_LISTAS
*&---------------------------------------------------------------------*
FORM f_seleciona_listas .

  SELECT *   "#EC CI_NOFIRST
    INTO TABLE tg_listas
    FROM ztsdd_listas_p
   WHERE pltyp_p IN so_pltyp.

  IF sy-subrc EQ 0.
    SORT tg_listas BY pltyp_p.
  ENDIF.

ENDFORM.
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_PVFINAL_LISTA
*&---------------------------------------------------------------------*
FORM f_seleciona_pvfinal_lista  USING    pv_matnr TYPE matnr
                                         pv_pltyp TYPE pltyp
                                CHANGING p_pvfin_lista TYPE endpr.

  DATA: vl_kbetr TYPE konp-kbetr.
  CONSTANTS: c_valor TYPE p DECIMALS 2 VALUE '0.01'.

  "Buscar preço de venda final
  "--------------------------------------------------------------------------------------------------
  " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
  " Reason     : SELECT...ENDSELECT with UP TO 1 ROWS should be replaced with SELECT SINGLE for better performance and modern ABAP syntax.
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Antes      :
  "   SELECT b~kbetr UP TO 1 ROWS  "#EC CI_SEL_NESTED
  "     INTO vl_kbetr
  "     FROM a155 AS a INNER JOIN konp AS b
  "       ON ( a~knumh = b~knumh
  "           AND a~kschl = b~kschl )
  "       WHERE a~kappl = 'V'
  "         AND a~kschl = 'VKP0'
  "         AND a~pltyp = pv_pltyp
  "         AND a~matnr = pv_matnr
  "         AND a~datbi >= so_vkkab-low
  "         AND a~datab <= so_vkkab-low
  "     ORDER BY a~knumh.  " <LMB_S4_BM>
  "   ENDSELECT.
  "--------------------------------------------------------------------------------------------------
  "--------------------------------------------------------------------------------------------------
  " WARNING - ABAP BEST PRACTICE NON-COMPLIANCE (SAP S/4HANA 2025 (Private Edition))
  " Issue      : Direct access to SAP standard tables A155 and KONP may violate Clean Core principles
  " RAG Source : Clean core extensibility for SAP S_4HANA Cloud.pdf
  " Impact     : Direct table access may break in future S/4HANA releases if table structures change or are replaced by CDS views
  "--------------------------------------------------------------------------------------------------
  " Recommended code (suggestion — not applied):
  "   * Consider using released pricing APIs or CDS views if available
  "   * Check for pricing-related BAPIs or function modules
  "   * Evaluate if CDS view I_PricingConditionRecord or similar released objects can replace direct table access
  "--------------------------------------------------------------------------------------------------
  SELECT SINGLE b~kbetr
    INTO vl_kbetr
    FROM a155 AS a INNER JOIN konp AS b
      ON ( a~knumh = b~knumh
          AND a~kschl = b~kschl )
      WHERE a~kappl = 'V'
        AND a~kschl = 'VKP0'
        AND a~pltyp = pv_pltyp
        AND a~matnr = pv_matnr
        AND a~datbi >= so_vkkab-low
        AND a~datab <= so_vkkab-low
    ORDER BY a~knumh.
  "--------------------------------------------------------------------------------------------------
  " END OF MODIFICATION - Capgemini SAP AI Remediation
  "--------------------------------------------------------------------------------------------------
  "--------------------------------------------------------------------------------------------------
  " BEGIN OF MODIFICATION - Capgemini SAP AI Remediation
  " Reason     : Replace obsolete EQ operator with modern = operator for better readability and consistency.
  " RAG Source : From Classic ABAP to ABAP.pdf
  " Antes      : IF sy-subrc EQ 0.
  "--------------------------------------------------------------------------------------------------
  IF sy-subrc = 0.
  "--------------------------------------------------------------------------------------------------
  " END OF MODIFICATION - Capgemini SAP AI Remediation
  "--------------------------------------------------------------------------------------------------
    CALL FUNCTION 'PRICE_POINT_READ'
      EXPORTING
        pi_vkorg                   = 'LB01'
        pi_vtweg                   = '10'
        pi_rktyp                   = 'A'
        pi_eprgr                   = 'ZLMB07'
        pi_price                   = vl_kbetr
        pi_waers                   = 'BRL'
        pi_datam                   = sy-datum
        pi_kurst                   = 'M'
        pi_hwaer                   = 'BRL'
        pi_mfact                   = '1'
      IMPORTING
        pe_price                   = vl_kbetr
      EXCEPTIONS
        no_price_point_group_found = 1
        no_price_points_maintained = 2
        conversion_not_found       = 3
        OTHERS                     = 4.

    p_pvfin_lista = vl_kbetr.
  ELSE.
    p_pvfin_lista = c_valor.
  ENDIF.




ENDFORM.
*&---------------------------------------------------------------------*
*&      Form  F_VALIDA_CENTRO
*&---------------------------------------------------------------------*
FORM f_valida_centro .

 select single vlfkz
   into @data(vl_vlfkz)
   from t001w
  where werks = @so_werks-low.
 if sy-subrc ne 0.
   clear vl_vlfkz.
 endif.

 if vl_vlfkz ne 'B'.
   message e208(00) with 'Centro não é Plataforma ou CD'.
 endif.


ENDFORM.