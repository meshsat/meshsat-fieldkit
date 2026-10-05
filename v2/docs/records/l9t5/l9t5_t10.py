#!/usr/bin/env python3
"""l9t5_t10.py: Layer 9 record l9t5, task T10 (the owner's instruction of 4 October 2026, part 7; finding L9T5-F06, confirmed by
the collaborator's recheck V3): the three I/O supervisors' private 3.3 V regulators on board B (MESHSAT-1357). PROTOTYPE DESIGN:
nothing in this kit has been built, bought, powered or measured; no figure printed here is a measurement.

"Verify its applicable operating conditions and give it a named correction and acceptance criterion. Adding a dedicated ground
return does not address that separate deficit." It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256;
  2. THE APPLICABLE OPERATING STATE: what the contract, the panel page, the architecture, the generators and the firmware in the
     tree define for the supervisors (run mode, clock, voltage scale); what nothing defines;
  3. ST's printed rows for both silicon revisions the order code admits, each with its table, page and column;
  4. the junction temperature: the operating point of each printed state at L4-E12's inside air on the package's printed thermal
     resistance, solved against the table's own maxima (a state with no point at or under TJmax is not operable there);
  5. the auxiliaries' share (the CAN transceivers' printed supply currents against the declared 60 mA);
  6. the demand as a range, the bounded state to the worst nothing forbids;
  7. the regulator as drawn (AP2112K-3.3, SOT-25): its printed capability, dropout and THERMAL limit against that range;
  8. at most three corrections compared (a regulator per supervisor; a contract row; the supervisors fed differently), the
     selection (SESSION, with its reversal) and its ACCEPTANCE CRITERION as numbered conditions; Layer 5's row text;
  9. the selected circuit change drafted for boards A and B (apply_gen_sch_a_iocpre.py, apply_gen_sch_b_iocpre.py, after I-03's
     drafts): composed in L4-E9's order, regenerated, read in the netlist and the intent, mutated, and judged on C-DEV rev 1;
  10j (round 6, the check cx45's Q3): the quorum's schedule, the containment no firmware sets (apply_gen_sch_b_iocguard.py: a
     transmit-share limiter per transceiver and a rail trip per supervisor) composed, read and mutated, the surviving quorum per fault,
     the other supervisors' headroom, the thermal envelope with its qualification limits, and the rows on revision V and 14.0k;
 10. the state of L9T5-F06, the findings for other authors, and the predicates test_l9t5.py holds.
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_t10.py  (l9t5_t10.out is its output, regenerated with
_bin/regen_out.py after l9t5_drafts.out). Labels: PRINTED (a maker's limit), TYPICAL, DECLARED, MODEL, ASSUMPTION, SESSION."""
import hashlib
import importlib.util
import math
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import l9t5_drafts as D  # noqa: E402  (its compositions, netlists, sheets' figures and the case)
CHK = D.CHK

PRE = {b: os.path.join(HERE, "apply_gen_sch_%s_iocpre.py" % b) for b in "ab"}
SHEETS = {"h743": "v2/vendor/st/st-stm32h743xi-datasheet.pdf", "ap2112": "v2/vendor/diodes/diodes-ap2112-ldo.pdf",
          "ap632": "v2/vendor/diodes/diodes-ap63200-series-buck.pdf", "tcan": "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf",
          "tps62933": "v2/vendor/ti/ti-tps62933.pdf", "rm0433": "v2/vendor/st/st-rm0433-rev8.pdf",
          # T10 round 6 (cx45 Q3): both held back (v2/docs/records/l4e7/fetch_held_back.py), the kit's parts already (L4-E7's backstop)
          "ina169": "v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "tps3701": "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf"}
DOCS = {"contract": "v2/docs/HW-FW-CONTRACT.md", "panel": "v2/docs/PANEL.md", "arch": "v2/docs/ARCH-PCB-B-IOHA.md", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "l4e12": "v2/docs/records/l4e12/l4e12_thermal.out", "rvpwr": "v2/docs/records/rv-pwr/pwr_budget.py", "gndret": "v2/docs/records/l8r2/l8r2_gndret.out",
        "drafts": "v2/docs/records/l9t5/l9t5_drafts.py", "drafts_out": "v2/docs/records/l9t5/l9t5_drafts.out",
        "pre_a": "v2/docs/records/l9t5/apply_gen_sch_a_iocpre.py", "pre_b": "v2/docs/records/l9t5/apply_gen_sch_b_iocpre.py",
        "trace": "v2/docs/REQUIREMENTS-TRACE.md", "shdn": "v2/docs/records/l9t5/apply_gen_sch_b_canshdn.py",
        "contract_draft": "v2/docs/records/l9t5/apply_hw_fw_contract_t10.py", "cdev2": "v2/docs/records/l9t5/inputs/cases-cdev-rev2-20261005.md",
        "set_a": "v2/docs/records/l9t5/apply_gen_sch_a_iocset.py", "set_b": "v2/docs/records/l9t5/apply_gen_sch_b_iocset.py",
        "guard_b": "v2/docs/records/l9t5/apply_gen_sch_b_iocguard.py"}
# the session's choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
TJ_GOAL = 125.0            # C: the junction this record holds each LDO to at the inside air (25 K under the sheet's 150 C absolute maximum)
BOUND = ("VOS3", 144)      # the state the proposed contract row bounds each supervisor to: voltage scale 3, HCLK at most 144 MHz, the
                           # least printed VOS3 row over the 64 MHz the controller is taken to start at from its HSI (ASSUMPTION: ST's
                           # reference manual RM0433 is not held; the contract already says so). A bound its own reset state broke
                           # would be no bound
ETA_K1 = 0.88              # the per-supervisor buck's efficiency in option K1: board B's own declaration for the same part (U25), NOT PLOTTED at 5 V in
R601, R602_OLD = 56.2e3, 10.7e3


def refuse(msg):
    sys.stderr.write("l9t5_t10: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def sha(relpath, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, relpath), "rb").read()).hexdigest()[:n]


def text(relpath):
    return open(os.path.join(ROOT, relpath), encoding="utf-8").read()


_PDF = {}


def pdf(key):
    if key not in _PDF:
        try:
            r = subprocess.run(["pdftotext", "-layout", os.path.join(ROOT, SHEETS[key]), "-"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError) as e:
            refuse("pdftotext could not read %s (%s)" % (SHEETS[key], e))
        _PDF[key] = r.stdout.decode("utf-8", "replace")
    return _PDF[key]


ROW = re.compile(r"(\d{2,3})\s+(\d+(?:\.\d+)?)\s+(\d+)(?:\(3\))?\s+(\d+)\s+(\d+)(?:\(3\))?\s+(\d+|-)\s*(?:mA)?\s*$")
VOS = {"Y": {400: "VOS1", 300: "VOS2", 216: "VOS2"}, "V": {480: "VOS0", 400: "VOS1", 300: "VOS2", 216: "VOS2"}}


def run_table(t, head, what):
    """{('off'|'on', MHz): (typ, max25, max85, max105, max125 or None)} mA, from one run-mode table: the rows that print maxima, in
    the table's order; the 'all peripherals enabled' group starts where the frequency rises again."""
    blk = need(t, head + r"(.*?)\n\s*1\. Data are in DTCM", what, re.S).group(1)
    rows, grp, last = {}, "off", None
    for line in blk.splitlines():
        m = ROW.search(line)
        if not m:
            continue
        f = int(m.group(1))
        if last is not None and f > last:
            grp = "on"
        last = f
        rows[(grp, f)] = (float(m.group(2)),) + tuple(float(x) for x in m.groups()[2:5]) + ((float(m.group(6)),) if m.group(6) != "-" else (None,))
    return rows


def figures():
    P = {}
    t = pdf("h743")
    need(t, r"DS12110 Rev 10", "the H743 sheet's revision")
    P["Y"] = run_table(t, r"Table 30\. Typical and maximum current consumption in Run mode, code with data processing\s*\n\s*running from ITCM, regulator ON\(1\)", "Table 30 (rev Y)")
    P["V"] = run_table(t, r"Table 129\. Typical and maximum current consumption in Run mode, code with data processing\s*\n\s*running from ITCM, LDO regulator ON\(1\)", "Table 129 (rev V)")
    for rev, n in (("Y", 12), ("V", 14)):
        if len(P[rev]) != n or ("on", 400) not in P[rev] or ("off", 25) not in P[rev] or ("off", 60) not in P[rev]:
            refuse("the rev %s run-mode table no longer reads as %d rows with maxima" % (rev, n))
    need(t, r"2\. Guarantee[d] by characterization results", "the maxima's basis (characterization)")
    P["theta_mcu"] = float(need(t, r"Thermal resistance junction-ambient\s*\n\s*([\d.]+)\s*\n\s*LQFP100 - 14 x 14 mm /0\.5 mm pitch", "the LQFP100's junction to ambient").group(1))
    P["tj_mcu"] = float(need(t, r"TJ\s+Maximum junction temperature\s+(\d+)", "the H743's maximum junction").group(1))
    P["ta_mcu"] = float(need(t, r"Ambient temperature for the suffix 6\s+Maximum power dissipation\s+\S40\s+(\d+)", "the suffix 6 ambient at maximum dissipation").group(1))
    m = need(t, r"Standard operating voltage\s+-\s+([\d.]+)\s+([\d.]+)", "the H743's VDD range")
    P["vdd"] = (float(m.group(1)), float(m.group(2)))
    need(t, r"5\. TJmax = 105 .C\.", "VOS0's junction limit")
    t = pdf("ap2112")
    P["ap_rev"] = need(t, r"Document number: (DS39724 Rev\. 2 - 2)", "the AP2112 sheet's number").group(1)
    P["theta_ldo"] = float(need(t, r"SOT25\s+(\d+)\s*\n\s*\S+\s+Thermal Resistance \(Junction to Ambient\)\(No Heatsink\)", "the SOT25's junction to ambient").group(1))
    P["tj_ldo"] = float(need(t, r"Operating Junction Temperature Range\s+\+(\d+)", "the AP2112's junction (absolute maximum)").group(1))
    P["tsd"] = float(need(t, r"Thermal Shutdown Temperature\s+\S\s+\S\s+\+(\d+)", "the thermal shutdown (typical)").group(1))
    P["ta_ldo"] = float(need(t, r"Ambient Operation Temperature Range\s+-40\s+\+(\d+)", "the AP2112's ambient range").group(1))
    sec = need(t, r"AP2112-3\.3 Electrical Characteristics.*?ISHORT\s+Short Current Limit\s+VOUT = 0V\s+\S\s+(\d+)", "the AP2112-3.3 table", re.S)
    P["ishort"] = float(sec.group(1)) / 1000.0
    sec = sec.group(0)
    P["imax"] = float(need(sec, r"IOUT\(MAX\)\s+Maximum Output Current\s+VIN = 4\.3V, VOUT = [\d.]+V to [\d.]+V\s+(\d+)", "IOUT(MAX)").group(1)) / 1000.0
    m_vo = need(sec, r"VOUT\s+VOUT\s*\n.*?\n.*?\*([\d.]+)%\s+\*([\d.]+)%", "VOUT's band", re.S)
    P["vout_hi"] = float(m_vo.group(2)) / 100.0
    P["vout_lo"] = float(m_vo.group(1)) / 100.0      # round 5 (part 21): the LDO's least output, the corner of its largest drop
    P["load"] = float(need(sec, r"Load Regulation\s+VIN = 4\.3V, 1mA \S IOUT \S 600mA\s+-1\s+0\.2\s+([\d.]+)\s+%/A", "the load regulation maximum").group(1)) / 100.0
    P["drop"] = {i: float(need(sec, r"IOUT = %dmA\s+\S\s+\d+\s+(\d+)" % i, "the dropout at %d mA" % i).group(1)) / 1000.0 for i in (10, 300, 600)}
    need(sec, r"Line Regulation\s+4\.3V\S VIN \S 6V, IOUT = 30mA", "the line regulation's range (from 4.3 V)")
    m = need(t, r"VIN\s+Supply Voltage\s+([\d.]+)\s+([\d.]+)\s+V", "the AP2112's supply range")
    P["vin"] = (float(m.group(1)), float(m.group(2)))
    t = pdf("ap632")
    P["k1_rev"] = need(t, r"Document number: (DS41326 Rev\. 3 - 2)", "the AP63200 series sheet's number").group(1)
    P["k1_a"] = float(need(t, r"(\d)A Continuous Output Current", "the AP6320x's rating").group(1))
    P["k1_theta"] = float(need(t, r"Junction to Ambient\s+TSOT26\s+(\d+)", "the TSOT26's junction to ambient").group(1))
    m = need(t, r"VIN\s+Supply Voltage\s+([\d.]+)\s+(\d+)\s+V", "the AP6320x's supply range")
    P["k1_vin"] = (float(m.group(1)), float(m.group(2)))
    P["k1_tj"] = float(need(t, r"TJ\s+Junction Temperature\s+\+(\d+)", "the AP6320x's junction (absolute maximum)").group(1))
    P["k1_eff_5v"] = bool(re.search(r"Efficiency vs\. Output Current, VIN = 5V", t))
    t = pdf("tcan")
    need(t, r"SLLSEQ7F", "the TCAN334 sheet's number")
    P["can_dom"] = float(need(t, r"CL = open, S, STB and SHDN = 0V\.\s+(\d+)\s*\n\s*Typical Bus Load", "ICC dominant, typical bus load").group(1)) / 1000.0
    P["can_dom_hi"] = float(need(t, r"CL = open, S, STB and SHDN = 0V\.\s+(\d+)\s*\n\s*Supply current Normal Mode\s+High Bus Load", "ICC dominant, high bus load").group(1)) / 1000.0
    P["can_fault"] = float(need(t, r"SHDN = 0V, CANH = -12V, RL = open,\s+(\d+)", "ICC dominant with a bus fault").group(1)) / 1000.0
    P["can_rec"] = float(need(t, r"ICC\s+Recessive\s+([\d.]+)\s*$", "ICC recessive").group(1)) / 1000.0
    # the bus-fault row is the current while the driver is DOMINANT into the fault (TXD = 0 V), and the driver's dominant time-out
    # ends only a held TXD (5.7 and note 1; 6.3.7: the dominant share is limited by that time-out and the protocol)
    need(t, r"TXD = 0V, S, STB and\s+mA\s+Dominant with\s+SHDN = 0V, CANH = -12V, RL = open,\s+180", "the bus-fault row's condition (TXD = 0 V)")
    P["can_dto"] = tuple(float(x) for x in need(t, r"tTXD_DTO\s+Driver dominant time out \(1\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+ms",
                                                  "the driver dominant time-out").groups())
    need(t, r"percentage dominant is limited by the TXD dominant time out and CAN\s+protocol", "6.3.7's dominant share")
    t = pdf("tps62933")
    need(t, r"0\.8-V to 22-V output voltage range", "the TPS62933's output range")
    m = need(t, r"500\s+(4\.7)\s+40\s+15\s*\n\s*3\.3\s+31\.3\s+10\.0.*?500\s+(6\.8)\s+20\s+10\s*\n\s*5\s+52\.5\s+10\.0", "Table 10-2's 3.3 V and 5 V rows", re.S)
    P["tps_l"] = (float(m.group(1)), float(m.group(2)))
    # the tree's own texts
    m = need(text(DOCS["l4e12"]), r"E5\s+ambient 60\.0 C; mixed air ([\d.]+) C; in the exhaust ([\d.]+) C", "L4-E12's inside air at E5")
    P["air"], P["air_exhaust"] = float(m.group(1)), float(m.group(2))
    gb = text(DOCS["gen_b"])
    m = need(gb, r'_intent\.rail\("\+3V3_IOC%s" % _t, 3\.3, ([\d.]+), ([\d.]+), _u', "board B's +3V3_IOCx declaration")
    P["decl"] = (float(m.group(1)), float(m.group(2)))
    m = need(gb, r'loads=dict\(\[\(_n\[0\], ([\d.]+)\), \(_n\[1\], ([\d.]+)\), \(_n\[2\], ([\d.]+)\), \(_n\[3\], ([\d.]+)\)\]\)', "board B's +3V3_IOCx loads")
    P["decl_loads"] = tuple(float(x) for x in m.groups())
    need(gb, r'"25 MHz 3225 \(CAN-FD bit timing needs a crystal, not the HSI\)"', "the supervisors' crystal")
    need(gb, r'"TCAN334D CAN-FD transceiver, controller %s on heartbeat fabric %s"', "the supervisors' transceivers")
    c = text(DOCS["contract"])
    rows = [l for l in c.splitlines() if l.startswith("|") and re.search(r"supervisor", l, re.I)]
    P["contract_rows"] = len(rows)
    P["contract_bound"] = [l[:60] for l in rows if re.search(r"\bVOS\d?\b|\bHCLK\b|run mode|voltage scal|\b\d+ MHz\b", l, re.I)]
    need(c, r"three I/O supervisors \| B, U41, U51, U61 STM32H743VIT6 \| a private AP2112K 3\.3 V each", "the contract's supervisor row")
    P["panel_bound"] = [l[:60] for l in text(DOCS["panel"]).splitlines() if re.search(r"supervisor", l, re.I) and re.search(r"\bVOS\d?\b|\bHCLK\b|run mode", l, re.I)]
    P["arch"] = " ".join(need(text(DOCS["arch"]), r"(roughly 60 mA each at 3\.3 V with the\s+core clocked to what CAN-FD timing needs, not to 480 MHz)", "the architecture's intent").group(1).split())
    # round 5 (V6-B3): the requirement that covers the fabric faults, read where it is written: CON-004 in the trace, rows 7 and 8 of
    # the architecture's FMEA (section 12) and its test A7 (section 13)
    tr = text(DOCS["trace"])
    m = need(tr, r"^\| CON-004 \| (constraint) \| (core) \| DEFINED \|[^\n]*\| (BLOCKER) \|$", "CON-004's row in the trace's table")
    P["con004_class"] = m.groups()
    P["con004"] = need(tr, r"^\*\*CON-004\*\* \(constraint\)\. (.*?)$", "CON-004's statement").group(1)
    P["con004_acc"] = need(tr, r"\*\*CON-004\*\* \(constraint\)\..*?\n\n\*Accept when:\* (.*?)$", "CON-004's acceptance", re.M | re.S).group(1)
    P["con004_alloc"] = need(tr, r"\*\*CON-004\*\* \(constraint\)\..*?\n\n\*allocated to ([^;]*);", "CON-004's allocation", re.M | re.S).group(1)
    at = text(DOCS["arch"])
    P["row7"] = need(at, r"^\| 7 \| (One CAN fabric breaks or a transceiver fails dominant) \| n/a \| ([^|]*?) \| ([^|]*?) \|", "IOHA FMEA row 7").groups()
    P["row8"] = need(at, r"^\| 8 \| (Both CAN fabrics break) \| n/a \| ([^|]*?) \| ([^|]*?) \|", "IOHA FMEA row 8").groups()
    P["a7"] = need(at, r"^\| A7 \| (Heartbeat fabric break) \| ([^|]*?) \| ([^|]*?) \|$", "IOHA test A7").groups()
    need(at, r"Every row is a failure this design is supposed to survive or is knowingly exposed to", "section 12's scope sentence")
    fw = os.path.join(ROOT, "v2", "firmware")
    P["fw"] = sorted(os.listdir(fw)) if os.path.isdir(fw) else []
    m = need(text(DOCS["rvpwr"]), r"3 \* \(([\d.]+) \+ 0\.06\) \* 3\.3, 3 \* \(([\d.]+) \+ 0\.06\) \* 3\.3, 3 \* \(([\d.]+) \+ 0\.06\) \* 3\.3", "rv-pwr's three supervisor figures")
    P["rv"] = tuple(float(x) for x in m.groups())
    return P


def interp(row, tj):
    """the table's maximum (A) at a junction temperature: linear between its printed columns at 25, 85, 105 and 125 C (MODEL)."""
    pts = [(25.0, row[1]), (85.0, row[2]), (105.0, row[3])] + ([(125.0, row[4])] if row[4] is not None else [])
    for (t0, i0), (t1, i1) in zip(pts, pts[1:]):
        if tj <= t1:
            return (i0 + (i1 - i0) * (max(tj, t0) - t0) / (t1 - t0)) / 1000.0
    return None


def point(row, air, theta, tj_max, vdd=3.3):
    """the operating point TJ = air + theta x VDD x Imax(TJ) on the table's maxima, or None when none exists at or under tj_max."""
    top = min(tj_max, 125.0 if row[4] is not None else 105.0)
    lo_, hi_ = air, top

    def g(tj):
        return air + theta * vdd * interp(row, tj) - tj
    if g(hi_) > 0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo_ + hi_)
        if g(mid) > 0:
            lo_ = mid
        else:
            hi_ = mid
    return hi_, interp(row, hi_)


# ------------------------------------------------------------------------------------------------ round 5 (5 October 2026)
# the session's round-5 choices (SESSION under the owner's standing rule of 26 September 2026), each printed with its reason
SHARE = 0.02             # each supervisor's own TXD dominant share on a fabric, at most, over every WINDOW (FW-B21): about 20 classic
                         # frames per 100 ms at 1 Mbit/s, many times what a 2-of-3 heartbeat needs
WINDOW_MS = 100          # the window the share is held over (short against any package's thermal time constant: none printed)
PROBE_S, PROBE_MS = 1.0, 100   # a stopped fabric is probed no more than once a second, for at most 100 ms
F_TX_MHZ, C_IO_PF = 1.0, 20.0  # the two FDCAN TX pins' toggle rate (1 Mbit/s at most, FW-B09) and their ASSUMED load each
R_TOL = 0.01             # every resistor of the generator taken at 1 % (ASSUMPTION: the value strings carry no tolerance)
SHDN = os.path.join(HERE, "apply_gen_sch_b_canshdn.py")
CONTRACT = os.path.join(HERE, "apply_hw_fw_contract_t10.py")
RM = SHEETS["rm0433"]
SUBSET = ("FDCAN registers", "FDCAN kernel", "I2C1 registers", "I2C1 kernel", "GPIOA", "GPIOB", "GPIOC", "GPIOD", "GPIOE", "GPIOH", "SYSCFG")
TWICE = ("FDCAN registers", "FDCAN kernel")   # one clock enable serves both instances; counted twice, a margin for their activity


def flat_(s):
    return " ".join(s.split())


def rm_page(p):
    try:
        r = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), os.path.join(ROOT, RM), "-"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("pdftotext could not read %s page %d (%s)" % (RM, p, e))
    t = r.stdout.decode("utf-8", "replace")
    if not re.search(r"\b%d/3353\b" % p, t):
        refuse("RM0433 page %d does not carry its own page number" % p)
    return flat_(t)


def figures5(P):
    """round 5's figures: the enabled peripherals (Table 39, rev Y; Table 137, rev V), the HSE and LSI, the TCAN334's fault rows and
    modes, the reference manual's reset state and FDCAN behaviour, CON-017."""
    t = pdf("h743")
    Q = {}
    for rev, head, end, ncol in (("Y", r"\n\s*Table 39\. Peripheral current consumption in Run mode\s*\n", r"\n\s*Table 40\. Peripheral current consumption in Stop", 3),
                                 ("V", r"\n\s*Table 137\. Peripheral current consumption in Run mode\s*\n", r"\n\s*Table 138\. Low-power mode wakeup timings", 4)):
        blk = need(t, head + r"(.*?)" + end, "the peripheral table of rev %s" % rev, re.S).group(1)
        s = {}
        for name in SUBSET:
            m = need(blk, r"^(?:\s*[A-Z][A-Z0-9]*)?\s+%s\s+((?:[\d.]+\s+){%d}[\d.]+)(?:\s+\S*/MHz)?\s*$" % (re.escape(name), ncol - 1),
                     "%s in the rev %s peripheral table" % (name, rev))
            s[name] = float(m.group(1).split()[-1])          # the last column is VOS3
        Q["S_" + rev] = s
        Q["s_" + rev] = sum(v * (2 if k in TWICE else 1) for k, v in s.items())
    need(t, r"frcc_c_ck = 200 MHz \(Scale 3\)", "the peripheral table's VOS3 condition")
    need(t, r"fPCLK = frcc_c_ck/4, and fHCLK = frcc_c_ck/2", "the peripheral table's bus clocks")
    hse = [float(x) for x in re.findall(r"-\s+([\d.]+)\s+-\s*\n\s*CL=10 pF at 32 MHz", t)]
    if len(hse) != 2:
        refuse("the HSE's 32 MHz consumption row is not read in both revisions' tables")
    Q["hse"] = max(hse) / 1000.0
    lsi = [float(x) for x in re.findall(r"IDD\(LSI\)\(\d\)[^\n]*?-\s+-\s+(\d+)\s+(\d+)\s+nA", t) for x in [x[1]]]
    if not lsi:
        refuse("the LSI's consumption is not read")
    Q["lsi"] = max(lsi) * 1e-9
    m = need(t, r"fHSI\s+HSI frequency\s+VDD=3\.3 V, TJ=30 .C\s+[\d.]+\(2\)\s+(\d+)\s", "the HSI's frequency")
    Q["hsi"] = float(m.group(1))
    c = pdf("tcan")
    Q["ios_dom"] = float(need(c, r"V\(CANL\) = 12V, CANH =\s+(\d+)\s+open, TXD = 0V", "IOS(DOM) at CANL 12 V").group(1)) / 1000.0
    Q["ios_rec"] = float(need(c, r"Short-circuit steady-state output current, Recessive\s+\S+\s+(\d+)\s+mA", "IOS(REC)").group(1)) / 1000.0
    Q["vod_canh_min"] = float(need(c, r"CANH\s+See Figure 6-3 and Figure 6-2, TXD =\s+([\d.]+)\s+VCC", "VO(D) CANH's minimum").group(1))
    Q["vod_canl_max"] = float(need(c, r"CANL\s+CL = open\s+[\d.]+\s+([\d.]+)", "VO(D) CANL's maximum").group(1))
    Q["vit_max"] = float(need(c, r"^\s*VIT\s+(\d+)\s+(\d+)\s*$", "the receiver's threshold").group(2)) / 1000.0
    Q["icc_shdn"] = float(need(c, r"SHDN = VCC, RXD floating, TXD at VCC\s+([\d.]+)", "ICC in shutdown").group(1)) * 1e-6
    Q["vbus_abs"] = float(need(c, r"Voltage at any bus terminal \(CANH or CANL\), V\(BUS\)\s+\S+\s+(\d+)\s+V", "the bus pins' absolute maximum").group(1))
    need(c, r"HIGH\s+Lowest Current\s+Disabled \(OFF\)\(2\)\s+Disabled \(OFF\)", "Table 6-5, SHDN high: driver and receiver off")
    need(c, r"The internal bias should not be relied on by design", "6.3.6 on the internal pull-downs")
    need(c, r"SHDN\s+5\s+.\s+5\s+.\s+I\s+Drive high for shutdown mode\. Internal pull-down\.", "the TCAN334's pin 5 (SHDN)")
    # the reference manual, held since 27 September 2026 (T10-A1 round 4 took it as not held)
    Q["rm_vos"] = need(rm_page(279), r"After reset, the system starts on the lowest Run mode voltage scaling \(VOS3\)", "RM0433 p.279").group(0)
    Q["rm_hsi"] = need(rm_page(349), r"After a system reset, the HSI is selected as system clock and all PLLs are switched OFF", "RM0433 p.349").group(0)
    Q["rm_init"] = need(rm_page(2464), r"or by going Bus_Off\. While INIT bit in FDCAN_CCCR register is set, message transfer from and to the CAN bus is "
                                        r"stopped, the status of the CAN bus output FDCAN_TX is recessive \(high\)", "RM0433 p.2464").group(0)
    Q["rm_dar"] = need(rm_page(2470), r"the automatic retransmission may be disabled via FDCAN_CCCR\.DAR", "RM0433 p.2470").group(0)
    need(rm_page(2470), r"In DAR mode all transmissions are automatically canceled after they started on the CAN bus", "RM0433 p.2470, DAR mode")
    need(rm_page(2527), r"Bit 6 DAR: Disable automatic retransmission", "RM0433 p.2527")
    Q["rm_bo"] = need(rm_page(2534), r"If the device goes Bus_Off, it sets FDCAN_CCCR\.INIT of its own, stopping all bus activities\. Once "
                                      r"FDCAN_CCCR\.INIT has been cleared by the CPU, the device waits for 129 occurrences of bus Idle", "RM0433 p.2534").group(0)
    tr = text(DOCS["trace"])
    Q["c17_5"] = need(tr, r"\(5\) the fitted supervisors are silicon revision V or X", "CON-017 (5)").group(0)
    Q["c17_4"] = need(tr, r"\(4\) the supervisor firmware builds for the STM32H743 and refuses to run both FDCAN fabrics on revision Y or W", "CON-017 (4)").group(0)
    gb = text(DOCS["gen_b"])
    if len(re.findall(r'r\("R(?:47[0-3]|50[4-7])", "60R4 1%"', gb)) != 8:
        refuse("the two split terminations of each fabric are not eight 60R4 1% resistors")
    Q["rl_min"] = 2 * 60.4 * (1 - 0.01) / 2.0       # two ends of 2 x 60R4 in parallel, each at -1 %
    need(gb, r'"5": "NC", "6": "CANL_%s%s" % \(_f, _seg\)', "the transceivers' pin 5 on no net (as drawn)")
    need(gb, r'"8": "GND"\}, "C2871143"\)', "the transceivers' STB (pin 8) on GND")
    return Q


def kfac(P, rev, tj):
    """the printed maxima's ratio to the typical for the whole peripheral set (all enabled less all disabled, VOS3 200 MHz, the run
    table of that revision), interpolated on the junction (MODEL; applied to the subset as an ASSUMPTION)."""
    on, off = P[rev][("on", 200)], P[rev][("off", 200)]
    ks = [(on[i + 1] - off[i + 1]) / (on[0] - off[0]) for i in range(4)]
    pts = list(zip((25.0, 85.0, 105.0, 125.0), ks))
    for (t0, k0), (t1, k1) in zip(pts, pts[1:]):
        if tj <= t1:
            return k0 + (k1 - k0) * (max(tj, t0) - t0) / (t1 - t0)
    return ks[-1]


def mcu_i(P, Q, rev, tj):
    """a controller's supply at its junction in the bounded state: the disabled row at 144 MHz, the enabled subset (per MHz times the
    144 MHz CPU clock, an upper bound for every bus or kernel clock at or under it, times the family's max to typical ratio), the
    HSE (TYPICAL, at 32 MHz), the LSI (its maximum) and the two TX pins' switching (ISW = VDD f C, ASSUMED 20 pF)."""
    row = interp(P[rev][("off", BOUND[1])], tj)
    if row is None:
        return None
    per = Q["s_" + rev] * BOUND[1] * 1e-6 * kfac(P, rev, tj)
    io = 2 * 3.3 * F_TX_MHZ * 1e6 * C_IO_PF * 1e-12
    return row + per + Q["hse"] + Q["lsi"] + io


def mcu_point(P, Q, rev, air):
    lo_, hi_ = air, P["tj_mcu"]

    def g(tj):
        return air + P["theta_mcu"] * 3.3 * mcu_i(P, Q, rev, tj) - tj
    if g(hi_) > 0:
        return None
    for _ in range(80):
        mid = 0.5 * (lo_ + hi_)
        if g(mid) > 0:
            lo_ = mid
        else:
            hi_ = mid
    return hi_, mcu_i(P, Q, rev, hi_)


def aux_from_netlist(nl, tag, vmax):
    """a controller's other loads on its own 3.3 V, from the composed netlist: every resistor from the rail to another net, and every
    resistor from a net on one of the controller's pins to GND (driven high, it draws V/R from the rail), each at VMAX over its value
    less R_TOL. The controller's VDD and its two transceivers are counted apart."""
    v33, u = "+3V3_IOC%s" % tag, {"A": "U41", "B": "U51", "C": "U61"}[tag]
    skip = {v33, "GND", "IOC%s_VCAP" % tag, "IOC%s_XI" % tag, "IOC%s_XO" % tag}
    pins = {n for n in nl["pins"][u].values() if n not in skip}
    got = []
    for ref, d_ in sorted(nl["pins"].items()):
        if not re.fullmatch(r"R\d+", ref) or len(d_) != 2:
            continue
        a, b = sorted(d_.values())
        if (v33 in (a, b) and a != b) or ({a, b} & pins and "GND" in (a, b)):
            r_ = CHK.kohm(CHK.value(nl, ref))
            got.append((ref, CHK.value(nl, ref), vmax / (r_ * (1 - R_TOL))))
    return got


def round5(w, P, DP, air, hi3, d_bound):
    Q = figures5(P)
    # round 5 (part 21, (1)): the LDO's drop at its WORST corner, the pre-regulator's top less the LDO's least output (98.5 %, PRINTED);
    # round 4 took the nominal 3.3 V. The drop falls as the output rises faster than the controller's current does, so the least output
    # is the corner of the largest dissipation; the run tables' currents are kept at their 3.3 V figures (not scaled down: conservative)
    ldo_k = P["theta_ldo"] * (hi3 - 3.3 * P["vout_lo"])

    def tj_l(i, a=air):
        return a + ldo_k * i
    out = {"Q": Q}
    w("10. ROUND 5 (5 October 2026): THE INDEPENDENT CHECK V6's ITEM C AND V6-B3; T10-A1's ROW, F13, F16 AND F17 WITH THEIR RESPONSES")
    w("   V6 (an AI review of candidate 7a82e82a) read T10 CONFIRMED AS CONDITIONAL, not on T10-A1 alone: F13 needs a transmit-share row, F16")
    w("   and F17 fault responses traced to CON-004, and the case row's supervisor figure revised; round 4's sentence that placed both fault")
    w("   states outside every requirement was wrong (V6-B3). Labels as above; every junction is a MODEL figure, never a measurement")
    w("")
    # 10a
    w("   10a. THE REQUIREMENT, READ WHERE IT IS WRITTEN (V6-B3; round 4 read REQ-073 and REQ-004 and missed it)")
    w("   CON-004 (REQUIREMENTS-TRACE.md; %s, %s, %s): '%s'" % (P["con004_class"] + (P["con004"],)))
    w("     accepted when: '%s'; allocated to %s" % (P["con004_acc"], P["con004_alloc"]))
    w("   ARCH-PCB-B-IOHA.md section 12 ('Every row is a failure this design is supposed to survive or is knowingly exposed to'):")
    w("     row 7 '%s': %s; detected by %s" % P["row7"])
    w("     row 8 '%s': %s; detected by %s" % (P["row8"][0], P["row8"][1], P["row8"][2]))
    a7p = P["a7"][2].split("; ")
    w("   section 13, test A7 '%s': method '%s'; pass: the quorum kept through each cut (paraphrased: the source's verb is a word this" % P["a7"][:2])
    w("     record does not print), '%s', '%s'" % (a7p[1], a7p[2]))
    w("   So F16 (one fabric faulted, row 7) and F17 (both, row 8) are inside a mandatory core constraint: their closure is REQUIRED for")
    w("   CON-004. A7 as written CUTS a fabric (the 0 Ohm break links R508 to R513): it exercises an open, not a shorted bus, and not the")
    w("   TCAN334's %.0f mA bus-fault row (TXD 0 V, CANH -12 V, RL open); the shorted-bus variants are analysed in 10e and named in V-B21" % (P["can_fault"] * 1000))
    w("   CON-017: '%s'; '%s' (V6-m9). So L9T5-F14's two revisions are" % (Q["c17_5"], Q["c17_4"]))
    w("     settled at assembly: the fitted part is V or X. DS12110 Rev 10 prints rev Y (section 6) and rev V (section 7) only, no rev X")
    w("     section; T10 keeps rev Y's larger rows as the cover for a rev X part (CONSERVATIVE for rev V by construction, an ASSUMPTION for")
    w("     rev X), and rev V's rows as the fitted revision's own figures")
    w("")
    # 10b
    w("   10b. THE REFERENCE MANUAL IS HELD (RM0433 Rev 8, v2/vendor/st/st-rm0433-rev8.pdf, filed 27 September 2026; round 4 took it as not held)")
    w("   p.279: '%s'; p.349: '%s';" % (Q["rm_vos"], Q["rm_hsi"]))
    w("   DS12110 Rev 10: fHSI %.0f MHz. So T10-A1's ASSUMPTION is replaced by the printed reset state, HSI at %.0f MHz and VOS3: INSIDE the bound" % (Q["hsi"], Q["hsi"]))
    w("   (VOS3, at most %d MHz), and the bound stays the least printed row over it" % BOUND[1])
    w("   p.2464: '...%s'" % Q["rm_init"])
    w("   p.2534: '%s' (no automatic recovery)" % Q["rm_bo"])
    w("   p.2470: '...%s'; p.2527: FDCAN_CCCR bit 6 DAR. With DAR = 1 a frame is sent once and" % Q["rm_dar"])
    w("     never repeated by the controller, so every transmission is one the firmware scheduled")
    w("")
    # 10c: the bounded state with its peripherals
    w("   10c. THE BOUNDED STATE WITH THE ENABLED PERIPHERALS (V6-m10; T10-A2 restated), AND THE AIR EACH FIGURE IS JUDGED AT")
    for rev, tab in (("Y", "Table 39, p.117 to 122"), ("V", "Table 137, p.224 to 228")):
        w("   rev %s, %s, VOS3, TYPICAL uA/MHz: %s; sum %.1f uA/MHz (FDCAN twice: one clock enable serves both" % (
            rev, tab, ", ".join("%s %.1f" % (k, v) for k, v in Q["S_" + rev].items()), Q["s_" + rev]))
        w("     instances, the second count a margin for their traffic)")
    k_y = [kfac(P, "Y", t) for t in (25.0, 85.0, 105.0, 125.0)]
    k_v = [kfac(P, "V", t) for t in (25.0, 85.0, 105.0, 125.0)]
    w("   the sheet prints these as TYPICAL at 25 C only; taken to a bound here (MODEL): times the CPU clock bound %d MHz (an upper bound for" % BOUND[1])
    w("     every bus or kernel clock FW-B20 holds at or under it, whichever clock the per-MHz figure refers to), times the ratio the printed")
    w("     maxima of ALL peripherals enabled less all disabled bear to their typical (VOS3 200 MHz, the run table; rev Y %s, rev V %s at TJ" % (
        "/".join("%.3f" % k for k in k_y), "/".join("%.3f" % k for k in k_v)))
    w("     25/85/105/125 C; ASSUMPTION: the subset's spread is no wider than the whole set's); plus the HSE at %.2f mA (TYPICAL, 32 MHz row;" % (Q["hse"] * 1000))
    w("     the run rows do not say whether their clock source is in them, so it is added), the LSI at %.0f nA (its maximum) and the two TX" % (Q["lsi"] * 1e9))
    w("     pins' switching %.3f mA (VDD x %.0f MHz x %.0f pF each, the load ASSUMED)" % (2 * 3.3 * F_TX_MHZ * C_IO_PF * 1e-3, F_TX_MHZ, C_IO_PF))
    out["aux"] = {}
    return Q, ldo_k, tj_l, out


def shdn_check(nl):
    """the SHDN draft read on a board B netlist: each transceiver's pin 5 on its controller's net, that net on the controller's PD2 or
    PB14 and on one 100 k to GND, nothing else on it. Returns (verdict, why)."""
    why = []
    for tag, base in (("A", 40), ("B", 50), ("C", 60)):
        for can, (un, mcu_pin, rn) in (("1", (3, "83", 4)), ("2", (4, "53", 5))):
            net = "IOC%s_CAN%s_SHDN" % (tag, can)
            u, ref = "U%d" % (base + un), "R%d" % (63 + 12 * (base // 10 - 4) + rn)
            mem = sorted(CHK.members(nl, net))
            want = sorted(["%s.5" % u, "U%d.%s" % (base + 1, mcu_pin), "%s.1" % ref])
            if mem != want:
                why.append("%s reaches %s, wanted %s" % (net, mem, want))
            elif CHK.pin(nl, ref, "2") != "GND" or CHK.value(nl, ref) != "100k":
                why.append("%s is %s to %s, wanted 100k to GND" % (ref, CHK.value(nl, ref), CHK.pin(nl, ref, "2")))
    return ("FAIL" if why else "DRAWN"), why


def round5_rest(w, P, DP, air, hi3, Q, ldo_k, tj_l, out):
    vmax = 3.3 * P["vout_hi"]          # the LDO's output at its printed +1.5 % band edge
    with tempfile.TemporaryDirectory(prefix="l9t5_t10r5_") as d:
        seq = D.seq_of("b", "slot")
        at = seq.index(D.MINE["b"]) + 1
        seq5 = seq[:at] + [PRE["b"], SHDN] + seq[at:]
        p5, res5, ok5 = D.compose("b", seq5, d, "t10r5")
        rc, net5, tab5 = D.netlist("b", p5, d, "t10r5")
        if rc or not ok5:
            refuse("board B with the SHDN draft did not compose or regenerate: %s" % ("; ".join("%s %s" % (s, v) for s, v, _m in res5 if v != "OK") or net5))
        nl5 = CHK.read(open(net5, "rb").read())
        seq4 = seq[:at] + [PRE["b"]] + seq[at:]
        p4, _r4, ok4 = D.compose("b", seq4, d, "t10r4")
        rc4, net4, _t4 = D.netlist("b", p4, d, "t10r4")
        if rc4 or not ok4:
            refuse("board B without the SHDN draft did not regenerate")
        nl4 = CHK.read(open(net4, "rb").read())
        v_new, why_new = shdn_check(nl5)
        v_old, why_old = shdn_check(nl4)
        mut = D.mutate(net5, d, "t10r5_mut", [(("U43", "5"), ("U43", "8"))])
        v_mut, why_mut = shdn_check(CHK.read(open(mut, "rb").read()))
        mut2 = D.mutate(net5, d, "t10r5_mut2", [(("R80", "2"), ("U53", "3"))])
        v_mut2, why_mut2 = shdn_check(CHK.read(open(mut2, "rb").read()))
        kit5, _v = CHK.run({"b": net5}, ROOT, io.StringIO(), label=lambda x: "b", div="t10")
        # the contract draft on a scratch copy of the tree's page
        cpy = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copy(os.path.join(ROOT, DOCS["contract"]), cpy)
        before_tree = sha(DOCS["contract"], 64)
        c1 = subprocess.run([sys.executable, "-B", CONTRACT, cpy], capture_output=True)
        c2 = subprocess.run([sys.executable, "-B", CONTRACT, cpy, "--write"], capture_output=True)
        c3 = subprocess.run([sys.executable, "-B", CONTRACT, cpy, "--write"], capture_output=True)
        page = open(cpy, encoding="utf-8").read()
        rows_new = [l.split(" | ")[0].lstrip("| ") for l in page.splitlines() if re.match(r"\| (FW-B2[01]|V-B2[01]) \|", l)]
        contract_ok = (c1.returncode == 0 and b"CHECK OK" in c1.stdout and c2.returncode == 0 and b"WRITTEN" in c2.stdout and c3.returncode == 3
                       and rows_new == ["FW-B20", "FW-B21", "V-B20", "V-B21"] and sha(DOCS["contract"], 64) == before_tree)
        # the circuit's own auxiliaries, the fabric's extent, board B's rails
        aux = {tag: aux_from_netlist(nl5, tag, vmax) for tag in "ABC"}
        rails = CHK.rails_of(tab5["intent"])
        can_nets = sorted({n for dd in nl5["pins"].values() for n in dd.values() if re.fullmatch(r"CAN[HL]_[AB]1?", n)})
        can_parts = sorted({r for r, dd in nl5["pins"].items() if set(dd.values()) & set(can_nets)})
        n_parts = len(tab5["parts"])
    out.update(rails=rails, seq5=[os.path.basename(s) for s in seq5], ok5=ok5, n_parts=n_parts, v_new=v_new, v_old=v_old, v_mut=v_mut, v_mut2=v_mut2, kit5=kit5,
               contract_ok=contract_ok, can_parts=can_parts)
    i_aux = max(sum(x[2] for x in v) for v in aux.values())
    out["i_aux"] = i_aux
    aux_a = aux["A"]
    w("   the controller's OTHER loads on its own 3.3 V, from the composed board B netlist (section 10f's composition): %s, each at the LDO's" % (
        ", ".join("%s %s" % (r, v) for r, v, _i in aux_a)))
    w("     %.4f V (VOUT +%.1f %%, PRINTED) over its value less %.0f %% (ASSUMED): %.4f A at most (the largest of the three controllers), against" % (
        vmax, (P["vout_hi"] - 1) * 100, R_TOL * 100, i_aux))
    w("     the generator's DECLARED %.3f A for the third part; the circuit's own figure is used below (MODEL, every resistor at the full rail)" % P["decl_loads"][3])
    i_rec, i_dom = P["can_rec"], P["can_dom_hi"]
    i_can = i_rec + (i_dom - i_rec) * SHARE
    out["i_can"] = i_can
    B = {}
    for rev in "YV":
        for a in (air, P["air_exhaust"]):
            pt = mcu_point(P, Q, rev, a)
            if pt is None:
                B[(rev, a)] = None
                continue
            reg = pt[1] + i_aux + 2 * i_can
            B[(rev, a)] = (pt[0], pt[1], reg, tj_l(reg, a), pt[1] + P["decl_loads"][3] + 2 * i_can, pt[1] + sum(P["decl_loads"][1:]))

    def max_air(rev):
        lo_, hi_ = 40.0, 100.0
        for _ in range(60):
            mid = 0.5 * (lo_ + hi_)
            pt = mcu_point(P, Q, rev, mid)
            if pt is not None and tj_l(pt[1] + i_aux + 2 * i_can, mid) <= TJ_GOAL:
                lo_ = mid
            else:
                hi_ = mid
        return lo_
    out["B"], out["max_air"] = B, {rev: max_air(rev) for rev in "YV"}
    w("   the LDO's drop at its worst corner (part 21): the pre-regulator's top %.4f V less the LDO's least output %.4f V (%.1f %%, PRINTED): %.4f V," % (
        hi3, 3.3 * P["vout_lo"], P["vout_lo"] * 100, hi3 - 3.3 * P["vout_lo"]))
    w("     %.1f K/A at 184 C/W (round 4 and section 8 used the nominal 3.3 V: %.4f V, %.1f K/A); every junction of section 10 is at this corner" % (
        P["theta_ldo"] * (hi3 - 3.3 * P["vout_lo"]), hi3 - 3.3, P["theta_ldo"] * (hi3 - 3.3)))
    w("   the two transceivers at FW-B21's share (10d): %.4f A each. THE BOUNDED STATE, each figure with the air it is judged at:" % i_can)
    w("     rev  air                       controller (TJ)        regulator   LDO junction  against %.0f C" % TJ_GOAL)
    for rev in "YV":
        for a, lab in ((air, "L4-E12 E5 mixed %.2f C" % air), (P["air_exhaust"], "L4-E12 E5 exhaust %.2f C" % P["air_exhaust"])):
            b_ = B[(rev, a)]
            if b_ is None:
                w("     %s    %-25s NO OPERATING POINT at or under %.0f C: the H743 itself is outside its rating in the bounded state" % (rev, lab, P["tj_mcu"]))
            else:
                w("     %s    %-25s %.4f A (%.1f C)     %.4f A    %6.1f C      %s" % (rev, lab, b_[1], b_[0], b_[2], b_[3], "holds" if b_[3] <= TJ_GOAL else "FAILS"))
    w("   the largest local air at which the bounded state holds %.0f C at the LDO with a controller operating point: rev Y %.2f C, rev V %.2f C" % (
        TJ_GOAL, out["max_air"]["Y"], out["max_air"]["V"]))
    w("   (V6-m10's 79.4 C was the declared peak's). JUDGED at %.2f C, the case's air (C-DEV rev 1, L4-E12 E5's mixed air, T10-A2 as written):" % air)
    by, bv = B[("Y", air)], B[("V", air)]
    w("     rev V %s (%.1f C); rev Y's rows, the cover for a rev X part, %s (%.1f C) at this corner (10h (1), SESSION L9T5-D7: rev V fitted)." % (
        "holds" if bv[3] <= TJ_GOAL else "FAILS", bv[3], "hold" if by[3] <= TJ_GOAL else "do NOT hold", by[3]))
    w("     In the exhaust air rev V holds (%.1f C); rev Y's rows give the controller no" % B[("V", P["air_exhaust"])][3])
    w("     operating point, which matters only for a rev X part (no printed rows) placed in air over %.2f C: which air the pockets see is the" % out["max_air"]["Y"])
    w("     inside air's question (U-02, the T-H1 mock-up), not settled here. With the generator's DECLARED auxiliaries instead (0.060 A a")
    w("     supervisor for its three other parts) rev Y reads %.1f C and rev V %.1f C at %.2f C: the declaration over-covers, it does not bound" % (
        tj_l(by[5], air), tj_l(bv[5], air), air))
    w("")
    # 10d: F13
    i_max_dom = (P["decl_loads"][1] - i_rec) / SHARE + i_rec
    out["i_max_dom"] = i_max_dom
    w("   10d. F13: THE TRANSMIT SHARE BOUNDED (FW-B21, drafted)")
    w("   With FDCAN_CCCR.DAR = 1 every frame is one the firmware scheduled (10b), so the firmware's schedule alone sets how long each TXD is")
    w("   dominant. FW-B21: each supervisor's own TXD dominant at most %.0f %% of every %d ms window on each fabric, its frames, their error flags" % (SHARE * 100, WINDOW_MS))
    w("   and its acknowledgements counted. A transceiver then averages ICC_rec + (ICC_dom - ICC_rec) x %.2f = %.1f + (%.0f - %.1f) x %.2f = %.2f mA" % (
        SHARE, i_rec * 1000, i_dom * 1000, i_rec * 1000, SHARE, i_can * 1000))
    w("   (PRINTED %.0f mA dominant at RL 50 Ohm: the bus's least RL is %.2f Ohm, two ends of 2 x 60R4 at -1 %%, between the 50 and 60 Ohm rows," % (
        i_dom * 1000, Q["rl_min"]))
    w("   the larger taken), under its DECLARED %.3f A; the declaration holds for ANY dominant current up to %.1f mA at that share, which covers" % (
        P["decl_loads"][1], i_max_dom * 1000))
    w("   the %.0f mA bus-fault row and the %.0f mA short-circuit row. The function needs far less: the quorum's frames at 1 Mbit/s or less" % (
        P["can_fault"] * 1000, Q["ios_dom"] * 1000))
    w("   (FW-B09) are a few per 100 ms; the bound is a firmware property the schedule computes, CONFIRMED on the bench by V-B21, not decided there")
    w("   The window: the junction follows the window's average when the window is short against the package's thermal time constant, which")
    w("   Diodes does not print (MISSING); whatever that constant, the junction never passes the held figure of section 8 (m) (%.1f C on rev Y" % (
        tj_l(by[1] + i_aux + 2 * i_dom, air)))
    w("   at this air with the enabled set, under the %.0f C absolute maximum)" % P["tj_ldo"])
    w("   F13: the held row (m) stays the no-row bound; WITH THE ROW the regulator reads %.1f C on rev V (%s %.0f C) and %.1f C on rev Y's cover" % (
        bv[3], "inside" if bv[3] <= TJ_GOAL else "OVER", TJ_GOAL, by[3]))
    w("     (%s; a rev X part HELD under L9T5-D7) at %.2f C, the worst drop's corner" % ("inside" if by[3] <= TJ_GOAL else "OVER by %.1f K" % (by[3] - TJ_GOAL), air))
    w("")
    return out


def round5_faults(w, P, air, Q, tj_l, out):
    """10e to 10g: the credible bus faults inside board B, each regulator's current and junction held, with the DTO and with the
    response; the response drafted; the case row's figure for the coordinator."""
    i_rec, i_dom, i_aux, i_can = P["can_rec"], P["can_dom_hi"], out["i_aux"], out["i_can"]
    rl = Q["rl_min"]
    v33 = 3.3 * P["vout_hi"]
    rails = out["rails"]
    neg = sorted(n for n, r in rails.items() if float(r.get("volts") or 0) < 0)
    high = sorted(n for n, r in rails.items() if float(r.get("volts") or 0) > Q["vbus_abs"])
    out["neg"], out["high"] = neg, high
    w("   10e. THE CREDIBLE BUS FAULTS INSIDE BOARD B (V6-B3, 1a; F16 and F17 restated per fault)")
    w("   Both fabrics lie wholly on board B: the parts on CANH_*/CANL_* in the composed netlist are %s, no connector among them. Board B's" % ", ".join(out["can_parts"]))
    w("   rails (the composed intent) include %s below 0 V: so the bus-fault row's -12 V has no source in this kit, and that row (%.0f mA) is" % (
        "none" if not neg else ", ".join(neg), P["can_fault"] * 1000))
    w("   used only as the ASSUMED figure for the faults whose current TI does not print (B1, B2). Rails over the bus pins' %.0f V absolute" % Q["vbus_abs"])
    w("   maximum: %s: a short to one is outside every printed figure (finding L9T5-F19, not credited)" % ", ".join(high))
    w("   The faulted transceiver's current while its TXD is dominant, I_f (a fault draws on ITS OWN supervisor's regulator):")
    flt = [
        ("B1", "CANH to GND (SOIC-8 pins 7 and 8 adjacent; STB is on GND)", "every dominant bit reads recessive: errors, error passive, bus-off",
         P["can_fault"], "ASSUMED: the %.0f mA row, printed at the larger voltage across the driver (CANH -12 V); at 0 V not printed" % (P["can_fault"] * 1000), "err"),
        ("B2", "CANH to CANL (pins 6 and 7 adjacent)", "differential zero: every dominant bit reads recessive, as B1",
         P["can_fault"], "ASSUMED as B1: the driver into its own low side, current-limited (6.3.7), not printed", "err"),
        ("B3", "CANL to GND", "the bus still works: CANH at %.2f V or more dominant (PRINTED) against the %.1f V threshold" % (Q["vod_canh_min"], Q["vit_max"]),
         i_dom + Q["vod_canl_max"] / rl, "MODEL: the %.0f mA row plus VO(D) CANL's %.2f V over RL %.2f Ohm" % (i_dom * 1000, Q["vod_canl_max"], rl), "ok"),
        ("B4", "CANH to a 3.3 V or 5 V net (its own +3V3_IOCx the worst)", "the bus still works; every node's dominant bits draw the termination current from that net",
         i_dom + v33 / rl, "MODEL: the %.0f mA row plus %.4f V over RL; the other nodes' bits add 2 x %.2f x %.1f mA" % (i_dom * 1000, v33, SHARE, v33 / rl * 1000), "own"),
        ("B5", "CANL to a 3.3 V or 5 V net (its own +3V3_IOCx the worst)", "dominant reads recessive: errors, as B1",
         Q["ios_dom"], "ASSUMED: IOS(DOM)'s %.0f mA, printed at CANL 12 V" % (Q["ios_dom"] * 1000), "err"),
        ("B6", "an open (a cut track or joint; A7's break links removed)", "an isolated node's frames go unacknowledged",
         P["can_dom"], "MODEL: the %.0f mA row at 60 Ohm (the open segment's RL is 120.8 Ohm, larger)" % (P["can_dom"] * 1000), "ack"),
        ("B7a", "a transceiver failed dominant: its TXD held low (a pin or a peripheral)", "the DTO frees the bus after %.1f to %.1f ms (PRINTED)" % (
            P["can_dto"][0], P["can_dto"][2]), i_dom, "PRINTED row into the healthy bus", "dto"),
        ("B7b", "a transceiver failed dominant: its driver stuck on, the DTO dead with it", "the bus held dominant; no node can send",
         i_dom, "MODEL: the failed driver taken as the dominant row (a failed part; nothing printed)", "stuck"),
    ]
    by_rev = {}
    for rev in "YV":
        bm = out["B"][(rev, air)][1]
        base = bm + i_aux
        rows_ = []
        for fid, what, bus, i_f, lab, kind in flt:
            other = i_can
            held = base + other + i_f
            if kind == "dto":
                dto = base + other + i_rec + Q["ios_rec"]
            elif kind == "ack":
                dto = base + other + i_rec + (i_f - i_rec) * 5.0 / 6.0
            elif kind == "stuck":
                dto = held
            else:
                dto = None
            if kind == "stuck":
                resp = base + other + Q["icc_shdn"]
            elif kind == "own":
                resp = base + other + i_rec + (i_f - i_rec) * SHARE + 2 * SHARE * v33 / rl
            else:
                resp = base + other + i_rec + (i_f - i_rec) * SHARE
            rows_.append((fid, held, dto, resp))
        by_rev[rev] = rows_
    for fid, what, bus, i_f, lab, kind in flt:
        w("     %-4s %s: %s" % (fid, what, bus))
        w("          I_f %.4f A, %s" % (i_f, lab))
    w("   Each regulator's current and LDO junction at %.2f C (one fabric faulted, the other at its share; IOHA row 7, a served state: %.0f C):" % (air, TJ_GOAL))
    w("     fault  rev  held (no DTO, no row)      the parts alone (DTO, no row)            with the response (FW-B21, SHDN drafted)")
    worst = {}
    for rev in "YV":
        for fid, held, dto, resp in by_rev[rev]:
            if dto is None:
                dto_s = "NOT BOUNDED (no row)"
            else:
                dto_s = "%.4f A %6.1f C" % (dto, tj_l(dto, air))
            w("     %-5s  %s    %.4f A %6.1f C %-7s   %-40s %.4f A %6.1f C %s" % (fid, rev, held, tj_l(held, air), "FAILS" if tj_l(held, air) > TJ_GOAL else "",
                                                                          dto_s, resp, tj_l(resp, air), "holds" if tj_l(resp, air) <= TJ_GOAL else "FAILS"))
        worst[rev] = max(r[3] for r in by_rev[rev] if r[0] != "B7b")
    out["fault_rows"], out["worst"] = by_rev, worst
    w("   the criterion per row (the owner's part 22; 10i reads every row again on both set points): every response and held row above is a")
    w("     SUSTAINED state (a fault on the bus stays until repaired), so %.0f C applies, %.0f C being the absolute maximum and never an operating" % (TJ_GOAL, P["tj_ldo"]))
    w("     target; the parts-alone column's B7a is a TRANSIENT the DTO ends in %.1f ms (its row is then the recessive figure)" % P["can_dto"][2])
    # both fabrics (row 8): the two worst responses together
    both = {}
    for rev in "YV":
        bm = out["B"][(rev, air)][1]
        f_resp = max(i_rec + (i_f - i_rec) * SHARE + (2 * SHARE * v33 / rl if kind == "own" else 0.0) for _f, _w, _b, i_f, _l, kind in flt if kind != "stuck")
        held2 = bm + i_aux + 2 * max(i_f for _f, _w, _b, i_f, _l, kind in flt)
        both[rev] = (bm + i_aux + 2 * f_resp, held2)
    out["both"] = both
    out["f_resp"] = max(i_rec + (i_f - i_rec) * SHARE + (2 * SHARE * v33 / rl if kind == "own" else 0.0) for _f, _w, _b, i_f, _l, kind in flt if kind != "stuck")
    out["flt"] = flt
    w("   Both fabrics faulted (IOHA row 8: 'nothing moves' is the accepted outcome, the regulators must survive it: %.0f C in any state;" % P["tj_ldo"])
    w("   the %.0f C criterion read as well): the worst response figure on both transceivers" % TJ_GOAL)
    for rev in "YV":
        w("     rev %s: held %.4f A, %.1f C (%s %.0f C); with the response %.4f A, %.1f C: %s %.0f C, %s %.0f C" % (
            rev, both[rev][1], tj_l(both[rev][1], air), "OVER" if tj_l(both[rev][1], air) > P["tj_ldo"] else "under", P["tj_ldo"],
            both[rev][0], tj_l(both[rev][0], air), "holds" if tj_l(both[rev][0], air) <= P["tj_ldo"] else "FAILS", P["tj_ldo"],
            "inside" if tj_l(both[rev][0], air) <= TJ_GOAL else "over", TJ_GOAL))
    st = [r for r in by_rev["Y"] if r[0] == "B7b"][0]
    out["b7b"] = (st[1], tj_l(st[1], air))
    w("   B7b if the failed part ignores its SHDN too: its own regulator holds %.4f A, %.1f C on rev Y (%.1f C rev V): under the %.0f C absolute" % (
        st[1], tj_l(st[1], air), tj_l([r for r in by_rev["V"] if r[0] == "B7b"][0][1], air), P["tj_ldo"]))
    b7v = tj_l([r for r in by_rev["V"] if r[0] == "B7b"][0][1], air)
    w("     maximum; %s the %.0f C criterion on rev V's rows (fitted, L9T5-D7), over it on rev Y's cover. SESSION decision (L9T5-D5): tolerated where" % (
        "inside" if b7v <= TJ_GOAL else "over", TJ_GOAL))
    w("     it is over. Why: it is one part failing three of its own functions at")
    w("     once (driver, time-out, mode pin); the regulator stays inside its printed absolute maximum, so its supervisor lives and the quorum")
    w("     holds on the other fabric (row 7); the fabric's errors detect it. To reverse: a load switch on each transceiver's supply (six parts)")
    w("   So with the response, on rev V's rows (fitted, L9T5-D7) every credible single fabric fault %s %.0f C (worst %.1f C; rev Y's cover %.1f C, %s)" % (
        "holds" if tj_l(worst["V"], air) <= TJ_GOAL else "does NOT hold", TJ_GOAL, tj_l(worst["V"], air), tj_l(worst["Y"], air),
        "inside" if tj_l(worst["Y"], air) <= TJ_GOAL else "over"))
    w("   and both fabrics faulted %s %.0f C" % ("hold" if max(tj_l(both[r][0], air) for r in "YV") <= P["tj_ldo"] else "do NOT hold", P["tj_ldo"]))
    w("   (%.1f C rev Y, %.1f C rev V); WITHOUT a row nothing bounds B1 to B6 (the parts' own bus-off ends a burst, but no row bounds how soon" % (
        tj_l(both["Y"][0], air), tj_l(both["V"][0], air)))
    w("   firmware restarts,")
    w("   and B6's unacknowledged frames repeat without end under automatic retransmission: %.1f C)" % tj_l([r for r in by_rev["Y"] if r[0] == "B6"][0][2], air))
    w("")
    # 10f: the response drafted
    w("   10f. THE RESPONSE, DRAFTED AND COMPOSED")
    w("   (1) FIRMWARE: apply_hw_fw_contract_t10.py on HW-FW-CONTRACT.md (UNAPPLIED; Layer 5 rows brought forward as a named prerequisite of")
    w("       the power gate, reason and acceptance in its docstring): FW-B20 (the run state, T10-A1, RM0433's reset state inside it), FW-B21")
    w("       (DAR = 1, the %.0f %% share per %d ms, a faulted fabric stopped and its transceiver shut down within 100 ms, probed once a second for" % (
        SHARE * 100, WINDOW_MS))
    w("       at most %d ms), V-B20, V-B21. On a scratch copy: check OK, written, second application refused, the tree's page untouched: %s" % (
        PROBE_MS, "yes" if out["contract_ok"] else "NO"))
    w("   (2) CIRCUIT: apply_gen_sch_b_canshdn.py (board B; release-guarded by RELEASE-T10.md): each TCAN334D's SHDN (pin 5, on no net as")
    w("       drawn: TI 6.3.6, 'The internal bias should not be relied on by design') to its controller's PD2 (fabric A) or PB14 (fabric B), 100 k")
    w("       to GND so a controller in reset leaves its transceivers in normal mode; SHDN high is the shutdown mode, driver and receiver off,")
    w("       %.1f uA at most (SLLSEQ7F 5.5, Table 6-5). Composed straight after T10's iocpre (%d drafts: %s): %s; %d parts" % (
        Q["icc_shdn"] * 1e6, len(out["seq5"]), "every step OK" if out["ok5"] else "REFUSED", "the generator ran to its end", out["n_parts"]))
    w("       read on the netlist: SHDN %s; record l9t5's own board B check %s; the state before it (no draft) %s; mutations: U43's pin 5" % (
        out["v_new"], out["kit5"], out["v_old"]))
    w("       exchanged with its pin 8 (GND) %s; R80 lifted from GND to +3V3_IOCB (a pull-up) %s" % (out["v_mut"], out["v_mut2"]))
    w("")
    # 10g: the case row's figure for the coordinator
    w("   10g. THE CASE ROW'S SUPERVISOR FIGURE, FOR THE COORDINATOR (C-DEV rev 1 carries rv-pwr's HIGH: 0.400 A a controller plus 0.060 A)")
    cy, cv = out["B"][("Y", air)], out["B"][("V", air)]
    out["cdev"] = (cy[1], cy[1] + sum(P["decl_loads"][1:]))
    w("   derived: the bounded controller with its enabled set at its operating point at %.2f C, rev Y's rows (the cover): %.4f A (TJ %.1f C);" % (air, cy[1], cy[0]))
    w("   in the budget's own form, 3 x (%.4f + 0.060) x 3.3 = %.3f W at +3V3_IOCx in place of 3 x (0.400 + 0.060) x 3.3 = %.3f W; +5V_IOC then" % (
        cy[1], 3 * (cy[1] + 0.06) * 3.3, 3 * 0.46 * 3.3))
    w("   carries %.4f A in place of 1.3800 A (an LDO passes its output current). With FW-B21's share and the circuit's own auxiliaries the" % (3 * (cy[1] + 0.06)))
    w("   regulator carries %.4f A (rev Y; %.4f A rev V). LABELLED SCENARIO until the coordinator issues the row: section 9's (4) at the" % (cy[2], cv[2]))
    w("   case's HIGH stays NOT COVERED on rev 1's figure; on this figure the LDO reads %.1f C with the DECLARED auxiliaries and %.1f C with" % (
        tj_l(cy[5], air), tj_l(cy[2], air)))
    w("   the share and the circuit's own (rev Y)")
    w("")
    return out



FRAME_BITS = 135          # a classic CAN frame with 8 data bytes at its most stuffing, every bit counted dominant (ASSUMPTION: the
                          # standard ISO 11898-1 is not held; 111 bits before stuffing and 24 stuff bits, the textbook figure)
NEED = (1, 8)             # the service the record assumes (ASSUMPTION: the tree defines no CAN message rate): one state frame per
                          # supervisor per fabric per 100 ms, and a burst of 8 event frames in a window when ownership moves
VDD_TOL = 0.015           # the LDO's VOUT band (+1.5 %, PRINTED); the run tables are at VDD 3.3 V: the current taken up in proportion (MODEL)


def round5_answers(w, P, DP, air, hi3, Q, tj_l, out):
    """10h: the four questions the owner's review of 5 October 2026 (part 21) says the independent check will ask."""
    ldo_k = P["theta_ldo"] * (hi3 - 3.3 * P["vout_lo"])
    k_top = P["theta_ldo"] * (hi3 - 3.3 * P["vout_hi"])
    i_aux, i_can, f_resp = out["i_aux"], out["i_can"], out["f_resp"]
    w("   10h. THE FOUR QUESTIONS THE INDEPENDENT CHECK WILL ASK (the owner's review of checkpoint 2, 5 October 2026, part 21)")
    # (1) the thermal and current inputs, the margin and where it is lost
    w("   (1) WHAT THE 125 C RESULT RESTS ON, WHAT CONSUMES ITS MARGIN, AND AT WHICH CORNER IT IS LOST (MODEL; each state at its own worst)")
    w("     the inputs: the air (L4-E12 E5's mixed %.2f C, the case's; %.2f C in the exhaust); the LDO's 184 C/W 'no heat sink' (Diodes prints no" % (
        air, P["air_exhaust"]))
    w("     board for it: the layout must give each LDO at least that board's copper, a Layer 10 means, read by T10-A5); the pre-regulator's top")
    w("     %.4f V (the divider at 0.1 %% and 25 ppm/K over 65 K, VFB's printed band and IFB: every tolerance at its worst); the controller's" % hi3)
    w("     printed maxima at its own junction; the enabled set's bound; the circuit's auxiliaries at the full rail; the share fully used")
    states = {}
    for rev in "YV":
        b_ = out["B"][(rev, air)]
        states[(rev, "the bounded state")] = (b_[1], i_aux + 2 * i_can)
        states[(rev, "the worst single fault, responded")] = (b_[1], i_aux + i_can + f_resp)
        states[(rev, "both fabrics faulted, responded")] = (b_[1], i_aux + 2 * f_resp)

    def tj_at(rev, extra, a):
        pt = mcu_point(P, Q, rev, a)
        return None if pt is None else (a + ldo_k * (pt[1] + extra), pt[1])
    ledger = {}
    for (rev, lab), (i_m, extra) in states.items():
        tj = tj_l(i_m + extra, air)
        m = TJ_GOAL - tj
        lo_, hi_ = air - 20.0, air + 20.0
        for _ in range(60):
            mid = 0.5 * (lo_ + hi_)
            r_ = tj_at(rev, extra, mid)
            if r_ is not None and r_[0] <= TJ_GOAL:
                lo_ = mid
            else:
                hi_ = mid
        th = (TJ_GOAL - air) / ((hi3 - 3.3) * (i_m + extra))
        th = (TJ_GOAL - air) / ((hi3 - 3.3 * P["vout_lo"]) * (i_m + extra))
        tj_top = air + k_top * (i_m * (1 + VDD_TOL) + extra)
        ledger[(rev, lab)] = (tj, m, lo_, th, m / ldo_k, tj_top)
        w("     rev %s, %-34s %.4f A, %.1f C: margin %+.2f K = %+.1f mA at the LDO; lost at a local air of %.2f C, or at %.0f C/W in place of 184;"
          % (rev, lab + ":", i_m + extra, tj, m, m / ldo_k * 1000, lo_, th))
        w("       at the LDO's top output (the controller's current up %.1f %%, MODEL; the drop smaller) it reads %.1f C, under the corner above" % (
            VDD_TOL * 100, tj_top))
    yv = {k: v for k, v in ledger.items() if k[0] == "Y"}
    vv = {k: v for k, v in ledger.items() if k[0] == "V"}
    out["ledger"] = ledger
    i_cap = (TJ_GOAL - air) / ldo_k - (i_aux + 2 * f_resp)
    out["i_cap"] = i_cap
    w("     so at the worst corner (the LDO's least output, the case's air): rev V's own rows keep %.1f K or more in every state and hold to a local air" % min(
        v[1] for v in vv.values()))
    w("     of %.2f C, over the %.2f C exhaust; rev Y's rows, the COVER this record takes for a rev X part (DS12110 prints no rev X rows), read %.1f to"
      % (min(v[2] for v in vv.values()), P["air_exhaust"], min(v[0] for v in yv.values())))
    w("     %.1f C: they DO NOT hold 125 C at this corner (round 4 and the first pass of round 5 judged the nominal drop). What consumes the margin:" % max(
        v[0] for v in yv.values()))
    w("     the controller's leakage at its own junction (rev Y's 144 MHz row climbs from %.0f mA at 85 C to %.0f mA at 105 C), the enabled set's bound and" % (
        P["Y"][("off", 144)][2], P["Y"][("off", 144)][3]))
    sens = {}
    for rev in "YV":
        hi_, lo_ = tj_at(rev, i_aux + 2 * f_resp, air + 0.25), tj_at(rev, i_aux + 2 * f_resp, air - 0.25)
        sens[rev] = (hi_[0] - lo_[0]) / 0.5 if hi_ and lo_ else None
    w("     the drop's corner; each kelvin of local air costs %.2f K at the LDO on rev V's rows and %.2f K on rev Y's (the controller's own" % (sens["V"], sens["Y"]))
    w("     operating point rises with the air, steeply on rev Y's rows near their runaway)")
    w("     THE CONTROLLER FIGURE A FITTED PART MUST MEET for the worst state (both fabrics faulted, responded) to hold 125 C at this corner: at most")
    w("     %.4f A at its own operating point at %.2f C air (rev V's rows: %.4f A; rev Y's: %.4f A). PROVISIONAL CHOICE (SESSION L9T5-D7): the" % (
        i_cap, air, out["B"][("V", air)][1], out["B"][("Y", air)][1]))
    w("     supervisors are fitted in revision V (inside CON-017 (5), which admits V or X), the revision whose printed rows hold; a rev X part is")
    w("     accepted only after the supplier's V-B20 reads its supply current at the bound, at a junction of 105 C or more, at most that figure")
    w("     (specimen: three rev X STM32H743VIT6 on the first-article board B; quantity: each supervisor's supply current at FW-B20's bound and")
    w("     FW-B21's share, at its operating junction; pass limit: at most %.4f A); the inside air at the pockets is U-02's (the T-H1 mock-up)" % i_cap)
    # (2) the service budget
    w("   (2) THE CAN SERVICE UNDER THE BOUND (VOS3, at most 144 MHz, 2 % of every 100 ms per fabric)")
    w("     what the fabrics carry: the supervisors' quorum (state, leases, epochs, the votes' agreement; FW-B09, IOHA sections 6 and 7). Not on")
    w("     them: the modules' heartbeats (GPIO lines HB1 to HB3, FW-B01), the voted outputs (GPIO into the voters, FW-B12), FW-E07's stopped-fan")
    w("     report (board E's sensor controller, the kit bus, FW-E07 and V-E07's 5 s). The tree defines no CAN message rate; the record ASSUMES")
    w("     %d state frame per supervisor per fabric per 100 ms and a burst of %d event frames in a window when ownership moves" % NEED)
    svc = {}
    for rate in (125e3, 500e3, 1e6):          # 125 kbit/s shown as the case FW-B21 excludes (its range is 500 kbit/s to 1 Mbit/s)
        bits = SHARE * WINDOW_MS * 1e-3 * rate
        n = int(bits // (FRAME_BITS + 2))          # each own frame, and the acknowledgements of the other two's frames
        svc[rate] = n
        w("     at %4.0f kbit/s: %5.0f dominant bit times a window: %2d frames of %d bits (every bit counted dominant) with two acknowledgements each;"
          % (rate / 1e3, bits, n, FRAME_BITS))
        w("       the need %d (%s)" % (sum(NEED), "inside" if n >= sum(NEED) else "NOT inside: a state frame per window only, the event burst spread over %d windows" % (
            -(-NEED[1] // max(1, n - NEED[0])) if n > NEED[0] else 0)))
    w("     REQ-004's 30 s for a moved bank (ownership plus re-enumeration) is %d windows; at 125 kbit/s the event burst spreads over at most %d of" % (
        int(30.0 / (WINDOW_MS * 1e-3)), -(-NEED[1] // max(1, svc[125e3] - NEED[0]))))
    w("     them; at 500 kbit/s and over it fits one window. A7: with one fabric cut the other carries the same traffic under the same share (the")
    w("     share is per fabric, not shared). CON-004's quorum needs two of three state frames inside the loss timeout the firmware sets: the")
    w("     share allows %d to %d a window at FW-B21's 500 kbit/s to 1 Mbit/s (%d at 125 kbit/s, which FW-B21 therefore excludes). So the bound keeps" % (
        svc[500e3], svc[1e6], svc[125e3]))
    w("     the service the tree requires, on the assumed message set (the firmware's to confirm")
    w("     against its real one, V-B21)")
    # (3) enforceability
    w("   (3) WHAT ENFORCES THE BOUND AND THE RESPONSE IN THE FAULTS THE CALCULATION USES (an unapplied contract row is no mechanism)")
    w("     HARDWARE, whatever the firmware does: the TCAN334's driver time-out frees a held TXD in %.1f to %.1f ms (PRINTED); the FDCAN's own bus-off" % (
        P["can_dto"][0], P["can_dto"][2]))
    w("     sets INIT and holds TX recessive with no automatic restart (RM0433 p.2464 and p.2534; the count to bus-off is the CAN standard's, not")
    w("     held); any reset (the IWDG, started by option byte under FW-B10, on its own LSI) returns the reset state, inside the bound, with the TX")
    w("     pins high-impedance and each TXD on the transceiver's pull-up, recessive; SHDN rests on its 100 k in normal mode (the draft)")
    w("     FIRMWARE (FW-B20, FW-B21, enforceable only once applied and built): the clock and VOS read back at start; DAR = 1; the share; a fabric")
    w("     at error passive, bus-off or with no valid frame for 100 ms stopped and its transceiver shut down; probing once a second for 100 ms")
    w("     per fault, what acts and when (each window carries at most %.0f ms of own dominant drive by the schedule, so a fault's current is" % (SHARE * WINDOW_MS))
    w("     averaged over the window whatever the detection time):")
    rows3 = (("B1, B2, B5 (bits read wrong)", "each scheduled frame errs once (DAR); EP or BO stops the fabric and SHDN; the device's own bus-off backs it", "the schedule's 2 ms a window; the stop within 100 ms"),
             ("B3, B4 (the bus still works)", "nothing detects them: the share alone bounds the current, which the result above already counts", "every window"),
             ("B6 (an open: no acknowledgement)", "each frame errs once (DAR, ACK errors); the no-valid-frame rule stops the fabric", "within 100 ms; 2 ms a window before"),
             ("B7a (TXD held low)", "the DTO (hardware) frees the drive; the FDCAN errs; the firmware stops the fabric", "%.1f ms" % P["can_dto"][2]),
             ("B7b (driver stuck on, DTO dead)", "every supervisor sees no valid frame; each stops the fabric and drives its SHDN; the failed part may ignore it (L9T5-D5)", "within 100 ms"))
    for a, b, c in rows3:
        w("       %-34s %-118s %s" % (a, b, c))
    i_babble = out["B"][("Y", air)][1] + i_aux + 2 * i_dom_of(P)
    w("     THE FIRMWARE AS THE FAULTING PARTY: a hang is ended by the IWDG (hardware-started, FW-B10) and leaves nothing new transmitted (DAR); with DAR")
    w("     mis-set and the CPU hung, B6's endless retransmission is the worst (%.1f C on rev Y, the parts-alone column), under the %.0f C absolute" % (
        tj_l([r for r in out["fault_rows"]["Y"] if r[0] == "B6"][0][2], air), P["tj_ldo"]))
    w("     maximum. A running firmware that breaks the share (a babbling supervisor) is bounded by both transceivers held dominant: %.4f A, %.1f C on" % (
        i_babble, tj_l(i_babble, air)))
    w("     rev Y, under %.0f C, over %.0f C (it costs margin, not the regulator; its own fabric traffic is then the quorum's problem, an FMEA row" % (
        P["tj_ldo"], TJ_GOAL))
    w("     IOHA section 12 does not carry: finding L9T5-F21). A running firmware that breaks the CLOCK bound (FW-B20) takes the controller")
    w("     itself outside its rating (section 4: no operating point over 200 MHz with the peripherals on) and can take the LDO over 150 C:")
    w("     nothing in hardware prevents it. That is a SYSTEMATIC firmware defect, closed by the firmware's verification (FW-B20's read-back,")
    w("     V-B20, CON-017 (4)'s firmware stage), not by a protective mechanism: an OPEN implementation obligation, not a desk-fixable circuit")
    w("     defect. Round 4's K1 (a buck per supervisor) would let the regulator survive it, but not the controller (SESSION decision L9T5-D6:")
    w("     K1 not taken for it; to reverse, round 4's K1)")
    # L9T5-F22's lever, as a labelled SCENARIO for the drafts' owner: the set point held at the largest current this record computes for a
    # regulator (the held B5 row on rev Y), the dropout INFERRED linear between its printed 300 and 600 mA points
    G = D.gndret()
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    i_hold = max(r[1] for r in out["fault_rows"]["Y"])
    drop_i = P["drop"][300] + (P["drop"][600] - P["drop"][300]) * (i_hold - 0.3) / 0.3
    need_i = 3.3 * (P["vout_hi"] + P["load"] * i_hold) + drop_i
    sc = []
    for rb in (13.7e3, 14.0e3, 14.3e3):
        lo_, nom_, hi_ = CHK.vout_band(R601, rb)
        at_ = lo_ - D.RAIL_BUDGET * nom_ - 3 * i_hold * r_sup - G["shift_drawn_ub"]
        k_ = P["theta_ldo"] * (hi_ - 3.3 * P["vout_lo"])
        sc.append((rb, nom_, hi_, at_, at_ >= need_i, air + k_ * (out["B"][("Y", air)][1] + i_aux + 2 * f_resp)))
    out["f22"] = (i_hold, need_i, sc)
    w("   L9T5-F22's lever (SCENARIO for the T10 drafts' owner, not drafted): the LDOs' input held over its requirement at the largest current this")
    w("     record computes for a regulator (%.4f A, the held B5 row on rev Y; dropout %.0f mV INFERRED between the printed 300 and 600 mA points):" % (
        i_hold, drop_i * 1000))
    w("     %.4f V. R602 at:" % need_i)
    for rb, nom_, hi_, at_, ok_, tjy in sc:
        w("       %.1f k: %.4f V nominal, top %.4f V; the LDOs' input at least %.4f V (%s); rev Y's cover, both fabrics faulted, %.1f C" % (
            rb / 1e3, nom_, hi_, at_, "holds" if ok_ else "FAILS", tjy))
    w("     (T10-A3 as round 4 wrote it, at the full 600 mA, fails with any of them: that criterion is the drafts' owner's to restate)")
    # (4) the composed changes against the calculation and C-DEV rev 2
    c = importlib.util.spec_from_file_location("l9t5_contract_draft", CONTRACT)
    cm = importlib.util.module_from_spec(c)
    c.loader.exec_module(cm)
    rows = cm.FW_B20 + cm.FW_B21
    want = ("VOS3", "at most 144 MHz", "at most %d %% of every %d ms window" % (round(SHARE * 100), WINDOW_MS), "no more than once a second",
            "for at most %d ms" % PROBE_MS, "no valid frame for %d ms" % WINDOW_MS, "FDCAN_CCCR.DAR = 1", "PD2 (fabric A) and PB14 (fabric B) with 100 k",
            "between 500 kbit/s and 1 Mbit/s")
    miss = [x for x in want if x not in rows]
    cd = text(DOCS["cdev2"])
    nums = {"reg_y": "%.4f A a regulator" % out["B"][("Y", air)][2], "reg_v": "%.4f A rev V" % out["B"][("V", air)][2],
            "mcu": "%.4f A at TJ %.1f C" % (out["B"][("Y", air)][1], out["B"][("Y", air)][0]),
            "w": "%.3f W at +3V3_IOCx" % (3 * (out["cdev"][0] + 0.06) * 3.3), "ioc": "+5V_IOC %.4f A" % (3 * (out["cdev"][0] + 0.06)),
            "aux": "%.4f A at most" % i_aux}
    cd_flat = " ".join(cd.replace("*", "").split())
    cmiss = [k for k, v in nums.items() if v not in cd_flat]
    out["match"] = (not miss, not cmiss, out["v_new"] == "DRAWN")
    w("   (4) THE COMPOSED CHANGES AGAINST THE CALCULATION AND THE ISSUED CASE ROW")
    w("     the contract draft's rows carry this record's figures (%s): %s" % ("; ".join(want), "every one" if not miss else "MISSING: %s" % miss))
    w("     the SHDN draft's nets in the regenerated board B netlist: %s (10f); the pre-regulator's divider: section 9's reading" % out["v_new"])
    w("     C-DEV rev 2 as the coordinator issued it (the copy inputs/cases-cdev-rev2-20261005.md, sha256 %s, of _runs/cases/CASES-2026-10-04.md):" % sha(DOCS["cdev2"]))
    w("     its figures against this output's (%s): %s" % ("; ".join(nums.values()), "every one equal" if not cmiss else "DIFFER: %s" % cmiss))
    w("")
    return out


def i_dom_of(P):
    return P["can_dom_hi"]


FITTED_REV, COVER_REV = "V", "Y"   # SESSION L9T5-D7: the fitted revision's printed rows judge the design; rev Y's are the cover for rev X
SET = os.path.join(HERE, "apply_gen_sch_%s_iocset.py")   # T10 round 5, part 22: the set point delta (L9T5-F22 drafted)
R602_SET = 14.0e3


def set_check(nl):
    """the set point delta read on a board A netlist: R601 over R602 is 56.2k over 14.0k (0.1 %), its band 3.9063 to 4.1174 V."""
    dv = CHK.divider(nl)
    if not dv:
        return "FAIL", ["no divider on U601's FB"]
    why = []
    if abs(dv[0] - R601) > 1e-6 or abs(dv[1] - R602_SET) > 1e-6:
        why.append("the divider is %s over %s, wanted 56.2k over 14.0k" % (CHK.value(nl, dv[2]), CHK.value(nl, dv[3])))
    if "0.1%" not in CHK.value(nl, dv[3]):
        why.append("R602 is not a 0.1 % part")
    return ("FAIL" if why else "DRAWN"), why


def round5_part22(w, P, DP, air, hi3, Q, tj_l, out):
    """10i: the owner's review of checkpoint 3 (part 22), items B and C: the criterion per state, the babbling and hung rows, the
    set point delta drafted (L9T5-F22), the fitted revision made the model's case selection, the Layer 6 and Layer 12 rows drafted."""
    i_aux, i_can = out["i_aux"], out["i_can"]
    lo14, nom14, hi14 = CHK.vout_band(R601, R602_SET)
    k13 = P["theta_ldo"] * (hi3 - 3.3 * P["vout_lo"])
    k14 = P["theta_ldo"] * (hi14 - 3.3 * P["vout_lo"])
    rows = []
    for rev in (FITTED_REV, COVER_REV):
        b_ = out["B"][(rev, air)]
        fr = {r[0]: r for r in out["fault_rows"][rev]}
        st = [("the bounded state (FW-B20, FW-B21)", b_[2], "sustained, served", TJ_GOAL)]
        for fid in ("B1", "B2", "B3", "B4", "B5", "B6", "B7a"):
            st.append(("%s with the response" % fid, fr[fid][3], "sustained, served (row 7)", TJ_GOAL))
        st.append(("B7b, SHDN obeyed", fr["B7b"][3], "sustained, served (row 7)", TJ_GOAL))
        st.append(("B7b, SHDN ignored (L9T5-D5)", fr["B7b"][1], "sustained, a failed part", TJ_GOAL))
        st.append(("both fabrics faulted, responded", out["both"][rev][0], "sustained, row 8", TJ_GOAL))
        st.append(("hung, DAR mis-set (the IWDG ends it)", fr["B6"][2], "transient, ended by the IWDG", P["tj_ldo"]))
        st.append(("babbling (nothing ends it)", b_[1] + i_aux + 2 * P["can_dom_hi"], "sustained, a firmware fault", TJ_GOAL))
        for lab, i, kind, lim in st:
            rows.append((rev, lab, i, kind, lim, air + k13 * i, air + k14 * i))
    out["p22_rows"] = rows
    w("   10i. THE OWNER'S REVIEW OF CHECKPOINT 3 (part 22): THE CRITERION PER STATE, AND THE SET POINT THAT BOUNDS THE BABBLING ROW")
    w("   the rule (the owner's part 22; T10's criterion since round 4): a SUSTAINED state, served or a fault the design must survive, is judged")
    w("   at %.0f C, because %.0f C is the absolute maximum and never an operating target; a TRANSIENT that hardware ends within a bound is" % (TJ_GOAL, P["tj_ldo"]))
    w("   judged at %.0f C on its steady-state figure (an upper bound of any transient), and %.0f C is read beside it. Hung: the FDCAN" % (P["tj_ldo"], TJ_GOAL))
    w("   retransmits with the CPU hung only until the IWDG resets it (hardware-started under FW-B10; its timeout the firmware's to set); a")
    w("   babbler: a running firmware that breaks FW-B21 and still serves its watchdog is ended by nothing: SUSTAINED. The service in it: the")
    w("   babbler can deny both fabrics by arbitration, so the quorum may stop and the voters hold the home assignment (row 8's safe state);")
    w("   that a single supervisor's firmware can stop CON-004's quorum is L9T5-F21 (OPEN, Layer 5 and IOHA section 12: a voted silence of")
    w("   the babbler, its transceivers' SHDN or its LDO's EN by the other two, is the circuit direction; NOT drafted here)")
    w("   the set point delta (apply_gen_sch_a_iocset.py, apply_gen_sch_b_iocset.py, after T10's iocpre; L9T5-F22 drafted): R602 14.0k, %.4f V" % nom14)
    w("     nominal, %.4f to %.4f V; the drop at its worst corner %.4f V, %.1f K/A (13.3k: %.4f V, %.1f K/A)" % (
        lo14, hi14, hi14 - 3.3 * P["vout_lo"], k14, hi3 - 3.3 * P["vout_lo"], k13))
    w("     state at %.2f C (MODEL)                     rev  current    criterion        13.3k (iocpre)   14.0k (iocset)" % air)
    for rev, lab, i, kind, lim, t13, t14 in rows:
        w("     %-44s %s   %.4f A   %-16s %6.1f C %-6s  %6.1f C %s" % (lab, rev, i, "%.0f C (%s)" % (lim, kind.split(",")[0]), t13,
                                                                     "holds" if t13 <= lim else "FAILS", t14, "holds" if t14 <= lim else "FAILS"))
    fit13 = all(t13 <= lim for rev, lab, i, kind, lim, t13, t14 in rows if rev == FITTED_REV)
    fit14 = all(t14 <= lim for rev, lab, i, kind, lim, t13, t14 in rows if rev == FITTED_REV)
    bab = {rev: (t13, t14) for rev, lab, i, kind, lim, t13, t14 in rows if lab.startswith("babbling")}
    out["p22"] = dict(fit13=fit13, fit14=fit14, bab=bab, k14=k14, hi14=hi14, lo14=lo14)
    w("     so on revision %s (fitted, L9T5-D7): with iocpre alone the babbling row FAILS %.0f C (%.1f C); with iocset every row %s %.0f C (the" % (
        FITTED_REV, TJ_GOAL, bab[FITTED_REV][0], "holds" if fit14 else "does NOT hold", TJ_GOAL))
    w("     babbler %.1f C). On rev Y's rows, the cover for rev X, the babbler stays over 125 C at 14.0k (%.1f C): a rev X part is still" % (
        bab[FITTED_REV][1], bab[COVER_REV][1]))
    w("     admitted only by V-B20 (10h (1)); the proof above is revision V's and is never applied to revisions X or Y")
    # T10-A3 restated at the record's largest current, and the composition of the delta
    G = D.gndret()
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    i_hold = max(r[1] for r in out["fault_rows"][COVER_REV])
    drop_i = P["drop"][300] + (P["drop"][600] - P["drop"][300]) * (i_hold - 0.3) / 0.3
    need_i = 3.3 * (P["vout_hi"] + P["load"] * i_hold) + drop_i
    at_i = lo14 - D.RAIL_BUDGET * nom14 - 3 * i_hold * r_sup - G["shift_drawn_ub"]
    out["p22"]["a3"] = (i_hold, need_i, at_i)
    w("   T10-A3 RESTATED (SESSION L9T5-D8): each LDO's input over its requirement at the largest current this record computes for a regulator")
    w("     (%.4f A, the held B5 row on rev Y's rows; dropout %.0f mV INFERRED between the printed 300 and 600 mA points): at least %.4f V against" % (
        i_hold, drop_i * 1000, at_i))
    w("     %.4f V: %s. Round 4 held it at the LDO's full 600 mA; at 14.0k that criterion fails, and a supervisor drawing more than the record's" % (
        need_i, "holds" if at_i >= need_i else "FAILS"))
    w("     largest current is a supervisor fault its own BOR ends (it browns out alone; the other two hold the quorum, IOHA row 3)")
    with tempfile.TemporaryDirectory(prefix="l9t5_t10p22_") as d:
        res = {}
        for b in "ab":
            seq = D.seq_of(b, "slot")
            at = seq.index(D.MINE[b]) + 1
            seq = seq[:at] + [PRE[b], SET % b] + seq[at:]
            p_, r_, ok_ = D.compose(b, seq, d, "p22")
            rc, net, tab = D.netlist(b, p_, d, "p22")
            if rc or not ok_:
                refuse("board %s with the set point delta did not compose or regenerate: %s" % (b, net))
            res[b] = (ok_, net, tab, len(seq))
        nla = CHK.read(open(res["a"][1], "rb").read())
        v_set, why_set = set_check(nla)
        m1 = D.mutate(res["a"][1], d, "p22_mut", [(("R601", "1"), ("R602", "2"))])
        v_m1, _w = set_check(CHK.read(open(m1, "rb").read()))
        raw = open(res["a"][1], encoding="utf-8").read().replace('(value "14.0k 0.1% 25ppm")', '(value "13.3k 0.1% 25ppm")')
        m2 = os.path.join(d, "p22_mut2.net")
        open(m2, "w", encoding="utf-8").write(raw)
        v_m2, _w = set_check(CHK.read(open(m2, "rb").read()))
        ra_, rb_ = CHK.rails_of(res["a"][2]["intent"]), CHK.rails_of(res["b"][2]["intent"])
        decl_ok = (abs(ra_["+5V_IOC"]["volts"] - 4.01) < 1e-9 and ra_["+5V_IOC"]["v_work"] >= hi14 and abs(rb_["+5V_IOC"]["volts"] - 4.01) < 1e-9
                   and all(abs(rb_[n]["efficiency"] - 0.82) < 1e-9 for n in ("+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC")))
        bare = os.path.join(d, "bare_gen_sch_a.py")
        shutil.copy(D.GEN["a"], bare)
        r_bare = subprocess.run([sys.executable, "-B", SET % "a", bare, "--write"], capture_output=True)
        r_again = subprocess.run([sys.executable, "-B", SET % "a", D.GEN["a"], "--write"], capture_output=True)
    out["p22"].update(v_set=v_set, v_m1=v_m1, v_m2=v_m2, decl_ok=decl_ok, ok=res["a"][0] and res["b"][0],
                      tree_refused=r_again.returncode == 3 and r_bare.returncode == 3)
    w("   the delta composed straight after iocpre (board A %d drafts, board B %d): %s; the generators ran to their end; a generator without" % (
        res["a"][3], res["b"][3], "every step OK" if out["p22"]["ok"] else "REFUSED"))
    w("     iocpre %s, the tree's generator %s" % ("refused" if r_bare.returncode == 3 else "NOT REFUSED", "refused" if r_again.returncode == 3 else "NOT REFUSED"))
    w("     read on board A's netlist: the set point %s; mutations: the divider inverted %s, R602 back to 13.3k %s; the declarations read +5V_IOC" % (
        v_set, v_m1, v_m2))
    w("     4.01 V on both boards (v_work %.2f V) and each +3V3_IOCx at efficiency 0.82: %s. Record l9t5's own pre-regulator check (Slot A's" % (
        ra_["+5V_IOC"]["v_work"], "yes" if decl_ok else "NO"))
    w("     check_l9t5_netlist.py) holds the 13.3k divider: its 't10' entry is Slot A's to restate when it takes this delta (L9T5-F24)")
    # C: the revision made enforceable
    w("   THE FITTED REVISION MADE ENFORCEABLE (part 22, C): three rows drafted for their owners, none applied (T10-ROUND5.md section 3):")
    w("     Layer 6 (part identity, STM32H743-COMPATIBILITY.md F1 and the BOM line of U41, U51, U61): STM32H743VIT6, LCSC C114409, SILICON REVISION")
    w("       V ONLY (package marking revision code 'V', DBGMCU_IDC REV_ID 0x2003; ES0392 Rev 15 Table 2); X and Y not accepted; reason L9T5-D7")
    w("       (this record's 10h and 10i); acceptance: the BOM line and the compatibility page name revision V")
    w("     Layer 12 (incoming inspection and first article): every supervisor's package read for revision code 'V' before assembly, a lot with")
    w("       any other code held; at first power each supervisor's REV_ID read over SWD equal to 0x2003; reason and acceptance as above")
    w("     the model's case selection (this script): the verdicts of F13, F16, F17 and the rows above read revision %s's printed rows only;" % FITTED_REV)
    w("       revision %s's rows are printed as the cover for a rev X part and decide nothing; no figure of revision %s is applied to X or Y" % (
        COVER_REV, FITTED_REV))
    w("")
    return out


EN_DASH = chr(0x2013)       # the sheets' minus sign, written by its code point (no long dash in this file)
GUARD_B = os.path.join(HERE, "apply_gen_sch_b_iocguard.py")   # T10 round 6 (the check cx45's Q3): the share limiters and the rail trips
RS_TRIP, RL_TRIP, RF_TRIP, CF_TRIP = 0.3, 5.76e3, 100e3, 10e-6   # read back from the draft below, never used unread
FRAME_D_MIN = 0.15         # ASSUMED: the least dominant fraction of back-to-back classic frames from a CAN controller (SOF, the reserved and
                           # stuff bits; an all-recessive 8-byte frame carries about 26 dominant bits in 133): a babbler through its FDCAN
                           # holds the limiter's input at or under 1 - 0.15 of the rail


def guard_values():
    """The draft's values, read from its module (never typed): the rail trip and the limiter."""
    sp = importlib.util.spec_from_file_location("t10_guard_values", GUARD_B)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    rt, lm = dict(m.RAIL_TRIP), dict(m.LIMITER)
    f = lambda v: float(re.match(r"([\d.]+)", v).group(1)) * {"k": 1e3, "M": 1e6, "R": 1.0, "u": 1e-6, "n": 1e-9}[re.match(r"[\d.]+([kMRun])", v).group(1)]
    return dict(rs=f(rt["rs"]), rl=f(rt["rl"]), rf=f(rt["rf"]), cf=f(rt["cf"]), r1=f(lm["r1"]), r2=f(lm["r2"]), c=f(lm["c"]), rpu=f(lm["rpu"]),
                rsd=f(lm["rsd"]), amp=rt["amp"], cmp=rt["cmp"], edits=len(m.EDITS), tol_l=0.001 if "0.1%" in lm["r2"] else 0.01)


def guard_sheets():
    """INA169 (SBOS181F) and TPS3701 (SBVS240C), both held back (v2/docs/records/l4e7/fetch_held_back.py), and the TCAN334's SHDN rows."""
    a, t, c = pdf("ina169"), pdf("tps3701"), pdf("tcan")
    S = {}
    m = need(a, r"VSENSE = 10 mV %s 150 mV\s+(\d+)\s+(\d+)\s+(\d+)\s+µA/V" % EN_DASH, "INA169: the transconductance")
    S["gm"] = tuple(float(m.group(k)) * 1e-6 for k in (1, 2, 3))
    S["vos"] = float(need(a, r"INA169\s+±0\.2\s+±(\d+(?:\.\d+)?)\s*\n\s*vs\. temperature", "INA169: the offset").group(1)) * 1e-3
    S["ta_hi"] = float(need(a, r"INA169: all other characteristics at TA = %s40°C to \+(\d+)°C" % EN_DASH, "INA169: its temperature range").group(1))
    m = need(t, r"VIT%s\(INB\)\s+INB pin negative input threshold voltage VDD = 1\.8 V to 36 V\s+(\d+)\s+([\d.]+)\s+(\d+)\s+mV" % EN_DASH, "TPS3701: VIT-(INB)")
    S["vtm"] = (float(m.group(1)) * 1e-3, float(m.group(3)) * 1e-3)
    m = need(t, r"VIT\+\(INB\)\s+INB pin positive input threshold voltage\s+VDD = 1\.8 V to 36 V\s+(\d+)\s+([\d.]+)\s+(\d+)\s+mV", "TPS3701: VIT+(INB)")
    S["vtp"] = (float(m.group(1)) * 1e-3, float(m.group(3)) * 1e-3)
    m = need(t, r"VDD = 1\.8 V and 36 V, VINA, VINB = 6\.5 V\s+%s(\d+)\s+\+1\s+\+(\d+)\s+nA" % EN_DASH, "TPS3701: IIN")
    S["iin"] = float(m.group(2)) * 1e-9
    need(t, r"exceeds the threshold voltage\s*\n\s*VIT\+\(INB\), OUTB is driven low\.", "TPS3701: OUTB's polarity")
    S["vih"] = float(need(c, r"VIH\s+HIGH level input voltage\s+(\d+(?:\.\d+)?)\s+V", "TCAN334: VIH").group(1))
    S["iil"] = float(need(c, r"IIL\s+LOW level input leakage current\s+STB, S, SHDN = 0V, VCC = 3\.6V\s+%s(\d+)" % EN_DASH, "TCAN334: SHDN's IIL").group(1)) * 1e-6
    S["vil"] = float(need(c, r"VIL\s+LOW level input voltage\s+(\d+(?:\.\d+)?)\s+V", "TCAN334: VIL").group(1))
    return S


def guard_check(nl):
    """The containment delta read on a board B netlist by pin. Returns (verdict, why)."""
    why = []
    for tag, k in (("A", 0), ("B", 1), ("C", 2)):
        b = 40 + 10 * k
        U = lambda n: "U%d" % (b + n)
        GR = lambda n: "R%d" % (600 + 20 * k + n)
        GC = lambda n: "C%d" % (940 + 10 * k + n)
        GD = lambda n: "D%d" % (400 + 10 * k + n)
        ldo_in, en, isns, isf, v33 = "IOC%s_LDO_IN" % tag, "IOC%s_LDO_EN" % tag, "IOC%s_ISNS" % tag, "IOC%s_ISF" % tag, "+3V3_IOC%s" % tag
        why += CHK.rows(nl, [(U(0), "1", ldo_in), (U(0), "3", en), (GR(0), "1", "+5V_IOC"), (GR(0), "2", ldo_in),
                             (U(5), "1", isns), (U(5), "2", "GND"), (U(5), "3", "+5V_IOC"), (U(5), "4", ldo_in), (U(5), "5", "+5V_IOC"),
                             (GR(1), "1", isns), (GR(1), "2", "GND"), (GR(2), "1", isns), (GR(2), "2", isf), (GC(1), "1", isf), (GC(1), "2", "GND"),
                             (U(6), "2", "GND"), (U(6), "4", isf), (U(6), "5", "+5V_IOC"), (U(6), "6", en)])
        if not CHK.value(nl, U(5)).startswith("INA169") or not CHK.value(nl, U(6)).startswith("TPS3701"):
            why.append("%s/%s are %r/%r, not the INA169 and the TPS3701" % (U(5), U(6), CHK.value(nl, U(5))[:20], CHK.value(nl, U(6))[:20]))
        if not CHK.value(nl, GR(0)).startswith("0.3R") or not CHK.value(nl, GR(1)).startswith("5.76k"):
            why.append("%s %r and %s %r are not the 0.3 ohm sense and 5.76 kOhm output resistors" % (GR(0), CHK.value(nl, GR(0)), GR(1), CHK.value(nl, GR(1))))
        if set(r.split(".")[0] for r in CHK.members(nl, ldo_in)) != {U(0), GR(0), U(5), "C%d" % (400 + 20 * k)}:
            why.append("%s reaches %s, not the LDO, the sense resistor, the monitor and the LDO's input capacitor" % (ldo_in, CHK.members(nl, ldo_in)))
        if "%s.6" % U(6) not in CHK.members(nl, en):
            why.append("the rail trip's OUTB is not on %s" % en)
        for j, (can, un) in enumerate((("1", 3), ("2", 4))):
            sd, lim, lo = "IOC%s_CAN%s_SD" % (tag, can), "IOC%s_CAN%s_LIM" % (tag, can), "IOC%s_CAN%s_LIMO" % (tag, can)
            tx, gpio = "IOC%s_CAN%s_TX" % (tag, can), "IOC%s_CAN%s_SHDN" % (tag, can)
            why += CHK.rows(nl, [(U(un), "5", sd), (GD(2 * j), "1", sd), (GD(2 * j), "2", gpio), (GD(2 * j + 1), "1", sd), (GD(2 * j + 1), "2", lo),
                                 (GR(3 + 4 * j), "1", sd), (GR(3 + 4 * j), "2", "GND"), (GR(4 + 4 * j), "1", tx), (GR(4 + 4 * j), "2", lim),
                                 (GR(5 + 4 * j), "1", lim), (GR(5 + 4 * j), "2", "GND"), (GC(3 + 2 * j), "1", lim), (GC(3 + 2 * j), "2", "GND"),
                                 (U(7 + j), "2", "GND"), (U(7 + j), "4", lim), (U(7 + j), "5", "+5V_IOC"), (U(7 + j), "6", lo),
                                 (GR(6 + 4 * j), "1", v33), (GR(6 + 4 * j), "2", lo)])
            if sorted(CHK.members(nl, sd)) != sorted(["%s.5" % U(un), "%s.1" % GD(2 * j), "%s.1" % GD(2 * j + 1), "%s.1" % GR(3 + 4 * j)]):
                why.append("%s reaches %s" % (sd, CHK.members(nl, sd)))
            if not CHK.value(nl, U(7 + j)).startswith("TPS3701") or not CHK.value(nl, GR(5 + 4 * j)).startswith("150k 0.1%"):
                why.append("controller %s fabric %s's limiter is %r with %r" % (tag, can, CHK.value(nl, U(7 + j))[:16], CHK.value(nl, GR(5 + 4 * j))))
    return ("FAIL" if why else "DRAWN"), why


def round6_cx45(w, P, DP, air, hi3, Q, tj_l, out):
    """10j: the check cx45's Q3 (a) to (d) on T10: the message schedule, the containment drafted (the transmit-share limiter and the rail
    trip, apply_gen_sch_b_iocguard.py), the surviving quorum per fault, the other controllers' headroom, the thermal envelope with its
    qualification limits, and every row made to agree on revision V and the 14.0k set point."""
    GV, GS = guard_values(), guard_sheets()
    i_aux, p22 = out["i_aux"], out["p22"]
    lo14, nom14, hi14 = CHK.vout_band(R601, R602_SET)
    k14 = p22["k14"]                                                    # K/A at the drop's worst corner (14.0k)
    drop14 = hi14 - 3.3 * P["vout_lo"]
    b_v = out["B"][(FITTED_REV, air)]
    fr = {r[0]: r for r in out["fault_rows"][FITTED_REV]}
    i_rec, i_dom = P["can_rec"], P["can_dom_hi"]
    # (a) the schedule: per controller and fabric in each 100 ms window one state frame and at most five event frames
    bits, n_frames, acks = FRAME_BITS, 6, 2 * 6
    dom_bound = n_frames * bits + acks
    budget = {r: SHARE * WINDOW_MS * 1e-3 * r for r in (500e3, 1e6)}
    load = 3 * n_frames * bits / (500e3 * WINDOW_MS * 1e-3)
    lat = (3 * n_frames - 1) * bits / 500e3
    # the share limiter: its threshold in dominant share, its detection and its release
    k_nom = GV["r2"] / (GV["r1"] + GV["r2"])
    tl = GV["tol_l"]
    k_lo = GV["r2"] * (1 - tl) / (GV["r1"] * (1 + tl) + GV["r2"] * (1 - tl))
    k_hi = GV["r2"] * (1 + tl) / (GV["r1"] * (1 - tl) + GV["r2"] * (1 + tl))
    rpar_hi = GV["r1"] * (1 + tl) * GV["r2"] * (1 + tl) / (GV["r1"] * (1 + tl) + GV["r2"] * (1 + tl))
    v33 = (3.3 * P["vout_lo"], 3.3 * P["vout_hi"])
    e_iin = GS["iin"] * rpar_hi
    d_lo = 1.0 - (GS["vtm"][1] + e_iin) / (v33[0] * k_lo)               # the earliest trip
    d_hi = 1.0 - (GS["vtm"][0] - e_iin) / (v33[1] * k_hi)               # the latest
    rel_ok = (1.0 - SHARE) * v33[0] * k_lo - e_iin > GS["vtp"][1]       # the legitimate 2 % share leaves the transceiver enabled
    tau_l = GV["c"] * 1.1 * rpar_hi
    v0 = (1.0 - SHARE) * v33[1] * k_hi
    t_held = tau_l * math.log(v0 / (GS["vtm"][0] - e_iin))              # a held-dominant TXD from the legitimate share
    # a controller-driven babbler (back-to-back frames, at least FRAME_D_MIN dominant): its average falls toward (1 - FRAME_D_MIN)
    t_bab = tau_l * math.log((FRAME_D_MIN - SHARE) / (FRAME_D_MIN - d_hi)) if FRAME_D_MIN > d_hi else float("inf")
    sd_trip = (v33[0] - GV["rpu"] * GS["iil"] - 0.715) * GV["rsd"] / (GV["rsd"] + GV["rpu"])    # LIMO pulled up through the diode into 100k
    sd_low = GS["iil"] * GV["rsd"]                                       # the pin's own leakage into 100k with nothing driving it
    i_lim_pu = 2 * v33[1] / (GV["rpu"] * 0.99)                           # two LIMO pull-ups sunk by OUTB in normal service, from the rail
    i_tx_lim = i_rec + (i_dom - i_rec) * d_hi                            # a transceiver's average at the limiter's latest share
    i_bab6 = b_v[2] + i_lim_pu + 2 * (i_tx_lim - (i_rec + (i_dom - i_rec) * SHARE))   # the babbler bounded by the limiters
    # the rail trip: the trip current's window from the printed rows (resistors 1 %)
    vt = GS["vtp"]
    i_max = (vt[1] / (GS["gm"][0] * GV["rl"] * 0.99) + GS["vos"]) / (GV["rs"] * 0.99) + GS["iin"] * GV["rf"] * 1.01 / (GS["gm"][0] * GV["rl"] * 0.99 * GV["rs"] * 0.99)
    i_min = (vt[0] / (GS["gm"][2] * GV["rl"] * 1.01) - GS["vos"]) / (GV["rs"] * 1.01) - GS["iin"] * GV["rf"] * 1.01 / (GS["gm"][2] * GV["rl"] * 1.01 * GV["rs"] * 1.01)
    tau_t = (GV["rf"] + GV["rl"]) * 1.01 * GV["cf"] * 1.1               # the charging path is RL + RF (the check cx46's finding 6)
    serve = [("the bounded state with the limiters' pull-ups", b_v[2] + i_lim_pu)] + [("%s with the response" % f, fr[f][3] + i_lim_pu) for f in ("B1", "B2", "B3", "B4", "B5", "B6", "B7a")] \
        + [("both fabrics faulted, responded", out["both"][FITTED_REV][0] + i_lim_pu), ("a babbler, the limiters bounding it", i_bab6)]
    serve_max = max(i for _l, i in serve)
    tj_hold = air + k14 * i_max
    tj_mcu = air + P["theta_mcu"] * 3.3 * i_max
    air_125 = TJ_GOAL - k14 * i_max
    theta_125 = (TJ_GOAL - air) / (drop14 * i_max)
    # the worst current any firmware can draw: the sheet's largest rev V row, the auxiliaries and both transceivers held dominant
    i_mcu_max = max(v[3] for v in P["V"].values() if v[3] is not None) / 1000.0
    i_any = i_mcu_max + i_aux + 2 * i_dom + i_lim_pu
    t_trip = tau_t * math.log((i_any - b_v[2]) / (i_any - i_max))
    t_vb23 = tau_t * math.log((0.30 - (b_v[2] + i_lim_pu)) / (0.30 - i_max))   # V-B23's step from the bounded state to 0.30 A (cx46 6)
    # the check cx46's periodic countermodel, reproduced on its own ASSUMPTIONS (finding 7): 0.50 A for 0.40 s every 1.50 s (0 A between),
    # a single thermal pole of 184 K/W and 0.25 s, 0.020 V of extra feed and return drop, the drafted 0.30 ohm sense resistor
    cm_i, cm_on, cm_per, cm_tau, cm_drop = 0.50, 0.40, 1.50, 0.25, 0.020
    cm_p = (drop14 - cm_drop - GV["rs"] * cm_i) * cm_i
    cm_tj = air + P["theta_ldo"] * cm_p * (1 - math.exp(-cm_on / cm_tau)) / (1 - math.exp(-cm_per / cm_tau))
    cm_f = cm_i * (1 - math.exp(-cm_on / 1.0)) / (1 - math.exp(-cm_per / 1.0))
    cm_z = P["theta_ldo"] * (1 - math.exp(-0.171 / cm_tau))
    p0, pf = drop14 * b_v[2], drop14 * i_any
    tj0 = air + P["theta_ldo"] * p0
    zth_need = (P["tj_ldo"] - tj0) / (pf - p0)
    # T10-A3 at the trip's maximum, the sense resistor's drop counted
    G = D.gndret()
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    def need_at(i):
        drop_i = P["drop"][10] + (P["drop"][300] - P["drop"][10]) * (i - 0.01) / 0.29 if i <= 0.3 else P["drop"][300] + (P["drop"][600] - P["drop"][300]) * (i - 0.3) / 0.3
        return 3.3 * (P["vout_hi"] + P["load"] * i) + drop_i
    at_trip = lo14 - D.RAIL_BUDGET * nom14 - 3 * i_max * r_sup - G["shift_drawn_ub"] - GV["rs"] * 1.01 * i_max
    # the other controllers' inputs while one draws the worst current until its trip
    i_tot = i_any + 2 * serve_max
    at_other = lo14 - D.RAIL_BUDGET * nom14 - i_tot * r_sup - G["shift_drawn_ub"] - GV["rs"] * 1.01 * serve_max
    R6 = dict(cm=(cm_p, cm_tj, cm_f, cm_z), t_vb23=t_vb23, d=(d_lo, d_hi), rel_ok=rel_ok, t_held=t_held, t_bab=t_bab, sd=(sd_trip, sd_low), win=(i_min, i_max), serve_max=serve_max, tj_hold=tj_hold,
              tj_mcu=tj_mcu, t_trip=t_trip, zth=zth_need, a3=(need_at(i_max), at_trip), other=(need_at(serve_max), at_other), dom=(dom_bound, budget[500e3]),
              i_bab6=i_bab6, air_125=air_125, theta_125=theta_125)
    w("   10j. THE CHECK cx45's Q3 (focused check of candidate 06077cee, NOT CONFIRMED) AND ITS RECHECK cx46 (of 4d0ff8a2: CORRECTIONS NOT CLOSED,")
    w("   the second negative: the method ends; this section is the DISPOSITION, text and predicates, no new design): THE SCHEDULE, THE")
    w("   CONTAINMENT DRAFTED, THE QUORUM, THE HEADROOM, THE THERMAL ENVELOPE, THE ROWS (DERIVED on the printed rows; labels as above). Every")
    w("   claim below is OPEN or PROVISIONAL; nothing in it is closed; what each handed-over case weakens is said at the claim")
    w("   (a) THE MESSAGE SCHEDULE, FW-B22 (drafted in apply_hw_fw_contract_t10.py): per controller and fabric, in every %d ms window, one state" % WINDOW_MS)
    w("     frame (its view of the assignment, its health, a sequence count) and at most five event frames; classic 8-byte frames at 500 kbit/s")
    w("     or 1 Mbit/s, %d bit-times each with stuffing (MODEL); a larger change spreads over windows. Its dominant bound, every bit counted" % bits)
    w("     dominant plus %d acknowledgements: %d bit-times against FW-B21's %.0f (2 %% of the window at 500 kbit/s; %.0f at 1 Mbit/s): inside;" % (
        acks, dom_bound, budget[500e3], budget[1e6]))
    w("     the bus %.1f %% loaded at 500 kbit/s; a state frame waits at most %.1f ms behind every other frame of its window; the quorum's" % (100 * load, lat * 1e3))
    w("     2-of-3 decision reads the three state frames of one window: at most %d ms plus %.1f ms" % (WINDOW_MS, lat * 1e3))
    w("     PROVISIONAL (cx46 5): this establishes the traffic MODEL, not a fault-contained quorum service: a TX pin toggled as a GPIO under the")
    w("     limiter's share and a latent stuck comparator are admitted counterexamples (L9T5-F21 weakens FW-B22 and CON-004's quorum)")
    w("   (b) THE CONTAINMENT DRAFTED (apply_gen_sch_b_iocguard.py, after iocbuck, iocpre and canshdn; NOT APPLIED): two bounds that no firmware")
    w("     sets, each acting on one controller only; the rows read (PRINTED): INA169 %.0f to %.0f uA/V, offset at most %.1f mV, specified to %.0f C;" % (
        GS["gm"][0] * 1e6, GS["gm"][2] * 1e6, GS["vos"] * 1e3, GS["ta_hi"]))
    w("     TPS3701 VIT-(INB) %.0f to %.0f mV, VIT+(INB) %.0f to %.0f mV, its inputs at most %.0f nA, OUTB low over VIT+(INB); TCAN334 SHDN VIH %.0f V, VIL" % (
        GS["vtm"][0] * 1e3, GS["vtm"][1] * 1e3, GS["vtp"][0] * 1e3, GS["vtp"][1] * 1e3, GS["iin"] * 1e9, GS["vih"]))
    w("     %.1f V, at most %.0f uA out of the pin at 0 V" % (GS["vil"], GS["iil"] * 1e6))
    w("     the response times below are MODEL figures without the comparator's own delay (SBVS240C prints its propagation and start-up delays")
    w("     TYPICAL only), with TXD's high level taken as the rail and the frames' least dominant fraction an ASSUMPTION: not maxima")
    w("     1. THE TRANSMIT-SHARE LIMITER, one per transceiver: TXD through %.0f kOhm over %.0f kOhm with %.0f uF (%.0f ms at its slowest), the" % (
        GV["r1"] / 1e3, GV["r2"] / 1e3, GV["c"] * 1e6, tau_l * 1e3))
    w("        average %.4f of the rail times (1 - the dominant share); the transceiver is silenced when its share passes %.1f to %.1f %% (the" % (k_nom, 100 * d_lo, 100 * d_hi))
    w("        rail at +-1.5 %%, the resistors at %.1f %%, the threshold and the input current printed); at the legitimate 2 %% it stays enabled: %s;" % (
        100 * GV["tol_l"], "yes" if rel_ok else "NO"))
    w("        SHDN driven to at least %.2f V (VIH %.0f V) by LIMO's %.0f kOhm through a 1N4148W (0.715 V PRINTED at 1 mA, taken as the bound) into %.0f kOhm," % (
        sd_trip, GS["vih"], GV["rpu"] / 1e3, GV["rsd"] / 1e3))
    w("        and held at %.2f V (VIL %.1f V) by that %.0f kOhm against the pin's own %.0f uA when nothing drives it; the controller's own SHDN" % (
        sd_low, GS["vil"], GV["rsd"] / 1e3, GS["iil"] * 1e6))
    w("        request reaches the pin through the other diode. A held-dominant TXD is silenced within %.1f ms (the driver's own time-out, %.1f to" % (
        t_held * 1e3, P["can_dto"][0]))
    w("        %.1f ms PRINTED, frees the bus first); a babbler through its FDCAN, whose frames carry at least %.0f %% dominant bits (ASSUMED,"
      % (P["can_dto"][2], 100 * FRAME_D_MIN))
    w("        FRAME_D_MIN: an all-recessive 8-byte frame carries about 24 dominant bits in 130), within %.0f ms; the silence lasts while its" % (t_bab * 1e3))
    w("        TXD keeps the share over the limit and ends by itself when the share falls. A latent stuck comparator (OUTB held low) leaves that")
    w("        transceiver's share unbounded with nothing to find it in service: it weakens the service's containment (PROVISIONAL)")
    w("     2. THE RAIL TRIP, one per controller: %.1f ohm from +5V_IOC to its LDO, the INA169 into %.2f kOhm, a %.2f s average (%.2f + %.0f kOhm" % (
        GV["rs"], GV["rl"] / 1e3, tau_t, GV["rl"] / 1e3, GV["rf"] / 1e3))
    w("        in the charging path, %.0f uF," % (GV["cf"] * 1e6))
    w("        at its slowest), a TPS3701 holding the LDO's EN low while the average is over the threshold: %.4f to %.4f A at the tolerances;" % (i_min, i_max))
    w("        tripped, the controller is unpowered; the average then falls, the LDO restarts, and a controller still over the threshold is")
    w("        unpowered again: its supply's AVERAGE is held at the threshold (DERIVED); its peak is not (e). A latent rail trip (its monitor")
    w("        dead, its OUTB released) removes even that average bound with nothing to find it in service (PROVISIONAL)")
    w("        V-B23's response, as round 6 drafted it (EN low within 0.2 s of a 0.30 A load), is WITHDRAWN (cx46 6): from the bounded state the")
    w("        drafted network reaches the trip's maximum after %.2f s (MODEL, the comparator's delay not counted); a corrected response mechanism" % t_vb23)
    w("        and the complete network calculation are REMAINING ENGINEERING, protection not relaxed to obtain a pass")
    w("   (c) THE QUORUM AND RECOVERY, FAULT BY FAULT (quorum: two of three controllers serving; IOHA rows 3, 7 and 8), PROVISIONAL (cx46 5):")
    rows_q = (("a babbler through its FDCAN (FW-B21 broken), one or both fabrics", "its limiter silences its transceiver within %.0f ms; the bus free; the other two" % (t_bab * 1e3),
               "automatic: the limiter releases when its share falls"),
              ("a held-dominant TXD", "the time-out frees the bus within %.1f ms, the limiter silences it within %.1f ms" % (P["can_dto"][2], t_held * 1e3), "automatic"),
              ("a clock or load outside FW-B20 (any firmware)", "the rail trip unpowers it, its average held at %.4f A or less; the other two" % i_max,
               "automatic: it restarts while its average is under the trip"),
              ("a fabric shorted, the firmware's response absent", "its transceivers' share bounded by the limiter, the rail under the trip; the other fabric", "the fabric's repair"),
              ("a limiter's comparator dead, or its OUTB released", "that transceiver silent: the controller on its other fabric; the quorum holds", "found at once (its frames absent)"),
              ("a limiter's OUTB stuck low", "that transceiver's share no longer bounded: LATENT, a second fault (a babbler) needed", "bench V-B22; handed over (below)"),
              ("the rail trip's OUTB stuck low, or its monitor's output high", "the controller unpowered: the other two", "found at once"),
              ("the rail trip's monitor dead or its OUTB released", "no current bound for that controller: LATENT, a second fault needed", "bench V-B23; handed over (below)"),
              ("one firmware fault in all three (a systematic fault)", "each rail and each transceiver bounded on its own; the service may stop: the voters hold the home assignment (row 8)", "the firmware's V-B20 to V-B22"))
    for a_, b_, c_ in rows_q:
        w("     %-62s %-118s %s" % (a_, b_, c_))
    w("     a CONTROLLER-DRIVEN babbler denies the bus at most for its detection time, %.0f ms, the voters holding their assignment meanwhile" % (t_bab * 1e3))
    w("     (row 8), because its frames' dominant bits keep its share over the limit;")
    w("     WHAT IS NOT CLOSED (handed over as remaining engineering, no exception presumed): a TX pin repurposed as a GPIO and toggled under")
    w("     the limiter's least %.1f %% share disrupts the bus without tripping it; attributing it needs each controller's TXD read by the other" % (100 * d_lo))
    w("     two and a 2-of-2 vote of the other two on its SHDN or its LDO's EN (twelve observation inputs and six vote outputs, a pin plan for")
    w("     the three H743s): NOT DRAFTED here. And a latent stuck comparator in either bound, found only on the bench (V-B22, V-B23), with")
    w("     no service interval bounding that: the double faults. Outputs OPEN or PROVISIONAL on them: CON-004's quorum verdict (OPEN), FW-B22")
    w("     (PROVISIONAL), L9T5-F21 (OPEN) and this section's quorum rows. REMAINING ENGINEERING: an independent peer-silence or diagnostic")
    w("     circuit and the recovery proof. VOS0 under the trip takes the controller past its own 105 C VOS0 limit from %.4f A (MODEL), under" % (
        (105.0 - air) / (P["theta_mcu"] * 3.3)))
    w("     the trip's band: it weakens the controller's survival and so FW-B20's and FW-B22's service (PROVISIONAL)")
    w("   (d) THE OTHER CONTROLLERS' HEADROOM DURING A RESPONSE: one controller at the worst current any firmware draws until its trip, %.4f A" % i_any)
    w("     (the sheet's largest rev V row %.3f A, the auxiliaries, both transceivers held dominant), the other two at the largest served %.4f A:" % (i_mcu_max, serve_max))
    w("     U601's load %.4f A, under its declared peak; each other LDO's input at least %.4f V against its %.4f V: %s (the lead at the" % (
        i_tot, at_other, need_at(serve_max), "holds" if at_other >= need_at(serve_max) else "FAILS"))
    w("     total current, the return's shift as drawn, the sense resistor at +1 %)")
    w("     T10-A3 at the trip's AVERAGE maximum (L9T5-D8's criterion superseded; PROVISIONAL: a periodic load's peak above it is not covered,")
    w("     (e)): each LDO's input at %.4f A, the sense" % i_max)
    w("     resistor's drop counted: at least %.4f V against %.4f V: %s" % (at_trip, need_at(i_max), "holds" if at_trip >= need_at(i_max) else "FAILS"))
    w("   (e) THE THERMAL ENVELOPE, PEAK AND SUSTAINED (cx45's averaged-current point; cx46 7: NOT CLOSED, PROVISIONAL):")
    w("     a constant current at the trip's average maximum %.4f A reads the LDO's junction %.1f C at %.2f C air (the drop's worst corner, %.1f" % (
        i_max, tj_hold, air, k14))
    w("       K/A, MODEL) and the controller's %.1f C; that is a constant-current MODEL, not a bound: the trip holds an AVERAGE, and a periodic" % tj_mcu)
    w("       load under it heats more. The check cx46's countermodel, reproduced on its ASSUMPTIONS (%.2f A for %.2f s every %.2f s, a single" % (
        cm_i, cm_on, cm_per))
    w("       thermal pole of %.0f K/W and %.2f s, %.3f V of extra drop, the 0.3 ohm sense): %.4f W in the pulse, the filtered current's peak" % (
        P["theta_ldo"], cm_tau, cm_drop, cm_p))
    w("       %.4f A (under the trip's least %.4f A), Zth(171 ms) %.1f K/W (inside the about 105 K/W proposed below), and the junction's periodic peak" % (
        cm_f, i_min, cm_z))
    w("       %.2f C, OVER 125 C: the universal sustained bound and its positive margin are WITHDRAWN; peak-current containment or a complete" % cm_tj)
    w("       periodic electrothermal solution with uncertainty is REMAINING ENGINEERING. A latent rail trip removes even the average bound")
    w("     Every served state is under the trip's least %.4f A (the largest" % i_min)
    w("       %.4f A): %s" % (serve_max, "none trips" if serve_max < i_min else "ONE TRIPS"))
    for lab, i in serve:
        w("         %-52s %.4f A   LDO %.1f C" % (lab, i, air + k14 * i))
    w("     transient: from the bounded state to the worst current, the trip acts within %.0f ms (the average's slowest time constant); the" % (t_trip * 1e3))
    w("       steady figure at that current is %.1f C, so the 150 C transient rule needs the LDO's transient thermal impedance at %.0f ms no" % (
        air + P["theta_ldo"] * pf, t_trip * 1e3))
    w("       more than %.0f C/W on board B's copper (its steady %.0f C/W PRINTED for its own board): NOT PRINTED by Diodes, a QUALIFICATION LIMIT" % (
        zth_need, P["theta_ldo"]))
    w("       (first article, below); the controller passes its own rating in that time at VOS0 (a firmware fault, ended by the trip)")
    w("     the qualification limits below are measurements to take, NOT an acceptance of the sustained bound (cx46 7: the countermodel meets")
    w("     them and passes 125 C): the LDO's junction-to-air resistance on board B at most %.0f C/W at %.2f C air, or" % (theta_125, air))
    w("       the local air at most %.1f C at the printed %.0f C/W (each holds 125 C at the trip's maximum); Zth(%.0f ms) at most %.0f C/W;" % (
        air_125, P["theta_ldo"], t_trip * 1e3, zth_need))
    w("       the INA169's site under its specified %.0f C; measured on the first article of board B in a %.0f C chamber with one controller" % (GS["ta_hi"], air))
    w("       forced to the trip (a load on its rail), not at the bounded state alone (T10-A5 restated, T10-ROUND5.md section 6)")
    w("     residual handed over: VOS0 at a current under the trip takes the H743 past its own %d C VOS0 limit at this air (%.1f C at %.4f A):" % (105, tj_mcu, i_max))
    w("       the LDO is held, the controller is not; a VOS0 entry no hardware prevents (Layer 5 and Layer 6)")
    w("   (f) THE ROWS MADE TO AGREE: every procurement, contract and inspection instruction points to revision V (L9T5-D7), the final set point")
    w("     R602 14.0k (4.0114 V nominal) and 125 C for every sustained state; revision X is HELD with no admission route (round 5's V-B20 route")
    w("     at 0.2318 A and L9T5-F22's 'admits any revision' are SUPERSEDED); a rev X part's admission, its own qualification, and the sustained")
    w("     thermal acceptance it would rest on are REMAINING ENGINEERING ((e)); the rail trip's least %.4f A is a drafted circuit's figure," % i_min)
    w("     not a qualification limit")
    with tempfile.TemporaryDirectory(prefix="l9t5_t10r6_") as d:
        seq = D.seq_of("b", "slot")
        at = seq.index(D.MINE["b"]) + 1
        seq6 = seq[:at] + [PRE["b"], SHDN, SET % "b", GUARD_B] + seq[at:]
        p6, res6, ok6 = D.compose("b", seq6, d, "t10r6")
        rc6, net6, _t6 = D.netlist("b", p6, d, "t10r6")
        if rc6 or not ok6:
            refuse("board B with the containment delta did not compose or regenerate: %s" % net6)
        nl6 = CHK.read(open(net6, "rb").read())
        v6, why6 = guard_check(nl6)
        muts = (("the limiter reading RXD, not TXD", [(("R604", "1"), ("U43", "4"))]),
                ("the rail trip's EN and its input exchanged", [(("U46", "6"), ("U46", "4"))]),
                ("the LDO before the sense resistor", [(("U40", "1"), ("R600", "1"))]),
                ("the limiter's pull-up from +5V_IOC", [(("R606", "1"), ("U47", "5"))]),
                ("the controller's SHDN diode reversed", [(("D400", "1"), ("D400", "2"))]),
                ("the filter capacitor reversed onto ground", [(("C941", "1"), ("C941", "2"))]))
        vm = []
        for i, (lab, sw) in enumerate(muts):
            q = D.mutate(net6, d, "r6m%d" % i, sw)
            vm.append((lab, guard_check(CHK.read(open(q, "rb").read()))[0]))
        bare = os.path.join(d, "bare_gen_sch_b.py")
        shutil.copy(D.GEN["b"], bare)
        r_bare = subprocess.run([sys.executable, "-B", GUARD_B, bare, "--write"], capture_output=True)
        r_tree = subprocess.run([sys.executable, "-B", GUARD_B, D.GEN["b"], "--write"], capture_output=True)
        r_twice = subprocess.run([sys.executable, "-B", GUARD_B, p6, "--write"], capture_output=True)
    R6.update(v6=v6, why6=why6, vm=vm, ok6=ok6, refused=(r_bare.returncode == 3, r_tree.returncode == 3 and b"NOT RELEASED" in r_tree.stderr, r_twice.returncode == 3))
    w("   COMPOSED: board B in L4-E9's order with I-03's draft, iocpre, canshdn, iocset and the containment delta (%d drafts): %s; the generator" % (
        len(seq6), "every step OK" if ok6 else "REFUSED"))
    w("     ran to its end; read by pin (each rail's sense, monitor, filter and trip on its EN; each transceiver's SD, diodes, average and")
    w("     limiter): %s%s" % (v6, (": " + "; ".join(why6[:3])) if why6 else ""))
    for lab, v in vm:
        w("     mutated, %-48s %s" % (lab + ":", v))
    w("     the delta on a generator without record l9t5's drafts: %s; a second time: %s; on the tree's own generator: %s" % (
        "refused" if R6["refused"][0] else "NOT REFUSED", "refused" if R6["refused"][2] else "NOT REFUSED", "refused (NOT RELEASED)" if R6["refused"][1] else "NOT REFUSED"))
    w("     record l9t5's own I-03 check (Slot A's check_l9t5_netlist.py) holds the LDOs' VIN on +5V_IOC: its entry is Slot A's to restate when")
    w("     it takes this delta (L9T5-F25)")
    ok = (rel_ok and d_lo > SHARE and d_hi < FRAME_D_MIN and t_held < 0.1 and sd_trip > GS["vih"] and sd_low < GS["vil"] and serve_max < i_min and tj_hold <= TJ_GOAL
          and at_trip >= need_at(i_max) and at_other >= need_at(serve_max) and dom_bound <= budget[500e3] and v6 == "DRAWN"
          and all(v == "FAIL" for _l, v in vm) and all(R6["refused"]) and ok6)
    R6["ok"] = ok
    w("   DISPOSITION (10j, after cx46): cx45's Q3 NOT CLOSED. Drafted and reproducible: FW-B22's traffic MODEL and the containment circuits'")
    w("     composition (%s). OPEN or PROVISIONAL: CON-004's quorum service (OPEN), FW-B22 (PROVISIONAL), L9T5-F21 (OPEN), the limiter's and" % (
        "composed, read by pin, mutated" if ok else "NOT as drafted"))
    w("     the rail trip's response times (PROVISIONAL, no printed maximum for the comparator's delay), V-B23's response (WITHDRAWN), the sustained thermal")
    w("     bound (WITHDRAWN as a bound, PROVISIONAL), T10-A3 at a peak (PROVISIONAL). REMAINING ENGINEERING, for the receiving company: the")
    w("     peer-silence or diagnostic circuit with the recovery proof; the corrected rail-trip response and its network calculation; peak-")
    w("     current containment or the periodic electrothermal solution; a rev X part's qualification; VOS0 under the trip")
    w("")
    out["r6"] = R6
    return out


def main():
    out = []
    w = out.append
    for rel in list(SHEETS.values()) + list(DOCS.values()):
        if not os.path.isfile(os.path.join(ROOT, rel)):
            refuse("input %s is missing" % rel)
    P = figures()
    DP = D.figures()
    cm = D.case_module()
    R = cm.compute()
    C = R["C"]
    G = D.gndret()
    air = P["air"]
    w("l9t5_t10: Layer 9 record l9t5, task T10: the three I/O supervisors' 3.3 V regulators (finding L9T5-F06; MESHSAT-1357)")
    w("prototype design; nothing built, bought, powered or measured; nothing applied to the tree; the owner's instruction of 4 October 2026, part 7:")
    w("'verify its applicable operating conditions and give it a named correction and acceptance criterion'")
    w("")
    w("1. INPUTS, pinned by sha256")
    for rel in list(SHEETS.values()) + list(DOCS.values()):
        w("   %s %s" % (sha(rel), rel))
    w("")
    # 2. the applicable state
    w("2. THE APPLICABLE OPERATING STATE OF A SUPERVISOR (U41, U51, U61, STM32H743VIT6), AS THE TREE DEFINES IT")
    w("   v2/docs/HW-FW-CONTRACT.md: %d rows name the supervisors (their I2C target addresses, CAN FD at 1 Mbps or less, the quorum, the vote rate);" % P["contract_rows"])
    w("     rows that bound a run mode, a clock or a voltage scale: %s" % ("NONE" if not P["contract_bound"] else "; ".join(P["contract_bound"])))
    w("   v2/docs/PANEL.md: rows that bound them: %s" % ("NONE" if not P["panel_bound"] else "; ".join(P["panel_bound"])))
    w("   v2/docs/ARCH-PCB-B-IOHA.md (Power): '%s': an INTENT, with no clock," % P["arch"])
    w("     no voltage scale, no acceptance and no measured or printed current (DECLARED, architecture text)")
    w("   v2/ecad/tools/gen_sch_b.py: a 25 MHz crystal a controller (HSE); each +3V3_IOCx DECLARED %.2f A typical, %.2f A peak, its loads %.3f A for" % (
        P["decl"] + (P["decl_loads"][0],)))
    w("     the controller and %.3f A for each of its three other parts" % P["decl_loads"][1])
    w("   firmware in the tree: v2/firmware holds %s only: NO supervisor firmware" % ", ".join(P["fw"]))
    w("   rv-pwr's budget (the case's loads): %.0f / %.0f / %.0f mA a controller (LOW, PLAN, HIGH) plus 60 mA of its other parts (DECLARED)" % tuple(x * 1000 for x in P["rv"]))
    unbounded = not P["contract_bound"] and not P["panel_bound"] and P["fw"] == ["panel"]
    w("   FINDING: %s" % ("THE STATE IS UNBOUNDED. Nothing in the tree defines, limits or tests a supervisor's run mode, clock or voltage scale; the" if unbounded
                           else "a bound exists (see above)"))
    w("     architecture's 60 mA is an intent, and the part runs whatever its firmware sets, up to the worst state its sheet prints")
    w("")
    # 3. ST's rows
    w("3. ST'S PRINTED ROWS (DS12110 Rev 10; Run mode, code with data processing from ITCM, the regulator ON; mA; the maxima are the sheet's")
    w("   characterization results (its table note 2), rev Y's 400 MHz all-peripherals figures at TJ 25 and 105 C tested in production: PRINTED). The order code STM32H743VIT6 does")
    w("   not fix the silicon revision, so both revisions' tables apply: rev Y, Table 30 (p.111); rev V, Table 129 (p.218)")
    w("   rev  state                                  typ   max at TJ 25 C   85 C  105 C  125 C")
    sel = [("off", 25), ("off", 60), ("off", 144), ("off", 200), ("on", 200), ("off", 400), ("on", 400)]
    for rev in ("Y", "V"):
        for key in sel + ([("on", 480)] if rev == "V" else []):
            row = P[rev][key]
            vos = VOS[rev].get(key[1], "VOS3")
            w("   %s    %-4s %3d MHz, all peripherals %-8s %5.1f %14.0f %6.0f %6.0f %6s" % (
                rev, vos, key[1], "disabled" if key[0] == "off" else "enabled", row[0], row[1], row[2], row[3], ("%.0f" % row[4]) if row[4] is not None else "-"))
    w("   the package (Table 230, p.346): LQFP100 junction to ambient %.1f C/W (PRINTED); maximum junction %.0f C (Table 23, p.105; VOS0: 105 C);" % (P["theta_mcu"], P["tj_mcu"]))
    w("   suffix 6 ambient to %.0f C at maximum dissipation; VDD %.2f to %.1f V (PRINTED)" % (P["ta_mcu"], P["vdd"][0], P["vdd"][1]))
    w("   rv-pwr's HIGH, %.0f mA, is rev Y's 400 MHz row with all peripherals enabled AT TJ 85 C; the same row prints %.0f mA at TJ 125 C" % (P["rv"][2] * 1000, P["Y"][("on", 400)][4]))
    w("")
    # 4. the junction
    i_ceiling = (P["tj_mcu"] - air) / P["theta_mcu"] / 3.3
    w("4. THE JUNCTION TEMPERATURE at L4-E12's inside air, %.2f C (E5's dwell, MODELED; %.2f C in the exhaust; inside the part's %.0f C ambient)" % (air, P["air_exhaust"], P["ta_mcu"]))
    w("   a controller dissipates VDD x IDD (its own regulator is linear): at that air its junction reaches %.0f C at %.3f A. Above that current the" % (P["tj_mcu"], i_ceiling))
    w("   H743 ITSELF is outside its rating, whatever regulator feeds it. Each state's operating point TJ = air + %.1f C/W x 3.3 V x Imax(TJ), the" % P["theta_mcu"])
    w("   maxima interpolated between their printed columns (MODEL on PRINTED figures):")
    PT = {}
    for rev in ("Y", "V"):
        for key in sel + ([("on", 480)] if rev == "V" else []):
            row = P[rev][key]
            tjm = 105.0 if (rev == "V" and key[1] == 480) else P["tj_mcu"]
            pt = point(row, air, P["theta_mcu"], tjm)
            PT[(rev, key)] = pt
            w("   %s    %-4s %3d MHz, peripherals %-8s  %s" % (rev, VOS[rev].get(key[1], "VOS3"), key[1], "disabled" if key[0] == "off" else "enabled",
              ("TJ %.1f C at %.4f A" % pt) if pt else "NO OPERATING POINT at or under %.0f C: the controller is outside its rating at this air in this state" % tjm))
    w("   so at the hot stop's air the worst state the sheet prints is not a state the controller can hold; what bounds it must be the firmware's")
    w("   configuration, and no document bounds that (section 2)")
    w("")
    # 5. auxiliaries
    aux_decl = sum(P["decl_loads"][1:])
    w("5. THE AUXILIARIES' AND THE PERIPHERALS' SHARE")
    w("   DECLARED: %.3f A a supervisor for its three other parts (two TCAN334D transceivers and the SWD and LED branch), in rv-pwr and in the generator" % aux_decl)
    w("   PRINTED (TI TCAN334, SLLSEQ7F 5.5): ICC recessive %.1f mA maximum; dominant %.0f mA maximum at 60 Ohm (%.0f mA at 50 Ohm); dominant with a bus" % (
        P["can_rec"] * 1000, P["can_dom"] * 1000, P["can_dom_hi"] * 1000))
    w("   fault %.0f mA maximum. Two transceivers: %.1f mA recessive, %.0f mA while both drive dominant bits, %.0f mA with both buses faulted" % (
        P["can_fault"] * 1000, 2 * P["can_rec"] * 1000, 2 * P["can_dom_hi"] * 1000, 2 * P["can_fault"] * 1000))
    w("   so the declared 60 mA covers one transceiver dominant; both dominant at once is a momentary %.0f mA (a frame's dominant bits), and the bus" % (2 * P["can_dom_hi"] * 1000))
    w("   fault row is a fault state. The controller's own peripherals (two FDCAN, I2C1, the ports, the watchdog) are in neither printed row: the")
    w("   'disabled' rows carry none and the 'enabled' rows carry all; their sum for the enabled set is OWED to the contract row (T10-A1)")
    w("")
    # 6. the demand
    bkey = ("off", BOUND[1])
    b_pts = {rev: PT[(rev, bkey)] for rev in ("Y", "V")}
    if any(v is None for v in b_pts.values()):
        refuse("the bounded state has no operating point: choose another bound")
    b_mcu = max(v[1] for v in b_pts.values())
    b_tj = max(v[0] for v in b_pts.values())
    d_bound = b_mcu + aux_decl
    d_bound_mom = b_mcu + 2 * P["can_dom_hi"] + P["decl_loads"][3]
    d_typ = P["decl"][0]
    d_high = P["rv"][2] + 0.06
    d_worst = P["Y"][("on", 400)][4] / 1000.0 + aux_decl
    d_worst_mom = P["Y"][("on", 400)][4] / 1000.0 + 2 * P["can_dom_hi"] + P["decl_loads"][3]
    w("6. THE DEMAND ON ONE REGULATOR, AS A RANGE")
    w("   declared typical (the generator, PLAN-like)                         %.4f A  DECLARED" % d_typ)
    w("   BOUNDED: %s, HCLK at most %d MHz, peripherals as section 5 owes: the controller %.4f A at its operating point (TJ %.1f C; the larger" % (
        BOUND[0], BOUND[1], b_mcu, b_tj))
    w("     revision), plus the declared auxiliaries                          %.4f A  MODEL on PRINTED maxima and DECLARED auxiliaries; %.4f A while both" % (d_bound, d_bound_mom))
    w("     transceivers drive dominant bits (momentary)")
    w("   the case's HIGH (rv-pwr; C-DEV rev 1's supervisors)                 %.4f A  PRINTED row at TJ 85 C plus DECLARED auxiliaries; no operating point" % d_high)
    w("     at this air (section 4)")
    w("   THE WORST NOTHING FORBIDS: rev Y at 400 MHz, all peripherals, the TJ 125 C column: %.4f A (%.4f A with both transceivers dominant);" % (d_worst, d_worst_mom))
    w("     no operating point at this air: the controller overheats first")
    w("   so the demand is %.4f A where a contract bounds the state, and anything up to %.4f A where none does" % (d_bound, d_worst))
    w("")
    # 7. the regulator as drawn
    lo5, nom5, hi5 = CHK.vout_band(R601, R602_OLD)

    def tj_ldo(i, vin_hi):
        return air + P["theta_ldo"] * (vin_hi - 3.3) * i

    def ceil_i(vin_hi, tj):
        return (tj - air) / P["theta_ldo"] / (vin_hi - 3.3)
    w("7. THE REGULATOR AS DRAWN: AP2112K-3.3 (Diodes %s), one a supervisor, fed from +5V_IOC (I-03's draft: %.4f to %.4f V)" % (P["ap_rev"], lo5, hi5))
    w("   PRINTED: output current %.0f mA minimum capability; dropout %.0f / %.0f / %.0f mV maximum at 10 / 300 / 600 mA (p.8); input %.1f to %.1f V; ambient to" % (
        P["imax"] * 1000, P["drop"][10] * 1000, P["drop"][300] * 1000, P["drop"][600] * 1000, P["vin"][0], P["vin"][1]))
    w("   %.0f C (p.3); SOT25 junction to ambient %.0f C/W, no heat sink (p.3); junction %.0f C (absolute maximum, p.3); thermal shutdown %.0f C (TYPICAL" % (
        P["ta_ldo"], P["theta_ldo"], P["tj_ldo"], P["tsd"]))
    w("   behaviour, no maximum trip printed: never an acceptance); foldback short current %.0f mA (TYPICAL). It drops its whole input to 3.3 V: at" % (
        P["ishort"] * 1000))
    w("   the %.4f V maximum, %.4f V times its current" % (hi5, hi5 - 3.3))
    w("   its THERMAL limit at the %.2f C air: junction %.0f C at %.4f A; %.0f C (this record's criterion, SESSION) at %.4f A: it binds far under the 600 mA" % (
        air, P["tj_ldo"], ceil_i(hi5, P["tj_ldo"]), TJ_GOAL, ceil_i(hi5, TJ_GOAL)))
    rows7 = [("declared typical", d_typ), ("the bounded state", d_bound), ("the declared peak", P["decl"][1]), ("the case's HIGH", d_high), ("the worst nothing forbids", d_worst)]
    AS = {}
    for lab, i in rows7:
        tj = tj_ldo(i, hi5)
        AS[lab] = tj
        w("     %-26s %.4f A: junction %6.1f C: %s" % (lab, i, tj, "inside the %.0f C criterion" % TJ_GOAL if tj <= TJ_GOAL else
                                                    "over the criterion, under the absolute maximum" if tj <= P["tj_ldo"] else "OVER the absolute maximum" + (
                                                        "; over its 600 mA capability" if i > P["imax"] else "")))
    w("   FINDING (wider than L9T5-F06 stated it): the deficit is thermal before it is a current limit. As drawn the regulator passes its absolute")
    w("   maximum junction at the case's own HIGH (C-DEV rev 1's supervisors), not only in the TJ 125 C state; and with the state unbounded")
    w("   nothing keeps the demand under either limit. Moving the LDOs to +5V_IOC (I-03) did not change this; a ground return does not address it")
    w("")
    # 8. the corrections
    w("8. THE CORRECTIONS COMPARED (three), THE SELECTION AND ITS ACCEPTANCE CRITERION")
    r_sup = G["rhot"] + 2 * DP["vh_r"][1]
    shift_ub = G["shift_drawn_ub"]
    # K1
    k1_loss = {lab: i * 3.3 * (1.0 / ETA_K1 - 1.0) for lab, i in rows7}
    k1_tj = {lab: air + P["k1_theta"] * k1_loss[lab] for lab, _i in rows7}
    ioc_v_least = lo5 - D.RAIL_BUDGET * 5.0
    k1_in = {lab: 3 * i * 3.3 / ETA_K1 / ioc_v_least for lab, i in rows7}
    w("   K1 A REGULATOR PER SUPERVISOR that covers the worst: a buck in place of each LDO, the part board B already fits as U25, AP63203WU-7 (Diodes")
    w("      %s: %.0f A, input %.1f to %.0f V, TSOT26 %.0f C/W, junction %.0f C absolute; PRINTED). At an efficiency of %.2f (DECLARED, U25's; its 5 V input" % (
        P["k1_rev"], P["k1_a"], P["k1_vin"][0], P["k1_vin"][1], P["k1_theta"], P["k1_tj"], ETA_K1))
    w("      curve is %s): junction %.1f C at the bounded demand and %.1f C at the worst (MODEL); U601's load %.4f A bounded, %.4f A at the worst," % (
        "plotted" if P["k1_eff_5v"] else "NOT PLOTTED", k1_tj["the bounded state"], k1_tj["the worst nothing forbids"], k1_in["the bounded state"], k1_in["the worst nothing forbids"]))
    w("      against its %.0f A (PRINTED); the lead's pin 1 the same. Changes: board B, three bucks with an inductor, a bootstrap and two output" % DP["tps_a"])
    w("      capacitors each in the supervisors' pockets, the LDOs' lands and value texts, switching ripple on each controller's VDD and VDDA; board A")
    w("      none. Physical: the pockets' placement and routing, the ripple, the start. It does NOT make the unbounded state hold: the controller")
    w("      itself has no operating point there (section 4), so K2's row is needed with it as well")
    # K2
    w("   K2 A CONTRACT ROW THAT BOUNDS THE STATE (Layer 5's; its text below), the circuit as drawn: the demand becomes %.4f A; the LDO's junction" % d_bound)
    k2_over = AS["the bounded state"] > P["tj_ldo"]
    w("      %.1f C at this air: %s the %.0f C absolute maximum by %.1f K, over the %.0f C criterion. Changes: none on either board; a firmware" % (
        AS["the bounded state"], "OVER" if k2_over else "under", P["tj_ldo"], abs(P["tj_ldo"] - AS["the bounded state"]), TJ_GOAL))
    w("      acceptance and a measured current. Alone it %s" % (
        "does not hold: the bound is needed and is not enough" if k2_over else "leaves the regulator with no margin on its printed thermal resistance"))
    # K3
    need600 = 3.3 * (P["vout_hi"] + P["load"] * 0.6) + P["drop"][600]
    cands = []
    e96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78,
           1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24,
           3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90,
           6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]
    for dec in (1e3, 1e4):
        for e in e96:
            rb = e * dec
            lo_, nom_, hi_ = CHK.vout_band(R601, rb)
            at_ldo = lo_ - D.RAIL_BUDGET * nom_ - 3 * 0.6 * r_sup - shift_ub
            if at_ldo >= need600:
                cands.append((nom_, rb, lo_, hi_, at_ldo))
    nom3, r602, lo3, hi3, at600 = min(cands)
    w("   K3 THE SUPERVISORS FED DIFFERENTLY: U601 (board A, I-03's own buck, which feeds nothing else) as a PRE-REGULATOR for the LDOs. Its set point")
    w("      is the least on the E96 series, R601 kept, that holds each LDO's input over its requirement at its full %.0f mA (%.4f V: VOUT +%.1f %%, load" % (
        P["imax"] * 1000, need600, (P["vout_hi"] - 1) * 100))
    w("      regulation %.0f %%/A, dropout %.0f mV; PRINTED) after the rail's %.0f %% budget, the lead at three times 600 mA and the return's shift AS DRAWN" % (
        P["load"] * 100, P["drop"][600] * 1000, D.RAIL_BUDGET * 100))
    w("      (%.4f V, record l8r2): R602 %.1f k, %.4f V nominal, %.4f to %.4f V; the LDOs' input then at least %.4f V" % (shift_ub, r602 / 1e3, nom3, lo3, hi3, at600))
    K3 = {}
    for lab, i in rows7:
        K3[lab] = tj_ldo(i, hi3)
    w("      an LDO drops at most %.4f V: junction %.0f C at %.4f A, %.0f C at %.4f A (as drawn %.4f and %.4f A). Junctions: typical %.1f C, bounded" % (
        hi3 - 3.3, TJ_GOAL, ceil_i(hi3, TJ_GOAL), P["tj_ldo"], ceil_i(hi3, P["tj_ldo"]), ceil_i(hi5, TJ_GOAL), ceil_i(hi5, P["tj_ldo"]), K3["declared typical"]))
    w("      %.1f C, the declared peak %.1f C, the case's HIGH %.1f C (still over), the worst not covered. Changes: board A, one resistor value and" % (
        K3["the bounded state"], K3["the declared peak"], K3["the case's HIGH"]))
    w("      the rail's declarations; board B, declarations only (no part, no net); U601's load is the LDOs' own current (%.4f A at the case's HIGH)," % (3 * d_high))
    w("      the lead's pin 1 the same. Physical: the LDOs' real thermal resistance on board B's copper, U601's efficiency at this output, the LDOs'")
    w("      accuracy between their dropout and 4.3 V (the sheet tests VOUT at 4.3 V and prints line regulation from 4.3 V; the input here is")
    w("      %.4f to %.4f V, inside the printed %.1f to %.1f V supply range). A shared 3.3 V buck with no LDO was not taken: it removes each" % (at600, hi3, P["vin"][0], P["vin"][1]))
    w("      controller's own regulator, on which the architecture's failure domains rest")
    d_f1 = b_mcu + P["can_fault"] + P["can_rec"] + P["decl_loads"][3]
    d_f2 = b_mcu + 2 * P["can_fault"] + P["decl_loads"][3]
    tj_m, tj_f1, tj_f2 = tj_ldo(d_bound_mom, hi3), tj_ldo(d_f1, hi3), tj_ldo(d_f2, hi3)
    tj_m5, tj_f15, tj_f25 = tj_ldo(d_bound_mom, hi5), tj_ldo(d_f1, hi5), tj_ldo(d_f2, hi5)

    def bound(tj, served):
        """the owner's rule of 5 October 2026: over 125 C in a state the design must serve, or over 150 C in any state, FAILS"""
        return "FAILS" if (tj > P["tj_ldo"] or (served and tj > TJ_GOAL)) else "holds"
    # the three figures kept apart (owner, 5 October 2026): 125 C this record's criterion; 150 C the printed absolute maximum, never
    # exceeded and never a target; 160 C the shutdown, TYPICAL behaviour with no maximum trip printed, never an acceptance
    w("      NOT INSIDE THE BOUND, each row judged against its own limit. Three figures kept apart: %.0f C, T10's design criterion (SESSION);" % TJ_GOAL)
    w("      %.0f C, the AP2112K's printed absolute maximum junction (DS39724 Rev. 2-2, Absolute Maximum Ratings, p.3), never to be exceeded and never" % P["tj_ldo"])
    w("      an operating target; %.0f C, its thermal shutdown, TYPICAL behaviour only (p.8, no maximum trip printed), which shows no protection below" % P["tsd"])
    w("      %.0f C and is no acceptance. A row over %.0f C in a state the design must serve, or over %.0f C in any state, FAILS its thermal bound." % (
        P["tj_ldo"], TJ_GOAL, P["tj_ldo"]))
    w("      Every junction below is a MODEL figure (the inside air, the printed 184 C/W and the current), never a measured temperature")
    w("      (m) both transceivers driving dominant, held: %.4f A, junction %.1f C MODEL with the pre-regulator (%.1f C MODEL as drawn). IN T10's" % (
        d_bound_mom, tj_m, tj_m5))
    w("          SCOPE: normal traffic sets its average. Against %.0f C: %s at the held figure. A held drive is ended by the parts: the TCAN334's" % (
        TJ_GOAL, bound(tj_m, True)))
    w("          driver dominant time-out frees the bus after %.1f to %.1f ms (SLLSEQ7F, tTXD_DTO, PRINTED) and the protocol forces recessive bits" % (
        P["can_dto"][0], P["can_dto"][2]))
    w("          (6.3.7, p.20); but the average a supervisor's traffic sets is bounded by no row (FW-B09 bounds the rate, 1 Mbps or less, not the")
    w("          share), and T10-A2 is judged at the DECLARED %.3f A a transceiver. OPEN DEFECT L9T5-F13: it closes when a contract row bounds each" % (
        P["decl_loads"][1]))
    w("          supervisor's transmit share so that its transceivers' average stays at or under that declaration (round 5: drafted, section 10d)")
    w("          or when the regulator holds %.0f C at the bounded share (owners: Layer 5 for the row; board B's generator owner for the" % TJ_GOAL)
    w("          declaration). As drawn: %s, L9T5-F06" % bound(tj_m5, True))
    w("      (f1) one fabric faulted, its transceiver driving dominant into the fault (the %.0f mA row's condition: TXD = 0 V, CANH = -12 V, RL open;" % (
        P["can_fault"] * 1000))
    w("          SLLSEQ7F 5.5, p.6), the other transceiver recessive: %.4f A, junction %.1f C MODEL (%.1f C MODEL as drawn). Each supervisor has a" % (
        d_f1, tj_f1, tj_f15))
    w("          transceiver on each fabric, so the row applies to all three regulators. A FAULT STATE OUTSIDE T10's SCOPE (the steady demand on")
    w("          C-DEV rev 1) which the design must serve: ARCH-PCB-B-IOHA.md section 12 row 7 ('quorum continues on the other fabric') and its test")
    w("          A7. Against %.0f C: %s (%s %.0f C). The driver's time-out ends a held TXD, not the controller's repeated attempts, and the current is" % (
        TJ_GOAL, bound(tj_f1, True), "under" if tj_f1 < P["tj_ldo"] else "OVER", P["tj_ldo"]))
    w("          %s the %.0f mA capability: no printed limit holds the junction at %.0f C. COVERED BY CON-004 (round 5, V6-B3; round 4 read REQ-073" % (
        "under" if d_f1 < P["imax"] else "OVER", P["imax"] * 1000, TJ_GOAL))
    w("          and REQ-004 and missed it): REQUIREMENTS-TRACE.md, %s, %s, %s: '%s'; accepted when '%s'" % (P["con004_class"] + (
        P["con004"].split(", and ")[1] if ", and " in P["con004"] else P["con004"], P["con004_acc"])))
    w("          Row 7 ('%s') is a failure the design must survive: '%s'; its test A7 '%s'." % (P["row7"][0], P["row7"][1], P["a7"][1]))
    w("          So this state's closure is REQUIRED for CON-004. A7 as written cuts the bus (the break links): it does not exercise this row's bus")
    w("          fault, which needs its own analysis (section 10e). OPEN DEFECT L9T5-F16 (owners: Layer 5 for the firmware rows, CON-004's '%s')." % P["con004_alloc"])
    w("          The response drafted in round 5 (section 10f) ends the dominant drive by the firmware's schedule and a transceiver shutdown, the")
    w("          service lost stated: that supervisor silent on the faulted fabric, quorum on the other (row 7). As drawn: %s, L9T5-F06 as well" % (
        bound(tj_f15, True)))
    w("      (f2) both fabrics faulted, both transceivers driving into their faults: %.4f A, junction %.1f C MODEL (%.1f C MODEL as drawn), on all three" % (
        d_f2, tj_f2, tj_f25))
    w("          regulators. A double fault outside T10's scope (row 8, and A7's 'with both broken nothing moves'). Against %.0f C, in any state: %s." % (
        P["tj_ldo"], bound(tj_f2, False)))
    w("          The current is %s the capability, so no printed limit acts, and the typical shutdown is no acceptance. COVERED BY CON-004 through" % (
        "under" if d_f2 < P["imax"] else "OVER"))
    w("          row 8 ('%s': '%s') and A7's '%s': 'nothing moves' is the" % (P["row8"][0], P["row8"][1][:60] + "...", P["a7"][2].split("; ")[-1]))
    w("          accepted outcome, but the regulators must survive it. OPEN DEFECT L9T5-F17 (owners as F16). The response must hold each regulator")
    w("          inside %.0f C (or cut the transceivers' current) with the service lost stated: both fabrics silent, no majority, the voters at the" % (
        P["tj_ldo"]))
    w("          home assignment (row 8); drafted in round 5 (section 10f). As drawn: %s" % bound(tj_f25, False))
    w("      the foldback (the output short's behaviour) acts in no row")
    FAULT = {"mom": tj_m, "f1": tj_f1, "f2": tj_f2, "d_f1": d_f1, "d_f2": d_f2,
             "fails": [bound(x, s) for x, s in ((tj_m, True), (tj_f1, True), (tj_f2, False), (tj_m5, True), (tj_f15, True), (tj_f25, False))]}
    k3_ok = K3["the bounded state"] <= TJ_GOAL and K3["the declared peak"] <= TJ_GOAL and d_bound <= ceil_i(hi3, TJ_GOAL)
    w("   SELECTED (SESSION): K3 WITH K2's ROW AS ITS CONDITION, A DRAFTED CANDIDATE, UNCHECKED. Why: the state must be bounded under every option,")
    w("   because the controller itself has no operating point above it (section 4); with the bound the demand is %.4f A, which K2 alone %s (%.1f C)" % (
        d_bound, "does not hold" if AS["the bounded state"] > P["tj_ldo"] else "holds without margin", AS["the bounded state"]))
    w("   and K3 holds at %.1f C on a one-resistor change in a draft this record already owns; K1 covers currents the controller cannot draw at this" % K3["the bounded state"])
    w("   air and costs three switching stages in board B's tightest area. To reverse: drop apply_gen_sch_?_iocpre.py (the drafts are separate from")
    w("   I-03's) and take K1; it becomes necessary if Layer 5 cannot bound the state or the bench reads the LDOs hotter than the printed figure")
    w("   NOT the owner's: no requirement changes and no money beyond a resistor value. Layer 5's row is its owner's to accept (text below)")
    w("   THE ACCEPTANCE CRITERION (T10), every condition required:")
    w("   T10-A1 the contract carries a row that bounds each supervisor to %s and HCLK at most %d MHz (the least printed row over the 64 MHz it is" % BOUND)
    w("          taken to start at, an ASSUMPTION: RM0433 is not held; the row's owner confirms the reset state is inside the bound), with")
    w("          only the peripheral clocks the board uses (FDCAN1, FDCAN2, I2C1, the ports in use, the watchdog) enabled, and a firmware acceptance:")
    w("          the clock tree and the voltage scale read back at start and refused otherwise; the printed figure for that state with the enabled")
    w("          set's own currents summed, or the supply current measured on the first article at a junction of at least 105 C")
    w("   T10-A2 at %.2f C inside air and that state's demand (%.4f A here), each regulator's junction is at most %.0f C on its printed thermal" % (air, d_bound, TJ_GOAL))
    w("          resistance (%.1f C with K3; %.1f C as drawn), and at its declared peak %.2f A (%.1f C with K3)" % (
        K3["the bounded state"], AS["the bounded state"], P["decl"][1], K3["the declared peak"]))
    w("   T10-A3 each LDO's input stays over its requirement at its full %.0f mA at the least set point, with the return as drawn: %.4f V against" % (P["imax"] * 1000, at600))
    w("          %.4f V (%+.4f V)" % (need600, at600 - need600))
    w("   T10-A4 the draft composes in L4-E9's order after I-03's, its divider is read in the regenerated netlist with a mutation that fails, and")
    w("          the declarations it writes are read in the intent (section 9)")
    w("   T10-A5 PHYSICAL, on the first article: each LDO's case temperature at the bounded state in a %.0f C chamber, and each supervisor's supply" % air)
    w("          current in that state; a supervisor forced out of the bound (a firmware fault) must be returned inside it by a response that acts")
    w("          before the LDO's junction reaches %.0f C (the clock read-back's reset or the watchdog), the voters at their default meanwhile and the" % P["tj_ldo"])
    w("          service lost stated; the LDO's thermal shutdown (%.0f C, TYPICAL, no maximum trip printed) is no acceptance: Layer 5's FMEA row" % P["tsd"])
    w("   LAYER 5'S ROW, TEXT FOR ITS OWNER (HW-FW-CONTRACT.md section 3.3, a new FW-B row; not applied by this record):")
    w("     | FW-Bxx | the supervisors' supply: a private AP2112K-3.3 each from the pre-regulated +5V_IOC (record l9t5 T10) | Run each supervisor at")
    w("       %s with HCLK at most %d MHz (no PLL above it); enable only FDCAN1, FDCAN2, I2C1, the GPIO ports in use and the IWDG; read the clock" % BOUND)
    w("       tree and the voltage scale back at start and stay in reset-safe outputs if they differ; never raise either at run time | record l9t5")
    w("       l9t5_t10.out (ST DS12110 Rev 10 Tables 30 and 129; Diodes DS39724 Rev. 2-2) | supply current of each supervisor in that state at a")
    w("       junction of at least 105 C; each LDO's case temperature in a %.0f C chamber | OWED |" % air)
    w("")
    # 9. the draft
    w("9. THE SELECTED CIRCUIT CHANGE, DRAFTED (apply_gen_sch_a_iocpre.py, apply_gen_sch_b_iocpre.py; release-guarded by RELEASE-T10.md; after I-03's drafts)")
    with tempfile.TemporaryDirectory(prefix="l9t5_t10_") as d:
        tree_before = {b: D.sha(D.GEN[b], 64) for b in "ab"}
        STEP = []
        for b in "ab":
            t0 = os.path.join(d, "bare_gen_sch_%s.py" % b)
            shutil.copy(D.GEN[b], t0)
            r0 = subprocess.run([sys.executable, "-B", PRE[b], t0, "--write"], capture_output=True)
            t1 = os.path.join(d, "one_gen_sch_%s.py" % b)
            shutil.copy(D.GEN[b], t1)
            ra = subprocess.run([sys.executable, "-B", D.MINE[b], t1, "--write"], capture_output=True)
            r1 = subprocess.run([sys.executable, "-B", PRE[b], t1], capture_output=True)
            r2 = subprocess.run([sys.executable, "-B", PRE[b], t1, "--write"], capture_output=True)
            n_ed = re.search(rb"WRITTEN, (\d+) edit", r2.stdout)
            r3 = subprocess.run([sys.executable, "-B", PRE[b], t1, "--write"], capture_output=True)
            r4 = subprocess.run([sys.executable, "-B", PRE[b], D.GEN[b], "--write"], capture_output=True)
            ok = (r0.returncode == 3 and ra.returncode == 0 and r1.returncode == 0 and b"CHECK OK" in r1.stdout and r2.returncode == 0 and bool(n_ed)
                  and r3.returncode == 3 and r4.returncode == 3)
            STEP.append(ok)
            w("   %s: without I-03's draft %s; after it: check %s, applied %s (%s edits), second application %s; the tree's gen_sch_%s.py %s" % (
                os.path.basename(PRE[b]), "refused" if r0.returncode == 3 else "NOT REFUSED", "OK" if r1.returncode == 0 else "FAILED",
                "OK" if r2.returncode == 0 else "FAILED", n_ed.group(1).decode() if n_ed else "?", "refused" if r3.returncode == 3 else "NOT REFUSED", b,
                "refused" if r4.returncode == 3 else "NOT REFUSED"))
        if any(D.sha(D.GEN[b], 64) != tree_before[b] for b in "ab"):
            refuse("a draft wrote into the tree")
        comp, nets, tabs = {}, {}, {}
        for b in "ab":
            seq = D.seq_of(b, "slot")
            at = seq.index(D.MINE[b]) + 1
            seq = seq[:at] + [PRE[b]] + seq[at:]
            p, res, ok = D.compose(b, seq, d, "t10")
            comp[b] = ok
            w("   board %s composed in L4-E9's order, this draft straight after I-03's (%d drafts): %s" % (
                b.upper(), len(seq), "every step OK" if ok else "; ".join("%s %s" % (s, v) for s, v, _m in res if v != "OK")))
            rc, path, table = D.netlist(b, p, d, "t10")
            if rc or not ok:
                refuse("board %s's composition with the T10 draft did not regenerate: %s" % (b, path))
            nets[b], tabs[b] = path, table
            w("     the generator ran to its end (%d parts, %d unplaced, intent written: %s)" % (len(table["parts"]), len(table["unplaced"]), "yes" if table["intent_written"] else "NO"))
        buf = io.StringIO()
        kit, V = CHK.run({b: nets[b] for b in "ab"}, ROOT, buf, label=lambda x: "board %s composed with the T10 draft" % x.upper(), div="t10")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()).rstrip("\n"))
        ia, ib = tabs["a"]["intent"], tabs["b"]["intent"]
        wall = float(CHK.rails_of(ia)["VBUS_WALL"]["amps_peak"])
        basis = {"dev_lead": C["b_i_least"], "ioc": 3 * d_high, "wall": wall}
        DECL = {}
        for b, it in (("a", ia), ("b", ib)):
            DECL[b], why = CHK.decl(b, it, basis)
            w("       %s DECL %s%s (the peak's basis here: the three LDOs' own current at the case's HIGH, %.4f A)" % (b.upper(), DECL[b], (": " + "; ".join(why[:2])) if why else "", 3 * d_high))
        ra_, rb_ = CHK.rails_of(ia), CHK.rails_of(ib)
        w("   the intent: board A +5V_IOC %.2f V, v_work %.2f V, %.2f A typical, %.4f A peak; VBAT's entry for U601 %.2f A; board B +5V_IOC %.2f V," % (
            ra_["+5V_IOC"]["volts"], ra_["+5V_IOC"]["v_work"], ra_["+5V_IOC"]["amps_typ"], ra_["+5V_IOC"]["amps_peak"], ra_["VBAT"]["loads"]["U601"], rb_["+5V_IOC"]["volts"]))
        w("     %.4f A peak; the three +3V3_IOCx at efficiency %s" % (rb_["+5V_IOC"]["amps_peak"], ", ".join("%.2f" % rb_[n]["efficiency"] for n in ("+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC"))))
        intent_ok = (abs(ra_["+5V_IOC"]["volts"] - 4.18) < 1e-9 and abs(rb_["+5V_IOC"]["volts"] - 4.18) < 1e-9 and ra_["+5V_IOC"]["v_work"] >= hi3
                     and all(abs(rb_[n]["efficiency"] - 0.79) < 1e-9 for n in ("+3V3_IOCA", "+3V3_IOCB", "+3V3_IOCC")))
        nl = CHK.read(open(nets["a"], "rb").read())
        dv = CHK.divider(nl)
        drawn_r602 = dv[1] if dv else None
        w("   the divider read on the netlist: %s over %s: %.4f V nominal by the checker's arithmetic: %s section 8's selection (R602 %.1f k)" % (
            CHK.value(nl, dv[2]), CHK.value(nl, dv[3]), CHK.vout_band(dv[0], dv[1])[1], "EQUALS" if abs(drawn_r602 - r602) < 1e-6 else "DIFFERS FROM", r602 / 1e3))
        # the old state and a mutation
        seq_old = D.seq_of("a", "slot")
        p_old, _r, ok_old = D.compose("a", seq_old, d, "t10_old")
        rc, path_old, _t = D.netlist("a", p_old, d, "t10_old")
        buf = io.StringIO()
        kit_old, _v = CHK.run({"a": path_old}, ROOT, buf, label=lambda x: "old state: board A composed WITHOUT the T10 draft, read for the pre-regulator", div="t10")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines() if "DIV" in l or "old state" in l or "record l9t5" in l).rstrip("\n"))
        mp = D.mutate(nets["a"], d, "t10_mut", [(("R601", "1"), ("R602", "2"))])
        buf = io.StringIO()
        kit_mut, _v = CHK.run({"a": mp}, ROOT, buf, label=lambda x: "mutation: R601's rail end and R602's ground end exchanged (the divider inverted)", div="t10")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines() if "DIV" in l or "mutation" in l or "record l9t5" in l).rstrip("\n"))
    # judged on C-DEV rev 1
    iomax = (DP["ihs"][2] + DP["ils"][2]) / 2.0
    w("   JUDGED ON C-DEV REV 1 (the device rail's case), with the draft composed:")
    c1 = C["b_margin"] > 0
    w("   (1) U7: unchanged, %.4f A against %.4f A (%+.4f A): the supervisors are on +5V_IOC either way: %s" % (C["b_i_least"], C["lim_min"], C["b_margin"], "HOLDS" if c1 else "FAILS"))
    c2 = 3 * d_high < DP["tps_a"] and iomax < DP["vh_a"]
    w("   (2) U601 and the lead's pin 1: the LDOs' own current at the case's HIGH %.4f A (an LDO passes its output current; I-03's %.4f A was the" % (3 * d_high, CHK.ceil4(C["ioc_in_w"] / (lo5 - D.RAIL_BUDGET * 5.0))))
    w("       5 V case's constant-power convention), against U601's %.0f A (PRINTED) and the VH's %.0f A; U601's limit %.2f A unchanged: %s" % (
        DP["tps_a"], DP["vh_a"], iomax, "HOLDS" if c2 else "FAILS"))
    w("       U601 at %.2f V out is inside the TPS62933's output range (PRINTED 0.8 to 22 V); its inductor 6.8 uH is Table 10-2's value for 5 V, the 3.3 V" % nom3)
    w("       row gives %.1f uH: between the two printed rows (TYPICAL guidance; its efficiency at this output is NOT PLOTTED)" % P["tps_l"][0])
    c3 = at600 >= need600
    w("   (3) the LDOs' input: at least %.4f V at three times 600 mA with the return as drawn, against %.4f V: %s; at most %.4f V, inside the" % (at600, need600, "HOLDS" if c3 else "FAILS", hi3))
    w("       AP2112's %.1f V and under D900's 5 V standoff" % P["vin"][1])
    c4 = k3_ok
    w("   (4) the regulators' junctions at %.2f C air: bounded demand %.1f C, declared peak %.1f C against the %.0f C criterion: %s under T10-A1's" % (
        air, K3["the bounded state"], K3["the declared peak"], TJ_GOAL, "HOLDS" if c4 else "FAILS"))
    w("       bound. At the case's HIGH for the supervisors (%.2f A a regulator) the junction reads %.1f C: NOT COVERED, with or without this draft" % (d_high, K3["the case's HIGH"]))
    w("       (%.1f C as drawn): the case's HIGH is the unbounded state's TJ 85 C figure, which T10-A1 removes; until Layer 5 accepts that row the" % AS["the case's HIGH"])
    w("       budget keeps it and this item stays open against it")
    w("   (5) the return between the boards: the draft adds no load and no contact; I-03's connected-path row is unchanged (CONDITIONAL on record")
    w("       l8r2's return, l9t5_drafts.out section 6)")
    acc = c1 and c2 and c3 and c4 and DECL == {"a": "DRAWN", "b": "DRAWN"} and kit == "DRAWN" and intent_ok
    w("   THE DRAFT ON C-DEV REV 1: %s. T10-A1 (Layer 5's row) and T10-A5 (the bench) are NOT met by" % ("items 1 to 3 hold; item 4 holds only under T10-A1's bound" if acc else "DOES NOT HOLD"))
    w("   anything in this tree; item 4 at the case's HIGH is NOT COVERED")
    w("")
    # 10. round 5
    Q, _ldo_k, tj_l, R5 = round5(w, P, DP, air, hi3, d_bound)
    R5 = round5_rest(w, P, DP, air, hi3, Q, _ldo_k, tj_l, R5)
    R5 = round5_faults(w, P, air, Q, tj_l, R5)
    R5 = round5_answers(w, P, DP, air, hi3, Q, tj_l, R5)
    R5 = round5_part22(w, P, DP, air, hi3, Q, tj_l, R5)
    R5 = round6_cx45(w, P, DP, air, hi3, Q, tj_l, R5)
    # 11. state, findings, predicates
    w("11. THE STATE OF L9T5-F06 (T10)")
    by_, bv_ = R5["B"][("Y", air)], R5["B"][("V", air)]
    # judged on rev V's rows, the revision L9T5-D7 fits (inside CON-017 (5)); rev Y's rows, the cover for a rev X part, are printed apart
    f16_ok = tj_l(R5["worst"]["V"], air) <= TJ_GOAL
    f17_ok = max(tj_l(R5["both"][r][0], air) for r in "YV") <= P["tj_ldo"] and tj_l(R5["both"]["V"][0], air) <= TJ_GOAL
    f13_ok = bv_[3] <= TJ_GOAL
    cover_fails = by_[3] > TJ_GOAL
    drafted_ok = R5["contract_ok"] and R5["v_new"] == "DRAWN" and R5["v_old"] == "FAIL" and R5["v_mut"] == "FAIL" and R5["v_mut2"] == "FAIL"
    w("   L9T5-F06 STAYS OPEN, round 5's state: T10-A1's row is DRAFTED (FW-B20, unapplied) with the reset state now printed inside it; T10-A2")
    w("   is restated with the enabled peripherals at the drop's worst corner: at the case's %.2f C air it holds on rev V's rows (%.1f C), the revision" % (
        air, bv_[3]))
    w("   L9T5-D7 fits, and NOT on rev Y's rows (%.1f C), the cover for a rev X part, which is HELD with no admission route (10j (f)); T10-A3" % by_[3])
    w("   as 10j (d) restates it (PROVISIONAL at a peak) and T10-A4 (section 9); T10-A5 is physical, its qualification limits measurements,")
    w("   not an acceptance (10j (e)). The independent checks cx45 and cx46 read rounds 5 and 6: NOT CONFIRMED, then CORRECTIONS NOT CLOSED;")
    w("   Layer 5 has not accepted the rows; nothing is applied. In the exhaust air a rev X part rests on rev Y's rows, which hold only to")
    w("   %.2f C local air (10c): that air is U-02's question. Round 4 was the first attempt at this correction (K3 with K2's row); V6's check" % R5["max_air"]["Y"])
    w("   of it read CONFIRMED AS CONDITIONAL, not a negative; round 5 is the second round on the same correction, adding the rows V6 named")
    w("   L9T5-F13: %s. The row (FW-B21's share) is drafted; with it the regulator reads %.1f C on rev V (fitted, L9T5-D7) and %.1f C on rev Y's" % (
        "A DRAFTED CORRECTION, DESK ACCEPTANCE MET BY ITS AUTHOR ON REV V, UNCHECKED" if f13_ok and drafted_ok else "OPEN", bv_[3], by_[3]))
    w("     cover at %.2f C (the drop's worst corner)" % air)
    w("     against %.0f C; the bench (V-B20, V-B21) confirms the firmware's implementation and decides no feasibility. Stays OPEN in the" % TJ_GOAL)
    w("     register; PROVISIONAL after cx46: a firmware outside the row is bounded only on its AVERAGE by the drafted rail trip (10j (e)),")
    w("     and a latent rail trip removes even that")
    w("   L9T5-F16: %s. Every credible single fabric fault inside board B holds %.0f C with the response on rev V (worst %.1f C; rev Y's cover %.1f C;" % (
        "A DRAFTED CORRECTION, DESK ACCEPTANCE MET BY ITS AUTHOR ON REV V, UNCHECKED" if f16_ok and drafted_ok else "OPEN", TJ_GOAL,
        tj_l(R5["worst"]["V"], air), tj_l(R5["worst"]["Y"], air)))
    w("     10e), the circuit half composed, read and mutated (10f); the B7b residual reads 120.0 C on rev V, inside 125 C (L9T5-D5 withdrawn,")
    w("     round 6). Covered by CON-004 (10a). Stays OPEN in the register; PROVISIONAL: a latent share comparator weakens the response's")
    w("     containment and the quorum on the other fabric (10j (c))")
    p22 = R5["p22"]
    w("   THE BABBLING ROW (part 22): a SUSTAINED fault state, %.0f C applies: on rev V with iocpre alone %.1f C, FAILS; with the set point" % (
        TJ_GOAL, p22["bab"][FITTED_REV][0]))
    w("     delta (iocset, DRAFTED, composed, read, mutated) %.1f C, holds: a DRAFTED CORRECTION, desk acceptance met by its author on rev V," % p22["bab"][FITTED_REV][1])
    w("     UNCHECKED, PROVISIONAL (a babbler outside FW-B20's clock is bounded only on its average, 10j (e)). Its quorum effect stays OPEN")
    w("     (L9T5-F21; 10j (c)). The hung row is a transient the IWDG ends: %.0f C applies and it holds" % P["tj_ldo"])
    w("   L9T5-F17: %s. Both fabrics faulted hold %.0f C with the response (%.1f C rev Y, %.1f C rev V); held, %.1f C (rev Y). Same conditions" % (
        "A DRAFTED CORRECTION, DESK ACCEPTANCE MET BY ITS AUTHOR ON REV V, UNCHECKED" if f17_ok and drafted_ok else "OPEN", P["tj_ldo"],
        tj_l(R5["both"]["Y"][0], air), tj_l(R5["both"]["V"][0], air), tj_l(R5["both"]["Y"][1], air)))
    w("   FINDINGS FOR OTHER AUTHORS")
    w("   L9T5-F09 (Layer 5, HW-FW-CONTRACT.md 3.3): answered by the drafted rows FW-B20 and FW-B21 (apply_hw_fw_contract_t10.py, the integrator's")
    w("     to apply); the FMEA row for a supervisor out of its bound (T10-A5) stays Layer 5's")
    w("   L9T5-F10 (boards A and B generator owners, cosmetic): the net keeps the name +5V_IOC at 4.18 V; a rename would touch both I-03 drafts")
    w("   L9T5-F11 (Layer 6): R602 13.3 k at 0.1 percent and 25 ppm/K carries no order code (its code is owed)")
    w("   L9T5-F12 (the coordinator, for case row C-DEV, and rv-pwr's owner): the supervisors' HIGH (%.0f mA) is a state with no operating point at" % (P["rv"][2] * 1000))
    w("     the hot stop's air; the revised figure and its derivation are in 10g (%.4f A a controller, rev Y's rows, in place of 0.400 A); a" % R5["cdev"][0])
    w("     LABELLED SCENARIO until the coordinator issues the row")
    w("   L9T5-F14 (Layer 6; V6-m9): CON-017 (5) fits revision V or X only and (4) refuses both fabrics on Y or W, so T10's bound on rev Y's")
    w("     larger rows is CONSERVATIVE for the fitted rev V; rev X has no printed rows and rests on rev Y's (10a)")
    w("   L9T5-F18 (board B's generator owner): each TCAN334D's SHDN (pin 5) is on no net, resting on an internal pull-down TI says not to rely")
    w("     on (SLLSEQ7F 6.3.6); answered by apply_gen_sch_b_canshdn.py (DRAFTED, 10f)")
    w("   L9T5-F19 (board B's layout owner, Layer 10): %s on board B exceed the TCAN334's +-%.0f V bus pins; a short from one to a CAN" % (
        ", ".join(R5["high"]), Q["vbus_abs"]))
    w("     conductor is outside every printed figure: a clearance rule between those nets and the fabrics is a layout means, not credited here")
    w("   L9T5-F21 (Layer 5, IOHA section 12's owner): a supervisor whose firmware babbles on both fabrics (a running firmware that breaks FW-B21)")
    w("     is in no FMEA row; round 6 (10j) bounds a babbler through its FDCAN in hardware (the transmit-share limiters, 0.23 s); OPEN for a TX")
    w("     pin toggled as a GPIO under the limiter's least share (the peers' TXD observation and 2-of-2 vote, not drafted) and the FMEA row")
    w("   L9T5-F22 (record l9t5's T10 drafts' owner, Slot A, and Layer 6): DRAFTED in part 22 (apply_gen_sch_?_iocset.py, R602 14.0k, taken);")
    w("     revision X stays HELD until its own qualification (10j (f))")
    w("   L9T5-F25 (Slot A, record l9t5's I-03 check): check_l9t5_netlist.py reads the LDOs' VIN on +5V_IOC; with the containment delta")
    w("     (apply_gen_sch_b_iocguard.py, round 6) each sits behind its sense resistor on IOC{t}_LDO_IN: to restate when the delta is taken")
    w("   L9T5-F24 (Slot A, record l9t5's pre-regulator check): check_l9t5_netlist.py's 't10' divider (13.3k) is to be restated to 14.0k when")
    w("     the set point delta (apply_gen_sch_?_iocset.py, part 22) is taken; and the delta folded into iocpre (one writer per file)")
    w("   L9T5-F20 (Layer 6; L4-E9's change list): PD2 and PB14 become outputs on each supervisor (STM32H743-COMPATIBILITY.md's matrix) and")
    w("     R67, R68, R79, R80, R91, R92 (100 k) need order codes; the draft needs a row in L4-E9's change list after T10's iocpre (V6-m11)")
    w("")
    pred = {}
    pred["no contract, panel or firmware text in the tree bounds a supervisor's run mode, clock or voltage scale"] = unbounded
    pred["both revisions' run-mode tables are read; rv-pwr's HIGH is rev Y's 400 MHz all-peripherals maximum at TJ 85 C"] = abs(P["rv"][2] * 1000 - P["Y"][("on", 400)][2]) < 1e-9
    pred["the worst state the sheet prints has no operating point at or under TJmax at the inside air, on either revision"] = PT[("Y", ("on", 400))] is None and PT[("V", ("on", 400))] is None
    pred["as drawn the regulator is over its absolute maximum junction at the case's HIGH and over the criterion at the bounded state"] = (
        AS["the case's HIGH"] > P["tj_ldo"] and AS["the bounded state"] > TJ_GOAL)
    pred["the selected set point is the least E96 value that keeps the LDOs' input over their 600 mA requirement with the return as drawn"] = (
        abs(r602 - 13.3e3) < 1e-6 and at600 >= need600)
    pred["with the pre-regulator the regulator is inside the criterion at the bounded state and at its declared peak, not at the case's HIGH"] = (
        k3_ok and K3["the case's HIGH"] > TJ_GOAL)
    pred["the held dominant and bus-fault rows are judged on their own limits (125 C served, 150 C any state) and all six FAIL them"] = (
        FAULT["fails"] == ["FAILS"] * 6 and TJ_GOAL < FAULT["mom"] < FAULT["f1"] < P["tj_ldo"] < FAULT["f2"]
        and FAULT["d_f1"] < FAULT["d_f2"] < P["imax"])
    pred["each T10 draft refuses a target without I-03's draft, applies once after it, refuses twice and refuses the tree"] = len(STEP) == 2 and all(STEP)
    pred["both boards compose with the T10 drafts and read DRAWN, declarations included; the netlist's divider is the selected one"] = (
        all(comp.values()) and kit == "DRAWN" and DECL == {"a": "DRAWN", "b": "DRAWN"} and intent_ok and abs(drawn_r602 - r602) < 1e-6)
    pred["the old state (no T10 draft) and the mutated divider both FAIL the pre-regulator's check"] = kit_old == "FAIL" and kit_mut == "FAIL"
    pred["on C-DEV rev 1 U7, U601, the lead's pin 1 and the LDOs' input hold with the draft"] = c1 and c2 and c3
    pred["round 5: CON-004, IOHA rows 7 and 8 and test A7 are read; A7's method is a cut"] = (
        P["con004_class"] == ("constraint", "core", "BLOCKER") and "cut" in P["a7"][1] and "quorum" in P["row7"][1])
    pred["round 5: the reset state the reference manual prints (HSI at 64 MHz, VOS3) is inside the bound"] = Q["hsi"] <= BOUND[1] and BOUND[0] == "VOS3"
    pred["round 5: at the drop's worst corner the bounded state holds 125 C at the case's air on rev V's rows (fitted, L9T5-D7)"] = f13_ok
    pred["round 5: with the response every credible single fabric fault holds 125 C on rev V's rows and both fabrics hold 150 C on both"] = f16_ok and f17_ok
    pred["round 5 (part 21, (1)): rev Y's rows, the cover for a rev X part, do not hold 125 C at that corner (a rev X part waits on V-B20)"] = cover_fails
    pred["round 5: without a row the held bus-fault rows still FAIL (the response, not the parts, closes them)"] = all(
        tj_l(h, air) > TJ_GOAL for rev in "YV" for fid, h, _d, _r in R5["fault_rows"][rev] if fid in ("B1", "B2", "B5"))
    pred["round 5: the SHDN draft composes and reads DRAWN; the state before it and both mutations FAIL; the contract draft applies once"] = drafted_ok and R5["ok5"]
    pred["round 5 (part 21, (4)): the contract draft carries this record's figures and C-DEV rev 2 as issued carries this output's"] = all(R5["match"])
    pred["round 5 (part 22): the babbling row FAILS 125 C on rev V with iocpre alone and every rev V row holds with the set point delta"] = (
        p22["bab"][FITTED_REV][0] > TJ_GOAL and p22["fit14"] and not p22["fit13"])
    pred["round 5 (part 22): the delta composes, reads 14.0k, refuses without iocpre and the tree; both mutations FAIL; T10-A3 holds restated"] = (
        p22["ok"] and p22["v_set"] == "DRAWN" and p22["v_m1"] == "FAIL" and p22["v_m2"] == "FAIL" and p22["decl_ok"] and p22["tree_refused"]
        and p22["a3"][2] >= p22["a3"][1])
    r6 = R5["r6"]
    pred["round 6 (cx45 Q3): the schedule's dominant bound is inside FW-B21's share at 500 kbit/s (a traffic MODEL, not quorum service)"] = r6["dom"][0] <= r6["dom"][1]
    pred["round 6: the share limiter's MODEL leaves the legitimate share enabled, trips over it, and drives SHDN past VIH and under VIL"] = (
        r6["rel_ok"] and r6["d"][0] > SHARE and r6["d"][1] < FRAME_D_MIN and r6["sd"][0] > 2.0 and r6["sd"][1] < 0.8)
    pred["round 6: every served state is under the rail trip's least current (a constant-current MODEL; no sustained bound claimed)"] = r6["serve_max"] < r6["win"][0]
    pred["round 6 (cx46 7): the countermodel stays under the trip's least filtered current and over 125 C: the sustained bound is not shown"] = (
        r6["cm"][2] < r6["win"][0] and r6["cm"][1] > TJ_GOAL and r6["cm"][3] < 105.0)
    pred["round 6 (cx46 6): the drafted network does not meet V-B23's 0.2 s: that response claim is withdrawn"] = r6["t_vb23"] > 0.2
    pred["round 6: T10-A3 at the trip's average maximum with the sense drop, and the other LDOs during a response (PROVISIONAL at a peak)"] = (
        r6["a3"][1] >= r6["a3"][0] and r6["other"][1] >= r6["other"][0])
    pred["round 6: the containment delta composes, reads DRAWN by pin, its six mutations FAIL, and refuses (a drafted circuit, not closure)"] = (
        r6["v6"] == "DRAWN" and all(v == "FAIL" for _l, v in r6["vm"]) and all(r6["refused"]) and r6["ok6"])
    w("12. THE PREDICATES")
    for k, v in pred.items():
        w("   %-134s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_t10: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
