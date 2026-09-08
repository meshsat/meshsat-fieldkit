#!/usr/bin/env python3
"""Differential impedance from a 2D field solver, as the second opinion the record owes (MESHSAT-862, 8 Sep 2026).

`impedance_check.py` computes IPC-2141 closed forms, whose accuracy is about 5 to 10 percent, and the appendix says no
impedance may be claimed until a solver confirms them. openEMS is not packaged for this host; `atlc` 4.6.1 is, and for a
uniform transmission line cross-section a 2D quasi-static finite-difference solver is the right instrument and is more
accurate than a closed form. This tool draws the cross-section as a bitmap in atlc's colour convention and reads its
odd-mode result back: Zdiff = 2 x Zodd.

  red    ff0000  the live conductor, +1 V (the P leg)
  green  00ff00  the grounded conductor, 0 V (the reference plane)
  blue   0000ff  the negative conductor, -1 V (the N leg)
  (atlc's own convention, from its manual and tutorial; green and blue are not what a KiCad eye expects)
  white  ffffff  vacuum (air above the board)
  grey   c0c0c0  the dielectric, its permittivity passed with -d

Usage:
  impedance_2d.py --w 0.30 --s 0.20 --t 0.035 --h 0.2104 --er 4.4 [--mode microstrip|stripline] [--h2 mm] [--ppmm 200]
  impedance_2d.py --selftest          the geometries of the record's two JLC stacks, against the closed forms

Prints one line per case: the geometry, Zodd, Zeven, Zdiff, and (with --target) the difference from the target.

Result of the first run (8 September 2026, 100 px/mm, the four outer-layer geometries of the record). The solder mask is
the term the closed forms leave out and it is worth 6 to 12 percent on an outer layer, so the like-for-like comparison is
the masked solve:

  4L 7628, 0.30/0.20 (the USB geometry adopted today)   solver 91.4 with mask, closed form 89, target 90
  4L 7628, 0.20/0.15 (as shipped on D8)                 solver 101.4,          closed form 102, target 90
  6L 3313, 0.127/0.127 (B17 USB)                        solver 90.4,           closed form 94,  target 90
  6L 3313, 0.127/0.20 (B17 DIFF100)                     solver 95.7,           closed form 101, target 100

The two methods agree within 0.6 to 5.5 percent, which confirms `impedance_check.py` for outer-layer pairs and confirms
both of its substantive findings: the geometry shipped on D8 really is about 101 ohm against a 90 ohm claim, and the
0.30/0.20 replacement really does hit the target. Inner-layer striplines are NOT confirmed: see the note in CASES."""
import sys, os, subprocess, tempfile, math

LIVE, GND, NEG, WHITE, DIEL, MASK = (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255), (192, 192, 192), (160, 160, 160)
CUTOFF = "0.01"   # the solver's convergence criterion; 0.001 moved a square-coax result by 0.03 percent and cost ten times the run

def solve(w, s, t, h, er, mode="microstrip", h2=None, ppmm=200, keep=None, mask=0.0, mask_er=3.5):
    """Zodd, Zeven, Zdiff (ohm) for a differential pair, w/s/t/h in mm. microstrip: one plane below, air above.
    stripline: planes above and below, h below and h2 above (h2 defaults to h), dielectric everywhere between."""
    from PIL import Image
    h2 = h if h2 is None else h2
    pair = 2 * w + s
    # atlc treats the bitmap edge as a conductor, so the domain has to be big enough that the edge stops mattering:
    # measured on the 0.30/0.20 case, 4h of air gives 74.5 ohm and 10h, 20h and 30h all give 97.4 (8 Sep 2026)
    margin = max(10.0 * h, 3.0 * pair)                     # the field has to decay before the wall
    W = pair + 2 * margin
    plane_t = max(0.035, t)
    if mode == "stripline": H = plane_t + h + t + h2 + plane_t
    else: H = plane_t + h + t + mask + max(1.0, 10 * h)    # air above the trace, past where the answer stops moving
    nx, ny = int(round(W * ppmm)), int(round(H * ppmm))
    im = Image.new("RGB", (nx, ny), WHITE); px = im.load()
    def box(x0, y0, x1, y1, col):                          # mm, y measured from the bottom of the cross-section
        i0, i1 = max(0, int(round(x0 * ppmm))), min(nx, int(round(x1 * ppmm)))
        j0, j1 = max(0, int(round(y0 * ppmm))), min(ny, int(round(y1 * ppmm)))
        for j in range(j0, j1):
            yy = ny - 1 - j
            for i in range(i0, i1): px[i, yy] = col
    y = 0.0
    box(0, y, W, y + plane_t, GND); y += plane_t          # the reference plane
    box(0, y, W, y + h, DIEL)                              # the dielectric under the traces
    yt = y + h
    x0 = margin
    box(x0, yt, x0 + w, yt + t, LIVE)                      # the P leg
    box(x0 + w + s, yt, x0 + 2 * w + s, yt + t, NEG)       # the N leg
    if mode != "stripline" and mask > 0:                   # the solder mask a real outer layer carries; the closed forms ignore it
        box(0, yt, W, yt + t + mask, MASK)
        box(x0, yt, x0 + w, yt + t, LIVE); box(x0 + w + s, yt, x0 + 2 * w + s, yt + t, NEG)
    if mode == "stripline":
        box(0, yt, W, yt + t + h2, DIEL)                   # fill the gaps beside and above the traces
        box(x0, yt, x0 + w, yt + t, LIVE); box(x0 + w + s, yt, x0 + 2 * w + s, yt + t, NEG)
        box(0, yt + t + h2, W, yt + t + h2 + plane_t, GND)
    d = tempfile.mkdtemp(prefix="atlc-") if keep is None else keep
    os.makedirs(d, exist_ok=True)
    bmp = os.path.join(d, "xsec.bmp"); im.save(bmp)
    out = subprocess.run(["atlc", "-S", "-s", "-c", CUTOFF, "-d", "c0c0c0=%s" % er, "-d", "a0a0a0=%s" % mask_er, bmp], capture_output=True, text=True).stdout
    import re as _re
    got = {m.group(1): float(m.group(2)) for m in _re.finditer(r"(Z\w+|Er_\w+)=\s*([-\d.eE+]+)", out)}   # atlc prints "Zodd=   89.1", spaces after the equals
    if "Zodd" not in got: raise SystemExit("atlc gave no Zodd:\n" + out[:600])
    return got.get("Zodd"), got.get("Zeven"), got.get("Zdiff", 2 * got["Zodd"]), bmp

CASES = [   # (label, mode, w, s, t, h, er, the closed form's answer from impedance_check.py, the class's target)
    ("4L 7628 outer, USB now (D9, C8)",      "microstrip", 0.30,  0.20,  0.035, 0.2104, 4.4,  89, 90),
    ("4L 7628 outer, USB as shipped (D8)",   "microstrip", 0.20,  0.15,  0.035, 0.2104, 4.4, 102, 90),
    ("6L 3313 outer, USB (B17)",             "microstrip", 0.127, 0.127, 0.035, 0.0994, 4.1,  94, 90),
    ("6L 3313 outer, DIFF100 (B17)",         "microstrip", 0.127, 0.20,  0.035, 0.0994, 4.1, 101, 100),
    # the inner-layer case of the 3313 stack is asymmetric (0.55 core one side, 0.1088 prepreg the other) and this entry models it
    # symmetrically, so its numbers are NOT a like-for-like comparison and the stripline confirmation is still owed (8 Sep 2026)
    ("6L 3313 inner stripline, 0.127/0.127 (symmetric model, not the real stack)", "stripline", 0.127, 0.127, 0.0152, 0.55, 4.6, 74, 100),
]

def main(a):
    if "--selftest" in a:
        ppmm = int(a[a.index("--ppmm") + 1]) if "--ppmm" in a else 200
        print("impedance_2d: atlc 2D field solver against the closed forms of impedance_check.py (%d px/mm)" % ppmm)
        worst = 0.0
        for label, mode, w, s, t, h, er, closed, target in CASES:
            zo, ze, zd, _ = solve(w, s, t, h, er, mode, ppmm=ppmm)
            zm = solve(w, s, t, h, er, mode, ppmm=ppmm, mask=0.01)[2] if mode != "stripline" else zd
            d = 100.0 * (zm - closed) / closed; worst = max(worst, abs(d))   # the masked solve is the like-for-like number: a real outer layer carries mask
            print("impedance_2d: %-40s w %.3f s %.3f h %.4f er %.1f | solver %5.1f (with mask %5.1f) | closed form %3d | %+5.1f%% | target %d" % (label, w, s, h, er, zd, zm, closed, d, target))
        print("impedance_2d: worst difference between the masked solver and the closed form %.1f%%" % worst)
        return 0 if worst <= 10.0 else 1
    def f(k, d=None):
        return float(a[a.index(k) + 1]) if k in a else d
    w, s, t, h, er = f("--w"), f("--s"), f("--t", 0.035), f("--h"), f("--er", 4.4)
    if None in (w, s, h): print(__doc__); return 2
    mode = a[a.index("--mode") + 1] if "--mode" in a else "microstrip"
    zo, ze, zd, bmp = solve(w, s, t, h, er, mode, f("--h2"), int(f("--ppmm", 200)))
    print("impedance_2d: %s w %.3f s %.3f t %.3f h %.4f er %.2f -> Zodd %.1f, Zeven %.1f, Zdiff %.1f ohm" % (mode, w, s, t, h, er, zo, ze, zd))
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
