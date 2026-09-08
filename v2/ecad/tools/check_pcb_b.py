#!/usr/bin/env python3
"""Numeric verification of PCB-B phase B16 (MESHSAT-830, appendix 32.58): outline, rods, the three Compute Module 5 sites and their receptacle pairs,
the M.2 sockets and their standoffs, the QMX, LimeSDR and RockBLOCK sites, J_AB1 under the board, the fabric nets reaching their receptacles, six layers;
on a placed board the net-class patterns; on a routed board the pair report."""
import sys, pcbnew, itertools
from pcbnew import FromMM
OX, OY = 150.0, 110.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 330) < 0.005 and abs(y1 - y0 - 200) < 0.005 and abs(x0 + 165) < 0.005 and abs(y1 - 100) < 0.005, "outline 330 x 200 centred (X %.2f..%.2f Y %.2f..%.2f)" % (x0, x1, y0, y1))
fps = {}
for fp in b.GetFootprints():
    pads = list(fp.Pads()); d = pads[0].GetDrillSize() if pads else None
    fps[fp.GetReference()] = (case(fp.GetPosition()), (round(d.x / 1e6, 2), round(d.y / 1e6, 2)) if d else None)
holes = {r: v for r, v in fps.items() if r.startswith("H")}
def near(p, q, tol=0.01): return abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol
def find(pos, drill): return any(near(v[0], pos) and abs(v[1][0] - drill) < 0.01 for v in holes.values())
for (x, y) in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]: check(find((x, y), 3.2), "rod hole 3.2 at (%.1f, %.1f)" % (x, y))
CM5_C = {1: (-72.5, 60.0), 2: (-2.5, 60.0), 3: (67.5, 60.0)}
for s, (cx, cy) in CM5_C.items():
    for (x, y) in [(cx + dx, cy + dy) for dx in (-16.5, 16.5) for dy in (-24.0, 24.0)]:
        check(find((x, y), 2.7), "CM5 S%d M2.5 hole 2.7 at (%.1f, %.1f) (module 40 x 55 at (%.1f, %.1f), holes 33 x 48)" % (s, x, y, cx, cy))
RB_C = (139.0, -71.0)
for p in [(RB_C[0] + dx, RB_C[1] + dy) for dx in (-16, 16) for dy in (-16, 16)]: check(find(p, 4.3), "9704 bracket hole 4.3 at %s" % (p,))
placed = len(list(b.GetFootprints())) > 200
fpo = {f.GetReference(): f for f in b.GetFootprints()}
def bbox(f):
    bb = f.GetBoundingBox(False, False); return (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
if placed:
    for s, (cx, cy) in CM5_C.items():
        for ref, rx in (("U3%dA" % (s - 1), cx - 17.0), ("U3%dB" % (s - 1), cx + 17.0)):
            f = fpo.get(ref); check(f is not None, "%s (CM5 receptacle, slot S%d) present" % (ref, s))
            if f is None: continue
            smd = [case(p.GetPosition()) for p in f.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
            check(len(smd) == 100, "%s has 100 pads (got %d)" % (ref, len(smd)))
            xs = sorted(set(round(p[0], 2) for p in smd)); ys = sorted(set(round(p[1], 2) for p in smd))
            check(len(xs) == 2 and abs(xs[1] - xs[0] - 3.08) < 0.02 and abs((xs[0] + xs[1]) / 2 - rx) < 0.05, "%s rows 3.08 mm apart centred x %.1f (got %s)" % (ref, rx, xs))
            check(len(ys) == 50 and abs(ys[-1] - ys[0] - 19.6) < 0.02 and abs((ys[0] + ys[-1]) / 2 - (cy - 2.5)) < 0.05, "%s 50 positions at 0.4 mm over 19.6 mm centred y %.1f (got %d over %.2f)" % (ref, cy - 2.5, len(ys), ys[-1] - ys[0]))
            check(all(cx - 20 < p[0] < cx + 20 and cy - 27.5 < p[1] < cy + 27.5 for p in smd), "%s pads inside the module outline" % ref)
    # M.2 sockets: body centre (the placement centres the courtyard box) and the standoff hole (card length minus 1.75 from the socket datum; cards extend south, S2's NVMe east)
    M2 = {"J_M2N1": (-85, 5.35, (-85, -17.1), 67), "J_M2C1": (-57, 11.35, (-57, -5.1), 67), "J_M2C2": (-20, 0.35, (-20, -27.1), 67), "J_M2N2": (-9.35, -85, (13.1, -85), 67), "J_M2N3": (48, 5.35, (48, -17.1), 67), "J_M2C3": (79, 5.35, (79, -17.1), 67)}
    for ref, (ex, ey, (sx, sy), ncont) in M2.items():
        f = fpo.get(ref); check(f is not None, "%s present" % ref)
        if f is None: continue
        r = bbox(f); cxb, cyb = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
        check(abs(cxb - ex) < 0.6 and abs(cyb - ey) < 0.6, "%s socket box centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cxb, cyb))
        check(sum(1 for pd in f.Pads() if pd.GetNumber().isdigit()) == ncont, "%s carries %d contacts" % (ref, ncont))
        st = [case(pd.GetPosition()) for pd in f.Pads() if pd.GetNumber() == "M1"]
        check(len(st) == 1 and abs(st[0][0] - sx) < 1.0 and abs(st[0][1] - sy) < 1.0, "%s standoff hole near (%.2f, %.2f) (got %s)" % (ref, sx, sy, st))
    for ref in ("J_ETH", "J_HDMI", "J_PANEL", "J_LIME", "J_RB9704", "T1", "U1", "U3", "U4", "U5", "U11", "U12", "U13", "U14", "J_SIM1", "J_SIM2", "J_5V_DEV", "J_54V", "BT1") + tuple("U%d0%d" % (s, k) for s in (1, 2, 3) for k in (1, 2, 3, 4, 5, 6)):
        check(ref in fpo, "%s present" % ref)
    j = fpo.get("J_AB1")
    if j is not None:
        check(j.IsFlipped(), "J_AB1 on the underside"); r = bbox(j); check(abs((r[0] + r[2]) / 2 - 113) < 0.6 and abs((r[1] + r[3]) / 2 + 46) < 0.6, "J_AB1 centred at (113, -46) over A22's header (got %.1f, %.1f)" % ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2))
    # the fabric nets: every PCIe, USB 3 and HDMI net of a slot reaches its module receptacle and the part it feeds (the B14 lesson: a net that lives only on one part makes no ratsnest)
    bynet = {}
    for f in b.GetFootprints():
        for pd in f.Pads():
            nm = pd.GetNetname().lstrip("/")
            if nm: bynet.setdefault(nm, set()).add(f.GetReference())
    for s in (1, 2, 3):
        rb = "U3%dB" % (s - 1); sw = "U%d01" % s; hub = "U%d02" % s
        for nm in ("PCIE%d_TX_P" % s, "PCIE%d_TX_N" % s, "PCIE%d_RX_P" % s, "PCIE%d_RX_N" % s, "PCIE%d_CLK_P" % s, "PCIE%d_CLK_N" % s, "PCIE%d_nRST" % s):
            check(rb in bynet.get(nm, set()) and sw in bynet.get(nm, set()), "%s reaches %s and the PCIe switch %s (got %s)" % (nm, rb, sw, sorted(bynet.get(nm, set()))))
        for nm in ("USB3%d_TX_P" % s, "USB3%d_TX_N" % s, "USB%d_UP_P" % s, "USB%d_UP_N" % s):
            check(rb in bynet.get(nm, set()) and hub in bynet.get(nm, set()), "%s reaches %s and the hub %s" % (nm, rb, hub))
        for nm in ("USB3%d_RX_P" % s, "USB3%d_RX_N" % s): check(rb in bynet.get(nm, set()) and len(bynet.get(nm, set())) >= 2, "%s reaches %s and its coupling capacitor" % (nm, rb))
        for nm in ("HDMI%d_D0_P" % s, "HDMI%d_D1_P" % s, "HDMI%d_D2_P" % s, "HDMI%d_CK_P" % s, "HDMI%d_HPD" % s, "HDMI%d_SDA" % s):
            check(rb in bynet.get(nm, set()) and ({"U3", "U4"} & bynet.get(nm, set())), "%s reaches %s and a display switch (got %s)" % (nm, rb, sorted(bynet.get(nm, set()))))
        for k in range(4): check(len(bynet.get("ETH%d_P%d_P" % (s, k), set())) == 2, "ETH%d_P%d_P reaches the receptacle and its coupling capacitor" % (s, k))
        for nm in ("NVME%d_TX_P" % s, "NVME%d_RX_P" % s, "NVME%d_CLK_P" % s, "CARD%d_TX_P" % s, "CARD%d_RX_P" % s, "CARD%d_CLK_P" % s):
            check(sw in bynet.get(nm, set()) and any(r.startswith("J_M2") for r in bynet.get(nm, set())), "%s reaches the switch and an M.2 socket (got %s)" % (nm, sorted(bynet.get(nm, set()))))
    for nm in ("HDMIO_D0_P", "HDMIO_CK_P", "HDMIO_SCL"): check("J_HDMI" in bynet.get(nm, set()) and "U4" in bynet.get(nm, set()), "%s reaches J_HDMI and U4" % nm)
    for nm in ("MDI_A_P", "MDI_B_P", "MDI_C_P", "MDI_D_P"): check("J_ETH" in bynet.get(nm, set()) and "T1" in bynet.get(nm, set()), "%s reaches J_ETH and the magnetics" % nm)
    for nm in ("LIME_SSTX_P", "LIME_DP"): check("J_LIME" in bynet.get(nm, set()) and "U102" in bynet.get(nm, set()), "%s reaches J_LIME and the S1 hub" % nm)
    import fnmatch as _fn, json as _json, os as _os
    pro = _os.path.splitext(sys.argv[1])[0] + ".kicad_pro"
    if _os.path.exists(pro):
        pats = [(e["pattern"], e["netclass"]) for e in _json.load(open(pro)).get("net_settings", {}).get("netclass_patterns", [])]
        names = {b.GetNetInfo().GetNetItem(i).GetNetname() for i in range(1, b.GetNetInfo().GetNetCount())}
        dead = [p for p, c in pats if not any(_fn.fnmatchcase(n, p) for n in names)]
        check(not [p for p in dead if not p.startswith("/") and ("/" + p) in dead], "every label net-class pattern matches a net in one of its two forms (unmatched: %s)" % [p for p in dead if not p.startswith("/") and ("/" + p) in dead])
    tl = {}
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK": tl[t.GetNetname().lstrip("/")] = tl.get(t.GetNetname().lstrip("/"), 0.0) + t.GetLength() / 1e6
    if tl:   # 8 Sep 2026 (MESHSAT-862): the +5V pours on In4 and the GND plane get the A21 copper checks; every netlist pair is reported, a one-leg pair is a FAIL
        import sys as _sys, os as _os2; _sys.path.insert(0, _os2.path.dirname(_os2.path.abspath(__file__))); import copper_checks as _cc; print(_cc.run(b, check))
    names_all = {b.GetNetInfo().GetNetItem(k).GetNetname().lstrip("/") for k in range(1, b.GetNetInfo().GetNetCount())}
    pairs = sorted(set(n[:-2] for n in names_all if n.endswith(("_P", "_N")) and (n[:-2] + "_P") in names_all and (n[:-2] + "_N") in names_all))
    for pair in pairs:
        lp, ln = tl.get(pair + "_P", 0.0), tl.get(pair + "_N", 0.0)
        if (lp > 0) != (ln > 0): check(False, "pair %s has one leg routed and one not (P %.2f mm, N %.2f mm)" % (pair, lp, ln)); continue
        if lp or ln: print("%s pair length P %.2f mm, N %.2f mm, mismatch %.2f mm%s" % (("WARN " if abs(lp - ln) > 1.0 else "PASS ") + pair, lp, ln, abs(lp - ln), "" if abs(lp - ln) <= 1.0 else " (over 1.0 mm: add a meander on the short leg)"))
# hole-to-hole webs >= 2 mm between every pair of holes (drill edges), the socket standoffs and the module holes included
hl = [(v[0], v[1][0], r) for r, v in holes.items()]
for fp in b.GetFootprints():
    if fp.GetReference() in holes or fp.GetReference().startswith("S_"): continue
    for p in fp.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_PTH) and min(p.GetDrillSize().x, p.GetDrillSize().y) >= FromMM(2.0): hl.append((case(p.GetPosition()), p.GetDrillSize().x / 1e6, fp.GetReference()))
hl2 = [(a, c) for a, c in itertools.combinations(hl, 2) if a[2] != c[2]]   # a footprint's own holes (the USB 3 receptacle's peg beside its shield hole) are the library's business
pair = min(hl2, key=lambda t: ((t[0][0][0] - t[1][0][0]) ** 2 + (t[0][0][1] - t[1][0][1]) ** 2) ** 0.5 - (t[0][1] + t[1][1]) / 2)
minweb = ((pair[0][0][0] - pair[1][0][0]) ** 2 + (pair[0][0][1] - pair[1][0][1]) ** 2) ** 0.5 - (pair[0][1] + pair[1][1]) / 2
check(minweb >= 2.0, "minimum web between any two holes %.2f mm (>= 2.0): %s at %s and %s at %s" % (minweb, pair[0][2], pair[0][0], pair[1][2], pair[1][0]))
# device rectangles: inside the outline (3 mm margin; edge connectors and the bracket may reach the edge), pairwise non-overlapping, clear of nut keep-outs
R = {"CM5_1": (-92.5, 32.5, -52.5, 87.5), "COOLER_1": (-93, 32, -52, 88), "CM5_2": (-22.5, 32.5, 17.5, 87.5), "COOLER_2": (-23, 32, 18, 88), "CM5_3": (47.5, 32.5, 87.5, 87.5), "COOLER_3": (47, 32, 88, 88),
     "QMX": (-162, -66, -99, 29), "LIME": (130, -24, 161, 45), "RB9704": (113, -99, 165, -43), "JLIME": (137, -43, 154, -24), "JAB": (110.5, -67, 115.5, -25), "JRB": (95.5, -67, 105.5, -45.1),
     "ETH": (-162, 30, -122, 59), "T1": (-161.5, 59, -142.5, 77), "JETH": (-162, 81, -142, 100), "POE": (-140.5, 59, -122, 86), "WNE": (-121, 29, -102, 68), "JPANEL": (-137, 86.5, -95, 97.5),
     "GAP12": (-50, 33, -32, 97), "GAP23": (19, 33, 44, 97), "JFAN1": (-101.5, 41, -93.5, 49), "JFAN2": (-31.5, 41, -23.5, 49), "JFAN3": (88.5, 40, 96.5, 48),
     "WMIDS": (-152, -97, -116, -69), "JHDMI": (96, -100, 113, -86), "NEX": (96, 78, 123, 97.5), "SEX": (96, -85, 112, -78), "RADE": (125.5, 45.5, 162, 67), "E22": (96.8, 27.75, 125.3, 67.25), "E72A": (123, 67.5, 144, 100.5), "E72B": (144, 67.5, 165, 100.5), "RBX": (96, -25, 126, 27), "RBX2": (96, -44, 110, -26),
     "S1_M2N": (-96.5, -20, -73.5, 30.5), "S1_M2C": (-68.5, -8, -45.5, 30.5), "S2_M2C": (-35.5, -30, -4.5, 30.5), "S2_M2N": (-35, -97, 16.5, -73.5), "S2_SIM": (-3, -7, 12, 30.5), "S2_SUP": (12, -30, 32, 28), "S2_SUP2": (-3, -30, 12, -8),
     "S3_M2N": (36.5, -20, 59.5, 30.5), "S3_M2C": (67.5, -20, 90.5, 30.5), "NORTH1": (-94, 88.5, -52, 97.5), "NORTH2": (-23, 88.5, 18, 97.5), "NORTH3": (47, 88.5, 88, 97.5),
     "S1_SW": (-98, -49, -38, -21), "S1_RAIL": (-98, -70, -38, -49), "S1_SUP": (-86, -97, -38, -70), "S2_SW": (-36, -54, 32, -30), "S2_RAIL": (-36, -73.4, 32, -54),
     "S3_SW": (34, -49, 94, -21), "S3_RAIL": (34, -70, 94, -49), "S3_SUP": (46, -97, 94, -70),
     "JFLASH1": (-98, -100, -87, -90), "JFLASH2": (18.5, -100, 29.5, -90), "JFLASH3": (34, -100, 45, -90), "J5V1": (-97.5, -89.5, -87.5, -79.5), "J5V2": (22, -89, 32, -79), "J5V3": (34.5, -89.5, 44.5, -79.5)}
EDGE = {"JETH", "JHDMI", "RB9704", "E72A", "E72B", "JFLASH1", "JFLASH2", "JFLASH3", "J5V1", "J5V3", "JPANEL", "NORTH1", "NORTH2", "NORTH3", "NEX"}
for k, r in R.items():
    if k in EDGE: continue
    check(r[0] >= -162 and r[2] <= 162 and r[1] >= -97 and r[3] <= 97, "%s inside outline with 3 mm margin" % k)
def overlap(a, c): return not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
SKIP = ({"CM5_1", "COOLER_1"}, {"CM5_2", "COOLER_2"}, {"CM5_3", "COOLER_3"}, {"RB9704", "JAB"}, {"COOLER_1", "NORTH1"}, {"COOLER_2", "NORTH2"}, {"COOLER_3", "NORTH3"})
for (ka, a), (kb, bb) in itertools.combinations(R.items(), 2):
    if {ka, kb} in SKIP: continue
    check(not overlap(a, bb), "%s and %s do not overlap" % (ka, kb))
def rect_circle_clear(r, c, rad):
    cx = max(r[0], min(c[0], r[2])); cy = max(r[1], min(c[1], r[3])); return ((cx - c[0]) ** 2 + (cy - c[1]) ** 2) ** 0.5 >= rad
for k, r in R.items():
    if k == "RB9704": continue   # the bracket plate rides on 8 mm standoffs over rod nut R2 (silk note on the board)
    check(all(rect_circle_clear(r, rod, 4.5) for rod in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]), "%s clear of the 9 mm nut keep-outs" % k)
check(b.GetCopperLayerCount() == 6, "6 copper layers (B16, JLC06161H-3313)")
check(b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(1.6), "1.6 mm thick")
# 8 Sep 2026 (MESHSAT-862 Stage C): the intent gates (return path under the pair-class nets, decoupling loops, the rails of the intent file)
if any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks()):
    import os as _os3, sys as _sys3; _sys3.path.insert(0, _os3.path.dirname(_os3.path.abspath(__file__))); import intent_checks as _ic; print(_ic.run(b, check, sys.argv[1]))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
