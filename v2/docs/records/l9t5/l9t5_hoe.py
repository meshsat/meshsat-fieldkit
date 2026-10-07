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
    "v2/vendor/ti/ti-tps3808.pdf": [["-layout", "-f", "7", "-l", "7"], ["-layout", "-f", "11", "-l", "11"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PDFT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PDFT)
RM = "v2/vendor/st/st-rm0433-rev8.pdf"
DS = "v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf"
AN = "v2/vendor/st/st-an4938-rev7.pdf"
TPS = "v2/vendor/ti/ti-tps37-snvsbj1e.pdf"
TPS38 = "v2/vendor/ti/ti-tps3808.pdf"
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
    if len(nodes) != 2:
        refuse("the mutation's part %s is not on two nodes once each: %d" % (ref, len(nodes)))
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


def mon_check(nl, F, draft_mod):
    """the monitors read by pin on a netlist: per controller, its TPS37 on its own rail, SENSE1 on a node fed only by a divider from
    its own VCAP, SENSE2 on its own rail, RESET1 through the series resistor to its own NRST (the controller's pin 14), CTR1/MR on a
    node carrying only the hold capacitor to GND (W145), the unused pins open, the bypass at its VDD; the divider's values read off the
    netlist give a trip band inside (VOS3's top, VOS1's bottom) and a release over VOS3's top; the hold capacitor's value at least the
    draft's (Equation 2's hold no shorter than the reset-loop row's)"""
    why = []
    v3, v1 = F["vcore"]["VOS3"][2], F["vcore"]["VOS1"][0]
    for k, t in enumerate(TAGS):
        u, rt, rb, rs, cb = "U%d" % (810 + 10 * k), "R%d" % (810 + 10 * k), "R%d" % (811 + 10 * k), "R%d" % (812 + 10 * k), "C%d" % (810 + k)
        ch, mctr = "C%d" % (813 + k), "IOC%s_MONCTR" % t
        v33, vmon, mrst, nrst, vcap = "+3V3_IOC%s" % t, "IOC%s_VMON" % t, "IOC%s_MONRST" % t, "IOC%s_RST_n" % t, "IOC%s_VCAP" % t
        if not CHK.value(nl, u).startswith("TPS37 "):
            why.append("%s is %r, not a TPS37" % (u, CHK.value(nl, u)[:24]))
            continue
        why += CHK.rows(nl, [(u, "1", v33), (u, "2", vmon), (u, "3", v33), (u, "4", mrst), (u, "6", mctr), (u, "10", "GND"), (u, "11", "GND")])
        why += CHK.rows(nl, [(ch, "1", mctr), (ch, "2", "GND")])
        if CHK.members(nl, mctr) != sorted(["%s.6" % u, "%s.1" % ch]):
            why.append("%s carries %s, not CTR1 and its hold capacitor alone" % (mctr, CHK.members(nl, mctr)))
        vh = CHK.value(nl, ch)
        if not re.fullmatch(r"\d+(?:\.\d+)?[pnu](?: .*)?", vh):
            why.append("%s's value %r not readable (not fitted?)" % (ch, vh))
        elif farads(vh) < farads(draft_mod.HOLD):
            why.append("%s is %s, under the draft's %s: the hold shorter than the reset-loop row's" % (ch, vh, draft_mod.HOLD))
        for p in ("5", "7", "8", "9"):
            if CHK.pin(nl, u, p) not in (None, "NC"):
                why.append("%s.%s is on %s, wanted open" % (u, p, CHK.pin(nl, u, p)))
        if CHK.members(nl, vmon) != sorted(["%s.2" % u, "%s.2" % rt, "%s.1" % rb]):
            why.append("%s carries %s, not the monitor's SENSE1 and its divider alone" % (vmon, CHK.members(nl, vmon)))
        why += CHK.rows(nl, [(rt, "1", vcap), (rb, "2", "GND"), (rs, "1", mrst), (rs, "2", nrst), (cb, "1", v33), (cb, "2", "GND")])
        if CHK.members(nl, mrst) != sorted(["%s.4" % u, "%s.1" % rs]):
            why.append("%s carries %s, not RESET1 and its series resistor alone" % (mrst, CHK.members(nl, mrst)))
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
        for ref in (u, rt, rb, rs, cb, ch):
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
    pins = [RM, DS, AN, TPS, TPS38] + [DOCS[k] for k in ("draft", "guard", "drafts", "t10out", "t10py", "gen_b", "gennet", "ledger", "cx46", "l4reg",
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
    w("       an external divider), open-drain active-low RESET1 to that controller's NRST through %s, VDD on the controller's own 3.3 V." % dm.SERIES)
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
    rs = ohms(dm.SERIES)
    i_pk = rail[1] / (rs * (1 - tol(dm.SERIES)))                    # the drain at 0 V: the largest current it can sink through the series resistor
    r_low = rs * (1 + tol(dm.SERIES))
    c_rst = 100e-9 * (1 + C_RST_TOL)
    # the open drain holds at most VOL (300 mV) whenever it sinks 5 mA or less (p.7; ASSUMPTION: its current rises with its voltage), so
    # the node falls through r_low toward at most 300 mV, against the pull-ups; every corner of the rail and the pull-ups, the slowest kept
    t_fall = 0.0
    for v33 in rail:
        for r_up in (1.0 / (1.0 / (10e3 * (1 - TOL_PLAIN)) + 1.0 / F["rpu"][0]), 1.0 / (1.0 / (10e3 * (1 + TOL_PLAIN)) + 1.0 / F["rpu"][2])):
            a = (F["vol"] / v33 * r_up + r_low) / (r_low + r_up)
            tau = c_rst * (r_low * r_up / (r_low + r_up))
            t_fall = max(t_fall, tau * math.log((1 - a) / (F["vil_k"] - a)))
    t_resp = F["tcts"][1] + t_fall + F["vnf"]
    w("       the ending's timing, VCAP over the trip to the controller in reset:")
    w("         TPS37 sense delay tCTS %.0f us typ, %.0f us max at VIT 800 mV with CTS open, '20%% Overdrive from VIT' (7.6, p.9, PRINTED);" % (
        F["tcts"][0] * 1e6, F["tcts"][1] * 1e6))
    w("           VOS0's bottom %.2f V is %.1f %% over the trip's top, VOS1's %.2f V is %.1f %%: under 20 %%, so the printed maximum does NOT cover" % (
        vc["VOS0"][0], od0 * 100, vc["VOS1"][0], od1 * 100))
    w("           these entries (supplier task S2); 17 us is carried below as the figure S2 must confirm, never as a bound")
    w("         NRST pulled from the rail to VIL %.1f x VDD (Table 147, p.241: '%.1fVDD', NRST with the I/O rows) through %s and the open drain" % (F["vil_k"], F["vil_k"], dm.SERIES))
    w("           (at most VOL %.0f mV while it sinks 5 mA or less, p.7; ASSUMPTION: its current rises with its voltage) against NRST's 10 k" % (F["vol"] * 1e3))
    w("           (+-5 %%, ASSUMPTION) and RPU %.0f to %.0f kOhm (Table 152, p.248), every corner of the rail and the pull-ups" % (F["rpu"][0] / 1e3, F["rpu"][2] / 1e3))
    w("           and the 100 nF reset capacitor (+-20 %%, ASSUMPTION): at most %.1f us (MODEL); the peak sink %.2f mA under the recommended %.0f mA" % (
        t_fall * 1e6, i_pk * 1e3, F["ireset_rec"] * 1e3))
    w("           (7.3, p.6) and the absolute %.0f mA (7.1, p.6)" % (F["ireset_abs"] * 1e3))
    w("         NRST's 'Input not filtered pulse' at least %.0f ns (Table 152 and its note 2, p.248)" % (F["vnf"] * 1e9))
    w("         t_resp = %.0f + %.1f + %.1f us = %.1f us (CONDITIONAL on S2's sense delay)" % (F["tcts"][1] * 1e6, t_fall * 1e6, F["vnf"] * 1e6, t_resp * 1e6))
    # the reset hold (W145-1, W144's F1): CTR1 to GND through dm.HOLD, Equations 1 to 3 of 8.3.4.1 (p.23) on RCTR (7.5, p.8)
    c_hold = (farads(dm.HOLD) * (1 - C_RST_TOL), farads(dm.HOLD), farads(dm.HOLD) * (1 + C_RST_TOL))
    tctr_min = -math.log(F["eq"]["min"]) * F["rctr"][0] * c_hold[0] + 0.0      # tCTR(no cap)(min): no minimum printed, taken 0
    tctr_typ = -math.log(F["eq"]["typ"]) * F["rctr"][1] * c_hold[1]            # Equation 1 without its unprinted typical no-cap term
    tctr_max = -math.log(F["eq"]["max"]) * F["rctr"][2] * c_hold[2] + F["tctr"]  # the no-cap maximum, 40 us at 800 mV (7.6, p.9)
    t_full = F["full_frac"] * tctr_max                                          # the fault TI needs for a full discharge, at the largest delay
    # the fastest NRST fall to VIL (the fault's least length in a loop: the controller holds VCAP up until it is reset), the opposite
    # corner of t_fall: the least capacitor and series resistor, the weakest pull-ups, the drain at 0 V
    c_lo, r_lo = 100e-9 * (1 - C_RST_TOL), rs * (1 - tol(dm.SERIES))
    r_weak = 1.0 / (1.0 / (10e3 * (1 + TOL_PLAIN)) + 1.0 / F["rpu"][2])
    a_lo = r_lo / (r_lo + r_weak)
    t_fall_min = c_lo * (r_lo * r_weak / (r_lo + r_weak)) * math.log((1 - a_lo) / (F["vil_k"] - a_lo))
    w("       the reset hold (SESSION W145-1, W144's F1: CTR1/MR to GND through %s, read at +-%.0f %% as the reset capacitor is, ASSUMPTION; the" % (
        dm.HOLD, C_RST_TOL * 100))
    w("         pin's own words: '%s', Table 6-1 p.5; it is never driven, so it serves as the delay only):" % F["mr_q"])
    w("         RCTR %.0f / %.0f / %.0f kOhm (7.5, p.8); TI's Equations (8.3.4.1, p.23): typ -ln(%.2f), min -ln(%.2f), max -ln(%.2f) x RCTR x CCTR" % (
        F["rctr"][0] / 1e3, F["rctr"][1] / 1e3, F["rctr"][2] / 1e3, F["eq"]["typ"], F["eq"]["min"], F["eq"]["max"]))
    w("         + tCTR(no cap): tCTR(min) = %.4f x %.0f kOhm x %.0f nF + 0 = %.1f ms (the no-cap minimum is not printed: taken 0); tCTR(typ) %.1f ms;" % (
        -math.log(F["eq"]["min"]), F["rctr"][0] / 1e3, c_hold[0] * 1e9, tctr_min * 1e3, tctr_typ * 1e3))
    w("         tCTR(max) = %.4f x %.0f kOhm x %.0f nF + %.0f us = %.1f ms (PRINTED form, MODEL on the assumed capacitor band)" % (
        -math.log(F["eq"]["max"]), F["rctr"][2] / 1e3, c_hold[2] * 1e9, F["tctr"] * 1e6, tctr_max * 1e3))
    w("         its condition, TI's own words (8.3.4.1, p.23): '%s' and '%s'" % (F["short_q"], F["full_q"]))
    w("         so Equation 2's %.1f ms is a hold only after a fault longer than %.0f %% of the programmed delay: at most %.2f ms at tCTR(max)" % (
        tctr_min * 1e3, F["full_frac"] * 100, t_full * 1e3))
    w("         the cost: every self-test's reset and every power-up hold the controller up to %.1f ms more (below); no service needs it sooner" % (tctr_max * 1e3))
    w("       power-up: '%s' (8.3.1.1, p.18), VPOR %.1f V; the H743 leaves its own BOR0 reset from %.2f to %.2f V rising (Table 116, p.212), so" % (
        F["uvlo_q"], F["vpor"], F["bor0"][0], F["bor0"][2]))
    w("         NRST is held until the TPS37's VDD reaches its %.1f V minimum; then '%s' (7.6 note 4, p.9), tSD %.0f ms (p.9);" % (F["vdd_min"], F["tsd_note"], F["tsd"] * 1e3))
    w("         '%s' (the same note); Figure 7-3 (p.12) marks the first release at 'tSD + tCTRx' (DIAGRAM): from %.1f ms (tSD's minimum" % (
        F["tsd_cap_q"], tctr_min * 1e3))
    w("         is not printed) to %.1f ms after VDD reaches its minimum; no unmonitored start if the drawing holds (supplier task S4)" % ((F["tsd"] + tctr_max) * 1e3))
    w("       the rails: the TPS37 runs from %.1f V (7.3, p.6) on a rail of %.4f to %.4f V; its IDD at most %.1f uA (p.7); the divider loads VCAP" % (
        F["vdd_min"], rail[0], rail[1], F["idd"] * 1e6))
    w("         with at most %.1f uA: ST prints no figure for a load on VCAP (ASSUMPTION, supplier task S3); no case row changes" % (
        vc["VOS0"][2] / ((ohms(dm.TOP) + ohms(dm.BOTTOM)) * (1 - 0.001 - 25e-6 * TEMPCO_K)) * 1e6))
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
    w("   5e. ITS OWN FAULTS AND THEIR SELF-TEST (SESSION W140-3 as restated by W145-2 and W145-3 on W144's F3 and F11; the firmware row is")
    w("       FW-B23, drafted in apply_hw_fw_contract_hoe.py for L4A-61; nothing applied): at every start and then once every %.0f s, at HCLK" % T_TEST_S)
    w("       at most 144 MHz, the controller clears the reset flags (\"%s\", RM0433 8.4.4, p.332), keeps a marker where NRST does" % q_rmvf)
    w("       not reach (Table 55, p.330: \"%s\"), writes VOS = Scale 1 and waits at most %.1f us from that write (t_resp: the window" % (q_t55b, t_win * 1e6))
    w("       timed from the write covers the regulator's ramp, the monitor and NRST's fall on every unit in service, W144's F11; it replaces")
    w("       W140's VOSRDY 1 ms and 2 ms waits); still running, it writes Scale 3 within %.0f us (W145-2) and reports MONITOR FAILED in its" % T_RESTORE_US)
    w("       state frame. After the reset, PASSED needs the marker and RCC_RSR equal to Table 56's row 2, 'Pin reset (NRST)' (RM0433 8.4.4,")
    w("       p.332): %s set, %s clear (W145-3)." % (" and ".join(k for k in hdr if pat2[k]), ", ".join(k for k in hdr if not pat2[k])))
    w("       PINRSTF alone is not enough: \"%s\", \"%s\" (8.7.39, p.450), and Table 56 sets it in the rows %s too" % (q_pin, q_pin2, "; ".join(pin_too)))
    w("       (W144's F3). Scale 1 (VCAP %.2f V and up) is over the trip's top by %.1f %%: the test drives the whole real path, VCAP to divider to" % (vc["VOS1"][0], od1 * 100))
    w("       SENSE1 to RESET1 to NRST. One supervisor tests at a time and only while the other two serve (IOHA row 3); the peers flag a")
    w("       supervisor whose test counter has not moved for 2 x %.0f s (FW-B22's state frame). A healthy unit whose ramp makes the interval" % T_TEST_S)
    w("       from the write longer than t_resp reads MONITOR FAILED: found at the first article by S2, and then the window and S1's limit are")
    w("       re-read together (W145-2's reversal)")
    faults = [("divider top open or bottom shorted", "SENSE1 at 0 V: never trips", "the next test (no reset)"),
              ("divider bottom open or top shorted", "SENSE1 at VCAP (1.0 V and up) over 0.808 V: held in reset", "at once (the controller silent, IOHA row 3)"),
              ("a divider value drifted", "the band moves", "the test if the trip passes VOS1's bottom; else at once (held in reset)"),
              ("RESET1 stuck released, or the series resistor open", "never resets", "the next test"),
              ("RESET1 stuck low, or MONRST shorted to ground", "held in reset", "at once"),
              ("the TPS37 unpowered (VDD open)", "output undefined under VPOR", "the next test, or at once if it rests low"),
              ("SENSE1 and SENSE2 exchanged or shorted (assembly)", "SENSE1 at the rail: held in reset", "at once"),
              ("a slowed monitor (sense delay or NRST fall)", "the ending takes longer than t_resp", "the next test (its window is t_resp, F11)"),
              ("the hold capacitor shorted (CTR1/MR at GND)", "manual reset asserted: held in reset", "at once"),
              ("the hold capacitor open or missing", "the hold falls to tCTR(no cap)", "NOT by the test (it times no hold): S5 and inspection"),
              ("a firmware that skips the test", "a latent monitor fault stays latent", "the peers, within 2 x %.0f s" % T_TEST_S)]
    for f_, eff, det in faults:
        w("         %-50s %-58s found: %s" % (f_, eff, det))
    w("       the residuals: a monitor fault latent since the last test, then a firmware VOS0 entry: a double fault, its window at most %.0f s;" % T_TEST_S)
    w("       an open hold capacitor, then an image that enters VOS1 or VOS0 at every boot: a double fault the self-test does not bound (S-l)")
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
    # 5g the reset loop (W144's F1)
    duty = t_resp / (t_resp + tctr_min)
    rise = duty * p_ex * F["ja"]["LQFP100"]
    z_loop = (dT - rise) / p_ex
    t38 = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "7", "-l", "7"], PDFTEXT, REC)
    t38b = PDFT.pdf_text(ROOT, TPS38, ["-layout", "-f", "11", "-l", "11"], PDFTEXT, REC)
    m38 = need(t38, r"CT = VDD\s+(\d+)\s+(\d+)\s+(\d+)\s+ms", "TPS3808 6.6 td at CT = VDD (p.7)")
    td38 = [float(x) * 1e-3 for x in m38.groups()]
    need(t38, r"SBVS050N", "the TPS3808 sheet's revision")
    q38 = quote(t38b, "After MR returns to a logic high and SENSE is above its reset threshold, RESET is de-asserted after the user-defined "
                      "reset delay expires.", "TPS3808 7.3.3 (p.11)")
    w("   5g. THE RESET LOOP (W144's F1): an image that enters VOS1 or VOS0 at every boot. Each cycle it is in VOS1 or VOS0 for at most t_resp")
    w("       (S2) at the %.4f W step, then in reset; the reset and the boot are taken at no more than the bounded state's power (ASSUMPTION: the" % p_ex)
    w("       reset state, VOS3 with the reset clocks and every peripheral at reset, RM0433 p.279, inside FW-B20's bound)")
    w("         CTR1 open (W140's draft): the hold is tCTR(no cap), at most %.0f us and no minimum printed: the duty has no printed bound under 1" % (F["tctr"] * 1e6))
    w("         CTR1 at %s (this draft), after a full discharge: hold at least %.1f ms; duty at most %.1f / (%.1f + %.0f) us = %.3f %%; average rise" % (
        dm.HOLD, tctr_min * 1e3, t_resp * 1e6, t_resp * 1e6, tctr_min * 1e6, duty * 100))
    w("           at most %.3f %% x %.4f W x %.1f C/W = %.3f K (MODEL); S1's limit at t_resp becomes (%.2f - %.3f) / %.4f = %.2f K/W (the average" % (
        duty * 100, p_ex, F["ja"]["LQFP100"], rise, dT, rise, p_ex, z_loop))
    w("           plus one pulse's own rise, a superposition MODEL)")
    w("         ITS CONDITION, NOT SHOWN: TI's full discharge needs a fault longer than %.2f ms (5d). In the loop the fault lasts from the crossing" % (t_full * 1e3))
    w("           until VCAP falls under the release level: at least NRST's fastest fall to VIL, %.1f us (MODEL: %.0f nF, %.1f Ohm, the pull-ups" % (
        t_fall_min * 1e6, c_lo * 1e9, r_lo))
    w("           at their weakest, the drain at 0 V; tCTS's minimum is not printed, taken 0), while the controller still holds VCAP up, plus")
    w("           VCAP's fall after the reset, which no held document prints (the core's load in reset, the regulator on the scale change).")
    w("           %.1f us is %.1f %% of %.2f ms: on printed figures the hold after a loop's fault may be shorter than %.1f ms ('%s')." % (
        t_fall_min * 1e6, t_fall_min / t_full * 100, t_full * 1e3, tctr_min * 1e3, "the delay will be shorter than expected"))
    w("           So the %.3f %% and %.3f K are CONDITIONAL on S5 (section 9); S-k reads CONDITIONAL, never HOLDS" % (duty * 100, rise))
    w("         the route that removes S5 (finding W145-F1, for the targeted recheck; NOT drafted here, SESSION W145-5): a stage whose delay")
    w("           does not depend on the fault's length, for example board B's own TPS3808G30 with CT to VDD, td %.0f / %.0f / %.0f ms (TI SBVS050N" % tuple(x * 1e3 for x in td38))
    w("           6.6, p.7) and '%s' (7.3.3, p.11), RESET1 on its MR and its RESET on NRST;" % q38)
    w("           drawn naively it latches (its RESET holds NRST, NRST holds MONRST through the 750 Ohm, MONRST holds MR), so RESET1 must drive")
    w("           MR alone or through a diode; its response path, its own faults and their self-test are new work with their own check")
    w("   VERDICT H-2: NOT SUPPORTED ON PRINTED FIGURES AS A PROOF: the register's end condition ('no printed timing bounds the entry-to-reset")
    w("   interval, or the thermal time cannot be bounded on printed figures') is met, since neither the sense delay at VOS0's overdrive (S2)")
    w("   nor the controller's transient impedance (S1) is printed, and the reset loop's hold rests on TI's full-discharge condition (S5).")
    w("   It STANDS as the one drafted design that ends every VOS1 and VOS0 entry whatever the firmware does, on printed thresholds:")
    w("   PROVISIONAL under amendment 1, S1, S2 and S5 supplier tasks with pass limits, not a closure. Not claimed: a hardware bar, a")
    w("   printed interval, or a printed bound on the reset loop.")
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
         ("S-h", "power-up before the monitor is valid", "105 C", "NRST held under UVLO (p.18), then to tSD + tCTR (DIAGRAM; p.9 note 4)", "CONDITIONAL (S4)"),
         ("S-i", "a latent monitor fault, then a firmware VOS0 entry", "105 C", "a double fault; window at most %.0f s" % T_TEST_S, "RESIDUAL (single-fault)"),
         ("S-k", "the reset loop: an image entering VOS1 or VOS0 at every boot", "105 C",
          "duty <= %.3f %%, rise <= %.3f K; needs ZthJA(t_resp) <= %.2f K/W" % (duty * 100, rise, z_loop), "CONDITIONAL (S5, S1, S2)"),
         ("S-l", "an open hold capacitor, then the reset loop", "105 C", "a double fault the self-test does not see; inspection and S5",
          "RESIDUAL (single-fault)"),
         ("S-j", "any current up to the limiter's %.4f A" % ios[1], "as above", "a VOS3 state is S-a, S-b or S-g; a VOS1 or VOS0 state S-c, S-d or S-k",
          "no state outside S-a to S-l")]
    for row in S:
        w("   %-4s %-60s %-9s %-66s %s" % row)
    w("   THE CONDITIONS OF THE FOCUSED CHECK (W144, L4A-100), RESTATED:")
    w("     C1 (F1): the CTR1 hold drafted, composed, read and mutated, with the reset-loop row: DONE here (5d, 5g, section 8); the row's bound")
    w("        is CONDITIONAL on S5 (TI's full-discharge condition, W145-F1); a fixed-delay stage would remove S5 (not drafted)")
    w("     C2 (F2): U-02's local air at the supervisors at or under %.2f C (MODEL at %.4f V; W144's linear %.1f C)" % (air105_c, CORNER, air105_lin))
    w("     C3 (F4): revision V fitted (L9T5-D7): the trip window rests on Table 112's rows on DS12110's '(rev V)' pages (p.209); rev Y's Table 14")
    w("        (p.105) prints no core voltage per scale, and no held page prints rev X's; a rev X part also needs its VCAP per scale (S3)")
    w("     C4 (F8, F11): S1 at one supply corner (at most %.2f K/W at t_resp, %.2f K/W less the loop's rise with S5); S2 on the real VCAP" % (z_need, z_loop))
    w("        ramp, the self-test's window timed from the Scale 1 write; S3 and S4 as written; S5 new")
    w("     C5 (F3, F6): the register rows, HO-E-REGISTER-ROWS.md (R-1 S-f, R-2 S-g, R-3 the self-test's firmware row FW-B23, drafted in")
    w("        apply_hw_fw_contract_hoe.py)")
    w("   HO-E's ACCEPTANCE: CONDITIONAL. The served state holds 105 C; every VOS0 state the protection admits is ended by the drafted monitor,")
    w("   and whether the junction stays inside 105 C during the ending rests on S1 and S2, in a reset loop also on S5, and on C2 and C3.")
    w("   Nothing is upgraded: cx46 CORRECTIONS NOT CLOSED and Layer 4's DESK gate NOT PASSED stand; this task closes no cx46 item before")
    w("   its own check's targeted recheck (L4A-100).")
    w("")
    # ---------------------------------------------------------------- 7. the selection
    w("7. THE SELECTION")
    w("   SESSION W140-1: H-2 with the drafted VCORE monitor (apply_gen_sch_b_vcoremon.py) and the firmware rows of 5e, PROVISIONAL on S1 to S5.")
    w("     authority: SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026")
    w("     authority_why: an engineering selection inside the drafted circuit; no requirement, protected class, case row, purchase or")
    w("       publication changes; one approach stands after the reading (H-1 drops out on the documents, H-3 is not established on printed")
    w("       figures), so the ruling's second half (more than one option standing) fails; the residuals are measurable on a specimen (S1 to")
    w("       S5), so the selection accepts no risk a measurement cannot remove: amendment 1's supplier tasks, not an owner's risk acceptance")
    w("     ruled_by: W140 (Claude), MESHSAT-1357; ruled_on: 7 October 2026; reversed_by: none")
    w("     to reverse: drop apply_gen_sch_b_vcoremon.py; HO-E returns to REMAINING ENGINEERING with the owner item below")
    w("     end condition: S1 reads the controller's ZthJA at t_resp over %.2f K/W on board B (%.2f K/W less the loop's rise); or S2 reads" % (z_need, z_loop))
    w("       the sense delay at VOS0's overdrive long enough that S1's reading fails at the longer interval; or S5 fails and the fixed-delay")
    w("       stage (W145-F1) is not taken; or two negative independent checks of this selection")
    w("   W145's decisions (each authority: SESSION, under the same rules; ruled_by: W145 (Claude), MESHSAT-1357; ruled_on: 7 October 2026;")
    w("   reversed_by: none; authority_why: an engineering value or method inside the drafted circuit and its rows, no requirement, class,")
    w("   case row, purchase or publication changed, one option standing after the focused check's reading):")
    dec = [("W145-1", "the reset hold: %s from CTR1/MR to GND per monitor (C813, C814, C815), read at +-%.0f %%" % (dm.HOLD, C_RST_TOL * 100),
            "W144's F1 value: Equation 2's %.1f ms keeps the loop's duty at %.3f %%; it costs at most %.1f ms of reset at power-up and per test" % (
                tctr_min * 1e3, duty * 100, tctr_max * 1e3), "another value with 5g re-read"),
           ("W145-2", "the self-test's window: t_resp from the Scale 1 write, then Scale 3 within %.0f us" % T_RESTORE_US,
            "W144's F11: the ending timed on every unit in service, a slowed monitor found; the dead-monitor dwell bounded at %.1f us" % (t_dead * 1e6),
            "a window read from S2's measured ramp, S1 re-read"),
           ("W145-3", "PASSED: the marker and RCC_RSR equal to Table 56's row 2", "W144's F3: six other rows set PINRSTF too", "none needed"),
           ("W145-4", "every thermal limit at one supply corner, %.4f V" % CORNER, "W144's F8: W140 mixed a 3.3 V state with a rail-top step",
            "a narrower rail band issued as a case row"),
           ("W145-5", "the loop's bound left CONDITIONAL on S5; the fixed-delay stage named, not drafted",
            "the brief fixes the CTR1 hold; the stage needs a second part per supervisor, a latch-breaking element and its own check",
            "draft the stage (W145-F1)")]
    for d_ in dec:
        w("     %-7s %s" % d_[:2])
        w("             why: %s; to reverse: %s" % d_[2:])
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
        w("   RESET1 through %s to the controller's own pin 14, the other pins open, the bypass at VDD, every part inside its controller's" % dm.SERIES)
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
        w("   the mutations (each must FAIL the reading; the last, W145's on W144's F1, takes controller A's hold capacitor out):")
        mres = []
        for i, (lab, sw) in enumerate(muts):
            q = D.mutate(net1, d, "hoem%d" % i, sw)
            v_, _wy = mon_check(CHK.read(open(q, "rb").read()), F, dm)
            mres.append(v_)
            w("     %-98s %s" % (lab + ":", v_))
        q = remove_part(net1, d, "hoemhold", "C813")
        nlq = CHK.read(open(q, "rb").read())
        v_, wy_ = mon_check(nlq, F, dm)
        gone = "C813" not in nlq["comps"] and "C813" not in nlq["pins"]
        mres.append(v_ if gone else "NOT REMOVED")
        w("     %-98s %s" % ("the hold capacitor removed (C813 not fitted: CTR1/MR open, the hold back to tCTR(no cap)):", mres[-1]))
        w("       its reading: %s" % "; ".join(x for x in wy_ if "C813" in x or "MONCTR" in x)[:200])
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
                                 "C%d" % (813 + k))
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
    w("   W145-F1 (the targeted recheck of L4A-100, C1): the CTR1 hold is Equation 2's %.1f ms only after a full discharge, which TI ties to a" % (tctr_min * 1e3))
    w("     fault longer than %.0f %% of the programmed delay (%.2f ms); a reset loop's fault is NRST's fall (from %.1f us, MODEL) plus VCAP's" % (
        F["full_frac"] * 100, t_full * 1e3, t_fall_min * 1e6))
    w("     unprinted fall: S5. A delay that does not depend on the fault's length (a TPS3808 with CT to VDD, td from %.0f ms, SBVS050N 6.6" % (td38[0] * 1e3))
    w("     p.7) removes S5 if the latch through NRST is broken; drafting it is the next step if the recheck or S5 rejects the CTR1 hold")
    w("   W145-F2 (Layer 6): the hold capacitor C813, C814, C815: a ceramic 100 nF part that stays inside -%.0f %% to +%.0f %% over its tolerance," % (
        C_RST_TOL * 100, C_RST_TOL * 100))
    w("     its temperature at the supervisors and its bias on CTR1 (at most 5.5 V, the node's declaration), or 5g is re-read on its band")
    w("   W145-F3 (L4A-61, Layer 5): FW-B23 and V-B24 drafted in apply_hw_fw_contract_hoe.py, applied after apply_hw_fw_contract_t10.py")
    w("   W145-F4 (the register, the coordinator): rows R-1 (S-f), R-2 (S-g) and R-3 (FW-B23) in HO-E-REGISTER-ROWS.md")
    w("   W145-F5 (IOHA, Layer 5): the hold delays the three supervisors' start by %.1f to %.1f ms after their rail (tSD + tCTR) and holds the" % (
        tctr_min * 1e3, (F["tsd"] + tctr_max) * 1e3))
    w("     supervisor under test in reset up to %.1f ms each hour; IOHA row 3 (one supervisor out, the other two serve) covers the test" % (tctr_max * 1e3))
    w("   S1: the controller's junction-to-ambient transient impedance on board B, three first-article supervisors at the rail's top, a junction")
    w("     step at %.4f W: pass at most %.2f K/W at %.1f us (%.2f K/W if the reset loop's %.3f K is carried, S5), and at most %.2f K/W at the" % (
        p_ex, z_need, t_resp * 1e6, z_loop, rise, z_need1))
    w("     VOS1 step %.4f W at %.1f us and %.1f us (or ST's transient thermal data for the LQFP100 with board B's copper)" % (p_ex1, t_resp * 1e6, t_dead * 1e6))
    w("   S2: the monitor's interval on the real VCAP ramp (W144's F11; TI prints tCTS at 1 V/us and 20 % overdrive only): VCAP driven by the")
    w("     controller's own Scale 1 write and VOS0 entry, three supervisors, the chamber at %.0f C and at -40 C: pass, from the Scale 1 write and" % air)
    w("     from VCAP crossing the trip to NRST under VIL, at most %.1f us; PWR_CSR1's ACTVOS reading Scale 3 at the restart (a printed fact, F5)" % (t_resp * 1e6))
    w("   S3: VCAP in VOS3 with the divider fitted, under the controller's load steps: inside %.2f to %.2f V and under the trip's least %.4f V;" % (
        vc["VOS3"][0], vc["VOS3"][2], lo))
    w("     for a revision X part (W144's F4), its VCAP in VOS3, VOS1 and VOS0 read on three parts against Table 112's revision V rows first")
    w("   S4: NRST held low from the TPS37's VPOR through tSD + tCTR at power-up, released %.1f to %.1f ms after VDD reaches %.1f V (scope, ten" % (
        tctr_min * 1e3, (F["tsd"] + tctr_max) * 1e3, F["vdd_min"]))
    w("     power cycles each supervisor)")
    w("   S5: the reset loop's hold (W145-F1): three first-article supervisors on board B in a %.0f C chamber at the rail's top, an image that" % air)
    w("     enters VOS0 at every boot: NRST's low time per cycle over 100 consecutive cycles, and VCAP's fall from VOS0 to the release level")
    w("     after an NRST reset: pass, every hold at least %.1f ms (or VCAP's fall at least %.2f ms, TI's condition); or TI's discharge figure" % (
        tctr_min * 1e3, t_full * 1e3))
    w("     for a fault shorter than %.0f %% of the programmed delay (correspondence drafted, UNSENT)" % (F["full_frac"] * 100))
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
         ("the open drain's peak current is under the recommended maximum", i_pk <= F["ireset_rec"]),
         ("the draft composes with and without W137's and W138's drafts, in either order, and reads DRAWN", v1_ == "DRAWN" and v2_ == "DRAWN" and v0_ == "FAIL" and same_order and not overlap and not clash),
         ("each of the seven mutations FAILS, the last the hold capacitor removed", all(v == "FAIL" for v in mres) and len(mres) == 7),
         ("the draft refuses a second application and the tree's own generator", all(refused)),
         ("each monitor stays inside its controller's failure domain", all(con)),
         ("the VOS0 and VOS1 entries and the reset loop read CONDITIONAL, none HOLDS, and H-1 claims no hardware bar",
          all(r[4].startswith("CONDITIONAL") for r in S[2:5]) and sk[4].startswith("CONDITIONAL") and not vos_like),
         ("T10's bounded state (99.6 C, 0.1570 A) is reproduced at 3.3 V by T10's own model before it is read at one supply corner",
          abs(tb3 - tj_b) < 0.05 and abs(ib3 - i_b) < 5e-5 and tbc > tb3),
         ("VOS1's step takes the largest printed 125 C row of Tables 119 to 121 (Table 120's 544 mA, W144's F7)", t_v1 == "Table 120" and abs(i_v1[t_v1] - 0.544) < 1e-9),
         ("TI's full-discharge condition is not shown for a reset loop (its fault floor under 5 % of the delay): S-k stays CONDITIONAL on S5",
          t_fall_min < t_full and "S5" in sk[4]),
         ("RM0433 Table 56's pin-reset row is PINRSTF and CPURSTF set, every other flag clear, and six other rows set PINRSTF",
          pat2 == want2 and len(pin_too) == 6),
         ("every TPS37 page quoted is the page its text sits on (form feeds counted)", all(F["tps_pages"][k] == int(k.split("p.")[1]) for k in F["tps_pages"])),
         ("every RM0433 sentence quoted from pages 329 to 332 sits on the page named (form feeds counted)", all(rm_pages.values())),
         ("the trip window rests on DS12110's revision V pages, and rev Y's Table 14 prints no core voltage per scale",
          F["revv_hdr"] >= 2 and F["revy_hdr"] and not F["revy_vos"]),
         ("the bounded state reaches 105 C at a local air between the case's air and the exhaust air (C2)", air < air105_c < PT10["air_exhaust"]),
         ("the firmware row applies after T10's draft only, once, and leaves the tree's contract unchanged", contract_ok),
         ("the fixed-delay route's least delay is printed and longer than the CTR1 hold's (W145-F1)", td38[0] >= tctr_min)]
    for lab, ok in P:
        w("   %-128s %s" % (lab, "yes" if ok else "NO"))
    w("")
    w("l9t5_hoe: done")
    txt = "\n".join(out) + "\n"
    sys.stdout.write(txt)
    return 0 if all(ok for _l, ok in P) else 1


if __name__ == "__main__":
    sys.exit(main())
