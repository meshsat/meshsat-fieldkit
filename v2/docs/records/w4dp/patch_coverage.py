#!/usr/bin/env python3
"""Draft for the owner of v2/ecad/tools/pcb_rules_coverage.yaml (stream w4dp, MESHSAT-1357, 27 September 2026).

WHY. BAT-001's note still says "no second protector IC, no chemical fuse ... the PTC input is tied off" and that the remedy
is owner decision 40, which was ruled on 26 September 2026 and has been in board P's schematic since faf8c981; its FAIL
now has other reasons (pcb_pack_protection.yaml's hardware level, SC-c of drafts/w4dp/apply_registry.py). PWR-001's note
lists board D's RLY_K and board P's five undeclared and six undecided nets, which w4dp declares. Both notes gain a dated
sentence; nothing earlier is removed (the notes are the rule's history). BAT-001's remediation owner stays OWNER.

Usage: patch_coverage.py <tree root holding v2/>     edits by asserted old text; commit the file BEFORE rules_status runs
(an uncommitted configuration input reads CONFIG_CHANGED)."""
import os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
P = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_rules_coverage.yaml")
s = open(P, encoding="utf-8").read()

EDITS = [
 ("Reading unchanged: FAIL, 1 of 45 checks (no protection independent of software).\",",
  "Reading unchanged: FAIL, 1 of 45 checks (no protection independent of software). 27 September 2026 (stream w4dp, S-45 "
  "closed): THE TABLE DESCRIBES THE DRAWN CIRCUIT. Decision 40 was ruled on 26 September 2026 and board P carries its floor "
  "since faf8c981 (the BQ7720700 second level, the SCF9550 chemical fuse driven by its COUT and the gauge's FUSE through "
  "JP1 and Q3, the under-voltage hold Q5 on the discharge FET, the PTC element RT1 with PTCEN on BAT), and "
  "pcb_pack_protection.yaml now declares it present with its parts, each on the netlist, while "
  "tests/test_pack_protection.py holds the declaration to the netlist's connections both ways. The five functions are also "
  "judged on the parts that act without firmware (`level: hardware` rows) against the same cell limits, which keeps the "
  "requirement's words literal: over-voltage (U2, 4.325 V against 4.20 V with a 0.175 V allowance) and short circuit (F1, "
  "150 A against 240 A) pass; under-voltage (U2, 2.25 V against 2.30 V: W4DP-F1), over-temperature (U2, 70 C and no cold "
  "trip against -10 to 60 C: BAT-F16) and over-current (F1, 33.75 A against 24 A at 3P: W4DP-F2) fail. Reading on board P "
  "as regenerated, in scratch: FAIL, 3 of 63 checks, each a hardware row naming its open finding.\","),
 ("action: \"DONE 18 September 2026 for the derivation half: the cell's specification is in the tree, the threshold table "
  "is derived from it and gated, and every function carries its prototype test. What remains is the owner's: decision 40,",
  "action: \"27 September 2026: decision 40 is ruled and in the schematic, and the table judges the parts it added; what "
  "remains is the three hardware functions that miss the cell maker's limits (the open item drafts/w4dp/apply_registry.py "
  "calls S-x: a custom or different second level for under-voltage, the comparator hold of THERMAL-COORDINATION.md section "
  "8 for over-temperature, a fixed discharge over-current for over-current, or the owner restating BAT-001 for a second "
  "level), put to the qualified battery reviewer first because the circuit is frozen in front of that review. Earlier: "
  "DONE 18 September 2026 for the derivation half: the cell's specification is in the tree, the threshold table "
  "is derived from it and gated, and every function carries its prototype test. What remains is the owner's: decision 40,"),
 (" The session decisions TSN-D1 to TSN-D29 are filed as v2/docs/records/ts-net/ts-net-decisions.md.\"}",
  " The session decisions TSN-D1 to TSN-D29 are filed as v2/docs/records/ts-net/ts-net-decisions.md. BOARDS D AND P "
  "(stream w4dp, 27 September 2026): board D's D2 carries its order code and its maker's sheet (LCSC C81598, SEMTECH "
  "ELECTRONICS 1N4148W, v2/vendor/power/st-semtech-1n4148w-c81598.pdf) and RLY_K is a declared node at 6.5 V (+5V_TX plus "
  "the sheet's 1.25 V at 150 mA); board P declares BAT_F, VCC_F, SEC_VDD, SW and SCP_HTR as rails and PBI, CELL1 to CELL3, "
  "FUSE_G and FUSE_GQ as nodes, each from the BQ4050, BQ7720700, SCF9550 and its own parts' figures, with no net, pin or "
  "part moved. PWR-001 read in scratch on the regenerated netlists: board D PASS of 7 checks (0 undecided), board P PASS "
  "of 11 (10 declared rails, 7 declared nodes, 0 undecided). Board E's FAN1_SW and FAN2_SW stay UNDECIDED (S-76).\"}"),
]
for old, new in EDITS:
    if s.count(old) != 1: sys.exit("pcb_rules_coverage.yaml changed under this draft: %r found %d times" % (old[:70], s.count(old)))
    t = s.replace(old, new); assert t != s; s = t
open(P, "w", encoding="utf-8").write(s)
import yaml; yaml.safe_load(open(P, encoding="utf-8"))
print("patched", P)
