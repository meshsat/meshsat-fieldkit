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
    "part_reconcile.py": POST_ROUTE, "hand_route.py": POST_ROUTE, "direct_close.py": POST_ROUTE,
    "fix_a15_node.py": ONE_OFFS, "fix_a17_node.py": ONE_OFFS, "fix_a19_node.py": ONE_OFFS,
    "fix_a21_bands.py": ONE_OFFS, "bus_a21.py": ONE_OFFS, "bump_a18.py": ONE_OFFS,
    "fix_c7_u3.py": ONE_OFFS, "fix_d10_hubdm1.py": ONE_OFFS, "d9_gndvia.py": ONE_OFFS, "post_fix_a.py": ONE_OFFS,
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
    on stock while the pipeline behaved as though it had not. The fallback has to be a decision, not a silence.

    12 September 2026: the decision moved into `fr_jar.sh`, because route_one.sh was the only launcher making it."""
    src = open(os.path.join(TOOLS, "fr_jar.sh"), errors="replace").read()
    assert "FR_REQUIRE_MESH" in src, "there is no way to require the patched jar"
    tail = src[src.index("FR_REQUIRE_MESH"):]
    assert "return 2" in tail[:1200], "requiring it must refuse, not warn and continue"
    i = src.index('freerouting-1.9.0.jar"')
    assert "WARNING" in src[max(0, i - 400):i], "taking the stock jar must say so loudly"


def t_every_freerouting_launcher_takes_the_one_jar_answer():
    """12 September 2026. `jar_in_use()` gave the python side one answer in the middle of this same defect: a record
    that named the stock jar while the patched one ran. The SHELL side kept the original of it. route_one.sh chose
    properly; cont_route.sh, route_part.sh and long_route.sh each pinned `~/bin/freerouting-1.9.0.jar` by name, and
    route_pcb.sh took `ls ~/bin/freerouting-*.jar | tail -1`, which is 2.4.1 on a host that has it, launched with
    1.9.0 arguments under whatever java is first on PATH.

    Every one of them runs under a `timeout`, which is what makes the pin cost something rather than merely being
    untidy: on the stock jar a capped run leaves no session at all. cont_route.sh is declared at 80 passes in 900
    seconds against a board whose 60 passes take four hours, so the continuation could never have kept anything.
    fr_probe.sh is exempt and takes its jar as an argument, because comparing two jars is its whole purpose, and
    cont21.sh names 2.1.0 in its own name."""
    exempt = {"fr_probe.sh", "fr_jar.sh", "cont21.sh"}
    launches, names = [], []
    for f in sorted(os.listdir(TOOLS)):
        if not f.endswith(".sh") or f in exempt: continue
        src = "\n".join(l for l in open(os.path.join(TOOLS, f), errors="replace").read().splitlines()
                        if not l.lstrip().startswith("#"))
        chooses = "fr_jar " in src or "fr_jar)" in src
        if "-jar" in src and not chooses: launches.append(f)          # runs the router itself
        if "freerouting-" in src and ".jar" in src and not chooses: names.append(f)   # or pins one by name for a caller
    assert not launches, "these launch the router without fr_jar.sh: %s" % ", ".join(launches)
    assert not names, "these name a jar file rather than asking fr_jar.sh: %s" % ", ".join(names)


def t_every_capped_router_run_asks_for_the_per_pass_session():
    """The per-pass session is the only reason a cap is survivable, and it is a `-D` property the launcher has to
    pass. route_one.sh passed it; cont_route.sh and route_part.sh did not, so even on our own jar their timeouts
    threw the whole run away. The stock jar ignores an unknown property, so the line is safe with either."""
    for f in ("route_one.sh", "cont_route.sh", "route_part.sh"):
        src = open(os.path.join(TOOLS, f), errors="replace").read()
        i = src.index("-jar ")
        line = src[src.rindex("\n", 0, i) + 1:src.index("\n", i)]
        assert "freerouting.ses_per_pass" in line, \
            "%s runs the router under a timeout without asking for a session per pass" % f

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


def t_the_straightener_merges_a_whole_pass_before_reindexing():
    """The merge phase rebuilt its index over every live segment and restarted the scan after EACH merge, which
    is O(n squared) in segments. Board E reached the quality pass with 3,862 segments after the stub router
    closed three nets with 2,178-cell paths, and this ran for over an hour. A pass takes every merge it can find
    and only then re-indexes, and every merge is charged to the work budget so the bound is not a clock."""
    src = open(os.path.join(TOOLS, "straighten.py"), errors="replace").read()
    i = src.index("while changed")
    body = src[i:src.index("# 2.", i)]
    assert "break" not in body.split("if same_line_opposite")[-1], \
        "the merge loop still restarts after a single merge"
    assert "checks[0] < BUDGET" in body, "the merge loop is not bounded by the work budget"
    assert "touched" in body, "the pass does not guard against merging a segment twice"


def t_nothing_records_a_jar_by_a_default_string():
    """Every place that RECORDED which jar ran carried its own default, '~/bin/freerouting-1.9.0.jar', so with
    nothing pinned the journal line, the provenance file and the benchmark row all named the STOCK jar while the
    patched one ran. A record that says something other than what happened is what this channel exists to
    remove. One function answers the question and everything that records a jar calls it."""
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    assert "def jar_in_use(" in src, "there is no single answer to which jar ran"
    body = src[src.index("def jar_in_use("):]
    body = body[:body.index("\ndef ", 10)]
    rest = src.replace(body, "")
    for line in rest.splitlines():
        if "freerouting-1.9.0.jar" not in line: continue
        if line.strip().startswith("#"): continue
        assert ("preflight" in line or "checks.append" in line or "endswith" in line or "ok(" in line), \
            "a jar is recorded by a default string rather than by jar_in_use(): %s" % line.strip()[:120]


def t_the_supervisor_keeps_the_best_routed_board_of_a_run():
    """A remedy can make a board worse and every round re-routes from scratch, so the supervisor was discarding
    a good board to keep a bad one: board E went 0 hard and 1 open in round one, then 0 hard and 23 opens after
    the via_costs remedy, and the 1-open board was gone. Every other stage in this pipeline keeps a result only
    if it improves (cont_route.sh, stub_accept.py, quality_pass.sh); the supervisor did not."""
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    assert "best_board = (None, None, 0)" in src, "the run does not track a best board"
    i = src.index("def run(profile_fn")
    body = src[i:]
    assert "RESTORED_BEST" in body, "nothing restores the best board when the rounds run out"
    j = body.index('status = "STOPPED_BUDGET"')
    tail = body[j:j + 1400]
    assert "shutil.copy(best_board[1]" in tail, \
        "the budget stop does not put the best board back, so the run ends on the worst round"
    # and a restored board is not a finished board: the finish is what closes the last opens, runs every gate
    # and cuts the deliverable, and it last ran on the round being discarded.
    assert "restored best board" in body, "the restored board never gets its finish"


def t_a_phase_copy_declares_what_its_board_declares():
    """A phase directory is a copy of its board's project, and the declaration files travel with the copy:
    `lcsc-allow.txt`, `erc-allow.txt`, `bypass-allow.txt`. They are TRACKED, so a copy taken before a fix keeps
    the old declaration and every `git reset --hard` restores it.

    Board E was a clean board on 12 September, 0 hard and 0 unrouted through every gate, and its deliverable was
    refused for five sensor headers whose allow line had been corrected hours earlier in `pcb-e1-dock` while
    `pcb-e1-dock-e7` still carried the sixteen-line version. The board was judged against a declaration that is
    not the one in the repo."""
    ecad = os.path.dirname(TOOLS)
    bad = []
    for d in sorted(glob.glob(os.path.join(ecad, "pcb-*-*"))):
        m = re.fullmatch(r"(pcb-[a-z0-9]+-[a-z0-9]+)-([a-z]\d+)", os.path.basename(d))
        if not m: continue
        canon = os.path.join(ecad, m.group(1))
        if not os.path.isdir(canon): continue
        for f in ("lcsc-allow.txt", "erc-allow.txt", "bypass-allow.txt"):
            a, b = os.path.join(canon, f), os.path.join(d, f)
            if not os.path.exists(a): continue
            if not os.path.exists(b): bad.append("%s has no %s" % (os.path.basename(d), f)); continue
            if open(a, errors="replace").read() != open(b, errors="replace").read():
                bad.append("%s/%s differs from %s's" % (os.path.basename(d), f, m.group(1)))
    assert not bad, "a phase copy declares something its board does not: %s" % bad


def t_the_restored_board_brings_its_project_files():
    """The project file carries the net-class assignments every gate reads, and a remedy can change the route
    block between rounds. A board from round N under a project file from round N+1 is the B19 trap of
    9 September again, where a copied project directory had no netclass_assignments and every gate judged the
    board against the Default class."""
    src = open(os.path.join(TOOLS, "routeflow.py"), errors="replace").read()
    i = src.index("RESTORED_BEST")
    window = src[max(0, i - 800):i]
    assert ".kicad_pro" in window and ".kicad_prl" in window, \
        "the restore copies only the board, leaving the previous round's project file beside it"


def t_a_timing_wrapper_comes_after_the_function_it_wraps():
    """`X = _timed("bucket", X)` above `def X` is a NameError at import, and the file still compiles.

    11 September 2026: three buckets were added to the pre-router's profile and two of them named functions
    defined two hundred lines further down. Compiling proved nothing, which is the standing lesson of this
    project in another costume: the error lives on the import path, not in the parse."""
    src_path = os.path.join(TOOLS, "pair_preroute.py")
    src = open(src_path, errors="replace").read()
    lines = src.splitlines()
    defined = {}
    for i, ln in enumerate(lines):
        m = re.match(r"def (\w+)\(", ln)
        if m and m.group(1) not in defined: defined[m.group(1)] = i
        m = re.match(r"class (\w+)[\(:]", ln)
        if m and m.group(1) not in defined: defined[m.group(1)] = i
    bad = []
    for i, ln in enumerate(lines):
        m = re.match(r"(\w+)(?:\.\w+)? = _timed\(", ln.strip())
        if not m: continue
        name = m.group(1)
        if name in defined and defined[name] > i:
            bad.append("line %d wraps %s, which is defined at line %d" % (i + 1, name, defined[name] + 1))
    assert not bad, "a timing wrapper runs before its function exists:\n  " + "\n  ".join(bad)


def t_the_compiled_stub_search_defaults_off_without_numba():
    """`PAIR_FAST_STUBS` must default from the kernel's own HAVE_NUMBA, never from a bare "1".

    11 September 2026: the stub search moved onto pairsearch's kernel and is 14.7x on B19 WITH numba. Without
    numba that same kernel is a numpy heap in a Python loop, which is slower than the heapq it replaces, so a
    bare default would quietly make every host that lacks numba worse while the measurement that justified the
    change was taken on one that has it."""
    src = open(os.path.join(TOOLS, "pair_preroute.py"), errors="replace").read()
    m = re.search(r'_FAST_STUBS = os\.environ\.get\("PAIR_FAST_STUBS",\s*([^)]*)\)', src)
    assert m, "pair_preroute.py has no _FAST_STUBS default to check"
    assert "HAVE_NUMBA" in m.group(1), "the default is %s: it must read pairsearch.HAVE_NUMBA" % m.group(1).strip()


def t_no_router_takes_an_auto_selected_x_display_alone():
    """Two routes on one host must not race for a display.

    12 September 2026: `xvfb-run -a` chooses by racing, so two routes a minute apart can land on the same display.
    (The suspicion that this had killed C10's router at pass 24 was WRONG, and is recorded here because a false
    cause in a comment outlives the bug it invents.) `-n` names a number and `-a` still walks forward from it."""
    import os, re
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = []
    for f in sorted(x for x in os.listdir(tools) if x.endswith(".sh")):
        for ln in open(os.path.join(tools, f), errors="replace"):
            if ln.lstrip().startswith("#"): continue   # a comment may quote the defect it describes
            code = ln.split(" #", 1)[0]                # and so may a trailing one
            for m in re.finditer(r"xvfb-run\s+(-[a-z]+\s+)*", code):
                seg = m.group(0)
                if "-n" not in seg and "-a" in seg: bad.append("%s: %s" % (f, code.strip()[:80]))
    assert not bad, "a router takes an auto-selected display with no number of its own:\n  " + "\n  ".join(bad)


def t_no_script_kills_every_display_on_the_host():
    """`pkill -9 -f "^Xvfb"` cleared one script's stale display by killing every virtual display on the machine,
    which would take every other route's router with it. A named display makes the problem local."""
    import os, re
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bad = [f for f in sorted(os.listdir(tools)) if f.endswith(".sh")
           and re.search(r"pkill[^\n]*\^?Xvfb", open(os.path.join(tools, f), errors="replace").read())]
    assert not bad, "these scripts kill every Xvfb on the host: " + ", ".join(bad)

def t_the_contention_order_tool_is_classified():
    """Every tool in this directory is one of the declared classes; a new one must say which."""
    import os
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert os.path.exists(os.path.join(tools, "pair_order_from_plan.py")), "the contention-order tool is gone"
    s = open(os.path.join(tools, "pair_order_from_plan.py"), errors="replace").read()
    assert "PAIR_ORDER_FILE" not in s or "plan" in s, "the tool must say what it consumes"
    assert "appendix 32.137" in s, "a tool born of a measurement carries the section that measured it"


def t_a_board_is_never_drcd_without_its_project_file():
    """A board file whose `.kicad_pro` is not beside it under its own stem is checked against the DEFAULT net
    class: hundreds of false clearance and via violations, with nothing in the output saying which class set was
    used. It has cost this pipeline twice. First on 7 September 2026, when `pcb-b-compute-b19` was staged from a
    B15-era project file and `intent_checks.py` crashed on `netclass_assignments: None` against btest's 396.
    Then on 12 September, when `cont_route.sh` scored its `-before` copy, whose stem no project file matches, and
    printed "before hard 1074" for a board the finish had measured at hard 0 one minute earlier.

    The check belongs at the one place that judges rather than in each caller, and it is a refusal, because a
    number computed against the wrong rules is worse than no number."""
    src = open(os.path.join(TOOLS, "drc.sh"), errors="replace").read()
    assert "kicad_pro" in src, "drc.sh does not look for the board's project file"
    i = src.index("${B%.kicad_pcb}.kicad_pro")   # the test itself, not the comment that explains it
    assert "exit 1" in src[i:i + 700], "drc.sh warns about a missing project file instead of refusing"
    assert "DRC_REQUIRE_PROJECT" in src, "there is no way to judge a board against the default classes deliberately"
    # and every shell tool that makes a copy of a board under a NEW stem and scores it must copy the project too
    src = open(os.path.join(TOOLS, "cont_route.sh"), errors="replace").read()
    assert '"$W/$N-before.kicad_pro"' in src, "the continuation scores a board copy with no project file beside it"


def t_the_stub_router_checks_that_a_closure_closed_anything():
    """A claimed closure that does not close is worse than a refusal: the finish reads the count, the record
    reads the count, and the board carries a via that touches nothing. A24's /+3V3 was reported as
    "closed: 0 tracks, 1 vias, path 1 cells" in two separate runs and the DRC named the same open pair after
    both, because the search reaches a GOAL CELL, which is the target cluster's copper grown by the search
    margin, and a via dropped in such a cell can touch no copper at all. Every closure is checked against
    KiCad's own connectivity now and taken back off the board when it did not connect (12 September 2026)."""
    src = open(os.path.join(TOOLS, "stub_router.py"), errors="replace").read()
    assert "GetUnconnectedCount" in src, "the stub router does not ask KiCad whether its closure connected anything"
    i = src.index("closed += 1")
    window = src[max(0, i - 1200):i]
    assert "NOT CLOSED" in window and "b.Remove(t)" in window, \
        "a closure that did not connect is still counted as one"


def t_no_post_route_pass_rewrites_a_phase_or_a_stackup_onto_the_silk():
    """The facts on a board's silk belong to the generator that knows them. `silk_fix_all.py` ran in every finish
    AFTER the generators and rewrote each board's title to a stale phase and a stale stackup: A's to "REV A (A18)"
    and "285 x 160 x 1.6 mm FR-4, 4 layers ... 2026-09-04" on a board that is A24, 240 x 160, six layers; B's to
    "REV A (B12)" and "245x170x1.6 4L"; C's to "REV A, C5". A24's routed board carries A18 on its front silk
    because of it, and `verify_deliverable` refuses a deliverable whose silk names another phase, so this cost a
    board its last step after the copper was finished (12 September 2026). D's rule set had already been dropped
    for the same reason on 8 September, which is how the shape of this was recognisable."""
    src = open(os.path.join(TOOLS, "silk_fix_all.py"), errors="replace").read()
    body = src[src.index("RULES = {"):src.index("\nb = pcbnew.LoadBoard")]
    bad = [l for l in body.splitlines()
           if "text=" in l and re.search(r"REV A|\d+\s*x\s*\d+|\d\s*layers|\dL\b", l)]
    assert not bad, "a legend rule writes a phase, a size or a layer count onto the silk: %s" % (bad[0].strip()[:120],)


def t_the_stub_router_reads_its_plane_nets_from_the_board():
    """A net in PLANES takes a different branch: its goal becomes any cell a via may stand in, on the assumption
    that a pour carries the rest of the connection. The set was the hard-coded string "GND,+5V,+3V3,CELL+", and
    A24 has no +3V3 pour, so for /+3V3 the stub router never searched for the other cluster at all. It dropped one
    via beside the source and reported "closed: 0 tracks, 1 vias, path 1 cells", twice, in two separate runs, and
    the DRC named the same open pair after both (12 September 2026). A board's plane nets are a fact about the
    board, and a fact about the board is read from the board."""
    src = open(os.path.join(TOOLS, "stub_router.py"), errors="replace").read()
    i = src.index("PLANES = ")
    body = src[i:i + 600]
    assert "GetFilledArea" in body, "the plane-net set is not read from the board's filled zones"
    assert "_PLANES_ARG" in body, "there is no way to name the plane nets deliberately"


def t_a_via_standing_in_a_pad_of_its_own_net_is_not_dangling():
    """`cleanup_dangling.py` counted the TRACKS touching a via and removed it below two. A via that joins a pad on
    one layer to a track on another has one track and one pad, and it was removed as dangling: A24's /+3V3 via at
    (233.4, 134.9) joined pad C104.1 to a B.Cu track, and the board went from 0 unrouted to 1 in the first ten
    seconds of its finish, after the copper had been closed and measured (12 September 2026). A via in a pad of
    its own net is the whole point of a via in a pad, and the same file already counts a track that merely passes
    OVER a via."""
    src = open(os.path.join(TOOLS, "cleanup_dangling.py"), errors="replace").read()
    i = src.index("n = sum(1 for t in T")
    window = src[i:i + 1400]
    assert "HitTest" in window, "a via's connection count ignores the pads of its own net"
    assert window.index("HitTest") < window.index("if n <= 1"), "the pad is counted after the decision"


def t_a_leg_refusal_says_where_it_was_refused():
    """"the legs clear no smoothing of the centreline" was the largest single failure class on B19 and read the
    same whether the leg was refused in open board or a millimetre from its own pad. Those are different
    findings: 30 of 46 refusals measured on 12 September 2026 were within 2 mm of one of the pair's own pads, at
    J_HDMI, T1 and the pairs' own coupling capacitors, which is a placement answer and not a search one, and the
    only reason it was ever seen is that a knob nobody would remember to set happened to be on. The failure line
    carries the position, the layer, the distance to the pair's nearest own pad and which side of 2 mm it is."""
    src = open(os.path.join(TOOLS, "pair_preroute.py"), errors="replace").read()
    i = src.index("the legs clear no smoothing of the centreline%s")
    window = src[max(0, i - 1400):i]
    assert "at the station" in window and "out in the corridor" in window, \
        "the leg-fit failure does not say whether it was refused at a station or in the corridor"
    assert "_leg_hit[0]" in window, "the failure line does not read the recorded refusal point"


def t_a_nearness_window_carries_the_pads_own_reach():
    """A window measured from a pad's CENTRE misses a pad that is wide (MESHSAT-862, 12 September 2026).

    `escape.py` checks every candidate via against every other pad, and skipped the check entirely when
    the pad's centre was more than a fixed 6 mm away. BT1 on board B is a CR2032 holder whose pad 2 is a
    land many millimetres across, so an escape via three millimetres from its edge sat eight from its
    centre, was never tested, and landed inside the pad: 53 of the 82 hard DRC violations left on B19's
    placed board after the land patterns were corrected. The window carries the pad's own half extent
    now. The rule is general because the mistake is: a proximity test against an extended shape may not
    be short-circuited on the distance to its centre.
    """
    import re as _re
    src = open(os.path.join(TOOLS, "escape.py"), errors="replace").read()
    hits = _re.findall(r"abs\(v\.[xy] - qp\.[xy]\) > ([^:\n]+)", src)
    if not hits:
        raise AssertionError("escape.py no longer has the nearness window this rule guards")
    for h in hits:
        if "qreach" not in h:
            raise AssertionError("escape.py short-circuits a pad test on the distance to the pad CENTRE "
                                 "with no allowance for the pad's own size: %s" % h.strip())


def t_a_margin_against_the_board_is_the_boards_own():
    """`prefanout.py`'s in-pad fallback kept a number typed into the tool (MESHSAT-862, 12 September 2026).

    It placed a via at a pad's centre whenever every other-net pad was at least 0.15 mm away, while board
    B's own hole clearance is 0.19 mm and its minimum clearance 0.127: a via could satisfy the tool and
    fail the DRC, which is 25 of the 45 hard violations left on B19's placed board after the land patterns
    and the escape window were corrected. A margin that is not the board's is a second opinion about the
    board.
    """
    import re as _re
    src = open(os.path.join(TOOLS, "prefanout.py"), errors="replace").read()
    if "m_HoleClearance" not in src or "INPAD_CLR" not in src:
        raise AssertionError("prefanout.py does not read the board's own hole and minimum clearance")
    for m in _re.finditer(r"qr \+ VIA_D / 2 \+ ([A-Za-z_(0-9.)]+)", src):
        if "INPAD_CLR" not in m.group(1):
            raise AssertionError("the in-pad fallback keeps a typed margin from other pads: %s" % m.group(1))


def t_no_via_is_laid_without_a_clearance_test():
    """`escape.py`'s exposed-pad loop added thermal vias unconditionally (MESHSAT-862, 12 September 2026).

    A thermal via sits inside its own exposed pad, so it looked safe. It is a THROUGH via and this board
    is assembled on both sides: it emerges on B.Cu among the underside decoupling and landed on other
    parts' pads, which is 25 of the hard violations on B19's placed board. The same shape as the
    pre-router's six unasked emissions in 32.135: an exemption that is true of the pad is not true of the
    other side of the board. Every via this file lays passes clear() now.
    """
    import re as _re
    src = open(os.path.join(TOOLS, "escape.py"), errors="replace").read()
    body = src.split('"""', 2)[2] if src.count('"""') >= 2 else src
    for m in _re.finditer(r"\n(\s*)via = pcbnew\.PCB_VIA\(b\)", body):
        start = max(0, m.start() - 700)
        window = body[start:m.start()]
        if "clear(" not in window:
            raise AssertionError("escape.py lays a via with no clearance test in the 700 characters before it: "
                                 "...%s" % body[m.start():m.start() + 90].strip())
