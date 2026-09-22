" Created By     : Capgemini SAP AI - Code Generation Engine
" Created On     : 03-07-2026
" Convention     : Workbook ABAP_Move2S4_Final.docx

@EndUserText.label: 'Consumption View for VKP5 Conditions'
@AccessControl.authorizationCheck: #CHECK
@Metadata.allowExtensions: true

define root view entity ZC_VKP5CONDITIONS
  provider contract transactional_query
  as projection on ZI_VKP5CONDITIONS
{
      // Key fields
  key Application,
  key ConditionType,
  key ConditionRecord,
  key SalesOrganization,
  key DistributionChannel,
  key Material,

      // Display fields
      CreationDate,
      CreatedBy,
      ValidFrom,
      ValidTo,
      ConditionAmount,
      ConditionUnit,
      PricingUnit,
      ConditionPricingUnit,
      ConditionTypeDescription,
      LastChangedDate,
      LastChangedBy,
      SystemDate
}