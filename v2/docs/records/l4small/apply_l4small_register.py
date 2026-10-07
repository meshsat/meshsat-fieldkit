#!/usr/bin/env python3
"""apply_l4small_register.py: W130's correction 2 (its check of the 41 commits that changed cx46-reviewed inputs, register task L4A-86,
`_runs/claude/w130ricverify/REPORT-FULL-AS-RECEIVED.md`, "Corrections needed" item 2, commit bad162ad NOT VERIFIED) on L4-E9's
register (MESHSAT-1357, worker W133, branch fnd/l4small, 7 October 2026). UNAPPLIED on its branch: the set 33 integrator runs it, then
regenerates l4e9_power_path.out (which reads the register).

WHAT IT DOES: R-208's order note read "l8p section 6 item 4, which reads R264 and C264 on the tree's order with the guard, R-222,
before it": R264 and C264 are record l8p's own board A composition only; the connected candidate's full order gives d8dec31's PB network
R603 and C607. The note is restated with W130's words, "(R264 and C264 on record l8p's own board A composition, l8p_drafts.out:N1; R603
and C607 on the connected candidate's full order, l9t5_connected.out:N2)", where N1 and N2 are read at apply time as the lines of those
two outputs that print the readings (on main be07863b: 420 and 79, W130's numbers; on set 32's fnd/int32 the first is 432), so the
citation points at the tree it is written into. No row's kind, state, order or class changes; no figure is new. Nothing in this kit
has been built, bought, powered or measured. Engine and its checks E1 to E6: v2/docs/records/l4small/l4small_edit.py.
Usage:  apply_l4small_register.py [ROOT] [--check | --write]   (default ROOT: this tree; default --check: nothing is written)
Exit 0: checked or written; 2: usage; 3: refused (already applied, an anchor or a cited reading missing or not unique)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l4small"))
import l4small_edit as E  # noqa: E402

NAME = "apply_l4small_register"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
L8P = "v2/docs/records/l8p/l8p_drafts.out"
CON = "v2/docs/records/l9t5/l9t5_connected.out"
OLD = ("(l8p section 6 item 4, which reads R264 and C264 on the tree's order with the guard, R-222, before it; R248 and C247 were "
       "round 1's reading, its section 5 at `515f6cf2`)")
NEW = ("(l8p section 6 item 4 (R264 and C264 on record l8p's own board A composition, l8p_drafts.out:%d; R603 and C607 on the "
       "connected candidate's full order, l9t5_connected.out:%d); R248 and C247 were round 1's reading, its section 5 at `515f6cf2`)")
READ_L8P = "d8dec31/apply_gen_sch_a_mainpb.py"
READ_L8P_AND = "(R264, C264)"
READ_CON = "d8dec31's mainpb, the last next-free taker: R603, C607 on MAIN_PB"


def _line(root, rel, *needles):
    p = os.path.join(root, rel)
    if not os.path.isfile(p):
        raise E.Refused("%s is not in %s" % (rel, root))
    hits = [i + 1 for i, l in enumerate(open(p, encoding="utf-8").read().splitlines()) if all(n in l for n in needles)]
    if len(hits) != 1:
        raise E.Refused("%s prints the reading %r on %d lines, one expected" % (rel, needles[0], len(hits)))
    return hits[0]


def edits(root):
    return [(REG, OLD, NEW % (_line(root, L8P, READ_L8P, READ_L8P_AND), _line(root, CON, READ_CON)), False)]


if __name__ == "__main__":
    sys.exit(E.main(NAME, HERE, edits))
