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


def t_the_finish_keeps_the_count_the_stub_stage_was_handed():
    assert "out/$N-drc-before-stub.json" in FIN, "the finish keeps no DRC from before the stub router"
    i = FIN.find("drc.sh $N.kicad_pcb out/$N-drc-before-stub.json")
    j = FIN.find("stub_router.py")
    assert 0 < i < j, "the before-stub DRC must be taken before the stub router runs"


def t_it_reverts_when_the_board_ends_more_open():
    assert "MORE OPEN than it found it" in FIN, "nothing compares the two counts"
    i = FIN.find("MORE OPEN than it found it")
    blk = FIN[i - 400:i + 400]
    assert 'cp out/$N-par-routed.kicad_pcb $N.kicad_pcb' in blk, "it does not revert to the router's own board"
    assert '"$_UA" -gt "$_UB"' in blk, "the comparison is not on the unrouted counts"


def t_the_revert_re_runs_the_drc_so_later_stages_read_the_board_they_have():
    i = FIN.find("MORE OPEN than it found it")
    blk = FIN[i:i + 400]
    assert blk.count("drc.sh") >= 1, "after reverting, the DRC is not retaken and every later gate reads a stale one"


def t_the_hard_zero_revert_is_still_there():
    """The older guard, which reverts when a closure brings a hard violation, must survive this one."""
    assert "stub router hurt: reverting" in FIN, "the hard-violation revert is gone"
