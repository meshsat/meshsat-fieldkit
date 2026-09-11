#!/usr/bin/env python3
"""Three rules: how a driver waits, how a tool chooses the board it judges, and how a pass walks a board.

Stage 0a and 0d of the control-plane programme (MESHSAT-862, 11 September 2026, v2/docs/CONTROL-PLANE.md).

WAITS. A wait without a deadline makes a job immortal and nothing says so. Twelve finishes and
`finish_b_after.sh` were bounded on 10 September; `long_route.sh` still held one on 11 September, waiting on
any Freerouting process started outside its own flock, and a stray java process would have held it for ever.

BOARD CHOICE. A tool must never learn which board to judge by globbing a project directory. `pcb-b-compute/`
carried `b5m.kicad_pcb`, the 2 September B5 board, beside `pcb-b-compute.kicad_pcb`, and `b5m` sorts FIRST.
A wave script that globbed the directory on 11 September exported a BOM for B from a nine-day-old board and
nothing in its output said which board it had read. The stale file is gone; this rule is what stops the next
one from mattering. A board comes from the board table (`tools/boards/<letter>.json`) or from an argument.

BOARD ORDER. A pass that LAYS copper greedily must not walk the board in the board file's own order, because
that order follows the random UUID KiCad mints for every item. Measured on 11 September: two runs of the D
chain on identical input differed in four tracks and four vias, the escape stubs of /MICAMP_OUT and /SAU_RST.
`boardorder.py` carries the stable order and the whole story; this rule is what stops a fifth laying pass
from being written without it.
"""
import os, re, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECAD = os.path.dirname(TOOLS)

LOOP = re.compile(r"^\s*(?:while|until)\b")
DEADLINE = re.compile(r"-ge\s+\"?\$\{[A-Z_]+:-\d+\}|-gt\s+\d+")
GLOB_BOARD = re.compile(r"ls\s+\"?\$?\{?\w*\}?\"?/?\*\.kicad_pcb|glob\.glob\([^)]*\*\.kicad_pcb")


def _loops(path):
    """Each loop as (start line, body text), from the header to the `done` that closes it.

    A one-line loop closes on its OWN line. Getting that wrong is not academic: the first version of this
    rule ran past the end of `while ... do sleep 20; done` and swallowed the next loop's `-gt 900`, so it
    reported the unbounded wait in long_route.sh as bounded. A rule that passes on the tree it was written
    to fail is worse than no rule, which is why every rule here is run against the pre-fix tree."""
    lines = open(path, errors="replace").read().splitlines()
    for i, line in enumerate(lines):
        if not LOOP.match(line): continue
        if re.search(r"\bdone\b", line):
            yield i + 1, line; continue
        body = [line]
        for j in range(i + 1, min(i + 40, len(lines))):
            body.append(lines[j])
            if re.search(r"\bdone\b", lines[j]): break
        yield i + 1, "\n".join(body)


def t_every_wait_loop_has_a_deadline():
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "*.sh"))):
        for n, body in _loops(p):
            if "sleep" not in body: continue          # not a wait
            if "kill -0" in body: continue            # bounded by the child it watches, which has its own timeout
            if not DEADLINE.search(body):
                bad.append("%s:%d" % (os.path.basename(p), n))
    assert not bad, "a wait loop with no deadline makes the job immortal: %s" % bad


def t_no_tool_picks_a_board_by_globbing_a_project_directory():
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "*.sh")) + glob.glob(os.path.join(TOOLS, "*.py"))):
        for n, line in enumerate(open(p, errors="replace"), 1):
            if line.lstrip().startswith(("#", '"')): continue
            if not GLOB_BOARD.search(line): continue
            # a deliverable folder holds exactly one board by construction and verify_deliverable gates that
            if "release" in line or "boards/" in line: continue
            bad.append("%s:%d %s" % (os.path.basename(p), n, line.strip()[:70]))
    assert not bad, "a tool guesses which board to judge: %s" % bad


def t_no_project_directory_holds_a_second_board():
    """The hazard the rule above protects against, checked where it lives: one board per project directory,
    so that a glob anywhere (a wave script, a one-off, a future tool) cannot pick the wrong one."""
    bad = []
    for d in sorted(glob.glob(os.path.join(ECAD, "pcb-*"))):
        if not os.path.isdir(d): continue
        boards = [os.path.basename(b) for b in glob.glob(os.path.join(d, "*.kicad_pcb"))]
        if len(boards) > 1: bad.append("%s: %s" % (os.path.basename(d), sorted(boards)))
    assert not bad, "a project directory holds more than one board: %s" % bad


# ---------------------------------------------------------------- board order

# Passes that lay copper GREEDILY, walking the board and taking room as they go, so that what fits depends
# on the order they walk in. A new one belongs here with the others.
LAYING = ("escape.py", "prefanout.py", "join_adjacent_pins.py", "pour_stitch.py")

# The other ways a tool in this tree creates copper, each of which lays from its own ordered source rather
# than from the board's file order, so a random uuid cannot reach it. These are classifications, not
# excuses: a file lands in one of them because someone read it.
GENERATORS = "lay from their own component and region lists, in the order those lists are written"
POST_ROUTE = "work from an explicit list (a DRC report, a pruned-pad list, a named net), not from board order"
ONE_OFFS = "board-specific hand fixes for one phase, each naming its own items"

CLASSIFIED = {
    "gen_pcb_e5.py": GENERATORS, "gen_pcb_p3.py": GENERATORS, "gen_pcb_a3.py": GENERATORS,
    "gen_pcb_b3.py": GENERATORS, "gen_pcb_c3.py": GENERATORS, "gen_pcb_d3.py": GENERATORS,
    "power_copper.py": GENERATORS,
    "finish_stubs.py": POST_ROUTE, "fix_pad_escapes.py": POST_ROUTE, "gap_closer_checked.py": POST_ROUTE,
    "stub_router.py": POST_ROUTE, "pair_preroute.py": POST_ROUTE, "pair_shadow.py": POST_ROUTE,
    "zone_pad_via.py": POST_ROUTE, "escape_prune.py": POST_ROUTE, "stub_accept.py": POST_ROUTE,
    "cleanup_dangling.py": POST_ROUTE, "straighten.py": POST_ROUTE, "via_merge.py": POST_ROUTE,
    "meander.py": POST_ROUTE, "ses_import_lock.py": POST_ROUTE, "ses_merge.py": POST_ROUTE,
    "part_reconcile.py": POST_ROUTE, "hand_route.py": POST_ROUTE,
    "fix_a15_node.py": ONE_OFFS, "fix_a17_node.py": ONE_OFFS, "fix_a19_node.py": ONE_OFFS,
    "fix_a21_bands.py": ONE_OFFS, "bus_a21.py": ONE_OFFS, "bump_a18.py": ONE_OFFS,
    "fix_c7_u3.py": ONE_OFFS, "d9_gndvia.py": ONE_OFFS, "post_fix_a.py": ONE_OFFS,
    "post_fix_b4.py": ONE_OFFS, "post_fix_b13.py": ONE_OFFS, "post_fix_d.py": ONE_OFFS,
}

CREATES_COPPER = re.compile(r"pcbnew\.(PCB_VIA|PCB_TRACK|PCB_ARC)\s*\(")
# Only a loop at column zero: in these scripts that is the pass itself. A `for f in b.GetFootprints()` inside
# a helper is building an obstacle list, and the same obstacles come out whatever order it walks in.
WALKS_FILE_ORDER = re.compile(r"^for\s+[\w, ()]+\s+in\s+(?:list\()?\w+\.(GetFootprints|Zones)\(\)")


def t_a_pass_that_lays_copper_walks_the_board_in_a_stable_order():
    bad = []
    for fn in LAYING:
        p = os.path.join(TOOLS, fn)
        if not os.path.exists(p): bad.append("%s is listed as a laying pass and does not exist" % fn); continue
        src = open(p, errors="replace").read()
        if not CREATES_COPPER.search(src):
            bad.append("%s is listed as a laying pass but creates no copper" % fn); continue
        if "import boardorder" not in src:
            bad.append("%s lays copper and does not use boardorder" % fn); continue
        for n, line in enumerate(src.splitlines(), 1):
            if WALKS_FILE_ORDER.match(line):
                bad.append("%s:%d walks the board in file order while laying copper" % (fn, n))
    assert not bad, "the board's own order follows a random uuid: %s" % bad


def t_every_copper_laying_tool_is_classified():
    """The rule above is only as good as its list. A tool that creates copper and is classified nowhere must
    be read by a person and put in one of the four buckets, here, in writing."""
    unclassified = []
    for fn in sorted(os.listdir(TOOLS)):
        if not fn.endswith(".py"): continue
        if fn in LAYING or fn in CLASSIFIED: continue
        if CREATES_COPPER.search(open(os.path.join(TOOLS, fn), errors="replace").read()):
            unclassified.append(fn)
    assert not unclassified, ("these create copper and are classified nowhere; read each and put it in "
                              "LAYING (and give it boardorder) or in CLASSIFIED: %s" % unclassified)


# ---------------------------------------------------------------- work budgets

# Passes whose cost grows with the square of the board's copper, so they must be bounded in WORK. Seconds are not
# a budget here: a clock decided a result in this project twice, and the fix both times was to count the work.
QUADRATIC = {
    "straighten.py": ("STRAIGHTEN_BUDGET", "the shortcut test is O(copper on the layer) per candidate; on E7 it "
                                           "ran over an hour inside a finish and the finish was killed by hand "
                                           "(appendix 32.89, 9 September 2026)"),
}


def t_a_quadratic_pass_carries_a_work_budget():
    bad = []
    for fn, (env, why) in QUADRATIC.items():
        p = os.path.join(TOOLS, fn)
        if not os.path.exists(p): bad.append("%s is listed and does not exist" % fn); continue
        src = open(p, errors="replace").read()
        if env not in src: bad.append("%s has no %s (%s)" % (fn, env, why)); continue
        if "os.environ" not in src.split(env)[1][:120]: bad.append("%s does not read %s from the environment" % (fn, env))
        if "capped" not in src: bad.append("%s spends a budget and never says when it ran out" % fn)
    assert not bad, "an unbounded quadratic pass makes a job immortal without saying so: %s" % bad


# ---------------------------------------------------------------- silent fallbacks

def t_the_router_does_not_fall_back_to_the_stock_jar_in_silence():
    """Round-two H5. Our build writes a session after every pass; the stock one writes one only when the whole job
    ends, so a cut run leaves nothing, and every pass ceiling in every profile exists because of that. route_one.sh
    chose the stock jar silently when ours was absent, and `onstart.sh` never built ours, so every fresh box routed
    on stock while the pipeline behaved as though it had not. The fallback has to be a decision, not a silence."""
    src = open(os.path.join(TOOLS, "route_one.sh"), errors="replace").read()
    assert "FR_REQUIRE_MESH" in src, "there is no way to require the patched jar"
    # from the first mention onwards, not between the first and the second: the message itself names the knob,
    # so splitting on it cuts the window short and the rule failed on correct code
    tail = src[src.index("FR_REQUIRE_MESH"):]
    assert "exit 2" in tail[:900], "requiring it must refuse, not warn and continue"
    i = src.index("freerouting-1.9.0.jar\"")
    assert "WARNING" in src[max(0, i - 400):i], "taking the stock jar must say so loudly"


def t_the_verdict_horizon_is_taken_before_the_chain_runs():
    """`pre_started` is the timestamp that decides which verdicts belong to this stage. Taken AFTER the chain,
    it excludes every verdict the chain just wrote and the stage reads as "no verdicts at all", which
    verdict.collect treats as INCONCLUSIVE. It was in that position for one commit on 11 September 2026 and the
    unit test for the collector could not see it, because the defect is where the line sits, not what it does."""
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    i = src.index("pre_started =")   # the expression changed once; the POSITION is what this rule is about
    j = src.index("rc = sh(expand(argv", i - 4000 if i > 4000 else 0)
    assert i < j, "pre_started is taken after the pre-route chain runs, so it excludes the chain's own verdicts"


def t_the_verdict_horizon_is_actually_passed_to_the_collector():
    """Computing a horizon and not passing it is the same as having none, and that is what happened: the edit
    that added `since=since` to the collect call was lost when an assertion later in the same patch script
    aborted before the file was written. `pre_started` was computed, journalled and dropped, and boards P and E
    were each blocked three times by a verdict their own earlier finish had written.

    The rule that catches it is about the CALL, not the value: two earlier rules checked that the horizon exists
    and where it is taken, and both passed throughout."""
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    i = src.index("def judge_verdicts(")
    body = src[i:src.index("\ndef ", i + 10)]
    assert "verdict.collect(" in body, body[:200]
    call = body[body.index("verdict.collect("):]
    call = call[:call.index(")") + 1]
    assert "since=" in call, "judge_verdicts collects without the horizon it was given: %s" % call


def t_a_round_starts_with_a_clean_verdict_channel():
    """The horizon has one-second resolution, so a verdict written in the same second as the stage began is not
    'before' it: P's round-two pre stage was blocked by a verify_deliverable its round-one finish had written
    0 seconds earlier. The round clears out/*.verdict.json before the chain runs, which also makes a gate that
    does not re-run read as absent rather than as its previous answer."""
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    i = src.index("pre_started =")
    window = src[max(0, i - 900):i]
    assert "*.verdict.json" in window and "os.remove" in window, \
        "a round does not clear the verdict channel before its chain runs"
    j = src.index("rc = sh(expand(argv", i)
    assert src.index("*.verdict.json") < j, "the clear happens after the chain has already written verdicts"
