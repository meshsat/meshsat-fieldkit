#!/usr/bin/env python3
"""The face's Z budget, printed from panel1450.py (9 September 2026, appendix 32.85; datum rows rewritten 27 September 2026 for C1 on C6).

Written because the display's depth was argued in prose for three days and never computed. Every number below comes from
panel1450.py or is derived from it here; nothing is typed twice. Run it before and after any change to the face stack:

    python3 v2/ecad/tools/z_budget.py

It prints the two chains that meet under the monitor, both from the case floor (the face side through the setting legs of C6,
the frame's ring and the plate of C1; the board side through the stack of panel1450.STACK), what the display needs, what stands
in the way inside its footprint, and the margin at nominal, at the linear worst case, as RSS (each bound three sigma) and at the
worst with every allowance no source states taken twice (the sensitivity reading of v2/docs/CASE-MARGINS.md section 1, which is
not a bound on those allowances). The tolerance model is CASE-MARGINS.md's. A negative margin is the same defect `check_pcb_c.py`
blocks on through `clearance_report()`; this tool shows WHERE the millimetres went.

Row M1 stays OPEN whatever this prints: three contributors have no source yet (the Xenarc body's 28.66 and its rear frame, the
CM5 heatsink's 21.0, the gap and bay spacers), and the chain carries unstated allowances. Exit status 1 if the worst case of any
margin is under the 2.0 mm the C gate requires."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel1450 as L

MARGIN = 2.0   # the same figure check_pcb_c.py holds deep face parts to
UNSTATED = ("floor under the leg", "ring 9.39", "B bow")   # CASE-MARGINS.md section 1: Peli's case and the frame's ring publish no tolerance; bow is a build allowance
TBD = ["the Xenarc 709GNK body's 28.66 (read from its drawing at 400 dpi, no tolerance) and its steel rear frame (a kit part to draw)",
       "the CM5 heatsink's 21.0 (from the render scene, not a Raspberry Pi drawing)",
       "the blind-mate gap spacer (13.4) and the A-to-B bay spacer (31.3): no parts named"]


def rects_overlap(a, b):
    return a[2] > b[0] and a[0] < b[2] and a[3] > b[1] and a[1] < b[3]


def m1_chain():
    """M1, the monitor body over the CM5 heatsinks: (nominal, worst, rss_low, worst with the unstated allowances doubled, tolerances)."""
    heat = max(h for _, h, name in L.B16_TALL if "heatsink" in name)
    nominal = L.FACE_TOP_Z - L.XENARC["height"] - (L.B_TOP_Z + heat)
    tols = list(L.FACE_TOP_TOLS) + [("VHB 5952", L.STACK_TOL["vhb"]), ("laminate E", L.STACK_TOL["laminate"]),
                                    ("laminate A", L.STACK_TOL["laminate"]), ("laminate B", L.STACK_TOL["laminate"]), ("B bow", L.STACK_TOL["bow"])]
    worst = nominal - sum(t for _, t in tols)
    rss = nominal - math.sqrt(sum(t * t for _, t in tols))
    wc2 = worst - sum(t for n, t in tols if n.startswith(UNSTATED))
    return nominal, worst, rss, wc2, tols, heat


def main():
    X = L.XENARC
    gx, gy = X["c"]; bw, bh = X["body"]
    foot = (gx - bw / 2, gy - bh / 2, gx + bw / 2, gy + bh / 2)
    glass_z = L.FACE_TOP_Z if X.get("recess") else L.FACE_TOP_Z + X["height"]
    body_bottom = glass_z - X["height"]

    print("FACE SIDE, from the case floor (C6 legs, C1 plate on the 1450PF frame)")
    print("   %-40s %8.2f  (Peli's shoulder %.2f + %.2f + 0.10 - ring %.2f + floor %.2f + leg %.2f + ring %.2f)" % (
        "setting leg pad top (LEG_TOP_Z)", L.LEG_TOP_Z, L.PELI["shoulder_z"], L.TOL["case_z"], L.PELI["ring_t"], L.TOL["floor"], L.TOL["leg"], L.TOL["sheet"]))
    print("   %-40s %8.2f" % ("frame bottom (skirt edge)", L.FRAME_BOTTOM_Z))
    print("   %-40s %8.2f  (+ ring %.2f)" % ("frame ring top face", L.LEG_TOP_Z + L.PELI["ring_t"], L.PELI["ring_t"]))
    lo = L.FACE_TOP_Z - sum(t for _, t in L.FACE_TOP_TOLS); hi = L.FACE_TOP_Z + sum(t for _, t in L.FACE_TOP_TOLS)
    print("   %-40s %8.2f  (+ plate %.2f; %.2f .. %.2f over %s)" % ("plate top face (FACE_TOP_Z)", L.FACE_TOP_Z, L.PLATE[2], lo, hi,
                                                                 ", ".join("%s %.2f" % t for t in L.FACE_TOP_TOLS)))
    print("   %-40s %8.2f" % ("plate underside", L.PLATE_UNDER_Z))
    print("   %-40s %8.2f  (the rebated band's top; Peli's rim %.2f)" % ("plate edge top", L.FACE_TOP_Z - L.REBATE, L.PELI["rim_z"]))
    print("   %-40s %8.2f" % ("backer C top", L.PLATE_UNDER_Z - L.BACKER_GAP))
    print("   %-40s %8.2f" % ("backer C underside", L.BACKER_UNDER_Z))

    print("\nBOARD SIDE, from the case floor (panel1450.STACK)")
    z = 0.0
    for name, t in L.STACK:
        print("   %-40s %8.2f .. %6.2f  (%.1f)" % (name, z, z + t, t)); z += t
    print("   %-40s %8.2f" % ("B16 top copper (B_TOP_Z)", L.B_TOP_Z))
    nominal, worst, rss, wc2, tols, heat = m1_chain()
    print("   %-40s %8.2f  (B_TOP_Z + %.1f)" % ("CM5 heatsink top", L.B_TOP_Z + heat, heat))

    print("\nDISPLAY")
    print("   %-40s %8.2f  (%s)" % ("glass surface", glass_z, "recessed, level with the plate" if X.get("recess") else "PROUD OF THE PLATE"))
    print("   %-40s %8.2f  (front bezel flange %.2f + rear shell %.2f)" % ("body bottom", body_bottom, X["bezel_depth"], X["shell_depth"]))
    print("   %-40s %8.2f" % ("depth needed below the face", X["height"]))

    print("\nINSIDE THE DISPLAY'S FOOTPRINT  X %.3f .. %.3f, Y %.3f .. %.3f (nominal)" % (foot[0], foot[2], foot[1], foot[3]))
    worst_n = None
    for rect, h, name in L.B16_TALL:
        if not rects_overlap(foot, rect):
            continue
        top = L.B_TOP_Z + h
        margin = body_bottom - top
        print("   %-34s top %7.2f   margin %+7.2f %s" % (name, top, margin, "" if margin >= MARGIN else "<-- SHORT"))
        if worst_n is None or margin < worst_n[1]:
            worst_n = (name, margin)
    for ref, c, d in L.deep_parts():
        if ref.startswith("XENARC"):
            continue
        r = L.deep_part_rect(ref, c, d)
        if not rects_overlap(foot, r):
            continue
        print("   %-34s bottom %7.2f  (face part inside the footprint) <-- MOVE IT" % (ref, L.FACE_TOP_Z - d))
        worst_n = (ref, -99.0)

    print("\nM1, THE MONITOR BODY OVER THE CM5 HEATSINKS (v2/docs/CASE-MARGINS.md 3.1)")
    print("   tolerances in the chain: %s" % ", ".join("%s %.2f" % t for t in tols))
    print("   nominal %+.2f   worst %+.2f   RSS low %+.2f   worst, unstated x2 %+.2f   (floor %.1f)" % (nominal, worst, rss, wc2, MARGIN))
    print("   left out of every figure, TBD:")
    for t in TBD:
        print("     - %s" % t)
    print("   verdict: OPEN (TBD contributors; %s)" % ("the unstated allowances doubled fall below the floor" if wc2 < MARGIN else "the design basis holds with them doubled"))

    print("\nBACKER RING")
    n = L.BLOCK_NOTCH
    south = gy - bh / 2
    print("   void opening Y %.1f .. %.1f, the body's south edge %.3f" % (-88.0, 88.0, south))
    print("   notch %s: covers the body %s, reaches %.3f mm past its south edge"
          % (n, "yes" if n[0] <= foot[0] and n[2] >= foot[2] else "NO", south - n[1]))

    print("\nPROUD OF THE FACE (ruling 14.6, limit %.1f mm)" % L.PROUD_LIMIT)
    print("   %-40s %8.2f" % ("monitor glass", 0.0 if X.get("recess") else X["height"]))
    print("   %-40s %8.2f" % ("e-paper lens", L.EPAPER["lens_t"] + L.EPAPER["tape_t"] - L.EPAPER["pocket_depth"]))
    over = L.proud_report()

    bad = [r for r in L.clearance_report() if r[2] < MARGIN]
    print("\nVERDICT")
    print("   worst inside the footprint, nominal: %s" % ("%s %+.2f mm" % worst_n if worst_n else "nothing overlaps"))
    print("   M1 at the worst case: %+.2f mm against %.1f" % (worst, MARGIN))
    print("   deep parts under %.1f mm (nominal, clearance_report): %s" % (MARGIN, bad or "none"))
    print("   display surfaces over %.1f mm proud: %s" % (L.PROUD_LIMIT, over or "none"))
    ok = not bad and not over and worst >= MARGIN
    print("   %s" % ("BUDGET MET ON THE DESIGN BASIS (M1 stays OPEN on its TBD contributors)" if ok else "BUDGET NOT MET"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
