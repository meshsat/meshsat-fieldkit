#!/usr/bin/env python3
"""The keep-out the router can see (rule ANA-001, MESHSAT-862, 16 September 2026).

Board A declares nineteen sensitive nodes with the distance each wants from switching copper and six are routed
between 0.18 and 0.36 mm from a switch node. The net class clearance is the only instrument the router honours
and it applies between every pair of nets on the board, which is the wrong shape for a rule about one kind of
neighbour. These are the properties that keep the band from costing connections; the board fixtures need KiCad
and run in the route itself."""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
SRC = open(os.path.join(TOOLS, "sensitive_guard.py"), encoding="utf-8").read()
ROUTE = open(os.path.join(TOOLS, "route_one.sh"), encoding="utf-8").read()


def t_the_band_is_drawn_on_the_copy_and_never_on_the_board():
    """It reaches the ROUTER through the DSN. The real board's DRC and every fabrication output are untouched,
    which is what makes a router-only constraint safe to add at all."""
    i = ROUTE.index("sensitive_guard.py")
    w = ROUTE[max(0, i - 900):i + 400]
    assert "-noplanes.kicad_pcb" in w, "the guard is not run on the temporary export board"
    assert "SENSITIVE_GUARD" in w, "there is no way to turn it off"
    assert "sensitive_guard.py\" \"$W/$N-noplanes.kicad_pcb\"" in ROUTE, \
        "the guard is handed something other than the temporary board"


def t_the_band_does_not_cover_the_net_it_protects():
    """An annulus: the net's own copper grown by the board clearance is subtracted, or the router cannot
    finish the very net the band exists for."""
    assert "band.BooleanSubtract(own)" in SRC, "the band swallows its own net's copper"


def t_a_foreign_pad_is_punched_out_of_the_band():
    """A pad inside a track keep-out is an escape that can no longer be made. The PA head keep-out of
    15 September cost exactly that and was reverted."""
    assert "band.BooleanSubtract(hole)" in SRC, "a foreign pad inside the band is not punched out"
    assert 'p.GetNetname().lstrip("/") == nm: continue' in SRC, "the net's own pads are punched out too"


def t_a_net_with_no_copper_gets_no_band():
    """A band around nothing is a band around the whole board."""
    assert "nothing to draw a band around" in SRC, "a net with no copper is not reported"
    assert "if not segs:" in SRC, "the empty case is not handled"


def t_the_points_go_into_the_zones_own_outline():
    """SetOutline() takes ownership of a Python-owned polygon and the board frees it twice: the first version
    segfaulted at the save, after printing every band it had computed. Appending into the zone's own outline
    is the shape that does not."""
    assert "z.SetOutline(" not in SRC, "the zone is handed a polygon it will free"
    assert "o = z.Outline(); o.RemoveAllContours()" in SRC, "the points are not appended into the zone's own outline"
    assert "o.NewHole(i)" in SRC, "the punched pads are lost when the band is copied into the zone"
