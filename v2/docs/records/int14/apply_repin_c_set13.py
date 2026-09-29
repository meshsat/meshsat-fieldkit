#!/usr/bin/env python3
"""Board C's netlist pin in the reliability list moved to its regenerated netlist after set 13's circuit change (MESHSAT-1357,
29 September 2026; stream csi's CSI-D3: four 27R series resistors R53 to R56 on the e-paper lines; a copy of
records/int13/apply_repin_c_set13.py narrowed to board C). The content changed, so the pin moves only on a proof computed
here and never typed: (1) the parts, parsed from main's netlist and the tree's (tx_inhibit.parse_netlist): exactly R53 to
R56 added, none removed or changed in value or footprint, none a connector; (2) the reliability inventory, run on the new
netlist in scratch, gives the same candidate, classed, excluded and refused counts as main's reading; (3) the new line is
the one `reliability.py --pins` prints. A board already pinned at its current netlist is left as it is. Refuses when a
proof fails. Run from the repository root: python3 <this file>."""
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
    ("c", "pcb-c-display-c8", "pcb-c-display", rng("R", 53, 56), set()),
)
KEYS = ("candidates", "classed", "excluded", "refused")


def refuse(m):
    print("apply_repin_c_set13: REFUSED: %s" % m)
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
    for r in report: print("apply_repin_c_set13: " + r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
