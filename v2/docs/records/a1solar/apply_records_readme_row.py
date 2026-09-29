#!/usr/bin/env python3
"""DRAFT apply script (stream a1solar, MESHSAT-1357, 29 September 2026): adds the `a1solar/` row to the worktree table
of v2/docs/records/README.md, after the `energy/` row. For the integrator to run; NOT executed by the stream.

It asserts the anchor row is present once, asserts the new row is absent (refuses a second run), writes, re-reads the
file and checks the table gained exactly one row and nothing else changed. Usage: apply_records_readme_row.py
[--file <path>] (default: the README one folder up from this script).
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "README.md")
ANCHOR = "| `energy/` | stream energy (28 September 2026, branch `fnd/energy` from `038037ed`)"
NEW_ROW = ("| `a1solar/` | stream a1solar (29 September 2026, branch `fnd/a1solar`, second issue after its AI check): "
           "Option A(i)'s solar panel selected from makers' documents (six candidates; the design basis four Renogy "
           "RNG-100DB-H in 2S2P, a session decision gated on the owner's REQ-016), the array's cold Voc, hot and "
           "edge-of-cloud Isc, the stage's 34.3 V fixed input point, the entry at 20 A and 56.3 V, REQ-016 per "
           "arrangement for the owner, a gated draft list for board E's writer, both energy design cases at the "
           "array's typical and adverse ratios, and the planes the array may face from 50 PVGIS mean days "
           "(`SELECTION.md`, `ARRAY.md`, `array_calc.py`, `energy_runs.py` with their outputs); authored in the tree |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=DEFAULT)
    a = ap.parse_args()
    path = os.path.abspath(a.file)
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    if any(l.startswith("| `a1solar/` |") for l in lines):
        sys.stderr.write("apply_records_readme_row: the a1solar/ row is already present, refusing a second run\n")
        return 2
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    assert len(idx) == 1, "anchor row (energy/) not found exactly once: %d" % len(idx)
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
    print("apply_records_readme_row: added the a1solar/ row after the energy/ row in %s" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
