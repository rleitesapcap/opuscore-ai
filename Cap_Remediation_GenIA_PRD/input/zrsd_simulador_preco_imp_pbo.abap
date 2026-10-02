*----------------------------------------------------------------------*
***INCLUDE ZRSD_SIMULADOR_PRECO_IMP_PBO.
*----------------------------------------------------------------------*
*&---------------------------------------------------------------------*
*&      Module  STATUS_9000  OUTPUT
*&---------------------------------------------------------------------*
*       text
*----------------------------------------------------------------------*
MODULE status_9000 OUTPUT.
  SET PF-STATUS 'STATUS_9000'.
  SET TITLEBAR 'TIT9000'.

  IF vg_custom_container IS INITIAL.
**Initializing the grid and calling the fm to Display the O/P
    PERFORM f_create_and_init_alv.
  ENDIF.


ENDMODULE.                 " STATUS_9000  OUTPUT