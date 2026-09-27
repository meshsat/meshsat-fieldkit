#!/usr/bin/env python3
"""Independent netlist comparison for MESHSAT-1357 round 8, board B (stream b). Written for this round; reads two KiCad 9
kicadsexpr netlists with its own s-expression reader (no project tool, no kisch) and compares:
  - every component record: value, footprint, the LCSC field, libsource lib/part, and every other field;
  - every net, by NAME, as the set of its nodes (ref, pin, pinfunction, pintype);
  - and, independent of names, every net by its node set, so a rename with unchanged membership reads as a rename.
It prints a JSON report: parts added, removed, changed (field by field); nets added, removed, changed (nodes in/out);
nets renamed (same nodes, new name). A second argument set, --expect <json>, classifies each difference against the
round's declared change list and prints every UNEXPLAINED difference; exit 1 if any.
Usage: netdiff_r8b.py <old.net> <new.net> [--expect expected.json] [--out report.json]"""
import json, re, sys

def parse(text):
    tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop(); cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"').replace("\\\\", "\\") if t.startswith('"') else t)
    return cur[0]

def kids(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]

def one(node, name, default=None):
    k = kids(node, name)
    return k[0][1] if k and len(k[0]) > 1 else default

def load(path):
    root = parse(open(path, encoding="utf-8").read())
    comps, nets = {}, {}
    for comp in kids(kids(root, "components")[0], "comp"):
        ref = one(comp, "ref")
        rec = {"value": one(comp, "value"), "footprint": one(comp, "footprint")}
        for f in (kids(comp, "fields")[0] if kids(comp, "fields") else []):
            if isinstance(f, list) and f[0] == "field":
                nm = one(f, "name"); val = f[-1] if isinstance(f[-1], str) and len(f) > 2 else ""
                rec["field:" + nm] = val
        ls = kids(comp, "libsource")
        if ls: rec["lib"] = one(ls[0], "lib"); rec["part"] = one(ls[0], "part")
        comps[ref] = rec
    for net in kids(kids(root, "nets")[0], "net"):
        name = one(net, "name")
        nodes = set()
        for n in kids(net, "node"):
            nodes.add((one(n, "ref"), one(n, "pin"), one(n, "pinfunction", ""), one(n, "pintype", "")))
        nets[name] = nodes
    return comps, nets

def main(a):
    old, new = a[0], a[1]
    exp = json.load(open(a[a.index("--expect") + 1])) if "--expect" in a else None
    out = a[a.index("--out") + 1] if "--out" in a else None
    oc, on = load(old); nc, nn = load(new)
    rep = {"old": old, "new": new,
           "parts_old": len(oc), "parts_new": len(nc), "nets_old": len(on), "nets_new": len(nn),
           "parts_added": sorted(set(nc) - set(oc)), "parts_removed": sorted(set(oc) - set(nc)), "parts_changed": {},
           "nets_added": sorted(set(nn) - set(on)), "nets_removed": sorted(set(on) - set(nn)), "nets_changed": {}}
    for r in sorted(set(oc) & set(nc)):
        d = {k: [oc[r].get(k), nc[r].get(k)] for k in sorted(set(oc[r]) | set(nc[r])) if oc[r].get(k) != nc[r].get(k)}
        if d: rep["parts_changed"][r] = d
    for n in sorted(set(on) & set(nn)):
        if on[n] != nn[n]:
            rep["nets_changed"][n] = {"out": sorted(map(list, on[n] - nn[n])), "in": sorted(map(list, nn[n] - on[n]))}
    # nets whose node set is unchanged but whose name is: a pure rename
    byset_old = {frozenset(v): k for k, v in on.items()}
    rep["nets_renamed"] = {byset_old[frozenset(nn[n])]: n for n in rep["nets_added"] if frozenset(nn[n]) in byset_old
                           and byset_old[frozenset(nn[n])] in rep["nets_removed"]}
    unexplained = []
    if exp is not None:
        pa, pr = set(exp.get("parts_added", [])), set(exp.get("parts_removed", []))
        pc = exp.get("parts_changed", {})
        na, nr, nch = set(exp.get("nets_added", [])), set(exp.get("nets_removed", [])), exp.get("nets_changed", {})
        rx = lambda pats, x: any(re.fullmatch(p, x) for p in pats)
        for r in rep["parts_added"]:
            if not rx(pa, r): unexplained.append("part added " + r)
        for r in rep["parts_removed"]:
            if not rx(pr, r): unexplained.append("part removed " + r)
        for r, d in rep["parts_changed"].items():
            allowed = [set(v) for k, v in pc.items() if re.fullmatch(k, r)]
            for f in d:
                if not any(f in s for s in allowed): unexplained.append("part %s field %s %r -> %r" % (r, f, d[f][0], d[f][1]))
        for n in rep["nets_added"]:
            if not rx(na, n): unexplained.append("net added " + n)
        for n in rep["nets_removed"]:
            if not rx(nr, n): unexplained.append("net removed " + n)
        for n, d in rep["nets_changed"].items():
            pats = [v for k, v in nch.items() if re.fullmatch(k, n)]
            if not pats: unexplained.append("net changed %s (out %s, in %s)" % (n, d["out"], d["in"])); continue
            refs = pats[0]
            for node in d["out"] + d["in"]:
                if not rx(refs, node[0]): unexplained.append("net %s node %s.%s moved (%s)" % (n, node[0], node[1], "out" if node in d["out"] else "in"))
        rep["unexplained"] = unexplained
    s = json.dumps(rep, indent=1, sort_keys=True)
    if out: open(out, "w").write(s + "\n")
    print("parts %d -> %d (+%d -%d ~%d); nets %d -> %d (+%d -%d ~%d, renamed %d)" % (
        len(oc), len(nc), len(rep["parts_added"]), len(rep["parts_removed"]), len(rep["parts_changed"]),
        len(on), len(nn), len(rep["nets_added"]), len(rep["nets_removed"]), len(rep["nets_changed"]), len(rep.get("nets_renamed", {}))))
    if exp is not None:
        print("unexplained: %d" % len(unexplained))
        for u in unexplained[:200]: print("  " + u)
        return 1 if unexplained else 0
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
