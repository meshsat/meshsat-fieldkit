#!/usr/bin/env python3
"""Numeric verification of PCB-C C7, the backer ring under the aluminium face plate of the Peli 1450 (MESHSAT-830; appendix 32.40, 32.51, 32.60): the ring outline
with its window and the monitor-block notch, the eight standoff screws on GND, every panel-mount part on the plate's site from tools/panel1450.py (the plate and this
board share the file, so a site here is a hole there), the toggle body slots, the headset jack holes, the LEDs under the light guides, the ribbon and the lead lands on
the underside, the e-paper ZIF and the light sensor on the top side, the MIL-STD-1472 pitch, and the height rule: every deep face part clears B16's tall parts by 2 mm
(panel1450.clearance_report) and the backer's parts clear the stack under the strips."""
import sys, math, os, pcbnew
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
OUTER = (L.STRIP_L[0], L.STRIP_B[1], L.STRIP_R[2], L.STRIP_L[3]); VOID = (L.STRIP_L[2], L.STRIP_B[3], L.STRIP_R[0], L.STRIP_T[1])
check(abs(x0 - OUTER[0]) < 0.01 and abs(x1 - OUTER[2]) < 0.01 and abs(ybot - OUTER[1]) < 0.01 and abs(ytop - OUTER[3]) < 0.01, "ring outline %.0f x %.0f from %s (got %.1f..%.1f, %.1f..%.1f)" % (OUTER[2] - OUTER[0], OUTER[3] - OUTER[1], OUTER, x0, x1, ybot, ytop))
top_inner = [sg for sg in segs if abs(sg[0][1] - VOID[3]) < 0.01 and abs(sg[1][1] - VOID[3]) < 0.01 and min(sg[0][0], sg[1][0]) > OUTER[0] + 1]
check(len(top_inner) == 1 and abs(min(top_inner[0][0][0], top_inner[0][1][0]) - VOID[0]) < 0.01 and abs(max(top_inner[0][0][0], top_inner[0][1][0]) - VOID[2]) < 0.01, "the window %s: its top edge at Y %.0f from X %.0f to %.0f" % (VOID, VOID[3], VOID[0], VOID[2]))
nx0, ny0, nx1, ny1 = L.BLOCK_NOTCH
notch = [sg for sg in segs if abs(sg[0][1] - ny0) < 0.01 and abs(sg[1][1] - ny0) < 0.01]
check(len(notch) == 1 and abs(min(notch[0][0][0], notch[0][1][0]) - nx0) < 0.01 and abs(max(notch[0][0][0], notch[0][1][0]) - nx1) < 0.01, "the monitor body notch %s cut into the bottom strip" % (L.BLOCK_NOTCH,))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def bbox(fp):
    bb = fp.GetBoundingBox(False, False); return (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
STRIPS = (L.STRIP_L, L.STRIP_B, L.STRIP_R, L.STRIP_T)
def in_strips(fp, margin=0.0):
    l, bt, rt, tp = bbox(fp)
    def inside(r): return l >= r[0] + margin and rt <= r[2] - margin and bt >= r[1] + margin and tp <= r[3] - margin
    corner = (l >= OUTER[0] and rt <= OUTER[2] and bt >= OUTER[1] and tp <= OUTER[3] and not (l > VOID[0] and rt < VOID[2] and bt > VOID[1] and tp < VOID[3]))
    return any(inside(r) for r in STRIPS) or corner
# 1. the eight standoff screws on GND, 3.2 drill, at the plate's standoff sites
holes = [fps["H%d" % i] for i in range(1, 9) if "H%d" % i in fps]
check(len(holes) == 8 and "H9" not in fps, "eight standoff screws H1..H8 (got %d)" % len(holes))
hp = [case(h.GetPosition()) for h in holes]
check(all(any(abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 for p in hp) for (x, y) in L.STANDOFFS), "standoff screws on the plate's eight sites")
check(all(list(h.Pads())[0].GetDrillSize().x == pcbnew.FromMM(3.2) and list(h.Pads())[0].GetNetname() == "GND" for h in holes), "every standoff screw is a 3.2 mm plated pad on GND (the plate's bond)")
# 2. panel-mount sites equal the plate's (the same file): hole centres exact, body slots on the toggles, the jack holes
npth = {fp.GetReference(): [p for p in fp.Pads() if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH] for fp in b.GetFootprints()}
SITES = {r: c for r, c, h, d in L.BUTTONS}; SITES.update({r: c for r, c in L.TOGGLES}); SITES[L.LIGHT[0]] = L.LIGHT[1]; SITES[L.SOUNDER[0]] = L.SOUNDER[1]; SITES.update({r: c for r, c in L.HEADSETS})
off = {r: (case(npth[r][0].GetPosition()), SITES[r]) for r in SITES if r in fps and npth.get(r)}
bad_site = [r for r, (got, exp_) in off.items() if abs(got[0] - exp_[0]) > 0.01 or abs(got[1] - exp_[1]) > 0.01]
check(len(off) == len(SITES) and not bad_site, "the seven switch holes, the sounder hole and the two jack holes sit exactly on the plate's sites (off: %s, missing: %s)" % (bad_site, [r for r in SITES if r not in off]))
for r, (w, h) in [(r, L.TOGGLE_BODY) for r, c in L.TOGGLES] + [(L.LIGHT[0], L.LIGHT_BODY)]:
    p = npth.get(r, [None])[0]
    check(p is not None and p.GetDrillShape() == pcbnew.PAD_DRILL_SHAPE_OBLONG and abs(p.GetDrillSize().x / 1e6 - w) < 0.05 and abs(p.GetDrillSize().y / 1e6 - h) < 0.05, "%s body slot %.0f x %.0f through the backer" % (r, w, h))
for r, c, hole, depth in L.BUTTONS:
    p = npth.get(r, [None])[0]; check(p is not None and abs(p.GetDrillSize().x / 1e6 - hole) < 0.05, "%s passes its %.1f mm hole" % (r, hole))
p = npth.get(L.SOUNDER[0], [None])[0]; check(p is not None and abs(p.GetDrillSize().x / 1e6 - L.SOUNDER[2]) < 0.05, "BZ1 passes its %.1f mm hole" % L.SOUNDER[2])
for r, c in L.HEADSETS:
    p = npth.get(r, [None])[0]; check(p is not None and abs(p.GetDrillSize().x / 1e6 - L.HEADSET_BODY) < 0.05, "%s passes its %.1f mm hole" % (r, L.HEADSET_BODY))
swp = [(fp.GetReference(), pd.GetNumber()) for fp in b.GetFootprints() if fp.GetReference().startswith("SW_") or fp.GetReference() == "BZ1" for pd in fp.Pads() if pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and not pd.IsOnLayer(pcbnew.B_Cu)]
check(not swp, "every switch and sounder lead land is an SMD pad on the underside (%s)" % swp[:6])
# 3. the sixteen LEDs on their light-guide sites, top face, through-hole
leds = {r: c for r, c, name in L.STATUS_LEDS + L.BAR_LEDS}
def dome(fp):
    ps = [case(pd.GetPosition()) for pd in fp.Pads()]; return (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps))
led_off = [r for r, c in leds.items() if r not in fps or abs(dome(fps[r])[0] - c[0]) > 0.3 or abs(dome(fps[r])[1] - c[1]) > 0.3 or fps[r].IsFlipped()]
check(not led_off, "sixteen LEDs on the plate's light-guide sites, top face (off: %s)" % led_off)
pth = [(fp.GetReference(), pd.GetNumber()) for fp in b.GetFootprints() for pd in fp.Pads() if pd.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and not (fp.GetReference().startswith("H") or fp.GetReference().startswith("D"))]
check(not pth, "no plated component hole but the standoff screws and the LEDs (%s)" % pth[:6])
# 4. controls: pitch, the plate outline, the strips; the top-side parts of the top and right strips
sw = {r: case(fp.GetPosition()) for r, fp in fps.items() if r.startswith("SW_")}
check(len(sw) == 7, "seven panel switches (got %d)" % len(sw))
pairs = [(a, c_) for i, a in enumerate(sw) for c_ in list(sw)[i + 1:]]
dmin = min(math.hypot(sw[a][0] - sw[c_][0], sw[a][1] - sw[c_][1]) for a, c_ in pairs)
check(dmin >= 25.0, "switch centre pitch >= 25 mm (MIL-STD-1472 gloved use), min %.1f" % dmin)
W, H = L.PLATE[0], L.PLATE[1]
outside_window = [r for r, fp in fps.items() if not r.startswith("H") and (bbox(fp)[0] < -W / 2 + 3 or bbox(fp)[2] > W / 2 - 3 or bbox(fp)[1] < -H / 2 + 3 or bbox(fp)[3] > H / 2 - 3)]
check(not outside_window, "every part inside the plate outline by 3 mm (%s)" % outside_window[:6])
off_board = [r for r, fp in fps.items() if not r.startswith("H") and not in_strips(fp, 0.0)]
check(not off_board, "every part on the ring (left, bottom, right or top strip), nothing over the window (%s)" % off_board[:8])
def mech_bbox(fp):
    """The COURTYARD where the footprint has one, else the bounding box. 9 Sep 2026 (32.85): the notch test used the bounding box,
    which includes silkscreen text; J_HSJ2's silk reaches 2.18 mm further north than any copper or body it owns and failed a notch
    the part is mechanically clear of. A notch is cut so a body can pass; silk is what the legend pass moves."""
    cy = fp.GetCourtyard(pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd)
    if cy.OutlineCount():
        bb = cy.BBox(); return (bb.GetLeft() / 1e6 - OX, OY - bb.GetBottom() / 1e6, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6)
    return bbox(fp)
notch_hit = [r for r, fp in fps.items() if not r.startswith("H") and mech_bbox(fp)[2] > nx0 and mech_bbox(fp)[0] < nx1 and mech_bbox(fp)[3] > ny0 and mech_bbox(fp)[1] < ny1 + 1]
check(not notch_hit, "nothing sits in the monitor block notch (%s)" % notch_hit[:6])
def site_ok(ref, xy, tol=0.6):
    fp = fps.get(ref)
    if fp is None: return False
    l, bt, rt, tp = bbox(fp); return abs((l + rt) / 2 - xy[0]) < tol and abs((bt + tp) / 2 - xy[1]) < tol
check(site_ok("J_EPD", L.J_EPD_POS, 1.5) and not fps["J_EPD"].IsFlipped(), "the e-paper ZIF J_EPD on the top strip's top side at %s" % (L.J_EPD_POS,))
check(site_ok(L.LIGHT_SENSOR[0], L.LIGHT_SENSOR[1]) and not fps[L.LIGHT_SENSOR[0]].IsFlipped(), "the light sensor on the top side under its guide at %s" % (L.LIGHT_SENSOR[1],))
check(site_ok("J_PANEL", L.J_PANEL_POS, 1.5) and fps["J_PANEL"].IsFlipped(), "the ribbon J_PANEL on the underside at %s (over B16's header)" % (L.J_PANEL_POS,))
ep_reach = math.hypot(L.J_EPD_POS[0] - (L.EPAPER["c"][0] - L.EPAPER["module"][0] / 2), L.J_EPD_POS[1] - L.EPAPER["c"][1])
check(ep_reach <= L.EPAPER["tail_len"] - 8.0, "the e-paper flex reaches the ZIF: %.1f mm of %.1f (8 mm of folds kept)" % (ep_reach, L.EPAPER["tail_len"]))
# 5. the height rule: every deep face part against B16's tall parts (panel1450.B16_TALL), 2 mm; the backer's own parts under the strips
rep = L.clearance_report(); worst = [(r, n, c) for r, n, c in rep if c < 2.0]
check(not worst, "every deep face part clears B16's tall parts by 2 mm (%s)" % ["%s over %s: %.1f" % w for w in worst][:6])
# 9 Sep 2026 (appendix 32.84): the check above asks whether a deep face part clears a tall board part UNDER the plate.
# Nothing asked whether two things ON the plate can both be there, and the Xenarc overlapped the e-paper lens by
# 1.045 mm and J_HSJ2's hole by 0.745 mm until a render showed it. Marking that a part hides is reported, not blocked.
face_hw = L.face_overlap_report("hw")
check(not face_hw, "no two face parts overlap in plan on the plate (%s)" % ["%s / %s %.2f x %.2f mm" % f for f in face_hw][:6])
face_hidden = L.face_overlap_report("hidden")
if face_hidden: print("check_pcb_c: INFO  laser marking under a face part: %s" % ["%s / %s %.2f x %.2f mm" % f for f in face_hidden][:4])
# 9 Sep 2026 (appendix 32.85): the owner's ruling 14.6 says every display surface is level with the plate, at most 0.5 to 0.8 mm
# proud. The Xenarc stood 28.66 mm proud for three days and no gate asked, because "proud" was prose in the record and a number
# in nobody's code. It is a number in panel1450.py now and this is where it blocks.
proud = L.proud_report()
check(not proud, "every display surface is within %.1f mm of the plate's face (%s)" % (L.PROUD_LIMIT, ["%s %.2f mm" % q for q in proud]))
ALLOW = {L.STRIP_T: 9.5, L.STRIP_L: 3.5, L.STRIP_B: 3.5, L.STRIP_R: 3.5}   # the underside's tallest parts per strip: the IDC ribbon header on the top strip, SMD parts elsewhere
tall_under = [(name, h, round(L.BACKER_UNDER_Z - ALLOW[st] - (L.B_TOP_Z + h), 1)) for (rx0, ry0, rx1, ry1), h, name in L.B16_TALL for st in STRIPS if rx1 > st[0] and rx0 < st[2] and ry1 > st[1] and ry0 < st[3] and L.BACKER_UNDER_Z - ALLOW[st] - (L.B_TOP_Z + h) < 3.0]
check(not tall_under, "B16's tall parts under the strips stay 3 mm below the backer's underside parts (3.5 mm allowance, 9.5 under the top strip's ribbon header): %s" % tall_under[:4])
# 6. board, vias, connectors
check(b.GetCopperLayerCount() == 4 and b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(L.BACKER_T), "4 copper layers (In1 ground plane), %.1f mm thick" % L.BACKER_T)
check(any(z.GetNetname() == "GND" and not z.GetIsRuleArea() and z.IsOnLayer(pcbnew.In1_Cu) for z in b.Zones()), "In1 carries the GND plane zone")
check(sum(1 for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith("In1 plane")) >= 7, "In1 plane keep-outs present (the clusters are the only windows)")
vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
check(all(v.GetDrillValue() >= pcbnew.FromMM(0.2) - 1 for v in vias), "every via drill >= 0.2 mm")
keep = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetDoNotAllowVias()]   # the In1 plane bands allow vias; only the cut-out and edge keep-outs forbid them
inkeep = [case(v.GetPosition()) for v in vias for z in keep if z.Outline().Contains(v.GetPosition())]
check(not inkeep, "no via inside a cut-out keep-out (%d found)" % len(inkeep))
conn = {r: fps[r] for r in ("J_PANEL", "J_MAINSW", "J_PIJ2") if r in fps}
check(len(conn) == 3 and all(fp.IsFlipped() and all(pd.GetAttribute() == pcbnew.PAD_ATTRIB_SMD for pd in fp.Pads()) for fp in conn.values()), "J_PANEL, J_MAINSW and J_PIJ2 are SMD parts on the underside")
under = [r for r, fp in fps.items() if fp.IsFlipped() and r not in conn]
check(all(in_strips(fps[r]) for r in under), "the underside cluster stays on the strips")
# 8 Sep 2026 (MESHSAT-862 Stage C): the intent gates (return path under the pair-class nets, decoupling loops, the rails of the intent file)
if any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks()):
    import os as _os3, sys as _sys3; _sys3.path.insert(0, _os3.path.dirname(_os3.path.abspath(__file__))); import intent_checks as _ic; print(_ic.run(b, check, sys.argv[1]))
# 8 Sep 2026 (MESHSAT-862): the copper checks were wired into the A and P gates only, and they are what finds a pour the router
# has eaten to islands or a stitch via the fill retreated from. D9 ended a clean route with eleven such islands on its front ground pour.
import copper_checks as _cc2; print(_cc2.run(b, check))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
