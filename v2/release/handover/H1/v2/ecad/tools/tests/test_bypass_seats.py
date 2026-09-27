#!/usr/bin/env python3
"""Where a declared decoupling capacitor could sit: two fixtures and two mechanical rules.

`bypass_seats.py` is a REPORT (appendix 32.311). It exists because the reservation pass has never reserved a
slot on any board of the set, so every board's declared capacitors are wherever the packer had room: board
A's were 13.2 to 44.5 mm from the pins they serve and board B's up to 251.9. The tool prints the seat line a
generator's FIXED table would carry, measured outside every courtyard, escape fan, part-forbidding rule
area, packer region rectangle and the board edge.

THE DEFECTIVE FIXTURE is a board whose only space near the pin is inside an escape fan: the tool must offer
no seat and say so, because a seat inside a fan costs that part its escapes (9 September: D10's U7 lost six
of seventeen). THE ACCEPTABLE FIXTURE is the same board with the fine-pitch part replaced by a two-pad one,
where the seat exists and must be found.

The two mechanical rules are about the traps this tool was written around: a probe that carries another
board's case frame prints numbers for a board nobody is building, and a report with no declaration must not
pass on a denominator of zero.
"""
import os, sys, json, tempfile, subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import Skip, block

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _pcbnew():
    try:
        import pcbnew; return pcbnew
    except Exception as e:
        raise Skip("no pcbnew here (%s)" % type(e).__name__)


def _fixture(tmp, fine):
    """A board with one part, one capacitor 20 mm away, and either a fine-pitch part or a two-pad one."""
    pcbnew = _pcbnew()
    b = pcbnew.BOARD(); b.SetCopperLayerCount(2)
    for (x1, y1, x2, y2) in ((0, 0, 60, 0), (60, 0, 60, 40), (60, 40, 0, 40), (0, 40, 0, 0)):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
        s.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
        s.SetWidth(pcbnew.FromMM(0.1)); b.Add(s)
    def part(ref, x, y, pads):
        fp = pcbnew.FOOTPRINT(b); fp.SetReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        for i, (dx, dy) in enumerate(pads, 1):
            p = pcbnew.PAD(fp); p.SetNumber(str(i)); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            p.SetShape(pcbnew.PAD_SHAPE_RECT)
            p.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.3), pcbnew.FromMM(0.3)))
            p.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x + dx), pcbnew.FromMM(y + dy)))
            p.SetLayerSet(pcbnew.LSET.FrontMask()); fp.Add(p)
        b.Add(fp); return fp
    if fine:   # ten pads on a 0.5 mm pitch: _needs_fan says yes and its fan is closed to a seat
        part("U1", 10.0, 20.0, [(i * 0.5 - 2.25, -1.0) for i in range(10)] + [(i * 0.5 - 2.25, 1.0) for i in range(10)])
    else:
        part("U1", 10.0, 20.0, [(-1.0, 0.0), (1.0, 0.0)])
    part("C1", 30.0, 20.0, [(-0.5, 0.0), (0.5, 0.0)])
    path = os.path.join(tmp, "fix.kicad_pcb"); b.Save(path)
    os.makedirs(os.path.join(tmp, "out"), exist_ok=True)
    json.dump({"bypass": [{"cap": "C1", "part": "U1", "pin": "1", "net": "VDD"}]},
              open(os.path.join(tmp, "out", "fix-intent.json"), "w"))
    return path


def _run(path, extra=()):
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "bypass_seats.py"), path, "--board", "x",
                        "--frame", "0,0"] + list(extra),
                       capture_output=True, text=True, timeout=300,
                       env=dict(os.environ, VERDICT_DIR=os.path.join(os.path.dirname(path), "vd")))
    return p.returncode, p.stdout + p.stderr


def t_a_seat_inside_an_escape_fan_is_not_offered():
    """THE DEFECTIVE FIXTURE: the only room near the pin belongs to the part's own fan."""
    with tempfile.TemporaryDirectory() as tmp:
        # 21 September 2026: at a 3.0 mm reach the corrected fan box (c18d936b, built from the courtyard edges) leaves
        # a legal seat 2.98 mm from the pin OUTSIDE the fan, which is decision 42's own arithmetic, so the fixture
        # was no longer defective and the box suite said so; at 2.5 mm the fan alone forbids every seat.
        rc, out = _run(_fixture(tmp, fine=True), ("--reach", "2.5"))
        assert "1 declared" in out, out[-400:]
        assert "no seat within" in out, "a seat inside the fan was offered: %s" % out[-400:]
        assert "0 seat(s) offered" in out, out[-300:]


def t_a_seat_that_exists_is_found():
    """THE ACCEPTABLE FIXTURE: the same board with a two-pad part, where the room is real."""
    with tempfile.TemporaryDirectory() as tmp:
        rc, out = _run(_fixture(tmp, fine=False))
        assert "1 declared" in out, out[-400:]
        assert '"C1"' in out, "no seat offered where one exists: %s" % out[-400:]
        assert "1 seat(s) offered" in out, out[-300:]


def t_the_case_frame_is_read_and_never_assumed():
    """A probe written for board A and pointed at board C prints board A's frame: (150, 110) against (297, 210).

    Asked of the CODE rather than of the prose: the frame reader must look the generator up by the board's
    letter and must have a branch for not finding one. The first version of this rule asserted that no "150"
    appeared in the function and failed on its own docstring, which is a rule about wording."""
    src = open(os.path.join(TOOLS, "bypass_seats.py"), errors="replace").read()
    body = block(src, "def _frame(")
    code = "\n".join(l for l in body.splitlines() if not l.strip().startswith("#"))
    code = code.split('"""')[0] + "".join(code.split('"""')[2:]) if code.count('"""') >= 2 else code
    assert "gen_pcb_" in code and "% letter" in code, "the frame is not looked up by the board's letter"
    assert "re.search" in code, "the frame is not read out of the generator"
    assert "no frame found" in body, "a tool that cannot find the frame must say so, not assume one"


def t_no_declaration_is_inconclusive_and_never_a_pass():
    """A board whose intent file is not there must not read as a board with nothing to declare."""
    src = open(os.path.join(TOOLS, "bypass_seats.py"), errors="replace").read()
    body = block(src, "def main(")
    i = body.find('if not r["declared"]')
    assert i > 0, "main() does not handle a board with no declared capacitor"
    seg = block(body[i:], 'if not r["declared"]', stops=("\n    r ", "\n    print(", "\n    if ", "\n    for "))
    seg = seg or body[i:]
    assert "INCONCLUSIVE" in seg and "missing_input" in seg, "no declaration must be INCONCLUSIVE with its input named"
