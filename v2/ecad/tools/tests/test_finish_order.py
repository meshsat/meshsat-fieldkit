#!/usr/bin/env python3
"""The finish runs its stages in the order that has reasons, and the fifteen clones did not.

MESHSAT-862, 11 September 2026. The order established with B13 on 5 September is: clean up first, then the stub
router, then a zone refill, then the check. It has two written reasons, both defects that were paid for:

  * the stub router's closing via counts as a plane clearance violation when the zone fill is stale, so a legal
    closure is reverted;
  * `cleanup_dangling.py` running AFTER the stub router can remove the very via the closure used.

Five of the fifteen finish scripts run the stub router FIRST. The correct family (a22, a23, b19, c7, c8) carries
the order with the comment that explains it; the other family (d8, d9, e6, p1, p2) carries the opposite with no
comment at all, which is what drift looks like. Those five are the boards whose deliverables shipped.

`finish.sh` is one file with the order in it once. Until the fifteen are retired, WRONG_ORDER keeps the debt
visible and counted rather than remembered.
"""
import os, re, sys, json, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STAGES = ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch", "stub_router")

# The five that run the stub router before the clean-up, with no reason given. Each must be either fixed or
# retired in favour of finish.sh; this list is the debt, printed on every run.
WRONG_ORDER = {
    "finish_d8.sh": "D8, released 8 September",
    "finish_d9.sh": "D9, released 8 September; D10 ends its route with one open",
    "finish_e6.sh": "E6, released; E7's finish stopped with five opens",
    "finish_p1.sh": "P1, released 7 September",
    "finish_p2.sh": "P2, released 8 September; P3's deliverable is the one current folder",
}


def _order(path):
    """The stages of a script, in the order they first appear."""
    seen, out = set(), []
    for line in open(path, errors="replace"):
        t = line.strip()
        if t.startswith("#"): continue
        for s in STAGES:
            if re.search(r"\b%s\.py" % s, t) and s not in seen: seen.add(s); out.append(s)
    return out


def t_the_one_finish_cleans_up_before_it_stubs():
    o = _order(os.path.join(TOOLS, "finish.sh"))
    assert "stub_router" in o, o
    for before in ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch"):
        assert before in o, (before, o)
        assert o.index(before) < o.index("stub_router"), \
            "%s must run before the stub router: %s" % (before, o)


def t_every_board_has_a_finish_block_with_every_key():
    need = {"stub_layers", "pour_nets", "pair_match", "pair_audit_nets", "post_fix", "pruned_gate", "gate_grep"}
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        d = json.load(open(p))
        assert "finish" in d, "%s has no finish block" % os.path.basename(p)
        missing = need - set(d["finish"])
        assert not missing, "%s finish block lacks %s" % (os.path.basename(p), sorted(missing))


def t_a_board_that_matches_pairs_names_the_pairs_it_audits():
    """The audit images are what a stopped chain is read from; a board that gates on pairs and names none would
    stop with nothing to look at."""
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        f = json.load(open(p))["finish"]
        if f["pair_match"]:
            assert f["pair_audit_nets"], "%s gates on pairs and names no audit net" % os.path.basename(p)


def t_the_clone_drift_is_counted_until_the_clones_are_retired():
    """Not an assertion that the five are fixed: an assertion that the list is accurate. A debt list that has
    drifted from the tree is worse than none, because it reads as though someone is watching."""
    wrong = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "finish_*.sh"))):
        fn = os.path.basename(p)
        if fn in ("finish_board.sh", "finish_b_after.sh", "finish_a18.sh"): continue
        o = _order(p)
        if "stub_router" in o and any(s in o and o.index(s) > o.index("stub_router")
                                      for s in ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch")):
            wrong.append(fn)
    assert sorted(wrong) == sorted(WRONG_ORDER), \
        "the drift list is stale: the tree says %s, WRONG_ORDER says %s" % (sorted(wrong), sorted(WRONG_ORDER))
    for fn, why in sorted(WRONG_ORDER.items()):
        print("       finish order still wrong: %-16s %s" % (fn, why))
