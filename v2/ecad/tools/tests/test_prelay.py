#!/usr/bin/env python3
"""A long net the router will not take is laid before the router runs (MESHSAT-862, 14 September 2026).

Board C's `/EPD_SDA` runs 249 mm from J_EPD pin 14 to U3 pad 5 across a panel whose outline is a ring with a
240 by 176 mm display window through the middle, so it has exactly one corridor: east along the top strip,
then south down the right strip. Four routes left it or left another net exactly like it (C11 left EPD_SDA,
C12 left /PWM1 and /HB2, C13 left fifty-nine, C14 left EPD_SDA and /HB3), and a board-wide search at a 0.1 mm
grid on all three routing layers finds no path on the ROUTED board even at the panel's own 0.127 clearance.

On the PLACED board those strips are empty. The lane is laid there, locked, and the router works around it.
That is `bus_a21.py`'s pattern of 5 September with the waypoints searched instead of typed, and these rules
hold the three things that make it safe: it is declared per board and off everywhere else, it is restricted
to the named nets rather than let loose on a board where every net is unconnected, and the board is kept only
if the hard count does not rise.
"""
import os, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = open(os.path.join(TOOLS, "full.sh")).read()
SR = open(os.path.join(TOOLS, "stub_router.py")).read()


def t_the_search_can_be_restricted_to_named_nets():
    assert 'os").environ.get("STUB_NETS"' in SR, "there is no net filter, so a placed board would be routed whole"
    i = SR.find("_WANT = ")
    body = SR[i:i + 700]
    assert "if _WANT and netname(its[0][\"net\"]) not in _WANT: continue" in body, (
        "the filter does not actually skip the pairs of other nets")


def t_the_stage_is_declared_per_board_and_off_by_default():
    assert 'PRELAY="$(cfg prelay_nets)"' in FULL, "the stage does not read its declaration"
    assert 'if [ -n "$PRELAY" ]; then' in FULL, "the stage runs on boards that never asked for it"
    for letter in ("a", "b", "d", "e", "p"):
        d = json.load(open(os.path.join(TOOLS, "boards", letter + ".json")))
        assert not d.get("prelay_nets"), "board %s declares a pre-lay and nothing has measured one there" % letter


def t_the_board_is_kept_only_if_the_hard_count_does_not_rise():
    i = FULL.find('PRELAY="$(cfg prelay_nets)"')
    body = FULL[i:i + 2200]
    assert "preprelay" in body, "there is no copy to go back to"
    assert 'if [ "$H1" -gt "$H0" ]' in body, "nothing compares the hard count before and after"
    assert "the lane hurt the board and was taken back" in body, "a refused lane is not reported as one"


def t_it_runs_before_the_pre_route_drc_that_judges_the_board():
    i = FULL.find('PRELAY="$(cfg prelay_nets)"')
    j = FULL.find("--label 'pre-route DRC'")
    assert 0 < i < j, "the pre-lay runs after the gate that would have to judge its copper"


def t_c_declares_it_with_its_reason():
    d = json.load(open(os.path.join(TOOLS, "boards", "c.json")))
    nets = {n.strip() for n in (d.get("prelay_nets") or "").split(",")}
    assert {"/EPD_SDA", "/EPD_SCL", "/EPD_DC", "/EPD_RST", "/EPD_CS", "/EPD_BUSY"} <= nets, (
        "board C does not declare the whole e-paper bus; C15 pre-laid SDA alone and the route then left "
        "DC, RST and SCL open, the lines beside it in the same corridor: %s" % sorted(nets))
    assert d.get("prelay_layers"), "no layers are named, so the search would take the tool's default two"
    assert "249 mm" in d.get("_prelay_why", ""), "the declaration does not carry the measurement behind it"
