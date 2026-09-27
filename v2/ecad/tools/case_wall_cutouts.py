#!/usr/bin/env python3
"""1:1 marking templates for the Peli 1450's walls and check prints of the made plates, for the arrangement chosen on 26 and 27 Sep 2026
(C2, C3 and C4 of v2/docs/CASE-MARGINS.md, the session's choices SC-07 under the owner's standing rule of 26 Sep 2026). MESHSAT-1357.

Every position comes from v2/ecad/tools/panel1450.py (CONN_PLATE, CONN_ITEMS, RF_PLATE, WALL_EAST, WALL_WEST, SMA_Z); nothing is typed here twice.
Sheets (A4 landscape, 1:1; print at 100 percent, no fit to page, and check the 100 mm bar with a rule):
  1 BACK WALL, seen from OUTSIDE (case +X, east, on your LEFT): the connector plate's footprint, its six wall holes (hole saws 29, 22, 18,
    drill 8) and six 4.5 screw holes; the hinge fairings' bases at |X| 58.93; the Z datum.
  2 EAST WALL, seen from OUTSIDE (case +Y, the hinge wall, on your RIGHT): the RF entry plate's footprint, five 27 mm hole-saw holes at Z 59 and
    eight 5.0 screw holes; the inner ribs at Y 0 and +-76.2 (inside) and the outer features at Y 0 and +-79.0 for orientation.
  3 WEST WALL, seen from OUTSIDE (case +Y on your LEFT): the same plate outline, seven 27 mm holes and eight 5.0 screw holes.
  4 CONNECTOR PLATE check print, seen from outside: outline, cut-outs, M3 tap centres, 4.5 screw holes.
  5 and 6 RF ENTRY PLATE check prints (east, west), seen from outside: outline, 16.3 holes, the 26.0 spot-faces on the back (dashed),
    M4 tap centres.
A seventh file, face-plate-1to1-A3.pdf, is the face plate's check print on A3 (written by the same call with --face).
The earlier issue of this file (2306b0e6) drew a 54 x 82 x 3 plate between ribs no Peli file has and eleven Amphenol 132170 couplers at
Z 88, and drew both end walls as if seen from inside while labelling them as seen from outside; it is superseded (release/revA/case/README.md).
The Z datum is the cavity floor inside: transfer it to the outside with a height gauge (the floor is not visible from outside). Marking from a
paper template is +-0.3 (INFERRED; CASE-MARGINS.md section 1): a drilling jig would make it a stated tolerance.
Prototype: nothing has been cut. Usage: case_wall_cutouts.py <out.pdf> [--face <face-plate.dxf> <out-A3.pdf>]   (reportlab, ezdxf)."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import panel1450 as L
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

TW = 0.0349 / 0.9994; HX0, HY0 = 186.97, 129.82      # Peli's drafted inner walls (STEP, CASE-MARGINS.md 2.3)
OUT_FLAT_Z, RIM_FLANGE_Z = 15.9, 97.91                # the back wall's outer bottom radius ends; the outer rim flange starts (DXF A-A, B-B)
FAIR_X = 58.93                                        # hinge fairings' bases (DXF top view)
RIBS_END = (-76.2, 0.0, 76.2); RIB_Z = (26.42, 84.58)
FEATURES = (-79.0, 0.0, 79.0); FEAT_Z = 92.4


class Sheet:
    def __init__(self, c, W, H, ox_mm, oz_mm, sgn):
        """sgn: +1 draws case coordinate u to the paper's right, -1 to the left; (ox_mm, oz_mm): paper mm of u 0, z 0."""
        self.c, self.W, self.H, self.ox, self.oz, self.s = c, W, H, ox_mm, oz_mm, sgn
    def P(self, u, z): return (self.ox + self.s * u) * mm, (self.oz + z) * mm
    def line(self, u0, z0, u1, z1, w=0.3, dash=None):
        c = self.c; c.setLineWidth(w); c.setDash(*dash) if dash else c.setDash(); c.line(*self.P(u0, z0), *self.P(u1, z1)); c.setDash()
    def circle(self, u, z, d, w=0.5, dash=None):
        c = self.c; c.setLineWidth(w); c.setDash(*dash) if dash else c.setDash(); x, y = self.P(u, z); c.circle(x, y, d / 2 * mm, stroke=1, fill=0); c.setDash()
    def cross(self, u, z, r=3.0): self.line(u - r, z, u + r, z, 0.2); self.line(u, z - r, u, z + r, 0.2)
    def rect(self, u0, z0, u1, z1, w=0.4, dash=None, r=0.0):
        c = self.c; c.setLineWidth(w); c.setDash(*dash) if dash else c.setDash()
        (ax, az), (bx, bz) = self.P(u0, z0), self.P(u1, z1)
        if r: c.roundRect(min(ax, bx), min(az, bz), abs(bx - ax), abs(bz - az), r * mm, stroke=1, fill=0)
        else: c.rect(min(ax, bx), min(az, bz), abs(bx - ax), abs(bz - az), stroke=1, fill=0)
        c.setDash()
    def text(self, u, z, s, size=6.5, anchor="c", angle=0):
        c = self.c; x, y = self.P(u, z); c.saveState(); c.translate(x, y); c.rotate(angle); c.setFont("Helvetica", size)
        {"c": c.drawCentredString, "r": c.drawRightString}.get(anchor, c.drawString)(0, 0, s); c.restoreState()
    def ptext(self, x_mm, y_mm, s, size=6.5, anchor="l"):
        c = self.c; c.setFont("Helvetica", size); {"c": c.drawCentredString, "r": c.drawRightString}.get(anchor, c.drawString)(x_mm * mm, y_mm * mm, s)
    def scale_bar(self, x_mm, y_mm):
        c = self.c; c.setLineWidth(1.0); c.line(x_mm * mm, y_mm * mm, (x_mm + 100) * mm, y_mm * mm)
        for xx in (x_mm, x_mm + 100): c.setLineWidth(0.6); c.line(xx * mm, (y_mm - 2) * mm, xx * mm, (y_mm + 2) * mm)
        self.ptext(x_mm + 50, y_mm - 4.5, "100 mm at 1:1: print at 100 percent, no fit to page; check with a rule", 6.5, "c")
    def notes(self, lines, x_mm, y_mm, width=165, size=6.0):
        import textwrap
        k = 0
        for n in lines:
            for part in textwrap.wrap(n, width): self.ptext(x_mm, y_mm - 3.3 * k, part, size); k += 1
            k += 0.35
    def title(self, s, sub=""):
        self.c.setFont("Helvetica-Bold", 9); self.c.drawString(8 * mm, self.H - 9 * mm, s)
        if sub: self.c.setFont("Helvetica", 6.5); self.c.drawString(8 * mm, self.H - 13 * mm, sub)
    def footer(self, n, of):
        self.ptext(8, 5, "MeshSat V2 case set, MESHSAT-1357, 27 Sep 2026: v2/ecad/tools/case_wall_cutouts.py from panel1450.py. Prototype: nothing cut. Sheet %d of %d." % (n, of), 5.5)


def back_wall(c, W, H, n, of):
    P = L.CONN_PLATE
    s = Sheet(c, W, H, W / mm / 2, 45.0, -1.0)
    s.title("SHEET %d: BACK WALL (hinge side, case +Y), seen from OUTSIDE: case +X (east) is on your LEFT" % n,
            "The connector plate (C3): footprint dashed, wall holes solid. Tape the sheet on the outer skin with its floor line at the cavity floor's height (transfer it from inside).")
    s.line(-75, 0, 75, 0, 0.8); s.ptext(8, 45 + 1.2, "cavity floor Z 0 (inside): transfer from inside", 6)
    s.line(-75, OUT_FLAT_Z, 75, OUT_FLAT_Z, 0.3, (2, 2)); s.ptext(8, 45 + OUT_FLAT_Z + 1.2, "outer bottom radius ends ~Z 15.9", 5.5)
    s.line(-75, RIM_FLANGE_Z, 75, RIM_FLANGE_Z, 0.3, (2, 2)); s.ptext(8, 45 + RIM_FLANGE_Z + 1.2, "outer rim flange from Z 97.9", 5.5)
    for fx in (-FAIR_X, FAIR_X):
        s.line(fx, 10, fx, 100, 0.3, (1, 1.5)); s.text(fx, 101.5, "fairing base |X| 58.93", 5.0)
    s.rect(P["x0"], P["z0"], P["x1"], P["z1"], 0.4, (3, 2), r=P["corner_r"])
    for it in L.CONN_ITEMS:
        x, z = it["c"]; s.circle(x, z, it["wall_hole"], 0.7); s.cross(x, z, 5)
        s.text(x, z + 1.5, it["key"], 8); s.text(x, z - it["wall_hole"] / 2 - 3.2, "%s %.0f at X %+.1f Z %.1f" % ("hole saw" if it["wall_hole"] >= 18 else "drill", it["wall_hole"], x, z), 5.2)
    for (x, z) in P["screws"]: s.circle(x, z, P["screw_hole"], 0.5); s.cross(x, z, 3)
    s.text(0, P["z1"] + 3, "plate and gasket outline X %.1f..%.1f, Z %.1f..%.1f; six 4.5 at X +-51.1, Z 24.2 / 50.1 / 76.0" % (P["x0"], P["x1"], P["z0"], P["z1"]), 6)
    s.scale_bar(15, 33)
    s.notes(["Items (panel1450.CONN_ITEMS): A sealed RJ45 (pick OPEN), C shore DC D38999/20 sh 13, B sealed USB-C (panel drawing OPEN), E the pod's M8 receptacle (OPEN), "
             "D USB host 233-370 sh 15, F ground stud M6 (OPEN). Cut: drill the six 4.5 and the 8 first, then the hole saws from outside; deburr both faces; dry-fit the "
             "plate and its gasket before any sealant. The X 0 rib (inside, 0.75 proud) may lie on this wall: holes C and D cross it; nothing bears on it (T1 photos tell).",
             "Checks this sheet serves: T1 (the fairings' extent down the wall), T5 (read the wall's thickness from each hole, 4.58 to 6.10 assumed), T6 (the plate on "
             "plain skin all round, the open lid clear of the mated plugs). OPEN rows: M14a, M14b, M14i, M14m (CASE-MARGINS.md 3.2)."], 8, 25)
    s.footer(n, of)


def end_wall(c, W, H, n, of, wall):
    R = L.RF_PLATE; sites = L.WALL_EAST if wall == "east" else L.WALL_WEST
    sgn = 1.0 if wall == "east" else -1.0
    s = Sheet(c, W, H, W / mm / 2, 45.0, sgn)
    s.title("SHEET %d: %s END WALL (case %sX), seen from OUTSIDE: case +Y (the hinge wall) is on your %s" % (n, wall.upper(), "+" if wall == "east" else "-", "RIGHT" if sgn > 0 else "LEFT"),
            "The RF entry plate (C4): footprint dashed, wall holes solid. Tape the sheet on the outer skin with its floor line at the cavity floor's height (transfer it from inside).")
    s.line(-128, 0, 128, 0, 0.8); s.ptext(8, 45 + 1.2, "cavity floor Z 0 (inside): transfer from inside", 6)
    for ry in RIBS_END: s.line(ry, RIB_Z[0], ry, RIB_Z[1], 0.3, (1, 1.5))
    s.text(76.2, RIB_Z[1] + 1.5, "inner ribs Y 0, +-76.2 (inside)", 5.0)
    for fy in FEATURES: s.circle(fy, FEAT_Z, 7.5, 0.3, (1, 1))
    s.text(0, FEAT_Z + 5.5, "outside features Y 0, +-79.0 at Z 92.4 (orientation marks)", 5.0)
    s.rect(-R["y"], R["z0"], R["y"], R["z1"], 0.4, (3, 2), r=R["corner_r"])
    for name, y in sites:
        s.circle(y, L.SMA_Z, R["wall_hole"], 0.7); s.cross(y, L.SMA_Z, 5)
        s.text(y, L.SMA_Z + R["wall_hole"] / 2 + 1.5, name, 6); s.text(y, L.SMA_Z - R["wall_hole"] / 2 - 3.0, "Y %+.0f" % y, 5.5)
    for (y, z) in R["screws"]: s.circle(y, z, R["wall_screw_hole"], 0.5); s.cross(y, z, 3)
    s.text(0, R["z1"] + 9.5, "plate and gasket outline Y +-%.1f, Z %.2f..%.2f; hole saw 27 at Z %.1f on a 31 pitch; eight 5.0 at Y +-45, +-100, Z 40.65 / 77.35" % (
        R["y"], R["z0"], R["z1"], L.SMA_Z), 6)
    s.scale_bar(15, 33)
    s.notes(["Arrestors (panel1450.WALL_%s): the ruled PolyPhaser GTH-SFF-AL, tightened on the RF entry plate on the bench, then the plate goes on its gasket with eight "
             "M4 x 12 A2 button heads from inside on rubber-faced sealing washers. Cut: drill the eight 5.0 first, then the 27 hole saws from outside; deburr; dry-fit." % wall.upper(),
             "Checks this sheet serves: T5 (wall thickness at each hole), T6 (the plate on plain skin all round), T11 (one arrestor on its plate). OPEN rows: M10, M11c, M11d, "
             "M11e, M11g, M13, M13c; inside, the jumpers (M17a to M17x, M18; M17g and M17x FAIL AS ASSUMED until the plug is picked)."], 8, 25)
    s.footer(n, of)


def conn_plate_print(c, W, H, n, of):
    P = L.CONN_PLATE
    s = Sheet(c, W, H, W / mm / 2, 60.0, -1.0)
    s.title("SHEET %d: CONNECTOR PLATE check print, 1:1, seen from OUTSIDE (case +X on your LEFT)" % n,
            "%s, %.1f thick. Cut-outs solid; M3 tap centres (drill 2.5) small; 4.5 screw holes. Z is the case's (the plate spans Z %.1f..%.1f)." % (P["material"], P["t"], P["z0"], P["z1"]))
    s.rect(P["x0"], P["z0"] - 40, P["x1"], P["z1"] - 40, 0.8, r=P["corner_r"])
    for it in L.CONN_ITEMS:
        x, z = it["c"]; z -= 40
        if it["key"] == "B":
            s.circle(x, z, it["cutout"], 0.7); s.line(x - 4, z - L.CONN_B_FLAT, x + 4, z - L.CONN_B_FLAT, 0.7); s.text(x, z - L.CONN_B_FLAT - 2.8, "flat %.2f to -Z" % L.CONN_B_FLAT, 5)
        else:
            s.circle(x, z, it["cutout"], 0.7)
        s.cross(x, z, 4); s.text(x, z + 1.2, it["key"], 7)
        s.text(x, z - it["cutout"] / 2 - 2.8, "%.2f%s" % (it["cutout"], " PROVISIONAL" if it["status"] == "OPEN" else ""), 5)
        if it["screws"]:
            q = it["screws"][0] / 2
            for dx in (-q, q):
                for dz in (-q, q): s.circle(x + dx, z + dz, 2.5, 0.4)
    for (x, z) in P["screws"]: s.circle(x, z - 40, P["screw_hole"], 0.5); s.cross(x, z - 40, 2.5)
    s.scale_bar(15, 30)
    s.notes(["A cut-out marked PROVISIONAL is the class's; it is cut only after the picked part's own panel drawing confirms it (CASE-MARGINS.md section 6)."], 8, 22)
    s.footer(n, of)


def rf_plate_print(c, W, H, n, of, wall):
    R = L.RF_PLATE; sites = L.WALL_EAST if wall == "east" else L.WALL_WEST; sgn = 1.0 if wall == "east" else -1.0
    s = Sheet(c, W, H, W / mm / 2, 20.0, sgn)
    s.title("SHEET %d: RF ENTRY PLATE, %s, check print 1:1, seen from OUTSIDE (case +Y on your %s)" % (n, wall.upper(), "RIGHT" if sgn > 0 else "LEFT"),
            "%s. 16.3 through at each arrestor; the 26.0 spot-face 1.5 deep is on the BACK (dashed); M4 tapped through (tap centres, drill 3.3). Z is the case's." % R["material"])
    s.rect(-R["y"], R["z0"], R["y"], R["z1"], 0.8, r=R["corner_r"])
    for name, y in sites:
        s.circle(y, L.SMA_Z, R["hole"], 0.7); s.circle(y, L.SMA_Z, R["spot"][0], 0.4, (2, 1.5)); s.cross(y, L.SMA_Z, 4)
        s.text(y, R["z1"] + 2, name, 6)
    for (y, z) in R["screws"]: s.circle(y, z, 3.3, 0.5); s.cross(y, z, 2.5)
    s.scale_bar(15, 12)
    s.footer(n, of)


def face_print(dxf_fn, out_fn):
    """The face plate on A3 at 1:1 from its DXF (outline, through cuts, the rebate line, the relief pocket), seen from above."""
    import ezdxf
    doc = ezdxf.readfile(dxf_fn); msp = doc.modelspace()
    c = canvas.Canvas(out_fn, pagesize=landscape(A3)); W, H = landscape(A3)
    ox, oy = W / 2, H / 2 + 1 * mm   # the plate's top edge 16 mm under the page's, clear of the title lines
    def P(x, y): return ox + x * mm, oy + y * mm
    styles = {"OUTLINE": (0.8, None), "THROUGH": (0.5, None), "POCKET_1MM": (0.3, (2, 1.5)), "REBATE_2MM_TOP": (0.3, (4, 2)),
              "RELIEF_0.8MM_UNDERSIDE": (0.3, (1, 1)), "STANDOFF_M3": (0.4, None)}
    for e in msp:
        w, dash = styles.get(e.dxf.layer, (0.3, None)); c.setLineWidth(w); c.setDash(*dash) if dash else c.setDash()
        if e.dxftype() == "CIRCLE":
            x, y = P(e.dxf.center.x, e.dxf.center.y); c.circle(x, y, e.dxf.radius * mm, stroke=1, fill=0)
        elif e.dxftype() == "LWPOLYLINE":
            pts = [P(p[0], p[1]) for p in e.get_points("xy")]
            path = c.beginPath(); path.moveTo(*pts[0])
            for q in pts[1:]: path.lineTo(*q)
            if e.closed: path.close()
            c.drawPath(path, stroke=1, fill=0)
        elif e.dxftype() == "LINE":
            c.line(*P(e.dxf.start.x, e.dxf.start.y), *P(e.dxf.end.x, e.dxf.end.y))
    c.setDash()
    c.setFont("Helvetica-Bold", 9); c.drawString(10 * mm, H - 6.5 * mm, "FACE PLATE check print, 1:1 on A3, seen from above (C1): 377.2 x 263.0 x 3.0")
    c.setFont("Helvetica", 6.5)
    c.drawString(10 * mm, H - 10.5 * mm, "Solid: outline and through cuts. Long dashes: the rebate line (outside it the band is 2.0 lower). Short dashes: the e-paper pocket. Dots: the 0.8 relief in the UNDERSIDE.")
    c.setLineWidth(1.0); c.line(10 * mm, 8 * mm, 110 * mm, 8 * mm); c.drawCentredString(60 * mm, 4 * mm, "100 mm at 1:1: print at 100 percent on A3, no fit to page")
    c.drawString(250 * mm, 4 * mm, "MeshSat V2 case set, MESHSAT-1357, 27 Sep 2026: case_wall_cutouts.py --face from face-plate.dxf. Prototype: nothing cut.")
    c.showPage(); c.save(); print("wrote", out_fn)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "case-templates-1to1.pdf"
    c = canvas.Canvas(out, pagesize=landscape(A4)); W, H = landscape(A4); of = 6
    back_wall(c, W, H, 1, of); c.showPage()
    end_wall(c, W, H, 2, of, "east"); c.showPage()
    end_wall(c, W, H, 3, of, "west"); c.showPage()
    conn_plate_print(c, W, H, 4, of); c.showPage()
    rf_plate_print(c, W, H, 5, of, "east"); c.showPage()
    rf_plate_print(c, W, H, 6, of, "west"); c.showPage()
    c.save(); print("wrote", out)
    if "--face" in sys.argv:
        k = sys.argv.index("--face"); face_print(sys.argv[k + 1], sys.argv[k + 2])
