#!/usr/bin/env python3
"""A trial board is measured with its connectivity rebuilt, and a crashing stage is not silent (14 Sep 2026).

`direct_close` lays a candidate shape on a copy, fills the zones, saves it and asks the DRC whether the board
improved. On A26 every trial came back with **499 unconnected items**, which is KiCad's own cap on that list,
against the 12 the real board has: the filler had been given a stale net graph, so every pour connection read
as open and `U1 < U0` could never be true. The tool could not accept a shape on that board no matter what it
proposed.

It was invisible for a second reason: the finish ran it as `python3 ... | grep -a direct_close`, so its stdout
was block-buffered and the process then SEGFAULTED in pcbnew, taking 1,812 lines of output with it. The finish
log showed nothing at all between `stitch_prune` and `quality`, and the stage looked like it had never run.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DC = open(os.path.join(TOOLS, "direct_close.py")).read()
FIN = open(os.path.join(TOOLS, "finish.sh")).read()

GUARD = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "guarded.sh"), errors="replace").read()


def t_the_trial_board_has_its_connectivity_rebuilt_before_the_fill():
    i = DC.find("pcbnew.ZONE_FILLER(b).Fill(b.Zones())")
    assert i > 0, "direct_close no longer fills its trial board"
    assert "BuildConnectivity()" in DC[max(0, i - 400):i], "the filler is given a stale net graph"


def t_the_trial_board_is_saved_with_the_connectivity_it_was_measured_with():
    i = DC.find("pcbnew.SaveBoard(trial, b)")
    assert "BuildConnectivity()" in DC[max(0, i - 300):i], "the board is saved before its connectivity is rebuilt"


def t_the_finish_runs_it_unbuffered():
    i = FIN.find("direct_close.py")
    blk = FIN[max(0, i - 200):i]
    assert "python3 -u" in blk, "a buffered stdout dies with the process when it crashes"


def t_the_finish_reads_its_exit_status():
    """direct_close runs under the guard, which runs the command in the current shell (a process substitution, not a
    pipe) and reads its exit status into RC and the verdict file."""
    assert "guarded direct_close python3 -u $T/direct_close.py" in FIN, "direct_close does not run under the guard"
    assert 'RC=$?' in GUARD and '"$@" > >(tee' in GUARD, "the exit status is thrown away by a pipeline"


