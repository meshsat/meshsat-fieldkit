#!/usr/bin/env python3
"""An independent netlist comparison for the w3de parity proof (MESHSAT-1357, 27 September 2026).

It does not use regen_compare.py or netlist_parts.py: it tokenises the two KiCad s-expression netlists itself and
compares EVERY component (reference, value, footprint, every field) and EVERY net (its name and the set of (reference,
pin) on it), then lists each pin whose net changed. With --expect <json> it checks the differences against an
expected-change list and exits 1 on anything unexpected or on an expected change that did not happen.

  net_compare.py <committed.net> <candidate.net> [--expect expected.json] [--json]

expected.json: {"components_added": [ref...], "components_removed": [ref...], "components_changed": {ref: [field...]},
                "pins_moved": {"REF.PIN": ["old net", "new net"], ...}, "nets_added": [...], "nets_removed": [...]}
Pins on an added component are reported under pins_added, and those on a removed one under pins_removed; net names
are compared without a leading slash."""
import json, re, sys

def tokens(s):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)

def parse(s):
    toks = tokens(s); pos = 0
    def rd():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == "(":
            out = []
            while toks[pos] != ")": out.append(rd())
            pos += 1; return out
        return t[1:-1] if t.startswith('"') else t
    return rd()

def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]

def load(path):
    root = parse(open(path, encoding="utf-8").read())
    comps = {}
    for c in find(find(root, "components")[0], "comp"):
        d = {}
        for x in c[1:]:
            if not isinstance(x, list): continue
            k = x[0]
            if k in ("ref", "value", "footprint", "datasheet", "description"): d[k] = x[1] if len(x) > 1 else ""
            elif k == "fields":
                for f in find(x, "field"):
                    nm = [y for y in f if isinstance(y, list) and y[0] == "name"]
                    val = [y for y in f[1:] if not isinstance(y, list)]
                    d["field:" + (nm[0][1] if nm else "?")] = val[0] if val else ""
            elif k == "libsource":
                d["libsource"] = " ".join("%s=%s" % (y[0], y[1]) for y in x[1:] if isinstance(y, list) and len(y) > 1)
            elif k == "property":
                nm = [y for y in x if isinstance(y, list) and y[0] == "name"]; vl = [y for y in x if isinstance(y, list) and y[0] == "value"]
                d["property:" + (nm[0][1] if nm else "?")] = vl[0][1] if vl else ""
        comps[d["ref"]] = d
    nets = {}; pin_net = {}
    for n in find(find(root, "nets")[0], "net"):
        name = [x for x in n if isinstance(x, list) and x[0] == "name"][0][1].lstrip("/")
        pins = set()
        for nd in find(n, "node"):
            r = [x for x in nd if isinstance(x, list) and x[0] == "ref"][0][1]
            p = [x for x in nd if isinstance(x, list) and x[0] == "pin"][0][1]
            pins.add((r, p)); pin_net["%s.%s" % (r, p)] = name
        nets[name] = pins
    return comps, nets, pin_net

def compare(a, b):
    ca, na, pa = load(a); cb, nb, pb = load(b)
    res = {"components_added": sorted(set(cb) - set(ca)), "components_removed": sorted(set(ca) - set(cb)),
           "components_changed": {}, "nets_added": sorted(set(nb) - set(na)), "nets_removed": sorted(set(na) - set(nb)),
           "pins_moved": {}, "pins_added": {}, "pins_removed": {}, "counts": {}}
    for r in sorted(set(ca) & set(cb)):
        ch = sorted(k for k in set(ca[r]) | set(cb[r]) if ca[r].get(k) != cb[r].get(k))
        if ch: res["components_changed"][r] = {k: [ca[r].get(k), cb[r].get(k)] for k in ch}
    for k in sorted(set(pa) | set(pb)):
        r = k.split(".")[0]
        if k in pa and k in pb and pa[k] != pb[k]: res["pins_moved"][k] = [pa[k], pb[k]]
        elif k not in pa: res["pins_added"][k] = pb[k]
        elif k not in pb: res["pins_removed"][k] = pa[k]
    res["counts"] = {"components": [len(ca), len(cb)], "nets": [len(na), len(nb)], "pins": [len(pa), len(pb)]}
    return res

def check(res, exp):
    bad = []
    for key in ("components_added", "components_removed", "nets_added", "nets_removed"):
        if sorted(res[key]) != sorted(exp.get(key, [])): bad.append("%s: got %s, expected %s" % (key, res[key], exp.get(key, [])))
    ec = exp.get("components_changed", {})
    for r, ch in res["components_changed"].items():
        if r not in ec or sorted(ch) != sorted(ec[r]): bad.append("component %s changed %s, expected %s" % (r, sorted(ch), ec.get(r)))
    for r in ec:
        if r not in res["components_changed"]: bad.append("component %s expected to change and did not" % r)
    em = exp.get("pins_moved", {})
    for k, v in res["pins_moved"].items():
        if em.get(k) != v: bad.append("pin %s moved %s, expected %s" % (k, v, em.get(k)))
    for k in em:
        if k not in res["pins_moved"]: bad.append("pin %s expected to move %s and did not" % (k, em[k]))
    for key in ("pins_added", "pins_removed"):
        ea = exp.get(key, {})
        for k, v in res[key].items():
            if ea.get(k) != v: bad.append("%s %s on %s, expected %s" % (key, k, v, ea.get(k)))
        for k in ea:
            if k not in res[key]: bad.append("%s %s expected and absent" % (key, k))
    return bad

if __name__ == "__main__":
    a, b = sys.argv[1], sys.argv[2]
    res = compare(a, b)
    if "--json" in sys.argv: print(json.dumps(res, indent=1, sort_keys=True))
    else:
        print("counts (committed, candidate):", res["counts"])
        for k in ("components_added", "components_removed", "nets_added", "nets_removed"): print("%s: %s" % (k, res[k]))
        for r, ch in res["components_changed"].items(): print("changed %s: %s" % (r, ch))
        for k, v in res["pins_moved"].items(): print("pin moved %s: %s -> %s" % (k, v[0], v[1]))
        for k, v in res["pins_added"].items(): print("pin added %s on %s" % (k, v))
        for k, v in res["pins_removed"].items(): print("pin removed %s from %s" % (k, v))
    if "--expect" in sys.argv:
        exp = json.load(open(sys.argv[sys.argv.index("--expect") + 1]))
        bad = check(res, exp)
        for x in bad: print("UNEXPECTED  " + x)
        print("RESULT: %s" % ("ONLY THE EXPECTED CHANGES" if not bad else "%d UNEXPECTED" % len(bad)))
        sys.exit(1 if bad else 0)
