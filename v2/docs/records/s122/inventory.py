#!/usr/bin/env python3
"""Step 1 of stream s122 (S-122, MESHSAT-1357): collect every sentence of the documents CFL-016 names that names a part
reference, a net, a board, a rail, a gate function or a generator line, and write the list to `inventory.out` with a
count per document. The scope (which sections) is `s122lib.SCOPE`; the parser and the name finder are `s122lib`.

Writes only `inventory.out` beside this file (or prints it with --stdout). Run: python3 inventory.py [--stdout]."""
import os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402


def render(inv, nls):
    out = ["# Stream s122 inventory: every in-scope sentence of the documents CFL-016 names that names a part, net, board,",
           "# rail, gate function or generator line. Written by v2/docs/records/s122/inventory.py at the commit it ran in.",
           "# Netlists parsed (tx_inhibit.parse_netlist): " + ", ".join("%s %s@%s" % (k, nl["path"], nl["sha16"]) for k, nl in sorted(nls.items())),
           "# Documents: " + ", ".join("%s@%s" % (rel, L.sha16(rel)) for rel, _s in L.SCOPE),
           "# Scope: " + "; ".join("%s %s" % (os.path.basename(rel), "whole" if s == "ALL" else ", ".join(
               k + ("" if v is None else " (" + ", ".join(v) + ")") for k, v in s.items())) for rel, s in L.SCOPE),
           ""]
    counts = {}
    for sid, rel, key, kind, line, s, nm in inv:
        counts[rel] = counts.get(rel, 0) + 1
        tags = "; ".join("%s=%s" % (k, ",".join(x if isinstance(x, str) else ":".join(y for y in x if y) for x in v))
                         for k, v in nm.items() if v)
        out.append("%s [%s]" % (sid, L.sid_digest(s)))
        out.append("    " + s)
        out.append("    names: " + tags)
    out.append("")
    out.append("# counts per document")
    for rel, _s in L.SCOPE:
        out.append("%s: %d sentences" % (rel, counts.get(rel, 0)))
    out.append("total: %d sentences" % sum(counts.values()))
    return "\n".join(out) + "\n"


def main():
    nls = L.netlists()
    inv = L.inventory(nls)
    text = render(inv, nls)
    if "--stdout" in sys.argv:
        sys.stdout.write(text)
    else:
        open(os.path.join(HERE, "inventory.out"), "w", encoding="utf-8").write(text)
        print("inventory.py: %d sentences written to inventory.out" % len(inv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
