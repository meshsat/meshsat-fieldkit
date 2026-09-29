#!/usr/bin/env python3
"""Boards B and C's netlist pins in the reliability list moved to their regenerated netlists after set 12's CIRCUIT change
(MESHSAT-1357, 29 September 2026; stream d4emcon's FEA-002 remedies B-1 to B-5 and D4E-F1). The content changed, so each pin
moves only on a proof, computed here and never typed: (1) the parts, parsed from main's netlist and the tree's
(tx_inhibit.parse_netlist): on B the added parts are exactly the gates and buffers U537 to U554, the resistors R532 to R550
and the decoupling capacitors C668 to C685 the generator's decoupling library adds for them, the changed ones exactly R41,
R42, R238, R527 and U536, none removed; on C exactly R52 and D23 added; no added part is a connector; (2) the reliability
inventory, run on the new netlists in scratch, gives the same candidate, classed, excluded and refused counts as main's
reading; (3) the new line is the one `reliability.py --pins` prints. No hold or reviewed port set pins boards B and C.
A board already pinned at its current netlist is left as it is, so the script moves a pin again after a later
re-export of the same content (board C after its EMCON_HW node declaration), always proving against main.
Widened after the set 12 check's minors (apply_b_chk12.py): board B also adds R551 (U543's timing tie).
Refuses when a proof fails; a board already pinned is re-proved and left as it is, and the file is written again (the set 12 check's m6). Run from the repository root: python3 <this file>."""
import hashlib, json, os, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
sys.path.insert(0, TOOLS)
import tx_inhibit as TX

def rng(p, a, b): return {"%s%d" % (p, i) for i in range(a, b + 1)}
BOARDS = (
    ("b", "pcb-b-compute-b19", "pcb-b-compute", rng("U", 537, 554) | rng("R", 532, 551) | rng("C", 668, 685),
     {"R41", "R42", "R238", "R527", "U536"}),
    ("c", "pcb-c-display-c8", "pcb-c-display", {"R52", "D23"}, set()),
)
KEYS = ("candidates", "classed", "excluded", "refused")


def refuse(m):
    print("apply_repin_bc_set12: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def main():
    rp = os.path.join(TOOLS, "pcb_reliability.yaml")
    rt = open(rp, encoding="utf-8").read()
    pins_out = subprocess.run([sys.executable, "reliability.py", "--pins"], cwd=TOOLS, capture_output=True, text=True).stdout
    report = []
    for L, pd, stem, want_add, want_chg in BOARDS:
        rel = "v2/ecad/%s/out/%s.net" % (pd, stem)
        old_b = subprocess.run(["git", "-C", TOP, "show", "main:" + rel], capture_output=True, check=True).stdout
        new_p = os.path.join(TOP, rel)
        o16, n16 = sha16(old_b), sha16(open(new_p, "rb").read())
        if o16 == n16: refuse("board %s: the netlist is main's" % L)
        with tempfile.TemporaryDirectory() as td:
            op = os.path.join(td, "old.net"); open(op, "wb").write(old_b)
            old = TX.parse_netlist(op)
        new = TX.parse_netlist(new_p)
        oc, nc = old["comps"], new["comps"]
        added, removed = set(nc) - set(oc), set(oc) - set(nc)
        chg = {r for r in set(oc) & set(nc) if (oc[r]["value"], oc[r].get("fp")) != (nc[r]["value"], nc[r].get("fp"))}
        if added != want_add or removed or chg != want_chg:
            refuse("board %s: added %s, removed %s, changed %s" % (L, sorted(added ^ want_add), sorted(removed), sorted(chg ^ want_chg)))
        if any(r[:1] in ("J", "P", "X") for r in added): refuse("board %s: an added part is a connector" % L)
        with tempfile.TemporaryDirectory() as vd:
            subprocess.run([sys.executable, "tools/reliability.py", "--ecad", os.path.join(TOP, "v2/ecad"), "--board", L],
                           cwd=os.path.join(TOP, "v2/ecad"), env=dict(os.environ, VERDICT_DIR=vd), capture_output=True)
            vs = [f for f in os.listdir(vd) if f.endswith(".json")]
            if not vs: refuse("board %s: reliability.py wrote no reading in scratch" % L)
            nr = json.load(open(os.path.join(vd, vs[0]), encoding="utf-8"))
        mr = json.loads(subprocess.run(["git", "-C", TOP, "show", "main:v2/ecad/%s/routed/reliability.verdict.json" % pd], capture_output=True, check=True).stdout)
        cn, cm = [(nr.get("counts") or {}).get(k) for k in KEYS], [(mr.get("counts") or {}).get(k) for k in KEYS]
        if cn != cm: refuse("board %s: the reliability inventory changed %s against %s" % (L, cn, cm))
        line = [l for l in pins_out.split("\n") if '"%s/out/%s.net"' % (pd, stem) in l]
        if len(line) != 1 or n16 not in line[0]: refuse("board %s: reliability.py --pins does not print its line at %s" % (L, n16))
        new_wa = line[0].strip().split("   #")[0].strip()
        olds = [l for l in rt.split("\n") if l.strip().startswith("written_against:") and '"%s/out/%s.net"' % (pd, stem) in l]
        if len(olds) != 1: refuse("board %s: the list does not pin its netlist once" % L)
        if n16 in olds[0]: report.append("board %s already pinned at %s" % (L.upper(), n16)); continue
        indent = olds[0][:len(olds[0]) - len(olds[0].lstrip())]
        rt = rt.replace(olds[0], indent + new_wa)
        report.append("board %s %s -> %s: added %d, changed %s, inventory %s" % (L.upper(), o16, n16, len(added), ", ".join(sorted(chg)) or "none", dict(zip(KEYS, cn))))
    yaml.safe_load(rt)
    open(rp, "w", encoding="utf-8").write(rt)
    for r in report: print("apply_repin_bc_set12: " + r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
