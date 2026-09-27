#!/usr/bin/env python3
"""A09 adjudication cross-check with pcbnew (read-only): the LoRa blind-mate site on A and E, the parts inside the
D8 footprint on A's top and B's underside, and D8's own parts. Prints case-frame coordinates. Usage: a09_geom.py <repo>"""
import sys, os, hashlib, pcbnew
R = sys.argv[1]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def case(v, OX, OY): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
def bb(fp, OX, OY):
    b = fp.GetBoundingBox(False, False)
    return (round(b.GetLeft() / 1e6 - OX, 2), round(OY - b.GetBottom() / 1e6, 2), round(b.GetRight() / 1e6 - OX, 2), round(OY - b.GetTop() / 1e6, 2))
A = os.path.join(R, "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb")
for path in (A,):
    b = pcbnew.LoadBoard(path); print("A", path, sha(path), "thickness", b.GetDesignSettings().GetBoardThickness() / 1e6)
    for ref in ("J_BM10", "J_BM11", "J_RF11", "H2", "H5", "H6", "H7", "H8", "J_AB2"):
        fp = b.FindFootprintByReference(ref)
        p1 = [case(p.GetPosition(), 150, 110) for p in fp.Pads() if p.GetNumber() == "1"]
        print("  %-7s pos %s side %s pad1 %s bbox %s value %s" % (ref, case(fp.GetPosition(), 150, 110), "B" if fp.IsFlipped() else "F", p1, bb(fp, 150, 110), fp.GetValue()))
    inside = [(fp.GetReference(), fp.GetFPID().GetLibItemName().wx_str(), bb(fp, 150, 110)) for fp in b.GetFootprints()
              if not fp.IsFlipped() and 0 <= case(fp.GetPosition(), 150, 110)[0] <= 100 and -40 <= case(fp.GetPosition(), 150, 110)[1] <= 40
              and not fp.GetFPID().GetLibItemName().wx_str().startswith(("R_0", "C_0", "TestPoint", "MountingHole"))]
    print("  A top parts inside D8's footprint X 0..100 Y -40..40 (0402/0603/0805 R and C, test points and holes left out):")
    for r in sorted(inside): print("     ", r)
for path in (os.path.join(R, "v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb"), os.path.join(R, "v2/ecad/pcb-e1-dock-e7/routed/pcb-e1-dock.kicad_pcb"), os.path.join(R, "v2/ecad/pcb-e1-dock/pcb-e1-dock.kicad_pcb")):
    b = pcbnew.LoadBoard(path); print("E", path, sha(path))
    for t in b.GetDrawings():
        if isinstance(t, pcbnew.PCB_TEXT) and "MESHSAT PCB-E1" in t.GetText(): print("  silk:", t.GetText()[:40])
    holes = sorted(case(fp.GetPosition(), 150, 110) for fp in b.GetFootprints() if fp.GetReference().startswith("H") and case(fp.GetPosition(), 150, 110)[0] > 80)
    print("  holes east of X 80:", holes)
    for z in b.Zones():
        if z.GetIsRuleArea() and ("LORA" in z.GetZoneName() or "H2" in z.GetZoneName()):
            bx = z.GetBoundingBox(); print("  rule area %-45s bbox X %.2f..%.2f Y %.2f..%.2f" % (z.GetZoneName(), bx.GetLeft() / 1e6 - 150, bx.GetRight() / 1e6 - 150, 110 - bx.GetBottom() / 1e6, 110 - bx.GetTop() / 1e6))
D = os.path.join(R, "v2/ecad/pcb-d-aprs-d9/pcb-d-aprs.kicad_pcb")
b = pcbnew.LoadBoard(D); print("D", D, sha(D), "thickness", b.GetDesignSettings().GetBoardThickness() / 1e6)
e = b.GetBoardEdgesBoundingBox(); print("  outline local X %.1f..%.1f Y %.1f..%.1f -> case X %.1f..%.1f" % (e.GetLeft() / 1e6 - 100, e.GetRight() / 1e6 - 100, 100 - e.GetBottom() / 1e6, 100 - e.GetTop() / 1e6, e.GetLeft() / 1e6 - 100 + 50, e.GetRight() / 1e6 - 100 + 50))
for fp in sorted(b.GetFootprints(), key=lambda f: f.GetReference()):
    n = fp.GetFPID().GetLibItemName().wx_str()
    if fp.IsFlipped() or fp.GetReference().startswith(("J", "K", "U2", "H")):
        l = case(fp.GetPosition(), 100, 100)
        print("  %-8s %-45s %s local %s case (%.2f, %.2f) bbox_local %s" % (fp.GetReference(), n, "B" if fp.IsFlipped() else "F", l, l[0] + 50, l[1], bb(fp, 100, 100)))
Bp = os.path.join(R, "v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_pcb")
b = pcbnew.LoadBoard(Bp); print("B", Bp, sha(Bp), "thickness", b.GetDesignSettings().GetBoardThickness() / 1e6)
under = {}
for fp in b.GetFootprints():
    c = case(fp.GetPosition(), 150, 110)
    if fp.IsFlipped() and 0 <= c[0] <= 100 and -40 <= c[1] <= 40:
        n = fp.GetFPID().GetLibItemName().wx_str(); under[n] = under.get(n, 0) + 1
print("  B underside footprints inside D8's footprint:", under)
