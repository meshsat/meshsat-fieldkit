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
