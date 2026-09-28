#!/usr/bin/env python3
"""The configuration pins of boards A's and B's netlists moved to the regenerated files (MESHSAT-1357, integration set 8,
28 September 2026, S-98). Three configuration files pin a board's netlist by sha: the decision 31 review hold of board A
(tools/pcb_board_holds.yaml `netlist_sha16`), the reliability list's `written_against` of boards A and B
(tools/pcb_reliability.yaml), and the reviewed set of external pins of board A (tools/pcb_port_reviews.json
`netlist_sha256_16`). The regeneration changed each netlist's date and source lines only; this script PROVES that again
(main's file and the tree's, those lines dropped, byte-identical) and then moves each pin, asserting every old value occurs
exactly once where it is expected and re-parsing each file. The re-taken readings said the same (reliability.py: "its
components and nets are the same (a re-export)"). The three files are configuration inputs of their tools, so the readings
are re-taken after this commit. Refuses a second run. Run from the repository root: python3 <this file>."""
import hashlib, json, os, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
NETS = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"}


def refuse(m):
    print("apply_repin_netlists_s98: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def body(b): return b"\n".join(l for l in b.split(b"\n") if b"(date " not in l and b"(source " not in l)


def main():
    sh = {}
    for L, n in NETS.items():
        old = subprocess.run(["git", "-C", TOP, "show", "main:" + n], capture_output=True, check=True).stdout
        new = open(os.path.join(TOP, n), "rb").read()
        if body(old) != body(new): refuse("%s differs from main's in more than its date and source lines" % n)
        sh[L] = (sha16(old), sha16(new))
    edits = [
        ("v2/ecad/tools/pcb_board_holds.yaml", [('netlist_sha16: "%s"' % sh["a"][0], 'netlist_sha16: "%s"' % sh["a"][1])]),
        ("v2/ecad/tools/pcb_reliability.yaml", [('path: "pcb-a-power-a23/out/pcb-a-power.net", sha256_16: "%s"' % sh["a"][0],
                                                   'path: "pcb-a-power-a23/out/pcb-a-power.net", sha256_16: "%s"' % sh["a"][1]),
                                                  ('path: "pcb-b-compute-b19/out/pcb-b-compute.net", sha256_16: "%s"' % sh["b"][0],
                                                   'path: "pcb-b-compute-b19/out/pcb-b-compute.net", sha256_16: "%s"' % sh["b"][1])]),
        ("v2/ecad/tools/pcb_port_reviews.json", [('"netlist_sha256_16": "%s"' % sh["a"][0], '"netlist_sha256_16": "%s"' % sh["a"][1])]),
    ]
    staged = {}
    for rel, pairs in edits:
        t = open(os.path.join(TOP, rel), encoding="utf-8").read()
        for o, n in pairs:
            if t.count(n) == 1 and t.count(o) == 0: refuse("%s already carries %s (a second run)" % (rel, n.split('"')[-2]))
            if t.count(o) != 1: refuse("%s: %r occurs %d times" % (rel, o, t.count(o)))
            t = t.replace(o, n)
        (json.loads if rel.endswith(".json") else yaml.safe_load)(t)
        staged[rel] = t
    for rel, t in staged.items(): open(os.path.join(TOP, rel), "w", encoding="utf-8").write(t)
    print("apply_repin_netlists_s98: pins moved after the content proof: A %s -> %s (holds, reliability, port reviews), B %s -> %s (reliability)"
          % (sh["a"][0], sh["a"][1], sh["b"][0], sh["b"][1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
