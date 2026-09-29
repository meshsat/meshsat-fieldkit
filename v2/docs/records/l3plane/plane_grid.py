#!/usr/bin/env python3
"""plane_grid.py: M1's deployment condition, the planes the array may face, for the two lid options that fit (stream
l3plane, MESHSAT-1357, 30 September 2026). Evidence for the owner's decision of M1's deployment condition; it changes no
requirement and no record.

PROTOTYPE DESIGN, AI arithmetic: nothing is built, ordered or measured. Every figure printed is MODELED on the reference
day of SC-37 (the September mean day at Leiden, PVGIS), and every condition printed is INFERRED from the model's grid.

What it runs. The lid options of records/a1int/reconcile_lid_panel.py (4S14P, the tablet out, 4S20P in all; 4S15P, the
QMX out, 4S21P in all) through that script's own run(), which is a1elec's energy_two_pack.py (pinned) with the lid's
parallel count, the ratio and U3's input limit set, U3B at code 62 (7.936 A) and its carried 0.972, the lid at the
September basis. The only change to reconcile_lid_panel.py is run()'s optional prof, the hourly irradiance of the day;
its own output is unchanged to the byte. Each plane of records/a1solar/energy_runs.py's grid (slopes 0 to 70 degrees in
10 degree steps, azimuths 45 degrees east to 45 degrees west in 15 degree steps, 50 planes with flat counted once: 49
files under v2/vendor/solar/pvgis-planes/ and the 40/0 anchor) is run on its own PVGIS DRcalc September mean day, scaled
by the model's factor found on the 40/0 anchor, with that plane's own fixed-point ratios B (typical) and C (adverse), all
from energy_runs.py imported unchanged (pinned).

The cases, each at the lid basis:
  * P, the primary: U3's input limit at its minimum 6.1 A, U3B at its carried figure (reconcile_lid_panel.py's model);
  * I: U3 at the 6.0 A bracket;
  * H: U3 at 6.1 A, U3B hour by hour on its TI curve (records/s119/reconcile_s119.py's run() and curve(), imported
    unchanged, pinned), the model's most faithful reading of U3B by that record;
  * V20 and V19, a sensitivity this stream adds: U3 at 6.1 A with the charge bus at the front end's nominal regulation
    and at the low end of its DC band, both PARSED from records/s120/vbus20_bound.out section 2. The model holds the bus
    at energy_two_pack.py's V_BUS20 (20.7 V) when it turns U3's current limit into power; a current limit at a lower bus
    voltage is less power. The model is not edited: the case passes the current that gives the same power at 20.7 V.

The conditions (section 3): the maximal slope-by-azimuth rectangles of the grid whose every point meets M1 in both B and C,
per case, and a CONSERVATIVE set: every point meets both in P, I and H at once, with every lowest store above a floor, the
model's own hourly-step sensitivity PARSED from reconcile_lid_panel.out's NOTES (the larger figure it prints; measured by
its check at 40/0 and the second issue's settings, so a floor, not a bound). The same with V20 added shows what the
conservative condition becomes if the bus sits at its nominal regulation.

Before printing results it proves that it runs the committed model (exit 4 otherwise):
  0a. reconcile_lid_panel.out's rows for both lid options, B and C, U3 at 6.1 and 6.0 A, reproduced byte for byte
      through the plane machinery on the 40/0 anchor with the ratios as that output reads them;
  0b. energy_runs.out section 6 (the 4S12P lid on all 50 planes) reproduced byte for byte;
  0c. reconcile_s119.out section 7 (the two lid options on the old rule's planes, U3B hour by hour) reproduced byte for
      byte.

Run from the repository root:  python3 v2/docs/records/l3plane/plane_grid.py > v2/docs/records/l3plane/plane_grid.out
Deterministic: no date, host or absolute path in the output. Exit 2: a pinned script is not the pinned file; exit 3: an
input differs from HEAD or cannot be parsed; exit 4: a reproduction check failed."""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
RECS = os.path.join(TOP, "v2", "docs", "records")
PINS = {"a1int/reconcile_lid_panel.py": "031ab3f99779f657be720b36c9ea71c9933175b14bc6883e927df2937b31fd8a",
        "a1solar/energy_runs.py": "d0fd1949efce71868a143c57cd9e5a2db516daec774db1085541d1a5a920ffcb",
        "a1elec/energy_two_pack.py": "a3426880bf607d38b08449ec0a880f10a064ee2767324afad2c250cd5a9444f4",
        "s119/reconcile_s119.py": "69c7ee96a87d3bcb74929570329d4001abdcea36ca6a91058c57360c6e2dff14"}
for _rel, _want in PINS.items():
    if hashlib.sha256(open(os.path.join(RECS, _rel), "rb").read()).hexdigest() != _want:
        sys.stderr.write("plane_grid: %s is not the pinned file; refusing\n" % _rel)
        sys.exit(2)
for _d in ("a1elec", "a1solar", "s119", "a1int"):
    sys.path.insert(0, os.path.join(RECS, _d))
import energy_two_pack as TP  # noqa: E402
import energy_runs as ER  # noqa: E402
import reconcile_s119 as RS  # noqa: E402
import reconcile_lid_panel as RL  # noqa: E402

RUNS = "v2/docs/records/a1solar/energy_runs.out"
PANEL = "v2/docs/records/a1int/reconcile_lid_panel.out"
S119 = "v2/docs/records/s119/reconcile_s119.out"
S120 = "v2/docs/records/s120/vbus20_bound.out"
LIDS = ((14, "4S14P lid, the tablet out of the lid (4S20P in all)"),
        (15, "4S15P lid, the QMX out of the lid (4S21P in all)"))
U3_MIN, U3_BRACKET = 6.1, 6.0
RULE = ((20, 50), (-15, 15))   # the rule of ARRAY.md section 7, computed for the 4S12P lid


def head_equal(rel):
    text = open(os.path.join(TOP, rel), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + rel], capture_output=True, text=True).stdout
    if text != head:
        sys.stderr.write("plane_grid: %s differs from HEAD's; refusing\n" % rel)
        sys.exit(3)
    return text


def bus_band():
    """(nominal, DC band low end, DC band high end) of VBUS20, parsed from vbus20_bound.out section 2."""
    sec = head_equal(S120).split("2. THE FRONT END'S REGULATION", 1)[1].split("\n3. ", 1)[0]
    m1 = re.search(r"^\s+nominal\s+(\d+\.\d{3}) V\s*$", sec, re.M)
    m2 = re.search(r"(\d+\.\d{3}) to (\d+\.\d{3}) V\s+<- the DC band", sec)
    if not (m1 and m2):
        sys.stderr.write("plane_grid: %s section 2 not parsed\n" % S120)
        sys.exit(3)
    return float(m1.group(1)), float(m2.group(1)), float(m2.group(2))


def step_floor(panel):
    """The larger lowest-store drop the NOTES of reconcile_lid_panel.out print for a 0.01 h step (Wh)."""
    text = " ".join(panel.split())
    m = re.search(r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", text)
    if not m:
        sys.stderr.write("plane_grid: the hourly-step figures not found in %s's NOTES\n" % PANEL)
        sys.exit(3)
    return max(float(m.group(2)), float(m.group(4)))


def summary(rs):
    return (TP.verdict(rs), min(r["low_t"] for r in rs), min(r["low_l"] for r in rs))


def main():
    n0 = TP.NP_L
    d0, _pack, res40, t2m = TP.load_model()
    tmin = round(min(t2m), 2)
    RS.TMIN = tmin
    rat = RL.ratios()                      # energy_runs.out section 2, asserted equal to HEAD's
    panel = head_equal(PANEL)
    runs_out = head_equal(RUNS)
    s119_out = head_equal(S119)
    v_nom, v_low, v_high = bus_band()
    floor = step_floor(panel)
    AC, _EA, _TP = ER.pinned_import()
    AC.check_pins()
    pr0 = res40["pr"]
    if abs(pr0 - rat["A"][1]) > 5e-5:
        sys.stderr.write("plane_grid: the model's ratio %.5f is not energy_runs.out's A %.4f\n" % (pr0, rat["A"][1]))
        return 3
    prof0 = res40["months"][TP.MONTH]["profile"]
    ga, ta, _pl = ER.september(ER.ANCHOR)
    k_scale = sum(prof0) / sum(ga)
    if max(abs(k_scale * ga[h] - prof0[h]) for h in range(24)) > 1e-9:
        sys.stderr.write("plane_grid: the anchor scaled does not reproduce the model's profile\n")
        return 4
    v_mod = TP.V_BUS20
    cases = (("P", "U3 %.1f A (minimum), U3B carried %.3f" % (U3_MIN, TP.v("eta_u3b"))),
             ("I", "U3 %.1f A (bracket), U3B carried" % U3_BRACKET),
             ("H", "U3 %.1f A, U3B hour by hour (TI curve)" % U3_MIN),
             ("V20", "U3 %.1f A at the bus's nominal %.2f V (%.1f W)" % (U3_MIN, v_nom, U3_MIN * v_nom)),
             ("V19", "U3 %.1f A at the DC band's low end %.2f V (%.1f W)" % (U3_MIN, v_low, U3_MIN * v_low)))

    def run_case(key, n, pr, pp):
        if key == "P":
            return summary(RL.run(n, tmin, pr, U3_MIN, prof=pp)[0])
        if key == "I":
            return summary(RL.run(n, tmin, pr, U3_BRACKET, prof=pp)[0])
        if key == "H":
            return summary(RS.run(n, pr, U3_MIN, prof=pp, eta_b=RS.curve(n, "TI")))
        if key == "V20":
            return summary(RL.run(n, tmin, pr, U3_MIN * v_nom / v_mod, prof=pp)[0])
        return summary(RL.run(n, tmin, pr, U3_MIN * v_low / v_mod, prof=pp)[0])

    o = []
    P = o.append
    P("M1'S DEPLOYMENT CONDITION ON THE FULL PLANE GRID FOR THE TWO LID OPTIONS (plane_grid.py, stream l3plane, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, ordered or measured. Every figure is MODELED on the reference day of SC-37 (September")
    P("mean day at Leiden, PVGIS DRcalc 2005 to 2020, each plane its own day); every condition is INFERRED from the grid. AI")
    P("arithmetic, not a qualified review. Model: reconcile_lid_panel.py's run() over a1elec's energy_two_pack.py (pinned),")
    P("400 Wp (2S2P Renogy RNG-100DB-H), 200 W stage, entry E2's front end, base +%.0f C, lid at %.2f C (the September mean" % (TP.v("t_base_c"), tmin))
    P("day's minimum air), both start hours, 42.8 W, aged 80 percent; U3 %.3f, U3B at code 62 (%.3f A) and %.3f carried." % (
        TP.chain(d0)[2], TP.v("chg_a_lid"), TP.v("eta_u3b")))
    P("Ratios per plane from energy_runs.py (imported, pinned): B typical, C adverse; PVGIS's 0.9417 (40/0) kept for every plane.")
    P("")

    # 0. reproduction
    P("0. REPRODUCTION OF THE COMMITTED OUTPUTS")
    bad = 0
    pp0 = [k_scale * g for g in ga]
    n_ok = 0
    for n, _w in LIDS:
        for k in "BC":
            for uk, ua in (("minimum", U3_MIN), ("bracket", U3_BRACKET)):
                rs = RL.run(n, tmin, rat[k][1], ua, prof=pp0)[0]
                line = "   %s, U3 %-7s %.1f A, at %.2f C: %s" % (k, uk, ua, tmin, TP.fmt_run(rs))
                if (line + "\n") in panel:
                    n_ok += 1
                else:
                    bad += 1
    P("   0a. %s: %d of 8 rows (4S14P and 4S15P; B, C; U3 6.1 and 6.0 A) reproduced byte for byte through the plane" % (PANEL, n_ok))
    P("       machinery on the 40/0 anchor (energy_runs.py's file scaled by %.6f) with that output's own ratios" % k_scale)
    sec6 = runs_out.split("\n6. THE PLANES", 1)[1].split("THE PLANES THAT MEET IN BOTH CASES", 1)[0]
    d2, pack2, res4b, _t = TP.load_model()
    TP.NP_L, TP.NP_T = 12, TP.NP_B + 12
    n_ok = n_all = 0
    for sl in ER.SLOPES:
        for az in ER.ASPECTS:
            if sl == 0 and az != 0:
                continue
            G, TA, pl = ER.september(ER.plane_file(sl, az))
            Rp = ER.Ratios(AC, G, TA)
            rb = Rp.typical()
            rc, _f = Rp.adverse()
            pp = [k_scale * g for g in G]
            cells = []
            for pr in (pr0 * rb, pr0 * rc):
                r = dict(res4b)
                r["pr"] = pr
                rs = TP.both(d2, pack2, r, pp, 400, 200.0, TP.v("t_base_c"), tmin, TP.base_cfg())
                cells.append("%s %6.1f / %5.1f" % ("MEETS  " if TP.verdict(rs) else "NOT MET", min(x["low_t"] for x in rs),
                                                    min(x["low_l"] for x in rs)))
            line = "   %5d %+6d %10.3f %7.4f %7.4f %-26s %-26s" % (sl, az, k_scale * sum(G) / 1000.0, rb, rc, cells[0], cells[1])
            n_all += 1
            if (line + "\n") in sec6:
                n_ok += 1
            else:
                bad += 1
    TP.NP_L, TP.NP_T = n0, TP.NP_B + n0
    P("   0b. %s section 6: %d of %d plane rows (the 4S12P lid, entry E2) reproduced byte for byte" % (RUNS, n_ok, n_all))
    sec7 = s119_out.split("\n7. THE DEPLOYMENT RULE'S PLANES", 1)[1].split("\n8. ", 1)[0]
    n_ok = n_all = 0
    for sl, az in [(0, 0)] + [(s, a) for s in (20, 30, 40, 50) for a in (-15, 0, 15)]:
        G, TA, pl = ER.september(ER.plane_file(sl, az))
        Rp = ER.Ratios(AC, G, TA)
        rb = Rp.typical()
        rc, _f = Rp.adverse()
        pp = [k_scale * g for g in G]
        cells = []
        for n in (14, 15):
            for pr in (rat["A"][1] * rb, rat["A"][1] * rc):
                rs = RS.run(n, pr, 6.1, prof=pp, eta_b=RS.curve(n, "TI"))
                ok = TP.verdict(rs)
                same = TP.verdict(RS.run(n, pr, 6.1, prof=pp)) == ok
                cells.append((("MEETS %6.1f / %5.1f" % (min(x["low_t"] for x in rs), min(x["low_l"] for x in rs))) if ok else "NOT MET") + ("" if same else " *"))
        line = "   %5d %+5d %8.4f %8.4f   %-22s %-22s %-22s %-22s" % (sl, az, rb, rc, *cells)
        n_all += 1
        if (line + "\n") in sec7:
            n_ok += 1
        else:
            bad += 1
    P("   0c. %s section 7: %d of %d plane rows (both lid options, U3B hour by hour) reproduced byte for byte" % (S119, n_ok, n_all))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        sys.stderr.write("plane_grid: %d reproduction row(s) failed; refusing to print results\n" % bad)
        return 4
    P("   The grid below therefore runs the committed model; only the plane's day and its two ratios change from row to row.")
    P("")
    P("   The cases (each both starts, lid at %.2f C; 'both' = the lowest store of the two packs together, Wh):" % tmin)
    for key, what in cases:
        P("     %-4s %s" % (key, what))
    P("   V20 and V19 are a SENSITIVITY this stream adds (INFERRED): the model turns U3's current limit into power at its")
    P("   V_BUS20 of %.1f V; %s section 2 prints the bus's nominal regulation %.3f V and DC band %.3f to %.3f V." % (v_mod, S120, v_nom, v_low, v_high))
    P("   The case passes %.4f A and %.4f A at %.1f V, the same power. The model and its committed outputs are not changed." % (
        U3_MIN * v_nom / v_mod, U3_MIN * v_low / v_mod, v_mod))
    P("")

    # 1. the grid
    planes = [(sl, az) for sl in ER.SLOPES for az in ER.ASPECTS if not (sl == 0 and az != 0)]
    res = {}
    meta = {}
    for sl, az in planes:
        G, TA, pl = ER.september(ER.plane_file(sl, az))
        if (int(pl[0]), int(pl[1])) != (sl, az):
            sys.stderr.write("plane_grid: %s is not the plane %d/%d\n" % (ER.plane_file(sl, az), sl, az))
            return 3
        Rp = ER.Ratios(AC, G, TA)
        rb = Rp.typical()
        rc, _f = Rp.adverse()
        pp = [k_scale * g for g in G]
        meta[(sl, az)] = (k_scale * sum(G) / 1000.0, rb, rc)
        for n, _w in LIDS:
            for key, _what in cases:
                res[(n, key, sl, az)] = (run_case(key, n, pr0 * rb, pp), run_case(key, n, pr0 * rc, pp))
    TP.NP_L, TP.NP_T = n0, TP.NP_B + n0

    def cell(v):
        return ("%6.1f / %5.1f" % (v[1], v[2])) if v[0] else "NOT MET"

    def short(v):
        return ("%6.1f" % v[1]) if v[0] else "   NOT"

    def sym(n, key, sl, az):
        b, c = res[(n, key, sl, az)]
        return "BC" if (b[0] and c[0]) else ("B" if b[0] else ("C" if c[0] else "-"))

    for idx, (n, what) in enumerate(LIDS):
        P("%d. %s: THE GRID (azimuth in degrees, negative east of south; flat is run once)" % (1 + idx, what.upper()))
        P("   %d.1 Case P, both / lid Wh or NOT MET" % (1 + idx))
        P("   %5s %5s %9s %7s %7s   %-16s %-16s" % ("slope", "azim", "kWh/m2/d", "B ratio", "C ratio", "B typical", "C adverse"))
        for sl, az in planes:
            kwh, rb, rc = meta[(sl, az)]
            b, c = res[(n, "P", sl, az)]
            P("   %5d %+5d %9.3f %7.4f %7.4f   %-16s %-16s" % (sl, az, kwh, rb, rc, cell(b), cell(c)))
        P("   %d.2 Every case, the lowest store of both packs in Wh (NOT = NOT MET); B typical / C adverse" % (1 + idx))
        P("   %5s %5s  %s" % ("slope", "azim", "  ".join("%-13s" % k for k, _w in cases)))
        for sl, az in planes:
            P("   %5d %+5d  %s" % (sl, az, "  ".join("%s %s" % (short(res[(n, k, sl, az)][0]), short(res[(n, k, sl, az)][1])) for k, _w in cases)))
        P("   %d.3 Verdict maps: BC meets in both B and C, B in the typical case only, - in neither" % (1 + idx))
        for key, cwhat in cases:
            P("   case %s (%s)" % (key, cwhat))
            P("      %8s %s" % ("slope", "".join("%6s" % ("%+d" % a) for a in ER.ASPECTS)))
            for sl in ER.SLOPES:
                if sl == 0:
                    P("      %8d %s" % (sl, "".join("%6s" % (sym(n, key, 0, 0) if a == 0 else ".") for a in ER.ASPECTS)))
                else:
                    P("      %8d %s" % (sl, "".join("%6s" % sym(n, key, sl, a) for a in ER.ASPECTS)))
        P("")

    # the conditions
    base = 1 + len(LIDS)
    P("%d. THE CONDITIONS THE GRIDS ALLOW (INFERRED; only grid points that meet in BOTH B and C; flat counts for every azimuth)" % base)
    P("   A rectangle is a slope range by an azimuth range whose every grid point meets both; 'maximal' = inside no larger one;")
    P("   'least' = its smallest lowest store of both packs over its points, cases B and C and the cases named, with the plane.")
    P("   'Within x of south' = the azimuth range -x to +x. The model's grid is its resolution: nothing between grid points is run.")
    P("   The floor: %.1f Wh, the larger lowest-store drop reconcile_lid_panel.out's NOTES print for a 0.01 h step (its check," % floor)
    P("   at 40/0 and the second issue's settings); a point whose least store is at or under it is not counted in a floored set.")
    sets = [("case P (the grid's condition)", ("P",), None), ("case I", ("I",), None), ("case H", ("H",), None),
            ("case V20", ("V20",), None), ("case V19", ("V19",), None),
            ("CONSERVATIVE: P, I and H at once, above the floor", ("P", "I", "H"), floor),
            ("CONSERVATIVE with the bus at its nominal: P, I, H and V20 at once, above the floor", ("P", "I", "H", "V20"), floor)]

    def point_ok(n, keys, fl, sl, az):
        if sl == 0:
            az = 0          # a flat plane has no azimuth: its one run stands for every column
        for key in keys:
            for v in res[(n, key, sl, az)]:
                if not v[0] or (fl is not None and v[1] <= fl):
                    return False
        return True

    def least(n, keys, pts):
        best = None
        for sl, az in pts:
            a0 = 0 if sl == 0 else az
            for key in keys:
                for ci, cn in ((0, "B"), (1, "C")):
                    v = res[(n, key, sl, a0)][ci]
                    if best is None or v[1] < best[0]:
                        best = (v[1], sl, az, key, cn)
        return best

    for n, what in LIDS:
        P("   %s" % what)
        for label, keys, fl in sets:
            rects = []
            for i in range(len(ER.SLOPES)):
                for j in range(i, len(ER.SLOPES)):
                    for a in range(len(ER.ASPECTS)):
                        for b in range(a, len(ER.ASPECTS)):
                            if all(point_ok(n, keys, fl, ER.SLOPES[s_], ER.ASPECTS[t]) for s_ in range(i, j + 1) for t in range(a, b + 1)):
                                rects.append((i, j, a, b))
            maxi = [r for r in rects if not any(q != r and q[0] <= r[0] and q[1] >= r[1] and q[2] <= r[2] and q[3] >= r[3] for q in rects)]
            maxi.sort(key=lambda r: (-(r[1] - r[0] + 1) * (r[3] - r[2] + 1), r))
            P("      %s:" % label)
            for r in maxi[:6]:
                pts = [(ER.SLOPES[s_], ER.ASPECTS[t]) for s_ in range(r[0], r[1] + 1) for t in range(r[2], r[3] + 1)]
                lw = least(n, keys, pts)
                P("         slope %2d to %2d, azimuth %+3d to %+3d: %2d grid points; least %5.1f Wh at %d/%+d (%s %s)" % (
                    ER.SLOPES[r[0]], ER.SLOPES[r[1]], ER.ASPECTS[r[2]], ER.ASPECTS[r[3]], len(pts), lw[0], lw[1], lw[2], lw[3], lw[4]))
            if len(maxi) > 6:
                P("         (%d further maximal rectangles, smaller)" % (len(maxi) - 6))
            if not maxi:
                P("         no grid point")
            for x in (0, 15, 30, 45):
                a, b = ER.ASPECTS.index(-x), ER.ASPECTS.index(x)
                runs, cur = [], None
                for s_ in range(len(ER.SLOPES)):
                    ok = all(point_ok(n, keys, fl, ER.SLOPES[s_], ER.ASPECTS[t]) for t in range(a, b + 1))
                    if ok and cur is None:
                        cur = s_
                    if not ok and cur is not None:
                        runs.append((cur, s_ - 1))
                        cur = None
                if cur is not None:
                    runs.append((cur, len(ER.SLOPES) - 1))
                txt = []
                for p_, q_ in runs:
                    pts = [(ER.SLOPES[s_], ER.ASPECTS[t]) for s_ in range(p_, q_ + 1) for t in range(a, b + 1)]
                    lw = least(n, keys, pts)
                    txt.append("slope %d to %d (least %.1f Wh at %d/%+d, %s %s)" % (ER.SLOPES[p_], ER.SLOPES[q_], lw[0], lw[1], lw[2], lw[3], lw[4]))
                P("         within %2d of south: %s" % (x, "; ".join(txt) or "no slope"))
    P("")

    # the lowest stores at the old rule's edges and the flat plane
    P("%d. THE LOWEST STORES AT THE OLD RULE'S EDGES (ARRAY.md section 7: 20 to 50 degrees within 15 degrees of south, computed" % (base + 1))
    P("   for the 4S12P lid), and on the planes one grid step outside it; case P unless named; both / lid Wh or NOT MET")
    (s_lo, s_hi), (a_lo, a_hi) = RULE
    inside = [(s, a) for s in ER.SLOPES if s_lo <= s <= s_hi for a in ER.ASPECTS if a_lo <= a <= a_hi]
    ring = sorted({(s, a) for s in ER.SLOPES for a in ER.ASPECTS
                   if s_lo - 10 <= s <= s_hi + 10 and a_lo - 15 <= a <= a_hi + 15 and (s, a) not in inside and s != 0})
    for n, what in LIDS:
        P("   %s" % what)
        for key in ("P", "I", "H", "V20", "V19"):
            for ci, cname in ((0, "B"), (1, "C")):
                vals = [(res[(n, key, s, a)][ci], s, a) for s, a in inside]
                if all(v[0][0] for v in vals):
                    low = min(vals, key=lambda v: v[0][1])
                    P("      case %-3s %s: every rule plane MEETS; lowest store %5.1f Wh at %d/%+d (lid %5.1f Wh)" % (
                        key, cname, low[0][1], low[1], low[2], low[0][2]))
                else:
                    miss = ", ".join("%d/%+d" % (s, a) for v, s, a in vals if not v[0])
                    P("      case %-3s %s: NOT every rule plane meets: NOT MET at %s" % (key, cname, miss))
        P("      the rule's edge planes, case P: %s" % "; ".join(
            "%d/%+d B %s C %s" % (s, a, short(res[(n, "P", s, a)][0]).strip(), short(res[(n, "P", s, a)][1]).strip())
            for s, a in inside if s in (s_lo, s_hi) or a in (a_lo, a_hi)))
        P("      one step outside, case P: %s" % "; ".join(
            "%d/%+d B %s C %s" % (s, a, short(res[(n, "P", s, a)][0]).strip(), short(res[(n, "P", s, a)][1]).strip()) for s, a in ring))
        b, c = res[(n, "P", 0, 0)]
        P("      laid flat (slope 0): %s" % "; ".join("case %s: B %s, C %s" % (
            k, cell(res[(n, k, 0, 0)][0]).strip(), cell(res[(n, k, 0, 0)][1]).strip()) for k, _w in cases))
    P("")
    P("%d. WHAT THE MODEL'S INPUTS TIE THE RESULT TO (read from the files)" % (base + 2))
    import json
    sites = {}
    for sl, az in planes:
        dj = json.load(open(os.path.join(TOP, ER.plane_file(sl, az)), encoding="utf-8"))
        loc, met = dj["inputs"]["location"], dj["inputs"]["meteo_data"]
        key = (loc["latitude"], loc["longitude"], met["radiation_db"], met["year_min"], met["year_max"])
        sites.setdefault(key, []).append("%d/%+d" % (sl, az))
    for key, pls in sorted(sites.items()):
        P("   plane days (DRcalc): latitude %.3f, longitude %.3f, %s %d to %d: %d of %d planes" % (key + (len(pls), len(planes))))
    mpath = d0["pinned"][0]["path"]
    mj = json.load(open(os.path.join(TOP, mpath), encoding="utf-8"))
    ml, mm = mj["inputs"]["location"], mj["inputs"]["meteo_data"]
    P("   the monthly mean that scales the day (%s): latitude %.3f, longitude %.3f, %s %d to %d;" % (
        mpath, ml["latitude"], ml["longitude"], mm["radiation_db"], mm["year_min"], mm["year_max"]))
    P("     September %.3f kWh/m2 a day on 40/0; the scale %.6f is it over the 40/0 DRcalc day's sum" % (
        res40["months"][TP.MONTH]["mean_day_kwh"], k_scale))
    P("   the lid basis %.2f C: the minimum of the 40/0 DRcalc file's September T2m (energy_two_pack.py's DRCALC)" % tmin)
    P("   the ratio %.4f: energy_inputs.yaml solar.panel.performance_ratio, src \"%s\"" % (
        pr0, d0["solar"]["panel"]["performance_ratio"]["src"]))
    P("   Every day, the scale, the lid basis and the ratio come from that one site; no other site's file is in the tree,")
    P("   so no other site is run here.")
    P("")
    P("END. Each line is the model's arithmetic on the September reference day; nothing is measured.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
