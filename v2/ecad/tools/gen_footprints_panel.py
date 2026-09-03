#!/usr/bin/env python3
"""Footprints for the PCB-C control panel, the dock and the RF junction, written into meshsat.pretty. Usage: gen_footprints_panel.py <meshsat.pretty dir>
Panel-mount switches are bench parts: the footprint is the panel hole plus through-hole solder pads for their flying leads, arranged
around the hole outside the switch body. All dimensions mm."""
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
def tht(num, x, y, drill=1.1, size=2.0, shape="circle"): return '\t(pad "%s" thru_hole %s (at %.3f %.3f) (size %.2f %.2f) (drill %.2f) (layers "*.Cu" "*.Mask"))' % (num, shape, x, y, size, size, drill)
def text(t, x, y, layer="F.Fab", size=1.0): return '\t(fp_text user "%s" (at %.3f %.3f) (layer "%s") (effects (font (size %g %g) (thickness 0.15))))' % (t, x, y, layer, size, size)
def write(name, lines):
    s = "\n".join(lines) + "\n)\n"; open(os.path.join(OUT, name + ".kicad_mod"), "w").write(s); print("wrote", name)
def panel_switch(name, hole, body_d, npads, pad_r, descr):
    """Panel-mount pushbutton or toggle: NPTH hole, courtyard = body plus nut, pads on a ring for the flying leads."""
    L = head(name, descr, "panel switch bench", "through_hole"); L[8] %= (body_d / 2 + 2.0); L[9] %= (body_d / 2 + 2.0)
    L.append(npth(0, 0, hole)); L.append(circle(0, 0, body_d / 2, "F.Fab")); L.append(circle(0, 0, body_d / 2 + 0.5, "F.CrtYd", 0.05)); L.append(circle(0, 0, body_d / 2 + 0.5, "B.CrtYd", 0.05))
    L.append(circle(0, 0, hole / 2 + 0.6, "F.SilkS"))
    for k in range(npads):
        a = math.radians(-90 + 360.0 * k / npads); x, y = pad_r * math.cos(a), pad_r * math.sin(a)
        L.append(tht(str(k + 1), x, y, 1.1, 2.0, "rect" if k == 0 else "circle"))
    L.append(text("lead pads 1..%d" % npads, 0, pad_r + 2.5, "F.Fab", 0.8)); write(name, L)
# 19 mm and 16 mm anti-vandal momentary with LED ring: 4 leads (NO, C, LED+, LED-); body Ø22 / Ø18 under the panel, nut Ø24 / Ø20
panel_switch("PanelSwitch_19mm", 19.2, 24.0, 4, 16.0, "19 mm anti-vandal momentary pushbutton with LED ring, IP67, panel hole 19.2, nut 24, four flying-lead pads")
panel_switch("PanelSwitch_16mm", 16.2, 20.0, 4, 14.0, "16 mm anti-vandal momentary pushbutton with LED ring, IP67, panel hole 16.2, nut 20, four flying-lead pads")
# 6.35 mm bushing toggles (12 mm nut): DPDT ON-ON-ON = 6 leads; SPST guarded = 3 leads (C, NO, NC) for the momentary/latching toggles under a flip cover
panel_switch("PanelToggle_DPDT", 6.5, 13.0, 6, 11.0, "6.35 mm bushing sealed toggle DPDT ON-ON-ON with IP67 boot, panel hole 6.5, nut 13, six flying-lead pads")
panel_switch("GuardedToggle_SPDT", 6.5, 13.0, 3, 11.0, "6.35 mm bushing sealed toggle under a red flip guard (MIL-DTL-3950 style), panel hole 6.5, nut 13, three flying-lead pads; guard base about 20 x 32")
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
