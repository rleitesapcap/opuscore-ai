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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_descreve_campos_grid .
  DATA: vl_linha TYPE i.
  REFRESH tg_fieldcat.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  IF rb_aut = abap_false.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
    "Layout do relatório
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
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio

*Inicio - L.Chagas - CC.8040 - 31.01.2022
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
*Fim - L.Chagas - CC.8040 - 31.01.2022
  ELSE.
    "Layout do relatório
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
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_layout_grid .

  CLEAR: vg_layout.
  vg_layout-zebra       = abap_true.
  vg_layout-cwidth_opt  = abap_true.
*  vg_layout-sel_mode    = c_a.
* Field that identify cell color in internal table
  MOVE 'COLOR_CELL' TO vg_layout-ctab_fname.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
  MOVE 'CELLTAB' TO vg_layout-stylefname.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM.
ENDFORM.                    " F_LAYOUT_GRID
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_DADOS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_seleciona_dados .
*  TYPES: BEGIN OF ty_eine,
*           infnr TYPE eina-infnr,
*           matnr TYPE eina-matnr,
*           werks TYPE eine-werks,
*         END OF ty_eine.
*  DATA: tl_mara TYPE TABLE OF ty_mara,
*        tl_eine TYPE TABLE OF ty_eine.
*
*  "Buscar parâmetros fixos
*  get_hard 'SD_0402_01_TIPO_MAT_REF_IMP' 'MTART' gr_mtart.
*  get_hard 'SD_0402_01_TIPO_PED_IMP' 'BSART' gr_bsart.
*  get_hard 'SD_0402_01_ORIGEM_MAT_IMP' 'J_1BMATORG' gr_mtorg.
*  get_hard 'SD_0402_01_STATUS_MAT' 'BSTAT' gr_bstat.
*
*  vg_edit = abap_true.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*  PERFORM f_busca_cdunico.
** Alteração - CD.3723 - 24.01.2020 - FIM.
*  IF rb_sim NE space.
*    "Seleção por simulação
*    PERFORM f_selecao_simulacao.
*  ELSE.
*
*    CLEAR: vg_erro, p_docsim.
*
** Validar informações
*    PERFORM f_valida_campos.
*
*    CHECK vg_erro IS INITIAL.
*
** Selecionar lista de preços
*    SELECT a~vkorg
*           a~vtweg
*           a~pltyp
*           a~vlgwk
*           b~ptext
*      INTO TABLE tg_twkao
*      FROM twkao AS a INNER JOIN t189t AS b            "#EC CI_BUFFJOIN
*         ON a~pltyp EQ b~pltyp
*      WHERE a~vkorg EQ p_vkorg
*        AND a~vtweg EQ p_vtweg
*        AND a~pltyp IN so_pltyp
*        AND a~vlgwk NE space
*        AND b~spras EQ sy-langu.
*
*    IF sy-subrc EQ 0.
*      SORT tg_twkao.
*    ENDIF.
*    IF tg_twkao[] IS NOT INITIAL.
*
** Seleciona dados dos centros
*      SELECT werks regio
*        INTO TABLE tg_t001w
*        FROM t001w
*        FOR ALL ENTRIES IN tg_twkao
*        WHERE werks EQ tg_twkao-vlgwk
*          OR werks IN so_werks.
*      IF sy-subrc EQ 0.
*        SORT tg_t001w.
*      ENDIF.
** Selecionar materiais para simulação
*      IF rb_ped NE space.
*        "Seleção por pedido
*        PERFORM f_selecao_pedido.
*
*      ELSEIF rb_mat NE space.
*        "Seleção por material
*        PERFORM f_selecao_material.
*
*      ELSEIF rb_mpc NE space.
*        "Seleção por material pré-cadastrado
*        PERFORM f_selecao_mat_pre_cad.
*      ENDIF.
*    ELSE.
*      "Não há lista de preços para essa seleção
*      MESSAGE s075(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ENDIF.
*
*  ENDIF.
*
** Alteração - CD.3723 - 24.01.2020 - Inicio
*  IF NOT tg_mara[] IS INITIAL.
*    IF NOT vg_cd_unico IS INITIAL.
*      tl_mara[] = tg_mara[].
*      SORT tl_mara BY matnr.
*      DELETE ADJACENT DUPLICATES FROM tl_mara COMPARING matnr.
*      IF NOT tl_mara[] IS INITIAL.
*        SELECT a~infnr a~matnr e~werks
*          INTO TABLE tl_eine
*          FROM eina AS a INNER JOIN eine AS e ON a~infnr = e~infnr
*          FOR ALL ENTRIES IN tl_mara
*         WHERE a~matnr = tl_mara-matnr
*           AND a~loekz = ' '
*           AND e~ekorg = 'LB01'
*           AND e~werks = vg_cd_unico.
*      ENDIF.
*      SORT tl_eine BY matnr.
*      LOOP AT tg_mara INTO eg_mara.
*        READ TABLE tl_eine WITH KEY matnr = eg_mara-matnr TRANSPORTING NO FIELDS.
*        IF sy-subrc NE 0.
*          DELETE tg_mara WHERE matnr = eg_mara-matnr.
*        ENDIF.
*      ENDLOOP.
*      IF tg_mara[] IS INITIAL.
*        MESSAGE w208(00) WITH 'Sem Reg Info para o CD'.
*        vg_erro = abap_true.
*      ENDIF.
*    ENDIF.
*  ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
** Alteração - CC.3526 - 18.09.2019 10:27:12 - Inicio
**** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
***  IF NOT tg_mara[] IS INITIAL.
***    tl_mara[] = tg_mara[].
***    SORT tl_mara BY matnr.
***    DELETE ADJACENT DUPLICATES FROM tl_mara COMPARING matnr.
***    SELECT matnr node
***     FROM wrf_matgrp_sku
***     INTO TABLE tg_node
***     FOR ALL ENTRIES IN tl_mara
***      WHERE hier_id = 'L1'
***        AND matnr   = tl_mara-matnr
***        AND date_from <= sy-datum
***        AND date_to >= sy-datum.
***
***    SELECT *
***      INTO TABLE tg_revionics
***      FROM ztsdc0001
***     WHERE datab <= sy-datum.
***
***     sort tg_node by matnr.
***     sort tg_revionics by secao.
***  ENDIF.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM
** Alteração - CC.3526 - 18.09.2019 10:27:12 - FIM
*ENDFORM.                    " F_SELECIONA_DADOS
*&---------------------------------------------------------------------*
*&      Form  F_PROCESSA_DADOS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_processa_dados .
*  DATA: "vl_infnr      TYPE infnr,
**        vl_ekorg      TYPE ekorg,
**        vl_esokz      TYPE esokz,
**        vl_werks_inf  TYPE zwerks_inf,
**        vl_lifnr      TYPE elifn,
**        vl_netpr      TYPE eine-netpr,
**        vl_peinh      TYPE eine-peinh,
*    vl_regio_from TYPE regio,
*    vl_regio_to   TYPE regio.
*
*  DATA vl_new_pcb2 TYPE dmbtr.                              "FB23112018
*  DATA vl_new_pcb3 TYPE ekpnn.                              "FB23112018
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*  DATA: tl_celltab TYPE lvc_t_styl.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*  DATA: vl_werks TYPE werks_d.
** Alteração - CD.3723 - 24.01.2020 - FIM
*  "Montar tabela de saída (tg_saida) para cada processamento
*
*  IF rb_sim NE space.    "Dados da simulação já gravada
*
*    LOOP AT tg_simuprech INTO eg_simuprech. "Dados de cabeçalho
*
*      "Valores da simulação
*      LOOP AT tg_simupreci INTO eg_simupreci WHERE docsim = eg_simuprech-docsim. "#EC CI_NESTED
*        CLEAR eg_saida.
*        eg_saida-matnr        = eg_simupreci-matnr.        "Material
*        eg_saida-uf_precad    = eg_simupreci-uf_precad.    "UF Material pré-cadastro
*
*        "Descrição Material
*        IF eg_simuprech-selecao EQ 1 OR  " Processado por pedido
*           eg_simuprech-selecao EQ 2.    " Processado por material
*          READ TABLE tg_mara INTO eg_mara WITH KEY matnr = eg_simupreci-matnr
*                                                   bwkey = eg_simupreci-werks.
*          eg_saida-maktx      = eg_mara-maktx.
*          eg_saida-mtuse      = eg_mara-mtuse.
*          eg_saida-mtorg      = eg_mara-mtorg.
*          eg_saida-steuc      = eg_mara-steuc.
*          eg_saida-matkl      = eg_mara-matkl.
*          eg_saida-matprecadx = space.
*          eg_saida-matnr_ref  = space.
*
*        ELSEIF eg_simuprech-selecao EQ 3.  " Processado por material pré-cadastrado
*          READ TABLE tg_precadmat INTO eg_precadmat WITH KEY matnr = eg_simupreci-matnr.
*          eg_saida-maktx      = eg_precadmat-maktx.
*
*          READ TABLE tg_mara INTO eg_mara WITH KEY matnr = eg_precadmat-mat_imp
*                                                   bwkey = eg_simupreci-werks.
*          eg_saida-mtuse      = eg_mara-mtuse.
*          eg_saida-mtorg      = eg_mara-mtorg.
*          eg_saida-steuc      = eg_mara-steuc.
*          eg_saida-matkl      = eg_mara-matkl.
*          eg_saida-matprecadx = abap_true.
*          eg_saida-matnr_ref  = eg_precadmat-mat_imp.
*          eg_saida-cod_agrup  = eg_precadmat-cod_agrup.
*          eg_saida-desc_agrup = eg_precadmat-desc_agrup.
*        ENDIF.
*
*        eg_saida-pltyp        = eg_simupreci-pltyp.        "Lista Preço
*
*        "Descrição lista de preço
*        READ TABLE tg_twkao INTO eg_twkao WITH KEY pltyp  = eg_simupreci-pltyp.
*        eg_saida-ptext        = eg_twkao-ptext.
*
*        eg_saida-qtde_min     = eg_simupreci-qtde_min.     "Quantidade Mínima
*        eg_saida-vrkme        = eg_simupreci-vrkme.        "Unidade de Medida
*        eg_saida-pcb          = eg_simupreci-pcb.          "PCB
** Alteração - CD.3723 - 24.01.2020 - Inicio
*        IF vg_cd_unico IS INITIAL.
** Alteração - CD.3723 - 24.01.2020 - FIM
*          eg_saida-werks        = eg_simupreci-werks.        "Centro
** Alteração - CD.3723 - 24.01.2020 - Inicio
*        ELSE.
*          eg_saida-werks      = vg_cd_unico.
*          eg_saida-werks_ori  = eg_simupreci-werks.
*        ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
*        eg_saida-lifnr        = eg_simupreci-lifnr.        "Fornecedor
*        eg_saida-pcl          = eg_simupreci-pcl.          "PCL
*        eg_saida-preco_transf = eg_simupreci-preco_transf. "Preço Transferência
*        eg_saida-rappel       = eg_simupreci-rappel.       "Rappel %
*        eg_saida-custo_log    = eg_simupreci-custo_log.    "Custo Logistico %
*        eg_saida-pv_liq       = eg_simupreci-pv_liq.       "PV Liquido
*        eg_saida-pv_fin       = eg_simupreci-pv_fin.       "PV Final
*        eg_saida-mg_liq       = eg_simupreci-mg_liq.       "Margem Líquida %
*        eg_saida-mg_bruta     = eg_simupreci-mg_bruta.     "Margem Bruta %
*        eg_saida-status_i     = eg_simupreci-status_i.     "Status aprovação
***        eg_saida-ebeln        = eg_simupreci-ebeln.        "Último Pedido     <002> - Inclusão - Descomentar quando simulador nacional estiver em PRD
*
*        eg_saida-pclst               = eg_simupreci-pclst.
*        eg_saida-custo_log           = eg_simupreci-lco.
*        eg_saida-rate_icms           = eg_simupreci-rate_icms.
*        eg_saida-base_icms           = eg_simupreci-base_icms.
*        eg_saida-cust_icms           = eg_simupreci-cust_icms.
*        eg_saida-val_icms            = eg_simupreci-val_icms.
*        eg_saida-rate_icms_st        = eg_simupreci-rate_icms_st.
*        eg_saida-base_icms_st        = eg_simupreci-base_icms_st.
*        eg_saida-rate_icms_st_int    = eg_simupreci-rate_icms_st_int.
*        eg_saida-base_icms_st_int    = eg_simupreci-base_icms_st_int.
*        eg_saida-base_red_1          = eg_simupreci-base_red_1.
*        eg_saida-base_red_2          = eg_simupreci-base_red_2.
*        eg_saida-val_base_st         = eg_simupreci-val_base_st.
*        eg_saida-val_icms_st         = eg_simupreci-val_icms_st.
*        eg_saida-rate_ipi            = eg_simupreci-rate_ipi.
*        eg_saida-base_ipi            = eg_simupreci-base_ipi.
*        eg_saida-val_ipi             = eg_simupreci-val_ipi.
*        eg_saida-rate_cofins         = eg_simupreci-rate_cofins.
*        eg_saida-base_cofins         = eg_simupreci-base_cofins.
*        eg_saida-val_cofins          = eg_simupreci-val_cofins.
*        eg_saida-rate_pis            = eg_simupreci-rate_pis.
*        eg_saida-base_pis            = eg_simupreci-base_pis.
*        eg_saida-val_pis             = eg_simupreci-val_pis.
*        eg_saida-val_rappel          = eg_simupreci-val_rappel.
*        eg_saida-val_custo_log       = eg_simupreci-val_custo_log.
*        eg_saida-total_imp_venda     = eg_simupreci-total_imp_venda.
*        eg_saida-c_mvto              = eg_simupreci-c_mvto.
*        eg_saida-c_pallet            = eg_simupreci-c_pallet.
*        eg_saida-frete               = eg_simupreci-frete.
*        eg_saida-tx_fin              = eg_simupreci-tx_fin.
*        eg_saida-tx_gest             = eg_simupreci-tx_gest.
*        eg_saida-c_arm               = eg_simupreci-c_arm.
*        eg_saida-umrez               = eg_simupreci-umrez.
*        eg_saida-hoehe               = eg_simupreci-hoehe.
*        eg_saida-breit               = eg_simupreci-breit.
*        eg_saida-laeng               = eg_simupreci-laeng.
*        eg_saida-tx_mov              = eg_simupreci-tx_mov.
*        eg_saida-tx_frete            = eg_simupreci-tx_frete.
*        eg_saida-custo_ins_pallet    = eg_simupreci-custo_ins_pallet.
*        eg_saida-dias_est            = eg_simupreci-dias_est.
*        eg_saida-custo_armazen       = eg_simupreci-custo_armazen.
*        eg_saida-rate_icms_comp      = eg_simupreci-rate_icms_comp.
*        eg_saida-base_icms_comp      = eg_simupreci-base_icms_comp.
*        eg_saida-val_icms_comp       = eg_simupreci-val_icms_comp.
*        eg_saida-rate_ipi_comp       = eg_simupreci-rate_ipi_comp.
*        eg_saida-base_ipi_comp       = eg_simupreci-base_ipi_comp.
*        eg_saida-val_ipi_comp        = eg_simupreci-val_ipi_comp.
*        eg_saida-rate_cofins_comp    = eg_simupreci-rate_cofins_comp.
*        eg_saida-base_cofins_comp    = eg_simupreci-base_cofins_comp.
*        eg_saida-val_cofins_comp     = eg_simupreci-val_cofins_comp.
*        eg_saida-rate_pis_comp       = eg_simupreci-rate_pis_comp.
*        eg_saida-base_pis_comp       = eg_simupreci-base_pis_comp.
*        eg_saida-val_pis_comp        = eg_simupreci-val_pis_comp.
*        eg_saida-calc_base_st_comp   = eg_simupreci-calc_base_st_comp.
*        eg_saida-calc_icms_st_comp   = eg_simupreci-calc_icms_st_comp.
*        eg_saida-maj_bst_comp        = eg_simupreci-maj_bst_comp.
*        eg_saida-maj_bicms_comp      = eg_simupreci-maj_bicms_comp.
*        eg_saida-calc_pis_st_comp    = eg_simupreci-calc_pis_st_comp.
*        eg_saida-calc_cofins_st_comp = eg_simupreci-calc_cofins_st_comp.
*        eg_saida-rate_icms_venda     = eg_simupreci-rate_icms_venda.
*        eg_saida-base_icms_venda     = eg_simupreci-base_icms_venda.
*        eg_saida-rate_icms_st_comp   = eg_simupreci-rate_icms_st_comp.
*        eg_saida-rate_st_int_comp    = eg_simupreci-rate_st_int_comp.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*        eg_saida-var_cust_log        = eg_simupreci-var_cust_log.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*        eg_saida-calc_cofins_st_comp = eg_simupreci-calc_cofins_st_comp.
*        eg_saida-gestao              = eg_simupreci-gestao.
*        eg_saida-tx_desp             = eg_simupreci-tx_despachante.
*        eg_saida-tx_fob              = eg_simupreci-tx_fob.
*        eg_saida-despachante         = eg_simupreci-despachante.
*        eg_saida-fob                 = eg_simupreci-fob.
*        eg_saida-fin                 = eg_simupreci-fin.
*
*        "Buscar estado origem
*        CLEAR eg_t001w.
*        READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_simupreci-werks.
*        vl_regio_from = eg_t001w-regio.
*
*        "buscar estado destino
*        CLEAR eg_t001w.
*        READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_twkao-vlgwk.
*        vl_regio_to = eg_t001w-regio.
*
*        eg_saida-state_from = vl_regio_from.
*        eg_saida-state_to   = vl_regio_to.
*        eg_saida-vkkab      = eg_simuprech-vkkab.
*        eg_saida-werks_to   = eg_twkao-vlgwk.
*
*        PERFORM f_desc_status.      "Descrição do Status
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*        PERFORM fill_celltab CHANGING tl_celltab.
*        FREE: eg_saida-celltab.
*        INSERT LINES OF tl_celltab INTO TABLE eg_saida-celltab.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM
*        APPEND eg_saida TO tg_saida.
*
*      ENDLOOP.
*
*      "GP e DGP
*      vg_gp = eg_simuprech-gp.
**      vg_dgp = eg_simuprech-dgp.
*
*      CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
*        EXPORTING
*          input  = vg_gp
*        IMPORTING
*          output = vg_gp.
*
**      SELECT SINGLE name1
**               FROM lfa1
**               INTO vg_gpname
**              WHERE lifnr EQ vg_gp.
**      IF sy-subrc NE 0.
**        CLEAR vg_gpname.
**      ENDIF.
**      SELECT SINGLE name1
**               FROM lfa1
**               INTO vg_dgpname
**              WHERE lifnr EQ vg_dgp.
*    ENDLOOP.
*    SELECT SINGLE name1
*             FROM lfa1
*             INTO vg_gpname
*            WHERE lifnr EQ vg_gp.
*    IF sy-subrc NE 0.
*      CLEAR vg_gpname.
*    ENDIF.
*  ELSE.
*    REFRESH tg_pcl.
*
*    LOOP AT tg_t001w INTO eg_t001w_a.       " Processar centros
*      IF eg_t001w_a-werks NOT IN so_werks.
*        CONTINUE.
*      ENDIF.
*
*      LOOP AT tg_twkao INTO eg_twkao.                    "#EC CI_NESTED
*
*        CLEAR eg_saida.
*
*        IF rb_ped NE space OR rb_mat NE space.  "Seleção por pedido ou por material
*
*          LOOP AT tg_mara INTO eg_mara WHERE bwkey EQ eg_t001w_a-werks. "#EC CI_NESTED
*
*            "Dados do material e da lista de preço
*            eg_saida-matnr  = eg_mara-matnr.
*            eg_saida-maktx  = eg_mara-maktx.
*            eg_saida-pltyp  = eg_twkao-pltyp.
*            eg_saida-ptext  = eg_twkao-ptext.
*            eg_saida-qtde_min = 0.
*            eg_saida-vrkme  = eg_mara-meins.
*
*            "PCB do material
*            READ TABLE tg_pcb INTO eg_pcb WITH KEY matnr = eg_mara-matnr
*                                                   werks = eg_t001w_a-werks.
*            IF sy-subrc EQ 0.
*              eg_saida-pcb = eg_pcb-pcb.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*              eg_saida-ltsnr = eg_pcb-ltsnr.
** Alteração - CD.3723 - 24.01.2020 - fim.
*              eg_saida-lifnr = eg_pcb-lifnr.
*              eg_saida-ebeln = eg_pcb-ebeln.    "<002> - Inclusão do último pedido
*
*              IF eg_pcb-land1 <> 'BR'. "Se for diferente de BR, alterar Origem do Material para cálculo
*                eg_mara-mtorg = eg_saida-mtorg = 1.
*              ENDIF.
*            ELSE.        "Não encontrado PCB para o material/centro, o mesmo é inválido
*              CLEAR eg_saida.
*              CONTINUE.
*            ENDIF.
*
**            eg_saida-rappel = 0.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            IF vg_cd_unico IS INITIAL.
** Alteração - CD.3723 - 24.01.2020 - FIM
*              eg_saida-werks        = eg_t001w_a-werks.        "Centro
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            ELSE.
*              eg_saida-werks      = vg_cd_unico.
*              eg_saida-werks_ori  = eg_t001w_a-werks.
*            ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
**            eg_saida-werks = eg_t001w_a-werks.
*
*            "Buscar PV Final para primeira exibição do ALV
*            PERFORM f_seleciona_pvfinal.
*
*            "Buscar Rappel para primeira exibição do ALV
*            PERFORM f_seleciona_rappel.
*
*            "Buscar estado origem
*            CLEAR eg_t001w.
*            READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_t001w_a-werks.
*            vl_regio_from = eg_t001w-regio.
*
*            "buscar estado destino
*            CLEAR eg_t001w.
*            READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_twkao-vlgwk.
*            vl_regio_to = eg_t001w-regio.
*
*            "Preparar dados para cálculo de PCL, Custo Logístico, Preço de Transferência
*            "Preço de Venda Líquida, Margem Líquida e Margem Bruta
*            REFRESH tg_dados.
*            CLEAR eg_dados.
*            READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_saida-matnr
*                                                   werks = eg_t001w_a-werks.
*            IF sy-subrc EQ 0.
*              eg_dados-pi_pclx       = abap_false.
*              eg_dados-pe_pcl        = eg_pcl-pcl.
*              eg_dados-pe_pclst      = eg_pcl-pclst.
*              eg_dados-pe_rate_icms_comp      =  eg_pcl-rate_icms_comp.
*              eg_dados-pe_base_icms_comp      =  eg_pcl-base_icms_comp.
*              eg_dados-pe_val_icms_comp       =  eg_pcl-val_icms_comp.
*              eg_dados-pe_rate_ipi_comp       =  eg_pcl-rate_ipi_comp.
*              eg_dados-pe_base_ipi_comp       =  eg_pcl-base_ipi_comp.
*              eg_dados-pe_val_ipi_comp        =  eg_pcl-val_ipi_comp.
*              eg_dados-pe_rate_cofins_comp    =  eg_pcl-rate_cofins_comp.
*              eg_dados-pe_base_cofins_comp    =  eg_pcl-base_cofins_comp.
*              eg_dados-pe_val_cofins_comp     =  eg_pcl-val_cofins_comp.
*              eg_dados-pe_rate_pis_comp       =  eg_pcl-rate_pis_comp.
*              eg_dados-pe_base_pis_comp       =  eg_pcl-base_pis_comp.
*              eg_dados-pe_val_pis_comp        =  eg_pcl-val_pis_comp.
*              eg_dados-pe_calc_base_st_comp   =  eg_pcl-calc_base_st_comp.
*              eg_dados-pe_calc_icms_st_comp   =  eg_pcl-calc_icms_st_comp.
*              eg_dados-pe_maj_bst_comp        =  eg_pcl-maj_bst_comp.
*              eg_dados-pe_maj_bicms_comp      =  eg_pcl-maj_bicms_comp.
*              eg_dados-pe_calc_pis_st_comp    =  eg_pcl-calc_pis_st_comp.
*              eg_dados-pe_calc_cofins_st_comp =  eg_pcl-calc_cofins_st_comp.
*              eg_dados-pe_rate_icms_st_comp   =  eg_pcl-rate_icms_st_comp.
*              eg_dados-pe_rate_st_int_comp    =  eg_pcl-rate_st_int_comp.
*            ELSE.
*              eg_dados-pi_pclx       = abap_true.
*            ENDIF.
*
*            eg_dados-pi_matprecadx = space.
*            eg_dados-pi_matnr      = eg_saida-matnr.
*            eg_dados-pi_matnr_ref  = space.
*            eg_dados-pi_matkl      = eg_mara-matkl.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            IF vg_cd_unico IS INITIAL.
** Alteração - CD.3723 - 24.01.2020 - FIM
*              eg_dados-pi_werks        = eg_t001w_a-werks.        "Centro
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            ELSE.
*              eg_dados-pi_werks      = vg_cd_unico.
*            ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
**            eg_dados-pi_werks      = eg_t001w_a-werks.
*            eg_dados-pi_werks_to   = eg_twkao-vlgwk.
*            eg_dados-pi_vkkab      = sy-datum.
*            eg_dados-pi_pcb        = eg_saida-pcb.
*            eg_dados-pi_tipo       = '1'.            "Importado
*            eg_dados-pi_state_from = vl_regio_from.
*            eg_dados-pi_state_to   = vl_regio_to.
*            eg_dados-pi_rappel     = eg_saida-rappel.
*            eg_dados-pi_mtuse      = eg_mara-mtuse.
*            eg_dados-pi_mtorg      = eg_mara-mtorg.
*            eg_dados-pi_pvfin      = eg_saida-pv_fin.
*            eg_dados-pi_steuc      = eg_mara-steuc.
*            eg_dados-pi_uf_precad  = eg_saida-uf_precad.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            eg_dados-pi_lifnr      =  eg_saida-lifnr.
*            eg_dados-pi_ltsnr      =  eg_saida-ltsnr.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            APPEND eg_dados TO tg_dados.
*
*            eg_saida-matprecadx = eg_dados-pi_matprecadx.
*            eg_saida-matnr_ref  = eg_dados-pi_matnr_ref.
*            eg_saida-matkl      = eg_dados-pi_matkl.
*            eg_saida-vkkab      = eg_dados-pi_vkkab.
*            eg_saida-werks_to   = eg_dados-pi_werks_to.
*            eg_saida-state_from = eg_dados-pi_state_from.
*            eg_saida-state_to   = eg_dados-pi_state_to.
*            eg_saida-mtuse      = eg_dados-pi_mtuse.
*            eg_saida-mtorg      = eg_dados-pi_mtorg.
*            eg_saida-steuc      = eg_dados-pi_steuc.
*
*            CLEAR vl_new_pcb2.                              "FB23112018
*            CALL FUNCTION 'ZFSD_CALCULA_PCB_IMPORTADO'      "FB23112018
*              EXPORTING                                     "FB23112018
** Alteração - CD.3723 - 24.01.2020 - Inicio
*                i_centro   = eg_t001w_a-werks               "FB23112018
**               i_centro   = eg_saida-werks                 "FB23112018
** Alteração - CD.3723 - 24.01.2020 - FIM
*                i_pedido   = eg_saida-ebeln                 "FB23112018
*                i_material = eg_saida-matnr                 "FB23112018
*              IMPORTING                                     "FB23112018
*                o_real     = vl_new_pcb2                    "FB23112018
*              EXCEPTIONS                                    "FB23112018
*                sem_dados  = 0                              "FB23112018
*                OTHERS     = 0.
*            IF sy-subrc EQ 0.                               "FB23112018
*              vl_new_pcb3 = vl_new_pcb2.                    "FB23112018
*            ENDIF.
*            READ TABLE tg_pcb INTO eg_pcb                   "FB23112018
*             WITH KEY ebeln = eg_saida-ebeln                "FB23112018
** Alteração - CD.3723 - 24.01.2020 - Inicio
**                      werks = eg_saida-werks                "FB23112018
*                      werks = eg_t001w_a-werks              "FB23112018
** Alteração - CD.3723 - 24.01.2020 - FIM
*                      matnr = eg_saida-matnr.               "FB23112018
*            IF sy-subrc = 0.                                "FB23112018
*              vl_new_pcb3 = vl_new_pcb3 / eg_pcb-menge.     "FB23112018
*            ELSE.                                           "FB23112018
*              CLEAR vl_new_pcb3.                            "FB23112018
*            ENDIF.                                          "FB23112018
*
*            "Calcular valores
*            CALL FUNCTION 'ZFSD_CALCULA_PRECO'
*              EXPORTING                                     "FB23112018
*                i_pcl    = eg_dados-pi_pcb                  "FB23112018
*                i_pcb    = vl_new_pcb3                      "FB23112018
*              TABLES
*                tg_dados = tg_dados.
*
*            READ TABLE tg_dados INTO eg_dados INDEX 1.
*
*            "Preencher valores calculados para PCL, Custo Logístico, Preço de Transferência
*            "Preço de Venda Líquida, Margem Líquida e Margem Bruta e dados de impostos
*            eg_saida-pcl              = eg_dados-pe_pcl.
*            eg_saida-pclst            = eg_dados-pe_pclst.
*            eg_saida-custo_log        = eg_dados-pe_lco.
*            eg_saida-preco_transf     = eg_dados-pe_preco_transf.
*            eg_saida-pv_liq           = eg_dados-pe_pv_liq.
*            eg_saida-mg_liq           = eg_dados-pe_mg_liq.
*            eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
*            eg_saida-rate_icms        = eg_dados-pe_rate_icms.
*            eg_saida-base_icms        = eg_dados-pe_base_icms.
*            eg_saida-cust_icms        = eg_dados-pe_cust_icms.
*            eg_saida-val_icms         = eg_dados-pe_val_icms.
*            eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
*            eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
*            eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
*            eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
*            eg_saida-base_red_1       = eg_dados-pe_base_red_1.
*            eg_saida-base_red_2       = eg_dados-pe_base_red_2.
*            eg_saida-val_base_st      = eg_dados-pe_val_base_st.
*            eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
*            eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
*            eg_saida-base_ipi         = eg_dados-pe_base_ipi.
*            eg_saida-val_ipi          = eg_dados-pe_val_ipi.
*            eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
*            eg_saida-base_cofins      = eg_dados-pe_base_cofins.
*            eg_saida-val_cofins       = eg_dados-pe_val_cofins.
*            eg_saida-rate_pis         = eg_dados-pe_rate_pis.
*            eg_saida-base_pis         = eg_dados-pe_base_pis.
*            eg_saida-val_pis          = eg_dados-pe_val_pis.
*            eg_saida-val_rappel       = eg_dados-pe_val_rappel.
*            eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
*            eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
*            eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
*            eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
*
*            eg_saida-c_mvto           = eg_dados-pe_c_mvto.
*            eg_saida-c_pallet         = eg_dados-pe_c_pallet.
*            eg_saida-frete            = eg_dados-pe_frete.
*            eg_saida-tx_fin           = eg_dados-pe_tx_fin.
*            eg_saida-tx_gest          = eg_dados-pe_tx_gest.
*            eg_saida-c_arm            = eg_dados-pe_c_arm.
*            eg_saida-umrez            = eg_dados-pe_umrez.
*            eg_saida-hoehe            = eg_dados-pe_hoehe.
*            eg_saida-breit            = eg_dados-pe_breit.
*            eg_saida-laeng            = eg_dados-pe_laeng.
*            eg_saida-tx_mov           = eg_dados-pe_tx_mov.
*            eg_saida-tx_frete         = eg_dados-pe_tx_frete.
*            eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
*            eg_saida-dias_est         = eg_dados-pe_dias_est.
*            eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
*            eg_saida-gestao           = eg_dados-pe_gestao.
*            eg_saida-tx_desp          = eg_dados-pe_tx_desp.
*            eg_saida-tx_fob           = eg_dados-pe_tx_fob.
*            eg_saida-despachante      = eg_dados-pe_despachante.
*            eg_saida-fob              = eg_dados-pe_fob.
*            eg_saida-fin              = eg_dados-pe_fin.
*
*            eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*            eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*            eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*            eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*            eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*            eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*            eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*            eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*            eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*            eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*            eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*            eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*            eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*            eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*            eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*            eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*            eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*            eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*            eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*            eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            eg_saida-var_cust_log        =  eg_dados-pe_var_cust_log.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            eg_saida-status_i         = space.                    "Status aprovação
*            PERFORM f_desc_status.      "Descrição do Status
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*            PERFORM fill_celltab CHANGING tl_celltab.
*            FREE: eg_saida-celltab.
*            INSERT LINES OF tl_celltab INTO TABLE eg_saida-celltab.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM
*            APPEND eg_saida TO tg_saida.
*
*            READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_dados-pi_matnr
** Alteração - CD.3723 - 24.01.2020 - Inicio
**                                                   werks = eg_dados-pi_werks.
*                                                   werks = eg_t001w_a-werks.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            IF sy-subrc NE 0.
*              eg_pcl-matnr      = eg_dados-pi_matnr.
*              eg_pcl-werks      = eg_dados-pi_werks.
*              eg_pcl-pcl        = eg_dados-pe_pcl.
*              eg_pcl-pclst      = eg_dados-pe_pclst.
*              eg_pcl-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*              eg_pcl-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*              eg_pcl-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*              eg_pcl-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*              eg_pcl-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*              eg_pcl-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*              eg_pcl-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*              eg_pcl-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*              eg_pcl-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*              eg_pcl-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*              eg_pcl-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*              eg_pcl-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*              eg_pcl-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*              eg_pcl-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*              eg_pcl-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*              eg_pcl-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*              eg_pcl-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*              eg_pcl-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*              eg_pcl-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*              eg_pcl-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*              APPEND eg_pcl TO tg_pcl.
*            ENDIF.
*          ENDLOOP.
*
*        ELSEIF rb_mpc NE space.
*
*          LOOP AT tg_precadmat INTO eg_precadmat.        "#EC CI_NESTED
*
*            "Dados do material pré-cadastrado
*            eg_saida-matnr        = eg_precadmat-matnr.    "Material
*            eg_saida-maktx        = eg_precadmat-maktx.    "Descrição Material
*            eg_saida-pltyp        = eg_twkao-pltyp.        "Lista Preço,
*            eg_saida-ptext        = eg_twkao-ptext.        "Descrição lista de preço
*            eg_saida-qtde_min     = eg_precadmat-qtde_min. "Quantidade Mínima
*            eg_saida-vrkme        = eg_precadmat-meinh.    "Unidade de Medida
*            eg_saida-pcb          = eg_precadmat-pcbsim.   "PCB
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            IF vg_cd_unico IS INITIAL.
** Alteração - CD.3723 - 24.01.2020 - FIM
*              eg_saida-werks        = eg_t001w_a-werks.        "Centro
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            ELSE.
*              eg_saida-werks      = vg_cd_unico.
*              eg_saida-werks_ori  = eg_t001w_a-werks.
*            ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
*
**            eg_saida-werks        = eg_t001w_a-werks.      "Centro
*
*            eg_saida-cod_agrup    = eg_precadmat-cod_agrup.
*            eg_saida-desc_agrup   = eg_precadmat-desc_agrup.
*            eg_saida-uf_precad    = eg_precadmat-uf.
*
**            "PCB
**            READ TABLE tg_pcb INTO eg_pcb WITH KEY matnr = eg_precadmat-mat_imp
**                                                   werks = eg_t001w_a-werks.
**            IF sy-subrc EQ 0.
**              eg_saida-lifnr = eg_pcb-lifnr.
**            ELSE.            "Não encontrado PCB para o material/centro, o mesmo é inválido
**              CLEAR eg_saida.
**              CONTINUE.
**            ENDIF.
*
**            eg_saida-rappel         = 0. "Rappel %
*
*            "Buscar estado origem
*            CLEAR eg_t001w.
*            READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_t001w_a-werks.
*            vl_regio_from = eg_t001w-regio.
*
*            "buscar estado destino
*            CLEAR eg_t001w.
*            READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_twkao-vlgwk.
*            vl_regio_to = eg_t001w-regio.
*
*            IF eg_precadmat-mat_ref NE space.
*              "Dados do material de referência
*              READ TABLE tg_mara INTO eg_mara WITH KEY matnr = eg_precadmat-mat_imp
*                                                       bwkey = eg_t001w_a-werks.
*            ELSE.
*              eg_mara-matkl = eg_precadmat-matkl.
*              eg_mara-mtuse = eg_precadmat-mtuse.
*              eg_mara-mtorg = eg_precadmat-mtorg.
*              eg_mara-steuc = eg_precadmat-steuc.
*            ENDIF.
*
*            "Buscar PV Final para primeira exibição do ALV
*            PERFORM f_seleciona_pvfinal.
*
*            "Buscar Rappel para primeira exibição do ALV
*            PERFORM f_seleciona_rappel.
*
*            "Preparar dados para cálculo de PCL, Custo Logístico, Preço de Transferência
*            "Preço de Venda Líquida, Margem Líquida e Margem Bruta
*            REFRESH tg_dados.
*            CLEAR eg_dados.
*
*            READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_saida-matnr
*                                                   werks = eg_t001w_a-werks.
*            IF sy-subrc EQ 0.
*              eg_dados-pi_pclx       = abap_false.
*              eg_dados-pe_pcl        = eg_pcl-pcl.
*              eg_dados-pe_pclst      = eg_pcl-pclst.
*              eg_dados-pe_rate_icms_comp      =  eg_pcl-rate_icms_comp.
*              eg_dados-pe_base_icms_comp      =  eg_pcl-base_icms_comp.
*              eg_dados-pe_val_icms_comp       =  eg_pcl-val_icms_comp.
*              eg_dados-pe_rate_ipi_comp       =  eg_pcl-rate_ipi_comp.
*              eg_dados-pe_base_ipi_comp       =  eg_pcl-base_ipi_comp.
*              eg_dados-pe_val_ipi_comp        =  eg_pcl-val_ipi_comp.
*              eg_dados-pe_rate_cofins_comp    =  eg_pcl-rate_cofins_comp.
*              eg_dados-pe_base_cofins_comp    =  eg_pcl-base_cofins_comp.
*              eg_dados-pe_val_cofins_comp     =  eg_pcl-val_cofins_comp.
*              eg_dados-pe_rate_pis_comp       =  eg_pcl-rate_pis_comp.
*              eg_dados-pe_base_pis_comp       =  eg_pcl-base_pis_comp.
*              eg_dados-pe_val_pis_comp        =  eg_pcl-val_pis_comp.
*              eg_dados-pe_calc_base_st_comp   =  eg_pcl-calc_base_st_comp.
*              eg_dados-pe_calc_icms_st_comp   =  eg_pcl-calc_icms_st_comp.
*              eg_dados-pe_maj_bst_comp        =  eg_pcl-maj_bst_comp.
*              eg_dados-pe_maj_bicms_comp      =  eg_pcl-maj_bicms_comp.
*              eg_dados-pe_calc_pis_st_comp    =  eg_pcl-calc_pis_st_comp.
*              eg_dados-pe_calc_cofins_st_comp =  eg_pcl-calc_cofins_st_comp.
*              eg_dados-pe_rate_icms_st_comp   =  eg_pcl-rate_icms_st_comp.
*              eg_dados-pe_rate_st_int_comp    =  eg_pcl-rate_st_int_comp.
*            ELSE.
*              eg_dados-pi_pclx       = abap_true.
*            ENDIF.
*
*            eg_dados-pi_matprecadx = abap_true.
*            eg_dados-pi_matnr      = eg_saida-matnr.
*            eg_dados-pi_matnr_ref  = eg_precadmat-mat_imp.
*            eg_dados-pi_mat_ref    = eg_precadmat-mat_ref.
*            eg_dados-pi_matkl      = eg_mara-matkl.
*
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            IF vg_cd_unico IS INITIAL.
** Alteração - CD.3723 - 24.01.2020 - FIM
*              eg_dados-pi_werks        = eg_t001w_a-werks.        "Centro
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            ELSE.
*              eg_dados-pi_werks      = vg_cd_unico.
*            ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
*
**            eg_dados-pi_werks      = eg_t001w_a-werks.
*            eg_dados-pi_werks_to   = eg_twkao-vlgwk.
*            eg_dados-pi_vkkab      = sy-datum.
*            eg_dados-pi_pcb        = eg_saida-pcb.
*            eg_dados-pi_tipo       = '1'.            "Importado
*            eg_dados-pi_state_from = vl_regio_from.
*            eg_dados-pi_state_to   = vl_regio_to.
*            eg_dados-pi_rappel     = eg_saida-rappel.
*            eg_dados-pi_mtuse      = eg_mara-mtuse.
*            eg_dados-pi_mtorg      = eg_mara-mtorg.
*            eg_dados-pi_pvfin      = eg_saida-pv_fin.
*            eg_dados-pi_steuc      = eg_mara-steuc.
*            eg_dados-pi_mwskz      = eg_precadmat-mwskz.
*            eg_dados-pi_uf_precad  = eg_saida-uf_precad.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            eg_dados-pi_lifnr      =  eg_saida-lifnr.
*            eg_dados-pi_ltsnr      =  eg_saida-ltsnr.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            APPEND eg_dados TO tg_dados.
*
*            eg_saida-matprecadx = eg_dados-pi_matprecadx.
*            eg_saida-matnr_ref  = eg_dados-pi_matnr_ref.
*            eg_saida-matkl      = eg_dados-pi_matkl.
*            eg_saida-vkkab      = eg_dados-pi_vkkab.
*            eg_saida-werks_to   = eg_dados-pi_werks_to.
*            eg_saida-state_from = eg_dados-pi_state_from.
*            eg_saida-state_to   = eg_dados-pi_state_to.
*            eg_saida-mtuse      = eg_dados-pi_mtuse.
*            eg_saida-mtorg      = eg_dados-pi_mtorg.
*            eg_saida-steuc      = eg_dados-pi_steuc.
*            eg_saida-mwskz      = eg_dados-pi_mwskz.
*            eg_saida-mat_ref    = eg_dados-pi_mat_ref.
*
*            "Calcular valores
*            CALL FUNCTION 'ZFSD_CALCULA_PRECO'
*              TABLES
*                tg_dados = tg_dados.
*
*            READ TABLE tg_dados INTO eg_dados INDEX 1.
*
*            "Preencher valores calculados para PCL, Custo Logístico, Preço de Transferência
*            "Preço de Venda Líquida, Margem Líquida e Margem Bruta e dados de impostos
*            eg_saida-pcl              = eg_dados-pe_pcl.          "PCL
*            eg_saida-pclst            = eg_dados-pe_pclst.
*            eg_saida-custo_log        = eg_dados-pe_lco.          "Custo Logistico %
*            eg_saida-preco_transf     = eg_dados-pe_preco_transf. "Preço Transferência
*            eg_saida-pv_liq           = eg_dados-pe_pv_liq.       "PV Liquido
*            eg_saida-mg_liq           = eg_dados-pe_mg_liq.       "Margem Líquida %
*            eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.     "Margem Bruta %
*            eg_saida-rate_icms        = eg_dados-pe_rate_icms.
*            eg_saida-base_icms        = eg_dados-pe_base_icms.
*            eg_saida-cust_icms        = eg_dados-pe_cust_icms.
*            eg_saida-val_icms         = eg_dados-pe_val_icms.
*            eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
*            eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
*            eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
*            eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
*            eg_saida-base_red_1       = eg_dados-pe_base_red_1.
*            eg_saida-base_red_2       = eg_dados-pe_base_red_2.
*            eg_saida-val_base_st      = eg_dados-pe_val_base_st.
*            eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
*            eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
*            eg_saida-base_ipi         = eg_dados-pe_base_ipi.
*            eg_saida-val_ipi          = eg_dados-pe_val_ipi.
*            eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
*            eg_saida-base_cofins      = eg_dados-pe_base_cofins.
*            eg_saida-val_cofins       = eg_dados-pe_val_cofins.
*            eg_saida-rate_pis         = eg_dados-pe_rate_pis.
*            eg_saida-base_pis         = eg_dados-pe_base_pis.
*            eg_saida-val_pis          = eg_dados-pe_val_pis.
*            eg_saida-val_rappel       = eg_dados-pe_val_rappel.
*            eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
*            eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
*            eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
*            eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
*
*
*            eg_saida-c_mvto           = eg_dados-pe_c_mvto.
*            eg_saida-c_pallet         = eg_dados-pe_c_pallet.
*            eg_saida-frete            = eg_dados-pe_frete.
*            eg_saida-tx_fin           = eg_dados-pe_tx_fin.
*            eg_saida-tx_gest          = eg_dados-pe_tx_gest.
*            eg_saida-c_arm            = eg_dados-pe_c_arm.
*            eg_saida-umrez            = eg_dados-pe_umrez.
*            eg_saida-hoehe            = eg_dados-pe_hoehe.
*            eg_saida-breit            = eg_dados-pe_breit.
*            eg_saida-laeng            = eg_dados-pe_laeng.
*            eg_saida-tx_mov           = eg_dados-pe_tx_mov.
*            eg_saida-tx_frete         = eg_dados-pe_tx_frete.
*            eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
*            eg_saida-dias_est         = eg_dados-pe_dias_est.
*            eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
*            eg_saida-gestao           = eg_dados-pe_gestao.
*            eg_saida-tx_desp          = eg_dados-pe_tx_desp.
*            eg_saida-tx_fob           = eg_dados-pe_tx_fob.
*            eg_saida-despachante      = eg_dados-pe_despachante.
*            eg_saida-fob              = eg_dados-pe_fob.
*            eg_saida-fin              = eg_dados-pe_fin.
*
*            eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*            eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*            eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*            eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*            eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*            eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*            eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*            eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*            eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*            eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*            eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*            eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*            eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*            eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*            eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*            eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*            eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*            eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*            eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*            eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*            eg_saida-status_i         = space.                    "Status aprovação
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            eg_saida-var_cust_log        =  eg_dados-pe_var_cust_log.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*            PERFORM f_desc_status.      "Descrição do Status
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*            PERFORM fill_celltab CHANGING tl_celltab.
*            FREE: eg_saida-celltab.
*            INSERT LINES OF tl_celltab INTO TABLE eg_saida-celltab.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM
*            APPEND eg_saida TO tg_saida.
*
*            READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_dados-pi_matnr
*                                                   werks = eg_dados-pi_werks.
*            IF sy-subrc NE 0.
*              eg_pcl-matnr      = eg_dados-pi_matnr.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*              IF vg_cd_unico IS INITIAL.
** Alteração - CD.3723 - 24.01.2020 - FIM
*                eg_pcl-werks        = eg_dados-pi_werks.        "Centro
** Alteração - CD.3723 - 24.01.2020 - Inicio
*              ELSE.
*                eg_pcl-werks      = vg_cd_unico.
*              ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
*
**              eg_pcl-werks      = eg_dados-pi_werks.
*              eg_pcl-pcl        = eg_dados-pe_pcl.
*              eg_pcl-pclst      = eg_dados-pe_pclst.
*              eg_pcl-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*              eg_pcl-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*              eg_pcl-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*              eg_pcl-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*              eg_pcl-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*              eg_pcl-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*              eg_pcl-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*              eg_pcl-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*              eg_pcl-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*              eg_pcl-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*              eg_pcl-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*              eg_pcl-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*              eg_pcl-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*              eg_pcl-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*              eg_pcl-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*              eg_pcl-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*              eg_pcl-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*              eg_pcl-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*              eg_pcl-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*              eg_pcl-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*              APPEND eg_pcl TO tg_pcl.
*            ENDIF.
*
*          ENDLOOP.
*        ENDIF.
*      ENDLOOP.
*    ENDLOOP.
*  ENDIF.
*
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Início da Inclusão
*  DATA tl_ekpo2 TYPE TABLE OF ty_ekpo.
*  tl_ekpo2 = tg_ekpo.
*  SORT tl_ekpo2 BY ebeln.
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Fim da Inclusão
*
** Alteração - CC.2279 - Luiz - 28.10.2018 - Inicio
*  IF rb_sim = space AND rb_mpc <> 'X'.                      "FB04122018
*    DATA: vl_new_pcb TYPE dmbtr,
*          vl_tabix   TYPE sy-tabix.
*    SORT tg_pcb BY ebeln werks matnr.
*    LOOP AT tg_saida INTO eg_saida.
*      CLEAR: vl_new_pcb, eg_pcb.
*      vl_tabix = sy-tabix.
** Alteração - CD.3723 - 24.01.2020 - Inicio
*      IF vg_cd_unico IS INITIAL.
*        vl_werks = eg_saida-werks.
*      ELSE.
*        vl_werks = eg_saida-werks_ori.
*      ENDIF.
** Alteração - CD.3723 - 24.01.2020 - FIM
*      CALL FUNCTION 'ZFSD_CALCULA_PCB_IMPORTADO'
*        EXPORTING
** Alteração - CD.3723 - 24.01.2020 - Inicio
*          i_centro   = vl_werks
**         i_centro   = eg_saida-werks
** Alteração - CD.3723 - 24.01.2020 - Inicio
*          i_pedido   = eg_saida-ebeln
*          i_material = eg_saida-matnr
*        IMPORTING
**         T_SAIDA    =
*          o_real     = vl_new_pcb
*        EXCEPTIONS
*          sem_dados  = 1
*          OTHERS     = 2.
*      IF sy-subrc NE 0.
*        CLEAR : vl_new_pcb.
*      ENDIF.
*      eg_saida-pcl = eg_saida-pcb.
*      READ TABLE tg_pcb INTO eg_pcb WITH KEY ebeln = eg_saida-ebeln
** Alteração - CD.3723 - 24.01.2020 - Inicio
*                                             werks = vl_werks
**                                             werks = eg_saida-werks
** Alteração - CD.3723 - 24.01.2020 - FIM
*                                             matnr = eg_saida-matnr
*                                    BINARY SEARCH.
*      IF eg_pcb-menge <> 0.
*        eg_saida-pcb = vl_new_pcb / eg_pcb-menge.
*
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Início da Inclusão
*        READ TABLE tl_ekpo2 ASSIGNING FIELD-SYMBOL(<tl_ekpo2>)
*          WITH KEY ebeln = eg_saida-ebeln BINARY SEARCH.
*        IF sy-subrc = 0.
*          eg_saida-pcb = eg_saida-pcb / ( <tl_ekpo2>-umrez / <tl_ekpo2>-umren ).
*        ENDIF.
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Fim da Inclusão
*
*      ELSE.
*        eg_saida-pcb = vl_new_pcb.
*      ENDIF.
*      MODIFY tg_saida FROM eg_saida INDEX vl_tabix.
*    ENDLOOP.
*  ENDIF.                                                    "FB04122018
** Alteração - CC.2279 - Luiz - 28.10.2018 - fim
*  "Classificar dados do relatório
*  SORT tg_saida BY matnr pltyp werks werks_to.
** Alteração - CC4486 - 07.05.2020  - Inicio
*  DELETE ADJACENT DUPLICATES FROM tg_saida COMPARING matnr pltyp werks werks_to.
** Alteração - CC4486 - 07.05.2020  - FIM
*ENDFORM.                    " F_PROCESSA_DADOS

*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*      -->DG_DYNDOC_ID  text
*----------------------------------------------------------------------*
FORM event_top_of_page USING  p_dyndoc_id TYPE REF TO cl_dd_document.

  "first add text, then pass it to comentry write fm
  DATA : vl_text(255) TYPE c.  "Text

* Preencher TOP OF PAGE
  IF p_docsim IS NOT INITIAL.
    CLEAR : vl_text.
    CONCATENATE 'Documento de Simulação:' p_docsim
           INTO vl_text SEPARATED BY space.
    PERFORM add_text USING vl_text.

* Add new-line
    CALL METHOD p_dyndoc_id->new_line.
  ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  IF rb_aut = abap_false.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
    CLEAR : vl_text.
    CONCATENATE 'GP:' vg_gp '-' vg_gpname
           INTO vl_text SEPARATED BY space.
    PERFORM add_text USING vl_text.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
** Add new-line
*  CALL METHOD p_dyndoc_id->new_line.
*
*  CLEAR : vl_text.
**  CONCATENATE 'DGP:' vg_dgp '-' vg_dgpname
**         INTO vl_text SEPARATED BY space.
**
**  PERFORM add_text USING vl_text.

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
*    IMPORTING
*      length   = vl_length.

* Get TOP->HTML_TABLE ready
  CALL METHOD vg_dyndoc_id->merge_document.

* Set wallpaper
  CALL METHOD vg_dyndoc_id->set_document_background
    EXPORTING
      picture_id = vl_background_id.

* Connect TOP document to HTML-Control
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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_create_and_init_alv .
  DATA: lt_exclude TYPE ui_functions.

  "create the container
  CREATE OBJECT vg_custom_container
    EXPORTING
      container_name = c_container.

* Create TOP-Document
  CREATE OBJECT vg_dyndoc_id
    EXPORTING
      style = 'ALV_GRID'.

* Create Splitter for custom_container
  CREATE OBJECT vg_splitter
    EXPORTING
      parent  = vg_custom_container
      rows    = 2
      columns = 1.

* Split the custom_container to two containers and move the reference
* to receiving containers vg_parent_html and vg_parent_grid
  CALL METHOD vg_splitter->get_container
    EXPORTING
      row       = 1
      column    = 1
    RECEIVING
      container = vg_parent_html.

* Set height for g_parent_html
  CALL METHOD vg_splitter->set_row_height
    EXPORTING
      id     = 1
      height = 10.

  CALL METHOD vg_splitter->get_container
    EXPORTING
      row       = 2
      column    = 1
    RECEIVING
      container = vg_parent_grid.

  CREATE OBJECT vg_grid
    EXPORTING
      i_parent = vg_parent_grid.


  PERFORM f_layout_grid.

* setting focus for created grid control
  CALL METHOD cl_gui_control=>set_focus
    EXPORTING
      control = vg_grid.

* Register ENTER to raise event DATA_CHANGED.
  CALL METHOD vg_grid->register_edit_event
    EXPORTING
      i_event_id = cl_gui_alv_grid=>mc_evt_enter.

  CREATE OBJECT vg_handler.
  SET HANDLER vg_handler->handle_top_of_page FOR vg_grid.
  SET HANDLER vg_handler->handle_toolbar FOR vg_grid.
*  SET HANDLER vg_handler->handle_hotspot FOR vg_grid.
*  SET HANDLER vg_handler->handle_menu_button FOR vg_grid.
  SET HANDLER vg_handler->handle_user_command FOR vg_grid.
  SET HANDLER vg_handler->handle_data_changed FOR vg_grid.
  SET HANDLER vg_handler->handle_data_changed_finished FOR vg_grid.

  PERFORM f_descreve_campos_grid.

* Optionally restrict generic functions to 'change only'.
*   (The user shall not be able to add new lines).
  PERFORM f_exclude_tb_functions CHANGING lt_exclude.

**Variant to save the layout
  eg_vari-report      = sy-repid.
*  eg_vari-handle      = space.
  eg_vari-log_group   = space.
  eg_vari-username    = space.
  eg_vari-variant     = space.
  eg_vari-text        = space.
  eg_vari-dependvars  = space.
  eg_vari-handle      = 'GRID'.

**Calling the Method for ALV output
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  IF rb_aut = abap_false.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
    CALL METHOD vg_grid->set_table_for_first_display
      EXPORTING
        it_toolbar_excluding = lt_exclude
        is_variant           = eg_vari
        is_layout            = vg_layout
        i_save               = 'A'
      CHANGING
        it_fieldcatalog      = tg_fieldcat
        it_outtab            = tg_saida[].
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - INICIO
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
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
* Initializing document
  CALL METHOD vg_dyndoc_id->initialize_document.

* Processing events
  CALL METHOD vg_grid->list_processing_events
    EXPORTING
      i_event_name = 'TOP_OF_PAGE'
      i_dyndoc_id  = vg_dyndoc_id.
  "end }
* Set editable cells to ready for input initially
  CALL METHOD vg_grid->set_ready_for_input
    EXPORTING
      i_ready_for_input = 1.

ENDFORM.                    " F_CREATE_AND_INIT_ALV
*&---------------------------------------------------------------------*
*&      Form  F_EXCLUDE_TB_FUNCTIONS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*      -->PT_EXCLUDE text
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
*&      Form  F_VALIDA_CAMPOS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_valida_campos .
*  DATA: tl_werks TYPE TABLE OF werks_d.
*
** Campos obrigatórios
*  IF p_vkorg IS INITIAL.
*    "Informar Organização de Vendas
*    MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m01 DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
*
*  IF p_vtweg IS INITIAL.
*    "Informar Canal de Distribuição
*    MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m02 DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
*
*  IF so_pltyp[] IS INITIAL.
*    "Informar Lista de Preço
*    MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m03 DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
*
*  IF so_vkkab[] IS INITIAL.
*    "Informar Validade
*    MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m04 DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
*
*  IF so_werks[] IS INITIAL.
*    "Informar Centro
*    MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m07 DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ELSE.
*    SELECT werks
*      FROM t001w
*      INTO TABLE tl_werks
*    WHERE werks IN so_werks
*      AND vlfkz = 'B'.
*    IF sy-subrc EQ 0.
*      IF tl_werks[] IS INITIAL.
*        "Informar um centro válido (CD).
*        MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m08 DISPLAY LIKE 'E'.
*        vg_erro = abap_true.
*      ENDIF.
*    ELSE.
*      MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m08 DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ENDIF.
*  ENDIF.
*
*  LOOP AT so_vkkab.
*    IF so_vkkab-low < sy-datum.
*      "Validade encontra-se no passado
*      MESSAGE s077(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*      EXIT.
*    ENDIF.
*  ENDLOOP.
*
*  IF rb_ped NE space.
*    IF so_ebeln[] IS INITIAL.
*      "Informar pedido
*      MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m05 DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ELSE.
** Validar se o pedido é de importação
*      SELECT  a~ebeln a~lifnr b~ltsnr UP TO 1 ROWS
*        INTO (ekko-ebeln, ekko-lifnr, ekpo-ltsnr)
*        FROM ekko AS a INNER JOIN ekpo AS b
*          ON a~ebeln = b~ebeln
*        WHERE a~ebeln IN so_ebeln
*          AND a~bsart IN gr_bsart.
*      ENDSELECT.
*      IF sy-subrc NE 0.
*        "Pedido não é de importação
*        MESSAGE s078(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*        vg_erro = abap_true.
*      ENDIF.
*    ENDIF.
*
*  ELSEIF rb_mat NE space.
*
*    IF so_matnr[] IS INITIAL.
*      "Informar material
*      MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m06 DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ELSE.
*      "Verificar se os materiais possuem o mesmo código de aprovador
*      SELECT b~responsibility
*        INTO TABLE tg_gp
*        FROM wrf_matgrp_prod AS a INNER JOIN wrf_matgrp_md3 AS b
*        ON a~hiernode3 = b~node AND
*           a~hier_id = b~hier_id
*        WHERE a~matnr IN so_matnr
*          AND a~hier_id = 'L1'
*          AND a~date_from <= sy-datum
*          AND a~date_to >= sy-datum
*          AND a~deleteflag EQ space
*          AND b~date_from <= sy-datum
*          AND b~date_to >= sy-datum
*          AND b~deleteflag EQ space.
*
**      SELECT b~lifn2
**        INTO TABLE tg_gp
**        FROM eina AS a INNER JOIN wyt3 AS b
**          ON a~lifnr = b~lifnr AND
**             a~ltsnr = b~ltsnr
**        INNER JOIN eine AS c
**          ON a~infnr = c~infnr
**        WHERE a~matnr IN so_matnr
**          AND a~loekz EQ space
**          AND b~parvw EQ c_zg
**          AND c~loekz EQ space.
*
*      IF sy-subrc NE 0.
*        "Materiais não possuem GP aprovador
*        MESSAGE s079(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*        vg_erro = abap_true.
*      ELSE.
*        "Verificar se há apenas um GP aprovador
*        SORT tg_gp BY lifn2.
*        DELETE ADJACENT DUPLICATES FROM tg_gp.
*        DESCRIBE TABLE tg_gp.
*
*        IF sy-tfill <> 1.
*          "Materiais possuem códigos de aprovador diferentes. Ajustar seleção.
*          MESSAGE s080(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*          vg_erro = abap_true.
*        ELSE.
*          "Selecionar DGP
*          READ TABLE tg_gp INTO eg_gp INDEX 1.
*
*          vg_gp = eg_gp-lifn2.
*
*          CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
*            EXPORTING
*              input  = vg_gp
*            IMPORTING
*              output = vg_gp.
*
*          SELECT SINGLE name1
*            FROM lfa1
*            INTO vg_gpname
*            WHERE lifnr EQ vg_gp.
*
**          SELECT SINGLE lifn2
**          INTO vg_dgp
**          FROM wyt3
**          WHERE lifnr EQ eg_gp-lifn2
**            AND parvw EQ c_zd.
**
**          SELECT SINGLE name1
**            FROM lfa1
**            INTO vg_dgpname
**            WHERE lifnr EQ vg_dgp.
*
*          REFRESH: tg_gp.
*
*        ENDIF.
*      ENDIF.
*    ENDIF.
*
*  ELSEIF rb_mpc NE space.       "Seleção por material pré-cadastrado
*    IF so_mati[] IS INITIAL AND p_cagrp IS INITIAL.
*      "Informar material
*      MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m06 DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ELSE.
*
*      IF so_mati[] IS NOT INITIAL AND
*         p_cagrp > 0.
*        "Informar apenas código do material OU código de agrupamento
*        MESSAGE s076(zmsd_classe_mensagem) WITH TEXT-m09 DISPLAY LIKE 'E'.
*        vg_erro = abap_true.
*      ELSE.
*        IF so_mati[] IS NOT INITIAL.
*          SELECT *
*            INTO TABLE tg_precadmat
*            FROM ztsdd_precadmat
*            WHERE matnr IN so_mati.
*
*        ELSEIF p_cagrp IS NOT INITIAL.
*          SELECT *
*            INTO TABLE tg_precadmat
*            FROM ztsdd_precadmat
*           WHERE cod_agrup EQ p_cagrp.
*        ENDIF.
*
*        IF tg_precadmat[] IS INITIAL.
*          "Materiais pré-cadastrados não encontrados
*          MESSAGE s081(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*          vg_erro = abap_true.
*
*        ELSE.
*          READ TABLE tg_precadmat INTO eg_precadmat WITH KEY mat_ref = abap_true.
*          IF sy-subrc EQ 0.
*            tg_precadmat_aux[] = tg_precadmat[].
*            DELETE tg_precadmat_aux WHERE mat_ref EQ space.
*
*            "Verificar se os materiais possuem o mesmo código de aprovador
*            IF NOT tg_precadmat_aux[] IS INITIAL.
*              SELECT b~responsibility
*                INTO TABLE tg_gp
*                FROM wrf_matgrp_prod AS a INNER JOIN wrf_matgrp_md3 AS b
*                ON a~hiernode3 = b~node AND
*                   a~hier_id = b~hier_id
*                FOR ALL ENTRIES IN tg_precadmat_aux
*                WHERE a~matnr EQ tg_precadmat_aux-mat_imp
*                  AND a~hier_id = 'L1'
*                  AND a~date_from <= sy-datum
*                  AND a~date_to >= sy-datum
*                  AND a~deleteflag EQ space
*                  AND b~date_from <= sy-datum
*                  AND b~date_to >= sy-datum
*                  AND b~deleteflag EQ space.
*              IF sy-subrc EQ 0.
*                SORT tg_gp.
*              ENDIF.
*            ENDIF.
**            SELECT b~lifn2
**              INTO TABLE tg_gp
**              FROM eina AS a INNER JOIN wyt3 AS b
**                ON a~lifnr = b~lifnr AND
**                   a~ltsnr = b~ltsnr
**              INNER JOIN eine AS c
**                ON a~infnr = c~infnr
**              FOR ALL ENTRIES IN tg_precadmat_aux
**              WHERE a~matnr EQ tg_precadmat_aux-mat_imp
**                AND a~loekz EQ space
**                AND b~parvw EQ c_zg
**                AND c~loekz EQ space.
*
*            IF sy-subrc NE 0.
*              "Materiais não possuem GP aprovador
*              MESSAGE s079(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*              vg_erro = abap_true.
*            ELSE.
*              "Verificar se os materiais pré-cadastrados com material de referência possuem os mesmos GPs aprovadores
*              "dos pré-cadastros criados sem referência
*              LOOP AT tg_precadmat INTO eg_precadmat WHERE mat_ref IS INITIAL.
*                READ TABLE tg_gp INTO eg_gp WITH KEY lifn2 = eg_precadmat-gp.
*                IF sy-subrc NE 0.
*                  "GP aprovador dos materiais pré-cadastrados(com e sem ref) são diferentes.
*                  MESSAGE s115(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*                  vg_erro = abap_true.
*                ENDIF.
*              ENDLOOP.
*
*              "Verificar se há apenas um GP aprovador
*              SORT tg_gp BY lifn2.
*              DELETE ADJACENT DUPLICATES FROM tg_gp.
*              DESCRIBE TABLE tg_gp.
*
*              IF sy-tfill <> 1.
*                "Materiais possuem códigos de aprovador diferentes. Ajustar seleção.
*                MESSAGE s080(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*                vg_erro = abap_true.
*              ELSE.
*                "Selecionar DGP
*                READ TABLE tg_gp INTO eg_gp INDEX 1.
*
*                vg_gp = eg_gp-lifn2.
*                CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
*                  EXPORTING
*                    input  = vg_gp
*                  IMPORTING
*                    output = vg_gp.
*
*
*
**              SELECT SINGLE lifn2
**              INTO vg_dgp
**              FROM wyt3
**              WHERE lifnr EQ eg_gp-lifn2
**                AND parvw EQ c_zd.
**
**              SELECT SINGLE name1
**                          FROM lfa1
**                          INTO vg_dgpname
**                          WHERE lifnr EQ vg_dgp.
*
*                REFRESH: tg_gp.
*              ENDIF.
*            ENDIF.
*          ELSE.
*            LOOP AT tg_precadmat INTO eg_precadmat WHERE mat_ref IS INITIAL.
*
*              CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
*                EXPORTING
*                  input  = eg_precadmat-gp
*                IMPORTING
*                  output = eg_precadmat-gp.
*
*              IF vg_gp IS INITIAL.
*                vg_gp = eg_precadmat-gp.
*
*                CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
*                  EXPORTING
*                    input  = vg_gp
*                  IMPORTING
*                    output = vg_gp.
*
**                SELECT SINGLE name1
**                            FROM lfa1
**                            INTO vg_gpname
**                            WHERE lifnr EQ vg_gp.
**                IF sy-subrc NE 0.
**                  CLEAR vg_gpname.
**                ENDIF.
*                CONTINUE.
*              ELSE.
*                IF vg_gp <> eg_precadmat-gp.
*                  "Materiais possuem códigos de aprovador diferentes. Ajustar seleção.
*                  MESSAGE s080(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*                  vg_erro = abap_true.
**                  EXIT.
*                ENDIF.
*              ENDIF.
*            ENDLOOP.
** Alteração por ATC - Inicio.
*            SELECT SINGLE name1
*                        FROM lfa1
*                        INTO vg_gpname
*                        WHERE lifnr EQ vg_gp.
*            IF sy-subrc NE 0.
*              CLEAR vg_gpname.
*            ENDIF.
** Alteração por ATC - Inicio.
*          ENDIF.
*        ENDIF.
*      ENDIF.
*    ENDIF.
*  ENDIF.
*ENDFORM.                    " F_VALIDA_CAMPOS
*&---------------------------------------------------------------------*
*&      Form  F_SELECAO_PEDIDO
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_selecao_pedido .
*
*  "Buscar materiais dos pedidos
*  SELECT b~matnr
*         b~werks
*         INTO TABLE tg_materiais
*         FROM ekko AS a INNER JOIN ekpo AS b
*           ON a~ebeln EQ b~ebeln
*         WHERE a~ebeln IN so_ebeln
*           AND a~bsart IN gr_bsart
*           AND a~loekz EQ space    "<002> - Filtrar pedidos marcados para eliminação
*           AND b~loekz EQ space.   "<002> - Filtrar pedidos marcados para eliminação
*  IF sy-subrc EQ 0.
*    SORT tg_materiais BY matnr.
*    DELETE ADJACENT DUPLICATES FROM tg_materiais.
*  ENDIF.
*  IF tg_materiais[] IS NOT INITIAL.
*    "Buscar dados dos materiais
*    SELECT a~matnr
*           a~mtart
*           a~matkl
*           a~meins
*           a~bstat
*           b~maktx
*           c~bwkey
*           c~mtuse
*           c~mtorg
*           d~werks
*           d~steuc
*      INTO TABLE tg_mara
*      FROM mara AS a INNER JOIN makt AS b
*      ON a~matnr EQ b~matnr
*          INNER JOIN mbew AS c
*      ON a~matnr EQ c~matnr
*          INNER JOIN marc AS d
*      ON a~matnr EQ d~matnr
*      FOR ALL ENTRIES IN tg_materiais
*      WHERE a~matnr EQ tg_materiais-matnr
*        AND a~lvorm EQ space.
**        AND d~werks EQ tg_materiais-werks.
*    IF sy-subrc EQ 0.
*      DELETE tg_mara WHERE mtart NOT IN gr_mtart.   "Tipo de documento
*      DELETE tg_mara WHERE bstat NOT IN gr_bstat.   "Status
*      DELETE tg_mara WHERE werks NE c_bwkey.        "Centro
*      DELETE tg_mara WHERE mtorg NOT IN gr_mtorg.   "Origem do material
*    ENDIF.
*    LOOP AT tg_mara INTO eg_mara.
*      READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_mara-bwkey.
*      IF sy-subrc NE 0.
*        DELETE tg_mara.
*      ENDIF.
*    ENDLOOP.
*
*    IF tg_mara[] IS INITIAL.
*      "Pedido não possui material válido para simulação
*      MESSAGE s073(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ELSE.
*      PERFORM f_busca_pcb.
*      IF sy-uname EQ '51024988'.
*        PERFORM f_busca_pcb_2.
*      ENDIF.
*    ENDIF.
*
*    "Verificar se os materiais possuem o mesmo código de aprovador
*    SELECT b~responsibility
*      INTO TABLE tg_gp
*      FROM wrf_matgrp_prod AS a INNER JOIN wrf_matgrp_md3 AS b
*      ON a~hiernode3 = b~node AND
*         a~hier_id = b~hier_id
*      FOR ALL ENTRIES IN tg_materiais
*      WHERE a~matnr EQ tg_materiais-matnr
*        AND a~hier_id = 'L1'
*        AND a~date_from <= sy-datum
*        AND a~date_to >= sy-datum
*        AND a~deleteflag EQ space
*        AND b~date_from <= sy-datum
*        AND b~date_to >= sy-datum
*        AND b~deleteflag EQ space.
*
**    SELECT b~lifn2
**      INTO TABLE tg_gp
**      FROM eina AS a INNER JOIN wyt3 AS b
**        ON a~lifnr = b~lifnr AND
**           a~ltsnr = b~ltsnr
**      INNER JOIN eine AS c
**          ON a~infnr = c~infnr
**      FOR ALL ENTRIES IN tg_materiais
**      WHERE a~matnr EQ tg_materiais-matnr
**        AND a~loekz EQ space
**        AND b~parvw EQ c_zg
**        AND c~loekz EQ space.
*
*    IF sy-subrc NE 0.
*      "Materiais não possuem GP aprovador
*      MESSAGE s079(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*      vg_erro = abap_true.
*    ELSE.
*      "Verificar se há apenas um GP aprovador
*      SORT tg_gp BY lifn2.
*      DELETE ADJACENT DUPLICATES FROM tg_gp.
*      DESCRIBE TABLE tg_gp.
*
*      IF sy-tfill <> 1.
*        "Materiais possuem códigos de aprovador diferentes. Ajustar seleção.
*        MESSAGE s080(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*        vg_erro = abap_true.
*      ELSE.
*        "Selecionar DGP
*        READ TABLE tg_gp INTO eg_gp INDEX 1.
*
*        vg_gp = eg_gp-lifn2.
*
*        CALL FUNCTION 'CONVERSION_EXIT_ALPHA_INPUT'
*          EXPORTING
*            input  = vg_gp
*          IMPORTING
*            output = vg_gp.
*
*        SELECT SINGLE name1
*          FROM lfa1
*          INTO vg_gpname
*          WHERE lifnr EQ vg_gp.
*
**        SELECT SINGLE lifn2
**        INTO vg_dgp
**        FROM wyt3
**        WHERE lifnr EQ eg_gp-lifn2
**          AND parvw EQ c_zd.
**
**        SELECT SINGLE name1
**          FROM lfa1
**          INTO vg_dgpname
**          WHERE lifnr EQ vg_dgp.
*
*        REFRESH: tg_gp.
*      ENDIF.
*    ENDIF.
*  ELSE.
*    "Não há dados para processamento
*    MESSAGE s107(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
*
*ENDFORM.                    " F_SELECAO_PEDIDO
*&---------------------------------------------------------------------*
*&      Form  F_SELECAO_MATERIAL
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_selecao_material .
*
*  "Buscar dados dos materiais
*  SELECT a~matnr
*         a~mtart
*         a~matkl
*         a~meins
*         a~bstat
*         b~maktx
*         c~bwkey
*         c~mtuse
*         c~mtorg
*         d~werks
*         d~steuc
*    INTO TABLE tg_mara
*    FROM mara AS a INNER JOIN makt AS b
*    ON a~matnr EQ b~matnr
*        INNER JOIN mbew AS c
*    ON a~matnr EQ c~matnr
*        INNER JOIN marc AS d
*    ON a~matnr EQ d~matnr
*    WHERE a~matnr IN so_matnr
*      AND a~lvorm EQ space.
*  IF sy-subrc EQ 0.
*    DELETE tg_mara WHERE mtart NOT IN gr_mtart.   "Tipo de documento
*    DELETE tg_mara WHERE bstat NOT IN gr_bstat.   "Status
*    DELETE tg_mara WHERE werks NE c_bwkey.        "Centro
*    DELETE tg_mara WHERE mtorg NOT IN gr_mtorg.   "Origem do material
*  ENDIF.
*  LOOP AT tg_mara INTO eg_mara.
*    READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_mara-bwkey.
*    IF sy-subrc NE 0.
*      DELETE tg_mara.
*    ENDIF.
*  ENDLOOP.
*
*  IF tg_mara[] IS INITIAL.
*    "Pedido não possui material válido para simulação
*    MESSAGE s086(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ELSE.
*    PERFORM f_busca_pcb.
*    IF sy-uname EQ '51024988'.
*      PERFORM f_busca_pcb_2.
*    ENDIF.
*  ENDIF.
*
*ENDFORM.                    " F_SELECAO_MATERIAL
*&---------------------------------------------------------------------*
*&      Form  F_SELECAO_MAT_PRE_CAD
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_selecao_mat_pre_cad .
*
*  IF tg_precadmat[] IS NOT INITIAL.
*
*    tg_precadmat_aux[] = tg_precadmat[].
*    DELETE tg_precadmat WHERE mat_imp EQ space.
*    IF tg_precadmat[] IS NOT INITIAL.
*      "Buscar dados dos materiais
*      SELECT a~matnr
*             a~mtart
*             a~matkl
*             a~meins
*             a~bstat
*             b~maktx
*             c~bwkey
*             c~mtuse
*             c~mtorg
*             d~werks
*             d~steuc
*        INTO TABLE tg_mara
*        FROM mara AS a INNER JOIN makt AS b
*        ON a~matnr EQ b~matnr
*            INNER JOIN mbew AS c
*        ON a~matnr EQ c~matnr
*            INNER JOIN marc AS d
*        ON a~matnr EQ d~matnr
*        FOR ALL ENTRIES IN tg_precadmat
*        WHERE a~matnr EQ tg_precadmat-mat_imp
*          AND a~lvorm EQ space.
*      IF sy-subrc EQ 0.
*        DELETE tg_mara WHERE mtart NOT IN gr_mtart.  "Tipo de documento
*        DELETE tg_mara WHERE bstat NOT IN gr_bstat.  "Status
*        DELETE tg_mara WHERE werks NE c_bwkey.       "Centro
*        DELETE tg_mara WHERE mtorg NOT IN gr_mtorg.  "Origem do material
*      ENDIF.
*      tg_precadmat[] = tg_precadmat_aux[].
*
*      LOOP AT tg_mara INTO eg_mara.
*        READ TABLE tg_t001w INTO eg_t001w WITH KEY werks = eg_mara-bwkey.
*        IF sy-subrc NE 0.
*          DELETE tg_mara.
*        ENDIF.
*      ENDLOOP.
*
*      IF tg_mara[] IS INITIAL.
*        READ TABLE tg_precadmat INTO eg_precadmat WITH KEY mat_ref = space.  "há pré-cadastro sem material de referência
*        IF sy-subrc NE 0.
*          "Material de referência utilizado no pré cadastro é inválido
*          MESSAGE s084(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*          vg_erro = abap_true.
*        ENDIF.
*      ELSE.
*        rb_cad = abap_true.
*        PERFORM f_busca_pcb.
*        IF sy-uname EQ '51024988'.
*          PERFORM f_busca_pcb_2.
*        ENDIF.
*      ENDIF.
*    ENDIF.
*    tg_precadmat[] = tg_precadmat_aux[].
*
*    SELECT mwskz text1                                  "#EC CI_NOORDER
*      FROM t007s
*      INTO TABLE tg_t007s
*      FOR ALL ENTRIES IN tg_precadmat
*      WHERE spras = sy-langu
*        AND kalsm = 'TAXBRA'
*        AND mwskz = tg_precadmat-mwskz.
*
*  ELSE.
*    "Materiais pré-cadastrados não encontrados.
*    MESSAGE s081(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
*
*
*
*ENDFORM.                    " F_SELECAO_MAT_PRE_CAD
*&---------------------------------------------------------------------*
*&      Form  F_SELECAO_SIMULACAO
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_selecao_simulacao .
*  DATA: tl_simupreci TYPE TABLE OF ztsdd_simupreci,
*        tl_precadmat TYPE TABLE OF ztsdd_precadmat.
*
*  "Dados da simulação
*  SELECT *
*   INTO TABLE tg_simuprech
*   FROM ztsdd_simuprech
*   WHERE docsim EQ p_docsim.
*
*  IF tg_simuprech[] IS INITIAL.
*    "Documento de simulação não encontrado
*    MESSAGE s074(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ELSE.
*    "Valores da simulação SO TEM UM POR VEZ.
*    READ TABLE tg_simuprech INTO eg_simuprech INDEX 1.  "#EC CI_NOORDER
*    IF sy-subrc EQ 0.
*      SELECT *
*      INTO TABLE tg_simupreci
*      FROM ztsdd_simupreci
**    FOR ALL ENTRIES IN tg_simuprech
*      WHERE docsim EQ eg_simuprech-docsim.
*    ENDIF.
*    IF tg_simuprech[] IS NOT INITIAL.
*
*      READ TABLE tg_simuprech INTO eg_simuprech INDEX 1. "#EC CI_NOORDER
*
*      "Buscar dados dos materiais
*      IF eg_simuprech-selecao = 1 OR   "Processado por Pedido
*         eg_simuprech-selecao = 2.     "Processado por Material
*        tl_simupreci[] = tg_simupreci[].
*        SORT tl_simupreci BY matnr.
*        DELETE ADJACENT DUPLICATES FROM tl_simupreci COMPARING matnr.
*        IF NOT tl_simupreci[] IS INITIAL.
*          SELECT a~matnr
*                 a~mtart
*                 a~matkl
*                 a~meins
*                 a~bstat
*                 b~maktx
*                 c~bwkey
*                 c~mtuse
*                 c~mtorg
*                 d~werks
*                 d~steuc
*            INTO TABLE tg_mara
*            FROM mara AS a INNER JOIN makt AS b
*            ON a~matnr EQ b~matnr
*                INNER JOIN mbew AS c
*            ON a~matnr EQ c~matnr
*                INNER JOIN marc AS d
*            ON a~matnr EQ d~matnr
*            FOR ALL ENTRIES IN tl_simupreci
*            WHERE a~matnr EQ tl_simupreci-matnr.
*          IF sy-subrc EQ 0.
*            SORT tg_mara.
*          ENDIF.
*        ENDIF.
*      ELSEIF eg_simuprech-selecao = 3.    "Processado por Material pré-cadastrado
*        tl_simupreci[] = tg_simupreci[].
*        SORT tl_simupreci BY matnr.
*        DELETE ADJACENT DUPLICATES FROM tl_simupreci COMPARING matnr.
*        IF tl_simupreci[] IS NOT INITIAL.
*          SELECT *
*          INTO TABLE tg_precadmat
*          FROM ztsdd_precadmat
*            FOR ALL ENTRIES IN tl_simupreci
*          WHERE matnr EQ tl_simupreci-matnr.
*        ENDIF.
*
*        tl_precadmat[] = tg_precadmat[].
*        SORT tl_precadmat BY mat_imp.
*        DELETE ADJACENT DUPLICATES FROM tl_precadmat COMPARING mat_imp.
*        IF tl_precadmat[] IS NOT INITIAL.
*          SELECT a~matnr
*                 a~mtart
*                 a~matkl
*                 a~meins
*                 a~bstat
*                 b~maktx
*                 c~bwkey
*                 c~mtuse
*                 c~mtorg
*                 d~werks
*                 d~steuc
*            INTO TABLE tg_mara
*            FROM mara AS a INNER JOIN makt AS b
*            ON a~matnr EQ b~matnr
*                INNER JOIN mbew AS c
*            ON a~matnr EQ c~matnr
*                INNER JOIN marc AS d
*            ON a~matnr EQ d~matnr
*            FOR ALL ENTRIES IN tl_precadmat
*            WHERE a~matnr EQ tl_precadmat-mat_imp.
*        ENDIF.
*      ENDIF.
*
*      " Selecionar listas de preços
*      tl_simupreci[] = tg_simupreci[].
*      SORT tl_simupreci BY pltyp.
*      DELETE ADJACENT DUPLICATES FROM tl_simupreci COMPARING pltyp.
*      IF NOT tl_simupreci[] IS INITIAL.
*        SELECT a~vkorg
*               a~vtweg
*               a~pltyp
*               a~vlgwk
*               b~ptext
*          INTO TABLE tg_twkao
*          FROM twkao AS a INNER JOIN t189t AS b        "#EC CI_BUFFJOIN
*             ON a~pltyp EQ b~pltyp
*          FOR ALL ENTRIES IN tl_simupreci
*          WHERE a~vkorg EQ eg_simuprech-vkorg
*            AND a~vtweg EQ eg_simuprech-vtweg
*            AND a~pltyp EQ tl_simupreci-pltyp
*            AND a~vlgwk NE space
*            AND b~spras EQ sy-langu.
*        IF sy-subrc EQ 0.
*          SORT tg_twkao.
*        ENDIF.
*      ENDIF.
*      " Seleciona dados dos centros
*      IF tg_twkao[] IS NOT INITIAL.
*        SELECT werks regio
*          INTO TABLE tg_t001w
*          FROM t001w
*          FOR ALL ENTRIES IN tg_twkao
*          WHERE werks EQ tg_twkao-vlgwk.
*        IF sy-subrc NE 0.
*          FREE: tg_t001w.
*        ENDIF.
*        tl_simupreci[] = tg_simupreci[].
*        SORT tl_simupreci BY werks.
*        DELETE ADJACENT DUPLICATES FROM tl_simupreci COMPARING werks.
*
*        IF tl_simupreci[] IS NOT INITIAL.
*          SELECT werks regio
*            APPENDING TABLE tg_t001w
*            FROM t001w
*            FOR ALL ENTRIES IN tl_simupreci
*            WHERE werks EQ tl_simupreci-werks.
*        ENDIF.
*
*        SORT tg_t001w BY werks.
*        DELETE ADJACENT DUPLICATES FROM tg_t001w COMPARING werks.
*      ENDIF.
*    ENDIF.
*
*    IF eg_simuprech-status_d NE space.
*      "Documento de simulação já submetido à aprovação. Não pode ser alterado.
**      MESSAGE s096(zmsd_classe_mensagem) WITH eg_mara-matnr DISPLAY LIKE 'E'.
*      MESSAGE s096(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*      vg_edit = abap_false.
*    ENDIF.
*  ENDIF.
*
*ENDFORM.                    " F_SELECAO_SIMULACAO
*&---------------------------------------------------------------------*
*&      Form  F_BUSCA_PCB
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_busca_pcb .
*  DATA: vl_wrbtr TYPE rseg-wrbtr,
*        vl_menge TYPE rseg-menge,
*        vl_tabix TYPE sy-tabix,
*        vl_lines TYPE i,
*        vl_knumh TYPE a017-knumh,
*        vl_lifnr TYPE a017-lifnr.
*
*  REFRESH tg_pcb.
*  IF rb_cad NE space.       "Buscar PCB do Cadastro
*    LOOP AT tg_mara INTO eg_mara.
*
*      REFRESH tg_eina.
*      SELECT a~lifnr                               "#EC CI_SEL_NESTED -
*             a~matnr        "Como pega todos os Reg Infos de todos os materiais, se tirar do loop pode buscar muita coisa e dar dump.
*             b~werks
*             b~netpr
*             b~peinh
** Alteração - CD.3723 - 24.01.2020 - Inicio
*             a~ltsnr
** Alteração - CD.3723 - 24.01.2020 - Inicio
*        INTO TABLE tg_eina
*        FROM eina AS a INNER JOIN eine AS b
*          ON a~infnr = b~infnr
*        WHERE a~matnr EQ eg_mara-matnr
*          AND a~loekz EQ space
*          AND b~ekorg EQ c_lb01
*          AND b~werks IN so_werks
*          AND b~loekz EQ space.
*
*      IF sy-subrc EQ 0.
*        IF rb_mpc IS INITIAL.
*          LOOP AT tg_eina INTO eg_eina.                  "#EC CI_NESTED
*            eg_pcb-werks = eg_eina-werks.
*            eg_pcb-lifnr = eg_eina-lifnr.
*            eg_pcb-matnr = eg_mara-matnr.
*            eg_pcb-ltsnr = eg_eina-ltsnr.
** Ajuste Upgrade EHP8 - 28.12.18 - Início
** Não utilizar tabela A017 com JOIN
*
**            SELECT SINGLE b~kbetr b~kpein c~land1
**              INTO (eg_pcb-pcb, eg_pcb-kpein, eg_pcb-land1)
**              FROM a017 AS a INNER JOIN konp AS b
**                ON a~knumh = b~knumh
**               INNER JOIN lfa1 AS c
**                ON a~lifnr = c~lifnr
**              WHERE a~kschl EQ 'ZPB0'
**                AND a~lifnr EQ eg_eina-lifnr
**                AND a~matnr EQ eg_mara-matnr
**                AND a~werks EQ eg_eina-werks
**                AND a~ekorg EQ 'LB01'
**                AND a~datbi >= so_vkkab-low
**                AND a~datab <= so_vkkab-low.
*
*            SELECT knumh lifnr UP TO 1 ROWS             "#EC CI_NOORDER
*              FROM a017
*              INTO (vl_knumh, vl_lifnr)
*              WHERE kschl EQ 'ZPB0'
*                AND lifnr EQ eg_eina-lifnr
*                AND matnr EQ eg_mara-matnr
*                AND ekorg EQ 'LB01'
*                AND werks EQ eg_eina-werks
*                AND datbi >= so_vkkab-low
*                AND datab <= so_vkkab-low.
*            ENDSELECT.
*            IF sy-subrc EQ 0.
*
*              SELECT SINGLE land1
*                FROM lfa1
*                INTO eg_pcb-land1
*                WHERE lifnr EQ vl_lifnr.
*              IF sy-subrc NE 0.
*                CLEAR eg_pcb-land1.
*              ENDIF.
*
*              SELECT kbetr kpein UP TO 1 ROWS
*                FROM konp
*                INTO (eg_pcb-pcb, eg_pcb-kpein)
*                WHERE knumh EQ vl_knumh.
*              ENDSELECT.
*              IF sy-subrc NE 0.
*                CLEAR : eg_pcb-pcb, eg_pcb-kpein.
*              ENDIF.
*            ENDIF.
** Ajuste Upgrade EHP8 - 28.12.18 - Fim
*
**            eg_pcb-pcb = eg_pcb-pcb / eg_eina-peinh.
*            eg_pcb-pcb = eg_pcb-pcb / eg_pcb-kpein.
*            APPEND eg_pcb TO tg_pcb.
*          ENDLOOP.
*        ENDIF.
*      ELSE.
*        "Registro info não encontrado para o material &
*        MESSAGE s082(zmsd_classe_mensagem) WITH eg_mara-matnr DISPLAY LIKE 'E'.
*        vg_erro = abap_true.
**        EXIT.
*      ENDIF.
*    ENDLOOP.
*
*  ELSEIF rb_upo NE space.   "Buscar PCB do último pedido
*    LOOP AT tg_mara INTO eg_mara.
*      vl_tabix = sy-tabix.
*      CLEAR: vl_wrbtr, vl_menge.
*      REFRESH: tg_ekpo, tg_rseg.
*
*      SELECT a~lifnr                               "#EC CI_SEL_NESTED -
*             b~ebeln    "Como pega todos os pedidos de todos os materiais, se tirar do loop pode buscar muita coisa e dar dump.
*             b~ebelp
*             b~matnr
*             b~werks
*             b~bpumz
*             b~bpumn
*             b~umrez      "<002> - Inclusão
*             b~umren      "<002> - Inclusão
*             b~ltsnr
*        INTO TABLE tg_ekpo
*        FROM ekko AS a INNER JOIN ekpo AS b
*        ON a~ebeln = b~ebeln
*        WHERE a~bsart EQ 'ZIMP'
*          AND a~loekz EQ space
*          AND b~matnr EQ eg_mara-matnr
*          AND b~loekz EQ space
*          AND b~werks IN so_werks
*          AND b~elikz EQ abap_true.
*      IF sy-subrc EQ 0.
*        "Manter apenas último pedido
*        SORT tg_ekpo BY werks ebeln DESCENDING.        "#EC CI_SORTLOOP
*      ENDIF.
*      LOOP AT tg_ekpo INTO eg_ekpo.                      "#EC CI_NESTED
*        DELETE tg_ekpo WHERE ebeln NE eg_ekpo-ebeln
*                         AND werks EQ eg_ekpo-werks.
*
*      ENDLOOP.
** Alteração - CD.3723 - 21.02.2020 - Inicio
*      IF NOT vg_cd_unico IS INITIAL.
*        READ TABLE tg_ekpo WITH KEY werks = vg_cd_unico TRANSPORTING NO FIELDS.
*        IF sy-subrc EQ 0.
*          DELETE tg_ekpo WHERE werks <> vg_cd_unico.
*        ENDIF.
*      ENDIF.
*      DESCRIBE TABLE tg_ekpo LINES vl_lines.
*      IF vl_lines > 1.
*        SORT tg_ekpo BY ebeln DESCENDING.              "#EC CI_SORTLOOP
*        READ TABLE tg_ekpo INDEX 1 INTO eg_ekpo.
*        DELETE tg_ekpo WHERE ebeln <> eg_ekpo-ebeln.
*      ENDIF.
** Alteração - CD.3723 - 21.02.2020 - Inicio
*
*      IF tg_ekpo[] IS NOT INITIAL.
*        SELECT b~belnr           "#EC CI_SEL_NESTED - "<002> - Inclusão
*               b~gjahr      " A seleção do pedido foi feita dentro do loop nao tem como tirar aqui. "<002> - Inclusão
*               b~buzei       "<002> - Inclusão
*               b~matnr
*               b~werks
*               b~wrbtr
*               b~menge
** Alteração - CC.1789 - Luiz - 12.06.2018  - Inicio
*               b~tbtkz
*               b~bnkan
** Alteração - CC.1789 - Luiz - 12.06.2018  - FIM
*               b~ebeln  """
*               b~ebelp  """
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Início da Inclusão
*               b~bstme
*               b~meins
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Fim da Inclusão
*          INTO TABLE tg_rseg
*          FROM rbkp AS a INNER JOIN rseg AS b
*            ON a~belnr = b~belnr AND
*               a~gjahr = b~gjahr
*          FOR ALL ENTRIES IN tg_ekpo
*          WHERE a~stblg EQ space
*            AND b~ebeln EQ tg_ekpo-ebeln
*            AND b~ebelp EQ tg_ekpo-ebelp.
*        IF sy-subrc NE 0.
*          FREE: tg_rseg.
*        ENDIF.
*        IF tg_rseg[] IS NOT INITIAL.
*          LOOP AT tg_ekpo INTO eg_ekpo.                  "#EC CI_NESTED
*
**           >>> <CC.2252> - Início da Inclusão - IROSA 21.09.2018
**           Verifica se há Código: ajuste posterior (TBTKZ = X) para separar as regras
*            READ TABLE tg_rseg TRANSPORTING NO FIELDS
*              WITH KEY werks = eg_ekpo-werks
*                       matnr = eg_ekpo-matnr
*                       tbtkz = abap_true.
*            IF sy-subrc IS INITIAL.
**           <<< <CC.2252> - Final da Inclusão - IROSA 21.09.2018
*
*              LOOP AT tg_rseg INTO eg_rseg WHERE werks EQ eg_ekpo-werks
*                                             AND matnr EQ eg_ekpo-matnr. "#EC CI_NESTED
**   Alteração - CC.1789 - Luiz - 12.06.2018  - Inicio
*                IF eg_rseg-tbtkz = abap_true.
*                  vl_wrbtr = vl_wrbtr + eg_rseg-bnkan.
*                ELSE.
*                  vl_wrbtr = vl_wrbtr + eg_rseg-wrbtr.
*                  vl_menge = vl_menge + eg_rseg-menge. "Inclusão - IROSA 21.09.2018
*                ENDIF.
**   Alteração - CC.1789 - Luiz - 12.06.2018 - fim
*
**                vl_menge = vl_menge + eg_rseg-menge. "Exclusão CC.1789 IROSA 29.06.2018
*              ENDLOOP.
*
**           >>> <CC.2252> - Início da Inclusão - IROSA 21.09.2018
*              IF vl_menge IS INITIAL.
*                vl_menge = eg_rseg-menge.
*              ENDIF.
*
*            ELSE.
*
*              LOOP AT tg_rseg INTO eg_rseg WHERE werks EQ eg_ekpo-werks
*                                             AND matnr EQ eg_ekpo-matnr. "#EC CI_NESTED
*
*                vl_wrbtr = vl_wrbtr + eg_rseg-wrbtr.
*
**                 Considera a quantidade apenas se o WRBTR tiver valor.
*                IF NOT eg_rseg-wrbtr IS INITIAL.
*                  vl_menge = vl_menge + eg_rseg-menge.
*                ENDIF.
*
*              ENDLOOP.
*
*            ENDIF.
**           <<< <CC.2252> - Final da Inclusão - IROSA 21.09.2018
*
**            vl_menge = eg_rseg-menge. "<CC.2252> - Exclusão - IROSA 21.09.2018
*            eg_pcb-werks = eg_ekpo-werks.
*            eg_pcb-lifnr = eg_ekpo-lifnr.
*            eg_pcb-ltsnr = eg_ekpo-ltsnr.
*            eg_pcb-matnr = eg_mara-matnr.
**<002> - Início - Substituir campos EKPO-BPUMZ e EKPO-BPUMNS pelos campos EKPO-UMREN e EKPO-UMREZ
**>>> Commented
****            eg_pcb-pcb = ( vl_wrbtr / vl_menge ) / ( eg_ekpo-bpumz / eg_ekpo-bpumn ).
**<<< Commented
*            eg_pcb-pcb = ( vl_wrbtr / vl_menge ) / ( eg_ekpo-umrez / eg_ekpo-umren ).
**<002> - Fim - Substituir campos EKPO-BPUMZ e EKPO-BPUMNS pelos campos EKPO-UMREN e EKPO-UMREZ
*            SELECT SINGLE land1
*              FROM lfa1
*              INTO eg_pcb-land1
*              WHERE lifnr EQ eg_pcb-lifnr.
*            IF sy-subrc NE 0.
*              CLEAR eg_pcb-land1.
*            ENDIF.
*
*            eg_pcb-ebeln = eg_ekpo-ebeln.     "<002> - Inclusão do número do pedido
*            eg_pcb-menge = vl_menge.
*            APPEND eg_pcb TO tg_pcb.
*          ENDLOOP.
*        ELSE.
** <002> - Início - Caso material não tenha nenhuma entrada, ignorá-lo e manter o processamento
** >>> Commented
***          "Fatura não encontrada para o material &
***          MESSAGE s105(zmsd_classe_mensagem) WITH eg_mara-matnr DISPLAY LIKE 'E'.
***          vg_erro = abap_true.
***          EXIT.
** <<< Commented
*          DELETE tg_mara INDEX vl_tabix.
*          CONTINUE.
** <002> - Fim - Caso material não tenha nenhuma entrada, ignorá-lo e manter o processamento
*        ENDIF.
*      ELSE.
** <002> - Início - Caso material não tenha nenhuma entrada, ignorá-lo e manter o processamento
** >>> Commented
****        "Pedido não encontrado para o material &
****        MESSAGE s104(zmsd_classe_mensagem) WITH eg_mara-matnr DISPLAY LIKE 'E'.
****        vg_erro = abap_true.
** <<< Commented
** <002> - Fim - Caso material não tenha nenhuma entrada, ignorá-lo e manter o processamento
*        DELETE tg_mara INDEX vl_tabix.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
*
** <002> - Início - Verificar se ainda há materiais a serem processados
*  IF tg_mara[] IS INITIAL.
*    "Não há dados para processamento
*    MESSAGE s107(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
*    vg_erro = abap_true.
*  ENDIF.
** <002> - Fim - Verificar se ainda há materiais a serem processados
*
*ENDFORM.                    " F_BUSCA_PCB

*&---------------------------------------------------------------------*
*&      Form  F_BUSCA_PCB_2

*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_PVFINAL
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_seleciona_pvfinal .
  DATA: vl_kbetr TYPE konp-kbetr.
  CONSTANTS: c_valor TYPE p DECIMALS 2 VALUE '0.01'.

  IF tg_mara[] IS NOT INITIAL.
    "Buscar preço de venda final
    SELECT b~kbetr UP TO 1 ROWS
      INTO vl_kbetr
      FROM a155 AS a INNER JOIN konp AS b
        ON ( a~knumh = b~knumh
            AND a~kschl = b~kschl )
        WHERE a~kappl = 'V'
          AND a~kschl = 'VKP0'
          AND a~vkorg = eg_twkao-vkorg
          AND a~vtweg = eg_twkao-vtweg
          AND a~pltyp = eg_twkao-pltyp
          AND a~matnr = eg_mara-matnr
          AND a~vrkme = eg_mara-meins
          AND a~datbi >= so_vkkab-low
          AND a~datab <= so_vkkab-low
          AND b~kschl = 'VKP0'
      ORDER BY a~knumh.  " <LMB_S4_BM>
    ENDSELECT.
    IF sy-subrc EQ 0.
      "Converter para preço psicológico
      CALL FUNCTION 'PRICE_POINT_READ'
        EXPORTING
          pi_vkorg                   = 'LB01'
          pi_vtweg                   = '10'
          pi_rktyp                   = 'A'
* Alteração - PR.8231 - 02.05.2022  - Inicio
*         pi_eprgr                   = 'ZLMB01'
          pi_eprgr                   = 'ZLMB07'
* Alteração - PR.8231 - 02.05.2022  - FIM
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
*      eg_saida-pv_fin = '0.01'.
      eg_saida-pv_fin = c_valor.
    ENDIF.
  ELSE.
*    eg_saida-pv_fin = '0.01'.
    eg_saida-pv_fin = c_valor.
  ENDIF.

ENDFORM.                    " F_SELECIONA_PVFINAL
*&---------------------------------------------------------------------*
*&      Form  F_DESC_STATUS
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_salvar_dados .
  DATA: vl_answer,
        vl_question(100),
        vl_objkey        TYPE swo_typeid,
        vl_retcode       TYPE sy-subrc,
        tl_simupreci     TYPE TABLE OF ztsdd_simupreci.

  IF vg_edit IS INITIAL.
    "Documento de simulação já submetido à aprovação. Não pode ser alterado.
*    MESSAGE s096(zmsd_classe_mensagem) WITH eg_mara-matnr DISPLAY LIKE 'E'.
    MESSAGE s096(zmsd_classe_mensagem) DISPLAY LIKE 'E'.
    EXIT.
  ENDIF.

* Salvar simulação?
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

* Dados de Cabeçalho
    IF rb_sim NE space. "Buscar dados de cabeçalho utilizados na criação do documento de simulação
      READ TABLE tg_simuprech INTO eg_simuprech WITH KEY docsim = p_docsim.
    ELSE.  "Novo documento de simulação
      eg_simuprech-docsim = p_docsim.
      eg_simuprech-vkorg = p_vkorg.
      eg_simuprech-vtweg = p_vtweg.
      READ TABLE so_vkkab INDEX 1.
      eg_simuprech-vkkab = so_vkkab-low.
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

    "Atualizar último modificador
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
* Alteração - CD.3723 - 24.01.2020 - Inicio
      eg_simupreci-var_cust_log         = eg_saida-var_cust_log.
* Alteração - CD.3723 - 24.01.2020 - Inicio
      eg_simupreci-uf_precad            = eg_saida-uf_precad.
      eg_simupreci-fob                  = eg_saida-fob.
      eg_simupreci-despachante          = eg_saida-despachante.
      eg_simupreci-tx_fob               = eg_saida-tx_fob.
      eg_simupreci-tx_despachante       = eg_saida-tx_desp.
      eg_simupreci-gestao               = eg_saida-gestao.
      eg_simupreci-fin                  = eg_saida-fin.
**      eg_simupreci-ebeln                = eg_saida-ebeln.   "<002> - Inclusão - Descomentar quando simulador nacional estiver em PRD
      APPEND eg_simupreci TO tl_simupreci.
      CLEAR eg_simupreci.
    ENDLOOP.
    IF NOT tl_simupreci[] IS INITIAL.
      MODIFY ztsdd_simupreci FROM TABLE tl_simupreci.
      IF sy-subrc EQ 0.
        COMMIT WORK.
      ENDIF.
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
      "submeter à aprovação
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
        UPDATE ztsdd_simuprech SET status_d = 10  "Em aprovação
                               WHERE docsim EQ p_docsim.
        IF sy-subrc EQ 0.
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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_seleciona_material_centro.
  DATA: tl_fieldcat TYPE slis_t_fieldcat_alv WITH HEADER LINE.
*        tl_fields   TYPE TABLE OF sval WITH HEADER LINE.

* Montar fieldcat para popup
  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'CHECK'.
  tl_fieldcat-seltext_m = space.
  tl_fieldcat-outputlen = 1.
  tl_fieldcat-checkbox = 'X'.
  tl_fieldcat-input = 'X'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'MATNR'.
  tl_fieldcat-seltext_m = 'Material'.
  tl_fieldcat-outputlen = 20.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'WERKS'.
  tl_fieldcat-seltext_m = 'Centro'.
  tl_fieldcat-outputlen = 4.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname = 'TG_MAT_POP'.
  tl_fieldcat-fieldname = 'MAKTX'.
  tl_fieldcat-seltext_m = 'Descrição'.
  tl_fieldcat-outputlen = 60.
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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_exibe_impostos.

  DATA: tl_fieldcat TYPE slis_t_fieldcat_alv WITH HEADER LINE.
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

*      tl_fieldcat-tabname = 'TG_IMPOSTOS'.
*      tl_fieldcat-fieldname = 'PTEXT'.
*      tl_fieldcat-seltext_m = text-t24.
*      tl_fieldcat-just = 'C'.
*      APPEND tl_fieldcat.
*      CLEAR tl_fieldcat.

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
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_exibe_c_log tables tl_data type STANDARD TABLE.

  data: tl_konw type TABLE OF konw.
  DATA: tl_fieldcat TYPE slis_t_fieldcat_alv WITH HEADER LINE.
* Alteração - PRIC-2507 - 17.04.2025  - Inicio
  tl_konw[] = tl_data[].
* Montar fieldcat para popup
  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'MANDT'.
  tl_fieldcat-no_out = 'X'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KNUMH'.
  tl_fieldcat-seltext_m = TEXT-020.
  tl_fieldcat-no_out = 'X'.
  tl_fieldcat-just = 'C'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KOPOS'.
  tl_fieldcat-seltext_m = TEXT-021.
  tl_fieldcat-no_out = 'X'.
  tl_fieldcat-just = 'C'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KLFN1'.
  tl_fieldcat-no_out = 'X'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KSTBW'.
  tl_fieldcat-seltext_m = TEXT-022.
  tl_fieldcat-just = 'C'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

  tl_fieldcat-tabname =  'TL_KONW'.
  tl_fieldcat-fieldname = 'KBETR'.
  tl_fieldcat-ref_fieldname =  'KONW'.
  tl_fieldcat-ref_tabname  = 'KBETR'.
  tl_fieldcat-seltext_m = TEXT-023.
  tl_fieldcat-just = 'C'.
  APPEND tl_fieldcat.
  CLEAR tl_fieldcat.

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


*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'MATNR'.
*  tl_fieldcat-seltext_m = TEXT-t03.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'WERKS'.
*  tl_fieldcat-seltext_m = TEXT-t21.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'PCL'.
*  tl_fieldcat-seltext_m = TEXT-t11.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'DIAS_EST'.
*  tl_fieldcat-seltext_m = TEXT-t64.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'UMREZ'.
*  tl_fieldcat-seltext_m = TEXT-t57.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'HOEHE'.
*  tl_fieldcat-seltext_m = TEXT-t58.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'BREIT'.
*  tl_fieldcat-seltext_m = TEXT-t59.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'LAENG'.
*  tl_fieldcat-seltext_m = TEXT-t60.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'TX_MOV'.
*  tl_fieldcat-seltext_m = TEXT-t61.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'C_MVTO'.
*  tl_fieldcat-seltext_m = TEXT-t51.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'C_PALLET'.
*  tl_fieldcat-seltext_m = TEXT-t52.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'CUSTO_INS_PALLET'.
*  tl_fieldcat-seltext_m = TEXT-t72.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'TX_FRETE'.
*  tl_fieldcat-seltext_m = TEXT-t62.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'FRETE'.
*  tl_fieldcat-seltext_m = TEXT-t53.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'TX_FIN'.
*  tl_fieldcat-seltext_m = TEXT-t54.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'FIN'.
*  tl_fieldcat-seltext_m = TEXT-t79.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'TX_GEST'.
*  tl_fieldcat-seltext_m = TEXT-t55.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'GESTAO'.
*  tl_fieldcat-seltext_m = TEXT-t73.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'C_ARM'.
*  tl_fieldcat-seltext_m = TEXT-t56.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'CUSTO_ARMAZEN'.
*  tl_fieldcat-seltext_m = TEXT-t78.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'TX_FOB'.
*  tl_fieldcat-seltext_m = TEXT-t74.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'FOB'.
*  tl_fieldcat-seltext_m = TEXT-t75.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'TX_DESP'.
*  tl_fieldcat-seltext_m = TEXT-t76.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  tl_fieldcat-tabname =  'TG_VAL_C_LOG'.
*  tl_fieldcat-fieldname = 'DESPACHANTE'.
*  tl_fieldcat-seltext_m = TEXT-t77.
*  tl_fieldcat-just = 'C'.
*  APPEND tl_fieldcat.
*  CLEAR tl_fieldcat.
*
*  CALL FUNCTION 'REUSE_ALV_POPUP_TO_SELECT'
*    EXPORTING
*      i_title               = 'Valores para cálculo Custo Logístico'
*      i_selection           = 'X'
*      i_zebra               = abap_true
*      i_screen_start_column = 15
*      i_screen_start_line   = 5
*      i_screen_end_column   = 150
*      i_screen_end_line     = 20
*      i_tabname             = 'TG_VAL_C_LOG'
*      it_fieldcat           = tl_fieldcat[]
*    TABLES
*      t_outtab              = tg_val_c_log
*    EXCEPTIONS
*      program_error         = 1
*      OTHERS                = 2.

* Alteração - PRIC-2507 - 17.04.2025  - FIM.
ENDFORM.                    " F_EXIBE_C_LOG
*&---------------------------------------------------------------------*
*&      Form  F_SELECIONA_RAPPEL
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_seleciona_rappel .
  DATA: vl_kbetr TYPE konp-kbetr.

  IF tg_mara[] IS NOT INITIAL.
    "Buscar rappel
    SELECT b~kbetr UP TO 1 ROWS
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
    ENDSELECT.
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
*  -->  p1        text
*  <--  p2        text
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
* Selecionar lista de preços
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
*        color_cell      TYPE lvc_t_scol,      "Cell color

    APPEND eg_saida_rel TO tg_saida_rel.
  ENDLOOP.

ENDFORM.                    " F_SELECIONA_DADOS_REL
*&---------------------------------------------------------------------*
*&      Form  FILL_CELLTAB
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*      <--P_PT_CELLTAB  text
*----------------------------------------------------------------------*
FORM fill_celltab CHANGING pt_celltab TYPE lvc_t_styl.
  DATA: ls_celltab TYPE lvc_s_styl,
        l_mode     TYPE raw4.
*  CLEAR eg_node.
  FREE: pt_celltab.
* Alteração - CC.3526 - 18.09.2019 10:27:12 - Inicio
**  if eg_saida-pv_fin > '0.01'.
**  read table tg_node into eg_node with key matnr = eg_saida-matnr
**                                  BINARY SEARCH.
**  read table tg_revionics with key secao = eg_node-node(2) BINARY SEARCH TRANSPORTING NO FIELDS.
**  if sy-subrc eq 0.
**    l_mode = cl_gui_alv_grid=>mc_style_disabled.
**  else.
**    l_mode = cl_gui_alv_grid=>mc_style_enabled.
**  endif.
**  else.
* Alteração - CC.3526 - 18.09.2019 10:27:12 - fim;
  l_mode = cl_gui_alv_grid=>mc_style_enabled.
*  endif.
  ls_celltab-fieldname = 'PV_FIN'.
  ls_celltab-style = l_mode.
  INSERT ls_celltab INTO TABLE pt_celltab.

ENDFORM.                               " FILL_CELLTAB
*&---------------------------------------------------------------------*
*&      Form  F_BUSCA_CDUNICO
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
*FORM f_busca_cdunico .
*  TYPES: BEGIN OF ty_werks,
*           werks TYPE t001w-werks,
*           regio TYPE t001w-regio,
*           fabkl TYPE t001w-fabkl,
*         END OF ty_werks.
*
*  DATA: tl_t001w TYPE TABLE OF ty_werks,
*        el_t001w TYPE ty_werks.
*
*  CLEAR: vg_cd_unico.
** Logica inicial para seleção de 1 unico Centro na tela de seleção (A ser definido ainda).
*  SELECT werks regio fabkl
*    INTO TABLE tl_t001w
*    FROM t001w
*   WHERE vlfkz = 'B'. "APenas Centros de Distribuicao.
*
*  IF sy-subrc EQ 0.
*
*    DELETE tl_t001w WHERE fabkl <> 'ZL'.
*    SORT tl_t001w BY werks.
*    READ TABLE tl_t001w INTO el_t001w WITH KEY werks = so_werks-low BINARY SEARCH.
*    IF sy-subrc EQ 0.
*      DELETE tl_t001w WHERE regio <> el_t001w-regio.
*      DELETE tl_t001w WHERE werks = el_t001w-werks.
*    ENDIF.
*    LOOP AT tl_t001w INTO el_t001w.
*      IF sy-tabix = 1.
*        vg_cd_unico = so_werks-low.
*      ENDIF.
*      so_werks-sign = 'I'.
*      so_werks-option = 'EQ'.
*      so_werks-low = el_t001w-werks.
*      APPEND so_werks.
*    ENDLOOP.
*  ENDIF.
*
*ENDFORM.
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

  p_so_matnr[] = so_matnr[].
  p_so_ebeln[] = so_ebeln[].
  p_so_mati[]  = so_mati[].
  p_so_werks[] = so_werks[].
  p_so_pltyp[] = so_pltyp[].
  p_so_vkkab[] = so_vkkab[].

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
*  -->  p1        text
*  <--  p2        text
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
      "Selecionar valor de venda na tabela 155 para o PLTYP em questao.
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
  SELECT b~kbetr UP TO 1 ROWS  "#EC CI_SEL_NESTED
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
    ORDER BY a~knumh.  " <LMB_S4_BM>
  ENDSELECT.
  IF sy-subrc EQ 0.
    "Converter para preço psicológico
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
*      eg_saida-pv_fin = '0.01'.
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