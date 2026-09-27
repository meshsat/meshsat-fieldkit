#!/usr/bin/env python3
"""The stub router's cluster test (MESHSAT-862, 17 September 2026).

What the search may aim at is decided by a union-find over the net's own copper: everything NOT connected to
the source is a goal. That test is the tool's own model of KiCad's connectivity, and where the model is
stricter than the thing it stands for the search is handed a goal that is already connected, lays a closure
that changes nothing, and takes it back off."""
import os, sys
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)


def t_a_track_end_on_another_tracks_body_is_one_cluster():
    """Board A's A37 finish, 17 September 2026. A closure was laid, both its ends measured 0.000 mm from the
    net's own copper, KiCad's unconnected count read 22 before and 22 after, and the piece came back off. The
    cluster test that decides what the search may aim at compared END POINTS only, so a T-junction split one
    KiCad cluster into two and the search was given a goal already connected to its source. A cluster test
    stricter than the connectivity it stands for invents work; the record carries the same lesson from the
    other side, where post_fix_b13 cut a T-junction foot off because it read ends only."""
    import os
    src = open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()
    i = src.index("def touches(")
    w = src[i:i + 2600]
    assert "PCB_TRACK" in w and "GetWidth()" in w, "the cluster test still compares end points only"
    assert "_u = max(0.0, min(1.0," in w, "there is no point-to-segment test"


def t_the_pieces_laid_since_are_found_by_uuid_and_never_as_the_last_n_of_the_track_list():
    """21 September 2026, board E's switching pre-lay. `BOARD.Add` puts a new track at the FRONT of the track
    list, so `list(b.GetTracks())[_n_before:]` named the OLDEST n tracks as a closure's own: a refused closure
    took old copper off and left its own pieces, and the drop-back dropped old copper, saw the same hard count,
    called the closures innocent and the stage's guard refused the whole group (seventeen closures lost twice
    for one item one closure owned). The pieces laid since are the tracks whose uuid was not there before."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stub_router.py"), encoding="utf-8").read()
    code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("#"))
    assert "GetTracks())[" not in code, "a track-list slice is still used as 'the pieces laid since'"
    assert "_before_ids = {t.m_Uuid.AsString() for t in b.GetTracks()}" in code, "the uuids before the emit are not recorded"
    assert code.count("_laid_since()") >= 2, "the refusal and the record do not both use the uuid window"


def t_kicads_board_add_puts_a_new_track_at_the_front_of_the_list():
    """THE API FACT, pinned where pcbnew is: the assumption the old slice rested on is false in KiCad 9."""
    try: import pcbnew
    except ImportError: raise Skip("pcbnew is not importable here")
    b = pcbnew.BOARD()
    for i in range(3):
        t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(i * 1000000, 0)); t.SetEnd(pcbnew.VECTOR2I(i * 1000000, 1000000)); b.Add(t)
    t = pcbnew.PCB_TRACK(b); t.SetStart(pcbnew.VECTOR2I(9000000, 0)); t.SetEnd(pcbnew.VECTOR2I(9000000, 1000000)); b.Add(t)
    L = list(b.GetTracks())
    assert L[0].m_Uuid.AsString() == t.m_Uuid.AsString(), "Add no longer prepends: the uuid window is still right, this pin is stale"
    assert L[-1].m_Uuid.AsString() != t.m_Uuid.AsString()

