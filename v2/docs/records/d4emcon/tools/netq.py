#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): read-only netlist queries, so that every path of the EMCON census is a printed
reading and not a recollection. It parses with tx_inhibit.parse_netlist (the RF-002 instrument's own reader).

usage: netq.py --tools <v2/ecad/tools> --ecad <v2/ecad> <board letter> net <NET>...     every node of each net
       netq.py --tools ... --ecad ... <board letter> part <REF>...                     every pin of each part
       netq.py --tools ... --ecad ... <board letter> grep <regex>                      nets and parts matching
Board letters: A B C D E P (the committed netlists under <ecad>/pcb-*/out/)."""
import os, re, sys

PATHS = {"A": "pcb-a-power-a23/out/pcb-a-power.net", "B": "pcb-b-compute-b19/out/pcb-b-compute.net",
         "C": "pcb-c-display-c8/out/pcb-c-display.net", "D": "pcb-d-aprs-d9/out/pcb-d-aprs.net",
         "E": "pcb-e1-dock-e7/out/pcb-e1-dock.net", "P": "pcb-p-pack-p2/out/pcb-p-pack.net"}


def load(tools, ecad, letter):
    sys.path.insert(0, os.path.abspath(tools)); sys.dont_write_bytecode = True
    import tx_inhibit
    return tx_inhibit.parse_netlist(os.path.join(ecad, PATHS[letter]))


def show_net(nl, k, n):
    nodes = nl["nets"].get(n)
    if nodes is None: print("%s %s: NO SUCH NET" % (k, n)); return
    print("%s net %s (%d nodes)" % (k, n, len(nodes)))
    for r, p, f in sorted(nodes, key=lambda x: (re.sub(r"\d+", "", x[0]), len(x[0]), x[0], len(x[1]), x[1])):
        c = nl["comps"].get(r) or {}
        print("    %-10s pin %-4s %-18s %s [%s]" % (r, p, f or "-", (c.get("value") or "")[:90], (c.get("fp") or "").split(":")[-1][:30]))


def show_part(nl, k, ref):
    c = nl["comps"].get(ref)
    if c is None: print("%s %s: NO SUCH PART" % (k, ref)); return
    print("%s part %s: %s [%s] lib %s" % (k, ref, c.get("value"), c.get("fp"), c.get("lib")))
    for (r, p), n in sorted(nl["pin"].items(), key=lambda x: (len(x[0][1]), x[0][1])):
        if r == ref: print("    pin %-4s %-18s %s" % (p, nl["func"].get((r, p)) or "-", n))


def main(argv):
    tools = ecad = None
    while argv and argv[0].startswith("--"):
        if argv[0] == "--tools": tools = argv[1]
        elif argv[0] == "--ecad": ecad = argv[1]
        argv = argv[2:]
    if not tools or not ecad or len(argv) < 3: print(__doc__); return 2
    k, what, args = argv[0].upper(), argv[1], argv[2:]
    nl = load(tools, ecad, k)
    for a in args:
        if what == "net": show_net(nl, k, a)
        elif what == "part": show_part(nl, k, a)
        elif what == "grep":
            rx = re.compile(a, re.I)
            for n in sorted(nl["nets"]):
                if rx.search(n): print("%s net  %s (%d nodes)" % (k, n, len(nl["nets"][n])))
            for r, c in sorted(nl["comps"].items()):
                if rx.search(r) or rx.search(c.get("value") or ""): print("%s part %s: %s" % (k, r, (c.get("value") or "")[:110]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
