#!/usr/bin/env python3
"""LAYER-STATUS.md's layer 3 gate row "An independent check accepts the handover" brought current (MESHSAT-1357, layer 3
round 4, 30 September 2026; set 16's integration check, minor 1): the row still read NOT MET and cited CHECK-1 to
CHECK-3, while CHECK-5 of L3-R2 accepted the handover as prepared with the six owner decisions pending and l3r2.yaml's
`independent_check` names it ACCEPTED. Round 4b (CHECK-1 of round 4, minor 4): the paragraph "Whose each remaining item
is" on the same page no longer lists the independent check of L3-R2 as remaining.

The edits replace that row and that one sentence, each located by its own text and asserted to occur exactly once;
nothing else on the page changes. No dash character is written. It refuses unless the accepted check is filed and verified the way the renderer
verifies it (render_l3r2.handover_checks: every record at its sha256/16, each verdict read from its record's first line,
the newest ACCEPTED and naming check-l3r2-5.md), and a second run is refused.

Usage: python3 apply_layer_status_l3_r4.py [--check] [--page PATH]   (--page: a copy of the page, for the tests)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402

sys.path.insert(0, os.path.join(E.TOP, "v2", "docs", "handover", "layer3"))
import render_l3r2 as RL  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/LAYER-STATUS.md")
CHECK = "v2/docs/records/l3r2/checks/check-l3r2-5.md"
OLD = ("| An independent check accepts the handover | NOT MET | the checks CHECK-1 to CHECK-3 of L3-R2 "
       "(`v2/docs/records/l3r2/checks/`) read accepted: no; their findings are answered in rounds 2, 3b and 3c and the "
       "owner's instructions in rounds 3 to 3c, and a further check of the filled issue by a checker who wrote none of "
       "L3-R2 is owed (L3-C27) |")
MARK = "| An independent check accepts the handover | MET for the handover as prepared"
CHECKER = " A checker: the independent check of L3-R2 (L3-C27)."
CHECKER_AT = "The integrator: the scripts and renders on the integration set (L3-C28)."


def new_row(entry):
    return (MARK + ", the six owner decisions pending | CHECK-5 of L3-R2 (`%s`, sha256/16 `%s`) reads accepted: yes for "
            "the handover as prepared at `028531e4` with the six owner decisions pending, and `l3r2.yaml`'s "
            "`independent_check` names it ACCEPTED; CHECK-1 to CHECK-4 did not accept it, their findings answered in rounds 2, "
            "3b, 3c and 3d, and CHECK-5's minors are answered in round 3e (L3-C27) |" % (CHECK, entry["sha16"]))


def edits(entry):
    """(old, new) pairs: the gate row, and the remaining-items sentence that named the check."""
    return [(OLD, new_row(entry)), (CHECKER_AT + CHECKER, CHECKER_AT)]


def build(t):
    if MARK in t: E.refuse("the page already carries %r: this script has run" % MARK)
    if t.count(OLD) != 1: E.refuse("the page does not carry the row CHECK-1 to CHECK-3 left once (%d)" % t.count(OLD))
    if t.count(CHECKER_AT + CHECKER) != 1: E.refuse("the page does not carry the remaining-items sentence on the check once")
    data = RL.load_data()
    try:
        chks = RL.handover_checks(data)
    except RL.RenderError as e:
        E.refuse("l3r2.yaml's independent_check does not verify: %s" % e)
    if not RL.handover_accepted(data): E.refuse("the newest check of L3-R2 is not ACCEPTED")
    last = chks[-1]
    if str(last["record"]) != CHECK: E.refuse("the newest check is %s, not %s" % (last["record"], CHECK))
    out = t
    for old, new in edits(last):
        for d in E.DASHES:
            if d in new: E.refuse("an edit carries a dash character")
        out = out.replace(old, new)
    back = out
    for old, new in reversed(edits(last)):
        back = back.replace(new, old, 1) if new != CHECKER_AT else back.replace(CHECKER_AT, CHECKER_AT + CHECKER, 1)
    if back != t: E.refuse("the page outside the replaced row and sentence moved")
    return out


def main(argv):
    page = argv[argv.index("--page") + 1] if "--page" in argv and argv.index("--page") + 1 < len(argv) else PAGE
    t = open(page, encoding="utf-8").read()
    try:
        new = build(t)
    except E.Refused as e:
        print("apply_layer_status_l3_r4: REFUSED: %s" % e)
        return 2
    print("apply_layer_status_l3_r4: the independent-check row restated and the remaining-items sentence on it dropped%s" % (" (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(page, "w", encoding="utf-8").write(new)
        print("apply_layer_status_l3_r4: written %s" % os.path.relpath(os.path.abspath(page), E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
