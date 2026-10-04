#!/usr/bin/env python3
"""Layer 9 item 9.12, record l9stk, the pack path's protection (MESHSAT-1357, 4 October 2026): W4DP-F2's firmware-independent
element, on the owner's instruction of 4 October 2026, with TI's SLVA673A ("Robust Hot Swap Design") as the calculation basis.

Desk arithmetic on committed files and makers' sheets; nothing here was built, bought or measured. It prints:

  1. board P's existing protection with its FETs welded: whether any element opens the discharge path on current alone, with no
     firmware, at a current and time that keep every series part within its limits;
  2. the limiting series part, Q39/Q40 (L4-E11): its 150 C current with the uncertainty of its installed path (a target, not a
     measurement), and the exposure a trip allowed at the cells' 24 A would leave;
  3. the selected element: an LM5069-2 breaker on board P between the gauge's discharge FET and PACK_P (the part board E's U6
     already uses), sized by the sheet's limits: its sense so its largest actual limit is the cells' 24 A and its smallest stays
     above the 18 A service, its power limit, fault timer, dv/dt start, input clamp and two CSD18510Q5B FETs, whose safe
     operating area is read from the FET's Figure 10 and derated to their case temperature (SLVA673A equations 4 to 7);
  4. every series part held at the breaker's largest actual limit, from L4-E12's inside air plus its own heating;
  5. the owner's protection table, one row per case;
  6. the design defects with their owners, the interface demands, the missing physical evidence with its specimen, acceptance
     and supplier task, and the predicates test_l9stk.py holds.

Run from the repository root: python3 v2/docs/records/l9stk/l9stk_protection.py
The committed output is regenerated only through _bin/regen_out.py. Its held-back input (SLVA673A) is fetched by
fetch_held_back.py; without it the script refuses.
"""
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.dont_write_bytecode = True

PINS = {
    "copper": "v2/docs/records/l9stk/l9stk_copper.py",
    "copper_out": "v2/docs/records/l9stk/l9stk_copper.out",
    "lm5069": "v2/vendor/ti/ti-lm5069.pdf",
    "csd18510": "v2/vendor/battery/ti-csd18510q5b.pdf",
    "csd17570": "v2/vendor/battery/ti-csd17570q5b.pdf",
    "smcj": "v2/vendor/power/littelfuse-smcj-series-tvs.pdf",
    "readings": "v2/docs/records/l9stk/inputs/csd18510q5b-figure-readings-2026-10-04.json",
    "slva673a": "v2/vendor/ti/held/ti-slva673a.pdf",
    "gen_sch_a": "v2/ecad/tools/gen_sch_a.py",
    "gen_sch_p": "v2/ecad/tools/gen_sch_p.py",
    "gen_sch_e": "v2/ecad/tools/gen_sch_e.py",
    "lcsc_fill": "v2/ecad/tools/lcsc_fill.py",
    "l4e11_out": "v2/docs/records/l4e11/l4e11_power.out",
    "pack_protection": "v2/ecad/tools/pcb_pack_protection.yaml",
    "mdd_smbj": "v2/vendor/power/mdd-smbj-series-tvs.pdf",
    "murata_prf": "v2/vendor/battery/murata-prf-series.pdf",
    "gen_pcb_p": "v2/ecad/tools/gen_pcb_p.py",
    "board_p": "v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb",
    "thermal_coord": "v2/docs/review-packets/battery/THERMAL-COORDINATION.md",
}
# the session's design choices (SESSION under the owner's standing rule of 26 September 2026), each checked below
RS_PARTS_MOHM = (4.0, 7.5)   # the breaker's sense: two metal-element shunts in parallel, 2.6087 mOhm
RS_TOL = 0.01                # their tolerance
RS_TCR = 50e-6               # their temperature coefficient at most, per K (to be met by the part Layer 6 files)
RS_DT = 100.0                # the span the coefficient is applied over, K (25 to 125 C)
CAP_TOL = 0.10               # the timer and dv/dt capacitors (X7R), +-10 %
T_FAULT_TARGET = 1.0e-3      # the fault timer's longest time, s: the capacitor is the E6 value at or under it
I_INRUSH_TARGET = 0.75       # the dv/dt start's inrush ceiling, A: the capacitor is the E6 value at or over it
NFET = 2                     # the breaker's FETs in parallel
TI_MARGIN = 1.5              # SLVA673A 3.1.2.5: "the MOSFET can handle 1.5x more than what is required during a hot-short"
TI_STEADY_C = 125.0          # SLVA673A 3.1.2.2: "keep the steady state FET temperature below 125 C"
RTH_SPREAD = 0.20            # the sensitivity shown on Q39/Q40's installed path, +-20 %
TVS = "SMCJ18A"              # the breaker's input clamp: the part board A's D1 already uses (C374030)
D_EN_MM = 1.0                # the enable contact's length short of the dock's power pins, mm (Layer 7's requirement)
R17_ALLOW = 1.0              # R17 designed apart: its coupling into any battery FET's junction at most this, K/W (E-1 reads it)
NFET_BAT = 3                 # the battery FETs selected (Q39, Q40 and the added Q41, the same BUK6Y10-30P)
SPLIT_EXAMPLE = 0.05         # a cell split the fallback is sized for, 5 % (a cell carrying 1.05 of its group's third)
PAD_MM2 = 645.16             # 1 in2, the CSD18510Q5B sheet's RthJA pad
E6 = (1.0, 1.5, 2.2, 3.3, 4.7, 6.8, 10.0)


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l9stk_protection: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def pdf(key):
    try:
        r = subprocess.run(["pdftotext", "-layout", rel(PINS[key]), "-"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("pdftotext could not read %s (%s)" % (PINS[key], e))
    return r.stdout.decode("utf-8", "replace")


def e6(x, up):
    d = 10 ** math.floor(math.log10(x) + 1e-12)
    vals = [k * d for k in E6]
    if up:
        return min(v for v in vals if v >= x * (1 - 1e-9))
    return max(v for v in vals if v <= x * (1 + 1e-9))


def e96_up(x):
    d = 10 ** math.floor(math.log10(x) + 1e-12)
    for k in range(97):
        v = round(10 ** (k / 96.0), 2) * d
        if v >= x * (1 - 1e-9):
            return v
    return 10 * d


def copper():
    sp = importlib.util.spec_from_file_location("l9stk_copper_for_protection", rel(PINS["copper"]))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ the inputs, read
def read():
    I = {}
    t = pdf("lm5069")
    num = r"([0-9.]+)"
    I["vcl"] = tuple(float(x) / 1e3 for x in need(t, r"^VCL\s+Threshold voltage\s+VIN-SENSE voltage\s+%s\s+%s\s+%s\s+mV" % (num, num, num), "VCL").groups())
    I["tcl_typ"] = float(need(t, r"^tCL\s+Response time\s+VIN-SENSE stepped from 0 mV to 80 mV\s+%s\s+µs" % num, "tCL").group(1)) * 1e-6
    I["vcb"] = tuple(float(x) / 1e3 for x in need(t, r"^VCB\s+Threshold voltage\s+VIN to SENSE\s+%s\s+%s\s+%s\s+mV" % (num, num, num), "VCB").groups())
    I["tcb_max"] = float(need(t, r"^tCB\s+Response time\s+%s\s+%s\s+µs" % (num, num), "tCB").group(2)) * 1e-6
    m = need(t, r"^VTMRH\s+Upper threshold\s+%s\s+%s\s+%s\s+V" % (num, num, num), "VTMRH")
    I["vtmrh"] = (float(m.group(1)), float(m.group(3)))
    m = need(t, r"Restart cycles \(LM5069-2\)\s+%s\s+%s\s+%s\s+V" % (num, num, num), "the restart threshold")
    I["vtmrl_restart"] = (float(m.group(1)), float(m.group(3)))
    I["vtmrl_end"] = float(need(t, r"End of 8th cycle \(LM5069-2\)\s+%s\s+V" % num, "the eighth cycle's end").group(1))
    m = need(t, r"Fault detection current\s+%s\s+%s\s+%s\s+µA" % (num, num, num), "the fault timer current")
    I["itmr"] = (float(m.group(1)) * 1e-6, float(m.group(3)) * 1e-6)
    m = need(t, r"Fault sink current\s+%s\s+%s\s+%s\s+µA" % (num, num, num), "the fault sink current")
    I["isink"] = (float(m.group(1)) * 1e-6, float(m.group(3)) * 1e-6)
    m = need(t, r"Insertion time current\s+%s\s+%s\s+%s\s+µA" % (num, num, num), "the insertion time current")
    I["iins"] = (float(m.group(1)) * 1e-6, float(m.group(3)) * 1e-6)
    I["dc_retry_typ"] = float(need(t, r"Fault restart duty cycle\s+LM5069-2 only\s+%s%%" % num, "the restart duty").group(1)) / 100.0
    m = need(t, r"Source current\s+Normal operation, GATE-OUT = 5 V\s+%s\s+%s\s+%s\s+µA" % (num, num, num), "the gate source")
    I["igate"] = (float(m.group(1)) * 1e-6, float(m.group(3)) * 1e-6)
    I["isink_off_min"] = float(need(t, r"^IGATE\s+UVLO < 2\.5 V\s+%s\s+%s\s+%s\s+mA" % (num, num, num), "the 2 mA pulldown").group(1)) * 1e-3
    I["isink_cb_min"] = float(need(t, r"VIN to SENSE = 150 mV or VIN < PORIT, VGATE = 5 V\s+%s\s+%s\s+%s\s+mA" % (num, num, num), "the breaker pulldown").group(1)) * 1e-3
    m = need(t, r"^VGATE\s+GATE-OUT voltage\s+%s\s+%s\s+%s\s+V" % (num, num, num), "VGATE")
    I["vgate"] = (float(m.group(1)), float(m.group(3)))
    I["pwrlim"] = tuple(float(x) for x in need(t, r"^PWRLIM-1\s+Power limit sense voltage\s+SENSE-OUT = 48 V, RPWR = 150 k\S\s+%s\s+%s\s+%s\s+mV" % (num, num, num), "PWRLIM").groups())
    m = need(t, r"R PWR\s+([0-9.]+) u 10 (\d) u R SNS \(PLIM ([0-9.]+)mV u", "the RPWR equation")
    I["kpwr"], I["vpwr_off"] = float(m.group(1)) * 10 ** int(m.group(2)), float(m.group(3)) * 1e-3
    I["vsns_min"] = float(need(t, r"a VSNS of less than (\d+) mV is not recommended", "the VSNS floor").group(1)) * 1e-3
    I["poren_max"] = float(need(t, r"^POREN\s+VIN increasing\s+%s\s+%s\s+V" % (num, num), "POREN").group(2))
    m = need(t, r"^VIN\s+Supply voltage\s+%s\s+%s\s+V" % (num, num), "the supply range")
    I["vin_roc"] = (float(m.group(1)), float(m.group(2)))
    I["tj_roc"] = float(need(t, r"^TJ\s+Junction temperature\s+[-\u20130-9]+\s+(\d+)\s+°C", "the junction range").group(1))
    I["vin_sense_abs"] = float(need(t, r"^VIN to SENSE\s+[-\u20130-9.]+\s+([0-9.]+)\s+V", "VIN to SENSE's maximum").group(1))
    need(t, r"LM5069-2\s+Auto Retry on Fault", "the retry option")
    need(t, r"Minimum and maximum limits are specified through test, design, or statistical correlation at TJ= \u201340°C to 125°C", "the table's range")
    s = pdf("csd18510")
    I["fet_vds"] = float(need(s, r"^BVDSS\s+Drain-to-source voltage\s+VGS = 0 V, ID = 250 μA\s+(\d+)\s+V", "CSD18510 BVDSS").group(1))
    I["fet_vgs"] = float(need(s, r"VGS\s+Gate-to-Source Voltage\s+±(\d+)\s+V", "CSD18510 VGS").group(1))
    I["fet_rds"] = float(need(s, r"VGS = 10 V, ID = 32 A\s+%s\s+%s" % (num, num), "CSD18510 RDS(on)").group(2)) * 1e-3
    I["fet_tj"] = float(need(s, r"\u201355 to (\d+)\s+°C", "CSD18510 junction range").group(1))
    I["fet_qg"] = float(need(s, r"Qg\s+Gate charge total \(10 V\)\s+%s\s+%s\s+nC" % (num, num), "CSD18510 Qg").group(2)) * 1e-9
    I["fet_idm"] = float(need(s, r"IDM\s+Pulsed Drain Current, TA = 25°C\(\d\)\s+(\d+)\s+A", "CSD18510 IDM").group(1))
    I["fet_rthja"] = float(need(s, r"RθJA\s+Junction-to-ambient thermal resistance \(1\) \(2\)\s+%s\s+°C/W" % num, "CSD18510 RthJA").group(1))
    I["fet_vsd"] = float(need(s, r"VSD\s+Diode forward voltage\s+ISD = 32 A, VGS = 0 V\s+%s\s+%s\s+V" % (num, num), "CSD18510 VSD").group(2))
    I["fet_rthja_min_cu"] = float(need(s, r"Max RθJA = 50°C/W\s+Max RθJA = (\d+)°C/W", "the minimum-pad RthJA").group(1))
    I["fet_rthjc"] = float(need(s, r"RθJC\s+Junction-to-case thermal resistance \(1\)\s+%s\s+°C/W" % num, "CSD18510 RthJC").group(1))
    need(s, r"1-in2 \(6\.45-cm2\), 2-oz \(0\.071-mm\) thick Cu pad", "the RthJA board")
    rd = json.load(open(rel(PINS["readings"]), encoding="utf-8"))
    if rd["pdf_sha256_16"] != sha(PINS["csd18510"]):
        refuse("the figure readings were taken on another copy of the CSD18510Q5B sheet")
    I["rd"] = rd
    q = pdf("csd17570")
    I["q12_rds"] = float(need(q, r"VGS = 10 V, ID = 50 A\s+%s\s+%s\s+m\S" % (num, num), "CSD17570 RDS(on)").group(2)) * 1e-3
    I["q12_vsd"] = float(need(q, r"VSD\s+Diode Forward Voltage\s+ISD = 50 A, VGS = 0 V\s+%s\s+%s\s+V" % (num, num), "CSD17570 VSD").group(2))
    I["q12_rthja"] = float(need(q, r"RθJA\s+Junction-to-Ambient Thermal Resistance \(1\) \(2\)\s+%s" % num, "CSD17570 RthJA").group(1))
    v = pdf("smcj")
    m = need(v, r"^\s*%s\s+\S+\s+\S+\s+\S+\s+%s\s+%s\s+%s\s+%s\s+%s\s+%s\s" % (TVS, num, num, num, num, num, num), "the %s row" % TVS)
    I["tvs"] = dict(vr=float(m.group(1)), vbr_min=float(m.group(2)), vc=float(m.group(5)), ipp=float(m.group(6)))
    sm = pdf("mdd_smbj")
    I["d1_ifsm"] = float(need(sm, r"Peak forward surge current, 8\.3ms single half sine-wave\s+IFSM\s+(\d+)\s+A", "SMBJ IFSM").group(1))
    need(sm, r"^\s*SMBJ20A\s+SMBJ20CA\s", "the SMBJ20A row")
    mp = need(pdf("murata_prf"), r"PRF15BB103RB6RC\s+10k\+/-50%\s+\S+\s+(\d+)\+/-(\d+)\s+32V", "the PRF15BB103 row")
    I["ptc"] = (float(mp.group(1)), float(mp.group(2)))
    w = re.sub(r"\s+", " ", pdf("slva673a"))
    for phrase in ("a single MOSFET will take all of the current", "at least 10% above the maximum load current",
                   "the SOA can be derated accordingly using Equation 5", "The power function follows the format shown in Equation 6",
                   "Worst-case FET stress is PLIM watts for TTIMER seconds", "the MOSFET can handle 1.5x more than what is required during a hot-short",
                   "keep the steady state FET temperature below 125°C", "PFET = VIN,MAX × IINR for t = tstart-up /2",
                   "the pulsed drain current must be greater than the current threshold of the circuit breaker"):
        if phrase not in w:
            refuse("SLVA673A no longer reads %r" % phrase)
    a = open(rel(PINS["gen_sch_a"]), encoding="utf-8").read()
    caps = re.findall(r'c\("C[123]", "(\d+)u [^"]*", "CELL_FUSED", "GND"', a)
    if len(caps) != 3:
        refuse("board A's CELL_FUSED capacitors moved")
    I["c_cellfused"] = sum(float(x) for x in caps) * 1e-6
    I["tvs_on_a"] = bool(re.search(r'kisch\.tvs\("D1", "%s ' % TVS, a))
    need(a, r'part\("J_PRE1", "Connector", "Conn_01x01_Pin", "pre-charge pin, longer, mates first', "board A's pre-charge pin")
    I["r_pre"] = float(need(a, r'r\("R1", "(\d+)R 2W 2512", "PRECHG", "CELL\+"', "board A's R1").group(1))
    p = open(rel(PINS["gen_sch_p"]), encoding="utf-8").read()
    m = need(p, r'r\("R10", "(\d+)m 2512 (\d+)W \(sense\)", "GND", "PACK_N"', "board P's R10")
    I["r10"] = (float(m.group(1)) * 1e-3, float(m.group(2)))
    need(p, r'pfet5\("Q2", "CSD17570Q5B 30 V N-FET, discharge switch", "DSG_G", "SW", "PACK_P"', "board P's Q2 on PACK_P")
    need(p, r'"SMBJ20A', "board P's D1")
    need(p, r'part\("RT1", "Device", "Thermistor_PTC", "PRF15BB103RB6RC', "board P's chip PTC")
    m = need(open(rel(PINS["gen_pcb_p"]), encoding="utf-8").read(), r"(\d+) x (\d+), two layers", "board P's outline")
    I["p_outline"] = (float(m.group(1)), float(m.group(2)))
    I["p_courtyards"], I["p_holes"], I["p_parts"] = board_p_areas(open(rel(PINS["board_p"]), encoding="utf-8").read())
    tc_ = open(rel(PINS["thermal_coord"]), encoding="utf-8").read()
    need(tc_, r"finding BAT-F20 is OPEN", "BAT-F20's status")
    I["batf20_w10"] = float(need(tc_, r"about (\d+) W at 10 A", "BAT-F20's 10 A figure").group(1))
    e = open(rel(PINS["gen_sch_e"]), encoding="utf-8").read()
    I["u6_code"] = need(e, r'ic\("U6", 10, "LM5069MM-2 hot-swap controller[^"]*", "VSSOP10", \{[^}]*\}, "(C\d+)"\)', "board E's U6").group(1)
    f = open(rel(PINS["lcsc_fill"]), encoding="utf-8").read()
    I["fet_code"] = need(f, r'\(r"\^CSD18510Q5B", "PowerPAK_SO-8"\): "(C\d+)"', "the CSD18510Q5B's code").group(1)
    o = open(rel(PINS["l4e11_out"]), encoding="utf-8").read()
    I["c_vsys"] = float(need(o, r"VSYS's capacitance at most (\d+) uF", "VSYS's capacitance").group(1)) * 1e-6
    I["i_pre"] = float(need(o, r"pre-charge (\d+) A \(MAKER, RECORD\)", "the gauge's pre-charge").group(1))
    m = need(o, r"the pair ([0-9.]+) nF at -15 V and about ([0-9.]+) nF near 0 V", "the pair's Ciss")
    I["ciss2"] = (float(m.group(1)), float(m.group(2)))
    I["ciss3"] = float(need(o, r"a third FET would put\s+Ciss at ([0-9.]+) nF typical, over TI's (\d+) nF", "a third FET's Ciss").group(1))
    I["ciss_ti"] = float(need(o, r"a third FET would put\s+Ciss at [0-9.]+ nF typical, over TI's (\d+) nF", "TI's Ciss").group(1))
    I["bat_rthjmb"] = float(need(o, r"Table 6's maximum Rth\(j-mb\) ([0-9.]+) K/W", "the BUK6Y10-30P's Rth(j-mb)").group(1))
    pp = yaml.safe_load(open(rel(PINS["pack_protection"]), encoding="utf-8"))
    lim = pp["cell"]["limits"]
    I["series"], I["par"] = pp["pack"]["series"], pp["pack"]["parallel_min"]
    I["vmax"] = I["series"] * lim["charge_voltage_v"]["value"]
    I["vmin"] = I["series"] * lim["discharge_cutoff_v"]["value"]
    I["cell_a"] = lim["max_continuous_discharge_ma"]["value"] / 1000.0
    return I


def board_p_areas(t):
    """Board P's placed courtyards per face (the P2 board file; rectangles and lines by their bounding box, circles by their
    radius) and the parts placed: an area budget, not a floor plan."""
    idx = [m.start() for m in re.finditer(r'\n\t\(footprint "', t)] + [len(t)]
    area = {"F": 0.0, "B": 0.0}
    holes, parts = 0.0, []
    for a, b in zip(idx, idx[1:]):
        f = t[a:b]
        ref = re.search(r'\(property "Reference" "([^"]+)"', f).group(1)
        parts.append(ref)
        xs, ys = [], []
        for m in re.finditer(r'\(fp_(?:line|rect)\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)(?:(?!\(fp_).)*?\(layer "([FB])\.CrtYd"\)', f, re.S):
            xs += [float(m.group(1)), float(m.group(3))]
            ys += [float(m.group(2)), float(m.group(4))]
            side = m.group(5)
        if xs:
            area[side] += (max(xs) - min(xs)) * (max(ys) - min(ys))
        for m in re.finditer(r'\(fp_circle\s+\(center ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)(?:(?!\(fp_).)*?\(layer "[FB]\.CrtYd"\)', f, re.S):
            r_ = math.hypot(float(m.group(3)) - float(m.group(1)), float(m.group(4)) - float(m.group(2)))
            holes += math.pi * r_ * r_
    return area, holes, parts


def soa_amps(rd, seg, vds):
    """The current a Figure 10 line allows at vds, by log-log interpolation along its read segment."""
    ax = rd["axes"]
    x1, x10 = ax["x_px"]["1"], ax["x_px"]["10"]
    y100, y1 = ax["y_px"]["100"], ax["y_px"]["1"]
    (xa, ya), (xb, yb) = rd["soa_segments"][seg]
    x = x1 + (x10 - x1) * math.log10(vds)
    if not (xa <= x <= xb):
        refuse("%g V is outside the read segment of the %s line" % (vds, seg))
    y = ya + (yb - ya) * (x - xa) / (xb - xa)
    return 10 ** ((y1 - y) / ((y1 - y100) / 2.0))


def soa_power(soa, t):
    """SLVA673A equation 6 between the two printed lines that bracket t; above the 10 ms line the DC line (no extrapolation);
    below the 10 us line refused."""
    pts = [(10e-6, soa["10 us"]), (100e-6, soa["100 us"]), (1e-3, soa["1 ms"]), (10e-3, soa["10 ms"])]
    if t > pts[-1][0]:
        return soa["DC"]
    if t < pts[0][0]:
        refuse("a pulse of %g s is shorter than the shortest printed line" % t)
    for (t1, p1), (t2, p2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            m = math.log(p1 / p2) / math.log(t1 / t2)
            return max(p1 * (t / t1) ** m, soa["DC"])


# ------------------------------------------------------------------------------------------------ the computation
def compute():
    for k, p in PINS.items():
        if not os.path.isfile(rel(p)):
            refuse("pinned input %s (%s) is missing (SLVA673A: python3 v2/docs/records/l9stk/fetch_held_back.py)" % (k, p))
    cm = copper()
    CR = cm.compute()
    C = CR["in"]
    I = read()
    R = {"pins": {k: (p, sha(p)) for k, p in PINS.items()}, "in": I, "cu": C}
    vmax, t0, air = I["vmax"], C["t0"], C["air_c"]
    service, cont, cells = C["kd_a"], C["cont"], I["cell_a"] * I["par"]
    R.update(vmax=vmax, t0=t0, air=air, service=service, cont=cont, cells=cells)
    if abs(cells - C["cells_a"]) > 1e-9:
        refuse("the cells' continuous current differs from the copper record's")
    # 1. board P's existing protection with its FETs welded
    blade_open = C["blade_a"] * C["mini_rows"][1][0] / 100.0
    f2_open = C["f2"]["a"] * C["f2"]["open_pct"] / 100.0
    R["existing"] = [
        ("the gauge's OCD1, OCD2 (%g A %g s, %g A %g s)" % (C["gauge"][0][1], C["gauge"][0][2], C["gauge"][1][1], C["gauge"][1][2]), "firmware levels acting through Q1 and Q2", "none: Q1 and Q2 are welded"),
        ("the AFE's AOLD, ASCD (%g A, %g A)" % (C["gauge"][2][1], C["gauge"][3][1]), "comparators set from data flash, acting through Q1 and Q2", "none: Q1 and Q2 are welded"),
        ("the second level U2 (BQ7720700)", "cell voltage, open wire and temperature; no current input", "none on current"),
        ("F2's heater (SCF9550)", "fired by U2's COUT or the gauge's FUSE output (firmware)", "none on current without firmware"),
        ("F2's element (%g A)" % C["f2"]["a"], "%g %% holds %g h at least; %g %% opens within %g s" % (C["f2"]["hold_pct"], C["f2"]["hold_h"], C["f2"]["open_pct"], C["f2"]["open_s"]),
         "no opening assured under %.2f A" % f2_open),
        ("the 25 A MINI blades F1 (board P), F3 (board E)", "%g %% holds %g s at least; %g %% opens within %g s" % (C["mini_rows"][0][0], C["mini_rows"][0][1], C["mini_rows"][1][0], C["mini_rows"][1][2]),
         "no opening assured under %.2f A" % blade_open),
    ]
    R["existing_floor"] = min(blade_open, f2_open)
    # 2. Q39/Q40
    each, rth, lim = C["pair_mohm_each"] / 1000.0, C["pair_rth"], C["pair_limit"]

    def tj_pair(a, ta, rth_=rth):
        return ta + rth_ * (a / 2.0) ** 2 * each

    def i150(rth_, ta):
        return 2.0 * math.sqrt((lim - ta) / (rth_ * each))

    def rth_for(a, ta):
        return (lim - ta) / ((a / 2.0) ** 2 * each)
    P = dict(rth=rth, each=each, lim=lim, i150_air=i150(rth, air), i150_t0=i150(rth, t0),
             spread=[(f, i150(rth * f, air), i150(rth * f, t0)) for f in (1 - RTH_SPREAD, 1.0, 1 + RTH_SPREAD)],
             exposure=[(a, tj_pair(a, air), tj_pair(a, t0)) for a in (22.0, 23.0, cells)])
    R["pair"] = P
    # 3. the breaker
    vclmin, vcltyp, vclmax = I["vcl"]
    u = RS_TOL + RS_TCR * RS_DT
    rs = 1.0 / sum(1.0 / (x * 1e-3) for x in RS_PARTS_MOHM)
    B = dict(rs=rs, u=u, rs_lo=vclmax / (cells * (1 - u)), rs_hi=vclmin / (service * (1 + u)),
             icl_min=vclmin / (rs * (1 + u)), icl_typ=vcltyp / rs, icl_max=vclmax / (rs * (1 - u)),
             icb_min=I["vcb"][0] / (rs * (1 + u)), icb_max=I["vcb"][2] / (rs * (1 - u)))
    B["share"] = [(x, rs / (x * 1e-3)) for x in RS_PARTS_MOHM]
    # the alternatives not taken: a limit set at the pair's 150 C current, and a blade small enough to open under it
    B["alt_icl_max"] = P["i150_t0"]
    B["alt_icl_min"] = P["i150_t0"] * (vclmin / vclmax) * (1 - u) / (1 + u)
    B["alt_blade"] = P["i150_t0"] / (C["mini_rows"][1][0] / 100.0)
    B["alt_blade_pct"] = 100.0 * service / B["alt_blade"]
    B["rs_w"] = [(x, (B["icl_max"] * sh) ** 2 * x * 1e-3) for x, sh in B["share"]]
    plim_floor = I["vsns_min"] * vmax / rs
    B["rpwr"] = e96_up(I["kpwr"] * rs * (plim_floor - I["vpwr_off"] * vmax / rs))
    B["plim_nom"] = B["rpwr"] / (I["kpwr"] * rs) + I["vpwr_off"] * vmax / rs
    lo, typ, hi = I["pwrlim"]
    B["plim_min"], B["plim_max"] = B["plim_nom"] * lo / typ, B["plim_nom"] * hi / typ
    B["vsns_pl"] = B["plim_nom"] * rs / vmax
    B["plim_abs_max"] = (B["vsns_pl"] + (hi - typ) * 1e-3) * vmax / rs   # the spread read as an offset (a sensitivity)
    B["cl_bound_w"] = vmax * B["icl_max"]
    # the timer
    ct = e6(T_FAULT_TARGET * I["itmr"][0] / (I["vtmrh"][1] * (1 + CAP_TOL)), up=False)
    B["ct"] = ct
    B["tf_min"] = ct * (1 - CAP_TOL) * I["vtmrh"][0] / I["itmr"][1]
    B["tf_max"] = ct * (1 + CAP_TOL) * I["vtmrh"][1] / I["itmr"][0]
    # the dv/dt start (SLVA673A 2.2.2 and 3.2.2.7)
    cout = I["c_vsys"] + I["c_cellfused"]
    cdv = e6(I["igate"][1] * cout / I_INRUSH_TARGET / (1 - CAP_TOL), up=True)
    B.update(cout=cout, cdv=cdv, inrush_max=I["igate"][1] * cout / (cdv * (1 - CAP_TOL)),
             start_max=vmax * cdv * (1 + CAP_TOL) / I["igate"][0])
    B["start_p"] = vmax * B["inrush_max"]
    # SLVA673A equation 3: a start in power limit (the live docking after the breaker's release), at the largest power limit
    B["t_pl_charge"] = cout / 2.0 * (vmax ** 2 / B["plim_max"] + B["plim_max"] / B["icl_max"] ** 2)
    B["start_teq"] = B["start_max"] / 2.0
    # the gate's charge and the turn-off times (the FETs' Qg scaled to the gate's 12.6 V; the dv/dt capacitor's full swing)
    q = NFET * I["fet_qg"] * I["vgate"][1] / 10.0 + cdv * (1 + CAP_TOL) * I["vgate"][1]
    B["q_off"] = q
    B["t_off_cb"] = I["tcb_max"] + q / I["isink_cb_min"]
    B["t_off_timer"] = q / I["isink_off_min"]
    B["clear_max"] = B["tf_max"] + B["t_off_timer"]
    # the retry: a duty independent of the capacitor (the worst currents and thresholds), and the longest dwell
    dv_min = I["vtmrh"][0] - I["vtmrl_restart"][1]
    dv_max = I["vtmrh"][1] - I["vtmrl_restart"][0]
    on = (I["vtmrh"][1] - I["vtmrl_end"]) / I["itmr"][0]
    off = 7 * (dv_min / I["isink"][1] + dv_min / I["itmr"][1]) + (I["vtmrh"][0] - I["vtmrl_end"]) / I["isink"][1]
    B["duty_max"] = on / (on + off)
    B["dwell_max"] = ct * (1 + CAP_TOL) * (7 * (dv_max / I["isink"][0] + dv_max / I["itmr"][0]) + (I["vtmrh"][1] - I["vtmrl_end"]) / I["isink"][0])
    B["retry_avg"] = B["plim_max"] * B["duty_max"]
    # the FETs: conduction at the largest held current (SLVA673A 2.4: an even split when enhanced), the case (equation 4)
    rd = I["rd"]
    rds_hot = I["fet_rds"] * rd["rdson_normalized_at_150c_vgs10"]
    p_each = (B["icl_max"] / NFET) ** 2 * rds_hot
    B.update(rds_hot=rds_hot, p_each=p_each)
    B["tc_held"] = t0 + I["fet_rthja"] * NFET * p_each          # both FETs' loss through one pad's RthJA (adjacent pads, mutual not printed)
    B["tj_held"] = B["tc_held"] + I["fet_rthjc"] * p_each
    B["tc_retry"] = t0 + I["fet_rthja"] * B["retry_avg"]
    B["tc"] = max(B["tc_held"], B["tc_retry"])
    B["derate"] = (I["fet_tj"] - B["tc"]) / (I["fet_tj"] - 25.0)
    soa = {k: soa_amps(rd, k, vmax) * vmax for k in ("DC", "10 ms", "1 ms", "100 us", "10 us")}
    B["soa"] = soa
    B["i10us"] = soa_amps(rd, "10 us", vmax)
    B["fault_soa"] = soa_power(soa, B["clear_max"]) * B["derate"]
    B["fault_ratio"] = B["plim_max"] / B["fault_soa"]
    B["fault_ratio_abs"] = B["plim_abs_max"] / B["fault_soa"]
    B["cl_ratio"] = B["cl_bound_w"] / B["fault_soa"]
    B["start_soa"] = soa_power(soa, B["start_teq"]) * B["derate"]
    B["start_ratio"] = B["start_p"] / B["start_soa"]
    k_read = 1.0 - rd["uncertainty_pct"] / 100.0
    B["fault_ratio_low"], B["start_ratio_low"] = B["fault_ratio"] / k_read, B["start_ratio"] / k_read
    B["sense_abs_a"] = I["vin_sense_abs"] / (rs * (1 - u))

    def fet_check(rthja):
        tc_ = max(t0 + rthja * NFET * p_each, t0 + rthja * B["retry_avg"])
        d_ = (I["fet_tj"] - tc_) / (I["fet_tj"] - 25.0)
        return tc_, d_, B["plim_max"] / (soa_power(soa, B["clear_max"]) * d_) / k_read, B["start_p"] / (soa_power(soa, B["start_teq"]) * d_) / k_read
    lo_, hi_ = I["fet_rthja"], I["fet_rthja_min_cu"]
    for _ in range(60):
        mid = 0.5 * (lo_ + hi_)
        if max(fet_check(mid)[2:]) <= 1 / TI_MARGIN:
            lo_ = mid
        else:
            hi_ = mid
    B["rthja_need"] = lo_
    B["min_cu_ratio"] = max(fet_check(I["fet_rthja_min_cu"])[2:]) if fet_check(I["fet_rthja_min_cu"])[1] > 0 else float("inf")
    # B-P1: docking. Without a correction the breaker is on when the dock's power pins mate.
    der75 = (I["fet_tj"] - 75.0) / (I["fet_tj"] - 25.0)
    B["dock_uncorr"] = dict(i10_der=B["i10us"] * B["derate"], ratio=C["dock_pk"] / (B["i10us"] * B["derate"]), ratio75=C["dock_pk"] / (B["i10us"] * der75),
                            vsense=C["dock_pk"] * rs)
    # (b) board A's pre-charge pin as the inrush element: the lead time it would need is set by the hand, not bounded
    r_loop = vmax / C["dock_pk"]
    tau = I["r_pre"] * cout
    B["pre"] = dict(r_loop=r_loop, tau=tau, t_cb=tau * math.log(vmax / (B["icb_min"] * r_loop)), t_abs=tau * math.log(vmax / (B["sense_abs_a"] * r_loop)))
    # (a) SELECTED: a make-last enable contact into UVLO (LM5069 11.1.1, Figure 45): the insertion time, then the dv/dt start
    B["t_ins"] = (ct * (1 - CAP_TOL) * I["vtmrh"][0] / I["iins"][1], ct * (1 + CAP_TOL) * I["vtmrh"][1] / I["iins"][0])
    B["v_withdraw"] = D_EN_MM * 1e-3 / B["t_off_timer"]
    B["dock_vsense"] = B["inrush_max"] * rs
    # the cells' split, the fallback's spread, the timer's integration of key-down excursions
    B["split_max"] = cells / B["icl_max"] - 1.0
    B["spread"] = B["icl_max"] / B["icl_min"]
    B["spread_need"] = (cells / (1 + SPLIT_EXAMPLE)) / service
    B["d_ratchet"] = I["isink"][0] / (I["itmr"][1] + I["isink"][0])
    # the charge direction, the clamp's freewheel duty
    B["pre_w"] = I["fet_vsd"] * I["i_pre"]
    B["pre_tj"] = t0 + I["fet_rthja"] * B["pre_w"]
    B["d1_ratio"] = B["icb_max"] / I["d1_ifsm"]
    # IF-2: the pads against board P's area (the P2 placement)
    B["p_face"] = I["p_outline"][0] * I["p_outline"][1]
    B["p_free"] = B["p_face"] - I["p_courtyards"]["F"] - I["p_holes"]
    B["p_pads"] = NFET * PAD_MM2
    R["B"] = B
    # 4. the junction limit of the charger's battery FETs (B-P2), and every series part held at the breaker's largest limit
    a = B["icl_max"]
    ks, W = CR["ks"], CR["w"]
    rise = {oz: cm.rise_pair(a, W["pair_%sk" % n], o, ks) for oz, n, o in (("1 oz", "1", cm.OZ1), ("2 oz", "2", cm.OZ2))}
    dt_band = max(rise.values())
    r17 = C["r17"]["mohm"] / 1000.0
    pr17 = a * a * r17
    budget = lim - t0 - dt_band
    J = dict(dt_band=dt_band, rise=rise, pr17=pr17, budget=budget)
    for n_ in (2, 3):
        pe = (a / n_) ** 2 * each
        J[n_] = dict(p=pe, fet_only=budget / pe, apart=(budget - R17_ALLOW * pr17) / pe, anywhere=budget / (pe + pr17))
    J["ciss"] = {2: I["ciss2"], 3: (I["ciss3"], I["ciss2"][1] * 3 / 2.0)}
    J["vs_target"] = J[3]["apart"] / rth

    def tj_sel(amps):
        rb = max(cm.rise_pair(amps, W["pair_%sk" % n], o, ks) for n, o in (("1", cm.OZ1), ("2", cm.OZ2)))
        return t0 + rb + J[NFET_BAT]["apart"] * (amps / NFET_BAT) ** 2 * each + R17_ALLOW * amps * amps * r17
    J["tj_service"] = tj_sel(service)
    J["tj_cont"] = tj_sel(cont)
    J["tj_held"] = tj_sel(a)
    J["ptc_service_pair"] = tj_pair(service, t0)
    R["J"] = J
    per = 0.5 * a / CR["field_pack"]
    q12_p = a * a * I["q12_rds"] * rd["rdson_normalized_at_150c_vgs10"]
    S = []

    def part(name, reading, frac, status):
        S.append(dict(name=name, reading=reading, frac=frac, status=status))
    part("the cells (%dP of %g A continuous)" % (I["par"], I["cell_a"]), "%.2f A, %.2f A a cell at an even split" % (a, a / I["par"]), a / cells,
         "printed; the split NOT HELD: E-5 with its fallback")
    part("Q39/Q40/Q41 (%d x BUK6Y10-30P, %g mOhm each at 150 C)" % (NFET_BAT, C["pair_mohm_each"]), "TJ %.1f C at the junction limit's allowances" % J["tj_held"],
         (J["tj_held"] - t0) / (lim - t0), "DESIGN DEFECT DD-2 until drawn; E-1")
    part("Q1 on board P with BAT-F20 (CHGIN = 1, the reading above T3)", "its body diode %.1f W (VSD %g V at most)" % (I["q12_vsd"] * a, I["q12_vsd"]), None,
         "DESIGN DEFECT DD-5 (BAT-F20, EQ-15): about %g W at 10 A already" % I["batf20_w10"])
    part("Q1/Q2 on board P, both enhanced (CSD17570Q5B, %g mOhm at 10 V, RthJA %g C/W)" % (I["q12_rds"] * 1e3, I["q12_rthja"]),
         "%.3f W each; TJ %.1f C on its own pad, %.1f C with both losses through one pad" % (q12_p, t0 + I["q12_rthja"] * q12_p, t0 + I["q12_rthja"] * 2 * q12_p),
         (I["q12_rthja"] * 2 * q12_p) / (150.0 - t0), "derived: the x%.1f is the CSD18510Q5B's (ASSUMPTION, E-8)" % rd["rdson_normalized_at_150c_vgs10"])
    part("the breaker's FETs (%d x CSD18510Q5B)" % NFET, "%.3f W each; TJ %.1f C (case %.1f C)" % (p_each, B["tj_held"], B["tc_held"]), (B["tj_held"] - t0) / (TI_STEADY_C - t0),
         "derived (IF-2, E-11)")
    part("R17 on board A (%s, %g W)" % (C["r17"]["mpn"], C["r17"]["w"]), "%.2f W" % pr17, pr17 / C["r17"]["w"], "printed at 25 C; derating NOT HELD (E-6)")
    part("R10 on board P (%g mOhm 2512, %g W)" % (I["r10"][0] * 1e3, I["r10"][1]), "%.2f W" % (a * a * I["r10"][0]), a * a * I["r10"][0] / I["r10"][1], "printed at 25 C; derating NOT HELD (E-6)")
    part("the breaker's sense (%s mOhm)" % " and ".join("%g" % x for x in RS_PARTS_MOHM), "; ".join("%.2f W in %g mOhm" % (w_, x) for x, w_ in B["rs_w"]), None,
         "a requirement on Layer 6's parts: 2 W each at the band's temperature")
    part("the XT60 (%g A, %g C)" % (C["xt60_a"], C["xt60_max_c"]), "%.2f A" % a, a / C["xt60_a"], "printed")
    part("the dock contacts (%d x %g A at a %g C rise)" % (C["pins"], C["pin_a"], C["pin_rise"]), "%.2f A a pin at an even split" % (a / C["pins"]), a / C["pins"] / C["pin_a"],
         "printed; the split NOT HELD (E-4)")
    part("the 25 A blades (MINI 297)", "%.1f %% of rating" % (100 * a / C["blade_a"]), a / (C["blade_a"] * C["mini_rows"][0][0] / 100.0),
         "printed hold at 110 %% for %g h at 25 C; the rerating NOT HELD (E-7)" % (C["mini_rows"][0][1] / 3600.0))
    part("F2's element (%g A)" % C["f2"]["a"], "%.1f %% of rating" % (100 * a / C["f2"]["a"]), a / C["f2"]["a"], "printed hold; its own range is the battery stream's")
    part("the pack path's copper (1 oz %.2f mm, 2 oz %.2f mm a face)" % (W["pair_1k"], W["pair_2k"]), "%.2f K steady" % dt_band, dt_band / 10.0, "decision 35's model (section 14)")
    part("the barrel field (%d of 0.4 mm)" % CR["field_pack"], "%.2f A a barrel, %.2f K" % (per, cm.barrel_rise(per, "inward")), cm.barrel_rise(per, "inward") / 10.0, "decision 35's model")
    part("the Keystone 3568 holder", "no current rating printed", None, "DESIGN DEFECT DD-4 (NOT HELD)")
    R["series"] = S
    # 5. the protection table
    T = []

    def row(case, cur, trip, clear, limiting, margin, status):
        T.append(dict(case=case, cur=cur, trip=trip, clear=clear, limiting=limiting, margin=margin, status=status))
    row("10 A continuous", "%.1f A held" % cont, "none reached (%.2f A least)" % B["icl_min"], "not a fault",
        "the XT60, %.2f of %g A" % (cont / C["xt60_a"], C["xt60_a"]), "%.2f" % (1 - cont / C["xt60_a"]), "printed")
    row("18 A for 60 s", "%.1f A, %g s" % (service, C["kd_s"]), "none reached (%.2f A least; %.2f A typical)" % (B["icl_min"], B["icl_typ"]),
        "not a fault; firmware ends it", "Q39 to Q41, TJ %.1f C at the allowances" % J["tj_service"], "%.1f K; the least limit %.2f A over the service" % (lim - J["tj_service"], B["icl_min"] - service),
        "derived; E-1, E-10")
    row("an overload under the unit's limit, held", "%.2f to %.2f A, indefinitely" % (service, a), "%.2f A largest (VCL %.1f mV, RS -%.1f %%)" % (a, vclmax * 1e3, 100 * u),
        "none: held by design", "Q39 to Q41 at %.1f C; the cells at %.3f of 8 A; Q1's body diode %.1f W under BAT-F20" % (J["tj_held"], a / cells, I["q12_vsd"] * a),
        "0 K at the allowances; %.2f %% split at most; Q1 OVER" % (100 * B["split_max"]), "DESIGN DEFECTS DD-2, DD-5; E-1, E-5")
    row("an overload over the unit's limit", "limited to %.2f A at most, then off" % a, "%.2f A largest" % a,
        "%.2f ms from the onset (timer %.3f, gate %.3f); regulated after tCL (%g us typ., no max.)" % (B["clear_max"] * 1e3, B["tf_max"] * 1e3, B["t_off_timer"] * 1e3, I["tcl_typ"] * 1e6),
        "the breaker FET, %.1f W for %.2f ms vs %.1f W" % (B["plim_max"], B["clear_max"] * 1e3, B["fault_soa"]), "%.2f (TI <= %.2f)" % (B["fault_ratio"], 1 / TI_MARGIN),
        "derived: the power limit at 5 mV and 10.6 to 16.8 V not printed (E-2)")
    row("a hot short, board P's FETs welded", "%g to %g A prospective" % (C["pf_low"], C["pf_high"]), "%.2f A largest (VCB %g mV)" % (B["icb_max"], I["vcb"][2] * 1e3),
        "%.1f us to the release, then as the row above: %.2f ms" % (B["t_off_cb"] * 1e6, (B["t_off_cb"] + B["clear_max"]) * 1e3),
        "the breaker FET: IDM %g A against the breaker's threshold (SLVA673A 3.1.2.2); VIN to SENSE over %g V above %.1f A" % (I["fet_idm"], I["vin_sense_abs"], B["sense_abs_a"]),
        "%.2f of IDM" % (B["icb_max"] / I["fet_idm"]), "(c) MISSING: E-3; the 0.3 V to TI (Q-TI-L9S-1)")
    row("a start into a short", "%.2f A at most (PLIM/VIN)" % (B["plim_max"] / vmax), "the power limit", "%.2f ms" % (B["clear_max"] * 1e3),
        "the breaker FET, as an overload", "%.2f" % B["fault_ratio"], "derived")
    row("a start (the gauge's FET on, a retry, assembly)", "%.3f A at most for %.1f ms" % (B["inrush_max"], B["start_max"] * 1e3), "none: %.1f W < %.1f W least" % (B["start_p"], B["plim_min"]),
        "not a fault", "the breaker FET, %.1f W for %.1f ms vs %.1f W (DC line)" % (B["start_p"], B["start_teq"] * 1e3, B["start_soa"]), "%.2f (TI <= %.2f)" % (B["start_ratio"], 1 / TI_MARGIN),
        "derived; IF-1")
    row("docking, the make-last enable (C-1b)", "%.3f A at most for %.1f ms, %.1f to %.1f ms after the enable mates" % (B["inrush_max"], B["start_max"] * 1e3, B["t_ins"][0] * 1e3, B["t_ins"][1] * 1e3),
        "none: a start", "not a fault", "the breaker FET as a start; VIN to SENSE %.2f mV" % (B["dock_vsense"] * 1e3), "%.2f (TI <= %.2f)" % (B["start_ratio"], 1 / TI_MARGIN),
        "derived; DD-6 until drawn; E-3")
    row("docking without the enable (the uncorrected design)", "E11-30's %.1f A peak with the breaker on" % C["dock_pk"], "%.2f A largest" % B["icb_max"], "%.1f us to the release" % (B["t_off_cb"] * 1e6),
        "the breaker FET: the 10 us line derated to %.1f C is %.1f A; VIN to SENSE %.3f V" % (B["tc"], B["dock_uncorr"]["i10_der"], B["dock_uncorr"]["vsense"]),
        "OVER: %.2f x the line (%.2f x at 75 C); %.2f x 0.3 V" % (B["dock_uncorr"]["ratio"], B["dock_uncorr"]["ratio75"], B["dock_uncorr"]["vsense"] / I["vin_sense_abs"]),
        "DESIGN DEFECT DD-6, corrected by C-1b (not a coupon)")
    row("a persistent fault, retrying", "the power limit at %.2f %% duty at most (%.1f %% typ.)" % (100 * B["duty_max"], 100 * I["dc_retry_typ"]), "as above", "each try as above",
        "the breaker FET, %.2f W average, case %.1f C" % (B["retry_avg"], B["tc_retry"]), "in the derating above", "derived")
    row("charging (the reverse direction)", "the charger's current; %g A precharge through a body diode while the breaker is off" % I["i_pre"], "none: the LM5069 does not limit reverse current",
        "not a fault", "the breaker FET's body diode, %.2f W, TJ %.1f C" % (B["pre_w"], B["pre_tj"]), "%.1f K" % (I["fet_tj"] - B["pre_tj"]), "printed (VSD); derived")
    row("the clamp shorted with board P's FETs welded (two faults)", "%g to %g A prospective" % (C["pf_low"], C["pf_high"]), "F1, 25 A MINI",
        "at most %g s at %g A and over (its %g %% row)" % (C["mini_rows"][4][2], C["blade_a"] * C["mini_rows"][4][0] / 100.0, C["mini_rows"][4][0]),
        "the board P bands to the clamp (decision 28's copper)", "the clamp's short alone is cleared by the AFE's ASCD (R10 sees it, IF-6)", "printed (F1's 600 % row); disposition stated, no new defect")
    row("the shore input, Q7 shorted", "F1's envelope (not through board P)", "F1, 10 A MINI", "section 14.6", "J_DCIN, R19", "OVER", "DESIGN DEFECT DD-3 (L4-E11)")
    R["table"] = T
    # 6. defects, interfaces, evidence
    R["defects"] = [
        ("DD-1", "W4DP-F2: no firmware-independent element opens the discharge path with board P's FETs welded; the breaker of section 3 is drafted here, not drawn", "board P's generator with W4DP-F2's owner (the battery stream)"),
        ("DD-2", "the charger's battery FETs: TJ at most 150 C held at %.2f A from %.2f C, with the band (%.2f K) and R17 (%.2f W) in place; the pair would need (Zself + Zmut) at most %.2f K/W (%.2f K/W with R17 anywhere), so a third BUK6Y10-30P is selected: (Zself + 2 Zmut) at most %.2f K/W with R17 designed apart (%.2f K/W anywhere)" % (
            a, t0, dt_band, pr17, J[2]["apart"], J[2]["anywhere"], J[3]["apart"], J[3]["anywhere"]), "L4-E11 (E11-29 restated as the junction limit; Q41 and its land; E11-37 with three)"),
        ("DD-3", "R19 passes its 3 W and J_DCIN its VH rating inside F1's envelope on the shore input (section 14.6)", "L4-E11"),
        ("DD-4", "the Keystone 3568 holder prints no current rating", "Layer 6/7"),
        ("DD-5", "BAT-F20: with CHGIN = 1 above T3 the discharge runs through Q1's body diode, %.1f W at %.2f A held (VSD %g V at most), about %g W at 10 A" % (I["q12_vsd"] * a, a, I["q12_vsd"], I["batf20_w10"]),
         "the battery stream (BAT-F20, EQ-15)"),
        ("DD-6", "docking with the breaker on takes it past its SOA and VIN to SENSE's maximum (table); the make-last enable C-1b is drafted here, not drawn", "board P's generator with the battery stream (the UVLO circuit); board E's generator (J_SMB's fifth contact); Layer 7 with L4-E11 (the dock's make-last contact and its land on board A)"),
    ]
    R["interfaces"] = [
        ("IF-1", "board A's loads on VSYS stay off until the breaker's start ends (at most %.1f ms after the enable, plus the %.1f ms insertion), or follow its PGD" % (B["start_max"] * 1e3, B["t_ins"][1] * 1e3), "L4-E11 with board A's generator"),
        ("IF-2", "each breaker FET's installed RthJA at most %.1f C/W (the sheet prints %g on 1 in2 of 2 oz, %g on its least pad); two 1 in2 pads take %.0f mm2 of the %.0f mm2 left on the P2 placement's top face (%.0f mm2 a face, %.0f placed, %.0f the holes; the bottom face empty), leaving %.0f mm2 for the round 4 parts, the breaker's other parts and the bands where they do not lie in the pads (an area budget, not a floor plan; the FETs' drain pads are the breaker's input band); the controller beside RS, VIN's bypass at RS" % (
            B["rthja_need"], I["fet_rthja"], I["fet_rthja_min_cu"], B["p_pads"], B["p_free"], B["p_face"], I["p_courtyards"]["F"], I["p_holes"], B["p_free"] - B["p_pads"]), "board P's generator"),
        ("IF-3", "the energy chain: a stage for the breaker between PACK_FETS and PACK_LEAD (its limit %.2f A)" % a, "the energy chain's owner (the integrator)"),
        ("IF-4", "the gauge's OCD1/OCD2 stay the first level with working FETs; no setting changes", "the firmware owner"),
        ("IF-5", "the pack's terminal is live only while the enable is closed: a host other than the kit's dock closes it or gets a dead terminal (fail-safe); board A's pre-charge pin J_PRE1 and R1 are no longer exercised at docking; E11-30's docking waveform no longer arises with the breaker in place", "the battery stream (CONOPS); board A's generator; L4-E11"),
        ("IF-6", "the gauge's PACK and VCC taps stay on Q2's source node; the clamp and the controller return to PACK_N, so a clamp short passes R10 where the AFE sees it; the breaker's output becomes the terminal PACK_P with D1 on it (its %g A forward surge against the %.2f A the lead can carry at turn-off)" % (I["d1_ifsm"], B["icb_max"]), "board P's generator"),
    ]
    R["missing"] = [
        ("E-1", "the battery FETs' junction limit", "the coupon of L4-E11 section 17 with Q39 to Q41, the band carrying %.2f A and R17 dissipating in place" % a,
         "the hottest junction at most 150 C referred to %.2f C; R17's coupling into each junction at most %g K/W (heat R17 alone)" % (t0, R17_ALLOW), "the body diode's VSD method"),
        ("E-2", "the breaker's power limit at its design point", "six LM5069-2 on the board P specimen", "the shorted-output current at %.1f V and %.1f V within %.2f to %.2f A, at -40, 25 and 125 C (the table is printed at 48 V)" % (
            vmax, I["vmin"], B["plim_min"] / vmax, B["plim_max"] / vmax), "the supplier's bench, against Q-TI-L9S-1"),
        ("E-3", "the hot short and the enabled docking", "the board P specimen with Q1/Q2 bypassed, the 12 AWG lead, boards E and A as built, a charged block",
         "10 shorts and 100 dockings with the FETs' case at %.0f C: the gate low within %.1f us of VCB; the docking current at most %.3f A; VIN to SENSE recorded; VCL read back within %g to %g mV; each FET's RDS(on) within +5 %%" % (
             B["tc"], B["t_off_cb"] * 1e6, B["inrush_max"], I["vcl"][0] * 1e3, I["vcl"][2] * 1e3), "the supplier's fault bench"),
        ("E-4", "the dock contacts' split", "the four-pin set of the fitted lot", "the lowest pin resistance at least %.3f of the highest (at the blades' %g A; %.3f at the breaker's %.2f A)" % (
            CR["pin_ratio_need"], C["blade_a"], (a / C["pin_a"] - 1.0) / (C["pins"] - 1), a), "each pin at mid-stroke"),
        ("E-5", "the cells' parallel split", "each series group of the built block", "no cell over %g A at %.2f A: the groups share within %.2f %%; FALLBACK, named now: a controller whose limit spread with its sense is at most %.3f (for a %g %% split; the LM5069's is %.3f), the LM5066I of SLVA673A's examples, its sheet not held" % (
            I["cell_a"], a, 100 * B["split_max"], B["spread_need"], 100 * SPLIT_EXAMPLE, B["spread"]), "the pack builder; Layer 6 for the fallback's sheet"),
        ("E-6", "R17, R10 and the breaker's sense derated", "the makers' sheets", "each at its section 4 reading at the band's temperature", "Layer 6"),
        ("E-7", "the blades at the inside air", "the fitted lot in the 3568 holder", "the service, %g A for %g s after %g A held at %.2f C, without opening" % (service, C["kd_s"], cont, t0), "the supplier; Layer 6 reads the rerating curve"),
        ("E-8", "Q1/Q2's installed path and their own RDS(on) at temperature", "board P's first specimen; the CSD17570Q5B's Figure 8", "TJ under 150 C at %.2f A held from %.2f C, both enhanced" % (a, t0), "board P's generator; Layer 6"),
        ("E-9", "the breaker's actual current limit", "six board P specimens (the two paralleled shunts' traces and Kelvin taps as built)", "between %.2f and %.2f A at -40, 25 and 125 C at %.1f V and %.1f V (the window counts the parts' %.1f %% only, its top %.2f A under the cells' %g A)" % (
            B["icl_min"], a, I["vmin"], vmax, 100 * u, cells - a, cells), "the supplier's bench"),
        ("E-10", "the pack current at key-down", "board A and the transmitters at the %g A service" % service, "the instantaneous pack current under %.2f A, or excursions above it each under %.3f ms and under %.2f %% of the time (the timer's integration)" % (
            B["icl_min"], B["tf_min"] * 1e3, 100 * B["d_ratchet"]), "the supplier's bring-up bench"),
        ("E-11", "the breaker FETs' installed path", "the board P specimen", "RthJA at most %.1f C/W per FET by the body diode's VSD method" % B["rthja_need"], "the supplier"),
    ]
    R["questions"] = [
        ("Q-TI-L9S-1", "LM5069: the power limit's accuracy at VSNS %.2f mV, and every limit at VIN %.1f to %.1f V (the table is printed at 48 V); VIN to SENSE above its %g V maximum for the microseconds before the gate is low in a hot short (%.0f A on this sense)" % (
            B["vsns_pl"] * 1e3, I["vmin"], vmax, I["vin_sense_abs"], B["sense_abs_a"]), "drafted, not sent"),
        ("Q-TI-17", "L4-E11's question on the BATFET's %g nF, now with three FETs (%.2f nF typical at -15 V, about %.2f nF near 0 V)" % (I["ciss_ti"], J["ciss"][3][0], J["ciss"][3][1]), "L4-E11's, drafted, not sent"),
    ]
    R["not_taken"] = [
        "a limit whose largest is the pair's %.2f A: its least %.2f A falls under the %g A service" % (B["alt_icl_max"], B["alt_icl_min"], service),
        "a blade opening under the pair's current: at most %.2f A, and the service at %.0f %% of it lies between the row that holds and the row that opens" % (B["alt_blade"], B["alt_blade_pct"]),
        "for docking, an inrush element at board A's dock entry: the pre-charge pin J_PRE1 (%g ohm into %.0f uF, a %.2f ms time constant) needs a lead of %.1f ms over the power pins to keep the step under the breaker's least threshold and %.1f ms to keep VIN to SENSE under %g V, and a hand sets the lead; a series element in the %.2f A path heats beside the battery FETs, whose junction is the binding limit" % (
            I["r_pre"], cout * 1e6, tau * 1e3, B["pre"]["t_cb"] * 1e3, B["pre"]["t_abs"] * 1e3, I["vin_sense_abs"], a),
        "the pair kept at (Zself + Zmut) at most %.2f K/W with R17 apart: %.0f %% under E11-29's present %g K/W, which L4-E11 judged of the order a board pour gives; it stays the fallback if E11-37 refuses three FETs" % (
            J[2]["apart"], 100 * (1 - J[2]["apart"] / rth), rth),
        "a thermal trip on the battery FETs' copper (the kit's PRF15BB103 chip PTC, %g +-%g C at 47 kOhm, into the enable loop): with E11-29's present target the %g A service already reaches %.1f C, inside its band" % (
            I["ptc"][0], I["ptc"][1], service, J["ptc_service_pair"]),
        "a controller with a tighter limit tolerance now: the LM5066I of SLVA673A's examples, its sheet not held; it is E-5's fallback",
    ]
    # 7. the predicates
    pr = {}
    pr["no existing element opens below the pair's 150 C current without firmware, with the FETs welded"] = R["existing_floor"] > P["i150_air"]
    pr["a trip allowed at the cells' 24 A leaves Q39/Q40 over 150 C at 22 and 23 A held"] = all(x[2] > lim for x in P["exposure"][:2])
    pr["the sense lies in its window (largest limit at most the cells' current, least above the service)"] = B["rs_lo"] <= rs <= B["rs_hi"]
    pr["the breaker's largest actual limit is at most the cells' continuous current"] = a <= cells + 1e-9
    pr["the breaker's least actual limit is above the 18 A service"] = B["icl_min"] > service
    pr["the typical limit is at least 10 % above the service (SLVA673A)"] = B["icl_typ"] >= 1.1 * service
    pr["the power limit's sense voltage is at least the 5 mV floor at the pack's full voltage"] = B["vsns_pl"] >= I["vsns_min"] - 1e-12
    pr["a start never reaches the power limit or the current limit"] = B["start_p"] < B["plim_min"] and B["inrush_max"] < B["icl_min"]
    pr["the fault pulse is inside the derated SOA with TI's 1.5x margin"] = B["fault_ratio"] <= 1 / TI_MARGIN
    pr["the start is inside the derated SOA with TI's 1.5x margin"] = B["start_ratio"] <= 1 / TI_MARGIN
    pr["both stay within TI's margin with the figure's reading uncertainty taken against them"] = max(B["fault_ratio_low"], B["start_ratio_low"]) <= 1 / TI_MARGIN
    pr["the breaker FETs hold the largest held current under 125 C"] = B["tj_held"] < TI_STEADY_C
    pr["the FET's pulsed rating exceeds the breaker's threshold and the docking peak"] = I["fet_idm"] > max(B["icb_max"], C["dock_pk"])
    pr["the gate's 12.6 V is inside the FET's VGS rating"] = I["vgate"][1] < I["fet_vgs"]
    pr["the clamp stands off the pack, clamps under the FET's VDS and takes the breaker's current"] = (
        I["tvs"]["vr"] >= vmax and I["tvs"]["vc"] < I["fet_vds"] and I["tvs"]["ipp"] >= B["icb_max"])
    pr["the controller runs over the pack's range"] = I["vin_roc"][0] <= I["vmin"] and I["poren_max"] <= I["vmin"] and vmax <= I["vin_roc"][1]
    pr["the clamp is a part the kit already uses"] = I["tvs_on_a"]
    pr["a limit at the pair's 150 C current would fall under the service; a blade under it would not carry the service assuredly"] = (
        B["alt_icl_min"] < service and B["alt_blade_pct"] > C["mini_rows"][0][0])
    pr["without the power limit the fault pulse would pass the SOA (the limit is relied on)"] = B["cl_ratio"] > 1.0
    pr["docking with the breaker on passes the derated 10 us line and VIN to SENSE's maximum (B-P1 stands without C-1b)"] = (
        B["dock_uncorr"]["ratio"] > 1.0 and B["dock_uncorr"]["ratio75"] > 1.0 and B["dock_uncorr"]["vsense"] > I["vin_sense_abs"])
    pr["with the make-last enable a docking is a start: under the power limit, the current limit and VIN to SENSE's maximum"] = (
        B["start_p"] < B["plim_min"] and B["inrush_max"] < B["icl_min"] and B["dock_vsense"] < I["vin_sense_abs"])
    pr["the enable breaks before the power pins at a withdrawal under 2 m/s"] = B["v_withdraw"] > 2.0
    pr["the pre-charge pin needs a lead a hand does not bound (over 1 ms either way)"] = min(B["pre"]["t_cb"], B["pre"]["t_abs"]) > 1e-3
    pr["the pair cannot hold the junction limit at E11-29's present target"] = J[2]["apart"] < rth
    pr["three FETs hold it with R17 apart at a path above E11-29's present target"] = J[3]["apart"] > rth
    pr["three FETs exceed TI's 5 nF Ciss guidance (E11-37 decides)"] = J["ciss"][3][0] > I["ciss_ti"]
    pr["the 18 A service stays under 150 C at the selected allowances"] = J["tj_service"] < lim
    pr["the cells' admissible split at the largest limit is under 0.5 %"] = B["split_max"] < 0.005
    pr["the LM5069's spread is wider than a 5 % split allows (E-5's fallback is a tighter controller)"] = B["spread"] > B["spread_need"]
    pr["the precharge through a body diode stays under 150 C"] = B["pre_tj"] < I["fet_tj"]
    pr["D1's forward surge rating covers the lead's current at turn-off"] = B["d1_ratio"] < 1.0
    pr["the FETs' 1 in2 pads fit the P2 placement's free top face"] = B["p_pads"] < B["p_free"]
    pr["the installed RthJA the derating needs lies between the sheet's two printed boards"] = I["fet_rthja"] <= B["rthja_need"] < I["fet_rthja_min_cu"]
    R["pred"] = pr
    return R


def render(R):
    I, C, B, P, J = R["in"], R["cu"], R["B"], R["pair"], R["J"]
    L = []
    w = L.append
    w("l9stk_protection: W4DP-F2's firmware-independent element and the pack path's protection table (record l9stk, MESHSAT-1357;")
    w("revised 4 October 2026 after the recheck PROTECTION: NOT CONFIRMED, B-P1 docking and B-P2 the battery FETs' junction).")
    w("Desk arithmetic on committed files and makers' sheets; nothing was built, bought or measured. Calculation basis: TI SLVA673A")
    w("(Robust Hot Swap Design) equations 3 to 7, its 2.4 on parallel FETs and its 3.1.2.2, 3.1.2.5 and 3.2.2.7 checks, on the LM5069's sheet.")
    w("")
    w("0. PINS (path  sha256/16)")
    for k, (p, s) in sorted(R["pins"].items()):
        w("   %-16s %s  sha256 %s" % (k, p, s))
    w("")
    w("1. BOARD P'S EXISTING PROTECTION WITH ITS FETS WELDED")
    for name, what, verdict in R["existing"]:
        w("   %-46s %s: %s" % (name, what, verdict))
    w("   the lowest current any of them opens on its own is %.2f A, over the battery FETs' 150 C current below: none meets the" % R["existing_floor"])
    w("   criterion, so a minimal addition is designed (section 3)")
    w("")
    w("2. THE LIMITING SERIES PART: Q39/Q40, THE CHARGER'S BATTERY FETS ON BOARD A (L4-E11)")
    w("   RDS(on) %g mOhm each: L4-E11's bound at a 150 C junction from the sheet's printed maxima (the actual is lower at a lower junction)" % (P["each"] * 1e3))
    w("   installed (Zself + Zmut) %g K/W steady: E11-29's TARGET, not a measurement; with both FETs at the bound the even split" % P["rth"])
    w("   gives each FET the largest loss (SLVA673A 2.4 for enhanced FETs; a lower RDS(on) in one FET lowers its loss)")
    w("   150 C held at %.2f A from the +%g C line and %.2f A from %.2f C (L4-E12's E5 dwell without the hold), FETs only: DERIVED, not a rating" % (P["i150_air"], R["air"], P["i150_t0"], R["t0"]))
    w("   its uncertainty is the installed path's: with it %g %% lower, as targeted, %g %% higher:" % (100 * RTH_SPREAD, 100 * RTH_SPREAD))
    w("     " + "; ".join("x%.1f: %.2f A (+%g C), %.2f A (%.2f C)" % (f_, a_, R["air"], b_, R["t0"]) for f_, a_, b_ in P["spread"]))
    w("   the exposure a trip at the cells' %g A would leave, held: %s" % (R["cells"], "; ".join("%.2f A: TJ %.1f C (+%g C), %.1f C (%.2f C)" % (a_, x_, R["air"], y_, R["t0"]) for a_, x_, y_ in P["exposure"])))
    w("   so 'at or under 24 A' is not a protection criterion; the criterion is current AND time for every part (section 5)")
    w("")
    w("3. THE SELECTED ELEMENT: AN LM5069-2 BREAKER ON BOARD P, FROM Q2'S SOURCE TO PACK_P, ENABLED BY A MAKE-LAST DOCK CONTACT")
    w("   the controller board E's U6 already uses (LCSC %s) and the FET board A's PA stage already uses (LCSC %s): no new part family" % (I["u6_code"], I["fet_code"]))
    w("   sense RS: %s mOhm in parallel = %.4f mOhm, %g %% and %g ppm/K over %g K: +-%.1f %% (the parts only; the traces and Kelvin taps are E-9's)" % (
        " and ".join("%g" % x for x in RS_PARTS_MOHM), B["rs"] * 1e3, 100 * RS_TOL, RS_TCR * 1e6, RS_DT, 100 * B["u"]))
    w("     its window: %.4f to %.4f mOhm (the largest limit at most the cells' %g A, the least above the %g A service)" % (B["rs_lo"] * 1e3, B["rs_hi"] * 1e3, R["cells"], R["service"]))
    w("     current limit %.2f / %.2f / %.2f A (VCL %g to %g mV over TJ -40 to 125 C, printed at VIN 48 V); breaker %.2f to %.2f A (VCB %g to %g mV)" % (
        B["icl_min"], B["icl_typ"], B["icl_max"], I["vcl"][0] * 1e3, I["vcl"][2] * 1e3, B["icb_min"], B["icb_max"], I["vcb"][0] * 1e3, I["vcb"][2] * 1e3))
    w("     the limits are printed at VIN 48 V and used at %.1f to %.1f V (Q-TI-L9S-1, E-2, E-3, E-9); the shares: %s" % (I["vmin"], R["vmax"], "; ".join("%g mOhm %.1f %%" % (x, 100 * s_) for x, s_ in B["share"])))
    w("   power limit: RPWR %.0f ohm (equation 9 at VSNS %g mV and %.1f V, the next E96 value up): %.2f W nominal, VSNS %.2f mV" % (
        B["rpwr"], I["vsns_min"] * 1e3, R["vmax"], B["plim_nom"], B["vsns_pl"] * 1e3))
    w("     its spread: %.2f to %.2f W with the table's %g/%g/%g mV read as a ratio (the table prints it at 25 mV only); read as an offset, %.2f W" % (
        B["plim_min"], B["plim_max"], I["pwrlim"][0], I["pwrlim"][1], I["pwrlim"][2], B["plim_abs_max"]))
    w("     without the power limit the FET would see %.1f W (VIN x the largest limit): the limit is relied on (E-2, Q-TI-L9S-1)" % B["cl_bound_w"])
    w("   fault timer: %.0f nF (+-%g %%): %.3f to %.3f ms (VTMRH %g to %g V, %g to %g uA); insertion %.2f to %.2f ms (%g to %g uA)" % (B["ct"] * 1e9, 100 * CAP_TOL, B["tf_min"] * 1e3, B["tf_max"] * 1e3,
        I["vtmrh"][0], I["vtmrh"][1], I["itmr"][0] * 1e6, I["itmr"][1] * 1e6, B["t_ins"][0] * 1e3, B["t_ins"][1] * 1e3, I["iins"][0] * 1e6, I["iins"][1] * 1e6))
    w("   gate: %.0f nC to remove (%d x %g nC at 10 V scaled to %g V, and the dv/dt capacitor's swing); breaker release %.1f us (tCB %g us, %g mA);" % (
        B["q_off"] * 1e9, NFET, I["fet_qg"] * 1e9, I["vgate"][1], B["t_off_cb"] * 1e6, I["tcb_max"] * 1e6, I["isink_cb_min"] * 1e3))
    w("     after the timer or the enable's opening %.0f us (%g mA): clearing %.3f ms at most from the limit's onset (tCL %g us typical, no maximum printed)" % (
        B["t_off_timer"] * 1e6, I["isink_off_min"] * 1e3, B["clear_max"] * 1e3, I["tcl_typ"] * 1e6))
    w("   dv/dt start: %.0f nF (+-%g %%) into %.0f uF (VSYS's %.0f uF, CELL_FUSED's %.0f uF), gate %g to %g uA: inrush %.3f A at most, %.1f ms at most" % (
        B["cdv"] * 1e9, 100 * CAP_TOL, B["cout"] * 1e6, I["c_vsys"] * 1e6, I["c_cellfused"] * 1e6, I["igate"][0] * 1e6, I["igate"][1] * 1e6, B["inrush_max"], B["start_max"] * 1e3))
    w("     SLVA673A 3.2.2.7: %.1f W for %.1f ms equivalent, under the power limit's least %.1f W, so the timer never runs" % (B["start_p"], B["start_teq"] * 1e3, B["plim_min"]))
    w("   retry (-2): duty %.2f %% at most from the worst currents and thresholds (%.1f %% typical); dwell %.3f s at most; %.2f W average" % (
        100 * B["duty_max"], 100 * I["dc_retry_typ"], B["dwell_max"], B["retry_avg"]))
    w("   FETs: %d x CSD18510Q5B (%g V, VGS +-%g V, %g mOhm at 10 V, IDM %g A, junction %g C, RthJA %g C/W on 1 in2 2 oz, %g on its least pad, RthJC %g C/W)" % (
        NFET, I["fet_vds"], I["fet_vgs"], I["fet_rds"] * 1e3, I["fet_idm"], I["fet_tj"], I["fet_rthja"], I["fet_rthja_min_cu"], I["fet_rthjc"]))
    w("     held at %.2f A: %.3f W each at %.3f mOhm (Figure 8's x%g at 150 C); case %.1f C with both losses through one pad, junction %.1f C" % (
        B["icl_max"], B["p_each"], B["rds_hot"] * 1e3, I["rd"]["rdson_normalized_at_150c_vgs10"], B["tc_held"], B["tj_held"]))
    w("     retrying: case %.1f C; the case used for the derating %.1f C, factor %.3f (equation 5)" % (B["tc_retry"], B["tc"], B["derate"]))
    w("     SOA at %.1f V and 25 C (Figure 10 read at 300 dpi, +-%g %%): %s" % (R["vmax"], I["rd"]["uncertainty_pct"], "; ".join("%s %.0f W" % (k, v) for k, v in B["soa"].items())))
    w("     the fault pulse: %.2f W for %.3f ms against %.1f W derated: %.2f (TI asks %.2f at most); %.2f with the offset reading" % (
        B["plim_max"], B["clear_max"] * 1e3, B["fault_soa"], B["fault_ratio"], 1 / TI_MARGIN, B["fault_ratio_abs"]))
    w("     the start: %.1f W for %.1f ms against %.1f W derated (the DC line: no extrapolation past 10 ms): %.2f" % (B["start_p"], B["start_teq"] * 1e3, B["start_soa"], B["start_ratio"]))
    w("     with Figure 10 read %g %% high (the SOA %g %% lower): %.2f and %.2f; TI's margin holds up to an installed RthJA of %.1f C/W per FET" % (
        I["rd"]["uncertainty_pct"], I["rd"]["uncertainty_pct"], B["fault_ratio_low"], B["start_ratio_low"], B["rthja_need"]))
    w("     the 10 us line at %.1f V: %.1f A at 25 C; IDM %g A against the breaker's %.2f A (SLVA673A 3.1.2.2)" % (R["vmax"], B["i10us"], I["fet_idm"], B["icb_max"]))
    w("   input clamp: %s on VIN (VR %g V, VBR %g V least, VC %g V at %g A), the part on board A's VBAT; output: board P's D1 (SMBJ20A), %g A forward" % (
        TVS, I["tvs"]["vr"], I["tvs"]["vbr_min"], I["tvs"]["vc"], I["tvs"]["ipp"], I["d1_ifsm"]))
    w("     surge (8.3 ms) against the %.2f A the lead can carry when the gate turns off (LM5069 11.1.2 B): %.2f" % (B["icb_max"], B["d1_ratio"]))
    w("     VIN to SENSE's %g V maximum is passed above %.1f A, which only a hot short reaches before the gate is low (Q-TI-L9S-1, E-3)" % (I["vin_sense_abs"], B["sense_abs_a"]))
    w("   controller: VIN %g to %g V recommended, on from %g V at most; the pack %.1f to %.1f V; OVLO to ground; UVLO from VIN through the enable" % (
        I["vin_roc"][0], I["vin_roc"][1], I["poren_max"], I["vmin"], R["vmax"]))
    w("   the charge direction: the LM5069 limits no reverse current; a charge passes the FETs' channel while the breaker is on and their body")
    w("     diodes while it is off (VIN under POREN, or the enable open): the gauge's %g A precharge in one diode %.2f W (VSD %g V at most), TJ %.1f C" % (I["i_pre"], B["pre_w"], I["fet_vsd"], B["pre_tj"]))
    w("   not taken:")
    for x in R["not_taken"]:
        w("     - %s" % x)
    w("")
    w("3a. B-P1: DOCKING. Without a correction the breaker is on when the dock's power pins mate, so a docking reaches E11-30's %.1f A:" % C["dock_pk"])
    w("     VIN to SENSE %.3f V against the %g V maximum; the 10 us line at %.1f V derated to the %.1f C case is %.1f A (%.2f x over it), at a 75 C case %.2f x" % (
        B["dock_uncorr"]["vsense"], I["vin_sense_abs"], R["vmax"], B["tc"], B["dock_uncorr"]["i10_der"], B["dock_uncorr"]["ratio"], B["dock_uncorr"]["ratio75"]))
    w("   C-1b SELECTED: a make-last enable contact into UVLO (LM5069 11.1.1 and Figure 45). On board P a 2N7002 holds UVLO low unless the enable line")
    w("     is grounded; the line runs on a fifth J_SMB contact to board E and on to a dock contact %g mm short of the power pins that meets board A's" % D_EN_MM)
    w("     ground. Docking: the power pins mate with the breaker off; the enable mates; after the insertion time (%.2f to %.2f ms) a dv/dt start at" % (B["t_ins"][0] * 1e3, B["t_ins"][1] * 1e3))
    w("     %.3f A at most, VIN to SENSE %.2f mV. Undocking: the enable breaks first and the gate is off %.0f us later, before the pins part at any" % (B["inrush_max"], B["dock_vsense"] * 1e3, B["t_off_timer"] * 1e6))
    w("     withdrawal under %.2f m/s. An open line is off (fail-safe). The gauge's own FET turning on is also a start now: E11-30's waveform no longer arises" % B["v_withdraw"])
    w("   the alternative, an inrush element at board A's dock entry, is not taken (the not-taken list above): the pre-charge pin's lead time is the hand's")
    w("")
    w("4. B-P2: THE BATTERY FETS' JUNCTION LIMIT AND EVERY SERIES PART AT THE BREAKER'S LARGEST LIMIT, %.2f A, FROM %.2f C" % (B["icl_max"], R["t0"]))
    w("   the limit: the hottest battery FET's junction at most %g C held at %.2f A from %.2f C, the band carrying the current (%.2f K: 1 oz %.2f, 2 oz %.2f)" % (
        P["lim"], B["icl_max"], R["t0"], J["dt_band"], J["rise"]["1 oz"], J["rise"]["2 oz"]))
    w("     and R17 dissipating %.2f W in place; the budget for the FETs and R17's coupling is %.2f K" % (J["pr17"], J["budget"]))
    w("   R17's coupling into a junction is at most that FET's Zself (a passive network peaks where it is heated; reciprocity), so it is bounded with no layout")
    w("     known; designed apart it is held to %g K/W, which E-1 reads" % R17_ALLOW)
    for n_, lab in ((2, "the pair (Zself + Zmut)"), (3, "three (Zself + 2 Zmut)")):
        w("   %-34s %.3f W each: FETs only %.2f K/W; R17 apart %.2f K/W; R17 anywhere %.2f K/W" % (lab, J[n_]["p"], J[n_]["fet_only"], J[n_]["apart"], J[n_]["anywhere"]))
    w("   E11-29's present target is %g K/W; Ciss: the pair %.2f nF at -15 V and %.2f near 0 V, three %.2f and about %.2f, against TI's %g nF (L4-E11 16c, E11-37)" % (
        P["rth"], J["ciss"][2][0], J["ciss"][2][1], J["ciss"][3][0], J["ciss"][3][1], I["ciss_ti"]))
    w("   SELECTED: a third BUK6Y10-30P (Q41), R17 designed apart: the path asked is %.2f times E11-29's present target, where the pair would need %.2f" % (J["vs_target"], J[2]["apart"] / P["rth"]))
    w("     of it; its cost is Ciss over TI's guidance, which the pair also passes near 0 V: E11-37's bench with three decides, the pair is the fallback")
    w("   at the allowances: %.1f C at %g A, %.1f C at the %g A service, %.1f C at %.2f A" % (J["tj_cont"], R["cont"], J["tj_service"], R["service"], J["tj_held"], B["icl_max"]))
    for s_ in R["series"]:
        w("   %-62s %-58s %s  %s" % (s_["name"], s_["reading"], "[%.2f]" % s_["frac"] if s_["frac"] is not None else "[-]", s_["status"]))
    w("   the parts' fractions are of the printed rating, the battery FETs' of their 150 C rise, the breaker FETs' of TI's 125 C rise, the copper's of 10 K")
    w("")
    w("5. THE PROTECTION TABLE (case | current, duration | largest actual trip threshold | longest clearing time | limiting component | margin | evidence)")
    for r in R["table"]:
        w("   %s | %s | %s | %s | %s | %s | %s" % (r["case"], r["cur"], r["trip"], r["clear"], r["limiting"], r["margin"], r["status"]))
    w("   the supported envelope (once DD-1, DD-2, DD-5 and DD-6 close): %.1f A held and %.1f A for %g s from %.2f C with no trip on any unit;" % (
        R["cont"], R["service"], C["kd_s"], R["t0"]))
    w("   currents to %.2f A held on every unit; between %.2f and %.2f A a unit holds or clears by its own threshold; above %.2f A every unit" % (
        B["icl_min"], B["icl_min"], B["icl_max"], B["icl_max"]))
    w("   clears within %.2f ms of its limit's onset; a docking is a start; no firmware and no working FET of board P in that path" % (B["clear_max"] * 1e3))
    w("")
    w("6. DESIGN DEFECTS (unresolved, each with its owner)")
    for k, what, who in R["defects"]:
        w("   %s %s; owner %s" % (k, what, who))
    w("   INTERFACE DEMANDS")
    for k, what, who in R["interfaces"]:
        w("   %s %s; owner %s" % (k, what, who))
    w("   MISSING PHYSICAL EVIDENCE (specimen; acceptance; supplier task)")
    for k, what, spec, acc, task in R["missing"]:
        w("   %s %s: %s; %s; %s" % (k, what, spec, acc, task))
    w("   MAKER QUESTIONS")
    for k, what, st in R["questions"]:
        w("   %s %s (%s)" % (k, what, st))
    w("")
    w("7. PREDICATES")
    for k, v in R["pred"].items():
        w("   %-116s %s" % (k, "yes" if v else "NO"))
    return "\n".join(L) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 1 if [k for k, v in R["pred"].items() if not v] else 0


if __name__ == "__main__":
    sys.exit(main())
