#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026), after stream w4dp's drafts: the handover's
questions carry what the stream answered and found, where the stream left them for the handover owner (its open items):
  - ENGINEERING-QUESTIONS.md EQ-19's attempts row gains boards D and P (their PWR-001 declarations) after board E's, and
    names S-76 closed;
  - EQ-10's exact issue gains W4DP-F1 and W4DP-F2 beside BAT-F16, the three hardware functions BAT-001's table now
    judges and finds short of the cell maker's limits, for the qualified battery review first;
  - the stream's README (filed as its record) gains the independent check's correction of derate's unrated list.
Idempotent by marker. Usage: fixes_w4dp_r8int6.py <repo root> <kit dir>"""
import json, os, sys

T, K = sys.argv[1:3]
ids = json.load(open(os.path.join(K, "ids.json")))
EQ = os.path.join(T, "v2/docs/handover/ENGINEERING-QUESTIONS.md")
t = open(EQ, encoding="utf-8").read(); o = t
M1 = "**Boards D and P (stream w4dp, 27 September 2026):**"
if M1 not in t:
    a = "S-76's board E half answered. |"
    assert t.count(a) == 1, "EQ-19: board E's sentence is not there (apply stream w4ae first)"
    t = t.replace(a, a[:-2] + " " + M1 + " board D's RLY_K a declared node at 6.5 V, with D2 given LCSC C81598 and its "
                  "maker's sheet filed (%s, %s); board P's BAT_F, VCC_F, SEC_VDD, SW and SCP_HTR declared rails and PBI, "
                  "CELL1 to CELL3, FUSE_G and FUSE_GQ nodes, the fuse gate bounded by TI's 6 V drive (%s); PWR-001 read PASS "
                  "of 7 on D and PASS of 11 on P in the stream's scratch, and S-76 is closed with both halves. |"
                  % (ids["SC_D2"], ids["SC_PWR_DP"], ids["SC_PWR_DP"]))
M2 = "Since stream w4dp (27 September 2026, "
if M2 not in t:
    a = "F2's rating is EQ-07. |"
    assert t.count(a) == 1, "EQ-10's exact issue moved"
    t = t.replace(a, "F2's rating is EQ-07. " + M2 + ids["S_BAT001_HW"] + "): BAT-001's table judges the parts that act "
                  "without firmware against the cell maker's limits, and three of the five functions miss them: under-voltage "
                  "(W4DP-F1, the BQ7720700's 2.25 V against the guideline's 2.30 V), over-current (W4DP-F2, nothing that acts "
                  "without firmware opens at or below 24 A at 3P) and over-temperature (BAT-F16), for this review first. |")
if t != o:
    open(EQ, "w", encoding="utf-8").write(t); print("fixes_w4dp: EQ-19 and EQ-10 carry stream w4dp's answers and findings")
RD = os.path.join(K, "README.md")
r = open(RD, encoding="utf-8").read()
M3 = "## Corrected at integration (r8int6): derate's unrated list"
if M3 not in r:
    r = r.rstrip("\n") + ("\n\n" + M3 + "\n\nThe independent check (w4dp check 2, an AI check) read derate's unrated list on "
        "board P as C1 to C9, C13 to C19, D2, D3, F1 and F2: of the fuse-gate parts only C19 is on it, and R29 to R32, JP1 "
        "and Q3 are not rated kinds, so derate never looks at them. Where this record says they are among derate's unrated "
        "parts, that is the correction; its conclusion, that the lower fuse-gate bound moves no derate count, stands.\n")
    open(RD, "w", encoding="utf-8").write(r); print("fixes_w4dp: the README carries the derate correction")
