#!/usr/bin/env python3
"""Numeric verification of PCB-C C5 (the sealed panel in the Peli 1520PF frame) against Peli drawing 1523-314-000, the TD2 STEP, the MIL-STD-1472 layout
rules and the sealing construction of appendix 32.34 (no plated hole on the face but LEDs and frame screws, keyed switch holes, seal bands, masked frame rings)."""
import sys, math, pcbnew
OX, OY = 297.0, 210.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
td2_segs = [sg for sg in segs if max(sg[0][1], sg[1][1]) < 60.0 and min(sg[0][1], sg[1][1]) > -70.0 and max(abs(sg[0][0]), abs(sg[1][0])) < 100.0]   # the display aperture only (the e-paper window sits at Y 73..127)
pts = [p for s in segs for p in s]
x0, x1, ybot, ytop = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
check(abs((x1 - x0) - 442.0) < 0.005 and abs((ytop - ybot) - 311.0) < 0.005 and abs(x0 + 221.0) < 0.005, "panel outline 442.000 x 311.000 centred (got %.3f x %.3f)" % (x1 - x0, ytop - ybot))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
# 1. the 16 frame screws on 431.8 x 301.2 (Peli 1523-314-000), Ø3.2 pads on GND
exp = [(x, y) for x in (-177.3, -88.6, 0.0, 88.6, 177.3) for y in (-150.6, 150.6)] + [(x, y) for x in (-215.9, 215.9) for y in (-110.7, 0.0, 110.7)]
holes = [fps["H%d" % i] for i in range(1, 17) if "H%d" % i in fps]
check(len(holes) == 16, "16 frame screw footprints (got %d)" % len(holes))
hp = [case(h.GetPosition()) for h in holes]
check(all(any(abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 for p in hp) for (x, y) in exp), "frame screws on the 431.8 x 301.2 pattern, no corner holes")
check(all(list(h.Pads())[0].GetDrillSize().x == pcbnew.FromMM(3.2) and list(h.Pads())[0].GetNetname() == "GND" for h in holes), "every frame screw is a Ø3.2 pad on GND (frame bond, MIL-STD-461)")
check(all(list(h.Pads())[0].GetSize().x == pcbnew.FromMM(8.0) and not list(h.Pads())[0].IsOnLayer(pcbnew.F_Mask) and list(h.Pads())[0].IsOnLayer(pcbnew.B_Mask) for h in holes), "frame screw rings 8.0 mm, masked on the face (gasket seat), open on the underside (star washer bond)")
# 2. aperture (STEP body + 0.4) and the glass bearing band
ipts = [p for s in td2_segs for p in s if -200 < p[0] < 200 and -140 < p[1] < 140]
ax0, ax1, ay0, ay1 = min(p[0] for p in ipts), max(p[0] for p in ipts), min(p[1] for p in ipts), max(p[1] for p in ipts)
ex = (-85.275 - 2.935 - 0.4, 83.275 - 2.935 + 0.4, -49.855 - 10.0 - 0.4, 49.855 - 10.0 + 0.4)
check(all(abs(a - e) < 0.005 for a, e in zip((ax0, ax1, ay0, ay1), ex)), "aperture X %.3f..%.3f Y %.3f..%.3f = TD2 body + 0.4 per side" % (ax0, ax1, ay0, ay1))
gx0, gx1, gy0, gy1 = -94.66, 94.66, -70.12, 50.12
check(min(ax0 - gx0, gx1 - ax1, ay0 - gy0, gy1 - ay1) >= 6.0, "glass bears on the panel by >= 6 mm on every side")
check(gx1 <= 211.3 - 5 and gy1 <= 145.6 - 5 and gy0 >= -145.6 + 5, "glass outline inside the frame window (422.6 x 291.2) by 5 mm")
band = [z for z in b.Zones() if z.GetIsRuleArea() and "tape band" in z.GetZoneName()]
check(len(band) == 1 and band[0].GetDoNotAllowTracks() and band[0].GetDoNotAllowVias() and band[0].GetDoNotAllowPads() and band[0].GetDoNotAllowCopperPour(), "display seal band rule area present: no tracks, vias, pads or pour under the glass flange")
# 2b. the sealing bands (C5): e-paper lens band and frame gasket band, face side copper-free, back side via-free; no via inside any of them
zn = {z.GetZoneName(): z for z in b.Zones() if z.GetIsRuleArea()}
def band_ok(name, face):
    z = zn.get(name)
    if z is None: return False
    if face: return z.GetDoNotAllowCopperPour() and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias()
    return z.GetDoNotAllowVias() and not z.GetDoNotAllowTracks()
check(band_ok("e-paper lens band F: no copper under the tape frame", True) and band_ok("e-paper lens band B: no vias under the sealing band", False), "e-paper lens band: face copper-free, back via-free")
check(band_ok("frame gasket band F: no copper under the PORON ring (frame screw rings excepted)", True) and band_ok("frame gasket band B: no vias under the sealing band", False), "frame gasket band: face copper-free, back via-free")
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
inband = [case(v.GetPosition()) for v in vias for z in (band + [zz for n, zz in zn.items() if "band" in n]) if z.Outline().Contains(v.GetPosition())]
check(not inband, "no via inside a seal band (%d found: %s)" % (len(inband), inband[:4]))
check(all(v.GetDrillValue() >= pcbnew.FromMM(0.3) - 1 for v in vias), "every via drill >= 0.3 mm (JLC 2-layer floor, plugging limit 0.5)")
check(all(v.GetDrillValue() <= pcbnew.FromMM(0.5) + 1 for v in vias), "every via drill <= 0.5 mm (JLC plugs holes up to 0.5)")
try: tent = open(sys.argv[1]).read().count("(tenting front back)") >= 1
except Exception: tent = False
check(tent, "board setup tents vias on both faces (the fab plugs them on top)")
# 2c. plated holes on the face: only the 16 frame screws and the 32 LED legs; every other part is SMD (connectors on the underside, switch leads on solder lands)
pth = [(fp.GetReference(), p.GetNumber()) for fp in b.GetFootprints() for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and not (fp.GetReference().startswith("H") or fp.GetReference().startswith("D"))]
check(not pth, "no plated component hole on the face except the frame screws and the LEDs (%s)" % pth[:6])
npth = {fp.GetReference(): [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH] for fp in b.GetFootprints()}
swp = [(fp.GetReference(), p.GetNumber()) for fp in b.GetFootprints() if fp.GetReference().startswith("SW_") or fp.GetReference() == "BZ1" for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and not p.IsOnLayer(pcbnew.B_Cu)]
check(not swp, "every switch and sounder lead land is an SMD pad on the underside (%s)" % swp[:6])
# 2d. panel-mount holes exactly on their MIL-STD-1472 sites, keyed holes for the K seal (three APEM) and the D flat (NKK LIGHT)
SITES = {"SW_MAIN": (-150, 100), "SW_PI": (-110, 100), "SW_TEST": (-70, 100), "SW_LIGHT": (120, 100), "SW_SOS": (170, 42), "SW_EMCON": (170, 0), "SW_ZERO": (170, -42), "BZ1": (-180, -100)}
off = {r: (case(npth[r][0].GetPosition()), SITES[r]) for r in SITES if r in fps and npth.get(r)}
bad_site = [r for r, (got, exp_) in off.items() if abs(got[0] - exp_[0]) > 0.01 or abs(got[1] - exp_[1]) > 0.01]
check(len(off) == 8 and not bad_site, "the seven switch holes and the sounder hole sit exactly on their sites (off: %s)" % bad_site)
def edge_items(fp): return [g for g in fp.GraphicalItems() if g.GetLayer() == pcbnew.Edge_Cuts]
key_ok = []
for r in ("SW_SOS", "SW_EMCON", "SW_ZERO"):
    fp = fps.get(r); items = edge_items(fp) if fp else []
    c = fp.GetPosition() if fp else None
    reach = max((g.GetBoundingBox().GetBottom() - c.y) / 1e6 for g in items) if items else 0.0   # KiCad +y = case -Y = toward the operator
    wide = max(g.GetBoundingBox().GetWidth() / 1e6 for g in items) if items else 0.0
    key_ok.append(abs(reach - 4.35) < 0.06 and abs(wide - 2.70) < 0.06)
check(all(key_ok), "APEM K-seal keyway notch 2.70 wide to 4.35 from the hole centre, toward the operator, on the three locking toggles")
fp = fps.get("SW_LIGHT"); dwide = max((g.GetBoundingBox().GetWidth() / 1e6 for g in edge_items(fp)), default=0.0) if fp else 0.0
check(fp is not None and abs(dwide - 5.8) < 0.06 and npth["SW_LIGHT"][0].GetDrillSize().x < pcbnew.FromMM(5.2), "NKK D hole on LIGHT: 6.5 with the flat at 5.8 across (Edge.Cuts) over an inscribed drill")
# 2e. courtyards inside the panel, connectors on the underside as SMD parts, die-cut outlines present
outside = [r for r, fp in fps.items() if not (-220.5 <= bbox(fp)[0] and bbox(fp)[2] <= 220.5 and -155.0 <= bbox(fp)[1] and bbox(fp)[3] <= 155.0)] if False else []

# 3. panel controls: pitch >= 25 mm between switch centres, all inside the window by 3 mm, 3 mm clear of every frame screw, nothing but LEDs over the Pi stack
sw = {r: case(fp.GetPosition()) for r, fp in fps.items() if r.startswith("SW_")}
check(len(sw) == 7, "seven panel switches (got %d)" % len(sw))
pairs = [(a, c_) for i, a in enumerate(sw) for c_ in list(sw)[i + 1:]]
dmin = min(math.hypot(sw[a][0] - sw[c_][0], sw[a][1] - sw[c_][1]) for a, c_ in pairs)
check(dmin >= 25.0, "switch centre pitch >= 25 mm (MIL-STD-1472 gloved use), min %.1f" % dmin)
def bbox(fp):
    bb = fp.GetBoundingBox(False, False); return (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
bad = []
for r, fp in fps.items():
    if r.startswith("H"): continue
    l, bt, rt, tp = bbox(fp)
    if fp.IsFlipped(): continue                                        # underside cluster: not on the visible face
    if l < -211.3 + 3 or rt > 211.3 - 3 or bt < -145.6 + 3 or tp > 145.6 - 3: bad.append(r + "@window")
    for (x, y) in exp:
        cx = max(l, min(x, rt)); cy = max(bt, min(y, tp))
        if math.hypot(cx - x, cy - y) < 1.7 + 3.0: bad.append(r + "@screw")
check(not bad, "every visible part inside the window by 3 mm and 3 mm clear of the frame screws (%s)" % bad)
stack = (-121.0, -48.5, -36.0, 48.5); over = []
for r, fp in fps.items():
    if r.startswith("H") or fp.IsFlipped(): continue
    l, bt, rt, tp = bbox(fp)
    if not (rt <= stack[0] or l >= stack[2] or tp <= stack[1] or bt >= stack[3]) and not r.startswith("D"): over.append(r)
check(not over, "only LEDs sit over the Pi + X1202 + cooler footprint (%s)" % over)
under = [r for r, fp in fps.items() if fp.IsFlipped()]
check(all(bbox(fps[r])[1] > 50 and bbox(fps[r])[0] > 130 for r in under if r not in ("J_MAINSW", "J_PIJ2", "R32", "R33", "J_EPD")), "underside cluster stays on the back strip's east part")
check(b.GetCopperLayerCount() == 2 and b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(2.0), "2 copper layers, 2.0 mm thick")
# e-paper recessed window (C4): aperture 94.19 x 53.6 centred on the module centre (30, 100), two tape lands and the body keep-out on the underside, nothing placed under the module
EPD_C = (30.0, 100.0)
win = [seg for seg in segs if 30 - 60 < min(seg[0][0], seg[1][0]) and max(seg[0][0], seg[1][0]) < 30 + 60 and 100 - 40 < min(seg[0][1], seg[1][1]) and max(seg[0][1], seg[1][1]) < 100 + 40]
if win:
    wx0 = min(min(a[0], b[0]) for a, b in win); wx1 = max(max(a[0], b[0]) for a, b in win); wy0 = min(min(a[1], b[1]) for a, b in win); wy1 = max(max(a[1], b[1]) for a, b in win)
    check(abs(wx1 - wx0 - 94.19) < 0.05 and abs(wy1 - wy0 - 53.6) < 0.05 and abs((wx0 + wx1) / 2 - EPD_C[0]) < 0.05 and abs((wy0 + wy1) / 2 - EPD_C[1]) < 0.05, "e-paper window 94.19 x 53.6 centred at (30, 100) (got %.2f x %.2f at %.2f, %.2f)" % (wx1 - wx0, wy1 - wy0, (wx0 + wx1) / 2, (wy0 + wy1) / 2))
else: check(False, "e-paper window present")
names = [z.GetZoneName() for z in b.Zones() if z.GetIsRuleArea()]
check(sum(1 for n in names if n.startswith("e-paper tape land")) == 2 and any(n.startswith("e-paper module body") for n in names), "e-paper underside rule areas (two lands, one body)")
mod = (EPD_C[0] - 52.9 - 1.0, EPD_C[1] - 26.9 - 1.0, EPD_C[0] + 52.9 + 1.0, EPD_C[1] + 26.9 + 1.0)
under = [fp.GetReference() for fp in b.GetFootprints() if fp.IsFlipped() and len(list(fp.Pads())) > 0 and not (fp.GetBoundingBox(False, False).GetRight() / 1e6 - OX < mod[0] or fp.GetBoundingBox(False, False).GetLeft() / 1e6 - OX > mod[2] or OY - fp.GetBoundingBox(False, False).GetTop() / 1e6 < mod[1] or OY - fp.GetBoundingBox(False, False).GetBottom() / 1e6 > mod[3])]
check(not under, "no underside part under the e-paper module (found %s)" % under)
outside = [r for r, fp in fps.items() if not (-220.5 <= bbox(fp)[0] and bbox(fp)[2] <= 220.5 and -155.0 <= bbox(fp)[1] and bbox(fp)[3] <= 155.0)]
check(not outside, "every footprint inside the panel outline by 0.5 mm (C4's J_PANEL hung 4 mm past the edge) (%s)" % outside)
conn = {r: fps[r] for r in ("J_PANEL", "J_EPD", "J_MAINSW", "J_PIJ2") if r in fps}
check(len(conn) == 4 and all(fp.IsFlipped() and all(p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for p in fp.Pads()) for fp in conn.values()), "J_PANEL, J_EPD, J_MAINSW and J_PIJ2 are SMD parts on the underside")
jp = fps.get("J_PANEL"); check(jp is not None and bbox(jp)[2] <= 210.3, "J_PANEL body inside the frame's bearing ring (east edge <= 210.3)")
U2 = getattr(pcbnew, "User_2", pcbnew.Eco1_User); U3 = getattr(pcbnew, "User_3", pcbnew.Eco2_User)
u2c = sum(1 for d in b.GetDrawings() if d.GetLayer() == U2 and d.GetClass() == "PCB_SHAPE" and d.GetShape() == pcbnew.SHAPE_T_CIRCLE)
u2s = sum(1 for d in b.GetDrawings() if d.GetLayer() == U2 and d.GetClass() == "PCB_SHAPE" and d.GetShape() in (pcbnew.SHAPE_T_SEGMENT, pcbnew.SHAPE_T_ARC))
u3s = sum(1 for d in b.GetDrawings() if d.GetLayer() == U3 and d.GetClass() == "PCB_SHAPE")
check(u2c == 16 and u2s >= 6 * 8 and u3s >= 2 * 8, "die-cut outlines on User.2 (three seals, 16 gasket holes) and the lenses on User.3 (got %d circles, %d edges, %d lens edges)" % (u2c, u2s, u3s))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
