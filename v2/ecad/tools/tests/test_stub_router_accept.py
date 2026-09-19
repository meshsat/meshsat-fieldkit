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
    # A RULE THAT NAMES A VARIABLE IS A RULE ABOUT THE SPELLING (19 September 2026): this line read
    # `_net, _tracks = laid.pop()` and broke when the closure stopped being recorded as track proxies
    # and became a list of KIIDs, which is a change the rule has no opinion about. What it is about is
    # that the walk takes the NEWEST closure first, which is `pop()` from the end and never `pop(0)`.
    assert "_drop(len(laid) - 1)" in s, "the drop-back's fallback walk does not take the NEWEST closure first"
    assert "laid.pop(0)" not in s, "the drop-back takes the OLDEST closure first"
    assert "while not _gave_up and laid and _h is not None and _h > _HARD0:" in s, \
        "the drop-back does not stop at the bar"
    assert "laid.append(" in s and "_n_before:" in s, \
        "nothing records what each closure laid, so there is nothing to drop back"


def t_it_is_on_by_default_and_can_be_turned_off():
    """On, because a stage that leaves the board worse is exactly what `guarded` throws away whole; off by an
    env var, because a measurement may want the stage's raw behaviour."""
    s = _src()
    assert 'os.environ.get("STUB_DRC", "1") != "0"' in s, "the drop-back is off by default or cannot be disabled"


def t_only_a_stage_that_already_hurt_pays_for_a_drc():
    """The first DRC is taken once, after the closures, and the per-closure ones only if that one is worse."""
    s = _src()
    i = s.index("_r0 = _hard_now()")
    j = s.index("if _h is not None and _h > _HARD0:")
    assert s.count("_hard_now()", 0, j) == 2, "more than one DRC is taken before the board is known to hurt"
    assert i < j


def t_the_drop_back_says_what_it_dropped_and_what_it_bought():
    s = _src()
    assert '  dropped the closure on %s: hard %s -> %s' in s, "a closure is dropped without saying so"
    assert "so it was NOT the closures" in s, \
        "a board still over the bar with every closure dropped does not say that it was not the closures"


def t_the_drop_backs_own_drc_gets_the_boards_project_file():
    """A board without its `.kicad_pro` beside it under its own stem is judged against the DEFAULT class and
    reports hundreds of false clearance and via violations, and `drc.sh` refuses it outright (12 September
    2026). `SaveBoard` writes a project file beside whatever it saves and that one is not this board's, so the
    real one is copied over it. Caught by reading the code back before the measurement returned."""
    s = _src()
    assert '_stem + ".kicad_pcb"' in s and '_stem + ".kicad_pro"' in s, \
        "the temp board and its project file do not share a stem"
    i, j = s.index("_sh.copy(_pro"), s.index('os.path.join(_here, "drc.sh")')
    assert i < j, "the DRC runs before the board's own project file is put beside it"


def t_a_drop_back_that_could_not_judge_says_so():
    """Absence is never a pass, and this one was silent on its first live run: the DRC refused the temp board
    for want of a project file, `_hard_now` returned None, the drop-back was skipped, and the only sign was a
    stage behaving exactly as it had before (19 September 2026)."""
    s = _src()
    assert "the drop-back could not read a hard set" in s, "a drop-back that judged nothing does not say so"
    i = s.index("_r0 = _hard_now()")
    j = s.index("if _h is None:")
    assert i < j < s.index("if _h is not None and _h > _HARD0:"), "the silence check is not on the first reading"


def t_the_drop_back_names_what_went_wrong_rather_than_swallowing_it():
    """A silent `except` is how a guard stops guarding, and this block had two of them: the DRC's own refusal
    and any exception while reading the hard set both returned None with nothing said, so 'the drop-back
    judged nothing' and 'the drop-back found nothing wrong' looked identical from outside (19 September
    2026, the third time in one afternoon in my own code)."""
    s = _src()
    assert "drop-back: the DRC refused the board it was given" in s, "a refused DRC is swallowed"
    assert 'print("  drop-back: %s while reading the hard set' in s, "an exception in the reader is swallowed"
    assert "except Exception as _e:" in s, "the exception is not named"


def t_the_drop_back_judges_a_board_whose_pours_match_its_copper():
    """THE FIRST LIVE READING THIS BLOCK EVER TOOK WAS 97, on a board a driver's own DRC read at hard 1 one
    minute earlier (19 September 2026, A44). Every closure is laid INTO a poured board and the pour retreats
    around new copper only when it is refilled, so judged against the fill from before the stage each closure
    reads as copper standing inside a pour it is not part of. The drop-back then dropped one closure, saw
    97 -> 97 because the other fifteen were still under the same stale fill, and would have thrown away every
    good closure to buy nothing. It is the 14 September defect and this morning's barrel defect in a third
    place, which is why the rule is about the ORDER and not about the number: the fill happens on the copy
    before the DRC is asked, and it happens on the saved-then-loaded copy, which is the only shape KiCad 9
    does not segfault on and the only one that leaves the board being edited alone."""
    s = _src()
    i = s.index("def _hard_now():")
    j = s.index("_r0 = _hard_now()")
    body = s[i:j]
    assert "ZONE_FILLER" in body, "the drop-back judges a board it never refilled"
    a = body.index("pcbnew.LoadBoard(sys.argv[1])")
    f = body.index("ZONE_FILLER")
    d = body.index('os.path.join(_here, "drc.sh")')
    assert a < f < d, "the fill is not taken on a loaded copy before the DRC"
    assert "ZONE_FILLER(_b)" in body and "ZONE_FILLER(b)" not in body, \
        "the fill runs on the board being edited rather than on the copy"


def t_the_drop_back_holds_a_uuid_and_never_a_proxy():
    """A SWIG PROXY DIES AFTER `Remove`, which `cleanup_dangling` has carried in its own docstring since it
    was written; the drop-back removes AND saves, so a proxy held from before the save is a freed object by
    the time the next `SaveBoard` walks the list. On A44 that was a SEGFAULT (exit 139) on the drop-back's
    second measurement, after it had already printed its first (19 September 2026). The identity that
    survives a save is the item's own KIID, and the pieces are looked up fresh against the live board."""
    s = _src()
    i = s.index("laid.append(")
    assert "m_Uuid.AsString()" in s[i:i + 400], "a closure is recorded as a track proxy rather than by KIID"
    assert "list(b.GetTracks())[_n_before:]))" not in s[i:i + 200], "the raw proxy list is still appended"
    k = s.index("_net, _uuids, _p2 = laid.pop(_i)")
    assert "m_Uuid.AsString() in _want" in s[k:k + 400], \
        "the drop does not look the pieces up against the live board"


def t_the_drop_back_aims_at_the_violation_before_it_walks():
    """NEWEST-FIRST IS AN ORDERING, NOT A DIAGNOSIS (19 September 2026, measured on A44 before it was written:
    the drop-back took nine closures off in order and the hard count never moved off 1, because the violation
    belonged to a closure laid earlier). On a sixteen-closure stage that costs sixteen DRCs to find one
    culprit and throws away fifteen good closures on the way, which is the very thing this block exists to
    stop. The DRC names the POSITION of every item it reports, so the closures standing at those positions go
    first and the newest-first walk is the fallback for a violation none of this copper owns."""
    s = _src()
    assert '_it.get("pos")' in s, "the drop-back does not read where the DRC says the violation is"
    assert "def _owns(" in s, "nothing asks whether a closure is the one the DRC is complaining about"
    assert "the DRC names its net" in s, "the suspect test does not use the net the report already names"
    assert "_suspect = sorted(_why)" in s, "the closures the DRC names are not picked out"
    i, j = s.index("_suspect = sorted(_why)"), s.index("while not _gave_up and laid and _h is not None")
    assert i < j, "the newest-first walk runs before the aimed drop rather than as its fallback"
    assert "it stands at the violation" in s, "an aimed drop does not say that it was aimed"
    # 19 September 2026: they go ONE AT A TIME now, newest first among the suspects, stopping the moment
    # the bar is met. Dropping the whole suspect set together is one DRC instead of several and it
    # OVER-DROPS: a violation usually names one or two nets, and taking every closure that answers to it
    # throws away the innocent with the guilty.
    assert '_why.get(_i, "aimed")' in s, "an aimed drop does not say which suspect it took"
    assert "dropped %s together" not in s, "the suspects are still dropped as a group, which over-drops"


def t_the_refill_the_drop_back_needs_runs_in_its_own_process():
    """KiCad's state does not survive being loaded and filled over and over inside one interpreter: the ninth
    such cycle in a single run SEGFAULTED the tool (19 September 2026, exit 139 on A44 after nine honest
    measurements, which is a crash that eats the measurement AND the stage). A child process cannot take the
    parent with it, and it costs one interpreter start per measurement, which a stage that already hurt can
    afford. The rule is about the isolation, not about the command line."""
    s = _src()
    i = s.index("def _hard_now():"); j = s.index("_r0 = _hard_now()")
    body = s[i:j]
    assert "sys.executable" in body, "the refill does not run in its own interpreter"
    assert "ZONE_FILLER" in body and "_sp.run([sys.executable" in body, \
        "the fill is not the thing that was moved out of process"
    assert "the refill of the copy failed" in body, "a failed refill is swallowed"


def t_a_drop_back_that_loses_its_instrument_stops_and_says_so():
    """A refill SEGFAULTED mid-walk on A44 (19 September 2026, exit -11 from the fill's own child process on
    the second drop). `_hard_now` returned None, the `while` condition quietly went false, and the tool then
    SAVED a board it had just been told was over the bar with nothing in the log about why it stopped: the
    board came out at hard 1 with 14 closures kept and the only sign was the count. Absence is never a pass
    and it is not a completion either."""
    s = _src()
    assert "_gave_up" in s, "the walk cannot tell a finished drop-back from one that lost its instrument"
    assert "lost its instrument part way through and STOPPED" in s, "a drop-back that gave up does not say so"
    assert "is NOT known to be back at hard" in s, \
        "the board it is about to write is not declared unproven"
    i = s.index("if _gave_up:")
    j = s.index('elif _h is not None and _h <= _HARD0:')
    assert i < j, "the give-up case is reported after the success case, so a failure can read as a success"


def t_the_clearance_margin_covers_the_grid_rather_than_a_fixed_hundredth():
    """A44'S CLOSERS COST ONE CLEARANCE ITEM AND IT MISSES BY FIVE MICROMETRES (19 September 2026):
    `netclass 'SENSE' clearance 0.1270 mm; actual 0.1219 mm`, and the stage's guard threw away sixteen good
    closures for it. The margin over the class was a flat 0.01 mm, written when the grid was 0.05, while long
    closures run at `STUB_GRID=0.1`: an obstacle map that marks a cell by its CENTRE can under-represent the
    real copper by up to half a cell, so at 0.1 mm the sampling error is fifty micrometres and a ten
    micrometre margin cannot cover it. It is half a cell now with the hundredth as the floor, which is the
    pair pre-router's own lesson about a corridor that did not cover its own legs, and it is a KNOB so the
    trade can be measured rather than asserted: a wider margin refuses paths a narrower one finds."""
    s = _src()
    assert "CLR_MARGIN" in s, "the margin is not named, so it cannot be measured"
    assert "max(0.01, G / 2.0)" in s, "the margin does not scale with the grid"
    assert 'os.environ.get("STUB_CLR_MARGIN"' in s, "the margin cannot be set for an arm"
    assert "v + 0.01" not in s, "the fixed hundredth is still the margin somewhere"
    assert "v + CLR_MARGIN" in s, "the class clearance does not take the margin"


def t_a_closure_the_walk_proved_innocent_goes_back_on():
    """A44 RAN THE WALK TO THE END AND THE TOOL THREW AWAY WHAT IT HAD JUST CLEARED (19 September 2026): the
    hard count never moved off 1 through all sixteen drops, the tool printed that it was not the closures,
    and then wrote `closed 0 of 19`. So it had spent sixteen DRCs to prove them innocent and lost all sixteen
    anyway, which is strictly worse than the behaviour it replaced. Taking copper off can only break
    connectivity and never make it, which is the argument `dot_prune`'s rescue loop already rests on, so a
    closure the walk cleared is safe to put back."""
    s = _src()
    assert "_taken.append((_net, _gone))" in s, "the dropped pieces are not kept, so nothing can be restored"
    assert "it was NOT the closures; putting all %d back" in s, "an innocent set is not put back"
    assert "closed = _closed0" in s, "the kept count is not restored with the copper"
    # NO FIXED WINDOW (the ratchet in test_rule_windows exists because a slice of N characters breaks when a
    # comment is added and passes wrongly when code is removed): the rule asks for the ORDER instead.
    assert s.index("it was NOT the closures") < s.index("b.Add(_t2)") < s.index("closure(s) restored"), \
        "the restore does not add the pieces back after the walk cleared them"


def t_every_open_net_gets_its_turn_at_the_closer():
    """WITHOUT A PER-NET BUDGET THE ALPHABET DECIDES WHICH OPENS ARE EVEN TRIED (19 September 2026). The tool
    had a node cap per search and the stage's own wall clock and nothing in between, so a net with many
    clusters spends search after search and the run ends before the later nets are reached. Board E's E23
    round 2 has six opens and its first alphabetically, `/FAN1_PWM`, is a 224 mm run across the strip that no
    closer can make: at the finish's own STUB_GRID=0.1 it ate thirty minutes on its own and the other five
    were never offered to the closer at all, which is why board E's closers keep reading "took none". The
    budget is per NET and checked before each pair, so an unclosable net costs its own budget and nothing
    else's, and zero turns it off."""
    s = _src()
    assert "STUB_NET_BUDGET_S" in s, "there is no per-net budget, so one net can eat the whole stage"
    assert "_net_t0" in s and "_NET_BUDGET" in s, "the budget is not measured per net"
    i, j = s.index("for it1, it2 in pairs:"), s.index("trk, via = build_maps(net)")
    assert s.index("_NET_BUDGET > 0", i) < j, "the budget is checked after the expensive work rather than before it"
    assert "the rest of this net's pairs are left so the other" in s, "a net that runs out of budget says nothing"


def t_a_cap_in_nodes_is_not_a_cap_in_time():
    """STUB_MAXN is 4,000,000 by default and board E's grid at the finish's own STUB_GRID=0.1 is about 6.7
    million cells over four layers, so ONE search can legitimately walk most of the board. `/FAN1_PWM`, a
    224 mm run across the strip that nothing can close, ate thirty minutes inside a single pair twice over
    and board E's other five opens were never reached; the per-net budget cannot help there because it is
    checked between pairs. The search carries its own clock now, checked inside the expansion loop, and it
    says when it gave up, because a search that stopped early and a search that found nothing are different
    answers (19 September 2026)."""
    s = _src()
    assert "STUB_SEARCH_S" in s, "a single search has no clock, so one pair can eat the whole stage"
    i = s.index("while pq:")
    j = s.index("for di, dj, c in steps:", i)
    assert "_s_budget" in s[i:j], "the clock is not checked inside the expansion loop"
    assert "the search gave up after" in s, "a search that ran out of time is indistinguishable from one that failed"


def t_the_drop_back_is_bounded_so_a_stage_is_not_killed_inside_it():
    """The drop-back runs INSIDE the stage, before the fill and save, and the stage is under the finish's own
    `stub_timeout_s`. Board A's closing stage already takes most of its hour at the board's own `stub_env`,
    so an unbounded walk of one DRC-and-refill per drop can push the whole stage past its timeout, and a
    stage killed there saves nothing and loses every closure it made. The walk stops on its own budget
    through the same honest path as a lost instrument, which says the board is NOT known to be back at the
    bar rather than pretending it is (19 September 2026)."""
    s = _src()
    assert "STUB_DROP_BUDGET_S" in s, "the drop-back can run for as long as it likes inside a timed stage"
    assert "def _out_of_time():" in s, "the budget is not a test the walk can ask"
    i = s.index("while not _gave_up and laid and _h is not None")
    j = s.index("_net = _drop(len(laid) - 1)", i)
    assert s.index("_out_of_time()", i) < j, "the budget is checked after the drop rather than before it"
    assert "still on the board" in s, "a walk that ran out of budget does not say what it left behind"


def t_a_stage_cut_at_its_wall_would_save_nothing_so_the_tool_is_told_the_wall():
    """THE FILL AND THE SAVE ARE THE LAST THING THIS TOOL DOES, so a stage cut by `finish.sh`'s `timeout`
    throws away every closure it made. A49's finish closed its first net TWENTY MINUTES into a 3600 s cap
    with twenty opens to go, and all of it would have gone at the wall for no reason (19 September 2026).
    `STUB_STAGE_S` is the caller telling the tool how long it has: it stops LAYING before that and spends
    what is left filling and saving what it has, and it says so. The `timeout` stays as the backstop. Zero is
    off and the tool behaves exactly as it did, which is also what happens when nobody passes it."""
    s = _src()
    assert "STUB_STAGE_S" in s, "the tool cannot know its own wall, so a cut stage saves nothing"
    assert "_STAGE_T0" in s, "the wall is not measured from the tool's own start"
    i = s.index("for it1, it2 in pairs:")
    j = s.index("trk, via = build_maps(net)", i)
    assert s.index("_STAGE_S > 0", i) < j, "the wall is checked after the expensive work rather than before it"
    assert "it stops laying now and spends what is left filling and saving them" in s, \
        "a stage that hit its wall does not say what it did about it"


def t_the_finish_passes_the_wall_it_imposes():
    """A limit the caller enforces and does not tell the tool about is how a stage loses an hour's work."""
    import os
    fin = open(os.path.join(TOOLS, "finish.sh"), encoding="utf-8").read()
    assert "STUB_STAGE_S=$STUB_STAGE_S" in fin, "the finish does not tell the stub router its wall"
    i, j = fin.index("STUB_STAGE_S=\"$(python3"), fin.index("STUB_STAGE_S=$STUB_STAGE_S")
    assert i < j, "the wall is computed after it is passed"
    assert 'timeout "$STUB_T"' in fin, "the timeout is no longer the backstop"


def t_the_drop_back_stands_down_when_the_stage_is_at_its_wall():
    """The drop-back costs a DRC and a refill per measurement and it runs BEFORE the fill and the save.
    `finish.sh` leaves five minutes between `STUB_STAGE_S` and its `timeout`, and that five minutes is the
    fill and the save and nothing else. Running the drop-back there is how a stage that stopped laying IN
    ORDER to bank its work gets killed banking it, which would undo the whole point of the wall (19 September
    2026). The stage's own guard is what stands behind those closures in that case, exactly as it did before
    the drop-back existed, and the tool says so rather than leaving it to be inferred."""
    s = _src()
    assert "if not _stage_over and closed and os.environ.get(\"STUB_DRC\"" in s, \
        "the drop-back still runs after the stage has hit its wall"
    assert "the drop-back is SKIPPED" in s, "a skipped drop-back says nothing about itself"
    assert "judged by the stage's own guard and by nothing here" in s, \
        "the closures left behind are not declared unjudged by this tool"
    i, j = s.index("if _stage_over and closed"), s.index("if not _stage_over and closed")
    assert i < j, "the skip notice comes after the block it replaces"


def _put_fn():
    """`_put`, executed exactly as the tool writes it. It needs numpy and nothing else, so it runs here."""
    import numpy as _np
    s = _src()
    i = s.index("def _put(mask,")
    j = s.index("def disc(mask,")
    ns = {"np": _np}
    exec(compile(s[i:j], "stub_router.py", "exec"), ns)
    return ns["_put"], _np


def t_a_stamp_ors_into_a_boolean_map_and_counts_into_an_integer_one():
    """THE WHOLE CACHE RESTS ON THIS ONE LINE (19 September 2026). A counted map is what lets the board be
    rasterised once instead of once per net: stamp everything, stamp the net's own items separately, and the
    cells blocked for that net are where the two counts differ. `|=` on an integer array is a BITWISE OR, so
    two overlapping obstacles in one cell would read 1, the net's own single item would read 1, and the cell
    would come out free: a closure laid straight through another net's copper, refused only later by the
    board-wide guard if it happened to raise the count. The helpers all compute the same boolean block and
    this is the one place that decides what is done with it."""
    _put, np = _put_fn()
    block = np.array([[True, True], [False, True]])
    m = np.zeros((2, 2), dtype=bool)
    _put(m, 0, 1, 0, 1, block); _put(m, 0, 1, 0, 1, block)
    assert m.tolist() == [[True, True], [False, True]], "a boolean map stopped being an OR"
    c = np.zeros((2, 2), dtype=np.int16)
    _put(c, 0, 1, 0, 1, block); _put(c, 0, 1, 0, 1, block)
    assert c.tolist() == [[2, 2], [0, 2]], "an integer map is not counting its stamps, so the cache cannot subtract"


def t_every_helper_accumulates_through_that_one_decision():
    """A helper that writes `mask[...] |= ...` itself is correct today and wrong the moment it is handed a
    counted map, and nothing about its call site says which kind it will get."""
    s = _src()
    i, j = s.index("def disc(mask,"), s.index("# ---- parse the unconnected pairs")
    body = s[i:j]
    assert "mask[i0:i1 + 1, j0:j1 + 1] |=" not in body, \
        "a rasterisation helper accumulates into its mask by itself instead of through _put"
    assert body.count("_put(mask,") == 4, "not every helper (disc, segment, poly, zpoly) stamps through _put"


def t_nothing_net_independent_is_ever_subtracted_from_the_total():
    """A hole-to-hole disc binds against a net's OWN drills as well as everyone else's, and a rule area, the
    board edge and the margin belong to no net at all. Counted into the total and then subtracted with the
    net's own items, every one of them would free copper the board does not have: the subtraction is the one
    operation in the cache that can only ever make the map emptier. They are kept in a separate BOOLEAN map
    that is OR'd in afterwards, and the own-map is built with that map absent so it cannot receive them."""
    s = _src()
    assert 'if _pth and aly_via is not None:' in s, "the drilled-pad hole-to-hole disc is not kept out of the subtractable total"
    assert 'if t.GetClass() == "PCB_VIA" and aly_via is not None:' in s, "the via hole-to-hole disc is not kept out of the subtractable total"
    assert '_stamp(own_trk, own_via, None, None, net, "own"' in s, \
        "the net's own map is offered the net-independent obstacles, which it would then subtract"
    assert 'if aly_trk is None: continue' in s and 'if aly_trk is None: return' in s, \
        "the own pass does not decline the rule areas, the board edge and the margin"
    assert '| ent["aly_trk"][L]' in s and '| ent["aly_via"]' in s, \
        "the net-independent map is not put back after the subtraction"


def t_copper_taken_off_the_board_rebuilds_the_map_rather_than_topping_it_up():
    """This tool LAYS copper between nets and takes it back off again: a refused closure is reverted and the
    drop-back removes whole closures at the end. Copper ADDED can be stamped into the total, which is the
    top-up and is the point of the cache. Copper REMOVED leaves the total too high somewhere and there is no
    stamp that lowers it, so the honest answer is to drop the bucket and rebuild. The watch is on the tracks'
    own identity, because a count of them cannot tell one piece added and one removed from nothing at all."""
    s = _src()
    assert 'if ent is not None and not (ent["kiids"] <= kii):' in s, \
        "a removal is not detected, so the cached map can stand higher than the board"
    assert "copper was taken off the board, so every bucket is rebuilt" in s, \
        "a rebuild after a removal says nothing about itself"
    i, j = s.index('if ent is not None and not (ent["kiids"] <= kii):'), s.index('if ent is not None:\n        new =')
    assert i < j, "the removal check runs after the top-up, which would stamp into a map that is already wrong"


def t_the_cache_key_carries_everything_the_radii_depend_on():
    """Two nets share a map only when every number in the scan agrees. Three of them are not the net's class:
    `STUB_NET_CLEAR` raises the laid net's own floor per pre-lay group, a narrow track end pulls TW down for
    one net alone, and a thin closure takes the board's minimum via instead of its class's. Every radius in
    the scan is `r + clearance + TW/2` or `+ VIA_D/2`, and VIA_DR sets the hole-to-hole discs, so a key
    missing any of them hands one net the map of another."""
    s = _src()
    assert "key = (round(_me, 6), round(TW, 6), round(VIA_D, 6), round(VIA_DR, 6))" in s, \
        "the cache key does not carry the clearance floor, the width and the via the map was built for"
    assert "if not _MAP_CACHE_ON: return _reference_maps(net, clr_to, w2, vr)" in s, \
        "with the cache off this is no longer the map the tool has always built"


def t_a_cached_map_that_differs_from_the_reference_stops_the_run():
    """The check mode is the proof, so it cannot be a warning: a map that differs from the one this tool has
    always searched is a board the tool cannot see, which is the 16 September defect exactly."""
    s = _src()
    assert "STUB_MAP_CHECK" in s, "there is no way to ask whether the cached map is the reference map"
    assert "refusing to route on it" in s, "a differing cached map does not stop the run"
    assert "raise SystemExit" in s[s.index("STUB_MAP_CHECK: the cached map differs"):][:400], \
        "the check prints its finding and carries on"
