#!/usr/bin/env python3
"""The decoupling pass runs on a board its parts are ON, and says so when they are not (20 September 2026).

THE DEFECT. `bypass_place.py`'s own docstring says "It runs after the placement generator and before the
escapes". Boards A and B declared `bypass_place_after: mechanical`, and in `full.sh` that point is after the
OUTLINE generator and before the PLACEMENT generator, so the pass ran on a board with no footprints at all.
Every entry answered "C94 or U18 not on the board" and the summary read `0 moved, 0 already within 3.0 mm,
40 stuck of 40 declared` on every board A and board B chain since the stage was wired in.

WHY IT MATTERED RATHER THAN BEING TIDY. That summary line is the same one a real run prints, so nothing on
any page could tell a pass that measured nothing from a pass that measured a board. Asked of board A's own
placed board the same pass reads **5 within 3.0 mm and 35 STUCK**, at 16.5 mm (C94 to U18 pin 5) up to
139.6 mm (C107 to U26 pin 14). The absence was hiding a finding.

THREE RULES. Two are fixtures and skip where pcbnew is not importable; the third is data and runs everywhere,
which is the one that fails on the tree this file was written against.
"""
import os, sys, json, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARDS = os.path.join(TOOLS, "boards")


def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _fixture(tmp, with_parts):
    """A board with an outline, an intent file declaring one bypass pair, and the two parts or neither."""
    pcbnew = _pcbnew()
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, 40, 0), (40, 0, 40, 30), (40, 30, 0, 30), (0, 30, 0, 0)):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    if with_parts:
        for ref, x, y in (("U1", 10.0, 10.0), ("C1", 25.0, 20.0)):
            fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref)
            fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
            p = pcbnew.PAD(fp); p.SetNumber("1"); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            p.SetShape(pcbnew.PAD_SHAPE_RECT)
            p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(1.0), pcbnew.FromMM(1.0)))
            p.SetPosition(fp.GetPosition()); p.SetLayerSet(pcbnew.LSET.FrontMask())
            fp.Add(p); b.Add(fp)
    path = os.path.join(tmp, "fix.kicad_pcb"); b.Save(path)
    os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
    json.dump({"bypass": [{"cap": "C1", "part": "U1", "pin": "1", "net": "VDD"}]},
              open(os.path.join(tmp, "out", "fix-intent.json"), "w"))
    return path


def _run(path):
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "bypass_place.py"), path],
                       capture_output=True, text=True, timeout=300)
    return p.returncode, p.stdout + p.stderr


def t_a_board_none_of_the_declared_parts_is_on_is_refused():
    """THE DEFECTIVE FIXTURE: the pass is given the board it was given for weeks and must decline."""
    with tempfile.TemporaryDirectory() as tmp:
        rc, out = _run(_fixture(tmp, with_parts=False))
        assert "INCONCLUSIVE" in out, out[-400:]
        assert "after the placement generator" in out, out[-400:]
        assert rc == 3, "a pass that measured nothing must not exit 0 (got %d)" % rc
        assert "stuck of" not in out, "it must not report an absence as a result: %s" % out[-300:]


def t_a_board_the_parts_are_on_is_measured():
    """THE ACCEPTABLE FIXTURE: with both parts on the board the pass measures and reports as it always did."""
    with tempfile.TemporaryDirectory() as tmp:
        rc, out = _run(_fixture(tmp, with_parts=True))
        assert "INCONCLUSIVE" not in out, out[-400:]
        assert "moved" in out and "stuck of" in out, out[-400:]
        assert rc in (0, 1), "a real reading exits 0 or 1 (got %d): %s" % (rc, out[-200:])


def t_no_board_runs_the_decoupling_pass_before_the_placement_generator():
    """THE DATA RULE, and the one that fails on the tree this file was written against.

    `mechanical` is the point in full.sh between the outline generator and the placement generator. A board
    that declares it runs the pass on a board with no footprints, which is not a measurement about anything."""
    bad = []
    for name in sorted(os.listdir(BOARDS)):
        if not name.endswith(".json"): continue
        d = json.load(open(os.path.join(BOARDS, name)))
        if d.get("bypass_place_after") == "mechanical": bad.append(name)
    assert not bad, ("these board files run bypass_place before the placement generator, on a board with no "
                     "footprints: %s" % ", ".join(bad))
