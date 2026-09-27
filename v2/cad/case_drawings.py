#!/usr/bin/env python3
"""The dimensioned drawings of the MeshSat V2 case set (MESHSAT-1357, 27 Sep 2026), from the single geometry source v2/ecad/tools/panel1450.py,
the board reading v2/cad/zstack.json (v2/cad/zstack.py, from the committed KiCad boards) and the margin table v2/vendor/peli/1450/frame_seat.out.
Every sheet states its tolerances, the source revision and the sha256 of its inputs, and labels the margin rows its features enter, OPEN ones in
red. Nothing here computes a verdict; frame_seat.py does. Prototype: nothing on these sheets has been made, bought or fitted.

Sheets (one PDF each, and all of them in case-drawings-all.pdf):
  2 frame-and-legs-drawing.pdf     the 1450PF frame in plan with Peli's insert bores, the four setting legs, the locator and the wedges (C1, C6)
  3 connector-plate-drawing.pdf    the back wall's connector plate, its six items, the gasket and the wall holes (C3)
  4 rf-entry-plates-drawing.pdf    the two end walls' RF entry plates, the arrestor clamp section and the jumper plugs (C2, C4)
  5 z-stack-drawing.pdf            the Z stack, floor to lid, with every board at its committed Z and the bays read from the boards
  6 case-plan-drawing.pdf          the case floor in plan: boards, rods, legs, pack group, walls' plates, jacks and clamps (mounting and access)
  7..13 board-envelope-<x>.pdf     each board: outline, holes, parts by height on both sides, from its committed KiCad file
  14 lid-tray-qmx-drawing.pdf      the QMX lid tray (C5): the part read from v2/cad/lid_bracket_qmx.py and its place on the lid, X 102.0 to 171.0
Sheet 1, the face plate, is v2/cad/plate_drawing.py's.
Usage: case_drawings.py <out dir>   (matplotlib: v2/cad/requirements-cad.txt)."""
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import panel1450 as L
import drawing_kit as K
from drawing_kit import plt, Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Arc

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
Z = json.load(open(os.path.join(HERE, "zstack.json"), encoding="utf-8"))
N_SHEETS = 14
RED, GREY, BLUE = "#b00020", "#777777", "#1f4e9a"
IN_COMMON = ["v2/ecad/tools/panel1450.py", "v2/vendor/peli/1450/frame_seat.out"]

# Peli's figures the sheets draw (CASE-MARGINS.md section 2; frame_seat.py's readings)
FRAME_OUT = (378.4, 263.1); SKIRT_IN = (366.68, 250.84); SKIRT_IN_R = 17.53; WIN_R = 6.35; FRAME_OUT_R = 16.51
INNER_Z15 = (375.01, 260.71); FLAT = (2 * L.PELI["flat_floor"][0], 2 * L.PELI["flat_floor"][1]); RIMZONE = (382.02, 267.72)
PELI_SCREWS = [(-113.03, -125.42), (113.03, -125.42), (-98.04, 125.42), (98.04, 125.42)]
LETTERING = (-108.99, -123.64, -68.80, -118.32)
TW = 0.0349 / 0.9994; HX0, HY0 = 186.97, 129.82
def hx(z): return HX0 + TW * z
def hy(z): return HY0 + TW * z


def save(fig, name, pdf_all):
    fig.savefig(os.path.join(OUT, name)); pdf_all.savefig(fig); plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------ sheet 2: the frame, the legs, the locator and the wedges
def sheet_frame(pdf_all):
    fig = K.sheet("1450PF frame with Peli's insert bores, the four setting legs (C6), locator and wedges", 2, N_SHEETS,
                  IN_COMMON + ["v2/cad/frame_leg.py", "v2/vendor/peli/1450/1450-panel-frame.STEP"], part="case_drawings.py (sheet 2)")
    ax = fig.add_axes([0.005, 0.28, 0.55, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Polygon(K.rrect_pts(0, 0, FRAME_OUT[0], FRAME_OUT[1], FRAME_OUT_R), closed=True, fill=False, lw=0.9))
    ax.add_patch(Polygon(K.rrect_pts(0, 0, SKIRT_IN[0], SKIRT_IN[1], SKIRT_IN_R), closed=True, fill=False, lw=0.5, ls="--", color=GREY))
    ax.add_patch(Polygon(K.rrect_pts(0, 0, L.WINDOW[0], L.WINDOW[1], WIN_R), closed=True, fill=False, lw=0.9))
    for (x, y) in L.FRAME_BOSSES:
        ax.add_patch(Circle((x, y), 5.18 / 2, fill=False, lw=0.6)); ax.plot([x - 4, x + 4], [y, y], lw=0.3, color="k"); ax.plot([x, x], [y - 4, y + 4], lw=0.3, color="k")
    ax.text(-150, -40, "10 x Peli brass insert 6-32 (bore 5.18 +-0.13) at the STEP's\npositions: the face plate's ten screws (C1)", fontsize=5.5, va="top")
    for (x, y) in PELI_SCREWS:
        ax.plot([x], [y], marker="s", ms=3, color=GREY);
    ax.text(0, -60, "grey squares: Peli's four self-tapping frame screws through the skirt,\nfront X +-113.03, back X +-98.04 (on the skirt's inner face)", fontsize=5.3, ha="center", color=GREY)
    lx0, ly0, lx1, ly1 = LETTERING
    ax.add_patch(Rectangle((lx0, ly0), lx1 - lx0, ly1 - ly0, fill=False, lw=0.4, color=GREY, hatch="////"))
    ax.text((lx0 + lx1) / 2, ly1 + 2, "\"1450 FRONT\" 0.51 high", fontsize=5, ha="center", color=GREY)
    G = L.LEG
    for sx in (-1, 1):
        for sy in (-1, 1):
            c0, c1 = sorted((sx * G["col_x"][0], sx * G["col_x"][1])); y0, y1 = sorted((sy * G["y"][0], sy * G["y"][1]))
            f0, f1 = sorted((sx * G["foot_x"][0], sx * G["foot_x"][1]))
            ax.add_patch(Rectangle((c0, y0), c1 - c0, y1 - y0, fc=BLUE, ec=BLUE, alpha=0.8))
            ax.add_patch(Rectangle((min(f0, c0), y0), max(f1, c1) - min(f0, c0), y1 - y0, fill=False, ec=BLUE, lw=0.5, ls=":"))
    # wedges at the middle of each wall, between the skirt and the case wall
    for (x, y, w, h) in ((-FRAME_OUT[0] / 2 - 3, -20, 3, 40), (FRAME_OUT[0] / 2, -20, 3, 40), (-20, -FRAME_OUT[1] / 2 - 3, 40, 3), (-20, FRAME_OUT[1] / 2, 40, 3)):
        ax.add_patch(Rectangle((x, y), w, h, fc="#e0a000", ec="k", lw=0.3))
    ax.text(FRAME_OUT[0] / 2 + 5, 0, "centring wedge\npairs (printed)", fontsize=5, va="center")
    K.dim_h(ax, -FRAME_OUT[0] / 2, FRAME_OUT[0] / 2, FRAME_OUT[1] / 2, "378.4 +-0.76 (sheet)", off=12)
    K.dim_v(ax, FRAME_OUT[0] / 2, -FRAME_OUT[1] / 2, FRAME_OUT[1] / 2, "263.1 +-0.76", off=24)
    K.dim_h(ax, -L.WINDOW[0] / 2, L.WINDOW[0] / 2, -L.WINDOW[1] / 2, "window %.2f (349.7 +-0.76)" % L.WINDOW[0], off=-25)
    K.dim_v(ax, -L.WINDOW[0] / 2, -L.WINDOW[1] / 2, L.WINDOW[1] / 2, "window %.2f" % L.WINDOW[1], off=-40)
    K.dim_h(ax, -179.07, 179.07, 75.95, "insert pattern 358.14 (sheet 358.1, +-0.38 per side)", off=-8, fs=5.5)
    K.dim_v(ax, 139.45, -121.16, 121.16, "242.32", off=-10, fs=5.5)
    K.dim_h(ax, -139.45, 0.0, 121.16, "139.45", off=-8, fs=5.5); K.dim_h(ax, 0.0, 139.45, 121.16, "139.45", off=-8, fs=5.5)
    K.dim_v(ax, 179.07, -75.95, 75.95, "151.90", off=-10, fs=5.5)
    K.tag(ax, 177.8, -109.4, "leg: M21b M21c M21d M21e OPEN", dx=-120, dy=-35)
    ax.text(0, 20, "PLAN, case frame (X east, +Y the hinge wall), seen from above.\nLegs (blue) under the ring: column |X| %.2f..%.2f, |Y| %.1f..%.1f;\nfeet (dotted) |X| %.1f..%.1f on the flat floor" % (
        G["col_x"][0], G["col_x"][1], G["y"][0], G["y"][1], G["foot_x"][0], G["foot_x"][1]), fontsize=6.3, ha="center")
    ax.set_xlim(-225, 225); ax.set_ylim(-165, 160)
    # --- the leg's elevation
    ex = fig.add_axes([0.55, 0.28, 0.25, 0.70]); ex.set_aspect("equal"); ex.axis("off")
    import frame_leg as FL
    p = FL.profile_pts(); pts = [p["p8"], p["p0"], p["p1"], p["p2"], p["p3"]]
    for k in range(1, 20):
        x = L.PELI["flat_floor"][0] + (G["col_x"][1] - L.PELI["flat_floor"][0]) * k / 20.0; pts.append((x, FL.fil_off_z(x)))
    pts += [p["p4"], p["p5"], p["p6"], p["p7"]]
    ex.add_patch(Polygon(pts, closed=True, fc="#c9d6ea", ec=BLUE, lw=0.8))
    # case: floor, fillet, drafted wall, shoulder, rim; frame ring and skirt; plate
    fx = L.PELI["flat_floor"][0]; R_ = L.PELI["fillet_r"]
    ex.plot([140, fx], [0, 0], color="k", lw=0.9)
    arc = [(fx + R_ * math.sin(t), R_ - R_ * math.cos(t)) for t in [k * (math.pi / 2) / 30 for k in range(31)]]
    ex.plot([a[0] for a in arc], [a[1] for a in arc], color="k", lw=0.9)
    ex.plot([hx(15.32), hx(101.04)], [15.32, 101.04], color="k", lw=0.9)
    ex.plot([hx(101.04), hx(101.04) + 0.51, hx(101.04) + 0.51, 191.29], [101.04, 101.04, 101.04, 108.97], color="k", lw=0.9)
    ex.plot([140, 200], [108.97, 108.97], color=GREY, lw=0.4, ls="--"); ex.text(141, 109.8, "Peli rim 108.97", fontsize=5.5, color=GREY)
    ex.plot([140, 200], [84.58, 84.58], color=GREY, lw=0.4, ls=":"); ex.text(141, 85.3, "rib tops 84.58 (knife-edge seat, not used)", fontsize=5.3, color=GREY)
    ring_top = L.LEG_TOP_Z + L.PELI["ring_t"]
    ex.add_patch(Rectangle((174.83, L.LEG_TOP_Z), 182.75 - 174.83, L.PELI["ring_t"], fc="#bbbbbb", ec="k", lw=0.5))
    ex.add_patch(Rectangle((183.34, L.FRAME_BOTTOM_Z), 189.18 - 183.34, ring_top - L.FRAME_BOTTOM_Z, fc="#bbbbbb", ec="k", lw=0.5))
    ex.add_patch(Rectangle((140, L.PLATE_UNDER_Z), L.PLATE[0] / 2 - 140, L.PLATE[2], fc="#9aa6b2", ec="k", lw=0.5))
    ex.text(150, L.FACE_TOP_Z + 1.2, "face plate on the ring (C1), top %.2f" % L.FACE_TOP_Z, fontsize=5.8)
    ex.text(184, L.FRAME_BOTTOM_Z - 3.5, "skirt bottom %.2f" % L.FRAME_BOTTOM_Z, fontsize=5.5)
    K.dim_v(ex, 180.17, 0, L.LEG_TOP_Z, "pad top %.2f +-0.10 (LEG_TOP_Z)" % L.LEG_TOP_Z, off=26, fs=6)
    K.dim_v(ex, 182.75, L.LEG_TOP_Z, ring_top, "ring 9.39", off=11, fs=5.5)
    K.dim_h(ex, G["foot_x"][0], G["foot_x"][1], 0, "foot %.1f..%.1f" % G["foot_x"], off=-7, fs=5.5)
    K.dim_h(ex, G["col_x"][0], G["col_x"][1], L.LEG_TOP_Z, "%.2f" % (G["col_x"][1] - G["col_x"][0]), off=7, fs=5.5)
    ex.annotate("R 15.88 fillet (Peli), relief 2.5 normal", xy=(176, 6.0), xytext=(143, 22), fontsize=5.5, arrowprops=dict(arrowstyle="-", lw=0.4))
    ex.text(G["col_x"][0] - 1, 55, "column\n|X| %.2f..%.2f" % G["col_x"], fontsize=5.5, ha="right")
    ex.text(157, 9.5, "gusset to Z %.0f; foot %.1f high (INFERRED shape)" % (G["gusset_z"], G["foot_h"]), fontsize=5.3)
    ex.text(175.6, L.LEG_TOP_Z - 3.2, "VHB pocket 0.9", fontsize=4.8)
    K.tag(ex, 180.17, 5.57, "M21c relief OPEN", dx=6, dy=-8)
    K.tag(ex, 169.0, 0.0, "M21a MET (foot end to tangent)", dx=-6, dy=-15, color="#2e7d32", ha="right")
    K.tag(ex, 180.17, 90.0, "M21d OPEN (corner to skirt)", dx=8, dy=-12)
    K.tag(ex, 175.4, L.LEG_TOP_Z, "M21e OPEN (pad under ring)", dx=-10, dy=14, ha="right")
    K.tag(ex, 183.3, 86.0, "M20 OPEN (the seat): 84.38..87.62", dx=-40, dy=-18, ha="right")
    ex.text(139, 121, "ELEVATION of the east-front leg (X-Z), case frame;\nthe other three mirror it. 6.0 6061-T6, 4 off, about 12.6 g each.", fontsize=6.0, va="top")
    ex.set_xlim(138, 212); ex.set_ylim(-12, 122)
    # locator and wedge notes
    nx = fig.add_axes([0.805, 0.28, 0.19, 0.70]); nx.axis("off")
    import textwrap as _t
    paras = [
        "LOCATOR (printed, PETG or PLA, 4 off). With the frame face down on the bench its key drops into a window corner and registers on both window faces "
        "(R 6.35 corner); its slot (pad + 0.2) holds the leg's pad at |X| 175.40..180.17, |Y| 106.4..112.4 on the ring's underside while the VHB 5952 pad cures. "
        "Its body keeps 1.0 inside the skirt's R 17.53 inner corner. It places a leg to 0.30 against the window (INFERRED; T2 measures it). leg-locator.step.",
        "WEDGES (printed, 2 pairs). 0 to 2.0 over 40, 10 wide, depth marks every 10; pushed between the skirt and the walls at the middle of opposite walls to "
        "equal marks; Peli's four screws driven; the wedges removed; the o-ring fitted. Centring +-0.20 (INFERRED). wedge.step.",
        "ORDER (the ASSEMBLY.md draft, C6). Legs bonded to the frame on the bench; the frame lowered on its legs into the case; centred; Peli's screws; the "
        "o-ring; the stack goes in; the face plate goes on last, ten 6-32 x 1/2 in by hand, no pressure (Peli step 4).",
        "LIFT-OUT. The plate lifts off; the frame and legs stay in the case (the stack clears the window by 8.25 per side at the worst, M7 MET).",
        "LOADS (C6, INFERRED). Pad 4.77 x 6.00 = 28.6 mm2: a 25 N face over four legs bears 0.22 MPa; a 100 g shock on a 2.5 kg face 21.4 MPa per pad, which the "
        "frame's polymer (not stated by Peli, TBD) is to carry; the column buckles at about 4650 N (pinned). T8 tests the VHB bond on the frame's polymer.",
        "LEG. 6.0 6061-T6, waterjet or laser from frame-leg.dxf, edges broken, 4 off (two are mirror images: cut the profile, flip it). Mass about 12.6 g each "
        "(the CAD's volume; CASE-MARGINS.md estimated 11.8)."]
    y = 1.0
    for para in paras:
        t = nx.text(0, y, "\n".join(_t.wrap(para, 64)), fontsize=5.7, va="top", linespacing=1.1)
        y -= (len(_t.wrap(para, 64)) + 0.8) * 5.7 * 1.25 / (0.70 * 11.69 * 72)
    K.rows_box(fig, None, ["M20", "M21a", "M21b", "M21c", "M21d", "M21e", "M21f", "M21g", "M21h", "M5", "M8z", "M1", "M7"])
    K.tolerance_box(fig, None, extra=["The legs' zones (|X| 156.0..180.17, |Y| 106.4..112.4, floor to Z 94.2, each within 0.88 of its place) are theirs alone."])
    save(fig, "frame-and-legs-drawing.pdf", pdf_all)


# ------------------------------------------------------------------ sheet 3: the connector plate (C3)
def sheet_connector(pdf_all):
    P = L.CONN_PLATE
    fig = K.sheet("Connector plate on the back wall (C3): six ruled items, gasket and wall holes", 3, N_SHEETS,
                  IN_COMMON + ["v2/cad/connector_plate.py"], part="case_drawings.py (sheet 3)")
    ax = fig.add_axes([0.01, 0.28, 0.52, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    V = lambda x, z: (-x, z)
    ax.add_patch(Polygon([V(*q) for q in K.rrect_pts(0, (P["z0"] + P["z1"]) / 2, P["x1"] - P["x0"], P["z1"] - P["z0"], P["corner_r"])], closed=True, fill=False, lw=1.0))
    for it in L.CONN_ITEMS:
        x, z = it["c"]; col = RED if it["status"] == "OPEN" else "k"
        ax.add_patch(Circle(V(x, z), it["cutout"] / 2, fill=False, lw=0.8, color=col))
        if it["key"] == "B":
            hw = math.sqrt((it["cutout"] / 2) ** 2 - L.CONN_B_FLAT ** 2)
            ax.plot([V(x, z)[0] - hw, V(x, z)[0] + hw], [z - L.CONN_B_FLAT, z - L.CONN_B_FLAT], lw=0.8, color=col)
        ax.add_patch(Circle(V(x, z), it["wall_hole"] / 2, fill=False, lw=0.4, ls="--", color=GREY))
        kind, s = it["flange"]
        if kind == "sq": ax.add_patch(Rectangle((V(x, z)[0] - s / 2, z - s / 2), s, s, fill=False, lw=0.4, ls=":", color=col))
        else: ax.add_patch(Circle(V(x, z), s / 2, fill=False, lw=0.4, ls=":", color=col))
        if it["screws"]:
            q = it["screws"][0] / 2
            for dx in (-q, q):
                for dz in (-q, q): ax.add_patch(Circle(V(x + dx, z + dz), 1.25, fill=False, lw=0.5))
        ax.text(V(x, z)[0], z, it["key"], fontsize=9, ha="center", va="center", fontweight="bold", color=col)
        ax.text(V(x, z)[0], z - it["cutout"] / 2 - 1.2, "(%.1f, %.1f)" % (x, z), fontsize=4.8, ha="center", va="top")
    for (x, z) in P["screws"]:
        ax.add_patch(Circle(V(x, z), P["screw_hole"] / 2, fill=False, lw=0.7)); ax.add_patch(Circle(V(x, z), 5.0, fill=False, lw=0.3, ls=":", color=GREY))
    K.dim_h(ax, -P["x1"], -P["x0"], P["z1"], "114.0 +-0.10 (case X %.1f..%.1f)" % (P["x0"], P["x1"]), off=7)
    K.dim_v(ax, -P["x0"], P["z0"], P["z1"], "68.3 (case Z %.1f..%.1f)" % (P["z0"], P["z1"]), off=8)
    K.dim_h(ax, -51.1, 51.1, P["z0"], "screw columns 102.2 (X +-51.1)", off=-6, fs=5.5)
    K.dim_v(ax, -P["x1"], 24.2, 76.0, "rows Z 24.2 / 50.1 / 76.0", off=-8, fs=5.5)
    ax.plot([-60, 60], [0, 0], lw=0.4, color=GREY); ax.text(-60, 0.8, "cavity floor Z 0 (inside); outer bottom radius flat from about Z 15.9", fontsize=5, color=GREY)
    ax.plot([-58.93, -58.93], [10, 95], lw=0.4, color=GREY, ls="--"); ax.plot([58.93, 58.93], [10, 95], lw=0.4, color=GREY, ls="--")
    ax.text(-58.93, 96, "hinge fairing\nbase |X| 58.93", fontsize=4.8, ha="center", color=GREY); ax.text(58.93, 96, "hinge fairing\nbase |X| 58.93", fontsize=4.8, ha="center", color=GREY)
    K.tag(ax, 57.0, 60.0, "M14i OPEN", dx=12, dy=12)
    K.tag(ax, 0.0, P["z0"], "M14b OPEN (bottom edge)", dx=-10, dy=-11)
    K.tag(ax, -4.6, 81.5, "M14a OPEN (D's body top 81.5 inside, skirt above)", dx=-35, dy=18, ha="right")
    K.tag(ax, 51.1, 24.2, "M14m OPEN (band)", dx=12, dy=-8)
    ax.text(0, 104, "SEEN FROM OUTSIDE THE BACK WALL: case +X (east) on your LEFT. Solid: plate cut-outs (red: the pick is OPEN, cut-out PROVISIONAL);\n"
                    "dashed: the wall hole under it; dotted: the part's flange or body on the plate face; small circles: M3 tapped (drill 2.5).", fontsize=5.8, ha="center")
    ax.set_xlim(-75, 75); ax.set_ylim(-4, 110)
    # item table
    tx = fig.add_axes([0.54, 0.28, 0.45, 0.70]); tx.axis("off")
    lines = ["ITEMS (panel1450.CONN_ITEMS; centre in case X, Z; plate cut-out / wall hole; flange screws)"]
    for it in L.CONN_ITEMS:
        lines.append("%s  (%+.1f, %.1f)  cut-out %s  wall %.0f  %s  [%s]" % (it["key"], it["c"][0], it["c"][1],
                     ("%.2f" % it["cutout"]) + (" D, flat %.2f to -Z" % L.CONN_B_FLAT if it["key"] == "B" else ""), it["wall_hole"],
                     ("4 x M3 on %.2f sq" % it["screws"][0]) if it["screws"] else "no flange screws", it["status"]))
        import textwrap as _t
        lines += ["     " + s for s in _t.wrap(it["what"], 92)]
    lines += ["", "PLATE: %s, %.1f thick, R %.1f corners, edges broken; %s." % (P["material"], P["t"], P["corner_r"], P["screw"]),
              "GASKET: 2.0 closed-cell EPDM or neoprene, the plate's outline, holes = the wall holes (connector-plate-gasket.dxf).",
              "Flanges of A, C and D on Glenair 930-001 flange gaskets (0.76), M3 x 10 A2 into the plate's threads; nothing stands proud of the back.",
              "WALL (1:1 template, back-wall sheet): hole saws 29 (A, B, D), 22 (C), 18 (E), drill 8 (F) and six 4.5; marked +-0.3 (INFERRED).",
              "STACK THROUGH THE WALL: flange gasket 0.76 + plate 5.0 + gasket 2.0 (1.5 compressed) + wall 5.34 (DXF A-A).",
              "INSIDE: A's patch plug under B16 and U51 and outboard of A22 (M14e, M14f); B's lead bent down at R 28 (M14g, M14h);",
              "C's cores turned down within 12 (M14d); D's right-angle USB-A plug, cable down, within 20.0 (M14c); F's bonding strap to A's ground.",
              "OPEN PICKS (section 6 of CASE-MARGINS.md): the sealed RJ45 (a shell 15 envelope rated 54 V: the Bulgin PX0833 fails both),",
              "the PXP4043/C panel drawing, the M8 receptacle's sheet, the pod and the stud. Until each is picked its cut-out stays PROVISIONAL."]
    import textwrap as _tw
    wrapped = []
    for ln in lines:
        wrapped += (_tw.wrap(ln, 130, subsequent_indent="     ") or [""])
    tx.text(0, 1, "\n".join(wrapped), fontsize=5.9, va="top", family="sans-serif")
    K.rows_box(fig, None, ["M14a", "M14b", "M14i", "M14j", "M14k", "M14l", "M14m", "M14n", "M14o", "M14p", "M14c", "M14d", "M14e", "M14f", "M14g", "M14h"])
    K.tolerance_box(fig, None, extra=["Each part floats on its fixings (A's and D's flanges 0.24 on M3, C's 0.29, B's body 0.30, E's 0.33, F's 0.30, "
                                                            "each M4 0.33); M14j and M14k carry those floats and two machined places per pair."])
    save(fig, "connector-plate-drawing.pdf", pdf_all)


# ------------------------------------------------------------------ sheet 4: the RF entry plates (C4) and the arrestor clamp
def sheet_rf(pdf_all):
    R = L.RF_PLATE
    fig = K.sheet("RF entry plates on the end walls (C2, C4): the arrestors as the antenna bulkheads", 4, N_SHEETS,
                  IN_COMMON + ["v2/cad/rf_entry_plate.py", "v2/vendor/polyphaser/polyphaser-gth-sff-al-sma-surge-protector.pdf"], part="case_drawings.py (sheet 4)")
    for k, (wall, sites, sgn, rect) in enumerate((("EAST", L.WALL_EAST, 1.0, [0.01, 0.635, 0.60, 0.35]), ("WEST", L.WALL_WEST, -1.0, [0.01, 0.285, 0.60, 0.35]))):
        ax = fig.add_axes(rect); ax.set_aspect("equal"); ax.axis("off")
        V = lambda y, z: (sgn * y, z)
        ax.add_patch(Polygon([V(*q) for q in K.rrect_pts(0, (R["z0"] + R["z1"]) / 2, 2 * R["y"], R["z1"] - R["z0"], R["corner_r"])], closed=True, fill=False, lw=1.0))
        for name, y in sites:
            ax.add_patch(Circle(V(y, L.SMA_Z), R["hole"] / 2, fill=False, lw=0.8))
            ax.add_patch(Circle(V(y, L.SMA_Z), R["spot"][0] / 2, fill=False, lw=0.4, ls="--"))
            ax.add_patch(Circle(V(y, L.SMA_Z), R["wall_hole"] / 2, fill=False, lw=0.3, ls=":", color=GREY))
            ax.text(V(y, 0)[0], R["z1"] + 2.5, name, fontsize=5.5, ha="center", rotation=0)
        for (y, z) in R["screws"]:
            ax.add_patch(Circle(V(y, z), 1.65, fill=False, lw=0.6))
        ax.plot([-118, 118], [0, 0], lw=0.4, color=GREY); ax.text(-118, 1.0, "cavity floor Z 0", fontsize=5, color=GREY)
        for ry in (-76.2, 0.0, 76.2):
            ax.plot([ry, ry], [26.42, 84.58], lw=0.3, color=GREY, ls=":")
        ax.text(76.2, 86.0, "inner ribs at Y 0, +-76.2\n(inside, Z 26.4..84.6)", fontsize=4.5, color=GREY, ha="center")
        for fy in (-79.0, 0.0, 79.0):
            ax.add_patch(matplotlib_ellipse(fy, 92.4))
        ax.text(0, 98.5, "end-wall features Y 0, +-79.0 at Z 92.4 (outside)", fontsize=4.8, ha="center", color=GREY)
        K.dim_h(ax, -R["y"], R["y"], R["z0"], "220.2 +-0.10 (case Y +-110.1)", off=-8)
        K.dim_v(ax, V(R["y"], 0)[0] if sgn > 0 else V(-R["y"], 0)[0], R["z0"], R["z1"], "48.9 (Z %.2f..%.2f)" % (R["z0"], R["z1"]), off=10, fs=5.5)
        K.dim_h(ax, V(sites[0][1], 0)[0], V(sites[1][1], 0)[0], L.SMA_Z, "31 pitch", off=13, fs=5.5)
        ax.text(sgn * R["y"] * 0 + (-116 if True else 0), L.SMA_Z, "axis Z %.1f" % L.SMA_Z, fontsize=5.5, ha="right", va="center")
        ax.text(0, 107, "%s WALL, SEEN FROM OUTSIDE: case +Y (the hinge wall) on your %s. %d arrestors, 16.3 through, spot-face 26.0 x 1.5 on the BACK (dashed);"
                " M4 tapped through (drill 3.3) at Y +-45, +-100, Z 40.65 / 77.35; dotted: the 27 mm wall hole" % (wall, "RIGHT" if sgn > 0 else "LEFT", len(sites)),
                fontsize=5.6, ha="center")
        K.tag(ax, V(100, 77.35)[0], 77.35, "M10 OPEN (heads below skirt)", dx=6 * sgn, dy=12, ha="left" if sgn > 0 else "right")
        K.tag(ax, V(-110.1, 0)[0], R["z0"] + 3, "M11c OPEN (band)", dx=-8 * sgn, dy=-14, ha="right" if sgn > 0 else "left")
        ax.set_xlim(-128, 128); ax.set_ylim(-4, 112)
    # section through an arrestor on its plate and the wall
    sx = fig.add_axes([0.615, 0.44, 0.38, 0.54]); sx.set_aspect("equal"); sx.axis("off")
    WALL = 5.34; GC = 1.5; g1 = WALL + GC; p1 = g1 + R["t"]; sd, sdep = R["spot"]; sf = g1 + sdep
    thread = 0.47 * 25.4; o_nom = 0.32; face = p1 + o_nom; t_end = face - thread; jack_in = 0.30 * 25.4; jack_out = 0.35 * 25.4
    body_len = 2.18 * 25.4 - thread - jack_in - jack_out
    for sg in (1, -1):
        sx.add_patch(Polygon([(0, sg * 13.5), (WALL, sg * 13.5), (WALL, sg * 31), (0, sg * 31)], closed=True, fc="#e6e6e6", ec="k", lw=0.5, hatch="///"))
        sx.add_patch(Polygon([(WALL, sg * 13.5), (g1, sg * 13.5), (g1, sg * 24.45), (WALL, sg * 24.45)], closed=True, fc="#444444", ec="k", lw=0.3))
        sx.add_patch(Polygon([(g1, sg * 13.0), (sf, sg * 13.0), (sf, sg * 8.15), (p1, sg * 8.15), (p1, sg * 24.45), (g1, sg * 24.45)], closed=True, fc="#9aa6b2", ec="k", lw=0.6))
    sx.add_patch(Rectangle((sf - 5.0, -12.0), 5.0, 24.0, fc="#e0a000", ec="k", lw=0.5))
    sx.add_patch(Rectangle((t_end, -7.94), thread, 15.88, fc="none", ec=BLUE, lw=0.7, ls="--"))
    sx.add_patch(Rectangle((t_end - jack_in, -3.2), jack_in, 6.4, fc="#dfe7f3", ec=BLUE, lw=0.6))
    sx.add_patch(Rectangle((face, -11.5), body_len, 23.0, fc="#c9d6ea", ec=BLUE, lw=0.7))
    sx.add_patch(Rectangle((face + body_len, -3.2), jack_out, 6.4, fc="#dfe7f3", ec=BLUE, lw=0.6))
    sx.add_patch(Rectangle((p1, -10.0), o_nom, 20.0, fc="#222222", ec="none"))
    sx.add_patch(Rectangle((t_end - jack_in - 10.0, -5.0), 10.0, 10.0, fc="none", ec=RED, lw=0.8, ls="--"))
    sx.plot([-34, 64], [0, 0], lw=0.3, color="k", ls="-.")
    lab = lambda x, y, tx, ty, t, **kw: sx.annotate(t, xy=(x, y), xytext=(tx, ty), fontsize=5.2, arrowprops=dict(arrowstyle="-", lw=0.35), va="center", **kw)
    lab(2.6, 27, -14, 36, "end wall 5.34 (DXF; T5), 27 hole saw")
    lab(g1 - 0.7, 20, 5, 38, "gasket 2.0 closed-cell, 1.5 compressed")
    lab(p1 - 1.0, 18, 22, 34, "RF entry plate 6.0, hole 16.3")
    lab(g1 + 0.7, -12.8, 10, -36, "spot-face 26.0 x 1.5 on the plate's BACK")
    lab(sf - 2.5, -8, -20, -30, "nut + lock washer, class 24.0 x 5.0 (M13b..d)")
    lab(face, 10.5, 30, 26, "O-ring 0.32 +-0.32 (drawn 0.63, not dimensioned)")
    lab(t_end + 4, 7.9, 24, 18, ".47 in 5/8-24 UNEF thread (11.94, reference only)")
    lab(face + 15, 11.5, 28, 16, "arrestor body 23 wide\n(55 x 23 x 31 max overall)")
    lab(t_end - jack_in - 5, 5.0, -28, 16, "jumper plug class: 10.0 beyond the jack,\n5.0 about its axis (M17g, M17x, M18)", color=RED)
    K.dim_h(sx, 0, WALL, -31, "5.34", off=-4, fs=5); K.dim_h(sx, g1, p1, -24.45, "6.0", off=-4, fs=5)
    K.dim_v(sx, p1, -8.15, 8.15, "16.3", off=3.5, fs=5); K.dim_v(sx, -1.0, -13.5, 13.5, "27", off=-2.0, fs=5)
    K.tag(sx, face, -2.0, "M13 OPEN (thread takes O-ring, web 4.5, nut 5.0: +1.20 worst)", dx=8, dy=-30)
    K.tag(sx, 0.5, -12.5, "M13c OPEN (nut radial in the 27)", dx=-4, dy=-10, ha="right")
    sx.text(-34, 40, "SECTION through one arrestor on its axis, the wall's Y horizontal: the case INSIDE to the LEFT. Tightened on the bench, cap up,\n"
                     "ground lug down; one ground lead per plate to stud F outside (GROUNDING-AND-SHIELDS.md, owed). Not to scale for measurement.", fontsize=5.5, va="bottom")
    sx.set_xlim(-34, 64); sx.set_ylim(-42, 44)
    K.rows_box(fig, [0.015, 0.098, 0.97, 0.175], ncols=2, fs=4.9, keys=["M10", "M11", "M11a", "M11b", "M11c", "M11d", "M11e", "M11f", "M11g", "M12", "M12b", "M13", "M13b", "M13c", "M13d", "M18", "M18b", "M18c", "M4c", "M21g",
                                                "M17a", "M17b", "M17c", "M17d", "M17e", "M17f", "M17g", "M17x", "M17w"])
    K.tolerance_box(fig, [0.62, 0.285, 0.37, 0.15], extra=["The arrestor's drawing marks every dimension 'for reference only': its .XX +-0.51 is an unstated allowance; its O-ring, "
                                                            "nut and washer are drawn, not dimensioned (TBD, PolyPhaser). The jumper plug is a class, not a part: M17g and M17x "
                                                            "fail with the class as laid out until the plug is picked (CASE-MARGINS.md 3.4)."])
    save(fig, "rf-entry-plates-drawing.pdf", pdf_all)


def matplotlib_ellipse(y, z):
    from matplotlib.patches import Ellipse
    return Ellipse((y, z), 6.1, 8.94, fill=False, lw=0.4, ec=GREY)


# ------------------------------------------------------------------ sheet 5: the Z stack
def sheet_zstack(pdf_all):
    fig = K.sheet("The Z stack, floor to lid: boards at their committed Z, the face on the legs, the bays read from the boards", 5, N_SHEETS,
                  IN_COMMON + ["v2/cad/zstack.json", "v2/cad/zstack.py"] + [Z["boards"][k]["file"] for k in ("a", "b")], part="case_drawings.py (sheet 5)")
    ax = fig.add_axes([0.01, 0.43, 0.98, 0.555]); ax.axis("off"); ax.set_aspect("equal")
    # the case section (X-Z at Y 0): floor, fillets, drafted walls, shoulder, rim; the lid ceiling
    fx = L.PELI["flat_floor"][0]; R_ = L.PELI["fillet_r"]
    for s in (-1, 1):
        arc = [(s * (fx + R_ * math.sin(t)), R_ - R_ * math.cos(t)) for t in [k * (math.pi / 2) / 30 for k in range(31)]]
        ax.plot([a[0] for a in arc], [a[1] for a in arc], color="k", lw=0.9)
        ax.plot([s * hx(15.32), s * hx(101.04)], [15.32, 101.04], color="k", lw=0.9)
        ax.plot([s * hx(101.04), s * 191.29], [101.04, 108.97], color="k", lw=0.9)
        ax.plot([s * 186.94, s * 186.94], [108.97, 108.97 + 45.47], color=GREY, lw=0.5, ls="--")
    ax.plot([-fx, fx], [0, 0], color="k", lw=0.9)
    ax.plot([-186.94, 186.94], [108.97 + 45.47, 108.97 + 45.47], color=GREY, lw=0.5, ls="--"); ax.text(0, 155.5, "lid inner ceiling 154.44 (STEP), 153.4 on the web page", fontsize=5.5, ha="center", color=GREY)
    # boards
    colours = dict(e="#2e7d32", e5="#558b2f", a="#1565c0", d="#6a1b9a", b="#00838f", c="#ef6c00", p="#795548")
    for k in ("e", "e5", "a", "d", "b", "c"):
        b = Z["boards"][k]; x0, x1 = b["outline"][0], b["outline"][2]
        ax.add_patch(Rectangle((x0, b["z_bottom"]), x1 - x0, b["thickness"], fc=colours[k], ec="k", lw=0.3))
        above = {"e": "a", "a": "b", "d": "b", "b": "c"}
        for side, sg in (("top", 1), ("bottom", -1)):
            t = b["tallest_%s" % side]
            if side == "top" and k in above:
                reg = Z["boards"][above[k]]["outline"]
                cand = [p for p in b["parts"] if p["side"] == "top" and p["height"] is not None and p["rect"][2] > reg[0] and p["rect"][0] < reg[2] and p["rect"][3] > reg[1] and p["rect"][1] < reg[3]]
                t = max(cand, key=lambda p: p["height"]) if cand else None
            if t and t["height"] and t["height"] > 0.5:
                zb = b["z_top"] if sg > 0 else b["z_bottom"] - t["height"]
                ax.add_patch(Rectangle((t["rect"][0], zb), t["rect"][2] - t["rect"][0], t["height"], fc=colours[k], ec="k", lw=0.2, alpha=0.45))
        ax.text(x1 + 1.5, b["z_bottom"] + 0.3, "%s %.2f..%.2f" % (k.upper(), b["z_bottom"], b["z_top"]), fontsize=5.2, color=colours[k], va="bottom")
    # modules: CM5 heatsinks and fans, RockBLOCK, LimeSDR (X extents)
    for (r, h, n, src) in L.B16_MODULES:
        ax.add_patch(Rectangle((r[0], L.B_TOP_Z), r[2] - r[0], h, fill=False, ec=colours["b"], lw=0.5, ls="--"))
    ax.text(-72, L.B_TOP_Z + 22, "CM5 + cooler\n21.0 (TBD)", fontsize=4.8, ha="center", color=colours["b"])
    # the pack block and P (INFERRED place)
    ax.add_patch(Rectangle((L.PACK_WEST_X, 0.0), L.PACK_BLOCK[0], L.PACK_BLOCK[2], fc="#bcaaa4", ec="k", lw=0.4, alpha=0.8))
    ax.text(L.PACK_WEST_X + L.PACK_BLOCK[0] / 2, 18, "4S3P block\n38.1 (A06)", fontsize=5, ha="center")
    # legs, frame, plate, monitor
    import frame_leg as FL
    p = FL.profile_pts(); pts = [p["p8"], p["p0"], p["p1"], p["p2"], p["p3"]]
    for kk in range(1, 20):
        x = fx + (L.LEG["col_x"][1] - fx) * kk / 20.0; pts.append((x, FL.fil_off_z(x)))
    pts += [p["p4"], p["p5"], p["p6"], p["p7"]]
    for s in (-1, 1): ax.add_patch(Polygon([(s * x, z) for x, z in pts], closed=True, fc="#c9d6ea", ec=BLUE, lw=0.5))
    ring_top = L.LEG_TOP_Z + L.PELI["ring_t"]
    for s in (-1, 1):
        ax.add_patch(Rectangle((s * 174.83 if s > 0 else -182.75, L.LEG_TOP_Z), 182.75 - 174.83, L.PELI["ring_t"], fc="#bbbbbb", ec="k", lw=0.4))
        ax.add_patch(Rectangle((s * 183.34 if s > 0 else -189.18, L.FRAME_BOTTOM_Z), 189.18 - 183.34, ring_top - L.FRAME_BOTTOM_Z, fc="#bbbbbb", ec="k", lw=0.4))
    ax.add_patch(Rectangle((-L.PLATE[0] / 2, L.PLATE_UNDER_Z), L.PLATE[0], L.PLATE[2], fc="#9aa6b2", ec="k", lw=0.4))
    X = L.XENARC; bw = X["body"][0]
    ax.add_patch(Rectangle((X["c"][0] - bw / 2, L.FACE_TOP_Z - X["height"]), bw, X["height"], fill=False, ec="k", lw=0.6, ls="-."))
    ax.text(0, L.FACE_TOP_Z - X["height"] + 12, "Xenarc 709GNK body (28.66, TBD)", fontsize=5.3, ha="center")
    ax.text(-298, 150, "SECTION at Y 0, case frame, X east to the right. Each board is drawn at its committed Z with the tallest part of its top side\n"
                       "that lies under the board above it (E under A, A and D under B, B under the backer ring) and the tallest of its underside.", fontsize=5.8, va="top")
    # arrestors outside the end walls at Z 59
    for s in (-1, 1):
        x0 = s * (hx(59) + 5.34 + 1.5 + 6.0)
        ax.add_patch(Rectangle((x0 if s > 0 else x0 - 43.4, 59 - 11.5), 43.4, 23.0, fc="#dfe7f3", ec=BLUE, lw=0.4))
    ax.text(hx(59) + 30, 47, "arrestors Z 59", fontsize=5, ha="center", va="top", color=BLUE)
    # levels and tags
    for zv, label in ((L.FACE_TOP_Z, "face top %.2f (104.77..108.27)" % L.FACE_TOP_Z), (L.LEG_TOP_Z, "leg pad top %.2f" % L.LEG_TOP_Z), (L.FRAME_BOTTOM_Z, "frame bottom %.2f" % L.FRAME_BOTTOM_Z),
                      (L.B_TOP_Z + 21.0, "heatsink top %.2f" % (L.B_TOP_Z + 21.0)), (L.FACE_TOP_Z - X["height"], "monitor body bottom %.2f" % (L.FACE_TOP_Z - X["height"])),
                      (108.97, "Peli rim 108.97"), (101.04, "Peli shoulder 101.04")):
        ax.plot([-235, -200], [zv, zv], lw=0.3, color="k"); ax.text(-236, zv, label, fontsize=5, ha="right", va="center")
    m1 = K.rows()["M1"]
    K.tag(ax, 0, L.B_TOP_Z + 21.0 + 3.0, "M1 %s: %+.2f / %+.2f worst (TBD Xenarc, heatsink, spacers)" % (m1["verdict"], m1["nom"], m1["worst"]), dx=-40, dy=50, ha="right")
    K.tag(ax, 188, 104.5, "M2, M2b OPEN (plate edge under the lid)", dx=-60, dy=30, ha="right")
    K.tag(ax, 150, 44.58, "M6 MET (pack top under B)", dx=40, dy=-28, color="#2e7d32")
    K.tag(ax, 185.5, 86.0, "M20 OPEN (seat)", dx=25, dy=-5)
    K.tag(ax, 95, 25.3, "W4-F17: J_AB2 on A stands 3.10 into D (read from the boards)", dx=60, dy=-30)
    ax.set_xlim(-300, 250); ax.set_ylim(-8, 162)
    # the tables
    lines = ["THE STACK FROM THE FLOOR (panel1450.STACK)"]
    z = 0.0
    for n, t in L.STACK:
        lines.append("  %-34s %6.2f .. %6.2f" % (n, z, z + t)); z += t
    lines.append("  %-34s %6.2f" % ("B top copper (B_TOP_Z)", L.B_TOP_Z))
    lines.append("  %-34s %6.2f .. %6.2f" % ("D on 6.0 standoffs", Z["boards"]["d"]["z_bottom"], Z["boards"]["d"]["z_top"]))
    lines.append("  %-34s %6.2f .. %6.2f" % ("E5 dock block (face 7.4 over E)", Z["boards"]["e5"]["z_bottom"], Z["boards"]["e5"]["z_top"]))
    lines.append("  %-34s %6.2f .. %6.2f" % ("C backer ring (10 under the plate)", Z["boards"]["c"]["z_bottom"], Z["boards"]["c"]["z_top"]))
    lines.append("  %-34s %6.2f .. %6.2f" % ("face plate on the frame ring", L.PLATE_UNDER_Z, L.FACE_TOP_Z))
    lines.append("  P: Z not set until the pack hold-down (S-27)")
    fig.add_axes([0.015, 0.28, 0.24, 0.145]).axis("off"); fig.axes[-1].text(0, 1, "\n".join(lines), fontsize=5.3, va="top", family="monospace")
    bl = ["BAYS READ FROM THE BOARDS (gap - lower part - upper part where they overlap in plan)"]
    for name, bay in Z["bays"].items():
        worst = bay["pairs"][0] if bay["pairs"] else None
        single = bay["tightest_single"][0] if bay["tightest_single"] else None
        bl.append("%s: gap %.2f" % (name, bay["gap"]))
        if worst: bl.append("   pair %s %.2f under %s %.2f: %+.2f%s" % (worst["lower"], worst["lower_h"], worst["upper"], worst["upper_h"], worst["clearance"], " (mate)" if worst["mate"] else ""))
        if single: bl.append("   tallest single %s %.2f (%s): leaves %+.2f" % (single["ref"], single["height"], single["where"], single["clearance"]))
    half = (len(bl) + 1) // 2
    for c, chunk in enumerate((bl[:half], bl[half:])):
        a = fig.add_axes([0.26 + c * 0.25, 0.28, 0.25, 0.145]); a.axis("off"); a.text(0, 1, "\n".join(chunk), fontsize=5.1, va="top", family="monospace")
    m = Z["monitor"]
    ml = ["B's parts under the monitor (body bottom %.2f):" % m["body_bottom_z"]] + ["   %s h %.2f leaves %+.2f" % (x["ref"], x["height"], x["clearance"]) for x in m["b_parts_under"][:4]]
    ml += ["B's underside over the pack pocket: %s %.2f," % (Z["pack_pocket"]["b_underside_tallest"]["ref"], Z["pack_pocket"]["b_underside_tallest"]["height"]),
           "   lowest Z %.2f" % Z["pack_pocket"]["lowest_z"], "",
           "Heights: each footprint's own KiCad 9 library model", "(kicad-packages3D 9.0.9); SUBSTITUTE where the named", "model file is missing; CLASS or MAKER where the",
           "footprint names none (zstack.py HEIGHT_CLASSES)."]
    a = fig.add_axes([0.765, 0.28, 0.22, 0.145]); a.axis("off"); a.text(0, 1, "\n".join(ml), fontsize=5.1, va="top", family="monospace")
    K.rows_box(fig, None, ["M1", "M2", "M2b", "M3", "M6", "M8z", "M20", "M4a", "M5", "M15a", "M15b"])
    K.tolerance_box(fig, None, extra=["Stack: JLC 1.6 +-0.16 per board and 3M VHB 5952 1.1 +-10 % (VERIFIED); the gap and bay spacers are unnamed (TBD); "
                                                            "B bow 0.3 (INFERRED). The section is at Y 0 with each board's tallest part drawn at its own X."])
    save(fig, "z-stack-drawing.pdf", pdf_all)


# ------------------------------------------------------------------ sheet 6: the case floor in plan (mounting and access)
def sheet_plan(pdf_all):
    fig = K.sheet("The case in plan: boards, rods, legs, pack group, wall plates, jacks and dock clamps", 6, N_SHEETS,
                  IN_COMMON + ["v2/cad/zstack.json"], part="case_drawings.py (sheet 6)")
    ax = fig.add_axes([0.005, 0.28, 0.69, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Polygon(K.rrect_pts(0, 0, INNER_Z15[0], INNER_Z15[1], 15.88), closed=True, fill=False, lw=0.9))
    ax.add_patch(Polygon(K.rrect_pts(0, 0, FLAT[0], FLAT[1], 0.01), closed=True, fill=False, lw=0.4, ls="--", color=GREY))
    ax.add_patch(Polygon(K.rrect_pts(0, 0, L.WINDOW[0], L.WINDOW[1], WIN_R), closed=True, fill=False, lw=0.4, ls="-.", color=GREY))
    ax.text(-FLAT[0] / 2 + 2, -FLAT[1] / 2 + 2, "flat floor (fillet tangents)", fontsize=5, color=GREY)
    colours = dict(e="#2e7d32", e5="#558b2f", a="#1565c0", d="#6a1b9a", b="#00838f", c="#ef6c00", p="#795548")
    for k in ("b", "a", "d", "e", "e5", "p"):
        b = Z["boards"][k]; o = b["outline"]
        ax.add_patch(Rectangle((o[0], o[1]), o[2] - o[0], o[3] - o[1], fill=False, ec=colours[k], lw=0.9 if k in ("a", "b") else 0.7, ls="-" if k != "p" else "--"))
        ax.text(o[0] + 1.5, o[3] - 1.5, "%s  %s" % (k.upper(), b["file"].split("/")[-2]), fontsize=5.5, va="top", color=colours[k])
        for h in b["holes"]:
            if h["drill"] >= 2.5: ax.add_patch(Circle((h["x"], h["y"]), h["drill"] / 2, fill=False, ec=colours[k], lw=0.5))
    ax.add_patch(Rectangle((L.PACK_WEST_X, -L.PACK_GROUP_LEN / 2 + 72.0), L.PACK_BLOCK[0], L.PACK_BLOCK[1], fc="#bcaaa4", ec="k", lw=0.4, alpha=0.6))
    ax.text(L.PACK_WEST_X + 28, 40, "4S3P block\n(A06)", fontsize=5.5, ha="center")
    G = L.LEG
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * G["foot_x"][0], sx * G["col_x"][1])); y0, y1 = sorted((sy * G["y"][0], sy * G["y"][1]))
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc=BLUE, ec=BLUE, alpha=0.5))
    for (x, y) in ((-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)):
        ax.plot([x], [y], marker="+", ms=8, color="k")
    # wall plates, jacks and clamps
    P = L.CONN_PLATE
    ax.add_patch(Rectangle((P["x0"], hy(50) + 5.34), P["x1"] - P["x0"], 2.0 + P["t"], fc="#9aa6b2", ec="k", lw=0.4))
    for it in L.CONN_ITEMS: ax.text(it["c"][0], hy(50) + 16, it["key"], fontsize=5.5, ha="center")
    ax.text(62, hy(50) + 10, "connector plate (C3),\nX -57..57, Z 18.3..86.6", fontsize=5.0, ha="left", va="center")
    for wall, sites, s in (("east", L.WALL_EAST, 1), ("west", L.WALL_WEST, -1)):
        xw = s * (hx(59) + 5.34 + 1.5)
        ax.add_patch(Rectangle((xw if s > 0 else xw - 6.0, -L.RF_PLATE["y"]), 6.0, 2 * L.RF_PLATE["y"], fc="#9aa6b2", ec="k", lw=0.4))
        for name, y in sites:
            x0 = xw + s * 6.0
            ax.add_patch(Rectangle((x0 if s > 0 else x0 - 36.0, y - 11.5), 36.0, 23.0, fc="#dfe7f3", ec=BLUE, lw=0.4))
            ax.text(x0 + s * 38.5, y, name, fontsize=4.8, ha="left" if s > 0 else "right", va="center")
    for name, x in [("VHF", -52), ("HF", -38), ("WIFI 2.4", -24), ("GNSS", -10), ("SDR", 4), ("P2P A", 18), ("P2P B", 32), ("5G MAIN", 60), ("5G DIV", 74), ("IRIDIUM", 88), ("LORA", 100)]:
        ax.plot([x], [-66], marker="o", ms=2.5, color="#2e7d32")
    ax.plot([46], [-66], marker="o", ms=3, mfc="none", color=RED); ax.text(46, -60, "ANT3 X +46\n(no clamp yet)", fontsize=4.5, ha="center", color=RED)
    ax.text(-52, -72, "E's float clamps at Y -66 (A's RF_X)", fontsize=5, color="#2e7d32")
    # tags
    K.tag(ax, 150.3, 60, "M4a, M5 OPEN (pack placed by hand)", dx=-10, dy=48, ha="right")
    K.tag(ax, 165, -20, "M17x OPEN, FAILS AS ASSUMED: B's east edge X 165", dx=-30, dy=-55, ha="right")
    K.tag(ax, 165, -80, "M18 OPEN (plugs to B's east-end parts)", dx=-5, dy=-40, ha="right")
    K.tag(ax, -110.5, 73, "W4-F7 OPEN: the rod stack is held by VHB only;\nthe north rods have no foot", dx=-10, dy=35, ha="right")
    K.tag(ax, -130.0, -113, "M15b OPEN (strip corner pads)", dx=-10, dy=-12, ha="right")
    K.tag(ax, -57, hy(50) + 6, "M14i OPEN", dx=-30, dy=12, ha="right")
    K.tag(ax, 0, -116.9, "M7 MET: lift-out through the window", dx=40, dy=-14, color="#2e7d32")
    ax.text(0, 162, "PLAN, case frame, seen from above: inner wall at the fillet tangent Z 15.32 (375.01 x 260.71), flat floor dashed, frame window dash-dot;\n"
                    "boards at their committed outlines with their mounting holes; legs blue; rods +; arrestors outside the end walls; the back wall at the top.", fontsize=5.8, ha="center")
    ax.set_xlim(-268, 252); ax.set_ylim(-150, 170)
    tx = fig.add_axes([0.70, 0.28, 0.29, 0.70]); tx.axis("off")
    lines = ["MOUNTING (read from the committed boards)"]
    for k in ("e", "e5", "a", "d", "b", "c", "p"):
        b = Z["boards"][k]; hs = [h for h in b["holes"] if h["drill"] >= 2.0]
        lines.append("%s: %d holes >= 2.0: %s" % (k.upper(), len(hs), ", ".join(sorted(set("%.1f" % h["drill"] for h in hs)))))
    lines += ["", "RETENTION (what holds what)",
              "- face plate: ten 6-32 x 1/2 in into Peli's inserts (C1)",
              "- frame: Peli's four self-tapping screws; the legs in compression",
              "- rod stack (E, A, B on four M3 rods at +-110.5, +-73): the dock",
              "  strip's VHB 5952 pads only; the north rods have no foot (W4-F7,",
              "  OPEN; proposal RF-1 not ruled; T8 bond test)",
              "- D on A: four M3 x 6 standoffs; C under the plate: eight PEM",
              "  SO-M3-10 standoffs; E5 on E: M3 standoffs",
              "- pack group: NOT DESIGNED (S-27, CON-006); placed by hand in",
              "  this drawing (M4a, M5 OPEN)",
              "- RockBLOCK 9704: four M4 on its bracket (H17..H20); fastener",
              "  type and drop owed (ASSEMBLY.md)",
              "", "ACCESS",
              "- lift-out: plate off, frame and legs stay; the stack clears the",
              "  window by 8.25 per side at the worst (M7 MET)",
              "- back wall: six items on the connector plate (C3); four picks OPEN",
              "- end walls: twelve arrestors on two entry plates (C2, C4), jumpers",
              "  to E's clamps on planned routes (every jumper row OPEN)",
              "- service ports on B (J_FLASH1..3, USB-C) and headers reachable",
              "  only with the plate off"]
    tx.text(0, 1, "\n".join(lines), fontsize=5.8, va="top", family="monospace")
    K.rows_box(fig, None, ["M4a", "M4b", "M5", "M7", "M15a", "M15b", "M16", "M17x", "M18", "M14i", "M21f"])
    K.tolerance_box(fig, None)
    save(fig, "case-plan-drawing.pdf", pdf_all)


# ------------------------------------------------------------------ sheets 7..13: the board envelopes
def band_colour(h):
    if h is None: return "#ff00ff"
    for lim, c in ((0.01, "#f2f2f2"), (1.0, "#d9f0d3"), (3.0, "#a6dba0"), (6.0, "#fee08b"), (10.0, "#fdae61"), (99.0, "#d73027")):
        if h <= lim: return c
    return "#d73027"


def sheet_board(k, number, pdf_all):
    b = Z["boards"][k]
    names = dict(e="E dock strip", e5="E5 dock block", a="A power and I/O", d="D APRS mezzanine", b="B compute", c="C panel backer ring", p="P pack BMS")
    fig = K.sheet("Board envelope %s: outline, holes and parts by height on both sides, read from the committed board" % names[k], number, N_SHEETS,
                  ["v2/cad/zstack.json", "v2/cad/zstack.py", b["file"], "v2/cad/zstack-models.json"], part="case_drawings.py (sheet %d)" % number)
    o = b["outline"]; w, h = o[2] - o[0], o[3] - o[1]
    for i, side in enumerate(("top", "bottom")):
        ax = fig.add_axes([0.005 + 0.4975 * i, 0.39, 0.4925, 0.595]); ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Rectangle((o[0], o[1]), w, h, fill=False, lw=1.0))
        for p in sorted(b["parts"], key=lambda p: (p["height"] or 0)):
            if p["side"] != side: continue
            r = p["rect"]
            if p["height"] is None:
                fc, hatch = ("#dddddd", "//") if p["klass"] in ("COVERED", "PANEL", "MATES") else ("#ff00ff", "xx")
            else:
                fc, hatch = band_colour(p["height"]), None
            ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], fc=fc, ec="k", lw=0.15, hatch=hatch))
            if p["height"] is not None and p["height"] >= 5.0:
                ax.text((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, "%s\n%.1f" % (p["ref"], p["height"]), fontsize=3.6, ha="center", va="center")
        for hh in b["holes"]:
            ax.add_patch(Circle((hh["x"], hh["y"]), hh["drill"] / 2, fill=False, lw=0.6, color="k"))
            if hh["drill"] >= 2.5: ax.text(hh["x"], hh["y"] - hh["drill"] / 2 - 0.8, "%.1f" % hh["drill"], fontsize=3.8, ha="center", va="top")
        if k == "b" and side == "top":
            for (r, hh_, n, src) in L.B16_MODULES:
                ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], fill=False, ec="#00838f", lw=0.8, ls="--"))
                ax.text(r[0] + 1, r[3] - 1, "%s %.1f" % (n, hh_), fontsize=3.8, va="top", color="#00838f")
            ax.add_patch(Rectangle((113.0, -99.0), 52.0, 56.0, fill=False, ec=RED, lw=0.4))
            K.tag(ax, 165, 0, "east edge X 165: M17x, M18 OPEN", dx=-20, dy=-110, ha="right")
        if k == "a" and side == "top":
            for pp in b["parts"]:
                if pp["ref"] == "J_AB2":
                    K.tag(ax, (pp["rect"][0] + pp["rect"][2]) / 2, pp["rect"][3], "J_AB2 9.1 under D (6.0 bay): W4-F17 OPEN", dx=-10, dy=40, ha="right")
            ax.add_patch(Rectangle((0.0, -40.0), 100.0, 80.0, fill=False, ec="#6a1b9a", lw=0.6, ls="--")); ax.text(1, 39, "D outline", fontsize=4.5, va="top", color="#6a1b9a")
        ax.text((o[0] + o[2]) / 2, o[3] + h * 0.04, "%s SIDE (%s)" % (side.upper(), "seen from above" if side == "top" else "seen from above, through the board: not mirrored"),
                fontsize=6.5, ha="center", va="bottom", fontweight="bold")
        K.dim_h(ax, o[0], o[2], o[1], "%.1f" % w, off=-h * 0.05, fs=5.5); K.dim_v(ax, o[0], o[1], o[3], "%.1f" % h, off=-w * 0.03, fs=5.5)
        ax.set_xlim(o[0] - w * 0.08, o[2] + w * 0.03); ax.set_ylim(o[1] - h * 0.12, o[3] + h * 0.10)
    tx = fig.add_axes([0.015, 0.28, 0.97, 0.105]); tx.axis("off")
    tt, tb = b["tallest_top"], b["tallest_bottom"]
    cls = {}
    for p in b["parts"]: cls[p["klass"]] = cls.get(p["klass"], 0) + 1
    lines = ["%s  sha256 %s  (%s)" % (b["file"], b["sha256"][:16], b["place"]),
             "outline X %.2f..%.2f, Y %.2f..%.2f (case frame), thickness %.2f (the file's), Z %s" % (o[0], o[2], o[1], o[3], b["thickness"],
             "%.2f..%.2f" % (b["z_bottom"], b["z_top"]) if b["z_bottom"] is not None else "not set (pack hold-down undesigned)"),
             "tallest top: %s; tallest bottom: %s" % ("%s %.2f (%s)" % (tt["ref"], tt["height"], tt["lib"]) if tt else "none",
                                                      "%s %.2f (%s)" % (tb["ref"], tb["height"], tb["lib"]) if tb else "none"),
             "parts %d by height source: %s" % (len(b["parts"]), ", ".join("%s %d" % kv for kv in sorted(cls.items()))),
             "holes: %s" % ", ".join("%s %.1f" % (hh["ref"], hh["drill"]) for hh in b["holes"] if hh["drill"] >= 2.0)[:400],
             "colour by height above the board surface: no body, <=1, <=3, <=6, <=10, >10 mm (light grey, greens, yellow, orange, red); grey hatched: a height another record owns "
             "(COVERED by a module envelope, a PANEL part hanging from the plate, a contact that MATES across a bay); magenta cross-hatched: TBD; B's module envelopes dashed."]
    import textwrap as _t
    tx.text(0, 1, "\n".join(sum((_t.wrap(s, 150) for s in lines), [])), fontsize=5.8, va="top", family="monospace")
    # the hole table (27 Sep 2026): every hole of 2.0 or more, its centre in the case frame as the board file places it, so the mounting and
    # the panel cut-outs are dimensioned on the sheet and not only drawn; the plan tolerance is the tolerance box's
    holes = [hh for hh in b["holes"] if hh["drill"] >= 2.0]
    per = 18; ncol = max(1, -(-len(holes) // per))
    for c in range(ncol):
        hx_ = fig.add_axes([0.015 + c * 0.505 / ncol, 0.098, 0.505 / ncol, 0.175]); hx_.axis("off")
        head = "HOLES %d of %d (drill 2.0 or more), centre in the case frame, mm" % (len(holes), len(b["holes"])) if c == 0 else ""
        body = ["%-9s %8s %8s %6s  %s" % ("ref", "X", "Y", "drill", "what")]
        wlen = max(12, int(190 / ncol) - 40)   # monospace at 5.0 pt: about 100 characters per column of two
        for hh in holes[c * per:(c + 1) * per]:
            body.append("%-9s %8.2f %8.2f %6.2f  %s" % (hh["ref"][:9], hh["x"], hh["y"], hh["drill"], (hh.get("what") or "")[:wlen]))
        hx_.text(0, 1, (head + "\n" if head else "\n") + "\n".join(body), fontsize=5.0, va="top", family="monospace", linespacing=1.15)
    K.tolerance_box(fig, None, extra=["Heights are nominal library bodies at the committed placements; a board's plan tolerance is JLC's outline class "
                                                            "(+-0.2, not held) and the stack's placement +-1.0 by hand (INFERRED)."])
    save(fig, "board-envelope-%s.pdf" % k, pdf_all)


# ------------------------------------------------------------------ sheet 14: the QMX lid tray (C5), the part and its place on the lid
def sheet_qmx_tray(pdf_all):
    """The printed tray of v2/cad/lid_bracket_qmx.py, read from its module constants and from the solid it builds, placed where C5 puts it
    (panel1450.QMX_TRAY_X across the case's X, lid_bracket_qmx.PLACE_Y along its Y; the part's local y runs along the case's X, as
    v2/cad/render/scene.py places it). Added 27 Sep 2026 (MESHSAT-1357, the layer 7 fixer c7) because the case set drew every made part of
    C1 to C6 but the tray."""
    import lid_bracket_qmx as Q
    part = Q.build(); bb = part.bounding_box()
    size = (round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3))
    assert size == (Q.LENGTH_OVER_TABS, Q.OL, Q.OH), "the solid (%s) is not the part the constants describe" % (size,)
    X0, X1 = L.QMX_TRAY_X
    assert abs((X1 - X0) - Q.OL) < 1e-9, "panel1450.QMX_TRAY_X must span the tray's width %.1f" % Q.OL
    QX, QY = (X0 + X1) / 2, (Q.PLACE_Y[0] + Q.PLACE_Y[1]) / 2
    to_case = lambda x, y: (QX + y, QY + x)          # part frame (x along the length, y across) -> case frame, lid closed, seen from above
    R = K.rows(); m3, m19 = R["M3"], R["M19"]
    CEIL = L.PELI["rim_z"] + L.PELI["lid_z"]          # the lid's inner ceiling, 154.44 (Peli's STEP)
    CEIL_EDGE_X = X1 + m19["nom"]                     # the lid's flat ceiling ends at X 173.08 (frame_seat.py M19)
    OPEN_FACE_Z = CEIL - Q.OH
    notch_z0 = Q.OH - 4.0 - Q.NOTCH[1] / 2            # the notch box's bottom in the part's z (its top is past the rim)
    fig = K.sheet("The QMX lid tray (C5): the printed part and its place on the lid's inner face, X %.1f to %.1f" % (X0, X1), 14, N_SHEETS,
                  IN_COMMON + ["v2/cad/lid_bracket_qmx.py", "v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf"], part="case_drawings.py (sheet 14)")
    # ---- A: the place on the lid, in plan (case frame, lid closed, seen from above through the lid)
    ax = fig.add_axes([0.005, 0.395, 0.40, 0.59]); ax.set_aspect("equal"); ax.axis("off")
    px, py = L.PLATE[0] / 2, L.PLATE[1] / 2
    ax.plot([60, px - L.PLATE_R], [py, py], lw=0.6, color=GREY); ax.plot([60, px - L.PLATE_R], [-py, -py], lw=0.6, color=GREY)
    ax.add_patch(Arc((px - L.PLATE_R, py - L.PLATE_R), 2 * L.PLATE_R, 2 * L.PLATE_R, theta1=0, theta2=90, lw=0.6, color=GREY))
    ax.add_patch(Arc((px - L.PLATE_R, -py + L.PLATE_R), 2 * L.PLATE_R, 2 * L.PLATE_R, theta1=270, theta2=360, lw=0.6, color=GREY))
    ax.plot([px, px], [-py + L.PLATE_R, py - L.PLATE_R], lw=0.6, color=GREY)
    ax.text(px - 2, -py + 3, "face plate edge (C1)", fontsize=4.8, ha="right", color=GREY)
    xw = L.XENARC["c"][0] + 205.75 / 2
    ax.plot([xw, xw], [L.XENARC["c"][1] - 140.09 / 2, L.XENARC["c"][1] + 140.09 / 2], lw=0.5, color=GREY, ls="-.")
    ax.text(xw - 1.5, L.XENARC["c"][1] - 140.09 / 2 - 2, "monitor window\neast edge %.2f\n(glass flush)" % xw, fontsize=4.6, ha="right", va="top", color=GREY)
    ax.plot([CEIL_EDGE_X, CEIL_EDGE_X], [-py + 4, py - 4], lw=0.8, color=BLUE, ls="--")
    ax.text(CEIL_EDGE_X + 1.2, py - 6, "lid's flat ceiling\nends X %.2f\n(frame_seat.py M19)" % CEIL_EDGE_X, fontsize=4.8, color=BLUE, va="top")
    for ref, (x, y), hole, depth in L.BUTTONS:
        ax.add_patch(Circle((x, y), hole / 2, fill=False, lw=0.5, color=GREY)); ax.text(x, y, ref.replace("SW_", ""), fontsize=4.0, ha="center", va="center", color=GREY)
    for ref, (x, y), name in L.STATUS_LEDS:
        ax.add_patch(Circle((x, y), L.LED_HOLE / 2, fill=False, lw=0.4, color=GREY))
    ax.add_patch(Circle(L.LIGHT_SENSOR[1], L.LED_HOLE / 2, fill=False, lw=0.4, color=GREY))
    cx_, cy_ = L.CAMERA[1]; ax.add_patch(Circle((cx_, cy_), L.CAMERA[2] / 2, fill=False, lw=0.5, color=GREY)); ax.text(cx_, cy_ + 6, "camera window", fontsize=4.4, ha="center", color=GREY)
    # the tray: body, tabs, holes, slots and the notch end
    body = [to_case(x, y) for x, y in K.rrect_pts(0, 0, Q.OW, Q.OL, Q.OUTER_R)]
    ax.add_patch(Polygon(body, closed=True, fc="#fff3d6", ec="k", lw=1.0, alpha=0.6))
    for (tx_, ty_) in Q.TAB_CENTRES:
        c = to_case(tx_, ty_); w, h = Q.TAB[1], Q.TAB[0]
        ax.add_patch(Rectangle((c[0] - w / 2, c[1] - h / 2), w, h, fc="#fff3d6", ec="k", lw=0.7))
    for (hx_, hy_) in Q.HOLE_CENTRES:
        c = to_case(hx_, hy_)
        ax.add_patch(Circle(c, Q.TAB_HOLE / 2, fill=False, lw=0.7)); ax.plot([c[0] - 4, c[0] + 4], [c[1], c[1]], lw=0.3, color="k"); ax.plot([c[0], c[0]], [c[1] - 4, c[1] + 4], lw=0.3, color="k")
        ax.text(c[0], c[1] + (7.5 if c[1] > QY else -7.5), "(%.1f, %.1f)" % c, fontsize=5.0, ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.2))
    for sx in (-1, 1):
        c = to_case(sx * Q.SLOT[2], 0)
        ax.add_patch(Rectangle((c[0] - Q.SLOT[1] / 2, c[1] - Q.SLOT[0] / 2), Q.SLOT[1], Q.SLOT[0], fill=False, lw=0.5))
    for sgn in (-1, 1):
        for sy in (-1, 1):
            c = to_case(sgn * Q.OW / 2, sy * Q.NOTCH[2])
            ax.add_patch(Rectangle((c[0] - Q.NOTCH[0] / 2, c[1] - 1.0), Q.NOTCH[0], 2.0, fill=sgn < 0, fc="#b00020" if sgn < 0 else "none", ec=RED, lw=0.5, ls="-" if sgn < 0 else ":"))
    ax.text(QX, QY + Q.OW / 2 - 6, "QMX tray, lid side\n(tab face on the lid)", fontsize=5.6, ha="center", va="top", fontweight="bold")
    K.tag(ax, QX, QY - Q.OW / 2, "notched end (red) as scene.py places the part;\ndotted: the part turned end for end. The unit's\nconnectors are on BOTH ends: OPEN, note 4", dx=20, dy=-50, ha="center")
    K.dim_h(ax, X0, X1, Q.PLACE_Y[1], "%.1f .. %.1f (%.1f)" % (X0, X1, X1 - X0), off=10)
    K.dim_v(ax, X0, Q.PLACE_Y[0], Q.PLACE_Y[1], "Y %.1f .. %.1f over the tabs (%.1f)" % (Q.PLACE_Y[0], Q.PLACE_Y[1], Q.LENGTH_OVER_TABS), off=-14)
    hc = sorted({to_case(*h) for h in Q.HOLE_CENTRES})
    K.dim_h(ax, hc[0][0], hc[-1][0], Q.PLACE_Y[0], "holes X %.1f / %.1f (%.1f)" % (hc[0][0], hc[-1][0], hc[-1][0] - hc[0][0]), off=-17, fs=5.5)
    K.dim_v(ax, hc[-1][0], hc[0][1], hc[-1][1], "holes Y %.1f / %.1f (%.1f)" % (hc[0][1], hc[-1][1], hc[-1][1] - hc[0][1]), off=16, fs=5.5)
    K.dim_h(ax, X1, CEIL_EDGE_X, -py + 12, "M19 %+.2f" % m19["nom"], off=0, fs=5.2, color="#1b5e20")
    ax.plot([QX - 3, QX + 3], [0, 0], lw=0.3, color=GREY); ax.plot([60, 60], [-3, 3], lw=0.3, color=GREY)
    ax.text(62, 1.0, "Y 0", fontsize=4.6, color=GREY)
    ax.plot([60, 72], [0, 0], lw=0.3, color=GREY)
    ax.text(60, py + 12, "A. PLACE ON THE LID, in plan: case frame (X east, +Y to the hinge wall), lid closed, seen from above through the lid.\n"
                         "Grey: the face under it (plate edge; buttons MAIN, PI, TEST; light guides D1 to D11 and the light sensor at X 128; camera window);\n"
                         "blue: where the lid's ceiling stops being flat.",
            fontsize=5.8, va="bottom")
    ax.set_xlim(52, 200); ax.set_ylim(-py - 18, py + 30)
    # ---- B: section at the tray's centre line (Y %.1f), lid closed
    ax = fig.add_axes([0.41, 0.66, 0.58, 0.325]); ax.set_aspect("equal"); ax.axis("off")
    ax.plot([60, px], [L.FACE_TOP_Z, L.FACE_TOP_Z], lw=0.9, color="k"); ax.plot([60, px], [L.FACE_TOP_Z - L.PLATE[2]] * 2, lw=0.5, color="k")
    ax.plot([px, px], [L.FACE_TOP_Z - L.PLATE[2], L.FACE_TOP_Z], lw=0.5, color="k")
    ax.text(62, L.FACE_TOP_Z + 0.8, "face top Z %.2f (104.77..108.27, M20)" % L.FACE_TOP_Z, fontsize=5.0, va="bottom")
    ax.plot([60, CEIL_EDGE_X], [CEIL, CEIL], lw=0.9, color=BLUE)
    ax.plot([CEIL_EDGE_X, CEIL_EDGE_X + 8], [CEIL, CEIL - 6], lw=0.6, color=BLUE, ls="--")
    ax.text(62, CEIL + 0.8, "lid's inner ceiling Z %.2f (rim %.2f + lid %.2f, Peli STEP)" % (CEIL, L.PELI["rim_z"], L.PELI["lid_z"]), fontsize=5.0, va="bottom", color=BLUE)
    ax.add_patch(Rectangle((X0, OPEN_FACE_Z), X1 - X0, Q.OH, fc="#fff3d6", ec="k", lw=0.9))
    ax.plot([X0, X1], [CEIL - Q.FLOOR] * 2, lw=0.4, color="k", ls="--"); ax.plot([X0 + Q.WALL, X0 + Q.WALL], [OPEN_FACE_Z, CEIL - Q.FLOOR], lw=0.4, color="k", ls="--"); ax.plot([X1 - Q.WALL, X1 - Q.WALL], [OPEN_FACE_Z, CEIL - Q.FLOOR], lw=0.4, color="k", ls="--")
    ux0 = QX - Q.UNIT[1] / 2
    ax.add_patch(Rectangle((ux0, CEIL - Q.FLOOR - Q.UNIT[2]), Q.UNIT[1], Q.UNIT[2], fill=False, ec=GREY, lw=0.6, ls=":"))
    ax.text(QX, CEIL - Q.FLOOR - Q.UNIT[2] / 2, "QMX unit %.0f x %.0f x %.0f\n(generator's figure, not\nin the held manual: TBD)" % Q.UNIT, fontsize=4.6, ha="center", va="center", color=GREY)
    for ref, (x, y), hole, depth in L.BUTTONS:
        if abs(y - QY) < 1e-6:
            ax.plot([x - hole / 2, x + hole / 2], [L.FACE_TOP_Z + 0.4] * 2, lw=1.6, color=RED, ls="--")   # its plate hole only: no height is drawn
            ax.annotate("", xy=(x, L.FACE_TOP_Z + 6.0), xytext=(x, L.FACE_TOP_Z + 0.6), arrowprops=dict(arrowstyle="->", lw=0.5, color=RED, ls="--"))
            ax.text(x, L.FACE_TOP_Z + 6.6, "%s: cap height above the face TBD (C&K sheet), M3" % ref, fontsize=4.6, ha="center", va="bottom", color=RED)
    K.dim_v(ax, X0, L.FACE_TOP_Z, OPEN_FACE_Z, "M3 %+.2f" % m3["nom"], off=-10, fs=5.2, color=RED)
    K.dim_v(ax, X1, OPEN_FACE_Z, CEIL, "%.1f" % Q.OH, off=9, fs=5.2)
    K.dim_h(ax, X0, X1, OPEN_FACE_Z, "%.1f" % (X1 - X0), off=-6, fs=5.2)
    K.dim_h(ax, X1, CEIL_EDGE_X, CEIL, "M19 %+.2f" % m19["nom"], off=5, fs=5.0, color="#1b5e20")
    ax.text(QX, OPEN_FACE_Z - 1.5, "open face of the pocket Z %.2f" % OPEN_FACE_Z, fontsize=4.8, ha="center", va="top")
    ax.text(60, CEIL + 9, "B. SECTION at the tray's centre line (Y %.1f), X east to the right, lid closed. The tray hangs from its tab face on the lid's ceiling;\n"
                          "M3 is the room left over the face's parts (their heights above the face are TBD: C&K and APEM sheets), M19 the tray's east edge inside the flat ceiling." % QY,
            fontsize=5.8, va="bottom")
    ax.set_xlim(58, 200); ax.set_ylim(L.FACE_TOP_Z - 6, CEIL + 22)
    # ---- C: the part, in its own frame (x along the length, y across the width, z up from the tab face)
    ax = fig.add_axes([0.41, 0.395, 0.30, 0.255]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Polygon(K.rrect_pts(0, 0, Q.OW, Q.OL, Q.OUTER_R), closed=True, fill=False, lw=0.9))
    ax.add_patch(Polygon(K.rrect_pts(0, 0, Q.IW, Q.IL, Q.POCKET_R), closed=True, fill=False, lw=0.5, ls="--"))
    for (tx_, ty_), (hx_, hy_) in zip(Q.TAB_CENTRES, Q.HOLE_CENTRES):
        ax.add_patch(Rectangle((tx_ - Q.TAB[0] / 2, ty_ - Q.TAB[1] / 2), Q.TAB[0], Q.TAB[1], fill=False, lw=0.7))
        ax.add_patch(Circle((hx_, hy_), Q.TAB_HOLE / 2, fill=False, lw=0.6))
    for sx in (-1, 1):
        ax.add_patch(Rectangle((sx * Q.SLOT[2] - Q.SLOT[0] / 2, -Q.SLOT[1] / 2), Q.SLOT[0], Q.SLOT[1], fill=False, lw=0.5))
    for sy in (-1, 1):
        ax.add_patch(Rectangle((-Q.OW / 2 - 0.5, sy * Q.NOTCH[2] - Q.NOTCH[0] / 2), Q.WALL + 1.0, Q.NOTCH[0], fc="#b00020", ec=RED, lw=0.4, alpha=0.6))
    K.dim_h(ax, -Q.LENGTH_OVER_TABS / 2, Q.LENGTH_OVER_TABS / 2, Q.OL / 2, "%.1f over the tabs (body %.1f)" % (Q.LENGTH_OVER_TABS, Q.OW), off=7, fs=5.2)
    K.dim_v(ax, Q.LENGTH_OVER_TABS / 2, -Q.OL / 2, Q.OL / 2, "%.1f" % Q.OL, off=6, fs=5.2)
    K.dim_h(ax, Q.HOLE_CENTRES[0][0], Q.HOLE_CENTRES[-1][0], -Q.OL / 2, "4 x d%.1f on %.1f x %.1f" % (Q.TAB_HOLE, 2 * abs(Q.HOLE_CENTRES[0][0]), 2 * abs(Q.HOLE_CENTRES[0][1])), off=-7, fs=5.0)
    K.dim_h(ax, -Q.SLOT[2], Q.SLOT[2], 0, "slots %.0f x %.0f at %.1f" % (Q.SLOT[0], Q.SLOT[1], 2 * Q.SLOT[2]), off=12, fs=4.6)
    ax.text(0, -Q.OL / 2 + 4.5, "pocket %.0f x %.0f R%.0f (dashed), outer R%.0f; tabs %.0f x %.0f x %.0f" % (Q.IW, Q.IL, Q.POCKET_R, Q.OUTER_R, Q.TAB[0], Q.TAB[1], Q.TAB[2]), fontsize=4.6, ha="center")
    ax.text(-Q.OW / 2 + 3, Q.OL / 2 - 3, "notches\n(red)", fontsize=4.6, va="top", color=RED)
    ax.text(-Q.LENGTH_OVER_TABS / 2, Q.OL / 2 + 13, "C. THE PART in its own frame, seen from the open face (x along the length)", fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.LENGTH_OVER_TABS / 2 - 4, Q.LENGTH_OVER_TABS / 2 + 12); ax.set_ylim(-Q.OL / 2 - 12, Q.OL / 2 + 20)
    # ---- D: side and end elevations of the part (z up from the tab face)
    ax = fig.add_axes([0.72, 0.395, 0.27, 0.255]); ax.set_aspect("equal"); ax.axis("off")
    side = [(-Q.OW / 2, 0), (Q.OW / 2, 0), (Q.OW / 2, Q.OH), (Q.OPEN_W / 2, Q.OH), (Q.OPEN_W / 2, Q.FLOOR + Q.LIP_H), (-Q.OPEN_W / 2, Q.FLOOR + Q.LIP_H), (-Q.OPEN_W / 2, Q.OH), (-Q.OW / 2, Q.OH)]
    ax.add_patch(Polygon(side, closed=True, fill=False, lw=0.8))
    for sx in (-1, 1):
        x0 = sx * (Q.OW / 2 - 1.0); x1 = sx * (Q.OW / 2 + Q.TAB[0] - 1.0)
        ax.add_patch(Rectangle((min(x0, x1), 0), abs(x1 - x0), Q.TAB[2], fill=False, lw=0.6))
    ax.plot([-Q.OW / 2, Q.OW / 2], [Q.FLOOR, Q.FLOOR], lw=0.3, ls="--", color="k")
    K.dim_h(ax, -Q.OPEN_W / 2, Q.OPEN_W / 2, Q.OH, "side walls open above the lip, %.1f" % Q.OPEN_W, off=5, fs=4.8)
    K.dim_v(ax, -Q.OW / 2, 0, Q.OH, "%.1f" % Q.OH, off=-5, fs=4.8)
    K.dim_v(ax, Q.OPEN_W / 2 - 6, 0, Q.FLOOR + Q.LIP_H, "%.0f+%.0f" % (Q.FLOOR, Q.LIP_H), off=0, fs=4.4, ext=False)
    ax.text(0, -3, "SIDE (along the length); tabs %.0f thick on the tab face (z 0)" % Q.TAB[2], fontsize=4.8, ha="center", va="top")
    ex = Q.OW / 2 + Q.TAB[0] + Q.OL / 2 + 12
    end = [(ex - Q.OL / 2, 0), (ex + Q.OL / 2, 0), (ex + Q.OL / 2, Q.OH)]
    for sy in (1, -1):
        c = ex + sy * Q.NOTCH[2]
        a, b = c + Q.NOTCH[0] / 2 * (1 if sy > 0 else -1), c - Q.NOTCH[0] / 2 * (1 if sy > 0 else -1)
        end += [(a, Q.OH), (a, notch_z0), (b, notch_z0), (b, Q.OH)]
    end += [(ex - Q.OL / 2, Q.OH)]
    ax.add_patch(Polygon(end, closed=True, fill=False, lw=0.8))
    K.dim_h(ax, ex - Q.OL / 2, ex + Q.OL / 2, 0, "%.1f" % Q.OL, off=-5, fs=4.8)
    K.dim_v(ax, ex + Q.NOTCH[2] + Q.NOTCH[0] / 2, notch_z0, Q.OH, "%.1f" % (Q.OH - notch_z0), off=5, fs=4.4)
    K.dim_h(ax, ex + Q.NOTCH[2] - Q.NOTCH[0] / 2, ex + Q.NOTCH[2] + Q.NOTCH[0] / 2, Q.OH, "%.0f" % Q.NOTCH[0], off=3.5, fs=4.4)
    K.dim_h(ax, ex - Q.NOTCH[2], ex + Q.NOTCH[2], notch_z0, "at %.0f" % (2 * Q.NOTCH[2]), off=-4.5, fs=4.4, ext=False)
    ax.text(ex, -9, "NOTCHED END (-x)", fontsize=4.8, ha="center", va="top")
    ax.text(-Q.OW / 2, Q.OH + 12, "D. ELEVATIONS of the part (z up from its tab face)", fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.OW / 2 - 12, ex + Q.OL / 2 + 10); ax.set_ylim(-14, Q.OH + 18)
    # ---- notes
    notes = [
        "1. PART: v2/cad/lid_bracket_qmx.py (the part of 9 September 2026, unchanged), printed (PETG class), %.1f x %.1f x %.1f over the tabs, "
        "%.0f mm3 (about %.0f g in PETG); lid-tray-qmx/lid-bracket-qmx.step and .stl in this release. Read from the solid the generator builds." % (
            size[0], size[1], size[2], part.volume, part.volume * 1.27e-3),
        "2. PLACE (C5, SC-07): the tray's width across case X %.1f to %.1f (panel1450.QMX_TRAY_X), its length along case Y %.1f to %.1f over the tabs "
        "(lid_bracket_qmx.PLACE_Y, unchanged since 9 Sep 2026), centre (%.1f, %.1f); the tab face on the lid's inner ceiling, the pocket open toward the face." % (
            X0, X1, Q.PLACE_Y[0], Q.PLACE_Y[1], QX, QY),
        "3. FIXING (ASSEMBLY.md, the QMX tray row): four M3 through the tabs' d%.1f holes at X %.1f / %.1f, Y %.1f / %.1f into four nuts bonded to the "
        "lid's unribbed inner face (a 2 mm ABS plate with four PEM nuts, DP8005); the screw length, the nut and the bond's strength are TBD. The hole "
        "pattern is symmetric, so the lid's nuts do not depend on which way the tray is turned." % (Q.TAB_HOLE, hc[0][0], hc[-1][0], hc[0][1], hc[-1][1]),
        "4. OPEN, THE UNIT'S FIT (a made-part item: no board moves on it): the held QMX operating manual (1_04_004, pages 7 to 9) puts the Paddle, "
        "Audio and DC jacks on the unit's left panel and RF (BNC), PTT and USB-C on its right panel. This tray has cable notches in one end wall only "
        "(%.0f wide, %.1f deep from the open face), so the lid harness's DC lead and its USB-C and BNC leads cannot all leave it; the notches' "
        "heights against the jacks are not checked (the manual's panel drawings carry no dimensions) and the unit's %.0f x %.0f x %.0f is the "
        "generator's figure, which the held manual does not state. The tray is revised from the unit's own drawing before it is printed "
        "(v2/docs/CASE-FIT-UNCERTAINTIES.md section 3)." % (Q.NOTCH[0], Q.OH - notch_z0, Q.UNIT[0], Q.UNIT[1], Q.UNIT[2]),
    ]
    tx = fig.add_axes([0.015, 0.28, 0.97, 0.105]); tx.axis("off")
    import textwrap as _t
    tx.text(0, 1, "\n".join(sum((_t.wrap(s, 235, subsequent_indent="   ") for s in notes), [])), fontsize=5.5, va="top")
    K.rows_box(fig, None, ["M3", "M19", "M20"])
    K.tolerance_box(fig, None, extra=["This sheet's part is printed: its tolerances are the printer's and are not stated (TBD); the place is marked "
                                      "on the lid by hand from the case centre and the flat ceiling's edge (+-1.0, INFERRED). M19 carries the lid's wall allowance."])
    save(fig, "lid-tray-qmx-drawing.pdf", pdf_all)


if __name__ == "__main__":
    with PdfPages(os.path.join(OUT, "case-drawings-2-to-14.pdf")) as pdf_all:
        sheet_frame(pdf_all); sheet_connector(pdf_all); sheet_rf(pdf_all); sheet_zstack(pdf_all); sheet_plan(pdf_all)
        for n, k in enumerate(("a", "b", "c", "d", "e", "e5", "p"), 7): sheet_board(k, n, pdf_all)
        sheet_qmx_tray(pdf_all)
    print("CASE-DRAWINGS-DONE")
