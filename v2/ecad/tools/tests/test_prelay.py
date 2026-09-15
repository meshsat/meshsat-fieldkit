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

GUARD = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "guarded.sh"), errors="replace").read()


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
    """15 September 2026: the pre-lay runs under the one guard on the pre-route basis; the guard restores its snapshot
    when hard or unrouted rose against the board it was handed."""
    i = FULL.find('PRELAY="$(cfg prelay_nets)"')
    body = FULL[i:i + 2200]
    assert "GUARD_MODE=pre guarded prelay" in body, "the pre-lay does not run under the guard on the pre-route basis"
    assert '"$AH" -gt "$BH"' in GUARD and "restored as it was handed in" in GUARD, "a refused lane is not taken back and reported"


def t_it_runs_before_the_pre_route_drc_that_judges_the_board():
    i = FULL.find('PRELAY="$(cfg prelay_nets)"')
    j = FULL.find("--label 'pre-route DRC'")
    assert 0 < i < j, "the pre-lay runs after the gate that would have to judge its copper"


def t_no_board_declares_a_pre_lay_and_c_carries_the_measurement_that_says_why():
    """C15 pre-laid /EPD_SDA alone and ended at 8 open against C14's 2; C16 pre-laid the whole six-wire bus,
    5 of 7 laid on the placed board, and routed 15 and 16 open against C14's 12 and 4. A lane taken by hand
    on a board whose strips are its only corridors costs the router more than it buys. The stage stays for
    the board that measures otherwise; today none does."""
    for letter in ("a", "b", "c", "d", "e", "p"):
        d = json.load(open(os.path.join(TOOLS, "boards", letter + ".json")))
        assert not d.get("prelay_nets"), "board %s declares a pre-lay and the only measurements say it costs opens" % letter
    d = json.load(open(os.path.join(TOOLS, "boards", "c.json")))
    assert "C16 MEASURED" in d.get("_prelay_why", "") and "C15" in d.get("_prelay_why", ""), (
        "the declaration was removed without the two measurements that removed it")
