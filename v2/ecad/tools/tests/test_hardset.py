#!/usr/bin/env python3
"""The DRC policy: one hard set, its two exemptions, and the refusal to read a broken report as a pass.

The defect these are written against is real and was in the tools this morning: seven copies of the hard tuple had drifted
apart, two of them silently narrower, so the supervisor could call a board CLEAN that the finish then refused (both red teams,
10 September 2026, appendix 32.99)."""
import os, re, json, tempfile, subprocess, sys
import hardset

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _v(t, *descs):
    return {"type": t, "severity": "error", "items": [{"description": d} for d in descs]}


def _drc(*violations, unrouted=0):
    return {"violations": list(violations), "unconnected_items": [{} for _ in range(unrouted)]}


def t_the_hard_set_is_fifteen_types():
    assert len(hardset.HARD_POST) == 15, "the hard set is %d types, the record says fifteen" % len(hardset.HARD_POST)
    assert hardset.HARD_PRE == hardset.HARD_POST, "pre and post must be one set"
    for t in ("clearance", "shorting_items", "tracks_crossing", "courtyards_overlap", "items_not_allowed", "via_diameter"):
        assert t in hardset.HARD_POST, "%s fell out of the hard set" % t


def t_a_clearance_violation_is_hard():
    c = hardset.counts(_drc(_v("clearance", "Track [GND] on F.Cu", "Pad 1 [+5V] of U1 on F.Cu")))
    assert c["hard"] == 1, c
    assert c["by_type"] == {"clearance": 1}, c


def t_a_reported_type_is_not_hard():
    c = hardset.counts(_drc(_v("silk_over_copper", "Text of U1"), _v("isolated_copper", "Zone [GND] on In1.Cu")))
    assert c["hard"] == 0, c
    assert c["report"] == {"silk_over_copper": 1, "isolated_copper": 1}, c


def t_a_footprints_own_courtyard_overlap_is_exempt():
    """The Wuerth USB 3 receptacle draws two courtyard polygons that overlap each other; the fab does not care."""
    v = _v("courtyards_overlap", "Footprint J_USB3 [USB3]", "Footprint J_USB3 [USB3]")
    assert hardset.exempt(v) is True
    c = hardset.counts(_drc(v)); assert c["hard"] == 0 and c["exempt"] == {"courtyards_overlap": 1}, c


def t_two_different_footprints_overlapping_is_hard():
    v = _v("courtyards_overlap", "Footprint U1 [QFN]", "Footprint U2 [QFN]")
    assert hardset.exempt(v) is False
    assert hardset.counts(_drc(v))["hard"] == 1


def t_a_same_part_mask_bridge_is_exempt_and_a_cross_part_one_is_not():
    same = _v("solder_mask_bridge", "Pad 3 [D+] of U30A on F.Cu", "Pad 4 [D-] of U30A on F.Cu")
    cross = _v("solder_mask_bridge", "Pad 3 [D+] of U30A on F.Cu", "Pad 1 [GND] of C12 on F.Cu")
    assert hardset.exempt(same) is True and hardset.exempt(cross) is False
    c = hardset.counts(_drc(same, cross)); assert c["hard"] == 1 and c["exempt"] == {"solder_mask_bridge": 1}, c


def t_an_exemption_needs_exactly_two_items_of_one_footprint():
    assert hardset.exempt({"type": "courtyards_overlap", "items": [{"description": "Footprint U1 [x]"}]}) is False
    assert hardset.exempt({"type": "clearance", "items": [{"description": "Pad 1 of U1"}, {"description": "Pad 2 of U1"}]}) is False


def t_unrouted_items_are_counted():
    assert hardset.counts(_drc(unrouted=7))["unrouted"] == 7


def t_a_broken_report_is_never_a_pass():
    """A DRC JSON that does not parse, or has no violations list, must raise: the caller may not read it as zero hard."""
    d = tempfile.mkdtemp(prefix="hardset-test-")
    bad = os.path.join(d, "bad.json"); open(bad, "w").write("{ this is not json")
    try:
        hardset.load(bad); raise AssertionError("unparseable JSON was accepted")
    except RuntimeError: pass
    empty = os.path.join(d, "empty.json"); json.dump({"something_else": []}, open(empty, "w"))
    try:
        hardset.load(empty); raise AssertionError("a JSON with no violations list was accepted")
    except RuntimeError: pass
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py"), bad], capture_output=True, text=True)
    assert r.returncode == 3, "the CLI must exit 3 on an unreadable report, got %d" % r.returncode
    assert "BLOCK" in r.stdout, r.stdout


def t_no_second_hard_set_definition_anywhere_in_the_tools():
    """The hard types are defined in one file, in ANY language, and nowhere else.

    The first version of this test scanned `*.py` only. Both round-two red teams found the consequence on 10 September 2026:
    the six-type tuple had survived in 27 SHELL scripts in twenty one different forms, several of them not even the six-type
    set, and five of them decided something (`route_one.sh` scored the attempt that `route_parallel.sh` then picked,
    `quality_pass.sh` kept or reverted a quality step, `pair_match.sh` said whether a meander hurt, the two partition scripts
    reported the merge). The test that "fails if a second definition appears anywhere" was looking in the one place the drift
    was not. It reads every text file now.

    A tool may name a NARROWER pattern for a reason, and those patterns live in hardset.py too (KNOT). What must never come
    back is a private set of type names in a consumer, in a heredoc or otherwise."""
    hits = []
    TYPES = hardset.DRIFT_MARKERS   # the names come from the policy itself, or this detector is the second definition
    for root, dirs, files in os.walk(TOOLS):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "bench", "cloud", "freerouting", "boards")]
        for f in files:
            if f == "hardset.py" or f.endswith((".json", ".txt", ".md", ".kicad_pcb", ".kicad_sch", ".pyc")): continue
            p = os.path.join(root, f)
            if os.path.basename(root) == "tests" and f.startswith("test_"): continue   # the fixtures name types on purpose
            try: text = open(p, errors="replace").read()
            except Exception: continue
            for n, line in enumerate(text.splitlines(), 1):
                s = line.strip()
                if s.startswith("#") or s.startswith("//"): continue
                # A line that is DATA rather than policy says so and why, the `erc-allow.txt` idiom inline: a marker with no
                # reason after it waives nothing.
                if re.search(r"drift-ok:\s*\S", s): continue
                # Two or more hard type names QUOTED on one line is a set, whatever the language quotes it with. The quotes
                # are what separates a definition from prose: unknot.py's docstring names two of them in a sentence.
                if sum(1 for t in TYPES if ('"%s"' % t) in s or ("'%s'" % t) in s) >= 2:
                    hits.append("%s:%d %s" % (os.path.relpath(p, TOOLS), n, s[:100]))
    assert not hits, "a second hard-set definition is back (%d line(s)):\n  " % len(hits) + "\n  ".join(hits)
