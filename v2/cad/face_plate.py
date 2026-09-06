#!/usr/bin/env python3
"""The aluminium face plate of the MeshSat field kit in the Peli 1450 (owner ruling 5 Sep 2026, appendix 32.40 item 5, 32.42).

365.5 x 249.5 x 3.0 mm 5754 or 6061, black anodised, clamped under the 1450PF frame ring inside its skirt with the PORON gasket ring on its 8 mm band
(the construction of 32.34, the plate replacing the PCB as the weather face). Cut-outs, all from v2/ecad/tools/panel1450.py: the ten M3 holes at the
frame's inserts, the display aperture inside a 1.0 mm pocket for the glass and its tape frame, the e-paper window inside a pocket for its 2 mm lens,
three round holes for the C&K buttons, three 6.5 mm holes with the APEM K keyway, the NKK D hole, the sounder hole, sixteen 2.6 mm H7 holes for the press-fit Mentor 1282.5004 IP68
light pipes, six self-clinching M3 standoff holes for the C6 backer board. Legends and the logo are laser marked from the SVG this script also writes.
Usage: face_plate.py <out dir>   (build123d in ~/.venv-cad on the VM). Writes face-plate.step, face-plate.stl, face-plate.dxf (the outline and every
through cut, for DataPro or JLC CNC) and face-plate-marking.svg; prints the sizes. Plate frame = case frame (X, Y from the case centre), Z up."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ecad", "tools"))
import panel1450 as L
from build123d import Box, Cylinder, Location, Vector, Axis, Rectangle, RectangleRounded, Plane, extrude, export_step, export_stl, Sketch, Polygon, Circle, Compound
from build123d import BuildSketch, BuildPart, Mode

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(OUT, exist_ok=True)
W, H, T = L.PLATE

def rrect(cx, cy, w, h, r, z0, depth):
    """Rounded-rectangle prism with its bottom at z0."""
    with BuildSketch(Plane.XY.offset(z0)) as sk:
        with Locations((cx, cy)): RectangleRounded(w, h, r)
    return extrude(sk.sketch, amount=depth)
def cyl(cx, cy, d, z0, depth):
    return Cylinder(d / 2, depth).moved(Location(Vector(cx, cy, z0 + depth / 2)))
def dhole(cx, cy, d, flat, flat_dir, z0, depth):
    """Round hole with one flat: a cylinder cut by a box on the flat side."""
    c = cyl(cx, cy, d, z0, depth)
    fx, fy = flat_dir; off = flat - d / 2   # the flat lies flat - d/2 from the centre... measured across: flat is the width across the flats side
    keep = Box(d + 2, d + 2, depth + 2).moved(Location(Vector(cx - fx * (d / 2 + 1 - (d - flat)), cy - fy * (d / 2 + 1 - (d - flat)), z0 + depth / 2)))
    return c & keep
def keyed_hole(cx, cy, d, key_w, key_d, key_dir, z0, depth):
    """Round hole with a rectangular keyway of width key_w reaching key_d beyond the hole edge in key_dir."""
    c = cyl(cx, cy, d, z0, depth); kx, ky = key_dir
    kw, kh = (key_w, d / 2 + key_d) if ky else (d / 2 + key_d, key_w)
    k = Box(kw, kh, depth).moved(Location(Vector(cx + kx * (d / 4 + key_d / 2), cy + ky * (d / 4 + key_d / 2), z0 + depth / 2)))
    return c + k

from build123d import Locations
plate = rrect(0, 0, W, H, L.PLATE_R, 0, T)
cuts = []
# frame screws, from below into the frame's inserts: M3 clearance 3.4
for (x, y) in L.FRAME_BOSSES: cuts.append(cyl(x, y, 3.4, -1, T + 2))
# display: glass pocket 1.0 deep from the top, aperture through
gx, gy = L.DISPLAY["c"]; gw, gh = L.DISPLAY["glass"]; aw, ah = L.DISPLAY["aperture"]
cuts.append(rrect(gx, gy, gw + 0.6, gh + 0.6, 8.3, T - L.DISPLAY["pocket_depth"], L.DISPLAY["pocket_depth"] + 1))
cuts.append(rrect(gx, gy, aw, ah, L.DISPLAY["aperture_r"], -1, T + 2))
# e-paper: lens pocket 1.0 deep, window through
ex, ey = L.EPAPER["c"]; lw, lh = L.EPAPER["lens"]; ww, wh = L.EPAPER["window"]
cuts.append(rrect(ex, ey, lw + 0.4, lh + 0.4, L.EPAPER["lens_r"], T - L.EPAPER["pocket_depth"], L.EPAPER["pocket_depth"] + 1))
cuts.append(rrect(ex, ey, ww, wh, 1.0, -1, T + 2))
# buttons: round holes
for ref, (x, y), d, depth in L.BUTTONS: cuts.append(cyl(x, y, d, -1, T + 2))
# locking toggles: 6.5 with the K keyway toward the operator (-Y)
for ref, (x, y) in L.TOGGLES: cuts.append(keyed_hole(x, y, L.TOGGLE_HOLE, L.TOGGLE_KEY[0], L.TOGGLE_KEY[1], (0, -1), -1, T + 2))
# NKK toggle: D hole, flat toward +X
lx, ly = L.LIGHT[1]; cuts.append(cyl(lx, ly, L.LIGHT_HOLE, -1, T + 2) & Box(L.LIGHT_FLAT + (L.LIGHT_HOLE - L.LIGHT_FLAT), L.LIGHT_HOLE + 2, T + 2).moved(Location(Vector(lx - (L.LIGHT_HOLE - L.LIGHT_FLAT) / 2, ly, T / 2))))
# sounder
sx, sy = L.SOUNDER[1]; cuts.append(cyl(sx, sy, L.SOUNDER[2], -1, T + 2))
# light pipes
for ref, (x, y), name in L.STATUS_LEDS + L.BAR_LEDS: cuts.append(cyl(x, y, L.LED_HOLE, -1, T + 2))
# backer standoffs: self-clinching M3, 4.2 mm hole (PEM SO-M3 in 3 mm aluminium), from the underside
for (x, y) in L.STANDOFFS: cuts.append(cyl(x, y, 4.2, -1, T + 2))
for c in cuts: plate -= c
bb = plate.bounding_box()
export_step(plate, os.path.join(OUT, "face-plate.step")); export_stl(plate, os.path.join(OUT, "face-plate.stl"))
print("face-plate %.1f x %.1f x %.1f mm, volume %.0f mm3 (%.0f g in aluminium)" % (bb.size.X, bb.size.Y, bb.size.Z, plate.volume, plate.volume * 2.7e-3))

# --- DXF of the outline and the through cuts (for the CNC service) and the marking SVG
def dxf_and_svg():
    import ezdxf
    doc = ezdxf.new("R2010"); msp = doc.modelspace(); doc.header["$INSUNITS"] = 4
    def poly_rrect(cx, cy, w, h, r, layer):
        pts = []
        for k in range(0, 91, 15):
            a = math.radians(k)
            for (sx, sy, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)): pass
        # explicit corner arcs
        corners = [(cx + w / 2 - r, cy + h / 2 - r, 0), (cx - w / 2 + r, cy + h / 2 - r, 90), (cx - w / 2 + r, cy - h / 2 + r, 180), (cx + w / 2 - r, cy - h / 2 + r, 270)]
        for (ax, ay, a0) in corners:
            for k in range(0, 91, 10): pts.append((ax + r * math.cos(math.radians(a0 + k)), ay + r * math.sin(math.radians(a0 + k))))
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    def circle(cx, cy, d, layer): msp.add_circle((cx, cy), d / 2, dxfattribs={"layer": layer})
    for name in ("OUTLINE", "THROUGH", "POCKET_1MM", "STANDOFF_M3", "MARKING"): doc.layers.add(name)
    poly_rrect(0, 0, W, H, L.PLATE_R, "OUTLINE")
    for (x, y) in L.FRAME_BOSSES: circle(x, y, 3.4, "THROUGH")
    poly_rrect(gx, gy, aw, ah, L.DISPLAY["aperture_r"], "THROUGH"); poly_rrect(gx, gy, gw + 0.6, gh + 0.6, 8.3, "POCKET_1MM")
    poly_rrect(ex, ey, ww, wh, 1.0, "THROUGH"); poly_rrect(ex, ey, lw + 0.4, lh + 0.4, L.EPAPER["lens_r"], "POCKET_1MM")
    for ref, (x, y), d, depth in L.BUTTONS: circle(x, y, d, "THROUGH")
    for ref, (x, y) in L.TOGGLES:
        circle(x, y, L.TOGGLE_HOLE, "THROUGH"); kw, kd = L.TOGGLE_KEY
        msp.add_lwpolyline([(x - kw / 2, y - 1.0), (x - kw / 2, y - L.TOGGLE_HOLE / 2 - kd), (x + kw / 2, y - L.TOGGLE_HOLE / 2 - kd), (x + kw / 2, y - 1.0)], close=False, dxfattribs={"layer": "THROUGH"})
    circle(lx, ly, L.LIGHT_HOLE, "THROUGH"); msp.add_line((lx + L.LIGHT_FLAT - L.LIGHT_HOLE / 2, ly - 3.0), (lx + L.LIGHT_FLAT - L.LIGHT_HOLE / 2, ly + 3.0), dxfattribs={"layer": "THROUGH"})
    circle(sx, sy, L.SOUNDER[2], "THROUGH")
    for ref, (x, y), name in L.STATUS_LEDS + L.BAR_LEDS: circle(x, y, L.LED_HOLE, "THROUGH")
    for (x, y) in L.STANDOFFS: circle(x, y, 4.2, "STANDOFF_M3")
    doc.saveas(os.path.join(OUT, "face-plate.dxf"))
    # marking SVG: 1 unit = 1 mm, origin at the plate centre, Y up
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.1fmm" height="%.1fmm" viewBox="%.1f %.1f %.1f %.1f">' % (W, H, -W / 2, -H / 2, W, H), '<g transform="scale(1,-1)" font-family="Helvetica, Arial, sans-serif" fill="#ffffff" stroke="none">']
    def txt(x, y, s, size=3.2, anchor="middle"): lines.append('<text x="%.2f" y="%.2f" font-size="%.2f" text-anchor="%s" transform="scale(1,-1)">%s</text>' % (x, -y, size, anchor, s))
    for ref, (x, y), name in L.STATUS_LEDS: txt(x - 4.0, y - 1.1, name, 2.6, "end")
    for k, (ref, (x, y), name) in enumerate(L.BAR_LEDS): txt(x, y + 5.0, "%d" % (20 * (k + 1)), 2.2)
    txt(L.BAR_LEDS[2][1][0], L.BAR_LEDS[2][1][1] - 6.0, "BATTERY %", 2.6)
    for ref, (x, y), d, depth in L.BUTTONS: txt(x, y + d / 2 + 4.0, {"SW_MAIN": "MAIN", "SW_PI": "PI", "SW_TEST": "TEST"}[ref], 3.6)
    for ref, (x, y) in L.TOGGLES: txt(x, y + 13.0, {"SW_SOS": "SOS", "SW_EMCON": "EMCON", "SW_ZERO": "ZEROIZE"}[ref], 3.6)
    txt(lx, ly + 13.0, "LIGHT", 3.6); txt(lx - 10.0, ly, "DAY", 2.4, "end"); txt(lx + 10.0, ly, "NIGHT", 2.4, "start"); txt(lx, ly - 12.0, "BLACKOUT", 2.4)
    txt(sx, sy - 19.0, "SOUNDER", 2.6)
    nx, ny, nw, nh = L.NAMEPLATE; lines.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="#ffffff" stroke-width="0.3"/>' % (nx - nw / 2, -ny - nh / 2, nw, nh))
    txt(nx, ny + 7.5, "MESHSAT FIELD KIT V2", 3.6); txt(nx, ny + 1.5, "S/N ________", 2.6); txt(nx, ny - 5.0, "PELI 1450  DC 12 V  RF HAZARD DURING TX", 2.4)
    txt(L.LOGO[0][0], L.LOGO[0][1], "[MESHSAT LOGO %.0f mm, tools/logo_meshsat.json]" % L.LOGO[1], 2.4)
    lines.append("</g></svg>"); open(os.path.join(OUT, "face-plate-marking.svg"), "w").write("\n".join(lines))
    print("face-plate.dxf and face-plate-marking.svg written")
dxf_and_svg()
print("FACE-PLATE-DONE")
