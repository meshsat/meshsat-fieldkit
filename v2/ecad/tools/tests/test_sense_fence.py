#!/usr/bin/env python3
"""THE FENCE ANA-001 NEEDS AND WHAT IT MUST NOT DO (MESHSAT-862, 21 September 2026).

E36 is board E's best router board, hard 0 and six open, and its round-1 board fails ANA-001 by sixty-seven
micrometres: TRK_CSP runs 0.433 mm from TRK_SW1 where its declaration asks 0.50, over 7.68 mm, all of it
outside the courtyard of the part that carries both. Board E pins ALL SIX declared switching nets and the
sense pair at a half-millimetre floor, which is E23's configuration and E23 read PASS 3 of 3, so this is
neither the declaration nor the pre-lay: the pre-lay locks the copper IT lays, and the router then added
unlocked copper to a net that is already pinned.

A rule area that forbids tracks is the one instrument that reaches Freerouting (it leaves KiCad's DSN export
as `wire_keepout`), and the trap is in the shape: a fence drawn over the copper it protects is
`items_not_allowed`, which is in the hard set. The first version of this tool put 84 of them on board E.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip


def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _board(pcbnew, tmp, with_neighbour):
    """A sense run down the middle of an empty board, and, in the acceptable case, another net's track already
    inside the band the fence would claim."""
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, 30, 0), (30, 0, 30, 20), (30, 20, 0, 20), (0, 20, 0, 0)):
        sh = pcbnew.PCB_SHAPE(b); sh.SetShape(pcbnew.SHAPE_T_SEGMENT); sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        sh.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2))); sh.SetWidth(pcbnew.FromMM(0.1)); b.Add(sh)
    for n in ("/SENSE", "/SW"):
        b.Add(pcbnew.NETINFO_ITEM(b, n))
    b.BuildListOfNets()
    def _track(net, x1, y1, x2, y2):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        t.SetWidth(pcbnew.FromMM(0.25)); t.SetLayer(pcbnew.F_Cu); t.SetNet(b.FindNet(net)); b.Add(t); return t
    _track("/SENSE", 5, 10, 25, 10)
    if with_neighbour: _track("/SW", 5, 10.4, 25, 10.4)   # 0.15 mm of copper gap: already inside the 0.5 mm band
    path = os.path.join(tmp, "fence.kicad_pcb"); pcbnew.SaveBoard(path, b); return path


def _run(path, apply_=False):
    import subprocess
    a = [sys.executable, os.path.join(TOOLS, "sense_fence.py"), path, "--board", "x", "--net", "SENSE:0.5",
         "--layers", "F.Cu"]
    if apply_: a.append("--apply")
    return subprocess.run(a, capture_output=True, text=True).stdout


def t_the_fence_is_drawn_beside_the_sense_run_and_never_over_any_copper():
    """THE DEFECTIVE FIXTURE, which is a board with room for the router to do the wrong thing: a 20 mm sense
    run with nothing beside it. The fence must exist, carry area, and cover NO existing copper, because a rule
    area that forbids tracks and sits on one is `items_not_allowed` and that type is in the hard set."""
    p = _pcbnew()
    with tempfile.TemporaryDirectory() as tmp:
        path = _board(p, tmp, with_neighbour=False)
        out = _run(path, apply_=True)
        assert "mm2 of fence at 0.50 mm" in out, out[-600:]
        assert "rule area(s) added" in out, out[-600:]
        b = p.LoadBoard(path)
        zones = [z for z in b.Zones() if z.GetIsRuleArea()]
        assert zones, "no rule area on the saved board: %s" % out[-400:]
        assert all(z.GetDoNotAllowTracks() for z in zones), "a fence that permits tracks is not a fence"
        # CONTAINS, never Collide: `Collide(point, r)` on a zone's SHAPE_POLY_SET answers about the OUTLINE
        # and says no for a point in the middle of the area, so the first version of this assertion passed on
        # the defective tool as happily as on the fixed one (21 September 2026, the same lesson the In3
        # corridor probe learnt this morning: a bounding box, or here a boundary, is not the region).
        for z in zones:
            o = z.Outline()
            for t in b.GetTracks():
                s_, e_ = t.GetStart(), t.GetEnd()
                for q in (s_, e_, p.VECTOR2I((s_.x + e_.x) // 2, (s_.y + e_.y) // 2)):
                    assert not o.Contains(q), \
                        "the fence covers copper that is already there, which is items_not_allowed: %s" % t.GetNetname()


def t_a_band_that_is_already_full_is_not_fenced():
    """THE ACCEPTABLE FIXTURE. Another net's track already runs 0.15 mm from the sense run, which is closer
    than the declaration asks and is the failure `sensitive_nodes` exists to report. The fence must not claim
    that ground: it is drawn where the router could still make things worse, never over a violation it cannot
    fix, and never over the copper that makes it. The area beside the neighbour is smaller than the open
    board's for that reason."""
    p = _pcbnew()
    with tempfile.TemporaryDirectory() as tmp:
        open_ = _run(_board(p, tmp, with_neighbour=False))
        full = _run(_board(p, tmp + "/x" if False else tempfile.mkdtemp(), with_neighbour=True))
        def _area(s):
            import re
            m = re.search(r"([0-9.]+) mm2 of fence", s); return float(m.group(1)) if m else -1.0
        assert _area(open_) > 0, open_[-400:]
        assert _area(full) >= 0, full[-400:]
        assert _area(full) < _area(open_), \
            "the fence did not shrink where copper already stands in the band: %.2f against %.2f" % (_area(full), _area(open_))
