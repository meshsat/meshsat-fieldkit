#!/usr/bin/env python3
"""Read-only: list every pin of the given refs with the net it lands on, from a KiCad 9 netlist.
Usage: refdump.py <file.net> REF [REF ...]"""
import re, sys
txt = open(sys.argv[1], encoding="utf-8").read()
comps = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
pins = {}
for p in txt.split('(net (code "')[1:]:
    name = re.match(r'(\d+)"\) \(name "([^"]*)"\)', p).group(2).lstrip("/")
    for ref, pin, fn in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?', p):
        pins.setdefault(ref, []).append((pin, fn, name))
def k(t):
    try: return (0, int(t[0]))
    except ValueError: return (1, t[0])
for ref in sys.argv[2:]:
    print("%s | %s" % (ref, comps.get(ref, "NOT IN NETLIST")[:140]))
    for pin, fn, name in sorted(pins.get(ref, []), key=k):
        print("   pin %s (%s) -> %s" % (pin, fn, name))
