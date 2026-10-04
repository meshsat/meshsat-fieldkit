#!/usr/bin/env python3
"""LAYER-STATUS.md brought to integration sets 28 and 29 (MESHSAT-1357, 4 October 2026; record int29).

Set 28 proposed rows for layers 5 to 8 and a new layer 12 (records/int28b/RESULT.md section 7) and did not apply them, because
this page is read by tests; set 29 applies them, updated with set 29's merged records: layer 9 items 9.1 and 9.2 from
records/l9pwr's README, 9.12 from records/l9stk's README, 9.3 from records/l9stk section 15; layers 4 and 8 with set 29's drafts
as DRAFTED and their defects OPEN (records l8r2 rounds 3 to 6, l8p, l9stk, l4e11 round 9, l4e7 round 6, l4e9 round 8); layer 5
item 5.11 with Layer 5's round 4 (records/l5r4); layer 12 item 12.1 with the panel firmware's round 4.

What it writes: one paragraph after the page's "At H3" paragraph, and in each of layers 4 to 9 a block headed "After set 29"
above the H2 table (the H2 table stays as it is: a row not listed in the new block keeps its H2 text), and a new section,
Layer 12, before Appendix A. Nothing else on the page changes; layer 3's section is not touched. No item is raised to MET
and no layer is credited as complete. Every anchor is asserted to occur exactly once; a second run is refused; no em or en
dash is written.

Usage: python3 apply_layer_status_set29.py [--check] [--page PATH]   (--page: a copy of the page)
Exit 0 written or checked; 2 refused (already applied, or an anchor not found once)."""
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
PAGE = os.path.join(TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "**After set 29 (4 October 2026, integration sets 28 and 29, MESHSAT-1357).**"

INTRO = (MARK + " Layers 4 to 9 each open with a table headed \"After set 29\": the items the records merged since H2 moved, "
         "each row naming its record (`v2/docs/records/<name>/`); a row not listed there keeps its H2 text in the table below "
         "it. A section \"Layer 12\" after Layer 9 holds the firmware, bring-up procedures, test plans and build "
         "documentation (the owner's instruction of 2 October 2026, `v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md`). No "
         "item is raised to MET by sets 28 and 29 and no layer from 4 on is COMPLETE: every circuit change named is a "
         "release-guarded DRAFT, not applied to any generator, and nothing has been built, bought or measured. The rows of "
         "sets 28 and 29 are composed from the merged records' own proposed rows (`v2/docs/records/int28b/RESULT.md` section 7, "
         "`v2/docs/records/l9pwr/README.md`, `v2/docs/records/l9stk/README.md`) and from the records named in each row "
         "(`v2/docs/records/int29/`).\n\n")

HEAD = "| Item | Acceptance item (short) | After set 29 | Evidence, or what remains |\n|---|---|---|---|\n"

L4 = ("**After set 29 (4 October 2026): IN_PROGRESS.** The connected power design is "
      "`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` (Layer 4 tasks L4-E1 to L4-E13 and their rounds; L4-E9 at round 8). "
      "The owner's three decisions stay apart (its section 6): the architecture candidate CONDITIONAL; the power-design "
      "closure gate BLOCKED; the fabrication release BLOCKED; the engineer handoff READY TO START, provisional. Status, in the "
      "owner's reviewer's words: \"Selected power-architecture candidate. Known design defects and qualification gaps remain "
      "open. Changes are drafts, not an implemented or qualified circuit. Power-design closure and fabrication release are "
      "blocked.\" No release check has judged this layer. The rows below are the items set 29's records move; every other "
      "item keeps its H2 row below, and where a row differs from a record it cites, the record governs.\n\n" + HEAD +
      "| 4.10 | rail and interconnect margins | PARTLY | Layer 9's budget on the drawn and the drafted trees (`records/l9pwr` "
      "round 2): every converter against its maker's rating or drafted limit. L9P-F02 (board A's slots 1 and 3 on the AP64500 "
      "over its 5 A with the coolers on the rail) corrected in drafts: slots 1 and 3 on slot 2's LM5176 stage with the "
      "coolers at full speed (`records/l8r2` rounds 4 to 6), CONDITIONAL on C4-1 to C4-6, the coordinator's closing check "
      "CLOSED AS CONDITIONAL (`records/l8r2/checks/check-l9pf02-coordinator.md`), OPEN in the register until the drafts are "
      "applied and C4-1 to C4-6 pass. OPEN: L9P-F01 (D-17, row 4.13 to 4.18), L9P-F03 (the device rail's LM5176 at 7.181 A "
      "drafted against 7.0957 A in PS-ALLTX at HIGH, 7.472 A at the least load voltage 4.9019 V; I-03), L9P-F04 to L9P-F06. "
      "The pack path's copper on boards A and E sized as a candidate (`records/l9stk` section 14), its outer weight the "
      "owner's open decision (L9STK CU). Not re-checked since H2: R17's rating, IF-AB-POWER's two ends, PWR-F02 |\n"
      "| 4.12 | trade decisions recorded | PARTLY | since H2, each Layer 4 record's decisions with their authority; the fans "
      "settled by D-18 (`records/l7pwr`). Set 29: slots 1 and 3 on the LM5176 rather than the AP64500 (`records/l8r2` "
      "section 1s); the pack breaker's latch-off LM5069-1 rather than the auto-retry -2 (`records/l9stk` section 15.4b); the "
      "third battery FET (`records/l9stk` section 15.5, Q42 in `records/l4e11` round 9); one stackup per board, written as "
      "seven session decisions in `records/l9stk/apply_decisions_l9stk.py` and not yet appended to `pcb_decisions.yaml`, with "
      "the outer copper weight of A and E open to the owner (L9STK CU). Open as at H2: board B's escape method (EQ-01), U8 "
      "(EQ-06), F2 (EQ-07) |\n"
      "| 4.13 to 4.18 | feasibility demonstrated; ZEROIZE, EMCON, failover, power and thermal, battery questions resolved | "
      "**OPEN** | power and battery: the closure gate BLOCKED (`records/l4e9`). Set 29, DRAFTED: W4DP-F2's firmware-independent "
      "element, an LM5069-1 latch-off breaker on board P with a make-last dock enable, an RC hold and the restart inhibit C-1c "
      "(`records/l9stk` section 15; its independent checks in `records/l9stk/checks/`, the last CONFIRMED AS CONDITIONAL at "
      "`0d72880b` with B-R2 left out), drawn as release-guarded drafts by `records/l8p`; the battery FETs' target restated as "
      "a junction limit with a third BUK6Y10-30P, Q42 (E11-29 CONDITIONAL on its specimen; E11-37 rebound to the three-device "
      "network, OPEN on Q-TI-17 or a bench with three); IF-1's VSYS hold U46, and DD-7's input-return reset and hardware "
      "charge inhibit (`records/l4e11` section 19). OPEN: B-R2 for a latch with a source present into a resistive fault; "
      "DD-3, the shore input, after one design-out attempt; DD-8's evidence (the inhibit's error budget allocated by "
      "part choice in `records/l8p` section 4, the NTC's tolerance at 80 C ASSUMED, E-12b and E-15 owed); D-17, the all-transmit floor, 16.214 V needed on the final drafts against REQ-018's 15.5 V "
      "pass line (L4-E9 round 8 withdrew round 7's raised floor; its one design-out attempt, the five fans' supplies off "
      "while the PA keys, CONDITIONAL on the 60 s fan-stop test R-213); B6-ENG-1 and B6-ENG-2, the solar guard and its sense "
      "(the engineer's). FEA-001 to FEA-007 otherwise as at H2 |\n\n")

L5 = ("**After set 29 (4 October 2026): IN_PROGRESS.** Layer 5's power pass (`records/l5pwr`), its rounds 2 and 3 "
      "(`records/l5r2`) and round 4 (`records/l5r4`) wrote Layer 4's power results, the pass-2 fields of every contract and "
      "the one slot-fault rule; no release check has judged this layer. The rows below are the items sets 28 and 29 moved; "
      "every other item (5.1, 5.3 MET with the same reading, 5.8, 5.14, 5.15) keeps its H2 row below.\n\n" + HEAD +
      "| 5.2 | every interface owned at both ends with its connector | PARTLY | all 31 contracts carry both ends with a part on "
      "every board end and every pass-2 field (`records/l5r2`; hc5's `check_contract_fields.py --all`); not MET: no census "
      "shows every interface of the netlists has a contract, and the generators write no MPN (EQ-21) |\n"
      "| 5.4 | electrical levels stated per interface | PARTLY | the power interfaces' levels with their Layer 4 basis and "
      "marks (`records/l5pwr`), the eight first-twelve contracts, the fans and the chassis bond (`records/l5r2`); the kit I2C "
      "bus's three segments owed (SC-59) |\n"
      "| 5.5 | power capacity of each power interface with margin | PARTLY | IF-EXT-DC, IF-AE-DOCK, the outlet and the PoE "
      "monitor (`records/l5pwr`); PANEL_5V per conductor (F1's trip band TBD), the mezzanine's +3V3, the PA lead at 60 "
      "percent, the MAIN lead's microamps, the fans' branch 1.3208 A at 89.8 percent, DRAFTED (`records/l5r2`); open: I-03's "
      "PS-ALLTX, E5's targets and the ground share (S-74, S-75), the ribbon and SMP-MAX ratings, the 813's pulse capability "
      "(E11-38; Layer 7's bound and drafted maker question) |\n"
      "| 5.6 | sequencing across interfaces | PARTLY (from OPEN) | L4-E9 section 4's sequencing fields, FW-E11, FW-A21, "
      "FW-A23, `power_line_states` (`records/l5pwr`); HOT-R1's line DRAWN on A and E since SC-70 (S-57 closed); the SLOT_EN "
      "hold DRAFTED on board A (`records/l8gnd`: U43, R230 to R232, C240, `apply_gen_sch_a_hotr1.py`, release-guarded) and "
      "written PROVISIONAL into the contracts and FW-C02 (`records/l5r2`); H2's item stays open until the keeper is in a "
      "generator, regenerated and at parity on the box; the panel firmware's F-03 (pico-sdk resets IO_BANK0 at boot, so FW-C02 "
      "cannot keep SLOT_EN alone) for the hold's owner |\n"
      "| 5.7 | reset, default and cable-out states for every control line | PARTLY | every power line of L4-E9 section 4 with "
      "its states and firmware row (`records/l5pwr`); default_state for the eight, SLOT_EN's cable-out with the keeper, U22's "
      "RUN line (`records/l5r2`); TX_INHIBIT_n's fail-safe level (EQ-25) |\n"
      "| 5.9 | harnesses defined and consistent | PARTLY | harness fields from ASSEMBLY.md and HC6-SC-7 (`records/l5r2`, its "
      "L5R2-F04); J_AB2 and MAIN at 128 and 480 mm, the fans on JST PH (`records/l7r2`); the jumper plug picked (Radiall "
      "R125.172.001, `records/l7r2`) |\n"
      "| 5.10 | mechanical mating of every interface | **OPEN** | mating fields on every contract (`records/l5r2`); W4-F17 "
      "(re-measured at 3.10 into D, `records/l7r2`), J_QMX's land (L5R2-F04, drafted on PH by `records/l8r2`) and the fans' "
      "lead terminations keep it open |\n"
      "| 5.11 | firmware obligations affecting hardware explicit | PARTLY | set 29: the slot-fault rule decided (`records/l5r4`, "
      "the panel firmware's F-14): one rule for a compute module lost at start-up and one lost while running in PANEL.md "
      "section 5 and FW-C05, CONOPS section 4e its source, the state kept across a controller reset (FW-C02, V-C05), a "
      "power-on reset read as HAD_POR set with the watchdog's REASON zero and the slot record beside the wipe journal (F-15, "
      "S-37), the five CFL readings rebound to that PANEL.md; set 28: the texts Layer 4's later rounds withdrew restated in the "
      "contract and the interfaces (L5-F09, L5-F10, L5-F11 closed by `records/l5pwr`'s set 28 round); earlier: FW-A19 to "
      "FW-A23, FW-C15, FW-E11 to FW-E13 added, FW-A09, FW-A14, FW-A16, FW-C08 and PANEL.md section 10 restated "
      "(`records/l5pwr`); FW-C02, FW-C01, FW-C14, V-C02, FW-E07, FW-E11 (DRAFTED, PROVISIONAL, `records/l5r2`); the panel "
      "controller's firmware implements FW-C01 to FW-C15 on host tests (`v2/firmware/panel`); owed: IF-7, the bridge's report "
      "of a tripped pack breaker (`records/l8p` section 7), FW-A05's floor text after D-17, the fan PWM row and FW-A09's "
      "recalibration; the bridge wire format (F-02, MESHSAT-837) is defined nowhere |\n"
      "| 5.12 | GND-002 implemented everywhere | PARTLY (from OPEN) | all four board changes DRAFTED (`records/l8gnd`: board "
      "A's CHASSIS net with R229 and the strap pad H1; board B's C33 and J_ETH shield on CHASSIS; release-guarded) and carried "
      "PROVISIONAL in IF-A-CHASSIS, IF-EXT-ETH, IF-EXT-DC, IF-AE-DOCK (`records/l5r2`); the bond's lugs and stud picked (JST "
      "R5.5-4, R5.5-6, M6 x 45, `records/l7r2`); open: the release and regeneration, the land in `meshsat.pretty`, the wall "
      "RJ45's shield path (no candidate read carries shield, PoE voltage and the envelope together, `records/l7r2` section 1), "
      "S-50's registry entry |\n"
      "| 5.13 | interface contracts consistent with the tree | PARTLY | the drawn board first, every draft DRAFTED with its "
      "row; stale texts corrected with their history kept (`records/l5r2`); `check_contracts.py` PASS 99 of 99 unchanged; "
      "`pcb_interfaces.yaml` is a CONFIG_INPUT of `interfaces.py`: its readings on every board are owed a re-take; owed by set "
      "29's drafts: the enable loop's contacts on IF-PE-PACK (J_SMB a 1x7) and IF-AE-DOCK (J_DOCK and J_BLK pins 3 to 5), "
      "PACK_P live only while docked (`records/l8p` section 7), the DC inlet's XT60-F (`records/l4e11` round 9, R-131) |\n\n")

L6 = ("**After set 29 (4 October 2026): IN_PROGRESS.** The power parts Layer 4 selected (`records/l6pwr`) and the generic "
      "parts of the six boards (`records/l6r2`) identified and sourced; `lcsc_fill.py`'s table corrected to codes that meet "
      "the identity tool's requirements; nothing on a regenerated netlist yet. The rows below are the items sets 28 and 29 "
      "moved; every other item (6.5, 6.9, 6.10, 6.11) keeps its H2 row below.\n\n" + HEAD +
      "| 6.1 | exact manufacturer, MPN, package and grade per fitted part | **OPEN**, toward PARTLY | the 28 power parts of "
      "L4-E5 to L4-E11 (14 RESOLVED on a page that prints the part number, 14 UNRESOLVED with their reason, "
      "`drafted_identities_l4_power`, `records/l6pwr`); 1440 of the 1657 uncoded fitted rows of the six boards given maker, "
      "MPN, package, code and grade (131 selections DECODED on the maker's table, 91 DOCUMENT_OWED, "
      "`drafted_identities_l6r2_passives`, `records/l6r2`); the five fans (`records/l7pwr`); both blocks sit outside "
      "`selections:` and are staged for the Layer 8 regeneration; no MPN field in the generators (EQ-21); owed by set 29's "
      "drafts: the 0.1 percent dividers of the LM5176 5.1 V stages (F5-03, `records/l8r2` round 6), board P's LM5069-1, "
      "OPA187IDBVR, NXRT15XH103FA1B010 and the 7-way J_SMB (`records/l8p` section 7, L8P-06), the silver-plated 25 A MINI "
      "blade 0297025.WXNV (`records/l9stk/apply_blade_plating_l9stk.py`, not applied) |\n"
      "| 6.2 | supporting documents with revision, source and currency | PARTLY | 17 makers' documents of the power parts (10 "
      "held back under their terms, fetched and matching) and Samsung's pages excerpted (`records/l6pwr`); the fans', "
      "cooler's and Preci-Dip's documents filed (`records/l7pwr`); JLCPCB's catalogue reading and KiCad's XAL footprints "
      "(`records/l6r2/inputs`); owed: the ZK sheet's URL, Samsung's MLCC catalogue, Milliohm's HoLLR sheet, Nexperia's "
      "packing legend, the 35E maker copy |\n"
      "| 6.3 | selection rationale recorded | PARTLY | one sentence per power part (`records/l6pwr`); rule I-1's order for "
      "every generic selection (`records/l6r2`); the fans row by row (`records/l7pwr`) |\n"
      "| 6.4 | compatibility findings; mismatches stay mismatches | PARTLY | the three Coilcraft rows of F4 proven on the "
      "maker's land, their footprint keys drafted, release-guarded (`records/l6r2` round 3); the standing wrong models as at "
      "H2 |\n"
      "| 6.6 | procurement constraints and alternatives | PARTLY | dated stock and price per selection, the five-kit need, "
      "an alternative per selection (`PROCUREMENT.md` section 8 Layer 6's and Layer 7's sections, `records/l6pwr`, "
      "`records/l6r2`); two stock pools read |\n"
      "| 6.7 | regenerated outputs preserve part decisions | PARTLY | `lcsc_fill.py`'s table corrected (eleven lines to the "
      "l6r2 selections, two X5R lines kept under rule C-D3b, held by `test_lcsc_fill_requirements.py`), so the next "
      "regeneration fills those codes; the generators' typed codes the certification refuses corrected through LCSC drafts "
      "(24 rows, `records/l6r2` round 4, release-guarded) (board E C5 now fills C113803; the generator's C14663 at line 713 "
      "belongs to C46 and C59, which carry it explicitly) |\n"
      "| 6.8 | a current, versioned BOM with identity per board | PARTLY | NOT MOVED: the parts are on no committed BOM until a "
      "board is regenerated with its drafts |\n\n")

L7 = ("**After set 29 (4 October 2026): IN_PROGRESS.** `records/l7pwr` settled the fans (D-18) and specified the T-H1 "
      "mock-up; `records/l7r2` decided the bond's lugs and stud, the jumper plug, the fans' terminations and the cooler "
      "fans' brackets; nothing built. The rows below are the items sets 28 and 29 moved; every other item (7.1 to 7.3, 7.6, "
      "7.7, 7.11 to 7.17) keeps its H2 row below.\n\n" + HEAD +
      "| 7.4 | mounting and retention | **OPEN**, toward PARTLY | the face's mounting drawn (C1); the cooler fans' cap bracket "
      "specified and their envelope drafted (`records/l7r2`, `apply_panel1450_coolers_r2.py`); the pack hold-down (S-27), the "
      "stack's retention and the mixers' sites undesigned |\n"
      "| 7.5 | connector, cable and service access | PARTLY | the connector plate (C3) drawn; the right-angle jumper plug "
      "picked (Radiall R125.172.001: M17x met, M17g met with 5G MAIN at 26.5 degrees and IRIDIUM in the back bundle, M18 at 5G "
      "MAIN -0.04 at the worst, F-R2-03); the bond's lugs and stud picked (JST R5.5-4, R5.5-6, M6 x 45); the fans' "
      "terminations on JST PH; J_AB2 and MAIN 128 and 480 mm (`records/l7r2`); the dock lead's pulse capability bounded on "
      "published relations, the 813 contact's a drafted maker question (`records/l7pwr`); the sealed RJ45 open (no candidate "
      "read carries shield, PoE voltage and the plate's envelope together); set 29: the dock enable's make-last contact, "
      "J_DOCK positions 3 and 5 at least 1 mm after every power pin at any angle the dock's guides allow, and the order at "
      "undocking (condition C1, `records/l8p` section 7), Layer 7's, open |\n"
      "| 7.8 | thermal interfaces specified | PARTLY | the PA flange sensor drawn on D (`76235aad`); the five IP68 fans "
      "picked (Sanyo Denki 9WL0612P4H001 mixers, 9WPA0412P6G001 cooler fans, `records/l7pwr`), the cooler fans placed on "
      "their brackets over the coolers with 3.46 to the PA and 13.36 to the plate (`records/l7r2`), their 12 V feeds drafted "
      "(board E's mixers L4-E11 section 18, board B's coolers `records/l8r2` item 1), the mixers' sites owed; the conductance "
      "(EQ-05) waits on T-H1 |\n"
      "| 7.9 | critical fit uncertainties resolved by suitable evidence | **OPEN** | FEA-007: the mock-up (L-07, EQ-08) and "
      "the desk items; T-H1's empty-case mock-up specified with its bill (`records/l7pwr/T-H1-MOCKUP-SPEC.md`: EUR 639.76, "
      "GBP 887.00, USD 147.38 read), not evidence; new nominal fits awaiting the box: the cooler fans' plan margins 1.0 and "
      "1.255 (F-R2-04), M18 at 5G MAIN (F-R2-03), the cooler fan's 2.76 mm to the backer; W4-F17 re-measured at 3.10 into D |\n"
      "| 7.10 | later physical checks allocated, deferral justified | PARTLY | FEA-007's staging as before; T-H1 allocated to "
      "the prototype bench with its specimen, bill, pass lines and the owner's authorisation named (`records/l7pwr`, "
      "`records/l4e12/T-H1-PROCEDURE-DRAFT.md`); the qualification procedures of `v2/docs/test-procedures/` (PROPOSED) |\n\n")

L8 = ("**After set 29 (4 October 2026): IN_PROGRESS on every board.** Records l8gnd, l8r2 (rounds 1 to 6) and l8p, and the "
      "Layer 4 records' apply scripts, drafted the known corrections as release-guarded apply scripts; no generator changed, "
      "no board regenerated. The rows below are the items sets 28 and 29 moved; every other item (8.1 to 8.4, 8.6, 8.8, 8.9, "
      "8.11 to 8.16, 8.18) keeps its H2 row below (8.1 and 8.9 stay MET for the committed generators; a regeneration with the "
      "drafts applied re-opens their parity on the box).\n\n" + HEAD +
      "| 8.5 | BOMs | PARTLY | two NOT_FOR_FAB BOMs per board as at H2; `lcsc_fill.py`'s table corrected (`records/l6r2`), so "
      "the next regeneration's BOMs fill those codes; the identity gap is Layer 6's (EQ-21) |\n"
      "| 8.7 | exact part and land mapping | PARTLY | SCH-005 as at H2; the three Coilcraft XAL rows on another series' "
      "footprint, the maker's land proven and the keys drafted (`records/l6r2` round 3, release-guarded) |\n"
      "| 8.10 | known schematic-affecting defects closed per board | **OPEN** | drafted, not applied (each release-guarded, "
      "refusing the generator until a RELEASE.md names an accepted check): GND-002's four changes and the SLOT_EN hold "
      "(`records/l8gnd`); board B's coolers on a per-slot 12 V step-up with an eFuse (E11-40, R-190), VBUS20's over-voltage "
      "cut-off in VIN_RAW (S-111, R-48), PANEL_5V behind an eFuse (L5R2-F03), board D's 3.3 V behind an eFuse as +3V3_A2D "
      "(L5R2-F05), J_QMX and J_CAM on the JST PH land (L5R2-F04), board C's PI button on U1 P1.3 (the panel firmware's F-01) "
      "(`records/l8r2` rounds 1 and 2). Set 29: board A's slots 1 and 3 on slot 2's LM5176 stage with the coolers at full "
      "speed (L9P-F02, `apply_gen_sch_a_slotlm.py`), both dividers of every LM5176 5.1 V stage at 0.1 percent (F5-03, "
      "`apply_gen_sch_a_fb01.py`), board B's six slot bucks at 500 kHz (O-20, `apply_gen_sch_b_rt500.py`), the pack path's "
      "return declared as a rail on A and E (`apply_gen_sch_a_packrtn.py`, `apply_gen_sch_e_packrtn.py`) (`records/l8r2` "
      "rounds 3 to 6); board P's LM5069-1 breaker with its hold and the restart inhibit C-1c, board E's enable loop and board "
      "A's PTC guard (`records/l8p`); board A's charger with the third battery FET Q42 and the VSYS hold U46, L8P-F02 and "
      "L8P-F03 corrected in the charger and auxiliary drafts, J_DCIN as the XT60-F, DD-7's input-return reset and hardware "
      "charge inhibit (`apply_gen_sch_a_dd7.py`) (`records/l4e11` round 9); L4-E7's backstop decoupling C66 to C68 in class D "
      "(`records/l4e7` round 6, L8P-F01 closed); the energy chain's conductor texts at the revised widths "
      "(`records/l9stk/apply_energy_chain_l9stk.py`, refusing until the register carries the board A and E stackup "
      "decisions). Open: P1-1 (the solar guard and its sense) left to the supplier; B-R2, DD-3, L9P-F01, L9P-F03; EQ-25 on C, "
      "PWR-001 on C, D, E, P and BAT-001 on P as at H2; `check_gnd002_netlist.py`, `check_l8r2_netlist.py` and "
      "`check_l8p_netlist.py` read NOT DRAWN on the committed netlists |\n"
      "| 8.17 | condition 1: substitutions stay mismatches until proven | PARTLY | as at H2; the corrected table's "
      "substitutions each carry their rule (C-D2, C-D3, C-D3b, R-S1, R-P) in `lcsc_fill.py` and `records/l6r2` |\n\n")

L9 = ("**After set 29 (4 October 2026): IN_PROGRESS.** Layer 9's power budget (`records/l9pwr`, item 9.1) and its stackups, "
      "copper and protection (`records/l9stk`, item 9.12 and the pack path) landed; nothing was routed, built or measured. "
      "The rows below are the items set 29's records move; every other item keeps its H2 row below.\n\n" + HEAD +
      "| 9.1 | current power calculations with margins and sensitivities | **PARTLY** (from OPEN) | `records/l9pwr` round 2 "
      "(`l9pwr_budget.py`, reproduces rv-pwr within 1e-9 W and every figure of another record it overlaps from that record's "
      "inputs): per state LOW / PLAN / HIGH per load and rail, every converter against its maker's rating or drafted limit, "
      "the pack side, on the generators at main `64cd25ee` (DRAWN) and with the Layer 4, 8 and 9 drafts (DRAFTED, ten drafts, "
      "not applied): the profile 43.30 W drawn, 44.58 W drafted (rv-pwr 42.82 W); sensitivities per state and over 12 to "
      "16.8 V; six margin findings: L9P-F01 OPEN (D-11's all-transmit floor needs 16.214 V rest on the drafts; L4-E9 round 8 "
      "keeps D-17 OPEN against REQ-018's 15.5 V pass line and withdrew round 7's 16.1 V), L9P-F02 resolved in the drafts "
      "(CONDITIONAL on `records/l8r2`'s C4-1 to C4-6), L9P-F03 to L9P-F06 OPEN; remains: the record's one focused review, "
      "L9P-F01's correction, the T-tier loads, the re-run once the drafts are applied |\n"
      "| 9.2 | current energy calculations with sensitivities | **OPEN** | PROVISIONAL; REQ-072 FAIL at desk; "
      "`energy_budget.py` and L4-E9's endurance rest on rv-pwr's 42.8 W profile, which `records/l9pwr` moves to 43.30 W drawn "
      "and 44.58 W drafted (energy-only 2.49 h and 2.42 h on L4-E10's 107.9 Wh, a consequence printed in l9pwr's R3, not this "
      "item's closure) |\n"
      "| 9.3 | protection coordination on the current design | PARTLY | as at H2 (`energy_chain.py` PASS of 98 on the H2 "
      "netlists, PWR-003 PASS on A, B, E, P, E5, BAT-001 FAIL on P, REQ-044); set 29: the pack path's protection on the "
      "owner's current-and-time criterion (`records/l9stk` section 15: board P's existing protection fails it with its FETs "
      "welded; the LM5069-1 breaker's limit 18.32 to 23.93 A, clearing within 1.29 ms with no firmware, its FETs at 0.57 and "
      "0.58 of the derated SOA by SLVA673A; every series part at the breaker's largest limit), DRAFTED, not drawn into any "
      "generator (`records/l8p`); its independent checks filed (`records/l9stk/checks/`, the last CONFIRMED AS CONDITIONAL "
      "with B-R2 left out); open: B-R2, DD-1 to DD-8, IF-1 to IF-7, the evidence E-1 to E-15, Q-TI-L9S-1 and Q-TI-17; "
      "decision 31's review owed |\n"
      "| 9.12 | stackup decided per board with measurement and cost | **PARTLY** (from OPEN) | one decision per board in "
      "`records/l9stk` with its measurement, derived bound or NO MEASUREMENT HELD (A 6L 1 oz with two-face bands; B 8L as the "
      "design input, conditional on decision 43's route; C 6L by decision 27; D 4L; E 4L 1 oz with two-face bands; P 4L 2 oz, "
      "0.5 oz inner with 16 mm planes; E5 2L 2 oz), written as seven session decisions in `apply_decisions_l9stk.py` and not "
      "yet appended to `pcb_decisions.yaml`; the outer copper weight of A and E open to the owner (L9STK CU: a band and its "
      "return need 78.29 mm a face at 1 oz, over board E's 68 mm strip, and 39.14 mm at 2 oz); the cost half NOT READ at any "
      "real outline (the public readings of 3 October 2026 print start prices and rates only), EQ-14 open for the supplier's "
      "quotation |\n\n")

L12 = ("## Layer 12. Firmware, bring-up, test plans and build documentation\n\n"
       "**After set 29 (4 October 2026): IN_PROGRESS.** Outside the nine pre-PCB layers above: the owner's instruction of 2 "
       "October 2026 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md`) asks for \"L12: firmware, bring-up procedures, test "
       "plans and build documentation in parallel wherever dependencies allow; physical results remain open until "
       "performed\". The item numbers are this page's. No release check has judged this layer, and nothing here has run on "
       "hardware.\n\n" + HEAD +
       "| 12.1 | firmware for each controller, with tests of its stated behaviour | PARTLY | the panel controller (board C, U3 "
       "RP2040): a portable core with its hardware layer and pico-sdk port, 64 host unit tests under `-Werror` after its round "
       "4 (`fnd/fw-r4`: Layer 5 round 4's one slot-fault rule followed, F-14 closed; the slot state kept across a controller "
       "reset in a flash sector beside the wipe journal, S-37; a power-on reset read as HAD_POR with the watchdog's REASON "
       "zero, F-15) and `test_fw_panel.py` binding the code to the netlists and FW-C01 to FW-C15 (`v2/firmware/panel`); the "
       "target build NOT compiled (no arm toolchain here), nothing run on hardware; findings F-01 to F-15 to their owners (F-01 "
       "drafted by `records/l8r2` item 4); the sensor controller (board E), the bridge's side and the wire format (F-02, "
       "MESHSAT-837) not started |\n"
       "| 12.2 | bring-up procedure per board | PARTLY | `v2/docs/PCB-BRING-UP.md`: the first-prototype bring-up of A, B, C, "
       "D, E, E5 and P written above the renderer's generated rail inventory (PROPOSED, for the design with its drafts "
       "applied, checked by `tp_check.py`); `rules_render.py --check` reads the page current; TST-001's reading on it owed a "
       "re-take |\n"
       "| 12.3 | test procedures for the qualification route | PARTLY | ten procedures (TP-CELL, TP-E11-29, -30, -31, -35, "
       "-36, -37, -38, TP-EPAPER, TP-SOLAR), each quoting its register row and 5d route row, every quote held to its source by "
       "`tp_check.py`, PROPOSED for the supplier to review; none run; set 29's records name further qualification items not "
       "yet written as procedures (C4-1 to C4-6, `records/l8r2`; E-1 to E-15, `records/l9stk`; E11-41 to E11-45, "
       "`records/l4e11` section 19) |\n"
       "| 12.4 | build documentation | NOT MOVED | BUILD.md and ASSEMBLY.md as at H2 |\n"
       "| 12.5 | physical results recorded | **OPEN** | nothing built or run; every procedure's result is owed |\n\n"
       "---\n\n")

SECTIONS = [("## Layer 4. System architecture\n\n", L4), ("## Layer 5. Partitioning and interfaces\n\n", L5),
            ("## Layer 6. Components\n\n", L6), ("## Layer 7. Mechanical and enclosure\n\n", L7),
            ("## Layer 8. Schematics\n\n", L8), ("## Layer 9. Pre-layout design analysis\n\n", L9)]
INTRO_AT = "**How to read this page after H2.**"
L12_AT = "## Appendix A. The audit at `e3aedb25` and each layer's edition history"


def refuse(msg):
    print("apply_layer_status_set29: REFUSED: %s" % msg)
    sys.exit(2)


def main(argv):
    check = "--check" in argv
    page = argv[argv.index("--page") + 1] if "--page" in argv else PAGE
    t = open(page, encoding="utf-8").read()
    if MARK in t:
        refuse("has run: the page carries set 29's mark")
    new = t
    for anchor in [INTRO_AT, L12_AT] + [a for a, _ in SECTIONS]:
        if new.count(anchor) != 1:
            refuse("anchor %r occurs %d times, not once" % (anchor[:60], new.count(anchor)))
    new = new.replace(INTRO_AT, INTRO + INTRO_AT, 1)
    for anchor, block in SECTIONS:
        nxt = new[new.index(anchor) + len(anchor):][:30]
        if not nxt.startswith("**At H2: IN_PROGRESS"):
            refuse("the section after %r does not open with its H2 status" % anchor.strip())
        new = new.replace(anchor, anchor + block, 1)
    new = new.replace(L12_AT, L12 + L12_AT, 1)
    for ch in ("—", "–"):
        if ch in INTRO + L4 + L5 + L6 + L7 + L8 + L9 + L12:
            refuse("a dash character in the text this script writes")
    # layer 3's section and everything outside the inserted blocks unchanged
    removed = new
    for block in [INTRO, L12] + [b for _, b in SECTIONS]:
        removed = removed.replace(block, "", 1)
    if removed != t:
        refuse("the page moved outside the inserted blocks")
    if check:
        print("apply_layer_status_set29: --check, nothing written: %d characters added (%d rows)" %
              (len(new) - len(t), sum(b.count("\n| ") for b in [L4, L5, L6, L7, L8, L9, L12])))
        return 0
    with open(page, "w", encoding="utf-8") as f:
        f.write(new)
    if open(page, encoding="utf-8").read() != new or MARK not in new:
        refuse("the written page does not read back")
    print("apply_layer_status_set29: written %s (%d characters added)" % (os.path.relpath(page, TOP), len(new) - len(t)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
