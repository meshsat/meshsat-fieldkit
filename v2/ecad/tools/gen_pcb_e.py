#!/usr/bin/env python3
"""PCB-E1 DOCK, mechanical: a 267 x 68 mm strip on the Peli 1450 floor (X -149 to 118, Y -113 to -45; the numbers are in the line
marked E6 below, and this docstring said 278 x 60 on the 1520 floor until 10 September 2026, which is the E4 board of appendix 32.25
and MESHSAT-790). Its north part lies under PCB-A's south edge at a 13.4 mm gap (the eleven blind-mate float clamps, the raised
contact block and the TEN 40 converter), its south part is clear of PCB-A and takes the tall parts (fuse holders, connectors, the
panel tracker stage). It began as a 250 x 44 mm strip. The two south rods pass through it
(Ø3.4 at (+-110.5, -73)), so the rods align the dock and PCB-A's 6 mm standoffs stand on it. It carries the shore-power entry and the
spring-pin targets that PCB-A's pins land on. Usage: gen_pcb_e.py <out.kicad_pcb>. Case-centred frame like PCB-A."""
import math, sys, os, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-e1-dock.kicad_pcb"
PRJDIR = os.path.dirname(os.path.abspath(OUT))
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')
PHASE = os.environ.get("PHASE", "E7")   # 9 September 2026: E gets the phase variable the other boards have, so the silk and the deliverable agree
X0, X1, Y0, Y1, R = -149.0, 118.0, -113.0, -45.0, 3.0   # E6: 267 x 68 (2 mm more to the wall, 6 mm more under A22); the west end stops 1 mm short of the BB-2590/U cradle (X -174 to -150, 32.49 item 12); the part west of X -121 is not under A22 (240 mm, X -120 to 120)
RF_SITES = [(-52.0, "VHF"), (-38.0, "HF"), (-24.0, "WIFI 2.4"), (-10.0, "GNSS"), (4.0, "SDR"), (18.0, "P2P A"), (32.0, "P2P B"), (60.0, "5G MAIN"), (74.0, "5G DIV"), (88.0, "IRIDIUM"), (102.0, "LORA")]   # eleven float clamps for the R222M80500 plugs, mirroring A22 (32.56)
BLOCK_HOLES = [(-104.0, -63.0), (-66.0, -63.0), (-104.0, -83.0), (-66.0, -83.0)]   # corner M3 standoffs of the raised contact block (pcb-e5-block, 43 x 25 at X -158..-115 Y -85..-60, face at 7.4 mm); its east edge stays 4.5 mm off the rod at (-110.5, -73) and its south edge 0.5 mm north of the J_BLK lands
UNDER_A_Y = -80.0   # north of this line PCB-A sits 13.4 mm above the strip: parts at most 12 mm tall
ROD_HOLES = [(-110.5, -73.0), (110.5, -73.0)]; ROD_D = 3.2; STANDOFF_KEEPOUT_D = 9.0
BLOCK_C = (-85.0, -70.0)                       # raised block centre: A22 J_DOCK (-76, -70), the 9 A pins at X -99..-87 and the pre-charge pin at -103 land on it (32.56)
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
board = pcbnew.BOARD()
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-E1 DOCK"); tb.SetRevision("A (%s)" % PHASE); tb.SetDate("2026-09-07"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-830. E6 floor dock strip: pack and vehicle entry to the raised block, panel tracker, sensor controller, eleven blind-mate float clamps, rods pass through. tools/gen_pcb_e.py + gen_pcb_e3.py"); board.SetTitleBlock(tb)
board.SetCopperLayerCount(4)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.40), ("m_MinThroughDrill", 0.20), ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.19), ("m_SolderMaskMinWidth", 0.1)):
    try: setattr(ds, attr, FromMM(val))
    except Exception as e: print("note:", attr, e)
def shape(layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetLayer(layer); s.SetWidth(FromMM(width)); board.Add(s); return s
def line(x1, y1, x2, y2, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); return s
def arc(cx, cy, r, a0, a1, layer, width=0.1):
    am = (a0 + a1) / 2.0; pt = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*pt(a0)), P(*pt(am)), P(*pt(a1))); return s
def circle(cx, cy, d, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetStart(P(cx, cy)); s.SetEnd(P(cx + d / 2.0, cy)); return s
def rounded_rect(x0, y0, x1, y1, r, layer, width=0.1):
    line(x0 + r, y0, x1 - r, y0, layer, width); line(x1, y0 + r, x1, y1 - r, layer, width); line(x1 - r, y1, x0 + r, y1, layer, width); line(x0, y1 - r, x0, y0 + r, layer, width)
    arc(x1 - r, y0 + r, r, 270, 360, layer, width); arc(x1 - r, y1 - r, r, 0, 90, layer, width); arc(x0 + r, y1 - r, r, 90, 180, layer, width); arc(x0 + r, y0 + r, r, 180, 270, layer, width)
def text(txt, x, y, layer, size=1.5, thick=0.25, angle=0.0, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(layer); t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick)); t.SetTextAngleDegrees(angle)
    if mirror: t.SetMirrored(True)
    board.Add(t); return t
def rule_area_circle(cx, cy, d, name, inner_d=None, layer=None):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True); z.SetDoNotAllowFootprints(False)
    if layer is None: z.SetLayerSet(pcbnew.LSET.AllCuMask(2))   # both outer layers (the standoffs and nuts touch both faces)
    else: z.SetLayer(layer)                                    # E6 route 1 (7 Sep 2026 01:14): the clamp sits on the top face only, so its no-copper circle is F.Cu only and B.Cu routes under it
    z.SetZoneName(name); o = z.Outline(); o.NewOutline()
    for i in range(36):
        a = math.radians(i * 10); p = P(cx + d / 2 * math.cos(a), cy + d / 2 * math.sin(a)); o.Append(p.x, p.y)
    if inner_d:
        h = o.NewHole(0)
        for i in range(36):
            a = math.radians(-i * 10); p = P(cx + inner_d / 2 * math.cos(a), cy + inner_d / 2 * math.sin(a)); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
rounded_rect(X0, Y0, X1, Y1, R, pcbnew.Edge_Cuts)
def edge_band(w=0.5):
    """E6 route 1 (7 Sep 2026 01:14, routeflow: 'edge clearance dominates: an edge keep-out band belongs in the outline generator'): a ring of rule area
    along the outline on every copper layer that forbids tracks and vias within w mm of the edge; pours keep their own clearance."""
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName("edge band: no tracks or vias within %.1f mm of the outline" % w)
    o = z.Outline(); o.NewOutline()
    for x, y in ((X0 - 1.0, Y0 - 1.0), (X1 + 1.0, Y0 - 1.0), (X1 + 1.0, Y1 + 1.0), (X0 - 1.0, Y1 + 1.0)): p = P(x, y); o.Append(p.x, p.y)
    h = o.NewHole(0)
    for x, y in ((X0 + w, Y0 + w), (X0 + w, Y1 - w), (X1 - w, Y1 - w), (X1 - w, Y0 + w)): p = P(x, y); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
edge_band(0.5)
for i, (x, y) in enumerate(ROD_HOLES, 1):
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % i); fp.SetValue("M3 rod pass-through, PCB-A standoff stands here"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp)
    circle(x, y, STANDOFF_KEEPOUT_D, pcbnew.F_SilkS, 0.15); rule_area_circle(x, y, STANDOFF_KEEPOUT_D, "standoff keep-out H%d" % i, inner_d=ROD_D + 3.0)
n = 3
rounded_rect(-106.5, -85.0, -63.5, -59.0, 1.5, pcbnew.Dwgs_User, 0.1); text("RAISED BLOCK pcb-e5-block on 6 mm M3 standoffs: A22 dock pins land here", BLOCK_C[0], BLOCK_C[1] + 8.5, pcbnew.Dwgs_User, 1.0, 0.18)
for (x, y) in BLOCK_HOLES:
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % n); fp.SetValue("M3 standoff, raised block"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp); n += 1
for (x, nm) in RF_SITES:
    cy = -66.0
    circle(x, cy, 9.9, pcbnew.Dwgs_User, 0.1); rounded_rect(x - 8.0, cy - 12.0, x + 8.0, cy + 12.0, 1.0, pcbnew.Dwgs_User, 0.1); text("CLAMP %s" % nm, x, cy - 14.5, pcbnew.F_SilkS, 0.9, 0.16)
    for hy in (cy - 10.0, cy + 10.0):
        fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % n); fp.SetValue("M3, float clamp %s" % nm); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, hy)); board.Add(fp); n += 1
    rule_area_circle(x, cy, 12.0, "clamp %s: no copper under the float clamp (top face)" % nm, layer=pcbnew.F_Cu)
line(-121.0, UNDER_A_Y, X1, UNDER_A_Y, pcbnew.Dwgs_User, 0.15); line(-121.0, Y0, -121.0, Y1, pcbnew.Dwgs_User, 0.15); text("PCB-A EDGE ABOVE (13.4 mm gap): north of this line and east of X -121 parts at most 12 mm tall", 0, UNDER_A_Y - 2.0, pcbnew.Dwgs_User, 1.0, 0.18)
text("MESHSAT PCB-E1 DOCK (%s)" % PHASE + "  -  pack 14.4 V and vehicle 9-36 V to the raised block -> A22  -  panel tracker  -  sensor controller on USB  -  eleven blind-mate clamps", 0, -46.3, pcbnew.F_SilkS, 1.2, 0.2)
text("D38999 DC pair -> J_DCIN -> F1 -> ideal diode -> LM5069 hot-swap -> filter -> raw bus  |  panel pair -> J_SOLAR -> F2 -> LT8705A tracker -> ideal diode  |  BB-2590/U cable XT60 -> F3 -> block  |  VHB pads to the floor", 0, -111.5, pcbnew.F_SilkS, 1.1, 0.18)
text("PCB-E1 underside: VHB pads at the four corners, no parts", 0, Y0 + 3.0, pcbnew.B_SilkS, 1.4, 0.22, mirror=True)
pcbnew.SaveBoard(OUT, board); print("saved", OUT, "holes:", n - 1)
