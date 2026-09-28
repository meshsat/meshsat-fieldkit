#!/usr/bin/env python3
"""DRAFT apply script (stream energy, MESHSAT-1357, 28 September 2026): adds the `energy/` row to the worktree table
of v2/docs/records/README.md, after the `h2/` row. For the integrator to run; NOT executed by the stream.

It asserts the anchor row is present, asserts the new row is absent (refuses a second run), writes, re-reads the
file and checks the table gained exactly one row and nothing else changed. Usage: apply_records_readme_row.py
[--file <path>] (default: the README relative to this script's repository root).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "README.md")
ANCHOR = "| `h2/` | the targeted fix of layers 1 and 3 (27 September 2026, branch `fnd/h2` from `62f26a44`)"
NEW_ROW = ("| `energy/` | stream energy (28 September 2026, branch `fnd/energy` from `038037ed`): mission M1's energy "
           "reconciliation on the owner's instruction of that day, M1 and REQ-072 preserved as written: the loads of each "
           "state with their kinds, the usable pack energy, the night at 52 N by month, the solar input per day, the "
           "hour-by-hour balance with its sensitivity, the options ranked and the smallest justified changes for the "
           "owner's decision (`ENERGY-RECONCILIATION.md`, `DECISION-PARAGRAPH.md`, `energy_budget.py` with its pinned "
           "inputs and output); authored in the tree, not filed from drafts |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if any(l.startswith("| `energy/` |") for l in lines):
        sys.stderr.write("apply_records_readme_row: the energy/ row is already present, refusing a second run\n")
        return 2
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, "anchor row (h2/) not found exactly once: %d" % len(idx)
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
    print("apply_records_readme_row: added the energy/ row after the h2/ row in %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
