" Created By     : Capgemini SAP AI - Code Generation Engine
" Created On     : 03-07-2026
" Convention     : Workbook ABAP_Move2S4_Final.dcls

@EndUserText.label: 'Access Control for Consumption View VKP5 Conditions'
@MappingRole: true

define role ZC_VKP5CONDITIONS {
  grant select on ZC_VKP5CONDITIONS
    where (SalesOrganization) = 
      aspect pfcg_auth (V_VBAK_VKO, VKORG, ACTVT='03') 
      and 
      (SalesOrganization) = 'BR01'; // Default company code BR01
}