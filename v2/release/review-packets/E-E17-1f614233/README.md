# Review packet: board E (pcb-e1-dock) at 1f614233

**UNBUILT PROTOTYPE DESIGN. No board of this set has been fabricated, assembled or tested; nothing in this packet is physical evidence. A review packet is a review input: it does NOT release this board to fabrication, layout or ordering, and it approves nothing.**

**READINESS OF THIS PACKET: QUARANTINED, NOT_FOR_FAB.** No file here is an order file; the two BOM files carry NOT_FOR_FAB in their names.
This board is HELD by decision 31 (board E's exposed-port protection), in the hold's own words: ROUTING_STATUS PASS, ELECTRICAL_PROTECTION_STATUS BLOCKED_DECISION_31, FAB_READINESS NOT_READY, PUBLICATION_STATUS HELD. The hold permits: "a review package clearly quarantined as NOT_FOR_FAB may be generated, so the board can be read and reviewed while it is held". It forbids: "any orderable fabrication package, any promotion of the board or its folder, any publication of the board file or its evidence".

| | |
|---|---|
| Board | E, `v2/ecad/pcb-e1-dock-e7` |
| Source revision | `1f614233998c3087a53abfa977be134465ce9f47` (docs(review): the review of the 26 September progress report is recorded, to be executed item by item [MESHSAT-1357]), 2026-09-26T14:13:16+02:00 |
| Compared with | `82dd1e4dc44efabeee1164a995cda4e866610f3d` (fix(tests): the blocked-land fixture no longer overwrites the lcsc_fill evidence rules CMP-002 and SUP-001 read [MESHSAT-1357]) |
| Declared phase | E17, from `tools/boards/e.json`: the phase of the board's committed LAYOUT. The layout is not part of this packet and is not judged by it (rule SCH-002 decides whether it carries this netlist). The schematic's own title-block label is E42P |
| Complete | yes |
| Built | 2026-09-26T15:55:47Z with KiCad 9.0.9, tool sha256 `7913d0a57567d896` |
| Part sources read | a SOURCES.yaml supplied with --sources, identified by its sha256, sha256 `2b192f2bb8ded051` |

## What this packet is, and is not

- It is a review input for a qualified reviewer: the schematic of one board exactly as committed at the source revision, with what changed since the previous revision and why, the parts and their primary sources, and the interfaces it shares with other boards.
- It is NOT a release. No layout, fabrication, order or approval follows from it. Hardware state: unbuilt prototype design.
- It is desk material only: no bench measurement, EMC, thermal or environmental test exists for this board.
- The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 5) asked for it.

## Contents

| File | What | sha256 (first 16) |
|---|---|---|
| `bom/NOT_FOR_FAB-parts-identity.csv` | the part identity and footprint map, one row per BOM line (NOT_FOR_FAB: a review input, never an order file) | `3df14323c8da6f90` |
| `bom/NOT_FOR_FAB-pcb-e1-dock-bom.csv` | the BOM exported from the committed schematic (build_sch.sh's own fields and grouping), byte for byte as KiCad wrote it; NOT_FOR_FAB in its name because it is a review input, never an order file | `ad363511f0646b78` |
| `bom/parts-identity.json` | machine-readable record, see README.md | `96f1c2da5dd0fc7c` |
| `bom/sources-coverage.json` | machine-readable record, see README.md | `b33536d47b05c774` |
| `changes/attribution-read-by-hand.yaml` | the reading of every changed reference by hand: IDs, the generator lines that carry them, the reason in words; the build checked every ID against its lines | `3198b8024b4ab84f` |
| `changes/changes.json` | machine-readable record, see README.md | `32099da523b7fd09` |
| `changes/gen_sch_e.diff` | the generator diff between the two revisions | `23c5e07154434e8c` |
| `changes/prev-82dd1e4d-gen_sch_e.py` | the generator at the previous revision | `5cf0b323d51cda6a` |
| `changes/prev-82dd1e4d.net` | the committed netlist at the previous revision | `a7784a00cc7a89db` |
| `contracts/check_contracts.log` | the revision's check_contracts.py output in the packet's work copy | `6b3e2290bec66008` |
| `contracts/contracts.json` | machine-readable record, see README.md | `73585d9994e3915a` |
| `interfaces/interfaces.json` | machine-readable record, see README.md | `9e1f0d50d50d382c` |
| `native/boards-e.json` | the board declaration (declared phase, classes) | `72adb2e89b490449` |
| `native/fp-lib-table` | the project's footprint library table | `9c2d14bd7a666d84` |
| `native/gen_sch_e.py` | the generator that writes the schematic: the design's source of truth, with the finding IDs in its comments | `d120ebfb9afbee6e` |
| `native/meshsat.pretty/PogoTargets_2x6.kicad_mod` | project footprint used by this board | `94b2f0134ac6ee11` |
| `native/meshsat.pretty/Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm.kicad_mod` | project footprint used by this board | `4fd7bf77769ab06d` |
| `native/meshsat.pretty/SolderPad_8x6.kicad_mod` | project footprint used by this board | `c9da5808d2ef317e` |
| `native/netlist/pcb-e1-dock-intent.json` | the generator's intent file (rails, nodes, bypass declarations) | `9ae33eb17d04670e` |
| `native/netlist/pcb-e1-dock.net` | the committed netlist (KiCad s-expression) the change report reads | `d910e49c5f5f50b2` |
| `native/netlist/pcb-e1-dock.net.prov.json` | the netlist's provenance sidecar (generator identity, schematic sha) | `7c67af4ec83e09c7` |
| `native/pcb-e1-dock.kicad_pro` | its KiCad project file | `9f3d11f497873838` |
| `native/pcb-e1-dock.kicad_sch` | the committed schematic at the source revision (KiCad 9 native) | `4b0438bec4a85b45` |
| `open/holds-and-decisions.json` | machine-readable record, see README.md | `99ea9e6e5d83c08a` |
| `schematic/pcb-e1-dock-erc.json` | KiCad ERC of the committed schematic, every severity; a report, not a verdict | `10319c5d8dcdbdb5` |
| `schematic/pcb-e1-dock-schematic-sheet.pdf` | the whole schematic as one sheet | `44cba105a4629cbf` |
| `schematic/pcb-e1-dock-schematic.pdf` | the schematic, paged into A3 blocks by the revision's own sch_pages.py (what build_sch.sh publishes) | `43e6759734770250` |

Verify: `python3 v2/ecad/tools/review_packet.py verify <this folder>` or `sha256sum -c SHA256SUMS` inside it. `MANIFEST.json` carries the full record.

## Schematic exports

- KiCad 9.0.9 exported the PDFs, BOM, ERC and netlist from the committed schematic.
- The exported netlist against the committed netlist: **PARITY_AFTER_NOISE** (regen_compare; PARITY_AFTER_NOISE means only the export's own path, date and tool differ).
- At the previous revision, the same comparison: **PARITY_AFTER_NOISE**, so both ends of the change report are schematic content.
- ERC, every severity, as a report and not a verdict (the project's gate `erc_gate.py` applies the board's allow list): warning:endpoint_off_grid 61, warning:lib_symbol_issues 257, warning:unconnected_wire_endpoint 37.
- kicad-cli printed "schematic has annotation errors" on the bom and netlist exports. KiCad does not say which symbol it means. A text reading of the committed schematic finds no repeated (reference, unit) and no unannotated reference among 257 symbol instances, so the cause is NOT ESTABLISHED; the exported netlist's parity above is what shows the export carries the committed circuit.

## Changes against `82dd1e4d`

Components 163 to 179, nets 118 to 124: 16 added, 0 removed, 11 changed. Generator lines added or changed: 237. Details per reference, with the generator lines and the comment each ID was read from, are in `changes/changes.json`.

**How each row was read.** Every changed reference was read by hand (`changes/attribution-read-by-hand.yaml`, the session (review stream PKT), 26 September 2026, from gen_sch_e.py at both revisions and the round-4 board E record): the IDs, the generator lines at `1f614233` that carry them, and the reason in words. The build refused the file unless every ID is written on its cited lines and every cited range is tied to the change (it names the reference or one of its nets, is the statement's own comment or its section header, or the row states the tie). The mechanical reading stays in `changes/changes.json` (`evidence.automatic`) beside each row, with `agrees` saying whether it matches; it differs on 21 of 27 rows, mostly because it credits every ID written in a part's own comment, including IDs cited there as context.

**Counts.** 27 changes: 27 carry a finding ID; 0 carry only an owner ruling, a decision or a rule ID; 0 carry no ID of any kind; 0 are UNVERIFIED_ATTRIBUTION. So **0 changes have no finding ID**. Finding IDs include the round records' own item IDs (R4D-1, R4E-02, RP-17), which are the session's records of that round.

| Ref | Kind | What changed | Finding IDs | Rulings and decisions | Rules | Status | Read | Generator lines (cited) |
|---|---|---|---|---|---|---|---|---|
| C52 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, C14663 | S-11, W1-F04, W5-F11 | D-02b, D-03.2 |  | TRACED | hand | gen_sch_e.py 524-537 |
| C53 | ADDED | 1n, Capacitor_SMD:C_0603_1608Metric, C1588 | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 575-576 |
| C54 | ADDED | 10u 25V, Capacitor_SMD:C_1206_3216Metric, C89632 | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 575 |
| C55 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, C14663 | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 575 |
| C56 | ADDED | 1u, Capacitor_SMD:C_0603_1608Metric, C15849 | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 632 |
| C57 | ADDED | 1u, Capacitor_SMD:C_0603_1608Metric, C15849 | C-05, S-10, W1-F05 |  |  | TRACED | hand | gen_sch_e.py 547-557 |
| C58 | ADDED | 1u, Capacitor_SMD:C_0603_1608Metric, C15849 | C-05, S-10, W1-F05 |  |  | TRACED | hand | gen_sch_e.py 547-557 |
| D1 | CHANGED | value: SMCJ40A (input surge: 40 V standoff on a line specified to 3 -> SMCJ40A (input surge: 40 V standoff on a line specified to 3; pin 1: GND_V -> DC_P; pin 2: DC_P -> GND_V | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_e.py 296 |
| D2 | CHANGED | value: SMCJ40A (bus clamp: 40 V standoff on the 9 to 36 V bus) -> SMCJ40A (bus clamp: 40 V standoff on the 9 to 36 V bus; unid; pin 1: GND -> VIN_RAW; pin 2: VIN_RAW -> GND | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_e.py 296 |
| D3 | CHANGED | value: SMCJ18A (pack node clamp) -> SMCJ18A (pack node clamp, unidirectional: cathode on CELL_F); lcsc:  -> C374030; pin 1: GND -> CELL_F; pin 2: CELL_F -> GND | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_e.py 220 |
| D4 | CHANGED | value: SMCJ28A (panel surge: 28 V standoff, conducting from 31.1 V, -> SMCJ28A (panel surge: 28 V standoff, conducting from 31.1 V,; pin 1: GND -> PV_P; pin 2: PV_P -> GND | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_e.py 419 |
| D10 | CHANGED | value: SMCJ40A (shore inlet clamp at the entry, in front of the ide -> SMCJ40CA (bidirectional, Littelfuse SMCJ40 row: 40 V standof; lcsc: C224052 -> C80273; pin 1: GND_V -> DC_F; pin 2: DC_F -> GND_V | R4E-01, S-09 |  |  | TRACED | hand | gen_sch_e.py 354 |
| J_GEIGER | CHANGED | value: Geiger counter module (RadiationD-v1.1 class): 5 V, GND, pul -> Geiger counter module (RadiationD-v1.1 class): 5 V switched ; pin 1: +5V_E6 -> +5V_GEIGER | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 575 |
| J_SMB | CHANGED | value: pack SMBus (XH or pin header): section A SDA SCL on I2C0, se -> SMBus lead to board P, JST-XH 1x4 (B4B-XH-A), P's pin order:; footprint: Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical -> Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical; lcsc:  -> C594232; pin 1: SDA0 -> SMBC; pin 2: SCL0 -> SMBD; pin 3: SDA1 -> GND; pin 4: SCL1 -> PRES_LEAD; pin 5: GND -> None; pin 6: GND -> None | A07, S-05 |  |  | TRACED | hand | gen_sch_e.py 197 |
| J_TAMP | ADDED | JST-XH 1x2 (B2B-XH-A): lid and tamper reed sensor lead, Littelfuse 59140-1-S-05-, Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical, C158012 | S-11, W1-F04, W5-F11 | D-02b, D-03.2 |  | TRACED | hand | gen_sch_e.py 524-526 |
| L2 | CHANGED | value: Bourns SRF1260-4R7Y dual-winding choke (7.2 A per winding at -> Bourns SRF1260-1R5Y dual-winding choke, common-mode connecti; pin 2: VIN_RAW -> GND_V; pin 3: GND_V -> VIN_RAW | F-IN-02, R4E-02, R4E-09 |  |  | TRACED | hand | gen_sch_e.py 314, 329 |
| R34 | CHANGED | pin 1: SDA0 -> SMBD | A07, S-05 |  |  | TRACED | hand | gen_sch_e.py 197-202 |
| R35 | CHANGED | pin 1: SCL0 -> SMBC | A07, S-05 |  |  | TRACED | hand | gen_sch_e.py 197-202 |
| R52 | ADDED | 100k, Resistor_SMD:R_0603_1608Metric, C25803 | S-11, W1-F04, W5-F11 | D-02b, D-03.2 |  | TRACED | hand | gen_sch_e.py 524-537 |
| R53 | ADDED | 10k, Resistor_SMD:R_0603_1608Metric, C25804 | S-11, W1-F04, W5-F11 | D-02b, D-03.2 |  | TRACED | hand | gen_sch_e.py 524-537 |
| R54 | ADDED | 1k, Resistor_SMD:R_0603_1608Metric, C21190 | A07, S-05 |  |  | TRACED | hand | gen_sch_e.py 197-207 |
| R55 | ADDED | 1M, Resistor_SMD:R_0603_1608Metric, C22935 | A07, S-05 |  |  | TRACED | hand | gen_sch_e.py 197-207 |
| R56 | ADDED | 100k, Resistor_SMD:R_0603_1608Metric, C25803 | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 132-140 |
| R57 | ADDED | 4.7R, Resistor_SMD:R_0603_1608Metric, C23164 | C-05, S-10, W1-F05 |  |  | TRACED | hand | gen_sch_e.py 547-557 |
| U10 | CHANGED | pin 27: unconnected-(U10-NC-Pad27) -> TAMPER_IO; pin 28: unconnected-(U10-NC-Pad28) -> PRES_IO; pin 29: unconnected-(U10-NC-Pad29) -> GEIGER_EN; pin 4: SDA0 -> SMBD; pin 5: SCL0 -> SMBC | A07, F-BP-02, S-05, S-11 |  |  | TRACED | hand | gen_sch_e.py 503-504, 197-204 |
| U16 | ADDED | TPS22810DRV, Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm, no LCSC code | F-BP-02 |  |  | TRACED | hand | gen_sch_e.py 575 |
| U17 | ADDED | SGP41-D-R4 VOC and NOx gas sensor, battery-bay air (I2C 0x59; DFN-6: 1 VDD 2 VSS, meshsat:Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm, C3659325 | C-05, S-10, W1-F05 |  |  | TRACED | hand | gen_sch_e.py 547-549 |
IDs found only on unchanged lines are listed in `changes/changes.json` as `context` and never counted as the change's. The generator diff is `changes/gen_sch_e.diff`.

## Part identity and footprints

124 BOM lines. 13 carry an entry in `v2/vendor/SOURCES.yaml` (identity, grade and the held documents with revision and sha256): 11 joined by the exact LCSC code of the line, and 2 lines that carry NO LCSC code, joined because the entry names this board and either its `where`, read at the revision its line number was written against, points at the line's defining statement while naming the reference or the part, or its fitted order code is written in the line's value. The other 111 lines carry no entry. SOURCES.yaml's own header says which parts it covers (its criteria (a) to (c)) and its `owed` list names the entries still owed; this packet does not judge criticality. `jlc_certified_row` is the certification table's row where it has one: that table was cut from older deliverables and a CERTIFIED there is not proof of identity (SOURCES.yaml header). Full map: `bom/NOT_FOR_FAB-parts-identity.csv` and `bom/parts-identity.json`; which entries name this board and what each joined: `bom/sources-coverage.json`.

**Joined by the line's LCSC code**

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Documents |
|---|---|---|---|---|---|
| D1 | SMCJ40A (input surge: 40 V standoff on a line specified to 3 | `Diode_SMD:D_SMC` | C224052 | tvs-surge-clamps | `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` (Revised 11/20/15) |
| D10 | SMCJ40CA (bidirectional, Littelfuse SMCJ40 row: 40 V standof | `Diode_SMD:D_SMC` | C80273 | tvs-surge-clamps | `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` (Revised 11/20/15) |
| D2 | SMCJ40A (bus clamp: 40 V standoff on the 9 to 36 V bus; unid | `Diode_SMD:D_SMC` | C224052 | tvs-surge-clamps | `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` (Revised 11/20/15) |
| D3 | SMCJ18A (pack node clamp, unidirectional: cathode on CELL_F) | `Diode_SMD:D_SMC` | C374030 | tvs-surge-clamps | `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` (Revised 11/20/15) |
| D4 | SMCJ28A (panel surge: 28 V standoff, conducting from 31.1 V, | `Diode_SMD:D_SMC` | C224047 | tvs-surge-clamps | `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` (Revised 11/20/15) |
| D9 | USBLC6-2SC6 | `Package_TO_SOT_SMD:SOT-23-6` | C7519 | usb-esd-array | `v2/vendor/st/st-usblc6-2-esd-protection.pdf` (Rev 7, December 2021) |
| J_BATT | Amass XT60-M: the BB-2590/U pack cable BTA-70762-2 (pin 2, t | `Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical` | C98733 | pack-connector | `v2/vendor/battery/amass-xt60-spec-tme.pdf` (V1.2 (stated on the sheet); PDF created ); `v2/vendor/battery/amass-xt60e-m-shoptronica.pdf` (PDF title 'AMASS XT60C-M SPEC', ModDate ) |
| J_SMB | SMBus lead to board P, JST-XH 1x4 (B4B-XH-A), P's pin order: | `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical` | C594232 | pack-and-lid-leads-jst-xh | `v2/vendor/connectors/jst-xh-catalogue.pdf` (not printed; the catalogue as served on ) |
| J_TAMP | JST-XH 1x2 (B2B-XH-A): lid and tamper reed sensor lead, Litt | `Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical` | C158012 | pack-and-lid-leads-jst-xh | `v2/vendor/connectors/jst-xh-catalogue.pdf` (not printed; the catalogue as served on ) |
| U10 | RP2040 sensor controller (USB to B16 through the dock) | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` | C2040 | rp2040 | `v2/vendor/rp2040/rpi-rp2040-datasheet.pdf` (build-date 2025-02-20, build-version 318); `v2/vendor/rp2040/rpi-rp2040-hardware-design.pdf` (not read; PDF ModDate 2026-08-20) |
| U17 | SGP41-D-R4 VOC and NOx gas sensor, battery-bay air (I2C 0x59 | `meshsat:Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm` | C3659325 | battery-bay-gas-sensor | `v2/vendor/sensirion/sgp41-datasheet.pdf` (version 1.0, December 2021) |

**Lines with no LCSC code, joined to the entry that covers them.** No order code fixes the maker of such a line, so the entry's identity verdict speaks for the part it names, not for a purchase; the entry says what the line's order code is, or that it is not pinned.

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Joined by | Documents |
|---|---|---|---|---|---|---|
| L2 | Bourns SRF1260-1R5Y dual-winding choke, common-mode connecti | `Inductor_SMD:L_CommonModeChoke_Bourns_SRF1260` | none | vehicle-input-choke | where gen_sch_e.py:341 at 1f614233 (the value names SRF1260-1R5Y) | `v2/vendor/power/bourns-srf1260-common-mode-choke.pdf` (REV. 03/18) |
| U16 | TPS22810DRV | `Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` | none | load-switch-tps22810 | where gen_sch_e.py:577 at 1f614233 (names U16) | `v2/vendor/ti/ti-tps22810-load-switch.pdf` (SLVSDH0C, December 2016, revised January) |

Every entry of SOURCES.yaml that names board E (and is on this revision's generators) joined at least one BOM line here (8 entries).

## Cross-board and harness contracts that touch this board

The revision's own `check_contracts.py`, run in this packet's work copy (never in the repository), traced so each contract carries the boards it names: 9 name board E: **9 PASS, 0 FAIL, 0 UNJUDGED**.
- Board A was regenerated from its generator at the source revision in the work copy, because its committed netlist predates the widened generator identity: gen_sch exit 0, build_sch exit 0, regenerated netlist against the committed one: **PARITY_AFTER_NOISE**. Board A's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it).
- Board B was regenerated from its generator at the source revision in the work copy, because its committed netlist predates the widened generator identity: gen_sch exit 0, build_sch exit 0, regenerated netlist against the committed one: **PARITY_AFTER_NOISE**. Board B's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it).

| Result | Contract | Boards | Where |
|---|---|---|---|
| PASS | dock 2x6 contact map identical on A (J_DOCK) and E (J_BLK) | A, E | `check_contracts.py:239` |
| PASS | E6: SHORE_INHIBIT reaches the sensor controller U10 (directly or through its series resistor) | E | `check_contracts.py:248` |
| PASS | E: the 12 AWG lands P_CP and P_CN exist | E | `check_contracts.py:256` |
| PASS | E6: the pack return lands on GND (the 14.4 V node's return is the ground plane, 32.56) | E | `check_contracts.py:258` |
| PASS | E: the XT60 carries the pack on pin 2 and the return on pin 1, which is what P's leads land on | E, P | `check_contracts.py:371` |
| PASS | the pack pair is not crossed between board P's leads and board E's XT60 | E, P | `check_contracts.py:378` |
| PASS | E: R48 (22R (pulse input series)) is in series with a real pin on both sides | E | `check_contracts.py:402` |
| PASS | rail CELL+: the shares sum to 1.0% within the 2.0% the rail declares | A, E | `check_contracts.py:448` |
| PASS | rail VIN_RAW: the shares sum to 2.0% within the 2.0% the rail declares | A, E | `check_contracts.py:448` |

## Interfaces declared for this board (`tools/pcb_interfaces.yaml`)

- **USB_FULL_SPEED**: USB 1.1 and 2.0 FULL speed, 12 Mb/s, between parts on one board. Impedance not stated (tolerance not stated), intra-pair not stated, maximum length not stated. Nets here: USB_DM_R, USB_DP_R, USB_E6_N, USB_E6_P. Source: TI TUSB2046B datasheet, features, first page (`v2/vendor/ti/ti-tusb2046b.pdf`); TI PCM2912A datasheet, features (`v2/vendor/ti/ti-pcm2912a.pdf`).

## Holds and open decisions

- Hold on this board: decision 31, board E's exposed-port protection: BLOCKED_DECISION_31, NOT_READY, HELD.
- Open decision 42: a decoupling capacitor cannot be both within 3 mm of a fine-pitch pin and outside that part's escape fan (boards: not declared; the text names them).

## Not in this packet

- A layout. The board file of the declared phase is not included and nothing here judges it; whether it carries this netlist is rule SCH-002's question.
- Change marks on the schematic sheets. The PDFs are plain exports of the committed schematic; what changed is marked in the change table above, by reference, with the generator lines that carry each finding ID.
- Calculations and fault-state diagrams. Where the review asks for them (battery protection, board P; the charger state sequence, board A) they are separate work items with their own owner; this packet carries the circuit they will be judged against.
- Physical evidence of any kind.
