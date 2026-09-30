#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to L3-R2's round 3c (MESHSAT-1357, 30 September 2026), on CHECK-3 of L3-R2 minors 1
and 4: appendix A.3's integrator line says what the scripts enforce instead of "coherent by construction", and finding
F-01 states the history of stream r11dep's record as it is (checked once and not accepted, then answered).

Every edit replaces a sentence an earlier script wrote, located by its own text and asserted to occur exactly once;
nothing else on the page changes (the page outside the replaced sentences is compared). No dash character is written. It
refuses unless apply_layer_status_l3_r3b.py has run, and a second run is refused.

Usage: python3 apply_layer_status_l3_r3c.py [--check]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3edit as E  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "checked once and not accepted, then answered"
EDITS = [
    ("the six owner rows prepared as `v2/docs/records/l3r2/conditional/od_l3_1.py` to `od_l3_6.py`, not applied, coherent "
     "by construction;",
     "the six owner rows prepared as `v2/docs/records/l3r2/conditional/od_l3_1.py` to `od_l3_6.py`, not applied, each "
     "refusing or recording a conflict on the combinations closure item L3-C32 names, and no other combination claimed "
     "coherent;"),
    ("(its author's record, not yet checked, finds L1 past its saturation current at the 9 V floor and the FETs' thermal "
     "path not established)",
     "(stream r11dep's record, " + MARK + " in its second issue, finds L1 past its saturation current at the 9 V floor and "
     "the FETs' thermal path not established; that issue's check is reported accepted and is filed with the power path's "
     "check)"),
]


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    if "the steady-state range with its brackets" not in t: E.refuse("apply_layer_status_l3_r3b.py has not run on this page")
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
        print("apply_layer_status_l3_r3c: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r3c: %d sentences restated%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(PAGE, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r3c: written %s" % os.path.relpath(PAGE, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
