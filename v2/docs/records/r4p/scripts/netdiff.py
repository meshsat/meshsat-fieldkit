#!/usr/bin/env python3
"""Semantic difference of two KiCad s-expression netlists (round 4 board P, 26 September 2026).
Prints: components removed, added, changed (value, footprint, LCSC, library symbol); then every pin whose net changed
(ref.pin: old -> new), grouped; then nets that exist on one side only. Pure Python.
Usage: netdiff.py <base.net> <new.net>"""
import re, sys
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
    return rd(0)[0][0]
def uq(s): return s[1:-1].replace('\\"', '"') if isinstance(s, str) and s.startswith('"') else s
def kids(n, k): return [e for e in n if isinstance(e, list) and e and e[0] == k]
def load(p):
    nl = parse(open(p, encoding="utf-8").read())
    comps = {}
    for c in kids(kids(nl, "components")[0], "comp"):
        ref = uq(kids(c, "ref")[0][1])
        d = {"value": uq(kids(c, "value")[0][1]), "footprint": uq(kids(c, "footprint")[0][1]) if kids(c, "footprint") else ""}
        ls = kids(c, "libsource"); d["lib"] = (uq(kids(ls[0], "lib")[0][1]) + ":" + uq(kids(ls[0], "part")[0][1])) if ls else ""
        f = {}
        for fl in kids(c, "fields"):
            for x in kids(fl, "field"):
                nm = [e for e in x if isinstance(e, list) and e[0] == "name"]
                if nm: f[uq(nm[0][1])] = uq(x[-1]) if isinstance(x[-1], str) else ""
        for x in kids(c, "property"):
            nm = kids(x, "name"); vl = kids(x, "value")
            if nm and vl: f.setdefault(uq(nm[0][1]), uq(vl[0][1]))
        d["LCSC"] = f.get("LCSC", "")
        comps[ref] = d
    pins, nets = {}, {}
    for n in kids(kids(nl, "nets")[0], "net"):
        name = uq(kids(n, "name")[0][1]); nodes = set()
        for nd in kids(n, "node"):
            r, p = uq(kids(nd, "ref")[0][1]), uq(kids(nd, "pin")[0][1]); nodes.add((r, p)); pins[(r, p)] = name
        nets[name] = nodes
    return comps, pins, nets
b, n = load(sys.argv[1]), load(sys.argv[2])
bc, bp, bn = b; nc, np_, nn = n
print("components: base %d, new %d" % (len(bc), len(nc)))
rm = sorted(set(bc) - set(nc)); ad = sorted(set(nc) - set(bc))
print("REMOVED components (%d):" % len(rm))
for r in rm: print("  - %-6s %-40s %s  LCSC %s" % (r, bc[r]["value"][:40], bc[r]["footprint"], bc[r]["LCSC"]))
print("ADDED components (%d):" % len(ad))
for r in ad: print("  + %-6s %-40s %s  LCSC %s  [%s]" % (r, nc[r]["value"][:40], nc[r]["footprint"], nc[r]["LCSC"], nc[r]["lib"]))
print("CHANGED components:")
for r in sorted(set(bc) & set(nc)):
    for k in ("value", "footprint", "LCSC", "lib"):
        if bc[r][k] != nc[r][k]: print("  ~ %-6s %-9s %r -> %r" % (r, k, bc[r][k], nc[r][k]))
print("PIN NET CHANGES on components present on both sides:")
common = set(bc) & set(nc)
ch = sorted(k for k in set(bp) | set(np_) if k[0] in common and bp.get(k) != np_.get(k))
for k in ch: print("  %s.%s: %s -> %s" % (k[0], k[1], bp.get(k, "(no node)"), np_.get(k, "(no node)")))
print("NETS only in base: %s" % sorted(set(bn) - set(nn)))
print("NETS only in new: %s" % sorted(set(nn) - set(bn)))
print("NETS on both sides whose node set changed:")
for name in sorted(set(bn) & set(nn)):
    if bn[name] != nn[name]:
        print("  %s: -%s +%s" % (name, sorted("%s.%s" % x for x in bn[name] - nn[name]), sorted("%s.%s" % x for x in nn[name] - bn[name])))
