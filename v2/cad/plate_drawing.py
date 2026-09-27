#!/usr/bin/env python3
"""Dimensioned drawing of the Peli 1450 face plate (v2/cad/face_plate.py) from its DXF: sheet 1 of the case set, A3 landscape, with the outline,
every cut-out, the ten 6-32 screw holes at Peli's insert bores, the rebated band, the relief pocket, the standoff holes, the pockets, a dimension
set, an edge section (the plate on the frame's ring over Peli's o-ring, C1 on C6), the cut-out table from v2/ecad/tools/panel1450.py, the
tolerance statement, the source revision with the sha256 of its inputs, and the margin rows the plate enters (v2/vendor/peli/1450/frame_seat.out),
OPEN ones in red. Prototype drawing: nothing has been made. First issue 5 Sep 2026 (appendix 32.42); this issue 27 Sep 2026 (MESHSAT-1357, C1).
Usage: plate_drawing.py <face-plate.dxf> <out.pdf>   (ezdxf + matplotlib: v2/cad/requirements-cad.txt)."""
import sys, os, math, textwrap
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "ecad", "tools"))
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy
import drawing_kit as K
from drawing_kit import plt, Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages
import panel1450 as L

dxf_fn, out_fn = sys.argv[1], sys.argv[2]
doc = ezdxf.readfile(dxf_fn); msp = doc.modelspace()
W, H = L.PLATE[0], L.PLATE[1]
RED = "#b00020"
with PdfPages(out_fn) as pdf:
    fig = K.sheet("Face plate (C1): 377.2 x 263.0 x 3.0 on the 1450PF frame, ten 6-32 into Peli's inserts, rebated band", 1, 14,
                  ["v2/ecad/tools/panel1450.py", "v2/cad/face_plate.py", "v2/vendor/peli/1450/frame_seat.out"], part="plate_drawing.py (sheet 1)")
    ax = fig.add_axes([0.005, 0.28, 0.61, 0.70])
    ctx = RenderContext(doc); Frontend(ctx, MatplotlibBackend(ax), config=Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE)).draw_layout(msp, finalize=True)
    fig.set_size_inches(*K.A3)          # ezdxf's finalize resizes the figure to the drawing; the sheet is A3
    ax.set_xlim(-W / 2 - 34, W / 2 + 30); ax.set_ylim(-H / 2 - 32, H / 2 + 26); ax.set_aspect("equal"); ax.axis("off")
    dim, vdim = K.dim_h, K.dim_v
    dim(ax, -W / 2, W / 2, H / 2, "%.1f +-0.10 (plate, R%.0f)" % (W, L.PLATE_R), off=12); vdim(ax, W / 2, -H / 2, H / 2, "%.1f +-0.10" % H, off=14)
    dim(ax, -L.REB_IN[0] / 2, L.REB_IN[0] / 2, -H / 2, "full-thickness face %.1f (R%.0f); outside it the band is rebated %.1f from the top" % (L.REB_IN[0], L.REBATE_R, L.REBATE), off=-12, fs=5.8)
    vdim(ax, -W / 2, -L.REB_IN[1] / 2, L.REB_IN[1] / 2, "%.1f" % L.REB_IN[1], off=-14)
    dim(ax, -179.07, 179.07, -75.95, "6-32 holes %.1f at Peli's inserts: 358.14 (sheet 358.1)" % L.FACE_HOLE, off=-7, fs=5.5)
    vdim(ax, 139.45, -121.16, 121.16, "242.32", off=-9, fs=5.3)
    dim(ax, -139.45, 139.45, 121.16, "278.90", off=-7, fs=5.3); vdim(ax, 179.07, -75.95, 75.95, "151.90", off=-9, fs=5.3)
    rx0, ry0, rx1, ry1, rd = L.RELIEF_POCKET
    ax.add_patch(Rectangle((rx0, ry0), rx1 - rx0, ry1 - ry0, fill=False, ec="k", lw=0.5, ls="--"))
    ax.text((rx0 + rx1) / 2, ry1 + 1.5, "relief %.1f x %.1f x %.1f in the UNDERSIDE (lettering)" % (rx1 - rx0, ry1 - ry0, rd), fontsize=5.0, ha="center", va="bottom")
    dx, dy = L.XENARC["c"]; mw, mh = L.XENARC["window"]
    dim(ax, dx - mw / 2, dx + mw / 2, dy - mh / 2, "monitor window %.2f" % mw, off=-6, fs=5.5); vdim(ax, dx + mw / 2, dy - mh / 2, dy + mh / 2, "%.2f" % mh, off=6, fs=5.5)
    ax.text(dx, dy + 8, "Xenarc 709GNK IN the plate, glass level with the face; rear frame M4 x4", fontsize=5.5, ha="center")
    ex, ey = L.EPAPER["c"]; ww, wh = L.EPAPER["window"]
    dim(ax, ex - ww / 2, ex + ww / 2, ey + wh / 2, "e-paper window %.2f x %.1f" % (ww, wh), off=6, fs=5.5)
    for ref, (x, y), hole, depth in L.BUTTONS: ax.text(x + hole / 2 + 3, y, "%s\nd%.1f" % (ref, hole), fontsize=5.3, va="center")
    for ref, (x, y) in L.TOGGLES: ax.text(x - 22, y, "%s\nd%.1f + key" % (ref, L.TOGGLE_HOLE), fontsize=5.3, va="center")
    ax.text(L.LIGHT[1][0] - 22, L.LIGHT[1][1], "%s\nD %.1f/%.1f" % (L.LIGHT[0], L.LIGHT_HOLE, L.LIGHT_FLAT), fontsize=5.3, va="center")
    ax.text(L.SOUNDER[1][0], L.SOUNDER[1][1] - L.SOUNDER[2] / 2 - 4, "%s d%.1f" % (L.SOUNDER[0], L.SOUNDER[2]), fontsize=5.3, ha="center", va="top")
    for ref, (x, y) in L.HEADSETS: ax.text(x, y - L.HEADSET_HOLE / 2 - 3, "%s d%.1f" % (ref, L.HEADSET_HOLE), fontsize=5.0, ha="center", va="top")
    ax.text(L.CAMERA[1][0], L.CAMERA[1][1] + 7, "camera d%.0f" % L.CAMERA[2], fontsize=5.3, ha="center")
    ax.text(L.PA_MOUNT["c"][0], L.PA_MOUNT["c"][1] + 13, "PA flange: 2 x PEM S-M3 (4.2) %.0f apart, underside" % L.PA_MOUNT["holes"], fontsize=5.3, ha="center")
    for k, (x, y) in enumerate(L.FRAME_BOSSES): ax.text(x, y + 3.6, "6-32", fontsize=4.6, ha="center")
    ax.text(0, 0, "+", fontsize=9, ha="center", va="center")
    ax.text(0, H / 2 + 22, "SEEN FROM ABOVE (the face). Case frame: X along the case, +Y toward the hinge wall; the cross is the case centre.", fontsize=6, ha="center")
    K.scale_bar(ax, -W / 2 - 25, -H / 2 - 27)
    K.tag(ax, W / 2, 0, "M8x OPEN", dx=8, dy=30); K.tag(ax, 0, H / 2, "M8y OPEN", dx=60, dy=8)
    K.tag(ax, -L.REB_IN[0] / 2, H / 2 - 3, "M2, M2b OPEN (band under the lid)", dx=10, dy=18)
    K.tag(ax, dx - mw / 2, dy, "M1 OPEN (body over the heatsinks)", dx=-40, dy=-40, ha="right")
    # edge section: the plate on the ring over the o-ring channel
    sx = fig.add_axes([0.62, 0.64, 0.37, 0.345]); sx.set_aspect("equal"); sx.axis("off")
    zt = L.FACE_TOP_Z; zu = L.PLATE_UNDER_Z; zr = L.LEG_TOP_Z
    sx.add_patch(Rectangle((174.83, zr), 182.75 - 174.83, L.PELI["ring_t"], fc="#bbbbbb", ec="k", lw=0.5))
    sx.add_patch(Rectangle((183.34, L.FRAME_BOTTOM_Z), 189.18 - 183.34, zu - L.FRAME_BOTTOM_Z, fc="#bbbbbb", ec="k", lw=0.5))
    sx.add_patch(Polygon([(170, zu), (W / 2, zu), (W / 2, zu + L.PLATE[2] - L.REBATE), (L.REB_IN[0] / 2, zu + L.PLATE[2] - L.REBATE), (L.REB_IN[0] / 2, zt), (170, zt)],
                         closed=True, fc="#9aa6b2", ec="k", lw=0.6))
    sx.add_patch(Circle((186.9, zu - 1.4), 1.4, fc="#333333", ec="k", lw=0.3))
    TW = 0.0349 / 0.9994
    sx.plot([186.97 + TW * 90, 186.97 + TW * 101.04, 187.48 + TW * 101.04, 191.29], [90, 101.04, 101.04, 108.97], color="k", lw=0.9)
    sx.plot([170, 196], [108.97, 108.97], lw=0.4, ls="--", color="#777777"); sx.text(170.5, 109.4, "Peli rim 108.97", fontsize=5, color="#777777")
    sx.plot([179.07, 179.07], [zr - 1, zt + 1], lw=0.4, ls="-.", color="k")
    sx.add_patch(Rectangle((179.07 - 1.75, zt), 3.5, 2.2, fc="#666666", ec="k", lw=0.3))
    sx.text(179.07, zt + 3.0, "6-32 pan head", fontsize=4.8, ha="center")
    K.dim_v(sx, W / 2, zu, zt, "3.0", off=3.0, fs=5); K.dim_v(sx, W / 2, zu + L.PLATE[2] - L.REBATE, zt, "2.0", off=6.0, fs=5)
    K.dim_h(sx, L.REB_IN[0] / 2, W / 2, zt, "%.1f" % (W / 2 - L.REB_IN[0] / 2), off=3.5, fs=5)
    sx.text(170.5, zt + 1.0, "face top %.2f (104.77..108.27)" % zt, fontsize=5.2)
    sx.text(175.2, zr + 3.5, "1450PF ring 9.39", fontsize=4.8); sx.text(183.5, L.FRAME_BOTTOM_Z + 2, "skirt", fontsize=4.8)
    sx.text(186.0, zu - 5.0, "Peli o-ring in the\nchannel, covered", fontsize=4.6)
    K.tag(sx, 191.0, zu + 0.5, "M8z OPEN (underside above the shoulder)", dx=0, dy=-12, ha="right")
    sx.text(170, 116, "EDGE SECTION at the east end insert (X-Z), not to scale for measurement", fontsize=5.8)
    sx.set_xlim(169, 198); sx.set_ylim(84, 118)
    # the table
    tx = fig.add_axes([0.62, 0.28, 0.37, 0.35]); tx.axis("off")
    rows = [("Plate", "%.1f x %.1f x %.1f, R%.0f, 5754 or 6061, black anodised; band outside %.1f x %.1f rebated %.1f from the top (1.0 left); relief %.1f x %.1f x %.1f in the underside over the frame's lettering" % (
                W, H, L.PLATE[2], L.PLATE_R, L.REB_IN[0], L.REB_IN[1], L.REBATE, rx1 - rx0, ry1 - ry0, rd)),
            ("Screws", "10 x %s from above into Peli's brass inserts (6-32 x 1/4, M3.5 x 6.3), by hand, no pressure (Peli step 4); holes %.1f at the STEP bores" % (L.FACE_SCREW, L.FACE_HOLE)),
            ("Seal", "Peli's o-ring in the channel between the frame and the case wall, covered by the plate (Peli step 4); every cut-out sealed by its part. The PORON ring of the earlier construction is dropped (C1). Water shows it: T3, T7"),
            ("Monitor", "Xenarc 709GNK IN the plate at (%.0f, %.0f), glass level with the face (owner ruling 9 Sep 2026): window %.2f x %.2f R%.0f, four M4 (4.5) for the rear frame" % (dx, dy, mw, mh, L.XENARC["window_r"])),
            ("E-paper", "window %.2f x %.1f at (%.0f, %.0f); 1.0 pocket for the 1.0 lens on 0.05 tape" % (ww, wh, ex, ey)),
            ("Controls", "; ".join("%s d%.1f" % (r, h_) for r, c, h_, d in L.BUTTONS) + "; toggles d%.1f + key; NKK D %.1f; sounder d%.1f; headsets d%.1f; camera d%.0f" % (
                L.TOGGLE_HOLE, L.LIGHT_HOLE, L.SOUNDER[2], L.HEADSET_HOLE, L.CAMERA[2])),
            ("Light guides", "17 x d%.1f H7 (Mentor 1282.5004)" % L.LED_HOLE),
            ("Standoffs", "8 x PEM SO-M3-10 (4.2) for the backer C; 2 x PEM S-M3 (4.2) for the PA flange"),
            ("Marking", "face-plate-marking.svg (laser)")]
    fig.canvas.draw(); rend = fig.canvas.get_renderer(); inv = tx.transAxes.inverted()
    def height(t):
        bb = t.get_window_extent(renderer=rend); lo = inv.transform((bb.x0, bb.y0)); hi = inv.transform((bb.x1, bb.y1)); return hi[1] - lo[1]
    y = 0.99
    for a, b in rows:
        t1 = tx.text(0.0, y, a, fontsize=6.2, fontweight="bold", va="top", transform=tx.transAxes); y -= height(t1) + 0.003
        t2 = tx.text(0.0, y, "\n".join(textwrap.wrap(b, 120)), fontsize=5.3, va="top", linespacing=1.1, transform=tx.transAxes); y -= height(t2) + 0.008
    K.rows_box(fig, None, ["M1", "M2", "M2b", "M3", "M8x", "M8y", "M8z", "M8f", "M8h", "M19", "M21h"])
    K.tolerance_box(fig, None, extra=["Plate float on the smallest 6-32 in a 4.6 hole: 0.63 (every plate chain carries it)."])
    pdf.savefig(fig); plt.close(fig)
print("PLATE-DRAWING-DONE", out_fn)
