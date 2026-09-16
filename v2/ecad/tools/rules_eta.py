#!/usr/bin/env python3
"""The ETA, derived from the gap register and the measured run history (MESHSAT-862, 16 September 2026).

The owner asked for a calibrated estimate rather than a number. This computes one from data that already
exists: every open rule in the coverage map carries a remediation with an owner, its dependencies and a P50
and P80 effort, and every route this project has run has left its duration in a routeflow journal. Nothing
here is typed in per run.

The model, stated so its assumptions can be argued with:
  * ACTIVE ENGINEERING TIME is the critical path through the remediation graph, not the sum: work with no
    dependency between items runs in parallel, and this session is one worker, so the parallel width is 1 for
    SESSION work and unbounded for waits.
  * OWNER and VENDOR items are WAITS, not work: they are elapsed time this project cannot compress, and they
    are reported separately rather than mixed into the engineering estimate.
  * BOARD WORK is measured: the median and the worst observed route-and-finish duration per board from the
    journals, multiplied by the re-routes the open rules imply.
  * P50 is the sum of p50 efforts along the critical path; P80 is the sum of p80 efforts along the same path,
    which is conservative (it assumes the pessimistic case correlates) and is stated as such.

Usage: rules_eta.py [--json] [--hours-per-day 6]
"""
import os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules_lib as R
import rules_status as S

ECAD = os.path.dirname(HERE)


def open_items(cov=None):
    """[(rule id, owner, p50, p80, depends_on)] for every rule with work left."""
    cov = cov if cov is not None else S.coverage()
    out = []
    for rid, c in sorted(cov.items()):
        rem = c.get("remediation")
        if not rem: continue
        out.append(dict(rule=rid, owner=rem.get("owner", "SESSION"), p50=float(rem.get("p50_h") or 0),
                        p80=float(rem.get("p80_h") or 0), depends_on=list(rem.get("depends_on") or []),
                        action=rem.get("action", ""), maturity=c.get("maturity")))
    return out


def cycles(items):
    """Every dependency cycle in the gap register, as a list of rule ids.

    A CYCLE IS REFUSED, NOT ABSORBED (16 September 2026). `cost()` below carries a seen-set and returns zero
    on a revisit, which keeps it from recursing for ever and also makes a cycle invisible: the critical path
    is then computed by silently truncating one of the two edges, and nothing says which one was dropped or
    that the number is short. The register held exactly that, RET-001 depending on SI-001 and SI-001 on
    RET-001, while the critical path it produced was being reported every ten minutes."""
    by = {i["rule"]: i for i in items}
    found, colour = [], {}

    def walk(rid, stack):
        if colour.get(rid) == 2: return
        if rid in stack:
            found.append(stack[stack.index(rid):] + [rid]); return
        i = by.get(rid)
        if i is None: return
        for d in i["depends_on"]: walk(d, stack + [rid])
        colour[rid] = 2

    for i in items: walk(i["rule"], [])
    uniq, seen = [], set()
    for c in found:
        k = frozenset(c)
        if k not in seen: seen.add(k); uniq.append(c)
    return uniq


def critical_path(items, key="p50"):
    """The longest chain through the dependency graph, in hours. Items with no dependency between them are
    concurrent only in the sense that they do not extend each other's chain; the worker model is applied by
    the caller. Raises on a cycle rather than returning a number that quietly omits an edge."""
    cyc = cycles(items)
    if cyc:
        raise ValueError("the gap register has %d dependency cycle(s) and a critical path through a cycle is "
                         "not a duration: %s" % (len(cyc), "; ".join(" -> ".join(c) for c in cyc[:4])))
    by = {i["rule"]: i for i in items}
    memo = {}

    def cost(rid, seen=()):
        if rid in memo: return memo[rid]
        i = by.get(rid)
        if i is None or rid in seen: return 0.0
        best = max([cost(d, seen + (rid,)) for d in i["depends_on"]] or [0.0])
        memo[rid] = best + i[key]
        return memo[rid]

    return max([cost(i["rule"]) for i in items] or [0.0])


def route_history():
    """Measured route and finish durations from every routeflow journal in the tree: {board: [minutes]}."""
    out = {}
    for f in glob.glob(os.path.join(ECAD, "pcb-*", "out", "routeflow", "journal.jsonl")):
        board = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(f))))
        for line in open(f, errors="replace"):
            try: rec = json.loads(line)
            except ValueError: continue
            note = str(rec.get("note", ""))
            if "autoroute minutes" in note:
                # the note carries a dict per attempt, {'1': 49.7}: the VALUE is the duration, and the key is
                # the attempt number, which the first version of this parser took as a one-minute route
                blob = note.split("autoroute minutes", 1)[1]
                for part in blob.replace("{", " ").replace("}", " ").split(","):
                    if ":" not in part: continue
                    try:
                        v = float(part.split(":", 1)[1].strip().strip("'\""))
                        if v > 0: out.setdefault(board, []).append(v)
                    except ValueError: continue
    return out


def model(hours_per_day=6.0):
    cov = S.coverage(); items = open_items(cov)
    session = [i for i in items if i["owner"] == "SESSION"]
    waits = [i for i in items if i["owner"] in ("OWNER", "VENDOR", "LAB")]
    eng_p50, eng_p80 = sum(i["p50"] for i in session), sum(i["p80"] for i in session)
    path_p50, path_p80 = critical_path(items, "p50"), critical_path(items, "p80")
    hist = route_history()
    routes = sorted(v for vs in hist.values() for v in vs)
    med = routes[len(routes) // 2] if routes else None
    worst = routes[-1] if routes else None
    return dict(
        open_items=len(items), session_items=len(session), wait_items=len(waits),
        engineering_hours={"p50": eng_p50, "p80": eng_p80},
        critical_path_hours={"p50": path_p50, "p80": path_p80},
        owner_waits=[{"rule": i["rule"], "action": i["action"][:90], "p50_h": i["p50"], "p80_h": i["p80"]} for i in waits],
        route_history={"boards": {k: len(v) for k, v in hist.items()}, "median_minutes": med, "worst_minutes": worst},
        calendar_days={"p50": round(eng_p50 / hours_per_day, 1), "p80": round(eng_p80 / hours_per_day, 1)},
        hours_per_day=hours_per_day,
        assumptions=[
            "one worker on SESSION items, so engineering hours are summed rather than parallelised",
            "OWNER and VENDOR items are waits and are not in the engineering total",
            "P80 sums the pessimistic case along the whole path, which assumes correlation and is conservative",
            "board route time is measured from the journals in this tree and is elapsed, not engineering, time",
            "no estimate here covers prototype manufacture or physical validation, which need hardware",
        ])


def main(argv):
    hpd = float(argv[argv.index("--hours-per-day") + 1]) if "--hours-per-day" in argv else 6.0
    m = model(hpd)
    if "--json" in argv: print(json.dumps(m, indent=1, sort_keys=True)); return 0
    print("rules_eta: %d open item(s): %d session, %d owner or vendor waits"
          % (m["open_items"], m["session_items"], m["wait_items"]))
    print("engineering effort   P50 %5.0f h   P80 %5.0f h" % (m["engineering_hours"]["p50"], m["engineering_hours"]["p80"]))
    print("critical path        P50 %5.0f h   P80 %5.0f h  (the longest dependency chain)"
          % (m["critical_path_hours"]["p50"], m["critical_path_hours"]["p80"]))
    print("at %.0f h a day       P50 %5.1f d   P80 %5.1f d  of engineering, waits excluded"
          % (m["hours_per_day"], m["calendar_days"]["p50"], m["calendar_days"]["p80"]))
    rh = m["route_history"]
    print("routes measured      %d board(s), median %s min, worst %s min per attempt"
          % (len(rh["boards"]), rh["median_minutes"], rh["worst_minutes"]))
    print("\nwaits that are not engineering time:")
    for w in m["owner_waits"]: print("  %-8s %s" % (w["rule"], w["action"][:88]))
    print("\nassumptions:")
    for a in m["assumptions"]: print("  - %s" % a)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
