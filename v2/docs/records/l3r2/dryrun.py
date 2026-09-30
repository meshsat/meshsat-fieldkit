#!/usr/bin/env python3
"""Dry runs of every prepared owner-decision script of L3-R2 on COPIES of the registry (MESHSAT-1357, 30 September 2026).

Each chain starts from a copy of v2/ecad/tools/pcb_requirements.yaml and applies the scripts of conditional/ in the
order their prerequisites allow, with placeholder words, printing what each changes; nothing in the tree is written. The
output (dryrun.out beside this file) is deterministic: temporary paths are printed as <copy>. Row L3-OD4's band, row
L3-OD3's keep figures and row L3-OD6's coverage figures come from fixture files written into the copy's directory,
standing in for the checked energy basis until it is filed (row L3-OD6's own table holds no figure yet, so a coverage
target read from it is refused); the refusals of the incoherent chains are part of the record.

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
    ("recommended where recommended (rows 2, 4 and 6 held; the QMX out, adopt and the average-day benchmark shown)",
     [("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt"), ("od_l3_5.py", "reading-c"),
      ("od_l3_6.py", "mean-day")]),
    ("the QMX outside the case", [("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-outside"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("the tablet out", [("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("1S4P: a band refused (no grid), no deployment condition accepted",
     [("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "1s4p"), ("od_l3_4.py", "adopt"), ("od_l3_4.py", "reject")]),
    ("CHECK-1's incoherent path: REQ-016 kept, then adopt refused",
     [("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "keep"), ("od_l3_4.py", "adopt"), ("od_l3_5.py", "reading-c")]),
    ("Option A(i) rejected: row 2 refused", [("od_l3_1.py", "reject"), ("od_l3_2.py", "qmx-out")]),
    ("both lid items kept: an open conflict, then a band refused and no deployment condition accepted",
     [("od_l3_1.py", "approve"), ("od_l3_2.py", "both-kept"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt"), ("od_l3_4.py", "reject")]),
    ("a coverage target read from row L3-OD6's own table: refused while its figures are HELD", [("od_l3_6.py", "coverage:tree")]),
    ("a coverage target of 90 percent whose store does not fit (fixture figures): an open conflict; row L3-OD1 keeps the target; a band refused",
     [("od_l3_6.py", "coverage:90"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt"),
      ("od_l3_4.py", "reject")]),
    ("a coverage target of 50 percent whose store fits (fixture figures)", [("od_l3_6.py", "coverage:50")]),
    ("CFL-017 kept open", [("od_l3_5.py", "measure")]),
    ("cells above +60 C", [("od_l3_5.py", "cells")]),
]


def main(argv):
    print("L3-R2 DRY RUNS of the prepared owner-decision scripts, each chain on a fresh copy of the registry.")
    print("Placeholder words 'dry run', date 2026-10-01. Nothing in the tree is written. Rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 are")
    print("held by D-22 and D-23 for the tree's registry; a copy is not held, so each prepared change is exercised here. Row L3-OD4's band and")
    print("row L3-OD3's keep figures and row L3-OD6's coverage figures come from FIXTURE files standing in for the checked")
    print("energy basis, which is not filed yet;")
    print("the push is a placeholder of 20 N standing in for the owner's number.")
    for name, steps in CHAINS:
        d = tempfile.mkdtemp(prefix="l3r2-dry-")
        reg = os.path.join(d, "pcb_requirements.yaml")
        shutil.copy(REG, reg)
        ev = os.path.join(d, "basis-fixture.md")
        open(ev, "w", encoding="utf-8").write("FIXTURE, not the energy basis: %s; array 1100 Wp, entry 80 A. Coverage 90: "
                                              "3000 Wh usable, 4000 Wh nominal, 20.5 kg, 12.5 litres. Coverage 50: 900 Wh "
                                              "usable, 1100 Wh nominal, 6.5 kg, 3.5 litres.\n" % BAND)
        table = os.path.join(d, "table-fixture.yaml")
        open(table, "w", encoding="utf-8").write(
            "rows:\n"
            "  - {id: cov-90, option: coverage, share: 90, usable_wh: 3000, nominal_wh: 4000, mass_kg: 20.5, volume_l: 12.5, fits: 'NO', evidence: '%s'}\n"
            "  - {id: cov-50, option: coverage, share: 50, usable_wh: 900, nominal_wh: 1100, mass_kg: 6.5, volume_l: 3.5, fits: 'YES', evidence: '%s'}\n"
            % (ev, ev))
        print("\n== chain: %s" % name)
        for script, opt in steps:
            opt, _, share = opt.partition(":")
            args = [sys.executable, os.path.join(COND, script), "--option", opt, "--words", "dry run", "--date", "2026-10-01",
                    "--registry", reg]
            if script == "od_l3_6.py" and share == "tree": args += ["--share", "90"]
            elif script == "od_l3_6.py" and share: args += ["--share", share, "--table", table]
            if script == "od_l3_4.py" and opt == "adopt": args += ["--band", BAND, "--band-evidence", ev, "--push-n", "20"]
            if script == "od_l3_3.py" and opt == "keep": args += ["--array-wp", "1100", "--entry-a", "80", "--evidence", ev]
            r = subprocess.run(args, capture_output=True, text=True, cwd=d)
            out = re.sub(r"\S*" + re.escape(os.path.basename(d)) + r"/pcb_requirements\.yaml", "<copy>", r.stdout)
            out = out.replace(d, "<copy dir>")
            print("-- %s --option %s (exit %d)" % (script, opt, r.returncode))
            for line in out.rstrip().split("\n"): print("   " + line)
        shutil.rmtree(d, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
