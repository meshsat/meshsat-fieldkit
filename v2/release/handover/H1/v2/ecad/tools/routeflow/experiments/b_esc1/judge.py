#!/usr/bin/env python3
"""judge.py: read the outcome of the board B escape trial Q-B-ESC-1 off its own files (v2/docs/B-FEASIBILITY.md
section 7). EXPERIMENTAL: the outcome is a feasibility reading about one region, never a layout result.

Usage: judge.py <trial dir>   -> writes <trial dir>/outcome.json and prints the outcome; exit 0

Reads, per arm A in a6 and a8: <A>/base.json (count_open.py's pass-0 count), <A>/final.json (count_open.py on the
imported, filled board), <A>/s3-counts.txt (hardset.py "H U"), <A>/watch/watch.json (plateau_watch.py); and
<trial>/integrity.json.

One sample per arm, because the router is deterministic (tests/test_driver_hygiene.py, "Freerouting is deterministic,
so N attempts with identical parameters are one attempt run N times", measured 5 September 2026): a repeat would be
the same number twice, so there is no between-repeat scatter to read and the table below has none.

An arm CLOSES when its S3 open count is 0 and its hard count is 0. An arm is SETTLED when it closed, stopped on
PLATEAU, or ended by itself with its last reading not a new minimum of the pass-0 count (<arm>/base.json) and every
observed session; an arm cut by a cap while still falling is not settled, and its count is only an upper bound.

  REGION-CLOSES-ON-6    a6 closes
  LAYERS-HELP           a8 closes, a6 does not and a6 is settled
  LAYERS-PARTIAL        a6 is settled with a6 open > 0, a8 does not close and a8 open <= 0.5 x a6 open
  LAYERS-NOT-THE-LEVER  both settled, a8 open > 0.5 x a6 open, and at least half of a8's residue pads (named parts)
                        are also in a6's residue
  INCONCLUSIVE          anything else, with the reason: the arms differ, an arm has no reading (no first pass inside
                        90 minutes), a count still falling at its cap, the residue at different pads, or both arms at
                        0 open with hard DRC items (the open count cannot separate them)

Integration, 26 September 2026: the pass-0 count joined the "still falling" test and the both-at-zero case became
INCONCLUSIVE; the first version read one observed pass as settled and two zero-open arms with hard items as
LAYERS-PARTIAL.

The 0.5 factor is a stated convention of this page, not a measured constant."""
import sys, os, json


def load(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return None


def arm(t, a):
    w = load(os.path.join(t, a, "watch", "watch.json")) or {}
    f = load(os.path.join(t, a, "final.json"))
    base = load(os.path.join(t, a, "base.json")) or {}
    hard = None
    try:
        hard = int(open(os.path.join(t, a, "s3-counts.txt")).read().split()[0])
    except (OSError, ValueError, IndexError):
        pass
    counts = w.get("counts") or []
    # "Still falling" is judged over the pass-0 count as well (integration, 26 September 2026): a job cut after one
    # observed pass that fell from pass 0 was read as settled when only the observed sessions were compared.
    seq = ([base["open"]] if isinstance(base.get("open"), int) else []) + list(counts)
    falling = len(seq) >= 2 and seq[-1] < min(seq[:-1])
    opened = f["open"] if f else None
    closed = opened == 0 and hard == 0
    settled = bool(f) and (closed or w.get("stop") == "PLATEAU" or (w.get("stop") == "JOB_ENDED" and not falling))
    pads = set()
    if f:
        for rows in f.get("residue", {}).values():
            pads.update(r["pad"] for r in rows)
    return {"stop": w.get("stop"), "observed": w.get("observed_sessions"), "counts": counts, "open": opened,
            "hard": hard, "closed": closed, "settled": settled, "falling_at_stop": falling, "residue_pads": sorted(pads)}


def main(a):
    if not a:
        print(__doc__)
        return 2
    t = a[0]
    integ = load(os.path.join(t, "integrity.json")) or {}
    r6, r8 = arm(t, "a6"), arm(t, "a8")
    out, why = "INCONCLUSIVE", ""
    if not integ.get("agree"):
        why = "the arms differ in something other than layer count (integrity.json)"
    elif r6["open"] is None:
        why = "a6 has no reading (stop %s): the tool cannot answer at this cap" % r6["stop"]
    elif r6["closed"]:
        out, why = "REGION-CLOSES-ON-6", "a6 reached 0 open with hard 0"
    elif r8["open"] is None:
        why = "a8 has no reading (stop %s)" % r8["stop"]
    elif r8["closed"] and r6["settled"]:
        out, why = "LAYERS-HELP", "a8 closed; a6 settled at %d open" % r6["open"]
    elif r6["open"] == 0 and r8["open"] == 0:
        # Both arms joined every S3 net and neither closed, so each carries hard DRC items: the open count cannot
        # separate the arms, and this table has no hard-count outcome (integration, 26 September 2026).
        why = "both arms reach 0 open but carry hard DRC items (a6 hard %s, a8 hard %s)" % (r6["hard"], r8["hard"])
    elif r6["settled"] and not r8["closed"] and r6["open"] > 0 and r8["open"] <= 0.5 * r6["open"]:
        out, why = "LAYERS-PARTIAL", "a8 %d open against a6 %d" % (r8["open"], r6["open"])
    elif r6["settled"] and r8["settled"] and r8["open"] > 0.5 * r6["open"]:
        shared = set(r8["residue_pads"]) & set(r6["residue_pads"])
        if r8["residue_pads"] and len(shared) >= 0.5 * len(r8["residue_pads"]):
            out, why = "LAYERS-NOT-THE-LEVER", "a8 %d open against a6 %d; %d of a8's %d residue pads are a6's too" % (
                r8["open"], r6["open"], len(shared), len(r8["residue_pads"]))
        else:
            why = "a8 %d open against a6 %d but the residue sits at different pads" % (r8["open"], r6["open"])
    else:
        # Reached only when an arm is not settled: it ended by itself (JOB_ENDED) or was cut by a cap while its count
        # was still falling. The reason names both, not only a cut (fix-up, 26 September 2026).
        why = ("an arm is not settled: it ended or was cut by a cap while its count was still falling "
               "(a6 stop %s, falling %s; a8 stop %s, falling %s)"
               % (r6["stop"], r6["falling_at_stop"], r8["stop"], r8["falling_at_stop"]))
    res = {"label": "EXPERIMENTAL (Q-B-ESC-1)", "outcome": out, "why": why, "a6": r6, "a8": r8, "integrity": integ}
    json.dump(res, open(os.path.join(t, "outcome.json"), "w"), indent=1)
    print("judge: %s: %s" % (out, why))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
