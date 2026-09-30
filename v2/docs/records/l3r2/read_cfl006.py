#!/usr/bin/env python3
"""CFL-006 re-read on the four files its reading is bound to (layer 3's second issue, L3-R2, MESHSAT-1357, 30 September
2026).

CFL-006 is CONFLICT_RESOLVED (resolved by owner ruling D-06: one 4S3P block of the Samsung INR18650-35E, about 145 Wh)
and reads FAIL, because its acceptance asks that one named cell and one parallel count be used by the energy chain, the
protection table, the runtime and the enclosure, and the enclosure lags. This script reads each bound file and prints,
fact by fact, what it carries; it exits 1 if any fact the registry sentence rests on does not hold, so the sentence is
never written on a file that says otherwise.

Facts read:
  P1  pcb_pack_protection.yaml names the 4S3P INR18650-35E block of about 145 Wh with parallel_min and parallel_max 3
  E1  pcb_energy_chain.yaml names the 4S3P block (D-06) as its pack source
  F1  pcb_board_facts.yaml names board P's one 4S3P block (D-06)
  C1  v2/cad/pack_4s.py is marked SUPERSEDED in its own docstring and names D-06's 4S3P block and S-27
  C2  v2/cad/pack_4s.py still draws the wrapped 4S4P block (its CELLS constant is commented as the 4S4P block)
  C3  no hold-down or enclosure of the 4S3P block is drawn by it (the docstring says the hold-down is not designed yet)

Usage: python3 read_cfl006.py        (from anywhere in the tree; prints the reading, exit 0 when every fact holds)
"""
import hashlib
import os
import re
import subprocess
import sys

TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=os.path.dirname(os.path.abspath(__file__)),
                     capture_output=True, check=True).stdout.decode().strip()
FILES = {
    "protection": "v2/ecad/tools/pcb_pack_protection.yaml",
    "chain": "v2/ecad/tools/pcb_energy_chain.yaml",
    "facts": "v2/ecad/tools/pcb_board_facts.yaml",
    "enclosure": "v2/cad/pack_4s.py",
}


def text(rel):
    return open(os.path.join(TOP, rel), encoding="utf-8").read()


def sha16(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()[:16]


def facts():
    t = {k: text(v) for k, v in FILES.items()}
    one = lambda s: " ".join(s.split())
    out = []
    out.append(("P1", bool(re.search(r'topology: "4S3P Samsung INR18650-35E, about 145 Wh"', t["protection"]))
                and bool(re.search(r"^\s*parallel_min: 3\b", t["protection"], re.M))
                and bool(re.search(r"^\s*parallel_max: 3\b", t["protection"], re.M)),
                "the protection table's pack block: topology 4S3P Samsung INR18650-35E, about 145 Wh; parallel_min 3, parallel_max 3"))
    out.append(("E1", "the 4S3P block (Samsung INR18650-35E, about 145 Wh; owner ruling D-06" in t["chain"],
                "the energy chain's pack source: the 4S3P block (Samsung INR18650-35E, about 145 Wh; owner ruling D-06)"))
    out.append(("F1", "one 4S3P block of Samsung INR18650-35E, about 145 Wh (owner ruling D-06)" in t["facts"],
                "the board facts: board P is the battery board of one 4S3P block of Samsung INR18650-35E, about 145 Wh (D-06)"))
    doc = one(t["enclosure"].split('"""')[1]) if t["enclosure"].count('"""') >= 2 else ""
    out.append(("C1", doc.startswith("SUPERSEDED") and "4S3P" in doc and "S-27" in doc,
                "the enclosure script's docstring opens SUPERSEDED, names D-06's shrink-wrapped 4S3P block and session item S-27"))
    out.append(("C2", bool(re.search(r"^CELLS = \([^)]*\)\s*# the wrapped 4S4P 18650 block", t["enclosure"], re.M)),
                "the enclosure script still draws the wrapped 4S4P 18650 block (its CELLS constant)"))
    out.append(("C3", "hold-down is not designed yet" in doc,
                "the enclosure script says the 4S3P block's hold-down is not designed yet"))
    return out


def main():
    ok = True
    for k, rel in FILES.items():
        print("file %-10s %s sha256/16 %s" % (k, rel, sha16(rel)))
    for fid, holds, what in facts():
        print("%s %s  %s" % (fid, "HOLDS " if holds else "FAILS ", what))
        ok = ok and holds
    print("reading: the cell and the parallel count agree in the protection table, the energy chain and the board facts "
          "(D-06); the enclosure script is superseded and still draws the 4S4P box, and no 4S3P enclosure or hold-down "
          "is drawn: CFL-006 stays FAIL on the enclosure alone (S-27)" if ok else "reading: NOT MADE, a fact failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
