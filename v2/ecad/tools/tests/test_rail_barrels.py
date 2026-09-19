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


def _row(amps, drill=0.4, at=(10.0, 10.0), have=1):
    return {"net": "RAIL", "ref": "U1", "pad": "1", "at": at, "drill": drill,
            "have": have, "need": vc.barrels_for(amps, drill), "amps": amps,
            "part_amps": amps, "pads": 1, "why": ""}


def t_a_site_a_cluster_can_answer_is_planned():
    """THE ACCEPTABLE FIXTURE. 3.00 A on a 0.40 mm barrel needs four, which is a cluster beside the pad."""
    r = _row(3.0)
    pts, axis, note = rb.plan(r, [])
    assert len(pts) == 4, (len(pts), note)


def t_a_site_that_needs_more_barrels_than_a_cluster_holds_is_declined():
    """THE DEFECTIVE FIXTURE, and it is board P's own: CELL4 crosses at ONE 0.50 mm barrel carrying 18.00 A.

    A 0.50 mm barrel holds 1.05 A, so the arithmetic asks for eighteen, and eighteen barrels in a row beside a
    pad is a busbar and a different pad. The tool must REFUSE to draw it and say so, because a fixer that
    answers any number turns a measured refusal into copper nobody chose."""
    r = _row(18.0, drill=0.5)
    assert r["need"] > rb.MAX_BARRELS, r["need"]
    pts, axis, note = rb.plan(r, [])
    assert pts == [], pts
    assert "busbar" in note and "placement item" in note, note


def t_the_cap_is_a_number_a_caller_can_move_and_not_a_silence():
    """The same site with the cap raised is planned, so the refusal is the CAP's and not a failure to try."""
    r = _row(18.0, drill=0.5)
    pts, axis, note = rb.plan(r, [], max_barrels=32)
    assert len(pts) == r["need"] == 18, (len(pts), r["need"])


def t_the_barrels_are_centred_on_the_site_so_the_one_there_keeps_its_copper():
    """A site with a barrel already on it is the normal case: the fanout's own via. Centre on it."""
    r = _row(3.0, at=(10.0, 20.0))
    pts, axis, note = rb.plan(r, [])
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    assert abs(cx - 10.0) < 1e-9 and abs(cy - 20.0) < 1e-9, (cx, cy)


def t_the_pitch_keeps_this_project_s_hole_to_hole_floor():
    """Board E's block vias went to 0.10 mm hole to hole on 18 September and the placed board came back with
    eight hole_to_hole violations. The plan may never produce that, at any drill this project uses."""
    for drill in (0.2, 0.25, 0.3, 0.4, 0.5, 0.7):
        r = _row(6.0, drill=drill)
        pts, axis, note = rb.plan(r, [], max_barrels=64)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                assert d - drill >= rb.FLOOR - 1e-9, (drill, d, d - drill)


def t_the_axis_chosen_is_the_one_that_keeps_furthest_from_another_net_s_pad():
    """A neighbour due east must push the cluster onto y, and a neighbour due north onto x."""
    r = _row(3.0)
    pts, axis, _ = rb.plan(r, [(10.9, 10.0)])
    assert axis == "y", (axis, pts)
    pts, axis, _ = rb.plan(r, [(10.0, 10.9)])
    assert axis == "x", (axis, pts)


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
    assert "GetDrill()" not in SRC, "rail_barrels walks the vias itself instead of asking the judge"


def t_it_does_not_carry_its_own_copy_of_the_drc_helpers():
    """`return_gaps.py` quietly stopped agreeing with its own gate on 17 September. One answer to 'what does
    the DRC say about this board', and it is via_parallel's."""
    assert "_vp._measure(" in SRC and "_vp._hit_positions(" in SRC
    assert "\ndef _measure(" not in SRC and "\ndef _hit_positions(" not in SRC
    assert "drc.sh" not in SRC, "rail_barrels shells out to the DRC itself"


def t_it_reports_before_it_lays():
    """A dry run is the default: `--apply` is what puts copper on a board."""
    assert 'apply_ = "--apply" in argv' in SRC
    i = SRC.find('if not apply_:')
    j = SRC.find('pcbnew.SaveBoard')
    assert 0 < i < j, "the dry-run return does not come before the first save"


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
