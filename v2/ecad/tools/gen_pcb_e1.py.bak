#!/usr/bin/env python3
"""PCB-E1 DOCK, mechanical: a 250 x 44 mm strip on the Peli 1520 floor under PCB-A's south edge. The two south rods pass through it
(Ø3.4 at (+-110.5, -73)), so the rods align the dock and PCB-A's 6 mm standoffs stand on it. It carries the shore-power entry and the
spring-pin targets that PCB-A's pins land on. Usage: gen_pcb_e.py <out.kicad_pcb>. Case-centred frame like PCB-A."""
import math, sys, os, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-e1-dock.kicad_pcb"
PRJDIR = os.path.dirname(os.path.abspath(OUT))
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')
X0, X1, Y0, Y1, R = -125.0, 125.0, -95.0, -51.0, 3.0
ROD_HOLES = [(-110.5, -73.0), (110.5, -73.0)]; ROD_D = 3.2; STANDOFF_KEEPOUT_D = 9.0
DOCK_C = (-12.0, -70.0)                       # spring-pin target block centre = PCB-A's J_DOCK pin block (mirrored)
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
board = pcbnew.BOARD()
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-E1 DOCK"); tb.SetRevision("A (E1)"); tb.SetDate("2026-09-03"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-709. Floor dock strip: shore-power entry 9-36 V -> 12 V, spring-pin targets for PCB-A, rods pass through. tools/gen_pcb_e.py + gen_pcb_e3.py"); board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.45), ("m_MinThroughDrill", 0.25), ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.25), ("m_SolderMaskMinWidth", 0.1)):
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
def rule_area_circle(cx, cy, d, name, inner_d=None):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(2)); z.SetZoneName(name); o = z.Outline(); o.NewOutline()
    for i in range(36):
        a = math.radians(i * 10); p = P(cx + d / 2 * math.cos(a), cy + d / 2 * math.sin(a)); o.Append(p.x, p.y)
    if inner_d:
        h = o.NewHole(0)
        for i in range(36):
            a = math.radians(-i * 10); p = P(cx + inner_d / 2 * math.cos(a), cy + inner_d / 2 * math.sin(a)); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
rounded_rect(X0, Y0, X1, Y1, R, pcbnew.Edge_Cuts)
for i, (x, y) in enumerate(ROD_HOLES, 1):
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % i); fp.SetValue("M3 rod pass-through, PCB-A standoff stands here"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp)
    circle(x, y, STANDOFF_KEEPOUT_D, pcbnew.F_SilkS, 0.15); rule_area_circle(x, y, STANDOFF_KEEPOUT_D, "standoff keep-out H%d" % i, inner_d=ROD_D + 3.0)
rounded_rect(DOCK_C[0] - 7.0, DOCK_C[1] - 4.0, DOCK_C[0] + 7.0, DOCK_C[1] + 4.0, 1.0, pcbnew.Dwgs_User, 0.1); text("PCB-A J_DOCK pins land here", DOCK_C[0], DOCK_C[1] + 7.0, pcbnew.Dwgs_User, 1.2, 0.2)
text("MESHSAT PCB-E1 DOCK  -  shore 9-36 V -> 12 V 40 W -> PCB-A spring pins  -  rods through H1/H2", 0, -52.3, pcbnew.F_SilkS, 1.2, 0.2)
text("DC IN +/- (IP68 bulkhead lead)  |  F1 7.5 A mini blade  |  reverse polarity + 33 V TVS  |  opto inhibit on pin 8  |  VHB pads to the floor", 0, -93.3, pcbnew.F_SilkS, 1.3, 0.2)
text("PCB-E1 underside: VHB pads at the four corners, no parts", 0, Y0 + 3.0, pcbnew.B_SilkS, 1.4, 0.22, mirror=True)
pcbnew.SaveBoard(OUT, board); print("saved", OUT)
