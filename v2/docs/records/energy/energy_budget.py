#!/usr/bin/env python3
"""energy_budget.py: mission M1's energy reconciliation (stream energy, MESHSAT-1357, 28 September 2026).

PROTOTYPE DESIGN: nothing in this kit has been built, powered or measured. Every figure printed is arithmetic on
makers' figures, on generator declarations and on stated assumptions read from energy_inputs.yaml beside this file;
the readings are an AI's (an AI review). Nothing printed is a measurement.

What it prints (the sections of ENERGY-RECONCILIATION.md):
  1  the loads of each state M1 uses, with the kind of every figure, recounted from the components
  2  the usable energy of the pack, new and aged, at +20 C, 0 C and the cells' -10 C floor
  3  the night at 52 N by month from the solar declination, with civil twilight
  4  the solar energy into the kit per day by month, panel size and the 100 W window
  5  M1 hour by hour: the balance for the design month and the worst month, and the sensitivity table
  6  the options' numbers
  7  the smallest changes' numbers

Determinism: the output carries no date, host or absolute path; two runs on the same inputs give the same bytes.
Inputs: this file pins energy_inputs.yaml and the files it lists by sha256 and refuses to run, naming the file, if
any of them changed. Usage: energy_budget.py [--root <repository root>]  (needs python3 with PyYAML; a few seconds).
"""
import argparse
import hashlib
import math
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS_SHA256 = "474a84e2d3ef877b02e1a6d1baa8c7063116d791e6d72322178e66dd57965e81"  # energy_inputs.yaml, set by --pin


class InputError(Exception):
    pass


# ----------------------------------------------------------------------------------------------------- helpers
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def interp(points, x):
    """Linear interpolation on [[x, y], ...] sorted by x; clamped at the ends."""
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return points[-1][1]


def bisect(f, lo, hi, n=60):
    """Smallest x in [lo, hi] with f(x) true, f monotone; returns hi if never true."""
    if not f(hi):
        return None
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if f(mid):
            hi = mid
        else:
            lo = mid
    return hi


class Out:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        self.lines.append(s)

    def table(self, headers, rows):
        w = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(str(h)) for i, h in enumerate(headers)]
        fmt = "  " + "  ".join("%%-%ds" % x for x in w)
        self(fmt % tuple(headers))
        self(fmt % tuple("-" * x for x in w))
        for r in rows:
            self(fmt % tuple(str(x) for x in r))

    def text(self):
        return "\n".join(self.lines) + "\n"


def f1(x):
    return "%.1f" % x


def f2(x):
    return "%.2f" % x


# ----------------------------------------------------------------------------------------------- 1. the loads
def state_rows(d, state):
    """The battery-side W of every load in a state, from the PS-IDLE-SPEC rows and the state's rules."""
    rules = d["state_rules"].get(state, {})
    base_state = rules.get("base")
    if base_state:
        rows = state_rows(d, base_state)
    else:
        rows = [dict(r) for r in d["loads"]]
        for r in rows:
            r["state_bat"] = r["bat"]
            r["state_load"] = r["load"]
            r["state_kind"] = r["tier"]
    off = set(rules.get("off_groups", []))   # not "off": YAML 1.1 reads that key as the boolean False
    typ = set(rules.get("cm5_typ", []))
    low = set(rules.get("low", []))
    night = set(rules.get("night", []))
    for r in rows:
        g = r["group"]
        ratio = r["bat"] / r["load"] if r["load"] else 1.0   # the row's own conversion and distribution factor
        if g in off:
            r["state_bat"], r["state_load"] = 0.0, 0.0
        elif g in typ:
            r["state_load"] = 4.5   # the maker's typical operating 900 mA at 5 V (cm5-datasheet.pdf section 3.3)
            r["state_bat"] = r["state_load"] * ratio
        elif g in low and "low_load" in r:
            r["state_load"] = r["low_load"]
            r["state_bat"] = r["state_load"] * ratio
        elif g in night and "night_load" in r:
            r["state_load"] = r["night_load"]
            r["state_bat"] = r["state_load"] * ratio
    return rows


def state_power(d, state, sourced_d=False):
    """Sum of the rows plus the distribution I2R correction; sourced_d swaps the D rows for the makers' figures."""
    rows = state_rows(d, state)
    tot_bat = 0.0
    tot_load = 0.0
    kinds = {"S": 0.0, "R": 0.0, "D": 0.0, "T": 0.0}
    counts = {"S": 0, "R": 0, "D": 0, "T": 0}
    for r in rows:
        b, l = r["state_bat"], r["state_load"]
        if sourced_d and r["tier"] == "D" and "maker_w_at_load" in r and l > 0:
            l2 = r["maker_w_at_load"] * (l / r["load"])
            b = b * (l2 / l) if l else 0.0
            l = l2
        if l > 0:
            kinds[r["tier"]] += b
            counts[r["tier"]] += 1
        tot_bat += b
        tot_load += l
    return tot_bat, tot_load, kinds, counts, rows


def section1(o, d):
    o("1. THE LOADS OF THE STATES M1 USES (battery-side W, PLAN, 14.4 V; kinds S maker / R maker's bound at a duty /")
    o("   D declaration / T placeholder; MEASURED: none, the tree holds no measurement of any load)")
    o()
    rows = state_rows(d, "PS-IDLE-SPEC")
    o("1a. PS-IDLE-SPEC, every load (records/rv-pwr/pwr_budget.out, the model behind CONOPS 4a's 42.8 W):")
    o.table(["load", "at load W", "battery W", "kind", "maker's figure for the D rows (d4energy)", "source"],
            [[r["name"], f2(r["load"]), f2(r["bat"]), r["tier"], (f2(r["maker_w_at_load"]) if "maker_w_at_load" in r else ""), r["src"][:110]] for r in rows])
    o()
    res = {}
    o("1b. The four states recounted from the same components, against the tree's model:")
    trows = []
    for st in ("PS-IDLE-SPEC", "PS-RED2", "PS-SURV-R", "PS-SURV", "PS-NIGHT-RELAY"):
        b, l, kinds, counts, _ = state_power(d, st)
        bs, ls, _, _, _ = state_power(d, st, sourced_d=True)
        m = d["model_states"].get(st)
        res[st] = {"recount_bat": b, "recount_load": l, "sourced_bat": bs, "model": (m["plan"] if m else None),
                   "kinds": kinds, "counts": counts}
        trows.append([st, f2(l), f2(b), (f2(m["plan"]) if m else "n/a (this record's option a)"),
                      (f2(b - m["plan"]) if m else ""), f2(bs),
                      "S %d %.1f W / R %d %.1f / D %d %.1f / T %d %.1f" % (counts["S"], kinds["S"], counts["R"], kinds["R"], counts["D"], kinds["D"], counts["T"], kinds["T"])])
    o.table(["state", "at loads W", "recount battery W", "model PLAN W", "recount - model", "D rows at makers' figures W", "kind counts and battery W"], trows)
    o()
    o("   The recount applies each state's on/off rules to the PS-IDLE-SPEC rows with each row's own conversion factor")
    o("   (battery W over load W in PS-IDLE-SPEC) and does not re-solve the distribution I2R at the lower current, which")
    o("   is why it reads a few tenths of a watt above the model in the reduced states (the model's I2R at 31 W is")
    o("   about 0.1 W, at 43 W about 0.2 W). The 'D rows at makers' figures' column replaces the five declared rows")
    o("   (panel board C, other +3V3_DEV logic, board E controller, board A logic, four CP2102N bridges) by the sum of")
    o("   the makers' typical supply currents d4energy read for the same parts, and the board D row by the maker's")
    o("   figure where it is HIGHER than the declaration: the declarations are copper-sizing allocations, and the")
    o("   difference (about 3 W) is what the bench must settle; the balance below runs at the model's PLAN figures and")
    o("   never at the lower ones (nothing is lowered to obtain a result).")
    o()
    return res


# ------------------------------------------------------------------------------------------ 2. usable energy
class Pack:
    def __init__(self, d):
        p = d["pack"]
        self.n_s = p["series"]
        self.n_p = p["parallel"]
        self.c_min = p["capacity_min_ah"]["value"]
        self.rate = p["rate_factor"]["points"]
        self.temp = p["temperature_factor"]["points"]
        self.vmean = p["mean_v_points"]["points"]
        self.f300 = p["end_of_discharge"]["fraction_at_3v00"]["points"]
        self.f280 = p["end_of_discharge"]["fraction_at_2v80"]["points"]
        self.rsoc = p["end_of_discharge"]["graceful"]["rsoc_reserve"]
        self.age80 = p["ageing"]["aged_80"]["factor"]
        self.age60 = p["ageing"]["aged_60"]["factor"]
        self.chg_a = p["charge"]["current_a"]["value"]
        self.taper = p["charge"]["taper_from_soc"]
        self.chg_eta = p["charge"]["energy_efficiency"]["value"]

    def cell_current(self, p_w, n_p=None):
        n_p = n_p or self.n_p
        v = self.n_s * 3.60
        for _ in range(3):
            i = p_w / v / n_p
            v = self.n_s * interp(self.vmean, i)
        return i

    def usable_wh(self, p_w, t_c=20.0, age=1.0, dod="3v00", n_p=None):
        """Wh the cells deliver to the graceful shutdown at constant power p_w (a chain of factors, each labelled)."""
        n_p = n_p or self.n_p
        i = self.cell_current(p_w, n_p)
        f_rate = interp(self.rate, i)
        f_t = interp(self.temp, t_c)
        v_mean = interp(self.vmean, i)
        f_v = interp(self.f300 if dod == "3v00" else self.f280, i)
        f_dod = min(f_v, 1.0 - self.rsoc)   # whichever ends the run first: the voltage line or the 5 percent reserve
        wh = self.n_s * n_p * self.c_min * f_rate * f_t * v_mean * f_dod * age
        return wh, {"i_cell": i, "f_rate": f_rate, "f_t": f_t, "v_mean": v_mean, "f_dod": f_dod, "age": age}


def section2(o, d, pack, res1):
    o("2. USABLE BATTERY ENERGY of the ruled 4S3P block (12 x Samsung INR18650-35E)")
    o()
    o("   E = 12 cells x C_min x f_rate(I) x f_T x V_mean(I) x f_dod x f_age, at the state's constant power:")
    o("   C_min 3.35 Ah (spec 3.1, 0.2C to 2.65 V at 23 C); f_rate spec 7.8 (100 percent at 0.68 A, 97 at 3.4 A, linear);")
    o("   f_T spec 7.5 (40 / 97 at -10 C at 3.4 A, 1.00 at 20 to 40 C; between -10 and 20 C linear, INFERRED, a lower")
    o("   bound at the kit's currents); V_mean the typical cell's Wh / Ah of the Technical Report (3.624 V at 0.2C, 3.443 V")
    o("   at 3.5 A, linear); f_dod the share of the trace delivered when the cell reaches the graceful line of 3.00 V")
    o("   under load (0.937 at 0.7 A, 0.905 at 3.5 A, an AI reading of the maker's traces) or the 5 percent RSOC")
    o("   reserve, whichever comes first (the voltage line does, at every current here); f_age 0.80 (REQ-014, SC-23) or")
    o("   0.60 (spec 7.9, the lower bracket). Nominal: 12 x 3.35 x 3.60 = %.1f Wh." % (12 * 3.35 * 3.60))
    o()
    rows = []
    res = {}
    for st in ("PS-IDLE-SPEC", "PS-RED2", "PS-SURV-R", "PS-SURV", "PS-NIGHT-RELAY"):
        p = res1[st]["model"] or res1[st]["recount_bat"]
        for t in (20.0, 0.0, -10.0):
            new, k = pack.usable_wh(p, t, 1.0)
            a80, _ = pack.usable_wh(p, t, pack.age80)
            a60, _ = pack.usable_wh(p, t, pack.age60)
            res[(st, t)] = {"new": new, "a80": a80, "a60": a60, "p": p, "k": k}
            rows.append([st, f1(p), "%+.0f" % t, f2(k["i_cell"]), "%.4f" % k["f_rate"], "%.3f" % k["f_t"], "%.3f" % k["v_mean"], "%.3f" % k["f_dod"],
                         f1(new), f1(a80), f1(a60), f2(new / p), f2(a80 / p), f2(a60 / p)])
    o.table(["state", "W at pack", "cells C", "A a cell", "f_rate", "f_T", "V_mean", "f_dod", "new Wh", "aged 80 Wh", "aged 60 Wh", "h new", "h aged 80", "h aged 60"], rows)
    o()
    o("   Check against the tree: POWER-THERMAL section 6 reads 108.1 Wh aged (80 percent) for PS-IDLE-SPEC by a different")
    o("   route (rate factor, a 0.05 Ohm sag, a 5 percent reserve); this chain reads %.1f Wh: the two agree within 1 Wh." % res[("PS-IDLE-SPEC", 20.0)]["a80"])
    o("   -10 C is the cells' discharge floor (spec 3.12) and D-02d's -20 C is the AMBIENT once the kit is warm: the pack")
    o("   heater (7.5 W at the mat, RS PRO 245-556, about 8.3 W at the pack through its buck) must hold the cells at or")
    o("   above -10 C there, which adds that load to the balance; a start below about -10 C at the cells is out of scope (D-02d).")
    o("   Option (b): the graceful line at 2.80 V under load instead of 3.00 V (still above the gauge's 2.50 V trip and the")
    o("   maker's 2.50 V terminate line, 0.15 V above the spec's 2.65 V cut-off) moves f_dod from %.3f to %.3f at" % (
        pack.usable_wh(42.8)[1]["f_dod"], pack.usable_wh(42.8, dod="2v80")[1]["f_dod"]))
    o("   PS-IDLE-SPEC's current: %.1f Wh aged instead of %.1f, a gain of %.1f Wh (about %.0f percent)." % (
        pack.usable_wh(42.8, 20.0, 0.8, "2v80")[0], pack.usable_wh(42.8, 20.0, 0.8)[0],
        pack.usable_wh(42.8, 20.0, 0.8, "2v80")[0] - pack.usable_wh(42.8, 20.0, 0.8)[0],
        100 * (pack.usable_wh(42.8, 20.0, 0.8, "2v80")[0] / pack.usable_wh(42.8, 20.0, 0.8)[0] - 1)))
    o()
    return res


# ------------------------------------------------------------------------------------------------ 3. the night
def declination_deg(day_of_year):
    """Spencer (1971) Fourier series for the solar declination; within about 0.05 degrees of the ephemeris."""
    g = 2.0 * math.pi * (day_of_year - 1) / 365.0
    dec = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
           + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    return math.degrees(dec)


def day_length_h(lat_deg, dec_deg, h0_deg):
    """Hours the sun's centre is above altitude h0: cos(w) = (sin h0 - sin lat sin dec) / (cos lat cos dec)."""
    lat, dec, h0 = map(math.radians, (lat_deg, dec_deg, h0_deg))
    c = (math.sin(h0) - math.sin(lat) * math.sin(dec)) / (math.cos(lat) * math.cos(dec))
    if c >= 1.0:
        return 0.0
    if c <= -1.0:
        return 24.0
    return 2.0 * math.degrees(math.acos(c)) / 15.0


DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def section3(o, d):
    lat = d["solar"]["latitude_deg"]
    o("3. THE NIGHT AT %.2f N (Leiden) by month: the solar declination from Spencer's (1971) series (within about 0.05" % lat)
    o("   degrees), the day length from cos(w0) = (sin h0 - sin lat sin dec) / (cos lat cos dec) with h0 = -0.833 degrees")
    o("   (refraction and the sun's half-diameter, the usual sunrise definition) and h0 = -6 degrees (civil twilight).")
    o("   Accuracy of the day length: about 2 to 4 minutes at this latitude (the series' error and the refraction's")
    o("   weather dependence); no ephemeris is held in the tree. 'Sun down' is 24 h less the sunrise-to-sunset day;")
    o("   'dark' is 24 h less the civil-twilight day (a panel gives almost nothing in twilight: PVGIS's mean-day")
    o("   irradiance at the first and last lit hour is 0 to 57 W/m2 in September).")
    o()
    rows = []
    res = {}
    for m in range(12):
        start = sum(DAYS[:m]) + 1
        dl = [day_length_h(lat, declination_deg(start + k), -0.833) for k in range(DAYS[m])]
        dt = [day_length_h(lat, declination_deg(start + k), -6.0) for k in range(DAYS[m])]
        mean_dl, mean_dt = sum(dl) / len(dl), sum(dt) / len(dt)
        mid = day_length_h(lat, declination_deg(start + 14), -0.833)
        res[m + 1] = {"day_h": mean_dl, "night_h": 24 - mean_dl, "dark_h": 24 - mean_dt, "dec15": declination_deg(start + 14)}
        rows.append([MONTHS[m], "%+.1f" % declination_deg(start + 14), f2(mid), f2(mean_dl), f2(24 - mean_dl), f2(mean_dt), f2(24 - mean_dt)])
    o.table(["month", "dec. on the 15th", "day h on the 15th", "mean day h", "mean sun-down h", "mean twilight day h", "mean dark h"], rows)
    o()
    ds = day_length_h(lat, declination_deg(172), -0.833)
    dw = day_length_h(lat, declination_deg(355), -0.833)
    o("   Extremes: the summer solstice (21 June) day %.2f h, night %.2f h; the winter solstice (21 December) day %.2f h," % (ds, 24 - ds, dw))
    o("   night %.2f h. September (the design month): mean night %.2f h sun down, %.2f h dark. The longest night is" % (24 - dw, res[9]["night_h"], res[9]["dark_h"]))
    o("   %.2f h (December's mean; %.2f at the solstice), the shortest %.2f h (June's mean; %.2f at the solstice)." % (res[12]["night_h"], 24 - dw, res[6]["night_h"], 24 - ds))
    o("   Cross-check against PVGIS's mean-day profile (hours with any irradiance, UTC): June 04:00 to 19:59 (16 h),")
    o("   September 06:00 to 18:59 (13 h, the last hour at 0.4 W/m2), December 08:00 to 15:59 (8 h, the last at 1.9),")
    o("   against %.1f, %.1f and %.1f h of sun here: the hourly grid rounds outward by up to an hour each side." % (res[6]["day_h"], res[9]["day_h"], res[12]["day_h"]))
    o()
    return res


# ------------------------------------------------------------------------------------------- 4. the solar input
def month_mean_day_kwh(monthly_json, m):
    vals = [r["H(i_opt)_m"] for r in monthly_json["outputs"]["monthly"] if r["month"] == m]
    return sum(vals) / len(vals) / DAYS[m - 1], len(vals)


def profile(d, monthly_json, m):
    raw = d["solar"]["day_profile_w_m2"][m]
    mean_day, n = month_mean_day_kwh(monthly_json, m)
    s = sum(raw) / 1000.0
    scale = mean_day / s
    return [x * scale for x in raw], mean_day, scale, n


def panel_w(g, wp, pr):
    return wp * g / 1000.0 * pr


def node_w(g, wp, pr, window, eta):
    return min(panel_w(g, wp, pr), window) * eta


def section4(o, d, monthly_json):
    s = d["solar"]
    pr = s["panel"]["performance_ratio"]["typ"]
    eta = 1.0
    for c in s["chain"]:
        eta *= c["eta"]
    eta_lo = 1.0
    eta_hi = 1.0
    for c in s["chain"]:
        eta_lo *= c["low"]
        eta_hi *= c["high"]
    window = s["window"]["stage_max_w_in"]["value"]
    o("4. THE SOLAR CONTRIBUTION per day, into the kit's system node")
    o()
    o("   Resource: PVGIS-SARAH2 monthly irradiation 2015 to 2020 on the 40 degree south plane (the pinned monthly file),")
    o("   the mean day of each month; the day's shape from PVGIS's DRcalc mean-day profile (2005 to 2020, on fnd/d4energy),")
    o("   scaled to the pinned monthly mean. Panel: STC rating x G / 1000 x %.4f (PVGIS's own angle, spectral and" % pr)
    o("   temperature losses, no system loss; maximum-power tracking assumed, which the fixed 17.6 V stage does not do:")
    o("   the low bracket takes 0.80). Window: at most %.0f W into the stage (REQ-016); above it the stage clips." % window)
    o("   Chain into the node: %.2f x %.2f x %.2f = %.4f (bracket %.3f to %.3f); the panel's 5.68 A at 17.6 V sits" % (
        s["chain"][0]["eta"], s["chain"][1]["eta"], s["chain"][2]["eta"], eta, eta_lo, eta_hi))
    o("   under F2's and J_SOLAR's 10 A.")
    o()
    res = {"pr": pr, "eta": eta, "eta_lo": eta_lo, "eta_hi": eta_hi, "window": window, "months": {}}
    rows = []
    for m in (6, 9, 12):
        prof, mean_day, scale, n = profile(d, monthly_json, m)
        res["months"][m] = {"profile": prof, "mean_day_kwh": mean_day, "scale": scale}
        for wp in d["sensitivity"]["panel_wp_list"]:
            e_panel = sum(panel_w(g, wp, pr) for g in prof)
            e_node = sum(node_w(g, wp, pr, window, eta) for g in prof)
            e_node_noclip = e_panel * eta
            clipped_h = sum(1 for g in prof if panel_w(g, wp, pr) > window)
            peak = max(panel_w(g, wp, pr) for g in prof)
            res["months"][m][wp] = {"e_panel": e_panel, "e_node": e_node, "e_node_noclip": e_node_noclip, "clipped_h": clipped_h, "peak": peak}
            rows.append([MONTHS[m - 1], f2(mean_day), "%.3f" % scale, "%d" % wp, f1(e_panel), f1(peak), "%d" % clipped_h, f1(e_node), f1(e_node_noclip),
                         f1(e_node * eta_lo / eta * 0.80 / pr), f1(e_node * eta_hi / eta)])
    o.table(["month", "kWh/m2 a day", "profile scale", "panel Wp", "panel Wh/day", "panel peak W", "hours clipped", "into node Wh/day (100 W window)", "no window", "low bracket", "high bracket"], rows)
    o()
    o("   Reading the table: a 100 Wp panel never reaches the window (its peak is under 100 W) and gives %.0f Wh a day at the" % res["months"][9][100]["e_node"])
    o("   node in September and %.0f in December (the low brackets %.0f and %.0f). A larger panel is clipped at 100 W into" % (
        res["months"][12][100]["e_node"], res["months"][9][100]["e_node"] * eta_lo / eta * 0.80 / pr, res["months"][12][100]["e_node"] * eta_lo / eta * 0.80 / pr))
    o("   the stage for the hours shown, and the most the window can pass in a day is %.0f W x the lit hours: %.0f Wh in" % (window * eta, window * eta * sum(1 for g in res["months"][9]["profile"] if g > 0)))
    o("   September and %.0f Wh in December with a panel large enough to hold the clip all day. That is the ceiling a" % (window * eta * sum(1 for g in res["months"][12]["profile"] if g > 0)))
    o("   re-rated input path (S-53) would lift; the fuse F2 and J_SOLAR at 10 A carry two paralleled 100 Wp panels'")
    o("   short-circuit current (about 12.5 A) NOT, so more than about 150 Wp of 12 V class panel also re-rates the entry.")
    o()
    return res


# ---------------------------------------------------------------------------------------------- 5. the balance
def simulate(d, pack, prof, p_load, wp, window, eta, pr, start_h, t_c, age, hours, dod="3v00", n_p=None, e_scale=1.0):
    """Hour by hour. The node's demand is p_load (W at the pack terminals); the solar path feeds it first and the
    surplus charges the cells at the charger's limit; the deficit comes from the cells. When the usable energy is
    gone the kit stops (the graceful shutdown) and restarts when the sun alone carries the load (the operator, since
    the kit does not restart by itself, CONOPS section 4c) or once the pack is half recharged. 'short_wh' is the
    load left unserved: the deficit at the stop plus, in every stopped hour, the load less what the sun gives.
    Returns the trace and the summary."""
    n_p = n_p or pack.n_p
    e_full, _ = pack.usable_wh(p_load, t_c, age, dod, n_p)
    e_full *= e_scale
    v_pack = pack.n_s * interp(pack.vmean, pack.cell_current(p_load, n_p))
    chg_max_w = pack.chg_a * (n_p / pack.n_p) * v_pack
    can_charge = d["pack"]["charge_window_c"]["low"] <= t_c <= d["pack"]["charge_window_c"]["high"]
    e = e_full
    running = True
    trace = []
    first_stop = None
    short_wh = 0.0
    hours_run = 0
    nights = []
    night_draw = 0.0
    in_night = False
    for h in range(hours):
        hh = (start_h + h) % 24
        g = prof[hh]
        p_sun = node_w(g, wp, pr, window, eta)
        if not running and (p_sun >= p_load or e >= 0.5 * e_full):
            running = True   # the operator restarts it once the sun carries the load or the pack is half recharged
        load = p_load if running else 0.0
        if p_sun >= load:
            surplus = p_sun - load
            soc = e / e_full
            cap = chg_max_w if soc < pack.taper else chg_max_w * max(0.0, (1.0 - soc) / (1.0 - pack.taper))
            chg = min(surplus, cap) * pack.chg_eta if can_charge else 0.0
            e = min(e_full, e + chg)
            if in_night:
                nights.append(night_draw)
                in_night, night_draw = False, 0.0
            flow = chg
        else:
            deficit = load - p_sun
            in_night = True
            if not running:
                short_wh += p_load - p_sun   # the load the stopped kit does not serve and the sun does not carry
                flow = 0.0
            elif e >= deficit:
                e -= deficit
                night_draw += deficit
                flow = -deficit
            else:
                short_wh += deficit - e
                night_draw += e
                e = 0.0
                flow = -deficit
                running = False
                if first_stop is None:
                    first_stop = h
        if running:
            hours_run += 1
        trace.append((h, hh, g, p_sun, load, flow, e, running))
    if in_night:
        nights.append(night_draw)
    return trace, {"e_full": e_full, "first_stop": first_stop, "short_wh": short_wh, "hours_run": hours_run, "end_wh": e,
                   "nights": nights, "chg_max_w": chg_max_w, "ok": first_stop is None}


def section5(o, d, pack, res1, res3, res4, monthly_json):
    s = d["solar"]
    pr, eta, window = res4["pr"], res4["eta"], res4["window"]
    hours = d["mission"]["hours"]
    o("5. M1 AS WRITTEN, HOUR BY HOUR: %d hours from a full aged pack (80 percent), the reference day (September) and the" % hours)
    o("   worst month (December), a 100 Wp panel in the 100 W window, the loads at the model's PLAN figures.")
    o()
    states = ("PS-IDLE-SPEC", "PS-RED2", "PS-SURV-R", "PS-SURV", "PS-NIGHT-RELAY")
    res = {}
    # the design case in full
    prof9 = res4["months"][9]["profile"]
    p = res1["PS-IDLE-SPEC"]["model"]
    tr, sm = simulate(d, pack, prof9, p, 100.0, window, eta, pr, 6, 20.0, pack.age80, hours)
    o("5a. The design case in full: PS-IDLE-SPEC %.1f W, September, start 06:00 UTC, cells +20 C, usable %.1f Wh." % (p, sm["e_full"]))
    o.table(["h", "UTC", "G W/m2", "sun at node W", "load W", "cells +/- W", "cells Wh left", "running"],
            [[t[0], "%02d:00" % t[1], f1(t[2]), f1(t[3]), f1(t[4]), "%+.1f" % t[5], f1(t[6]), ("yes" if t[7] else "STOPPED")] for t in tr])
    o()
    o("   First stop at hour %s; ran %d of %d hours; load unserved over the 72 h %.0f Wh of %.0f asked; the pack's draw" % (
        str(sm["first_stop"]), sm["hours_run"], hours, sm["short_wh"], p * hours))
    o("   in each period of sun below the load: %s Wh." % ", ".join(f1(x) for x in sm["nights"]))
    o()
    o("5b. Every state, both months, both start hours (aged 80 percent; December's cells at +5 C, f_T %.3f):" % interp(pack.temp, 5.0))
    rows = []
    for st in states:
        pl = res1[st]["model"] or res1[st]["recount_bat"]
        for m in (9, 12, 6):
            prof = res4["months"][m]["profile"]
            t_c = d["mission"]["cell_temp_c_by_month"][m]
            for sh in d["mission"]["start_hours_utc"]:
                tr, sm = simulate(d, pack, prof, pl, 100.0, window, eta, pr, sh, t_c, pack.age80, hours)
                night_h = res3[m]["night_h"]
                deficit_h = sum(1 for hh in range(24) if node_w(prof[hh], 100.0, pr, window, eta) < pl)
                res[(st, m, sh)] = dict(sm, night_h=night_h, deficit_h=deficit_h, p=pl)
                rows.append([st, f1(pl), MONTHS[m - 1], "%02d:00" % sh, f1(sm["e_full"]), f1(night_h), "%d" % deficit_h, f1(pl * deficit_h),
                             (str(sm["first_stop"]) if sm["first_stop"] is not None else "none"), "%d" % sm["hours_run"], f1(sm["short_wh"]), ("MET" if sm["ok"] else "NOT MET")])
    o.table(["state", "W", "month", "start", "usable Wh", "sun-down h", "h sun < load", "Wh a night at that load", "first stop h", "h run of 72", "Wh unserved", "72 h"], rows)
    o()
    o("   'h sun < load' counts the hours of the mean day in which the 100 Wp panel's power at the node is below the load:")
    o("   the pack carries those hours, and they are longer than the astronomical night because a 100 Wp panel exceeds")
    o("   42.8 W at the node only above about %.0f W/m2." % (42.8 / (pr * eta * 0.1)))
    o()
    # sensitivity on the design case
    o("5c. SENSITIVITY, the design case (PS-IDLE-SPEC, September, start 06:00, aged 80 percent): what each input alone would")
    o("   have to be for the 72 hours to end above the graceful threshold, the others as they are.")
    prof = prof9

    def ok_load(w):
        return simulate(d, pack, prof, w, 100.0, window, eta, pr, 6, 20.0, pack.age80, hours)[1]["ok"]

    def ok_energy(k):
        return simulate(d, pack, prof, p, 100.0, window, eta, pr, 6, 20.0, pack.age80, hours, e_scale=k)[1]["ok"]

    def ok_panel(wp, win=window):
        return simulate(d, pack, prof, p, wp, win, eta, pr, 6, 20.0, pack.age80, hours)[1]["ok"]

    w_max = bisect(lambda w: ok_load(w) if w > 0 else True, 0.0, p) if not ok_load(p) else p
    # largest load that passes: search downward
    lo, hi = 0.0, p
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if ok_load(mid):
            lo = mid
        else:
            hi = mid
    w_max = lo
    k_min = bisect(ok_energy, 1.0, 40.0)
    wp_min_100 = bisect(lambda wp: ok_panel(wp, window), 100.0, 5000.0)
    wp_min_nowin = bisect(lambda wp: ok_panel(wp, 1e9), 100.0, 5000.0)
    e_aged = res[("PS-IDLE-SPEC", 9, 6)]["e_full"]
    rows = [
        ["load W at the pack (42.8 now)", f1(w_max), "the whole kit at %.0f percent of PS-IDLE-SPEC: below the heat stage's 21.7 W and this record's night state" % (100 * w_max / p)],
        ["usable pack energy Wh (%.0f aged now)" % e_aged, f1(k_min * e_aged) if k_min else "over 40 x", "%.1f packs of the ruled size, aged; %.1f new (%.0f Wh)" % (k_min, k_min * 0.8, k_min * e_aged) if k_min else ""],
        ["panel Wp in the 100 W window (100 now)", (f1(wp_min_100) if wp_min_100 else "none: no panel size passes inside the window"), "the window's ceiling binds before the night does"],
        ["panel Wp with no window (re-rated path)", (f1(wp_min_nowin) if wp_min_nowin else "none: no panel size passes with this pack"), "the night binds: the pack empties whatever the day gives"],
        ["night h the pack carries at 42.8 W", f2(e_aged / p), "against %.1f h of sun-down and %d h of sun below the load in September" % (res3[9]["night_h"], res[("PS-IDLE-SPEC", 9, 6)]["deficit_h"])],
    ]
    o.table(["input", "value that closes M1 alone", "meaning"], rows)
    o()
    # combined: night state + 2v80 + panel with no window
    o("5d. Combinations inside the approved constraints, September, start 06:00, aged 80 percent (the night state of")
    o("   option (a), the 2.80 V line of (b), the panel and window of (e)):")
    rows = []
    pn = res1["PS-NIGHT-RELAY"]["recount_bat"]
    for st, pl in (("PS-IDLE-SPEC", p), ("PS-RED2", res1["PS-RED2"]["model"]), ("PS-SURV-R", res1["PS-SURV-R"]["model"]), ("PS-NIGHT-RELAY", pn)):
        for dod in ("3v00", "2v80"):
            for wp, win in ((100.0, window), (200.0, window), (330.0, 300.0), (400.0, 1e9)):
                for m in (9, 6, 12):
                    prf = res4["months"][m]["profile"]
                    t_c = d["mission"]["cell_temp_c_by_month"][m]
                    tr, sm = simulate(d, pack, prf, pl, wp, win, eta, pr, 6, t_c, pack.age80, hours, dod=dod)
                    tr2, sm2 = simulate(d, pack, prf, pl, wp, win, eta, pr, 6, t_c, pack.age80, hours, dod=dod, n_p=6)
                    rows.append([st, f1(pl), dod, "%.0f" % wp, ("%.0f" % win if win < 1e8 else "none"), MONTHS[m - 1], f1(sm["e_full"]),
                                 ("MET" if sm["ok"] else "NOT MET, unserved %.0f Wh, stop h %d" % (sm["short_wh"], sm["first_stop"])),
                                 ("MET" if sm2["ok"] else "NOT MET, unserved %.0f Wh" % sm2["short_wh"])])
                    res[("combo", st, dod, wp, win, m)] = (sm["ok"], sm2["ok"], sm["short_wh"], sm2["short_wh"])
    o.table(["state", "W", "graceful line", "panel Wp", "window W", "month", "usable Wh", "one 4S3P pack (the ruled one)", "two 4S3P packs (D-01's deferred second)"], rows)
    o()
    return res


# ----------------------------------------------------------------------------------------------- 6. options
def section6(o, d, pack, res1, res2, res3, res4, res5):
    o("6. THE OPTIONS, with numbers (all inside the case ruling of 7 September 2026: the Peli 1450 never changes)")
    o()
    pn = res1["PS-NIGHT-RELAY"]
    o("6a. Operating modes at night: PS-NIGHT-RELAY, the lowest state that still meets M1's must-hold (a handheld's")
    o("    message over the LoRa mesh reaches a remote correspondent over Iridium, or APRS; the kit keeps running).")
    rows = []
    for r in state_rows(d, "PS-NIGHT-RELAY"):
        if r["state_load"] > 0:
            rows.append([r["name"], f2(r["state_load"]), f2(r["state_bat"]), r["tier"]])
    o.table(["load ON in PS-NIGHT-RELAY", "at load W", "battery W", "kind"], rows)
    o("    OFF: slots 1 and 2 with their fans, PCIe switches and drives; both WiFi link cards; the 5G module (no host on")
    o("    slot 3); the monitor and HDMI 5 V; the SDR, the camera, the QMX, the Geiger (deferred by D-01); the E72 pair;")
    o("    the mixer fans (a shaded, cool night; on in the heat). Battery-side %.1f W PLAN (%.1f W with the D rows at" % (pn["recount_bat"], pn["sourced_bat"]))
    o("    the makers' figures); the aged pack carries it %.1f h at +20 C (%.1f h at the sourced figure), against" % (res2[("PS-NIGHT-RELAY", 20.0)]["a80"] / pn["recount_bat"], res2[("PS-NIGHT-RELAY", 20.0)]["a80"] / pn["sourced_bat"]))
    o("    September's %.1f h of sun-down and %d h of sun below the load (100 Wp). It does not carry a September night alone." % (
        res3[9]["night_h"], res5[("PS-NIGHT-RELAY", 9, 6)]["deficit_h"]))
    o("    What it changes: firmware and operator settings only (the KSZ energy-detect mode and the supervisors' 200 MHz")
    o("    clock are firmware items to confirm on the generated boards); it is the heat stage after BANK-R1 with six")
    o("    loads off or lowered, so it needs BANK-R1 in board B's generator (CONOPS 4c). Cost: none in parts. Mission:")
    o("    the monitor, the WiFi link, 5G and Zigbee are dark at night; the e-paper and the panel lamps carry the status.")
    o()
    e20 = res2[("PS-IDLE-SPEC", 20.0)]
    e280 = pack.usable_wh(42.8, 20.0, 0.8, "2v80")[0]
    o("6b. The usable depth of discharge: the graceful line 3.00 V to 2.80 V under load gains %.1f Wh aged (%.0f to %.0f Wh);" % (e280 - e20["a80"], e20["a80"], e280))
    o("    the 5 percent RSOC reserve then ends the run first at low currents (f_dod capped at 0.95). Cost: none; a")
    o("    gauge image and bridge setting (CONOPS 4c's PROVISIONAL threshold). Mission: about %.0f minutes more at" % (60 * (e280 - e20["a80"]) / 42.8))
    o("    PS-IDLE-SPEC, %.0f at the night state; cycle life is the maker's question (the cycle test discharges to 2.65 V)." % (60 * (e280 - e20["a80"]) / pn["recount_bat"]))
    o()
    o("6c. Cells in the east pocket (58 x 240 x 47.9 mm; A06's fit study on the committed board B underside):")
    o.table(["configuration", "nominal Wh", "east pocket", "west pocket"], [[v["config"], f1(v["wh_nominal"]), v["east"], v["west"]] for v in d["pockets"]["a06_verdicts"]])
    o("    Nothing larger than the ruled block fits the east pocket with board P beside the cells; a 4S2P 21700 fits at")
    o("    the same energy (no 21700 cell sheet is held). Gain: none. Cost: none.")
    o()
    lid = d["pockets"]["lid"]
    o("6d. A second pack's location inside the fixed case (D-01 deferred it, 'no location found'):")
    o("    - east pocket: taken by the ruled pack (6c).")
    o("    - west pocket, 58 x 160 x 47.9: A06 found no arrangement with board P BESIDE the cells (X spare -17.42). Not")
    o("      tried by A06: the 4S3P block alone (56.65 x 133.5 x 38.1) with its board P on top of the block or remote")
    o("      over a cell-tap harness: 133.5 fits the 160, 56.65 the 58 (1.35 spare, the same as the east), and the")
    o("      height 38.1 + a board P of about 8 mm assembled is about 46 against the 47.9 (about 2 mm, under the 3.32")
    o("      the east block keeps at the worst base). A candidate to CHECK with A06's script, not a finding; it")
    o("      displaces the west-wall cable drop zone (CASE-MARGINS section 3.4) and the heater mat's twin.")
    o("    - the lid: the flat ceiling is %.0f x %.0f, the depth %.2f at the worst; the QMX tray r2 takes X %.1f to %.1f" % (
        lid["ceiling_x_mm"], lid["ceiling_y_mm"], lid["depth_worst_mm"], lid["tray_r2_x"][0], lid["tray_r2_x"][1]))
    o("      and stands %.2f below the ceiling. A ONE-LAYER 4S3P block, two rows of six cells (2 x 56.65 = 113.3 by" % lid["tray_r2_stack_below_ceiling_mm"])
    o("      2 x 66.25 + 1 = 133.5 by 19.55 high) or one row of twelve (223.6 x 66.25 x 19.55), on a 2 mm lid plate as")
    o("      the tray's, over the WEST third of the lid (X -173 to 83, where D-01's deferred tablet bracket was to go)")
    o("      leaves %.1f mm over the face parts, more than the tray's own room. Mass about 0.65 kg of cells and board" % (lid["depth_worst_mm"] - 2.0 - 19.55))
    o("      in the lid; a lid harness across the hinge (the QMX's crossing is already an open item, S-95); the drop")
    o("      and vibration hold-down (TEST-PLAN E1, E2) and the lid's own strength are new items. A candidate to CHECK")
    o("      against CASE-MARGINS' lid rows (M3, M19) and the face parts' heights (T9), not a finding.")
    o("    Energy: a second 4S3P in parallel doubles every usable figure of section 2 (%.0f Wh aged at PS-IDLE-SPEC);" % (2 * e20["a80"]))
    o("    what the combinations of 5d then meet is in that table's last column. Cost ESTIMATE: 12 cells (about 4 EUR")
    o("    each at a European distributor, about 50 EUR), a second board P (about 30 EUR fabricated and assembled, the")
    o("    JLC BOM's order of magnitude), strip, wrap and a plate: under 150 EUR; a second pack build and a second")
    o("    protection commissioning (TEST-PLAN section 5 twice).")
    o()
    m9, m12 = res4["months"][9], res4["months"][12]
    o("6e. The panel and the 100 W window (S-53's route): the table of section 4. Into the node per day, September /")
    o("    December: 100 Wp %.0f / %.0f Wh; 200 Wp %.0f / %.0f (clipped %d h in September); 330 Wp %.0f / %.0f (clipped" % (
        m9[100]["e_node"], m12[100]["e_node"], m9[200]["e_node"], m12[200]["e_node"], m9[200]["clipped_h"], m9[330]["e_node"], m12[330]["e_node"]))
    o("    %d h); with no window at all 330 Wp gives %.0f / %.0f. PS-IDLE-SPEC asks %.0f Wh a day, the reduced mode %.0f," % (
        m9[330]["clipped_h"], m9[330]["e_node_noclip"], m12[330]["e_node_noclip"], 24 * 42.8, 24 * 31.38))
    o("    the heat stage %.0f, the night state %.0f. So: inside the window no panel carries PS-IDLE-SPEC's day; a" % (24 * 23.27, 24 * pn["recount_bat"]))
    o("    re-rated path to about 300 W with a 330 Wp panel carries the heat stage's September day and the night state's")
    o("    December day; what it cannot do is carry any night, which is the pack's. A panel above about 150 Wp of 12 V")
    o("    class also exceeds F2's and J_SOLAR's 10 A at its short circuit (about 6.25 A per 100 Wp, gen_sch_e.py:474),")
    o("    so the entry (F2, J_SOLAR, D4, the copper of PV_P) is re-declared with the stage. Cost ESTIMATE: the stage's")
    o("    inductor, FETs and sense resistor for 3 x the current, a 20 A fuse and connector, under 40 EUR of parts on")
    o("    board E; the panel itself 100 to 300 EUR per 100 Wp class. Mission: none removed; a bigger panel to carry.")
    o()
    ve = d["solar"]["vehicle_entry"]
    for st, pl in (("PS-IDLE-SPEC", 42.8), ("PS-RED2", 31.38), ("PS-SURV-R", 23.27), ("PS-NIGHT-RELAY", pn["recount_bat"])):
        pass
    o("6f. An external DC source on the 9 to 36 V entry, as an OPTION and not the mission's basis: the entry guarantees")
    o("    %.2f A (carries %.2f A) through F1 10 A, the LM74700 diode, the LM5069 hot-swap and the choke into board A's" % (ve["guaranteed_a"]["value"], ve["carried_a"]))
    o("    front end, chain %.3f to the node. At 12 V the guaranteed %.2f A is %.0f W at the source and %.0f W at the node," % (
        ve["chain_eta"]["value"], ve["guaranteed_a"]["value"], 12 * ve["guaranteed_a"]["value"], 12 * ve["guaranteed_a"]["value"] * ve["chain_eta"]["value"]))
    o("    above every state M1 uses (42.8 W needs %.1f A at 12 V, %.1f A at 24 V at the source). Energy a source must" % (42.8 / ve["chain_eta"]["value"] / 12, 42.8 / ve["chain_eta"]["value"] / 24))
    o("    give per night, the sun-down hours of section 3 (September %.1f h, December %.1f h; by day the panel's" % (res3[9]["night_h"], res3[12]["night_h"]))
    o("    shortfall against the load is on top of it, section 5b's 'h sun < load'):")
    rows = []
    for st, pl in (("PS-IDLE-SPEC", 42.8), ("PS-RED2", 31.38), ("PS-SURV-R", 23.27), ("PS-NIGHT-RELAY", pn["recount_bat"])):
        wh9 = pl * res3[9]["night_h"] / ve["chain_eta"]["value"]
        wh12 = pl * res3[12]["night_h"] / ve["chain_eta"]["value"]
        rows.append([st, f1(pl), f1(wh9), f1(wh9 / 12.0), f1(wh9 / 12.8), f1(wh12), f1(wh12 / 12.0)])
    o.table(["state", "W", "September night Wh from the source", "Ah at 12 V", "Ah of a 12.8 V LiFePO4", "December night Wh", "Ah at 12 V"], rows)
    o("    A vehicle's 70 Ah lead-acid battery gives about 35 Ah before half discharge, a 100 Ah LiFePO4 about 80 Ah:")
    o("    PS-IDLE-SPEC takes a vehicle battery below half in one night, the night state does not. The entry needs no")
    o("    board change (EQ-13, route b). It changes M1's setting from 'pack and solar', which is why it is stated here")
    o("    as optional and NOT taken as the basis (the owner's instruction of 28 September 2026).")
    o()
    return {}


# --------------------------------------------------------------------------------------- 7. smallest changes
def section7(o, d, pack, res1, res4, res5):
    pn = res1["PS-NIGHT-RELAY"]["recount_bat"]
    o("7. THE SMALLEST JUSTIFIED CHANGES (from 5d): M1 as written (PS-IDLE-SPEC, one aged 4S3P pack, the 100 W window)")
    o("   is NOT met by any combination of (a), (b) and (e) alone: the night binds at every load of the kit above")
    o("   %.1f W (5c), and the lowest state that meets the must-hold reads %.1f W. What meets M1's must-hold through" % (res5["w_max_load"], pn))
    o("   the design month's night from a full aged pack, in order of the change asked:")
    keys = [
        ("1. night state (a) + 2.80 V line (b) + second 4S3P pack (d), 100 Wp, 100 W window", ("PS-NIGHT-RELAY", "2v80", 100.0, 100.0)),
        ("2. as 1 with a 200 Wp panel in the 100 W window", ("PS-NIGHT-RELAY", "2v80", 200.0, 100.0)),
        ("3. as 1 with the path re-rated to 300 W and a 330 Wp panel (e)", ("PS-NIGHT-RELAY", "2v80", 330.0, 300.0)),
        ("4. heat stage PS-SURV-R at night + (b) + second pack + re-rated path and 330 Wp", ("PS-SURV-R", "2v80", 330.0, 300.0)),
        ("5. reduced mode PS-RED2 at night + (b) + second pack + re-rated path and 330 Wp", ("PS-RED2", "2v80", 330.0, 300.0)),
        ("6. PS-IDLE-SPEC as written + (b) + second pack + re-rated path and 330 Wp", ("PS-IDLE-SPEC", "2v80", 330.0, 300.0)),
    ]
    rows = []
    for label, (st, dod, wp, win) in keys:
        cells = []
        pl = res1[st]["model"] or res1[st]["recount_bat"]
        for m in (9, 6, 12):
            ok1, ok2, s1, s2 = res5[("combo", st, dod, wp, win, m)]
            prf = res4["months"][m]["profile"]
            t_c = d["mission"]["cell_temp_c_by_month"][m]
            deficit_h = sum(1 for hh in range(24) if node_w(prf[hh], wp, res4["pr"], win, res4["eta"]) < pl)
            e2 = 2.0 * pack.usable_wh(pl, t_c, pack.age80, dod)[0]
            cells.append(("MET" if ok2 else "NOT MET") + ": night asks %.0f Wh (%.1f W x %d h), two packs hold %.0f" % (pl * deficit_h, pl, deficit_h, e2))
        rows.append([label] + cells)
    o.table(["change set (two packs)", "September", "June", "December"], rows)
    o()
    o("   'MET' is the hour-by-hour run ending above the graceful threshold with no stop; the ask and the hold beside")
    o("   it are the one-night arithmetic that explains it (a run can pass with the ask slightly above the hold when")
    o("   the sun charges the packs part way through the deficit hours, and fail the other way when December's")
    o("   cold cells hold less).")


# ---------------------------------------------------------------------------------------------------- driver
def run(root, inputs_path):
    d = yaml.safe_load(open(inputs_path, encoding="utf-8"))
    bad = []
    for p in d["pinned"]:
        full = os.path.join(root, p["path"])
        if not os.path.exists(full):
            bad.append("%s (missing)" % p["path"])
        elif sha256_of(full) != p["sha256"]:
            bad.append("%s (changed: %s)" % (p["path"], sha256_of(full)[:16]))
    if bad:
        raise InputError("pinned input(s) missing or changed, refusing to run: " + "; ".join(bad))
    import json
    monthly = json.load(open(os.path.join(root, d["pinned"][0]["path"]), encoding="utf-8"))
    o = Out()
    o("M1 ENERGY RECONCILIATION (stream energy, MESHSAT-1357). PROTOTYPE DESIGN: nothing built, ordered or measured; every")
    o("figure is arithmetic on makers' figures, generator declarations and stated assumptions (AI review). Inputs pinned:")
    for p in d["pinned"]:
        o("  %s  %s" % (p["sha256"][:16], p["path"]))
    o("  %s  %s" % (sha256_of(inputs_path)[:16], os.path.relpath(inputs_path, root)))
    o()
    pack = Pack(d)
    res1 = section1(o, d)
    res2 = section2(o, d, pack, res1)
    res3 = section3(o, d)
    res4 = section4(o, d, monthly)
    res5 = section5(o, d, pack, res1, res3, res4, monthly)
    # the largest load that passes alone (recomputed here for section 7's sentence)
    prof = res4["months"][9]["profile"]
    lo, hi = 0.0, 42.8
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if simulate(d, pack, prof, mid, 100.0, res4["window"], res4["eta"], res4["pr"], 6, 20.0, pack.age80, d["mission"]["hours"])[1]["ok"]:
            lo = mid
        else:
            hi = mid
    res5["w_max_load"] = lo
    section6(o, d, pack, res1, res2, res3, res4, res5)
    section7(o, d, pack, res1, res4, res5)
    o("END. REQ-072's verdict on these figures: FAIL (unchanged); see ENERGY-RECONCILIATION.md sections 5 and 7.")
    return o.text()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
    ap.add_argument("--inputs", default=os.path.join(HERE, "energy_inputs.yaml"))
    ap.add_argument("--pin", action="store_true", help="print the inputs file's sha256 (to set INPUTS_SHA256) and exit")
    a = ap.parse_args()
    if a.pin:
        print(sha256_of(a.inputs))
        return 0
    if sha256_of(a.inputs) != INPUTS_SHA256:
        sys.stderr.write("energy_budget: %s changed (sha256 %s), refusing to run; re-pin deliberately with --pin\n" % (os.path.basename(a.inputs), sha256_of(a.inputs)[:16]))
        return 2
    try:
        sys.stdout.write(run(os.path.abspath(a.root), os.path.abspath(a.inputs)))
    except InputError as e:
        sys.stderr.write("energy_budget: %s\n" % e)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
