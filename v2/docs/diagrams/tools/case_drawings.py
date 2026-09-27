#!/usr/bin/env python3
"""The case interior in plan and in Z, drawn from the committed geometry sources (MESHSAT-1357, handover layer 4).

Writes svg/case-plan.svg, svg/case-zstack.svg, the same two as pdf/, and case-drawings.md (every number the drawings use,
with the file it was read from). Design drawings of an unbuilt prototype: nothing in this kit has been built, fitted to a
case or measured, and nominal geometry establishes no physical fit, alignment or seal (CASE-MARGINS.md section 1).

Sources, read at run time and never retyped here:
  v2/vendor/peli/frame_seat.py (imported): the Peli 1450 cavity, the 1450PF frame, the chosen face plate C1, the setting
      legs C6, board B's heights with the VHB lift, the pack block's east face and top (CASE-MARGINS.md's own calculator)
  v2/vendor/peli/1450/frame_seat.out: that calculator's committed output, for the figures it computes inside its main
      block (the face top and its range, the arrestor sites of C2, the connector plate of C3)
  v2/vendor/peli/case_margins.py: the pack block's wrapped size
  v2/ecad/tools/panel1450.py (imported): board B's outline, the backer strips, the Xenarc body, B's tall parts, the
      AS-CODED face height and wall jacks
  v2/ecad/tools/gen_pcb_a.py, gen_pcb_e.py, gen_pcb_e5.py, gen_pcb_p.py (their top-level constants, parsed, not imported:
      they need KiCad): the outlines of boards A, E, E5 and P, the rods, board D's mezzanine site, the blind-mate row
  v2/cad/render/scene.py (parsed): the Z of boards E5, A and D in the render stack, before the VHB lift
  v2/ecad/tools/pcb_board_facts.yaml: each board's outline, checked against the generators

Where the tree carries two figures for one thing (the face height and the wall jacks as panel1450.py codes them against
the arrangement CASE-MARGINS.md chose), both are drawn and labelled; nothing is reconciled here.

Needs matplotlib and PyYAML (runner-safe, no CAD). Usage: python3 v2/docs/diagrams/tools/case_drawings.py"""
import ast, os, re, sys, textwrap
sys.dont_write_bytecode = True   # nothing written into the tree beside the sources read
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as N
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon

sys.path.insert(0, os.path.join(N.REPO, "v2/ecad/tools"))
sys.path.insert(0, os.path.join(N.REPO, "v2/vendor/peli"))
import panel1450 as P
import frame_seat as F

D = os.path.join(N.REPO, "v2/docs/diagrams")
SRC = {k: v for k, v in [
    ("frame_seat", "v2/vendor/peli/frame_seat.py"), ("frame_seat_out", "v2/vendor/peli/1450/frame_seat.out"),
    ("case_margins", "v2/vendor/peli/case_margins.py"), ("panel1450", "v2/ecad/tools/panel1450.py"),
    ("gen_pcb_a", "v2/ecad/tools/gen_pcb_a.py"), ("gen_pcb_e", "v2/ecad/tools/gen_pcb_e.py"),
    ("gen_pcb_e5", "v2/ecad/tools/gen_pcb_e5.py"), ("gen_pcb_p", "v2/ecad/tools/gen_pcb_p.py"),
    ("scene", "v2/cad/render/scene.py"), ("board_facts", "v2/ecad/tools/pcb_board_facts.yaml"),
    ("case_margins_md", "v2/docs/CASE-MARGINS.md")]}
PHRASE = "Design drawing of an unbuilt prototype: nothing has been built, fitted to a case or measured."


def consts(rel):
    """Top-level literal assignments of a Python source, without importing it."""
    out = {}
    for node in ast.parse(open(os.path.join(N.REPO, rel), encoding="utf-8").read()).body:
        if isinstance(node, ast.Assign):
            try:
                val = ast.literal_eval(node.value)
            except ValueError:
                continue
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = val
                elif isinstance(t, ast.Tuple) and isinstance(val, tuple) and len(t.elts) == len(val):
                    for e, v in zip(t.elts, val):
                        if isinstance(e, ast.Name):
                            out[e.id] = v
    return out


def text(rel):
    return open(os.path.join(N.REPO, rel), encoding="utf-8").read()


def read_geometry():
    g, used = {}, []

    def put(key, val, src, note=""):
        g[key] = val; used.append((key, val, src, note))
    ca, ce, ce5, cp = consts(SRC["gen_pcb_a"]), consts(SRC["gen_pcb_e"]), consts(SRC["gen_pcb_e5"]), consts(SRC["gen_pcb_p"])
    facts = yaml.safe_load(text(SRC["board_facts"]))
    out = text(SRC["frame_seat_out"])
    sc = text(SRC["scene"])
    zs = {n: float(z) for n, z in re.findall(r'import_board\("(pcb_[a-z0-9]+)", "[^"]+", ([0-9.]+)', sc)}
    # case and frame (frame_seat.py)
    put("case_wall_z0", (F.HX0, F.HY0), SRC["frame_seat"], "inner end and long wall planes at Z 0 (half sizes), drafted %.3f per mm of Z" % F.TW)
    put("case_flat_floor", (F.FLAT_X, F.FLAT_Y), SRC["frame_seat"], "flat floor to the R %.2f fillet tangent (half sizes)" % F.FIL_R)
    put("case_corner_r", F.CORNER_R, SRC["frame_seat"])
    put("case_rim", F.RIM, SRC["frame_seat"], "Peli base depth, STEP and drawing")
    put("case_shoulder", F.SHOULDER, SRC["frame_seat"])
    put("case_rib_top", F.RIB_TOP, SRC["frame_seat"])
    put("case_wall_t", F.WALL_T, SRC["frame_seat"])
    put("lid_depth", F.LID_STEP, SRC["frame_seat"])
    put("frame_window", F.F_WIN, SRC["frame_seat"], "1450PF window half sizes")
    put("frame_ring_t", F.RING_T, SRC["frame_seat"])
    put("frame_section", frame_section_data(), SRC["frame_seat"],
        "the 1450PF frame in section on the end walls' straight part: bottom = C6 pad top less RING_UNDER, ring from the pad top, "
        "skirt inner face F_SKIRT_IN, outer face frame_half() on F_OUT['x'] up to the gasket step, then the flange F_FLANGE")
    put("legs", dict(x=F.LEG_X, y=F.LEG_Y, foot_x=F.FOOT_X, pad_top=F.LEG_TOP), SRC["frame_seat"], "C6 setting legs (|X|, |Y|)")
    put("plate_c1", F.PLATE, SRC["frame_seat"], "C1 face plate, chosen")
    put("face_top_c1", F.LEG_TOP + F.RING_T + F.PLATE[2], SRC["frame_seat"], "leg pad top + ring + plate")
    m = re.search(r"face top ([0-9.]+) nominal, ([0-9.]+) \.\. ([0-9.]+) on the legs", out)
    put("face_top_range", (float(m.group(2)), float(m.group(3))), SRC["frame_seat_out"], "section (C)")
    m = re.search(r"frame bottom ([0-9.]+) nominal, ([0-9.]+) \.\. ([0-9.]+) \(legs\)", out)
    put("frame_bottom", tuple(float(x) for x in m.groups()), SRC["frame_seat_out"], "the skirt's bottom edge: nominal, low, high")
    if abs(g["frame_bottom"][0] - g["frame_section"]["bottom"]) > 0.005:
        raise SystemExit("frame bottom: frame_seat.out %.2f, frame_seat.py LEG_TOP - RING_UNDER %.2f" % (g["frame_bottom"][0], g["frame_section"]["bottom"]))
    m = re.search(r"M21d in two dimensions: .*?: ([0-9.]+) nominal \(straight face ([0-9.]+)\)", out)
    put("m21d", (float(m.group(1)), float(m.group(2))), SRC["frame_seat_out"], "leg column to the skirt's inner face: at the corner arc, on the straight face")
    m = re.search(r"M20 \(the seat, a statement\): frame bottom ([0-9.]+) nominal against rib tops ([0-9.]+): ([0-9.]+) above", out)
    put("m20", tuple(float(x) for x in m.groups()), SRC["frame_seat_out"], "frame bottom, rib tops, clearance")
    put("b_under_top", (F.B_UNDER, F.B_TOP), SRC["frame_seat"], "board B underside and top copper with the 1.1 VHB lift")
    put("vhb_lift", round(F.B_UNDER - (P.B_TOP_Z - 1.6), 2), SRC["frame_seat"], "B_UNDER less panel1450's underside")
    put("heatsink", F.HEATSINK, SRC["frame_seat"], "height above B's top (panel1450.py:36); no Raspberry Pi drawing held (TBD)")
    put("xenarc_h", F.XEN_H, SRC["frame_seat"], "monitor body depth (panel1450.py:44); the maker's drawing is owed (TBD)")
    put("pack_east_top", (F.PACK_EAST, F.PACK_TOP), SRC["frame_seat"], "pack block east face X and top Z (A06, M6)")
    m = re.search(r"4S3P 18650, 3 x 2, ([0-9.]+) x ([0-9.]+) x ([0-9.]+) wrapped", text(SRC["case_margins"]))
    put("pack_block", tuple(float(x) for x in m.groups()), SRC["case_margins"], "wrapped block, X x Y x Z")
    m = re.search(r"pack group \(([0-9.]+) long, A06\)", text(SRC["frame_seat"]))
    put("pack_group_len", float(m.group(1)), SRC["frame_seat"], "block, 2 mm and board P along Y, centred (M5)")
    m = re.search(r"east \((\d+)\): ([^;]+); west \((\d+)\): ([^;]+); axis Z ([0-9.]+)", out)
    sites = lambda s: [(n.strip(), float(y)) for n, y in re.findall(r"([A-Z0-9 .]+?) ([+-][0-9]+)", s)]
    put("arrestors", dict(east=sites(m.group(2)), west=sites(m.group(4)), z=float(m.group(5))), SRC["frame_seat_out"], "C2, on the RF entry plates (C4)")
    m = re.search(r"plate ([0-9.]+) x ([0-9.]+) x ([0-9.]+) at X ([-0-9.]+)\.\.([-0-9.]+), Z ([0-9.]+)\.\.([0-9.]+)", out)
    put("connector_plate", tuple(float(x) for x in m.groups()), SRC["frame_seat_out"], "C3 on the back wall: w, h, t, X0, X1, Z0, Z1")
    # the margin table's tally and M1's worst case, read rather than typed so the footers cannot go stale (review of 27 Sep 2026)
    m = re.search(r"(\d+) rows: (\d+) MET, (\d+) OPEN, (\d+) NOT MET", out)
    put("margin_rows", tuple(int(x) for x in m.groups()), SRC["frame_seat_out"], "margin rows: total, MET, OPEN, NOT MET")
    m = re.search(r"\n  M1 +monitor body over the CM5 heatsinks +([0-9.]+) +([+-][0-9.]+) +([+-][0-9.]+) ", out)
    put("m1_row", (float(m.group(2)), float(m.group(3))), SRC["frame_seat_out"], "M1: nominal, worst")
    # boards
    put("A", (ca["BOARD_X0"], -ca["BOARD_W"] / 2, ca["BOARD_X0"] + ca["BOARD_L"], ca["BOARD_W"] / 2), SRC["gen_pcb_a"])
    put("D", tuple(ca["MEZZ_RECT"]), SRC["gen_pcb_a"], "MEZZ_RECT, board D's site on A")
    put("B", tuple(P.B_OUTLINE), SRC["panel1450"])
    put("E", (ce["X0"], ce["Y0"], ce["X1"], ce["Y1"]), SRC["gen_pcb_e"])
    put("E5", (ce5["X0"], ce5["Y0"], ce5["X1"], ce5["Y1"]), SRC["gen_pcb_e5"])
    put("P_size", (cp["BOARD_L"], cp["BOARD_W"]), SRC["gen_pcb_p"], "placed at the pack block's south end, length along Y: INFERRED from ASSEMBLY.md section 3 and M5")
    put("C_strips", dict(L=P.STRIP_L, B=P.STRIP_B, R=P.STRIP_R, T=P.STRIP_T), SRC["panel1450"])
    put("rods", ca["ROD_HOLES"], SRC["gen_pcb_a"])
    put("rf_row", (ca["RF_X"], ca["RF_Y"]), SRC["gen_pcb_a"], "blind-mate receptacles on A's underside")
    put("z_scene", dict(E=zs.get("pcb_e6", 0.0), E5=zs.get("pcb_e5"), A=zs.get("pcb_a22"), D=zs.get("pcb_d8")), SRC["scene"],
        "board bottoms in the render stack, before the VHB lift")
    put("as_coded", dict(face_top=P.FACE_TOP_Z, plate=P.PLATE, sma_z=P.SMA_Z, west=P.WALL_WEST, east=P.WALL_EAST,
                         backer_gap=P.BACKER_GAP, backer_t=P.BACKER_T), SRC["panel1450"], "superseded by C1, C2 and C6 (CASE-MARGINS.md section 4)")
    put("tall", P.B16_TALL, SRC["panel1450"], "board B's tall parts, height above B's top")
    put("xenarc", P.XENARC, SRC["panel1450"])
    # outline check against the facts file
    for key, letter in (("A", "a"), ("B", "b"), ("E", "e"), ("D", "d")):
        x0, y0, x1, y1 = g[key]
        fo = facts[letter]["outline_mm"]
        if [round(x1 - x0, 2), round(y1 - y0, 2)] != [float(fo[0]), float(fo[1])]:
            raise SystemExit("board %s: generator outline %s x %s, pcb_board_facts.yaml %s" % (key, x1 - x0, y1 - y0, fo))
    return g, used


def frame_section_data():
    """The 1450PF frame's section at the end walls, every figure from frame_seat.py: its constants and its own outer-face
    profile frame_half(), sampled and reduced to its corners (no number of the profile is retyped here)."""
    zb = round(F.LEG_TOP - F.RING_UNDER, 2)
    top = round(zb + F.FH, 2)
    if abs(top - (F.LEG_TOP + F.RING_T)) > 0.005:
        raise SystemExit("frame_seat.py: bottom + FH %.2f is not pad top + RING_T %.2f" % (top, F.LEG_TOP + F.RING_T))
    n = int(round(F.FH / 0.01))
    prof = [(i * 0.01, F.frame_half(i * 0.01, F.F_OUT["x"])) for i in range(n + 1)]
    prof = [(round(h, 2), x) for h, x in prof if x is not None]
    keep = [prof[0]]
    for a, b, c in zip(prof, prof[1:], prof[2:]):
        if abs((b[1] - a[1]) * (c[0] - b[0]) - (c[1] - b[1]) * (b[0] - a[0])) > 1e-9:
            keep.append(b)
    keep.append(prof[-1])
    hw, xw = max(keep, key=lambda p: p[1])
    return dict(bottom=zb, ring_under=F.LEG_TOP, top=top, win=F.F_WIN[0], skirt_in=F.F_SKIRT_IN[0], outer=keep,
                step_z=round(zb + keep[-1][0], 2), flange=F.F_FLANGE[0], widest=(round(zb + hw, 2), xw),
                wall_at_widest=round(F.hx(zb + hw), 2))


def frame_poly(fs, sx):
    """The frame's section outline on the side sx (+1 east, -1 west), in case X and Z."""
    pts = [(fs["win"], fs["ring_under"]), (fs["skirt_in"], fs["ring_under"]), (fs["skirt_in"], fs["bottom"])]
    pts += [(x, fs["bottom"] + h) for h, x in fs["outer"]]
    pts += [(fs["flange"], fs["step_z"]), (fs["flange"], fs["top"]), (fs["win"], fs["top"])]
    return [(sx * x, z) for x, z in pts]


def rect(ax, x0, y0, x1, y1, **kw):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **kw))


def rrect(ax, hx, hy, r, **kw):
    ax.add_patch(FancyBboxPatch((-hx + r, -hy + r), 2 * (hx - r), 2 * (hy - r), boxstyle="round,pad=%g" % r, **kw))


def footer(fig, lines, head):
    ids = ", ".join("%s %s" % (os.path.basename(SRC[k]), N.sha16(SRC[k])) for k in ("case_margins_md", "frame_seat", "frame_seat_out", "panel1450", "board_facts"))
    # wrapped at 240 characters: at 7.5 pt a longer line ran past the plan's right edge (readback of 27 Sep 2026, round 8)
    body = lines + ["Sources by sha256/16: %s." % ids, "Every other input is in v2/docs/diagrams/case-drawings.md. Generated by v2/docs/diagrams/tools/case_drawings.py. " + PHRASE]
    fig.text(0.01, 0.01, "\n".join(w for ln in body for w in textwrap.wrap(ln, 240)),
             fontsize=7.5, va="bottom", ha="left", family="DejaVu Sans")


def plan(g, head):
    fig, ax = plt.subplots(figsize=(16.5, 12.5))
    fig.subplots_adjust(left=0.05, right=0.99, top=0.93, bottom=0.2)
    hx0, hy0 = g["case_wall_z0"]
    fx, fy = g["case_flat_floor"]
    rrect(ax, hx0, hy0, g["case_corner_r"], fill=False, lw=1.6, ec="#e65100")
    rrect(ax, F.hx(g["case_rim"]), F.hy(g["case_rim"]), g["case_corner_r"], fill=False, lw=0.8, ec="#e65100", ls="--")
    rect(ax, -fx, -fy, fx, fy, fill=False, lw=0.6, ec="#e65100", ls=":")
    wx, wy = g["frame_window"]
    rrect(ax, wx, wy, F.F_WIN_R, fill=False, lw=1.0, ec="#6d4c41", ls="-.")
    rrect(ax, F.F_SKIRT_IN[0], F.F_SKIRT_IN[1], F.F_SKIRT_IN_R, fill=False, lw=0.8, ec="#6d4c41", ls=":")
    rrect(ax, F.F_OUT["x"][0], F.F_OUT["y"][0], F.F_OUT_R, fill=False, lw=0.6, ec="#6d4c41")
    px, py, _ = g["plate_c1"]
    rect(ax, -px / 2, -py / 2, px / 2, py / 2, fill=False, lw=0.8, ec="#455a64", ls=(0, (6, 3)))
    cpx, cpy, _ = g["as_coded"]["plate"]
    rect(ax, -cpx / 2, -cpy / 2, cpx / 2, cpy / 2, fill=False, lw=0.6, ec="#9e9e9e", ls=":")
    # boards, lowest first
    colours = dict(E="#a5d6a7", E5="#66bb6a", A="#90caf9", D="#ce93d8", B="#ffe082", C="#b0bec5", P="#ef9a9a")
    for key, lab in (("E", "E dock strip 267 x 68"), ("E5", "E5"), ("A", "A power 240 x 160"), ("D", "D APRS 100 x 80")):
        x0, y0, x1, y1 = g[key]
        rect(ax, x0, y0, x1, y1, fc=colours[key], ec="#263238", lw=0.9, alpha=0.55)
        ax.text(x0 + 3, y0 + 3 if key != "A" else y1 - 9, lab, fontsize=8)
    x0, y0, x1, y1 = g["B"]
    rect(ax, x0, y0, x1, y1, fill=False, ec="#f9a825", lw=2.0)
    ax.text(x0 + 3, y1 - 9, "B compute 330 x 200 (above A; drawn as its outline)", fontsize=8, color="#8d6e00")
    for name, s in g["C_strips"].items():
        rect(ax, s[0], s[1], s[2], s[3], fill=False, ec="#546e7a", lw=0.8, hatch="//", alpha=0.6)
    ax.text(g["C_strips"]["L"][0] + 2, g["C_strips"]["T"][3] + 2, "C panel backer ring (four strips, under the face plate)", fontsize=7.5, color="#37474f",
            bbox=dict(facecolor="white", edgecolor="none", pad=0.6))   # kept legible over the frame window's line
    # the pack block and board P (east pocket)
    bw, bl, bh = g["pack_block"]; east, top = g["pack_east_top"]; glen = g["pack_group_len"]
    pl, pw = g["P_size"]
    y_s = -glen / 2
    rect(ax, east - bw, y_s + pl + 2.0, east, glen / 2, fc="#ef9a9a", ec="#b71c1c", lw=1.0, alpha=0.7)
    ax.text(east - bw + 2, glen / 2 - 12, "4S3P block\n%.2f x %.1f" % (bw, bl), fontsize=7.5)
    cx = east - bw / 2
    rect(ax, cx - pw / 2, y_s, cx + pw / 2, y_s + pl, fc="#ffcdd2", ec="#b71c1c", lw=0.9, ls="--")
    ax.text(cx - pw / 2 + 1, y_s + 3, "P 70 x 44\n(place\nINFERRED)", fontsize=7)
    # rods, legs, the blind-mate row
    for x, y in g["rods"]:
        ax.add_patch(plt.Circle((x, y), 1.6, color="#212121"))
    lg = g["legs"]
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * lg["x"][0], sx * lg["x"][1])); y0, y1 = sorted((sy * lg["y"][0], sy * lg["y"][1]))
            rect(ax, x0, y0, x1, y1, fc="#6d4c41", ec="#3e2723")
            f0, f1 = sorted((sx * lg["foot_x"][0], sx * lg["foot_x"][1]))
            rect(ax, f0, y0, f1, y1, fc="none", ec="#6d4c41", lw=0.6, ls="--")
    rx, ry = g["rf_row"]
    ax.plot(rx, [ry] * len(rx), "o", ms=3, color="#1565c0")
    ax.text(rx[0] - 6, ry - 9, "blind-mate row on A's underside (11 sites)", fontsize=7, color="#1565c0")
    # walls: the arrestors (C2) and the connector plate (C3); the as-coded jacks
    ar = g["arrestors"]; hxz = F.hx(ar["z"])
    for side, sites in ((1, ar["east"]), (-1, ar["west"])):
        for n, y in sites:
            ax.plot([side * hxz, side * (hxz + g["case_wall_t"] + 14)], [y, y], color="#1565c0", lw=2.2)
            ax.text(side * (hxz + g["case_wall_t"] + 16), y, n, fontsize=6.5, va="center", ha="left" if side > 0 else "right", color="#1565c0")
    for n, y in g["as_coded"]["west"]:
        ax.plot([-hx0 - 2], [y], "x", color="#9e9e9e", ms=5)
    for n, y in g["as_coded"]["east"]:
        ax.plot([hx0 + 2], [y], "x", color="#9e9e9e", ms=5)
    w, h, t, cx0, cx1, _, _ = g["connector_plate"]
    rect(ax, cx0, hy0 + g["case_wall_t"], cx1, hy0 + g["case_wall_t"] + t, fc="#1565c0", ec="#0d47a1")
    ax.text((cx0 + cx1) / 2, hy0 + g["case_wall_t"] + t + 3, "C3 connector plate %.1f x %.1f (back wall, outside)" % (w, h), fontsize=7.5, ha="center", color="#0d47a1")
    # dimensions
    def dim(x0, y0, x1, y1, lab, off=0, vertical=False):
        ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#37474f"))
        ax.text((x0 + x1) / 2 + (off if vertical else 0), (y0 + y1) / 2 + (0 if vertical else off), lab, fontsize=7.5,
                ha="center", va="center", rotation=90 if vertical else 0, backgroundcolor="white")
    dim(-hx0, -hy0 - 8, hx0, -hy0 - 8, "cavity at the floor %.2f (drafted 2 deg to %.2f at the rim)" % (2 * hx0, 2 * F.hx(g["case_rim"])), -4)
    dim(-hx0 - 62, -hy0, -hx0 - 62, hy0, "cavity at the floor %.2f" % (2 * hy0), -5, True)
    dim(g["B"][0], g["B"][3] + 4, g["B"][2], g["B"][3] + 4, "B 330", 3)
    dim(g["A"][0], g["A"][3] - 16, g["A"][2], g["A"][3] - 16, "A 240", 3)
    dim(east - bw, -glen / 2 - 5, east, -glen / 2 - 5, "%.2f" % bw, -3)
    ax.set_xlim(-hx0 - 80, hx0 + 70); ax.set_ylim(-hy0 - 25, hy0 + 30); ax.set_aspect("equal")
    ax.set_xlabel("X (mm), case centre, +X east end wall"); ax.set_ylabel("Y (mm), +Y back (hinge) wall")
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_title("Case interior, plan view: Peli 1450 with the 1450PF frame, the board set and the pack (design drawing of an unbuilt prototype)", fontsize=11)
    legend = [
        "Orange solid: cavity wall at the floor (Peli STEP); orange dashed: at the rim Z %.2f; orange dotted: flat floor to the R %.2f fillet." % (g["case_rim"], F.FIL_R),
        "Brown dash-dot: 1450PF frame window; brown dotted: the frame skirt's inner face (M21d); brown thin: the frame's outer face at the skirt bottom (Z %.2f; %.2f wider per side at its widest). Grey dashed: face plate C1 %.1f x %.1f (chosen); grey dotted: panel1450.py's plate %.1f x %.1f (as coded, superseded)." % (g["frame_section"]["bottom"], g["frame_section"]["widest"][1] - g["frame_section"]["outer"][0][1], px, py, cpx, cpy),
        "Brown solid: C6 setting legs (column; the dashed box is the foot on the flat floor). Black dots: the four M3 rods. Blue ticks: C2 arrestors at Z %.0f on the RF entry plates; grey x: panel1450.py's wall jacks at Z %.0f (as coded, superseded)." % (ar["z"], g["as_coded"]["sma_z"]),
        "NOT SHOWN: parts on the boards (only board B's outline), cables and jumpers, the pack's hold-down (not designed, S-27), the lid and the QMX tray, the Xenarc and e-paper on the face, fasteners, and any tolerance band: CASE-MARGINS.md section 3 holds the margins, %d of %d OPEN." % (g["margin_rows"][2], g["margin_rows"][0]),
        "Board P's place at the block's south end is INFERRED (ASSEMBLY.md section 3, CASE-MARGINS.md M5); its hold-down and the block's are owed. Nominal geometry establishes no fit (CASE-MARGINS.md section 1)."]
    footer(fig, legend, head)
    return fig


def detail_a(fig, g):
    """Detail A: the east end wall at the frame, where the 1450PF frame's ring and skirt, the C6 leg, the face plate C1
    and the case wall meet (M20, M21d). The west end is its mirror."""
    ax = fig.add_axes([0.05, 0.155, 0.47, 0.305])
    fs = g["frame_section"]; lg = g["legs"]; rim = g["case_rim"]; sh = g["case_shoulder"]; t = g["case_wall_t"]
    z0, z1, x0, x1 = 74.0, 112.0, 150.0, 199.0
    # the wall: the drafted inner face below the shoulder, the rim zone above it (frame_seat.py RIMZ_X), the wall behind
    zs = [z0 + i * (sh - z0) / 20 for i in range(21)]
    inner = [(F.hx(z), z) for z in zs] + [(F.RIMZ_X, sh), (F.RIMZ_X, rim)]
    ax.add_patch(Polygon(inner + [(F.RIMZ_X + t, rim), (F.hx(z0) + t, z0)], closed=True, fc="#ffe0b2", ec="none"))
    ax.plot(*zip(*inner), color="#e65100", lw=1.4)
    ax.plot([F.RIMZ_X, F.RIMZ_X + t], [rim, rim], color="#e65100", lw=1.4)
    ax.text(F.hx(z0) + t / 2, z0 + 2, "end wall\n%.2f" % t, fontsize=7, ha="center", color="#bf360c")
    ax.text(F.RIMZ_X + t + 0.4, rim, "rim %.2f" % rim, fontsize=7.5, va="center", color="#e65100")
    ax.annotate("shoulder %.2f (ledge to X %.2f)" % (sh, F.RIMZ_X), (F.RIMZ_X, sh), (198.0, 101.3), fontsize=7.5, va="center",
                color="#e65100", arrowprops=dict(arrowstyle="->", lw=0.6, color="#e65100"))
    # the end-wall rib (innermost line of its cone) and its top
    rz = [z0 + i * (g["case_rib_top"] - z0) / 10 for i in range(11)]
    ax.plot([F.rib_in(F.RIB_AX_X, z) for z in rz], rz, color="#e65100", lw=0.9, ls="--")
    fb, rt, m20 = g["m20"]
    ax.annotate("end-wall rib (dashed), top %.2f;\nM20: skirt bottom %.2f above it" % (rt, m20), (F.rib_in(F.RIB_AX_X, rt), rt),
                (198.0, 80.0), fontsize=7.5, ha="left", va="center", color="#e65100", arrowprops=dict(arrowstyle="->", lw=0.6, color="#e65100"))
    # the C6 leg column up to its pad, the frame, the plate with its rebate
    rect(ax, lg["x"][0], z0, lg["x"][1], lg["pad_top"], fc="#8d6e63", ec="#3e2723", lw=0.8)
    ax.text((lg["x"][0] + lg["x"][1]) / 2, (z0 + lg["pad_top"]) / 2, "C6 leg column, X %.2f to %.2f" % tuple(lg["x"]), fontsize=7,
            ha="center", va="center", rotation=90, color="white")
    ax.add_patch(Polygon(frame_poly(fs, 1), closed=True, fc="#a1887f", ec="#3e2723", lw=0.9))
    px, _, pt = g["plate_c1"]; rb = F.REB_IN[0] / 2
    plate = [(x0, fs["top"]), (px / 2, fs["top"]), (px / 2, fs["top"] + pt - F.REBATE), (rb, fs["top"] + pt - F.REBATE),
             (rb, fs["top"] + pt), (x0, fs["top"] + pt)]
    ax.add_patch(Polygon(plate, closed=True, fc="#b0bec5", ec="#263238", lw=0.9))
    # labels, each figure from frame_seat.py or its output
    lo, hi = g["frame_bottom"][1], g["frame_bottom"][2]
    xs = (fs["skirt_in"] + fs["outer"][0][1]) / 2
    ax.errorbar([xs], [fs["bottom"]], yerr=[[fs["bottom"] - lo], [hi - fs["bottom"]]], fmt="none", ecolor="#263238", capsize=3, lw=0.9)
    ax.annotate("skirt bottom %.2f nominal\n(%.2f to %.2f on the legs)" % (fs["bottom"], lo, hi), (fs["skirt_in"], fs["bottom"]),
                (166.0, 80.0), fontsize=7.5, ha="center", arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("ring underside %.2f\n= C6 pad top" % fs["ring_under"], (177.8, fs["ring_under"]), (151.0, 91.5), fontsize=7.5,
                ha="left", va="center", arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.text(fs["win"] + 0.4, (fs["ring_under"] + fs["top"]) / 2, "ring %.2f\n%.2f to %.2f" % (g["frame_ring_t"], fs["ring_under"], fs["top"]),
            fontsize=7, va="center")
    ax.annotate("window edge X %.2f" % fs["win"], (fs["win"], fs["top"] - 1.0), (160.0, 98.5), fontsize=7.5, ha="center",
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("skirt inner face X %.2f" % fs["skirt_in"], (fs["skirt_in"], 88.5), (166.5, 85.5), fontsize=7.5, ha="center",
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("", (lg["x"][1], 91.0), (fs["skirt_in"], 91.0), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#b71c1c"))
    arc, straight = g["m21d"]
    ax.text((lg["x"][1] + fs["skirt_in"]) / 2, 91.6, "M21d %.2f" % straight, fontsize=7, ha="center", va="bottom", color="#b71c1c")
    zw, xw = fs["widest"]
    ax.annotate("frame widest X %.2f at Z %.2f;\nwall %.2f there (%.2f per side)" % (xw, zw, fs["wall_at_widest"], fs["wall_at_widest"] - xw),
                (xw, zw), (198.0, 90.5), fontsize=7.5, ha="left", va="center", arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("gasket step Z %.2f;\nflange X %.2f above it" % (fs["step_z"], fs["flange"]), (fs["outer"][-1][1], fs["step_z"]), (198.0, 96.5),
                fontsize=7.5, ha="left", va="center", arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.annotate("C1 edge X %.2f, band from X %.2f\nrebated %.1f; face top %.2f" % (px / 2, rb, F.REBATE, g["face_top_c1"]),
                (px / 2, fs["top"] + pt - F.REBATE), (198.0, 105.0), fontsize=7.5, ha="left", va="center", arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.set_xlim(x0, x1 + 24); ax.set_ylim(z0, z1 + 2); ax.set_aspect("equal")
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_xlabel("X (mm), east end wall; the west end is its mirror"); ax.set_ylabel("Z (mm)")
    ax.set_title("Detail A: the 1450PF frame at the end wall, in section on the wall's straight part (|Y| under %.2f)" % F.F_SKIRT_IN_C[1], fontsize=9.5)
    fig.text(0.55, 0.455, "\n".join([
        "Detail A, the frame in section. Every figure is frame_seat.py's (constants, and",
        "its own outer-face profile frame_half()) or its output frame_seat.out:",
        "  skirt: bottom %.2f nominal, %.2f to %.2f on the legs (section (C))," % (fs["bottom"], lo, hi),
        "    from the inner face X %.2f out to the outer face, X %.2f at the bottom," % (fs["skirt_in"], fs["outer"][0][1]),
        "    %.2f at its widest (Z %.2f) and %.2f at the gasket step (Z %.2f);" % (xw, zw, fs["outer"][-1][1], fs["step_z"]),
        "  ring: underside %.2f on the C6 pads, top %.2f, from the window X %.2f;" % (fs["ring_under"], fs["top"], fs["win"]),
        "  flange above the step: X %.2f; face plate C1 on the ring, top %.2f." % (fs["flange"], g["face_top_c1"]),
        "M21d (leg column to the skirt's inner face): %.2f on the straight face drawn here," % straight,
        "  %.2f nominal at the skirt's R %.2f corner arc, where the leg's outer-back" % (arc, F.F_SKIRT_IN_R),
        "  corner sits (CASE-MARGINS.md, OPEN). M20: the skirt bottom sits %.2f above" % m20,
        "  the end-wall rib tops %.2f; the same skirt bottom runs along the long walls," % rt,
        "  where M10 and M14a measure the highest parts below it.",
        "Not in this section: the frame's corner arcs, its insert bores and gasket, the",
        "  lid; the case's rim-zone face above the shoulder is drawn plumb (its draft",
        "  above the ledge is not in frame_seat.py)."]), fontsize=8, va="top", ha="left", family="DejaVu Sans")
    return ax


def zstack(g, head):
    fig = plt.figure(figsize=(16.5, 15.0))
    ax = fig.add_axes([0.06, 0.5, 0.92, 0.46])
    hx0, _ = g["case_wall_z0"]; rim = g["case_rim"]; lift = g["vhb_lift"]
    # the cavity section: drafted end walls and the floor fillet
    wall = [(-F.hx(rim), rim), (-hx0, 0.0), (hx0, 0.0), (F.hx(rim), rim)]
    ax.plot(*zip(*wall), color="#e65100", lw=1.6)
    t = g["case_wall_t"]
    ax.add_patch(Polygon([(-F.hx(rim), rim), (-hx0, 0), (-hx0 - t, 0), (-F.hx(rim) - t, rim)], fc="#ffe0b2", ec="none"))
    ax.add_patch(Polygon([(F.hx(rim), rim), (hx0, 0), (hx0 + t, 0), (F.hx(rim) + t, rim)], fc="#ffe0b2", ec="none"))
    for z, lab, ls in ((rim, "rim %.2f" % rim, "-"), (g["case_shoulder"], "shoulder %.2f" % g["case_shoulder"], "--"), (g["case_rib_top"], "rib top %.2f" % g["case_rib_top"], ":")):
        ax.plot([-hx0 - 35, -hx0 + 25], [z, z], color="#e65100", lw=0.8, ls=ls); ax.text(-hx0 - 36, z, lab, fontsize=7.5, ha="right", va="center", color="#e65100")
    ax.plot([F.hx(rim) - 30, F.hx(rim) + 15], [rim + g["lid_depth"]] * 2, color="#e65100", lw=0.8, ls="--")
    ax.text(F.hx(rim) + 16, rim + g["lid_depth"], "lid inside %.2f (closed)" % (rim + g["lid_depth"]), fontsize=7.5, va="center", color="#e65100")
    zsc = g["z_scene"]

    def board(x0, x1, zb, lab, col, th=1.6):
        rect(ax, x0, zb, x1, zb + th, fc=col, ec="#263238", lw=0.8)
        ax.text(x0 + 2, zb + th + 0.8, lab, fontsize=7.5)
    board(g["E"][0], g["E"][2], zsc["E"] + lift, "E dock strip %.1f to %.1f (on VHB %.1f)" % (zsc["E"] + lift, zsc["E"] + lift + 1.6, lift), "#a5d6a7")
    board(g["E5"][0], g["E5"][2], zsc["E5"] + lift, "E5 %.1f" % (zsc["E5"] + lift), "#66bb6a")
    board(g["A"][0], g["A"][2], zsc["A"] + lift, "A power %.1f to %.1f (blind-mate gap above E)" % (zsc["A"] + lift, zsc["A"] + lift + 1.6), "#90caf9")
    board(g["D"][0], g["D"][2], zsc["D"] + lift, "D %.1f" % (zsc["D"] + lift), "#ce93d8")
    bu, bt = g["b_under_top"]
    board(g["B"][0], g["B"][2], bu, "B compute: underside %.1f, top %.1f" % (bu, bt), "#ffe082")
    for (x0, y0, x1, y1), h, name in g["tall"]:
        if "heatsink" in name or "fan" in name:
            rect(ax, x0, bt, x1, bt + h, fc="#cfd8dc" if "heatsink" in name else "none", ec="#455a64", lw=0.7, ls="-" if "heatsink" in name else "--")
    ax.text(-93, bt + g["heatsink"] + 0.8, "CM5 heatsinks, top %.1f (fans, dashed, lie north of the monitor)" % (bt + g["heatsink"]), fontsize=7.5)
    bw, bl, bh = g["pack_block"]; east, top = g["pack_east_top"]
    rect(ax, east - bw, top - bh, east, top, fc="#ef9a9a", ec="#b71c1c", lw=1.0)
    ax.text(east - bw + 1, top - bh / 2, "4S3P\nblock\ntop %.2f" % top, fontsize=7.5)
    # the face: chosen (C1 on C6) and as coded
    ft = g["face_top_c1"]; lo, hi = g["face_top_range"]; px = g["plate_c1"][0]
    rect(ax, -px / 2, ft - g["plate_c1"][2], px / 2, ft, fc="#b0bec5", ec="#263238", lw=0.9)
    ax.text(0, ft + 1.0, "face plate C1 on the frame, top %.2f nominal (%.2f to %.2f)" % (ft, lo, hi), fontsize=8, ha="center")
    ax.errorbar([140.0], [ft], yerr=[[ft - lo], [hi - ft]], fmt="o", ms=3, color="#263238", capsize=4, lw=1.0)
    ax.text(143, hi + 1.0, "face top range on the legs", fontsize=7, color="#263238")
    lg = g["legs"]; fb = g["frame_bottom"]
    fs = g["frame_section"]
    for sx in (-1, 1):
        x0, x1 = sorted((sx * lg["x"][0], sx * lg["x"][1]))
        rect(ax, x0, 0, x1, lg["pad_top"], fc="#8d6e63", ec="#3e2723", lw=0.6)
        ax.add_patch(Polygon(frame_poly(fs, sx), closed=True, fc="#a1887f", ec="#3e2723", lw=0.6))
    ax.text(lg["x"][0] - 3, 64, "C6 setting leg, pad top %.2f" % lg["pad_top"], fontsize=7.5, ha="right")
    ax.text(145.0, 118.0, "1450PF frame: ring %.2f to %.2f on the legs, skirt to X %.2f, skirt bottom %.2f (%.2f to %.2f)" % (
        fs["ring_under"], fs["top"], fs["widest"][1], fs["bottom"], g["frame_bottom"][1], g["frame_bottom"][2]), fontsize=7.5, ha="right", va="center", color="#3e2723")
    rect(ax, 150.0, 74.0, 199.0 + t, 114.0, fill=False, ec="#37474f", lw=0.7, ls="--")
    ax.text(150.0, 115.0, "detail A (below)", fontsize=7.5, color="#37474f")
    xe = g["xenarc"]; xw = xe["body"][0]
    rect(ax, -xw / 2, ft - xe["height"], xw / 2, ft, fc="none", ec="#1b5e20", lw=1.2)
    ax.text(-xw / 2 + 2, ft - xe["height"] + 1, "Xenarc 709GNK body %.2f deep, bottom %.2f" % (xe["height"], ft - xe["height"]), fontsize=7.5, color="#1b5e20")
    m1 = ft - xe["height"] - (bt + g["heatsink"])
    ax.annotate("", (60, bt + g["heatsink"]), (60, ft - xe["height"]), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#b71c1c"))
    ax.text(62, (bt + g["heatsink"] + ft - xe["height"]) / 2, "M1 %.2f nominal (floor 2.0; OPEN)" % m1, fontsize=8, color="#b71c1c", va="center")
    ac = g["as_coded"]
    ax.plot([-px / 2, px / 2], [ac["face_top"]] * 2, color="#9e9e9e", lw=1.0, ls=":")
    ax.text(F.hx(rim) + t + 3, ac["face_top"], "panel1450.py face top %.1f\n(as coded, superseded)" % ac["face_top"], fontsize=7.5, color="#757575",
            ha="left", va="center")
    # walls: arrestors and their entry plates (C2, C4), the as-coded jacks
    ar = g["arrestors"]
    for sx in (-1, 1):
        xw_ = sx * (F.hx(ar["z"]) + t)
        ax.plot([xw_, xw_ + sx * 22], [ar["z"]] * 2, color="#1565c0", lw=3)
        ax.plot([sx * (F.hx(ac["sma_z"]) + t + 1)], [ac["sma_z"]], "x", color="#9e9e9e", ms=6)
    ax.text(F.hx(ar["z"]) + t + 24, ar["z"], "C2 arrestor axis Z %.0f" % ar["z"], fontsize=7.5, va="center", color="#1565c0")
    ax.text(F.hx(ac["sma_z"]) + t + 5, ac["sma_z"] + 2.5, "as coded Z %.0f" % ac["sma_z"], fontsize=7, color="#757575")
    ax.set_xlim(-hx0 - 70, hx0 + 75); ax.set_ylim(-5, rim + g["lid_depth"] + 8); ax.set_aspect("equal")
    ax.set_xlabel("X (mm), case centre, +X east end wall (projection along Y: parts at different Y overlap here)"); ax.set_ylabel("Z (mm) above the cavity floor")
    ax.grid(True, lw=0.3, alpha=0.4)
    ax.set_title("Case interior, Z stack (section along X, all Y projected): the chosen arrangement C1 on C6 (design drawing of an unbuilt prototype)", fontsize=11)
    legend = [
        "Heights: boards E, E5, A and D from scene.py's render stack plus the %.1f mm VHB 5952 lift (CASE-MARGINS.md C1 follow-on); board B, the pack top and the face from frame_seat.py, which CASE-MARGINS.md computes with." % lift,
        "Grey dotted and grey x: what panel1450.py still codes (face top %.1f, wall jacks at Z %.0f), superseded by C1, C6 and C2 until the CAD follows (S-27, ARCHITECTURE.md 7.1)." % (ac["face_top"], ac["sma_z"]),
        "M1 is CASE-MARGINS.md's tightest chain: its heatsink height, the Xenarc depth and the spacers have no maker source, so it is OPEN (%+.2f at the worst). The bar at X 140 is the face top's range on the legs." % g["m1_row"][1],
        "NOT SHOWN: board parts other than the CM5 heatsinks and fans, the backer ring C, the e-paper, the PA module under the plate, cables, the RF entry plates' outline, the connector plate, the QMX tray in the lid, fasteners, tolerance stacks;",
        "the frame's corner arcs, insert bores and gasket (the frame is drawn in section on the end walls' straight part, detail A), and the case's rim-zone step above the shoulder in the main view (drawn in detail A).",
        "Board E5's height is the render's (Z %.1f before the lift); gen_pcb_e5.py's docstring says its face is at 7.4 mm: the controlling figure is the blind-mate gap window 12.4 to 14.4 (ARCHITECTURE.md 7.1)." % zsc["E5"]]
    detail_a(fig, g)
    footer(fig, legend, head)
    return fig


def main():
    head, dirty = N.git_rev(list(SRC.values()))
    g, used = read_geometry()
    # svg.hashsalt fixes matplotlib's clip-path ids, so the same inputs give byte-identical SVGs (MANIFEST.json hashes them)
    plt.rcParams.update({"svg.fonttype": "none", "font.family": "DejaVu Sans", "pdf.fonttype": 42, "svg.hashsalt": "meshsat-v2-case"})
    for name, fn in (("case-plan", plan), ("case-zstack", zstack)):
        fig = fn(g, head)
        fig.savefig(os.path.join(D, "svg", name + ".svg"), metadata={"Date": None})
        fig.savefig(os.path.join(D, "pdf", name + ".pdf"), metadata={"CreationDate": None, "ModDate": None})
        plt.close(fig)
    L = ["# Case drawings: every number and its source", "",
         "Generated by `v2/docs/diagrams/tools/case_drawings.py`; do not edit by hand. %s The drawings are `svg/case-plan.svg` "
         "and `svg/case-zstack.svg` (PDF copies in `pdf/`)." % PHRASE, "",
         N.tree_line(head, dirty), "",
         "| Source | sha256/16 | Last changed |", "|---|---|---|"]
    for k, rel in SRC.items():
        L.append("| `%s` | `%s` | `%s` |" % (rel, N.sha16(rel), N.last_commit(rel)))
    L += ["", "| Quantity | Value | Read from | Note |", "|---|---|---|---|"]
    for key, val, src, note in used:
        v = str(val)
        L.append("| %s | %s | `%s` | %s |" % (key, v if len(v) < 160 else v[:157] + "...", src, note))
    L += ["", "## What these drawings do not show", "",
          "- Any fit, alignment or seal: nominal geometry establishes none of them (CASE-MARGINS.md section 1); the margins and their verdicts are CASE-MARGINS.md section 3.",
          "- Parts on the boards, other than board B's CM5 heatsinks and fans in the Z stack; cables, jumpers and the pack's hold-down (not designed yet, S-27).",
          "- `v2/cad/` (last changed `%s`): its models predate D-06, C1 and C6 and are not the source of these drawings." % N.last_commit("v2/cad")]
    open(os.path.join(D, "case-drawings.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("case drawings: plan and Z stack written from %d quantities" % len(used))


if __name__ == "__main__":
    main()
