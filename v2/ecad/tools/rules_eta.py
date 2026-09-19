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

EVERY OPEN ITEM DECLARES HOW IT EXECUTES (16 September 2026), because "how many hours of work is left" and
"when is it done" are different questions and the second one needs to know what can run beside what. The
classes are below in EXECUTION; an item that declares none, or one this file does not know, is an error rather
than a default, since a silent default would put box work in the session's queue or the other way about.

AN ENGINEERING HOUR IS NOT AN ELAPSED HOUR AND A BOX HOUR IS NOT EITHER. A session item costs its hours at the
working day declared on the command line; a rented box runs through the night, so a box item costs its hours at
twenty-four hours a day. The two are converted to DAYS per item before anything is summed, because mixing them
in one total is how this project reported twenty-four days as an ETA twice.

THE PROGRAMME IS LONGER THAN THE DESIGN, and the stages between them are not rules: a fabricator's queue, a
courier, a bench and a chamber booking. They are declared in `pcb_programme_stages.yaml` with the KIND of each
number, and only a number this project has measured itself counts as evidence. None of them has been measured
yet, because nothing has been ordered.

Usage: rules_eta.py [--json] [--hours-per-day 6] [--agents N] [--boxes N]
"""
import os, sys, json, glob
import verdict          # the guarded flag reader (19 September 2026)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rules_lib as R
import rules_status as S

ECAD = os.path.dirname(HERE)
STAGES = os.path.join(HERE, "pcb_programme_stages.yaml")

# How an open item executes. The value decides which pool its hours are drawn from and at what rate its hours
# become days; it does NOT decide when the item may start, which is what depends_on is for.
EXECUTION = {
    "PARALLEL_AGENT": "session work with no shared file, so several may run at once in their own worktrees",
    "PARALLEL_BOX":   "work whose cost is a route, a sweep or a solve on a rented host, so it runs at the fleet's width",
    "SEQUENTIAL":     "session work that must be serialised: one producer, a shared file, or a never-auto floor",
    "OWNER":          "a ruling. No amount of compute shortens it and it is never in the engineering total",
    "VENDOR_OR_STANDARD_WAIT": "a third party's answer, or a document that has to be obtained and read",
    "HARDWARE":       "needs built hardware, so it cannot start before the fabrication stage ends",
}
SESSION_CLASSES = ("PARALLEL_AGENT", "SEQUENTIAL")
WAIT_CLASSES = ("OWNER", "VENDOR_OR_STANDARD_WAIT")


def open_items(cov=None):
    """[(rule id, owner, p50, p80, depends_on)] for every rule with work left."""
    cov = cov if cov is not None else S.coverage()
    out = []
    for rid, c in sorted(cov.items()):
        rem = c.get("remediation")
        if not rem: continue
        ex = rem.get("execution")
        if ex not in EXECUTION:
            raise SystemExit("rules_eta: %s declares execution %r, which is not one of %s. An open item with no "
                             "execution class cannot be scheduled: it would silently join the session's queue."
                             % (rid, ex, ", ".join(sorted(EXECUTION))))
        out.append(dict(rule=rid, owner=rem.get("owner", "SESSION"), p50=float(rem.get("p50_h") or 0),
                        p80=float(rem.get("p80_h") or 0), depends_on=list(rem.get("depends_on") or []),
                        action=rem.get("action", ""), maturity=c.get("maturity"), execution=ex))
    return out


def day_rate(item, hours_per_day):
    """The hours-to-days rate for ONE item, which is a property of where it runs and not of the project's day.

    A rented box does not keep office hours: a twelve hour route costs half an elapsed day, not two working
    days. A session item costs its hours at the declared working day. Conflating the two is the arithmetic
    behind both of the elapsed ETAs this project has had to withdraw."""
    return 24.0 if item["execution"] == "PARALLEL_BOX" else float(hours_per_day)


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


def critical_path_days(items, key="p50", hours_per_day=6.0):
    """The same longest chain, costed in DAYS with each item converted at its own rate.

    The hours version above answers "how much work", which is a fair question with one answer. This one
    answers "how long", and the two are not the same number in different units: a box item's twelve hours are
    half a day and a session item's twelve hours are two."""
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
        memo[rid] = best + i[key] / day_rate(i, hours_per_day)
        return memo[rid]

    return max([cost(i["rule"]) for i in items] or [0.0])


def stages():
    """The declared non-rule stages, with the kind of every number kept beside it."""
    import yaml
    d = yaml.safe_load(open(STAGES, encoding="utf-8"))
    st = d.get("stages") or {}
    for name, v in st.items():
        if not v.get("source"):
            raise SystemExit("rules_eta: stage %s declares no source kind; a number with no provenance is not "
                             "an estimate, it is a wish" % name)
        if v["source"] != "COMPUTED" and ("p50_days" not in v or "p80_days" not in v):
            raise SystemExit("rules_eta: stage %s declares no p50_days/p80_days" % name)
    return st


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


def pools(items, hours_per_day, agents, boxes):
    """Elapsed days per resource pool, at P50 and P80.

    A pool is a set of items that compete for the same thing: the session's own attention, or the rented
    fleet. SEQUENTIAL work takes one of the session's workers and cannot be split however many there are, so
    it is a floor on the session pool as well as part of its total."""
    out = {}
    for key in ("p50", "p80"):
        d = lambda cls: sum(i[key] / day_rate(i, hours_per_day) for i in items if i["execution"] == cls)
        seq, agent, box = d("SEQUENTIAL"), d("PARALLEL_AGENT"), d("PARALLEL_BOX")
        out[key] = {"sequential_days": seq, "agent_days": agent, "box_days": box,
                    "session_pool_days": max(seq, (seq + agent) / max(1, agents)),
                    "box_pool_days": box / max(1, boxes)}
    return out


def milestones(design_p50, design_p80, st=None):
    """The programme dates, chained from the declared stages. Each carries the kind of its numbers, so a
    reader can see which of them this project has ever measured (none of them, today)."""
    st = st if st is not None else stages()
    order = ["DESIGN_PACKAGE_READY_FOR_PROTOTYPE", "FABRICATION_AND_ASSEMBLY", "BENCH_BRING_UP",
             "LAB_VALIDATION", "PRODUCTION_RELEASE_READY"]
    out, c50, c80 = [], 0.0, 0.0
    for name in order:
        v = st.get(name)
        if v is None:
            raise SystemExit("rules_eta: the stage %s is not declared in pcb_programme_stages.yaml" % name)
        p50 = design_p50 if v["source"] == "COMPUTED" else float(v["p50_days"])
        p80 = design_p80 if v["source"] == "COMPUTED" else float(v["p80_days"])
        c50 += p50; c80 += p80
        out.append({"stage": name, "stage_p50_days": round(p50, 1), "stage_p80_days": round(p80, 1),
                    "cumulative_p50_days": round(c50, 1), "cumulative_p80_days": round(c80, 1),
                    "source": v["source"], "basis": " ".join(str(v.get("basis", "")).split())})
    return out


def model(hours_per_day=6.0, agents=1, boxes=2):
    cov = S.coverage(); items = open_items(cov)
    session = [i for i in items if i["execution"] in SESSION_CLASSES + ("PARALLEL_BOX",)]
    waits = [i for i in items if i["execution"] in WAIT_CLASSES]
    eng_p50, eng_p80 = sum(i["p50"] for i in session), sum(i["p80"] for i in session)
    path_p50, path_p80 = critical_path(items, "p50"), critical_path(items, "p80")
    pl = pools(items, hours_per_day, agents, boxes)
    st = stages()
    wait = st["OWNER_AND_VENDOR_WAITS"]
    cpd50 = critical_path_days(items, "p50", hours_per_day)
    cpd80 = critical_path_days(items, "p80", hours_per_day)
    design_p50 = max(cpd50, pl["p50"]["session_pool_days"], pl["p50"]["box_pool_days"], float(wait["p50_days"]))
    design_p80 = max(cpd80, pl["p80"]["session_pool_days"], pl["p80"]["box_pool_days"], float(wait["p80_days"]))
    ms = milestones(design_p50, design_p80, st)
    by_class = {}
    for c in sorted(EXECUTION):
        sel = [i for i in items if i["execution"] == c]
        by_class[c] = {"items": len(sel), "p50_h": sum(i["p50"] for i in sel), "p80_h": sum(i["p80"] for i in sel),
                       "rules": [i["rule"] for i in sel]}
    hist = route_history()
    routes = sorted(v for vs in hist.values() for v in vs)
    med = routes[len(routes) // 2] if routes else None
    worst = routes[-1] if routes else None
    return dict(
        open_items=len(items), session_items=len(session), wait_items=len(waits),
        engineering_hours={"p50": eng_p50, "p80": eng_p80},
        critical_path_hours={"p50": path_p50, "p80": path_p80},
        by_execution=by_class, pools=pl, width={"agents": agents, "boxes": boxes},
        design_package_days={"p50": round(design_p50, 1), "p80": round(design_p80, 1)},
        critical_path_days={"p50": round(cpd50, 1), "p80": round(cpd80, 1)},
        milestones=ms,
        owner_waits=[{"rule": i["rule"], "execution": i["execution"], "action": i["action"][:90],
                      "p50_h": i["p50"], "p80_h": i["p80"]} for i in waits],
        route_history={"boards": {k: len(v) for k, v in hist.items()}, "median_minutes": med, "worst_minutes": worst},
        engineering_days={"p50": round(eng_p50 / hours_per_day, 1), "p80": round(eng_p80 / hours_per_day, 1)},
        hours_per_day=hours_per_day,
        assumptions=[
            "ENGINEERING DAYS ARE NOT ELAPSED DAYS. The engineering figure is effort at one worker; the design "
            "package figure is elapsed and is the one to read as a date",
            "the session pool runs at width %d and the fleet at width %d, both given on the command line; at "
            "width 1 the agent and sequential work share one queue" % (agents, boxes),
            "a box item's hours are elapsed at 24 h a day, a session item's at %.0f h a day" % hours_per_day,
            "OWNER and VENDOR items are waits: they run beside the work and bind only what depends on them",
            "P80 sums the pessimistic case along the whole path, which assumes correlation and is conservative",
            "board route time is measured from the journals in this tree and is elapsed, not engineering, time",
            "every stage after the design package is DECLARED or VENDOR PUBLISHED and none has been measured "
            "by this project, because nothing has been ordered",
        ])


def main(argv):
    hpd = float(verdict.opt(argv, "--hours-per-day", 6.0))
    agents = int(verdict.opt(argv, "--agents", 1))
    boxes = int(verdict.opt(argv, "--boxes", 2))
    m = model(hpd, agents, boxes)
    if "--json" in argv: print(json.dumps(m, indent=1, sort_keys=True)); return 0
    print("rules_eta: %d open item(s): %d work, %d owner or vendor waits"
          % (m["open_items"], m["session_items"], m["wait_items"]))
    print("engineering effort   P50 %5.0f h   P80 %5.0f h   (%.1f d / %.1f d at %.0f h a day, ONE worker, "
          "waits excluded: this is EFFORT, not a date)"
          % (m["engineering_hours"]["p50"], m["engineering_hours"]["p80"], m["engineering_days"]["p50"],
             m["engineering_days"]["p80"], m["hours_per_day"]))
    print("\nwhat the open work is, by how it executes:")
    for c, v in sorted(m["by_execution"].items(), key=lambda kv: -kv[1]["p50_h"]):
        if not v["items"]: continue
        print("  %-24s %2d item(s)  P50 %4.0f h  P80 %4.0f h   %s"
              % (c, v["items"], v["p50_h"], v["p80_h"], ", ".join(v["rules"])))
        print("  %-24s %s" % ("", EXECUTION[c]))
    print("\nELAPSED, at %d session worker(s) and %d rented box(es):" % (m["width"]["agents"], m["width"]["boxes"]))
    print("  session pool         P50 %5.1f d   P80 %5.1f d" % (m["pools"]["p50"]["session_pool_days"], m["pools"]["p80"]["session_pool_days"]))
    print("  fleet pool           P50 %5.1f d   P80 %5.1f d" % (m["pools"]["p50"]["box_pool_days"], m["pools"]["p80"]["box_pool_days"]))
    print("  longest chain        P50 %5.1f d   P80 %5.1f d" % (m["critical_path_days"]["p50"], m["critical_path_days"]["p80"]))
    print("  DESIGN PACKAGE       P50 %5.1f d   P80 %5.1f d   (the largest of the three, plus the owner wait)"
          % (m["design_package_days"]["p50"], m["design_package_days"]["p80"]))
    print("\nthe programme, cumulative elapsed days from today:")
    for s_ in m["milestones"]:
        print("  %-36s P50 %5.1f d  P80 %6.1f d   [%s]"
              % (s_["stage"], s_["cumulative_p50_days"], s_["cumulative_p80_days"], s_["source"]))
    rh = m["route_history"]
    print("\nroutes measured      %d board(s), median %s min, worst %s min per attempt"
          % (len(rh["boards"]), rh["median_minutes"], rh["worst_minutes"]))
    print("\nwaits that are not engineering time:")
    for w in m["owner_waits"]: print("  %-8s %-24s %s" % (w["rule"], w["execution"], w["action"][:70]))
    print("\nassumptions:")
    for a in m["assumptions"]: print("  - %s" % a)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
