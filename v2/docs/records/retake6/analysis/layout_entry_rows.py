#!/usr/bin/env python3
"""retake6: the layout-entry rows of CURRENT-EVIDENCE.md, per board, parsed from the page's own table.

Usage: layout_entry_rows.py <label>=<page> [<label>=<page> ...]
Reads the section "Layout entry, per board: the exact remaining blockers" of each page (the table whose header begins
"| board | rule | reading now |") and prints, per board, the count and each reason (rule or decision or blocker with
its result, and the reading's class). It reads pages; it writes nothing and decides nothing.
"""
import sys, collections

ORDER = ["A", "B", "C", "D", "E", "P", "E5"]


def rows(path):
    out = collections.OrderedDict((b, []) for b in ORDER)
    on = False
    for line in open(path, encoding="utf-8"):
        if line.startswith("| board | rule | reading now |"): on = True; continue
        if on:
            if not line.startswith("|"):
                if out and any(out.values()): break
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if set(c[0]) <= set("-"): continue
            out.setdefault(c[0], []).append((c[1], c[2]))
    return out


if __name__ == "__main__":
    pages = [a.split("=", 1) for a in sys.argv[1:]]
    data = [(lab, rows(p)) for lab, p in pages]
    for lab, d in data:
        print("%s: %d reasons: %s" % (lab, sum(len(v) for v in d.values()), ", ".join("%s %d" % (b, len(d[b])) for b in ORDER)))
    for b in ORDER:
        print("\nboard %s" % b)
        for lab, d in data:
            print("  %s (%d):" % (lab, len(d[b])))
            for r, cls in d[b]: print("     %-24s %s" % (r, cls))
