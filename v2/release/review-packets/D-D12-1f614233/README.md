# Review packet: board D (pcb-d-aprs) at 1f614233

**UNBUILT PROTOTYPE DESIGN. No board of this set has been fabricated, assembled or tested; nothing in this packet is physical evidence. A review packet is a review input: it does NOT release this board to fabrication, layout or ordering, and it approves nothing.**

**READINESS OF THIS PACKET: QUARANTINED, NOT_FOR_FAB.** No file here is an order file; the two BOM files carry NOT_FOR_FAB in their names.
This board is HELD by decision 31 (board D's exposed-port protection), in the hold's own words: ROUTING_STATUS PASS, ELECTRICAL_PROTECTION_STATUS BLOCKED_DECISION_31, FAB_READINESS NOT_READY, PUBLICATION_STATUS HELD. The hold permits: "a review package clearly quarantined as NOT_FOR_FAB may be generated". It forbids: "any orderable fabrication package, any promotion of the board or its folder".

| | |
|---|---|
| Board | D, `v2/ecad/pcb-d-aprs-d9` |
| Source revision | `1f614233998c3087a53abfa977be134465ce9f47` (docs(review): the review of the 26 September progress report is recorded, to be executed item by item [MESHSAT-1357]), 2026-09-26T14:13:16+02:00 |
| Compared with | `82dd1e4dc44efabeee1164a995cda4e866610f3d` (fix(tests): the blocked-land fixture no longer overwrites the lcsc_fill evidence rules CMP-002 and SUP-001 read [MESHSAT-1357]) |
| Declared phase | D12, from `tools/boards/d.json`: the phase of the board's committed LAYOUT. The layout is not part of this packet and is not judged by it (rule SCH-002 decides whether it carries this netlist). The schematic's own title-block label is D37P |
| Complete | yes |
| Built | 2026-09-26T15:53:22Z with KiCad 9.0.9, tool sha256 `7913d0a57567d896` |
| Part sources read | a SOURCES.yaml supplied with --sources, identified by its sha256, sha256 `2b192f2bb8ded051` |

## What this packet is, and is not

- It is a review input for a qualified reviewer: the schematic of one board exactly as committed at the source revision, with what changed since the previous revision and why, the parts and their primary sources, and the interfaces it shares with other boards.
- It is NOT a release. No layout, fabrication, order or approval follows from it. Hardware state: unbuilt prototype design.
- It is desk material only: no bench measurement, EMC, thermal or environmental test exists for this board.
- The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 5) asked for it.

## Contents

| File | What | sha256 (first 16) |
|---|---|---|
| `bom/NOT_FOR_FAB-parts-identity.csv` | the part identity and footprint map, one row per BOM line (NOT_FOR_FAB: a review input, never an order file) | `ed360faa6c3ea43b` |
| `bom/NOT_FOR_FAB-pcb-d-aprs-bom.csv` | the BOM exported from the committed schematic (build_sch.sh's own fields and grouping), byte for byte as KiCad wrote it; NOT_FOR_FAB in its name because it is a review input, never an order file | `923ce0a8c4ebe85e` |
| `bom/parts-identity.json` | machine-readable record, see README.md | `2d7a26127a0b87d3` |
| `bom/sources-coverage.json` | machine-readable record, see README.md | `55c85301647aef8b` |
| `changes/attribution-read-by-hand.yaml` | the reading of every changed reference by hand: IDs, the generator lines that carry them, the reason in words; the build checked every ID against its lines | `2a85b4fe4c1614b1` |
| `changes/changes.json` | machine-readable record, see README.md | `5d841ca2d4a5d204` |
| `changes/gen_sch_d.diff` | the generator diff between the two revisions | `4343d9a6888fcbdc` |
| `changes/prev-82dd1e4d-gen_sch_d.py` | the generator at the previous revision | `f1fef1594efd3e6e` |
| `changes/prev-82dd1e4d.net` | the committed netlist at the previous revision | `9a087a115c7bb175` |
| `contracts/check_contracts.log` | the revision's check_contracts.py output in the packet's work copy | `6b3e2290bec66008` |
| `contracts/contracts.json` | machine-readable record, see README.md | `db1d750a53d217b1` |
| `interfaces/interfaces.json` | machine-readable record, see README.md | `285f33881ca301a3` |
| `native/boards-d.json` | the board declaration (declared phase, classes) | `e0f787a8bfe117a1` |
| `native/fp-lib-table` | the project's footprint library table | `9c2d14bd7a666d84` |
| `native/gen_sch_d.py` | the generator that writes the schematic: the design's source of truth, with the finding IDs in its comments | `c4317b3f53b69212` |
| `native/meshsat.pretty/IDC-Header_2x08_P2.54mm_Vertical_NarrowPad.kicad_mod` | project footprint used by this board | `a01394897fbff050` |
| `native/meshsat.pretty/NiceRF_SA868.kicad_mod` | project footprint used by this board | `e7a55e1a606daff4` |
| `native/netlist/pcb-d-aprs-intent.json` | the generator's intent file (rails, nodes, bypass declarations) | `a8c9ea452c4aff59` |
| `native/netlist/pcb-d-aprs.net` | the committed netlist (KiCad s-expression) the change report reads | `e2534f5e34c1f5bf` |
| `native/netlist/pcb-d-aprs.net.prov.json` | the netlist's provenance sidecar (generator identity, schematic sha) | `7e21f4b5fad79d70` |
| `native/pcb-d-aprs.kicad_pro` | its KiCad project file | `a820c200f1b4a542` |
| `native/pcb-d-aprs.kicad_sch` | the committed schematic at the source revision (KiCad 9 native) | `b9a44e503a3342b3` |
| `open/holds-and-decisions.json` | machine-readable record, see README.md | `c447fd05b2e462c3` |
| `schematic/pcb-d-aprs-erc.json` | KiCad ERC of the committed schematic, every severity; a report, not a verdict | `957329a2129ff5f9` |
| `schematic/pcb-d-aprs-schematic-sheet.pdf` | the whole schematic as one sheet | `fb9f4470b7776dc9` |
| `schematic/pcb-d-aprs-schematic.pdf` | the schematic, paged into A3 blocks by the revision's own sch_pages.py (what build_sch.sh publishes) | `cd12bba8cb1130a3` |

Verify: `python3 v2/ecad/tools/review_packet.py verify <this folder>` or `sha256sum -c SHA256SUMS` inside it. `MANIFEST.json` carries the full record.

## Schematic exports

- KiCad 9.0.9 exported the PDFs, BOM, ERC and netlist from the committed schematic.
- The exported netlist against the committed netlist: **PARITY_AFTER_NOISE** (regen_compare; PARITY_AFTER_NOISE means only the export's own path, date and tool differ).
- At the previous revision, the same comparison: **PARITY_AFTER_NOISE**, so both ends of the change report are schematic content.
- ERC, every severity, as a report and not a verdict (the project's gate `erc_gate.py` applies the board's allow list): warning:endpoint_off_grid 33, warning:lib_symbol_issues 309, warning:unconnected_wire_endpoint 44.
- kicad-cli printed "schematic has annotation errors" on the bom and netlist exports. KiCad does not say which symbol it means. A text reading of the committed schematic finds no repeated (reference, unit) and no unannotated reference among 309 symbol instances, so the cause is NOT ESTABLISHED; the exported netlist's parity above is what shows the export carries the committed circuit.

## Changes against `82dd1e4d`

Components 213 to 221, nets 172 to 174: 8 added, 0 removed, 15 changed. Generator lines added or changed: 271. Details per reference, with the generator lines and the comment each ID was read from, are in `changes/changes.json`.

**How each row was read.** Every changed reference was read by hand (`changes/attribution-read-by-hand.yaml`, the session (review stream PKT), 26 September 2026, from gen_sch_d.py at both revisions and the round-4 board D record): the IDs, the generator lines at `1f614233` that carry them, and the reason in words. The build refused the file unless every ID is written on its cited lines and every cited range is tied to the change (it names the reference or one of its nets, is the statement's own comment or its section header, or the row states the tie). The mechanical reading stays in `changes/changes.json` (`evidence.automatic`) beside each row, with `agrees` saying whether it matches; it differs on 14 of 23 rows, mostly because it credits every ID written in a part's own comment, including IDs cited there as context.

**Counts.** 23 changes: 22 carry a finding ID; 0 carry only an owner ruling, a decision or a rule ID; 1 carry no ID of any kind; 0 are UNVERIFIED_ATTRIBUTION. So **1 changes have no finding ID**. Finding IDs include the round records' own item IDs (R4D-1, R4E-02, RP-17), which are the session's records of that round.

| Ref | Kind | What changed | Finding IDs | Rulings and decisions | Rules | Status | Read | Generator lines (cited) |
|---|---|---|---|---|---|---|---|---|
| C15 | CHANGED | pin 1: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 326 |
| C16 | CHANGED | pin 1: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 326 |
| C17 | CHANGED | pin 1: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 326 |
| C61 | CHANGED | value: 4.7n -> 1u; footprint: Capacitor_SMD:C_0402_1005Metric -> Capacitor_SMD:C_0603_1608Metric; lcsc:  -> C15849; pin 1: VGG_CT -> +5V_D8 | F-PR-02 |  |  | TRACED | hand | gen_sch_d.py 601 |
| C62 | CHANGED | value: 100n -> 2.2u 16V X5R; lcsc:  -> C23630 | F-PR-02 |  |  | TRACED | hand | gen_sch_d.py 483-517 |
| C64 | ADDED | 1u, Capacitor_SMD:C_0603_1608Metric, C15849 | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 288-290 |
| C65 | ADDED | 1u, Capacitor_SMD:C_0603_1608Metric, C15849 | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 288-290 |
| D1 | CHANGED | value: SMBJ5.0A -> SMBJ6.0A (6.0 V standoff on the 5.09 V mezzanine rail); lcsc:  -> C83270; pin 1: GND -> +5V_D8; pin 2: +5V_D8 -> GND | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_d.py 216 |
| D10 | CHANGED | value: PESD5V0S1BA bidirectional ESD clamp at the jack: headset 1 m -> PESD12VL1BA bidirectional ESD clamp at the jack: headset 1 m; lcsc: C19224 -> C38558 | W6-F14, W7-F3 |  |  | TRACED | hand | gen_sch_d.py 416-425 |
| D13 | CHANGED | value: PESD5V0S1BA bidirectional ESD clamp at the jack: headset 2 m -> PESD12VL1BA bidirectional ESD clamp at the jack: headset 2 m; lcsc: C19224 -> C38558 | W6-F14, W7-F3 |  |  | TRACED | hand | gen_sch_d.py 416-425 |
| R8 | CHANGED | pin 2: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 283 |
| R9 | CHANGED | pin 2: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 271, 287 |
| R10 | CHANGED | pin 2: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 271, 287 |
| R33 | CHANGED | value: 4.7k -> 470R; lcsc:  -> C23179 | A01 |  |  | TRACED | hand | gen_sch_d.py 351 |
| R34 | CHANGED | value: 100k -> 4.7k | A01 |  |  | TRACED | hand | gen_sch_d.py 351 |
| R80 | ADDED | 56.2k 0.1% 25ppm, Resistor_SMD:R_0603_1608Metric, C705784 | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 288-292 |
| R81 | ADDED | 10.7k 0.1% 25ppm, Resistor_SMD:R_0603_1608Metric, C861078 | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 288-292 |
| R82 | ADDED | 71.5k 1%, Resistor_SMD:R_0603_1608Metric, C23103 | F-PR-02 |  |  | TRACED | hand | gen_sch_d.py 483-493 |
| R83 | ADDED | 10.0k 1%, Resistor_SMD:R_0603_1608Metric, C25804 | F-PR-02 |  |  | TRACED | hand | gen_sch_d.py 483-493 |
| TP25 | ADDED | +3V4_HUB, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  |  | NO_ID_OF_ANY_KIND | hand | gen_sch_d.py 550-552 |
| U4 | CHANGED | value: TUSB2046BI four-port USB 2.0 full-speed hub (LQFP-32; BUSPWR -> TUSB2046IBVFR four-port USB 2.0 full-speed hub (TI, LQFP-32 ; lcsc:  -> C702369; pin 25: +3V3_D8 -> +3V4_HUB; pin 26: +3V3_D8 -> +3V4_HUB; pin 3: +3V3_D8 -> +3V4_HUB; pin 6: +3V3_D8 -> +3V4_HUB | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 58, 271-281 |
| U15 | CHANGED | value: TPS22810DRV -> TLV75801PDRVR adjustable LDO, PA gate bias VGG 4.48 V while ; lcsc:  -> C2876308; pin 2: unconnected-(U15-QOD-Pad2) -> VGG_FB; pin 3: VGG_CT -> GND; pin 4: GND -> PA_KEY; pin 5: PA_KEY -> unconnected-(U15-NC-Pad5) | F-PR-02 |  |  | TRACED | hand | gen_sch_d.py 483 |
| U17 | ADDED | TLV75801PDBVR adjustable LDO, +3V4_HUB 3.44 V for the hub (1 IN 2 GND 3 EN 4 FB , Package_TO_SOT_SMD:SOT-23-5, C2877852 | W6-F5 |  |  | TRACED | hand | gen_sch_d.py 288 |

**The 1 changes with no finding ID, and their reason**

- TP25 (no ID of any kind; round record: round-4 board D record, R4D-2 (W6-F5): 'TP25 is its test point'; the generator's comment at 550 to 552 carries no ID): a test pad on the hub's own supply +3V4_HUB, for the bench measurement owed to TEST-PLAN.md; appended so TP1 to TP24 keep their numbers

IDs found only on unchanged lines are listed in `changes/changes.json` as `context` and never counted as the change's. The generator diff is `changes/gen_sch_d.diff`.

## Part identity and footprints

107 BOM lines. 17 carry an entry in `v2/vendor/SOURCES.yaml` (identity, grade and the held documents with revision and sha256): 16 joined by the exact LCSC code of the line, and 1 lines that carry NO LCSC code, joined because the entry names this board and either its `where`, read at the revision its line number was written against, points at the line's defining statement while naming the reference or the part, or its fitted order code is written in the line's value. The other 90 lines carry no entry. SOURCES.yaml's own header says which parts it covers (its criteria (a) to (c)) and its `owed` list names the entries still owed; this packet does not judge criticality. `jlc_certified_row` is the certification table's row where it has one: that table was cut from older deliverables and a CERTIFIED there is not proof of identity (SOURCES.yaml header). Full map: `bom/NOT_FOR_FAB-parts-identity.csv` and `bom/parts-identity.json`; which entries name this board and what each joined: `bom/sources-coverage.json`.

**Joined by the line's LCSC code**

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Documents |
|---|---|---|---|---|---|
| D1 | SMBJ6.0A (6.0 V standoff on the 5.09 V mezzanine rail) | `Diode_SMD:D_SMB` | C83270 | tvs-surge-clamps | `v2/vendor/power/littelfuse-smbj-series-tvs.pdf` (Revised JC.07/04/25) |
| D10 | PESD12VL1BA bidirectional ESD clamp at the jack: headset 1 m | `Diode_SMD:D_SOD-323` | C38558 | esd-mic-clamps | `v2/vendor/nexperia/nexperia-pesd12vl1ba.pdf` (14 April 2023) |
| D11 | PESD5V0S1BA bidirectional ESD clamp at the jack: headset 1 p | `Diode_SMD:D_SOD-323` | C19224 | esd-headset-clamps | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (PESD5V0S1BA v.6, 26 April 2024 (revision) |
| D12 | PESD5V0S1BA bidirectional ESD clamp at the jack: headset 2 s | `Diode_SMD:D_SOD-323` | C19224 | esd-headset-clamps | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (PESD5V0S1BA v.6, 26 April 2024 (revision) |
| D13 | PESD12VL1BA bidirectional ESD clamp at the jack: headset 2 m | `Diode_SMD:D_SOD-323` | C38558 | esd-mic-clamps | `v2/vendor/nexperia/nexperia-pesd12vl1ba.pdf` (14 April 2023) |
| D14 | PESD5V0S1BA bidirectional ESD clamp at the jack: headset 2 p | `Diode_SMD:D_SOD-323` | C19224 | esd-headset-clamps | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (PESD5V0S1BA v.6, 26 April 2024 (revision) |
| D9 | PESD5V0S1BA bidirectional ESD clamp at the jack: headset 1 s | `Diode_SMD:D_SOD-323` | C19224 | esd-headset-clamps | `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` (PESD5V0S1BA v.6, 26 April 2024 (revision) |
| J_HS1 | JST-PH 1x5 socket: headset 1, SPK GND MIC GND PTT (the lead  | `Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical` | C157993 | jst-ph-headers | `v2/vendor/connectors/jst-ph-catalogue.pdf` (not printed; PDF of 27 January 2026 per ) |
| J_HS2 | JST-PH 1x5 socket: headset 2, SPK GND MIC GND PTT (the lead  | `Connector_JST:JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical` | C157993 | jst-ph-headers | `v2/vendor/connectors/jst-ph-catalogue.pdf` (not printed; PDF of 27 January 2026 per ) |
| Q1 | 2N7002 PA_EN -> H/L low (never tie H/L high) | `Package_TO_SOT_SMD:SOT-23` | C8545 | logic-nfet-2n7002 | `v2/vendor/power/jscj-2n7002-c8545.pdf` (J, Sep 2016 (as printed)) |
| Q2 | 2N7002 relay coil | `Package_TO_SOT_SMD:SOT-23` | C8545 | logic-nfet-2n7002 | `v2/vendor/power/jscj-2n7002-c8545.pdf` (J, Sep 2016 (as printed)) |
| Q3 Q4 Q5 Q6 Q7 Q8 Q9 | 2N7002 | `Package_TO_SOT_SMD:SOT-23` | C8545 | logic-nfet-2n7002 | `v2/vendor/power/jscj-2n7002-c8545.pdf` (J, Sep 2016 (as printed)) |
| U15 | TLV75801PDRVR adjustable LDO, PA gate bias VGG 4.48 V while  | `Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` | C2876308 | board-d-regulators-tlv758p | `v2/vendor/ti/ti-tlv758p.pdf` (Rev. D, April 2018, revised October 2023) |
| U17 | TLV75801PDBVR adjustable LDO, +3V4_HUB 3.44 V for the hub (1 | `Package_TO_SOT_SMD:SOT-23-5` | C2877852 | board-d-regulators-tlv758p | `v2/vendor/ti/ti-tlv758p.pdf` (Rev. D, April 2018, revised October 2023) |
| U4 | TUSB2046IBVFR four-port USB 2.0 full-speed hub (TI, LQFP-32  | `Package_QFP:LQFP-32_7x7mm_P0.8mm` | C702369 | board-d-usb-hub | `v2/vendor/ti/ti-tusb2046b.pdf` (Rev. L, February 2000, revised June 2017); `v2/vendor/ti/ti-tusb2046b-slls413l-addendum-2025.pdf` (Rev. L, February 2000, revised June 2017) |
| U5 | USBLC6-2SC6 | `Package_TO_SOT_SMD:SOT-23-6` | C7519 | usb-esd-array | `v2/vendor/st/st-usblc6-2-esd-protection.pdf` (Rev 7, December 2021) |

**Lines with no LCSC code, joined to the entry that covers them.** No order code fixes the maker of such a line, so the entry's identity verdict speaks for the part it names, not for a purchase; the entry says what the line's order code is, or that it is not pinned.

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Joined by | Documents |
|---|---|---|---|---|---|---|
| U2 | NiceRF SA868 VHF 2 W exciter, bench-fitted (castellated; VBA | `meshsat:NiceRF_SA868` | none | vhf-exciter | where gen_sch_d.py:265 at 1f614233 (names U2) | `v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf` (V1.3) |

Every entry of SOURCES.yaml that names board D (and is on this revision's generators) joined at least one BOM line here (9 entries).

Entries that name board D for a part placed on no schematic (by their own `placed_part: false`), so they join no BOM line by design: `vhf-pa`.

## Cross-board and harness contracts that touch this board

The revision's own `check_contracts.py`, run in this packet's work copy (never in the repository), traced so each contract carries the boards it names: 11 name board D: **11 PASS, 0 FAIL, 0 UNJUDGED**.
- Board A was regenerated from its generator at the source revision in the work copy, because its committed netlist predates the widened generator identity: gen_sch exit 0, build_sch exit 0, regenerated netlist against the committed one: **PARITY_AFTER_NOISE**. Board A's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it).
- Board B was regenerated from its generator at the source revision in the work copy, because its committed netlist predates the widened generator identity: gen_sch exit 0, build_sch exit 0, regenerated netlist against the committed one: **PARITY_AFTER_NOISE**. Board B's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it).

| Result | Contract | Boards | Where |
|---|---|---|---|
| PASS | transmit inhibit present on D (J_HARN1) | D | `check_contracts.py:213` |
| PASS | D: TX_INHIBIT_n reaches the KEY gate U12 (D8: KEY = PTT_ANY AND TX_INHIBIT_n) | D | `check_contracts.py:226` |
| PASS | D: nothing but the harness, its pull-down, a test point and the KEY gate touches TX_INHIBIT_n | D | `check_contracts.py:227` |
| PASS | J_MEZZ1 (A) and J_HARN1 (D) 2x8 maps identical | A, D | `check_contracts.py:283` |
| PASS | D8 USB pair USB_D8_P: B16 J_AB1 -> A22 J_AB1/J_MEZZ1 -> D8 J_HARN1 | A, B, D | `check_contracts.py:288` |
| PASS | D8 USB pair USB_D8_N: B16 J_AB1 -> A22 J_AB1/J_MEZZ1 -> D8 J_HARN1 | A, B, D | `check_contracts.py:288` |
| PASS | +3V3 on D J_HARN1 | D | `check_contracts.py:295` |
| PASS | D8: TX_INHIBIT_n from J_HARN1 into the KEY gate | D | `check_contracts.py:300` |
| PASS | D: TX_INHIBIT_n is pulled DOWN on this board, so a missing panel inhibits | D | `check_contracts.py:351` |
| PASS | rail +3V3: the shares sum to 3.0% within the 3.0% the rail declares | A, C, D | `check_contracts.py:448` |
| PASS | rail +5V_D8: the shares sum to 6.0% within the 6.0% the rail declares | A, D | `check_contracts.py:448` |

## Interfaces declared for this board (`tools/pcb_interfaces.yaml`)

- **USB_FULL_SPEED**: USB 1.1 and 2.0 FULL speed, 12 Mb/s, between parts on one board. Impedance not stated (tolerance not stated), intra-pair not stated, maximum length not stated. Nets here: HUB_DM0, HUB_DM1, HUB_DM2, HUB_DM3, HUB_DM4, HUB_DP0, HUB_DP1, HUB_DP2, HUB_DP3, HUB_DP4, HUB_FB, HUB_OVRCUR_n .... Source: TI TUSB2046B datasheet, features, first page (`v2/vendor/ti/ti-tusb2046b.pdf`); TI PCM2912A datasheet, features (`v2/vendor/ti/ti-pcm2912a.pdf`).

## Holds and open decisions

- Hold on this board: decision 31, board D's exposed-port protection: BLOCKED_DECISION_31, NOT_READY, HELD.
- Open decision 42: a decoupling capacitor cannot be both within 3 mm of a fine-pitch pin and outside that part's escape fan (boards: not declared; the text names them).

## Not in this packet

- A layout. The board file of the declared phase is not included and nothing here judges it; whether it carries this netlist is rule SCH-002's question.
- Change marks on the schematic sheets. The PDFs are plain exports of the committed schematic; what changed is marked in the change table above, by reference, with the generator lines that carry each finding ID.
- Calculations and fault-state diagrams. Where the review asks for them (battery protection, board P; the charger state sequence, board A) they are separate work items with their own owner; this packet carries the circuit they will be judged against.
- Physical evidence of any kind.
