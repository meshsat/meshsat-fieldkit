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
        _t = json.load(open(p))
        if _t.get("chain") is False: continue   # board E5 has no finish: it is generated from board A's board file
        d = _t.get("finish", {})
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
    for call in ("before = judge(b, path, radius, identity=_identity)",
                 "after = judge(b, path, radius, identity=_identity)"):
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


def t_a_check_belongs_to_exactly_one_rule_and_a_quotation_cannot_move_it():
    """16 September 2026, evening. The bucket split was written so that one decoupling capacitor 3 mm too far
    from its pin could not fail the return-path rule. It then classified by searching the WHOLE message, and
    every return-path line quotes the net's declared basis in brackets: board B's three STM32 core-regulator
    nets are declared as "an internal-supply decoupling node, a local rail", so the word decoupling inside that
    quotation put three RETURN-PATH failures into the DECOUPLING verdict and rule DEC-001 failed on board B for
    something that is not decoupling. The quotation is stripped before the keys are matched, and a line two
    buckets claim is named rather than counted twice."""
    import os
    src = open(os.path.join(TOOLS, "intent_checks.py"), encoding="utf-8").read()
    i = src.index("BUCKETS = (")
    w = src[i:i + 2200]
    assert 'head = lambda t: t.split("[")[0]' in w, "the bucket keys are matched against the quoted evidence"
    assert "k in head(t)" in w, "the whole message is still searched"
    assert "BELONGS TO %d RULES" in src, "a check claimed by two buckets is silently counted in both"

    # the real message shapes, each landing in exactly one bucket
    BUCKETS = (("intent_return_path", ("return path",)), ("intent_return_via", ("return via",)),
               ("intent_decoupling", ("bypass", "decoupling")),
               ("intent_rails", ("is a declared rail", "intent rail", "intent file carries")))
    head = lambda t: t.split("[")[0]
    cases = {
        "return path under IOCA_VCAP (LOW_SPEED_OR_DC): a reference exists under -0.0 of 2.9 mm "
        "[an internal-supply decoupling node, a local rail]": "intent_return_path",
        "return via: 41 of 245 signal vias have a ground via within 1.5 mm": "intent_return_via",
        "bypass C18 to U6 pin 2: 2.1 mm from the pin it serves": "intent_decoupling",
        "every power-symbol net is a declared rail (30 of 36)": "intent_rails",
    }
    for msg, want in cases.items():
        owners = [n for n, keys in BUCKETS if any(k in head(msg) for k in keys)]
        assert owners == [want], (msg[:60], owners)


def t_the_gap_report_judges_by_the_same_bar_as_the_gate():
    """A diagnostic that disagrees with the gate sends a reader to fix copper the gate does not refuse.

    `return_gaps.py` opens by saying its totals agree with the gate's line, and since 16 September they did
    not: the gate asks each net the question its spectral class deserves and the report kept the one uniform
    limit the gate had before that. On board C it named 87 nets of 127 where the gate fails 18, and it was
    failing slow nets for a gap when the question asked of a slow net is whether a reference exists at all.
    """
    import os
    src = open(os.path.join(TOOLS, "return_gaps.py"), encoding="utf-8").read()
    assert "import signal_class" in src or ", signal_class" in src, "the report does not read the spectral class"
    assert "signal_class.limit(" in src, "the report computes its own limit instead of the gate's"
    assert 'q == "EXISTS"' in src, "a slow net is still failed for a gap rather than for having no reference"
    assert "as the gate judges them" in src, "the report does not say which bar it used"


def t_no_tool_asks_a_via_for_its_width_without_a_layer():
    """KiCad 9 makes a via's width per layer, and the bare `GetWidth()` raises a wxWidgets assertion on every
    call: on a host built with assertions it prints a line per via and can end the process, which is how it
    presented on 17 September 2026 when the board-fixture family was first run where KiCad is. It was live in
    `return_via.py`, on every via of every real board, while the fixer looked for a free site; in
    `board_diff.py`, which compares two boards via by via; in `fix_a17_node.py`; and in `dot_prune.py`, whose
    ternary called the SAME method on both branches, so whatever it meant to do for a via it never did.

    The rule reads the code rather than the runtime, because the tools it governs need KiCad and the runner
    has none: a line that identifies an item as a PCB_VIA may not then ask it for a bare width."""
    import os, re
    bad = []
    # 18 September 2026: pair_router/ as well, where occupancy.py asked every via for a bare width in its site test
    # and B22's pair pass printed the assertion once per via.
    files = [fn for fn in sorted(os.listdir(TOOLS)) if fn.endswith(".py")] + \
            ["pair_router/" + fn for fn in sorted(os.listdir(os.path.join(TOOLS, "pair_router"))) if fn.endswith(".py")]
    for fn in files:
        if fn == "kicad_compat.py": continue
        src = open(os.path.join(TOOLS, fn), encoding="utf-8", errors="replace").read()
        for i, line in enumerate(src.splitlines(), 1):
            # the identifier this line has just called a via, asked for a bare width on the same line
            for m in re.finditer(r'(\w+)\.GetClass\(\)\s*==\s*"PCB_VIA"', line):
                if re.search(r"\b%s\.GetWidth\(\s*\)" % re.escape(m.group(1)), line):
                    bad.append("%s:%d %s" % (fn, i, line.strip()[:90]))
            # and the blunt case: a via built or fetched on this line and asked for its width
            if re.search(r"PCB_VIA\b", line) and re.search(r"\bv\.GetWidth\(\s*\)", line):
                bad.append("%s:%d %s" % (fn, i, line.strip()[:90]))
    assert not bad, "a via is asked for its width with no layer, which asserts in KiCad 9: %s" % bad


# ---------------------------------------------------------------------------------------------------------
# A DERIVED COPY MUST NOT DECIDE A NET'S CLASS BY ITS OWN FILENAME (17 September 2026, rule RET-004).
#
# The fixer's dry run works on `<board>-return_via-dry.kicad_pcb`, and BOTH lookups that make this rule
# proportionate are keyed on the board's name: `intent.load` finds no intent beside a file with that stem and
# `signal_class` finds no letter for it in the board table. So every rail and every declaration disappeared,
# all 131 of board E's signal vias were judged as though they were fast where the judge judges 60 and asks for
# 4, and the fixer placed 22 ground vias for a fan tachometer, an opto inhibit, a Geiger input and a current
# monitor. Its report could not be compared with the verdict at all, which is how it went unnoticed.

def _rv_src():
    """return_via's source, read as text: this file runs where pcbnew is not, and the tool imports it."""
    return open(os.path.join(TOOLS, "return_via.py"), encoding="utf-8").read()


def t_the_judge_takes_an_identity_that_is_not_the_file_it_was_handed():
    src = _rv_src()
    assert "def judge(b, path=None, radius=RETURN_MM, identity=None):" in src, "the judge takes no identity"
    assert "identity = identity or path" in src
    for call in ("intent.load(identity)", "signalnets.classify(b, identity", "_sc.classify(b, identity"):
        assert call in src, "the classification still keys on the copy's own path: %s" % call


def t_the_fixer_passes_the_original_board_as_the_identity():
    src = _rv_src()
    i_fix = src.index("def fix(path, dry=False")
    body = src[i_fix:src.index("\ndef ", i_fix + 10)] if "\ndef " in src[i_fix + 10:] else src[i_fix:]
    assert "_identity = path" in body and body.index("_identity = path") < body.index("if dry:"), \
        "the identity is taken after the path has been replaced by the copy"
    assert body.count("identity=_identity") >= 2, "a judge call in the fixer still has no identity"


def t_an_unclassified_run_says_so_instead_of_reporting_a_measured_zero():
    """An empty classification makes every net UNKNOWN, which this rule judges at the strictest bar. That is
    the safe direction and it must never be silent: the printed line used to read '0 on a net with no edge to
    return', which is what a board with no slow nets also reads."""
    src = _rv_src()
    assert "NO SIGNAL CLASSIFICATION" in src, "the empty classification is silent again"
    assert '"classified": bool(_cls)' in src, "the reading does not say whether it was classified"


def t_the_examination_runs_before_the_screen_that_reads_it():
    """18 September 2026. RET-004's requirement makes it a SCREEN for RET-003: a via beyond the screening
    distance is examined against that rule rather than failed outright, and the examination is `ref_change`'s
    per-via reading of what each transition references. The sweep ran the screen at line 92 and the examination
    twenty-six lines later, so the file never existed when it was wanted; with the order the wrong way round the
    screen declares its missing input and the reading is INCONCLUSIVE, which is honest and is not a reading."""
    t = _code("gate_sweep.sh")
    i_ref = t.index("ref_change.py"); i_rv = t.index("return_via.py")
    assert i_ref < i_rv, "gate_sweep runs return_via before ref_change, so the screen has nothing to examine with"


def t_the_screen_names_what_it_examined_and_what_still_stands():
    """A count of flagged vias is not a diagnosis, which is the lesson of 12 September in a third place. The
    verdict carries the two buckets the examination removes (a reference that never changes, and a change to
    another NET where only a capacitor can help) and the vias that stand as this screen's own case, so the
    reader can tell a board that needs ground vias from a board that needs `return_stitch`."""
    s = _src("return_via.py")
    for k in ("examined_same_reference", "examined_to_power", "unclassified", "standing"):
        assert '"%s"' % k in s, "the return-via verdict does not count %s" % k
    assert "missing_input=missing" in s, \
        "the screen does not declare the examination as a missing input, so a reading taken without it could " \
        "displace one taken with it"


def t_a_pour_is_an_obstacle_to_a_closure_and_not_to_a_pre_lay():
    """MEASURED ON BOARD D, 18 September 2026, after three boards' pre-lays had laid nothing.

    `stub_router`'s obstacle map has carried every filled pour since 16 September, and it must: in the FINISH a
    piece laid through a plane is measured against a fill that has not moved, and board A's closures shorted its
    ground that way. At PRE-LAY time none of that is true. Nothing is routed yet, the stage re-fills before
    anything judges the board, and KiCad's fill retreats around a locked track exactly as it does around the
    router's own, which is why the ROUTER may cross a plane and this tool may not. With the pours in the map a
    poured board has almost nothing free: board D's pre-lay reported **5,140 free cells of 834,561** and
    `/PCM_VDD` FAILED pad to pad three times in 833 s on a board with no routing on it at all. With
    `STUB_POUR_OBSTACLE=0` the same board, the same net and the same window read **1,324,904 free cells and
    closed 3 of 3**, and the board after its own refill reads hard 0 of the fifteen types. The flag defaults to
    ON so a finish is unchanged, and the pre-lay stage is the one caller that turns it off."""
    s = _src("stub_router.py")
    assert 'os.environ.get("STUB_POUR_OBSTACLE", "1")' in s.replace("__import__(\"os\").", "os."), \
        "the pour obstacle is not a flag, or its default is not ON"
    i = s.index("_POUR_OBSTACLE == 0")
    assert "z.GetFilledArea()" in s[i:i + 300], "the flag does not guard the FILLED-POUR branch of the map"
    t = _code("full.sh")
    j = t.index("STUB_NETS=\"$GNETS\"")
    assert "STUB_POUR_OBSTACLE" in t[max(0, j - 400):j], "the pre-lay stage does not turn the pour obstacle off"
    fin = _code("finish.sh")
    assert "STUB_POUR_OBSTACLE" not in fin, "the finish turns the pour obstacle off, which is what shorted board A"
