#!/usr/bin/env python3
"""apply_l4small_tests.py: the restated test expectations that go with stream l4small's apply scripts (MESHSAT-1357, worker W133,
branch fnd/l4small, 7 October 2026). UNAPPLIED on its branch, like the scripts whose results these tests read: the set 33
integrator runs it in the same step as `records/l9t5/apply_l4small_revx.py` and `records/l4small/apply_l4small_b2.py`.

  v2/ecad/tools/tests/test_w11l9t5.py  t_the_generator_prints_the_restated_rows holds the connected generator to "the base with the
      two rows' literals and W20's three swapped". apply_l4small_revx.py inserts SESSION L9T5-D11 into three more literals of that
      generator (section 10's revision X lines). RESTATED EXPECTATION: those three insertions are swapped in too, by exact literal,
      and nothing else may differ. Basis: the decision L9T5-D11 (record l9t5, `T10-ROUND5.md` section W133) and the edits as filed.
      Refused mutant: a generator carrying only two of the three, or any other change, still fails `swapped == src` (shown in
      test_l4small.t_the_restated_generator_check_refuses_a_partial_application).
  v2/ecad/tools/tests/test_l4e7.py     the docstring of t_p0sol_d10_is_written_as_an_unresolved_defect_and_b2_never_as_its_closure
      said "route B2 is an unapproved PARTIAL proposal" as the owner's part 23 framed it: labelled as round 3's words with the
      current state (SESSION L4E7-D1). No assertion changes.
Engine and its checks E1 to E6 (GROW: an insertion that may add lines, in a test module): v2/docs/records/l4small/l4small_edit.py.
Usage:  apply_l4small_tests.py [ROOT] [--check | --write]   (default ROOT: this tree; default --check: nothing is written)
Exit 0: checked or written; 2: usage; 3: refused (already applied, an anchor missing or not unique, or the result does not parse)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l4small_edit as E  # noqa: E402

NAME = "apply_l4small_tests"
W11 = "v2/ecad/tools/tests/test_w11l9t5.py"
L4E7 = "v2/ecad/tools/tests/test_l4e7.py"

W133_LITS = '''# W133's three insertions (7 October 2026, record l9t5's apply_l4small_revx.py; basis: SESSION L9T5-D11, record l9t5's
# T10-ROUND5.md section W133): section 10's revision X lines of the connected generator carry the decision, nothing else moves
W133_LITS = [
    ('in its bounded state (V-B20, 10j (f)), and a draw over"',
     'in its bounded state (V-B20, 10j (f)) [revision X NOT ADMITTED since 7 October 2026, SESSION L9T5-D11], and a draw over"'),
    ('current, so revision X stays HELD on V-B20 (Slot C, 10j (f));")',
     'current, so revision X stays HELD on V-B20 (Slot C, 10j (f)) [superseded: NOT ADMITTED, SESSION L9T5-D11];")'),
    ("(its bounded state over the trip's least; HELD on V-B20); the LDO input headroom",
     "(its bounded state over the trip's least; HELD on V-B20 [superseded: NOT ADMITTED, SESSION L9T5-D11]); the LDO input headroom"),
]
'''
W133_LOOP = '''    # restated by W133 (7 October 2026; basis: SESSION L9T5-D11, record l9t5's T10-ROUND5.md section W133): the three insertions of
    # record l9t5's apply_l4small_revx.py are swapped in too, by exact literal; any other difference still fails below
    for o, n in W133_LITS:
        assert swapped.count(o) == 1, o[:40]
        swapped = swapped.replace(o, n)
'''
LOOP_ANCHOR = '''        swapped = swapped.replace('w("%s"' % o, 'w("%s"' % n)
    assert swapped == src, "the generator differs from the base in more than the two rows' literals and W20's three"'''

EDITS = [
    (W11, "# W11's tip: the W11 section of the README says its line numbers are this branch's",
          W133_LITS + "# W11's tip: the W11 section of the README says its line numbers are this branch's", E.GROW),
    (W11, LOOP_ANCHOR,
          LOOP_ANCHOR.split("\n")[0] + "\n" + W133_LOOP + LOOP_ANCHOR.split("\n")[1], E.GROW),
    (L4E7, "stay PROVISIONAL; route B2 is an unapproved PARTIAL proposal and no text says",
           "stay PROVISIONAL; route B2 is an unapproved PARTIAL proposal [round 3's words; UNSELECTED and WITHDRAWN AS DRAFTED since,\n"
           "    and SESSION L4E7-D1 takes up no presence-pair route] and no text says", E.GROW),
]

if __name__ == "__main__":
    sys.exit(E.main(NAME, HERE, EDITS))
