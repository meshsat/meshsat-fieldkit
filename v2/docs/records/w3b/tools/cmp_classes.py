#!/usr/bin/env python3
"""Stream w3b (MESHSAT-1357, 27 September 2026): board B's decision 42 classes as the generator now writes them, entry by entry
against the round 8 map v2/docs/records/r8b/decoupling-classes-b.json, and a census of every board's intent (does every
declaration carry a class of the six and a basis). A desk reading of the intent files, not DEC-001: DEC-001 is a placed-board
rule and board B's placement predates round 8.
Usage: cmp_classes.py <candidate B intent> <r8b map> [<other intent>...]   exit 1 on an unexplained class difference"""
import json, sys, collections
RULED = ("R", "D", "L", "A", "B1", "B2")
# the corrections this stream makes to the round 8 map, each with its reason (the map's clause belongs to another part)
EXPECTED = {"C65": ("D", "D"), "C66": ("D", "D"), "C508": ("R", "D"), "C509": ("R", "D")}
# the declarations this stream adds (W3B-F2, the LG290P's V_BCKP capacitors), which the round 8 map cannot carry
NEW = {"C72": "D", "C73": "D", "C74": "D"}
cand = json.load(open(sys.argv[1])); rec = json.load(open(sys.argv[2]))
ci = {(e["cap"], e["part"], e["pin"]): e for e in cand["bypass"]}
ri = {(e["cap"], e["part"], e["pin"]): e for e in rec["entries"]}
print("candidate entries %d, map entries %d, keys equal: %s" % (len(ci), len(ri), set(ci) == set(ri)))
bad = []
for k in sorted(set(ci) | set(ri)):
    c, r = ci.get(k), ri.get(k)
    if r is None and c is not None and NEW.get(k[0]) == c.get("class") and str(c.get("basis") or "").strip():
        print("NEW       %s: class %s (%s)" % (k, c["class"], c["basis"][:70])); continue
    if c is None or r is None: bad.append("%s only in %s" % (k, "map" if c is None else "candidate")); continue
    if c.get("class") not in RULED or not str(c.get("basis") or "").strip(): bad.append("%s: class %r basis %r" % (k, c.get("class"), c.get("basis"))); continue
    if c["class"] == "L" and not c.get("value_floor"): bad.append("%s: class L with no value_floor" % (k,))
    if c["class"] != r["class"]:
        exp = EXPECTED.get(k[0])
        if exp and exp == (r["class"], c["class"]): print("CORRECTED %s: map %s (%s) -> %s (%s)" % (k, r["class"], r["clause"][:60], c["class"], c["basis"][:70]))
        else: bad.append("%s: map %s, candidate %s" % (k, r["class"], c["class"]))
    elif k[0] in EXPECTED:
        print("CLAUSE    %s: class %s kept; map clause %r -> %s" % (k, c["class"], r["clause"][:60], c["basis"][:70]))
print("candidate classes:", dict(collections.Counter(e["class"] for e in cand["bypass"])))
print("map classes:      ", dict(collections.Counter(e["class"] for e in rec["entries"])))
for p in sys.argv[3:]:
    d = json.load(open(p)); b = d.get("bypass") or []
    n_cls = sum(1 for e in b if e.get("class") in RULED and str(e.get("basis") or "").strip())
    print("census %-44s %3d of %3d entries carry a ruled class and a basis %s" % (p.split("/")[-1], n_cls, len(b), dict(collections.Counter(e.get("class") for e in b))))
print("unexplained: %d" % len(bad))
for x in bad: print("  UNEXPLAINED " + x)
sys.exit(1 if bad else 0)
