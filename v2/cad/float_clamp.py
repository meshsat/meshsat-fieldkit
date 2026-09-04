#!/usr/bin/env python3
"""Float nest for the Radiall R222M80500 right-angle SMP-MAX plug on the dock strip (seven sites, appendix 32.25 and 32.32).

Geometry from the Radiall TDS R222.M80.500 issue 1115 A (vendor/rf/radiall-R222M80500-tds.pdf): body 6.5 mm square, far face
10.7 mm from the interface reference plane, cable axis 7.98 mm from it (so 2.7 mm above the strip when the far face rests on the
strip), body about 5.5 mm tall with the round collar and the outer-contact fingers above it, cable pull-off 53 N minimum. The
receptacle under PCB-A (R222M00720) reaches 7.7 mm below the board, which at the 13.4 mm gap is 5.7 mm above the strip, so no
retainer can sit over the plug's shoulder: the plug is held by its own cable, tied into the nest's slot, against the 9 N slide-on
disengagement force, and the nest locates the body with 1.0 mm of radial float and 4.5 mm of guidance while the receptacle's
8.3 mm funnel does the fine centring. Footprint 24 x 16, two M3 clearance holes 20 mm apart matching the strip's clamp holes at
site centre +-10 mm, cable slot toward +X, a tie groove over and under the block.
Usage: float_clamp.py <out dir>  (build123d). Frame: X along the strip, Y across it, Z up from the strip's top face."""
import sys, os
from build123d import Box, Cylinder, Location, Vector, export_step, export_stl

OUT = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(OUT, exist_ok=True)
L, W, H = 16.0, 24.0, 4.5            # block along X, across Y, tall
CAV = 8.5                            # cavity for the 6.5 square body with 1.0 mm float each way
SLOT = 2.8                           # RG-316 is 2.5 mm
def box(w, l, h, x, y, z): return Box(w, l, h).moved(Location(Vector(x + w / 2, y + l / 2, z + h / 2)))
nest = box(L, W, H, -L / 2, -W / 2, 0)
nest -= box(CAV, CAV, H + 2, -CAV / 2, -CAV / 2, -1)                      # body cavity, through
nest -= box(L / 2 + 1, SLOT, H + 2, 0, -SLOT / 2, -1)                     # cable slot to the +X face, full height
nest -= box(L / 2 + 1, SLOT + 2.0, 1.0, 0, -SLOT / 2 - 1.0, 0)           # slot floor relief so the crimp ferrule (2.95) clears the strip
for y in (-10.0, 10.0): nest -= Cylinder(1.7, H + 2).moved(Location(Vector(0, y, H / 2)))   # M3 clearance, strip holes at +-10
nest -= box(3.0, W + 2, 1.0, 2.0, -W / 2 - 1, H - 1.0)                    # tie groove over the block, just past the cavity
nest -= box(3.0, W + 2, 1.0, 2.0, -W / 2 - 1, 0)                          # tie groove under the block (the tie passes under it)
for k in (-1, 1):                                                          # lead-in chamfer along the cavity top edges, as four wedges
    nest -= box(1.0, CAV + 2, 1.0, k * CAV / 2 - (1.0 if k < 0 else 0.0), -CAV / 2 - 1, H - 1.0)
    nest -= box(CAV + 2, 1.0, 1.0, -CAV / 2 - 1, k * CAV / 2 - (1.0 if k < 0 else 0.0), H - 1.0)
bb = nest.bounding_box(); export_step(nest, os.path.join(OUT, "float-nest-smp-max.step")); export_stl(nest, os.path.join(OUT, "float-nest-smp-max.stl"))
print("float-nest-smp-max  %.1f x %.1f x %.1f mm, volume %.0f mm3, seven off" % (bb.size.X, bb.size.Y, bb.size.Z, nest.volume))
print("CLAMP-CAD-DONE")
