***********************************************************************
*                                                                     *
*      *********************************************************      *
*      *                +---------------------+                *      *
*      *                | G r u p o | A S S A |                *      *
*      *                +---------------------+                *      *
*      *********************************************************      *
*                                                                     *
***********************************************************************
*---------------------------------------------------------------------*
*** Dados do programa                                                 *
*---------------------------------------------------------------------*
* Nome  : Programa para Seleção dos Parâmetros de HARDCODE            *
* Título: Programa para Seleção dos Parâmetros de HARDCODE            *
* Autor : André Luiz C. de Almeida                                    *
* Data  : 01.10.2012                                                  *
*                                                                     *
* Objetivos: Parametrização de HARDCODE (Header)                      *
*                                                                     *
* Especificação: Desenvolvimento Genérico para o Projeto Retail       *
*                                                                     *
*---------------------------------------------------------------------+
*** Histórico das modificações                                        |
*---+--------+----------------+---------------------------------------+
*Seq|Data    |Autor           |COD/ Descrição da modificação ou erro  |
*---+--------+----------------+---------------------------------------+
*001|01.10.12|André Almeida   | Desenvolvimento Inicial               +
*---+--------+----------------+---------------------------------------+

* Busca os parâmetros de HARDCODE
  DEFINE get_hard.

*   Função para Seleção dos Parâmetros de HARDCODE
        call function 'ZFXX_HARDCODE'
          exporting
            pi_fieldname            = &2
            pi_usage_process        = &1
          tables
            pt_content              = &3
          exceptions
            processo_nao_encontrado = 1
            formato_range_invalido  = 2
            others                  = 3.

        if not sy-subrc is initial.
          append 'ECP*' to &3.
        endif.
  END-OF-DEFINITION.


* Busca a Destination Parametrizada para a RFC Informada
  DEFINE get_destination.

*   Identifica a Destination para a Chamada da RFC
    call function 'ZFXX_DESTINATION'
      exporting
        pi_nome_rfc         = &1
      importing
        pc_destination      = &2
      exceptions
        rfc_nao_encontrada  = 1
        rfc_sem_destination = 2
        others              = 3.

*   Destination "Xpto" para forçar erro em chamada
    if not sy-subrc is initial.
      &2 = 'SEM_DEST_PARAMETRIZADO'.
    endif.

  END-OF-DEFINITION.