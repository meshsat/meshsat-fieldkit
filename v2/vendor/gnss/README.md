# GNSS receiver documents

u-blox data sheets and the NEO-M9N integration manual behind the compute-module respin study (MESHSAT-709, appendix 32.35, `docs/respin-research-cm5-2026-09-04.md`): the candidates for a receiver on the carrier itself. Fetched 4 September 2026 from content.u-blox.com (the SAM-M10Q sheet sits under the newer `/documents/` path). The licence remark of the parent folder applies: these documents belong to u-blox and are kept here so the design record can be checked against the same pages later. Nothing here has been built; the carrier that would take one of these modules is a design study.

| File | Source | Date | What it is used for |
|---|---|---|---|
| `ublox-neo-m9n-00b-datasheet-UBX-19014285-R08.pdf` | https://content.u-blox.com/sites/default/files/NEO-M9N-00B_DataSheet_UBX-19014285.pdf | 4 Sep 2026 (R08) | the NEO-M9N-00B four-constellation receiver: footprint and pinout, supply and current figures, interfaces, the module candidate |
| `ublox-neo-m9n-integration-manual-UBX-19014286-R10.pdf` | https://content.u-blox.com/sites/default/files/NEO-M9N_Integrationmanual_UBX-19014286.pdf | 4 Sep 2026 (R10) | the reference schematic, antenna supply and supervisor, backup supply, layout and placement rules for the NEO-M9N |
| `ublox-max-m10s-datasheet-UBX-20035208-R08.pdf` | https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf | 4 Sep 2026 (R08) | the MAX-M10S, the smaller and lower-power alternative: footprint, pinout, current figures |
| `ublox-sam-m10q-datasheet-UBX-22013293-R05.pdf` | https://content.u-blox.com/sites/default/files/documents/SAM-M10Q_DataSheet_UBX-22013293.pdf | 4 Sep 2026 (R05) | the SAM-M10Q antenna module (patch antenna on the module): footprint, ground-plane and keep-out requirements, the no-external-antenna alternative |
