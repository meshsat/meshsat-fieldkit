#!/usr/bin/env python3
"""PCB-E1 DOCK phase E4 (appendix 32.25, MESHSAT-790), mechanical: a 285 x 60 mm strip on the Peli 1520 floor; its north 29 mm lie under PCB-A's south edge at a 13.4 mm gap (the seven blind-mate float clamps, the raised contact block and the TEN 40 converter), its south 31 mm are clear of PCB-A and take the tall parts (fuse holders, connectors, the panel tracker stage). Originally a 250 x 44 mm strip. The two south rods pass through it
(Ø3.4 at (+-110.5, -73)), so the rods align the dock and PCB-A's 6 mm standoffs stand on it. It carries the shore-power entry and the
spring-pin targets that PCB-A's pins land on. Usage: gen_pcb_e.py <out.kicad_pcb>. Case-centred frame like PCB-A."""
import math, sys, os, pcbnew
from pcbnew import VECTOR2I, FromMM
OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-e1-dock.kicad_pcb"
PRJDIR = os.path.dirname(os.path.abspath(OUT))
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')
X0, X1, Y0, Y1, R = -160.0, 125.0, -111.0, -51.0, 3.0
RF_SITES = [(-100.0, "UHF"), (-84.0, "WIFI 2.4"), (-26.0, "WIFI 5.8"), (-12.0, "SDR"), (70.0, "LTE"), (92.0, "IRIDIUM"), (103.0, "LORA")]   # float clamps for the R222M80500 plugs, mirroring A19 (site 7 at Y -64)
BLOCK_HOLES = [(-153.0, -74.5), (-118.0, -74.5), (-153.0, -65.5), (-118.0, -65.5)]   # M3 standoffs of the raised contact block (pcb-e5-block, 39 x 12, face at 7.4 mm)
UNDER_A_Y = -80.0   # north of this line PCB-A sits 13.4 mm above the strip: parts at most 12 mm tall
ROD_HOLES = [(-110.5, -73.0), (110.5, -73.0)]; ROD_D = 3.2; STANDOFF_KEEPOUT_D = 9.0
BLOCK_C = (-135.5, -70.0)                      # raised block centre: A19 J_DOCK (-124, -70) and the 9 A pins at X -147..-135 land on it
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
board = pcbnew.BOARD()
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-E1 DOCK"); tb.SetRevision("A (E4)"); tb.SetDate("2026-09-05"); tb.SetCompany("MeshSat")
tb.SetComment(0, "MESHSAT-709 / 790. E4 floor dock strip: shore entry, panel tracker, battery module entry to the raised block, seven blind-mate float clamps, rods pass through. tools/gen_pcb_e.py + gen_pcb_e3.py"); board.SetTitleBlock(tb)
board.SetCopperLayerCount(4)
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
n = 3
rounded_rect(BLOCK_C[0] - 19.5, BLOCK_C[1] - 6.0, BLOCK_C[0] + 19.5, BLOCK_C[1] + 6.0, 1.0, pcbnew.Dwgs_User, 0.1); text("RAISED BLOCK pcb-e5-block on 6 mm M3 standoffs: A19 dock pins land here", BLOCK_C[0], BLOCK_C[1] + 8.5, pcbnew.Dwgs_User, 1.0, 0.18)
for (x, y) in BLOCK_HOLES:
    fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % n); fp.SetValue("M3 standoff, raised block"); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, y)); board.Add(fp); n += 1
for (x, nm) in RF_SITES:
    cy = -64.0 if nm == "LORA" else -66.0
    circle(x, cy, 9.9, pcbnew.Dwgs_User, 0.1); rounded_rect(x - 8.0, cy - 12.0, x + 8.0, cy + 12.0, 1.0, pcbnew.Dwgs_User, 0.1); text("CLAMP %s" % nm, x, cy - 14.5, pcbnew.F_SilkS, 0.9, 0.16)
    for hy in (cy - 10.0, cy + 10.0):
        fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/MountingHole.pretty", "MountingHole_3.2mm_M3"); fp.SetReference("H%d" % n); fp.SetValue("M3, float clamp %s" % nm); fp.Reference().SetVisible(False); fp.Value().SetVisible(False); fp.SetPosition(P(x, hy)); board.Add(fp); n += 1
    rule_area_circle(x, cy, 12.0, "clamp %s: no copper under the float clamp" % nm)
line(X0, UNDER_A_Y, X1, UNDER_A_Y, pcbnew.Dwgs_User, 0.15); text("PCB-A EDGE ABOVE (13.4 mm gap): north of this line parts at most 12 mm tall", 0, UNDER_A_Y - 2.0, pcbnew.Dwgs_User, 1.0, 0.18)
text("MESHSAT PCB-E1 DOCK (E4)  -  shore 9-36 V and panel tracker -> 12 V 40 W -> raised block -> PCB-A  -  seven blind-mate clamps  -  rods through H1/H2", 0, -52.3, pcbnew.F_SilkS, 1.2, 0.2)
text("D38999 DC pair -> J_DCIN -> F1 -> ideal diode -> TEN 40  |  panel pair -> J_SOLAR -> F2 -> LT8705A tracker 15 V -> ideal diode  |  battery module XT60 -> block lands  |  VHB pads to the floor", 0, -109.3, pcbnew.F_SilkS, 1.1, 0.18)
text("PCB-E1 underside: VHB pads at the four corners, no parts", 0, Y0 + 3.0, pcbnew.B_SilkS, 1.4, 0.22, mirror=True)
pcbnew.SaveBoard(OUT, board); print("saved", OUT, "holes:", n - 1)
