#!/usr/bin/env python3
"""How much of a current-sense signal is the copper's own drop (a report, MESHSAT-862, 18 September 2026).

Board A's charger reads its input current across R16, a 10 mOhm shunt whose whole signal at the rail's 6.0 A is
60 mV, and the high side taps the VBUS20 POUR rather than R16's own pad. The question could not be asked while
`dc_drop` solved a potential at every node and reported one of them; it writes the pad potentials now, so the
error at a tap is a subtraction. These rules use a synthetic potentials file, so they need no board and no
KiCad: the arithmetic is the thing being held, and the boards are the fixtures for the geometry."""
import os, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kelvin_check as K


def _pots(drop_element, drop_tap, rail="VBUS20"):
    return {"board": "x.kicad_pcb", "nets": {rail: [
        {"ref": "R16", "pad": "1", "x": 0.0, "y": 0.0, "drop_v": drop_element},
        {"ref": "R147", "pad": "1", "x": 1.0, "y": 0.0, "drop_v": drop_tap}]}}


DECL = [{"sense": "CH_ACP_F", "rail": "VBUS20", "element": "R16.1", "tap": "R147.1", "full_scale_mv": 60.0}]


def t_a_tap_on_the_shunts_own_pad_is_a_kelvin_connection():
    """THE ACCEPTABLE FIXTURE: 0.1 mV of copper between the two, 0.17 percent of a 60 mV signal."""
    rows, fails = K.judge(DECL, _pots(0.050000, 0.050100))
    assert not fails, fails
    (k, err, share) = rows[0]
    assert abs(err - 0.1) < 1e-6 and share < 1.0, (err, share)


def t_a_tap_on_the_pour_is_not():
    """THE DEFECTIVE FIXTURE: 3 mV of copper drop between the shunt's pad and the tap is 5 percent of the
    reading, so the charger's input-current limit is off by five percent and nothing else in the set says so."""
    rows, fails = K.judge(DECL, _pots(0.050000, 0.053000))
    assert len(fails) == 1, fails
    assert "5.0%" in fails[0] and "not a Kelvin connection" in fails[0], fails[0]


def t_a_pad_the_mesh_did_not_solve_is_said_so_and_not_guessed():
    rows, fails = K.judge(DECL, {"nets": {"VBUS20": [{"ref": "R16", "pad": "1", "drop_v": 0.05}]}})
    assert not fails, "a missing tap was turned into a pass or a failure"
    assert rows[0][1] is None and "R147.1" in str(rows[0][2]), rows[0]


def t_a_board_with_no_solved_mesh_decides_nothing():
    """`dc_drop` has to have run. Absence is never a pass, and it is not a finding either."""
    with tempfile.TemporaryDirectory() as d:
        b = os.path.join(d, "pcb-a-power.kicad_pcb"); open(b, "w").write("(kicad_pcb)")
        out = os.path.join(d, "out"); os.makedirs(out)
        env = os.environ.get("VERDICT_DIR")
        os.environ["VERDICT_DIR"] = out
        try: rc = K.main([b, "--board", "a"])
        finally:
            if env is None: os.environ.pop("VERDICT_DIR", None)
            else: os.environ["VERDICT_DIR"] = env
        assert rc == 3, "a board with no solved mesh did not read INCONCLUSIVE (rc %s)" % rc
        v = json.load(open(os.path.join(out, "kelvin_check.verdict.json")))
        assert v["verdict"] == "INCONCLUSIVE" and "pad-potentials" in (v.get("missing_input") or ""), v


def t_it_decides_nothing_until_a_rule_asks():
    """It is ADVISORY on purpose: the registry has no rule for this question yet, and a measurement without a
    rule is worth having so that the rule can be written against a number instead of a fear."""
    src = open(os.path.join(TOOLS, "kelvin_check.py"), encoding="utf-8").read()
    assert "advisory=True" in src, "the report is not marked advisory, so it could decide a rule by accident"
    assert "does not solve" not in src or "Nothing here solves anything" in src


def t_the_declaration_is_data_and_board_a_carries_the_one_that_is_known():
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_sensitive.yaml"), encoding="utf-8"))
    ks = ((d.get("boards") or {}).get("a") or {}).get("kelvin") or []
    assert ks, "board A declares no sense tap, and its charger's is the one this file was written for"
    k = ks[0]
    for field in ("sense", "rail", "element", "tap", "full_scale_mv", "why"):
        assert k.get(field), "the declaration has no %s, so the reading would be about nothing" % field
    assert k["element"].split(".")[0] != k["tap"].split(".")[0], "the element and the tap are the same part"


def t_a_board_that_declares_no_tap_is_not_an_open_question():
    """A board with no current sense has nothing to measure, which is neither a declared zero (a pass with its
    reason) nor an undeclared one (inconclusive): the reading says the rule does not arise here. Board C's panel
    and board E5's contact block are the cases."""
    import tempfile, json as _j
    with tempfile.TemporaryDirectory() as d:
        b = os.path.join(d, "pcb-c-display.kicad_pcb"); open(b, "w").write("(kicad_pcb)")
        out = os.path.join(d, "out"); os.makedirs(out)
        env = os.environ.get("VERDICT_DIR"); os.environ["VERDICT_DIR"] = out
        try: rc = K.main([b, "--board", "c"])
        finally:
            if env is None: os.environ.pop("VERDICT_DIR", None)
            else: os.environ["VERDICT_DIR"] = env
        assert rc == 0, rc
        v = _j.load(open(os.path.join(out, "kelvin_check.verdict.json")))
        assert v["applicable"] is False and v["counts"]["declared"] == 0, v


def t_the_finish_takes_the_reading_where_the_mesh_was_just_solved():
    """It reads dc_drop's output, so it runs after it; and it stops nothing, because a report that blocks a
    board is a rule nobody wrote."""
    sh = open(os.path.join(TOOLS, "finish.sh"), encoding="utf-8").read()
    i, j = sh.find("dc_drop.py"), sh.find("kelvin_check.py")
    assert 0 < i < j, "the report runs before the mesh it reads"
    line = sh[sh.rfind("\n", 0, j) + 1: sh.find("\n", j)]
    assert "stop " not in line, "the report can stop a finish, and no rule asks this question yet"


def t_a_declaration_key_nobody_reads_is_refused_before_it_is_believed():
    """THE DEFECTIVE FIXTURE, and the defect is not cosmetic: `judge` turns an error in millivolts into a
    SHARE with `full_scale_mv`, and a row with no share is never added to `fails`. So one mistyped key makes a
    failing tap print its millivolts and pass. Proved to fail on the tool as it stood: before the guard,
    `check_declaration` did not exist and a row carrying `full_scale_MV` was measured and never judged."""
    bad = K.check_declaration([{"sense": "X", "rail": "R", "element": "R1.1", "tap": "R2.1",
                                "full_scale_MV": 60.0, "why": "typed the wrong case"}])
    assert any("full_scale_mv" in b for b in bad), bad
    assert any("full_scale_MV" in b and "not one this file reads" in b for b in bad), bad


def t_an_element_that_is_its_own_tap_measures_zero_by_construction():
    bad = K.check_declaration([{"sense": "X", "rail": "R", "element": "R1.1", "tap": "R1.1",
                                "full_scale_mv": 60.0, "why": "both ends the same pad"}])
    assert any("same pad" in b for b in bad), bad


def t_the_real_declaration_passes_its_own_guard():
    """THE ACCEPTABLE FIXTURE: every row this project ships."""
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_sensitive.yaml"), encoding="utf-8"))
    decls = []
    for L, blk in sorted((d.get("boards") or {}).items()):
        for k in (blk or {}).get("kelvin") or []: decls.append(dict(k, board=L))
    assert decls, "the set declares no sense tap at all"
    assert not K.check_declaration(decls), K.check_declaration(decls)


def t_every_declared_pad_is_a_pad_of_its_own_rail_on_that_boards_netlist():
    """A row whose element or tap is not on its rail can only ever read 'pad X or Y is not on Z', which decides
    nothing while looking exactly like a declaration that was measured. The committed netlists are the check.
    Board A's ISNS rows tap an IC PIN rather than a filter resistor, which is what the LM5176 does (pins 13 and
    14 sit straight on the two nets the shunt separates), so the check is about the NET and never the part."""
    import re, yaml, glob
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_sensitive.yaml"), encoding="utf-8"))
    ecad = os.path.dirname(TOOLS)
    stems = {"a": "pcb-a-power", "b": "pcb-b-compute", "c": "pcb-c-display",
             "d": "pcb-d-aprs", "e": "pcb-e1-dock", "p": "pcb-p-pack"}
    checked = 0
    for L, blk in sorted((d.get("boards") or {}).items()):
        rows = (blk or {}).get("kelvin") or []
        if not rows: continue
        hits = glob.glob(os.path.join(ecad, stems.get(L, "?") + "*", "out", stems.get(L, "?") + ".net"))
        if not hits:
            raise __import__("harness").Skip("this tree holds no committed netlist for board %s" % L)
        nets, cur = {}, None
        for line in open(hits[0], encoding="utf-8"):
            m = re.search(r'\(net \(code "?\d+"?\) \(name "([^"]+)"\)', line)
            if m: cur = m.group(1); nets[cur] = set(); continue
            m = re.search(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', line)
            if m and cur: nets[cur].add((m.group(1), m.group(2)))
        for r in rows:
            members = nets.get(r["rail"]) or nets.get("/" + str(r["rail"])) or set()
            assert members, "board %s declares a tap on %s and no such net is in its netlist" % (L, r["rail"])
            for key in ("element", "tap"):
                ref, _, pad = str(r[key]).partition(".")
                assert (ref, pad) in members, ("board %s, %s: %s is not a pad of %s, so this row can only ever "
                                               "report a missing pad" % (L, r["sense"], r[key], r["rail"]))
                checked += 1
    assert checked >= 34, "only %d pads checked; the set declares seventeen taps" % checked


def t_a_tap_on_a_conductor_nothing_solves_is_a_declaration_question_and_says_so():
    """THE DEFECTIVE FIXTURE, and it is a mistake of mine from this morning. dc_drop solves a potential only
    on a declared RAIL, so a tap whose reference conductor is declared a NODE can never be measured however
    good the mesh is. Board E's tracker pair references TRK_LSENSE and TRK_SW2, which board E declares as
    switching NODES, and the two rows written at 07:52 read back as 'the mesh solved no pad', which points at
    the tool when the answer is in the declaration. Proved to fail on the tool as it stood: `judge` took two
    arguments and had no way to tell the two silences apart."""
    d = [{"sense": "TRK_CSP", "rail": "TRK_LSENSE", "element": "R5.1", "tap": "R6.1", "full_scale_mv": 30.8}]
    rows, fails = K.judge(d, {"nets": {}}, {"rails": {}, "nodes": {"TRK_LSENSE": {}}})
    assert not fails, fails
    assert rows[0][1] is None and "declared a NODE" in rows[0][2] and "DECLARATION question" in rows[0][2], rows[0]


def t_a_rail_the_mesh_simply_missed_still_says_that():
    """THE ACCEPTABLE FIXTURE: a rail that IS declared and has no solved pad is the tool's silence, not the
    declaration's, and the two sentences must not merge."""
    d = [{"sense": "X", "rail": "VBUS20", "element": "R1.1", "tap": "R2.1", "full_scale_mv": 60.0}]
    rows, fails = K.judge(d, {"nets": {}}, {"rails": {"VBUS20": {}}, "nodes": {}})
    assert rows[0][1] is None and "the mesh solved no pad" in rows[0][2], rows[0]
