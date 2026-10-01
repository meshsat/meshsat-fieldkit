#!/usr/bin/env python3
"""l4e_replay.py: layer 4 task L4-E2, the energy architecture comparison under ONE assumption set (MESHSAT-1357,
written 30 September and 1 October 2026). It replays the checked layer 3 energy model with the solar stage's input
clipped at REQ-016's 100 W instead of the 200 W window of proposal P-03, for the two architectures the collaborator's
L4-E1 assessment names:

  A1  D-06's single 4S3P pack of Samsung INR18650-35E in the east pocket (no owner ruling changes);
  A2  the base 4S6P plus a separately protected lid 4S9P, both lid functions kept (an explicit proposal that changes
      D-06 only; Option A(i)'s arrangement A of a1mech).

PROTOTYPE DESIGN, desk arithmetic: nothing is built, bought, powered or measured. Every energy figure is MODELED on
a1elec's energy_two_pack.py through l3plane's energy_basis.py set-up (both pinned, imported unchanged). The corrected
power path is HYPOTHETICAL; every WE figure is CONDITIONAL on the three undocumented efficiencies (C-8).

Before any result it proves (exit 4 otherwise):
  0a  l3batt's runtime.py, re-run in a child process, reproduces the checked runtime.out byte for byte;
  0b  this harness reproduces runtime.out section 1's D06 and A35 rows, all twenty cells of section 2 (400 Wp, 200 W)
      and section 3's least lid at 48 h and 72 h for NOM, WE and NOM90 (TYP and WAB);
  0c  this harness reproduces three_cases.out's AS DRAWN rows at WE for the both-kept lid (the drawn case used here);
  0d  the single-pack use of the two-pack model (A1: the lid off) reproduces energy_budget.out section 5b's two
      PS-IDLE-SPEC September rows (a 100 Wp panel in the 100 W window, the record's chain): first stop and unserved Wh.
Only then does it change one input, the stage window, from 200 W to 100 W, and print the comparison. Every run of the model
is refused unless its store account and its service ledger close (section 5). Section 11 refuses (exit 3) when a row of the
LT8705A sheet's electrical characteristics that names the input-current mechanism or the input-voltage hold reads back
differently from its table or is not classified there, and (exit 4) when O-2's setting lets any corner of the envelope take
more than REQ-016's 100 W. Section 12 (the review's L4-R02) pins a nominally compatible candidate panel, the SunPower SPR-E-Flex-100,
from its held sheet (read back and pinned; its installation guide's 10 % qualification keeps source compliance
INCONCLUSIVE, check astra-check-l4e3-1), builds its hourly operating point under the stage's input hold and O-2's limit with
a1solar's single-diode model, and reruns A1 and A2 on that trace; section 13 lists the profile's undocumented loads.

Run from the repository root:  python3 v2/docs/records/l4e/l4e_replay.py > v2/docs/records/l4e/l4e_replay.out
Deterministic; standard library plus PyYAML (through the imported model). About one minute, most of it 0a.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import itertools
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
try:
    os.nice(10)                 # a shared host: stay behind interactive work
except OSError:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = os.path.join(TOP, "v2", "docs", "records")
PINS = {
    "l3batt/runtime.py": "885bd4fadf9000cf45f7f66e2ba518b7b390e1092e9a0246e6f6a52c760897ee",
    "l3batt/runtime.out": "87d9c1ee590597638c57aa97c384c217af9eb36044a2db39e27194a88047fc13",
    "l3plane/energy_basis.py": "7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47",
    "l3plane/three_cases.py": "2395d75e48c9787773373aefcd02aeaeb04f5cfcf9d7c4a948617e1547bfab68",
    "l3plane/three_cases.out": "8119987a20fad08cae0edc928726c847b1f5ec41f81cfd9552849793567e96be",
    "energy/energy_budget.out": "5b11a90df10fee7bcafbb4e9931e05eafbc91120083e6e33815b12bce943e4dd",
    "r11dep/r11_dep.out": "f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209",
    "a1solar/array_calc.py": "fdeaf63f525f1d7f4ca54502083369cfd4f322a41207ff0a52582c27038fd1e4",
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def refuse(code, msg):
    sys.stderr.write("l4e_replay: %s; refusing\n" % msg)
    sys.exit(code)


for _rel, _want in PINS.items():
    if sha(os.path.join(REC, _rel)) != _want:
        refuse(2, "%s is not the pinned file" % _rel)
sys.path.insert(0, os.path.join(REC, "l3plane"))
import energy_basis as EBS  # noqa: E402
TP, ER = EBS.TP, EBS.ER
BUD = TP.EB                 # records/energy/energy_budget.py, as energy_two_pack.py imports it
EF = EBS.EF                 # records/s117/efficiency.py

RUNTIME_OUT = "v2/docs/records/l3batt/runtime.out"
THREE_OUT = "v2/docs/records/l3plane/three_cases.out"
BUDGET_OUT = "v2/docs/records/energy/energy_budget.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
WP_TRACE = 400.0            # the checked availability series: 400 Wp in 2S2P (P-03), runtime.py's call
WIN_P03 = 200.0             # P-03's stage window, the one runtime.out used
T_COLD = -10.0              # REQ-072's battery-only cold case (REQ-046's discharge floor)
LID_A = 9                   # a1mech arrangement A (HF and the tablet kept): 4S9P
BASE_A2 = 6                 # the base pockets' 4S6P (energy_two_pack.NP_B)
BASE_A1 = 3                 # D-06's 4S3P
U3_TOL = 0.1                # three_cases.py: U3's minimum 0.1 A under its setting (INFERRED from SLUSE66A p.80's maximum)
U3_DERATED = 4.00           # r11dep A-1 and three_cases.py: the derated variant of the drawn circuit
U3_WINDOW = 4.65            # section 8: the least 50 mA setting whose minimum covers REQ-016's window at the declared efficiencies
# Section 11, O-2 (checks astra-check-l4e2-1 B2 and astra-check-l4e2-2 B2): the LT8705A's input-current limit (8705af p.31,
# Figure 11: IMON_IN = I x RSENSE1 x gm(A7) x RIMON_IN, regulated by EA2 at the IMON_IN reference) must keep V_in x I_in at or
# under REQ-016's 100 W at every loaded input voltage an admitted panel presents. The second check found a tolerance list
# picked by hand; so every row of the sheet's electrical characteristics (pp.3 to 6) whose parameter names the input-current
# mechanism (CSPIN, CSNIN, A7, IMON_IN, EA2, SRVO_IIN) or the input-voltage hold (FBIN, EA3, VC) is enumerated below, each
# quoted as `pdftotext -f 4 -l 6 -layout v2/vendor/power/lt8705a.pdf -` prints it, and classified. At run time every row's
# printed MIN / TYP / MAX is read back from the pinned sheet by column and must equal the table (exit 3), and every parameter
# line of pp.3 to 6 that names the mechanism must be classified here (exit 3). The page header of pp.4 and 5 reads "The l
# denotes the specifications which apply over the full operating temperature range, otherwise specifications are at TA =
# 25 C. VIN = 12V, SHDN = 3V unless otherwise noted."
#   use STACK      its printed limits enter the worst-case stack of the limit
#   use ALLOWANCE  a TYP-only row entered with a stated assumption (the TYP taken as the bound)
#   use HOLD       the input-voltage hold's stack (the lower corner of the envelope)
#   use CONDITION  a range the design must stay inside; checked, it moves nothing while it holds
#   use NONE       it does not move the limit; the reason given
EC_ROWS = [
    # p.4: "Regulation Voltages for IMON_IN and IMON_OUT   VC = 1.2V   l   1.187 1.208 1.229   V"
    dict(id="IMON_REG", page=4, name="Regulation Voltages for IMON_IN and IMON_OUT", sub=None, full=True, min=1.187, typ=1.208, max=1.229,
         unit="V", use="STACK", why="the reference EA2 regulates IMON_IN to (Figure 11), printed at VIN = 12 V and VC = 1.2 V"),
    # p.4: "Line Regulation for IMON_IN and IMON_OUT Error Amp   VIN = 12V to 80V; Not Switching   0.002 0.005   %/V" / "Reference Voltage"
    dict(id="IMON_LINE", page=4, name="Line Regulation for IMON_IN and IMON_OUT Error Amp", sub=None, full=False, min=None, typ=0.002,
         max=0.005, unit="%/V", use="STACK", why="the reference's shift with VIN from the 12 V IMON_REG is printed at; its maximum, "
         "either sign, from 12 V to the corner's voltage (printed 'Not Switching'; applied as printed while switching, ASSUMPTION)"),
    # p.5: "VCSPIN-CSNIN to IMON_IN Amplifier A7 gm   VCSPIN - VCSNIN = 50mV, VCSPIN = 5.025V" then
    #      "(All Grades)   0.95 1 1.05 mmho", "(LT8705AE, LT8705AI)   l   0.94 1 1.06 mmho", "(LT8705AH, LT8705AMP)   l   0.93 1 1.07 mmho"
    dict(id="A7_ALL", page=5, name="VCSPIN-CSNIN to IMON_IN Amplifier A7 gm", sub="(All Grades)", full=False, min=0.95, typ=1.0, max=1.05,
         unit="mmho", use="STACK", why="the sense gain at 25 C, every grade"),
    dict(id="A7_EI", page=5, name="VCSPIN-CSNIN to IMON_IN Amplifier A7 gm", sub="(LT8705AE, LT8705AI)", full=True, min=0.94, typ=1.0,
         max=1.06, unit="mmho", use="STACK", why="the sense gain over the full range, E and I grades"),
    dict(id="A7_HMP", page=5, name="VCSPIN-CSNIN to IMON_IN Amplifier A7 gm", sub="(LT8705AH, LT8705AMP)", full=True, min=0.93, typ=1.0,
         max=1.07, unit="mmho", use="STACK", why="the sense gain over the full range, H and MP grades: the netlist names no grade, "
         "so the widest printed limits are stacked"),
    # p.5: "IMON_IN Error Amp EA2 Voltage Gain   130   V/V"
    dict(id="EA2_AV", page=5, name="IMON_IN Error Amp EA2 Voltage Gain", sub=None, full=False, min=None, typ=130.0, max=None,
         unit="V/V", use="ALLOWANCE", why="IMON_REG is printed at VC = 1.2 V; in regulation VC sits where the power stage needs it, "
         "which moves the regulated point by (VC - 1.2 V) / gain. No VC operating range and no minimum gain are printed: the "
         "allowance takes VC anywhere in its absolute maximum range (p.2) and the TYP gain as its bound (ASSUMPTION)"),
    # p.5: "IMON_IN Error Amp EA2 gm   185   umho"
    dict(id="EA2_GM", page=5, name="IMON_IN Error Amp EA2 gm", sub=None, full=False, min=None, typ=185.0, max=None, unit="umho",
         use="NONE", why="its effect on the regulated point is carried by the voltage-gain row (EA2_AV)"),
    # p.4: "CSPIN, CSNIN Bias Current   BOOST Capacitor Charge Control Block Not Active" / "ICSPIN + ICSNIN, VCSPIN = VCSNIN = 12V   31   uA"
    dict(id="CS_BIAS", page=4, name="CSPIN, CSNIN Bias Current", sub="ICSPIN + ICSNIN", full=False, min=None, typ=31.0, max=None,
         unit="uA", use="CONDITION", why="an offset only through resistance in series with the pins, which the maker forbids "
         "(p.30: 'do not place resistors in series with any of the CSxIN or CSxOUT pins'); zero while that holds. No offset "
         "voltage row is printed for A7; its gm is printed at a 50 mV differential, the point the setting is sized to sit at"),
    # p.5: "CSPIN, CSNIN Common Mode Operating Voltage Range   l   1.5   80   V"
    dict(id="CS_CM", page=5, name="CSPIN, CSNIN Common Mode Operating Voltage Range", sub=None, full=True, min=1.5, typ=None, max=80.0,
         unit="V", use="CONDITION", why="the pins sit at the panel voltage, inside it across the envelope"),
    # p.5: "CSPIN, CSNIN Differential Operating Voltage Range   l   -100   100   mV"
    dict(id="CS_DIFF", page=5, name="CSPIN, CSNIN Differential Operating Voltage Range", sub=None, full=True, min=-100.0, typ=None,
         max=100.0, unit="mV", use="CONDITION", why="the sense resistor puts 50 mV across the pins at the nominal limit, and "
         "the fault's 1.61 / 1.208 of it stays inside"),
    # p.5: "IMON_IN Maximum Output Current   l   100   uA"
    dict(id="IMON_IOUT", page=5, name="IMON_IN Maximum Output Current", sub=None, full=True, min=100.0, typ=None, max=None, unit="uA",
         use="CONDITION", why="A7 sources 50 mV x its gm at the limit, at most 53.5 uA, under it"),
    # p.5: "IMON_IN Overvoltage Threshold   l   1.55 1.61 1.67   V"
    dict(id="IMON_OV", page=5, name="IMON_IN Overvoltage Threshold", sub=None, full=True, min=1.55, typ=1.61, max=1.67, unit="V",
         use="NONE", why="the overcurrent fault (p.31) above the limit; switching stops, which bounds nothing upward"),
    # p.5: "SRVO_IIN Activation Threshold (Note 5)   (VIMON_IN Rising) - (Regulation Voltage for   -60 -49 -37 mV"
    dict(id="SRVO_IIN", page=5, name="SRVO_IIN Activation Threshold (Note 5)", sub=None, full=False, min=-60.0, typ=-49.0, max=-37.0,
         unit="mV", use="NONE", why="a status output, not in the loop"),
    dict(id="SRVO_IIN_H", page=5, name="SRVO_IIN Activation Threshold Hysteresis (Note 5)", sub=None, full=False, min=None, typ=22.0,
         max=None, unit="mV", use="NONE", why="a status output, not in the loop"),
    dict(id="SRVO_IIN_LV", page=5, name="SRVO_IIN, SRVO_IOUT Low Voltage (Note 5)", sub=None, full=True, min=None, typ=110.0, max=330.0,
         unit="mV", use="NONE", why="a status output, not in the loop"),
    dict(id="SRVO_IIN_LK", page=5, name="SRVO_IIN, SRVO_IOUT Leakage Current (Note 5)", sub=None, full=True, min=None, typ=0.0, max=1.0,
         unit="uA", use="NONE", why="a status output, not in the loop"),
    # p.4: "Gain from VC to Maximum Current Sense Voltage   Boost Mode   150   mV/V"
    dict(id="VC_GAIN", page=4, name="Gain from VC to Maximum Current Sense Voltage", sub=None, full=False, min=None, typ=150.0, max=None,
         unit="mV/V", use="NONE", why="the inner current loop's gain; the limit is set at EA2's input whatever it is"),
    # the input-voltage hold, the envelope's lower corner. p.4: "Regulation Voltage for FBIN   VC = 1.2V (LT8705AE, LT8705AI)   l
    # 1.184 1.205 1.226 V" and "VC = 1.2V (LT8705AH, LT8705AMP)   l   1.182 1.205 1.226 V"
    dict(id="FBIN_EI", page=4, name="Regulation Voltage for FBIN", sub="(LT8705AE, LT8705AI)", full=True, min=1.184, typ=1.205,
         max=1.226, unit="V", use="HOLD", why="the hold's reference, E and I grades"),
    dict(id="FBIN_HMP", page=4, name="Regulation Voltage for FBIN", sub="(LT8705AH, LT8705AMP)", full=True, min=1.182, typ=1.205,
         max=1.226, unit="V", use="HOLD", why="the hold's reference, H and MP grades (no grade named: the widest stacked)"),
    # p.4: "Line Regulation for FBOUT and FBIN Error Amp Reference   VIN = 12V to 80V; Not Switching   0.002 0.005   %/V"
    dict(id="FB_LINE", page=4, name="Line Regulation for FBOUT and FBIN Error Amp Reference", sub=None, full=False, min=None, typ=0.002,
         max=0.005, unit="%/V", use="HOLD", why="the hold reference's shift from 12 V, either sign"),
    # p.4: "FBIN Pin Bias Current   Current Out of Pin   10   nA"
    dict(id="FBIN_BIAS", page=4, name="FBIN Pin Bias Current", sub=None, full=False, min=None, typ=10.0, max=None, unit="nA",
         use="HOLD", why="out of the pin into the divider, lowering the hold by the current x R8; TYP taken (ASSUMPTION)"),
    # p.4: "FBIN Error Amp EA3 Voltage Gain   90   V/V"
    dict(id="EA3_AV", page=4, name="FBIN Error Amp EA3 Voltage Gain", sub=None, full=False, min=None, typ=90.0, max=None, unit="V/V",
         use="HOLD", why="as EA2_AV, for the hold: VC in its absolute maximum range, the TYP gain as the bound (ASSUMPTION)"),
    dict(id="EA3_GM", page=4, name="FBIN Error Amp EA3 gm", sub=None, full=False, min=None, typ=130.0, max=None, unit="umho",
         use="NONE", why="carried by EA3_AV"),
    dict(id="SRVO_FBIN", page=4, name="SRVO_FBIN Activation Threshold (Note 5)", sub=None, full=False, min=56.0, typ=72.0, max=89.0,
         unit="mV", use="NONE", why="a status output, not in the loop"),
    dict(id="SRVO_FBIN_H", page=4, name="SRVO_FBIN Activation Threshold Hysteresis (Note 5)", sub=None, full=False, min=None, typ=33.0,
         max=None, unit="mV", use="NONE", why="a status output, not in the loop"),
    dict(id="SRVO_FBIN_LV", page=4, name="SRVO_FBIN, SRVO_FBOUT Low Voltage (Note 5)", sub=None, full=True, min=None, typ=110.0,
         max=330.0, unit="mV", use="NONE", why="a status output, not in the loop"),
    dict(id="SRVO_FBIN_LK", page=4, name="SRVO_FBIN, SRVO_FBOUT Leakage Current (Note 5)", sub=None, full=True, min=None, typ=0.0,
         max=1.0, unit="uA", use="NONE", why="a status output, not in the loop"),
]
EC_TOKENS = ("CSPIN", "CSNIN", "A7", "IMON_IN", "EA2", "SRVO_IIN", "FBIN", "EA3", "VC ")
# p.2 (absolute maximum ratings): "VC Voltage (Note 2).................................... -0.3V to 2.2V"
LT8705A_PDF = ("v2/vendor/power/lt8705a.pdf", "8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3")
R_TOL = 0.01                # RSENSE1 and RIMON_IN are not chosen: 1 % each, all of tolerance and drift (ASSUMPTION); R8, R9 1 % (NETLIST)
I_RES = 0.001               # the nominal setting's stated resolution, A; the derived setting is rounded DOWN to it
V_LINE_REF = 12.0           # the VIN the page header prints the references at
T_ENDS = ("the cold end", "the hot end")   # the full-range (l) limits hold at both; no end-specific values are printed
# Section 12 (review L4-R02): the panel pinned inside REQ-016's window, from its maker's sheet (held back by its terms and
# fetched by v2/docs/records/a1solar/fetch_held_back.py into v2/vendor/solar/held/, which git ignores; pinned by sha256).
SPR_PDF = ("v2/vendor/solar/held/sunpower-spr-e-flex-100-datasheet-523809-revd.pdf",
           "da06e5e2d9bca625f54a756105e009950a2352e4764868853cb26921372ff605")
SPR_GUIDE = ("v2/vendor/solar/held/sunpower-flex-safety-installation-524958-revf.pdf",   # held back; pinned by a1solar too
             "b8ebdfb7019a399accd75e564a4a764eed565f7066dfd25b131fe65365ec6dd9")
SPR_QUAL = "Rated electrical characteristics are within 10% of measured values at Standard Test Conditions"
SPR_ROWS = (   # (label on the sheet, the figure as printed, a1solar's CAND['SPR100'] key, the value in its units)
    (r"Nominal Power \(Pnom\)\s+(\d+) W", "p", 1.0),
    (r"Rated Voltage \(Vmpp\)\s+([\d.]+) V", "vmp", 1.0),
    (r"Rated Current \(Impp\)\s+([\d.]+) A", "imp", 1.0),
    (r"Open-circuit voltage \(Voc\)\s+([\d.]+) V", "voc", 1.0),
    (r"Short-curcuit current \(Isc\)\s+([\d.]+) A", "isc", 1.0),
    (r"Voltage Temp Coefficient\s+[\u2013-]([\d.]+) mV", "beta_voc_abs", -1e-3),
    (r"Current Temp Coefficient\s+([\d.]+) mA", "alpha_isc_abs", 1e-3),
    (r"Power Temp Coeffiecient\s+[\u2013-]([\d.]+)%", "gamma_p", -1e-2),
)
UNDOC = {   # section 13: each tier T load of load_trace.out, the maker's figure held, and what would settle it
    "Xenarc 709GNK": (
        "now: 6.0 W at the load, the design record's figure (appendix 32.52); HIGH 10 W",
        "held: v2/vendor/xenarc/xenarc-709gnk-product-manual-v2.pdf p.4 'Power Consumption: <= 10W', a maximum; no typical,",
        "no figure per brightness (the manual's dimmer and auto sensor, pp.5 onward); the product page says the same",
        "INCONCLUSIVE: measure its DC input at the kit's supply, at the brightness settings the profile uses, warm and cold"),
    "WiFi link card 2 (standby)": (
        "now: 1.0 W at the load, a placeholder (energy_inputs.yaml); 0 W if held unpowered by PCIE_PWR_EN; bounded by 9.1 W",
        "held: v2/vendor/wifi/asiarf-AW7915-AED_V1.pdf p.4 'Power consumption maximum is 9.1W, average is 7W' (an active card);",
        "p.1 'Deep sleep mode is supported', no figure; the product page 'maximum is 9W, average is 4 - 8W'",
        "INCONCLUSIVE: measure the card's 3.3 V current in the standby state its firmware sets; holding it unpowered is a",
        "design choice that changes the link's failover (CHO-002), not a measurement"),
    "VHF PA 30 W": (
        "now: 0.9 W at the load, a planning placeholder, about 1.2 % duty of a key-down (energy_inputs.yaml)",
        "held: v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf p.2: Pout 30 W at a total efficiency above 40 % (VDD 12.5 V),",
        "so at most 75 W in at key-down; leakage IGG at most 1 mA at VGG 0 V. The average is that input times the beacon duty,",
        "which is the profile's: CONOPS section 5's fixed site (one 1 s beacon in 10 minutes) is about 0.13 W",
        "INCONCLUSIVE: the beacon rate the profile means, and the PA's measured supply energy per beacon at the kit's VDD"),
}
CHECK_B1 = ["270.132086", "286.306461", "500.372955", "516.547330"]   # astra-check-l4e2-1, Checks, kit energy conservation


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


NUM = re.compile(r"(?<![\w.])[\u2013-]?\d+(?:\.\d+)?(?![\w.])")


def pdf_lines(rel, n):
    r = subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"], capture_output=True, text=True)
    if r.returncode != 0:
        refuse(3, "pdftotext could not read %s p.%d" % (rel, n))
    return r.stdout.split("\n")


def ec_cols(lines):
    """The MIN / TYP / MAX / UNITS columns of an electrical-characteristics page, from its PARAMETER header line."""
    for ln in lines:
        if ln.startswith("PARAMETER") and " MIN " in ln and " MAX " in ln:
            return {k: ln.index(k) for k in ("MIN", "TYP", "MAX", "UNITS")}
    return None


def ec_vals(ln, c):
    """The printed MIN, TYP and MAX of one line, each number assigned to the nearest column (the sheet's minus is U+2013)."""
    out = {"min": None, "typ": None, "max": None}
    for m in NUM.finditer(ln):
        if m.start() < c["MIN"] - 4 or m.start() >= c["UNITS"]:
            continue
        mid = 0.5 * (m.start() + m.end())
        k = min(("MIN", "TYP", "MAX"), key=lambda kk: abs(c[kk] + 1.5 - mid))
        out[k.lower()] = float(m.group(0).replace("\u2013", "-"))
    return out


def ec_row(pages, page, name, sub):
    L = pages[page]
    c = ec_cols(L)
    if c is None:
        refuse(3, "8705af p.%d has no PARAMETER header" % page)
    idx = [i for i, ln in enumerate(L) if ln.startswith(name)]
    if len(idx) != 1:
        refuse(3, "8705af p.%d: the row '%s' is found %d times" % (page, name, len(idx)))
    j = idx[0]
    if sub is not None:
        js = [i for i in range(idx[0], min(idx[0] + 8, len(L))) if sub in L[i]]
        if not js:
            refuse(3, "8705af p.%d: the row '%s' has no line '%s'" % (page, name, sub))
        j = js[0]
    return ec_vals(L[j], c)


def i_factor(v, vref, vref_typ, line_pct, ls, dv_ea, es, gm, r1, r2):
    """I_lim / I_set at input voltage v for one vertex (8705af p.31: I_lim = V_IMON / (gm x RSENSE1 x RIMON_IN))."""
    return (vref * (1.0 + ls * line_pct * 1e-2 * (v - V_LINE_REF)) + es * dv_ea) / vref_typ / (gm * r1 * r2)


def main():
    o = []
    P = o.append

    # ------------------------------------------------------------------------------------------ 0a: runtime.py again
    rt = subprocess.run([sys.executable, "-B", os.path.join(REC, "l3batt", "runtime.py")], cwd=TOP, capture_output=True)
    rt_ok = rt.returncode == 0 and rt.stdout == open(os.path.join(TOP, RUNTIME_OUT), "rb").read()
    if not rt_ok:
        refuse(4, "runtime.py's re-run does not reproduce runtime.out (exit %d)" % rt.returncode)

    # ------------------------------------------------------------------------------------------ the model, as runtime.py sets it up
    D0, PACK0, RES0, t2m = TP.load_model()
    EBS.D0, EBS.PACK0, EBS.RES0 = D0, PACK0, RES0
    EBS.TMIN = round(min(t2m), 2)
    notes = " ".join(EBS.head_equal(EBS.PANEL).split())
    m = need(notes, r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", "NOTES step")
    md = need(notes, r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", "NOTES drain")
    EBS.FLOOR = FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_w = float(md.group(2)) / D0["mission"]["hours"]
    vr = EBS.VR.compute()
    AC, _e, _t = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    v_min, v_nom = vr["bands"][0][4], vr["nominal"]
    rd = EBS.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EBS.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in need(TP.PAR["v_ak"][1], r"([\d]+) / ([\d]+) / ([\d]+) mV", "v_ak").groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    win_req016 = float(D0["solar"]["window"]["stage_max_w_in"]["value"])
    if win_req016 != 100.0 or "REQ-016" not in D0["solar"]["window"]["stage_max_w_in"]["src"]:
        refuse(3, "energy_inputs.yaml's stage window is not REQ-016's 100 W")
    chg_a1_cell = D0["pack"]["charge"]["current_a"]["value"] / D0["pack"]["parallel"]   # 3.06 A / 3 = 1.02 A a cell
    r11 = EBS.head_equal(R11_OUT)
    held = tuple(float(x) for x in need(r11, r"held, R11 10\.0 mOhm:\s+([\d.]+) / ([\d.]+) / ([\d.]+) A", "r11_dep.out held band").groups())
    other = float(need(r11, r"plus ([\d.]+) A of VBUS20's other loads", "r11_dep.out other loads").group(1))
    fe_held = held[0] - other
    u3_e1, u3_e2 = TP.v("u3_iin_e1_a"), TP.v("u3_iin_draft_a")
    load0 = TP.LOAD

    def we(v, i, extra=None):
        x = {"eta_u3": EBS.u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    lo3 = {"eta_st": ch[0]["low"], "eta_fe": ch[1]["low"], "chg_eta": ce["low"]}
    hi3 = {"eta_st": ch[0]["high"], "eta_fe": ch[1]["high"], "chg_eta": ce["high"]}
    one3 = {"eta_st": 1.0, "eta_fe": 1.0, "chg_eta": 1.0}
    # (bus, U3's input limit, overrides): runtime.py's five cases, three_cases.py's AS DRAWN at WE, and the sensitivities
    CASES = {
        "DRAWN": (v_nom, u3_e1, {"eta_u3": EBS.u3_day(v_nom, u3_e1, "TI"), "fe_i": fe_held}),
        "NOM": (v_nom, u3_e2, {"eta_u3": EBS.u3_day(v_nom, u3_e2, "TI")}),
        "NOM90": (v_nom, u3_e2, dict({"eta_u3": EBS.u3_day(v_nom, u3_e2, "TI")}, **lo3)),
        "WE": (v_min, 6.1, we(v_min, 6.1)),
        "WE90": (v_min, 6.1, we(v_min, 6.1, lo3)),
        "DRAWN-WE": (v_min, u3_e1 - U3_TOL, we(v_min, min(u3_e1 - U3_TOL, fe_held), {"fe_i": fe_held})),
        "WE97": (v_min, 6.1, we(v_min, 6.1, hi3)),
        "WE100": (v_min, 6.1, we(v_min, 6.1, one3)),
        "REC": (v_nom, u3_e2, {}),
        "DERATED-WE": (v_min, U3_DERATED - U3_TOL, we(v_min, U3_DERATED - U3_TOL, {"fe_i": fe_held})),
        "WINDOW-WE": (v_min, U3_WINDOW - U3_TOL, we(v_min, 6.1)),
    }
    node0 = TP.node_power

    def node_collapse(d, res4, g, wp, window, entry):
        """r11dep A-2 / B-5's inferred collapse (three_cases.py's bound): the charge path delivers U3's cap or nothing."""
        if entry is None:
            return node0(d, res4, g, wp, window, entry)
        e_st, e_fe, e_ch = TP.chain(d)
        avail = min(BUD.panel_w(g, wp, res4["pr"]), window) * e_st * e_fe
        cap = min(entry["fe_out_w"], entry["u3_in_w"])
        return cap * e_ch if avail >= cap else 0.0

    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def run(arch, key, n, build, start, hours, window, wp=WP_TRACE, collapse=False, load_w=None, chg_cell=None,
            account=False, ratio=None, entry=None, ov_extra=None, t_l=None, gser=None):
        """One run of energy_two_pack.sim(). arch A2: the base 4S6P and a lid of n in parallel at the lid's temperature;
        arch A1: one pack of n in parallel at the base temperature, no lid (so no lid path and no lid drain)."""
        vb, iin, ov = CASES[key]
        ov = dict(ov, **(ov_extra or {}))
        pr = pr0 * (rat40[build] if ratio is None else ratio)
        vals = [(prof0 if gser is None else gser)[(start + h) % 24] for h in range(hours)]
        saved = (TP.NP_B, TP.NP_L, TP.NP_T, TP.LOAD, TP.node_power)
        try:
            if arch == "A2":
                d, pack, r, cfg = EBS.setup(n, pr, vb, iin, ov)
                drain = ov.get("drain_w", 0.0)
            else:
                d, pack, r, cfg = EBS.setup(0, pr, vb, iin, ov)
                TP.NP_B, TP.NP_L, TP.NP_T = n, 0, n
                cfg["lid"] = False
                cfg["chg_a_b"] = (chg_a1_cell if chg_cell is None else chg_cell) * n
                drain = 0.0
            if entry is not None:
                cfg["entry"] = entry
            d = dict(d)
            d["mission"] = dict(d["mission"], hours=hours)
            TP.LOAD = (load0 if load_w is None else load_w) + drain
            if collapse:
                TP.node_power = node_collapse
            tr = []
            res = TP.sim(d, pack, r, EBS.Series(vals), wp, window, start, TP.v("t_base_c"), EBS.TMIN if t_l is None else t_l, cfg, tr)
            a = res["acct"] = acct(d, r, cfg, res, tr, vals, wp, window, collapse, TP.LOAD, hours, pack.chg_eta)
            if abs(a["closure"]) > 1e-6 or abs(a["kit_res"]) > 1e-6 or abs(a["legacy_res"]) > 1e-6 or a["node_dev"] > 1e-9 \
                    or abs(a["dsg_path_res"]) > 1e-6:
                refuse(4, "a run's energy account or service ledger does not close (%s %s start %d, %d h)" % (arch, key, start, hours))
            res["load"] = TP.LOAD
            res["uns"] = a["unserved"]
            return res
        finally:
            TP.NP_B, TP.NP_L, TP.NP_T, TP.LOAD, TP.node_power = saved

    def acct(d, r, cfg, res, tr, vals, wp, window, collapse, load, hours, eta_c):
        """The per-pack and kit energy account of one run, from the model's own chain and hour trace (Wh), with the SERVICE
        LEDGER (the check astra-check-l4e2-1, B1): energy_two_pack.sim() sets the load to zero while the kit is stopped and
        then both subtracts that hour's sun from its unserved counter and charges the packs with the same sun. The ledger
        counts service from the traced load flows instead: an hour served in full, the stop hour's sun plus what the stores
        delivered, a stopped hour nothing. Its kit balance (node energy + initial store = served + spill + charge losses +
        discharge losses, the cutoff's included, + final store) closes with the stopped hours' sun counted once. The
        model's own counter is kept, labelled the legacy model metric, for reproduction and comparison."""
        e_st, e_fe, e_ch = TP.chain(d)
        ent = TP.ENTRIES[cfg["entry"]]
        cap = min(ent["fe_out_w"], ent["u3_in_w"]) if ent is not None else float("inf")
        a = dict.fromkeys(("arr", "clip", "stage_in", "bus_avail", "not_taken", "u3_loss", "node", "sun_load", "offered",
                           "accepted", "spill", "stored", "drawn", "cap_hours", "full_h", "node_indep", "served_l", "spill_l",
                           "chg_eff_b", "chg_conv_l", "chg_eff_l", "clamp", "dsg_loss", "cutoff", "delivered", "stop_sun",
                           "stop_chg", "stop_spill", "legacy_credit"), 0.0)
        eb, el = res["eb_full"], res["el_full"]
        cut_b = cut_l = None
        worst_dev = 0.0
        for i, row in enumerate(tr):
            h, _hh, p_sun, ld, a_b, a_l, d_b, d_l, e_b, e_l, running = row
            g = vals[i]
            p_arr = BUD.panel_w(g, wp, r["pr"])
            p_in = min(p_arr, window)
            avail = p_in * e_st * e_fe
            taken = ((cap if avail >= cap else 0.0) if collapse else min(avail, cap)) if ent is not None else avail
            worst_dev = max(worst_dev, abs(taken * e_ch - p_sun))
            a["node_indep"] += taken * e_ch
            # the service ledger, hour by hour from the traced flows
            if p_sun >= ld:                           # the model's surplus branch (a stopped hour has ld = 0)
                a["served_l"] += ld
                a["spill_l"] += p_sun - ld - a_b - a_l
                a["chg_eff_b"] += a_b * (1.0 - eta_c)
                clamp = (eb + a_b * eta_c) - e_b
                if a_l > 0.0:
                    t_w = TP.lid_terminal_from_node(a_l, res["v_l"], TP.eta_at(cfg["eta_b"], a_l), cfg["r_chg"])
                    a["chg_conv_l"] += a_l - t_w
                    a["chg_eff_l"] += t_w * (1.0 - eta_c)
                    clamp += (el + t_w * eta_c) - e_l
                a["clamp"] += clamp
                if ld == 0.0:
                    a["stop_sun"] += p_sun
                    a["stop_chg"] += a_b + a_l
                    a["stop_spill"] += p_sun - a_b - a_l
                    a["legacy_credit"] += min(p_sun, load)
            else:                                     # the deficit branch: the stores deliver d_b + d_l at the node
                a["served_l"] += p_sun + d_b + d_l
                a["delivered"] += d_b + d_l
                loss = ((eb + el) - (e_b + e_l)) - (d_b + d_l)
                a["dsg_loss"] += loss
                if not running:
                    a["cutoff"] += loss
            a["arr"] += p_arr
            a["clip"] += p_arr - p_in
            a["stage_in"] += p_in
            a["bus_avail"] += avail
            a["not_taken"] += avail - taken
            a["u3_loss"] += taken * (1.0 - e_ch)
            a["node"] += p_sun
            a["cap_hours"] += 1.0 if (ent is not None and avail > cap) else 0.0
            a["sun_load"] += min(p_sun, ld)
            a["offered"] += max(0.0, p_sun - ld)
            a["accepted"] += a_b + a_l
            dlt = (e_b + e_l) - (eb + el)
            if dlt >= 0:
                a["stored"] += dlt
            else:
                a["drawn"] -= dlt
            eb, el = e_b, e_l
            if cfg["base"] and cut_b is None and e_b <= 1e-9:
                cut_b = h
            if cfg["lid"] and cut_l is None and e_l <= 1e-9:
                cut_l = h
            if ld > 0 and running:
                a["full_h"] += 1
        a["spill"] = a["offered"] - a["accepted"]
        a["chg_loss"] = a["accepted"] - a["stored"]
        a["dsg_path"] = res["loss"]["dsg_path"]
        a["asked"] = load * hours
        a["legacy_unserved"] = res["short"]                     # the legacy model metric
        a["served"] = a["served_l"]
        a["unserved"] = a["asked"] - a["served_l"]
        a["start"] = res["eb_full"] + res["el_full"]
        a["end"] = res["end_b"] + res["end_l"]
        a["closure"] = a["start"] + a["stored"] - a["drawn"] - a["end"]
        a["chg_losses"] = a["chg_eff_b"] + a["chg_conv_l"] + a["chg_eff_l"] + a["clamp"]
        a["kit_res"] = (a["node_indep"] + a["start"]) - (a["served_l"] + a["spill_l"] + a["chg_losses"] + a["dsg_loss"] + a["end"])
        a["legacy_res"] = (a["unserved"] - a["legacy_unserved"]) - a["legacy_credit"]
        a["dsg_path_res"] = (a["dsg_loss"] - a["cutoff"]) - a["dsg_path"]
        a["cut_b"], a["cut_l"] = cut_b, cut_l
        a["node_dev"] = worst_dev
        return a

    def meanday(arch, key, n, build, hours, window, **kw):
        rs = [run(arch, key, n, build, s, hours, window, **kw) for s in (6, 18)]
        stops = [r_["first_stop"] for r_ in rs if r_["first_stop"] is not None]
        return {"ok": all(r_["ok"] for r_ in rs), "both": min(r_["low_t"] for r_ in rs), "base": min(r_["low_b"] for r_ in rs),
                "lid": min(r_["low_l"] for r_ in rs), "short": max(r_["short"] for r_ in rs), "stop": min(stops) if stops else None,
                "stops": [r_["first_stop"] for r_ in rs], "shorts": [r_["short"] for r_ in rs],
                "uns": [r_["uns"] for r_ in rs], "unserved": max(r_["uns"] for r_ in rs),
                "el": rs[0]["el_full"], "eb": rs[0]["eb_full"], "rs": rs}

    def cellx(s):
        if s["ok"]:
            return "%.1f (base %.1f, lid %.1f) %s/%s" % (s["both"], s["base"], s["lid"], "Y" if s["both"] > FLOOR else "N",
                                                         "Y" if s["base"] > FLOOR and s["lid"] > FLOOR else "N")
        return "NOT MET, stops at h %s, %.1f unserved" % ("/".join("-" if x is None else str(x) for x in s["stops"]), s["short"])

    def least(arch, key, build, hours, window, lo, hi, iters, **kw):
        def ok(x):
            s = meanday(arch, key, x, build, hours, window, **kw)
            return s["ok"] and s["both"] > FLOOR
        if not ok(hi):
            return None
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            if ok(mid):
                hi = mid
            else:
                lo = mid
        return hi

    # ------------------------------------------------------------------------------------------ 0b to 0d: this harness
    rto = open(os.path.join(TOP, RUNTIME_OUT), encoding="utf-8").read()
    bad = []
    pk = PACK0
    # section 1: D06 and A35 (runtime.py's own arithmetic, reproduced here)
    e20 = pk.usable_wh(load0, 20.0, pk.age80, "3v00", BASE_A1)[0]
    ecd = pk.usable_wh(load0, T_COLD, pk.age80, "3v00", BASE_A1)[0]

    def lid_loss(p_l, v_l):
        i = p_l / v_l
        return (i * vak[1] + i * i * TP.v("r_lid_dsg")) / p_l
    pb, pl = load0 * BASE_A2 / (BASE_A2 + LID_A), load0 * LID_A / (BASE_A2 + LID_A)
    v_l = pk.n_s * 3.60
    a2_only = []
    for t_ in (20.0, T_COLD):
        eb_ = pk.usable_wh(pb, t_, pk.age80, "3v00", BASE_A2)[0]
        el_ = pk.usable_wh(pl, t_, pk.age80, "3v00", LID_A)[0] * (1 - lid_loss(pl, v_l))
        a2_only.append((eb_, el_))
    a1_bo = (e20, ecd, e20 / load0, ecd / load0)
    ld2 = load0 + drain_w
    a2_bo = (sum(a2_only[0]), sum(a2_only[1]), sum(a2_only[0]) / ld2, sum(a2_only[1]) / ld2)
    for lab, row in (("D06: D-06's 4S3P of 35E (12 cells), no lid pack", a1_bo), ("A35: A(i) base 4S6P + lid 4S9P of 35E (60 cells)", a2_bo)):
        want = "   %-58s usable %6.1f Wh / %6.1f Wh: %5.2f h at +20 C, %5.2f h at %.0f C" % ((lab,) + row + (T_COLD,))
        if want not in rto:
            bad.append("runtime.out 1 %s" % lab[:3])
    # section 2: twenty cells
    sec2 = rto.split("\n2. BATTERY PLUS SOLAR", 1)[1].split("\n3. ", 1)[0]
    for hours in (48, 72):
        blk = sec2.split("   %d HOURS\n" % hours, 1)[1]
        for key in ("DRAWN", "NOM", "NOM90", "WE", "WE90"):
            line = "     %-8s TYP %-52s WAB %s" % (key, cellx(meanday("A2", key, LID_A, "TYP", hours, WIN_P03)),
                                                   cellx(meanday("A2", key, LID_A, "WAB", hours, WIN_P03)))
            if line not in blk:
                bad.append("runtime.out 2 %s %d h" % (key, hours))
    # section 3: the least lid, 48 and 72 h, NOM, WE, NOM90, TYP and WAB (runtime.py's bounds: 1 to 40, 30 steps)
    sec3 = rto.split("\n3. THE STORE THAT CARRIES", 1)[1].split("\n4. ", 1)[0]
    n3 = 0
    for hours in (48, 72):
        for key in ("NOM", "WE", "NOM90"):
            for b in ("TYP", "WAB"):
                x = least("A2", key, b, hours, WIN_P03, 1.0, 40.0, 30)
                s9, sx = meanday("A2", key, LID_A, b, hours, WIN_P03), meanday("A2", key, x, b, hours, WIN_P03)
                line = "     %d h %-6s %s: lid 4S%.2fP, against the both-kept 4S9P: %+.1f 35E cells, %+.1f Wh usable" % (
                    hours, key, b, x, 4 * (x - LID_A), sx["el"] - s9["el"])
                n3 += 1
                if line not in sec3:
                    bad.append("runtime.out 3 %s %s %d h" % (key, b, hours))
    # 0c: three_cases.out, AS DRAWN at WE inputs, the both-kept lid
    tco = EBS.head_equal(THREE_OUT)
    blk = tco.split("AS DRAWN, WE inputs:", 1)[1].split("\n   DERATED", 1)[0]
    mrow = need(blk, r"^\s+4S9P both kept\s+TYP NOT MET,\s+([\d.]+) unserved\s+N/N\s+WAB NOT MET,\s+([\d.]+) unserved", "three_cases.out drawn WE 4S9P")
    tc_rep = [meanday("A2", "DRAWN-WE", LID_A, b, 72, WIN_P03) for b in ("TYP", "WAB")]
    tc_ok = all((not s["ok"]) and "%.1f" % s["short"] == mrow.group(1 + i) for i, s in enumerate(tc_rep))
    blk = tco.split("DERATED VARIANT, WE inputs:", 1)[1].split("\n   RESISTOR", 1)[0]
    mrow_d = need(blk, r"^\s+4S9P both kept\s+TYP NOT MET,\s+([\d.]+) unserved\s+N/N\s+WAB NOT MET,\s+([\d.]+) unserved", "three_cases.out derated WE 4S9P")
    td_rep = [meanday("A2", "DERATED-WE", LID_A, b, 72, WIN_P03) for b in ("TYP", "WAB")]
    tc_ok = tc_ok and all((not s["ok"]) and "%.1f" % s["short"] == mrow_d.group(1 + i) for i, s in enumerate(td_rep))
    if not tc_ok:
        bad.append("three_cases.out AS DRAWN WE 4S9P")
    # 0d: the single-pack use (A1 with the lid off) against energy_budget.out 5b (100 Wp, 100 W, the record's chain, E3)
    bo = EBS.head_equal(BUDGET_OUT)
    b5 = {}
    for st in ("06:00", "18:00"):
        mm = need(bo, r"^\s+PS-IDLE-SPEC\s+42\.8\s+September\s+%s\s+([\d.]+)\s+[\d.]+\s+\d+\s+[\d.]+\s+(\d+)\s+(\d+)\s+([\d.]+)\s+NOT MET" % st,
                  "energy_budget.out 5b %s" % st)
        b5[st] = mm.groups()
    rep_d = {}
    for st, s_h in (("06:00", 6), ("18:00", 18)):
        rr = run("A1", "REC", BASE_A1, "TYP", s_h, 72, win_req016, wp=100.0, ratio=1.0, entry="E3")
        rep_d[st] = ("%.1f" % rr["eb_full"], str(rr["first_stop"]), "%d" % rr["acct"]["full_h"], "%.1f" % rr["short"])
    # the E3 run must carry the record's own chain, not a case's: check it
    d_chk = EBS.setup(0, pr0, v_nom, u3_e2, {})[0]
    chain_ok = abs(TP.chain(d_chk)[0] * TP.chain(d_chk)[1] * TP.chain(d_chk)[2] - RES0["eta"]) < 1e-12
    b5_ok = chain_ok and all(rep_d[st] == b5[st] for st in b5)
    if not b5_ok:
        bad.append("energy_budget.out 5b")
    if bad:
        sys.stdout.write("REPRODUCTION FAILED: %s\n" % "; ".join(bad))
        refuse(4, "%d reproduction check(s) failed" % len(bad))

    # ------------------------------------------------------------------------------------------ the header and section 0
    P("L4-E2: THE ENERGY ARCHITECTURE REPLAY UNDER REQ-016'S 100 W WINDOW (l4e_replay.py, layer 4, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, bought, powered or measured. MODELED on a1elec's energy_two_pack.py through l3plane's")
    P("energy_basis.py set-up (both pinned, imported unchanged). The corrected power path is HYPOTHETICAL; every WE figure is")
    P("CONDITIONAL on the three undocumented efficiencies (C-8). The author's analysis, AI arithmetic; not a qualified review and")
    P("not the independent check.")
    P("")
    P("0. REPRODUCTION (before any result)")
    P("   0a l3batt's runtime.py re-run in a child process reproduces runtime.out byte for byte (sha256 %s): yes" % PINS["l3batt/runtime.out"][:16])
    P("   (0b to 0d reproduce the model's own unserved counter, the LEGACY MODEL METRIC; every served and unserved figure from")
    P("   section 3 on is the SERVICE LEDGER's of section 5, which counts a stopped hour's sun once)")
    P("   0b this harness reproduces runtime.out section 1's D06 and A35 rows, the twenty cells of section 2 (400 Wp, 200 W) and")
    P("      section 3's %d least-lid lines (48 and 72 h; NOM, WE, NOM90; TYP and WAB): yes" % n3)
    P("   0c this harness reproduces three_cases.out's AS DRAWN and DERATED VARIANT rows at WE inputs, the both-kept lid, 72 h:")
    P("      TYP %.1f and %.1f, WAB %.1f and %.1f Wh unserved (the legacy model metric): yes" % (
        tc_rep[0]["short"], td_rep[0]["short"], tc_rep[1]["short"], td_rep[1]["short"]))
    P("   0d the single-pack use (the lid off) reproduces energy_budget.out 5b, PS-IDLE-SPEC, September, a 100 Wp panel in the")
    P("      100 W window on the record's own chain: 06 UTC usable %s Wh, first stop h %s, %s h run, %s Wh unserved; 18 UTC first" % (
        rep_d["06:00"][0], rep_d["06:00"][1], rep_d["06:00"][2], rep_d["06:00"][3]))
    P("      stop h %s, %s h run, %s Wh unserved (energy_budget.py's counter, the same legacy metric): yes (so 'full service' below" % (
        rep_d["18:00"][1], rep_d["18:00"][2], rep_d["18:00"][3]))
    P("      counts hours as the record's 'h run' does)")
    P("")

    # ------------------------------------------------------------------------------------------ 1. the assumption set
    u3we = CASES["WE"][2]["eta_u3"]
    u3dw = CASES["DRAWN-WE"][2]["eta_u3"]
    P("1. THE ONE ASSUMPTION SET (both architectures; only the stage window differs from runtime.out section 2)")
    P("   load       PS-IDLE-SPEC %.1f W at the pack terminals over its 39 loads (REQ-072's objective_profile); HF available, not" % load0)
    P("              receiving; the tablet not charged, the USB-C outlet off; A2 adds the lid path's standby drain %.3f W (WE)" % drain_w)
    P("   store      full at the start, aged to %.0f %% (REQ-014), each pack to its 3.00 V line with the %.0f %% reserve; the base at" % (
        100 * pk.age80, 100 * pk.rsoc))
    P("              +%.0f C, A2's lid at %.2f C (SC-37's air minimum); battery-only both at +20 C, then both at %.0f C" % (
        TP.v("t_base_c"), EBS.TMIN, T_COLD))
    P("   sun        SC-37's mean September day at Leiden, one plane 40/0, repeated; TYP the case, WAB a sensitivity (build ratio")
    P("              %.4f / %.4f on PVGIS's %.4f); starts 06 and 18 UTC; the availability series is the checked 400 Wp 2S2P trace" % (
        rat40["TYP"], rat40["WAB"], pr0))
    P("   window     the stage's input clipped at REQ-016's %.0f W (energy_inputs.yaml: '%s')" % (
        win_req016, D0["solar"]["window"]["stage_max_w_in"]["src"][:60]))
    P("   CORRECTED  HYPOTHETICAL, ENERGY-BASIS 6c's WE: bus %.3f V, U3's limit 6.1 A, U3 %.4f, U3B %.3f, stage %.2f, front end" % (
        v_min, u3we, TP.v("eta_u3b_lo"), ch[0]["eta"]))
    P("              %.2f, charge %.2f (CONDITIONAL), lid loops %.3f / %.3f Ohm, V(AK) %.0f mV; U3's cap %.1f W" % (
        ch[1]["eta"], ce["value"], rd[1], rc_[1], 1000 * vak[2], 6.1 * v_min))
    P("   AS DRAWN   board A as generated: R11 10 mOhm (front end's stacked minimum %.3f A less %.3f A of other loads = %.3f A)," % (
        held[0], other, fe_held))
    P("              U3 at its INFERRED minimum %.2f A (set 4.15 A), U3 %.4f; the other WE inputs as above (three_cases.py's" % (
        u3_e1 - U3_TOL, u3dw))
    P("              DRAWN at WE); cap %.1f W. UPPER BOUND: min(available, cap) kept, which A-2 says the drawn path does not" % (
        min(u3_e1 - U3_TOL, fe_held) * v_min))
    P("              guarantee. LOWER BOUND: A-2's inferred collapse, an hour whose power at VBUS20 is under the cap delivers nothing")
    P("   A1         one pack at +20 C, charged at %.2f A a cell (energy_inputs.yaml's D-06 figure, 3.06 A for 4S3P), no lid path" % chg_a1_cell)
    P("   A2         base 4S6P at +20 C (U3, %.3f A) and lid 4S9P at %.2f C (U3B, %.3f A, IIN %.1f A; the join of TOPOLOGY.md)" % (
        TP.v("chg_a_base"), EBS.TMIN, TP.v("chg_a_lid"), TP.v("iin_lid_a")))
    P("   pass line  COMB (the kit never stops and the lowest combined store stays above the %.1f Wh floor), as runtime.py" % FLOOR)
    P("")

    # ------------------------------------------------------------------------------------------ 2. battery only
    P("2. BATTERY-ONLY ENDURANCE (runtime.out section 1, reproduced in 0b; no solar)")
    P("   A1 D-06's 4S3P: usable %.1f Wh at +20 C, %.1f Wh at %.0f C: %.2f h and %.2f h" % (a1_bo[0], a1_bo[1], T_COLD, a1_bo[2], a1_bo[3]))
    P("   A2 base 4S6P + lid 4S9P: usable %.1f Wh at +20 C, %.1f Wh at %.0f C: %.2f h and %.2f h" % (a2_bo[0], a2_bo[1], T_COLD, a2_bo[2], a2_bo[3]))
    P("   against 48 h: A1 short by %.1f h (%.0f Wh at +20 C), A2 short by %.1f h (%.0f Wh at +20 C); against 72 h: A1 %.1f h (%.0f Wh)," % (
        48 - a1_bo[2], 48 * load0 - a1_bo[0], 48 - a2_bo[2], 48 * ld2 - a2_bo[0], 72 - a1_bo[2], 72 * load0 - a1_bo[0]))
    P("   A2 %.1f h (%.0f Wh). Battery-only closes neither end at any temperature; the objective is a solar-assisted one." % (
        72 - a2_bo[2], 72 * ld2 - a2_bo[0]))
    P("")

    # ------------------------------------------------------------------------------------------ 3. solar-assisted, 100 W
    P("3. SOLAR-ASSISTED, THE STAGE INPUT CLIPPED AT %.0f W: A CONDITIONAL SCREENING STIMULUS (section 7: the series is the 400 Wp" % win_req016)
    P("   2S2P trace, which REQ-016 does not admit). First interruption per start (hour from the start, and its UTC hour), unserved")
    P("   Wh at 48 h and at 72 h per start (the service ledger, section 5), and the hours of full service in each horizon")
    paths = (("CORRECTED, HYPOTHETICAL, WE", "WE", False), ("AS DRAWN, WE, upper bound", "DRAWN-WE", False),
             ("AS DRAWN, WE, lower bound (A-2 collapse)", "DRAWN-WE", True))
    archs = (("A1", "A1 D-06's 4S3P", BASE_A1), ("A2", "A2 base 4S6P + lid 4S9P", LID_A))
    main = {}
    for ak, alab, n in archs:
        for plab, key, col in paths:
            for b in ("TYP", "WAB"):
                s48 = meanday(ak, key, n, b, 48, win_req016, collapse=col)
                s72 = meanday(ak, key, n, b, 72, win_req016, collapse=col)
                main[(ak, key, col, b)] = (s48, s72)
            s48, s72 = main[(ak, key, col, "TYP")]
            w48, w72 = main[(ak, key, col, "WAB")]
            P("   %-26s %s" % (alab, plab))
            for i, st in enumerate((6, 18)):
                fs = s72["stops"][i]
                P("     TYP from %02d UTC: first interruption %s; unserved %6.1f Wh at 48 h, %6.1f Wh at 72 h; full service %2d of 48 h, %2d of 72 h" % (
                    st, "none" if fs is None else "h %2d (%02d UTC)" % (fs, (st + fs) % 24), s48["uns"][i], s72["uns"][i],
                    s48["rs"][i]["acct"]["full_h"], s72["rs"][i]["acct"]["full_h"]))
            P("     WAB (sensitivity): first interruption h %s; unserved at 48 h %s Wh, at 72 h %s Wh (06 / 18 UTC)" % (
                "/".join("-" if x is None else str(x) for x in w72["stops"]), " / ".join("%.1f" % x for x in w48["uns"]),
                " / ".join("%.1f" % x for x in w72["uns"])))
    P("   The same cases in runtime.out's window (200 W, P-03), for the difference the window alone makes (TYP, 06 / 18 UTC):")
    p03 = {}
    for ak, alab, n in archs:
        for plab, key, col in paths[:2]:
            a48 = meanday(ak, key, n, "TYP", 48, WIN_P03, collapse=col)
            a72 = meanday(ak, key, n, "TYP", 72, WIN_P03, collapse=col)
            p03[(ak, key)] = (a48, a72)
            P("     %-26s %-28s first interruption h %s; unserved %s Wh at 48 h, %s Wh at 72 h" % (
                alab, plab.split(",")[0] + ("" if key == "WE" else " (UB)"), "/".join("-" if x is None else str(x) for x in a72["stops"]),
                " / ".join("%.1f" % x for x in a48["uns"]), " / ".join("%.1f" % x for x in a72["uns"])))
    P("")

    # ------------------------------------------------------------------------------------------ 4. least additional storage
    P("4. THE LEAST ADDITIONAL USABLE STORAGE (COMB line, both starts, the %.0f W window; continuous parallel count; A1 grows its" % win_req016)
    P("   one pack at +20 C, A2 grows its lid at %.2f C with the base held at 4S6P, as runtime.py section 3; usable Wh aged)" % EBS.TMIN)
    lst = {}
    for ak, alab, n in archs:
        for plab, key, col in paths:
            for hours in (48, 72):
                for b in ("TYP", "WAB"):
                    if b == "WAB" and key != "WE":
                        continue
                    x = least(ak, key, b, hours, win_req016, 1.0, 160.0, 34, collapse=col)
                    s0 = meanday(ak, key, n, b, hours, win_req016, collapse=col)
                    if x is None:
                        lst[(ak, key, col, hours, b)] = None
                        P("     %-4s %-40s %d h %s: none up to %d in parallel" % (ak, plab, hours, b, 160))
                        continue
                    sx = meanday(ak, key, x, b, hours, win_req016, collapse=col)
                    k = "el" if ak == "A2" else "eb"
                    add = sx[k] - s0[k]
                    lst[(ak, key, col, hours, b)] = (x, add, sx["eb"] + sx["el"])
                    P("     %-4s %-40s %d h %s: %s 4S%.2fP; %+7.1f Wh usable (%+5.1f 35E cells) over %s, store %.1f Wh in all" % (
                        ak, plab, hours, b, "lid" if ak == "A2" else "pack", x, add, 4 * (x - n), "4S9P lid" if ak == "A2" else "4S3P",
                        sx["eb"] + sx["el"]))
    P("   What the records say fits (not changed here): A1's east pocket holds the ruled 4S3P block alone (packfit_west.out);")
    P("   A2 is the largest in-case store found with both lid functions kept: base 4S6P (M4a, M5, M6w OPEN) and 39 lid places")
    P("   (36 used; a1mech 1 and 2; the check's bound with P2 costing nothing, 43 places); no 21700 lid beats it (SHORTLIST.md 3)")
    P("")

    # ------------------------------------------------------------------------------------------ 5. energy accounts
    P("5. THE ENERGY ACCOUNT AND THE SERVICE LEDGER, TYP, 72 h, the %.0f W window (Wh over the run; per start; kit and per pack)" % win_req016)
    P("   array = the 400 Wp trace at the array; clip = above the window; stage in = into the stage; bus = at VBUS20 before the")
    P("   entry's cap (stage and front end losses taken); not taken = refused by the entry's cap or its collapse; U3 = U3's loss;")
    P("   node = at the system node; to load = the node's sun used by the load in the hour; accepted = taken into charge at the")
    P("   node; spill = offered to charge but refused (packs full or tapering, or the charge ceiling); stored = into the cells;")
    P("   chg loss = accepted less stored (U3B, the lid loop, the 0.95 charge efficiency); drawn = out of the cells; lid path =")
    P("   the lid's discharge path loss; cut = the first hour each pack stands at its line (the kit's stop puts both there);")
    P("   closure = start + stored - drawn - end.")
    P("   SERVICE LEDGER (check astra-check-l4e2-1, B1): served = the load in every hour it is carried in full, plus in the stop")
    P("   hour the sun and what the stores delivered, nothing in a stopped hour; charge losses = the base's 0.95, U3B and the lid")
    P("   loop, the lid's 0.95, and the model's full-store clamp; discharge losses = the lid path, and at the cutoff what the")
    P("   stores held but did not deliver; kit residual = node + start - (served + spill + charge losses + discharge losses + end),")
    P("   the node summed independently from the chain. The legacy model metric is energy_two_pack's unserved counter, which")
    P("   also credits each stopped hour's sun, up to the load, as served while charging with it (the credit printed)")
    for ak, alab, n in archs:
        for plab, key, col in paths:
            s72 = main[(ak, key, col, "TYP")][1]
            for i, st in enumerate((6, 18)):
                a = s72["rs"][i]["acct"]
                P("   %s %s, from %02d UTC" % (ak, plab, st))
                P("     array %.1f, clip %.1f, stage in %.1f, bus %.1f, not taken %.1f, U3 %.1f, node %.1f (hours the cap binds: %d)" % (
                    a["arr"], a["clip"], a["stage_in"], a["bus_avail"], a["not_taken"], a["u3_loss"], a["node"], a["cap_hours"]))
                P("     to load %.1f, accepted %.1f, spill %.1f, stored %.1f, chg loss %.1f; drawn %.1f, lid path %.1f; start %.1f, end %.1f" % (
                    a["sun_load"], a["accepted"], a["spill"], a["stored"], a["chg_loss"], a["drawn"], a["dsg_path"], a["start"], a["end"]))
                P("     cut base h %s, lid h %s, kit stop h %s; store closure %.2e" % (
                    "-" if a["cut_b"] is None else a["cut_b"], ("-" if a["cut_l"] is None else a["cut_l"]) if ak == "A2" else "(no lid)",
                    "-" if s72["rs"][i]["first_stop"] is None else s72["rs"][i]["first_stop"], a["closure"]))
                P("     LEDGER: asked %.1f, served %.1f, unserved %.1f; spill %.1f; charge losses %.1f (base 0.95 %.1f, U3B and loop %.1f," % (
                    a["asked"], a["served_l"], a["unserved"], a["spill_l"], a["chg_losses"], a["chg_eff_b"], a["chg_conv_l"]))
                P("     lid 0.95 %.1f, clamp %.1f); discharge losses %.1f (cutoff %.1f); stopped-hour sun %.1f, to charge %.1f, spilled %.1f;" % (
                    a["chg_eff_l"], a["clamp"], a["dsg_loss"], a["cutoff"], a["stop_sun"], a["stop_chg"], a["stop_spill"]))
                P("     kit residual %.2e; legacy model metric: unserved %.1f, its stopped-hour credit %.1f" % (
                    a["kit_res"], a["legacy_unserved"], a["legacy_credit"]))
    P("   THE LEDGER'S CLOSURE, every architecture, path, horizon and start (TYP, 100 W): unserved Wh and the kit residual")
    for ak, alab, n in archs:
        for plab, key, col in paths:
            cells = []
            for hi_, hours in enumerate((48, 72)):
                s_ = main[(ak, key, col, "TYP")][hi_]
                for i, st in enumerate((6, 18)):
                    aa = s_["rs"][i]["acct"]
                    cells.append("%d h %02d UTC %.6f (%.1e)" % (hours, st, aa["unserved"], aa["kit_res"]))
            P("     %s %-40s %s" % (ak, plab, "; ".join(cells[:2])))
            P("     %s %-40s %s" % ("  ", "", "; ".join(cells[2:])))
    chk = [main[("A2", "WE", False, "TYP")][hi_]["rs"][i]["acct"]["unserved"] for hi_ in (0, 1) for i in (0, 1)]
    if ["%.6f" % x for x in chk] != CHECK_B1:
        refuse(4, "the ledger does not reproduce the check's A2 corrected figures")
    P("   the check's own flow-derived figures for A2 corrected (astra-check-l4e2-1: %s Wh at 48 / 72 h, 06 / 18 UTC)" % " / ".join(CHECK_B1))
    P("   reproduced to the sixth decimal: yes")
    P("   (every run of this script, not only these, is refused unless its store closure, its kit residual, the legacy")
    P("   metric's difference from the ledger less the stopped-hour credit, and the lid path's loss less the model's all stay")
    P("   under 1e-6 Wh, and its node power equals the model's in every hour to 1e-9 W)")
    P("")

    # ------------------------------------------------------------------------------------------ 6. thresholds
    P("6. WHERE A RESULT COULD TURN ON AN UNDOCUMENTED FIGURE (TYP, 100 W; the corrected path unless named)")
    for ak, alab, n in archs:
        for key, lab in (("WE90", "the three at their 0.90 bracket"), ("WE97", "stage and front end 0.97, charge 0.98 (the high bracket)"),
                         ("WE100", "all three at 1.00 (the three undocumented efficiencies set to 1.00; U3, U3B and the lid path's losses retained)")):
            s48 = meanday(ak, key, n, "TYP", 48, win_req016)
            s72 = meanday(ak, key, n, "TYP", 72, win_req016)
            k = "el" if ak == "A2" else "eb"
            adds = []
            for hours in (48, 72):
                x = least(ak, key, "TYP", hours, win_req016, 1.0, 160.0, 34)
                adds.append("none up to 160 in parallel" if x is None else "%+.1f" % (
                    meanday(ak, key, x, "TYP", hours, win_req016)[k] - meanday(ak, key, n, "TYP", hours, win_req016)[k]))
            P("   %s, %s: 48 h %s; 72 h %s; least addition %s / %s Wh" % (
                ak, lab, "MET" if s48["ok"] else "NOT MET (%.1f)" % s48["unserved"], "MET" if s72["ok"] else "NOT MET (%.1f)" % s72["unserved"],
                adds[0], adds[1]))
    # U3's efficiency re-weighted over the 100 W day by the same method (s117's efficiency.py, TI's equations)
    e_st0, e_fe0, _ = TP.chain(D0)

    def u3_day_w(vin, ilim, reading, window):
        cap = min(0.043 / (TP.v("fe_r11_draft_mohm") / 1000.0) * vin, ilim * vin)
        pin = pout = 0.0
        for g in prof0:
            p = min(min(BUD.panel_w(g, WP_TRACE, pr0), window) * e_st0 * e_fe0, cap)
            if p < 1.0:
                continue
            e = EF.eta("buck", vin, p / vin, 14.5, min(3.968, p * 0.95 / 14.5), EF.CHOSEN_U3, EF.U3["ind"], EF.U3["f"],
                       EF.U3["r_in"], EF.U3["r_chg"], reading)
            pin += p
            pout += p * e
        return pout / pin
    if abs(u3_day_w(v_min, 6.1, "lower", WIN_P03) - u3we) > 1e-12:
        refuse(4, "u3_day_w does not reproduce energy_basis.u3_day at 200 W")
    u3w100 = u3_day_w(v_min, 6.1, "lower", win_req016)
    for ak, alab, n in archs:
        s72 = meanday(ak, "WE", n, "TYP", 72, win_req016, ov_extra={"eta_u3": u3w100})
        s48 = meanday(ak, "WE", n, "TYP", 48, win_req016, ov_extra={"eta_u3": u3w100})
        base72 = main[(ak, "WE", False, "TYP")]
        P("   %s, U3 re-weighted over the 100 W day (%.4f against WE's %.4f, TI's method at the makers' maxima): unserved %s at 48 h" % (
            ak, u3w100, u3we, " / ".join("%.1f" % x for x in s48["uns"])))
        P("      and %s at 72 h (was %s and %s)" % (" / ".join("%.1f" % x for x in s72["uns"]),
                                                 " / ".join("%.1f" % x for x in base72[0]["uns"]), " / ".join("%.1f" % x for x in base72[1]["uns"])))
    # A1's charge setting
    s_a = meanday("A1", "WE", BASE_A1, "TYP", 72, win_req016)
    s_b = meanday("A1", "WE", BASE_A1, "TYP", 72, win_req016, chg_cell=TP.v("chg_a_base") / BASE_A1)
    P("   A1 charged at %.3f A (code 31, %.2f A a cell, the generator's 4 A class) instead of 3.06 A: unserved at 72 h %s Wh" % (
        TP.v("chg_a_base"), TP.v("chg_a_base") / BASE_A1, " / ".join("%.1f" % x for x in s_b["uns"])))
    P("      against %s (06 / 18 UTC)" % " / ".join("%.1f" % x for x in s_a["uns"]))
    # the steady load each store carries (the discriminating measurement: the loads with no document)
    P("   The steady load at the pack terminals each store carries through the horizon (COMB, TYP, the profile's load replaced):")
    for ak, alab, n in archs:
        for plab, key, col in paths[:2]:
            vals = []
            for hours in (48, 72):
                lo, hi = 1.0, load0
                okf = lambda L: (lambda s: s["ok"] and s["both"] > FLOOR)(meanday(ak, key, n, "TYP", hours, win_req016, collapse=col, load_w=L))
                if okf(hi):
                    vals.append(">= %.1f" % hi)
                    continue
                for _ in range(30):
                    mid = 0.5 * (lo + hi)
                    if okf(mid):
                        lo = mid
                    else:
                        hi = mid
                vals.append("%.1f" % lo)
            P("     %s %-40s 48 h %s W, 72 h %s W (PS-IDLE-SPEC: PLAN %.1f, LOW 33.1, HIGH 82.8 W)" % (ak, plab, vals[0], vals[1], load0))
    P("")

    # ------------------------------------------------------------------------------------------ 7. what the stimulus represents
    P("7. WHAT THE 100 W RESULT REPRESENTS: the series is the 400 Wp 2S2P trace (a1solar's build, fixed point %.2f V, ratio %.4f TYP)" % (
        R40.win[1], rat40["TYP"]))
    e_st, e_fe = ch[0]["eta"], ch[1]["eta"]
    p_arr = [BUD.panel_w(g, WP_TRACE, pr0 * rat40["TYP"]) for g in prof0]
    arr, c200, c100 = sum(p_arr), sum(min(x, WIN_P03) for x in p_arr), sum(min(x, win_req016) for x in p_arr)
    hclip, pk_ = sum(1 for x in p_arr if x > win_req016), max(p_arr)
    P("   the stimulus: %.1f Wh a day at the array (peak %.1f W); %.1f Wh into the stage at 200 W; %.1f Wh at 100 W, clipped in %d hours" % (
        arr, pk_, c200, c100, hclip))
    node100 = c100 * e_st * e_fe * u3we
    ceil100 = sum(min(BUD.panel_w(g, 20000.0, pr0 * rat40["TYP"]), win_req016) for g in prof0) * e_st * e_fe * u3we
    demand = load0 * 24
    P("   at the node on WE: %.1f Wh a day through the 100 W window; the window's ceiling with a 20 kWp array (energy_budget.out 4's" % node100)
    P("   method, on WE's chain) %.1f. PS-IDLE-SPEC asks %.1f Wh a day at the pack terminals (%.1f with A2's drain): under WE no" % (
        ceil100, demand, demand + 24 * drain_w))
    P("   array carries the day's demand through this window, so each day ends shorter than it began and the store must hold the")
    P("   first night plus each later day's deficit (at the node, before charge losses, %.1f Wh a day with the stimulus)" % (demand - node100))
    need_wp = [(h, 100.0 / (prof0[h] / 1000.0 * pr0 * rat40["TYP"])) for h in range(24) if prof0[h] > 0.0]
    P("   the array needed to reach 100 W in an hour at the trace's ratio: %s" % ", ".join("%02d UTC %.0f Wp" % x for x in need_wp if x[1] < 2000.0))
    P("   REQ-016 admits a panel of at most 25 V open circuit at its coldest, held at 17.6 V, at most 100 W into the stage")
    P("   (acceptance: a bench supply on a 100 W panel's curve, MPP 17.6 V, Voc 25 V). The trace is 2S2P at %.2f V: 51.28 V cold" % R40.win[1])
    P("   (a1solar ARRAY.md 1), outside it. The held panel is outside it even alone (25.64 V at -20 C cells); a1solar ARRAY.md 5")
    P("   reads the SunPower (24.05 V) and PowerFilm's 15 V model (24.86 V) as admitted at -20 C, none at -40 C; neither has an")
    P("   availability trace in the tree. The records read an array above about 150 Wp of the 12 V class as re-rating the")
    P("   entry's 10 A (energy_budget.out 4), which REQ-016's acceptance names. So the 100 W result is a CONDITIONAL SCREENING")
    P("   STIMULUS: it stands for a compliant source only if one delivers, in every hour, at least min(the 400 Wp trace, 100 W).")
    P("   Sensitivity on the held panel's fit held at 17.6 V (a1solar's ratio method, INFERRED; the panel itself is not compliant):")
    for npar in (1, 2, 4):
        rr = R40.typical(v=17.6, ns=1, np_=npar)
        wp_ = 100.0 * npar
        for ak, alab, n in archs:
            s48 = meanday(ak, "WE", n, "TYP", 48, win_req016, wp=wp_, ratio=rr)
            s72 = meanday(ak, "WE", n, "TYP", 72, win_req016, wp=wp_, ratio=rr)
            p_arr = [BUD.panel_w(g, wp_, pr0 * rr) for g in prof0]
            P("     1S%dP %3.0f Wp, ratio %.4f, %.1f Wh a day into the stage: %s first interruption h %s; unserved %s at 48 h, %s at 72 h" % (
                npar, wp_, rr, sum(min(x, win_req016) for x in p_arr), ak, "/".join("-" if x is None else str(x) for x in s72["stops"]),
                " / ".join("%.1f" % x for x in s48["uns"]), " / ".join("%.1f" % x for x in s72["uns"])))
    P("   (1S4P of the held panel: 25.64 V at -20 C cells and a 40 A entry by a1solar ARRAY.md 5; shown for the energy only)")
    P("")

    # ------------------------------------------------------------------------------------------ 8. the charge path REQ-016 needs
    P("8. THE CHARGE PATH REQ-016'S WINDOW NEEDS (TYP, 100 W, the lowest bus %.3f V)" % v_min)
    for lab, es, efe in (("declared 0.93 x 0.93", ch[0]["eta"], ch[1]["eta"]), ("high bracket 0.97 x 0.97", ch[0]["high"], ch[1]["high"]),
                         ("no loss, 1.00 x 1.00", 1.0, 1.0)):
        p_bus = max(min(BUD.panel_w(g, WP_TRACE, pr0 * rat40["TYP"]), win_req016) for g in prof0) * es * efe
        setting = 0.05 * math.ceil((p_bus / v_min + U3_TOL) / 0.05 - 1e-9)
        P("   %-26s the largest power at VBUS20 %.1f W: U3's input minimum at least %.3f A; the 50 mA setting at least %.2f A," % (
            lab, p_bus, p_bus / v_min, setting))
        P("   %-26s its maximum %.2f A, so through R11 %.3f A (0.060 A of other loads) to %.3f A (C-9's 0.079 A)" % (
            "", setting + U3_TOL, setting + U3_TOL + 0.060, setting + U3_TOL + 0.079))
    for ak, alab, n in archs:
        for key, lab in (("WE", "CORRECTED, U3 6.1 A minimum (the drafted 6.2 A setting)"),
                         ("WINDOW-WE", "WINDOW-SIZED, U3 %.2f A minimum (a %.2f A setting), HYPOTHETICAL" % (U3_WINDOW - U3_TOL, U3_WINDOW)),
                         ("DERATED-WE", "DERATED VARIANT, U3 %.2f A minimum (4.00 A set), R11 as drawn, upper bound" % (U3_DERATED - U3_TOL)),
                         ("DRAWN-WE", "AS DRAWN, U3 %.2f A minimum (4.15 A set), upper bound" % (u3_e1 - U3_TOL))):
            r_ = [meanday(ak, key, n, "TYP", h, win_req016) for h in (48, 72)]
            x = [least(ak, key, "TYP", h, win_req016, 1.0, 160.0, 34) for h in (48, 72)]
            kk = "el" if ak == "A2" else "eb"
            add = ["%+.1f" % (meanday(ak, key, x[i], "TYP", h, win_req016)[kk] - r_[i][kk]) if x[i] is not None else "none"
                   for i, h in enumerate((48, 72))]
            P("   %s %-77s unserved %.1f / %.1f Wh at 48 / 72 h; least addition %s / %s Wh" % (
                ak, lab, r_[0]["unserved"], r_[1]["unserved"], add[0], add[1]))
    P("   the held front end (R11 10 mOhm) gives %.3f A to U3 at its stacked minimum; the drafted 6.2 mOhm gives 6.733 A; the" % fe_held)
    P("   corrected path's 6.1 A cap (%.1f W) never binds at 100 W: %s" % (6.1 * v_min, "yes" if all(
        main[(ak, "WE", False, b)][h]["rs"][i]["acct"]["cap_hours"] == 0 for ak, _l, _n in archs for b in ("TYP", "WAB") for h in (0, 1) for i in (0, 1)) else "NO"))
    P("")
    # ------------------------------------------------------------------------------------------ 9. the layer 3 headline cases
    P("9. THE LAYER 3 HEADLINE CASES: runtime.out section 2's rows (A2, 4S9P lid, TYP), the legacy model metric runtime.out")
    P("   published against the service ledger, under the Layer 3 case's own inputs (P-03's 400 Wp 2S2P array, the 200 W clip),")
    P("   then with only the window moved to REQ-016's 100 W (each figure the larger of the two starts, as runtime.out prints it)")
    for key, lab in (("DRAWN", "DRAWN, NOM inputs (runtime.out's AS DRAWN, an upper bound)"), ("NOM", "NOM, CORRECTED PATH, HYPOTHETICAL"),
                     ("WE", "WE, CORRECTED PATH, HYPOTHETICAL, CONDITIONAL")):
        r200 = [meanday("A2", key, LID_A, "TYP", h, WIN_P03) for h in (48, 72)]
        r100 = [meanday("A2", key, LID_A, "TYP", h, win_req016) for h in (48, 72)]
        P("   %-58s 200 W: stops h %s; legacy model metric %.1f / %.1f Wh (published), ledger %.1f / %.1f Wh at 48 / 72 h" % (
            lab, "/".join("-" if x is None else str(x) for x in r200[1]["stops"]), r200[0]["short"], r200[1]["short"],
            r200[0]["unserved"], r200[1]["unserved"]))
        P("   %-58s 100 W: stops h %s; legacy model metric %.1f / %.1f Wh, ledger %.1f / %.1f Wh at 48 / 72 h" % (
            "", "/".join("-" if x is None else str(x) for x in r100[1]["stops"]), r100[0]["short"], r100[1]["short"],
            r100[0]["unserved"], r100[1]["unserved"]))
    P("   (the published figures are understated by the stopped-hour double count; they stay as published in Layer 3)")
    P("")

    # ------------------------------------------------------------------------------------------ 10. the levers together
    P("10. THE IN-CONSTRAINT LEVERS TOGETHER, A2, CORRECTED, TYP, 100 W: each at its favourable end, none established")
    levers = (("WE as above (4S9P lid at %.2f C)" % EBS.TMIN, "WE", LID_A, None),
              ("+ the lid at the base's +20 C (a bound: no heating energy counted)", "WE", LID_A, 20.0),
              ("+ 4S10P in the lid (the check's 43-place bound, a1mech README 1)", "WE", 10, 20.0),
              ("+ stage and front end 0.97, charge 0.98 (the high bracket)", "WE97", 10, 20.0))
    for lab, key, n, tl in levers:
        r_ = [meanday("A2", key, n, "TYP", h, win_req016, t_l=tl) for h in (48, 72)]
        x = [least("A2", key, "TYP", h, win_req016, 1.0, 160.0, 34, t_l=tl) for h in (48, 72)]
        add = ["%+.1f" % (meanday("A2", key, x[i], "TYP", h, win_req016, t_l=tl)["el"] - r_[i]["el"]) if x[i] is not None else "none"
               for i, h in enumerate((48, 72))]
        loads = []
        for h in (48, 72):
            lo, hi = 1.0, load0
            okf = lambda L, h=h: (lambda s_: s_["ok"] and s_["both"] > FLOOR)(meanday("A2", key, n, "TYP", h, win_req016, t_l=tl, load_w=L))
            if okf(hi):
                loads.append(">= %.1f" % hi)
                continue
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                if okf(mid):
                    lo = mid
                else:
                    hi = mid
            loads.append("%.1f" % lo)
        P("   %-66s store %.1f Wh; unserved %.1f / %.1f Wh at 48 / 72 h;" % (lab, r_[0]["eb"] + r_[0]["el"], r_[0]["unserved"], r_[1]["unserved"]))
        P("   %-66s least addition %s / %s Wh; steady load carried %s / %s W" % ("", add[0], add[1], loads[0], loads[1]))
    P("")
    # ------------------------------------------------------------------------------------------ 11. O-2's bound
    if sha(os.path.join(TOP, LT8705A_PDF[0])) != LT8705A_PDF[1]:
        refuse(2, "the LT8705A sheet is not the pinned file")
    pages = {n: pdf_lines(LT8705A_PDF[0], n) for n in (2, 3, 4, 5, 6)}
    # (a) every tabled row reads back from the sheet as printed
    for r_ in EC_ROWS:
        got = ec_row(pages, r_["page"], r_["name"], r_["sub"])
        want = {"min": r_["min"], "typ": r_["typ"], "max": r_["max"]}
        if any((got[k] is None) != (want[k] is None) or (got[k] is not None and abs(got[k] - want[k]) > 1e-9) for k in want):
            refuse(3, "8705af p.%d '%s' %s reads %s, not the table's %s" % (r_["page"], r_["name"], r_["sub"] or "", got, want))
    # (b) every parameter line of pp.3 to 6 that names the mechanism is classified in the table
    unclassified = []
    for n in (3, 4, 5, 6):
        for ln in pages[n]:
            if not ln or ln[0].isspace() or ln.startswith("Note") or ln.startswith("Electrical") or ln.startswith("PARAMETER"):
                continue
            param = re.split(r"\s{3,}", ln.strip())[0]
            if any(t in param + " " for t in EC_TOKENS) and not any(r_["page"] == n and ln.startswith(r_["name"]) for r_ in EC_ROWS):
                unclassified.append("p.%d '%s'" % (n, param))
    if unclassified:
        refuse(3, "rows of 8705af that name the input-current mechanism or the hold are not classified: %s" % "; ".join(unclassified))
    m_vc = need("\n".join(pages[2]), r"VC Voltage \(Note 2\)\.+\s*([\u2013-]?[\d.]+)V to ([\d.]+)V", "8705af p.2 VC absolute maximum")
    vc_lo, vc_hi = (float(x.replace("\u2013", "-")) for x in m_vc.groups())
    dvc = max(abs(vc_hi - 1.2), abs(1.2 - vc_lo))        # the largest VC excursion from the 1.2 V the references are printed at
    gse = EBS.head_equal("v2/ecad/tools/gen_sch_e.py")
    r8 = float(need(gse, r'r\("R8", "([\d.]+)k 1% \(RFBIN1', "gen_sch_e.py R8").group(1))
    r9 = float(need(gse, r'r\("R9", "([\d.]+)k 1% \(RFBIN2', "gen_sch_e.py R9").group(1))
    reqs = open(os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml"), encoding="utf-8").read()
    r016 = " ".join(reqs.split("  - id: REQ-016\n", 1)[1].split("\n  - id: ", 1)[0].split())
    v_oc = float(need(r016, r"an open-circuit voltage of at most ([\d.]+) V at the panel's coldest", "REQ-016's open-circuit ceiling").group(1))
    p_win = float(need(r016, r"at most ([\d.]+) W into the stage", "REQ-016's window").group(1))

    # (c) THE SIZING: the stack the table's classification gives (STACK and ALLOWANCE rows only)
    by = {r_["id"]: r_ for r_ in EC_ROWS}
    use = lambda i, u: by[i]["use"] == u

    def size_kmax(v, ids):
        ref = by["IMON_REG"]
        vref = ref["max"] if (use("IMON_REG", "STACK") and "IMON_REG" in ids) else ref["typ"]
        line = by["IMON_LINE"]["max"] if (use("IMON_LINE", "STACK") and "IMON_LINE" in ids) else 0.0
        gms = [by[i]["min"] for i in ("A7_ALL", "A7_EI", "A7_HMP") if use(i, "STACK") and i in ids] or [by["A7_ALL"]["typ"]]
        ea = dvc / by["EA2_AV"]["typ"] if (use("EA2_AV", "ALLOWANCE") and "EA2_AV" in ids) else 0.0
        return i_factor(v, vref, ref["typ"], line, 1.0, ea, 1.0, min(gms), 1.0 - R_TOL, 1.0 - R_TOL)
    all_ids = set(by)
    steps = (("IMON_REG, A7 over the E and I grades' full range, the two resistors (the first issue's stack)", {"IMON_REG", "A7_EI"}),
             ("+ IMON_LINE, the reference's line regulation from 12 V to %.0f V" % v_oc, {"IMON_REG", "A7_EI", "IMON_LINE"}),
             ("+ A7 over every grade's printed limits (A7_ALL, A7_HMP: no grade is named)", {"IMON_REG", "A7_EI", "IMON_LINE", "A7_ALL", "A7_HMP"}),
             ("+ EA2_AV, the error amplifier's finite gain over VC's range (the ALLOWANCE)", all_ids))
    i_ceil = p_win / v_oc / size_kmax(v_oc, all_ids)
    i_set = math.floor(i_ceil / I_RES + 1e-9) * I_RES

    # (d) THE CHECK, independent of the classification: the limit's physics (p.31) with its rows read from the sheet
    ref_p = ec_row(pages, 4, "Regulation Voltages for IMON_IN and IMON_OUT", None)
    line_p = ec_row(pages, 4, "Line Regulation for IMON_IN and IMON_OUT Error Amp", None)["max"]
    gm_p = [ec_row(pages, 5, "VCSPIN-CSNIN to IMON_IN Amplifier A7 gm", g) for g in ("(All Grades)", "(LT8705AE, LT8705AI)", "(LT8705AH, LT8705AMP)")]
    gm_lo, gm_hi = min(g["min"] for g in gm_p), max(g["max"] for g in gm_p)
    ea_p = dvc / ec_row(pages, 5, "IMON_IN Error Amp EA2 Voltage Gain", None)["typ"]
    fb_p = [ec_row(pages, 4, "Regulation Voltage for FBIN", g) for g in ("(LT8705AE, LT8705AI)", "(LT8705AH, LT8705AMP)")]
    fbline_p = ec_row(pages, 4, "Line Regulation for FBOUT and FBIN Error Amp Reference", None)["max"]
    fbbias_p = ec_row(pages, 4, "FBIN Pin Bias Current", None)["typ"] * 1e-9
    ea3_p = dvc / ec_row(pages, 4, "FBIN Error Amp EA3 Voltage Gain", None)["typ"]

    def hold(vfb, ls, es, s8, s9, bias):
        v = vfb * (1 + r8 / r9)
        for _ in range(50):                          # the line term depends on the hold's own voltage: iterate to the fixed point
            vref = vfb * (1.0 + ls * fbline_p * 1e-2 * (v - V_LINE_REF)) + es * ea3_p
            v = vref * (1.0 + r8 * s8 / (r9 * s9)) - bias * r8 * 1e3 * s8
        return v
    v_lo = min(hold(min(f["min"] for f in fb_p), -1, -1, s8, s9, fbbias_p) for s8 in (1 - R_TOL, 1 + R_TOL) for s9 in (1 - R_TOL, 1 + R_TOL))
    v_hi_hold = max(hold(max(f["max"] for f in fb_p), 1, 1, s8, s9, 0.0) for s8 in (1 - R_TOL, 1 + R_TOL) for s9 in (1 - R_TOL, 1 + R_TOL))
    v_nom_hold = hold(fb_p[0]["typ"], 0, 0, 1.0, 1.0, 0.0)
    grid = sorted(set([v_lo, v_oc] + [round(v_lo + 0.01 * k, 6) for k in range(int((v_oc - v_lo) / 0.01) + 1)]))
    grid = [v for v in grid if v_lo - 1e-12 <= v <= v_oc + 1e-12]
    worst, n_corners = None, 0
    for t_end in T_ENDS:
        for vref, ls, gm, r1, r2, es in itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi),
                                                           (1 - R_TOL, 1 + R_TOL), (1 - R_TOL, 1 + R_TOL), (-1, 1)):
            for v in grid:
                pw = v * i_set * i_factor(v, vref, ref_p["typ"], line_p, ls, ea_p, es, gm, r1, r2)
                n_corners += 1
                if worst is None or pw > worst[0]:
                    worst = (pw, v, t_end, vref, ls, gm, r1, r2, es)
    if worst[0] > p_win + 1e-9:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "O-2's setting %.3f A lets the stage take %.4f W at %.3f V (%s): over REQ-016's %.0f W" % (
            i_set, worst[0], worst[1], worst[2], p_win))
    k_lo = min(i_factor(v_lo, vref, ref_p["typ"], line_p, ls, ea_p, es, gm, r1, r2)
               for vref, ls, gm, r1, r2, es in itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi),
                                                                 (1 - R_TOL, 1 + R_TOL), (1 - R_TOL, 1 + R_TOL), (-1, 1)))
    i_lo = i_set * k_lo
    p_lo, p_typ = v_lo * i_lo, v_nom_hold * i_set
    # the E or I grade fixed by procurement (information only)
    i_ceil_ei = p_win / v_oc / i_factor(v_oc, by["IMON_REG"]["max"], by["IMON_REG"]["typ"], by["IMON_LINE"]["max"], 1, dvc / by["EA2_AV"]["typ"], 1,
                                         min(by["A7_ALL"]["min"], by["A7_EI"]["min"]), 1 - R_TOL, 1 - R_TOL)

    P("11. O-2'S BOUND (checks astra-check-l4e2-1 and -2, B2): V_in x I_in,max at most %.0f W at every corner of the envelope" % p_win)
    P("   a current limit alone does not bound power: FBIN (8705af p.29) only lowers the current when the input falls below its")
    P("   set point, so while the input-current loop (p.31) limits, the input rises along the panel's curve toward its open-circuit")
    P("   voltage. A fixed %.2f A (%.0f W at 17.6 V) is %.1f W at a loaded 20 V and %.1f W at %.0f V" % (
        p_win / 17.6, p_win, 20.0 * p_win / 17.6, v_oc * p_win / 17.6, v_oc))
    P("   THE ROWS (8705af pp.2 to 6, read back from the pinned sheet by column, each equal to the table: yes; every parameter line")
    P("   of pp.3 to 6 naming %s classified: yes)" % ", ".join(t.strip() for t in EC_TOKENS))
    for r_ in EC_ROWS:
        P("     p.%d %-12s %-5s %s%s: %s / %s / %s %s%s" % (
            r_["page"], r_["id"], r_["use"][:5] if r_["use"] != "ALLOWANCE" else "ALLOW", r_["name"], (" " + r_["sub"]) if r_["sub"] else "",
            *("-" if r_[k] is None else ("%g" % r_[k]) for k in ("min", "typ", "max")), r_["unit"], " (full range)" if r_["full"] else " (25 C)"))
    P("     p.2 VC absolute maximum %.1f to %.1f V: the largest VC excursion from the references' VC = 1.2 V is %.1f V, so the" % (vc_lo, vc_hi, dvc))
    P("     EA2 allowance is %.1f V / %.0f = %.2f mV on IMON_IN and the EA3 allowance %.1f V / %.0f = %.2f mV on FBIN" % (
        dvc, by["EA2_AV"]["typ"], 1e3 * dvc / by["EA2_AV"]["typ"], dvc, by["EA3_AV"]["typ"], 1e3 * dvc / by["EA3_AV"]["typ"]))
    P("     RSENSE1 and RIMON_IN at %.0f %% each (ASSUMPTION, all of tolerance and drift); R8 %.0fk and R9 %.2fk at 1 %% (NETLIST)" % (
        100 * R_TOL, r8, r9))
    P("   THE ENVELOPE: the loaded input voltage from the hold's tolerance-adjusted lower corner %.3f V (FBIN %.3f V, every grade's" % (
        v_lo, min(f["min"] for f in fb_p)))
    P("   minimum; its line regulation, the EA3 allowance and the FBIN bias against it; R8 and R9 at their worst) to REQ-016's")
    P("   %.0f V open-circuit ceiling, which no loaded voltage exceeds; the hold spans %.3f / %.3f / %.3f V; both temperature ends" % (
        v_oc, v_lo, v_nom_hold, v_hi_hold))
    P("   (the full-range rows' printed limits hold at both; the 25 C rows applied as printed at both, ASSUMPTION)")
    P("   THE SETTING, sized by the classified stack at the %.0f V corner (the rows that moved it):" % v_oc)
    for lab, ids in steps:
        P("     %-100s ceiling %.6f A" % (lab, p_win / v_oc / size_kmax(v_oc, ids)))
    P("     rounded DOWN to the stated %.0f mA resolution: the nominal setting %.3f A (the E or I grade fixed by procurement would" % (
        1e3 * I_RES, i_set))
    P("     allow %.6f A)" % i_ceil_ei)
    P("   THE CHECK, independent of the classification (the limit's rows read from the sheet, %d corners: %d voltages from %.3f to" % (
        n_corners, len(grid), v_lo))
    P("   %.0f V, both temperature ends, and every combination of the reference, its line regulation, A7, the two resistors and" % v_oc)
    P("   the EA2 allowance at their limits): the worst corner %.3f V (both temperature ends alike), reference %.3f V, line %s," % (
        worst[1], worst[3], "+" if worst[4] > 0 else "-"))
    P("   gm %.2f mmho, resistors %s / %s, EA2 %s: V_in x I_in,max = %.4f W, margin %.4f W under %.0f W (refused above it)" % (
        worst[5], "low" if worst[6] < 1 else "high", "low" if worst[7] < 1 else "high", "+" if worst[8] > 0 else "-", worst[0],
        p_win - worst[0], p_win))
    P("   THE CONSEQUENCE: in an hour the limit acts, the stage takes between %.1f W at the lower corner (%.3f V x %.3f A, the" % (
        p_lo, v_lo, i_lo))
    P("   limit's lowest there) and %.0f W; at the nominal hold and setting %.1f W (%.3f V x %.3f A). Where between is the admitted" % (
        p_win, p_typ, v_nom_hold, i_set))
    P("   panel's own curve, INCONCLUSIVE until O-1 pins it. The fault threshold sits at IMON_IN 1.61 V typical, %.2f times the" % (
        by["IMON_OV"]["typ"] / by["IMON_REG"]["typ"]))
    P("   limit (p.31). The bench sweep runs from %.3f V to %.0f V at both temperature ends, steady state and transients recorded" % (v_lo, v_oc))
    P("   apart")
    P("   The replay with the stage window at the lower corner and at the nominal hold (CORRECTED, WE, TYP; a separate row, not")
    P("   the 100 W screening case, and still on the non-compliant stimulus):")
    o2rows = {}
    for wlab, win_ in (("lower corner %.1f W" % p_lo, p_lo), ("nominal hold %.1f W" % p_typ, p_typ), ("screening case %.0f W" % p_win, p_win)):
        for ak, alab, n in archs:
            r_ = [meanday(ak, "WE", n, "TYP", h, win_) for h in (48, 72)]
            x = [least(ak, "WE", "TYP", h, win_, 1.0, 160.0, 34) for h in (48, 72)]
            kk = "el" if ak == "A2" else "eb"
            add = ["%+.1f" % (meanday(ak, "WE", x[i], "TYP", h, win_)[kk] - r_[i][kk]) if x[i] is not None else "none"
                   for i, h in enumerate((48, 72))]
            o2rows[(wlab, ak)] = (r_, add)
            P("     %-22s %s: first interruption h %s; unserved %s at 48 h, %s at 72 h; least addition %s / %s Wh" % (
                wlab, ak, "/".join("-" if v_ is None else str(v_) for v_ in r_[1]["stops"]), " / ".join("%.1f" % v_ for v_ in r_[0]["uns"]),
                " / ".join("%.1f" % v_ for v_ in r_[1]["uns"]), add[0], add[1]))
    P("")
    # ------------------------------------------------------------------------------------------ 12. the candidate panel
    sp = os.path.join(TOP, SPR_PDF[0])
    if not os.path.exists(sp) or sha(sp) != SPR_PDF[1]:
        refuse(2, "the SunPower SPR-E-Flex-100 sheet is not the pinned file (fetch it: v2/docs/records/a1solar/fetch_held_back.py)")
    sp_text = " ".join(pdf_lines(SPR_PDF[0], 1))
    cspr = AC.CAND["SPR100"]
    for pat, key, scale in SPR_ROWS:
        val = float(need(sp_text, pat, "the SunPower sheet's %s" % key).group(1)) * scale
        if abs(val - cspr[key]) > 1e-9:
            refuse(3, "the SunPower sheet's %s reads %g, a1solar's CAND %g" % (key, val, cspr[key]))
    cells = int(need(sp_text, r"(\d+) Prime monocrystalline", "the SunPower sheet's cell count").group(1))
    gp = os.path.join(TOP, SPR_GUIDE[0])
    if not os.path.exists(gp) or sha(gp) != SPR_GUIDE[1]:
        refuse(2, "SunPower's guide 524958 Rev F is not the pinned file (fetch it: v2/docs/records/a1solar/fetch_held_back.py)")
    g3 = " ".join(" ".join(pdf_lines(SPR_GUIDE[0], 3)).split())
    if SPR_QUAL not in g3 or "Table 1: Electrical Characteristics" not in g3 or "SPR-E-Flex-100" not in g3 or "Page | 2" not in g3:
        refuse(3, "SunPower's guide 524958 Rev F p.3 does not carry Table 1's qualification as read")
    qual = float(need(g3, r"within (\d+)% of measured values", "the guide's tolerance").group(1)) / 100.0
    tol = need(sp_text, r"Power Tolerance\s+\+(\d+)/[\u2013-](\d+)%", "the SunPower sheet's power tolerance").groups()
    voc20, voc40 = AC.voc_at(cspr, -20.0), AC.voc_at(cspr, -40.0)
    if voc20 > v_oc + 1e-9:
        refuse(4, "the pinned panel's cold open-circuit voltage %.2f V exceeds REQ-016's %.0f V" % (voc20, v_oc))
    dsp = AC.Diode(cspr)
    fits = [("the exact fit", dsp), ("Rs 0.1 Ohm", AC.DiodeRs(cspr, 0.1)), ("Rs 0.2 Ohm", AC.DiodeRs(cspr, 0.2))]
    noct, rl = AC.NOCT_ASSUMED, AC.lead_r()
    vfx = [v_lo, v_nom_hold, v_hi_hold]
    vert = list(itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi), (1 - R_TOL, 1 + R_TOL), (1 - R_TOL, 1 + R_TOL), (-1, 1)))

    def lim_lo(v):
        return i_set * min(i_factor(v, a, ref_p["typ"], line_p, b, ea_p, c_, gm, r1, r2) for a, b, gm, r1, r2, c_ in vert)

    def lim_hi(v):
        return i_set * max(i_factor(v, a, ref_p["typ"], line_p, b, ea_p, c_, gm, r1, r2) for a, b, gm, r1, r2, c_ in vert)

    def lim_nom(v):
        return i_set

    def op_point(d, g, tc, v_hold, lim, r_lead):
        """The stage's input in one hour: the FBIN hold at v_hold (8705af p.29) while the panel gives less than the limit
        there; else the input-current limit (p.31), the board's voltage rising along the curve to where the panel gives it."""
        if g <= 0.0:
            return 0.0, 0.0, 0.0, False
        i_h = d.current(v_hold, g, tc, r_lead)
        if lim is None or i_h <= lim(v_hold):
            return v_hold * i_h, v_hold, i_h, False
        lo, hi = v_hold, d.mpp(g, tc)[2]
        for _ in range(80):
            m = 0.5 * (lo + hi)
            if d.current(m, g, tc, r_lead) > lim(m):
                lo = m
            else:
                hi = m
        v = 0.5 * (lo + hi)
        return v * lim(v), v, lim(v), True

    def trace(d, v_hold, lim, noct_=noct, r_lead=rl, npar=1):
        """Hour by hour on SC-37's mean September day: the stage's input power (W), by a1solar's convention: PVGIS's power at
        the maximum-power point (panel_w, its 0.9417 carrying the angle, spectral and temperature losses) times the single-diode
        model's operating point over its own maximum-power point at the same irradiance and cell temperature."""
        out, bound, lim_h = [], [], 0
        for h in range(24):
            g, ta = prof0[h], TA40[h]
            if g <= 0.0:
                out.append(0.0)
                continue
            tc = AC.t_cell(ta, g, noct_)
            pw, v_, i_, limited = op_point(d, g, tc, v_hold, (None if lim is None else (lambda v, lim=lim: lim(v) / npar)), r_lead * npar)
            pm = AC.arr_mpp(d, 1, 1, g, tc)[0]
            st = BUD.panel_w(g, 100.0 * npar, pr0) * (pw / pm)
            if st > p_win + 1e-9 or v_ * i_ * npar > p_win + 1e-9:
                refuse(4, "the candidate's trace exceeds %.0f W at hour %d" % (p_win, h))
            out.append(st)
            lim_h += limited
        return out, lim_h
    grid_rows = []
    for vlab, vh in (("lower hold corner", v_lo), ("nominal hold", v_nom_hold), ("upper hold corner", v_hi_hold)):
        for llab, lf in (("no input limit (as drawn)", None), ("limit at its lowest", lim_lo), ("limit nominal", lim_nom), ("limit at its highest", lim_hi)):
            tr, nl = trace(dsp, vh, lf)
            grid_rows.append((vlab, vh, llab, sum(tr), nl, tr))
    e_mpp = sum(BUD.panel_w(g, 100.0, pr0) for g in prof0)
    P("12. A NOMINALLY COMPATIBLE CANDIDATE PANEL WITH THE PROPOSED CONTROL (review L4-R02): the SunPower SPR-E-Flex-100, 1S1P;")
    P("   SOURCE COMPLIANCE INCONCLUSIVE (check astra-check-l4e3-1, B1); every figure below is conditional on the sheet's nominal values")
    P("   the sheet: %s" % SPR_PDF[0])
    P("   (SunPower document 523809 Rev D, a distributor's issue; held back by its terms, pinned by sha256; its one page read")
    P("   back and equal to a1solar's CAND['SPR100']): Pnom %.0f W (+%s / -%s %%), Vmpp %.1f V, Impp %.1f A, Voc %.1f V, Isc %.1f A;" % (
        cspr["p"], tol[0], tol[1], cspr["vmp"], cspr["imp"], cspr["voc"], cspr["isc"]))
    P("   Voc %.1f mV/K, Isc +%.1f mA/K, Pmax %.2f %%/K; %d cells; no NOCT and no low-irradiance data printed" % (
        1e3 * cspr["beta_voc_abs"], 1e3 * cspr["alpha_isc_abs"], 100 * cspr["gamma_p"], cells))
    rise = (v_oc - voc20) / cspr["voc"]
    P("   REQ-016's window at the kit's use boundary, -20 C (REQ-024 and D-02a: use at -20 to +40 C; REQ-016: at most %.0f V at the" % v_oc)
    P("   coldest operating temperature): the NOMINAL open circuit is %.2f V there, %.2f V under; the panel's own -40 C rating is a" % (
        voc20, v_oc - voc20))
    P("   component limit, not the kit's range (%.2f V there, for information). The guide %s" % (voc40, SPR_GUIDE[0]))
    quote = need(g3, r"(Rated electrical characteristics are within \d+% of measured values at Standard Test Conditions of: .*?spectrum\.)",
                 "the guide's qualification sentence").group(1)
    P("   (SunPower 524958 Rev F, printed p.2, PDF p.3, under Table 1, which lists the SPR-E-Flex-100) reads, verbatim:")
    P("     \"%s" % quote.split(" of: ")[0] + " of:")
    P("     %s\"" % quote.split(" of: ")[1])
    P("   The nominal margin admits an STC open circuit")
    P("   at most %.2f %% above the sheet's %.1f V (the coefficient held at its nominal); %.0f %% above gives %.2f V at -20 C. So the" % (
        100 * rise, cspr["voc"], 100 * qual, cspr["voc"] * (1 + qual) - (cspr["voc"] - voc20)))
    P("   panel is a nominally compatible candidate, not a shown compliant source; the 100 W nominal rating, the")
    P("   stage's window holding the input at most %.0f W; its hot short-circuit current about %.2f A, under F2 and J_SOLAR's 10 A" % (
        p_win, AC.isc_at(cspr, 70.0)))
    P("   the model (a1solar's array_calc, imported and pinned): the single-diode model without a shunt term, fitted to Isc, Voc,")
    P("   Vmpp and Impp with dP/dV = 0 at the maker's point (A %.4f V, Rs %.4f Ohm: %s)," % (dsp.a_ref, dsp.rs, dsp.fit_note))
    P("   temperature by the maker's coefficients, the current in proportion to irradiance; cells by the NOCT model at %.0f C" % noct)
    P("   (INFERRED: SunPower prints none)")
    P("   over SC-37's hourly air (%.1f to %.1f C), the 5 m lead at %.4f Ohm (ESTIMATE); by a1solar's convention the stage's input" % (
        min(TA40), max(TA40), rl))
    P("   is PVGIS's maximum-power figure (its 0.9417) times the model's operating point over the model's own maximum-power point")
    P("   the stage's input each hour: the FBIN hold while the panel gives less than O-2's limit there, else the limit with the")
    P("   voltage riding up the curve; the hold at %.3f / %.3f / %.3f V (section 11) and the limit at its lowest, nominal %.3f A" % (
        v_lo, v_nom_hold, v_hi_hold, i_set))
    P("   and its highest (section 11's rows at the operating voltage). At the maximum-power point the day gives %.1f Wh (PVGIS)" % e_mpp)
    P("   Wh a day into the stage (hours the limit binds):")
    for vlab, vh, llab, e_, nl, _tr in grid_rows:
        P("     %-18s %.3f V, %-26s %6.1f Wh (%d h)" % (vlab, vh, llab, e_, nl))
    get = {(r_[0], r_[2]): r_ for r_ in grid_rows}
    tr_drawn = get[("nominal hold", "no input limit (as drawn)")][5]
    tr_nom = get[("nominal hold", "limit nominal")][5]
    tr_low = get[("lower hold corner", "limit at its lowest")][5]
    worst_row = min(grid_rows, key=lambda r_: r_[3] if r_[2] != "no input limit (as drawn)" else 1e9)
    tr_worst = worst_row[5]
    sens = []
    for lab, dd, nn, rr in (("the Rs 0.1 Ohm fit", fits[1][1], noct, rl), ("the Rs 0.2 Ohm fit", fits[2][1], noct, rl),
                            ("cells 10 K hotter (NOCT %.0f C)" % (noct + 10), dsp, noct + 10, rl), ("the lead twice as long", dsp, noct, 2 * rl)):
        sens.append((lab, sum(trace(dd, v_nom_hold, lim_nom, nn, rr)[0])))
    P("   sensitivity at the nominal hold and limit: %s" % "; ".join("%s %.1f Wh" % x for x in sens))
    two = trace(dsp, v_nom_hold, lim_nom, npar=2)
    P("   two panels in parallel (1S2P), the same control: %.1f Wh a day (%d h limited); their %.1f A short circuit re-rates F2 and" % (
        sum(two[0]), two[1], 2 * AC.isc_at(cspr, 70.0)))
    P("   J_SOLAR's 10 A, which REQ-016's acceptance names: a proposal, the owner's (shown for the energy only)")
    gs = lambda tr: [x / (100.0 * pr0 / 1000.0) for x in tr]    # the stage's input as the model's irradiance at 100 Wp, pr0
    runs = (("AS DRAWN, WE, upper bound; no input limit, hold %.3f V" % v_nom_hold, "DRAWN-WE", False, tr_drawn),
            ("AS DRAWN, WE, lower bound (A-2 collapse); the same trace", "DRAWN-WE", True, tr_drawn),
            ("CORRECTED, WE; O-2 nominal (%.3f V, %.3f A)" % (v_nom_hold, i_set), "WE", False, tr_nom),
            ("CORRECTED, WE; O-2 lower edge (the lower hold corner %.3f V, the limit's lowest; the limit never binds)" % v_lo, "WE", False, tr_low),
            ("CORRECTED, WE; the least-energy corner (%s, %s)" % (worst_row[0], worst_row[2]), "WE", False, tr_worst))
    P("   A1 AND A2 ON THE CANDIDATE'S TRACE, conditional on its nominal sheet values (the stage's input as above; the rest of")
    P("   section 1's assumption set; the service")
    P("   ledger; pairs 06 / 18 UTC). The 100 W screening case of sections 3 and 4 stays beside it as a labelled comparison.")
    ctr = {}
    for lab, key, col, tr in runs:
        P("   %s: %.1f Wh a day into the stage" % (lab, sum(tr)))
        for ak, alab, n in archs:
            r_ = [meanday(ak, key, n, "TYP", h, win_req016, collapse=col, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            x = [least(ak, key, "TYP", h, win_req016, 1.0, 160.0, 34, collapse=col, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            kk = "el" if ak == "A2" else "eb"
            add = ["%+.1f" % (meanday(ak, key, x[i], "TYP", h, win_req016, collapse=col, gser=gs(tr), wp=100.0, ratio=1.0)[kk] - r_[i][kk])
                   if x[i] is not None else "none up to 160 in parallel" for i, h in enumerate((48, 72))]
            ctr[(lab, ak)] = (r_, add)
            P("     %s: first interruption h %s; unserved %s at 48 h, %s at 72 h; least addition %s / %s Wh" % (
                ak, "/".join("-" if v_ is None else str(v_) for v_ in r_[1]["stops"]), " / ".join("%.1f" % v_ for v_ in r_[0]["uns"]),
                " / ".join("%.1f" % v_ for v_ in r_[1]["uns"]), add[0], add[1]))
    P("   The steady load at the pack terminals A2 carries through the horizon on the candidate's trace (COMB, a sensitivity:")
    P("   PS-IDLE-SPEC stays the defined 42.8 W profile):")
    thr = {}
    for lab, key, tr in (("CORRECTED, O-2 nominal", "WE", tr_nom), ("CORRECTED, O-2 lower edge", "WE", tr_low),
                         ("AS DRAWN, upper bound", "DRAWN-WE", tr_drawn)):
        vals_ = []
        for ak in ("A2", "A1"):
            n = LID_A if ak == "A2" else BASE_A1
            for hours in (48, 72):
                lo, hi = 1.0, load0
                okf = lambda L: (lambda s_: s_["ok"] and s_["both"] > FLOOR)(meanday(ak, key, n, "TYP", hours, win_req016, load_w=L,
                                                                                    gser=gs(tr), wp=100.0, ratio=1.0))
                if okf(hi):
                    vals_.append(">= %.1f" % hi)
                    continue
                for _ in range(30):
                    mid = 0.5 * (lo + hi)
                    if okf(mid):
                        lo = mid
                    else:
                        hi = mid
                vals_.append("%.1f" % lo)
                thr[(lab, ak, hours)] = lo
        P("     %-28s A2 48 h %s W, 72 h %s W; A1 48 h %s W, 72 h %s W" % (lab, vals_[0], vals_[1], vals_[2], vals_[3]))
    P("")

    # ------------------------------------------------------------------------------------------ 13. the undocumented loads
    lto = EBS.head_equal("v2/docs/records/l3batt/load_trace.out")
    t_rows = [(float(m_.group(1)), m_.group(2).strip()) for m_ in re.finditer(r"^\s+([\d.]+)\s+T\s+(.+?)\s{2,}", lto, re.M)]
    t_sum = sum(w for w, _n in t_rows)
    tier = need(lto, r"T ([\d.]+)\s*$", "load_trace.out's tier T total")
    if abs(t_sum - float(tier.group(1))) > 0.051:
        refuse(3, "load_trace.out's T rows sum %.2f W, its tier line %s" % (t_sum, tier.group(1)))
    P("13. THE LOADS OF PS-IDLE-SPEC WITH NO DOCUMENT (review item): %d rows of load_trace.out's tier T, %.2f W at the pack" % (len(t_rows), t_sum))
    P("   terminals of the profile's %.1f W. Each: its figure now, the maker's figure held, and what would settle it" % load0)
    for w_, nm in t_rows:
        info = UNDOC.get(nm)
        if info is None:
            refuse(3, "the undocumented load '%s' has no entry in UNDOC" % nm)
        P("     %5.2f W  %s" % (w_, nm))
        for ln in info:
            P("            %s" % ln)
    P("   none of the three is settled by a held maker's figure: each stays INCONCLUSIVE until measured or specified. The profile")
    P("   is not lowered. On the candidate's trace A2's corrected path meets 48 h at a steady %.1f W (section 12), %.1f W under" % (
        thr[("CORRECTED, O-2 nominal", "A2", 48)], load0 - thr[("CORRECTED, O-2 nominal", "A2", 48)]))
    P("   the profile, against %.2f W of undocumented loads: settling them cannot by itself close the gap on that trace" % t_sum
      if load0 - thr[("CORRECTED, O-2 nominal", "A2", 48)] > t_sum else
      "   the profile, against %.2f W of undocumented loads: settling them could close the gap only if they fall that far" % t_sum)
    P("")
    P("END. Each line is the model's arithmetic; nothing is measured. No result here is demonstrated capability: the circuit as")
    P("drawn fails; the corrected path is HYPOTHETICAL and CONDITIONAL on three undocumented efficiencies; the 100 W results rest")
    P("on a series REQ-016 does not admit and are a screening stimulus only; section 12's candidate trace rests on one held sheet's")
    P("nominal values (source compliance INCONCLUSIVE), a single-diode fit to them and an INFERRED cell temperature, on one mean day.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
