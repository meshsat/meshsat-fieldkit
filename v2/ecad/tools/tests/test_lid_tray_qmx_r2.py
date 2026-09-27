#!/usr/bin/env python3
"""The QMX lid tray r2 fits the unit the maker describes, the unit can be put into it, and its face room is read from the solid above
each part (MESHSAT-1357, S-63, EQ-24; stream w5tray, second pass of 27 to 28 September 2026).

The r1 tray of 9 September 2026 was notched at one end while the QMX has jacks on both end panels, and its 95 x 63 x 25 came from no
maker document. The first pass of r2 held the unit under ledges and lintels that were part of the tray: its checker found that the unit
cannot be fitted (B1) and that its face-room row for the buttons was measured from the wrong solid (B2). Each rule here states a
property of v2/cad/lid_tray_qmx_r2.py or of v2/cad/lid_tray_qmx_r2_check.py (importing them builds nothing, so this runs without the CAD
venv) and is shown refusing a defective copy:

  * the jack table the set is built on is the one v2/vendor/qrp-labs/qmx-figures.out measured on the maker's figures and photograph,
    read by parsing that record, not typed twice;
  * every jack on BOTH end panels admits a plug body wider than its own panel opening by 2 mm at the worst of its scaled place, so no
    end is closed (a sill raised to a wall is refused);
  * B1, the unit goes in: the unit at its largest, with everything that stands proud of it, keeps the stated minimum to every solid
    of the tray on its way in, and the frame to everything on its way over the unit; THE FIRST PASS'S TRAY WITH ITS DOCUMENTED WAY IN
    IS REFUSED, and so are the r2 tray with a lintel printed across an end and a unit one millimetre wider;
  * the frame keeps off both knobs and their finger room and off the LCD window, and is a closed ring;
  * the east edge stays where C5 put the r1 tray (panel1450.QMX_TRAY_X[1]), so M19 does not move, and the place spans the part;
  * B2, the face room: every row's depth is the deepest solid of the table over that part's footprint; THE FIRST PASS'S ROW FOR THE
    BUTTONS, MEASURED FROM THE UNIT'S TOP FACE, IS REFUSED AGAINST ITS OWN TRAY; no row is NOT MET, a knob 3 mm taller is, and every
    face part with a solid of the set over it has a height read from a maker's sheet that the tree holds;
  * the pads always touch the unit over the tolerance corners, never pass 60 percent, and the unit never reaches the floor's stop;
  * every tray screw's tip stays inside the lid plate (a longer screw reaches the bond and is refused), and every frame screw
    passes through its nut and stops short of its hole's bottom;
  * every link of the retention holds the load case the record names, and the record says which link governs;
  * the record prints itself the same twice, and the released set carries its own manifest and leaves the release's files alone."""
import os, sys, re, copy, hashlib, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
V2 = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.join(V2, "cad"))
from harness import need

FIGURES = os.path.join(V2, "vendor", "qrp-labs", "qmx-figures.out")
REL = os.path.join(V2, "release", "case-2026-09-27")
R2 = os.path.join(REL, "lid-tray-qmx-r2")


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
            probs.append("%s (%s panel): the set admits r %.2f, the opening alone needs r %.2f" % (nm, j["panel"], Q.admitted_radius(nm), need_r))
    return probs


def frame_problems(Q):
    """The frame in plan: off each knob's finger room, off the LCD window, and closed (each bar and ledge meets a rail or a ledge)."""
    probs = []
    fr = [e for e in Q.elements() if e["part"] == "frame"]
    for e in fr:
        x0, x1, y0, y1 = e["box"][:4]
        for sx in (-1, 1):
            kx, ky, r = sx * Q.KNOB_X, Q.KNOB_Y, Q.KNOB_D / 2 + Q.FINGER
            dx = max(x0 - kx, 0.0, kx - x1); dy = max(y0 - ky, 0.0, ky - y1)
            if (dx * dx + dy * dy) ** 0.5 < r - 1e-9:
                probs.append("%s stands %.2f from the knob at x %+.1f, inside its %.1f of finger room" % (e["name"], (dx * dx + dy * dy) ** 0.5, kx, r))
        lx0, lx1 = -Q.U0 + Q.LCD[0], -Q.U0 + Q.LCD[1]; ly0, ly1 = Q.UNIT[1] / 2 - Q.LCD[3], Q.UNIT[1] / 2 - Q.LCD[2]
        if min(x1, lx1) - max(x0, lx0) > 1e-9 and min(y1, ly1) - max(y0, ly0) > 1e-9:
            probs.append("%s lies over the LCD window" % e["name"])
    touch = lambda a, b: min(a[1], b[1]) - max(a[0], b[0]) > -1e-9 and min(a[3], b[3]) - max(a[2], b[2]) > -1e-9
    seen, todo = {fr[0]["name"]}, [fr[0]]
    while todo:
        a = todo.pop()
        for b in fr:
            if b["name"] not in seen and touch(a["box"], b["box"]): seen.add(b["name"]); todo.append(b)
    if len(seen) != len(fr): probs.append("the frame is in pieces: %s hang on nothing" % sorted(e["name"] for e in fr if e["name"] not in seen))
    if not any(e["box"][0] < -Q.U0 and e["box"][1] > Q.U0 for e in fr): probs.append("no rail runs the unit's whole length")
    return probs


def fitting_problems(C, E):
    probs = []
    for title, rows in C.fitting(E):
        bad, least = C.judge(rows)
        probs += ["%s: %s keeps %.2f to the %s" % (title.split(",")[0], b["by"], b["clearance"], b["solid"]) for b in bad]
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
    ends = [e for e in Q.elements() if e["part"] == "tray" and "sill" in e["name"]]
    assert ends and all(e["box"][5] <= Q.Z_SILL + 1e-9 for e in ends), "a sill stands above the sill height"
    walls = [e for e in Q.elements() if e["part"] == "tray" and e["box"][5] > Q.Z_SILL + 1e-9]
    assert walls and all(abs(e["box"][0]) <= Q.U0 and abs(e["box"][1]) <= Q.U0 for e in walls), "a wall or post of the tray stands beside an end panel's plugs"


def t_b1_the_unit_goes_in_and_the_frame_over_it():
    import lid_tray_qmx_r2 as Q, lid_tray_qmx_r2_check as C
    E = Q.elements()
    assert not fitting_problems(C, E), fitting_problems(C, E)
    one, two = C.fitting(E)
    assert len(one[1]) == len(Q.parts(E, "tray")) and len(two[1]) == len(Q.parts(E, "tray", "unit", "proud")), "a solid was left out of a way in"
    assert C.judge(one[1])[1]["clearance"] >= C.MIN_INSERT and C.MIN_INSERT >= C.PRINT_TOL, "the stated minimum is under the printed parts' own tolerance"
    # the known-bad case of blocking item B1: the first pass's tray and its documented way in
    bad, _ = C.judge(C.pass1_way_in())
    assert bad, "the first pass's tray, which no assembled QMX can enter, passed the insertion check"
    hit = {b["solid"]: b for b in bad}
    assert "lintel at the keeper end" in hit and hit["lintel at the keeper end"]["by"].endswith("knob") and hit["lintel at the keeper end"]["clearance"] < 0, hit
    # the same defect in the r2 tray: a lintel printed across the front end at the height of the unit's top face
    E2 = E + [Q._e("tray", "a lintel printed on the tray", -Q.FRAME_X, -Q.U0, -Q.SIDE_OUT, Q.SIDE_OUT, Q.Z_UT, Q.Z_TOP)]
    got = fitting_problems(C, E2)
    assert any("a lintel printed on the tray" in g for g in got), got
    # and a unit one millimetre wider than the maker's: it does not pass between the walls
    E3 = copy.deepcopy(E)
    for e in E3:
        if e["part"] == "unit": b = e["box"]; e["box"] = (b[0], b[1], b[2] - 0.5, b[3] + 0.5, b[4], b[5])
    got = fitting_problems(C, E3)
    assert any("wall" in g for g in got), got
    # a knob the frame's ledge would land on: the knob-edge ledge run through a knob zone
    E4 = E + [Q._e("frame", "a ledge over the knob", Q.KNOB_X - 5, Q.KNOB_X + 5, -Q.SIDE_OUT, Q.KNOB_Y, Q.Z_UT, Q.Z_TOP, seat=("unit", "tray"))]
    got = fitting_problems(C, E4)
    assert any("TUNE knob" in g for g in got), got


def t_the_frame_clears_the_knobs_and_the_lcd():
    import lid_tray_qmx_r2 as Q
    assert not frame_problems(Q), frame_problems(Q)
    segs = Q.FRONT_SEGMENTS
    try:
        Q.FRONT_SEGMENTS = [(-Q.FRAME_X, Q.FRAME_X)]                  # the r1 idea: one full-length lip along the knob edge
        got = frame_problems(Q)
    finally:
        Q.FRONT_SEGMENTS = segs
    assert got and any("finger room" in g for g in got), "a full-length knob-edge ledge passed"
    back = Q.LEDGE_BACK
    try:
        Q.LEDGE_BACK = 20.0                                            # a back ledge reaching the LCD window
        got = frame_problems(Q)
    finally:
        Q.LEDGE_BACK = back
    assert got and any("LCD" in g for g in got), got


def t_the_place_keeps_c5_east_edge():
    import panel1450 as L, lid_tray_qmx_r2 as Q
    assert abs(Q.EAST_EDGE_X - L.QMX_TRAY_X[1]) < 1e-9 and abs(Q.SPAN_X[1] - L.QMX_TRAY_X[1]) < 1e-9, (Q.SPAN_X, L.QMX_TRAY_X)
    assert abs((Q.SPAN_X[1] - Q.SPAN_X[0]) - Q.SIZE[1]) < 1e-9 and abs((Q.SPAN_Y[1] - Q.SPAN_Y[0]) - Q.SIZE[0]) < 1e-9
    assert len(Q.PLATE_HOLES) == 10 and len(set(Q.PLATE_HOLES)) == 10 and len(set(Q.FRAME_SCREWS)) == 6
    base = [e for e in Q.elements() if e["part"] in ("tray", "frame", "plate", "screw")]
    assert all(abs(e["box"][0]) <= Q.BASE_X + 1e-9 and abs(e["box"][1]) <= Q.BASE_X + 1e-9 and abs(e["box"][2]) <= Q.BASE_Y + 1e-9 and abs(e["box"][3]) <= Q.BASE_Y + 1e-9
               for e in base), "a solid of the set lies outside the base the place is computed from"


def t_b2_face_room_is_read_from_the_solid_above_each_part():
    import lid_tray_qmx_r2 as Q, lid_tray_qmx_r2_check as C, panel1450 as L
    E = Q.elements() + C.plug_envelopes()[0]
    rows = C.face_rows(E)
    got = {r["ref"]: r for r in rows}
    # every row's depth is the deepest solid of the table over the part's footprint, found again here without the check's own search
    for r in rows:
        f = r["foot"]; x0, x1, y0, y1 = f[2] - Q.PLACE_Y, f[3] - Q.PLACE_Y, f[0] - Q.PLACE_X, f[1] - Q.PLACE_X
        tops = [e["box"][5] for e in E if e["part"] != "plate" and min(e["box"][1], x1) - max(e["box"][0], x0) > 1e-9 and min(e["box"][3], y1) - max(e["box"][2], y0) > 1e-9]
        assert tops and abs(max(tops) + Q.BOND + Q.PLATE_T - r["depth"]) < 1e-9, (r["ref"], r["depth"], max(tops))
    # the three buttons stand under the frame, not under the unit's top face
    for ref in ("SW_MAIN", "SW_PI", "SW_TEST"):
        assert ref in got and got[ref]["part"] == "frame" and abs(got[ref]["depth"] - (Q.BOND + Q.PLATE_T + Q.Z_TOP)) < 1e-9, got.get(ref)
        assert got[ref]["height"] >= 2.5, "a button's head without its seal: %s" % got[ref]["height"]
    assert not [r for r in rows if r["verdict"] == "NOT MET"], [r["ref"] for r in rows if r["verdict"] == "NOT MET"]
    # the set's own allowances are in every row: the worst is under the room's worst by more than the depth and the height
    room = C.room()
    assert all(room[1] - r["depth"] - r["height"] - r["worst"] >= 0.43 - 1e-9 for r in rows), "a row without the set's own allowances"
    assert all(abs((r["worst"] - r["wc2"]) - ((room[1] - room[2]) + (room[1] - r["depth"] - r["height"] - r["worst"]))) < 1e-9 for r in rows), "the sensitivity column does not take the set's allowances twice"
    # the known-bad case of blocking item B2: the first pass's row for the buttons against the solids of the first pass's tray
    E1, P1 = C.pass1_elements()
    probs = C.claimed_depth_problems(E1, (P1["place_x"], P1["place_y"]), C.PASS1_ROWS)
    assert len(probs) == 3 and all("2.00 deeper" in p for p in probs), probs
    assert not C.claimed_depth_problems(E, (Q.PLACE_X, Q.PLACE_Y), [("row", (r["ref"],), r["depth"], "derived") for r in rows if r["ref"] != "FACE"]), "the derived rows refuse themselves"
    # a real interference is NOT MET: a knob 3 mm taller
    kh = Q.KNOB_H
    try:
        Q.KNOB_H = kh + 3.0
        tall = C.face_rows(Q.elements() + C.plug_envelopes()[0])
    finally:
        Q.KNOB_H = kh
    assert any(r["verdict"] == "NOT MET" and r["solid"].endswith("knob") for r in tall), [(r["ref"], r["verdict"]) for r in tall]
    # every face part under the set has a height, and each height's source names a sheet the tree holds or a ruling
    assert not [n for n in C.unread_face_parts() if C.over(E, [(c[0] - s[0] / 2, c[0] + s[0] / 2, c[1] - s[1] / 2, c[1] + s[1] / 2)
                for m, c, s, k in L.FACE_ITEMS if m == n][0], (Q.PLACE_X, Q.PLACE_Y))], "a face part under the set has no height"
    for f in ("switches/ck-atp19-series-datasheet.pdf", "switches/ck-atp16-series-datasheet.pdf", "mentor/mentor-ll14-14-ip68-front-panel-light-guides.pdf"):
        need(os.path.join(V2, "vendor", f), "a maker's sheet section B reads")
    assert "XFRAME_2" in got and "XENARC_WINDOW" in got and "D1" in got and "U_LIGHT" in got, sorted(got)


def t_pads_touch_at_every_corner():
    import lid_tray_qmx_r2 as Q, lid_tray_qmx_r2_check as C
    t0, t1 = Q.PAD["t"] * (1 - Q.PAD["t_tol"]), Q.PAD["t"] * (1 + Q.PAD["t_tol"])
    hi, lo = Q.Z_UB + C.PRINT_TOL + Q.UNIT_TOL, Q.Z_UB - C.PRINT_TOL - Q.UNIT_TOL
    least = t0 - hi; most = (t1 - lo) / t1
    assert least > 0.0 and most < 0.60, (least, most)
    assert lo > Q.FLOOR, "the unit at its lowest sits on the floor's stop: the frame cannot come down on the wall tops"
    assert all(e["box"][5] <= Q.Z_UB + 1e-9 for e in Q.elements() if e["part"] == "pad")


def t_screws_stay_where_they_hold():
    import lid_tray_qmx_r2 as Q
    screw = 5.0                                                        # the M3 x 5 of SCREW, flush at the boss top
    assert "M3 x 5" in Q.SCREW
    tip_below_plate_face = screw - Q.Z_SILL
    assert 0.0 < tip_below_plate_face <= Q.PLATE_T - 0.3, tip_below_plate_face
    assert not (6.0 - Q.Z_SILL <= Q.PLATE_T - 0.3), "an M3 x 6 would stay in the plate: the rule would not refuse it"
    # the frame screws: through the frame and the post's top into the nut, the tip past the nut and above the hole's bottom
    assert "M3 x 10" in Q.FRAME_SCREW and abs(Q.BH["length"] - 10.0) < 1e-9
    tip = Q.Z_TOP - Q.BH["length"]; js15 = 0.29
    assert tip + js15 + 0.4 < Q.NUT_Z[0], "a short screw at a thick frame does not pass through its nut: tip %.2f, nut from %.2f" % (tip + js15 + 0.4, Q.NUT_Z[0])
    assert tip - js15 - 0.4 > Q.Z_TOP - Q.BH["length"] - 2.0, "a long screw bottoms in its hole"
    assert Q.NUT["slot_h"] > Q.NUT["m"] and Q.NUT["slot_w"] > Q.NUT["s"] and Q.NUT_Z[1] < Q.Z_UT - 2.0, "the nut has no slot to sit in or no roof to bear on"
    posts = {(round(e["box"][0] + Q.POST["w"] / 2, 2)) for e in Q.elements() if "post" in e["name"]}
    assert all(round(x, 2) in posts for x, y in Q.FRAME_SCREWS), "a frame screw with no post under it"
    assert (Q.POST["w"] - Q.NUT["slot_w"]) / 2 >= 2.0, "the cheeks beside a nut slot are under 2 mm"


def t_every_link_holds_the_load_case():
    import lid_tray_qmx_r2 as Q, lid_tray_qmx_r2_check as C
    load = C.DESIGN_G * (Q.UNIT_MASS + C.PLUG_MASS) * C.G0
    links = [l for l in C.retention() if l[0] != "out*"]
    assert {l[0] for l in links} == {"out", "x", "y"}, "a direction has no link"
    weak = [(l[1], l[2] / load) for l in links if l[2] < 2.0 * load]
    assert not weak, "a link holds under twice the load case: %s" % weak
    rep, ok = C.report()
    assert "LOAD CASE the set is designed to: %.0f g" % C.DESIGN_G in rep and "Governing link" in rep and "stays OPEN" in rep, "the record does not name its load case, its governing link or what stays open"
    assert C.PC["hdt045"] > C.E3S_STORAGE and C.PC["hdt180"] > C.E3S_STORAGE, "the material's heat deflection is not over E3-S's storage temperature"


def t_the_record_prints_itself_twice_and_the_release_is_left_alone():
    import lid_tray_qmx_r2_check as C
    a, ok = C.report(); b, _ = C.report()
    assert a == b and ok, "the record differs between two runs, or fails"
    assert "CONTROL 1, which must FAIL" in a and "FAILS as it must" in a and "THE CHECK IS BROKEN" not in a
    mf = need(os.path.join(R2, "MANIFEST.sha256"), "the r2 set's own manifest")
    names = {}
    for ln in open(mf, encoding="utf-8"):
        if ln.strip() and not ln.startswith("#"):
            d, n = ln.split(None, 1); names[n.strip()] = d
    for f in ("lid-tray-qmx-r2.step", "lid-tray-qmx-r2.stl", "lid-tray-qmx-r2-frame.step", "lid-tray-qmx-r2-frame.stl", "lid-plate-qmx-r2.step",
              "lid-plate-qmx-r2.dxf", "lid-tray-qmx-r2-drawing.pdf", "lid-tray-qmx-r2-check.out", "README.md"):
        assert f in names, "the r2 set's manifest does not carry %s" % f
        assert hashlib.sha256(open(os.path.join(R2, f), "rb").read()).hexdigest() == names[f], "%s changed since the manifest was written" % f
    assert sorted(names) == sorted(f for f in os.listdir(R2) if f != "MANIFEST.sha256"), "the r2 folder and its manifest name different files"
    rec = open(os.path.join(R2, "lid-tray-qmx-r2-check.out"), encoding="utf-8").read()
    assert "RESULT: PASS: the table is what was built" in rec and "RESULT of sections B and E: PASS" in rec, "the released record's checks did not pass"
    assert rec.startswith(a), "the released record is not what the check prints from this tree"
    # the release the r2 set stands beside keeps its bytes: its own manifest still holds, and git sees no change under it but the new folder
    import case_geometry_check as G
    assert not G.manifest(REL), G.manifest(REL)
    rel_names = {ln.split(None, 1)[1].strip() for ln in open(os.path.join(REL, "MANIFEST.sha256"), encoding="utf-8") if ln.strip() and not ln.startswith("#")}
    assert "lid-tray-qmx/lid-bracket-qmx.stl" in rel_names and not any(n.startswith("lid-tray-qmx-r2/") for n in rel_names), "the release's manifest was edited for r2"
