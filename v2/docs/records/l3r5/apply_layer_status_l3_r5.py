#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to round 5 (MESHSAT-1357, 30 September 2026), on the owner's reviewer's review of
the decision brief (owner ruling D-26) and on the owner's addendum (D-27): row L3-OD7, M1's runtime, joins the gate's
first two conditions ahead of the six rows; the gate's first condition reads the target unambiguous on a combination whose
requirements do not contradict (a target the studied candidate does not meet is valid and records a feasibility item);
the gate gains its fifth condition, every recorded target with a feasibility disposition; the independent check's row
says that the decided issue is checked again; the closure paragraph's round 3b rules are followed by the rules that
replace them; and the page states which of the reviewer's three status levels holds.

Every edit replaces a text an earlier script wrote, located by its own text and asserted to occur exactly once; nothing
else on the page changes. No dash character is written. It refuses unless D-26 and D-27 are in the registry, and a
second run is refused.

Usage: python3 apply_layer_status_l3_r5.py [--check] [--page PATH]   (--page: a copy of the page, for the tests)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "| Every recorded target has a feasibility disposition (D-26) |"
LEVEL = ("\n**Status level (the owner's reviewer's three, D-26).** At this writing none holds: \"requirements drafted / "
         "decisions recorded\" needs the seven rows decided (row L3-OD7, M1's runtime, first, D-27; row L3-OD2 does not "
         "apply after a reject) and applied by their "
         "scripts, with the acceptance definitions written into the requirements they define; \"requirements baseline "
         "validated and accepted\" needs the five conditions above MET, the definition re-issue approved (L3-C26) and the "
         "owner's acceptance of the baseline; \"design and hardware compliant\" is a later layers' target. The live "
         "statement is `REQUIREMENTS-L3-R2.md` section 2.\n")
EDITS = [
    ("`OWNER-DECISIONS-L3.md` (the six rows the owner decides, board A's current-limit resistor as two results, row "
     "L3-OD6's options table and the combinations the evidence covers)",
     "`OWNER-DECISIONS-L3.md` (the rows the owner decides, row L3-OD7 on M1's runtime first since D-27 and then the six "
     "of layer 3's target, board A's current-limit resistor as two results, row L3-OD6's options table, the acceptance "
     "definitions, the feasibility items and the requirements that cannot both hold)"),
    ("| The target is unambiguous | NOT MET | the owner's rows L3-OD1 to L3-OD4 and L3-OD6 (",
     "| The target is unambiguous | NOT MET | the owner's row L3-OD7 (M1's runtime, answered first, D-27) and rows L3-OD1 "
     "to L3-OD4 and L3-OD6 ("),
    ("| The requirement-changing owner decisions are resolved | NOT MET | the six rows L3-OD1 to L3-OD6, each carrying the "
     "figures of the checked basis",
     "| The requirement-changing owner decisions are resolved | NOT MET | the seven rows: L3-OD7 (M1's runtime and its "
     "store, with HF and the tablet kept, D-27), filled from the runtime and battery comparison of stream l3batt "
     "(fnd/l3batt 83577a13, its CHECK-2 accepted), and L3-OD1 to L3-OD6, each carrying the figures of the checked "
     "basis"),
    ("decided on a combination the evidence covers,",
     "decided on a combination whose requirements do not contradict (D-26: a target the studied candidate does not meet "
     "is valid and records a feasibility item),"),
    ("round 3e (L3-C27) |",
     "round 3e (L3-C27); once a row is decided, the decided issue is checked again (D-26) |\n" + MARK + " NOT MET | each "
     "decided row's option with its disposition (a credible route, inconclusive with the evidence named, or no route "
     "with a quantified trade-off returned to the owner) and each feasibility item its answer records (FI-01 to FI-06) "
     "not owed, on stream l3feas's bounded feasibility record bound to its checked tip (`l3r2.yaml` feasibility_basis, "
     "CHECK-2 of stream l3feas accepted; L3-C54) |"),
    ("a combination these rules do not name is not claimed coherent.",
     "a combination these rules do not name is not claimed coherent. Since round 5 (D-26, `v2/docs/records/l3r5/`) "
     "those rules are replaced: an answer records the owner's target, and a target the studied candidate does not meet "
     "(a lid that does not carry the store, both lid items kept, a coverage target, row L3-OD1's reject) records its "
     "feasibility item instead of a conflict; since D-27 row L3-OD7 (M1's runtime and its store) is answered first, rows "
     "L3-OD1, L3-OD2, L3-OD4 and L3-OD6 refuse until it is, and row L3-OD6 also after 48 hours or HF listening until its "
     "table is restated from the runtime comparison; both lid items kept, the owner's stated wish, is never refused; "
     "row L3-OD2 needs row L3-OD1 approved, row L3-OD3 needs it answered either "
     "way, and row L3-OD4 needs rows L3-OD1 to L3-OD3 answered (row L3-OD2 where it applies), its adopt no particular "
     "answer of them or of row L3-OD6; only requirements that cannot both hold are "
     "refused: row L3-OD2 after row L3-OD1's reject, row L3-OD6 beside row L3-OD7's 48 hours or HF listening, and the "
     "QMX out beside HF listening (closure item L3-C32; "
     "`OWNER-DECISIONS-L3.md` lists the rules)."),
    ("\n**What the session closed (30 September 2026, `v2/docs/records/l3r2/`).**",
     LEVEL + "\n**What the session closed (30 September 2026, `v2/docs/records/l3r2/`).**"),
]


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    d = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    if not any(r["id"] == "D-26" for r in d["owner_rulings"]): E.refuse("D-26 is not in the registry: run apply_l3r5_d26.py first")
    if not any(r["id"] == "D-27" for r in d["owner_rulings"]): E.refuse("D-27 is not in the registry: run apply_l3r5_d27.py first")
    out = t
    for old, new in EDITS:
        for dch in E.DASHES:
            if dch in new: E.refuse("an edit carries a dash character")
        if out.count(old) != 1: E.refuse("the page does not carry %r once (%d)" % (old[:70], out.count(old)))
        out = out.replace(old, new)
    back = out
    for old, new in reversed(EDITS): back = back.replace(new, old)
    if back != t: E.refuse("the page outside the replaced texts moved")
    return out


def main(argv):
    page = argv[argv.index("--page") + 1] if "--page" in argv and argv.index("--page") + 1 < len(argv) else PAGE
    t = open(page, encoding="utf-8").read()
    try:
        new = build(t)
    except E.Refused as e:
        print("apply_layer_status_l3_r5: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r5: %d texts restated%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(page, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r5: written %s" % os.path.relpath(os.path.abspath(page), E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
