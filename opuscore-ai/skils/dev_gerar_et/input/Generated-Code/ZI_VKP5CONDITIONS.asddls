" Created By     : Capgemini SAP AI - Code Generation Engine
" Created On     : 03-07-2026
" Convention     : Workbook ABAP_Move2S4_Final.docx

@AbapCatalog.viewEnhancementCategory: [#NONE]
@AccessControl.authorizationCheck: #CHECK
@EndUserText.label: 'Interface View for VKP5 Conditions'
@Metadata.ignorePropagatedAnnotations: true

define root view entity ZI_VKP5CONDITIONS
  as select from a304                    // Condition Table
    inner join   a908 on a908.kappl = a304.kappl
                      and a908.kschl = a304.kschl
    inner join   konh on konh.knumh = a304.knumh
    inner join   konp on konp.knumh = konh.knumh
{
      // Key fields
  key a304.kappl                     as Application,
  key a304.kschl                     as ConditionType,
  key a304.knumh                     as ConditionRecord,
  key a304.vkorg                     as SalesOrganization,
  key a304.vtweg                     as DistributionChannel,
  key a304.matnr                     as Material,

      // Condition header data
      konh.erdat                     as CreationDate,
      konh.ernam                     as CreatedBy,
      konh.datab                     as ValidFrom,
      konh.datbi                     as ValidTo,

      // Condition values
      konp.kbetr                     as ConditionAmount,
      konp.konwa                     as ConditionUnit,
      konp.kpein                     as PricingUnit,
      konp.kmein                     as ConditionPricingUnit,

      // Additional fields for display
      a908.vtext                     as ConditionTypeDescription,
      
      // ETag for optimistic locking
      konh.aedat                     as LastChangedDate,
      konh.aenam                     as LastChangedBy,
      
      // Technical fields
      $session.system_date           as SystemDate
}
where
      a304.kappl = 'V'                // Sales application
  and konh.datbi >= $session.system_date  // Valid conditions only