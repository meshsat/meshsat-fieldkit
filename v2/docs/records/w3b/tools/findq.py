#!/usr/bin/env python3
"""findq.py <txt> <regex> [context lines]: the physical page (form feeds counted) and lines of every match."""
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 2
pages = t.split("\f")
rx = re.compile(sys.argv[2], re.I)
for pi, pg in enumerate(pages, 1):
    L = pg.split("\n")
    for i, l in enumerate(L):
        if rx.search(l):
            print("--- page %d line %d" % (pi, i + 1))
            for k in range(max(0, i - ctx), min(len(L), i + ctx + 1)): print("   " + L[k].rstrip()[:200])
