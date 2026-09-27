#!/usr/bin/env python3
"""frame_seat.py reads the case set's design numbers; it does not type them (MESHSAT-1357, 27 September 2026).

DRAFT for v2/ecad/tools/tests/test_frame_seat_inputs.py. It lands in the same commit as drafts/hc7/frame_seat.py (to
v2/vendor/peli/frame_seat.py) and drafts/hc7/frame_seat.out (to v2/vendor/peli/1450/frame_seat.out): on the committed frame_seat.py of
a6f87e9d it fails by design, because that file types U51's height (1.6 as an INFERRED class figure; the maker's maximum, which the draft
reads, is the same 1.60, ST DS12117 Rev 9 Table 217) and a six-part hand list of B16's east-end tall parts (which misses the E72 module U14
at 7.76 from the east plugs).

The rules, each a property of the tree:
  * every design name frame_seat.py assigns (the plate, its rebate and holes, the legs, the stack, the connector plate's screws, the RF entry
    plates' screws, the arrestor sites) is either read or equal to v2/ecad/tools/panel1450.py's value, and the board inputs (U51_H, the
    tall list) are never literals (v2/cad/case_geometry_check.py literal_inputs, whose detector test_case_geometry.py proves on fixtures);
  * every worst-case chain that takes a board part's height (U51_H, for M14e and M14g) reads the maker's maximum the board reading carries
    (`height_max`), never the library model's nominal body (case_geometry_check.worst_case_reads; the second review of 27 September 2026
    found the first draft feeding U51's typical 1.50 into both rows);
  * frame_seat.py, run now, prints the recorded frame_seat.out (so a panel1450.py or zstack.json change that moves a margin is caught the day
    it lands, with the record to regenerate and CASE-MARGINS.md to re-read);
  * the pad top and face top that record was computed with are panel1450's.
Nothing here writes anything."""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
V2 = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.join(V2, "cad"))
from harness import need


def t_frame_seat_reads_its_design_numbers():
    import case_geometry_check as C, panel1450 as L
    src = open(need(C.FRAME_SEAT, "frame_seat.py"), encoding="utf-8").read()
    probs = C.literal_inputs(src, L) + C.worst_case_reads(src)
    assert not probs, probs
    assert "import panel1450" in src and "zstack.json" in src, "frame_seat.py names neither panel1450 nor the board reading"


def t_frame_seat_record_is_current_and_on_the_face_basis():
    import case_geometry_check as C, panel1450 as L
    need(C.FRAME_SEAT_OUT, "frame_seat.out")
    probs = C.frame_seat_current() + C.face_basis(open(C.FRAME_SEAT_OUT, encoding="utf-8").read(), L)
    assert not probs, probs


def t_a_drifted_panel1450_moves_the_reading():
    """The reading follows panel1450: a copy of frame_seat.py run against a panel1450 whose screw hole is 0.2 smaller prints a different
    M8f row, so a typed copy of the number could not have hidden the change."""
    import subprocess, tempfile, shutil, case_geometry_check as C
    tmp = tempfile.mkdtemp()
    try:
        for sub in ("vendor/peli", "ecad/tools", "cad"):
            os.makedirs(os.path.join(tmp, "v2", sub), exist_ok=True)
        shutil.copy(C.FRAME_SEAT, os.path.join(tmp, "v2", "vendor", "peli", "frame_seat.py"))
        shutil.copy(os.path.join(V2, "cad", "zstack.json"), os.path.join(tmp, "v2", "cad", "zstack.json"))
        src = open(os.path.join(TOOLS, "panel1450.py"), encoding="utf-8").read()
        assert "FACE_HOLE = 4.6 " in src, "the fixture's anchor moved: panel1450.FACE_HOLE is no longer written as 4.6"
        open(os.path.join(tmp, "v2", "ecad", "tools", "panel1450.py"), "w", encoding="utf-8").write(src.replace("FACE_HOLE = 4.6 ", "FACE_HOLE = 4.4 ", 1))
        got = subprocess.run([sys.executable, os.path.join(tmp, "v2", "vendor", "peli", "frame_seat.py")], capture_output=True, text=True, timeout=120)
        assert got.returncode == 0, got.stderr[-400:]
        rec = [l for l in open(C.FRAME_SEAT_OUT, encoding="utf-8") if l.startswith("  M8f ")]
        new = [l + "\n" for l in got.stdout.splitlines() if l.startswith("  M8f ")]
        assert rec and new and rec != new, "M8f did not move with panel1450.FACE_HOLE: %s / %s" % (rec, new)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
