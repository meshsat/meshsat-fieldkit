#!/usr/bin/env python3
"""Generate PCB-A POWER + I/O (MeshSat field-kit carrier, Rev A) - MECHANICAL + PLACEMENT layer (phase A1).

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
Blog V4 69 x 27 x 13 body; Sonoff ZBDongle-P 87 x 25.5 x 13.5 incl. plug. Owner rulings R2
(hub per board), R4/R17 (Z), R11 (dual RockBLOCK site), 2026-09-02.
"""
import math, sys
import pcbnew
from pcbnew import VECTOR2I, FromMM

OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-a-power.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 285.0, 160.0, 5.0
BOARD_X0 = -165.0                  # A15: the board grows 45 mm to port for the welded 1S8P pack; the rods stay at (+-110.5, +-73)
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
# A19 (appendix 32.17, 32.22, 32.23): no pack on the board; the battery module on the floor reaches this board over the dock block
POWER_ZONE = (-162.0, -40.0, -32.0, 2.0)     # charger, gauge, three converters and their fuse row (former pack area)
CTRL_ZONE = (-162.0, 2.0, -118.0, 36.0)     # main power control, heating-pad switch, 3.3 V buck
RF_SITES = [(-100.0, -56.0, "UHF"), (-84.0, -56.0, "WIFI 2.4"), (-26.0, -56.0, "WIFI 5.8"), (-12.0, -56.0, "SDR"), (70.0, -74.0, "LTE"), (92.0, -74.0, "IRIDIUM"), (103.0, -54.0, "LORA")]   # SMP-MAX receptacles on the underside at Y -66; SMA jacks on top at the given Y (south of the GPS puck for the two under it)
RF_Y = -66.0
DOCK_BLOCK = (-155.0, -76.0, -116.0, -64.0)   # A19's own pin field: 2x6 signal pins J_DOCK at (-124, -70), 9 A power pins at X -147..-135, pre-charge at (-151, -70); 5.5 mm from the rod nut at (-110.5, -73). The block board below is larger (43 x 25, gen_pcb_e5.py) and reaches X -115, still 4.5 mm clear of that rod.
# APRS mezzanine site (R3): 80 x 62 on four M3 standoffs, harness headers on its west side
MEZZ_RECT = (5.0, -31.0, 85.0, 31.0)
MEZZ_HOLES = [(10.0, -26.0), (80.0, -26.0), (10.0, 26.0), (80.0, 26.0)]
J_MEZZ = (-8.0, 8.0)          # 2x8 IDC: USB pairs for codec + UART, PTT/TR, EN, GND, 5V logic
J_MEZZ_PWR = (-8.0, -18.0)    # JST-VH 2-pin: raw cell node + GND to the 8 V boost (R15)
# GPS puck (u-blox Gmouse, captive USB cable): bracket slots + receptacle + cable tie-downs
GPS_RECT = (50.0, -65.0, 90.0, -39.0)
GPS_SLOTS = [(58.0, -70.0), (82.0, -70.0), (48.0, -36.0), (92.0, -36.0)]
J_GPS = (30.0, -52.0)         # USB-A receptacle, opening +X
GPS_COIL_SLOTS = [(100.0, -42.0), (100.0, -50.0), (100.0, -58.0)]   # A19: 2 mm north so the LORA blind-mate site clears them
# WiFi Alfa AWUS036ACM: body 85 x 26 + USB-A 3.0 plug west; two RP-SMA east -> two WiFi bulkheads (R16)
WIFI_RECT = (20.0, 39.5, 105.0, 65.5)
WIFI_SLOTS = [(45.0, 36.0), (85.0, 36.0), (45.0, 69.0), (85.0, 69.0)]
J_WIFI = (8.0, 52.5)          # USB-A receptacle, opening +X
# power connectors
J_AB = (-72.0, -66.0)         # 2x9 IDC top side (A20), ribbon up to PCB-B's underside header at (-72, -78)
J_LEDS = (-38.0, -74.0)       # XH 1x10: five front-wall LEDs (R5); A20: 2 mm east of the A19 spot, clear of the 2x9 J_AB1 box header
HUB_ZONE = (-104.0, 25.0, -30.0, 77.0)     # A19: seven-port hub, five eFuse + INA219 channels, PCA9555 0x21 and 0x24, LED drivers (grown south into the former pack area)
BANK_ZONE = (-70.0, -72.0, -30.0, -46.0)    # A19: charger BQ25792 zone, next to the 12 V dock pins and the node bar
# ---------------------------------------------------------------- plumbing (as PCB-C)
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-B COMPUTE"); tb.SetRevision("A")
tb.SetDate("2026-09-02"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-709. Case-centred frame. Phase B1 mechanical + placement. tools/gen_pcb_b.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.45), ("m_MinThroughDrill", 0.2),
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
rounded_rect(BOARD_X0, -hy, BOARD_X0 + BOARD_L, hy, BOARD_R, pcbnew.Edge_Cuts)
for i, (x, y) in enumerate(ROD_HOLES, 1):
    hole("H%d" % i, x, y, 3.2, "M3 rod R%d" % i)
    for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS): circle(x, y, NUT_KEEPOUT_D, layer, 0.15)
    rule_area_annulus(x, y, NUT_KEEPOUT_D, ROD_DRILL + 3.0, "nut keep-out R%d" % i)
    text("R%d" % i, x, y + 7.0 if y < 0 else y - 7.0, pcbnew.F_SilkS, 1.5, 0.25)
n = 5
# ---------------------------------------------------------------- A19 power zone, dock block, RF sites
rect(POWER_ZONE, pcbnew.Dwgs_User, 0.15); text("POWER ZONE (A19): fuse row F3 F4 F5 F2 at Y -46, converters M1 M2 PI north of it, gauge by the pins", (POWER_ZONE[0] + POWER_ZONE[2]) / 2, POWER_ZONE[3] + 2.5, pcbnew.Dwgs_User, 1.0, 0.18)
rect(CTRL_ZONE, pcbnew.Dwgs_User, 0.15); text("MAIN POWER CONTROL, HEATING PAD SWITCH, 3.3 V BUCK", (CTRL_ZONE[0] + CTRL_ZONE[2]) / 2, CTRL_ZONE[3] + 2.5, pcbnew.Dwgs_User, 1.0, 0.18)
rect(DOCK_BLOCK, pcbnew.Dwgs_User, 0.15); text("DOCK BLOCK (underside): J_DOCK 2x6 signal pins + 9 A power pins + pre-charge pin, land on the dock block", (DOCK_BLOCK[0] + DOCK_BLOCK[2]) / 2, DOCK_BLOCK[1] - 2.5, pcbnew.Dwgs_User, 1.0, 0.18)
text("BATTERY MODULE ON THE CASE FLOOR (32.22): 12 x Samsung 35E 1S12P 42 Ah, BMS 30 A, over the dock block pins", -97.0, -78.0, pcbnew.F_SilkS, 1.1, 0.18)
for (x, sy, nm) in RF_SITES:
    circle(x, RF_Y - 2.0 if nm == "LORA" else RF_Y, 12.0, pcbnew.Dwgs_User, 0.1); circle(x, RF_Y - 2.0 if nm == "LORA" else RF_Y, 8.3, pcbnew.B_SilkS, 0.12)
    text("BM %s" % nm, x, RF_Y - 8.0, pcbnew.B_SilkS, 1.0, 0.18, mirror=True); text("SMA %s" % nm, x, sy + 6.0 if sy > -70 else sy - 5.5, pcbnew.F_SilkS, 0.9, 0.16)
# ---------------------------------------------------------------- APRS mezzanine site
rect(MEZZ_RECT, pcbnew.F_SilkS, 0.12)
text("APRS MEZZANINE SITE  80 x 62", 45.0, 3.0, pcbnew.F_SilkS, 1.4, 0.22)
text("DMR858M + 8 V boost + codec + UART on 4x M3 (R3)", 45.0, 0.0, pcbnew.F_SilkS, 1.0, 0.18)
text("SMA -> UHF bulkhead (+128.75, +25, +25)", 45.0, -3.0, pcbnew.F_SilkS, 1.0, 0.18)
for (x, y) in MEZZ_HOLES:
    hole("H%d" % n, x, y, 3.2, "M3 standoff, mezzanine"); n += 1
place("Connector_IDC", "IDC-Header_2x08_P2.54mm_Vertical", "J_MEZZ1", J_MEZZ[0], J_MEZZ[1], "mezzanine harness 2x8", rot=0)
text("J_MEZZ1", J_MEZZ[0] - 8.0, J_MEZZ[1], pcbnew.F_SilkS, 1.0, 0.18, angle=90)
text("J_MEZZ_PWR VH2 (cell node)", J_MEZZ_PWR[0], J_MEZZ_PWR[1] + 7.0, pcbnew.F_SilkS, 1.0, 0.18)
# ---------------------------------------------------------------- A20: the GPS puck and the WiFi dongle sites are gone (GNSS and WiFi live on B13's module); their floor stays free
# ---------------------------------------------------------------- power connectors, interconnect, LEDs
rect((J_AB[0] - 13.5, J_AB[1] - 5.5, J_AB[0] + 13.5, J_AB[1] + 5.5), pcbnew.Dwgs_User, 0.1); text("J_AB1 2x9 -> PCB-B underside (-72,-78)", J_AB[0], J_AB[1] + 8.0, pcbnew.Dwgs_User, 0.9, 0.15)
rect((J_LEDS[0] - 13.0, J_LEDS[1] - 3.0, J_LEDS[0] + 13.0, J_LEDS[1] + 3.0), pcbnew.Dwgs_User, 0.1); text("J_LEDS XH1x10 -> front-wall LED row (R5)", J_LEDS[0], J_LEDS[1] + 5.0, pcbnew.Dwgs_User, 0.9, 0.15)
rect(HUB_ZONE, pcbnew.Dwgs_User, 0.15); text("CONTROL ZONE (A20): wall-port eFuse + INA219, PCA9555 0x21 + 0x24, LED drivers (the hub went to B13)", (HUB_ZONE[0] + HUB_ZONE[2]) / 2, HUB_ZONE[3] + 2.5, pcbnew.Dwgs_User, 1.0, 0.18)
rect(BANK_ZONE, pcbnew.Dwgs_User, 0.15); text("CHARGER ZONE (A19): BQ25792 from the dock 12 V into the node, JEITA on the module thermistor", (BANK_ZONE[0] + BANK_ZONE[2]) / 2, BANK_ZONE[1] - 2.5, pcbnew.Dwgs_User, 1.0, 0.18)
# ---------------------------------------------------------------- datum + legends
line(-4, 0, 4, 0, pcbnew.Dwgs_User); line(0, -4, 0, 4, pcbnew.Dwgs_User); text("CASE DATUM (0,0)", 0, -6.0, pcbnew.Dwgs_User, 1.1, 0.18)
text("MESHSAT FIELD KIT  -  PCB-A POWER + I/O  -  REV A (A19)", 48, 76.5, pcbnew.F_SilkS, 2.2, 0.35)
text("MESHSAT-709 / 789  |  285 x 160 x 1.6 mm FR-4, 4 layers  |  matte black  |  2026-09-04", 48, 73.3, pcbnew.F_SilkS, 1.1, 0.18)
text("BACK WALL (+Y)", -20, 77.0, pcbnew.F_SilkS, 1.4, 0.22); text("FRONT WALL (-Y)   v v v", 20, -76.0, pcbnew.F_SilkS, 1.3, 0.22)
text("PORT (-X)", -hx + 5.0, 0, pcbnew.F_SilkS, 1.2, 0.2, angle=90); text("STARBOARD (+X)", hx - 5.0, 0, pcbnew.F_SilkS, 1.2, 0.2, angle=90)
text("PCB-A UNDERSIDE - 13.4 mm above the dock strip (32.21); dock block pins and seven SMP-MAX receptacles land on the dock", 45, -76.0, pcbnew.B_SilkS, 1.5, 0.25, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes:", n - 1)
