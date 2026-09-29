#!/usr/bin/env python3
"""DRAFT apply script (stream a1elec, MESHSAT-1357, 29 September 2026): adds the `a1elec/` row to the worktree table of
v2/docs/records/README.md, as the table's last row (the row before the heading "## Filed files", whatever the
integrator has added since this stream's base). For the integrator to run; NOT executed by the stream.

It asserts the heading is present once and the new row absent (refuses a second run with exit 2), writes, re-reads the
file and checks the table gained exactly one row and nothing else changed. Usage: apply_records_readme_row.py
[--file <path>] (default: the README beside this folder).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "README.md")
HEADING = "## Filed files"
NEW_ROW = ("| `a1elec/` | stream a1elec (29 September 2026, branch `fnd/a1elec` from `13b5352b`): Option A(i)'s electrical "
           "work package on the owner's instruction of that day, M1 and REQ-072 unchanged: the two-pack power path at the "
           "system node with a second BQ25731 and a current-limited ideal-diode path for the lid pack (`TOPOLOGY.md`), the "
           "lid gauge's BQ4050 under a k = 2 current-scale calibration with all 63 scaled data-flash words (`GAUGE.md`, "
           "`gauge_scale.py`), the two-pack energy model with its exact equivalence to the aggregate 4S18P and the lid's own "
           "temperature (`energy_two_pack.py`), and board A's charger and entry drafts (`CHARGER.md`); desk results and "
           "drafts, nothing applied to a generator |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if any(l.startswith("| `a1elec/` |") for l in lines):
        sys.stderr.write("apply_records_readme_row: the a1elec/ row is already present, refusing a second run\n")
        return 2
    h = [i for i, l in enumerate(lines) if l.strip() == HEADING]
    assert len(h) == 1, "heading %r not found exactly once: %d" % (HEADING, len(h))
    rows = [i for i in range(h[0]) if lines[i].startswith("| `") and lines[i].endswith("|")]
    assert rows, "no table row before the heading"
    last = rows[-1]
    before_rows = sum(1 for l in lines if l.startswith("| `") and l.endswith("|"))
    new_lines = lines[: last + 1] + [NEW_ROW] + lines[last + 1:]
    text = "\n".join(new_lines)
    assert text != "\n".join(lines), "the new text does not differ"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    with open(path, encoding="utf-8") as f:
        check = f.read().split("\n")
    after_rows = sum(1 for l in check if l.startswith("| `") and l.endswith("|"))
    assert after_rows == before_rows + 1, "the table did not gain exactly one row"
    assert check[last + 1] == NEW_ROW and len(check) == len(lines) + 1, "the file changed in more than the one row"
    print("apply_records_readme_row: added the a1elec/ row after line %d of %s" % (last + 1, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
