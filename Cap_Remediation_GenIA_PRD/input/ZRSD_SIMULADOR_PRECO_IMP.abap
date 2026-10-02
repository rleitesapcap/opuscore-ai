REPORT zrsd_simulador_preco_imp NO STANDARD PAGE HEADING.
***********************************************************************
*                                                                     *
*      *********************************************************      *
*      *                +---------------------+                *      *
*      *                | VBR Soluções em TI  |                *      *
*      *                +---------------------+                *      *
*      *********************************************************      *
*                                                                     *
***********************************************************************
*---------------------------------------------------------------------*
*** Dados do programa                                                 *
*---------------------------------------------------------------------*
* Nome  : ZRSD_SIMULADOR_PRECO_IMP                                    *
* Título: Simulador de Preço Importado                                *
* Autor : Anderson Tessitori                                          *
* Data  : 23.03.2017                                                  *
*                                                                     *
* Objetivos: Simular os preços para materiais importados              *
*                                                                     *
* Espec.Técnica(ET): 3D1_ET_REA_SC_SD_CC.0402 - Simulador preço       *
*                    importado                                        *
*---------------------------------------------------------------------+
*** Histórico das modificações                                        |
*---+--------+----------------+---------------------------------------+
*Seq|Data    |Autor           |COD/ Descrição da modificação ou erro  |
*---+--------+----------------+---------------------------------------+
*001|23.03.17|Anderson Tessitori |Codificação inicial                 |
*---+--------+----------------+---------------------------------------+
*002|07.02.18|Anderson Tessitori |CC.1547 - Ajustes seleção por pedido|
*---+--------+----------------+---------------------------------------+
*003|01.06.20|Luiz Otavio     |CC.4316 - Automacao. Transformação de  |
* chamadas do monitor de importado como função para tratamento em mais|
* de um programa. Nao foi feita melhoria. Apenas chamada para funcao  |
*---+--------+----------------+---------------------------------------+
*004|02.09.22|Luiz Otavio     |PR.08863 - Tratamento para Multiplas   |
* listas de preco para o mesmo refsite                                |
*---+--------+----------------+---------------------------------------+
*005|12.07.22|Luiz Otavio     |PR.09951 - Tratamento para campo werks |
* impedir preenchimento errado                                        |
*---+--------+----------------+---------------------------------------+
*006|06.08.24|Luiz Otavio     |PR.02460 ajuste para busca de preco    +
* por cadastro (PRIC-1712)                                            +
*---+--------+----------------+---------------------------------------+
*007|17.04.25|Luiz Otavio     |PRIC-2507 - Alteração no processo de   +
* fluxo logistico                                                     +
*---------------------------------------------------------------------*
* Declaração: Include(s)
*---------------------------------------------------------------------*
INCLUDE zrsd_simulador_preco_imp_top. " Declarações
INCLUDE zrsd_simulador_preco_imp_f01. " Rotinas auxiliares
INCLUDE zrsd_simulador_preco_imp_pbo. " Rotinas antes da exibição
INCLUDE zrsd_simulador_preco_imp_pai. " Rotinas após ação

INCLUDE <icon>.
* Alteração - PR.09951 - 12.07.2023 - Inicio
AT SELECTION-SCREEN ON so_werks.
  PERFORM f_valida_centro.
* Alteração - PR.09951 - 12.07.2023 - FIM
*&---------------------------------------------------------------------*
*& AT SELECTION-SCREEN OUTPUT
*&---------------------------------------------------------------------*
AT SELECTION-SCREEN OUTPUT.
* Se a seleção for por pedido, habilitar campo de nº de pedido
* e o critério adicional PCB do CE
  IF rb_ped NE space.
    LOOP AT SCREEN.
      IF screen-group1 = ped OR
         screen-group1 = all OR
         screen-group1 = pcb.
        screen-active = '1'.
        MODIFY SCREEN.
      ELSEIF screen-group1 NE space.
        screen-active = '0'.
        MODIFY SCREEN.
      ENDIF.
    ENDLOOP.
  ENDIF.

* Se a seleção for por material, habilitar campos de nº de material,
* e o critério adicional PCB do CE
  IF rb_mat NE space.
    LOOP AT SCREEN.
      IF screen-group1 = mat OR
         screen-group1 = all OR
         screen-group1 = pcb.
        screen-active = '1'.
        MODIFY SCREEN.
      ELSEIF screen-group1 NE space.
        screen-active = '0'.
        MODIFY SCREEN.
      ENDIF.
    ENDLOOP.
  ENDIF.

* Se a seleção for por material pré-cadastrado, habilitar campos de nº de material pré-cadastrado
* O critério adicional será obrigatoriamente o PCB do cadastro, pois não há essa informação no CE
  IF rb_mpc NE space.
    LOOP AT SCREEN.
      IF screen-group1 = mpc OR
         screen-group1 = all.
        screen-active = '1'.
        MODIFY SCREEN.
      ELSEIF screen-group1 NE space.
        screen-active = '0'.
        MODIFY SCREEN.
      ENDIF.
    ENDLOOP.
  ENDIF.

* Se a seleção for por simulação, habilitar apenas o campo de nº de simulação
  IF rb_sim NE space.
    LOOP AT SCREEN.
      IF screen-group1 = sim.
        screen-active = '1'.
        MODIFY SCREEN.
      ELSEIF screen-group1 NE space.
        screen-active = '0'.
        MODIFY SCREEN.
      ENDIF.
    ENDLOOP.
  ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
* Se a seleção for por Relatorio de precificação, habilitar somente Simulacao e Material.
  IF rb_aut NE space.
    LOOP AT SCREEN.
      IF screen-group1 = sim OR
         screen-group1 = mat.
        screen-active = '1'.
        MODIFY SCREEN.
      ELSEIF screen-group1 NE space.
        screen-active = '0'.
        MODIFY SCREEN.
      ENDIF.
    ENDLOOP.
  ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM

*>>> <CC.2252> - Início da Inclusão - IROSA 19.09.2018

* Pega os usuários habilitados cadastrados via transação ZXX_PAR2
  get_hard 'SD_0402_01_USUARIO_PCB' 'UNAME' gr_uname.
* Alteração - PR.02460 - 23.08.2024- Inicio
  SELECT zuserlb1 UP TO 1 ROWS
    INTO @DATA(vl_zuserlb1)
    FROM ztmmc_stat_preco.
  ENDSELECT.
  IF sy-subrc EQ 0.
    CLEAR er_uname.
    er_uname-sign = 'I'.
    er_uname-option = 'EQ'.
    er_uname-low = vl_zuserlb1.
    APPEND er_uname TO gr_uname.
  ENDIF.
* Alteração - PR.02460 - 23.08.2024- Inicio

  IF sy-uname NOT IN gr_uname.
    LOOP AT SCREEN.
      IF screen-group1 EQ pcb.
        screen-input = '0'.
        MODIFY SCREEN.
      ENDIF.
    ENDLOOP.
  ENDIF.


*<<< <CC.2252> - Fim da Inclusão - IROSA 19.09.2018
*---------------------------------------------------------------------*
*       CLASS lcl_event_handler IMPLEMENTATION
*---------------------------------------------------------------------*
CLASS lcl_event_handler IMPLEMENTATION.

  METHOD handle_toolbar.

    CONSTANTS: cl_bt_set     TYPE ui_func VALUE 'BT_SET',
               cl_bt_set_pcb TYPE ui_func VALUE 'BT_SET_PCB',
               cl_bt_comp    TYPE ui_func VALUE 'BT_COMP',
               cl_bt_c_log   TYPE ui_func VALUE 'BT_C_LOG',
               cl_bt_rappel  TYPE ui_func VALUE 'BT_RAPPEL',
               cl_bt_transf  TYPE ui_func VALUE 'BT_TRANSF',
               cl_bt_venda   TYPE ui_func VALUE 'BT_VENDA',
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
               cl_bt_rep     TYPE ui_func VALUE 'BT_REP'.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim.

    DATA el_toolbar  TYPE stb_button.

*- Adicionar um separador no menu do ALV.
    CLEAR el_toolbar.
    el_toolbar-butn_type = 3.
    APPEND el_toolbar TO e_object->mt_toolbar.
*
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
    IF rb_aut = abap_false.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim

*- Adicionar botões:
      IF vg_edit IS NOT INITIAL.
* Alteração - CC.2279 - Luiz - 26.10.2018 15:47:13 - Inicio
*        CLEAR el_toolbar.
*        el_toolbar-function = cl_bt_set_pcb.
*        el_toolbar-quickinfo = text-009.
*        el_toolbar-text = text-009.
*        el_toolbar-disabled = ''.
*        APPEND el_toolbar TO e_object->mt_toolbar.
* Alteração - CC.2279 - Luiz - 26.10.2018 15:47:13 - fim

* Alteração - CC.2373 - Fabiano Bartholomeu - 26.10.2018 - Inicio
        IF  rb_mpc IS NOT INITIAL.
          CLEAR el_toolbar.
          el_toolbar-function = cl_bt_set_pcb.
          el_toolbar-quickinfo = TEXT-009.
          el_toolbar-text = TEXT-009.
          el_toolbar-disabled = ''.
          APPEND el_toolbar TO e_object->mt_toolbar.
        ENDIF.
* Alteração - CC.2373 - Fabiano Bartholomeu - 12.12.2018 - Fim

        CLEAR el_toolbar.
        el_toolbar-function = cl_bt_rappel.
        el_toolbar-quickinfo = TEXT-012.
        el_toolbar-text = TEXT-012.
        el_toolbar-disabled = ''.
        APPEND el_toolbar TO e_object->mt_toolbar.

        CLEAR el_toolbar.
        el_toolbar-function = cl_bt_set.
        el_toolbar-quickinfo = TEXT-008.
        el_toolbar-text = TEXT-008.
        el_toolbar-disabled = ''.
        APPEND el_toolbar TO e_object->mt_toolbar.
      ENDIF.

      CLEAR el_toolbar.
      el_toolbar-function = cl_bt_c_log.
      el_toolbar-quickinfo = TEXT-011.
      el_toolbar-text = TEXT-011.
      el_toolbar-disabled = ''.
      APPEND el_toolbar TO e_object->mt_toolbar.

      CLEAR el_toolbar.
      el_toolbar-function = cl_bt_comp.
      el_toolbar-quickinfo = TEXT-010.
      el_toolbar-text = TEXT-010.
      el_toolbar-disabled = ''.
      APPEND el_toolbar TO e_object->mt_toolbar.

      CLEAR el_toolbar.
      el_toolbar-function = cl_bt_transf.
      el_toolbar-quickinfo = TEXT-013.
      el_toolbar-text = TEXT-013.
      el_toolbar-disabled = ''.
      APPEND el_toolbar TO e_object->mt_toolbar.

      CLEAR el_toolbar.
      el_toolbar-function = cl_bt_venda.
      el_toolbar-quickinfo = TEXT-014.
      el_toolbar-text = TEXT-014.
      el_toolbar-disabled = ''.
      APPEND el_toolbar TO e_object->mt_toolbar.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
    ELSE.
      CLEAR el_toolbar.
      el_toolbar-function = cl_bt_rep.
      el_toolbar-quickinfo = TEXT-015.
      el_toolbar-text = TEXT-015.
      el_toolbar-disabled = ''.
      APPEND el_toolbar TO e_object->mt_toolbar.
    ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
  ENDMETHOD.

*  METHOD handle_hotspot.
*
**    IF e_column_id-fieldname = 'VBELN'.
**
**      READ TABLE tg_saida_h INTO eg_saida_h INDEX e_row_id-index.
**      PERFORM f_seleciona_itens USING eg_saida_h-vbeln.
**      vg_grid = 2.
**      CALL METHOD vg_grid2->refresh_table_display.
**
**    ENDIF.
*
*  ENDMETHOD.                  "on_hotspot_click

*  METHOD handle_menu_button.
*
**    CONSTANTS: cl_btn_aprov     TYPE ui_func VALUE 'BT_APROV',
**               cl_btn_list_itm TYPE ui_func VALUE 'LISTITM'.
**
**    IF e_ucomm = cl_btn_aprov.
**      CALL METHOD e_object->add_function
**        EXPORTING
**          fcode = cl_btn_list_itm
**          text  = 'Submeter aprovação'. "text-l01.
**    ENDIF.
*
*  ENDMETHOD.

  METHOD  handle_user_command.
    DATA: tl_columns    TYPE lvc_t_col,
          el_columns    TYPE LINE OF lvc_t_col,
          tl_index_rows TYPE lvc_t_row,
          el_index_rows TYPE LINE OF lvc_t_row,
*          tl_row_no     TYPE lvc_t_roid,
*          el_row_no     TYPE LINE OF lvc_t_roid,
          vl_value(132) TYPE c,
          vl_calc       TYPE c,
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*          vl_retorno    TYPE ztsdd_simupreca-msg_autom,
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM.
          vl_tabix      TYPE sy-tabix.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
    DATA: el_celltab      TYPE lvc_s_styl.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - fim
    IF e_ucomm EQ 'BT_SET' OR
       e_ucomm EQ 'BT_RAPPEL'.

      IF e_ucomm NE 'BT_RAPPEL'.
*   Obtém a coluna selecionada
        CALL METHOD vg_grid->get_selected_columns
          IMPORTING
            et_index_columns = tl_columns.

        DELETE tl_columns WHERE fieldname NE 'QTDE_MIN'
                            AND fieldname NE 'PV_FIN'.
      ELSE.
        el_columns-fieldname = 'RAPPEL'.
        APPEND el_columns TO tl_columns.
      ENDIF.

      IF tl_columns[] IS NOT INITIAL.

        "Verificar material a ser alterado
        PERFORM f_seleciona_material_centro.

        IF tg_mat_pop[] IS NOT INITIAL.
          "Exibir popup para definição de valor
          LOOP AT tl_columns INTO el_columns.

            CALL FUNCTION 'FOBU_POPUP_GET_VALUE'
              EXPORTING
                tablename         = 'ZTSDD_SIMUPRECI'
                fieldname         = el_columns-fieldname
              IMPORTING
                field_value_int_c = vl_value
              EXCEPTIONS
                internal_error    = 1
                cancelled         = 2
                OTHERS            = 3.
            IF sy-subrc NE 0.
              CLEAR vl_value.
            ENDIF.
            IF vl_value IS NOT INITIAL.
              LOOP AT tg_mat_pop INTO eg_mat_pop.        "#EC CI_NESTED
                LOOP AT tg_saida INTO eg_saida WHERE matnr = eg_mat_pop-matnr
                                                 AND werks = eg_mat_pop-werks. "#EC CI_NESTED
                  vl_tabix = sy-tabix.
                  CASE el_columns-fieldname.
                    WHEN 'QTDE_MIN'.
                      eg_saida-qtde_min = vl_value.
                    WHEN 'RAPPEL'.
                      eg_saida-rappel = vl_value.
                      vl_calc = abap_true.
                    WHEN 'PV_FIN'.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
                      READ TABLE eg_saida-celltab INTO el_celltab INDEX 1.
                      IF sy-subrc EQ 0.
                        IF el_celltab-style = cl_gui_alv_grid=>mc_style_disabled.
                          CONTINUE.
                        ENDIF.
                      ENDIF.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - fim
                      eg_saida-pv_fin = vl_value.
                      "Converter para preço psicológico
                      CALL FUNCTION 'PRICE_POINT_READ'
                        EXPORTING
                          pi_vkorg                   = 'LB01'
                          pi_vtweg                   = '10'
                          pi_rktyp                   = 'A'
* Alteração - PR.8231 - 02.05.2022  - Inicio
*                         pi_eprgr                   = 'ZLMB01'
                          pi_eprgr                   = 'ZLMB07'
* Alteração - PR.8231 - 02.05.2022  - FIM
                          pi_price                   = eg_saida-pv_fin
                          pi_waers                   = 'BRL'
                          pi_datam                   = sy-datum
                          pi_kurst                   = 'M'
                          pi_hwaer                   = 'BRL'
                          pi_mfact                   = '1'
                        IMPORTING
                          pe_price                   = eg_saida-pv_fin
                        EXCEPTIONS
                          no_price_point_group_found = 1
                          no_price_points_maintained = 2
                          conversion_not_found       = 3
                          OTHERS                     = 4.
                      IF sy-subrc EQ 0.
                        vl_calc = abap_true.
                      ENDIF.
                  ENDCASE.
                  MODIFY tg_saida FROM eg_saida INDEX vl_tabix.
                ENDLOOP.
              ENDLOOP.
            ENDIF.
          ENDLOOP.


          IF vl_calc IS NOT INITIAL.
            " Efetuar cálculos com os novos valores
            REFRESH tg_dados.
            LOOP AT tg_mat_pop INTO eg_mat_pop.
              LOOP AT tg_saida INTO eg_saida WHERE matnr = eg_mat_pop-matnr
                                               AND werks = eg_mat_pop-werks. "#EC CI_NESTED

                "Preparar dados para cálculo
                eg_dados-pi_matprecadx = eg_saida-matprecadx.
                eg_dados-pi_matnr      = eg_saida-matnr.
                eg_dados-pi_matnr_ref  = eg_saida-matnr_ref.
                eg_dados-pi_mat_ref    = eg_saida-mat_ref.
                eg_dados-pi_matkl      = eg_saida-matkl.
                eg_dados-pi_werks      = eg_saida-werks.
                eg_dados-pi_werks_to   = eg_saida-werks_to.
                eg_dados-pi_vkkab      = eg_saida-vkkab.
                eg_dados-pi_tipo       = '1'.
                eg_dados-pi_state_from = eg_saida-state_from.
                eg_dados-pi_state_to   = eg_saida-state_to.
                eg_dados-pi_mtuse      = eg_saida-mtuse.
                eg_dados-pi_mtorg      = eg_saida-mtorg.
                eg_dados-pi_steuc      = eg_saida-steuc.
                eg_dados-pi_pcb        = eg_saida-pcb.
                eg_dados-pe_pcl        = eg_saida-pcl.
                eg_dados-pe_pclst      = eg_saida-pclst.
                eg_dados-pi_pclx       = space.
                eg_dados-pi_mwskz      = eg_saida-mwskz.
                eg_dados-pi_pvfin      = eg_saida-pv_fin.
                eg_dados-pi_rappel     = eg_saida-rappel.
                eg_dados-pi_index      = sy-tabix.
                eg_dados-pi_uf_precad  = eg_saida-uf_precad.

                "Manter dados de compra
                eg_dados-pe_rate_icms_comp      =  eg_saida-rate_icms_comp.
                eg_dados-pe_base_icms_comp      =  eg_saida-base_icms_comp.
                eg_dados-pe_val_icms_comp       =  eg_saida-val_icms_comp.
                eg_dados-pe_rate_ipi_comp       =  eg_saida-rate_ipi_comp.
                eg_dados-pe_base_ipi_comp       =  eg_saida-base_ipi_comp.
                eg_dados-pe_val_ipi_comp        =  eg_saida-val_ipi_comp.
                eg_dados-pe_rate_cofins_comp    =  eg_saida-rate_cofins_comp.
                eg_dados-pe_base_cofins_comp    =  eg_saida-base_cofins_comp.
                eg_dados-pe_val_cofins_comp     =  eg_saida-val_cofins_comp.
                eg_dados-pe_rate_pis_comp       =  eg_saida-rate_pis_comp.
                eg_dados-pe_base_pis_comp       =  eg_saida-base_pis_comp.
                eg_dados-pe_val_pis_comp        =  eg_saida-val_pis_comp.
                eg_dados-pe_calc_base_st_comp   =  eg_saida-calc_base_st_comp.
                eg_dados-pe_calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
                eg_dados-pe_maj_bst_comp        =  eg_saida-maj_bst_comp.
                eg_dados-pe_maj_bicms_comp      =  eg_saida-maj_bicms_comp.
                eg_dados-pe_calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
                eg_dados-pe_calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
                eg_dados-pe_rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
                eg_dados-pe_rate_st_int_comp    =  eg_saida-rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
                eg_dados-pi_lifnr               =  eg_saida-lifnr.
                eg_dados-pi_ltsnr               =  eg_saida-ltsnr.
*                eg_dados-pe_umren_ekpo          =  eg_saida-umren_ekpo.
*                eg_dados-pe_umrez_ekpo          =  eg_saida-umrez_ekpo.
* Alteração - CD.3723 - 24.01.2020 - Inicio
* Alteração - PR.08863 - 02.09.2022 - Inicio
                PERFORM f_verifica_multipla_lista TABLES tg_saida
                                                  USING eg_saida-matnr
                                                        eg_saida-pltyp
                                                        eg_saida-pv_fin
                                                  CHANGING eg_dados-pi_pvfin_lista.

* Alteração - PR.08863 - 02.09.2022 - FIM.

                APPEND eg_dados TO tg_dados.
              ENDLOOP.
            ENDLOOP.

            IF tg_dados[] IS NOT INITIAL.
* Alteração - CC.4592 - 01.07.2020- Inicio
              IF e_ucomm NE 'BT_RAPPEL'.
* Alteração - CC.4592 - 01.07.2020- FIM
                READ TABLE tg_dados INTO eg_dados INDEX 1.  "FB23112018
                CALL FUNCTION 'ZFSD_CALCULA_PRECO'
                  EXPORTING                                   "FB23112018
                    i_pcl    = eg_dados-pe_pcl                "FB23112018
                    i_pcb    = eg_dados-pi_pcb                "FB23112018
                  TABLES
                    tg_dados = tg_dados.
* Alteração - CC.4592 - 01.07.2020- Inicio
              ELSE.
                CALL FUNCTION 'ZFSD_CALCULA_PRECO'
                  TABLES
                    tg_dados = tg_dados.
              ENDIF.
* Alteração - CC.4592 - 01.07.2020- FIM.
              LOOP AT tg_dados INTO eg_dados.
                READ TABLE tg_saida INTO eg_saida INDEX eg_dados-pi_index.

                eg_saida-pcl              = eg_dados-pe_pcl.
                eg_saida-pclst            = eg_dados-pe_pclst.
                eg_saida-preco_transf     = eg_dados-pe_preco_transf.
                eg_saida-custo_log        = eg_dados-pe_lco.
                eg_saida-pv_liq           = eg_dados-pe_pv_liq.
                eg_saida-mg_liq           = eg_dados-pe_mg_liq.
                eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
                eg_saida-pv_fin           = eg_dados-pi_pvfin.
                eg_saida-rate_icms        = eg_dados-pe_rate_icms.
                eg_saida-base_icms        = eg_dados-pe_base_icms.
                eg_saida-cust_icms        = eg_dados-pe_cust_icms.
                eg_saida-val_icms         = eg_dados-pe_val_icms.
                eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
                eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
                eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
                eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
                eg_saida-base_red_1       = eg_dados-pe_base_red_1.
                eg_saida-base_red_2       = eg_dados-pe_base_red_2.
                eg_saida-val_base_st      = eg_dados-pe_val_base_st.
                eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
                eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
                eg_saida-base_ipi         = eg_dados-pe_base_ipi.
                eg_saida-val_ipi          = eg_dados-pe_val_ipi.
                eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
                eg_saida-base_cofins      = eg_dados-pe_base_cofins.
                eg_saida-val_cofins       = eg_dados-pe_val_cofins.
                eg_saida-rate_pis         = eg_dados-pe_rate_pis.
                eg_saida-base_pis         = eg_dados-pe_base_pis.
                eg_saida-val_pis          = eg_dados-pe_val_pis.
                eg_saida-val_rappel       = eg_dados-pe_val_rappel.
                eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
                eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
                eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
                eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
* Alteração - CC.4592 - 01.07.2020  - Inicio
                eg_saida-zstp             = eg_dados-pe_zstp.
                eg_saida-zstv             = eg_dados-pe_zstv.
                eg_saida-zstd             = eg_dados-pe_zstd.
* Alteração - CC.4592 - 01.07.2020  - Fim
                eg_saida-c_mvto           = eg_dados-pe_c_mvto.
                eg_saida-c_pallet         = eg_dados-pe_c_pallet.
                eg_saida-frete            = eg_dados-pe_frete.
                eg_saida-tx_fin           = eg_dados-pe_tx_fin.
                eg_saida-tx_gest          = eg_dados-pe_tx_gest.
                eg_saida-c_arm            = eg_dados-pe_c_arm.
                eg_saida-umrez            = eg_dados-pe_umrez.
                eg_saida-hoehe            = eg_dados-pe_hoehe.
                eg_saida-breit            = eg_dados-pe_breit.
                eg_saida-laeng            = eg_dados-pe_laeng.
                eg_saida-tx_mov           = eg_dados-pe_tx_mov.
                eg_saida-tx_frete         = eg_dados-pe_tx_frete.
                eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
                eg_saida-dias_est         = eg_dados-pe_dias_est.
                eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
                eg_saida-gestao           = eg_dados-pe_gestao.
                eg_saida-tx_desp          = eg_dados-pe_tx_desp.
                eg_saida-tx_fob           = eg_dados-pe_tx_fob.
                eg_saida-despachante      = eg_dados-pe_despachante.
                eg_saida-fob              = eg_dados-pe_fob.
                eg_saida-fin              = eg_dados-pe_fin.

                eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
                eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
                eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
                eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
                eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
                eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
                eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
                eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
                eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
                eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
                eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
                eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
                eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
                eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
                eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
                eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
                eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
                eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
                eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
                eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
                eg_saida-var_cust_log        =  eg_dados-pe_var_cust_log.
* Alteração - CD.3723 - 24.01.2020 - Inicio

                MODIFY tg_saida FROM eg_saida INDEX eg_dados-pi_index.
              ENDLOOP.
            ENDIF.
          ENDIF.
          CALL METHOD vg_grid->refresh_table_display.
        ENDIF.
      ENDIF.
    ENDIF.

    IF e_ucomm EQ 'BT_SET_PCB'.
      "Verificar material a ser alterado
      PERFORM f_seleciona_material_centro.

      IF tg_mat_pop[] IS NOT INITIAL.
        CALL FUNCTION 'FOBU_POPUP_GET_VALUE'
          EXPORTING
            tablename         = 'ZTSDD_SIMUPRECI'
            fieldname         = 'PCB'
          IMPORTING
            field_value_int_c = vl_value
          EXCEPTIONS
            internal_error    = 1
            cancelled         = 2
            OTHERS            = 3.
        IF sy-subrc NE 0.
          CLEAR vl_value.
        ENDIF.
        IF vl_value IS NOT INITIAL.
          REFRESH: tg_dados, tg_pcl.

          "Atribuir valores
          LOOP AT tg_mat_pop INTO eg_mat_pop.
            LOOP AT tg_saida INTO eg_saida WHERE matnr EQ eg_mat_pop-matnr
                                             AND werks EQ eg_mat_pop-werks. "#EC CI_NESTED
              eg_saida-pcb = vl_value.
              MODIFY tg_saida FROM eg_saida INDEX sy-tabix.

              "Preparar dados para cálculo
              eg_dados-pi_matprecadx = eg_saida-matprecadx.
              eg_dados-pi_matnr      = eg_saida-matnr.
              eg_dados-pi_matnr_ref  = eg_saida-matnr_ref.
              eg_dados-pi_matkl      = eg_saida-matkl.
              eg_dados-pi_werks      = eg_saida-werks.
              eg_dados-pi_werks_to   = eg_saida-werks_to.
              eg_dados-pi_vkkab      = eg_saida-vkkab.
              eg_dados-pi_tipo       = '1'.
              eg_dados-pi_state_from = eg_saida-state_from.
              eg_dados-pi_state_to   = eg_saida-state_to.
              eg_dados-pi_mtuse      = eg_saida-mtuse.
              eg_dados-pi_mtorg      = eg_saida-mtorg.
              eg_dados-pi_steuc      = eg_saida-steuc.
              eg_dados-pi_pcb        = eg_saida-pcb.
              eg_dados-pi_index      = sy-tabix.
              eg_dados-pi_mat_ref    = eg_saida-mat_ref.
              eg_dados-pi_mwskz      = eg_saida-mwskz.

              READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_saida-matnr
                                                     werks = eg_saida-werks.
              IF sy-subrc EQ 0.
                eg_dados-pi_pclx       = abap_false.
                eg_dados-pe_pcl        = eg_pcl-pcl.
                eg_dados-pe_pclst      = eg_pcl-pclst.
                eg_dados-pe_rate_icms_comp      =  eg_pcl-rate_icms_comp.
                eg_dados-pe_base_icms_comp      =  eg_pcl-base_icms_comp.
                eg_dados-pe_val_icms_comp       =  eg_pcl-val_icms_comp.
                eg_dados-pe_rate_ipi_comp       =  eg_pcl-rate_ipi_comp.
                eg_dados-pe_base_ipi_comp       =  eg_pcl-base_ipi_comp.
                eg_dados-pe_val_ipi_comp        =  eg_pcl-val_ipi_comp.
                eg_dados-pe_rate_cofins_comp    =  eg_pcl-rate_cofins_comp.
                eg_dados-pe_base_cofins_comp    =  eg_pcl-base_cofins_comp.
                eg_dados-pe_val_cofins_comp     =  eg_pcl-val_cofins_comp.
                eg_dados-pe_rate_pis_comp       =  eg_pcl-rate_pis_comp.
                eg_dados-pe_base_pis_comp       =  eg_pcl-base_pis_comp.
                eg_dados-pe_val_pis_comp        =  eg_pcl-val_pis_comp.
                eg_dados-pe_calc_base_st_comp   =  eg_pcl-calc_base_st_comp.
                eg_dados-pe_calc_icms_st_comp   =  eg_pcl-calc_icms_st_comp.
                eg_dados-pe_maj_bst_comp        =  eg_pcl-maj_bst_comp.
                eg_dados-pe_maj_bicms_comp      =  eg_pcl-maj_bicms_comp.
                eg_dados-pe_calc_pis_st_comp    =  eg_pcl-calc_pis_st_comp.
                eg_dados-pe_calc_cofins_st_comp =  eg_pcl-calc_cofins_st_comp.
                eg_dados-pe_rate_icms_st_comp   =  eg_pcl-rate_icms_st_comp.
                eg_dados-pe_rate_st_int_comp    =  eg_pcl-rate_st_int_comp.
              ELSE.
                eg_dados-pi_pclx       = abap_true.
              ENDIF.

              eg_dados-pi_pvfin      = eg_saida-pv_fin.
              eg_dados-pi_rappel     = eg_saida-rappel.
              eg_dados-pi_uf_precad  = eg_saida-uf_precad.

              "Manter dados de compra
              eg_dados-pe_rate_icms_comp      =  eg_saida-rate_icms_comp.
              eg_dados-pe_base_icms_comp      =  eg_saida-base_icms_comp.
              eg_dados-pe_val_icms_comp       =  eg_saida-val_icms_comp.
              eg_dados-pe_rate_ipi_comp       =  eg_saida-rate_ipi_comp.
              eg_dados-pe_base_ipi_comp       =  eg_saida-base_ipi_comp.
              eg_dados-pe_val_ipi_comp        =  eg_saida-val_ipi_comp.
              eg_dados-pe_rate_cofins_comp    =  eg_saida-rate_cofins_comp.
              eg_dados-pe_base_cofins_comp    =  eg_saida-base_cofins_comp.
              eg_dados-pe_val_cofins_comp     =  eg_saida-val_cofins_comp.
              eg_dados-pe_rate_pis_comp       =  eg_saida-rate_pis_comp.
              eg_dados-pe_base_pis_comp       =  eg_saida-base_pis_comp.
              eg_dados-pe_val_pis_comp        =  eg_saida-val_pis_comp.
              eg_dados-pe_calc_base_st_comp   =  eg_saida-calc_base_st_comp.
              eg_dados-pe_calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
              eg_dados-pe_maj_bst_comp        =  eg_saida-maj_bst_comp.
              eg_dados-pe_maj_bicms_comp      =  eg_saida-maj_bicms_comp.
              eg_dados-pe_calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
              eg_dados-pe_calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
              eg_dados-pe_rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
              eg_dados-pe_rate_st_int_comp    =  eg_saida-rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
              eg_dados-pi_lifnr               =  eg_saida-lifnr.
              eg_dados-pi_ltsnr               =  eg_saida-ltsnr.
*              eg_dados-pe_umren_ekpo          =  eg_saida-umren_ekpo.
*              eg_dados-pe_umrez_ekpo          =  eg_saida-umrez_ekpo.
* Alteração - CD.3723 - 24.01.2020 - Inicio
* Alteração - PR.08863 - 02.09.2022 - Inicio
              PERFORM f_verifica_multipla_lista TABLES tg_saida
                                                USING eg_saida-matnr
                                                      eg_saida-pltyp
                                                      eg_saida-pv_fin
                                                CHANGING eg_dados-pi_pvfin_lista.

* Alteração - PR.08863 - 02.09.2022 - FIM.
              APPEND eg_dados TO tg_dados.
            ENDLOOP.
          ENDLOOP.

          IF tg_dados[] IS NOT INITIAL.
            READ TABLE tg_dados INTO eg_dados INDEX 1.      "FB23112018
            CALL FUNCTION 'ZFSD_CALCULA_PRECO'
              EXPORTING                                   "FB23112018
                i_pcl    = eg_dados-pe_pcl                "FB23112018
                i_pcb    = eg_dados-pi_pcb                "FB23112018
              TABLES
                tg_dados = tg_dados.

            LOOP AT tg_dados INTO eg_dados.
              READ TABLE tg_saida INTO eg_saida INDEX eg_dados-pi_index.

              eg_saida-pcl              = eg_dados-pe_pcl.
              eg_saida-pclst            = eg_dados-pe_pclst.
              eg_saida-preco_transf     = eg_dados-pe_preco_transf.
              eg_saida-custo_log        = eg_dados-pe_lco.
              eg_saida-pv_liq           = eg_dados-pe_pv_liq.
              eg_saida-mg_liq           = eg_dados-pe_mg_liq.
              eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
              eg_saida-pv_fin           = eg_dados-pi_pvfin.
              eg_saida-rate_icms        = eg_dados-pe_rate_icms.
              eg_saida-base_icms        = eg_dados-pe_base_icms.
              eg_saida-cust_icms        = eg_dados-pe_cust_icms.
              eg_saida-val_icms         = eg_dados-pe_val_icms.
              eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
              eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
              eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
              eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
              eg_saida-base_red_1       = eg_dados-pe_base_red_1.
              eg_saida-base_red_2       = eg_dados-pe_base_red_2.
              eg_saida-val_base_st      = eg_dados-pe_val_base_st.
              eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
              eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
              eg_saida-base_ipi         = eg_dados-pe_base_ipi.
              eg_saida-val_ipi          = eg_dados-pe_val_ipi.
              eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
              eg_saida-base_cofins      = eg_dados-pe_base_cofins.
              eg_saida-val_cofins       = eg_dados-pe_val_cofins.
              eg_saida-rate_pis         = eg_dados-pe_rate_pis.
              eg_saida-base_pis         = eg_dados-pe_base_pis.
              eg_saida-val_pis          = eg_dados-pe_val_pis.
              eg_saida-val_rappel       = eg_dados-pe_val_rappel.
              eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
              eg_saida-gestao           = eg_dados-pe_gestao.
              eg_saida-tx_desp          = eg_dados-pe_tx_desp.
              eg_saida-tx_fob           = eg_dados-pe_tx_fob.
              eg_saida-despachante      = eg_dados-pe_despachante.
              eg_saida-fob              = eg_dados-pe_fob.
              eg_saida-fin              = eg_dados-pe_fin.
              eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
              eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
              eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
* Alteração - CC.4592 - 01.07.2020  - Inicio
              eg_saida-zstp             = eg_dados-pe_zstp.
              eg_saida-zstv             = eg_dados-pe_zstv.
              eg_saida-zstd             = eg_dados-pe_zstd.
* Alteração - CC.4592 - 01.07.2020  - Fim
              eg_saida-c_mvto           = eg_dados-pe_c_mvto.
              eg_saida-c_pallet         = eg_dados-pe_c_pallet.
              eg_saida-frete            = eg_dados-pe_frete.
              eg_saida-tx_fin           = eg_dados-pe_tx_fin.
              eg_saida-tx_gest          = eg_dados-pe_tx_gest.
              eg_saida-c_arm            = eg_dados-pe_c_arm.
              eg_saida-umrez            = eg_dados-pe_umrez.
              eg_saida-hoehe            = eg_dados-pe_hoehe.
              eg_saida-breit            = eg_dados-pe_breit.
              eg_saida-laeng            = eg_dados-pe_laeng.
              eg_saida-tx_mov           = eg_dados-pe_tx_mov.
              eg_saida-tx_frete         = eg_dados-pe_tx_frete.
              eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
              eg_saida-dias_est         = eg_dados-pe_dias_est.
              eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
              eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
              eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
              eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
              eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
              eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
              eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
              eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
              eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
              eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
              eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
              eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
              eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
              eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
              eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
              eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
              eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
              eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
              eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
              eg_saida-rate_icms_venda     =  eg_dados-pe_rate_icms_venda.
              eg_saida-base_icms_venda     =  eg_dados-pe_base_icms_venda.
              eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
              eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
              eg_saida-var_cust_log        =  eg_dados-pe_var_cust_log.
* Alteração - CD.3723 - 24.01.2020 - Inicio
              MODIFY tg_saida FROM eg_saida INDEX eg_dados-pi_index.

              READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_dados-pi_matnr
                                                     werks = eg_dados-pi_werks.
              IF sy-subrc NE 0.
                eg_pcl-matnr      = eg_dados-pi_matnr.
                eg_pcl-werks      = eg_dados-pi_werks.
                eg_pcl-pcl        = eg_dados-pe_pcl.
                eg_pcl-pclst      = eg_dados-pe_pclst.
                eg_pcl-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
                eg_pcl-base_icms_comp      =  eg_dados-pe_base_icms_comp.
                eg_pcl-val_icms_comp       =  eg_dados-pe_val_icms_comp.
                eg_pcl-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
                eg_pcl-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
                eg_pcl-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
                eg_pcl-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
                eg_pcl-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
                eg_pcl-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
                eg_pcl-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
                eg_pcl-base_pis_comp       =  eg_dados-pe_base_pis_comp.
                eg_pcl-val_pis_comp        =  eg_dados-pe_val_pis_comp.
                eg_pcl-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
                eg_pcl-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
                eg_pcl-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
                eg_pcl-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
                eg_pcl-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
                eg_pcl-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
                eg_pcl-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
                eg_pcl-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
                APPEND eg_pcl TO tg_pcl.
              ENDIF.

            ENDLOOP.
          ENDIF.
          CALL METHOD vg_grid->refresh_table_display.
        ENDIF.
      ENDIF.
    ENDIF.

    IF e_ucomm EQ 'BT_COMP'   OR
       e_ucomm EQ 'BT_TRANSF' OR
       e_ucomm EQ 'BT_VENDA'.

      sy-ucomm = e_ucomm.

*   Obtém a linha selecionada
      CALL METHOD vg_grid->get_selected_rows
        IMPORTING
          et_index_rows = tl_index_rows.
*          et_row_no     = tl_row_no.

      REFRESH tg_impostos.
      LOOP AT tl_index_rows INTO el_index_rows.

        READ TABLE tg_saida INTO eg_saida INDEX el_index_rows-index.
        eg_impostos-matnr               =  eg_saida-matnr.
        eg_impostos-werks               =  eg_saida-werks.
        eg_impostos-ptext               =  eg_saida-ptext.
        eg_impostos-mwskz               =  eg_saida-mwskz.

        READ TABLE tg_t007s INTO eg_t007s WITH KEY mwskz = eg_impostos-mwskz.
        eg_impostos-text1  = eg_t007s-text1.

        eg_impostos-state_from          =  eg_saida-state_from.
        eg_impostos-uf_precad           =  eg_saida-uf_precad.

        IF e_ucomm EQ 'BT_COMP' AND eg_saida-mat_ref IS NOT INITIAL.
          CONTINUE.
        ENDIF.

        eg_impostos-state_to            =  eg_saida-state_to.
        eg_impostos-rate_icms           =  eg_saida-rate_icms.
        eg_impostos-base_icms           =  eg_saida-base_icms.
        eg_impostos-rate_icms_venda     =  eg_saida-rate_icms_venda.
        eg_impostos-base_icms_venda     =  eg_saida-base_icms_venda.
        eg_impostos-cust_icms           =  eg_saida-cust_icms.
        eg_impostos-val_icms            =  eg_saida-val_icms.
        eg_impostos-rate_icms_st        =  eg_saida-rate_icms_st.
        eg_impostos-base_icms_st        =  eg_saida-base_icms_st.
        eg_impostos-rate_icms_st_int    =  eg_saida-rate_icms_st_int.
        eg_impostos-base_icms_st_int    =  eg_saida-base_icms_st_int.
        eg_impostos-base_red_1          =  eg_saida-base_red_1.
        eg_impostos-base_red_2          =  eg_saida-base_red_2.
        eg_impostos-val_base_st         =  eg_saida-val_base_st.
        eg_impostos-val_icms_st         =  eg_saida-val_icms_st.
        eg_impostos-rate_ipi            =  eg_saida-rate_ipi.
        eg_impostos-base_ipi            =  eg_saida-base_ipi.
        eg_impostos-val_ipi             =  eg_saida-val_ipi.
        eg_impostos-rate_cofins         =  eg_saida-rate_cofins.
        eg_impostos-base_cofins         =  eg_saida-base_cofins.
        eg_impostos-val_cofins          =  eg_saida-val_cofins.
        eg_impostos-rate_pis            =  eg_saida-rate_pis.
        eg_impostos-base_pis            =  eg_saida-base_pis.
        eg_impostos-val_pis             =  eg_saida-val_pis.
        eg_impostos-val_rappel          =  eg_saida-val_rappel.
        eg_impostos-val_custo_log       =  eg_saida-val_custo_log.
        eg_impostos-total_imp_venda     =  eg_saida-total_imp_venda.
        eg_impostos-rate_icms_comp      =  eg_saida-rate_icms_comp.
        eg_impostos-base_icms_comp      =  eg_saida-base_icms_comp.
        eg_impostos-val_icms_comp       =  eg_saida-val_icms_comp.
        eg_impostos-rate_ipi_comp       =  eg_saida-rate_ipi_comp.
        eg_impostos-base_ipi_comp       =  eg_saida-base_ipi_comp.
        eg_impostos-val_ipi_comp        =  eg_saida-val_ipi_comp.
        eg_impostos-rate_cofins_comp    =  eg_saida-rate_cofins_comp.
        eg_impostos-base_cofins_comp    =  eg_saida-base_cofins_comp.
        eg_impostos-val_cofins_comp     =  eg_saida-val_cofins_comp.
        eg_impostos-rate_pis_comp       =  eg_saida-rate_pis_comp.
        eg_impostos-base_pis_comp       =  eg_saida-base_pis_comp.
        eg_impostos-val_pis_comp        =  eg_saida-val_pis_comp.
        eg_impostos-calc_base_st_comp   =  eg_saida-calc_base_st_comp.
        eg_impostos-calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
        eg_impostos-maj_bst_comp        =  eg_saida-maj_bst_comp.
        eg_impostos-maj_bicms_comp      =  eg_saida-maj_bicms_comp.
        eg_impostos-calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
        eg_impostos-calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
        eg_impostos-rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
        eg_impostos-rate_st_int_comp    =  eg_saida-rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
        eg_impostos-var_cust_log        = eg_saida-var_cust_log.
* Alteração - CD.3723 - 24.01.2020 - FIM
* Alteração - CC.4592 - 01.07.2020  - Inicio
        eg_impostos-zstp             = eg_saida-zstp.
        eg_impostos-zstv             = eg_saida-zstv.
        eg_impostos-zstd             = eg_saida-zstd.
* Alteração - CC.4592 - 01.07.2020  - Fim
        APPEND eg_impostos TO tg_impostos.
        CLEAR eg_impostos.
      ENDLOOP.

      IF e_ucomm EQ 'BT_COMP'.
        "Função disponível apenas para materiais pré-cadastrados sem referência.
        MESSAGE i124(zmsd_classe_mensagem).
        SORT tg_impostos BY matnr werks.
        DELETE ADJACENT DUPLICATES FROM tg_impostos COMPARING matnr werks.
      ENDIF.

      IF tg_impostos[] IS NOT INITIAL.
        PERFORM f_exibe_impostos.
      ENDIF.

      CALL METHOD vg_grid->refresh_table_display.
    ENDIF.

    IF e_ucomm EQ 'BT_C_LOG'.
* Alteração - PRIC-2507 - 17.04.2025  - Inicio
      SELECT knumh UP TO 1 ROWS
        INTO @DATA(vl_knumh)
        FROM a350
       WHERE kappl = 'V'
         AND vkorg = 'LB01'
         AND kschl = 'ZCLX'
         AND datbi >= @so_vkkab-low
         AND datab <= @so_vkkab-low.
      ENDSELECT.
      IF sy-subrc EQ 0.
        SELECT *
          INTO TABLE @DATA(tl_konw)
          FROM konw
         WHERE knumh = @vl_knumh.
        IF sy-subrc EQ 0.
          IF tl_konw[] IS NOT INITIAL.
            LOOP AT tl_konw ASSIGNING FIELD-SYMBOL(<fs_k>).
              <fs_k>-kbetr = <fs_k>-kbetr / 10.
            ENDLOOP.
            PERFORM f_exibe_c_log TABLES tl_konw.
          ENDIF.

        ENDIF.
      ENDIF.

**   Obtém a linha selecionada
*      CALL METHOD vg_grid->get_selected_rows
*        IMPORTING
*          et_index_rows = tl_index_rows.
**          et_row_no     = tl_row_no.
*
*      REFRESH tg_val_c_log.
*      LOOP AT tl_index_rows INTO el_index_rows.
*        READ TABLE tg_saida INTO eg_saida INDEX el_index_rows-index.
*
*        eg_val_c_log-matnr            = eg_saida-matnr.
*        eg_val_c_log-werks            = eg_saida-werks.
*        eg_val_c_log-pcl              = eg_saida-pcl.
*        eg_val_c_log-c_mvto           = eg_saida-c_mvto.
*        eg_val_c_log-c_pallet         = eg_saida-c_pallet.
*        eg_val_c_log-frete            = eg_saida-frete.
*        eg_val_c_log-tx_fin           = eg_saida-tx_fin.
*        eg_val_c_log-tx_gest          = eg_saida-tx_gest.
*        eg_val_c_log-c_arm            = eg_saida-c_arm.
*        eg_val_c_log-umrez            = eg_saida-umrez.
*        eg_val_c_log-hoehe            = eg_saida-hoehe.
*        eg_val_c_log-breit            = eg_saida-breit.
*        eg_val_c_log-laeng            = eg_saida-laeng.
*        eg_val_c_log-tx_mov           = eg_saida-tx_mov.
*        eg_val_c_log-tx_frete         = eg_saida-tx_frete.
*        eg_val_c_log-custo_ins_pallet = eg_saida-custo_ins_pallet.
*        eg_val_c_log-dias_est         = eg_saida-dias_est.
*        eg_val_c_log-custo_armazen    = eg_saida-custo_armazen.
*        eg_val_c_log-gestao           = eg_saida-gestao.
*        eg_val_c_log-tx_desp          = eg_saida-tx_desp.
*        eg_val_c_log-tx_fob           = eg_saida-tx_fob.
*        eg_val_c_log-despachante      = eg_saida-despachante.
*        eg_val_c_log-fob              = eg_saida-fob.
*        eg_val_c_log-fin              = eg_saida-fin.
*
*        APPEND eg_val_c_log TO tg_val_c_log.
*        CLEAR eg_val_c_log.
*      ENDLOOP.
*
*      IF tg_val_c_log[] IS NOT INITIAL.
*        PERFORM f_exibe_c_log.
*      ENDIF.
* Alteração - PRIC-2507 - 17.04.2025 - FIM
    ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
    IF e_ucomm EQ 'BT_REP'.

*   Obtém a linha selecionada
      CALL METHOD vg_grid->get_selected_rows
        IMPORTING
          et_index_rows = tl_index_rows.
*          et_row_no     = tl_row_no.

      LOOP AT tl_index_rows INTO el_index_rows.

        READ TABLE tg_saida_rel INTO eg_saida_rel INDEX el_index_rows-index.
        IF sy-subrc EQ 0.

          CALL FUNCTION 'ZFMM_AUTO_SIMULACAO_PRECO_V2'
            EXPORTING
              docsim              = eg_saida_rel-docsim
              pltyp               = eg_saida_rel-pltyp
              matnr               = eg_saida_rel-matnr
              werks               = eg_saida_rel-werks
              reprocessar         = 'X'
              uname               = sy-uname
*            IMPORTING
*             retorno             = vl_retorno
            EXCEPTIONS
              selecao_errada      = 1
              nenhum_doc_aprovado = 2
              OTHERS              = 3.
          IF sy-subrc <> 0.
            CLEAR eg_saida_rel.
          ENDIF.
        ENDIF.
      ENDLOOP.
      PERFORM f_seleciona_dados_rel.
      CALL METHOD vg_grid->refresh_table_display.
    ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
  ENDMETHOD.

  METHOD handle_top_of_page.
* Top-of-page event
    PERFORM event_top_of_page USING vg_dyndoc_id.

  ENDMETHOD.                            "handle_top_of_page

  METHOD handle_data_changed.

    " Just trigger PAI followed by PBO
    CALL METHOD cl_gui_cfw=>set_new_ok_code
      EXPORTING
        new_code = 'ENTER'
*        IMPORTING
*       rc       =
      .

  ENDMETHOD.                    "handle_data_changed

  METHOD handle_data_changed_finished.
*   define local data
    DATA: ls_cell        TYPE lvc_s_modi.

    REFRESH: tg_dados, tg_change.
    CLEAR: eg_dados, eg_change.

    "Sumarizar alterações no ALV
    LOOP AT et_good_cells INTO ls_cell.

      READ TABLE tg_change INTO eg_change WITH KEY index = ls_cell-row_id.

      IF sy-subrc EQ 0.
        CASE ls_cell-fieldname.
          WHEN 'PCB'.
            eg_change-pclx = abap_true.
            eg_change-pcb_v = ls_cell-value.

          WHEN 'PV_FIN'.
            eg_change-pv_fin_v = ls_cell-value.

          WHEN 'RAPPEL'.
            eg_change-rappel_v = ls_cell-value.
        ENDCASE.
        MODIFY tg_change FROM eg_change INDEX sy-tabix.

      ELSE.
        eg_change-index = ls_cell-row_id.

        CASE ls_cell-fieldname.
          WHEN 'PCB'.
            eg_change-pclx = abap_true.
            eg_change-pcb_v = ls_cell-value.

          WHEN 'PV_FIN'.
            eg_change-pv_fin_v = ls_cell-value.

          WHEN 'RAPPEL'.
            eg_change-rappel_v = ls_cell-value.
        ENDCASE.

        APPEND eg_change TO tg_change.
      ENDIF.
      CLEAR eg_change.
    ENDLOOP.

    "Preparar dados para cálculo
    LOOP AT tg_change INTO eg_change.
      READ TABLE tg_saida INTO eg_saida INDEX eg_change-index.

      eg_dados-pi_matprecadx = eg_saida-matprecadx.
      eg_dados-pi_matnr      = eg_saida-matnr.
      eg_dados-pi_matnr_ref  = eg_saida-matnr_ref.
      eg_dados-pi_matkl      = eg_saida-matkl.
      eg_dados-pi_werks      = eg_saida-werks.
      eg_dados-pi_werks_to   = eg_saida-werks_to.
      eg_dados-pi_vkkab      = eg_saida-vkkab.
      eg_dados-pi_tipo       = '1'.
      eg_dados-pi_state_from = eg_saida-state_from.
      eg_dados-pi_state_to   = eg_saida-state_to.
      eg_dados-pi_mtuse      = eg_saida-mtuse.
      eg_dados-pi_mtorg      = eg_saida-mtorg.
      eg_dados-pi_steuc      = eg_saida-steuc.
      eg_dados-pi_mat_ref    = eg_saida-mat_ref.
      eg_dados-pi_mwskz      = eg_saida-mwskz.

      IF eg_change-pcb_v IS NOT INITIAL.
        eg_dados-pi_pcb        = eg_change-pcb_v.
        eg_dados-pi_pclx       = abap_true.
      ELSE.
        eg_dados-pi_pcb        = eg_saida-pcb.
        eg_dados-pe_pcl        = eg_saida-pcl.
        eg_dados-pe_pclst      = eg_saida-pclst.
        eg_dados-pi_pclx       = space.
      ENDIF.

      IF eg_change-pv_fin_v IS NOT INITIAL.
        "Converter para preço psicológico
        CALL FUNCTION 'PRICE_POINT_READ'
          EXPORTING
            pi_vkorg                   = 'LB01'
            pi_vtweg                   = '10'
            pi_rktyp                   = 'A'
* Alteração - PR.8231 - 02.05.2022  - Inicio
*           pi_eprgr                   = 'ZLMB01'
            pi_eprgr                   = 'ZLMB07'
* Alteração - PR.8231 - 02.05.2022  - FIM
            pi_price                   = eg_change-pv_fin_v
            pi_waers                   = 'BRL'
            pi_datam                   = sy-datum
            pi_kurst                   = 'M'
            pi_hwaer                   = 'BRL'
            pi_mfact                   = '1'
          IMPORTING
            pe_price                   = eg_change-pv_fin_v
          EXCEPTIONS
            no_price_point_group_found = 1
            no_price_points_maintained = 2
            conversion_not_found       = 3
            OTHERS                     = 4.
        IF sy-subrc EQ 0.
          eg_dados-pi_pvfin     = eg_change-pv_fin_v.
        ENDIF.
      ELSE.
        eg_dados-pi_pvfin     = eg_saida-pv_fin.
      ENDIF.

      IF eg_change-rappel_v IS NOT INITIAL.
        eg_dados-pi_rappel     = eg_change-rappel_v.
      ELSE.
        eg_dados-pi_rappel     = eg_saida-rappel.
      ENDIF.

      eg_dados-pi_index      = eg_change-index.
      eg_dados-pi_uf_precad  = eg_saida-uf_precad.

      "Manter dados de compra
      eg_dados-pe_rate_icms_comp      =  eg_saida-rate_icms_comp.
      eg_dados-pe_base_icms_comp      =  eg_saida-base_icms_comp.
      eg_dados-pe_val_icms_comp       =  eg_saida-val_icms_comp.
      eg_dados-pe_rate_ipi_comp       =  eg_saida-rate_ipi_comp.
      eg_dados-pe_base_ipi_comp       =  eg_saida-base_ipi_comp.
      eg_dados-pe_val_ipi_comp        =  eg_saida-val_ipi_comp.
      eg_dados-pe_rate_cofins_comp    =  eg_saida-rate_cofins_comp.
      eg_dados-pe_base_cofins_comp    =  eg_saida-base_cofins_comp.
      eg_dados-pe_val_cofins_comp     =  eg_saida-val_cofins_comp.
      eg_dados-pe_rate_pis_comp       =  eg_saida-rate_pis_comp.
      eg_dados-pe_base_pis_comp       =  eg_saida-base_pis_comp.
      eg_dados-pe_val_pis_comp        =  eg_saida-val_pis_comp.
      eg_dados-pe_calc_base_st_comp   =  eg_saida-calc_base_st_comp.
      eg_dados-pe_calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
      eg_dados-pe_maj_bst_comp        =  eg_saida-maj_bst_comp.
      eg_dados-pe_maj_bicms_comp      =  eg_saida-maj_bicms_comp.
      eg_dados-pe_calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
      eg_dados-pe_calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
      eg_dados-pe_rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
      eg_dados-pe_rate_st_int_comp    =  eg_saida-rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
      eg_dados-pi_lifnr               =  eg_saida-lifnr.
      eg_dados-pi_ltsnr               =  eg_saida-ltsnr.
*      eg_dados-pe_umren_ekpo          =  eg_saida-umren_ekpo.
*      eg_dados-pe_umrez_ekpo          =  eg_saida-umrez_ekpo.
* Alteração - CD.3723 - 24.01.2020 - Inicio
* Alteração - PR.08863 - 02.09.2022 - Inicio
      PERFORM f_verifica_multipla_lista TABLES tg_saida
                                        USING eg_saida-matnr
                                              eg_saida-pltyp
                                              eg_saida-pv_fin
                                        CHANGING eg_dados-pi_pvfin_lista.

* Alteração - PR.08863 - 02.09.2022 - FIM.
      APPEND eg_dados TO tg_dados.
    ENDLOOP.

    IF tg_dados[] IS NOT INITIAL.

      READ TABLE tg_dados INTO eg_dados INDEX 1.            "FB23112018
      CALL FUNCTION 'ZFSD_CALCULA_PRECO'
        EXPORTING                                           "FB23112018
          i_pcl    = eg_dados-pe_pcl                        "FB23112018
          i_pcb    = eg_dados-pi_pcb                        "FB23112018
        TABLES
          tg_dados = tg_dados.

      LOOP AT tg_dados INTO eg_dados.
        READ TABLE tg_saida INTO eg_saida INDEX eg_dados-pi_index.

        eg_saida-pcl              = eg_dados-pe_pcl.
        eg_saida-pclst            = eg_dados-pe_pclst.
        eg_saida-preco_transf     = eg_dados-pe_preco_transf.
        eg_saida-custo_log        = eg_dados-pe_lco.
        eg_saida-pv_liq           = eg_dados-pe_pv_liq.
        eg_saida-mg_liq           = eg_dados-pe_mg_liq.
        eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
        eg_saida-pv_fin           = eg_dados-pi_pvfin.
        eg_saida-rate_icms        = eg_dados-pe_rate_icms.
        eg_saida-base_icms        = eg_dados-pe_base_icms.
        eg_saida-cust_icms        = eg_dados-pe_cust_icms.
        eg_saida-val_icms         = eg_dados-pe_val_icms.
        eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
        eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
        eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
        eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
        eg_saida-base_red_1       = eg_dados-pe_base_red_1.
        eg_saida-base_red_2       = eg_dados-pe_base_red_2.
        eg_saida-val_base_st      = eg_dados-pe_val_base_st.
        eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
        eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
        eg_saida-base_ipi         = eg_dados-pe_base_ipi.
        eg_saida-val_ipi          = eg_dados-pe_val_ipi.
        eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
        eg_saida-base_cofins      = eg_dados-pe_base_cofins.
        eg_saida-val_cofins       = eg_dados-pe_val_cofins.
        eg_saida-rate_pis         = eg_dados-pe_rate_pis.
        eg_saida-base_pis         = eg_dados-pe_base_pis.
        eg_saida-val_pis          = eg_dados-pe_val_pis.
        eg_saida-val_rappel       = eg_dados-pe_val_rappel.
        eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
        eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
        eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
        eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
        eg_saida-gestao           = eg_dados-pe_gestao.
        eg_saida-tx_desp          = eg_dados-pe_tx_desp.
        eg_saida-tx_fob           = eg_dados-pe_tx_fob.
        eg_saida-despachante      = eg_dados-pe_despachante.
        eg_saida-fob              = eg_dados-pe_fob.
        eg_saida-fin              = eg_dados-pe_fin.

        eg_saida-c_mvto           = eg_dados-pe_c_mvto.
        eg_saida-c_pallet         = eg_dados-pe_c_pallet.
        eg_saida-frete            = eg_dados-pe_frete.
        eg_saida-tx_fin           = eg_dados-pe_tx_fin.
        eg_saida-tx_gest          = eg_dados-pe_tx_gest.
        eg_saida-c_arm            = eg_dados-pe_c_arm.
        eg_saida-umrez            = eg_dados-pe_umrez.
        eg_saida-hoehe            = eg_dados-pe_hoehe.
        eg_saida-breit            = eg_dados-pe_breit.
        eg_saida-laeng            = eg_dados-pe_laeng.
        eg_saida-tx_mov           = eg_dados-pe_tx_mov.
        eg_saida-tx_frete         = eg_dados-pe_tx_frete.
        eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
        eg_saida-dias_est         = eg_dados-pe_dias_est.
        eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.

        eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
        eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
        eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
        eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
        eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
        eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
        eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
        eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
        eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
        eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
        eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
        eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
        eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
        eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
        eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
        eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
        eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
        eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
        eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
        eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
* Alteração - CD.3723 - 24.01.2020 - Inicio
        eg_saida-var_cust_log        =  eg_dados-pe_var_cust_log.
* Alteração - CD.3723 - 24.01.2020 - Inicio
        MODIFY tg_saida FROM eg_saida INDEX eg_dados-pi_index.
      ENDLOOP.
    ENDIF.

  ENDMETHOD.                    "handle_data_changed_finished
ENDCLASS.                 "LCL_EVENT_HANDLER IMPLEMENTATION

*---------------------------------------------------------------------*
* Evento: START-OF-SELECTION
*---------------------------------------------------------------------*
* Objetivo: <descrição>
*---------------------------------------------------------------------*
START-OF-SELECTION.
* Alteração - PR.08862 - 02.09.2022  - Inicio
  PERFORM f_seleciona_listas.
* Alteração - PR.08862 - 02.09.2022  - FIM

* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  IF rb_aut = abap_true.
    PERFORM f_seleciona_dados_rel.
    PERFORM f_call_screen.
  ELSE.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM.
*    PERFORM f_seleciona_dados.
*
*    CHECK vg_erro IS INITIAL.
*
*    PERFORM f_processa_dados.
*    PERFORM f_call_screen.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*  else.
* Alteração - CC.4316 - 01.06.2020 - Inicio
    PERFORM f_seleciona_dados_new.
    CHECK vg_erro IS INITIAL.
    PERFORM f_processa_dados_new.
    PERFORM f_call_screen.
* Alteração - CC.4316 - 01.06.2020 - FIM
  ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM.