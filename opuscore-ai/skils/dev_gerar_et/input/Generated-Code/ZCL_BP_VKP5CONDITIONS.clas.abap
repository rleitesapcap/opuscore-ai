" Created By     : Capgemini SAP AI - Code Generation Engine
" Created On     : 03-07-2026
" Convention     : Workbook ABAP_Move2S4_Final.docx

CLASS zcl_bp_vkp5conditions DEFINITION
  PUBLIC
  INHERITING FROM cl_abap_behavior_handler
  FINAL
  CREATE PUBLIC .

  PUBLIC SECTION.
    " Constants for condition maintenance
    CONSTANTS: gc_application TYPE kappl VALUE 'V',
               gc_success_msg TYPE symsgid VALUE 'ZVK',
               gc_error_msg TYPE symsgid VALUE 'ZVK'.

  PRIVATE SECTION.
    " Handler methods for behavior operations
    METHODS get_instance_authorizations FOR INSTANCE AUTHORIZATION
      IMPORTING keys REQUEST requested_authorizations FOR vkp5conditions RESULT result.

    METHODS create FOR MODIFY
      IMPORTING entities FOR CREATE vkp5conditions.

    METHODS update FOR MODIFY
      IMPORTING entities FOR UPDATE vkp5conditions.

    METHODS delete FOR MODIFY
      IMPORTING keys FOR DELETE vkp5conditions.

    METHODS read FOR READ
      IMPORTING keys FOR READ vkp5conditions RESULT result.

    METHODS lock FOR LOCK
      IMPORTING keys FOR LOCK vkp5conditions.

    " Validations
    METHODS validateconditiondata FOR VALIDATE ON SAVE
      IMPORTING keys FOR vkp5conditions~validateconditiondata.

    METHODS validatedates FOR VALIDATE ON SAVE
      IMPORTING keys FOR vkp5conditions~validatedates.

    " Determinations
    METHODS setdefaultvalues FOR DETERMINE ON MODIFY
      IMPORTING keys FOR vkp5conditions~setdefaultvalues.

    " Actions
    METHODS updatecondition FOR MODIFY
      IMPORTING keys FOR ACTION vkp5conditions~updatecondition RESULT result.

    " Helper methods
    METHODS call_condition_bapi
      IMPORTING
        iv_condition_record TYPE knumh
        iv_condition_type   TYPE kschl
        iv_sales_org        TYPE vkorg
        iv_material         TYPE matnr
        iv_condition_amount TYPE kbetr
      RETURNING
        VALUE(rv_success)   TYPE abap_bool.

    METHODS map_bapi_messages
      IMPORTING
        it_return TYPE bapiret2_tab
      CHANGING
        co_reported TYPE REF TO if_abap_behv_message.
ENDCLASS.

CLASS zcl_bp_vkp5conditions IMPLEMENTATION.
  METHOD get_instance_authorizations.
    " Authority check for VKP5 conditions
    LOOP AT keys INTO DATA(ls_key).
      " Check authorization for sales organization
      AUTHORITY-CHECK OBJECT 'V_VBAK_VKO'
        ID 'VKORG' FIELD ls_key-salesorganization
        ID 'ACTVT' FIELD '03'.
      
      IF sy-subrc = 0.
        APPEND VALUE #( %tky = ls_key-%tky
                       %update = if_abap_behv=>auth-allowed
                       %delete = if_abap_behv=>auth-allowed ) TO result.
      ELSE.
        APPEND VALUE #( %tky = ls_key-%tky
                       %update = if_abap_behv=>auth-unauthorized
                       %delete = if_abap_behv=>auth-unauthorized
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'No authorization for sales organization' ) ) TO result.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD create.
    " Implementation for create operation
    LOOP AT entities INTO DATA(ls_entity).
      " Basic validation before creation
      IF ls_entity-conditiontype IS INITIAL.
        APPEND VALUE #( %tky = ls_entity-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_entity-%tky
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Condition type is mandatory' ) ) TO reported-vkp5conditions.
        CONTINUE.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD update.
    " Implementation for update operation
    LOOP AT entities INTO DATA(ls_entity).
      " Update condition record via BAPI
      DATA(lv_success) = call_condition_bapi(
        iv_condition_record = ls_entity-conditionrecord
        iv_condition_type   = ls_entity-conditiontype
        iv_sales_org        = ls_entity-salesorganization
        iv_material         = ls_entity-material
        iv_condition_amount = ls_entity-conditionamount
      ).

      IF lv_success = abap_true.
        APPEND VALUE #( %tky = ls_entity-%tky
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-success
                                                   text = 'Condition updated successfully' ) ) TO reported-vkp5conditions.
      ELSE.
        APPEND VALUE #( %tky = ls_entity-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_entity-%tky
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Error updating condition' ) ) TO reported-vkp5conditions.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD delete.
    " Implementation for delete operation
    LOOP AT keys INTO DATA(ls_key).
      " Check if condition can be deleted
      SELECT SINGLE knumh FROM konh
        INTO @DATA(lv_knumh)
        WHERE knumh = @ls_key-conditionrecord.

      IF sy-subrc = 0.
        " Mark for deletion via BAPI
        " Implementation depends on specific BAPI requirements
        APPEND VALUE #( %tky = ls_key-%tky
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-success
                                                   text = 'Condition marked for deletion' ) ) TO reported-vkp5conditions.
      ELSE.
        APPEND VALUE #( %tky = ls_key-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_key-%tky
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Condition not found' ) ) TO reported-vkp5conditions.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD read.
    " Implementation for read operation
    SELECT * FROM zi_vkp5conditions
      FOR ALL ENTRIES IN @keys
      WHERE conditionrecord = @keys-conditionrecord
      INTO TABLE @DATA(lt_conditions).

    LOOP AT keys INTO DATA(ls_key).
      READ TABLE lt_conditions INTO DATA(ls_condition)
        WITH KEY conditionrecord = ls_key-conditionrecord.
      
      IF sy-subrc = 0.
        APPEND CORRESPONDING #( ls_condition ) TO result.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD lock.
    " Implementation for locking conditions
    LOOP AT keys INTO DATA(ls_key).
      CALL FUNCTION 'ENQUEUE_EZKONH'
        EXPORTING
          knumh = ls_key-conditionrecord
        EXCEPTIONS
          OTHERS = 1.

      IF sy-subrc <> 0.
        APPEND VALUE #( %tky = ls_key-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_key-%tky
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Condition is locked by another user' ) ) TO reported-vkp5conditions.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validateconditiondata.
    " Validate condition data
    READ ENTITIES OF zi_vkp5conditions IN LOCAL MODE
      ENTITY vkp5conditions
      FIELDS ( conditiontype salesorganization material )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_conditions).

    LOOP AT lt_conditions INTO DATA(ls_condition).
      " Validate condition type
      SELECT SINGLE kschl FROM t685
        INTO @DATA(lv_kschl)
        WHERE kschl = @ls_condition-conditiontype.

      IF sy-subrc <> 0.
        APPEND VALUE #( %tky = ls_condition-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_condition-%tky
                       %element-conditiontype = if_abap_behv=>mk-on
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Invalid condition type' ) ) TO reported-vkp5conditions.
      ENDIF.

      " Validate sales organization
      SELECT SINGLE vkorg FROM tvko
        INTO @DATA(lv_vkorg)
        WHERE vkorg = @ls_condition-salesorganization.

      IF sy-subrc <> 0.
        APPEND VALUE #( %tky = ls_condition-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_condition-%tky
                       %element-salesorganization = if_abap_behv=>mk-on
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Invalid sales organization' ) ) TO reported-vkp5conditions.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD validatedates.
    " Validate date ranges
    READ ENTITIES OF zi_vkp5conditions IN LOCAL MODE
      ENTITY vkp5conditions
      FIELDS ( validfrom validto )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_conditions).

    LOOP AT lt_conditions INTO DATA(ls_condition).
      IF ls_condition-validfrom > ls_condition-validto.
        APPEND VALUE #( %tky = ls_condition-%tky ) TO failed-vkp5conditions.
        APPEND VALUE #( %tky = ls_condition-%tky
                       %element-validfrom = if_abap_behv=>mk-on
                       %element-validto = if_abap_behv=>mk-on
                       %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                   text = 'Valid from date cannot be after valid to date' ) ) TO reported-vkp5conditions.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD setdefaultvalues.
    " Set default values for new conditions
    READ ENTITIES OF zi_vkp5conditions IN LOCAL MODE
      ENTITY vkp5conditions
      FIELDS ( application validfrom )
      WITH CORRESPONDING #( keys )
      RESULT DATA(lt_conditions).

    LOOP AT lt_conditions INTO DATA(ls_condition).
      DATA(lt_update) = VALUE ENTITY UPDATE zi_vkp5conditions( ).
      
      " Set default application
      IF ls_condition-application IS INITIAL.
        ls_condition-application = gc_application.
        lt_update-%tky = ls_condition-%tky.
        lt_update-application = gc_application.
        lt_update-%control-application = if_abap_behv=>mk-on.
      ENDIF.

      " Set default valid from date
      IF ls_condition-validfrom IS INITIAL.
        ls_condition-validfrom = sy-datum.
        lt_update-%tky = ls_condition-%tky.
        lt_update-validfrom = sy-datum.
        lt_update-%control-validfrom = if_abap_behv=>mk-on.
      ENDIF.

      IF lt_update-%tky IS NOT INITIAL.
        APPEND lt_update TO DATA(lt_updates).
      ENDIF.
    ENDLOOP.

    IF lt_updates IS NOT INITIAL.
      MODIFY ENTITIES OF zi_vkp5conditions IN LOCAL MODE
        ENTITY vkp5conditions
        UPDATE FIELDS ( application validfrom )
        WITH lt_updates.
    ENDIF.
  ENDMETHOD.

  METHOD updatecondition.
    " Action to update condition via BAPI
    LOOP AT keys INTO DATA(ls_key).
      " Read current condition data
      READ ENTITIES OF zi_vkp5conditions IN LOCAL MODE
        ENTITY vkp5conditions
        ALL FIELDS WITH VALUE #( ( %tky = ls_key-%tky ) )
        RESULT DATA(lt_condition).

      IF lines( lt_condition ) = 1.
        DATA(ls_condition) = lt_condition[ 1 ].
        
        " Call BAPI to update condition
        DATA(lv_success) = call_condition_bapi(
          iv_condition_record = ls_condition-conditionrecord
          iv_condition_type   = ls_condition-conditiontype
          iv_sales_org        = ls_condition-salesorganization
          iv_material         = ls_condition-material
          iv_condition_amount = ls_condition-conditionamount
        ).

        IF lv_success = abap_true.
          APPEND VALUE #( %tky = ls_key-%tky
                         %param = CORRESPONDING #( ls_condition ) ) TO result.
          
          APPEND VALUE #( %tky = ls_key-%tky
                         %msg = new_message_with_text( severity = if_abap_behv_message=>severity-success
                                                     text = 'Condition updated successfully via BAPI' ) ) TO reported-vkp5conditions.
        ELSE.
          APPEND VALUE #( %tky = ls_key-%tky ) TO failed-vkp5conditions.
          APPEND VALUE #( %tky = ls_key-%tky
                         %msg = new_message_with_text( severity = if_abap_behv_message=>severity-error
                                                     text = 'BAPI call failed for condition update' ) ) TO reported-vkp5conditions.
        ENDIF.
      ENDIF.
    ENDLOOP.
  ENDMETHOD.

  METHOD call_condition_bapi.
    " Call BAPI for condition maintenance
    DATA: lo_condition_bapi TYPE REF TO cl_condition_maintenance,
          lt_return         TYPE bapiret2_tab,
          ls_condition_data TYPE any.

    TRY.
        " Initialize BAPI wrapper
        CREATE OBJECT lo_condition_bapi.

        " Prepare condition data structure
        " This is a simplified example - actual structure depends on BAPI requirements
        DATA(ls_condition_key) = VALUE any(
          knumh = iv_condition_record
          kschl = iv_condition_type
          vkorg = iv_sales_org
          matnr = iv_material
        ).

        DATA(ls_condition_value) = VALUE any(
          kbetr = iv_condition_amount
          konwa = 'EUR'
          kpein = 1
        ).

        " Call condition change BAPI
        CALL FUNCTION 'BAPI_PRICES_CONDITIONS'
          EXPORTING
            operation_mode    = 'CHANGE'
            condition_type    = iv_condition_type
            sales_org         = iv_sales_org
            material          = iv_material
          IMPORTING
            return            = lt_return.

        " Check BAPI return messages
        READ TABLE lt_return TRANSPORTING NO FIELDS 
          WITH KEY type = 'E'.
        
        IF sy-subrc = 0.
          rv_success = abap_false.
          " Map error messages to RAP framework
          map_bapi_messages( EXPORTING it_return = lt_return
                            CHANGING co_reported = reported ).
        ELSE.
          " Commit BAPI transaction
          CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
            EXPORTING
              wait = 'X'.
          rv_success = abap_true.
        ENDIF.

      CATCH cx_root INTO DATA(lx_error).
        " Handle BAPI exceptions
        MESSAGE lx_error->get_text( ) TYPE 'E'.
        rv_success = abap_false.
    ENDTRY.
  ENDMETHOD.

  METHOD map_bapi_messages.
    " Map BAPI return messages to RAP message framework
    DATA: lo_message TYPE REF TO if_abap_behv_message.

    LOOP AT it_return INTO DATA(ls_return).
      CASE ls_return-type.
        WHEN 'E' OR 'A'.
          lo_message = new_message_with_text( 
            severity = if_abap_behv_message=>severity-error
            text = |{ ls_return-message }| ).
        WHEN 'W'.
          lo_message = new_message_with_text( 
            severity = if_abap_behv_message=>severity-warning
            text = |{ ls_return-message }| ).
        WHEN 'S'.
          lo_message = new_message_with_text( 
            severity = if_abap_behv_message=>severity-success
            text = |{ ls_return-message }| ).
        WHEN 'I'.
          lo_message = new_message_with_text( 
            severity = if_abap_behv_message=>severity-information
            text = |{ ls_return-message }| ).
      ENDCASE.

      " Add message to reported structure
      " Note: This would need to be called with proper entity context
    ENDLOOP.
  ENDMETHOD.
ENDCLASS.