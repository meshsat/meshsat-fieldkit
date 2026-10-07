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
    "v2/vendor/st/st-rm0433-rev8.pdf": [["-layout", "-f", "215", "-l", "216"], ["-layout", "-f", "260", "-l", "260"],
                                        ["-layout", "-f", "262", "-l", "264"], ["-layout", "-f", "279", "-l", "280"],
                                        ["-layout", "-f", "307", "-l", "309"], ["-layout", "-f", "560", "-l", "560"],
                                        ["-layout", "-f", "1896", "-l", "1896"]],
    "v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf": [["-layout", "-f", "29", "-l", "29"], ["-layout", "-f", "208", "-l", "210"],
                                                       ["-layout", "-f", "212", "-l", "212"], ["-layout", "-f", "215", "-l", "215"],
                                                       ["-layout", "-f", "241", "-l", "241"], ["-layout", "-f", "248", "-l", "248"],
                                                       ["-layout", "-f", "344", "-l", "345"]],
    "v2/vendor/st/st-an4938-rev7.pdf": [["-layout", "-f", "10", "-l", "10"], ["-layout", "-f", "19", "-l", "19"]],
    "v2/vendor/ti/ti-tps37-snvsbj1e.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PDFT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PDFT)
RM = "v2/vendor/st/st-rm0433-rev8.pdf"
DS = "v2/vendor/st/st-stm32h743xi-datasheet-rev11.pdf"
AN = "v2/vendor/st/st-an4938-rev7.pdf"
TPS = "v2/vendor/ti/ti-tps37-snvsbj1e.pdf"
REC = "v2/docs/records/l9t5"
DOCS = {"draft": REC + "/apply_gen_sch_b_vcoremon.py", "guard": REC + "/apply_gen_sch_b_iocguard.py", "drafts": REC + "/l9t5_drafts.py",
        "t10out": REC + "/l9t5_t10.out", "t10py": REC + "/l9t5_t10.py", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "gennet": "v2/docs/records/l8p/gen_netlist.py", "ledger": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "cx46": "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md", "trace": "v2/docs/REQUIREMENTS-TRACE.md",
        "ioha": "v2/docs/ARCH-PCB-B-IOHA.md",
        "l4reg": REC + "/inputs/l4reg-L4REG-3b6eb8be.md", "l4regout": REC + "/inputs/l4reg-l4reg_compare-9fbda7a6.out",
        "regstage": REC + "/inputs/l4reg-apply_gen_sch_b_regstage-469594bb.py", "round6": REC + "/inputs/l4canmb-T10-ROUND6-0a94dd2c.md",
        "canmb": REC + "/inputs/l4canmb-apply_gen_sch_b_canmb-8fb8815a.py",
        "u23": "v2/docs/records/efuse/apply_gen_sch_b_u23ilm.py", "u24": "v2/docs/records/efuse/apply_gen_sch_b_u24ilm.py"}
TAGS = "ABC"
EN = chr(0x2013)       # the sheets' dash, written by its code point (no long dash in this file)
MINUS = chr(0x2212)    # ST's minus sign
MU = "[%s%s]" % (chr(0xB5), chr(0x3BC))
OHM = "[%s%s]" % (chr(0x3A9), chr(0x2126))
# ---- the session's choices (SESSION, under the owner's standing rule of 26 September 2026; section 7 gives each reason) ----
T_TEST_S = 3600.0      # W140-3: the monitor's self-test runs at every start and then once every T_TEST_S seconds per supervisor
T_VOSRDY_MS = 1.0      # W140-3: the self-test waits at most this long for VOSRDY after writing Scale 1, then restores Scale 3
T_WAIT_MS = 2.0        # W140-3: after VOSRDY, at most this long for the monitor's reset; a return is MONITOR FAILED
TEMPCO_K = 65.0        # T10's convention for a 25 ppm/K resistor (l9t5_t10.out 10j: "the divider at 0.1 % and 25 ppm/K over 65 K")
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
    its own VCAP, SENSE2 on its own rail, RESET1 through the series resistor to its own NRST (the controller's pin 14), the unused pins
    open, the bypass at its VDD; the divider's values read off the netlist give a trip band inside (VOS3's top, VOS1's bottom) and a
    release over VOS3's top"""
    why = []
    v3, v1 = F["vcore"]["VOS3"][2], F["vcore"]["VOS1"][0]
    for k, t in enumerate(TAGS):
        u, rt, rb, rs, cb = "U%d" % (810 + 10 * k), "R%d" % (810 + 10 * k), "R%d" % (811 + 10 * k), "R%d" % (812 + 10 * k), "C%d" % (810 + k)
        v33, vmon, mrst, nrst, vcap = "+3V3_IOC%s" % t, "IOC%s_VMON" % t, "IOC%s_MONRST" % t, "IOC%s_RST_n" % t, "IOC%s_VCAP" % t
        if not CHK.value(nl, u).startswith("TPS37 "):
            why.append("%s is %r, not a TPS37" % (u, CHK.value(nl, u)[:24]))
            continue
        why += CHK.rows(nl, [(u, "1", v33), (u, "2", vmon), (u, "3", v33), (u, "4", mrst), (u, "10", "GND"), (u, "11", "GND")])
        for p in ("5", "6", "7", "8", "9"):
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
        for ref in (u, rt, rb, rs, cb):
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
    pins = [RM, DS, AN, TPS] + [DOCS[k] for k in ("draft", "guard", "drafts", "t10out", "t10py", "gen_b", "gennet", "ledger", "cx46", "l4reg",
                                                  "l4regout", "regstage", "round6", "canmb", "u23", "u24")]
    for rel in pins:
        w("   %s %s" % (sha(rel), rel))
    for tp, h, _held in PDFT.inputs(ROOT, PDFTEXT):
        if h is None:
            refuse("%s is absent; %s" % (tp, PDFT.retake_command(REC)))
        w("   %s %s" % (h[:16], tp))
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
    w("   the VOS0 rows ST prints (Table 119, p.215, revision V, LDO ON, maxima 'Guaranteed by characterization results'; mA):")
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
    w("   READING: the voltage scale is a software choice made after every reset (PWR_D3CR's VOS bits, then ODEN for VOS0); no pin, strap or")
    w("   option byte selects or caps it. The one hardware means the documents print is the Bypass supply (an external regulator on VCAP; VOS0")
    w("   'available only with LDO regulator'), and that configuration is itself written by software once after every POR, with the LDO enabled")
    w("   by default until then; in Bypass the clock is still the firmware's ('must be consistent with the targeted maximum frequency').")
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
    w("   the least ThetaJA of any package is %s's %.1f C/W, %.1fx the need; the fitted LQFP100 reads %.1f C/W" % (best, F["ja"][best], F["ja"][best] / need_en, F["ja"]["LQFP100"]))
    w("   a heat path through the case top: ThetaJC %.1f C/W leaves %.2f C/W for the interface and a heat sink to the %.2f C air inside the" % (
        F["jc"]["LQFP100"], need_en - F["jc"]["LQFP100"], air))
    w("     sealed case; no heat sink or interface material is held in v2/vendor/ and none prints a figure for board B's pockets")
    w("   the air at which VOS0's enabled maximum holds 105 C on the printed %.1f C/W: %.1f C, against the case's %.2f C" % (th, 105.0 - th * vdd * F["vos0_en"][3], air))
    w("   the regulator's own theta (W138's TPS73733DCQRM3, 76.0 C/W PRINTED, record l4reg) moves the REGULATOR's junction; the controller's")
    w("     105 C current, (105 - air) / (theta x VDD) = %.4f A, does not depend on it: no regulator part acts on HO-E" % i105)
    w("   VERDICT H-3: FAILS on printed figures (no package and no printed heat path reaches %.2f C/W at this air)." % need_en)
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
    # timing
    rail = (3.2422, 3.3577)                  # W137's rail band (canmb section 6, the AP2112K); W138's TPS73733 band 3.2505 to 3.3495 lies inside it
    need(r6, r"Each rail 3\.2422 to 3\.3577 V", "W137's rail band")
    r_on = F["vol"] / F["vol_i"]
    rs = ohms(dm.SERIES)
    i_pk = rail[1] / (rs * (1 - tol(dm.SERIES)))
    r_low = rs * (1 + tol(dm.SERIES)) + r_on
    r_up_max = 1.0 / (1.0 / (10e3 * (1 + TOL_PLAIN)) + 1.0 / F["rpu"][2])
    c_rst = 100e-9 * (1 + C_RST_TOL)
    a = r_low / (r_low + r_up_max)
    tau = c_rst * (r_low * r_up_max / (r_low + r_up_max))
    t_fall = tau * math.log((1 - a) / (F["vil_k"] - a))
    t_resp = F["tcts"][1] + t_fall + F["vnf"]
    w("       the ending's timing, VCAP over the trip to the controller in reset:")
    w("         TPS37 sense delay tCTS %.0f us typ, %.0f us max at VIT 800 mV with CTS open, '20%% Overdrive from VIT' (7.6, p.9, PRINTED);" % (
        F["tcts"][0] * 1e6, F["tcts"][1] * 1e6))
    w("           VOS0's bottom %.2f V is %.1f %% over the trip's top, VOS1's %.2f V is %.1f %%: under 20 %%, so the printed maximum does NOT cover" % (
        vc["VOS0"][0], od0 * 100, vc["VOS1"][0], od1 * 100))
    w("           these entries (supplier task S2); 17 us is carried below as the figure S2 must confirm, never as a bound")
    w("         NRST pulled from the rail to VIL %.1f x VDD (Table 147, p.241: '%.1fVDD', NRST with the I/O rows) through %s and the open drain" % (F["vil_k"], F["vil_k"], dm.SERIES))
    w("           (VOL %.0f mV at 5 mA, p.7: at most %.0f Ohm, MODEL) against NRST's 10 k (+-5 %%, ASSUMPTION) and RPU %.0f to %.0f kOhm (Table 152, p.248)" % (
        F["vol"] * 1e3, r_on, F["rpu"][0] / 1e3, F["rpu"][2] / 1e3))
    w("           and the 100 nF reset capacitor (+-20 %%, ASSUMPTION): at most %.1f us (MODEL); the peak sink %.2f mA under the recommended %.0f mA" % (
        t_fall * 1e6, i_pk * 1e3, F["ireset_rec"] * 1e3))
    w("           (7.3, p.6) and the absolute %.0f mA (7.1, p.6)" % (F["ireset_abs"] * 1e3))
    w("         NRST's 'Input not filtered pulse' at least %.0f ns (Table 152, p.248, guaranteed by design)" % (F["vnf"] * 1e9))
    w("         t_resp = %.0f + %.1f + %.1f us = %.1f us (CONDITIONAL on S2's sense delay)" % (F["tcts"][1] * 1e6, t_fall * 1e6, F["vnf"] * 1e6, t_resp * 1e6))
    w("       power-up: '%s' (8.3.1.1, p.18), VPOR %.1f V; the H743 leaves its own BOR0 reset from %.2f to %.2f V rising (Table 116, p.212), so" % (
        F["uvlo_q"], F["vpor"], F["bor0"][0], F["bor0"][2]))
    w("         NRST is held until the TPS37's VDD reaches its %.1f V minimum; then '%s' (7.6 note 4, p.9), tSD %.0f ms (p.9);" % (F["vdd_min"], F["tsd_note"], F["tsd"] * 1e3))
    w("         Figure 7-3 (p.12) marks the first release at 'tSD + tCTRx' (DIAGRAM): no unmonitored start if the drawing holds (supplier task S4)")
    w("       the rails: the TPS37 runs from %.1f V (7.3, p.6) on a rail of %.4f to %.4f V; its IDD at most %.1f uA (p.7); the divider loads VCAP" % (
        F["vdd_min"], rail[0], rail[1], F["idd"] * 1e6))
    w("         with at most %.1f uA: ST prints no figure for a load on VCAP (ASSUMPTION, supplier task S3); no case row changes" % (
        vc["VOS0"][2] / ((ohms(dm.TOP) + ohms(dm.BOTTOM)) * (1 - 0.001 - 25e-6 * TEMPCO_K)) * 1e6))
    # 5e own faults
    w("   5e. ITS OWN FAULTS AND THEIR SELF-TEST (SESSION W140-3, the firmware rows for L4A-61, nothing applied): at every start and then once")
    w("       every %.0f s, at HCLK at most 144 MHz, the controller writes VOS = Scale 1, waits for VOSRDY at most %.1f ms (RM0433 p.309: '1: Ready," % (T_TEST_S, T_VOSRDY_MS))
    w("       voltage level at or above VOS selected level'), then at most %.1f ms for its own reset; a return is MONITOR FAILED (Scale 3" % T_WAIT_MS)
    w("       restored, reported in its state frame); after the reset, RCC_RSR's pin-reset flag with a marker kept over reset reads PASSED.")
    w("       Scale 1 (VCAP %.2f V and up) is over the trip's top by %.1f %%: the test drives the whole real path, VCAP to divider to SENSE1 to" % (vc["VOS1"][0], od1 * 100))
    w("       RESET1 to NRST. One supervisor tests at a time and only while the other two serve (IOHA row 3); the peers flag a supervisor")
    w("       whose test counter has not moved for 2 x %.0f s (FW-B22's state frame)." % T_TEST_S)
    faults = [("divider top open or bottom shorted", "SENSE1 at 0 V: never trips", "the next test (no reset)"),
              ("divider bottom open or top shorted", "SENSE1 at VCAP (1.0 V and up) over 0.808 V: held in reset", "at once (the controller silent, IOHA row 3)"),
              ("a divider value drifted", "the band moves", "the test if the trip passes VOS1's bottom; else at once (held in reset)"),
              ("RESET1 stuck released, or the series resistor open", "never resets", "the next test"),
              ("RESET1 stuck low, or MONRST shorted to ground", "held in reset", "at once"),
              ("the TPS37 unpowered (VDD open)", "output undefined under VPOR", "the next test, or at once if it rests low"),
              ("SENSE1 and SENSE2 exchanged or shorted (assembly)", "SENSE1 at the rail: held in reset", "at once"),
              ("a firmware that skips the test", "a latent monitor fault stays latent", "the peers, within 2 x %.0f s" % T_TEST_S)]
    for f_, eff, det in faults:
        w("         %-50s %-58s found: %s" % (f_, eff, det))
    w("       the residual: a monitor fault latent since the last test, then a firmware VOS0 entry: a double fault, its window at most %.0f s" % T_TEST_S)
    # 5f the thermal time
    p_ex = rail[1] * (F["vos0_en"][3] - i_b)
    dT = 105.0 - tj_b
    z_need = dT / p_ex
    p_ex1 = rail[1] * (F["vos1_en"][4] - i_b)
    z_need1 = (125.0 - tj_b) / p_ex1
    t_dead = (T_VOSRDY_MS + T_WAIT_MS) * 1e-3
    vol_si = p_ex * t_resp / (RHO_C_SI * dT) * 1e3                                    # mm3
    w("   5f. THE CONTROLLER'S THERMAL TIME: DS12110 Rev 11 prints steady resistances only (Table 222: ThetaJA, ThetaJB, ThetaJC; no transient")
    w("       impedance, no heat capacity, in the pages read); NOT PRINTED. What the ending needs instead (MODEL on PRINTED):")
    w("         from the bounded state (revision V, %.4f A, junction %.1f C at %.2f C air: T10 10c), VOS0's enabled maximum %.3f A at %.4f V" % (i_b, tj_b, air, F["vos0_en"][3], rail[1]))
    w("         adds at most %.3f W; to stay inside 105 C (%.1f K) the junction-to-ambient transient impedance at t_resp must be at most %.2f K/W" % (p_ex, dT, z_need))
    w("         the self-test with a dead monitor holds Scale 1 for at most %.1f ms (5e); VOS1's enabled maximum at 125 C, %.3f A (Table 119, a" % (t_dead * 1e3, F["vos1_en"][4]))
    w("         bound for any VOS1 clock and peripheral set, ASSUMPTION: monotonic), adds at most %.3f W; inside VOS1's 125 C (%.1f K): at most" % (p_ex1, 125.0 - tj_b))
    w("         %.2f K/W at %.1f ms" % (z_need1, t_dead * 1e3))
    w("         for scale only (ASSUMPTION, a handbook figure, credited nothing): %.2f J/(cm3 K) of silicon makes %.1f K in %.1f us at %.3f W need" % (
        RHO_C_SI, dT, t_resp * 1e6, p_ex))
    w("         %.4f mm3 of silicon heated adiabatically; ST prints no die size" % vol_si)
    w("   VERDICT H-2: NOT SUPPORTED ON PRINTED FIGURES AS A PROOF: the register's end condition ('no printed timing bounds the entry-to-reset")
    w("   interval, or the thermal time cannot be bounded on printed figures') is met, since neither the sense delay at VOS0's overdrive (S2)")
    w("   nor the controller's transient impedance (S1) is printed. It STANDS as the one drafted design that ends every VOS1 and VOS0 entry")
    w("   whatever the firmware does, on printed thresholds: PROVISIONAL under amendment 1, S1 and S2 supplier tasks with pass limits, not a")
    w("   closure. Not claimed: a hardware bar, or a printed interval.")
    w("")
    # ---------------------------------------------------------------- 6. acceptance
    w("6. THE ACCEPTANCE, STATE BY STATE ('the controller inside 105 C in every served state and every state the protection admits'; 105 C is")
    w("   VOS0's limit, 125 C VOS1 to VOS3's, Table 113; every figure MODEL on PRINTED unless marked)")
    tj_v3 = float(need(t10, r"V\s+VOS3 200 MHz, peripherals enabled\s+TJ ([\d.]+) C at ([\d.]+) A", "T10 section 4, VOS3 200 MHz enabled on rev V").group(1))
    S = [("S-a", "the bounded served state (FW-B20, FW-B21, rev V)", "105 C", "%.1f C (T10 10c)" % tj_b, "HOLDS" if tj_b <= 105.0 else "FAILS"),
         ("S-b", "VOS3 at its printed maximum (200 MHz, all peripherals)", "125 C", "%.1f C (T10 section 4)" % tj_v3, "HOLDS" if tj_v3 <= 125.0 else "FAILS"),
         ("S-c", "a VOS0 entry by any firmware", "105 C", "ended within t_resp %.1f us; needs ZthJA(t_resp) <= %.2f K/W" % (t_resp * 1e6, z_need),
          "CONDITIONAL (S1, S2)"),
         ("S-d", "a VOS1 entry by any firmware, the self-test included", "125 C", "ended within t_resp; needs ZthJA(t_resp) <= %.2f K/W" % z_need1,
          "CONDITIONAL (S1, S2)"),
         ("S-e", "the self-test with a dead monitor", "125 C", "at most %.1f ms (firmware); needs ZthJA(%.1f ms) <= %.2f K/W" % (t_dead * 1e3, t_dead * 1e3, z_need1),
          "CONDITIONAL (S1)"),
         ("S-f", "VOS2 with VCAP under the trip's top (%.2f to %.4f V)" % (vc["VOS2"][0], hi), "125 C", "not surely ended by the monitor",
          "OPEN (FW-B20's verification; L4REG-F7)"),
         ("S-g", "VOS3 above its printed 200 MHz", "125 C", "no printed current", "OPEN (FW-B20's verification; L4REG-F7)"),
         ("S-h", "power-up before the monitor is valid", "105 C", "NRST held under UVLO (p.18); release at tSD + tCTRx (DIAGRAM)", "CONDITIONAL (S4)"),
         ("S-i", "a latent monitor fault, then a firmware VOS0 entry", "105 C", "a double fault; window at most %.0f s" % T_TEST_S, "RESIDUAL (single-fault)"),
         ("S-j", "any current up to the limiter's %.4f A" % ios[1], "as above", "a VOS3 state is S-a or S-b; a VOS1 or VOS0 state is S-c or S-d",
          "no state outside S-a to S-i")]
    for row in S:
        w("   %-4s %-56s %-9s %-66s %s" % row)
    w("   HO-E's ACCEPTANCE: CONDITIONAL. The served state holds 105 C; every VOS0 state the protection admits is ended by the drafted monitor,")
    w("   and whether the junction stays inside 105 C during the ending rests on S1 and S2. Nothing is upgraded: cx46 CORRECTIONS NOT")
    w("   CLOSED and Layer 4's DESK gate NOT PASSED stand; this task closes no cx46 item before its own check (L4A-100).")
    w("")
    # ---------------------------------------------------------------- 7. the selection
    w("7. THE SELECTION")
    w("   SESSION W140-1: H-2 with the drafted VCORE monitor (apply_gen_sch_b_vcoremon.py) and the firmware rows of 5e, PROVISIONAL on S1 to S4.")
    w("     authority: SESSION, under the owner's standing rule of 26 September 2026 and his ruling of 21 September 2026")
    w("     authority_why: an engineering selection inside the drafted circuit; no requirement, protected class, case row, purchase or")
    w("       publication changes; one approach stands after the reading (H-1 drops out on the documents, H-3 fails on printed figures), so")
    w("       the ruling's second half (more than one option standing) fails; the residuals are measurable on a specimen (S1 to S4), so")
    w("       the selection accepts no risk a measurement cannot remove: amendment 1's supplier tasks, not an owner's risk acceptance")
    w("     ruled_by: W140 (Claude), MESHSAT-1357; ruled_on: 7 October 2026; reversed_by: none")
    w("     to reverse: drop apply_gen_sch_b_vcoremon.py; HO-E returns to REMAINING ENGINEERING with the owner item below")
    w("     end condition: S1 reads the controller's ZthJA at t_resp over %.2f K/W on board B; or S2 reads the sense delay at VOS0's overdrive" % z_need)
    w("       long enough that S1's reading fails at the longer interval; or two negative independent checks of this selection")
    w("   the owner item, PREPARED AND NOT RAISED (it would be raised only if the selection's end condition is met): 'The I/O supervisors'")
    w("     STM32H743 cannot hold its 105 C VOS0 limit in the case's air, and no hardware means bars VOS0. Either accept that the 105 C limit")
    w("     during a firmware fault rests on the controller's measured transient thermal response, or change the supervisor part to one whose")
    w("     printed rows hold at this air (a part change and its cost).'")
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
        w("   the mutations (each must FAIL the reading):")
        mres = []
        for i, (lab, sw) in enumerate(muts):
            q = D.mutate(net1, d, "hoem%d" % i, sw)
            v_, _wy = mon_check(CHK.read(open(q, "rb").read()), F, dm)
            mres.append(v_)
            w("     %-98s %s" % (lab + ":", v_))
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
            dom = {n for ref in ("U%d" % (810 + 10 * k), "R%d" % (810 + 10 * k), "R%d" % (811 + 10 * k), "R%d" % (812 + 10 * k), "C%d" % (810 + k))
                   for n in nl1["pins"].get(ref, {}).values()} - {"GND", "NC"}
            con.append(all(n.endswith("IOC%s" % t) or "IOC%s_" % t in n for n in dom))
        w("   CON-004's failure domains ('own regulator branch, reset supervisor, watchdog, crystal and SWD pads'): each monitor touches its own")
        w("   controller's nets and ground only: %s; no controller pin added (CON-017's count unchanged)" % ("yes" if all(con) else "NO"))
    w("")
    # ---------------------------------------------------------------- 9. findings
    w("9. FINDINGS FOR OTHER AUTHORS AND THE SUPPLIER'S TASKS (amendment 1: none is a gate of this desk round)")
    w("   W140-F1 (L4A-61, Layer 5): FW-B20 restated: VOS3 only; SYSCFG_PWRCR.ODEN never written; the one other VOS write is 5e's self-test")
    w("     (Scale 1 at HCLK at most 144 MHz, VOSRDY within %.1f ms, the reset within %.1f ms, MONITOR FAILED reported); a static check of the" % (T_VOSRDY_MS, T_WAIT_MS))
    w("     image for those writes; FW-B22's state frame carries the test counter, the peers flag one stalled for 2 x %.0f s" % T_TEST_S)
    w("   W140-F2 (Layer 6): the TPS37 option (channel 1 OV, 01, open drain active low, 2 % hysteresis) needs an orderable code and a stock")
    w("     line; TI: '%s'" % F["moq"])
    w("   W140-F3 (Layer 10): the WSON-10 land id is this draft's ASSUMPTION; the divider sits at the VCAP pins, its sense node short; the series")
    w("     resistor at the NRST end")
    w("   W140-F4 (L4REG-F7, W138): VOS1 and VOS0 entries are ended by the monitor; VOS2 under the trip and VOS3 above 200 MHz are not (S-f,")
    w("     S-g): they rest on FW-B20's verification")
    w("   W140-F5 (the register, L4A-100): the check reads this comparison and the draft; H-1's reading and H-3's arithmetic are on the pages")
    w("     quoted in sections 3 and 4")
    w("   S1: the controller's junction-to-ambient transient impedance on board B, three first-article supervisors, a junction step at")
    w("     %.3f W: pass at most %.2f K/W at %.1f us and %.2f K/W at %.1f ms (or ST's transient thermal data for the LQFP100 with board B's copper)" % (
        p_ex, z_need, t_resp * 1e6, z_need1, t_dead * 1e3))
    w("   S2: the monitor's entry-to-NRST interval at a VOS0 entry and at the self-test's Scale 1 entry, three supervisors, the chamber at")
    w("     %.0f C: pass at most %.1f us" % (air, t_resp * 1e6))
    w("   S3: VCAP in VOS3 with the divider fitted, under the controller's load steps: inside %.2f to %.2f V and under the trip's least %.4f V" % (
        vc["VOS3"][0], vc["VOS3"][2], lo))
    w("   S4: NRST held low from the TPS37's VPOR through tSD + tCTR at power-up (scope, ten power cycles each supervisor)")
    w("")
    # ---------------------------------------------------------------- 10. predicates
    w("10. THE PREDICATES")
    P = [("every quoted sentence of H-1 is in its pinned text, with its page", True),
         ("no option-byte field of FLASH_OPTSR_PRG selects a voltage scale or the supply configuration", not vos_like),
         ("T10's 0.1936 A and 112.7 C are reproduced from T10's own air and theta", abs(i105 - i105_t10) < 5e-5 and abs(tj_at(i_trip) - tj_t10) < 0.05),
         ("no printed VOS0 row has an operating point at or under 105 C at the case's air", ops["dis"][0] > 0 and ops["en"][0] > 0),
         ("no package in Table 222 reaches the ThetaJA H-3 needs", min(F["ja"].values()) > need_en),
         ("the selected divider's band lies inside VOS3's top and VOS1's bottom, its release over VOS3's top", lo > vc["VOS3"][2] and hi < vc["VOS1"][0] and rel > vc["VOS3"][2]),
         ("the printed 20 % overdrive does not cover VOS0's bottom (S2 is owed, not assumed)", od0 < 0.20),
         ("the open drain's peak current is under the recommended maximum", i_pk <= F["ireset_rec"]),
         ("the draft composes with and without W137's and W138's drafts, in either order, and reads DRAWN", v1_ == "DRAWN" and v2_ == "DRAWN" and v0_ == "FAIL" and same_order and not overlap and not clash),
         ("each of the six mutations FAILS", all(v == "FAIL" for v in mres) and len(mres) == 6),
         ("the draft refuses a second application and the tree's own generator", all(refused)),
         ("each monitor stays inside its controller's failure domain", all(con)),
         ("the VOS0 and VOS1 entries read CONDITIONAL, none HOLDS, and H-1 claims no hardware bar", all(r[4].startswith("CONDITIONAL") for r in S[2:5]) and not vos_like)]
    for lab, ok in P:
        w("   %-118s %s" % (lab, "yes" if ok else "NO"))
    w("")
    w("l9t5_hoe: done")
    txt = "\n".join(out) + "\n"
    sys.stdout.write(txt)
    return 0 if all(ok for _l, ok in P) else 1


if __name__ == "__main__":
    sys.exit(main())
