#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026; second round, item M7 of its check): adds the
`s119/` row to the worktree table of v2/docs/records/README.md, after the `a1solar/` row. For the integrator to run.

It refuses (exit 2, never an assert, which `python -O` would strip) unless the anchor row is present once and the new row
is absent (a second run refuses); with --check it writes nothing; otherwise it writes, re-reads the file and checks that
the table gained exactly the one row and nothing else changed. Usage: apply_records_readme_row.py [--check] [--file <path>]
(default: the README one folder up from this script)."""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "README.md")
ANCHOR = "| `a1solar/` | stream a1solar (29 September 2026, branch `fnd/a1solar`, second issue after its AI check)"
NEW_ROW = ("| `s119/` | stream s119 (29 September 2026, branch `fnd/s119` from `a1f8ec70`, S-119, two rounds): the energy "
           "chain's charger rows restated from the FETs' losses (U3 0.98 to 0.979 with decision 57's FETs; U3B 0.975 to "
           "0.972 on U3's 400 kHz row, the session decision drafted by `apply_decision_s119.py`, weighted over the model's "
           "own hours by `u3b_hourly.py`), U3B's inductor checked (`inductor_u3b.py`), the chain's scripts re-issued with "
           "their pins moved and every output regenerated, the headline figures before and after (`headline_diff.py`), "
           "Option A(i)'s lid reconciliation re-run with the change from the accepted figures, U3B hour by hour, the "
           "failing case, the sensitivity, the room for the excluded core loss and the deployment rule's planes "
           "(`reconcile_s119.py`), the parsed comparison that re-pinned energy_4s6p.py's gen_sch_a.py (`cmp_gen_sch_a.py`), "
           "and the apply scripts for the registry, the decision register and the pages; authored in the tree |")


def refuse(msg):
    sys.stderr.write("apply_records_readme_row: REFUSED: %s\n" % msg)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    if any(l.startswith("| `s119/` |") for l in lines):
        refuse("the s119/ row is already present (a second run)")
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    if len(idx) != 1:
        refuse("the anchor row (a1solar/) is found %d times, not once" % len(idx))
    if "\u2014" in NEW_ROW or "\u2013" in NEW_ROW:
        refuse("the row carries an em or en dash")
    before_rows = sum(1 for l in lines if l.startswith("| `") and l.endswith("|"))
    new_lines = lines[: idx[0] + 1] + [NEW_ROW] + lines[idx[0] + 1:]
    new = "\n".join(new_lines)
    if new == text:
        refuse("the new text does not differ")
    if a.check:
        print("CHECK ONLY: %s would gain the s119/ row after the a1solar/ row; not written" % path)
        return 0
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    with open(path, encoding="utf-8") as f:
        back = f.read().split("\n")
    after_rows = sum(1 for l in back if l.startswith("| `") and l.endswith("|"))
    if after_rows != before_rows + 1 or back[idx[0] + 1] != NEW_ROW or back[: idx[0] + 1] + back[idx[0] + 2:] != lines:
        refuse("the file changed in more than the one row")
    print("apply_records_readme_row: added the s119/ row after the a1solar/ row in %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
