#!/usr/bin/env python3
"""Layer 9 task T5, record l9t5 (MESHSAT-1357, 4 October 2026): the case rows C-ALLTX rev 3 and C-DEV rev 1, their uncertainty,
at most three service-neutral approaches to F01 (D-17) compared, and I-03 / L9P-F04's correction selected. PROTOTYPE DESIGN,
DESK ARITHMETIC: nothing in this kit has been built, powered or measured; no figure printed here is a measurement.

It imports record l9pwr's budget (v2/docs/records/l9pwr/l9pwr_budget.py, round 4) UNCHANGED, pinned by sha256, and takes the
case row from it (its section 7b: C-ALLTX's definition, rev 2's text which rev 3 keeps, computed from the row's own text; rev 3
withdrew rev 2's quoted figure and prints this record's; round 4 pins the rev 3 case file; each pack-fed converter at the VBAT the case
sets). It then reads the makers' printed figures, every one parsed from its pinned sheet (pdftotext), never typed:
  1. the case row: the need at 18 A, the allowance at 15.5 V rest, the deficit, split into load pins, conversion, path and cells;
  2. the uncertainties the coordinator's row names, each with its label (PRINTED, TYPICAL, MODEL, ASSUMPTION, MISSING): the
     gauge's current indication against the indicated 18 A (BQ4050 SLUSC67B 6.14), R_cell (35E Ver. 1.1 7.4), the path's
     tolerance (the dock contacts' printed maximum against W2's inferred leads and contacts), the converters' unplotted points,
     the rest voltage's fall during the 60 s (no curve held, R-214); bound by bound, then combined;
  3. labelled scenarios beside the case (the compute modules at 8 W; D-11's basis on rv-pwr's typ_nontx);
  4. three approaches, each service-neutral, each with what it changes, what it touches and the evidence it needs: A1 the VHF
     PA held to its 30 W service by the maker's own output control (VGG), A2 the pack path's resistance (T6's copper options in
     volts), A3 the low-voltage conversion arrangement; each judged on the case and on its uncertainty;
  5. C-DEV and L9P-F04: the two corrections the challenge names (a re-rated path with its protection, or the load split onto a
     separately protected converter), with their numbers, and the selection;
  6. the selection, what is drafted, what stays open; 7. the predicates test_l9t5.py holds.

Run from the repository root: python3 v2/docs/records/l9t5/l9t5_case.py
The committed output is regenerated only through _bin/regen_out.py. Stdlib, PyYAML and pdftotext (poppler); about two seconds.
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
    "budget": "v2/docs/records/l9pwr/l9pwr_budget.py",
    "budget_out": "v2/docs/records/l9pwr/l9pwr_budget.out",
    "rvpwr": "v2/docs/records/rv-pwr/pwr_budget.py",
    "cases": "v2/docs/records/l9t5/inputs/coordinator-cases-2026-10-04-rev3.md",
    "challenge": "v2/docs/records/l9t5/inputs/astra-challenge-f01-1.md",
    "sources": "v2/docs/records/l9t5/inputs/SOURCES.txt",
    "bq4050": "v2/vendor/battery/ti-bq4050.pdf",
    "cell": "v2/vendor/battery/samsung-35e-orbtronic.pdf",
    "ra30": "v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf",
    "vh": "v2/vendor/connectors/jst-vh-catalogue.pdf",
    "xt60": "v2/vendor/battery/amass-xt60-spec-tme.pdf",
    "tps62933": "v2/vendor/ti/ti-tps62933.pdf",
    "gen_a": "v2/ecad/tools/gen_sch_a.py",
    "gen_b": "v2/ecad/tools/gen_sch_b.py",
    "gen_d": "v2/ecad/tools/gen_sch_d.py",
    "gen_p": "v2/ecad/tools/gen_sch_p.py",
    "lcsc_fill": "v2/ecad/tools/lcsc_fill.py",
    "chain": "v2/ecad/tools/pcb_energy_chain.yaml",
    "reqs": "v2/ecad/tools/pcb_requirements.yaml",
}
COPIES = ("cases", "challenge")          # filed as received from outside the tree; SOURCES.txt names each with its sha256

# the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
GAUGE_DT = 32.0           # K: the gauge's temperature span from a 23 C calibration to the case's +55 C cell limit (ASSUMPTION)
CAL_REF = 0.002           # the calibration reference's accuracy as a fraction of 18 A (ASSUMPTION, the bench's own instrument)
LOOP_DB = (0.25, 0.5, 1.0)  # dB: the PA output loop's half-tolerance, three values shown (the loop is not designed: a bound each)
PA_SERVICE_W = 30.0       # W: the PA's service output (the device set of 6 September 2026: "SA868 + 30 W PA stage")
CU_RHO20, CU_ALPHA = 1.7241e-8, 0.00393   # annealed copper (IEC 60028), Ohm m at 20 C and per K: MODEL constants
R43_TRY = (0.0056, 0.0050)               # Ohm: the device rail's average shunt, the two values option (a) is shown at


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l9t5_case: REFUSED: %s\n" % msg)
    sys.exit(2)


def text(key):
    p = rel(PINS[key])
    if not os.path.isfile(p):
        refuse("%s (%s) is not in the tree" % (PINS[key], key))
    return open(p, encoding="utf-8").read()


def flat(t):
    return " ".join(t.split())


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


_PDF = {}


def pdf(key):
    if key not in _PDF:
        try:
            r = subprocess.run(["pdftotext", "-layout", rel(PINS[key]), "-"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            refuse("pdftotext could not read %s (%s)" % (PINS[key], e))
        _PDF[key] = r.stdout.decode("utf-8", "replace")
    return _PDF[key]


def budget_module():
    sp = importlib.util.spec_from_file_location("l9pwr_budget_for_l9t5", rel(PINS["budget"]))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ 0. the inputs, read
def read():
    I = {}
    src = text("sources")
    for k in COPIES:
        full = hashlib.sha256(open(rel(PINS[k]), "rb").read()).hexdigest()
        if ("%s sha256 %s" % (os.path.basename(PINS[k]), full)) not in src:
            refuse("SOURCES.txt does not name %s at its sha256" % PINS[k])
    # the case rows, as the coordinator fixed them (read to quote, never to compute)
    c = flat(text("cases"))
    I["case_quote"] = need(c, r"On Layer 9's final drafts this case needs ([\d.]+) V rest \(([\d.]+) W at VBAT\)", "rev 2's quoted figure (withdrawn by rev 3)").groups()
    need(c, r"## C-ALLTX rev 3 \(15:45 CEST; rev 2's quoted figure withdrawn\) Rev 2's definition stands; its quoted figure did not belong to it\.", "rev 3's heading")
    m = need(c, r"THE CASE \(REQ-018 \+ CONOPS 4a\): ([\d.]+) W at VBAT, need ([\d.]+) V at 18 A and R_cell 0\.06 Ohm: deficit \+([\d.]+) V nominal", "rev 3's case figures")
    I["rev3_case"] = tuple(float(x) for x in m.groups())
    I["rev3_bound"] = float(need(c, r"With the printed uncertainties bounded \(the gauge's uncalibrated error, the dock contacts at their printed maximum\): ([\d.]+) V\.", "rev 3's bounded figure").group(1))
    I["case_text"] = need(c, r"Fixed: (that state and no other: transmitters keyed at HIGH, monitor full, FANS RUNNING, outlets 0 W, heater off, standby card off, every other load at typical)", "C-ALLTX rev 2's text").group(1)
    m = need(c, r"C-DEV rev 1.*?([\d.]+) A demanded \(([\d.]+) V, every load at constant power; ([\d.]+) A at 5\.1 V\) against the LM5176 stage's ([\d.]+) A loop minimum", "C-DEV rev 1", re.S)
    I["cdev_quote"] = tuple(float(x) for x in m.groups())
    I["f04_quote"] = float(need(c, r"L9P-F04 \(the PA rail, ([\d.]+) A against the same minimum\)", "L9P-F04's quoted current").group(1))
    ch = flat(text("challenge"))
    I["ch_allow"] = float(need(ch, r"the nominal 18 A/15\.5 V power allowance is ([\d.]+) W", "the challenge's allowance").group(1))
    I["ch_gain_a"] = float(need(ch, r"gives 0\.008 × 0\.1215/0\.002 = ([\d.]+) A", "the challenge's gauge reading").group(1))
    # the gauge's coulomb counter (TI BQ4050, SLUSC67B 6.14, p.11)
    g = pdf("bq4050")
    sec = need(g, r"^6\.14 Electrical Characteristics: Coulomb Counter.*?^6\.15", "BQ4050 6.14", re.M | re.S).group(0)
    I["g_rev"] = need(g, r"(SLUSC67B)", "the BQ4050 sheet's number").group(1)
    I["g_gain"] = float(need(sec, r"Gain error\s+15-bit \+ sign, over input voltage range\s+±([\d.]+)%\s+±([\d.]+)%\s+FSR", "the gain error").group(2)) / 100.0
    I["g_fsr_div"] = float(need(sec, r"Full scale range\s+.VREF1/(\d+)\s+VREF1/\d+\s+V", "the full scale range").group(1))
    m = need(sec, r"1 LSB = VREF1/\(10 × 2 \) = ([\d.]+)/\(10 × 2 \) = ([\d.]+) µV", "the LSB footnote")
    I["g_vref1"], I["g_lsb"] = float(m.group(1)), float(m.group(2)) * 1e-6
    I["g_inl"] = float(need(sec, r"Integral nonlinearity \(1\)\s+16-bit, best fit over input voltage range\s+±([\d.]+)\s+±([\d.]+)\s+LSB", "INL").group(2))
    I["g_off"] = float(need(sec, r"Offset error\s+16-bit, Post-calibration\s+±([\d.]+)\s+±([\d.]+)\s+µV", "the offset").group(2)) * 1e-6
    I["g_drift"] = float(need(sec, r"Gain error drift\s+15-bit \+ sign, over input voltage range\s+(\d+)\s+PPM/°C", "the gain drift").group(1)) * 1e-6
    # round 4 (the recheck V3's blocker 4): the offset's own drift, printed beside the gain drift and left out until now
    I["g_off_drift"] = float(need(sec, r"Offset error drift\s+15-bit \+ sign, Post-calibration\s+([\d.]+)\s+([\d.]+)\s+µV/°C", "the offset drift").group(2)) * 1e-6
    I["g_range"] = float(need(sec, r"Input voltage range\s+.([\d.]+)\s+([\d.]+)\s+V", "the input range").group(2))
    # board P's sense resistor (gen_sch_p.py R10) and the tree's 2 mOhm 2512 part (lcsc_fill.py)
    m = need(text("gen_p"), r'r\("R10", "(\d+)m 2512 (\d+)W \(sense\)", "GND", "PACK_N", "RS2512"\)', "board P's R10")
    I["r10"], I["r10_w"] = float(m.group(1)) * 1e-3, float(m.group(2))
    I["r10_tol"] = float(need(text("lcsc_fill"), r'\(r"\^2mOhm (\d+)% 2512", "R_2512"\): "(C\d+)"', "the tree's 2 mOhm 2512 part").group(1)) / 100.0
    # the cell (Samsung SDI INR18650-35E specification Ver. 1.1)
    t = pdf("cell")
    I["cell_ver"] = need(t, r"Version No\.\s+(Ver\. [\d.]+)", "the cell sheet's version").group(1)
    I["cell_z"] = float(need(t, r"Initial internal impedance\s+≤ (\d+)m\S\s*$", "7.4's impedance").group(1)) * 1e-3
    I["cell_cap"] = float(need(t, r"Standard Discharge Capacity ≥ ([\d,]+)mAh", "7.2's capacity").group(1).replace(",", "")) / 1000.0
    # the PA module (Mitsubishi RA30H1317M1, October 2011)
    t = pdf("ra30")
    I["pa_pout_max"] = float(need(t, r"Pout\s+Output Power\s+f=135-175MHz, VGG<5V\s+(\d+)\s+W", "the 45 W rating").group(1))
    m = need(t, r"Pout>(\d+)W, .T>(\d+)% @ VDD=([\d.]+)V, VGG=5V, Pin=50mW", "the printed minimum")
    I["pa_pout_min"], I["pa_eta_min"], I["pa_vdd"] = float(m.group(1)), float(m.group(2)) / 100.0, float(m.group(3))
    m = need(t, r"At Pout=(\d+)W, VDD=([\d.]+)V and Pin=50mW each stage transistor operating conditions are:", "the heat-sink example")
    I["pa_ex_pout"], I["pa_ex_vdd"] = float(m.group(1)), float(m.group(2))
    ex = t[m.end():m.end() + 900]
    s1 = need(ex, r"^\s*1\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", "stage 1's row")
    s2 = need(ex, r"^\s*2\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", "stage 2's row")
    I["pa_ex_idd"] = (float(s1.group(4)), float(s2.group(4)))
    I["pa_ex_eta"] = float(need(t, r"Rth\(case-air\) = \(90°C - 60°C\) / \(30W/(\d+)% . 30W \+ 0\.05W\)", "the example's efficiency").group(1)) / 100.0
    need(t, r"Output Power Control:\s+By the gate voltage \(VGG\)\.", "the maker's output control")
    # board D's VGG today (gen_sch_d.py: an open-loop band)
    m = need(text("gen_d"), r"line regulation 7\.5 mV maximum,\s*\n# IFB 0\.1 uA through R82 \(7\.3 mV\), load regulation negligible at the gate's 1 mA \(IGG, RA30H1317M1\): ([\d.]+) to ([\d.]+) V\.", "board D's VGG band")
    I["vgg_band"] = (float(m.group(1)), float(m.group(2)))
    # the connectors and the buck
    I["vh_a"] = float(need(pdf("vh"), r"Current rating: (\d+) A", "the VH's rating").group(1))
    t = pdf("tps62933")
    I["tps_a"] = float(need(flat(t), r"(\d)-A \(TPS62933 and TPS62933x\)", "the TPS62933's rating").group(1))
    m = need(t, r"TPS62933 and TPS62933x\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\n\s*IHS_LIMIT\s+High-side MOSFET current limit", "the high-side limit")
    I["tps_ihs"] = tuple(float(x) for x in m.groups())
    # board A's device rail and its lead, board B's end (generators as drawn)
    a = text("gen_a")
    need(a, r'vh2\("J_5V_DEV", "USB device rail to B16 \(JST-VH\): \+ -", "\+5V_DEV"\)', "board A's J_5V_DEV")
    need(text("gen_b"), r'part\("J_5V_DEV", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: USB device rail from A22 J_5V_DEV: \+ -"', "board B's J_5V_DEV")
    # W2's path composition (rv-pwr's comment) and the dock contacts' printed maximum (the energy chain's DOCK_BLOCK basis)
    m = need(text("rvpwr"), r"W2 A10's (\d+) mOhm \(three ([\d.]+) mOhm blades, two ([\d.]+) mOhm FETs, the (\d+) mOhm shunt VERIFIED; about (\d+) mOhm\s*\n# of lead and contacts INFERRED\)", "W2's path")
    I["w2"] = tuple(float(x) * 1e-3 for x in m.groups())
    import yaml
    ch_ = yaml.safe_load(text("chain"))
    st = {s_["id"]: s_ for s_ in ch_["stages"]}
    I["pin_max"] = float(need(st["DOCK_BLOCK"]["conductor"]["basis"], r"Contact Resistance: (\d+) mOhm max", "the dock contacts' resistance").group(1)) * 1e-3
    I["pin_n"] = int(round(float(st["DOCK_BLOCK"]["conductor"]["rating_a"]) / float(need(st["DOCK_BLOCK"]["conductor"]["basis"], r"Continuous (\d+) amps", "the pin rating").group(1))))
    I["xt60_a"] = float(st["PACK_LEAD"]["connector"]["rating_a"])          # the energy chain's PACK_LEAD row (the XT60's sheet, held)
    # REQ-018's acceptance (quoted)
    rq = flat(text("reqs"))
    I["req018"] = need(rq, r"- id: REQ-018 .*? acceptance: >-? (PS-ALLTX \(every transmitter keyed.*?\(D-11's declared values, SC-35, from SC-10\)\.)", "REQ-018's acceptance").group(1)
    return I


# ------------------------------------------------------------------------------------------------ the computation
def compute():
    for k, p in PINS.items():
        if not os.path.isfile(rel(p)):
            refuse("pinned input %s (%s) is missing" % (k, p))
    I = read()
    m = budget_module()
    B = m.compute()
    pb, F, D, hc = B["d11_rv_record"], B["F"], B["cfgs"]["DRAFTED"], B["hc"]
    R = {"pins": {k: (p, sha(p)) for k, p in PINS.items()}, "in": I, "bud_pred_ok": all(B["pred"].values())}
    ca = B["calltx"]
    case = ca["new"]
    vals = dict(ca["vals"])
    R["case"] = case
    R["case_quote_row"] = ca["old_basis"]
    R["basis_case"] = ca["basis_case"]
    R["cm5_8"] = ca["cm5_8"]
    I_CASE, V_REST = m.CASE_I, m.CASE_V_REST
    R["I"], R["V"] = I_CASE, V_REST

    def row(vv=None, **kw):
        return m.case_row(pb, F, D, vals if vv is None else vv, **kw)

    def margin(r):
        return V_REST - r["need"]

    # ---- 1. the row's parts: conversion by kind, the path by element
    kinds = {"the LM5176 5.1 V stages (slots and the device rail, declared 0.90)": ("S1", "S2", "S3", "DEV"),
             "the PA and HF LM5176 stages (the 12 V curve, NOT PLOTTED at 13.8 V)": ("PA", "HF"),
             "LDOs (the supervisors, the KSZ's 2.5 V, board E's 3.3 V)": ("IOC", "KSZ2V5", "E3V3"),
             "the fans' converters (the cooler step-ups, U22)": ("S1F", "S2F", "S3F", "FAN12")}
    conv = case["conv_by"]
    parts = []
    used = set()
    for lab, ns in kinds.items():
        parts.append((lab, math.fsum(conv.get(n, 0.0) for n in ns)))
        used.update(ns)
    parts.append(("every other converter and series element", math.fsum(v for n, v in conv.items() if n not in used)))
    R["conv_parts"] = parts
    R["path_parts"] = [(a, b, I_CASE * I_CASE * b) for a, b, s in D.r_parts]

    # ---- 2. the uncertainties
    U = {}
    fsr = I["g_vref1"] / I["g_fsr_div"]
    terms = [("gain error, PRINTED maximum +-%.1f %% of FSR (VREF1/%d = %.4f V, VREF1 typical)" % (100 * I["g_gain"], I["g_fsr_div"], fsr), I["g_gain"] * fsr / I["r10"]),
             ("integral nonlinearity, PRINTED maximum %.1f LSB of %.2f uV" % (I["g_inl"], I["g_lsb"] * 1e6), I["g_inl"] * I["g_lsb"] / I["r10"]),
             ("offset, PRINTED maximum %.0f uV post-calibration (the counter's offset is calibrated by its own routine)" % (I["g_off"] * 1e6), I["g_off"] / I["r10"]),
             ("R10's tolerance, ASSUMPTION %.0f %% (the generator prints none; the tree's 2 mOhm 2512 part)" % (100 * I["r10_tol"]), I["r10_tol"] * I_CASE),
             ("gain drift, PRINTED maximum %.0f ppm/K over %.0f K (ASSUMPTION: a 23 C calibration to the +55 C cell limit)" % (I["g_drift"] * 1e6, GAUGE_DT), I["g_drift"] * GAUGE_DT * I_CASE),
             ("offset drift, PRINTED maximum %.1f uV/K over the same %.0f K (round 4: rounds 1 to 3 left it out)" % (I["g_off_drift"] * 1e6, GAUGE_DT), I["g_off_drift"] * GAUGE_DT / I["r10"])]
    U["off_drift"] = terms[-1][1]
    U["gauge_terms"] = terms
    U["gauge_uncal"] = math.fsum(x for _l, x in terms)
    U["gauge_cal"] = math.fsum(x for l_, x in terms[1:] if not l_.startswith("R10")) + CAL_REF * I_CASE
    U["gauge_gain_only"] = terms[0][1]
    for k in ("gauge_gain_only", "gauge_uncal", "gauge_cal"):
        U[k + "_row"] = row(i=I_CASE - U[k])
    # R_cell
    r_cov = (V_REST - case["p"] / I_CASE - I_CASE * case["r_path"]) * 3.0 / (F["series"] * I_CASE)
    U["rcell_cov"] = r_cov
    U["rcell_rows"] = [(rc, row(r_cell=rc)) for rc in (I["cell_z"], 0.07, 0.08)]
    # the path
    w2_known = 3 * I["w2"][1] + 2 * I["w2"][2] + I["w2"][3]
    pins_rt = 2 * I["pin_max"] / I["pin_n"]
    U["w2"] = (I["w2"][0], w2_known, I["w2"][4], pins_rt)
    U["path_pins_row"] = row(r_extra=max(0.0, pins_rt - I["w2"][4]))
    U["path_per_mohm"] = I_CASE * 1e-3
    U["path_10_row"] = row(r_extra=0.010)
    # the converters' unplotted points
    U["pa95_row"] = row(eff_over={"PA": 0.95})
    U["dev85_row"] = row(eff_over={n: 0.85 for n in ("S1", "S2", "S3", "DEV")})
    # the 60 s
    q = I_CASE * 60.0 / 3600.0
    U["q60"] = (q, q / 3.0 / I["cell_cap"])
    # combined: the printed gauge (uncalibrated) with the dock contacts' maximum, R_cell at the assumption
    U["comb_printed"] = row(i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]))
    U["comb_before_r4"] = row(i=I_CASE - (U["gauge_uncal"] - U["off_drift"]), r_extra=max(0.0, pins_rt - I["w2"][4]))   # rounds 1 to 3's sum, which rev 3 quotes
    U["comb_all"] = row(i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]), r_cell=0.07,
                        eff_over={"PA": 0.95, "S1": 0.85, "S2": 0.85, "S3": 0.85, "DEV": 0.85})
    R["U"] = U

    # ---- 4. approaches
    A = {}
    # A1: the PA held to its 30 W service by its own output control; the maker's design figure 40 % at 30 W
    pa_hi_now = vals["VHF PA 30 W"]
    eta = I["pa_ex_eta"]
    ex_w = I["pa_ex_vdd"] * sum(I["pa_ex_idd"])
    a1 = []
    for db in LOOP_DB:
        p_hi = PA_SERVICE_W * 10 ** (2 * db / 10.0)              # the loop's target set so its low end is the 30 W service
        p_dc = p_hi / eta
        v2 = dict(vals)
        v2["VHF PA 30 W"] = p_dc
        r0 = row(v2)
        ru = row(v2, i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]))
        v8 = dict(v2)
        for s_ in (1, 2, 3):
            v8["CM5 slot %d" % s_] = 8.0
        r8 = row(v8, i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]))
        vb = dict(ca["basis_vals"])
        vb["VHF PA 30 W"] = p_dc
        rb = row(vb, i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]))
        rall = row(v2, i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]), r_cell=0.08,
                   eff_over={"PA": 0.95, "S1": 0.85, "S2": 0.85, "S3": 0.85, "DEV": 0.85})
        rc_cov = (V_REST - ru["p"] / ru["i"] - ru["i"] * ru["r_path"]) * 3.0 / (F["series"] * ru["i"])
        a1.append(dict(db=db, p_hi=p_hi, p_dc=p_dc, i_pa=p_dc / D.nodes["PA"][2], nom=r0, unc=ru, m8=r8, basis=rb, all=rall, rc_cov=rc_cov))
    A["a1"] = a1
    A["a1_pa_now"] = pa_hi_now
    A["a1_ex_w"] = ex_w
    A["pa_lim"] = D.limits["PA"]
    # A2: the pack path
    A["a2_whole_v"] = I_CASE * case["r_path"]
    t_hot = 76.25 + 9.16           # C: L4-E12's inside air plus the band's own 9.16 K at 23.93 A (record l9stk 15.5), a MODEL bound
    sec_mm2 = 2 * 39.14 * 0.035    # mm2: the band at 1 oz, two faces (record l9stk 14.4's 39.14 mm a face); 2 oz: 19.57 mm x 0.070 mm, the same
    r100 = 2 * CU_RHO20 * (1 + CU_ALPHA * (t_hot - 20.0)) * 0.1 / (sec_mm2 * 1e-6)
    A["a2_band"] = (sec_mm2, 2 * 19.57 * 0.070, r100, I_CASE * r100)
    nb = len(F["bat_refs"])
    A["a2_fet4"] = (F["bat_fets"][1] / 1000.0 / nb - F["bat_fets"][1] / 1000.0 / (nb + 1))
    A["a2_close"] = case["deficit"] / (I_CASE * I_CASE)          # Ohm of path that the nominal deficit equals
    A["a2_close_unc"] = (U["comb_printed"]["p"] - U["comb_printed"]["allow"]) / (U["comb_printed"]["i"] ** 2)
    # A3: the LDO-fed rails onto bucks at the declared floor 0.85 (no 3.3 V or 2.5 V point is plotted for the TPS62933)
    n_ = case["nodes"]
    a3 = []
    for n in ("IOC", "KSZ2V5", "E3V3"):
        p_in, p_out = n_[n][0], n_[n][1]
        a3.append((n, p_in, p_out, p_in - p_out / 0.85))
    A["a3"] = a3
    v3 = {}
    eff3 = {"IOC": 0.85, "KSZ2V5": 0.85, "E3V3": 0.85}
    r3 = m.case_row(pb, F, D, vals, eff_over=eff3)
    A["a3_row"] = r3
    A["a3_unc"] = m.case_row(pb, F, D, vals, eff_over=eff3, i=I_CASE - U["gauge_uncal"], r_extra=max(0.0, pins_rt - I["w2"][4]))
    R["A"] = A

    # ---- 5. C-DEV and L9P-F04
    stg = B["stages"][("DRAFTED", "ALLTX", "DEV")]
    lim = D.limits["DEV"]
    vsns = F["vsns"]
    tol = F["shunt_tol"]
    rs = F["lm"]["SD"][3]
    Cd = {"i_least": stg["i_least"], "i_hi": stg["i_hi"], "v_least": stg["v_least"], "lim_min": lim[1], "rs": rs,
          "lim_max": vsns[2] / (rs * (1 - tol)), "vsns": vsns, "tol": tol}
    opt_a = []
    for r in R43_TRY:
        opt_a.append((r, vsns[0] / (r * (1 + tol)), vsns[2] / (r * (1 - tol))))
    Cd["a"] = opt_a
    Cd["a_need_max"] = vsns[0] / (Cd["i_least"] * (1 + tol))                 # the largest R43 that supplies C-DEV
    Cd["a_need_min"] = vsns[2] / (I["vh_a"] * (1 - tol))                     # the smallest R43 that keeps the maximum at the VH's rating
    ev_hi = m.run_state(D, hc, "ALLTX", "hi")[1]["nodes"]
    ioc_in = ev_hi["IOC"][0]
    Cd["ioc_in_w"] = ioc_in
    Cd["ioc_i_const_p"] = ioc_in / Cd["v_least"]
    Cd["ioc_i_ldo"] = ev_hi["IOC"][1] / 3.3
    Cd["b_i_least"] = Cd["i_least"] - Cd["ioc_i_const_p"]
    Cd["b_margin"] = Cd["lim_min"] - Cd["b_i_least"]
    Cd["b_buck_a"] = Cd["ioc_i_const_p"]
    pa_hi = ev_hi["PA"][2]
    Cd["f04"] = (pa_hi, D.limits["PA"][1])
    R["C"] = Cd
    R["pred"] = predicates(R)
    return R


def predicates(R):
    I, U, A, C, case = R["in"], R["U"], R["A"], R["C"], R["case"]
    P = {}
    P["the budget's predicates all hold on this tree (record l9pwr round 4)"] = R["bud_pred_ok"]
    P["the case row reproduces the challenge's allowance at 18 A and 15.5 V to 1 mW"] = abs(case["allow"] - I["ch_allow"]) < 0.001
    P["the gauge's printed gain error alone reproduces the challenge's 0.486 A to 1 mA"] = abs(U["gauge_gain_only"] - I["ch_gain_a"]) < 0.001
    P["rev 2's quoted 16.214 V, withdrawn by rev 3, is D-11's basis (rv-pwr's typ_nontx), not the case's text, to 1 mV"] = (
        abs(R["case_quote_row"]["V_rest"]["hi"] - float(I["case_quote"][0])) < 0.001 and abs(case["need"] - float(I["case_quote"][0])) > 0.5)
    P["the case row needs more than 15.5 V nominally (F01 / D-17 stays open on the case)"] = case["need"] > R["V"]
    P["C-ALLTX rev 3's printed case (241.039 W at VBAT, 15.5162 V, +0.0162 V) is what this script computes from the pinned rev 3 file"] = (
        PINS["cases"].endswith("-rev3.md") and abs(case["p"] - I["rev3_case"][0]) < 0.0005 and abs(case["need"] - I["rev3_case"][1]) < 0.00005
        and abs(case["need"] - R["V"] - I["rev3_case"][2]) < 0.00005)
    P["rev 3's bounded 16.0684 V is this record's sum before the gauge's offset drift; with that printed term the bound is higher"] = (
        abs(U["comb_before_r4"]["need"] - I["rev3_bound"]) < 0.00005 and U["comb_printed"]["need"] > U["comb_before_r4"]["need"])
    P["the printed gauge bound alone takes the case further from 15.5 V than the nominal deficit"] = U["gauge_uncal_row"]["need"] - case["need"] > case["need"] - R["V"]
    by = {a["db"]: a for a in A["a1"]}
    P["A1 at +-0.25 and +-0.5 dB meets 15.5 V on the case with the printed gauge bound and the dock contacts' maximum; at +-1 dB it does not"] = (
        by[0.25]["unc"]["need"] < R["V"] and by[0.5]["unc"]["need"] < R["V"] and by[1.0]["unc"]["need"] > R["V"])
    P["A1 at +-0.25 dB also meets 15.5 V with the 8 W modules, with D-11's basis, and with R_cell 0.08 Ohm and U4's lower efficiencies"] = (
        by[0.25]["m8"]["need"] < R["V"] and by[0.25]["basis"]["need"] < R["V"] and by[0.25]["all"]["need"] < R["V"])
    P["A1 keeps the PA rail under U13's loop minimum at +-0.5 dB and tighter, not at +-1 dB (L9P-F04)"] = (
        by[0.25]["i_pa"] < A["pa_lim"][1] and by[0.5]["i_pa"] < A["pa_lim"][1] and by[1.0]["i_pa"] > A["pa_lim"][1])
    P["A2: what the path could lose (W2's inferred leads and contacts and a fourth battery FET) is less than the printed gauge bound needs"] = (
        U["w2"][2] + A["a2_fet4"] < A["a2_close_unc"])
    P["A2: T6's two copper options carry the same section (1 oz 39.14 mm and 2 oz 19.57 mm a face)"] = abs(A["a2_band"][0] - A["a2_band"][1]) < 1e-9
    P["A3 closes the nominal deficit and not the printed gauge bound"] = A["a3_row"]["need"] < R["V"] < A["a3_unc"]["need"]
    P["C-DEV: no 1 % R43 both supplies the case and keeps the loop's maximum under the VH's 10 A"] = C["a_need_max"] < C["a_need_min"]
    P["C-DEV option (b) leaves U7 under its loop minimum with at least 0.5 A"] = C["b_margin"] > 0.5
    P["C-DEV option (b)'s buck carries its load under its printed rating, and its limit under the VH's 10 A"] = (
        C["b_buck_a"] < I["tps_a"] and I["tps_ihs"][2] < I["vh_a"])
    P["the PA rail at its present HIGH is over U13's loop minimum (L9P-F04, as the case row quotes)"] = abs(C["f04"][0] - I["f04_quote"]) < 0.001 and C["f04"][0] > C["f04"][1]
    P["C-DEV's quoted 7.472 A and 7.0957 A are the budget's"] = abs(C["i_least"] - I["cdev_quote"][0]) < 0.0005 and abs(C["lim_min"] - I["cdev_quote"][3]) < 0.0001
    return P


# ------------------------------------------------------------------------------------------------ render
def render(R):
    I, U, A, C, case = R["in"], R["U"], R["A"], R["C"], R["case"]
    V, Ic = R["V"], R["I"]
    L = []
    w = L.append
    w("l9t5_case: C-ALLTX rev 3 and C-DEV rev 1 for task T5 (record l9t5, MESHSAT-1357, 4 October 2026). PROTOTYPE DESIGN, DESK")
    w("ARITHMETIC: nothing in this kit has been built, powered or measured. Labels: PRINTED (a maker's limit), TYPICAL (a maker's typical")
    w("figure or curve), MODEL (this record's or the budget's arithmetic), ASSUMPTION (a value no held document gives), MISSING (no held")
    w("evidence bounds it).")
    w("")
    w("0. PINS (path  sha256/16)")
    for k, (p, s) in sorted(R["pins"].items()):
        w("   %-12s %s  sha256 %s" % (k, p, s))
    w("   the copies in inputs/ (filed as received, named with their sha256 in inputs/SOURCES.txt): %s" % ", ".join(PINS[k] for k in COPIES))
    w("")
    w("1. THE CASE ROW, C-ALLTX REV 3 (its definition is rev 2's text, kept by rev 3; record l9pwr round 4, out 7b, on DRAFTED; the case file")
    w("   pinned is the coordinator's rev 3, inputs/coordinator-cases-2026-10-04-rev3.md)")
    w("   the row's text: %s" % I["case_text"])
    w("   REQ-018's acceptance: %s" % I["req018"])
    w("   need %.4f V rest at %.0f A; the allowance at %.1f V and %.0f A %.3f W at VBAT (the challenge: %.3f W); the deficit %+.3f W, %+.4f V" % (
        case["need"], Ic, V, Ic, case["allow"], I["ch_allow"], case["deficit"], case["need"] - V))
    w("   where the %.1f W the cells' EMF gives at %.0f A goes (MODEL):" % (case["emf_w"], Ic))
    w("     the load pins                       %8.3f W" % case["load"])
    w("     conversion                          %8.3f W" % case["conv"])
    for lab, x in R["conv_parts"]:
        w("        %-66s %7.3f W" % (lab, x))
    w("     the pack path %.6f Ohm              %8.3f W" % (case["r_path"], case["path_w"]))
    for a, b, x in R["path_parts"]:
        w("        %-66s %7.3f W (%.4f mOhm)" % (a.split(" (")[0][:66], x, b * 1000))
    w("     the cells, %.4f Ohm (R_cell %.3f Ohm, ASSUMPTION)  %8.3f W" % (case["r_cells"], case["r_cell"], case["cell_w"]))
    w("     the sum less the EMF: %+.3f W = the deficit" % (case["load"] + case["conv"] + case["path_w"] + case["cell_w"] - case["emf_w"]))
    q = R["case_quote_row"]
    w("   rev 2's quoted figure %s V (%s W at VBAT), WITHDRAWN by rev 3, is D-11's basis on rv-pwr's typ_nontx: %.4f V, %.3f W; the case's text gives" % (
        I["case_quote"][0], I["case_quote"][1], q["V_rest"]["hi"], q["vbat_W"]))
    w("     %.4f V (out 7b of record l9pwr names the loads that differ); rev 3 prints the case as %.3f W, %.4f V, +%.4f V: this script's figures;" % (
        case["need"], I["rev3_case"][0], I["rev3_case"][1], I["rev3_case"][2]))
    w("     the basis is shown beside it as a labelled scenario")
    w("")
    w("2. THE UNCERTAINTIES THE ROW NAMES, EACH BOUNDED ALONE, THEN COMBINED (need at the bound; the case's nominal %.4f V)" % case["need"])
    w("   U1 the gauge's current indication against the indicated %.0f A (TI BQ4050 %s 6.14, p.11, -40 to 85 C; board P's R10 %.0f mOhm):" % (Ic, I["g_rev"], I["r10"] * 1000))
    for lab, x in U["gauge_terms"]:
        w("        %-110s %.4f A" % (lab, x))
    w("      one-sided sum, uncalibrated: %.4f A, so the true current at the indicated %.0f A is %.4f A: needs %.4f V" % (U["gauge_uncal"], Ic, Ic - U["gauge_uncal"], U["gauge_uncal_row"]["need"]))
    w("      the gain error alone (the challenge's reading): %.4f A: needs %.4f V" % (U["gauge_gain_only"], U["gauge_gain_only_row"]["need"]))
    w("      calibrated (the TRM's routines calibrate the counter's gain and offset; the reference at %.1f %% of %.0f A, ASSUMPTION): %.4f A: needs %.4f V" % (
        100 * CAL_REF, Ic, U["gauge_cal"], U["gauge_cal_row"]["need"]))
    w("   U2 R_cell %.3f Ohm is an ASSUMPTION; the cell sheet (Samsung SDI INR18650-35E %s, 7.4) prints %.0f mOhm at most, INITIAL, AC 1 kHz; no" % (case["r_cell"], I["cell_ver"], I["cell_z"] * 1000))
    w("      DC or pulse figure is printed; the nominal row covers R_cell up to %.4f Ohm; " % U["rcell_cov"] + "; ".join(
        "at %.3f Ohm needs %.4f V" % (rc, r["need"]) for rc, r in U["rcell_rows"]))
    w("   U3 the path: W2's %.1f mOhm is %.2f mOhm of VERIFIED parts and about %.0f mOhm of leads and contacts INFERRED (rv-pwr); the dock's %d" % (
        U["w2"][0] * 1000, U["w2"][1] * 1000, U["w2"][2] * 1000, I["pin_n"]))
    w("      contacts each way at their PRINTED %.0f mOhm maximum are %.1f mOhm forward and return alone, %+.1f mOhm over the inferred figure for every" % (
        I["pin_max"] * 1000, U["w2"][3] * 1000, (U["w2"][3] - U["w2"][2]) * 1000))
    w("      lead and contact: needs %.4f V; the XT60's contacts, the leads and the boards' bands are not bounded in the tree (MISSING); each mOhm" % U["path_pins_row"]["need"])
    w("      of path is %.1f mV of rest voltage at %.0f A; 10 mOhm more needs %.4f V" % (U["path_per_mohm"] * 1000, Ic, U["path_10_row"]["need"]))
    w("   U4 the converters' points: the PA stage's 13.8 V output is NOT PLOTTED (the budget extrapolates SNVSAI1D's 12 V curve: %.4f at %.3f V in);" % (
        case["nodes"]["PA"][3], case["nodes"]["PA"][4]))
    w("      at 0.95 it needs %.4f V; the four LM5176 5.1 V stages' 0.90 is the generators' declaration (NOT PLOTTED): at 0.85 it needs %.4f V" % (
        U["pa95_row"]["need"], U["dev85_row"]["need"]))
    w("   U5 the rest voltage's fall during the key-down: %.2f Ah leaves the pack in 60 s at %.0f A, %.2f %% of a cell's %.2f Ah (35E 7.2); the cell's" % (
        U["q60"][0], Ic, 100 * U["q60"][1], I["cell_cap"]))
    w("      rest-voltage curve is not held as data (R-214, OWED): MISSING; D-11's method takes the rest voltage at the key-down's start only")
    w("   COMBINED, printed bounds with the stated assumptions (U1 uncalibrated, U3 the dock contacts' maximum, R_cell %.3f Ohm): %.3f W at VBAT at" % (
        case["r_cell"], U["comb_printed"]["p"]))
    w("      %.4f A, needs %.4f V (%+.4f V); with R_cell 0.070 Ohm and the converters at U4's lower figures also: needs %.4f V" % (
        U["comb_printed"]["i"], U["comb_printed"]["need"], U["comb_printed"]["need"] - V, U["comb_all"]["need"]))
    w("      (round 4: the gauge's offset drift, %.4f A, is in U1's sum now; without it the bound was %.4f V, the figure the case row's rev 3" % (
        U["off_drift"], U["comb_before_r4"]["need"]))
    w("      quotes, %.4f V: the row's quoted bound is the coordinator's to restate; F01 / D-17 is OPEN on either figure)" % I["rev3_bound"])
    w("")
    w("3. LABELLED SCENARIOS BESIDE THE CASE (never substituted for it)")
    w("   the compute modules at 8 W (the budget's HIGH; K4's hold has no numerical ceiling): %.3f W, needs %.4f V" % (R["cm5_8"]["p"], R["cm5_8"]["need"]))
    w("   D-11's basis on rv-pwr's typ_nontx at the case's VBAT (the row's quoted reading): %.3f W, needs %.4f V" % (R["basis_case"]["p"], R["basis_case"]["need"]))
    w("")
    w("4. THREE SERVICE-NEUTRAL APPROACHES (none sheds a load the row keeps; each judged on the case and on section 2's printed bound)")
    a1 = A["a1"]
    w("   A1 THE VHF PA HELD TO ITS %.0f W SERVICE BY ITS MAKER'S OWN OUTPUT CONTROL (a closed loop on VGG, board D)" % PA_SERVICE_W)
    w("      today: board D sets VGG open-loop to %.2f to %.2f V (gen_sch_d.py), so nothing holds Pout under the module's %.0f W rating; the budget's" % (
        I["vgg_band"][0], I["vgg_band"][1], I["pa_pout_max"]))
    w("        HIGH %.0f W is that rating at the %.0f %% PRINTED minimum efficiency (Mitsubishi RA30H1317M1, October 2011: Pout > %.0f W, total efficiency" % (
        A["a1_pa_now"], 100 * I["pa_eta_min"], I["pa_pout_min"]))
    w("        > %.0f %% at VDD %.1f V, VGG 5 V); the sheet names VGG as the output control and designs its heat sink at Pout %.0f W, VDD %.1f V, %.0f %%:" % (
        100 * I["pa_eta_min"], I["pa_vdd"], I["pa_ex_pout"], I["pa_ex_vdd"], 100 * I["pa_ex_eta"]))
    w("        IDD %.2f + %.2f A, %.1f W (PRINTED as the maker's design condition, not as a limit under VGG control)" % (I["pa_ex_idd"][0], I["pa_ex_idd"][1], A["a1_ex_w"]))
    w("      the change: a forward-power detector and a VGG loop on board D whose low end is the %.0f W service; the PA's DC figure at the loop's" % PA_SERVICE_W)
    w("        high end over the maker's %.0f %%, by the loop's half-tolerance (the loop is not designed: three bounds):" % (100 * I["pa_ex_eta"]))
    for a in a1:
        w("        +-%.2f dB: Pout at most %.2f W, the PA %.2f W (rail %.3f A against U13's %.4f A): the case %.3f W, needs %.4f V; with the printed" % (
            a["db"], a["p_hi"], a["p_dc"], a["i_pa"], A["pa_lim"][1], a["nom"]["p"], a["nom"]["need"]))
        w("          gauge bound and the dock contacts' maximum %.4f V (R_cell covered to %.4f Ohm); modules at 8 W %.4f V; D-11's basis %.4f V; R_cell" % (
            a["unc"]["need"], a["rc_cov"], a["m8"]["need"], a["basis"]["need"]))
        w("          0.080 Ohm with U4's lower efficiencies as well %.4f V" % a["all"]["need"])
    w("      verdict: the loop's accuracy binds: at +-0.5 dB the case closes with the printed gauge bound (R_cell to about 0.084 Ohm), at +-0.25 dB also")
    w("        the 8 W modules, D-11's basis and R_cell 0.08 Ohm with U4's lower efficiencies; at +-1 dB the high end passes the module's 45 W rating")
    w("        and the approach fails. A variant inside A1: the PA rail at the sheet's own VDD 12.5 V (U13's divider), so the 40 % is read at its condition")
    w("      touches: board D (the detector, the loop, the VGG drive; gen_sch_d.py), Layer 5 (the PA key and output-control contract), the PA's")
    w("        RF checks (harmonics at the controlled drive: the sheet prints -35 / -45 dBc at VGG 5 V only); L9P-F04 closes with it (the rail under")
    w("        U13's loop minimum, no shunt or lead change); the PA rail, its copper and every protection are unchanged")
    w("      evidence owed: the module's drain current at the loop's high end, VDD 13.8 V, 135 / 155 / 175 MHz, case -20 to +70 C, three samples")
    w("        (a bench row; the sheet's 40 %% is printed at %.1f V); the loop's own accuracy over temperature (its parts' sheets)" % I["pa_ex_vdd"])
    w("   A2 THE PACK PATH'S RESISTANCE (T6's copper is the owner's decision)")
    w("      the whole path %.4f mOhm is worth %.4f V at %.0f A; the case's nominal deficit equals %.3f mOhm; with the printed gauge bound %.3f mOhm" % (
        case["r_path"] * 1000, A["a2_whole_v"], Ic, A["a2_close"] * 1000, A["a2_close_unc"] * 1000))
    w("      T6's options: the band at 1 oz, %.2f mm2 (39.14 mm a face, two faces), and at 2 oz, %.2f mm2 (19.57 mm a face): the SAME section, so" % (
        A["a2_band"][0], A["a2_band"][1]))
    w("        either option is worth 0 V against the other as sized (record l9stk 14.4); each 100 mm of band, forward and return, hot at %.2f C is" % (76.25 + 9.16))
    w("        %.3f mOhm, %.1f mV at %.0f A (MODEL, IEC 60028 copper); the band lengths are the layout's (not known)" % (A["a2_band"][2] * 1000, A["a2_band"][3] * 1000, Ic))
    w("      a fourth BUK6Y10-30P: %.3f mOhm less, %.1f mV (and Ciss over TI's 5 nF guidance, E11-37: L4-E11's); the other elements are protection" % (
        A["a2_fet4"] * 1000, A["a2_fet4"] * Ic * 1000))
    w("        parts (R17, the breaker's sense and FETs, the blades, F2), which this task does not move")
    w("      verdict: closes the nominal deficit with about 1 mOhm, NOT the printed gauge bound; touches boards A, E, P and the energy chain")
    w("   A3 THE LOW-VOLTAGE CONVERSION ARRANGEMENT (the LDO-fed rails onto bucks at the declared floor 0.85; no 3.3 V point is plotted)")
    for n, p_in, p_out, sav in A["a3"]:
        w("      %-7s in %.3f W, out %.3f W: %.3f W less at its input" % (n, p_in, p_out, sav))
    w("      the case %.3f W, needs %.4f V; with the printed gauge bound and the dock contacts' maximum %.4f V: closes the nominal deficit, NOT the" % (
        A["a3_row"]["p"], A["a3_row"]["need"], A["a3_unc"]["need"]))
    w("        bound; touches boards B and E and the supervisors' high-availability supply (ARCH-PCB-B-IOHA)")
    w("   the 5.1 V stages' efficiency (0.90 declared, NOT PLOTTED) is not an approach: no maker figure supports a better one")
    w("")
    w("5. C-DEV REV 1 AND L9P-F04 (the device rail U7 and the PA rail U13, LM5176 SNVSAI1D: VSNS %.0f / %.0f / %.0f mV)" % tuple(x * 1000 for x in C["vsns"]))
    w("   the case: %.4f A at the least load voltage %.4f V (every load at constant power), %.4f A at 5.1 V, against %.4f A (R43 %.0f mOhm at +%.0f %%);" % (
        C["i_least"], C["v_least"], C["i_hi"], C["lim_min"], C["rs"] * 1000, 100 * C["tol"]))
    w("     the loop's highest %.4f A against J_5V_DEV's JST-VH %.0f A (PRINTED, 16 AWG)" % (C["lim_max"], I["vh_a"]))
    w("   (a) A RE-RATED PATH: R43 at most %.4f mOhm supplies the case; at least %.4f mOhm keeps the loop's highest at the VH's %.0f A: no value does" % (
        C["a_need_max"] * 1000, C["a_need_min"] * 1000, I["vh_a"]))
    w("       both (the challenge's Q4, reproduced); " + "; ".join("R43 %.1f mOhm: %.4f to %.4f A" % (r * 1000, lo, hi) for r, lo, hi in C["a"]))
    w("       so J_5V_DEV becomes a single contact rated over the loop's highest (the XT60, %.0f A in the energy chain's PACK_LEAD row) and its lead" % I["xt60_a"])
    w("       a gauge whose rating covers it")
    w("       (the lead's rating NOT HELD), with U11's INA226 calibration and the stage's current-limit screen (L6's 21.8 A typical reference)")
    w("   (b) THE LOAD SPLIT ONTO A SEPARATELY PROTECTED CONVERTER: the three supervisors' LDOs (U40, U50, U60 on board B, the IOC node) leave")
    w("       +5V_DEV for a new always-on 5.1 V buck on board A (a TPS62933, the part U12, U33 and U41 are; %.0f A, PRINTED) on its own JST-VH lead:" % I["tps_a"])
    w("       the IOC draws %.3f W at HIGH (%.4f A at %.4f V by the case's constant-power method; %.4f A as the LDOs' own current), so U7's case" % (
        C["ioc_in_w"], C["ioc_i_const_p"], C["v_least"], C["ioc_i_ldo"]))
    w("       becomes %.4f A against %.4f A: %+.4f A; the buck carries %.4f A under its rating and its high-side limit %.1f / %.1f / %.1f A (PRINTED)" % (
        C["b_i_least"], C["lim_min"], C["b_margin"], C["b_buck_a"], *I["tps_ihs"]))
    w("       stays under its lead's %.0f A; U7, R43, its lead and U11 are unchanged" % I["vh_a"])
    w("   SELECTED (SESSION): (b). Why: every figure it rests on is printed (the buck's rating and limit, the VH's rating, LM5176's VSNS); U7's")
    w("     limit and its lead's protection stay as they are; (a) needs a lead rating the tree does not hold. Its condition: the supervisors' supply")
    w("     must stay up whenever +5V_DEV's must (the slots off, the hot stop, the recovery): the buck follows RAIL_EN as U7 does (L4-E11's U46 hold)")
    w("   L9P-F04: the PA rail at HIGH %.4f A against U13's %.4f A; with A1 it is the PA's capped figure (section 4), no shunt or lead change" % C["f04"])
    w("")
    w("6. THE SELECTION")
    w("   F01 / D-17 on C-ALLTX rev 3: A1, the PA held to its 30 W service by a VGG loop on board D (SESSION, within authority: no requirement,")
    w("     money or claim changes; the kit's VHF stage is a 30 W stage). It is the only approach that closes the case with the printed gauge")
    w("     bound; A2 and A3 close only the nominal deficit. Its acceptance: the loop's half-tolerance at most 0.5 dB over temperature (the case")
    w("     with the printed bounds), at most 0.25 dB to cover the 8 W modules and D-11's basis as well. CONDITIONAL on the bench row of section 4")
    w("     (the drain current at the loop's high end at VDD 13.8 V) and on a detector whose sheet prints that accuracy; not drafted: no detector")
    w("     part is held and the loop is not designed (the next deliverable: a held detector's sheet and board D's draft)")
    w("   I-03 / C-DEV: (b), the supervisors on their own buck; L9P-F04: with A1 at +-0.5 dB or tighter")
    w("   FOR C-PROT (record l9stk's, reported, not changed here): the gauge's uncalibrated one-sided error (U1, %.4f A) exceeds the %.2f A between" % (U["gauge_uncal"], 18.32 - Ic))
    w("     the 18 A service and the breaker's least limit 18.32 A (l9stk 15.4), so an under-reading gauge lets the true current reach the")
    w("     breaker's least limit while it indicates under 18 A; calibrated (U1, %.4f A) the error is under that gap" % U["gauge_cal"])
    w("   OPEN: F01 / D-17 and I-03 until a draft composes and its acceptance holds on its case, and the collaborator's targeted check (V3);")
    w("     U5 (R-214), the PA bench row, the case row's quoted figure (a revision is the coordinator's)")
    w("")
    w("7. PREDICATES")
    for k, v in R["pred"].items():
        w("   %-128s %s" % (k, "yes" if v else "NO"))
    return "\n".join(L) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 1 if [k for k, v in R["pred"].items() if not v] else 0


if __name__ == "__main__":
    sys.exit(main())
