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
 10. the state of L9T5-F06, the findings for other authors, and the predicates test_l9t5.py holds.
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_t10.py  (l9t5_t10.out is its output, regenerated with
_bin/regen_out.py after l9t5_drafts.out). Labels: PRINTED (a maker's limit), TYPICAL, DECLARED, MODEL, ASSUMPTION, SESSION."""
import hashlib
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
          "tps62933": "v2/vendor/ti/ti-tps62933.pdf"}
DOCS = {"contract": "v2/docs/HW-FW-CONTRACT.md", "panel": "v2/docs/PANEL.md", "arch": "v2/docs/ARCH-PCB-B-IOHA.md", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "l4e12": "v2/docs/records/l4e12/l4e12_thermal.out", "rvpwr": "v2/docs/records/rv-pwr/pwr_budget.py", "gndret": "v2/docs/records/l8r2/l8r2_gndret.out",
        "drafts": "v2/docs/records/l9t5/l9t5_drafts.py", "drafts_out": "v2/docs/records/l9t5/l9t5_drafts.out",
        "pre_a": "v2/docs/records/l9t5/apply_gen_sch_a_iocpre.py", "pre_b": "v2/docs/records/l9t5/apply_gen_sch_b_iocpre.py"}
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
    need(t, r"2\. Guaranteed by characterization results", "the maxima's basis (characterization)")
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
    P["vout_hi"] = float(need(sec, r"VOUT\s+VOUT\s*\n.*?\n.*?\*([\d.]+)%\s+\*([\d.]+)%", "VOUT's band", re.S).group(2)) / 100.0
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
    w("3. ST'S PRINTED ROWS (DS12110 Rev 10; Run mode, code with data processing from ITCM, the regulator ON; mA; the maxima 'guaranteed by")
    w("   characterization results', rev Y's 400 MHz all-peripherals figures at TJ 25 and 105 C tested in production: PRINTED). The order code STM32H743VIT6 does")
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
    w("   %.0f C (p.3); SOT25 junction to ambient %.0f C/W, no heat sink (p.3); junction %.0f C (absolute maximum, p.3); thermal shutdown %.0f C (TYPICAL);" % (
        P["ta_ldo"], P["theta_ldo"], P["tj_ldo"], P["tsd"]))
    w("   foldback short current %.0f mA (TYPICAL). It drops its whole input to 3.3 V: at the %.4f V maximum, %.4f V times its current" % (P["ishort"] * 1000, hi5, hi5 - 3.3))
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
    k3_ok = K3["the bounded state"] <= TJ_GOAL and K3["the declared peak"] <= TJ_GOAL and d_bound <= ceil_i(hi3, TJ_GOAL)
    w("   SELECTED (SESSION): K3 WITH K2's ROW AS ITS CONDITION. Why: the state must be bounded under every option, because the controller itself")
    w("   has no operating point above it (section 4); with the bound the demand is %.4f A, which K2 alone %s (%.1f C) and K3" % (
        d_bound, "does not hold" if AS["the bounded state"] > P["tj_ldo"] else "holds without margin", AS["the bounded state"]))
    w("   holds at %.1f C on a one-resistor change in a draft this record already owns; K1 covers currents the controller cannot draw at this" % K3["the bounded state"])
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
    w("          current in that state; a supervisor forced out of the bound (a firmware fault) must end in the LDO's thermal shutdown or the")
    w("          controller's reset with the voters at their default: Layer 5's FMEA row, not shown here")
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
    # 10. state, findings, predicates
    w("10. THE STATE OF L9T5-F06 (T10)")
    w("   L9T5-F06 STAYS OPEN: the conditions are verified from the sources (the state is unbounded), a correction is selected with its acceptance")
    w("   criterion, and its circuit half is drafted and read by its author only. No independent check has read it; Layer 5 has not accepted the")
    w("   row; nothing is applied. This is the first attempt at this correction")
    w("   FINDINGS FOR OTHER AUTHORS")
    w("   L9T5-F09 (Layer 5, HW-FW-CONTRACT.md 3.3): the supervisors' state is bounded by no row; the row text above (T10-A1); the FMEA row for a")
    w("     supervisor out of its bound (T10-A5)")
    w("   L9T5-F10 (boards A and B generator owners, cosmetic): the net keeps the name +5V_IOC at 4.18 V; a rename would touch both I-03 drafts")
    w("   L9T5-F11 (Layer 6): R602 13.3 k at 0.1 percent and 25 ppm/K carries no order code (its code is owed)")
    w("   L9T5-F12 (Layer 9's budget, this author's, and rv-pwr's owner): the supervisors' HIGH (%.0f mA) is a state with no operating point at the" % (P["rv"][2] * 1000))
    w("     hot stop's air; once Layer 5 accepts T10-A1 the budget's HIGH for them is the bounded state's figure (%.4f A a supervisor with its" % d_bound)
    w("     auxiliaries), which lowers C-DEV's and every state's device or IOC load; not changed here (a case row's inputs)")
    w("   L9T5-F13 (board B's generator owner, rv-pwr): the 60 mA declared for a supervisor's other parts is under two TCAN334's printed dominant")
    w("     current (%.0f mA) and far under their bus-fault row (%.0f mA): a momentary and a fault figure the declarations do not carry" % (2 * P["can_dom_hi"] * 1000, 2 * P["can_fault"] * 1000))
    w("   L9T5-F14 (Layer 6): the order code STM32H743VIT6 admits silicon revisions Y and V, whose printed currents differ (Tables 30 and 129)")
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
    pred["each T10 draft refuses a target without I-03's draft, applies once after it, refuses twice and refuses the tree"] = len(STEP) == 2 and all(STEP)
    pred["both boards compose with the T10 drafts and read DRAWN, declarations included; the netlist's divider is the selected one"] = (
        all(comp.values()) and kit == "DRAWN" and DECL == {"a": "DRAWN", "b": "DRAWN"} and intent_ok and abs(drawn_r602 - r602) < 1e-6)
    pred["the old state (no T10 draft) and the mutated divider both FAIL the pre-regulator's check"] = kit_old == "FAIL" and kit_mut == "FAIL"
    pred["on C-DEV rev 1 U7, U601, the lead's pin 1 and the LDOs' input hold with the draft"] = c1 and c2 and c3
    w("11. THE PREDICATES")
    for k, v in pred.items():
        w("   %-134s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_t10: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
