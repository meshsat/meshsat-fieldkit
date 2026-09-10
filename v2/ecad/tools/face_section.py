#!/usr/bin/env python3
"""A Y-Z section through the face at the display, drawn from panel1450.py (9 September 2026, appendix 32.85).
One-off: run when the face changed, and the section it drew is in appendix 32.85. Kept because the record cites it.

The owner's ruling 14.6 is about a surface the eye can check: the glass level with the aluminium. A pass/fail line in a
log cannot be checked by eye, and a full render needs a rented GPU box, so this draws the section: the plate, the monitor
in its window, the e-paper lens in its pocket, the backer ring, B16 and the CM5 stack, all at true scale in Z and Y.

Usage: face_section.py [out.png]   (default v2/images/face-section.png)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import panel1450 as L

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "images", "face-section.png")
X = L.XENARC
gy = X["c"][1]; bh = X["body"][1]
FACE, UNDER = L.FACE_TOP_Z, L.PLATE_UNDER_Z
fig, ax = plt.subplots(figsize=(15.5, 5.2))


def band(y0, z0, dy, dz, colour, label=None, edge="black", z=2, alpha=1.0):
    ax.add_patch(Rectangle((y0, z0), dy, dz, facecolor=colour, edgecolor=edge, linewidth=0.7, zorder=z, alpha=alpha))
    if label:
        ax.text(y0 + dy / 2, z0 + dz / 2, label, ha="center", va="center", fontsize=7, zorder=z + 1)


# the plate, in two pieces because the monitor's window goes right through it
win_s, win_n = gy - X["window"][1] / 2, gy + X["window"][1] / 2
band(-L.PLATE[1] / 2, UNDER, win_s + L.PLATE[1] / 2, L.PLATE[2], "#b9bec4", "3 mm aluminium plate")
band(win_n, UNDER, L.PLATE[1] / 2 - win_n, L.PLATE[2], "#b9bec4", "plate")

# the monitor: bezel flange inside the plate's thickness, rear shell below, glass AT the face
band(gy - bh / 2, FACE - X["bezel_depth"], bh, X["bezel_depth"], "#3a3a3e", "Xenarc bezel flange %.2f" % X["bezel_depth"])
band(gy - bh / 2 + 7, FACE - X["height"], bh - 14, X["shell_depth"], "#2a2a2e", "rear shell %.2f" % X["shell_depth"])
ax.plot([gy - X["glass"][1] / 2, gy + X["glass"][1] / 2], [FACE, FACE], color="#19c1ff", linewidth=3.2, zorder=6)
ax.text(gy, FACE + 2.0, "GLASS SURFACE, level with the plate (0.00 mm proud)", ha="center", fontsize=8.5, color="#0072a3", zorder=7)

# the e-paper: 1.0 mm lens on 0.05 tape in the 1.0 mm pocket
ey = L.EPAPER["c"][1]; lh = L.EPAPER["lens"][1]
band(ey - lh / 2, FACE - L.EPAPER["pocket_depth"] + L.EPAPER["tape_t"], lh, L.EPAPER["lens_t"], "#cfe8ff", None, z=5)
ax.text(ey, FACE + 2.0, "e-paper lens, %.2f mm proud" % (L.EPAPER["lens_t"] + L.EPAPER["tape_t"] - L.EPAPER["pocket_depth"]), ha="center", fontsize=8, color="#0072a3")

# the backer ring, notched where the body passes
n = L.BLOCK_NOTCH
btop = UNDER - L.BACKER_GAP
band(-114.0, btop - L.BACKER_T, n[1] + 114.0, L.BACKER_T, "#1d6b34", "backer C7", z=3)
band(88.0, btop - L.BACKER_T, 26.0, L.BACKER_T, "#1d6b34", "C7", z=3)

# B16 and the CM5 stack
band(-100.0, L.B_TOP_Z - 1.6, 200.0, 1.6, "#1d6b34", "B16", z=1)
for rect, h, name in L.B16_TALL:
    if "CM5" not in name:
        continue
    if rect[0] > 0:
        continue          # one representative column, slot 1
    band(rect[1], L.B_TOP_Z, rect[3] - rect[1], h, "#8a8f95" if "heatsink" in name else "#55585c",
         "heatsink %.0f" % h if "heatsink" in name else "fan", z=4 if "heatsink" in name else 5, alpha=0.95)

# the PA flange, now north of the monitor
pa = L.PA_MOUNT
band(pa["c"][1] - pa["size"][1] / 2, UNDER - pa["height"], pa["size"][1], pa["height"], "#c08a2e", "PA", z=6)

ax.annotate("", xy=(gy, FACE), xytext=(gy, FACE - X["height"]), arrowprops=dict(arrowstyle="<->", color="#c02020", lw=1.1))
ax.text(gy + 3, FACE - X["height"] / 2, "28.66 into the void", fontsize=7.5, color="#c02020")
worst = min((L.B_TOP_Z + h for r, h, nm in L.B16_TALL if "heatsink" in nm), default=0)
ax.plot([-102, 102], [worst, worst], color="#c02020", linestyle=":", linewidth=0.9)
ax.text(-100, worst - 3.0, "CM5 heatsinks top %.2f, monitor bottom %.2f, margin %.2f mm" % (worst, FACE - X["height"], FACE - X["height"] - worst), fontsize=7.5, color="#c02020")

ax.set_xlim(-L.PLATE[1] / 2 - 5, L.PLATE[1] / 2 + 5); ax.set_ylim(L.B_TOP_Z - 8, FACE + 10)
ax.set_xlabel("case Y (mm), south at the left"); ax.set_ylabel("Z above the cavity floor (mm)")
ax.set_title("MeshSat V2 face, section through the display: the glass sits at the plate's top face (Z %.1f). Prototype design, nothing built." % FACE, fontsize=10)
ax.set_aspect("equal"); ax.grid(alpha=0.25, linewidth=0.4)
fig.tight_layout(); fig.savefig(out, dpi=150)
print("saved", os.path.normpath(out))
