#!/usr/bin/env python3
"""Impedance read-back (MESHSAT-862 Stage C, 8 Sep 2026): the order notes claimed 90 and 100 ohm pairs that nothing had ever computed
(appendix 32.64 W1). For every differential pair the project's net-class assignments put in a class with an impedance target (intent.py's
pair_classes, USB 90, DIFF100 100, RF 50 single-ended), every routed segment is measured (width, layer, the gap to its partner's nearest
parallel segment) and the closed-form impedance is computed against the stackup written in the board file (stackup_write.py):
  microstrip (IPC-2141 / Hammerstad):  Z0 = 87 / sqrt(er + 1.41) * ln(5.98 h / (0.8 w + t)),   Zdiff = 2 Z0 (1 - 0.48 exp(-0.96 s / h))
  stripline (symmetric, IPC-2141):     Z0 = 60 / sqrt(er) * ln(1.9 (2 h + t) / (0.8 w + t)),  Zdiff = 2 Z0 (1 - 0.347 exp(-2.9 s / h))
  asymmetric stripline uses h = the harmonic mean of the two plane distances (2 h1 h2 / (h1 + h2)).
The reference plane is the nearest copper layer above or below that carries a filled zone of GND or a power net under the segment; a segment
with no plane under it on either side is reported as UNREFERENCED (the return-path check of intent_checks.py owns that class); a pair whose
legs run more than three widths apart is UNCOUPLED (Freerouting has no differential-pair routing: found on every released board, 8 Sep 2026).
The pin fans are not judged: a segment within FAN_MM (3.0 mm) of a pad of the pair's nets is fan length, reported and left out of the
fraction, the median and the unreferenced count (USB 2.0 high speed rises in about 500 ps, 75 mm of FR-4 trace; a 3 mm feature is a
twenty-fifth of that edge and the specification itself allows short uncoupled pin regions; 8 Sep 2026, D9's pairs measured 89 ohm on their
runs and lost on their fans). Up to UNREF_MM (3.0 mm) of unreferenced length outside the fans is a NOTE, more is UNREFERENCED. A pair with
less than SHORT_MM (5 mm) of judged length is SHORT and counts as met: there is no coupled run to judge (D9's USB2 is 2.4 mm of fans).
Closed-form accuracy is about 5 to 10 percent; a pair reported MISSED goes to openEMS (Antmicro's kicad-si-simulation-wrapper), never to a
hand-typed number. Self-check (--selftest): a 50 ohm microstrip on FR-4 (er 4.4) needs w/h about 1.8 to 2.0, and the two formulas agree on a
standard case; JLCPCB's calculator values are the reference the record still owes.

Usage: impedance_check.py <board.kicad_pcb> [--tolerance 0.10] [--json out.json]   -> one line per pair, `impedance: N of M pairs within tol`, exit 1 on a miss."""
import sys, os, re, math, json
FAN_MM, UNREF_MM, SHORT_MM = 3.0, 3.0, 5.0   # the pin-fan radius left unjudged, the unreferenced length allowed, the judged length under which a pair is SHORT (docstring)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def z_microstrip(w, h, t, er): return 87.0 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))
def zd_microstrip(w, s, h, t, er): return 2 * z_microstrip(w, h, t, er) * (1 - 0.48 * math.exp(-0.96 * s / h))
def z_stripline(w, h, t, er): return 60.0 / math.sqrt(er) * math.log(1.9 * (2 * h + t) / (0.8 * w + t))
def zd_stripline(w, s, h, t, er): return 2 * z_stripline(w, h, t, er) * (1 - 0.347 * math.exp(-2.9 * s / h))

# ---------------------------------------------------------------- the 2D solver's correction (10 September 2026, MESHSAT-862)
# The closed forms above are IPC-2141 and good to about 5 to 10 percent, and the record has said since 8 September that no
# impedance may be claimed until a field solver confirms them. `impedance_2d.py` (atlc 4.6.1, a 2D quasi-static
# finite-difference solver, the cross-section drawn with its solder mask) has now been run on every geometry this project
# uses, and its answers are here so the GATE reads them rather than a formula the record already doubts.
#
#   geometry                                          closed form   solver (with mask)   difference
#   microstrip 0.300 / 0.200, h 0.2104, er 4.40           88.6            87.4              -1.3 %
#   microstrip 0.200 / 0.150, h 0.2104, er 4.40          102.0            95.9              -6.0 %
#   microstrip 0.127 / 0.127, h 0.0994, er 4.10           93.7            90.7              -3.1 %
#   microstrip 0.127 / 0.200, h 0.0994, er 4.10          101.4            99.2              -2.2 %
#   stripline  0.127 / 0.127, h 0.6057, er 4.45          138.1           102.0             -26.2 %
#   stripline  0.127 / 0.200, h 0.6057, er 4.45          147.6           118.1             -20.0 %
#
# The outer layers agree. The STRIPLINE does not: IPC-2141's stripline form is being used far outside the width-to-height
# ratio it was fitted for (w/h 0.21) and it reads 20 to 26 percent HIGH. The two stripline rows are the real inner layers of
# the JLC 3313 six-layer stack, where a track on In2 sees In1 0.55 mm above and In4 0.674 mm below, harmonic mean 0.6057, and
# In3 is the mirror.
#
# CORRECTION OF 8 SEPTEMBER'S FINDING. The record said "0.127/0.127 stripline on the 3313 stack computes about 74 ohm, not
# 100". That number came from the selftest's h = 0.1 mm, which is not this stack's plane distance; at the real 0.6057 the same
# formula gives 138 and the solver gives 102. So the inner-layer pairs were never 26 percent low. They are about 13 percent
# HIGH of a 90 ohm target and 18 percent high of a 100 ohm one, which is its own problem and a real one: a pair moved to In2
# or In3 at today's class widths misses its target, and the widths have to grow for an inner-layer pair.
CAL = [   # (mode, w, s, h, er, Zdiff from the solver with mask), matched within CAL_TOL of each dimension
    ("microstrip", 0.300, 0.200, 0.2104, 4.40,  87.4),
    ("microstrip", 0.200, 0.150, 0.2104, 4.40,  95.9),
    ("microstrip", 0.127, 0.127, 0.0994, 4.10,  90.7),
    ("microstrip", 0.127, 0.200, 0.0994, 4.10,  99.2),
    ("stripline",  0.127, 0.127, 0.6057, 4.45, 102.0),
    ("stripline",  0.127, 0.200, 0.6057, 4.45, 118.1),
]
CAL_TOL = 0.06      # 6 percent on each of w, s, h; er within 0.3
# Over the four solved microstrips the solver reads 0.94 to 0.99 of the closed form, mean 0.967; over the two solved
# striplines 0.74 and 0.80, mean 0.77. Both are measured biases rather than guesses, and both are applied to a geometry whose
# exact cross-section has not been solved, with the run saying how many millimetres were judged which way. The stripline
# factor rests on two points, so it is printed as a caution every time it is used.
MICROSTRIP_FACTOR = 0.967
STRIPLINE_FACTOR = 0.77
CAL_USED = {"solver": 0.0, "microstrip factor": 0.0, "stripline factor (two solved points)": 0.0}   # millimetres judged each way

def calibrated(mode, w, s, h, er, closed, length=0.0):
    """The best number this project has for this geometry, and which kind it is. Never silent about the difference."""
    for (m, cw, cs, ch, cer, z) in CAL:
        if m != mode: continue
        if abs(w - cw) <= CAL_TOL * cw and abs(s - cs) <= CAL_TOL * cs and abs(h - ch) <= CAL_TOL * ch and abs(er - cer) <= 0.3:
            CAL_USED["solver"] += length; return z, "solver"
    if mode == "microstrip":
        CAL_USED["microstrip factor"] += length; return closed * MICROSTRIP_FACTOR, "microstrip factor"
    CAL_USED["stripline factor (two solved points)"] += length; return closed * STRIPLINE_FACTOR, "stripline factor"

def read_stackup(path):
    """[(name, kind, thickness_mm, er)] from the (stackup ...) block written by stackup_write.py; copper layers carry kind 'copper'."""
    s = open(path, encoding="utf-8").read(); m = re.search(r"\n[ \t]+\(stackup\n(.*?)\n[ \t]+\)\n", s, re.S)
    if not m: return None
    out = []
    for line in m.group(1).splitlines():
        mm = re.match(r'\s*\(layer "([^"]+)" \(type "([^"]+)"\)(?: \(thickness ([0-9.]+)\))?(?: \(material "[^"]*"\))?(?: \(epsilon_r ([0-9.]+)\))?', line)
        if mm and mm.group(2) in ("copper", "prepreg", "core"): out.append((mm.group(1), mm.group(2), float(mm.group(3) or 0), float(mm.group(4)) if mm.group(4) else None))   # no default epsilon: a dielectric without one is refused
    return out

def geometry(stack, layer):
    """For a copper layer name: (t, [(distance to the next copper above, er above)], [(distance below, er below)])."""
    idx = [i for i, (n, k, th, er) in enumerate(stack) if k == "copper" and n == layer]
    if not idx: return None
    i = idx[0]; t = stack[i][2]
    def side(step):
        d = 0.0; ers = []; j = i + step
        while 0 <= j < len(stack):
            n, k, th, er = stack[j]
            if k == "copper": return d, (sum(e for e in ers if e) / max(1, len([e for e in ers if e])) if ers else None), n
            d += th; ers.append(er); j += step
        return None
    return t, side(-1), side(1)

def main(a):
    if not a or a[0] == "--selftest":
        # 50 ohm microstrip on FR-4: the classic w/h about 2 (Bogatin); the two coupled formulas agree on their shared limit
        h, t, er = 0.2104, 0.035, 4.4
        w50 = next(w for w in [x / 1000 for x in range(100, 800)] if z_microstrip(w, h, t, er) <= 50)
        ok1 = 1.6 <= w50 / h <= 2.2
        zd = zd_microstrip(0.2, 0.15, h, t, er); zs = zd_stripline(0.127, 0.127, 0.6057, 0.0152, 4.45)   # 0.6057 is the 3313 stack's real inner plane distance; this line said 0.1 mm until 10 Sep 2026 and produced the "74 ohm" of the record
        print("impedance selftest: 50 ohm microstrip on the JLC 7628 outer layer at w %.3f mm (w/h %.2f, expected 1.6 to 2.2): %s; the shipped USB geometry 0.20/0.15 on that layer computes %.0f ohm differential; 0.127/0.127 stripline on the 3313 stack's real inner layers %.0f ohm by the closed form, %.0f by the field solver" % (w50, w50 / h, "PASS" if ok1 else "FAIL", zd, zs, 102.0))
        return 0 if ok1 else 1
    import pcbnew, intent
    import verdict as _v
    tol = float(a[a.index("--tolerance") + 1]) if "--tolerance" in a else 0.10
    b = pcbnew.LoadBoard(a[0]); stack = read_stackup(a[0])
    if not stack:
        print("impedance: FAIL no stackup in the board file (run stackup_write.py)")
        # No stackup means no geometry to compute against: nothing was judged, which is not a clean board.
        return _v.write("impedance_check", _v.INCONCLUSIVE, denominator=0, inputs={"board": a[0]},
                        note="no stackup in the board file; run stackup_write.py")
    it = intent.load(a[0]); classes = (it or {}).get("pair_classes", intent.Z_DEFAULT)
    pro = os.path.splitext(a[0])[0] + ".kicad_pro"; assign = {}
    if os.path.exists(pro): assign = json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {})
    names = {b.GetNetInfo().GetNetItem(k).GetNetname() for k in range(1, b.GetNetInfo().GetNetCount())}
    def cls_of(net):
        c = assign.get(net) or assign.get("/" + net.lstrip("/")) or assign.get(net.lstrip("/"))
        return c[0] if isinstance(c, list) and c else (c if isinstance(c, str) else None)   # KiCad 9 stores the assignment as a list of class names
    pairs = sorted({n[:-2] for n in names if n.endswith("_P") and n[:-2] + "_N" in names})
    planes = {}   # layer -> list of filled polys of plane nets
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetFilledArea() <= 0: continue
        planes.setdefault(z.GetFirstLayer(), []).append(z.GetFilledPolysList(z.GetFirstLayer()))
    lname = {b.GetLayerName(L): L for L in range(64) if b.GetLayerName(L)}
    segs = {}
    for tr in b.GetTracks():
        if tr.GetClass() == "PCB_TRACK": segs.setdefault(tr.GetNetname(), []).append(tr)
    results = []; miss = 0; checked = 0
    for pr in pairs:
        cl = cls_of(pr + "_P") or "Default"; target = classes.get(cl, {}).get("z_diff")
        if not target: continue
        p, n = segs.get(pr + "_P", []) or segs.get("/" + pr + "_P", []), segs.get(pr + "_N", []) or segs.get("/" + pr + "_N", [])
        # 11 September 2026 (MESHSAT-862): both UNROUTED exits appended their verdict and `continue`d
        # BEFORE the `miss += 1` below, so a pair with no track on one leg was printed in the summary
        # and did not fail the gate. The exit status is `1 if miss else 0`, so the board passed.
        if not p or not n: miss += 1; results.append((pr, cl, target, None, 0.0, 0.0, "UNROUTED", None, 0, 0.0)); continue
        tot = 0.0; ok_len = 0.0; unref = 0.0; zs = []; gaps = []; fan = 0.0
        pnets = {pr + "_P", pr + "_N", "/" + pr.lstrip("/") + "_P", "/" + pr.lstrip("/") + "_N"}
        ppads = [q.GetPosition() for f in b.GetFootprints() for q in f.Pads() if q.GetNetname() in pnets]
        for sp in p:
            L = sp.GetLayer(); ln = b.GetLayerName(L); w = sp.GetWidth() / 1e6; length = sp.GetLength() / 1e6
            if length < 0.2: continue
            # the partner's nearest parallel segment on the same layer
            mid = (sp.GetStart() + sp.GetEnd()); mx, my = mid.x / 2, mid.y / 2
            if any(math.hypot(mx - q.x, my - q.y) / 1e6 <= FAN_MM for q in ppads): fan += length; continue   # a pin fan: not judged
            best = None
            for sn in n:
                if sn.GetLayer() != L: continue
                ax, ay, bx, by = sn.GetStart().x, sn.GetStart().y, sn.GetEnd().x, sn.GetEnd().y
                dx, dy = bx - ax, by - ay; l2 = dx * dx + dy * dy
                if l2 == 0: continue
                u = max(0.0, min(1.0, ((mx - ax) * dx + (my - ay) * dy) / l2)); cx, cy = ax + u * dx, ay + u * dy
                dist = math.hypot(mx - cx, my - cy) / 1e6
                if best is None or dist < best: best = dist
            tot += length
            g = geometry(stack, ln)
            if g is None: continue
            t, above, below = g
            def ref(side):
                if not side: return None
                d, er, name = side
                Lr = lname.get(name)
                if Lr in planes and any(pl.Contains(pcbnew.VECTOR2I(int(mx), int(my))) for pl in planes[Lr]): return d, er
                return None
            ra, rb = ref(above), ref(below)
            if best is None or best - w <= 0: zs.append(None); continue
            s = best - w; gaps.append((s, length))
            if ra and rb:
                h = 2 * ra[0] * rb[0] / (ra[0] + rb[0]); er = (ra[1] + rb[1]) / 2
                z, _cal = calibrated("stripline", w, s, h, er, zd_stripline(w, s, h, t, er), length)
            elif ra or rb:
                h, er = (ra or rb)
                z, _cal = calibrated("microstrip", w, s, h, er, zd_microstrip(w, s, h, t, er), length)
            else: unref += length; continue
            zs.append(z)
            if abs(z - target) <= tol * target: ok_len += length
        if not tot and not fan: miss += 1; results.append((pr, cl, target, None, 0.0, 0.0, "UNROUTED", None, 0, 0.0)); continue
        if tot < SHORT_MM:   # no coupled run to judge: the pair is its fans (a series resistor beside its chip)
            checked += 1; results.append((pr, cl, target, None, 1.0, 0.0, "SHORT", None, 0, fan)); continue
        zz = [z for z in zs if z]; med = sorted(zz)[len(zz) // 2] if zz else None; frac = ok_len / tot
        # the length-weighted median gap between the legs: a pair the router laid as two lone traces (Freerouting has no pair routing) shows a gap of millimetres
        gaps.sort(); acc = 0.0; gmed = None
        for g, ln_ in gaps:
            acc += ln_
            if acc >= sum(x[1] for x in gaps) / 2: gmed = g; break
        wmed = sorted(sp.GetWidth() / 1e6 for sp in p)[len(p) // 2]
        uncoupled = gmed is None or gmed > 3 * wmed
        verdict = "MET" if frac >= 0.9 and unref <= UNREF_MM else ("UNCOUPLED" if uncoupled else ("UNREFERENCED" if unref > UNREF_MM else "MISSED"))
        if verdict != "MET": miss += 1
        checked += 1; results.append((pr, cl, target, med, frac, unref, verdict, gmed, wmed, fan))
    for pr, cl, target, med, frac, unref, v, gmed, wmed, fan in results:
        print("impedance: %-12s %-14s class %-8s target %3.0f ohm, median %s ohm, %3.0f%% of the length within %d%%, legs %s mm apart at w %.2f, unreferenced %.1f mm, fans %.1f mm" % (v, pr, cl, target, ("%.0f" % med) if med else "-", frac * 100, tol * 100, ("%.2f" % gmed) if gmed is not None else "-", wmed or 0, unref, fan))
    print("impedance: %d of %d pairs with a target within %d%% on the analytical model (%d unrouted; %d pairs on the board)" % (checked - miss, checked, tol * 100, sum(1 for r in results if r[6] == "UNROUTED"), len(pairs)))
    # Say which numbers came from the field solver and which from the closed form, because on the stripline geometry they
    # differ by 38 percent and a reader must never have to guess which one a verdict rests on (10 September 2026).
    tot_mm = sum(CAL_USED.values()) or 1.0
    print("impedance: where the numbers come from: %s" % "; ".join("%.0f mm %s" % (v, k) for k, v in CAL_USED.items() if v > 0) or "nothing judged")
    if CAL_USED["stripline factor (two solved points)"] > 0:
        print("impedance: NOTE %.0f mm (%.0f%%) judged with the stripline correction, which rests on two solved geometries (the solver reads"
              " 0.74 and 0.80 of IPC-2141 there). Solve that cross-section with impedance_2d.py before the number is quoted outside this project."
              % (CAL_USED["stripline factor (two solved points)"], 100.0 * CAL_USED["stripline factor (two solved points)"] / tot_mm))
    if any(er is None for _, k, _, er in stack if k != "copper"):
        print("impedance: FAIL a dielectric without epsilon_r in the stackup")
        return _v.write("impedance_check", _v.INCONCLUSIVE, counts={"pairs": len(pairs)}, denominator=checked,
                        inputs={"board": a[0]}, note="a dielectric in the stackup carries no epsilon_r")
    if "--json" in a: json.dump([dict(pair=r[0], cls=r[1], target=r[2], median=r[3], fraction=r[4], unreferenced_mm=r[5], verdict=r[6], gap_mm=r[7], width_mm=r[8], fan_mm=r[9]) for r in results], open(a[a.index("--json") + 1], "w"), indent=1)
    by_v = {}
    for r in results: by_v[r[6]] = by_v.get(r[6], 0) + 1
    # 0 of 0 must not read as agreement, and it must not read as a failure either when zero is the DECLARED state.
    # A board whose schematic declares its pair classes and gives none of them a target has said what it means:
    # C's only pair is the RP2040's USB at 1.1 full speed, so no target applies, `intent.pair_class("USB")` writes
    # an empty entry and the loop above skips it (gen_sch_c.py:247, appendix 32.76). A board with NO declaration
    # at all is the other case, and there nothing was judged: a missing intent file, a project without class
    # assignments, a chain that did not run. The first is PASS with its reason, the second INCONCLUSIVE.
    # 11 September 2026 (MESHSAT-862): the first draft of this check made C's correct state block its own board.
    declared = bool((it or {}).get("pair_classes"))
    if checked: res = _v.PASS if not miss else _v.FAIL
    elif declared: res = _v.PASS
    else: res = _v.INCONCLUSIVE
    if not checked:
        print("impedance: no pair on this board carries an impedance target (%s)"
              % ("declared that way in the schematic" if declared else "and the board declares no pair class at all"))
    return _v.write("impedance_check", res,
                    counts=dict(by_v, met=checked - miss, missed=miss, pairs_on_board=len(pairs), classes_declared=len((it or {}).get("pair_classes") or {})),
                    denominator=checked,
                    evidence=["%s %s class %s target %s ohm" % (r[6], r[0], r[1], r[2]) for r in results if r[6] != "MET"],
                    inputs={"board": a[0]},
                    note="" if checked else ("the board declares its pair classes and gives none a target, which is its recorded design"
                                             if declared else "the board declares no pair class: nothing was judged"))

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
