#!/usr/bin/env python3
"""l4hod.py: record l4hod, Layer 4 task L4A-58 (the ledger's HO-D under W138's limiter, row (b) of the AI-scope register; W146,
MESHSAT-1357, 7 October 2026): the peers' in-service test of each supervisor's TPS2553-1, drafted on board B as record l9t5's
apply_gen_sch_b_hodtest.py. PROTOTYPE DESIGN: nothing in this kit has been built, bought, powered or measured; no figure printed here
is a measurement. It closes no cx46 item and moves no state.

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the makers' texts as the records' helper returns them);
  2. why: the FAULT pin asserts only while the limiter limits, so a lost limit is invisible in service (W138's own new failure mode,
     the ledger's HO-D, the guard's objection in L8P-BREAKER.md, the owner's part 24);
  3. the makers' rows this record reads, each with its label and page;
  4. the composition on board B in L4-E9's change-list order with W137's canmb, W138's regstage, W143's canen and this draft in EVERY
     order they admit: every step, the netlists equal, CON-004, canmb and canen still read by pin;
  5. the test path read by pin (who can start the test, what it loads, who reads what), its failing mutations and the draft's refusals;
  6. the pin plan recounted (CON-017's convention) and read against DS12110 Table 9;
  7. the levels on the makers' printed rows (MODEL from PRINTED), the dark and faulty cases;
  8. the test's electrical acceptance (the judge J0 to J9) and its failing mutations: a test that cannot detect a lost limit among them;
  9. the procedure (DRAFTED), its timing on printed figures, the interval the target is out, the service lost, the detection interval;
 10. the test path's own faults, each with its detection and bound, the procedure's failing mutations (a stuck test switch left
     undetected among them), and the residuals;
 11. the SESSION decisions, the findings, the supplier's tasks, what closes once independently checked;
 12. the predicates test_l4hod.py holds.
Run from the repository root:  python3 v2/docs/records/l4hod/l4hod.py  (about 20 s; it composes board B in temporary directories,
never the tree). Output: l4hod.out, regenerated with _bin/regen_out.py. Labels: PRINTED (a maker's limit or tested row), TYPICAL,
DESCRIBED (a maker's prose, no limit), DRAFTED (a contract row or a drafted figure, not applied), MODEL, INFERRED, ASSUMPTION, SESSION."""
import hashlib
import importlib.util
import itertools
import math
import os
import re
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
L9 = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
REC = "v2/docs/records/l4hod"
L9R = "v2/docs/records/l9t5"


def _load(rel, name):
    sp = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# record l4canen (W143): its composition helpers and its netlist reads of CON-004, canmb and the EN route (its figures() is NOT called
# here); record l4reg (W138): the served rows parsed from T10's output and record l9t5's supply path (its sheets() is NOT called here)
CEN = _load("v2/docs/records/l4canen/l4canen.py", "l4hod_l4canen")
REG = _load("v2/docs/records/l4reg/l4reg_compare.py", "l4hod_l4reg")
D, CHK, M = CEN.D, CEN.CHK, CEN.M
PDFT = CEN.PDFT

# W34's convention (Q-41 item 1): every maker's text this record reads, each with its options; the held-back sheets' texts are held back
# with them (fetched by the records pdftext.FETCH names: l4canen and l4reg for the TI sheets, w5identc for UNI-ROYAL's). Re-take after a
# sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4hod
PDFTEXT = {
    "v2/vendor/diodes/diodes-bat46w.pdf": [["-layout"]],
    "v2/vendor/passives/held/uniroyal-series-11cd644d.pdf": [["-layout", "-f", "4", "-l", "7"]],
    "v2/vendor/power/aos-ao3400a-n-mosfet.pdf": [["-layout"]],
    "v2/vendor/st/st-rm0433-rev8.pdf": [["-layout", "-f", "533", "-l", "533"]],
    "v2/vendor/st/st-stm32h743xi-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps737-sbvs067w.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tps62933.pdf": [["-layout"]],
}
SHEETS = {"bat": "v2/vendor/diodes/diodes-bat46w.pdf", "uni": "v2/vendor/passives/held/uniroyal-series-11cd644d.pdf",
          "fet": "v2/vendor/power/aos-ao3400a-n-mosfet.pdf", "rm": "v2/vendor/st/st-rm0433-rev8.pdf",
          "h743": "v2/vendor/st/st-stm32h743xi-datasheet.pdf", "lim": "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf",
          "ldo": "v2/vendor/ti/held/ti-tps737-sbvs067w.pdf", "tcan": "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf",
          "u601": "v2/vendor/ti/ti-tps62933.pdf"}
DOCS = {"hodtest": L9R + "/apply_gen_sch_b_hodtest.py", "canen": L9R + "/apply_gen_sch_b_canen.py", "canmb": L9R + "/apply_gen_sch_b_canmb.py",
        "regstage": L9R + "/apply_gen_sch_b_regstage.py", "canen_out": "v2/docs/records/l4canen/l4canen.out",
        "canen_py": "v2/docs/records/l4canen/l4canen.py", "canmb_out": L9R + "/l9t5_canmb.out", "canq_out": L9R + "/l9t5_canq.out",
        "l4reg_out": "v2/docs/records/l4reg/l4reg_compare.out", "l4reg_py": "v2/docs/records/l4reg/l4reg_compare.py",
        "t10_out": L9R + "/l9t5_t10.out", "rem": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "brk": "v2/docs/records/l8p/L8P-BREAKER.md", "own": "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md",
        "ioha": "v2/docs/ARCH-PCB-B-IOHA.md", "register": REC + "/inputs/l4ai-register-L4A-58-row.tsv",
        "gen_b": "v2/ecad/tools/gen_sch_b.py", "gennet": "v2/docs/records/l8p/gen_netlist.py"}
EN = chr(0x2013)       # the sheets' minus sign, written by its code point (no long dash in this file)
MU = "[%s%s]" % (chr(0xB5), chr(0x3BC))
TAGS = "ABC"

# ------------------------------------------------------------------------------------------------ the session's choices (section 11)
R_NOM, R_TOL = 3.0, 0.01           # Ohm: the test load, 1 % (W146-D1); UNI-ROYAL's thick-film 2512 series
AIR_LO, AIR_HI = -20.0, 76.25      # C: the envelope's coldest air (C-ALLTX rev 3 corner) and board B's inside air at its hot corner (T10)
K_TOP, K_BOT, K_TOL, K_TCR = 10e3, 20e3, 0.001, 25e-6     # the read divider, 0.1 % 25 ppm/C (R601/R602's class on board A)
R_PU, R_PU_TOL = 10e3, 0.05        # the FAULT pull-up to each peer's own rail (a 5 % allowance, ASSUMPTION: no tolerance named in the value)
R_GS, R_GPD = 1e3, 100e3           # the test switch's gate resistor and pull-down
ADC_ERR = 10e-3                    # V at the pin, ASSUMPTION: ten times rev V's TYPICAL +10/-20 LSB TUE at 16 bits (no maximum printed)
B_MAX = 0.5e-3                     # A: what the output feeds besides the load while it conducts: the two dividers and the regulator's EN pull-up at the
                                   # output's top (0.2 mA, MODEL on the drawn resistors) and 0.3 mA for the regulator held off by the EN diode (ASSUMPTION:
                                   # SBVS067W prints its shutdown current 20 nA TYPICAL only)
B_BOR = 20e-3                      # A, ASSUMPTION: the same with the EN diode open: the target held in reset by BOR level 2 (no reset current printed)
C_DOM = 16e-6                      # F, ASSUMPTION: the output node with the target's 3.3 V domain behind it (1 uF + 10 uF + 1.6 uF drawn, rounded up)
VF_COLD = 0.10                     # V, ASSUMPTION: the BAT46W's forward rise from 25 C to -20 C (no cold row printed)
IR_HOT = 20e-6                     # A, ASSUMPTION: the BAT46W's reverse current at 76.25 C and 3.4 V (5 uA at 60 C, 7.5 uA at 10 V, 60 C printed)
# DRAFTED (the procedure, section 9; W146-D4, D5, D8)
T_SINGLE, T_GAP = 4e-3, 1e-3       # s: each half closed alone in step 2, and the gap between the two halves' sub-slots
T_ABORT_CLOSER, V_ABORT = 0.2e-3, 2.5   # s and V: the closing peer's abort check after its closure; the output above which the limit is not acting
T_STAGGER3 = 2e-3                  # s: in step 3 the lower half closes this long after the upper, by its own clock (the load's moment is its closure)
T_READ = (1.0e-3, 4.0e-3)          # s after the drop each peer sees: the reading window (61 samples, 50 us apart)
T_SAMPLE = 50e-6                   # s: each peer's ADC and FAULT sampling period during step 3
T_OPEN = 12e-3                     # s after the drop: both halves open at the latest
V_LATCH, T_LATCH_HOLD = 0.3, 5e-3  # V and s: the output under this for 5 ms with the load open reads LATCHED
V_OFF, V_OK = 2.0, 3.3             # V: step 1's 'limiter off' and every step's 'limiter on' thresholds on the output
T_SETTLE = 20e-3                   # s: the output at V_OK for this long before step 2
T_FIRST, T_STAGGER, T_PERIOD = 60.0, 20.0, 3600.0   # s: the first round after the quorum first holds, the stagger, the period per supervisor
WINDOW, ALIGN = 0.1, 1e-3          # s: FW-B22's window (W139) and the window clocks' alignment (W143-D9)
CONFIRM = 2                        # windows: a continuous check's fault declared on its second consecutive failure (as W143's self-test)
LOSS_COUNT = 3                     # windows: FW-B22's loss count (W139-D6)


def refuse(msg):
    sys.stderr.write("l4hod: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def sha(rel, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:n]


def text(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def pdf(key):
    """a whole sheet's layout text (the page reads have their own functions, so that every read names its options literally)"""
    return PDFT.pdf_text(ROOT, SHEETS[key], ["-layout"], PDFTEXT, REC)


def rm_page533():
    return PDFT.pdf_text(ROOT, SHEETS["rm"], ["-layout", "-f", "533", "-l", "533"], PDFTEXT, REC)


def uni_pages4to7():
    return PDFT.pdf_text(ROOT, SHEETS["uni"], ["-layout", "-f", "4", "-l", "7"], PDFTEXT, REC)


def ti_page(t, pos):
    """the printed page of the TI page whose footer follows pos (even pages print the number first, odd pages last)"""
    for m in re.finditer(r"^(\d+)\s+Submit Document(?:ation)? Feedback|Submit Document(?:ation)? Feedback\s+(\d+)\s*$", t[pos:], re.M):
        return int(m.group(1) or m.group(2))
    refuse("no TI page footer after offset %d" % pos)


def st_page(t, pos):
    m = re.search(r"DS12110 Rev 10\s+(\d+)/357|(\d+)/357\s+DS12110 Rev 10", t[pos:])
    if not m:
        refuse("no DS12110 page footer after offset %d" % pos)
    return int(m.group(1) or m.group(2))


def uni_page(t, pos):
    return int(need(t[pos:], r"Page (\d)/9", "UNI-ROYAL's page footer").group(1))


def bat_page(t, pos):
    return int(need(t[pos:], r"BAT46W\s+(\d) of 5", "the BAT46W's page footer").group(1))


def F_(v, label, where):
    return (v, label, where)


# ------------------------------------------------------------------------------------------------ 3. the makers' printed rows
def figures():
    S = {}
    # --- TI TPS2553-1, SLVS841F (W138's limiter): its rows read with W135's and W138's patterns
    t = pdf("lim")
    S["lim_rev"] = need(t, r"(SLVS841F) %s NOVEMBER 2008 %s REVISED AUGUST 2016" % (EN, EN), "SLVS841F's revision").group(1)
    m = need(t, r"RILIM = 49\.9 kΩ\s*\n\s*connected to GND\s+\S40°C ≤TJ ≤125°C\s+(\d+)\s+(\d+)\s+(\d+)", "IOS at 49.9 kOhm over TJ")
    S["ios49"] = F_(tuple(float(x) / 1000 for x in m.groups()), "PRINTED", "SLVS841F 7.5 p.%d (min / typ / max, -40 to 125 C TJ)" % ti_page(t, m.end()))
    need(t, r"Current-limit threshold \(Maximum DC[^\n]*\n\s*output current IOUT delivered to load\)", "IOS's definition (any load, 7.5)")
    eq = {}
    for k in ("max", "nom", "min"):
        m = need(t, r"(\d+)V\s*\n\s*IOS%s \(mA\) =\s*\n\s*RILIM([\d.]+)kW" % k, "the IOS%s equation" % k)
        eq[k] = (float(m.group(1)), float(m.group(2)))
    S["ios_eq"] = F_(eq, "PRINTED", "SLVS841F 9.5.1 p.%d (the maker's equations)" % ti_page(t, m.end()))
    m = need(t, r"DBV package, \S40°C ≤TJ ≤125°C\s+(\d+)", "rDS(on) DBV over TJ")
    S["ron"] = F_(float(m.group(1)) / 1000, "PRINTED", "SLVS841F 7.5 p.%d (maximum, -40 to 125 C TJ)" % ti_page(t, m.end()))
    m = need(t, r"FAULT assertion or de-assertion due to overcurrent condition\s+(\d+)\s+([\d.]+)\s+(\d+)\s+ms", "the overcurrent deglitch")
    S["deglitch"] = F_(tuple(float(x) / 1000 for x in m.groups()), "PRINTED", "SLVS841F 7.5 p.%d (min / typ / max)" % ti_page(t, m.end()))
    m = need(t, r"ton\s+Turnon time\s+CL = 1 %sF, RL = 100 \S, \(see Figure 20\)\s+([\d.]+)\s+ms" % MU, "TPS2553 ton")
    S["ton"] = F_(float(m.group(1)) * 1e-3, "PRINTED", "SLVS841F 7.5 p.%d (maximum, CL 1 uF, RL 100 ohm)" % ti_page(t, m.end()))
    m = need(t, r"toff\s+Turnoff time\s+CL = 1 %sF, RL = 100 \S, \(see Figure 20\)\s+([\d.]+)\s+ms" % MU, "TPS2553 toff")
    S["toff"] = F_(float(m.group(1)) * 1e-3, "PRINTED", "SLVS841F 7.5 p.%d (maximum)" % ti_page(t, m.end()))
    m2 = need(t, r"CL = 1 %sF, RL = 100 Ω,\s+VIN = 6\.5 V\s+([\d.]+)\s+([\d.]+)\s*\ntr\s+Rise time, output" % MU, "the rise time at 6.5 V (7.5)")
    S["tr"] = F_(float(m2.group(2)) / 1000, "PRINTED", "SLVS841F 7.5 p.%d (maximum, VIN 6.5 V, CL 1 uF, RL 100 ohm)" % ti_page(t, m2.end()))
    m = need(t, r"Fast Overcurrent Response - (\d+) µs \(Typical\)", "the overcurrent response (typical)")
    S["tios"] = F_(float(m.group(1)) * 1e-6, "TYPICAL", "SLVS841F p.1 (Features; 7.5 prints tIOS typical only)")
    m = need(t, r"VOL\s+Output low voltage, FAULT\s+I/FAULT = (\d+) mA\s+(\d+)\s+mV", "FAULT's VOL")
    S["flt_vol"] = F_((float(m.group(2)) / 1000, float(m.group(1)) / 1000), "PRINTED", "SLVS841F 7.5 p.%d (maximum at 1 mA)" % ti_page(t, m.end()))
    m = need(t, r"Off-state leakage\s+V/FAULT = 6\.5 V\s+(\d+)\s+µA", "FAULT's off-state leakage")
    S["flt_lkg"] = F_(float(m.group(1)) * 1e-6, "PRINTED", "SLVS841F 7.5 p.%d (maximum)" % ti_page(t, m.end()))
    sinks = re.findall(r"Continuous FAULT sink current\s+0\s+(\d+)\s+mA", t)
    if len(sinks) != 2:
        refuse("the FAULT sink rows (7.1, 7.3) no longer read as two")
    S["flt_sink"] = F_((float(sinks[0]) / 1000, float(sinks[1]) / 1000), "PRINTED", "SLVS841F 7.1 p.5 (absolute) and 7.3 p.6 (recommended)")
    m = need(t, r"VIL\s+Low-level input voltage on EN or EN\s+([\d.]+)", "TPS2553 EN VIL")
    S["en_vil"] = F_(float(m.group(1)), "PRINTED", "SLVS841F 7.3 p.%d" % ti_page(t, m.end()))
    m = need(t, r"(The TPS255x-1 asserts the FAULT signal during a fault condition and remains asserted while\s*\nthe part is latched-off\. The FAULT signal is "
             r"de-asserted once device power is cycled or the enable is toggled)", "SLVS841F 9.3.3's FAULT response")
    S["flt_text"], S["flt_text_p"] = " ".join(m.group(1).split()), ti_page(t, m.end())
    m = need(t, r"(The FAULT open-drain output is asserted \(active low\) during an overcurrent, overtemperature, or reverse-voltage\s*\ncondition\.)",
             "SLVS841F 9.3.3's first sentence")
    S["flt_only"] = " ".join(m.group(1).split())
    m = need(t, r"(The latch-off devices \(TPS255x-1\) assert the FAULT flag after the deglitch period and\s*\nimmediately turn off the device\.)",
             "SLVS841F 10.1.1's latch-off sentence")
    S["latch_text"], S["latch_text_p"] = " ".join(m.group(1).split()), ti_page(t, m.end())
    need(t, r"Information in the following applications sections is not part of the TI component\s*\n\s*specification", "10's disclaimer")
    m = need(t, r"(The device remains\s+off until power is cycled or the device enable is toggled\.)", "SLVS841F 9.3.1's latch")
    S["latch_exit"], S["latch_exit_p"] = " ".join(m.group(1).split()), ti_page(t, m.end())
    # --- TI TPS737, SBVS067W (W138's regulator)
    t = pdf("ldo")
    S["ldo_rev"] = need(t, r"(SBVS067W) %s JANUARY 2006 %s REVISED AUGUST 2025" % (EN, EN), "SBVS067W's revision").group(1)
    m = need(t, r"5\.4 Thermal Information\s*\n\s*TPS737 New silicon\s*\n.*?DRB \(VSON\)\s+DCQ \(SOT-223\)\s+DRV \(WSON\).*?RθJA\s+Junction-to-ambient thermal resistance\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)",
             "the new silicon's thermal table (5.4)", re.S)
    S["ldo_rja"] = F_(float(m.group(2)), "PRINTED", "SBVS067W 5.4 p.%d (DCQ, new silicon)" % ti_page(t, m.end()))
    m = need(t, r"5\.5V; 10mA ≤ IOUT ≤ 1A, new\s+%s([\d.]+)\s+±0\.5\s+([\d.]+)\s*\n\s*silicon" % EN, "the new accuracy (5.6)")
    S["ldo_acc"] = F_(float(m.group(2)) / 100, "PRINTED", "SBVS067W 5.6 p.%d (VOUT + 0.5 V <= VIN <= 5.5 V)" % ti_page(t, m.end()))
    m = need(t, r"VDO\s+IOUT = 1A, new silicon\s+(\d+)\s+(\d+)\s+mV", "the new dropout (5.6)")
    S["ldo_vdo"] = F_(float(m.group(2)) / 1000, "PRINTED", "SBVS067W 5.6 p.%d (maximum at 1 A, new silicon)" % ti_page(t, m.end()))
    m = need(t, r"VEN\(high\)\s+EN pin high \(enabled\)\s+([\d.]+)\s+VIN\s+V", "EN high (5.6)")
    S["ldo_en_hi"] = F_(float(m.group(1)), "PRINTED", "SBVS067W 5.6 p.%d" % ti_page(t, m.end()))
    m = need(t, r"VEN\(low\)\s+EN pin low \(shutdown\)\s+0\s+([\d.]+)\s+V", "EN low (5.6)")
    S["ldo_en_lo"] = F_(float(m.group(1)), "PRINTED", "SBVS067W 5.6 p.%d" % ti_page(t, m.end()))
    m = need(t, r"VIN\s+Input supply voltage\s+([\d.]+)\s+([\d.]+)\s+V", "the input range (5.3)")
    S["ldo_vin"] = F_((float(m.group(1)), float(m.group(2))), "PRINTED", "SBVS067W 5.3 p.%d" % ti_page(t, m.end()))
    m = need(t, r"ISHDN\s+Shutdown current \(IGND\)\s+VEN ≤ 0\.5V, VOUT ≤ VIN ≤ 5\.5V\s+(\d+)\s+nA", "the shutdown current (5.6)")
    S["ldo_shdn"] = F_(float(m.group(1)) * 1e-9, "TYPICAL", "SBVS067W 5.6 p.%d (typical only)" % ti_page(t, m.end()))
    m = need(t, r"IGND\s+Ground pin current\s+IOUT = 10mA \(IQ\)\s+(\d+)\s+µA", "the ground current at 10 mA (5.6)")
    S["ldo_iq"] = F_(float(m.group(1)) * 1e-6, "TYPICAL", "SBVS067W 5.6 p.%d (typical only)" % ti_page(t, m.end()))
    m = need(t, r"(To make sure that all charge is removed\s*\nfrom the gate of the pass transistor, the EN pin must be driven low before the input voltage is removed\.)",
             "the reverse current section (6.3.4)")
    S["ldo_rev_text"], S["ldo_rev_p"] = " ".join(m.group(1).split()), ti_page(t, m.end())
    # --- AOS AO3400A, Rev 3.1 (board B's Q212 part, the test switch)
    t = pdf("fet")
    S["fet_rev"] = need(t, r"(Rev 3\.1: July 2023)", "the AO3400A sheet's revision").group(1)
    need(t, r"Electrical Characteristics \(TJ=25\S+C unless otherwise noted\)", "AO3400A's table conditions (TJ 25 C)")
    S["vth"] = F_(tuple(float(x) for x in need(t, r"VGS\(th\)\s+Gate Threshold Voltage\s+VDS=VGS ID=250mA\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "AO3400A VGS(th)").groups()),
                  "PRINTED", "AO3400A p.2 (TJ 25 C)")
    S["rds25"] = F_(float(need(t, r"VGS=2\.5V, ID=3A\s+([\d.]+)\s+([\d.]+)\s+mW", "AO3400A RDS(on) at VGS 2.5 V").group(2)) * 1e-3, "PRINTED", "AO3400A p.2 (VGS 2.5 V, TJ 25 C)")
    m = need(t, r"VGS=10V, ID=5\.7A\s+(\d+)\s+([\d.]+)\s*\n\s*mW\s*\n\s*TJ=125.C\s+(\d+)\s+(\d+)", "AO3400A RDS(on) at 10 V, 25 and 125 C")
    S["rds10"] = F_((float(m.group(2)) * 1e-3, float(m.group(4)) * 1e-3), "PRINTED", "AO3400A p.2 (VGS 10 V: TJ 25 C and 125 C maxima)")
    S["fet_id70"] = F_(float(need(t, r"Current\s+TA=70.C\s+([\d.]+)\s+A", "AO3400A ID at 70 C").group(1)), "PRINTED", "AO3400A p.1 (TA 70 C)")
    S["fet_idm"] = F_(float(need(t, r"Pulsed Drain Current\s+IDM\s+(\d+)", "AO3400A IDM").group(1)), "PRINTED", "AO3400A p.1")
    S["igss"] = F_(float(need(t, r"IGSS\s+Gate-Body leakage current\s+VDS=0V, VGS= \S12V\s+(\d+)\s+nA", "AO3400A IGSS").group(1)) * 1e-9, "PRINTED", "AO3400A p.2 (TJ 25 C)")
    S["vgs_max"] = F_(float(need(t, r"Gate-Source Voltage\s+VGS\s+\S(\d+)\s+V", "AO3400A VGS maximum").group(1)), "PRINTED", "AO3400A p.1")
    # --- Diodes BAT46W, DS30044 Rev. 20-2 (board A's bootstrap diode, C83152): each peer's FAULT read
    t = pdf("bat")
    S["bat_rev"] = need(t, r"Document number: (DS30044 Rev\. 20 - 2)", "the BAT46W sheet's number").group(1)
    need(t, r"Electrical Characteristics \(@TA = \+25°C, unless otherwise specified\.\)", "the BAT46W's table conditions (TA 25 C)")
    m = need(t, r"([\d.]+)\s+IF = 0\.1mA\s*\nForward Voltage\s+VF\s+\S\s+\S\s+([\d.]+)\s+V\s+IF = 10mA", "BAT46W VF")
    S["vf"] = F_((float(m.group(1)), float(m.group(2))), "PRINTED", "DS30044 p.%d (maximum at 0.1 mA and 10 mA, TA 25 C)" % bat_page(t, m.end()))
    m = need(t, r"([\d.]+)\s+VR = 1\.5V\s*\n\s*([\d.]+)\s+VR = 1\.5V, TJ = \+60°C", "BAT46W IR at 1.5 V")
    S["ir"] = F_((float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6), "PRINTED", "DS30044 p.%d (maximum at VR 1.5 V, 25 C and TJ 60 C)" % bat_page(t, m.end()))
    S["bat_if"] = F_(float(need(t, r"Forward Continuous Current\s+IF\s+(\d+)\s+mA", "BAT46W IF").group(1)) / 1000, "PRINTED", "DS30044 p.2")
    S["bat_tj"] = F_(float(need(t, r"Operating Temperature Range\s+TJ\s+-55 to \+(\d+)", "BAT46W TJ").group(1)), "PRINTED", "DS30044 p.2")
    # --- ST STM32H743, DS12110 Rev 10, revision V's tables
    h = pdf("h743")
    b157 = M.block(h, "Table 157. I/O static characteristics", "DS12110 Table 157 (rev V)", 7000)
    vil, vih = re.findall(r"(\d\.\d)VDD\(1\)", b157)[:2]
    S["vil_k"], S["vih_k"] = F_(float(vil), "PRINTED", "DS12110 Table 157 p.243"), F_(float(vih), "PRINTED", "DS12110 Table 157 p.243")
    S["ilkg"] = F_(float(need(b157, r"0< VIN %s Max\(VDDXXX\)\(9\)\s+-\s+-\s+\+/-(\d+)" % chr(0x2264), "FT leakage").group(1)) * 1e-9, "PRINTED", "DS12110 Table 157 p.243 (FT_xx)")
    need(b157, r"6\. VIN must be less than Max\(VDDXXX\) \+ 3\.6 V\.", "Table 157 note 6")
    b158 = M.block(h, "Table 158. Output voltage characteristics for all I/Os except PC13, PC14, PC15 and PI8(1)", "DS12110 Table 158", 1500)
    S["voh_drop"] = F_(float(need(b158, r"VOH\s+Output high level voltage\s+IIO=-8 mA\s+VDD%s([\d.]+)" % chr(0x2212), "VOH at -8 mA").group(1)), "PRINTED", "DS12110 Table 158 p.245 (at -8 mA)")
    b126 = M.block(h, "Table 126. Reset and power control block characteristics", "DS12110 Table 126 (rev V)", 2500)
    m = need(b126, r"\(VPOR/VPDR thresholds\)\s+Falling edge\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "VPDR falling")
    S["vpdr"] = F_(tuple(float(x) for x in m.groups()), "PRINTED", "DS12110 Table 126 p.215 (falling)")
    m = need(b126, r"VBOR2\s+Brown-out reset threshold 2\s*\n\s+Falling edge\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "VBOR2 falling")
    S["vbor2"] = F_(tuple(float(x) for x in m.groups()), "PRINTED", "DS12110 Table 126 p.215 (falling)")
    b184 = M.block(h, "Table 184. ADC characteristics(1)(2)", "DS12110 Table 184", 40000)
    need(b184, r"VAIN\(5\)\s+-\s+-\s+-\s+0\s+-\s+VREF\+\s+V", "the conversion range (Table 184)")
    S["cadc"] = F_(float(need(b184, r"CADC\s+and hold\s+-\s+-\s+-\s+-\s+(\d+)\s+-\s+pF", "CADC").group(1)) * 1e-12, "TYPICAL", "DS12110 Table 184 p.277 (typical only)")
    b186 = M.block(h, "Table 186. ADC accuracy(1)(2)", "DS12110 Table 186", 3500)
    m = need(b186, r"Direct\s+Single ended\s+-\s+\+(\d+)/%s(\d+)\s+-" % EN, "TUE, direct channel, single ended")
    S["tue_typ"] = F_((float(m.group(1)), -float(m.group(2))), "TYPICAL", "DS12110 Table 186 p.282 (16 bits, typical only)")
    need(b186, r"1\. Data guaranteed by characterization for BGA packages\. The values for LQFP packages might differ\.", "Table 186 note 1")
    rows = {}
    for p in (15, 16, 42, 43, 44, 45):
        rows[p] = table9_row(h, p)
    S["t9"] = rows
    S["ft_unpowered"] = need(text(DOCS["gen_b"]), r"(FT_xxx: Min\(VDD, \.\.\.\) \+ 4\.0 V, so 4\.0 V unpowered)", "the FT pins' unpowered maximum").group(1)
    r533 = rm_page533()
    S["rm_reset"] = " ".join(need(r533, r"(During and just after reset, the alternate functions are not active and most of the I/O ports\s*\n\s*are configured in analog mode\.)",
                                  "RM0433 11.3.1").group(1).split())
    S["debug_pins"] = re.findall(r"(P[AB]\d+): N?J", r533)
    # --- TI TCAN334, SLLSEQ7F: the tested supervisor's transceivers as its rail falls
    t = pdf("tcan")
    S["tcan_rev"] = need(t, r"(SLLSEQ7F) %s DECEMBER 2015 %s REVISED MAY 2025" % (EN, EN), "SLLSEQ7F's revision").group(1)
    m = need(t, r"Falling under voltage detection on VCC for protected\s*\n\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)", "UV(VCC) falling")
    S["tcan_uv"] = F_(tuple(float(x) for x in m.groups()), "PRINTED", "SLLSEQ7F 5.5 p.%d (falling, protected mode)" % ti_page(t, m.end()))
    m = need(t, r"(This protects the bus during an under voltage event on VCC by placing the\s*\nbus into a high impedance biased to ground state)", "SLLSEQ7F 6.3.4")
    S["tcan_text"], S["tcan_text_p"] = " ".join(m.group(1).split()), ti_page(t, m.end())
    # --- TI TPS62933, SLUSEA4D (board A's U601, +5V_IOC's source): its switching frequency with RT open (the drafted part)
    t = pdf("u601")
    S["u601_rev"] = need(t, r"(SLUSEA4D) %s JUNE 2021 %s REVISED AUGUST 2022" % (EN, EN), "SLUSEA4D's revision").group(1)
    m = need(t, r"RT = floating\s+(\d+)\s+(\d+)\s+(\d+)", "fSW with RT floating")
    S["u601_fsw"] = F_(float(m.group(1)) * 1e3, "PRINTED", "SLUSEA4D 7.5 p.%d (minimum, RT floating)" % ti_page(t, m.end()))
    need(t, r"Load Transient Response, 0\.5 to 2\.5", "the load-transient figures (typical curves only)")
    # --- UNI-ROYAL thick-film chip resistors, V.3 Feb 2019 (the test load's series)
    u = uni_pages4to7()
    m = need(u, r"^\s*2512\s+1W\s+1\S-10M\S\s+0\.01\S-10M\S", "the 2512's power rating (6)")   # the sheet's Ohm is U+2126
    S["uni_p"] = F_(1.0, "PRINTED", "UNI-ROYAL V.3 p.%d (2512, at 70 C)" % uni_page(u, m.end()))
    m = need(u, r"The overload voltage is (2\.5) times RCWV or Max\. Overload voltage whichever is less", "the overload voltage (9)")
    S["uni_ov_k"] = F_(float(m.group(1)), "PRINTED", "UNI-ROYAL V.3 p.%d (RCWV = sqrt(P x R))" % uni_page(u, m.end()))
    need(u, r"P = power rating \(WATT\.\) R = nominal resistance \(OHM\)", "RCWV's terms")
    m = need(u, r"±0\.5%,\S?1%:\s+±\(([\d.]+)%\+([\d.]+)\S\)\s+4\.13 Permanent resistance change after the application of a\s*\n.*?for 5 seconds", "the short-time overload (11)", re.S)
    S["uni_ovl"] = F_((float(m.group(1)) / 100, float(m.group(2))), "PRINTED", "UNI-ROYAL V.3 p.%d (1 %%: change after 2.5 x RCWV for 5 s)" % uni_page(u, m.end()))
    m = need(u, r"0805,1206,1210,2010,1812,2512:\s*\n(?:.*\n){3}\s*1\S?≤R≤10\S?:\s*\S?(\d+)PPM/", "the TCR of 1 to 10 Ohm in 2512 (11)")   # private-use glyphs for the Ohm and the plus-minus
    S["uni_tcr"] = F_(float(m.group(1)) * 1e-6, "PRINTED", "UNI-ROYAL V.3 p.%d (+-, 1 to 10 Ohm, 0805 to 2512)" % uni_page(u, m.end()))
    m = need(u, r"±0\.5%,\S?1%\s*:\s*±\(([\d.]+)%\+([\d.]+)\S?\)\s+4\.25\.1 Permanent resistance change after 1,000 hours operating at", "the load life (11)")
    S["uni_life"] = F_((float(m.group(1)) / 100, float(m.group(2))), "PRINTED", "UNI-ROYAL V.3 p.%d (1 %%: after 1,000 h at RCWV, 70 C)" % uni_page(u, m.end()))
    # --- the records this round reads (its own tree)
    o = text(DOCS["canen_out"])
    m = need(o, r"each controller's rail: the envelope.*?: ([\d.]+) to ([\d.]+) V; \+5V_IOC at board B ([\d.]+) to ([\d.]+) V", "canen's rail envelope", re.S)
    S["rail"], S["v5b"] = (float(m.group(1)), float(m.group(2))), (float(m.group(3)), float(m.group(4)))
    S["t_gate_on"] = float(need(o, r"the FET's gate passes 2\.5 V within ([\d.]+) s of the second vote", "canen's restart time").group(1))
    S["t_gate_off"] = float(need(o, r"the FET's gate falls under its least threshold within ([\d.]+) s", "canen's release time").group(1))
    S["en_low_min"] = float(need(o, r"EN is held under VIL for at least ([\d.]+) s of the 2\.0 s hold", "canen's EN low time").group(1))
    S["recovery"] = float(need(o, r"= ([\d.]+) s \(MODEL on PRINTED, DRAFTED and the boot ASSUMPTION\)", "canen's recovery interval").group(1))
    S["canen_res"] = need(o, r"(\d+) residuals, (\d) of them of the recovery only", "canen's residual count").groups()
    S["canen_rows"] = re.findall(r"^ {3}(the [^\n]*?) {2,}(\w[^\n]*?) {2,}([^\n]*?) {2,}(NOT in service: RESIDUAL \(recovery\)) +none$", o, re.M)
    S["t_hold"] = CEN.T_HOLD
    S["selftest"] = float(need(text(DOCS["canmb_out"]), r"DETECTED WITHIN ([\d.]+) s of its onset", "the restated self-test interval").group(1))
    q = text(DOCS["canq_out"])
    m = need(q, r"^\s+R3\s+row 3\s+(a node out and contained)\s+(a node out and contained)\s+(\d)\s+(\d)/(\d)\s", "canq's row R3")
    S["r3"] = (m.group(1), int(m.group(4)), int(m.group(5)))
    S["rejoin"] = float(need(q, r"a dark or reset controller: boot ([\d.]+) ms \(ASSUMPTION\) \+ MON 2 windows \+ its slot: ([\d.]+) ms", "canq's rejoin").group(2)) * 1e-3
    S["boot"] = float(need(q, r"a dark or reset controller: boot ([\d.]+) ms \(ASSUMPTION\)", "canq's boot").group(1)) * 1e-3
    S["u601"] = float(need(text(DOCS["t10_out"]), r"against U601's (\d+) A \(PRINTED\)", "U601's rating in T10").group(1))
    lo = text(DOCS["l4reg_out"])
    S["j2_tj"] = float(need(lo, r"J2 holds regulator junction ([\d.]+) C at ([\d.]+) A on ([\d.]+) C/W", "W138's J2").group(1))
    S["e_latch"] = float(need(lo, r"at most ([\d.]+) mJ \(MODEL\)", "W138's latch energy").group(1)) * 1e-3
    return S


def table9_row(h, pin):
    """DS12110 Table 9's row of an LQFP-100 pin read from its line and its neighbours (a cell of the type or the additional functions may
    wrap above or below the row's line): (port, type, the row's text); refused when the pin's line is not found once"""
    lines = h.splitlines()
    idx = [i for i, l in enumerate(lines) if re.match(r"^%d\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(P[A-E]\d+)\s+I/O\b" % pin, l)]
    if len(idx) != 1:
        refuse("DS12110 Table 9: pin %d's row is found %d times" % (pin, len(idx)))
    i = idx[0]
    port = re.match(r"^%d\s+(?:\S+\s+){7}(P[A-E]\d+)" % pin, lines[i]).group(1)
    m = re.search(r"\bI/O\s+(\S+)", lines[i])
    typ = m.group(1)
    if typ == "-" or not typ.startswith(("FT", "TT")):
        up = re.search(r"\s(FT_|TT_)\s", lines[i - 1] + " ")
        dn = re.match(r"^\s+(\w+)\b", lines[i + 1])
        typ = (up.group(1) + dn.group(1)) if up and dn else "?"
    block = "\n".join(lines[max(0, i - 5):i + 5])
    return port, typ, block


# ------------------------------------------------------------------------------------------------ 4. the composition
def drafts():
    return {"M": os.path.join(ROOT, DOCS["canmb"]), "R": os.path.join(ROOT, DOCS["regstage"]), "E": os.path.join(ROOT, DOCS["canen"]),
            "H": os.path.join(ROOT, DOCS["hodtest"])}


ORDERS = tuple("".join(o) for o in itertools.permutations("MREH")
               if o.index("R") < o.index("E") and o.index("M") < o.index("E") and o.index("R") < o.index("H"))


def order(letters):
    """board B's drafts in L4-E9's change-list order: record l9t5's iocpre, canshdn, iocset and iocguard, then the four in the order
    named, then the efuse record's R-236 and R-237 and Layer 6's three last"""
    seq = D.seq_of("b", "slot")
    at = seq.index(D.MINE["b"]) + 1
    mid = [os.path.join(L9, f) for f in ("apply_gen_sch_b_iocpre.py", "apply_gen_sch_b_canshdn.py", "apply_gen_sch_b_iocset.py",
                                         "apply_gen_sch_b_iocguard.py")]
    P = drafts()
    mid += [P[x] for x in letters]
    mid += [os.path.join(ROOT, M.DOCS["u23"]), os.path.join(ROOT, M.DOCS["u24"])]
    return seq[:at] + mid + seq[at:]


def build(d, letters):
    seq = order(letters)
    p, res, ok = D.compose("b", seq, d, letters or "base")
    if not ok:
        return seq, res, False, p, None, None
    rc, net, _t = D.netlist("b", p, d, letters or "base")
    if rc:
        return seq, res, False, p, None, None
    return seq, res, True, p, net, CHK.read(open(net, "rb").read())


def mcu(k):
    return "U%d" % (41 + 10 * k)


def owner_of(nl, member):
    """the controller whose pin a node is, or None"""
    ref = member.split(".")[0]
    if re.fullmatch(r"U[456]1", ref) and CHK.value(nl, ref).startswith("STM32H743"):
        return TAGS[(int(ref[1:]) - 41) // 10]
    return None


def drivers(nl, net, seen=None):
    """the controllers whose pins reach a net through series resistors (never through a rail or ground)"""
    seen = set() if seen is None else seen
    seen.add(net)
    found = {o for o in (owner_of(nl, x) for x in CHK.members(nl, net)) if o}
    for x in CHK.members(nl, net):
        ref = x.split(".")[0]
        if ref.startswith("R"):
            for n2 in nl["pins"].get(ref, {}).values():
                if n2 not in seen and n2 != "GND" and not n2.startswith("+"):
                    found |= drivers(nl, n2, seen)
    return found


def starters(nl, k):
    """who can start controller k's test, traced on the netlist (never from the names): every path from the bottom of each resistor on
    k's limiter output to ground through AO3400A channels; each path needs every one of its FETs on, so the controllers reaching its
    gates; returns the list of the paths' controller sets (an empty set: a path needing nobody)"""
    lim_out = CHK.pin(nl, "U%d" % (45 + 10 * k), "6")
    loads = [x.split(".")[0] for x in CHK.members(nl, lim_out) if x.split(".")[0].startswith("R") and "2512" in CHK.value(nl, x.split(".")[0])]
    fets = {r: p for r, p in nl["pins"].items() if CHK.value(nl, r).startswith("AO3400A")}
    edges = {}
    for r, p in fets.items():
        dn, sn = p.get("3"), p.get("2")
        edges.setdefault(dn, []).append((sn, r))
        edges.setdefault(sn, []).append((dn, r))
    paths = []
    for ld in loads:
        bottom = [n for n in nl["pins"][ld].values() if n != lim_out][0]

        def walk(net, used):
            if net == "GND":
                paths.append(set().union(*[drivers(nl, fets[r]["1"]) for r in used]) if used else set())
                return
            for nxt, r in edges.get(net, ()):
                if r not in used and nxt != lim_out and len(used) < 4:
                    walk(nxt, used + [r])
        walk(bottom, [])
    return loads, paths


def hod_check(nl, H):
    """the draft read by pin, per controller t with its peers p (the next) and q (the one after): the 3.0 Ohm on t's limiter output,
    the upper AO3400A from its bottom to the middle node gated by p's planned pin through 1 kOhm with 100 kOhm to ground, the lower one
    to ground gated by q's; t's limiter FAULT on its own node with the two BAT46W cathodes, each anode on its peer's planned pin with
    10 kOhm to that peer's own rail; each peer's divider from t's limiter output to its planned ADC pin with 10 nF; nothing else on
    these nets; and the trace from the load to ground finds a 2-of-2 of t's two peers, never one controller, never t"""
    why = []
    pin_of = {(use, dist): p for p, (_port, use, dist) in H.TEST_PINS.items()}
    for k, t in enumerate(TAGS):
        p_, q_ = TAGS[(k + 1) % 3], TAGS[(k + 2) % 3]
        kp, kq = (k + 1) % 3, (k + 2) % 3
        rr = lambda n: "R%d" % (800 + 20 * k + n)                        # noqa: E731
        qa, qb, da, db, ca, cb = "Q%d" % (590 + 2 * k), "Q%d" % (591 + 2 * k), "D%d" % (404 + 10 * k), "D%d" % (405 + 10 * k), "C%d" % (970 + 10 * k), "C%d" % (971 + 10 * k)
        de = "D%d" % (406 + 10 * k)
        lim, out = "U%d" % (45 + 10 * k), "IOC%s_LDO_IN" % t
        tl, tm, ga, gb, flt = ("IOC%s_%s" % (t, n) for n in ("TL", "TM", "TGA", "TGB", "LIM_FLT"))
        sa, sb, fa, fb, va, vb = ("IOC%s_%s%s" % (t, n, pp) for n, pp in (("TSW", p_), ("TSW", q_), ("FLT", p_), ("FLT", q_), ("VS", p_), ("VS", q_)))

        def exact(net, want):
            if sorted(CHK.members(nl, net)) != sorted(want):
                why.append("%s reaches %s, not %s" % (net, CHK.members(nl, net), sorted(want)))
        why += CHK.rows(nl, [(lim, "6", out), (lim, "4", flt), (rr(0), "1", out), (rr(0), "2", tl), (qa, "3", tl), (qa, "2", tm), (qa, "1", ga),
                             (qb, "3", tm), (qb, "2", "GND"), (qb, "1", gb), (rr(1), "2", ga), (rr(2), "1", ga), (rr(2), "2", "GND"),
                             (rr(3), "2", gb), (rr(4), "1", gb), (rr(4), "2", "GND"), (rr(5), "1", "+3V3_IOC%s" % p_), (rr(6), "1", "+3V3_IOC%s" % q_),
                             (da, "1", flt), (da, "2", fa), (db, "1", flt), (db, "2", fb), (rr(7), "1", out), (rr(8), "2", "GND"), (rr(9), "1", out),
                             (rr(10), "2", "GND"), (ca, "2", "GND"), (cb, "2", "GND"), (de, "1", tl), (de, "2", "IOC%s_LDO_EN" % t),
                             ("U%d" % (40 + 10 * k), "5", "IOC%s_LDO_EN" % t)])
        for ref, want in ((rr(0), H.R_LOAD), (rr(1), H.R_GS), (rr(3), H.R_GS), (rr(2), H.R_GPD), (rr(4), H.R_GPD), (rr(5), H.R_FPU), (rr(6), H.R_FPU),
                          (rr(7), H.R_TOP), (rr(9), H.R_TOP), (rr(8), H.R_BOT), (rr(10), H.R_BOT), (ca, H.C_ADC), (cb, H.C_ADC)):
            if CHK.value(nl, ref) != want:
                why.append("%s is %r, not %r" % (ref, CHK.value(nl, ref), want))
        for ref, part in ((qa, H.FET), (qb, H.FET), (da, H.DIODE), (db, H.DIODE), (de, H.DIODE), (lim, "TPS2553-1")):
            if not CHK.value(nl, ref).startswith(part):
                why.append("%s is not the drafted %s" % (ref, part))
        exact(tl, ["%s.2" % rr(0), "%s.3" % qa, "%s.1" % de])
        exact(tm, ["%s.2" % qa, "%s.3" % qb])
        exact(ga, ["%s.1" % qa, "%s.2" % rr(1), "%s.1" % rr(2)])
        exact(gb, ["%s.1" % qb, "%s.2" % rr(3), "%s.1" % rr(4)])
        exact(flt, ["%s.4" % lim, "%s.1" % da, "%s.1" % db])
        exact(sa, ["%s.1" % rr(1), "%s.%d" % (mcu(kp), pin_of[("switch", 2)])])     # p is t's next; t is p's 'one after'
        exact(sb, ["%s.1" % rr(3), "%s.%d" % (mcu(kq), pin_of[("switch", 1)])])     # q is t's one after; t is q's next
        exact(fa, ["%s.2" % rr(5), "%s.2" % da, "%s.%d" % (mcu(kp), pin_of[("fault", 2)])])
        exact(fb, ["%s.2" % rr(6), "%s.2" % db, "%s.%d" % (mcu(kq), pin_of[("fault", 1)])])
        exact(va, ["%s.2" % rr(7), "%s.1" % rr(8), "%s.1" % ca, "%s.%d" % (mcu(kp), pin_of[("adc", 2)])])
        exact(vb, ["%s.2" % rr(9), "%s.1" % rr(10), "%s.1" % cb, "%s.%d" % (mcu(kq), pin_of[("adc", 1)])])
        v, w_ = start_verdict(nl, k)
        if v != "2 of 2":
            why.append("controller %s's test: %s" % (t, w_))
        rd = readers(nl, k)
        if rd != ({p_, q_}, {p_, q_}):
            why.append("controller %s's limiter is read by %s (output) and %s (FAULT), not by its two peers" % (t, sorted(rd[0]), sorted(rd[1])))
    return ("DRAWN" if not why else "FAIL"), why


def start_verdict(nl, k):
    """('2 of 2', text) when every path from the test load to ground needs both of controller k's peers and nobody else; else the
    failure: a path with nobody, one controller, or k itself"""
    t = TAGS[k]
    peers = {TAGS[(k + 1) % 3], TAGS[(k + 2) % 3]}
    loads, paths = starters(nl, k)
    if not loads:
        return "NO LOAD", "no test load on its limiter's output: the test cannot load it (a lost limit is never shown)"
    if not paths:
        return "NO PATH", "no switched path from the load to ground"
    for s in paths:
        if not s:
            return "ALWAYS", "a path from the load to ground needs no controller"
        if t in s:
            return "SELF", "a path needs controller %s itself (%s)" % (t, ",".join(sorted(s)))
        if len(s) < 2:
            return "1 of 1", "a path is started by controller %s alone" % ",".join(sorted(s))
        if s != peers:
            return "OTHER", "a path needs %s" % ",".join(sorted(s))
    return "2 of 2", "every path needs %s and %s" % tuple(sorted(peers))


def readers(nl, k):
    """the controllers reading controller k's limiter output (through a divider resistor from that output to their pin) and its FAULT
    (through a diode whose cathode is on that limiter's FAULT pin), traced on the netlist"""
    out, flt = CHK.pin(nl, "U%d" % (45 + 10 * k), "6"), CHK.pin(nl, "U%d" % (45 + 10 * k), "4")
    vread, fread = set(), set()
    for x in CHK.members(nl, out):
        ref = x.split(".")[0]
        if ref.startswith("R") and "0.1%" in CHK.value(nl, ref):
            other = [n for n in nl["pins"][ref].values() if n != out]
            for n in other:
                vread |= {o for o in (owner_of(nl, y) for y in CHK.members(nl, n)) if o}
    for x in CHK.members(nl, flt or "-"):
        ref = x.split(".")[0]
        if ref.startswith("D") and x.endswith(".1") and CHK.value(nl, ref).startswith("BAT46W"):
            an = CHK.pin(nl, ref, "2")
            fread |= {o for o in (owner_of(nl, y) for y in CHK.members(nl, an)) if o}
    return vread, fread


# ------------------------------------------------------------------------------------------------ 8. the reading model and the judge
def rt_band(S):
    """the test load over its life and the air (MODEL on PRINTED): nominal 3.0 Ohm, its 1 %, the series' 200 ppm/C over the air span
    (either sign), and the load-life change +-(1 % + 0.05 Ohm) as the ageing allowance (ASSUMPTION beyond the printed 1,000 h)"""
    tcr = S["uni_tcr"][0] * max(AIR_HI - 25.0, 25.0 - AIR_LO)
    life_k, life_ohm = S["uni_life"][0]
    lo = R_NOM * (1 - R_TOL) * (1 - tcr) * (1 - life_k) - life_ohm
    hi = R_NOM * (1 + R_TOL) * (1 + tcr) * (1 + life_k) + life_ohm
    return lo, hi, tcr


def k_band():
    tcr = K_TCR * max(AIR_HI - 25.0, 25.0 - AIR_LO)
    e = K_TOL + tcr
    k_nom = K_BOT / (K_TOP + K_BOT)
    k_lo = K_BOT * (1 - e) / (K_TOP * (1 + e) + K_BOT * (1 - e))
    k_hi = K_BOT * (1 + e) / (K_TOP * (1 - e) + K_BOT * (1 + e))
    return k_nom, k_lo, k_hi


def corners(S, rt=None, adc=ADC_ERR, bmax=B_MAX):
    """every corner of the reading's error terms: (R_T true, divider ratio true, VREF+ true, ADC error at the pin, B)"""
    lo, hi, _t = rt if rt else rt_band(S)
    k_nom, k_lo, k_hi = k_band()
    return [(r, k, v, e, b) for r in (lo, hi) for k in (k_lo, k_hi) for v in S["rail"] for e in (-adc, adc) for b in (0.0, bmax)]


def reading(ios, c):
    """a peer's reading of the limiter's current: the output (IOS - B) x R_T, divided, converted against its own rail taken at 3.3 V"""
    r, k, vref, e, b = c
    k_nom = K_BOT / (K_TOP + K_BOT)
    vpin = k * (ios - b) * r + e
    return vpin * 3.3 / vref / (k_nom * R_NOM)


def measured(v_true, c):
    """a peer's measured output for a true output, over one corner of the reading (the divider, its own rail, the ADC error)"""
    _r, k, vref, e, _b = c
    k_nom = K_BOT / (K_TOP + K_BOT)
    return (k * v_true + e) * 3.3 / vref / k_nom


def thresholds(S, **kw):
    """I_lo and I_hi: the least and the largest reading a healthy limiter (IOS inside its band) can give over every corner"""
    lo1, hi1 = S["ios"]
    cs = corners(S, **kw)
    return min(reading(lo1, c) for c in cs), max(reading(hi1, c) for c in cs)


def pass_band(S, i_lo, i_hi, **kw):
    """the IOS a passing reading can come from: inverted at I_lo and I_hi over every corner"""
    k_nom = K_BOT / (K_TOP + K_BOT)
    cs = corners(S, **kw)
    inv = lambda i, c: (i * k_nom * R_NOM * c[2] / 3.3 - c[3]) / (c[1] * c[0]) + c[4]   # noqa: E731
    return min(inv(i_lo, c) for c in cs), max(inv(i_hi, c) for c in cs)


ADMIT = {"PRINTED"}     # the labels a figure used as a LIMIT may carry; a DRAFTED, MODEL or ASSUMPTION figure is named as such where it enters


def judge(S, R, cfg):
    """the test's electrical acceptance on its case (MODEL on PRINTED; each limit's label checked at J0). cfg: the drafted choices
    (r_nom, t_single, read window, deglitch figure) so that a mutation changes one of them. Returns (verdict, rows)."""
    rows = []
    lim = {"deglitch_min": cfg["deglitch"], "ios": (S["ios"], "PRINTED", "SLVS841F 7.5 with the 1 % RILIM"), "u601": (S["u601"], "PRINTED", "TPS62933")}
    bad = [k for k, v in lim.items() if v[1] not in ADMIT]
    rows.append(("J0", not bad, "every figure used as a limit is PRINTED: %s" % ("yes" if not bad else "NO (%s carries %s)" % (bad, [lim[b][1] for b in bad]))))
    tdg = cfg["deglitch"][0]
    lo1, hi1 = S["ios"]
    rt = (R_NOM if cfg["r_nom"] is None else cfg["r_nom"])
    scale = rt / R_NOM
    rlo, rhi, _tc = rt_band(S)
    rlo, rhi = rlo * scale, rhi * scale
    avail, fixed, r_sup = R["avail"], R["fixed"], R["r_sup"]
    peers_i = 2 * R["s3"]
    rfet_hot = S["rds25"][0] * S["rds10"][0][1] / S["rds10"][0][0]
    ron = S["ron"][0]
    # J1: the demand at the least input forces a healthy limiter to limit (the target taken drawing nothing, the others at their peak)
    d_min = (fixed - peers_i * r_sup) / (rhi + 2 * rfet_hot + ron + r_sup)
    rows.append(("J1", d_min >= hi1, "the demand at the least input %.4f A against IOSmax %.4f A (R_T %.3f Ohm at its top, both switches %.4f Ohm hot INFERRED, the "
                 "limiter %.3f Ohm, the others at %.4f A each): %s" % (d_min, hi1, rhi, rfet_hot, ron, R["s3"], "%.2f times" % (d_min / hi1))))
    # J2: a lost limit's current, with the target and the others at their peak, inside U601's 3 A and the survivors' input
    d_lost = S["v5b"][1] / rlo
    total = d_lost + 3 * R["s3"]
    sv = avail(R["s3"], d_lost + 3 * R["s3"], ron)
    nd = R["need"](R["s3"])
    rows.append(("J2", total <= S["u601"] and sv >= nd, "a lost limit draws at most %.4f A (the rail's top %.4f V on R_T's least %.3f Ohm, nothing else counted); with all "
                 "three at %.4f A U601 carries %.4f A against %.0f A PRINTED; each survivor's input %.4f V against %.4f V" % (d_lost, S["v5b"][1], rlo, R["s3"], total, S["u601"], sv, nd)))
    # J3: the test load inside its printed ratings
    p_ok = hi1 ** 2 * rhi
    v_ov = S["uni_ov_k"][0] * math.sqrt(S["uni_p"][0] * rt)
    t_lost = T_ABORT_CLOSER + T_STAGGER3 + ALIGN
    rows.append(("J3", S["v5b"][1] <= v_ov and max(t_lost, cfg["deglitch"][0][2]) < 5.0, "the healthy test puts at most %.3f W in R_T for at most %.0f ms (rated %.0f W at 70 C); a "
                 "lost limit puts at most %.4f V across it for at most %.1f ms (its closer's abort, %.1f ms by the other peer), inside the series' short-time overload of %.1f x "
                 "RCWV = %.3f V for 5 s (PRINTED)" % (p_ok, cfg["deglitch"][0][2] * 1e3, S["uni_p"][0], S["v5b"][1], T_ABORT_CLOSER * 1e3, t_lost * 1e3, S["uni_ov_k"][0], v_ov)))
    # J4: the reading's acceptance and what a pass guarantees: IOS under the regulator's 125 C current
    i_lo, i_hi = thresholds(S, rt=(rlo, rhi, 0))
    ios_pmin, ios_pmax = pass_band(S, i_lo, i_hi, rt=(rlo, rhi, 0))
    i125 = R["i125"]
    rows.append(("J4", ios_pmax < i125, "a healthy limiter reads %.4f to %.4f A; a pass admits IOS %.4f to %.4f A, under the regulator's 125 C current %.4f A "
                 "(76.0 C/W PRINTED, %.4f V drop): a lost limit (IOS over it) never passes" % (i_lo, i_hi, ios_pmin, ios_pmax, i125, R["drop"])))
    # J5: the abort separates a limit acting from one lost, over every corner
    cs = corners(S, rt=(rlo, rhi, 0))
    v_ok_true = hi1 * rhi
    v_lost_true = fixed - (d_lost + 3 * R["s3"]) * r_sup - (d_lost + R["s3"]) * ron
    v_ok_hi = max(measured(v_ok_true, c) for c in cs)
    v_lost_lo = min(measured(v_lost_true, c) for c in cs)
    rows.append(("J5", v_ok_hi < V_ABORT < v_lost_lo, "the output while a healthy limiter limits is at most %.4f V and reads at most %.4f V; with the limit lost it is at least %.4f V "
                 "(the least input less the lost current %.4f A and the target's %.4f A through the limiter's %.3f Ohm) and reads at least %.4f V; the abort at %.1f V lies "
                 "between them over every corner of the reading" % (v_ok_true, v_ok_hi, v_lost_true, d_lost, R["s3"], ron, v_lost_lo, V_ABORT)))
    # J6: a stuck other half in step 2 never latches the target: the single step is shorter than the printed least deglitch
    rows.append(("J6", cfg["t_single"] + 1e-4 < tdg[0], "each half alone for %.1f ms, under the least deglitch %.1f ms (%s): a stuck "
                 "other half loads the rail for at most that and nothing latches" % (cfg["t_single"] * 1e3, tdg[0] * 1e3, cfg["deglitch"][1])))
    # J7: the reading window after the limiter's settling and before its least deglitch, with the sampling
    rows.append(("J7", cfg["read"][1] + T_SAMPLE < tdg[0] and cfg["read"][0] >= 1e-3, "the reading %.1f to %.1f ms after the drop each peer sees, before the least "
                 "deglitch %.1f ms; its start 1 ms after the drop is %d times the TYPICAL 2 us response (ASSUMPTION that the limit has settled)" % (
                     cfg["read"][0] * 1e3, cfg["read"][1] * 1e3, tdg[0] * 1e3, int(cfg["read"][0] / S["tios"][0]))))
    # J8: the limiter's own energy in a test inside the short-circuit case W138 bounded
    v_drop = S["v5b"][1] - (lo1 - B_MAX) * rlo
    e_test = v_drop * hi1 * tdg[2]
    rows.append(("J8", e_test <= S["e_latch"], "the limiter dissipates at most %.1f mJ in a test (its drop at most %.4f V at IOSmax for the %.0f ms deglitch), inside W138's "
                 "%.1f mJ latch case (an output short)" % (e_test * 1e3, v_drop, tdg[2] * 1e3, S["e_latch"] * 1e3)))
    # J9: the gate drive holds the switches at their printed RDS(on) row in both cases
    vg = (S["rail"][0] - S["voh_drop"][0]) * R_GPD / (R_GPD + R_GS)
    vgs_a = vg - d_lost * rfet_hot
    rows.append(("J9", min(vg, vgs_a) >= 2.5 and S["fet_id70"][0] >= d_lost, "the gates at least %.4f V (VOH at -8 mA, 1 kOhm and 100 kOhm); the upper switch's VGS at "
                 "least %.4f V with %.4f A in the lower: over the 2.5 V RDS(on) row; %.4f A against ID %.1f A at 70 C" % (vg, vgs_a, d_lost, d_lost, S["fet_id70"][0])))
    ok = all(r[1] for r in rows)
    return ("HOLDS" if ok else "FAILS (%s)" % ", ".join(r[0] for r in rows if not r[1])), rows


# ------------------------------------------------------------------------------------------------ 9. the procedure and its timing
def procedure(S, R):
    """the drafted steps with their durations on printed and drafted figures; returns the steps and the derived intervals"""
    t1_fall = S["t_gate_on"] + S["toff"][0] + C_DOM * (1.0 / (1.0 / (K_TOP + K_BOT) * 2)) * math.log(S["v5b"][1] / V_OFF)
    t1_back = 1e-3 + S["t_gate_off"] + S["ton"][0] + S["tr"][0]
    step1 = ALIGN + t1_fall + t1_back
    step2 = 2 * T_SINGLE + 2 * T_GAP + 2 * ALIGN
    step3 = 2 * ALIGN + T_OPEN + T_LATCH_HOLD
    step4 = ALIGN + S["t_hold"] + S["t_gate_off"] + S["ton"][0] + S["tr"][0] + S["rejoin"]
    out = WINDOW + step1 + T_SETTLE + step2 + step3 + step4
    verdict = WINDOW + step1 + T_SETTLE + step2 + 2 * ALIGN + T_OPEN + T_LATCH_HOLD
    steps = [
        ("0", "the announcement", WINDOW, "both peers mark the target under test in their state frames (one window); from here canen's automatic restart and FW-B21's "
         "stop do not act on it and the self-test's phases skip by their own precondition (all three functional)"),
        ("1", "the restore route exercised", step1, "both peers assert their restart votes (record l4canen's route); each sees the output under %.1f V within %.3f s "
         "(the gate over 2.5 V %.3f s, the limiter's turn-off %.0f ms PRINTED, the node and the target's domain (%.0f uF, ASSUMPTION) on the two dividers alone), releases, "
         "and sees it back over %.1f V within %.3f s (the gate under its threshold %.3f s, ton %.0f ms and tr %.1f ms PRINTED); else ABORT, nothing latched" % (
             V_OFF, t1_fall, S["t_gate_on"], S["toff"][0] * 1e3, C_DOM * 1e6, V_OK, t1_back, S["t_gate_off"], S["ton"][0] * 1e3, S["tr"][0] * 1e3)),
        ("1s", "settle", T_SETTLE, "the output at %.1f V or more for %.0f ms (the target restarting under its limiter)" % (V_OK, T_SETTLE * 1e3)),
        ("2", "each half alone", step2, "the next controller closes the upper half for %.0f ms, then, %.0f ms later by its own clock, the one after closes the lower half for "
         "%.0f ms; both read the output: a drop under %.1f V is the OTHER half stuck on (SWITCH STUCK ON); under the %.0f ms least deglitch, so nothing latches" % (
             T_SINGLE * 1e3, (T_SINGLE + T_GAP + ALIGN) * 1e3, T_SINGLE * 1e3, V_ABORT, S["deglitch"][0][0] * 1e3)),
        ("3", "the load", step3, "the upper half closes, then the lower (the load's moment, its closer's clock); the closer checks the output under %.1f V %.1f ms after "
         "closing, the other peer %.1f ms after its own, else opens at once (LIMIT NOT SHOWN); each reads the output %.0f to %.0f ms after the drop it sees (I = V / 3.0 Ohm), "
         "FAULT's fall %.2f to %.2f ms after it, the output under %.1f V 1 ms after FAULT (latched); both open %.0f ms after the drop at the latest; the output stays under "
         "%.1f V for %.0f ms with the load open (LATCHED)" % (V_ABORT, T_ABORT_CLOSER * 1e3, (T_ABORT_CLOSER + T_STAGGER3 + ALIGN) * 1e3, T_READ[0] * 1e3,
                                                              T_READ[1] * 1e3, S["deglitch"][0][0] * 1e3 - 0.25, S["deglitch"][0][2] * 1e3 + 0.25, V_LATCH,
                                                              T_OPEN * 1e3, V_LATCH, T_LATCH_HOLD * 1e3)),
        ("4", "the restore", step4, "both peers assert their restart votes for %.1f s (canen's hold), release; the gate under its threshold %.3f s, ton %.0f ms and tr %.1f ms "
         "PRINTED, the output back over %.1f V and FAULT high (9.3.3: 'de-asserted once ... the enable is toggled'); the target boots and rejoins within %.3f s (W139: "
         "boot %.1f s ASSUMPTION, 2 windows listening, its slot)" % (S["t_hold"], S["t_gate_off"], S["ton"][0] * 1e3, S["tr"][0] * 1e3, V_OK, S["rejoin"], S["boot"])),
    ]
    return steps, dict(step1=step1, step2=step2, step3=step3, step4=step4, out=out, verdict=verdict, t1_fall=t1_fall, t1_back=t1_back)


# ------------------------------------------------------------------------------------------------ 10. the test path's own faults
CHECKS = ("pre", "single_a", "single_b", "abort", "read", "fault", "latch", "restore", "cont_fault", "cont_vout", "two_readers")


def faults(cfg):
    """every single fault of the test path of one supervisor (and its procedure's), with what it does, what finds it and when, and
    whether it can leave a supervisor limited or unpowered in service. cfg: the set of checks the procedure runs (CHECKS); a check
    removed shows which faults it alone finds. Returns rows (element, fault, effect, found_by or None, bound, leaves_off)."""
    has = lambda *c: all(x in cfg for x in c)                         # noqa: E731
    P, C, T = "within the test period", "within %.1f s (continuous)" % (CONFIRM * WINDOW + WINDOW), "at once"
    rows = [
        ("the limiter", "its limit lost (no limiting, or IOS over the regulator's 125 C current)", "RE-7's bound gone for that supervisor: LATENT, a second fault needed",
         "step 3: LIMIT NOT SHOWN or LIMIT HIGH" if has("abort", "read") else None, P, False),
        ("the limiter", "its limit low (IOS under the pass band)", "spurious latches at the served peaks", "step 3: LIMIT LOW" if has("read") else None, P, False),
        ("the limiter", "no latch (a non-latching part fitted)", "a held overload keeps limiting; canen's restart premise gone", "step 3: NO LATCH" if has("latch") else None, P, False),
        ("the limiter's FAULT", "stuck high (never asserts)", "an overcurrent reported by nothing", "step 3: FAULT NOT SEEN" if has("fault") else None, P, False),
        ("the limiter's FAULT", "stuck low (asserted without cause)", "a false fault report", "both peers: FAULT low with the output normal" if has("cont_fault") else None, C, False),
        ("the test load (3.0 Ohm)", "open", "no test current", "step 3: LIMIT NOT SHOWN" if has("abort") else None, P, False),
        ("the test load (3.0 Ohm)", "short", "the test loads with the two switches only (limited by the limiter)", "step 3: LIMIT LOW (the reading near zero)" if has("read") else None, P, False),
        ("the upper switch", "drain-source short, or its gate held on", "LATENT: the lower half alone would load the rail", "step 2: the lower half alone drops the output" if has("single_b") else None, P, False),
        ("the upper switch", "open, or gate-source short", "the test cannot load", "step 3: LIMIT NOT SHOWN" if has("abort") else None, P, False),
        ("the lower switch", "drain-source short, or its gate held on", "LATENT: the upper half alone would load the rail", "step 2: the upper half alone drops the output" if has("single_a") else None, P, False),
        ("the lower switch", "open, or gate-source short", "the test cannot load", "step 3: LIMIT NOT SHOWN" if has("abort") else None, P, False),
        ("a switch", "gate-drain short", "the gate follows the drain; its peer's pin sees it through 1 kOhm (at most 4.1 mA)", "step 3: the reading off its band or no drop" if has("read", "abort") else None, P, False),
        ("a gate's 1 kOhm", "open", "that half never closes", "step 3: LIMIT NOT SHOWN" if has("abort") else None, P, False),
        ("a gate's 1 kOhm", "short", "none alone (it bounds a gate-drain short's current)", "NOT in service: RESIDUAL", "none", False),
        ("a gate's 100 kOhm", "open", "the gate floats only while its peer is dark, when no test runs", "NOT in service: RESIDUAL", "none", False),
        ("a gate's 100 kOhm", "short", "that half never closes", "step 3: LIMIT NOT SHOWN" if has("abort") else None, P, False),
        ("a peer's switch pin or its firmware", "stuck high, or closing without cause", "as its half held on: LATENT", "step 2 (the other half's single step)" if has("single_a", "single_b") else None, P, False),
        ("a peer's switch pin or its firmware", "stuck low, or never closing", "the test cannot load", "step 3: LIMIT NOT SHOWN" if has("abort") else None, P, False),
        ("a peer's FAULT pull-up (10 kOhm)", "open", "that peer's pin floats", "step 3: the two peers disagree on FAULT" if has("fault", "two_readers") else None, P, False),
        ("a peer's FAULT pull-up (10 kOhm)", "short", "that peer reads FAULT high always; FAULT then sinks from its rail through the diode alone", "step 3: the two peers disagree on FAULT" if has("fault", "two_readers") else None, P, False),
        ("a peer's BAT46W", "open", "that peer never sees FAULT", "step 3: the two peers disagree on FAULT" if has("fault", "two_readers") else None, P, False),
        ("a peer's BAT46W", "short", "when that peer is dark the other reads FAULT low", "the other peer: FAULT low with the output normal" if has("cont_fault") else None, "at that peer's next dark interval (its own test)", False),
        ("a peer's FAULT pin", "stuck reading high", "that peer misses FAULT", "step 3: the two peers disagree on FAULT" if has("fault", "two_readers") else None, P, False),
        ("a peer's FAULT pin", "stuck reading low", "that peer reads FAULT always", "that peer: FAULT low with the output normal" if has("cont_fault") else None, C, False),
        ("a peer's divider top (10 kOhm)", "open", "that peer reads 0 V", "that peer: the output out of its band" if has("cont_vout") else None, C, False),
        ("a peer's divider top (10 kOhm)", "short", "that peer's pin carries the output (at most 4.1174 V, inside an FT pin's limit while powered)", "that peer: the output out of its band" if has("cont_vout") else None, C, False),
        ("a peer's divider bottom (20 kOhm)", "open or short", "that peer reads full scale or 0 V", "that peer: the output out of its band" if has("cont_vout") else None, C, False),
        ("a peer's 10 nF", "short", "that peer reads 0 V", "that peer: the output out of its band" if has("cont_vout") else None, C, False),
        ("a peer's 10 nF", "open", "the sample taken from 6.67 kOhm (a long sampling time, DRAFTED)", "NOT in service: RESIDUAL", "none", False),
        ("the EN diode (BAT46W)", "open", "the target's regulator stays on in the load; BOR level 2 holds the target in reset (B at most %.0f mA, ASSUMPTION, inside the "
         "guarantee's margin)" % (B_BOR * 1e3), "NOT in service: RESIDUAL", "none", False),
        ("the EN diode (BAT46W)", "short", "in service none (the load's bottom sits at the output); with the bench jumper fitted the load sits across the output and the "
         "limiter latches (bench only)", "NOT in service: RESIDUAL", "none", False),
        ("a peer's ADC pin or its reading", "stuck inside the band", "that peer sees no drop", "step 3: the two peers disagree (one aborts)" if has("two_readers", "abort") else None, P, False),
        ("canen's restore route", "cannot pull EN low (six of its seven recovery residuals)", "the test would latch the target for good", "step 1: the output does not fall; ABORT, nothing latched" if has("pre") else None, P,
         not has("pre")),
        ("canen's restore route", "EN stuck low (the FET shorted, the gate's output high, the pull-up open)", "the target off: canen's own single faults, found at once", "canen 8: its frames absent", "at once (canen)", False),
        ("the limiter", "its latch not cleared by EN (against 9.3.1's description)", "the test leaves the target latched", "step 4: the output not back", T, True),
    ]
    return rows


# ------------------------------------------------------------------------------------------------ the report
def main():
    out = []
    w = out.append
    S = figures()
    H = CEN.load(DOCS["hodtest"], "l4hod_hodtest_draft")
    E = CEN.load(DOCS["canen"], "l4hod_canen_draft")
    MB = CEN.load(DOCS["canmb"], "l4hod_canmb_draft")
    pred = {}
    # the served rows and record l9t5's supply path, as W138 reads them (record l4reg)
    Erows = REG.rows()
    avail, (lo14, nom14, hi14), r_sup, fixed = REG.path(Erows, None, D.figures(), D.gndret())
    S["ios"] = REG.band_row(S["ios49"][0], {"min": (0, S["ios_eq"][0]["min"][1]), "max": (0, S["ios_eq"][0]["max"][1])}, 0.01)
    s3 = max(float(x) for x in re.findall(r"S3' B\d with the healthy fabric's bit\s+([\d.]+) A", text(DOCS["l4reg_out"])))
    drop = Erows["drop"][0]
    i125 = (125.0 - Erows["air"][0]) / (S["ldo_rja"][0] * drop)
    regd = dict(acc=S["ldo_acc"], vdo1a=S["ldo_vdo"])
    R = dict(avail=avail, fixed=fixed, r_sup=r_sup, s3=s3, s1=Erows["s1"][0], drop=drop, i125=i125, need=lambda i: REG.need_reg(regd, i))
    w("l4hod: record l4hod, Layer 4 task L4A-58 (the ledger's HO-D under W138's limiter): the peers' in-service test of each supervisor's")
    w("TPS2553-1 drafted as record l9t5's apply_gen_sch_b_hodtest.py, composed with W137's canmb, W138's regstage and W143's canen in every order")
    w("they admit, its levels, its acceptance, its procedure and detection interval, and its own faults (MESHSAT-1357, W146; a DRAFT, NOT APPLIED;")
    w("prototype design, nothing built or measured; it closes no cx46 item and moves no state)")
    w("")
    w("1. INPUTS (sha256/16)")
    for k in sorted(DOCS):
        w("   %s %s" % (sha(DOCS[k]), DOCS[k]))
    for rel_, h_, held in PDFT.inputs(ROOT, PDFTEXT):
        w("   %s %s%s" % ((h_ or "ABSENT")[:16], rel_, "  (held back)" if held else ""))
    for k in sorted(SHEETS):
        w("   %s %s%s" % (sha(SHEETS[k]), SHEETS[k], "  (held back)" if "/held/" in SHEETS[k] else ""))
    w("")
    # ---------------------------------------------------------------- 2. why
    w("2. WHY (quoted; the drafts it rests on are unchecked)")
    lo = text(DOCS["l4reg_out"])
    f7 = need(lo, r"(the limiter's latent loss of\s+its limit \(HO-D, L4A-58: FAULT asserts only while limiting\))", "W138's (7)", re.S).group(1)
    w("   W138's new failure mode (l4reg_compare.out section 4 (7)): \"%s\"" % " ".join(f7.split()))
    w("   %s 9.3.3 (page %d, DESCRIBED): \"%s\"; and: \"%s\"" % (S["lim_rev"], S["flt_text_p"], S["flt_only"], S["flt_text"]))
    rem = text(DOCS["rem"])
    hod = need(rem, r"(\*\*Unresolved\.\*\* A diagnostic with a bounded interval covering faults after start-up and in the diagnostic itself)", "the ledger's HO-D").group(1)
    w("   the ledger's HO-D (REMAINING-ENGINEERING.md): \"%s\"" % hod.replace("**", ""))
    brk = need(text(DOCS["brk"]), r"(No automatic diagnostic is drafted: one that tests a shunt opens\s+the breaker in service)", "the guard's objection").group(1)
    for i_, ln in enumerate(textwrap.wrap("the guard's objection (L8P-BREAKER.md, finding L8P-R9-F1): \"%s\": here the quorum tolerates one supervisor out (IOHA row 3: "
                                          "\"the other two are a majority and ownership is unaffected\"), so a test that switches its target off is admissible" % " ".join(brk.split()), 124)):
        w(("   " if i_ == 0 else "     ") + ln)
    own = need(text(DOCS["own"]), r"(Any automatic diagnostic needs a bounded detection/response interval, including faults that arise after startup and faults affecting the diagnostic itself\.)",
               "the owner's part 24").group(1)
    w("   the owner's part 24: \"%s\"" % own)
    reg_row = text(DOCS["register"]).splitlines()
    w("   the register's row (inputs/l4ai-register-L4A-58-row.tsv, sha256 %s, copied from the coordinator's _runs/l4ai/register.tsv): %s" % (
        sha(DOCS["register"], 8), reg_row[1].split("\t")[0] + " " + reg_row[1].split("\t")[5][:80] + "..."))
    w("")
    # ---------------------------------------------------------------- 3. the makers' rows
    w("3. THE MAKERS' ROWS READ (value, label, where)")
    show = [("TPS2553-1 IOS at 49.9 kOhm", "ios49"), ("TPS2553-1 rDS(on)", "ron"), ("TPS2553-1 FAULT deglitch", "deglitch"), ("TPS2553-1 ton", "ton"),
            ("TPS2553-1 toff", "toff"), ("TPS2553-1 tr", "tr"), ("TPS2553-1 tIOS", "tios"), ("TPS2553-1 FAULT VOL (V, at A)", "flt_vol"),
            ("TPS2553-1 FAULT leakage", "flt_lkg"), ("TPS2553-1 FAULT sink", "flt_sink"), ("TPS2553-1 EN VIL", "en_vil"),
            ("TPS737 theta JA (DCQ)", "ldo_rja"), ("TPS737 EN high", "ldo_en_hi"), ("TPS737 EN low", "ldo_en_lo"), ("TPS737 VIN", "ldo_vin"),
            ("TPS737 IGND at 10 mA", "ldo_iq"), ("TPS737 ISHDN", "ldo_shdn"), ("AO3400A VGS(th)", "vth"), ("AO3400A RDS(on) 2.5 V", "rds25"), ("AO3400A RDS(on) 10 V 25/125 C", "rds10"),
            ("AO3400A ID at 70 C", "fet_id70"), ("AO3400A IDM", "fet_idm"), ("AO3400A IGSS", "igss"), ("BAT46W VF (0.1, 10 mA)", "vf"),
            ("BAT46W IR (1.5 V; 25, 60 C)", "ir"), ("BAT46W IF", "bat_if"), ("BAT46W TJ max", "bat_tj"), ("H743 VIL / VDD", "vil_k"), ("H743 VIH / VDD", "vih_k"),
            ("H743 FT leakage", "ilkg"), ("H743 VOH drop at -8 mA", "voh_drop"), ("H743 VPDR falling", "vpdr"), ("H743 VBOR2 falling", "vbor2"),
            ("H743 CADC", "cadc"), ("H743 ADC TUE (LSB)", "tue_typ"), ("TCAN334 UV(VCC) falling", "tcan_uv"), ("UNI-ROYAL 2512 power", "uni_p"),
            ("UNI-ROYAL overload / RCWV", "uni_ov_k"), ("UNI-ROYAL overload change", "uni_ovl"), ("UNI-ROYAL TCR 1-10 Ohm", "uni_tcr"),
            ("UNI-ROYAL load life", "uni_life"), ("TPS62933 fSW, RT open", "u601_fsw")]
    for lab, key in show:
        v, l_, wh = S[key]
        vs = ", ".join(("%g" % x) for x in v) if isinstance(v, tuple) else ("%g" % v)
        w("   %-34s %-28s %-8s %s" % (lab, vs, l_, wh))
    w("   described: SLVS841F 10.1.1 (page %d, application information, 'not part of the TI component specification'): \"%s\"" % (S["latch_text_p"], S["latch_text"]))
    w("   described: SLVS841F 9.3.1 (page %d): \"%s\"; SBVS067W 6.3.4 (page %d): \"%s\"" % (S["latch_exit_p"], S["latch_exit"], S["ldo_rev_p"], S["ldo_rev_text"]))
    w("   described: %s 6.3.4 (page %d): \"%s\"; RM0433 Rev 8 p.533: \"%s\"" % (S["tcan_rev"], S["tcan_text_p"], S["tcan_text"], S["rm_reset"]))
    w('   DS12110 Table 186 note 1: "Data guaranteed by characterization for BGA packages. The values for LQFP packages might differ." (no maximum printed)')
    w("   the limiter's band with the 1 %% RILIM (MODEL on PRINTED, W138's): %.4f to %.4f A; the regulator's 125 C current at the corner: %.4f A (%.2f C air, %.4f V drop)" % (
        S["ios"][0], S["ios"][1], i125, Erows["air"][0], drop))
    w("")
    # ---------------------------------------------------------------- 4. the composition
    with tempfile.TemporaryDirectory(prefix="l4hod_") as d:
        runs = {}
        for o_ in ORDERS + ("MRE",):
            runs[o_] = build(d, o_)
            if not runs[o_][2]:
                refuse("board B did not compose or regenerate (%s): %s" % (o_, "; ".join("%s %s" % (s, v) for s, v, _m in runs[o_][1] if v != "OK")))
        nl0 = runs["MRE"][5]
        nls = {o_: runs[o_][5] for o_ in ORDERS}
        same = all(nls[o_]["comps"] == nls[ORDERS[0]]["comps"] and nls[o_]["pins"] == nls[ORDERS[0]]["pins"] for o_ in ORDERS)
        nl1 = nls[ORDERS[0]]
        nets = lambda nl: len({n for p in nl["pins"].values() for n in p.values() if n != "NC"})   # noqa: E731
        name = {"M": "canmb", "R": "regstage", "E": "canen", "H": "hodtest"}
        w("4. THE COMPOSITION on board B in L4-E9's change-list order: record l9t5's iocpre, canshdn, iocset and iocguard, then W137's canmb, W138's")
        w("   regstage, W143's canen and this draft in every order they admit (canen after canmb and regstage; this draft after regstage), then the")
        w("   efuse record's R-236 and R-237 and Layer 6's three; the generator run to its end through record l8p's gen_netlist.py")
        for o_ in ORDERS:
            st = [v for _s, v, _m in runs[o_][1]]
            w("     order %-38s %d steps, every one %s" % (", ".join(name[x] for x in o_) + ":", len(st), "OK" if all(v == "OK" for v in st) else "NOT OK"))
        w("   the netlists of the %d orders: %s (%d parts, %d nets); without this draft (canmb, regstage, canen): %d parts, %d nets" % (
            len(ORDERS), "IDENTICAL" if same else "DIFFERENT", len(nl1["comps"]), nets(nl1), len(nl0["comps"]), nets(nl0)))
        added = sorted(set(nl1["comps"]) - set(nl0["comps"]), key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        retyped = sorted([r for r in set(nl1["comps"]) & set(nl0["comps"]) if nl1["comps"][r].get("value") != nl0["comps"][r].get("value")
                          or nl1["pins"].get(r) != nl0["pins"].get(r)], key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        removed = sorted(set(nl0["comps"]) - set(nl1["comps"]))
        for i_, ln in enumerate(textwrap.wrap("this draft adds %d: %s" % (len(added), ", ".join(added)), 124)):
            w(("   " if i_ == 0 else "     ") + ln)
        w("   it removes %d; changes the value or nets of %d: %s" % (len(removed), len(retyped), ", ".join(retyped)))
        cv, cw = CEN.con004(nl1)
        mv, mw = CEN.mb_check(nl1, MB)
        ev, ew = CEN.en_check(nl1, E)
        w("   CON-004 on the composed netlist (record l4canen's reading): %s%s; canmb by pin on the limiter's state: %s%s; canen's EN route by pin: %s%s" % (
            cv, (": " + "; ".join(cw[:2])) if cw else "", mv, (": " + "; ".join(mw[:2])) if mw else "", ev, (": " + "; ".join(ew[:2])) if ew else ""))
        w("")
        # ------------------------------------------------------------ 5. the test path read by pin
        hv, hw = hod_check(nl1, H)
        hv_all = {o_: hod_check(nls[o_], H)[0] for o_ in ORDERS}
        w("5. THE TEST PATH READ BY PIN (per controller t: the 3.0 Ohm on t's limiter output, the upper AO3400A gated by t's next controller through 1 kOhm")
        w("   with 100 kOhm to ground, the lower to ground gated by the one after, t's FAULT on its own node with the two peers' BAT46W cathodes, each")
        w("   anode on its peer's pin with 10 kOhm to that peer's own rail, each peer's 10k over 20k with 10 nF to its ADC pin; nothing else on these")
        w("   nets but the third BAT46W from t's regulator EN to the load's bottom; traced from the load to ground: who can start the test; traced from")
        w("   the output and FAULT: who reads them)")
        w("     every order: %s%s" % (", ".join("%s %s" % (o_, v) for o_, v in hv_all.items()), (": " + "; ".join(hw[:3])) if hw else ""))
        for k, t in enumerate(TAGS):
            v, txt = start_verdict(nl1, k)
            rd = readers(nl1, k)
            w("     controller %s's test: %s (%s); its output read by {%s}, its FAULT by {%s}" % (t, v, txt, ", ".join(sorted(rd[0])), ", ".join(sorted(rd[1]))))
        net1 = runs[ORDERS[0]][4]
        swaps = (("a test a single peer can start (both halves' gates from controller B)", [(("Q591", "1"), ("R802", "1"))]),
                 ("a test a single peer can start (the upper half bridged: the load straight to the middle node)", [(("Q590", "2"), ("R800", "2"))]),
                 ("the target in its own test (A's pin 42 on its own upper half, B's pin 43 on B's lower)", [(("U51", "43"), ("U41", "42"))]),
                 ("a test that cannot detect a lost limit (the load on +5V_IOC, ahead of the limiter)", [(("R800", "1"), ("C940", "1"))]),
                 ("the load on another supervisor's output (A's on B's)", [(("R800", "1"), ("R820", "1"))]),
                 ("a peer reading the limiter's input, not its output (B's divider on +5V_IOC)", [(("R807", "1"), ("C950", "1"))]),
                 ("a peer reading another limiter's FAULT (A's and B's BAT46W swapped)", [(("D404", "1"), ("D414", "1"))]))
        muts = []
        for i, (lab, sw) in enumerate(swaps):
            qn = D.mutate(net1, d, "hm%d" % i, sw)
            nq = CHK.read(open(qn, "rb").read())
            muts.append((lab, hod_check(nq, H)[0], start_verdict(nq, 0)[0], readers(nq, 0)))
        for lab, v, sv_, rd in muts:
            w("     mutated, %-96s %s (A's test: %s; read by {%s} / {%s})" % (lab + ":", v, sv_, ",".join(sorted(rd[0])), ",".join(sorted(rd[1]))))
        hp = os.path.join(ROOT, DOCS["hodtest"])
        p_noreg = D.compose("b", order("M"), d, "noreg")[0]
        r_noreg = subprocess.run([sys.executable, "-B", hp, p_noreg, "--write"], capture_output=True)
        r_twice = subprocess.run([sys.executable, "-B", hp, runs[ORDERS[0]][3], "--write"], capture_output=True)
        r_tree = subprocess.run([sys.executable, "-B", hp, D.GEN["b"], "--write"], capture_output=True)
        refused = (r_noreg.returncode == 3 and b"regstage" in r_noreg.stderr, r_twice.returncode == 3 and b"already applied" in r_twice.stderr,
                   r_tree.returncode == 3 and b"NOT RELEASED" in r_tree.stderr)
        w("   the draft on a generator without regstage: %s; a second time: %s; on the tree's own generator: %s" % tuple(
            ("refused" if x else "NOT REFUSED") + (" (NOT RELEASED)" if i == 2 and x else "") for i, x in enumerate(refused)))
        w("   writing the tree's generator also needs canen's EN route in it (the test's restore); scratch copies take every order")
        w("")
        # ------------------------------------------------------------ 6. the pin plan
        names = M.h743_names()
        h = pdf("h743")
        w("6. THE PIN PLAN on the composed candidate, read against DS12110 Rev 10 Table 9 and RM0433 Rev 8 p.533")
        plan_ok = True
        for k, t in enumerate(TAGS):
            for p, (port, use, dist) in sorted(H.TEST_PINS.items()):
                port9, typ, blk = S["t9"][p]
                before, after = CHK.pin(nl0, mcu(k), str(p)), CHK.pin(nl1, mcu(k), str(p))
                adc_ok = True
                if use == "adc":
                    fn = H.ADC_FUNC[p]
                    a, b = fn.split("_")
                    adc_ok = (a + "_") in blk and re.search(r"\b%s\b" % b, blk) is not None
                ok = (names.get(p) == port == port9 and typ.startswith("FT") and before in (None, "NC") and after not in (None, "NC")
                      and port not in S["debug_pins"] and adc_ok)
                plan_ok &= ok
                what = {"switch": "closes its half of the test switch on %s", "fault": "reads %s's FAULT", "adc": "reads %s's output"}[use] % TAGS[(k + dist) % 3]
                w("     controller %s pin %d %-5s %-6s %-34s net %-14s free before: %s%s" % (t, p, port, typ, what, after,
                                                                                         "yes" if before in (None, "NC") else "NO (%s)" % before,
                                                                                         ("; " + H.ADC_FUNC[p] + (" read" if adc_ok else " NOT READ")) if use == "adc" else ""))
        cnt0 = {t: M.counts(nl0, names, mcu(k)) for k, t in enumerate(TAGS)}
        cnt1 = {t: M.counts(nl1, names, mcu(k)) for k, t in enumerate(TAGS)}
        w("   every pin: the generator's port name, a Table 9 row with an FT type, free before this draft, no debug pin (%s), the ADC function where read: %s" % (
            ", ".join(S["debug_pins"]), "yes" if plan_ok else "NO"))
        w("   the switch outputs are analog (high impedance) during and just after reset (RM0433 p.533), so each 100 kOhm holds its half off then")
        same_cnt = all(cnt1[t][:3] == cnt1["A"][:3] for t in TAGS)
        w("   THE COUNT (CON-017's convention), per controller: before this draft %d of 100; %d supplies, %d unconnected; with it %d of 100; %d supplies, %d" % (
            cnt0["A"][0], cnt0["A"][1], cnt0["A"][2], cnt1["A"][0], cnt1["A"][1], cnt1["A"][2]))
        w("     unconnected (the same for B and C: %s); CON-017 restated for its owner (finding W146-F3)" % ("yes" if same_cnt else "NO"))
        w("")
        # ------------------------------------------------------------ 7. the levels
        lv = levels(S, R)
        w("7. THE LEVELS on the makers' printed rows (MODEL from PRINTED; assumptions named)")
        for ln in lv["lines"]:
            for i_, x in enumerate(textwrap.wrap(ln, 124)):
                w(("   " if i_ == 0 else "     ") + x)
        w("   all levels hold: %s" % ("yes" if lv["ok"] else "NO"))
        w("")
        # ------------------------------------------------------------ 8. the acceptance judge
        base_cfg = dict(r_nom=None, t_single=T_SINGLE, read=T_READ, deglitch=S["deglitch"])
        jv, jrows = judge(S, R, base_cfg)
        rlo, rhi, tcr = rt_band(S)
        i_lo, i_hi = thresholds(S)
        pmin, pmax = pass_band(S, i_lo, i_hi)
        w("8. THE TEST'S ELECTRICAL ACCEPTANCE (the judge; MODEL on PRINTED; ASSUMPTION and DRAFTED figures named)")
        w("   the reading (each peer, its own): I = V / 3.0 Ohm from the output's mean %.0f to %.0f ms after the drop, the pin's voltage taken against the peer's own" % (
            T_READ[0] * 1e3, T_READ[1] * 1e3))
        w("     3.3 V as 3.3 V; its error terms over every corner: R_T %.4f to %.4f Ohm (1 %%, %.0f ppm/C over %.0f K PRINTED, the load life's +-(%.0f %% + %.2f Ohm) as ageing,"
          % (rlo, rhi, S["uni_tcr"][0] * 1e6, max(AIR_HI - 25, 25 - AIR_LO), S["uni_life"][0][0] * 100, S["uni_life"][0][1]))
        k_nom, k_lo, k_hi = k_band()
        w("     ASSUMPTION past 1,000 h); the divider %.5f to %.5f (0.1 %%, 25 ppm/C); the rail %.4f to %.4f V (record l4canen's envelope); the ADC +-%.0f mV at the pin" % (
            k_lo, k_hi, S["rail"][0], S["rail"][1], ADC_ERR * 1e3))
        w("     (ASSUMPTION: %s's TYPICAL %+g/%g LSB at 16 bits, no maximum printed, characterised on BGA); what the output feeds besides the load, B, 0 to" % (
            "Table 186", S["tue_typ"][0][0], S["tue_typ"][0][1]))
        w("     %.1f mA: the two dividers and the regulator's EN pull-up at the output's top (MODEL on the drawn resistors) and the regulator held off by the" % (B_MAX * 1e3))
        w("     EN diode (ASSUMPTION %.1f mA: ISHDN %.0f nA TYPICAL only); with that diode open, the target held in reset by BOR level 2 (its rail under the" % (
            B_MAX * 1e3 - 0.2, S["ldo_shdn"][0] * 1e9))
        w("     output, at most %.4f V, under VBOR2's %.2f V falling minimum, PRINTED), B at most %.0f mA (ASSUMPTION): the second barrier" % (
            S["ios"][1] * rt_band(S)[1], S["vbor2"][0][0], B_BOR * 1e3))
        w("   record l9t5's supply path at board B (W138's reading of it): the least input %.4f V less %.5f Ohm times the lead's current; the served peak" % (fixed, r_sup))
        w("     S3' %.4f A a supervisor (record l4reg's section 2)" % R["s3"])
        w("   the acceptance: a healthy limiter (%.4f to %.4f A) reads %.4f to %.4f A over every corner: PASS inside, LIMIT LOW under, LIMIT HIGH over (DRAFTED)" % (
            S["ios"][0], S["ios"][1], i_lo, i_hi))
        w("   a PASS admits IOS %.4f to %.4f A; the regulator's 125 C current is %.4f A, so every limit that passes keeps the regulator at %.1f C or less (76.0 C/W PRINTED)" % (
            pmin, pmax, i125, Erows["air"][0] + S["ldo_rja"][0] * drop * pmax))
        b_crit = i125 - (pass_band(S, i_lo, i_hi, bmax=0.0)[1])
        adc_crit = crit_adc(S, i125)
        w("     the margin: the guarantee holds for B up to %.1f mA (%.1f mA with the EN diode, %.0f mA assumed without it) and for an ADC error up to +-%.0f mV at" % (
            b_crit * 1e3, B_MAX * 1e3, B_BOR * 1e3, adc_crit * 1e3))
        w("     the pin (assumed %.0f mV)" % (ADC_ERR * 1e3))
        w("     the low side: a pass admits IOS from %.4f A, %.4f A under the largest served peak %.4f A (S3'): such a limit latches its supervisor at that peak in" % (
            pmin, R["s3"] - pmin, R["s3"]))
        w("     service, a node out that canen restarts and the next test reads LOW only under %.4f A: a service residual stated, not a protection one (W146-F8)" % pmin)
        for code, ok, txt in jrows:
            for i_, x in enumerate(textwrap.wrap("%s %s %s" % (code, "holds" if ok else "FAILS", txt), 122)):
                w(("   " if i_ == 0 else "      ") + x)
        w("   the judge: %s" % jv)
        jmuts = [("a TYPICAL deglitch (7.5 ms) taken as the bound", dict(base_cfg, deglitch=((S["deglitch"][0][1],) * 3, "TYPICAL", "SLVS841F 7.5 typ"))),
                 ("a test that cannot detect a lost limit: R_T 10 Ohm (a healthy limiter never limits)", dict(base_cfg, r_nom=10.0)),
                 ("R_T 1.0 Ohm (a lost limit's current over U601)", dict(base_cfg, r_nom=1.0)),
                 ("each half alone for 6 ms (a stuck other half latches the target)", dict(base_cfg, t_single=6e-3)),
                 ("the reading to 5.5 ms after the drop (past the least deglitch)", dict(base_cfg, read=(1e-3, 5.5e-3)))]
        jm = []
        for lab, cfg in jmuts:
            v, _r = judge(S, R, cfg)
            jm.append((lab, v))
            w("     mutated, %-86s %s" % (lab + ":", v))
        w("")
        # ------------------------------------------------------------ 9. the procedure
        steps, T = procedure(S, R)
        w("9. THE PROCEDURE (DRAFTED for Layer 5's contract; L4A-61 propagates it) AND ITS TIMING on the printed figures")
        w("   preconditions, each peer on its own observation: all three in the quorum on both fabrics for the last 10 windows, no other HO-D test and no")
        w("   contained node, the target's FAULT high and its output in band; the schedule (DRAFTED, W146-D5): the first round %.0f s after the quorum first" % T_FIRST)
        w("   holds (A, B, C %.0f s apart), then each supervisor every %.0f s, the three %.0f s apart; a test whose preconditions fail waits for the next window" % (
            T_STAGGER, T_PERIOD, T_PERIOD / 3))
        for code, lab, dur, txt in steps:
            for i_, x in enumerate(textwrap.wrap("step %s, %s (%.3f s): %s" % (code, lab, dur, txt), 122)):
                w(("   " if i_ == 0 else "      ") + x)
        w("   any failed check: both peers open their halves, the verdict goes into their state frames and the kit's status path, the target is restored")
        w("     if latched (step 4) or simply readmitted if never latched; that supervisor's tests stop until the next start (DRAFTED, W146-D6); each peer")
        w("     writes the target and the step to its backup registers before step 3 and clears it after step 4, so a peer that boots with a step 3")
        w("     recorded (the survivors reset by the step's transient, W146-F10) takes that test as failed (LIMIT NOT SHOWN) and stops its tests: the")
        w("     transient cannot repeat on every restart (DRAFTED; the registers' retention through a brown-out reset is RM0433's backup domain, not")
        w("     read here: ASSUMPTION; DS12110 describes VBAT supplying that domain when VDD is absent)")
        w("   THE INTERVAL THE TARGET IS OUT of the quorum: %.3f s (the announcement %.1f s, step 1 %.3f s, settle %.3f s, step 2 %.3f s, step 3 %.3f s, step 4 %.3f s)" % (
            T["out"], WINDOW, T["step1"], T_SETTLE, T["step2"], T["step3"], T["step4"]))
        w("     (MODEL on PRINTED, DRAFTED and the boot and domain ASSUMPTIONs; record l4canen's recovery %.3f s is step 4 plus its %.1f s decision)" % (
            S["recovery"], CEN.T_DEC))
        c_loc, c_loc_refs = cap_sum(nl1, "+5V_IOC")
        c_out, c_out_refs = cap_sum(nl1, "+3V3_IOCB")
        hu = {lab: holdup(S, R, c_loc, c_out, st_) for lab, st_ in (("lost", S["v5b"][1] / rt_band(S)[0]), ("healthy", S["ios"][1]))}
        v0, v_need, t_rail, v_reg, t_hold = hu["lost"]
        para = ("THE SERVICE LOST: two of three serve for that interval (IOHA row 3: ownership unaffected); the quorum has no spare then (a second "
                "supervisor out is row 4's home assignment); %.2f %% of the time at %.0f s a supervisor. The survivors keep their supply on the DC path "
                "(J2 and record l4reg's J4 (c)); the transient dip of +5V_IOC at the test's load step (at most %.4f A with a healthy limit, %.4f A with "
                "the limit lost, for the closer's %.1f ms) is NOT bounded on printed figures (U601's load-transient response and the lead's inductance "
                "are not printed; the base design's own overload step of up to IOSmax has the same open term, W138's J7 being a DC row): PROVISIONAL, "
                "finding W146-F10. The hold-up it would need (MODEL on the drawn capacitors and the printed thresholds): board B's +5V_IOC carries "
                "%.1f uF (%s); from %.4f V before the step to the survivors' need %.4f V at their limiter's input it carries the lost limit's step "
                "%.2f us, the healthy step %.2f us; each survivor's own %.1f uF (B's: %s) then holds its rail from the regulator's least %.4f V over "
                "VBOR2's highest falling %.2f V (PRINTED) for %.1f us at its %.4f A peak: the survivors stay out of reset if U601 and the lead carry "
                "the step within %.1f us (%.0f of U601's switching periods at its printed least %.0f kHz); its load-transient response is printed only "
                "as TYPICAL figures, so that time is the supplier's pass limit (L4HOD.md section 11, task 2). Their frames hold: the target's "
                "transceivers go to the protected mode (bus high impedance) as its rail falls under UV(VCC) %.2f to %.2f V (PRINTED), its TXDs rest "
                "recessive on canmb's pull-ups, and W139's row R3 (a controller dark, its onset scanned over the window) reads '%s' with the "
                "survivors' gap %d windows against the loss count %d: W139's loss count respected; the target itself is lost to the quorum by that "
                "count, as planned, and rejoins listening first (W139-D9)" % (
                    100 * 3 * T["out"] / T_PERIOD, T_PERIOD, S["ios"][1], S["v5b"][1] / rt_band(S)[0], T_ABORT_CLOSER * 1e3, c_loc * 1e6,
                    ", ".join(c_loc_refs), v0, v_need, t_rail * 1e6, hu["healthy"][2] * 1e6, c_out * 1e6, ", ".join(c_out_refs), v_reg,
                    S["vbor2"][0][2], t_hold * 1e6, R["s3"], (t_rail + t_hold) * 1e6, (t_rail + t_hold) * S["u601_fsw"][0], S["u601_fsw"][0] / 1e3,
                    S["tcan_uv"][0][0], S["tcan_uv"][0][2], S["r3"][0], S["r3"][1], LOSS_COUNT))
        for i_, x in enumerate(textwrap.wrap(para, 122)):
            w(("   " if i_ == 0 else "     ") + x)
        w("   W143's self-test skips its phases while the target is out (its own precondition: all three functional): a latent vote-path fault arising in a")
        w("     test is found within %.2f s + %.3f s = %.3f s (finding W146-F2)" % (S["selftest"], T["out"], S["selftest"] + T["out"]))
        w("   THE DETECTION INTERVAL of a lost limit (MODEL on the drafted schedule and the printed timing): a limit lost after start-up is found within")
        det = T_PERIOD + T["verdict"]
        det0 = T_FIRST + 2 * T_STAGGER + T["verdict"]
        w("     %.0f s + %.3f s = %.3f s of its onset (the period plus the test's verdict, steps 0 to 3); one present at start-up within %.3f s of the quorum" % (
            T_PERIOD, T["verdict"], det, det0))
        w("     first holding; a test whose preconditions fail waits, so the interval is bounded while the preconditions hold (a node out or a fabric down")
        w("     adds its own repair time, IOHA rows 3 and 7)")
        w("")
        # ------------------------------------------------------------ 10. the faults
        full = set(CHECKS)
        rows = faults(full)
        w("10. THE TEST PATH'S OWN FAULTS (per supervisor; continuous checks every window, a fault declared on the second consecutive failure)")
        w("   element | fault | effect | leaves its supervisor off | found by | bound")
        for el, fl, eff, by, bound, off in rows:
            for i_, x in enumerate(textwrap.wrap("%s | %s | %s | %s | %s | %s" % (el, fl, eff, "YES" if off else "no", by or "NOT FOUND", bound), 122)):
                w(("   " if i_ == 0 else "      ") + x)
        resid = [r for r in rows if r[3] and r[3].startswith("NOT in service")]
        undetected = [r for r in rows if r[3] is None]
        off_rows = [r for r in rows if r[5]]
        w("   %d rows; %d residuals, each with no effect alone in service (a gate's 1 kOhm short, a gate's 100 kOhm open, a reading capacitor open, the EN diode open or short);"
          " none NOT FOUND" % (len(rows), len(resid))
          if not undetected else "   %d rows; NOT FOUND: %d" % (len(rows), len(undetected)))
        w("   the ones that can leave a supervisor unpowered: %s" % "; ".join("%s, %s" % (r[0], r[1]) for r in off_rows))
        w("     a limiter whose latch EN does not clear (a part fault against 9.3.1's description) leaves it latched exactly as any real overload would; the")
        w("     test reveals it at once (step 4), canen's automatic restart retries every 10 s and RAIL_EN returns it: a stated residual of the part")
        w("   no single fault of the test path can load the rail outside a test (two halves in series, one per peer), hold a load past %.0f ms in step 2 or" % (T_SINGLE * 1e3))
        w("     past the abort in step 3 (either peer opens its half), or leave the target latched: the restore route is exercised %.3f s before the load (step 1)" % (
            T["step1"] + T_SETTLE + T["step2"]))
        cov = [r for r in S["canen_rows"]]
        if len(cov) != 6:
            refuse("record l4canen's recovery residual rows no longer read as six")
        w("   step 1 exercises record l4canen's route end to end every test: of canen's %s residuals (%s of the recovery only), these become detected within the" % S["canen_res"])
        w("     test period (finding W146-F1): %s" % "; ".join("%s %s" % (r[0], r[1]) for r in cov if not r[0].startswith("a peer's restart decision")))
        w("   double faults, named and bounded (each half of the pair found first within the test period): the test load shorted AND the limit lost: the")
        w("     test then asks up to U601's own current limit for at most the closer's %.1f ms (%.1f ms by the other peer), so +5V_IOC may sag under all three" % (
            T_ABORT_CLOSER * 1e3, (T_ABORT_CLOSER + T_STAGGER3 + ALIGN) * 1e3))
        w("     and the quorum restarts (a transient row 8, every pin analog in reset so both halves open); the first of the two found ends the tests of that")
        w("     supervisor (W146-D6); both halves stuck on: the target latched and held off, a node out (IOHA row 3), its restore failing; a common firmware")
        w("     fault in both peers is outside the single-fault scope, as for every 2-of-2 vote of this plane; a half stuck on AND the limit lost: step")
        w("     2's single closure then loads the rail with the lost limit's current for its %.0f ms (inside J2 and J3) and step 3 reads LIMIT NOT SHOWN" % (
            T_SINGLE * 1e3))
        w("   the FAULT window's lower edge assumes the limiter's die does not reach its thermal shutdown inside the deglitch (no transient thermal")
        w("     impedance is printed; W138 left the same term open for an output short): a trip there asserts FAULT at once (SLVS841F 9.3.3), which the")
        w("     test reads as a failure (FAULT EARLY), never as a pass")
        pm = [("a stuck test switch left undetected (step 2 omitted)", full - {"single_a", "single_b"}),
              ("a stuck lower half left undetected (step 2 checks the upper's partner only)", full - {"single_a"}),
              ("the restore route not exercised first (step 1 omitted)", full - {"pre"}),
              ("one peer alone judging FAULT (no second reader)", full - {"two_readers"}),
              ("no continuous checks (FAULT and the output only at the test)", full - {"cont_fault", "cont_vout"})]
        pmut = []
        for lab, cfg in pm:
            rr_ = faults(cfg)
            und = [r for r in rr_ if r[3] is None]
            offs = [r for r in rr_ if r[5]]
            v = "FAIL" if (und or len(offs) > len(off_rows)) else "HOLDS"
            pmut.append((lab, v, len(und), len(offs)))
            w("   mutated procedure, %-80s %s (%d NOT FOUND; %d leave a supervisor off)" % (lab + ":", v, len(und), len(offs)))
        w("")
        # ------------------------------------------------------------ 11. decisions, findings
        w("11. SESSION DECISIONS (W146-D1 to D10), FINDINGS (W146-F1 to F9), THE SUPPLIER'S TASKS AND WHAT CLOSES ONCE CHECKED: in L4HOD.md beside this")
        w("   script, with their reasons and reversals; nothing closes here: HO-D under the limiter stays REMAINING ENGINEERING, cx46's items and Layer 4's")
        w("   DESK gate keep their states until row (b)'s independent check (L4A-62) reads this record")
        w("")
        # ------------------------------------------------------------ 12. predicates
        pred["the composition: every order of canmb, regstage, canen and this draft composes, every step OK, the netlists identical"] = \
            same and all(runs[o_][2] for o_ in ORDERS) and len(ORDERS) == 5
        pred["the parts: this draft adds 54 (the declared ones), removes none, changes the three limiters and the three controllers"] = \
            len(added) == 54 and set(added) == set(H.ADDS) and not removed and set(retyped) == {"U41", "U45", "U51", "U55", "U61", "U65"}
        pred["CON-004 holds, canmb and canen's EN route still read DRAWN on the composed netlist"] = cv == "HOLDS" and mv == "DRAWN" and ev == "DRAWN"
        pred["the test path reads DRAWN by pin in every order; each test needs a 2-of-2 of its target's two peers; both peers read its output and FAULT"] = \
            all(v == "DRAWN" for v in hv_all.values()) and all(start_verdict(nl1, k)[0] == "2 of 2" for k in range(3))
        pred["every netlist mutation FAILS (seven), a test a single peer can start and a test that cannot detect a lost limit among them"] = \
            len(muts) == 7 and all(v == "FAIL" for _l, v, _s, _r in muts) and muts[0][2] == "1 of 1" and muts[1][2] == "1 of 1" and muts[3][2] == "NO LOAD"
        pred["the draft refuses a generator without regstage, a second application and the tree's generator (NOT RELEASED)"] = all(refused)
        pred["the pin plan: pins 15, 16 and 42 to 45 free before, FT rows of Table 9, the ADC functions read, no debug pin; the count 49 of 100, 14 supplies, 37 unconnected"] = \
            plan_ok and same_cnt and cnt1["A"][:3] == (49, 14, 37) and cnt0["A"][:3] == (43, 14, 43)
        pred["the levels hold on the printed rows (gates, FAULT high and low, the dark peer, the ADC pins, the loads on the rails)"] = lv["ok"]
        pred["the judge HOLDS (J0 to J9): the demand forces the limit, a lost limit's current is carried, a pass keeps the regulator under 125 C"] = jv == "HOLDS"
        pred["every judge mutation FAILS (five), a test that cannot detect a lost limit and a TYPICAL limit among them"] = \
            all(v.startswith("FAILS") for _l, v in jm) and "J0" in jm[0][1] and "J1" in jm[1][1]
        pred["the interval out, the service lost and the detection interval are bounded on printed and drafted figures"] = \
            T["out"] < 10.0 and det < T_PERIOD + 10.0 and det0 < 200.0
        pred["every fault of the test path has a row with its detection and bound; no single fault is NOT FOUND; only the part's own latch can leave its supervisor off"] = \
            not undetected and len(off_rows) == 1 and off_rows[0][0] == "the limiter"
        pred["every procedure mutation FAILS (five), a stuck test switch left undetected among them"] = \
            len(pmut) == 5 and all(v == "FAIL" for _l, v, _u, _o in pmut)
        pred["nothing closes here"] = True
    w("12. THE PREDICATES (v2/ecad/tools/tests/test_l4hod.py holds them)")
    for k_, v_ in pred.items():
        w("   %s: %s" % (k_, "yes" if v_ else "NO"))
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 1


def cap_sum(nl, net):
    """the capacitance drawn on a net (each capacitor with one pin on it and the other on ground), from the values' leading figure"""
    tot, refs = 0.0, []
    for x in CHK.members(nl, net):
        ref = x.split(".")[0]
        pins = nl["pins"].get(ref, {})
        if ref.startswith("C") and sorted(pins.values()) == sorted([net, "GND"]):
            m = re.match(r"([\d.]+)\s*([pnu])", CHK.value(nl, ref))
            if not m:
                refuse("capacitor %s's value %r does not read" % (ref, CHK.value(nl, ref)))
            tot += float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6}[m.group(2)]
            refs.append(ref)
    return tot, sorted(refs)


def holdup(S, R, c_local, c_out, step):
    """the time the survivors stay out of reset if nothing supplies a load step at board B (MODEL): the local capacitance carries the
    step from the rail's level before it to the survivors' need at their limiter's input, then each survivor's output capacitance carries
    its peak current from the regulator's least output to VBOR2's highest falling threshold"""
    v0 = R["fixed"] - 3 * R["s3"] * R["r_sup"]
    v_need = R["need"](R["s3"]) + R["s3"] * S["ron"][0]
    t_rail = c_local * (v0 - v_need) / step
    v_reg = 3.3 * (1 - S["ldo_acc"][0])
    t_hold = c_out * (v_reg - S["vbor2"][0][2]) / R["s3"]
    return v0, v_need, t_rail, v_reg, t_hold


def crit_adc(S, i125):
    """the largest ADC error at the pin (V) for which a pass still admits no IOS over the regulator's 125 C current (bisection)"""
    lo_, hi_ = 0.0, 0.5
    for _ in range(40):
        mid = (lo_ + hi_) / 2
        a, b = thresholds(S, adc=mid)
        if pass_band(S, a, b, adc=mid)[1] < i125:
            lo_ = mid
        else:
            hi_ = mid
    return lo_


def levels(S, R):
    """the levels of the test path on the printed rows; returns the lines and whether all hold"""
    L, ok = [], True
    vdd_lo, vdd_hi = S["rail"]
    v5lo, v5hi = S["v5b"]
    vih, vil = S["vih_k"][0] * vdd_hi, S["vil_k"][0] * vdd_lo
    vg = (vdd_lo - S["voh_drop"][0]) * R_GPD / (R_GPD + R_GS)
    goff = (S["ilkg"][0] + S["igss"][0]) * R_GPD
    ok &= vg >= 2.5 and goff < S["vth"][0][0]
    L.append("the switch gates: a peer's high at least %.4f V (VDD - %.1f V at 8 mA, Table 158) through 1 kOhm over 100 kOhm: %.4f V, over the 2.5 V RDS(on) row (AO3400A, "
             "TJ 25 C PRINTED; hot %.1f mOhm INFERRED from the 10 V rows' 125 C ratio); a peer in reset or dark leaves its pin analog (RM0433 p.533) and the gate at most %.4f V "
             "(the pin's 250 nA and IGSS 100 nA into 100 kOhm) against VGS(th) %.2f V" % (vdd_lo - S["voh_drop"][0], S["voh_drop"][0], vg,
                                                                                      S["rds25"][0] * S["rds10"][0][1] / S["rds10"][0][0] * 1e3, goff, S["vth"][0][0]))
    i_flt = 2 * vdd_hi / (R_PU * (1 - R_PU_TOL))
    v_low = S["flt_vol"][0][0] + S["vf"][0][1] + VF_COLD
    ok &= i_flt <= S["flt_vol"][0][1] and v_low < vil and i_flt <= S["flt_sink"][0][1]
    L.append("FAULT low at a peer's pin: VOL %.2f V at %.0f mA (PRINTED; it sinks at most %.3f mA from the two pull-ups) plus the BAT46W's VF %.2f V at 10 mA (PRINTED, 25 C) and "
             "%.2f V for the cold (ASSUMPTION): at most %.3f V against 0.3 VDD = %.4f V (Table 157)" % (S["flt_vol"][0][0], S["flt_vol"][0][1] * 1e3, i_flt * 1e3, S["vf"][0][1],
                                                                                                  VF_COLD, v_low, vil))
    v_hi = vdd_lo - R_PU * (1 + R_PU_TOL) * (S["ilkg"][0] + IR_HOT + S["flt_lkg"][0])
    ok &= v_hi >= vih
    L.append("FAULT high at a peer's pin: its own rail through 10 kOhm less the pin's 250 nA, the other (dark) peer's diode reverse current %.0f uA (ASSUMPTION at 76.25 C: 5 uA "
             "at 60 C and 1.5 V PRINTED) and FAULT's 1 uA off-state leakage (PRINTED): at least %.4f V against 0.7 VDD = %.4f V; no pin ever sees more than its own rail; "
             "a dark peer's anode sits at its dark rail, its diode reverse biased" % (IR_HOT * 1e6, v_hi, vih))
    k_nom, k_lo, k_hi = k_band()
    vpin = v5hi * k_hi
    ok &= vpin <= vdd_lo and vpin <= 4.0
    L.append("each ADC pin: at most %.4f V (the output's top %.4f V on the divider's highest ratio), inside 0 to VREF+ (Table 184, VREF+ the peer's own rail, at least %.4f V) "
             "and under the FT pins' 4.0 V unpowered (%s); a shorted divider top puts the output on the pin, %.4f V at most: inside an FT pin's limit while powered "
             "(VDD + 3.6 V, Table 157 note 6), 0.1174 V over 4.0 V only while that peer is dark (a residual of the double condition, W146-F9)" % (vpin, v5hi, vdd_lo, S["ft_unpowered"], v5hi))
    i_div = 2 * v5hi / (K_TOP + K_BOT) * 1.01
    i_pu = 2 * vdd_hi / (R_PU * (1 - R_PU_TOL))
    L.append("the loads the path adds: the two dividers %.3f mA on each limiter's output; a peer's rail carries its two FAULT pull-ups only while FAULT is low (%.3f mA); "
             "the gates draw nothing static: no case row changes (a labelled scenario for the coordinator, W146-F6)" % (i_div * 1e3, i_pu * 1e3 / 2))
    rfet_hot = S["rds25"][0] * S["rds10"][0][1] / S["rds10"][0][0]
    v_en = S["ios"][1] * 2 * rfet_hot + S["vf"][0][0] + VF_COLD
    i_en = S["ios"][1] * rt_band(S)[1] / 100e3
    ok &= v_en < S["ldo_en_lo"][0] and i_en <= 0.1e-3
    L.append("the tested target's regulator while the load conducts: the load's bottom at most %.4f V (IOSmax through both switches hot, INFERRED), its EN through the "
             "BAT46W at most %.4f V (VF %.2f V at 0.1 mA PRINTED, it carries %.0f uA from the EN's 100 kOhm, and %.2f V for the cold, ASSUMPTION) against the TPS737's "
             "%.1f V low (SBVS067W 5.6, PRINTED): the regulator is off and blocks reverse current (6.3.4, DESCRIBED); with either half open the load carries nothing, its "
             "bottom sits at the output and the diode is off; with the limit lost the bottom rises to the lost current's drop and the test aborts anyway" % (
                 S["ios"][1] * 2 * rfet_hot, v_en, S["vf"][0][0], i_en * 1e6, VF_COLD, S["ldo_en_lo"][0]))
    L.append("the second barrier: while its limiter limits the output is %.3f to %.3f V, so the target's rail is under VBOR2's %.2f V falling minimum (PRINTED) and with BOR "
             "at level 2 (DRAFTED, W146-D9) it is held in reset even with the EN diode open" % (
                 (S["ios"][0] - B_BOR) * rt_band(S)[0], S["ios"][1] * rt_band(S)[1], S["vbor2"][0][0]))
    ok &= S["ios"][1] * rt_band(S)[1] < S["vbor2"][0][0]
    return dict(lines=L, ok=bool(ok))


if __name__ == "__main__":
    sys.exit(main())
