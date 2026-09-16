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


def t_no_net_class_sits_below_the_boards_own_minimum():
    """Rule IMP-002. Board B's project file shipped USB and DIFF100 at 0.10 mm against its own 0.127 mm board
    minimum while the generator's table said 0.127: two hand-written copies that had drifted. The project
    classes are built from the generator's table now, and full.sh gates the board on it."""
    src = open(os.path.join(TOOLS, "full.sh")).read()
    i_gen = src.index("gen_pcb_${L}3.py"); i_cf = src.index("class_floor.py"); i_drc = src.index("--label 'pre-route DRC'")
    assert i_gen < i_cf < i_drc, "class_floor.py does not run between the placement and the pre-route DRC"
    assert "block \"a net class is below" in src, "the chain does not block on it"
    b3 = open(os.path.join(TOOLS, "gen_pcb_b3.py")).read()
    i_cls = b3.index('net_settings", {})["classes"]')
    block = b3[i_cls - 400:i_cls + 200]
    assert "CLASSES[" in block, "board B writes its project classes from a second hand-written list again"


def t_the_fixer_may_reach_past_the_target_but_the_judge_may_not():
    """Reaching further is a repair; moving the bar is a ruling (MESHSAT-862, 16 September 2026).

    Board D12 routed 0 hard and 0 unrouted and one signal via of 37, HUB_DM3 at the hub port, had all 64 of its
    candidate ground-via sites inside 1.5 mm on another net's copper. A ground via at 2 mm is not the declared
    number, and it is a shorter return loop than no via at all, so the fixer now searches outward and prints
    what it achieved. The thing that must NOT happen is the bar moving with it: the verdict is still taken at
    the declared radius, so a via placed at 2 mm still reads as lacking and reaches the owner as a measured
    choice rather than disappearing into a pass."""
    src = open(os.path.join(TOOLS, "return_via.py"), encoding="utf-8").read()
    assert "OUTER = (" in src, "the outer rings are gone"
    i_outer = src.index("OUTER = (")
    # the judge is called with the radius it was given, never with a widened one
    for call in ("before = judge(b, path, radius)", "after = judge(b, path, radius)"):
        assert call in src, "the fixer stopped judging at the declared radius: %r" % call
    assert "judge(b, path, radius + " not in src and "judge(b, path, OUTER" not in src, \
        "the judge was widened to match the fixer, which is the bar moving"
    # and a placement beyond the radius is reported rather than silently kept
    assert "BEYOND the declared" in src, "a ground via placed past the target is not reported"


def t_the_check_reads_the_declared_radius_and_says_so():
    """The verdict names the number it judged at, because a return-path figure with no radius beside it is the
    kind of claim this registry exists to refuse."""
    src = open(os.path.join(TOOLS, "return_via.py"), encoding="utf-8").read()
    i = src.index("def check(")
    seg = src[i:i + 1600]
    assert "within %.1f mm" in seg and "radius" in seg, "the check does not print the radius it used"


def t_a_board_gate_reports_the_intent_items_and_does_not_count_them():
    """One composite verdict must not fail every rule it is mapped to (MESHSAT-862, 16 September 2026).

    Board D routed 0 hard and 0 unrouted with one item left, a single signal via short of a ground via. That is
    an EMC item and RET-004's to decide. Because the board gate counted it in its own failure list as well, the
    MECHANICAL rule MEC-001 read FAIL on six boards from the same defect: the readiness then names a rule that
    is not the one that failed, which is worse than a wrong number because it points the work at the wrong
    place. The gate prints those items and the five intent verdicts decide them; the finish blocks on those
    verdicts, so it stops in exactly the same places."""
    import os
    for L in ("a", "b", "c", "d", "e", "p"):
        s = open(os.path.join(TOOLS, "check_pcb_%s.py" % L), encoding="utf-8").read()
        if "intent_checks as _ic" not in s: continue
        assert "_intent_check" in s, "check_pcb_%s.py still hands the intent run its own failure list" % L
        assert "_ic.run(b, _intent_check" in s, "check_pcb_%s.py does not pass the reporting wrapper" % L
    f = open(os.path.join(TOOLS, "finish.sh"), encoding="utf-8").read()
    for name in ("intent_return_path", "intent_return_via", "intent_decoupling", "intent_rails"):
        assert name in f, "the finish does not block on %s, so removing it from the gate weakened a gate" % name
