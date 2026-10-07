#!/usr/bin/env python3
"""apply_l4small_ledger.py: register tasks L4A-60 (RE-8) and L4A-80 (RE-18, HO-G) on the remaining-engineering ledger, the P0 list and
L4-E9's copies of the ledger's rows (MESHSAT-1357, worker W133, branch fnd/l4small, 7 October 2026). UNAPPLIED on its branch: set 32
(fnd/int32) changes all four files, so the set 33 integrator runs it on the integrated tree and then regenerates L4-E9's output.

WHAT IT DOES, each by insertion (the earlier words kept; no line moves, so every citation of these files still holds):
  RE-8 (cx46 item 8): the receiving company's task "a rev X part's qualification" and the summary row now say that SESSION L9T5-D11
    (record l9t5, `T10-ROUND5.md` section W133) does not admit revision X, so that qualification is an UNSELECTED OPTION, not a task;
  RE-18 and HO-G (cx46 item 18): the state and the task now say that SESSION L4E7-D1 (record l4e7, `B2-PRESENCE.md` section 8) takes
    up no presence-pair route, so nothing in the baseline rests on HO-G;
  the P0 list's quotation of T10's remaining-engineering list (its line on "a rev X part's qualification");
  L4-E9's generator (LEDGER_ROWS' RE-8 and RE-18, SUP8G's "a rev X part's V-B20") and its page, the same insertions.
The ledger's classes and counts are NOT changed (RE-8 and RE-18 stay "remaining engineering" until a check reads the decisions); no cx46
item closes. Nothing in this kit has been built, bought, powered or measured.
Engine and its checks E1 to E6: v2/docs/records/l4small/l4small_edit.py.
Usage:  apply_l4small_ledger.py [ROOT] [--check | --write]   (default ROOT: this tree; default --check: nothing is written)
Exit 0: checked or written; 2: usage; 3: refused (already applied, an anchor missing or not unique, or the result does not parse)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l4small"))
import l4small_edit as E  # noqa: E402

NAME = "apply_l4small_ledger"
LED = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
P0L = "v2/docs/records/l4close/P0-POWER-LIST.md"
L4PY = "v2/docs/records/l4e9/l4e9_power_path.py"
L4MD = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
DX = "SESSION L9T5-D11"
DB = "SESSION L4E7-D1"
ROW8 = "a rev X part's qualification (V-B20 at most 0.2183 A) on RE-7's bound |"
ROW8_NEW = ("a rev X part's qualification (V-B20 at most 0.2183 A) on RE-7's bound [an UNSELECTED OPTION since 7 October 2026, %s: "
            "revision X NOT ADMITTED, no task] |" % DX)
ROW18 = "HO-G, only if a presence-pair route is taken up again |"
ROW18_NEW = "HO-G, only if a presence-pair route is taken up again [none is: %s, 7 October 2026] |" % DB
SUP = "a rev X part's V-B20 ([CON:350])."
SUP_NEW = "a rev X part's V-B20 ([CON:350]) [an UNSELECTED OPTION since 7 October 2026, %s: revision X NOT ADMITTED, not a task]." % DX

EDITS = [
    # the ledger: RE-8
    (LED, "its rows re-solved\" ([T10R:144-145]), resting on RE-7's bound ([T10R:224]).",
          "its rows re-solved\" ([T10R:144-145]), resting on RE-7's bound ([T10R:224]) [none since 7 October 2026: %s (record l9t5, "
          "`T10-ROUND5.md` section W133) does not admit revision X, so this qualification is an UNSELECTED OPTION outside the scope, "
          "not a task]." % DX, True),
    (LED, ROW8 + " revision X HELD; L9T5-F23 rows |",
          ROW8_NEW + " revision X HELD [NOT ADMITTED, %s]; L9T5-F23 rows |" % DX, True),
    # the ledger: RE-18 and HO-G
    (LED, "HO-G stays REMAINING ENGINEERING outside the\n  baseline.",
          "HO-G stays REMAINING ENGINEERING outside the\n  baseline [and %s (7 October 2026, record l4e7 `B2-PRESENCE.md` section 8) "
          "takes up no presence-pair route, so nothing in the baseline rests on HO-G]." % DB, True),
    (LED, "**Task.** Only for a presence-pair route taken up again ([B2:157-164]).",
          "**Task.** Only for a presence-pair route taken up again ([B2:157-164]) [none is taken up: %s, 7 October 2026]." % DB, True),
    (LED, "| RE-18 | remaining engineering | " + ROW18, "| RE-18 | remaining engineering | " + ROW18_NEW, True),
    # the P0 list's quotation of T10's remaining-engineering list
    (P0L, "containment or the periodic electrothermal solution, a rev X part's qualification, VOS0 under the trip",
          "containment or the periodic electrothermal solution, a rev X part's qualification [an UNSELECTED OPTION since 7 October "
          "2026, %s: revision X NOT ADMITTED], VOS0 under the trip" % DX, True),
    # L4-E9's generator and its page: the same rows
    (L4PY, ROW8, ROW8_NEW, True),
    (L4PY, "| RE-18 | route B2 marked unselected and withdrawn throughout (item 18) | REMAINING ENGINEERING | " + ROW18,
           "| RE-18 | route B2 marked unselected and withdrawn throughout (item 18) | REMAINING ENGINEERING | " + ROW18_NEW, True),
    (L4PY, SUP, SUP_NEW, True),
    (L4MD, ROW8, ROW8_NEW, True),
    (L4MD, "| RE-18 | route B2 marked unselected and withdrawn throughout (item 18) | REMAINING ENGINEERING | " + ROW18,
           "| RE-18 | route B2 marked unselected and withdrawn throughout (item 18) | REMAINING ENGINEERING | " + ROW18_NEW, True),
    (L4MD, SUP, SUP_NEW, True),
]

if __name__ == "__main__":
    sys.exit(E.main(NAME, HERE, EDITS))
