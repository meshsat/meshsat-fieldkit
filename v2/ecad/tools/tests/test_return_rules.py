#!/usr/bin/env python3
"""The two return-current rules of 15 September 2026 (owner ruling 20:15 CEST, appendix 32.198) as structure: what the
finish runs, in which order, what every board declares, and that the signal filter reads its exclusions from data.
The board-level fixtures (a track with and without a plane under it, a via with and without its ground via) are in
test_board_gates.py, where pcbnew is."""
import os, re, json, glob
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _src(name): return open(os.path.join(TOOLS, name), errors="replace").read()


def _code(name):
    """The finish without its comment lines."""
    return "".join(l for l in open(os.path.join(TOOLS, name), errors="replace") if not l.strip().startswith("#"))


def t_the_finish_places_return_vias_after_the_last_copper_stage_and_before_the_final_refill():
    t = _code("finish.sh")
    i_rail = t.index("rail_prune.py"); i_rv = t.index("return_via.py"); i_fill = t.rindex("ZONE_FILLER"); i_gate = t.index("routed-board gate")
    assert i_rail < i_rv < i_fill < i_gate, "return_via.py must run after rail_prune and before the final refill and the routed-board gate (positions %d %d %d %d)" % (i_rail, i_rv, i_fill, i_gate)
    assert "cfg x return_via" in t, "the stage is declared per board through cfg, like every other finish stage"


def t_every_board_declares_return_via_with_its_reason():
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        d = json.load(open(p)).get("finish", {})
        assert d.get("return_via") is True, "%s: finish.return_via must be true (owner ruling 15 Sep 2026: every board)" % os.path.basename(p)
        assert "32.198" in d.get("_return_via_why", ""), "%s: _return_via_why names the appendix section" % os.path.basename(p)


def t_the_intent_check_judges_every_signal_net_and_the_return_vias():
    s = _src("intent_checks.py")
    assert "signalnets.classify" in s and "signalnets.is_signal" in s, "rule 1 judges the signal nets from signalnets, not the pair classes alone"
    assert "return_via.judge" in s, "rule 2 is judged inside the board gate (intent_checks item 4)"
    assert "cls_of(net) not in targets and not signalnets.is_signal" in s, "a pair-class net and a signal net are both judged; neither filter alone"


def t_the_signal_filter_reads_its_exclusions_from_data_not_a_net_list():
    s = _src("signalnets.py")
    body = s.split('"""', 2)[2]   # past the docstring
    lits = re.findall(r'"([^"\n]*)"', body)
    allowed = {"GND", "unconnected-", "Default", "ground", "unconnected pin", "owns a filled zone", "rail of the intent file", "class %s", ".kicad_pro", "net_settings", "netclass_assignments", "/", ""}
    names = [l for l in lits if l not in allowed and not l.isupper()]
    assert not names, "signalnets.py must not carry net names as literals (it reads zone owners, intent rails and classes): %s" % names
    assert "GetZoneName" not in body and "z.GetNetname()" in body, "a zone owner is read off the zone's net, not its name"
    assert "POWER_CLASSES" in body and "class_of" in body, "power nets are excluded by their CLASS from the project file"


def t_the_return_via_tool_is_a_gate_and_a_fixer_with_the_finish_s_judgement():
    s = _src("return_via.py")
    assert "verdict.write(\"return_via\"" in s, "--check writes the verdict file"
    assert "h1 > h0 or u1 > u0" in s, "the fixer reverts when the hard or the unrouted count rose against the board it was handed"
    assert "FAN_PITCH_MM = 0.5" in s and "RETURN_MM = 1.5" in s, "the ruled numbers: 0.5 mm fans exempt, 1.5 mm to the ground via"
    assert "_in_gnd_fill" in s, "a ground via is placed only inside a ground fill"


def t_every_copper_editing_pass_after_the_router_runs_under_the_one_guard():
    """15 September 2026, red team round four H2: five hand-rolled keep-or-revert blocks with three comparison rules
    became one function. A copper pass added later must go through it too."""
    t = _code("finish.sh")
    for stage in ("guarded stub stub_stage", "guarded stitch_prune", "guarded direct_close", "guarded return_via"):
        assert stage in t, "%s is not under the guard" % stage
    assert '. "$T/guarded.sh"' in t, "the finish does not source the guard"
    assert "GUARD_MODE=pre guarded prelay" in _code("full.sh"), "the pre-lay is not under the guard"
    g = _src("guarded.sh")
    assert '"$AH" -gt "$BH"' in g and '"$AU" -gt "$BU"' in g and 'verdict.write("guard-"' in g, "the guard compares both counts and writes a verdict"


def t_the_ground_via_grid_is_laid_after_the_fanout_and_before_the_pre_route_drc():
    """gnd_grid.py (15 September 2026) lays rule 2's ground vias before the route, on the board with its escapes, fanout and
    pair copper down, and the pre-route DRC then judges them with everything else; it runs only where a board declares it."""
    src = open(os.path.join(TOOLS, "full.sh")).read()
    i_fan = src.index("prefanout.py"); i_grid = src.index("gnd_grid.py"); i_drc = src.index("--label 'pre-route DRC'")
    assert i_fan < i_grid < i_drc, "the grid stage is not between the fanout and the pre-route DRC"
    assert "get('gnd_grid')" in src, "the grid stage is not read from the board file"
    g = open(os.path.join(TOOLS, "gnd_grid.py")).read()
    for must in ("other_zones", "via_keepouts", "_in_gnd_fill", "_site_free", "_own_hard"):
        assert must in g, "gnd_grid.py lacks its %s test" % must


def t_a_solder_jumpers_pads_carry_the_class_clearance_before_the_route():
    """D12's grid route (15 September 2026): KiCad's SolderJumper footprints declare a zero local pad clearance, the DSN hands it
    to the router, and the routed board carries a hard clearance item at the jumper. full.sh sets the class clearance on those
    pads after the placement and before the escapes, on every board."""
    src = open(os.path.join(TOOLS, "full.sh")).read()
    i_gen = src.index("gen_pcb_${L}3.py"); i_j = src.index("jumper_clearance.py"); i_esc = src.index("escape.py $N.kicad_pcb")
    assert i_gen < i_j < i_esc, "jumper_clearance.py is not between the placement and the escapes"
    g = open(os.path.join(TOOLS, "jumper_clearance.py")).read()
    assert "SolderJumper" in g and "SetLocalClearance" in g, "jumper_clearance.py does not set the pads' local clearance"
