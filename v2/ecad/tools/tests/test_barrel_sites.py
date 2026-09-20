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


def t_a_barrel_remembers_the_line_that_placed_it():
    """THE ANSWER TO A SITE THE GENERATOR OWNS IS "ADD POINTS TO THE CALL", SO NAME THE CALL (20 September
    2026). `barrel_sites --suggest` gave a coordinate, and board E has thirteen such sites whose calls take
    arguments that are expressions: finding each one is a hunt. Board A's generator grew its own frame walk
    for this on 19 September and it works there and nowhere else. `power_copper.stitch` records the first
    frame OUTSIDE power_copper.py for every barrel it places, so a helper like board A's `row`/`col` reports
    the generator's line and not its own, and `write_provenance` puts the map beside the board.

    Proved to fail on the tool as it stood: `PowerCopper` had no `placed_by` and `stitch` walked no frame."""
    src = open(os.path.join(TOOLS, "power_copper.py"), encoding="utf-8").read()
    assert "placed_by" in src and "_getframe" in src, "stitch does not record its caller"
    assert "def write_provenance" in src, "the map is never written beside the board"
    # the list is the CLASS's: a generator builds several PowerCopper objects in one run and the sidecar is
    # one file about one board, so a per-instance list would record whichever object the writer was called on
    i = src.index("class PowerCopper:")
    head = src[i:src.index("def __init__", i)]
    assert "placed_by" in head, "placed_by is per instance, so a run with two PowerCopper objects loses half"
    rd = open(os.path.join(TOOLS, "barrel_sites.py"), encoding="utf-8").read()
    assert "_placed_by_src" in rd, "the suggester cannot name the call"
    assert "SIDECAR AND NOT EVIDENCE" in rd, "the reader does not say the map judges nothing"


def t_a_locked_via_that_no_power_copper_call_placed_says_so():
    """A LOCKED VIA IS NOT ALWAYS THE GENERATOR'S BARREL (MESHSAT-862, 20 September 2026).

    `locked_here` asks only whether a LOCKED via sits at the site, and `escape.py` locks every escape stub's
    via while the pre-lay locks its own. Seven of board E's thirteen such sites have no entry in the barrel
    provenance at all, so "add N points to the call that placed it" was advice about a call that does not
    exist. With the map beside the board the two can be told apart, and where the site is not in it the
    answer is the fanout's via count at that pad, which is a different edit.

    Proved to fail on the tool as it stood: it printed the same sentence for every locked site."""
    src = open(os.path.join(TOOLS, "barrel_sites.py"), encoding="utf-8").read()
    assert "NO POWER-COPPER CALL" in src, "every locked site still gets the same advice"
    assert "_prov_seen" in src, "the reader cannot say whether the map was there to be checked"
    i = src.index("NO POWER-COPPER CALL")
    j = src.index("_placed_by_src(path")
    assert j < i, "the site is declared unplaced before the map is consulted"


def t_the_solved_currents_must_be_this_boards_and_say_so_when_they_are_not():
    """A SOLVED FILE NAMES ITS BOARD BY SHA (MESHSAT-862, 20 September 2026).

    `<stem>-via-currents.json` named its board by FILENAME, and every phase of a board carries the same one.
    Board E's currents solved on E17 were read beside E29's board, which carries five clusters E17 does not,
    and every "add N point(s)" that came back was about neither: the classification was sound and the counts
    were the old board's current at the new board's via. That is 17 September's rule, a verdict names the
    board it was taken on, owed by the DATA FILE that feeds PI-003 just as much as by a verdict, and it is
    the third reading taken off the wrong artefact today.

    Proved to fail on the tools as they stood: `dc_drop` wrote no sha and `barrel_sites` compared nothing."""
    dd = open(os.path.join(TOOLS, "dc_drop.py"), encoding="utf-8").read()
    assert "board_sha256_16" in dd, "the solved currents still name their board by filename alone"
    assert dd.count("board_sha256_16") >= 2, "the pad potentials are not stamped as well as the currents"
    bs = open(os.path.join(TOOLS, "barrel_sites.py"), encoding="utf-8").read()
    assert "THE SOLVED CURRENTS ARE ANOTHER BOARD'S" in bs, "the reader does not check whose currents it has"
    assert "name no board sha" in bs, "a file written before the sha existed is not told apart from a match"
    # and it must DECIDE nothing: this is a sentence, not a refusal, because an older file is not an error
    i = bs.index("THE SOLVED CURRENTS ARE ANOTHER BOARD'S")
    seg = bs[max(0, i - 400):i + 400]
    assert "return 3" not in seg and "raise" not in seg, "the mismatch refuses the run instead of naming it"
