#!/usr/bin/env python3
"""Update footprint Value fields on a routed board from the schematic netlist (BOM strings only; no placement change). Usage: set_values.py <board> <netlist.net>"""
import sys, re, pcbnew
def parse(s):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def rd(i):
        out = []
        while i < len(tok):
            t = tok[i]
            if t == "(": sub, i = rd(i + 1); out.append(sub)
            elif t == ")": return out, i + 1
            else: out.append(t); i += 1
        return out, i
    return rd(0)[0]
def uq(s): return s[1:-1] if s.startswith('"') else s
def kids(n, key): return [e for e in n if isinstance(e, list) and e and e[0] == key]
nl = parse(open(sys.argv[2]).read())[0]; vals = {}
for c in kids(kids(nl, "components")[0], "comp"): vals[uq(kids(c, "ref")[0][1])] = uq(kids(c, "value")[0][1])
b = pcbnew.LoadBoard(sys.argv[1]); n = 0
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r in vals and fp.GetValue() != vals[r]: print("  %s: %s -> %s" % (r, fp.GetValue()[:40], vals[r][:60])); fp.SetValue(vals[r]); n += 1
missing = [r for r in vals if not r.startswith("#") and r not in {f.GetReference() for f in b.GetFootprints()}]
pcbnew.SaveBoard(sys.argv[1], b); print("set_values: %d values updated; parts in the netlist but not on the board: %s" % (n, missing))
