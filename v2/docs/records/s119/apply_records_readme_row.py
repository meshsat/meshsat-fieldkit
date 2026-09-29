#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026): adds the `s119/` row to the worktree table
of v2/docs/records/README.md, after the `a1solar/` row. For the integrator to run; NOT executed by the stream
(adapted from records/a1solar/apply_records_readme_row.py).

It asserts the anchor row is present once, asserts the new row is absent (refuses a second run), writes, re-reads the
file and checks the table gained exactly one row and nothing else changed. Usage: apply_records_readme_row.py
[--file <path>] (default: the README one folder up from this script).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "README.md")
ANCHOR = "| `a1solar/` | stream a1solar (29 September 2026, branch `fnd/a1solar`, second issue after its AI check)"
NEW_ROW = ("| `s119/` | stream s119 (29 September 2026, branch `fnd/s119` from `a1f8ec70`, S-119): the energy chain's "
           "charger rows restated from the drawn and drafted FETs' losses (U3 0.98 to 0.979, U3B 0.975 to 0.961; "
           "`records/s117/efficiency.out`), the chain's scripts re-issued with their pins moved and every output "
           "regenerated, the headline figures before and after (`headline_diff.py`), Option A(i)'s lid reconciliation "
           "re-run with the change from the accepted figures, the failing case, the sensitivity, the margins and the "
           "deployment rule's planes (`reconcile_s119.py`), the parsed comparison that re-pinned energy_4s6p.py's "
           "gen_sch_a.py (`cmp_gen_sch_a.py`), and the apply scripts for the registry and the pages; authored in the tree |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if any(l.startswith("| `s119/` |") for l in lines):
        sys.stderr.write("apply_records_readme_row: the s119/ row is already present, refusing a second run\n")
        return 2
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, "anchor row (a1solar/) not found exactly once: %d" % len(idx)
    before_rows = sum(1 for l in lines if l.startswith("| `") and l.endswith("|"))
    new_lines = lines[: idx[0] + 1] + [NEW_ROW] + lines[idx[0] + 1:]
    text = "\n".join(new_lines)
    assert text != "\n".join(lines), "the new text does not differ"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(path, encoding="utf-8") as f:
        check = f.read().split("\n")
    after_rows = sum(1 for l in check if l.startswith("| `") and l.endswith("|"))
    assert after_rows == before_rows + 1, "the table did not gain exactly one row"
    assert check[idx[0] + 1] == NEW_ROW and len(check) == len(lines) + 1, "the file changed in more than the one row"
    print("apply_records_readme_row: added the s119/ row after the a1solar/ row in %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
