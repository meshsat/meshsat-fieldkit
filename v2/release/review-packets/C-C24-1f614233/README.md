# Review packet: board C (pcb-c-display) at 1f614233

**UNBUILT PROTOTYPE DESIGN. No board of this set has been fabricated, assembled or tested; nothing in this packet is physical evidence. A review packet is a review input: it does NOT release this board to fabrication, layout or ordering, and it approves nothing.**

**READINESS OF THIS PACKET: QUARANTINED, NOT_FOR_FAB.** No file here is an order file; the two BOM files carry NOT_FOR_FAB in their names.

| | |
|---|---|
| Board | C, `v2/ecad/pcb-c-display-c8` |
| Source revision | `1f614233998c3087a53abfa977be134465ce9f47` (docs(review): the review of the 26 September progress report is recorded, to be executed item by item [MESHSAT-1357]), 2026-09-26T14:13:16+02:00 |
| Compared with | `82dd1e4dc44efabeee1164a995cda4e866610f3d` (fix(tests): the blocked-land fixture no longer overwrites the lcsc_fill evidence rules CMP-002 and SUP-001 read [MESHSAT-1357]) |
| Declared phase | C24, from `tools/boards/c.json`: the phase of the board's committed LAYOUT. The layout is not part of this packet and is not judged by it (rule SCH-002 decides whether it carries this netlist). The schematic's own title-block label is C24 |
| Complete | yes |
| Built | 2026-09-26T15:50:55Z with KiCad 9.0.9, tool sha256 `7913d0a57567d896` |
| Part sources read | a SOURCES.yaml supplied with --sources, identified by its sha256, sha256 `2b192f2bb8ded051` |

## What this packet is, and is not

- It is a review input for a qualified reviewer: the schematic of one board exactly as committed at the source revision, with what changed since the previous revision and why, the parts and their primary sources, and the interfaces it shares with other boards.
- It is NOT a release. No layout, fabrication, order or approval follows from it. Hardware state: unbuilt prototype design.
- It is desk material only: no bench measurement, EMC, thermal or environmental test exists for this board.
- The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 5) asked for it.

## Contents

| File | What | sha256 (first 16) |
|---|---|---|
| `bom/NOT_FOR_FAB-parts-identity.csv` | the part identity and footprint map, one row per BOM line (NOT_FOR_FAB: a review input, never an order file) | `0e82ec46166af38d` |
| `bom/NOT_FOR_FAB-pcb-c-display-bom.csv` | the BOM exported from the committed schematic (build_sch.sh's own fields and grouping), byte for byte as KiCad wrote it; NOT_FOR_FAB in its name because it is a review input, never an order file | `5168db7db2d508d0` |
| `bom/parts-identity.json` | machine-readable record, see README.md | `65f76b331bce4f70` |
| `bom/sources-coverage.json` | machine-readable record, see README.md | `52111aa1d2038506` |
| `changes/attribution-read-by-hand.yaml` | the reading of every changed reference by hand: IDs, the generator lines that carry them, the reason in words; the build checked every ID against its lines | `52570da3a6d22def` |
| `changes/changes.json` | machine-readable record, see README.md | `5c77c678e5f86734` |
| `changes/gen_sch_c.diff` | the generator diff between the two revisions | `d52db2230c9259f6` |
| `changes/prev-82dd1e4d-gen_sch_c.py` | the generator at the previous revision | `547ad39ae05128d0` |
| `changes/prev-82dd1e4d.net` | the committed netlist at the previous revision | `ba01b558b949d4f2` |
| `contracts/check_contracts.log` | the revision's check_contracts.py output in the packet's work copy | `6b3e2290bec66008` |
| `contracts/contracts.json` | machine-readable record, see README.md | `028b160fb9e79795` |
| `interfaces/interfaces.json` | machine-readable record, see README.md | `60e7879fd5a8fc41` |
| `native/boards-c.json` | the board declaration (declared phase, classes) | `f0d20727dd563eac` |
| `native/fp-lib-table` | the project's footprint library table | `9c2d14bd7a666d84` |
| `native/gen_sch_c.py` | the generator that writes the schematic: the design's source of truth, with the finding IDs in its comments | `5f1ce2dd66ed7d2d` |
| `native/meshsat.pretty/BackerScrew_M3_GND.kicad_mod` | project footprint used by this board | `e0b8f321b6539d37` |
| `native/meshsat.pretty/Hirose_FH34SRJ-24S.kicad_mod` | project footprint used by this board | `088c3893a6e7cd07` |
| `native/meshsat.pretty/LeadLands_1x02.kicad_mod` | project footprint used by this board | `1e3fa195a8f63a9c` |
| `native/meshsat.pretty/PanelJack_17mm.kicad_mod` | project footprint used by this board | `57e493be8fb2bbe2` |
| `native/meshsat.pretty/PanelSounder.kicad_mod` | project footprint used by this board | `b0cefe91582284d9` |
| `native/meshsat.pretty/PanelSwitch_16mm.kicad_mod` | project footprint used by this board | `d96bed5c02a78200` |
| `native/meshsat.pretty/PanelSwitch_19mm.kicad_mod` | project footprint used by this board | `9f90b2fa4904b3f3` |
| `native/meshsat.pretty/ToggleBody_DPDT.kicad_mod` | project footprint used by this board | `1bc556b1632dc3ca` |
| `native/meshsat.pretty/ToggleBody_SPDT.kicad_mod` | project footprint used by this board | `a8576aab37c32b12` |
| `native/meshsat.pretty/Vishay_VEML7700.kicad_mod` | project footprint used by this board | `fb8764f71ec401dc` |
| `native/netlist/pcb-c-display-intent.json` | the generator's intent file (rails, nodes, bypass declarations) | `5c8d991e3805016a` |
| `native/netlist/pcb-c-display.net` | the committed netlist (KiCad s-expression) the change report reads | `2834f0d8c4071d56` |
| `native/netlist/pcb-c-display.net.prov.json` | the netlist's provenance sidecar (generator identity, schematic sha) | `184a37704ba12825` |
| `native/pcb-c-display.kicad_pro` | its KiCad project file | `36ff707561384db0` |
| `native/pcb-c-display.kicad_sch` | the committed schematic at the source revision (KiCad 9 native) | `8591f93e40cff1b8` |
| `open/holds-and-decisions.json` | machine-readable record, see README.md | `861c4da9979fb6aa` |
| `schematic/pcb-c-display-erc.json` | KiCad ERC of the committed schematic, every severity; a report, not a verdict | `7049e926e4d6bc58` |
| `schematic/pcb-c-display-schematic-sheet.pdf` | the whole schematic as one sheet | `1eac42915af9b272` |
| `schematic/pcb-c-display-schematic.pdf` | the schematic, paged into A3 blocks by the revision's own sch_pages.py (what build_sch.sh publishes) | `a93b4cde25f7afe6` |

Verify: `python3 v2/ecad/tools/review_packet.py verify <this folder>` or `sha256sum -c SHA256SUMS` inside it. `MANIFEST.json` carries the full record.

## Schematic exports

- KiCad 9.0.9 exported the PDFs, BOM, ERC and netlist from the committed schematic.
- The exported netlist against the committed netlist: **PARITY_AFTER_NOISE** (regen_compare; PARITY_AFTER_NOISE means only the export's own path, date and tool differ).
- At the previous revision, the same comparison: **PARITY_AFTER_NOISE**, so both ends of the change report are schematic content.
- ERC, every severity, as a report and not a verdict (the project's gate `erc_gate.py` applies the board's allow list): warning:endpoint_off_grid 10, warning:lib_symbol_issues 266, warning:unconnected_wire_endpoint 24.
- kicad-cli printed "schematic has annotation errors" on the bom and netlist exports. KiCad does not say which symbol it means. A text reading of the committed schematic finds no repeated (reference, unit) and no unannotated reference among 266 symbol instances, so the cause is NOT ESTABLISHED; the exported netlist's parity above is what shows the export carries the committed circuit.

## Changes against `82dd1e4d`

Components 194 to 204, nets 144 to 146: 10 added, 0 removed, 10 changed. Generator lines added or changed: 83. Details per reference, with the generator lines and the comment each ID was read from, are in `changes/changes.json`.

**How each row was read.** Every changed reference was read by hand (`changes/attribution-read-by-hand.yaml`, the session (review stream PKT), 26 September 2026, from gen_sch_c.py at both revisions and the round-4 board C record): the IDs, the generator lines at `1f614233` that carry them, and the reason in words. The build refused the file unless every ID is written on its cited lines and every cited range is tied to the change (it names the reference or one of its nets, is the statement's own comment or its section header, or the row states the tie). The mechanical reading stays in `changes/changes.json` (`evidence.automatic`) beside each row, with `agrees` saying whether it matches; it differs on 9 of 20 rows, mostly because it credits every ID written in a part's own comment, including IDs cited there as context.

**Counts.** 20 changes: 9 carry a finding ID; 8 carry only an owner ruling, a decision or a rule ID; 3 carry no ID of any kind; 0 are UNVERIFIED_ATTRIBUTION. So **11 changes have no finding ID**. Finding IDs include the round records' own item IDs (R4D-1, R4E-02, RP-17), which are the session's records of that round.

| Ref | Kind | What changed | Finding IDs | Rulings and decisions | Rules | Status | Read | Generator lines (cited) |
|---|---|---|---|---|---|---|---|---|
| C20 | CHANGED | pin 1: ZEROIZE_HW -> ZEROIZE_SW | W3-F12 | D-03.2, D-03.3 |  | TRACED | hand | gen_sch_c.py 168-174 |
| C31 | CHANGED | value: 1u 25V -> 4.7u 25V; lcsc:  -> C90057 | none |  |  | NO_ID_OF_ANY_KIND | hand | gen_sch_c.py 261-263 |
| C39 | ADDED | 100n, Capacitor_SMD:C_0603_1608Metric, C14663 | W3-F12 | D-03.2, D-03.3 |  | TRACED | hand | gen_sch_c.py 168-173, 354 |
| D19 | CHANGED | lcsc:  -> C268712; pin 1: EPD_SW -> EPD_VGH; pin 2: EPD_VGH -> EPD_SW | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_c.py 252 |
| D20 | CHANGED | lcsc:  -> C268712; pin 1: EPD_PUMP -> GND; pin 2: GND -> EPD_PUMP | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_c.py 252-257 |
| D21 | CHANGED | lcsc:  -> C268712; pin 1: EPD_VGL -> EPD_PUMP; pin 2: EPD_PUMP -> EPD_VGL | A03, F-IN-01, S-09 |  |  | TRACED | hand | gen_sch_c.py 252-257 |
| Q6 | CHANGED | value: Si2302CDS-T1-GE3 logic-level N-FET (Vishay, SOT-23, G S D li -> Si2300DS-T1-GE3 N-FET (Vishay, SOT-23, G S D like the 2N7002; lcsc: C10488 -> C72271 | none |  |  | NO_ID_OF_ANY_KIND | hand | gen_sch_c.py 245-249 |
| R10 | CHANGED | pin 1: ZEROIZE_HW -> ZEROIZE_SW | W3-F12 | D-03.2, D-03.3 |  | TRACED | hand | gen_sch_c.py 168-174 |
| SW_ZERO | CHANGED | value: ZEROIZE locking toggle, maintained (APEM 5636ADKB-2V, hinged -> ZEROIZE locking toggle, maintained (APEM 5636ADKB-2V, single; pin 1: ZEROIZE_HW -> ZEROIZE_SW | W3-F12, W5-ZEROIZE-4 | D-03.1, D-03.2, D-03.3 |  | TRACED | hand | gen_sch_c.py 212, 168-175 |
| TP41 | ADDED | ZEROIZE_SW, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP42 | ADDED | SDA, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP43 | ADDED | SCL, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP44 | ADDED | SOS_SW, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP45 | ADDED | TEST_SW, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP46 | ADDED | TR_APRS, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP47 | ADDED | C_DVDD, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| TP48 | ADDED | BOOT_J, TestPoint:TestPoint_Pad_D1.5mm, no LCSC code | none |  | TST-001 | TRACED | hand | gen_sch_c.py 306 |
| U3 | CHANGED | pin 34: ZEROIZE_HW -> ZEROIZE_SW | W3-F12 | D-03.2, D-03.3, decision 30 |  | TRACED | hand | gen_sch_c.py 111, 123, 168-175 |
| U9 | CHANGED | value: 74LVC1G34 non-inverting buffer (2 A 4 Y): EMCON_HW follows T -> 74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC; lcsc:  -> C151394 | none |  |  | NO_ID_OF_ANY_KIND | hand | gen_sch_c.py 157-165 |
| U12 | ADDED | 74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC1G17W5-7, SOT-25: 2 , Package_TO_SOT_SMD:SOT-23-5, C151394 | W3-F12 | D-03.2, D-03.3 |  | TRACED | hand | gen_sch_c.py 168-176 |

**The 11 changes with no finding ID, and their reason**

- C31 (no ID of any kind; round record: round-4 board C record, section 1 item 2: found while proving item 1 (S-09 / A03 / F-IN-01) against the same PDi figure; the record gives it no finding ID of its own): the pump capacitor goes from 1 uF to 4.7 uF 25 V because PDi's EPD driving-circuit note Rev.02 draws 4.7 uF there (page 3) and lists it in its BOM (page 10, item 2)
- Q6 (no ID of any kind; round record: round-4 board C record, section 1 item 3: found while proving item 1; no finding ID of its own): the boost FET changes from the 20 V Si2302CDS to the 30 V Si2300DS that PDi names, to meet PDi's drain criterion (Rev.02 page 4 note 1: VDDS 30 V)
- TP41 (ruling, decision or rule only: TST-001): test access owed before placement: ZEROIZE_SW (W5 test-access list, section 3), appended after TP40 so nothing is renumbered
- TP42 (ruling, decision or rule only: TST-001): test access owed before placement: SDA
- TP43 (ruling, decision or rule only: TST-001): test access owed before placement: SCL
- TP44 (ruling, decision or rule only: TST-001): test access owed before placement: SOS_SW
- TP45 (ruling, decision or rule only: TST-001): test access owed before placement: TEST_SW
- TP46 (ruling, decision or rule only: TST-001): test access owed before placement: TR_APRS
- TP47 (ruling, decision or rule only: TST-001): test access owed before placement: C_DVDD, the RP2040 core
- TP48 (ruling, decision or rule only: TST-001): test access owed before placement: BOOT_J, the BOOTSEL node through R5's 1k
- U9 (no ID of any kind; round record: round-4 board C record, section 1 item 6: found while doing item 5 (D-03.2 and D-03.3 conformance, W3-F12); no finding ID of its own): the EMCON buffer becomes a Schmitt-input 74LVC1G17, because TX_INHIBIT_n rises with a 77 us time constant against the 74LVC1G34's 10 ns/V input-transition limit

IDs found only on unchanged lines are listed in `changes/changes.json` as `context` and never counted as the change's. The generator diff is `changes/gen_sch_c.diff`.

## Part identity and footprints

127 BOM lines. 9 carry an entry in `v2/vendor/SOURCES.yaml` (identity, grade and the held documents with revision and sha256): 9 joined by the exact LCSC code of the line, and 0 lines that carry NO LCSC code, joined because the entry names this board and either its `where`, read at the revision its line number was written against, points at the line's defining statement while naming the reference or the part, or its fitted order code is written in the line's value. The other 118 lines carry no entry. SOURCES.yaml's own header says which parts it covers (its criteria (a) to (c)) and its `owed` list names the entries still owed; this packet does not judge criticality. `jlc_certified_row` is the certification table's row where it has one: that table was cut from older deliverables and a CERTIFIED there is not proof of identity (SOURCES.yaml header). Full map: `bom/NOT_FOR_FAB-parts-identity.csv` and `bom/parts-identity.json`; which entries name this board and what each joined: `bom/sources-coverage.json`.

**Joined by the line's LCSC code**

| Refs | Value | Footprint | LCSC | SOURCES.yaml | Documents |
|---|---|---|---|---|---|
| D19 | SS2040FL: EPD_SW -> VGH | `Diode_SMD:D_SOD-123F` | C268712 | epd-rectifiers | `v2/vendor/power/panjit-ss2020fl-series.pdf` (SS2020FL_SERIES-REV.10S, August 17, 2017) |
| D20 | SS2040FL: pump clamp | `Diode_SMD:D_SOD-123F` | C268712 | epd-rectifiers | `v2/vendor/power/panjit-ss2020fl-series.pdf` (SS2020FL_SERIES-REV.10S, August 17, 2017) |
| D21 | SS2040FL: pump -> VGL | `Diode_SMD:D_SOD-123F` | C268712 | epd-rectifiers | `v2/vendor/power/panjit-ss2020fl-series.pdf` (SS2020FL_SERIES-REV.10S, August 17, 2017) |
| Q2 Q3 Q4 | 2N7002 | `Package_TO_SOT_SMD:SOT-23` | C8545 | logic-nfet-2n7002 | `v2/vendor/power/jscj-2n7002-c8545.pdf` (J, Sep 2016 (as printed)) |
| Q6 | Si2300DS-T1-GE3 N-FET (Vishay, SOT-23, G S D like the 2N7002 | `Package_TO_SOT_SMD:SOT-23` | C72271 | epd-boost-fet | `v2/vendor/vishay/vishay-si2300ds.pdf` (S10-0111-Rev. A, 18-Jan-10) |
| U6 U7 U8 U10 U11 | USBLC6-2SC6 | `Package_TO_SOT_SMD:SOT-23-6` | C7519 | usb-esd-array | `v2/vendor/st/st-usblc6-2-esd-protection.pdf` (Rev 7, December 2021) |
| U12 | 74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC | `Package_TO_SOT_SMD:SOT-23-5` | C151394 | panel-schmitt-buffers | `v2/vendor/diodes/diodes-74lvc1g17.pdf` (Rev. 8-2 (pages 2 onward); page 1's foot) |
| U3 | RP2040 panel controller (USB device on B16's slot-1 hub, the | `Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm` | C2040 | rp2040 | `v2/vendor/rp2040/rpi-rp2040-datasheet.pdf` (build-date 2025-02-20, build-version 318); `v2/vendor/rp2040/rpi-rp2040-hardware-design.pdf` (not read; PDF ModDate 2026-08-20) |
| U9 | 74LVC1G17 Schmitt-trigger non-inverting buffer (Diodes 74LVC | `Package_TO_SOT_SMD:SOT-23-5` | C151394 | panel-schmitt-buffers | `v2/vendor/diodes/diodes-74lvc1g17.pdf` (Rev. 8-2 (pages 2 onward); page 1's foot) |

Every entry of SOURCES.yaml that names board C (and is on this revision's generators) joined at least one BOM line here (6 entries).

## Cross-board and harness contracts that touch this board

The revision's own `check_contracts.py`, run in this packet's work copy (never in the repository), traced so each contract carries the boards it names: 7 name board C: **7 PASS, 0 FAIL, 0 UNJUDGED**.
- Board A was regenerated from its generator at the source revision in the work copy, because its committed netlist predates the widened generator identity: gen_sch exit 0, build_sch exit 0, regenerated netlist against the committed one: **PARITY_AFTER_NOISE**. Board A's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it).
- Board B was regenerated from its generator at the source revision in the work copy, because its committed netlist predates the widened generator identity: gen_sch exit 0, build_sch exit 0, regenerated netlist against the committed one: **PARITY_AFTER_NOISE**. Board B's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it).

| Result | Contract | Boards | Where |
|---|---|---|---|
| PASS | J_PANEL 2x13 map identical on B and C | B, C | `check_contracts.py:207` |
| PASS | transmit inhibit present on C (SW_EMCON) | C | `check_contracts.py:213` |
| PASS | panel controller USB pair USB_PNL_P on B16 and C7 J_PANEL | B, C | `check_contracts.py:297` |
| PASS | panel controller USB pair USB_PNL_N on B16 and C7 J_PANEL | B, C | `check_contracts.py:297` |
| PASS | C7: SW_EMCON drives TX_INHIBIT_n, EMCON_HW leaves on J_PANEL | C | `check_contracts.py:299` |
| PASS | C7: U9 buffers TX_INHIBIT_n into EMCON_HW rather than inverting it | C | `check_contracts.py:355` |
| PASS | rail +3V3: the shares sum to 3.0% within the 3.0% the rail declares | A, C, D | `check_contracts.py:448` |

## Interfaces declared for this board (`tools/pcb_interfaces.yaml`)

- **USB_FULL_SPEED**: USB 1.1 and 2.0 FULL speed, 12 Mb/s, between parts on one board. Impedance not stated (tolerance not stated), intra-pair not stated, maximum length not stated. Nets here: USB_DM_R, USB_DP_R, USB_PNL_N, USB_PNL_P. Source: TI TUSB2046B datasheet, features, first page (`v2/vendor/ti/ti-tusb2046b.pdf`); TI PCM2912A datasheet, features (`v2/vendor/ti/ti-pcm2912a.pdf`).

## Holds and open decisions

- No hold in `tools/pcb_board_holds.yaml` names this board.
- Open decision 42: a decoupling capacitor cannot be both within 3 mm of a fine-pitch pin and outside that part's escape fan (boards: not declared; the text names them).

## Not in this packet

- A layout. The board file of the declared phase is not included and nothing here judges it; whether it carries this netlist is rule SCH-002's question.
- Change marks on the schematic sheets. The PDFs are plain exports of the committed schematic; what changed is marked in the change table above, by reference, with the generator lines that carry each finding ID.
- Calculations and fault-state diagrams. Where the review asks for them (battery protection, board P; the charger state sequence, board A) they are separate work items with their own owner; this packet carries the circuit they will be judged against.
- Physical evidence of any kind.
