#!/usr/bin/env python3
"""The one hard set of the pipeline (MESHSAT-862, 8 Sep 2026, appendix 32.64). Every gate that decides on a DRC JSON counts through here;
the six-type tuple used to live in eleven copies and every other error-severity type KiCad reported was discarded.

HARD_POST and HARD_PRE are the same fifteen types (the register of 8 Sep 2026 found four different sets: tracks_crossing in no pre-route set,
courtyards_overlap, via_diameter, drill_out_of_range and items_not_allowed in no post-route set); `pre` and `post` are accepted for the callers' record.
REPORT: computed and printed with counts, never blocking (the record reads them; a jump is a symptom, appendix 32.33).
Two exemptions, both about one footprint against itself: a courtyard overlap of a footprint's own two courtyard polygons (the Wuerth USB 3
receptacle) and a solder-mask bridge inside one footprint (two pads of a fine-pitch part, which JLC gang-masks, or a library mask drawing over its
own pad; a bridge between different parts or pad to track stays hard).

Usage: hardset.py <drc.json> [pre|post] [--score FILE] [--counts FILE] [--gate FILE] [--flag FILE] [--label TEXT] [--examples N]
  prints  hardset: hard H of T types {type: n} unrouted U | report {type: n}
  --score writes H; --counts writes "H U"; --gate writes OK or BLOCK H; --flag writes clean or open (hard 0 and unrouted 0).  Exit 3 on an unreadable JSON (never a pass).

THE SHELL USES THE SAME POLICY THROUGH THIS CLI (10 September 2026, both round-two red teams C1/P0). Twenty seven shell scripts
carried their own tuple in a heredoc, in twenty one different forms, several of them NOT the six-type set: the drift the register
of 8 September found in Python had a second home nobody had looked in, and five of those scripts decide something today
(`route_one.sh` scores the attempt route_parallel.sh then picks, `quality_pass.sh` keeps or reverts a quality step,
`pair_match.sh` decides whether a meander hurt, `part_stage2.sh` and `part_reconcile.sh` report the partition). No shell script
counts violation types any more; they call this file and read the number back."""
import sys, json, collections, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

HARD_POST = ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance",
             "solder_mask_bridge", "annular_width", "track_width", "diff_pair_gap_out_of_range", "zones_intersect", "courtyards_overlap",
             "via_diameter", "drill_out_of_range", "items_not_allowed")   # one set (the register of 8 Sep found four different ones, none complete)
HARD_PRE = HARD_POST
# Named patterns, so a tool that acts on a narrower set says which one and why here rather than keeping a private tuple
# (10 September 2026, both red teams C1: seven copies of the hard set had drifted apart, two of them silently narrower).
KNOT = ("shorting_items", "tracks_crossing")   # unknot.py: the router's knot, two nets tangled at one spot; a symptom pattern, not a policy subset
# The names a drift detector looks for (`routeflow.py selftest` and `tests/test_hardset.py`): the hard types that are ONLY ever
# DRC violation types. `track_width`, `via_diameter`, `clearance` and `hole_clearance` are left out because they are also net
# class property names, and a generator reading `cl.get("via_diameter")` is not a second DRC policy. Two of these quoted on one
# line outside this file is a private hard set (10 September 2026, both round-two red teams C1).
DRIFT_MARKERS = ("shorting_items", "tracks_crossing", "hole_to_hole", "copper_edge_clearance", "solder_mask_bridge",
                 "annular_width", "diff_pair_gap_out_of_range", "zones_intersect", "courtyards_overlap",
                 "drill_out_of_range", "items_not_allowed")
REPORT = ("connection_width", "isolated_copper", "starved_thermal", "copper_sliver", "silk_over_copper", "silk_overlap", "silk_edge_clearance",
          "track_dangling", "via_dangling", "net_conflict", "lib_footprint_mismatch", "diff_pair_uncoupled_length_too_long", "skew_out_of_range",
          "length_out_of_range", "too_many_vias", "malformed_courtyard", "missing_courtyard")

def _fp_of(item):
    """The footprint reference an item description names, or None ('Pad 3 [GND] of U30A on F.Cu', 'Footprint U1 [..]', 'Courtyard of U1')."""
    d = item.get("description", "")
    m = re.search(r"\bof ([A-Za-z_]+[0-9A-Za-z_]*)\b", d) or re.search(r"Footprint ([A-Za-z_]+[0-9A-Za-z_]*)", d)
    return m.group(1) if m else None

def exempt(v):
    """A violation of one footprint against itself, which the fab handles: own-courtyard overlap, same-part mask bridge."""
    items = v.get("items", [])
    if len(items) != 2: return False
    a, c = _fp_of(items[0]), _fp_of(items[1])
    if not a or a != c: return False
    if v["type"] == "courtyards_overlap": return True
    if v["type"] == "solder_mask_bridge": return True   # two pads of one part (JLC gang-masks) or a part's own mask drawing over its pad (the U.FL library footprint)
    return False

def load(path):
    """A DRC JSON must parse and carry a violations list; anything else is a tool failure, never a pass (routeflow rule)."""
    try: d = json.load(open(path))
    except Exception as e: raise RuntimeError("unreadable DRC JSON %s: %s" % (path, e))
    if not isinstance(d, dict) or "violations" not in d: raise RuntimeError("DRC JSON %s has no violations list" % path)
    return d

def counts(d, which="post"):
    types = HARD_PRE if which == "pre" else HARD_POST
    by = collections.Counter(); rep = collections.Counter(); ex = collections.Counter()
    for v in d["violations"]:
        t = v.get("type", "")
        if t in types:
            if exempt(v): ex[t] += 1
            else: by[t] += 1
        elif t in REPORT: rep[t] += 1
    return {"hard": sum(by.values()), "by_type": dict(by), "exempt": dict(ex), "types": types, "unrouted": len(d.get("unconnected_items", [])), "report": dict(rep)}

def examples(d, which="post", n=4):
    types = HARD_PRE if which == "pre" else HARD_POST
    out = []
    for t in types:
        for v in [v for v in d["violations"] if v.get("type") == t and not exempt(v)][:n]:
            out.append("   %s | %s" % (t, " / ".join(i.get("description", "")[:70] for i in v.get("items", []))))
    return out

def _vname(label):
    """One verdict file per judgement: `hardset` alone, or `hardset-<label>` when the caller named the moment."""
    if not label: return "hardset"
    return "hardset-" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def main(a):
    if not a or a[0] in ("-h", "--help"): print(__doc__); return 2
    which = "pre" if "pre" in a[1:2] else "post"
    def opt(k): return a[a.index(k) + 1] if k in a else None
    try: d = load(a[0])
    except RuntimeError as e:
        print("hardset: BLOCK %s" % e)
        return verdict.write(_vname(opt("--label")), verdict.INCONCLUSIVE, denominator=0,
                             inputs={"drc": a[0]}, note=str(e))
    c = counts(d, which); n = int(opt("--examples") or 4)
    print("hardset: hard %d of %d types %s unrouted %d | report %s%s" % (c["hard"], len(c["types"]), c["by_type"] or "{}", c["unrouted"], c["report"] or "{}",
          (" | exempt %s" % c["exempt"]) if c["exempt"] else ""))
    for line in examples(d, which, n): print(line)
    if opt("--label"): print("%s: hard %d unrouted %d (%d types checked)" % (opt("--label"), c["hard"], c["unrouted"], len(c["types"])))
    if opt("--score"): open(opt("--score"), "w").write("%d\n" % c["hard"])
    if opt("--counts"): open(opt("--counts"), "w").write("%d %d\n" % (c["hard"], c["unrouted"]))   # the shell's interface: "hard unrouted" on one line
    if opt("--gate"): open(opt("--gate"), "w").write("OK" if c["hard"] == 0 else "BLOCK %d" % c["hard"])
    if opt("--flag"): open(opt("--flag"), "w").write(("clean" if c["hard"] == 0 and c["unrouted"] == 0 else "open") + "\n")
    # hardset is BOTH a measuring instrument and a gate: `--score` and `--counts` callers read the files above and
    # rely on exit 0 meaning "the DRC JSON was readable" (pair_match.sh returns 999999 on a non-zero exit). So the
    # verdict is written as a file and the exit code is deliberately left alone. The label distinguishes the three
    # judgements one finish makes (after the stub router, the routed-board gate, the deliverable DRC), which would
    # otherwise overwrite each other. 11 September 2026.
    verdict.write(_vname(opt("--label")),
                  verdict.PASS if (c["hard"] == 0 and c["unrouted"] == 0) else verdict.FAIL,
                  counts={"hard": c["hard"], "unrouted": c["unrouted"], "types_checked": len(c["types"]),
                          "by_type": c["by_type"], "report": c["report"]},
                  denominator=len(c["types"]),
                  evidence=examples(d, which, 6),
                  inputs={"drc": a[0]},
                  note=(opt("--label") or "") + " (exit code stays the reader contract of --score and --counts)")
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
