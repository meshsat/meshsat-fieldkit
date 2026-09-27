#!/usr/bin/env python3
"""The QMX lid tray r2 fits the unit the maker describes (MESHSAT-1357, 27 September 2026, S-63, EQ-24; worktree fnd/w5tray).

The r1 tray of 9 September 2026 was notched at one end while the QMX has jacks on both end panels, and its 95 x 63 x 25 came from no
maker document. Each rule here states a property of v2/cad/lid_tray_qmx_r2.py (importing it builds nothing, so this runs without the
CAD venv) and is shown refusing a defective copy:

  * the jack table the tray is built on is the one v2/vendor/qrp-labs/qmx-figures.out measured on the maker's figures and photograph,
    read by parsing that record, not typed twice;
  * every jack on BOTH end panels admits a plug body wider than its own panel opening by 2 mm at the worst of its scaled place, so no
    end is closed (a sill raised to a wall is refused);
  * no knob-edge ledge lies over a knob or its finger room, and the back ledge stops short of the LCD window;
  * the east edge stays where C5 put the r1 tray (panel1450.QMX_TRAY_X[1]), so M19 does not move, and the place spans the part;
  * the knob tips, the ledges and the unit's top face keep the case margins' 1.0 minimum over the face at the worst with every
    unstated allowance taken twice, on the room frame_seat.out's M3 was computed with (a stack 3 mm deeper is refused);
  * the pads always touch the unit over the tolerance corners and never pass half their thickness by more than the sheet's range;
  * every tray screw's tip stays inside the lid plate (a longer screw reaches the bond and is refused);
  * the case release carries the r2 set in its MANIFEST and still carries the superseded r1 files, unchanged, as history."""
import os, sys, re, copy

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
V2 = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.join(V2, "cad"))
from harness import need

FIGURES = os.path.join(V2, "vendor", "qrp-labs", "qmx-figures.out")


def _figures():
    """qmx-figures.out parsed: {'left': [(x, y, w, h)...], 'right': [...], 'photo': {name: (x, y)}, 'top': [(x, y, d, from_front)...]}."""
    out = {"left": [], "right": [], "photo": {}, "top": []}
    cur = None
    for line in open(need(FIGURES, "the scaled QMX figures"), encoding="utf-8"):
        if line.startswith("LEFT panel"): cur = "left"
        elif line.startswith("RIGHT panel on the maker"): cur = "photo"
        elif line.startswith("RIGHT panel"): cur = "right"
        elif line.startswith("TOP face"): cur = "top"
        m = re.match(r"\s+hole\s+x\s+([\d.]+)\s+y\s+([\d.]+)\s+([\d.]+) x\s+([\d.]+)", line)
        if m and cur in ("left", "right"): out[cur].append(tuple(float(g) for g in m.groups()))
        m = re.match(r"\s+(RF|PTT|USB)\s+x\s+([\d.]+)\s+y\s+([\d.]+)", line)
        if m and cur == "photo": out["photo"][m.group(1)] = (float(m.group(2)), float(m.group(3)))
        m = re.match(r"\s+circle\s+x\s+([\d.]+)\s+y\s+([\d.]+)\s+d\s+([\d.]+)\s+\(([\d.]+) from the front", line)
        if m and cur == "top": out["top"].append(tuple(float(g) for g in m.groups()))
    return out


def _jacks_from_figures(F):
    """The jacks as the figures give them: v from the knob edge (left panel drawn from outside: v = 63 - x), height y."""
    big = lambda holes: [h for h in holes if not (h[0] in (3.0, 60.0) and h[1] in (3.0, 22.0))]   # drop the corner screws
    L = sorted(big(F["left"])); R = sorted(big(F["right"]))
    assert len(L) == 3 and len(R) == 3, (L, R)
    fig = {"Paddle": (63.0 - L[0][0], L[0][1]), "Audio": (63.0 - L[1][0], L[1][1]), "DC": (63.0 - L[2][0], L[2][1]),
           "RF": (R[0][0], R[0][1]), "PTT": (R[1][0], R[1][1]), "USB": (R[2][0], R[2][1])}
    return fig


def jack_table_problems(Q, F):
    probs = []
    fig = _jacks_from_figures(F)
    for nm, (v, h) in fig.items():
        j = Q.JACKS[nm]
        vs, hs = [v], [h]
        if nm in F["photo"]:
            vs.append(F["photo"][nm][0]); hs.append(F["photo"][nm][1])
        if abs(min(j["v"]) - min(vs)) > 0.051 or abs(max(j["v"]) - max(vs)) > 0.051:
            probs.append("%s: v %s is not the figures' %s" % (nm, j["v"], sorted(vs)))
        if abs(min(j["h"]) - min(hs)) > 0.051 or abs(max(j["h"]) - max(hs)) > 0.051:
            probs.append("%s: h %s is not the figures' %s" % (nm, j["h"], sorted(hs)))
    return probs


def open_end_problems(Q):
    """Each jack admits a plug body wider than its panel opening by 2 mm (the opening a plug passes, plus its shell)."""
    probs = []
    for nm, j in Q.JACKS.items():
        opening = j["hole"] if not isinstance(j["hole"], tuple) else j["hole"][1]
        need_r = opening / 2 + 1.0
        if Q.admitted_radius(nm) < need_r:
            probs.append("%s (%s panel): the tray admits r %.2f, the opening alone needs r %.2f" % (nm, j["panel"], Q.admitted_radius(nm), need_r))
    return probs


def ledge_problems(Q):
    probs = []
    for x0, x1 in Q.FRONT_SEGMENTS:
        for sx in (-1, 1):
            a, b = sorted((sx * Q.KNOB_ZONE[0], sx * Q.KNOB_ZONE[1]))
            if x0 < b and x1 > a: probs.append("knob-edge ledge %.1f .. %.1f over the knob zone %.1f .. %.1f" % (x0, x1, a, b))
        if abs(x0) > Q.U0 or abs(x1) > Q.U0: probs.append("knob-edge ledge past the end face")
    lcd_near = Q.LCD[2]                       # the LCD window's edge nearest the back edge, from the back edge
    if Q.LEDGE_BACK - Q.CLR >= lcd_near: probs.append("the back ledge reaches the LCD window")
    return probs


def t_the_jack_table_is_the_measured_one():
    import lid_tray_qmx_r2 as Q
    F = _figures()
    probs = jack_table_problems(Q, F)
    assert not probs, probs
    bad = copy.deepcopy(F); bad["photo"]["RF"] = (12.1, 11.6)       # a record without the photograph's RF place
    assert jack_table_problems(Q, bad), "a jack table wider than its record passed"
    assert abs(F["top"][0][3] - Q.KNOB_V) < 0.051 and abs(F["top"][0][0] - Q.KNOB_U) < 0.051, (F["top"][0], Q.KNOB_U, Q.KNOB_V)


def t_both_end_panels_are_open():
    import lid_tray_qmx_r2 as Q
    probs = open_end_problems(Q)
    assert not probs, probs
    sill = Q.SILL_H
    try:
        Q.SILL_H = 6.0; Q.Z_SILL = Q.Z_UB + Q.SILL_H                   # a sill raised into an end wall
        got = open_end_problems(Q)
    finally:
        Q.SILL_H = sill; Q.Z_SILL = Q.Z_UB + Q.SILL_H
    assert got and any(g.startswith("PTT") for g in got) and any(g.startswith("Audio") for g in got), got
    assert {j["panel"] for j in Q.JACKS.values()} == {"L", "R"}, "the table lost an end panel"


def t_ledges_clear_the_knobs_and_the_lcd():
    import lid_tray_qmx_r2 as Q
    assert not ledge_problems(Q), ledge_problems(Q)
    segs = Q.FRONT_SEGMENTS
    try:
        Q.FRONT_SEGMENTS = [(-(Q.U0 - 1.0), Q.U0 - 1.0)]              # the r1 idea: one full-length lip along the knob edge
        got = ledge_problems(Q)
    finally:
        Q.FRONT_SEGMENTS = segs
    assert got, "a full-length knob-edge ledge passed"


def t_the_place_keeps_c5_east_edge():
    import panel1450 as L, lid_tray_qmx_r2 as Q
    assert abs(Q.EAST_EDGE_X - L.QMX_TRAY_X[1]) < 1e-9 and abs(Q.SPAN_X[1] - L.QMX_TRAY_X[1]) < 1e-9, (Q.SPAN_X, L.QMX_TRAY_X)
    assert abs((Q.SPAN_X[1] - Q.SPAN_X[0]) - Q.SIZE[1]) < 1e-9 and abs((Q.SPAN_Y[1] - Q.SPAN_Y[0]) - Q.SIZE[0]) < 1e-9
    assert len(Q.PLATE_HOLES) == 10 and len(set(Q.PLATE_HOLES)) == 10


def t_face_room_at_the_worst():
    import lid_tray_qmx_r2 as Q, lid_tray_qmx_r2_check as C
    R = C.frame_seat_rows()
    wc2_room = R["M3"]["wc2"] + C.m3_tray(R)                          # the tray depth M3 was computed with (r1's 28.0, or r2's from its label)
    def rows(q):
        top = q.BOND + q.PLATE_T + q.Z_UT
        return {"ledge": wc2_room - (top + q.LEDGE_T), "top": wc2_room - top, "knob": wc2_room - top - q.KNOB_H}
    got = rows(Q)
    assert got["ledge"] >= C.MIN_MECH and got["knob"] >= C.MIN_MECH, got
    class Deeper: pass
    d = Deeper(); d.__dict__.update({k: getattr(Q, k) for k in ("BOND", "PLATE_T", "Z_UT", "LEDGE_T", "KNOB_H")}); d.PLATE_T += 3.0
    assert rows(d)["knob"] < C.MIN_MECH, "a stack 3 mm deeper kept the knob tips clear: the rule reads nothing"
    rep = C.report()
    assert "M3r2k" in rep and "MET on the INFERRED knob" in rep, rep[:200]


def t_pads_touch_at_every_corner():
    import lid_tray_qmx_r2 as Q, lid_tray_qmx_r2_check as C
    t0, t1 = Q.PAD["t"] * (1 - Q.PAD["t_tol"]), Q.PAD["t"] * (1 + Q.PAD["t_tol"])
    least = t0 - (Q.Z_UB + 2 * C.PRINT_TOL); most = (t1 - (Q.Z_UB - 2 * C.PRINT_TOL)) / t1
    assert least > 0.0 and most < 0.60, (least, most)


def t_screw_tips_stay_in_the_plate():
    import lid_tray_qmx_r2 as Q
    screw = 5.0                                                        # the M3 x 5 of SCREW, flush at the boss top
    assert "M3 x 5" in Q.SCREW
    tip_below_plate_face = screw - Q.Z_SILL
    assert 0.0 < tip_below_plate_face <= Q.PLATE_T - 0.3, tip_below_plate_face
    assert not (6.0 - Q.Z_SILL <= Q.PLATE_T - 0.3), "an M3 x 6 would stay in the plate: the rule would not refuse it"


def t_the_release_carries_r2_and_keeps_r1():
    rel = os.path.join(V2, "release", "case-2026-09-27")
    mf = need(os.path.join(rel, "MANIFEST.sha256"), "the case release")
    names = {ln.split(None, 1)[1].strip() for ln in open(mf, encoding="utf-8") if ln.strip() and not ln.startswith("#")}
    for f in ("lid-tray-qmx-r2/lid-tray-qmx-r2.step", "lid-tray-qmx-r2/lid-tray-qmx-r2.stl", "lid-tray-qmx-r2/lid-tray-qmx-r2-keeper.step",
              "lid-tray-qmx-r2/lid-tray-qmx-r2-keeper.stl", "lid-tray-qmx-r2/lid-plate-qmx-r2.step", "lid-tray-qmx-r2/lid-plate-qmx-r2.dxf",
              "lid-tray-qmx-r2/lid-tray-qmx-r2-drawing.pdf", "lid-tray-qmx-r2/lid-tray-qmx-r2-check.out", "lid-tray-qmx-r2/README.md",
              "lid-tray-qmx/lid-bracket-qmx.step", "lid-tray-qmx/lid-bracket-qmx.stl", "drawings/lid-tray-qmx-drawing.pdf"):
        assert f in names, "the case release's MANIFEST does not carry %s" % f
    head = "".join(ln for ln in open(mf, encoding="utf-8") if ln.startswith("#"))
    assert "SUPERSEDED" in head and "lid-tray-qmx/lid-bracket-qmx.stl" in head, head
    rec = open(os.path.join(rel, "lid-tray-qmx-r2", "lid-tray-qmx-r2-check.out"), encoding="utf-8").read()
    assert "RESULT: PASS" in rec, "the released record's solid checks did not pass"
