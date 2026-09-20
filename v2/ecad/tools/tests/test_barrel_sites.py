#!/usr/bin/env python3
"""What a barrel over its rating is offered as, and what it is refused as (MESHSAT-862, 20 September 2026).

`barrel_sites --suggest` prints the `power_copper.cluster` line each over-rated layer transition would take,
and a person pastes it into a generator. Board E cost three chain runs to find the two things it was not
saying: a site whose barrel is a connector's plated COMPONENT HOLE is not a via transition at all, and the
room it reports was measured to the nearest pad's CENTRE rather than to its copper. Both are here."""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))




def t_a_component_hole_is_not_a_barrel_and_is_declined():
    """A VIA CLUSTER ANSWERS A VIA TRANSITION (MESHSAT-862, 20 September 2026).

    `--suggest` takes its drill from the thing already at the site, and at four of board E's ten sites that
    thing is a connector's plated COMPONENT HOLE, 1.78 mm at the XT60 fuse holder F3 and the DC inlet F1.
    Suggested as a cluster and applied, E24 came back with eight `annular_width` at -0.4900 mm and sixteen
    `hole_to_hole` at 0.0000: a lattice of 1.78 mm vias beside a connector is not a thing, and those four
    were the whole of that hard set. Proved to fail on the tool as it stood, which printed a cluster line for
    all four."""
    src = open(os.path.join(TOOLS, "barrel_sites.py"), encoding="utf-8").read()
    assert "pad_here" in src, "the suggester cannot tell a via from a component hole"
    assert "COMPONENT HOLE" in src, "a component hole is not declined with its reason"
    i, j = src.find("_pad = next("), src.find("if any(x.get(\"locked_here\")")
    assert 0 < i < j, "the component-hole test runs after the locked-via test, so a pad site still gets a line"


def t_room_is_measured_to_the_pads_edge_and_says_it_is_a_model():
    """`DC_F` was reported with 1.34 mm of room while its lattice landed 0.1450 mm from a 3.30 by 2.50 land,
    because the distance was to the pad's CENTRE. It is to the rectangle now, with the barrel's own copper
    taken off, and the comment says plainly that a single row is walked so the number is an indication and
    the chain is the evidence."""
    src = open(os.path.join(TOOLS, "barrel_sites.py"), encoding="utf-8").read()
    # NOT A FIXED BYTE WINDOW. `test_prelay` and `test_stub_zone_obstacle` both broke on 18 September when a
    # comment pushed a literal past a slice, and a ratchet exists to stop the 87 rules that still search one
    # from becoming 88. The window here is the FUNCTION: from `def worst` to the next line at its own indent.
    i = src.find("def worst(ax):")
    assert i > 0, "the room function is gone"
    indent = len(src[:i].split("\n")[-1])
    rest = src[i:].split("\n")
    body_lines = [rest[0]]
    for ln in rest[1:]:
        if ln.strip() and len(ln) - len(ln.lstrip()) <= indent: break
        body_lines.append(ln)
    body = "\n".join(body_lines)
    assert "o[6] / 2.0" in body and "o[7] / 2.0" in body, "room is still measured to the pad centre"
    assert "STILL A MODEL" in body, "the estimate does not say it is one"
