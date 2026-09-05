#!/usr/bin/env python3
"""Footprints for the PCB-C control panel, the dock and the RF junction, written into meshsat.pretty. Usage: gen_footprints_panel.py <meshsat.pretty dir>
Panel-mount switches are bench parts: the footprint is the panel hole (with the maker's keyway or D flat where the seal needs it) plus
solder lands on the underside for their flying leads, arranged around the hole outside the switch body (C5: no plated hole on the face
except the LEDs and the frame screws, so rain on the face has no path into the case). All dimensions mm."""
import sys, os, math
OUT = sys.argv[1] if len(sys.argv) > 1 else "../meshsat.pretty"
def head(name, descr, tags, attr):
    return ['(footprint "%s"' % name, '\t(version 20241229)', '\t(generator "meshsat")', '\t(generator_version "9.0")', '\t(layer "F.Cu")',
            '\t(descr "%s")' % descr, '\t(tags "%s")' % tags, '\t(attr %s)' % attr,
            '\t(property "Reference" "REF**" (at 0 -%.2f 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))',
            '\t(property "Value" "VAL**" (at 0 %.2f 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))']
def circle(cx, cy, r, layer, w=0.12): return '\t(fp_circle (center %.3f %.3f) (end %.3f %.3f) (stroke (width %g) (type default)) (fill no) (layer "%s"))' % (cx, cy, cx + r, cy, w, layer)
def rect(x0, y0, x1, y1, layer, w=0.1): return '\t(fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width %g) (type default)) (fill no) (layer "%s"))' % (x0, y0, x1, y1, w, layer)
def npth(x, y, d): return '\t(pad "" np_thru_hole circle (at %.3f %.3f) (size %.2f %.2f) (drill %.2f) (layers "*.Cu" "*.Mask"))' % (x, y, d, d, d)
def keepout_circle(r, name, n=36):
    """Rule area in the footprint on both copper layers: no tracks, vias or pour inside radius r. Freerouting ignores Edge.Cuts inside a footprint and KiCad
    draws an unplated pad larger than its drill as copper, so a routed outline (keyway notch, D flat) needs this to keep copper off its edge clearance."""
    pts = " ".join("(xy %.3f %.3f)" % (r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n))
    return '\t(zone (net 0) (net_name "") (layers "F&B.Cu") (name "%s") (hatch edge 0.5) (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed)) (polygon (pts %s)))' % (name, pts)
def tht(num, x, y, drill=1.1, size=2.0, shape="circle"): return '\t(pad "%s" thru_hole %s (at %.3f %.3f) (size %.2f %.2f) (drill %.2f) (layers "*.Cu" "*.Mask"))' % (num, shape, x, y, size, size, drill)
def text(t, x, y, layer="F.Fab", size=1.0): return '\t(fp_text user "%s" (at %.3f %.3f) (layer "%s") (effects (font (size %g %g) (thickness 0.15))%s))' % (t, x, y, layer, size, size, " (justify mirror)" if layer.startswith("B.") else "")
WRITTEN = []
def write(name, lines):
    s = "\n".join(lines) + "\n)\n"
    if "%." in s: raise SystemExit("footprint %s has an unformatted label placeholder (head() lines 8 and 9 need the label offset)" % name)   # 5 Sep 2026: BackerScrew shipped with %.2f in it and KiCad loaded None
    open(os.path.join(OUT, name + ".kicad_mod"), "w").write(s); WRITTEN.append(name); print("wrote", name)
def smd_back(num, x, y, w=2.0, h=3.0):
    """Solder land on the underside for a flying lead: the footprint sits on the face (its hole and body are face features), the lead is soldered from below."""
    return '\t(pad "%s" smd rect (at %.3f %.3f) (size %.2f %.2f) (layers "B.Cu" "B.Paste" "B.Mask"))' % (num, x, y, w, h)
def poly(pts, layer, w=0.1, fill="no"):
    return '\t(fp_poly (pts %s) (stroke (width %g) (type default)) (fill %s) (layer "%s"))' % (" ".join("(xy %.3f %.3f)" % p for p in pts), w, fill, layer)
def dflat_outline(d, flat, n=48):
    """D hole: circle d truncated by a chord so the hole measures `flat` across from the round side to the flat (NKK A58: 6.5 with 5.8)."""
    r = d / 2.0; c = flat - r                                                       # chord distance from the centre (positive: the flat cuts the +X side)
    a0 = math.degrees(math.acos(c / r)); pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (360.0 - 2 * a0) * k / n); pts.append((r * math.cos(a), r * math.sin(a)))
    return pts
KEYWAY_W, KEYWAY_D = 2.70, 1.10          # APEM 5000 series K seal cut-out (catalogue page A40): 6.50 hole with a 2.70 wide, 1.10 deep keyway notch
NKK_D_FLAT = 5.8                        # NKK M series D3 bushing cut-out (A58): 6.5 with the flat at 5.8 across
def panel_switch(name, hole, body_d, npads, pad_r, descr, keyway=None, dflat=None):
    """Panel-mount pushbutton or toggle (C5, sealed face): NPTH hole, courtyard = body plus nut, solder lands on the underside for the flying leads.
    keyway = angle in degrees of a KEYWAY_W x KEYWAY_D notch on the hole edge (Edge.Cuts, routed by the fab; 0 = +X, 90 = +y in footprint coordinates, which is KiCad's y-down, i.e. case -Y);
    dflat = angle of an NKK D flat (the drilled hole shrinks to the inscribed circle, the D outline goes on Edge.Cuts for the router)."""
    L = head(name, descr, "panel switch bench sealed", "through_hole"); L[8] %= (body_d / 2 + 2.0); L[9] %= (body_d / 2 + 2.0)
    if dflat is not None:
        r = hole / 2.0; c = NKK_D_FLAT - r
        L.append(npth(0, 0, round(2 * c - 0.05, 2)))                                    # inscribed drill: the router's obstacle; the fab routes the D
        L.append(keepout_circle(hole / 2 + 0.35, "D hole edge clearance"))              # C5 route 1: two tracks sat inside the D outline's edge clearance
        th = math.radians(dflat); pts = [(x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)) for x, y in dflat_outline(hole, NKK_D_FLAT)]
        L.append(poly(pts, "Edge.Cuts", 0.05))
    elif keyway is not None:
        L.append(npth(0, 0, hole)); L.append(keepout_circle(hole / 2 + KEYWAY_D + 0.35, "keyway edge clearance"))
    else:
        L.append(npth(0, 0, hole))
    if keyway is not None:
        th = math.radians(keyway); r = hole / 2.0
        rect_pts = [(r - 0.8, -KEYWAY_W / 2), (r + KEYWAY_D, -KEYWAY_W / 2), (r + KEYWAY_D, KEYWAY_W / 2), (r - 0.8, KEYWAY_W / 2)]
        pts = [(x * math.cos(th) - y * math.sin(th), x * math.sin(th) + y * math.cos(th)) for x, y in rect_pts]
        L.append(poly(pts, "Edge.Cuts", 0.05))                                          # the notch straddles the hole edge; the fab routes it after the drill
    L.append(circle(0, 0, body_d / 2, "F.Fab")); L.append(circle(0, 0, body_d / 2 + 0.5, "F.CrtYd", 0.05)); L.append(circle(0, 0, body_d / 2 + 0.5, "B.CrtYd", 0.05))
    for k in range(npads):                                                                   # no face silk: the gasket or O-ring seats there
        a = math.radians(-90 + 360.0 * k / npads); x, y = pad_r * math.cos(a), pad_r * math.sin(a)
        L.append(smd_back(str(k + 1), x, y, 2.4 if k == 0 else 2.0, 3.0))
    L.append(text("lead lands 1..%d on the underside" % npads, 0, pad_r + 2.5, "B.Fab", 0.8)); write(name, L)
# 19 mm and 16 mm anti-vandal momentary with LED ring: 4 leads (NO, C, LED+, LED-); body Ø22 / Ø18 under the panel, nut Ø24 / Ø20; a die-cut silicone gasket under the bezel seals the face
panel_switch("PanelSwitch_19mm", 19.2, 24.0, 4, 16.0, "19 mm anti-vandal momentary pushbutton with LED ring, IP67, panel hole 19.2, nut 24, gasket washer under the bezel, four lead lands underneath")
panel_switch("PanelSwitch_16mm", 16.2, 20.0, 4, 14.0, "16 mm anti-vandal momentary pushbutton with LED ring, IP67, panel hole 16.2, nut 20, gasket washer under the bezel, four lead lands underneath")
# 6.35 mm bushing toggles: NKK M2044SD3A01 DPDT ON-ON-ON on a D3 splashproof bushing (D flat toward +X, its O-ring under the nut); APEM 5636ADKB-2V locking toggles with the K seal (keyway toward -Y, the operator)
panel_switch("PanelToggle_DPDT", 6.5, 13.0, 6, 11.0, "NKK M2044SD3A01 DPDT ON-ON-ON, D3 bushing IP67 with the AT516 O-ring and the AT428H boot, D hole 6.5 / 5.8 flat toward +X, six lead lands underneath", dflat=0.0)

# C6 (5 Sep 2026, the backer board under the aluminium face plate): the toggles pass THROUGH the backer, so their footprints carry a body slot instead of a
# bushing hole; the plate (v2/cad/face_plate.py) carries the keyed and D holes. The buttons and the sounder pass their own bushing holes.
def body_slot(name, w, h, npads, pad_r, descr):
    L = head(name, descr, "panel switch body slot backer", "through_hole"); L[8] %= (max(w, h) / 2 + 2.0); L[9] %= (max(w, h) / 2 + 2.0)
    L.append('\t(pad "" np_thru_hole oval (at 0 0) (size %.2f %.2f) (drill oval %.2f %.2f) (layers "*.Cu" "*.Mask"))' % (w, h, w, h))
    L.append(rect(-w / 2 - 0.5, -h / 2 - 0.5, w / 2 + 0.5, h / 2 + 0.5, "F.CrtYd", 0.05)); L.append(rect(-w / 2 - 0.5, -h / 2 - 0.5, w / 2 + 0.5, h / 2 + 0.5, "B.CrtYd", 0.05))
    for k in range(npads):
        a = math.radians(-90 + 360.0 * k / npads); x, y = pad_r * math.cos(a), pad_r * math.sin(a)
        L.append(smd_back(str(k + 1), x, y, 2.4 if k == 0 else 2.0, 3.0))
    L.append(text("body slot %.0f x %.0f, lands 1..%d underneath" % (w, h, npads), 0, pad_r + 2.5, "B.Fab", 0.8)); write(name, L)
body_slot("ToggleBody_SPDT", 15.0, 22.0, 3, 15.0, "APEM 5636ADKB-2V body passing the backer board: 15 x 22 slot, three lead lands underneath; the keyed 6.5 hole is in the face plate")
body_slot("ToggleBody_DPDT", 15.0, 12.0, 6, 11.5, "NKK M2044SD3A01 body passing the backer board: 15 x 12 slot, six lead lands underneath; the D hole is in the face plate")
L = head("BackerScrew_M3_GND", "C6 backer screw M3 into the plate's self-clinching standoff: plated hole 3.2, 6.0 mm ring both sides, GND", "backer screw gnd", "through_hole"); L[8] %= 4.5; L[9] %= 4.5
L.append('\t(pad "1" thru_hole circle (at 0 0) (size 6.0 6.0) (drill 3.2) (layers "*.Cu" "*.Mask"))'); L.append(circle(0, 0, 3.5, "F.CrtYd", 0.05)); write("BackerScrew_M3_GND", L)
panel_switch("GuardedToggle_SPDT", 6.5, 13.0, 3, 11.0, "APEM 5636ADKB-2V locking toggle, K front seal (O-ring + U360 gasket), 6.5 hole with the 2.70 x 1.10 keyway toward the operator (case -Y), three lead lands underneath", keyway=90.0)   # footprint +y is KiCad down = case -Y
# panel-mount IP68 sounder Floyd Bell MC-09-530-Q (docs/respin-research-seal-2026-09-04.md f): 1-1/8 in hole (28.575), bezel gasket 61663 on the face,
# body about 34 mm deep behind the panel plus 11 mm of solder tabs, two lead lands underneath outside the body
SOUNDER_HOLE, SOUNDER_BODY, SOUNDER_PAD_R = 28.6, 34.0, 21.5
panel_switch("PanelSounder", SOUNDER_HOLE, SOUNDER_BODY, 2, SOUNDER_PAD_R, "IP68 panel-mount sounder (Floyd Bell MC-09-530-Q class), threaded body through a %.1f mm hole, bezel gasket on the face, two lead lands underneath" % SOUNDER_HOLE)
# frame screw: M3 through a plated GND ring, 8.0 mm land on the underside for the bonded sealing washer; the face side stays under solder mask (flat gasket seat, no bare ring)
L = head("FrameScrew_M3_GND", "1520PF frame screw M3: plated hole 3.2, GND ring 8.0 on the underside under the bonded sealing washer, face masked", "frame screw gnd sealed", "through_hole")
L[8] %= 5.5; L[9] %= 5.5
L.append('\t(pad "1" thru_hole circle (at 0 0) (size 8.0 8.0) (drill 3.2) (layers "*.Cu" "B.Mask"))')
L.append(circle(0, 0, 4.5, "F.CrtYd", 0.05)); L.append(circle(0, 0, 4.5, "B.CrtYd", 0.05)); L.append(circle(0, 0, 4.0, "B.Fab")); write("FrameScrew_M3_GND", L)
# two solder lands for a flying lead pair (the MAIN and PI button leads): 2.0 x 3.0 at 2.5 mm pitch, on the footprint's own side (placed flipped onto the underside)
L = head("LeadLands_1x02", "two solder lands for a 2-wire lead, 2.0 x 3.0 pads at 2.5 mm pitch", "lead lands", "smd"); L[8] %= 3.5; L[9] %= 3.5
for k, x in enumerate((-1.25, 1.25)): L.append('\t(pad "%d" smd %s (at %.3f 0) (size 2.0 3.0) (layers "F.Cu" "F.Paste" "F.Mask"))' % (k + 1, "rect" if k == 0 else "roundrect", x) if k == 0 else '\t(pad "%d" smd rect (at %.3f 0) (size 2.0 3.0) (layers "F.Cu" "F.Paste" "F.Mask"))' % (k + 1, x))
L.append(rect(-2.8, -2.0, 2.8, 2.0, "F.Fab")); L.append(rect(-3.0, -2.2, 3.0, 2.2, "F.CrtYd", 0.05)); L.append(text("1", -1.25, -2.6, "F.Fab", 0.7)); write("LeadLands_1x02", L)
# WeAct 3.7 in e-paper module (reference only since C4, the panel uses a recessed window): outline 105.79 x 53.80, holes Ø3.2 on 100.19 x 48.20 (2.80 from every edge, from the STEP), glass 92.99 x 53.0 between the hole columns; the 92.99 in the WeAct drawing is the glass width, not the hole pitch
L = head("WeAct_EPD_3p7", "WeAct Studio 3.7 in e-paper module 105.79 x 53.80 on four M3 standoffs (holes Ø3.2 on 100.19 x 48.20, glass 92.99 x 53.0); active area 81.5 x 47.0; 8-pin header wired by a lead to J_EPD", "epaper module bench", "through_hole")
L[8] %= 29.0; L[9] %= 29.0
W, H = 105.79, 53.80; cx, cy = W / 2, H / 2
holes = [(2.80 - cx, 2.80 - cy), (W - 2.80 - cx, 2.80 - cy), (2.80 - cx, H - 2.80 - cy), (W - 2.80 - cx, H - 2.80 - cy)]
for (x, y) in holes: L.append(npth(x, y, 3.2)); L.append(circle(x, y, 3.0, "F.Fab"))
L.append(rect(-cx, -cy, cx, cy, "F.Fab")); L.append(rect(-cx - 0.5, -cy - 0.5, cx + 0.5, cy + 0.5, "F.CrtYd", 0.05)); L.append(rect(-cx, -cy, cx, cy, "F.SilkS", 0.15))
L.append(rect(-40.77, -23.5, 40.77, 23.5, "F.Fab")); L.append(text("E-PAPER 3.7in ACTIVE 81.5 x 47.0", 0, 0, "F.Fab", 1.2)); L.append(text("header end", cx - 8, 0, "F.Fab", 0.8))
write("WeAct_EPD_3p7", L)
# spring-pin dock: 4 pins per polarity on the stack side (Mill-Max 0906/0965 class, Ø1.5 hole) and matching 3 mm gold target pads on the dock; 2.54 mm pitch, two rows
for name, target in (("PogoPins_2x4", False), ("PogoTargets_2x4", True)):
    L = head(name, "spring-pin dock, 2 x 4 contacts at 2.54 mm: pins on the stack side, flat gold targets on the dock", "pogo dock", "through_hole" if not target else "smd")
    L[8] %= 5.0; L[9] %= 5.0
    n = 1
    for row in (-1.27, 1.27):
        for col in range(4):
            x = (col - 1.5) * 2.54
            if target: L.append('\t(pad "%d" smd circle (at %.3f %.3f) (size 2.0 2.0) (layers "F.Cu" "F.Mask"))' % (n, x, row))   # 2.0 at 2.54 pitch: 0.54 mm between targets; 3.0 overlapped
            else: L.append(tht(str(n), x, row, 1.5, 2.2))
            n += 1
    L.append(rect(-6.0, -3.0, 6.0, 3.0, "F.Fab")); L.append(rect(-6.5, -3.5, 6.5, 3.5, "F.CrtYd", 0.05)); write(name, L)
# guide pin (Ø4 dowel, chamfered) seat: Ø4.1 NPTH on the dock, Ø4.3 on the stack side
for name, d in (("GuidePin_Dock", 4.1), ("GuidePin_Stack", 4.3)):
    L = head(name, "landing guide pin seat, %s mm hole" % d, "guide pin dock", "through_hole"); L[8] %= 4.0; L[9] %= 4.0
    L.append(npth(0, 0, d)); L.append(circle(0, 0, 4.0, "F.CrtYd", 0.05)); L.append(circle(0, 0, 3.5, "F.SilkS")); write(name, L)


# self-test (5 Sep 2026): every footprint written above must load in KiCad, or the chain stops here instead of at a silent "not found" later
try:
    import pcbnew
    bad = [n for n in WRITTEN if pcbnew.FootprintLoad(OUT, n) is None]
    if bad: raise SystemExit("footprints KiCad cannot load: %s" % ", ".join(bad))
    print("footprint self-test: %d loaded" % len(WRITTEN))
except ImportError:
    print("footprint self-test skipped (no pcbnew)")
