*&---------------------------------------------------------------------*
*&  Include           ZRSD_SIMULADOR_PRECO_IMP_TOP
*&---------------------------------------------------------------------*
INCLUDE zexx_hardcode.        " Hardcode

*---------------------------------------------------------------------*
* Declaração: Estrutura(s) de tabela(s)
*---------------------------------------------------------------------*
TABLES: "ztsdd_simuprech,   "Simulação de preço importado - Cabeçalho
  "        ztsdd_simupreci,   "Simulação de preço importado - Item
  ztsdd_precadmat,   "Materiais pré-cadastrados
  ekko,              "Cabeçalho do documento de compra
  ekpo,              "Item do documento de compra
*        t001w,             "Centros/filiais
  calp.              "Cálculo do preço de venda: item de um cálculo de preço

*---------------------------------------------------------------------*
* Declaração: Constante(s)
*---------------------------------------------------------------------*
CONSTANTS: sim(3)        TYPE c VALUE 'SIM',
           mat(3)        TYPE c VALUE 'MAT',
           mpc(3)        TYPE c VALUE 'MPC',
           ped(3)        TYPE c VALUE 'PED',
           all(3)        TYPE c VALUE 'ALL',
           pcb(3)        TYPE c VALUE 'PCB',
*           c_a(1)        TYPE c VALUE 'A',
*           c_zg(2)       TYPE c VALUE 'ZG',
*           c_zd(2)       TYPE c VALUE 'ZD',
           c_back(4)     TYPE c VALUE 'BACK',
           c_exit(4)     TYPE c VALUE 'EXIT',
           c_canc(4)     TYPE c VALUE 'CANC',
*           c_lb01(4)     TYPE c VALUE 'LB01',
*           c_bwkey(4)    TYPE c VALUE 'CD01',
           c_container   TYPE scrfname VALUE 'CONTAINER',
           c_stat_10(30) TYPE c VALUE 'Aguardando aprovação',
           c_stat_20(30) TYPE c VALUE 'Rejeitado',
           c_stat_30(30) TYPE c VALUE 'Aprovado',
           c_stat_00(30) TYPE c VALUE 'Não enviado para aprovação'.

**---------------------------------------------------------------------*
** Declaração: Variável(is)
**---------------------------------------------------------------------*
DATA: "gr_mtart TYPE RANGE OF mtart,
      "gr_bsart TYPE RANGE OF bsart,
      "gr_bstat TYPE RANGE OF bstat,
      "gr_mtorg TYPE RANGE OF j_1bmatorg,
      gr_uname TYPE RANGE OF syst_uname, "<CC.2252> Inclusão IROSA 19.09.2018
      er_uname like line of gr_uname.
DATA: vg_erro(1) TYPE c,
      vg_edit(1) TYPE c,
* Alteração - CD.3723 - 24.01.2020 - Inicio
*      vg_cd_unico TYPE werks_d,
* Alteração - CD.3723 - 24.01.2020 - FIM
      vg_gp      TYPE wyt3-lifn2,             "GP Aprovador
      vg_dgp     TYPE wyt3-lifn2,             "DGP Aprovador
      vg_gpname  TYPE lfa1-name1.            "Nome GP Aprovador
*      vg_dgpname TYPE lfa1-name1.             "Nome DGP Aprovador

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
*      save_ok       LIKE sy-ucomm,
*      vg_container1 TYPE scrfname VALUE 'CONTAINER',
      vg_layout     TYPE lvc_s_layo.
*DATA: v_lines TYPE i.
*DATA: v_line(3) TYPE c.

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

*  BEGIN OF ty_materiais,
*    matnr TYPE mara-matnr,
*    werks TYPE ewerk,
*  END OF ty_materiais,

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

*  BEGIN OF ty_t001w,
*    werks TYPE t001w-werks,            "Centro
*    regio TYPE t001w-regio,            "Região
*  END OF ty_t001w,

*  BEGIN OF ty_gp,
*    lifn2 TYPE wrf_resp,              "GP Aprovador
*  END OF ty_gp,

*  BEGIN OF ty_pcb,
*    werks TYPE werks_d,                  "Centro
*    lifnr TYPE lifnr,                  "Fornecedor
*    matnr TYPE matnr,                  "Material
*    pcb   TYPE ekpgr,                  "PCB
*    land1 TYPE land1_gp,               "Chave do país
*    kpein TYPE kpein,                  "Unidade de preço padrão
*    ebeln TYPE ebeln,                  "Pedido     <002> - Inclusão
*    menge TYPE menge_d,
** Alteração - CD.3723 - 24.01.2020 - Inicio
*    ltsnr TYPE ltsnr,
** Alteração - CD.3723 - 24.01.2020 - FIM
*  END OF ty_pcb,

*  BEGIN OF ty_ekpo,
*    lifnr TYPE ekko-lifnr,             "Fornecedor
*    ebeln TYPE ekpo-ebeln,             "Nº do documento de compras
*    ebelp TYPE ekpo-ebelp,             "Nº item do documento de compra
*    matnr TYPE ekpo-matnr,             "Material
*    werks TYPE ekpo-werks,             "Centro
*    bpumz TYPE ekpo-bpumz,             "Fator de conversão - numerador
*    bpumn TYPE ekpo-bpumn,             "Fator de conversão - Denomimador
*    umrez TYPE ekpo-umrez,             "Fator de conversão - numerador     "<002> - Inclusão
*    umren TYPE ekpo-umren,             "Fator de conversão - Denomimador   "<002> - Inclusão
** Alteração - CD.3723 - 24.01.2020 - Inicio
*    ltsnr TYPE ekpo-ltsnr,
** Alteração - CD.3723 - 24.01.2020 - FIM
*  END OF ty_ekpo,

*  BEGIN OF ty_rseg,
*    belnr TYPE rseg-belnr,             "Documento       <002> - Inclusão
*    gjahr TYPE rseg-gjahr,             "Exercício       <002> - Inclusão
*    buzei TYPE rseg-buzei,             "Item            <002> - Inclusão
*    matnr TYPE rseg-matnr,             "Material
*    werks TYPE rseg-werks,             "Centro
*    wrbtr TYPE rseg-wrbtr,             "Montante
*    menge TYPE rseg-menge,             "Quantidade
** Alteração - CC.1789 - Luiz - 12.06.2018  - Inicio
*    tbtkz TYPE rseg-tbtkz,
*    bnkan TYPE rseg-bnkan,
** Alteração - CC.1789 - Luiz - 12.06.2018  - FIM
*** inicio welber tiburcio 03.01.19
*    ebeln TYPE rseg-ebeln,
*    ebelp TYPE rseg-ebelp,
*** fim welber tiburcio 03.01.19
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Início da Inclusão
*    bstme TYPE rseg-bstme,
*    meins TYPE rseg-meins,
** CC.3029 - Fabiano Bartholomeu - 10.06.2019 - Fim da Inclusão
*  END OF ty_rseg,

*  BEGIN OF ty_eina,
*    lifnr TYPE eina-lifnr,             "Fornecedor
*    matnr TYPE eina-matnr,             "Material
*    werks TYPE eine-werks,             "Centro
*    netpr TYPE eine-netpr,             "Montante
*    peinh TYPE eine-peinh,             "Unidade de preço
** Alteração - CD.3723 - 24.01.2020 - Inicio
*    ltsnr TYPE eina-ltsnr,
** Alteração - CD.3723 - 24.01.2020 - FIM
*  END OF ty_eina,

*  BEGIN OF ty_saida,
*    mark(1)             TYPE c,
*    matnr               TYPE matnr,           "Material
*    maktx               TYPE maktx,           "Descrição Material
*    pltyp               TYPE pltyp,           "Lista Preço,
*    ptext               TYPE text20,          "Descrição lista de preço
*    cod_agrup           TYPE zesd_cod_agrup,  "Código de agrupamento
*    desc_agrup          TYPE zesd_desc_agrup, "Descrição
*    qtde_min            TYPE menge_d,         "Quantidade Mínima
*    vrkme               TYPE w_vrkme_vkp,     "Unidade de Medida
*    pcb                 TYPE ekpgr,           "PCB
*    werks               TYPE ewerk,           "Centro
*    lifnr               TYPE elifn,           "Fornecedor
*    pcl                 TYPE ekpnn,           "PCL
*    pclst               TYPE ekpnn,           "PCL ST
*    preco_transf        TYPE ekpnn,           "Preço Transferência
*    rappel              TYPE kbetr,           "Rappel %
*    custo_log           TYPE kbetr,           "Custo Logistico %
*    pv_liq              TYPE vkpzw,           "PV Liquido
*    pv_fin              TYPE endpr,           "PV Final
*    mg_liq              TYPE wty_kbetr3,      "Margem Líquida %
*    mg_bruta            TYPE wty_kbetr3,      "Margem Bruta %
*    status_i            TYPE zesd_status_i,   "Status aprovação
*    status_i_d(30)      TYPE c,               "Descrição Status Aprovação
*    matprecadx          TYPE c,               "Material pré-cadastrado
*    matnr_ref           TYPE matnr,           "Material referência
*    mat_ref             TYPE flag,            "Possui material de referência
*    matkl               TYPE matkl,           "Tipo de Material
*    vkkab               TYPE vkkab,           "Data
*    werks_to            TYPE ewerk,           "Centro
*    state_from          TYPE regio,           "Região Origem
*    state_to            TYPE regio,           "Região Destino
*    mtuse               TYPE mbew-mtuse,      "Origem
*    mtorg               TYPE mbew-mtorg,      "Utilização
*    steuc               TYPE marc-steuc,      "NCM
*    mwskz               TYPE mwskz,           "Código IVA
*    ebeln               TYPE ebeln,           "Pedido        <002> - Inclusão
*    uf_precad           TYPE zesd_calcula_preco-pi_uf_precad,        "UF material pré-cadastrado
*    rate_icms           TYPE zesd_calcula_preco-pe_rate_icms,        "Rate ICMS
*    base_icms           TYPE zesd_calcula_preco-pe_base_icms,        "Base ICMS
*    cust_icms           TYPE zesd_calcula_preco-pe_cust_icms,        "Custo com ICMS (Calculado)
*    val_icms            TYPE zesd_calcula_preco-pe_val_icms,         "Valor ICMS (Calculado)
*    rate_icms_venda     TYPE zesd_calcula_preco-pe_rate_icms_venda,  "Rate ICMS Venda
*    base_icms_venda     TYPE zesd_calcula_preco-pe_base_icms_venda,  "Base ICMS Venda
*    rate_icms_st        TYPE zesd_calcula_preco-pe_rate_icms_st,     "Rate ICMS ST
*    base_icms_st        TYPE zesd_calcula_preco-pe_base_icms_st,     "Base ICMS ST
*    rate_icms_st_int    TYPE zesd_calcula_preco-pe_rate_icms_st_int, "Rate ICMS ST Interno
*    base_icms_st_int    TYPE zesd_calcula_preco-pe_base_icms_st_int, "Base ICMS ST Interno
*    base_red_1          TYPE zesd_calcula_preco-pe_base_red_1,       "Base Reduzida 1
*    base_red_2          TYPE zesd_calcula_preco-pe_base_red_2,       "Base Reduzida 2
*    val_base_st         TYPE zesd_calcula_preco-pe_val_base_st,      "Valor Base ST (Calculado)
*    val_icms_st         TYPE zesd_calcula_preco-pe_val_icms_st,      "Valor ICMS ST (Calculado)
*    rate_ipi            TYPE zesd_calcula_preco-pe_rate_ipi,         "Rate IPI
*    base_ipi            TYPE zesd_calcula_preco-pe_base_ipi,         "Base IPI
*    val_ipi             TYPE zesd_calcula_preco-pe_val_ipi,          "Valor IPI (Calculado)
*    rate_cofins         TYPE zesd_calcula_preco-pe_rate_cofins,      "Rate COFINS
*    base_cofins         TYPE zesd_calcula_preco-pe_base_cofins,      "Base COFINS
*    val_cofins          TYPE zesd_calcula_preco-pe_val_cofins,       "Valor COFINS (Calculado)
*    rate_pis            TYPE zesd_calcula_preco-pe_rate_pis,         "Rate PIS
*    base_pis            TYPE zesd_calcula_preco-pe_base_pis,         "Base PIS
*    val_pis             TYPE zesd_calcula_preco-pe_val_pis,          "Valor PIS (Calculado)
*    val_rappel          TYPE zesd_calcula_preco-pe_val_rappel,       "Valor Rappel (Calculado)
*    val_custo_log       TYPE zesd_calcula_preco-pe_val_custo_log,    "Valor Custo Logístico (Calculado)
*    total_imp_venda     TYPE zesd_calcula_preco-pe_total_imp_venda,  "Total Imposto de Venda
*    c_mvto              TYPE zesd_calcula_preco-pe_c_mvto,           "Custo movimentação
*    c_pallet            TYPE zesd_calcula_preco-pe_c_pallet,         "Custo Insumo Pallet
*    frete               TYPE zesd_calcula_preco-pe_frete,            "Frete
*    tx_fin              TYPE zesd_calcula_preco-pe_tx_fin,           "Taxa financeira
*    tx_gest             TYPE zesd_calcula_preco-pe_tx_gest,          "Taxa gestão
*    c_arm               TYPE zesd_calcula_preco-pe_c_arm,            "Custo de armazenagem
*    umrez               TYPE zesd_calcula_preco-pe_umrez,            "Qtde RS
*    hoehe               TYPE zesd_calcula_preco-pe_hoehe,            "Altura
*    breit               TYPE zesd_calcula_preco-pe_breit,            "Largura
*    laeng               TYPE zesd_calcula_preco-pe_laeng,            "Comprimento
*    tx_mov              TYPE zesd_calcula_preco-pe_tx_mov,           "Taxa de movimentação
*    tx_frete            TYPE zesd_calcula_preco-pe_tx_frete,         "Taxa de frete
*    custo_ins_pallet    TYPE zesd_calcula_preco-pe_custo_ins_pallet, "Custo insumo pallet
*    dias_est            TYPE zesd_calcula_preco-pe_dias_est,         "Dias de estoque
*    custo_armazen       TYPE zesd_calcula_preco-pe_custo_armazen,    "Custo Armazenagem
*    rate_icms_comp      TYPE zesd_calcula_preco-pe_base_icms_comp,   "Rate ICMS Compra
*    base_icms_comp      TYPE zesd_calcula_preco-pe_base_icms_comp,   "Base ICMS Compra
*    val_icms_comp       TYPE zesd_calcula_preco-pe_val_icms_comp,    "Valor ICMS Compra
*    rate_ipi_comp       TYPE zesd_calcula_preco-pe_rate_ipi_comp,    "Rate IPI Compra
*    base_ipi_comp       TYPE zesd_calcula_preco-pe_base_ipi_comp,    "Base IPI Compra
*    val_ipi_comp        TYPE zesd_calcula_preco-pe_val_ipi_comp,     "Valor IPI Compra
*    rate_cofins_comp    TYPE zesd_calcula_preco-pe_rate_cofins_comp, "Rate COFINS Compra
*    base_cofins_comp    TYPE zesd_calcula_preco-pe_base_cofins_comp, "Base COFINS Compra
*    val_cofins_comp     TYPE zesd_calcula_preco-pe_val_cofins_comp,  "Valor COFINS Compra
*    rate_pis_comp       TYPE zesd_calcula_preco-pe_rate_pis_comp,    "Rate PIS Compra
*    base_pis_comp       TYPE zesd_calcula_preco-pe_base_pis_comp,    "Base PIS Compra
*    val_pis_comp        TYPE zesd_calcula_preco-pe_val_pis_comp,     "Valor PIS Compra
*    calc_base_st_comp   TYPE zesd_calcula_preco-pe_calc_base_st_comp, "Base ST Compra
*    calc_icms_st_comp   TYPE zesd_calcula_preco-pe_calc_icms_st_comp, "ICMS ST Compra
*    rate_icms_st_comp   TYPE zesd_calcula_preco-pe_rate_icms_st_comp, "Rate ICMS ST Compra
*    rate_st_int_comp    TYPE zesd_calcula_preco-pe_rate_st_int_comp , "Rate ICMS ST Interno Compra
*    maj_bst_comp        TYPE zesd_calcula_preco-pe_maj_bst_comp,      "MAJ BST Compra
*    maj_bicms_comp      TYPE zesd_calcula_preco-pe_maj_bicms_comp,    "MAJ BICMS Compra
*    calc_pis_st_comp    TYPE zesd_calcula_preco-pe_calc_pis_st_comp,  "PIS ST Compra
*    calc_cofins_st_comp TYPE zesd_calcula_preco-pe_calc_cofins_st_comp, "COFINS ST Compra
*    gestao              TYPE zesd_calcula_preco-pe_gestao,             "Valor Gestão Custo Logístico
*    tx_desp             TYPE zesd_calcula_preco-pe_tx_desp,            "Taxa Despachante Custo Logístico
*    tx_fob              TYPE zesd_calcula_preco-pe_tx_fob,             "Taxa FOB Custo Logístico
*    fob                 TYPE zesd_calcula_preco-pe_fob,               "FOB
*    despachante         TYPE zesd_calcula_preco-pe_despachante,       "Despachante
*    fin                 TYPE zesd_calcula_preco-pe_fin,               "Financeira
*    color_cell          TYPE lvc_t_scol,      "Cell color
** Alteração - CD.3723 - 24.01.2020 - Inicio
*    var_cust_log        TYPE zesd_calcula_preco-pe_var_cust_log,
*    werks_ori           TYPE werks_d,
*    ltsnr               TYPE ltsnr,
** Alteração - CD.3723 - 24.01.2020 - FIM
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*    celltab             TYPE lvc_t_styl,
** Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM.
*  END OF ty_saida,

*  BEGIN OF ty_impostos,
*    matnr               TYPE matnr,                                  "Material
*    werks               TYPE ewerk,                                  "Centro
*    ptext               TYPE text20,                                 "Descrição lista de preço
*    state_from          TYPE regio,                                  "Região Origem
*    state_to            TYPE regio,                                  "Região Destino
*    mwskz               TYPE mwskz,                                  "Código IVA
*    text1               TYPE text1_007s,                             "Descrição IVA
*    rate_icms           TYPE zesd_calcula_preco-pe_rate_icms,        "Rate ICMS
*    base_icms           TYPE zesd_calcula_preco-pe_base_icms,        "Base ICMS
*    rate_icms_venda     TYPE zesd_calcula_preco-pe_rate_icms,        "Rate ICMS
*    base_icms_venda     TYPE zesd_calcula_preco-pe_base_icms,        "Base ICMS
*    cust_icms           TYPE zesd_calcula_preco-pe_cust_icms,        "Custo com ICMS (Calculado)
*    val_icms            TYPE zesd_calcula_preco-pe_val_icms,         "Valor ICMS (Calculado)
*    rate_icms_st        TYPE zesd_calcula_preco-pe_rate_icms_st,     "Rate ICMS ST
*    base_icms_st        TYPE zesd_calcula_preco-pe_base_icms_st,     "Base ICMS ST
*    rate_icms_st_int    TYPE zesd_calcula_preco-pe_rate_icms_st_int, "Rate ICMS ST Interno
*    base_icms_st_int    TYPE zesd_calcula_preco-pe_base_icms_st_int, "Base ICMS ST Interno
*    base_red_1          TYPE zesd_calcula_preco-pe_base_red_1,       "Base Reduzida 1
*    base_red_2          TYPE zesd_calcula_preco-pe_base_red_2,       "Base Reduzida 2
*    val_base_st         TYPE zesd_calcula_preco-pe_val_base_st,      "Valor Base ST (Calculado)
*    val_icms_st         TYPE zesd_calcula_preco-pe_val_icms_st,      "Valor ICMS ST (Calculado)
*    rate_ipi            TYPE zesd_calcula_preco-pe_rate_ipi,         "Rate IPI
*    base_ipi            TYPE zesd_calcula_preco-pe_base_ipi,         "Base IPI
*    val_ipi             TYPE zesd_calcula_preco-pe_val_ipi,          "Valor IPI (Calculado)
*    rate_cofins         TYPE zesd_calcula_preco-pe_rate_cofins,      "Rate COFINS
*    base_cofins         TYPE zesd_calcula_preco-pe_base_cofins,      "Base COFINS
*    val_cofins          TYPE zesd_calcula_preco-pe_val_cofins,       "Valor COFINS (Calculado)
*    rate_pis            TYPE zesd_calcula_preco-pe_rate_pis,         "Rate PIS
*    base_pis            TYPE zesd_calcula_preco-pe_base_pis,         "Base PIS
*    val_pis             TYPE zesd_calcula_preco-pe_val_pis,          "Valor PIS (Calculado)
*    val_rappel          TYPE zesd_calcula_preco-pe_val_rappel,       "Valor Rappel (Calculado)
*    val_custo_log       TYPE zesd_calcula_preco-pe_val_custo_log,    "Valor Custo Logístico (Calculado)
*    total_imp_venda     TYPE zesd_calcula_preco-pe_total_imp_venda,  "Total Imposto de Venda
*    rate_icms_comp      TYPE zesd_calcula_preco-pe_base_icms_comp,   "Rate ICMS Compra
*    base_icms_comp      TYPE zesd_calcula_preco-pe_base_icms_comp,   "Base ICMS Compra
*    val_icms_comp       TYPE zesd_calcula_preco-pe_val_icms_comp,    "Valor ICMS Compra
*    rate_ipi_comp       TYPE zesd_calcula_preco-pe_rate_ipi_comp,    "Rate IPI Compra
*    base_ipi_comp       TYPE zesd_calcula_preco-pe_base_ipi_comp,    "Base IPI Compra
*    val_ipi_comp        TYPE zesd_calcula_preco-pe_val_ipi_comp,     "Valor IPI Compra
*    rate_cofins_comp    TYPE zesd_calcula_preco-pe_rate_cofins_comp, "Rate COFINS Compra
*    base_cofins_comp    TYPE zesd_calcula_preco-pe_base_cofins_comp, "Base COFINS Compra
*    val_cofins_comp     TYPE zesd_calcula_preco-pe_val_cofins_comp,  "Valor COFINS Compra
*    rate_pis_comp       TYPE zesd_calcula_preco-pe_rate_pis_comp,    "Rate PIS Compra
*    base_pis_comp       TYPE zesd_calcula_preco-pe_base_pis_comp,    "Base PIS Compra
*    val_pis_comp        TYPE zesd_calcula_preco-pe_val_pis_comp,     "Valor PIS Compra
*    calc_base_st_comp   TYPE zesd_calcula_preco-pe_calc_base_st_comp, "Base ST Compra
*    calc_icms_st_comp   TYPE zesd_calcula_preco-pe_calc_icms_st_comp, "ICMS ST Compra
*    rate_icms_st_comp   TYPE zesd_calcula_preco-pe_rate_icms_st_comp, "Rate ICMS ST Compra
*    maj_bst_comp        TYPE zesd_calcula_preco-pe_maj_bst_comp,      "MAJ BST Compra
*    maj_bicms_comp      TYPE zesd_calcula_preco-pe_maj_bicms_comp,    "MAJ BICMS Compra
*    calc_pis_st_comp    TYPE zesd_calcula_preco-pe_calc_pis_st_comp,  "PIS ST Compra
*    calc_cofins_st_comp TYPE zesd_calcula_preco-pe_calc_cofins_st_comp, "COFINS ST Compra
*    rate_st_int_comp    TYPE zesd_calcula_preco-pe_rate_st_int_comp , "Rate ICMS ST Interno Compra
*    uf_precad           TYPE zesd_calcula_preco-pi_uf_precad,          "UF Materail pré-cadastrado
*    gestao              TYPE zesd_calcula_preco-pe_gestao,            "Valor Gestão Custo Logístico
*    tx_desp             TYPE zesd_calcula_preco-pe_tx_desp,           "Taxa Despachante Custo Logístico
*    tx_fob              TYPE zesd_calcula_preco-pe_tx_fob,            "Taxa FOB Custo Logístico
*    fob                 TYPE zesd_calcula_preco-pe_fob,               "FOB
*    despachante         TYPE zesd_calcula_preco-pe_despachante,       "Despachante
*    fin                 TYPE zesd_calcula_preco-pe_fin,               "Financeira
** Alteração - CD.3723 - 24.01.2020 - Inicio
*    var_cust_log        TYPE zesd_calcula_preco-pe_var_cust_log,
** Alteração - CD.3723 - 24.01.2020 - FIM
*  END OF ty_impostos,

*  BEGIN OF ty_val_c_log,
*    matnr            TYPE matnr,                                  "Material
*    werks            TYPE ewerk,                                  "Centro
*    pcl              TYPE ekpnn,                                  "PCL
*    c_mvto           TYPE zesd_calcula_preco-pe_c_mvto,           "Custo movimentação
*    c_pallet         TYPE zesd_calcula_preco-pe_c_pallet,         "Custo Insumo Pallet
*    frete            TYPE zesd_calcula_preco-pe_frete,            "Frete
*    tx_fin           TYPE zesd_calcula_preco-pe_tx_fin,           "Taxa financeira
*    tx_gest          TYPE zesd_calcula_preco-pe_tx_gest,          "Taxa gestão
*    c_arm            TYPE zesd_calcula_preco-pe_c_arm,            "Custo de armazenagem
*    umrez            TYPE zesd_calcula_preco-pe_umrez,            "Qtde RS
*    hoehe            TYPE zesd_calcula_preco-pe_hoehe,            "Altura
*    breit            TYPE zesd_calcula_preco-pe_breit,            "Largura
*    laeng            TYPE zesd_calcula_preco-pe_laeng,            "Comprimento
*    tx_mov           TYPE zesd_calcula_preco-pe_tx_mov,           "Taxa de movimentação
*    tx_frete         TYPE zesd_calcula_preco-pe_tx_frete,         "Taxa de frete
*    custo_ins_pallet TYPE zesd_calcula_preco-pe_custo_ins_pallet, "Custo insumo pallet
*    dias_est         TYPE zesd_calcula_preco-pe_dias_est,         "Dias de estoque
*    custo_armazen    TYPE zesd_calcula_preco-pe_custo_armazen,    "Custo Armazenagem
*    gestao           TYPE zesd_calcula_preco-pe_gestao,            "Valor Gestão Custo Logístico
*    tx_desp          TYPE zesd_calcula_preco-pe_tx_desp,           "Taxa Despachante Custo Logístico
*    tx_fob           TYPE zesd_calcula_preco-pe_tx_fob,            "Taxa FOB Custo Logístico
*    fob              TYPE zesd_calcula_preco-pe_fob,               "FOB
*    despachante      TYPE zesd_calcula_preco-pe_despachante,       "Despachante
*    fin              TYPE zesd_calcula_preco-pe_fin,               "Financeira
*  END OF ty_val_c_log,

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

*** inicio welber tiburcio 03.01.19
*  BEGIN OF ty_a017,
*    lifnr TYPE a017-lifnr,
*    matnr TYPE a017-matnr,
*    werks TYPE a017-werks,
*    knumh TYPE a017-knumh,
*  END OF ty_a017,
*
*  BEGIN OF ty_lfa1,
*    lifnr TYPE lfa1-lifnr,
*    land1 TYPE lfa1-land1,
*  END OF ty_lfa1,

*  BEGIN OF ty_konp,
*    knumh TYPE konp-knumh,
*    kbetr TYPE konp-kbetr,
*    kpein TYPE konp-kpein,
*  END OF ty_konp.
** fim welber tiburcio 03.01.19

* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
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
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
* Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*TYPES: BEGIN OF ty_node,
*         matnr TYPE wrf_matgrp_sku-matnr,
*         node  TYPE wrf_matgrp_sku-node,
*       END OF ty_node.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM

*---------------------------------------------------------------------*
* Declaração: Estrutura(s)
*---------------------------------------------------------------------*
DATA:
  eg_twkao     TYPE ty_twkao,
*  eg_materiais TYPE ty_materiais,
  eg_mara      TYPE ty_mara,
*  eg_precadmat TYPE ztsdd_precadmat,
  eg_dados     TYPE zesd_calcula_preco,
  eg_simuprech TYPE ztsdd_simuprech,
  eg_simupreci TYPE ztsdd_simupreci,
*  eg_impostos  TYPE ty_impostos,
  eg_impostos  TYPE zssd_mon_imp_impostos,
  eg_pcl       TYPE ty_pcl,
*  eg_val_c_log TYPE ty_val_c_log,
  eg_change    TYPE ty_change,
*  eg_t001w     TYPE ty_t001w,
*  eg_t001w_a   TYPE ty_t001w,
*  eg_gp        TYPE ty_gp,
*  eg_pcb       TYPE ty_pcb,
*  eg_ekpo      TYPE ty_ekpo,
*  eg_rseg      TYPE ty_rseg,
*  eg_eina      TYPE ty_eina,
  eg_saida     TYPE zssd_mon_imp_saida,
*  eg_saida     TYPE ty_saida,
  eg_fieldcat  TYPE lvc_s_fcat,
*  x_fieldcat   TYPE lvc_s_fcat,
  eg_vari      TYPE disvariant,
*  eg_rows      TYPE lvc_s_row,
*  eg_excluding TYPE ui_functions,
*  eg_color     TYPE lvc_s_scol,
  eg_mat_pop   TYPE ty_mat_pop,
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  eg_saida_rel TYPE ty_saida_rel,
  eg_simupreca TYPE ztsdd_simupreca,
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
  eg_t007s     TYPE ty_t007s.
** inicio welber tiburcio 03.01.19
*  eg_a017      TYPE ty_a017.
*  eg_lfa1      TYPE ty_lfa1,
*  eg_konp      TYPE ty_konp.
** fim welber tiburcio 03.01.19.

*---------------------------------------------------------------------*
* Declaração: Tabela(s) Interna(s)
*---------------------------------------------------------------------*
DATA:
  tg_twkao     TYPE TABLE OF ty_twkao,
*  tg_materiais     TYPE TABLE OF ty_materiais,
  tg_mara      TYPE TABLE OF ty_mara,
*  tg_precadmat     TYPE TABLE OF ztsdd_precadmat,
*  tg_precadmat_aux TYPE TABLE OF ztsdd_precadmat,
  tg_dados     TYPE TABLE OF zesd_calcula_preco,
  tg_simuprech TYPE TABLE OF ztsdd_simuprech,
  tg_simupreci TYPE TABLE OF ztsdd_simupreci,
*  tg_impostos      TYPE TABLE OF ty_impostos,
  tg_impostos  TYPE zcsd_mon_imp_impostos,
  tg_pcl       TYPE TABLE OF ty_pcl,
*  tg_val_c_log TYPE TABLE OF ty_val_c_log,
  tg_change    TYPE TABLE OF ty_change,
*  tg_t001w         TYPE TABLE OF ty_t001w,
*  tg_gp            TYPE TABLE OF ty_gp,
*  tg_pcb           TYPE TABLE OF ty_pcb,
*  tg_ekpo          TYPE TABLE OF ty_ekpo,
*  tg_rseg          TYPE TABLE OF ty_rseg,
*  tg_eina          TYPE TABLE OF ty_eina,
  tg_saida     TYPE TABLE OF zssd_mon_imp_saida,
*  tg_saida         TYPE TABLE OF ty_saida,
* Alteração - PR.08863 - 02.09.2022 - Inicio
  tg_listas    TYPE TABLE OF ztsdd_listas_p,
* Alteração - PR.08863 - 02.09.2022 - FIM
  tg_fieldcat  TYPE TABLE OF lvc_s_fcat,
*  tg_color         TYPE TABLE OF lvc_s_scol,
*  tg_rows          TYPE lvc_t_row,
  tg_mat_pop   TYPE TABLE OF ty_mat_pop,
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
  tg_saida_rel TYPE TABLE OF ty_saida_rel,
  tg_simupreca TYPE TABLE OF ztsdd_simupreca,
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
  tg_t007s     TYPE TABLE OF ty_t007s.
** inicio welber tiburcio 03.01.19
*  tg_a017          TYPE TABLE OF ty_a017,
*  tg_lfa1          TYPE TABLE OF ty_lfa1.
*  tg_konp          TYPE TABLE OF ty_konp.
** fim welber tiburcio 03.01.19.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*  tg_node          TYPE TABLE OF ty_node,
*  eg_node          TYPE ty_node.
*  tg_revionics     TYPE TABLE OF ztsdc0001.
* Alteração - CC.3169 - 23.07.2019 10:27:12 - FIM
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
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
            rb_aut TYPE c RADIOBUTTON GROUP g1.                                 "Relatorio Precificação.
* Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fi
SELECTION-SCREEN: END OF BLOCK b1.

SELECTION-SCREEN: BEGIN OF BLOCK b2 WITH FRAME TITLE TEXT-002.
PARAMETERS: p_docsim TYPE ztsdd_simuprech-docsim  MODIF ID sim .                "Documento de Simulação

SELECT-OPTIONS: so_ebeln  FOR ekko-ebeln MODIF ID ped NO INTERVALS NO-EXTENSION,   "Nº do Pedido
                so_matnr  FOR calp-matnr MODIF ID mat,                             "Nº do Material
                so_mati   FOR ztsdd_precadmat-matnr MODIF ID mpc.                  "Nº Material pré cadastrado
PARAMETERS:  p_cagrp  TYPE ztsdd_cod_agrup-cod_agrup MODIF ID mpc.                 "Código de agrupamento
SELECTION-SCREEN: END OF BLOCK b2.

SELECTION-SCREEN: BEGIN OF BLOCK b3 WITH FRAME TITLE TEXT-003 .
*PARAMETERS: rb_cad TYPE c RADIOBUTTON GROUP g2  MODIF ID pcb,       "PCB do cadastro
PARAMETERS: rb_cad TYPE c RADIOBUTTON GROUP g2  MODIF ID pcb,       "PCB do cadastro
            rb_upo TYPE c RADIOBUTTON GROUP g2  MODIF ID pcb DEFAULT 'X'.                   "PCB do último pedido
SELECTION-SCREEN: END OF BLOCK b3.

SELECTION-SCREEN: BEGIN OF BLOCK b4 WITH FRAME TITLE TEXT-004.
PARAMETERS: p_vkorg TYPE calp-vkorg MODIF ID all DEFAULT 'LB01',      "Organização de vendas
            p_vtweg TYPE calp-vtweg MODIF ID all DEFAULT '10'.        "Canal de distribuição
* Alteração - PR.09951 - 12.07.2023 - Inicio
*SELECT-OPTIONS: so_werks FOR ekpo-werks MODIF ID all,                 "Centro de Compra
SELECT-OPTIONS: so_werks FOR ekpo-werks MODIF ID all no INTERVALS no-EXTENSION, "Centro de Compra
* Alteração - PR.09951 - 12.07.2023 - FIM.
                so_pltyp FOR calp-pltyp MODIF ID all,                 "Lista de preços
                so_vkkab FOR calp-vkkab MODIF ID all.                 "Validade
SELECTION-SCREEN: END OF BLOCK b4.

*---------------------------------------------------------------------*
*       CLASS lcl_event_handler DEFINITION
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
*                    FOR EVENT menu_button OF cl_gui_alv_grid
*        IMPORTING e_object e_ucomm,

      " -- User Command --
      handle_user_command
                    FOR EVENT user_command OF cl_gui_alv_grid
        IMPORTING e_ucomm,

      " -- Hotspot --
*      handle_hotspot
*                    FOR EVENT hotspot_click OF cl_gui_alv_grid
*        IMPORTING e_column_id
*                    e_row_id
*                    es_row_no,

      " -- Top-of-Page --
      handle_top_of_page
        FOR EVENT top_of_page OF cl_gui_alv_grid,
*        IMPORTING e_dyndoc_id,

      handle_data_changed
        FOR EVENT data_changed OF cl_gui_alv_grid,
*        IMPORTING er_data_changed,

      handle_data_changed_finished
            FOR EVENT data_changed_finished OF cl_gui_alv_grid
        IMPORTING
*            e_modified
            et_good_cells.

ENDCLASS.                    "lcl_event_handler DEFINITION

**---------------------------------------------------------------------*
**       CLASS lcl_event_handler IMPLEMENTATION
**---------------------------------------------------------------------*
*CLASS lcl_event_handler IMPLEMENTATION.
*
*  METHOD handle_toolbar.
*
*    CONSTANTS: cl_bt_set     TYPE ui_func VALUE 'BT_SET',
*               cl_bt_set_pcb TYPE ui_func VALUE 'BT_SET_PCB',
*               cl_bt_comp    TYPE ui_func VALUE 'BT_COMP',
*               cl_bt_c_log   TYPE ui_func VALUE 'BT_C_LOG',
*               cl_bt_rappel  TYPE ui_func VALUE 'BT_RAPPEL',
*               cl_bt_transf  TYPE ui_func VALUE 'BT_TRANSF',
*               cl_bt_venda   TYPE ui_func VALUE 'BT_VENDA',
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*               cl_bt_rep     TYPE ui_func VALUE 'BT_REP'.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim.
*
*    DATA el_toolbar  TYPE stb_button.
*
**- Adicionar um separador no menu do ALV.
*    CLEAR el_toolbar.
*    el_toolbar-butn_type = 3.
*    APPEND el_toolbar TO e_object->mt_toolbar.
**
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*    IF rb_aut = abap_false.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
*
**- Adicionar botões:
*      IF vg_edit IS NOT INITIAL.
** Alteração - CC.2279 - Luiz - 26.10.2018 15:47:13 - Inicio
**        CLEAR el_toolbar.
**        el_toolbar-function = cl_bt_set_pcb.
**        el_toolbar-quickinfo = text-009.
**        el_toolbar-text = text-009.
**        el_toolbar-disabled = ''.
**        APPEND el_toolbar TO e_object->mt_toolbar.
** Alteração - CC.2279 - Luiz - 26.10.2018 15:47:13 - fim
*
** Alteração - CC.2373 - Fabiano Bartholomeu - 26.10.2018 - Inicio
*        IF  rb_mpc IS NOT INITIAL.
*          CLEAR el_toolbar.
*          el_toolbar-function = cl_bt_set_pcb.
*          el_toolbar-quickinfo = TEXT-009.
*          el_toolbar-text = TEXT-009.
*          el_toolbar-disabled = ''.
*          APPEND el_toolbar TO e_object->mt_toolbar.
*        ENDIF.
** Alteração - CC.2373 - Fabiano Bartholomeu - 12.12.2018 - Fim
*
*        CLEAR el_toolbar.
*        el_toolbar-function = cl_bt_rappel.
*        el_toolbar-quickinfo = TEXT-012.
*        el_toolbar-text = TEXT-012.
*        el_toolbar-disabled = ''.
*        APPEND el_toolbar TO e_object->mt_toolbar.
*
*        CLEAR el_toolbar.
*        el_toolbar-function = cl_bt_set.
*        el_toolbar-quickinfo = TEXT-008.
*        el_toolbar-text = TEXT-008.
*        el_toolbar-disabled = ''.
*        APPEND el_toolbar TO e_object->mt_toolbar.
*      ENDIF.
*
*      CLEAR el_toolbar.
*      el_toolbar-function = cl_bt_c_log.
*      el_toolbar-quickinfo = TEXT-011.
*      el_toolbar-text = TEXT-011.
*      el_toolbar-disabled = ''.
*      APPEND el_toolbar TO e_object->mt_toolbar.
*
*      CLEAR el_toolbar.
*      el_toolbar-function = cl_bt_comp.
*      el_toolbar-quickinfo = TEXT-010.
*      el_toolbar-text = TEXT-010.
*      el_toolbar-disabled = ''.
*      APPEND el_toolbar TO e_object->mt_toolbar.
*
*      CLEAR el_toolbar.
*      el_toolbar-function = cl_bt_transf.
*      el_toolbar-quickinfo = TEXT-013.
*      el_toolbar-text = TEXT-013.
*      el_toolbar-disabled = ''.
*      APPEND el_toolbar TO e_object->mt_toolbar.
*
*      CLEAR el_toolbar.
*      el_toolbar-function = cl_bt_venda.
*      el_toolbar-quickinfo = TEXT-014.
*      el_toolbar-text = TEXT-014.
*      el_toolbar-disabled = ''.
*      APPEND el_toolbar TO e_object->mt_toolbar.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*    ELSE.
*      CLEAR el_toolbar.
*      el_toolbar-function = cl_bt_rep.
*      el_toolbar-quickinfo = TEXT-015.
*      el_toolbar-text = TEXT-015.
*      el_toolbar-disabled = ''.
*      APPEND el_toolbar TO e_object->mt_toolbar.
*    ENDIF.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
*  ENDMETHOD.
*
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
*
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
*
*  METHOD  handle_user_command.
*    DATA: tl_columns    TYPE lvc_t_col,
*          el_columns    TYPE LINE OF lvc_t_col,
*          tl_index_rows TYPE lvc_t_row,
*          el_index_rows TYPE LINE OF lvc_t_row,
*          tl_row_no     TYPE lvc_t_roid,
*          el_row_no     TYPE LINE OF lvc_t_roid,
*          vl_value(132) TYPE c,
*          vl_calc       TYPE c,
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*          vl_retorno    TYPE ztsdd_simupreca-msg_autom,
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM.
*          vl_tabix      TYPE sy-tabix.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*    DATA: el_celltab      TYPE lvc_s_styl.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - fim
*    IF e_ucomm EQ 'BT_SET' OR
*       e_ucomm EQ 'BT_RAPPEL'.
*
*      IF e_ucomm NE 'BT_RAPPEL'.
**   Obtém a coluna selecionada
*        CALL METHOD vg_grid->get_selected_columns
*          IMPORTING
*            et_index_columns = tl_columns.
*
*        DELETE tl_columns WHERE fieldname NE 'QTDE_MIN'
*                            AND fieldname NE 'PV_FIN'.
*      ELSE.
*        el_columns-fieldname = 'RAPPEL'.
*        APPEND el_columns TO tl_columns.
*      ENDIF.
*
*      IF tl_columns[] IS NOT INITIAL.
*
*        "Verificar material a ser alterado
*        PERFORM f_seleciona_material_centro.
*
*        IF tg_mat_pop[] IS NOT INITIAL.
*          "Exibir popup para definição de valor
*          LOOP AT tl_columns INTO el_columns.
*
*            CALL FUNCTION 'FOBU_POPUP_GET_VALUE'
*              EXPORTING
*                tablename         = 'ZTSDD_SIMUPRECI'
*                fieldname         = el_columns-fieldname
*              IMPORTING
*                field_value_int_c = vl_value
*              EXCEPTIONS
*                internal_error    = 1
*                cancelled         = 2
*                OTHERS            = 3.
*            IF sy-subrc NE 0.
*              CLEAR vl_value.
*            ENDIF.
*            IF vl_value IS NOT INITIAL.
*              LOOP AT tg_mat_pop INTO eg_mat_pop.
*                LOOP AT tg_saida INTO eg_saida WHERE matnr = eg_mat_pop-matnr
*                                                 AND werks = eg_mat_pop-werks.
*                  vl_tabix = sy-tabix.
*                  CASE el_columns-fieldname.
*                    WHEN 'QTDE_MIN'.
*                      eg_saida-qtde_min = vl_value.
*                    WHEN 'RAPPEL'.
*                      eg_saida-rappel = vl_value.
*                      vl_calc = abap_true.
*                    WHEN 'PV_FIN'.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - Inicio
*                      READ TABLE eg_saida-celltab INTO el_celltab INDEX 1.
*                      IF sy-subrc EQ 0.
*                        IF el_celltab-style = cl_gui_alv_grid=>mc_style_disabled.
*                          CONTINUE.
*                        ENDIF.
*                      ENDIF.
** Alteração - CC.3169 - 23.07.2019 10:27:12 - fim
*                      eg_saida-pv_fin = vl_value.
*                      "Converter para preço psicológico
*                      CALL FUNCTION 'PRICE_POINT_READ'
*                        EXPORTING
*                          pi_vkorg                   = 'LB01'
*                          pi_vtweg                   = '10'
*                          pi_rktyp                   = 'A'
*                          pi_eprgr                   = 'ZLMB01'
*                          pi_price                   = eg_saida-pv_fin
*                          pi_waers                   = 'BRL'
*                          pi_datam                   = sy-datum
*                          pi_kurst                   = 'M'
*                          pi_hwaer                   = 'BRL'
*                          pi_mfact                   = '1'
*                        IMPORTING
*                          pe_price                   = eg_saida-pv_fin
*                        EXCEPTIONS
*                          no_price_point_group_found = 1
*                          no_price_points_maintained = 2
*                          conversion_not_found       = 3
*                          OTHERS                     = 4.
*                      IF sy-subrc EQ 0.
*                        vl_calc = abap_true.
*                      ENDIF.
*                  ENDCASE.
*                  MODIFY tg_saida FROM eg_saida INDEX vl_tabix.
*                ENDLOOP.
*              ENDLOOP.
*            ENDIF.
*          ENDLOOP.
*
*
*          IF vl_calc IS NOT INITIAL.
*            " Efetuar cálculos com os novos valores
*            REFRESH tg_dados.
*
*            LOOP AT tg_mat_pop INTO eg_mat_pop.
*              LOOP AT tg_saida INTO eg_saida WHERE matnr = eg_mat_pop-matnr
*                                               AND werks = eg_mat_pop-werks.
*
*                "Preparar dados para cálculo
*                eg_dados-pi_matprecadx = eg_saida-matprecadx.
*                eg_dados-pi_matnr      = eg_saida-matnr.
*                eg_dados-pi_matnr_ref  = eg_saida-matnr_ref.
*                eg_dados-pi_mat_ref    = eg_saida-mat_ref.
*                eg_dados-pi_matkl      = eg_saida-matkl.
*                eg_dados-pi_werks      = eg_saida-werks.
*                eg_dados-pi_werks_to   = eg_saida-werks_to.
*                eg_dados-pi_vkkab      = eg_saida-vkkab.
*                eg_dados-pi_tipo       = '1'.
*                eg_dados-pi_state_from = eg_saida-state_from.
*                eg_dados-pi_state_to   = eg_saida-state_to.
*                eg_dados-pi_mtuse      = eg_saida-mtuse.
*                eg_dados-pi_mtorg      = eg_saida-mtorg.
*                eg_dados-pi_steuc      = eg_saida-steuc.
*                eg_dados-pi_pcb        = eg_saida-pcb.
*                eg_dados-pe_pcl        = eg_saida-pcl.
*                eg_dados-pe_pclst      = eg_saida-pclst.
*                eg_dados-pi_pclx       = space.
*                eg_dados-pi_mwskz      = eg_saida-mwskz.
*                eg_dados-pi_pvfin      = eg_saida-pv_fin.
*                eg_dados-pi_rappel     = eg_saida-rappel.
*                eg_dados-pi_index      = sy-tabix.
*                eg_dados-pi_uf_precad  = eg_saida-uf_precad.
*
*                "Manter dados de compra
*                eg_dados-pe_rate_icms_comp      =  eg_saida-rate_icms_comp.
*                eg_dados-pe_base_icms_comp      =  eg_saida-base_icms_comp.
*                eg_dados-pe_val_icms_comp       =  eg_saida-val_icms_comp.
*                eg_dados-pe_rate_ipi_comp       =  eg_saida-rate_ipi_comp.
*                eg_dados-pe_base_ipi_comp       =  eg_saida-base_ipi_comp.
*                eg_dados-pe_val_ipi_comp        =  eg_saida-val_ipi_comp.
*                eg_dados-pe_rate_cofins_comp    =  eg_saida-rate_cofins_comp.
*                eg_dados-pe_base_cofins_comp    =  eg_saida-base_cofins_comp.
*                eg_dados-pe_val_cofins_comp     =  eg_saida-val_cofins_comp.
*                eg_dados-pe_rate_pis_comp       =  eg_saida-rate_pis_comp.
*                eg_dados-pe_base_pis_comp       =  eg_saida-base_pis_comp.
*                eg_dados-pe_val_pis_comp        =  eg_saida-val_pis_comp.
*                eg_dados-pe_calc_base_st_comp   =  eg_saida-calc_base_st_comp.
*                eg_dados-pe_calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
*                eg_dados-pe_maj_bst_comp        =  eg_saida-maj_bst_comp.
*                eg_dados-pe_maj_bicms_comp      =  eg_saida-maj_bicms_comp.
*                eg_dados-pe_calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
*                eg_dados-pe_calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
*                eg_dados-pe_rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
*                eg_dados-pe_rate_st_int_comp    =  eg_saida-rate_st_int_comp.
*
*                APPEND eg_dados TO tg_dados.
*              ENDLOOP.
*            ENDLOOP.
*
*            IF tg_dados[] IS NOT INITIAL.
*              READ TABLE tg_dados INTO eg_dados INDEX 1.    "FB23112018
*              CALL FUNCTION 'ZFSD_CALCULA_PRECO'
*                EXPORTING                                   "FB23112018
*                  i_pcl    = eg_dados-pe_pcl                "FB23112018
*                  i_pcb    = eg_dados-pi_pcb                "FB23112018
*                TABLES
*                  tg_dados = tg_dados.
*
*              LOOP AT tg_dados INTO eg_dados.
*                READ TABLE tg_saida INTO eg_saida INDEX eg_dados-pi_index.
*
*                eg_saida-pcl              = eg_dados-pe_pcl.
*                eg_saida-pclst            = eg_dados-pe_pclst.
*                eg_saida-preco_transf     = eg_dados-pe_preco_transf.
*                eg_saida-custo_log        = eg_dados-pe_lco.
*                eg_saida-pv_liq           = eg_dados-pe_pv_liq.
*                eg_saida-mg_liq           = eg_dados-pe_mg_liq.
*                eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
*                eg_saida-pv_fin           = eg_dados-pi_pvfin.
*                eg_saida-rate_icms        = eg_dados-pe_rate_icms.
*                eg_saida-base_icms        = eg_dados-pe_base_icms.
*                eg_saida-cust_icms        = eg_dados-pe_cust_icms.
*                eg_saida-val_icms         = eg_dados-pe_val_icms.
*                eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
*                eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
*                eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
*                eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
*                eg_saida-base_red_1       = eg_dados-pe_base_red_1.
*                eg_saida-base_red_2       = eg_dados-pe_base_red_2.
*                eg_saida-val_base_st      = eg_dados-pe_val_base_st.
*                eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
*                eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
*                eg_saida-base_ipi         = eg_dados-pe_base_ipi.
*                eg_saida-val_ipi          = eg_dados-pe_val_ipi.
*                eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
*                eg_saida-base_cofins      = eg_dados-pe_base_cofins.
*                eg_saida-val_cofins       = eg_dados-pe_val_cofins.
*                eg_saida-rate_pis         = eg_dados-pe_rate_pis.
*                eg_saida-base_pis         = eg_dados-pe_base_pis.
*                eg_saida-val_pis          = eg_dados-pe_val_pis.
*                eg_saida-val_rappel       = eg_dados-pe_val_rappel.
*                eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
*                eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
*                eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
*                eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
*
*                eg_saida-c_mvto           = eg_dados-pe_c_mvto.
*                eg_saida-c_pallet         = eg_dados-pe_c_pallet.
*                eg_saida-frete            = eg_dados-pe_frete.
*                eg_saida-tx_fin           = eg_dados-pe_tx_fin.
*                eg_saida-tx_gest          = eg_dados-pe_tx_gest.
*                eg_saida-c_arm            = eg_dados-pe_c_arm.
*                eg_saida-umrez            = eg_dados-pe_umrez.
*                eg_saida-hoehe            = eg_dados-pe_hoehe.
*                eg_saida-breit            = eg_dados-pe_breit.
*                eg_saida-laeng            = eg_dados-pe_laeng.
*                eg_saida-tx_mov           = eg_dados-pe_tx_mov.
*                eg_saida-tx_frete         = eg_dados-pe_tx_frete.
*                eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
*                eg_saida-dias_est         = eg_dados-pe_dias_est.
*                eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
*                eg_saida-gestao           = eg_dados-pe_gestao.
*                eg_saida-tx_desp          = eg_dados-pe_tx_desp.
*                eg_saida-tx_fob           = eg_dados-pe_tx_fob.
*                eg_saida-despachante      = eg_dados-pe_despachante.
*                eg_saida-fob              = eg_dados-pe_fob.
*                eg_saida-fin              = eg_dados-pe_fin.
*
*                eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*                eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*                eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*                eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*                eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*                eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*                eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*                eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*                eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*                eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*                eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*                eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*                eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*                eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*                eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*                eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*                eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*                eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*                eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*                eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*                MODIFY tg_saida FROM eg_saida INDEX eg_dados-pi_index.
*              ENDLOOP.
*            ENDIF.
*          ENDIF.
*          CALL METHOD vg_grid->refresh_table_display.
*        ENDIF.
*      ENDIF.
*    ENDIF.
*
*    IF e_ucomm EQ 'BT_SET_PCB'.
*      "Verificar material a ser alterado
*      PERFORM f_seleciona_material_centro.
*
*      IF tg_mat_pop[] IS NOT INITIAL.
*        CALL FUNCTION 'FOBU_POPUP_GET_VALUE'
*          EXPORTING
*            tablename         = 'ZTSDD_SIMUPRECI'
*            fieldname         = 'PCB'
*          IMPORTING
*            field_value_int_c = vl_value
*          EXCEPTIONS
*            internal_error    = 1
*            cancelled         = 2
*            OTHERS            = 3.
*        IF sy-subrc NE 0.
*          CLEAR vl_value.
*        ENDIF.
*        IF vl_value IS NOT INITIAL.
*          REFRESH: tg_dados, tg_pcl.
*
*          "Atribuir valores
*          LOOP AT tg_mat_pop INTO eg_mat_pop.
*            LOOP AT tg_saida INTO eg_saida WHERE matnr EQ eg_mat_pop-matnr
*                                             AND werks EQ eg_mat_pop-werks.
*              eg_saida-pcb = vl_value.
*              MODIFY tg_saida FROM eg_saida INDEX sy-tabix.
*
*              "Preparar dados para cálculo
*              eg_dados-pi_matprecadx = eg_saida-matprecadx.
*              eg_dados-pi_matnr      = eg_saida-matnr.
*              eg_dados-pi_matnr_ref  = eg_saida-matnr_ref.
*              eg_dados-pi_matkl      = eg_saida-matkl.
*              eg_dados-pi_werks      = eg_saida-werks.
*              eg_dados-pi_werks_to   = eg_saida-werks_to.
*              eg_dados-pi_vkkab      = eg_saida-vkkab.
*              eg_dados-pi_tipo       = '1'.
*              eg_dados-pi_state_from = eg_saida-state_from.
*              eg_dados-pi_state_to   = eg_saida-state_to.
*              eg_dados-pi_mtuse      = eg_saida-mtuse.
*              eg_dados-pi_mtorg      = eg_saida-mtorg.
*              eg_dados-pi_steuc      = eg_saida-steuc.
*              eg_dados-pi_pcb        = eg_saida-pcb.
*              eg_dados-pi_index      = sy-tabix.
*              eg_dados-pi_mat_ref    = eg_saida-mat_ref.
*              eg_dados-pi_mwskz      = eg_saida-mwskz.
*
*              READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_saida-matnr
*                                                     werks = eg_saida-werks.
*              IF sy-subrc EQ 0.
*                eg_dados-pi_pclx       = abap_false.
*                eg_dados-pe_pcl        = eg_pcl-pcl.
*                eg_dados-pe_pclst      = eg_pcl-pclst.
*                eg_dados-pe_rate_icms_comp      =  eg_pcl-rate_icms_comp.
*                eg_dados-pe_base_icms_comp      =  eg_pcl-base_icms_comp.
*                eg_dados-pe_val_icms_comp       =  eg_pcl-val_icms_comp.
*                eg_dados-pe_rate_ipi_comp       =  eg_pcl-rate_ipi_comp.
*                eg_dados-pe_base_ipi_comp       =  eg_pcl-base_ipi_comp.
*                eg_dados-pe_val_ipi_comp        =  eg_pcl-val_ipi_comp.
*                eg_dados-pe_rate_cofins_comp    =  eg_pcl-rate_cofins_comp.
*                eg_dados-pe_base_cofins_comp    =  eg_pcl-base_cofins_comp.
*                eg_dados-pe_val_cofins_comp     =  eg_pcl-val_cofins_comp.
*                eg_dados-pe_rate_pis_comp       =  eg_pcl-rate_pis_comp.
*                eg_dados-pe_base_pis_comp       =  eg_pcl-base_pis_comp.
*                eg_dados-pe_val_pis_comp        =  eg_pcl-val_pis_comp.
*                eg_dados-pe_calc_base_st_comp   =  eg_pcl-calc_base_st_comp.
*                eg_dados-pe_calc_icms_st_comp   =  eg_pcl-calc_icms_st_comp.
*                eg_dados-pe_maj_bst_comp        =  eg_pcl-maj_bst_comp.
*                eg_dados-pe_maj_bicms_comp      =  eg_pcl-maj_bicms_comp.
*                eg_dados-pe_calc_pis_st_comp    =  eg_pcl-calc_pis_st_comp.
*                eg_dados-pe_calc_cofins_st_comp =  eg_pcl-calc_cofins_st_comp.
*                eg_dados-pe_rate_icms_st_comp   =  eg_pcl-rate_icms_st_comp.
*                eg_dados-pe_rate_st_int_comp    =  eg_pcl-rate_st_int_comp.
*              ELSE.
*                eg_dados-pi_pclx       = abap_true.
*              ENDIF.
*
*              eg_dados-pi_pvfin      = eg_saida-pv_fin.
*              eg_dados-pi_rappel     = eg_saida-rappel.
*              eg_dados-pi_uf_precad  = eg_saida-uf_precad.
*
*              "Manter dados de compra
*              eg_dados-pe_rate_icms_comp      =  eg_saida-rate_icms_comp.
*              eg_dados-pe_base_icms_comp      =  eg_saida-base_icms_comp.
*              eg_dados-pe_val_icms_comp       =  eg_saida-val_icms_comp.
*              eg_dados-pe_rate_ipi_comp       =  eg_saida-rate_ipi_comp.
*              eg_dados-pe_base_ipi_comp       =  eg_saida-base_ipi_comp.
*              eg_dados-pe_val_ipi_comp        =  eg_saida-val_ipi_comp.
*              eg_dados-pe_rate_cofins_comp    =  eg_saida-rate_cofins_comp.
*              eg_dados-pe_base_cofins_comp    =  eg_saida-base_cofins_comp.
*              eg_dados-pe_val_cofins_comp     =  eg_saida-val_cofins_comp.
*              eg_dados-pe_rate_pis_comp       =  eg_saida-rate_pis_comp.
*              eg_dados-pe_base_pis_comp       =  eg_saida-base_pis_comp.
*              eg_dados-pe_val_pis_comp        =  eg_saida-val_pis_comp.
*              eg_dados-pe_calc_base_st_comp   =  eg_saida-calc_base_st_comp.
*              eg_dados-pe_calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
*              eg_dados-pe_maj_bst_comp        =  eg_saida-maj_bst_comp.
*              eg_dados-pe_maj_bicms_comp      =  eg_saida-maj_bicms_comp.
*              eg_dados-pe_calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
*              eg_dados-pe_calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
*              eg_dados-pe_rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
*              eg_dados-pe_rate_st_int_comp    =  eg_saida-rate_st_int_comp.
*
*              APPEND eg_dados TO tg_dados.
*            ENDLOOP.
*          ENDLOOP.
*
*          IF tg_dados[] IS NOT INITIAL.
*            READ TABLE tg_dados INTO eg_dados INDEX 1.      "FB23112018
*            CALL FUNCTION 'ZFSD_CALCULA_PRECO'
*              EXPORTING                                   "FB23112018
*                i_pcl    = eg_dados-pe_pcl                "FB23112018
*                i_pcb    = eg_dados-pi_pcb                "FB23112018
*              TABLES
*                tg_dados = tg_dados.
*
*            LOOP AT tg_dados INTO eg_dados.
*              READ TABLE tg_saida INTO eg_saida INDEX eg_dados-pi_index.
*
*              eg_saida-pcl              = eg_dados-pe_pcl.
*              eg_saida-pclst            = eg_dados-pe_pclst.
*              eg_saida-preco_transf     = eg_dados-pe_preco_transf.
*              eg_saida-custo_log        = eg_dados-pe_lco.
*              eg_saida-pv_liq           = eg_dados-pe_pv_liq.
*              eg_saida-mg_liq           = eg_dados-pe_mg_liq.
*              eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
*              eg_saida-pv_fin           = eg_dados-pi_pvfin.
*              eg_saida-rate_icms        = eg_dados-pe_rate_icms.
*              eg_saida-base_icms        = eg_dados-pe_base_icms.
*              eg_saida-cust_icms        = eg_dados-pe_cust_icms.
*              eg_saida-val_icms         = eg_dados-pe_val_icms.
*              eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
*              eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
*              eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
*              eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
*              eg_saida-base_red_1       = eg_dados-pe_base_red_1.
*              eg_saida-base_red_2       = eg_dados-pe_base_red_2.
*              eg_saida-val_base_st      = eg_dados-pe_val_base_st.
*              eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
*              eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
*              eg_saida-base_ipi         = eg_dados-pe_base_ipi.
*              eg_saida-val_ipi          = eg_dados-pe_val_ipi.
*              eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
*              eg_saida-base_cofins      = eg_dados-pe_base_cofins.
*              eg_saida-val_cofins       = eg_dados-pe_val_cofins.
*              eg_saida-rate_pis         = eg_dados-pe_rate_pis.
*              eg_saida-base_pis         = eg_dados-pe_base_pis.
*              eg_saida-val_pis          = eg_dados-pe_val_pis.
*              eg_saida-val_rappel       = eg_dados-pe_val_rappel.
*              eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
*              eg_saida-gestao           = eg_dados-pe_gestao.
*              eg_saida-tx_desp          = eg_dados-pe_tx_desp.
*              eg_saida-tx_fob           = eg_dados-pe_tx_fob.
*              eg_saida-despachante      = eg_dados-pe_despachante.
*              eg_saida-fob              = eg_dados-pe_fob.
*              eg_saida-fin              = eg_dados-pe_fin.
*              eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
*              eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
*              eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
*
*              eg_saida-c_mvto           = eg_dados-pe_c_mvto.
*              eg_saida-c_pallet         = eg_dados-pe_c_pallet.
*              eg_saida-frete            = eg_dados-pe_frete.
*              eg_saida-tx_fin           = eg_dados-pe_tx_fin.
*              eg_saida-tx_gest          = eg_dados-pe_tx_gest.
*              eg_saida-c_arm            = eg_dados-pe_c_arm.
*              eg_saida-umrez            = eg_dados-pe_umrez.
*              eg_saida-hoehe            = eg_dados-pe_hoehe.
*              eg_saida-breit            = eg_dados-pe_breit.
*              eg_saida-laeng            = eg_dados-pe_laeng.
*              eg_saida-tx_mov           = eg_dados-pe_tx_mov.
*              eg_saida-tx_frete         = eg_dados-pe_tx_frete.
*              eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
*              eg_saida-dias_est         = eg_dados-pe_dias_est.
*              eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
*              eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*              eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*              eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*              eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*              eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*              eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*              eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*              eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*              eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*              eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*              eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*              eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*              eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*              eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*              eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*              eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*              eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*              eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*              eg_saida-rate_icms_venda     =  eg_dados-pe_rate_icms_venda.
*              eg_saida-base_icms_venda     =  eg_dados-pe_base_icms_venda.
*              eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*              eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*              MODIFY tg_saida FROM eg_saida INDEX eg_dados-pi_index.
*
*              READ TABLE tg_pcl INTO eg_pcl WITH KEY matnr = eg_dados-pi_matnr
*                                                     werks = eg_dados-pi_werks.
*              IF sy-subrc NE 0.
*                eg_pcl-matnr      = eg_dados-pi_matnr.
*                eg_pcl-werks      = eg_dados-pi_werks.
*                eg_pcl-pcl        = eg_dados-pe_pcl.
*                eg_pcl-pclst      = eg_dados-pe_pclst.
*                eg_pcl-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*                eg_pcl-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*                eg_pcl-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*                eg_pcl-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*                eg_pcl-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*                eg_pcl-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*                eg_pcl-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*                eg_pcl-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*                eg_pcl-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*                eg_pcl-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*                eg_pcl-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*                eg_pcl-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*                eg_pcl-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*                eg_pcl-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*                eg_pcl-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*                eg_pcl-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*                eg_pcl-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*                eg_pcl-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*                eg_pcl-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*                eg_pcl-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*                APPEND eg_pcl TO tg_pcl.
*              ENDIF.
*
*            ENDLOOP.
*          ENDIF.
*          CALL METHOD vg_grid->refresh_table_display.
*        ENDIF.
*      ENDIF.
*    ENDIF.
*
*    IF e_ucomm EQ 'BT_COMP'   OR
*       e_ucomm EQ 'BT_TRANSF' OR
*       e_ucomm EQ 'BT_VENDA'.
*
*      sy-ucomm = e_ucomm.
*
**   Obtém a linha selecionada
*      CALL METHOD vg_grid->get_selected_rows
*        IMPORTING
*          et_index_rows = tl_index_rows
*          et_row_no     = tl_row_no.
*
*      REFRESH tg_impostos.
*      LOOP AT tl_index_rows INTO el_index_rows.
*
*        READ TABLE tg_saida INTO eg_saida INDEX el_index_rows-index.
*        eg_impostos-matnr               =  eg_saida-matnr.
*        eg_impostos-werks               =  eg_saida-werks.
*        eg_impostos-ptext               =  eg_saida-ptext.
*        eg_impostos-mwskz               =  eg_saida-mwskz.
*
*        READ TABLE tg_t007s INTO eg_t007s WITH KEY mwskz = eg_impostos-mwskz.
*        eg_impostos-text1  = eg_t007s-text1.
*
*        eg_impostos-state_from          =  eg_saida-state_from.
*        eg_impostos-uf_precad           =  eg_saida-uf_precad.
*
*        IF e_ucomm EQ 'BT_COMP' AND eg_saida-mat_ref IS NOT INITIAL.
*          CONTINUE.
*        ENDIF.
*
*        eg_impostos-state_to            =  eg_saida-state_to.
*        eg_impostos-rate_icms           =  eg_saida-rate_icms.
*        eg_impostos-base_icms           =  eg_saida-base_icms.
*        eg_impostos-rate_icms_venda     =  eg_saida-rate_icms_venda.
*        eg_impostos-base_icms_venda     =  eg_saida-base_icms_venda.
*        eg_impostos-cust_icms           =  eg_saida-cust_icms.
*        eg_impostos-val_icms            =  eg_saida-val_icms.
*        eg_impostos-rate_icms_st        =  eg_saida-rate_icms_st.
*        eg_impostos-base_icms_st        =  eg_saida-base_icms_st.
*        eg_impostos-rate_icms_st_int    =  eg_saida-rate_icms_st_int.
*        eg_impostos-base_icms_st_int    =  eg_saida-base_icms_st_int.
*        eg_impostos-base_red_1          =  eg_saida-base_red_1.
*        eg_impostos-base_red_2          =  eg_saida-base_red_2.
*        eg_impostos-val_base_st         =  eg_saida-val_base_st.
*        eg_impostos-val_icms_st         =  eg_saida-val_icms_st.
*        eg_impostos-rate_ipi            =  eg_saida-rate_ipi.
*        eg_impostos-base_ipi            =  eg_saida-base_ipi.
*        eg_impostos-val_ipi             =  eg_saida-val_ipi.
*        eg_impostos-rate_cofins         =  eg_saida-rate_cofins.
*        eg_impostos-base_cofins         =  eg_saida-base_cofins.
*        eg_impostos-val_cofins          =  eg_saida-val_cofins.
*        eg_impostos-rate_pis            =  eg_saida-rate_pis.
*        eg_impostos-base_pis            =  eg_saida-base_pis.
*        eg_impostos-val_pis             =  eg_saida-val_pis.
*        eg_impostos-val_rappel          =  eg_saida-val_rappel.
*        eg_impostos-val_custo_log       =  eg_saida-val_custo_log.
*        eg_impostos-total_imp_venda     =  eg_saida-total_imp_venda.
*        eg_impostos-rate_icms_comp      =  eg_saida-rate_icms_comp.
*        eg_impostos-base_icms_comp      =  eg_saida-base_icms_comp.
*        eg_impostos-val_icms_comp       =  eg_saida-val_icms_comp.
*        eg_impostos-rate_ipi_comp       =  eg_saida-rate_ipi_comp.
*        eg_impostos-base_ipi_comp       =  eg_saida-base_ipi_comp.
*        eg_impostos-val_ipi_comp        =  eg_saida-val_ipi_comp.
*        eg_impostos-rate_cofins_comp    =  eg_saida-rate_cofins_comp.
*        eg_impostos-base_cofins_comp    =  eg_saida-base_cofins_comp.
*        eg_impostos-val_cofins_comp     =  eg_saida-val_cofins_comp.
*        eg_impostos-rate_pis_comp       =  eg_saida-rate_pis_comp.
*        eg_impostos-base_pis_comp       =  eg_saida-base_pis_comp.
*        eg_impostos-val_pis_comp        =  eg_saida-val_pis_comp.
*        eg_impostos-calc_base_st_comp   =  eg_saida-calc_base_st_comp.
*        eg_impostos-calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
*        eg_impostos-maj_bst_comp        =  eg_saida-maj_bst_comp.
*        eg_impostos-maj_bicms_comp      =  eg_saida-maj_bicms_comp.
*        eg_impostos-calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
*        eg_impostos-calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
*        eg_impostos-rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
*        eg_impostos-rate_st_int_comp    =  eg_saida-rate_st_int_comp.
*        APPEND eg_impostos TO tg_impostos.
*        CLEAR eg_impostos.
*      ENDLOOP.
*
*      IF e_ucomm EQ 'BT_COMP'.
*        "Função disponível apenas para materiais pré-cadastrados sem referência.
*        MESSAGE i124(zmsd_classe_mensagem).
*        SORT tg_impostos BY matnr werks.
*        DELETE ADJACENT DUPLICATES FROM tg_impostos COMPARING matnr werks.
*      ENDIF.
*
*      IF tg_impostos[] IS NOT INITIAL.
*        PERFORM f_exibe_impostos.
*      ENDIF.
*
*      CALL METHOD vg_grid->refresh_table_display.
*    ENDIF.
*
*    IF e_ucomm EQ 'BT_C_LOG'.
**   Obtém a linha selecionada
*      CALL METHOD vg_grid->get_selected_rows
*        IMPORTING
*          et_index_rows = tl_index_rows
*          et_row_no     = tl_row_no.
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
*    ENDIF.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
*    IF e_ucomm EQ 'BT_REP'.
*
**   Obtém a linha selecionada
*      CALL METHOD vg_grid->get_selected_rows
*        IMPORTING
*          et_index_rows = tl_index_rows
*          et_row_no     = tl_row_no.
*
*      LOOP AT tl_index_rows INTO el_index_rows.
*
*        READ TABLE tg_saida_rel INTO eg_saida_rel INDEX el_index_rows-index.
*        IF sy-subrc EQ 0.
*
*          CALL FUNCTION 'ZFMM_AUTO_SIMULACAO_PRECO_V2'
*            EXPORTING
*              docsim              = eg_saida_rel-docsim
*              pltyp               = eg_saida_rel-pltyp
*              matnr               = eg_saida_rel-matnr
*              werks               = eg_saida_rel-werks
*              reprocessar         = 'X'
*              uname               = sy-uname
*            IMPORTING
*              retorno             = vl_retorno
*            EXCEPTIONS
*              selecao_errada      = 1
*              nenhum_doc_aprovado = 2
*              OTHERS              = 3.
*          IF sy-subrc <> 0.
*            clear vl_retorno.
*          ENDIF.
*        ENDIF.
*      ENDLOOP.
*      PERFORM f_seleciona_dados_rel.
*      CALL METHOD vg_grid->refresh_table_display.
*    ENDIF.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - fim
*  ENDMETHOD.
*
*  METHOD handle_top_of_page.
** Top-of-page event
*    PERFORM event_top_of_page USING vg_dyndoc_id.
*
*  ENDMETHOD.                            "handle_top_of_page
*
*  METHOD handle_data_changed.
*
*    " Just trigger PAI followed by PBO
*    CALL METHOD cl_gui_cfw=>set_new_ok_code
*      EXPORTING
*        new_code = 'ENTER'
**        IMPORTING
**       rc       =
*      .
*
*  ENDMETHOD.                    "handle_data_changed
*
*  METHOD handle_data_changed_finished.
**   define local data
*    DATA: ls_cell        TYPE lvc_s_modi.
*
*    REFRESH: tg_dados, tg_change.
*    CLEAR: eg_dados, eg_change.
*
*    "Sumarizar alterações no ALV
*    LOOP AT et_good_cells INTO ls_cell.
*
*      READ TABLE tg_change INTO eg_change WITH KEY index = ls_cell-row_id.
*
*      IF sy-subrc EQ 0.
*        CASE ls_cell-fieldname.
*          WHEN 'PCB'.
*            eg_change-pclx = abap_true.
*            eg_change-pcb_v = ls_cell-value.
*
*          WHEN 'PV_FIN'.
*            eg_change-pv_fin_v = ls_cell-value.
*
*          WHEN 'RAPPEL'.
*            eg_change-rappel_v = ls_cell-value.
*        ENDCASE.
*        MODIFY tg_change FROM eg_change INDEX sy-tabix.
*
*      ELSE.
*        eg_change-index = ls_cell-row_id.
*
*        CASE ls_cell-fieldname.
*          WHEN 'PCB'.
*            eg_change-pclx = abap_true.
*            eg_change-pcb_v = ls_cell-value.
*
*          WHEN 'PV_FIN'.
*            eg_change-pv_fin_v = ls_cell-value.
*
*          WHEN 'RAPPEL'.
*            eg_change-rappel_v = ls_cell-value.
*        ENDCASE.
*
*        APPEND eg_change TO tg_change.
*      ENDIF.
*      CLEAR eg_change.
*    ENDLOOP.
*
*    "Preparar dados para cálculo
*    LOOP AT tg_change INTO eg_change.
*      READ TABLE tg_saida INTO eg_saida INDEX eg_change-index.
*
*      eg_dados-pi_matprecadx = eg_saida-matprecadx.
*      eg_dados-pi_matnr      = eg_saida-matnr.
*      eg_dados-pi_matnr_ref  = eg_saida-matnr_ref.
*      eg_dados-pi_matkl      = eg_saida-matkl.
*      eg_dados-pi_werks      = eg_saida-werks.
*      eg_dados-pi_werks_to   = eg_saida-werks_to.
*      eg_dados-pi_vkkab      = eg_saida-vkkab.
*      eg_dados-pi_tipo       = '1'.
*      eg_dados-pi_state_from = eg_saida-state_from.
*      eg_dados-pi_state_to   = eg_saida-state_to.
*      eg_dados-pi_mtuse      = eg_saida-mtuse.
*      eg_dados-pi_mtorg      = eg_saida-mtorg.
*      eg_dados-pi_steuc      = eg_saida-steuc.
*      eg_dados-pi_mat_ref    = eg_saida-mat_ref.
*      eg_dados-pi_mwskz      = eg_saida-mwskz.
*
*      IF eg_change-pcb_v IS NOT INITIAL.
*        eg_dados-pi_pcb        = eg_change-pcb_v.
*        eg_dados-pi_pclx       = abap_true.
*      ELSE.
*        eg_dados-pi_pcb        = eg_saida-pcb.
*        eg_dados-pe_pcl        = eg_saida-pcl.
*        eg_dados-pe_pclst      = eg_saida-pclst.
*        eg_dados-pi_pclx       = space.
*      ENDIF.
*
*      IF eg_change-pv_fin_v IS NOT INITIAL.
*        "Converter para preço psicológico
*        CALL FUNCTION 'PRICE_POINT_READ'
*          EXPORTING
*            pi_vkorg                   = 'LB01'
*            pi_vtweg                   = '10'
*            pi_rktyp                   = 'A'
*            pi_eprgr                   = 'ZLMB01'
*            pi_price                   = eg_change-pv_fin_v
*            pi_waers                   = 'BRL'
*            pi_datam                   = sy-datum
*            pi_kurst                   = 'M'
*            pi_hwaer                   = 'BRL'
*            pi_mfact                   = '1'
*          IMPORTING
*            pe_price                   = eg_change-pv_fin_v
*          EXCEPTIONS
*            no_price_point_group_found = 1
*            no_price_points_maintained = 2
*            conversion_not_found       = 3
*            OTHERS                     = 4.
*        IF sy-subrc EQ 0.
*          eg_dados-pi_pvfin     = eg_change-pv_fin_v.
*        ENDIF.
*      ELSE.
*        eg_dados-pi_pvfin     = eg_saida-pv_fin.
*      ENDIF.
*
*      IF eg_change-rappel_v IS NOT INITIAL.
*        eg_dados-pi_rappel     = eg_change-rappel_v.
*      ELSE.
*        eg_dados-pi_rappel     = eg_saida-rappel.
*      ENDIF.
*
*      eg_dados-pi_index      = eg_change-index.
*      eg_dados-pi_uf_precad  = eg_saida-uf_precad.
*
*      "Manter dados de compra
*      eg_dados-pe_rate_icms_comp      =  eg_saida-rate_icms_comp.
*      eg_dados-pe_base_icms_comp      =  eg_saida-base_icms_comp.
*      eg_dados-pe_val_icms_comp       =  eg_saida-val_icms_comp.
*      eg_dados-pe_rate_ipi_comp       =  eg_saida-rate_ipi_comp.
*      eg_dados-pe_base_ipi_comp       =  eg_saida-base_ipi_comp.
*      eg_dados-pe_val_ipi_comp        =  eg_saida-val_ipi_comp.
*      eg_dados-pe_rate_cofins_comp    =  eg_saida-rate_cofins_comp.
*      eg_dados-pe_base_cofins_comp    =  eg_saida-base_cofins_comp.
*      eg_dados-pe_val_cofins_comp     =  eg_saida-val_cofins_comp.
*      eg_dados-pe_rate_pis_comp       =  eg_saida-rate_pis_comp.
*      eg_dados-pe_base_pis_comp       =  eg_saida-base_pis_comp.
*      eg_dados-pe_val_pis_comp        =  eg_saida-val_pis_comp.
*      eg_dados-pe_calc_base_st_comp   =  eg_saida-calc_base_st_comp.
*      eg_dados-pe_calc_icms_st_comp   =  eg_saida-calc_icms_st_comp.
*      eg_dados-pe_maj_bst_comp        =  eg_saida-maj_bst_comp.
*      eg_dados-pe_maj_bicms_comp      =  eg_saida-maj_bicms_comp.
*      eg_dados-pe_calc_pis_st_comp    =  eg_saida-calc_pis_st_comp.
*      eg_dados-pe_calc_cofins_st_comp =  eg_saida-calc_cofins_st_comp.
*      eg_dados-pe_rate_icms_st_comp   =  eg_saida-rate_icms_st_comp.
*      eg_dados-pe_rate_st_int_comp    =  eg_saida-rate_st_int_comp.
*      APPEND eg_dados TO tg_dados.
*    ENDLOOP.
*
*    IF tg_dados[] IS NOT INITIAL.
*
*      READ TABLE tg_dados INTO eg_dados INDEX 1.            "FB23112018
*      CALL FUNCTION 'ZFSD_CALCULA_PRECO'
*        EXPORTING                                           "FB23112018
*          i_pcl    = eg_dados-pe_pcl                        "FB23112018
*          i_pcb    = eg_dados-pi_pcb                        "FB23112018
*        TABLES
*          tg_dados = tg_dados.
*
*      LOOP AT tg_dados INTO eg_dados.
*        READ TABLE tg_saida INTO eg_saida INDEX eg_dados-pi_index.
*
*        eg_saida-pcl              = eg_dados-pe_pcl.
*        eg_saida-pclst            = eg_dados-pe_pclst.
*        eg_saida-preco_transf     = eg_dados-pe_preco_transf.
*        eg_saida-custo_log        = eg_dados-pe_lco.
*        eg_saida-pv_liq           = eg_dados-pe_pv_liq.
*        eg_saida-mg_liq           = eg_dados-pe_mg_liq.
*        eg_saida-mg_bruta         = eg_dados-pe_mg_bruta.
*        eg_saida-pv_fin           = eg_dados-pi_pvfin.
*        eg_saida-rate_icms        = eg_dados-pe_rate_icms.
*        eg_saida-base_icms        = eg_dados-pe_base_icms.
*        eg_saida-cust_icms        = eg_dados-pe_cust_icms.
*        eg_saida-val_icms         = eg_dados-pe_val_icms.
*        eg_saida-rate_icms_st     = eg_dados-pe_rate_icms_st.
*        eg_saida-base_icms_st     = eg_dados-pe_base_icms_st.
*        eg_saida-rate_icms_st_int = eg_dados-pe_rate_icms_st_int.
*        eg_saida-base_icms_st_int = eg_dados-pe_base_icms_st_int.
*        eg_saida-base_red_1       = eg_dados-pe_base_red_1.
*        eg_saida-base_red_2       = eg_dados-pe_base_red_2.
*        eg_saida-val_base_st      = eg_dados-pe_val_base_st.
*        eg_saida-val_icms_st      = eg_dados-pe_val_icms_st.
*        eg_saida-rate_ipi         = eg_dados-pe_rate_ipi.
*        eg_saida-base_ipi         = eg_dados-pe_base_ipi.
*        eg_saida-val_ipi          = eg_dados-pe_val_ipi.
*        eg_saida-rate_cofins      = eg_dados-pe_rate_cofins.
*        eg_saida-base_cofins      = eg_dados-pe_base_cofins.
*        eg_saida-val_cofins       = eg_dados-pe_val_cofins.
*        eg_saida-rate_pis         = eg_dados-pe_rate_pis.
*        eg_saida-base_pis         = eg_dados-pe_base_pis.
*        eg_saida-val_pis          = eg_dados-pe_val_pis.
*        eg_saida-val_rappel       = eg_dados-pe_val_rappel.
*        eg_saida-val_custo_log    = eg_dados-pe_val_custo_log.
*        eg_saida-rate_icms_venda  = eg_dados-pe_rate_icms_venda.
*        eg_saida-base_icms_venda  = eg_dados-pe_base_icms_venda.
*        eg_saida-total_imp_venda  = eg_dados-pe_total_imp_venda.
*        eg_saida-gestao           = eg_dados-pe_gestao.
*        eg_saida-tx_desp          = eg_dados-pe_tx_desp.
*        eg_saida-tx_fob           = eg_dados-pe_tx_fob.
*        eg_saida-despachante      = eg_dados-pe_despachante.
*        eg_saida-fob              = eg_dados-pe_fob.
*        eg_saida-fin              = eg_dados-pe_fin.
*
*        eg_saida-c_mvto           = eg_dados-pe_c_mvto.
*        eg_saida-c_pallet         = eg_dados-pe_c_pallet.
*        eg_saida-frete            = eg_dados-pe_frete.
*        eg_saida-tx_fin           = eg_dados-pe_tx_fin.
*        eg_saida-tx_gest          = eg_dados-pe_tx_gest.
*        eg_saida-c_arm            = eg_dados-pe_c_arm.
*        eg_saida-umrez            = eg_dados-pe_umrez.
*        eg_saida-hoehe            = eg_dados-pe_hoehe.
*        eg_saida-breit            = eg_dados-pe_breit.
*        eg_saida-laeng            = eg_dados-pe_laeng.
*        eg_saida-tx_mov           = eg_dados-pe_tx_mov.
*        eg_saida-tx_frete         = eg_dados-pe_tx_frete.
*        eg_saida-custo_ins_pallet = eg_dados-pe_custo_ins_pallet.
*        eg_saida-dias_est         = eg_dados-pe_dias_est.
*        eg_saida-custo_armazen    = eg_dados-pe_custo_armazen.
*
*        eg_saida-rate_icms_comp      =  eg_dados-pe_rate_icms_comp.
*        eg_saida-base_icms_comp      =  eg_dados-pe_base_icms_comp.
*        eg_saida-val_icms_comp       =  eg_dados-pe_val_icms_comp.
*        eg_saida-rate_ipi_comp       =  eg_dados-pe_rate_ipi_comp.
*        eg_saida-base_ipi_comp       =  eg_dados-pe_base_ipi_comp.
*        eg_saida-val_ipi_comp        =  eg_dados-pe_val_ipi_comp.
*        eg_saida-rate_cofins_comp    =  eg_dados-pe_rate_cofins_comp.
*        eg_saida-base_cofins_comp    =  eg_dados-pe_base_cofins_comp.
*        eg_saida-val_cofins_comp     =  eg_dados-pe_val_cofins_comp.
*        eg_saida-rate_pis_comp       =  eg_dados-pe_rate_pis_comp.
*        eg_saida-base_pis_comp       =  eg_dados-pe_base_pis_comp.
*        eg_saida-val_pis_comp        =  eg_dados-pe_val_pis_comp.
*        eg_saida-calc_base_st_comp   =  eg_dados-pe_calc_base_st_comp.
*        eg_saida-calc_icms_st_comp   =  eg_dados-pe_calc_icms_st_comp.
*        eg_saida-maj_bst_comp        =  eg_dados-pe_maj_bst_comp.
*        eg_saida-maj_bicms_comp      =  eg_dados-pe_maj_bicms_comp.
*        eg_saida-calc_pis_st_comp    =  eg_dados-pe_calc_pis_st_comp.
*        eg_saida-calc_cofins_st_comp =  eg_dados-pe_calc_cofins_st_comp.
*        eg_saida-rate_icms_st_comp   =  eg_dados-pe_rate_icms_st_comp.
*        eg_saida-rate_st_int_comp    =  eg_dados-pe_rate_st_int_comp.
*
*        MODIFY tg_saida FROM eg_saida INDEX eg_dados-pi_index.
*      ENDLOOP.
*    ENDIF.
*
*  ENDMETHOD.                    "handle_data_changed_finished
*ENDCLASS.                 "LCL_EVENT_HANDLER IMPLEMENTATION

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
* Alteração - PR.09951 - 12.07.2023 - Inicio
  so_werks-sign = 'I'.
  so_werks-option = 'EQ'.
  so_werks-low =  '0099'.
  append so_werks.
* Alteração - PR.09951 - 12.07.2023 - FIM


**&---------------------------------------------------------------------*
**& AT SELECTION-SCREEN OUTPUT
**&---------------------------------------------------------------------*
*AT SELECTION-SCREEN OUTPUT.
*
** Se a seleção for por pedido, habilitar campo de nº de pedido
** e o critério adicional PCB do CE
*  IF rb_ped NE space.
*    LOOP AT SCREEN.
*      IF screen-group1 = ped OR
*         screen-group1 = all OR
*         screen-group1 = pcb.
*        screen-active = '1'.
*        MODIFY SCREEN.
*      ELSEIF screen-group1 NE space.
*        screen-active = '0'.
*        MODIFY SCREEN.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
*
** Se a seleção for por material, habilitar campos de nº de material,
** e o critério adicional PCB do CE
*  IF rb_mat NE space.
*    LOOP AT SCREEN.
*      IF screen-group1 = mat OR
*         screen-group1 = all OR
*         screen-group1 = pcb.
*        screen-active = '1'.
*        MODIFY SCREEN.
*      ELSEIF screen-group1 NE space.
*        screen-active = '0'.
*        MODIFY SCREEN.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
*
** Se a seleção for por material pré-cadastrado, habilitar campos de nº de material pré-cadastrado
** O critério adicional será obrigatoriamente o PCB do cadastro, pois não há essa informação no CE
*  IF rb_mpc NE space.
*    LOOP AT SCREEN.
*      IF screen-group1 = mpc OR
*         screen-group1 = all.
*        screen-active = '1'.
*        MODIFY SCREEN.
*      ELSEIF screen-group1 NE space.
*        screen-active = '0'.
*        MODIFY SCREEN.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
*
** Se a seleção for por simulação, habilitar apenas o campo de nº de simulação
*  IF rb_sim NE space.
*    LOOP AT SCREEN.
*      IF screen-group1 = sim.
*        screen-active = '1'.
*        MODIFY SCREEN.
*      ELSEIF screen-group1 NE space.
*        screen-active = '0'.
*        MODIFY SCREEN.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - Inicio
** Se a seleção for por Relatorio de precificação, habilitar somente Simulacao e Material.
*  IF rb_aut NE space.
*    LOOP AT SCREEN.
*      IF screen-group1 = sim OR
*         screen-group1 = mat.
*        screen-active = '1'.
*        MODIFY SCREEN.
*      ELSEIF screen-group1 NE space.
*        screen-active = '0'.
*        MODIFY SCREEN.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
** Alteração - CC.1653 - Luiz - 27.04.2018 14:32:13 - FIM
*
**>>> <CC.2252> - Início da Inclusão - IROSA 19.09.2018
*
** Pega os usuários habilitados cadastrados via transação ZXX_PAR2
*  get_hard 'SD_0402_01_USUARIO_PCB' 'UNAME' gr_uname.
*
*  IF sy-uname NOT IN gr_uname.
*    LOOP AT SCREEN.
*      IF screen-group1 EQ pcb.
*        screen-input = '0'.
*        MODIFY SCREEN.
*      ENDIF.
*    ENDLOOP.
*  ENDIF.
**<<< <CC.2252> - Fim da Inclusão - IROSA 19.09.2018