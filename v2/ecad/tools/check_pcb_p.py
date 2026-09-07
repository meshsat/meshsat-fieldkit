#!/usr/bin/env python3
"""PCB-P P1 numeric gate (MESHSAT-830, appendix 32.62): outline 70 x 44, four M3 holes at (+-32, +-19), two copper layers, the power path parts at their sites,
the locked bands present on both layers at 4 mm for every power net, every part on the top side, the gauge U1 on the QFN-32 land."""
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); OX, OY = 100.0, 100.0; fails = []
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
fps = {f.GetReference(): f for f in b.GetFootprints()}
bb = b.GetBoardEdgesBoundingBox(); w, h = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6
check(abs(w - 70) < 0.3 and abs(h - 44) < 0.3, "outline 70 x 44 (got %.1f x %.1f)" % (w, h))
check(b.GetCopperLayerCount() == 2, "two copper layers")
for ref, (x, y) in (("H1", (-32, -19)), ("H2", (32, -19)), ("H3", (-32, 19)), ("H4", (32, 19))):
    f = fps.get(ref); p = case(f.GetPosition()) if f else None
    check(f is not None and abs(p[0] - x) < 0.05 and abs(p[1] - y) < 0.05, "hole %s at (%d, %d)%s" % (ref, x, y, "" if f is None else " got %s" % (p,)))
for ref in ("U1", "F1", "Q1", "Q2", "R10", "W_BP", "W_BN", "W_P", "W_N", "J_CELL", "J_TS", "J_SMB", "D1", "D2"): check(ref in fps, "present %s" % ref)
check("U1" in fps and "QFN-32-1EP_5x5mm_P0.5mm" in fps["U1"].GetFPIDAsString(), "U1 on the QFN-32 5x5 land")
SITES = {"W_BP": (-27, 12.5), "F1": (-15.6, 15), "Q1": (0, 15), "Q2": (8, 15), "W_P": (26, 12.5), "W_BN": (-27, -12.5), "R10": (-18, -15), "W_N": (-8, -13.5), "J_CELL": (12, -17.5), "J_TS": (30.5, -9), "J_SMB": (30.5, 2)}
for ref, (x, y) in SITES.items():
    f = fps.get(ref)
    if f is None: continue
    fb = f.GetBoundingBox(False, False); cx, cy = case(pcbnew.VECTOR2I((fb.GetLeft() + fb.GetRight()) // 2, (fb.GetTop() + fb.GetBottom()) // 2))
    check(abs(cx - x) < 0.8 and abs(cy - y) < 0.8, "%s box centre at (%.1f, %.1f) got (%.1f, %.1f)" % (ref, x, y, cx, cy))
flipped = [f.GetReference() for f in b.GetFootprints() if f.IsFlipped()]
check(not flipped, "every part on the top side%s" % ("" if not flipped else ": " + ",".join(flipped[:6])))
for net in ("CELL4", "FUSED", "SW", "PACK_P", "PACK_N", "GND"):
    for L in (pcbnew.F_Cu, pcbnew.B_Cu):
        n = sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetLayer() == L and t.GetNetname().lstrip("/") == net and t.GetWidth() >= pcbnew.FromMM(2.7) and t.IsLocked())
        check(n >= 1, "locked band of %s on %s (%d)" % (net, b.GetLayerName(L), n))
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import copper_checks as _cc; print(_cc.run(b, check))   # 8 Sep 2026 (MESHSAT-862)
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
