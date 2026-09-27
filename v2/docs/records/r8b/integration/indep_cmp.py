#!/usr/bin/env python3
"""Integration's own netlist comparison (MESHSAT-1357 round 8 set 3, 27 September 2026): not the author's netdiff_r8b.py.
Reads two KiCad s-expression netlists with its own reader, lists every component record difference (value, footprint,
each field, libsource) and every net whose node set differs (ref, pin, pinfunction, pintype), then holds each difference
against the author's per-finding list (expected_r8b.json: full-match regular expressions; parts_changed with the
attributes allowed to move; nets_changed with the refs allowed to join or leave). Usage:
  indep_cmp.py <old.net> <new.net> [--expect expected.json] [--drop FINDING:KIND ...]   exit 1 if anything is unexplained"""
import json, re, sys
def tok(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in "()": yield c; i += 1
        elif c.isspace(): i += 1
        elif c == '"':
            j = i + 1; b = []
            while s[j] != '"':
                if s[j] == "\\": b.append(s[j + 1]); j += 2
                else: b.append(s[j]); j += 1
            yield ("S", "".join(b)); i = j + 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in "()": j += 1
            yield ("S", s[i:j]); i = j
def parse(s):
    st = [[]]
    for t in tok(s):
        if t == "(": st.append([])
        elif t == ")": x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1])
    return st[0][0]
def get(x, k):
    for y in x:
        if isinstance(y, list) and y and y[0] == k: return y
def load(p):
    t = parse(open(p, encoding="utf-8").read())
    comps = {}
    for c in get(t, "components")[1:]:
        ref = get(c, "ref")[1]; rec = {}
        for key in ("value", "footprint", "datasheet", "description"):
            v = get(c, key); rec[key] = v[1] if v and len(v) > 1 else ""
        ls = get(c, "libsource")
        if ls: rec["libsource"] = tuple((q[0], q[1]) for q in ls[1:] if isinstance(q, list) and len(q) > 1)
        fl = get(c, "fields")
        if fl:
            for q in fl[1:]:
                if isinstance(q, list) and q[0] == "field":
                    nm = get(q, "name"); val = q[-1] if isinstance(q[-1], str) else ""
                    rec["field:" + (nm[1] if nm else "?")] = val
        comps[ref] = rec
    nets = {}
    for n in get(t, "nets")[1:]:
        nm = get(n, "name")[1]; nodes = set()
        for q in n:
            if isinstance(q, list) and q[0] == "node":
                d = {k[0]: k[1] for k in q[1:] if isinstance(k, list) and len(k) > 1}
                nodes.add((d.get("ref"), d.get("pin"), d.get("pinfunction", ""), d.get("pintype", "")))
        nets[nm] = nodes
    return comps, nets
def fm(pats, x): return any(re.fullmatch(p, x) for p in pats)
def main(a):
    old, new = a[0], a[1]
    exp = json.load(open(a[a.index("--expect") + 1])) if "--expect" in a else None
    drop = [a[i + 1] for i, x in enumerate(a) if x == "--drop"]
    (oc, on), (nc, nn) = load(old), load(new)
    diff = {"parts_added": sorted(set(nc) - set(oc)), "parts_removed": sorted(set(oc) - set(nc)),
            "parts_changed": {}, "nets_added": sorted(set(nn) - set(on)), "nets_removed": sorted(set(on) - set(nn)),
            "nets_changed": {}}
    for r in sorted(set(oc) & set(nc)):
        ks = sorted(k for k in set(oc[r]) | set(nc[r]) if oc[r].get(k) != nc[r].get(k))
        if ks: diff["parts_changed"][r] = ks
    for n in sorted(set(on) & set(nn)):
        if on[n] != nn[n]:
            diff["nets_changed"][n] = sorted({x[0] for x in on[n] ^ nn[n]})
    print("parts %d -> %d (+%d -%d ~%d); nets %d -> %d (+%d -%d ~%d)" % (len(oc), len(nc), len(diff["parts_added"]),
          len(diff["parts_removed"]), len(diff["parts_changed"]), len(on), len(nn), len(diff["nets_added"]),
          len(diff["nets_removed"]), len(diff["nets_changed"])))
    if exp is None:
        print(json.dumps(diff, indent=1)); return 0
    items = [f for f in exp["_findings"] if "%s:%s" % (f["finding"], f["kind"]) not in drop]
    un = []
    for kind in ("parts_added", "parts_removed", "nets_added", "nets_removed"):
        for x in diff[kind]:
            if not any(f["kind"] == kind and fm(f["patterns"], x) for f in items): un.append((kind, x))
    for r, ks in diff["parts_changed"].items():
        ok = [f for f in items if f["kind"] == "parts_changed" and fm(f["patterns"], r)]
        allowed = set(k for f in ok for k in (f.get("allowed") or []))
        bad = [k for k in ks if not (k in allowed or any(f.get("allowed") is None for f in ok))]
        if not ok or bad: un.append(("parts_changed", "%s %s" % (r, bad or ks)))
    for n, refs in diff["nets_changed"].items():
        ok = [f for f in items if f["kind"] == "nets_changed" and fm(f["patterns"], n)]
        if any(f.get("allowed") is None for f in ok): continue
        allowed = [p for f in ok for p in f["allowed"]]
        bad = [r for r in refs if not fm(allowed, r)]
        if not ok or bad: un.append(("nets_changed", "%s %s" % (n, bad or refs)))
    print("unexplained: %d" % len(un))
    for u in un: print("  UNEXPLAINED %s %s" % u)
    return 1 if un else 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
