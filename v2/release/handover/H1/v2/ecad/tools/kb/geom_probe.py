#!/usr/bin/env python3
"""geom_probe.py, the measurable facts of a vendor CAD model, as text (MESHSAT-862, 10 September 2026).

Half of what this project needs from `v2/vendor/` is not in a datasheet, it is in a STEP or a DXF: the
hole pattern of the e-paper module, the envelope of a socket, the rib positions of the case. Those
files are binary as far as search is concerned, so they sit in the store as documents with no text and
the mechanical claims of the record rest on whoever probed the model that day.

This writes what a probe finds beside the model, as a plain text file the store then indexes like any
other document: the envelope, every distinct hole diameter with its count, and the pattern each hole
group forms. Nothing here is a rendering or an approximation of geometry; it is the coordinates the
file itself carries.

  STEP is ISO-10303-21 ASCII, so CARTESIAN_POINT, AXIS2_PLACEMENT_3D and CIRCLE are read directly,
  with no CAD library and no venv, which is why this runs on the runner as well as on the box.
  DXF is read by group code, which is the same idea.

Verified against a fact the record already carries: the WeAct 3.7 e-paper module's holes, probed from
its own STEP on 5 September, sit on 100.19 x 48.20 mm. If this tool disagrees with that, it is wrong.

Usage: geom_probe.py [path ...]      (default: every model under v2/vendor/)
       geom_probe.py --selftest      (the WeAct hole pattern, the one number we can check)
"""
import sys, os, re, glob, math, hashlib, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "vendor"))
MODEL_EXT = (".step", ".stp", ".dxf", ".x_t")
TOL = 1e-4          # mm, when two radii or coordinates count as the same

RE_POINT = re.compile(r"#(\d+)\s*=\s*CARTESIAN_POINT\s*\(\s*'[^']*'\s*,\s*\(([^)]*)\)", re.I)
RE_AXIS = re.compile(r"#(\d+)\s*=\s*AXIS2_PLACEMENT_3D\s*\(\s*'[^']*'\s*,\s*#(\d+)", re.I)
RE_CIRCLE = re.compile(r"#\d+\s*=\s*CIRCLE\s*\(\s*'[^']*'\s*,\s*#(\d+)\s*,\s*([0-9.eE+-]+)\s*\)", re.I)
RE_MILLI = re.compile(r"\.MILLI\.\s*,?\s*\.METRE\.", re.I)
RE_ASSY = re.compile(r"NEXT_ASSEMBLY_USAGE_OCCURRENCE", re.I)
HOLE_MIN_D = 0.5     # below this a circle is an edge fillet or a pad corner, never a hole


def _f(s):
    try:
        return float(s)
    except ValueError:
        return None


def read_step(path):
    """(points, circles, units). A circle is (diameter, x, y, z) with the centre resolved through its
    placement, because CIRCLE carries an axis reference and not a coordinate."""
    text = open(path, encoding="utf-8", errors="replace").read()
    n_assy = len(RE_ASSY.findall(text))
    pts = {}
    for m in RE_POINT.finditer(text):
        xyz = [_f(v.strip()) for v in m.group(2).split(",")]
        if len(xyz) == 3 and None not in xyz:
            pts[m.group(1)] = tuple(xyz)
    axis = {m.group(1): m.group(2) for m in RE_AXIS.finditer(text)}
    circles = []
    for m in RE_CIRCLE.finditer(text):
        p = pts.get(axis.get(m.group(1), ""))
        r = _f(m.group(2))
        if p and r:
            circles.append((2.0 * r,) + p)
    return list(pts.values()), circles, ("mm" if RE_MILLI.search(text) else "unknown"), n_assy


def read_dxf(path):
    """DXF by group code: 10/20/30 are coordinates, 40 a radius on a CIRCLE entity.

    Only the ENTITIES section is read. The HEADER section uses the same group codes for its variables,
    and $EXTMIN/$EXTMAX in an empty or unbounded drawing are written as 1e20, which turned one Peli
    drawing into a part two hundred billion kilometres across."""
    pts, circles = [], []
    cur_ent, cx, cy, cz, cr = None, None, None, 0.0, None
    in_entities = False
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    for i in range(0, len(lines) - 1, 2):
        code, val = lines[i].strip(), lines[i + 1].strip()
        if code == "2" and val.upper() in ("HEADER", "CLASSES", "TABLES", "BLOCKS", "ENTITIES", "OBJECTS"):
            in_entities = (val.upper() == "ENTITIES")
            continue
        if not in_entities:
            continue
        if code == "0":
            if cur_ent == "CIRCLE" and cx is not None and cr:
                circles.append((2.0 * cr, cx, cy, cz))
            cur_ent, cx, cy, cz, cr = val.upper(), None, None, 0.0, None
        elif code == "10":
            cx = _f(val)
        elif code == "20":
            cy = _f(val)
            if cx is not None and cy is not None:
                pts.append((cx, cy, 0.0))
        elif code == "30":
            cz = _f(val) or 0.0
        elif code == "40" and cur_ent == "CIRCLE":
            cr = _f(val)
    if cur_ent == "CIRCLE" and cx is not None and cr:
        circles.append((2.0 * cr, cx, cy, cz))
    return pts, circles, "drawing units (a DXF declares no unit here)", 0


_BOUNDS = {}


def _limits(points):
    """Per axis, a generous robust interval: the quartiles widened by ten interquartile ranges.

    Construction geometry is not rare and not small: the LimeSDR model puts four percent of its points
    at plus and minus 400,000 mm, so a fixed percentile trim does not reach them while ten IQRs does,
    and on a well behaved part ten IQRs is so wide that nothing real is ever cut."""
    key = id(points)
    if key in _BOUNDS:
        return _BOUNDS[key]
    lim = []
    for axis in range(3):
        v = sorted(p[axis] for p in points)
        n = len(v)
        q1, q3 = v[int(0.25 * (n - 1))], v[int(0.75 * (n - 1))]
        iqr = max(q3 - q1, 1e-6)
        lim.append((q1 - 10 * iqr, q3 + 10 * iqr))
    _BOUNDS[key] = lim
    return lim


def _inlier(q, points):
    lim = _limits(points)
    return all(lim[a][0] <= q[a] <= lim[a][1] for a in range(3))


def bbox(points, lo=0.0, hi=1.0):
    """The bounding box of a point set, optionally between two quantiles per axis.

    The quantile form exists because exporters write construction geometry into the same point list:
    the LimeSDR model carries points at +-400,000 mm, so its raw box reads 800 metres across. Trimming
    a quarter percent from each end gives the body; both are printed, and a large gap between them is
    said out loud rather than smoothed over."""
    if not points:
        return None
    out = []
    for axis in range(3):
        v = sorted(p[axis] for p in points)
        i = int(lo * (len(v) - 1)); j = int(hi * (len(v) - 1))
        out += [v[i], v[j]]
    return tuple(out)


def group_circles(circles):
    """Distinct diameters, each with its centres. Coaxial duplicates (the two faces of one hole, and
    every surface the modeller drew through it) collapse to one, or a four-hole plate reads as forty."""
    groups = {}
    for d, x, y, z in circles:
        key = round(d, 3)
        groups.setdefault(key, []).append((x, y, z))
    out = []
    for d in sorted(groups):
        seen = []
        for (x, y, z) in groups[d]:
            if not any(abs(x - a) < 0.05 and abs(y - b) < 0.05 for a, b in seen):
                seen.append((x, y))
        out.append((d, seen))
    return out


def describe(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".x_t":
        return None                       # Parasolid is not a text format we can read honestly
    pts, circles, units, n_assy = (read_dxf(path) if ext == ".dxf" else read_step(path))
    if not pts:
        return None
    b = bbox(pts)
    body = [q for q in pts if _inlier(q, pts)] or pts
    trim = bbox(body)
    n_out = len(pts) - len(body)
    raw_span = max(b[1] - b[0], b[3] - b[2], b[5] - b[4])
    trim_span = max(trim[1] - trim[0], trim[3] - trim[2], trim[5] - trim[4])
    contaminated = n_out > 0 and trim_span > 0 and raw_span > 3 * trim_span
    rel = os.path.relpath(path, VENDOR)
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    L = []
    name = os.path.splitext(os.path.basename(rel))[0]
    L.append("Geometry of %s, probed from %s" % (name, rel))
    L.append("")
    L.append("Written by tools/kb/geom_probe.py, not hand edited, so that a CAD model's measurable")
    L.append("facts can be searched and reviewed as text instead of living only in whoever opened the")
    L.append("model that day. Units: %s. EVERY NUMBER IS A MEASUREMENT OF THIS FILE, NOT A" % units)
    L.append("SPECIFICATION: a vendor model may carry a connector, an antenna or a mounting boss the")
    L.append("catalogue dimension leaves out, and it may be exported in any orientation. Where the")
    L.append("manufacturer publishes a drawing, the drawing wins and this is how to find the number")
    L.append("to check against it.")
    L.append("")
    L.append("source file: %s" % rel)
    L.append("sha256 (first 16): %s" % h)
    L.append("size: %d bytes" % os.path.getsize(path))
    L.append("points read: %d" % len(pts))
    L.append("")
    if n_assy:
        # An assembly holds every component in ITS OWN coordinate system and places them through
        # transforms this reader does not apply. A bounding box over the raw points is then a number
        # about nothing: the WeAct module, 105 x 54 mm, reads as 845 x 421 mm that way. Say so, and
        # do not print an envelope that would be quoted later as a measurement.
        L.append("%s ENVELOPE: NOT MEASURED. This file is an assembly (%d component occurrences)," % (name, n_assy))
        L.append("  and each component's coordinates are its own; placing them needs a CAD kernel, which this")
        L.append("  reader deliberately is not. Open the model, or probe a single-part file instead.")
        L.append("  For the record, the raw spread of all points, which is NOT the part size:")
        L.append("  X %.1f to %.1f, Y %.1f to %.1f, Z %.1f to %.1f" % (b[0], b[1], b[2], b[3], b[4], b[5]))
    else:
        if ext == ".dxf":
            L.append("%s EXTENTS OF THE DRAWING SHEET. This is a 2D drawing, not a solid: the box below" % name)
            L.append("is the sheet, several views sit on it at different places, and only the circle")
            L.append("centres further down are positions within a view.")
        else:
            L.append("%s ENVELOPE (single part, so the bounding box of its points is the part)." % name)
        L.append("Axes are THE FILE'S OWN: a vendor model is often exported Y up, and this reader does")
        L.append("not turn it, so read the three extents as sizes and not as width, depth and height.")
        if contaminated:
            L.append("  This file also carries construction geometry far outside the body. The raw box is")
            L.append("  %.0f x %.0f x %.0f, which is not the part. With the %d outlying points removed"
                     % (b[1] - b[0], b[3] - b[2], b[5] - b[4], n_out))
            L.append("  (%.1f percent of the file), the body is:" % (100.0 * n_out / len(pts)))
            L.append("  axis 1 %.3f to %.3f   extent %.3f" % (trim[0], trim[1], trim[1] - trim[0]))
            L.append("  axis 2 %.3f to %.3f   extent %.3f" % (trim[2], trim[3], trim[3] - trim[2]))
            L.append("  axis 3 %.3f to %.3f   extent %.3f" % (trim[4], trim[5], trim[5] - trim[4]))
        else:
            L.append("  axis 1 %.3f to %.3f   extent %.3f" % (b[0], b[1], b[1] - b[0]))
            L.append("  axis 2 %.3f to %.3f   extent %.3f" % (b[2], b[3], b[3] - b[2]))
            L.append("  axis 3 %.3f to %.3f   extent %.3f" % (b[4], b[5], b[5] - b[4]))
    L.append("")
    groups = group_circles(circles)
    small = [(d, c) for d, c in groups if d < HOLE_MIN_D]
    groups = [(d, c) for d, c in groups if d >= HOLE_MIN_D]
    if groups:
        L.append("%s HOLES AND ROUND FEATURES of %.1f mm and over, coaxial duplicates collapsed."
                 % (name, HOLE_MIN_D))
        L.append("In an assembly a pattern is still true WITHIN the component that carries it, which is")
        L.append("how a module's mounting holes come out right.")
        for d, centres in groups:
            if len(centres) > 64:
                L.append("  %s: diameter %.3f : %d centres (too many to be a hole pattern, not listed)" % (name, d, len(centres)))
                continue
            xs = [c[0] for c in centres]; ys = [c[1] for c in centres]
            span = ""
            if len(centres) > 1:
                span = "   pattern %.3f x %.3f" % (max(xs) - min(xs), max(ys) - min(ys))
            # the model's name on every group line, because these files are otherwise near identical
            # and a search for one module's hole pattern returned a different module's
            L.append("  %s: diameter %.3f : %d %s%s"
                     % (name, d, len(centres), "hole" if len(centres) == 1 else "holes", span))
            for (x, y) in sorted(centres)[:12]:
                L.append("      at X %.3f  Y %.3f" % (x, y))
    else:
        L.append("%s HOLES: no circle of %.1f mm or more is in this file" % (name, HOLE_MIN_D))
    if small:
        L.append("")
        L.append("(%d smaller circle sizes were read and are not listed: below %.1f mm they are edge"
                 % (len(small), HOLE_MIN_D))
        L.append("fillets and pad corners, not holes.)")
    L.append("")
    return "\n".join(L) + "\n"


def selftest():
    """The WeAct 3.7 e-paper module: the record says its holes are on 100.19 x 48.20 mm."""
    cand = glob.glob(os.path.join(VENDOR, "weact", "Hardware", "*.step"))
    if not cand:
        print("selftest: the WeAct module STEP is not in this tree"); return 3
    pts, circles, _u, _a = read_step(cand[0])
    best = None
    for d, centres in group_circles(circles):
        if len(centres) == 4:
            xs = [c[0] for c in centres]; ys = [c[1] for c in centres]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            if 90 < w < 110 and 40 < h < 60:
                best = (d, w, h)
    if not best:
        print("selftest: no four-hole pattern near the recorded size was found"); return 1
    d, w, h = best
    ok = abs(w - 100.19) < 0.05 and abs(h - 48.20) < 0.05
    print("selftest: WeAct 3.7 holes, diameter %.2f, pattern %.2f x %.2f mm against the record's "
          "100.19 x 48.20 -> %s" % (d, w, h, "MATCH" if ok else "DISAGREES"))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    paths = a.paths or [p for p in glob.glob(os.path.join(VENDOR, "**", "*"), recursive=True)
                        if os.path.splitext(p)[1].lower() in MODEL_EXT]
    wrote = skipped = 0
    for p in sorted(paths):
        try:
            text = describe(p)
        except Exception as e:
            print("geom_probe: %s failed (%s: %s)" % (os.path.relpath(p, VENDOR), type(e).__name__, e))
            skipped += 1
            continue
        if not text:
            print("geom_probe: %s carries no readable geometry" % os.path.relpath(p, VENDOR))
            skipped += 1
            continue
        out = os.path.splitext(p)[0] + ".geom.txt"
        open(out, "w").write(text)
        wrote += 1
        print("geom_probe: %s" % os.path.relpath(out, VENDOR))
    print("geom_probe: %d written, %d skipped" % (wrote, skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
