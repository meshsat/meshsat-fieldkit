#!/usr/bin/env python3
"""Record l9t5, P0-1 (MESHSAT-1357, 5 October 2026, Slot A of the P0 power closure): F01 / D-17, the all-transmit case C-ALLTX
rev 3, reproduced and three corrections compared inside the fixed requirements, one selected. PROTOTYPE DESIGN, DESK ARITHMETIC:
nothing in this kit has been built, bought, powered or measured; no figure printed here is a measurement.

What it does, from the repository root (python3 v2/docs/records/l9t5/l9t5_f01.py; stdlib, PyYAML, pdftotext; a few seconds):
  1. reproduces the failing case from this record's own l9t5_case.py (imported unchanged, pinned by sha256): 15.5162 V nominal,
     16.0718 V with the printed uncertainties bounded, against REQ-018's 15.5 V; and solves the PA's DC input the case allows;
  2. (a) A1, the VHF PA held to its 30 W service by a VGG loop on an RF detector, with the detector's accuracy obtained by a
     per-unit build calibration: the calibration's own uncertainty, term by term, and what it leaves unbounded;
  3. (b) the gauge's current term bounded by a per-pack calibration of the BQ4050 plus the dock contacts' printed maximum;
  4. (c) a PA drain-current loop: the module's drain current at the regulated PA rail is the controlled quantity, sensed on board A,
     closed through VGG on board D; its accuracy from printed limits, the case at the loop's upper corner, the service at its lower;
  5. the selection (SESSION, reason, reversal), 6. what stays open, 7. the predicates test_l9t5.py holds.
Labels: PRINTED (a maker's min or max column), TYPICAL (a maker's typical figure or curve), DECLARED (a generator's or record's
stated value), MODEL (arithmetic), ASSUMPTION (no held document gives it), MISSING (nothing held bounds it).
The committed output is regenerated only through _bin/regen_out.py.
"""
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l9t5_paloop as PL  # noqa: E402
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True

PINS = {
    "cx44": "v2/docs/records/l9t5/inputs/cx44-astra-f01-selection-as-received.md",
    "case_py": "v2/docs/records/l9t5/l9t5_case.py",
    "case_out": "v2/docs/records/l9t5/l9t5_case.out",
    "a1_out": "v2/docs/records/l9t5/l9t5_a1.out",
    "budget": "v2/docs/records/l9pwr/l9pwr_budget.py",
    "cases": "v2/docs/records/l9t5/inputs/coordinator-cases-2026-10-04-rev3.md",
    "ra30": "v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf",
    "bq4050": "v2/vendor/battery/ti-bq4050.pdf",
    "hojlr": "v2/vendor/passives/milliohm-hojlr2512-series.pdf",
    "millmax": "v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf",
    "precidip": "v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf",
    "xt60": "v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf",
    "ina250": "v2/vendor/ti/held/ti-ina250-sbos511c.pdf",
    "tlv758p": "v2/vendor/ti/ti-tlv758p.pdf",
    "tlv9062": "v2/vendor/ti/ti-tlv9062-op-amp.pdf",
    "lm5176": "v2/vendor/ti/lm5176-datasheet.pdf",
    "gen_a": "v2/ecad/tools/gen_sch_a.py",
    "gen_d": "v2/ecad/tools/gen_sch_d.py",
    "lcsc_fill": "v2/ecad/tools/lcsc_fill.py",
    "held_fetch": "v2/docs/records/l4e7/fetch_held_back.py",
    "paloop": "v2/docs/records/l9t5/l9t5_paloop.py",
    "wsl": "v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf",
    "csd18510": "v2/vendor/battery/ti-csd18510q5b.pdf",
    "ina226": "v2/vendor/ti/ti-ina226.pdf",
}
HELD = ("ina250",)        # gitignored maker's sheet: record l4e7's fetch_held_back.py fetches it and checks its sha256

# ---- the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
I_SVC_W = 30.0                       # W: the PA's service output (CHO-001: "SA868 with a RA30H1317M1 30 W stage")
T_HI, T_LO, T_REF = 85.0, -20.0, 25.0  # C: board A's air bound for the loop's parts (L4-E12's 76.25 C under it) and the cold end
# (c) the loop's design values and its printed-limit arithmetic live in l9t5_paloop.py (one source for this script, the case,
# the drafts and the netlist check); imported below
# (a) A1's calibration terms that no held document gives, shown so the reader sees their size (ASSUMPTION each)
A1_DIR_DB, A1_VSWR = 20.0, 3.0       # a board coupler's directivity and the RA30H1317M1's stability-row load VSWR 3:1 (PRINTED row)
# (b) the gauge's calibration
CAL_REF = 0.002                      # the calibration reference's accuracy, fraction of 18 A (ASSUMPTION; l9t5_case.py's CAL_REF)
CAL_T = 25.0                         # C: the calibration's temperature (ASSUMPTION)
P_AIR = 76.25                        # C: board P's air taken as L4-E12's inside air (ASSUMPTION; record l9stk carries P's own)
R10_RTH = 100.0 / 3.0                # K/W: from HoJLR2512's power curve (3 W to 70 C, zero at 170 C): MODEL


def rel(p):
    return os.path.join(ROOT, p)


def refuse(msg):
    sys.stderr.write("l9t5_f01: REFUSED: %s\n" % msg)
    sys.exit(2)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


_PDF = {}


def pdf(key):
    if key not in _PDF:
        p = rel(PINS[key])
        if not os.path.isfile(p):
            refuse("%s is not in the tree%s" % (PINS[key], " (held back: run v2/docs/records/l4e7/fetch_held_back.py)" if key in HELD else ""))
        r = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True)
        if r.returncode != 0:
            refuse("pdftotext could not read %s" % PINS[key])
        _PDF[key] = r.stdout.decode("utf-8", "replace")
    return _PDF[key]


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern no longer matches its pinned input" % what)
    return m


def load(key, name):
    sp = importlib.util.spec_from_file_location(name, rel(PINS[key]))
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ the makers' printed rows
def read():
    S = {}
    S.update(PL.read_sheets())                  # INA250A2, TLV758P, TLV9062, LM5176: l9t5_paloop.py
    # the RA30H1317M1 (Mitsubishi, October 2011)
    t = pdf("ra30")
    m = need(t, r"Pout>(\d+)W, .T>(\d+)% @ VDD=([\d.]+)V, VGG=5V, Pin=50mW", "the RA30 printed minimum")
    S["pa_pmin"], S["pa_eta"], S["pa_vdd"] = float(m.group(1)), float(m.group(2)) / 100, float(m.group(3))
    S["pa_pmax_rating"] = float(need(t, r"Pout\s+Output Power\s+f=135-175MHz, VGG<5V\s+(\d+)\s+W", "the 45 W rating").group(1))
    need(t, r"ELECTRICAL CHARACTERISTICS \(Tcase=\+25°C", "the RA30 table's 25 C condition")
    m = need(t, r"At Pout=(\d+)W, VDD=([\d.]+)V and Pin=50mW each stage transistor operating conditions are:", "the heat-sink example")
    ex = t[m.end():m.end() + 900]
    s1 = need(ex, r"^\s*1\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", "stage 1's row")
    s2 = need(ex, r"^\s*2\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", "stage 2's row")
    S["pa_ex_idd"] = float(s1.group(4)) + float(s2.group(4))
    S["pa_ex_vdd"] = float(m.group(2))
    need(t, r"Pout<30W \(VGG control\), Load VSWR=3:1", "the RA30 stability row (VGG control)")
    need(t, r"The output power and drain current increase as the gate voltage\s*\n?\s*increases\.", "the RA30 description: Pout and IDD rise with VGG")
    # the gauge (TI BQ4050 SLUSC67B 6.14) and its shunt (Milliohm HoJLR2512, the tree's R10 part)
    g = pdf("bq4050")
    sec = need(g, r"^6\.14 Electrical Characteristics: Coulomb Counter.*?^6\.15", "BQ4050 6.14", re.M | re.S).group(0)
    need(sec, r"Gain error\s+15-bit \+ sign, over input voltage range\s+±[\d.]+%\s+±[\d.]+%\s+FSR", "the gain error row (no post-calibration figure)")
    S["g_cal_rows"] = re.findall(r"(Offset error(?: drift)?)\s+\S+(?: \+ sign)?, Post-calibration", sec)
    t = pdf("hojlr")
    S["r10_tcr"] = float(need(t, r"±(\d+) \(2mR~500mR\)", "HoJLR2512 TCR").group(1)) * 1e-6
    need(text("lcsc_fill"), r'\(r"\^2mOhm 1% 2512", "R_2512"\): "C2903471",\s+# HoJLR2512-3W-2mR-1%', "R10's part in lcsc_fill.py")
    # the dock's power contacts (Mill-Max) and the Preci-Dip 813 signal contacts
    t = pdf("millmax")
    need(t, r"Contact Resistance:", "the Mill-Max contact resistance row")
    t = pdf("precidip")
    S["pd_i"] = float(need(t, r"OPERATING CURRENT\s+Max\. ([\d.]+) A", "Preci-Dip 813 current").group(1))
    S["pd_r"] = float(need(t, r"CONTACT RESISTANCE\s+(\d+) m. \(static measurement, halfway position\)", "Preci-Dip 813 resistance").group(1)) * 1e-3
    t = pdf("xt60")
    S["xt60_r"] = float(need(t, r"≤([\d.]+)mΩ", "XT60 2021V1 contact resistance").group(1)) * 1e-3
    # board A (U13's divider, R55, +5V_D8IN, J_MEZZ1 pin 16) and board D (VGG, R82, R83) as drawn
    a = text("gen_a")
    need(a, r'lm5176\("PA", "U13", "VBAT", "\+13V8_PA", "PA_EN", "162k"', "U13's FB top resistor")
    need(a, r'rfb_val="10k 1%"', "the LM5176 helper's FB bottom resistor")
    need(a, r'isns="6m", isns_lcsc="C843882"', "U13's 6 mOhm ISNS shunt R55")
    m = need(a, r"LM5176 minimum average limit is ([\d.]+) A with initial \+/-1 percent, or ([\d.]+) A with the assumed (\d+) K shunt temperature change and \+/-(\d+) ppm/K TCR", "the generator's shunt TCR assumption")
    S["isns_dt"], S["isns_tcr"] = float(m.group(3)), float(m.group(4)) * 1e-6
    need(a, r'_intent\.rail\("\+5V_D8IN", 5\.0, 1\.0, 2\.0, "L13", loads=\{"U23": 1\.0\}, switch="U41"', "+5V_D8IN as drawn")
    need(a, r'"15": "ZEROIZE_HW", "16": "AB_SPARE"\}\)', "J_MEZZ1 pin 16, the spare conductor")
    d = text("gen_d")
    need(d, r'r\("R82", "71\.5k 1%", "VGG_SW", "VGG_FB"', "board D's R82")
    need(d, r'r\("R83", "10\.0k 1%", "VGG_FB", "GND"', "board D's R83")
    need(d, r'"15": "ZEROIZE_HW", "16": "AB_SPARE"\}\)', "J_HARN1 pin 16, the spare conductor")
    need(text("held_fetch"), r'"v2/vendor/ti/held/ti-ina250-sbos511c\.pdf"', "record l4e7's fetch of the INA250 sheet")
    return S


def text(key):
    p = rel(PINS[key])
    if not os.path.isfile(p):
        refuse("%s is not in the tree" % PINS[key])
    return open(p, encoding="utf-8").read()


# ------------------------------------------------------------------------------------------------ the computation
def compute():
    for k, p in PINS.items():
        if not os.path.isfile(rel(p)):
            refuse("pinned input %s (%s) is missing%s" % (k, p, " (held back: v2/docs/records/l4e7/fetch_held_back.py)" if k in HELD else ""))
    S = read()
    case_mod = load("case_py", "l9t5_case_for_f01")
    C = case_mod.compute()                                    # the record's own case, unchanged
    m = case_mod.budget_module()
    B = m.compute()
    pb, F, D = B["d11_rv_record"], B["F"], B["cfgs"]["DRAFTED"]
    vals = dict(B["calltx"]["vals"])
    U, I = C["U"], C["in"]
    I18, V = m.CASE_I, m.CASE_V_REST
    pins_rt = 2 * I["pin_max"] / I["pin_n"]
    rx = max(0.0, pins_rt - I["w2"][4])                       # the dock contacts at their printed maximum over W2's inferred figure
    gu = U["gauge_uncal"]
    R = {"S": S, "C": C, "rx": rx, "gu": gu, "V": V, "I": I18, "pins": {k: (p, sha(p)) for k, p in PINS.items()}}

    def row(pa=None, gi=0.0, r_extra=0.0, rc=None, eff=None, vv=None):
        v = dict(vals if vv is None else vv)
        if pa is not None:
            v["VHF PA 30 W"] = pa
        return m.case_row(pb, F, D, v, i=I18 - gi, r_extra=r_extra, r_cell=rc, eff_over=eff)

    def solve(fn, lo, hi, target=V):
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if fn(mid) > target:
                hi = mid
            else:
                lo = mid
        return lo

    # ---- 1. reproduce, and the PA's DC the case allows
    R["nom"], R["bnd"] = C["case"], U["comb_printed"]
    R["pa_now"] = vals["VHF PA 30 W"]
    R["pa_allow_nom"] = solve(lambda p: row(p)["need"], 40.0, 130.0)
    R["pa_allow_bnd"] = solve(lambda p: row(p, gu, rx)["need"], 40.0, 130.0)
    R["pa_stage_eta"] = C["case"]["nodes"]["PA"][3]

    # ---- 2. (a) A1 with the detector calibrated per unit
    A = {}
    A["db"] = [(db, I_SVC_W * 10 ** (2 * db / 10.0)) for db in (0.25, 0.5)]
    A["eta_need"] = [(db, p / R["pa_allow_bnd"]) for db, p in A["db"]]      # the PA efficiency the bounded case needs at the high end
    gam = (A1_VSWR - 1) / (A1_VSWR + 1)
    k = gam * 10 ** (-A1_DIR_DB / 20.0)
    A["dir_db"] = (20 * math.log10(1 + k), 20 * math.log10(1 - k))
    R["A"] = A

    # ---- 3. (b) the gauge calibrated per pack
    Bc = {}
    fsr = I["g_vref1"] / I["g_fsr_div"]
    dt_g = P_AIR - CAL_T
    r10_rise = (I18 ** 2) * I["r10"] * R10_RTH
    dt_r10 = P_AIR + r10_rise - CAL_T
    terms = [("the calibration reference, ASSUMPTION %.1f %% of %.0f A (no instrument is held)" % (100 * CAL_REF, I18), CAL_REF * I18),
             ("integral nonlinearity, PRINTED %.1f LSB of %.2f uV (calibration does not remove it)" % (I["g_inl"], I["g_lsb"] * 1e6), I["g_inl"] * I["g_lsb"] / I["r10"]),
             ("offset, PRINTED %.0f uV post-calibration" % (I["g_off"] * 1e6), I["g_off"] / I["r10"]),
             ("gain drift, PRINTED %.0f ppm/K from a %.0f C calibration to board P's %.2f C air (ASSUMPTION: P at L4-E12's air), %.2f K" % (I["g_drift"] * 1e6, CAL_T, P_AIR, dt_g), I["g_drift"] * dt_g * I18),
             ("offset drift, PRINTED %.1f uV/K over the same %.2f K" % (I["g_off_drift"] * 1e6, dt_g), I["g_off_drift"] * dt_g / I["r10"]),
             ("R10's TCR, PRINTED +-%.0f ppm/K (HoJLR2512), over %.1f K: the air plus its own %.1f K at %.3f W (MODEL, its power curve)" % (S["r10_tcr"] * 1e6, dt_r10, r10_rise, I18 ** 2 * I["r10"]), S["r10_tcr"] * dt_r10 * I18)]
    Bc["terms"] = terms
    Bc["cal"] = math.fsum(x for _l, x in terms)
    Bc["row_cal"] = row(None, Bc["cal"], rx)
    Bc["row_zero"] = row(None, 0.0, rx)
    Bc["row_zero_nom"] = row(None, 0.0, 0.0)
    R["B"] = Bc

    # ---- 4. (c) the drain-current loop, round 2 of the selection (l9t5_paloop.cap: every term labelled)
    L = PL.cap(S)
    loop_w = L["supply_a"] * PL.V5[1] / 0.90            # W at VBAT: the loop's own supply through U41 (declared 0.90), MODEL
    L["loop_w"] = loop_w

    def rowc(pa, gi=0.0, r_extra=0.0, rc=None, eff=None, vv=None):
        r_ = row(pa, gi, r_extra, rc, eff, vv)
        r_ = dict(r_)
        r_["need"] = r_["need"] + loop_w / r_["i"]          # the loop's supply added at VBAT, first order (1 mV class)
        return r_
    L["bnd_drawn"] = rowc(L["p_max_drawn"], gu, rx)
    L["nom"] = rowc(L["p_max"])
    L["bnd"] = rowc(L["p_max"], gu, rx)
    L["bnd_r07"] = rowc(L["p_max"], gu, rx, rc=0.07)
    L["bnd_r08"] = rowc(L["p_max"], gu, rx, rc=0.08)
    L["bnd_eff"] = rowc(L["p_max"], gu, rx, eff={"PA": 0.95, "S1": 0.85, "S2": 0.85, "S3": 0.85, "DEV": 0.85})
    v8 = dict(vals)
    for s_ in (1, 2, 3):
        v8["CM5 slot %d" % s_] = 8.0
    L["bnd_m8"] = rowc(L["p_max"], gu, rx, vv=v8)
    L["bnd_d11"] = rowc(L["p_max"], gu, rx, vv=dict(B["calltx"]["basis_vals"]))
    L["bnd_all"] = rowc(L["p_max"], gu, rx, rc=0.08, eff={"PA": 0.95, "S1": 0.85, "S2": 0.85, "S3": 0.85, "DEV": 0.85})
    L["rx_cover"] = solve(lambda r: rowc(L["p_max"], gu, rx + r)["need"], 0.0, 0.2)
    L["rc_cover"] = solve(lambda r: rowc(L["p_max"], gu, rx, rc=r)["need"], 0.0, 0.3)
    L["path_rest"] = [("the pack lead's XT60, two contacts at the PRINTED %.1f mOhm maximum (Amass 2021V1, new: aged MISSING)" % (S["xt60_r"] * 1e3), 2 * S["xt60_r"]),
                      ("12 AWG pack lead, 2 x 150 mm at 85 C (ASSUMPTION: length; 5.21 mOhm/m at 20 C, copper)", 2 * 0.150 * 5.21e-3 * (1 + 0.00393 * 65)),
                      ("board bands, 2 x 200 mm at record l9stk 14.4's section (MODEL; the layout's lengths are not known)", 2 * 0.200 * 1.582e-3 / 0.1 / 2)]
    L["path_rest_sum"] = math.fsum(x for _l, x in L["path_rest"])
    L["bnd_rest"] = rowc(L["p_max"], gu, rx + L["path_rest_sum"])
    L["gshift"] = PL.ground_shift_bound()
    L["rest"] = PL.rest_top(S)
    L["band"] = PL.vgg_band(S, gnd_shift=PL.GND_SHIFT, rest_hi=L["rest"])
    L["band_drawn"] = PL.vgg_band(S, r83=10.0e3, rinj=1e18, gnd_shift=0.0, rest_hi=0.0)
    L["dyn"], L["fall"], L["ramp_t"], L["exc"] = PL.dynamics(S)
    # the service overlap: the maker's 30 W design condition (an EXAMPLE at the printed minimum efficiency, 25 C, 12.5 V, VGG 5 V, full
    # drive) against the cap's least current; and the efficiency the cap's least needs at the module's terminals
    L["svc_i_ex"] = S["pa_ex_idd"]
    feed_r = S["ina_rpkg"] + 2 * 0.020 + 2 * 0.150 * 13.17e-3 * 1.25     # INA250 (TYPICAL), J_PA's VH contacts (20 mOhm after test), 16 AWG
    L["feed_r"] = feed_r
    L["vdd_term"] = (L["vpa"][0] - L["i_min"] * feed_r, L["vpa"][2])
    L["svc_eta_need"] = I_SVC_W / (L["vdd_term"][0] * L["i_min"])
    L["svc_eta_need_hi"] = I_SVC_W / (L["vdd_term"][1] * L["i_min"])
    L["svc_margin"] = L["i_min"] / L["svc_i_ex"] - 1
    # what the case would allow if U13's own limit and J_PA did not bind (the room a redesign route has)
    L["i_case_max"] = R["pa_allow_bnd"] / L["vpa"][2]
    L["heat_now"] = R["pa_now"] - I_SVC_W
    L["heat_c"] = L["p_max"] - I_SVC_W
    R["L"] = L
    R["sel"] = "c"
    R["pred"] = predicates(R)
    return R


def predicates(R):
    S, C, A, Bc, L = R["S"], R["C"], R["A"], R["B"], R["L"]
    V = R["V"]
    P = {}
    P["1a: the case reproduces at 15.5162 V nominal and 16.0718 V bounded on this base"] = abs(R["nom"]["need"] - 15.5162) < 5e-5 and abs(R["bnd"]["need"] - 16.0718) < 5e-5
    P["1a: both exceed REQ-018's 15.5 V (F01 / D-17 OPEN before any correction)"] = R["nom"]["need"] > V and R["bnd"]["need"] > V
    P["(a): A1's case rests on the PA's efficiency at the loop's high end, which no row prints (it needs more than 32 percent)"] = all(e > 0.32 for _db, e in A["eta_need"])
    P["(b): a gauge with zero error and the path as inferred still needs more than 15.5 V (b cannot close the case alone)"] = Bc["row_zero_nom"]["need"] > V and Bc["row_zero"]["need"] > V
    P["(b): the calibrated residual leaves the case over 15.5 V"] = Bc["row_cal"]["need"] > V
    P["(c): U13's BIAS (gate drive) would take more than the cap's room under U13's limit if it stayed behind R55"] = L["bias"][0] > L["u13_min"] - L["i_max"]
    P["(c): with BIAS on PA_OUT, the cap's top plus R55's other loads stays under U13's own loop minimum (hot shunt, printed TCR)"] = L["i_max"] + L["r55_other"] < L["u13_min"]
    P["(c): the band on the PRINTED rows alone (no ASSUMPTION or TYPICAL term) lies inside the band with them"] = (
        L["i_min"] < L["i_min_printed_only"] < L["i_max_printed_only"] < L["i_max"] and L["vset_printed"][0] > L["vset"][0])
    P["(c): B-PA1's pass limit is at or under the band's calculated floor (rounded down, cx46)"] = L["bpa1_limit"] <= L["i_min"]
    P["(c): Q551's held load is stated apart from the steady load and carried to V-PA-REF and B-PA2, not into the steady band (cx46)"] = (
        L["ref_held"] > L["ref_load"][1])
    P["(c): the cap's top is under the INA250's 15 A continuous rating"] = L["i_max"] < S["ina_imax"]
    P["(c): the case at the cap's top meets 15.5 V with the gauge bound, the dock contacts' maximum and the loop's own supply"] = L["bnd"]["need"] < V
    P["(c): the margin there is at least 0.2 V"] = V - L["bnd"]["need"] >= 0.2
    P["(c): with the rest of the path at its illustrated bound it still meets 15.5 V"] = L["bnd_rest"]["need"] < V
    P["(c): the overlap rests on the maker's EXAMPLE (6.0 A): the cap's least is over it, and no printed row bounds the transfer"] = L["i_min"] > L["svc_i_ex"]
    P["(c): the PA's DC at the cap's top is under what the bounded case allows"] = L["p_max"] < R["pa_allow_bnd"]
    P["(c): board D's open-loop VGG top stays under 5 V with the ground shift and the loop at rest"] = L["band"][2] < 5.0 and L["gshift"] < PL.GND_SHIFT
    P["(c): the loop's authority takes VGG under 3.5 V"] = L["band"][3] < 3.5
    P["(c): the reference's load lies within 2 % of its 1 mA test condition and its residual (10 x TYPICAL, ASSUMPTION) under 0.01 % of PA_ISET"] = (
        L["ref_dI"] < 2e-5 and L["ref_resid"] < 1e-4 * L["vset"][1])
    P["(c): R553's and R559's corners widen the band (cx45 Q1)"] = L["i_min"] < L["i_min_nores"] and L["i_max"] > L["i_max_nores"]
    P["(c): the INA250's junction at the inside air and the cap's top is under its 125 C specified range (TYPICAL RthJA)"] = L["ina_tj"] < 125.0
    P["(c): the set point's ramp (3 tau) outlasts K1's 3 ms operate time, so the drive arrives under a low set point"] = L["ramp_t"] > 0.003
    P["selection: (c), PROVISIONAL on B-PA1 (F01's row is PROVISIONAL, never closed on printed limits)"] = R["sel"] == "c"
    P["(c): every modelled excursion under a load step ends inside the breaker's 0.282 ms least timer (MODEL, TYPICAL plant)"] = max(t for _k, _d, t in L["exc"]) < 0.282e-3
    return P


# ------------------------------------------------------------------------------------------------ render
def render(R):
    S, C, A, Bc, L = R["S"], R["C"], R["A"], R["B"], R["L"]
    V, I18 = R["V"], R["I"]
    out = []
    w = out.append
    w("l9t5_f01: P0-1, F01 / D-17 on C-ALLTX rev 3 (record l9t5, Slot A of the P0 power closure, MESHSAT-1357, 5 October 2026). PROTOTYPE")
    w("DESIGN, DESK ARITHMETIC: nothing has been built, bought, powered or measured. Labels: PRINTED (a maker's min or max), TYPICAL, DECLARED,")
    w("MODEL, ASSUMPTION, MISSING.")
    w("")
    w("0. PINS (path  sha256/16; the INA250 sheet is held back, fetched and checked by record l4e7's fetch_held_back.py, never committed)")
    for k, (p, s) in sorted(R["pins"].items()):
        w("   %-10s %s  sha256 %s" % (k, p, s))
    w("")
    w("1. THE FAILING CASE, REPRODUCED (1a): this record's l9t5_case.py imported unchanged on this base")
    w("   C-ALLTX rev 3 from its text: %.3f W at VBAT, need %.4f V rest at %.0f A (R_cell %.3f Ohm, the case's ASSUMPTION): %+.4f V over REQ-018's %.1f V" % (
        R["nom"]["p"], R["nom"]["need"], I18, R["nom"]["r_cell"], R["nom"]["need"] - V, V))
    w("   with the printed uncertainties bounded (the BQ4050's uncalibrated %.4f A, so %.4f A true at the indicated %.0f A; the dock's Mill-Max power" % (R["gu"], I18 - R["gu"], I18))
    w("   pins at their PRINTED 20 mOhm maximum, %+.1f mOhm over W2's inferred leads and contacts): need %.4f V (%+.4f V)" % (R["rx"] * 1e3, R["bnd"]["need"], R["bnd"]["need"] - V))
    w("   the PA's DC input the case allows, the rest unchanged (MODEL): %.2f W nominal, %.2f W bounded; today's HIGH is %.1f W (the %.0f W rating" % (
        R["pa_allow_nom"], R["pa_allow_bnd"], R["pa_now"], S["pa_pmax_rating"]))
    w("   at the %.0f %% PRINTED minimum efficiency); the PA stage U13 converts at %.4f from VBAT in the budget (the 12 V curve, NOT PLOTTED at 13.8 V)" % (
        100 * S["pa_eta"], R["pa_stage_eta"]))
    w("   so the whole deficit sits in one number nothing in the drawn design bounds: the PA's DC input, today set by an open-loop VGG")
    w("")
    w("2. (a) A1 WITH THE DETECTOR CALIBRATED PER UNIT (the loop holds RF output; the case is judged in DC watts)")
    w("   what the calibration must establish, term by term (the loop's half-tolerance tiers of round 2: +-0.25 and +-0.5 dB):")
    w("     the reference power meter's own accuracy at 144 to 146 MHz and 30 to 38 W: ASSUMPTION (no instrument or its certificate is held)")
    w("     the detector's drift NOT removed by calibration: a two-temperature calibration removes offset and slope at two points only; the")
    w("       curvature between and beyond them is printed by no sheet (record l9t5_a1.out: ADL5902, ADL5513, LMH2110, LTC5582 print temperature")
    w("       deviation as TYPICAL only), and board D's U22 reads the PA flange on a lead, not the detector's die: MISSING")
    w("     the sampler (coupler) under a field antenna's mismatch: forward-power error +%.2f / %.2f dB at the sheet's 3:1 stability-row VSWR with a" % A["dir_db"])
    w("       %.0f dB directivity (ASSUMPTION: no coupler is held or designed); calibration into 50 Ohm does not remove it" % A1_DIR_DB)
    w("     the set point and the error amplifier: printable once drawn (small); the detector's supply on board D: the ADL5902 needs 4.5 V,")
    w("       over +5V_D8's 4.3408 V floor (record s99a), the ADL5513 runs from 3.3 V on TYPICAL rows only")
    w("     THE CONVERSION TO THE CASE'S QUANTITY: the loop bounds RF watts; the case is DC watts. The bounded case allows %.2f W of PA input, so" % R["pa_allow_bnd"])
    for db, e in A["eta_need"]:
        w("       at +-%.2f dB (Pout at most %.2f W) the PA must convert at %.1f %% or better at that point" % (db, I_SVC_W * 10 ** (2 * db / 10.0), 100 * e))
    w("       the sheet prints %.0f %% only at Tcase 25 C, VDD %.1f V, VGG 5 V, Pin 50 mW (full drive); at VDD 13.8 V under VGG control, hot, no row: MISSING" % (
        100 * S["pa_eta"], S["pa_vdd"]))
    w("   VERDICT (a): at most a PROVISIONAL choice, as (c) is (section 5 judges both on one standard). The calibration's residual (drift")
    w("     curvature, the sampler under mismatch) and the PA's efficiency at the controlled point are each bounded by nothing held; its supplier")
    w("     tasks would be two (the detector chain's residual over the envelope; the PA's DC input at the loop's high end, limit under %.2f W at RF" % R["pa_allow_bnd"])
    w("     over 30 W), and the second sits on the failing case itself. Ranked second.")
    w("")
    w("3. (b) THE GAUGE CALIBRATED PER PACK, THE DOCK CONTACTS BOUNDED FROM A PRINTED FIGURE")
    w("   SLUSC67B 6.14 prints no post-calibration gain row: the calibration (bqStudio's routine, the TRM's) replaces the %.1f %% FSR gain error and" % (100 * C["in"]["g_gain"]))
    w("   R10's 1 %% tolerance by its reference; what it leaves (%s are the only post-calibration rows):" % " and ".join(sorted(set(S["g_cal_rows"]))))
    for lab, x in Bc["terms"]:
        w("     %-132s %.4f A" % (lab, x))
    w("     one-sided residual %.4f A: need %.4f V with the dock contacts at their maximum" % (Bc["cal"], Bc["row_cal"]["need"]))
    w("   the dock contacts: the power pins are Mill-Max (the energy chain's DOCK_BLOCK: 20 mOhm max, PRINTED; four in parallel each way), already")
    w("     in the bound; the Preci-Dip 813 sheet is the dock's SIGNAL contacts (%.0f mOhm, no min or max column, %.1f A maximum operating current)," % (S["pd_r"] * 1e3, S["pd_i"]))
    w("     which carry none of the 18 A")
    w("   a PERFECT gauge (zero error): need %.4f V with the dock contacts at their maximum, %.4f V with W2's inferred path" % (Bc["row_zero"]["need"], Bc["row_zero_nom"]["need"]))
    w("   VERDICT (b): CANNOT CLOSE THE CASE ALONE. Even zero gauge error leaves the case's own nominal deficit (%+.4f V); the calibration is a" % (Bc["row_zero_nom"]["need"] - V))
    w("     means of shrinking a bound, not a correction of the circuit's demand. Not needed by (c) below, so not proposed as a prerequisite.")
    w("")
    w("4. (c) A PA DRAIN-CURRENT LOOP, ROUND 2 OF THE SELECTION (after cx44's NOT SUPPORTED, the first negative, kept as given)")
    w("   the circuit (to be drafted in 1c): board A: U551 INA250A2 (2 mOhm integrated shunt, 500 mV/A) in series from +13V8_PA to J_PA, VS on")
    w("     +5V_D8IN; U552 TLV758P set point PA_ISET (R551 %.2fk over R552 %.0f Ohm at 0.1 %%: %.4f V nominal, a %.2f mA preload, the sheet's IOUT = 1 mA" % (
        PL.R_SET_TOP / 1e3, PL.R_SET_BOT, L["vset"][1], L["ref_preload"] * 1e3))
    w("     test condition); R559 1k and C557 10 uF ramp it into PA_ISP, held at 0 V by Q551 (2N7002) while OUTLET_OK is high (the PA not keyed;")
    w("     OUTLET_OK = NOT (TR_APRS AND PA_EN) is U30's, drawn), so at each key the set point rises from zero (3 tau = %.0f ms, longer than K1's" % (L["ramp_t"] * 1e3))
    w("     3 ms operate time: the RF drive arrives under a low set point and the current approaches the cap from below); U553 TLV9062: half A")
    w("     integrates PA_IMON against PA_ISP (R553 10k, C554 10 nF), R560 470k into its summing node winds it down while held, half B inverts it")
    w("     about PA_MID, so PA_ILIM rests at 0 V under the set point; R558 1k into J_MEZZ1 pin 16 (AB_SPARE); U13's FB divider at 0.1 % (fb01's")
    w("     keyword) and U13's BIAS re-tapped from +13V8_PA to PA_OUT, ahead of R55. Board D: R57 110k from PA_ILIM into VGG_FB, R83 to 11.0k")
    w("     (R83 // R57 = 10.0k), C76 1 nF, and R58 470 Ohm from VGG_SW to ground: U15 (an LDO) cannot sink, so VGG's fall needs a defined bleed")
    w("   R55 CARRIES MORE THAN THE PA (cx44): U13's BIAS (pin 24) sits on +13V8_PA behind R55 as drawn and takes VCC's power above 8 V (LM5176")
    w("     SNVSAI1D 7.3.2): four CSD18510Q5B at VCC's %.2f V top, Qg read between the PRINTED %.0f nC (4.5 V) and %.0f nC (10 V) maxima (MODEL:" % (
        S["lm_vcc"][2], S["fet_qg45"] * 1e9, S["fet_qg10"] * 1e9))
    w("     linear between them) = %.1f nC, at fSW's PRINTED %.0f kHz maximum scaled to RT 40.2k = %.1f kHz, plus the %.0f mA operating current: %.4f A," % (
        L["bias"][1] * 1e9, S["lm_fsw"][2] / 1e3, L["bias"][2] / 1e3, S["lm_iop"] * 1e3, L["bias"][0]))
    w("     more than the %.4f A between the cap's top and U13's limit: BIAS moves to PA_OUT (a node over 8 V ahead of the shunt). R55 then carries" % (
        L["u13_min"] - L["i_max"]))
    for lab, x in L["r55_terms"]:
        w("       %-104s %.6f A" % (lab, x))
    w("       together %.6f A beside the PA's feed" % L["r55_other"])
    w("   the cap's band, every term (I = (PA_ISP (1 + R553/R560) - V+ R553/R560 + VOS) / (G (1 + gain error)) - IOS, at the corners together):")
    w("     V_SET (TLV758P %s): VFB %.2f V +-%.0f %% PRINTED for TJ -40 to 85 C (the part's own rise at the 1 mA preload is milliwatts over the %.2f C" % (
        S["ref_rev"], S["ref_vfb"], 100 * S["ref_acc"], PL.T_AIR))
    w("       air, so TJ under 85 C; %.1f %% to 125 C), line regulation %.1f mV PRINTED max, IFB %.1f uA PRINTED max into %.2fk, the divider at" % (
        100 * S["ref_acc125"], S["ref_line"] * 1e3, S["ref_ifb"] * 1e6, PL.R_SET_TOP / 1e3))
    w("       +-%.4f %% each (0.1 %% and 25 ppm/K over 65 K, DECLARED class): %.4f to %.4f V" % (100 * (PL.DIV_TOL + PL.DIV_TCR * PL.DIV_DT), L["vset"][0], L["vset"][2]))
    w("     THE REFERENCE'S ACTUAL LOAD (cx45 Q1): the sheet prints the accuracy at IOUT = 1 mA only and its load regulation (0.1 to 500 mA) as")
    w("       %.3f V/A TYPICAL; the drawn load is %.4f to %.4f mA (VFB's and R552's corners, IFB, the hold's leakage through R559), at most %.1f uA" % (
        L["ref_loadreg_typ"], L["ref_load"][0] * 1e3, L["ref_load"][1] * 1e3, L["ref_dI"] * 1e6))
    w("       from the test condition; the residual is bounded at %.0f times the TYPICAL row (ASSUMPTION): %.2f uV at PA_ISET, carried in the" % (
        PL.LOADREG_X, L["ref_resid"] * 1e6))
    w("       corners above; PROVISIONAL on the supplier's validation task V-PA-REF (section 6)")
    w("     Q551'S HOLD AND RELEASE (cx46 item 2): Q551 holding PA_ISP near ground loads the reference through R559 as well: up to %.4f mA" % (
        L["ref_held"] * 1e3))
    w("       (PA_ISET's top across R559's low corner plus the divider; Q551's RDS(on) neglected, an upper bound, MODEL), %.1f times the test" % (
        L["ref_held"] / 1e-3))
    w("       condition; at ten times the TYPICAL row its residual is %.3f mV while held (ASSUMPTION). It moves no steady band (the cap is" % (
        L["ref_held_resid"] * 1e3))
    w("       held at zero), but on release C557 charges through R559 and the load falls to the steady one in about %.1f ms (3 R559 C557): the" % (
        L["release_t"] * 1e3))
    w("       reference's recovery is inside the set point's ramp, read by V-PA-REF and B-PA2 (section 6); its load regulation at that load is")
    w("       TYPICAL only: REMAINING ENGINEERING (the reference's loading through the hold and the release), with the acceptance limits below")
    w("     R553 (0.1 %%, 25 ppm/K) %.4fk to %.4fk and R559 (the tree's 1 %% class, ASSUMPTION) %.4fk to %.4fk at their corners (cx45 Q1; round 2 held" % (
        L["r_int"][0] / 1e3, L["r_int"][1] / 1e3, L["r_ss"][0] / 1e3, L["r_ss"][1] / 1e3))
    w("       them nominal: %.4f to %.4f A)" % (L["i_min_nores"], L["i_max_nores"]))
    w("     Q551 and C557 leakage into R559 (2N7002 IDSS 80 nA PRINTED at 25 C, doubled every 10 K to the air: record l8p's ASSUMPTION; C557 at")
    w("       %.0f Ohm F, ASSUMPTION): %.2f uA, %.2f mV off the set point (the bottom only)" % (PL.IR_X7R_OHM_F, L["leak"] * 1e6, L["leak"] * PL.R_SS * 1e3))
    w("     the INA250A2 (%s), gain:" % S["ina_rev"])
    for lab, k, x in L["gain_terms"]:
        w("       %-104s %-10s %.4f %%" % (lab, k, 100 * x))
    w("       together +-%.4f %% (the PRINTED part %.2f %%)" % (100 * L["gerr"], 100 * L["gerr_printed"]))
    w("     the INA250A2, offset:")
    for lab, k, x in L["ios_terms"]:
        w("       %-104s %-10s %.4f A" % (lab, k, x))
    w("       together +-%.4f A" % L["ios"])
    w("     the integrator (TLV9062 %s):" % S["oa_rev"])
    for lab, k, x in L["vos_terms"]:
        w("       %-118s %-10s %.4f mV" % (lab, k, x * 1e3))
    w("       together +-%.4f mV; R560's offset (V+ - PA_ISP) x R553 / R560 is a deterministic term inside the formula, R560 1 %% 100 ppm/K" % (L["vos"] * 1e3))
    w("     THE CAP: %.4f A nominal; %.4f to %.4f A over every corner (MODEL on the terms above); on the PRINTED rows alone (no TYPICAL or" % (
        L["i_nom"], L["i_min"], L["i_max"]))
    w("       ASSUMPTION term: the load residual, IB, C554's leakage, the stress rows, the nonlinearity and the hold's leakage out; R559 at the")
    w("       tree's 1 %% class, ASSUMPTION) %.4f to %.4f A, which is NOT a guaranteed band (the TYPICAL and ASSUMPTION terms are real)" % (
        L["i_min_printed_only"], L["i_max_printed_only"]))
    w("   against the PA rail's own limit, U13's average loop (VSNS %.0f mV PRINTED min on R55, WSL25126L000FEA 6 mOhm 1 %%, TCR +-%.0f ppm/K PRINTED" % (
        S["lm_vsns"][0] * 1e3, S["wsl_tcr"] * 1e6))
    w("     for 5 to 6.9 mOhm): R55 at the cap's top dissipates %.3f W, %.1f C on the %.2f C air with %.0f K/W from the WSL2512 derating line (MODEL," % (
        L["r55_w"], L["r55_t"], PL.T_AIR, PL.R55_RTH))
    w("     not a printed thermal resistance): least %.4f A (%.4f A initial); the cap's top and R55's other loads %.4f A: %.4f A under it" % (
        L["u13_min"], L["u13_min_init"], L["i_max"] + L["r55_other"], L["u13_min"] - L["i_max"] - L["r55_other"]))
    w("     so in the steady state U13 stays in voltage regulation at the cap on these bounded figures: L9P-F04 PROVISIONAL with the selection")
    w("     (the owner's part 21: the PA rail's rows depend on the PROVISIONAL service and dynamics)")
    w("   U13's output: VREF %.3f to %.3f V PRINTED, 162k over 10k; at 1 %% (as drawn, 100 ppm/K over 65 K ASSUMPTION) %.3f to %.3f V; at 0.1 %% 25" % (
        S["lm_vref"][0], S["lm_vref"][2], L["vpa_drawn"][0], L["vpa_drawn"][2]))
    w("     ppm/K (fb01's keyword, values unchanged) %.3f to %.3f V" % (L["vpa"][0], L["vpa"][2]))
    w("   THE CASE AT THE CAP'S TOP (C-ALLTX rev 3, the PA's DC input at most %.3f V x %.4f A = %.2f W, it was %.1f W; the loop's own %.2f mA on" % (
        L["vpa"][2], L["i_max"], L["p_max"], R["pa_now"], L["supply_a"] * 1e3))
    w("     +5V_D8IN added at VBAT as %.3f W):" % L["loop_w"])
    w("     nominal %.3f W at VBAT, need %.4f V; BOUNDED (the gauge's %.4f A, the dock contacts' maximum, R_cell %.3f Ohm the case's ASSUMPTION):" % (
        L["nom"]["p"], L["nom"]["need"], R["gu"], L["bnd"]["r_cell"]))
    w("     need %.4f V, a MODEL margin of %.4f V under 15.5 V (with U13's divider left at 1 %%: %.4f V)" % (L["bnd"]["need"], V - L["bnd"]["need"], L["bnd_drawn"]["need"]))
    w("     the margin covers %.2f mOhm more path or R_cell to %.4f Ohm; the rest of the path outside the dock contacts (MISSING in the tree)," % (
        L["rx_cover"] * 1e3, L["rc_cover"]))
    w("     illustrated:")
    for lab, x in L["path_rest"]:
        w("       %-112s %.3f mOhm" % (lab, x * 1e3))
    w("       together %.3f mOhm: need %.4f V" % (L["path_rest_sum"] * 1e3, L["bnd_rest"]["need"]))
    w("     labelled scenarios, never the case: R_cell 0.070 Ohm %.4f V, 0.080 Ohm %.4f V; U4's lower efficiencies %.4f V; the compute modules at 8 W" % (
        L["bnd_r07"]["need"], L["bnd_r08"]["need"], L["bnd_eff"]["need"]))
    w("       %.4f V; D-11's basis %.4f V; R_cell 0.08 with U4's lower efficiencies %.4f V" % (L["bnd_m8"]["need"], L["bnd_d11"]["need"], L["bnd_all"]["need"]))
    w("     what the case would allow if U13's limit and J_PA did not bind: %.4f A at %.3f V (the room a redesign route has, see 6)" % (
        L["i_case_max"], L["vpa"][2]))
    w("   THE 30 W SERVICE AT THE CAP'S LEAST (%.4f A): THE OVERLAP IS NOT ESTABLISHED BY ANY PRINTED ROW (cx44's crux). Pout and IDD rise" % L["i_min"])
    w("     together with VGG (the sheet's description), so the cap keeps 30 W only if the module's drain current for 30 W, at its terminals, over")
    w("     the envelope (air -20 to %.2f C, the flange to +85 C under C4, 144 to 146 MHz, the available VGG band, the feed and return drops)," % PL.T_AIR)
    w("     is at most the cap's least. What is held: the maker's heat-sink EXAMPLE, IDD %.2f A at 30 W, 12.5 V and the PRINTED minimum efficiency" % L["svc_i_ex"])
    w("     40 %% (Tcase 25 C, VGG 5 V, full drive): %.4f A (%.1f %%) under the cap's least. Its transfer to the kit's conditions is an ASSUMPTION" % (
        L["i_min"] - L["svc_i_ex"], 100 * L["svc_margin"]))
    w("     (a class-B stage's DC current at a given output does not depend on VDD: MODEL). At the module's terminals (U13's lowest %.3f V less" % L["vpa"][0])
    w("     %.1f mOhm of INA250, J_PA's contacts at 20 mOhm after test and 16 AWG, at the cap's least: %.3f V) the cap's least needs %.1f %% efficiency," % (
        L["feed_r"] * 1e3, L["vdd_term"][0], 100 * L["svc_eta_need"]))
    w("     %.1f %% at the top rail; the open-loop VGG band (its top under the sheet's 5 V service condition, as drawn today) is part of B-PA1" % (
        100 * L["svc_eta_need_hi"]))
    w("     VERDICT: the overlap is a BOUNDED PROVISIONAL CHOICE under the owner's part 19 (amendment 1, point 2), never a printed closure: the")
    w("     cap's band as above, the supplier's validation task B-PA1 (section 6) decides it; F01's row is PROVISIONAL on it")
    w("   the loop's dynamics (cx44): compensation the integrator R553 C554 (0.1 ms; 0.47 ms in round 2, shortened in 2b against the breaker's timer), the inverter unity, the injection R82/R57 = %.2f;" % (PL.R82 / PL.R_INJ))
    for k, fc, pm in L["dyn"]:
        w("     at a module slope dIDD/dVGG of %4.1f A/V (TYPICAL curves only) the crossover is %6.0f Hz and the phase margin %.1f deg against the" % (k, fc, pm))
        w("       INA250A2's TYPICAL %.0f kHz bandwidth and the 1 us harness filter (MODEL)" % (S["ina_bw"] / 1e3))
    w("     VGG falls only by its loads (U15 cannot sink): with R58 470 Ohm about %.2f V/ms at 4.2 V (MODEL, the module's own gate current not counted);" % (L["fall"] / 1e3))
    w("     an excursion over the cap mid key-down (a load step) lasts about the VGG travel dI / slope over the lesser of the loop's slew and the")
    w("       bleed's rate (MODEL, first order): " + "; ".join("%.0f A/V %.1f A %.3f ms" % (k, di, t * 1e3) for k, di, t in L["exc"]))
    w("       against record l9stk's breaker timer, 0.282 ms least: every modelled corner inside it (MODEL on TYPICAL plant figures)")
    w("     saturation: half A rests at its top rail under the set point and leaves it at once, half B's output then rises from 0 V (no dead band);")
    w("     acquisition at each key: the set point ramps from zero (held by OUTLET_OK), so the current approaches the cap from below; settling is")
    w("     milliseconds against the 60 s key-down. NOT BOUNDED at the desk: a disturbance that raises the drain current over the cap mid key-down")
    w("     (a load change at the antenna) is corrected at VGG's fall rate; the excursion is bounded in size by U13's own loop (at most %.3f A" % L["u13_max"])
    w("     average, cold) and in time only by a measurement: PROVISIONAL, the supplier's task B-PA2 with record l9stk's E-10 (the breaker's")
    w("     timer, 0.282 ms least)")
    w("")
    w("4b. THE CONNECTED CONSEQUENCES (each traced in 1c's acceptance; cx44's checklist)")
    w("   +5V_D8IN (U41): %.2f mA more (IQ and IGND PRINTED maxima, the preload, the divider, R560); U41's 3 A and the rail's 2.0 A peak unchanged" % (L["supply_a"] * 1e3))
    w("   R55 and U13: BIAS off R55; R55's other loads %.3f mA; the steady cap %.4f A under U13's least %.4f A" % (L["r55_other"] * 1e3, L["i_max"], L["u13_min"]))
    w("   INA250 insertion: %.1f mOhm TYPICAL, %.3f W at the cap's top, junction %.1f C at %.2f C air (RthJA %.1f K/W TYPICAL, a layout's own figure" % (
        S["ina_rpkg"] * 1e3, L["ina_w"], L["ina_tj"], PL.T_AIR, S["ina_rja"]))
    w("     is Layer 10's); its drop lowers the module's VDD by about %.0f mV, inside U13's window's effect above" % (L["i_max"] * S["ina_rpkg"] * 1e3))
    w("   J_PA and its 16 AWG lead: %.4f A against the VH's PRINTED 10 A (it carried a declared 6.0 A and the case's 8.19 A before)" % L["i_max"])
    w("   the PA's ground: unchanged (J_PA pin 2, the plate, the shields); the sense is high-side, nothing enters the return")
    w("   the harness reference: board D's ground up to %.3f V above board A's (bounded %.4f V on the D8 lead, MODEL): VGG at rest %.3f to %.3f V" % (
        PL.GND_SHIFT, L["gshift"], L["band"][0], L["band"][2]))
    w("     (drawn %.3f to %.3f V), the top under the module's 5 V; the loop's authority at most %.3f V" % (L["band_drawn"][0], L["band_drawn"][2], L["band"][3]))
    w("   EMCON and the key: U15's EN stays PA_KEY; with PA_KEY low U15 is off and VGG held by its discharge and R58; the loop only lowers VGG; with")
    w("     PA_EN low OUTLET_OK is high and the set point held at 0 V (both ways safe); a lost PA_ILIM conductor leaves VGG at R83's 11.0k alone,")
    w("     lower than the band (the cap is lost, the PA runs open loop under VGG's own lower band: a single-failure row for Layer 8)")
    w("   the pack and the protection: steady state as THE CASE above (the pack's true current at 15.5 V rest under the breaker's least 18.32 A);")
    w("     transients PROVISIONAL (B-PA2, E-10)")
    w("   thermal duty: the PA's heat at most %.2f W less its RF output (%.2f W at 30 W out; today's HIGH less 30 W %.2f W); with less than 30 W" % (
        L["p_max"], L["heat_c"], L["heat_now"]))
    w("     out, more of the %.2f W is heat: REQ-059's thermal row reads the cap's top as its DC input" % L["p_max"])
    w("   interfaces: IF-A-PA (J_PA behind U551, the cap) and IF-AD-HARNESS (pin 16 PA_ILIM) are Layer 5 texts owed (named prerequisites)")
    w("")
    w("5. THE SELECTION, ROUND 2 (authority: SESSION; ruled_by: Slot A under the owner's standing rule of 26 September 2026, the ruling of")
    w("   21 September 2026 and part 19 of 5 October 2026; ruled_on: 5 October 2026)")
    w("   (a) and (c) are judged on ONE standard (cx44: rejecting (a) for an unprinted PA transfer while crediting (c)'s was inconsistent): each")
    w("     rests on an unprinted PA transfer, so each is at most a PROVISIONAL choice with a supplier validation task. The difference is WHERE")
    w("     the unprinted transfer sits: (c) bounds the case's own quantity (DC watts) on the terms of section 4 and leaves the 30 W service on")
    w("     one bench row (B-PA1, the module's drain current at 30 W); (a) leaves the case itself on the PA's efficiency at the loop's high end")
    w("     (at least %.1f %% at +-0.5 dB) AND the service on a detector chain whose calibration residual no sheet bounds (two bench tasks, one" % (
        100 * A["eta_need"][1][1]))
    w("     of them on the failing case). (b) cannot close the case. RANK: (c) first, (a) second.")
    w("   SELECTED: (c), PROVISIONAL: F01 / D-17's row reads PROVISIONAL on B-PA1 (feasibility of the 30 W service under the cap) and B-PA2")
    w("     (the dynamics), never closed on printed limits; its dependants read PROVISIONAL too: L9P-F04's closure claim, the PA rail's rows")
    w("     (+13V8_PA and +13V8_PAJ at 6.93 A) and board D's loop (R57, R58, R83)")
    w("   AFTER cx46 (the second negative on the method, which ends it; kept as given): F01 / D-17 and every dependant (C-ALLTX rev 3 at the")
    w("     cap, U13's room, B-PA1's limit, the PA rail's rows) stay PROVISIONAL; the reference's loading through Q551's hold and release and")
    w("     the acceptance limits are REMAINING ENGINEERING for the receiving company, never a qualification-only item")
    w("   WITHDRAWN (cx44): round 1's fallback \"a lower-VGG-wins RF loop for the service floor\": an RF loop cannot restore output while the current")
    w("     cap binds. If B-PA1 fails (the module needs more than the cap's least for 30 W), the ARRANGEMENT fails (amendment point 4), not a")
    w("     requirement: the remaining routes are (R1) raise U13's own limit and the cap with it (R55 lower, J_PA's lead and contacts re-rated: the")
    w("     bounded case allows %.4f A at the top rail, %.4f A more than the cap's top) and (R2) a PA rail at the sheet's 12.5 V with VGG to its 5 V" % (
        L["i_case_max"], L["i_case_max"] - L["i_max"]))
    w("     condition (U13's divider, board D's VGG band); each would be checked on the same case before adoption. No requirement changes.")
    w("")
    w("6. THE SUPPLIER'S VALIDATION TASKS (amendment 1, point 2: UNSENT, nothing bought; each with specimen, quantity and pass limit)")
    w("   B-PA1 (FEASIBILITY of the service under the cap; the PROVISIONAL choice above depends on it):")
    w("     specimen: three RA30H1317M1, each on the plate's heat path, driven by board D's chain (the SA868 through the 10 dB pad, Pin about 50 mW)")
    w("     quantity: the drain current (and gate current) at Pout 30.0 W under VGG control, at module-terminal VDD %.2f and %.2f V, 144 / 145 /" % (
        L["vdd_term"][0], L["vdd_term"][1]))
    w("       146 MHz, flange 25 C and +85 C and an air of -20 C, into 50 Ohm and into a 3:1 load at its worst phase, VGG within the drawn band")
    w("     pass limit: IDD at 30.0 W at most %.3f A (the band's floor %.4f A rounded DOWN, cx46) less the measurement's own expanded" % (
        L["bpa1_limit"], L["i_min"]))
    w("       uncertainty (k = 2, stated by the lab), every point;")
    w("       the transfer to other modules is the supplier's to justify (three units establish no population limit)")
    w("     capability: a 50 Ohm 50 W load and a 3:1 mismatch, an RF power meter with stated uncertainty, a DC supply with current reading, a")
    w("       temperature chamber or plate control")
    w("   B-PA2 (the loop's dynamics, PROVISIONAL): on the built loop, the drain current's settling at each key (0 to the cap without overshoot")
    w("     over %.3f A), the excursion and its duration after a step from 1:1 to 3:1 load mid key-down, the PA rail inside U13's regulation, and" % L["i_max"])
    w("     the pack current against record l9stk's E-10 (under 18.32 A, or excursions under 0.282 ms each and 1.03 % of the time); and the")
    w("     release from Q551's hold (cx46): the cap's settling with the reference recovering from its held load, no overshoot over the top")
    w("   V-PA-REF (the reference at its actual load, cx45 Q1; PROVISIONAL until read): three TLV75801P of the fitted lot, each at its drawn")
    w("     load %.3f and %.3f mA, -40, 25 and 85 C, VIN 5.0 V: VFB within %.4f to %.4f V (the sheet's +-%.0f %% at 1 mA, which the cap's band" % (
        L["ref_load"][0] * 1e3, L["ref_load"][1] * 1e3, S["ref_vfb"] * (1 - S["ref_acc"]), S["ref_vfb"] * (1 + S["ref_acc"]), 100 * S["ref_acc"]))
    w("     above already carries, widened by the %.2f uV residual); a unit outside it moves the cap's band, B-PA1's pass limit with it;" % (L["ref_resid"] * 1e6))
    w("     and at Q551's held load (up to %.3f mA) and through the release step back to the drawn load (VFB's excursion and recovery" % (L["ref_held"] * 1e3))
    w("     within the set point's %.1f ms ramp, cx46 item 2)" % (L["release_t"] * 1e3))
    w("   U5 (R-214, the rest voltage's fall in the 60 s) MISSING: the case at the cap has %.4f V of MODEL margin against it" % (V - L["bnd"]["need"]))
    w("")
    w("7. CX44'S TEN FINDINGS, EACH DISPOSED OF (the owner's part 21: CORRECTED WITH DESK EVIDENCE, STILL AN OPEN DESIGN DEFECT, or GENUINELY")
    w("   EXTERNAL with its effect on the candidate; as received: inputs/cx44-astra-f01-selection-as-received.md; the evidence is this output's")
    w("   section named, l9t5_f01_drafts.out and the drafts)")
    e = L["exc"]
    worst_exc = max(t for _k, _d, t in e)
    rows = [
        ("1", "the 6 A example does not establish 30 W at the cap's least", "GENUINELY EXTERNAL",
         "the module's drain current for 30 W over the kit's envelope is printed nowhere: the 6.00 A is labelled the maker's EXAMPLE and its "
         "transfer an ASSUMPTION (4, THE 30 W SERVICE); effect: F01 / D-17 PROVISIONAL on B-PA1 (6); if B-PA1 reads over %.3f A less the lab's "
         "uncertainty the arrangement fails and routes R1 or R2 are taken (5)" % L["bpa1_limit"]),
        ("2", "typical stress data and an assumed bias in a printed band", "CORRECTED WITH DESK EVIDENCE",
         "the terms split by label (l9t5_paloop.py cap(); 4, the INA250A2 gain and offset, the integrator): %.4f to %.4f A with the TYPICAL "
         "allowances carried whole, %.4f to %.4f A on the PRINTED rows alone (not a guaranteed band); residual GENUINELY EXTERNAL: no printed maximum for the shunt's "
         "stress rows; effect: the %.4f A under U13's least absorbs %.2f %% more gain drift" % (
             L["i_min"], L["i_max"], L["i_min_printed_only"], L["i_max_printed_only"], L["u13_min"] - L["i_max"] - L["r55_other"],
             100 * (L["u13_min"] - L["i_max"] - L["r55_other"]) / L["i_max"])),
        ("3", "reference loading, junction, supply, common mode, loop residuals", "STILL AN OPEN DESIGN DEFECT for the reference's loading (cx46)",
         "the reference's loading through Q551's hold (up to %.3f mA) and release is REMAINING ENGINEERING (4, cx46 item 2); the rest CORRECTED WITH "
         "DESK EVIDENCE: R552 549 Ohm gives a %.4f mA preload; the reference's steady load %.4f to %.4f mA against SBVS351D's IOUT = 1 mA test condition, its "
         "residual bounded at %.0f times the TYPICAL load regulation (ASSUMPTION, %.2f uV) and PROVISIONAL on V-PA-REF (6, cx45); R553 and R559 at "
         "their corners (cx45); TJ under 85 C at the %.2f C air; +5V_D8IN 4.872 to 5.133 V; "
         "the integrator's terms %.4f mV in all, IB and C554's leakage carried as ASSUMPTION allowances (4)" % (
             L["ref_held"] * 1e3, L["ref_preload"] * 1e3, L["ref_load"][0] * 1e3, L["ref_load"][1] * 1e3, PL.LOADREG_X, L["ref_resid"] * 1e6, PL.T_AIR,
             L["vos"] * 1e3)),
        ("4", "R55 carries U13's BIAS and other loads", "CORRECTED WITH DESK EVIDENCE",
         "BIAS bounded at %.4f A (4) and re-tapped to PA_OUT (apply_gen_sch_a_paloop.py edit 1; U13.24 on PA_OUT on the composed netlist; mutation "
         "M06 fails, l9t5_f01_drafts.out 4); R55's other loads %.3f mA; R55 at %.1f C (printed TCR; its thermal resistance a MODEL); the cap's "
         "top and the rest %.4f A under %.4f A. L9P-F04's closure claim reads PROVISIONAL with the selection (part 21)" % (
             L["bias"][0], L["r55_other"] * 1e3, L["r55_t"], L["u13_min"] - L["i_max"] - L["r55_other"], L["u13_min"])),
        ("5", "no compensation, settling or excursion bound", "CORRECTED WITH DESK EVIDENCE (MODEL)",
         "the integrator 0.1 ms, crossover %.0f to %.0f Hz and phase margin %.1f to %.1f deg on TYPICAL slopes and bandwidth; R58 470 Ohm, VGG falls "
         "about %.2f V/ms; the set point held and ramped at each key (3 tau %.0f ms, over K1's 3 ms); an excursion under a load step at most "
         "%.3f ms on the model against the breaker's 0.282 ms; residual GENUINELY EXTERNAL: the module's slope and dynamics (B-PA2, l9stk "
         "E-10); effect: the dynamic rows PROVISIONAL" % (
             min(x[1] for x in L["dyn"]), max(x[1] for x in L["dyn"]), min(x[2] for x in L["dyn"]), max(x[2] for x in L["dyn"]), L["fall"] / 1e3,
             L["ramp_t"] * 1e3, worst_exc * 1e3)),
        ("6", "0.2981 V was a conditional margin", "CORRECTED WITH DESK EVIDENCE",
         "relabelled MODEL; %.4f V with the loop's own %.3f W, covering %.2f mOhm more path or R_cell to %.4f Ohm (4); the case's own "
         "assumptions (R_cell DC, the converters' efficiencies, U5) stay GENUINELY EXTERNAL; effect: R_cell 0.08 Ohm reads %.4f V, over 15.5 V, "
         "a labelled scenario" % (V - L["bnd"]["need"], L["loop_w"], L["rx_cover"] * 1e3, L["rc_cover"], L["bnd_r08"]["need"])),
        ("7", "a lower-VGG-wins RF loop cannot restore output", "CORRECTED WITH DESK EVIDENCE",
         "the fallback withdrawn; the remaining routes R1 (U13's limit and the cap raised: the case allows %.4f A) and R2 (the PA rail at "
         "12.5 V, VGG to 5 V) named (5)" % L["i_case_max"]),
        ("8", "B-PA1 and B-PA2 decide feasibility, envelope and uncertainty missing", "CORRECTED WITH DESK EVIDENCE",
         "rewritten (6): the cold end, terminal VDD %.2f and %.2f V, 3:1 load, the lab's k = 2 uncertainty in the pass limit, the transfer the "
         "supplier's to justify; the facts they produce are GENUINELY EXTERNAL and F01 stays PROVISIONAL on them" % (L["vdd_term"][0], L["vdd_term"][1])),
        ("9", "the connected consequences omitted", "CORRECTED WITH DESK EVIDENCE; texts owed",
         "listed with figures (4b); STILL OPEN as texts owed by their owners (no circuit defect): IF-A-PA and IF-AD-HARNESS (Layer 5), the lost "
         "PA_ILIM conductor's single-failure row (Layer 8), REQ-059's thermal row at %.2f W of DC input (Layer 7/8)" % L["p_max"]),
        ("10", "the gauge bound's own assumptions", "CORRECTED WITH DESK EVIDENCE",
         "kept labelled in 1 and 3 (the 32 K span, board P at the inside air, R10's self-heating from its power curve); board P's air "
         "GENUINELY EXTERNAL until its own row; effect: none on the selection, (b) fails even with a perfect gauge (3)"),
    ]
    for no, what, state, ev in rows:
        w("   %-3s %-66s %s" % (no, what, state))
        txt = ev
        while txt:
            cut = txt[:126]
            if len(txt) > 126:
                cut = cut[:cut.rfind(" ")]
            w("        %s" % cut)
            txt = txt[len(cut):].lstrip()
    R["dispo"] = rows
    w("")
    w("8. PREDICATES")
    for k, v in R["pred"].items():
        w("   %-132s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_f01: done")
    return "\n".join(out) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    if not all(R["pred"].values()):
        sys.stderr.write("l9t5_f01: a predicate does not hold\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
