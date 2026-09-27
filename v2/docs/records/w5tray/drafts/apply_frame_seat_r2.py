"""frame_seat.py reads the QMX lid tray r2's stack (MESHSAT-1357, 27 September 2026, S-63; worktree fnd/w5tray). DRAFT for the
integrator (it also teaches test_frame_seat_inputs.py's drift fixture to carry the r2 module), to apply AFTER apply_w5tray.py and after hc7's frame_seat.py draft if that lands first (this script's anchors are the three
QMX lines, which that draft leaves as they are; if one moved, the assertion names it). Run from the worktree root; it edits
v2/vendor/peli/frame_seat.py, then re-runs it into v2/vendor/peli/1450/frame_seat.out and prints the rows that changed.

What changes and why: frame_seat.py typed the r1 tray's depth (TRAY = 28.0, from lid_bracket_qmx.py) and counted no lid plate. It
reads the r2 stack instead: M3 becomes the room under the r2 tray's open face (bond + lid plate + tray, 31.30 from the ceiling, the
depth printed in the label, which v2/cad/lid_tray_qmx_r2_check.py reads back), still OPEN on the button caps, its note naming the
knob tips' row M3r2k of the r2 record (kept there, not added here, so the 70 rows and their 35 OPEN that the brief, FEA-007 and the
case pages count do not move), and M19 reads the tray's east edge (171.0, unchanged) from the r2 module. After it: CASE-MARGINS.md's M3 row and text re-read against the new frame_seat.out (the r2
record's M3r2a is the same number), the records bound to frame_seat.out re-read, and `python3 v2/ecad/tools/tests/run.py case_geometry
frame_seat lid_tray_qmx_r2`. The released case set (v2/release/case-2026-09-27/margins/frame_seat.out) keeps its own copy."""
import subprocess, sys

P = "v2/vendor/peli/frame_seat.py"
OUT = "v2/vendor/peli/1450/frame_seat.out"
s = open(P, encoding="utf-8").read(); s0 = s


def sub(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:100]); assert a != b
    s = s.replace(a, b)


sub('import panel1450 as P1450                  # not "L": part C and part G use L as a local name\n',
    'import panel1450 as P1450                  # not "L": part C and part G use L as a local name\n'
    'sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cad"))\n'
    'import lid_tray_qmx_r2 as QT               # the QMX lid tray r2 (27 Sep 2026, S-63): its stack from the lid ceiling and its east edge\n')
sub('TRAY = 28.0                                # v2/cad/lid_bracket_qmx.py:13-16\n',
    'TRAY = round(QT.BOND + QT.PLATE_T + QT.Z_TOP, 2)       # 31.30: bond, lid plate and tray to its open face (the r1 tray typed 28.0, no plate)\n'
    )
sub('    row("M3", "space under the QMX tray for the face parts (lid STEP 45.47; web 44.45 in the worst)", MIN_MECH, RIM + LID_STEP - TRAY - face_nom,\n'
    '        face_tols + rim_tols + [("lid depth, web page against STEP", LID_STEP - LID_WEB)], open_="parts under the tray: C&K button heights TBD")\n',
    '    row("M3", "space under the QMX tray r2 (%.2f from the ceiling) for the face parts (lid STEP 45.47; web 44.45 in the worst)" % TRAY, MIN_MECH,\n'
    '        RIM + LID_STEP - TRAY - face_nom, face_tols + rim_tols + [("lid depth, web page against STEP", LID_STEP - LID_WEB)],\n'
    '        open_="parts under the tray: C&K button heights TBD; the QMX knob tips: M3r2k of the r2 record")\n')
sub('    row("M19", "QMX tray east edge inside the lid\'s flat ceiling (C5)", MIN_MECH, 173.08 - 171.0, [("case per wall", T_WALL)])\n',
    '    row("M19", "QMX tray east edge inside the lid\'s flat ceiling (C5; r2 keeps it)", MIN_MECH, 173.08 - QT.SPAN_X[1], [("case per wall", T_WALL)])\n')
open(P, "w", encoding="utf-8").write(s)
# the drift fixture of test_frame_seat_inputs.py runs a copy of frame_seat.py in a tree of its own: it now needs the r2 module there too
TF = "v2/ecad/tools/tests/test_frame_seat_inputs.py"
tf = open(TF, encoding="utf-8").read()
a = '        shutil.copy(os.path.join(V2, "cad", "zstack.json"), os.path.join(tmp, "v2", "cad", "zstack.json"))\n'
assert tf.count(a) == 1, "the drift fixture's anchor moved"
tf = tf.replace(a, a + '        shutil.copy(os.path.join(V2, "cad", "lid_tray_qmx_r2.py"), os.path.join(tmp, "v2", "cad", "lid_tray_qmx_r2.py"))   # frame_seat.py reads the r2 stack\n')
open(TF, "w", encoding="utf-8").write(tf)
before = open(OUT, encoding="utf-8").read().splitlines()
got = subprocess.run([sys.executable, P], capture_output=True, text=True, timeout=120)
assert got.returncode == 0, got.stderr[-400:]
open(OUT, "w", encoding="utf-8").write(got.stdout)
after = got.stdout.splitlines()
for line in after:
    if line not in before: print("new:", line)
for line in before:
    if line not in after: print("old:", line)
