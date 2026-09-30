#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to L3-R2's round 3d (MESHSAT-1357, 30 September 2026), on CHECK-4 of L3-R2 (minor 1
and the S-127 closure): the power-path findings named by their checked classes (A-1 and A-2, B-1 to B-5, C-1 to C-9, at
closure items L3-C37 to L3-C44 and L3-C46 to L3-C53) in place of the first issue's PP-01 to PP-08, and S-127 stated closed.

Every edit replaces a sentence an earlier script wrote, located by its own text and asserted to occur exactly once;
nothing else on the page changes. No dash character is written. It refuses unless apply_layer_status_l3_fill.py has run
and S-127 is closed in the registry, and a second run is refused.

Usage: python3 apply_layer_status_l3_r3d.py [--check]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "the findings A-1 and A-2, B-1 to B-5 and C-1 to C-9"
EDITS = [
    ("with its corrections (PP-01 to PP-08) listed as engineering tasks tracked downstream (L3-C34, L3-C35, L3-C37 to "
     "L3-C44), not layer 3 prerequisites.",
     "with " + MARK + " it assumes closed listed as engineering tasks tracked downstream (L3-C34, L3-C35, L3-C37 to L3-C44 "
     "and L3-C46 to L3-C53), not layer 3 prerequisites."),
    ("The session: S-127 closed in the registry with REQ-072 re-read on the filed basis (L3-C31). Engineering, downstream: "
     "the power-path corrections PP-01 to PP-08 (L3-C37 to L3-C44), not owner decisions.",
     "S-127 is closed in the registry by the session, with REQ-072 re-read on the filed basis (L3-C31, "
     "`v2/docs/records/l3r2/apply_l3r2_s127.py`). Engineering, downstream: the power-path findings A-1 to C-9 (L3-C37 to "
     "L3-C44 and L3-C46 to L3-C53), not owner decisions."),
]


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    if "the checked basis at fnd/l3plane cd8720a1" not in t: E.refuse("apply_layer_status_l3_fill.py has not run on this page")
    d = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    if not any(x["id"] == "S-127" for x in d["closed_items"]): E.refuse("S-127 is not closed: run apply_l3r2_s127.py first")
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
        print("apply_layer_status_l3_r3d: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r3d: %d sentences restated%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(PAGE, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r3d: written %s" % os.path.relpath(PAGE, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
