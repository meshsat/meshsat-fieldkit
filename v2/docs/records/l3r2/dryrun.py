#!/usr/bin/env python3
"""Dry runs of every prepared owner-decision script of L3-R2 on COPIES of the registry (MESHSAT-1357, 30 September 2026).

Each chain starts from a copy of v2/ecad/tools/pcb_requirements.yaml and applies the scripts of conditional/ in the
order their prerequisites allow, with placeholder words, printing what each changes; nothing in the tree is written. The
output (dryrun.out beside this file) is deterministic: temporary paths are printed as <copy>. Row L3-OD4's band, row
L3-OD3's keep figures and row L3-OD6's table come from fixture files written into the copy's directory, so that each
chain exercises the lid checks on a known table; one chain reads row L3-OD6's own table, filled from the checked basis
(fnd/l3plane cd8720a1) and verified against it. Row L3-OD4's band is the basis's: none at U3's 6.0 A bracket. The fixture table has the mean day in TYP carried by the tablet-out and QMX-out lids, in WAB by the QMX-out lid
only, and no coverage target carried by any lid. The chains are EXAMPLES, not recommendations. Since D-26 (layer 3 round
5) a target the studied candidate does not meet is recorded with its feasibility item (FI-01 to FI-06), and only
requirements that cannot both hold are refused (row L3-OD2 after a reject; a second answer to a decided row); those
refusals are part of the record. The owner's own numbers (the push, the slope for a lid with no figure, the pass line of
sub-choice 1b) take STAND-INS here. Since D-27 row L3-OD7 (M1's runtime) is answered first: every chain that reaches rows
L3-OD1, L3-OD2, L3-OD4 or L3-OD6 starts with it answered 72-required, a STAND-IN for the owner's runtime answer, and three
chains show the rows refused before it and after its other answers.

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
RUNTIME_SCRIPTS = ("od_l3_1.py", "od_l3_2.py", "od_l3_4.py", "od_l3_6.py")   # rows L3-OD1, L3-OD2, L3-OD4, L3-OD6 (D-27)
CHAINS = [
    ("an example chain, not a recommendation: the mean day in TYP, then approve at the kit loads, the QMX out, 2S2P, adopt at a 10 N stand-in, reading-c",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "2s2p"),
      ("od_l3_4.py", "adopt"), ("od_l3_5.py", "reading-c")]),
    ("the QMX outside the case", [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-outside"),
                                  ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("the tablet out, the mean day in TYP", [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"),
                                             ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("row 4 before row 6: adopt is valid now (no band exists, D-26)", [("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"),
                                                                        ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt")]),
    ("HF kept with WAB: the mean day in WAB with the tablet-out lid, a valid target with feasibility item FI-02 (D-26)",
     [("od_l3_6.py", "mean-day:WAB"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out")]),
    ("1S4P with adopt and a second answer to row 4 refused",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "1s4p"),
      ("od_l3_4.py", "adopt"), ("od_l3_4.py", "reject")]),
    ("REQ-016 kept, then adopt (valid, D-26)",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "keep"),
      ("od_l3_4.py", "adopt"), ("od_l3_5.py", "reading-c")]),
    ("Option A(i) rejected: feasibility item FI-01; row 2 refused as a contradiction; rows 3 to 6 answered",
     [("od_l3_1.py", "reject"), ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt:slope"),
      ("od_l3_5.py", "reading-c"), ("od_l3_6.py", "mean-day:TYP")]),
    ("both lid items kept: feasibility item FI-04, then adopt at the both-kept lid's figures",
     [("od_l3_6.py", "mean-day:TYP"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "both-kept"), ("od_l3_3.py", "2s2p"),
      ("od_l3_4.py", "adopt")]),
    ("an answer read from row L3-OD6's own table, filled from the checked basis and read again from it", [("od_l3_6.py", "mean-day:TYP:tree")]),
    ("a coverage target of 95 percent in WAB that no lid carries (fixture): feasibility item FI-03; row L3-OD1 keeps the target",
     [("od_l3_6.py", "coverage:WAB:95"), ("od_l3_1.py", "approve"), ("od_l3_2.py", "tablet-out"), ("od_l3_3.py", "2s2p"),
      ("od_l3_4.py", "adopt")]),
    ("row 1 before row 7: refused (D-27), then answered after it", [("od_l3_1.py", "approve"), ("od_l3_7.py", "72-required"),
                                                                     ("od_l3_1.py", "approve")]),
    ("48 hours required, 72 desired: rows 1 and 6 refused until restated from the runtime comparison; row 5 answered",
     [("od_l3_7.py", "48-required-72-desired"), ("od_l3_1.py", "approve"), ("od_l3_6.py", "mean-day:TYP"),
      ("od_l3_5.py", "reading-c")]),
    ("72 hours with an upgraded battery arrangement: row 1 refused until restated from the runtime comparison",
     [("od_l3_7.py", "72-required-battery-upgrade"), ("od_l3_1.py", "reject")]),
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
    print("Placeholder words 'dry run', date 2026-10-01. Nothing in the tree is written. The checked basis (fnd/l3plane cd8720a1,")
    print("CHECK-5) is filed, so the tree's rows are no longer held; the chains run on copies. Row L3-OD3's keep figures and")
    print("row L3-OD6's table come from FIXTURE files, except in the chain that reads the tree's filled table; row L3-OD4's band")
    print("is the basis's (none at U3's 6.0 A bracket); the push is a STAND-IN of 10 N for the owner's number, the pass line")
    print("kit-loads a stand-in for his sub-choice 1b, and 2 degrees the stand-in slope for a lid with no mechanical figure.")
    print("D-26: a target the studied candidate does not meet is recorded with its feasibility item; only requirements that")
    print("cannot both hold are refused. D-27: row L3-OD7 (M1's runtime) comes first; a chain reaching rows 1, 2, 4 or 6")
    print("starts with it answered 72-required, a STAND-IN for the owner's runtime answer.")
    print("The chains are examples, not recommendations.")
    for name, steps in CHAINS:
        if not any(s == "od_l3_7.py" for s, _ in steps) and any(s in RUNTIME_SCRIPTS for s, _ in steps):
            steps = [("od_l3_7.py", "72-required")] + list(steps)
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
            if script == "od_l3_4.py" and opt == "adopt": args += ["--push-n", "10"] + (["--slope-deg", "2"] if "slope" in parts else [])
            if script == "od_l3_1.py" and opt == "approve": args += ["--pass-line", "kit-loads"]
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
