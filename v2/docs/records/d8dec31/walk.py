#!/usr/bin/env python3
"""Walk a conductor from a connector pin: every node on its net, then through each two-pin series part to the next net
(worker d8dec31, decision 31's review). It prints; it judges nothing.

Usage: walk.py <netlist.net> <net> [hops]
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netread

GROUND = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)
SERIES = re.compile(r"^(R|F|FB|L|D|JP|C)\d")


def main(path, start, hops=2):
    comps, nets = netread.read(path)
    seen, frontier = {start}, [(start, 0, start)]
    while frontier:
        net, depth, how = frontier.pop(0)
        rows = nets.get(net)
        if rows is None:
            print("NET %s is not on this netlist" % net); continue
        print("%sNET %s (%d nodes)  [%s]" % ("  " * depth, net, len(rows), how))
        if len(rows) > 45:
            print("%s  (a rail or a bus of %d nodes: not expanded)" % ("  " * depth, len(rows))); continue
        for r, p, fn, ty in sorted(rows):
            c = comps[r]
            print("%s  %-10s pin %-3s %-14s %-12s %s" % ("  " * depth, r, p, fn[:14], ty[:12], c["value"][:100]))
            if depth < hops and SERIES.match(r) and len(c["pins"]) == 2 and not re.match(r"^C\d", r):
                for q, n2 in c["pins"].items():
                    if n2 != net and n2 not in seen and not GROUND.match(n2):
                        seen.add(n2); frontier.append((n2, depth + 1, "through %s" % r))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2)
