#!/usr/bin/env python3
"""PCB-E5 DOCK BLOCK (appendix 32.25, MESHSAT-790): the raised contact board on 6 mm standoffs above the dock strip, face at 7.4 mm, so PCB-A's
spring contacts (Preci-Dip 813 signal pins, 7.0 mm; Mill-Max 0858 class 9 A power pins) land on flat gold targets at the 13.4 mm blind-mate gap.
Top: the 2 x 6 signal targets (mirror of A19 J_DOCK at (-124, -70): A19's pins are on its underside, so its row order is mirrored: block pad k meets
A19 pin k+6 for k = 1..6 and pin k-6 for k = 7..12), four CELL+ targets, four return targets and the pre-charge target. Bottom: a 2 x 6 wire land
(2.54 mm, plated) and two 2.3 mm plated holes for the 12 AWG wires down to the strip's lands. No schematic: nets are named here. 2 oz copper.
Usage: gen_pcb_e5.py <out.kicad_pcb>. Case-centred frame like the strip."""
import sys, os, math, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-e5-block.kicad_pcb"
PRJDIR = os.path.dirname(os.path.abspath(OUT)); MSLIB = os.path.normpath(os.path.join(PRJDIR, "..", "meshsat.pretty"))
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
X0, X1, Y0, Y1, R = -156.0, -115.0, -80.0, -64.0, 1.5
HOLES = [(-153.0, -74.5), (-118.0, -74.5), (-153.0, -65.5), (-118.0, -65.5)]
board = pcbnew.BOARD()
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-E5 DOCK BLOCK"); tb.SetRevision("A (E5)"); tb.SetDate("2026-09-05"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-709 / 790. Raised contact block on the dock strip: targets for PCB-A's signal and 9 A power pins, wire lands below. tools/gen_pcb_e5.py"); board.SetTitleBlock(tb)
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
rounded_rect(X0, Y0, X1, Y1, R, pcbnew.Edge_Cuts)
for i, (x, y) in enumerate(HOLES, 1):
    fp = place("MountingHole", "MountingHole_3.2mm_M3", "H%d" % i, x, y, "M3 standoff 6 mm to the dock strip")
# A19 pin nets by pin number (its J_DOCK): 1-4 SHORE_12V, 5-7 GND, 8 SHORE_INHIBIT, 9 TS_MOD, 10 GND, 11 CELL_SENSE_P, 12 spare
A19 = {1: "SHORE_12V", 2: "SHORE_12V", 3: "SHORE_12V", 4: "SHORE_12V", 5: "GND", 6: "GND", 7: "GND", 8: "SHORE_INHIBIT", 9: "TS_MOD", 10: "GND", 11: "CELL_SENSE_P", 12: "BLK_SPARE"}
mirror = {k: (k + 6 if k <= 6 else k - 6) for k in range(1, 13)}   # block pad k faces A19 pin mirror[k]
tgt = place("meshsat", "PogoTargets_2x6", "T_SIG", -124.0, -70.0, "signal targets (A19 J_DOCK lands here)")
for pad in tgt.Pads(): pad.SetNet(net(A19[mirror[int(pad.GetNumber())]]))
land = place("meshsat", "PogoTargets_2x6", "L_SIG", -124.0, -77.0, "wire lands to the strip J_BLK (same order as A19 pins)", back=True)
for pad in land.Pads():
    pad.SetNet(net(A19[mirror[int(pad.GetNumber())]]))   # flipped: the same pad number sits under the same X, mirrored row, so it meets its own target's net
power = []
for k in range(4):
    x = -147.0 + 4.0 * k
    t = place("meshsat", "Mill-Max_0858_target", "T_CP%d" % (k + 1), x, -73.0, "CELL+ target (9 A pin)"); [p.SetNet(net("CELL+")) for p in t.Pads()]
    t = place("meshsat", "Mill-Max_0858_target", "T_CN%d" % (k + 1), x, -67.0, "return target (9 A pin)"); [p.SetNet(net("CELL_N")) for p in t.Pads()]
t = place("meshsat", "Mill-Max_0858_target", "T_PRE", -151.0, -70.0, "pre-charge target (longer pin, mates first)"); [p.SetNet(net("CELL+")) for p in t.Pads()]
w = place("meshsat", "WireHole_2mm", "WH_CP", -143.0, -77.5, "12 AWG to the strip P_CP"); [p.SetNet(net("CELL+")) for p in w.Pads()]
w = place("meshsat", "WireHole_2mm", "WH_CN", -137.0, -77.5, "12 AWG to the strip P_CN"); [p.SetNet(net("CELL_N")) for p in w.Pads()]
# copper: signal targets to lands (straight tracks, same X, top pad row to the land row through a via), power pours
def track(x1, y1, x2, y2, w, layer, n):
    t = pcbnew.PCB_TRACK(board); t.SetStart(P(x1, y1)); t.SetEnd(P(x2, y2)); t.SetWidth(FromMM(w)); t.SetLayer(layer); t.SetNet(net(n)); board.Add(t)
def via(x, y, n, d=0.6, dr=0.3):
    v = pcbnew.PCB_VIA(board); v.SetPosition(P(x, y)); v.SetWidth(FromMM(d)); v.SetDrill(FromMM(dr)); v.SetNet(net(n)); v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); board.Add(v)
tp = {int(p.GetNumber()): p for p in tgt.Pads()}; lp = {int(p.GetNumber()): p for p in land.Pads()}
for k in range(1, 13):
    a, b = tp[k].GetPosition(), lp[k].GetPosition(); ax, ay = a.x / 1e6 - OX, OY - a.y / 1e6; bx, by = b.x / 1e6 - OX, OY - b.y / 1e6
    n = A19[mirror[k]]; vy = -73.6 if k <= 6 else -72.6
    track(ax, ay, ax, vy, 0.4, pcbnew.F_Cu, n); via(ax, vy, n); track(bx, vy, bx, by, 0.4, pcbnew.B_Cu, n)
def pour(layer, n, name, rect):
    z = pcbnew.ZONE(board); z.SetLayer(layer); z.SetNet(net(n)); z.SetZoneName(name); z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetMinThickness(FromMM(0.25)); z.SetLocalClearance(FromMM(0.3))
    o = z.Outline(); o.NewOutline(); x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)): p = P(x, y); o.Append(p.x, p.y)
    board.Add(z); return z
pour(pcbnew.F_Cu, "CELL+", "CELL+ pour F", (-155, -79.5, -133, -70.5)); pour(pcbnew.B_Cu, "CELL+", "CELL+ pour B", (-155, -79.5, -140, -70.5))
pour(pcbnew.F_Cu, "CELL_N", "CELL_N pour F", (-155, -69.5, -133, -64.5)); pour(pcbnew.B_Cu, "CELL_N", "CELL_N pour B", (-139, -79.5, -133, -64.5))
for k in range(6): via(-153.0 + 3.0 * k, -75.5, "CELL+", 0.8, 0.4)
for k in range(3): via(-136.0 + 1.0 * k, -70.0, "CELL_N", 0.6, 0.3)
text("PCB-E5 DOCK BLOCK  face 7.4 mm  A19 pins land here", -135.5, -62.5, pcbnew.F_SilkS, 0.9, 0.15)
text("wires down to the strip: 12 signal + CELL+ / CELL_N 12 AWG", -135.5, -81.5, pcbnew.B_SilkS, 0.8, 0.13, mirror=True)
pcbnew.ZONE_FILLER(board).Fill(board.Zones()); pcbnew.SaveBoard(OUT, board); print("saved", OUT, "footprints:", len(list(board.GetFootprints())), "nets:", board.GetNetCount())
