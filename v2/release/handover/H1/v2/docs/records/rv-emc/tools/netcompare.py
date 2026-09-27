#!/usr/bin/env python3
"""Read-only: compare two KiCad 9 netlists net by net (node sets) and part by part (values).
Usage: netcompare.py <read.net> <other.net>"""
import re, sys
def load(path):
    txt = open(path, encoding="utf-8").read()
    comps = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
    nets = {}
    for p in txt.split('(net (code "')[1:]:
        m = re.match(r'(\d+)"\) \(name "([^"]*)"\)', p)
        nets[m.group(2)] = frozenset(re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', p))
    return comps, nets
ca, na = load(sys.argv[1]); cb, nb = load(sys.argv[2])
nets = sorted(n for n in set(na) | set(nb) if na.get(n) != nb.get(n))
parts = sorted((r, ca.get(r), cb.get(r)) for r in set(ca) | set(cb) if ca.get(r) != cb.get(r))
print("read: %s  other: %s" % (sys.argv[1], sys.argv[2]))
print("nets changed: %d %s" % (len(nets), nets))
print("parts changed: %d %s" % (len(parts), parts))
