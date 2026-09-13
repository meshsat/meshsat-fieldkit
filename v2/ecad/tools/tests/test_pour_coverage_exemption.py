#!/usr/bin/env python3
"""A supplementary ground pour on a routing layer is not judged by its coverage (MESHSAT-862, 13 Sept 2026).

`copper_checks` refuses a pour that fills less than half its own outline, because a pour the router's tracks
have eaten to slivers carries nothing. That is true when the pour IS the return path. C11's GND pour on In2, a
ROUTING layer, fills 17,270 of 34,895 mm2 of the board (49.5 percent) while In1 beside it is a SOLID ground
plane at 99 percent, and the board was refused for half a percent of a heuristic.

The exemption is exactly the one the loose-piece check already makes two lines above, and it is narrow on
purpose: GND only, only when a pour of the same net on ANOTHER layer fills at least 80 percent of its own
outline, and the number is printed either way. A board with no such plane is judged as before.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "copper_checks.py")).read()


def t_the_exemption_needs_a_solid_plane_of_the_same_net_on_another_layer():
    i = SRC.find("_cover_ok = area >= MIN_COVER * rect")
    assert i > 0, "the coverage test is no longer a named condition"
    blk = SRC[i:i + 700]
    assert "if solid_gnd and not _cover_ok" in blk, "the exemption does not require the solid plane"


def t_the_solid_plane_test_is_the_same_one_the_loose_piece_check_uses():
    i = SRC.find("solid_gnd = ")
    blk = SRC[i:i + 260]
    assert 'GetNetname() == "GND"' in blk, "the exemption is not restricted to ground"
    assert "GetFirstLayer() != L" in blk, "the plane may be on the same layer as the pour it excuses"
    assert "0.8 * outline_area" in blk, "the plane does not have to be solid"


def t_an_exempted_pour_still_prints_its_number():
    i = SRC.find("if solid_gnd and not _cover_ok")
    blk = SRC[i:i + 600]
    assert "NOTE pour" in blk and "%.0f%%" in blk, "the exemption hides the coverage instead of reporting it"


def t_a_pour_with_no_such_plane_is_still_refused():
    i = SRC.find("_cover_ok = area >= MIN_COVER * rect")
    blk = SRC[i:i + 900]
    assert "check(loose == 0 and _cover_ok" in blk, "the coverage no longer decides at all"
