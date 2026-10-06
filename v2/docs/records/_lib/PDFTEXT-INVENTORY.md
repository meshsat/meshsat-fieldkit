# PDFTEXT-INVENTORY: every records script that mentions pdftotext, and what W34 did with it (MESHSAT-1357, Q-41 item 1)

DONE: the enumeration (section 2), the location decision (section 3), the helper, the re-take script and the regression, 25 generators
converted (section 4: the brief's six records, then every remaining run-time caller outside section 5); W36's findings applied by W37
(section 7: F-P1, F-P2, F-R1, F-R2, F-K5 corrected; F-C1 stated; the integration order of F-K1 to F-K3 in section 6); W53's finding
closed by W55 (section 8: l8p_c4.py's undeclared read declared, every converted generator and reader run with the tools refused, the
static declaration check). NOT DONE: section 5's 15 scripts, each for its stated reason. NEXT: the coordinator's adoption in set 32
(sections 6 and 8).

Author W34 (tooling, inside the records), 6 October 2026 (Europe/Amsterdam), branch `fnd/w34pdftext` from `aed4bd23` (set 31's
regenerated lineage). This branch changes HOW a generator obtains a maker's PDF text, never WHAT it computes from it: no verdict, figure,
claim or design moves. It commits no `.out`: the coordinator regenerates every output at SET 32's integration, so the branch is adopted in
the next set with the cascade (section 6). Prototype design throughout: nothing in the kit is built, bought, powered or measured.

## 1. The defect and the correction

The records' generators ran `pdftotext` when they ran, so an output depended on the host's poppler build and data. On 6 October 2026
the JST VH catalogue (`v2/vendor/connectors/jst-vh-catalogue.pdf`, CID Type 0C fonts with Identity-H) extracted to 184 bytes on a box
image without `poppler-data` against the runner's 39318; 151 tests of set 30's first suite box failed and six record modules had to run
on a second box (`_runs/int30/QUEUE.md`, Q-41 and the entries of 08:35 to 09:40 CEST). The outputs pinned each PDF's digest, never the
text that was read. Correction (the coordinator's ruling, authority SESSION): one helper (`pdftext.py`) that returns the committed text
and refuses when it is absent, one re-take script (`retake_pdf_text.py`) that takes it on the runner (Debian 12, pdftotext 22.12.0,
poppler-data 0.4.12-1), every converted generator reading through the helper and printing each text's sha256 as an input line beside
the PDF's own pin, and the regression `v2/ecad/tools/tests/test_pdftext_input.py`.

## 2. The enumeration (base `aed4bd23`; 63 files; classified by reading each call, the converted ones also by a census run)

The census: every converted generator was first run once on the runner, unchanged, with a logging `pdftotext` first on PATH (it
recorded the arguments and ran the real tool); every output equalled its committed `.out` byte for byte, and the arguments are the
extractions its PDFTEXT table declares (l4e8's from its own page() calls, read from its source; a module's table holds its own reads,
not those of a module it imports). "Named in the file" lists the PDF paths a script's text names (a static reading, not a run).

| Class | Files |
|---|---|
| RUN-TIME EXTRACTION, CONVERTED | 25 |
| RUN-TIME EXTRACTION THROUGH ANOTHER SCRIPT'S READER, CONVERTED (W55; not in the census by name) | 1 |
| RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | 6 |
| RUN-TIME EXTRACTION, NOT CONVERTED (accepted Layer 3) | 5 |
| RUN-TIME EXTRACTION, NOT CONVERTED (the coordinator's checker) | 1 |
| RUN-TIME EXTRACTION, NOT CONVERTED (historical) | 3 |
| FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | 8 |
| DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | 15 |
| total | 64 (63 by name at the base, and W55's row) |

| Script (under `v2/docs/records/`) | Class | Why | PDFs (paths under `v2/vendor/`) | Test modules that name it |
|---|---|---|---|---|
| `a1elec/gauge_scale.py` | RUN-TIME EXTRACTION, NOT CONVERTED (historical) | an early record's generator (no test module reads it); out of the brief's six and of the set's failing modules | 1 committed, 0 held back (named in the file): `battery/ti-sluuaq3a-bq4050-trm.pdf` | none |
| `cx1/checks/check-1-phase1.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | a filed check's text | 0 committed, 0 held back (named in the file) | none |
| `d6dec/box/basis_check.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | the rented box's text cache for a one-off basis check | 0 committed, 0 held back (named in the file) | none |
| `d6dec/make_basis_md.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | prose naming a reading taken earlier | 3 committed, 0 held back (named in the file): `power/ltc2954.pdf`, `sensirion/sgp41-datasheet.pdf`, `ti/ti-tmp117-temperature.pdf` | none |
| `d6rel/revision_scan.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | prints revision lines for a person to read | 0 committed, 0 held back (named in the file) | none |
| `d8dec31/ledger_pages.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | a one-off quote check over the ledger's pages | 0 committed, 0 held back (named in the file) | none |
| `efuse/efuse_check.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 15 committed, 2 held back (declared in its PDFTEXT table): `connectors/jst-ph-catalogue.pdf`, `connectors/jst-sh-catalogue.pdf`, `connectors/jst-vh-catalogue.pdf`, `connectors/wurth-wr-bhd-idc-socket-61201623021.pdf`, `connectors/wurth-wr-bhd-idc-socket-61202623021.pdf`, `connectors/wurth-wr-cab-ribbon-63911615521cab.pdf`, `connectors/wurth-wr-cab-ribbon-63912615521cab.pdf`, `connectors/wurth-wr-com-usb3-a-692122030100.pdf`, `power/ti-tps2595-efuse.pdf`, `power/tps2596.pdf`, `ti/ti-lm5069.pdf`, `ti/ti-tps2065c-slvsau6i.pdf`, `ti/ti-tps22810-load-switch.pdf`, `ti/ti-tps25740.pdf`, `ti/tps23861-datasheet.pdf`; held back: `ti/held/ti-tps1663-slvset9g.pdf`, `ti/held/ti-tps4811-q1-slusee5e.pdf` | test_efuse |
| `int16/apply_hold_back_panjit.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | a one-off apply script (integration set 16) | 1 committed, 1 held back (named in the file): `power/panjit-ss2020fl-series.pdf`; held back: `power/held/panjit-ss2020fl-series.pdf` | none |
| `l3batt/tablet.py` | RUN-TIME EXTRACTION, NOT CONVERTED (accepted Layer 3) | accepted Layer 3 record; its source is pinned by sha in a filed check | 3 committed, 2 held back (named in the file): `battery/ti-csd18510q5b.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-tps25740.pdf`; held back: `tablet/held/samsung-galaxy-tab-active5-spec-sheet.pdf`, `tablet/held/zebra-et40-et45-spec-sheet-en-us.pdf` | none |
| `l3feas/hf_wab.py` | RUN-TIME EXTRACTION, NOT CONVERTED (accepted Layer 3) | accepted Layer 3 record; its source is pinned by sha in a filed check | 1 committed, 0 held back (named in the file): `ti/bq25731-datasheet.pdf` | none |
| `l3feas/solar_interface.py` | RUN-TIME EXTRACTION, NOT CONVERTED (accepted Layer 3) | accepted Layer 3 record; its source is pinned by sha in a filed check | 2 committed, 0 held back (named in the file): `power/lt8705a.pdf`, `solar/renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf` | none |
| `l3plane/curve_readings.py` | RUN-TIME EXTRACTION, NOT CONVERTED (accepted Layer 3) | accepted Layer 3 record; its source is pinned by sha in a filed check | 2 committed, 0 held back (named in the file): `power/lt8705a.pdf`, `ti/lm5176-datasheet.pdf` | none |
| `l3plane/energy_basis.py` | RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | accepted Layer 3; in the l4e7 KEY's files part; source pinned by l3batt, l3feas, l3plane, l4e_replay and a filed check | 1 committed, 0 held back (named in the file): `battery/samsung-35e-conrad.pdf` | test_l3r2 |
| `l3plane/vbus20_range.py` | RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | accepted Layer 3; in the l4e7 KEY's files part; source pinned by energy_basis.py and a filed check | 3 committed, 1 held back (named in the file): `passives/yageo-rc-l-series-v12.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf`; held back: `passives/held/uniroyal-series-11cd644d.pdf` | none |
| `l3plane/weather_basis.py` | RUN-TIME EXTRACTION, NOT CONVERTED (accepted Layer 3) | accepted Layer 3 record; its source is pinned by sha in a filed check | 1 committed, 0 held back (named in the file): `battery/samsung-35e-orbtronic.pdf` | none |
| `l4close/verify_risks.py` | RUN-TIME EXTRACTION, NOT CONVERTED (the coordinator's checker) | the coordinator's checker of Layer 4's closure; it runs against an exported tree named as its argument, where a held-back sheet's text is absent by construction, so its reading route is the coordinator's to set | 17 committed, 8 held back (named in the file): `battery/pcm/rubitherm-rt57hc-2026-01-21.pdf`, `bosch/bosch-bme688.pdf`, `diodes/diodes-ap2112-ldo.pdf`, `diodes/diodes-ap63200-series-buck.pdf`, `diodes/diodes-ap64500.pdf`, `passives/milliohm-hojlr2512-series.pdf`, `power/littelfuse-smcj-series-tvs.pdf`, `power/lt8705a.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-pcm2912a.pdf`, `ti/ti-sn74lv1t08.pdf`, `ti/ti-sn74lvc2g07.pdf`, `ti/ti-tlv758p.pdf`, `ti/ti-tmp117-temperature.pdf`, `ti/ti-tps62933.pdf`, `ti/ti-tusb8041.pdf`; held back: `passives/held/vishay-wsl-30100-2023-11-23.pdf`, `power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf`, `ti/held/ti-bq25730-sluse65a.pdf`, `ti/held/ti-csd17577q5a-slps516.pdf`, `ti/held/ti-csd17578q5a-slps526.pdf`, `ti/held/ti-csd19536ktt-slps540c.pdf`, `ti/held/ti-tlv755p-c404027.pdf`, `ti/held/ti-tps4811-q1-slusee5e.pdf` | test_l4close |
| `l4e/l4e_replay.py` | RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | in the l4e7 KEY's files part; source pinned by sha in l4e13, l4e5 and l4e7_stage_settings.py | 4 committed, 2 held back (named in the file): `mitsubishi/ra30h1317m1-datasheet.pdf`, `power/lt8705a.pdf`, `wifi/asiarf-AW7915-AED_V1.pdf`, `xenarc/xenarc-709gnk-product-manual-v2.pdf`; held back: `solar/held/sunpower-flex-safety-installation-524958-revf.pdf`, `solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf` | test_l4e5, test_l4e7 |
| `l4e10/l4e10_cell_thermal.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 9 committed, 6 held back (declared in its PDFTEXT table): `battery/eaton-scf9550-elx1135.pdf`, `battery/heater/rs-pro-245-556-heater-mat-sheet.pdf`, `battery/molicel-inr18650-p28a-v1.pdf`, `battery/pcm/rubitherm-rt57hc-2026-01-21.pdf`, `battery/samsung-35e-akkuzentrum.pdf`, `battery/samsung-35e-orbtronic.pdf`, `battery/ti-bq4050.pdf`, `battery/ti-bq77207.pdf`, `battery/ti-sluuaq3a-bq4050-trm.pdf`; held back: `battery/held/lg-inr18650hg2-rev0-2014.pdf`, `battery/held/saft-lsh20-31015-2-0426.pdf`, `battery/held/saft-mp176065xtd-31109-2-0625.pdf`, `battery/held/samsung-inr18650-30q-v1.0-2015.pdf`, `battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf`, `battery/held/samsung-inr18650-30q6-v1.0-2020.pdf` | test_l4e10 |
| `l4e11/l4e11_power.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 35 committed, 19 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-tme.pdf`, `battery/samsung-35e-orbtronic.pdf`, `battery/ti-bq4050.pdf`, `battery/ti-csd17570q5b.pdf`, `battery/ti-csd18510q5b.pdf`, `battery/ti-sluuaq3a-bq4050-trm.pdf`, `coilcraft/coilcraft-xal60xx-series.pdf`, `connectors/jst-vh-catalogue.pdf`, `d38999/amphenol-d38999-iii-federal.pdf`, `d38999/cables/alpha-25064-spec.pdf`, `d38999/cables/lapp-olflex-robust-210-product-information.pdf`, `diodes/diodes-ap63200-series-buck.pdf`, `diodes/diodes-ap64500.pdf`, `diodes/diodes-bzt52c-ds18004.pdf`, `keystone/M65p42.pdf`, `passives/yageo-cc-series.pdf`, `passives/yageo-rc-l-series-v12.pdf`, `power/aos-ao3401a-p-mosfet.pdf`, `power/bourns-mf-msmf-pptc.pdf`, `power/bourns-srf1260-common-mode-choke.pdf`, `power/bq25792.pdf`, `power/bq25798.pdf`, `power/jscj-2n7002-c8545.pdf`, `power/lcsc-panasonic-eehzk1v101xp.pdf`, `power/littelfuse-smcj-series-tvs.pdf`, `power/ltc2954.pdf`, `power/st-semtech-1n4148w-c81598.pdf`, `power/ti-csd19532q5b-n-fet.pdf`, `power/tps2596.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-lm5069.pdf`, `ti/ti-lm74700-q1.pdf`, `ti/ti-tps37-snvsbj1e.pdf`, `ti/ti-tps62933.pdf`; held back: `nexperia/held/nexperia-an11158-rev7.pdf`, `nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf`, `nexperia/held/nexperia-pxp9r1-30ql.pdf`, `passives/held/moolee-hollr2512-ho-a0-2022-01-06.pdf`, `passives/held/murata-grm3195c1h104ga05-01a-2026-06-11.pdf`, `passives/held/murata-grm3195c1h683ja05-01a-2026-06-11.pdf`, `power/held/adi-ltc3115-1-rev-e.pdf`, `power/held/aos-aons21357-rev2.1-2023-11.pdf`, `power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf`, `power/held/littelfuse-997-mini58v-rev2025-11-18.pdf`, `power/held/vishay-sqj403ep-67109-reva.pdf`, `power/held/vishay-sqj407ep-62806-revb.pdf`, `ti/held/ti-bq25730-sluse65a.pdf`, `ti/held/ti-csd19536ktt-slps540c.pdf`, `ti/held/ti-spra953c-thermal-metrics.pdf`, `ti/held/ti-tps1663-slvset9g.pdf`, `ti/held/ti-tps4811-q1-slusee5e.pdf`, `ti/held/ti-tps55340-slvsbd4e.pdf`, `ti/held/ti-tps63070-slvsc58b.pdf` | test_l4e11, test_l4e_svg_readers, test_w24l4e9, test_w3annex |
| `l4e12/l4e12_thermal.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 31 committed, 3 held back (declared in its PDFTEXT table): `bosch/bosch-bme688.pdf`, `bulgin/bulgin-4000-series-sealed-usb-c.pdf`, `bulgin/bulgin-pxp4043c-usb-c-rear-panel.pdf`, `cm5/cm5-datasheet.pdf`, `diodes/diodes-ap2112-ldo.pdf`, `diodes/diodes-ap63200-series-buck.pdf`, `diodes/diodes-ap64500.pdf`, `fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf`, `nicerf/nicerf-sa868-datasheet-v1.3.pdf`, `omron/omron-g6k-signal-relay.pdf`, `pdi/pdi-e2370ks0c1-flyer.pdf`, `pulse/pulse-h5007nl.pdf`, `quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`, `seals/floydbell-mc-09-530-q-spec.pdf`, `seals/nkk-ip-rated-switches-accessories.pdf`, `sensirion/sgp41-datasheet.pdf`, `storage/cervoz-m2-2242-nvme-titan.pdf`, `switches/ck-atp16-series-datasheet.pdf`, `switches/ck-atp19-series-datasheet.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-pcm2912a.pdf`, `ti/ti-sn74lv1t08.pdf`, `ti/ti-sn74lvc2g07.pdf`, `ti/ti-tlv758p.pdf`, `ti/ti-tmp117-temperature.pdf`, `ti/ti-tps62933.pdf`, `ti/ti-tusb2046b.pdf`, `ti/ti-tusb8041.pdf`, `wifi/asiarf-AW7915-AED_V1.pdf`, `xenarc/xenarc-709gnk-product-manual-v2.pdf`; held back: `ti/held/ti-csd17577q5a-slps516.pdf`, `ti/held/ti-csd17578q5a-slps526.pdf`, `ti/held/ti-tlv755p-c404027.pdf` | test_l4e12 |
| `l4e13/l4e13_panel.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4); l4e_replay.main(), run in-process, still extracts its own pages (KEY group) | 2 committed, 3 held back (declared in its PDFTEXT table): `connectors/jst-vh-catalogue.pdf`, `power/littelfuse-smcj-series-tvs.pdf`; held back: `solar/held/solbian-sx-series-datasheet-eng-2023-02.pdf`, `solar/held/sunpower-flex-safety-installation-524958-revf.pdf`, `solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf` | test_l4e13 |
| `l4e4/l4e4_limits.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through r11dep/r11_dep.py (not converted) | 3 committed, 0 held back (named in the file): `battery/ti-csd18510q5b.pdf`, `bulgin/bulgin-4000-series-sealed-usb-c.pdf`, `ti/ti-tps25740.pdf` | test_l4e4, test_l4e5, test_l4e6 |
| `l4e5/l4e5_source_control.py` | RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | in the l4e7 KEY's files part; source pinned by sha in l4e7_stage_settings.py | 4 committed, 0 held back (named in the file): `power/lt8705a.pdf`, `ti/bq25731-datasheet.pdf`, `ti/ti-lm5069.pdf`, `ti/ti-lm74700-q1.pdf` | test_l4e5 |
| `l4e6/l4e6_fault_handling.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through the l4e4 and r11dep records (not converted) | 3 committed, 0 held back (named in the file): `power/coilcraft-xal1010.pdf`, `power/coilcraft-xal1510.pdf`, `ti/lm5176-datasheet.pdf` | test_l4e6 |
| `l4e7/l4e7_p0sol.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | a sentence on the re-key host | 2 committed, 4 held back (named in the file): `power/coilcraft-xal1510.pdf`, `power/lt8705a.pdf`; held back: `passives/held/vishay-wsl-30100-2023-11-23.pdf`, `ti/held/ti-ina169-sbos181f.pdf`, `ti/held/ti-tps3701-sbvs240c.pdf`, `ti/held/ti-tps4811-q1-slusee5e.pdf` | test_l4e7 |
| `l4e7/l4e7_stage_settings.py` | RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | the l4e7 KEY's own source (its src part; its pdftotext part records the host's version) | 10 committed, 9 held back (named in the file): `diodes/diodes-bzt52c-ds18004.pdf`, `infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf`, `passives/milliohm-hojlr2512-series.pdf`, `power/coilcraft-xal1510.pdf`, `power/littelfuse-smcj-series-tvs.pdf`, `power/lt8705a.pdf`, `power/ti-csd19532q5b-n-fet.pdf`, `ti/ti-lm5069.pdf`, `ti/ti-lm74700-q1.pdf`, `ti/ti-tps3808.pdf`; held back: `passives/held/vishay-wsl-30100-2023-11-23.pdf`, `passives/held/yageo-rt-series-v16-2025-05-06.pdf`, `power/held/infineon-bsc028n06ns-rev2.1-c148250.pdf`, `power/held/mil-std-461g-2015-12-11.pdf`, `power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf`, `ti/held/ti-ina169-sbos181f.pdf`, `ti/held/ti-ina250-sbos511c.pdf`, `ti/held/ti-tps3701-sbvs240c.pdf`, `ti/held/ti-tps4811-q1-slusee5e.pdf` | test_l4e7 |
| `l4e8/ripple_dense.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4); L4-E4's compute(), run in-process, still reaches r11dep/r11_dep.py (KEY group) | 4 committed, 1 held back (declared in its PDFTEXT table): `passives/milliohm-hojlr2512-series.pdf`, `power/lcsc-panasonic-eehzk1v101xp.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf`; held back: `passives/held/uniroyal-series-11cd644d.pdf` | test_l4e8 |
| `l4e9/l4e9_power_path.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 16 committed, 1 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-tme.pdf`, `connectors/jst-vh-catalogue.pdf`, `connectors/millmax-rugged-power-spring-pins-page28.pdf`, `d38999/amphenol-d38999-iii-federal.pdf`, `infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf`, `keystone/M65p42.pdf`, `keystone/littelfuse-297-ficcorp.pdf`, `passives/yageo-cc-series.pdf`, `power/littelfuse-smcj-series-tvs.pdf`, `power/ti-csd19532q5b-n-fet.pdf`, `power/tps2596.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-ina226.pdf`, `ti/ti-lm5069.pdf`, `ti/ti-lm74700-q1.pdf`; held back: `power/held/littelfuse-997-mini58v-rev2025-11-18.pdf` | test_applier_state, test_l4e7, test_l4e9, test_l4e_svg_readers, test_recpack, test_w11l9t5, test_w13l4e9, test_w20oneliners, test_w24l4e9, test_w7rem |
| `l5r2/l5r2_interfaces.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 7 committed, 0 held back (declared in its PDFTEXT table): `connectors/jst-vh-catalogue.pdf`, `connectors/wurth-wr-bhd-box-header-61202621621.pdf`, `connectors/wurth-wr-bhd-idc-socket-61202623021.pdf`, `connectors/wurth-wr-cab-ribbon-63912615521cab.pdf`, `mitsubishi/ra30h1317m1-datasheet.pdf`, `power/bourns-mf-msmf-pptc.pdf`, `power/ltc2954.pdf` | test_l5r2, test_w14l5 |
| `l6pwr/l6pwr_parts.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through v2/ecad/tools/part_identities.py (outside the records) | 7 committed, 10 held back (named in the file): `battery/samsung-35e-orbtronic.pdf`, `passives/milliohm-hojlr2512-series.pdf`, `power/lcsc-panasonic-eehzk1v101xp.pdf`, `power/littelfuse-smcj-series-tvs.pdf`, `power/ti-csd19532q5b-n-fet.pdf`, `ti/ti-tps3808.pdf`, `vishay/vishay-wsl-power-metal-strip.pdf`; held back: `battery/held/saft-mp176065xtd-31109-2-0625.pdf`, `nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf`, `passives/held/vishay-wsl-30100-2023-11-23.pdf`, `power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf`, `ti/held/ti-bq25730-sluse65a.pdf`, `ti/held/ti-csd19536ktt-slps540c.pdf`, `ti/held/ti-ina169-sbos181f.pdf`, `ti/held/ti-tps1663-slvset9g.pdf`, `ti/held/ti-tps3701-sbvs240c.pdf`, `ti/held/ti-tps4811-q1-slusee5e.pdf` | test_l6pwr |
| `l6r2/l6r2_passives.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through v2/ecad/tools/part_identities.py (outside the records) | 4 committed, 1 held back (named in the file): `coilcraft/coilcraft-xal40xx-series.pdf`, `coilcraft/coilcraft-xal60xx-series.pdf`, `passives/milliohm-hojlr2512-series.pdf`, `passives/yageo-cc-series.pdf`; held back: `passives/held/uniroyal-series-11cd644d.pdf` | test_l6r2, test_lcsc_fill_requirements |
| `l7pwr/l7pwr_fans_th1.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 5 committed, 0 held back (declared in its PDFTEXT table): `cm5/rpi-cm5-cooler-product-brief-2024-12.pdf`, `fans/samesky-cfm-60bg68-dc-axial-fan-2024-09-12.pdf`, `fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf`, `fans/sunon-ip56-ip68-gr487-fan-series-239-E-2023-04-07.pdf`, `precidip/precidip-catalog-slc-2018-03-20.pdf` | test_l7pwr, test_l8r2 |
| `l7r2/l7r2_items.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 3 committed, 0 held back (declared in its PDFTEXT table): `bulgin/bulgin-px0833-sealed-rj45-coupler.pdf`, `d38999/amphenol-d38999-iii-federal.pdf`, `d38999/glenair-series-iii-iv-panel-cutouts.pdf` | test_l7r2 |
| `l8p/l8p_drafts.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 11 committed, 1 held back (declared in its PDFTEXT table): `battery/murata-nxrt15xh103fa1b.pdf`, `battery/murata-prf-series.pdf`, `battery/ti-bq4050.pdf`, `battery/ti-csd17570q5b.pdf`, `battery/ti-csd18510q5b.pdf`, `battery/ti-sluuaq3a-bq4050-trm.pdf`, `diodes/diodes-bzt52c-ds18004.pdf`, `power/jscj-2n7002-c8545.pdf`, `power/st-semtech-1n4148w-c81598.pdf`, `ti/ti-lm5069.pdf`, `ti/ti-lm74700-q1.pdf`; held back: `ti/held/ti-opa187-sbos807e.pdf` | test_l8p |
| `l8p/l8p_c4.py` | RUN-TIME EXTRACTION THROUGH ANOTHER SCRIPT'S READER, CONVERTED (W55) | named no pdftotext at the base, so the census by name missed it: it ran pdftotext through `l8p_guard.pdftext()` (and refused on this branch, W53); it declares and reads its three sheets with its own table since W55 (section 8) | 2 committed, 1 held back (declared in its PDFTEXT table): `diodes/diodes-bzt52c-ds18004.pdf`, `power/jscj-2n7002-c8545.pdf`; held back: `ti/held/ti-lm26lv-snis144g.pdf` | test_l8p |
| `l8p/l8p_guard.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 5 committed, 2 held back (declared in its PDFTEXT table): `battery/ti-csd17570q5b.pdf`, `battery/ti-csd18510q5b.pdf`, `power/aos-ao3400a-n-mosfet.pdf`, `power/jscj-2n7002-c8545.pdf`, `ti/ti-lm5069.pdf`; held back: `ti/held/ti-lm26lv-snis144g.pdf`, `ti/held/ti-tps709-sbvs186h.pdf` | test_l8p |
| `l8r2/l8r2_dist.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through l8r2_gndret.py and l8r2_p0.py (converted) | 0 committed, 0 held back (named in the file) | test_l8r2 |
| `l8r2/l8r2_drafts.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 2 committed, 0 held back (declared in its PDFTEXT table): `cm5/cm5-datasheet.pdf`, `fans/sunon-dc-fan-catalogue-240A-pp18-40-extract.pdf` | test_l8r2 |
| `l8r2/l8r2_gndret.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 6 committed, 0 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`, `battery/amass-xt60-spec-tme.pdf`, `connectors/jst-vh-catalogue.pdf`, `connectors/wurth-wr-bhd-box-header-61202621621.pdf`, `connectors/wurth-wr-bhd-idc-socket-61202623021.pdf`, `connectors/wurth-wr-cab-ribbon-63912615521cab.pdf` | test_l8r2 |
| `l8r2/l8r2_p0.py` | RUN-TIME EXTRACTION, CONVERTED | one of the brief's six records; reads the committed text (section 4) | 4 committed, 0 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`, `battery/amass-xt60-spec-tme.pdf`, `connectors/jst-ph-catalogue.pdf`, `hirose/hirose-ufl-series-catalogue-2009-02-digikey-copy.pdf` | test_l8r2 |
| `l9pwr/l9pwr_budget.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 7 committed, 0 held back (declared in its PDFTEXT table): `diodes/diodes-ap2112-ldo.pdf`, `diodes/diodes-ap63200-series-buck.pdf`, `diodes/diodes-ap64500.pdf`, `power/ti-tlv755p-ldo.pdf`, `power/tps2596.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-tps62933.pdf` | test_l9pwr, test_l9t5 |
| `l9stk/l9stk_copper.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 3 committed, 0 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-tme.pdf`, `connectors/jst-vh-catalogue.pdf`, `keystone/littelfuse-297-ficcorp.pdf` | test_l9stk |
| `l9stk/l9stk_protection.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 12 committed, 1 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-tme.pdf`, `battery/murata-nxrt15xh103fa1b.pdf`, `battery/murata-prf-series.pdf`, `battery/ti-csd17570q5b.pdf`, `battery/ti-csd18510q5b.pdf`, `connectors/jst-vh-catalogue.pdf`, `keystone/littelfuse-297-ficcorp.pdf`, `power/jscj-2n7002-c8545.pdf`, `power/littelfuse-smcj-series-tvs.pdf`, `power/mdd-smbj-series-tvs.pdf`, `power/st-semtech-1n4148w-c81598.pdf`, `ti/ti-lm5069.pdf`; held back: `ti/held/ti-slva673a.pdf` | test_l9stk |
| `l9t5/l9t5_a1.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 1 committed, 4 held back (declared in its PDFTEXT table): `mitsubishi/ra30h1317m1-datasheet.pdf`; held back: `adi/held/adi-adl5513-revb.pdf`, `adi/held/adi-adl5902-revb.pdf`, `adi/held/adi-ltc5582-revd.pdf`, `ti/held/ti-lmh2110-snws022d.pdf` | test_l9t5 |
| `l9t5/l9t5_case.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 11 committed, 1 held back (declared in its PDFTEXT table): `battery/samsung-35e-orbtronic.pdf`, `battery/ti-bq4050.pdf`, `battery/ti-csd18510q5b.pdf`, `connectors/jst-vh-catalogue.pdf`, `mitsubishi/ra30h1317m1-datasheet.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-ina226.pdf`, `ti/ti-tlv758p.pdf`, `ti/ti-tlv9062-op-amp.pdf`, `ti/ti-tps62933.pdf`, `vishay/vishay-wsl-power-metal-strip.pdf`; held back: `ti/held/ti-ina250-sbos511c.pdf` | test_l9t5 |
| `l9t5/l9t5_cm5.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 1 committed, 0 held back (declared in its PDFTEXT table): `cm5/cm5-datasheet.pdf` | test_l9t5 |
| `l9t5/l9t5_connected.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through the l9t5 modules it imports | 0 committed, 0 held back (named in the file) | test_applier_state, test_l9t5, test_recpack, test_w11l9t5, test_w24l4e9, test_w9l9t5 |
| `l9t5/l9t5_drafts.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 6 committed, 0 held back (declared in its PDFTEXT table): `coilcraft/coilcraft-xal60xx-series.pdf`, `connectors/jst-vh-catalogue.pdf`, `diodes/diodes-ap2112-ldo.pdf`, `st/st-stm32h743xi-datasheet.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-tps62933.pdf` | test_l9t5 |
| `l9t5/l9t5_f01.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 12 committed, 1 held back (declared in its PDFTEXT table): `battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`, `battery/ti-bq4050.pdf`, `battery/ti-csd18510q5b.pdf`, `connectors/millmax-rugged-power-spring-pins-page28.pdf`, `mitsubishi/ra30h1317m1-datasheet.pdf`, `passives/milliohm-hojlr2512-series.pdf`, `precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-ina226.pdf`, `ti/ti-tlv758p.pdf`, `ti/ti-tlv9062-op-amp.pdf`, `vishay/vishay-wsl-power-metal-strip.pdf`; held back: `ti/held/ti-ina250-sbos511c.pdf` | test_l9t5, test_recpack |
| `l9t5/l9t5_f01_drafts.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | reads through the l9t5 modules it imports | 0 committed, 0 held back (named in the file) | test_l9t5 |
| `l9t5/l9t5_paloop.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 6 committed, 1 held back (declared in its PDFTEXT table): `battery/ti-csd18510q5b.pdf`, `ti/lm5176-datasheet.pdf`, `ti/ti-ina226.pdf`, `ti/ti-tlv758p.pdf`, `ti/ti-tlv9062-op-amp.pdf`, `vishay/vishay-wsl-power-metal-strip.pdf`; held back: `ti/held/ti-ina250-sbos511c.pdf` | test_l9t5, test_w15class |
| `l9t5/l9t5_t10.py` | RUN-TIME EXTRACTION, CONVERTED | a remaining run-time caller; reads the committed text (section 4) | 6 committed, 2 held back (declared in its PDFTEXT table): `diodes/diodes-ap2112-ldo.pdf`, `diodes/diodes-ap63200-series-buck.pdf`, `st/st-rm0433-rev8.pdf`, `st/st-stm32h743xi-datasheet.pdf`, `ti/ti-tcan334-can-fd-transceiver.pdf`, `ti/ti-tps62933.pdf`; held back: `ti/held/ti-ina169-sbos181f.pdf`, `ti/held/ti-tps3701-sbvs240c.pdf` | test_l9t5 |
| `r11dep/r11_dep.py` | RUN-TIME EXTRACTION, NOT CONVERTED (l4e7 KEY group) | source pinned by sha in l4e4, l4e5, l4e6 and l4e8 (l4e4 and l4e5 are in the l4e7 KEY's files part) | 8 committed, 0 held back (named in the file): `connectors/millmax-rugged-power-spring-pins-page28.pdf`, `passives/milliohm-hojlr2512-series.pdf`, `power/coilcraft-xal1010.pdf`, `power/lcsc-panasonic-eehzk1v101xp.pdf`, `power/lt8705a.pdf`, `power/ti-csd19532q5b-n-fet.pdf`, `ti/bq25731-datasheet.pdf`, `ti/lm5176-datasheet.pdf` | test_l4e4, test_l4e6, test_r11dep |
| `r4b/pin_parity.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | a usage line | 0 committed, 0 held back (named in the file) | none |
| `rv-dec/dec_mmscan.py` | RUN-TIME EXTRACTION, NOT CONVERTED (historical) | a scan of the vendor tree whose source is pinned by the released H1 to H3 manifests | 0 committed, 0 held back (named in the file) | none |
| `s122/apply_docs_s122_r4.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | prose | 4 committed, 0 held back (named in the file): `m2/amphenol-mdt420b01001-m2-b-key.pdf`, `m2/te-2199119-m2-b-key.pdf`, `mitsubishi/ra30h1317m1-datasheet.pdf`, `ti/ti-lm5069.pdf` | none |
| `s122/judgements.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | prose naming a reading | 7 committed, 0 held back (named in the file): `battery/samsung-35e-orbtronic.pdf`, `battery/ti-bq4050.pdf`, `m2/amphenol-mdt420b01001-m2-b-key.pdf`, `m2/te-2199119-m2-b-key.pdf`, `mitsubishi/ra30h1317m1-datasheet.pdf`, `nicerf/nicerf-sa868-datasheet-v1.3.pdf`, `ti/ti-lm5069.pdf` | none |
| `s122/verdicts.py` | RUN-TIME EXTRACTION, NOT CONVERTED (historical) | stream s122's verdict writer of 29 September 2026 (no test module reads it) | 0 committed, 0 held back (named in the file) | none |
| `w4dp/patch_vendor_index.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | prose | 1 committed, 0 held back (named in the file): `power/st-semtech-1n4148w-c81598.pdf` | none |
| `w5identc/build_table.py` | DRY-RUN OR TRANSCRIPT, no call of its own (untouched) | prose naming a reading | 16 committed, 1 held back (named in the file): `diodes/diodes-bat46w.pdf`, `hirose/hirose-fh34-series-ffc-connectors.pdf`, `passives/arlitech-atnr-series-spec.pdf`, `passives/fenghua-series-705023d3.pdf`, `passives/uniroyal-cs03w5f470lt5e.pdf`, `passives/yageo-cc-series.pdf`, `power/aos-ao3401a-p-mosfet.pdf`, `power/jscj-2n7002-c8545.pdf`, `power/ti-tlv755p-ldo.pdf`, `seals/floydbell-mc-09-530-q-spec.pdf`, `switches/apem-switch-guards-series.pdf`, `switches/ck-atp16-series-datasheet.pdf`, `switches/ck-atp19-series-datasheet.pdf`, `switches/nkk-m-series-toggles-datasheet.pdf`, `vishay/veml7700-datasheet.pdf`, `winbond/winbond-w25q16jv-serial-flash.pdf`; held back: `passives/held/uniroyal-series-11cd644d.pdf` | test_part_identities |
| `w5identc/scan_vendor.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | a one-off scan of every vendor PDF | 0 committed, 0 held back (named in the file) | none |
| `w5si/apply/apply_board_c_declarations.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | a one-off apply script | 3 committed, 0 held back (named in the file): `diodes/diodes-74lvc1g17.pdf`, `rp2040/rpi-rp2040-datasheet.pdf`, `ti/ti-sn74lvc1g57.pdf` | none |
| `w5si/tools/cite_fill.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | a citation filler run by hand | 0 committed, 0 held back (named in the file) | none |
| `w5si/tools/edge_search.py` | FETCH, SCAN, APPLY OR RE-TAKE SCRIPT (untouched) | a search tool run by hand | 0 committed, 0 held back (named in the file) | test_edge_length |

Outside the records (named for the coordinator, not in this brief's scope): `v2/ecad/tools/part_identities.py` (read by l6pwr and l6r2),
`pack_protection.py`, `edge_length.py` and `handover_exports.py` run pdftotext; so do four test modules directly (`test_energy_chain`,
`test_l3r5`, `test_l5r4`, `test_l8r2`'s fan sheets) and twenty guard a skip on `shutil.which("pdftotext")`.

## 3. Where the text lives (a SESSION decision, recorded under the owner's standing rule of 26 September 2026)

The brief named `<record>/inputs/pdftext/<pdf stem>.txt`. Taken instead: beside the PDF, `<pdf folder>/pdftext/<pdf stem>.<tag>.txt`
with the sidecar `<that file>.meta.json`; a held-back PDF's text under its `held/pdftext/`, which the existing `held/` lines of
.gitignore exclude. Reason, read in the test modules, not guessed: the record tests scan their record's tree as the record's own prose.
`test_l4e11.t_no_dashes_and_no_claim_words` opens every entry of `inputs/` as a file (a `pdftext/` folder there raises), and
`test_l4e13`, `test_l4e12`, `test_l7r2`, `test_l5r4`, `test_l6pwr`, `test_l6r2` and `test_w5l8p` walk the record for `.txt` (or every
file) and refuse an en or em dash or a claim word ("guaranteed", "rated for"); a maker's verbatim text carries both (TI prints its minus
signs as U+2013). Writing the dashes out would change the bytes the generators parse, and restating ten tests to exempt maker text is
not this branch's to do. The vendor tree already holds text extractions of maker documents (`v2/vendor/m2/*.ocr.txt`), and the handover
pack's rule for them (`v2/docs/handover/pack.yaml`: L6 "text extractions of maker documents", `v2/vendor/**/*.txt` and `**/*.json`)
classifies the new files with no edit. One text serves every record that reads the same PDF with the same options, so two records cannot
pin two different extractions of one document. The tag names the options: `layout`, `raw` (`-raw`) or `plain` (neither), then `.pN` for
one page or `.fN` / `.lN` for a range. Reversal: move the files under each record's `inputs/pdftext/` (one line, `pdftext.text_path`)
after those tests exempt verbatim maker text.

The held-back sheets: every `fetch_held_back.py` header states that its sheets carry the maker's copyright or notice and no grant to
redistribute (a1solar, int16, l3batt, l4e7, l4e9, l4e10, l4e11, l4e12, l4e13, l6pwr, l7r2, l8p, l8r2, l9stk, l9t5, s117, w5identc). The
full text of a sheet is a copy of it, so no held-back sheet's text is committed: it is written beside the PDF under `held/`, ignored, and
the helper refuses when it is absent exactly as the generators refuse an absent PDF, naming the fetch and the re-take.

The fetch a refusal names (W37, 6 October 2026, W36's finding F-P2). The refusal named "the record's fetch_held_back.py" for every
held sheet, which for 12 reads is the wrong script: efuse and l4e8 have no fetch script of their own, and l4e12, l4e13, l9t5 and l9t5_t10
read sheets another record fetches. `pdftext.FETCH` now maps each of the 43 held-back sheets the PDFTEXT tables declare to the records
whose `fetch_held_back.py` lists it (read from each script's own document list, parsed, never run); the refusal names the reading
record's own script when it is listed, else the first. Read against W36's evidence: every one of the 43 has a fetch route, so no sheet
is without one; the two records W36 named as having none are records without a fetch script of their own, not sheets without a route:
efuse's TPS1663 and TPS4811 are fetched by l4e11's (and l6pwr's) script, l4e8's Uniroyal sheet by w5identc's. The other ten: l4e12's
CSD17577 and CSD17578 by s117's, l4e13's two SunPower sheets by a1solar's, l9t5's INA250 (case, f01, paloop) by l4e7's, l9t5_t10's
INA169 and TPS3701 by l4e7's (and l6pwr's). A sheet no script fetched would be refused with "no record's fetch_held_back.py fetches the
held-back sheet" (a finding, never a silent gap); `test_pdftext_input` re-derives the map from the fetch scripts and refuses a difference.

## 4. The converted generators (each record's `PDFTEXT` table is in its script; the texts are beside their PDFs)

| Generator (under `v2/docs/records/`) | pdftotext call sites replaced | Extractions declared | The check on the runner |
|---|---|---|---|
| `efuse/efuse_check.py` | 1 | 17 PDFs, 17 extractions (15 committed, 2 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l5r2/l5r2_interfaces.py` | 1 | 7 PDFs, 7 extractions (7 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l8r2/l8r2_drafts.py` | 1 | 2 PDFs, 2 extractions (2 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l8r2/l8r2_gndret.py` | 1 | 6 PDFs, 6 extractions (6 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l8r2/l8r2_p0.py` | 4 | 4 PDFs, 4 extractions (4 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l4e13/l4e13_panel.py` | 1 | 5 PDFs, 14 extractions (8 committed, 6 held back) | logged run (the replay still extracts): its own five sheets read 0 times; output = committed + 14 text lines |
| `l4e11/l4e11_power.py` | 2 | 54 PDFs, 68 extractions (44 committed, 24 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l4e9/l4e9_power_path.py` | 7 | 17 PDFs, 34 extractions (32 committed, 2 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l4e10/l4e10_cell_thermal.py` | 1 | 15 PDFs, 15 extractions (9 committed, 6 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l4e12/l4e12_thermal.py` | 1 | 34 PDFs, 34 extractions (31 committed, 3 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l7pwr/l7pwr_fans_th1.py` | 1 | 5 PDFs, 5 extractions (5 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l7r2/l7r2_items.py` | 1 | 3 PDFs, 3 extractions (3 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l8p/l8p_drafts.py` | 1 | 12 PDFs, 12 extractions (11 committed, 1 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l8p/l8p_c4.py` (W55) | 3 (its calls of `l8p_guard.pdftext()`) | 3 PDFs, 3 extractions (2 committed, 1 held back; each already declared by l8p_drafts or l8p_guard, so no new text) | pdftotext and pdftocairo refused: 0 calls, exit 0, output = committed + 3 text lines and 2 moved source pins (section 8) |
| `l8p/l8p_guard.py` | 1 | 7 PDFs, 7 extractions (5 committed, 2 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9pwr/l9pwr_budget.py` | 1 | 7 PDFs, 7 extractions (7 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9stk/l9stk_copper.py` | 1 | 3 PDFs, 3 extractions (3 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9stk/l9stk_protection.py` | 1 | 13 PDFs, 13 extractions (12 committed, 1 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9t5/l9t5_a1.py` | 1 | 5 PDFs, 5 extractions (1 committed, 4 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9t5/l9t5_case.py` | 1 | 12 PDFs, 12 extractions (11 committed, 1 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9t5/l9t5_cm5.py` | 1 | 1 PDFs, 1 extractions (1 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9t5/l9t5_drafts.py` | 1 | 6 PDFs, 6 extractions (6 committed, 0 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9t5/l9t5_f01.py` | 1 | 13 PDFs, 13 extractions (12 committed, 1 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l9t5/l9t5_paloop.py` | 1 | 7 PDFs, 7 extractions (6 committed, 1 held back) | no output of its own; its importers (case, f01, connected, f01_drafts) ran with pdftotext denied |
| `l9t5/l9t5_t10.py` | 2 | 8 PDFs, 13 extractions (11 committed, 2 held back) | pdftotext denied: 0 calls, exit 0, output = committed + the text lines (and moved source pins) |
| `l4e8/ripple_dense.py` | 1 | 5 PDFs, 19 extractions (18 committed, 1 held back) | logged run (r11dep still extracts): its own page reads gone (the held Uniroyal sheet read 0 times); output = committed + 19 text lines |

Totals: 223 distinct extractions, 171 committed (14,410,612 bytes of text, with a sidecar each) and 52 held back under `held/pdftext/`
(ignored, written on the runner, not in git). Each call site is replaced by `pdf_text(top, pdf, options, PDFTEXT, record)`, keeping the
generator's own pin and presence checks of the PDF, its decoding (`utf-8`, errors replaced; `universal_newlines=True` where the old
call used `text=True` or `os.popen`) and its page splitting; nothing it computes from the text changed. The check, per generator: a run
with a refusing `pdftotext` first on PATH (it logged its arguments and exited 1) gave exit 0, zero calls, and a stdout equal to the
committed `.out` but for the added text lines and the source-pin lines of the scripts W34 edited (and l4e12's count of its pins, 69 to
103: the count line moves because `base()` widens the pins dict with the 34 text pins, `R = {"pins": dict(PINS, **{...PDFT.inputs...})}`,
and line 0e prints its length; no figure moves; W34's disclosure stands, W36's finding F-C1, stated by W37). The indirect readers ran the same way with no call: l5r2's `l5r3_panel.py`, l8r2's `l8r2_dist.py`, l9t5's `l9t5_connected.py`
and `l9t5_f01_drafts.py`. Two keep a reader W34 did not convert, so their check was the logged run: `l4e13_panel.py` (its own 14 page
reads gone; `l4e_replay.main()`, run in-process, still makes 39 extractions of lm5176, lt8705a, bq25731, yageo, uniroyal and the two
SunPower sheets) and `ripple_dense.py` (its 19 page reads gone; L4-E4's `compute()` still reaches `r11_dep.py`).

## 5. Not converted, and why (each a SESSION decision under the owner's standing rule of 26 September 2026; reversible as stated)

- **The l4e7 KEY group** (`l4e7_stage_settings.py`, `l4e_replay.py`, `l4e5_source_control.py`, `r11_dep.py`, `l3plane/energy_basis.py`,
  `l3plane/vbus20_range.py`). L4-E7's results KEY records the host's `pdftotext -v` as one of its parts and `candidate_guard.py`
  treats it as a host part, so converting l4e7's extractions would not move `test_l4e7` off the runner; and every one of these sources
  is in the KEY's files part or pinned by sha in another record's source (l4e13, l4e5, l4e6, l4e8, l4e7), so converting them moves
  source pins through five records and the KEY for no change in host independence. Reversal: convert them, with the KEY's
  pdftotext part retired, in the set that re-keys l4e7 for another reason; the helper and the re-take serve them unchanged.
- **The accepted Layer 3 records** (`l3batt/tablet.py`, `l3feas/hf_wab.py`, `l3feas/solar_interface.py`, `l3plane/curve_readings.py`,
  `l3plane/weather_basis.py`): Layer 3 is accepted and not reopened; their sources are pinned by filed checks (`CHECK-*.md`).
- **The coordinator's checker** (`l4close/verify_risks.py`): it reads an exported tree named as its argument, where a held-back
  sheet's text is absent by construction; how it reads is the coordinator's to set.
- **Historical** (`a1elec/gauge_scale.py`, `rv-dec/dec_mmscan.py`, `s122/verdicts.py`): no test module reads them; `dec_mmscan.py`'s
  source is pinned by the released H1 to H3 manifests.
- **Outside the records** (not in this brief): `v2/ecad/tools/part_identities.py`, `pack_protection.py`, `edge_length.py`,
  `handover_exports.py`; the tests that run pdftotext themselves (`test_energy_chain`, `test_l3r5`, `test_l5r4`, `test_l8r2`'s fan sheets).

**What still reads the host's poppler (restated by W37, 6 October 2026, on W36's finding F-P1; the sentence it replaces said the
converted generators "no longer read the host's tool at all", which is false).** The converted generators no longer run `pdftotext`
on any path of their own. They still reach the host's poppler in two ways:

- **`pdftocairo -svg`, run by two converted generators** to read a maker's plotted curve as drawn: `l4e9/l4e9_power_path.py`, one
  call site (the CSD19532Q5B safe-operating-area page 6; W36 logged 1 call per run, W37 the same), and `l4e11/l4e11_power.py`, three
  call sites (the CSD19532Q5B and the held CSD19536KTT at page 6, the held AONS21357 at page 5; 5 calls per run). The SVG is not a
  committed input; pdftocairo's own host sensitivity has not been measured (W36, "Not checked"). `test_pdftext_input` pins these four
  call sites and these calls (section 7).
- **`pdftotext` through a module a converted generator runs**: `l4e13/l4e13_panel.py` runs `l4e/l4e_replay.main()` in-process (39
  extractions per run, W36's logged count), and `l4e8/ripple_dense.py` reaches `r11dep/r11_dep.py` through L4-E4's `compute()`; both
  modules are the l4e7 KEY group's (section 5, first item), listed in the regression as KNOWN callers with that reason.

A suite box therefore still needs poppler's `pdftotext` 22.12.0 and the `poppler-data` package for: the l4e7 KEY group (its KEY
records the host's `pdftotext -v`; `test_l4e7`, and a recompute reads the CID sheets); `r11dep/r11_dep.py`, which reads
`passives/milliohm-hojlr2512-series.pdf` (CID Type 0, no ToUnicode, the JST VH signature, W36's font census) in `test_r11dep`,
`test_l4e4`, `test_l4e5` and `test_l4e6`, and in `test_l4e8` through `ripple_dense`; `l4close/verify_risks.py` (`test_l4close`, both
CID sheets); `l4e13` through `l4e_replay` (`test_l4e13`); the accepted Layer 3 and historical readers above; and the four tools and
four tests outside the records. It needs `pdftocairo` for `l4e9` and `l4e11` and the tests that run them. W36's census is static (no
box was rented for it); the converted generators' own reads are the only ones W34 made host-independent.

## 6. What the coordinator does at set 32's integration (restated by W37, 6 October 2026, on W36's findings F-K1 to F-K3)

The order W34 wrote here ran backwards (W36's F-K1: the L4 outputs are pinned by l9pwr, l9stk, l7pwr, l8r2, l9t5_t10 and efuse, so the
L4 chain is upstream of all of them). The runner-local draft `_runs/int32/PLAN.draft.md` carries the same steps with the staging
commands and the moved line citations (F-K4).

1. Merge `fnd/w34pdftext` (no `.out` in it). Install the 52 held-back texts with the held sheets on every host that runs a converted
   record: they are ignored files under `v2/vendor/*/held/pdftext/`, so `freeze_l4_chain.sh`'s staging of every sibling worktree's
   `*/held/*` carries them while the pdftext worktree exists, and a box's held tar must be cut from a worktree that holds them (the
   re-key's `rekey_box_fresh.sh` tars p0pwr's, which has none); or re-take them on the host: `python3
   v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/<record>` for efuse, l4e8, l4e10, l4e11, l4e12, l4e13, l4e9, l8p, l9stk and
   l9t5 (each prints UNCHANGED for a committed text; a held sheet that is absent is refused with the script that fetches it).
2. Regenerate through `_bin/regen_out.py`, upstream first: `ripple_dense` (l4e8); then re-pin `L4E8_OUT` in `l4e12_thermal.py`'s PINS
   (`"c6181037..."`, W36's F-K2: `l4e12_thermal.py` refuses a ripple_dense.out that is not the pinned file, and `freeze_l4_chain.sh`
   re-pins only L4E10_OUT) to the new digest by hand; then the L4 pin chain (`freeze_l4_chain.sh`: l4e10, l4e11, l4e13, then l4e12,
   then l4e9, then its stability pass); then `l7pwr_fans_th1`; `l9stk_copper`, `l9stk_protection`; `l9pwr_budget`; the l9t5 cascade
   twice (`l9t5_case`, `l9t5_cm5`, `l9t5_a1`, `l9t5_f01`, `l9t5_drafts`, `l9t5_t10`, `l9t5_connected`, `l9t5_f01_drafts`, the second
   pass identical); l8r2 (`l8r2_gndret`, then `l8r2_p0`, `l8r2_drafts`, `l8r2_dist`); `l8p_drafts`, `l8p_guard`; `efuse_check`;
   `l5r2_interfaces`; `l7r2_items`; then `regen_targeted` with its base set to set 31's promoted commit (never HEAD) for every output
   that pins one of these. Each `.out` gains only its text lines and moved source pins (section 4); a figure that moves is a defect of
   this branch.
3. **The l4e7 KEY:** `v2/docs/records/l4e11/l4e11_power.out` is in the KEY's files part and gains 68 text lines, so the KEY reads
   MISMATCH after step 2 and is re-keyed on a debian:12 box as in set 31 (its parts move on "files" only). No other file the KEY covers
   is touched by W34 or W37 (l4e7's own scripts, `l4e_replay`, `l4e4`, `l4e5` and the rest are unchanged).
4. **After the re-key (W36's F-K3):** `l4e7_p0sol` (it pins l4e11_power.out); L4-E9's `l4e7p0` pin in `l4e9_power_path.py` (the
   digest of l4e7_p0sol.out) and `l4e9_power_path`; then `l5pwr_contracts` (pins l4e9's out), `l9t5_connected` and `l6r2_passives` (pin
   l4e9's source), `l8p_c4` (pins l8p_guard.py); then one more `regen_targeted` pass to convergence.
5. The record test modules compare their committed `.out` with a fresh run and some pin the edited sources' digests, so they fail on
   this branch until steps 2 to 4 (the adoption boundary; W34 and W37 ran only `test_pdftext_input` and `test_public_hygiene`). Their
   `shutil.which("pdftotext")` skips are now stale for the converted generators (harmless; left for their owners).
6. Size (W36's F-S1, the coordinator's item Q-53): the committed texts add about 14.4 MB raw to the public tree under `pack.yaml`'s L6
   include (`v2/vendor/**/*.txt` and `**/*.json`); W36's estimator read the handover ZIP over its cap already at W34's base (margin
   -17,812,603 bytes at `aed4bd23`, -20,227,393 at `6dc69ad2`), so a `pack.yaml` decision precedes any handover build. The supplier
   package (`_bin/pack_supplier.py`, runner-local) bundles records whose generators load `_lib/pdftext.py` but carries no `_lib` file
   (W36's F-S2); the rule to add is named in the plan draft.

## 7. W37's changes on W36's findings (6 October 2026; the review as received: `_runs/claude/w36rev/REPORT-AS-RECEIVED.md`)

- **F-P1** (provenance): section 5's closing sentence was false; restated there as what still reads the host's poppler (pdftocairo at
  four call sites in l4e9 and l4e11; pdftotext through `l4e_replay` and `r11_dep`) and which tests and boxes still need it.
- **F-P2** (provenance): `pdftext.FETCH` and `fetch_route()`; `read_pdf_text()` and `retake_pdf_text.py` name the script that fetches
  the sheet (section 3). The re-take now checks `.gitignore` BEFORE writing: a held-back sheet's text it would not exclude, or a
  committed sheet's text it would, is refused with nothing written (before W37 the text was written and then refused).
- **F-R1, F-R2** (regression): `test_pdftext_input` runs efuse, l5r2 and l9t5_case with a refusing pdftotext and a refusing pdftocairo
  first on PATH (exit 0, no call, every text's input line printed, the record folder unchanged; the output to a temporary file), and
  l4e9 and l4e11 with pdftotext refusing and pdftocairo logged (no pdftotext call; pdftocairo exactly at the pinned sites, 1 and 5
  calls); predicate (d) reads a pdftotext token in any string the code holds (shell=True, a variable, `/usr/bin/pdftotext`, f-string
  parts), allows pdftocairo only at its four sites, and lists the reached `l4e_replay`, `energy_basis`, `vbus20_range`, `r11_dep` and
  `l4e5_source_control` as KNOWN callers with their reason; with `aed4bd23` present it catches all 25 old sources. Added: the re-take's
  CHANGED path and its refusals on fixtures, an orphan text detected on a fixture and none in this tree, and the fetch map re-derived.
  As a mutation, the generator run against `aed4bd23`'s `efuse_check.py` FAILS (exit 2 with both tools refused); restored, it passes.
- **F-K5** (consequence): `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`, section 7 item 2, gains the re-take step.
- **F-C1** (computation, minor): stated in section 4; nothing changed.
- **F-K1 to F-K3, F-K4, F-S1, F-S2**: the coordinator's (section 6 and the plan draft); W37 changed no output, pin, generator or
  `_bin/` file.
