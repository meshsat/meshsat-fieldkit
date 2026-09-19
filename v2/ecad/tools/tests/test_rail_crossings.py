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


class _Board:
    def __init__(s, vias, fps): s._v, s._f = vias, fps
    def GetTracks(s): return s._v
    def GetFootprints(s): return s._f


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
