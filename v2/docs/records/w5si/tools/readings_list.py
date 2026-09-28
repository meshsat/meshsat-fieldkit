#!/usr/bin/env python3
"""The per-board counts and the nets behind them, from SI-001 readings taken in scratch (stream w5si, 27 September 2026,
MESHSAT-1357). A record of how the readings under ../readings/ were summarised; it reads the verdict and the table of
each board from a directory of scratch readings and writes nothing but its output.

Usage: readings_list.py <directory of readings> <label>
"""
import os, sys, json, collections

BOARDS = ("pcb-a-power", "pcb-b-compute", "pcb-c-display", "pcb-d-aprs", "pcb-e1-dock", "pcb-p-pack")


def main(d, label):
    tot = collections.Counter()
    print("SI-001 AT THE SCHEMATIC PHASE, readings taken in scratch outside any tree: %s" % label)
    print("Prototype design work: nothing has been built or measured. Every reading is INCONCLUSIVE; none is a PASS.")
    print()
    print("THE COUNTS. Denominator: the signal nets outside LOW_SPEED_OR_DC (the class the rule asks no edge of).")
    print("  signal = slow + non-slow; non-slow = decided by a maker's figure + decided by a bound + undecided;")
    print("  decided = answered + layout-bound; layout-bound = held by a maker's figure on every driver + BOUND_DECIDES")
    print()
    print("board | netlist sha256/16 | signal | slow | non-slow | maker's figure | bound | undecided | answered | layout-bound | of which maker-held | BOUND_DECIDES | verdict")
    tabs = {}
    for n in BOARDS:
        v = json.load(open(os.path.join(d, n, "edge_length.verdict.json")))
        t = json.load(open(os.path.join(d, n, "edge_length.table.json")))
        tabs[n] = t
        c = v["counts"]
        assert c["signal_nets"] == c["low_speed_nets"] + c["decided_nets"] + c["undecided_nets"] + c["contradicted_nets"], c
        assert c["decided_nets"] == c["maker_edge_nets"] + c["bound_edge_nets"], c
        assert c["decided_nets"] == c["may_be_long_nets"] == c["answered_nets"] + c["layout_bound_nets"], c
        assert c["layout_bound_nets"] == c["maker_held_nets"] + c["bound_decided_nets"], c
        assert c["contradicted_nets"] == 0, c
        non = c["signal_nets"] - c["low_speed_nets"]
        print("%s | %s | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d | %s" % (
            n[4].upper(), v["inputs"]["netlist"]["sha256_16"], c["signal_nets"], c["low_speed_nets"], non, c["maker_edge_nets"],
            c["bound_edge_nets"], c["undecided_nets"], c["answered_nets"], c["layout_bound_nets"], c["maker_held_nets"],
            c["bound_decided_nets"], v["verdict"]))
        for k in c: tot[k] += c[k]
        tot["non_slow"] += non
        rates = v["inputs"]["edge_rates"]["sha256_16"]
    print("all six | | %d | %d | %d | %d | %d | %d | %d | %d | %d | %d |" % (
        tot["signal_nets"], tot["low_speed_nets"], tot["non_slow"], tot["maker_edge_nets"], tot["bound_edge_nets"], tot["undecided_nets"],
        tot["answered_nets"], tot["layout_bound_nets"], tot["maker_held_nets"], tot["bound_decided_nets"]))
    assert tot["non_slow"] == tot["maker_edge_nets"] + tot["bound_edge_nets"] + tot["undecided_nets"]
    print("data file pcb_edge_rates.yaml sha256/16 %s" % rates)
    for n in BOARDS:
        t = tabs[n]; L = t["board"].upper()
        print()
        print("=== BOARD %s" % L)
        bd, mh = collections.defaultdict(list), collections.defaultdict(list)
        named = collections.defaultdict(set)
        for r in t["rows"]:
            for x in r.get("bound_decides") or []:
                e = r["net_edges"][x]
                bd[e["source"]].append(x)
                for b in e.get("bound_drivers") or []: named[x].add(b.split(":")[0])
            for x in r.get("maker_holds") or []:
                e = r["net_edges"][x]
                mh["%s, %.4g ns, critical %.1f mm" % (e["source"], e["edge_ns"], r["critical_by_net"][x])].append(x)
        print("  BOUND_DECIDES, %d net(s): layout-bound, and at least one driver on each has no published minimum. By the driver that governs:" % sum(map(len, bd.values())))
        for k, v in sorted(bd.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            print("    %s (%d): %s" % (k, len(v), ", ".join(sorted(v))))
        mixed = []
        for r in t["rows"]:
            for x in r.get("bound_decides") or []:
                e = r["net_edges"][x]
                if e.get("maker_edge_ns") is not None:
                    mixed.append("%s: bound %s; beside it %s at %.4g ns, which decides nothing" % (x, ", ".join(sorted(named[x])), e["maker_by"].split(":")[0], e["maker_edge_ns"]))
        print("  of them, %d net(s) carry a maker's figure BESIDE the bound (the nets the first pass called maker-held or that mix both):" % len(mixed))
        for m in sorted(mixed): print("    " + m)
        print("  MAKER_HELD, %d net(s): layout-bound, and every driver on each has a published minimum:" % sum(map(len, mh.values())))
        for k, v in sorted(mh.items()): print("    %s (%d): %s" % (k, len(v), ", ".join(sorted(v))))
        und = collections.defaultdict(list)
        for r in t["rows"]:
            for x, rs in (r.get("undecided") or {}).items(): und[rs[0][:90]].append(x)
        print("  UNDECIDED, %d net(s):" % sum(map(len, und.values())))
        for k, v in sorted(und.items(), key=lambda kv: -len(kv[1])): print("    %s (%d): %s" % (k, len(v), ", ".join(sorted(v))))
        rise = sorted({(x, e["rising"].get("edge_ns"), e["rising"]["source"]) for r in t["rows"] for x, e in (r.get("net_edges") or {}).items() if e.get("rising")})
        if rise: print("  OPEN-DRAIN NETS WITH THEIR RISE STATED (never the governing edge): %s" % "; ".join("%s rise %s ns (%s)" % x for x in rise))
        for nt in t.get("notes") or []:
            if "instrument limit" in nt: print("  note: " + nt)


if __name__ == "__main__":
    if len(sys.argv) != 3: print(__doc__); sys.exit(2)
    main(sys.argv[1], sys.argv[2])
