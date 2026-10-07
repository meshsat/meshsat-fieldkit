#!/usr/bin/env python3
"""K-24 (record l4k, MESHSAT-1357, W131, 7 October 2026): the description of route B2 in the docstring of record l9t5's change-list
applier apply_l4e9_changelist_p0.py brought to the baseline's reading. FOR THE INTEGRATOR, on set 33's integrated tree; not applied
on fnd/l4k.

K-24, standing on main be07863b at one place of the two the assessment cites:
  be07863b:v2/docs/records/l9t5/apply_l4e9_changelist_p0.py:23 "route B2 an unapproved PARTIAL proposal that does not resolve it"
against be07863b:v2/docs/records/l4e7/B2-PRESENCE.md:4 "UNSELECTED and WITHDRAWN AS DRAFTED" (the heading the assessment also cites,
L4E7-P0SOL.md section 4, reads "route B2 (UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline)" since W4's rewrite:
be07863b:v2/docs/records/l4e7/L4E7-P0SOL.md:121). The docstring describes what the applier wrote into L4-E9's generator at set
30's integration commit 7070f106; set 31 restated that generator data (L4-E9's set 31 row 23). The sentence is kept as history
and marked: the applier's data (its PY_EDITS, line 48, the text it applied at 7070f106 and the applied-state reader's subject) is
NOT edited, because it is the record of what was applied.

The rest of route B2's wording in the tree is register task L4A-80's sweep (RE-18 / HO-G), not this record's (never widened here).

Why a script (authority SESSION, W131; reversed by running the edit by hand on set 33's tree): the applier is not changed by set 32,
but its sha256 is pinned by record l9t5's l9t5_connected.out (its input line 13 at be07863b), which set 32 regenerates; the edit is
one docstring line in place (no line moves), the module still parses and its data is unchanged.

Outputs that move after the apply (named for set 33's regeneration): v2/docs/records/l9t5/l9t5_connected.out (the applier's
sha256 line) and the outputs of the l9t5 stability cascade that pin l9t5_connected.out.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _l4k_apply import run  # noqa: E402

CLP = "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py"

OLD = ("     model, the receiving company's engineering item E-1; route B2 an unapproved PARTIAL proposal that does not resolve it; D-16\n"
       "     corrected in draft);")
NEW = ("     model, the receiving company's engineering item E-1; route B2 (as written then, an unapproved partial proposal; since set "
       "31 UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline, with no owner item: record l4k, 7 October 2026, K-24), which "
       "does not resolve it; D-16\n"
       "     corrected in draft);")

EDITS = [(CLP, OLD, NEW)]

if __name__ == "__main__":
    sys.exit(run("apply_l4k_changelist (K-24)", EDITS))
