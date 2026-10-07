#!/usr/bin/env python3
"""apply_l4small_b2.py: register task L4A-80 (RE-18 and HO-G, cx46's item 18) on the files whose B2 wording is not yet swept
(MESHSAT-1357, worker W133, branch fnd/l4small, 7 October 2026). UNAPPLIED on its branch: the two drafts below are pinned by
l4e7_p0sol.out and l9t5_connected.out, which set 32 (fnd/int32) regenerates, so the set 33 integrator runs this and then regenerates
those outputs.

WHAT IT DOES, for SESSION decision L4E7-D1 (record l4e7, `B2-PRESENCE.md` section 8: no presence-pair route is taken up):
  apply_gen_sch_e_p0sol_b2.py  the refusal that said "P0-7's route B2 waits on the owner's ruling and an accepted check" (the one
                               owner-request wording left in record l4e7's files) is gone, and the draft now refuses the tree's
                               generator ALWAYS, whatever record l4e7's RELEASE.md says: a RELEASE.md written for the record's
                               baseline drafts (the C2 sense, R-240) would otherwise also have released this withdrawn draft. The
                               separate check (l4e7_p0sol.py ORDER_E_B2) composes it on scratch copies only, which this never gates.
                               Docstring and header comment restated to match (same line count).
  NOT here: the docstring sentence of record l9t5's applied change-list draft apply_l4e9_changelist_p0.py ("route B2 an
                               unapproved PARTIAL proposal", the DESK gate assessment's A1.5 and K-24) is record l4k's K-24
                               (fnd/l4k, records/l4k/apply_l4k_changelist.py), which marks it as the text of 7070f106; this
                               stream does not edit it a second time (the two edits would refuse each other).
No circuit, net, part or figure changes; no draft is applied. Nothing in this kit has been built, bought, powered or measured.
Engine and its checks E1 to E6: v2/docs/records/l4small/l4small_edit.py.
Usage:  apply_l4small_b2.py [ROOT] [--check | --write]   (default ROOT: this tree; default --check: nothing is written)
Exit 0: checked or written; 2: usage; 3: refused (already applied, an anchor missing or not unique, or the result does not parse)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l4small"))
import l4small_edit as E  # noqa: E402

NAME = "apply_l4small_b2"
B2D = "v2/docs/records/l4e7/apply_gen_sch_e_p0sol_b2.py"
D = "SESSION L4E7-D1"

OLD_RELEASED = '''def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; P0-7's route B2 waits on the owner's ruling and an accepted check")
    lines = [l.rstrip("\\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])
'''
NEW_RELEASED = '''def released():
    """SESSION L4E7-D1 (7 October 2026, B2-PRESENCE.md section 8): no presence-pair route is taken up, so this WITHDRAWN draft is
    never released onto the repository's own generator. Record l4e7's RELEASE.md releases the record's other drafts and is not
    read here: before L4E7-D1 a RELEASE.md written for the baseline's C2 sense (R-240) would have released this draft too.
    The separate check composes the draft on scratch copies only (l4e7_p0sol.py ORDER_E_B2), which this function never gates.
    Before L4E7-D1 this function read RELEASE.md's first line ("released: yes") and one accepted check named in it; that guard is
    kept in the history of this file (its commit before stream l4small's apply script), not as a route. To reverse: reverse
    L4E7-D1 first (a presence-pair route taken up as a new route with its own check, B2-PRESENCE.md section 5b's detection and
    INP protection drafted, composed and mutated), then restore the RELEASE.md guard from this file's history; until then every
    call of this function on the repository's own generator ends the run with exit 3 and the message below, so no route B2
    edit can reach gen_sch_e.py through this script.
    """
    refuse("NOT RELEASED: route B2 is UNSELECTED and WITHDRAWN AS DRAFTED and no presence-pair route is taken up "
           "(SESSION L4E7-D1, B2-PRESENCE.md section 8): no RELEASE.md releases this draft onto the tree's generator")
'''

EDITS = [
    (B2D, "kept as the record of the route and for its separate check only. No owner item",
          "kept as the record of the route and for its separate check only (%s, 7 October 2026: no presence-pair route is taken "
          "up, so the tree's generator is refused whatever RELEASE.md says). No owner item" % D, True),
    (B2D, "or the repository's own generator is named before RELEASE.md releases it).",
          "or the repository's own generator is named, which is refused always since %s)." % D, False),
    (B2D, "# gen_sch_e.py is refused until RELEASE.md beside this script reads \"released: yes\" on its first line and names an "
          "accepted check\n# (\"check: <repository path whose first line is 'accepted: yes'>\"). A copy elsewhere may be written "
          "(the tests do).\n",
          "# gen_sch_e.py is refused ALWAYS (%s, 7 October 2026, B2-PRESENCE.md section 8: no presence-pair route is taken up),\n"
          "# whatever record l4e7's RELEASE.md says (it releases the record's other drafts). A copy elsewhere may be written (the "
          "tests do).\n" % D, False),
    (B2D, OLD_RELEASED, NEW_RELEASED, False),
]

if __name__ == "__main__":
    sys.exit(E.main(NAME, HERE, EDITS))
