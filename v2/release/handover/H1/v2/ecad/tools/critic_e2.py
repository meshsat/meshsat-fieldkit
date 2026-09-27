#!/usr/bin/env python3
"""Stage E2 of the learned-critic experiment (MESHSAT-862, appendix 32.64): the analytical placement features of a tile against the router's outcome on
the same tile, over the jitter campaign's rows (tile_labels.py per sample: tx, ty, pads, fine_pads, unescaped_pads, escape_vias, locked_len, env_overlap,
nets_crossing, rule_area, opens, hard, router_vias, router_len). A tile "fails" when the router left an open or a hard violation in it. Each feature is
read as a yes/no predictor of that; precision and recall are printed per board and over all rows. Usage: critic_e2.py <csv> [<csv> ...]"""
import csv, sys, collections
rows = []
for f in sys.argv[1:]: rows += list(csv.DictReader(open(f)))
def num(r, k):
    try: return float(r[k])
    except (KeyError, ValueError): return 0.0
PRED = [("unescaped_pads > 0", lambda r: num(r, "unescaped_pads") > 0), ("env_overlap > 0", lambda r: num(r, "env_overlap") > 0), ("nets_crossing > 0", lambda r: num(r, "nets_crossing") > 0),
        ("fine_pads > 0", lambda r: num(r, "fine_pads") > 0), ("pads >= 12", lambda r: num(r, "pads") >= 12), ("nets_crossing >= 8", lambda r: num(r, "nets_crossing") >= 8),
        ("fine_pads > 0 and nets_crossing >= 8", lambda r: num(r, "fine_pads") > 0 and num(r, "nets_crossing") >= 8)]
tot = collections.Counter(); byb = collections.defaultdict(collections.Counter)
for r in rows:
    y = (num(r, "opens") + num(r, "hard")) > 0
    for name, fn in PRED:
        k = (name, bool(fn(r)), y); tot[k] += 1; byb[r.get("board", "?")][k] += 1
def report(c, label):
    n = sum(v for (nm, p, y), v in c.items() if nm == PRED[0][0]); pos = sum(v for (nm, p, y), v in c.items() if nm == PRED[0][0] and y)
    print("== %s: %d tiles, %d (%.1f%%) with an open or a hard violation" % (label, n, pos, 100.0 * pos / max(1, n)))
    for name, _ in PRED:
        tp = c[(name, True, True)]; fp = c[(name, True, False)]; fn = c[(name, False, True)]
        print("   %-38s flags %5d tiles  precision %.2f  recall %.2f" % (name, tp + fp, tp / max(1, tp + fp), tp / max(1, tp + fn)))
report(tot, "all rows (%d files)" % (len(sys.argv) - 1))
for b, c in sorted(byb.items()): report(c, b)
