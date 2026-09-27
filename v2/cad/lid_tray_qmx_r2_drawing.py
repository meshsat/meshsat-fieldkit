#!/usr/bin/env python3
"""Sheets 14r2-1, 14r2-2 and 14r2-3 of the case set: the QMX lid tray r2 placed on the lid, its three made parts dimensioned, and its
fitting, notes and record (MESHSAT-1357, S-63 and EQ-24; stream w5tray, second pass of 27 to 28 Sep 2026). They supersede sheet 14
(lid-tray-qmx-drawing.pdf) of v2/release/case-2026-09-27/. Every solid drawn is a row of lid_tray_qmx_r2.elements(), the one table the
parts are built from and the check reads; every number is read from v2/cad/lid_tray_qmx_r2.py, v2/ecad/tools/panel1450.py and
v2/vendor/peli/1450/frame_seat.out, and the face-room, retention and fitting rows from v2/cad/lid_tray_qmx_r2_check.py; nothing is typed
here but the drawing's own layout. Lettering: notes 6.3 pt, tables 5.4 pt monospace, labels in the views 5.0 pt or more.
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
RED, GREY, BLUE, GREEN = "#b00020", "#777777", "#1f4e9a", "#1b5e20"
COL = dict(tray="#f3d9a4", wall="#c89b45", frame="#9fb8e0", plate="#b8c7d9", pad="#555555", unit="#d0d0d0", proud="#ffffff", screw="#404040")
INPUTS = ["v2/cad/lid_tray_qmx_r2.py", "v2/cad/lid_tray_qmx_r2_check.py", "v2/ecad/tools/panel1450.py", "v2/vendor/peli/1450/frame_seat.out",
          "v2/vendor/qrp-labs/qmx-figures.out", "v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf"]
CEIL = L.PELI["rim_z"] + L.PELI["lid_z"]                        # the lid's inner ceiling, 154.44 (Peli STEP)
ZP = CEIL - Q.BOND - Q.PLATE_T                                  # the tray's mounting face in the case frame
E = Q.elements()
PLUGS, REACH = C.plug_envelopes()
REPORT, REPORT_OK = C.report()
FS, FS_NOTE, FS_TAB = 5.2, 6.3, 5.4
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
    tb.text(0.005, 0.04, "MESHSAT-1357, S-63, EQ-24. PROTOTYPE DESIGN: nothing made, printed, bought or fitted.\nSession choices under the owner's standing rule of 26 Sep 2026. AI review only.", fontsize=5.6, va="bottom")
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


def colour(e):
    if e["part"] == "tray": return COL["wall"] if e["box"][5] > Q.Z_SILL + 1e-9 else COL["tray"]
    return COL[e["part"]]


def plan(ax, els, case=False, **kw):
    """Elements in plan, the lowest first; in the case frame (X east, Y to the hinge) or the part's own."""
    for e in sorted(els, key=lambda e: (e["box"][5], e["name"])):
        x0, x1, y0, y1 = e["box"][:4]
        k = dict(fc=colour(e), ec="k", lw=0.5); k.update(kw)
        if e["shape"] == "cyl_z":
            c = cxy((x0 + x1) / 2, (y0 + y1) / 2) if case else ((x0 + x1) / 2, (y0 + y1) / 2)
            ax.add_patch(Circle(c, (x1 - x0) / 2, **k))
        elif case:
            a, b = cxy(x0, y0), cxy(x1, y1); rect(ax, a[0], a[1], b[0], b[1], **k)
        else:
            rect(ax, x0, y0, x1, y1, **k)


def cut(ax, els, axis, at, h=lambda v: v, z=lambda v: v, beside=(), **kw):
    """Elements cut by the plane `axis` = at, drawn across the other axis (through h) and z (through z); `beside` dashed."""
    i = 0 if axis == "x" else 2; j = 2 if axis == "x" else 0
    for e in sorted(els, key=lambda e: (e["box"][5], e["name"])):
        b = e["box"]
        if not (b[i] - 1e-9 <= at <= b[i + 1] + 1e-9): continue
        k = dict(fc=colour(e), ec="k", lw=0.5); k.update(kw)
        rect(ax, h(b[j]), z(b[4]), h(b[j + 1]), z(b[5]), **k)
    for e in beside:
        b = e["box"]; rect(ax, h(b[j]), z(b[4]), h(b[j + 1]), z(b[5]), fill=False, ec="k", lw=0.4, ls="--")


def text_block(fig, r, lines, fs=FS_NOTE, width=None, title=None, mono=False):
    ax = fig.add_axes(r); ax.axis("off")
    width = width or int(r[2] * 16.54 * 72 / (fs * 0.56))
    out = ([title] if title else []) + (list(lines) if mono else sum((textwrap.wrap(s, width, subsequent_indent="   ") for s in lines), []))
    ax.text(0, 1, "\n".join(out), fontsize=fs, va="top", linespacing=1.15, family=("monospace" if mono else "sans-serif"), fontweight="normal")
    return ax


def section_of(report, head):
    """The lines of one section of the record, from its heading to the blank line after it."""
    ls = report.splitlines(); k = [n for n, l in enumerate(ls) if l.startswith(head)][0]
    out = []
    for l in ls[k:]:
        if not l.strip(): break
        out.append(l.rstrip())
    return out


# ======================================================================================= sheet 1: the place, the section, the end panels
def page1(pdf):
    fig = sheet("QMX lid tray r2: its place on the lid, the section with the lid closed, both end panels and their plugs", "14r2-1 of 3")
    R = K.rows(); m19 = R["M19"]
    room_nom, room_worst, room_wc2 = C.room()
    rows = {r["ref"]: r for r in C.face_rows(E + PLUGS)}
    # ---- A. plan on the lid (case frame, seen from above through the lid, lid closed)
    ax = fig.add_axes([0.005, 0.285, 0.43, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    px, py = L.PLATE[0] / 2, L.PLATE[1] / 2
    ax.plot([40, px - L.PLATE_R], [py, py], lw=0.6, color=GREY); ax.plot([40, px - L.PLATE_R], [-py, -py], lw=0.6, color=GREY)
    ax.add_patch(Arc((px - L.PLATE_R, py - L.PLATE_R), 2 * L.PLATE_R, 2 * L.PLATE_R, theta1=0, theta2=90, lw=0.6, color=GREY))
    ax.add_patch(Arc((px - L.PLATE_R, -py + L.PLATE_R), 2 * L.PLATE_R, 2 * L.PLATE_R, theta1=270, theta2=360, lw=0.6, color=GREY))
    ax.plot([px, px], [-py + L.PLATE_R, py - L.PLATE_R], lw=0.6, color=GREY)
    ax.text(px + 1.5, -40, "face plate edge (C1)", fontsize=FS, ha="left", va="center", color=GREY, rotation=90)
    ceil_x = Q.EAST_EDGE_X + m19["nom"]; ceil_y = C.LID_FLAT_HALF_Y
    ax.plot([ceil_x, ceil_x], [-ceil_y, ceil_y], lw=0.8, color=BLUE, ls="--"); ax.plot([40, ceil_x], [ceil_y, ceil_y], lw=0.8, color=BLUE, ls="--")
    ax.plot([40, ceil_x], [-ceil_y, -ceil_y], lw=0.8, color=BLUE, ls="--")
    ax.text(ceil_x + 1.0, ceil_y - 3, "lid's flat\nceiling ends\nX %.2f,\nY +-%.2f" % (ceil_x, ceil_y), fontsize=FS, color=BLUE, va="top")
    plan(ax, Q.parts(E, "plate"), case=True, ec=BLUE, lw=0.6)
    plan(ax, Q.parts(E, "tray"), case=True, lw=0.4)
    plan(ax, Q.parts(E, "unit"), case=True, lw=0.8, alpha=0.8)
    plan(ax, Q.parts(E, "frame"), case=True, lw=0.5, alpha=0.75)
    for e in Q.parts(E, "proud"):
        if e["shape"] == "cyl_z": plan(ax, [e], case=True, lw=0.7)
    for sx in (-1, 1):
        kc = cxy(sx * Q.KNOB_X, Q.KNOB_Y)
        ax.add_patch(Circle(kc, Q.KNOB_D / 2 + Q.FINGER, fill=False, ec=GREEN, lw=0.4, ls=":"))
        ax.text(kc[0], kc[1], "VOL" if sx < 0 else "TUNE", fontsize=FS, ha="center", va="center")
    l0 = cxy(-Q.U0 + Q.LCD[0], Q.UNIT[1] / 2 - Q.LCD[3]); l1 = cxy(-Q.U0 + Q.LCD[1], Q.UNIT[1] / 2 - Q.LCD[2])
    rect(ax, l0[0], l0[1], l1[0], l1[1], fill=False, ec="k", lw=0.5, ls="--")
    ax.text((l0[0] + l1[0]) / 2, (l0[1] + l1[1]) / 2, "QMX LCD window", fontsize=FS, ha="center", va="center", rotation=90)
    for x, y in Q.PLATE_HOLES:
        c = cxy(x, y); ax.plot([c[0] - 2.5, c[0] + 2.5], [c[1], c[1]], lw=0.4, color=RED); ax.plot([c[0], c[0]], [c[1] - 2.5, c[1] + 2.5], lw=0.4, color=RED)
    for x, y in Q.FRAME_SCREWS:
        c = cxy(x, y); ax.add_patch(Circle(c, Q.BH["d_head"] / 2, fc=COL["screw"], ec="k", lw=0.4))
    # the face plate's parts under the set (grey, dashed), each with its height above the face
    for ref, foot, height, key in C.face_parts():
        if ref not in rows or ref == "XENARC_WINDOW": continue
        rect(ax, foot[0], foot[2], foot[1], foot[3], fill=False, ec=GREY, lw=0.5, ls="--")
        if not ref.startswith("D") or ref in ("D1", "D11"):
            ax.text(foot[1] + 0.8, (foot[2] + foot[3]) / 2, "%s %.1f" % (ref.replace("SW_", ""), height), fontsize=FS, ha="left", va="center", color="k", zorder=9,
                    bbox=dict(fc="white", ec="none", pad=0.2, alpha=0.8))
    xw = L.XENARC["c"][0] + L.XENARC["window"][0] / 2
    ax.plot([xw, xw], [L.XENARC["c"][1] - L.XENARC["window"][1] / 2, L.XENARC["c"][1] + L.XENARC["window"][1] / 2 - L.XENARC["window_r"]], lw=0.5, color=GREY, ls="-.")
    ax.text(xw - 1.5, -60, "monitor window's east edge X %.2f (glass level with the face, %.1f proud at most)" % (xw, L.PROUD_LIMIT), fontsize=FS, ha="right", va="center", color=GREY, rotation=90)
    # plugs: each jack's admitted envelope as a band from the panel face outward, and the lead lanes
    for nm, j in Q.JACKS.items():
        sx = 1 if j["panel"] == "R" else -1; r = Q.admitted_radius(nm)
        v0, v1 = min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE
        a = cxy(sx * Q.U0, -Q.UNIT[1] / 2 + v0 - r); b = cxy(sx * (Q.U0 + 38.0), -Q.UNIT[1] / 2 + v1 + r)
        perm = "harness" in j["use"]
        rect(ax, a[0], a[1], b[0], b[1], fc=("#ffe0e0" if perm else "#eeeeee"), ec=(RED if perm else GREY), lw=0.4, alpha=0.6)
        mid = cxy(sx * (Q.U0 + 24.0), -Q.UNIT[1] / 2 + (v0 + v1) / 2)
        ax.text(mid[0], mid[1], "%s d %.1f" % (nm, 2 * r), fontsize=FS, ha="center", va="center", rotation=90)
    ye = Q.PLACE_Y + Q.U0
    def lane(x, y0, turn_r):
        yb = ceil_y - C.MARGIN - turn_r
        ax.plot([x, x], [y0, yb], lw=1.1, color=RED)
        ax.add_patch(Arc((x - turn_r, yb), 2 * turn_r, 2 * turn_r, theta1=0, theta2=90, lw=1.1, color=RED))
        ax.plot([x - turn_r, 45], [yb + turn_r, yb + turn_r], lw=1.1, color=RED, ls=(0, (4, 2)))
    xrf = Q.PLACE_X - Q.UNIT[1] / 2 + sum(Q.JACKS["RF"]["v"]) / 2; xusb = Q.PLACE_X - Q.UNIT[1] / 2 + Q.JACKS["USB"]["v"][0]
    lane(xrf, ye + 30, C.RG316_R); lane(xusb, ye + 30, C.LEAD_R)
    xdc = Q.PLACE_X - Q.UNIT[1] / 2 + Q.JACKS["DC"]["v"][0]; yl = Q.PLACE_Y - Q.U0 - 40.0; ybl = -ceil_y + C.MARGIN + C.LEAD_R
    ax.plot([xdc, xdc], [yl + 25, ybl], lw=1.1, color=RED)
    ax.add_patch(Arc((xdc - C.LEAD_R, ybl), 2 * C.LEAD_R, 2 * C.LEAD_R, theta1=180, theta2=360, lw=1.1, color=RED))
    ax.plot([xdc - 2 * C.LEAD_R, xdc - 2 * C.LEAD_R], [ybl, ceil_y - C.MARGIN - C.LEAD_R], lw=1.1, color=RED, ls=(0, (4, 2)))
    ax.text(xrf - 3, ye + 40, "RF: RG-316, R %.1f" % C.RG316_R, fontsize=FS, color=RED, rotation=90, ha="right", va="bottom")
    ax.text(xusb + 2, ye + 40, "USB-C, R %.0f" % C.LEAD_R, fontsize=FS, color=RED, rotation=90, va="bottom")
    ax.text(xdc - 2 * C.LEAD_R - 2, -40, "DC lead loops back, R %.0f" % C.LEAD_R, fontsize=FS, color=RED, rotation=90, ha="right", va="center")
    ax.text(42, ceil_y + 1.5, "lid harness along the hinge side to its crossing of the sealed face: NOT DESIGNED (open item, sheet 14r2-3)", fontsize=FS, color=RED, va="bottom")
    K.dim_h(ax, Q.SPAN_X[0], Q.SPAN_X[1], Q.SPAN_Y[1], "X %.1f .. %.1f (%.1f)" % (Q.SPAN_X[0], Q.SPAN_X[1], 2 * Q.BASE_Y), off=6, fs=5.6)
    K.dim_v(ax, Q.SPAN_X[1], Q.SPAN_Y[0], Q.SPAN_Y[1], "Y %.1f .. %.1f (%.1f)" % (Q.SPAN_Y[0], Q.SPAN_Y[1], 2 * Q.BASE_X), off=9, fs=5.6)
    K.dim_h(ax, Q.EAST_EDGE_X, ceil_x, -ceil_y + 16, "M19 %+.2f" % m19["nom"], off=0, fs=FS, color=GREEN)
    ux0 = Q.PLACE_X - Q.UNIT[1] / 2
    K.dim_h(ax, ux0, ux0 + Q.UNIT[1], Q.PLACE_Y - Q.U0, "unit %.0f, knob edge west at X %.1f" % (Q.UNIT[1], ux0), off=-16, fs=FS)
    K.dim_v(ax, ux0, Q.PLACE_Y - Q.U0, Q.PLACE_Y + Q.U0, "unit %.0f: Y %.1f .. %.1f" % (Q.UNIT[0], Q.PLACE_Y - Q.U0, Q.PLACE_Y + Q.U0), off=-30, fs=FS)
    ax.text(40, ceil_y + 12, "A. PLACE ON THE LID, in plan: case frame (X east, +Y to the hinge wall), lid closed, seen from above through the lid.\n"
                             "Blue outline: the lid plate (bonded); tan: the tray, brown its walls and posts; light blue: the retaining frame with its six\n"
                             "screw heads; grey: the unit (right panel, RF PTT USB, toward the hinge; knob edge west); red crosses: the ten M3 in the plate;\n"
                             "red bands: the plugs of the permanent leads, grey bands: the operator's (unplugged before the lid closes); grey dashed: the\n"
                             "face plate's parts under the set, each with its height above the face.", fontsize=5.6, va="bottom")
    ax.set_xlim(38, 196); ax.set_ylim(-ceil_y - 6, ceil_y + 36)
    # ---- B. section at the TUNE knob (part x = KNOB_X), lid closed: X east to the right, Z up
    ax = fig.add_axes([0.44, 0.60, 0.55, 0.385]); ax.set_aspect("equal"); ax.axis("off")
    X = lambda y: Q.PLACE_X + y
    ax.plot([60, px], [L.FACE_TOP_Z] * 2, lw=0.9, color="k"); ax.plot([60, px], [L.FACE_TOP_Z - L.PLATE[2]] * 2, lw=0.5, color="k")
    ax.text(62, L.FACE_TOP_Z - 0.5, "face top Z %.2f nominal" % L.FACE_TOP_Z, fontsize=FS, va="top")
    ax.plot([60, ceil_x], [CEIL, CEIL], lw=1.0, color=BLUE); ax.plot([ceil_x, ceil_x + 8], [CEIL, CEIL - 6], lw=0.6, color=BLUE, ls="--")
    ax.text(62, CEIL + 0.8, "lid's inner ceiling Z %.2f (Peli STEP); bond %.2f and lid plate %.1f under it" % (CEIL, Q.BOND, Q.PLATE_T), fontsize=FS, va="bottom", color=BLUE)
    posts = [e for e in E if "post" in e["name"] or "screw head" in e["name"]]
    cut(ax, [e for e in E if e["part"] != "proud" or e["name"] == "TUNE knob"], "x", Q.KNOB_X, h=X, z=cz, beside=posts)
    ax.text(X(8), cz((Q.Z_UB + Q.Z_UT) / 2), "QMX %.0f x %.0f x %.0f (maker), 220 g\ntop face (LCD, knobs) toward the face" % Q.UNIT, fontsize=FS, ha="center", va="center")
    kx = X(Q.KNOB_Y)
    ax.text(kx, cz(Q.Z_UT + Q.KNOB_H / 2), "TUNE\nknob\n%.1f" % Q.KNOB_H, fontsize=FS, ha="center", va="center")
    for ref in ("SW_PI",):
        r = rows[ref]; f = r["foot"]
        rect(ax, f[0], L.FACE_TOP_Z, f[1], L.FACE_TOP_Z + r["height"], fc="#ffcccc", ec=RED, lw=0.5)
        ax.text((f[0] + f[1]) / 2, L.FACE_TOP_Z + r["height"] + 0.4, "buttons at X 150 (other Y): heads to %.1f and %.1f" % (rows["SW_MAIN"]["height"], r["height"]), fontsize=FS, ha="center", va="bottom", color=RED)
        K.dim_v(ax, X(Q.SIDE_IN - 1.5), cz(Q.Z_TOP), L.FACE_TOP_Z + r["height"], "M3r2.%s %+.2f (worst %+.2f)" % (ref, r["nom"], r["worst"]), off=0, fs=FS, color=GREEN)
    rw = rows["XENARC_WINDOW"]; rf = rows["FACE"]
    rect(ax, 60, L.FACE_TOP_Z, xw, L.FACE_TOP_Z + rw["height"], fc="#ffcccc", ec=RED, lw=0.4, alpha=0.6)
    ax.text(62, L.FACE_TOP_Z + rw["height"] + 0.4, "monitor: %.1f proud at most" % rw["height"], fontsize=FS, va="bottom", color=RED)
    K.dim_v(ax, kx + 4, cz(Q.Z_UT + Q.KNOB_H), L.FACE_TOP_Z, "M3r2.FACE %+.2f (worst %+.2f, twice %+.2f): OPEN" % (rf["nom"], rf["worst"], rf["wc2"]), off=0, fs=FS, color=RED)
    K.dim_v(ax, kx - 7.5, cz(Q.Z_UT + Q.KNOB_H), L.FACE_TOP_Z + rw["height"], "over the monitor %+.2f (worst %+.2f, twice %+.2f): OPEN" % (rw["nom"], rw["worst"], rw["wc2"]), off=0, fs=FS, color=RED)
    K.dim_v(ax, X(-Q.BASE_Y) - 2, CEIL, cz(Q.Z_UT), "%.2f" % (Q.BOND + Q.PLATE_T + Q.Z_UT), off=-3, fs=FS)
    K.dim_v(ax, X(-Q.BASE_Y) - 2, CEIL, cz(Q.Z_TOP), "%.2f" % (Q.BOND + Q.PLATE_T + Q.Z_TOP), off=-9, fs=FS)
    K.dim_v(ax, X(-Q.BASE_Y) - 2, CEIL, cz(Q.Z_UT + Q.KNOB_H), "%.2f" % (Q.BOND + Q.PLATE_T + Q.Z_UT + Q.KNOB_H), off=-15, fs=FS)
    K.dim_h(ax, X(-Q.BASE_Y), X(Q.BASE_Y), CEIL, "%.1f" % (2 * Q.BASE_Y), off=6, fs=FS)
    K.dim_h(ax, X(Q.BASE_Y), ceil_x, CEIL, "M19 %+.2f" % m19["nom"], off=10, fs=FS, color=GREEN)
    ax.text(60, CEIL + 13, "B. SECTION through the TUNE knob (Y %.1f), X east to the right, lid closed. Dashed: the posts and screw heads beside this plane.\n"
                           "Room from the face top to the ceiling %.2f nominal, %.2f at the worst, %.2f with every unstated allowance twice (frame_seat.out M3);\n"
                           "each row is taken from the deepest solid over the part, with the set's own allowances in it (the record, section B; sheet 14r2-3)." % (
                               Q.PLACE_Y + Q.KNOB_X, room_nom, room_worst, room_wc2), fontsize=5.6, va="bottom")
    ax.set_xlim(58, 192); ax.set_ylim(L.FACE_TOP_Z - 5, CEIL + 24)
    # ---- C. the end panels from outside, with the set's section around them
    n0, n1 = Q.rf_notch()
    for k, (panel, title) in enumerate((("L", "LEFT panel (front end, toward case -Y), seen from outside: knob edge on the RIGHT"),
                                        ("R", "RIGHT panel (hinge end, toward case +Y), seen from outside: knob edge on the LEFT"))):
        ax = fig.add_axes([0.44 + 0.275 * k, 0.285, 0.27, 0.30]); ax.set_aspect("equal"); ax.axis("off")
        W, H = Q.UNIT[1], Q.UNIT[2]
        fx = (lambda y: Q.UNIT[1] / 2 - y) if panel == "L" else (lambda y: y + Q.UNIT[1] / 2)     # part y -> x on the drawing, the knob edge at v = 0
        sx = -1 if panel == "L" else 1
        z0 = Q.Z_UB
        cut(ax, Q.parts(E, "plate", "frame"), "x", sx * (Q.U0 + 1.0), h=fx)
        cut(ax, [e for e in Q.parts(E, "tray") if "boss" not in e["name"]], "x", sx * (Q.FACE_X + 1.0), h=fx)
        for e in Q.parts(E, "tray"):
            if e["box"][5] > Q.Z_SILL + 1e-9 and "wall" in e["name"]:
                b = e["box"]; rect(ax, fx(b[2]), Q.Z_SILL, fx(b[3]), b[5], fill=False, ec="k", lw=0.4, ls="--")
        rect(ax, 0, z0, W, z0 + H, fill=False, ec="k", lw=1.0)
        for (sx_, sy_) in ((3.0, 3.0), (60.0, 3.0), (3.0, 22.0), (60.0, 22.0)):
            ax.add_patch(Circle((sx_, z0 + sy_), 1.25, fill=False, lw=0.4, color=GREY))
        fv = (lambda v: W - v) if panel == "L" else (lambda v: v)
        for nm, j in Q.JACKS.items():
            if j["panel"] != panel: continue
            r = Q.admitted_radius(nm)
            v0, v1 = min(j["v"]) - Q.JACK_RANGE, max(j["v"]) + Q.JACK_RANGE; h0, h1 = min(j["h"]) - Q.JACK_RANGE, max(j["h"]) + Q.JACK_RANGE
            xa, xb = sorted((fv(v0), fv(v1)))
            rect(ax, xa, z0 + h0, xb, z0 + h1, fc="#ffcccc", ec=RED, lw=0.5)
            for v in (v0, v1):
                for h in (h0, h1):
                    ax.add_patch(Circle((fv(v), z0 + h), r, fill=False, ec=(RED if "harness" in j["use"] else GREY), lw=0.35, ls=":"))
            ax.text((xa + xb) / 2, z0 + h1 + 0.6, "%s\nd %.1f" % (nm, 2 * r), fontsize=FS, ha="center", va="bottom")
        K.dim_v(ax, W + Q.CLR + Q.WALL + Q.POST["depth"] + 1.0, z0, Q.Z_SILL, "sill %.1f" % Q.SILL_H, off=4, fs=FS)
        K.dim_v(ax, W + Q.CLR + Q.WALL + Q.POST["depth"] + 1.0, z0, z0 + H, "%.0f" % H, off=10, fs=FS)
        K.dim_h(ax, 0, W, Q.Z_TOP, "%.0f" % W, off=5.0, fs=FS)
        kv = fv(Q.KNOB_V); rect(ax, kv - Q.KNOB_D / 2, z0 + H, kv + Q.KNOB_D / 2, z0 + H + Q.KNOB_H, fc="white", ec="k", lw=0.6)
        ax.text(kv, z0 + H + Q.KNOB_H + 0.5, "knob", fontsize=FS, ha="center", va="bottom")
        ax.text(-Q.CLR - Q.WALL - Q.POST["depth"], Q.Z_TOP + 22, "C%d. %s" % (k + 1, title), fontsize=5.6, va="bottom")
        ax.text(W / 2, -Q.PLATE_T - 1.0, ("open across the panel above the sill (top %.1f above the plate)%s;\nthe frame's end bar above the unit; walls dashed, behind" % (
            Q.Z_SILL, "" if panel == "L" else ", the sill cut to the floor under RF")), fontsize=FS, ha="center", va="top")
        ax.set_xlim(-16, W + 28); ax.set_ylim(-10, Q.Z_TOP + 28)
    # ---- the rows that decide, and the tolerances
    keep = [l.rstrip() for l in section_of(REPORT, "B. FACE ROOM") if l.strip().startswith(("row and part", "M3r2.XENARC", "M3r2.XFRAME_2", "M3r2.SW_", "M3r2.D1 ", "M3r2.D10", "M3r2.FACE", "M19 (east"))]
    text_block(fig, [0.015, 0.098, 0.97, 0.18], [l[3:] for l in keep] + [
        "every row of section B (the %d face parts under the set) is on sheet 14r2-3; frame_seat.out's own M3 (%+.2f, worst %+.2f) is the r1 tray's and stays until frame_seat.py reads r2 (a draft)" % (
            len(rows) - 1, R["M3"]["nom"], R["M3"]["worst"])], fs=FS_TAB, mono=True,
        title="FACE ROOM, the rows that decide (lid_tray_qmx_r2_check.py, section B): nominal, worst, worst with unstated allowances twice")
    fig.savefig(os.path.join(OUT, "lid-tray-qmx-r2-drawing-1.png"), dpi=110); pdf.savefig(fig); plt.close(fig)


# ======================================================================================= sheet 2: the parts
def page2(pdf):
    fig = sheet("QMX lid tray r2: the tray, the retaining frame and the lid plate, dimensioned", "14r2-2 of 3")
    n0, n1 = Q.rf_notch()
    # ---- D. tray plan in its own frame (x to the hinge, y east; seen from the open face, i.e. from the face plate with the lid closed)
    ax = fig.add_axes([0.005, 0.40, 0.49, 0.585]); ax.set_aspect("equal"); ax.axis("off")
    plan(ax, Q.parts(E, "tray"), lw=0.6)
    plan(ax, Q.parts(E, "pad"), lw=0.4)
    for x, y in Q.PLATE_HOLES:
        ax.add_patch(Circle((x, y), Q.CSK["d_head"] / 2, fill=False, ec=RED, lw=0.5)); ax.add_patch(Circle((x, y), Q.CSK["hole"] / 2, fill=False, ec=RED, lw=0.5))
    for x, y in Q.FRAME_SCREWS:
        sy = 1 if y > 0 else -1
        ax.add_patch(Circle((x, y), Q.BH["hole"] / 2, fill=False, ec=BLUE, lw=0.6))
        rect(ax, x - Q.NUT["slot_w"] / 2, sy * (Q.POST_Y - Q.NUT["slot_w"] / 2), x + Q.NUT["slot_w"] / 2, sy * Q.BASE_Y, fill=False, ec=BLUE, lw=0.5, ls="--")
    rect(ax, -Q.U0, -Q.UNIT[1] / 2, Q.U0, Q.UNIT[1] / 2, fill=False, ec="k", lw=0.5, ls=":")
    ax.text(0, 17, "pocket %.1f between the sills x %.1f between the walls\n(unit %.0f x %.0f, dotted: %.1f each side)" % (2 * Q.FACE_X, 2 * Q.SIDE_IN, Q.UNIT[0], Q.UNIT[1], Q.CLR), fontsize=5.6, ha="center", va="center")
    ax.text(0, -17, "PORON windows %.0f x %.0f through the floor at x %+.0f and %+.0f" % (Q.PAD["size"][0], Q.PAD["size"][1], *Q.PAD["x"]), fontsize=5.6, ha="center", va="center")
    ax.text(Q.FACE_X + Q.END_L / 2, (n0 + n1) / 2, "sill cut to the\nfloor under RF\ny %.1f .. %.1f" % (n0, n1), fontsize=FS, ha="center", va="center", rotation=90)
    ax.text(-(Q.FACE_X + Q.END_L / 2), 18, "sill, top %.1f" % Q.Z_SILL, fontsize=FS, ha="center", va="center", rotation=90)
    for px_ in Q.POST["x"]:
        ax.text(px_, Q.BASE_Y + 1.0, "%+.1f" % px_, fontsize=FS, ha="center", va="bottom")
    ax.text(-Q.BASE_X - 1, Q.BASE_Y + 1.0, "posts %.0f x %.0f at x" % (Q.POST["w"], Q.POST["depth"]), fontsize=FS, ha="right", va="bottom")
    K.dim_h(ax, -Q.BASE_X, Q.BASE_X, Q.BASE_Y, "%.1f base (lid plate the same)" % (2 * Q.BASE_X), off=9, fs=5.6)
    K.dim_v(ax, Q.BASE_X, -Q.BASE_Y, Q.BASE_Y, "%.1f" % (2 * Q.BASE_Y), off=6, fs=5.6)
    K.dim_h(ax, -Q.FACE_X, Q.FACE_X, -Q.BASE_Y, "%.1f between the sill faces" % (2 * Q.FACE_X), off=-5, fs=FS)
    K.dim_h(ax, -Q.WALL_X, Q.WALL_X, -Q.BASE_Y, "%.1f walls (%.1f short of each end face)" % (2 * Q.WALL_X, Q.WALL_END), off=-11, fs=FS)
    K.dim_v(ax, -Q.BASE_X, -Q.SIDE_IN, Q.SIDE_IN, "%.1f" % (2 * Q.SIDE_IN), off=-5, fs=FS)
    K.dim_v(ax, -Q.BASE_X, -Q.SIDE_OUT, Q.SIDE_OUT, "%.1f over walls" % (2 * Q.SIDE_OUT), off=-11, fs=FS)
    ax.text(-Q.BASE_X - 14, Q.BASE_Y + 17, "D. THE TRAY (print, Prusament PC Blend) in its own frame, seen from its open face: x toward the hinge (the unit's RIGHT panel),\n"
                                           "y east (the unit's back edge), z up from the lid plate. Brown: walls and posts to z %.1f; tan: floor %.1f, flanges and sills %.1f.\n"
                                           "Red: the ten countersunk M3 into the plate; blue: the six frame screws' holes and their nut slots (dashed, z %.1f .. %.1f)." % (
                                               Q.Z_UT, Q.FLOOR, Q.Z_SILL, Q.NUT_Z[0], Q.NUT_Z[1]), fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.BASE_X - 16, Q.BASE_X + 12); ax.set_ylim(-Q.BASE_Y - 16, Q.BASE_Y + 30)
    # ---- E1. section along the length at y = 0
    ax = fig.add_axes([0.50, 0.76, 0.49, 0.225]); ax.set_aspect("equal"); ax.axis("off")
    cut(ax, [e for e in E if e["part"] in ("plate", "tray", "pad", "frame") and "boss" not in e["name"]], "y", 0.0)
    rect(ax, -Q.U0, Q.Z_UB, Q.U0, Q.Z_UT, fc=COL["unit"], ec="k", lw=0.6, ls="--", alpha=0.6)
    ax.text(0, (Q.Z_UB + Q.Z_UT) / 2, "unit (dashed): lowered in from above, the frame then screwed over it", fontsize=5.6, ha="center", va="center")
    K.dim_v(ax, Q.BASE_X, 0, Q.Z_SILL, "%.1f" % Q.Z_SILL, off=4, fs=FS); K.dim_v(ax, Q.BASE_X, 0, Q.Z_TOP, "%.1f" % Q.Z_TOP, off=10, fs=FS)
    K.dim_v(ax, -Q.BASE_X, 0, Q.FLOOR, "%.1f" % Q.FLOOR, off=-4, fs=FS); K.dim_v(ax, -Q.BASE_X, 0, Q.Z_UB, "%.1f" % Q.Z_UB, off=-9, fs=FS)
    K.dim_v(ax, -Q.BASE_X, Q.Z_UT, Q.Z_TOP, "%.1f" % Q.FRAME_T, off=-4, fs=FS); K.dim_v(ax, -Q.BASE_X, 0, Q.Z_UT, "%.1f" % Q.Z_UT, off=-15, fs=FS)
    K.dim_h(ax, Q.U0 - Q.LEDGE_END, Q.FRAME_X, Q.Z_TOP, "%.1f" % (Q.LEDGE_END + Q.LINTEL_W), off=3, fs=FS)
    ax.text(-Q.BASE_X - 18, Q.Z_TOP + 9, "E1. SECTION ALONG THE LENGTH at y 0 (x to the right, z up from the lid plate): sills, pads, the frame's end bars", fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.BASE_X - 20, Q.BASE_X + 16); ax.set_ylim(-4, Q.Z_TOP + 14)
    # ---- E2. section across at x = 0, through a screwed post
    ax = fig.add_axes([0.50, 0.40, 0.25, 0.35]); ax.set_aspect("equal"); ax.axis("off")
    cut(ax, [e for e in E if e["part"] in ("plate", "tray", "frame", "screw") and "boss" not in e["name"]], "x", 0.0)
    rect(ax, -Q.PAD["size"][1] / 2, 0, Q.PAD["size"][1] / 2, Q.Z_UB, fill=False, ec="k", lw=0.4, ls="--")
    rect(ax, -Q.UNIT[1] / 2, Q.Z_UB, Q.UNIT[1] / 2, Q.Z_UT, fc=COL["unit"], ec="k", lw=0.6, ls="--", alpha=0.6)
    for sy in (-1, 1):
        rect(ax, sy * (Q.POST_Y - Q.NUT["slot_w"] / 2), Q.NUT_Z[0], sy * Q.BASE_Y, Q.NUT_Z[1], fc="white", ec=BLUE, lw=0.5)
        rect(ax, sy * Q.POST_Y - Q.BH["hole"] / 2, Q.Z_TOP - Q.BH["length"] - 2.0, sy * Q.POST_Y + Q.BH["hole"] / 2, Q.Z_TOP, fill=False, ec=BLUE, lw=0.4, ls="--")
    K.dim_h(ax, Q.SIDE_IN - Q.LEDGE_BACK, Q.SIDE_IN, Q.Z_TOP, "%.1f" % Q.LEDGE_BACK, off=5, fs=FS)
    K.dim_h(ax, -Q.SIDE_IN, -Q.SIDE_IN + Q.LEDGE_FRONT, Q.Z_TOP, "%.1f" % Q.LEDGE_FRONT, off=5, fs=FS)
    K.dim_h(ax, Q.SIDE_IN, Q.SIDE_OUT, 0, "%.1f" % Q.WALL, off=-5, fs=FS); K.dim_h(ax, Q.SIDE_OUT, Q.BASE_Y, 0, "%.1f" % Q.POST["depth"], off=-5, fs=FS)
    K.dim_v(ax, Q.BASE_Y, Q.NUT_Z[0], Q.NUT_Z[1], "slot %.1f" % Q.NUT["slot_h"], off=4, fs=FS)
    K.dim_v(ax, Q.BASE_Y, Q.NUT_Z[1], Q.Z_UT, "%.1f" % Q.NUT["roof"], off=10, fs=FS)
    ax.text(-Q.BASE_Y - 4, Q.Z_TOP + 12, "E2. SECTION ACROSS at x 0 (y to the right, the knob edge left),\nthrough two screwed posts: nut slots open outward (blue)", fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.BASE_Y - 6, Q.BASE_Y + 14); ax.set_ylim(-10, Q.Z_TOP + 20)
    # ---- F. the frame in plan
    ax = fig.add_axes([0.755, 0.40, 0.24, 0.35]); ax.set_aspect("equal"); ax.axis("off")
    plan(ax, Q.parts(E, "frame"), lw=0.5)
    for x, y in Q.FRAME_SCREWS: ax.add_patch(Circle((x, y), Q.BH["hole"] / 2, fc="white", ec=BLUE, lw=0.6))
    for sx in (-1, 1):
        ax.add_patch(Circle((sx * Q.KNOB_X, Q.KNOB_Y), Q.KNOB_D / 2 + Q.FINGER, fill=False, ec=GREEN, lw=0.4, ls=":"))
        ax.add_patch(Circle((sx * Q.KNOB_X, Q.KNOB_Y), Q.KNOB_D / 2, fill=False, ec="k", lw=0.4, ls="--"))
    K.dim_h(ax, -Q.FRAME_X, Q.FRAME_X, Q.BASE_Y, "%.1f" % (2 * Q.FRAME_X), off=5, fs=FS); K.dim_v(ax, Q.FRAME_X, -Q.BASE_Y, Q.BASE_Y, "%.1f" % (2 * Q.BASE_Y), off=6, fs=FS)
    K.dim_h(ax, -Q.KNOB_ZONE[1], -Q.KNOB_ZONE[0], -Q.SIDE_OUT, "open %.1f" % (Q.KNOB_ZONE[1] - Q.KNOB_ZONE[0]), off=9, fs=FS)
    K.dim_v(ax, -Q.FRAME_X, -Q.SIDE_IN + Q.LEDGE_FRONT, Q.SIDE_IN - Q.LEDGE_BACK, "opening %.1f" % (2 * Q.SIDE_IN - Q.LEDGE_FRONT - Q.LEDGE_BACK), off=-6, fs=FS)
    ax.text(0, 4, "opening %.1f x %.1f;\nthe knob edge open over |x| %.1f .. %.1f\n(green dotted: each knob's finger room)" % (2 * (Q.U0 - Q.LEDGE_END), 2 * Q.SIDE_IN - Q.LEDGE_FRONT - Q.LEDGE_BACK, *Q.KNOB_ZONE), fontsize=FS, ha="center", va="center")
    ax.text(-Q.FRAME_X - 8, Q.BASE_Y + 14, "F. THE RETAINING FRAME (print, PC Blend, flat, %.1f thick),\nin the tray's frame; six plain %.1f holes" % (Q.FRAME_T, Q.BH["hole"]), fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.FRAME_X - 10, Q.FRAME_X + 12); ax.set_ylim(-Q.BASE_Y - 6, Q.BASE_Y + 22)
    # ---- G. the lid plate and the hole tables
    ax = fig.add_axes([0.005, 0.10, 0.27, 0.29]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Polygon(K.rrect_pts(0, 0, 2 * Q.BASE_X, 2 * Q.BASE_Y, 6.0), closed=True, fc=COL["plate"], ec=BLUE, lw=0.7))
    for x, y in Q.PLATE_HOLES: ax.add_patch(Circle((x, y), Q.TAP / 2, fill=False, ec=RED, lw=0.6))
    K.dim_h(ax, -Q.BASE_X, Q.BASE_X, Q.BASE_Y, "%.1f" % (2 * Q.BASE_X), off=5, fs=FS); K.dim_v(ax, Q.BASE_X, -Q.BASE_Y, Q.BASE_Y, "%.1f" % (2 * Q.BASE_Y), off=5, fs=FS)
    ax.text(0, 0, "LID PLATE: 5052-H32, %.1f, R6 corners,\n10 x M3 tapped through (drill %.1f);\nDXF and STEP in lid-tray-qmx-r2/.\nBond face to the lid: DP8005 over the whole face" % (Q.PLATE_T, Q.TAP), fontsize=5.6, ha="center", va="center")
    ax.text(-Q.BASE_X, Q.BASE_Y + 12, "G. LID PLATE (plan, the tray's frame)", fontsize=5.6, va="bottom")
    ax.set_xlim(-Q.BASE_X - 3, Q.BASE_X + 12); ax.set_ylim(-Q.BASE_Y - 4, Q.BASE_Y + 18)
    rows = ["  #      x       y   what"] + ["%3d %+7.2f %+6.1f   %s" % (k + 1, x, y, w) for k, (x, y, w) in enumerate(
        [(x, y, "tray to plate, between the posts") for x, y in Q.SCREWS_BOSS] + [(x, y, "tray to plate, through a sill") for x, y in Q.SCREWS_END] +
        [(x, y, "frame to post, nut slot z %.1f .. %.1f" % Q.NUT_Z) for x, y in Q.FRAME_SCREWS])]
    text_block(fig, [0.285, 0.10, 0.34, 0.29], rows, fs=FS_TAB, mono=True,
               title="HOLES (part frame; the lid plate's tapped M3 at 1 to 10;\ncase X = %.1f + y, Y = %.1f + x)" % (Q.PLACE_X, Q.PLACE_Y))
    text_block(fig, [0.635, 0.10, 0.355, 0.29], [
        "HARDWARE. Ten %s, each head flush in its %.1f boss and its tip %.1f short of the plate's back face. Six %s with six %s in the posts' slots; "
        "the heads stand %.2f proud of the frame. Two pads, %s, %.0f x %.0f, in the floor windows on the plate. 3M DP8005 for the plate." % (
            Q.SCREW, Q.Z_SILL, Q.PLATE_T - (5.0 - Q.Z_SILL), Q.FRAME_SCREW, Q.FRAME_NUT, Q.BH["k"], Q.PAD["material"], Q.PAD["size"][0], Q.PAD["size"][1]),
        "MASSES (from the solids): tray %.1f g, frame %.1f g in PC Blend (1.22 g/cm3); lid plate %.1f g in 5052 (2.68 g/cm3); the unit 220 g (maker)." % (
            1000 * C.MASSES["tray"], 1000 * C.MASSES["frame"], 1000 * C.MASSES["plate"]),
        "PRINT. Tray floor down, frame flat, Prusament PC Blend, 100 percent infill, 0.20 mm layers (the data sheet's specimen settings, which the "
        "retention figures assume). No part has an overhang; the only bridges are the six nut slots' roofs, %.1f wide, which print without support. "
        "Printed dimensions +-0.2 (INFERRED)." % Q.NUT["slot_w"]], fs=FS_NOTE, title="HARDWARE, MASSES, PRINT")
    fig.savefig(os.path.join(OUT, "lid-tray-qmx-r2-drawing-2.png"), dpi=110); pdf.savefig(fig); plt.close(fig)


# ======================================================================================= sheet 3: fitting, notes, the record's rows
def page3(pdf):
    fig = sheet("QMX lid tray r2: fitting, operation, what stays open, and the record's face-room, fitting and retention rows", "14r2-3 of 3")
    one, two = C.fitting(E)
    l1, l2 = C.judge(one[1])[1], C.judge(two[1])[1]
    notes = [
        "1. FITTING, in this order. (a) Bond the lid plate to the lid's unribbed inner face at the place of sheet 14r2-1 with DP8005 (clean, dry; the sheet asks no "
        "primer on polypropylene; fixture 2 h). (b) Screw the tray on with its ten M3 x 5. (c) Lay the two pads in the floor windows, on the plate. (d) Slide a "
        "square nut into each of the six slots from outside. (e) Do NOT fit the unit's four self-adhesive feet (the maker calls them optional). With the lid open "
        "and the knobs on, lower the unit into the pocket from above, top face out, knob edge west, right panel (RF, PTT, USB) toward the hinge: it stands on the "
        "pads, %.2f above its place. (f) Lay the frame over it on the wall tops and drive the six M3 x 10 evenly until the frame sits on the wall tops all round; "
        "the pads are compressed by %.2f (%.2f to %.2f over the tolerances). (g) Plug the DC, RF and USB leads and tie each within 60 mm of its plug to a tie "
        "mount bonded to the lid, so no lead pulls on a jack. To take the unit out: the three plugs, the six frame screws, the frame, the unit." % (
            Q.PAD["t"] - Q.Z_UB, Q.PAD["t"] - Q.Z_UB, Q.PAD["t"] * (1 - Q.PAD["t_tol"]) - (Q.Z_UB + C.PRINT_TOL + Q.UNIT_TOL), Q.PAD["t"] * (1 + Q.PAD["t_tol"]) - (Q.Z_UB - C.PRINT_TOL - Q.UNIT_TOL)),
        "2. THE WAY IN IS CHECKED (the record, section E): the unit at its largest, with its knobs, button actuators and jacks, keeps %.2f to every solid of the "
        "tray on its way down (the least: %s to the %s), and the frame keeps %.2f to everything that stands proud of the unit (the least: %s to the %s); the "
        "stated minimum is %.2f. The first pass's tray, whose ledges and lintels were part of the tray, fails the same check, as it must." % (
            l1["clearance"], l1["by"], l1["solid"], l2["clearance"], l2["by"], l2["solid"], C.MIN_INSERT),
        "3. OPERATION: the LCD, both knobs and both buttons face the operator with the lid open (the text then reads down the lid); the frame keeps %.0f mm of "
        "finger room round each knob. The Paddle, Audio and PTT plugs are the operator's and come out before the lid closes." % Q.FINGER,
        "4. OPEN, carried with this set (not closed by it): (a) THE LID HARNESS'S CROSSING OF THE SEALED FACE: how the DC lead, the USB-C lead and the RG-316 "
        "jumper get from the lid to boards B and A under the face plate, which has no pass-through, is designed nowhere; it blocks the harness picks, ASSEMBLY's "
        "lid harness steps and the closing of the lid on a wired QMX. (b) The lid plate's bond strength on the case's polypropylene, and after a thermal cycle "
        "(T8 pull test). (c) The peak E1 puts on the lid (E1 with an accelerometer on the lid); the set is designed to %.0f g, an assumed peak. (d) The knob "
        "height (T9 with chalk on the knob tips, or the unit in hand): the knob rows are OPEN. (e) The lid's response in E2 and the pads' preload at their real "
        "compression. (f) The harness picks against the admitted plug bodies and R %.0f. (g) A threadlocker for the six frame screws and the ten tray screws "
        "that its maker states compatible with polycarbonate: none is named." % (C.DESIGN_G, C.LEAD_R)]
    text_block(fig, [0.015, 0.795, 0.97, 0.19], notes, fs=7.4, title="NOTES")
    face = [l[3:] for l in section_of(REPORT, "B. FACE ROOM") if l.strip().startswith(("row and part", "M3r2."))]
    text_block(fig, [0.015, 0.545, 0.97, 0.235], face, fs=6.3, mono=True,
               title="FACE ROOM, every row from the solid above the part (the record, section B): height above the face, depth from the lid ceiling, nominal, worst, worst with unstated allowances twice")
    ret = section_of(REPORT, "D. RETENTION")
    k0 = [n for n, l in enumerate(ret) if l.strip().startswith("dir ")][0]; k1 = [n for n, l in enumerate(ret) if l.strip().startswith("Governing link")][0]
    lines = [l[3:] for l in ret[1:3]] + [l[3:] for l in ret[k0:k1 + 1]]
    text_block(fig, [0.015, 0.245, 0.97, 0.285], lines, fs=6.0, mono=True,
               title="RETENTION (the record, section D): each link's capacity in N and in g on the unit, and its factor on the load case; the whole section, with E1, E2 and the sustained load, is in the record")
    K.tolerance_box(fig, [0.015, 0.098, 0.97, 0.125], extra=["Jack places, the knobs and everything proud of the unit are SCALED or INFERRED from the maker's undimensioned figures and photographs "
                    "(v2/vendor/qrp-labs/); the unit's 95 x 63 x 25 and 220 g are the maker's. Printed parts +-0.2 (FFF, INFERRED)."], fs=5.6)
    fig.savefig(os.path.join(OUT, "lid-tray-qmx-r2-drawing-3.png"), dpi=110); pdf.savefig(fig); plt.close(fig)


if __name__ == "__main__":
    with PdfPages(os.path.join(OUT, "lid-tray-qmx-r2-drawing.pdf")) as pdf:
        page1(pdf); page2(pdf); page3(pdf)
    print("wrote lid-tray-qmx-r2-drawing.pdf (3 pages) and the page PNGs")
    print("LID-TRAY-QMX-R2-DRAWING-DONE")
