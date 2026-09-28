#!/usr/bin/env python3
"""Sheet H1-1: the manufacturing drawing of H1, the heat-test face plate blank (v2/cad/h1_heat_test_plate.py), A3 landscape.

MESHSAT-1357, stream od01b, 29 Sep 2026. H1's own drawing, so the request for quote no longer orders it as "C1's CAD plus prose that
overrides the drawing". Every feature is drawn from h1_heat_test_plate.features(), which reads v2/ecad/tools/panel1450.py (C1's
single geometry source) and the Arcol HS100 fixing pattern; nothing on the sheet is typed except the labels, the tolerances and the
notes. Prototype drawing: nothing has been made.
Usage: h1_heat_test_plate_drawing.py <out.pdf> [<out.png>]   (matplotlib; the pinned CAD set of v2/cad/requirements-cad.lock)."""
import sys, os, textwrap, datetime, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import drawing_kit as K
from drawing_kit import plt, Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages
import panel1450 as L
import h1_heat_test_plate as P

out_pdf = sys.argv[1]; out_png = sys.argv[2] if len(sys.argv) > 2 else None
W, H, T = L.PLATE
INPUTS = ["v2/ecad/tools/panel1450.py", "v2/cad/h1_heat_test_plate.py", "v2/cad/h1_heat_test_plate_drawing.py",
          "v2/release/case-2026-09-27/face-plate/face-plate.dxf", "v2/vendor/arcol/arcol-hs-datasheet-12-14-08.pdf"]


def sheet():
    fig = plt.figure(figsize=K.A3, dpi=100); fig.patch.set_facecolor("white")
    fig.add_artist(Rectangle((0.008, 0.008), 0.984, 0.984, transform=fig.transFigure, fill=False, lw=1.0, color="k"))
    tb = fig.add_axes([0.008, 0.008, 0.984, 0.085]); tb.axis("off"); tb.set_xlim(0, 1); tb.set_ylim(0, 1)
    tb.add_patch(Rectangle((0, 0), 1, 1, fill=False, lw=1.0))
    for x in (0.30, 0.62, 0.86): tb.plot([x, x], [0, 1], lw=0.6, color="k")
    tb.text(0.005, 0.92, "MeshSat field kit V2, Peli 1450 case set: heat-test part", fontsize=7.5, fontweight="bold", va="top")
    tb.text(0.005, 0.62, "H1 heat-test face plate blank: 377.2 x 263.0 x 3.0, ten 6-32 holes,\nfour PEM S-M3 on the HS100 pattern 37.0 (X) x 35.0 (Y)", fontsize=8.4, fontweight="bold", va="top", linespacing=1.05)
    tb.text(0.005, 0.04, "MESHSAT-1357 (od01b). PROTOTYPE: nothing made, bought or fitted.\nQuantity 1. Serves ONLY the empty-case heat-balance test.", fontsize=5.6, va="bottom")
    try:
        base = os.environ.get("CASE_BASE_COMMIT") or subprocess.check_output(["git", "-C", K.REPO, "rev-parse", "--short=8", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        base = "unknown"
    src = ["Source: tree %s; inputs by sha256 (first 12):" % base] + ["  %s  %s" % (K.sha12(os.path.join(K.REPO, p)), p) for p in INPUTS]
    tb.text(0.305, 0.95, "\n".join(src), fontsize=5.3, va="top", family="monospace")
    tb.text(0.625, 0.95, "\n".join(textwrap.wrap("Generated %s by v2/cad/h1_heat_test_plate_drawing.py from the files named left. The editable sources govern; "
                                                   "this sheet governs over the DXF and STEP of H1 where they differ (tell us)." % datetime.date.today().isoformat(), 62)), fontsize=6, va="top")
    tb.text(0.865, 0.80, "Sheet H1-1 of 1", fontsize=10, fontweight="bold", va="top")
    tb.text(0.865, 0.45, "A3, mm\nnot to scale for measurement:\ndimensions govern", fontsize=6.3, va="top")
    return fig


with PdfPages(out_pdf) as pdf:
    fig = sheet()
    ax = fig.add_axes([0.005, 0.30, 0.60, 0.68]); ax.set_aspect("equal"); ax.axis("off")
    for layer, kind, p in P.features():
        if kind == "poly":
            xs = [q[0] for q in p] + [p[0][0]]; ys = [q[1] for q in p] + [p[0][1]]
            style = dict(OUTLINE=("k", "-", 1.0), REBATE_2MM_TOP=("k", "-", 0.5)).get(layer, ("k", "--", 0.5))
            ax.plot(xs, ys, color=style[0], ls=style[1], lw=style[2])
        else:
            x, y, d = p
            ax.add_patch(Circle((x, y), d / 2, fill=False, lw=0.7, ec="k" if layer == "THROUGH" else "#0b5394"))
            if layer == "PEM_S_M3":
                ax.add_patch(Circle((x, y), 3.1, fill=False, lw=0.4, ec="#0b5394", ls=":"))   # the nut's head outline, top face (indicative)
    x0, y0, x1, y1 = P.PATCH_RECT
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="#777777", lw=0.6, ls="-."))
    cx, cy = P.PATCH_C
    ax.plot([cx, cx], [y0 - 4, y1 + 4], lw=0.4, ls="-.", color="#777777"); ax.plot([x0 - 4, x1 + 4], [cy, cy], lw=0.4, ls="-.", color="#777777")
    ax.text(x1 + 2, y1 - 3, "Arcol HS100 (phantom, on the UNDERSIDE):\nA %.1f max across, B %.1f max along its axis (Y);\nnot part of H1" % (P.HS100["A_max"], P.HS100["B_max"]),
            fontsize=5.2, color="#555555", va="top")
    K.dim_h(ax, -W / 2, W / 2, H / 2, "%.1f +-0.10 (R%.0f)" % (W, L.PLATE_R), off=12)
    K.dim_v(ax, W / 2, -H / 2, H / 2, "%.1f +-0.10" % H, off=14)
    K.dim_h(ax, -L.REB_IN[0] / 2, L.REB_IN[0] / 2, -H / 2, "full-thickness face %.1f (R%.0f); outside it the band is rebated %.1f from the top (1.0 left)" % (L.REB_IN[0], L.REBATE_R, L.REBATE), off=-12, fs=5.8)
    K.dim_v(ax, -W / 2, -L.REB_IN[1] / 2, L.REB_IN[1] / 2, "%.1f" % L.REB_IN[1], off=-14)
    bx = sorted(set(round(abs(x), 2) for x, y in L.FRAME_BOSSES)); by = sorted(set(round(abs(y), 2) for x, y in L.FRAME_BOSSES))
    K.dim_h(ax, -179.07, 179.07, -75.95, "6-32 clearance holes d%.1f THRU at Peli's inserts: 358.14" % L.FACE_HOLE, off=-7, fs=5.3)
    K.dim_v(ax, 139.45, -121.16, 121.16, "242.32", off=-9, fs=5.3)
    K.dim_h(ax, -139.45, 139.45, 121.16, "278.90", off=-7, fs=5.3); K.dim_v(ax, 179.07, -75.95, 75.95, "151.90", off=-9, fs=5.3)
    xs = sorted(set(round(x, 2) for x, y in P.PEM_XY)); ys = sorted(set(round(y, 2) for x, y in P.PEM_XY))
    K.dim_h(ax, xs[0], xs[1], ys[0], "%.1f +-0.10 (G)" % (xs[1] - xs[0]), off=-8, fs=5.3, color="#0b5394")
    K.dim_v(ax, xs[0], ys[0], ys[1], "%.1f +-0.10 (F)" % (ys[1] - ys[0]), off=-8, fs=5.3, color="#0b5394")
    K.dim_h(ax, cx, 0, 0, "%.1f" % abs(cx), off=-18, fs=5.3, color="#0b5394"); K.dim_v(ax, 0, 0, cy, "%.1f" % cy, off=10, fs=5.3, color="#0b5394")
    ax.text(cx, y0 - 3, "4 x %s, holes d%.1f THRU, pressed from the TOP face,\nflush on the underside; pattern centre (%.1f, %.1f) = the PA flange site" % (P.PEM_PART, P.PEM_HOLE, cx, cy),
            fontsize=5.6, ha="center", va="top", color="#0b5394")
    rx0, ry0, rx1, ry1, rd = L.RELIEF_POCKET
    ax.text((rx0 + rx1) / 2, ry1 + 1.5, "relief %.1f x %.1f x %.1f deep in the UNDERSIDE" % (rx1 - rx0, ry1 - ry0, rd), fontsize=5.0, ha="center", va="bottom")
    for (x, y) in L.FRAME_BOSSES: ax.text(x, y + 3.6, "6-32", fontsize=4.6, ha="center")
    ax.text(0, 0, "+", fontsize=9, ha="center", va="center"); ax.text(2, -5, "case centre (datum)", fontsize=5.0)
    ax.text(0, H / 2 + 22, "SEEN FROM ABOVE (the top face). X along the case, +Y toward the hinge wall. No other feature: H1 is a closed skin.", fontsize=6, ha="center")
    K.scale_bar(ax, -W / 2 - 25, -H / 2 - 27)
    ax.set_xlim(-W / 2 - 34, W / 2 + 30); ax.set_ylim(-H / 2 - 32, H / 2 + 26)

    # section through a PEM nut and the resistor's flange (schematic, not to scale for measurement)
    sx = fig.add_axes([0.62, 0.70, 0.37, 0.28]); sx.set_aspect("equal"); sx.axis("off")
    sx.add_patch(Rectangle((0, 0), 30, T, fc="#9aa6b2", ec="k", lw=0.6))                      # H1
    sx.add_patch(Rectangle((13.9, 0), 4.2, T, fc="white", ec="k", lw=0.4))                    # the 4.2 hole
    sx.add_patch(Rectangle((13.9, T - 1.38), 4.2, 1.38, fc="#3d6fa8", ec="k", lw=0.4))       # clinched shank (indicative)
    sx.add_patch(Rectangle((12.9, T), 6.2, 1.5, fc="#3d6fa8", ec="k", lw=0.4))                # the nut's head on the top face (indicative)
    sx.add_patch(Rectangle((4, -3.0), 22, 3.0, fc="#c9c9c9", ec="k", lw=0.5))                  # the HS100's flange, 3.0 (Arcol)
    sx.add_patch(Rectangle((4, -0.15), 22, 0.15, fc="#f2c14e", ec="none"))                     # compound
    sx.add_patch(Rectangle((14.5, -6.5), 3.0, 6.5 + T + 1.5, fc="none", ec="k", lw=0.5, ls="--"))  # M3 screw
    sx.add_patch(Rectangle((13.0, -4.2), 6.0, 1.2, fc="#666666", ec="k", lw=0.3))              # washer and head
    sx.text(31, T / 2, "H1, %.1f, black anodised" % T, fontsize=5.4, va="center")
    sx.text(20, T + 1.8, "%s head on the TOP face\n(install after anodising)" % P.PEM_PART, fontsize=5.0)
    sx.text(27, -1.5, "HS100 flange 3.0 +-0.1, holes d3.2 max\n(Arcol 12/14.08 p. 2); compound in between", fontsize=5.0, va="center")
    sx.text(0, -7.5, "M3 A2 pan head and flat washer from BELOW through the resistor into the nut", fontsize=5.0)
    sx.text(0, 9.0, "SECTION THROUGH ONE NUT (schematic): the resistor sits flat on the flush underside", fontsize=5.8)
    sx.set_xlim(-1, 55); sx.set_ylim(-9, 10)

    tx = fig.add_axes([0.62, 0.30, 0.37, 0.39]); tx.axis("off")
    rows = [("Part", "H1, heat-test face plate blank, quantity 1. It is NOT the face plate C1 (sheet 1) and is not fitted to the kit: it serves only the empty-case heat-balance test."),
            ("Material, thickness", "EN AW-5754 (H22 or H32) or EN AW-6061-T6 aluminium plate, 3.0 +-0.13 (EN 485-4 class, INFERRED). No substitution without asking."),
            ("Finish", "Black anodised all over (Type II / sulphuric acid class, dyed black, sealed), the same finish as C1, because the test measures the heat that leaves "
             "through this plate and the finish sets its emissivity. The four PEM nuts are pressed AFTER anodising. No marking, no paint."),
            ("Outline and seal", "%.1f x %.1f R%.0f; band outside %.1f x %.1f (R%.0f) rebated %.1f from the top, 1.0 left; relief %.1f x %.1f x %.1f in the underside over the frame's "
             "lettering; underside otherwise flat: it covers Peli's o-ring as C1 does" % (W, H, L.PLATE_R, L.REB_IN[0], L.REB_IN[1], L.REBATE_R, L.REBATE, rx1 - rx0, ry1 - ry0, rd)),
            ("Holes", "10 x d%.1f THRU at Peli's insert bores (the same places as C1), for 6-32 UNC x 1/2 in A2 pan heads by hand; 4 x d%.1f THRU for %s on the HS100's "
             "pattern, G 37.0 along X and F 35.0 along Y, centre (%.1f, %.1f)" % (L.FACE_HOLE, P.PEM_HOLE, P.PEM_PART, cx, cy)),
            ("Omitted from C1", "both windows and the e-paper pocket, all control, light-guide, sounder, headset and camera holes, the monitor frame's four 4.5 holes, the eight "
             "PEM SO-M3-10 standoffs and C1's two PA nuts 60 apart"),
            ("Flatness", "0.5 over the plate after anodising and nut insertion (the session's figure: a gap under the edge would open the o-ring seal the test relies on); "
             "report the measured value"),
            ("Files", "h1-heat-test-plate.dxf (layers OUTLINE, THROUGH, REBATE_2MM_TOP, RELIEF_0.8MM_UNDERSIDE, PEM_S_M3), .step, .stl; this sheet governs")]
    fig.canvas.draw(); rend = fig.canvas.get_renderer(); inv = tx.transAxes.inverted()
    def height(t):
        bb = t.get_window_extent(renderer=rend); lo = inv.transform((bb.x0, bb.y0)); hi = inv.transform((bb.x1, bb.y1)); return hi[1] - lo[1]
    y = 0.99
    for a, b in rows:
        t1 = tx.text(0.0, y, a, fontsize=6.2, fontweight="bold", va="top", transform=tx.transAxes); y -= height(t1) + 0.003
        t2 = tx.text(0.0, y, "\n".join(textwrap.wrap(b, 118)), fontsize=5.3, va="top", linespacing=1.1, transform=tx.transAxes); y -= height(t2) + 0.022
    nx = fig.add_axes([0.015, 0.098, 0.505, 0.19]); nx.axis("off")
    notes = ["NOTES",
             "1. Units mm. Datum: the case centre (the plate's centre); X along the case, +Y toward the hinge wall. The DXF is in the same frame.",
             "2. The HS100 is not part of H1: it is shown to place the pattern. Its holes are 3.2 max on F 35.0 +-0.3 x G 37.0 +-0.3 (Arcol 12/14.08 p. 2); an M3 floats "
             "about 0.1 in them, so the pattern's tolerance here is +-0.10 and the operator checks the resistor's own pattern at receipt (TEST-PROCEDURE.md).",
             "3. The resistor's footprint stays inside the 1450PF window, %.1f mm from its edge at +Y (the ring under the plate): bend the +Y tag's lead down and "
             "toward -Y (h1-heat-test-plate-check.out)." % (L.WINDOW[1] / 2 - P.PATCH_RECT[3]),
             "4. Break all edges 0.2 to 0.5; no burr on the underside's sealing band. Deburr the PEM holes lightly on the top face only.",
             "5. Quote per RFQ line H1 (v2/docs/records/od01/MACHINING-RFQ.md). Do not cut before the case and frame have passed the receipt checks R1 to R8 of that request."]
    nx.text(0, 1, "\n".join(sum((textwrap.wrap(n, 130) for n in notes), [])), fontsize=5.4, va="top", linespacing=1.15)
    K.tolerance_box(fig, None, extra=["H1 (this sheet): outline +-0.10; thickness 3.0 +-0.13; rebate depth 2.0 and its line +-0.10; relief depth 0.8 +-0.10; the ten "
                                      "6-32 holes and the four PEM holes on position +-0.10 from the datum; hole diameters as drawn +0.10/-0.00 unless the nut maker's "
                                      "installation data ask otherwise (tell us)."])
    pdf.savefig(fig)
    if out_png: fig.savefig(out_png, dpi=110)
    plt.close(fig)
print("H1-DRAWING-DONE", out_pdf)
