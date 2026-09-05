#!/usr/bin/env python3
"""Numeric verification of PCB-A phase A1."""
import sys, pcbnew, itertools
OX, OY = 150.0, 110.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 285) < 0.005 and abs(y1 - y0 - 160) < 0.005 and abs(x0 + 165) < 0.005 and abs(y1 - 80) < 0.005, "outline 285 x 160, X -165..120 (A19 keeps the outline, 32.22)")
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def fpc(ref):
    bb = fps[ref].GetBoundingBox(False, False); return ((bb.GetLeft() + bb.GetRight()) / 2e6 - OX, OY - (bb.GetTop() + bb.GetBottom()) / 2e6)
def hole_at(x, y, d): return any(r.startswith("H") and abs(case(f.GetPosition())[0] - x) < 0.01 and abs(case(f.GetPosition())[1] - y) < 0.01 and abs(list(f.Pads())[0].GetDrillSize().x / 1e6 - d) < 0.01 for r, f in fps.items())
for (x, y) in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]: check(hole_at(x, y, 3.2), "rod hole at (%.1f, %.1f)" % (x, y))
for (x, y) in [(10, -26), (80, -26), (10, 26), (80, 26)]: check(hole_at(x, y, 3.2), "mezzanine M3 at (%d, %d)" % (x, y))
for ref, (ex, ey) in {"J_DOCK": (-124, -70), "J_PRE1": (-151, -70), "J_CP1": (-147, -73), "J_CN4": (-135, -67), "F3": (-150, -46), "F4": (-125, -46), "F5": (-100, -46), "F2": (-75, -46), "U22": (-148, -20), "U23": (-116, -20), "U24": (-84, -20), "U20": (-50, -58), "U21": (-112, -60), "R52": (-130, -60), "J_BM1": (-100, -66), "J_RF1": (-100, -56), "J_BM7": (103, -64), "J_RF7": (107, -54), "J_RF5": (70, -74), "J_WALL1": (-156, 62), "U6": (-70, 52), "J_MEZZ1": (-8, 8), "J_GPS1": (30, -52), "J_WIFI1": (8, 52.5),
                      }.items():   # A20: no GPS puck or WiFi dongle slots
    if ref not in fps: print("SKIP %s (placed at the netlist stage)" % ref); continue
    cx, cy = fpc(ref); check(abs(cx - ex) < 0.6 and abs(cy - ey) < 0.6, "%s centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cx, cy))
R = {"POWER": (-162, -40, -32, 2), "CTRL": (-162, 2, -118, 36), "DOCKBLK": (-155, -76, -116, -64), "MEZZ": (5, -31, 85, 31), "HUB": (-104, 25, -30, 78), "CHG": (-70, -72, -30, -46),
     "JMEZZ": (-13.5, -6.5, -2.5, 22.5), "JMEZZPWR": (-13, -22.5, -3, -13.5), "JAB": (-85.5, -71.5, -58.5, -60.5), "JLEDS": (-52, -77, -24, -71),
     "BM1": (-106, -72, -94, -60), "BM2": (-90, -72, -78, -60), "BM3": (-32, -72, -20, -60), "BM4": (-18, -72, -6, -60), "BM5": (64, -72, 76, -60), "BM6": (86, -72, 98, -60), "BM7": (98, -69, 108, -59)}
for k, r in R.items(): check(r[0] >= -163 and r[2] <= 118 and r[1] >= -78 and r[3] <= 78, "%s inside outline with 2 mm margin" % k)
def overlap(a, c): return not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
for (ka, a), (kb, c) in itertools.combinations(R.items(), 2):
    if {ka, kb} in ({"CHG", "JAB"}, {"CHG", "JLEDS"}, {"POWER", "DOCKBLK"}, {"JAB", "BM2"}, {"JLEDS", "BM3"}, {"CHG", "BM3"}): continue
    check(not overlap(a, c), "%s and %s do not overlap" % (ka, kb))
def rc(r, c, rad):
    cx = max(r[0], min(c[0], r[2])); cy = max(r[1], min(c[1], r[3])); return ((cx - c[0]) ** 2 + (cy - c[1]) ** 2) ** 0.5 >= rad
for k, r in R.items(): check(all(rc(r, rod, 4.5) for rod in [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]), "%s clear of the nut keep-outs" % k)
hl = [(case(f.GetPosition()), list(f.Pads())[0].GetDrillSize().x / 1e6) for r, f in fps.items() if r.startswith("H")]
minweb = min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 - (dp + dq) / 2 for (p, dp), (q, dq) in itertools.combinations(hl, 2))
check(minweb >= 2.0, "min web between holes %.2f mm" % minweb)
# 5 Sep 2026 (appendix 32.39): every label net-class pattern must match a net in one of its two forms, and after the route the rail and node widths are read back
import fnmatch as _fn, json as _json, os as _os
_pro = _os.path.splitext(sys.argv[1])[0] + ".kicad_pro"
if _os.path.exists(_pro):
    _pats = [(e["pattern"], e["netclass"]) for e in _json.load(open(_pro)).get("net_settings", {}).get("netclass_patterns", [])]
    _names = {b.GetNetInfo().GetNetItem(k).GetNetname() for k in range(1, b.GetNetInfo().GetNetCount())}
    _dead = {p for p, c in _pats if not any(_fn.fnmatchcase(n, p) for n in _names)}
    _bad = [p for p in _dead if not p.startswith("/") and ("/" + p) in _dead]
    check(not _bad, "every label net-class pattern matches a board net in one of its two forms (unmatched: %s)" % _bad)
_w = {}
for _t in b.GetTracks():
    if _t.GetClass() == "PCB_TRACK" and not _t.IsLocked(): _w.setdefault(_t.GetNetname().lstrip("/"), set()).add(round(_t.GetWidth() / 1e6, 2))
if _w:
    for _n, _min in (("+5V_PI", 0.5), ("+5V_M1", 0.5), ("+5V_M2", 0.5), ("CELL+", 0.6)):   # link widths; the islands, bands and planes carry the current (locked escapes excluded)
        if _n in _w: check(min(_w[_n]) >= _min - 0.01, "%s routed at its class width (>= %.1f mm; widths %s)" % (_n, _min, sorted(_w[_n])))
# A21 (5 Sep 2026): on a filled board every rail band, boost band and output island must be one piece over at least half its outline, and every
# locked 0.8/0.4 stitch via of the M2 and PI rails must sit in the fill of one of its rail's bottom bands (the current path converter -> island -> vias -> band -> riser -> VH).
if any(not z.GetIsRuleArea() and z.GetFilledArea() > 0 for z in b.Zones()):
    for z in b.Zones():
        _n = z.GetZoneName()
        if not z.GetIsRuleArea() and _n.startswith(("rail ", "VOUT island ", "boost ")):
            _fp = z.GetFilledPolysList(z.GetFirstLayer()); _bb = z.GetBoundingBox(); _rect = _bb.GetWidth() / 1e6 * _bb.GetHeight() / 1e6; _area = z.GetFilledArea() / 1e12
            check(_fp.OutlineCount() == 1 and _area >= 0.5 * _rect, "band '%s' is one piece over at least half its outline (%d pieces, %.0f of %.0f mm2)" % (_n, _fp.OutlineCount(), _area, _rect))
    for _t in b.GetTracks():
        if _t.Type() == pcbnew.PCB_VIA_T and _t.IsLocked() and abs(_t.GetDrillValue() / 1e6 - 0.4) < 0.01 and _t.GetNetname().lstrip("/") in ("+5V_M2", "+5V_PI"):
            _zs = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == _t.GetNetname() and z.GetZoneName().startswith("rail ")]
            check(any(z.GetFilledPolysList(pcbnew.B_Cu).Contains(_t.GetPosition()) for z in _zs), "stitch via %s at (%.1f, %.1f) sits in a filled rail band" % (_t.GetNetname(), _t.GetPosition().x / 1e6, _t.GetPosition().y / 1e6))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
