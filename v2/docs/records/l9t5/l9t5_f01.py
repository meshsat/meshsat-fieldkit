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
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True

PINS = {
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
}
HELD = ("ina250",)        # gitignored maker's sheet: record l4e7's fetch_held_back.py fetches it and checks its sha256

# ---- the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
I_SVC_W = 30.0                       # W: the PA's service output (CHO-001: "SA868 with a RA30H1317M1 30 W stage")
T_HI, T_LO, T_REF = 85.0, -20.0, 25.0  # C: board A's air bound for the loop's parts (L4-E12's 76.25 C under it) and the cold end
# (c) the loop's parts: INA250A2 (500 mV/A) on +5V_D8IN, a TLV758P as the set-point reference, a TLV9062 (integrator and inverter)
G_SENSE = 0.5                        # V/A, INA250A2
V5_WORK = 5.14                       # V, +5V_D8IN's declared v_work (gen_sch_a.py); the INA250's test supply is 5 V
REF_RT, REF_RB = 51.1e3, 10.0e3      # Ohm: the reference's divider, 0.1 % 25 ppm/K (stream s99a's resistor class)
DIV_TOL, DIV_TCR, DIV_DT = 0.001, 25e-6, 65.0
U13_RT, U13_RB = 162e3, 10e3         # Ohm: U13's divider as drawn (gen_sch_a.py, 1 %); TCR an ASSUMPTION below
R1PC_TCR = 100e-6                    # /K: the tree's 1 % 0603 class (UNI-ROYAL 0603WAF, gen_sch_d.py's note), ASSUMPTION for 162k/10k
U13_TOL_C = (0.001, 25e-6)           # (c) takes U13's divider to 0.1 % 25 ppm/K with record l8r2's fb01 keyword (its 5.1 V stages' class)
IB_BOUND = 1e-9                      # A: TLV9062 input bias bound (TYPICAL 0.5 pA printed only), ASSUMPTION, against R_I below
R_I = 10e3
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
    # INA250A2 (TI SBOS511C)
    t = pdf("ina250")
    S["ina_rev"] = need(t, r"(SBOS511C)", "the INA250 sheet's number").group(1)
    S["ina_gerr25"] = float(need(t, r"ISENSE = –10 A to 10 A, TA = 25°C\s+±([\d.]+)%\s+±([\d.]+)%", "INA250 gain error at 25 C").group(2)) / 100
    S["ina_gerr"] = float(need(t, r"System gain error\(6\)\s+±([\d.]+)%", "INA250 gain error over temperature").group(1)) / 100
    S["ina_ios"] = float(need(t, r"INA250A2, ISENSE = 0 A\s+±([\d.]+)\s+±([\d.]+)", "INA250A2 offset current").group(2)) * 1e-3
    S["ina_dios"] = float(need(t, r"RTI versus temperature\s+TA = –40°C to 125°C\s+(\d+)\s+(\d+)\s+μA/°C", "INA250 offset drift").group(2)) * 1e-6
    S["ina_psr"] = float(need(t, r"PSR\s+VS = 2\.7 V to 36 V, TA = –40°C to 125°C\s+±([\d.]+)\s+±([\d.]+)\s+mA/V", "INA250 PSR").group(2)) * 1e-3
    S["ina_cmr"] = float(need(t, r"INA250A2, VIN\+ = 0 V to 36 V,\s*\n\s*(\d+)\s+(\d+)", "INA250A2 CMR").group(1))
    m = need(t, r"Shunt resistance\s+([\d.]+)\s+(\d)\s+([\d.]+)\s*\n\s*RSHUNT\s+onboard amplifier", "INA250 shunt (with the onboard amplifier)")
    S["ina_rsh"] = float(m.group(2)) * 1e-3
    S["ina_rpkg"] = float(need(t, r"Package resistance\s+IN\+ to IN–\s+([\d.]+)", "INA250 package resistance").group(1)) * 1e-3
    S["ina_imax"] = float(need(t, r"TA = –40°C to 85°C\s+±(\d+)\s+A", "INA250 continuous current").group(1))
    S["ina_rja"] = float(need(t, r"RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)", "INA250 RthJA").group(1))
    S["ina_iq"] = float(need(t, r"IQ\s+Quiescent current\s+TA = –40°C to 125°C\s+(\d+)\s+(\d+)\s+μA", "INA250 IQ").group(2)) * 1e-6
    S["ina_stress"] = [float(x) / 100 for x in re.findall(r"(?:ISENSE = 30 A for 5 seconds|500 cycles|260°C solder, 10 s|1000 hours, TA = 150°C|24 hours, TA = –65°C)\s+±([\d.]+)%", t)]
    if len(S["ina_stress"]) != 5:
        refuse("INA250's five shunt stress rows")
    need(t, r"System gain error does not include the\s*\n\s*stress related characteristics", "INA250 note 6")
    # TLV758P (TI SBVS351D): the set-point reference
    t = pdf("tlv758p")
    S["ref_rev"] = need(t, r"(SBVS351D)", "the TLV758P sheet's number").group(1)
    S["ref_vfb"] = float(need(t, r"VFB\s+Feedback voltage\s+TJ = 25°C\s+([\d.]+)\s+V", "TLV758P VFB").group(1))
    S["ref_acc"] = float(need(t, r"Output accuracy\(1\)\s+–40°C ≤ TJ ≤ \+85°C\s+–(\d+)%\s+(\d+)%", "TLV758P accuracy").group(2)) / 100
    S["ref_line"] = float(need(t, r"Line regulation\s+VOUT\(NOM\) \+ 0\.5 V\(2\) ≤ VI N ≤ 6\.0 V\s+(\d+)\s+([\d.]+)\s+mV", "TLV758P line regulation").group(2)) * 1e-3
    S["ref_ifb"] = float(need(t, r"IFB\s+Feedback pin current\s+([\d.]+)\s+([\d.]+)\s+µA", "TLV758P IFB").group(2)) * 1e-6
    # TLV9062 (TI SBOS839N)
    t = pdf("tlv9062")
    S["oa_rev"] = need(t, r"(SBOS839N)", "the TLV906x sheet's number").group(1)
    S["oa_vos"] = float(need(t, r"VS = 5V, TA = –40°C to 125°C\s+±([\d.]+)\s*\n", "TLV9062 VOS over temperature").group(1)) * 1e-3
    S["oa_psrr"] = float(need(t, r"PSRR\s+Power-supply rejection ratio\s+VS = 1\.8V – 5\.5V, VCM = \(V–\)\s+±([\d.]+)\s+±([\d.]+)\s+µV/V", "TLV9062 PSRR").group(2)) * 1e-6
    S["oa_ib_typ"] = float(need(t, r"IB\s+Input bias current\s+±([\d.]+)\s+pA", "TLV9062 IB").group(1)) * 1e-12
    S["oa_vs"] = tuple(float(x) for x in need(t, r"VS\s+Supply voltage \(VS = \[V\+\] – \[V–\]\)\s+([\d.]+)\s+([\d.]+)\s+V", "TLV9062 supply").groups())
    # LM5176 (U13, the PA rail)
    t = pdf("lm5176")
    S["lm_vref"] = tuple(float(x) for x in need(t, r"VREF\s+Feedback reference voltage\s+FB = COMP\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "LM5176 VREF").groups())
    S["lm_ibfb"] = float(need(t, r"IBIAS\(FB\)\s+Feedback pin input bias current\s+FB in regulation\s+(\d+)\s+nA", "LM5176 FB bias").group(1)) * 1e-9
    S["lm_vsns"] = tuple(float(x) * 1e-3 for x in need(t, r"VSNS\s+Average current loop regulation target\s+(\d+)\s+(\d+)\s+(\d+)\s+mV", "LM5176 VSNS").groups())
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

    # ---- 4. (c) the drain-current loop
    L = {}
    lmv = S["lm_vref"]

    def vwin(tol, tcr):
        e = tol + tcr * 65.0
        return (lmv[0] * (1 + U13_RT * (1 - e) / (U13_RB * (1 + e))) - S["lm_ibfb"] * U13_RT,
                lmv[1] * (1 + U13_RT / U13_RB),
                lmv[2] * (1 + U13_RT * (1 + e) / (U13_RB * (1 - e))) + S["lm_ibfb"] * U13_RT)
    L["vpa_drawn"] = vwin(0.01, R1PC_TCR)
    L["vpa"] = vwin(*U13_TOL_C)
    dtol = DIV_TOL + DIV_TCR * DIV_DT
    vset_nom = S["ref_vfb"] * (1 + REF_RT / REF_RB)
    vset_hi = S["ref_vfb"] * (1 + S["ref_acc"]) * (1 + REF_RT * (1 + dtol) / (REF_RB * (1 - dtol))) + S["ref_ifb"] * REF_RT + S["ref_line"]
    vset_lo = S["ref_vfb"] * (1 - S["ref_acc"]) * (1 + REF_RT * (1 - dtol) / (REF_RB * (1 + dtol))) - S["ref_ifb"] * REF_RT - S["ref_line"]
    L["vset"] = (vset_lo, vset_nom, vset_hi)
    dT = max(T_HI - T_REF, T_REF - T_LO)
    ios = [("offset current, PRINTED max (25 C)", S["ina_ios"]),
           ("its drift, PRINTED %.0f uA/K max over %.0f K (board A's air to %.0f C)" % (S["ina_dios"] * 1e6, dT, T_HI), S["ina_dios"] * dT),
           ("PSR, PRINTED %.0f mA/V max, +5V_D8IN's %.2f V against the 5 V test" % (S["ina_psr"] * 1e3, V5_WORK), S["ina_psr"] * abs(V5_WORK - 5.0)),
           ("CMR, PRINTED %.0f dB min, the PA rail at its %.3f V top (as drawn) against the 12 V test" % (S["ina_cmr"], L["vpa_drawn"][2]),
            abs(L["vpa_drawn"][2] - 12.0) * 10 ** (-S["ina_cmr"] / 20.0) / S["ina_rsh"])]
    L["ios_terms"] = ios
    L["ios"] = math.fsum(x for _l, x in ios)
    L["gerr"] = S["ina_gerr"] + math.fsum(S["ina_stress"])          # gain error over temperature plus the shunt's stress rows
    vos = S["oa_vos"] + S["oa_psrr"] * abs(V5_WORK - 5.0) + IB_BOUND * R_I
    L["vos"] = vos
    L["i_nom"] = vset_nom / G_SENSE
    L["i_max"] = (vset_hi + vos + G_SENSE * L["ios"]) / (G_SENSE * (1 - L["gerr"]))
    L["i_min"] = (vset_lo - vos - G_SENSE * L["ios"]) / (G_SENSE * (1 + L["gerr"]))
    vs = S["lm_vsns"]
    L["u13_min"] = vs[0] / (0.006 * 1.01 * (1 + S["isns_tcr"] * S["isns_dt"]))
    L["u13_min_init"] = vs[0] / (0.006 * 1.01)
    L["u13_max"] = vs[2] / (0.006 * 0.99)
    L["p_max"] = L["vpa"][2] * L["i_max"]
    L["p_max_drawn"] = L["vpa_drawn"][2] * L["i_max"]
    L["bnd_drawn"] = row(L["p_max_drawn"], gu, rx)
    L["nom"] = row(L["p_max"])
    L["bnd"] = row(L["p_max"], gu, rx)
    L["bnd_r07"] = row(L["p_max"], gu, rx, rc=0.07)
    L["bnd_r08"] = row(L["p_max"], gu, rx, rc=0.08)
    L["bnd_eff"] = row(L["p_max"], gu, rx, eff={"PA": 0.95, "S1": 0.85, "S2": 0.85, "S3": 0.85, "DEV": 0.85})
    v8 = dict(vals)
    for s_ in (1, 2, 3):
        v8["CM5 slot %d" % s_] = 8.0
    L["bnd_m8"] = row(L["p_max"], gu, rx, vv=v8)
    L["bnd_d11"] = row(L["p_max"], gu, rx, vv=dict(B["calltx"]["basis_vals"]))
    L["bnd_all"] = row(L["p_max"], gu, rx, rc=0.08, eff={"PA": 0.95, "S1": 0.85, "S2": 0.85, "S3": 0.85, "DEV": 0.85})
    # how much more path, and how high R_cell, the bounded case at the loop's top still covers
    L["rx_cover"] = solve(lambda r: row(L["p_max"], gu, rx + r)["need"], 0.0, 0.2)
    L["rc_cover"] = solve(lambda r: row(L["p_max"], gu, rx, rc=r)["need"], 0.0, 0.3)
    # what the rest of the path (outside the dock contacts) could hold, an illustration on printed and assumed figures
    L["path_rest"] = [("the pack lead's XT60, two contacts at the PRINTED %.1f mOhm maximum (Amass 2021V1)" % (S["xt60_r"] * 1e3), 2 * S["xt60_r"]),
                      ("12 AWG pack lead, 2 x 150 mm at 85 C (ASSUMPTION: length; 5.21 mOhm/m at 20 C, copper)", 2 * 0.150 * 5.21e-3 * (1 + 0.00393 * 65)),
                      ("board bands, 2 x 200 mm at record l9stk 14.4's section (MODEL; the layout's lengths are not known)", 2 * 0.200 * 1.582e-3 / 0.1 / 2)]
    L["path_rest_sum"] = math.fsum(x for _l, x in L["path_rest"])
    L["bnd_rest"] = row(L["p_max"], gu, rx + L["path_rest_sum"])
    # the service at the loop's bottom: the maker's own 30 W design condition, carried to 13.8 V by a labelled model
    L["svc_i_ex"] = S["pa_ex_idd"]
    L["svc_eta_need_vmin"] = I_SVC_W / (L["vpa"][0] * L["i_min"])
    L["svc_eta_classb"] = S["pa_eta"] * S["pa_ex_vdd"] / L["vpa"][1]
    # heat in the PA at the loop's top, against today's HIGH (REQ-059's "about 45 W")
    L["heat_now"] = R["pa_now"] - I_SVC_W
    L["heat_c"] = L["p_max"] - I_SVC_W
    # the INA250's own heat and the key-up transient bound
    L["ina_w"] = L["i_max"] ** 2 * (S["ina_rpkg"])
    L["ina_tj"] = T_HI + L["ina_w"] * S["ina_rja"]
    R["L"] = L

    # ---- 5. the scenario table for the selection
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
    P["(c): the loop's top stays under U13's own loop minimum with its shunt's TCR (L9P-F04 closes)"] = L["i_max"] < L["u13_min"]
    P["(c): the loop's top is under the INA250's 15 A continuous rating"] = L["i_max"] < S["ina_imax"]
    P["(c): the case at the loop's top meets 15.5 V with the printed gauge bound and the dock contacts' maximum"] = L["bnd"]["need"] < V
    P["(c): the margin there is at least 0.2 V"] = V - L["bnd"]["need"] >= 0.2
    P["(c): with U13's divider left at 1 % the bounded case still meets 15.5 V, with less margin"] = L["bnd_drawn"]["need"] < V and L["bnd_drawn"]["need"] > L["bnd"]["need"]
    P["(c): with the rest of the path at its illustrated bound it still meets 15.5 V"] = L["bnd_rest"]["need"] < V
    P["(c): the loop's bottom is over the maker's 30 W design current (6.0 A at 12.5 V, the printed minimum efficiency)"] = L["i_min"] > L["svc_i_ex"]
    P["(c): the PA's DC at the loop's top is under what the bounded case allows"] = L["p_max"] < R["pa_allow_bnd"]
    P["(c): the PA's worst heat falls (the loop's top less 30 W, against today's HIGH less 30 W)"] = L["heat_c"] < L["heat_now"]
    P["(c): the INA250's junction at 85 C air and the loop's top is under its 125 C specified range"] = L["ina_tj"] < 125.0
    P["selection: (c), the only option that bounds the case's own quantity on printed limits"] = R["sel"] == "c"
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
    w("   VERDICT (a): NOT CREDITABLE at the desk. The calibration's residual (drift curvature, the sampler under mismatch) and the PA's efficiency at")
    w("     the controlled point are each bounded by nothing held; a measurement would decide whether the loop holds the case at all (specimen: the")
    w("     loop with three RA30H1317M1 on the plate; quantity: the PA's DC input and RF output at the loop's high end, 144 to 146 MHz, flange -20 to")
    w("     +85 C, load VSWR to 3:1; limit: DC input under %.2f W at RF over 30 W). A1 stays a direction, as round 2 left it." % R["pa_allow_bnd"])
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
    w("4. (c) A PA DRAIN-CURRENT LOOP (the module's drain current on the regulated PA rail is the controlled quantity)")
    w("   the circuit (drafted in 1c): board A: U13's FB divider at 0.1 %; an INA250A2 (2 mOhm integrated shunt, 500 mV/A) in series between +13V8_PA and J_PA pin 1, on")
    w("     +5V_D8IN; a TLV758P as the set-point reference (%.4f V nominal, %.1fk over %.1fk at 0.1 %%); a TLV9062: half A integrates the" % (L["vset"][1], REF_RT / 1e3, REF_RB / 1e3))
    w("     difference, half B inverts it about half the supply, so the output rests at 0 V while the current is under the set point; out on")
    w("     J_MEZZ1 pin 16 (AB_SPARE, a spare conductor of the drawn harness) to board D, where a resistor into VGG_FB (U15's feedback node) lowers")
    w("     VGG as the output rises. The loop can only LOWER VGG under its open-loop band (4.30 to 4.68 V today): EMCON and the PA's VGG < 5 V")
    w("     ratings are untouched; with PA_KEY low U15 is off and VGG stays at 0 V whatever the line does")
    w("   the cap's band, every term (I = (V_SET - VOS - G x IOS) / (G x (1 + gain error)) at its corners):")
    w("     V_SET (TLV758P %s): VFB %.2f V +-%.0f %% PRINTED (-40 to 85 C TJ), line regulation %.1f mV PRINTED max, IFB %.1f uA PRINTED max into %.1fk," % (
        S["ref_rev"], S["ref_vfb"], 100 * S["ref_acc"], S["ref_line"] * 1e3, S["ref_ifb"] * 1e6, REF_RT / 1e3))
    w("       the divider at +-%.2f %% each (0.1 %% and 25 ppm/K over 65 K, DECLARED class): %.4f to %.4f V" % (100 * (DIV_TOL + DIV_TCR * DIV_DT), L["vset"][0], L["vset"][2]))
    w("     the INA250A2 (%s): system gain error +-%.2f %% PRINTED (-40 to 125 C; amplifier and shunt), plus the shunt's stress rows %s %% (TYPICAL" % (
        S["ina_rev"], 100 * S["ina_gerr"], "+".join("%.3g" % (100 * x) for x in S["ina_stress"])))
    w("       column, note 6 excludes them from the gain error; added whole): +-%.3f %%" % (100 * L["gerr"]))
    for lab, x in L["ios_terms"]:
        w("       %-108s %.4f A" % (lab, x))
    w("       offset, all terms: +-%.4f A" % L["ios"])
    w("     the integrator (TLV9062 %s): VOS %.1f mV PRINTED max (VS 5 V, -40 to 125 C), PSRR %.0f uV/V PRINTED max, IB %.1f pA TYPICAL only (bounded" % (
        S["oa_rev"], S["oa_vos"] * 1e3, S["oa_psrr"] * 1e6, S["oa_ib_typ"] * 1e12))
    w("       here at %.0f nA, ASSUMPTION, into %.0fk): +-%.3f mV" % (IB_BOUND * 1e9, R_I / 1e3, L["vos"] * 1e3))
    w("     the cap: %.4f A nominal, %.4f to %.4f A over every corner (MODEL on PRINTED limits)" % (L["i_nom"], L["i_min"], L["i_max"]))
    w("   against the PA rail's own limits:")
    w("     U13's average current loop (LM5176 VSNS %.0f / %.0f / %.0f mV on R55 6 mOhm 1 %%): least %.4f A initial, %.4f A with the generator's" % (
        S["lm_vsns"][0] * 1e3, S["lm_vsns"][1] * 1e3, S["lm_vsns"][2] * 1e3, L["u13_min_init"], L["u13_min"]))
    w("       DECLARED %.0f ppm/K over %.0f K; the cap's top is %.4f A under it, so U13 stays in voltage regulation at the cap: L9P-F04 CLOSES" % (
        S["isns_tcr"] * 1e6, S["isns_dt"], L["u13_min"] - L["i_max"]))
    w("     U13's output (VREF %.3f to %.3f V PRINTED, 162k over 10k, IBIAS %.0f nA PRINTED): as drawn at 1 %% (%.0f ppm/K over 65 K, ASSUMPTION)" % (
        S["lm_vref"][0], S["lm_vref"][2], S["lm_ibfb"] * 1e9, R1PC_TCR * 1e6))
    w("       %.3f to %.3f V; with (c)'s divider at %.1f %% %.0f ppm/K (record l8r2's fb01 keyword rfb_tol, values unchanged) %.3f to %.3f V" % (
        L["vpa_drawn"][0], L["vpa_drawn"][2], 100 * U13_TOL_C[0], U13_TOL_C[1] * 1e6, L["vpa"][0], L["vpa"][2]))
    w("     the INA250's continuous rating %.0f A (PRINTED, -40 to 85 C); its package %.1f mOhm (TYPICAL) at the cap's top %.3f W, junction %.1f C at" % (
        S["ina_imax"], S["ina_rpkg"] * 1e3, L["ina_w"], L["ina_tj"]))
    w("       %.0f C air with %.1f K/W (TYPICAL) under its 125 C specified range" % (T_HI, S["ina_rja"]))
    w("   THE CASE AT THE CAP'S TOP: the PA's DC input at most %.3f V x %.4f A = %.2f W (it was %.1f W); with U13's divider left at 1 %%" % (
        L["vpa"][2], L["i_max"], L["p_max"], R["pa_now"]))
    w("     (%.3f V x %.4f A = %.2f W) the bounded case needs %.4f V, margin %.4f V: the divider's tolerance is part of the correction" % (
        L["vpa_drawn"][2], L["i_max"], L["p_max_drawn"], L["bnd_drawn"]["need"], R["V"] - L["bnd_drawn"]["need"]))
    w("     nominal: %.3f W at VBAT, need %.4f V (%+.4f V)" % (L["nom"]["p"], L["nom"]["need"], L["nom"]["need"] - V))
    w("     BOUNDED (the gauge's uncalibrated %.4f A, the dock contacts at their maximum, R_cell %.3f): need %.4f V, MARGIN %.4f V UNDER 15.5 V" % (
        R["gu"], L["bnd"]["r_cell"], L["bnd"]["need"], V - L["bnd"]["need"]))
    w("     the same bound covers %.2f mOhm more path, or R_cell to %.4f Ohm (the case's 0.060 is an ASSUMPTION; the sheet prints 35 mOhm AC, initial)" % (
        L["rx_cover"] * 1e3, L["rc_cover"]))
    w("     the rest of the path, outside the dock contacts (U3 of l9t5_case.out: MISSING in the tree), illustrated:")
    for lab, x in L["path_rest"]:
        w("       %-112s %.3f mOhm" % (lab, x * 1e3))
    w("       together %.3f mOhm: need %.4f V (inside the %.2f mOhm the margin covers)" % (L["path_rest_sum"] * 1e3, L["bnd_rest"]["need"], L["rx_cover"] * 1e3))
    w("     labelled scenarios on the bounded row, never the case: R_cell 0.070 Ohm %.4f V; 0.080 Ohm %.4f V; U4's lower efficiencies (PA 0.95, 5.1 V" % (
        L["bnd_r07"]["need"], L["bnd_r08"]["need"]))
    w("       stages 0.85) %.4f V; the compute modules at 8 W %.4f V; D-11's basis (rv-pwr's typ_nontx) %.4f V; R_cell 0.08 with U4's lower efficiencies %.4f V" % (
        L["bnd_eff"]["need"], L["bnd_m8"]["need"], L["bnd_d11"]["need"], L["bnd_all"]["need"]))
    w("   THE SERVICE AT THE CAP'S BOTTOM (%.4f A): the PA is a 30 W stage (CHO-001). Pout and IDD rise together with VGG (the sheet's description)," % L["i_min"])
    w("     so the cap keeps 30 W wherever the module's drain current at 30 W is under the cap's bottom. The maker's own 30 W design condition is")
    w("     IDD %.2f A at VDD %.1f V and the PRINTED minimum efficiency %.0f %% (the heat-sink example, Tcase 25 C): %.4f A under the cap's bottom (%.1f %%)" % (
        L["svc_i_ex"], S["pa_ex_vdd"], 100 * S["pa_eta"], L["i_min"] - L["svc_i_ex"], 100 * (L["i_min"] / L["svc_i_ex"] - 1)))
    w("     at 13.8 V under VGG control no row is printed: a class-B stage's DC current at a given output does not depend on VDD (MODEL), so 6.0 A")
    w("     carries over; read as efficiency, the cap's bottom needs %.1f %% at U13's lowest %.3f V, where the model gives %.1f %% at the nominal rail" % (
        100 * L["svc_eta_need_vmin"], L["vpa"][0], 100 * L["svc_eta_classb"]))
    w("     the hot flange (to +85 C, C4) is printed by no row: the bench row below confirms; it is the same bench question gen_sch_d.py already owes")
    w("     for the open-loop VGG (\"a module at its 5 V corner may not reach nominal output at 4.30 to 4.68 V\"), now with a current limit beside it")
    w("   what else it touches (each traced in 1c): the PA's heat falls from %.1f W (today's HIGH less 30 W) to %.1f W at most (REQ-059 reads about" % (
        L["heat_now"], L["heat_c"]))
    w("     45 W); the key-up transient (before the integrator acts the PA draws at most U13's own limit, %.3f A, for the loop's settling time); the" % L["u13_max"])
    w("     harness conductor AB_SPARE becomes a signal (both boards' generators, the contract IF-AD-HARNESS's row: Layer 5's text); board D's R83")
    w("     re-valued so the open-loop band is unchanged with the injection resistor in place")
    w("   VERDICT (c): CLOSES THE CASE ON PRINTED LIMITS with a %.3f V margin, no calibration, no new RF part; one physical row confirms the" % (V - L["bnd"]["need"]))
    w("     service (narrower obligation: the drain current at 30 W at the cap's conditions is under the cap's bottom, which the maker's design")
    w("     condition supports with %.1f %%)" % (100 * (L["i_min"] / L["svc_i_ex"] - 1)))
    w("")
    w("5. THE SELECTION (authority: SESSION, under the owner's standing rule of 26 September 2026 and the ruling of 21 September 2026)")
    w("   SELECTED: (c), the PA drain-current loop. Why (the owner's rule: the simplest supported correction with useful margin and the fewest")
    w("     new uncertain dependencies): it bounds the case's own quantity (DC watts) on printed limits (INA250, TLV758P, TLV9062, LM5176), so")
    w("     F01's bound needs no calibration and no measurement; it closes L9P-F04 in the same move; it lowers the PA's worst heat; it adds three")
    w("     small ICs and passives on board A (and U13's divider to 0.1 %), a resistor pair on board D, and a conductor the harness already carries. (a) leaves the case")
    w("     on an unprinted efficiency and an unbounded calibration residual; (b) cannot close the case's nominal deficit at all.")
    w("   its one physical dependency is the PA's drain current at its 30 W service under the cap (supported by the maker's design condition,")
    w("     confirmed on the bench); it is not new: the open-loop design already owes it.")
    w("   REVERSAL: if the independent challenge shows the service at the cap's bottom unsupported, the cap's band is moved up inside U13's")
    w("     loop minimum (the top may rise to %.3f A before it meets it) or, failing that, (c) is kept for the case and A1's RF loop is added for the" % L["u13_min"])
    w("     service floor (two loops, the lower VGG wins); the drafts of 1c are reverted by not applying them (nothing is applied to the tree).")
    w("")
    w("6. WHAT STAYS OPEN AFTER THE SELECTION (F01 / D-17 is OPEN until 1c's draft composes, reads on the netlists with a failing mutation and")
    w("   its electrical acceptance holds on C-ALLTX rev 3, and an independent check reads it)")
    w("   B-PA1 (physical, confirms the service): specimen three RA30H1317M1 on the plate's heat path with board D's drive; quantity the drain")
    w("     current at Pout 30 W under VGG control, VDD %.2f and %.2f V, 144 / 145 / 146 MHz, flange 25 C and 85 C; limit at most %.3f A (the cap's" % (
        L["vpa"][0], L["vpa"][2], L["i_min"]))
    w("     bottom); capability: a 50 Ohm 50 W load, an RF power meter, a DC supply with current reading; owner: the supplier's bench (unsent)")
    w("   B-PA2 (physical, confirms the loop): the cap's current at the three frequencies and both flange temperatures, inside %.3f to %.3f A;" % (
        L["i_min"], L["i_max"]))
    w("     the key-up transient on a scope (the loop's settling, the PA rail inside U13's regulation), with the VGG capture gen_sch_d.py owes")
    w("   U5 (the rest voltage's fall during the 60 s, R-214) stays MISSING; the case at the cap has %.3f V of margin against it" % (V - L["bnd"]["need"]))
    w("")
    w("7. PREDICATES")
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
