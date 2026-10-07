#!/usr/bin/env python3
"""K-13 and K-23 (record l4k, MESHSAT-1357, W131, 7 October 2026): two printed sentences of record l4e7's generator
l4e7_p0sol.py brought to the reading its own pages carry since set 31 (W4's rewrite at 786aed2f, merged at ec85131c). FOR THE
INTEGRATOR, on set 33's integrated tree; not applied on fnd/l4k.

K-13, standing on main be07863b in the generator alone:
  be07863b:v2/docs/records/l4e7/l4e7_p0sol.out:281-282 "Completed independently on the present port network: D-16's correction
  (section 2)" (printed by be07863b:v2/docs/records/l4e7/l4e7_p0sol.py:1225),
against the pages, be07863b:v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md:119-120 "ADDRESSED IN DRAFTS, PROVISIONAL, not completed"
and the register's R-240 (DRAFTED). The new words, "Independent of E-1, ADDRESSED IN DRAFTS and PROVISIONAL:", are the pages'
state words; chosen so the paragraph keeps its four printed lines (the generator's wrap at 130 columns, simulated on the
paragraph's text: 4 lines before, 4 after), so no later line of l4e7_p0sol.out moves for this edit.

K-23, standing on main be07863b in the generator alone:
  be07863b:v2/docs/records/l4e7/l4e7_p0sol.out:403 "Validation: P1-1's S1 (the first two added to its rows)" (printed by
  be07863b:v2/docs/records/l4e7/l4e7_p0sol.py:1353),
against the pages' reading, be07863b:v2/docs/records/l4e7/B2-PRESENCE.md:184 "REMAINING ENGINEERING inside E-1" and
be07863b:v2/docs/records/l4e7/B2-PRESENCE.md:185-186 "P1-1's S1 row (b) is the later validation of that computation, not a
substitute for it", and the ledger's HO-F (section 6, item E: the narrower reading). The new sentence places both open cases of section 5g inside E-1, S1's rows (a) and (b) their later
validation; 6 printed lines before and after (simulated), so nothing below moves.

Both edits are in place (one source line each, no line of l4e7_p0sol.py moves); the dated attribution is a trailing comment on
the same source line, so the printed text stays the record's.

Why a script (authority SESSION, W131; reversed by running the two edits by hand on set 33's tree): l4e7_p0sol.py is changed by set
32 (fnd/int32 4c8196a0, record l4e7's WP-B; both old texts read the same there, at its lines 1290 and 1418) and its sha256 is pinned
by record l9t5's l9t5_connected.out (its input line 26 at be07863b), which set 32 regenerates.

Outputs that move after the apply (named for set 33's regeneration, not regenerated here: the generator reads makers' held curves
for its section 0d and its output is in the l9t5 stability cascade): v2/docs/records/l4e7/l4e7_p0sol.out (the two paragraphs' words;
line count unchanged by these edits) and every output that pins it or l4e7_p0sol.py (l9t5_connected.out's input lines). No figure,
verdict, state or citation target of the output changes; no test reads either sentence (searched: v2/ecad/tools/tests and
v2/docs/records, *.py, 7 October 2026).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _l4k_apply import run  # noqa: E402

GEN = "v2/docs/records/l4e7/l4e7_p0sol.py"

OLD_13 = ('         "Completed independently on the present port network: D-16\'s correction (section 2), the regulation and "\n'
          '         "its correlated margin, the 100 W bound re-run')
NEW_13 = ('         "Independent of E-1, ADDRESSED IN DRAFTS and PROVISIONAL: D-16\'s correction (section 2), the regulation and "  '
          '# K-13, record l4k, 7 October 2026: the pages\' reading since set 31 (SUPPLIER-P1-1-P0SOL.md E-1 (d)), in place of '
          'round 3\'s wording\n'
          '         "its correlated margin, the 100 W bound re-run')

OLD_23 = ('         "and the pair\'s fault detection and INP\'s protection (5f). Validation: P1-1\'s S1 (the first two added to its rows); '
          'the "\n         "last two are REMAINING ENGINEERING outside the baseline')
NEW_23 = ('         "and the pair\'s fault detection and INP\'s protection (5f). The first two are REMAINING ENGINEERING inside E-1, '
          'P1-1\'s S1 rows (a) and (b) their later validation; the "  # K-23, record l4k, 7 October 2026: B2-PRESENCE.md section 7 '
          'since set 31, in place of the validation-only reading\n         "last two are REMAINING ENGINEERING outside the baseline')

EDITS = [(GEN, OLD_13, NEW_13), (GEN, OLD_23, NEW_23)]

if __name__ == "__main__":
    sys.exit(run("apply_l4k_p0sol (K-13, K-23)", EDITS))
