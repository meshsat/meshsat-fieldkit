#!/usr/bin/env python3
"""Float clamp BAR for the Radiall R222M80500 right-angle SMP-MAX plugs on the dock strip (appendix 32.25 and 32.32; one bar
for every blind-mate site since MESHSAT-1357 round 8, findings A09 and R4E-07, and owner ruling D-07's third 5G site).

Geometry from the Radiall TDS R222.M80.500 issue 1115 A (vendor/rf/radiall-R222M80500-tds.pdf): body 6.5 mm square, far face
10.7 mm from the interface reference plane, cable axis 7.98 mm from it (so 2.7 mm above the strip when the far face rests on the
strip), body about 5.5 mm tall with the round collar and the outer-contact fingers above it, cable pull-off 53 N minimum. The
receptacle under PCB-A (R222M00720) reaches 7.7 mm below the board, which at the 13.4 mm gap is 5.7 mm above the strip, so no
retainer can sit over the plug's shoulder: the plug is held by its own cable, tied into its slot, against the 9 N slide-on
disengagement force, and each cavity locates the body with 1.0 mm of radial float and 4.5 mm of guidance while the receptacle's
8.3 mm funnel does the fine centring.

WHY A BAR (26 to 26 September 2026). The first design was a 16 x 24 mm nest per site. The sites are 14 mm apart (12 mm from
IRIDIUM to LORA), so neighbouring nests overlapped by 2 to 4 mm, the LORA nest crossed the rod H2's standoff keep-out, and each
nest's cable slot left toward +X straight into the next nest (A09, R4E-07). One bar holds every cavity at board A's receptacle X
with 3.5 mm or more of material between cavities, its M3 clamp holes sit at the mid-pitch points (no cavity and no slot there),
and each cable slot leaves toward -Y or +Y, the side CASE-MARGINS.md section 3.4 routes that jumper from.

THE SITES ARE NOT TYPED HERE: they, the slot sides and the bar's dimensions are read (ast, never grepped) from
v2/ecad/tools/gen_pcb_e.py, which draws the same bar on the board, so the part and its footprint cannot drift apart.

Cable retention: two 1.6 x 3.0 mm tie slots through the side rail, one each side of the cable slot and 1.0 mm off the cavity,
joined by a 1.0 mm groove over the rail's top and a 1.0 mm groove under it, so a 2.5 mm cable tie passes down one slot, under the cable, up the other and
over the cable, closing the cable into its slot without loading the plug body.
Usage: float_clamp.py <out dir>  (build123d). Frame: case X along the strip, case Y across it, Z up from the strip's top face.
"""
import ast, os, sys
from build123d import Box, Cylinder, Location, Vector, export_step, export_stl

OUT = sys.argv[1] if len(sys.argv) > 1 else "."; os.makedirs(OUT, exist_ok=True)
GEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecad", "tools", "gen_pcb_e.py")


def _consts(path, names):
    """The literal values of top-level assignments in gen_pcb_e.py (single names and tuple unpacking), or refuse."""
    tree = ast.parse(open(path, encoding="utf-8").read()); got = {}
    for n in tree.body:
        if not isinstance(n, ast.Assign): continue
        for t in n.targets:
            if isinstance(t, ast.Name) and t.id in names: got[t.id] = ast.literal_eval(n.value)
            elif isinstance(t, ast.Tuple) and isinstance(n.value, ast.Tuple):
                for k, e in enumerate(t.elts):
                    if isinstance(e, ast.Name) and e.id in names: got[e.id] = ast.literal_eval(n.value.elts[k])
    miss = sorted(set(names) - set(got))
    if miss: raise SystemExit("float_clamp: gen_pcb_e.py does not define %s" % miss)
    return got


C = _consts(GEN, ("RF_SITES", "CLAMP_Y", "CLAMP_W", "CLAMP_H", "CLAMP_CAV", "CLAMP_WALL", "CLAMP_HOLE_DY", "CLAMP_SLOT",
                  "CLAMP_SLOT_DIR"))
XS = sorted(float(x) for x, _ in C["RF_SITES"])
W, H, CAV, WALL, HDY, SLOT = C["CLAMP_W"], C["CLAMP_H"], C["CLAMP_CAV"], C["CLAMP_WALL"], C["CLAMP_HOLE_DY"], C["CLAMP_SLOT"]
X0, X1 = XS[0] - CAV / 2 - WALL, XS[-1] + CAV / 2 + WALL
if min(b - a for a, b in zip(XS, XS[1:])) - CAV < 3.5 - 1e-9: raise SystemExit("float_clamp: less than 3.5 mm between cavities")
TIE_W, TIE_L, TIE_DX = 1.6, 3.0, SLOT / 2 + 1.6      # tie slot size (X by Y) and its centre's offset from the cable slot's axis


def box(lx, ly, lz, x, y, z):
    """A box by its minimum corner (x, y, z) and its lengths."""
    return Box(lx, ly, lz).moved(Location(Vector(x + lx / 2, y + ly / 2, z + lz / 2)))


# the frame's Y is measured from the bar's centre line (the receptacles' RF_Y on the board)
bar = box(X1 - X0, W, H, X0, -W / 2, 0)
for x in XS:
    d = int(C["CLAMP_SLOT_DIR"][x]); ye = d * W / 2
    bar -= box(CAV, CAV, H + 2, x - CAV / 2, -CAV / 2, -1)                                  # body cavity, through
    y0 = min(d * CAV / 2 - d * 0.5, ye + d * 1.0); y1 = max(d * CAV / 2 - d * 0.5, ye + d * 1.0)
    bar -= box(SLOT, y1 - y0, H + 2, x - SLOT / 2, y0, -1)                                  # cable slot to the -Y or +Y face
    bar -= box(SLOT + 2.0, y1 - y0, 1.0, x - SLOT / 2 - 1.0, y0, 0)                         # slot floor relief (crimp ferrule 2.95)
    yt = d * (CAV / 2 + 1.0 + TIE_L / 2)                                                    # tie slots 1.0 mm off the cavity, clear of the M3 holes
    for sx in (-1, 1):
        bar -= box(TIE_W, TIE_L, H + 2, x + sx * TIE_DX - TIE_W / 2, yt - TIE_L / 2, -1)
    bar -= box(2 * TIE_DX + TIE_W, TIE_L, 1.0, x - TIE_DX - TIE_W / 2, yt - TIE_L / 2, H - 1.0)  # tie groove over the rail
    bar -= box(2 * TIE_DX + TIE_W, TIE_L, 1.0, x - TIE_DX - TIE_W / 2, yt - TIE_L / 2, 0)        # tie groove under the rail
    for k in (-1, 1):                                                                        # lead-in chamfer as four wedges
        bar -= box(1.0, CAV + 2, 1.0, x + k * CAV / 2 - (1.0 if k < 0 else 0.0), -CAV / 2 - 1, H - 1.0)
        bar -= box(CAV + 2, 1.0, 1.0, x - CAV / 2 - 1, k * CAV / 2 - (1.0 if k < 0 else 0.0), H - 1.0)
for a, b in zip(XS, XS[1:]):                                                                 # M3 clearance at mid-pitch, +-HDY
    for y in (-HDY, HDY): bar -= Cylinder(1.7, H + 2).moved(Location(Vector((a + b) / 2, y, H / 2)))
bb = bar.bounding_box()
export_step(bar, os.path.join(OUT, "float-clamp-bar-smp-max.step")); export_stl(bar, os.path.join(OUT, "float-clamp-bar-smp-max.stl"))
print("float-clamp-bar-smp-max  %.2f x %.2f x %.2f mm (X %.2f to %.2f), volume %.0f mm3, %d cavities, %d M3 holes, one off"
      % (bb.size.X, bb.size.Y, bb.size.Z, bb.min.X, bb.max.X, bar.volume, len(XS), 2 * (len(XS) - 1)))
print("CLAMP-CAD-DONE")
