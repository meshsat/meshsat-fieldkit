#!/usr/bin/env python3
"""DRAFT apply script (layer 3's second issue, L3-R2, MESHSAT-1357, 30 September 2026): adds the `l3r2/` row to the
worktree table of v2/docs/records/README.md, after the `s119/` row. For the integrator to run on the set that carries
this branch; not run in the branch, so a merge of README.md never conflicts on it.

It refuses (exit 2) unless the anchor row is present once and the new row is absent (a second run refuses); with --check
it writes nothing; otherwise it writes and checks that the file gained exactly the one row.
Usage: apply_records_readme_row.py [--check] [--file <path>]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "..", "README.md")
ANCHOR = "| `s119/` | stream s119 (29 September 2026, branch `fnd/s119` from `a1f8ec70`, S-119, two rounds)"
NEW_ROW = ("| `l3r2/` | layer 3's second issue, L3-R2 (30 September 2026, branch `fnd/l3r2` on `4012429e`, on the owner's "
           "instruction D-21, his review D-22, his instruction on the six-row table D-23, his addendum on the power path "
           "D-24 and his corrections D-25): the registry's editing helpers (`l3edit.py`), the session's closures "
           "(`apply_l3r2_session.py`, `apply_l3r2_d23.py` to `apply_l3r2_d25.py`, `apply_l3r2_r3b.py`), the basis reader "
           "and the prepared fill (`basis_reader.py`, `set_energy_basis.py`, `fill_l3r2_from_basis.py`), CFL-006's re-read "
           "(`read_cfl006.py`), the layer status page's layer 3 restated (`apply_layer_status_l3.py`, rounds 3 and 3b "
           "`apply_layer_status_l3_r3.py` and `apply_layer_status_l3_r3b.py`), the prepared "
           "owner-decision scripts of rows L3-OD1 to L3-OD6 (`conditional/`, not applied, rows 1, 2, 4 and 6 held until "
           "the energy basis and the power path are checked) and their dry runs (`dryrun.py`), the independent checks of L3-R2 and the checks of "
           "the energy basis (`checks/`); the pages are `v2/docs/handover/layer3/`; authored in the tree |")


def refuse(msg):
    sys.stderr.write("apply_records_readme_row: REFUSED: %s\n" % msg)
    sys.exit(2)


def main(argv):
    path = os.path.abspath(argv[argv.index("--file") + 1]) if "--file" in argv else os.path.abspath(DEFAULT)
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    if len(idx) != 1: refuse("the anchor row occurs %d times" % len(idx))
    if any(l.startswith("| `l3r2/` |") for l in lines): refuse("the l3r2/ row is already there")
    for dch in ("\u2013", "\u2014"):
        if dch in NEW_ROW: refuse("the row carries a dash character")
    new_lines = lines[:idx[0] + 1] + [NEW_ROW] + lines[idx[0] + 1:]
    new = "\n".join(new_lines)
    if len(new_lines) != len(lines) + 1: refuse("the table did not gain exactly one row")
    if "--check" in argv:
        print("apply_records_readme_row: the l3r2/ row would follow the s119/ row (check only)"); return 0
    open(path, "w", encoding="utf-8").write(new)
    if open(path, encoding="utf-8").read().split("\n") != new_lines: refuse("the file did not read back as written")
    print("apply_records_readme_row: written %s" % os.path.relpath(path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
