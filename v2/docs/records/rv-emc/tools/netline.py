#!/usr/bin/env python3
"""Read-only: print the line number of each named net's '(net (code' line in a KiCad netlist.
Usage: netline.py <file.net> NET [NET ...]"""
import re, sys
lines = open(sys.argv[1], encoding="utf-8").read().split("\n")
idx = {}
for i, l in enumerate(lines, 1):
    m = re.search(r'\(net \(code "\d+"\) \(name "([^"]*)"\)', l)
    if m: idx[m.group(1).lstrip("/")] = i
for n in sys.argv[2:]:
    print("%s:%s %s" % (sys.argv[1], idx.get(n, "NOT FOUND"), n))
