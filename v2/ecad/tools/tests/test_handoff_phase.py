#!/usr/bin/env python3
"""The order set describes the board it ships.

MESHSAT-862, 11 September 2026. `make_handoff.py` carried a hard-coded phase per board, and that phase is what
ORDER-NOTES.txt says while a person places the order. The table had drifted: it named D8 and P1 while the tree
held D9 and P3, so a rebuilt order set would have attached a note describing D8 to D10's gerbers. The order note
is the one artefact of this pipeline that travels to the fab with the board, so a stale one is not cosmetic.

The phase is resolved from the deliverable folders now, and the prose must have been written for the phase it
describes, or the run refuses. These tests drive the real script in a fixture tree, with a stub `pcbnew`, so they
exercise the refusal rather than a copy of its logic.
"""
import os, sys, re, shutil, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _tree(phases, notes_phase, options=True):
    """A fixture tree: v2/ecad/tools/make_handoff.py plus v2/release/revA/boards/<folders>.

    `options=False` is the board with no fabrication-note block at all (E5, the bare dock block): it asserts
    no phase there, so nothing about it can be stale."""
    d = tempfile.mkdtemp(prefix="handoff-phase-")
    tools = os.path.join(d, "v2", "ecad", "tools"); os.makedirs(tools)
    boards = os.path.join(d, "v2", "release", "revA", "boards"); os.makedirs(boards)
    src = open(os.path.join(TOOLS, "make_handoff.py")).read()
    # one board in the table, the D row, with its notes written for `notes_phase`
    row = ('BOARDS = [("meshsat-pcb-d-revA-D8", "pcb-d-aprs", "pcb-d-aprs", "PCB-D APRS", "D8",\n'
           '           "%s is the APRS mezzanine; the SA868 is bench-fitted")]\n'
           'PCB_OPTIONS = %s\n' % (notes_phase,
                                   ('{"pcb-d-aprs": ["FABRICATION NOTES (%s, four layers)", ""]}' % notes_phase)
                                   if options else "{}"))
    # cut the real PCB_OPTIONS first, only as far as the resolver: cutting after the row was inserted would
    # delete the fixture's own PCB_OPTIONS, and cutting past the marker would delete the code under test
    src = re.sub(r"^PCB_OPTIONS = \{.*?^# -+ the table against the tree",
                 "# ----- the table against the tree", src, count=1, flags=re.S | re.M)
    src = re.sub(r"^BOARDS = \[.*?^\]\n", row, src, count=1, flags=re.S | re.M)
    open(os.path.join(tools, "make_handoff.py"), "w").write(src)
    for ph in phases:
        f = os.path.join(boards, "meshsat-pcb-d-revA-%s" % ph); os.makedirs(f)
        open(os.path.join(f, "pcb-d-aprs-gerbers.zip"), "w").write("x")
        open(os.path.join(f, "pcb-d-aprs-bom.status"), "w").write("OK\n")
    stub = os.path.join(d, "stub"); os.makedirs(stub)
    open(os.path.join(stub, "pcbnew.py"), "w").write("def LoadBoard(*a, **k): raise SystemExit('fixture: no board')\n")
    return d, tools, stub


def _run(phases, notes_phase, options=True):
    d, tools, stub = _tree(phases, notes_phase, options)
    env = dict(os.environ, PYTHONPATH=stub)
    r = subprocess.run([sys.executable, os.path.join(tools, "make_handoff.py")], capture_output=True, text=True, env=env, cwd=d)
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, r.stdout + r.stderr


def t_a_newer_deliverable_with_stale_notes_is_refused():
    rc, out = _run(["D8", "D9", "D10"], "D8")
    assert rc != 0, out
    assert "newest D deliverable is D10" in out, out
    assert "D8 notes to D10 gerbers" in out or "attach D8 notes" in out, out


def t_a_newer_deliverable_with_its_own_notes_is_taken():
    rc, out = _run(["D8", "D9", "D10"], "D10")
    assert "advanced D8 -> D10" in out, out
    assert "the newest D deliverable is" not in out, out


def t_the_phase_order_is_numeric_not_alphabetic():
    """D10 sorts before D8 as text. Sorting the folders as strings would have called D9 the newest and shipped
    the board before the current one."""
    rc, out = _run(["D8", "D9", "D10"], "D9")
    assert "newest D deliverable is D10" in out, out


def t_the_table_matching_the_tree_says_nothing():
    rc, out = _run(["D8"], "D8")
    assert "advanced" not in out, out
    assert "does not describe" not in out, out


# ---------------------------------------------------------------- the other face of the same defect (19 Sep 2026)
# The four rules above all drive the ADVANCE path: the table has fallen behind the tree. The guard's condition
# made that a hypothesis about how prose goes stale, because `if seen[-1] == phase: return` returned before any
# prose was read. A board whose table entry already named the tree's newest folder was therefore never asked
# whether its own notes did, and three of the seven did not: the fabrication section opened `(D10, ...)` above
# D11 gerbers, `(E7, ...)` above E9 and `(P3, ...)` above P4. These two run the SAME tree with the SAME phase
# on both sides and differ only in what the prose says, so nothing but the prose can decide them.

def t_a_note_written_for_another_phase_is_refused_when_the_phase_did_not_advance():
    """THE DEFECTIVE FIXTURE. Table D8, tree D8, notes written for D7: expected verdict FAIL."""
    rc, out = _run(["D8"], "D7")
    assert rc != 0, out
    assert "board D ships D8" in out, out
    assert "does not describe D8" in out, out


def t_a_note_written_for_its_own_phase_is_taken_when_the_phase_did_not_advance():
    """THE ACCEPTABLE FIXTURE. The same tree with the notes written for D8: expected verdict PASS."""
    rc, out = _run(["D8"], "D8")
    assert "ships D8" not in out, out
    assert "Update" not in out, out


def t_a_board_with_no_fabrication_note_block_is_not_refused_for_saying_nothing():
    """Board E5 is a bare block and has no PCB_OPTIONS entry. A text that does not exist asserts no phase, so
    it cannot be stale; the hand-fitted list still carries the claim and is still checked."""
    rc, out = _run(["D8"], "D8", options=False)
    assert "PCB_OPTIONS" not in out, out
    rc, out = _run(["D8"], "D7", options=False)
    assert rc != 0, out
    assert "the hand-fitted list does not describe D8" in out, out


def t_every_committed_board_row_resolves_against_this_tree():
    """THE RULE ON THE REAL TABLE, not on a fixture. The two rules above prove the guard fires; this one asks
    whether it fires TODAY, on the seven rows and the seven deliverable folders this repo actually holds. Board
    C's row said C17 while the tree held C24 from the day C24 was cut, so the order set has refused to rebuild
    since, and nobody would have known until somebody ran it. It reads the declarations and the resolver out of
    the real file with `pcbnew` stubbed, because the resolver needs no board."""
    import harness
    src = open(os.path.join(TOOLS, "make_handoff.py"), encoding="utf-8").read()
    # NEVER PUT A STUB IN sys.modules FROM A TEST (19 September 2026, caught within the hour): the first
    # version of this rule installed a fake `pcbnew` so the slice would import, and every later test in the
    # same process that decides to SKIP by trying `import pcbnew` then believed KiCad was present and ran
    # against the stub. Three rules that had skipped all week failed instead. The import is removed from the
    # slice, which needs no module at all, and the process is left as it was found.
    lines = src.splitlines(True)
    hit = [i for i, l in enumerate(lines) if l.startswith("import ") and "pcbnew" in l]
    assert hit, "make_handoff no longer imports pcbnew on an import line; this rule strips it from the slice"
    lines[hit[0]] = lines[hit[0]].replace(", pcbnew", "").replace("import pcbnew\n", "\n")
    src = "".join(lines)
    ns = {"__name__": "mh_probe", "__file__": os.path.join(TOOLS, "make_handoff.py")}
    exec(compile(src[:src.index("def _rows(rows):")], "make_handoff.py", "exec"), ns)
    if not os.path.isdir(ns["DL"]): raise harness.Skip("no deliverable folders in this tree")
    bad = []
    for f, stem, prj, title, ph, hand in ns["BOARDS"]:
        try:
            ns["_resolve"](f, prj, ph, hand)
        except SystemExit as e:
            bad.append(str(e).splitlines()[0])
    assert not bad, ("the order set cannot be rebuilt from this tree: %s" % " | ".join(bad))
