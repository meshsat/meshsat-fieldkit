#!/usr/bin/env python3
"""l4canen.py: record l4canen, round 9 of record l9t5's task T10 (Layer 4 task L4A-54's correction on W139's quorum analysis, row (b)
of the AI-scope register; W143, MESHSAT-1357, 7 October 2026). PROTOTYPE DESIGN: nothing in this kit has been built, bought, powered
or measured; no figure printed here is a measurement.

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the makers' texts as the records' helper returns them);
  2. why: W139's finding W139-F2 (a supervisor latched off by W138's TPS2553-1 has nothing driving its EN) and the node W138 named;
  3. the composition on board B in L4-E9's change-list order with W137's canmb and W138's regstage in BOTH orders, with and without
     record l9t5's apply_gen_sch_b_canen.py after them: every step, the netlists equal in both orders, CON-004, canmb read by pin on
     the limiter's state, the limiter and regulator rows;
  4. the EN route read by pin, the mutations that must FAIL (an EN route a single peer can hold, among them) and the draft's refusals;
  5. the pin plan recounted (CON-017's convention) and read against DS12110 Table 9;
  6. the levels on the makers' printed rows (MODEL from PRINTED), the dark and faulty cases;
  7. the timing: the restart decision, the delay, the restart, the latched supervisor's RECOVERY INTERVAL, the rate and its energy;
  8. the route's own faults with their detection, and the route's in-service test riding on the restated self-test;
  9. FW-B21's stop at the loss count read against the corrected drafts, and the contract draft's text (DAR = 1 with ES0392's
     workaround quoted with its page, the restated self-test, the restart rule), composed on a scratch copy of the page;
 10. the SESSION decisions, the findings, what closes once independently checked;
 11. the predicates test_l4canen.py holds.
Run from the repository root:  python3 v2/docs/records/l4canen/l4canen.py  (about 20 s; it composes board B in temporary directories,
never the tree). Output: l4canen.out, regenerated with _bin/regen_out.py. Labels: PRINTED (a maker's limit), TYPICAL, DRAFTED (a
contract row or a drafted figure, not applied), MODEL, ASSUMPTION, SESSION."""
import ast
import hashlib
import importlib.util
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
L9 = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
sys.path.insert(0, L9)
import l9t5_canmb as M  # noqa: E402  (canmb's checks, CON-017's count and DS12110's Table 9 reader; its figures() is NOT called here)
D, CHK = M.D, M.CHK

# W34's convention (Q-41 item 1): every maker's text this record reads, each with its options; the held-back sheets' texts are held back
# with them (fetch_held_back.py beside this file). Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py
# v2/docs/records/l4canen
PDFTEXT = {
    "v2/vendor/power/aos-ao3400a-n-mosfet.pdf": [["-layout"]],
    "v2/vendor/st/st-es0392-rev15.pdf": [["-layout", "-f", "48", "-l", "48"]],
    "v2/vendor/st/st-rm0433-rev8.pdf": [["-layout", "-f", "533", "-l", "533"]],
    "v2/vendor/st/st-stm32h743xi-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf": [["-layout"]],
    "v2/vendor/ti/held/ti-tps737-sbvs067w.pdf": [["-layout"]],
    "v2/vendor/ti/ti-sn74lvc1g08.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PDFT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PDFT)
REC = "v2/docs/records/l4canen"
SHEETS = {"fet": "v2/vendor/power/aos-ao3400a-n-mosfet.pdf", "es": "v2/vendor/st/st-es0392-rev15.pdf",
          "rm": "v2/vendor/st/st-rm0433-rev8.pdf", "h743": "v2/vendor/st/st-stm32h743xi-datasheet.pdf",
          "lim": "v2/vendor/ti/held/ti-tps2553-slvs841f.pdf", "ldo": "v2/vendor/ti/held/ti-tps737-sbvs067w.pdf",
          "g08": "v2/vendor/ti/ti-sn74lvc1g08.pdf"}
L9R = "v2/docs/records/l9t5"
DOCS = {"canen": L9R + "/apply_gen_sch_b_canen.py", "canmb": L9R + "/apply_gen_sch_b_canmb.py",
        "regstage": REC + "/inputs/l4reg-apply_gen_sch_b_regstage-469594bb.py", "sources": REC + "/inputs/SOURCES.txt",
        "guard": L9R + "/apply_gen_sch_b_iocguard.py", "iocset": L9R + "/apply_gen_sch_a_iocset.py", "iocpre": L9R + "/apply_gen_sch_b_iocpre.py",
        "canmb_py": L9R + "/l9t5_canmb.py", "canmb_out": L9R + "/l9t5_canmb.out", "canq_py": L9R + "/l9t5_canq.py",
        "canq_out": L9R + "/l9t5_canq.out", "canq_page": L9R + "/T10-CANQ.md", "contract": "v2/docs/HW-FW-CONTRACT.md",
        "contract_t10": L9R + "/apply_hw_fw_contract_t10.py", "contract_canq": L9R + "/apply_hw_fw_contract_canq.py",
        "l4reg_out": L9R + "/inputs/l4reg-l4reg_compare-9fbda7a6.out", "drafts": L9R + "/l9t5_drafts.py",
        "gen_b": "v2/ecad/tools/gen_sch_b.py", "gennet": "v2/docs/records/l8p/gen_netlist.py", "trace": "v2/docs/REQUIREMENTS-TRACE.md"}
EN = chr(0x2013)       # the sheets' minus sign, written by its code point (no long dash in this file)
MU = "[%s%s]" % (chr(0xB5), chr(0x3BC))
TAGS = "ABC"
# DRAFTED by this round (the restart rule, apply_hw_fw_contract_canq.py) and SESSION (W143-D5): each printed with its reason in section 7
T_DEC = 2.0            # s: no edge on either of the target's TXDs and no state frame of it on either fabric for this long, at a peer
T_HOLD = 2.0           # s: a peer's restart vote is held this long, then released
T_RATE = 10.0          # s: at most one restart vote per target in this time (W139's route)
EN_LOW_MIN = 0.5       # s: the least time the route must hold the limiter's EN low (two orders over its printed turn-off time)
PULSE = (68e-3, 72e-3)     # s, a test pulse in the asserting peer's window (P1, P2 and V on the restart route)
READ = (66e-3, 74e-3)      # s, the target reads its restart gate's output over this span of its own window
# ASSUMPTION (a Layer 10 and Layer 6 part-selection bound, finding W143-F6): the RC's 4.7 uF keeps at least this much at 3.3 V over
# -20 to 85 C (21 % of nominal); its +10 % tolerance is the X7R class's, no part number being chosen yet
C_EFF_MIN, C_TOL = 1.0e-6, 0.10
C_RB_PF = 46.0         # ASSUMPTION, a Layer 10 bound: the read-back line, the reader's CIO included (as canmb's observation lines)
VGS_ON = 2.5           # V: the AO3400A's RDS(on) row is printed at this gate drive


def refuse(msg):
    sys.stderr.write("l4canen: REFUSED: %s\n" % msg)
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


def es_page48():
    return PDFT.pdf_text(ROOT, SHEETS["es"], ["-layout", "-f", "48", "-l", "48"], PDFTEXT, REC)


def rm_page533():
    return PDFT.pdf_text(ROOT, SHEETS["rm"], ["-layout", "-f", "533", "-l", "533"], PDFTEXT, REC)


def load(rel, name):
    sp = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def literal(src, name):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    refuse("%s is not a module-level literal" % name)


def page_after(t, pos):
    """the printed page number of the page whose footer follows pos in TI's layout text (even pages print the number first, odd
    pages last)"""
    for m in re.finditer(r"^(\d+)\s+Submit Document(?:ation)? Feedback|Submit Document(?:ation)? Feedback\s+(\d+)\s*$", t[pos:], re.M):
        return int(m.group(1) or m.group(2))
    refuse("no page footer after offset %d" % pos)


def column(t, m, value_group):
    """MIN, TYP or MAX: the header word of the table above a matched row nearest to where the matched number stands"""
    line_start = t.rfind("\n", 0, m.start(value_group)) + 1
    col = m.start(value_group) - line_start
    for hm in reversed(list(re.finditer(r"^.*\bMIN\s+TYP\s+MAX\b.*$", t[:m.start()], re.M))):
        hdr = hm.group(0)
        cols = [(abs(mm.start() + len(mm.group(0)) / 2.0 - col), mm.group(0)) for mm in re.finditer(r"MIN|TYP|MAX", hdr)]
        return min(cols)[1]
    refuse("no MIN TYP MAX header above the row")


# ------------------------------------------------------------------------------------------------ the makers' printed rows
def figures():
    F = {}
    t = pdf("lim")
    F["lim_rev"] = need(t, r"(SLVS841F) %s NOVEMBER 2008 %s REVISED AUGUST 2016" % (EN, EN), "SLVS841F's revision").group(1)
    m = need(t, r"VIH\s+High-level input voltage on EN or EN\s+([\d.]+)", "TPS2553 EN VIH")
    F["en_vih"], F["en_vih_p"] = float(m.group(1)), page_after(t, m.end())
    F["en_vil"] = float(need(t, r"VIL\s+Low-level input voltage on EN or EN\s+([\d.]+)", "TPS2553 EN VIL").group(1))
    F["en_vmax"] = float(need(t, r"VEN\s+Enable voltage\s+TPS2553/53-1\s+([\d.]+)\s+([\d.]+)\s+V", "TPS2553 VEN").group(2))
    F["vin_max"] = float(need(t, r"VIN\s+Input voltage, IN\s+([\d.]+)\s+([\d.]+)\s+V", "TPS2553 VIN").group(2))
    m = need(t, r"IEN\s+Input current\s+VEN = 0 V or 6\.5 V, VEN = 0 V or 6\.5 V\s+%s([\d.]+)\s+([\d.]+)\s+%sA" % (EN, MU), "TPS2553 IEN")
    F["ien"], F["tab75_p"] = float(m.group(2)) * 1e-6, page_after(t, m.end())
    F["ton"] = float(need(t, r"ton\s+Turnon time\s+CL = 1 %sF, RL = 100 \S, \(see Figure 20\)\s+([\d.]+)\s+ms" % MU, "TPS2553 ton").group(1)) * 1e-3
    F["toff"] = float(need(t, r"toff\s+Turnoff time\s+CL = 1 %sF, RL = 100 \S, \(see Figure 20\)\s+([\d.]+)\s+ms" % MU, "TPS2553 toff").group(1)) * 1e-3
    F["deglitch"] = tuple(float(x) * 1e-3 for x in need(t, r"FAULT assertion or de-assertion due to overcurrent condition\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+ms",
                                                        "TPS2553 FAULT deglitch").groups())
    m = need(t, r"(The device remains\s+off until power is cycled or the device enable is toggled\.)", "SLVS841F 9.3.1's latch")
    F["latch"], F["latch_p"] = " ".join(m.group(1).split()), page_after(t, m.end())
    need(t, r"EN\s+%s\s+%s\s+3\s+4\s+I\s+Enable input, logic high turns on power switch" % (chr(0x2014), chr(0x2014)), "TPS2553's EN pin (active high)")
    t = pdf("ldo")
    F["ldo_rev"] = need(t, r"(SBVS067W) %s JANUARY 2006 %s REVISED AUGUST 2025" % (EN, EN), "SBVS067W's revision").group(1)
    F["ldo_acc"] = float(need(t, r"10mA \S IOUT \S 1A, new\s+%s([\d.]+)\s+\S0\.5\s+([\d.]+)" % EN, "TPS737 accuracy, new silicon").group(2)) / 100.0
    m = need(t, r"tSTR\s+Startup time\s+VOUT = 3V, RL = 30\S, COUT = 1%sF, new silicon\s+(\d+)\s+%ss" % (MU, MU), "TPS737 tSTR, new silicon")
    F["tstr"], F["tstr_col"] = float(m.group(1)) * 1e-6, column(t, m, 1)
    t = pdf("fet")
    F["fet_rev"] = need(t, r"(Rev 3\.1: July 2023)", "the AO3400A sheet's revision").group(1)
    need(t, r"Electrical Characteristics \(TJ=25\S+C unless otherwise noted\)", "AO3400A's table conditions (TJ 25 C)")
    F["vth"] = tuple(float(x) for x in need(t, r"VGS\(th\)\s+Gate Threshold Voltage\s+VDS=VGS ID=250mA\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", "AO3400A VGS(th)").groups())
    F["rdson25"] = float(need(t, r"VGS=2\.5V, ID=3A\s+([\d.]+)\s+([\d.]+)\s+mW", "AO3400A RDS(on) at VGS 2.5 V").group(2)) * 1e-3
    m = need(t, r"VDS=30V, VGS=0V\s+(\d+)\s*\n\s*IDSS\s+Zero Gate Voltage Drain Current\s+mA\s*\n\s+TJ=55\S+C\s+(\d+)", "AO3400A IDSS")
    F["idss25"], F["idss55"] = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6     # the sheet's SymbolMT 'm' is mu (section 6)
    F["igss"] = float(need(t, r"IGSS\s+Gate-Body leakage current\s+VDS=0V, VGS= \S12V\s+(\d+)\s+nA", "AO3400A IGSS").group(1)) * 1e-9
    F["vgs_max"] = float(need(t, r"Gate-Source Voltage\s+VGS\s+\S(\d+)\s+V", "AO3400A VGS maximum").group(1))
    g = pdf("g08")
    F["g_rev"] = need(g, r"(SCES217AA) %s APRIL 1999 %s REVISED AUGUST 2026" % (EN, EN), "SCES217AA's revision").group(1)
    F["g_vih"] = float(need(g, r"VIH\s+High-level input voltage\s+V\s*\n\s+VCC = 3V to 3\.6V\s+([\d.]+)\s*\n", "SN74LVC1G08 VIH").group(1))
    F["g_vil"] = float(need(g, r"VIL\s+Low-level input voltage\s+V\s*\n\s+VCC = 3V to 3\.6V\s+([\d.]+)\s*\n", "SN74LVC1G08 VIL").group(1))
    F["g_vimax"] = float(need(g, r"VI\s+Input voltage\s+0\s+([\d.]+)\s+V", "SN74LVC1G08 VI").group(1))
    m = need(g, r"IOH = %s100%sA\s+1\.65V to 5\.5V\s+VCC %s ([\d.]+)\s+VCC %s ([\d.]+)" % (EN, MU, EN, EN), "SN74LVC1G08 VOH at -100 uA")
    F["g_voh_drop"] = float(m.group(2))                                 # -40 to 125 C
    F["g_vol100"] = float(need(g, r"IOL = 100%sA\s+1\.65V to 5\.5V\s+([\d.]+)" % MU, "SN74LVC1G08 VOL at 100 uA").group(1))
    F["g_vol16"] = float(need(g, r"IOL = 16mA\s+([\d.]+)\s+([\d.]+)\s*\n\s+3V", "SN74LVC1G08 VOL at 16 mA, VCC 3 V").group(2))
    F["g_ii"] = float(need(g, r"II\s+VI = 5\.5V or GND\s+0 to 5\.5V\s+\S(\d+)\s+\S\d+\s+%sA" % MU, "SN74LVC1G08 II").group(1)) * 1e-6
    F["g_ioff"] = float(need(g, r"Ioff\s+VI or VO = 5\.5V\s+0\s+\S(\d+)\s+\S\d+\s+%sA" % MU, "SN74LVC1G08 Ioff").group(1)) * 1e-6
    F["g_icc"] = float(need(g, r"ICC\s+VI = 5\.5V or GND,\s+IO = 0\s+1\.65V to 5\.5V\s+(\d+)\s+(\d+)\s+%sA" % MU, "SN74LVC1G08 ICC").group(2)) * 1e-6
    F["g_dicc"] = float(need(g, r"One input at VCC %s 0\.6V,\s*\n\s*%sICC\s+3V to 5\.5V\s+(\d+)\s+(\d+)\s+%sA" % (EN, chr(0x394), MU), "SN74LVC1G08 delta ICC").group(2)) * 1e-6
    h = pdf("h743")
    b157 = M.block(h, "Table 157. I/O static characteristics", "DS12110 Table 157 (rev V)", 7000)
    vil, vih = re.findall(r"(\d\.\d)VDD\(1\)", b157)[:2]
    F["vil_k"], F["vih_k"] = float(vil), float(vih)
    F["ilkg"] = float(need(b157, r"0< VIN %s Max\(VDDXXX\)\(9\)\s+-\s+-\s+\+/-(\d+)" % chr(0x2264), "FT leakage").group(1)) * 1e-9
    F["cio"] = float(need(b157, r"CIO\s+I/O pin capacitance\s+-\s+-\s+(\d+)\s+-\s+pF", "CIO").group(1)) * 1e-12
    b158 = M.block(h, "Table 158. Output voltage characteristics for all I/Os except PC13, PC14, PC15 and PI8(1)", "DS12110 Table 158", 1500)
    F["voh_drop"] = float(need(b158, r"VOH\s+Output high level voltage\s+IIO=-8 mA\s+VDD%s([\d.]+)" % chr(0x2212), "VOH at -8 mA").group(1))
    F["iio"] = 8e-3
    r533 = rm_page533()
    F["debug_pins"] = re.findall(r"(P[AB]\d+): N?J", r533)
    e = es_page48()
    m = need(e, r"^(2\.24\.5)\s+DAR mode transmission failure due to lost arbitration\s*\n.*?Workaround\s*\n\s+(Upon failure,.*?restart the transmission\.)",
             "ES0392 2.24.5's workaround", re.M | re.S)
    F["es_item"], F["es_work"] = m.group(1), " ".join(m.group(2).split())
    m = need(e, r"ES0392 - Rev (\d+)\s+page (\d+)/(\d+)", "ES0392's page footer")
    F["es_rev"], F["es_page"] = m.group(1), "page %s/%s" % (m.group(2), m.group(3))
    # the records this round reads (its own tree)
    o = text(DOCS["canmb_out"])
    m = need(o, r"at the rail's declared 0\.25 A: ([\d.]+) V to ([\d.]+) V", "canmb's rail band (AP2112K-3.3)")
    F["rail_ap"] = (float(m.group(1)), float(m.group(2)))
    F["i_ctrl"] = float(need(o, r"all at once: at most ([\d.]+) A", "canmb's controller rail figure").group(1))
    F["cycle"] = float(need(o, r"one cycle is 12 windows x 100 ms = ([\d.]+) s;", "the restated cycle").group(1))
    F["t_det"] = float(need(o, r"DETECTED WITHIN ([\d.]+) s of its onset", "the restated interval").group(1))
    F["align"] = float(need(o, r"each margin less the window clocks' alignment ([\d.]+) ms, DRAFTED", "the window alignment").group(1)) * 1e-3
    F["phases_ok"] = need(o, r"restated schedule, precondition as worded:\s+every phase of every transceiver \d times: (yes|NO)", "the phases run").group(1)
    s = text(DOCS["iocset"])
    m = need(s, r"\(R602 14\.0k, ([\d.]+) to ([\d.]+) V\)", "+5V_IOC's band at board A (iocset, T10 round 5)")
    F["v5_a"] = (float(m.group(1)), float(m.group(2)))
    F["v5_budget"] = float(need(text(DOCS["iocpre"]), r"budget=([\d.]+), share=0\.015, converted=False", "+5V_IOC's drop budget").group(1))
    lo = text(DOCS["l4reg_out"])
    F["ios"] = tuple(float(x) for x in need(lo, r"inside the band \(([\d.]+) to ([\d.]+) A\)", "W138's limiter band").groups())
    F["e_latch"] = float(need(lo, r"at most ([\d.]+) mJ \(MODEL\)", "W138's latch energy").group(1)) * 1e-3
    q = text(DOCS["canq_py"])
    F["Q"] = literal(q, "CFG")
    qo = text(DOCS["canq_out"])
    F["rc2"] = float(need(qo, r"a dark or reset controller: boot [\d.]+ ms \(ASSUMPTION\) \+ MON 2 windows \+ its slot: ([\d.]+) ms", "canq's rejoin bound").group(1)) * 1e-3
    F["f2"] = need(qo, r"^\s+F2\s+-\s+(quorum lost)\s+(quorum lost)\s", "canq's row F2").groups()
    F["m1c"] = need(qo, r"^\s+M1c\s+-\s+(a node out and contained)\s+(a node out and contained)\s+(\d)\s", "canq's row M1c").groups()
    F["acc_a9"] = need(qo, r"A9 the contract draft carries this record's figures.*?\s(yes|NO)$", "canq's A9").group(1)
    F["ft_unpowered"] = need(text(DOCS["gen_b"]), r"(FT_xxx: Min\(VDD, \.\.\.\) \+ 4\.0 V, so 4\.0 V unpowered)", "the FT pins' unpowered maximum").group(1)
    return F


# ------------------------------------------------------------------------------------------------ the composition
def order(first, with_en=True, with_mb=True, with_reg=True):
    """board B's drafts in L4-E9's change-list order with canmb and regstage after iocguard in the order named, canen after both, the
    efuse record's R-236 and R-237 after those, Layer 6's three last"""
    seq = D.seq_of("b", "slot")
    at = seq.index(D.MINE["b"]) + 1
    mid = [os.path.join(L9, f) for f in ("apply_gen_sch_b_iocpre.py", "apply_gen_sch_b_canshdn.py", "apply_gen_sch_b_iocset.py",
                                         "apply_gen_sch_b_iocguard.py")]
    mb, reg = os.path.join(ROOT, DOCS["canmb"]), os.path.join(ROOT, DOCS["regstage"])
    pair = [mb, reg] if first == "mb" else [reg, mb]
    mid += [x for x in pair if (x != mb or with_mb) and (x != reg or with_reg)]
    if with_en:
        mid.append(os.path.join(ROOT, DOCS["canen"]))
    mid += [os.path.join(ROOT, M.DOCS["u23"]), os.path.join(ROOT, M.DOCS["u24"])]
    return seq[:at] + mid + seq[at:]


def build(d, tag, **kw):
    seq = order(**kw)
    p, res, ok = D.compose("b", seq, d, tag)
    if not ok:
        return seq, res, False, p, None, None
    rc, net, _t = D.netlist("b", p, d, tag)
    if rc:
        return seq, res, False, p, None, None
    return seq, res, True, p, net, CHK.read(open(net, "rb").read())


def mcu(k):
    return "U%d" % (41 + 10 * k)


def con004(nl):
    """CON-004 read as record l9t5's canmb reads it, with the regulator either the AP2112K (pin 5) or W138's TPS73733 (pin 2): three
    supply branches, each controller's rail sourced by its own regulator alone, two fabrics with their termination and break links;
    the restart gates' 100 Ohm feeds are loads on a rail, never a source of another"""
    why = []
    for k, t in enumerate(TAGS):
        v33 = "+3V3_IOC%s" % t
        outs = [m for m in CHK.members(nl, v33) if (CHK.value(nl, m.split(".")[0]).startswith("AP2112K") and m.endswith(".5"))
                or (CHK.value(nl, m.split(".")[0]).startswith("TPS73733") and m.endswith(".2"))]
        if outs != ["U%d.%s" % (40 + 10 * k, "2" if CHK.value(nl, "U%d" % (40 + 10 * k)).startswith("TPS73733") else "5")]:
            why.append("%s's sources are %s, not its own regulator U%d alone" % (v33, outs, 40 + 10 * k))
        for m in CHK.members(nl, v33):
            ref = m.split(".")[0]
            if ref.startswith("R") and any(n.startswith("+3V3_IOC") and n != v33 for n in nl["pins"].get(ref, {}).values()):
                why.append("%s joins %s to another controller's rail" % (ref, v33))
    rest = M.con004(nl)[1]
    why += [w_ for w_ in rest if "sources are" not in w_]
    return ("HOLDS" if not why else "FAIL"), why


def mb_check(nl, MB):
    """canmb read by pin as record l9t5 reads it, on the limiter's state: round 6's rail trips (U46, U56, U66) are W138's to remove,
    so their rows are replaced by the limiter's (U45, U55, U65 a TPS2553-1 with IN on +5V_IOC, EN on IOC{t}_LIM_EN, OUT on
    IOC{t}_LDO_IN) and the regulator's (U40, U50, U60 a TPS73733 from IOC{t}_LDO_IN)"""
    v, why = M.mb_check(nl, MB)
    why = [w_ for w_ in why if not re.match(r"U[456][56]\.", w_)]
    for k, t in enumerate(TAGS):
        u = 40 + 10 * k
        why += CHK.rows(nl, [("U%d" % (u + 5), "1", "+5V_IOC"), ("U%d" % (u + 5), "3", "IOC%s_LIM_EN" % t), ("U%d" % (u + 5), "6", "IOC%s_LDO_IN" % t),
                             ("U%d" % u, "1", "IOC%s_LDO_IN" % t), ("U%d" % u, "2", "+3V3_IOC%s" % t)])
        if not CHK.value(nl, "U%d" % (u + 5)).startswith("TPS2553-1") or not CHK.value(nl, "U%d" % u).startswith("TPS73733"):
            why.append("U%d or U%d is not W138's limiter and regulator" % (u + 5, u))
    return ("DRAWN" if not why else "FAIL"), why


def holders(nl, k):
    """who can pull controller k's limiter EN low, traced on the netlist (never from the names): from the FET's gate through series
    resistors to a gate's output, then to the controllers whose pins reach that gate's two inputs, or straight to a controller's pin.
    ('AND', {controllers on input A}, {controllers on input B}) or ('DIRECT', {controllers}) or ('NONE', set())"""
    en = "IOC%s_LIM_EN" % TAGS[k]
    fets = []
    for m in CHK.members(nl, en):
        r = m.split(".")[0]
        if r.startswith("R"):
            other = [n for p, n in nl["pins"].get(r, {}).items() if n != en]
            for n in other:
                fets += [x.split(".")[0] for x in CHK.members(nl, n) if x.endswith(".3") and CHK.value(nl, x.split(".")[0]).startswith("AO3400A")]
    if len(fets) != 1:
        return ("NONE", set())
    g = CHK.pin(nl, fets[0], "1")

    def mcus(net):
        return {TAGS[(int(x.split(".")[0][1:]) - 41) // 10] for x in CHK.members(nl, net)
                if re.fullmatch(r"U[456]1\.\d+", x) and CHK.value(nl, x.split(".")[0]).startswith("STM32H743")}
    direct, gates = set(), []
    seen, frontier = {g}, [g]
    while frontier:                                    # through series resistors, stopping at a gate's output (a driven net)
        n = frontier.pop()
        outs = [x.split(".")[0] for x in CHK.members(nl, n) if x.endswith(".4") and CHK.value(nl, x.split(".")[0]).startswith("SN74LVC1G08")]
        if outs:
            gates += outs
            continue
        direct |= mcus(n)
        for x in CHK.members(nl, n):
            ref = x.split(".")[0]
            if ref.startswith("R"):
                for n2 in nl["pins"].get(ref, {}).values():
                    if n2 not in seen and n2 != "GND" and not n2.startswith("+"):
                        seen.add(n2)
                        frontier.append(n2)
    if direct:
        return ("DIRECT", direct)
    if len(set(gates)) != 1:
        return ("NONE", set())
    gt = gates[0]
    return ("AND", mcus(CHK.pin(nl, gt, "1")), mcus(CHK.pin(nl, gt, "2")))


def en_check(nl, E):
    """the draft read by pin: for each controller X, its restart gate on the NEXT controller's rail through the drafted 100 Ohm with its
    100 nF, its two inputs the two OTHER controllers' planned restart pins, each held low by 10 kOhm; its output through 100 kOhm into
    4.7 uF with 1 MOhm to ground on an AO3400A's gate, whose drain reaches X's limiter EN through 470 Ohm; the EN pulled up by 10 kOhm
    to +5V_IOC; X's planned read-back pin on the gate's output through 10 kOhm; nothing else on any of these nets; and the trace from
    the EN back to the controllers finds a 2-of-2 of the two peers, never one controller"""
    why = []
    vote_pin = {d: p for p, (_port, use, d) in E.RST_PINS.items() if use == "vote"}
    rb_pin = [p for p, (_port, use, _d) in E.RST_PINS.items() if use == "readback"][0]
    for k, t in enumerate(TAGS):
        pa, pb = TAGS[(k + 1) % 3], TAGS[(k + 2) % 3]
        gate, fet, cdec, crc = "U%d" % (586 + k), "Q%d" % (586 + k), "C%d" % (947 + 10 * k), "C%d" % (948 + 10 * k)
        rsup, rva, rvb, rrc, rpd = ("R%d" % (615 + 20 * k + n) for n in range(5))
        rdr, rrb, rpu, lim = "R%d" % (660 + 2 * k), "R%d" % (661 + 2 * k), "R%d" % (602 + 20 * k), "U%d" % (45 + 10 * k)
        env, y, g, dr, en, rb = ("IOC%s_%s" % (t, n) for n in ("ENVCC", "RSTY", "RSTG", "RSTD", "LIM_EN", "RSTRB"))

        def exact(net, want):
            if sorted(CHK.members(nl, net)) != sorted(want):
                why.append("%s reaches %s, not %s" % (net, CHK.members(nl, net), sorted(want)))
        exact(env, ["%s.2" % rsup, "%s.5" % gate, "%s.1" % cdec])
        why += CHK.rows(nl, [(rsup, "1", "+3V3_IOC%s" % pa), (gate, "3", "GND"), (gate, "4", y), (cdec, "2", "GND"),
                             (rrc, "1", y), (rrc, "2", g), (crc, "2", "GND"), (rpd, "2", "GND"), (fet, "1", g), (fet, "2", "GND"), (fet, "3", dr),
                             (rdr, "1", dr), (rdr, "2", en), (rpu, "1", "+5V_IOC"), (rpu, "2", en), (lim, "3", en), (rrb, "1", y), (rrb, "2", rb)])
        for ref, want in ((rsup, E.R_SUP), (rrc, E.R_RC), (crc, E.C_RC), (rpd, E.R_PD), (rdr, E.R_DRAIN), (rrb, E.R_RB), (rpu, E.R_ENPU),
                          (rva, E.R_VPD), (rvb, E.R_VPD)):
            if CHK.value(nl, ref) != want:
                why.append("%s is %r, not %r" % (ref, CHK.value(nl, ref), want))
        if not CHK.value(nl, gate).startswith(E.GATE) or not CHK.value(nl, fet).startswith(E.FET) or not CHK.value(nl, lim).startswith("TPS2553-1"):
            why.append("%s, %s or %s is not the drafted part" % (gate, fet, lim))
        ins = [CHK.pin(nl, gate, "1"), CHK.pin(nl, gate, "2")]
        want = ["IOC%s_RSTV%s" % (t, p) for p in (pa, pb)]
        if sorted(x or "" for x in ins) != sorted(want):
            why.append("%s's inputs are %s, not the two peers' restart votes %s" % (gate, ins, want))
        for p, pd in ((pa, rva), (pb, rvb)):
            kp = TAGS.index(p)
            vnet = "IOC%s_RSTV%s" % (t, p)
            gp = "1" if CHK.pin(nl, gate, "1") == vnet else "2"
            exact(vnet, ["%s.%s" % (gate, gp), "%s.1" % pd, "%s.%d" % (mcu(kp), vote_pin[(k - kp) % 3])])
            why += CHK.rows(nl, [(pd, "2", "GND")])
        exact(y, ["%s.4" % gate, "%s.1" % rrc, "%s.1" % rrb])
        exact(g, ["%s.2" % rrc, "%s.1" % crc, "%s.1" % rpd, "%s.1" % fet])
        exact(dr, ["%s.3" % fet, "%s.1" % rdr])
        exact(en, ["%s.3" % lim, "%s.2" % rpu, "%s.2" % rdr])
        exact(rb, ["%s.2" % rrb, "%s.%d" % (mcu(k), rb_pin)])
        h = holders(nl, k)
        if not (h[0] == "AND" and len(h[1]) == 1 and len(h[2]) == 1 and h[1] != h[2] and t not in (h[1] | h[2])):
            why.append("controller %s's EN is held by %s, not a 2-of-2 of its two peers" % (t, h))
        if CHK.pin(nl, rsup, "1") == "+3V3_IOC%s" % t:
            why.append("%s's restart gate sits on its own rail: dead when it is latched" % t)
    return ("DRAWN" if not why else "FAIL"), why


# ------------------------------------------------------------------------------------------------ the report
def main():
    out = []
    w = out.append
    F = figures()
    E = load(DOCS["canen"], "l4canen_canen_draft")
    MB = load(DOCS["canmb"], "l4canen_canmb_draft")
    REG = load(DOCS["regstage"], "l4canen_regstage_input")
    Q = F["Q"]
    pred = {}
    R = {}
    w("l4canen: record l4canen, T10 round 9 (Layer 4 task L4A-54's correction on W139's L4A-55): the latched supervisor's EN route")
    w("(W139-F2) drafted as record l9t5's apply_gen_sch_b_canen.py, composed with W137's canmb and W138's regstage in both orders, its")
    w("levels, recovery interval and own faults, and FW-B21's stop and the contract text read against the corrected drafts (MESHSAT-1357;")
    w("a DRAFT, NOT APPLIED; prototype design, nothing built or measured)")
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
    pg = text(DOCS["canq_page"])
    f2 = need(pg, r"(As drafted: nobody, so a latched supervisor\s+returns only by a kit power cycle \(RAIL_EN\), at the operator's time: the recovery proof is NOT met for that state \(W139-F2\)\.)",
              "T10-CANQ.md's W139-F2", re.S).group(1)
    regdoc = REG.__doc__
    node = need(regdoc, r"(EN on\s+IOC\{t\}_LIM_EN, pulled up to \+5V_IOC by 100 kOhm \(R602, R622, R642\): the node the peers' restart and the in-service test of\s+L4A-54 and L4A-58 would drive)",
                "W138's EN node", re.S).group(1)
    w("2. WHY (W139's finding and W138's node, quoted; unchecked drafts)")
    for ln in textwrap.wrap("T10-CANQ.md section 6: \"%s\"" % " ".join(f2.split()), 124):
        w("   " + ln)
    for ln in textwrap.wrap("W138's apply_gen_sch_b_regstage.py (inputs/, fnd/l4reg 86dbcdff): \"%s\"" % " ".join(node.split()), 124):
        w("   " + ln)
    w("   %s 9.3.1 (page %d, PRINTED): \"%s\"" % (F["lim_rev"], F["latch_p"], F["latch"]))
    w("     FAULT deglitch on an overcurrent %.0f to %.0f ms (7.5, page %d, PRINTED)" % (F["deglitch"][0] * 1e3, F["deglitch"][2] * 1e3, F["tab75_p"]))
    w("   the route (W139's, drawn here): the two peers restart a latched supervisor by a 2-of-2 vote on its limiter's EN, each on its own")
    w("     observation and needing no fabric, so that a single faulty peer can never hold a healthy supervisor off, as canmb's SHDN votes")
    w("")
    # ---------------------------------------------------------------- 3. the composition
    with tempfile.TemporaryDirectory(prefix="l4canen_") as d:
        runs = {}
        for tag, kw in (("mbre", dict(first="mb")), ("remb", dict(first="reg")), ("mbr0", dict(first="mb", with_en=False)),
                        ("rem0", dict(first="reg", with_en=False)), ("mb00", dict(first="mb", with_en=False, with_reg=False))):
            runs[tag] = build(d, tag, **kw)
            if not runs[tag][2]:
                refuse("board B did not compose or regenerate (%s): %s" % (tag, "; ".join("%s %s" % (s, v) for s, v, _m in runs[tag][1] if v != "OK")))
        nl1, nl2, nl0a, nl0b, nlm = (runs[t_][5] for t_ in ("mbre", "remb", "mbr0", "rem0", "mb00"))
        same_en = nl1["comps"] == nl2["comps"] and nl1["pins"] == nl2["pins"]
        same_0 = nl0a["comps"] == nl0b["comps"] and nl0a["pins"] == nl0b["pins"]
        nets = lambda nl: len({n for p in nl["pins"].values() for n in p.values() if n != "NC"})
        w("3. THE COMPOSITION on board B in L4-E9's change-list order: record l9t5's iocpre, canshdn, iocset and iocguard, then canmb and W138's")
        w("   regstage in either order, then apply_gen_sch_b_canen.py, then the efuse record's R-236 and R-237 and Layer 6's three; the")
        w("   generator run to its end through record l8p's gen_netlist.py")
        for tag, lab in (("mbre", "canmb, regstage, canen"), ("remb", "regstage, canmb, canen")):
            st = [(os.path.basename(s), v) for s, v, _m in runs[tag][1]]
            mid = [n for n, _v in st if n in ("apply_gen_sch_b_canmb.py", "l4reg-apply_gen_sch_b_regstage-469594bb.py", "apply_gen_sch_b_canen.py")]
            w("     order %-26s %d steps, every one %s; the three in turn: %s" % (lab + ":", len(st), "OK" if all(v == "OK" for _n, v in st) else "NOT OK",
                                                                        ", ".join(mid)))
        w("   the netlists of the two orders: %s with canen (%d parts, %d nets), %s without it (%d parts, %d nets; W138's claim re-read on the" % (
            "IDENTICAL" if same_en else "DIFFERENT", len(nl1["comps"]), nets(nl1), "IDENTICAL" if same_0 else "DIFFERENT", len(nl0a["comps"]), nets(nl0a)))
        w("     corrected canmb); canmb alone (iocguard's state, no regstage): %d parts" % len(nlm["comps"]))
        added = sorted(set(nl1["comps"]) - set(nl0a["comps"]), key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        retyped = sorted([r for r in set(nl1["comps"]) & set(nl0a["comps"]) if nl1["comps"][r].get("value") != nl0a["comps"][r].get("value")
                          or nl1["pins"].get(r) != nl0a["pins"].get(r)], key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        removed = sorted(set(nl0a["comps"]) - set(nl1["comps"]))
        for i_, ln in enumerate(textwrap.wrap("canen adds %d: %s" % (len(added), ", ".join(added)), 124)):
            w(("   " if i_ == 0 else "     ") + ln)
        w("   canen removes %d; changes the value or nets of %d: %s" % (len(removed), len(retyped), ", ".join(retyped)))
        cv, cw = con004(nl1)
        mv, mw = mb_check(nl1, MB)
        ev, ew = en_check(nl1, E)
        ev2 = en_check(nl2, E)[0]
        w("   CON-004 on the composed netlist (each rail sourced by its own regulator alone, no resistor joining two rails, two fabrics, their")
        w("     termination and break links, no part joining the fabrics): %s%s" % (cv, (": " + "; ".join(cw[:3])) if cw else ""))
        w("   canmb read by pin on the limiter's state (record l9t5's reading; the rail trips' rows replaced by W138's limiter and regulator):")
        w("     %s%s" % (mv, (": " + "; ".join(mw[:3])) if mw else ""))
        w("")
        # ------------------------------------------------------------ 4. the EN route read by pin, mutations, refusals
        w("4. THE EN ROUTE READ BY PIN (each controller's restart gate on the NEXT controller's rail through 100 Ohm, its inputs the two other")
        w("   controllers' planned restart pins each held low by 10 kOhm, its output through 100 kOhm into 4.7 uF with 1 MOhm to ground on an")
        w("   AO3400A whose drain reaches that controller's limiter EN through 470 Ohm, the EN pulled up by 10 kOhm, the read-back pin on the")
        w("   gate's output through 10 kOhm, nothing else on these nets; traced from each EN back to the controllers: a 2-of-2 of its two peers):")
        w("     order canmb first: %s%s; order regstage first: %s" % (ev, (": " + "; ".join(ew[:3])) if ew else "", ev2))
        for k, t in enumerate(TAGS):
            h = holders(nl1, k)
            w("     controller %s's EN: %s of {%s} and {%s}" % (t, h[0], ", ".join(sorted(h[1])), ", ".join(sorted(h[2])) if len(h) > 2 else ""))
        muts = []
        swaps = (("an EN route a single peer can hold (both of A's restart gate inputs from B)", [(("U586", "2"), ("R616", "1"))]),
                 ("the FET's gate driven by one peer's vote directly (no 2-of-2)", [(("Q586", "1"), ("R616", "1"))]),
                 ("the restart gate on the target's own rail (dead when it is latched)", [(("R615", "1"), ("U47", "5"))]),
                 ("the FET on another supervisor's EN (A's drain resistor on B's EN)", [(("R660", "2"), ("R662", "2"))]),
                 ("no delay (the FET's gate on the gate's output)", [(("Q586", "1"), ("R618", "1"))]),
                 ("the read-back on another controller's restart gate (A's pin 61 on B's)", [(("U41", "61"), ("U51", "61"))]),
                 ("a peer's vote on the wrong target (B's vote on A swapped with its vote on C)", [(("U51", "60"), ("U51", "59"))]))
        for i, (lab, sw) in enumerate(swaps):
            qn = D.mutate(runs["mbre"][4], d, "enm%d" % i, sw)
            nq = CHK.read(open(qn, "rb").read())
            muts.append((lab, en_check(nq, E)[0], holders(nq, 0)))
        hs = lambda h: h[0] + ("" if h[0] == "NONE" else " " + " ".join("{%s}" % ",".join(sorted(s)) for s in h[1:]))
        for lab, v, h in muts:
            w("     mutated, %-88s %s (A's EN: %s)" % (lab + ":", v, hs(h)))
        en_path = os.path.join(ROOT, DOCS["canen"])
        r_noreg = subprocess.run([sys.executable, "-B", en_path, runs["mb00"][3], "--write"], capture_output=True)
        p_nomb = D.compose("b", order(first="reg", with_en=False, with_mb=False), d, "nomb")[0]
        r_nomb = subprocess.run([sys.executable, "-B", en_path, p_nomb, "--write"], capture_output=True)
        r_twice = subprocess.run([sys.executable, "-B", en_path, runs["mbre"][3], "--write"], capture_output=True)
        r_tree = subprocess.run([sys.executable, "-B", en_path, D.GEN["b"], "--write"], capture_output=True)
        refused = (r_noreg.returncode == 3 and b"regstage" in r_noreg.stderr, r_nomb.returncode == 3 and b"canmb" in r_nomb.stderr,
                   r_twice.returncode == 3 and b"already applied" in r_twice.stderr, r_tree.returncode == 3 and b"NOT RELEASED" in r_tree.stderr)
        w("   the draft on a generator without regstage: %s; without canmb: %s; a second time: %s; on the tree's own generator: %s" % tuple(
            ("refused" if x else "NOT REFUSED") + (" (NOT RELEASED)" if i == 3 and x else "") for i, x in enumerate(refused)))
        w("")
        # ------------------------------------------------------------ 5. the pin plan
        h = pdf("h743")
        names = M.h743_names()
        w("5. THE PIN PLAN on the composed candidate, read against DS12110 Rev 10 Table 9 and RM0433 Rev 8 p.533")
        plan_ok = True
        for k, t in enumerate(TAGS):
            for p, (port, use, dist) in sorted(E.RST_PINS.items()):
                t9 = M.table9(h, p, port)
                before, after = CHK.pin(nl0a, mcu(k), str(p)), CHK.pin(nl1, mcu(k), str(p))
                ok = names.get(p) == port and t9 is not None and before in (None, "NC") and after not in (None, "NC") and port not in F["debug_pins"]
                plan_ok &= ok
                what = ("restart vote on %s" % TAGS[(k + dist) % 3]) if use == "vote" else "reads its own restart gate"
                w("     controller %s pin %d %-5s %-6s %-28s net %-16s free before: %s" % (t, p, port, t9[2] if t9 else "?", what, after,
                                                                                         "yes" if before in (None, "NC") else "NO (%s)" % before))
        cnt0 = {t: M.counts(nl0a, names, mcu(k)) for k, t in enumerate(TAGS)}
        cnt1 = {t: M.counts(nl1, names, mcu(k)) for k, t in enumerate(TAGS)}
        w("   every pin: the generator's port name, a Table 9 row with I/O, free before canen, no debug pin (%s): %s" % (", ".join(F["debug_pins"]),
                                                                                                                    "yes" if plan_ok else "NO"))
        w("   the votes are plain outputs, analog (high impedance) during and just after reset (RM0433 p.533), so the 10 kOhm holds each restart")
        w("     gate input low then; the read-back is a plain input with no pull (the gate drives it whenever the gate is powered)")
        w("   THE COUNT (CON-017's convention), per controller: before canen %d of 100; %d supplies, %d unconnected; with canen %d of 100; %d" % (
            cnt0["A"][:3] + cnt1["A"][:2]))
        w("     supplies, %d unconnected (the same for B and C: %s); CON-017 restated for its owner (finding W143-F4)" % (
            cnt1["A"][2], "yes" if cnt1["A"][:3] == cnt1["B"][:3] == cnt1["C"][:3] else "NO"))
        w("")
        R.update(same_en=same_en, same_0=same_0, cv=cv, mv=mv, ev=ev, ev2=ev2, muts=muts, refused=refused, plan_ok=plan_ok, cnt0=cnt0,
                 cnt1=cnt1, added=added, removed=removed, retyped=retyped, n1=len(nl1["comps"]), n0=len(nl0a["comps"]),
                 steps_ok=all(runs[t_][2] for t_ in runs))
    # ---------------------------------------------------------------- 6. levels
    rail_lo = min(F["rail_ap"][0], 3.3 * (1 - F["ldo_acc"]))
    rail_hi = max(F["rail_ap"][1], 3.3 * (1 + F["ldo_acc"]))
    v5_lo = F["v5_a"][0] * (1 - F["v5_budget"])
    v5_hi = F["v5_a"][1]
    kv = lambda s: float(re.match(r"([\d.]+)", s).group(1)) * {"k": 1e3, "M": 1e6, "R": 1.0}[re.match(r"[\d.]+([kMR])", s).group(1)]
    tol = lambda s: 0.01 if "1%" in s else 0.05
    r_sup, r_vpd, r_rc, r_pd, r_dr, r_rb, r_pu = (kv(x) for x in (E.R_SUP, E.R_VPD, E.R_RC, E.R_PD, E.R_DRAIN, E.R_RB, E.R_ENPU))
    t_sup, t_vpd, t_rc, t_pd, t_dr, t_pu = (tol(x) for x in (E.R_SUP, E.R_VPD, E.R_RC, E.R_PD, E.R_DRAIN, E.R_ENPU))
    c_nom = float(re.match(r"([\d.]+)u", E.C_RC).group(1)) * 1e-6
    L = {}
    L["vote_hi"] = rail_lo - F["voh_drop"]
    L["vote_lo"] = (F["g_ii"] + F["ilkg"]) * r_vpd * (1 + t_vpd)
    L["vote_i"] = rail_hi / (r_vpd * (1 - t_vpd))
    L["i_gate"] = F["g_icc"] + 2 * F["g_dicc"] + rail_hi / (r_rc * (1 - t_rc) + r_pd * (1 - t_pd)) + F["ilkg"]
    L["env_lo"] = rail_lo - r_sup * (1 + t_sup) * L["i_gate"]
    L["env_hi"] = rail_hi
    L["y_hi"] = L["env_lo"] - F["g_voh_drop"]
    k_lo = r_pd * (1 - t_pd) / (r_rc * (1 + t_rc) + r_pd * (1 - t_pd))
    k_hi = r_pd * (1 + t_pd) / (r_rc * (1 - t_rc) + r_pd * (1 + t_pd))
    L["vinf_lo"] = L["y_hi"] * k_lo
    L["vinf_hi"] = L["env_hi"] * k_hi
    rpar = lambda a, b: a * b / (a + b)
    L["rest"] = F["g_vol100"] * k_hi + F["igss"] * rpar(r_rc * (1 + t_rc), r_pd * (1 + t_pd))
    tau_min = rpar(r_rc * (1 - t_rc), r_pd * (1 - t_pd)) * C_EFF_MIN
    tau_max = rpar(r_rc * (1 + t_rc), r_pd * (1 + t_pd)) * c_nom * (1 + C_TOL)
    t_p = PULSE[1] - PULSE[0]
    L["pulse_g"] = L["rest"] + (L["vinf_hi"] - L["rest"]) * (1 - math.exp(-t_p / tau_min))
    L["pulse2_g"] = L["rest"] + (L["vinf_hi"] - L["rest"]) * (1 - math.exp(-2 * t_p / tau_min))
    L["en_lo"] = v5_hi * (r_dr * (1 + t_dr) + F["rdson25"]) / (r_pu * (1 - t_pu) + r_dr * (1 + t_dr) + F["rdson25"])
    L["en_lo_env"] = F["vin_max"] * (r_dr * (1 + t_dr) + F["rdson25"]) / (r_pu * (1 - t_pu) + r_dr * (1 + t_dr) + F["rdson25"])
    L["leak_ok"] = (v5_lo - F["en_vih"]) / (r_pu * (1 + t_pu)) - F["ien"]
    L["en_hi_th"] = v5_lo - (250e-6 + F["ien"]) * r_pu * (1 + t_pu)
    L["i_short_pu"] = v5_hi / (r_dr * (1 - t_dr))
    L["i_short_c"] = rail_hi / (r_sup * (1 - t_sup))
    L["rb_hi"] = L["y_hi"]
    L["rb_vih"] = F["vih_k"] * rail_hi
    L["rb_lo"] = F["g_vol100"] + F["ilkg"] * r_rb * 1.05
    L["rb_vil"] = F["vil_k"] * rail_lo
    L["fault_y"] = F["g_vol16"]
    L["fault_g"] = L["fault_y"] * k_hi + F["igss"] * rpar(r_rc * (1 + t_rc), r_pd * (1 + t_pd))
    L["dark_g"] = F["igss"] * r_pd * (1 + t_pd)
    L["ctrl"] = F["i_ctrl"] + L["i_gate"] + 2 * L["vote_i"]
    lv_ok = (L["vote_hi"] > F["g_vih"] and L["vote_lo"] < F["g_vil"] and L["vote_i"] < F["iio"] and 3.0 <= L["env_lo"] and L["env_hi"] <= 3.6
             and L["vote_hi"] >= L["env_hi"] - 0.6 and rail_hi <= F["g_vimax"] and L["vinf_lo"] > VGS_ON and L["pulse_g"] < F["vth"][0]
             and L["en_lo"] < F["en_vil"] and L["en_lo_env"] < F["en_vil"] and L["leak_ok"] > F["idss55"] and L["en_hi_th"] > F["en_vih"]
             and L["rb_hi"] > L["rb_vih"] and L["rb_lo"] < L["rb_vil"] and L["fault_g"] < F["vth"][0] and L["dark_g"] < F["vth"][0]
             and L["i_short_c"] + F["i_ctrl"] < F["ios"][0] and L["vinf_hi"] < F["vgs_max"])
    w("6. THE LEVELS on the makers' printed rows (MODEL from PRINTED figures; a resistor that names no tolerance at +-5 %, ASSUMPTION)")
    w("   each controller's rail: the envelope of the AP2112K-3.3's band (%.4f to %.4f V, l9t5_canmb.out) and W138's TPS73733's +-%.1f %% (%s 5.6," % (
        F["rail_ap"][0], F["rail_ap"][1], F["ldo_acc"] * 100, F["ldo_rev"]))
    w("     PRINTED for VOUT + 0.5 V <= VIN; INFERRED below it, W138's L4REG-F2): %.4f to %.4f V; +5V_IOC at board B %.4f to %.4f V (iocset's band" % (
        rail_lo, rail_hi, v5_lo, v5_hi))
    w("     %.4f to %.4f V at board A, DRAFTED, less the rail's %.0f %% budget)" % (F["v5_a"][0], F["v5_a"][1], F["v5_budget"] * 100))
    w("   the restart votes: a voter's high at least %.4f V (VDD - %.1f V at 8 mA, DS12110 Table 158) against the SN74LVC1G08's VIH %.1f V (VCC" % (
        L["vote_hi"], F["voh_drop"], F["g_vih"]))
    w("     3 to 3.6 V, %s 5.3); a voter in reset or dark leaves its input at most %.4f V (II %.0f uA and the pin's %.0f nA into the 10 kOhm)" % (
        F["g_rev"], L["vote_lo"], F["g_ii"] * 1e6, F["ilkg"] * 1e9))
    w("     against VIL %.1f V; the voter's output current at most %.3f mA, inside Table 158's 8 mA" % (F["g_vil"], L["vote_i"] * 1e3))
    w("   the gate's supply through %s from the NEXT controller's rail: the gate draws at most %.4f mA (ICC %.0f uA, delta ICC %.0f uA an input" % (
        E.R_SUP, L["i_gate"] * 1e3, F["g_icc"] * 1e6, F["g_dicc"] * 1e6))
    w("     at VCC - 0.6 V, PRINTED, taken for both; the votes stand within 0.6 V of its VCC: %.4f >= %.4f - 0.6), so its VCC is %.4f to %.4f V," % (
        L["vote_hi"], L["env_hi"], L["env_lo"], L["env_hi"]))
    w("     inside the 3 to 3.6 V rows; a peer's vote above it is inside the inputs' %.1f V (5.3)" % F["g_vimax"])
    w("   the FET's gate (%s from the gate's output, %s to ground, %s): the gate's high at least %.4f V (VCC - %.2f V at -100 uA, -40 to" % (
        E.R_RC, E.R_PD, E.C_RC + "F", L["y_hi"], F["g_voh_drop"]))
    w("     125 C, PRINTED), so a restart vote drives it toward at least %.4f V against the %.1f V at which the AO3400A's RDS(on) is printed" % (
        L["vinf_lo"], VGS_ON))
    w("     (at most %.0f mOhm, TJ 25 C, %s; at the 0.6 mA it carries here the drop is microvolts, so no temperature row is needed); at rest" % (
        F["rdson25"] * 1e3, F["fet_rev"]))
    w("     at most %.4f V (VOL %.1f V at 100 uA through the divider, IGSS %.0f nA, PRINTED at TJ 25 C)" % (L["rest"], F["g_vol100"], F["igss"] * 1e9))
    w("   A TEST PULSE of %.0f ms (the route's P and V phases) moves the FET's gate to at most %.4f V (two pulses back to back %.4f V) on the" % (
        t_p * 1e3, L["pulse_g"], L["pulse2_g"]))
    w("     RC's least time constant %.1f ms (%.1f uF effective, ASSUMPTION, a Layer 10 bound), against VGS(th) %.2f to %.2f V (PRINTED at TJ" % (
        tau_min * 1e3, C_EFF_MIN * 1e6, F["vth"][0], F["vth"][2]))
    w("     25 C only: margin %.3f V for the threshold's fall with temperature, which the sheet does not print): the test never switches the" % (
        F["vth"][0] - L["pulse_g"]))
    w("     supervisor off")
    w("   the limiter's EN, pulled up by %s to +5V_IOC, pulled down through %s by the FET: low at most %.4f V (%.4f V even at the sheet's" % (
        E.R_ENPU, E.R_DRAIN, L["en_lo"], L["en_lo_env"]))
    w("     %.1f V input maximum) against VIL %.2f V (%s 7.3, page %d, PRINTED); high, with the FET off, for any leakage up to %.1f uA (IEN" % (
        F["vin_max"], F["en_vil"], F["lim_rev"], F["en_vih_p"], L["leak_ok"] * 1e6))
    w("     %.1f uA PRINTED) against VIH %.1f V: the AO3400A prints IDSS %.0f uA at 25 C and %.0f uA at TJ 55 C (VDS 30 V), and no row above 55" % (
        F["ien"] * 1e6, F["en_vih"], F["idss25"] * 1e6, F["idss55"] * 1e6))
    w("     C, so at board B's 76.25 C air the margin (%.0f times the 55 C row) is an ASSUMPTION, not a printed bound (finding W143-F6); with the" % (
        L["leak_ok"] / F["idss55"]))
    w("     FET's gate at its least threshold (250 uA at VDS = VGS, PRINTED; taken at VDS up to 4.1 V, ASSUMPTION) EN stays at %.4f V" % L["en_hi_th"])
    w("     (the sheet sets mu and Omega in its SymbolMT font, so its text reads them as m and W: 'mA' there is uA and 'mW' is mOhm)")
    w("   a shorted EN pull-up: the FET then draws at most %.2f mA through %s during a restart, and the restart fails (a residual, section 8)" % (
        L["i_short_pu"] * 1e3, E.R_DRAIN))
    w("   the read-back (a plain input, %s from the gate's output): high at least %.4f V against 0.7 VDD = %.4f V, low at most %.4f V against" % (
        E.R_RB, L["rb_hi"], L["rb_vih"], L["rb_lo"]))
    w("     0.3 VDD = %.4f V (DS12110 Table 157); a FAULTY target driving its read-back pin reaches only the gate's output through %s, which" % (
        L["rb_vil"], E.R_RB))
    w("     then stays at most %.1f V (VOL at 16 mA, VCC 3 V, PRINTED): the FET's gate at most %.4f V, under its threshold" % (L["fault_y"], L["fault_g"]))
    w("   the dark cases: the gate unpowered (its supplying peer dark): its output takes at most %.0f uA (Ioff PRINTED) and the FET's gate rests" % (
        F["g_ioff"] * 1e6))
    w("     on its 1 MOhm at most %.4f V (IGSS): no restart and no switch-off; the latched target's read-back pin sees at most %.4f V through" % (
        L["dark_g"], rail_hi))
    w("     10 kOhm, inside the FT pins' unpowered maximum (gen_sch_b.py reading DS12110 Rev 10: \"%s\")" % F["ft_unpowered"])
    w("   the gate's 100 nF shorted: the next controller's rail carries at most %.1f mA more through %s; with its own worst state (%.4f A," % (
        L["i_short_c"] * 1e3, E.R_SUP, F["i_ctrl"]))
    w("     l9t5_canmb.out) that is %.4f A, under W138's limiter's least %.4f A: the next controller keeps its supply" % (
        F["i_ctrl"] + L["i_short_c"], F["ios"][0]))
    w("   each controller's own rail with the route: at most %.4f A (its worst %.4f A, plus the previous controller's restart gate %.4f mA" % (
        L["ctrl"], F["i_ctrl"], L["i_gate"] * 1e3))
    w("     and its two restart votes asserted, %.3f mA each): a labelled scenario for C-DEV (finding W143-F8), no case row changed here" % (
        L["vote_i"] * 1e3))
    w("   all levels hold: %s" % ("yes" if lv_ok else "NO"))
    w("")
    # ---------------------------------------------------------------- 7. timing and the recovery interval
    ppm = 20e-6
    t_eval = Q["t_eval_us"] * 1e-6
    W_ = Q["window_us"] * 1e-6
    skew = t_eval + 2 * ppm * T_DEC + 2.2 * r_rb * C_RB_PF * 1e-12
    t_charge = tau_max * math.log(L["vinf_lo"] / (L["vinf_lo"] - VGS_ON))
    en_low = T_HOLD - t_charge - skew
    t_dis = tau_max * math.log((L["vinf_hi"] - L["rest"]) / (F["vth"][0] - L["rest"]))
    probe_cycle = (Q["probe_period_us"] + Q["probe_len_us"]) * 1e-6
    rejoin = F["rc2"]
    recovery = T_DEC + t_eval + T_HOLD + t_dis + F["ton"] + F["tstr"] + rejoin
    p_avg = F["e_latch"] / T_RATE
    t_ok = (T_DEC > probe_cycle and T_DEC > rejoin and t_charge + skew < T_HOLD and en_low >= EN_LOW_MIN and EN_LOW_MIN > 100 * F["toff"]
            and T_RATE > recovery and F["tstr_col"] == "TYP")
    w("7. THE TIMING on printed figures and the drafted rows: the restart, the recovery interval, the rate")
    w("   THE DECISION (DRAFTED, W143-D5): a controller asserts its restart vote on a peer when it has captured no edge on either of that")
    w("     peer's TXDs (its own TIM3 captures) and received no state frame of it on either fabric for %.1f s, at most once in %.0f s per peer," % (T_DEC, T_RATE))
    w("     and holds it %.1f s; it needs no fabric and never votes on a message received over one. A running controller is never that" % T_HOLD)
    w("     silent: with both fabrics stopped by FW-B21 it still probes each once a second (%.1f s cycle, l9t5_canq.py CFG), and a booting" % probe_cycle)
    w("     controller rejoins within %.3f s (l9t5_canq.out section 8: boot, ASSUMPTION, MON 2 windows, its slot), both under %.1f s" % (rejoin, T_DEC))
    w("   the two peers' votes start within %.3f ms of each other (each evaluates within %.0f ms, DRAFTED; two crystals' +-20 ppm over the" % (
        skew * 1e3, t_eval * 1e3))
    w("     decision; the read-back copy of a TXD edge %.0f ns): they see the same last edge through the same buffers" % (2.2 * r_rb * C_RB_PF * 1e-3))
    w("   THE RESTART: the FET's gate passes %.1f V within %.3f s of the second vote (the RC's largest time constant %.3f s: %s and %s at" % (
        VGS_ON, t_charge, tau_max, E.R_RC, E.R_PD))
    w("     their 1 %%, %s +%.0f %%, ASSUMPTION), so EN is held under VIL for at least %.3f s of the %.1f s hold, against the %.0f ms the" % (
        E.C_RC + "F", C_TOL * 100, en_low, T_HOLD, F["toff"] * 1e3))
    w("     limiter's turn-off takes at most (%s 7.5, PRINTED) and the %.1f s this route requires (DRAFTED): \"the device enable is toggled\"" % (
        F["lim_rev"], EN_LOW_MIN))
    w("   THE RETURN: the votes released, the FET's gate falls under its least threshold within %.3f s; EN rises through %s; the limiter turns" % (
        t_dis, E.R_ENPU))
    w("     on within %.0f ms (%s 7.5, PRINTED, CL 1 uF, RL 100 Ohm), the TPS73733 starts in %.0f us (%s 5.6, new silicon: %s, no maximum" % (
        F["ton"] * 1e3, F["lim_rev"], F["tstr"] * 1e6, F["ldo_rev"], F["tstr_col"]))
    w("     printed), and the controller boots, listens 2 windows in bus monitoring mode and sends in its slot within %.3f s (W139's bound)" % rejoin)
    w("   THE RECOVERY INTERVAL of a latched supervisor, its cause gone: %.1f s (decision) + %.0f ms + %.1f s (hold) + %.3f s (release) +" % (
        T_DEC, t_eval * 1e3, T_HOLD, t_dis))
    w("     %.0f ms + %.0f us (TYPICAL) + %.3f s = %.3f s (MODEL on PRINTED, DRAFTED and the boot ASSUMPTION); before this round: NONE," % (
        F["ton"] * 1e3, F["tstr"] * 1e6, rejoin, recovery))
    w("     an operator's power cycle")
    w("   a persistent cause: the limiter latches again after its %.0f to %.0f ms deglitch (PRINTED) and the peers try again %.0f s after their" % (
        F["deglitch"][0] * 1e3, F["deglitch"][2] * 1e3, T_RATE))
    w("     last vote: at most %.1f mJ an attempt (W138's MODEL), %.2f mW on average; the other two keep the quorum throughout (IOHA row 3)" % (
        F["e_latch"] * 1e3, p_avg * 1e3))
    w("   with two supervisors latched the third cannot restart either (2 of 2 needs both peers): row 4's outcome until RAIL_EN is cycled;")
    w("     with all three latched (row 8 with W138's limiter, R8b) only RAIL_EN returns them, as W139 found")
    w("   a supervisor held off on the bench (IOHA A4 and A6, J_IOCOFF fitted) is restarted every %.0f s by its peers: harmless, its LDO's EN" % T_RATE)
    w("     stays held (finding W143-F9)")
    w("   timing holds: %s" % ("yes" if t_ok else "NO"))
    w("")
    # ---------------------------------------------------------------- 8. the route's own faults
    t_det = F["t_det"]
    rows = [("a restart vote output, its line or its gate input", "stuck low or open", "the route cannot restart the target", "V_EN fails", "T"),
            ("a restart vote output, its line or its gate input", "stuck high", "one peer alone could switch the target off (1 of 1)", "the other peer's P_EN fails", "T"),
            ("a peer's restart decision (firmware)", "votes without cause", "as a vote stuck high: alone it switches nothing", "the other peer's P_EN fails", "T"),
            ("a peer's restart decision (firmware)", "dead", "the route cannot restart the target", "NOT in service: RESIDUAL (recovery)", "-"),
            ("a restart vote pull-down (10 kOhm)", "short", "as its vote stuck low", "V_EN fails", "T"),
            ("a restart vote pull-down (10 kOhm)", "open", "floats only while its voter is in reset or dark", "NOT in service: RESIDUAL", "-"),
            ("the restart gate", "output stuck low", "the route cannot restart the target", "V_EN fails", "T"),
            ("the restart gate", "output stuck high", "the FET turns on: the target switched off (IOHA row 3)", "its frames absent", "S"),
            ("the gate's 100 Ohm feed", "open", "the gate unpowered: no restart", "V_EN fails", "T"),
            ("the gate's 100 Ohm feed", "short", "none until its 100 nF also shorts (then the next rail)", "NOT in service: RESIDUAL", "-"),
            ("the gate's 100 nF", "short", "the gate unpowered (next rail loaded, inside its limit)", "V_EN fails", "T"),
            ("the RC's 100 kOhm", "open", "the FET never turns on: no restart", "NOT in service: RESIDUAL (recovery)", "-"),
            ("the RC's 100 kOhm", "short", "no delay: a V_EN pulse reaches the FET", "V_EN: the target resets, one restart", "R"),
            ("the RC's 4.7 uF", "open", "no delay (the FET's own Ciss, TYPICAL only)", "V_EN: the target resets, one restart", "R"),
            ("the RC's 4.7 uF", "short", "the FET never turns on: no restart", "NOT in service: RESIDUAL (recovery)", "-"),
            ("the FET's 1 MOhm", "short", "the FET never turns on: no restart", "NOT in service: RESIDUAL (recovery)", "-"),
            ("the FET's 1 MOhm", "open", "its gate rests on leakage only while the gate is unpowered", "NOT in service: RESIDUAL", "-"),
            ("the AO3400A", "drain-source short", "EN held low: the target switched off (IOHA row 3)", "its frames absent", "S"),
            ("the AO3400A", "open, or gate-source short", "no restart", "NOT in service: RESIDUAL (recovery)", "-"),
            ("the 470 Ohm", "open", "no restart", "NOT in service: RESIDUAL (recovery)", "-"),
            ("the 470 Ohm", "short", "none (it bounds a shorted pull-up's current)", "NOT in service: RESIDUAL", "-"),
            ("the EN pull-up (10 kOhm)", "open", "EN floats: the limiter may switch off (IOHA row 3)", "its frames absent", "S"),
            ("the EN pull-up (10 kOhm)", "short", "EN cannot be pulled low: no restart", "NOT in service: RESIDUAL (recovery)", "-"),
            ("the read-back's 10 kOhm", "open", "the target cannot see its gate: V_EN reads low", "V_EN fails (a route fault flagged)", "T"),
            ("the read-back's 10 kOhm", "short", "a faulty target reaches the gate's output directly", "NOT in service: RESIDUAL", "-"),
            ("the target's read-back input", "stuck", "P_EN or V_EN reads wrong", "that phase fails", "T")]
    when = {"T": "within %.2f s" % t_det, "S": "within %.3f s" % (t_charge + F["toff"] + W_),
            "R": "within %.2f s, the target back within %.3f s" % (t_det, rejoin + F["ton"] + F["tstr"]), "-": "none"}
    w("8. THE ROUTE'S OWN FAULTS (per supervisor) and the route's in-service test")
    w("   THE TEST rides on the restated self-test (l9t5_canmb.out section 7): in the windows of the fabric A target X, P_EN in its P1 and P2")
    w("     windows pulses one peer's restart vote on X from %.0f to %.0f ms of that peer's window, V_EN in its V window both peers', and X reads" % (
        PULSE[0] * 1e3, PULSE[1] * 1e3))
    w("     its restart gate's output from %.0f to %.0f ms of its own (the windows aligned within %.1f ms, so each pulse lies inside the read span" % (
        READ[0] * 1e3, READ[1] * 1e3, F["align"] * 1e3))
    w("     and V_EN's two pulses overlap %.0f ms or more): P_EN reads low, V_EN high, and a fault is declared on the second consecutive failure;" % (
        (t_p - 2 * F["align"]) * 1e3))
    w("     the verdicts travel on either fabric, so the route's test keeps its interval, %.2f s, with one fabric down; one cycle %.4f s" % (t_det, F["cycle"]))
    w("   element                                          fault                       effect                                                 found by                              bound")
    for el, fl, eff, det, tt in rows:
        w("   %-48s %-27s %-54s %-37s %s" % (el, fl, eff, det, when[tt]))
    res = [r for r in rows if r[4] == "-"]
    rec = [r for r in res if "(recovery)" in r[3]]
    hold_any = [r for r in rows if "1 of 1" in r[2]]
    w("   %d residuals, %d of them of the recovery only (a latched supervisor then waits for RAIL_EN, the state before this round); none" % (
        len(res), len(rec)))
    w("     switches a healthy supervisor off or lets one peer do so alone; the faults that switch a supervisor off are single faults of its")
    w("     own power path, IOHA row 3, found at once; the one fault that leaves a 1-of-1 route (a vote stuck high, or a decision that votes")
    w("     without cause) is found within %.2f s by the other peer's P_EN, without switching anything off" % t_det)
    w("   NOT TAKEN (W143-D7): a start-up restart of each supervisor by its peers, which would bound the recovery residuals by the kit's power")
    w("     cycle at the cost of switching every healthy supervisor off once per start; the residuals stay named and are injected on the")
    w("     first article (section 10, the supplier's tasks)")
    w("")
    # ---------------------------------------------------------------- 9. FW-B21 and the contract text
    src = text(DOCS["contract_canq"])
    b21, b22, vb22 = literal(src, "FW_B21_NEW"), literal(src, "FW_B22_CANQ"), literal(src, "V_B22_CANQ")
    quote = "'%s'" % F["es_work"]
    must = ["DAR = 1", "ES0392 Rev %s %s" % (F["es_rev"], F["es_item"]), F["es_page"], quote, "12-window cycle", "(n mod 12) div",
            "by n mod 4", "its only frame in that hold", "through their attribution paths",
            "in the previous window every controller received every other's state frame on that fabric", "RESTART",
            "for %.0f s" % T_HOLD, "at most once in %.0f s per peer" % T_RATE, "never on a message received over a fabric",
            "from 68 ms to 72 ms", "from 66 ms to 74 ms", "on either fabric", "52 ms to 88 ms"]
    missing = [m_ for m_ in must if m_ not in b22]
    v_must = ["restart route", "P1, P2 and V pulses", "never switched off"]
    v_missing = [m_ for m_ in v_must if m_ not in vb22]
    with tempfile.TemporaryDirectory(prefix="l4canen_c_") as d:
        cp = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copy(os.path.join(ROOT, DOCS["contract"]), cp)
        run = lambda s, *a: subprocess.run([sys.executable, "-B", os.path.join(ROOT, s), cp] + list(a), capture_output=True).returncode
        steps = [run(DOCS["contract_canq"], "--check"), run(DOCS["contract_t10"], "--write"), run(DOCS["contract_canq"], "--write"),
                 run(DOCS["contract_canq"], "--write")]
        page = open(cp, encoding="utf-8").read()
    carried = b22.strip() in page and b21 in page
    stop_ok = ("more than %d windows" % Q["stop_windows"] in b21 and Q["stop_windows"] == Q["n_loss"] and F["f2"] == ("quorum lost", "quorum lost")
               and F["m1c"][:2] == ("a node out and contained", "a node out and contained"))
    c_ok = not missing and not v_missing and steps == [3, 0, 0, 3] and carried and F["acc_a9"] == "yes"
    w("9. FW-B21'S STOP AT THE LOSS COUNT AND THE CONTRACT TEXT, read against the corrected drafts (apply_hw_fw_contract_canq.py, W139's")
    w("   rows with this round's text; DRAFTED, UNAPPLIED)")
    for ln in textwrap.wrap("FW-B21 as restated: \"...%s\"" % b21, 124):
        w("   " + ln)
    w("   the stop is the loss count (%d windows; l9t5_canq.py CFG stop_windows %d, n_loss %d); with the drafted one-window stop W139's row F2" % (
        Q["stop_windows"], Q["stop_windows"], Q["n_loss"]))
    w("     (M1c's GPIO jammer on both fabrics) reads \"%s\" on both schedules against M1c's required \"a node out and contained\", which" % F["f2"][0])
    w("     the restated stop gives (\"%s\"): the single-window stop FAILS the jammer row (the test re-runs it, test_l4canen.py)" % F["m1c"][0])
    w("   consistent with the corrected drafts: the self-test never silences a state frame (its hold lies outside every slot,")
    w("     l9t5_canmb.out section 7), so no test phase can starve a fabric of valid frames toward the stop; a fabric the stop holds is")
    w("     probed once a second, so its controller's TXDs move within %.1f s, under the restart decision's %.1f s: the stop never invites a" % (
        probe_cycle, T_DEC))
    w("     restart; and the stopped fabric's self-test phases wait for it while the other fabric's run: %s" % ("yes" if stop_ok else "NO"))
    w("   FW-B22 restated carries: %s; missing: %s" % ("every phrase above" if not missing else "NOT every phrase", ", ".join(missing) or "none"))
    w("   DAR = 1 with ES0392 Rev %s %s's printed workaround quoted with its page (%s): \"%s\"" % (F["es_rev"], F["es_item"], F["es_page"], F["es_work"][:60] + "..."))
    w("   V-B22 restated carries the route's rows: %s" % ("yes" if not v_missing else "NO (%s)" % ", ".join(v_missing)))
    w("   on a scratch copy of the page: the draft without t10's rows exit %d; t10's written exit %d; this draft written exit %d; a second" % tuple(steps[:3]))
    w("     time exit %d; the written page carries FW-B22 and FW-B21 as drafted: %s; W139's A9 on this text: %s" % (
        steps[3], "yes" if carried else "NO", F["acc_a9"]))
    w("")
    # ---------------------------------------------------------------- 10. decisions, findings, disposition
    w("10. SESSION DECISIONS (W143-D1 to D10), FINDINGS (W143-F1 to F9) AND WHAT CLOSES ONCE CHECKED: in record l9t5's T10-ROUND9.md")
    w("   sections 7 to 9, with their reasons and reversals; nothing closes here: W139-F2's recovery proof for a latched supervisor, cx46's")
    w("   item 5, CON-004's quorum service and FW-B22 keep their states until the independent check (L4A-62) reads this round")
    w("")
    # ---------------------------------------------------------------- 11. predicates
    pred["the composition: canmb and regstage in either order, canen after both, every step OK, the netlists identical in both orders (with canen and without)"] = (
        R["steps_ok"] and R["same_en"] and R["same_0"])
    pred["the parts: canen adds 33, removes none, changes R602, R622 and R642 and the three controllers' pins"] = (
        len(R["added"]) == 33 and not R["removed"] and set(R["retyped"]) == {"R602", "R622", "R642", "U41", "U51", "U61"} and R["n1"] == R["n0"] + 33)
    pred["CON-004 holds on the composed netlist (three branches, each rail its own regulator's alone, two fabrics) and canmb reads DRAWN on the limiter's state"] = (
        R["cv"] == "HOLDS" and R["mv"] == "DRAWN")
    pred["the EN route reads DRAWN by pin in both orders, each EN held by a 2-of-2 of its two peers"] = R["ev"] == "DRAWN" and R["ev2"] == "DRAWN"
    pred["every mutation FAILS (seven), an EN route a single peer can hold among them"] = (
        len(R["muts"]) == 7 and all(v == "FAIL" for _l, v, _h in R["muts"]) and R["muts"][0][2][0] == "AND" and R["muts"][1][2][0] == "DIRECT")
    pred["the draft refuses a generator without regstage, without canmb, a second application and the tree's generator (NOT RELEASED)"] = all(R["refused"])
    pred["the pin plan: pins 59 to 61 free before, Table 9 I/O rows, no debug pin; the count 43 of 100, 14 supplies, 43 unconnected on each controller"] = (
        R["plan_ok"] and all(R["cnt1"][t][:3] == (R["cnt0"][t][0] + 3, 14, R["cnt0"][t][2] - 3) for t in TAGS) and R["cnt1"]["A"][:3] == (43, 14, 43))
    pred["the levels hold on the printed rows (votes, the gate's supply, the FET's gate under a test pulse and over 2.5 V on a restart, EN low and high, the read-back, the faulty and dark cases)"] = lv_ok
    pred["the timing holds and the recovery interval is bounded (decision over the probe cycle and the rejoin, EN low over the turn-off, the rate over the recovery)"] = t_ok and recovery < T_RATE
    pred["every fault of the route has a row; no residual lets one peer act alone; the 1-of-1 faults are found within the self-test's interval"] = (
        len(rows) == 26 and len(hold_any) == 1 and all(r[4] == "T" for r in rows if "1 of 1" in r[2] or r[1] == "votes without cause") and t_det < 10.0)
    pred["FW-B21's stop at the loss count consistent with the drafts, the single-window stop failing the jammer row (W139's F2)"] = stop_ok
    pred["the contract text carries DAR = 1 with ES0392's workaround quoted with its page, the restated self-test and the restart rule, and composes after t10's"] = c_ok
    pred["nothing closes here"] = True
    w("11. THE PREDICATES (v2/ecad/tools/tests/test_l4canen.py holds them)")
    for k_, v in pred.items():
        w("   %s: %s" % (k_, "yes" if v else "NO"))
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
