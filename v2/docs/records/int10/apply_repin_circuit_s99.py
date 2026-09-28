#!/usr/bin/env python3
"""Board A's three configuration pins moved to its regenerated netlist after S-99's CIRCUIT change (MESHSAT-1357, integration
set 9, 29 September 2026). Unlike set 8's re-export, the content changed (decision 55: the D8 split), so each pin moves only
on a proof that its subject is untouched, computed here and never typed:
  * the parts: parsed from main's netlist and the tree's (tx_inhibit.parse_netlist), the added parts are exactly the ten of
    the D8 split (U41, L13, C227 to C232, R217, R218) and none is removed;
  * the decision 31 review hold (tools/pcb_board_holds.yaml `netlist_sha16`) and the reviewed port set
    (tools/pcb_port_reviews.json `netlist_sha256_16`): the review's subject is the exposed conductors; every external pin
    the reviewed set holds for board A is on the same net in the new netlist (netlist_board.read_netlist), and no added
    part is a connector;
  * the reliability list (tools/pcb_reliability.yaml `written_against` of board A): the tool's own inventory, run on the
    new netlist in scratch, gives the same candidates, classed, excluded and refused counts as main's reading, and the new
    line is the one `reliability.py --pins` prints.
Refuses when any proof fails or on a second run. Run from the repository root: python3 <this file>."""
import hashlib, json, os, subprocess, sys, tempfile

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2/ecad/tools")
sys.path.insert(0, TOOLS)
import tx_inhibit as TX
import netlist_board as NB
NET = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
ADDED = {"U41", "L13", "C227", "C228", "C229", "C230", "C231", "C232", "R217", "R218"}


def refuse(m):
    print("apply_repin_circuit_s99: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def main():
    old_b = subprocess.run(["git", "-C", TOP, "show", "main:" + NET], capture_output=True, check=True).stdout
    new_p = os.path.join(TOP, NET)
    new_b = open(new_p, "rb").read()
    o16, n16 = sha16(old_b), sha16(new_b)
    if o16 == n16: refuse("board A's netlist is main's")
    with tempfile.TemporaryDirectory() as td:
        op = os.path.join(td, "old.net")
        open(op, "wb").write(old_b)
        old, new = TX.parse_netlist(op), TX.parse_netlist(new_p)
        old_pins = NB.read_netlist(op)
    new_pins = NB.read_netlist(new_p)
    added, removed = set(new["comps"]) - set(old["comps"]), set(old["comps"]) - set(new["comps"])
    if added != ADDED or removed: refuse("parts added %s removed %s, expected exactly the D8 split's ten" % (sorted(added), sorted(removed)))
    if any(r[:1] in ("J", "P", "X") for r in added): refuse("an added part is a connector")
    rev = json.load(open(os.path.join(TOOLS, "pcb_port_reviews.json"), encoding="utf-8"))
    ext = rev["boards"]["a"]["external"]
    bad = []
    for ref, pins in ext.items():
        for pin, net in pins.items():
            got = (new_pins.get(ref) or {}).get(str(pin))
            if got is None or got.lstrip("/") != str(net).lstrip("/"): bad.append("%s.%s %s -> %s" % (ref, pin, net, got))
    if bad: refuse("reviewed external pins moved: %s" % bad[:5])
    npins = sum(len(v) for v in ext.values())
    # the reliability inventory on the new netlist, in scratch, against main's reading
    with tempfile.TemporaryDirectory() as vd:
        subprocess.run([sys.executable, "tools/reliability.py", "--ecad", os.path.join(TOP, "v2/ecad"), "--board", "a"],
                       cwd=os.path.join(TOP, "v2/ecad"), env=dict(os.environ, VERDICT_DIR=vd), capture_output=True)
        vs = [f for f in os.listdir(vd) if f.endswith(".json")]
        if not vs: refuse("reliability.py wrote no reading in scratch")
        nr = json.load(open(os.path.join(vd, vs[0]), encoding="utf-8"))
    main_r = json.loads(subprocess.run(["git", "-C", TOP, "show", "main:v2/ecad/pcb-a-power-a23/routed/reliability.verdict.json"],
                                       capture_output=True, check=True).stdout)
    keys = ("candidates", "classed", "excluded", "refused")
    cn, cm = [(nr.get("counts") or {}).get(k) for k in keys], [(main_r.get("counts") or {}).get(k) for k in keys]
    if cn != cm: refuse("the reliability inventory changed: %s against main's %s" % (cn, cm))
    pins_out = subprocess.run([sys.executable, "reliability.py", "--pins"], cwd=TOOLS, capture_output=True, text=True).stdout
    line = [l for l in pins_out.split("\n") if '"pcb-a-power-a23/out/pcb-a-power.net"' in l]
    if len(line) != 1 or n16 not in line[0]: refuse("reliability.py --pins does not print board A's line at %s" % n16)
    new_wa = line[0].strip().split("   #")[0].strip()
    # the three moves
    edits = []
    hp = os.path.join(TOOLS, "pcb_board_holds.yaml")
    ht = open(hp, encoding="utf-8").read()
    if ht.count('netlist_sha16: "%s"' % o16) != 1: refuse("the hold does not pin %s once" % o16)
    edits.append((hp, ht.replace('netlist_sha16: "%s"' % o16, 'netlist_sha16: "%s"' % n16), yaml.safe_load))
    rp = os.path.join(TOOLS, "pcb_reliability.yaml")
    rt = open(rp, encoding="utf-8").read()
    olds = [l for l in rt.split("\n") if l.strip().startswith("written_against:") and '"pcb-a-power-a23/out/pcb-a-power.net"' in l]
    if len(olds) != 1 or o16 not in olds[0]: refuse("the reliability list does not pin board A at %s once" % o16)
    indent = olds[0][:len(olds[0]) - len(olds[0].lstrip())]
    edits.append((rp, rt.replace(olds[0], indent + new_wa), yaml.safe_load))
    pp = os.path.join(TOOLS, "pcb_port_reviews.json")
    pt = open(pp, encoding="utf-8").read()
    if pt.count('"netlist_sha256_16": "%s"' % o16) != 1: refuse("the reviewed set does not pin %s once" % o16)
    edits.append((pp, pt.replace('"netlist_sha256_16": "%s"' % o16, '"netlist_sha256_16": "%s"' % n16), json.loads))
    for p, t, parse in edits:
        parse(t)
    for p, t, _ in edits:
        open(p, "w", encoding="utf-8").write(t)
    print("apply_repin_circuit_s99: board A %s -> %s; added parts %s (none a connector); %d reviewed external pins on the same nets; "
          "reliability inventory unchanged %s; pins moved in pcb_board_holds.yaml, pcb_reliability.yaml (%s), pcb_port_reviews.json"
          % (o16, n16, ", ".join(sorted(added)), npins, dict(zip(keys, cn)), new_wa))
    return 0


if __name__ == "__main__":
    sys.exit(main())
