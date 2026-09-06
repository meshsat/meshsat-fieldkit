#!/usr/bin/env python3
"""Numeric verification of PCB-C C6, the backer board under the aluminium face plate of the Peli 1450 (appendix 32.40 items 4 and 5, 32.42): the U outline in
the strips outside PCB-B, the six standoff screws on GND, every panel-mount part on the plate's site from tools/panel1450.py (the plate and this board share
the file, so a site here is a hole there), the toggle body slots, the LEDs under the light pipes, the connectors on the underside as SMD parts, the MIL-STD-1472
pitch, and the height rule: every deep part outside PCB-B's outline and every part's depth below the face at least 3 mm above the stack under it
(v2/cad/stack-heightmap.json)."""
import sys, math, os, json, pcbnew
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel1450 as L
OX, OY = 297.0, 210.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1, ybot, ytop = min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)
OUTER = (L.STRIP_L[0], L.STRIP_B[1], L.STRIP_R[2], L.STRIP_L[3]); VOID = (L.STRIP_L[2], L.STRIP_B[3], L.STRIP_R[0], L.STRIP_L[3])
check(abs(x0 - OUTER[0]) < 0.01 and abs(x1 - OUTER[2]) < 0.01 and abs(ybot - OUTER[1]) < 0.01 and abs(ytop - OUTER[3]) < 0.01, "U outline %.0f x %.0f from %s (got %.1f..%.1f, %.1f..%.1f)" % (OUTER[2] - OUTER[0], OUTER[3] - OUTER[1], OUTER, x0, x1, ybot, ytop))
inner = [sg for sg in segs if abs(sg[0][1] - VOID[1]) < 0.01 and abs(sg[1][1] - VOID[1]) < 0.01]
check(len(inner) == 1 and abs(min(inner[0][0][0], inner[0][1][0]) - VOID[0]) < 0.01 and abs(max(inner[0][0][0], inner[0][1][0]) - VOID[2]) < 0.01, "the U is open over the display and the e-paper: inner edge at Y %.0f from X %.0f to %.0f" % (VOID[1], VOID[0], VOID[2]))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def bbox(fp):
    bb = fp.GetBoundingBox(False, False); return (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
def in_strips(fp, margin=0.0):
    l, bt, rt, tp = bbox(fp)
    def inside(r): return l >= r[0] + margin and rt <= r[2] - margin and bt >= r[1] + margin and tp <= r[3] - margin
    return inside(L.STRIP_L) or inside(L.STRIP_B) or inside(L.STRIP_R) or inside((L.STRIP_L[0], L.STRIP_B[1], L.STRIP_L[2], L.STRIP_L[3])) or (l >= OUTER[0] and rt <= OUTER[2] and bt >= OUTER[1] and tp <= OUTER[3] and not (rt > VOID[0] and l < VOID[2] and tp > VOID[1]))
# 1. the six standoff screws on GND, 3.2 drill, at the plate's standoff sites
holes = [fps["H%d" % i] for i in range(1, 7) if "H%d" % i in fps]
check(len(holes) == 6 and "H7" not in fps, "six standoff screws H1..H6 (got %d)" % len(holes))
hp = [case(h.GetPosition()) for h in holes]
check(all(any(abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 for p in hp) for (x, y) in L.STANDOFFS), "standoff screws on the plate's six sites %s" % L.STANDOFFS)
check(all(list(h.Pads())[0].GetDrillSize().x == pcbnew.FromMM(3.2) and list(h.Pads())[0].GetNetname() == "GND" for h in holes), "every standoff screw is a 3.2 mm plated pad on GND (the plate's bond)")
# 2. panel-mount sites equal the plate's (the same file): hole centres exact, body slots on the toggles
npth = {fp.GetReference(): [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH] for fp in b.GetFootprints()}
SITES = {r: c for r, c, h, d in L.BUTTONS}; SITES.update({r: c for r, c in L.TOGGLES}); SITES[L.LIGHT[0]] = L.LIGHT[1]; SITES[L.SOUNDER[0]] = L.SOUNDER[1]
off = {r: (case(npth[r][0].GetPosition()), SITES[r]) for r in SITES if r in fps and npth.get(r)}
bad_site = [r for r, (got, exp_) in off.items() if abs(got[0] - exp_[0]) > 0.01 or abs(got[1] - exp_[1]) > 0.01]
check(len(off) == 8 and not bad_site, "the seven switch holes and the sounder hole sit exactly on the plate's sites (off: %s)" % bad_site)
for r, (w, h) in [(r, L.TOGGLE_BODY) for r, c in L.TOGGLES] + [(L.LIGHT[0], L.LIGHT_BODY)]:
    p = npth.get(r, [None])[0]
    check(p is not None and p.GetDrillShape() == pcbnew.PAD_DRILL_SHAPE_OBLONG and abs(p.GetDrillSize().x / 1e6 - w) < 0.05 and abs(p.GetDrillSize().y / 1e6 - h) < 0.05, "%s body slot %.0f x %.0f through the backer" % (r, w, h))
for r, c, hole, depth in L.BUTTONS:
    p = npth.get(r, [None])[0]; check(p is not None and abs(p.GetDrillSize().x / 1e6 - hole) < 0.05, "%s passes its %.1f mm hole" % (r, hole))
p = npth.get(L.SOUNDER[0], [None])[0]; check(p is not None and abs(p.GetDrillSize().x / 1e6 - L.SOUNDER[2]) < 0.05, "BZ1 passes its %.1f mm hole" % L.SOUNDER[2])
swp = [(fp.GetReference(), pd.GetNumber()) for fp in b.GetFootprints() if fp.GetReference().startswith("SW_") or fp.GetReference() == "BZ1" for pd in fp.Pads() if pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and not pd.IsOnLayer(pcbnew.B_Cu)]
check(not swp, "every switch and sounder lead land is an SMD pad on the underside (%s)" % swp[:6])
# 3. the sixteen LEDs on their light-pipe sites, top face, through-hole
leds = {r: c for r, c, name in L.STATUS_LEDS + L.BAR_LEDS}
def dome(fp):   # the LED's dome sits between its two pads; KiCad's LED_D3.0mm origin is pad 1, 1.27 mm off the dome (C6 run 2 lesson)
    ps = [case(pd.GetPosition()) for pd in fp.Pads()]; return (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
led_off = [r for r, c in leds.items() if r not in fps or abs(dome(fps[r])[0] - c[0]) > 0.3 or abs(dome(fps[r])[1] - c[1]) > 0.3 or fps[r].IsFlipped()]
check(not led_off, "sixteen LEDs on the plate's light-pipe sites, top face (off: %s)" % led_off)
pth = [(fp.GetReference(), pd.GetNumber()) for fp in b.GetFootprints() for pd in fp.Pads() if pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and not (fp.GetReference().startswith("H") or fp.GetReference().startswith("D"))]
check(not pth, "no plated component hole but the standoff screws and the LEDs (%s)" % pth[:6])
# 4. controls: pitch, the window, the strips
sw = {r: case(fp.GetPosition()) for r, fp in fps.items() if r.startswith("SW_")}
check(len(sw) == 7, "seven panel switches (got %d)" % len(sw))
pairs = [(a, c_) for i, a in enumerate(sw) for c_ in list(sw)[i + 1:]]
dmin = min(math.hypot(sw[a][0] - sw[c_][0], sw[a][1] - sw[c_][1]) for a, c_ in pairs)
check(dmin >= 25.0, "switch centre pitch >= 25 mm (MIL-STD-1472 gloved use), min %.1f" % dmin)
W, H = L.PLATE[0], L.PLATE[1]   # the backer hangs under the plate: its parts stay inside the plate's outline by 3 mm (the frame window rule is the plate's, not the backer's)
outside_window = [r for r, fp in fps.items() if not r.startswith("H") and (bbox(fp)[0] < -W / 2 + 3 or bbox(fp)[2] > W / 2 - 3 or bbox(fp)[1] < -H / 2 + 3 or bbox(fp)[3] > H / 2 - 3)]
check(not outside_window, "every part inside the plate outline by 3 mm (%s)" % outside_window[:6])
off_board = [r for r, fp in fps.items() if not r.startswith("H") and not in_strips(fp, 0.0)]
check(not off_board, "every part on the U (left, bottom or right strip), nothing over the void (%s)" % off_board[:8])
# 5. the height rule: deep parts outside PCB-B's outline; every part's depth against the stack under it (3 mm)
bx0, by0, bx1, by1 = L.B_OUTLINE
deep_over_b = [r for r, (x, y), d in L.deep_parts() if bx0 - 3 < x < bx1 + 3 and by0 - 3 < y < by1 + 3]
check(not deep_over_b, "deep parts (buttons, toggles, sounder) outside PCB-B's outline (%s)" % deep_over_b)
hm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cad", "stack-heightmap.json")
if os.path.exists(hm_path):
    hm = json.load(open(hm_path)); step = hm["step"]
    def stack_top(x0_, y0_, x1_, y1_):
        top = 0.0
        for iy in range(hm["ny"]):
            yy = hm["y0"] + iy * step
            if yy < y0_ - step or yy > y1_ + step: continue
            for ix in range(hm["nx"]):
                xx = hm["x0"] + ix * step
                if x0_ - step <= xx <= x1_ + step: top = max(top, hm["z"][iy][ix])
        return top
    worst = []
    for r, (x, y), d in L.deep_parts():
        rad = 12.0; t = stack_top(x - rad, y - rad, x + rad, y + rad); bottom = L.FACE_TOP_Z - d
        if bottom - t < 3.0: worst.append("%s %.0f over %.0f" % (r, bottom, t))
    check(not worst, "every deep part's bottom at least 3 mm above the stack under it (%s)" % worst)
    # the backer itself with 9 mm of parts below its underside
    board_bottom = L.PLATE_UNDER_Z - L.BACKER_GAP - L.BACKER_T - 9.0; t = max(stack_top(*L.STRIP_L), stack_top(*L.STRIP_B), stack_top(*L.STRIP_R))
    check(board_bottom - t >= 3.0, "the backer's parts (down to %.0f) clear the stack under the strips (top %.0f)" % (board_bottom, t))
    disp_t = stack_top(L.DISPLAY["c"][0] - 95, L.DISPLAY["c"][1] - 61, L.DISPLAY["c"][0] + 95, L.DISPLAY["c"][1] + 61); epd_t = stack_top(L.EPAPER["c"][0] - 53, L.EPAPER["c"][1] - 27, L.EPAPER["c"][0] + 53, L.EPAPER["c"][1] + 27)
    check(L.PLATE_UNDER_Z - L.DISPLAY["depth_below"] - disp_t >= 3.0 and L.PLATE_UNDER_Z - L.EPAPER["depth_below"] - epd_t >= 3.0, "display (%.0f over %.0f) and e-paper (%.0f over %.0f) clear the stack by 3 mm" % (L.PLATE_UNDER_Z - L.DISPLAY["depth_below"], disp_t, L.PLATE_UNDER_Z - L.EPAPER["depth_below"], epd_t))
else: check(False, "stack height map v2/cad/stack-heightmap.json present")
# 6. board, vias, connectors
check(b.GetCopperLayerCount() == 4 and b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(L.BACKER_T), "4 copper layers (In1 ground plane), %.1f mm thick" % L.BACKER_T)
check(any(z.GetNetname() == "GND" and not z.GetIsRuleArea() and z.IsOnLayer(pcbnew.In1_Cu) for z in b.Zones()), "In1 carries the GND plane zone")
in1_tracks = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetLayer() == pcbnew.In1_Cu]
check(sum(1 for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith("In1 plane")) >= 5, "In1 plane keep-outs present (the clusters are the only windows)")
if in1_tracks: print("note: %d tracks on In1 (%.0f mm), inside the cluster windows if the keep-outs hold" % (len(in1_tracks), sum(pcbnew.ToMM(t.GetLength()) for t in in1_tracks)))
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
MIN_DRILL = 0.2 if b.GetCopperLayerCount() >= 4 else 0.3   # JLC: 0.2 mm on four layers, 0.3 mm on two (C6 run of 6 Sep 06:03: the 0.3 rule refused a clean four-layer route)
check(all(v.GetDrillValue() >= pcbnew.FromMM(MIN_DRILL) - 1 for v in vias), "every via drill >= %.1f mm" % MIN_DRILL)
keep = [z for z in b.Zones() if z.GetIsRuleArea() and "keep-out" in z.GetZoneName()]
inkeep = [case(v.GetPosition()) for v in vias for z in keep if z.Outline().Contains(v.GetPosition())]
check(not inkeep, "no via inside a cut-out keep-out (%d found)" % len(inkeep))
conn = {r: fps[r] for r in ("J_PANEL", "J_EPD", "J_MAINSW", "J_PIJ2") if r in fps}
check(len(conn) == 4 and all(fp.IsFlipped() and all(pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for pd in fp.Pads()) for fp in conn.values()), "J_PANEL, J_EPD, J_MAINSW and J_PIJ2 are SMD parts on the underside")
under = [r for r, fp in fps.items() if fp.IsFlipped() and r not in conn and r not in ("R32", "R33")]
check(all(in_strips(fps[r]) for r in under), "the underside cluster stays on the strips")
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
