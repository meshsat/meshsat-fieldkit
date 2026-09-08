#!/usr/bin/env python3
"""Generate PCB-P PACK BMS, phase P1 (MESHSAT-830, appendix 32.62: the built 4S smart pack): MECHANICAL layer.

Board-local frame: origin at the board centre, +X along the pack's length, +Y across it. 70 x 44, two layers on JLC's 2 oz stack, four M3 holes at
(+-32, +-19) for the enclosure's bosses (v2/cad/pack_4s.py). The board lies at the end of the cell block inside the enclosure, parts up, the
25 A blade holder the tallest part. The power path (B+ land, blade, charge FET, discharge FET, pack + land) runs along the north edge and the
shunt with the B- and pack - lands along the south edge; tools/gen_pcb_p3.py places the parts, lays the locked 2 oz bands of the power path on both
layers and packs the gauge and its filters in the middle.
"""
import math, sys, os
import os, pcbnew
from pcbnew import VECTOR2I, FromMM
PHASE = os.environ.get("PHASE", "P2")   # the silk carries the phase the chain builds; the gate in verify_deliverable.py refuses a deliverable stamped with another (8 Sep 2026)


OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-p-pack.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 70.0, 44.0, 2.0
STANDOFFS = [(-32.0, -19.0), (32.0, -19.0), (-32.0, 19.0), (32.0, 19.0)]
SO_DRILL, SO_KEEPOUT_D = 3.2, 6.5
OX, OY = 100.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
PRJDIR = os.path.dirname(os.path.abspath(OUT))
MSLIB = os.path.normpath(os.path.join(PRJDIR, "..", "meshsat.pretty"))
os.makedirs(MSLIB, exist_ok=True)
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')

# ---------------------------------------------------------------- sites (board frame): the power path along the north edge, the shunt along the south edge, the gauge in the middle
W_BP, F1, Q1, Q2, W_P = (-27.0, 12.5), (-15.6, 15.0), (0.0, 15.0), (8.0, 15.0), (26.0, 12.5)     # B+ land, blade holder, charge FET, discharge FET, pack + land
W_BN, R10, W_N = (-27.0, -12.5), (-18.0, -15.0), (-8.0, -13.5)                                    # B- land, the 2 mohm shunt, pack - land
J_CELL, J_TS, J_SMB = (12.0, -17.5), (30.5, -9.0), (30.5, 2.0)                                     # the tap header, the thermistor lead, the SMBus lead (all along the south and east edges)
ZONES = {"GAUGE": (-23, -10, 4, 12), "SIG": (4, -10, 22, 12), "TPS": (-33, -12, -25, 8.5)}
# ---------------------------------------------------------------- plumbing (as PCB-B)
board = pcbnew.BOARD()
board.SetCopperLayerCount(2)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-P PACK BMS"); tb.SetRevision("A")
tb.SetDate("2026-09-07"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-830. Board-local frame, +X along the pack, the board at the end of the cell block inside the pack enclosure (appendix 32.62). P1: BQ4050 SMBus gauge and protection for the built 4S pack, two layers, 2 oz. tools/gen_pcb_p.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.5), ("m_MinThroughDrill", 0.3), ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.2), ("m_SolderMaskMinWidth", 0.1)):
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
def text(txt, x, y, layer, size=1.2, thick=0.2, angle=0.0, mirror=False):
    t = pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(layer)
    t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick)); t.SetTextAngleDegrees(angle)
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    if mirror: t.SetMirrored(True)
    board.Add(t); return t
LIBS = "/usr/share/kicad/footprints/"
def place(lib, name, ref, x, y, value="", rot=0.0, back=False, centre=True):
    fp = pcbnew.FootprintLoad(MSLIB if lib == "meshsat" else LIBS + lib + ".pretty", name)
    if fp is None: print("WARNING footprint missing:", lib, name); return None
    fp.SetReference(ref); fp.SetValue(value); fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    fp.SetPosition(P(x, y))
    if back: fp.Flip(P(x, y), False)
    fp.SetOrientationDegrees(rot); board.Add(fp)
    if centre:
        bb = fp.GetBoundingBox(False, False); cx, cy = (bb.GetLeft() + bb.GetRight()) // 2, (bb.GetTop() + bb.GetBottom()) // 2
        t = P(x, y); fp.Move(VECTOR2I(t.x - cx, t.y - cy))
    return fp
def rule_area_poly(pts, name, layers=None, vias=True):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(vias); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(layers if layers is not None else pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for x, y in pts: p = P(x, y); o.Append(p.x, p.y)
    board.Add(z); return z
def rule_area_annulus(cx, cy, d, inner_d, name):
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(True); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName(name)
    o = z.Outline(); o.NewOutline()
    for i in range(36):
        a = math.radians(i * 10); p = P(cx + d / 2 * math.cos(a), cy + d / 2 * math.sin(a)); o.Append(p.x, p.y)
    h = o.NewHole(0)
    for i in range(36):
        a = math.radians(-i * 10); p = P(cx + inner_d / 2 * math.cos(a), cy + inner_d / 2 * math.sin(a)); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z
def hole(ref, x, y, d, value):
    name = {2.7: "MountingHole_2.7mm_M2.5", 3.2: "MountingHole_3.2mm_M3"}[d]
    return place("MountingHole", name, ref, x, y, value)
def edge_band(w=0.5):
    hx, hy = BOARD_L / 2, BOARD_W / 2
    z = pcbnew.ZONE(board); z.SetIsRuleArea(True); z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(board.GetCopperLayerCount())); z.SetZoneName("edge band: no tracks or vias within %.1f mm of the outline" % w)
    o = z.Outline(); o.NewOutline()
    for x, y in ((-hx - 1, -hy - 1), (hx + 1, -hy - 1), (hx + 1, hy + 1), (-hx - 1, hy + 1)): p = P(x, y); o.Append(p.x, p.y)
    h = o.NewHole(0)
    for x, y in ((-hx + w, -hy + w), (-hx + w, hy - w), (hx - w, hy - w), (hx - w, -hy + w)): p = P(x, y); o.Append(p.x, p.y, 0, h)
    board.Add(z); return z


# ---------------------------------------------------------------- outline, holes, edge band
hx, hy = BOARD_L / 2, BOARD_W / 2
rounded_rect(-hx, -hy, hx, hy, BOARD_R, pcbnew.Edge_Cuts)
edge_band(0.5)
for i, (x, y) in enumerate(STANDOFFS, 1):
    hole("H%d" % i, x, y, 3.2, "M3 into the enclosure boss")
    circle(x, y, SO_KEEPOUT_D, pcbnew.F_SilkS, 0.12); rule_area_annulus(x, y, SO_KEEPOUT_D, SO_DRILL + 2.0, "boss keep-out H%d" % i)
for k, r in ZONES.items(): rect(r, pcbnew.Dwgs_User, 0.12); text(k, (r[0] + r[2]) / 2, r[3] - 1.0, pcbnew.Dwgs_User, 0.8, 0.14)
text("B+ > F1 25A > Q1 CHG > Q2 DSG > PACK+", 0.0, 20.2, pcbnew.F_SilkS, 0.8, 0.14)
text("B- > R10 2m > PACK-   taps J_CELL   NTC J_TS   SMBus J_SMB", -6.0, -20.2, pcbnew.F_SilkS, 0.8, 0.14)
text("PCB-P PACK BMS REV A (%s)" % PHASE, 0, -3.0, pcbnew.B_SilkS, 1.2, 0.2, mirror=True)
text("MESHSAT-830 | 70x44x1.6 2L 2oz | 2026-09-07", 0, -5.5, pcbnew.B_SilkS, 0.8, 0.14, mirror=True)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes: 4")
