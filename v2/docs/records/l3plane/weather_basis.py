#!/usr/bin/env python3
"""weather_basis.py: M1's modelled historical coverage for the three lid configurations, the store each weather basis would
need (the owner's decision L3-OD6 as a quantified choice), and a bounded table of credible improvements (stream l3plane,
MESHSAT-1357, 30 September 2026; the owner's instruction of that day, folded into the energy basis's second round).

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured. Every energy figure is MODELED on a1elec's
energy_two_pack.py through energy_basis.py's set-up (imported, pinned); the weather is PVGIS's filed hourly series; every
coverage figure is a MODELLED HISTORICAL COVERAGE, the share of past September windows the model carries, not a success
probability; the cell figures are MAKER (Samsung SDI's sheet) and the store sizes INFERRED from the model.

What it runs:
  A. every 72 hour window of the filed series (16 Septembers) for the three lids (4S9P both kept, 4S14P tablet out, 4S15P
     QMX out), at energy_basis.py's WE (restated) with both array builds, and with the three undocumented efficiencies at
     their brackets' lower ends and at the makers' own readings, and at NOM; three failure criteria, each reported: the kit
     stops (both packs empty), the two packs together at or under the floor, either pack alone at or under the floor;
  B. per window, the least lid pack (the base held at 4S6P) that carries it at WE on the COMBINED line, by bisection on the
     lid's parallel count; the store it amounts to; its percentiles for illustrative coverage targets beside SC-37's mean
     day; cells, mass and volume at the cell sheet's figures; the fit against the mechanical records' established places;
  C. one table of credible improvements, each alone from WE: coverage and the mean-day margin, and whether it keeps or
     reduces the approved service.
Before any result it proves (exit 4 otherwise) that its window runs reproduce energy_basis.out section 8's six rows and its
mean-day runs energy_basis.out section 5's WE rows.

Second issue (CHECK-2 of ec415c09, minors 1 to 3): WE-MKR's charge figure follows energy_basis.out's corrected base bound;
the sizing takes the percentile of each window's own cell count; the multiples are given in usable Wh and in cells.

Run from the repository root:  python3 v2/docs/records/l3plane/weather_basis.py > v2/docs/records/l3plane/weather_basis.out
Deterministic. Exit 2: a pinned script is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import json
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
RECS = os.path.join(TOP, "v2", "docs", "records")
PIN_EB = "7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47"
if hashlib.sha256(open(os.path.join(HERE, "energy_basis.py"), "rb").read()).hexdigest() != PIN_EB:
    sys.stderr.write("weather_basis: energy_basis.py is not the pinned file; refusing\n")
    sys.exit(2)
sys.path.insert(0, HERE)
import energy_basis as EB  # noqa: E402
TP, ER = EB.TP, EB.ER

EB_OUT = "v2/docs/records/l3plane/energy_basis.out"
CURVES = "v2/docs/records/l3plane/curve_readings.out"
A1MECH = "v2/docs/records/a1mech/README.md"
POWER = "v2/docs/feasibility/POWER-THERMAL.md"
CELL_SPEC = "v2/vendor/battery/samsung-35e-orbtronic.pdf"   # Ver. 1.1, pinned by energy_inputs.yaml: 3.1, 3.10, 3.11
LIDS = ((9, "4S9P both kept"), (14, "4S14P tablet out"), (15, "4S15P QMX out"))
TARGETS = (50, 80, 95)                                      # ILLUSTRATIVE coverage targets, not proposals


def refuse(code, msg):
    sys.stderr.write("weather_basis: %s; refusing\n" % msg)
    sys.exit(code)


def page(rel, n):
    return subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"],
                          capture_output=True, text=True, check=True).stdout


def sim1(n, pr, vbus, iin, over, vals, start, t_l, wp=400.0):
    over = over or {}
    d, pack, r, cfg = EB.setup(n, pr, vbus, iin, over)
    load0 = TP.LOAD
    TP.LOAD = load0 + over.get("drain_w", 0.0)
    try:
        return TP.sim(d, pack, r, EB.Series(vals), wp, 200.0, start, TP.v("t_base_c"), t_l, cfg)
    finally:
        TP.LOAD = load0


def crit(r):
    """(the kit never stops, both packs together above the floor, each pack above the floor)"""
    return (r["ok"], r["ok"] and r["low_t"] > EB.FLOOR, r["ok"] and r["low_b"] > EB.FLOOR and r["low_l"] > EB.FLOOR)


def main():
    D0, PACK0, RES0, t2m = TP.load_model()
    EB.D0, EB.PACK0, EB.RES0 = D0, PACK0, RES0
    EB.TMIN = round(min(t2m), 2)
    eb_out = EB.head_equal(EB_OUT)
    curves = EB.head_equal(CURVES)
    panel = EB.head_equal(EB.PANEL)
    notes = " ".join(panel.split())
    m = re.search(r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", notes)
    md = re.search(r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", notes)
    if not (m and md):
        refuse(3, "reconcile_lid_panel.out's NOTES not parsed")
    EB.FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_wh = float(md.group(2))
    drain_w = drain_wh / D0["mission"]["hours"]
    vr = EB.VR.compute()
    AC, _e, _t = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    v_min, v_nom = vr["bands"][0][4], vr["nominal"]
    rd = EB.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EB.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in re.search(r"([\d]+) / ([\d]+) / ([\d]+) mV", TP.PAR["v_ak"][1]).groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    rd_st = re.search(r"READING at 6 to 12 A on the 35 V curve \(board E's stage delivers up to about 12 A at 15\.1 V\): ([\d.]+) to", curves)
    rd_fe = re.search(r"READING at 5\.5 to 6 A \(board A's front end carries U3's 6\.1 A\): ([\d.]+) to", curves)
    rd_cb = re.findall(r"A discharging: (0\.\d{4})", eb_out)
    if not (rd_st and rd_fe and len(rd_cb) >= 3):
        refuse(3, "the makers' readings not parsed")
    st_mkr, fe_mkr, cb_mkr = float(rd_st.group(1)) / 100.0, float(rd_fe.group(1)) / 100.0, min(float(x) for x in rd_cb)
    ptxt = " ".join(open(os.path.join(TOP, POWER), encoding="utf-8").read().split())
    mp = re.search(r"PS-IDLE-SPEC with both WiFi link cards held off\*\* \(no peer kit linked, PCIE_PWR_EN held low by software\): ([\d.]+) W, saving ([\d.]+) W", ptxt)
    if not mp:
        refuse(3, "POWER-THERMAL.md's link-off variant not parsed")
    link_off_w, link_save = float(mp.group(1)), float(mp.group(2))
    iin_clamp = TP.v("u3_iin_max_a")

    def we(v, i, extra=None):
        x = {"eta_u3": EB.u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    e_nom = EB.u3_day(v_nom, TP.v("u3_iin_draft_a"), "TI")
    cases = {
        "WE": (v_min, 6.1, we(v_min, 6.1)),
        "WE-LO": (v_min, 6.1, we(v_min, 6.1, {"eta_st": ch[0]["low"], "eta_fe": ch[1]["low"], "chg_eta": ce["low"]})),
        "WE-MKR": (v_min, 6.1, we(v_min, 6.1, {"eta_st": st_mkr, "eta_fe": fe_mkr, "chg_eta": cb_mkr})),
        "NOM": (v_nom, TP.v("u3_iin_draft_a"), {"eta_u3": e_nom}),
    }

    # the series and its windows
    ser = os.path.join(TOP, EB.SERIES[0])
    if hashlib.sha256(open(ser, "rb").read()).hexdigest() != EB.SERIES[1]:
        refuse(2, "the filed series is not the pinned file")
    sj = json.load(open(ser, encoding="utf-8"))
    rows = sj["outputs"]["hourly"]
    years = sorted({r_["time"][:4] for r_ in rows})
    by_year = {y: [r_ for r_ in rows if r_["time"][:4] == y] for y in years}
    dayrat = {}
    for y in years:
        for dd in range(30):
            G = [r_["G(i)"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]]
            TA = [r_["T2m"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]]
            Rp = ER.Ratios(AC, G, TA)
            dayrat[(y, dd)] = (Rp.typical(), Rp.adverse()[0])
    wins = []
    for y in years:
        yr = by_year[y]
        for dd in range(27):
            for st in (6, 18):
                i0 = dd * 24 + st
                seg = yr[i0:i0 + 72]
                days = [(i0 + i) // 24 for i in range(72)]
                vals = {b: [seg[i]["G(i)"] * dayrat[(y, days[i])][bi] for i in range(72)] for bi, b in enumerate(("TYP", "WAB"))}
                wins.append({"y": y, "day": dd + 1, "st": st, "vals": vals, "t_l": round(min(r_["T2m"] for r_ in seg), 2),
                             "irr": sum(r_["G(i)"] for r_ in seg) / 1000.0})

    def cover(n, key, b, over_extra=None, wp=400.0, load_delta=0.0, iin=None, vbus=None):
        c = cases[key]
        ov = dict(c[2])
        ov.update(over_extra or {})
        if load_delta:
            ov["drain_w"] = ov.get("drain_w", 0.0) + load_delta
        res = [crit(sim1(n, pr0, vbus or c[0], iin or c[1], ov, w["vals"][b], w["st"], w["t_l"], wp)) for w in wins]
        return [sum(1 for x in res if x[i]) for i in range(3)]

    # mean day at 40/0
    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def meanday(n, key, b, over_extra=None, wp=400.0, load_delta=0.0, iin=None, vbus=None):
        c = cases[key]
        ov = dict(c[2])
        ov.update(over_extra or {})
        if load_delta:
            ov["drain_w"] = ov.get("drain_w", 0.0) + load_delta
        rs = [sim1(n, pr0 * rat40[b], vbus or c[0], iin or c[1], ov, [prof0[(s + h) % 24] for h in range(72)], s, EB.TMIN, wp)
              for s in (6, 18)]
        return {"ok": all(r["ok"] for r in rs), "both": min(r["low_t"] for r in rs), "base": min(r["low_b"] for r in rs),
                "lid": min(r["low_l"] for r in rs), "short": max(r["short"] for r in rs), "eb": rs[0]["eb_full"], "el": rs[0]["el_full"]}

    o = []
    P = o.append
    P("M1'S MODELLED HISTORICAL COVERAGE, THE STORE EACH WEATHER BASIS WOULD NEED, AND CREDIBLE IMPROVEMENTS (weather_basis.py,")
    P("stream l3plane, MESHSAT-1357). PROTOTYPE DESIGN: nothing built, powered or measured. MODELED on a1elec's energy_two_pack.py")
    P("through energy_basis.py's set-up (pinned); every coverage figure is a MODELLED HISTORICAL COVERAGE, not a success")
    P("probability. The author's analysis, AI arithmetic; not a qualified review and not the independent check.")
    P("")

    # 0. reproduction
    bad = 0
    sec8 = eb_out.split("\n8. INFORMATIVE ONLY", 1)[1]
    for n in (14, 15):
        for key, b in (("NOM", "TYP"), ("WE", "TYP"), ("WE", "WAB")):
            cnt = cover(n, key, b)[0]
            mm = re.search(r"^\s+4S%dP\s+%s %s\s+(\d+) of\s+(\d+)" % (n, key, b), sec8, re.M)
            if not mm or int(mm.group(1)) != cnt or int(mm.group(2)) != len(wins):
                bad += 1
    sec5 = eb_out.split("\n5. THE CASES ON THE REFERENCE PLANE", 1)[1].split("\n6. ", 1)[0]
    for n in (9, 14, 15):
        for b in ("TYP", "WAB"):
            s = meanday(n, "WE", b)
            txt = ("%6.1f (base %5.1f, lid %5.1f)" % (s["both"], s["base"], s["lid"])) if s["ok"] else ("NOT MET, %5.1f unserved" % s["short"])
            if txt not in sec5:
                bad += 1
    P("0. REPRODUCTION: this script's window runs reproduce energy_basis.out section 8's six counts, and its mean-day runs the six")
    P("   WE rows of section 5: %s" % ("yes" if bad == 0 else "NO (%d)" % bad))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "%d reproduction check(s) failed" % bad)
    P("")

    # A. definitions and coverage
    P("A. THE MODELLED HISTORICAL COVERAGE, EXACTLY")
    P("   dataset: PVGIS 5.2, the seriescalc API (%s), radiation %s, meteorology %s, horizon %s; hourly averages," % (
        re.sub(r"\?.*", "", "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?"), sj["inputs"]["meteo_data"]["radiation_db"],
        sj["inputs"]["meteo_data"]["meteo_db"], sj["inputs"]["meteo_data"]["horizon_data"]))
    P("     UTC, stamped at HH:11; the September rows filed as %s" % EB.SERIES[0])
    P("   years: %s to %s (%d Septembers); the panel orientation: slope %d degrees, azimuth %d (south), latitude %.3f, longitude %.3f" % (
        years[0], years[-1], len(years), sj["inputs"]["mounting_system"]["fixed"]["slope"]["value"],
        sj["inputs"]["mounting_system"]["fixed"]["azimuth"]["value"], sj["inputs"]["location"]["latitude"], sj["inputs"]["location"]["longitude"]))
    P("   windows: %d of 72 hours, one starting at 06:00 and one at 18:00 UTC on each of 1 to 27 September of each year, so they" % len(wins))
    P("     OVERLAP (starts 12 h apart); none crosses the month's end (the last window's last hour is 30 September 17:11 UTC);")
    P("     the series is used as PVGIS gives it, not scaled to the 2015 to 2020 monthly mean")
    P("   initial charge: both packs full (their aged usable energy) at each window's start; no carry-over between windows")
    P("   ageing: REQ-014's 80 percent of the cells' specification minimum (energy_inputs.yaml aged_80), the 3.00 V line with the")
    P("     5 percent reserve; pack temperatures: the base at +%.0f C, the lid at the window's own minimum air (T2m)" % TP.v("t_base_c"))
    P("   load: PS-IDLE-SPEC %.1f W at the pack terminals (POWER-THERMAL.md section 4), plus in every WE case the lid path's standby" % TP.LOAD)
    P("     drain, %.1f Wh over 72 h (reconcile_lid_panel.out NOTES), both split between the packs by capacity" % drain_wh)
    P("   array: 400 Wp, four Renogy RNG-100DB-H in 2S2P, a 200 W stage window; each calendar day's own TYP or WAB ratio")
    P("   failure criteria, all three reported: STOP, the kit stops (both packs at their 3.00 V line: the model's M1 verdict);")
    P("     COMB, the two packs' combined lowest store at or under %.1f Wh; EACH, either pack's own lowest store at or under %.1f Wh" % (EB.FLOOR, EB.FLOOR))
    P("   the cases: WE, energy_basis.out 1c's restated WE (conditional on the stage %.2f, front end %.2f and charge %.2f declared);" % (
        ch[0]["eta"], ch[1]["eta"], ce["value"]))
    P("     WE-LO, the same three at their brackets' lower ends (%.2f, %.2f, %.2f); WE-MKR, the same three at the makers' readings" % (
        ch[0]["low"], ch[1]["low"], ce["low"]))
    P("     (stage %.3f and front end %.3f, curve_readings.out; charge %.4f, the cell sheet's resistive bound, energy_basis.out 2):" % (
        st_mkr, fe_mkr, cb_mkr))
    P("     INFERRED readings of other circuits and an upper bound, not established; NOM, energy_basis.out 1c's nominal inputs")
    P("")
    P("   %-18s %-10s %-26s %-26s %-26s" % ("lid", "case", "windows kept: no STOP", "COMB above the floor", "EACH above the floor"))
    covA = {}
    for n, what in LIDS:
        for key, b in (("WE", "TYP"), ("WE", "WAB"), ("WE-LO", "TYP"), ("WE-MKR", "TYP"), ("NOM", "TYP")):
            c3 = cover(n, key, b)
            covA[(n, key, b)] = c3
            P("   %-18s %-10s %s" % (what, "%s %s" % (key, b), " ".join("%4d of %d (%5.1f %%)       " % (x, len(wins), 100.0 * x / len(wins)) for x in c3)))
    P("   MODELLED HISTORICAL COVERAGE: the share of these past September windows the model carries; not a probability of success.")
    P("")

    # B. sizing
    P("B. THE STORE EACH WEATHER BASIS WOULD NEED (the owner's decision L3-OD6; ILLUSTRATIVE targets, not proposals)")
    P("   Method: for each window, the least lid pack (the base held at 4S6P) with which the window passes COMB at WE, by bisection")
    P("   on the lid's parallel count (a real number, so the store is continuous); the store it amounts to is the base's and the")
    P("   lid's usable energy at the window's own lid temperature (aged, to the 3.00 V line with the reserve, at the load's rate).")
    P("   A target of X %% takes the X-th percentile of those stores over the %d windows. The mean-day basis (SC-37) uses the same" % len(wins))
    P("   bisection on the reference day at 40/0, both starts.")

    def need_lid(runs):
        lo, hi = 1.0, 400.0
        if runs(lo):
            return lo
        if not runs(hi):
            return None
        for _ in range(16):
            mid = 0.5 * (lo + hi)
            if runs(mid):
                hi = mid
            else:
                lo = mid
        return hi
    cw, cm = cases["WE"][2], cases["WE"]
    need = {}
    for b in ("TYP", "WAB"):
        lst = []
        for w in wins:
            f = (lambda x, w=w: crit(sim1(x, pr0, cm[0], cm[1], cw, w["vals"][b], w["st"], w["t_l"]))[1])
            x = need_lid(f)
            r = sim1(x, pr0, cm[0], cm[1], cw, w["vals"][b], w["st"], w["t_l"])
            lst.append((r["eb_full"] + r["el_full"], x, w))
        need[b] = sorted(lst, key=lambda z: z[0])
    md_need = {}
    for b in ("TYP", "WAB"):
        f = (lambda x, b=b: all(crit(sim1(x, pr0 * rat40[b], cm[0], cm[1], cw, [prof0[(s + h) % 24] for h in range(72)], s, EB.TMIN))[1]
                                for s in (6, 18)))
        x = need_lid(f)
        r = sim1(x, pr0 * rat40[b], cm[0], cm[1], cw, [prof0[(6 + h) % 24] for h in range(72)], 6, EB.TMIN)
        md_need[b] = (r["eb_full"] + r["el_full"], x)

    # the cell sheet and the places
    t1 = page(CELL_SPEC, 3)
    mw = re.search(r"3\.10 Cell Weight\s+(\d+) g max", t1)
    mh = re.search(r"Height : Max\. ([\d.]+) mm", t1)
    mdm = re.search(r"Diameter: Max\. \S+ ([\d.]+) mm", t1)
    mc = re.search(r"Min ([\d,]+)mAh", t1)
    mv = re.search(r"3\.3 Nominal Voltage\s+([\d.]+)V", t1)
    if not (mw and mh and mdm and mc and mv):
        refuse(3, "the cell sheet's page 3 not parsed")
    g_cell, h_cell, d_cell = float(mw.group(1)), float(mh.group(1)), float(mdm.group(1))
    ah_cell, v_cell = float(mc.group(1).replace(",", "")) / 1000.0, float(mv.group(1))
    wh_cell = ah_cell * v_cell
    vol_box = d_cell * d_cell * h_cell / 1000.0
    vol_cyl = math.pi * (d_cell / 2) ** 2 * h_cell / 1000.0
    mech = open(os.path.join(TOP, A1MECH), encoding="utf-8").read()
    places = {}
    for lab, n in (("A", 9), ("B", 14), ("C", 15)):
        mm = re.search(r"^\| %s \| [^|]+\| (\d+) \|" % lab, mech, re.M)
        if not mm:
            refuse(3, "a1mech's arrangement %s not parsed" % lab)
        places[n] = int(mm.group(1))
    base_cells = 4 * TP.NP_B
    cur = {n: meanday(n, "WE", "TYP") for n, _w in LIDS}
    P("   cells (MAKER, %s): %.2f Ah minimum x %.2f V nominal = %.2f Wh a cell (3.1, 3.3); %.0f g maximum (3.10); %.2f mm high by" % (
        CELL_SPEC, ah_cell, v_cell, wh_cell, g_cell, h_cell))
    P("     %.2f mm across (3.11): %.2f cm3 as a cylinder, %.2f cm3 as its square footprint. Cells only: holders, protection" % (d_cell, vol_cyl, vol_box))
    P("     boards, wiring and enclosures are not counted. Established places (a1mech README section 2's table; the base 4S6P,")
    P("     %d cells): lid A %d, B %d, C %d, so at most %s cells in 4S groups." % (
        base_cells, places[9], places[14], places[15],
        ", ".join("%d (%s)" % (base_cells + 4 * (places[n] // 4), w) for n, w in LIDS)))
    P("   the current stores at WE on the mean day (the model's usable at the reference lid temperature %.2f C):" % EB.TMIN)
    for n, what in LIDS:
        cells = base_cells + 4 * n
        P("     %-18s %3d cells, %.1f Wh nominal, %.1f Wh usable (%.3f of nominal: ageing 0.80, the 3.00 V line with the reserve," % (
            what, cells, cells * wh_cell, cur[n]["eb"] + cur[n]["el"], (cur[n]["eb"] + cur[n]["el"]) / (cells * wh_cell)))
        P("     %-18s rate and temperature, as the model computes them)" % "")
    P("   the allowances between nominal and usable, per pack of the 4S21P kit (energy_budget.py's Pack.usable_wh, its factors):")
    for lab, n_p, t_c in (("base 4S6P at +%.0f C" % TP.v("t_base_c"), TP.NP_B, TP.v("t_base_c")), ("lid 4S15P at %.2f C" % EB.TMIN, 15, EB.TMIN)):
        wh_, k_ = PACK0.usable_wh(TP.LOAD * n_p / (TP.NP_B + 15), t_c, PACK0.age80, "3v00", n_p)
        P("     %-22s %.3f A a cell: rate %.3f, temperature %.3f, mean voltage %.3f V (%.3f of %.2f V), to the 3.00 V line or the" % (
            lab, k_["i_cell"], k_["f_rate"], k_["f_t"], k_["v_mean"], k_["v_mean"] / v_cell, v_cell))
        P("     %-22s 5 %% reserve %.3f, ageing %.2f: %.3f of nominal, %.1f Wh" % (
            "", k_["f_dod"], k_["age"], k_["f_rate"] * k_["f_t"] * k_["v_mean"] / v_cell * k_["f_dod"] * k_["age"], wh_))
    P("   cell limits: charge at most %.3f A a cell for cycle life (REQ-075; the sheet's 3.5), against U3's %.3f A over 6 cells and" % (
        1.02, TP.v("chg_a_base")))
    P("     U3B's %.3f A over the lid's cells (%.3f A a cell at 4S15P, less for a larger lid); discharge far under the sheet's 8 A (3.8)" % (
        TP.v("chg_a_lid"), TP.v("chg_a_lid") / 15))
    P("")
    P("   Third issue (CHECK-2 minors 2 and 3): the cells are the percentile of each window's own cell count (the least 4S")
    P("   group that carries it), not the count of the window at the store's percentile; the multiples are given both in usable")
    P("   Wh (against the 4S21P kit at the reference lid temperature) and in cells (against its 84 cells, the physical quantity).")
    P("   %-30s %-6s %-14s %-12s %-12s %-12s %-12s %-22s %-22s %s" % ("basis", "build", "usable, Wh", "lid, 4SnP", "cells (4S)",
                                                                  "nominal, Wh", "mass, kg", "volume, l (cyl / box)",
                                                                  "x the 4S21P: Wh; cells", "fits?"))
    usable21 = cur[15]["eb"] + cur[15]["el"]
    cells21 = base_cells + 4 * 15
    opt_rows = []
    for b in ("TYP", "WAB"):
        u, x = md_need[b]
        opt_rows.append(("(i) SC-37's mean day, 40/0", b, u, int(math.ceil(x - 1e-9))))
        counts = sorted(int(math.ceil(z[1] - 1e-9)) for z in need[b])
        for tgt in TARGETS:
            k = max(0, int(math.ceil(tgt / 100.0 * len(wins))) - 1)
            opt_rows.append(("(ii) %d %% of the windows" % tgt, b, need[b][k][0], counts[k]))
    mult = {"wh": [], "cells": []}
    for lab, b, u, n_l in opt_rows:
        cells = base_cells + 4 * n_l
        fits = [w for n, w in LIDS if cells <= base_cells + 4 * (places[n] // 4)]
        if lab.startswith("(ii)"):
            mult["wh"].append(u / usable21)
            mult["cells"].append(cells / float(cells21))
        P("   %-30s %-6s %-14.1f %-12s %-12d %-12.1f %-12.2f %-22s %-22s %s" % (
            lab, b, u, "4S%dP" % n_l, cells, cells * wh_cell, cells * g_cell / 1000.0,
            "%.1f / %.1f" % (cells * vol_cyl / 1000.0, cells * vol_box / 1000.0), "%.2f; %.2f" % (u / usable21, cells / float(cells21)),
            ("fits " + ", ".join(fits)) if fits else "fits no established arrangement"))
    P("   The store needed per window (TYP): median %.1f Wh, the largest %.1f Wh; the model's store of the 4S21P kit %.1f Wh." % (
        need["TYP"][len(wins) // 2][0], need["TYP"][-1][0], usable21))
    P("   'Several times more energy': the illustrative targets need %.2f to %.2f times the 4S21P kit's usable store, and %.2f to" % (
        min(mult["wh"]), max(mult["wh"]), min(mult["cells"])))
    P("   %.2f times its %d cells." % (max(mult["cells"]), cells21))
    P("   Assumptions: WE's inputs (conditional on the three undocumented efficiencies); 400 Wp; the load as in A; the store grown on")
    P("   the lid's side with U3B's code 62 charge current unchanged; a full store at each window's start; the percentile is over")
    P("   overlapping windows of 16 Septembers, not independent trials.")
    P("")

    # C. improvements
    P("C. CREDIBLE IMPROVEMENTS, EACH ALONE FROM WE (TYP): the modelled historical coverage (COMB) of the 4S14P and 4S15P lids,")
    P("   and the mean-day margin on 40/0 (the lowest combined store, TYP / WAB, or NOT MET); nothing designed, nothing adopted")
    rowsC = [
        ("WE as restated (the reference)", {}, 400.0, 0.0, None, "", "the reference"),
        ("PS-IDLE-SPEC with both WiFi link cards held off, %.1f W (%.1f W less; POWER-THERMAL.md section 4)" % (link_off_w, link_save),
         {}, 400.0, -link_save, None, "", "REDUCES the approved service: the kit-to-kit link card is off (valid only while no peer kit is linked); a proposal"),
        ("the array at 600 Wp (2S3P, six panels; each day's 2S2P ratio kept, INFERRED)", {}, 600.0, 0.0, None, "",
         "PRESERVES the service; outside the owner's stated 'about 400 Wp into a 200 W stage': his call"),
        ("U3's input limit set to its %.2f A clamp (energy_two_pack.py u3_iin_max_a, MAKER), %.2f A minimum (INFERRED as for 6.1 A)" % (
            iin_clamp, iin_clamp - 0.1), {"eta_u3": EB.u3_day(v_min, iin_clamp - 0.1, "lower")}, 400.0, 0.0, iin_clamp - 0.1, "",
         "PRESERVES the service; a register setting inside the drafted entry (R16 10 mOhm, the front end's 6.94 A)"),
        ("board E's stage at its maker curve's reading %.3f (curve_readings.out 2, INFERRED)" % st_mkr, {"eta_st": st_mkr}, 400.0, 0.0,
         None, "", "PRESERVES the service; a figure to be established, not an improvement one can apply"),
    ]
    P("   %-100s %-16s %-16s %-26s %s" % ("improvement", "4S14P coverage", "4S15P coverage", "mean-day margin 4S14P; 4S15P", "service"))
    for lab, ex, wp, dl, iin, _x, svc in rowsC:
        cov = [cover(n, "WE", "TYP", ex, wp, dl, iin)[1] for n in (14, 15)]
        mdm_ = []
        for n in (14, 15):
            cc = []
            for b in ("TYP", "WAB"):
                s = meanday(n, "WE", b, ex, wp, dl, iin)
                cc.append(("%.1f" % s["both"]) if s["ok"] else "NOT MET")
            mdm_.append(" / ".join(cc))
        P("   %-100s %-16s %-16s %-26s %s" % (lab, "%.1f %%" % (100.0 * cov[0] / len(wins)), "%.1f %%" % (100.0 * cov[1] / len(wins)),
                                           "; ".join(mdm_), svc))
    P("   Not in the table: PS-IDLE-SPEC's documented LOW, %s W (POWER-THERMAL.md section 4), is a bound from the loads' lowest" % (
        re.search(r"PS-IDLE-SPEC \(monitor on, APRS beacons\) \| [\d.]+ \| ([\d.]+) /", ptxt).group(1)))
    P("   documented figures, not an established idle load; no measured load exists.")
    P("")
    P("END. Each line is the model's arithmetic; nothing is measured.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
