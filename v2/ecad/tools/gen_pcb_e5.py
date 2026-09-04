#!/usr/bin/env python3
"""PCB-E5 DOCK BLOCK (appendix 32.25 and 32.26, MESHSAT-790): the raised contact board on 6 mm M3 standoffs above the dock strip, face at
7.4 mm, so PCB-A's spring contacts (Preci-Dip 813 signal pins, 7.0 mm; Mill-Max 0858 class 9 A power pins) land on flat gold targets at the
13.4 mm blind-mate gap. Top: the 2 x 6 signal targets under A19's J_DOCK (-124, -70); their nets are copied from the A19 board by position
(A19's connector sits on its underside, so its pin order is mirrored on the block), four CELL+ targets, four return targets and the
pre-charge target. Twelve plated wire lands (2 x 6 at 2.54 mm, 1.0 mm holes) at (-124, -77.5) carry the same nets straight down each
column to the strip's J_BLK lands (the underside silk names every land); two 2.3 mm plated holes take the 12 AWG CELL+ / CELL_N wires to
the strip's P_CP / P_CN. No schematic: nets are named here. 2 oz copper, 43 x 25 mm, X -158..-115, Y -85..-60.
Usage: gen_pcb_e5.py <out.kicad_pcb>   (reads ../pcb-a-power/pcb-a-power.kicad_pcb for the pin order). Case-centred frame like the strip."""
import sys, os, math, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-e5-block.kicad_pcb"
PRJDIR = os.path.dirname(os.path.abspath(OUT)); MSLIB = os.path.normpath(os.path.join(PRJDIR, "..", "meshsat.pretty"))
A19_PCB = os.path.normpath(os.path.join(PRJDIR, "..", "pcb-a-power", "pcb-a-power.kicad_pcb"))
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
X0, X1, Y0, Y1, R = -158.0, -115.0, -85.0, -60.0, 1.5
HOLES = [(-155.5, -63.0), (-117.5, -63.0), (-155.5, -82.0), (-117.5, -82.0)]      # = BLOCK_HOLES of gen_pcb_e.py (the strip's standoffs), in the four corners so nothing crowds the contact field
board = pcbnew.BOARD()
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-E5 DOCK BLOCK"); tb.SetRevision("A (E5)"); tb.SetDate("2026-09-05"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-709 / 790. Raised contact block on the dock strip: targets for PCB-A's signal and 9 A power pins, plated wire lands below. tools/gen_pcb_e5.py"); board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.2), ("m_TrackMinWidth", 0.2), ("m_ViasMinSize", 0.5), ("m_MinThroughDrill", 0.3), ("m_HoleToHoleMin", 0.5), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.25), ("m_SolderMaskMinWidth", 0.1)):
    try: setattr(ds, attr, FromMM(val))
    except Exception as e: print("note:", attr, e)
def shape(layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetLayer(layer); s.SetWidth(FromMM(width)); board.Add(s); return s
def line(x1, y1, x2, y2, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); return s
def arc(cx, cy, r, a0, a1, layer, width=0.1):
    am = (a0 + a1) / 2.0; pt = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*pt(a0)), P(*pt(am)), P(*pt(a1))); return s
def rounded_rect(x0, y0, x1, y1, r, layer, width=0.1):
    line(x0 + r, y0, x1 - r, y0, layer, width); line(x1, y0 + r, x1, y1 - r, layer, width); line(x1 - r, y1, x0 + r, y1, layer, width); line(x0, y1 - r, x0, y0 + r, layer, width)
    arc(x1 - r, y0 + r, r, 270, 360, layer, width); arc(x1 - r, y1 - r, r, 0, 90, layer, width); arc(x0 + r, y1 - r, r, 90, 180, layer, width); arc(x0 + r, y0 + r, r, 180, 270, layer, width)
def text(txt, x, y, layer, size=1.0, thick=0.15, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(layer); t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick))
    if mirror: t.SetMirrored(True)
    board.Add(t); return t
NETS = {}
def net(name):
    if name not in NETS: n = pcbnew.NETINFO_ITEM(board, name); board.Add(n); NETS[name] = n
    return NETS[name]
def place(lib, name, ref, x, y, value="", back=False, rot=0.0):
    fp = pcbnew.FootprintLoad(MSLIB if lib == "meshsat" else "/usr/share/kicad/footprints/" + lib + ".pretty", name)
    if fp is None: raise SystemExit("footprint missing: %s:%s" % (lib, name))
    fp.SetReference(ref); fp.SetValue(value); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp)
    if back: fp.Flip(P(x, y), False)
    fp.SetOrientationDegrees(rot); return fp
def no_pour_circle(cx, cy, d, name):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(False); z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(2)); z.SetZoneName(name); o = z.Outline(); o.NewOutline()
    for i in range(36):
        a = math.radians(i * 10); p = P(cx + d / 2 * math.cos(a), cy + d / 2 * math.sin(a)); o.Append(p.x, p.y)
    board.Add(z); return z
rounded_rect(X0, Y0, X1, Y1, R, pcbnew.Edge_Cuts)
for i, (x, y) in enumerate(HOLES, 1):
    place("MountingHole", "MountingHole_3.2mm_M3", "H%d" % i, x, y, "M3 standoff 6 mm to the dock strip"); no_pour_circle(x, y, 4.8, "standoff H%d: no pour" % i)
# --- A19's J_DOCK pin under every target, by position (the A19 connector is flipped to its underside; whatever KiCad's flip does, the match is geometric)
if not os.path.exists(A19_PCB): raise SystemExit("A19 board not found, the block copies its pin order from it: " + A19_PCB)
a19b = pcbnew.LoadBoard(A19_PCB); jd = a19b.FindFootprintByReference("J_DOCK")
if jd is None: raise SystemExit("A19 board has no J_DOCK")
jp = jd.GetPosition(); a19 = {}
for p in jd.Pads(): a19[(round((p.GetPosition().x - jp.x) / 1e4), round((p.GetPosition().y - jp.y) / 1e4))] = (int(p.GetNumber()), p.GetNetname())
tgt = place("meshsat", "PogoTargets_2x6", "T_SIG", -124.0, -70.0, "signal targets (A19 J_DOCK lands here)")
PIN = {}   # block pad number -> (A19 pin number, net)
for pad in tgt.Pads():
    key = (round((pad.GetPosition().x - tgt.GetPosition().x) / 1e4), round((pad.GetPosition().y - tgt.GetPosition().y) / 1e4))
    if key not in a19: raise SystemExit("no A19 pin above block target pad %s" % pad.GetNumber())
    num, n = a19[key]; n = n.lstrip("/")
    if not n or n.startswith("unconnected-"): n = "BLK_SPARE"
    PIN[int(pad.GetNumber())] = (num, n); pad.SetNet(net(n))
land = place("meshsat", "WireLands_2x6", "L_SIG", -124.0, -77.5, "plated wire lands to the strip J_BLK (net names on the underside silk)")
for pad in land.Pads(): pad.SetNet(net(PIN[int(pad.GetNumber())][1]))
for k in range(4):
    x = -147.0 + 4.0 * k
    t = place("meshsat", "Mill-Max_0858_target", "T_CP%d" % (k + 1), x, -73.0, "CELL+ target (9 A pin)"); [p.SetNet(net("CELL+")) for p in t.Pads()]
    t = place("meshsat", "Mill-Max_0858_target", "T_CN%d" % (k + 1), x, -67.0, "return target (9 A pin)"); [p.SetNet(net("CELL_N")) for p in t.Pads()]
t = place("meshsat", "Mill-Max_0858_target", "T_PRE", -151.0, -70.0, "pre-charge target (longer pin, mates first)"); [p.SetNet(net("CELL+")) for p in t.Pads()]
w = place("meshsat", "WireHole_2mm", "WH_CP", -140.0, -81.0, "12 AWG to the strip P_CP"); [p.SetNet(net("CELL+")) for p in w.Pads()]
w = place("meshsat", "WireHole_2mm", "WH_CN", -140.0, -63.0, "12 AWG to the strip P_CN"); [p.SetNet(net("CELL_N")) for p in w.Pads()]
# --- copper: every target to the land of its own column. North row: up to a via, then down on B.Cu under the south target to the north land.
# South row: down on F.Cu, jog half a pitch east to pass between the north lands, back into the south land. Power: pours plus stitching vias.
def track(x1, y1, x2, y2, w, layer, n):
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(net(n)); board.Add(t)
def via(x, y, n, d=0.6, dr=0.3):
    v = pcbnew.PCB_VIA(board); v.SetPosition(P(x, y)); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(dr)); v.SetNet(net(n)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); board.Add(v)
def dxy(p): q = p.GetPosition(); return q.x / 1e6 - OX, OY - q.y / 1e6
tp = {int(p.GetNumber()): p for p in tgt.Pads()}; lp = {int(p.GetNumber()): p for p in land.Pads()}
SHORT = {"SHORE_12V": "12V", "GND": "GND", "SHORE_INHIBIT": "INH", "TS_MOD": "TS", "CELL_SENSE_P": "KS+", "BLK_SPARE": "SP"}
for k in range(1, 7):
    n = tp[k].GetNetname(); x, yn = dxy(tp[k]); _, yln = dxy(lp[k])
    track(x, yn, x, -66.0, 0.4, pcbnew.F_Cu, n); via(x, -66.0, n); track(x, -66.0, x, yln, 0.4, pcbnew.B_Cu, n)
    n = tp[k + 6].GetNetname(); x, ys = dxy(tp[k + 6]); _, yls = dxy(lp[k + 6]); xj = x + 1.27
    pts = [(x, ys), (x, -73.6), (xj, -74.9), (xj, -77.5), (x, yls)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]): track(x1, y1, x2, y2, 0.3, pcbnew.F_Cu, n)
    text(SHORT.get(tp[k].GetNetname(), "?"), x, -74.6, pcbnew.B_SilkS, 0.5, 0.1, mirror=True); text(SHORT.get(tp[k + 6].GetNetname(), "?"), x, -80.6, pcbnew.B_SilkS, 0.5, 0.1, mirror=True)
def pour(layer, n, name, rect):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net(n)); z.SetZoneName(name); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    board.Add(z); return z
# CELL+ owns the south band (its target row at Y -73, the pre-charge disc and the 12 AWG hole), CELL_N the north band (row at Y -67 and its hole).
for L in (pcbnew.F_Cu, pcbnew.B_Cu):
    pour(L, "CELL+", "CELL+ pour " + board.GetLayerName(L), (-157, -84, -133, -71)); pour(L, "CELL_N", "CELL_N pour " + board.GetLayerName(L), (-157, -66, -133, -61))
for x in (-153.0, -145.0, -137.0): via(x, -80.0, "CELL+", 0.8, 0.4); via(x, -62.5, "CELL_N", 0.8, 0.4)
for x in (-149.0, -141.0): via(x, -71.8, "CELL+", 0.8, 0.4)
text("E5 DOCK BLOCK  face 7.4 mm", -124.0, -61.5, pcbnew.F_SilkS, 0.8, 0.14)
text("CELL+ 12 AWG", -145.0, -83.0, pcbnew.F_SilkS, 0.8, 0.14); text("RETURN 12 AWG", -145.0, -61.5, pcbnew.F_SilkS, 0.8, 0.14)
pcbnew.SaveBoard(OUT, board); b2 = pcbnew.LoadBoard(OUT); pcbnew.ZONE_FILLER(b2).Fill(b2.Zones()); pcbnew.SaveBoard(OUT, b2)
print("saved", OUT, "footprints:", len(list(b2.GetFootprints())), "nets:", b2.GetNetCount())
print("block target / land k -> A19 J_DOCK pin, net (wire land k to the strip J_BLK pin of that number):")
for k in range(1, 13): print("  %2d -> pin %2d  %s" % (k, PIN[k][0], PIN[k][1]))
