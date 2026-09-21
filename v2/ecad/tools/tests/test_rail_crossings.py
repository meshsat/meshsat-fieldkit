#!/usr/bin/env python3
"""The barrels a declared rail's own crossing needs, asked before the route (rule PI-003's second report).

MESHSAT-862, 18 September 2026. `via_current` judges PI-003 on the SOLVED mesh and needs a routed board;
`rail_crossings.judge` asks the arithmetic half on the finished placement, where a generator can still answer
it for free. Two things in it cost a version each and both are rules here: a part's current is SPLIT across the
pads it takes it on (with the whole current at every pad board B reads 102 short crossings of 103 instead of
six, which is the attribution error of 16 September repeated), and a rail's `source` may be a LIST, which the
first version used as a dictionary key.

The board is a fake of nine methods rather than a KiCad file, so these rules run on the runner as well as on
the box: the judge touches method names only and never a pcbnew constant. `test_pair_router_imports` exists
because a rule that can only run where KiCad is leaves the runner's suite green while the tool is broken."""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import rail_crossings as rc
import via_current as vc

MM = 1000000


class _P:
    def __init__(s, x, y): s.x, s.y = int(x * MM), int(y * MM)


class _BB:
    def __init__(s, w, h): s._w, s._h = int(w * MM), int(h * MM)
    def GetWidth(s): return s._w
    def GetHeight(s): return s._h


class _Via:
    def __init__(s, net, x, y, drill, width=None):
        s._n, s._p, s._d = net, _P(x, y), int(drill * MM)
        s._w = int((width if width is not None else drill + 0.4) * MM)
    def GetClass(s): return "PCB_VIA"
    def GetNetname(s): return s._n
    def GetPosition(s): return s._p
    def GetDrill(s): return s._d
    def GetWidth(s): return s._w        # the ring `rail_barrels` must reuse, never invent


class _Pad:
    def __init__(s, net, num, x, y, w=1.0, h=1.0): s._n, s._num, s._p, s._b = net, num, _P(x, y), _BB(w, h)
    def GetNetname(s): return s._n
    def GetNumber(s): return s._num
    def GetPosition(s): return s._p
    def GetBoundingBox(s): return s._b


class _FP:
    def __init__(s, ref, pads): s._r, s._pads = ref, pads
    def GetReference(s): return s._r
    def Pads(s): return s._pads


class _Trk:
    """A track piece of `net` on copper layer `layer` (a KiCad layer id): the fake's one non-via track."""
    def __init__(s, net, layer): s._n, s._l = net, layer
    def GetClass(s): return "PCB_TRACK"
    def GetNetname(s): return s._n
    def GetLayer(s): return s._l


class _Zone:
    def __init__(s, net, layer, rule_area=False): s._n, s._l, s._r = net, layer, rule_area
    def GetNetname(s): return s._n
    def GetFirstLayer(s): return s._l
    def GetIsRuleArea(s): return s._r


class _PTHPad(_Pad):
    """A plated component hole: copper on every layer of the board by construction."""
    def GetDrillSizeX(s): return int(0.8 * MM)


class _Board:
    def __init__(s, vias, fps, zones=()): s._v, s._f, s._z = vias, fps, list(zones)
    def GetTracks(s): return s._v
    def GetFootprints(s): return s._f
    def Zones(s): return s._z


def _one_pad_source(barrels, drill=0.4, amps=3.0):
    """A rail whose source part takes the whole current on ONE pad, with `barrels` vias standing on it."""
    pads = [_Pad("/RAIL", "1", 10.0, 10.0)]
    vias = [_Via("/RAIL", 10.0 + 0.1 * i, 10.0, drill) for i in range(barrels)]
    return _Board(vias, [_FP("U1", pads)]), {"/RAIL": {"amps_peak": amps, "source": "U1"}}


def t_a_crossing_with_fewer_barrels_than_its_current_needs_is_named():
    """THE DEFECTIVE FIXTURE. 3.00 A through one 0.40 mm barrel: the barrel holds 0.90 A, so it needs four."""
    b, rails = _one_pad_source(1)
    short, judged = rc.judge(b, rails)
    assert judged == 1, judged
    assert len(short) == 1, short
    assert "needs 4" in short[0], short[0]


def t_a_crossing_with_the_barrels_its_current_needs_is_not_named():
    """THE ACCEPTABLE FIXTURE, the same rail with the copper it asks for: four barrels, nothing reported."""
    b, rails = _one_pad_source(4)
    short, judged = rc.judge(b, rails)
    assert judged == 1 and short == [], (judged, short)


def t_a_part_s_current_is_split_across_the_pads_it_takes_it_on():
    """The attribution rule, and the number the other reading would give is computed here rather than asserted.

    A part that takes 3.00 A on four pads carries about 0.75 A at each, which one 0.40 mm barrel holds. Divide
    the rail's WHOLE current by the barrels at each pad instead and every one of the four reads short, which is
    board B's 102 of 103 and board A's 29 of 31 in the hand-over report of 16 September."""
    pads = [_Pad("/RAIL", str(i + 1), 10.0 + 3.0 * i, 10.0) for i in range(4)]
    vias = [_Via("/RAIL", 10.0 + 3.0 * i, 10.0, 0.4) for i in range(4)]
    b = _Board(vias, [_FP("U1", pads)])
    short, judged = rc.judge(b, {"/RAIL": {"amps_peak": 3.0, "loads": {"U1": 3.0}}})
    assert judged == 4, judged
    assert short == [], short
    assert vc.barrels_for(3.0 / 4, 0.4) == 1 and vc.barrels_for(3.0, 0.4) == 4, "the two readings must differ"


def t_a_rail_whose_source_is_several_references_is_not_used_as_a_key():
    """Board B's slot rails are fed from more than one place and the intent carries a LIST. The first version
    wrote `want[r["source"]]` and raised `unhashable type: 'list'` on the first board that has one, which is
    the 13 September lesson about a list used as a dictionary key, in a second tool."""
    b, rails = _one_pad_source(1)
    rails["/RAIL"]["source"] = ["U1", "U2"]
    short, judged = rc.judge(b, rails)
    assert judged == 1 and len(short) == 1, (judged, short)


def t_a_pad_with_no_crossing_is_not_a_failure():
    """A rail that does not change layer at a pad has nothing for this rule to count: absence is not a short
    barrel, it is a pad the route may never via at all, and `via_current` is what answers that afterwards."""
    b, rails = _one_pad_source(0)
    short, judged = rc.judge(b, rails)
    assert judged == 0 and short == [], (judged, short)


def t_it_lays_nothing():
    """Where to put more copper is a placement question whose shape differs per board, so this tool reports and
    the generator answers. A report that edits the board would be a second, silent placement pass."""
    src = open(os.path.join(os.path.dirname(HERE), "rail_crossings.py"), encoding="utf-8").read()
    for forbidden in ("b.Add(", "SaveBoard", "SetLocked", "PCB_VIA("):
        assert forbidden not in src, "rail_crossings changes the board: %s" % forbidden


def t_the_count_comes_from_the_rule_that_judges_it_after_the_route():
    """The pre-route report and the post-route verdict must not be two different arithmetics, or a board can
    pass one and fail the other on the same copper."""
    src = open(os.path.join(os.path.dirname(HERE), "rail_crossings.py"), encoding="utf-8").read()
    assert "import via_current as _vc" in src and "_vc.barrels_for(" in src, src[:200]


def t_kicad_is_imported_where_the_judge_cannot_see_it():
    """So these rules run on the runner. A module-level `import pcbnew` would make the whole file skip there."""
    src = open(os.path.join(os.path.dirname(HERE), "rail_crossings.py"), encoding="utf-8").read()
    assert "\nimport pcbnew" not in src, "rail_crossings imports KiCad at module scope; the judge's rules skip"
    assert "    import pcbnew" in src, "main must import KiCad for itself"


def t_it_is_declared_in_the_coverage_map_as_this_rule_s_report():
    """A tool a chain runs on every board is declared beside the rule it reports for, or nobody reading the
    rule knows it exists. `barrel_sites.py` is the report from the solved board; this one is from the placed."""
    cov = open(os.path.join(os.path.dirname(HERE), "pcb_rules_coverage.yaml"), encoding="utf-8").read()
    assert "rail_crossings.py" in cov, "rail_crossings.py is in full.sh and in no coverage entry"


def t_the_row_carries_the_ring_already_on_the_site():
    """A barrel added beside one that is there must be the SAME via. Board A declares a 0.20 mm annular floor
    and `rail_barrels`'s first version chose a 0.70 mm ring on a 0.40 mm drill, which is 0.15: the DRC refused
    all seven of board A's sites and the tool laid nothing. The ring is the site's own, so the judge carries
    it."""
    b, rails = _one_pad_source(1, drill=0.4, amps=3.0)
    rows, judged = rc.rows(b, rails)
    assert len(rows) == 1, rows
    assert abs(rows[0]["width"] - 0.8) < 1e-9, rows[0]["width"]


def t_the_window_does_not_grow_with_the_count_it_asks_for():
    """A version of this walk grew its window by (need - 1) * pitch / 2 so that it could count the cluster a
    fixer would lay. It was measured on the same three board files with nothing but the judge changed and it
    LOOSENED the question: board A read 5 short where it read 8, board B 3 where it read 5, board E 2 where it
    read 4. A window that wide does not count the answer, it counts the NEIGHBOURHOOD, sweeping up every
    fanout via of the same rail that happens to be near and is not at this crossing. The window is the pad
    plus `reach_mm`, and the FIXER is told what it is: a cluster that does not fit is a placement item."""
    pads = [_Pad("/RAIL", "1", 10.0, 10.0, 0.6, 0.6)]
    vias = [_Via("/RAIL", 10.0 + 0.9 * k, 10.0, 0.5) for k in (-2, -1, 0, 1, 2)]
    b = _Board(vias, [_FP("U1", pads)])
    short, judged = rc.judge(b, {"/RAIL": {"amps_peak": 5.0, "source": "U1"}})
    assert judged == 1 and len(short) == 1, (judged, short)
    assert "3 barrel(s)" in short[0], ("the two barrels 1.8 mm out were counted", short[0])


def t_the_row_carries_the_window_the_fixer_must_fit_inside():
    """The fixer places barrels the judge will count, or none: `reach` and the pad centre travel in the row so
    the two cannot disagree about where the window is."""
    b, rails = _one_pad_source(1, drill=0.4, amps=3.0)
    rows, judged = rc.rows(b, rails)
    assert rows and "reach" in rows[0] and "at_pad" in rows[0], rows[0].keys()
    assert rows[0]["reach"] > 0


def t_the_window_never_shrinks_below_the_one_it_started_with():
    """The wider window is taken only when it finds MORE, so a site whose cluster is not there reads exactly
    as it did: this is a widening for counting an answer, never a loosening of the question."""
    pads = [_Pad("/RAIL", "1", 10.0, 10.0, 0.6, 0.6)]
    vias = [_Via("/RAIL", 10.0, 10.0, 0.5)]
    b = _Board(vias, [_FP("U1", pads)])
    short, judged = rc.judge(b, {"/RAIL": {"amps_peak": 5.0, "source": "U1"}})
    assert judged == 1 and len(short) == 1, (judged, short)
    assert "1 barrel(s)" in short[0] and "needs 5" in short[0], short[0]


def t_a_pre_route_barrel_tool_says_when_it_is_given_the_placed_snapshot():
    """THE DEFECTIVE FIXTURE, and it is an artefact question rather than a copper one (20 September 2026).

    full.sh copies out/<N>-placed.kicad_pcb at line 170 and takes the PREROUTE_STOP_AFTER_PLACE exit at 212,
    while rail_barrels --apply, the stage that fills a short crossing, runs at 309. A shortfall read off that
    snapshot is one the chain fills forty lines later, and it cost a wrong sentence about board D. Both tools
    deliberately ACCEPT a snapshot, so the answer is not a refusal: the tool says which board it was given."""
    import io, contextlib, os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import via_current as vc
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        said = vc.placed_snapshot_note("rail_crossings", "/tmp/nowhere/pcb-d-aprs-placed.kicad_pcb")
    out = buf.getvalue()
    assert said is True, "the note did not fire on a -placed board"
    assert "PLACED SNAPSHOT" in out and "rail_barrels --apply" in out, out


def t_the_same_tool_says_nothing_about_a_board_the_chain_really_makes():
    """THE ACCEPTABLE FIXTURE: the note must not become noise on every run. The chain reads rail_crossings on
    the project's own board, and that board carries the barrels the stage laid."""
    import io, contextlib, os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import via_current as vc
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        said = vc.placed_snapshot_note("rail_crossings", "/tmp/nowhere/pcb-d-aprs.kicad_pcb")
    assert said is False and buf.getvalue() == "", buf.getvalue()


def t_both_pre_route_barrel_tools_ask_it():
    """A rule about the CALLERS, parsed rather than grepped: a note only one of the two tools carries is a
    note the next hand probe walks past."""
    import ast, os
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in ("rail_crossings.py", "rail_barrels.py"):
        src = open(os.path.join(here, f), encoding="utf-8").read()
        calls = [n for n in ast.walk(ast.parse(src))
                 if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "placed_snapshot_note"]
        assert calls, "%s never asks whether it was given the placed snapshot" % f


def t_a_site_of_mixed_drills_is_judged_on_what_its_barrels_carry():
    """THE DEFECT OF 21 SEPTEMBER 2026: board E's VIN_RAW at L2 pad 2 holds the generator's ten 0.50 mm barrels
    (10.5 A together) and one 0.25 mm fanout via, and the judge took the smallest hole as the site's drill and
    asked for sixteen of them for 10 A, a false busbar declined as a placement item for a day. The site carries
    its current and is not short; the same eleven barrels all at 0.25 mm are."""
    pads = [_Pad("/RAIL", "1", 10.0, 10.0)]
    vias = [_Via("/RAIL", 10.0 + 0.1 * i, 10.0, 0.5) for i in range(10)] + [_Via("/RAIL", 11.2, 10.0, 0.25)]
    b = _Board(vias, [_FP("U1", pads)]); rails = {"/RAIL": {"amps_peak": 10.0, "source": "U1"}}
    short, judged = rc.judge(b, rails)
    assert judged == 1 and short == [], "ten 0.50 mm barrels and a 0.25 mm one carry 10 A and were called short: %s" % short
    small = [_Via("/RAIL", 10.0 + 0.1 * i, 10.0, 0.25) for i in range(11)]
    short2, _ = rc.judge(_Board(small, [_FP("U1", pads)]), rails)
    assert len(short2) == 1 and "11 barrel(s) carrying" in short2[0] and "at 0.25 mm" in short2[0], short2


def t_a_new_barrel_takes_the_largest_drill_already_on_the_site():
    """The fixer copies a barrel of the site; it must copy the generator's 0.50 and never the fanout's 0.25."""
    pads = [_Pad("/RAIL", "1", 10.0, 10.0)]
    vias = [_Via("/RAIL", 10.0, 10.0, 0.5), _Via("/RAIL", 10.6, 10.0, 0.25)]
    rows, _ = rc.rows(_Board(vias, [_FP("U1", pads)]), {"/RAIL": {"amps_peak": 6.0, "source": "U1"}})
    assert rows and abs(rows[0]["drill"] - 0.5) < 1e-9, "the drill for new barrels is not the largest on the site: %s" % rows
    assert rows[0]["carried"] > 1.0 and rows[0]["need"] > rows[0]["have"], rows[0]


def t_pads_of_one_number_are_one_land_and_one_crossing():
    """THE DEFECTIVE FIXTURE (21 September 2026, board E): KiCad draws a PowerPAK SO-8's drain as five pads numbered
    5, the tab and four leads joined inside the part. The judge took each as a pad of its own, split Q7's 8.00 A
    five ways and read four crossings of 1.60 A at leads 1.27 mm apart, two of which stayed short by 0.12 A after
    the fixer had answered the other two, while the tab carrying the whole current was never asked for 8 A."""
    # U1 takes 3.0 A on pad "5" drawn as three pieces 3 mm apart, one 0.40 mm barrel on each piece
    pads = [_Pad("/RAIL", "5", 10.0, 10.0 + 3.0 * i, 0.6, 0.6) for i in range(3)]
    vias = [_Via("/RAIL", 10.0, 10.0 + 3.0 * i, 0.4) for i in range(3)]
    rails = {"/RAIL": {"amps_peak": 3.0, "source": "U1"}}
    short, judged = rc.rows(_Board(vias, [_FP("U1", pads)]), rails)
    assert judged == 1 and len(short) == 1, (judged, [r["why"] for r in short])
    r = short[0]
    assert r["pad"] == "5" and r["pads"] == 1 and r["instances"] == 3, r
    assert r["have"] == 3, "the barrels of every piece of the land count once each: %s" % r["have"]
    assert abs(r["amps"] - 3.0) < 1e-9 and r["need"] == 4, (r["amps"], r["need"])   # three 0.40 barrels carry 2.7 A
    assert "pad 5 drawn as 3 pieces of one land" in r["why"], r["why"]
    # THE ACCEPTABLE FIXTURE: three DISTINCT numbers are three lands and three crossings of a third each
    pads = [_Pad("/RAIL", str(i + 1), 10.0, 10.0 + 3.0 * i, 0.6, 0.6) for i in range(3)]
    short, judged = rc.rows(_Board(vias, [_FP("U1", pads)]), rails)
    assert judged == 3 and len(short) == 3, (judged, len(short))
    assert all(abs(r["amps"] - 1.0) < 1e-9 and r["have"] == 1 and r["instances"] == 1 for r in short), short
    assert not any("pieces of one land" in r["why"] for r in short)


def t_a_net_on_one_layer_at_generation_is_named_because_its_crossing_is_the_routers_to_make():
    """THE DEFECTIVE FIXTURE (21 September 2026, appendix 32.346 addendum 02:45): board E's HS_S and board A's six
    FET drain tabs lie on F.Cu alone before the route (no zone, no band, no plated hole), so the barrel the judge
    counted at each tab is the FANOUT's own via reaching bare laminate, and the crossing it asks barrels for
    exists only if the ROUTER makes one. `via_current` already declines such a site on the solved mesh
    (`crosses_layers`); this judge never asked. The row says so and the line says so; the count is not changed."""
    F_CU, IN2_CU = 0, 2
    pads = [_Pad("/RAIL", "5", 10.0, 10.0, 0.6, 0.6)]
    vias = [_Via("/RAIL", 10.0, 10.0, 0.25)]
    rails = {"/RAIL": {"amps_peak": 3.0, "source": "U1"}}
    tracks = [_Trk("/RAIL", F_CU), _Trk("/RAIL", F_CU)]
    short, judged = rc.rows(_Board(vias + tracks, [_FP("U1", pads)]), rails)
    assert judged == 1 and len(short) == 1, (judged, short)
    r = short[0]
    assert r["one_layer"] is True, r
    assert "the net lies on one layer at generation" in r["why"], r["why"]
    assert r["need"] > r["have"], "the count is deliberately unchanged tonight: %s" % r
    # THE ACCEPTABLE FIXTURES: a zone on a second layer, or a plated hole, is copper the net changes layer to
    short, judged = rc.rows(_Board(vias + tracks, [_FP("U1", pads)], zones=[_Zone("/RAIL", IN2_CU)]), rails)
    assert short[0]["one_layer"] is False and "one layer at generation" not in short[0]["why"], short[0]
    short, judged = rc.rows(_Board(vias + tracks, [_FP("U1", pads + [_PTHPad("/RAIL", "9", 20.0, 10.0)])]), rails)
    assert short[0]["one_layer"] is False, short[0]
    # a zone and a track on the SAME layer are still one layer (the first version keyed a zone as a tuple)
    short, judged = rc.rows(_Board(vias + tracks, [_FP("U1", pads)], zones=[_Zone("/RAIL", F_CU)]), rails)
    assert short[0]["one_layer"] is True, short[0]
    # a rule area of the net's name is not copper
    short, judged = rc.rows(_Board(vias + tracks, [_FP("U1", pads)], zones=[_Zone("/RAIL", IN2_CU, rule_area=True)]), rails)
    assert short[0]["one_layer"] is True, short[0]

