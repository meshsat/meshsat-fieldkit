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
    # ITS VERDICT GOES IN ITS OWN DIRECTORY (18 September 2026). The CLI writes one wherever it is run from,
    # and run from v2/ecad that is the evidence the readiness reads: this fixture's "unreadable DRC" reading
    # about a file in /tmp sat in out/hardset.verdict.json until the suite started refusing to move the tree's
    # own verdicts.
    env = dict(os.environ, VERDICT_DIR=d)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py"), bad], capture_output=True, text=True, env=env)
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


# ---------------------------------------------------------------------------------------------------------
# A JUDGEMENT NAMES THE BOARD IT WAS TAKEN ON (17 September 2026, rule PLC-001).
#
# The defect: a DRC report is a derived file, and a hardset verdict named only that report. So a verdict was
# attributable only by the directory it sat in, and a placement measurement could not be carried beside the
# board it belongs to, because nothing in it could prove which board it was about. Boards A, D and P read "no
# hardset-placed verdict for this board" while their placement HAD been measured, in trees that were later
# thrown away, and the verdicts that survived on the box could not honestly be adopted.
#
# `rules_status._named_board` compares `inputs.board.sha256_16` with the boards a project directory holds, so
# the identity has to be the board's own content and not its path.

def _run(args, cwd):
    return subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py")] + args,
                          cwd=cwd, capture_output=True, text=True)


def t_a_labelled_judgement_records_the_board_it_read():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "out"))
        drc = os.path.join(d, "r.json"); open(drc, "w").write(json.dumps(_drc()))
        board = os.path.join(d, "b.kicad_pcb"); open(board, "wb").write(b"(kicad_pcb (version 20240108))\n")
        import hashlib
        want = hashlib.sha256(open(board, "rb").read()).hexdigest()[:16]
        r = _run([drc, "post", "--label", "placed", "--board", board], d)
        assert r.returncode == 0, r.stderr
        v = json.load(open(os.path.join(d, "out", "hardset-placed.verdict.json")))
        got = ((v.get("inputs") or {}).get("board") or {}).get("sha256_16")
        assert got == want, "the verdict names board %r, the file hashes to %r" % (got, want)


def t_without_the_board_the_verdict_is_unchanged():
    """The identity is an addition, not a demand: every caller that has no board file still writes a verdict,
    and it names no board rather than naming a wrong one."""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "out"))
        drc = os.path.join(d, "r.json"); open(drc, "w").write(json.dumps(_drc()))
        r = _run([drc, "post", "--label", "placed"], d)
        assert r.returncode == 0, r.stderr
        v = json.load(open(os.path.join(d, "out", "hardset-placed.verdict.json")))
        assert (v.get("inputs") or {}).get("board") is None, v.get("inputs")
        assert v.get("verdict") == "PASS", v.get("verdict")


def t_an_unreadable_board_is_named_and_not_hashed():
    """A path that cannot be read must not produce an identity: a verdict that claims a board it never read is
    worse than one that names none, because the comparison would silently pass."""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "out"))
        drc = os.path.join(d, "r.json"); open(drc, "w").write(json.dumps(_drc()))
        r = _run([drc, "post", "--label", "placed", "--board", os.path.join(d, "gone.kicad_pcb")], d)
        assert r.returncode == 0, r.stderr
        b = (json.load(open(os.path.join(d, "out", "hardset-placed.verdict.json"))).get("inputs") or {}).get("board")
        assert b and "sha256_16" not in b and "unreadable" in b, b


def _hardset_calls(text):
    """Every hardset invocation in a shell script, as one logical line each."""
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if "hardset.py" in line and not line.startswith("#"):
            out.append(line)
    return out


def t_every_judgement_on_a_board_this_script_holds_names_that_board():
    """THE STRUCTURAL HALF. A script that reads `$N-...drc.json` has `$N.kicad_pcb` beside it by construction,
    so there is no reason for its judgement to be anonymous, and every reason for it not to be: these are the
    verdicts the registry reads."""
    import glob as _g
    bad = []
    for p in sorted(_g.glob(os.path.join(TOOLS, "*.sh"))):
        for line in _hardset_calls(open(p, encoding="utf-8", errors="replace").read()):
            if re.search(r"\$N[A-Za-z_-]*drc\.json", line) and "--board" not in line:
                bad.append("%s: %s" % (os.path.basename(p), line[:110]))
    assert not bad, "a judgement about a board the script holds, that does not name it:\n  " + "\n  ".join(bad)


# ---- the cap says it is a cap (21 September 2026) ----
#
# KiCad's DRC export lists at most about 499 unconnected items, so a board at that number reports a FLOOR.
# It cost a day elsewhere: the pre-lay took its work list from that list and two arms of the same tools were
# handed sixteen pairs and twenty, which is why `prelay_pairs.py` exists. Nothing judged changes here; the
# reading now says what it is, so no reader takes 499 for a measurement.

def t_a_reading_at_the_cap_says_so_and_one_below_it_does_not():
    import hardset as h
    at = h.counts({"violations": [], "unconnected_items": [1] * h.CAP}, "post")
    assert at["unrouted_at_cap"] is True, "a board at KiCad's own list cap reports its floor as a count"
    below = h.counts({"violations": [], "unconnected_items": [1] * 17}, "post")
    assert below["unrouted_at_cap"] is False, "a board of seventeen opens is not at any cap"
    assert below["unrouted"] == 17, "the count itself must not move"


def t_the_printed_line_carries_the_cap_and_only_then():
    """The rule is about the CALL, not about how many characters follow the anchor.

    Written first as a four-hundred-character slice after the anchor, which is the fixed-window shape the
    suite's own ratchet refuses (84 against a declared 83, caught before the commit): add a comment inside
    the call and it fails, delete the line and it can find its literal in the next function. And quoting the
    refused slice IN THIS DOCSTRING kept the count at 84, because the detector reads the file and not the
    code, which is 21 September's own lesson about a docstring that quotes the line it replaces.
    `ast` gives the call itself."""
    import ast
    src = open(os.path.join(TOOLS, "hardset.py"), encoding="utf-8").read()
    assert "AT KiCad's list cap: a floor, not a count" in src, \
        "the sentence a reader sees is the whole point of the flag"
    calls = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "print"
             and "hardset: hard" in (ast.get_source_segment(src, n) or "")]
    assert len(calls) == 1, "expected exactly one summary line, found %d" % len(calls)
    assert "unrouted_at_cap" in ast.get_source_segment(src, calls[0]), \
        "the summary line does not ask whether the count is the cap"


def t_the_verdict_a_later_reader_opens_carries_the_cap_too():
    """The printed line is gone by the time anyone reads the verdict, so the flag has to be IN the file.

    Proved to fail on HEAD: `git show HEAD:v2/ecad/tools/hardset.py` writes its counts without it."""
    import ast
    src = open(os.path.join(TOOLS, "hardset.py"), encoding="utf-8").read()
    calls = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and "verdict.write" in (ast.get_source_segment(src, n) or "")[:40]]
    assert calls, "hardset writes no verdict any more, which is a bigger change than this rule"
    # The INCONCLUSIVE write for an unreadable report carries no counts and owes none: it judged nothing.
    # Every write that DOES carry counts is a reading, and a reading of 499 has to say what 499 is.
    judged = [c for c in calls if any(k.arg == "counts" for k in c.keywords)]
    assert judged, "no hardset verdict carries counts, so nothing carries the reading either"
    for c in judged:
        kw = {k.arg: ast.get_source_segment(src, k.value) for k in c.keywords}
        assert "unrouted_at_cap" in kw["counts"], \
            "the verdict's counts do not say whether the unrouted number is KiCad's own list cap"
