#!/usr/bin/env python3
"""Every connector-class part of a board, pin by pin, with the net and what else is on it (worker d8dec31).

Usage: dump_connectors.py <netlist.net>
A connector-class part is every reference that is not R, C, L, D, U, Q, FB, F, Y or X followed by a digit: the J, P, PAD,
JP, K, LED, TP, SW, BT, H and W families. Test points are listed in one block at the end. Ground nets are named, not expanded.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netread

GROUND = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)


def key(p):
    try: return (0, int(p))
    except ValueError: return (1, p)


def main(path):
    comps, nets = netread.read(path)
    tps = []
    for r in sorted(comps):
        if re.match(r"^(R|C|L|D|U|Q|FB|F|Y|X)\d", r): continue
        c = comps[r]
        if re.match(r"^TP\d", r):
            tps.append((r, c)); continue
        print("=== %s [%s] fp=%s LCSC=%s" % (r, c["value"], c["footprint"], c["fields"].get("LCSC", "")))
        for p in sorted(c["pins"], key=key):
            n = c["pins"][p]
            others = sorted((a, b) for a, b, _f, _t in nets[n] if a != r)
            if GROUND.match(n):
                print("    pin %-3s %-22s (ground, %d other nodes)" % (p, n, len(others)))
            else:
                print("    pin %-3s %-22s (%d) %s" % (p, n, len(others), ", ".join("%s.%s" % o for o in others[:40])
                                                     + (" ..." if len(others) > 40 else "")))
    print("=== test points")
    for r, c in tps:
        for p in sorted(c["pins"], key=key):
            print("    %-6s pin %s %-22s [%s]" % (r, p, c["pins"][p], c["value"][:80]))


if __name__ == "__main__":
    main(sys.argv[1])
