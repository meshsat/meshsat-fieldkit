#!/usr/bin/env python3
"""Draft for the owner of v2/docs/TEST-PLAN.md (stream w4dp, MESHSAT-1357, 27 September 2026).

WHY. `pcb_pack_protection.yaml` now carries BAT-001's hardware level as five rows (`level: hardware`, S-45), and
tests/test_pack_protection.py holds every row of the table to TEST-PLAN.md by name, so section 5 gains rows 10 to 14 and
its closing paragraph, which said the second level's parts "are not rows of the table above", is brought to the table.
The gauge's rows 1 to 9 are untouched. Nothing below has been run; the numbers are the makers' (the table's own rows).

Usage: patch_test_plan.py <tree root holding v2/>     edits by asserted old text; refuses a file that changed under it."""
import os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
P = os.path.join(ROOT, "v2", "docs", "TEST-PLAN.md")
s = open(P, encoding="utf-8").read()

ANCHOR = ("| 9 | **precharge window**: a deeply discharged cell is charged at full current, or a dead cell is charged at all | "
          "1 to 3 V | 1.00 to 3.00 V, Pack Design Guideline, pre-charging voltage range | a block brought to 2.5 V per cell: "
          "the gauge pre-charges at about 1 A and does not raise the current until every cell is above 3.00 V; a block below "
          "1.00 V per cell is not charged at all and the gauge says so | protection | REQ-044 |\n")
ROWS = (
    "| 10 | **second level cell over voltage**: a cell is charged above its own charging voltage and the gauge has not "
    "stopped it | device U2 (BQ7720700): 4.325 V, 1 s (+-20 mV from 0 to 60 C, +-50 mV from -40 to 110 C; 1 s +-150 ms); "
    "COUT fires F2 once JP1 is closed | 4.20 V, 3.2 Charging Voltage, with a 0.175 V allowance so the second level clears "
    "the gauge's own 4.25 V trip at every corner | JP1 open and the gauge on TI's shipped image (FETs held off, so it "
    "cannot latch 2LVL): a 4S string simulator on J_CELL at 3.70 V per cell, one cell raised in 5 mV steps: TP11 (FUSE_G, "
    "COUT through R29) goes high with that cell between 4.305 and 4.345 V at room temperature, 0.85 to 1.15 s after the "
    "step that crosses it, and falls again once the cell is back 100 mV lower; F2 untouched because JP1 is open | "
    "protection | REQ-044 |\n"
    "| 11 | **second level cell under voltage**: a cell is discharged below the voltage the cell maker sets for "
    "over-discharge protection and the gauge has not stopped it | device U2: 2.25 V, 1 s (+-50 mV); DOUT holds the "
    "discharge FET off through Q5, the fuse is not fired | 2.30 V, Pack Design Guideline, NCA/NCM min. voltage of "
    "over-discharging protection: NOT MET, the trip is 2.20 to 2.30 V (finding W4DP-F1, open) | JP1 open, the gauge on "
    "TI's shipped image: the string simulator at 3.70 V per cell, one cell lowered in 5 mV steps: Q5's gate (DOUT) goes "
    "high with that cell between 2.20 and 2.30 V, 0.85 to 1.15 s after the step that crosses it, Q2's gate (DSG_G, read on "
    "R18's FET-side pad) is held at VSS, and DOUT falls again once the cell is back above about 2.35 V | protection | "
    "REQ-044 |\n"
    "| 12 | **second level over temperature**: the cells are hotter than the cell maker allows and the gauge has not "
    "stopped it | device U2: 70 C, 4 s on its own 103AT-2 (J_TS2), 62.7 to 77.5 C at its network; no cold trip | -10 to "
    "60 C, 3.12 Operating Temperature: NOT MET, the level acts only above the cells' limit (finding BAT-F16, open) | P10 "
    "(section 7) | protection | REQ-044 |\n"
    "| 13 | **fuse over current discharge**: the pack delivers more than the cells are rated for, continuously, and the "
    "gauge has not stopped it | F1, the 25 A MINI blade: holds 27.5 A (110 %) for 360,000 s at least, opens 33.75 A (135 %) "
    "in 0.75 to 600 s (Littelfuse 297); F2 is 30 A | 8.0 A per cell (24 A at 3P), 3.8 Max. Discharge Current: NOT MET, "
    "no element that acts without firmware opens at or below 24 A (finding W4DP-F2, open) | on a spare holder, F1 samples "
    "of the fitted lot on a current source with a thermocouple on the blade: at 24 A for one hour none opens; at 33.75 A "
    "each opens within 600 s and at 50 A within 5 s | protection | REQ-044, REQ-045 |\n"
    "| 14 | **fuse short circuit discharge**: a short across the pack terminal with the protection FETs failed closed | F1: "
    "150 A (600 %) opens in 0.030 to 0.100 s; about 10.9 ms at the lowest prospective fault, 240 A (625 A2s typical); 1000 A "
    "interrupting at 32 VDC | the prospective fault at this node, 240 to 480 A (pcb_energy_chain.yaml, PACK_CELLS) | on a "
    "sacrificial board P with Q2 bypassed by a link (a welded discharge FET), a bolted short through a 1 mOhm shunt on a "
    "charged block behind a fire blanket: F1 opens and clears within 100 ms, F2's element is intact afterwards (its "
    "resistance logged before and after), and no cell vents | protection | REQ-044, REQ-045 |\n")
OLD = ("**And the one this table cannot test.** BAT-001 asks for protection in hardware INDEPENDENT OF ANY\n"
       "SOFTWARE. Every function above is the gauge's, whose thresholds live in data flash. **Corrected 26 September 2026\n")
NEW = ("**Rows 10 to 14 are the hardware level (27 September 2026, S-45).** BAT-001 asks for protection in hardware\n"
       "INDEPENDENT OF ANY SOFTWARE, with the trip points set from the cell maker's own limits. Rows 1 to 9 are the gauge's,\n"
       "whose thresholds live in data flash; rows 10 to 14 are the parts that act with no firmware (U2, and F2 through JP1\n"
       "and Q3; Q5; F1), judged by `pack_protection.py` against the same cell limits. Three of them do not meet the\n"
       "requirement's words (rows 11, 12 and 13: W4DP-F1, BAT-F16, W4DP-F2), which is a design finding and not a bench\n"
       "result, and the gate reads FAIL on them until the circuit or an owner's acceptance answers each. **Corrected 26 September 2026\n")
OLD2 = ("(`gen_sch_p.py` lines 243, 288 and 414 to 502). Those need no firmware, and they sit beyond the gauge's thresholds\n"
        "rather than beside them, so they are not rows of the table above; their bench checks are items of the battery review\n"
        "packet (`review-packets/battery/PROTECTION-ARCHITECTURE.md`, its commissioning readings O-9 among them, and\n")
NEW2 = ("(`gen_sch_p.py` lines 243, 288 and 414 to 502). Those need no firmware, and they sit beyond the gauge's thresholds\n"
        "rather than beside them; since 27 September 2026 they are rows 10 to 14 of the table above, and their other bench\n"
        "checks are items of the battery review packet (`review-packets/battery/PROTECTION-ARCHITECTURE.md`, its\n"
        "commissioning readings O-9 among them, and\n")
for old, new in ((ANCHOR, ANCHOR + ROWS), (OLD, NEW), (OLD2, NEW2)):
    if s.count(old) != 1: sys.exit("TEST-PLAN.md changed under this draft: %r found %d times" % (old[:70], s.count(old)))
    t = s.replace(old, new)
    assert t != s
    s = t
for fid in ("second level cell over voltage", "second level cell under voltage", "second level over temperature",
            "fuse over current discharge", "fuse short circuit discharge", "decision 40"):
    assert fid in s.lower(), fid
open(P, "w", encoding="utf-8").write(s)
print("patched", P)
