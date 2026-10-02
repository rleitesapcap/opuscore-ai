*----------------------------------------------------------------------*
***INCLUDE ZRSD_SIMULADOR_PRECO_IMP_PAI.
*----------------------------------------------------------------------*
*&---------------------------------------------------------------------*
*&      Module  USER_COMMAND_9000  INPUT
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
MODULE user_command_9000 INPUT.

  vg_grid->check_changed_data( ).

  CASE sy-ucomm.
    WHEN c_back OR c_exit OR c_canc.
      PERFORM f_exit.
    WHEN 'ENTER'.
      CALL METHOD vg_grid->refresh_table_display.
    WHEN 'SAVE'.
      PERFORM f_salvar_dados.
  ENDCASE.

ENDMODULE.                 " USER_COMMAND_9000  INPUT
*&---------------------------------------------------------------------*
*&      Form  F_EXIT
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
*  -->  p1        text
*  <--  p2        text
*----------------------------------------------------------------------*
FORM f_exit .
  DATA: vl_answer.
*        vl_question(100).
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  IF rb_aut = abap_false.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
* Abandonar dados da simulação?
  CALL FUNCTION 'POPUP_TO_CONFIRM'
    EXPORTING
      titlebar              = text-q06
      text_question         = text-q05
      text_button_1         = 'Sim'(006)
      text_button_2         = 'Não'(007)
      display_cancel_button = ' '
    IMPORTING
      answer                = vl_answer
    EXCEPTIONS
      text_not_found        = 1
      OTHERS                = 2.

  IF sy-subrc EQ 0 AND vl_answer EQ '1'.
    LEAVE TO SCREEN 0.
  ENDIF.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  else.
    leave to screen 0.
  endif.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
ENDFORM.                    " F_EXIT