"""Shared sheet furniture for the MeshSat V2 case drawings (MESHSAT-1357, 27 Sep 2026): A3 sheets, a title block that names the source revision
and the sha256 of every input the sheet was drawn from, the tolerance statement, and the box of margin rows (MET or OPEN) read from
v2/vendor/peli/1450/frame_seat.out, so a drawing never states a verdict of its own. Used by case_drawings.py and plate_drawing.py.
matplotlib only (v2/cad/requirements-cad.txt)."""
import os, re, math, hashlib, datetime, subprocess, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon, Arc

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(V2, ".."))
FRAME_SEAT_OUT = os.path.join(V2, "vendor", "peli", "1450", "frame_seat.out")
A3 = (16.54, 11.69)
BASE_COMMIT = os.environ.get("CASE_BASE_COMMIT", "")

GENERAL_TOLERANCES = [
    "Dimensions in mm. Kit parts (this sheet): machined positions and outlines +-0.10; the 3.0 face plate +-0.13 and the 6.0 entry plates +-0.20 (EN 485-4 class, "
    "standard not held, INFERRED); the setting leg's pad height +-0.10; rebate depth and line +-0.10; spot-face floors +-0.10.",
    "Peli: the 1450PF sheet 1453-314-000 rev A states +-0.76 on one-decimal and +-0.25 on two-decimal mm (VERIFIED); drawing 1451-931 states no tolerance "
    "(\"typical industry-standard tolerances apply\"), so every case allowance is the session's (INFERRED, UNSTATED).",
    "Design basis only (v2/docs/CASE-MARGINS.md section 1, Verdicts): a MET row still meets its minimum with every unstated allowance taken twice, a "
    "sensitivity reading and not a bound on those allowances; an OPEN row rests on something no held source gives. Nominal CAD establishes no fit, seal "
    "or alignment; checks T1 to T11 (CASE-MARGINS.md section 5) do. Prototype: nothing on this sheet has been made, bought or fitted.",
]


def sha12(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]
    except OSError:
        return "absent"


def base_commit():
    if BASE_COMMIT: return BASE_COMMIT
    try:
        return subprocess.check_output(["git", "-C", REPO, "rev-parse", "--short=8", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def rows():
    """frame_seat.out's table: key -> dict(min, nom, worst, rss, wc2, verdict, label)."""
    out = {}
    pat = re.compile(r"^  (M\w+)\s+(.+?)\s+(\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+([+-]\d+\.\d\d)\s+(OPEN, FAILS AS ASSUMED|NOT MET|OPEN|MET)")
    for line in open(FRAME_SEAT_OUT, encoding="utf-8"):
        m = pat.match(line.rstrip("\n"))
        if m:
            k = m.group(1)
            out[k] = dict(label=m.group(2).strip(), min=float(m.group(3)), nom=float(m.group(4)), worst=float(m.group(5)), rss=float(m.group(6)),
                          wc2=float(m.group(7)), verdict=m.group(8))
    # M8 is printed as M8x and M8y; M20 and M9 are statements judged in CASE-MARGINS.md 3.2
    out.setdefault("M20", dict(label="the frame's seat on the setting legs (a statement)", min=0, nom=86.00, worst=84.38, rss=0, wc2=0, verdict="OPEN"))
    return out


def sheet(title, number, of, inputs, part=None):
    """A new A3 landscape figure with the title block. inputs: list of repo-relative paths whose sha256 the block prints."""
    fig = plt.figure(figsize=A3, dpi=100)
    fig.patch.set_facecolor("white")
    # border and title block
    fig.add_artist(Rectangle((0.008, 0.008), 0.984, 0.984, transform=fig.transFigure, fill=False, lw=1.0, color="k"))
    tb = fig.add_axes([0.008, 0.008, 0.984, 0.085]); tb.axis("off"); tb.set_xlim(0, 1); tb.set_ylim(0, 1)
    tb.add_patch(Rectangle((0, 0), 1, 1, fill=False, lw=1.0))
    tb.plot([0.30, 0.30], [0, 1], lw=0.6, color="k"); tb.plot([0.62, 0.62], [0, 1], lw=0.6, color="k"); tb.plot([0.86, 0.86], [0, 1], lw=0.6, color="k")
    tb.text(0.005, 0.92, "MeshSat field kit V2, Peli 1450 case set", fontsize=7.5, fontweight="bold", va="top")
    tb.text(0.005, 0.60, "\n".join(textwrap.wrap(title, 64)), fontsize=8.6, fontweight="bold", va="top", linespacing=1.05)
    tb.text(0.005, 0.04, "MESHSAT-1357. PROTOTYPE DESIGN: nothing made, bought or fitted.\nSession choices under the owner's standing rule of 26 Sep 2026 (SC-07).", fontsize=5.6, va="bottom")
    src = ["Source: tree %s plus the case release's changes (fnd/hc7); inputs by sha256 (first 12):" % base_commit()]
    for p in inputs:
        src.append("  %s  %s" % (sha12(os.path.join(REPO, p)), p))
    tb.text(0.305, 0.95, "\n".join(src[:7]), fontsize=5.6, va="top", family="monospace")
    tb.text(0.625, 0.95, "\n".join(textwrap.wrap("Generated %s by v2/cad/%s from the files named left; regenerate with v2/cad/README.md. The editable sources govern; this sheet is a copy." % (
        datetime.date.today().isoformat(), part or "case_drawings.py"), 62)), fontsize=6, va="top")
    tb.text(0.865, 0.80, "Sheet %d of %d" % (number, of), fontsize=10, fontweight="bold", va="top")
    tb.text(0.865, 0.45, "A3, mm\nnot to scale for measurement:\ndimensions govern; use the\n1:1 templates for marking", fontsize=6.3, va="top")
    return fig


TOL_RECT = [0.53, 0.098, 0.455, 0.175]
ROWS_RECT = [0.015, 0.098, 0.505, 0.175]


def tolerance_box(fig, rect=None, extra=(), wrap=None, fs=5.4):
    rect = rect or TOL_RECT
    ax = fig.add_axes(rect); ax.axis("off")
    wrap = wrap or int(rect[2] * 16.54 * 72 / (fs * 0.62))
    txt = []
    for t in list(GENERAL_TOLERANCES) + list(extra):
        txt += textwrap.wrap(t, wrap)
    ax.text(0, 1, "TOLERANCES AND STATUS\n" + "\n".join(txt), fontsize=fs, va="top", family="sans-serif", linespacing=1.12)
    return ax


def rows_box(fig, rect, keys, heading="Margin rows this sheet's features enter (frame_seat.out): key, verdict, min, nominal, worst, worst with unstated x2", ncols=1, fs=5.2, width=None):
    """The rows (MET or OPEN) of v2/vendor/peli/1450/frame_seat.out that the sheet's features enter; OPEN ones in red. ncols splits a long list."""
    R = rows(); rect = rect or ROWS_RECT
    per = int(math.ceil(len(keys) / float(ncols)))
    width = width or int((rect[2] / ncols) * 16.54 * 72 / (fs * 0.60)) - 2
    for c in range(ncols):
        ax = fig.add_axes([rect[0] + c * rect[2] / ncols, rect[1], rect[2] / ncols, rect[3]]); ax.axis("off")
        if c == 0: ax.text(0, 1, heading, fontsize=fs, va="top", fontweight="bold")
        dy = fs * 1.32 / (rect[3] * 11.69 * 72.0)
        y = 1.0 - 1.4 * dy
        for k in keys[c * per:(c + 1) * per]:
            r = R.get(k)
            if k == "M20":
                line, col = "M20   OPEN                    the frame's seat: bottom Z 86.00 nominal, 84.38..87.62 on the legs (T2)", "#b00020"
            elif r is None:
                line, col = "%-5s (not in frame_seat.out)" % k, "k"
            else:
                line = "%-5s %-22s %5.2f %+7.2f %+7.2f %+7.2f  %s" % (k, r["verdict"], r["min"], r["nom"], r["worst"], r["wc2"], r["label"])
                col = "#b00020" if r["verdict"].startswith("OPEN") or r["verdict"] == "NOT MET" else "#1b5e20"
            ax.text(0, y, line[:width], fontsize=fs, va="top", family="monospace", color=col)
            y -= dy
    return None


def dim_h(ax, x0, x1, y, text, off=0.0, fs=6.5, ext=True, color="k"):
    ax.annotate("", xy=(x0, y + off), xytext=(x1, y + off), arrowprops=dict(arrowstyle="<->", lw=0.5, color=color, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + off, text, fontsize=fs, ha="center", va="bottom", color=color, bbox=dict(fc="white", ec="none", pad=0.3))
    if ext:
        ax.plot([x0, x0], [y, y + off], lw=0.3, color=color); ax.plot([x1, x1], [y, y + off], lw=0.3, color=color)


def dim_v(ax, x, y0, y1, text, off=0.0, fs=6.5, ext=True, color="k"):
    ax.annotate("", xy=(x + off, y0), xytext=(x + off, y1), arrowprops=dict(arrowstyle="<->", lw=0.5, color=color, shrinkA=0, shrinkB=0))
    ax.text(x + off, (y0 + y1) / 2, text, fontsize=fs, ha="center", va="center", rotation=90, color=color, bbox=dict(fc="white", ec="none", pad=0.3))
    if ext:
        ax.plot([x, x + off], [y0, y0], lw=0.3, color=color); ax.plot([x, x + off], [y1, y1], lw=0.3, color=color)


def tag(ax, x, y, text, color="#b00020", fs=6.0, dx=0.0, dy=0.0, ha="left"):
    """An OPEN-row label on a feature: a small leader and the row key(s) with the verdict, in red."""
    if dx or dy:
        ax.annotate(text, xy=(x, y), xytext=(x + dx, y + dy), fontsize=fs, color=color, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.4, color=color), bbox=dict(fc="white", ec=color, lw=0.4, pad=0.8))
    else:
        ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va="center", bbox=dict(fc="white", ec=color, lw=0.4, pad=0.8))


def rrect_pts(cx, cy, w, h, r, n=8):
    pts = []
    for (ax_, ay_, a0) in ((cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)):
        for k in range(n + 1):
            a = __import__("math").radians(a0 + 90.0 * k / n); pts.append((ax_ + r * __import__("math").cos(a), ay_ + r * __import__("math").sin(a)))
    return pts


def scale_bar(ax, x, y, length=50.0, fs=6):
    ax.plot([x, x + length], [y, y], lw=2, color="k"); ax.plot([x, x], [y - 1.5, y + 1.5], lw=0.8, color="k"); ax.plot([x + length, x + length], [y - 1.5, y + 1.5], lw=0.8, color="k")
    ax.text(x + length / 2, y + 2, "%.0f mm" % length, fontsize=fs, ha="center", va="bottom")
