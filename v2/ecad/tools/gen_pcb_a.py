#!/usr/bin/env python3
"""Generate PCB-A POWER + I/O, phase A22 (MESHSAT-830, 7 Sep 2026): the mechanical and placement-frame layer.

Case-centred frame as in the geometry appendix (+Y = case back wall). Millimetres. Appendix 32.56: 240 x 160 at X -120 to +120 (the west
45 mm of A21 went to the BB-2590/U cradle), rods at (+-110.5, +-73), the dock block moved east of the west rod, eleven blind-mate sites
along the south band, the D8 mezzanine 100 x 80 at X 0 to 100, the front end, charger and PoE stages in the west column, the rails in the
middle column, the PD outlet and the eFuses in the north-east band, the lead connectors on the east strip. The PA module is on the face plate.
"""
import math, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-a-power.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 240.0, 160.0, 5.0
BOARD_X0 = -120.0
ROD_HOLES = [(-110.5, -73.0), (110.5, -73.0), (-110.5, 73.0), (110.5, 73.0)]
ROD_DRILL, NUT_KEEPOUT_D = 3.2, 9.0
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
import os
PRJDIR = os.path.dirname(os.path.abspath(OUT))
MSLIB = os.path.normpath(os.path.join(PRJDIR, "..", "meshsat.pretty"))
os.makedirs(MSLIB, exist_ok=True)
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')
def slot_footprint(w, h):
    name = "Slot_%gx%g_NPTH" % (w, h)
    path = os.path.join(MSLIB, name + ".kicad_mod")
    if not os.path.exists(path):
        open(path, "w").write('(footprint "%s"\n\t(version 20241229)\n\t(generator "meshsat")\n\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "NPTH slot %g x %g mm for a cable tie or strap")\n\t(attr exclude_from_pos_files exclude_from_bom)\n\t(pad "" np_thru_hole oval (at 0 0) (size %g %g) (drill oval %g %g) (layers "*.Cu" "*.Mask"))\n\t(fp_rect (start %g %g) (end %g %g) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd"))\n)\n' % (name, w, h, w, h, w, h, -w/2-0.25, -h/2-0.25, w/2+0.25, h/2+0.25))
    return name

# ---------------------------------------------------------------- sites (case frame), appendix 32.56
DOCK_BLOCK = (-104.0, -78.0, -66.0, -64.0)       # underside pin field: J_PRE1 (-103, -70), J_CP1..4 (-99 + 4k, -73), J_CN1..4 (-99 + 4k, -67), J_DOCK 2x6 (-76, -70); E6's raised block reads these
RF_X = [-52, -38, -24, -10, 4, 18, 32, 60, 74, 88, 100]     # VHF HF WIFI24 GNSS SDR P2P-A P2P-B 5G-MAIN 5G-DIV IRID LORA (LORA at 100 since the ribbon moved to the east strip, 32.58)
RF_NAMES = ["VHF", "HF", "WIFI 2.4", "GNSS", "SDR", "P2P A", "P2P B", "5G MAIN", "5G DIV", "IRIDIUM", "LORA"]
RF_Y, RF_JY = -66.0, -56.0                        # SMP-MAX receptacles (underside) and SMA jacks (top)
FRONT_ZONE = (-118.0, 34.0, -70.0, 66.0)           # LM5176 front end from the dock's shore pins to the 20 V bus (J_AB1 sits above it at (-90, 76))
CHARGER_ZONE = (-118.0, -6.0, -70.0, 34.0)         # BQ25731 and its stage
POE_ZONE = (-118.0, -44.0, -70.0, -6.0)            # LM5176 boost to 54 V
FUSE_SITE = (-97.0, -52.0)                        # F1 25 A blade, between the POE zone and the dock block
RAILS_ZONE = (-66.0, 34.0, -2.0, 72.0)             # four TPS56637 rails with their INA226, VH outputs at Y 75
PA_ZONE = (-66.0, -14.0, -16.0, 20.0)
MID_ZONE = (-66.0, 20.0, -2.0, 34.0)               # the 3.3 V buck and the control passives              # LM5176 13.8 V for the PA on the plate
HF_ZONE = (-46.0, -48.0, -16.0, -22.0)             # TPS55288 12 V for the QMX
CTRL_ZONE = (-66.0, -48.0, -46.0, -14.0)
TP_ZONE = (-88.5, -64.0, -68.0, -46.0)              # test points beside the fuse           # LTC2954, expanders, mux, AND gates, 3.3 V buck
MEZZ_RECT = (0.0, -40.0, 100.0, 40.0)              # D8 mezzanine 100 x 80 on four M3 standoffs
MEZZ_HOLES = [(5.0, -35.0), (95.0, -35.0), (5.0, 35.0), (95.0, 35.0)]
J_MEZZ = (-8.0, 8.0); J_MEZZ_PWR = (-8.0, -18.0)
NE_ZONE = (0.0, 44.0, 100.0, 72.0)                 # USB-C PD outlet stage and the three eFuses
EAST_STRIP = (105.0, -67.0, 118.0, 67.0)           # lead connectors, rotated 90: J_PA (110, 62), J_MON (110, 50), J_HEAT (110, 38), J_USBC_OUT (110, 26), J_HF (110, 12), J_54V (110, 0), J_USBW (110, -12); J_MAINSW at (98, 75) in the north-east corner; J_AB1 (2x13 along Y) at (113, -46) on top, B16's underside header at the same case XY (32.58)
J_AB = (113.0, -46.0)                              # 2x13 IDC along Y, top side, on the east strip: B16's underside header at the same case XY (32.58; the north-west spot of 32.56 lies under B16's first module column)
# ---------------------------------------------------------------- plumbing (as PCB-C)
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-B COMPUTE"); tb.SetRevision("A")
tb.SetDate("2026-09-02"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-709. Case-centred frame. Phase B1 mechanical + placement. tools/gen_pcb_b.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.45), ("m_MinThroughDrill", 0.2),
                  ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.2), ("m_SolderMaskMinWidth", 0.1)):
    try: setattr(ds, attr, FromMM(val))
    except Exception as e: print("note:", attr, e)

def shape(layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board); s.SetLayer(layer); s.SetWidth(FromMM(width)); board.Add(s); return s
def line(x1, y1, x2, y2, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(P(x1, y1)); s.SetEnd(P(x2, y2)); return s
def arc(cx, cy, r, a0, a1, layer, width=0.1):
    pt = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(P(*pt(a0)), P(*pt((a0 + a1) / 2)), P(*pt(a1))); return s
def circle(cx, cy, d, layer, width=0.1):
    s = shape(layer, width); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetStart(P(cx, cy)); s.SetEnd(P(cx + d / 2, cy)); return s
def rounded_rect(x0, y0, x1, y1, r, layer, width=0.1):
    x0, x1 = min(x0, x1), max(x0, x1); y0, y1 = min(y0, y1), max(y0, y1)
    line(x0 + r, y0, x1 - r, y0, layer, width); line(x1, y0 + r, x1, y1 - r, layer, width)
    line(x1 - r, y1, x0 + r, y1, layer, width); line(x0, y1 - r, x0, y0 + r, layer, width)
    arc(x1 - r, y0 + r, r, 270, 360, layer, width); arc(x1 - r, y1 - r, r, 0, 90, layer, width)
    arc(x0 + r, y1 - r, r, 90, 180, layer, width); arc(x0 + r, y0 + r, r, 180, 270, layer, width)
def rect(r, layer, width=0.1):
    x0, y0, x1, y1 = r
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))): line(a[0], a[1], b[0], b[1], layer, width)
def text(txt, x, y, layer, size=1.5, thick=0.25, angle=0.0, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick)); t.SetTextAngleDegrees(angle)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    if mirror: t.SetMirrored(True)
    board.Add(t); return t
LIBS = "/usr/share/kicad/footprints/"
def fp_load(lib, name):
    fp = pcbnew.FootprintLoad(MSLIB if lib == "meshsat" else LIBS + lib + ".pretty", name)
    if fp is None: print("WARNING footprint missing:", lib, name)
    return fp
def place(lib, name, ref, x, y, value="", rot=0.0, back=False, centre=True):
    fp = fp_load(lib, name)
    if fp is None: return None
    fp.SetReference(ref); fp.SetValue(value); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    fp.SetPosition(P(x, y))
    if back: fp.Flip(P(x, y), False)
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    if centre:                                       # library origins vary (pin 1, centre...): centre the body on the target
        bb = fp.GetBoundingBox(False, False)
        cx, cy = (bb.GetLeft() + bb.GetRight()) // 2, (bb.GetTop() + bb.GetBottom()) // 2
        t = P(x, y); fp.Move(VECTOR2I(t.x - cx, t.y - cy))
    return fp
def hole(ref, x, y, d, value):
    name = {2.2: "MountingHole_2.2mm_M2", 2.7: "MountingHole_2.7mm_M2.5", 3.2: "MountingHole_3.2mm_M3", 4.3: "MountingHole_4.3mm_M4"}[d]
    if d != ROD_DRILL: keepout_circle(x, y, d + 2.0, "keep-out: " + ref)   # rods get their annular keep-out separately
    return place("MountingHole", name, ref, x, y, value)
def slot(ref, x, y, w, h, value="tie slot"):
    keepout_rect(x - w / 2 - 0.8, y - h / 2 - 0.8, x + w / 2 + 0.8, y + h / 2 + 0.8, "keep-out: " + ref)
    return place("meshsat", slot_footprint(w, h), ref, x, y, value, centre=True)
def rule_area_annulus(cx, cy, d, inner_d, name):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(4)); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for i in range(36):
        a = math.radians(i * 10); p = P(cx + d / 2 * math.cos(a), cy + d / 2 * math.sin(a)); o.Append(p.x, p.y)
    h = o.NewHole(0)
    for i in range(36):
        a = math.radians(-i * 10); p = P(cx + inner_d / 2 * math.cos(a), cy + inner_d / 2 * math.sin(a)); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
def rule_area_poly(pts, name):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(4)); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in pts:
        p = P(x, y); o.Append(p.x, p.y)
    board.Add(z); return z
def keepout_circle(cx, cy, d, name, n=36):
    return rule_area_poly([(cx + d / 2 * math.cos(math.radians(i * 360 / n)), cy + d / 2 * math.sin(math.radians(i * 360 / n))) for i in range(n)], name)
def keepout_rect(x0, y0, x1, y1, name):
    return rule_area_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], name)
def site(r, label, sublabel="", layer=pcbnew.F_SilkS, lx=None, ly=None):
    rect(r, layer, 0.12); cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    lx = cx if lx is None else lx; ly = cy if ly is None else ly
    text(label, lx, ly + 1.6, layer, 1.4, 0.22)
    if sublabel: text(sublabel, lx, ly - 1.4, layer, 1.0, 0.18)

# ---------------------------------------------------------------- outline + rods
hx, hy = BOARD_L / 2, BOARD_W / 2
rounded_rect(BOARD_X0, -hy, BOARD_X0 + BOARD_L, hy, BOARD_R, pcbnew.Edge_Cuts)
def edge_band(w=0.5):
    """A22 round 2 (7 Sep 2026): no tracks or vias within w mm of the outline on any copper layer (the E6 route 1 lesson); pours keep their own clearance."""
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName("edge band: no tracks or vias within %.1f mm of the outline" % w)
    o = z.Outline(); o.NewOutline(); X0, X1 = BOARD_X0, BOARD_X0 + BOARD_L
    for x, y in ((X0 - 1.0, -hy - 1.0), (X1 + 1.0, -hy - 1.0), (X1 + 1.0, hy + 1.0), (X0 - 1.0, hy + 1.0)): p = P(x, y); o.Append(p.x, p.y)
    h = o.NewHole(0)
    for x, y in ((X0 + w, -hy + w), (X0 + w, hy - w), (X1 - w, hy - w), (X1 - w, -hy + w)): p = P(x, y); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
edge_band(0.5)
for i, (x, y) in enumerate(ROD_HOLES, 1):
    hole("H%d" % i, x, y, 3.2, "M3 rod R%d" % i)
    for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS): circle(x, y, NUT_KEEPOUT_D, layer, 0.15)
    rule_area_annulus(x, y, NUT_KEEPOUT_D, ROD_DRILL + 3.0, "nut keep-out R%d" % i)
    text("R%d" % i, x, y + 7.0 if y < 0 else y - 7.0, pcbnew.F_SilkS, 1.5, 0.25)
n = 5
# ---------------------------------------------------------------- zones (drawing layer), dock block, RF sites
for zr, label in ((FRONT_ZONE, "FRONT END: LM5176 9-36 V -> 20 V BUS"), (CHARGER_ZONE, "CHARGER BQ25731 4S FROM THE 20 V BUS"), (POE_ZONE, "POE RAIL: LM5176 BOOST 54 V"),
                  (RAILS_ZONE, "SLOT RAILS S1 S2 S3 + DEVICE RAIL: TPS56637 + INA226"), (PA_ZONE, "PA RAIL: LM5176 13.8 V (PA ON THE PLATE)"), (HF_ZONE, "HF RAIL: TPS55288 12 V"),
                  (CTRL_ZONE, "CONTROL: LTC2954, EXPANDERS, EMCON GATES"), (MID_ZONE, "3.3 V BUCK, CONTROL PASSIVES"), (TP_ZONE, "TEST POINTS"), (NE_ZONE, "USB-C PD OUTLET + EFUSES (MONITOR, HEATER, D8)"), (EAST_STRIP, "LEAD CONNECTORS")):
    rect(zr, pcbnew.Dwgs_User, 0.15); text(label, (zr[0] + zr[2]) / 2, zr[3] + 1.8, pcbnew.Dwgs_User, 0.9, 0.16)
rect(DOCK_BLOCK, pcbnew.Dwgs_User, 0.15); text("DOCK BLOCK (underside): J_DOCK 2x6 + 9 A pins + pre-charge pin, land on E6's block", (DOCK_BLOCK[0] + DOCK_BLOCK[2]) / 2, DOCK_BLOCK[1] - 1.8, pcbnew.Dwgs_User, 0.9, 0.16)
text("BB-2590/U PACK IN ITS CRADLE WEST OF THIS BOARD (32.49 item 12), ITS CABLE INTO E6, THE NODE OVER THE DOCK PINS", -60.0, -79.0, pcbnew.F_SilkS, 1.0, 0.16)
for x, nm in zip(RF_X, RF_NAMES):
    circle(x, RF_Y, 12.0, pcbnew.Dwgs_User, 0.1); circle(x, RF_Y, 8.3, pcbnew.B_SilkS, 0.12)
    text("BM %s" % nm, x, RF_Y - 8.0, pcbnew.B_SilkS, 0.9, 0.16, mirror=True); text("SMA %s" % nm, x, RF_JY + 6.0, pcbnew.F_SilkS, 0.85, 0.15)
# ---------------------------------------------------------------- D8 mezzanine site
rect(MEZZ_RECT, pcbnew.F_SilkS, 0.12)
text("D8 MEZZANINE SITE  100 x 80", 50.0, 3.0, pcbnew.F_SilkS, 1.4, 0.22)
text("SA868 exciter, LPF, T/R relay, USB codec set, PTT and EMCON logic on 4x M3 (32.56); the PA module is on the face plate", 50.0, 0.0, pcbnew.F_SilkS, 0.9, 0.16)
for (x, y) in MEZZ_HOLES:
    hole("H%d" % n, x, y, 3.2, "M3 standoff, mezzanine"); n += 1
place("Connector_IDC", "IDC-Header_2x08_P2.54mm_Vertical", "J_MEZZ1", J_MEZZ[0], J_MEZZ[1], "mezzanine harness 2x8", rot=0)   # along Y beside the mezzanine (its shroud is 29 mm long)
text("J_MEZZ1", J_MEZZ[0] - 8.0, J_MEZZ[1], pcbnew.F_SilkS, 1.0, 0.18, angle=90)
text("J_MEZZ_PWR1 VH2 (5 V)", J_MEZZ_PWR[0], J_MEZZ_PWR[1] + 7.0, pcbnew.F_SilkS, 0.9, 0.16)
rect((J_AB[0] - 5.5, J_AB[1] - 21.0, J_AB[0] + 5.5, J_AB[1] + 21.0), pcbnew.Dwgs_User, 0.1); text("J_AB1 2x13 -> B16 underside (113, -46)", J_AB[0] - 9.0, J_AB[1], pcbnew.Dwgs_User, 0.9, 0.15, angle=90)
text("F1 25 A", FUSE_SITE[0], FUSE_SITE[1] + 8.0, pcbnew.Dwgs_User, 0.9, 0.15)
# ---------------------------------------------------------------- datum + legends
line(-4, 0, 4, 0, pcbnew.Dwgs_User); line(0, -4, 0, 4, pcbnew.Dwgs_User); text("CASE DATUM (0,0)", 0, -6.0, pcbnew.Dwgs_User, 1.1, 0.18)
text("MESHSAT FIELD KIT  -  PCB-A POWER + I/O  -  REV A (A22)", 50, 76.5, pcbnew.F_SilkS, 2.2, 0.35)
text("MESHSAT-830  |  240 x 160 x 1.6 mm FR-4, 4 layers  |  matte black  |  2026-09-07", 50, 73.3, pcbnew.F_SilkS, 1.1, 0.18)
text("BACK WALL (+Y)", -30, 77.0, pcbnew.F_SilkS, 1.4, 0.22); text("FRONT WALL (-Y)   v v v", 30, -78.5, pcbnew.F_SilkS, 1.3, 0.22)
text("PORT (-X)", -hx + 5.0, 20, pcbnew.F_SilkS, 1.2, 0.2, angle=90); text("STARBOARD (+X)", hx - 5.0, -60, pcbnew.F_SilkS, 1.2, 0.2, angle=90)
text("PCB-A UNDERSIDE - 13.4 mm above the dock strip E6; the dock block pins and eleven SMP-MAX receptacles land on the dock", 30, -76.0, pcbnew.B_SilkS, 1.4, 0.25, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes:", n - 1)
