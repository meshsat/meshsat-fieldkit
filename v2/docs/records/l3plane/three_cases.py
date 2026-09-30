#!/usr/bin/env python3
"""three_cases.py: M1's energy on the reference day and over the past Septembers for three power-path cases and one
derated variant, kept apart (stream l3plane with stream r11dep, MESHSAT-1357, 30 September 2026; the owner's amendments of
that day: "distinguish: the circuit as drawn; the resistor-only proposal; any hypothetical corrected power path used for
feasibility calculations", "Do not count energy available only through an inadequate power path as demonstrated
capability", and "Show its energy consequence as a clearly labelled derated variant; preserve the actual as-drawn case").

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured. Every energy figure is MODELED on a1elec's
energy_two_pack.py through energy_basis.py's set-up (imported, pinned); the electrical limits are read from r11dep's
r11_dep.out (pinned); every coverage figure is a MODELLED HISTORICAL COVERAGE, not a success probability.

The cases (board A's front end U2 LM5176 with its average-current sense R11, board A's charger U3 BQ25731):
  AS DRAWN    R11 10 mOhm and U3 as set (entry E1, IIN_HOST 4.15 A): the lower of U3's setting and the front end's stacked
              minimum less the other VBUS20 loads reaches U3 (r11_dep.out 3). The model's min(available, cap) is kept, which
              the as-drawn charge path does not guarantee either (r11dep A-2): these figures are its upper bound.
  DERATED     a variant of AS DRAWN, U3's IIN_HOST at 4.05 A: it fixes the current-limit coordination only (U3's maximum plus
              the other loads under the front end's stacked minimum); it resolves nothing else.
  RESISTOR    R11 6.2 mOhm and U3 IIN_HOST 6.2 A, nothing else changed: INCONCLUSIVE. Its upper bound is the corrected path's
              figure; its lower bound here takes r11dep B-5's inferred collapse (a fixed IIN_HOST with a source that gives less
              than U3 asks walks VIN_RAW down to the stage's latch): an hour whose power at VBUS20 is under U3's cap delivers
              nothing. That bound is pessimistic in hours where the packs are full or tapering, when U3 asks less than its cap.
  CORRECTED   HYPOTHETICAL: the figures energy_basis.py's NOM and WE assume (min(available, cap) at U3's 6.2 A), valid only
              with every correction r11dep's R11-DEPENDENCY.md lists; the stacked minimum of the proposed front end fed as
              its cap moves no result (checked here).

Before any result it proves (exit 4 otherwise) that its mean-day runs reproduce energy_basis.out section 5's NOM, WE and
GEN rows and its window runs reproduce weather_basis.out's NOM and WE coverage of the 4S14P and 4S15P lids.

Run from the repository root:  python3 v2/docs/records/l3plane/three_cases.py > v2/docs/records/l3plane/three_cases.out
Deterministic. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
PIN_EB = "7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47"
if hashlib.sha256(open(os.path.join(HERE, "energy_basis.py"), "rb").read()).hexdigest() != PIN_EB:
    sys.stderr.write("three_cases: energy_basis.py is not the pinned file; refusing\n")
    sys.exit(2)
sys.path.insert(0, HERE)
import energy_basis as EB  # noqa: E402
TP, ER = EB.TP, EB.ER

EB_OUT = "v2/docs/records/l3plane/energy_basis.out"
WB_OUT = "v2/docs/records/l3plane/weather_basis.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
LIDS = ((9, "4S9P both kept"), (14, "4S14P tablet out"), (15, "4S15P QMX out"))
U3_DERATED = 4.05          # r11dep A-1, the derated variant: IIN_HOST at 4.05 A nominal or less (4.05 x 1.025 + 0.060 = 4.211 A, under 4.212 A)
U3_TOL = 0.1               # SLUSE66A 9.6.22 p.80: the maximum 100 mA above the setting; the minimum mirrored (INFERRED), as WE's 6.1 A


def refuse(code, msg):
    sys.stderr.write("three_cases: %s; refusing\n" % msg)
    sys.exit(code)


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def crit(r):
    return (r["ok"], r["ok"] and r["low_t"] > EB.FLOOR, r["ok"] and r["low_b"] > EB.FLOOR and r["low_l"] > EB.FLOOR)


def main():
    D0, PACK0, RES0, t2m = TP.load_model()
    EB.D0, EB.PACK0, EB.RES0 = D0, PACK0, RES0
    EB.TMIN = round(min(t2m), 2)
    eb_out = EB.head_equal(EB_OUT)
    wb_out = EB.head_equal(WB_OUT)
    r11 = EB.head_equal(R11_OUT)
    notes = " ".join(EB.head_equal(EB.PANEL).split())
    m = need(notes, r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", "NOTES step")
    md = need(notes, r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", "NOTES drain")
    EB.FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_w = float(md.group(2)) / D0["mission"]["hours"]
    vr = EB.VR.compute()
    AC, _e, _t = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    v_min, v_nom = vr["bands"][0][4], vr["nominal"]
    rd = EB.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EB.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in need(TP.PAR["v_ak"][1], r"([\d]+) / ([\d]+) / ([\d]+) mV", "v_ak").groups())

    # the electrical limits, from r11dep (checked there, CHECK-3)
    held = tuple(float(x) for x in need(r11, r"held, R11 10\.0 mOhm:\s+([\d.]+) / ([\d.]+) / ([\d.]+) A", "r11_dep.out held band").groups())
    prop = tuple(float(x) for x in need(r11, r"proposed, R11 6\.2 mOhm:\s+([\d.]+) / ([\d.]+) / ([\d.]+) A", "r11_dep.out proposed band").groups())
    other = float(need(r11, r"plus ([\d.]+) A of VBUS20's other loads", "r11_dep.out other loads").group(1))
    fe_held, fe_prop = held[0] - other, prop[0] - other
    u3_e1, u3_e2 = TP.v("u3_iin_e1_a"), TP.v("u3_iin_draft_a")

    def we(v, i, extra=None):
        x = {"eta_u3": EB.u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    # (bus, U3's input limit, overrides) per case and input set
    cases = {
        ("GEN", "NOM"): (v_nom, u3_e1, {"eta_u3": EB.u3_day(v_nom, u3_e1, "TI"), "fe_i": vr["cc"]["gen"][0]}),
        ("DRAWN", "NOM"): (v_nom, u3_e1, {"eta_u3": EB.u3_day(v_nom, min(u3_e1, fe_held), "TI"), "fe_i": fe_held}),
        ("DRAWN", "WE"): (v_min, u3_e1 - U3_TOL, we(v_min, min(u3_e1 - U3_TOL, fe_held), {"fe_i": fe_held})),
        ("DERATED", "NOM"): (v_nom, U3_DERATED, {"eta_u3": EB.u3_day(v_nom, U3_DERATED, "TI"), "fe_i": fe_held}),
        ("DERATED", "WE"): (v_min, U3_DERATED - U3_TOL, we(v_min, U3_DERATED - U3_TOL, {"fe_i": fe_held})),
        ("CORRECTED", "NOM"): (v_nom, u3_e2, {"eta_u3": EB.u3_day(v_nom, u3_e2, "TI")}),
        ("CORRECTED", "WE"): (v_min, 6.1, we(v_min, 6.1)),
        ("CORRECTED-FE", "NOM"): (v_nom, u3_e2, {"eta_u3": EB.u3_day(v_nom, u3_e2, "TI"), "fe_i": fe_prop}),
        ("CORRECTED-FE", "WE"): (v_min, 6.1, we(v_min, 6.1, {"fe_i": fe_prop})),
    }
    cases[("RESISTOR-LB", "NOM")] = cases[("CORRECTED", "NOM")]
    cases[("RESISTOR-LB", "WE")] = cases[("CORRECTED", "WE")]

    node0 = TP.node_power

    def node_collapse(d, res4, g, wp, window, entry):
        """B-5's inferred collapse: the charge path delivers U3's cap or nothing."""
        if entry is None:
            return node0(d, res4, g, wp, window, entry)
        e_st, e_fe, e_ch = TP.chain(d)
        avail = min(TP.EB.panel_w(g, wp, res4["pr"]), window) * e_st * e_fe
        cap = min(entry["fe_out_w"], entry["u3_in_w"])
        return cap * e_ch if avail >= cap else 0.0

    def sim1(key, n, pr, vals, start, t_l):
        vb, iin, ov = cases[key]
        d, pack, r, cfg = EB.setup(n, pr, vb, iin, ov)
        load0 = TP.LOAD
        TP.LOAD = load0 + ov.get("drain_w", 0.0)
        TP.node_power = node_collapse if key[0] == "RESISTOR-LB" else node0
        try:
            return TP.sim(d, pack, r, EB.Series(vals), 400.0, 200.0, start, TP.v("t_base_c"), t_l, cfg)
        finally:
            TP.LOAD = load0
            TP.node_power = node0

    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def meanday(key, n, b):
        rs = [sim1(key, n, pr0 * rat40[b], [prof0[(s + h) % 24] for h in range(72)], s, EB.TMIN) for s in (6, 18)]
        return {"ok": all(r["ok"] for r in rs), "both": min(r["low_t"] for r in rs), "base": min(r["low_b"] for r in rs),
                "lid": min(r["low_l"] for r in rs), "short": max(r["short"] for r in rs)}

    def cellx(s):
        return ("%6.1f (base %5.1f, lid %5.1f)" % (s["both"], s["base"], s["lid"])) if s["ok"] else ("NOT MET, %5.1f unserved" % s["short"])

    def lines(s):
        return "%s/%s" % ("Y" if s["ok"] and s["both"] > EB.FLOOR else "N", "Y" if s["ok"] and s["base"] > EB.FLOOR and s["lid"] > EB.FLOOR else "N")

    # the windows, as weather_basis.py builds them
    ser = os.path.join(TOP, EB.SERIES[0])
    if hashlib.sha256(open(ser, "rb").read()).hexdigest() != EB.SERIES[1]:
        refuse(2, "the filed series is not the pinned file")
    rows = json.load(open(ser, encoding="utf-8"))["outputs"]["hourly"]
    years = sorted({r_["time"][:4] for r_ in rows})
    by_year = {y: [r_ for r_ in rows if r_["time"][:4] == y] for y in years}
    dayrat = {}
    for y in years:
        for dd in range(30):
            Rp = ER.Ratios(AC, [r_["G(i)"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]], [r_["T2m"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]])
            dayrat[(y, dd)] = (Rp.typical(), Rp.adverse()[0])
    wins = []
    for y in years:
        for dd in range(27):
            for st in (6, 18):
                i0 = dd * 24 + st
                seg = by_year[y][i0:i0 + 72]
                days = [(i0 + i) // 24 for i in range(72)]
                wins.append({"st": st, "t_l": round(min(r_["T2m"] for r_ in seg), 2),
                             "vals": {b: [seg[i]["G(i)"] * dayrat[(y, days[i])][bi] for i in range(72)] for bi, b in enumerate(("TYP", "WAB"))}})

    def cover(key, n, b):
        res = [crit(sim1(key, n, pr0, w["vals"][b], w["st"], w["t_l"])) for w in wins]
        return [sum(1 for x in res if x[i]) for i in range(3)]

    o = []
    P = o.append
    P("M1 ON THREE POWER-PATH CASES AND ONE DERATED VARIANT, KEPT APART (three_cases.py, stream l3plane with r11dep, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, powered or measured. MODELED on a1elec's energy_two_pack.py through energy_basis.py's set-up")
    P("(pinned); the electrical limits from r11dep's r11_dep.out; every coverage figure is a MODELLED HISTORICAL COVERAGE, not a")
    P("success probability. The author's analysis, AI arithmetic; not a qualified review and not the independent check.")
    P("")

    # 0. reproduction
    bad = 0
    sec5 = eb_out.split("\n5. THE CASES ON THE REFERENCE PLANE", 1)[1].split("\n6. ", 1)[0]
    for (key, eb_key) in ((("CORRECTED", "NOM"), "NOM"), (("CORRECTED", "WE"), "WE"), (("GEN", "NOM"), "GEN")):
        for n, _w in LIDS:
            for bi, b in enumerate(("TYP", "WAB")):
                s = meanday(key, n, b)
                row = need(sec5, r"^\s+4S%dP\s+%s\s{2,}(.+?)\s{2,}([YN]/[YN])\s+(.+?)\s{2,}([YN]/[YN])\s*$" % (n, eb_key), "section 5 %s 4S%dP" % (eb_key, n))
                if cellx(s).strip() != row.group(1 + 2 * bi).strip() or lines(s) != row.group(2 + 2 * bi):
                    bad += 1
    secA = wb_out.split("\nA. THE MODELLED HISTORICAL COVERAGE", 1)[1].split("\nB. ", 1)[0]
    rep = {}
    for n, what in LIDS[1:]:
        for kk in ("NOM", "WE"):
            c3 = cover(("CORRECTED", kk), n, "TYP")
            rep[(n, kk)] = c3
            mm = need(secA, r"^\s+%s\s+%s TYP\s+(\d+) of \d+ \(\s*[\d.]+ %%\)\s+(\d+) of \d+ \(\s*[\d.]+ %%\)\s+(\d+) of" % (re.escape(what), kk),
                      "weather_basis.out %s %s" % (what, kk))
            if [int(x) for x in mm.groups()] != c3:
                bad += 1
    P("0. REPRODUCTION: the mean-day runs reproduce energy_basis.out section 5's NOM, WE and GEN rows (18 cells with their pass")
    P("   lines), and the window runs reproduce weather_basis.out A's NOM TYP and WE TYP rows of the 4S14P and 4S15P lids: %s" % (
        "yes" if bad == 0 else "NO (%d)" % bad))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "%d reproduction check(s) failed" % bad)
    P("")

    # 1. the limits fed in
    P("1. THE ELECTRICAL LIMITS FED IN (r11dep's r11_dep.out 3, stacked; checked by CHECK-3)")
    P("   the front end's average limit, held R11 10 mOhm: %.3f / %.3f / %.3f A; proposed R11 6.2 mOhm: %.3f / %.3f / %.3f A" % (held + prop))
    P("   VBUS20's other loads through R11 besides U3: %.3f A; so U3 can draw at most %.3f A (held) and %.3f A (proposed) at the" % (
        other, fe_held, fe_prop))
    P("   front end's stacked minimum. U3's settings: E1 %.2f A (board A as generated), E2 %.2f A (drafted), the derated variant %.2f A;" % (
        u3_e1, u3_e2, U3_DERATED))
    P("   U3's minimum at a setting taken %.1f A under it (INFERRED, as WE's 6.1 A)" % U3_TOL)
    P("")

    # 2. the mean day
    P("2. THE REFERENCE DAY AT 40/0 (SC-37's mean September day; each cell: both packs' lowest store (base, lid) in Wh, or the")
    P("   unserved energy; COMB/EACH as energy_basis.out 1d; start 06 and 18 UTC)")
    rowsets = (
        ("AS DRAWN, NOM inputs: U3 as set, %.2f A, under the front end's %.3f A (the model's min(available, cap) kept: an UPPER bound)" % (u3_e1, fe_held), ("DRAWN", "NOM")),
        ("AS DRAWN, WE inputs: U3 at its INFERRED minimum %.2f A (upper bound as above)" % (u3_e1 - U3_TOL), ("DRAWN", "WE")),
        ("DERATED VARIANT of AS DRAWN, NOM inputs: U3 at %.2f A (coordination only)" % U3_DERATED, ("DERATED", "NOM")),
        ("DERATED VARIANT, WE inputs: U3 at its INFERRED minimum %.2f A" % (U3_DERATED - U3_TOL), ("DERATED", "WE")),
        ("RESISTOR-ONLY, lower bound under B-5's inferred collapse, NOM inputs (INCONCLUSIVE between this and CORRECTED NOM)", ("RESISTOR-LB", "NOM")),
        ("RESISTOR-ONLY, lower bound under B-5's inferred collapse, WE inputs (INCONCLUSIVE between this and CORRECTED WE)", ("RESISTOR-LB", "WE")),
        ("CORRECTED PATH, HYPOTHETICAL, NOM inputs (energy_basis.out NOM)", ("CORRECTED", "NOM")),
        ("CORRECTED PATH, HYPOTHETICAL, WE inputs, CONDITIONAL on three undocumented efficiencies (energy_basis.out WE)", ("CORRECTED", "WE")),
    )
    md_res = {}
    for title, key in rowsets:
        P("   %s" % title)
        for n, what in LIDS:
            s_t, s_w = meanday(key, n, "TYP"), meanday(key, n, "WAB")
            md_res[(key, n)] = (s_t, s_w)
            P("     %-18s TYP %-40s %s   WAB %-40s %s" % (what, cellx(s_t), lines(s_t), cellx(s_w), lines(s_w)))
    same = all(cellx(meanday(("CORRECTED-FE", k), n, b)) == cellx(meanday(("CORRECTED", k), n, b)) for k in ("NOM", "WE") for n, _w in LIDS for b in ("TYP", "WAB"))
    P("   the proposed front end's stacked minimum (%.3f A to U3) fed as the corrected path's cap moves no cell: %s" % (fe_prop, "yes" if same else "NO"))
    same_gen = all(cellx(meanday(("DRAWN", "NOM"), n, b)) == cellx(meanday(("GEN", "NOM"), n, b)) for n, _w in LIDS for b in ("TYP", "WAB"))
    P("   the as-drawn rows at NOM equal energy_basis.out's GEN (the printed %.2f A minimum): %s (U3's %.2f A binds in both)" % (
        vr["cc"]["gen"][0], "yes" if same_gen else "NO", u3_e1))
    P("")

    # 3. coverage
    P("3. THE MODELLED HISTORICAL COVERAGE, %d September 72 h windows of 2005 to 2020 at 40/0 (weather_basis.out A's windows, loads," % len(wins))
    P("   ageing and temperatures), TYP build: windows kept (no STOP) / COMB above the floor / EACH above the floor")
    cov = {}
    for title, key in (("AS DRAWN, NOM (upper bound)", ("DRAWN", "NOM")), ("DERATED VARIANT, NOM", ("DERATED", "NOM")),
                       ("RESISTOR-ONLY lower bound, NOM", ("RESISTOR-LB", "NOM")), ("RESISTOR-ONLY lower bound, WE", ("RESISTOR-LB", "WE"))):
        for n, what in LIDS:
            c3 = cover(key, n, "TYP")
            cov[(key, n)] = c3
            P("   %-34s %-18s %s" % (title, what, " / ".join("%3d (%4.1f %%)" % (x, 100.0 * x / len(wins)) for x in c3)))
    for n, what in LIDS[1:]:
        for kk in ("NOM", "WE"):
            P("   %-34s %-18s %s   (weather_basis.out A, reproduced)" % ("CORRECTED PATH, HYPOTHETICAL, %s" % kk, what,
                                                                         " / ".join("%3d (%4.1f %%)" % (x, 100.0 * x / len(wins)) for x in rep[(n, kk)])))
    P("   CORRECTED PATH, 4S9P: 0 in every case (weather_basis.out A)")
    P("")
    P("END. Each line is the model's arithmetic; nothing is measured. No figure here is demonstrated capability: AS DRAWN and the")
    P("DERATED VARIANT fail M1; RESISTOR-ONLY is INCONCLUSIVE; CORRECTED PATH is HYPOTHETICAL until every correction of")
    P("R11-DEPENDENCY.md is closed.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
