#!/usr/bin/env python3
"""Two rules about how a driver waits and how a tool chooses the board it judges.

Stage 0a and 0d of the control-plane programme (MESHSAT-862, 11 September 2026, v2/docs/CONTROL-PLANE.md).

WAITS. A wait without a deadline makes a job immortal and nothing says so. Twelve finishes and
`finish_b_after.sh` were bounded on 10 September; `long_route.sh` still held one on 11 September, waiting on
any Freerouting process started outside its own flock, and a stray java process would have held it for ever.

BOARD CHOICE. A tool must never learn which board to judge by globbing a project directory. `pcb-b-compute/`
carried `b5m.kicad_pcb`, the 2 September B5 board, beside `pcb-b-compute.kicad_pcb`, and `b5m` sorts FIRST.
A wave script that globbed the directory on 11 September exported a BOM for B from a nine-day-old board and
nothing in its output said which board it had read. The stale file is gone; this rule is what stops the next
one from mattering. A board comes from the board table (`tools/boards/<letter>.json`) or from an argument.
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
