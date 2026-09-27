#!/usr/bin/env python3
"""S-12, MESHSAT-1357 round 8 (board B author, 26 September 2026): write the board-B-only land
meshsat.pretty/M2_B-Key_Socket_3052_TE2199119.kicad_mod from the generated M2_B-Key_Socket_3052.kicad_mod
(gen_footprints_b16.py) plus the two locating holes of TE customer drawing C-2199119 rev F, sheet 3
("RECOMMENDED NGFF MINI CARD MOUNTING TYPE_SMT_PCB OUTLINE", v2/vendor/m2/te-2199119-customer-drawing-revF.pdf,
sha256 ef35dbf8332b951c...), read from the rendered sheet:
  - dia 1.1 +-0.05, datum Y, 10 left of the centre line; dia 1.6 +-0.05, datum X, 10 right of it ("20" between them);
  - on the line 4.5 below the inner edge of the odd row's pads and 6.05 below their outer edge, 3.05 above the even
    row's outer edge. The generated land puts the odd row at Y -5.275 (1.55 long: outer edge -6.05, inner edge -4.5) and
    the even row at Y +2.275 (outer edge +3.05), so that line is this land's Y 0.
Both are non-plated (np_thru_hole, no pad number): the connector's locating pegs, not pins. The file is written, not
generated in the pipeline: if gen_footprints_b16.py ever changes the base land, run this again.
Usage: mk_m2b_te2199119.py <meshsat.pretty dir>"""
import os, sys
d = sys.argv[1]
src = open(os.path.join(d, "M2_B-Key_Socket_3052.kicad_mod")).read()
assert src.startswith('(footprint "M2_B-Key_Socket_3052"'), "unexpected base land"
out = src.replace('(footprint "M2_B-Key_Socket_3052"', '(footprint "M2_B-Key_Socket_3052_TE2199119"', 1)
out = out.replace('(descr "M.2 B-key socket', '(descr "TE 2199119-3 M.2 key B socket, 67 positions, 3.2 mm (TE C-2199119 rev F): the B16 land plus the two NPTH locating holes of sheet 3 (dia 1.1 at X -10, dia 1.6 at X +10). M.2 B-key socket', 1)
out = out.replace('(property "Value" "M2_B-Key_Socket_3052"', '(property "Value" "M2_B-Key_Socket_3052_TE2199119"', 1)
holes = ('\t(pad "" np_thru_hole circle (at -10.000 0.000) (size 1.10 1.10) (drill 1.10) (layers "*.Cu" "*.Mask"))\n'
         '\t(pad "" np_thru_hole circle (at 10.000 0.000) (size 1.60 1.60) (drill 1.60) (layers "*.Cu" "*.Mask"))\n')
anchor = '\t(pad "M1" thru_hole circle'
assert out.count(anchor) == 1
out = out.replace(anchor, holes + anchor, 1)
assert out != src
open(os.path.join(d, "M2_B-Key_Socket_3052_TE2199119.kicad_mod"), "w").write(out)
print("wrote", os.path.join(d, "M2_B-Key_Socket_3052_TE2199119.kicad_mod"))
