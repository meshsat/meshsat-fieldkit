# Battery module research (MESHSAT-791 respin brief): cells, protection, envelope, fuse, connector, thermistor

Date: 4 September 2026. Scope: the five items of the module brief for a welded 1S12P Samsung INR18650-35E module (one cell in voltage, 3.0 to 4.2 V), a single-cell protection board rated 30 A or more continuous with a thermistor input or its own temperature cut-off, the module envelope for a 4 x 3 and a 6 x 2 flat arrangement, a 40 A blade fuse with holder, the Amass XT60 rating, and the 103AT-2 / NXRT thermistor for the charger JEITA input on PCB-A. Every figure carries its document and page. Page numbers are PDF page indices of the saved file (the Samsung specification prints its folio one lower, so "p3" is the sheet's page 2). All documents are saved in this folder (`scratchpad/respin/module/`), fetched with curl from the maker or, where the maker refused, from a distributor copy or the Wayback Machine. Nothing in any git repository was touched. Sizes in mm unless stated. Nothing of this has been built; the numbers are design inputs for the prototype.

## 0. Documents saved

| File | Source | What it is |
|---|---|---|
| `samsung-35e-orbtronic.pdf` (19 p) | orbtronic.com/content/samsung-35e-datasheet-inr18650-35e.pdf | Samsung SDI "Specification of Product" INR18650-35E, Spec. No. INR18650-35E, Ver. 1.1, 9 July 2015 (the released specification; used for every cell number below) |
| `samsung-35e-akkuzentrum.pdf` (25 p) | akkuzentrum.de/media/datasheets/Samsung__35E.pdf | the same specification, Ver. 1.0 (10 March 2015), with the long-form handling annex |
| `samsung-35e-conrad.pdf` (9 p) | asset.conrad.com (Conrad product datasheet 1499572) | Samsung SDI "Technical Report of INR18650-35E", June 2015, tentative specification with typical capacity, energy and rate data |
| `samsung-35e-relectro.pdf` (13 p) | relectro.co.za | reseller test sheet (lygte-info style); not a Samsung document, quoted only where flagged |
| `ti-bq2970.pdf` (35 p) | ti.com/lit/ds/symlink/bq2970.pdf | TI BQ2970/1/2/3 data sheet SLUSBU9I (March 2014, revised August 2024) |
| `ti-sluuaz3-bq29700evm.pdf` (7 p) | ti.com/lit/ug/sluuaz3/sluuaz3.pdf | TI BQ29700 EVM user's guide SLUUAZ3 (schematic, BOM) |
| `ti-csd17570q5b.pdf` (13 p) | ti.com/lit/ds/symlink/csd17570q5b.pdf | TI CSD17570Q5B 30 V NexFET SLPS471D (May 2017) |
| `ti-csd18510q5b.pdf` (12 p) | ti.com/lit/ds/symlink/csd18510q5b.pdf | TI CSD18510Q5B 40 V NexFET SLPS632 (March 2017), alternate |
| `ablic-s8261.pdf` (34 p) | ablic.com/en/doc/datasheet/battery_protection/S8261_E.pdf | ABLIC S-8261 Series 1-cell protection IC, Rev. 5.5_00 |
| `nisshinbo-r5405.pdf` (35 p) | nisshinbo-microdevices.co.jp (Wayback copy, direct refused) | Nisshinbo (Ricoh) R5403x/R5405x 1-cell protector, No. EA-215-201014 |
| `nisshinbo-r5460-rs.pdf` (38 p) | docs.rs-online.com/9a1c/A700000012409390.pdf | Nisshinbo R5460x2xx, No. EA-165-230201: a 2-cell protector, kept only to document that it does not apply |
| `batteryspace-prod-spec-274.pdf` (1 p) | batteryspace.com/prod-specs/274.pdf | AA Portable Power Corp spec sheet, model PCB-LIS1A15 (the 1S "20 A limit" module) |
| `pages/batteryspace-1s-20a.html`, `pages/batteryspace-1s-15a.html` | batteryspace.com product pages | the two highest-current documented 1S modules found (PCB-LIS1A15, PCB-Li-1S15A) |
| `pages/tenergy-1s-8p5a-22a.html` | power.tenergy.com | Tenergy 1S PCB, working 8.5 A, cutoff 22 A (SKU 32174) |
| `littelfuse-299-maxi32v.pdf` (3 p) | littelfuse.com assetdocs (Wayback copy, direct 403) | Littelfuse MAXI 299 series blade fuse, 32 V, revised 6 January 2025 |
| `littelfuse-287-atof.pdf` (3 p) | farnell.com/datasheets/3767635.pdf | Littelfuse ATOF 287 series blade fuse, 32 V, revised 18 August 2022 |
| `littelfuse-maxi-mah-inline.pdf` (1 p) | littelfuse.com assetdocs maxi-mah-datasheet (Wayback copy) | Littelfuse MAXI MAH series in-line holder |
| `littelfuse-maxi-152-holder.pdf` (2 p) | littelfuse.com assetdocs maxi-152-datasheet (Wayback copy) | Littelfuse MAXI 152 series in-line splashproof holder |
| `littelfuse-ato-fha-inline.pdf` (1 p) | littelfuse.com assetdocs ato-fha-datasheet (Wayback copy) | Littelfuse ATO FHA series in-line holder (20 A / 30 A) |
| `keystone/M65p39.pdf` to `M65p44.pdf` | keyelco.com/userAssets/file/M65pNN.pdf | Keystone catalogue M65, fuse clips and holders section (p40 MAXI holder 3555 / 3555-2, p41 ATO holders 3557, p42 MINI holders incl. 3568) |
| `amass-xt60-spec-tme.pdf` (2 p) | tme.eu/Document/.../XT60 SPEC.pdf (Wayback copy, direct 403) | Changzhou Amass XT60-F (p1) and XT60-M (p2) specification V1.2 |
| `amass-xt60e-m-shoptronica.pdf` (1 p) | shoptronica.com/ficheros/XT60E-M.pdf | Amass XT60E-M (panel mount) specification with temperature-rise data |
| `semitec-at-p12-13.pdf` (2 p) | semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf | Semitec AT thermistor catalogue pages 12 to 13 (103AT-2 dimensions, table, R-T table, handling) |
| `semitec-catalog-129M.pdf` (28 p) | semitec-global.com/uploads/2022/01/NTC_thermistors_Circuit_129M.pdf | Semitec catalogue 129M (same AT pages at p12 to p13, plus general definitions) |
| `semitec-103at-2-kempston.pdf` (2 p) | files.kempstoncontrols.com | distributor copy of the AT table |
| `murata-nxrt15xh103fa1b.pdf` (3 p) | datasheet.octopart.com (copy of the Murata product-search sheet, updated 14 June 2022) | Murata NXRT15XH103FA1B010 |
| `renders/*.png` | made here with pdftoppm | the Semitec dimension page, the two NexFET curve pages, Keystone p40, used to read drawings |

Helper scripts `pg.py` (page locator over the extracted text) and `tbl.py` (HTML table extractor) are in the folder; every `.txt` is the `pdftotext -layout` extraction of the PDF beside it.

Refused or not found: littelfuse.com (403 to curl, Wayback served the sheets), tme.eu documents (403, Wayback served the XT60 spec), mouser.com PDFs (JavaScript challenge, no archive copy), lcsc.com datasheet links (HTML), akkuparts24.de (403), bestechpower.com (certificate mismatch on www, category URLs 404), batteryspace.com category page (404, product pages fine). No document with a nickel-strip welding schedule exists in the Samsung set; the specification only rules how the cell may be joined (section 1.6).

## 1. Samsung INR18650-35E (Spec. Ver. 1.1, `samsung-35e-orbtronic.pdf`)

### 1.1 Dimensions and mass

- Cell dimension: height Max. 65.25 mm, diameter Max. 18.55 mm (section 3.11, p3; Fig. 1 outline, p4). The specification gives maxima only, no nominal and no tolerance band. The June 2015 tentative technical report shows "Φ max 18.50 mm, max 65.25 mm, with tube" (`samsung-35e-conrad.pdf` p2); the released Ver. 1.0 and 1.1 raised the diameter maximum to 18.55, so 18.55 is the design figure.
- Cell weight: 50 g max (section 3.10, p3; Ver. 1.0 section 3.13, `samsung-35e-akkuzentrum.pdf` p4; technical report p2 "Max. 50.0 g").
- Reseller figures, not Samsung's: "Diameter 18.55 mm ± 0.1, Height 65.25 mm ± 0.15, Weight 48 g ± 1" (`samsung-35e-relectro.pdf` p1). Not used for the envelope; quoted so that nobody reads them back as manufacturer tolerances.

### 1.2 Capacity and voltage

- Standard discharge capacity Min 3,350 mAh (charge 0.5 C = 1,700 mA to 4.2 V, cut-off 0.02 C = 68 mA; discharge 0.2 C = 680 mA to 2.65 V; 1 C = 3,400 mA) (section 3.1, p3). Rated capacity at 1 C ≥ 3,250 mAh (section 7.3, p5).
- Typical capacity 3,450 mAh, 3,482 mAh / 12.62 Wh measured at 0.2 C (technical report p2, p3); at 3.5 A 3,468 mAh / 11.94 Wh, at 7.0 A 3,429 mAh / 11.37 Wh, at 10.0 A 3,379 mAh / 10.98 Wh (technical report p6).
- Charging voltage 4.2 V, nominal 3.60 V, CC-CV (sections 3.2 to 3.4, p3). Discharge cut-off 2.65 V (section 3.9, p3). Initial internal impedance ≤ 35 mΩ at AC 1 kHz (section 7.4, p5).
- Rate capability: 8,000 mA gives 92% of the standard capacity (section 7.8, p7). Cycle life ≥ 2,010 mAh (60%) after 500 cycles at 1,020 mA charge / 3,400 mA discharge (section 7.9, p7). Shipped at 3.49 to 3.69 V (section 7.11, p7).

### 1.3 Current limits

- Charging current: standard 1,700 mA (cycle life 1,020 mA), standard charging time 4 h; Max. charge current 2,000 mA "not for cycle life" (sections 3.5 to 3.7, p3). The tentative report said Max. 1,500 mA (technical report p2); the released specification's 2,000 mA governs, and the module never sees it (section 1.5).
- Max. discharge current: 8,000 mA for continuous discharge; 13,000 mA not for continuous discharge (section 3.8, p3).

### 1.4 Temperature windows

- Operating temperature (cell surface): charge 0 to 45 °C, discharge -10 to 60 °C (section 3.12, p3).
- Storage: 1 year -20 to 25 °C, 3 months -20 to 45 °C, 1 month -20 to 60 °C, at ex-factory 30% charge with more than 80% recovery (section 3.13, p3).
- Capacity versus temperature at 3,400 mA: 40% at -10 °C, 97% at 23 °C, 97% at 40 °C (section 7.5, p6); charging at 0 °C returns 60% of capacity, at 23 °C and 45 °C 100% (section 7.6, p6).
- Pack design guideline table (p14): for "Portable IT" 4.20 V charge voltage, full-charge cut-off 0.05 C, re-charge at 4.10 V, NCA minimum voltage to terminate discharging 2.50 V, NCA minimum over-discharge protection 2.30 V (2.00 V for power tools, 2.50 V for the other classes), BMS shut-down 2.00 V, BMS consumption after shut-down 10 µA per cell, do not charge below 1.00 V, pre-charge 1.0 to 3.0 V at 0.1 to 0.5 C.

### 1.5 Derived 1S12P figures (twelve cells in parallel)

| Quantity | Per cell (document) | 1S12P |
|---|---|---|
| Capacity, specification minimum | 3,350 mAh (p3) | 40.2 Ah |
| Capacity, typical | 3,450 mAh (technical report p2), 3,482 mAh at 0.2 C (p3) | 41.4 Ah, 41.8 Ah |
| Energy, typical at 0.2 C | 12.62 Wh (technical report p3) | 151 Wh |
| Continuous discharge, cell limit | 8 A (p3) | 96 A |
| Non-continuous discharge, cell limit | 13 A (p3) | 156 A |
| Standard charge current | 1.7 A (p3) | 20.4 A |
| Maximum charge current | 2.0 A (p3) | 24 A |
| Charge cut-off, specification | 0.02 C = 68 mA (p3) | 0.82 A |
| Charge cut-off, pack guideline "Portable IT" | 0.05 C (p14) | 2.0 A |
| Internal impedance, max | 35 mΩ (p5) | 2.9 mΩ |
| Mass, max | 50 g (p3) | 600 g |

The brief's "42 Ah" is 12 x 3.5 Ah, the reseller's nominal figure (`samsung-35e-relectro.pdf` p1); the Samsung minimum is 40.2 Ah and the typical about 41.5 Ah. The A19 charger's 3 A is 0.25 A per cell (0.074 C), far below the standard 0.5 C; at 3 A the 40.2 Ah minimum needs about 13.4 h plus the CV tail, which agrees with the appendix's "about 14 h". The appendix 32.24 line "its weight (about 1.4 kg of cells)" is wrong by a factor of two: twelve 35E cells are 600 g maximum (section 3.10, p3).

### 1.6 Joining the cells: what the sheet says (no strip schedule exists)

- "The cell should not be soldered directly with leads. Namely, the cell should be welded with leads on its terminal and then be soldered with wire or leads to soldered lead. Otherwise, it may cause damage of component, such as separator and insulator, by heat generation." (Proper Use and Handling, section 6.1, p11; Ver. 1.0 p20 says the same).
- "Don't heat partial area of the battery with heated objects such as soldering iron." (p16) and "Don't solder on the battery directly." (p17).
- Cells must be visually inspected before assembly and rejected on sleeve damage, can distortion or electrolyte smell (section 7.1, p11); the battery needs shock absorbers and a distance from heat sources (sections 6.2, 6.3, p11); a reverse-connection-proof terminal design is required (section 6.5, p11); the system must have an over-discharge cut and the charger a cell-voltage detector (section 3.3, p10).
- Samsung gives no nickel-strip thickness, weld energy or electrode schedule anywhere in the three copies; the 0.15 mm strip of the brief is a build choice, not a Samsung figure.

## 2. Single-cell protection at 30 A continuous

### 2.1 Documented 1S modules: none reaches 30 A

Searched: Batteryspace (AA Portable Power Corp), Tenergy, JBD (Jiabaida), Daly, BesTech Power, plus generic "1S 30 A" searches. Findings:

- Batteryspace PCB-LIS1A15, sold as "PCB for 3.7 V Li-ion battery, 20 A limit" (`batteryspace-prod-spec-274.pdf` p1 and `pages/batteryspace-1s-20a.html`): charge 4.2 V CC/CV; consumption ≤ 10 µA; maximal continuous charging current 15 A; maximal continuous discharging current 15 A, 20 A for 5 minutes; over-charge detection 4.25 ± 0.025 V, delay 0.5 to 2.0 s, release 4.05 ± 0.05 V; over-discharge detection 2.50 ± 0.062 V, delay 14 to 26 ms, release 3.0 ± 0.075 V; over-current detection voltage 0.2 V ± 0.015 V, detection current 35 ± 5 A (adjustable), delay 8 to 16 ms, release on cut load; short circuit 200 to 800 µs; B- to P- resistance ≤ 20 mΩ; -40 to +85 °C operating; weight 17.0 g; 65 x 10 x 2.5 mm; MOSFET options AON6354 (V2) or AON6504 (V1); no thermistor. This is the highest-current documented 1S board found: 15 A continuous, not 30 A.
- Batteryspace PCB-Li-1S15A, "1S at 15 A limited, for 20700 / 21700 cells" (`pages/batteryspace-1s-15a.html`): 15 A continuous charge and discharge; over-charge 4.250 ± 0.050 V (release 4.050 ± 0.050 V); over-discharge 2.500 ± 0.100 V (release 3.000 ± 0.100 V); over-current 65 ± 10 A, 5 to 20 ms; short 200 to 800 µs; ≤ 20 mΩ; round board Ø19.5 x 1 mm; terminals P+, P-, B+, B- and T = "10K NTC" (the only documented 1S board with a thermistor terminal). 15 A only, and its Ø19.5 form is for a cell-end mount.
- Tenergy 1S PCB SKU 32174 (`pages/tenergy-1s-8p5a-22a.html`): over-charge 4.25 ± 0.05 V (release 4.05 ± 0.05 V), over-discharge 2.50 ± 0.10 V, rated operational current ≤ 8.5 A, over-current 22 ± 4 A, 28.8 x 7 x 2.5 mm, no NTC. Tenergy's other 1S boards are 1.5 to 9 A.
- JBD: the catalogue search returns 3S and higher only (no 1S product). Daly: the "1S" search returns no product. BesTech: the site's category pages did not resolve (404 on the 1S Li-ion category, certificate mismatch on www), so no BesTech sheet could be verified. "Hongbo": no maker page or sheet was found under that name; the 1S boards sold under many brand names are the DW01 + 8205A pair at 2 to 12 A (search results only, no document).

Conclusion: no documented 1S module at 30 A continuous exists in the searched set. The best documented modules are 15 A (PCB-LIS1A15, PCB-Li-1S15A). A 30 A single-cell protector therefore has to be built from a protection IC and discrete MOSFETs (section 2.2), or the requirement relaxed to 15 A with a documented module (the kit's real load is far below 15 A; the 30 A figure of appendix 32.24 AY is a margin ruling for the owner).

### 2.2 TI BQ2970 external-FET design sized for 30 A (`ti-bq2970.pdf`)

How the IC senses current: "Voltage sensing across external FETs for overcurrent protection (OCP) is within ±5 mV (typical)" (Features, p1); the VSS pin "for either Vds sensing or external sense resistor sensing" (section 5.1.2, p4). There is no sense resistor in the reference design: the drop across the two back-to-back N-channel FETs between CELL- and PACK- is the measurement (Typical Application, Figure 9-1, p19). The V- pin carries a 2.2 kΩ series resistor to PACK-, BAT gets a 330 Ω plus 0.1 µF filter, and a 5 MΩ gate-source resistor per FET is optional (p19, p20; EVM schematic and BOM: R1 330 Ω, R2 2.2 kΩ, R3/R4 5.1 MΩ, C1 0.1 µF, `ti-sluuaz3-bq29700evm.pdf` p2, p4).

Fixed thresholds (Device Comparison Table, p3):

| Part | OVP / delay | UVP / delay | OCC / delay | OCD / delay | SCD / delay |
|---|---|---|---|---|---|
| BQ29700 | 4.275 V / 1.25 s | 2.800 V / 144 ms | -0.100 V / 8 ms | 0.100 V / 20 ms | 0.5 V / 250 µs |
| BQ29728 | 4.280 V / 1.25 s | 2.800 V / 144 ms | -0.100 V / 8 ms | 0.150 V / 8 ms | 0.5 V / 250 µs |
| BQ29732 | 4.280 V / 1.25 s | 2.500 V / 144 ms | -0.100 V / 8 ms | 0.190 V / 8 ms | 0.5 V / 250 µs |

Recovery delays: OVP 12 ms, UVP/OCC/OCD 8 ms (note 1, p3). Accuracy: VOVP ±20 mV (0 to 85 °C), OVP hysteresis 100 mV, VUVP ±50 mV, UVP hysteresis 100 mV (p6); VOCD and VOCC ±10 mV at 25 °C, ±15 mV over -40 to 85 °C (p6); OCD releases when BAT - V- > 1 V (p6). Operating range BAT - VSS 1.5 to 8 V, BAT - V- 1.5 to 28 V; supply 4 µA typical, 5.5 µA max (p5); PACK+ input range VSS - 0.3 V to 12 V (p1). Gate drive: VOH (discharge FET high output) 3.4 to 3.7 V at BAT = 3.8 V, IOH = -30 µA (p5), so the FET gate never sees more than the cell voltage. Package WSON-6 DSE, 1.50 x 1.50 x 0.75 mm (p1); RθJA 190.5 °C/W (p5), irrelevant at 4 µA. Orderable BQ29700DSER (3000 reel) / BQ29700DSET (250 reel), -40 to 85 °C (addendum, p31 to p32 of the file).

TI's sizing rule (Detailed Design Procedure, p19 to p20): total resistance tolerated across the two FETs = VOCD / I_max (their example 100 mV / 7 A = 14.3 mΩ); the total Rds(on) "should factor in any worst-case parameter based on the FET ON resistance, derating due to temperature effects and minimum required operation, and the associated gate drive (Vgs)"; FET criteria Vdss and Rds at Vgs = 3.5 V; "Imax > 50 A to allow for short Circuit Current condition for 350 µs (max delay timer)", the short current being pack voltage over cell resistance + 2 x Rds + trace (p20). Layout: FET-to-FET connection very close (no extra drop in the sense path), the BAT RC close to the IC, heat spreading for the FETs (section 9.4.1, p22).

MOSFET pair: TI CSD17570Q5B (`ti-csd17570q5b.pdf`): 30 V, Rds(on) 0.74 mΩ typical / 0.92 mΩ max at Vgs = 4.5 V, ID = 50 A; 0.56 / 0.69 mΩ at 10 V (p3); continuous drain current 53 A at TA = 25 °C on a 1 in² 2 oz pad (RθJA 40 °C/W typical), 100 A package limited; pulsed drain current 400 A (pulse ≤ 100 µs) (p1); RθJC 0.8 °C/W, RθJA 50 °C/W max on the same pad (p3); SON 5 x 6 mm (p1). Figure 7 "On-State Resistance vs Gate-to-Source Voltage" (p5, render `renders/csd17570-p5-05.png`): at Tc 25 °C about 0.6 mΩ from 4 V upward and about 0.7 mΩ at 3.5 V; at Tc 125 °C about 1.0 mΩ from 5 V upward and about 1.2 mΩ at 3.5 V; below 3 V the curve rises steeply. Alternate CSD18510Q5B (`ti-csd18510q5b.pdf`): 40 V, 1.2 / 1.6 mΩ at 4.5 V, 0.79 / 0.96 mΩ at 10 V (p3), 42 A silicon limited, 400 A pulsed (p1); its higher Rds at the 3.4 V gate drive makes it the second choice.

Sizing at 30 A with the BQ29700 and one CSD17570Q5B per switch (two FETs in series, back to back):

- Total Rds at 25 °C: 1.84 mΩ (max) / 1.48 mΩ (typical). Drop at 30 A: 55 mV / 44 mV, below the 85 mV minimum OCD threshold (100 mV - 15 mV, p6): 30 A continuous does not trip.
- Hot: at Tc 125 °C and the 3.4 V minimum gate drive (p5 of the BQ2970 sheet), Figure 7 gives about 1.2 mΩ per FET, 2.4 mΩ total, 72 mV at 30 A: still under 85 mV. The OCD trip current is 100 mV / 1.84 mΩ = 54 A (max Rds, 25 °C) to 68 A (typical), falling to about 42 A at 125 °C.
- Near the over-discharge threshold (BAT 2.8 to 3.0 V) the gate sees under 3 V, where Figure 7 rises steeply; a 30 A load at end of discharge trips OCD early. That is the protective direction and costs nothing at the kit's real load (a few amperes), but if a hard 30 A hold-in is wanted at 2.8 V, the BQ29728 (OCD 150 mV, same 4.280 / 2.800 V window, p3) allows 4.5 mΩ total (2.25 mΩ per FET) at 30 A with a trip of 82 A (max Rds) to 101 A (typical); or a second CSD17570Q5B in parallel per switch halves the drop (0.92 mΩ total max, 28 mV at 30 A) with the BQ29700 tripping at 109 A (max Rds). The BQ29732's 2.500 V UVP would sit below the specification's 2.65 V cut-off (section 1.2) although inside the pack guideline's 2.50 V NCA row (p14); not preferred.
- Dissipation at 30 A: 30² x 1.84 mΩ = 1.66 W total, 0.83 W per FET, about +42 °C at RθJA 50 °C/W (p3) on a 1 in² 2 oz pad each: junction about 67 °C at 25 °C ambient, about 102 °C at 60 °C ambient. At an 8 A load: 0.12 W total.
- Charge direction: OCC -100 mV trips at 54 A of charge current (max Rds); the 3 A charger never approaches it.
- Short circuit: SCD 0.5 V across 1.84 mΩ = 270 A, cleared in 250 µs (p3). The prospective short current of the 12P node is high: 4.2 V over (2.9 mΩ pack, section 1.5, + 1.84 mΩ FETs + about 3 mΩ of 12 AWG leads and the fuse's 1.4 mΩ, section 4) is roughly 500 A for 250 µs. The FET's 400 A pulsed rating is specified for 100 µs (p1, note 2); TI's design criterion is "Imax > 50 A ... for 350 µs" for a 7 A pack (p20). For this module the lead length between pack and FETs is part of the protection budget; keep the FETs at the pack end of the positive lead with the fuse in series (the MAXI 40 A does not open in 250 µs at 500 A: its I²t is 8,500 A²s, section 4, against 60 A²s in that pulse). Flag for the coordinator: verify the FET pulse capability against the measured pack impedance before the first short-circuit test, or add a third FET in parallel per switch.
- Sense resistor: none with the BQ29700 (a 1 mΩ shunt in the PACK- path would put 30 A at 85 mV, exactly the minimum OCD, so it cannot be used). With the BQ29728 a 1.0 mΩ shunt between the DSG FET source and PACK- (total 2.84 mΩ) gives 85 mV at 30 A against a 135 mV minimum threshold and a trip of 53 A typical, if a trip independent of Rds(on) drift is wanted; the sheet allows it ("external sense resistor sensing", p4).
- Thermistor: the BQ2970 has no TS input. The module's temperature cut-off is the charger's JEITA input on PCB-A (section 5) through the module's own 103AT-2, and Samsung's 0 to 45 °C charge window (section 1.4) is enforced there. If a cut-off inside the module is required, the S-8261 and R5405 have none either; a thermal fuse or a PTC in the strip path is the usual answer and no document for one was in scope.

### 2.3 Equivalent ICs from the other two makers

- ABLIC S-8261 (`ablic-s8261.pdf`, Rev. 5.5_00): overcharge 3.900 to 4.500 V in 5 mV steps, ±25 mV; overcharge hysteresis 0.1 to 0.4 V; overdischarge 2.000 to 3.000 V, ±50 mV; overcurrent 1 detection voltage 0.050 to 0.300 V in 10 mV steps, ±15 mV; overcurrent 2 0.500 V fixed, ±100 mV; load short-circuit detection; 0 V charge selectable; 3.5 µA typical; -40 to +85 °C; SOT-23-6 (Features, p1). Same Vds sensing across the two N-channel FETs through the VM pin; R1 470 Ω (300 Ω to 1 kΩ) between VDD and the cell, R2 2 kΩ (300 Ω to 4 kΩ) between VM and PACK-, FET threshold voltage ≤ the overdischarge detection voltage (p24). Overcurrent 1 delay 4.5 / 9 / 18 ms options, overcurrent 2 delay 1.12 / 2.24 ms (p5). Nearest match to the BQ29700 window: S-8261ABMMD-G3MT2x, 4.280 V, hysteresis 0.20 V, 2.800 V, 0 V hysteresis, VIOV1 0.100 V, 0 V charge available (p4); with more Rds allowance: S-8261ACKMD-G4KT2x, 4.280 / 0.20 / 2.800 / 0 / 0.130 V (p4). The 30 A arithmetic of section 2.2 carries over one to one (85 mV minimum for the 0.100 V part, 115 mV for the 0.130 V part).
- Nisshinbo R5405 (`nisshinbo-r5405.pdf`, EA-215-201014): 1-cell protector, SOT-23-6 / DFN(PLP)1616-6 / DFN1814-6 (p1); over-charge 4.0 to 4.5 V in 5 mV steps ±25 mV, over-discharge 2.0 to 3.0 V in 0.1 V steps ±2.5%, excess discharge-current 0.05 to 0.20 V in 5 mV steps ±15 mV, excess charge-current -0.05 to -0.20 V; delays 1.0 s / 20 ms / 6 or 12 ms / 8 or 16 ms / 200 to 400 µs; 4.0 µA typical; absolute maximum 30 V (p2). Application: R1 330 Ω, C1 0.01 µF, R2 1 kΩ, R1 < 1 kΩ, R1 + R2 ≥ 1 kΩ, R2 ≤ 10 kΩ (p18). Code list (p6, p7): R5405x106EC 4.275 / 2.300 / 0.100 / -0.100 V, 1 s / 20 ms / 6 ms / 8 ms / 200 µs, 0 V charge OK; R5405x128EC 4.280 / 2.800 / 0.050 / -0.100 V (its 50 mV excess-current threshold is too low for 30 A through 1.84 mΩ); R5405N311KD 4.280 / release 4.080 / 2.300 / release 2.900 / 0.130 / -0.100 V. The brief's "Ricoh R5460" is Nisshinbo's 2-cell protector (`nisshinbo-r5460-rs.pdf` p1, "Li-ION/POLYMER 2-CELL PROTECTOR"); it does not apply to a 1S module, the 1-cell family is the R5405.

## 3. Module envelope

Inputs: cell Ø 18.55 max x 65.25 max (section 1.1); nickel strip 0.15 mm on the terminal faces only; wrap 0.5 mm all round (brief). Cells lie flat in one layer with parallel axes; a "row" is the cells side by side across the diameter direction, rows sit end to end along the length. Adjacent rows are placed head to head and tail to tail so that the strips meeting at a row junction carry the same polarity; the conservative count keeps two strips at every junction (one per row) plus one at each outer end. One bus strip along a flat face joins the like-polarity row strips; it adds 0.15 mm to the thickness (on a side it would add 0.15 mm to the width instead).

| Arrangement | Cell block W x L x T | With strips (length +n x 0.15, thickness +0.15 bus) | With 0.5 mm wrap (+1.0 each) | Footprint |
|---|---|---|---|---|
| 4 x 3 (4 across, 3 rows) | 74.20 x 195.75 x 18.55 | 74.20 x 196.65 (6 strips) x 18.70 | **75.2 x 197.7 x 19.7** | 14,860 mm² |
| 6 x 2 (6 across, 2 rows) | 111.30 x 130.50 x 18.55 | 111.30 x 131.10 (4 strips) x 18.70 | **112.3 x 132.1 x 19.7** | 14,830 mm² |

Shared junction strips (one strip welded from both sides is not practical, so this is the lower bound only) would take 0.30 mm off the 4 x 3 length and 0.15 mm off the 6 x 2 length.

Flatness: both are one cell thick, 19.7 mm wrapped (19.55 without the face bus), and both cover the same area; neither is flatter than the other. What differs is the plan shape: 4 x 3 is a 75 x 198 bar, 6 x 2 a 112 x 132 slab. Against the candidate location in the appendix (MESHSAT-791 paragraph: the east floor band, about 87 mm between PCB-A's east edge and the case wall, 283 mm long), only the 4 x 3 fits (75.2 wide leaves 11.8 mm for enclosure walls and cradle; 197.7 long leaves 85 mm of the band); the 6 x 2 at 112.3 mm does not fit the band. The appendix's "about 205 x 85 x 30 mm with the enclosure" is consistent with the 4 x 3 figure plus 3.5 to 5 mm of wall each side and 10 mm of height for the BMS and vent path.

Mass: cells 600 g maximum (12 x 50 g, section 1.1). Nickel strips for the 4 x 3 (six row-end strips of about 75 mm plus two face buses of about 200 mm, 8 mm wide, 0.15 mm thick, 8.9 g/cm³): about 9 g. A 0.5 mm wrap over the 4 x 3 surface (about 40,600 mm²): about 20 cm³, about 27 g at 1.35 g/cm³. Wrapped pack about 640 g; with a protection board (17 g for the reference PCB-LIS1A15, `pages/batteryspace-1s-20a.html`), the MAXI fuse (5.7 g, section 4), holder, XT60 and leads about 0.7 kg complete. ASSEMBLY.md and the appendix must say 0.6 kg of cells, not 1.4 kg.

## 4. 40 A blade fuse and holder; XT60 rating

### 4.1 Fuse: Littelfuse MAXI 299 series, 40 A (`littelfuse-299-maxi32v.pdf`)

- Ratings: 32 V DC; interrupting 1000 A at 32 V DC; -40 to +125 °C environmental; terminals silver-plated (or tin-plated) zinc alloy, silver plating good to 150 °C at the terminal interface; housing PA66 UL 94 V-2; 5.7 g typical; ISO 8820-3:2002, SAE J 1888, SAE 2576; UL listed 20 to 80 A (p1). Part numbers: 0299040.ZXNV (Ag, 1200 per box), 0299040.L (Ag, 50), 0299040.TXN (Ag, 10), 0299040.ZXT (Sn, 1200) (p1).
- 40 A row: test cable 4 mm², typical voltage drop 75 mV, typical cold resistance 1.4 mΩ, typical I²t 8,500 A²s (p2). Dimensions (drawing p2): 29.2 long, 21.6 high overall, 8.9 thick, blade 0.8 thick, 8 wide.
- Time-current (p3): 100% of rating 360,000 s minimum; 135% 60 to 1,800 s; 200% 2 to 50 s; 350% 0.2 to 7 s; 600% 0.04 to 1 s. Derating of the 40 A part (p3): 40 A at -40 to 20 °C, 34 A at 65 °C, 30 A at 85 °C, 25 A at 110 °C, 22 A at 125 °C.
- ATO alternative: Littelfuse ATOF 287 series 40 A (`littelfuse-287-atof.pdf`): 32 V DC, 1000 A interrupting, 1.4 g, 0287040.PXCN (Sn) / 0287040.PXS (Ag) (p1); 40 A row test cable 6 mm², 96 mV drop, 1.44 mΩ, 3,300 A²s; 19.1 x 18.8 x 5.1, blade 0.65 thick (p2); 35 and 40 A: 100% 360,000 s min, 135% 0.75 to 600 s, 200% 0.15 to 5 s, 350% 0.08 to 0.5 s, 600% 0.15 s max (p3). The ATO body is smaller, but no ATO holder in the documented set is rated for 40 A (next item), so the MAXI is the recommendation.

### 4.2 Holder

- Littelfuse MAXI MAH series in-line holder, MAHC0001ZXJ (5 in / 127 mm leads) or MAHC0001ZXJA (150 mm) (`littelfuse-maxi-mah-inline.pdf` p1): current rating continuous 45 A, maximum 60 A, terminal 60 A; 32 V DC; 6 AWG UL-3288 150 °C leads; maximum operating temperature 80 °C; UL 94 V-2 thermoplastic; tethered cover; centre hole for bulkhead mounting. This is the in-line holder for the module's positive lead. (The 6 AWG lead is heavier than the 12 AWG of the XT60 path; it is spliced or crimped to the 12 AWG pigtail.)
- Littelfuse MAXI 152 series splashproof in-line holder (`littelfuse-maxi-152-holder.pdf`): 32 V DC, 60 A and 80 A bodies, IP54 / IP64 / IP67 versions, UL 94 V-0 or HB (p1); 01520006Z 60 A body, 01520010Z 60 A IP67 with set screw, cable seals for 2.5 to 6, 6 to 10 and 16 mm² (p2). Alternative if the module enclosure wants a sealed holder.
- PCB-mount alternative on the module's own board: Keystone 3555 clip / 3555-2 two-clip holder for MAXI blades (`keystone/M65p40.pdf`, render `renders/keystone-p40-1.png`): 0.51 mm copper contacts, tin-nickel plate; glass-filled nylon UL 94V-0; UL current rating 50 A at 500 V AC; -50 to +145 °C; 3555-2 body 35.8 long x 11.3 high, pins on 8.4 / 12.7 / 8.4 mm spacing with Ø3.9 mm holes (four places).
- Why not ATO holders: Littelfuse ATO FHA in-line holders are 20 A standard and 30 A heavy-duty (12 AWG leads) at 32 V DC (`littelfuse-ato-fha-inline.pdf` p1); the Keystone ATO PC-mount holder 3557 is UL 30 A (`keystone/M65p41.pdf`), and the MINI holder 3568 used on A18 is UL 30 A for 15 A MINI blades (`keystone/M65p42.pdf`). None is rated for a 40 A blade.

### 4.3 Coordination note

The Amass XT60 is rated 30 A continuous (section 4.4). A 40 A fuse protects the wiring against faults (its 200% point is 80 A for 2 to 50 s, p3), it does not protect the connector against a sustained 30 to 40 A overload. If the coordinator wants the fuse to coordinate with the connector, the same MAXI holder takes the 0299030 (30 A, 1.9 mΩ, 4,100 A²s) or 0299035 (35 A, 1.7 mΩ, 6,000 A²s) (p2). The electronic OCD of section 2.2 (54 to 68 A) sits between the fuse's 135% and 200% points either way.

### 4.4 Connector: Amass XT60 (`amass-xt60-spec-tme.pdf`, V1.2)

- XT60-F (p1) and XT60-M (p2): contact resistance 0.55 mΩ; rated voltage DC 500 V; rated current 30 A; instantaneous current 60 A; 1000 mating cycles; recommended cable 12 AWG (3.3 mm²); -20 to 120 °C; brass, gold plated; PA housing, UL94 V0.
- XT60E-M panel-mount receptacle (`amass-xt60e-m-shoptronica.pdf` p1): same 30 A / 60 A / 12 AWG / 500 V figures; temperature rise 27.8 °C at 30 A with 12 AWG, 85 °C at 30 A with 14 AWG, 124.8 °C at 60 A (14 AWG); CE/UL; -20 to 120 °C. The 12 AWG figure is the one to hold: 14 AWG at 30 A already runs the contact 85 °C above ambient.

## 5. Thermistor for the charger JEITA input on PCB-A

### 5.1 Semitec 103AT-2 (`semitec-at-p12-13.pdf`, catalogue pages 12 to 13)

- Table (p1): R25 10.0 kΩ, tolerance ±1%, B value (25/85 °C) 3435 K ±1%, dissipation factor approx. 2.0 mW/°C, thermal time constant approx. 15 s (63.2% step, sensor suspended in mid-air), rated power 10 mW at 25 °C, operating temperature -50 to 110 °C. The catalogue 129M repeats the page (`semitec-catalog-129M.pdf` p12) and lists the 103AT-2 R-T range separately (p11).
- Dimensions, Fig. 2 (p1, render `renders/semitec-at-p1-1.png`): resin head 3.7 max long, 4.0 max wide, 2.4 max thick; leads Ø0.5 tin-plated 42 alloy on 2.54 ± 0.25 pitch; 8.5 ± 1 from the head to the lead-pitch transition, 17 ± 1.5 overall from the head to the lead end (a bare-lead bead, no cable); colour code white for the 103AT-2. Weight is not stated.
- R-T table for the 103AT (p2, kΩ): -20 °C 67.77; -10 °C 42.47; 0 °C 27.28; 10 °C 17.96; 20 °C 12.09; 25 °C 10.00; 30 °C 8.313; 40 °C 5.827; 50 °C 4.160; 60 °C 3.020; 70 °C 2.228; 85 °C 1.451; 100 °C 0.9731; 110 °C 0.7576. The 0 °C (27.28 kΩ) and 60 °C (3.020 kΩ) rows are the values the BQ25798's fixed T1 / T5 comparators assume with its RT1 5.24 kΩ / RT2 30.31 kΩ network (see `respin-research-power-2026-09-04.md`, BQ25798 p46), and 45 °C interpolates to about 4.9 kΩ between the 40 and 50 °C rows.
- Handling (p2): bend leads no closer than 3 mm to the head, load under 2 N; solder no closer than 5 mm to the head with a 50 W iron for at most 7 s at 340 °C; resistance to soldering heat 10 s at 260 °C or 3.5 s at 350 °C with ΔR, ΔB within ±1%; tensile 2 N for 10 s vertical.
- Semitec offers the same element with lead wires (the AT-4 with PVC AWG30 leads 40 to 100 mm, Fig. 4, p1; the 103AT-4 is -30 to 90 °C) and the JT series with 25 to 100 mm leads (catalogue p9); for the pack sensor a lead-wire type or a bench-soldered pigtail on the 103AT-2 (5 mm rule) is the practical choice. The power research already noted LCSC C5346323 for the 103AT-2 with zero stock; it is a bench-fit part either way.

### 5.2 Murata NXRT15XH103FA1B (`murata-nxrt15xh103fa1b.pdf`, product-search sheet for the 010 lead length)

- Specifications (p2): resistance 10 kΩ at 25 °C, ±1%; B constant 25/50 °C 3380 K ±1%; B 25/80 °C 3428 K, B 25/85 °C 3434 K, B 25/100 °C 3455 K (reference values); maximum operating current 0.12 mA; rated power 7.5 mW at 25 °C; dissipation constant 1.5 mW/°C; operating -40 to 125 °C; thermal time constant 4 s; lead-wire type, size code 010 = 10 mm lead; mass 0.042 g; consumer grade (p1). The 030 and 040 suffixes are the 30 and 40 mm lead versions (distributor listings; no separate Murata sheet fetched).
- Equivalence: B25/85 3434 K against the Semitec's 3435 K, so the charger's fixed thresholds land within the tolerance band; the Murata bead is faster (4 s against 15 s) and smaller, the sheet shows the head only as a drawing (no numeric head size in the text), and UL1434 recognised (file E137188, p1). Either part serves the JEITA input; the 103AT-2 is the part the TI sheets name.

## 6. Recommended parts

| Part | Document file | Key figure |
|---|---|---|
| Samsung INR18650-35E, 12 pcs, welded 1S12P | `samsung-35e-orbtronic.pdf` p3, p4 | Ø18.55 x 65.25 max, 50 g max, 3,350 mAh min, 8 A continuous, charge 0 to 45 °C; 1S12P 40.2 Ah min, 96 A continuous, 600 g |
| TI BQ29700DSER | `ti-bq2970.pdf` p3, p5, p6 | OVP 4.275 V, UVP 2.800 V, OCD 100 mV (85 mV min), OCC -100 mV, SCD 0.5 V / 250 µs, WSON-6 1.5 x 1.5 |
| TI CSD17570Q5B, 2 pcs (one per switch; a second pair in parallel or the BQ29728 if the end-of-discharge hold-in at 30 A matters) | `ti-csd17570q5b.pdf` p1, p3, p5 | 30 V, 0.92 mΩ max at 4.5 V, 53 A continuous, 400 A pulsed, SON 5 x 6; 30 A gives 55 mV, trip 54 to 68 A |
| Alternate IC: ABLIC S-8261ABMMD-G3MT2x | `ablic-s8261.pdf` p1, p4, p24 | 4.280 / 2.800 / 0.100 V, SOT-23-6, R1 470 Ω, R2 2 kΩ |
| Alternate IC: Nisshinbo R5405x106EC | `nisshinbo-r5405.pdf` p2, p6, p18 | 4.275 / 2.300 / 0.100 V, 6 ms, R1 330 Ω, R2 1 kΩ |
| Fallback documented module (15 A): Batteryspace PCB-LIS1A15 | `batteryspace-prod-spec-274.pdf` p1 | 15 A continuous, 20 A 5 min, OCD 35 ± 5 A, 4.25 / 2.50 V, 65 x 10 x 2.5, 17 g, no NTC |
| Littelfuse MAXI 0299040.ZXNV (40 A) | `littelfuse-299-maxi32v.pdf` p1 to p3 | 32 V DC, 1.4 mΩ, 8,500 A²s, 30 A at 85 °C, 29.2 x 21.6 x 8.9 |
| Littelfuse MAHC0001ZXJ in-line MAXI holder | `littelfuse-maxi-mah-inline.pdf` p1 | 45 A continuous, 60 A max, 6 AWG leads, 80 °C max |
| PCB alternative: Keystone 3555-2 MAXI holder | `keystone/M65p40.pdf` | UL 50 A, 35.8 x 11.3, Ø3.9 holes on 8.4 / 12.7 / 8.4 |
| Amass XT60-M / XT60-F (XT60E-M for the panel side) | `amass-xt60-spec-tme.pdf` p1, p2; `amass-xt60e-m-shoptronica.pdf` p1 | 30 A rated, 60 A instantaneous, 12 AWG, 500 V DC, 27.8 °C rise at 30 A with 12 AWG |
| Semitec 103AT-2 | `semitec-at-p12-13.pdf` p1, p2 | 10 kΩ ±1%, B25/85 3435 K ±1%, 27.28 kΩ at 0 °C, 3.020 kΩ at 60 °C, head 3.7 x 4.0 x 2.4 max, leads Ø0.5 on 2.54, 17 ± 1.5 long |
| Alternate: Murata NXRT15XH103FA1B030 | `murata-nxrt15xh103fa1b.pdf` p2 | 10 kΩ ±1%, B25/85 3434 K, 4 s, -40 to 125 °C |

Envelope figures (wrapped pack, one cell thick, section 3):

- 4 x 3: 75.2 x 197.7 x 19.7 mm, about 640 g wrapped, about 0.7 kg with protection board, fuse, holder and connector. Fits the 87 mm east band.
- 6 x 2: 112.3 x 132.1 x 19.7 mm, same mass and thickness. Does not fit the 87 mm band.

## 7. Open points for the coordinator

1. The 30 A continuous requirement (appendix 32.24 AY) has no documented off-the-shelf 1S module behind it; the choice is the BQ29700 discrete design of section 2.2 on the module's own small board, or a documented 15 A module (PCB-LIS1A15, or the PCB-Li-1S15A which brings a 10 kΩ NTC terminal) with the requirement relaxed. Either way the temperature cut-off during charge lives in the charger's JEITA input on PCB-A, not in the protector.
2. Short-circuit pulse rating of the FETs against the 12P node's prospective current (section 2.2): verify on the bench before the first short test, or fit a third FET per switch.
3. Fuse versus connector: 40 A blade over a 30 A connector (section 4.3); decide whether a 30 or 35 A MAXI is wanted instead.
4. ASSEMBLY.md and the appendix carry "about 1.4 kg of cells"; the sheet gives 600 g for twelve cells.
5. The "42 Ah" of the brief is the nominal 12 x 3.5 Ah; the Samsung minimum is 40.2 Ah, typical about 41.5 Ah.
