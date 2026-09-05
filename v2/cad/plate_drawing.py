#!/usr/bin/env python3
"""Dimensioned drawing of the Peli 1450 face plate (v2/cad/face_plate.py) from its DXF: A3 landscape at 1:2 with the outline, every cut-out, the
frame screw holes, the standoff holes, the pockets, a dimension set and the cut-out table from v2/ecad/tools/panel1450.py. Prototype drawing,
5 Sep 2026 (appendix 32.42). Usage: plate_drawing.py <face-plate.dxf> <out.pdf>   (ezdxf + matplotlib, ~/.venv-cad on the VM)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecad", "tools"))
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, ColorPolicy, BackgroundPolicy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import panel1450 as L

dxf_fn, out_fn = sys.argv[1], sys.argv[2]
doc = ezdxf.readfile(dxf_fn); msp = doc.modelspace()
W, H = L.PLATE[0], L.PLATE[1]
with PdfPages(out_fn) as pdf:
    # --- sheet 1: the plate at 1:2 with dimensions
    fig = plt.figure(figsize=(16.54, 11.69), dpi=100)              # A3 landscape
    ax = fig.add_axes([0.01, 0.09, 0.59, 0.86])
    ctx = RenderContext(doc); Frontend(ctx, MatplotlibBackend(ax), config=Configuration(color_policy=ColorPolicy.BLACK, background_policy=BackgroundPolicy.WHITE)).draw_layout(msp, finalize=True)
    ax.set_xlim(-W / 2 - 30, W / 2 + 30); ax.set_ylim(-H / 2 - 30, H / 2 + 30); ax.set_aspect("equal"); ax.axis("off")
    def dim(x0, y0, x1, y1, text, off=0.0, vertical=False):
        if vertical:
            ax.annotate("", xy=(x0 + off, y0), xytext=(x0 + off, y1), arrowprops=dict(arrowstyle="<->", lw=0.6)); ax.text(x0 + off + 2, (y0 + y1) / 2, text, fontsize=7, rotation=90, va="center")
            ax.plot([x0, x0 + off + 3], [y0, y0], lw=0.3, color="k"); ax.plot([x0, x0 + off + 3], [y1, y1], lw=0.3, color="k")
        else:
            ax.annotate("", xy=(x0, y0 + off), xytext=(x1, y0 + off), arrowprops=dict(arrowstyle="<->", lw=0.6)); ax.text((x0 + x1) / 2, y0 + off + 2, text, fontsize=7, ha="center")
            ax.plot([x0, x0], [y0, y0 + off + 3], lw=0.3, color="k"); ax.plot([x1, x1], [y0, y0 + off + 3], lw=0.3, color="k")
    dim(-W / 2, H / 2, W / 2, H / 2, "%.1f" % W, off=14); dim(W / 2, -H / 2, W / 2, H / 2, "%.1f" % H, off=14, vertical=True)
    dim(-L.WINDOW[0] / 2, -H / 2, L.WINDOW[0] / 2, -H / 2, "window %.2f (frame ring)" % L.WINDOW[0], off=-14)
    dim(-W / 2, -L.WINDOW[1] / 2, -W / 2, L.WINDOW[1] / 2, "window %.2f" % L.WINDOW[1], off=-14, vertical=True)
    dx, dy = L.DISPLAY["c"]; aw, ah = L.DISPLAY["aperture"]
    dim(dx - aw / 2, dy - ah / 2, dx + aw / 2, dy - ah / 2, "aperture %.2f" % aw, off=-6); dim(dx + aw / 2, dy - ah / 2, dx + aw / 2, dy + ah / 2, "%.2f" % ah, off=6, vertical=True)
    ex, ey = L.EPAPER["c"]; ww, wh = L.EPAPER["window"]
    dim(ex - ww / 2, ey + wh / 2, ex + ww / 2, ey + wh / 2, "e-paper window %.2f x %.1f" % (ww, wh), off=6)
    for ref, (x, y), hole, depth in L.BUTTONS: ax.text(x + hole / 2 + 3, y, "%s\nd%.1f" % (ref, hole), fontsize=5.5, va="center")
    for ref, (x, y) in L.TOGGLES: ax.text(x - 22, y, "%s\nd%.1f + key" % (ref, L.TOGGLE_HOLE), fontsize=5.5, va="center")
    ax.text(L.LIGHT[1][0] - 22, L.LIGHT[1][1], "%s\nD %.1f/%.1f" % (L.LIGHT[0], L.LIGHT_HOLE, L.LIGHT_FLAT), fontsize=5.5, va="center")
    ax.text(L.SOUNDER[1][0], L.SOUNDER[1][1] - L.SOUNDER[2] / 2 - 4, "%s d%.1f" % (L.SOUNDER[0], L.SOUNDER[2]), fontsize=5.5, ha="center", va="top")
    ax.text(L.STATUS_LEDS[0][1][0], L.STATUS_LEDS[-1][1][1] - 8, "D1..D11 d%.1f H7\n9 mm pitch" % L.LED_HOLE, fontsize=5.5, ha="center", va="top")
    ax.text(L.BAR_LEDS[2][1][0], L.BAR_LEDS[0][1][1] - 8, "D12..D16 d%.1f H7, 6 mm pitch" % L.LED_HOLE, fontsize=5.5, ha="center", va="top")
    for k, (x, y) in enumerate(L.FRAME_BOSSES): ax.text(x, y + 4, "M3", fontsize=5, ha="center")
    for k, (x, y) in enumerate(L.STANDOFFS): ax.text(x + (4 if k < 4 else 0), y + (0 if k < 4 else 5), "SO-M3 H%d" % (k + 1) if k < 4 else "H%d" % (k + 1), fontsize=5, va="center" if k < 4 else "bottom", ha="left" if k < 4 else "center")
    ax.text(0, 0, "+", fontsize=9, ha="center", va="center"); ax.text(0, H / 2 + 24, "the cross marks the case frame origin: X along the case, +Y toward the hinge wall; the plate is symmetric on both axes", fontsize=5.5, ha="center", va="bottom")
    ax.plot([-W / 2 - 25, -W / 2 - 25 + 50], [-H / 2 - 25, -H / 2 - 25], lw=2, color="k"); ax.text(-W / 2 - 25 + 25, -H / 2 - 22, "50 mm", fontsize=7, ha="center")
    # the table
    tx = fig.add_axes([0.61, 0.07, 0.38, 0.91]); tx.axis("off")
    rows = [("Plate", "%.1f x %.1f x %.1f, R%.0f corners, 5754 or 6061, black anodised" % (W, H, L.PLATE[2], L.PLATE_R)),
            ("Frame screws", "10 x M3 clearance 3.4 at the 1450PF inserts"),
            ("Display", "Touch Display 2: aperture %.2f x %.2f R%.1f at (%.0f, %.0f); 1.0 pocket %.2f x %.2f from below for the glass and its tape frame" % (aw, ah, L.DISPLAY["aperture_r"], dx, dy, L.DISPLAY["glass"][0], L.DISPLAY["glass"][1])),
            ("E-paper", "WeAct 3.7: window %.2f x %.1f at (%.0f, %.0f); 1.0 pocket %.2f x %.1f R%.0f from above for the 2 mm lens" % (ww, wh, ex, ey, L.EPAPER["lens"][0], L.EPAPER["lens"][1], L.EPAPER["lens_r"])),
            ("Buttons", "; ".join("%s d%.1f at (%.0f, %.0f)" % (r, h, c[0], c[1]) for r, c, h, d in L.BUTTONS) + " (C&K ATP19/ATP16, silicone washer under the bezel)"),
            ("Toggles", "; ".join("%s at (%.0f, %.0f)" % (r, c[0], c[1]) for r, c in L.TOGGLES) + ": d%.1f with the %.2f x %.2f keyway toward -Y (APEM 5636ADKB-2V, K seal)" % (L.TOGGLE_HOLE, L.TOGGLE_KEY[0], L.TOGGLE_KEY[1])),
            ("Light switch", "%s at (%.0f, %.0f): D hole %.1f with the %.1f flat toward +X (NKK M2044SD3A01, O-ring and AT401A boot)" % (L.LIGHT[0], L.LIGHT[1][0], L.LIGHT[1][1], L.LIGHT_HOLE, L.LIGHT_FLAT)),
            ("Sounder", "%s d%.1f at (%.0f, %.0f) (Floyd Bell MC-09-530-Q, 61663 gasket)" % (L.SOUNDER[0], L.SOUNDER[2], L.SOUNDER[1][0], L.SOUNDER[1][1])),
            ("Light guides", "16 x d%.1f H7 reamed: Mentor 1282.5004 IP68 (2.5 shaft, 3.2 head, A 7.5) over the 3 mm LEDs of the backer C6" % L.LED_HOLE),
            ("Standoffs", "6 x PEM SO-M3-10 self-clinching from below at " + ", ".join("(%.0f, %.0f)" % c for c in L.STANDOFFS) + "; hole 4.2"),
            ("Marking", "laser: legends, the battery bar, the nameplate %.0f x %.0f at (%.0f, %.0f), the logo d%.0f at (%.0f, %.0f) (face-plate-marking.svg)" % (L.NAMEPLATE[2], L.NAMEPLATE[3], L.NAMEPLATE[0], L.NAMEPLATE[1], L.LOGO[1], L.LOGO[0][0], L.LOGO[0][1])),
            ("Seal", "PORON gasket ring in the %.0f mm band under the frame ring; every cut-out sealed by its part (32.34 construction, 32.42)" % L.BAND)]
    import textwrap
    fig.canvas.draw(); rend = fig.canvas.get_renderer(); inv = tx.transAxes.inverted()
    def height(t):
        bb = t.get_window_extent(renderer=rend); lo = inv.transform((bb.x0, bb.y0)); hi = inv.transform((bb.x1, bb.y1)); return hi[1] - lo[1]
    y = 0.99
    for k, (a, b) in enumerate(rows):
        t1 = tx.text(0.0, y, a, fontsize=7.0, fontweight="bold", va="top", transform=tx.transAxes); y -= height(t1) + 0.003
        t2 = tx.text(0.0, y, "\n".join(textwrap.wrap(b, 56)), fontsize=6.0, va="top", linespacing=1.15, transform=tx.transAxes); y -= height(t2) + 0.008
    fig.text(0.02, 0.012, "MeshSat field kit V2, Peli 1450 face plate, Rev A, 5 Sep 2026, scale 1:2 on A3, all mm. Prototype drawing generated by v2/cad/plate_drawing.py from face-plate.dxf (layers OUTLINE, THROUGH, POCKET_1MM, STANDOFF_M3). Nothing built.", fontsize=7)
    pdf.savefig(fig); plt.close(fig)
print("PLATE-DRAWING-DONE", out_fn)
