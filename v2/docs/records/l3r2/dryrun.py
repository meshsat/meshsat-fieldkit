#!/usr/bin/env python3
"""Dry runs of every prepared owner-decision script of L3-R2 on COPIES of the registry (MESHSAT-1357, 30 September 2026).

Each chain starts from a copy of v2/ecad/tools/pcb_requirements.yaml and applies the scripts of conditional/ in the
order their prerequisites allow, with placeholder words, printing what each changes; nothing in the tree is written. The
output (dryrun.out beside this file) is deterministic: temporary paths are printed as <copy>. Row L3-OD4's band, row
L3-OD3's keep figures and row L3-OD6's table come from fixture files written into the copy's directory, standing in for
the checked energy basis until it is filed (row L3-OD6's own table holds no figure yet, so an answer read from it is
refused). The fixture table has the mean day in TYP carried by the tablet-out and QMX-out lids, in WAB by the QMX-out lid
only, and no coverage target carried by any lid. The chains are EXAMPLES, not recommendations: row L3-OD6's
recommendation is held (CHECK-2 of L3-R2, minor 3). The refusals of the incoherent chains are part of the record.

Usage: python3 dryrun.py > dryrun.out
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
COND = os.path.join(HERE, "conditional")
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
BAND = "the band the checked energy basis gives"
CHAINS = [
    ("an example chain, not a recommendation (rows 1, 2, 4 and 6 held): the mean day in TYP, then the QMX out and adopt",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "2s2p"),
      ("od_l3_4.py", "adopt"), ("od_l3_5.py", "reading-c")]),
    ("the QMX outside the case", [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-outside"),
                                  ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("the tablet out, the mean day in TYP", [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"),
                                             ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("CHECK-2's path A: row 4 before row 6, adopt refused", [("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"),
                                                              ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("CHECK-2's path B: the mean day in WAB with the tablet-out lid, an open conflict",
     [("od_l3_6.py", "mean-day:WAB"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out")]),
    ("1S4P: a band refused (no grid), no deployment condition accepted",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "1s4p"),
      ("od_l3_4.py", "adopt"), ("od_l3_4.py", "reject")]),
    ("CHECK-1's incoherent path: REQ-016 kept, then adopt refused",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "keep"),
      ("od_l3_4.py", "adopt"), ("od_l3_5.py", "reading-c")]),
    ("Option A(i) rejected: row 2 refused", [("od_l3_1.py", "reject"), ("od_l3_2.py", "qmx-out")]),
    ("both lid items kept: an open conflict, then a band refused and no deployment condition accepted",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "both-kept"), ("od_l3_3.py", "2s2p"),
      ("od_l3_4.py", "adopt"), ("od_l3_4.py", "reject")]),
    ("an answer read from row L3-OD6's own table: refused while its figures are HELD", [("od_l3_6.py", "mean-day:TYP:tree")]),
    ("a coverage target of 95 percent in WAB that no lid carries (fixture): an open conflict; row L3-OD1 keeps the target; a band refused",
     [("od_l3_6.py", "coverage:WAB:95"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"), ("od_l3_3.py", "2s2p"),
      ("od_l3_4.py", "adopt"), ("od_l3_4.py", "reject")]),
    ("CFL-017 kept open", [("od_l3_5.py", "measure")]),
    ("cells above +60 C", [("od_l3_5.py", "cells")]),
]
ROWS = []
for basis in ("mean-day", "50", "80", "95"):
    for build in ("TYP", "WAB"):
        fits = ("[tablet-out, qmx-out]" if build == "TYP" else "[qmx-out]") if basis == "mean-day" else "[]"
        ROWS.append("  - {id: %s-%s, option: %s, share: %s, build: %s, usable_wh: '619.0', lid_block: 4S13P, cells: 76, "
                    "nominal_wh: '916.6', mass_kg: '3.80', volume_cyl_l: '1.3', volume_box_l: '1.7', x_wh: '0.89', "
                    "x_cells: '0.90', fits: %s, evidence: fixture B}\n"
                    % (basis if basis == "mean-day" else "cov-" + basis, build, "mean-day" if basis == "mean-day" else "coverage",
                       "null" if basis == "mean-day" else basis, build, fits))


def main(argv):
    print("L3-R2 DRY RUNS of the prepared owner-decision scripts, each chain on a fresh copy of the registry.")
    print("Placeholder words 'dry run', date 2026-10-01. Nothing in the tree is written. Rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 are")
    print("held by D-22, D-23 and D-24 for the tree's registry; a copy is not held, so each prepared change is exercised here.")
    print("Row L3-OD4's band, row L3-OD3's keep figures and row L3-OD6's table come from FIXTURE files standing in for the")
    print("checked energy basis, which is not filed yet; the push is a placeholder of 20 N standing in for the owner's number.")
    print("The chains are examples, not recommendations.")
    for name, steps in CHAINS:
        d = tempfile.mkdtemp(prefix="l3r2-dry-")
        reg = os.path.join(d, "pcb_requirements.yaml")
        shutil.copy(REG, reg)
        ev = os.path.join(d, "basis-fixture.md")
        open(ev, "w", encoding="utf-8").write('FIXTURE, not the energy basis: "%s"; array 1100 Wp, entry 80 A.\n' % BAND)
        table = os.path.join(d, "table-fixture.yaml")
        open(table, "w", encoding="utf-8").write("rows:\n" + "".join(ROWS))
        print("\n== chain: %s" % name)
        for script, opt in steps:
            parts = opt.split(":")
            opt = parts[0]
            args = [sys.executable, os.path.join(COND, script), "--option", opt, "--words", "dry run", "--date", "2026-10-01",
                    "--registry", reg]
            if script == "od_l3_4.py" and opt == "adopt": args += ["--band", BAND, "--band-evidence", ev, "--push-n", "20"]
            if script == "od_l3_3.py" and opt == "keep": args += ["--array-wp", "1100", "--entry-a", "80", "--evidence", ev]
            if script == "od_l3_6.py":
                args += ["--build", parts[1]] + (["--share", parts[2]] if opt == "coverage" else [])
                if "tree" not in parts: args += ["--table", table]
            if script == "od_l3_2.py": args += ["--table", table]
            r = subprocess.run(args, capture_output=True, text=True, cwd=d)
            out = re.sub(r"\S*" + re.escape(os.path.basename(d)) + r"/pcb_requirements\.yaml", "<copy>", r.stdout)
            out = out.replace(d, "<copy dir>")
            print("-- %s --option %s (exit %d)" % (script, ":".join(parts), r.returncode))
            for line in out.rstrip().split("\n"): print("   " + line)
        shutil.rmtree(d, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
