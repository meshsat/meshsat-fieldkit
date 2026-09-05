#!/usr/bin/env python3
"""bench_compare: grade a routed board's metrics against the baseline (Freerouting quality programme, Stage 1).

Gates first: any hard violation or open connection makes the run INELIGIBLE for quality ranking (it is recorded, never ranked); a differential
pair over 1 mm after matching is a REGRESSION; router vias or total length up by more than 5 percent is a REGRESSION. Otherwise MET, with
  Q = 0.5 x (router vias / baseline router vias) + 0.3 x (length / baseline length) + 0.2 x (segments / baseline segments)
lower is better, 1.0 is the released board. Time is printed beside Q and never folded into it.
Usage: bench_compare.py <baseline.json> <metrics.json> [--board KEY] [--json out]   (KEY defaults to the metrics' tag, then its board stem)"""
import sys, json, os

def arg(name, default=None): return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def compare(base, m):
    if m.get("hard") is None or m.get("unrouted") is None: return "UNMEASURABLE", "no DRC numbers in the metrics", None
    if m["hard"] > 0 or m["unrouted"] > 0: return "INELIGIBLE", "hard %d of %d types, unrouted %d of %d connections" % (m["hard"], m["hard_types_checked"], m["unrouted"], m["connections"]), None
    if m.get("pairs_over_1mm", 0) > 0: return "REGRESSION", "%d differential pairs over 1 mm" % m["pairs_over_1mm"], None
    bv, bl, bs = max(1, base["vias_router"]), max(1e-9, base["length_mm"]), max(1, base["tracks"])
    rv, rl, rs = m["vias_router"] / bv, m["length_mm"] / bl, m["tracks"] / bs
    q = round(0.5 * rv + 0.3 * rl + 0.2 * rs, 4)
    note = "router vias %d vs %d (%+.1f%%), length %.0f vs %.0f mm (%+.1f%%), segments %d vs %d (%+.1f%%), Q %.3f, time %.0f s vs %.0f s" % (
        m["vias_router"], base["vias_router"], (rv - 1) * 100, m["length_mm"], base["length_mm"], (rl - 1) * 100, m["tracks"], base["tracks"], (rs - 1) * 100, q, m.get("wall_seconds", 0), base.get("wall_seconds", 0))
    if rv > 1.05 or rl > 1.05: return "REGRESSION", note, q
    return "MET", note, q

def main():
    base_all = json.load(open(sys.argv[1])); m = json.load(open(sys.argv[2]))
    key = arg("--board") or m.get("tag") or os.path.splitext(m["board"])[0]
    base = base_all.get(key) or next((v for k, v in base_all.items() if k.startswith(key) or key.startswith(k)), None)
    if base is None: print("UNMEASURABLE: no baseline for", key, "in", sys.argv[1]); sys.exit(3)
    verdict, note, q = compare(base, m)
    res = {"board": key, "verdict": verdict, "Q": q, "note": note, "baseline_tag": base.get("tag")}
    if arg("--json"): json.dump(res, open(arg("--json"), "w"), indent=1)
    print("%s %s: %s" % (verdict, key, note)); sys.exit(0 if verdict == "MET" else 1)

if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    main()
