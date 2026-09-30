#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 brought to L3-R2's fill (MESHSAT-1357, 30 September 2026): the checked energy basis and the
checked power path are filed (fnd/l3plane cd8720a1, the energy stream's CHECK-5, accepted), so the rows are no longer held
and finding F-01 states the checked result.

Every edit replaces a sentence an earlier script wrote, located by its own text and asserted to occur exactly once;
nothing else on the page changes. No dash character is written. It refuses unless apply_layer_status_l3_r3c.py has run and
l3r2.yaml names both checked files, and a second run is refused.

Usage: python3 apply_layer_status_l3_fill.py [--check]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "the checked basis at fnd/l3plane cd8720a1"
EDITS = [
    ("the six rows L3-OD1 to L3-OD6; rows L3-OD1, L3-OD2 and L3-OD4 are held by D-22, and row L3-OD6's recommendation and "
     "figures by D-23, until the energy basis is filed",
     "the six rows L3-OD1 to L3-OD6, each carrying the figures of " + MARK + " (the energy stream's CHECK-5, accepted), "
     "which lifted the holds of D-22, D-23 and D-24"),
    ("the first check (`v2/docs/records/l3r2/checks/check-l3r2-1.md`) reads accepted: no; its findings are answered in "
     "round 2 and the owner's instructions in round 3, and a further check",
     "the checks CHECK-1 to CHECK-3 of L3-R2 (`v2/docs/records/l3r2/checks/`) read accepted: no; their findings are "
     "answered in rounds 2, 3b and 3c and the owner's instructions in rounds 3 to 3c, and a further check of the filled "
     "issue"),
    ("Which lid option meets M1 across the kit's supply range, and on which planes, is stated only from the checked energy "
     "basis (S-127) and the checked power path (L3-C45); until then no energy figure on the L3 pages is the design's "
     "(`L3-RECONCILIATION.md` (a)).",
     "On " + MARK + ": as drawn, and in the derated variant now at 4.00 A, every lid fails M1 on the reference day; the "
     "resistor-only proposal is inconclusive; only on the hypothetical corrected path do the 4S14P and 4S15P lids meet at "
     "nominal inputs, and at the worst established inputs the 4S15P lid meets in both array builds on the combined line "
     "while failing at U3's 6.0 A bracket in WAB, and the 4S14P lid fails in WAB; no plane band exists at U3's 6.0 A "
     "bracket; every coverage target of 50 percent or more needs more cells than any established arrangement holds "
     "(`L3-RECONCILIATION.md` (a), finding F-01). No figure is demonstrated capability."),
    ("The owner: rows L3-OD1 to L3-OD6 (`OWNER-DECISIONS-L3.md`), rows 1, 2, 4 and 6 after the energy basis. Stream "
     "l3plane and an independent checker: the energy basis and its check (S-127, L3-C31), its second round with row "
     "L3-OD6's figures (the store each weather option needs, its mass and volume, and whether it fits the case); stream "
     "r11dep and its independent check: the power path at Option A(i)'s currents (L3-C45).",
     "The owner: rows L3-OD1 to L3-OD6 (`OWNER-DECISIONS-L3.md`), all six with the checked figures. The session: S-127 "
     "closed in the registry with REQ-072 re-read on the filed basis (L3-C31)."),
]


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    if "checked once and not accepted, then answered" not in t: E.refuse("apply_layer_status_l3_r3c.py has not run on this page")
    data = C.l3data()
    for key in ("energy_basis", "power_path_check"):
        ok, why = C.basis_state(data, key=key)
        if not ok: E.refuse("the fill is not done: %s" % why)
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
        print("apply_layer_status_l3_fill: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_fill: %d sentences restated%s" % (len(EDITS), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(PAGE, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_fill: written %s" % os.path.relpath(PAGE, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
