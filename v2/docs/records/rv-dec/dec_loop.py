#!/usr/bin/env python3
"""Decision 42: the loop inductance each placement option adds, from published closed forms and the recorded stackups
(MESHSAT-1357, 26 September 2026). Every number here is INFERRED: a closed-form estimate, not a field solve and not a
measurement. It compares OPTIONS on one board; the capacitor's own ESL is common to all options and left out.

1. Track from a capacitor's rail pad to the IC pin, on the outer layer over the first inner plane.
   Hammerstad and Jensen (1980, "Accurate models for microstrip computer-aided design", IEEE MTT-S Digest), zero
   thickness: Z01(u) = eta0/(2 pi) ln( f(u)/u + sqrt(1 + 4/u^2) ),  f(u) = 6 + (2 pi - 6) exp(-(30.666/u)^0.7528),
   u = w/h. The inductance per length of a quasi-TEM line is L' = Z0 sqrt(eps_eff)/c = Z01/c, which does not depend on
   the dielectric constant (inductance does not see the dielectric).
2. A via pair of length l carrying the loop current out and back (a capacitor on the far side, its rail via and its
   ground via): the two-wire line, L = (mu0 l / pi) acosh(s / 2r), s the via pitch, r the barrel radius.
3. A capacitor's impedance above its series resonance is its mounted inductance, independent of its value
   (Altera AN 574, May 2009, PDF page 6), so the comparison below holds for 100 nF and for 10 nF alike.
"""
import math

ETA0 = 376.730; C_MM_NS = 299.792458   # mm per ns
MU0_NH_PER_MM = 4 * math.pi * 1e-1      # mu0 = 4 pi 1e-7 H/m = 1.2566 nH/mm

def z01(u):
    f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / u) ** 0.7528))
    return ETA0 / (2 * math.pi) * math.log(f / u + math.sqrt(1 + 4 / u ** 2))

def l_track(w, h):    # nH per mm
    return z01(w / h) / C_MM_NS   # ohm / (mm/ns) = ns*ohm/mm = nH/mm

def l_via_pair(l, s, r=0.15):
    return MU0_NH_PER_MM * l / math.pi * math.acosh(s / (2 * r))

STACKS = {   # outer copper to the first inner plane, and total thickness, from the tree's own records
    "JLC06161H-3313 (boards A and B, six layers)": {"h": 0.0994, "board": 1.5832,
        "src": "v2/vendor/fabricator/jlcpcb-impedance-stackups-2026-09-16.md:33-47; tools/stackup_write.py:16"},
    "JLC08161H-2116 (board B, the eight-layer measurement of decision 43)": {"h": 0.1164, "board": 1.6,
        "src": "v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md (eight-layer table)"},
    "JLC04161H-7628 (boards C24 and D12, four layers 1 oz, ground on In1 and In2)": {"h": 0.2104, "board": 1.5862,
        "src": "v2/ecad/tools/stackup_write.py:15; the stackup blocks of the committed C24 and D12 board files"},
    "JLC04162H-7628 (board P, four layers 2 oz, decision 28)": {"h": 0.2104, "board": 1.6562,
        "src": "v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md (four-layer 2 oz table)"},
}

if __name__ == "__main__":
    print("1. track inductance per mm over the first inner plane (nH/mm)")
    for name, s in STACKS.items():
        print("   %-70s h %.4f mm:  w 0.20 %.3f   w 0.30 %.3f   w 0.50 %.3f" % (name, s["h"], l_track(0.20, s["h"]), l_track(0.30, s["h"]), l_track(0.50, s["h"])))
    print("2. via pair, 0.30 mm drill (r 0.15), through most of a 1.6 mm board (l = board minus the top dielectric)")
    for s_mm in (0.5, 0.8, 1.2):
        l = 1.5832 - 0.0994 - 0.035
        print("   pitch %.1f mm, l %.3f mm: %.2f nH" % (s_mm, l, l_via_pair(l, s_mm)))
    print("3. the options for one 0402 at a 0.4 to 0.5 mm pitch part on board B's six-layer stack, 0.25 mm track")
    Lt = l_track(0.25, 0.0994)
    for label, d in (("own-pin window, rail pad about 1.0 mm from the pin", 1.0),
                     ("outside the fan, rail pad about 3.2 mm from the pin", 3.2),
                     ("outside the fan, rail pad about 5.0 mm (a crowded part)", 5.0)):
        print("   %-58s track %.2f nH" % (label, Lt * d))
    for s_mm in (0.5, 0.8):
        print("   underside under the pin, dog-bone 0.5 mm + via pair at %.1f mm pitch:        %.2f nH"
              % (s_mm, Lt * 0.5 + l_via_pair(1.5832 - 0.0994 - 0.035, s_mm)))

    print("4. a capacitor on the side OPPOSITE its part (checker item 1, 26 September): dog-bone 0.5 mm + via pair from")
    print("   the far surface to the first plane under the part (l = board - outer copper - first dielectric), and the")
    print("   VIA ALLOWANCE: the length of 0.25 mm outer track over that plane with the same inductance as the via pair")
    for name, st in STACKS.items():
        l = st["board"] - st["h"] - 0.035
        Lt = l_track(0.25, st["h"])
        vp = [l_via_pair(l, s_mm) for s_mm in (0.5, 0.8, 1.2)]
        print("   %-70s L' %.3f nH/mm, l %.3f mm, via pair %.2f / %.2f / %.2f nH at 0.5 / 0.8 / 1.2 mm; allowance at 0.8 mm %.1f mm"
              % (name, Lt, l, vp[0], vp[1], vp[2], vp[1] / Lt))
        print("   %-70s opposite side under the pin (0.5 mm dog-bone + via pair at 0.8 mm) %.2f nH; own side, rail pad 1.0 / 3.2 / 5.0 mm: %.2f / %.2f / %.2f nH"
              % ("", Lt * 0.5 + vp[1], Lt * 1.0, Lt * 3.2, Lt * 5.0))

    # 5. (checker cycle 3, 26 September 16:42) SENSITIVITY of the via allowance, and AN 574's own worked figure.
    print("5. sensitivity of the via allowance (mm of outer track equal to the via pair) to via pitch and track width")
    for name, st in STACKS.items():
        l = st["board"] - st["h"] - 0.035
        cells = []
        for s_mm in (0.5, 0.8, 1.2):
            for w in (0.20, 0.25, 0.30):
                cells.append("p%.1f/w%.2f %.1f" % (s_mm, w, l_via_pair(l, s_mm) / l_track(w, st["h"])))
        print("   %-70s %s" % (name, "  ".join(cells)))
    # AN 574 (May 2009) p.15-16: a 115 mil (2.921 mm) board, the plane on layer 3, 12 mil (0.305 mm) from the top and
    # 103 mil (2.616 mm) from the bottom; a fully optimised 0402 mounts at 2.3 nH on the bottom and 0.57 nH on the top.
    MIL = 0.0254
    d_nh = 2.3 - 0.57; d_len = (103 - 12) * MIL
    rate = d_nh / d_len
    print("   AN 574's example: %.2f nH more for %.3f mm more via length, %.3f nH per mm of via" % (d_nh, d_len, rate))
    for name, st in STACKS.items():
        l = st["board"] - st["h"] - 0.035; own = st["h"] + 0.035; extra = l - own
        print("   %-70s far-side via %.3f mm, own-side via to the first plane %.3f mm, extra %.3f mm: at AN 574's rate %.2f nH; this model %.2f nH at 0.8 mm pitch"
              % (name, l, own, extra, rate * extra, l_via_pair(l, 0.8)))
