#!/usr/bin/env python3
"""A board-wide count is not a test of one closure on a net with many clusters (MESHSAT-862, 19 September 2026).

Since 12 September a stub closure is kept only when KiCad's WHOLE-BOARD unconnected count drops, which was the
answer to a closure that reported success and connected nothing (A24's `/+3V3`, "closed: 0 tracks, 1 vias,
path 1 cells", twice, with the DRC naming the same open pair afterwards both times). That rule is right when a
net has two clusters. Board A's five `*_SW2` nets carry 21, 22 and 23 items in as many clusters apiece,
because the generator lays an escape stub per pad and nothing else, and joining two of twenty-three does not
move a board-wide number: ALL TWENTY pairs were refused with `a path was found and it did not connect: start
0.000 mm and end 0.000 mm from this net's nearest copper`, in three configurations measured one variable at a
time (the pours as obstacles and not, and every layer against the outer two). The same tool on the same board
in the same run closed 9 of 10 on the five `*_CSF` nets, which carry five and twelve items, so it is the net's
shape and not the tool.

CORRECTION, the same hour: the refusal printed `start 0.000 mm and end 0.000 mm` for all twenty and that was
an artefact of measuring AFTER the pieces were taken back off. Measured before the emit the same ends are
0.153 to 4.409 mm from their own net's copper, so the search ends at a GOAL CELL and not on the net, and what
puts an end on the copper is the LANDING, whose reach had been a silent 1.2 mm since it was written.

A closure is kept now when the landing put BOTH of its ends on the net's own copper AND the board-wide count
did not RISE. That keeps the whole of what the count was protecting, because a closure that cuts a pour or shorts a
neighbour raises it, and drops only the half of it that was never about this pair. These rules exercise the
decision as one function, so they need no board and run where KiCad is not.
"""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _decide():
    """`keep_closure` and the landing reach, executed exactly as they are written in the tool."""
    src = open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()
    i, j = src.index("LAND_REACH_MM = float("), src.index("closed = 0")
    ns = {"os": os}
    exec(compile(src[i:j], "stub_router.py", "exec"), ns)
    return ns["keep_closure"]


def t_a_closure_that_drops_the_board_count_is_kept_as_it_always_was():
    assert _decide()(100, 99, False) == "count_fell"


def t_a_closure_on_a_many_cluster_net_is_kept_when_both_ends_are_on_its_copper():
    """THE DEFECTIVE FIXTURE, which is what board A's twenty pairs were: the count does not move and the
    landing put both ends on the net's own copper. Expected verdict: KEPT."""
    assert _decide()(549, 549, True) == "ends_on_copper"


def t_a_closure_that_lands_on_nothing_is_still_taken_back_off():
    """THE ACCEPTABLE FIXTURE, the defect of 12 September: a via dropped in a goal cell that touches no copper.
    Expected verdict: REFUSED, whatever the count did."""
    d = _decide()
    assert d(549, 549, False) == "refuse"


def t_a_closure_that_raises_the_board_count_is_refused_even_with_both_ends_on_copper():
    """The protection the count was there for is kept whole: cutting a pour or shorting a neighbour raises it."""
    assert _decide()(549, 552, True) == "refuse"


def t_an_unreadable_count_is_never_a_pass():
    d = _decide()
    assert d(None, 549, True) == "refuse"
    assert d(549, None, True) == "refuse"


def t_the_landing_reach_keeps_the_number_it_had_and_is_a_knob_now():
    """1.2 mm was the landing's silent reach since it was written and it stays the default, so nothing that
    worked changes; it is readable and settable so a board can be measured at its own distance, which board A
    needs because its path ends are up to 4.409 mm from their own copper."""
    src = open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()
    i = src.index("LAND_REACH_MM = float(")
    line = src[i:src.index("\n", i)]
    assert '"1.2"' in line and "STUB_LAND_REACH" in line, line
    assert "reach=LAND_REACH_MM" in src, "the landing does not use the knob it declares"


def t_the_tool_asks_the_function_rather_than_repeating_its_condition():
    src = open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()
    assert 'keep_closure(_U, _U2, ends_on == 2) == "ends_on_copper"' in src, \
        "the acceptance is written out again beside the function that decides it"
    assert "_g_start, _g_end = _gap_pre(path[0]), _gap_pre(path[-1])" in src, \
        "the two end gaps are not measured before the copper is laid, so they would read zero by construction"
    i, j = src.index("def _gap_pre"), src.index("nt, nv = emit(netobj, path)")
    assert i < j, "the gaps are measured after the copper is laid, which is how 0.000 mm came to be printed"


# ------------------------------- a closure that costs a hard violation is not a closure (19 September 2026)
# This stage judges each closure by CONNECTIVITY and the stage as a whole is judged by `guarded`, which
# reverts EVERYTHING when the hard count rises. On board A's A44 that throws away sixteen good closures for
# one bad one, and the OLD acceptance does the same on the same board, so it is the stage's oldest shape and
# not today's change: two of board A's five arms pick up one to three `clearance` items, a closure's own via
# against another net's pad. The board is judged here now and the closures are dropped back one at a time,
# newest first, until the hard count is no worse than it was handed.

def _src():
    return open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()


def t_the_bar_is_the_report_the_tool_was_handed():
    """Not a count measured again, and never zero: a stage may leave the board no worse than it found it."""
    s = _src()
    assert '_HARD0 = _hs0.counts(drc)["hard"]' in s, "the bar is not read from the report this tool was given"
    i, j = s.index("_HARD0 = _hs0.counts"), s.index("for it1, it2 in pairs:")
    assert i < j, "the bar is read after the closures have started"


def t_the_drop_back_walks_newest_first_and_stops_at_the_bar():
    s = _src()
    assert "_net, _tracks = laid.pop()" in s, "the drop-back does not take the NEWEST closure first"
    assert "while laid and _h is not None and _h > _HARD0:" in s, "the drop-back does not stop at the bar"
    assert "laid.append((net, list(b.GetTracks())[_n_before:]))" in s, \
        "nothing records what each closure laid, so there is nothing to drop back"


def t_it_is_on_by_default_and_can_be_turned_off():
    """On, because a stage that leaves the board worse is exactly what `guarded` throws away whole; off by an
    env var, because a measurement may want the stage's raw behaviour."""
    s = _src()
    assert 'os.environ.get("STUB_DRC", "1") != "0"' in s, "the drop-back is off by default or cannot be disabled"


def t_only_a_stage_that_already_hurt_pays_for_a_drc():
    """The first DRC is taken once, after the closures, and the per-closure ones only if that one is worse."""
    s = _src()
    i = s.index("_h = _hard_now()")
    j = s.index("while laid and _h is not None")
    assert s.count("_h = _hard_now()", 0, j) == 1, "more than one DRC is taken before the board is known to hurt"
    assert i < j


def t_the_drop_back_says_what_it_dropped_and_what_it_bought():
    s = _src()
    assert 'print("  dropped the closure on %s: hard %s -> %s"' in s, "a closure is dropped without saying so"
    assert "so it was not the closures" in s, \
        "a board still over the bar with every closure dropped does not say that it was not the closures"
