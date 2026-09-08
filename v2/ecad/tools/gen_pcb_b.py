#!/usr/bin/env python3
"""Generate PCB-B COMPUTE, phase B16 (MESHSAT-830, appendix 32.58): MECHANICAL layer. Case-centred frame (+Y = back wall), millimetres.

330 x 200 centred on the rods, six layers on JLC06161H-3313. Three slot columns S1 (X -98..-38), S2 (-36..32), S3 (34..94): the CM5 site of each
in the north band (module 40 x 55 with its long axis along Y at (-72.5, 60), (-2.5, 60), (67.5, 60); the two Amphenol receptacles 17 mm off the
centre, 2.5 mm south; four M2.5 holes on 33 x 48; the cooler 41 x 56 over it) and the column south of it down to the south edge (M.2 sockets at
Y 25 with the cards extending south, the PCIe switch and hub, the rails, the bench parts, the flashing USB-C on the south edge). West band: the
QMX bay (63 x 95 along Y at X -162..-99, Y -66..29 between the rods, tie slots), the HDMI receptacle at the west edge, the regulators and expanders, the Ethernet
block north (KSZ9897R, magnetics, the RJ45 at the north edge, the PoE injector) and the panel ribbon at the north edge. East band: the LimeSDR bay
(31 x 69 along Y at X 130..161, Y -25..44, its USB 3 receptacle at the south end), the radios north (E22 LoRa, two E72 with their antennas at the
north edge, the LG290P, the bridges), the RockBLOCK 9704 bracket south-east (52 x 56 on 32 x 32 holes at (139, -71), its plate on 8 mm standoffs over rod nut R2); J_AB1 on the underside at
(113, -46) over A22's ribbon header. The board overhangs A22 by 45 mm on each side and 20 mm north and south (support posts: ASSEMBLY.md).
"""
import math, sys, os
import os, pcbnew
from pcbnew import VECTOR2I, FromMM
PHASE = os.environ.get("PHASE", "B17")   # the silk carries the phase the chain builds; the gate in verify_deliverable.py refuses a deliverable stamped with another (8 Sep 2026)


OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-b-compute.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 330.0, 200.0, 5.0
ROD_HOLES = [(-110.5, -73.0), (110.5, -73.0), (-110.5, 73.0), (110.5, 73.0)]
ROD_DRILL, NUT_KEEPOUT_D = 3.2, 9.0
OX, OY = 150.0, 110.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
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

# ---------------------------------------------------------------- sites (case frame), appendix 32.58
SLOT_X = {1: (-98.0, -38.0), 2: (-36.0, 32.0), 3: (34.0, 94.0)}
CM5_C = {1: (-72.5, 60.0), 2: (-2.5, 60.0), 3: (67.5, 60.0)}
def cm5_rect(s): cx, cy = CM5_C[s]; return (cx - 20.0, cy - 27.5, cx + 20.0, cy + 27.5)
def cooler_rect(s): cx, cy = CM5_C[s]; return (cx - 20.5, cy - 28.0, cx + 20.5, cy + 28.0)
def cm5_holes(s): cx, cy = CM5_C[s]; return [(cx + dx, cy + dy) for dx in (-16.5, 16.5) for dy in (-24.0, 24.0)]
QMX_RECT = (-162.0, -66.0, -99.0, 29.0)                    # QRP Labs QMX assembled unit 95 x 63 x 25 along Y on four printed feet, strapped through the slots
QMX_SLOTS = [(-100.5, 20.0), (-100.5, -40.0), (-145.0, -67.5), (-116.0, -67.5)]
LIME_RECT = (130.0, -24.0, 161.0, 45.0)                   # LimeSDR Mini 2.4 (69 x 31.4) along Y, its plug in J_LIME at the south end, SMAs north
LIME_SLOTS = [(128.0, -2.0), (128.0, 28.0)]
J_LIME = (145.5, -33.5)
RB_C = (139.0, -71.0)
RB9704_RECT = (RB_C[0] - 26.0, RB_C[1] - 28.0, RB_C[0] + 26.0, RB_C[1] + 28.0)      # Ground Control bracket 52 x 56
RB9704_HOLES = [(RB_C[0] + dx, RB_C[1] + dy) for dx in (-16.0, 16.0) for dy in (-16.0, 16.0)]
J_AB = (113.0, -46.0)                                     # 2x13 IDC on the UNDERSIDE, over A22's J_AB1 at the same case XY
J_ETH = (-152.0, 91.0)                                    # RJ45 at the north edge, opening to the back wall
J_HDMI = (104.5, -93.0)                                   # HDMI A at the south edge (south-east corner), opening south, its face at the board edge
J_PANEL = (-116.0, 92.0)                                  # 2x13 along X at the north edge, ribbon up to C7
# zones of the placement stage (gen_pcb_b3.py packs into them; drawn for the record)
ZONES = {"ETH": (-162, 31, -122, 59), "POE": (-140.5, 58, -122, 86), "WNE": (-121, 29, -102, 68), "WMIDS": (-152, -97, -116, -69), "GAP12": (-50, 33, -32, 97), "GAP23": (19, 33, 44, 97), "RADE": (125.5, 45.5, 162, 67), "RBX": (96, -25, 128, 27), "RBX2": (96, -44, 110, -26), "NEX": (96, 78, 123, 97.5), "SEX": (96, -85, 112, -78)}

# ---------------------------------------------------------------- plumbing
board = pcbnew.BOARD()
board.SetCopperLayerCount(6)   # JLC06161H-3313: F.Cu / In1 GND / In2 / In3 / In4 5 V / B.Cu
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-B COMPUTE"); tb.SetRevision("A")
tb.SetDate("2026-09-07"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-830. Case-centred frame. B16: three Compute Module 5 slots on a PCIe/USB 3/Ethernet/HDMI fabric (appendix 32.52, 32.58). tools/gen_pcb_b.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.40), ("m_MinThroughDrill", 0.20), ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.19), ("m_SolderMaskMinWidth", 0.1)):
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
    if centre:
        bb = fp.GetBoundingBox(False, False)
        cx, cy = (bb.GetLeft() + bb.GetRight()) // 2, (bb.GetTop() + bb.GetBottom()) // 2
        t = P(x, y); fp.Move(VECTOR2I(t.x - cx, t.y - cy))
    return fp
def hole(ref, x, y, d, value):
    name = {2.2: "MountingHole_2.2mm_M2", 2.7: "MountingHole_2.7mm_M2.5", 3.2: "MountingHole_3.2mm_M3", 4.3: "MountingHole_4.3mm_M4"}[d]
    if d != ROD_DRILL: keepout_circle(x, y, d + 2.0, "keep-out: " + ref)
    return place("MountingHole", name, ref, x, y, value)
def slot(ref, x, y, w, h, value="tie slot"):
    keepout_rect(x - w / 2 - 0.8, y - h / 2 - 0.8, x + w / 2 + 0.8, y + h / 2 + 0.8, "keep-out: " + ref)
    return place("meshsat", slot_footprint(w, h), ref, x, y, value, centre=True)
def rule_area_annulus(cx, cy, d, inner_d, name):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName(name)
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
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in pts:
        p = P(x, y); o.Append(p.x, p.y)
    board.Add(z); return z
def keepout_circle(cx, cy, d, name, n=36):
    return rule_area_poly([(cx + d / 2 * math.cos(math.radians(i * 360 / n)), cy + d / 2 * math.sin(math.radians(i * 360 / n))) for i in range(n)], name)
def keepout_rect(x0, y0, x1, y1, name):
    return rule_area_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], name)
def edge_band(w=0.5):
    """No tracks or vias within w mm of the outline on any copper layer (E6 route 1 lesson, 7 Sep 2026); pours keep their own clearance."""
    hx, hy = BOARD_L / 2, BOARD_W / 2
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName("edge band: no tracks or vias within %.1f mm of the outline" % w)
    o = z.Outline(); o.NewOutline()
    for x, y in ((-hx - 1, -hy - 1), (hx + 1, -hy - 1), (hx + 1, hy + 1), (-hx - 1, hy + 1)): p = P(x, y); o.Append(p.x, p.y)
    h = o.NewHole(0)
    for x, y in ((-hx + w, -hy + w), (-hx + w, hy - w), (hx - w, hy - w), (hx - w, -hy + w)): p = P(x, y); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
def site(r, label, sublabel="", layer=pcbnew.F_SilkS, lx=None, ly=None):
    rect(r, layer, 0.12); cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    lx = cx if lx is None else lx; ly = cy if ly is None else ly
    text(label, lx, ly + 1.6, layer, 1.4, 0.22)
    if sublabel: text(sublabel, lx, ly - 1.4, layer, 1.0, 0.18)

# ---------------------------------------------------------------- outline + rods
hx, hy = BOARD_L / 2, BOARD_W / 2
rounded_rect(-hx, -hy, hx, hy, BOARD_R, pcbnew.Edge_Cuts)
edge_band(0.5)
for i, (x, y) in enumerate(ROD_HOLES, 1):
    hole("H%d" % i, x, y, 3.2, "M3 rod R%d" % i)
    for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS): circle(x, y, NUT_KEEPOUT_D, layer, 0.15)
    rule_area_annulus(x, y, NUT_KEEPOUT_D, ROD_DRILL + 3.0, "nut keep-out R%d" % i)
    text("R%d" % i, x, y + 7.0, pcbnew.F_SilkS, 1.5, 0.25)
n = 5
# ---------------------------------------------------------------- the three Compute Module 5 sites (receptacles U30A/B, U31A/B, U32A/B are placed by gen_pcb_b3.py)
for s in (1, 2, 3):
    cx, cy = CM5_C[s]
    rect(cm5_rect(s), pcbnew.Dwgs_User, 0.1); rect(cooler_rect(s), pcbnew.F_SilkS, 0.12)
    for (x, y) in cm5_holes(s):
        hole("H%d" % n, x, y, 2.7, "M2.5 standoff 4.0 mm, CM5 slot S%d" % s); n += 1
    text("SLOT S%d: COMPUTE MODULE 5 on 2x Amphenol 10164227-1004A1RLF, M2.5 x 4 on 33 x 48; IP68 cooler 41 x 56 over it" % s, cx, cy + 31.5, pcbnew.F_SilkS, 0.9, 0.16)
    text("GPIO connector WEST, high-speed connector EAST", cx, cy - 31.5, pcbnew.F_SilkS, 0.9, 0.16)
    x0, x1 = SLOT_X[s]
    rect((x0, -97.0, x1, 30.0), pcbnew.Dwgs_User, 0.12); text("S%d column: M.2 sockets north (cards south), PCIe switch, USB 3 hub, rails, bench" % s, (x0 + x1) / 2, 31.5, pcbnew.Dwgs_User, 0.9, 0.16)
# ---------------------------------------------------------------- QMX bay, LimeSDR bay, RockBLOCK site
site(QMX_RECT, "HF: QRP Labs QMX (assembled, 95 x 63 x 25) on four printed feet", "USB lead -> J_QMX; 12 V straight from A22 J_HF; antenna -> A22 HF jack", lx=-130.5, ly=-18.0)
for i, (x, y) in enumerate(QMX_SLOTS, 1): slot("S_QMX%d" % i, x, y, 5.0, 1.8)
site(LIME_RECT, "LimeSDR Mini 2.4 bay (69 x 31.4)", "plug -> J_LIME south; SMAs north -> A22 SDR jack", lx=145.5, ly=10.0)
for i, (x, y) in enumerate(LIME_SLOTS, 1): slot("S_LIME%d" % i, x, y, 5.0, 1.8)
usb3 = place("Connector_USB", "USB3_A_Receptacle_Wuerth_692122030100", "J_LIME", J_LIME[0], J_LIME[1], "USB 3.0 A receptacle, LimeSDR", rot=180)   # opening north into the bay (the land opens toward local +y); reused by gen_pcb_b3.py, not placed twice
if usb3 is None: rect((J_LIME[0] - 7, J_LIME[1] - 8, J_LIME[0] + 7, J_LIME[1] + 8), pcbnew.F_SilkS, 0.15)
text("J_LIME", J_LIME[0] + 12.0, J_LIME[1], pcbnew.F_SilkS, 1.0, 0.18)
rect(RB9704_RECT, pcbnew.F_SilkS, 0.12); text("ROCKBLOCK 9704 on the GC bracket (4x M4, 32 x 32) on 8 mm standoffs: the plate passes over rod nut R2", RB_C[0], RB_C[1] + 2.0, pcbnew.F_SilkS, 1.0, 0.18); text("pigtail -> A22 IRIDIUM jack; USB via CP2102N", RB_C[0], RB_C[1] - 1.5, pcbnew.F_SilkS, 1.0, 0.18)
for (x, y) in RB9704_HOLES:
    hole("H%d" % n, x, y, 4.3, "M4, GC 9704 bracket"); n += 1
# ---------------------------------------------------------------- fixed connectors of the bands (footprints come with the netlist; outlines here)
rect((J_ETH[0] - 8.5, J_ETH[1] - 11, J_ETH[0] + 8.5, J_ETH[1] + 9), pcbnew.Dwgs_User, 0.1); text("J_ETH RJ45 -> sealed wall RJ45 (PoE out)", J_ETH[0], J_ETH[1] - 13.0, pcbnew.Dwgs_User, 0.9, 0.15)
rect((J_HDMI[0] - 8, J_HDMI[1] - 8, J_HDMI[0] + 8, J_HDMI[1] + 8), pcbnew.Dwgs_User, 0.1); text("J_HDMI -> Xenarc pass-through", J_HDMI[0] + 3.0, J_HDMI[1] - 10.5, pcbnew.Dwgs_User, 0.9, 0.15)
rect((J_PANEL[0] - 17.5, J_PANEL[1] - 4.5, J_PANEL[0] + 17.5, J_PANEL[1] + 4.5), pcbnew.Dwgs_User, 0.1); text("J_PANEL 2x13 ribbon up to PCB-C C7", J_PANEL[0], J_PANEL[1] - 6.5, pcbnew.F_SilkS, 0.9, 0.16)
text("J_AB1 2x13 to PCB-A A22 (underside, same case XY)", J_AB[0], J_AB[1] + 19.0, pcbnew.B_SilkS, 0.9, 0.15, mirror=True)
for k, r in ZONES.items(): rect(r, pcbnew.Dwgs_User, 0.15); text(k, (r[0] + r[2]) / 2, r[3] - 1.5, pcbnew.Dwgs_User, 1.0, 0.18)
text("E22-900M30S LoRa | E72 x2 (antennas -> north edge) | LG290P + U.FL -> A22 GNSS jack | CP2102N bridges", 130.0, 98.0, pcbnew.F_SilkS, 0.9, 0.16)
text("KSZ9897R Gigabit switch | H5007NL | PoE TPS23861 (54 V from A22 J_54V)", -142.0, 38.5, pcbnew.F_SilkS, 0.9, 0.16)
# datum + legends
line(-4, 0, 4, 0, pcbnew.Dwgs_User); line(0, -4, 0, 4, pcbnew.Dwgs_User); text("CASE DATUM (0,0)", 0, -6.0, pcbnew.Dwgs_User, 1.1, 0.18)
text("PCB-B COMPUTE  REV A (%s)" % PHASE, 100, -96.0, pcbnew.F_SilkS, 1.6, 0.26)
text("MESHSAT-830 | 330x200x1.6 6L JLC06161H-3313 | matte black | 2026-09-07", 100, -99.0, pcbnew.F_SilkS, 1.0, 0.16)
text("BACK WALL (+Y)", 0, 98.5, pcbnew.F_SilkS, 1.2, 0.2); text("FRONT WALL (-Y)   v v v", -60, -98.5, pcbnew.F_SilkS, 1.2, 0.2)
text("PORT (-X)", -hx + 5.5, -60, pcbnew.F_SilkS, 1.2, 0.2, angle=90); text("STARBOARD (+X)", hx - 6.0, 60, pcbnew.F_SilkS, 1.2, 0.2, angle=90)
text("PCB-B UNDERSIDE - faces PCB-A", 0, -hy + 9.0, pcbnew.B_SilkS, 1.6, 0.25, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes:", n - 1)
