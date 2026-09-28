"""frame_seat.py reads the QMX lid tray r2's stack (MESHSAT-1357, S-63; branch fnd/w5tray; first drafted 27 September 2026 for the
first pass of the design, recovered and corrected to its second pass the same day). DRAFT for the integrator, to apply AFTER
apply_w5tray.py and after hc7's frame_seat.py draft if that lands first (this script's anchors are the three QMX lines, which that
draft leaves as they are; if one moved, the assertion names it). Run from the root of the integration tree; it edits
v2/vendor/peli/frame_seat.py, re-runs it into v2/vendor/peli/1450/frame_seat.out, prints the rows that changed, and teaches
test_frame_seat_inputs.py's drift fixture to carry the r2 module. Every old text is asserted present and every new text to differ, both
edited Python files are parsed again after they are written, and a second run refuses (its first anchor is gone).

What changes and why: frame_seat.py typed the r1 tray's depth (TRAY = 28.0, from lid_bracket_qmx.py) and counted no lid plate. It
reads the r2 stack instead: M3 becomes the room under the r2 set's retaining frame, its deepest printed face (bond + lid plate + tray
and frame, 32.30 from the ceiling, the depth printed in the label, which v2/cad/lid_tray_qmx_r2_check.py reads back to find the room),
+15.62 nominal, +12.09 at the worst, +9.81 with unstated allowances twice. It stays OPEN, and its note says why: every face part under
the set has its own row in the r2 record (M3r2.<part>, from the solid over the part and the part's read height), and the two knob rows
there are OPEN on the knob's INFERRED height. No row is added, so the 70 rows and their 35 OPEN that the brief, FEA-007 and the case
pages count do not move. M19 reads the set's east edge (171.0, unchanged) from the r2 module.

After it: CASE-MARGINS.md's M3 row and text re-read against the new frame_seat.out, the records bound to frame_seat.out re-read, and
`python3 v2/ecad/tools/tests/run.py case_geometry frame_seat lid_tray_qmx_r2`. THE R2 SET IS NOT TOUCHED: its record prints the room
(47.92, 44.39, 42.11), which is the same before and after this script, so lid-tray-qmx-r2-check.out still equals what the check prints
and the set's MANIFEST.sha256 still holds; its README's table of inputs names frame_seat.out a65c0792, the file it was built with, and
sheet 14r2-1's title block the same. The released case set (v2/release/case-2026-09-27/margins/frame_seat.out) keeps its own copy."""
import subprocess, sys

P = "v2/vendor/peli/frame_seat.py"
OUT = "v2/vendor/peli/1450/frame_seat.out"
s = open(P, encoding="utf-8").read(); s0 = s
assert "import lid_tray_qmx_r2 as QT" not in s, "already applied"


def sub(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:100]); assert a != b
    s = s.replace(a, b)


sub('import panel1450 as P1450                  # not "L": part C and part G use L as a local name\n',
    'import panel1450 as P1450                  # not "L": part C and part G use L as a local name\n'
    'sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cad"))\n'
    'import lid_tray_qmx_r2 as QT               # the QMX lid tray r2 (27 Sep 2026, S-63): its stack from the lid ceiling and its east edge\n')
assert abs(round(0.20 + 2.0 + 30.1, 2) - 32.30) < 1e-9
sub('TRAY = 28.0                                # v2/cad/lid_bracket_qmx.py:13-16\n',
    'TRAY = round(QT.BOND + QT.PLATE_T + QT.Z_TOP, 2)       # 32.30: bond, lid plate, tray and retaining frame (the r1 tray typed 28.0, no plate)\n'
    )
sub('    row("M3", "space under the QMX tray for the face parts (lid STEP 45.47; web 44.45 in the worst)", MIN_MECH, RIM + LID_STEP - TRAY - face_nom,\n'
    '        face_tols + rim_tols + [("lid depth, web page against STEP", LID_STEP - LID_WEB)], open_="parts under the tray: C&K button heights TBD")\n',
    '    row("M3", "space under the QMX tray r2 (%.2f from the ceiling) (lid STEP 45.47; web 44.45 in the worst)" % TRAY, MIN_MECH,\n'
    '        RIM + LID_STEP - TRAY - face_nom, face_tols + rim_tols + [("lid depth, web page against STEP", LID_STEP - LID_WEB)],\n'
    '        open_="each face part under the set: its M3r2 row in the r2 record; the knob rows there are OPEN")\n')
sub('    row("M19", "QMX tray east edge inside the lid\'s flat ceiling (C5)", MIN_MECH, 173.08 - 171.0, [("case per wall", T_WALL)])\n',
    '    row("M19", "QMX tray east edge inside the lid\'s flat ceiling (C5; r2 keeps it)", MIN_MECH, 173.08 - QT.SPAN_X[1], [("case per wall", T_WALL)])\n')
assert s != s0
open(P, "w", encoding="utf-8").write(s)
import ast
ast.parse(open(P, encoding="utf-8").read())
# the drift fixture of test_frame_seat_inputs.py runs a copy of frame_seat.py in a tree of its own: it now needs the r2 module there too
TF = "v2/ecad/tools/tests/test_frame_seat_inputs.py"
tf = open(TF, encoding="utf-8").read()
a = '        shutil.copy(os.path.join(V2, "cad", "zstack.json"), os.path.join(tmp, "v2", "cad", "zstack.json"))\n'
assert tf.count(a) == 1, "the drift fixture's anchor moved"
tf = tf.replace(a, a + '        shutil.copy(os.path.join(V2, "cad", "lid_tray_qmx_r2.py"), os.path.join(tmp, "v2", "cad", "lid_tray_qmx_r2.py"))   # frame_seat.py reads the r2 stack\n')
open(TF, "w", encoding="utf-8").write(tf)
ast.parse(open(TF, encoding="utf-8").read())
before = open(OUT, encoding="utf-8").read().splitlines()
got = subprocess.run([sys.executable, P], capture_output=True, text=True, timeout=120)
assert got.returncode == 0, got.stderr[-400:]
open(OUT, "w", encoding="utf-8").write(got.stdout)
after = got.stdout.splitlines()
for line in after:
    if line not in before: print("new:", line)
for line in before:
    if line not in after: print("old:", line)
m3 = [l for l in after if l.startswith("  M3 ")]
assert len(m3) == 1 and "(32.30 from the ceiling)" in m3[0] and "web 44.45 in the worst)" in m3[0] and "+15.62" in m3[0] and "+12.09" in m3[0] and m3[0].rstrip().count("OPEN") >= 1, m3
assert len(after) == len(before), "a row was added or lost: the 70 rows and 35 OPEN are counted elsewhere"
