#!/usr/bin/env python3
"""Read-only: dump the nodes of named nets from a KiCad 9 netlist (.net), with each ref's value.
Usage: netdump.py <file.net> NET [NET ...]   (a leading '/' on the stored name is ignored)"""
import re, sys
txt = open(sys.argv[1], encoding="utf-8").read()
comps = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', txt))
nets = {}
parts = txt.split('(net (code "')[1:]
for p in parts:
    m = re.match(r'(\d+)"\) \(name "([^"]*)"\)', p)
    name = m.group(2).lstrip("/")
    nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?', p)
    nets[name] = nodes
for want in sys.argv[2:]:
    ns = nets.get(want)
    if ns is None:
        print("%s: NOT IN NETLIST" % want); continue
    print("%s (%d nodes):" % (want, len(ns)))
    for ref, pin, fn in ns:
        print("   %s.%s %s | %s" % (ref, pin, ("(" + fn + ")") if fn else "", comps.get(ref, "?")[:120]))
