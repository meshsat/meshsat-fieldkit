#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to L3-R2's third round (MESHSAT-1357, 30 September 2026): the owner's instruction on
the six-row decision table (owner ruling D-23), row L3-OD6, and the facts the first check of the energy basis confirmed.

Every edit replaces a sentence apply_layer_status_l3.py wrote, located by its own text (never a line number) and asserted
to occur exactly once; nothing else on the page changes (the result is compared with the page outside the replaced
sentences). No dash character is written. It refuses unless apply_layer_status_l3.py has run and D-23 is in the
registry, and a second run is refused.

Usage: python3 apply_layer_status_l3_r3.py [--check]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "(owner ruling D-23)"
EDITS = [
    ("holds rows L3-OD1, L3-OD2 and L3-OD4 until a corrected, independently checked energy comparison arrives. Both are "
     "filed in `v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`.",
     "holds rows L3-OD1, L3-OD2 and L3-OD4 until a corrected, independently checked energy comparison arrives; his "
     "instruction on the six-row table the same day " + MARK + " adds row L3-OD6, M1's weather basis, as a quantified "
     "choice whose recommendation and figures are held with them, and asks every row for its options, recommendation, "
     "quantified consequences and dependencies. All three are filed in "
     "`v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`."),
    ("`OWNER-DECISIONS-L3.md` (the five rows the owner decides and the combinations the evidence covers)",
     "`OWNER-DECISIONS-L3.md` (the six rows the owner decides, board A's current-limit resistor as two results, row "
     "L3-OD6's options table and the combinations the evidence covers)"),
    ("the owner's rows L3-OD1 to L3-OD4 (Option A(i)'s store; where the displaced lid item goes and whether its function "
     "stays; the solar input; M1's deployment conditions) decided",
     "the owner's rows L3-OD1 to L3-OD4 and L3-OD6 (Option A(i)'s store; where the displaced lid item goes and whether its "
     "function stays; the solar input; M1's deployment conditions; M1's weather basis) decided"),
    ("the five rows L3-OD1 to L3-OD5; rows L3-OD1, L3-OD2 and L3-OD4 are held by D-22 until the energy basis is filed",
     "the six rows L3-OD1 to L3-OD6; rows L3-OD1, L3-OD2 and L3-OD4 are held by D-22, and row L3-OD6's recommendation and "
     "figures by D-23, until the energy basis is filed"),
    ("its findings are answered in round 2, and a further check",
     "its findings are answered in round 2 and the owner's instructions in round 3, and a further check"),
    ("D-21 and D-22 recorded; S-114 closed (the reconciliation filed and REQ-072 re-read on it)",
     "D-21, D-22 and D-23 recorded; S-114 closed (the reconciliation filed and REQ-072 re-read on it)"),
    ("Every open item is classified by layer, and every item no record waits on carries its disposition (acceptance item "
     "3.15).",
     "Every open item is classified by layer, and every item no record waits on carries its disposition (acceptance item "
     "3.15). In round 3 the first check of the energy basis is filed (`v2/docs/records/l3r2/checks/energy-basis-check-1/`, "
     "accepted: no) and the four facts it confirmed are recorded (`L3-RECONCILIATION.md` (a), CF-01 to CF-04): the charge "
     "bus's range, board A as generated, the September weather record and the relocation facts; every option that "
     "cannot meet M1 is flagged in the table, and row L3-OD2 offers both lid items kept, flagged."),
    ("**Feasibility finding F-01, for the owner.** The two-pack results were computed on the energy model's most favourable "
     "charge bus (20.7 V, above the bus's nominal 20.000 V and its stated band of 19.080 to 20.960 V); at lower bus "
     "voltages, and with U3's 6.0 A bracket, the margins fall, the tablet-out lid's the most.",
     "**Feasibility finding F-01, for the owner.** The two-pack results were computed on the energy model's most favourable "
     "charge bus (20.7 V); the bus at U3's input is now established at 19.146 / 20.000 / 20.887 V across the in-use "
     "envelope (fact CF-01), and at lower bus voltages, and with U3's 6.0 A bracket, the margins fall, the tablet-out "
     "lid's the most. Every Option A(i) result also rests on board A's entry re-rated as drafted (R11 6.2 mOhm): on the "
     "circuit as generated no lid meets M1 (fact CF-02), and the change's implementation and physical verification are "
     "downstream items (L3-C34, L3-C35), not layer 3 prerequisites."),
    ("The owner: rows L3-OD1 to L3-OD5 (`OWNER-DECISIONS-L3.md`), rows 1, 2 and 4 after the energy basis. Stream l3plane "
     "and an independent checker: the energy basis and its check (S-127, L3-C31), and the relocation facts row L3-OD2 "
     "needs.",
     "The owner: rows L3-OD1 to L3-OD6 (`OWNER-DECISIONS-L3.md`), rows 1, 2, 4 and 6 after the energy basis. Stream "
     "l3plane and an independent checker: the energy basis and its check (S-127, L3-C31), its second round with row "
     "L3-OD6's figures (the store each weather option needs, its mass and volume, and whether it fits the case)."),
    ("rows L3-OD1, L3-OD2 and L3-OD4 held by his review D-22.",
     "rows L3-OD1, L3-OD2 and L3-OD4 held by his review D-22; row L3-OD6 added and held by his instruction D-23 (round 3, "
     "`v2/docs/records/l3r2/apply_l3r2_d23.py`)."),
    ("the five owner rows prepared as `v2/docs/records/l3r2/conditional/od_l3_1.py` to `od_l3_5.py`",
     "the six owner rows prepared as `v2/docs/records/l3r2/conditional/od_l3_1.py` to `od_l3_6.py`"),
    ("Owner: the integrator as registry writer; the owner for rows L3-OD1 to L3-OD5.",
     "Owner: the integrator as registry writer; the owner for rows L3-OD1 to L3-OD6."),
]


def build(t):
    if MARK in t: E.refuse("the page already carries %s: this script has run" % MARK)
    if "L3-R2 (30 September 2026" not in t: E.refuse("apply_layer_status_l3.py has not run on this page")
    d = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    if not any(r["id"] == "D-23" for r in d["owner_rulings"]): E.refuse("D-23 is not in the registry: run apply_l3r2_d23.py first")
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
        print("apply_layer_status_l3_r3: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r3: %d sentences restated%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(PAGE, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r3: written %s" % os.path.relpath(PAGE, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
