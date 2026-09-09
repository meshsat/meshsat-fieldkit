#!/usr/bin/env python3
"""Generate PCB-D APRS mezzanine, phase D8 (MESHSAT-830, appendix 32.56, 32.57, 32.59): MECHANICAL layer.

Board-local frame: origin at the board centre = case (50, 0) on A22's mezzanine site (case X 0 to 100, Y -40 to 40), +X = case east,
+Y = case north. 100 x 80, four layers, four M3 standoffs at local (+-45, +-35) = A22's (5, +-35) and (95, +-35). The harness headers sit
at the west edge opposite A22's J_MEZZ1 (case (-8, 8)) and J_MEZZ_PWR1 (case (-8, -18)). The SA868 exciter sits west of centre, the T/R relay
and the low-pass filter along the south edge with the antenna SMA at the south-west corner (pigtail to A22's VHF jack J_RF1 at case (-52, -56)),
the PA leads at the north edge (drive U.FL, output SMA, gate bias header; the RA30H1317M1 bolts to the face plate, 32.56), the USB set
(hub, codec, bridge, headphone amplifier) east, the two headset lead headers at the east edge, the PTT and EMCON logic between the exciter
and the relay. tools/gen_pcb_d3.py places the parts and pours the planes.
"""
import math, sys, os
import os, pcbnew
from pcbnew import VECTOR2I, FromMM
PHASE = os.environ.get("PHASE", "D10")   # the silk carries the phase the chain builds; the gate in verify_deliverable.py refuses a deliverable stamped with another (8 Sep 2026)


OUT = sys.argv[1] if len(sys.argv) > 1 else "pcb-d-aprs.kicad_pcb"
BOARD_L, BOARD_W, BOARD_R = 100.0, 80.0, 3.0
STANDOFFS = [(-45.0, -35.0), (45.0, -35.0), (-45.0, 35.0), (45.0, 35.0)]
SO_DRILL, SO_KEEPOUT_D = 3.2, 7.5
OX, OY = 100.0, 100.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
PRJDIR = os.path.dirname(os.path.abspath(OUT))
MSLIB = os.path.normpath(os.path.join(PRJDIR, "..", "meshsat.pretty"))
os.makedirs(MSLIB, exist_ok=True)
open(os.path.join(PRJDIR, "fp-lib-table"), "w").write('(fp_lib_table\n  (version 7)\n  (lib (name "meshsat")(type "KiCad")(uri "${KIPRJMOD}/../meshsat.pretty")(options "")(descr "MeshSat carrier in-code footprints"))\n)\n')

# ---------------------------------------------------------------- sites (board frame)
SA868_C = (-15.0, 12.0)                     # module 35.6 x 19 (body X -32.8..2.8, Y 2.5..21.5), ANT pad 12 at its south-east corner
K1 = (2.0, -12.0)                           # T/R relay G6K-2F-Y between the exciter's ANT pad and the filter
J_HARN = (-42.0, 8.0)                       # 2x8 IDC along Y at the west edge, ribbon to A22 J_MEZZ1 (case (-8, 8))
J_PWR = (-42.0, -18.0)                      # JST-VH 2, +5V_D8 from A22 J_MEZZ_PWR1 (case (-8, -18))
J_ANT = (-32.0, -33.0)                      # SMA vertical, pigtail to A22's VHF jack
J_PAOUT = (35.0, 33.0)                      # SMA vertical, the PA's output coax from the face plate
J_PAIN = (-8.0, -18.0)                      # U.FL, the PA's drive coax
J_VGG = (46.0, 32.0)                        # gate bias lead to the PA (2-pin)
J_HS = [(46.5, 12.0), (46.5, -12.0)]        # headset leads from the face plate jacks (1x5 along Y at the east edge)
ZONES = {"RFP": (-5, -34, 45, -26), "CTRL": (-45, -22, -4, -8), "AUD": (8, -24, 45, 0), "HUB": (5, 2, 45, 28), "WEST": (-48, -34, -38, -22)}

# ---------------------------------------------------------------- plumbing (as PCB-B)
board = pcbnew.BOARD()
board.SetCopperLayerCount(4)
tb = pcbnew.TITLE_BLOCK(); tb.SetTitle("MeshSat Field Kit carrier - PCB-D APRS MEZZANINE"); tb.SetRevision("A")
tb.SetDate("2026-09-07"); tb.SetCompany("MeshSat"); tb.SetComment(0, "MESHSAT-830. Board-local frame, +X = case east; the board sits on A22's mezzanine standoffs. D8: SA868 exciter, T/R relay, low-pass filter, the PA on the face plate, USB audio and control set (appendix 32.56, 32.57, 32.59). tools/gen_pcb_d.py")
board.SetTitleBlock(tb)
ds = board.GetDesignSettings(); ds.SetBoardThickness(FromMM(1.6)); ds.SetAuxOrigin(P(0, 0)); ds.SetGridOrigin(P(0, 0))
for attr, val in (("m_MinClearance", 0.127), ("m_TrackMinWidth", 0.127), ("m_ViasMinSize", 0.45), ("m_MinThroughDrill", 0.25), ("m_HoleToHoleMin", 0.3), ("m_CopperEdgeClearance", 0.3), ("m_HoleClearance", 0.2), ("m_SolderMaskMinWidth", 0.1)):
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

# ---------------------------------------------------------------- outline, standoffs, edge band
hx, hy = BOARD_L / 2, BOARD_W / 2
rounded_rect(-hx, -hy, hx, hy, BOARD_R, pcbnew.Edge_Cuts)
edge_band(0.5)
for i, (x, y) in enumerate(STANDOFFS, 1):
    hole("H%d" % i, x, y, 3.2, "M3 standoff on A22 (5/95, +-35)")
    circle(x, y, SO_KEEPOUT_D, pcbnew.F_SilkS, 0.12); rule_area_annulus(x, y, SO_KEEPOUT_D, SO_DRILL + 2.0, "standoff keep-out H%d" % i)
# sites for the fit check and the record
rect((SA868_C[0] - 17.8, SA868_C[1] - 9.5, SA868_C[0] + 17.8, SA868_C[1] + 9.5), pcbnew.Dwgs_User, 0.1)
text("SA868 VHF exciter (bench-fitted): PTT and audio to the codec set, ANT to the T/R relay", SA868_C[0] + 2.0, SA868_C[1] + 12.5, pcbnew.F_SilkS, 0.85, 0.15)
text("T/R relay K1 and the 5-pole low-pass filter along the south edge; J_ANT -> A22 VHF jack J_RF1 pigtail", 5.0, -37.5, pcbnew.F_SilkS, 0.85, 0.15)
text("PA leads on the south edge: J_PAIN drive U.FL, J_PAOUT output SMA, J_VGG gate bias; VDD 13.8 V from A22 J_PA direct", 5.0, 37.5, pcbnew.F_SilkS, 0.85, 0.15)
text("J_HARN1 <- A22 J_MEZZ1", J_HARN[0] + 2.0, J_HARN[1] + 13.0, pcbnew.F_SilkS, 0.85, 0.15); text("J_PWR1 +5V_D8", J_PWR[0] + 2.0, J_PWR[1] - 6.5, pcbnew.F_SilkS, 0.85, 0.15)
text("headset leads J_HS1 / J_HS2 from the face plate jacks (SPK MIC PTT GND GND)", 30.0, 0.8, pcbnew.F_SilkS, 0.85, 0.15)
for k, r in ZONES.items(): rect(r, pcbnew.Dwgs_User, 0.12); text(k, (r[0] + r[2]) / 2, r[3] - 1.2, pcbnew.Dwgs_User, 0.9, 0.15)
line(-3, 0, 3, 0, pcbnew.Dwgs_User); line(0, -3, 0, 3, pcbnew.Dwgs_User); text("BOARD DATUM = CASE (50, 0)", 0, -4.5, pcbnew.Dwgs_User, 0.9, 0.15)
text("PCB-D APRS MEZZANINE  REV A (%s)" % PHASE, 0, -36.0, pcbnew.B_SilkS, 1.4, 0.22, mirror=True)
text("MESHSAT-830 | 100x80x1.6 4L | 2026-09-07", 0, -38.5, pcbnew.B_SilkS, 0.9, 0.15, mirror=True)
text("CASE EAST (+X) ->", 42.0, -38.5, pcbnew.F_SilkS, 0.9, 0.15); text("NORTH (+Y)", -42.0, 37.5, pcbnew.F_SilkS, 0.9, 0.15)
pcbnew.SaveBoard(OUT, board)
print("saved", OUT, "holes: 4")
