#!/usr/bin/env python3
"""energy_basis.py: the energy basis of the owner's layer 3 decisions L3-OD1, L3-OD2 and L3-OD4 (stream l3plane,
MESHSAT-1357, 30 September 2026): M1's energy balance with the charge bus at its established range, its sensitivity to
every input the model carries, exact case definitions, and an INFORMATIVE worse-weather case.

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured. Every energy figure is MODELED; the bus range is
vbus20_range.py's (MAKER, NETLIST, INFERRED per term); every band is INFERRED from the model's grid.

The model is reconcile_lid_panel.py's: a1elec's energy_two_pack.py (pinned) with the lid's parallel count, the
performance ratio and U3's input limit set, the rest of its parameters as carried. This script builds each run the way
reconcile_lid_panel.run() does, with these inputs made explicit instead of fixed:
  * the charge bus VBUS20 (V) at which U3's current limit becomes power (the model holds it at V_BUS20 = 20.7 V), and the
    front end's drafted current limit at the same bus (43 mV over the drafted 6.2 mOhm);
  * U3's input current limit (A); U3's efficiency, recomputed at that bus and limit by stream s117's own method
    (efficiency.py's daily(), imported unchanged, pinned), at TI's reading, the makers' maxima (lower) or the favourable
    reading (upper);
  * U3B's efficiency, the stage's and the front end's efficiencies, the pack's charge efficiency, the lid's discharge and
    charge loops and the ideal diode's drop, each within the bracket the model's own sources print (parsed, not typed).
Before any result it proves (exit 4 otherwise): 0a the runs reproduce every row of reconcile_lid_panel.out byte for byte
at 20.7 V; 0b the U3 figure reproduces efficiency.py's day at E2 exactly; 0c the plane runs reproduce plane_grid.out's case
P lowest stores on all 50 planes for both lid options; 0d a 72 hour series fed hour by hour reproduces the mean-day run.

Run from the repository root:  python3 v2/docs/records/l3plane/energy_basis.py > v2/docs/records/l3plane/energy_basis.out
Deterministic. Exit 2: a pinned script or input is not the pinned file; 3: an input cannot be parsed; 4: a reproduction
check failed."""
import copy
import hashlib
import json
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
        "s117/efficiency.py": "c24d5cfe209be3db7437c39c6762ef4257dd881d561cba047284aa7cc08b5809",
        "l3plane/vbus20_range.py": "7b4dbea2e25de487a0ce6e734ab65f74ebea87f7a3532159c611ae47cc7ffeaa"}
SERIES = ("v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json",
          "c5f0363a9d97b6db6e5ef10fa89904fd55e30aca67007760b9d77caa3b0debd7")
for _rel, _want in PINS.items():
    if hashlib.sha256(open(os.path.join(RECS, _rel), "rb").read()).hexdigest() != _want:
        sys.stderr.write("energy_basis: %s is not the pinned file; refusing\n" % _rel)
        sys.exit(2)
for _d in ("a1elec", "a1solar", "s117", "l3plane", "a1int"):
    sys.path.insert(0, os.path.join(RECS, _d))
import energy_two_pack as TP  # noqa: E402
import energy_runs as ER  # noqa: E402
import efficiency as EF  # noqa: E402
import vbus20_range as VR  # noqa: E402
import reconcile_lid_panel as RL  # noqa: E402

PANEL = "v2/docs/records/a1int/reconcile_lid_panel.out"
EFF_OUT = "v2/docs/records/s117/efficiency.out"
GRID_OUT = "v2/docs/records/l3plane/plane_grid.out"
SC76_V = 19.08          # SC-76's figure (fnd/l3r2), stream s120's DC band minimum: run for comparison only
LIDS = ((9, "4S9P, both lid functions kept (4S15P in all)"), (14, "4S14P, the tablet bracket out (4S20P in all)"),
        (15, "4S15P, the QMX HF set out (4S21P in all)"))
D0 = PACK0 = RES0 = None
TMIN = None


def refuse(code, msg):
    sys.stderr.write("energy_basis: %s; refusing\n" % msg)
    sys.exit(code)


def head_equal(rel):
    text = open(os.path.join(TOP, rel), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + rel], capture_output=True, text=True).stdout
    if text != head:
        refuse(3, "%s differs from HEAD's" % rel)
    return text


def bracket(text, what):
    m = re.search(r"bracket ([\d.]+) to ([\d.]+)", text)
    if not m:
        refuse(3, "no bracket in %s" % what)
    return float(m.group(1)), float(m.group(2))


def setup(n, pr, vbus, iin, over):
    """reconcile_lid_panel.run()'s set-up with the bus, the limit and the named overrides explicit."""
    TP.NP_L = n
    TP.NP_T = TP.NP_B + n
    d = dict(D0)
    d["solar"] = dict(D0["solar"])
    d["solar"]["chain"] = [dict(c) for c in D0["solar"]["chain"]]
    for k, i in (("eta_st", 0), ("eta_fe", 1), ("eta_u3", 2)):
        if k in over:
            d["solar"]["chain"][i]["eta"] = over[k]
    pack = copy.copy(PACK0)
    if "chg_eta" in over:
        pack.chg_eta = over["chg_eta"]
    r = dict(RES0)
    r["pr"] = pr
    fe_w = (over["fe_i"] * vbus) if "fe_i" in over else 0.043 / (TP.v("fe_r11_draft_mohm") / 1000.0) * vbus
    TP.ENTRIES["_u3"] = {"fe_out_w": fe_w, "u3_in_w": iin * vbus, "what": ""}
    cfg = TP.base_cfg()
    cfg["entry"] = "_u3"
    for k in ("eta_b", "r_dsg", "r_chg", "v_ak"):
        if k in over:
            cfg[k] = over[k]
    return d, pack, r, cfg


def run(n, pr, vbus, iin, over=None, prof=None, t_l=None):
    d, pack, r, cfg = setup(n, pr, vbus, iin, over or {})
    pf = RES0["months"][TP.MONTH]["profile"] if prof is None else prof
    return TP.both(d, pack, r, pf, 400.0, 200.0, TP.v("t_base_c"), TMIN if t_l is None else t_l, cfg)


class Series:
    """A 72 hour irradiance series fed to energy_two_pack.sim() hour by hour: sim() asks prof[hh] once per hour in order."""

    def __init__(self, vals):
        self.vals, self.i = vals, 0

    def __getitem__(self, _hh):
        v = self.vals[self.i]
        self.i += 1
        return v


def sim_series(n, pr, vbus, iin, over, vals, start, t_l):
    d, pack, r, cfg = setup(n, pr, vbus, iin, over or {})
    return TP.sim(d, pack, r, Series(vals), 400.0, 200.0, start, TP.v("t_base_c"), t_l, cfg)


def u3_day(vin, ilim, reading):
    """efficiency.py's daily() for U3 as drawn (decision 57), at another bus voltage and input limit."""
    e_st, e_fe, _ = TP.chain(D0)
    cap = min(0.043 / (TP.v("fe_r11_draft_mohm") / 1000.0) * vin, ilim * vin)
    pin = pout = 0.0
    for g in RES0["months"][TP.MONTH]["profile"]:
        p = min(min(TP.EB.panel_w(g, 400, RES0["pr"]), 200.0) * e_st * e_fe, cap)
        if p < 1.0:
            continue
        e = EF.eta("buck", vin, p / vin, 14.5, min(3.968, p * 0.95 / 14.5), EF.CHOSEN_U3, EF.U3["ind"], EF.U3["f"],
                   EF.U3["r_in"], EF.U3["r_chg"], reading)
        pin += p
        pout += p * e
    return pout / pin


def summ(rs):
    return {"ok": TP.verdict(rs), "both": min(r["low_t"] for r in rs), "lid": min(r["low_l"] for r in rs),
            "base": min(r["low_b"] for r in rs), "short": max(r["short"] for r in rs)}


def cell(s):
    return ("MEETS %6.1f" % s["both"]) if s["ok"] else ("NOT MET, %5.1f Wh unserved" % s["short"])


def short(s):
    return ("%6.1f" % s["both"]) if s["ok"] else "   NOT"


def main():
    global D0, PACK0, RES0, TMIN
    D0, PACK0, RES0, t2m = TP.load_model()
    TMIN = round(min(t2m), 2)
    rat = RL.ratios()
    panel = head_equal(PANEL)
    eff_out = head_equal(EFF_OUT)
    grid_out = head_equal(GRID_OUT)
    ser = os.path.join(TOP, SERIES[0])
    if hashlib.sha256(open(ser, "rb").read()).hexdigest() != SERIES[1]:
        refuse(2, "the filed PVGIS series is not the pinned file")
    vr = VR.compute()
    AC, _EA, _TP = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    ga, ta, _pl = ER.september(ER.ANCHOR)
    prof0 = RES0["months"][TP.MONTH]["profile"]
    k_scale = sum(prof0) / sum(ga)
    m = re.search(r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)",
                  " ".join(panel.split()))
    if not m:
        refuse(3, "the hourly-step figures not in reconcile_lid_panel.out")
    floor = max(float(m.group(2)), float(m.group(4)))

    o = []
    P = o.append
    P("THE ENERGY BASIS OF LAYER 3'S DECISIONS L3-OD1, L3-OD2 AND L3-OD4 (energy_basis.py, stream l3plane, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, powered or measured. Energy figures MODELED (a1elec's energy_two_pack.py, pinned, as")
    P("reconcile_lid_panel.py runs it); the bus range from vbus20_range.py (MAKER, NETLIST, INFERRED per term); bands INFERRED")
    P("from the model's grid. AI arithmetic, not a qualified review.")
    P("")

    # 0. reproduction
    bad = 0
    P("0. REPRODUCTION")
    n_ok = n_all = 0
    for n, _w in LIDS:
        for k in "ABC":
            for uk, ua in RL.U3:
                if k == "A" and uk != "nominal":
                    continue
                line = "   %s, U3 %-7s %.1f A, at %.2f C: %s" % (k, uk, ua, TMIN, TP.fmt_run(run(n, rat[k][1], TP.V_BUS20, ua)))
                n_all += 1
                if (line + "\n") in panel:
                    n_ok += 1
                else:
                    bad += 1
    P("   0a. %s: %d of %d rows reproduced byte for byte by this script's runs at %.1f V" % (PANEL, n_ok, n_all, TP.V_BUS20))
    prof_e2 = EF.profile()[0]
    row = re.search(r"U3, chosen FETs, day at E2\s+(0\.\d{3})\s+(0\.\d{3})\s+(0\.\d{3})", eff_out)
    got = [u3_day(TP.V_BUS20, TP.v("u3_iin_draft_a"), r) for r in ("lower", "TI", "upper")]
    ref = [EF.daily(EF.CHOSEN_U3, "E2", prof_e2, r)[0] for r in ("lower", "TI", "upper")]
    same = row and got == ref and ["%.3f" % x for x in got] == list(row.groups())
    bad += 0 if same else 1
    P("   0b. U3's day at E2 (%.1f V, %.1f A): %s, equal to efficiency.py's daily() and to %s section 7 (%s)" % (
        TP.V_BUS20, TP.v("u3_iin_draft_a"), " / ".join("%.4f" % x for x in got), EFF_OUT, "yes" if same else "NO"))
    planes = [(sl, az) for sl in ER.SLOPES for az in ER.ASPECTS if not (sl == 0 and az != 0)]
    PR = {}
    for sl, az in planes:
        G, TA, pl = ER.september(ER.plane_file(sl, az))
        Rp = ER.Ratios(AC, G, TA)
        PR[(sl, az)] = ([k_scale * g for g in G], Rp.typical(), Rp.adverse()[0])
    n_ok = n_all = 0
    for idx, n in ((1, 14), (2, 15)):
        sec = grid_out.split("   %d.2 Every case" % idx, 1)[1].split("   %d.3 Verdict maps" % idx, 1)[0]
        for sl, az in planes:
            pp, rb, rc = PR[(sl, az)]
            cells = [short(summ(run(n, pr0 * r, TP.V_BUS20, 6.1, prof=pp))) for r in (rb, rc)]
            mm = re.search(r"^\s+%d\s+%s\s+(\S+)\s+(\S+)\s" % (sl, re.escape("%+d" % az)), sec, re.M)
            n_all += 1
            if mm and [c.strip() for c in cells] == [mm.group(1), mm.group(2)]:
                n_ok += 1
            else:
                bad += 1
    P("   0c. %s case P (6.1 A, U3B carried, 20.7 V): %d of %d plane cells (both lid options, both array builds) reproduced" % (GRID_OUT, n_ok, n_all))
    ok = True
    for n in (14, 15):
        for start in (6, 18):
            d, pack, r, cfg = setup(n, pr0 * PR[(40, 0)][1], TP.V_BUS20, 6.1, {})
            a = TP.sim(d, pack, r, prof0, 400.0, 200.0, start, TP.v("t_base_c"), TMIN, cfg)
            b = sim_series(n, pr0 * PR[(40, 0)][1], TP.V_BUS20, 6.1, {}, [prof0[(start + h) % 24] for h in range(72)], start, TMIN)
            ok = ok and all(a[k] == b[k] for k in ("ok", "first_stop", "short", "low_b", "low_l", "low_t"))
    bad += 0 if ok else 1
    P("   0d. the mean day fed as a 72 hour series reproduces the mean-day runs exactly (both lids, both starts): %s" % ("yes" if ok else "NO"))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "%d reproduction check(s) failed" % bad)
    P("")

    # 1. definitions
    mj = json.load(open(os.path.join(TOP, D0["pinned"][0]["path"]), encoding="utf-8"))
    dj = json.load(open(os.path.join(TOP, ER.ANCHOR), encoding="utf-8"))
    fits = [lab for lab, _d in AC.renogy_fits()]
    win = AC.vset_window(AC.R8_DRAFT, AC.R9_DRAFT)
    P("1. THE CASES, EXACTLY")
    P("   1a. THE WEATHER: SC-37's reference day, the only weather these runs establish")
    P("       resource: PVGIS 5.2, %s monthly means %d to %d at latitude %.3f, longitude %.3f (%s), the September mean day" % (
        mj["inputs"]["meteo_data"]["radiation_db"], mj["inputs"]["meteo_data"]["year_min"], mj["inputs"]["meteo_data"]["year_max"],
        mj["inputs"]["location"]["latitude"], mj["inputs"]["location"]["longitude"], D0["pinned"][0]["path"]))
    P("       on the %d degree, azimuth %d plane (PVGIS's optimum): %.3f kWh/m2 a day" % (
        mj["inputs"]["plane"]["fixed_inclined_optimal"]["slope"]["value"], mj["inputs"]["plane"]["fixed_inclined_optimal"]["azimuth"]["value"],
        RES0["months"][TP.MONTH]["mean_day_kwh"]))
    P("       shape: PVGIS DRcalc's September mean-day profile, %s %d to %d, hourly, UTC, on that plane (%s: %.3f kWh/m2)," % (
        dj["inputs"]["meteo_data"]["radiation_db"], dj["inputs"]["meteo_data"]["year_min"], dj["inputs"]["meteo_data"]["year_max"],
        ER.ANCHOR, sum(ga) / 1000.0))
    P("       scaled by %.6f to the monthly mean; the same 24 hours repeated for 72 hours; runs from 06 and 18 UTC, a full pack;" % k_scale)
    P("       air %.2f to %.2f C (the profile's T2m), the lid pack at %.2f C (its minimum) and the base pack at +%.0f C for 72 hours." % (
        min(t2m), max(t2m), TMIN, TP.v("t_base_c")))
    P("       Other planes: each plane's own DRcalc mean day (v2/vendor/solar/pvgis-planes/), scaled by the same factor.")
    P("       NO WORSE-WEATHER CASE IS ESTABLISHED BY THESE RUNS: a mean day is not a cloudy day; section 6 is INFORMATIVE only.")
    P("   1b. THE ARRAY BUILD (both on the SAME mean day; the ratio multiplies PVGIS's %.4f, the 40/0 plane's losses kept for every plane)" % pr0)
    P("       TYP, the typical build: fit '%s', the FBIN point at %.2f V, NOCT %.0f C, a %.0f m lead (%.4f ohm loop)." % (
        fits[0], win[1], AC.CAND["REN100"]["noct"], AC.LEAD_M, AC.lead_r()))
    P("       WAB, the WORST ARRAY BUILD (the earlier records' case C, renamed; it is NOT weather): the worst of the three single-diode")
    P("       fits (%s), the FBIN point at the worse end of its window (%.2f or %.2f V: FBIN over temperature and R8, R9 at 1 %%)," % (
        ", ".join(fits), win[0], win[2]))
    P("       cells 10 K above the NOCT model, a %.0f m lead (twice the loop), and the hotter cells' own loss of maximum-power energy" % (2 * AC.LEAD_M))
    P("       (the lower of the model's and the maker's -0.42 %%/K). At 40/0: TYP %.4f, WAB %.4f of the tracked energy." % (PR[(40, 0)][1], PR[(40, 0)][2]))
    P("   1c. THE ELECTRICAL INPUTS")
    band_env, band_m1 = vr["bands"][0], vr["bands"][1]
    v_nom, v_min, v_max = vr["nominal"], band_env[4], band_env[5]
    i_nom = TP.v("u3_iin_draft_a")
    e_nom = u3_day(v_nom, i_nom, "TI")
    e_we = u3_day(v_min, 6.1, "lower")
    e_we6 = u3_day(v_min, 6.0, "lower")
    rd = bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    mk = re.search(r"([\d]+) / ([\d]+) / ([\d]+) mV", TP.PAR["v_ak"][1])
    vak = tuple(float(x) / 1000.0 for x in mk.groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    cases = {
        "NOM": ("nominal: VBUS20 %.3f V (the regulation's nominal), U3 at %.1f A (IIN_HOST's nominal), U3 %.4f (TI's reading at that "
                "bus), U3B %.3f, stage %.2f, front end %.2f, pack charge %.2f, lid loops %.3f / %.3f ohm, V(AK) %.0f mV" % (
                    v_nom, i_nom, e_nom, TP.v("eta_u3b"), ch[0]["eta"], ch[1]["eta"], ce["value"], TP.v("r_lid_dsg"), TP.v("r_lid_chg"), vak[1] * 1000),
                v_nom, i_nom, {"eta_u3": e_nom}),
        "WE": ("the established worst electrical inputs: VBUS20 %.3f V (the envelope's minimum, vbus20_range.out 6), U3 at 6.1 A (its "
               "minimum), U3 %.4f (the makers' maxima at that bus), U3B %.3f (its lower bracket); the other losses nominal" % (
                   v_min, e_we, TP.v("eta_u3b_lo")),
               v_min, 6.1, {"eta_u3": e_we, "eta_b": TP.v("eta_u3b_lo")}),
        "WE60": ("WE with U3 at the 6.0 A bracket (U3 %.4f)" % e_we6, v_min, 6.0, {"eta_u3": e_we6, "eta_b": TP.v("eta_u3b_lo")}),
        "WA": ("every bracket unfavourable at once: WE60 plus stage %.2f, front end %.2f, pack charge %.2f, lid loops %.3f / %.3f ohm, "
               "V(AK) %.0f mV" % (ch[0]["low"], ch[1]["low"], ce["low"], rd[1], rc_[1], vak[2] * 1000),
               v_min, 6.0, {"eta_u3": e_we6, "eta_b": TP.v("eta_u3b_lo"), "eta_st": ch[0]["low"], "eta_fe": ch[1]["low"],
                            "chg_eta": ce["low"], "r_dsg": rd[1], "r_chg": rc_[1], "v_ak": vak[2]}),
        "GEN": ("board A AS GENERATED: R11 10 mOhm, so the front end limits at %.2f A minimum (vbus20_range.out 7) and U3's limit is "
                "set under it at %.2f A (energy_two_pack entry E1); bus nominal, U3 %.4f (TI's reading there), the rest nominal" % (
                    vr["cc"]["gen"][0], TP.v("u3_iin_e1_a"), u3_day(v_nom, TP.v("u3_iin_e1_a"), "TI")),
                v_nom, TP.v("u3_iin_e1_a"), {"eta_u3": u3_day(v_nom, TP.v("u3_iin_e1_a"), "TI"), "fe_i": vr["cc"]["gen"][0]}),
        "M207": ("for comparison, the model as published: %.1f V, 6.1 A, U3 %.3f and U3B %.3f carried (plane_grid.out case P)" % (
                     TP.V_BUS20, ch[2]["eta"], TP.v("eta_u3b")), TP.V_BUS20, 6.1, {}),
        "SC76": ("for comparison, SC-76's basis: %.2f V, 6.1 A, U3 and U3B carried (plane_grid.out case V19)" % SC76_V, SC76_V, 6.1, {}),
    }
    order = ("NOM", "WE", "WE60", "WA", "GEN", "M207", "SC76")
    for k in order:
        P("       %-5s %s" % (k, cases[k][0]))
    P("       Common to every case: 400 Wp (four Renogy RNG-100DB-H in 2S2P) into a 200 W stage window, the drafted entry (R11")
    P("       6.2 mOhm: the front end limits at 6.94 A minimum, above U3; as generated R11 is 10 mOhm and the bus cannot carry U3's")
    P("       limit, vbus20_range.out 7), U3B at code 62 (%.3f A), PS-IDLE-SPEC %.1f W at the pack terminals, the cells aged to 80" % (TP.v("chg_a_lid"), TP.LOAD))
    P("       percent, the 3.00 V line with the 5 percent reserve, the charge and discharge split by capacity.")
    P("")

    # 2. U3's efficiency against the bus
    P("2. U3'S EFFICIENCY AGAINST THE BUS AND ITS LIMIT (efficiency.py's method, the reference day at 40/0, the drafted entry)")
    P("   %-44s %8s %8s %8s   %s" % ("bus, limit", "lower", "TI", "upper", "power into U3 at the limit"))
    for lab, v in (("the envelope's minimum", v_min), ("the reference day's minimum", band_m1[4]), ("SC-76", SC76_V),
                   ("nominal", v_nom), ("the model's", TP.V_BUS20), ("the envelope's maximum", v_max)):
        for ilim in (6.0, 6.1, 6.2):
            P("   %-44s %8.4f %8.4f %8.4f   %6.1f W" % ("%s %.3f V, %.1f A" % (lab, v, ilim), u3_day(v, ilim, "lower"),
                                                    u3_day(v, ilim, "TI"), u3_day(v, ilim, "upper"), v * ilim))
    P("   At a lower bus U3 bucks a smaller ratio and loses slightly less; the power it may take falls in proportion to the bus.")
    P("")

    # 3. sensitivity at 40/0
    pp40, rb40, rc40 = PR[(40, 0)]
    nom = cases["NOM"]
    axes = [("VBUS20 (and U3's TI reading at it)", [("%.3f V" % v_min, dict(vbus=v_min, eta_u3=u3_day(v_min, i_nom, "TI"))),
                                                    ("%.3f V" % v_max, dict(vbus=v_max, eta_u3=u3_day(v_max, i_nom, "TI")))]),
            ("U3's input limit (and its TI reading)", [("6.0 A", dict(iin=6.0, eta_u3=u3_day(v_nom, 6.0, "TI"))),
                                                      ("6.1 A", dict(iin=6.1, eta_u3=u3_day(v_nom, 6.1, "TI")))]),
            ("U3's efficiency", [("lower %.4f" % u3_day(v_nom, i_nom, "lower"), dict(eta_u3=u3_day(v_nom, i_nom, "lower"))),
                                 ("upper %.4f" % u3_day(v_nom, i_nom, "upper"), dict(eta_u3=u3_day(v_nom, i_nom, "upper")))]),
            ("U3B's efficiency", [("%.3f" % TP.v("eta_u3b_lo"), dict(eta_b=TP.v("eta_u3b_lo"))), ("%.3f" % TP.v("eta_u3b_hi"), dict(eta_b=TP.v("eta_u3b_hi")))]),
            ("the stage's efficiency", [("%.2f" % ch[0]["low"], dict(eta_st=ch[0]["low"])), ("%.2f" % ch[0]["high"], dict(eta_st=ch[0]["high"]))]),
            ("the front end's efficiency", [("%.2f" % ch[1]["low"], dict(eta_fe=ch[1]["low"])), ("%.2f" % ch[1]["high"], dict(eta_fe=ch[1]["high"]))]),
            ("the pack's charge efficiency", [("%.2f" % ce["low"], dict(chg_eta=ce["low"])), ("%.2f" % ce["high"], dict(chg_eta=ce["high"]))]),
            ("the lid's discharge loop", [("%.3f ohm" % rd[1], dict(r_dsg=rd[1])), ("%.3f ohm" % rd[0], dict(r_dsg=rd[0]))]),
            ("the lid's charge loop", [("%.3f ohm" % rc_[1], dict(r_chg=rc_[1])), ("%.3f ohm" % rc_[0], dict(r_chg=rc_[0]))]),
            ("the ideal diode's V(AK)", [("%.0f mV" % (vak[2] * 1000), dict(v_ak=vak[2])), ("%.0f mV" % (vak[0] * 1000), dict(v_ak=vak[0]))]),
            ("the array build", [("WAB", dict(build="WAB")), ("TYP", dict(build="TYP"))])]

    def run_at(n, extra, build="TYP", plane=(40, 0)):
        pp, rb, rc = PR[plane]
        args = dict(vbus=nom[1], iin=nom[2], **nom[3])
        args.update(extra)
        b = args.pop("build", build)
        vbus, iin = args.pop("vbus"), args.pop("iin")
        return summ(run(n, pr0 * (rb if b == "TYP" else rc), vbus, iin, over=args, prof=pp))

    P("3. SENSITIVITY ON THE REFERENCE PLANE (40 degrees, south), one input at a time from NOM with the TYP build; the lowest")
    P("   store of both packs in Wh (or the energy left unserved), and its change from NOM")
    for n, what in LIDS:
        base = run_at(n, {})
        P("   %s: NOM %s" % (what, cell(base)))
        rank = []
        for name, ends in axes:
            res = [(lab, run_at(n, ex)) for lab, ex in ends]
            metric = [(s["both"] if s["ok"] else -s["short"]) for _l, s in res]
            b0 = base["both"] if base["ok"] else -base["short"]
            P("      %-38s %-14s %-30s %+7.1f   %-14s %-30s %+7.1f" % (name, res[0][0], cell(res[0][1]), metric[0] - b0,
                                                                  res[1][0], cell(res[1][1]), metric[1] - b0))
            rank.append((metric[0] - b0, name))
        rank.sort()
        P("      ranked by the unfavourable end: %s" % "; ".join("%s %+.1f" % (nm, dv) for dv, nm in rank[:5]))
    P("   (a NOT MET row's metric is minus the unserved energy, so the change counts across the verdict)")
    P("")

    # 3b. the power U3 may take
    P("3b. THE LOWEST STORE AGAINST THE POWER U3 MAY TAKE (the bus times U3's limit), every other input at NOM, on 40/0: the")
    P("    electrical inputs VBUS20 and IIN_HOST act only through this product (and U3's efficiency, section 2)")
    P("   %-10s %s" % ("into U3", "  ".join("%-27s" % ("%s %s" % (dict(LIDS)[n].split(",")[0], b)) for n in (14, 15) for b in ("TYP", "WAB"))))
    for pw in range(108, 132, 2):
        cells = []
        for n in (14, 15):
            for b in ("TYP", "WAB"):
                s_ = summ(run(n, pr0 * (rb40 if b == "TYP" else rc40), v_nom, pw / v_nom, over={"eta_u3": e_nom}, prof=pp40))
                cells.append("%-27s" % cell(s_))
        P("   %6.1f W  %s" % (pw, "  ".join(cells)))
    P("   (the bus's established range %.3f to %.3f V is %.1f to %.1f W at 6.1 A and %.1f to %.1f W at 6.0 A; nominal %.1f W at %.1f A)" % (
        v_min, v_max, v_min * 6.1, v_max * 6.1, v_min * 6.0, v_max * 6.0, v_nom * i_nom, i_nom))
    P("")

    # 4. combined cases at 40/0
    P("4. THE COMBINED CASES ON THE REFERENCE PLANE (40/0): verdict, lowest store of both packs / lid / base in Wh, unserved")
    P("   %-44s %-5s %-44s %-44s" % ("lid option", "case", "TYP", "WAB"))
    combos = {}
    for n, what in LIDS:
        for k in order:
            c = cases[k]
            row = []
            for b in ("TYP", "WAB"):
                s = summ(run(n, pr0 * (rb40 if b == "TYP" else rc40), c[1], c[2], over=c[3], prof=pp40))
                combos[(n, k, b)] = s
                row.append(("MEETS  both %6.1f, lid %5.1f, base %5.1f" % (s["both"], s["lid"], s["base"])) if s["ok"]
                           else "NOT MET, unserved %6.1f Wh" % s["short"])
            P("   %-44s %-5s %-44s %-44s" % (what.split(",")[0], k, row[0], row[1]))
    P("")

    # 5. the grid at the combined cases
    P("5. THE PLANES AT NOM, WE, WE60 AND WA (each plane's own mean day and ratios); a point COUNTS when TYP and WAB both meet with")
    P("   every lowest store above the floor %.1f Wh (reconcile_lid_panel.out's NOTES: the model's hourly-step sensitivity)" % floor)
    grid = {}
    for n in (14, 15):
        for k in ("NOM", "WE", "WE60", "WA"):
            c = cases[k]
            for pl in planes:
                pp, rb, rc = PR[pl]
                grid[(n, k, pl)] = tuple(summ(run(n, pr0 * r, c[1], c[2], over=c[3], prof=pp)) for r in (rb, rc))

    def counts(n, k, sl, az):
        a0 = 0 if sl == 0 else az
        return all(s["ok"] and s["both"] > floor for s in grid[(n, k, (sl, a0))])

    def rects(n, k):
        rr = []
        S, A = ER.SLOPES, ER.ASPECTS
        for i in range(len(S)):
            for j in range(i, len(S)):
                for a in range(len(A)):
                    for b in range(a, len(A)):
                        if all(counts(n, k, S[s], A[t]) for s in range(i, j + 1) for t in range(a, b + 1)):
                            rr.append((i, j, a, b))
        mx = [r for r in rr if not any(q != r and q[0] <= r[0] and q[1] >= r[1] and q[2] <= r[2] and q[3] >= r[3] for q in rr)]
        mx.sort(key=lambda r: (-(r[1] - r[0] + 1) * (r[3] - r[2] + 1), r))
        return mx

    def least(n, k, pts):
        return min(((s["both"], sl, az, b) for sl, az in pts for s, b in zip(grid[(n, k, (sl, 0 if sl == 0 else az))], ("TYP", "WAB"))),
                   key=lambda x: x[0])
    bands = {}
    for n in (14, 15):
        what = dict(LIDS)[n]
        P("   %s" % what)
        for k in ("NOM", "WE", "WE60", "WA"):
            P("      case %s, maps (BW both builds count, T the TYP build only meets, - neither counts)" % k)
            P("         %6s %s" % ("slope", "".join("%5s" % ("%+d" % a) for a in ER.ASPECTS)))
            for sl in ER.SLOPES:
                cells = []
                for az in ER.ASPECTS:
                    if sl == 0 and az != 0:
                        cells.append("%5s" % ".")
                        continue
                    t, w = grid[(n, k, (sl, az))]
                    cells.append("%5s" % ("BW" if counts(n, k, sl, az) else ("T" if t["ok"] else "-")))
                P("         %6d %s" % (sl, "".join(cells)))
            mx = rects(n, k)
            bands[(n, k)] = mx
            for r in mx[:4]:
                pts = [(ER.SLOPES[s], ER.ASPECTS[t]) for s in range(r[0], r[1] + 1) for t in range(r[2], r[3] + 1)]
                lw = least(n, k, pts)
                P("         band: slope %2d to %2d, azimuth %+3d to %+3d (%2d points); least %5.1f Wh at %d/%+d (%s)" % (
                    ER.SLOPES[r[0]], ER.SLOPES[r[1]], ER.ASPECTS[r[2]], ER.ASPECTS[r[3]], len(pts), lw[0], lw[1], lw[2], lw[3]))
            if not mx:
                P("         band: none (no grid point counts)")
            for x in (0, 15, 30):
                a, b = ER.ASPECTS.index(-x), ER.ASPECTS.index(x)
                runs, cur = [], None
                for s in range(len(ER.SLOPES)):
                    okk = all(counts(n, k, ER.SLOPES[s], ER.ASPECTS[t]) for t in range(a, b + 1))
                    if okk and cur is None:
                        cur = s
                    if not okk and cur is not None:
                        runs.append((cur, s - 1))
                        cur = None
                if cur is not None:
                    runs.append((cur, len(ER.SLOPES) - 1))
                P("         within %2d of south: %s" % (x, "; ".join("slope %d to %d" % (ER.SLOPES[p], ER.SLOPES[q]) for p, q in runs) or "no slope"))
    P("")

    # 5b. the proposed bands' edges
    P("5b. THE EDGES OF EACH OPTION'S WE BAND (the largest rectangle of case WE), lowest store TYP / WAB in Wh per case")
    for n in (14, 15):
        mx = bands[(n, "WE")]
        if not mx:
            P("   %s: no WE band" % dict(LIDS)[n])
            continue
        r = mx[0]
        s0, s1, a0, a1 = ER.SLOPES[r[0]], ER.SLOPES[r[1]], ER.ASPECTS[r[2]], ER.ASPECTS[r[3]]
        P("   %s: WE band slope %d to %d, azimuth %+d to %+d" % (dict(LIDS)[n], s0, s1, a0, a1))
        edge = [(sl, az) for sl in ER.SLOPES for az in ER.ASPECTS if s0 <= sl <= s1 and a0 <= az <= a1 and (sl in (s0, s1) or az in (a0, a1))]
        for k in ("NOM", "WE", "WE60", "WA"):
            P("      %-5s %s" % (k, "; ".join("%d/%+d %s/%s" % (sl, az, short(grid[(n, k, (sl, az))][0]).strip(),
                                                              short(grid[(n, k, (sl, az))][1]).strip()) for sl, az in edge)))
    P("")

    # 6. informative weather
    P("6. INFORMATIVE ONLY, NOT A REQUIREMENT CASE: M1 IN SEPTEMBER'S ACTUAL WEATHER, 2005 TO 2020, AT 40/0")
    sj = json.load(open(ser, encoding="utf-8"))
    rows = sj["outputs"]["hourly"]
    years = sorted({r_["time"][:4] for r_ in rows})
    by_year = {y: [r_ for r_ in rows if r_["time"][:4] == y] for y in years}
    mean_day = [sum(r_["G(i)"] for r_ in rows if int(r_["time"][9:11]) == h) / (len(rows) / 24) for h in range(24)]
    P("   data: %s (fetched by fetch_pvgis_series.py: PVGIS 5.2 seriescalc, %s %s to %s, latitude %.3f, longitude %.3f, slope %d," % (
        SERIES[0], sj["inputs"]["meteo_data"]["radiation_db"], years[0], years[-1], sj["inputs"]["location"]["latitude"],
        sj["inputs"]["location"]["longitude"], sj["inputs"]["mounting_system"]["fixed"]["slope"]["value"]))
    P("   azimuth %d, hourly averages, UTC): its mean September day is %.3f kWh/m2, the DRcalc profile's %.3f (hour by hour equal: %s)." % (
        sj["inputs"]["mounting_system"]["fixed"]["azimuth"]["value"], sum(mean_day) / 1000.0, sum(ga) / 1000.0,
        "yes" if max(abs(mean_day[h] - ga[h]) for h in range(24)) < 0.5 else "NO"))
    P("   Method (one site, one plane, one method): every 72 hour window starting at 06 or 18 UTC on 1 to 27 September of each year")
    P("   (%d windows); the series as PVGIS gives it (NOT scaled to the 2015 to 2020 monthly mean); each calendar day's own TYP or" % (len(years) * 27 * 2))
    P("   WAB ratio folded into its hours; the lid pack at the window's own minimum air; a full pack at the start; the rest as 1.")
    dayrat = {}
    for y in years:
        for dd in range(30):
            G = [r_["G(i)"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]]
            TA = [r_["T2m"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]]
            if sum(G) <= 0.0:
                dayrat[(y, dd)] = (1.0, 1.0)
                continue
            Rp = ER.Ratios(AC, G, TA)
            dayrat[(y, dd)] = (Rp.typical(), Rp.adverse()[0])
    wins = []
    for y in years:
        yr = by_year[y]
        for dd in range(27):
            for st in (6, 18):
                i0 = dd * 24 + st
                seg = yr[i0:i0 + 72]
                wins.append((y, dd + 1, st, seg, [(i0 + i) // 24 for i in range(72)]))
    res = {}
    wcases = (("NOM", "TYP"), ("WE", "TYP"), ("WE", "WAB"))
    for n in (14, 15):
        for k, b in wcases:
            c = cases[k]
            out = []
            for y, day, st, seg, days in wins:
                bi = 0 if b == "TYP" else 1
                vals = [seg[i]["G(i)"] * dayrat[(y, days[i])][bi] for i in range(72)]
                t_l = round(min(r_["T2m"] for r_ in seg), 2)
                s = sim_series(n, pr0, c[1], c[2], c[3], vals, st, t_l)
                out.append((sum(r_["G(i)"] for r_ in seg) / 1000.0, y, day, st, t_l, s))
            res[(n, k, b)] = out
    ref72 = 3 * RES0["months"][TP.MONTH]["mean_day_kwh"]
    irr = sorted(w[0] for w in res[(14, "NOM", "TYP")])
    P("   72 hour irradiation over the windows: lowest %.2f, 10th percentile %.2f, median %.2f kWh/m2; the reference day x 3: %.2f" % (
        irr[0], irr[len(irr) // 10], irr[len(irr) // 2], ref72))
    P("   %-44s %-9s %-22s %-40s %-40s %s" % ("lid option", "case", "windows meeting M1", "the darkest window", "the 10th percentile window",
                                            "meets from / fails up to (kWh/m2)"))
    for n in (14, 15):
        for k, b in wcases:
            out = sorted(res[(n, k, b)], key=lambda w: (w[0], w[1], w[2], w[3]))
            nm = sum(1 for w in out if w[5]["ok"])
            dk, p10 = out[0], out[len(out) // 10]
            meets = [w[0] for w in out if w[5]["ok"]]
            fails = [w[0] for w in out if not w[5]["ok"]]

            def wtxt(w):
                return "%s-09-%02d %02dh %.2f kWh/m2, %s" % (w[1], w[2], w[3], w[0], ("MEETS %.1f" % w[5]["low_t"]) if w[5]["ok"]
                                                              else "NOT MET %.0f Wh" % w[5]["short"])
            P("   %-44s %-9s %4d of %4d (%5.1f %%)   %-40s %-40s %s / %s" % (
                dict(LIDS)[n].split(",")[0], "%s %s" % (k, b), nm, len(out), 100.0 * nm / len(out), wtxt(dk), wtxt(p10),
                ("%.2f" % min(meets)) if meets else "none", ("%.2f" % max(fails)) if fails else "none"))
    P("   4S9P is not run here: it does not meet M1 on the mean day in any case (section 4).")
    P("   Limits of this case: PVGIS's %.4f is an average loss applied to single days; one plane; the base at +%.0f C; a full pack" % (pr0, TP.v("t_base_c")))
    P("   at every window's start (no carry-over from the days before); SARAH2's hourly averages as given.")
    P("")
    P("END. Each line is the model's arithmetic; nothing is measured.")
    sys.stdout.write("\n".join(o) + "\n")
    TP.NP_L = 12
    TP.NP_T = TP.NP_B + 12
    return 0


if __name__ == "__main__":
    sys.exit(main())
