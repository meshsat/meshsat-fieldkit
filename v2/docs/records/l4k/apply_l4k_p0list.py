#!/usr/bin/env python3
"""K-13 (record l4k, MESHSAT-1357, W131, 7 October 2026): the P0 list's quotation of record l4e7's superseded "Completed
independently" wording marked as the candidate's, with the page's present words beside it. FOR THE INTEGRATOR (the P0 list is the
coordinator's file), on set 33's integrated tree; not applied on fnd/l4k.

K-13, standing on main be07863b in the P0 list's row P0-7:
  be07863b:v2/docs/records/l4close/P0-POWER-LIST.md:124 "Completed independently of E-1 ...: D-16's correction"
cites record l4e7's request at `v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:89-92`, which held those words at the candidate
dd1aed00 (the list's bare citations read there); on main the page reads in their place
  be07863b:v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:119-120 "ADDRESSED IN DRAFTS, PROVISIONAL, not completed"
(W4's rewrite at 786aed2f, merged into set 31 at ec85131c). The P0 list's quotation is kept (it is true of the revision it reads,
and test_w17p0list holds every bare citation at dd1aed00); a dated note is added after its citation, inside the same line, in the
list's own citation form (`<sha>:path:N`, which test_w17p0list reads at that sha; the note's quotation is on those lines there).

Why a script (authority SESSION, W131; reversed by running the edit by hand on set 33's tree): the P0 list is changed by set 32
(fnd/int32 4c8196a0: its lines 44, 101, 133 and 177, re-cites); its line 125 is not, so the edit applies there unchanged.
Outputs that move: none (no output pins the P0 list; searched *.out under v2/docs/records, 7 October 2026).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _l4k_apply import run  # noqa: E402

P0L = "v2/docs/records/l4close/P0-POWER-LIST.md"

OLD = "(`v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:89-92`); its row R-240 DRAFTED"
NEW = ("(`v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:89-92`; dated note, 7 October 2026, record l4k, K-13: the page's words at "
       "the candidate; since W4's rewrite at `786aed2f` it reads in their place \"ADDRESSED IN DRAFTS, PROVISIONAL, not completed\" "
       "(`be07863b:v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:119-120`)); its row R-240 DRAFTED")

EDITS = [(P0L, OLD, NEW)]

if __name__ == "__main__":
    sys.exit(run("apply_l4k_p0list (K-13)", EDITS))
