#!/usr/bin/env python3
"""energy_basis.py (second issue): the energy basis of the owner's layer 3 decisions L3-OD1, L3-OD2 and L3-OD4 (stream
l3plane, MESHSAT-1357, 30 September 2026): M1's energy balance with the charge bus at its established range, what every
input the model carries does to it at the proposed basis, what each undocumented efficiency must reach, exact case
definitions, each pack's own lowest store, and an INFORMATIVE worse-weather case.

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured. Every energy figure is MODELED; the bus range is
vbus20_range.py's (MAKER, NETLIST, INFERRED per term); every band and threshold is INFERRED from the model's grid.

Second issue, after the independent check CHECK-1 of 6a283b25 (accepted: no):
  * B1: the one at a time sensitivity is taken from WE (both array builds) and from NOM with the worst array build; the
    first issue's table from NOM with the typical build sat where the packs fill before dusk and hid every charge-side loss;
    it is kept, marked so;
  * B2: WE is restated to hold only figures with a maker's document behind them at their worst, plus the lid path's
    ESTIMATE resistances at their bracket's worse end and the lid's standby drain; the three efficiencies no maker document
    gives for this circuit (board E's stage, board A's front end, the pack's charge efficiency) stay at their declared
    values and every WE result is labelled CONDITIONAL on them; the minimum each must reach, per lid option and band point,
    is printed beside the makers' own curve readings (curve_readings.out) and the cell sheet's resistive bound;
  * minors: each pack's lowest store is tested as well as the combined one (two pass lines, COMBINED and EACH PACK); the
    knee is stated per build; the bus's brackets (the divider's rise, the resistors' endurance) are run; labels.

The model is reconcile_lid_panel.py's: a1elec's energy_two_pack.py (pinned) with the lid's parallel count, the ratio and
U3's input limit set, the rest as carried; this script builds each run as reconcile_lid_panel.run() does, with the bus,
the limit and the named inputs explicit. Before any result it proves (exit 4 otherwise): 0a the runs reproduce every row of
reconcile_lid_panel.out byte for byte at 20.7 V; 0b the U3 figure reproduces efficiency.py's day at E2 exactly; 0c the
plane runs reproduce plane_grid.out's case P on all 50 planes for both lid options; 0d a 72 hour series fed hour by hour
reproduces the mean-day run; 0e the first issue's WE is reproduced against its committed rows (commit 6a283b25).

Third issue (CHECK-2 of ec415c09, minor 1): the cell's resistive bound for the base pack takes the kit's whole parallel
count for the discharge current (it took 12 cells); the WE-MKR reading of weather_basis.py follows it.

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
        "l3plane/vbus20_range.py": "f4eabc3536334604b007acc34c4ac78ac218a7cfb294f4352a9baaaeff78ff01"}
SERIES = ("v2/vendor/solar/pvgis-series/pvgis-leiden-seriescalc-2005-2020-september-slope40-aspect0.json",
          "c5f0363a9d97b6db6e5ef10fa89904fd55e30aca67007760b9d77caa3b0debd7")
CELL = "v2/vendor/battery/samsung-35e-conrad.pdf"      # pinned by energy_inputs.yaml; checked below against that pin
FIRST_ISSUE = "6a283b25"                               # the first issue of this script's output, for check 0e
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
CURVES = "v2/docs/records/l3plane/curve_readings.out"
SELF_OUT = "v2/docs/records/l3plane/energy_basis.out"
SC76_V = 19.08          # SC-76's figure (fnd/l3r2), stream s120's DC band minimum: run for comparison only
LIDS = ((9, "4S9P, both lid functions kept (4S15P in all)"), (14, "4S14P, the tablet bracket out (4S20P in all)"),
        (15, "4S15P, the QMX HF set out (4S21P in all)"))
D0 = PACK0 = RES0 = None
TMIN = None
FLOOR = None


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
    over = over or {}
    d, pack, r, cfg = setup(n, pr, vbus, iin, over)
    pf = RES0["months"][TP.MONTH]["profile"] if prof is None else prof
    load0 = TP.LOAD
    TP.LOAD = load0 + over.get("drain_w", 0.0)      # the lid path's standby drain as load at the pack terminals
    try:
        return TP.both(d, pack, r, pf, 400.0, 200.0, TP.v("t_base_c"), TMIN if t_l is None else t_l, cfg)
    finally:
        TP.LOAD = load0


class Series:
    """A 72 hour irradiance series fed to energy_two_pack.sim() hour by hour: sim() asks prof[hh] once per hour in order."""

    def __init__(self, vals):
        self.vals, self.i = vals, 0

    def __getitem__(self, _hh):
        v = self.vals[self.i]
        self.i += 1
        return v


def sim_series(n, pr, vbus, iin, over, vals, start, t_l):
    over = over or {}
    d, pack, r, cfg = setup(n, pr, vbus, iin, over)
    load0 = TP.LOAD
    TP.LOAD = load0 + over.get("drain_w", 0.0)
    try:
        return TP.sim(d, pack, r, Series(vals), 400.0, 200.0, start, TP.v("t_base_c"), t_l, cfg)
    finally:
        TP.LOAD = load0


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


def comb(s):
    return s["ok"] and s["both"] > FLOOR


def each(s):
    return s["ok"] and s["base"] > FLOOR and s["lid"] > FLOOR


def cell(s):
    return ("MEETS %6.1f" % s["both"]) if s["ok"] else ("NOT MET, %5.1f Wh unserved" % s["short"])


def packs(s):
    return ("%6.1f (base %5.1f, lid %5.1f)" % (s["both"], s["base"], s["lid"])) if s["ok"] else ("NOT MET, %5.1f unserved" % s["short"])


def short(s):
    return ("%6.1f" % s["both"]) if s["ok"] else "   NOT"


def metric(s):
    return s["both"] if s["ok"] else -s["short"]


def main():
    global D0, PACK0, RES0, TMIN, FLOOR
    D0, PACK0, RES0, t2m = TP.load_model()
    TMIN = round(min(t2m), 2)
    rat = RL.ratios()
    panel = head_equal(PANEL)
    eff_out = head_equal(EFF_OUT)
    grid_out = head_equal(GRID_OUT)
    curves = head_equal(CURVES)
    first = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (FIRST_ISSUE, SELF_OUT)], capture_output=True, text=True).stdout
    if "THE ENERGY BASIS OF LAYER 3" not in first:
        refuse(3, "the first issue's output is not at %s" % FIRST_ISSUE)
    ser = os.path.join(TOP, SERIES[0])
    if hashlib.sha256(open(ser, "rb").read()).hexdigest() != SERIES[1]:
        refuse(2, "the filed PVGIS series is not the pinned file")
    cell_pin = [p_["sha256"] for p_ in D0["pinned"] if p_["path"] == CELL]
    if not cell_pin or hashlib.sha256(open(os.path.join(TOP, CELL), "rb").read()).hexdigest() != cell_pin[0]:
        refuse(2, "the cell sheet is not energy_inputs.yaml's pinned file")
    vr = VR.compute()
    AC, _EA, _TP = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    ga, ta, _pl = ER.september(ER.ANCHOR)
    prof0 = RES0["months"][TP.MONTH]["profile"]
    k_scale = sum(prof0) / sum(ga)
    notes = " ".join(panel.split())
    m = re.search(r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", notes)
    md = re.search(r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", notes)
    if not (m and md):
        refuse(3, "the hourly-step figures or the standby drain not in reconcile_lid_panel.out")
    FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_wh = float(md.group(2))
    drain_w = drain_wh / D0["mission"]["hours"]

    o = []
    P = o.append
    P("THE ENERGY BASIS OF LAYER 3'S DECISIONS L3-OD1, L3-OD2 AND L3-OD4 (energy_basis.py second issue, stream l3plane,")
    P("MESHSAT-1357). PROTOTYPE DESIGN: nothing built, powered or measured. Energy figures MODELED (a1elec's energy_two_pack.py,")
    P("pinned, as reconcile_lid_panel.py runs it); the bus range from vbus20_range.py (MAKER, NETLIST, INFERRED per term); bands")
    P("and thresholds INFERRED from the model's grid. The author's analysis, AI arithmetic; not a qualified review, and not")
    P("the independent check.")
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

    # the cases
    band_env, band_m1 = vr["bands"][0], vr["bands"][1]
    v_nom, v_min, v_max = vr["nominal"], band_env[4], band_env[5]
    v_rise = vr["brackets"][0][2][0]
    v_life = vr["brackets"][1][2][0]
    i_nom = TP.v("u3_iin_draft_a")
    rd = bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    mk = re.search(r"([\d]+) / ([\d]+) / ([\d]+) mV", TP.PAR["v_ak"][1])
    vak = tuple(float(x) / 1000.0 for x in mk.groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    e_nom = u3_day(v_nom, i_nom, "TI")

    def we_over(v, i, extra=None):
        x = {"eta_u3": u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    cases = {
        "NOM": ("nominal: VBUS20 %.3f V, U3's limit %.1f A, U3 %.4f (TI's reading at that bus, INFERRED), U3B %.3f (INFERRED), stage "
                "%.2f and front end %.2f (DECLARED), pack charge %.2f (INFERRED, no document), lid loops %.3f / %.3f Ohm (ESTIMATE), "
                "V(AK) %.0f mV (MAKER typical), no standby drain" % (v_nom, i_nom, e_nom, TP.v("eta_u3b"), ch[0]["eta"], ch[1]["eta"],
                                                                     ce["value"], TP.v("r_lid_dsg"), TP.v("r_lid_chg"), vak[1] * 1000),
                v_nom, i_nom, {"eta_u3": e_nom}),
        "WE": ("RESTATED: every term with a maker's document at its worst: VBUS20 %.3f V (the steady-state range's minimum, "
               "vbus20_range.out 6), U3's limit 6.1 A (INFERRED minimum), U3 %.4f (the makers' maxima at that bus, INFERRED by TI's "
               "method), U3B %.3f (INFERRED, lower bracket), V(AK) %.0f mV (MAKER maximum); the lid loops at their ESTIMATE's worse "
               "end %.3f / %.3f Ohm; the lid's standby drain %.1f Wh over 72 h added to the load. CONDITIONAL ON three undocumented "
               "efficiencies held at their declared values: stage %.2f, front end %.2f, pack charge %.2f" % (
                   v_min, u3_day(v_min, 6.1, "lower"), TP.v("eta_u3b_lo"), vak[2] * 1000, rd[1], rc_[1], drain_wh,
                   ch[0]["eta"], ch[1]["eta"], ce["value"]),
               v_min, 6.1, we_over(v_min, 6.1)),
        "WE60": ("WE with U3's limit at the 6.0 A bracket", v_min, 6.0, we_over(v_min, 6.0)),
        "WEL": ("WE with the bus at its endurance bracket %.3f V (the resistors at the makers' 1000 h limits; a bound)" % v_life,
                v_life, 6.1, we_over(v_life, 6.1)),
        "WA": ("WE60 with the three undocumented efficiencies at their brackets' lower ends: stage %.2f, front end %.2f, pack "
               "charge %.2f" % (ch[0]["low"], ch[1]["low"], ce["low"]),
               v_min, 6.0, we_over(v_min, 6.0, {"eta_st": ch[0]["low"], "eta_fe": ch[1]["low"], "chg_eta": ce["low"]})),
        "WE1": ("the FIRST issue's WE (V(AK), the lid loops and the drain nominal), for continuity with CHECK-1's figures",
                v_min, 6.1, {"eta_u3": u3_day(v_min, 6.1, "lower"), "eta_b": TP.v("eta_u3b_lo")}),
        "GEN": ("board A AS GENERATED: R11 10 mOhm, the front end's limit %.2f A minimum, U3's limit set under it at %.2f A (entry E1; "
                "its %.2f A maximum is 50 mA under the front end's minimum); bus nominal; U3 %.4f; the rest nominal" % (
                    vr["cc"]["gen"][0], TP.v("u3_iin_e1_a"), TP.v("u3_iin_e1_a") + 0.1, u3_day(v_nom, TP.v("u3_iin_e1_a"), "TI")),
                v_nom, TP.v("u3_iin_e1_a"), {"eta_u3": u3_day(v_nom, TP.v("u3_iin_e1_a"), "TI"), "fe_i": vr["cc"]["gen"][0]}),
        "M207": ("for comparison, the model as published: %.1f V, 6.1 A, U3 %.3f and U3B %.3f carried (plane_grid.out case P)" % (
                     TP.V_BUS20, ch[2]["eta"], TP.v("eta_u3b")), TP.V_BUS20, 6.1, {}),
        "SC76": ("for comparison, SC-76's basis: %.2f V, 6.1 A, U3 and U3B carried (plane_grid.out case V19)" % SC76_V, SC76_V, 6.1, {}),
    }
    order = ("NOM", "WE", "WE60", "WEL", "WA", "WE1", "GEN", "M207", "SC76")
    pp40, rb40, rc40 = PR[(40, 0)]

    def at(n, k, b="TYP", plane=(40, 0), extra=None, vbus=None, iin=None):
        pp, rb, rc = PR[plane]
        c = cases[k]
        ov = dict(c[3])
        ov.update(extra or {})
        return summ(run(n, pr0 * (rb if b == "TYP" else rc), vbus or c[1], iin or c[2], over=ov, prof=pp))
    ok = True
    for n, _w in LIDS:
        for b in ("TYP", "WAB"):
            s = at(n, "WE1", b)
            ln = ("MEETS  both %6.1f, lid %5.1f, base %5.1f" % (s["both"], s["lid"], s["base"])) if s["ok"] else "NOT MET, unserved %6.1f Wh" % s["short"]
            ok = ok and ln in first
    bad += 0 if ok else 1
    P("   0e. the first issue's WE (case WE1 here) reproduces its six rows of %s at %s: %s" % (SELF_OUT, FIRST_ISSUE, "yes" if ok else "NO"))
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
    P("       NO WORSE-WEATHER CASE IS ESTABLISHED BY THESE RUNS: a mean day is not a cloudy day; section 7 is INFORMATIVE only.")
    P("   1b. THE ARRAY BUILD (both on the SAME mean day; the ratio multiplies PVGIS's %.4f, the 40/0 plane's losses kept for every plane)" % pr0)
    P("       TYP, the typical build: fit '%s', the FBIN point at %.2f V, NOCT %.0f C, a %.0f m lead (%.4f ohm loop)." % (
        fits[0], win[1], AC.CAND["REN100"]["noct"], AC.LEAD_M, AC.lead_r()))
    P("       WAB, the WORST ARRAY BUILD (the earlier records' case C, renamed; it is NOT weather): the worst of the three single-diode")
    P("       fits (%s), the FBIN point at the worse end of its window (%.2f or %.2f V: FBIN over temperature and R8, R9 at 1 %%)," % (
        ", ".join(fits), win[0], win[2]))
    P("       cells 10 K above the NOCT model, a %.0f m lead (twice the loop), and the hotter cells' own loss of maximum-power energy" % (2 * AC.LEAD_M))
    P("       (the lower of the model's and the maker's -0.42 %%/K). At 40/0: TYP %.4f, WAB %.4f of the tracked energy." % (PR[(40, 0)][1], PR[(40, 0)][2]))
    P("   1c. THE ELECTRICAL AND LOSS INPUTS (basis: MAKER, NETLIST, INFERRED from a maker's figures, DECLARED, ESTIMATE)")
    for k in order:
        P("       %-5s %s" % (k, cases[k][0]))
    P("       Common to every case: 400 Wp (four Renogy RNG-100DB-H in 2S2P) into a 200 W stage window, the drafted entry (R11")
    P("       6.2 mOhm: the front end limits at 6.94 A minimum, above U3; GEN excepted), U3B at code 62 (%.3f A), PS-IDLE-SPEC %.1f W" % (TP.v("chg_a_lid"), TP.LOAD))
    P("       at the pack terminals, the cells aged to 80 percent, the 3.00 V line with the 5 percent reserve, the charge and discharge")
    P("       split by capacity. The standby drain is carried as load at the pack terminals, split by capacity like the rest.")
    P("   1d. THE PASS LINES: M1 is MET when neither start stops the kit. The two tests beside it, each against the floor %.1f Wh," % FLOOR)
    P("       the model's hourly-step sensitivity as reconcile_lid_panel.out's NOTES print it (measured at 40/0 at an earlier")
    P("       issue's settings; CHECK-1 measured at most 0.1 Wh at WE): COMBINED, the lowest store of both packs together above it;")
    P("       EACH PACK, the base's and the lid's own lowest stores each above it (a pack at 0.0 Wh has reached its own 3.00 V")
    P("       line with the reserve: the kit runs on on the other pack). Which one REQ-072 needs is the owner's reading: L3-OD1's")
    P("       drafted ruling on fnd/l3r2 reads 'the pack' in a requirement as each pack unless it names one.")
    P("")

    # 2. the undocumented efficiencies: what the makers' documents give
    P("2. THE THREE UNDOCUMENTED EFFICIENCIES: WHAT THE MAKERS' OWN DOCUMENTS GIVE")
    rd_fe = re.search(r"READING at 5\.5 to 6 A \(board A's front end carries U3's 6\.1 A\): ([\d.]+) to ([\d.]+) %", curves)
    rd_st = re.search(r"READING at 6 to 12 A on the 35 V curve \(board E's stage delivers up to about 12 A at 15\.1 V\): ([\d.]+) to ([\d.]+) %", curves)
    if not (rd_fe and rd_st):
        refuse(3, "curve_readings.out's readings not parsed")
    P("   board E's stage (LT8705A, declared %.2f, bracket %.2f to %.2f, 'NOT PLOTTED at this ratio'): 8705af p.41's own 12 V, 15 A" % (
        ch[0]["eta"], ch[0]["low"], ch[0]["high"]))
    P("      design (the same M1 and M2 parts as board E's Q3 and Q4) reads %s to %s %% at 6 to 12 A from 35 V (TYPICAL, 25 C, INFERRED;" % rd_st.groups())
    P("      curve_readings.out 2). Not a figure for board E at 34.3 to 15.1 V over the day's hours: NOT ESTABLISHED.")
    P("   board A's front end (LM5176, declared %.2f, bracket %.2f to %.2f, 'NOT PLOTTED at 20 V out'): SNVSAI1D p.9 Figure 6-2's" % (
        ch[1]["eta"], ch[1]["low"], ch[1]["high"]))
    P("      9 V to 12 V boost reads %s to %s %% at 5.5 to 6 A (TYPICAL, 25 C, INFERRED; curve_readings.out 1). Not a figure for" % rd_fe.groups())
    P("      board A at 15.1 to 20 V, 200 kHz, 10 uH: NOT ESTABLISHED.")
    cp3 = subprocess.run(["pdftotext", "-layout", "-f", "3", "-l", "3", os.path.join(TOP, CELL), "-"], capture_output=True, text=True).stdout
    cp7 = subprocess.run(["pdftotext", "-layout", "-f", "7", "-l", "7", os.path.join(TOP, CELL), "-"], capture_output=True, text=True).stdout
    m3 = re.search(r"Standard Capacity_0\.2C[\s\S]*?([\d,]+)\s+([\d.]+)\s", cp3)
    m7 = re.search(r"Initial\s+After storage[\s\S]*?\n\s+([\d.]+)\s+([\d.]+)\s*\n", cp7)
    if not (m3 and m7):
        refuse(3, "the cell sheet's pages 3 and 7 not parsed")
    ah, wh = float(m3.group(1).replace(",", "")) / 1000.0, float(m3.group(2))
    r_ac, r_dc = float(m7.group(1)) / 1000.0, float(m7.group(2)) / 1000.0
    v02 = wh / ah
    i02 = 0.2 * ah
    ocv = v02 + i02 * r_dc
    rows_c = []
    for lab, n_p, n_lid, i_c in (("base 4S6P (4S20P kit) at U3's %.3f A" % TP.v("chg_a_base"), TP.NP_B, 14, TP.v("chg_a_base")),
                                 ("base 4S6P (4S21P kit) at U3's %.3f A" % TP.v("chg_a_base"), TP.NP_B, 15, TP.v("chg_a_base")),
                                 ("lid 4S14P at U3B's %.3f A" % TP.v("chg_a_lid"), 14, 14, TP.v("chg_a_lid")),
                                 ("lid 4S15P at U3B's %.3f A" % TP.v("chg_a_lid"), 15, 15, TP.v("chg_a_lid"))):
        icell = i_c / n_p
        idis = TP.LOAD / (4 * v02) / (TP.NP_B + n_lid)      # the kit's whole parallel count (CHECK-2 minor 1)
        rows_c.append((lab, icell, idis, (ocv - idis * r_dc) / (ocv + icell * r_dc)))
    P("   the pack's charge efficiency (declared %.2f, bracket %.2f to %.2f, energy_inputs.yaml 'INFERRED ... no held document gives" % (
        ce["value"], ce["low"], ce["high"]))
    P("      it'): Samsung SDI's INR18650-35E sheet (%s, pinned by energy_inputs.yaml) gives p.3 the standard 0.2C discharge," % CELL)
    P("      %.3f Ah and %.2f Wh (a mean %.3f V), and p.7 one storage sample's initial AC-IR %.1f mOhm and DC-IR %.1f mOhm. It gives no" % (
        ah, wh, v02, r_ac * 1000, r_dc * 1000))
    P("      charged energy, charge curve, coulombic efficiency or hysteresis. The resistive part alone, (OCV - I_dis R) / (OCV + I_chg R)")
    P("      with OCV %.3f V (the 0.2C mean plus its own IR drop) and R the sample's DC-IR (INFERRED):" % ocv)
    for lab, icell, idis, e in rows_c:
        P("         %-38s %.3f A a cell charging, %.3f A discharging: %.4f" % (lab, icell, idis, e))
    P("      That is an UPPER bound on the charge efficiency (the undocumented losses only lower it): NOT ESTABLISHED.")
    P("")

    # 3. U3's efficiency against the bus
    P("3. U3'S EFFICIENCY AGAINST THE BUS AND ITS LIMIT (INFERRED by efficiency.py's method, the reference day at 40/0, the drafted entry)")
    P("   %-44s %8s %8s %8s   %s" % ("bus, limit", "lower", "TI", "upper", "power into U3 at the limit"))
    for lab, v in (("the endurance bracket", v_life), ("the divider-rise bracket", v_rise), ("the envelope's minimum", v_min),
                   ("SC-76", SC76_V), ("nominal", v_nom), ("the model's", TP.V_BUS20), ("the envelope's maximum", v_max)):
        for ilim in (6.0, 6.1, 6.2):
            P("   %-44s %8.4f %8.4f %8.4f   %6.1f W" % ("%s %.3f V, %.1f A" % (lab, v, ilim), u3_day(v, ilim, "lower"),
                                                    u3_day(v, ilim, "TI"), u3_day(v, ilim, "upper"), v * ilim))
    P("")

    # 4. sensitivity
    P("4. ONE INPUT AT A TIME ON 40/0, FROM WE (TYP and WAB) AND FROM NOM WAB: the lowest store of both packs in Wh (or minus the")
    P("   energy left unserved) and its change; the base's and the lid's own lowest in brackets. WE is CONDITIONAL (1c).")
    axes_we = [("VBUS20, the endurance bracket %.3f V" % v_life, dict(vbus=v_life, eta_u3=u3_day(v_life, 6.1, "lower"))),
               ("VBUS20, the divider-rise bracket %.3f V" % v_rise, dict(vbus=v_rise, eta_u3=u3_day(v_rise, 6.1, "lower"))),
               ("VBUS20 nominal %.3f V (favourable)" % v_nom, dict(vbus=v_nom, eta_u3=u3_day(v_nom, 6.1, "lower"))),
               ("U3's limit 6.0 A", dict(iin=6.0, eta_u3=u3_day(v_min, 6.0, "lower"))),
               ("U3's limit 6.2 A (favourable)", dict(iin=6.2, eta_u3=u3_day(v_min, 6.2, "lower"))),
               ("U3 at TI's reading (favourable)", dict(eta_u3=u3_day(v_min, 6.1, "TI"))),
               ("U3B carried %.3f (favourable)" % TP.v("eta_u3b"), dict(eta_b=TP.v("eta_u3b"))),
               ("the stage %.2f" % ch[0]["low"], dict(eta_st=ch[0]["low"])),
               ("the stage %.2f (favourable)" % ch[0]["high"], dict(eta_st=ch[0]["high"])),
               ("the front end %.2f" % ch[1]["low"], dict(eta_fe=ch[1]["low"])),
               ("the front end %.2f (favourable)" % ch[1]["high"], dict(eta_fe=ch[1]["high"])),
               ("the pack's charge efficiency %.2f" % ce["low"], dict(chg_eta=ce["low"])),
               ("the pack's charge efficiency %.2f (favourable)" % ce["high"], dict(chg_eta=ce["high"])),
               ("the lid loops nominal %.3f / %.3f Ohm (favourable)" % (TP.v("r_lid_dsg"), TP.v("r_lid_chg")),
                dict(r_dsg=TP.v("r_lid_dsg"), r_chg=TP.v("r_lid_chg"))),
               ("V(AK) typical %.0f mV (favourable)" % (vak[1] * 1000), dict(v_ak=vak[1])),
               ("no standby drain (favourable)", dict(drain_w=0.0))]

    def ax_run(n, base_k, b, ex):
        ex = dict(ex)
        vb, ii = ex.pop("vbus", None), ex.pop("iin", None)
        return at(n, base_k, b, extra=ex, vbus=vb, iin=ii)
    ranks = {}
    for n, what in LIDS[1:]:
        P("   %s" % what)
        for b in ("TYP", "WAB"):
            base = at(n, "WE", b)
            P("      from WE %s: %s" % (b, packs(base)))
            rk = []
            for name, ex in axes_we:
                s = ax_run(n, "WE", b, ex)
                dv = metric(s) - metric(base)
                P("         %-52s %-44s %+7.1f" % (name, packs(s), dv))
                rk.append((dv, name))
            other = at(n, "WE", "WAB" if b == "TYP" else "TYP")
            dv = metric(other) - metric(base)
            P("         %-52s %-44s %+7.1f" % ("the other array build", packs(other), dv))
            rk.append((dv, "the array build"))
            ranks[(n, b)] = sorted(x for x in rk if x[0] < 0)
        base = at(n, "NOM", "WAB")
        P("      from NOM WAB: %s" % packs(base))
        for name, ex in [("VBUS20 %.3f V" % v_min, dict(vbus=v_min, eta_u3=u3_day(v_min, i_nom, "TI"))),
                         ("U3's limit 6.1 A", dict(iin=6.1, eta_u3=u3_day(v_nom, 6.1, "TI"))),
                         ("U3's limit 6.0 A", dict(iin=6.0, eta_u3=u3_day(v_nom, 6.0, "TI"))),
                         ("U3 at the makers' maxima", dict(eta_u3=u3_day(v_nom, i_nom, "lower"))),
                         ("U3B %.3f" % TP.v("eta_u3b_lo"), dict(eta_b=TP.v("eta_u3b_lo"))),
                         ("the stage %.2f" % ch[0]["low"], dict(eta_st=ch[0]["low"])),
                         ("the front end %.2f" % ch[1]["low"], dict(eta_fe=ch[1]["low"])),
                         ("the pack's charge efficiency %.2f" % ce["low"], dict(chg_eta=ce["low"])),
                         ("the lid loops %.3f / %.3f Ohm" % (rd[1], rc_[1]), dict(r_dsg=rd[1], r_chg=rc_[1])),
                         ("V(AK) %.0f mV" % (vak[2] * 1000), dict(v_ak=vak[2])),
                         ("the standby drain %.1f Wh" % drain_wh, dict(drain_w=drain_w))]:
            s = ax_run(n, "NOM", "WAB", ex)
            P("         %-52s %-44s %+7.1f" % (name, packs(s), metric(s) - metric(base)))
    P("   The unfavourable changes from WE, largest first:")
    for n, _w in LIDS[1:]:
        for b in ("TYP", "WAB"):
            P("      %s WE %s: %s" % (dict(LIDS)[n].split(",")[0], b, "; ".join("%s %+.1f" % (nm, dv) for dv, nm in ranks[(n, b)])))
    P("   (the first issue's table, one at a time from NOM TYP, sat where both packs fill before dusk and hid the charge-side")
    P("   losses; it is withdrawn)")
    P("")

    # 4b. the knee
    P("4b. THE LOWEST STORE AGAINST THE POWER U3 MAY TAKE (the bus times U3's limit), every other input at NOM, on 40/0")
    P("   %-10s %s" % ("into U3", "  ".join("%-27s" % ("%s %s" % (dict(LIDS)[n].split(",")[0], b)) for n in (14, 15) for b in ("TYP", "WAB"))))
    for pw in range(108, 132, 2):
        cells_ = []
        for n in (14, 15):
            for b in ("TYP", "WAB"):
                s_ = summ(run(n, pr0 * (rb40 if b == "TYP" else rc40), v_nom, pw / v_nom, over={"eta_u3": e_nom}, prof=pp40))
                cells_.append("%-27s" % cell(s_))
        P("   %6.1f W  %s" % (pw, "  ".join(cells_)))
    P("   With the TYP build the store rises steeply from 110 to 122 W and is flat above (the packs fill before dusk); with the WAB")
    P("   build it keeps rising to 128 W. The bus's steady-state range is %.1f to %.1f W at 6.1 A and %.1f to %.1f W at 6.0 A." % (
        v_min * 6.1, v_max * 6.1, v_min * 6.0, v_max * 6.0))
    P("")

    # 5. combined cases at 40/0
    P("5. THE CASES ON THE REFERENCE PLANE (40/0): both packs' lowest store (the base's, the lid's) in Wh or the unserved energy;")
    P("   COMB and EACH: the two pass lines of 1d (Y meets, N does not)")
    P("   %-8s %-5s %-44s %-9s %-44s %-9s" % ("lid", "case", "TYP", "COMB/EACH", "WAB", "COMB/EACH"))
    for n, what in LIDS:
        for k in order:
            r2 = []
            for b in ("TYP", "WAB"):
                s = at(n, k, b)
                r2 += [packs(s), "%s/%s" % ("Y" if comb(s) else "N", "Y" if each(s) else "N")]
            P("   %-8s %-5s %-44s %-9s %-44s %-9s" % (what.split(",")[0], k, r2[0], r2[1], r2[2], r2[3]))
    P("")

    # 6. the grid
    P("6. THE PLANES: bands where BOTH builds pass, per case and pass line (maps: B both builds pass, T the TYP build only")
    P("   passes, - neither), INFERRED from the grid")
    grid = {}
    for n in (14, 15):
        for k in ("NOM", "WE", "WE60", "WA"):
            for pl in planes:
                grid[(n, k, pl)] = (at(n, k, "TYP", pl), at(n, k, "WAB", pl))

    def passes(n, k, sl, az, line):
        a0 = 0 if sl == 0 else az
        return all(line(s) for s in grid[(n, k, (sl, a0))])

    def rects(n, k, line):
        rr = []
        S, A = ER.SLOPES, ER.ASPECTS
        for i in range(len(S)):
            for j in range(i, len(S)):
                for a in range(len(A)):
                    for b in range(a, len(A)):
                        if all(passes(n, k, S[s], A[t], line) for s in range(i, j + 1) for t in range(a, b + 1)):
                            rr.append((i, j, a, b))
        mx = [r for r in rr if not any(q != r and q[0] <= r[0] and q[1] >= r[1] and q[2] <= r[2] and q[3] >= r[3] for q in rr)]
        mx.sort(key=lambda r: (-(r[1] - r[0] + 1) * (r[3] - r[2] + 1), r))
        return mx
    bands = {}
    for n in (14, 15):
        P("   %s" % dict(LIDS)[n])
        for k in ("NOM", "WE", "WE60", "WA"):
            for lname, line in (("COMB", comb), ("EACH", each)):
                mx = rects(n, k, line)
                bands[(n, k, lname)] = mx
                P("      case %s, pass line %s" % (k, lname))
                P("         %6s %s" % ("slope", "".join("%5s" % ("%+d" % a) for a in ER.ASPECTS)))
                for sl in ER.SLOPES:
                    cc = []
                    for az in ER.ASPECTS:
                        if sl == 0 and az != 0:
                            cc.append("%5s" % ".")
                            continue
                        t, w = grid[(n, k, (sl, az))]
                        cc.append("%5s" % ("B" if passes(n, k, sl, az, line) else ("T" if line(t) else "-")))
                    P("         %6d %s" % (sl, "".join(cc)))
                for r in mx[:3]:
                    pts = [(ER.SLOPES[s], ER.ASPECTS[t]) for s in range(r[0], r[1] + 1) for t in range(r[2], r[3] + 1)]
                    lw = {key: min(((s[key], sl, az, bb) for sl, az in pts for s, bb in zip(grid[(n, k, (sl, az))], ("TYP", "WAB"))),
                                   key=lambda x: x[0]) for key in ("both", "base", "lid")}
                    P("         band: slope %2d to %2d, azimuth %+3d to %+3d (%2d points); least %s" % (
                        ER.SLOPES[r[0]], ER.SLOPES[r[1]], ER.ASPECTS[r[2]], ER.ASPECTS[r[3]], len(pts),
                        "; ".join("%s %.1f Wh at %d/%+d %s" % ((key,) + lw[key]) for key in ("both", "base", "lid"))))
                if not mx:
                    P("         band: none")
    P("")

    # 7. thresholds
    P("7. WHAT EACH UNDOCUMENTED FIGURE MUST REACH: at each point, the input alone moved from WE (the rest as WE), the least")
    P("   value at which both builds still pass the line (bisection; 'any' = passes at the search's worst end; 'none' = fails")
    P("   at its best end)")
    rng = {"chg_eta": (0.80, 1.00), "eta_st": (0.80, 1.00), "eta_fe": (0.80, 1.00), "vbus": (16.0, 22.0), "iin": (5.0, 6.35)}
    decl = {"chg_eta": ce["value"], "eta_st": ch[0]["eta"], "eta_fe": ch[1]["eta"], "vbus": v_min, "iin": 6.1}
    names = {"chg_eta": "pack charge", "eta_st": "stage", "eta_fe": "front end", "vbus": "VBUS20", "iin": "U3's limit"}

    def ok_at(n, pl, key, x, line):
        ex = {}
        vb = ii = None
        if key == "vbus":
            vb = x
        elif key == "iin":
            ii = x
        else:
            ex[key] = x
        return all(line(at(n, "WE", b, pl, extra=ex, vbus=vb, iin=ii)) for b in ("TYP", "WAB"))

    def thresh(n, pl, key, line):
        lo, hi = rng[key]
        if ok_at(n, pl, key, lo, line):
            return "any"
        if not ok_at(n, pl, key, hi, line):
            return "none"
        for _ in range(22):
            mid = 0.5 * (lo + hi)
            if ok_at(n, pl, key, mid, line):
                hi = mid
            else:
                lo = mid
        return ("%.3f V" % hi) if key == "vbus" else (("%.3f A" % hi) if key == "iin" else "%.3f" % hi)
    th = {}
    pts_by = {15: sorted(set([(40, 0)] + [(ER.SLOPES[s], ER.ASPECTS[t]) for r in bands[(15, "WE", "COMB")][:1]
                                          for s in range(r[0], r[1] + 1) for t in range(r[2], r[3] + 1)])),
              14: [(30, 0), (40, 0), (40, 15), (50, 0)]}
    P("   %-8s %-7s %-5s %-12s %-12s %-12s %-12s %-12s" % ("lid", "point", "line", "pack charge", "stage", "front end", "VBUS20", "U3's limit"))
    P("   %-8s %-7s %-5s %-12s %-12s %-12s %-12s %-12s" % ("", "", "WE's", "%.2f" % decl["chg_eta"], "%.2f" % decl["eta_st"],
                                                       "%.2f" % decl["eta_fe"], "%.3f V" % decl["vbus"], "%.1f A" % decl["iin"]))
    for n in (15, 14):
        for pl in pts_by[n]:
            for lname, line in (("COMB", comb), ("EACH", each)):
                vals = [thresh(n, pl, key, line) for key in ("chg_eta", "eta_st", "eta_fe", "vbus", "iin")]
                th[(n, pl, lname)] = vals
                P("   %-8s %-7s %-5s %-12s %-12s %-12s %-12s %-12s" % (dict(LIDS)[n].split(",")[0], "%d/%+d" % pl, lname, *vals))
    P("   The makers' documents for the three efficiencies (section 2): the stage's curve reads %s to %s %% and the front end's" % (
        rd_st.group(1), rd_st.group(2)))
    P("   %s to %s %% at their nearest printed points (other circuits, typical, INFERRED); the cell sheet bounds the charge" % rd_fe.groups())
    P("   efficiency's resistive part at %.4f to %.4f from above. None establishes a figure for this kit." % (
        min(r_[3] for r_ in rows_c), max(r_[3] for r_ in rows_c)))
    P("")

    # 8. informative weather
    P("8. INFORMATIVE ONLY, NOT A REQUIREMENT CASE: M1 IN SEPTEMBER'S ACTUAL WEATHER, 2005 TO 2020, AT 40/0")
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
    P("   M1 counted as met when neither pack path stops the kit (the model's verdict); WE is CONDITIONAL (1c).")
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
                wins.append((y, dd + 1, st, yr[i0:i0 + 72], [(i0 + i) // 24 for i in range(72)]))
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
    P("   %-8s %-9s %-22s %-40s %-40s %s" % ("lid", "case", "windows meeting M1", "the darkest window", "the 10th percentile window",
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
            P("   %-8s %-9s %4d of %4d (%5.1f %%)   %-40s %-40s %s / %s" % (
                dict(LIDS)[n].split(",")[0], "%s %s" % (k, b), nm, len(out), 100.0 * nm / len(out), wtxt(dk), wtxt(p10),
                ("%.2f" % min(meets)) if meets else "none", ("%.2f" % max(fails)) if fails else "none"))
    P("   4S9P is not run here: it does not meet M1 on the mean day in any case (section 5).")
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
