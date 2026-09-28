#!/usr/bin/env python3
"""The re-binding of the seven layout constraint sheets to the set 6 candidate (p3bind, MESHSAT-1357, 27 September 2026).

WHAT IT DID, ONCE. For each sheet of v2/docs/layout-constraints/ it
  1. put a new opening paragraph and the sheet's `bound` block above the H2 binding's paragraph, which it keeps as that
     binding's record under a lead that says so (on E5, above the sheet's one opening paragraph);
  2. replaced section 2's power table by the tables `calc/rail_widths.py` prints for the board on the committed
     inputs, with a `note` column whose text is NOTES below;
  3. made the edits of EDITS to the sentences of section 2 that the new table made untrue.
No other section is touched: the script asserts that every line outside the opening and section 2 is byte for byte
what it was.

WHERE EVERY NUMBER COMES FROM. The cells are constraints_bound.emit_tables', which are rail_widths.py's. A note quotes
the intent file's own text for the rail: every quotation is a `{q}` of NOTES and the script asserts that it is a
substring of that rail's `note` in the committed intent file, so a quotation cannot drift from its source. A figure a
note gives for an OLDER candidate (12.31 A, 11.92 mm at e3aedb25) is rail_widths.py run on that commit's intent file
(records/p3bind/rail-moves.md), and the commit a note names for a change is the first whose intent file carries
today's currents (records/p3bind/rail-commits.md).

IT STARTS FROM THE SHEETS AS THEY STOOD AT 760d7f41, read out of git, so its output is a function of that commit's
sheets, the calculation and the notes below, and running it again gives the same bytes. It writes a sheet only while
the working copy is that commit's text or its own output: a sheet somebody has edited since (the other sections are
re-read by other workers) is refused, never overwritten. After writing it runs the check and fails unless every sheet
passes. To re-bind the sheets another day use `constraints_bound.py --emit <letter>`, which prints the block and the
tables with the notes a sheet already holds.
Usage: rebind_sheets.py [--dry-run]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "v2", "ecad", "tools"))
import constraints_bound as CB

READ = ("2026-09-27", "760d7f41")
BASE = "760d7f41"
H2_LEAD = "**Bound to the H2 line (after H2, 27 September 2026).**"
H2_KEPT = "**As re-bound to the H2 line (after H2, 27 September 2026), kept as that binding's record.**"
FIRST = {"e5": "A view over the records at `main` `e3aedb25`"}
BOARD_FILE = {"a": "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb", "b": "v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb",
              "c": "v2/ecad/pcb-c-display-c8/pcb-c-display.kicad_pcb", "d": "v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_pcb",
              "e": "v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb", "p": "v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb"}
NAME = {"a": "Board A", "b": "Board B", "c": "Board C", "d": "Board D", "e": "Board E", "e5": "Board E5", "p": "Board P"}

# What set 6 changed in each board's inputs, read from `git diff 6ec37197..760d7f41` of the intent file and the netlist.
SET6 = {
    "a": "Set 6 changed board A's netlist in `c4ad8350` (the hot stop line HOT-R1 drawn) and nothing of its intent file "
         "but the `written` stamp: **no row of the power table moved**.",
    "b": "Set 6 changed board B's netlist and intent file in `910da406` (EMCON forces the RockBLOCK's ENABLE low and drives "
         "each card rail's enable from its slot's own 5 V): four decoupling entries (C607, C637, C667, C559), the gates "
         "U116, U216, U316 and U536 entered as loads of 1 to 2 mA, and the switch and enable net of +5V_LORA, +5V_LIME "
         "and +5V_RB declared. No rail's declared typical or peak current changed: **no row of the power table moved**.",
    "c": "Set 6 changed board C's netlist and intent file in `e28f91a6` (TX_INHIBIT_n fails safe with the panel unpowered; "
         "the supplies PWR-001 refused are declared): **+3V3 moved and EPD_VCC, LED_RAIL_SW and LED_RAIL are new rows**, "
         "each marked **SET 6** in the table.",
    "d": "Set 6 changed board D's netlist and intent file in `932cf9d7` (the flyback diode D2 ordered with its sheet; the "
         "node RLY_K declared). A node is not a rail: **no row of the power table moved**.",
    "e": "Set 6 changed board E's netlist and intent file in `c4ad8350` (the hot stop line HOT-R1 drawn; the nodes FAN1_SW "
         "and FAN2_SW declared). A node is not a rail: **no row of the power table moved**.",
    "e5": "Set 6 changed neither of board E5's inputs. **The table is new with this binding**: until it the sheet quoted the "
          "model's figures in a sentence, with nothing generated to compare them with.",
    "p": "Set 6 changed board P's netlist and intent file in `932cf9d7` (the supplies PWR-001 refused are declared, with "
         "the nodes PBI, CELL1 to CELL3, FUSE_G and FUSE_GQ): **BAT_F, VCC_F, SEC_VDD, SW and SCP_HTR are new rows**, each "
         "marked **SET 6** in the table, and SW is judged at the pack path's 18 A.",
}
OLDER = {
    "e5": "the readings at `e3aedb25`, with what the H2 line changed stated in the paragraph below (`ef144760`)",
}
AGAINST = {"e5": "the board file and the chain below"}

# The notes. {letter: {"main" | "sized": {rail as the tool prints it: (text, [quotations])}}}
H2 = "**H2**"
S6 = "**SET 6**"
NOTES = {
    "a": {"main": {
        "CELL+": ("the pack path; the inner width is not a practical conductor, so outer copper only (item 1)", []),
        "CELL_FUSED": ("the pack path", []),
        "VBAT": ("the pack path", []),
        "VIN_RAW": (H2 + ": 14.10 A since `b7f96784`; at `e3aedb25` it was 12.31 A, which is 11.92 mm on one outer face and "
                    "17 / 14 / 12 barrels. The intent file: \"{q0}\", \"{q1}\". The inner width is not a practical "
                    "conductor (item 4)",
                    ["declared at board E's 14.10 A since R8E-N01 (27 September 2026: this board's front end at its ISNS "
                     "limit drawing from a 9.0 V bus, R4A-N12)",
                     "crossing the dock on the Mill-Max power pins J_VR1 to J_VR4 (EQ-16)"]),
        "+5V_S1": ("slot 1's rail runs at 4.65 A in PS-ALLTX PLAN (PWR-F02, item 5)", []),
        "PRECHG": (H2 + ", new in `ffca0771`: \"{q0}\". The typical current is nil, so the widths are; the barrels are at "
                   "the 1.68 A peak", ["the pre-charge pin's conductor to R1 (10 Ohm) and CELL+: 1.68 A at most"]),
        "VMON": (H2 + ", new in `ffca0771`: \"{q0}\"",
                 ["the Xenarc 709GNK monitor's supply behind the eFuse U21 (limit 1.2 A, MON_EN)"]),
        "+3V3_EMCON_EF": (H2 + ", new in `ffca0771`: \"{q0}\"; declared at 0.4 mA typical and 2 mA peak, which print as "
                          "0.00", ["the EMCON gates' supply behind the eFuse U39"]),
        "+3V3_EMCON": (H2 + ", new in `ffca0771`: \"{q0}\"; declared at 0.4 mA typical and 2 mA peak, which print as 0.00",
                       ["the four SN74AUP1G08 EMCON gates' own supply behind R213"]),
    }},
    "b": {"main": {
        "+5V_S1": ("a slot rail, a plane on In4 today", []),
        "+5V_S2": ("the 5G slot; board A declares 2.5 A typical for the same conductor (`pcb_interfaces.yaml` IF-AB-POWER, "
                   "status DISAGREE, I-03 open)", []),
        "+5V_S3": ("a slot rail, a plane on In4 today", []),
        "+5V_DEV": ("the device rail; its declared children and its peak are the question of `boards/b.json` "
                    "`_b_feeders_declared_and_the_device_rail_is_short_at_peak`", []),
        "+3V3_S1A": ("**declared below its maker's figure** (PWR-F01): size it by the second table", []),
        "+3V3_M2C1": ("**declared below its maker's figure** (PWR-F01): size it by the second table", []),
        "+3V3_S3A": ("**declared below its maker's figure** (PWR-F01): size it by the second table", []),
        "+3V3_M2C3": ("**declared below its maker's figure** (PWR-F01): size it by the second table", []),
        "+3V3_S2A": ("the RM520N-GL socket", []),
        "+3V3_M2C2": ("the RM520N-GL socket, past its Kelvin shunt", []),
        "+1V2_KSZ": ("**declared below its maker's figure** (PWR-F03): size it by the second table", []),
        "+2V5_KSZ": ("**declared below its maker's figure** (PWR-F03): size it by the second table", []),
        "+1V1_S1": ("**its peak is declared below the maker's four-SS row** (PWR-F05): the second table", []),
        "+1V1_S2": ("**its peak is declared below the maker's four-SS row** (PWR-F05): the second table", []),
        "+1V1_S3": ("**its peak is declared below the maker's four-SS row** (PWR-F05): the second table", []),
        "+5V_LIME": ("the SDR bay's eFuse; its peak with +5V_RB's is the fabric question of "
                     "`_b_feeders_declared_and_the_device_rail_is_short_at_peak`", []),
        "+5V_RB": ("the satellite modem: \"{q0}\", so the peak sets the barrels",
                   ["burst current on a transmit attempt is the number the copper has to carry, not its average"]),
        "+54V_POE": ("spacing governs, section 8", []),
        "GND": ("the return of the four input rails, carried by the In1 plane and the outer pours: the widths are what one "
                "conductor would need and no band is asked for; the barrels are per transition, at the 21 A peak", []),
        "PANEL_5V": ("behind F1, an MF-MSMF110 (1.1 A hold, 2.2 A trip) since round 8, `b76c18cb` (`boards/b.json` "
                     "`_panel_5v_fuse_r8_why`): the copper must clear the fuse's hold, which the width of this row does "
                     "not say. The record's answer is the PANEL class at 0.8 mm in `gen_pcb_b3.py` for the next cut "
                     "(`pcb_energy_chain.yaml` stage B_PANEL_5V); board C declares 1.0 A peak on the same conductor", []),
        "VBUS_FLASH1": (H2 + ", new in `caba1876`: \"{q0}\"; nanoamperes, which print as 0.00",
                        ["it feeds only the USBLC6-2SC6's VBUS reference (pin 5)"]),
        "VBUS_FLASH2": (H2 + ", new in `caba1876`: as VBUS_FLASH1", []),
        "VBUS_FLASH3": (H2 + ", new in `caba1876`: as VBUS_FLASH1", []),
        "SIM1_VCC": (H2 + ", new in `caba1876`: \"{q0}\"; the 50 mA peak is INFERRED, the intent file says",
                     ["SIM 1's supply from the module's USIM1_VDD"]),
        "SIM2_VCC": (H2 + ", new in `caba1876`: \"{q0}\"", ["SIM 2's supply from the module's USIM2_VDD"]),
        "SIMC2_VCC": (H2 + ", new in `caba1876`: \"{q0}\"",
                      ["SIM 2's supply at the holder, past the 0 Ohm eSIM option link R272"]),
        "VBAT_RTC": (H2 + ", new in `caba1876`: \"{q0}\"; microamperes, which print as 0.00",
                     ["the CR2032's 3 V to the three modules' RTC inputs (pin 76)"]),
        "POE_P": (H2 + ", new in `caba1876`: \"{q0}\"; spacing governs, section 8",
                  ["a series segment of +54V_POE at the port's 0.60 A peak"]),
        "MDI_A_P": (H2 + ", new in `caba1876`: \"{q0}\"; spacing governs, section 8",
                    ["a series segment of POE_P carrying half its current, and a 1000BASE-T signal conductor"]),
        "MDI_A_N": (H2 + ", new in `caba1876`: as MDI_A_P", []),
        "MDI_B_P (return of +54V_POE)": (H2 + ", new in `caba1876`: \"{q0}\"; \"{q1}\", so spacing governs, section 8",
                                         ["half the port's return from the jack's pin 3", "up to 57 V with it off"]),
        "MDI_B_N (return of +54V_POE)": (H2 + ", new in `caba1876`: as MDI_B_P", []),
        "POE_DRAIN (return of +54V_POE)": (H2 + ", new in `caba1876`: \"{q0}\"; \"{q1}\"",
                                           ["the port's return from T1's centre tap MCT2 (pin 21) to the drain of the "
                                            "port switch Q1", "up to 57 V with it off"]),
        "POE_SEN (return of +54V_POE)": (H2 + ", new in `caba1876`: \"{q0}\"",
                                         ["the port's return from Q1's source to the 0.25 Ohm sense resistor R12"]),
        "GNSS_VDD_RF": (H2 + ", new in `caba1876`: \"{q0}\"; the currents are INFERRED, the intent file says",
                        ["the active antenna's supply from the LG290P's VDD_RF to R23"]),
        "GNSS_BIAS": (H2 + ", new in `caba1876`: \"{q0}\"", ["a series segment of GNSS_VDD_RF"]),
        "GNSS_ANT": (H2 + ", new in `caba1876`: \"{q0}\"", ["a series segment of GNSS_VDD_RF"]),
    }, "sized": {}},
    "c": {"main": {
        "+5V": ("from board B's PANEL_5V over J_PANEL", []),
        "+3V3": (S6 + ", moved in `e28f91a6` (W4C-F5): 0.12 / 0.20 A at the H2 line. The intent file: \"{q0}\". The outer "
                 "widths do not move at two decimals and the inner goes from 0.10 to 0.13 mm. The LDO U5 (TLV75533) is "
                 "rated under the declared peak: \"{q1}\"",
                 ["the figures cover the child EPD_VCC: its own loads' 0.119 A typical and 0.199 A peak plus EPD_VCC's "
                  "0.030 and 0.521 A",
                  "U5 is rated 500 mA (TI SBVS320D): the excess at the peak is 0.35 uC per on-phase, 24 mV on C2, C28 and "
                  "C29 at most; U5's average through a refresh is an open item read at bring-up"]),
        "EPD_VCC": (S6 + ", new in `e28f91a6`, one of the supplies PWR-001 refused at H2: \"{q0}\". Of its 30 mA typical "
                    "10 mA is INFERRED for the boost; the peak is \"{q1}\"",
                    ["the e-paper's switched supply: Q5 (AO3401A) from +3V3 to the panel's VDDIO and VDD and to the boost "
                     "inductor L1", "0.5 A peak into L1 = the boost switch's current class"]),
        "LED_RAIL_SW": (S6 + ", new in `e28f91a6`, one of the supplies PWR-001 refused at H2: \"{q0}\". Declared at 0.1593 A "
                        "typical and 0.4619 A peak: \"{q1}\"",
                        ["the lighting supply behind the LIGHTING toggle",
                         "Typical: the lamps at their design currents; peak: every lamp with no forward drop at 5.25 V"]),
        "LED_RAIL": (S6 + ", new in `e28f91a6`, one of the supplies PWR-001 refused at H2: \"{q0}\"; \"{q1}\"",
                     ["the PWM'd lamp rail: Q1 (AO3401A) from LED_RAIL_SW",
                      "18 lamps behind their series resistors, 8 mA each by design"]),
    }},
    "d": {"main": {
        "+5V_D8": ("from board A over J_PWR1", []),
        "+5V_SA": ("the exciter, behind FB1; its layer transition needs the two barrels of this row (the first item below)", []),
        "+5V_TX": (H2 + ", new in `76235aad` (round 8): \"{q0}\"",
                   ["the transmit chain's 5 V behind the TPS22810 load switch U21"]),
    }},
    "e": {"main": {
        "CELL_F": ("the pack path, F3 to the dock block; the inner width is not a conductor (item 1)", []),
        "CELL+": ("the pack path, J_BATT to F3", []),
        "VIN_RAW": (H2 + ": 14.10 A since `bc0f562f` (round 8); at `e3aedb25` it was 6.15 A, which is 3.67 mm on one outer "
                    "face and 9 / 7 / 6 barrels. The intent file: \"{q0}\"; \"{q1}\"",
                    ["Declared at 14.10 A typical and peak (R4A-N12, 26 September 2026): board A's front end at its ISNS "
                     "limit (5.7 A at 20.7 V, 0.93) drawing from a 9.0 V bus",
                     "the 12 AWG pad to the dock's four VIN_RAW power pins (EQ-16, 27 September 2026; until then J_BLK "
                     "pins 1 to 4)"]),
        "DC_IN": ("the shore and vehicle inlet", []),
        "DC_F": ("the shore and vehicle inlet", []),
        "DC_P": ("the shore and vehicle inlet", []),
        "HS_S": ("the shore and vehicle inlet", []),
        "DC_HS": ("the shore and vehicle inlet", []),
        "PV_P": ("the solar input", []),
        "PV_IN": ("the solar input", []),
        "TRK_OUT": (H2 + ": 10.33 A since `bc0f562f` (round 8); at `e3aedb25` it was 6.16 A, which is 3.68 mm on one outer "
                    "face and 9 / 7 / 6 barrels. The intent file: \"{q0}\"",
                    ["Declared at 10.33 A typical and peak (R4A-N12, 26 September 2026): the panel's 93 W at the 9 V bus "
                     "floor, when a vehicle holds the bus under 15.1 V; 6.16 A is the figure at 15.1 V"]),
        "SGP_VDD": (H2 + ", new in `b7f96784`: \"{q0}\"; 4.6 mA, which prints as 0.00",
                    ["the SGP41's VDD behind its RC element"]),
    }},
    "e5": {"main": {
        "CELL+": ("the four CELL+ targets and their wire land; the currents are the chain's for the stage, and 4.5 A a pin "
                  "if the four share equally (INFERRED, the second item below)", []),
        "CELL_N (return of CELL+)": ("the four return targets and their wire land", []),
    }},
    "p": {"main": {
        "PACK_P": ("the pack path, the pack terminal", []),
        "CELL4": ("the pack path, the top cell tap at the fuse", []),
        "FUSED": ("the pack path, after F1", []),
        "SCP_OUT": ("the pack path, after F2", []),
        "PACK_N (return of PACK_P)": ("the pack path's return, W_N to R10; its stubs take the PACK class (item 2)", []),
        "BAT_F": (S6 + ", new in `932cf9d7`, one of the supplies PWR-001 refused at H2: \"{q0}\"; 336 uA, which prints as "
                  "0.00", ["U1's primary supply (SLUSC67B pin 32, 'Primary power supply input pin')"]),
        "VCC_F": (S6 + ", new in `932cf9d7`, one of the supplies PWR-001 refused at H2: \"{q0}\"",
                  ["U1's secondary supply (SLUSC67B pin 26, 'Secondary power supply input'), from the pack terminal "
                   "through R7 1 kohm"]),
        "SEC_VDD": (S6 + ", new in `932cf9d7`, one of the supplies PWR-001 refused at H2: \"{q0}\"; \"{q1}\"",
                    ["U2's supply (SLUSEG7D pin 1 VDD; RVD 300 ohm and CVD 100 nF, Table 8-1)",
                     "0.18 mA declared as the peak"]),
        "SW": (S6 + ", new in `932cf9d7`, one of the supplies PWR-001 refused at H2: \"{q0}\". **Pack path**: the intent "
               "file declares it a series segment of SCP_OUT at SCP_OUT's own currents, so it is judged at PWR-F12's 18 A "
               "with the rest of that conductor (`calc/rail_widths.py`, WHICH RAILS ARE THE PACK PATH; the session's, "
               "27 September 2026). The FETs want their drain copper (item 4), and this is it",
               ["the common drain of Q1 and Q2 (CSD17570Q5B, TI SLPS471D), the pack's whole current: 10 A typical and 18 "
                "A peak as SCP_OUT and PACK_P carry it"]),
        "SCP_HTR": (S6 + ", new in `932cf9d7`: \"{q0}\"; \"{q1}\"",
                    ["the chemical fuse's heater return (Eaton SCF9550-30-05, ELX1135: heater 4.8 to 8.0 ohm, operating "
                     "10.5 to 23.5 V, opens the fuse within 60 s)",
                     "declared at 3.5 A typical as well as peak because a 60 s event is a steady state for copper"]),
    }},
}

TABLE_SAYS = ("The table is `calc/rail_widths.py`'s output on the inputs this sheet's `bound` block names, row for row in "
              "the tool's own order and cell for cell, and `v2/ecad/tools/constraints_bound.py` fails when the two "
              "differ; the `note` column is this sheet's and is not compared (README, \"The bound block\"). A width "
              "printed 0.00 is under 0.005 mm, a current of a few milliamperes: the fabricator's floor governs there, "
              "not the current.")
SIZED_SAYS = ("Sized at the maker's figure, above the declaration (`calc/rail_widths.py` SIZED_TO; "
              "`v2/docs/feasibility/POWER-THERMAL.md` section 10). The declaration is unchanged and is board B's owner's "
              "to correct; until it is, these are the widths and barrel counts to follow:")

# Sentences of section 2 the new table made untrue: (old, new). Each old text must stand exactly once in section 2.
EDITS = {
    "b": [("Where a maker's figure exceeds the declaration (POWER-THERMAL PWR-F01,\nF03, F05), the maker's figure is the "
           "one to size to, and the row says so.",
           "Where a maker's figure exceeds the declaration (POWER-THERMAL PWR-F01,\nF03, F05), the maker's figure is the "
           "one to size to: the first table is the declaration's, its row says so in its note,\nand the second table "
           "sizes the same rail at the maker's figure.")],
    "c": [("The project file's PWR and RAIL classes are 0.5 mm wide; both rails are far inside them. Board C's feed is "
           "protected\nupstream on board B (a 2.0 A hold polyfuse whose copper there is the constraint, `B.md` section 2).",
           "The project file's PWR and RAIL classes are 0.5 mm wide; all five rails are far inside them. Board C's feed is "
           "protected\nupstream on board B (F1, since round 8 an MF-MSMF110 with a 1.1 A hold, whose copper there is the "
           "constraint, `B.md` section 2).")],
    "e5": [("(`calc/rail_widths.py`'s model applied to 18 A at 0.070 mm; the block\n  has no intent file, so the table is "
            "not generated for it).",
            "(the table above, which `calc/rail_widths.py` generates for the\n  block since the set 6 binding from the "
            "chain's stage, the block having no intent file).")],
}


def git_short(*a):
    rc, out = CB._git(ROOT, *a)
    assert rc == 0 and out, a
    return out


def block(letter, RW):
    L = CB.emit_block(letter, ROOT, RW, today=READ[0])
    assert L[0] == CB.OPEN and L[-1] == CB.FENCE
    body = [l for l in L[1:-1] if l.split()[0] not in ("read",)]
    assert not [l for l in body if "UNKNOWN" in l], body
    n = NSEC[letter]
    rest = "sections 1 and 3 to %d" % n
    out = [CB.OPEN, body[0], body[1], "read       %s at %s" % READ,
           "current    section 2: the power table, and the figures the text under it quotes from it",
           "older      %s: read at e3aedb25, with the H2 line's changes marked at ef144760" % rest]
    out += [l for l in body[2:] if l.split()[0] in CB.INPUT_ROLES]
    if letter in BOARD_FILE:
        rel = BOARD_FILE[letter]
        out.append("board_file %s sha256/16 %s changed %s" % (rel, CB.sha16(os.path.join(ROOT, rel)),
                                                              git_short("log", "-1", "--format=%h", "--", rel)))
    out += [l for l in body[2:] if l.split()[0] not in CB.INPUT_ROLES]
    out.append(CB.FENCE)
    return out


def opening(letter, RW):
    n = NSEC[letter]
    older = OLDER.get(letter, "the readings at `e3aedb25` with the H2 line's changes marked where they stand (`ef144760`, "
                              "the paragraph below)")
    p = ("**Bound to the set 6 candidate (27 September 2026, read at `%s`).** This sheet's inputs stand in the block "
         "below, one to a line, each with its sha256/16 and the commit it last changed in, with the model and the stack "
         "the widths were computed on; `v2/ecad/tools/constraints_bound.py` fails when a committed input, the "
         "calculation or this sheet's power table moves without the others (README, \"The bound block\"). **Re-read on "
         "this candidate: section 2 alone.** Its power table is `calc/rail_widths.py`'s output on the inputs below, and "
         "the widths, currents and barrel counts the text under the table quotes were compared with the table and agree. "
         "**Not re-read on this candidate: sections 1 and 3 to %d**, which are %s. %s A line of the older sections that "
         "names a part, a net, a current or a count is compared with %s before it is "
         "followed, and where this sheet and a record disagree the record governs (README). %s is not at layout entry: "
         "no board is (`v2/docs/CURRENT-EVIDENCE.md`, which holds the reasons current on this candidate; a count of "
         "reasons in a paragraph below is its own binding's).") % (
             READ[1], n, older, SET6[letter], AGAINST.get(letter, "the netlist and the intent file below"), NAME[letter])
    return wrap(p)


def wrap(text, width=120):
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w) if cur else w
    if cur: out.append(cur)
    return out


def notes_for(letter, RW):
    """{(table head, rail): note}, every quotation checked against the intent file's own note for the rail."""
    t = RW.rows(letter, ROOT)
    rails = {}
    if t["kind"] == "intent":
        with open(os.path.join(ROOT, RW.BOARDS[letter][0]), encoding="utf-8") as f: rails = json.load(f)["rails"]
    printed = {"main": [RW.cells(r)[0] for r in t["rows"]], "sized": [RW.cells_sized(r)[0] for r in t["sized"]]}
    net_of = {RW.cells(r)[0]: r["net"] for r in t["rows"]}
    out = {}
    for kind, d in NOTES.get(letter, {}).items():
        head = tuple(RW.HEAD if kind == "main" else RW.HEAD_SIZED)
        for rail, (text, quotes) in d.items():
            assert rail in printed[kind], "%s: NOTES names %r and the tool prints no such row" % (letter, rail)
            src = " ".join(str((rails.get(net_of.get(rail, rail)) or {}).get("note") or "").split())
            for q in quotes:
                assert q in src, "%s %s: the intent file's note does not say %r\n  it says: %s" % (letter, rail, q, src)
            note = text.format(**{"q%d" % i: q for i, q in enumerate(quotes)})
            assert "\n" not in note and "|" not in note, (letter, rail)
            out[(head, rail)] = note
    return out


def tables(letter, RW):
    """Section 2's tables as lines: the tool's cells, this script's notes. A table none of whose rows has a note
    carries no note column (the check takes a table with the column or without it)."""
    notes = notes_for(letter, RW)
    groups, head = [], None
    for l in CB.emit_tables(letter, ROOT, RW):
        c = CB.split_row(l)
        if c is None or CB.is_rule(c): continue
        if c[0] == "rail":
            head = tuple(c[:-1]); groups.append((head, [])); continue
        groups[-1][1].append((c[:-1], notes.get((head, c[0]), "")))
    assert groups and groups[0][0] == tuple(RW.HEAD)
    out = []
    for k, (head, rows) in enumerate(groups):
        if k:
            assert head == tuple(RW.HEAD_SIZED), head
            out += [""] + wrap(SIZED_SAYS) + [""]
        noted = any(n for _c, n in rows)
        out.append("| " + " | ".join(list(head) + ([CB.NOTE] if noted else [])) + " |")
        out.append("|" + "|".join(RW.ALIGN.get(h, "---") for h in head) + ("|---|" if noted else "|"))
        for c, n in rows:
            out.append("| " + " | ".join(x.replace("|", "\\|") for x in c + ([n] if noted else [])) + " |")
    return out


def rebind(letter, RW, text):
    lines = text.split("\n")
    assert CB.OPEN not in [l.strip() for l in lines], "%s at %s already carries a bound block" % (letter, BASE)
    # ---- the opening
    lead = FIRST.get(letter, H2_LEAD)
    at = [i for i, l in enumerate(lines) if l.startswith(lead)]
    assert len(at) == 1 and lines[at[0] - 1] == "", (letter, at)
    k = at[0]
    if letter not in FIRST:
        lines[k] = lines[k].replace(H2_LEAD, H2_KEPT, 1)
        assert lines[k].startswith(H2_KEPT)
    lines[k:k] = opening(letter, RW) + [""] + block(letter, RW) + [""]
    # ---- section 2
    heads = [i for i, l in enumerate(lines) if l.split()[:2] == ["##", CB.POWER_SECTION]]
    assert len(heads) == 1, (letter, heads)
    a = heads[0]
    b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("## "))
    sec = lines[a + 1:b]
    rows = [i for i, l in enumerate(sec) if CB.split_row(l) is not None]
    new = [TABLE_SAYS_WRAPPED, ""] + tables(letter, RW)
    if rows:
        assert rows == list(range(rows[0], rows[-1] + 1)), "%s: section 2 holds more than one table" % letter
        sec[rows[0]:rows[-1] + 1] = "\n".join(new).split("\n")
    else:
        assert sec[0] == "", letter
        sec[1:1] = "\n".join(new).split("\n") + [""]
    body = "\n".join(sec)
    for old, neu in EDITS.get(letter, []):
        assert body.count(old) == 1, "%s: section 2 does not carry %r exactly once" % (letter, old)
        assert old != neu
        body = body.replace(old, neu)
    lines[a + 1:b] = body.split("\n")
    return "\n".join(lines)


def outside(text):
    """The sheet without its opening and its section 2: what this script must leave byte for byte."""
    lines = text.split("\n")
    first = next(i for i, l in enumerate(lines) if l.startswith("## "))
    a = next(i for i, l in enumerate(lines) if l.split()[:2] == ["##", CB.POWER_SECTION])
    b = next(i for i in range(a + 1, len(lines)) if lines[i].startswith("## "))
    return [lines[0]] + lines[first:a + 1] + lines[b:]


def main(argv):
    RW = CB.load_calc()
    global NSEC, TABLE_SAYS_WRAPPED
    TABLE_SAYS_WRAPPED = "\n".join(wrap(TABLE_SAYS))
    NSEC, todo, refused = {}, {}, []
    for letter, name in sorted(CB.SHEETS.items()):
        rel = "/".join(CB.SHEET_DIR + (name,))
        rc, _full = CB._git(ROOT, "rev-parse", "--verify", "--quiet", BASE + "^{commit}")
        assert rc == 0, "this repository does not hold %s" % BASE
        import subprocess
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, rel)], capture_output=True)
        assert r.returncode == 0, rel
        base = r.stdout.decode("utf-8")
        NSEC[letter] = max(int(l.split()[1].rstrip(".")) for l in base.split("\n") if l.startswith("## "))
        new = rebind(letter, RW, base)
        assert new != base
        assert outside(new) == outside(base), "%s: a line outside the opening and section 2 changed" % name
        assert len(CB.bound_blocks(new.split("\n"))) == 1
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f: cur = f.read()
        if cur == new: print("rebind: %-3s already this script's output" % letter.upper())
        elif cur == base: todo[os.path.join(ROOT, rel)] = new
        else: refused.append(rel)
    if refused:
        print("rebind: REFUSED, edited since %s and not this script's output: %s. Nothing written; use "
              "constraints_bound.py --emit and edit the sheet" % (BASE, ", ".join(refused)))
        return 2
    if "--dry-run" in argv:
        for p, new in todo.items(): print("would write %s (%d lines)" % (os.path.relpath(p, ROOT), new.count("\n")))
        return 0
    for p, new in todo.items():
        with open(p, "w", encoding="utf-8") as f: f.write(new)
    bad = []
    for letter in RW.ORDER:
        r = CB.judge(letter, ROOT, RW)
        bad += r["fails"]
        print("rebind: %-3s %d check(s), %d failed" % (letter.upper(), r["checked"], len(r["fails"])))
    for b in bad: print("  FAIL %s" % b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
