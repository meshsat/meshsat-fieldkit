#!/usr/bin/env python3
"""Numeric verification of PCB-A phase A22 (MESHSAT-830, appendix 32.56): outline, rods, the dock block, the eleven blind-mate sites, the mezzanine, the
zones, the fixed parts; on a placed board the net-class patterns; on a routed board the width read-back of the node and rail nets and the pair report."""
import sys, pcbnew, itertools
OX, OY = 150.0, 110.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []; checked = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    checked.append(m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 240) < 0.005 and abs(y1 - y0 - 160) < 0.005 and abs(x0 + 120) < 0.005 and abs(y1 - 80) < 0.005, "outline 240 x 160, X -120..120 (32.56)")
check(b.GetCopperLayerCount() == 6, "6 copper layers (A22, JLC06161H-3313; under P0 review 11 Sep 2026)")
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
def fpc(ref):
    bb = fps[ref].GetBoundingBox(False, False); return ((bb.GetLeft() + bb.GetRight()) / 2e6 - OX, OY - (bb.GetTop() + bb.GetBottom()) / 2e6)
def hole_at(x, y, d): return any(r.startswith("H") and abs(case(f.GetPosition())[0] - x) < 0.01 and abs(case(f.GetPosition())[1] - y) < 0.01 and abs(list(f.Pads())[0].GetDrillSize().x / 1e6 - d) < 0.01 for r, f in fps.items())
RODS = [(-110.5, -73), (110.5, -73), (-110.5, 73), (110.5, 73)]
for (x, y) in RODS: check(hole_at(x, y, 3.2), "rod hole at (%.1f, %.1f)" % (x, y))
for (x, y) in [(5, -35), (95, -35), (5, 35), (95, 35)]: check(hole_at(x, y, 3.2), "mezzanine M3 at (%d, %d)" % (x, y))
RF_X = [-52, -38, -24, -10, 4, 18, 32, 60, 74, 88, 100]
EXPECT = {"J_DOCK": (-76, -70), "J_PRE1": (-103, -70), "J_CP1": (-99, -73), "J_CN4": (-87, -67), "F1": (-97, -52), "J_AB1": (113, -46), "J_MEZZ1": (-8, 8), "J_MEZZ_PWR1": (-8, -18),
          "U2": (-94, 56), "U3": (-96, 12), "U16": (-96, -26), "U4": (-60, 47), "U7": (-12, 47), "U13": (-44, 6), "U15": (-36, -27), "U18": (10, 65), "U1": (-49, -28), "U27": (-50, -19), "J_PA": (110, 62), "J_54V": (110, 0), "J_MAINSW": (98, 75)}
for k, x in enumerate(RF_X, 1): EXPECT["J_BM%d" % k] = (x, -66); EXPECT["J_RF%d" % k] = (x, -56)
for ref, (ex, ey) in EXPECT.items():
    if ref not in fps: print("SKIP %s (placed at the netlist stage)" % ref); continue
    cx, cy = fpc(ref); check(abs(cx - ex) < 0.6 and abs(cy - ey) < 0.6, "%s centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cx, cy))
R = {"FRONT": (-118, 34, -70, 66), "CHARGER": (-118, -6, -70, 34), "POE": (-118, -44, -70, -6), "RAILS": (-66, 32, -2, 72), "PA": (-66, -14, -16, 20), "MID": (-66, 20, -2, 32), "HF": (-46, -48, -16, -22), "CTRL": (-66, -48, -46, -14), "TPZ": (-88.5, -64, -68, -46),
     "MEZZ": (0, -40, 100, 40), "NE": (0, 44, 100, 72), "EAST": (105, -67, 118, 67), "DOCKBLK": (-104, -78, -66, -64), "JAB": (107.5, -67, 118.5, -25), "FUSE": (-106, -58, -88.5, -46), "JMEZZ": (-13.5, -7, -2.5, 23), "JMEZZPWR": (-13, -22.5, -3, -13.5)}
for k, x in enumerate(RF_X, 1): R["BM%d" % k] = (x - 4.2, -70.5, x + 4.2, -51.5)
for k, r in R.items(): check(r[0] >= -119 and r[2] <= 119 and r[1] >= -79 and r[3] <= 79, "%s inside the outline with a 1 mm margin" % k)
def overlap(a, c): return not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
for (ka, a), (kb, c) in itertools.combinations(R.items(), 2):
    if {ka, kb} in ({"FUSE", "POE"}, {"EAST", "MEZZ"}, {"EAST", "JAB"}, {"MID", "JMEZZ"}): continue
    check(not overlap(a, c), "%s and %s do not overlap" % (ka, kb))
def rc(r, c, rad):
    cx = max(r[0], min(c[0], r[2])); cy = max(r[1], min(c[1], r[3])); return ((cx - c[0]) ** 2 + (cy - c[1]) ** 2) ** 0.5 >= rad
for k, r in R.items(): check(all(rc(r, rod, 4.5) for rod in RODS), "%s clear of the nut keep-outs" % k)
# 8 Sep 2026 (32.66): the region test missed Q2 in the nut keep-out because FEQ was not in the list; every footprint's own box is tested too
_nut = []
for _fp in b.GetFootprints():
    _bb = _fp.GetBoundingBox(False, False); _r = (_bb.GetLeft() / 1e6 - OX, OY - _bb.GetBottom() / 1e6, _bb.GetRight() / 1e6 - OX, OY - _bb.GetTop() / 1e6)
    if not _fp.GetReference().startswith("H") and not all(rc(_r, rod, 4.5) for rod in RODS): _nut.append(_fp.GetReference())   # the rod holes H1 to H4 are the rods
check(not _nut, "every footprint clear of the four rod nut keep-outs (4.5 mm)%s" % ("" if not _nut else ": " + ", ".join(_nut[:8])))
hl = [(case(f.GetPosition()), list(f.Pads())[0].GetDrillSize().x / 1e6) for r, f in fps.items() if r.startswith("H")]
minweb = min(((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5 - (dp + dq) / 2 for (p, dp), (q, dq) in itertools.combinations(hl, 2))
check(minweb >= 2.0, "min web between holes %.2f mm" % minweb)
# PowerPAK FETs (7 Sep 2026): pads 1-3 one net (source), pad 4 the gate, pad 5 the drain tab; a three-pin map left gate and drain on source pins in A22 round 1
for _f in b.GetFootprints():
    if "PowerPAK" in _f.GetFPIDAsString():
        _n = {}
        for _p in _f.Pads(): _n.setdefault(_p.GetNumber(), set()).add(_p.GetNetname())
        check(len(_n.get("1", set()) | _n.get("2", set()) | _n.get("3", set())) == 1 and "" not in _n.get("1", set()) and _n.get("4", {""}) != {""} and _n.get("5", {""}) != {""} and _n.get("4") != _n.get("5"),
              "%s PowerPAK pad map: source 1-3 %s, gate 4 %s, drain 5 %s" % (_f.GetReference(), sorted(_n.get("1", set())), sorted(_n.get("4", set())), sorted(_n.get("5", set()))))
# net-class patterns must match a board net in one of their two forms (5 Sep 2026, 32.39)
import fnmatch as _fn, json as _json, os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
_pro = _os.path.splitext(sys.argv[1])[0] + ".kicad_pro"
if _os.path.exists(_pro) and b.GetNetInfo().GetNetCount() > 1:
    _pats = [(e["pattern"], e["netclass"]) for e in _json.load(open(_pro)).get("net_settings", {}).get("netclass_patterns", [])]
    _names = {b.GetNetInfo().GetNetItem(k).GetNetname() for k in range(1, b.GetNetInfo().GetNetCount())}
    _dead = {p for p, c in _pats if not any(_fn.fnmatchcase(n, p) for n in _names)}
    _bad = [p for p in _dead if not p.startswith("/") and ("/" + p) in _dead]
    check(not _bad, "every label net-class pattern matches a board net in one of its two forms (unmatched: %s)" % _bad)
# routed board: the node and rail nets at their class widths (locked escapes excluded), every differential pair reported
_w = {}
for _t in b.GetTracks():
    if _t.GetClass() == "PCB_TRACK" and not _t.IsLocked() and _t.GetLength() >= 3.0e6: _w.setdefault(_t.GetNetname().lstrip("/"), set()).add(round(_t.GetWidth() / 1e6, 2))   # 3 mm: the escape knees, joins and closures are short
if _w:
    for _n, _min in (("VBAT", 0.5), ("CELL+", 0.5), ("VBUS20", 0.5), ("+5V_S1", 0.4), ("+5V_S2", 0.4), ("+5V_S3", 0.4), ("+5V_DEV", 0.4), ("+13V8_PA", 0.4)):   # A22 run 8: the route campaign closes the board at these widths, the A23 power-copper pass carries the currents
        if _n in _w: check(min(_w[_n]) >= _min - 0.01, "%s routed at its class width (>= %.1f mm; widths %s)" % (_n, _min, sorted(_w[_n])))
# 8 Sep 2026 (MESHSAT-862): the A21 copper checks (pour contiguity, locked vias in fill, cross-layer links) return for A22's 20 A copper, shared in copper_checks.py
import copper_checks as _cc; print(_cc.run(b, check))
_tl = {}
for _t in b.GetTracks():
    if _t.GetClass() == "PCB_TRACK": _tl[_t.GetNetname().lstrip("/")] = _tl.get(_t.GetNetname().lstrip("/"), 0.0) + _t.GetLength() / 1e6
_names = {b.GetNetInfo().GetNetItem(k).GetNetname().lstrip("/") for k in range(1, b.GetNetInfo().GetNetCount())}
for _pair in sorted(set(n[:-2] for n in _names if n.endswith(("_P", "_N")) and (n[:-2] + "_P") in _names and (n[:-2] + "_N") in _names)):   # every pair of the netlist, not only the routed ones (8 Sep 2026)
    _lp, _ln = _tl.get(_pair + "_P", 0.0), _tl.get(_pair + "_N", 0.0)
    if not _lp and not _ln: continue
    if (_lp > 0) != (_ln > 0): check(False, "pair %s has one leg routed and one not (P %.2f mm, N %.2f mm)" % (_pair, _lp, _ln)); continue
    print("%s pair length P %.2f mm, N %.2f mm, mismatch %.2f mm%s" % (("WARN " if abs(_lp - _ln) > 1.0 else "PASS ") + _pair, _lp, _ln, abs(_lp - _ln), "" if abs(_lp - _ln) <= 1.0 else " (over 1.0 mm: add a meander on the short leg)"))
# 8 Sep 2026 (MESHSAT-862 Stage C): the intent gates (return path under the pair-class nets, decoupling loops, the rails of the intent file)
if any(t.GetClass() == "PCB_TRACK" and not t.IsLocked() for t in b.GetTracks()):
    import os as _os3, sys as _sys3; _sys3.path.insert(0, _os3.path.dirname(_os3.path.abspath(__file__))); import intent_checks as _ic; print(_ic.run(b, check, sys.argv[1]))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails))
# The verdict is a file and the exit code, and the denominator travels with it: a bare "0 FAIL" is what a
# gate that ran, a gate that loaded an empty board and a gate whose checks were all skipped all print.
# MESHSAT-862, 11 Sep 2026.
import os as _osv, sys as _sysv
_sysv.path.insert(0, _osv.path.dirname(_osv.path.abspath(__file__)))
import verdict as _v
_nfp = len(list(b.GetFootprints()))
_sysv.exit(_v.write("check_pcb_a",
                    _v.INCONCLUSIVE if not _nfp else (_v.PASS if not fails else _v.FAIL),
                    counts={"fail": len(fails), "pass": len(checked) - len(fails), "footprints": _nfp},
                    denominator=len(checked),
                    evidence=fails,
                    inputs={"board": sys.argv[1]},
                    note="" if _nfp else "the board loaded with no footprints, so nothing here is a judgement of a board"))
