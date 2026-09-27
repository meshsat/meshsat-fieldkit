#!/usr/bin/env python3
"""Sheets 14r2-1 and 14r2-2 of the case set: the QMX lid tray r2 placed on the lid, dimensioned, and its three parts (MESHSAT-1357,
27 Sep 2026, S-63 and EQ-24; worktree fnd/w5tray). They supersede sheet 14 (lid-tray-qmx-drawing.pdf) of v2/release/case-2026-09-27/.
Every number is read from v2/cad/lid_tray_qmx_r2.py, v2/ecad/tools/panel1450.py and v2/vendor/peli/1450/frame_seat.out, and the
retention and face-room rows from v2/cad/lid_tray_qmx_r2_check.py; nothing is typed here but the drawing's own layout.
Usage: lid_tray_qmx_r2_drawing.py <out dir>   (matplotlib; v2/cad/requirements-cad.lock). Writes lid-tray-qmx-r2-drawing.pdf and a PNG
of each page at 110 dpi for the read-back."""
import os, sys, textwrap, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import panel1450 as L
import drawing_kit as K
import lid_tray_qmx_r2 as Q
import lid_tray_qmx_r2_check as C
from drawing_kit import plt, Rectangle, Circle, Polygon
from matplotlib.patches import Arc
from matplotlib.backends.backend_pdf import PdfPages

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
RED, GREY, BLUE, GREEN, TRAY, UNITC, PLATEC = "#b00020", "#777777", "#1f4e9a", "#1b5e20", "#f3d9a4", "#d0d0d0", "#b8c7d9"
INPUTS = ["v2/cad/lid_tray_qmx_r2.py", "v2/cad/lid_tray_qmx_r2_check.py", "v2/ecad/tools/panel1450.py", "v2/vendor/peli/1450/frame_seat.out",
          "v2/vendor/qrp-labs/qmx-figures.out", "v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf"]
CEIL = L.PELI["rim_z"] + L.PELI["lid_z"]                        # the lid's inner ceiling, 154.44 (Peli STEP)
ZP = CEIL - Q.BOND - Q.PLATE_T                                  # the tray's mounting face in the case frame
def cz(z): return ZP - z                                        # part z -> case Z, lid closed
def cxy(x, y): return (Q.PLACE_X + y, Q.PLACE_Y + x)            # part (x, y) -> case (X, Y), lid closed, seen from above


def sheet(title, label):
    """drawing_kit.sheet's A3 furniture with this set's own source line."""
    fig = plt.figure(figsize=K.A3, dpi=100); fig.patch.set_facecolor("white")
    fig.add_artist(Rectangle((0.008, 0.008), 0.984, 0.984, transform=fig.transFigure, fill=False, lw=1.0, color="k"))
    tb = fig.add_axes([0.008, 0.008, 0.984, 0.085]); tb.axis("off"); tb.set_xlim(0, 1); tb.set_ylim(0, 1)
    tb.add_patch(Rectangle((0, 0), 1, 1, fill=False, lw=1.0))
    for x in (0.30, 0.62, 0.86): tb.plot([x, x], [0, 1], lw=0.6, color="k")
    tb.text(0.005, 0.92, "MeshSat field kit V2, Peli 1450 case set", fontsize=7.5, fontweight="bold", va="top")
    tb.text(0.005, 0.60, "\n".join(textwrap.wrap(title, 64)), fontsize=8.6, fontweight="bold", va="top", linespacing=1.05)
    tb.text(0.005, 0.04, "MESHSAT-1357, S-63, EQ-24. PROTOTYPE DESIGN: nothing made, printed, bought or fitted.\nSession choices under the owner's standing rule of 26 Sep 2026.", fontsize=5.6, va="bottom")
    src = ["Source: tree %s plus the QMX tray r2 (fnd/w5tray); inputs by sha256 (first 12):" % K.base_commit()]
    src += ["  %s  %s" % (K.sha12(os.path.join(K.REPO, p)), p) for p in INPUTS]
    tb.text(0.305, 0.97, "\n".join(src), fontsize=5.0, va="top", family="monospace")
    tb.text(0.625, 0.95, "\n".join(textwrap.wrap("Generated %s by v2/cad/lid_tray_qmx_r2_drawing.py from the files named left; regenerate with "
                                                "v2/cad/README.md. The editable sources govern; this sheet is a copy. Supersedes sheet 14 "
                                                "(lid-tray-qmx-drawing.pdf, the r1 tray of 9 Sep 2026)." % datetime.date.today().isoformat(), 62)), fontsize=6, va="top")
    tb.text(0.865, 0.80, "Sheet %s" % label, fontsize=10, fontweight="bold", va="top")
    tb.text(0.865, 0.45, "A3, mm\nnot to scale for measurement:\ndimensions govern", fontsize=6.3, va="top")
    return fig


def rect(ax, x0, y0, x1, y1, **kw):
    ax.add_patch(Rectangle((min(x0, x1), min(y0, y1)), abs(x1 - x0), abs(y1 - y0), **kw))


def part_rect_case(ax, x0, x1, y0, y1, **kw):
    a, b = cxy(x0, y0), cxy(x1, y1); rect(ax, a[0], a[1], b[0], b[1], **kw)


def text_block(fig, r, lines, fs=5.4, width=None, title=None, mono=False):
    ax = fig.add_axes(r); ax.axis("off")
    width = width or int(r[2] * 16.54 * 72 / (fs * 0.60))
    out = ([title] if title else []) + (list(lines) if mono else sum((textwrap.wrap(s, width, subsequent_indent="   ") for s in lines), []))
    ax.text(0, 1, "\n".join(out), fontsize=fs, va="top", linespacing=1.13, family=("monospace" if mono else "sans-serif"))
    return ax


# ======================================================================================= page 1: the place and the plugs
def page1(pdf):
    fig = sheet("QMX lid tray r2: its place on the lid, the section with the lid closed, both end panels and their plugs", "14r2-1 of 2")
    R = K.rows(); m3, m19 = R["M3"], R["M19"]
    room_nom, room_worst = m3["nom"] + C.R1_TRAY, m3["worst"] + C.R1_TRAY
    # ---- A. plan on the lid (case frame, seen from above through the lid, lid closed)
    ax = fig.add_axes([0.005, 0.285, 0.43, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    px, py = L.PLATE[0] / 2, L.PLATE[1] / 2
    ax.plot([40, px - L.PLATE_R], [py, py], lw=0.6, color=GREY); ax.plot([40, px - L.PLATE_R], [-py, -py], lw=0.6, color=GREY)
    ax.add_patch(Arc((px - L.PLATE_R, py - L.PLATE_R), 2 * L.PLATE_R, 2 * L.PLATE_R, theta1=0, theta2=90, lw=0.6, color=GREY))
    ax.add_patch(Arc((px - L.PLATE_R, -py + L.PLATE_R), 2 * L.PLATE_R, 2 * L.PLATE_R, theta1=270, theta2=360, lw=0.6, color=GREY))
    ax.plot([px, px], [-py + L.PLATE_R, py - L.PLATE_R], lw=0.6, color=GREY)
    ax.text(px - 2, -py + 3, "face plate edge (C1)", fontsize=4.8, ha="right", color=GREY)
    xw = L.XENARC["c"][0] + L.XENARC["window"][0] / 2
    ax.plot([xw, xw], [L.XENARC["c"][1] - L.XENARC["window"][1] / 2, L.XENARC["c"][1] + L.XENARC["window"][1] / 2], lw=0.5, color=GREY, ls="-.")
    ax.text(xw - 1.5, L.XENARC["c"][1] - L.XENARC["window"][1] / 2 - 2, "monitor glass east edge\nX %.2f (flush)" % xw, fontsize=4.4, ha="right", va="top", color=GREY)
    for (fx, fy) in L.XENARC["frame_holes"]:
        if fx > 0: ax.add_patch(Circle((fx, fy), 2.25, fill=False, lw=0.4, color=GREY))
    for ref, (x, y), hole, depth in L.BUTTONS:
        ax.add_patch(Circle((x, y), hole / 2, fill=False, lw=0.5, color=GREY)); ax.text(x, y, ref.replace("SW_", ""), fontsize=4.0, ha="center", va="center", color=GREY)
    for ref, (x, y), name in L.STATUS_LEDS: ax.add_patch(Circle((x, y), L.LED_HOLE / 2, fill=False, lw=0.4, color=GREY))
    ax.add_patch(Circle(L.LIGHT_SENSOR[1], L.LED_HOLE / 2, fill=False, lw=0.4, color=GREY))
    cx_, cy_ = L.CAMERA[1]; ax.add_patch(Circle((cx_, cy_), L.CAMERA[2] / 2, fill=False, lw=0.5, color=GREY))
    ceil_x = Q.EAST_EDGE_X + m19["nom"]; ceil_y = C.LID_FLAT_HALF_Y
    ax.plot([ceil_x, ceil_x], [-ceil_y, ceil_y], lw=0.8, color=BLUE, ls="--"); ax.plot([40, ceil_x], [ceil_y, ceil_y], lw=0.8, color=BLUE, ls="--")
    ax.plot([40, ceil_x], [-ceil_y, -ceil_y], lw=0.8, color=BLUE, ls="--")
    ax.text(ceil_x + 1.0, ceil_y - 3, "lid's flat\nceiling ends\nX %.2f, Y +-%.2f" % (ceil_x, ceil_y), fontsize=4.6, color=BLUE, va="top")
    # the lid plate, the tray base, walls, ledges, lintels, end block and keeper, the unit and its knobs
    part_rect_case(ax, -Q.BASE_X, Q.BASE_X, -Q.BASE_Y, Q.BASE_Y, fc=PLATEC, ec=BLUE, lw=0.6)
    part_rect_case(ax, -Q.BASE_X + 0.8, Q.BASE_X - 0.8, -Q.BASE_Y + 0.8, Q.BASE_Y - 0.8, fc=TRAY, ec="k", lw=0.6, alpha=0.8)
    for sy in (-1, 1): part_rect_case(ax, -Q.FACE_X, Q.FACE_X, sy * Q.SIDE_IN, sy * Q.SIDE_OUT, fc="#c89b45", ec="k", lw=0.5)
    part_rect_case(ax, Q.FACE_X, Q.BASE_X, -Q.BASE_Y + 0.8, Q.BASE_Y - 0.8, fc="#c89b45", ec="k", lw=0.5)
    part_rect_case(ax, -Q.BASE_X, -Q.FACE_X, -Q.SIDE_OUT, Q.SIDE_OUT, fc="#9fb8e0", ec="k", lw=0.5)
    part_rect_case(ax, -Q.U0, Q.U0, -Q.UNIT[1] / 2, Q.UNIT[1] / 2, fc=UNITC, ec="k", lw=0.8, alpha=0.7)
    for sx in (-1, 1):
        kc = cxy(sx * Q.KNOB_X, Q.KNOB_Y)
        ax.add_patch(Circle(kc, Q.KNOB_D / 2, fc="white", ec="k", lw=0.7)); ax.add_patch(Circle(kc, Q.KNOB_D / 2 + Q.FINGER, fill=False, ec=GREEN, lw=0.4, ls=":"))
        ax.text(kc[0], kc[1], "VOL" if sx < 0 else "TUNE", fontsize=4.2, ha="center", va="center")
    for u, v in Q.BUTTONS:
        bc = cxy(-Q.U0 + u, -Q.UNIT[1] / 2 + v); ax.add_patch(Circle(bc, 2.15, fill=False, lw=0.5))
    l0 = cxy(-Q.U0 + Q.LCD[0], Q.UNIT[1] / 2 - Q.LCD[3]); l1 = cxy(-Q.U0 + Q.LCD[1], Q.UNIT[1] / 2 - Q.LCD[2])
    rect(ax, l0[0], l0[1], l1[0], l1[1], fill=False, ec="k", lw=0.5, ls="--")
    ax.text((l0[0] + l1[0]) / 2, (l0[1] + l1[1]) / 2, "QMX\nLCD\nwindow", fontsize=4.4, ha="center", va="center", rotation=90)
    for x, y in Q.PLATE_HOLES:
        c = cxy(x, y); ax.add_patch(Circle(c, 1.7, fill=False, lw=0.5, color=RED)); ax.plot([c[0] - 2.5, c[0] + 2.5], [c[1], c[1]], lw=0.25, color=RED); ax.plot([c[0], c[0]], [c[1] - 2.5, c[1] + 2.5], lw=0.25, color=RED)
    # plugs: each jack's admitted envelope as a band from the panel face outward, and the lead lanes
    for nm, j in Q.JACKS.items():
        sx = 1 if j["panel"] == "R" else -1; r = Q.admitted_radius(nm)
        v0, v1 = min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE
        a = cxy(sx * Q.U0, -Q.UNIT[1] / 2 + v0 - r); b = cxy(sx * (Q.U0 + 38.0), -Q.UNIT[1] / 2 + v1 + r)
        perm = "harness" in j["use"]
        rect(ax, a[0], a[1], b[0], b[1], fc=("#ffe0e0" if perm else "#eeeeee"), ec=(RED if perm else GREY), lw=0.4, alpha=0.7)
        mid = cxy(sx * (Q.U0 + 20.0), -Q.UNIT[1] / 2 + (v0 + v1) / 2)
        ax.text(mid[0], mid[1], "%s\nd %.1f" % (nm, 2 * r), fontsize=4.0, ha="center", va="center", rotation=90)
    ye = Q.PLACE_Y + Q.U0
    def lane(x, y0, turn_r, west=True):
        yb = ceil_y - C.MARGIN - turn_r
        ax.plot([x, x], [y0, yb], lw=1.1, color=RED)
        cx0 = x - turn_r if west else x + turn_r
        ax.add_patch(Arc((cx0, yb), 2 * turn_r, 2 * turn_r, theta1=0 if west else 90, theta2=90 if west else 180, lw=1.1, color=RED))
        ax.plot([cx0, 45], [yb + turn_r, yb + turn_r], lw=1.1, color=RED, ls=(0, (4, 2)))
    xrf = Q.PLACE_X - Q.UNIT[1] / 2 + sum(Q.JACKS["RF"]["v"]) / 2; xusb = Q.PLACE_X - Q.UNIT[1] / 2 + Q.JACKS["USB"]["v"][0]
    lane(xrf, ye + 30, C.RG316_R); lane(xusb, ye + 30, C.LEAD_R)
    xdc = Q.PLACE_X - Q.UNIT[1] / 2 + Q.JACKS["DC"]["v"][0]; yl = Q.PLACE_Y - Q.U0 - 40.0; ybl = -ceil_y + C.MARGIN + C.LEAD_R
    ax.plot([xdc, xdc], [yl + 25, ybl], lw=1.1, color=RED)
    ax.add_patch(Arc((xdc - C.LEAD_R, ybl), 2 * C.LEAD_R, 2 * C.LEAD_R, theta1=180, theta2=360, lw=1.1, color=RED))
    ax.plot([xdc - 2 * C.LEAD_R, xdc - 2 * C.LEAD_R], [ybl, ceil_y - C.MARGIN - C.LEAD_R], lw=1.1, color=RED, ls=(0, (4, 2)))
    ax.text(xrf - 3, ye + 38, "RF: RG-316, R %.1f" % C.RG316_R, fontsize=4.6, color=RED, rotation=90, ha="right", va="bottom")
    ax.text(xusb + 2, ye + 38, "USB-C lead, R %.0f" % C.LEAD_R, fontsize=4.6, color=RED, rotation=90, va="bottom")
    ax.text(xdc - 2 * C.LEAD_R - 2, -40, "DC lead loops back, R %.0f" % C.LEAD_R, fontsize=4.6, color=RED, rotation=90, ha="right", va="center")
    ax.text(47, ceil_y + 1.5, "lid harness along the hinge side (ASSEMBLY step 10) to its crossing of the sealed face: NOT DESIGNED (new open item)",
            fontsize=4.6, color=RED, va="bottom")
    K.dim_h(ax, Q.SPAN_X[0], Q.SPAN_X[1], Q.SPAN_Y[1], "X %.1f .. %.1f (%.1f)" % (Q.SPAN_X[0], Q.SPAN_X[1], 2 * Q.BASE_Y), off=6, fs=5.4)
    K.dim_v(ax, Q.SPAN_X[1], Q.SPAN_Y[0], Q.SPAN_Y[1], "Y %.1f .. %.1f (%.1f)" % (Q.SPAN_Y[0], Q.SPAN_Y[1], 2 * Q.BASE_X), off=9, fs=5.4)
    K.dim_h(ax, Q.EAST_EDGE_X, ceil_x, -ceil_y + 16, "M19 %+.2f" % m19["nom"], off=0, fs=5.0, color=GREEN)
    ux0 = Q.PLACE_X - Q.UNIT[1] / 2
    K.dim_h(ax, ux0, ux0 + Q.UNIT[1], Q.PLACE_Y - Q.U0, "unit %.0f, knob edge west at X %.1f" % (Q.UNIT[1], ux0), off=-14, fs=5.0)
    K.dim_v(ax, ux0, Q.PLACE_Y - Q.U0, Q.PLACE_Y + Q.U0, "unit %.0f: Y %.1f .. %.1f" % (Q.UNIT[0], Q.PLACE_Y - Q.U0, Q.PLACE_Y + Q.U0), off=-26, fs=5.0)
    ax.text(40, ceil_y + 19, "A. PLACE ON THE LID, in plan: case frame (X east, +Y to the hinge wall), lid closed, seen from above through the lid.\n"
                             "Blue: the lid plate (bonded) and where the lid's ceiling stops being flat; tan: the tray; light blue: the keeper; grey: the unit\n"
                             "(its right panel, RF PTT USB, toward the hinge; knob edge west); red crosses: the ten M3 in the plate; red bands: the plugs\n"
                             "each jack admits (permanent leads), grey bands: the operator's jacks (unplugged before the lid closes); red: the lead lanes.",
            fontsize=5.4, va="bottom")
    ax.set_xlim(38, 196); ax.set_ylim(-ceil_y - 6, ceil_y + 34)
    # ---- B. section at the TUNE knob (Y = PLACE_Y + KNOB_X), lid closed: X east to the right, Z up
    ax = fig.add_axes([0.44, 0.60, 0.55, 0.385]); ax.set_aspect("equal"); ax.axis("off")
    ys = Q.PLACE_Y + Q.KNOB_X
    ax.plot([60, px], [L.FACE_TOP_Z] * 2, lw=0.9, color="k"); ax.plot([60, px], [L.FACE_TOP_Z - L.PLATE[2]] * 2, lw=0.5, color="k")
    ax.text(62, L.FACE_TOP_Z - 0.5, "face top Z %.2f (104.77..108.27, M20)" % L.FACE_TOP_Z, fontsize=5.0, va="top")
    ax.plot([60, ceil_x], [CEIL, CEIL], lw=1.0, color=BLUE); ax.plot([ceil_x, ceil_x + 8], [CEIL, CEIL - 6], lw=0.6, color=BLUE, ls="--")
    ax.text(62, CEIL + 0.8, "lid's inner ceiling Z %.2f (Peli STEP); bond %.2f and lid plate %.1f under it" % (CEIL, Q.BOND, Q.PLATE_T), fontsize=5.0, va="bottom", color=BLUE)
    rect(ax, Q.SPAN_X[0], CEIL - Q.BOND, Q.SPAN_X[1], ZP, fc=PLATEC, ec=BLUE, lw=0.5)
    X = lambda y: Q.PLACE_X + y
    rect(ax, X(-Q.BASE_Y), ZP, X(Q.BASE_Y), cz(Q.FLOOR), fc=TRAY, ec="k", lw=0.5)
    for px0, px1 in ((-Q.PAD["size"][1] / 2, Q.PAD["size"][1] / 2),):
        rect(ax, X(px0), ZP, X(px1), cz(Q.Z_UB), fc="#555555", ec="k", lw=0.3)
    ax.text(X(0), cz(Q.Z_UB) + 0.2, "PORON pad", fontsize=4.2, ha="center", va="bottom", color="white")
    for sy in (-1, 1):
        top = Q.Z_TOP if sy > 0 else Q.Z_UT                          # at the knob the knob-edge wall stops at the unit's top face
        rect(ax, X(sy * Q.SIDE_IN), ZP, X(sy * Q.SIDE_OUT), cz(top), fc="#c89b45", ec="k", lw=0.5)
        g = [(X(sy * Q.SIDE_OUT), cz(Q.FLOOR)), (X(sy * (Q.SIDE_OUT + Q.GUSSET["depth"])), cz(Q.FLOOR)), (X(sy * Q.SIDE_OUT), cz(Q.GUSSET["z_top"]))]
        ax.add_patch(Polygon(g, closed=True, fill=False, ec="k", lw=0.4, ls="--"))
    rect(ax, X(Q.SIDE_IN - Q.LEDGE_BACK), cz(Q.Z_UT), X(Q.SIDE_IN), cz(Q.Z_TOP), fc="#c89b45", ec="k", lw=0.5)
    rect(ax, X(-Q.UNIT[1] / 2), cz(Q.Z_UB), X(Q.UNIT[1] / 2), cz(Q.Z_UT), fc=UNITC, ec="k", lw=0.8, alpha=0.8)
    ax.text(X(8), cz((Q.Z_UB + Q.Z_UT) / 2), "QMX %.0f x %.0f x %.0f (maker), 220 g\ntop face (LCD, knobs) toward the face" % Q.UNIT, fontsize=5.0, ha="center", va="center")
    kx = X(Q.KNOB_Y)
    rect(ax, kx - Q.KNOB_D / 2, cz(Q.Z_UT), kx + Q.KNOB_D / 2, cz(Q.Z_UT + Q.KNOB_H), fc="white", ec="k", lw=0.7)
    ax.text(kx, cz(Q.Z_UT + Q.KNOB_H / 2), "TUNE\nknob\n%.1f" % Q.KNOB_H, fontsize=4.2, ha="center", va="center")
    for ref, (x, y), hole, depth in L.BUTTONS:
        ax.plot([x - hole / 2, x + hole / 2], [L.FACE_TOP_Z + 0.4] * 2, lw=1.4, color=RED, ls="--")
    ax.text(150, L.FACE_TOP_Z + 1.2, "buttons at X 150 (other Y), caps TBD", fontsize=4.4, ha="center", va="bottom", color=RED)
    K.dim_v(ax, X(Q.SIDE_OUT) + 3, cz(Q.Z_TOP), L.FACE_TOP_Z, "M3r2a %+.2f (worst %+.2f)" % (room_nom - (Q.BOND + Q.PLATE_T + Q.Z_TOP),
            room_worst - (Q.BOND + Q.PLATE_T + Q.Z_TOP)), off=4, fs=4.8, color=GREEN)
    K.dim_v(ax, X(20.0), cz(Q.Z_UT), L.FACE_TOP_Z, "M3r2b %+.2f (worst %+.2f) less cap" % (room_nom - (Q.BOND + Q.PLATE_T + Q.Z_UT), room_worst - (Q.BOND + Q.PLATE_T + Q.Z_UT)),
            off=0, fs=4.8, color=RED)
    K.dim_v(ax, kx, cz(Q.Z_UT + Q.KNOB_H), L.FACE_TOP_Z, "M3r2k %+.2f\n(worst %+.2f)" % (room_nom - (Q.BOND + Q.PLATE_T + Q.Z_UT) - Q.KNOB_H,
            room_worst - (Q.BOND + Q.PLATE_T + Q.Z_UT) - Q.KNOB_H), off=0, fs=4.6, color=GREEN)
    K.dim_v(ax, X(-Q.BASE_Y) - 2, CEIL, cz(Q.Z_UT), "%.2f" % (Q.BOND + Q.PLATE_T + Q.Z_UT), off=-3, fs=4.8)
    K.dim_v(ax, X(-Q.BASE_Y) - 2, CEIL, cz(Q.Z_TOP), "%.2f" % (Q.BOND + Q.PLATE_T + Q.Z_TOP), off=-9, fs=4.8)
    K.dim_h(ax, X(-Q.BASE_Y), X(Q.BASE_Y), CEIL, "%.1f" % (2 * Q.BASE_Y), off=6, fs=4.8)
    K.dim_h(ax, X(Q.BASE_Y), ceil_x, CEIL, "M19 %+.2f" % m19["nom"], off=10, fs=4.6, color=GREEN)
    ax.text(60, CEIL + 12, "B. SECTION through the TUNE knob (Y %.1f), X east to the right, lid closed. Dashed: the gussets beside this plane. Room from the\n"
                           "face top to the ceiling %.2f nominal, %.2f at the worst (frame_seat.out M3 + the r1 tray's %.1f); the r2 rows from lid_tray_qmx_r2_check.py." % (
                               ys, room_nom, room_worst, C.R1_TRAY), fontsize=5.4, va="bottom")
    ax.set_xlim(58, 192); ax.set_ylim(L.FACE_TOP_Z - 5, CEIL + 22)
    # ---- C. the end panels from outside, with the tray's section around them
    for k, (panel, title) in enumerate((("L", "LEFT panel (front end, toward case -Y), seen from outside: knob edge on the RIGHT"),
                                        ("R", "RIGHT panel (hinge end, toward case +Y), seen from outside: knob edge on the LEFT"))):
        ax = fig.add_axes([0.44 + 0.275 * k, 0.285, 0.27, 0.30]); ax.set_aspect("equal"); ax.axis("off")
        W, H = Q.UNIT[1], Q.UNIT[2]
        fx = (lambda v: W - v) if panel == "L" else (lambda v: v)          # v from the knob edge -> x on the drawing
        z0 = Q.Z_UB                                                        # draw z above the tray's mounting face (the lid plate), up the page
        rect(ax, -Q.CLR - Q.WALL, -Q.PLATE_T, W + Q.CLR + Q.WALL, 0, fc=PLATEC, ec=BLUE, lw=0.4)
        rect(ax, -Q.CLR - Q.WALL, 0, W + Q.CLR + Q.WALL, Q.FLOOR, fc=TRAY, ec="k", lw=0.4)
        rect(ax, -Q.CLR - Q.WALL, Q.FLOOR, W + Q.CLR + Q.WALL, Q.Z_SILL, fc=("#9fb8e0" if panel == "L" else "#c89b45"), ec="k", lw=0.5, alpha=0.9)
        for x0 in (-Q.CLR - Q.WALL, W + Q.CLR):
            rect(ax, x0, Q.Z_SILL, x0 + Q.WALL, Q.Z_TOP, fc="#c89b45", ec="k", lw=0.5)
        rect(ax, -Q.CLR - Q.WALL, Q.Z_UT, W + Q.CLR + Q.WALL, Q.Z_TOP, fc="#c89b45", ec="k", lw=0.5, alpha=0.8)
        rect(ax, 0, z0, W, z0 + H, fill=False, ec="k", lw=1.0)
        for (sx_, sy_) in ((3.0, 3.0), (60.0, 3.0), (3.0, 22.0), (60.0, 22.0)):
            ax.add_patch(Circle((sx_, z0 + sy_), 1.25, fill=False, lw=0.4, color=GREY))
        for nm, j in Q.JACKS.items():
            if j["panel"] != panel: continue
            r = Q.admitted_radius(nm)
            v0, v1 = min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE; h0, h1 = min(j["h"]) - Q.JACK_RANGE, max(j["h"]) + Q.JACK_RANGE
            xa, xb = sorted((fx(v0), fx(v1)))
            rect(ax, xa, z0 + h0, xb, z0 + h1, fc="#ffcccc", ec=RED, lw=0.5)
            for v in (v0, v1):
                for h in (h0, h1):
                    ax.add_patch(Circle((fx(v), z0 + h), r, fill=False, ec=(RED if "harness" in j["use"] else GREY), lw=0.35, ls=":"))
            ax.text((xa + xb) / 2, z0 + h1 + 0.6, "%s\nd %.1f" % (nm, 2 * r), fontsize=4.4, ha="center", va="bottom")
        K.dim_v(ax, W + Q.CLR + Q.WALL + 1.0, z0, Q.Z_SILL, "sill %.1f" % Q.SILL_H, off=4, fs=4.4)
        K.dim_v(ax, W + Q.CLR + Q.WALL + 1.0, z0, z0 + H, "%.0f" % H, off=9, fs=4.6)
        K.dim_h(ax, 0, W, z0 + H, "%.0f" % W, off=6.5, fs=4.6)
        kv = fx(Q.KNOB_V); ax.plot([kv, kv], [z0 + H, z0 + H + Q.KNOB_H], lw=0.8, color="k"); ax.text(kv, z0 + H + Q.KNOB_H + 0.5, "knob", fontsize=4.2, ha="center", va="bottom")
        ax.text(-Q.CLR - Q.WALL, Q.Z_TOP + 16, "C%d. %s" % (k + 1, title), fontsize=5.2, va="bottom")
        ax.text(W / 2, -Q.PLATE_T - 1.0, "tray open across the panel above the %s (top %.1f above the plate); lintel above the unit" % (
            "keeper" if panel == "L" else "end block", Q.Z_SILL), fontsize=4.2, ha="center", va="top")
        ax.set_xlim(-10, W + 18); ax.set_ylim(-8, Q.Z_TOP + 22)
    # ---- the r2 rows and the tolerances
    rep = C.report().splitlines()
    rows = [l.strip() for l in rep if l.strip().startswith(("M3r2", "M19 (east"))]
    text_block(fig, [0.015, 0.098, 0.505, 0.18], rows + [
        "frame_seat.out's own M3 (%+.2f, worst %+.2f) is the r1 tray's and stays until frame_seat.py reads r2 (a draft); M19 and M20 are unchanged." % (m3["nom"], m3["worst"]),
        "Plugs: the tray admits each body named in A and C1/C2 at the worst of its jack's scaled place (lid_tray_qmx_r2_check.py --solids: no intersection on "
        "the solids, two controls that must intersect do). The admitted bodies are the requirement on the harness picks (RG-316 BNC, USB-C, 2.1 x 5.5 plug) "
        "and on the operator's 3.5 mm plugs; the DC and USB leads must bend at R %.0f or less, the RG-316 at R %.1f." % (C.LEAD_R, C.RG316_R)],
        fs=5.2, title="FACE ROOM AND PLUGS (lid_tray_qmx_r2_check.py, sections A and B); MET in the r2 record, OPEN where its input is TBD")
    K.tolerance_box(fig, None, extra=["Jack places and the knob are SCALED from the maker's undimensioned figures and photographs (v2/vendor/qrp-labs/qmx-figures.out), "
                                      "each taken over its figure-to-photograph spread plus 0.5; the unit's 95 x 63 x 25 and 220 g are the maker's. Printed parts +-0.2 "
                                      "(FFF, INFERRED); the place is marked on the lid by hand from the case centre and the flat ceiling's edge (+-1.0, INFERRED)."])
    fig.savefig(os.path.join(OUT, "lid-tray-qmx-r2-drawing-1.png"), dpi=110); pdf.savefig(fig); plt.close(fig)


# ======================================================================================= page 2: the parts
def page2(pdf):
    fig = sheet("QMX lid tray r2: the tray, the keeper and the lid plate, dimensioned; hardware, print and fitting; retention", "14r2-2 of 2")
    # ---- D. tray plan in its own frame (x to the hinge, y east; seen from the open face, i.e. from the face plate with the lid closed)
    ax = fig.add_axes([0.005, 0.47, 0.46, 0.515]); ax.set_aspect("equal"); ax.axis("off")
    rect(ax, -Q.BASE_X, -Q.BASE_Y, Q.BASE_X, Q.BASE_Y, fc=TRAY, ec="k", lw=0.8)
    for sy in (-1, 1): rect(ax, -Q.FACE_X, sy * Q.SIDE_IN, Q.FACE_X, sy * Q.SIDE_OUT, fc="#c89b45", ec="k", lw=0.6)
    rect(ax, Q.BACK_LEDGE[0], Q.SIDE_IN - Q.LEDGE_BACK, Q.BACK_LEDGE[1], Q.SIDE_IN, fc="none", ec="k", lw=0.5, hatch="////")
    for x0, x1 in Q.FRONT_SEGMENTS: rect(ax, x0, -Q.SIDE_IN, x1, -Q.SIDE_IN + Q.LEDGE_FRONT, fc="none", ec="k", lw=0.5, hatch="////")
    for sx in (-1, 1):
        rect(ax, sx * Q.U0, -Q.SIDE_OUT, sx * (Q.U0 + Q.LINTEL_W), Q.SIDE_OUT, fc="none", ec="k", lw=0.5, hatch="\\\\\\\\")
        a, b = sorted((sx * Q.KNOB_ZONE[0], sx * Q.KNOB_ZONE[1])); rect(ax, a, -Q.SIDE_OUT, b, -Q.SIDE_IN, fc="white", ec=GREEN, lw=0.5, ls="--")
    rect(ax, Q.FACE_X, -Q.BASE_Y, Q.BASE_X, Q.BASE_Y, fc="#c89b45", ec="k", lw=0.6)
    rect(ax, -Q.BASE_X, -Q.SIDE_OUT, -Q.FACE_X, Q.SIDE_OUT, fc="none", ec=BLUE, lw=0.8, ls="--")
    for gx in Q.GUSSET["x"]:
        for sy in (-1, 1): rect(ax, gx - Q.GUSSET["t"] / 2, sy * Q.SIDE_OUT, gx + Q.GUSSET["t"] / 2, sy * (Q.SIDE_OUT + Q.GUSSET["depth"]), fc="#c89b45", ec="k", lw=0.4)
    for px_ in Q.PAD["x"]: rect(ax, px_ - Q.PAD["size"][0] / 2, -Q.PAD["size"][1] / 2, px_ + Q.PAD["size"][0] / 2, Q.PAD["size"][1] / 2, fc="#555555", ec="k", lw=0.4)
    for x, y in Q.SCREWS_BOSS: ax.add_patch(Circle((x, y), 4.0, fc="#c89b45", ec="k", lw=0.5))
    for x, y in Q.PLATE_HOLES:
        ax.add_patch(Circle((x, y), Q.CSK["d_head"] / 2, fill=False, ec=RED, lw=0.5)); ax.add_patch(Circle((x, y), Q.CSK["hole"] / 2, fill=False, ec=RED, lw=0.5))
    ax.text(0, Q.SIDE_IN - Q.LEDGE_BACK - 1.5, "back ledge %.1f over the unit, x %.1f .. %.1f" % (Q.LEDGE_BACK, *Q.BACK_LEDGE), fontsize=4.8, ha="center", va="top")
    ax.text(0, -Q.SIDE_IN + Q.LEDGE_FRONT + 1.5, "knob-edge ledge %.1f in three segments; wall lowered to the unit's top\nin the knob zones |x| %.1f .. %.1f (green dashed)" % (
        Q.LEDGE_FRONT, *Q.KNOB_ZONE), fontsize=4.8, ha="center", va="bottom")
    ax.text(0, 0, "pocket %.1f x %.1f\n(unit %.0f x %.0f, %.1f each side)\nPORON windows %.0f x %.0f at x %+.0f / %+.0f" % (
        2 * Q.FACE_X, 2 * Q.SIDE_IN, Q.UNIT[0], Q.UNIT[1], Q.CLR, Q.PAD["size"][0], Q.PAD["size"][1], *Q.PAD["x"]), fontsize=5.0, ha="center", va="center")
    ax.text((Q.FACE_X + Q.BASE_X) / 2, Q.BASE_Y + 1.0, "END BLOCK (integral):\nsill face x %+.1f, top %.1f" % (Q.FACE_X, Q.Z_SILL), fontsize=4.4, ha="center", va="bottom")
    ax.text(-(Q.FACE_X + Q.BASE_X) / 2, Q.BASE_Y + 1.0, "KEEPER (separate, blue dashed):\nface x %+.1f, on the deck" % -Q.FACE_X, fontsize=4.4, ha="center", va="bottom", color=BLUE)
    K.dim_h(ax, -Q.BASE_X, Q.BASE_X, Q.BASE_Y, "%.1f base (lid plate the same)" % (2 * Q.BASE_X), off=6, fs=5.2)
    K.dim_v(ax, Q.BASE_X, -Q.BASE_Y, Q.BASE_Y, "%.1f" % (2 * Q.BASE_Y), off=6, fs=5.2)
    K.dim_h(ax, -Q.FACE_X, Q.FACE_X, -Q.BASE_Y, "%.1f between sill and keeper faces" % (2 * Q.FACE_X), off=-6, fs=5.0)
    K.dim_v(ax, -Q.BASE_X, -Q.SIDE_IN, Q.SIDE_IN, "%.1f" % (2 * Q.SIDE_IN), off=-6, fs=5.0)
    K.dim_v(ax, -Q.BASE_X, -Q.SIDE_OUT, Q.SIDE_OUT, "%.1f over walls" % (2 * Q.SIDE_OUT), off=-12, fs=5.0)
    ax.text(-Q.BASE_X, Q.BASE_Y + 16, "D. THE TRAY (print, Prusament PC Blend) in its own frame, seen from its open face: x toward the hinge (the unit's RIGHT panel),\n"
                                       "y east (the unit's back edge), z up from the lid plate. Red: the ten countersunk M3 (hatched: ledges and lintels at z %.1f .. %.1f)." % (Q.Z_UT, Q.Z_TOP),
            fontsize=5.4, va="bottom")
    ax.set_xlim(-Q.BASE_X - 16, Q.BASE_X + 14); ax.set_ylim(-Q.BASE_Y - 14, Q.BASE_Y + 26)
    # hole table
    rows = ["  #  x       y       where"] + ["%3d %+6.1f %+6.1f  %s" % (k + 1, x, y, w) for k, (x, y, w) in enumerate(
        [(x, y, "flange boss, tray") for x, y in Q.SCREWS_BOSS] + [(x, y, "end block, tray") for x, y in Q.SCREWS_END_R] + [(x, y, "keeper through deck") for x, y in Q.SCREWS_KEEPER])]
    tx = fig.add_axes([0.005, 0.285, 0.16, 0.18]); tx.axis("off")
    tx.text(0, 1, "HOLES (part frame; the lid plate's tapped M3\nat the same x, y; case X = %.1f + y, Y = %.1f + x)\n" % (Q.PLACE_X, Q.PLACE_Y) + "\n".join(rows), fontsize=5.0, va="top", family="monospace")
    # ---- E. sections of the tray: along the length at y = 0, and across at x = 0
    ax = fig.add_axes([0.47, 0.74, 0.52, 0.245]); ax.set_aspect("equal"); ax.axis("off")
    rect(ax, -Q.BASE_X, -Q.PLATE_T, Q.BASE_X, 0, fc=PLATEC, ec=BLUE, lw=0.4)
    rect(ax, -Q.BASE_X, 0, Q.BASE_X, Q.FLOOR, fc=TRAY, ec="k", lw=0.5)
    for px_ in Q.PAD["x"]:
        rect(ax, px_ - Q.PAD["size"][0] / 2, 0, px_ + Q.PAD["size"][0] / 2, Q.Z_UB, fc="#555555", ec="k", lw=0.3)
    rect(ax, Q.FACE_X, 0, Q.BASE_X, Q.Z_SILL, fc="#c89b45", ec="k", lw=0.5)
    rect(ax, -Q.BASE_X, Q.FLOOR, -Q.FACE_X, Q.Z_SILL, fc="#9fb8e0", ec="k", lw=0.5)
    for sx in (-1, 1):
        a, b = sorted((sx * Q.U0, sx * (Q.U0 + Q.LINTEL_W))); rect(ax, a, Q.Z_UT, b, Q.Z_TOP, fc="#c89b45", ec="k", lw=0.5)
    rect(ax, -Q.U0, Q.Z_UB, Q.U0, Q.Z_UT, fc=UNITC, ec="k", lw=0.6, ls="--", alpha=0.6)
    ax.text(0, (Q.Z_UB + Q.Z_UT) / 2, "unit (dashed): slides in from the keeper end, the keeper then screwed on", fontsize=4.8, ha="center", va="center")
    K.dim_v(ax, Q.BASE_X, 0, Q.Z_SILL, "%.1f" % Q.Z_SILL, off=4, fs=4.6); K.dim_v(ax, Q.BASE_X, 0, Q.Z_TOP, "%.1f" % Q.Z_TOP, off=10, fs=4.6)
    K.dim_v(ax, -Q.BASE_X, 0, Q.FLOOR, "%.1f" % Q.FLOOR, off=-4, fs=4.4); K.dim_v(ax, -Q.BASE_X, 0, Q.Z_UB, "%.1f" % Q.Z_UB, off=-9, fs=4.4)
    K.dim_v(ax, -Q.BASE_X, Q.Z_UT, Q.Z_TOP, "%.1f" % Q.LEDGE_T, off=-4, fs=4.4); K.dim_v(ax, -Q.BASE_X, 0, Q.Z_UT, "%.1f" % Q.Z_UT, off=-14, fs=4.4)
    K.dim_h(ax, Q.U0, Q.U0 + Q.LINTEL_W, Q.Z_TOP, "lintel %.1f" % Q.LINTEL_W, off=3, fs=4.4)
    ax.text(-Q.BASE_X, Q.Z_TOP + 8, "E1. SECTION ALONG THE LENGTH at y 0 (x to the right, z up from the lid plate)", fontsize=5.4, va="bottom")
    ax.set_xlim(-Q.BASE_X - 20, Q.BASE_X + 16); ax.set_ylim(-4, Q.Z_TOP + 14)
    ax = fig.add_axes([0.47, 0.47, 0.25, 0.26]); ax.set_aspect("equal"); ax.axis("off")
    rect(ax, -Q.BASE_Y, -Q.PLATE_T, Q.BASE_Y, 0, fc=PLATEC, ec=BLUE, lw=0.4); rect(ax, -Q.BASE_Y, 0, Q.BASE_Y, Q.FLOOR, fc=TRAY, ec="k", lw=0.5)
    for sy in (-1, 1):
        rect(ax, sy * Q.SIDE_IN, 0, sy * Q.SIDE_OUT, Q.Z_TOP, fc="#c89b45", ec="k", lw=0.5)
        ax.add_patch(Polygon([(sy * Q.SIDE_OUT, Q.FLOOR), (sy * (Q.SIDE_OUT + Q.GUSSET["depth"]), Q.FLOOR), (sy * Q.SIDE_OUT, Q.GUSSET["z_top"])], closed=True, fc="#c89b45", ec="k", lw=0.5))
    rect(ax, Q.SIDE_IN - Q.LEDGE_BACK, Q.Z_UT, Q.SIDE_IN, Q.Z_TOP, fc="#c89b45", ec="k", lw=0.5)
    rect(ax, -Q.SIDE_IN, Q.Z_UT, -Q.SIDE_IN + Q.LEDGE_FRONT, Q.Z_TOP, fc="#c89b45", ec="k", lw=0.5)
    rect(ax, -Q.UNIT[1] / 2, Q.Z_UB, Q.UNIT[1] / 2, Q.Z_UT, fc=UNITC, ec="k", lw=0.6, ls="--", alpha=0.6)
    K.dim_h(ax, Q.SIDE_IN - Q.LEDGE_BACK, Q.SIDE_IN, Q.Z_TOP, "%.1f" % Q.LEDGE_BACK, off=2.5, fs=4.4)
    K.dim_h(ax, -Q.SIDE_IN, -Q.SIDE_IN + Q.LEDGE_FRONT, Q.Z_TOP, "%.1f" % Q.LEDGE_FRONT, off=2.5, fs=4.4)
    K.dim_h(ax, Q.SIDE_IN, Q.SIDE_OUT, 0, "%.1f" % Q.WALL, off=-4, fs=4.4); K.dim_h(ax, Q.SIDE_OUT, Q.BASE_Y, 0, "%.1f" % Q.GUSSET["depth"], off=-4, fs=4.4)
    K.dim_v(ax, Q.BASE_Y, Q.FLOOR, Q.GUSSET["z_top"], "gusset to %.1f" % Q.GUSSET["z_top"], off=4, fs=4.2)
    ax.text(-Q.BASE_Y, Q.Z_TOP + 7, "E2. SECTION ACROSS at x 0 (y to the right)\nknob edge left; gussets %.1f thick at x %s" % (
        Q.GUSSET["t"], ", ".join("%+.0f" % g for g in Q.GUSSET["x"])), fontsize=5.0, va="bottom")
    ax.set_xlim(-Q.BASE_Y - 4, Q.BASE_Y + 10); ax.set_ylim(-9, Q.Z_TOP + 16)
    # ---- F. keeper and lid plate
    ax = fig.add_axes([0.73, 0.47, 0.26, 0.26]); ax.set_aspect("equal"); ax.axis("off")
    rect(ax, -Q.BASE_X, -Q.BASE_Y, Q.BASE_X, Q.BASE_Y, fc=PLATEC, ec=BLUE, lw=0.7)
    for x, y in Q.PLATE_HOLES: ax.add_patch(Circle((x, y), Q.TAP / 2, fill=False, ec=RED, lw=0.6))
    K.dim_h(ax, -Q.BASE_X, Q.BASE_X, Q.BASE_Y, "%.1f" % (2 * Q.BASE_X), off=5, fs=4.6); K.dim_v(ax, Q.BASE_X, -Q.BASE_Y, Q.BASE_Y, "%.1f" % (2 * Q.BASE_Y), off=5, fs=4.6)
    ax.text(0, 0, "LID PLATE: 5052-H32, %.1f, R6 corners,\n10 x M3 tapped through (drill %.1f),\nholes as the table left; DXF and STEP\nin lid-tray-qmx-r2/. Bond face to the lid:\nDP8005 over the whole face" % (Q.PLATE_T, Q.TAP),
            fontsize=4.6, ha="center", va="center")
    ax.text(-Q.BASE_X, -Q.BASE_Y - 6, "KEEPER: %.1f x %.1f x %.1f PC Blend, three countersunk M3 at x %+.1f, y -24 / 0 / +24;\nits face bears on the left panel's bottom %.1f" % (
        Q.END_L, 2 * Q.SIDE_OUT, Q.Z_SILL - Q.FLOOR, -(Q.FACE_X + Q.END_L / 2), Q.SILL_H), fontsize=4.6, va="top", color=BLUE)
    ax.text(-Q.BASE_X, Q.BASE_Y + 12, "F. LID PLATE (plan, the tray's frame) and KEEPER", fontsize=5.4, va="bottom")
    ax.set_xlim(-Q.BASE_X - 3, Q.BASE_X + 12); ax.set_ylim(-Q.BASE_Y - 22, Q.BASE_Y + 20)
    # ---- G. notes, and the retention table from the check
    rep = C.report().splitlines()
    ret = [l.rstrip() for l in rep[rep.index([l for l in rep if l.startswith("D. RETENTION")][0]):]]
    notes = [
        "1. PARTS: tray and keeper printed in Prusament PC Blend (TDS v1.1: HDT 113 C at 0.45 MPa, interlayer 21 +-2 MPa), floor down, 100 percent infill, "
        "0.20 mm layers (the sheet's specimen settings, which the retention figures assume); the knob-edge and back ledges print as 3.0 and 4.0 overhangs. Lid plate "
        "5052-H32 2.0 from the DXF. Two pads, Rogers PORON 4701-30 Very Soft 320 kg/m3, 3.18 thick, 24 x 20, in the floor windows on the plate. Ten M3 x 5 "
        "countersunk hex socket (ISO 10642 class) A2, each head flush and its tip 0.6 short of the plate's back face. 3M DP8005 for the plate.",
        "2. FITTING: bond the plate to the lid's unribbed inner face at the place of sheet 14r2-1 with DP8005 (clean, dry; the sheet asks no primer on PP; "
        "fixture 2 h); screw the tray on (four boss and three end-block screws); fit the pads; do NOT fit the unit's four self-adhesive feet (the maker calls "
        "them optional); with the lid open, slide the unit in from the keeper end, right panel first, under both ledges and the end lintel; screw the keeper on; "
        "plug the DC, RF and USB leads and tie each within 60 mm of its plug to a tie mount bonded to the lid, so no lead pulls on a jack.",
        "3. OPERATION: the LCD, both knobs and both buttons face the operator with the lid open (the text then reads down the lid); the Paddle, Audio and PTT "
        "plugs are the operator's and come out before the lid closes.",
        "4. OPEN, carried with this sheet (not closed by it): the face crossing of the lid harness (not designed anywhere); the lid plate's bond strength on "
        "the case's polypropylene (T8 pull test); the peak E1 puts on the lid (E1 with an accelerometer on the lid); the knob height (T9 with chalk on the knob "
        "tips; MET for any knob up to the height in the r2 record); the button cap heights (M3, T9); the harness picks against the admitted plug bodies and R %.0f." % C.LEAD_R,
    ]
    text_block(fig, [0.17, 0.285, 0.82, 0.18], notes, fs=5.0, title="NOTES")
    text_block(fig, [0.015, 0.098, 0.975, 0.18], ret, fs=4.3, title=None, mono=True)
    fig.savefig(os.path.join(OUT, "lid-tray-qmx-r2-drawing-2.png"), dpi=110); pdf.savefig(fig); plt.close(fig)


if __name__ == "__main__":
    with PdfPages(os.path.join(OUT, "lid-tray-qmx-r2-drawing.pdf")) as pdf:
        page1(pdf); page2(pdf)
    print("wrote lid-tray-qmx-r2-drawing.pdf (2 pages) and the page PNGs")
    print("LID-TRAY-QMX-R2-DRAWING-DONE")
