#!/usr/bin/env python3
"""Stream w4b (MESHSAT-1357, 27 September 2026): DRAFTS for the owners of v2/docs/feasibility/EMCON.md, v2/docs/ARCHITECTURE.md,
v2/docs/PANEL.md and v2/ecad/tools/pcb_interfaces.yaml, to be applied by the integrator in the tree board B's w4b files are
committed in. The stream owns gen_sch_b.py, tools/boards/b.json and board B's regenerated schematic-phase files only, so every
page change it needs is here. Each edit asserts the text it replaces exactly once, and the whole run is refused when any anchor
is missing. Usage: page_drafts_w4b.py <repo root> [--check]

What each page gains (record: v2/docs/records/w4b/w4b-decisions.md once filed; drafts/w4b/w4b-decisions.md until then):
  EMCON.md       section 4c (new, before section 5): the RockBLOCK's ENABLE (W4B-D1), L4 case (2) on the supply enables
                 (W4B-D2), fault F2 on the card rails (W4B-D3), the L2 figure with the new readers, and RF-002's walk with and
                 without the tool rows drafted for the tools author; a bullet in section 0; section 0a's rows 4 to 7, 14 to
                 17; section 7's L4 and RockBLOCK rows; section 8's board B and tools hand-offs.
  ARCHITECTURE   section 6.3's rows 4 to 7, 14 and 17; section 13.4's SD-EMC-1 row and three finding rows W4B-D1 to D3.
  PANEL.md       section 6's EMCON_HW row (the card supplies' enables, the three dividers, U536) and correction (17).
  pcb_interfaces IF-B-LIME and IF-B-RB9704: the enable nets and the RockBLOCK's ENABLE as generated.
Prototype framing throughout: nothing is built; every statement is a desk reading of the regenerated netlist or of a maker's
document."""
import os, sys

EMCON = "v2/docs/feasibility/EMCON.md"
ARCH = "v2/docs/ARCHITECTURE.md"
PANEL = "v2/docs/PANEL.md"
IFC = "v2/ecad/tools/pcb_interfaces.yaml"

SEC_4C = """## 4c. Stream w4b, board B: the RockBLOCK's ENABLE, L4 case (2) on the supply enables, the card rails on each slot's own 5 V, and RF-002's walk

Drawn in `gen_sch_b.py` by stream w4b (27 September 2026, MESHSAT-1357, on main `91894cd7`) and regenerated on the KiCad box
with main's chain: main's own generator reproduces main's committed board B files (schematic PARITY; netlist, intent,
provenance and ERC PARITY_AFTER_NOISE; BOM PARITY), and the candidate's netlist differs from main's only by the stream's
per-decision list, read by the integration's own comparator (`v2/docs/records/r8b/integration/indep_cmp.py`): 13 parts added,
3 removed, 6 changed, 7 nets added and 19 changed, 0 unexplained, and the comparator refuses when any decision's entries are
dropped. A desk reading on board B only; no row has been shown on a bench. Each change is taken by the session under the
owner's standing rule of 26 September 2026 (record `v2/docs/records/w4b/w4b-decisions.md`). For board B this section
supersedes the RockBLOCK, L4 and card-rail statements of sections 0 to 4b and 7 to 8 where they differ.

| Item | Board B as drawn by stream w4b | State on B |
|---|---|---|
| Row 4, the RockBLOCK's ENABLE (W4B-D1) | `RB_IEN` (J_RB9704 pin 3, the module's I_EN) is the output of U536, an SN74LVC1G08 on +3V3_DEV: `EMCON_HW AND RB_SW_IEN`, where `RB_SW_IEN` is U6 pin 19's request, held low at power-on by R528 (4.7 k against the expander's 100 uA pull-up, 0.47 V). R527 (10 k) holds `RB_IEN` low with U536 unpowered (Ioff 10 uA, 0.10 V; the maker's 176 kOhm alone would let it reach about 1.8 V). The maker, Ground Control: I_EN "is used to initiate startup and shutdown of the 9704 module", with "a weak voltage-divider (270KOhm/430KOhm) pull-up to the input voltage" and "a series 10KOhm resistor", and "can be driven directly with an MCU pin, or an open-drain output" (hardware page, fetched 27 September 2026; schematic rev 2B page 3). EMCON asserted: the module's buffer input sits at about 0.28 V with V_IN_ORED at its 5.3 V maximum, and +5V_RB is removed at the same instant (U503) | ENABLE CLOSED at desk: no firmware, the expander's or the panel's, can keep the module enabled on its supercapacitors under EMCON. The row stays OPEN locally: what the Iridium 9704 does when ENABLE falls, and how long its shutdown on its own capacitors lasts, is in no held document, so row 4's 1 s L_max is TBD (bench E-04); Ground Control's warning ("once I_EN has been driven high, the host application must wait for I_BTD to transition high before driving I_EN low again ... Failure to follow this procedure may result in damage to the 9704 module") is met by an EMCON during the module's boot, the edge the maker's own divider makes on every loss of external power, which EMCON also causes at that instant: accepted as a stated residual, as the 5G module's flash warning is; U536's own 0 to 1.65 V band is L4 case (2), with +5V_RB off there (next row) |
| L4 case (2) on U501 to U504 (W4B-D2) | the enables of U23 and U24 (TPS259631) and U21 (TPS22810) sit at 0.6 of their gate's output: R529 to R531, 10 k 1 percent in series, and R514 to R516, 15 k 1 percent to GND, on the nodes `LIME_UVLO`, `RB_UVLO` and `E22_UVLO` (board A's SD-A8-3 remedy, the same values and codes). A gate at most at its own 1.65 V band edge puts at most 0.998 V on the pin, under VUVLO(F) and VENF, 1.08 V minimum (SLVSET8A 7.5, SLVSDH0C 7.5); powered and high, at least 1.43 V (VOH 2.4 V at 16 mA, SCES217AA 5.5), over VUVLO(R) 1.22 V and VENR 1.30 V maximum; unpowered, 0.15 V (Ioff 10 uA into 15.15 k), under VSD 0.53 V and VSHUTF 0.5 V. U505 needs none: U22's input is +3V3_DEV itself (4.15) | CLOSED at desk on U501 to U504 (bench E-11 records it); not applicable to U505 |
| Fault F2 on the card rails (W4B-D3) | each slot's card buck enable `S{s}A_EN` is driven push-pull by U{s}16, an SN74LV1T08 (TI SCLS739F) run from +5V_S{s}, the buck's own input: `EMCON_HW AND PCIE_PWR_EN{s}`. R{s}64 is removed, and U{s}15's second channel is freed (2A on GND). Found when RF-002's walk, given the SN74LVC2G06's row, read the old node: with +3V3_CM{s} down and +5V_S{s} up, only R{s}06 and R{s}64 (110 k) held `S{s}A_EN` against the AP64500's own EN sources ("an internal 1.5uA pullup current source" and, once on, "a 4uA hysteresis pullup current source"; 5.5 uA typical with no maximum at VEN 1.5 V, DS41979), so a buck that was on when its module's 3.3 V fell could stay on beyond EMCON's reach, on slot 2 the RM520N-GL with its own firmware. Now the gate is powered whenever the buck has an input; EMCON asserted, its output is at most 0.1 V at 20 uA and 0.35 V at 8 mA (SCLS739F 6.5) with no resistor for the EN current to lift; its VIL is 0.8 V at VCC 4.5 to 5.5 V and its inputs are 5.5 V tolerant with II +-1 uA at VCC 0 to 5.5 V; in its unspecified band the buck's input is under its 3.5 V UVLO | CLOSED at desk for rows 5 to 7 in fault F2; one gate added to the latency (tpd 7.0 ns maximum at VCC 5 V and 30 pF, SCLS739F 6.6) |
| L2 with the new readers | `EMCON_HW`'s readers on B are now U501, U503 to U506 and U536 (Ioff 10 uA), U112, U212, U312 (Ioff 10 uA) and U116, U216, U316 (II 1 uA at VCC 0 to 5.5 V). RF-002's walk, with the rows drafted for the tools author, bounds the line at 0.58 V in its worst fail-safe state (0.50 V on main), under the 0.8 V VIL | CLOSED at desk (the walk's bound) |
| RF-002's walk | main's `tx_inhibit.py` holds no row for the SN74LVC2G06 or the SN74LV1T08, and its re-take in scratch reads `inhibit_chain_b` FAIL 11, PASS 3, UNDECIDED 6 on the candidate (FAIL 11, PASS 6, UNDECIDED 3 on main); `inhibit_chain_a` and `_c` move by one PASS to UNDECIDED each, on the line's new readers. With the rows drafted for the tools author (`drafts/w4b/tools/apply_tx_inhibit_w4b.py` and its test changes: the two logic rows, the AO3400A read as an N-channel FET, U221 and J_QMX in ACCESSORIES, and a VCC-band field for the LV1T08's VIL) it reads FAIL 1, PASS 15, UNDECIDED 4, and boards A and C as on main. The FAIL is `TX_INHIBIT_n`'s fail-safe state (W3T-F1, EQ-25, board C). UNDECIDED: the LimeSDR (the USBLC6-2's VBUS on `+5V_LIME` with its I/O on the hub's pins), both E72 (the cJTAG headers on `+3V3_ZB`, the other module's supply pin, the CP2102N's RTS and DTR behind R28 to R31) and the RM520N-GL (U221, the TPS3808 powered from the socket rail it watches, a part in no class of the walk). The six CM5 radios, both AW7915 cards, the RockBLOCK's supply and the E22 read PASS, and board B's census PASS | the rows: the tools author's; the three back-feed items: SD-EMC-2's |

**What stays open on B after stream w4b.** SD-EMC-2's back-feed into the RockBLOCK (`RB_RXD`, `RB_CTRL`, and R41 and R42's
pull-ups on the module's outputs `RB_STATUS` and `RB_XMTG`), the E22 and both E72 (their lines' series resistance, which needs
each interface's edge budget); the Iridium 9704's response to ENABLE (a maker's document owed); U536's own L4 band; Q212's
conduction over temperature; and every row's bench test.

"""


def edits():
    E = []
    E.append((EMCON, "  RF-002's walk does not model the SN74LVC2G06 yet and reads board B FAIL on that gap (section 4b).\n",
              "  RF-002's walk does not model the SN74LVC2G06 yet and reads board B FAIL on that gap (section 4b).\n"
              "- **Stream w4b, board B (section 4c, 27 September 2026).** The RockBLOCK's ENABLE is forced low by hardware (U536,\n"
              "  `EMCON_HW AND` the expander's request, R527 holding it low unpowered), so no firmware can keep the module enabled on\n"
              "  its own supercapacitors under EMCON; L4 case (2) is closed at desk on U501 to U504 by 10 k over 15 k dividers on the\n"
              "  switches' enables; and each card buck's enable is driven by an SN74LV1T08 on its slot's own 5 V (U116, U216, U316),\n"
              "  which closes a fault F2 hole the walk found once it read the SN74LVC2G06. With the rows drafted for the tools author\n"
              "  RF-002's walk reads board B FAIL 1 (`TX_INHIBIT_n`, W3T-F1), PASS 15, UNDECIDED 4 (section 4c).\n"))
    E.append((EMCON, "| 4 | RockBLOCK 9704 | **OPEN since this revision**: the supply gate is drawn, but the module runs on its own supercapacitors with ENABLE held by U6 (4.4) | OPEN | the local item; back-feed (SD-EMC-2); L4 on U503 (L1 to L3 closed at desk on B in round 8, 4b); SD-EMC-6 |",
              "| 4 | RockBLOCK 9704 | **OPEN**: the supply gate is drawn and, since stream w4b, its ENABLE is forced low by hardware (U536, 4c); the module keeps its own supercapacitors, and what it does when ENABLE falls is unpublished (4.4, 4c) | OPEN | the local item; back-feed (SD-EMC-2); L4 on U503 closed at desk by its enable divider, U536's own band open (4c); SD-EMC-6 (L1 to L3 closed at desk on B in round 8, 4b) |"))
    E.append((EMCON, "Q212's 25 C-only rows and the flash warning its named residuals | OPEN |",
              "Q212's 25 C-only rows and the flash warning its named residuals; fault F2 (its module's 3.3 V down with the buck on) closed at desk by U216 since stream w4b (4c) | OPEN |"))
    E.append((EMCON, "| 6, 7 | AW7915-AED x2 | CLOSED (4.6) | OPEN |",
              "| 6, 7 | AW7915-AED x2 | CLOSED (4.6); fault F2 closed at desk by U116 and U316 since stream w4b (4c) | OPEN |"))
    E.append((EMCON, "| 14 | E22-900M30S LoRa | CLOSED (4.14) | OPEN | L4 on U504; back-feed (SD-EMC-2); SD-EMC-6 (L1 to L3 closed at desk on B in round 8, 4b) |",
              "| 14 | E22-900M30S LoRa | CLOSED (4.14) | OPEN | back-feed (SD-EMC-2); SD-EMC-6 (L1 to L3 closed at desk on B in round 8, 4b; L4 on U504 closed at desk by its enable divider since stream w4b, 4c) |"))
    E.append((EMCON, "| 15, 16 | E72 CC2652P x2 | CLOSED (4.15) | OPEN | L4 on U505; back-feed (SD-EMC-2); SD-EMC-6 (L1, L2 closed at desk on B in round 8, 4b) |",
              "| 15, 16 | E72 CC2652P x2 | CLOSED (4.15) | OPEN | back-feed (SD-EMC-2); SD-EMC-6 (L1, L2 closed at desk on B in round 8, 4b; L4 does not apply to U505, whose switch's input is the gate's own rail, 4.15 and 4c) |"))
    E.append((EMCON, "| 17 | LimeSDR Mini 2.4 | CLOSED (4.17) | OPEN | L4 on U501 and U502; SD-EMC-6 (L1 to L3 closed at desk on B in round 8, 4b) |",
              "| 17 | LimeSDR Mini 2.4 | CLOSED (4.17) | OPEN | SD-EMC-6 (L1 to L3 closed at desk on B in round 8, 4b; L4 on U501 and U502 closed at desk by the enable divider since stream w4b, 4c) |"))
    E.append((EMCON, "board B: case (1) gone in round 8, case (2) open on U501 to U505 (bench E-11; section 4b);",
              "board B: case (1) gone in round 8, case (2) closed at desk on U501 to U504 by stream w4b's enable dividers and not applicable to U505 (section 4c), open on U536 (the RockBLOCK's ENABLE gate, with +5V_RB off in its band) and INFERRED on U{s}12 to U{s}15 (bench E-11);"))
    E.append((EMCON, "| board B author (ENABLE forced low by hardware); the session (a lookup of the Iridium 9704 module's ENABLE behaviour); bench E-04 |",
              "| board B: ENABLE forced low by hardware, done at desk by stream w4b (U536, R527, R528; section 4c); the session: a lookup of the Iridium 9704 module's ENABLE behaviour, still owed (Ground Control's hardware page says only that I_EN initiates startup and shutdown); bench E-04 |"))
    E.append((EMCON, "Still owed on B: the RockBLOCK's ENABLE forced\n    low by hardware (4.4); SD-EMC-2's series resistance on the RockBLOCK, E22 and E72 lines; L4 case (2) on U501 to U505\n    (bench E-11);",
              "Still owed on B after stream w4b (section 4c, which drew the RockBLOCK's\n    ENABLE, L4 case (2) on U501 to U504 and the card bucks' enables on the slots' own 5 V): SD-EMC-2's series resistance on\n    the RockBLOCK, E22 and E72 lines; U536's own L4 band (bench E-11);"))
    E.append((EMCON, "Move `J_QMX` from OWED to ACCESSORIES, citing QRP Labs' schematics for PCB\n  Rev 1, 2, 3/4 and 5.\n",
              "Move `J_QMX` from OWED to ACCESSORIES, citing QRP Labs' schematics for PCB\n  Rev 1, 2, 3/4 and 5. Drafted by stream w4b (`drafts/w4b/tools/apply_tx_inhibit_w4b.py`, `apply_tx_inhibit_tests_w4b.py`),\n"
              "  with the SN74LV1T08's row (board B's U116, U216, U316) and a VCC-band VIL field; still the tools author's: a class for\n"
              "  the TPS3808 supervisor (U221), the USBLC6-2's VBUS beside a USB hub's pins, and the declared bench headers and\n"
              "  CP2102N pulls on `+3V3_ZB` (section 4c).\n"))
    E.append((EMCON, "## 5. Decisions taken by the session under the owner's standing rule of 26 September 2026\n",
              SEC_4C + "## 5. Decisions taken by the session under the owner's standing rule of 26 September 2026\n"))
    # ARCHITECTURE.md, section 6.3 and 13.4
    E.append((ARCH, "| 4 | RockBLOCK 9704 (B) | eFuse off | OPEN locally since `EMCON.md`'s sixth revision: the module runs on two 10 F supercapacitors of its own after the eFuse opens, with its ENABLE held by U6 alone (`EMCON.md` 4.4); back-feed (SD-EMC-2) |",
              "| 4 | RockBLOCK 9704 (B) | eFuse off, and since stream w4b (27 September 2026) its ENABLE held low by hardware (U536 = EMCON_HW AND the panel's request) | OPEN locally: the module runs on two 10 F supercapacitors of its own after the eFuse opens, and what it does when ENABLE falls is unpublished (`EMCON.md` 4.4, 4c); back-feed (SD-EMC-2) |"))
    E.append((ARCH, "supply removed at once by hardware (S2A_EN, FULL_CARD_POWER_OFF# and W_DISABLE1# low,",
              "supply removed at once by hardware (S2A_EN, driven since stream w4b by U216 from the slot's own 5 V, FULL_CARD_POWER_OFF# and W_DISABLE1# low,"))
    E.append((ARCH, "| 6, 7 | AW7915-AED cards, slots 1 and 3 (B) | card buck off (`458b2873`); W_DISABLE1# not counted | gate CLOSED at desk; back-feed OPEN |",
              "| 6, 7 | AW7915-AED cards, slots 1 and 3 (B) | card buck off (`458b2873`; since stream w4b its enable is driven from the slot's own 5 V by U116, U316); W_DISABLE1# not counted | gate CLOSED at desk, fault F2 included (`EMCON.md` 4c); back-feed OPEN |"))
    E.append((ARCH, "| 14 | E22-900M30S LoRa (B) | load switch off | OPEN: back-feed |",
              "| 14 | E22-900M30S LoRa (B) | load switch off (its enable at 0.6 of its gate since stream w4b, L4 case (2)) | OPEN: back-feed |"))
    E.append((ARCH, "| 17 | LimeSDR Mini 2.4 (B) | eFuse on its USB VBUS off | OPEN on the shared items |",
              "| 17 | LimeSDR Mini 2.4 (B) | eFuse on its USB VBUS off (its enable at 0.6 of its gate since stream w4b, L4 case (2)) | OPEN on the shared items |"))
    E.append((ARCH, "the bound's CINT term and the flash on bench E-12; RF-002's walk does not model the SN74LVC2G06 yet (tools) |",
              "the bound's CINT term and the flash on bench E-12; RF-002's walk does not model the SN74LVC2G06 yet (tools; the row drafted by stream w4b, `EMCON.md` 4c) |\n"
              "| W4B-D1 (`EMCON.md` 4c) | The RockBLOCK 9704's ENABLE was held by the expander alone, so under EMCON the module could run on its own supercapacitors | DRAWN at desk by stream w4b (27 September 2026): U536 = EMCON_HW AND the request, R527 holding it low unpowered; the 9704's response to ENABLE is a maker's document owed, bench E-04 |\n"
              "| W4B-D2 (`EMCON.md` 4c) | L4 case (2): U501 to U504 in their 0 to 1.65 V supply band could turn the LimeSDR's, the RockBLOCK's or the E22's switch on | CLOSED at desk by stream w4b: each enable at 0.6 of its gate (10 k over 15 k, 1 percent); bench E-11 |\n"
              "| W4B-D3 (`EMCON.md` 4c) | With a module's 3.3 V down and its slot's 5 V up, the card buck's enable was held only by 110 k against the AP64500's EN current, which has no stated maximum once on, so a card (slot 2's 5G module included) could stay powered beyond EMCON | CLOSED at desk by stream w4b: U116, U216, U316 (SN74LV1T08 on the slot's own 5 V) drive the enable |"))
    # PANEL.md, section 6's EMCON_HW row and a correction line
    E.append((PANEL, "each single gate `U501` to `U505` (SN74LVC1G08, which state Ioff) ANDs it into the supply enables of the LimeSDR, the RockBLOCK, the LoRa module and both E72;",
              "each single gate `U501` to `U505` (SN74LVC1G08, which state Ioff) ANDs it into the supply enables of the LimeSDR, the RockBLOCK, the LoRa module and both E72, the first three reaching their switches at 0.6 of the gate's output so a gate in its unspecified supply band cannot turn one on (stream w4b), and `U536` ANDs it into the RockBLOCK's own ENABLE (`RB_IEN`, its J3 pin 3), so no firmware holds the module enabled on its capacitors (stream w4b);"))
    E.append((PANEL, "and `U115`, `U215`, `U315` pull each card's `W_DISABLE1#` and its buck's enable low, so all three card supplies go, the 5G module's included;",
              "and `U115`, `U215`, `U315` pull each card's `W_DISABLE1#` low, while each card's supply enable is driven by `U116`, `U216`, `U316` (SN74LV1T08, `EMCON_HW` AND the module's `PCIE_PWR_EN`) from that slot's own 5 V, so all three card supplies go, the 5G module's included, whether or not the module's own 3.3 V is up (stream w4b);"))
    E.append((PANEL, "> supervisors answer at 0x34, 0x35 and 0x36, clear of the PoE controller's broadcast address (section 7: the open\n> finding of (13) is closed as a firmware contract).\n",
              "> supervisors answer at 0x34, 0x35 and 0x36, clear of the PoE controller's broadcast address (section 7: the open\n> finding of (13) is closed as a firmware contract).\n\n"
              "> **Corrections of 27 September 2026 (stream w4b, board B).** Nothing has been built. (17) The RockBLOCK's ENABLE is\n"
              "> `EMCON_HW` AND the panel's request (`U536`); the expander pin that drove it is a request now (`RB_SW_IEN`), which the\n"
              "> panel firmware writes low on EMCON and raises after a release only once `RB_STATUS` reads low, Ground Control's\n"
              "> I_EN/I_BTD order. The card supplies' enables are driven from each slot's own 5 V (`U116`, `U216`, `U316`), and the\n"
              "> LimeSDR's, the RockBLOCK's and the LoRa module's switch enables sit at 0.6 of their gates (section 6).\n"))
    # pcb_interfaces.yaml, IF-B-LIME and IF-B-RB9704
    E.append((IFC, "      power: \"LIME_EN = EMCON AND the hub's port power AND LIME_SW_EN (U19, gen_sch_b.py:975)\"",
              "      power: \"LIME_EN = EMCON AND the hub's port power AND LIME_SW_EN (U501 and U502 since round 8); the eFuse's EN/UVLO at 0.6 of it (LIME_UVLO, R529 over R514, stream w4b)\""))
    E.append((IFC, "off under EMCON (its only supply); R514 holds LIME_EN low\"",
              "off under EMCON (its only supply); R514 holds LIME_UVLO low (0.15 V with the gates unpowered, stream w4b)\""))
    E.append((IFC, "      levels: \"3.3 V logic on board B's side: RB_IEN and RB_CTRL from U6 (+3V3_DEV);",
              "      levels: \"3.3 V logic on board B's side: RB_IEN from U536 (EMCON_HW AND U6's request RB_SW_IEN, stream w4b) and RB_CTRL from U6 (+3V3_DEV);"))
    E.append((IFC, "      power: \"+5V_RB from eFuse U24, RB_EN = EMCON AND RB_SW_EN (U19); removed under EMCON (EMCON.md section 4, E-04)\"",
              "      power: \"+5V_RB from eFuse U24, RB_EN = EMCON AND RB_SW_EN (U503 since round 8), its EN/UVLO at 0.6 of it (RB_UVLO, stream w4b); removed under EMCON, with the module's ENABLE held low by U536 (EMCON.md section 4c, E-04)\""))
    E.append((IFC, "      back_power: \"RB_IEN and RB_CTRL from U6 and the UART from its bridge can drive into an unpowered module (W5-F13, EMCON.md SD-EMC-2):",
              "      back_power: \"RB_CTRL from U6 and the UART from its bridge can drive into an unpowered module (RB_IEN is held low by U536 under EMCON and by R527 with U536 unpowered, stream w4b) (W5-F13, EMCON.md SD-EMC-2):"))
    E.append((IFC, "      default_state: \"+5V_RB off (RB_EN held low by R515; RB_SW_EN by R51 4.7 k). RB_IEN and RB_CTRL have no pull on board B:\n"
                   "        until the panel configures U6 they are U6 inputs held HIGH by its internal 100 k pull-ups ('pulls the I/O to a default\n"
                   "        high when configured as an input and undriven', TI SCPS131J section 8, ti-pca9555.pdf), which is the SD-EMC-2 back-feed\n"
                   "        path into an unpowered module; FW-A08 writes U6's outputs low before its configuration\"",
              "      default_state: \"+5V_RB off (RB_UVLO held low by R515; RB_SW_EN by R51 4.7 k). RB_IEN is held low by U536's AND and by\n"
              "        R527 10 k with U536 unpowered, and U6's request RB_SW_IEN by R528 4.7 k (stream w4b). RB_CTRL has no pull on board B:\n"
              "        until the panel configures U6 it is a U6 input held HIGH by its internal 100 k pull-up ('pulls the I/O to a default\n"
              "        high when configured as an input and undriven', TI SCPS131J section 8, ti-pca9555.pdf), which is the SD-EMC-2 back-feed\n"
              "        path into an unpowered module; FW-A08 writes U6's outputs low before its configuration\""))
    return E


def main(a):
    if not a:
        print(__doc__); return 2
    root = a[0]; check = "--check" in a
    texts, bad = {}, []
    assert not [n for _p, _o, n in edits() if "\u2014" in n or "\u2013" in n], "an em or en dash in a drafted text"
    for path, old, new in edits():
        t = texts.get(path)
        if t is None: t = texts[path] = open(os.path.join(root, path), encoding="utf-8").read()
        n = t.count(old)
        if n != 1: bad.append((path, old[:80], n)); continue
        texts[path] = t.replace(old, new, 1)
    for b in bad: print("ANCHOR %s: found %d time(s): %r" % (b[0], b[2], b[1]))
    if bad:
        print("REFUSED: nothing written"); return 1
    for path, t in texts.items():
        if path.endswith(".yaml"):
            import yaml; yaml.safe_load(t)
        if not check: open(os.path.join(root, path), "w", encoding="utf-8").write(t)
        print("%s %s" % ("checked" if check else "wrote", path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
