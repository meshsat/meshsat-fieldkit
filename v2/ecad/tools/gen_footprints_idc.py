#!/usr/bin/env python3
"""Narrow-pad IDC headers, so a differential pair can leave the connector between its columns.

12 September 2026 (MESHSAT-862, appendix 32.124 and decision 6). KiCad's `Connector_IDC` headers carry 1.70 mm
round pads on a 1.00 mm drill at a 2.54 mm grid, which leaves **2.54 - 1.70 = 0.84 mm** between the two
columns. A 0.30/0.20/0.30 pair with its 0.127 class clearance needs **1.054 mm**, so no pair can leave an inner
row of such a header on any layer, the pins being through-hole: the pad is the channel, not the pitch. Board D's
`/USB_D8` and the three pairs of A and B's `J_AB1` are all that, and only an END row escapes it.

This writes the same footprints with the pads narrowed **across the columns only**, 1.40 mm in x and the full
1.70 mm in y, which leaves **1.14 mm** of channel, 0.086 mm more than the pair needs. The ring is then 0.20 mm
on the x sides and 0.35 mm on the y sides, against the 0.15 mm JLCPCB asks for a plated through hole, so the
narrowing is inside the fab's own floor with margin on the axis that carries the solder fillet.

Usage: gen_footprints_idc.py <meshsat.pretty dir> [<kicad Connector_IDC.pretty>]"""
import sys, os, re

SIZES = ("2x05", "2x07", "2x08", "2x09", "2x10", "2x13", "2x20")   # every IDC header the generators name (2x05: the wall-port ribbon J_AB2, 12 September 2026)
PAD_X, PAD_Y = 1.40, 1.70
SRC_DEFAULT = "/usr/share/kicad/footprints/Connector_IDC.pretty"

out_dir = sys.argv[1]
src_dir = sys.argv[2] if len(sys.argv) > 2 else SRC_DEFAULT
if not os.path.isdir(src_dir): sys.exit("gen_footprints_idc: no Connector_IDC.pretty at %s" % src_dir)
os.makedirs(out_dir, exist_ok=True)

n_written = 0
for s in SIZES:
    name = "IDC-Header_%s_P2.54mm_Vertical" % s
    src = os.path.join(src_dir, name + ".kicad_mod")
    if not os.path.exists(src): continue
    t = open(src, errors="replace").read()
    # every through-hole pad of the pin field is 1.7 x 1.7 on a 1.0 drill; the 1 x 1 ones are the shroud marks
    before = len(re.findall(r"\(size 1\.7 1\.7\)", t))
    t = t.replace("(size 1.7 1.7)", "(size %.2f %.2f)" % (PAD_X, PAD_Y))
    new = name + "_NarrowPad"
    # Rename by replacing the STEM everywhere first and only then checking the header: renaming the header and
    # then replacing the stem gives "..._NarrowPad_NarrowPad", a footprint whose internal name does not match
    # its file, which `pcbnew.FootprintLoad` answers with None and no message. That took B's whole chain down
    # to 27 footprints and 52 identical gate failures on the first run (12 September 2026), which is the same
    # silent shape as the malformed BackerScrew of 5 September.
    t = t.replace(name, new)
    if ('(footprint "%s"' % new) not in t: sys.exit("gen_footprints_idc: %s did not take its new name" % new)
    if (new + "_NarrowPad") in t: sys.exit("gen_footprints_idc: %s was renamed twice" % new)
    open(os.path.join(out_dir, new + ".kicad_mod"), "w").write(t)
    print("gen_footprints_idc: wrote %s, %d pads narrowed to %.2f x %.2f (channel %.2f mm)"
          % (new, before, PAD_X, PAD_Y, 2.54 - PAD_X))
    n_written += 1
print("gen_footprints_idc: %d footprint(s)" % n_written)
if not n_written: sys.exit("gen_footprints_idc: nothing written, which is not a success")
