#!/usr/bin/env python3
"""The case geometry stays one geometry (MESHSAT-1357, 27 September 2026).

The case set of v2/release/case-2026-09-27/ is generated from one source, v2/ecad/tools/panel1450.py, and from one reading of the committed
boards, v2/cad/zstack.json (v2/cad/zstack.py). Its margins are computed by v2/vendor/peli/frame_seat.py. Until this day the three drifted
apart silently: panel1450 coded a face 5.12 mm lower than the one the margins were computed for, and its list of board B's tall parts, typed
from a floor plan of 9 September, missed the E22/E72/LG290P modules and slot 1's M.2 cards and held J_ETH and nine pin headers under
envelopes shorter than their parts. Each rule here states a property of the tree and is shown refusing a defective copy
(v2/cad/case_geometry_check.py does the reading; nothing here writes anything):

  * the board reading names each board by sha256, and every one is still the committed file;
  * panel1450's stack thicknesses and board outlines are the board files' own;
  * every part 3.0 mm or taller on board B's top lies under a face-gate envelope at least as tall, and every part with no height under one;
  * the pad top and the face top frame_seat.out was computed with are panel1450's;
  * frame_seat.py, run now, prints the recorded frame_seat.out;
  * a case release folder is an immutable copy: its files still carry the sha256 its MANIFEST names;
  * the detector for typed design numbers in frame_seat.py refuses a drifted literal and passes a read one (the rule on the real file goes
    with the frame_seat.py draft of the same day, drafts/hc7/test_frame_seat_inputs.py, because the committed file types two of them);
  * panel1450 without the board reading refuses: importing it still works (the generators and the CAD need no board reading), but
    B16_TALL, B16_FROM_BOARD and clearance_report() raise ZstackMissing, so board C's gate crashes to INCONCLUSIVE instead of passing on
    the module envelopes alone (the second review of 27 September 2026 found the first loader falling back to 8 envelopes of 59);
  * a maker's maximum height on a board part (zstack.py MAKER_MAX) is read for that part's body, and a worst-case chain of frame_seat.py
    takes it, never the library model's nominal height (the same review: the draft had fed U51's typical 1.50 into M14e and M14g);
  * the QMX lid tray is a released made part like the others: panel1450.QMX_TRAY_X spans the part's own width, its place along Y spans
    the part's length over its tabs, and the release carries its STEP, STL and sheet (the second review of the case release found the
    tray undrawn; the fixer c7 added it the same day). Importing lid_bracket_qmx builds nothing, so this runs without the CAD set.
"""
import os, sys, json, copy, tempfile, hashlib, shutil, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
V2 = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.join(V2, "cad"))
from harness import need


def _z():
    return json.load(open(need(os.path.join(V2, "cad", "zstack.json"), "the board reading"), encoding="utf-8"))


def t_zstack_names_the_committed_boards():
    import case_geometry_check as C
    z = _z()
    for k, b in z["boards"].items(): need(os.path.join(os.path.dirname(V2), b["file"]), "board %s" % k)
    probs = C.board_identity(z)
    assert not probs, probs
    bad = copy.deepcopy(z); bad["boards"]["b"]["sha256"] = "0" * 64
    assert C.board_identity(bad) and "b:" in C.board_identity(bad)[0], "a reading of another board B passed"


def t_stack_and_outlines_are_the_boards():
    import case_geometry_check as C, panel1450 as L
    z = _z()
    probs = C.stack_and_outlines(z, L)
    assert not probs, probs
    bad = copy.deepcopy(z); bad["boards"]["a"]["thickness"] = 2.0; bad["boards"]["e"]["outline"] = [-133.5, -113.0, 133.5, -45.0]
    got = C.stack_and_outlines(bad, L)
    assert any(p.startswith("board A:") for p in got) and any(p.startswith("board e outline") for p in got), got


def t_face_gates_cover_board_b():
    import case_geometry_check as C, panel1450 as L
    z = _z()
    assert L.B16_FROM_BOARD and L.B16_FROM_BOARD["sha256"] == z["boards"]["b"]["sha256"], "panel1450.B16_TALL is not the board reading"
    probs = C.b16_coverage(z, L.B16_TALL)
    assert not probs, probs
    short = [(r, h, n) for r, h, n in L.B16_TALL if not n.startswith("J_ETH")]
    got = C.b16_coverage(z, short)
    assert any(p.startswith("J_ETH") for p in got), "an envelope list without J_ETH passed: %s" % got[:3]
    legacy = [((-162.0, 81.0, -142.0, 98.0), 14.0, "J_ETH RJ45")] + [(r, h, n) for r, h, n in L.B16_TALL if not n.startswith("J_ETH")]
    got = C.b16_coverage(z, legacy)
    assert any(p.startswith("J_ETH") and "taller" in p for p in got), "J_ETH under the 9 Sep 14.0 envelope passed: %s" % got[:3]


def t_face_basis_is_the_margins_basis():
    import case_geometry_check as C, panel1450 as L
    out = open(need(C.FRAME_SEAT_OUT, "frame_seat.out"), encoding="utf-8").read()
    probs = C.face_basis(out, L)
    assert not probs, probs
    old = "  pad top 93.53 = shoulder 101.04 + ...\n  face top 101.40 nominal, 99.65 .. 103.15 on the legs\n"
    got = C.face_basis(old, L)
    assert len(got) == 2, "a margin reading on the superseded face passed: %s" % got


def t_frame_seat_prints_its_record():
    import case_geometry_check as C
    need(C.FRAME_SEAT, "frame_seat.py"); need(C.FRAME_SEAT_OUT, "frame_seat.out")
    probs = C.frame_seat_current()
    assert not probs, probs


def t_release_folder_is_immutable():
    import case_geometry_check as C
    d = tempfile.mkdtemp()
    open(os.path.join(d, "a.txt"), "w").write("plate 377.2\n")
    h = hashlib.sha256(open(os.path.join(d, "a.txt"), "rb").read()).hexdigest()
    open(os.path.join(d, "MANIFEST.sha256"), "w").write("# test\n%s  a.txt\n" % h)
    assert not C.manifest(d), C.manifest(d)
    open(os.path.join(d, "a.txt"), "w").write("plate 365.5\n")
    assert C.manifest(d) == ["a.txt: changed since the release"], C.manifest(d)
    rel = os.path.join(V2, "release", "case-2026-09-27")
    if os.path.isdir(rel):
        probs = C.manifest(rel)
        assert not probs, probs


def t_typed_design_numbers_are_found():
    import case_geometry_check as C, panel1450 as L
    drifted = "PLATE = (365.5, 249.5, 3.0)\nU51_H = 1.6\nB_TOP = 49.5 + 1.1\n"
    got = C.literal_inputs(drifted, L)
    assert any(p.startswith("PLATE typed") for p in got) and any(p.startswith("U51_H is typed") for p in got), got
    assert not any(p.startswith("B_TOP") for p in got), "B_TOP 49.5 + 1.1 equals panel1450's 50.6 and was refused: %s" % got
    read = "PLATE = P1450.PLATE\nU51_H = _part('b', 'U51')['height_max']\ntall = [r for r in P1450.B16_TALL]\n"
    assert not C.literal_inputs(read, L), C.literal_inputs(read, L)


def t_a_worst_case_chain_takes_the_makers_maximum():
    import case_geometry_check as C
    nominal = "U51_H = _part('b', 'U51')['height']\n"
    got = C.worst_case_reads(nominal)
    assert got and got[0].startswith("U51_H reads ['height']"), "a worst-case chain on the model's nominal body passed: %s" % got
    assert C.worst_case_reads("U51_H = 1.6\n"), "a typed U51_H passed the worst-case read rule"
    assert not C.worst_case_reads("U51_H = _part('b', 'U51')['height_max']\n"), C.worst_case_reads("U51_H = _part('b', 'U51')['height_max']\n")


def t_a_makers_maximum_is_read_for_its_part():
    import case_geometry_check as C
    z = _z()
    probs = C.maker_maxima(z)
    assert not probs, probs
    u51 = [p for p in z["boards"]["b"]["parts"] if p["ref"] == "U51"]
    assert len(u51) == 1 and u51[0]["height_max"] == 1.60 and u51[0]["height_typ"] == 1.50 and "DS12117" in u51[0]["height_max_source"], \
        "board B's U51 carries no maker's maximum from ST's sheet: %s" % u51
    bad = copy.deepcopy(z)
    q = [p for p in bad["boards"]["b"]["parts"] if p["ref"] == "U51"][0]
    q["height"] = 1.40
    assert any("U51" in x and "another body" in x for x in C.maker_maxima(bad)), "a maximum on a body the sheet does not describe passed"
    q["height"] = 1.50; q["height_max_source"] = "a sheet (v2/vendor/st/no-such-sheet.pdf)"
    assert any("U51" in x and "names no file" in x for x in C.maker_maxima(bad)), "a maximum whose source is not in the tree passed"


def _panel1450_in(tmp, zstack):
    """A copy of panel1450.py in a tree of its own, with `zstack` (None, or the text of v2/cad/zstack.json) beside it; returns the tools dir."""
    tools = os.path.join(tmp, "v2", "ecad", "tools"); os.makedirs(tools); os.makedirs(os.path.join(tmp, "v2", "cad"))
    shutil.copy(os.path.join(TOOLS, "panel1450.py"), tools)
    if zstack is not None:
        open(os.path.join(tmp, "v2", "cad", "zstack.json"), "w", encoding="utf-8").write(zstack)
    return tools


_PROBE = r"""
import sys, json
sys.path.insert(0, sys.argv[1])
import panel1450 as L
out = {"imported": True, "plate": list(L.PLATE)}
for what, f in (("tall", lambda: len(L.B16_TALL)), ("from", lambda: L.B16_FROM_BOARD["zstack_sha256_16"]), ("report", lambda: len(L.clearance_report()))):
    try: out[what] = f()
    except L.ZstackMissing as e: out[what] = "ZstackMissing"
    except Exception as e: out[what] = "OTHER " + e.__class__.__name__
print(json.dumps(out))
"""


def _probe(tools):
    r = subprocess.run([sys.executable, "-c", _PROBE, tools], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-400:]
    return json.loads(r.stdout.strip().splitlines()[-1])


def t_panel1450_without_the_board_reading_refuses_and_never_falls_back():
    z = open(need(os.path.join(V2, "cad", "zstack.json"), "the board reading"), encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="p1450-")
    try:
        got = _probe(_panel1450_in(os.path.join(tmp, "absent"), None))
        assert got["imported"] and got["plate"], got
        assert got["tall"] == got["from"] == got["report"] == "ZstackMissing", "panel1450 without zstack.json gave a list: %s" % got
        mods = json.loads(z); mods["b16_envelopes"] = [e for e in mods["b16_envelopes"] if e["name"].startswith(("CM5", "LimeSDR", "RockBLOCK"))]
        got = _probe(_panel1450_in(os.path.join(tmp, "modules"), json.dumps(mods)))
        assert got["tall"] == "ZstackMissing", "a reading of the module envelopes alone was taken as the board's: %s" % got
        got = _probe(_panel1450_in(os.path.join(tmp, "broken"), z[: len(z) // 2]))
        assert got["tall"] == "ZstackMissing", "a truncated reading was taken: %s" % got
        got = _probe(_panel1450_in(os.path.join(tmp, "whole"), z))
        assert got["tall"] == len(json.loads(z)["b16_envelopes"]) and got["from"] == hashlib.sha256(z.encode("utf-8")).hexdigest()[:16], got
        assert isinstance(got["report"], int) and got["report"] > 0, got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


TRAY_FILES = ("lid-tray-qmx/lid-bracket-qmx.step", "lid-tray-qmx/lid-bracket-qmx.stl", "drawings/lid-tray-qmx-drawing.pdf")


def _tray_missing(manifest_text):
    names = {ln.split()[1] for ln in manifest_text.splitlines() if ln.strip() and not ln.startswith("#")}
    return [f for f in TRAY_FILES if f not in names]


def t_the_qmx_lid_tray_is_released_at_its_place():
    import panel1450 as L
    import lid_bracket_qmx as Q
    x0, x1 = L.QMX_TRAY_X
    assert abs((x1 - x0) - Q.OL) < 1e-9, "QMX_TRAY_X %s does not span the tray's width %.1f" % (L.QMX_TRAY_X, Q.OL)
    assert abs((Q.PLACE_Y[1] - Q.PLACE_Y[0]) - Q.LENGTH_OVER_TABS) < 1e-9, (Q.PLACE_Y, Q.LENGTH_OVER_TABS)
    assert len(Q.HOLE_CENTRES) == 4 and len({(abs(x), abs(y)) for x, y in Q.HOLE_CENTRES}) == 1, "the tab holes are no longer one symmetric pattern"
    # the defective copy: the release of the second build, which drew every made part but the tray
    old = "# test\n" + "".join("%s  %s\n" % ("0" * 64, f) for f in ("face-plate/face-plate.step", "drawings/case-drawings-2-to-13.pdf"))
    assert _tray_missing(old) == list(TRAY_FILES), _tray_missing(old)
    rel = os.path.join(V2, "release", "case-2026-09-27")
    if os.path.isdir(rel):
        got = _tray_missing(open(os.path.join(rel, "MANIFEST.sha256"), encoding="utf-8").read())
        assert not got, "the case release does not carry %s" % got
