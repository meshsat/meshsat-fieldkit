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
    """16 September 2026: the same argument, with GROUND taken out of it. Board A's `VBUS20 F.Cu` island fills
    44 percent because the front end's gate drives and sense lines cross it, and the rail's second layer,
    `VBUS20 under In3.Cu`, fills 98 percent behind the keep-out that field does allow. A power rail with
    continuous copper on another layer is the ground case word for word; what must not change is that the
    exemption REQUIRES such a pour."""
    i = SRC.find("_cover_ok = area >= MIN_COVER * rect")
    assert i > 0, "the coverage test is no longer a named condition"
    blk = SRC[i:i + 2500]
    assert "if solid_gnd and not _cover_ok" in blk, "the ground exemption has gone"
    assert "if _solid_other and not solid_gnd and not _cover_ok" in blk, \
        "the exemption does not require a solid pour of the same net elsewhere"
    j = SRC.find("_solid_other = any(")
    cond = SRC[j:j + 260]
    assert "o.GetNetname() == z.GetNetname()" in cond and "o.GetFirstLayer() != L" in cond \
        and "0.8 * outline_area(o)" in cond, "the other pour is not required to be the same net, elsewhere, and solid"


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
    blk = SRC[i:i + 3000]
    assert "check(loose == 0 and _cover_ok" in blk, "the coverage no longer decides at all"


def t_only_the_coverage_bar_is_exempted_never_the_loose_pieces():
    """A floating piece of a power net is a defect whatever another layer does, so the generalisation touches
    the coverage number and nothing else."""
    i = SRC.index("_solid_other = any(")
    j = SRC.index("check(loose == 0 and _cover_ok", i)
    assert "_cover_ok = True" in SRC[i:j], "the exemption does not reach the coverage bar"
    assert "loose = 0" not in SRC[i:j], "the exemption silently forgives loose pieces too"
