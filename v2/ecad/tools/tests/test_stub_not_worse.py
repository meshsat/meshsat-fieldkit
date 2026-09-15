#!/usr/bin/env python3
"""The stub stage must not leave a board more open than it found it (MESHSAT-862, 13 September 2026).

`stub_accept.py` drops a closure only when a DRC finds it in a HARD violation, so a set of closures that
opens other connections without breaking a rule is kept. On A25 the board went into the stub router at 13
unrouted, came out at 81, and stub_accept kept nine closure nets and left it at 80. The guard existed and was
measuring the wrong thing.

It is the fault the record names twice already: `stitch_prune` judging against zero instead of against the
board it was given (11 September), and a routeflow remedy throwing away a better board (11 September). The
answer is the same each time, so the finish now compares the unrouted count with what the stub router was
handed and reverts every closure if it is worse.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIN = open(os.path.join(TOOLS, "finish.sh")).read()

GUARD = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "guarded.sh"), errors="replace").read()


def t_the_finish_keeps_the_count_the_stub_stage_was_handed():
    """15 September 2026: the stub stage runs under the one guard (tools/guarded.sh), which takes the counts of the board
    it is HANDED before the command runs and compares against them, never against zero."""
    assert "guarded stub stub_stage" in FIN, "the stub stage does not run under the guard"
    i = GUARD.find('--counts "out/guard-$LBL-before.txt"'); j = GUARD.find('"$@"')
    assert 0 < i < j, "the guard does not take the handed-in counts before the command runs"


def t_it_reverts_when_the_board_ends_more_open():
    assert '"$AU" -gt "$BU"' in GUARD, "the guard does not compare the unrouted counts"
    assert 'cp "out/$N-guard-$LBL.kicad_pcb" "$N.kicad_pcb"' in GUARD, "the guard does not restore its own snapshot (the board it was handed, not the raw router board)"


def t_the_revert_re_runs_the_drc_so_later_stages_read_the_board_they_have():
    i = GUARD.find('cp "out/$N-guard-$LBL.kicad_pcb" "$N.kicad_pcb"')
    assert "drc.sh" in GUARD[i:i + 200], "after restoring, the DRC is not retaken and every later gate reads a stale one"


def t_the_hard_zero_revert_is_still_there():
    assert '"$AH" -gt "$BH"' in GUARD, "a rise in the hard count no longer restores the board"
    assert "stub_accept.py" in FIN, "the per-closure acceptance is gone"




def t_a_pass_that_closed_nothing_writes_nothing():
    """16 September 2026, A35 round two: both closures were taken back off and the fill-and-save of the unchanged
    board segfaulted in KiCad's filler (exit 139), which cost the phase. A pass that changed nothing has nothing
    to write, and the fill and the save are the two most expensive and least safe things the tool does."""
    src = open(os.path.join(TOOLS, "stub_router.py"), errors="replace").read()
    i = src.index("if closed == 0:")
    tail = src[i:i + 600]
    assert "the board is untouched" in tail, "the zero-closure path does not say the board is untouched"
    assert tail.index("else:") < tail.index("SaveBoard"), "the board is saved outside the closed-something branch"
