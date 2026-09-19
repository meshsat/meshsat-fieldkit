#!/usr/bin/env python3
"""A track shorter than the process can draw (MESHSAT-862, 16 September 2026).

Board E11's re-finish came back hard 0 and unrouted 1, and the open connection was a GND track 0.0002 mm long,
two tenths of a micrometre, standing beside U13 pad 2. It is not a conductor and no fabricator draws it, but it
is a piece of the GND net that reaches nothing, so the board reads one connection short and the finish refuses
it. `cleanup_dangling.py` skips every net that owns a zone, which is right for its own job and is why this
class of artefact survives on exactly the nets most likely to carry it.

The fixtures build boards, so they skip where pcbnew is not importable; the admission rule below does not."""
import os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _board(pcbnew):
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, 40, 0), (40, 0, 40, 30), (40, 30, 0, 30), (0, 30, 0, 0)):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    return b


def _track(pcbnew, b, x1, y1, x2, y2, w=0.25):
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetWidth(pcbnew.FromMM(w)); t.SetLayer(pcbnew.F_Cu); b.Add(t); return t


def t_a_lone_dot_goes_and_a_real_track_stays():
    pcbnew = _pcbnew()
    import importlib
    dp = importlib.import_module("dot_prune")
    b = _board(pcbnew)
    _track(pcbnew, b, 10.0, 10.0, 20.0, 10.0)                 # a real track
    _track(pcbnew, b, 30.0, 20.0, 30.0002, 20.0)              # E11's dot, standing alone
    tmp = tempfile.mkdtemp(prefix="dot-prune-test-")
    p = os.path.join(tmp, "dots.kicad_pcb"); b.Save(p)
    rc = dp.main([p])
    b2 = pcbnew.LoadBoard(p)
    lens = sorted(round(((t.GetStart().x - t.GetEnd().x) ** 2 + (t.GetStart().y - t.GetEnd().y) ** 2) ** 0.5 / 1e6, 4)
                  for t in b2.GetTracks() if t.GetClass() == "PCB_TRACK")
    assert lens == [10.0], "the dot was not removed or the real track went with it: %s" % lens
    assert rc == 0, rc


def t_a_dot_that_really_bridges_two_tracks_is_kept():
    """A zero-length track still has a WIDTH, so it renders as a copper dot that can genuinely join two things
    that both reach it. **The two tracks have to be apart for that to mean anything**: this fixture used to
    give them a SHARED endpoint at (15, 10), so they were already one cluster and the dot joined nothing, and
    the rule passed on a board where removing the dot changes nothing at all (19 September 2026). They end
    0.3 mm apart now and the 0.4 mm wide dot between them is the only copper that spans the gap."""
    pcbnew = _pcbnew()
    import importlib
    dp = importlib.import_module("dot_prune")
    b = _board(pcbnew)
    net = pcbnew.NETINFO_ITEM(b, "BRIDGED"); b.Add(net)
    for t in (_track(pcbnew, b, 10.0, 10.0, 15.0, 10.0), _track(pcbnew, b, 15.3, 10.0, 20.0, 10.0),
              _track(pcbnew, b, 15.15, 10.0, 15.1501, 10.0)):
        t.SetNet(net)
    tmp = tempfile.mkdtemp(prefix="dot-bridge-test-")
    p = os.path.join(tmp, "bridge.kicad_pcb"); b.Save(p)
    dp.main([p])
    b2 = pcbnew.LoadBoard(p)
    n = sum(1 for t in b2.GetTracks() if t.GetClass() == "PCB_TRACK")
    assert n == 3, "the bridging dot was removed: %d track(s) left" % n


def t_a_dot_between_two_things_that_already_touch_is_not_a_bridge():
    """THE DEFECTIVE FIXTURE, and it is what board A carries 198 of (19 September 2026). The touch count says
    a dot reaching two items is a bridge, and it is only a bridge if those items are not already connected.
    One of board A's sits ON U15 pad 7, a micrometre from the pad's own centre, and KiCad's DRC then names
    EITHER the dot or the pad as that cluster's representative: three runs of the same closer on the same
    frozen board read three different boards and two different hard counts. Taking copper off can only break
    connectivity, never make it, so the honest test is to take the dot off ALONE and look."""
    pcbnew = _pcbnew()
    import importlib
    dp = importlib.import_module("dot_prune")
    b = _board(pcbnew)
    net = pcbnew.NETINFO_ITEM(b, "TOUCHING"); b.Add(net)
    for t in (_track(pcbnew, b, 10.0, 10.0, 15.0, 10.0), _track(pcbnew, b, 15.0, 10.0, 20.0, 10.0),
              _track(pcbnew, b, 15.0, 10.0, 15.0001, 10.0)):
        t.SetNet(net)
    tmp = tempfile.mkdtemp(prefix="dot-touching-test-")
    p = os.path.join(tmp, "touching.kicad_pcb"); b.Save(p)
    dp.main([p])
    b2 = pcbnew.LoadBoard(p)
    lens = sorted(round(((t.GetStart().x - t.GetEnd().x) ** 2 + (t.GetStart().y - t.GetEnd().y) ** 2) ** 0.5 / 1e6, 4)
                  for t in b2.GetTracks() if t.GetClass() == "PCB_TRACK")
    assert lens == [5.0, 5.0], ("the redundant dot survived: %s" % lens)


def t_the_finish_runs_it_under_a_guard():
    """Every pass that cuts copper on a board bound for manufacture is judged by the board, not by its author."""
    s = open(os.path.join(TOOLS, "finish.sh"), encoding="utf-8").read()
    assert "dot_prune.py" in s, "the finish does not run it"
    i = s.index("dot_prune.py")
    line = s[s.rindex("\n", 0, i) + 1:i]
    assert line.strip().startswith("guarded "), "dot_prune runs outside the finish's guard: %r" % line
