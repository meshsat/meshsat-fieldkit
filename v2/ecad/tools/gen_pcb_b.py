#!/usr/bin/env python3
"""Generate PCB-B COMPUTE (MeshSat field-kit carrier, Rev A) - MECHANICAL + PLACEMENT layer.

Case-centred frame as in the geometry appendix (+Y = case back wall). Millimetres.
Phase B1: outline, rod holes + nut keep-outs, every COTS site with its real hole pattern,
cradle slots for the USB stick, pass-through, the reserved zones. Phase B2 adds the schematic-driven copper.

B13 (appendix 32.35, MESHSAT-795): the Raspberry Pi 5 on standoffs is replaced by a Compute Module 5
site (55 x 40 module on two Amphenol 10164227-1004A1RLF, 4.0 mm stack, four M2.5 holes on 33 x 48; the
CM5 Cooler 41 x 56 x 12.7 over it; footprint from the CM5IO design files, appendix 32.35 and vendor/cm5/).
The T-Call, XIAO, T-Beam and ZigBee dongle sites, the 40-pin ribbon header, the two upstream USB-C
receptacles and the pigtail headers are gone. New sites: the mini PCIe LTE card (30 x 50.95 full-size
card on its socket, north band), the nano-SIM holder, the NEO-M9N GNSS module with its U.FL, the
Wio-SX1262 LoRa module, the E72-2G4M20S1E ZigBee module (east strip, PCB antenna to the back wall),
the 22-pin display FPC, the RTC cell holder, the fan header, the flashing USB-C on the south edge.
Kept from B12: outline 245 x 170, rods, SDR bay (RTL-SDR Blog V4 69 x 27 x 13 or LimeSDR Mini 2.0
69.0 x 31.37), RockBLOCK dual site (9603 drawing 45 x 45, 2x Ø2.5 at 3.15 from the edges, 38.7 apart;
9704 STEP 52.0 x 47.8 on the ACC-RB9704SMA-MOUNT bracket 52 x 56 with 4x Ø4.6 on 32 x 32), the DCF77
connector, the panel ribbon, the pass-through, the three rail leads from PCB-A, J_AB1 underneath.
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
        open(path, "w").write('(footprint "%s"\n\t(version 20241229)\n\t(generator "meshsat")\n\t(generator_version "9.0")\n\t(layer "F.Cu")\n\t(descr "NPTH slot %g x %g mm for a cable tie or strap")\n\t(attr exclude_from_pos_files exclude_from_bom)\n\t(pad "" np_thru_hole roundrect (at 0 0) (size %g %g) (drill oval %g %g) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.5))\n)\n' % (name, w, h, w, h, w, h))
    return name

# ---------------------------------------------------------------- sites (case frame)
# Compute Module 5: module 55 x 40 with the long axis along Y, centred (-88, 0), holes 33 x 48 (M2.5, 3.5 mm inset), connectors along the long edges
# (GPIO connector west, high-speed connector east); the CM5 Cooler 41 x 56 x 12.7 sits on the module. Nothing else inside the cooler outline.
CM5_C = (-88.0, 0.0)
CM5_RECT = (CM5_C[0] - 20.0, CM5_C[1] - 27.5, CM5_C[0] + 20.0, CM5_C[1] + 27.5)
COOLER_RECT = (CM5_C[0] - 20.5, CM5_C[1] - 28.0, CM5_C[0] + 20.5, CM5_C[1] + 28.0)
CM5_HOLES = [(CM5_C[0] + dx, CM5_C[1] + dy) for dx in (-16.5, 16.5) for dy in (-24.0, 24.0)]   # M2.5, 33 x 48 (datasheet 4.1.1)
# SDR bay: receptacle west (RTL-SDR plug faces -X), stick body eastwards, SMA end at the east; tie slots
SDR_RECEPT = (-12.0, 0.0)                       # receptacle centre, opening faces +X
SDR_RECT = (-4.0, -16.0, 78.0, 16.0)
SDR_SLOTS = [(20.0, -18.0), (74.0, -18.0), (20.0, 18.0), (66.0, 18.0)]   # tie-wrap slots 5 x 1.8
# LTE mini PCIe card (north band): socket at the west end, full-size card 30 x 50.95 extending east, two M2.5 standoffs in the socket footprint
LTE_RECT = (-32.0, 52.0, 26.0, 82.0)
WIFI_RECT = (27.0, 49.0, 64.0, 71.0)   # B14: M.2 E-key socket at (34, 60) rot -90, the 2230 card along +X to 64, standoff hole at (62.25, 60); IPEX leads east
# ZigBee module (east strip): E72-2G4M20S1E 28.7 x 17.5, long axis along Y, PCB antenna toward the back wall
ZB_RECT = (84.0, 16.0, 104.0, 52.0)   # the module body plus its 3 mm antenna keep-out; its small parts pack east of it
# RockBLOCK dual site centred (52, -48): 9704 on the GC bracket (4x Ø4.6 on 32 x 32), 9603 offset +6 in Y
RB_C = (52.0, -48.0)
RB9704_RECT = (RB_C[0] - 26.0, RB_C[1] - 28.0, RB_C[0] + 26.0, RB_C[1] + 28.0)      # bracket 52 x 56
RB9704_HOLES = [(RB_C[0] + dx, RB_C[1] + dy) for dx in (-16.0, 16.0) for dy in (-16.0, 16.0)]
RB9603_C = (52.0, -42.0)
RB9603_RECT = (RB9603_C[0] - 22.5, RB9603_C[1] - 22.5, RB9603_C[0] + 22.5, RB9603_C[1] + 22.5)
RB9603_HOLES = [(RB9603_C[0] - 19.35, RB9603_C[1] + 22.5 - 3.15), (RB9603_C[0] + 19.35, RB9603_C[1] + 22.5 - 3.15)]
# DCF77 remote-mount connector, JST-XH 4-pin, north edge
J_DCF77 = (-85.0, 77.0)
# zones of the schematic phase (gen_pcb_b3.py packs the parts into them): hub east of the module, bucks and bench headers south of it, control west
HUB_ZONE = (-66.0, -36.0, -22.0, -12.0)
BUCK_ZONE = (-58.0, -82.0, -36.0, -52.0)
CTRL_ZONE = (-119.5, -64.0, -100.0, -30.0)
J_AB = (-72.0, -78.0)                           # 2x9 IDC on the UNDERSIDE, ribbon down to PCB-A
J_FLASH = (-30.0, -77.5)                        # USB-C on the south edge: rpiboot eMMC flashing only, opening faces -Y
PASS_CENTRE = (-13.0, -50.0, 15.0)              # Ø15 general pass-through

# ---------------------------------------------------------------- plumbing (as PCB-C)
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-B COMPUTE"); tb.SetRevision("A")
tb.SetDate("2026-09-05"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-802. Case-centred frame. B14: M.2 WiFi P2P socket on the CM5 PCIe lane (appendix 32.37) on B13: Compute Module 5 carrier (appendix 32.35), radios on the module's buses, three rails from PCB-A. tools/gen_pcb_b.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.40), ("m_MinThroughDrill", 0.20),   # B13: the 0.4 mm connector rows take 0.40/0.20 vias at the pad tips (the CM5IO scheme)
                  ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.19), ("m_SolderMaskMinWidth", 0.1)):   # hole clearance 0.19 as the CM5IO project (its 0.4 mm rows put a 0.20 drill 0.24 mm from the neighbour track)
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

# ---------------------------------------------------------------- Compute Module 5 site (the two receptacles U30A/U30B are placed by gen_pcb_b3.py; holes and outline here)
n = 5
rect(CM5_RECT, pcbnew.Dwgs_User, 0.1); rect(COOLER_RECT, pcbnew.F_SilkS, 0.12)
for (x, y) in CM5_HOLES:
    hole("H%d" % n, x, y, 2.7, "M2.5 standoff 4.0 mm, CM5"); n += 1
text("COMPUTE MODULE 5 on 2x Amphenol 10164227-1004A1RLF (4.0 mm stack), M2.5 x 4 on 33 x 48; CM5 Cooler 41 x 56 over it", CM5_C[0], CM5_C[1] + 31.5, pcbnew.F_SilkS, 0.9, 0.16)
text("GPIO connector WEST, high-speed connector EAST; U.FL antenna lead to the WiFi bulkhead (dtparam=ant2)", CM5_C[0], CM5_C[1] - 31.5, pcbnew.F_SilkS, 0.9, 0.16)
text("B13: no Pi 5, no ribbon, no USB plug on the compute side (appendix 32.35)", CM5_C[0], CM5_C[1] - 34.5, pcbnew.F_SilkS, 0.9, 0.16)
# SDR bay (RTL-SDR V4 or LimeSDR Mini 2.0)
site(SDR_RECT, "SDR BAY: RTL-SDR Blog V4 (69 x 27) or LimeSDR Mini 2.0 (69 x 31.4)", "USB-A plug -> receptacle west; SMA east -> SDR bulkhead (Lime: RX + TX, 2 bulkheads)", lx=36.0, ly=0.0)
for i, (x, y) in enumerate(SDR_SLOTS): slot("S_RTL%d" % (i + 1), x, y, 5.0, 1.8)
usb_a = place("Connector_USB", "USB_A_Stewart_SS-52100-001_Horizontal", "J_RTL1", SDR_RECEPT[0], SDR_RECEPT[1], "USB-A receptacle, SDR", rot=90)
if usb_a is None: rect((SDR_RECEPT[0] - 7, SDR_RECEPT[1] - 7.5, SDR_RECEPT[0] + 7, SDR_RECEPT[1] + 7.5), pcbnew.F_SilkS, 0.15)
text("J_RTL1", SDR_RECEPT[0], SDR_RECEPT[1] + 9.5, pcbnew.F_SilkS, 1.0, 0.18)
# LTE card (north band) and ZigBee module (east strip): outlines for the fit check; the footprints come with the netlist
rect(LTE_RECT, pcbnew.Dwgs_User, 0.1)
rect(WIFI_RECT, pcbnew.Dwgs_User, 0.1)
text("WIFI P2P: AsiaRF AW7915-AED M.2 2230 on J_WIFI1 (CM5 PCIe), M2.5 standoff; 2x IPEX pigtails -> WIFI P2P bulkheads (east wall)", (WIFI_RECT[0] + WIFI_RECT[2]) / 2, WIFI_RECT[1] - 1.6, pcbnew.F_SilkS, 0.9, 0.16)
text("LTE: Quectel EG25-G mini PCIe (full-size card 30 x 50.95) on J_LTE1, 2x M2.5 standoffs; SIM in J_SIM1; pigtails -> LTE bulkhead", (LTE_RECT[0] + LTE_RECT[2]) / 2, LTE_RECT[3] + 1.6, pcbnew.F_SilkS, 0.9, 0.16)
rect(ZB_RECT, pcbnew.Dwgs_User, 0.1)
text("ZIGBEE: Ebyte E72-2G4M20S1E (CC2652P), PCB antenna to the back wall", (ZB_RECT[0] + ZB_RECT[2]) / 2, ZB_RECT[3] + 1.6, pcbnew.F_SilkS, 0.9, 0.16)
text("GNSS NEO-M9N + U.FL -> GPS bulkhead   |   LoRa Wio-SX1262, IPEX -> LoRa bulkhead", -96.0, 68.5, pcbnew.F_SilkS, 0.9, 0.16)
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
# zones (drawn for the record; gen_pcb_b3.py packs into them)
rect(HUB_ZONE, pcbnew.Dwgs_User, 0.15); text("USB2517I HUB (upstream = CM5 USB3-0 pair)", (HUB_ZONE[0] + HUB_ZONE[2]) / 2, HUB_ZONE[3] + 2.0, pcbnew.Dwgs_User, 1.0, 0.18)
rect(BUCK_ZONE, pcbnew.Dwgs_User, 0.15); text("3.3 V BUCKS", (BUCK_ZONE[0] + BUCK_ZONE[2]) / 2, BUCK_ZONE[3] + 2.0, pcbnew.Dwgs_User, 1.0, 0.18)
rect(CTRL_ZONE, pcbnew.Dwgs_User, 0.15); text("EXPANDERS, I2C BUFFER, LEVEL STAGES", (CTRL_ZONE[0] + CTRL_ZONE[2]) / 2, CTRL_ZONE[3] + 2.0, pcbnew.Dwgs_User, 0.9, 0.16)
text("J_5V_M1 / J_5V_M2 (VH) from PCB-A; J_5V_PI (VH) beside the module", -92.0, -40.0, pcbnew.Dwgs_User, 0.9, 0.15)
rect((J_FLASH[0] - 4.5, J_FLASH[1] - 4, J_FLASH[0] + 4.5, J_FLASH[1] + 4), pcbnew.Dwgs_User, 0.1); text("J_FLASH: rpiboot only", J_FLASH[0], J_FLASH[1] - 6, pcbnew.Dwgs_User, 0.9, 0.15)
text("J_AB1 2x9 to PCB-A (underside)", J_AB[0], J_AB[1] + 8.0, pcbnew.B_SilkS, 0.9, 0.15, mirror=True)
text("J_PANEL ribbon up to PCB-C", 86.0, 75.5, pcbnew.F_SilkS, 0.9, 0.16)
# datum + legends
line(-4, 0, 4, 0, pcbnew.Dwgs_User); line(0, -4, 0, 4, pcbnew.Dwgs_User); text("CASE DATUM (0,0)", 0, -6.0, pcbnew.Dwgs_User, 1.1, 0.18)
text("PCB-B COMPUTE  REV A (B14)", 70, -79.0, pcbnew.F_SilkS, 1.6, 0.26)
text("MESHSAT-795 | 245x170x1.6 4L | matte black | 2026-09-04", 70, -82.5, pcbnew.F_SilkS, 1.1, 0.18)
text("BACK WALL (+Y)", -10, 83.0, pcbnew.F_SilkS, 1.2, 0.2); text("FRONT WALL (-Y)   v v v", -100, -83.2, pcbnew.F_SilkS, 1.5, 0.25)
text("PORT (-X)", -hx + 5.5, 20, pcbnew.F_SilkS, 1.2, 0.2, angle=90); text("STARBOARD (+X)", hx - 6.0, 0, pcbnew.F_SilkS, 1.2, 0.2, angle=90)
text("PCB-B UNDERSIDE - faces PCB-A", 0, -hy + 9.0, pcbnew.B_SilkS, 1.6, 0.25, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes:", n - 1)
