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


def _tree(phases, notes_phase):
    """A fixture tree: v2/ecad/tools/make_handoff.py plus v2/release/revA/boards/<folders>."""
    d = tempfile.mkdtemp(prefix="handoff-phase-")
    tools = os.path.join(d, "v2", "ecad", "tools"); os.makedirs(tools)
    boards = os.path.join(d, "v2", "release", "revA", "boards"); os.makedirs(boards)
    src = open(os.path.join(TOOLS, "make_handoff.py")).read()
    # one board in the table, the D row, with its notes written for `notes_phase`
    row = ('BOARDS = [("meshsat-pcb-d-revA-D8", "pcb-d-aprs", "pcb-d-aprs", "PCB-D APRS", "D8",\n'
           '           "%s is the APRS mezzanine; the SA868 is bench-fitted")]\n'
           'PCB_OPTIONS = {"pcb-d-aprs": ["FABRICATION NOTES (%s, four layers)", ""]}\n' % (notes_phase, notes_phase))
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


def _run(phases, notes_phase):
    d, tools, stub = _tree(phases, notes_phase)
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
