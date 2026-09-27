#!/usr/bin/env python3
"""Differential impedance of the candidate layer uses for board B, solved with atlc (MESHSAT-1357, 27 September 2026).

WHAT THIS IS. A desk solve that feeds v2/docs/STACKUP-DECISIONS.md. It decides nothing: it gives the pair widths each
candidate layer use of board B would need, so the choice between six layers re-assigned (B-FEASIBILITY.md option A2)
and eight layers (decision 43, JLC08161H-2116) can be taken on numbers. It is EXPERIMENTAL evidence in the sense of
the owner's condition 7: it authorises no layout. The fabricator's own impedance calculation and coupon govern at
order (IMP-001); these are the second opinion the record asks for before that.

WHY NOT impedance_2d.py AS IT STANDS. `v2/ecad/tools/impedance_2d.py` draws ONE dielectric constant for the whole
cross-section. The inner layers these candidates use sit between a core and a prepreg with different constants
(JLC06161H-3313: core 4.6 above In2, 2116 prepreg 4.16 below it; JLC08161H-2116: 0.3 mm core 4.41 and 2 x 1080
prepreg 3.91), so this driver draws the two dielectrics in two colours and passes each its own constant. Everything
else follows impedance_2d.py's convention and colour code (atlc's own: red the P leg at +1 V, blue the N leg at -1 V,
green the grounded planes, white air), its 200 px/mm, its cut-off 0.01, its domain margins, and its outer-layer
solder mask of 0.01 mm at er 3.5. Zdiff = 2 x Zodd, read from atlc's output.

GEOMETRY CONVENTION, the same as impedance_2d.py: plane, h_below, trace of thickness t, h_above, plane. The listed
dielectric thicknesses are the fabricator's layer table (v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md and
jlcpcb-impedance-stackups-2026-09-16.md, transcribed in v2/ecad/tools/stackup_write.py STACKS). A copper layer
between the trace and a plane that carries signals is NOT drawn (no copper assumed there), which is the pessimistic
reading for a layer that is mostly clear and optimistic nowhere that matters for the choice made from it.

CALIBRATION CASES (printed first, so every run shows whether this driver reproduces the tree's recorded solves):
  6L 3313 outer 0.127/0.127, h 0.0994, er 4.1, masked: recorded 90.7 (memory reference and impedance_2d CASES)
  6L 3313 inner 0.127/0.127, symmetric h 0.6057, er 4.45: recorded 102.0

Usage (on a host with atlc 4.6.1 and Pillow; the runner has no atlc, and a solver run does not belong on it):
  stack_solves.py [--ppmm 200] [--jobs 8]      prints every case and the interpolated widths
"""
import os, re, sys, shutil, subprocess, tempfile
from concurrent.futures import ProcessPoolExecutor

LIVE, GND, NEG, WHITE = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)
D_BELOW, D_ABOVE, MASK = (192, 192, 192), (200, 200, 200), (160, 160, 160)
CUTOFF = "0.01"
T_OUT, T_IN = 0.035, 0.0152          # finished copper, 1 oz outer and 0.5 oz inner (the STACKS rows)


def solve(w, s, t, h_below, er_below, h_above=None, er_above=None, ppmm=200, mask=0.0, mask_er=3.5):
    """Zdiff for a pair. h_above None = microstrip (air above, optional mask); otherwise an asymmetric stripline."""
    from PIL import Image
    pair = 2 * w + (s if s is not None else -w)
    hmax = max(h_below, h_above or 0.0)
    margin = max(10.0 * hmax, 3.0 * pair)
    W = pair + 2 * margin
    plane_t = 0.035
    if h_above is None:
        H = plane_t + h_below + t + mask + max(1.0, 10 * h_below)
    else:
        H = plane_t + h_below + t + h_above + plane_t
    nx, ny = int(round(W * ppmm)), int(round(H * ppmm))
    im = Image.new("RGB", (nx, ny), WHITE); px = im.load()

    def box(x0, y0, x1, y1, col):
        i0, i1 = max(0, int(round(x0 * ppmm))), min(nx, int(round(x1 * ppmm)))
        j0, j1 = max(0, int(round(y0 * ppmm))), min(ny, int(round(y1 * ppmm)))
        for j in range(j0, j1):
            yy = ny - 1 - j
            for i in range(i0, i1):
                px[i, yy] = col

    y = 0.0
    box(0, y, W, y + plane_t, GND); y += plane_t
    box(0, y, W, y + h_below, D_BELOW)
    yt = y + h_below
    x0 = margin
    if h_above is None:
        if mask > 0:
            box(0, yt, W, yt + t + mask, MASK)
    else:
        box(0, yt, W, yt + t + h_above, D_ABOVE)      # the trace sits in the upper dielectric's side, as impedance_2d does
        box(0, yt + t + h_above, W, yt + t + h_above + plane_t, GND)
    box(x0, yt, x0 + w, yt + t, LIVE)
    if s is not None:
        box(x0 + w + s, yt, x0 + 2 * w + s, yt + t, NEG)
    d = tempfile.mkdtemp(prefix="atlc-hc9-")
    bmp = os.path.join(d, "xsec.bmp"); im.save(bmp)
    args = ["atlc", "-S", "-s", "-c", CUTOFF, "-d", "c0c0c0=%s" % er_below, "-d", "a0a0a0=%s" % mask_er]
    if h_above is not None:
        args += ["-d", "c8c8c8=%s" % (er_above if er_above is not None else er_below)]
    try:
        out = subprocess.run(args + [bmp], capture_output=True, text=True).stdout
    finally:
        shutil.rmtree(d, ignore_errors=True)          # atlc writes its field files beside the bitmap; nothing is kept
    got = {m.group(1): float(m.group(2)) for m in re.finditer(r"(Z\w+|Er_\w+)=\s*([-\d.eE+]+)", out)}
    if s is None:                                     # a single conductor: atlc prints Zo
        if "Zo" not in got:
            raise SystemExit("atlc gave no Zo:\n" + out[:600])
        return got["Zo"]
    if "Zodd" not in got:
        raise SystemExit("atlc gave no Zodd:\n" + out[:600])
    return got.get("Zdiff", 2 * got["Zodd"])


# (key, label, t, h_below, er_below, h_above, er_above, mask)
GEOMS = [
    ("cal-out", "CAL 6L 3313 outer, h 0.0994 er 4.1, masked", T_OUT, 0.0994, 4.1, None, None, 0.01),
    ("cal-in",  "CAL 6L 3313 inner, symmetric h 0.6057 er 4.45", T_IN, 0.6057, 4.45, 0.6057, 4.45, 0.0),
    ("6L-out",  "6L JLC06161H-3313 outer (F over In1 / B over In4): microstrip h 0.0994 er 4.1, masked", T_OUT, 0.0994, 4.1, None, None, 0.01),
    ("6L-in-asis", "6L 3313 In2 as B21 uses it: In1 GND 0.55 core er 4.6 above, In4 split 5 V planes 0.674 below (In3 routing, not drawn), er 4.16 below",
     T_IN, 0.674, 4.16, 0.55, 4.6, 0.0),
    ("6L-A2-In2", "6L 3313 option A2, In2 between In3 GND (0.1088 2116 er 4.16) and In1 GND (0.55 core er 4.6)", T_IN, 0.1088, 4.16, 0.55, 4.6, 0.0),
    ("8L-out",  "8L JLC08161H-2116 outer (F over In1 / B over In6): microstrip h 0.1164 er 4.16, masked", T_OUT, 0.1164, 4.16, None, None, 0.01),
    ("8L-in",   "8L JLC08161H-2116 inner signal layer between a plane across 0.1528 (2 x 1080, er 3.91) and a plane across 0.3 (core, er 4.41)",
     T_IN, 0.1528, 3.91, 0.3, 4.41, 0.0),
]
# single-ended 50 ohm RF lines on the outer layers (RF-001): (key, label, h, er)
SE_GEOMS = [
    ("se-4L", "4L JLC04161H-7628 outer (boards D, E): microstrip h 0.2104 er 4.4, masked", 0.2104, 4.4),
    ("se-6L", "6L JLC06161H-3313 outer (boards A, B, C): microstrip h 0.0994 er 4.1, masked", 0.0994, 4.1),
    ("se-8L", "8L JLC08161H-2116 outer (board B candidate): microstrip h 0.1164 er 4.16, masked", 0.1164, 4.16),
]
SE_WIDTHS = [0.12, 0.14, 0.16, 0.18, 0.20, 0.24, 0.30, 0.35, 0.40]
WIDTHS = {"out": [0.09, 0.10, 0.11, 0.127, 0.15, 0.18, 0.20], "in": [0.075, 0.09, 0.10, 0.11, 0.127, 0.15, 0.18, 0.21]}
GAPS = [0.127, 0.152, 0.20]
TARGETS = [85.0, 90.0, 100.0]


def run(job):
    key, label, t, hb, eb, ha, ea, mask, w, s, ppmm = job
    return key, w, s, solve(w, s, t, hb, eb, ha, ea, ppmm=ppmm, mask=mask)


def interp_width(rows, target):
    """rows: [(w, z)] sorted by w with z falling as w grows; the width that gives target, by linear interpolation."""
    for (w0, z0), (w1, z1) in zip(rows, rows[1:]):
        if (z0 - target) * (z1 - target) <= 0 and z0 != z1:
            return w0 + (target - z0) * (w1 - w0) / (z1 - z0)
    return None


def main(a):
    ppmm = int(a[a.index("--ppmm") + 1]) if "--ppmm" in a else 200
    jobs_n = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 8
    jobs = []
    for key, label, t, hb, eb, ha, ea, mask in GEOMS:
        if key.startswith("cal"):
            jobs.append((key, label, t, hb, eb, ha, ea, mask, 0.127, 0.127, ppmm))
            continue
        ws = WIDTHS["out" if ha is None else "in"]
        for s in GAPS:
            for w in ws:
                jobs.append((key, label, t, hb, eb, ha, ea, mask, w, s, ppmm))
    for key, label, h, er in SE_GEOMS:
        for w in SE_WIDTHS:
            jobs.append((key, label, T_OUT, h, er, None, None, 0.01, w, None, ppmm))
    with ProcessPoolExecutor(max_workers=jobs_n) as ex:
        res = list(ex.map(run, jobs))
    z = {}
    for key, w, s, zd in res:
        z[(key, w, s)] = zd
    print("stack_solves: atlc at %d px/mm, cut-off %s; Zdiff in ohm" % (ppmm, CUTOFF))
    for key, label, *_ in GEOMS:
        print()
        print("## %s: %s" % (key, label))
        if key.startswith("cal"):
            rec = {"cal-out": 90.7, "cal-in": 102.0}[key]
            print("   0.127/0.127 -> %.1f (recorded %.1f, difference %+.1f)" % (z[(key, 0.127, 0.127)], rec, z[(key, 0.127, 0.127)] - rec))
            continue
        ha = [g for g in GEOMS if g[0] == key][0][5]
        ws = WIDTHS["out" if ha is None else "in"]
        print("   w \\ s   " + "  ".join("%7.3f" % s for s in GAPS))
        for w in ws:
            print("   %.3f   " % w + "  ".join("%7.1f" % z[(key, w, s)] for s in GAPS))
        for s in GAPS:
            rows = sorted((w, z[(key, w, s)]) for w in ws)
            parts = []
            for tg in TARGETS:
                wt = interp_width(rows, tg)
                parts.append("%.0f ohm: %s" % (tg, ("w %.3f" % wt) if wt else "outside the solved widths"))
            print("   gap %.3f -> %s" % (s, "; ".join(parts)))
    for key, label, h, er in SE_GEOMS:
        print()
        print("## %s: %s" % (key, label))
        rows = sorted((w, z[(key, w, None)]) for w in SE_WIDTHS)
        print("   " + "  ".join("w %.2f: %.1f" % r for r in rows))
        wt = interp_width(rows, 50.0)
        print("   50 ohm single-ended -> %s" % (("w %.3f" % wt) if wt else "outside the solved widths"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
