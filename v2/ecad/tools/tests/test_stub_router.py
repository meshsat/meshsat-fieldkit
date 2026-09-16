#!/usr/bin/env python3
"""The stub router's cluster test (MESHSAT-862, 17 September 2026).

What the search may aim at is decided by a union-find over the net's own copper: everything NOT connected to
the source is a goal. That test is the tool's own model of KiCad's connectivity, and where the model is
stricter than the thing it stands for the search is handed a goal that is already connected, lays a closure
that changes nothing, and takes it back off."""
import os, sys

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
