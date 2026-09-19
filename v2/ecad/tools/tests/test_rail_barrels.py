"""The rules of `rail_barrels.py`, the pre-route fixer for rule PI-003's cheap half.

MESHSAT-862, 19 September 2026. `rail_crossings.py` names the short crossings and lays nothing; this is the
tool that lays them, on the PLACED board, where the room beside a rail's source pad is still empty. Everything
worth a rule here is arithmetic over numbers or a property of the file, so all of it runs on the runner: the
placement itself (`plan`), the cap that refuses a busbar, the axis choice, and the four properties that keep
this file from having its own opinion about a count, a site, or what the DRC said.
"""
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS); sys.path.insert(0, HERE)
import harness
import rail_barrels as rb
import via_current as vc

SRC = open(os.path.join(TOOLS, "rail_barrels.py"), encoding="utf-8").read()


def _row(amps, drill=0.4, at=(10.0, 10.0), have=1, near=None, width=None):
    return {"net": "RAIL", "ref": "U1", "pad": "1", "at": at, "drill": drill,
            "width": width if width is not None else drill + 0.4,
            "near": near if near is not None else [at] * have,
            "have": have, "need": vc.barrels_for(amps, drill), "amps": amps,
            "part_amps": amps, "pads": 1, "why": ""}


OPEN = lambda x, y: True            # every site free
SHUT = lambda x, y: False           # no site free


def t_a_site_a_cluster_can_answer_is_planned():
    """THE ACCEPTABLE FIXTURE. 3.00 A on a 0.40 mm barrel needs four and one is there, so THREE are owed."""
    r = _row(3.0)
    pts, axis, note = rb.plan(r, OPEN)
    assert r["need"] == 4, r["need"]
    assert len(pts) == 3, (len(pts), note)


def t_a_site_that_needs_more_barrels_than_a_cluster_holds_is_declined():
    """THE DEFECTIVE FIXTURE, and it is board P's own: CELL4 crosses at ONE 0.50 mm barrel carrying 18.00 A.

    A 0.50 mm barrel holds 1.05 A, so the arithmetic asks for eighteen, and eighteen barrels in a row beside a
    pad is a busbar and a different pad. The tool must REFUSE to draw it and say so, because a fixer that
    answers any number turns a measured refusal into copper nobody chose."""
    r = _row(18.0, drill=0.5)
    assert r["need"] > rb.MAX_BARRELS, r["need"]
    pts, axis, note = rb.plan(r, OPEN)
    assert pts == [], pts
    assert "busbar" in note and "placement item" in note, note


def t_the_cap_is_a_number_a_caller_can_move_and_not_a_silence():
    """The same site with the cap raised is planned, so the refusal is the CAP's and not a failure to try."""
    r = _row(18.0, drill=0.5)
    pts, axis, note = rb.plan(r, OPEN, max_barrels=32)
    assert r["need"] == 18 and len(pts) == 17, (len(pts), r["need"])


def t_the_lattice_is_anchored_on_the_barrel_already_there_and_never_collides_with_it():
    """The defect that made board A's first real run lay nothing: `need` points centred on the PAD put two
    new holes half a pitch from the barrel standing in the middle, and the DRC answered `hole_to_hole` at
    every one of seven sites. The new barrels grow out of the one that is there."""
    # The fanout's via sits BESIDE the pad, not on it, which is what makes the anchor visible: a lattice on
    # the pad centre and a lattice on the barrel are different lattices, and only one of them misses the
    # barrel. This fixture is 0.55 mm off the pad, which is where `prefanout` puts a via on a 1 mm land.
    r = _row(3.0, at=(10.0, 20.0), near=[(10.55, 20.0)])
    pts, axis, note = rb.plan(r, OPEN)
    floor = r["drill"] + rb.FLOOR
    for px, py in pts:
        assert math.hypot(px - 10.55, py - 20.0) >= floor - 1e-9, ("collides with the barrel there", px, py)
    on_lattice = [p for p in pts if abs(math.hypot(p[0] - 10.55, p[1] - 20.0) - (r["drill"] + 0.4)) < 1e-9]
    assert on_lattice, ("no barrel sits one pitch from the one already there", pts)


def t_a_barrel_already_there_that_is_off_the_lattice_is_still_kept_clear_of():
    """Two barrels 0.50 mm apart on a 0.40 mm drill: the lattice anchored on the first puts its next point
    0.80 mm along, which is 0.30 mm from the second, under this project's 0.6995 mm hole-to-hole floor. The
    plan must step past it rather than lay a hole the DRC will answer `hole_to_hole` for."""
    r = _row(3.0, at=(10.0, 20.0), have=2, near=[(10.0, 20.0), (10.80, 20.30)])
    pts, axis, note = rb.plan(r, OPEN)
    floor = r["drill"] + rb.FLOOR
    for px, py in pts:
        for qx, qy in r["near"]:
            assert math.hypot(px - qx, py - qy) >= floor - 1e-9, ((px, py), (qx, qy))


def t_only_the_barrels_still_owed_are_laid():
    """A site with three of the four it needs is owed ONE, not four."""
    r = _row(3.0, have=3, near=[(10.0, 10.0), (10.8, 10.0), (11.6, 10.0)])
    pts, axis, note = rb.plan(r, OPEN)
    assert len(pts) == 1, (len(pts), note)


def t_a_site_with_nowhere_free_to_stand_is_declined_and_not_forced():
    """`return_via._site_free` is the board's answer; when it refuses everywhere the site is a placement item
    and the tool says so rather than laying copper the DRC will strip."""
    r = _row(3.0)
    pts, axis, note = rb.plan(r, SHUT)
    assert pts == [] and "nowhere to stand" in note, note


def t_a_site_that_already_carries_what_it_needs_is_not_touched():
    r = _row(0.5, have=4, near=[(10.0, 10.0)] * 4)
    pts, axis, note = rb.plan(r, OPEN)
    assert pts == [] and "already carries" in note, note


def t_the_pitch_keeps_this_project_s_hole_to_hole_floor():
    """Board E's block vias went to 0.10 mm hole to hole on 18 September and the placed board came back with
    eight hole_to_hole violations. The plan may never produce that, at any drill this project uses."""
    for drill in (0.2, 0.25, 0.3, 0.4, 0.5, 0.7):
        r = _row(6.0, drill=drill)
        pts, axis, note = rb.plan(r, OPEN, max_barrels=64)
        allp = pts + list(r["near"])
        for i in range(len(allp)):
            for j in range(i + 1, len(allp)):
                d = math.hypot(allp[i][0] - allp[j][0], allp[i][1] - allp[j][1])
                if d == 0: continue        # two recorded barrels at one point is the fixture, not a plan
                assert d - drill >= rb.FLOOR - 1e-9, (drill, d, d - drill)


def t_the_axis_chosen_is_the_one_the_board_leaves_room_on():
    """A wall of refused sites due east and west must push the cluster onto y, and the other way round."""
    r = _row(3.0)
    pts, axis, _ = rb.plan(r, lambda x, y: abs(y - 10.0) > 1e-9)      # only off-axis in y is free
    assert axis == "y" and len(pts) == 3, (axis, pts)
    pts, axis, _ = rb.plan(r, lambda x, y: abs(x - 10.0) > 1e-9)
    assert axis == "x" and len(pts) == 3, (axis, pts)


def t_the_board_s_own_site_test_is_the_one_used_and_not_a_second_copy():
    """`return_via._site_free` knows about every other net's pads, tracks and vias on every layer, and it
    carries the paste-aperture fix of 17 September. A second geometry test here would be the third tool with
    that defect."""
    assert "_rv._site_free(" in SRC
    assert "GetBoundingBox()" not in SRC and "IsOnCopperLayer" not in SRC


def t_a_routed_board_is_this_tool_s_refusal_and_not_its_work():
    """Locked escapes are a placed board; a field of unlocked router copper is not."""
    class _T:
        def __init__(s, locked): s._l = locked
        def GetClass(s): return "PCB_TRACK"
        def IsLocked(s): return s._l
    class _B:
        def __init__(s, t): s._t = t
        def GetTracks(s): return s._t
    assert rb._routed(_B([_T(True)] * 4000)) is False
    assert rb._routed(_B([_T(False)] * 4000)) is True
    assert rb._routed(_B([_T(False)] * 50)) is False, "a handful of loose pieces is not a route"


def t_the_count_is_the_rule_s_own_and_not_this_file_s():
    """The barrel count comes from `via_current` through `power_copper`, which is what judges it after the
    route. A second implementation here is how a fixer and its judge stop agreeing."""
    assert "power_copper" in SRC and "via_current" in SRC
    assert "0.725" not in SRC and "0.44" not in SRC, "rail_barrels carries IPC-2221's own exponents"


def t_the_sites_come_from_the_judge_s_own_walk():
    """`rail_crossings.rows` is the judge carrying numbers instead of prose; this file must read THAT."""
    assert "rail_crossings" in SRC and "_rc.rows(" in SRC
    # The rule is about where the SITES come from, not about which method names appear: `_hole_free` reads
    # drills to judge a CANDIDATE, which is geometry and not site discovery. What must not be here is a second
    # walk that decides which crossings are short.
    body = SRC[SRC.index("def main(argv):"):]
    assert "barrels_for(" not in body, "main computes its own barrel count instead of reading the judge's rows"
    assert body.count("_rc.rows(") == 1, "the sites come from somewhere other than the judge's own walk"
    assert "rows, judged = _rc.rows(" in body, "the rows are not taken straight from the judge"
    for r in ("for r in rows", "plans.append", "declined.append"):
        assert r in body, "the plan is not built from the judge's rows"
    assert '"need"' not in body.split("for r in rows")[0], "main decides how many barrels a site needs"


def t_it_does_not_carry_its_own_copy_of_the_drc_helpers():
    """`return_gaps.py` quietly stopped agreeing with its own gate on 17 September. One answer to 'what does
    the DRC say about this board', and it is via_parallel's."""
    assert "_vp._measure(" in SRC and "_vp._hit_positions(" in SRC
    assert "\ndef _measure(" not in SRC and "\ndef _hit_positions(" not in SRC
    assert "drc.sh" not in SRC, "rail_barrels shells out to the DRC itself"


def t_it_reports_before_it_lays():
    """A dry run is the default: `--apply` is what puts copper on a board."""
    assert 'apply_ = "--apply" in argv' in SRC
    body = SRC[SRC.index("def main(argv):"):]
    i = body.find('if not apply_:')
    j = body.find('_save_filled(')
    assert 0 < i < j, "the dry-run return does not come before the first save inside main"
    assert "SaveBoard" not in body[:i], "main writes the board before it has decided to"


def t_a_refused_site_names_the_counterparty_and_not_only_the_type():
    """`escape_prune` printed a pad list until 8 September and the placement could not be corrected from it.
    A type on its own ("clearance") is the same shape: the DRC's description names both items of the pair."""
    assert 'v_.get("description")' in SRC, "the refusal carries no description"
    i = SRC.find("that site is reverted")
    j = SRC.find('print("rail_barrels:     %s" % why)')
    assert 0 < i < j, "the description is not printed with the refusal"


def t_a_site_the_drc_refuses_is_reverted_alone_before_the_whole_set_is():
    """The keep-what-the-DRC-accepts shape of `stub_accept` and `direct_close`, not all or nothing first."""
    assert "that site is reverted" in SRC
    assert "reverting every barrel" in SRC
    assert SRC.find("that site is reverted") < SRC.find("reverting every barrel")


def t_it_is_declared_in_the_coverage_map_as_pi003_s_fixer():
    import yaml
    cov = yaml.safe_load(open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8"))
    ent = (cov.get("coverage") or {}).get("PI-003") or {}
    blob = repr(ent)
    assert "rail_barrels" in blob, "PI-003 does not name its pre-route fixer"


def t_the_board_is_refilled_before_anything_measures_it():
    """A through via lands in every pour it crosses. A pour filled before the via existed still has its copper
    at that point, and the DRC answers `zone clearance 0.3000 mm; actual 0.0000 mm` at every barrel: board A's
    first three runs of this tool reverted all seven sites for that and nothing else. The finish learnt this on
    14 September; a tool that adds copper and then reads a DRC has to learn it too."""
    assert "ZONE_FILLER" in SRC, "rail_barrels measures a board it has not refilled"
    fn = harness.block(SRC, "def _save_filled")
    assert fn, "there is no refill helper to read"
    # THE DOCSTRING IS PROSE, NOT CODE, and it names every one of these three: read the body after it, or the
    # rule is about the order the explanation happens to be written in.
    fn = fn[fn.index('"""', fn.index('"""') + 3) + 3:]
    i_save, i_load, i_fill = fn.find("SaveBoard"), fn.find("LoadBoard"), fn.find("ZONE_FILLER")
    assert 0 <= i_save < i_load < i_fill, \
        "the refill does not save, then reload, then fill, which is what stops ZONE_FILLER segfaulting"
    # every measurement of this board goes through it
    assert "pcbnew.SaveBoard(path, b)\n    h, u" not in SRC and "pcbnew.SaveBoard(path, b)\n        h, u" not in SRC
    body = SRC[SRC.index("def main(argv):"):]
    assert body.count("_save_filled(") == 2, "main does not write the board through the refill exactly twice"
    assert "SaveBoard" not in body, "main saves the board without refilling it"


def t_the_chain_runs_it_after_the_fanout_and_before_the_pre_lay():
    """Order matters twice. AFTER the fanout, the ground grid and the escape prune, so `_site_free` sees every
    via those stages laid; BEFORE the pre-lay, because power copper is not a thing a signal run should have to
    be moved for. It is declared per board, like `gnd_grid`, so a board that has not been read gets nothing."""
    full = open(os.path.join(TOOLS, "full.sh"), encoding="utf-8").read()
    assert "rail_barrels.py" in full, "the chain never lays the barrels a rail's own crossing needs"
    i_fan = full.index("prefanout.py")
    i_rb = full.index("rail_barrels.py")
    i_prelay = full.index("STUB_NETS=\"$GNETS\"")   # the pre-lay stage itself, not the paragraph about it
    assert i_fan < i_rb < i_prelay, (i_fan, i_rb, i_prelay)
    assert "'rail_barrels'" in full or '"rail_barrels"' in full, "the stage is not declared per board"


def t_every_verdict_names_the_rail_table_it_read_and_when_it_was_written():
    """The intent file records a project name and a minute, never a board hash, so this tool cannot refuse a
    mismatched pair. What it must not do is leave a reader guessing: the board, its mtime, the intent path and
    the intent's own `written` stamp travel in every verdict taken after the table is read. An intent
    regenerated on another day describes another board's rails, which is the evidence-crossing defect this
    project has paid for twice."""
    body = SRC[SRC.index("def main(argv):"):]
    assert '"intent_written"' in body and '"board_mtime"' in body
    after = body[body.index("_inputs = {"):]
    assert after.count("inputs=_inputs") == 3, \
        "a verdict written after the rail table was read does not name it (%d of 3)" % after.count("inputs=_inputs")


def t_it_leaves_no_backup_behind_in_the_project_directory():
    """The backup exists so a hurt board can be put back; once the board that stands is chosen it is this
    tool's scratch, and a stray `.bak` beside a phase board is the next person's question."""
    body = SRC[SRC.index("def main(argv):"):]
    assert "os.remove(bak)" in body, "the backup is never removed"
    assert body.index("shutil.copy2(path, bak)") < body.index("os.remove(bak)")


def t_a_candidate_must_pass_the_hole_test_as_well_as_the_copper_test():
    """`return_via._site_free` keeps a barrel's RING clear of other nets' copper. Hole to hole is a different
    rule with a different number and it is not in that test: two 0.25 mm drills need 0.5495 mm between centres
    where the copper test is satisfied at 0.362. E21's own chain proved it, the DRC refusing a barrel at
    J_BLK pad 1 for `hole_to_hole` alone. Every drilled hole counts, this net's included: a hole does not care
    whose net it is."""
    assert "_hole_free(b, X, Y, _d)" in SRC, "the site test does not ask about holes"
    body = SRC[SRC.index("def _hole_free"):SRC.index("def _routed")]
    assert "GetDrillSize" in body, "plated component holes are not counted"
    assert "PCB_VIA" in body, "other vias' holes are not counted"
    assert "GetNetname" not in body, "the hole test skips its own net, and a hole does not care whose net it is"
    assert "FLOOR" in body, "the hole test does not use this project's own hole-to-hole floor"


def t_the_fixer_never_decides_pi003_and_never_blocks_a_route():
    """PI-003 is decided after the route by `via_current` on the solved mesh; this tool lays copper and reports
    what it laid. The first version wrote a deciding verdict on the --apply path and E21's chain was
    GATE_BLOCKED by it, because board E has two sites the tool declines as busbars and declines CORRECTLY. A
    fixer that stops a route for a declared placement item is a fixer behaving as a blocker."""
    body = SRC[SRC.index("def main(argv):"):]
    segs = body.split("_v.write(")[1:]
    assert len(segs) >= 4, "fewer verdict paths than this tool has"
    for seg in segs:
        head = seg[:seg.index("rules=[")] if "rules=[" in seg else seg[:400]
        assert ("advisory=True" in head) or ("missing_input=" in head), \
            "a verdict that is neither advisory nor a declared missing input: %r" % head[:140]


def t_a_cluster_only_part_of_which_fits_is_declined_rather_than_half_laid():
    """The case that matters, because it is the one that looks like progress. 3.00 A on a 0.40 mm barrel needs
    four and one is there, so three are owed at a pitch of 0.8 mm: two of them land inside a 1.0 mm window and
    the outer two do not. Laying the two would put copper on the board and leave the crossing reading exactly
    as short as before, because the judge counts what is inside its window and nothing else."""
    r = _row(3.0, drill=0.4, at=(10.0, 10.0), near=[(10.0, 10.0)])
    r["reach"], r["at_pad"] = 1.0, (10.0, 10.0)
    assert r["need"] == 4, r["need"]
    pts, axis, note = rb.plan(r, OPEN)
    assert pts == [], (pts, note)
    assert "only 2 of the 3" in note and "placement item" in note, note


def t_a_cluster_that_does_not_fit_the_judge_s_window_is_declined_whole():
    """Half an answer is not an answer: the judge counts barrels within its own window and nothing else, so
    laying part of a cluster leaves the crossing exactly as short as it was while putting copper on a board.
    The window travels in the row (`reach`, `at_pad`) so the fixer and the judge cannot disagree about it."""
    r = _row(6.0, drill=0.5, at=(10.0, 10.0), near=[(10.0, 10.0)])
    r["reach"], r["at_pad"] = 0.6, (10.0, 10.0)          # a millimetre of room, a cluster of nine
    pts, axis, note = rb.plan(r, OPEN, max_barrels=16)
    assert pts == [], (pts, note)
    assert "judged over" in note and "placement item" in note, note


def t_a_cluster_that_fits_is_still_laid():
    """THE ACCEPTABLE FIXTURE for the same rule: two barrels of 0.40 mm span 0.8 mm and fit a 1.3 mm window."""
    r = _row(1.4, drill=0.4, at=(10.0, 10.0), near=[(10.0, 10.0)])
    r["reach"], r["at_pad"] = 1.3, (10.0, 10.0)
    assert r["need"] == 2, r["need"]
    pts, axis, note = rb.plan(r, OPEN)
    assert len(pts) == 1, (pts, note)
    assert math.hypot(pts[0][0] - 10.0, pts[0][1] - 10.0) <= 1.3 + 1e-9
