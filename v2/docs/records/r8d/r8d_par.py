"""r8d: an independent comparison of board D's netlist and intent, written for round 8 of MESHSAT-1357 only.

It proves, or refuses, one claim: board D's regenerated netlist differs from main's (fc144600) ONLY in the changes
listed in EXPECT below, each tied to its finding id, and main's own generator reproduces main's committed netlist.

Netlist: every component's full record (value, footprint, fields, libsource, properties; tstamps and sheetpath left
out, which a regeneration renumbers), every net's nodes with (ref, pin, pinfunction, pintype), and the libparts.
Intent: key by key, rails and nodes by name, bypass entries by capacitor.
Every difference is printed with both sides and classed EXPECTED (with its finding id) or UNEXPECTED. Exit 1 on any
UNEXPECTED, and on any EXPECTED item that did not occur (a listed change that is not in the netlist is a claim, not
a change).

Usage: r8d_par.py <out dir> <tree tools dir>   (reads <out>/base/ref, <out>/base/files, <out>/new/files)"""
import json, re, sys

O, TOOLS = sys.argv[1], sys.argv[2]
sys.path.insert(0, TOOLS)
from kisch import parse

N = "pcb-d-aprs"
L4, F15, G12, G14, PLED, PVGG, P1 = "EMCON-L4", "PWR-F15", "G12", "G14", "PARTS-C2287", "PARTS-J_VGG", "R8D-P1"
NEW_COMPS = {**{r: L4 for r in ("U21", "R90", "R91", "R95", "C69", "C70", "C71", "TP27")},
             **{r: F15 for r in ("J_FLANGE", "R92", "R93", "R94", "C72", "C73", "C74", "C75", "U22", "TP26")}}
# changed components: the record keys each may change
CHANGED_COMPS = {"C31": (G12, {"value", "footprint", "fields", "property:LCSC"}),
                 "C32": (G12, {"value", "footprint", "fields", "property:LCSC"}),
                 "LED2": (PLED, {"value"}), "LED5": (PLED, {"value"}),
                 "J_VGG": (PVGG, {"fields", "property:LCSC"}),
                 "C44": (P1, {"fields", "property:LCSC"}), "C45": (P1, {"fields", "property:LCSC"})}
NEW_NETS = {"+5V_TX": L4, "TXSUP_EN": L4, "TXSUP_CT": L4, "TXSUP_QOD": L4,
            "FLANGE_NTC": F15, "FLANGE_AIN0": F15, "FLANGE_REF": F15}
# for each existing net: (finding, nodes that may leave, nodes that may join), nodes as (ref, pin)
MOVED = {"+5V_D8": (L4, {("FB1", "1"), ("K1", "1"), ("D2", "1"), ("C57", "1"), ("U15", "6"), ("C61", "1")},
                    {("U21", "6"), ("C71", "1")}),
         "+3V3_D8": (L4, set(), {("R90", "1")}),
         "+3V3": (F15, set(), {("R92", "1"), ("R94", "1"), ("U22", "8"), ("C75", "1")}),
         "SDA": (F15, set(), {("U22", "9")}), "SCL": (F15, set(), {("U22", "10")}),
         "GND": ("EMCON-L4 and PWR-F15", set(), {("U21", "4"), ("U21", "7"), ("R91", "2"), ("C69", "2"), ("C70", "2"), ("C71", "2"),
                 ("J_FLANGE", "2"), ("C72", "2"), ("C73", "2"), ("C74", "2"), ("C75", "2"),
                 ("U22", "1"), ("U22", "3"), ("U22", "6"), ("U22", "7")})}
NEW_NET_NODES = {"+5V_TX": {("FB1", "1"), ("K1", "1"), ("D2", "1"), ("C57", "1"), ("U15", "6"), ("C61", "1"), ("U21", "1"),
                            ("R95", "2"), ("TP27", "1")},
                 "TXSUP_EN": {("U21", "5"), ("R90", "2"), ("R91", "1"), ("C69", "1")},
                 "TXSUP_CT": {("U21", "3"), ("C70", "1")}, "TXSUP_QOD": {("U21", "2"), ("R95", "1")},
                 "FLANGE_NTC": {("J_FLANGE", "1"), ("R92", "2"), ("C72", "1"), ("R93", "1"), ("TP26", "1")},
                 "FLANGE_AIN0": {("R93", "2"), ("C73", "1"), ("U22", "4")},
                 "FLANGE_REF": {("R94", "2"), ("C74", "1"), ("U22", "5")}}
NEW_UNCONNECTED = {("U22", "2"): F15}        # ALERT/RDY, left unconnected (SBAS444E 9.1.4)
NEW_LIBPARTS = {"Power_Management:TPS22810DRV": L4, "meshsat_ic:U22": F15}
# ic() draws each IC as its own libpart and names its pins by their nets, so U15's pin 6 is renamed with its net
CHANGED_LIBPARTS = {"meshsat_ic:U15": (L4, '"\\"+5V_D8\\""', '"\\"+5V_TX\\""')}


def uq(s): return s[1:-1] if isinstance(s, str) and s.startswith('"') else s
def sub(node, head): return [x for x in node if isinstance(x, list) and x and x[0] == head]
def flat(node): return json.dumps(node, separators=(",", ":"))


def load_net(path):
    tree = parse(open(path, encoding="utf-8").read())[0]
    comps, nets, libparts = {}, {}, {}
    for cs in sub(tree, "components"):
        for c in sub(cs, "comp"):
            ref = uq(sub(c, "ref")[0][1])
            rec = {"value": uq(sub(c, "value")[0][1]) if sub(c, "value") else None,
                   "footprint": uq(sub(c, "footprint")[0][1]) if sub(c, "footprint") else None,
                   "fields": {}, "libsource": None, "properties": {}, "other": []}
            for f in sub(c, "fields"):
                for fl in sub(f, "field"):
                    rec["fields"][uq(sub(fl, "name")[0][1])] = [uq(x) for x in fl[2:] if not isinstance(x, list)]
            if sub(c, "libsource"):
                rec["libsource"] = {x[0]: uq(x[1]) for x in sub(c, "libsource")[0][1:] if isinstance(x, list) and len(x) > 1}
            for pr in sub(c, "property"):
                rec["properties"][uq(sub(pr, "name")[0][1])] = uq(sub(pr, "value")[0][1]) if sub(pr, "value") else None
            for x in c[1:]:
                if isinstance(x, list) and x and x[0] not in ("ref", "value", "footprint", "fields", "libsource", "property", "sheetpath", "tstamps"):
                    rec["other"].append(flat(x))
            comps[ref] = rec
    for ns in sub(tree, "nets"):
        for n in sub(ns, "net"):
            name = uq(sub(n, "name")[0][1]).lstrip("/")
            nodes = {}
            for nd in sub(n, "node"):
                g = {x[0]: uq(x[1]) for x in nd[1:] if isinstance(x, list) and len(x) > 1}
                nodes[(g.get("ref"), g.get("pin"))] = (g.get("pinfunction", ""), g.get("pintype", ""))
            extra = [flat(x) for x in n[1:] if isinstance(x, list) and x and x[0] not in ("code", "name", "node")]
            nets[name] = (nodes, extra)
    for lp in sub(tree, "libparts"):
        for p in sub(lp, "libpart"):
            libparts["%s:%s" % (uq(sub(p, "lib")[0][1]), uq(sub(p, "part")[0][1]))] = flat(p)
    return comps, nets, libparts


def comp_diff(a, b):
    out = [k for k in ("value", "footprint", "fields", "libsource", "other") if a.get(k) != b.get(k)]
    pa, pb = a.get("properties") or {}, b.get("properties") or {}
    out += ["property:" + k for k in sorted(set(pa) | set(pb)) if pa.get(k) != pb.get(k)]
    return out


def netlist_pair(x, y, gx, gy, expect):
    (c1, n1, l1), (c2, n2, l2) = gx, gy
    exp, unexp, seen = [], [], set()
    for r in sorted(set(c1) | set(c2)):
        a, b = c1.get(r), c2.get(r)
        if a == b: continue
        if a is None:
            if expect and r in NEW_COMPS:
                exp.append("[%s] comp %s ADDED: %s | %s | %s" % (NEW_COMPS[r], r, b["value"], b["footprint"], b["fields"].get("LCSC") or b["properties"].get("LCSC")))
                seen.add(("comp", r)); continue
            unexp.append("comp %s present only on %s: %s" % (r, y, b)); continue
        if b is None:
            unexp.append("comp %s present only on %s: %s" % (r, x, a)); continue
        d = comp_diff(a, b)
        if expect and r in CHANGED_COMPS and set(d) <= CHANGED_COMPS[r][1]:
            exp.append("[%s] comp %s changes %s: value %r -> %r, footprint %r -> %r, LCSC %r -> %r" % (
                CHANGED_COMPS[r][0], r, d, a["value"], b["value"], a["footprint"], b["footprint"],
                a["fields"].get("LCSC") or a["properties"].get("LCSC"), b["fields"].get("LCSC") or b["properties"].get("LCSC")))
            seen.add(("comp", r)); continue
        unexp.append("comp %s differs in %s\n        %s: %s\n        %s: %s" % (r, d, x, a, y, b))
    for n in sorted(set(n1) | set(n2)):
        a, b = n1.get(n), n2.get(n)
        if a == b: continue
        if a is None:
            nodes = b[0]
            um = re.match(r"unconnected-\((\w+)-", n)
            if expect and n in NEW_NETS and set(nodes) == NEW_NET_NODES[n]:
                exp.append("[%s] net %s ADDED with %s" % (NEW_NETS[n], n, sorted("%s.%s(%s/%s)" % (k[0], k[1], v[0], v[1]) for k, v in nodes.items())))
                seen.add(("net", n)); continue
            if expect and um and set(nodes) <= set(NEW_UNCONNECTED) and len(nodes) == 1:
                k = list(nodes)[0]; exp.append("[%s] net %s ADDED (%s.%s, a deliberate no-connect)" % (NEW_UNCONNECTED[k], n, k[0], k[1]))
                seen.add(("nc", k)); continue
            unexp.append("net %s present only on %s: %s" % (n, y, sorted(nodes.items()))); continue
        if b is None:
            unexp.append("net %s present only on %s: %s" % (n, x, sorted(a[0].items()))); continue
        (na, ea), (nb, eb) = a, b
        if ea != eb: unexp.append("net %s attributes differ: %s | %s" % (n, ea, eb))
        gone, came = set(na) - set(nb), set(nb) - set(na)
        changed = [k for k in set(na) & set(nb) if na[k] != nb[k]]
        if changed: unexp.append("net %s: pinfunction/pintype changed on %s" % (n, [(k, na[k], nb[k]) for k in sorted(changed)]))
        if not gone and not came: continue
        if expect and n in MOVED and gone == MOVED[n][1] and came == MOVED[n][2]:
            exp.append("[%s] net %s: left %s, joined %s" % (MOVED[n][0], n, sorted("%s.%s" % k for k in gone),
                                                          sorted("%s.%s(%s/%s)" % (k[0], k[1], nb[k][0], nb[k][1]) for k in came)))
            seen.add(("net", n)); continue
        unexp.append("net %s node set differs: only %s %s, only %s %s" % (n, x, sorted(gone), y, sorted(came)))
    for p in sorted(set(l1) | set(l2)):
        if l1.get(p) == l2.get(p): continue
        if expect and p in NEW_LIBPARTS and p not in l1:
            exp.append("[%s] libpart %s ADDED" % (NEW_LIBPARTS[p], p)); seen.add(("libpart", p)); continue
        if expect and p in CHANGED_LIBPARTS and p in l1 and p in l2:
            tag, was, now = CHANGED_LIBPARTS[p]
            if l1[p].count(was) == 1 and l1[p].replace(was, now) == l2[p]:
                exp.append("[%s] libpart %s: one pin name %s -> %s, nothing else" % (tag, p, was, now)); seen.add(("libpart", p)); continue
        unexp.append("libpart %s %s" % (p, "only on %s" % (x if p not in l2 else y) if (p in l1) != (p in l2) else "content differs"))
    if expect:
        want = {("comp", r) for r in NEW_COMPS} | {("comp", r) for r in CHANGED_COMPS} | {("net", n) for n in NEW_NETS} | \
               {("net", n) for n in MOVED} | {("nc", k) for k in NEW_UNCONNECTED}
        want |= {("libpart", p) for p in NEW_LIBPARTS if p not in l1} | {("libpart", p) for p in CHANGED_LIBPARTS}
        for m in sorted(want - seen): unexp.append("LISTED BUT ABSENT: %s %s" % m)
    return exp, unexp


def intent_pair(x, y, a, b, expect):
    exp, unexp = [], []
    for k in sorted(set(a) | set(b)):
        if k in ("written", "rails", "nodes", "bypass"): continue
        if a.get(k) != b.get(k): unexp.append("intent key %s differs: %s | %s" % (k, json.dumps(a.get(k))[:300], json.dumps(b.get(k))[:300]))
    ra, rb = a.get("rails") or {}, b.get("rails") or {}
    rails_exp = {"+5V_D8": L4, "+3V3_D8": L4, "+5V_TX": L4, "+5V_SA": L4, "+3V3": F15}
    for r in sorted(set(ra) | set(rb)):
        if ra.get(r) == rb.get(r): continue
        keys = sorted(k for k in set(ra.get(r) or {}) | set(rb.get(r) or {}) if (ra.get(r) or {}).get(k) != (rb.get(r) or {}).get(k))
        line = "rail %s %s: %s" % (r, "ADDED" if r not in ra else "changes", {k: ((ra.get(r) or {}).get(k), (rb.get(r) or {}).get(k)) for k in keys if k != "note"})
        if expect and r in rails_exp: exp.append("[%s] %s%s" % (rails_exp[r], line, " (+note)" if "note" in keys else ""))
        else: unexp.append(line)
    na, nb = a.get("nodes") or {}, b.get("nodes") or {}
    for n in sorted(set(na) | set(nb)):
        if na.get(n) == nb.get(n): continue
        if expect and n in ("AMP_HPVDD", "TXSUP_EN", "FLANGE_NTC") and n not in na:
            exp.append("[%s] node %s ADDED: %s" % ({"AMP_HPVDD": G12, "TXSUP_EN": L4, "FLANGE_NTC": F15}[n], n, nb[n]))
        else: unexp.append("node %s: %s | %s" % (n, na.get(n), nb.get(n)))
    ba = {e["cap"]: e for e in a.get("bypass") or []}; bb = {e["cap"]: e for e in b.get("bypass") or []}
    orda = [e["cap"] for e in a.get("bypass") or []]; ordb = [e["cap"] for e in b.get("bypass") or []]
    if [c for c in ordb if c in ba] != orda: unexp.append("bypass order of the existing entries moved: %s | %s" % (orda, ordb))
    for c in sorted(set(ba) | set(bb)):
        ea, eb = ba.get(c), bb.get(c)
        if ea == eb: continue
        if ea is None:
            if expect and c in ("C71", "C75") and eb.get("class") and eb.get("basis"):
                exp.append("[%s] bypass %s ADDED: %s.%s %s class %s" % (L4 if c == "C71" else F15, c, eb["part"], eb["pin"], eb["net"], eb["class"])); continue
            unexp.append("bypass %s only on %s: %s" % (c, y, eb)); continue
        if eb is None: unexp.append("bypass %s only on %s: %s" % (c, x, ea)); continue
        core_a = {k: ea.get(k) for k in ("cap", "part", "pin", "net")}; core_b = {k: eb.get(k) for k in ("cap", "part", "pin", "net")}
        added = {k: eb[k] for k in eb if k not in ea}
        other = [k for k in ea if k not in ("cap", "part", "pin", "net") and ea.get(k) != eb.get(k)]
        ok = expect and set(added) <= {"class", "basis", "floor_uF", "maker_mm"} and "class" in added and "basis" in added and not other
        if ok and core_a != core_b:
            ok = (c == "C17" and core_b == {"cap": "C17", "part": "U17", "pin": "5", "net": "+3V4_HUB"} and added.get("class") == "B1") or \
                 (c == "C61" and core_a["net"] == "+5V_D8" and core_b == {"cap": "C61", "part": "U15", "pin": "6", "net": "+5V_TX"})
        tag = G14 + (" and the C17 re-declaration" if c == "C17" else " and EMCON-L4 (U15's IN on +5V_TX)" if c == "C61" else "")
        line = "bypass %s: %s -> %s, + %s" % (c, core_a, core_b if core_a != core_b else "same", {k: (v if k != "basis" else v[:70]) for k, v in added.items()})
        (exp if ok else unexp).append(("[%s] " % tag if ok else "") + line)
    if expect:
        missing = [c for c in bb if not bb[c].get("class")]
        if missing: unexp.append("bypass entries without a class: %s" % missing)
    return exp, unexp


sides = {"committed": "%s/base/ref" % O, "base_regen": "%s/base/files" % O, "new_regen": "%s/new/files" % O}
nets = {k: load_net("%s/%s.net" % (v, N)) for k, v in sides.items()}
ints = {k: json.load(open("%s/%s-intent.json" % (v, N))) for k, v in sides.items()}
total = 0
for x, y in (("committed", "base_regen"), ("committed", "new_regen"), ("base_regen", "new_regen")):
    ex = y == "new_regen"
    e1, u1 = netlist_pair(x, y, nets[x], nets[y], ex)
    e2, u2 = intent_pair(x, y, ints[x], ints[y], ex)
    total += len(u1) + len(u2)
    c1, n1, l1 = nets[x]; c2, n2, l2 = nets[y]
    print("PAIR %-10s vs %-10s comps %d/%d nets %d/%d libparts %d/%d  expected %d  UNEXPECTED %d  => %s" % (
        x, y, len(c1), len(c2), len(n1), len(n2), len(l1), len(l2), len(e1) + len(e2), len(u1) + len(u2),
        "IDENTICAL" if not (e1 or e2 or u1 or u2) else ("ONLY_EXPECTED" if not (u1 or u2) else "UNEXPECTED")))
    if ints[x].get("written") != ints[y].get("written"): print("   noise      intent written %s -> %s" % (ints[x].get("written"), ints[y].get("written")))
    for s in e1 + e2: print("   expected   " + s)
    for s in u1 + u2: print("   UNEXPECTED " + s)
print("TOTAL UNEXPECTED: %d" % total)
sys.exit(1 if total else 0)
