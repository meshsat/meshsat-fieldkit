#!/usr/bin/env python3
"""The intent half of w3de's parity proof: every key of a committed -intent.json against the candidate's, the
`written` time dropped (regen_compare.py's N5 and nothing else). Prints each rail, node, bypass entry and pass-through
added, removed or changed, and for a changed rail or node the fields that changed.
  intent_compare.py <committed-intent.json> <candidate-intent.json>"""
import json, sys
a, b = (json.load(open(x)) for x in sys.argv[1:3])
for d in (a, b): d.pop("written", None)
for k in sorted(set(a) | set(b)):
    if k in ("rails", "nodes", "pair_classes", "pass_through"):
        x, y = a.get(k) or {}, b.get(k) or {}
        for n in sorted(set(y) - set(x)): print("%s added: %s" % (k, n))
        for n in sorted(set(x) - set(y)): print("%s removed: %s" % (k, n))
        for n in sorted(set(x) & set(y)):
            if x[n] != y[n]:
                ch = sorted(f for f in set(x[n]) | set(y[n]) if x[n].get(f) != y[n].get(f)) if isinstance(x[n], dict) else ["value"]
                print("%s changed: %s %s" % (k, n, ch))
    elif k == "bypass":
        key = lambda e: (e["cap"], e["part"], e["pin"])
        x = {key(e): e for e in a.get(k) or []}; y = {key(e): e for e in b.get(k) or []}
        for n in sorted(set(y) - set(x)): print("bypass added: %s -> %s.%s (%s)" % (n + (y[n].get("class"),)))
        for n in sorted(set(x) - set(y)): print("bypass removed: %s -> %s.%s" % n)
        for n in sorted(set(x) & set(y)):
            if x[n] != y[n]: print("bypass changed: %s -> %s.%s %s" % (n + (sorted(f for f in set(x[n]) | set(y[n]) if x[n].get(f) != y[n].get(f)),)))
    elif a.get(k) != b.get(k):
        print("%s changed" % k)
