#!/usr/bin/env python3
"""The face's Z budget, printed from panel1450.py (9 September 2026, appendix 32.85).

Written because the display's depth was argued in prose for three days and never computed. Every number below comes from
panel1450.py or is derived from it here; nothing is typed twice. Run it before and after any change to the face stack:

    python3 v2/ecad/tools/z_budget.py

It prints the stack, what the display needs, what stands in the way inside its footprint, and the margin. A negative
margin is the same defect `check_pcb_c.py` blocks on through `clearance_report()`; this tool exists to show WHERE the
millimetres went, which a pass/fail cannot. Exit status 1 if any margin is under the 2.0 mm the C gate requires."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel1450 as L

MARGIN = 2.0   # the same figure check_pcb_c.py holds deep face parts to


def rects_overlap(a, b):
    return a[2] > b[0] and a[0] < b[2] and a[3] > b[1] and a[1] < b[3]


def main():
    X = L.XENARC
    gx, gy = X["c"]; bw, bh = X["body"]
    foot = (gx - bw / 2, gy - bh / 2, gx + bw / 2, gy + bh / 2)
    glass_z = L.FACE_TOP_Z if X.get("recess") else L.FACE_TOP_Z + X["height"]
    body_bottom = glass_z - X["height"]

    print("FACE STACK (mm above the Peli 1450 cavity floor)")
    for name, z in (("plate top face (FACE_TOP_Z)", L.FACE_TOP_Z), ("plate underside", L.PLATE_UNDER_Z),
                    ("backer C7 top", L.PLATE_UNDER_Z - L.BACKER_GAP), ("backer C7 underside", L.BACKER_UNDER_Z),
                    ("B16 top copper (B_TOP_Z)", L.B_TOP_Z)):
        print("   %-32s %8.2f" % (name, z))

    print("\nDISPLAY")
    print("   %-32s %8.2f  (%s)" % ("glass surface", glass_z, "recessed, level with the plate" if X.get("recess") else "PROUD OF THE PLATE"))
    print("   %-32s %8.2f  (front bezel flange %.2f + rear shell %.2f)" % ("body bottom", body_bottom, X["bezel_depth"], X["shell_depth"]))
    print("   %-32s %8.2f" % ("depth needed below the face", X["height"]))
    print("   %-32s %8.2f" % ("proud of the plate", 0.0 if X.get("recess") else X["height"]))

    print("\nINSIDE THE DISPLAY'S FOOTPRINT  X %.3f .. %.3f, Y %.3f .. %.3f" % (foot[0], foot[2], foot[1], foot[3]))
    worst = None
    for rect, h, name in L.B16_TALL:
        if not rects_overlap(foot, rect):
            continue
        top = L.B_TOP_Z + h
        margin = body_bottom - top
        print("   %-34s top %7.2f   margin %+7.2f %s" % (name, top, margin, "" if margin >= MARGIN else "<-- SHORT"))
        if worst is None or margin < worst[1]:
            worst = (name, margin)
    for ref, c, d in L.deep_parts():
        if ref.startswith("XENARC"):
            continue
        r = L.deep_part_rect(ref, c, d)
        if not rects_overlap(foot, r):
            continue
        print("   %-34s bottom %7.2f  (face part inside the footprint) <-- MOVE IT" % (ref, L.FACE_TOP_Z - d))
        worst = (ref, -99.0)

    print("\nBACKER RING")
    n = L.BLOCK_NOTCH
    south = gy - bh / 2
    print("   void opening Y %.1f .. %.1f, the body's south edge %.3f" % (-88.0, 88.0, south))
    print("   notch %s: covers the body %s, reaches %.3f mm past its south edge"
          % (n, "yes" if n[0] <= foot[0] and n[2] >= foot[2] else "NO", south - n[1]))

    print("\nPROUD OF THE FACE (ruling 14.6, limit %.1f mm)" % L.PROUD_LIMIT)
    print("   %-32s %8.2f" % ("monitor glass", 0.0 if X.get("recess") else X["height"]))
    print("   %-32s %8.2f" % ("e-paper lens", L.EPAPER["lens_t"] + L.EPAPER["tape_t"] - L.EPAPER["pocket_depth"]))
    over = L.proud_report()

    bad = [r for r in L.clearance_report() if r[2] < MARGIN]
    print("\nVERDICT")
    print("   worst inside the footprint: %s" % ("%s %+.2f mm" % worst if worst else "nothing overlaps"))
    print("   deep parts under %.1f mm:   %s" % (MARGIN, bad or "none"))
    print("   display surfaces over %.1f mm proud: %s" % (L.PROUD_LIMIT, over or "none"))
    ok = not bad and not over
    print("   %s" % ("BUDGET MET" if ok else "BUDGET NOT MET"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
