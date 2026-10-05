#!/usr/bin/env python3
"""l8p_guard.py: Layer 8 record l8p, round 7 (MESHSAT-1357, 5 October 2026): the CHECK of record l9stk's guard selection G2 for
finding L8P-F07, made BEFORE any draft, as this round's brief orders (item 1), on case row C-PROT rev 1.

Record l9stk's round 4 (branch fnd/l9stk2 at 43da41ca; its page section 15.9 and l9stk_guard.out, copied into inputs/ with sha256)
SELECTED (SESSION, unchecked) G2 for the battery FETs' thermal guard on board A: a TI LM26LV factory-preset temperature switch at
130 C, supplied from DOCK_EN_OUT through a TI TPS70950, pulling DOCK_EN_RET through an AOS AO3400A, with a fixed 15 kOhm 1 % in
RT1's place; board P unchanged. This script reads the makers' sheets itself (the two TI sheets held back, fetch_held_back.py; the
AO3400A and 2N7002 sheets committed) and reproduces, or does not, each figure the selection rests on:
  1. what record l9stk states (read from its output, never retyped);
  2. the switch: its printed trip limits over supply and temperature, its output stage and what it sinks and sources, its supply
     current, its start;
  3. the regulator: its input range, its accuracy and the conditions it is printed at, its dropout, its ground current and the
     conditions it is printed at (VIN 7.6, 10.6, 16.8 and 29.2 V asked), its start, its capacitors, its enable;
  4. the shunt FET: its threshold against the switch's output levels, its on-resistance rows, its off leakage;
  5. the enable loop's readings with every resistor at its tolerance, the guard's 30 uA on DOCK_EN_OUT and the shunt's off
     leakage on DOCK_EN_RET: held at 7.6 V, on at 7.6, 10.6 and 16.8 V, off when tripped, the regulator's supply, and L4-E11
     20c's window (a ramping closed loop never read held);
  6. the case row's two sides for the switch on its printed limits (the no-trip side with the gauge's condition C4, the trip
     side's gradient budget on the worst split);
  7. the verdict, the stop, and the smallest correction scope for the selection's owner (DERIVED, not drafted, not checked);
  8. the recheck V2R's V2R-m9, DELTA-02's defect class on board P: what the bench items E-8 and E-14 (a) can and cannot bound as
     written on paralleled FETs, and the per-device method they would need (L4-E11's method (B) at 08f7e38a, copied, unchecked);
  9. the predicates.
Labels: PRINTED (a maker's printed limit), TYPICAL (a maker's typical figure or curve), ASSUMED, DERIVED (this script's
arithmetic), RECORD (another record's figure, read from its copy). Nothing has been built, bought or measured.

Run from the repository root:  python3 v2/docs/records/l8p/l8p_guard.py   (l8p_guard.out is its output, regenerated with
_bin/regen_out.py). Exit 0 on a completed check, whatever its verdict; 2 when an input is missing or a pattern no longer matches."""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
VENDOR = os.path.join(ROOT, "v2", "vendor")
LM26LV = os.path.join(VENDOR, "ti", "held", "ti-lm26lv-snis144g.pdf")
TPS709 = os.path.join(VENDOR, "ti", "held", "ti-tps709-sbvs186h.pdf")
AO3400A = os.path.join(VENDOR, "power", "aos-ao3400a-n-mosfet.pdf")
N7002 = os.path.join(VENDOR, "power", "jscj-2n7002-c8545.pdf")
LM5069 = os.path.join(VENDOR, "ti", "ti-lm5069.pdf")
L9_OUT = os.path.join(HERE, "inputs", "l9stk_guard-43da41ca.out.txt")
L9_PAGE = os.path.join(HERE, "inputs", "l9stk-section15.9-43da41ca.md")
L4_20C = os.path.join(HERE, "inputs", "l4e11-section20c-ecb598c5.md")   # round 9: taken again at L4-E11 round 17, the same bytes
L9_P15 = os.path.join(HERE, "inputs", "l9stk-section15-0d72880b.md")
L4_B = os.path.join(HERE, "inputs", "l4e11-sections23d-24b-08f7e38a.md")
DRAFTS_OUT = os.path.join(HERE, "l8p_drafts.out")
CSD18510 = os.path.join(VENDOR, "battery", "ti-csd18510q5b.pdf")
CSD17570 = os.path.join(VENDOR, "battery", "ti-csd17570q5b.pdf")
PINNED = {L9_OUT: "66ee65bd07ef3fc17aba3fcf790464240aebc46a1cc455867e0283b474ca6bab",
          L9_PAGE: "fabaf09e34ff7ea1d3632d9148d7b033f245fe937ed289801d656bc527df1184",
          LM26LV: "e8ce79af19c668cbbaa964f78fff3eaae5d0f8b09e97d373efe0666d42885d2d",
          TPS709: "8c14e3efae738a27b857b789aa87369de9037a8ef3616a9f71a423587cdc6949"}

# the loop as drawn (record l8p's board P draft, apply_gen_sch_p_breaker.py; record l9stk 15.4, C-1b): R106 10 kOhm from BRK_VIN to
# DOCK_EN_OUT, R107 22 kOhm from DOCK_EN_RET to the return; both ASSUMED 1 % (the draft prints no tolerance; l8p R106_TOL, R107_TOL)
R106, R107, TOL = 10e3, 22e3, 0.01
R_FIX = 15e3                         # G2's fixed resistor in RT1's place, 1 % (record l9stk 15.9)
V_CLAMP = 29.2                       # BRK_VIN's clamp (record l9stk 15.4)
GUARD_ALLOW = 30e-6                  # the draw record l9stk allows the guard on DOCK_EN_OUT (15.9; Layer 5's row)
T_SHUNT = 86.25                      # record l9stk's ASSUMED site temperature of the shunt for its off leakage (guard 5)
DOUBLING = 10.0                      # ASSUMED: off leakage doubles every 10 K from the hottest printed row (record l9stk's and l8p's convention)
HOT_RDS = 2.0                        # a FET's on-resistance taken as twice its 25 C maximum when hot (record l8p's N7002_HOT convention; a bound, no figure read)
U = "µ"


def refuse(msg):
    sys.stderr.write("l8p_guard: REFUSED: %s\n" % msg)
    sys.exit(2)


def rel(p):
    return os.path.relpath(p, ROOT)


def sha(p, n=64):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def pdftext(path):
    if not os.path.isfile(path):
        refuse("%s is absent (held back: run v2/docs/records/l8p/fetch_held_back.py)" % rel(path))
    try:
        r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("pdftotext could not read %s (%s)" % (rel(path), e))
    return r.stdout.decode("utf-8", "replace")


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its input" % what)
    return m


N = r"([0-9.]+)"
D = "[\u2013-]"                       # TI prints its minus signs as en dashes


def read_l9stk():
    """Record l9stk's own statements of G2, read from its output and page (RECORD)."""
    t = open(L9_OUT, encoding="utf-8").read()
    pg = open(L9_PAGE, encoding="utf-8").read()
    L = {}
    m = need(t, r"^\s+130 C\s+%s C\s+%s C\s+%s and %s C\s+%s K\s+%s K\s+%s K, %s K" % ((N,) * 8), "l9stk: the 130 C preset's row")
    L["no_trip"], L["trip"], L["reset_lo"], L["reset_hi"], L["m10"], L["m18"], L["grad"], L["grad2"] = (float(m.group(k)) for k in range(1, 9))
    L["c4_j"] = float(need(t, r"the junction reads %s C held \(DERIVED" % N, "l9stk: C4's junction").group(1))
    L["c4_m"] = float(need(t, r"held \(DERIVED, the rise\s+scaled by the square of the current\): %s K under the 130 C preset" % N, "l9stk: C4's margin").group(1))
    L["j10"] = float(need(t, r"no trip: 10 A held:\s+the hottest junction at the allowances %s C" % N, "l9stk: 10 A").group(1))
    L["j18"] = float(need(t, r"no trip: 18 A for 60 s, read as held: the hottest junction at the allowances %s C" % N, "l9stk: 18 A").group(1))
    m = need(t, r"its junction leads its mounting base by %s K\s*\n\s+with two FETs carrying all.*?by %s K \(Rth\(j-mb\) %s K/W PRINTED\)" % (N, N, N),
             "l9stk: the junction's lead", re.M | re.S)
    L["lead"], L["lead2"], L["rth_jmb"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
    L["draw"] = float(need(t, r"the guard's draw: %s uA \(the switch and the regulator, PRINTED maxima\) against the %s uA" % (N, N), "l9stk: the draw").group(1)) * 1e-6
    L["allow"] = float(need(t, r"against the %s uA this round allows it" % N, "l9stk: the allowance").group(1)) * 1e-6
    m = need(t, r"off leakage %s uA at 55 C PRINTED, %s uA at %s C ASSUMED \(doubling every 10 K\), counted on the return" % (N, N, N), "l9stk: the shunt's leakage")
    L["idss55"], L["idss_hot"], L["t_shunt"] = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6, float(m.group(3))
    L["v_reg"] = float(need(t, r"the regulator in regulation from BRK_VIN %s V" % N, "l9stk: the regulation threshold").group(1))
    L["levels"] = {}
    for v in ("7.6", "10.6", "16.8", "29.2"):
        m = need(t, r"^\s+%s V\s+%s to\s+%s V\s+%s to\s+%s V\s+%s mV,\s+%s V, %s mA" % (re.escape(v), N, N, N, N, N, N, N), "l9stk: the loop at %s V" % v)
        L["levels"][float(v)] = tuple(float(m.group(k)) for k in range(1, 8))
    L["ratio_closed"] = float(need(t, r"RET/OUT closed %s against %s" % (N, N), "l9stk: the closed ratio").group(1))
    L["ratio_window"] = float(need(t, r"RET/OUT closed %s against %s" % (N, N), "l9stk: the window's ratio").group(2))
    need(t, r"G2: the loop with the fixed resistor keeps the first inverter on, the held reading, the window and the gates at every voltage\s+yes",
         "l9stk: its predicate on the window")
    need(pg, r"\s+".join(re.escape(x) for x in "so a ramping loop (a docking, the gauge's wake, a back-fed precharge) is never read held".split()),
         "l9stk 15.9: the acceptance (c) on a ramping loop")
    L["window_any"] = need(t, r"the levels of section 2 hold for any element from %s to %s kOhm" % (N, N), "l9stk: the element's range")
    L["el_lo"], L["el_hi"] = float(L["window_any"].group(1)) * 1e3, float(L["window_any"].group(2)) * 1e3
    return L


def read_sheets():
    S = {}
    lm = pdftext(LM26LV)
    need(lm, r"SNIS144G %s JULY 2007 %s REVISED SEPTEMBER 2016" % (D, D), "LM26LV: the revision")
    S["vdd_abs"] = float(need(lm, r"^Supply voltage\s+%s0\.3\s+%s\s+V" % (D, N), "LM26LV: the supply's absolute maximum").group(1))
    m = need(lm, r"^VDD\s+Supply voltage\s+%s\s+%s\s+V" % (N, N), "LM26LV: the recommended supply")
    S["vdd_min"], S["vdd_max"] = float(m.group(1)), float(m.group(2))
    S["is_max"] = float(need(lm, r"^IS\s+Quiescent power supply current\s+%s\s+%s\s+%sA" % (N, N, U), "LM26LV: IS").group(2)) * 1e-6
    need(lm, r"minimum and maximum limits apply for TA = TJ = %s50°C to 150°C,\s*\nVDD = 1\.6 V to 5\.5 V" % D, "LM26LV: the table's conditions")
    m = need(lm, r"^\s+Hysteresis\s+%s\s+%s\s+%s\s+°C" % (N, N, N), "LM26LV: the hysteresis")
    S["hyst"] = (float(m.group(1)), float(m.group(3)))
    S["voh_drop"] = float(need(lm, r"VDD ≥ 3\.3 V, Source ≤ 780 %sA\s+VDD %s %s" % (U, D, N), "LM26LV: VOH").group(1))
    S["voh_i"] = 780e-6
    S["vol"] = float(need(lm, r"VDD ≥ 1\.6 V, Source ≤ 385 %sA\s+%s" % (U, N), "LM26LV: VOL").group(1))
    S["t_en"] = float(need(lm, r"^tEN\s+Time from power ON to digital output enabled \(1\)\s+%s\s+%s\s+ms" % (N, N), "LM26LV: tEN").group(2)) * 1e-3
    m = need(lm, r"^Trip point accuracy \(2\)\s+TA = 0°C to 150°C, VDD = 5 V\s+%s%s\s+%s\s+°C" % (D, N, N), "LM26LV: the trip accuracy")
    S["acc"] = float(m.group(2))
    S["acc_vdd"] = 5.0
    S["vih_drop"] = float(need(lm, r"^VIH\s+Logic High threshold voltage\s+VDD %s %s" % (D, N), "LM26LV: TRIP_TEST's VIH").group(1))
    S["iih"] = float(need(lm, r"^IIH\s+Logic High input current\s+%s\s+%s\s+%sA" % (N, N, U), "LM26LV: TRIP_TEST's IIH").group(2)) * 1e-6
    S["tj_abs"] = float(need(lm, r"^Maximum junction temperature, TJ\(MAX\)\s+%s" % N, "LM26LV: TJ(MAX)").group(1))
    need(lm, r"pad can be a floating node\. However, for improved noise immunity the thermal", "LM26LV: the thermal pad may float")
    need(lm, r"OVERTEMP is active-high with a push-pull structure\. OVERTEMP, is", "LM26LV: the push-pull output")
    need(lm, r"Driving the\s+TRIP_TEST input high causes the digital", "LM26LV: TRIP_TEST", re.M | re.S)
    S["q130_active"] = bool(re.search(r"LM26LVQISDX-130/NOPB\s+Active", lm))
    S["q130_small_obsolete"] = bool(re.search(r"LM26LVQISD-130/NOPB\s+Obsolete", lm))
    S["c125_active"] = bool(re.search(r"LM26LVCISD-125/NOPB\s+Active", lm))
    m = need(lm, r"^\s+130\s+%s\s+%s\s+%s\s+%s\s*$" % (N, N, N, N), "LM26LV: Table 1 at 130 C")
    S["vtrip130_g4"] = float(m.group(4)) * 1e-3
    S["rja"] = float(need(lm, r"RθJA\s+Junction-to-ambient thermal resistance\s+%s" % N, "LM26LV: RthJA").group(1))
    tp = pdftext(TPS709)
    need(tp, r"SBVS186H %s MARCH 2012 %s REVISED JULY 2021" % (D, D), "TPS709: the revision")
    m = need(tp, r"^\s*VIN\s+Input voltage range\s+%s\s+%s\s+V" % (N, N), "TPS709: the input range")
    S["vin_min"], S["vin_max"] = float(m.group(1)), float(m.group(2))
    S["vin_abs"] = float(need(tp, r"^\s+VIN\s+%s0\.3\s+%s" % (D, N), "TPS709: the input's absolute maximum").group(1))
    need(tp, r"at ambient temperature \(TA\) = %s40°C to \+85°C, VIN = VOUT\(typ\) \+ 1 V or 2\.7 V \(whichever is greater\), IOUT = 1 mA" % D, "TPS709: the table's conditions")
    S["ec_ta_max"], S["ec_headroom"], S["ec_iout"] = 85.0, 1.0, 1e-3
    S["acc_out"] = float(need(tp, r"VOUT ≥ 3\.3 V\s+%s1%%\s+(1)%%" % D, "TPS709: the accuracy at 3.3 V and over").group(1)) / 100.0
    S["line"] = float(need(tp, r"Line regulation\s+\(VOUT\(nom\) \+ 1 V, 2\.7 V\) ≤ VIN ≤ 30 V\s+%s\s+%s" % (N, N), "TPS709: the line regulation").group(2)) * 1e-3
    S["load"] = float(need(tp, r"Load regulation\s+%s\s+%s\s*\n\s+greater\), 100 %sA ≤ IOUT ≤ 150 mA" % (N, N, U), "TPS709: the load regulation").group(2)) * 1e-3
    S["load_min_i"] = 100e-6
    S["vdo"] = float(need(tp, r"TPS70950, IOUT = 50 mA\s+%s\s+%s" % (N, N), "TPS709: TPS70950's dropout").group(2)) * 1e-3
    need(tp, r"VDO approximately scales with the output current because", "TPS709: the dropout scales with the current (7.3.2)")
    S["ignd"] = float(need(tp, r"IOUT = 0 mA, VOUT > 3\.3 V\s+%s\s+%s\s+%sA" % (N, N, U), "TPS709: IGND").group(2)) * 1e-6
    S["tstr"] = float(need(tp, r"VOUT\(nom\) > 3\.3 V\s+%s\s+%s" % (N, N), "TPS709: tSTR").group(2)) * 1e-6
    need(tp, r"This pin can be\s*\n?.*?left floating to enable the device", "TPS709: EN may float", re.M | re.S)
    S["cout_min"] = float(need(tp, r"for stability is %s µF" % N, "TPS709: the least output capacitance").group(1)) * 1e-6
    need(tp, r"An input capacitor is necessary if line transients greater than 10 V in", "TPS709: the input capacitor")
    S["tj_rec"] = float(need(tp, r"TJ\s+Operating junction temperature\s+%s40\s+%s" % (D, N), "TPS709: the recommended TJ").group(1))
    S["reg_active"] = bool(re.search(r"TPS70950DBVR\s+Active", tp))
    ao = pdftext(AO3400A)
    S["ao_vds"] = float(need(ao, r"Drain-Source Voltage\s+VDS\s+%s" % N, "AO3400A: VDS").group(1))
    S["ao_vgs"] = float(need(ao, r"Gate-Source Voltage\s+VGS\s+±%s" % N, "AO3400A: VGS").group(1))
    m = need(ao, r"VGS\(th\)\s+Gate Threshold Voltage\s+VDS=VGS ID=250mA\s+%s\s+%s\s+%s" % (N, N, N), "AO3400A: the threshold")
    S["ao_vth"] = (float(m.group(1)), float(m.group(3)))
    S["ao_r45"] = float(need(ao, r"VGS=4\.5V, ID=5A\s+%s\s+%s" % (N, N), "AO3400A: RDS(on) at 4.5 V").group(2)) * 1e-3
    S["ao_r25"] = float(need(ao, r"VGS=2\.5V, ID=3A\s+%s\s+%s" % (N, N), "AO3400A: RDS(on) at 2.5 V").group(2)) * 1e-3
    # IDSS: the text layer prints the unit "mA" where the page shows "uA" (the sheet's font maps the micro sign); read on the
    # page image by this record (Rev 3.1, July 2023, p.2: "IDSS Zero Gate Voltage Drain Current VDS=30V, VGS=0V 1 uA; TJ=55 C 5")
    m = need(ao, r"IDSS\s+Zero Gate Voltage Drain Current\s+mA\s*\n\s+TJ=55°C\s+%s" % N, "AO3400A: IDSS at 55 C")
    S["ao_idss55"] = float(m.group(1)) * 1e-6
    S["ao_idss_t"] = 55.0
    nj = pdftext(N7002)
    S["n_idss"] = float(need(nj, r"Zero Gate Voltage Drain Current\s+IDSS\s+VDS=60 V, VGS=0 V\s+(\d+)\s+nA", "2N7002: IDSS").group(1)) * 1e-9
    m = need(nj, r"Vth\(GS\)\s+VDS=VGS, ID=250 µA\s+%s\s+%s\s+%s" % (N, N, N), "2N7002: the threshold")
    S["n_vth"] = (float(m.group(1)), float(m.group(3)))
    S["n_r5"] = float(need(nj, r"VGS=5 V, ID=50mA\s+%s\s+%s" % (N, N), "2N7002: RDS(on) at 5 V").group(2))
    ls = pdftext(LM5069)
    S["porit"] = float(need(ls, r"PORIT\s+VIN increasing\s+%s\s+%s\s+V" % (N, N), "LM5069: PORIT").group(1))
    return S


def read_records():
    R = {}
    c = open(L4_20C, encoding="utf-8").read()
    R["ret_held"] = float(need(c, r"under \*\*%s V\*\* at least; read closed over %s V at most" % (N, N), "L4-E11 20c: the held reading").group(1))
    R["ret_closed"] = float(need(c, r"under \*\*%s V\*\* at least; read closed over %s V at most" % (N, N), "L4-E11 20c: the closed reading").group(2))
    m = need(c, r"over \*\*%s V\*\* at most \(%s V at least\)" % (N, N), "L4-E11 20c: the powered reading")
    R["out_pw_hi"], R["out_pw_lo"] = float(m.group(1)), float(m.group(2))
    R["load_ret"] = float(need(c, r"\*\*The load on DOCK_EN_RET\*\* is SENSE1 alone, at most %s uA" % N, "L4-E11 20c: the return's load").group(1)) * 1e-6
    R["load_out"] = float(need(c, r"board A's %s kOhm on it" % N, "L4-E11 20c: DOCK_EN_OUT's load").group(1)) * 1e3
    R["window_ratio"] = float(need(c, r"RET/OUT over %s when OUT reads powered" % N, "L4-E11 20c: the window").group(1))
    R["window_r"] = float(need(c, r"never reads held while RT1 is under \*\*%s kOhm\*\*" % N, "L4-E11 20c: the window's RT1").group(1)) * 1e3
    need(c, r"a trigger there stops a dead pack's precharge", "L4-E11 20c: what a held reading in a ramp does")
    R["offset"] = float(need(c, r"board P's pull, %s V:" % N, "L4-E11 20c: board P's pull").group(1))
    p = open(L9_P15, encoding="utf-8").read()
    m = need(p, r"the\s+pack\s+%s\s+to\s+%s\s+V" % (N, N), "l9stk 15 (0d72880b): the pack's range")
    R["vmin"], R["vmax"] = float(m.group(1)), float(m.group(2))
    R["air"] = float(need(p, r"L4-E12's\s+%s\s+C" % N, "l9stk 15: the inside air").group(1))
    return R


# ------------------------------------------------------------------------------------------------ the loop, DC (DERIVED)
def closed(v, i_out, i_ret, r6, rf, r7, r_out):
    """The closed loop (the shunt off): node OUT fed from BRK_VIN through R106, loaded by board A's divider r_out and the guard's
    draw i_out; node RET between rf and R107, loaded by the sinks i_ret. Returns (OUT, RET)."""
    # RET = (OUT/rf - i_ret) / (1/rf + 1/r7); OUT: (v - OUT)/r6 = (OUT - RET)/rf + OUT/r_out + i_out
    a = 1.0 / rf + 1.0 / r7
    k = (1.0 / rf) / a                  # RET = k OUT - i_ret / a
    g = 1.0 / r6 + 1.0 / rf + 1.0 / r_out - k / rf
    out = (v / r6 - i_out - (i_ret / a) / rf) / g
    return out, k * out - i_ret / a


def held(v, i_out, r6, rf, r_out, v_ret=0.0):
    """DOCK_EN_RET pulled to v_ret (board P's detector, board A's Q44, or the guard's shunt): DOCK_EN_OUT."""
    return (v / r6 - i_out + v_ret / rf) / (1.0 / r6 + 1.0 / rf + 1.0 / r_out)


def delta02():
    """The figures section 9 uses: the two TI FETs' RthJC and VSD rows (PRINTED), the band's top and Q109's power (RECORD, this
    record's own l8p_drafts.out sections 3b and 3c), and L4-E11's method as copied (its selection row and its fixture's table)."""
    D = {}
    a = pdftext(CSD18510)
    D["rjc"] = float(need(a, r"R\u03b8JC\s+Junction-to-case thermal resistance \(1\)\s+%s" % N, "CSD18510Q5B: RthJC").group(1))
    D["vsd"] = float(need(a, r"VSD\s+Diode forward voltage\s+ISD = 32 A, VGS = 0 V\s+%s\s+%s\s+V" % (N, N), "CSD18510Q5B: VSD").group(2))
    b = pdftext(CSD17570)
    D["rjc17"] = float(need(b, r"R\u03b8JC\s+Junction-to-Case Thermal Resistance \(1\)\s+%s" % N, "CSD17570Q5B: RthJC").group(1))
    o = open(DRAFTS_OUT, encoding="utf-8").read()
    D["i_top"] = float(need(o, r"most %s A against the latched FET's" % N, "l8p_drafts.out 3b: the band's top").group(1))
    D["p109"] = float(need(o, r"the breaker's 23\.93 A held:\s+Q109 [0-9.]+ mV, %s W" % N, "l8p_drafts.out 3c: Q109 at 23.93 A").group(1))
    c = open(L4_B, encoding="utf-8").read()
    need(c, r"\*\*\(B\)\.\*\* It is the only one of the three that leaves the copper as board A's, gives each device's power and junction with no\s+assumption about sharing",
         "L4-E11 23d: method (B)")
    need(c, r"A series switch \*\*SW_S\*\* in the heating supply's \+ lead", "L4-E11 24b: the fixture")
    return D


def bisect(f, lo, hi, n=80):
    """The least x in [lo, hi] with f(x) true (f monotone false then true)."""
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        lo, hi = (lo, mid) if f(mid) else (mid, hi)
    return hi


def main():
    for p, want in PINNED.items():
        if not os.path.isfile(p):
            refuse("%s is absent (held back: run v2/docs/records/l8p/fetch_held_back.py)" % rel(p))
        if sha(p) != want:
            refuse("%s is not the pinned bytes (sha256 %s, wanted %s)" % (rel(p), sha(p, 16), want[:16]))
    L, S, R = read_l9stk(), read_sheets(), read_records()
    out = []
    w = out.append
    w("l8p_guard: record l9stk's guard selection G2 CHECKED before any draft (record l8p round 7, MESHSAT-1357, 5 October 2026;\n")
    w("case row C-PROT rev 1). Desk arithmetic on the makers' sheets and the records' copies; nothing was built, bought or measured.\n")
    w("LABELS: PRINTED a maker's printed limit; TYPICAL a maker's typical figure or curve; ASSUMED; DERIVED this script's arithmetic; RECORD\n")
    w("another record's figure, read from its copy.\n\n")
    w("0. PINS (sha256/16)\n")
    for p in (L9_OUT, L9_PAGE, L4_20C, L9_P15, L4_B, DRAFTS_OUT, LM26LV, TPS709, AO3400A, N7002, LM5069, CSD18510, CSD17570, os.path.abspath(__file__)):
        w("   %s  %s%s\n" % (sha(p, 16), rel(p), "  (held back, fetch_held_back.py)" if "/held/" in p else ""))
    w("\n1. WHAT RECORD l9stk STATES OF G2 (RECORD: its l9stk_guard.out and page 15.9 at 43da41ca, copied)\n")
    w("   the 130 C preset: no trip under %.1f C, surely tripped from %.1f C, resets between %.1f and %.1f C\n" % (L["no_trip"], L["trip"], L["reset_lo"], L["reset_hi"]))
    w("   margins: %.1f K at 10 A (junction %.1f C), %.1f K in the 18 A service (%.1f C); at the gauge's condition C4 (%.1f C) %.1f K\n"
      % (L["m10"], L["j10"], L["m18"], L["j18"], L["c4_j"], L["c4_m"]))
    w("   the gradient left on the worst split %.2f K (two FETs carrying all %.2f K); the junction's lead %.2f K (%.2f K), Rth(j-mb) %.1f K/W\n"
      % (L["grad"], L["grad2"], L["lead"], L["lead2"], L["rth_jmb"]))
    w("   the guard's draw %.2f uA against %.0f uA; the regulator in regulation from BRK_VIN %.2f V; the shunt's off leakage %.0f uA at 55 C\n"
      % (L["draw"] * 1e6, L["allow"] * 1e6, L["v_reg"], L["idss55"] * 1e6))
    w("     PRINTED, %.1f uA at %.2f C ASSUMED, counted on the return\n" % (L["idss_hot"] * 1e6, L["t_shunt"]))
    w("   its predicate: \"the loop with the fixed resistor keeps the first inverter on, the held reading, the window and the gates at\n")
    w("     every voltage: yes\"; its acceptance (c): \"so a ramping loop (a docking, the gauge's wake, a back-fed precharge) is never\n")
    w("     read held\"; its window check: \"RET/OUT closed %.3f against %.4f\" (the closed loop's ratio)\n" % (L["ratio_closed"], L["ratio_window"]))

    # ------------------------------------------------------------------ 2. the switch
    lo_trip, hi_trip = 130.0 - S["acc"], 130.0 + S["acc"]
    rs_lo, rs_hi = lo_trip - S["hyst"][1], hi_trip - S["hyst"][0]
    w("\n2. THE SWITCH ON ITS SHEET: TI LM26LV, SNIS144G (July 2007, revised September 2016); held back\n")
    w("   PRINTED: trip point accuracy -%.1f to +%.1f C at TA 0 to 150 C and VDD = %.0f V (6.8; the only condition it is printed at)\n" % (S["acc"], S["acc"], S["acc_vdd"]))
    w("     the 130 C preset: no trip under %.1f C, surely tripped from %.1f C; hysteresis %.1f to %.1f C (6.6, over VDD 1.6 to 5.5 V and -50 to\n"
      % (lo_trip, hi_trip, S["hyst"][0], S["hyst"][1]))
    w("     150 C): resets between %.1f and %.1f C                                                     record l9stk's figures: REPRODUCED\n" % (rs_lo, rs_hi))
    w("   PRINTED: supply %.1f to %.1f V recommended, %.0f V absolute; IS %.0f uA at most over -50 to 150 C and 1.6 to 5.5 V; TJ(MAX) %.0f C\n"
      % (S["vdd_min"], S["vdd_max"], S["vdd_abs"], S["is_max"] * 1e6, S["tj_abs"]))
    w("   PRINTED: OVERTEMP (pin 5) active high, push-pull: VOH at least VDD - %.1f V sourcing up to %.0f uA (VDD 3.3 V or more); VOL at most\n"
      % (S["voh_drop"], S["voh_i"] * 1e6))
    w("     %.1f V sinking up to 385 uA; the open-drain output (pin 3) is active LOW and needs a pull-up: it is not the one to use\n" % S["vol"])
    w("   PRINTED: outputs enabled %.1f ms at most after VDD passes 1.3 V (tEN); their state before that is NOT PRINTED (taken as high, the\n" % (S["t_en"] * 1e3))
    w("     worse side for a false hold); TRIP_TEST asserts both outputs, read high from VDD - %.1f V, %.1f uA at most into it, and puts VTRIP\n"
      % (S["vih_drop"], S["iih"] * 1e6))
    w("     on VTEMP: %.3f V for a 130 C preset (Table 1, gain 4: a check in place that the part is the 130 C preset)\n" % S["vtrip130_g4"])
    w("   PRINTED: the thermal pad may float (for noise, to ground); RthJA %.1f C/W: its own heating at 5 V and %.0f uA %.3f K (DERIVED)\n"
      % (S["rja"], S["is_max"] * 1e6, 5.0 * S["is_max"] * S["rja"]))
    w("   orderable table: LM26LVQISDX-130/NOPB %s; LM26LVQISD-130/NOPB %s; LM26LVCISD-125/NOPB %s                REPRODUCED\n"
      % ("Active" if S["q130_active"] else "NOT ACTIVE", "Obsolete" if S["q130_small_obsolete"] else "not obsolete", "Active" if S["c125_active"] else "NOT ACTIVE"))
    w("   NOT PRINTED: the trip point at any VDD but 5 V; record l9stk writes \"at a 5 V supply\", which is the condition, not a range\n")

    # ------------------------------------------------------------------ 3. the regulator
    vout_hi = 5.0 * (1 + S["acc_out"])
    vout_lo = 5.0 * (1 - S["acc_out"])
    vin_ec = 5.0 + S["ec_headroom"]
    vin_l9 = vout_hi + S["vdo"]
    w("\n3. THE REGULATOR ON ITS SHEET: TI TPS70950 (TPS709 family, SBVS186H, March 2012, revised July 2021); held back\n")
    w("   PRINTED: input %.1f to %.0f V recommended, %.0f V absolute, against the loop's %.1f V clamp: holds; TJ recommended to %.0f C\n"
      % (S["vin_min"], S["vin_max"], S["vin_abs"], V_CLAMP, S["tj_rec"]))
    w("   PRINTED: the table's conditions are TA -40 to +%.0f C, VIN = VOUT(typ) + %.0f V (%.1f V here), IOUT = %.0f mA \"unless otherwise noted\"\n"
      % (S["ec_ta_max"], S["ec_headroom"], vin_ec, S["ec_iout"] * 1e3))
    w("     DC accuracy +-%.0f %% (VOUT 3.3 V or more): %.2f to %.2f V; line regulation %.0f mV at most from %.1f to 30 V; load regulation %.0f mV\n"
      % (S["acc_out"] * 100, vout_lo, vout_hi, S["line"] * 1e3, vin_ec, S["load"] * 1e3))
    w("     at most from %.0f uA to 150 mA; dropout %.0f mV at most at 50 mA (TPS70950); start %.1f ms at most (VOUT over 3.3 V, 47 ohm load)\n"
      % (S["load_min_i"] * 1e6, S["vdo"] * 1e3, S["tstr"] * 1e3))
    w("     ground current %.2f uA at most at IOUT = 0 (VOUT over 3.3 V), at the table's VIN of %.1f V: NOT PRINTED at 7.6 V (in dropout),\n" % (S["ignd"] * 1e6, vin_ec))
    w("     10.6, 16.8 or 29.2 V. TYPICAL: Figure 6-15 (the TPS70933, EN open) draws it flat at about 1.3, 1.75 and 2.25 uA (-40, 25,\n")
    w("     85 C) from about 8 V to 30 V; Figure 6-16 rises by microamps per milliampere of load; the dropout's ground current is described\n")
    w("     (\"limits the increase\") and not printed (read on the page image by this record; TYPICAL, not a limit)\n")
    w("   PRINTED: EN may float (a 300 nA pull-up; never tied to IN, its 6.5 V clamp); COUT %.1f uF effective or more, ESR 0.2 ohm or less;\n" % (S["cout_min"] * 1e6))
    w("     an input capacitor is needed for line transients over 10 V (DOCK_EN_OUT steps from 0 to the loop's level at every docking)\n")
    w("   the guard's input current at the switch's %.0f uA: %.2f uA PRINTED at VIN %.1f V and IOUT 1 mA's table (record l9stk's %.2f uA:\n"
      % (S["is_max"] * 1e6, (S["is_max"] + S["ignd"]) * 1e6, vin_ec, L["draw"] * 1e6))
    w("     REPRODUCED as a figure; its conditions are the table's, so at the loop's voltages it is the TYPICAL curve's, inside the %.0f uA\n" % (GUARD_ALLOW * 1e6))
    w("     allowance with %.2f uA to spare); the output at 16 uA is under the load regulation's printed 100 uA: its accuracy there NOT PRINTED\n"
      % ((GUARD_ALLOW - S["is_max"] - S["ignd"]) * 1e6))
    w("   the dropout at the guard's microamps: not printed; 7.3.2 says it \"approximately scales with the output current\" (a description, not a\n")
    w("     limit), so the printed %.0f mV at 50 mA is a bound there (record l9stk takes it so)\n" % (S["vdo"] * 1e3))
    w("   the regulation threshold: record l9stk takes VOUT + 1 %% + the dropout bound, %.2f V on DOCK_EN_OUT; the table's own condition for\n" % vin_l9)
    w("     the printed accuracy is VIN at least %.1f V\n" % vin_ec)

    # ------------------------------------------------------------------ 4. the shunt
    vg_on = vout_lo - S["voh_drop"]
    w("\n4. THE SHUNT ON ITS SHEET: AOS AO3400A, Rev 3.1 (July 2023), committed\n")
    w("   PRINTED: VDS %.0f V (the return's clamp 17.4 V: holds); VGS +-%.0f V against the switch's %.1f V: holds; threshold %.2f to %.2f V at\n"
      % (S["ao_vds"], S["ao_vgs"], S["vdd_abs"], S["ao_vth"][0], S["ao_vth"][1]))
    w("     250 uA and 25 C only; RDS(on) %.0f mOhm at most at VGS 4.5 V, %.0f mOhm at 2.5 V; IDSS %.0f uA at most at 55 C and VDS 30 V\n"
      % (S["ao_r45"] * 1e3, S["ao_r25"] * 1e3, S["ao_idss55"] * 1e6))
    w("   on: the switch's VOH at least %.2f V with VDD at its least %.2f V (DERIVED), over the 4.5 V row and inside VGS: holds (a gate\n" % (vg_on, vout_lo))
    w("     filter's divider must keep it over 4.5 V, or over 2.5 V for the 2.5 V row)                          record l9stk: REPRODUCED\n")
    w("   off: the switch's VOL at most %.1f V against the least threshold %.2f V at 25 C: holds at 25 C; hot NOT PRINTED (the threshold falls\n"
      % (S["vol"], S["ao_vth"][0]))
    w("     with temperature); the subthreshold current at VGS %.1f V NOT PRINTED (IDSS is printed at VGS 0 only)\n" % S["vol"])
    i_ao_hot = S["ao_idss55"] * 2 ** ((T_SHUNT - S["ao_idss_t"]) / DOUBLING)
    i_ao_air = S["ao_idss55"] * 2 ** ((R["air"] - S["ao_idss_t"]) / DOUBLING)
    w("   off leakage on DOCK_EN_RET: %.1f uA at %.2f C (record l9stk's site, ASSUMED doubling every %.0f K from 55 C), %.1f uA at the %.2f C air\n"
      % (i_ao_hot * 1e6, T_SHUNT, DOUBLING, i_ao_air * 1e6, R["air"]))
    w("     (DERIVED); record l9stk's %.1f uA: REPRODUCED\n" % (L["idss_hot"] * 1e6))

    # ------------------------------------------------------------------ 5. the loop
    r6p, r6m, rfp, rfm, r7p, r7m = R106 * (1 + TOL), R106 * (1 - TOL), R_FIX * (1 + TOL), R_FIX * (1 - TOL), R107 * (1 + TOL), R107 * (1 - TOL)
    i_ret_base = R["load_ret"] + S["n_idss"]
    i_ret = i_ret_base + i_ao_hot
    vth_hi, vth_lo = S["n_vth"][1], S["n_vth"][0]
    w("\n5. THE LOOP WITH G2 (DERIVED; R106 10 kOhm, R107 22 kOhm and the fixed 15 kOhm each 1 % at its worse sign, ASSUMED for R106 and R107;\n")
    w("   board A's %.0f kOhm on DOCK_EN_OUT and %.0f uA on DOCK_EN_RET, RECORD L4-E11 20c; board P's Q107 %.0f nA, the 2N7002's printed IDSS;\n"
      % (R["load_out"] / 1e3, R["load_ret"] * 1e6, S["n_idss"] * 1e9))
    w("   the guard at its %.0f uA allowance on DOCK_EN_OUT; the shunt's %.1f uA on DOCK_EN_RET (5 below at the air); the first inverter Q103's\n"
      % (GUARD_ALLOW * 1e6, i_ao_hot * 1e6))
    w("   gate on DOCK_EN_RET, %.1f to %.1f V, PRINTED; the breaker runs from PORIT %.1f V, PRINTED)\n" % (vth_lo, vth_hi, S["porit"]))
    w("   (a) ON: the first inverter's gate, closed, at its least, against %.1f V\n" % vth_hi)
    on_ok = True
    for v in (S["porit"], R["vmin"], R["vmax"], V_CLAMP):
        _o, g_lo = closed(v, GUARD_ALLOW, i_ret, r6p, rfp, r7m, R["load_out"])
        o_hi, g_hi = closed(v, 0.0, 0.0, r6m, rfm, r7p, 1e18)          # the most: no load anywhere
        ok = g_lo > vth_hi and g_hi < 20.0
        on_ok &= ok
        lv = L["levels"].get(v)
        w("       BRK_VIN %5.1f V: the gate %5.2f to %5.2f V; DOCK_EN_OUT closed %5.2f to %5.2f V%s  %s\n"
          % (v, g_lo, g_hi, _o, o_hi, ("  (l9stk: %.2f to %.2f V)" % (lv[0], lv[1])) if lv else "", "holds" if ok else "FAILS"))
    w("   (b) HELD at %.1f V: board P's detector (or board A's Q44) holds DOCK_EN_RET at 0 to %.3f V; DOCK_EN_OUT must read powered (over %.3f V)\n"
      % (S["porit"], R["offset"], R["out_pw_hi"]))
    o_held = held(S["porit"], GUARD_ALLOW, r6p, rfm, R["load_out"])
    room = (S["porit"] / r6p) - R["out_pw_hi"] * (1.0 / r6p + 1.0 / rfm + 1.0 / R["load_out"])
    w("       at the %.0f uA allowance: %.3f V, holds; any draw under %.0f uA holds it (DERIVED): the regulator is in dropout there (DOCK_EN_OUT\n"
      % (GUARD_ALLOW * 1e6, o_held, room * 1e6))
    w("       %.2f V), where its ground current is not printed; TI describes it as limited                                    holds\n" % o_held)
    w("   (c) OFF, TRIPPED: the shunt carries DOCK_EN_OUT's current through the fixed resistor; the return, against %.1f V (the first inverter)\n" % vth_lo)
    w("       and %.4f V (board A reads held)\n" % R["ret_held"])
    off_ok = True
    for v in (S["porit"], R["vmin"], R["vmax"], V_CLAMP):
        o_tr = held(v, GUARD_ALLOW, r6p, rfm, R["load_out"])
        o_trh = held(v, 0.0, r6m, rfp, R["load_out"])
        i_sh = o_trh / rfm
        v_ret = i_sh * S["ao_r45"] * HOT_RDS
        ok = v_ret < min(vth_lo, R["ret_held"]) and o_tr > R["out_pw_hi"]
        off_ok &= ok
        lv = L["levels"].get(v)
        w("       BRK_VIN %5.1f V: the return %.3f mV, DOCK_EN_OUT %5.2f V (read powered: DD-7 reads held + powered), the shunt %.2f mA%s  %s\n"
          % (v, v_ret * 1e3, o_tr, i_sh * 1e3, ("  (l9stk: %.3f mV, %.2f V, %.2f mA)" % (lv[4], lv[5], lv[6])) if lv else "", "holds" if ok else "FAILS"))
    w("   (d) THE SUPPLY: the least BRK_VIN at which DOCK_EN_OUT reaches the regulator's input condition\n")
    for name, vin_need in (("record l9stk's (VOUT + 1 %% + 500 mV), %.2f V" % vin_l9, vin_l9), ("the table's (VOUT(typ) + 1 V), %.1f V" % vin_ec, vin_ec)):
        vc = bisect(lambda v: closed(v, GUARD_ALLOW, i_ret, r6p, rfp, r7m, R["load_out"])[0] >= vin_need, 1.0, 40.0)
        vt = bisect(lambda v: held(v, GUARD_ALLOW, r6p, rfm, R["load_out"]) >= vin_need, 1.0, 40.0)
        w("       %s: closed from %.2f V, tripped from %.2f V\n" % (name, vc, vt))
    vt_l9 = bisect(lambda v: held(v, GUARD_ALLOW, r6p, rfm, R["load_out"]) >= vin_l9, 1.0, 40.0)
    vt_ec = bisect(lambda v: held(v, GUARD_ALLOW, r6p, rfm, R["load_out"]) >= vin_ec, 1.0, 40.0)
    vc_ec = bisect(lambda v: closed(v, GUARD_ALLOW, i_ret, r6p, rfp, r7m, R["load_out"])[0] >= vin_ec, 1.0, 40.0)
    w("       record l9stk's %.2f V is the tripped figure on its criterion (this record: %.2f V): %s. Closed (the state that trips) the\n"
      % (L["v_reg"], vt_l9, "REPRODUCED" if abs(vt_l9 - L["v_reg"]) < 0.05 else "NOT REPRODUCED"))
    w("       regulator meets the table's condition from %.2f V, under the pack's %.1f V: every trip in the service is judged at VDD 5 V.\n" % (vc_ec, R["vmin"]))
    w("       Tripped, it meets it from %.2f V; under that the switch holds its output on less than 5 V (it runs from %.1f V), so the RESET\n" % (vt_ec, S["vdd_min"]))
    w("       point after a trip below %.2f V is not printed; the next trip, with the loop closed again, is (a restart point, not the protection)\n" % vt_ec)
    # (e) the window
    w("   (e) THE WINDOW (L4-E11 20c: \"A ramping closed loop never reads held while RT1 is under %.1f kOhm (RET/OUT over %.4f when OUT\n" % (R["window_r"] / 1e3, R["window_ratio"]))
    w("       reads powered)\"; \"a trigger there stops a dead pack's precharge\"). Board A reads OUT powered from %.3f V at least (%.3f V at most)\n"
      % (R["out_pw_lo"], R["out_pw_hi"]))
    w("       and RET held under %.4f V at least (closed over %.2f V at most); a ramp is never read held only if RET stays over %.2f V\n"
      % (R["ret_held"], R["ret_closed"], R["ret_closed"]))
    w("       wherever OUT reaches %.3f V. %.1f kOhm is a ratio bound (22 / (22 + RT1) at %.4f): it counts no sink on the return.\n"
      % (R["out_pw_lo"], R["window_r"] / 1e3, R["window_ratio"]))

    def ret_at(o, i_sink, rf, r7):
        return (o - i_sink * rf) * r7 / (rf + r7)
    k = r7m / (rfp + r7m)
    i_allow = (R["out_pw_lo"] - R["ret_closed"] / k) / rfp
    w("       the sink the return may carry, the fixed resistor at +1 %% and R107 at -1 %%: %.2f uA (DERIVED)\n" % (i_allow * 1e6))
    # the same doubling applied to every off FET already on the return, at the air (ASSUMED sites): board A's Q44 (L4-E11's 2N7002,
    # drain on DOCK_EN_RET) and board P's Q107 over Q108 (two 2N7002 in series, taken as one); 20c counts SENSE1 alone
    i_n_air = S["n_idss"] * 2 ** ((R["air"] - 25.0) / DOUBLING)
    i_all_air = R["load_ret"] + 2 * i_n_air
    rows = (("U48's SENSE1 (RECORD 20c) and board P's Q107 (PRINTED, 25 C)", i_ret_base),
            ("those and the shunt at the %.2f C air (ASSUMED doubling)" % R["air"], i_ret_base + i_ao_air),
            ("those and the shunt at record l9stk's %.2f C site (ASSUMED doubling)" % T_SHUNT, i_ret),
            ("SENSE1, Q44 and Q107 at the air on the same doubling (no guard)", i_all_air),
            ("those and the AO3400A at the air", i_all_air + i_ao_air))
    win = {}
    for name, i_s in rows:
        rr = ret_at(R["out_pw_lo"], i_s, rfp, r7m)
        rr_fav = ret_at(R["out_pw_hi"], i_s, R_FIX, R107)
        ok = rr >= R["ret_closed"]
        win[name] = ok
        w("       %-70s %5.1f uA: RET %.3f V at OUT %.3f V  %s\n" % (name, i_s * 1e6, rr, R["out_pw_lo"], "holds" if ok else "FAILS"))
    rr_fav = ret_at(R["out_pw_hi"], i_ret, R_FIX, R107)
    o_lo = R["out_pw_lo"]
    o_hi = bisect(lambda o: ret_at(o, i_ret, rfp, r7m) >= R["ret_closed"], o_lo, 10.0)
    t_star = S["ao_idss_t"] + DOUBLING * __import__("math").log2((i_allow - i_ret_base) / S["ao_idss55"])
    t_star_all = S["ao_idss_t"] + DOUBLING * __import__("math").log2((i_allow - i_all_air) / S["ao_idss55"])
    w("       at record l9stk's site the return reads %.3f V even at the most favourable corners (OUT %.3f V, held under %.4f V, every part\n"
      % (rr_fav, R["out_pw_hi"], R["ret_held"]))
    w("       nominal): read HELD. A closed loop ramping through DOCK_EN_OUT %.3f to %.2f V may read held (%.2f V is where the return passes\n"
      % (o_lo, o_hi, o_hi))
    w("       %.2f V); the shunt's site keeps the window only under %.1f C on the assumed doubling (%.1f K over the %.2f C air), and, with\n"
      % (R["ret_closed"], t_star, t_star - R["air"], R["air"]))
    w("       the same doubling applied to Q44 and Q107 at the air (%.1f uA before the guard), only under %.1f C: under the air itself\n"
      % (i_all_air * 1e6, t_star_all))
    w("       record l9stk's predicate \"the window ... at every voltage: yes\" and acceptance (c) \"a ramping loop ... is never read held\":\n")
    w("       NOT REPRODUCED on its own leakage figure. Its window check compares the CLOSED loop's ratio (%.3f) with %.4f; the window is a\n"
      % (L["ratio_closed"], L["ratio_window"]))
    w("       ramp's reading at OUT %.3f V, where a constant sink on the return weighs most. The gate filter it names keeps the shunt OFF in a\n" % R["out_pw_lo"])
    w("       ramp; the shunt's OFF leakage is what moves the return. The leakage at the ramp's VDS of about %.2f V is NOT PRINTED (AOS prints\n" % R["ret_closed"])
    w("       IDSS at VDS 30 V): the 30 V row is taken as the bound, as record l9stk counts it; a lower figure there is a physical question\n")

    # ------------------------------------------------------------------ 6. the case row's sides on the switch
    m10, m18 = lo_trip - L["j10"], lo_trip - L["j18"]
    m_c4 = lo_trip - L["c4_j"]
    g_left = 150.0 - hi_trip - L["lead"]
    g_left2 = 150.0 - hi_trip - L["lead2"]
    w("\n6. C-PROT rev 1 ON THE SWITCH'S PRINTED LIMITS (independent of section 5's finding; the junction's reading taken for the switch's\n")
    w("   temperature, the hot side for the no-trip judgement, RECORD l9stk 15.5)\n")
    w("   no trip at 10 A held: %.1f C against %.1f C, %.1f K; in the 18 A service read as held: %.1f C, %.1f K                 REPRODUCED\n"
      % (L["j10"], lo_trip, m10, L["j18"], m18))
    w("   the gauge's condition C4 (an indicated 18 A a true 18.80 A, the rise scaled by the current's square): %.1f C, %.1f K       REPRODUCED\n"
      % (L["c4_j"], m_c4))
    w("     that scaling holds RDS(on) at its 118.0 C value; the resistance rises with the junction, so the reading is somewhat higher\n")
    w("     (not bounded here: Nexperia's sheet is not held by this record)\n")
    w("   the trip: surely tripped from %.1f C at the die; the hottest junction leads its mounting base by %.2f K (worst split), %.2f K (two\n"
      % (hi_trip, L["lead"], L["lead2"]))
    w("     FETs carrying all): the mounting base may lead the switch's die by %.2f K (%.2f K) before a junction passes 150 C       REPRODUCED\n"
      % (g_left, g_left2))
    w("     that gradient is a LAYOUT and physical condition (E-13), unbounded on the desk\n")

    # ------------------------------------------------------------------ 7. the verdict and the correction scope
    i_n_hot = S["n_idss"] * 2 ** ((T_SHUNT - 25.0) / DOUBLING)
    rf_max = bisect(lambda rf: ret_at(R["out_pw_lo"], i_ret, rf * (1 + TOL), r7m) < R["ret_closed"], 1e3, 30e3)
    rf_max_all = bisect(lambda rf: ret_at(R["out_pw_lo"], i_all_air + i_ao_hot, rf * (1 + TOL), r7m) < R["ret_closed"], 1e3, 30e3)
    e24 = (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1)
    rf_e24 = max(m * 10 ** d for m in e24 for d in (3, 4) if m * 10 ** d <= rf_max)
    vt_rf = bisect(lambda v: held(v, GUARD_ALLOW, r6p, rf_e24 * (1 - TOL), R["load_out"]) >= vin_ec, 1.0, 40.0)
    w("\n7. VERDICT AND THE STOP\n")
    w("   NOT CONFIRMED, one figure: G2 as selected (the AO3400A on DOCK_EN_RET, the fixed 15 kOhm) keeps L4-E11 20c's window only while the\n")
    w("   shunt's site stays under %.1f C on the assumed doubling; at record l9stk's own %.2f C site the sinks on the return are %.1f uA against\n"
      % (t_star, T_SHUNT, i_ret * 1e6))
    w("   the %.1f uA the window allows, and a ramping closed loop reads held (finding L8P-F08, OPEN). Every other figure of record l9stk this\n" % (i_allow * 1e6))
    w("   script reads REPRODUCES (sections 2 to 6), with three relabellings: the trip accuracy is printed at VDD 5 V only; the regulator's\n")
    w("   ground current is printed at the table's VIN %.1f V only (TYPICAL elsewhere); its accuracy is printed from 100 uA of load.\n" % vin_ec)
    w("   As the brief orders, the draft STOPS here: no apply script is written for G2 in this round (a negative check of this solution, the\n")
    w("   first). L8P-F07 stays OPEN.\n")
    w("   The smallest correction scope for the selection's owner (DERIVED, NOT DRAFTED, NOT CHECKED; one of these, each a material change):\n")
    w("     (i)   a shunt of lower leakage: the kit's 2N7002 (Q44's and Q107's part) prints IDSS %.0f nA at 60 V (25 C); on the same doubling\n" % (S["n_idss"] * 1e9))
    w("           %.2f uA at %.2f C, %.1f uA on the return in all against %.1f uA (%.1f uA with Q44 and Q107 at the air on that doubling too);\n"
      % (i_n_hot * 1e6, T_SHUNT, (i_ret_base + i_n_hot) * 1e6, i_allow * 1e6, (i_all_air + i_n_hot) * 1e6))
    t_n_site = 25.0 + DOUBLING * __import__("math").log2((i_allow - i_all_air) / S["n_idss"])
    w("           it keeps the window for a shunt site up to %.1f C on that count; its on-resistance is printed at VGS 5 V (%.0f ohm at most) and 10 V\n"
      % (t_n_site, S["n_r5"]))
    w("           only, where the switch drives %.2f V: tripped, the return %.1f mV at %.1f V with %.0f ohm hot (a bound under 5 V, ASSUMED)\n"
      % (vg_on, held(V_CLAMP, 0.0, r6m, rfp, R["load_out"]) / rfm * S["n_r5"] * HOT_RDS * 1e3, V_CLAMP, S["n_r5"] * HOT_RDS))
    w("     (ii)  the fixed resistor at most %.2f kOhm nominal with the AO3400A at %.2f C (DERIVED, +1 %%), %.0f kOhm in E24: tripped, the regulator\n"
      % (rf_max / 1e3, T_SHUNT, rf_e24 / 1e3))
    w("           then meets the table's condition only from %.2f V, over the pack's %.1f V, so a trip low in the service holds on under 5 V;\n" % (vt_rf, R["vmin"]))
    w("           with Q44 and Q107 counted hot too, at most %.2f kOhm\n" % (rf_max_all / 1e3))
    w("     (iii) the shunt's site bounded under %.1f C (a layout condition, %.1f K over the air), with the leakage's doubling still ASSUMED;\n"
      % (t_star, t_star - R["air"]))
    w("           with Q44 and Q107 counted on the same doubling the bound is %.1f C, under the %.2f C air: NOT AVAILABLE on that count\n"
      % (t_star_all, R["air"]))
    w("   The trip and no-trip sides on the case row (section 6) do not depend on this choice.\n")

    # ------------------------------------------------------------------ 8. DELTA-02's class on board P (the recheck V2R's V2R-m9)
    D9 = delta02()
    w("\n8. DELTA-02'S CLASS ON BOARD P (the recheck V2R's V2R-m9; INFERRED unless labelled): three bench items name the body diode's VSD\n")
    w("   method on FETs that share drain and source, where neither a per-device power nor a per-device junction reading is defined\n")
    w("   E-14 (a): Q101 and Q102 (CSD18510Q5B) share BRK_SNS, PACK_P and BRK_GATE; E-8: Q1 and Q109 (CSD17570Q5B) share SCP_OUT and SW,\n")
    w("     their gates apart (the gauge's CHG, U105); Q2, alone between SW and BRK_VIN, is a device of its own; E11-45 (c): L4-E11's item\n")
    w("   what such an item reads as written: the pair's own drop at a common voltage (a pair calibrated as a pair in an isothermal oven\n")
    w("     reads a temperature BETWEEN its two junctions, since at one voltage the hotter diode carries more: a lower bound for the hotter);\n")
    w("     and the pair's total power exactly (the current times the common drop); never either device's power or junction\n")
    w("   what it can bound if the item adds a reading of the two mounting bases' difference dT_mb: the hotter junction at most the pair's\n")
    w("     reading + RthJC x the pair's total power + dT_mb, RthJC %.1f K/W at most (PRINTED, CSD18510Q5B SLPS632 and CSD17570Q5B, each 0.8)\n" % D9["rjc"])
    w("     E-14 (a) below the band's top %.3f A, VSD at most %.1f V (PRINTED at 32 A, a bound at an ampere): %.3f W, %.2f K + dT_mb\n"
      % (D9["i_top"], D9["vsd"], D9["i_top"] * D9["vsd"], D9["i_top"] * D9["vsd"] * D9["rjc"]))
    w("     E-8 at 23.93 A held, Q109's %.3f W (RECORD, this record's section 3c; with CHG on the pair shares it): %.2f K + dT_mb\n"
      % (D9["p109"], D9["p109"] * D9["rjc17"]))
    w("   the per-device method that bounds each without dT_mb: L4-E11's method (B) (round 13 23d, its fixture as round 14 redrew it, 24b;\n")
    w("     fnd/l4e11r11 at 08f7e38a, copied; UNCHECKED: the recheck V2R confirmed (B) as conditional and found round 13's fixture and pass\n")
    w("     rules not ready, which round 14 answers and no check has read): each gate apart, one channel heated at a time, each junction read\n")
    w("     by that FET's own threshold; written for Nexperia's P-channel BUK6Y10-30P on board A. Board P's pairs are TI N-channel parts:\n")
    w("     Q1 and Q109 have their gates apart already, Q101 and Q102 share BRK_GATE, so a specimen with a link in each gate branch (not\n")
    w("     drafted). No third fixture is written here\n")

    # ------------------------------------------------------------------ 9. predicates
    preds = [
        ("the 130 C preset's printed band is 127.8 to 132.2 C and its resets 122.3 to 127.7 C, as record l9stk prints", abs(lo_trip - L["no_trip"]) < 1e-9 and abs(hi_trip - L["trip"]) < 1e-9
         and abs(rs_lo - L["reset_lo"]) < 1e-9 and abs(rs_hi - L["reset_hi"]) < 1e-9),
        ("the trip accuracy is printed at VDD 5 V only", S["acc_vdd"] == 5.0),
        ("the switch and the regulator draw %.2f uA at their printed maxima, under the 30 uA allowance" % ((S["is_max"] + S["ignd"]) * 1e6),
         abs(S["is_max"] + S["ignd"] - L["draw"]) < 1e-9 and S["is_max"] + S["ignd"] < GUARD_ALLOW),
        ("the regulator's input range covers the 29.2 V clamp", S["vin_max"] >= V_CLAMP and S["vin_abs"] > V_CLAMP),
        ("the switch's least VOH is over the AO3400A's 4.5 V row and inside its VGS", vg_on > 4.5 and vout_hi < S["ao_vgs"]),
        ("the first inverter is on at 7.6, 10.6, 16.8 and 29.2 V, closed", on_ok),
        ("a held DOCK_EN_OUT reads powered at 7.6 V", o_held > R["out_pw_hi"]),
        ("tripped, the return is under 1 V and board A's held reading, and DOCK_EN_OUT reads powered, at every voltage", off_ok),
        ("closed, the regulator meets its table's VIN condition under the pack's least 10.6 V", vc_ec < R["vmin"]),
        ("the shunt's off leakage is record l9stk's figure at its site", abs(i_ao_hot - L["idss_hot"]) < 0.05e-6),
        ("L4-E11 20c's window holds with the return's sinks before the guard", win[rows[0][0]]),
        ("L4-E11 20c's window holds with the AO3400A at record l9stk's site (G2 as selected)", win[rows[2][0]]),
        ("L4-E11 20c's window holds with Q44 and Q107 at the air on the doubling, no guard", win[rows[3][0]]),
        ("the 2N7002 shunt at record l9stk's site keeps the window with Q44 and Q107 counted hot too", ret_at(R["out_pw_lo"], i_all_air + i_n_hot, rfp, r7m) >= R["ret_closed"]),
        ("C-PROT's no-trip side is printed at 10 A and in the 18 A service, and at condition C4", m10 > 0 and m18 > 0 and m_c4 > 0),
        ("C-PROT's trip side leaves the gradient record l9stk prints", abs(g_left - L["grad"]) < 0.006 and abs(g_left2 - L["grad2"]) < 0.006),
        ("both TI FETs of board P's paired items print RthJC 0.8 K/W at most", D9["rjc"] == 0.8 and D9["rjc17"] == 0.8),
    ]
    w("\n9. PREDICATES\n")
    for text, val in preds:
        w("   %-128s %s\n" % (text, "yes" if val else "NO"))
    sys.stdout.write("".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
