#!/usr/bin/env python3
"""Generate PCB-D APRS BOARD (MeshSat field-kit carrier, Rev A) - MECHANICAL + PLACEMENT layer (phase D1).

Board-local frame: origin at the board centre, +X = case east (SMA end of the radio), +Y = case north.
The board sits on PCB-A's four M3 standoffs at case (10/80, +-26) = local (+-35, +-26); local (0,0) = case (45, 0).
Sources: NiceRF DMR858M datasheet V1.2 p.10 (38.69 x 58.31, 24 castellated pads 2.54 mm, right row from
15.06 mm below the top edge, 2 x Ø3.00 holes at 2.81/2.96 (top-left) and 2.73/2.86 (bottom-right), SMA on the
top edge right of centre, USB-C bottom edge, 19.5 mm tall with the heatsink); PCB-A gen_pcb_a.py (site 80 x 62,
J_MEZZ1 2x8 at case (-8, 8), J_MEZZ_PWR VH2 at case (-8, -18)); owner decisions 2026-09-02 (AIOC-derived core).
The module is rotated 90 deg CW from the datasheet view: SMA -> east, right pad row (pins 1-12) -> south,
left pad row (13-24) -> north, pin 1 at the east end of the south row, pin 13 at the west end of the north row.
"""
import math, sys, os
import pcbnew
from pcbnew import VECTOR2I, FromMM

OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-d-aprs.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 80.0, 62.0, 3.0
STANDOFFS = [(-35.0, -26.0), (35.0, -26.0), (-35.0, 26.0), (35.0, 26.0)]   # M3, Ø3.2, Ø7.5 keep-out (nut/standoff face)
SO_DRILL, SO_KEEPOUT_D = 3.2, 7.5
OX, OY = 100.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
PRJDIR = os.path.dirname(os.path.abspath(OUT))
MSLIB = os.path.normpath(os.path.join(PRJDIR, "..", "meshsat.pretty"))
os.makedirs(MSLIB, exist_ok=True)
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')

# ---------------------------------------------------------------- DMR858M module (module frame, SMA end = +X)
MOD_L, MOD_W = 58.31, 38.69
MOD_C = (10.5, -2.0)                     # module centre: SMA end 0.35 mm inside the east edge (its NE standoff hole then keeps a 1.7 mm web to the edge); the module sits 11 mm up, so the boost column may run under its west end
PITCH = 2.54
ROW_IN = 1.27                            # pin-hole centres 1.27 mm inboard of the module's long edges (datasheet V1.2 p.10 drawing, measured 1.14 / 1.36): rows 36.15 mm apart
PIN_DRILL, PIN_PAD = 1.0, 1.7            # PCB-D carries two 1x12 2.54 mm female sockets (8.5 mm) that receive male headers soldered into the module's rows
MOD_STANDOFF = 11.0                      # socket 8.5 + header body 2.5: the module's back-side parts (switches, USB-C, about 5 mm) hang in that gap; heatsink up
MOD_HOLE_D = 2.9                         # M2.5 standoffs through PCB-D into the module's two Ø3.00 holes
def mod_pins():
    """(number, x, y) in the module frame (SMA end = +X). Datasheet front view (heatsink side, SMA top right) rotated 90 deg CW:
    the front-left row (pins 1-12, VCC at the SMA end) becomes the NORTH row, pin 1 east; the front-right row (24 at the SMA end, 13 at the far end) the SOUTH row."""
    pins = []
    for k in range(12): pins.append((k + 1, 14.095 - PITCH * k, MOD_W / 2 - ROW_IN))          # north row, pin 1 east (15.06 from the SMA edge)
    for j in range(12): pins.append((13 + j, -13.845 + PITCH * j, -(MOD_W / 2 - ROW_IN)))     # south row, pin 13 west, pin 24 east under pin 1
    return pins
MOD_HOLES = [(MOD_L / 2 - 2.81, MOD_W / 2 - 2.96), (-MOD_L / 2 + 2.86, -MOD_W / 2 + 2.73)]   # Ø3.00 on the module: 2.81 from the SMA edge / 2.96 from the pin-1 edge (NE), 2.86 / 2.73 (SW)
MOD_SMA_X = MOD_L / 2 + 6.0              # SMA jack straddles the SMA edge, body about 9 mm outboard
MOD_SMA_Y = -14.96                       # SMA centre 34.30 mm from the pin-1 edge in the datasheet view = 14.96 mm toward the pin-24 side: SOUTH of the module centre line
def dmr858m_footprint():
    name = "DMR858M"
    path = os.path.join(MSLIB, name + ".kicad_mod")
    s = ['(footprint "%s"' % name, '\t(version 20241229)', '\t(generator "meshsat")', '\t(generator_version "9.0")', '\t(layer "F.Cu")',
         '\t(descr "NiceRF DMR858M 5 W DMR/analog UHF module site: 38.69 x 58.31, two rows of 12 pin holes 2.54 mm, 1.27 mm inboard (datasheet V1.2 p.10); module on 2 x 1x12 sockets and M2.5 x 11 standoffs, heatsink up; SMA end = +X")',
         '\t(tags "DMR858M NiceRF radio")', '\t(attr through_hole)']
    hl, hw = MOD_L / 2, MOD_W / 2
    for layer, w, ins in (("F.Fab", 0.1, 0.0), ("F.SilkS", 0.15, 0.6)):       # silk outline inset 0.6 so it stays off the board edge
        s.append('\t(fp_rect (start %g %g) (end %g %g) (stroke (width %g) (type default)) (fill no) (layer "%s"))' % (-hl + ins, -hw + ins, hl - ins, hw - ins, w, layer))
    # courtyard: only what touches the board (the module itself sits 11 mm up): the two socket bodies and the two standoff hexes
    for yy in (MOD_W / 2 - ROW_IN, -(MOD_W / 2 - ROW_IN)):
        s.append('\t(fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd"))' % (-13.845 - 1.52, -yy - 1.5, 14.095 + 1.52, -yy + 1.5))
    for (hx, hy) in MOD_HOLES:
        s.append('\t(fp_circle (center %g %g) (end %g %g) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd"))' % (hx, -hy, hx + 3.0, -hy))
    for (hx, hy) in MOD_HOLES:
        s.append('\t(fp_circle (center %g %g) (end %g %g) (stroke (width 0.1) (type default)) (fill no) (layer "F.Fab"))' % (hx, -hy, hx + 1.5, -hy))
        s.append('\t(pad "" np_thru_hole circle (at %.3f %.3f) (size %g %g) (drill %g) (layers "*.Cu" "*.Mask"))' % (hx, -hy, MOD_HOLE_D, MOD_HOLE_D, MOD_HOLE_D))
        s.append('\t(fp_circle (center %g %g) (end %g %g) (stroke (width 0.12) (type default)) (fill no) (layer "F.SilkS"))' % (hx, -hy, hx + 3.0, -hy))
    s.append('\t(fp_text user "SMA" (at %g %g) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))' % (hl + 3.0, -MOD_SMA_Y))
    s.append('\t(fp_text user "USB-C" (at %g %g) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))' % (-hl - 3.5, 0))
    s.append('\t(fp_text user "DMR858M on 2 x 1x12 sockets + M2.5 x 11 standoffs, heatsink up" (at 0 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
    for yy in (MOD_W / 2 - ROW_IN, -(MOD_W / 2 - ROW_IN)):     # socket bodies 2.5 x 30.5 on F.Fab
        s.append('\t(fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.1) (type default)) (fill no) (layer "F.Fab"))' % (-13.845 - 1.27, -yy - 1.25, 14.095 + 1.27, -yy + 1.25))
    s.append('\t(property "Reference" "REF**" (at 0 %g 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))' % (-hw - 2.5))
    s.append('\t(property "Value" "DMR858M" (at 0 %g 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))' % (hw + 2.5))
    for num, x, y in mod_pins():
        shape = "rect" if num == 1 else "circle"
        s.append('\t(pad "%d" thru_hole %s (at %.3f %.3f) (size %g %g) (drill %g) (layers "*.Cu" "*.Mask"))' % (num, shape, x, -y, PIN_PAD, PIN_PAD, PIN_DRILL))
    # pin 1 marker: filled dot just east of pad 1 on the north row
    x1, y1 = mod_pins()[0][1], mod_pins()[0][2]
    s.append('\t(fp_circle (center %g %g) (end %g %g) (stroke (width 0.2) (type default)) (fill yes) (layer "F.SilkS"))' % (x1 + 1.7, -y1, x1 + 2.1, -y1))
    s.append(')')
    open(path, "w").write("\n".join(s) + "\n"); return name

# ---------------------------------------------------------------- other placed items (board frame)
J_HARN = (-33.0, 6.0)        # IDC 2x8 box header, pins along Y (11 x 29), ribbon to PCB-A J_MEZZ1 at case (-8, 8)
J_PWR = (-33.0, -14.0)       # JST-VH 2-pin (9.4 x 9.6) under the header, cable to PCB-A J_MEZZ_PWR at case (-8, -18)
N_STRIP = (-30.0, 18.6, 30.0, 30.4)     # north strip: D6 core (top: clock, bead, PCA9536, LED; bottom: codec, audio, PTT, UART header)
S_STRIP = (-17.0, -30.4, 30.0, -22.6)   # south strip: DNP speaker/host headers (top); jumpers + test points (bottom)
W_COL = (-27.0, -30.4, -18.0, 17.5)     # west column: TPS61089 boost (top)

# ---------------------------------------------------------------- plumbing (as PCB-A/B)
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-D APRS BOARD"); tb.SetRevision("A")
tb.SetDate("2026-09-02"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-709 / MESHSAT-748. Board-local frame, +X = case east. Phase D1 mechanical + placement. tools/gen_pcb_d.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(-BOARD_L / 2, -BOARD_W / 2)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.4), ("m_MinThroughDrill", 0.2),
                  ("m_HoleToHoleMin", 0.5), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.20), ("m_SolderMaskMinWidth", 0.1)):
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
    line(x0 + r, y0, x1 - r, y0, layer, width); line(x1, y0 + r, x1, y1 - r, layer, width)
    line(x1 - r, y1, x0 + r, y1, layer, width); line(x0, y1 - r, x0, y0 + r, layer, width)
    arc(x1 - r, y0 + r, r, 270, 360, layer, width); arc(x1 - r, y1 - r, r, 0, 90, layer, width)
    arc(x0 + r, y1 - r, r, 90, 180, layer, width); arc(x0 + r, y0 + r, r, 180, 270, layer, width)
def rect(r, layer, width=0.1):
    x0, y0, x1, y1 = r
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))): line(a[0], a[1], b[0], b[1], layer, width)
def text(txt, x, y, layer, size=1.2, thick=0.2, angle=0.0, mirror=False):
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
def rule_area_poly(pts, name, layers=None):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(layers if layers is not None else pcbnew.LSET.AllCuMask(4)); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in pts:
        p = P(x, y); o.Append(p.x, p.y)
    board.Add(z); return z
def keepout_circle(cx, cy, d, name, n=36):
    return rule_area_poly([(cx + d / 2 * math.cos(math.radians(i * 360 / n)), cy + d / 2 * math.sin(math.radians(i * 360 / n))) for i in range(n)], name)
def hole(ref, x, y, d, value):
    name = {2.2: "MountingHole_2.2mm_M2", 2.7: "MountingHole_2.7mm_M2.5", 3.2: "MountingHole_3.2mm_M3"}[d]
    return place("MountingHole", name, ref, x, y, value)

# ---------------------------------------------------------------- outline, standoffs
hx, hy = BOARD_L / 2, BOARD_W / 2
rounded_rect(-hx, -hy, hx, hy, BOARD_R, pcbnew.Edge_Cuts)
n = 1
for (x, y) in STANDOFFS:
    hole("H%d" % n, x, y, SO_DRILL, "M3 standoff to PCB-A"); keepout_circle(x, y, SO_KEEPOUT_D, "keep-out: standoff H%d" % n)
    for layer in (pcbnew.F_SilkS, pcbnew.B_SilkS): circle(x, y, SO_KEEPOUT_D, layer, 0.12)
    n += 1
# ---------------------------------------------------------------- radio module
mod = place("meshsat", dmr858m_footprint(), "U2", MOD_C[0], MOD_C[1], "DMR858M", rot=0, centre=False)
mx0, mx1 = MOD_C[0] - MOD_L / 2, MOD_C[0] + MOD_L / 2
text("DMR858M on 2x 1x12 sockets + M2.5 x 11 standoffs, heatsink up", 10, -8.5, pcbnew.B_SilkS, 0.75, 0.13, mirror=True)
text("SMA east -> UHF bulkhead | USB-C west | pin 1 = VCC (NE)", 10, -11.5, pcbnew.B_SilkS, 0.75, 0.13, mirror=True)
text("rows and holes per NiceRF datasheet V1.2 p.10", 10, -14.5, pcbnew.B_SilkS, 0.75, 0.13, mirror=True)
# SMA overhang marker beyond the east edge (User.Drawings), for the pigtail
rect((hx, MOD_C[1] + MOD_SMA_Y - 3.5, hx + 9.0, MOD_C[1] + MOD_SMA_Y + 3.5), pcbnew.Dwgs_User, 0.1); text("SMA", hx + 4.5, MOD_C[1] + MOD_SMA_Y + 5.0, pcbnew.Dwgs_User, 0.8, 0.15)
# ---------------------------------------------------------------- connectors
place("Connector_IDC", "IDC-Header_2x08_P2.54mm_Vertical", "J_HARN1", J_HARN[0], J_HARN[1], "harness to PCB-A J_MEZZ1 (IDC 2x8)", rot=0)
text("J_HARN1 to PCB-A J_MEZZ1", J_HARN[0] + 2.0, J_HARN[1] + 12.5, pcbnew.B_SilkS, 0.8, 0.15, mirror=True)
place("Connector_JST", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "J_PWR1", J_PWR[0], J_PWR[1], "cell node from PCB-A J_MEZZ_PWR (VH)", rot=0)
text("J_PWR1 MEZZ_CELL GND", J_PWR[0], J_PWR[1] + 6.5, pcbnew.B_SilkS, 0.8, 0.15, mirror=True)
# ---------------------------------------------------------------- reserved regions
for r, label in ((N_STRIP, "N: D6 core (top clock/expander/LED, bottom codec/audio/PTT)"), (S_STRIP, "S: DNP headers (top), jumpers + TPs (bottom)"), (W_COL, "W: 8 V boost")):
    rect(r, pcbnew.Dwgs_User, 0.1); text(label, (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, pcbnew.Dwgs_User, 0.8, 0.14, angle=90 if r is W_COL else 0)
# ---------------------------------------------------------------- legends
text("PCB-D APRS BOARD REV A (D5) | MESHSAT-709/748 | 2026-09-03", 10, -1.5, pcbnew.B_SilkS, 1.0, 0.17, mirror=True)
text("underside faces PCB-A: jumpers + test points", 10, -5.0, pcbnew.B_SilkS, 0.85, 0.15, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "standoff holes:", n - 1, "module pads:", len(list(mod.Pads())) if mod else 0)
