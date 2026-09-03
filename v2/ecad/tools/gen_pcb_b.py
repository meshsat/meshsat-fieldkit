#!/usr/bin/env python3
"""Generate PCB-B COMPUTE (MeshSat field-kit carrier, Rev A) - MECHANICAL + PLACEMENT layer.

Case-centred frame as in the geometry appendix (+Y = case back wall). Millimetres.
Phase B1: outline, rod holes + nut keep-outs, every COTS site with its real hole pattern,
cradle slots for the USB sticks, ribbon header, DCF77 connector, pass-throughs, reserved
hub / eFuse / monitor zone. Phase B2 adds the schematic-driven copper.

Sources: appendix s.2/3/6 (outline, rods, CAD device rectangles); CAD _PORTS map (Pi USB
face, X1202 USB-C IN on the south edge); Raspberry Pi 5 hole pattern 58 x 49 at 3.5 mm
from the edges; RockBLOCK 9603 drawing (45 x 45, 2x Ø2.5 at 3.15 from the edges, 38.7 apart);
RockBLOCK 9704 STEP (52.0 x 47.8, no holes, ACC-RB9704SMA-MOUNT bracket 52 x 56 with 4x Ø4.6
on 32 x 32); LilyGO T-Call A767X drawing (74.78 x 29.01, 4x Ø3 on 69.46 x 24.97); Seeed
Wio-SX1262 for XIAO STEP (17.78 x 21.44, one Ø2.2 hole 3.76 mm from a short edge); RTL-SDR
Blog V4 69 x 27 x 13 body; Sonoff ZBDongle-P 87 x 25.5 x 13.5 incl. plug; LimeSDR Mini 2.0 STEP
(69.0 x 31.37 PCB, USB 3.0 A plug centred on the width, RX/TX SMA at the far end, 11 mm tall);
LilyGO T-Beam 1W STEP H768-01 (PCB 43.06 x 116.75, holes Ø3.5 (32.18,113.66) Ø3 (-0.30,102.42)
Ø3 (35.20,83.92) Ø2 (2.62,3.00) Ø2 (32.28,2.99) in the PCB frame, SMA on the right of the top
edge, USB-C on the left edge at y 60.5..69.4, battery plate and shell hang 10 mm below the PCB
and are NOT fitted). Owner rulings R2 (hub per board), R4/R17 (Z), R11 (dual RockBLOCK site),
2026-09-02; re-layout B4 (owner go 2026-09-02): T-Beam 1W strip on the east edge, SDR bay dual
RTL-SDR / LimeSDR, ZigBee to the north band, RockBLOCK site west, pass-through south.
"""
import math, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-b-compute.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 245.0, 170.0, 5.0
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

# ---------------------------------------------------------------- sites (case frame)
# Pi 5 + X1202 stack: Pi long axis along Y, centred (-78.5, 0); Pi holes 3.5 mm in from the Pi edges
STACK_C = (-88.5, 0.0)                          # B11: 10 mm west of B10 so the X1202 extension clears J_RTL1
PI_RECT = (-116.5, -42.5, -60.5, 42.5)          # 56 x 85; HDMI long edge west, GPIO header edge east, SD-card end south
X1202_RECT = (-117.2, -42.5, -21.2, 42.5)       # B11: Geekworm X1202 V1.1 DXF (vendor/x1202): 96 x 85, the Pi flush on its west long edge (0.7 mm), 39.3 mm of board past the header edge; cells hang underneath to board level
STACK_HOLES = [(STACK_C[0] + dx, STACK_C[1] + dy) for dx in (-24.5, 24.5) for dy in (-29.0, 29.0)]   # 49 x 58, Ø2.7
# GPIO ribbon breakout, 2x20 IDC box header, pins along Y
J_GPIO = (-51.0, 48.5)                          # B11: north of the stack, pins along X (the B10 spot is under the X1202)
# SDR bay, dual: RTL-SDR Blog V4 (69 x 27 x 13) or LimeSDR Mini 2.0 (69 x 31.4 x 11). Both have the USB-A plug
# centred on one short end (points -X into the receptacle) and the SMA(s) on the other. Bay 84 x 32 on centreline Y 0.
SDR_RECEPT = (-12.0, 0.0)                       # receptacle centre, opening faces +X
SDR_RECT = (-4.0, -16.0, 78.0, 16.0)
SDR_SLOTS = [(20.0, -18.0), (74.0, -18.0), (20.0, 18.0), (66.0, 18.0)]   # tie-wrap slots 5 x 1.8
# Sonoff ZBDongle-P in the north band: body ~70 x 25.5 at X -40..30, plug points +X, receptacle at the east end
ZB_RECT = (-40.0, 55.0, 30.0, 80.5)
ZB_RECEPT = (38.0, 67.75)                       # opening faces -X
ZB_SLOTS = [(-10.0, 52.5), (18.0, 52.5), (-10.0, 82.0), (18.0, 82.0)]   # B11: the west pair east of the ribbon header
# LilyGO T-Call A7670E V1.0: 74.78 x 29.01, 4x Ø3.0 on 69.46 x 24.97; USB-C at the west end (CAD)
TCALL_C = (39.39, 35.5)
TCALL_RECT = (TCALL_C[0] - 37.39, TCALL_C[1] - 14.505, TCALL_C[0] + 37.39, TCALL_C[1] + 14.505)
TCALL_HOLES = [(TCALL_C[0] + dx, TCALL_C[1] + dy) for dx in (-34.73, 34.73) for dy in (-12.485, 12.485)]
TCALL_USBC = (-16.0, 46.0)                      # pigtail header (JST-PH), cable to the T-Call USB-C at its west end
# Seeed Wio-SX1262 + XIAO ESP32S3: 21.44 x 17.78, one Ø2.2 hole 3.76 mm from the west short edge; USB-C east
XIAO_C = (-93.0, 58.0)
XIAO_RECT = (XIAO_C[0] - 10.72, XIAO_C[1] - 8.89, XIAO_C[0] + 10.72, XIAO_C[1] + 8.89)
XIAO_HOLE = (XIAO_C[0] - 10.72 + 3.76, XIAO_C[1])
XIAO_SLOTS = [(-88.0, 46.0), (-88.0, 70.0)]
XIAO_USBC = (-76.0, 60.0)                       # B11: 2 mm north, clear of the ribbon header
# LilyGO T-Beam 1W (alternative LoRa radio, one of XIAO / T-Beam fitted): strip on the east edge, long axis Y,
# component side up, SMA end north (SMA at the NE corner, Y to 67.2: use a RIGHT-ANGLE SMA plug on the pigtail),
# USB-C on its west edge at Y -3.5..5.4 (right-angle USB-C plug), ON/OFF slide switch on its west edge at Y -18..-12.
# Fitted BARE: no battery plate, no shell (both hang 10 mm below the PCB). Five standoffs: 3x M2.5, 2x M2, 6 mm.
TB_X0, TB_Y0 = 79.3, -64.0                      # carrier position of the T-Beam PCB's SW corner (STEP face min corner)
def tb(sx, sy): return (TB_X0 + 4.08 + sx, TB_Y0 - 0.03 + sy)   # T-Beam PCB frame (STEP) -> carrier frame
TB_RECT = (TB_X0, TB_Y0, TB_X0 + 43.06, TB_Y0 + 116.75)
TB_HOLES_M25 = [tb(32.18, 113.66), tb(-0.30, 102.42), tb(35.20, 83.92)]   # Ø3.5, Ø3, Ø3 on the module
TB_HOLES_M2 = [tb(2.62, 3.00), tb(32.28, 2.99)]                           # Ø2 on the module
TB_SMA = (tb(27.57, 116.78), tb(36.81, 131.25))                           # SMA body beyond the PCB end
TB_USBC = (tb(-4.97, 60.50), tb(2.60, 69.44))
TB_PINROWS = [(tb(-4.0, 2.5), tb(-1.3, 41.2)), (tb(36.2, 2.5), tb(38.9, 41.2))]   # header pin rows: top-side copper keep-out
J_TBEAM = (70.0, 55.0)                          # JST-PH 4-pin pigtail header for the T-Beam USB-C (CH3, parallel to J_XIAO1)
# RockBLOCK dual site centred (52, -48): 9704 on the GC bracket (4x Ø4.6 on 32 x 32), 9603 offset +6 in Y
RB_C = (52.0, -48.0)
RB9704_RECT = (RB_C[0] - 26.0, RB_C[1] - 28.0, RB_C[0] + 26.0, RB_C[1] + 28.0)      # bracket 52 x 56
RB9704_HOLES = [(RB_C[0] + dx, RB_C[1] + dy) for dx in (-16.0, 16.0) for dy in (-16.0, 16.0)]
RB9603_C = (52.0, -42.0)
RB9603_RECT = (RB9603_C[0] - 22.5, RB9603_C[1] - 22.5, RB9603_C[0] + 22.5, RB9603_C[1] + 22.5)
RB9603_HOLES = [(RB9603_C[0] - 19.35, RB9603_C[1] + 22.5 - 3.15), (RB9603_C[0] + 19.35, RB9603_C[1] + 22.5 - 3.15)]
# DCF77 remote-mount connector, JST-XH 4-pin, north edge
J_DCF77 = (-85.0, 77.0)
# hub / eFuse / monitor zone (schematic phase), south-west, with the upstream USB-C and the A-B header
HUB_ZONE = (-96.0, -81.0, -46.0, -52.0)
J_5V_IN = (-52.0, -56.0)                        # XH2.54 2-pin from the X1202 5 V output
J_USB_UP = (-48.0, -66.0)                       # USB-C receptacle, upstream to a Pi port, opening faces +X
J_AB = (-72.0, -78.0)                           # 2x7 IDC on the UNDERSIDE, ribbon down to PCB-A
PASS_CENTRE = (-13.0, -50.0, 15.0)              # Ø15 general pass-through (moved south-west in B4)

# ---------------------------------------------------------------- plumbing (as PCB-C)
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-B COMPUTE"); tb.SetRevision("A")
tb.SetDate("2026-09-02"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-709. Case-centred frame. B11: real X1202 envelope (Geekworm DXF), stack 10 mm west, module rail from PCB-A. tools/gen_pcb_b.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.45), ("m_MinThroughDrill", 0.25),
                  ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.25), ("m_SolderMaskMinWidth", 0.1)):
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
rounded_rect(-hx, -hy, hx, hy, BOARD_R, pcbnew.Edge_Cuts)
for i, (x, y) in enumerate(ROD_HOLES, 1):
    hole("H%d" % i, x, y, 3.2, "M3 rod R%d" % i)
    for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS): circle(x, y, NUT_KEEPOUT_D, layer, 0.15)
    rule_area_annulus(x, y, NUT_KEEPOUT_D, ROD_DRILL + 3.0, "nut keep-out R%d" % i)
    text("R%d" % i, x, y + 7.0, pcbnew.F_SilkS, 1.5, 0.25)
# pass-throughs (Edge.Cuts)
circle(PASS_CENTRE[0], PASS_CENTRE[1], PASS_CENTRE[2], pcbnew.Edge_Cuts)
keepout_circle(PASS_CENTRE[0], PASS_CENTRE[1], PASS_CENTRE[2] + 2.0, "keep-out: centre pass-through")

# ---------------------------------------------------------------- stack
n = 5
for (x, y) in STACK_HOLES:
    hole("H%d" % n, x, y, 2.7, "M2.5 standoff, Pi/X1202 stack"); n += 1
rect(X1202_RECT, pcbnew.F_SilkS, 0.12); rect(PI_RECT, pcbnew.Dwgs_User, 0.1)
text("X1202 V1.1 96x85 + Pi 5 + cooler on 4x M2.5x22 (49x58); Pi HDMI edge WEST, header edge EAST, SD card SOUTH", STACK_C[0] + 19.5, 40.0, pcbnew.F_SilkS, 0.9, 0.16)
text("NO PART under the X1202 (cells at board level); DC jack NE corner faces +X; USB-A sockets overhang south 9 mm", STACK_C[0] + 19.5, -40.0, pcbnew.F_SilkS, 0.9, 0.16)
# ribbon header
place("Connector_IDC", "IDC-Header_2x20_P2.54mm_Vertical", "J_GPIO1", J_GPIO[0], J_GPIO[1], "Pi 5 GPIO ribbon 2x20", rot=90)
text("Pi 40-pin ribbon", J_GPIO[0], J_GPIO[1] + 7.5, pcbnew.F_SilkS, 1.2, 0.2)
# SDR bay (RTL-SDR V4 or LimeSDR Mini 2.0)
site(SDR_RECT, "SDR BAY: RTL-SDR Blog V4 (69 x 27) or LimeSDR Mini 2.0 (69 x 31.4)", "USB-A plug -> receptacle west; SMA east -> SDR bulkhead (Lime: RX + TX, 2 bulkheads)", lx=36.0, ly=0.0)
for i, (x, y) in enumerate(SDR_SLOTS): slot("S_RTL%d" % (i + 1), x, y, 5.0, 1.8)
usb_a = place("Connector_USB", "USB_A_Stewart_SS-52100-001_Horizontal", "J_RTL1", SDR_RECEPT[0], SDR_RECEPT[1], "USB-A receptacle, SDR", rot=90)
if usb_a is None: rect((SDR_RECEPT[0] - 7, SDR_RECEPT[1] - 7.5, SDR_RECEPT[0] + 7, SDR_RECEPT[1] + 7.5), pcbnew.F_SilkS, 0.15)
text("J_RTL1", SDR_RECEPT[0], SDR_RECEPT[1] + 9.5, pcbnew.F_SilkS, 1.0, 0.18)
# ZigBee (north band)
site(ZB_RECT, "SONOFF ZBDongle-P  CC2652P", "plug east -> receptacle; antenna west (2.4 GHz, in-case)", ly=67.75)
for i, (x, y) in enumerate(ZB_SLOTS): slot("S_ZB%d" % (i + 1), x, y, 5.0, 1.8)
usb_b = place("Connector_USB", "USB_A_Stewart_SS-52100-001_Horizontal", "J_ZB1", ZB_RECEPT[0], ZB_RECEPT[1], "USB-A receptacle, ZigBee", rot=-90)
if usb_b is None: rect((ZB_RECEPT[0] - 7, ZB_RECEPT[1] - 7.5, ZB_RECEPT[0] + 7, ZB_RECEPT[1] + 7.5), pcbnew.F_SilkS, 0.15)
text("J_ZB1", ZB_RECEPT[0], ZB_RECEPT[1] - 9.5, pcbnew.F_SilkS, 1.0, 0.18)
# T-Call
site(TCALL_RECT, "LILYGO T-Call A7670E (V1.0 / V1.1, one outline)  74.78 x 29.01", "4x M3 on 69.46 x 24.97; USB-C west; LTE pigtail -> LTE bulkhead")
for (x, y) in TCALL_HOLES:
    hole("H%d" % n, x, y, 3.2, "M3, T-Call corner"); n += 1
# T-Beam 1W strip (alternative to the XIAO)
rect(TB_RECT, pcbnew.F_SilkS, 0.12)
text("LILYGO T-BEAM 1W (alt. LoRa)", TB_X0 + 21.5, -6.0, pcbnew.F_SilkS, 1.3, 0.22, angle=90)
text("bare PCB + fan, 5 standoffs 6 mm; SMA N (right-angle plug); USB-C W", TB_X0 + 25.5, -6.0, pcbnew.F_SilkS, 0.9, 0.16, angle=90)
for (x, y) in TB_HOLES_M25:
    hole("H%d" % n, x, y, 2.7, "M2.5 standoff, T-Beam 1W"); n += 1
for (x, y) in TB_HOLES_M2:
    hole("H%d" % n, x, y, 2.2, "M2 standoff, T-Beam 1W"); n += 1
rect((TB_SMA[0][0], TB_SMA[0][1], TB_SMA[1][0], TB_SMA[1][1]), pcbnew.Dwgs_User, 0.1); text("SMA", (TB_SMA[0][0] + TB_SMA[1][0]) / 2, TB_SMA[1][1] + 1.5, pcbnew.Dwgs_User, 0.8, 0.15)
rect((TB_USBC[0][0], TB_USBC[0][1], TB_USBC[1][0], TB_USBC[1][1]), pcbnew.Dwgs_User, 0.1); text("USB-C", TB_USBC[0][0] - 4.0, (TB_USBC[0][1] + TB_USBC[1][1]) / 2, pcbnew.Dwgs_User, 0.8, 0.15)
for (a, b) in TB_PINROWS:
    keepout_rect(a[0], a[1], b[0], b[1], "keep-out: T-Beam header pins")
    rect((a[0], a[1], b[0], b[1]), pcbnew.Dwgs_User, 0.1)
text("J_TBEAM1 pigtail", J_TBEAM[0], J_TBEAM[1] + 5.0, pcbnew.F_SilkS, 1.0, 0.18)
text("J_PANEL ribbon up to PCB-C", 86.0, 75.5, pcbnew.F_SilkS, 0.9, 0.16)
# XIAO + Wio-SX1262
site(XIAO_RECT, "XIAO ESP32S3 + Wio-SX1262", "1x M2 + tie slots; u.FL -> LoRa bulkhead", lx=-62.0, ly=44.5)
hole("H%d" % n, XIAO_HOLE[0], XIAO_HOLE[1], 2.2, "M2 standoff, Wio-SX1262"); n += 1
for i, (x, y) in enumerate(XIAO_SLOTS): slot("S_XIAO%d" % (i + 1), x, y, 5.0, 1.8)
text("J_XIAO1 pigtail", XIAO_USBC[0], XIAO_USBC[1] + 7.5, pcbnew.F_SilkS, 1.0, 0.18)
# RockBLOCK dual site
rect(RB9704_RECT, pcbnew.F_SilkS, 0.12); rect(RB9603_RECT, pcbnew.Dwgs_User, 0.1)
text("ROCKBLOCK SITE", RB_C[0], RB_C[1] + 2.0, pcbnew.F_SilkS, 1.4, 0.22)
text("9704 on GC mount (4x M4, 32x32)", RB_C[0], RB_C[1] - 1.5, pcbnew.F_SilkS, 1.0, 0.18)
text("9603 direct (2x M2.5, 38.7)", RB_C[0], RB_C[1] - 4.5, pcbnew.F_SilkS, 1.0, 0.18)
for (x, y) in RB9704_HOLES:
    hole("H%d" % n, x, y, 4.3, "M4, GC 9704 bracket"); n += 1
for (x, y) in RB9603_HOLES:
    hole("H%d" % n, x, y, 2.7, "M2.5, RockBLOCK 9603"); n += 1
# DCF77
place("Connector_JST", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "J_DCF77", J_DCF77[0], J_DCF77[1], "DCF77 remote: 3V3 GND T P1")
text("DCF77: 3V3 GND T P1", -66.0, 82.5, pcbnew.F_SilkS, 0.9, 0.16)
# hub zone (reserved)
rect(HUB_ZONE, pcbnew.Dwgs_User, 0.15)
text("HUB / eFUSE / MONITOR ZONE  (phase B2: 4-port USB 2.0 hub, 4x eFuse, INA3221 x2, PCA9554)", (HUB_ZONE[0] + HUB_ZONE[2]) / 2, HUB_ZONE[3] + 2.5, pcbnew.Dwgs_User, 1.1, 0.2)
rect((J_5V_IN[0] - 4, J_5V_IN[1] - 3, J_5V_IN[0] + 4, J_5V_IN[1] + 3), pcbnew.Dwgs_User, 0.1); text("J_5V_IN XH", J_5V_IN[0], J_5V_IN[1] - 5, pcbnew.Dwgs_User, 0.9, 0.15)
rect((J_USB_UP[0] - 4.5, J_USB_UP[1] - 4, J_USB_UP[0] + 4.5, J_USB_UP[1] + 4), pcbnew.Dwgs_User, 0.1); text("J_USB_UP1", J_USB_UP[0], J_USB_UP[1] - 6, pcbnew.Dwgs_User, 0.9, 0.15)
text("J_AB1 2x7 to PCB-A (underside)", J_AB[0], J_AB[1] + 8.0, pcbnew.B_SilkS, 0.9, 0.15, mirror=True)
# datum + legends
line(-4, 0, 4, 0, pcbnew.Dwgs_User); line(0, -4, 0, 4, pcbnew.Dwgs_User); text("CASE DATUM (0,0)", 0, -6.0, pcbnew.Dwgs_User, 1.1, 0.18)
text("PCB-B COMPUTE  REV A (B11)", 70, -79.0, pcbnew.F_SilkS, 1.6, 0.26)
text("MESHSAT-709 | 245x170x1.6 4L | matte black | 2026-09-04", 70, -82.5, pcbnew.F_SilkS, 1.1, 0.18)
text("BACK WALL (+Y)", -10, 83.0, pcbnew.F_SilkS, 1.2, 0.2); text("FRONT WALL (-Y)   v v v", -100, -83.2, pcbnew.F_SilkS, 1.5, 0.25)
text("PORT (-X)", -hx + 5.5, 20, pcbnew.F_SilkS, 1.2, 0.2, angle=90); text("STARBOARD (+X)", hx - 6.0, 0, pcbnew.F_SilkS, 1.2, 0.2, angle=90)
text("PCB-B UNDERSIDE - faces PCB-A", 0, -hy + 9.0, pcbnew.B_SilkS, 1.6, 0.25, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes:", n - 1)
