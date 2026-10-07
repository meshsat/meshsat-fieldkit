#!/usr/bin/env python3
"""l9t5_hoe.py: Layer 4 task L4A-59, the ledger's HO-E (the supervisor's STM32H743 past its own 105 C VOS0 junction limit under the
protection): the comparison of at most three materially different approaches and the selection (record l9t5; MESHSAT-1357, W140,
7 October 2026). PROTOTYPE DESIGN: nothing in this kit has been built, bought, powered or measured; no figure printed here is a
measurement.

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the makers' texts as the records' helper returns them, the records and filed pages read);
  2. the failed case reproduced from T10 and cx46, the VOS0 rows ST prints and the current the protection now admits (W138's limiter);
  3. H-1, a hardware-forced voltage scale: what RM0433 Rev 8, DS12110 Rev 11 and AN4938 Rev 7 print about how a voltage scale is
     selected, every sentence quoted with its page, and the option bytes' fields; the verdict;
  4. H-3, a thermal-headroom part or heat path: the junction-to-ambient VOS0 would need on the printed rows against Table 222's
     printed resistances; the verdict;
  5. H-2, a firmware bound with an independent ending: the firmware bound, the IWDG, the peers (W137's vote) and a VCORE monitor
     drafted here (a TPS37 on each controller's VCAP holding its NRST), with its threshold band, its timing on printed rows, its
     power-up, its own faults and their self-test, and the controller's thermal time; the verdict;
  6. the acceptance read state by state ("the controller inside 105 C in every served state and every state the protection admits");
  7. the selection (SESSION, with its authority fields) and the owner item prepared but not raised;
  8. the draft apply_gen_sch_b_vcoremon.py composed on board B in L4-E9's change-list order (after iocguard; also with W137's canmb and
     W138's regstage), the regenerated netlist read by pin, the mutations that must FAIL and the refusals;
  9. findings for other authors and the supplier's tasks;
 10. the predicates its test holds (v2/ecad/tools/tests/test_l9t5_hoe.py).
W145 (7 October 2026) corrected it on the focused check L4A-100 (W144, `_runs/claude/w144chkhoe/`, findings F1 to F11, conditions C1 to
C5): the CTR1 reset hold drafted and the reset-loop row added (F1), U-02's local air (F2), the self-test's PASSED pattern (F3, RM0433
Table 56) and its window from the Scale 1 write (F11), the revision the trip window rests on (F4), the reset state printed (F5), the
register rows for S-f and S-g (F6), Table 120's 544 mA (F7), one supply corner for every thermal limit (F8), PWR_CR3's lock (F9) and
H-3 not established (F10).
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_hoe.py  (a few seconds; l9t5_hoe.out is its output, regenerated with
_bin/regen_out.py). Labels: PRINTED (a maker's limit or tested row), TYPICAL, DIAGRAM (read from a maker's drawn figure, no number in a
table), DECLARED, DRAFTED (a contract row or a circuit, not applied), MODEL, ASSUMPTION, SESSION."""
import hashlib
import importlib.util
import math
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
import l9t5_drafts as D  # noqa: E402  (its compositions, netlists and mutations)
CHK = D.CHK

# W34's convention (Q-41 item 1): the makers' PDFs this script reads as text, each with its options, taken once on the runner by
# v2/docs/records/_lib/retake_pdf_text.py beside its PDF; _lib/pdftext.py returns the text byte for byte and refuses when it is absent.
PDFTEXT = {
    "v2/vendor/st/st-rm0433-rev8.pdf": [["-layout", "-f", "215", "-l", "216"], ["-layout", "-f", "256", "-l", "256"], ["-layout", "-f", "260", "-l", "260"],
                                        ["-layout", "-f", "262", "-l", "264"], ["-layout", "-f", "279", "-l", "280"],
                                        ["-layout", "-f", "306", "-l", "306"], ["-layout", "-f", "307", "-l", "309"],
                                        ["-layout", "-f", "329", "-l", "332"], ["-layout", "-f", "449", "-l", "450"],
                                        ["-layout", "-f", "560", "-l", "560"], ["-layout", "-f", "1896", "-l", "1896"]],
    "v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf": [["-layout", "-f", "29", "-l", "29"], ["-layout", "-f", "105", "-l", "105"],
                                                       ["-layout", "-f", "208", "-l", "210"],
                                                       ["-layout", "-f", "212", "-l", "212"], ["-layout", "-f", "215", "-l", "215"],
                                                       ["-layout", "-f", "216", "-l", "216"],
                                                       ["-layout", "-f", "241", "-l", "241"], ["-layout", "-f", "248", "-l", "248"],
                                                       ["-layout", "-f", "344", "-l", "345"]],
    "v2/vendor/st/st-an4938-rev7.pdf": [["-layout", "-f", "10", "-l", "10"], ["-layout", "-f", "19", "-l", "19"]],
    "v2/vendor/ti/ti-tps37-snvsbj1e.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tps3808.pdf": [["-layout", "-f", "1", "-l", "1"], ["-layout", "-f", "4", "-l", "4"], ["-layout", "-f", "5", "-l", "5"],
                                    ["-layout", "-f", "6", "-l", "6"], ["-layout", "-f", "7", "-l", "7"],
                                    ["-layout", "-f", "11", "-l", "11"], ["-layout", "-f", "12", "-l", "12"]],
    "v2/vendor/ti/held/ti-tps3703-sbvs249b.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PDFT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PDFT)
RM = "v2/vendor/st/st-rm0433-rev8.pdf"
DS = "v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf"
AN = "v2/vendor/st/st-an4938-rev7.pdf"
TPS = "v2/vendor/ti/ti-tps37-snvsbj1e.pdf"
TPS38 = "v2/vendor/ti/ti-tps3808.pdf"
TPS3703 = "v2/vendor/ti/held/ti-tps3703-sbvs249b.pdf"   # W148: held back, v2/docs/records/l9t5hoe/fetch_held_back.py
REC = "v2/docs/records/l9t5"
DOCS = {"draft": REC + "/apply_gen_sch_b_vcoremon.py", "guard": REC + "/apply_gen_sch_b_iocguard.py", "drafts": REC + "/l9t5_drafts.py",
        "t10out": REC + "/l9t5_t10.out", "t10py": REC + "/l9t5_t10.py", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "gennet": "v2/docs/records/l8p/gen_netlist.py", "ledger": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "cx46": "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md", "trace": "v2/docs/REQUIREMENTS-TRACE.md",
        "ioha": "v2/docs/ARCH-PCB-B-IOHA.md",
        "l4reg": REC + "/inputs/l4reg-L4REG-3b6eb8be.md", "l4regout": REC + "/inputs/l4reg-l4reg_compare-9fbda7a6.out",
        "regstage": REC + "/inputs/l4reg-apply_gen_sch_b_regstage-469594bb.py", "round6": REC + "/inputs/l4canmb-T10-ROUND6-0a94dd2c.md",
        "canmb": REC + "/inputs/l4canmb-apply_gen_sch_b_canmb-8fb8815a.py", "sources": REC + "/inputs/SOURCES-HOE.txt",
        "u23": "v2/docs/records/efuse/apply_gen_sch_b_u23ilm.py", "u24": "v2/docs/records/efuse/apply_gen_sch_b_u24ilm.py",
        "contract": "v2/docs/HW-FW-CONTRACT.md", "cdraft": REC + "/apply_hw_fw_contract_hoe.py", "ct10": REC + "/apply_hw_fw_contract_t10.py"}
TAGS = "ABC"
EN = chr(0x2013)       # the sheets' dash, written by its code point (no long dash in this file)
MINUS = chr(0x2212)    # ST's minus sign
MU = "[%s%s]" % (chr(0xB5), chr(0x3BC))
OHM = "[%s%s]" % (chr(0x3A9), chr(0x2126))
# ---- the session's choices (SESSION, under the owner's standing rule of 26 September 2026; section 7 gives each reason) ----
T_TEST_S = 3600.0      # W140-3: the monitor's self-test runs at every start and then once every T_TEST_S seconds per supervisor
T_HOLD_CHECK_S = 7e-3  # W148-3: the self-test's restart must come at least this long after its Scale 1 write (the hold stage timed)
RTC_TOL = 0.40         # W148-3: the RTC clock error the hold check is read against (its source is Layer 5's: LSE or LSI)
T_RESTORE_US = 10.0    # W145-2: after its window (t_resp from the Scale 1 write, F11) the self-test writes Scale 3 within this long (a
                       # static property of the image, read like FW-B20's); W140-3's VOSRDY 1 ms and 2 ms waits are withdrawn
TEMPCO_K = 65.0        # T10's convention for a 25 ppm/K resistor (l9t5_t10.out 10j: "the divider at 0.1 % and 25 ppm/K over 65 K")
CORNER = 3.3577        # W145-4 (F8): every thermal limit read at one supply corner, the top of W137's rail band (canmb section 6);
                       # W138's TPS73733 band 3.2505 to 3.3495 V lies inside it; the run tables' currents kept at their printed figures
# ---- labelled assumptions ----
TOL_PLAIN = 0.05       # ASSUMPTION (W137's convention): a resistor whose value names no tolerance ("10k") is taken at +-5 %
C_RST_TOL = 0.20       # ASSUMPTION: the reset capacitor's "100n" names no tolerance; taken at +-20 %
RHO_C_SI = 1.63        # ASSUMPTION, a handbook figure, no maker's document: silicon's heat capacity per volume, J/(cm3 K)


def refuse(msg):
    sys.stderr.write("l9t5_hoe: REFUSED: %s\n" % msg)
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


def page(pdf, first, last=None):
    return PDFT.pdf_text(ROOT, pdf, ["-layout", "-f", str(first), "-l", str(last or first)], PDFTEXT, REC)


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def quote(t, sentence, what):
    """the sentence as the sheet prints it, matched through the layout's line breaks and runs of blanks; refused when absent"""
    pat = r"\s+".join(re.escape(w) for w in sentence.split())
    need(t, pat, what, re.S)
    return sentence


def draft():
    sp = importlib.util.spec_from_file_location("l9t5_hoe_draft", os.path.join(ROOT, DOCS["draft"]))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def ohms(v):
    t = v.split()[0]
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([kKMR]?)", t)
    if not m:
        refuse("a resistor value this script cannot read: %r" % v)
    return float(m.group(1)) * {"k": 1e3, "K": 1e3, "M": 1e6, "R": 1.0, "": 1.0}[m.group(2)]


def farads(v):
    """a capacitor's value string ("100n", "2.2u") in farads"""
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([pnu])", v.split()[0]) if v.split() else None
    if not m:
        refuse("a capacitor value this script cannot read: %r" % v)
    return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6}[m.group(2)]


def t10_model():
    """T10's own bounded-state model (l9t5_t10.py's figures, figures5 and mcu_i), imported by path; nothing of it is changed"""
    sp = importlib.util.spec_from_file_location("l9t5_hoe_t10", os.path.join(ROOT, DOCS["t10py"]))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    P = m.figures()
    return m, P, m.figures5(P)


def bpoint(T, P, Q, vdd, air):
    """the bounded state's operating point TJ = air + theta x vdd x I(TJ) on T10's revision V model (MODEL on PRINTED), by bisection"""
    lo_, hi_ = air, 125.0

    def g(tj):
        return air + P["theta_mcu"] * vdd * T.mcu_i(P, Q, "V", tj) - tj
    if g(hi_) > 0:
        return None
    for _ in range(100):
        mid = 0.5 * (lo_ + hi_)
        if g(mid) > 0:
            lo_ = mid
        else:
            hi_ = mid
    return hi_, T.mcu_i(P, Q, "V", hi_)


def air_at(T, P, Q, vdd, tj_goal):
    """the local air at which the bounded state's junction reaches tj_goal (MODEL), by bisection over the air"""
    lo_, hi_ = 40.0, 100.0
    for _ in range(100):
        mid = 0.5 * (lo_ + hi_)
        pt = bpoint(T, P, Q, vdd, mid)
        if pt is not None and pt[0] <= tj_goal:
            lo_ = mid
        else:
            hi_ = mid
    return lo_


def tol(v):
    m = re.search(r"(\d+(?:\.\d+)?)%", v)
    return float(m.group(1)) / 100.0 if m else TOL_PLAIN


def ppm(v):
    m = re.search(r"(\d+)ppm", v)
    return float(m.group(1)) * 1e-6 if m else 0.0


# ------------------------------------------------------------------------------------------------ the makers' printed rows
def figures():
    F = {}
    t = page(DS, 208, 210)
    m = need(t, r"VOS3 \(max frequency\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+200 MHz\)\s+VOS2 \(max frequency\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+"
                r"300 MHz\)\s+Internal regulator ON \(LDO\)\s+VOS1 \(max frequency\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+400 MHz\)\s+"
                r"VOS0\(4\) \(max\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+frequency 480 MHz\)\(5\)", "DS12110 Table 112, VCORE with the LDO ON", re.S)
    g = [float(x) for x in m.groups()]
    F["vcore"] = {"VOS3": g[0:3], "VOS2": g[3:6], "VOS1": g[6:9], "VOS0": g[9:12]}
    F["note4"] = quote(t, "4. VOS0 is available only when the LDO regulator is ON.", "Table 112 note 4")
    F["note5"] = quote(t, "5. TJMax = 105 °C.", "Table 112 note 5")
    rows = re.findall(r"^\s+(S?VOS\d)\s+LDO\s+(\d+)\s+(\d+|N/A)\s+([\d.]+)\s*$", t, re.M)
    F["t113"] = {r[0]: (int(r[1]), r[2], float(r[3])) for r in rows}
    if F["t113"].get("VOS0") != (105, "480", 1.7) or F["t113"].get("VOS1", (0,))[0] != 125 or F["t113"].get("VOS3", (0,))[0] != 125:
        refuse("DS12110 Table 113 is not where it was: %r" % F["t113"])
    F["tj_abs"] = int(need(t, r"TJ\s+Maximum junction temperature\s+(\d+)", "Table 111 (absolute maximum TJ)").group(1))
    t = page(DS, 215)
    v0 = re.findall(r"^\s+480\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+-\s*$", t, re.M)
    v1 = re.findall(r"^\s+400\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", t, re.M)
    if len(v0) != 2 or len(v1) != 2:
        refuse("DS12110 Table 119: the VOS0 480 MHz and VOS1 400 MHz rows are not where they were")
    F["vos0_dis"], F["vos0_en"] = [float(x) / 1e3 for x in v0[0]], [float(x) / 1e3 for x in v0[1]]       # typ, max at 25, 85, 105 C
    F["vos1_en"] = [float(x) / 1e3 for x in v1[1]]                                                        # typ, max at 25, 85, 105, 125 C
    need(t, r"Table 119\. Typical and maximum current consumption in Run mode, code with data processing", "Table 119's title")
    need(t, r"2\. Guaranteed by characterization results, unless otherwise specified\.", "Table 119 note 2")
    t = page(DS, 344, 345)
    pairs = re.findall(r"^\s+([\d.]+)\s*\n[^\n]*?((?:LQFP|TFBGA|UFBGA)[\w+]+) - ", t, re.M)
    if len(pairs) != 24:
        refuse("DS12110 Table 222: %d value and package pairs, not 24" % len(pairs))
    pk = [p for _v, p in pairs[:8]]
    if [p for _v, p in pairs[8:16]] != pk or [p for _v, p in pairs[16:]] != pk:
        refuse("DS12110 Table 222: the three blocks do not list the same packages in the same order")
    F["ja"] = {p: float(v) for v, p in pairs[:8]}
    F["jb"] = {p: float(v) for v, p in pairs[8:16]}
    F["jc"] = {p: float(v) for v, p in pairs[16:]}
    need(t, r"ΘJA\s+°C/W", "Table 222 ThetaJA"); need(t, r"ΘJB\s+°C/W", "Table 222 ThetaJB"); need(t, r"ΘJC\s+°C/W", "Table 222 ThetaJC")
    t = page(DS, 212)
    F["bor0"] = [float(x) for x in need(t, r"Brown-out reset threshold 0\s+Rising edge\(1\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "Table 116 BOR0").groups()]
    t = page(DS, 241)
    F["vil_k"] = float(need(t, r"I/O input low level voltage except\s+-\s+-\s+(0\.\d)VDD\(1\)", "Table 147 VIL").group(1))
    need(t, r"TT_xx, FT_xxx and NRST I/O", "Table 147 names NRST with the I/O input rows")
    t = page(DS, 248)
    F["rpu"] = [float(x) * 1e3 for x in need(t, r"RPU\(2\)\s+VIN = VSS\s+(\d+)\s+(\d+)\s+(\d+)", "Table 152 RPU").groups()]
    F["vnf"] = float(need(t, r"1\.71 V < VDD < 3\.6 V\s+(\d+)\s+-\s+-\s+ns\s*\n\s*VNF\(NRST\)", "Table 152 VNF").group(1)) * 1e-9
    t = page(DS, 29)
    F["scale0"] = quote(t, "Scale 0: boosted performance (available only with LDO regulator)", "DS12110 3.5.3 Scale 0")
    # the TPS37 (TI SNVSBJ1E, August 2023)
    t = PDFT.pdf_text(ROOT, TPS, ["-layout"], PDFTEXT, REC)
    need(t, r"SNVSBJ1E %s OCTOBER 2020 %s REVISED AUGUST 2023" % (EN, EN), "the TPS37 sheet's revision")
    m = need(t, r"Input Threshold Positive\s+VIT = 2\.7 V to 36 V\s+-1\.5\s+1\.5\s+%\s*\n\s*VITP\s+\(Overvoltage\)\s*\n\s*VIT\s+= 800 mV \(3\)\s+"
                r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "TPS37 VITP at 800 mV", re.S)
    F["vitp"] = [float(x) for x in m.groups()]
    F["isense"] = float(need(t, r"ISENSE\s+VIT = 800 mV\s+(\d+)\s+nA", "TPS37 ISENSE at 800 mV").group(1)) * 1e-9
    F["hys_range"] = need(t, r"VHYS Range = 2% to 13%", "TPS37 hysteresis options at 0.8 V").group(0)
    need(t, r"\[VHYSMIN=Hyst%\*\.985 \* \(VIT\+\(OV\)MIN\)\]", "TPS37 Figure 7-1, VHYSMIN")
    need(t, r"\[VHYSMAX = Hyst%\*1\.015 \* \(VIT\+\(OV\)MIN \)\]", "TPS37 Figure 7-1, VHYSMAX")
    F["hys"] = (0.985, 1.015)
    m = need(t, r"VIT = 800 mV\s*\n\s+CCTS1 = CCTS2 = Open\s+(\d+)\s+(\d+)\s+%ss\s*\n\s+20%% Overdrive from VIT" % MU, "TPS37 tCTS at 800 mV")
    F["tcts"] = (float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6)
    m = need(t, r"VIT = 800 mV\s*\n\s+CCTR1 = CCTR2 = Open\s+(\d+)\s+%ss\s*\n\s+20%% Overdrive from Hysteresis" % MU, "TPS37 tCTR at 800 mV")
    F["tctr"] = float(m.group(1)) * 1e-6
    F["tsd"] = float(need(t, r"tSD\s+Startup Delay \(4\)\s+(\d+)\s+ms", "TPS37 tSD").group(1)) * 1e-3
    F["tsd_note"] = quote(t, "During the power-on sequence, VDD must be at or above VDD (MIN) for at least tSD before the output is in the "
                             "correct state based on VSENSE.", "TPS37 note 4 of 7.6")
    F["uvlo_q"] = quote(t, "When the voltage on VDD is less than the UVLO voltage, but greater than the power-on reset voltage (VPOR), the "
                           "output pins will be in reset, regardless of the voltage at SENSE pins.", "TPS37 8.3.1.1")
    F["vpor"] = float(need(t, r"VPOR\s+RESET, Active Low\s+([\d.]+)\s+V", "TPS37 VPOR").group(1))
    F["vdd_min"] = float(need(t, r"Voltage\s+VDD\s+([\d.]+)\s+65\s+V", "TPS37 recommended VDD").group(1))
    F["ireset_rec"] = float(need(t, r"Current\s+IRESET1, IRESET2, IRESET1, IRESET2\s+0\s+±(\d+)\s+mA", "TPS37 recommended IRESET").group(1)) * 1e-3
    F["ireset_abs"] = float(need(t, r"Current\s+IRESET1, IRESET2, IRESET1, IRESET2\s+(\d+)\s+mA", "TPS37 absolute IRESET").group(1)) * 1e-3
    m = need(t, r"VOL \(5\)\s+Low level output voltage\s+(\d+)\s+mV\s*\n\s+IRESET = 5 mA", "TPS37 VOL")
    F["vol"], F["vol_i"] = float(m.group(1)) * 1e-3, 5e-3
    F["idd"] = float(need(t, r"VIT = 800 mV\s*\n\s+([\d.]+)\s+([\d.]+)\s+%sA\s*\n\s+VDD \(MIN\) \S VDD \S VDD \(MAX\)\s*\n IDD\s+Supply current into VDD pin" % MU, "TPS37 IDD at 800 mV").group(2)) * 1e-6
    need(t, r"SENSE1\s+2\s+3\s+I", "TPS37 Table 6-1 SENSE1 (DSK 2)")
    need(t, r"VDD\s+1\s+1\s+I\s+Input Supply Voltage: Bypass with a 0\.1 %sF capacitor to GND\." % MU, "TPS37 Table 6-1 VDD")
    need(t, r"asserts when SENSE1 rises outside of the upper voltage threshold", "TPS37 RESET1 (OV)")
    need(t, r"^\s+01\s+800 mV\s+70\s+7\.0 V[^\n]*\n\s+\(divider\s*\n\s+bypass\)", "TPS37 Table 11-1, option 01 (800 mV, divider)")
    F["moq"] = quote(t, "Contact TI sales representatives or consult TI's E2E forum for details and availability; minimum order quantities "
                        "may apply.", "TPS37 section 5")
    F["diagram"] = need(t, r"tSD \+ tCTRx\s+tCTSx\s+tCTRx[\s\S]{0,900}Figure 7-3\. SENSEx Overvoltage \(OV\) Timing Diagram", "TPS37 Figure 7-3") and True
    # the reset hold (W145, F1): RCTR (7.5, p.8), Equations 1 to 3 and the full-discharge sentence (8.3.4.1, p.23), note 4's capacitor (p.9)
    m = need(t, r"RCTR\s+(\d+)\s+(\d+)\s+(\d+)\s+Kohms\s*\n\s+\(CTR1 / MR , CTR2 / MR \)", "TPS37 RCTR")
    F["rctr"] = [float(x) * 1e3 for x in m.groups()]
    eq = {}
    for k, lab in (("typ", "1"), ("min", "2"), ("max", "3")):
        m = need(t, r"tCTRx \(%s\) = -ln \((0\.\d+)\) x RCTRx \(%s\) x CCTRx_EXT \(%s\) \+ tCTRx \(no cap[^)]*\)?\)?\s+\(%s\)" % (k, k, k, lab),
                 "TPS37 Equation %s" % lab)
        eq[k] = float(m.group(1))
    F["eq"] = eq
    F["eq_page"] = need(t, r"Equation 2 and Equation 3:[\s\S]{0,1600}Submit Document Feedback\s+23\s*\n", "TPS37 Equations 2 and 3 on p.23") and 23
    F["full_q"] = quote(t, "To ensure the capacitor is fully discharged, the time period or duration of the voltage fault needs to be greater "
                           "than 5% of the programmed reset time delay.", "TPS37 8.3.4.1, the full discharge")
    F["short_q"] = quote(t, "When a voltage fault occurs, the previously charged up capacitor discharges and if the monitored voltage returns "
                            "from the fault condition before the delay capacitor discharges completely, the delay will be shorter than expected.",
                         "TPS37 8.3.4.1, the shorter delay")
    F["full_frac"] = 0.05
    F["tsd_cap_q"] = quote(t, "tSD time includes the propagation delay (CCTR1 = CCTR2 = Open). Capaicitor in CCTR1 or CCTR2 will add time to tSD.",
                           "TPS37 7.6 note 4, the capacitor's addition (TI's own spelling)")
    F["mr_q"] = quote(t, "Manual Reset: If this pin is driven low, the RESET1/RESET1 output will reset and become asserted.", "TPS37 Table 6-1 CTR1/MR")
    # DS12110 Rev 11: Tables 120 and 121 (p.216), the rev V header of Table 112's pages (p.209), rev Y's Table 14 (p.105)
    t = page(DS, 216)
    v1 = re.findall(r"^\s+400\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", t, re.M)
    v0 = re.findall(r"\b480\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+-\s*$", t, re.M)      # Table 120's (its enabled row follows 'Run mode')
    t121 = re.findall(r"VOS([01])\s+(480|400)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$", t, re.M)
    if len(v1) != 2 or len(v0) != 2 or len(t121) != 4:
        refuse("DS12110 Tables 120 and 121: the VOS1 400 MHz and VOS0 480 MHz rows are not where they were")
    need(t, r"Table 120\. Typical and maximum current consumption in Run mode, code with data processing\s*\n\s+running from flash memory, cache ON",
         "Table 120's title")
    need(t, r"Table 121\. Typical and maximum current consumption in Run mode, code with data processing\s*\n\s+running from flash memory, cache OFF",
         "Table 121's title")
    F["t120_vos1_en"] = [float(x) / 1e3 for x in v1[1]]          # typ, max at 25, 85, 105, 125 C
    F["t120_vos0_en"] = [float(x) / 1e3 for x in v0[1]]          # typ, max at 25, 85, 105 C
    F["t121"] = {(r[0], "en" if i >= 2 else "dis"): [float(x) / 1e3 for x in r[2:]] for i, r in enumerate(t121)}
    t = page(DS, 208, 210)
    F["revv_hdr"] = len(re.findall(r"Electrical characteristics \(rev V\)", t))
    t = page(DS, 105)
    need(t, r"6\.3\.1\s+General operating conditions\s*\n\s*\n\s+Table 14\. General operating conditions", "rev Y's Table 14 (p.105)")
    F["revy_hdr"] = "Electrical characteristics (rev Y)" in t or "105/357" in t
    F["revy_vos"] = re.findall(r"VOS\d|VCAP|VCORE", t[t.index("Table 14."):])
    # the TPS37 pages this record quotes, each read off the text's page breaks (pdftotext writes a form feed between pages)
    t = PDFT.pdf_text(ROOT, TPS, ["-layout"], PDFTEXT, REC)
    F["tps_pages"] = {lab: t.count("\x0c", 0, t.index(s)) + 1 for lab, s in (
        ("Table 6-1, p.5", "Manual Reset: If this pin is driven low"), ("7.3, p.6", "Recommended Operating Conditions\nover"),
        ("7.5, p.7", "VIT = 800 mV (3)"), ("7.5, p.8", "RCTR "), ("7.6, p.9", "Sense detect time delay"),
        ("note 4, p.9", "Capaicitor in CCTR1"), ("Figure 7-3, p.12", "Figure 7-3. SENSEx Overvoltage"),
        ("8.3.1.1, p.18", "the output pins will be in reset"), ("Equation 2, p.23", "tCTRx (min) = -ln (0.31)"),
        ("full discharge, p.23", "To ensure the capacitor is fully discharged"))}
    # W148: the hold stage's sheets. TI TPS3703 (SBVS249B, November 2020; held back, l9t5hoe/fetch_held_back.py) and TI TPS3808 (SBVS050N,
    # August 2026, committed): the printed delays, the manual reset's pulse and levels, the drive, the options and the orderables
    t = PDFT.pdf_text(ROOT, TPS3703, ["-layout"], PDFTEXT, REC)
    need(t, r"SBVS249B %s MAY 2020 %s REVISED NOVEMBER 2020" % (EN, EN), "the TPS3703 sheet's revision")
    pg = lambda s: t.count("\x0c", 0, t.index(s)) + 1
    td = {}
    for m in re.finditer(r"^ tD\s+Reset time delay, TPS3703([A-C]), TPS3703([E-G])\s+CT = (Open|10 k%s to VDD)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+ms\s*$"
                         % OHM, t, re.M):
        for letter in m.group(1, 2):
            td[(letter, "open" if m.group(3) == "Open" else "vdd")] = tuple(float(x) / 1e3 for x in m.group(4, 5, 6))
    need(t, r"^ tD\s+Reset time delay, TPS3703D, TPS3703H\s+50\s+%ss\s*$" % MU, "TPS3703 tD, options D and H (50 us, NOM only)")
    for letter in "DH":
        td[(letter, "open")] = td[(letter, "vdd")] = (None, 50e-6, None)
    if sorted(td) != sorted((x, c) for x in "ABCDEFGH" for c in ("open", "vdd")) or td[("F", "vdd")] != (0.014, 0.020, 0.026):
        refuse("TPS3703 7.6's reset time delay rows are not the ones this record read: %r" % td)
    F["t3_td"] = td
    F["t3_td_page"] = pg("Reset time delay, TPS3703B, TPS3703F")
    hdr = need(t, r"^ +PARAMETER +MIN +NOM +MAX +UNIT *$", "TPS3703 7.6's column header").group(0)
    col_end = {k: hdr.index(k) + len(k) for k in ("MIN", "NOM", "MAX")}

    def col(row_pat, what):
        mm = need(t, row_pat, what)
        end = mm.end(1) - mm.start(0)
        k = min(col_end, key=lambda c: abs(col_end[c] - end))
        return float(mm.group(1)), k
    F["t3_tmrw"] = col(r"^ tMR_W\s+MR pin pulse width duration to assert RESET\s+(\d+)", "TPS3703 tMR_W")
    F["t3_tpdmr"] = col(r"^ tPD \(MR\)\s+Propagation delay from MR low to assert RESET\s+(\d+)", "TPS3703 tPD(MR)")
    F["t3_tgimr"] = col(r"^ tGI \(MR\)\s+Glitch Immunity MR pin\s+(\d+)", "TPS3703 tGI(MR)")
    m = need(t, r"^ tPD\s+Propagation detect delay\(1\) \(2\)\s+(\d+)\s+(\d+)\s+%ss" % MU, "TPS3703 tPD")
    F["t3_tpd"] = (float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6)
    F["t3_vol"] = [(float(a), float(b) * 1e-3, float(c) * 1e-3) for a, b, c in re.findall(
        r"VDD = ([\d.]+) V, IOUT = ([\d.]+) mA\s+(\d+)\s+mV", t)]
    if [v[0] for v in F["t3_vol"]] != [1.7, 2.0, 5.0] or any(v[2] != 0.25 for v in F["t3_vol"]):
        refuse("TPS3703 7.5's VOL rows are not the ones this record read: %r" % F["t3_vol"])
    F["t3_vmrl"] = float(need(t, r"VMR_L\s+MR logic low input\s+([\d.]+)\s+V", "TPS3703 VMR_L").group(1))
    F["t3_vmrh"] = float(need(t, r"VMR_H\s+MR logic high input\s+([\d.]+)\s+V", "TPS3703 VMR_H").group(1))
    F["t3_rmr"] = float(need(t, r"RMR\s+Manual reset Internal pullup resistance\s+(\d+)\s+K%s" % OHM, "TPS3703 RMR (NOM only)").group(1)) * 1e3
    F["t3_irec"] = float(need(t, r"IRESET\s+Output pin current\s+([\d.]+)\s+(\d+)\s+mA", "TPS3703 7.3 IRESET").group(2)) * 1e-3
    F["t3_irec_min"] = float(need(t, r"IRESET\s+Output pin current\s+([\d.]+)\s+(\d+)\s+mA", "TPS3703 7.3 IRESET").group(1)) * 1e-3
    F["t3_iabs"] = float(need(t, r"Current\s+IRESET\s+%s(\d+)\s+mA" % chr(0xB1), "TPS3703 7.1 IRESET").group(1)) * 1e-3
    m = need(t, r"UVLO\s+Under Voltage Lockout\(3\)\s+VDD falling below 1\.7 V\s+([\d.]+)\s+([\d.]+)\s+V", "TPS3703 UVLO")
    F["t3_uvlo"] = (float(m.group(1)), float(m.group(2)))
    F["t3_vpor"] = float(need(t, r"VPOR\s+Power on reset voltage\(2\)\s+VOL\(max\) = 0\.25 V, IOUT = 15 %sA\s+([\d.]+)\s+V" % MU, "TPS3703 VPOR").group(1))
    F["t3_vdd"] = tuple(float(x) for x in need(t, r"VDD\s+Supply pin voltage\s+([\d.]+)\s+([\d.]+)\s+V", "TPS3703 7.3 VDD").groups())
    m = need(t, r"VIT\+\(OV\)\s+Positive- going threshold accuracy\s+(-[\d.]+)\s+%s([\d.]+)\s+([\d.]+)\s+%%" % chr(0xB1), "TPS3703 accuracy")
    F["t3_acc"] = float(m.group(3)) / 100
    F["t3_acc_lo"] = float(need(t, r"Positive- going threshold accuracy\s+VIT < 800 mV\s+-(\d+)\s+(\d+)\s+%", "TPS3703 accuracy under 800 mV").group(2)) / 100
    F["t3_hys"] = float(need(t, r"VHYS\s+Hysteresis Voltage\(1\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+%", "TPS3703 hysteresis").group(3)) / 100
    F["t3_hys_lo"] = float(need(t, r"VHYS\s+Hysteresis Voltage\(1\)\s+VIT < 800 mV\s+([\d.]+)\s+([\d.]+)\s+%", "TPS3703 hysteresis under 800 mV").group(2)) / 100
    F["t3_pkg"] = tuple(float(x) for x in need(t, r"TPS3703\s+WSON \(6\)\s+([\d.]+) mm \S ([\d.]+) mm", "TPS3703 package size").groups())
    F["t3_q"] = {
        "mr": quote(t, "A logic low on MR causes RESET to assert.", "TPS3703 8.3.5"),
        "mr2": quote(t, "After MR returns to a logic high and the SENSE pin voltage is within a valid window", "TPS3703 8.3.5"),
        "mr3": quote(t, "RESET is deasserted after the reset delay time (tD).", "TPS3703 8.3.5"),
        "noteB": quote(t, "To initiate and continue time reset counter both conditions must be met MR pin above VMR_H or floating", "TPS3703 Figure 8-2 note B"),
        "noteC": quote(t, "MR is ignored during output RESET low event", "TPS3703 Figure 8-2 note C"),
        "sense": quote(t, "Connect to VDD pin if monitoring VDD supply voltage.", "TPS3703 pin functions, SENSE"),
        "uvonly": quote(t, "SENSE > VIT-(UV) Open or above VMR_H VDD > VDD(MIN) High", "TPS3703 Table 8-1, UV only"),
        "latch": quote(t, "In latch mode, if the RESET pin is low or triggers low, the pin will stay low regardless if V SENSE is within the "
                          "acceptable voltage boundaries", "TPS3703 9.1.3"),
        "unlatch": quote(t, "To unlatch the device provide a voltage to the CT pin that is greater than the CT pin comparator threshold voltage, V CT.",
                         "TPS3703 9.1.3"),
        "moq": quote(t, "minimum order quantities apply.", "TPS3703 section 5"),
        "reeval": quote(t, "The configuration of the CT pin is re-evaluated by the device every time the voltage on the SENSE line enters the "
                           "valid window", "TPS3703 8.3.4"),
        "uvlo": quote(t, "When the voltage on V DD is less than the device UVLO voltage but greater than the power-on reset voltage (V POR), the "
                         "RESET pin will be held low , regardless of the voltage on SENSE pin.", "TPS3703 8.4.2"),
        "note4": quote(t, "During the power-on sequence, VDD must be at or above VDD (MIN) for at least tSD + tD before the output is in the correct state.",
                       "TPS3703 7.6 note 4")}
    need(t, r"CT pin connected to VDD pin requires a pullup resistor; 10 k%s is recommended\." % OHM, "TPS3703 7.3 note 1")
    need(t, r"Good analog design practice is to place a 0\.1-%sF ceramic capacitor close to\s+2\s+VDD\s+I\s+this pin\." % MU, "TPS3703 pin functions, VDD")
    need(t, r"To use the factory-programmed timing options, the CT pin must either be left unconnected or pulled up to VDD\s+through a 10 k%s pull-up resistor\."
         % OHM, "TPS3703 9.1.2.1")
    F["t3_pages"] = {lab: pg(s) for lab, s in (
        ("pin functions, p.4", "Connect to VDD pin if"), ("7.3, p.5", "CT pin connected to VDD pin requires"), ("7.5, p.6", "MR logic low input"),
        ("7.6, p.7", "MR pin pulse width duration to assert RESET"), ("8.3.5, p.16", "A logic low on MR"),
        ("Figure 8-2 notes, p.16", "MR is ignored during output RESET low event"), ("8.4.2, p.17", "RESET pin will be held low"),
        ("9.1.2.1, p.19", "To use the factory-programmed timing options"), ("9.1.3, p.20", "In latch mode, if the RESET pin"),
        ("section 5, p.3", "minimum order quantities apply."), ("8.3.4, p.15", "The configuration of the CT pin is re-evaluated"))}
    F["t3_orderable"] = sorted(set((m.group(1), m.group(2), int(m.group(3)), int(m.group(4)) / 100.0) for m in re.finditer(
        r"^\s+(TPS3703([A-H])(\d)(\d{3})DSER)\s+Active\s", t, re.M)))
    nom_codes = [int(c_) / 100.0 for c_, v_ in re.findall(r"(?:^|\s)(\d{3})\s+(\d\.\d{2}) V\s*$", t, re.M) if abs(int(c_) / 100.0 - float(v_)) < 1e-9]
    F["t3_noms"] = sorted(set(nom_codes))
    if not F["t3_orderable"] or ("TPS3703F6050DSER", "F", 6, 0.50) not in F["t3_orderable"] or 1.00 not in F["t3_noms"]:
        refuse("TPS3703's orderables or Table 12-1's nominal codes are not the ones this record read")
    # TI TPS3808 (committed pages): td (6.6, p.7), the manual reset's pulse and propagation, VOL, VIL, RMR, 7.3.3, 7.3.4, the package
    t7 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "7", "-l", "7"], PDFTEXT, REC)
    hdr8 = need(t7, r"^ +PARAMETER +TEST CONDITIONS +MIN +TYP +MAX UNIT *$", "TPS3808 6.6's column header").group(0)
    c8 = {k: hdr8.index(k) + len(k) for k in ("MIN", "TYP", "MAX")}

    def col8(row_pat, what):
        mm = need(t7, row_pat, what)
        end = mm.end(1) - mm.start(0)
        return mm.group(1), min(c8, key=lambda c: abs(c8[c] - end))
    F["t38_tw_mr"] = col8(r"^ +RESET\s+MR\s+VIH = 0\.7VDD, VIL = 0\.3VDD\s+([\d.]+)", "TPS3808 tw, MR")
    F["t38_tpd_mr"] = col8(r"^ +Propagation delay\s+MR to RESET\s+VIH = 0\.7VDD, VIL = 0\.3VDD\s+(\d+)", "TPS3808 MR to RESET")
    m = need(t7, r"CT = VDD\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "TPS3808 td at CT = VDD")
    F["t38_td"] = tuple(float(x) * 1e-3 for x in m.groups())
    t6 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "6", "-l", "6"], PDFTEXT, REC)
    F["t38_vol"] = (float(need(t6, r"1\.8V . VDD . 6\.5V, IOL = 1mA\s+([\d.]+)\s+V", "TPS3808 VOL at 1 mA").group(1)), 1e-3)
    F["t38_rmr"] = float(need(t6, r"R MR\s+MR Internal pullup resistance\s+(\d+)\s+(\d+)\s+k%s" % OHM, "TPS3808 RMR").group(1)) * 1e3
    need(t6, r"VIL\s+MR logic low input\s+0\s+0\.3VDD", "TPS3808 VIL of MR")
    t11 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "11", "-l", "11"], PDFTEXT, REC)
    t12 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "12", "-l", "12"], PDFTEXT, REC)
    t1 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "1", "-l", "1"], PDFTEXT, REC)
    F["t38_q"] = {"mr": quote(t11, "A logic low (0.3 VDD) on MR causes RESET to assert.", "TPS3808 7.3.3 (p.11)"),
                  "delay": quote(t12, "Once MR is again logic high and SENSE is above VIT + VHYS (the threshold hysteresis), a delay circuit is enabled "
                                      "that holds RESET low for a specified reset delay period.", "TPS3808 7.3.4 (p.12)")}
    F["t38_pkg"] = tuple(float(x) for x in need(t1, r"DBV \(SOT-23, 6\)\s+([\d.]+)mm \S ([\d.]+)mm", "TPS3808 DBV package size").groups())
    need(t11, r"11\s*$", "TPS3808 p.11's page number")
    return F


# ------------------------------------------------------------------------------------------------ the composition
def order(extra=(), mon=True, mon_first=False):
    """board B's drafts in L4-E9's change-list order: record l8r2's, l9t5's iocbuck (the change list's slot), then iocpre, canshdn,
    iocset, iocguard; any extra drafts (W137's canmb and W138's regstage, from inputs/); this draft; the efuse record's R-236 and
    R-237; Layer 6's three last"""
    seq = D.seq_of("b", "slot")
    at = seq.index(D.MINE["b"]) + 1
    mid = [os.path.join(ROOT, REC, f) for f in ("apply_gen_sch_b_iocpre.py", "apply_gen_sch_b_canshdn.py", "apply_gen_sch_b_iocset.py",
                                                "apply_gen_sch_b_iocguard.py")]
    if mon and mon_first:
        mid.append(os.path.join(ROOT, DOCS["draft"]))
    mid += [os.path.join(ROOT, x) for x in extra]
    if mon and not mon_first:
        mid.append(os.path.join(ROOT, DOCS["draft"]))
    mid += [os.path.join(ROOT, DOCS["u23"]), os.path.join(ROOT, DOCS["u24"])]
    return seq[:at] + mid + seq[at:]


def build(d, tag, extra=(), mon=True, mon_first=False):
    seq = order(extra, mon, mon_first)
    p, res, ok = D.compose("b", seq, d, tag)
    if not ok:
        return seq, res, False, None, None
    rc, net, _t = D.netlist("b", p, d, tag)
    if rc:
        return seq, res, False, net, None
    return seq, res, True, net, CHK.read(open(net, "rb").read())


def remove_part(path, d, tag, ref):
    """a netlist with one part taken out (its nodes and its component entry), the mutation 'the part not fitted'; the component entry
    is found by a scan that balances parentheses outside quoted strings"""
    raw = open(path, encoding="utf-8").read()
    nodes = re.findall(r'\(node \(ref "%s"\) \(pin "[^"]+"\)\)' % re.escape(ref), raw)
    if len(nodes) < 2 or len(set(nodes)) != len(nodes):
        refuse("the mutation's part %s is not on its nodes once each: %d" % (ref, len(nodes)))
    for n_ in nodes:
        raw = raw.replace(n_, "", 1)
    head = '(comp (ref "%s")' % ref
    if raw.count(head) != 1:
        refuse("the mutation's part %s has not one component entry" % ref)
    i = j = raw.index(head)
    depth, quoted = 0, False
    while True:
        ch = raw[j]
        if quoted:
            if ch == "\\":
                j += 1
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    raw = raw[:i] + raw[j + 1:]
    q = os.path.join(d, tag + ".net")
    open(q, "w", encoding="utf-8").write(raw)
    return q


def band(top, bottom, F, dt=TEMPCO_K):
    """(trip min, trip max, release min) in VCAP volts for a divider given as its two value strings, on the printed rows"""
    rt, rb = ohms(top), ohms(bottom)
    et = tol(top) + ppm(top) * dt
    eb = tol(bottom) + ppm(bottom) * dt
    lo, hi = rt * (1 - et) / (rb * (1 + eb)), rt * (1 + et) / (rb * (1 - eb))
    v_lo, _v_typ, v_hi = F["vitp"]
    i_s = F["isense"] * rt * (1 + et)
    trip_min = v_lo * (1 + lo) - i_s
    trip_max = v_hi * (1 + hi) + i_s
    hys_max = 0.02 * F["hys"][1] * v_lo
    rel_min = (v_lo - hys_max) * (1 + lo) - i_s
    return trip_min, trip_max, rel_min


def hold_of(nl, F, u, ct_net, v33):
    """the hold stage's printed minimum delay read off the netlist: its value's TPS3703 order code (the delay option letter) and what
    its CT pin sees (a resistor to its own rail: 'CT = 10 kOhm to VDD'; nothing: 'CT = Open'; anything else: not a factory option);
    None when the part is not a TPS3703, the option prints no minimum, or CT is neither"""
    m = re.match(r"TPS3703([A-H])\d{4}DSER\b", CHK.value(nl, u) or "")
    if not m:
        return None, "not a TPS3703 order code"
    mem = [x for x in CHK.members(nl, ct_net) if x != "%s.3" % u] if ct_net and ct_net != "NC" else []
    if not mem:
        how = "open"
    elif len(mem) == 1 and mem[0].startswith("R") and CHK.pin(nl, mem[0].split(".")[0], "1" if mem[0].endswith(".2") else "2") == v33 \
            and abs(ohms(CHK.value(nl, mem[0].split(".")[0])) - 10e3) <= 10e3 * 0.05:
        how = "vdd"
    else:
        return None, "CT carries %s, neither open nor 10 k to the rail" % mem
    lo = F["t3_td"][(m.group(1), how)][0]
    return lo, "option %s, CT %s" % (m.group(1), how)


def mon_check(nl, F, draft_mod):
    """the monitors read by pin on a netlist: per controller, its TPS37 on its own rail, SENSE1 on a node fed only by a divider from
    its own VCAP, SENSE2 on its own rail, RESET1 on a node carrying only it and the hold stage's manual reset (W148); the hold stage on
    its own rail with SENSE on it, its RESET through the series resistor to its own NRST (the controller's pin 14) and on nothing else,
    its CT through 10 k to the rail; the unused pins open, the bypasses at both VDDs; the divider's values read off the netlist give a
    trip band inside (VOS3's top, VOS1's bottom) and a release over VOS3's top; the hold stage's printed minimum delay, read off its
    order code and its CT, at least the reset-loop row's (W148-1)"""
    why = []
    v3, v1 = F["vcore"]["VOS3"][2], F["vcore"]["VOS1"][0]
    need_hold = F["t3_td"][(draft_mod.HOLD_PART[7], "vdd")][0]
    for k, t in enumerate(TAGS):
        u, rt, rb, rs, cb = "U%d" % (810 + 10 * k), "R%d" % (810 + 10 * k), "R%d" % (811 + 10 * k), "R%d" % (812 + 10 * k), "C%d" % (810 + k)
        uh, rct, ch = "U%d" % (811 + 10 * k), "R%d" % (813 + 10 * k), "C%d" % (816 + k)
        v33, vmon, mrst, nrst, vcap = "+3V3_IOC%s" % t, "IOC%s_VMON" % t, "IOC%s_MONRST" % t, "IOC%s_RST_n" % t, "IOC%s_VCAP" % t
        mout, mct = "IOC%s_MONOUT" % t, "IOC%s_MONCT" % t
        if not CHK.value(nl, u).startswith("TPS37 "):
            why.append("%s is %r, not a TPS37" % (u, CHK.value(nl, u)[:24]))
            continue
        why += CHK.rows(nl, [(u, "1", v33), (u, "2", vmon), (u, "3", v33), (u, "4", mrst), (u, "10", "GND"), (u, "11", "GND")])
        for p_ in ("5", "6", "7", "8", "9"):
            if CHK.pin(nl, u, p_) not in (None, "NC"):
                why.append("%s.%s is on %s, wanted open" % (u, p_, CHK.pin(nl, u, p_)))
        if CHK.members(nl, vmon) != sorted(["%s.2" % u, "%s.2" % rt, "%s.1" % rb]):
            why.append("%s carries %s, not the monitor's SENSE1 and its divider alone" % (vmon, CHK.members(nl, vmon)))
        why += CHK.rows(nl, [(rt, "1", vcap), (rb, "2", "GND"), (cb, "1", v33), (cb, "2", "GND")])
        # the hold stage (W148-1)
        if not (CHK.value(nl, uh) or "").startswith("TPS3703"):
            why.append("%s is %r, not the hold stage" % (uh, (CHK.value(nl, uh) or "not fitted")[:24]))
        else:
            why += CHK.rows(nl, [(uh, "1", v33), (uh, "2", v33), (uh, "4", mout), (uh, "5", "GND"), (uh, "6", mrst)])
            lo, how = hold_of(nl, F, uh, CHK.pin(nl, uh, "3"), v33)
            if lo is None or lo < need_hold:
                why.append("%s's printed minimum delay %s (%s) is under the reset-loop row's %.0f ms" % (
                    uh, "not printed" if lo is None else "%.1f ms" % (lo * 1e3), how, need_hold * 1e3))
        if CHK.members(nl, mrst) != sorted(["%s.4" % u, "%s.6" % uh]):
            why.append("%s carries %s, not RESET1 and the hold stage's MR alone (bypassed or latching)" % (mrst, CHK.members(nl, mrst)))
        if CHK.members(nl, mout) != sorted(["%s.4" % uh, "%s.1" % rs]):
            why.append("%s carries %s, not the hold stage's RESET and its series resistor alone" % (mout, CHK.members(nl, mout)))
        why += CHK.rows(nl, [(rs, "1", mout), (rs, "2", nrst), (rct, "1", v33), (rct, "2", mct), (ch, "1", v33), (ch, "2", "GND")])
        mcu = "U%d" % (41 + 10 * k)
        if CHK.pin(nl, mcu, "14") != nrst or CHK.pin(nl, mcu, "48") != vcap or CHK.pin(nl, mcu, "73") != vcap:
            why.append("%s's NRST or VCAP is not the net its monitor reads or drives" % mcu)
        try:
            lo, hi, rel = band(CHK.value(nl, rt), CHK.value(nl, rb), F)
        except SystemExit:
            why.append("%s/%s values not readable" % (rt, rb))
            continue
        if not (lo > v3 and hi < v1 and rel > v3):
            why.append("controller %s's band %.4f to %.4f V (release from %.4f V) is not inside (%.2f, %.2f) V" % (t, lo, hi, rel, v3, v1))
        if abs(ohms(CHK.value(nl, rs)) - ohms(draft_mod.SERIES)) > 1e-9:
            why.append("%s is %s, not the draft's %s" % (rs, CHK.value(nl, rs), draft_mod.SERIES))
        for ref in (u, rt, rb, rs, cb, uh, rct, ch):
            for n in nl["pins"].get(ref, {}).values():
                if n not in ("GND", "NC") and not re.match(r"(\+3V3_)?IOC%s_" % t, n) and n != v33:
                    why.append("%s touches %s, a net outside controller %s's domain" % (ref, n, t))
    return ("DRAWN" if not why else "FAIL"), why


# ------------------------------------------------------------------------------------------------ the report
def main():
    out = []
    w = out.append
    F = figures()
    dm = draft()
    T, PT10, QT10 = t10_model()
    t10 = text(DOCS["t10out"])
    reg = text(DOCS["l4regout"])
    r6 = text(DOCS["round6"])
    w("l9t5_hoe: Layer 4 task L4A-59, the ledger's HO-E: the supervisor's STM32H743 past its own 105 C VOS0 junction limit under the")
    w("protection; at most three approaches compared, the selection and its draft (record l9t5; MESHSAT-1357, W140)")
    w("prototype design; nothing built, bought, powered or measured; nothing applied to the tree; every junction figure is a MODEL on")
    w("printed thermal resistances, never a measured temperature")
    w("")
    # ---------------------------------------------------------------- 1. inputs
    w("1. INPUTS, pinned by sha256")
    pins = [RM, DS, AN, TPS, TPS38, TPS3703, "v2/docs/records/l9t5hoe/fetch_held_back.py"] + [DOCS[k] for k in ("draft", "guard", "drafts", "t10out", "t10py", "gen_b", "gennet", "ledger", "cx46", "l4reg",
                                                         "l4regout", "regstage", "round6", "canmb", "sources", "u23", "u24", "contract",
                                                         "cdraft", "ct10")]
    for rel in pins:
        w("   %s %s" % (sha(rel), rel))
    for tp, h, _held in PDFT.inputs(ROOT, PDFTEXT):
        if h is None:
            refuse("%s is absent; %s" % (tp, PDFT.retake_command(REC)))
        w("   %s %s" % (h[:16], tp))
    named = dict(re.findall(r"^(\S+) sha256 ([0-9a-f]{64})$", text(DOCS["sources"]), re.M))
    copies = [DOCS[k] for k in ("l4reg", "l4regout", "regstage", "round6", "canmb")]
    copies_ok = sorted(named) == sorted(os.path.basename(c) for c in copies) and all(
        hashlib.sha256(open(os.path.join(ROOT, c), "rb").read()).hexdigest() == named[os.path.basename(c)] for c in copies)
    w("   the five copies from W137's and W138's branches equal the sha256 inputs/SOURCES-HOE.txt names: %s" % ("yes" if copies_ok else "NO"))
    w("")
    # ---------------------------------------------------------------- 2. the failed case
    air = float(need(t10, r"THE JUNCTION TEMPERATURE at L4-E12's inside air, ([\d.]+) C", "T10's inside air").group(1))
    th = float(need(t10, r"LQFP100 junction to ambient ([\d.]+) C/W \(PRINTED\)", "T10's LQFP100 theta").group(1))
    vdd = 3.3
    i105_t10 = float(need(t10, r"its own 105 C VOS0 limit from ([\d.]+) A \(MODEL\)", "T10 10j (c)'s 105 C current").group(1))
    m = need(t10, r"its own 105 C VOS0 limit at this air \(([\d.]+) C at ([\d.]+) A\)", "T10 10j (e)'s residual")
    tj_t10, i_trip = float(m.group(1)), float(m.group(2))
    m = need(t10, r"V\s+L4-E12 E5 mixed 76\.25 C\s+([\d.]+) A \(([\d.]+) C\)", "T10 10c's bounded state on revision V")
    i_b, tj_b = float(m.group(1)), float(m.group(2))
    cx = text(DOCS["cx46"])
    need(cx, r"the MCU reaches its 105 C VOS0 PRINTED LIMIT at approximately 0\.1936 A, MODEL, below the trip band", "cx46 finding 17")
    m = need(reg, r"TPS2553-1 at 49\.9 kOhm IOS ([\d.]+) to ([\d.]+) A", "W138's limiter band (l4reg_compare.out)")
    ios = (float(m.group(1)), float(m.group(2)))
    need(text(DOCS["l4reg"]), r"L4REG-F7\*\* \(L4A-59, HO-E\): round 6's rail trip held each controller's average", "W138's finding L4REG-F7")
    if abs(F["ja"]["LQFP100"] - th) > 1e-9:
        refuse("T10's LQFP100 theta %.1f is not DS12110 Rev 11 Table 222's %.1f" % (th, F["ja"]["LQFP100"]))
    i105 = (105.0 - air) / (th * vdd)
    tj_at = lambda i: air + th * vdd * i
    w("2. THE FAILED CASE, REPRODUCED, AND WHAT THE PROTECTION NOW ADMITS")
    w("   T10 10j (c) and (e) (record l9t5, l9t5_t10.out): 'VOS0 under the trip takes the controller past its own 105 C VOS0 limit from %.4f A'," % i105_t10)
    w("     '(%.1f C at %.4f A)'; cx46 finding 17: 'the MCU reaches its 105 C VOS0 PRINTED LIMIT at approximately 0.1936 A, MODEL'" % (tj_t10, i_trip))
    w("   reproduced (MODEL on PRINTED): the junction at %.2f C inside air (L4-E12 E5, the case's) on LQFP100's %.1f C/W (DS12110 Rev 11" % (air, th))
    w("     Table 222, p.344) at %.1f V: 105 C at %.4f A; %.1f C at %.4f A (the removed rail trip's average maximum)" % (vdd, i105, tj_at(i_trip), i_trip))
    w("   the 105 C itself: DS12110 Rev 11 Table 112 note 5, p.210: \"%s\", on the VOS0 rows; Table 113, p.210: VOS0 LDO, Max TJ %d C," % (F["note5"], F["t113"]["VOS0"][0]))
    w("     480 MHz, VDDLDO from %.1f V; VOS1 to VOS3: %d C. Table 111 (absolute maximum ratings), p.208: TJ %d C" % (F["t113"]["VOS0"][2], F["t113"]["VOS1"][0], F["tj_abs"]))
    w("   the VOS0 rows ST prints (Table 119, p.215, revision V, LDO ON, the maxima by characterization, its note 2; mA):")
    for lab, row in (("480 MHz, all peripherals disabled", F["vos0_dis"]), ("480 MHz, all peripherals enabled", F["vos0_en"])):
        w("     %-36s typ %3.0f (TYPICAL)   max %3.0f / %3.0f / %3.0f at TJ 25 / 85 / 105 C (PRINTED)" % (lab, row[0] * 1e3, row[1] * 1e3, row[2] * 1e3, row[3] * 1e3))
    ops = {}
    for lab, row in (("dis", F["vos0_dis"]), ("en", F["vos0_en"])):
        cols = [(25.0, row[1]), (85.0, row[2]), (105.0, row[3])]
        best = min(tj_at(i) - tj for tj, i in cols)            # piecewise linear: its least value is at a printed column
        ops[lab] = (best, tj_at(row[3]))
    w("   the operating point on the printed maxima (TJ = air + theta x VDD x Imax(TJ), linear between the printed columns; MODEL):")
    w("     peripherals disabled: none at or under 105 C (the least excess over the column's own TJ +%.1f K; %.1f C at the 105 C column)" % ops["dis"])
    w("     peripherals enabled:  none at or under 105 C (the least excess +%.1f K; %.1f C at the 105 C column)" % ops["en"])
    w("   the protection now: W138's selection (record l4reg, SESSION W138-1, filed in inputs/) puts a TPS2553-1 ahead of each supervisor's")
    w("     regulator with IOS %.4f to %.4f A and removes round 6's rail trip (W138-2); its finding L4REG-F7 hands the controller's protection" % ios)
    w("     to this task. At %.4f A (all of it in the controller, the brief's convention) the junction would read %.1f C; the controller's own" % (ios[1], tj_at(ios[1])))
    w("     VOS0 maximum at 105 C, %.3f A, lies inside the limiter's band, so whether the limiter ever acts on a VOS0 state is not printed," % F["vos0_en"][3])
    w("     and from %.4f A to the band's bottom it never does" % i105)
    w("   so HO-E is not a current limit's problem: no printed VOS0 row has an operating point inside 105 C at this air, at any current a")
    w("   regulator stage passes. W127's finding 2 stands (0.1855 A served against %.4f A, a 4.4 %% band) and is not the whole of it: VOS0" % i105)
    w("   must be kept out, or ended before the junction moves. The approaches below are judged on that.")
    w("")
    # ---------------------------------------------------------------- 3. H-1
    t260, t262, t279, t307, t560, t215 = page(RM, 260), page(RM, 262, 264), page(RM, 279, 280), page(RM, 307, 309), page(RM, 560), page(RM, 215, 216)
    a10, a19 = page(AN, 10), page(AN, 19)
    Q1 = [
        ("RM0433 Rev 8 p.264, 6.4.2", t262, "The regulator output voltage can be scaled by software to different voltage levels (VOS0(a), VOS1, VOS2, "
         "and VOS3) that are configured through VOS bits in PWR D3 domain control register (PWR_D3CR)."),
        ("RM0433 Rev 8 p.264", t262, "By default VOS3 is selected after system reset. VOS can be changed on-the-fly to adapt to the required system performance."),
        ("RM0433 Rev 8 p.279, 6.6.2", t279, "After reset, the system starts on the lowest Run mode voltage scaling (VOS3). The voltage scaling can then be "
         "changed on-the-fly by software by programming VOS bits in PWR D3 domain control register (PWR_D3CR)"),
        ("RM0433 Rev 8 p.279", t279, "The system maximum frequency can be reached by boosting the voltage scaling level to VOS0. This is done through the ODEN "
         "bit in the SYSCFG_PWRCR register."),
        ("RM0433 Rev 8 p.280, Note", t279, "VOS0 can be enabled only when VOS1 is programmed in PWR D3 domain control register (PWR_D3CR) VOS bits."),
        ("RM0433 Rev 8 p.309, 6.8.6 PWR_D3CR", t307, "Bits 15:14 VOS: Voltage scaling selection according to performance"),
        ("RM0433 Rev 8 p.309", t307, "01: Scale 3 (default)"),
        ("RM0433 Rev 8 p.560, 12.3.10 SYSCFG_PWRCR", t560, "Bit 0 ODEN: Overdrive enable, this bit allows to activate the LDO regulator overdrive mode."),
        ("RM0433 Rev 8 p.560", t560, "This bit must be written only in VOS1 voltage scaling mode."),
        ("RM0433 Rev 8 p.560", t560, "1: Overdrive mode enabled (the LDO generates VOS0 for VCORE)"),
        ("RM0433 Rev 8 p.260, Table 34 (LDO Bypass)", t260, "VCORE supplied from external source"),
        ("RM0433 Rev 8 p.262", t262, "Due to the LDO default state after power-up (enabled by default), the external VCORE voltage must remain higher than "
         "1.1 V until the LDO is disabled by software."),
        ("RM0433 Rev 8 p.306, 6.8.4 PWR_CR3", page(RM, 306), "This register is reset only by POR. It is not reset by wakeup from Standby mode "
         "and by the RESET pad."),
        ("RM0433 Rev 8 p.307, 6.8.4 PWR_CR3", t307, "The lower byte of this register is written once after POR and shall be written before changing VOS "
         "level or ck_sys clock frequency."),
        ("DS12110 Rev 11 p.29, 3.5.3", page(DS, 29), F["scale0"]),
        ("DS12110 Rev 11 p.210, Table 112 note 4", page(DS, 208, 210), F["note4"]),
        ("AN4938 Rev 7 p.10, 2.1.4", a10, "The LDO voltage regulator is always enabled after reset with a default output level set to power scale 3 (VOS3)."),
        ("AN4938 Rev 7 p.19, 2.3.7", a19, "The power management unit can be bypassed. This feature can be configured by software."),
        ("AN4938 Rev 7 p.19", a19, "In Bypass mode, the internal voltage scaling is not managed internally, and the external voltage value must be "
         "consistent with the targeted maximum frequency"),
    ]
    w("3. H-1, A HARDWARE-FORCED VOLTAGE SCALE: what the maker's documents print (each sentence matched in its pinned text)")
    for where, src, s in Q1:
        quote(src, s, where)
        w("   %-46s \"%s\"" % (where + ":", s))
    m = need(t215, r"4\.9\.9\s+FLASH option status register \(FLASH_OPTSR_PRG\)", "RM0433 4.9.9")
    fields = re.findall(r"Bits? \d+(?::\d+)? ([A-Z][A-Z0-9_]+(?:\[\d:\d\])?):", t215[m.start():])
    fields = list(dict.fromkeys(fields))
    vos_like = [f for f in fields if re.search(r"VOS|ODEN|SCU|LDO|BYPASS|SDLEVEL", f)]
    w("   the option bytes (RM0433 Rev 8 p.215 to 216, 4.9.9 FLASH_OPTSR_PRG, the user option word a part keeps across resets): %d fields," % len(fields))
    w("     %s; a field that selects a voltage scale or the supply configuration: %s" % (", ".join(fields), ", ".join(vos_like) or "NONE"))
    t256 = page(RM, 256)
    t32 = t256[t256.index("Table 32. PWR input/output signals connected to package pins or balls"):t256.index("Table 33.")]
    pins32 = re.findall(r"^\s{6,}([A-Z][A-Z0-9_+,\-]+)\s{2,}(?:Input/ |inputs/ )?([A-Z][^\n]+?)\s*$", t32, re.M)
    pins32 = [(n, squash(dsc)) for n, dsc in pins32 if n not in ("Pin", "Supply", "Digital")]
    w("   the PWR pins (RM0433 Rev 8 p.256, Table 32, 'PWR input/output signals connected to package pins or balls'): %s" % "; ".join(
        "%s %s" % (n, dsc) for n, dsc in pins32))
    if [n for n, _d in pins32] != ["VDD", "VDDA", "VREF+,VREF-", "VBAT", "VDDLDO", "VCAP", "VDD50USB", "VDD33USB", "VSS", "AHB", "PDR_ON"]:
        refuse("RM0433 Table 32's pins are not the ones this record read: %r" % pins32)
    pin_scale = [n for n, dsc in pins32 if re.search(r"scal|VOS|overdrive", dsc, re.I)]
    w("   READING: the voltage scale is a software choice made after every reset (PWR_D3CR's VOS bits, then ODEN for VOS0); no pin, strap or")
    w("   option byte selects or caps it. The one hardware means the documents print is the Bypass supply (an external regulator on VCAP; VOS0")
    w("   'available only with LDO regulator'), and that configuration is itself written by software once after every POR, with the LDO enabled")
    w("   by default until then; in Bypass the clock is still the firmware's ('must be consistent with the targeted maximum frequency').")
    w("   PWR_CR3's LOCK (W144's F9, RM0433 p.306 and p.307 above): the supply configuration is reset only by POR, not by the RESET pad, and is")
    w("   written once after POR; after that first write no later firmware fault can change it before the next POR, so a Bypass")
    w("   configuration written first would keep the LDO, and with it VOS0, off until then. It is still not a bar: the first write is made")
    w("   by whatever image runs first, and an image that writes the LDO configuration (or none) keeps the LDO on.")
    w("   VERDICT H-1: DROPS OUT (the register's end condition: the documents show no hardware means). Not claimed: any hardware bar on VOS0.")
    w("   The Bypass route would only move the firmware dependency to the first write after POR, at the cost of three external core")
    w("   regulators, and ST's run-current rows are printed with the 'LDO regulator ON' (Table 119's title): not pursued.")
    w("")
    # ---------------------------------------------------------------- 4. H-3
    w("4. H-3, A THERMAL-HEADROOM PART OR HEAT PATH: the junction-to-ambient VOS0 would need at %.2f C air (MODEL on PRINTED)" % air)
    need_en = (105.0 - air) / (vdd * F["vos0_en"][3])
    need_dis = (105.0 - air) / (vdd * F["vos0_dis"][3])
    need_ios = (105.0 - air) / (vdd * ios[1])
    w("   VOS0 480 MHz, all peripherals enabled, %.3f A at 105 C:  at most %.2f C/W" % (F["vos0_en"][3], need_en))
    w("   VOS0 480 MHz, all peripherals disabled, %.3f A at 105 C: at most %.2f C/W" % (F["vos0_dis"][3], need_dis))
    w("   the protection's largest admitted current, %.4f A (the brief's convention, all in the controller): at most %.2f C/W" % (ios[1], need_ios))
    w("   printed (DS12110 Rev 11 Table 222, p.344 to 345; JESD51-2 still air, its reference 8.10.1):")
    for p in F["ja"]:
        w("     %-14s ThetaJA %5.1f   ThetaJB %5.1f   ThetaJC %5.1f C/W" % (p, F["ja"][p], F["jb"][p], F["jc"][p]))
    best = min(F["ja"], key=lambda p: F["ja"][p])
    need_c = (105.0 - air) / (CORNER * F["vos0_en"][3])
    w("   at one supply corner (W145-4, W144's F8): the same row at the rail's top %.4f V needs at most %.2f C/W (the figure carried below)" % (CORNER, need_c))
    w("   the least ThetaJA of any package is %s's %.1f C/W, %.1fx the need; the fitted LQFP100 reads %.1f C/W" % (best, F["ja"][best], F["ja"][best] / need_c, F["ja"]["LQFP100"]))
    w("   every ThetaJB printed (the least %.1f C/W, %s) is over the need: no path through the board reaches it on printed figures" % (
        min(F["jb"].values()), min(F["jb"], key=lambda p: F["jb"][p])))
    best_jc = min(F["jc"], key=lambda p: F["jc"][p])
    w("   a heat path through the case top (W144's F10): the LQFP100's ThetaJC %.1f C/W leaves %.2f C/W, the %s's %.1f C/W leaves %.2f C/W" % (
        F["jc"]["LQFP100"], need_c - F["jc"]["LQFP100"], best_jc, F["jc"][best_jc], need_c - F["jc"][best_jc]))
    w("     (a package change on board B's supervisors; W144's %.2f and %.2f C/W are the same on the 3.3 V figure), for the interface, a heat" % (
        need_en - F["jc"]["LQFP100"], need_en - F["jc"][best_jc]))
    w("     sink and its path to the %.2f C air inside the sealed case;" % air)
    w("     a path from the top to the case wall (cooler than the inside air) is a third form; no held document prints a heat sink, an")
    w("     interface material, a strap or a wall path for these parts (the one cooler held is the CM5's), and none prints board B's pockets")
    w("   the air at which VOS0's enabled maximum holds 105 C on the printed %.1f C/W: %.1f C, against the case's %.2f C" % (th, 105.0 - th * vdd * F["vos0_en"][3], air))
    w("   the regulator's own theta (W138's TPS73733DCQRM3, 76.0 C/W PRINTED, record l4reg) moves the REGULATOR's junction; the controller's")
    w("     105 C current, (105 - air) / (theta x VDD) = %.4f A, does not depend on it: no regulator part acts on HO-E" % i105)
    w("   VERDICT H-3: NOT ESTABLISHED ON PRINTED FIGURES (no package's ThetaJA and no printed path reaches %.2f C/W at this air; a top or" % need_c)
    w("   wall path would rest on a heat sink, an interface and a mechanical path that no held document prints: not impossible, not")
    w("   established, not selected).")
    w("")
    # ---------------------------------------------------------------- 5. H-2
    w("5. H-2, A FIRMWARE BOUND WITH AN INDEPENDENT ENDING")
    fwb20 = need(t10, r"Run each supervisor at\s+VOS3 with HCLK at most 144 MHz \(no PLL above it\)", "T10's drafted FW-B20 row", re.S)
    w("   5a. THE FIRMWARE BOUND (FW-B20, DRAFTED in record l9t5, unapplied): '%s'. It is a property of an image that does not exist" % squash(fwb20.group(0)))
    w("       yet; it is verified, not enforced: the image's writes to PWR_D3CR (p.309) and SYSCFG_PWRCR (p.560) read by a static check. Alone")
    w("       it ends nothing: a corrupted or wrong image can still select VOS0 (section 3)")
    q_iwdg = quote(page(RM, 1896), "If the \u201cHardware watchdog\u201d feature is enabled through the device option bits, the watchdog is automatically "
                                   "enabled at power-on, and generates a reset unless the IWDG key register (IWDG_KR) is written by the software before "
                                   "the counter reaches end of count or if the downcounter is reloaded inside the window.", "RM0433 45.3.4")
    w("   5b. THE IWDG (RM0433 Rev 8 p.1896, 45.3.4): \"%s\"" % q_iwdg)
    w("       a running firmware that selects VOS0 and keeps writing IWDG_KR is never reset by it: NOT AN ENDING for HO-E (it ends hangs)")
    need(r6, r"each controller's TXD on each fabric drives a 74LVC1G34 buffer", "W137's observation (T10-ROUND6.md section 2)")
    need(r6, r"W137-D3 \| the vote acts on SHDN, not on the LDO's EN", "W137-D3")
    w("   5c. THE PEERS (W137's M-B vote, fnd/l4canmb 0d079eaf, T10-ROUND6.md filed in inputs/): each peer observes the other controllers' TXD")
    w("       lines and votes their transceivers' SHDN (W137-D3: 'the vote acts on SHDN, not on the LDO's EN'). A controller in VOS0 can still")
    w("       send good frames, and a silenced transceiver leaves its controller running: NOT AN ENDING for HO-E. Their use here is detection")
    w("       of a missed self-test (5e), through the state frame they already read")
    # 5d the monitor
    tops = []
    for mant in (3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32):
        top = "%.1fk 0.1%% 25ppm" % (mant * 10)
        lo, hi, rel = band(top, dm.BOTTOM, F)
        v3, v1 = F["vcore"]["VOS3"][2], F["vcore"]["VOS1"][0]
        tops.append((min(lo - v3, v1 - hi, rel - v3), top, lo, hi, rel))
    sel = max(tops)
    if sel[1] != dm.TOP:
        refuse("the draft's divider top %s is not the selection's %s" % (dm.TOP, sel[1]))
    lo, hi, rel = sel[2], sel[3], sel[4]
    vc = F["vcore"]
    w("   5d. THE VCORE MONITOR, DRAFTED (apply_gen_sch_b_vcoremon.py): a TI TPS37 per supervisor, channel 1 overvoltage (option 01, 800 mV,")
    w("       an external divider), open-drain active-low RESET1 into a hold stage that drives that controller's NRST through %s (W148-1), VDD" % dm.SERIES)
    w("       on the controller's own 3.3 V.")
    w("       What it reads: VCAP, the core voltage ST prints per scale (DS12110 Rev 11 Table 112, p.209, LDO ON, min/typ/max):")
    for s in ("VOS3", "VOS2", "VOS1", "VOS0"):
        w("         %s %.2f / %.2f / %.2f V" % ((s,) + tuple(vc[s])))
    w("       TPS37 rows (SNVSBJ1E): VITP %.3f / %.3f / %.3f V at VIT 800 mV (7.5, p.7); ISENSE at most %.0f nA (p.7); hysteresis options %s," % (
        F["vitp"][0], F["vitp"][1], F["vitp"][2], F["isense"] * 1e9, F["hys_range"]))
    w("       VHYS between Hyst%% x %.3f and x %.3f of VIT+(OV)MIN (Figure 7-1, p.10); the 2 %% option is the draft's" % F["hys"])
    w("       the divider: the E96 top over %s that keeps the trip band inside (VOS3's top %.2f V, VOS1's bottom %.2f V) and the release" % (dm.BOTTOM, vc["VOS3"][2], vc["VOS1"][0]))
    w("       over VOS3's top, with the largest least margin (SESSION W140-2; resistors at 0.1 %% plus 25 ppm/K over %.0f K, ISENSE either way):" % TEMPCO_K)
    for mg, top, l_, h_, r_ in tops:
        w("         top %-17s trip %.4f to %.4f V, release from %.4f V, least margin %+.4f V%s" % (top, l_, h_, r_, mg, "   SELECTED" if top == dm.TOP else ""))
    od0 = vc["VOS0"][0] / hi - 1.0
    od1 = vc["VOS1"][0] / hi - 1.0
    w("       so every VCAP in VOS3's printed band leaves the monitor released (%.4f V over %.2f V), and every VCAP in VOS1's or VOS0's band" % (lo, vc["VOS3"][2]))
    w("       trips it (%.4f V under %.2f V): any VOS1 entry, and so any VOS0 entry (RM0433 p.280's note), resets the controller to VOS3" % (hi, vc["VOS1"][0]))
    w("       (p.279). VOS2's band (%.2f to %.2f V) straddles the trip: a VOS2 entry is caught only above %.4f V (section 6, S-f)" % (vc["VOS2"][0], vc["VOS2"][2], hi))
    q_sr = quote(t262, "When a system reset occurs, the voltage regulator is enabled and supplies VCORE.", "RM0433 p.263")
    q_d3 = quote(t307, "Reset value: 0x0000 4000 (Following reset VOSRDY will be read 1 by software).", "RM0433 p.309 PWR_D3CR reset value")
    q_od = quote(t560, "Reset Value: 0x0000 0000", "RM0433 p.560 SYSCFG_PWRCR reset value")
    w("       the reset state the ending relies on: \"%s\" (RM0433 p.263); PWR_D3CR \"%s\" (p.309: VOS = 01, Scale 3);" % (q_sr, q_d3))
    t329 = page(RM, 329, 332)
    q_sys = quote(t329, "A system reset (nreset) resets all registers to their reset values unless otherwise specified in the register "
                        "description.", "RM0433 8.4.2 p.329")
    q_nrst = quote(t329, "A reset from NRST pin (external reset)", "RM0433 8.4.2 p.329, the NRST source")
    q_ext = quote(t329, "In case of an external reset, the reset pulse is generated while the NRST pin is asserted Low.", "RM0433 8.4.2 p.329")
    q_t55 = quote(t329, "Resets VDD domain: IWDG1, LDO...", "RM0433 Table 55 p.330, the NRST row")
    q_t55b = quote(t329, "Debug features, Flash memory, RTC and backup RAM are not reset", "RM0433 Table 55 p.330, the NRST row")
    need(t329, r"Pin\s+NRST\s+x x x - x x x x x - - - - x", "RM0433 Table 55's NRST row")
    need(t329, r"330/3353", "RM0433 p.330 in the pinned text")
    w("       SYSCFG_PWRCR \"%s\" (p.560: ODEN = 0). Which resets restore them is PRINTED (W144's F5): \"%s\" with \"%s\" among" % (q_od, q_sys, q_nrst))
    w("       its sources (8.4.2, p.329), and \"%s\"; Table 55 (p.330), the NRST row: \"%s\", \"%s\". PWR_D3CR's and" % (q_ext, q_t55, q_t55b))
    w("       SYSCFG_PWRCR's descriptions name no exception, where PWR_CR3's does (p.306: \"reset only by POR\"): an NRST reset restores")
    w("       VOS = Scale 3 and ODEN = 0 by the manual's own words; S2's ACTVOS reading confirms a printed fact on the specimen")
    # timing
    rail = (3.2422, 3.3577)                  # W137's rail band (canmb section 6, the AP2112K); W138's TPS73733 band 3.2505 to 3.3495 lies inside it
    need(r6, r"Each rail 3\.2422 to 3\.3577 V", "W137's rail band")
    c_rst = 100e-9 * (1 + C_RST_TOL)
    pullups = (1.0 / (1.0 / (10e3 * (1 - TOL_PLAIN)) + 1.0 / F["rpu"][0]), 1.0 / (1.0 / (10e3 * (1 + TOL_PLAIN)) + 1.0 / F["rpu"][2]))
    # W140's and W145's chain, kept as the figures' history: the TPS37's RESET1 through 750 Ohm onto NRST; the open drain holds at most VOL
    # (300 mV) whenever it sinks 5 mA or less (p.7; ASSUMPTION: its current rises with its voltage); every corner, the slowest kept
    rs_w145 = 750.0
    t_fall_w145 = 0.0
    for v33 in rail:
        for r_up in pullups:
            r_low = rs_w145 * 1.01
            a_ = (F["vol"] / v33 * r_up + r_low) / (r_low + r_up)
            tau = c_rst * (r_low * r_up / (r_low + r_up))
            t_fall_w145 = max(t_fall_w145, tau * math.log((1 - a_) / (F["vil_k"] - a_)))
    t_resp_w145 = F["tcts"][1] + t_fall_w145 + F["vnf"]

    def fall_bound(v33, r_up, c, r_s, vol, i_vol):
        """NRST from the rail to VIL through r_s into an open drain that sinks at least min(i_vol, (V - vol) / r_s): its printed VOL row
        (at most vol at i_vol) and the record's ASSUMPTION that its current rises with its voltage; against the pull-up r_up and the
        reset capacitor c (MODEL, two exponential phases); None when the drain cannot pull NRST under VIL at all"""
        vil = F["vil_k"] * v33
        v0, t_ = v33, 0.0
        if vol + i_vol * r_s < v0:                   # phase 1: at least i_vol into the drain, against the pull-up
            v_eq = v33 - i_vol * r_up
            v1 = max(vol + i_vol * r_s, vil)
            t_ += r_up * c * math.log((v0 - v_eq) / (v1 - v_eq))
            v0 = v1
        if v0 > vil:                                 # phase 2: through r_s toward the drain's VOL
            v_inf = (v33 * r_s + vol * r_up) / (r_s + r_up)
            if v_inf >= vil:
                return None
            t_ += c * (r_s * r_up / (r_s + r_up)) * math.log((v0 - v_inf) / (vil - v_inf))
        return t_

    def slowest(r_s, vol, i_vol):
        ts = [fall_bound(v33, r_up, c_rst, r_s * 1.01, vol, i_vol) for v33 in rail for r_up in pullups]
        return None if None in ts else max(ts)
    # the selected chain (SESSION W148-1): RESET1 into the TPS3703's MR; the TPS3703's RESET through dm.SERIES onto NRST; its drive at
    # most 250 mV at 3 mA (the VDD = 2 V row, 7.5 p.6), ASSUMPTION: no weaker at the rail's 3.24 to 3.36 V (TI prints the same 250 mV at
    # 5 mA with VDD = 5 V)
    rs = ohms(dm.SERIES)
    vol3, i3 = F["t3_vol"][1][2], F["t3_vol"][1][1]
    t_fall = slowest(rs, vol3, i3)
    i_pk = rail[1] / (rs * (1 - tol(dm.SERIES)))                     # the drain at 0 V: the largest current it can sink through R812
    v_inf_w = max((v33 * rs * 1.01 + vol3 * r_up) / (rs * 1.01 + r_up) for v33 in rail for r_up in pullups)
    i_hold_min = min((v33 - (v33 * rs * 1.01 + vol3 * r_up) / (rs * 1.01 + r_up)) / r_up for v33 in rail for r_up in pullups)
    tpd_mr = F["t3_tpdmr"][0] * 1e-9
    t_resp = F["tcts"][1] + tpd_mr + t_fall + F["vnf"]
    # the fastest NRST fall (an ideal drain, the least capacitor and series resistor, the weakest pull-ups): the least time the controller
    # holds VCAP up after RESET1 asserts, so the least length of the MR pulse in a loop
    c_lo, r_lo = 100e-9 * (1 - C_RST_TOL), rs * (1 - tol(dm.SERIES))
    r_weak = pullups[1]
    a_lo = r_lo / (r_lo + r_weak)
    t_fall_min = c_lo * (r_lo * r_weak / (r_lo + r_weak)) * math.log((1 - a_lo) / (F["vil_k"] - a_lo))
    hold = F["t3_td"][(dm.HOLD_PART[7], "vdd")]                      # the option letter of the orderable code, CT pulled to VDD
    w("       the ending's timing, VCAP over the trip to the controller in reset (the chain of SESSION W148-1: the TPS37's RESET1 drives the")
    w("       hold stage's manual reset, the hold stage's RESET drives NRST; section 5h compares it):")
    w("         TPS37 sense delay tCTS %.0f us typ, %.0f us max at VIT 800 mV with CTS open, '20%% Overdrive from VIT' (7.6, p.9, PRINTED);" % (
        F["tcts"][0] * 1e6, F["tcts"][1] * 1e6))
    w("           VOS0's bottom %.2f V is %.1f %% over the trip's top, VOS1's %.2f V is %.1f %%: under 20 %%, so the printed maximum does NOT cover" % (
        vc["VOS0"][0], od0 * 100, vc["VOS1"][0], od1 * 100))
    w("           these entries (supplier task S2); 17 us is carried below as the figure S2 must confirm, never as a bound")
    w("         RESET1 into the TPS3703's MR (TI SBVS249B): RESET1 at most %.0f mV while it sinks 5 mA or less (TPS37 p.7) against VMR_L at most" % (F["vol"] * 1e3))
    w("           %.1f V (7.5, p.6; MR is pulled up inside, RMR %.0f kOhm NOM, so RESET1 sinks tens of uA); '%s' (8.3.5, p.16); the pulse" % (
        F["t3_vmrl"], F["t3_rmr"] / 1e3, F["t3_q"]["mr"]))
    w("           must last tMR_W, at least %.0f us (7.6, p.7, %s column)" % (F["t3_tmrw"][0], F["t3_tmrw"][1]))
    w("         MR to RESET: tPD(MR) %.0f ns (7.6, p.7, %s column; no maximum printed: TYPICAL, inside S2's measured interval)" % (F["t3_tpdmr"][0], F["t3_tpdmr"][1]))
    w("         NRST pulled from the rail to VIL %.1f x VDD (Table 147, p.241: '%.1fVDD', NRST with the I/O rows) through %s by the TPS3703's open" % (
        F["vil_k"], F["vil_k"], dm.SERIES))
    w("           drain: at most %.0f mV at %.0f mA with VDD = %.0f V (7.5, p.6; the same %.0f mV at %.0f mA with VDD = %.0f V; ASSUMPTION: its drive at" % (
        vol3 * 1e3, i3 * 1e3, F["t3_vol"][1][0], F["t3_vol"][2][2] * 1e3, F["t3_vol"][2][1] * 1e3, F["t3_vol"][2][0]))
    w("           the rail's 3.24 to 3.36 V is no weaker than at 2 V, and its current rises with its voltage), against NRST's 10 k (+-5 %,")
    w("           ASSUMPTION) and RPU %.0f to %.0f kOhm (Table 152, p.248), every corner of the rail and the pull-ups and the 100 nF reset" % (
        F["rpu"][0] / 1e3, F["rpu"][2] / 1e3))
    w("           capacitor (+-20 %%, ASSUMPTION): at most %.1f us (MODEL); the peak sink %.2f mA under the recommended %.0f mA (7.3, p.5) and" % (
        t_fall * 1e6, i_pk * 1e3, F["t3_irec"] * 1e3))
    w("           the absolute %.0f mA (7.1); held, NRST sits at most at %.3f V under VIL and the drain sinks at least %.3f mA, over the" % (
        F["t3_iabs"] * 1e3, v_inf_w, i_hold_min * 1e3))
    w("           recommended minimum %.1f mA (7.3)" % (F["t3_irec_min"] * 1e3))
    w("         NRST's 'Input not filtered pulse' at least %.0f ns (Table 152 and its note 2, p.248)" % (F["vnf"] * 1e9))
    w("         t_resp = %.0f + %.1f + %.1f + %.1f us = %.1f us (CONDITIONAL on S2's sense delay and tPD(MR)); W140's and W145's chain (RESET1" % (
        F["tcts"][1] * 1e6, tpd_mr * 1e6, t_fall * 1e6, F["vnf"] * 1e6, t_resp * 1e6))
    w("           through 750 Ohm onto NRST, withdrawn: it latches with a hold stage, W145-F1) read %.1f us of NRST fall and %.1f us" % (
        t_fall_w145 * 1e6, t_resp_w145 * 1e6))
    # W145's CTR1 hold, withdrawn by W148-1 (the history of S5): Equation 2 on a 100 nF capacitor at -20 %, and TI's full-discharge condition
    c_w145 = 100e-9
    tctr_min = -math.log(F["eq"]["min"]) * F["rctr"][0] * c_w145 * (1 - C_RST_TOL)
    tctr_max = -math.log(F["eq"]["max"]) * F["rctr"][2] * c_w145 * (1 + C_RST_TOL) + F["tctr"]
    t_full = F["full_frac"] * tctr_max
    w("       the reset hold (SESSION W148-1, replacing W145-1's CTR1 capacitor): %s with CT pulled to its VDD through %s (TI 7.3" % (dm.HOLD_PART, dm.CT_PULLUP))
    w("         note 1: a pull-up 'is required, 10 kOhm is recommended'; 9.1.2.1: the factory-programmed timing), option %s's delay tD %.0f / %.0f /" % (
        dm.HOLD_PART[7], hold[0] * 1e3, hold[1] * 1e3))
    w("         %.0f ms (7.6, p.%d, PRINTED), after '%s ... %s' (8.3.5, p.16; Figure 8-2's note B: '%s'; note C: '%s')." % (
        hold[2] * 1e3, F["t3_td_page"], F["t3_q"]["mr2"], F["t3_q"]["mr3"], F["t3_q"]["noteB"], F["t3_q"]["noteC"]))
    w("         TI prints no condition on the fault's length beyond tMR_W: the hold is a timer, not a capacitor's discharge (9.1.2.1 against")
    w("         9.1.2.2's capacitor option, which this draft does not use). Its SENSE sits on its own VDD, so '%s' (8.3.4, p.15) happens at" % F["t3_q"]["reeval"])
    w("         the part's own start and SENSE never leaves the window after; a CT option misread there would show as a short hold, which")
    w("         W148-3's timing reads at the start's own test (5e). In a loop the MR pulse lasts at least NRST's fastest fall, %.1f us" % (t_fall_min * 1e6))
    w("         (MODEL: %.0f nF, %.1f Ohm, the pull-ups at their weakest, an ideal drain; tCTS's minimum is not printed, taken 0): the controller" % (
        c_lo * 1e9, r_lo))
    w("         holds VCAP up until it is reset, and only the hold stage's RESET resets it, so the pulse is %.0fx tMR_W" % (t_fall_min / (F["t3_tmrw"][0] * 1e-6)))
    w("         W145's CTR1 hold, WITHDRAWN (the history of S5): Equation 2's %.1f ms held only after a fault longer than %.2f ms ('%s')," % (
        tctr_min * 1e3, t_full * 1e3, F["full_q"]))
    w("           which a loop's fault was not shown to last; the TPS37's CTR1 is open again (tCTR(no cap) at most %.0f us)" % (F["tctr"] * 1e6))
    w("       power-up: the TPS3703 holds NRST low from its VPOR, at most %.1f V, through its UVLO, %.1f to %.1f V: '%s' (8.4.2, p.17);" % (
        F["t3_vpor"], F["t3_uvlo"][0], F["t3_uvlo"][1], F["t3_q"]["uvlo"]))
    w("         the TPS37 holds MONRST, so MR, low from its VPOR %.1f V: '%s' (8.3.1.1, p.18), to its %.1f V minimum, and then '%s'" % (
        F["vpor"], F["uvlo_q"], F["vdd_min"], F["tsd_note"]))
    w("         (7.6 note 4, p.9), tSD %.0f ms (p.9); the H743 leaves its own BOR0 reset from %.2f to %.2f V rising (Table 116, p.212). The" % (
        F["tsd"] * 1e3, F["bor0"][0], F["bor0"][2]))
    w("         hold adds at least %.0f ms after MR rises, longer than the TPS37's %.0f ms tSD, so the monitor is valid before the controller's" % (
        hold[0] * 1e3, F["tsd"] * 1e3))
    w("         first instruction: NRST is released %.1f to %.2f ms after VDD reaches %.1f V (tD's minimum; tSD + tCTR(no cap) + tD's maximum," % (
        hold[0] * 1e3, (F["tsd"] + F["tctr"] + hold[2]) * 1e3, F["vdd_min"]))
    w("         Figure 7-3 p.12 DIAGRAM for the TPS37's release; supplier task S4 confirms it)")
    w("       the rails: the TPS37 runs from %.1f V (7.3, p.6) and the TPS3703 from %.1f V (7.3) on a rail of %.4f to %.4f V; the TPS37's IDD" % (
        F["vdd_min"], F["t3_vdd"][0], rail[0], rail[1]))
    w("         at most %.1f uA (p.7); the divider loads VCAP with at most %.1f uA: ST prints no figure for a load on VCAP (ASSUMPTION, S3); no case" % (
        F["idd"] * 1e6, vc["VOS0"][2] / ((ohms(dm.TOP) + ohms(dm.BOTTOM)) * (1 - 0.001 - 25e-6 * TEMPCO_K)) * 1e6))
    w("         row changes")
    # 5e own faults
    t449 = page(RM, 449, 450)
    q_pin = quote(t449, "Bit 22 PINRSTF: Pin reset flag (NRST) (1)", "RM0433 p.450 PINRSTF")
    q_pin2 = quote(t449, "Set by hardware when a reset from pin occurs.", "RM0433 p.450 PINRSTF set")
    need(t449, r"8\.7\.39\s+RCC reset status register \(RCC_RSR\)", "RM0433 8.7.39 RCC_RSR")
    # RM0433 Table 56 (p.332): the flags a pin reset sets, and the other rows that set PINRSTF too (W144's F3)
    t56 = t329[t329.index("Table 56. Reset source identification (RCC_RSR)"):]
    need(t56, r"332/3353", "RM0433 p.332 in the pinned text")
    hdr = ["LPWRRSTF", "WWDG1RSTF", "IWDG1RSTF", "SFTRSTF", "PORRSTF", "PINRSTF", "BORRSTF", "D2RSTF", "D1RSTF", "CPURSTF"]
    rows56 = {}
    for m in re.finditer(r"^\s*(\d+)\s+(.+?)\s{2,}((?:[01]\s+){9}[01])\s*$", t56, re.M):
        rows56[int(m.group(1))] = (squash(m.group(2)), [int(x) for x in m.group(3).split()])
    rows56.pop(12, None)      # row 12's label sits on the lines around its number: read below on its own
    if sorted(rows56) != [1, 2, 3, 4, 5, 6, 8, 10, 11] or rows56[2][0] != "Pin reset (NRST)":
        refuse("RM0433 Table 56's rows are not the ones this record read: %r" % sorted(rows56))
    m = need(t56, r"^\s+(D1 erroneously enters DStandby mode or)\s*\n\s*12\s+((?:[01]\s+){9}[01])\s*\n\s+(CPU erroneously enters CStop mode)",
             "RM0433 Table 56 row 12")
    rows56[12] = (m.group(1) + " " + m.group(3), [int(x) for x in m.group(2).split()])
    pat2 = dict(zip(hdr, rows56[2][1]))
    pin_too = [rows56[k][0] for k in sorted(rows56) if k != 2 and dict(zip(hdr, rows56[k][1]))["PINRSTF"] == 1]
    q_rmvf = quote(t329, "The CPU can reset the flags by setting RMVF bit.", "RM0433 8.4.4 p.332")
    t_win = t_resp
    w("   5e. ITS OWN FAULTS AND THEIR SELF-TEST (SESSION W140-3 as restated by W145-2, W145-3 and W148-3; the firmware row is FW-B23,")
    w("       drafted in apply_hw_fw_contract_hoe.py for L4A-61; nothing applied): at every start and then once every %.0f s, at HCLK" % T_TEST_S)
    w("       at most 144 MHz, the controller clears the reset flags (\"%s\", RM0433 8.4.4, p.332), keeps a marker and the RTC's" % q_rmvf)
    w("       time where NRST does not reach (Table 55, p.330: \"%s\"), writes VOS = Scale 1 and waits at most %.1f us from that" % (q_t55b, t_win * 1e6))
    w("       write (t_resp: the window timed from the write covers the regulator's ramp, the monitor, the hold stage and NRST's fall on every")
    w("       unit in service, W144's F11); still running, it writes Scale 3 within %.0f us (W145-2) and reports MONITOR FAILED in its" % T_RESTORE_US)
    w("       state frame. After the reset, PASSED needs the marker and RCC_RSR equal to Table 56's row 2, 'Pin reset (NRST)' (RM0433 8.4.4,")
    w("       p.332): %s set, %s clear (W145-3)," % (" and ".join(k for k in hdr if pat2[k]), ", ".join(k for k in hdr if not pat2[k])))
    w("       and (W148-3) the RTC's time from the write to the restart at least %.0f ms: half the hold's printed %.0f ms minimum, %.1f times" % (
        T_HOLD_CHECK_S * 1e3, hold[0] * 1e3, T_HOLD_CHECK_S / F["t3_td"][(dm.HOLD_PART[7], "open")][2]))
    w("       the %.1f ms maximum TI prints with CT open (7.6), so a lost CT pull-up reads HOLD FAILED on an RTC clock within +-%.0f %%;" % (
        F["t3_td"][(dm.HOLD_PART[7], "open")][2] * 1e3, RTC_TOL * 100))
    w("       the restart after a reset adds NRST's rise and the boot, which no held page prints: the check sees a CT-open hold while they")
    w("       stay under %.1f ms (ASSUMPTION; V-B24 reads them on the first article)" % ((T_HOLD_CHECK_S / (1 + RTC_TOL) - F["t3_td"][(dm.HOLD_PART[7], "open")][2]
                                                                                  - t_resp) * 1e3))
    w("       PINRSTF alone is not enough: \"%s\", \"%s\" (8.7.39, p.450), and Table 56 sets it in the rows %s too" % (q_pin, q_pin2, "; ".join(pin_too)))
    w("       (W144's F3). Scale 1 (VCAP %.2f V and up) is over the trip's top by %.1f %%: the test drives the whole real path, VCAP to divider to" % (vc["VOS1"][0], od1 * 100))
    w("       SENSE1 to RESET1 to MR to RESET to NRST. One supervisor tests at a time and only while the other two serve (IOHA row 3); the peers")
    w("       flag a supervisor whose test counter has not moved for 2 x %.0f s (FW-B22's state frame). A healthy unit whose ramp makes the" % T_TEST_S)
    w("       interval from the write longer than t_resp reads MONITOR FAILED: found at the first article by S2, and then the window and S1's")
    w("       limit are re-read together (W145-2's reversal)")
    faults = [("divider top open or bottom shorted", "SENSE1 at 0 V: never trips", "the next test (no reset)"),
              ("divider bottom open or top shorted", "SENSE1 at VCAP (1.0 V and up) over 0.808 V: held in reset", "at once (the controller silent, IOHA row 3)"),
              ("a divider value drifted", "the band moves", "the test if the trip passes VOS1's bottom; else at once (held in reset)"),
              ("RESET1 stuck released, or MONRST open at MR", "never resets", "the next test"),
              ("RESET1 stuck low, or MONRST shorted to ground", "held in reset", "at once"),
              ("the TPS37 unpowered (VDD open)", "output undefined under VPOR", "the next test, or at once if it rests low"),
              ("SENSE1 and SENSE2 exchanged or shorted (assembly)", "SENSE1 at the rail: held in reset", "at once"),
              ("a slowed monitor or hold stage (sense, MR, NRST fall)", "the ending takes longer than t_resp", "the next test (its window is t_resp, F11)"),
              ("the hold stage's RESET stuck released, or R812 open", "never resets", "the next test"),
              ("the hold stage's RESET stuck low, or MONOUT at ground", "held in reset", "at once"),
              ("the hold stage unpowered (VDD open)", "RESET undefined under its VPOR", "the next test, or at once if it rests low"),
              ("the CT pull-up R813 open (CT floating)", "the hold falls to CT open's 0.7 to 1.3 ms", "the next test's hold timing (W148-3)"),
              ("CT shorted to ground", "TI's latch mode (9.1.3): held after a trip", "at once (the start's own test latches it)"),
              ("a firmware that skips the test", "a latent monitor fault stays latent", "the peers, within 2 x %.0f s" % T_TEST_S)]
    for f_, eff, det in faults:
        w("         %-54s %-58s found: %s" % (f_, eff, det))
    w("       the residuals: a monitor or hold fault latent since the last test, then a firmware VOS0 entry or an image that enters VOS1 or")
    w("       VOS0 at every boot: a double fault, its window at most %.0f s (S-i, S-l)" % T_TEST_S)
    # 5f the thermal time, at one supply corner (W145-4, W144's F8)
    tb3, ib3 = bpoint(T, PT10, QT10, 3.3, air)
    tbc, ibc = bpoint(T, PT10, QT10, CORNER, air)
    air105_c = air_at(T, PT10, QT10, CORNER, 105.0)
    air105_3 = air_at(T, PT10, QT10, 3.3, 105.0)
    m = need(t10, r"V\s+L4-E12 E5 exhaust 81\.89 C ([\d.]+) A \(([\d.]+) C\)", "T10 10c's exhaust row on revision V")
    tj_ex = float(m.group(2))
    air105_lin = air + (105.0 - tj_b) / (tj_ex - tj_b) * (PT10["air_exhaust"] - air)
    i_v1 = {"Table 119": F["vos1_en"][4], "Table 120": F["t120_vos1_en"][4], "Table 121": F["t121"][("1", "en")][4]}
    t_v1 = max(i_v1, key=lambda k: i_v1[k])
    p_ex = CORNER * (F["vos0_en"][3] - ibc)
    dT = 105.0 - tbc
    z_need = dT / p_ex
    p_ex1 = CORNER * (i_v1[t_v1] - ibc)
    z_need1 = (125.0 - tbc) / p_ex1
    z_w140 = (125.0 - tj_b) / (rail[1] * (F["vos1_en"][4] - i_b))          # W140's figure: Table 119 at mixed corners
    z_f7 = (125.0 - tj_b) / (rail[1] * (i_v1["Table 120"] - i_b))          # W144's F7: Table 120 at W140's corners
    z_w140c = (105.0 - tj_b) / (rail[1] * (F["vos0_en"][3] - i_b))         # W140's S-c figure, mixed corners
    t_dead = t_win + T_RESTORE_US * 1e-6
    vol_si = p_ex * t_resp / (RHO_C_SI * dT) * 1e3                                    # mm3
    v0_105 = {"Table 119": F["vos0_en"][3], "Table 120": F["t120_vos0_en"][3], "Table 121": F["t121"][("0", "en")][3]}
    w("   5f. THE CONTROLLER'S THERMAL TIME: DS12110 Rev 11 prints steady resistances only (Table 222: ThetaJA, ThetaJB, ThetaJC; no transient")
    w("       impedance, no heat capacity, in the pages read); NOT PRINTED. What the ending needs instead (MODEL on PRINTED), every figure at")
    w("       ONE supply corner, the rail's top %.4f V (SESSION W145-4, W144's F8; T10's own model, l9t5_t10.py's mcu_i, solved at that" % CORNER)
    w("       voltage, its run-table currents kept at their printed figures):")
    w("         the bounded state (revision V): %.2f C at %.4f A at 3.3 V (T10 10c prints %.1f C, %.4f A); at %.4f V %.2f C at %.4f A" % (
        tb3, ib3, tj_b, i_b, CORNER, tbc, ibc))
    w("         VOS0 at 105 C, all peripherals enabled, the largest printed: %s (%s); %.3f A adds %.4f W" % (
        ", ".join("%s %.0f mA" % (k, v * 1e3) for k, v in v0_105.items()), max(v0_105, key=lambda k: v0_105[k]), F["vos0_en"][3], p_ex))
    w("         to stay inside 105 C (%.2f K) the junction-to-ambient transient impedance at t_resp must be at most %.2f K/W (W140's %.2f K/W" % (
        dT, z_need, z_w140c))
    w("         mixed the 3.3 V state with the rail-top step; W144 read about 3.63 K/W)")
    w("         VOS1 at 125 C, all peripherals enabled, the largest printed (W144's F7): %s: %s, %.3f A (ASSUMPTION: a bound for any VOS1" % (
        ", ".join("%s %.0f mA" % (k, v * 1e3) for k, v in i_v1.items()), t_v1, i_v1[t_v1]))
    w("         clock and peripheral set, monotonic) adds %.4f W; inside VOS1's 125 C (%.2f K): at most %.2f K/W at t_resp for a VOS1 entry and at" % (
        p_ex1, 125.0 - tbc, z_need1))
    w("         %.1f us for the self-test with a dead monitor (5e: t_resp plus the Scale 3 write); W140 read %.2f K/W (Table 119, mixed corners)," % (
        t_dead * 1e6, z_w140))
    w("         W144's F7 %.2f K/W (Table 120 at W140's corners)" % z_f7)
    w("         U-02's local air (W144's F2): the bounded state itself reaches 105 C at %.2f C local air at %.4f V (%.2f C at 3.3 V; W144's" % (
        air105_c, CORNER, air105_3))
    w("         linear reading of T10's two air rows %.1f C); at or over that air no ending of any speed keeps a VOS0 entry inside 105 C:" % air105_lin)
    w("         condition C2 (the pockets' air is U-02's, the T-H1 mock-up)")
    w("         for scale only (ASSUMPTION, a handbook figure, credited nothing): %.2f J/(cm3 K) of silicon makes %.2f K in %.1f us at %.4f W need" % (
        RHO_C_SI, dT, t_resp * 1e6, p_ex))
    w("         %.4f mm3 of silicon heated adiabatically; ST prints no die size" % vol_si)
    # 5g the reset loop (W144's F1), on the hold stage (W148-1)
    duty = t_resp / hold[0]
    rise = duty * p_ex * F["ja"]["LQFP100"]
    z_loop = (dT - rise) / p_ex
    duty_w145 = t_resp_w145 / (t_resp_w145 + tctr_min)
    rise_w145 = duty_w145 * CORNER * (F["vos0_en"][3] - ibc) * F["ja"]["LQFP100"]
    w("   5g. THE RESET LOOP (W144's F1): an image that enters VOS1 or VOS0 at every boot. Each cycle it is in VOS1 or VOS0 for at most t_resp")
    w("       (S2) at the %.4f W step, then in reset; the reset and the boot are taken at no more than the bounded state's power (ASSUMPTION: the" % p_ex)
    w("       reset state, VOS3 with the reset clocks and every peripheral at reset, RM0433 p.279, inside FW-B20's bound)")
    w("         the hold stage (SESSION W148-1): every cycle's MR pulse lasts at least %.1f us, over tMR_W's %.0f us minimum (5d), so RESET" % (
        t_fall_min * 1e6, F["t3_tmrw"][0]))
    w("         asserts and is held for tD after MR returns high, at least %.0f ms (7.6, PRINTED), for ANY length of the fault: TI's note B" % (hold[0] * 1e3))
    w("         starts the counter when MR is high; read by note C instead (the counter from RESET's assertion), the controller is still out of")
    w("         VOS1 and VOS0 for at least tD less t_resp. Either way the duty is at most t_resp / tD(min) = %.1f / %.0f us = %.3f %%; the" % (
        t_resp * 1e6, hold[0] * 1e6, duty * 100))
    w("         average rise at most %.3f %% x %.4f W x %.1f C/W = %.3f K (MODEL); S1's limit at t_resp becomes (%.2f - %.3f) / %.4f = %.2f K/W" % (
        duty * 100, p_ex, F["ja"]["LQFP100"], rise, dT, rise, p_ex, z_loop))
    w("         (the average plus one pulse's own rise, a superposition MODEL). No fault-length condition: S5 is RETIRED (section 9)")
    w("         W145's CTR1 hold, withdrawn (5d): duty %.3f %% and %.3f K at its t_resp %.1f us, CONDITIONAL on TI's full discharge (S5)" % (
        duty_w145 * 100, rise_w145, t_resp_w145 * 1e6))
    # 5h the hold, compared (W148): at most three materially different approaches, each on its printed minimum
    tps5 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "5", "-l", "5"], PDFTEXT, REC)
    i38 = float(need(tps5, r"I RESET\s+RESET pin current\s+[\d.]+\s+(\d+)\s+mA", "TPS3808 6.3 I RESET").group(1)) * 1e-3
    rs38 = 750.0
    t_fall_a = slowest(rs38, F["t38_vol"][0], F["t38_vol"][1])
    t_resp_a = F["tcts"][1] + float(F["t38_tpd_mr"][0]) * 1e-9 + t_fall_a + F["vnf"]
    duty_a = t_resp_a / F["t38_td"][0]
    rise_a = duty_a * p_ex * F["ja"]["LQFP100"]
    z_a = (dT - rise_a) / p_ex
    ipk_a = rail[1] / (rs38 * 0.99)

    def window_fit(nom, tolp):
        """the VCAP range (g_lo, g_hi) of VSENSE / VCAP over which a TPS3703 window of nominal nom and tolerance tolp keeps VOS3's
        printed band inside its window (both releases outside it) and trips under VOS1's bottom, on 7.5's accuracy and hysteresis; None
        when no g up to 1 does (a divider cannot raise SENSE over VCAP); the divider's own tolerance is not charged (in the parts' favour)"""
        acc = F["t3_acc"] if nom >= 0.8 else F["t3_acc_lo"]
        hy = F["t3_hys"] if nom >= 0.8 else F["t3_hys_lo"]
        ov, uv = nom * (1 + tolp / 100.0), nom * (1 - tolp / 100.0)
        g_hi = min(1.0, ov * (1 - acc) * (1 - hy) / vc["VOS3"][2])
        g_lo = max(ov * (1 + acc) / vc["VOS1"][0], uv * (1 + acc) * (1 + hy) / vc["VOS3"][0])
        return (g_lo, g_hi) if g_lo < g_hi else None
    win_orderable = [(code, window_fit(nom, tl)) for code, letter, tl, nom in F["t3_orderable"] if letter in "ABCD"]
    fits_stock = [c for c, f in win_orderable if f]
    fits_cat = [(nom, tl, window_fit(nom, tl)) for nom in F["t3_noms"] for tl in (3, 4, 5, 6, 7) if window_fit(nom, tl)]
    best_cat = max(fits_cat, key=lambda x: (x[2][1] - x[2][0]) / x[2][1]) if fits_cat else None
    m1 = [x for x in fits_cat if abs(x[0] - 1.00) < 1e-9 and x[1] == 7]
    acc1, hy1 = F["t3_acc"], F["t3_hys"]
    marg_ov = 1.00 * 1.07 * (1 - acc1) * (1 - hy1) - vc["VOS3"][2]
    marg_uv = vc["VOS3"][0] - 1.00 * 0.93 * (1 + acc1) * (1 + hy1)
    od_hs2 = (vc["VOS1"][0] - 1.07 * (1 + acc1)) / 1.00
    area = {"TPS37": 2.5 * 2.5, "TPS3703": F["t3_pkg"][0] * F["t3_pkg"][1], "TPS3808": F["t38_pkg"][0] * F["t38_pkg"][1]}
    need(text(DOCS["draft"]), r"TPS37 in WSON-10 \(DSK\)", "the draft's TPS37 package")
    w("   5h. THE HOLD, COMPARED (W148, on W145's finding W145-F1): what bounds the reset loop's duty for ANY fault length on printed figures")
    w("       HS-1 a hold stage after the TPS37 (its RESET1 on the stage's manual reset alone; the stage's RESET onto NRST), two parts read:")
    w("         HS-1a TI TPS3808G30 (board B's U221 and U543, SBVS050N): td %.0f / %.0f / %.0f ms with CT to VDD (6.6, p.7, PRINTED); '%s'" % (
        tuple(x * 1e3 for x in F["t38_td"]) + (F["t38_q"]["mr"],)))
    w("           (7.3.3, p.11); '%s' (7.3.4, p.12): no fault-length condition. The MR pulse that registers: %s us in the %s column" % (
        F["t38_q"]["delay"], F["t38_tw_mr"][0], F["t38_tw_mr"][1]))
    w("           only (6.6), MR to RESET %s ns %s; its drive prints only %.1f V at %.0f mA (6.5, p.6; board B's D4E-F2 buffers U221 for the same" % (
        F["t38_tpd_mr"][0], F["t38_tpd_mr"][1], F["t38_vol"][0], F["t38_vol"][1] * 1e3))
    w("           reason): through 750 Ohm (peak %.2f mA, its 6.3 maximum %.0f mA, p.5) NRST's fall is bounded at %.1f us, t_resp %.1f us; duty" % (
        ipk_a * 1e3, i38 * 1e3, t_fall_a * 1e6, t_resp_a * 1e6))
    w("           %.3f %%, rise %.3f K, S1's limit %.2f K/W at %.1f us; IC body %.2f x %.2f mm (p.1)" % (
        duty_a * 100, rise_a, z_a, t_resp_a * 1e6, F["t38_pkg"][0], F["t38_pkg"][1]))
    w("         HS-1b TI %s (SBVS249B, held back): tD %.0f / %.0f / %.0f ms with CT to VDD through 10 k (7.6, p.7, PRINTED; option F," % (
        (dm.HOLD_PART,) + tuple(x * 1e3 for x in hold)))
    w("           UV only, SENSE on its own VDD: '%s', pin functions p.4); the MR pulse that registers: tMR_W %.0f us, %s column" % (
        F["t3_q"]["sense"], F["t3_tmrw"][0], F["t3_tmrw"][1]))
    w("           (PRINTED); its drive %.0f mV at %.0f mA (VDD 2 V row): t_resp %.1f us (5d); duty %.3f %%, rise %.3f K, S1's limit %.2f K/W" % (
        vol3 * 1e3, i3 * 1e3, t_resp * 1e6, duty * 100, rise, z_loop))
    w("           at %.1f us; IC body %.2f x %.2f mm (p.1); stock: Active in TI's package option addendum" % (t_resp * 1e6, F["t3_pkg"][0], F["t3_pkg"][1]))
    w("         own faults (both): the stage's RESET stuck released or the series resistor open (no reset: the next test), stuck low (held:")
    w("           at once), unpowered (the next test or at once), its timing lost (HS-1a: CT open gives 12 to 28 ms, 6.6; HS-1b: CT open gives")
    w("           %.1f to %.1f ms, found by W148-3's hold timing), CT at ground (HS-1b: TI's latch mode, held at the start's test: at once)" % (
        F["t3_td"][(dm.HOLD_PART[7], "open")][0] * 1e3, F["t3_td"][(dm.HOLD_PART[7], "open")][2] * 1e3))
    w("         parts per supervisor: U810, the hold stage, R810, R811, R812, R813, C810, C816 (8; W145's draft 6); the ICs' bodies %.2f mm2" % (
        area["TPS37"] + area["TPS3703"]))
    w("           (HS-1b) or %.2f mm2 (HS-1a) per supervisor against W145's %.2f mm2; board B carries three (Layer 10 lays them out)" % (
        area["TPS37"] + area["TPS3808"], area["TPS37"]))
    w("       HS-2 one supervisor on VCAP with a printed timeout, no TPS37: TI's TPS3703 window (OV and UV) with its factory-programmed tD")
    w("         (A: %.0f / %.0f / %.0f ms with CT to VDD) and tPD at most %.0f us at 5 %% overdrive (7.6, PRINTED). Its window must hold VOS3's" % (
        tuple(x * 1e3 for x in F["t3_td"][("A", "vdd")]) + (F["t3_tpd"][1] * 1e6,)))
    w("         printed %.2f to %.2f V with both releases outside it and trip under VOS1's %.2f V (accuracy +-%.1f %%, hysteresis up to %.1f %%," % (
        vc["VOS3"][0], vc["VOS3"][2], vc["VOS1"][0], acc1 * 100, hy1 * 100))
    w("         7.5; a divider can only lower SENSE): of the %d orderable window codes in the addendum (%s) %s fits;" % (
        len(win_orderable), ", ".join(c for c, _f in win_orderable), "none" if not fits_stock else ", ".join(fits_stock)))
    w("         of Table 12-1's catalogue (%d nominal codes x tolerances 3 to 7 %%) %d fit, none orderable ('%s', p.3), the widest a relative" % (
        len(F["t3_noms"]), len(fits_cat), F["t3_q"]["moq"]))
    w("         range of %.2f %% for the divider (%.2f V at %d %%); 1.00 V at 7 %% direct: OV release %.1f mV over VOS3's top, UV release %.1f mV" % (
        (best_cat[2][1] - best_cat[2][0]) / best_cat[2][1] * 100, best_cat[0], best_cat[1], marg_ov * 1e3, marg_uv * 1e3))
    w("         under its bottom, VOS1 %.1f %% over the trip; its UV side resets the controller on any VCAP under the window (a constraint on" % (od_hs2 * 100))
    w("         a reduced-voltage low-power mode); one part, %d to %d per supervisor with its CT pull-up, bypass, series resistor and a divider" % (4, 6))
    w("       HS-3 no retry: TI's latch mode ('%s', '%s', 9.1.3, p.20): the first trip holds" % (F["t3_q"]["latch"], F["t3_q"]["unlatch"]))
    w("         the controller until CT is driven from outside; FW-B23's self-test trips the monitor at every start, so every supervisor would")
    w("         latch at its first start unless a peer or a power cycle releases it, an action from outside its failure domain (CON-004)")
    w("       READING: HS-1a and HS-1b both bound the loop for any fault length on a printed minimum (180 and 14 ms); HS-1a's registration is")
    w("         TYPICAL and its drive slows NRST to %.1f us; HS-1b's registration is a printed minimum, its drive keeps t_resp at %.1f us, and" % (
        t_resp_a * 1e6, t_resp * 1e6))
    w("         its shorter hold costs %.3f K of loop rise; HS-2 needs a non-stock window with margins of a few millivolts; HS-3 breaks the" % rise)
    w("         self-test or the failure domains. SELECTED (SESSION W148-1, section 7): HS-1b, %s as the hold stage" % dm.HOLD_PART)
    w("   VERDICT H-2: NOT SUPPORTED ON PRINTED FIGURES AS A PROOF: the register's end condition ('no printed timing bounds the entry-to-reset")
    w("   interval, or the thermal time cannot be bounded on printed figures') is met, since neither the sense delay at VOS0's overdrive (S2)")
    w("   nor the controller's transient impedance (S1) is printed. The reset loop's hold no longer rests on an unprinted condition: the")
    w("   hold stage's printed minimum bounds its duty for any fault length (5g). It STANDS as the one drafted design that ends every VOS1")
    w("   and VOS0 entry whatever the firmware does, on printed thresholds: PROVISIONAL under amendment 1, S1 and S2 supplier tasks with")
    w("   pass limits, not a closure. Not claimed: a hardware bar, a printed interval.")
    w("")
    # ---------------------------------------------------------------- 6. acceptance
    w("6. THE ACCEPTANCE, STATE BY STATE ('the controller inside 105 C in every served state and every state the protection admits'; 105 C is")
    w("   VOS0's limit, 125 C VOS1 to VOS3's, Table 113; every figure MODEL on PRINTED unless marked, at one supply corner %.4f V, W145-4)" % CORNER)
    tj_v3 = float(need(t10, r"V\s+VOS3 200 MHz, peripherals enabled\s+TJ ([\d.]+) C at ([\d.]+) A", "T10 section 4, VOS3 200 MHz enabled on rev V").group(1))
    pv3 = T.point(PT10["V"][("on", 200)], air, PT10["theta_mcu"], 125.0, vdd=CORNER)
    tj_v3c = pv3[0] if pv3 else None
    S = [("S-a", "the bounded served state (FW-B20, FW-B21, rev V)", "105 C", "%.2f C (T10 10c's %.1f C at 3.3 V)" % (tbc, tj_b), "HOLDS" if tbc <= 105.0 else "FAILS"),
         ("S-b", "VOS3 at its printed maximum (200 MHz, all peripherals)", "125 C",
          "%.2f C (T10 section 4's %.1f C at 3.3 V)" % (tj_v3c, tj_v3) if tj_v3c else "no operating point", "HOLDS" if tj_v3c and tj_v3c <= 125.0 else "FAILS"),
         ("S-c", "a VOS0 entry by any firmware", "105 C", "ended within t_resp %.1f us; needs ZthJA(t_resp) <= %.2f K/W" % (t_resp * 1e6, z_need),
          "CONDITIONAL (S1, S2; C2, C3)"),
         ("S-d", "a VOS1 entry by any firmware, the self-test included", "125 C", "ended within t_resp; needs ZthJA(t_resp) <= %.2f K/W" % z_need1,
          "CONDITIONAL (S1, S2)"),
         ("S-e", "the self-test with a dead monitor", "125 C", "at most %.1f us (firmware); needs ZthJA(%.1f us) <= %.2f K/W" % (t_dead * 1e6, t_dead * 1e6, z_need1),
          "CONDITIONAL (S1)"),
         ("S-f", "VOS2 with VCAP under the trip's top (%.2f to %.4f V)" % (vc["VOS2"][0], hi), "125 C", "not surely ended by the monitor",
          "OPEN (row R-1, HO-E-REGISTER-ROWS.md)"),
         ("S-g", "VOS3 above its printed 200 MHz", "125 C", "no printed current", "OPEN (row R-2, HO-E-REGISTER-ROWS.md)"),
         ("S-h", "power-up before the monitor is valid", "105 C", "NRST held under both UVLOs, then tD (>= %.0f ms) after MR rises (5d)" % (hold[0] * 1e3),
          "CONDITIONAL (S4)"),
         ("S-i", "a latent monitor fault, then a firmware VOS0 entry", "105 C", "a double fault; window at most %.0f s" % T_TEST_S, "RESIDUAL (single-fault)"),
         ("S-k", "the reset loop: an image entering VOS1 or VOS0 at every boot", "105 C",
          "duty <= %.3f %%, rise <= %.3f K, any fault length; ZthJA(t_resp) <= %.2f K/W" % (duty * 100, rise, z_loop), "CONDITIONAL (S1, S2)"),
         ("S-l", "a latent hold fault (CT's pull-up lost), then the reset loop", "105 C", "a double fault; W148-3's hold timing, window at most %.0f s" % T_TEST_S,
          "RESIDUAL (single-fault)"),
         ("S-j", "any current up to the limiter's %.4f A" % ios[1], "as above", "a VOS3 state is S-a, S-b or S-g; a VOS1 or VOS0 state S-c, S-d or S-k",
          "no state outside S-a to S-l")]
    for row in S:
        w("   %-4s %-60s %-9s %-80s %s" % row)
    w("   THE CONDITIONS OF THE FOCUSED CHECK (W144, L4A-100), RESTATED:")
    w("     C1 (F1): the reset hold drafted, composed, read and mutated, with the reset-loop row: W145's CTR1 hold (CONDITIONAL on S5) replaced")
    w("        by the hold stage (SESSION W148-1: 5d, 5g, 5h, section 8), whose printed minimum bounds the loop for any fault length: S5 retired")
    w("     C2 (F2): U-02's local air at the supervisors at or under %.2f C (MODEL at %.4f V; W144's linear %.1f C)" % (air105_c, CORNER, air105_lin))
    w("     C3 (F4): revision V fitted (L9T5-D7): the trip window rests on Table 112's rows on DS12110's '(rev V)' pages (p.209); rev Y's Table 14")
    w("        (p.105) prints no core voltage per scale, and no held page prints rev X's; a rev X part also needs its VCAP per scale (S3)")
    w("     C4 (F8, F11): S1 at one supply corner (at most %.2f K/W at t_resp, %.2f K/W less the loop's rise); S2 on the real VCAP ramp, the" % (z_need, z_loop))
    w("        self-test's window timed from the Scale 1 write, now through the hold stage; S3 and S4 as written; S5 retired (W148-1)")
    w("     C5 (F3, F6): the register rows, HO-E-REGISTER-ROWS.md (R-1 S-f, R-2 S-g, R-3 the self-test's firmware row FW-B23, drafted in")
    w("        apply_hw_fw_contract_hoe.py)")
    w("   HO-E's ACCEPTANCE: CONDITIONAL. The served state holds 105 C; every VOS0 state the protection admits is ended by the drafted monitor,")
    w("   and whether the junction stays inside 105 C during the ending rests on S1 and S2 (in a reset loop too) and on C2 and C3.")
    w("   Nothing is upgraded: cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand; this task closes no cx46 item before")
    w("   its own check's targeted recheck (L4A-100).")
    w("")
    # ---------------------------------------------------------------- 7. the selection
    w("7. THE SELECTION")
    w("   SESSION W140-1: H-2 with the drafted VCORE monitor (apply_gen_sch_b_vcoremon.py) and the firmware rows of 5e, PROVISIONAL on S1 to S4")
    w("     (S5 retired by W148-1).")
    w("     authority: SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026")
    w("     authority_why: an engineering selection inside the drafted circuit; no requirement, protected class, case row, purchase or")
    w("       publication changes; one approach stands after the reading (H-1 drops out on the documents, H-3 is not established on printed")
    w("       figures), so the ruling's second half (more than one option standing) fails; the residuals are measurable on a specimen (S1 to")
    w("       S5), so the selection accepts no risk a measurement cannot remove: amendment 1's supplier tasks, not an owner's risk acceptance")
    w("     ruled_by: W140 (Claude), MESHSAT-1357; ruled_on: 7 October 2026; reversed_by: none")
    w("     to reverse: drop apply_gen_sch_b_vcoremon.py; HO-E returns to REMAINING ENGINEERING with the owner item below")
    w("     end condition: S1 reads the controller's ZthJA at t_resp over %.2f K/W on board B (%.2f K/W less the loop's rise); or S2 reads" % (z_need, z_loop))
    w("       the sense delay at VOS0's overdrive long enough that S1's reading fails at the longer interval; or two negative independent")
    w("       checks of this selection (W145's 'S5 fails' clause retired with S5 by W148-1)")
    w("   W145's decisions (each authority: SESSION, under the same rules; ruled_by: W145 (Claude), MESHSAT-1357; ruled_on: 7 October 2026;")
    w("   reversed_by: none unless named below; authority_why: an engineering value or method inside the drafted circuit and its rows, no")
    w("   requirement, class, case row, purchase or publication changed, one option standing after the focused check's reading):")
    dec = [("W145-1", "the reset hold: 100n from CTR1/MR to GND per monitor (C813, C814, C815), read at +-%.0f %%; REVERSED by W148-1" % (C_RST_TOL * 100),
            "W144's F1 value: Equation 2's %.1f ms kept the loop's duty at %.3f %% after a full discharge, which a loop was not shown to reach (S5)" % (
                tctr_min * 1e3, duty_w145 * 100), "W148-1's reversal"),
           ("W145-2", "the self-test's window: t_resp from the Scale 1 write, then Scale 3 within %.0f us" % T_RESTORE_US,
            "W144's F11: the ending timed on every unit in service, a slowed monitor found; the dead-monitor dwell bounded at %.1f us" % (t_dead * 1e6),
            "a window read from S2's measured ramp, S1 re-read"),
           ("W145-3", "PASSED: the marker and RCC_RSR equal to Table 56's row 2", "W144's F3: six other rows set PINRSTF too", "none needed"),
           ("W145-4", "every thermal limit at one supply corner, %.4f V" % CORNER, "W144's F8: W140 mixed a 3.3 V state with a rail-top step",
            "a narrower rail band issued as a case row"),
           ("W145-5", "the loop's bound left CONDITIONAL on S5; the fixed-delay stage named, not drafted; REVERSED by W148-1",
            "the brief fixed the CTR1 hold; the stage needs a second part per supervisor, a latch-breaking element and its own check",
            "W148-1 drafted the stage")]
    for d_ in dec:
        w("     %-7s %s" % d_[:2])
        w("             why: %s; to reverse: %s" % d_[2:])
    w("   W148's decisions (each authority: SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September")
    w("   2026; ruled_by: W148 (Claude), MESHSAT-1357; ruled_on: 7 October 2026; reversed_by: none; authority_why: an engineering selection")
    w("   inside the drafted circuit and its rows; the ruling's first half fails: no line a protected class holds, no money spent (nothing is")
    w("   bought; the parts are drafted), no change to what the kit is claimed to be, and no residual risk accepted that a measurement cannot")
    w("   remove; HS-1a also stands after the reading, so the choice between them is an engineering value, taken on 5h's figures):")
    dec148 = [("W148-1", "the reset hold: HS-1b, %s per monitor (U811, U821, U831), CT to its VDD through %s (R813, R823, R833), its RESET" % (
                   dm.HOLD_PART, dm.CT_PULLUP),
               "through %s (R812, R822, R832) onto NRST, the TPS37's RESET1 on its MR alone, CTR1 open, C813 to C815 withdrawn, C816 to C818" % dm.SERIES,
               "5h: its registration (tMR_W %.0f us) and its hold (%.0f ms) are both printed minima; its drive keeps t_resp at %.1f us against" % (
                   F["t3_tmrw"][0], hold[0] * 1e3, t_resp * 1e6),
               "HS-1a's %.1f us and TYPICAL registration; HS-2 is non-stock with millivolt margins; HS-3 breaks the self-test or CON-004" % (t_resp_a * 1e6),
               "HS-1a (TPS3808G30, CT to VDD through 49.9 k, RESET through 750 Ohm) with 5g re-read at its t_resp; end condition: V-B24 reads a",
               "hold under %.0f ms or an MR pulse that does not register, or two negative independent checks of this selection" % (hold[0] * 1e3)),
              ("W148-2", "the series resistor %s from the hold stage's RESET to NRST" % dm.SERIES, "",
               "the E24 value whose peak sink (%.2f mA at the rail's top, the drain at 0 V) stays under the TPS3703's recommended %.0f mA (7.3)" % (
                   i_pk * 1e3, F["t3_irec"] * 1e3),
               "with %.0f %% margin and whose held current stays over its recommended %.1f mA minimum" % ((1 - i_pk / F["t3_irec"]) * 100, F["t3_irec_min"] * 1e3),
               "750 Ohm with 5d's fall re-read", ""),
              ("W148-3", "FW-B23 times the hold: PASSED also needs the RTC's time from the Scale 1 write to the restart at least %.0f ms" % (T_HOLD_CHECK_S * 1e3), "",
               "a lost CT pull-up (the hold at %.1f to %.1f ms) is found by the next test on an RTC clock within +-%.0f %%, so S-l is a double fault" % (
                   F["t3_td"][(dm.HOLD_PART[7], "open")][0] * 1e3, F["t3_td"][(dm.HOLD_PART[7], "open")][2] * 1e3, RTC_TOL * 100),
               "bounded by the test interval, not a latent single fault", "drop the check; S-l back to inspection", ""),
              ("W148-4", "the TPS3703 sheet's fetch line in v2/docs/records/l9t5hoe/fetch_held_back.py, a folder of its own", "",
               "record l9t5's own fetch script is pinned by sha256 in l9t5_a1.py and l9t5_f01.py, whose outputs other records and pages pin;",
               "an entry there would move them all, outside this task", "move the entry into l9t5's script in a set whose dependency pass",
               "re-pins l9t5_a1.out and its dependants")]
    for d_ in dec148:
        w("     %-7s %s" % d_[:2])
        if d_[2]:
            w("             %s" % d_[2])
        w("             why: %s" % d_[3])
        w("               %s" % d_[4])
        w("             to reverse: %s%s" % (d_[5], (" " + d_[6]) if d_[6] else ""))
    w("   the owner item, PREPARED AND NOT RAISED (it would be raised only if the selection's end condition is met): 'The I/O supervisors'")
    w("     STM32H743 cannot hold its 105 C VOS0 limit in the case's air, and no hardware means bars VOS0. Either accept that the 105 C limit")
    w("     during a firmware fault rests on the controller's measured transient thermal response, or change the supervisor part to one whose")
    w("     printed rows hold at this air, or give it a heat sink and a path to the case (a part or mechanical change and its cost).'")
    w("")
    # ---------------------------------------------------------------- 8. the draft
    w("8. THE DRAFT COMPOSED, READ BY PIN, MUTATED AND REFUSED")
    with tempfile.TemporaryDirectory(prefix="l9t5_hoe_") as d:
        seq0, res0, ok0, net0, nl0 = build(d, "hoe0", mon=False)
        seq1, res1, ok1, net1, nl1 = build(d, "hoe1")
        seq2, res2, ok2, net2, nl2 = build(d, "hoe2", extra=(DOCS["canmb"], DOCS["regstage"]))
        seq3, res3, ok3, net3, nl3 = build(d, "hoe3", extra=(DOCS["canmb"], DOCS["regstage"]), mon_first=True)
        if not (ok0 and ok1 and ok2 and ok3 and nl0 and nl1 and nl2 and nl3):
            refuse("board B did not compose or regenerate: %s" % "; ".join("%s %s" % (s, v) for s, v, _m in (res0 + res1 + res2 + res3) if v != "OK"))
        same_order = open(net2, "rb").read() == open(net3, "rb").read()
        theirs = []
        for key in ("canmb", "regstage"):
            sp_ = importlib.util.spec_from_file_location("l9t5_hoe_" + key, os.path.join(ROOT, DOCS[key]))
            m_ = importlib.util.module_from_spec(sp_)
            sp_.loader.exec_module(m_)
            theirs += [x for pair in m_.EDITS for x in pair]
        overlap = [a for a, _b in dm.EDITS if any(a in x for x in theirs)]
        w("   board B in L4-E9's change-list order, this draft straight after iocguard (R-245), the efuse record's R-236 and R-237 after it,")
        w("   Layer 6's three last; the generator run to its end through record l8p's gen_netlist.py:")
        for s, v, _m in res1:
            w("     %-50s %s" % (s, v))
        nets = lambda nl: len({n for p in nl["pins"].values() for n in p.values() if n != "NC"})
        w("   %d drafts: every step OK; %d parts and %d nets with the draft, %d and %d without it (iocguard's state)" % (
            len(seq1), len(nl1["comps"]), nets(nl1), len(nl0["comps"]), nets(nl0)))
        added = sorted(set(nl1["comps"]) - set(nl0["comps"]), key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        removed = sorted(set(nl0["comps"]) - set(nl1["comps"]))
        changed = sorted(r for r in set(nl0["comps"]) & set(nl1["comps"]) if nl0["pins"].get(r) != nl1["pins"].get(r)
                         or nl0["comps"][r].get("value") != nl1["comps"][r].get("value"))
        w("   added %d: %s; removed %d; kept with new nets or values %d%s" % (len(added), ", ".join(added), len(removed), len(changed),
                                                                           (": " + ", ".join(changed)) if changed else ""))
        if sorted(added) != sorted(dm.ADDS):
            refuse("the parts added are not the draft's declared ADDS")
        v1_, w1_ = mon_check(nl1, F, dm)
        v0_, _w0 = mon_check(nl0, F, dm)
        v2_, w2_ = mon_check(nl2, F, dm)
        w("   the monitors read by pin (own rail, SENSE1 on a node fed only by the divider from the controller's own VCAP, SENSE2 on the rail,")
        w("   RESET1 on the hold stage's MR alone, the hold stage's RESET through %s to the controller's own pin 14 and its CT through %s to" % (dm.SERIES, dm.CT_PULLUP))
        w("   the rail (its printed minimum at least the loop row's), the other pins open, the bypasses at both VDDs, every part inside its controller's")
        w("   domain, the band off the netlist's values inside (%.2f, %.2f) V): %s%s; before the draft: %s" % (
            vc["VOS3"][2], vc["VOS1"][0], v1_, (": " + "; ".join(w1_[:3])) if w1_ else "", v0_))
        w("   with W137's canmb and W138's regstage (inputs/, after iocguard), this draft after them and before them: every step OK; the monitors")
        w("     %s%s; the two netlists %s" % (v2_, (": " + "; ".join(w2_[:3])) if w2_ else "", "identical" if same_order else "DIFFERENT"))
        mb_regs = sorted(set(nl2["comps"]) - set(nl1["comps"]))
        clash = sorted(set(dm.ADDS) & set(r for r in mb_regs))
        w("     the two drafts add %d parts of their own, none of them a designator of this draft (%s); an old text of this draft inside" % (
            len(mb_regs), "shared: " + ", ".join(clash) if clash else "none shared"))
        w("     any old or new text of theirs: %s" % (len(overlap) or "none"))
        muts = [("the monitor's output on a peer's NRST (A's and B's series resistors exchanged at the NRST end)", [(("R812", "2"), ("R822", "2"))]),
                ("the divider's top from the rail, not VCAP", [(("R810", "1"), ("C810", "1"))]),
                ("the divider's top and bottom exchanged (the trip at the other ratio)", [(("R810", "1"), ("R811", "2")), (("R810", "2"), ("R811", "1"))]),
                ("SENSE1 and SENSE2 exchanged (the overvoltage channel on the rail)", [(("U810", "2"), ("U810", "3"))]),
                ("the monitor on a peer's rail", [(("U810", "1"), ("U820", "1"))]),
                ("RESET1 on ground and the ground pin on the output (pins 4 and 10 exchanged)", [(("U810", "4"), ("U810", "10"))])]
        w("   the mutations (each must FAIL the reading; W140's six, W145's seventh on the hold that replaced its capacitor, W148's two):")
        mres = []
        for i, (lab, sw) in enumerate(muts):
            q = D.mutate(net1, d, "hoem%d" % i, sw)
            v_, _wy = mon_check(CHK.read(open(q, "rb").read()), F, dm)
            mres.append(v_)
            w("     %-98s %s" % (lab + ":", v_))
        for lab, tag_, ref_, sw_ in (
                ("the hold removed (W145's seventh on the hold that replaced its capacitor: U811 not fitted, nothing holds NRST)", "hoemhold", "U811", None),
                ("the hold stage bypassed (RESET1 and the stage's RESET exchanged: RESET1 through R812 onto NRST, the stage on its own MR)",
                 "hoembyp", None, [(("U810", "4"), ("U811", "4"))]),
                ("a hold shorter than its printed minimum (R813 not fitted: CT open, the delay %.1f to %.1f ms, under %.0f ms)" % (
                    F["t3_td"][(dm.HOLD_PART[7], "open")][0] * 1e3, F["t3_td"][(dm.HOLD_PART[7], "open")][2] * 1e3, hold[0] * 1e3),
                 "hoemshort", "R813", None)):
            q = remove_part(net1, d, tag_, ref_) if ref_ else D.mutate(net1, d, tag_, sw_)
            nlq = CHK.read(open(q, "rb").read())
            v_, wy_ = mon_check(nlq, F, dm)
            gone = ref_ is None or (ref_ not in nlq["comps"] and ref_ not in nlq["pins"])
            mres.append(v_ if gone else "NOT REMOVED")
            w("     %-98s %s" % (lab + ":", mres[-1]))
            w("       its reading: %s" % ("; ".join(x for x in wy_ if "IOCA" in x or "U811" in x or "U810" in x) or "-")[:220])
        dp = os.path.join(ROOT, DOCS["draft"])
        bare = os.path.join(d, "bare_gen_sch_b.py")
        shutil.copy(D.GEN["b"], bare)
        r_bare = subprocess.run([sys.executable, "-B", dp, bare, "--write"], capture_output=True)
        r_twice = subprocess.run([sys.executable, "-B", dp, bare, "--write"], capture_output=True)
        r_tree = subprocess.run([sys.executable, "-B", dp, D.GEN["b"], "--write"], capture_output=True)
        refused = (r_twice.returncode == 3 and b"already applied" in r_twice.stderr, r_tree.returncode == 3 and b"NOT RELEASED" in r_tree.stderr)
        w("   the draft on the tree's generator as it stands (no other draft): %s (order-free: it edits only the reset block and the class table);" % (
            "applies" if r_bare.returncode == 0 else "REFUSED"))
        w("   a second time: %s; on the tree's own generator: %s" % ("refused" if refused[0] else "NOT REFUSED",
                                                                  "refused (NOT RELEASED)" if refused[1] else "NOT REFUSED"))
        con = []
        for k, t in enumerate(TAGS):
            dom = {n for ref in ("U%d" % (810 + 10 * k), "R%d" % (810 + 10 * k), "R%d" % (811 + 10 * k), "R%d" % (812 + 10 * k), "C%d" % (810 + k),
                                 "U%d" % (811 + 10 * k), "R%d" % (813 + 10 * k), "C%d" % (816 + k))
                   for n in nl1["pins"].get(ref, {}).values()} - {"GND", "NC"}
            con.append(all(n.endswith("IOC%s" % t) or "IOC%s_" % t in n for n in dom))
        w("   CON-004's failure domains ('own regulator branch, reset supervisor, watchdog, crystal and SWD pads'): each monitor touches its own")
        w("   controller's nets and ground only: %s; no controller pin added (CON-017's count unchanged)" % ("yes" if all(con) else "NO"))
        # the firmware row's draft (W145, F3 and F11): on scratch copies of the tree's contract, after T10's draft
        before_c = hashlib.sha256(open(os.path.join(ROOT, DOCS["contract"]), "rb").read()).hexdigest()
        cpy = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copy(os.path.join(ROOT, DOCS["contract"]), cpy)
        rc_bare = subprocess.run([sys.executable, "-B", os.path.join(ROOT, DOCS["cdraft"]), cpy, "--write"], capture_output=True)
        rc_t10 = subprocess.run([sys.executable, "-B", os.path.join(ROOT, DOCS["ct10"]), cpy, "--write"], capture_output=True)
        rc_one = subprocess.run([sys.executable, "-B", os.path.join(ROOT, DOCS["cdraft"]), cpy, "--write"], capture_output=True)
        rc_two = subprocess.run([sys.executable, "-B", os.path.join(ROOT, DOCS["cdraft"]), cpy, "--write"], capture_output=True)
        after_c = open(cpy, encoding="utf-8").read()
        b23 = [l for l in after_c.splitlines() if l.startswith("| FW-B23 |")]
        contract_ok = (rc_bare.returncode == 3 and b"T10 rows" in rc_bare.stderr and rc_t10.returncode == 0 and rc_one.returncode == 0
                       and rc_two.returncode == 3 and b"already applied" in rc_two.stderr and len(b23) == 1
                       and all(k in b23[0] for k in ("PINRSTF and CPURSTF set", "LPWRRSTF, WWDG1RSTF, IWDG1RSTF, SFTRSTF, PORRSTF, BORRSTF, D2RSTF and D1RSTF clear",
                                                     "%.1f us from that write" % (t_resp * 1e6), "RMVF"))
                       and hashlib.sha256(open(os.path.join(ROOT, DOCS["contract"]), "rb").read()).hexdigest() == before_c)
        w("   the firmware row FW-B23 and V-B24 (apply_hw_fw_contract_hoe.py, W145, F3 and F11) on a scratch copy of the tree's contract: alone")
        w("     %s; after apply_hw_fw_contract_t10.py %s; a second time %s; the row carries Table 56's row 2 and the window %.1f us; the" % (
            "refused (T10's rows absent)" if rc_bare.returncode == 3 else "NOT REFUSED", "applies" if rc_one.returncode == 0 else "REFUSED",
            "refused" if rc_two.returncode == 3 else "NOT REFUSED", t_resp * 1e6))
        w("     tree's contract unchanged: %s" % ("yes" if contract_ok else "NO"))
    w("")
    # ---------------------------------------------------------------- 9. findings
    w("9. FINDINGS FOR OTHER AUTHORS AND THE SUPPLIER'S TASKS (amendment 1: none is a gate of this desk round)")
    w("   W140-F1 (L4A-61, Layer 5): FW-B20 restated: VOS3 only; SYSCFG_PWRCR.ODEN never written; the one other VOS write is FW-B23's")
    w("     self-test (drafted, apply_hw_fw_contract_hoe.py); a static check of the image for those writes")
    w("   W140-F2 (Layer 6): the TPS37 option (channel 1 OV, 01, open drain active low, 2 % hysteresis) needs an orderable code and a stock")
    w("     line; TI: '%s'" % F["moq"])
    w("   W140-F3 (Layer 10): the WSON-10 land id is this draft's ASSUMPTION; the divider sits at the VCAP pins, its sense node short; the series")
    w("     resistor at the NRST end; the hold capacitor at CTR1")
    w("   W140-F4 (L4REG-F7, W138): VOS1 and VOS0 entries are ended by the monitor; VOS2 under the trip and VOS3 above 200 MHz are not (S-f,")
    w("     S-g): register rows R-1 and R-2 (HO-E-REGISTER-ROWS.md)")
    w("   W140-F5 (the register, L4A-100): the targeted recheck reads this comparison, the draft and C1 to C3")
    gc = need(text(DOCS["gen_b"]), r"# (Watchdog and brownout are the H743's own IWDG and BOR\. That is deliberate): an internal watchdog cannot save a core", "gen_sch_b.py's supervisors' comment")
    w("   W140-F6 (board B's generator owner): the comment over the supervisors' loop reads '%s: ...'; it" % gc.group(1))
    w("     argues against a supervisor chip for output correctness, which the voters carry; the drafted monitor is for the controller's own")
    w("     VOS0 thermal limit, a different purpose; the draft does not edit the comment; when the draft is taken the comment is restated")
    w("   W145-F1 (the targeted recheck of L4A-100, C1): CLOSED BY W148-1 as a draft: the CTR1 hold was Equation 2's %.1f ms only after a" % (tctr_min * 1e3))
    w("     full discharge (a fault over %.2f ms; a loop's fault from %.1f us, MODEL); the hold stage's %.0f ms is a printed minimum for any MR" % (
        t_full * 1e3, t_fall_min * 1e6, hold[0] * 1e3))
    w("     pulse of at least %.0f us (5d, 5g); the latch W145 named is broken by RESET1 driving MR alone (section 8's bypass mutation)" % F["t3_tmrw"][0])
    w("   W145-F2 (Layer 6): WITHDRAWN with C813 to C815 (W148-1); its successor W148-F2 below")
    w("   W145-F3 (L4A-61, Layer 5): FW-B23 and V-B24 drafted in apply_hw_fw_contract_hoe.py, applied after apply_hw_fw_contract_t10.py; restated")
    w("     by W148 (the window %.1f us, the hold timing W148-3)" % (t_resp * 1e6))
    w("   W145-F4 (the register, the coordinator): rows R-1 (S-f), R-2 (S-g) and R-3 (FW-B23) in HO-E-REGISTER-ROWS.md")
    w("   W145-F5 (IOHA, Layer 5), restated by W148: the hold delays the three supervisors' start by %.1f to %.2f ms after their rail reaches" % (
        hold[0] * 1e3, (F["tsd"] + F["tctr"] + hold[2]) * 1e3))
    w("     %.1f V (5d) and holds the supervisor under test in reset up to %.1f ms each hour; IOHA row 3 (one supervisor out, the other two" % (
        F["vdd_min"], hold[2] * 1e3))
    w("     serve) covers the test")
    w("   W148-F1 (Layer 6): %s's LCSC code and stock line are owed; TI lists it Active (SBVS249B package option addendum); its land" % dm.HOLD_PART)
    w("     WSON-6 1.5 x 1.5 mm is this draft's ASSUMPTION (Layer 10); R813's 10 k and R812's 390 Ohm at 1 % are ordinary parts")
    w("   W148-F2 (Layer 10): the hold stage sits by its TPS37 in the controller's own pocket; CT's pull-up at its pin; R812 at the NRST end")
    w("   W148-F3 (the targeted recheck, C1 to C3): read 5d's new chain (t_resp %.1f us, one TYPICAL term, tPD(MR) %.0f ns), 5g's duty on" % (
        t_resp * 1e6, F["t3_tpdmr"][0]))
    w("     TI's notes B and C read either way, and 5h's comparison; S1's limit is now read at %.1f us, not W145's %.1f us" % (t_resp * 1e6, t_resp_w145 * 1e6))
    w("   W148-F4 (R-2's owner, a note): a loop driven by the image's own resets, each shorter than the TPS37's sense delay, is not seen by")
    w("     the monitor and so not held: each dwell is under tCTS and its cadence rests on the image's boot time, which no held page prints;")
    w("     it is S-g's kind (no printed current for an image outside FW-B20), not this hold's")
    w("   W148-F5 (the coordinator): TI's TPS3808 sheet, which the brief asked fetched and held back, has been committed in the tree since 26")
    w("     September 2026 (v2/vendor/SOURCES.yaml, supervisor-tps3808g30); the fetch of 7 October 2026 is byte for byte that copy")
    w("     (inputs/SOURCES-HOE.txt); its committed status is left as it is (a publication question, not this record's)")
    w("   S1: the controller's junction-to-ambient transient impedance on board B, three first-article supervisors at the rail's top, a junction")
    w("     step at %.4f W: pass at most %.2f K/W at %.1f us (%.2f K/W if the reset loop's %.3f K is carried), and at most %.2f K/W at the" % (
        p_ex, z_need, t_resp * 1e6, z_loop, rise, z_need1))
    w("     VOS1 step %.4f W at %.1f us and %.1f us (or ST's transient thermal data for the LQFP100 with board B's copper)" % (p_ex1, t_resp * 1e6, t_dead * 1e6))
    w("   S2: the monitor's interval on the real VCAP ramp (W144's F11; TI prints tCTS at 1 V/us and 20 % overdrive only, tPD(MR) as NOM only):")
    w("     VCAP driven by the controller's own Scale 1 write and VOS0 entry, three supervisors, the chamber at %.0f C and at -40 C: pass, from" % air)
    w("     the Scale 1 write and from VCAP crossing the trip to NRST under VIL, at most %.1f us; PWR_CSR1's ACTVOS reading Scale 3 at the" % (t_resp * 1e6))
    w("     restart (a printed fact, F5)")
    w("   S3: VCAP in VOS3 with the divider fitted, under the controller's load steps: inside %.2f to %.2f V and under the trip's least %.4f V;" % (
        vc["VOS3"][0], vc["VOS3"][2], lo))
    w("     for a revision X part (W144's F4), its VCAP in VOS3, VOS1 and VOS0 read on three parts against Table 112's revision V rows first")
    w("   S4: NRST held low from the hold stage's VPOR through both UVLOs, the TPS37's tSD and the hold at power-up, released %.1f to %.2f ms" % (
        hold[0] * 1e3, (F["tsd"] + F["tctr"] + hold[2]) * 1e3))
    w("     after VDD reaches %.1f V (scope, ten power cycles each supervisor)" % F["vdd_min"])
    w("   S5: RETIRED (SESSION W148-1): the reset loop's hold is the hold stage's printed minimum, %.0f ms for any MR pulse of at least %.0f us," % (
        hold[0] * 1e3, F["t3_tmrw"][0]))
    w("     so no figure TI does not print decides it; V-B24 still scopes NRST's low time per cycle on the first article as a confirmation of")
    w("     the implementation (pass at least %.0f ms), which closes nothing by itself and gates nothing here" % (hold[0] * 1e3))
    w("")
    # ---------------------------------------------------------------- 10. predicates
    w("10. THE PREDICATES")
    rm_pages = {s: 328 + t329.count("\x0c", 0, t329.index(s)) + 1 == pg for s, pg in (
        ("A system reset (nreset) resets", 329), ("A reset from NRST pin", 329), ("In case of an external reset", 329),
        ("Resets VDD domain: IWDG1, LDO...", 330), ("Debug features, Flash memory, RTC and", 330),
        ("The CPU can reset the flags by setting RMVF bit.", 332), ("Table 56. Reset source identification (RCC_RSR)", 332))}
    want2 = {"LPWRRSTF": 0, "WWDG1RSTF": 0, "IWDG1RSTF": 0, "SFTRSTF": 0, "PORRSTF": 0, "PINRSTF": 1, "BORRSTF": 0, "D2RSTF": 0, "D1RSTF": 0, "CPURSTF": 1}
    sk = [r for r in S if r[0] == "S-k"][0]
    P = [("the five filed copies equal the sha256 SOURCES-HOE.txt names (SOURCES.txt untouched: l9t5_case and l9t5_drafts pin it)", copies_ok),
         ("every quoted sentence of H-1 is in its pinned text, with its page", True),
         ("no option-byte field of FLASH_OPTSR_PRG and no PWR pin of Table 32 selects a voltage scale or the supply configuration", not vos_like and not pin_scale),
         ("T10's 0.1936 A and 112.7 C are reproduced from T10's own air and theta", abs(i105 - i105_t10) < 5e-5 and abs(tj_at(i_trip) - tj_t10) < 0.05),
         ("no printed VOS0 row has an operating point at or under 105 C at the case's air", ops["dis"][0] > 0 and ops["en"][0] > 0),
         ("no package's ThetaJA or ThetaJB in Table 222 reaches H-3's need at one supply corner", min(F["ja"].values()) > need_c and min(F["jb"].values()) > need_c),
         ("the selected divider's band lies inside VOS3's top and VOS1's bottom, its release over VOS3's top", lo > vc["VOS3"][2] and hi < vc["VOS1"][0] and rel > vc["VOS3"][2]),
         ("the printed 20 % overdrive does not cover VOS0's bottom (S2 is owed, not assumed)", od0 < 0.20),
         ("the hold stage's drain: its peak under TI's recommended maximum, its held current over the minimum, NRST held under VIL",
          i_pk <= F["t3_irec"] and i_hold_min >= F["t3_irec_min"] and v_inf_w < F["vil_k"] * rail[0]),
         ("the draft composes with and without W137's and W138's drafts, in either order, and reads DRAWN", v1_ == "DRAWN" and v2_ == "DRAWN" and v0_ == "FAIL" and same_order and not overlap and not clash),
         ("each of the nine mutations FAILS: W140's six, the hold removed, the hold stage bypassed, a hold under its printed minimum",
          all(v == "FAIL" for v in mres) and len(mres) == 9),
         ("the draft refuses a second application and the tree's own generator", all(refused)),
         ("each monitor stays inside its controller's failure domain", all(con)),
         ("the VOS0 and VOS1 entries and the reset loop read CONDITIONAL, none HOLDS, and H-1 claims no hardware bar",
          all(r[4].startswith("CONDITIONAL") for r in S[2:5]) and sk[4].startswith("CONDITIONAL") and not vos_like),
         ("T10's bounded state (99.6 C, 0.1570 A) is reproduced at 3.3 V by T10's own model before it is read at one supply corner",
          abs(tb3 - tj_b) < 0.05 and abs(ib3 - i_b) < 5e-5 and tbc > tb3),
         ("VOS1's step takes the largest printed 125 C row of Tables 119 to 121 (Table 120's 544 mA, W144's F7)", t_v1 == "Table 120" and abs(i_v1[t_v1] - 0.544) < 1e-9),
         ("the hold is a printed minimum for any MR pulse of tMR_W (MIN column) and the loop's least pulse exceeds it: S-k on S1 and S2, not S5",
          F["t3_tmrw"][1] == "MIN" and t_fall_min > F["t3_tmrw"][0] * 1e-6 and hold[0] > 0 and "S5" not in sk[4] and sk[4].startswith("CONDITIONAL")),
         ("RM0433 Table 56's pin-reset row is PINRSTF and CPURSTF set, every other flag clear, and six other rows set PINRSTF",
          pat2 == want2 and len(pin_too) == 6),
         ("every TPS37 page quoted is the page its text sits on (form feeds counted)", all(F["tps_pages"][k] == int(k.split("p.")[1]) for k in F["tps_pages"])),
         ("every RM0433 sentence quoted from pages 329 to 332 sits on the page named (form feeds counted)", all(rm_pages.values())),
         ("the trip window rests on DS12110's revision V pages, and rev Y's Table 14 prints no core voltage per scale",
          F["revv_hdr"] >= 2 and F["revy_hdr"] and not F["revy_vos"]),
         ("the bounded state reaches 105 C at a local air between the case's air and the exhaust air (C2)", air < air105_c < PT10["air_exhaust"]),
         ("the firmware row applies after T10's draft only, once, and leaves the tree's contract unchanged", contract_ok),
         ("every TPS3703 page quoted is the page its text sits on (form feeds counted)", all(F["t3_pages"][k] == int(k.split("p.")[1]) for k in F["t3_pages"])),
         ("no orderable TPS3703 window keeps VOS3's band inside it and trips under VOS1 (HS-2 needs a non-stock option)", not fits_stock and bool(fits_cat)),
         ("HS-1a's MR registration is TYPICAL only and HS-1b's tMR_W a MIN, and HS-1b's t_resp is the shorter (W148-1's reasons hold)",
          F["t38_tw_mr"][1] == "TYP" and F["t3_tmrw"][1] == "MIN" and t_resp < t_resp_a),
         ("W148-3's hold check reads the printed hold as PASSED and a CT-open hold as FAILED on an RTC clock within the tolerance",
          hold[0] * (1 - RTC_TOL) >= T_HOLD_CHECK_S > F["t3_td"][(dm.HOLD_PART[7], "open")][2] * (1 + RTC_TOL))]
    for lab, ok in P:
        w("   %-128s %s" % (lab, "yes" if ok else "NO"))
    w("")
    w("l9t5_hoe: done")
    txt = "\n".join(out) + "\n"
    sys.stdout.write(txt)
    return 0 if all(ok for _l, ok in P) else 1


if __name__ == "__main__":
    sys.exit(main())
