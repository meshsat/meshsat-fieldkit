#!/usr/bin/env python3
"""The configuration pins of every board's netlist moved to the files set 10 regenerated (MESHSAT-1357, 29 September 2026;
the widened form of records/int9/apply_repin_netlists_s98.py). Three configuration files pin a board's netlist by sha: the
review holds (tools/pcb_board_holds.yaml `netlist_sha16`), the reliability list's `written_against`
(tools/pcb_reliability.yaml) and the reviewed external pins (tools/pcb_port_reviews.json `netlist_sha256_16`). For each
board whose netlist changed, this script PROVES the change is the export's date and source lines only (main's file and the
tree's, those lines dropped, byte-identical), then moves every occurrence of the old sha16 in the three files to the new one,
re-parsing each. Refuses a changed body, a second run, or an old sha that no file carries. Run from the repository root."""
import hashlib, json, os, subprocess, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
NETS = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
        "c": "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
        "e": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net", "p": "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net"}
FILES = ["v2/ecad/tools/pcb_board_holds.yaml", "v2/ecad/tools/pcb_reliability.yaml", "v2/ecad/tools/pcb_port_reviews.json"]


def refuse(m):
    print("apply_repin_netlists_int11: REFUSED: %s" % m); sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def body(b): return b"\n".join(l for l in b.split(b"\n") if b"(date " not in l and b"(source " not in l)


def main():
    moves = {}
    for L, n in NETS.items():
        old = subprocess.run(["git", "-C", TOP, "show", "main:" + n], capture_output=True, check=True).stdout
        new = open(os.path.join(TOP, n), "rb").read()
        if old == new: continue
        if body(old) != body(new): refuse("%s differs from main's in more than its date and source lines" % n)
        moves[L] = (sha16(old), sha16(new))
    if not moves: refuse("no netlist changed")
    texts = {f: open(os.path.join(TOP, f), encoding="utf-8").read() for f in FILES}
    count = {}
    for L, (o, nw) in moves.items():
        n_old = sum(t.count(o) for t in texts.values())
        if n_old == 0 and sum(t.count(nw) for t in texts.values()): refuse("board %s is already moved (a second run)" % L)
        count[L] = n_old
        for f in FILES: texts[f] = texts[f].replace(o, nw)
    for f, t in texts.items(): (json.loads if f.endswith(".json") else yaml.safe_load)(t)
    for f, t in texts.items(): open(os.path.join(TOP, f), "w", encoding="utf-8").write(t)
    print("apply_repin_netlists_int11: " + "; ".join("%s %s -> %s (%d pin(s))" % (L.upper(), o, nw, count[L]) for L, (o, nw) in moves.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
