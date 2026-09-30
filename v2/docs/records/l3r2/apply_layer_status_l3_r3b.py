#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to L3-R2's round 3b (MESHSAT-1357, 30 September 2026), on CHECK-2 of L3-R2 B2 and B4
and the owner's addendum D-24: the coherence sentence says what the gate and the scripts enforce; finding F-01 states the
charge bus's steady-state range with the brackets beside it, as the checked energy basis gives them, and every result on
board A's front end in four cases (D-25 adds the derated variant); the rows wait on the power path's independent check.

Every edit replaces a sentence an earlier script wrote, located by its own text and asserted to occur exactly once;
nothing else on the page changes (the page outside the replaced sentences is compared). No dash character is written. It
refuses unless apply_layer_status_l3_r3.py has run, and a second run is refused.

Usage: python3 apply_layer_status_l3_r3b.py [--check]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "the steady-state range with its brackets"
EDITS = [
    ("The rows are made coherent: row L3-OD1 fixes the store only, row L3-OD3 alone fixes the array, and the scripts and "
     "the gate refuse a combination the evidence does not cover.",
     "The rows are made coherent as far as these rules go, and no further: rows L3-OD2 to L3-OD4 need row L3-OD1 approved; "
     "row L3-OD4's adopt needs row L3-OD3 answered 2s2p, row L3-OD2 not both-kept and row L3-OD6 answered mean-day first; "
     "row L3-OD2's lid must carry the store of row L3-OD6's answer in its build case by the filled table, or an open "
     "conflict is recorded; row L3-OD1 fixes the store only and row L3-OD3 alone the array. The scripts refuse or record a "
     "conflict and the gate reads the set incoherent on each (closure item L3-C32); a combination these rules do not "
     "name is not claimed coherent."),
    ("charge bus (20.7 V); the bus at U3's input is now established at 19.146 / 20.000 / 20.887 V across the in-use "
     "envelope (fact CF-01), and at lower bus voltages",
     "charge bus (20.7 V); the checked energy basis gives the bus at U3's input " + MARK + ": 19.146 / 20.000 / 20.887 V "
     "in steady state across the in-use envelope, and beside it 19.101 V with the divider 20 K warmer (an assumption), "
     "18.782 V with the resistors at their makers' 1000 h endurance limits (a bound, not an expectation) and 18.738 V with "
     "both (fact CF-01); an M1 claim states the brackets beside its result, as the basis does. At lower bus voltages"),
    ("Every Option A(i) result also rests on board A's entry re-rated as drafted (R11 6.2 mOhm): on the circuit as "
     "generated no lid meets M1 (fact CF-02), and the change's implementation and physical verification are downstream "
     "items (L3-C34, L3-C35), not layer 3 prerequisites. Which lid option meets M1 across the kit's supply range, and on "
     "which planes, is stated only from the checked energy basis (S-127);",
     "Every result on board A's front end is stated in four cases (owner rulings D-24 and D-25, fact CF-02): (a) the "
     "circuit as drawn, R11 10 mOhm, where no lid meets M1; (a') a derated variant, U3's input limit at 4.05 A or less, "
     "which fixes current-limit coordination only, not the other findings or M1; (b) the resistor-only proposal, R11 6.2 mOhm, which is not a sufficient "
     "solution (its author's record, not yet checked, finds L1 past its saturation current at the 9 V floor and the "
     "FETs' thermal path not established) and reads INCONCLUSIVE until the electrical check; (c) a hypothetical corrected "
     "power path, on which every Option A(i) figure rests, labelled hypothetical and never demonstrated capability, with "
     "its corrections (PP-01 to PP-08) listed as engineering tasks tracked downstream (L3-C34, L3-C35, L3-C37 to "
     "L3-C44), not layer 3 prerequisites. Which lid option meets M1 across the kit's supply range, and on which planes, "
     "is stated only from the checked energy basis (S-127) and the checked power path (L3-C45);"),
    ("adds row L3-OD6, M1's weather basis, as a quantified choice whose recommendation and figures are held with them, and "
     "asks every row for its options, recommendation, quantified consequences and dependencies. All three are filed in",
     "adds row L3-OD6, M1's weather basis, as a quantified choice whose recommendation and figures are held with them, and "
     "asks every row for its options, recommendation, quantified consequences and dependencies; and his addendum on the "
     "power path (owner ruling D-24) holds the rows until the power path at Option A(i)'s currents is independently "
     "checked and states every result on board A's front end in separate cases, and his corrections (owner ruling "
     "D-25) add a derated variant, class Kelvin sensing as an implementation requirement and ask every owner row to name "
     "the requirement it changes with the consequence quantified. All five are filed in"),
    ("each applied by its prepared script under `v2/docs/records/l3r2/conditional/`, on the checked energy basis (open "
     "item S-127) |",
     "each applied by its prepared script under `v2/docs/records/l3r2/conditional/`, on the checked energy basis (open "
     "item S-127) and the checked power path (L3-C45, D-24) |"),
    ("its second round with row L3-OD6's figures (the store each weather option needs, its mass and volume, and whether "
     "it fits the case).",
     "its second round with row L3-OD6's figures (the store each weather option needs, its mass and volume, and whether "
     "it fits the case); stream r11dep and its independent check: the power path at Option A(i)'s currents (L3-C45). "
     "Engineering, downstream: the power-path corrections PP-01 to PP-08 (L3-C37 to L3-C44), not owner decisions."),
]


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    if "(owner ruling D-23)" not in t: E.refuse("apply_layer_status_l3_r3.py has not run on this page")
    d = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    for rid, s in (("D-24", "apply_l3r2_d24.py"), ("D-25", "apply_l3r2_d25.py")):
        if not any(r["id"] == rid for r in d["owner_rulings"]): E.refuse("%s is not in the registry: run %s first" % (rid, s))
    out = t
    for old, new in EDITS:
        for dch in E.DASHES:
            if dch in new: E.refuse("an edit carries a dash character")
        if out.count(old) != 1: E.refuse("the page does not carry %r once (%d)" % (old[:70], out.count(old)))
        out = out.replace(old, new)
    back = out
    for old, new in EDITS: back = back.replace(new, old)
    if back != t: E.refuse("the page outside the replaced sentences moved")
    return out


def main(argv):
    t = open(PAGE, encoding="utf-8").read()
    try:
        new = build(t)
    except E.Refused as e:
        print("apply_layer_status_l3_r3b: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r3b: %d sentences restated%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(PAGE, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r3b: written %s" % os.path.relpath(PAGE, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
