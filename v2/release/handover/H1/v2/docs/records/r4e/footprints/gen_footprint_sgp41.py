#!/usr/bin/env python3
"""Draft footprint for the Sensirion SGP41-D-R4 (MESHSAT-1357 round 4, board E, item S-10; 26 September 2026).

KiCad 9.0.9's own libraries hold no land for this package (the Sensirion lands they carry are DFN-4 for the SHT4x,
DFN-8 and the SCD4x), so the land is written here from the maker's figure and nothing else:
  Sensirion "Datasheet SGP41", version 1.0, December 2021 (v2/vendor/sensirion/sgp41-datasheet.pdf,
  sha256 331f35ed1f027a74ec79b302763f7adb920759bc055b3d2ada17822bb0005bec):
  - Table 6 (page 7): 1 VDD, 2 VSS, 3 SDA, 4 n/a (connect to ground), 5 VDDH, 6 SCL; the die pad is ground.
  - Figure 17 (page 18): body 2.44 x 2.44 x 0.85 mm, pitch 0.8, pin 1 at the top left of the top view, the die pad's
    triangular cut marks pin 1 seen from below.
  - Figure 18 (page 19), the recommended land (top view): pads 0.55 x 0.4 mm, their centres 2.3 mm apart across the
    body and 0.8 mm apart along it; the exposed pad 1.25 x 1.7 mm with a 0.3 x 45 degree chamfer at the pin-1 corner;
    stencil aperture on the exposed pad 1.05 x 1.5 mm; pads non-solder-mask-defined; stencil 125 to 150 um.
  The 2.3 figure was read as centre to centre by measuring the rendered page (drafts/datasheets/img/sgp41_p-19.png):
  it spans the centres of the two pad columns, and the other reading (outer edge to outer edge) would put the pads'
  inner edges 0.025 mm INSIDE the exposed pad, which the drawing plainly does not show.

This file is a DRAFT in the round-4 worktree. It belongs in v2/ecad/meshsat.pretty (through a footprint generator the
board declares in boards/e.json `footprint_generator`, as board B does), which this author may not write; the box run
pointed KISCH_FP_DIRS at drafts/footprints so kisch could judge U17's pin map against this land.
Usage: gen_footprint_sgp41.py <meshsat.pretty dir>
"""
import os, sys

NAME = "Sensirion_DFN-6-1EP_2.44x2.44mm_P0.8mm_EP1.25x1.7mm"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "meshsat.pretty")
os.makedirs(OUT, exist_ok=True)

PAD_W, PAD_H, X_C, PITCH = 0.55, 0.40, 2.30 / 2.0, 0.80        # Figure 18
EP_W, EP_H, EP_CH = 1.25, 1.70, 0.30                          # Figure 18, chamfer 0.3 x 45 degrees at pin 1
PASTE_W, PASTE_H = 1.05, 1.50                                 # Figure 18 stencil aperture on the exposed pad
BODY = 2.44                                                   # Figure 17
# counter-clockwise from pin 1 at the top left of the top view (Table 6 and Figure 6 agree: VDD, VSS, SDA down the
# left, n/a, VDDH, SCL up the right). KiCad's y axis points down, so "top" is negative y.
PADS = [("1", -X_C, -PITCH), ("2", -X_C, 0.0), ("3", -X_C, PITCH),
        ("4", X_C, PITCH), ("5", X_C, 0.0), ("6", X_C, -PITCH)]

cx = X_C + PAD_W / 2.0 + 0.25                                 # courtyard 0.25 mm past the pads (IPC-7351 nominal)
cy = BODY / 2.0 + 0.25
lines = []
a = lines.append
a('(footprint "%s"' % NAME)
a('\t(version 20240108)')
a('\t(generator "meshsat")')
a('\t(generator_version "9.0")')
a('\t(layer "F.Cu")')
a('\t(descr "Sensirion SGP41-D-R4 VOC and NOx sensor, DFN-6 2.44 x 2.44 x 0.85 mm, 0.8 mm pitch; land of the SGP41 '
  'datasheet version 1.0 (December 2021) Figure 18, pin map Table 6; keep the sensor opening (top, bottom-right '
  'corner) free of conformal coating and wash")')
a('\t(tags "DFN-6 SGP41 Sensirion gas sensor VOC NOx")')
a('\t(property "Reference" "REF**" (at 0 -2.30 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))')
a('\t(property "Value" "%s" (at 0 2.30 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))' % NAME)
a('\t(property "Footprint" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))')
a('\t(property "Datasheet" "v2/vendor/sensirion/sgp41-datasheet.pdf (Sensirion, version 1.0, December 2021)" '
  '(at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))')
a('\t(property "Description" "" (at 0 0 0) (layer "F.Fab") (hide yes) (effects (font (size 1.27 1.27))))')
a('\t(attr smd)')
for num, x, y in PADS:
    a('\t(pad "%s" smd rect (at %.3f %.3f) (size %.2f %.2f) (layers "F.Cu" "F.Paste" "F.Mask"))' % (num, x, y, PAD_W, PAD_H))
# exposed pad: copper and mask on the numbered pad, paste on its own reduced aperture (an unnumbered pad, which
# kisch.land_pads does not count as a pin)
a('\t(pad "7" smd roundrect (at 0 0) (size %.2f %.2f) (layers "F.Cu" "F.Mask") (roundrect_rratio 0) '
  '(chamfer_ratio %.3f) (chamfer top_left))' % (EP_W, EP_H, EP_CH / EP_W))
a('\t(pad "" smd rect (at 0 0) (size %.2f %.2f) (layers "F.Paste"))' % (PASTE_W, PASTE_H))
h = BODY / 2.0
a('\t(fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.10) (type solid)) (fill no) (layer "F.Fab"))' % (-h, -h, h, h))
a('\t(fp_rect (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))' % (-cx, -cy, cx, cy))
# silk: two short corner marks clear of the pads and a pin-1 dot outside the body at the top left
s = h + 0.12
for (x0, y0, x1, y1) in ((-0.55, -s, 0.55, -s), (-0.55, s, 0.55, s)):
    a('\t(fp_line (start %.3f %.3f) (end %.3f %.3f) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))' % (x0, y0, x1, y1))
a('\t(fp_circle (center %.3f %.3f) (end %.3f %.3f) (stroke (width 0.12) (type solid)) (fill yes) (layer "F.SilkS"))'
  % (-cx + 0.10, -h - 0.35, -cx + 0.20, -h - 0.35))
a(')')
path = os.path.join(OUT, NAME + ".kicad_mod")
open(path, "w").write("\n".join(lines) + "\n")
print("wrote", path)
