"""Layer 4 task L4A-59, record l9t5 (MESHSAT-1357, W140, 7 October 2026, corrected by W145 the same day on the focused check
L4A-100's findings F1 to F11; v2/docs/records/l9t5/): HO-E's comparison of three approaches
(H-1 a hardware-forced voltage scale, H-2 a firmware bound with an independent ending, H-3 a thermal-headroom part or heat path), the
selection SESSION W140-1 and its draft apply_gen_sch_b_vcoremon.py, held as predicates on what l9t5_hoe.py computes and on the files
of the task.

The predicates: the committed l9t5_hoe.out is what the script prints and every input it pins is present at the sha256 it names; every
predicate the script states reads yes (fourteen); the sentences H-1 rests on are re-found here in the makers' committed texts, page by
page, and no option-byte field selects a voltage scale; H-3's arithmetic is re-solved from Table 119 and Table 222; the monitor's
threshold band is re-solved from the TPS37's printed rows and the draft's own values and lies between VOS3's top and VOS1's bottom;
the draft applies to a copy of the tree's generator, refuses a second application and the tree's own generator, and leaves the tree
byte for byte; the six mutations read FAIL; the acceptance reads CONDITIONAL and never met; the page carries the selection's authority
fields and claims no closure; the task's new files carry no long dash, no private path and no claim word outside quotations. W145's
additions: the CTR1 hold re-solved from TI's Equation 2 and the draft's value, the reset loop's duty and rise re-solved and its
full-discharge condition kept CONDITIONAL (S5); the hold capacitor's removal reads FAIL; every thermal limit at one supply corner;
Table 56's pin-reset row re-read; the firmware row FW-B23 applies only after T10's draft and once; the register rows file. W148's (the
same day, on W145's finding W145-F1): the hold stage that replaces the CTR1 capacitor, its printed minimum re-read from TI's TPS3703 and
TPS3808 sheets with their columns, the loop's duty re-solved on it for any fault length (S5 retired), the stock TPS3703 windows re-solved
against VCAP's band (none fits), the hold stage bypassed and a hold under its printed minimum read FAIL, W148-1's authority fields. W152's
(the same day, on the targeted recheck W150's F1 to F6): the loop's mean re-solved here on T10's own temperature-dependent current (F2),
S1's limits by U-02's local air and C2's pair (F1), the self-reset loop's row S-m and register row R-4 (F3), the hold check on the
LSI-clocked RTC re-read from ST's pages (F4), the reader's FAIL on R812 not fitted as the tenth mutation (F5), the marker rule, the
14 ms after MR by reference and ES0392's revision codes (F6). These are
software predicates on a DRAFT and its arithmetic: they establish no property of any board, monitor or controller, and nothing in the
kit has been built or measured.
"""
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

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l9t5_hoe.py")
OUT = os.path.join(REC, "l9t5_hoe.out")
DRAFT = os.path.join(REC, "apply_gen_sch_b_vcoremon.py")
PAGE = os.path.join(REC, "HO-E-COMPARISON.md")
ROWS = os.path.join(REC, "HO-E-REGISTER-ROWS.md")
CDRAFT = os.path.join(REC, "apply_hw_fw_contract_hoe.py")
CT10 = os.path.join(REC, "apply_hw_fw_contract_t10.py")
CONTRACT = os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
ST = os.path.join(ROOT, "v2", "vendor", "st", "pdftext")
TI = os.path.join(ROOT, "v2", "vendor", "ti", "pdftext")
TI_HELD = os.path.join(ROOT, "v2", "vendor", "ti", "held", "pdftext")   # held back (records/l9t5hoe/fetch_held_back.py, then the re-take); absent: the test skips
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _out():
    """the script run from the repository root, once; its stdout, its exit status"""
    if "out" not in _C:
        need(SCRIPT, "the HO-E script")
        r = subprocess.run([sys.executable, "-B", SCRIPT], cwd=ROOT, capture_output=True)
        _C["out"], _C["rc"], _C["err"] = r.stdout.decode("utf-8"), r.returncode, r.stderr.decode("utf-8", "replace")
    return _C["out"]


def _draft():
    sp = importlib.util.spec_from_file_location("l9t5_hoe_draft_under_test", need(DRAFT, "the draft"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _num(pat, text_):
    m = re.search(pat, text_)
    assert m, "the output no longer prints %r" % pat
    return float(m.group(1))


def _txt(folder, name):
    return open(need(os.path.join(folder, name), name), encoding="utf-8").read()


def _has(t, sentence):
    return re.search(r"\s+".join(re.escape(w) for w in sentence.split()), t, re.S) is not None


def t_output_reproduced_and_every_input_pinned():
    text_ = _out()
    assert _C["rc"] == 0, "l9t5_hoe.py exited %d: %s" % (_C["rc"], _C["err"][-300:])
    assert text_ == open(need(OUT, "the committed output"), encoding="utf-8").read(), "l9t5_hoe.out is not what the script prints"
    pins = re.findall(r"^\s{3}([0-9a-f]{16}) (v2/\S+)", text_, re.M)
    assert len(pins) >= 35, len(pins)
    for h, rel in pins:
        assert hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest().startswith(h), "%s is not pinned at its current sha256" % rel


def t_every_predicate_holds():
    text_ = _out()
    rows = [l for l in text_.split("10. THE PREDICATES")[1].split("l9t5_hoe: done")[0].splitlines()[1:] if l.strip()]
    assert len(rows) == 32, rows
    assert all(l.rstrip().endswith(" yes") for l in rows), [l for l in rows if not l.rstrip().endswith(" yes")]


def t_h1_rests_on_the_pages_it_quotes():
    """the voltage scale is software's: RM0433 p.264, p.279, p.280, p.309, p.560, p.307; DS12110 Rev 11 p.29 and p.210; AN4938 Rev 7
    p.10 and p.19; re-found here in the committed texts, each on the page the output names; the option word holds no scale"""
    p262 = _txt(ST, "st-rm0433-rev8.layout.f262.l264.txt")
    p279 = _txt(ST, "st-rm0433-rev8.layout.f279.l280.txt")
    p307 = _txt(ST, "st-rm0433-rev8.layout.f307.l309.txt")
    p560 = _txt(ST, "st-rm0433-rev8.layout.p560.txt")
    a19 = _txt(ST, "st-an4938-rev7.layout.p19.txt")
    d29 = _txt(ST, "st-stm32h743xi-datasheet-rev11.layout.p29.txt")
    d210 = _txt(ST, "st-stm32h743xi-datasheet-rev11.layout.f208.l210.txt")
    assert "264/3353" in p262 and _has(p262, "The regulator output voltage can be scaled by software")
    assert "279/3353" in p279 and _has(p279, "This is done through the ODEN bit in the SYSCFG_PWRCR register.")
    assert "280/3353" in p279 and _has(p279, "VOS0 can be enabled only when VOS1 is programmed")
    assert "560/3353" in p560 and _has(p560, "1: Overdrive mode enabled (the LDO generates VOS0 for VCORE)")
    assert "307/3353" in p307 and _has(p307, "The lower byte of this register is written once after POR")
    assert "19/46" in a19 and _has(a19, "The power management unit can be bypassed. This feature can be configured by software.")
    assert "29/357" in d29 and _has(d29, "Scale 0: boosted performance (available only with LDO regulator)")
    assert "210/357" in d210 and _has(d210, "4. VOS0 is available only when the LDO regulator is ON.") and _has(d210, "5. TJMax = 105 °C.")
    opt = _txt(ST, "st-rm0433-rev8.layout.f215.l216.txt")
    fields = set(re.findall(r"Bits? \d+(?::\d+)? ([A-Z][A-Z0-9_]+)", opt.split("4.9.9")[1]))
    assert {"IWDG1_SW", "BOR_LEV", "RDP"} <= fields, fields
    assert not [f for f in fields if re.search(r"VOS|ODEN|SCU|LDO|BYPASS", f)], fields
    p256 = _txt(ST, "st-rm0433-rev8.layout.p256.txt")
    t32 = p256.split("Table 32.")[1].split("Table 33.")[0]
    assert "256/3353" in p256 and "PDR_ON" in t32 and "VCAP" in t32
    assert not re.search(r"scal|VOS|overdrive", t32, re.I), "a PWR pin of Table 32 names a voltage scale"
    text_ = _out()
    assert "VERDICT H-1: DROPS OUT" in text_ and "Not claimed: any hardware bar on VOS0" in text_


def t_h3_arithmetic_resolved_from_the_printed_rows():
    """the junction-to-ambient VOS0 needs at 76.25 C air, from Table 119's 550 mA at TJ 105 C, against Table 222's least ThetaJA"""
    t119 = _txt(ST, "st-stm32h743xi-datasheet-rev11.layout.p215.txt")
    rows = re.findall(r"^\s+480\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+-\s*$", t119, re.M)
    i_en = float(rows[1][3]) / 1e3
    assert i_en == 0.550
    need_en = (105.0 - 76.25) / (3.3 * i_en)
    t222 = _txt(ST, "st-stm32h743xi-datasheet-rev11.layout.f344.l345.txt")
    ja = [float(v) for v in re.findall(r"^\s+([\d.]+)\s*\n[^\n]*?(?:LQFP|TFBGA|UFBGA)", t222, re.M)[:8]]
    assert len(ja) == 8 and min(ja) == 36.6 and ja[0] == 45.0
    text_ = _out()
    assert abs(_num(r"all peripherals enabled, 0\.550 A at 105 C:\s+at most ([\d.]+) C/W", text_) - round(need_en, 2)) < 1e-9
    need_c = (105.0 - 76.25) / (3.3577 * i_en)                # W144's F8: one supply corner, the rail's top
    assert abs(_num(r"at the rail's top 3\.3577 V needs at most ([\d.]+) C/W", text_) - round(need_c, 2)) < 1e-9
    assert min(ja) > 2 * need_c
    assert "VERDICT H-3: NOT ESTABLISHED ON PRINTED FIGURES" in text_ and "VERDICT H-3: FAILS" not in text_   # W144's F10


def t_monitor_band_resolved_from_the_tps37_rows_and_the_draft():
    """VCAP_trip = VITP (1 + Rt/Rb) +- ISENSE Rt, resistors at 0.1 % + 25 ppm/K over 65 K; release at VITP - VHYS, VHYS at most
    2 % x 1.015 of VITP's minimum (TI Figure 7-1); the band between VOS3's 1.05 V and VOS1's 1.15 V (DS12110 Rev 11 Table 112)"""
    t = _txt(TI, "ti-tps37-snvsbj1e.layout.txt")
    m = re.search(r"VIT\s+= 800 mV \(3\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+V", t)
    v_lo, v_hi = float(m.group(1)), float(m.group(3))
    assert (v_lo, v_hi) == (0.792, 0.808)
    dm = _draft()
    rt, rb = float(dm.TOP.split("k")[0]) * 1e3, float(dm.BOTTOM.split("k")[0]) * 1e3
    e = 0.001 + 25e-6 * 65
    lo = v_lo * (1 + rt * (1 - e) / (rb * (1 + e))) - 100e-9 * rt * (1 + e)
    hi = v_hi * (1 + rt * (1 + e) / (rb * (1 - e))) + 100e-9 * rt * (1 + e)
    rel = (v_lo - 0.02 * 1.015 * v_lo) * (1 + rt * (1 - e) / (rb * (1 + e))) - 100e-9 * rt * (1 + e)
    assert 1.05 < lo < hi < 1.15 and rel > 1.05, (lo, hi, rel)
    text_ = _out()
    assert ("top %s" % dm.TOP) in text_ and re.search(r"top %s\s+trip %.4f to %.4f V, release from %.4f V.*SELECTED" % (
        re.escape(dm.TOP), lo, hi, rel), text_), "the selected row is not the re-solved band"
    assert 1.26 / hi - 1 < 0.20, "VOS0's overdrive reached the printed 20 %: S2 would no longer be owed"
    assert "the printed maximum does NOT cover" in text_


def t_the_draft_applies_once_and_refuses_the_tree():
    before = hashlib.sha256(open(GEN_B, "rb").read()).hexdigest()
    with tempfile.TemporaryDirectory() as d:
        cp = os.path.join(d, "gen_sch_b.py")
        shutil.copy(GEN_B, cp)
        r1 = subprocess.run([sys.executable, "-B", DRAFT, cp, "--write"], capture_output=True)
        assert r1.returncode == 0, r1.stderr[-300:]
        new = open(cp, encoding="utf-8").read()
        ast.parse(new)
        assert new.count("_VMON") >= 3 and "TPS37" in new and "IOC%s_MONRST" in new and '"6": "IOC%s_MONRST" % _tag' in new
        assert '"4": "IOC%s_MONOUT" % _tag' in new and "_MONCTR" not in new and "TPS3703F6050DSER" in new
        r2 = subprocess.run([sys.executable, "-B", DRAFT, cp, "--write"], capture_output=True)
        assert r2.returncode == 3 and b"already applied" in r2.stderr
    r3 = subprocess.run([sys.executable, "-B", DRAFT, GEN_B, "--write"], capture_output=True)
    assert r3.returncode == 3 and b"NOT RELEASED" in r3.stderr
    assert hashlib.sha256(open(GEN_B, "rb").read()).hexdigest() == before, "the tree's generator changed"
    dm = _draft()
    assert len(dm.ADDS) == 24 and len(set(dm.ADDS)) == 24 and {"U811", "U821", "U831", "R813", "R823", "R833", "C816"} <= set(dm.ADDS)
    assert not {"C813", "C814", "C815"} & set(dm.ADDS), "W145's CTR1 capacitors are withdrawn (W148-1)"


def t_mutations_fail_and_the_draft_reads_drawn():
    text_ = _out()
    sec = text_.split("the mutations (each must FAIL the reading")[1].split("\n", 1)[1].split("the draft on the tree's generator")[0]
    rows = [l for l in sec.splitlines() if l.strip() and not l.strip().startswith("its reading:")]
    assert len(rows) == 10 and all(l.rstrip().endswith("FAIL") for l in rows), rows
    assert "the hold removed" in rows[6] and "the hold stage bypassed" in rows[7] and "shorter than its printed minimum" in rows[8]
    assert "series resistor not fitted (R812" in rows[9], rows[9]                     # W150's F5: the tenth mutation
    tenth = sec.split("series resistor not fitted (R812")[1].split("\n")[1]
    assert "its reading:" in tenth and "R812 is not fitted" in tenth, tenth
    assert "V): DRAWN; before the draft: FAIL" in text_
    assert "DRAWN; the two netlists identical" in text_
    assert ("added 24: C810, C811, C812, C816, C817, C818, R810, R811, R812, R813, R820, R821, R822, R823, R830, R831, R832, R833, U810, "
            "U811, U820, U821, U830, U831; removed 0") in text_


def t_acceptance_conditional_never_met():
    text_ = _out()
    acc = text_.split("6. THE ACCEPTANCE")[1].split("7. THE SELECTION")[0]
    for s_ in ("S-c", "S-d", "S-e", "S-k", "S-m"):
        row = [l for l in acc.splitlines() if l.strip().startswith(s_)][0]
        assert row.rstrip().split("  ")[-1].strip().startswith("CONDITIONAL"), row
    for s_, cond in (("S-c", "C2, C3"), ("S-d", "C2, C3"), ("S-e", "C2"), ("S-k", "C2, C3"), ("S-m", "C2, C3")):   # W150's F1
        row = [l for l in acc.splitlines() if l.strip().startswith(s_)][0]
        assert cond in row.rstrip().split("  ")[-1], (s_, row)
    sk = [l for l in acc.splitlines() if l.strip().startswith("S-k")][0]
    assert "S5" not in sk and "any fault length" in sk, sk           # W148-1: the loop's bound no longer rests on S5
    assert "every excursion the monitor registers" in sk, sk         # W150's F3
    sm = [l for l in acc.splitlines() if l.strip().startswith("S-m")][0]
    assert "S2 extended" in sm and "R-4" in sm, sm
    assert "W148-3" in [l for l in acc.splitlines() if l.strip().startswith("S-l")][0]
    for c_ in ("C1 (F1)", "C2 (F2; W150's F1), a pair", "C3 (F4)", "C4 (F8, F11)", "C5 (F3, F6)"):
        assert c_ in acc, c_
    assert "HO-E's ACCEPTANCE: CONDITIONAL" in acc
    for bad in ("ACCEPTANCE: MET", "ACCEPTANCE: HOLDS", "HO-E CLOSED", "cx46 item CLOSED"):
        assert bad not in text_, bad
    sel = text_.split("7. THE SELECTION")[1].split("8. THE DRAFT")[0]
    for f in ("authority: SESSION", "authority_why:", "ruled_by: W140", "ruled_on: 7 October 2026", "reversed_by: none", "PREPARED AND NOT RAISED"):
        assert f in sel, f


def t_the_page_states_the_selection_and_no_closure():
    page = open(need(PAGE, "the comparison page"), encoding="utf-8").read()
    first = page.splitlines()[0]
    assert first.startswith("**") and "DONE:" in first and "NOT DONE:" in first and "NEXT:" in first, first[:200]
    for s_ in ("H-1", "H-2", "H-3", "DROPS OUT", "NOT ESTABLISHED", "PROVISIONAL", "CONDITIONAL", "SESSION W140-1", "authority_why", "ruled_by",
               "ruled_on", "reversed_by", "apply_gen_sch_b_vcoremon.py", "NOT APPLIED", "S1", "S2", "S3", "S4", "S5", "L4A-100", "L4REG-F7",
               "0.5704 A", "76.0 C/W", "p.560", "p.279", "p.344", "NOT CLOSED", "C1", "C2", "C3", "C4", "C5", "W145-1", "W145-5", "Table 56",
               "p.329", "p.306", "FW-B23", "HO-E-REGISTER-ROWS.md", "apply_hw_fw_contract_hoe.py", "Equation 2", "p.23", "W148-1", "W148-3",
               "TPS3703", "HS-1", "HS-2", "HS-3", "S5: RETIRED", "SBVS249B", "tMR_W", "S-m", "R-4", "W152-1", "W152-5", "3.05 K/W",
               "78.81 C", "79.32 C", "ES0392 Rev 15", "0x2003", "PRINTED BY REFERENCE", "Ten mutations FAIL", "9b", "every excursion the monitor registers"):
        assert s_ in page, s_
    for bad in ("HO-E CLOSED", "desk acceptance MET", "hardware bar on VOS0 exists", "ACCEPTANCE: MET"):
        assert bad not in page, bad
    text_ = _out()
    for figure in re.findall(r"\b\d+\.\d+ (?:C/W|K/W|us)\b", page):
        assert figure in text_, "the page's figure %r is not in l9t5_hoe.out" % figure


def t_record_hygiene():
    files = [SCRIPT, OUT, DRAFT, PAGE, ROWS, CDRAFT, os.path.abspath(__file__)]
    for p in files:
        t = open(need(p, os.path.basename(p)), encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p != os.path.abspath(__file__):
            scan = re.sub(r"\"[^\"\n]*\"", "", t)
            scan = re.sub(r"'[^'\n]*'", "", scan)
            mm = CLAIM.search(scan)
            assert not mm, "a claim word %r in %s" % (mm.group(0), os.path.basename(p))


def t_hold_and_reset_loop_resolved():
    """W144's F1 as W148 corrects it (W145-F1): the hold is TI TPS3703 option F's tD with CT pulled to VDD, 14 ms minimum (SBVS249B 7.6,
    p.7), for any manual-reset pulse of tMR_W, 1 us, in the MIN column; the loop's least pulse (NRST's fastest fall) exceeds it; the duty
    re-solved as t_resp / tD(min) and the rise from the one-corner step; W145's CTR1 hold kept only as withdrawn history"""
    t = _txt(TI_HELD, "ti-tps3703-sbvs249b.layout.txt")
    page_of = lambda s: t.count("\x0c", 0, t.index(s)) + 1
    m = re.search(r"^ tD\s+Reset time delay, TPS3703B, TPS3703F\s+CT = 10 k\S to VDD\s+(\d+)\s+(\d+)\s+(\d+)\s+ms\s*$", t, re.M)
    assert m and (m.group(1), m.group(2), m.group(3)) == ("14", "20", "26") and page_of("Reset time delay, TPS3703B, TPS3703F") == 7
    hdr = re.search(r"^ +PARAMETER +MIN +NOM +MAX +UNIT *$", t, re.M).group(0)
    row = re.search(r"^ tMR_W\s+MR pin pulse width duration to assert RESET\s+(\d+)", t, re.M)
    assert row.group(1) == "1" and abs((row.end(1) - row.start(0)) - (hdr.index("MIN") + 3)) <= 2, "tMR_W is not in the MIN column"
    dm = _draft()
    assert dm.HOLD_PART == "TPS3703F6050DSER" and dm.CT_PULLUP.startswith("10k")
    text_ = _out()
    t_resp = _num(r"t_resp = 17 \+ 0\.5 \+ [\d.]+ \+ 0\.3 us = ([\d.]+) us", text_) * 1e-6
    p_ex = _num(r"0\.550 A adds ([\d.]+) W", text_)
    duty = t_resp / 0.014
    assert abs(_num(r"the duty is at most t_resp / tD\(min\) = [\d.]+ / 14000 us = ([\d.]+) %", text_) - round(duty * 100, 3)) < 1e-9
    assert abs(_num(r"W148's ([\d.]+) K held the step at the bounded state", text_) - round(duty * p_ex * 45.0, 3)) < 1e-9
    assert duty < 0.01 and "S5 is RETIRED" in text_ and "S5: RETIRED (SESSION W148-1)" in text_
    assert "prints 'tD' in its NOM column" in text_                       # W150's F6: the 14 ms after MR by reference
    row = re.search(r"^ tD \(MR\)\s+MR reset time delay\s+(tD)\s+ms\s*$", t, re.M)
    assert row and abs((row.end(1) - row.start(0)) - (hdr.index("NOM") + 3)) <= 2, "tD(MR)'s 'tD' is not in the NOM column"
    assert _num(r"In a loop the MR pulse lasts at least NRST's fastest fall, ([\d.]+) us", text_) > 1.0
    assert "W145's CTR1 hold, WITHDRAWN (the history of S5)" in text_ and "CONDITIONAL on S5" not in text_.split("5g. THE RESET LOOP")[1].split("W145's CTR1 hold, withdrawn")[0]


def t_hold_stage_compared():
    """W148's comparison (5h): TPS3808's MR pulse prints in the TYP column only (SBVS050N 6.6, p.7) and its td 180 ms minimum; no orderable
    TPS3703 window (its addendum) keeps VCAP's printed VOS3 band inside it and trips under VOS1's bottom, re-solved here on 7.5's
    accuracy and hysteresis; the selection W148-1 carries its authority fields and HS-1a stands as its reversal"""
    t7 = _txt(TI, "ti-tps3808.layout.p7.txt")
    hdr = re.search(r"^ +PARAMETER +TEST CONDITIONS +MIN +TYP +MAX UNIT *$", t7, re.M).group(0)
    row = re.search(r"^ +RESET\s+MR\s+VIH = 0\.7VDD, VIL = 0\.3VDD\s+([\d.]+)", t7, re.M)
    assert row.group(1) == "0.001" and abs((row.end(1) - row.start(0)) - (hdr.index("TYP") + 3)) <= 2, "TPS3808's MR pulse is not TYP"
    assert re.search(r"CT = VDD\s+180\s+300\s+420\s+ms", t7)
    t = _txt(TI_HELD, "ti-tps3703-sbvs249b.layout.txt")
    orderable = sorted(set(re.findall(r"^\s+TPS3703([A-D])(\d)(\d{3})DSER\s+Active\s", t, re.M)))
    assert len(orderable) == 13, orderable
    for _l, tl, nom in orderable:
        nom_v, tl_v = int(nom) / 100.0, int(tl) / 100.0
        acc, hy = (0.007, 0.008) if nom_v >= 0.8 else (0.01, 0.007)
        ov, uv = nom_v * (1 + tl_v), nom_v * (1 - tl_v)
        g_hi = min(1.0, ov * (1 - acc) * (1 - hy) / 1.05)
        g_lo = max(ov * (1 + acc) / 1.15, uv * (1 + acc) * (1 + hy) / 0.95)
        assert g_lo >= g_hi, "an orderable TPS3703 window fits VCAP: %s at %s %%" % (nom, tl)
    text_ = _out()
    sel = text_.split("7. THE SELECTION")[1].split("8. THE DRAFT")[0]
    for f in ("W148-1", "W148-2", "W148-3", "ruled_by: W148 (Claude)", "reversed_by: none", "HS-1a (TPS3808G30", "REVERSED by W148-1"):
        assert f in sel, f
    cmp_ = text_.split("5h. THE HOLD, COMPARED")[1].split("VERDICT H-2")[0]
    assert "HS-1a" in cmp_ and "HS-1b" in cmp_ and "HS-2" in cmp_ and "HS-3" in cmp_ and "none fits" in cmp_ and "SELECTED (SESSION W148-1" in cmp_


def t_one_supply_corner():
    """W144's F8: the S-c limit from the bounded state and the step at the same rail's top, read off the output's own figures"""
    text_ = _out()
    m = re.search(r"at 3\.3577 V ([\d.]+) C at ([\d.]+) A", text_)
    tb, ib = float(m.group(1)), float(m.group(2))
    assert 100.0 < tb < 100.5 and 0.158 < ib < 0.159
    p_ex = 3.3577 * (0.550 - ib)
    assert abs(_num(r"must be at most ([\d.]+) K/W \(W140's 4\.09 K/W", text_) - (105.0 - tb) / p_ex) < 0.01
    p1 = 3.3577 * (0.544 - ib)                                 # W144's F7: Table 120's 544 mA
    assert abs(_num(r"inside VOS1's 125 C \([\d.]+ K\): at most ([\d.]+) K/W at t_resp", text_) - (125.0 - tb) / p1) < 0.01
    t216 = _txt(ST, "st-stm32h743xi-datasheet-rev11.layout.p216.txt")
    assert "216/357" in t216 and re.search(r"^\s+400\s+175\s+264\s+336\s+424\s+544\s*$", t216, re.M)
    air = _num(r"the bounded state itself reaches 105 C at ([\d.]+) C local air at 3\.3577 V", text_)
    assert 76.25 < air < 81.89


def t_reset_flags_pattern():
    """W144's F3 and F5: Table 56's row 2 re-read from the committed RM0433 text (p.332), the reset scope of NRST (p.329, Table 55 p.330),
    and the drafted firmware row carrying exactly that pattern"""
    t = _txt(ST, "st-rm0433-rev8.layout.f329.l332.txt")
    assert "329/3353" in t and "332/3353" in t and "331/3353" in t
    assert _has(t, "A system reset (nreset) resets all registers to their reset values unless otherwise specified in the register description.")
    assert _has(t, "Resets VDD domain: IWDG1, LDO...")
    m = re.search(r"^\s*2\s+Pin reset \(NRST\)\s+((?:[01]\s+){9}[01])\s*$", t, re.M)
    assert m and m.group(1).split() == ["0", "0", "0", "0", "0", "1", "0", "0", "0", "1"], m and m.group(1)
    p306 = _txt(ST, "st-rm0433-rev8.layout.p306.txt")
    assert "306/3353" in p306 and _has(p306, "This register is reset only by POR. It is not reset by wakeup from Standby mode and by the RESET pad.")
    sp = importlib.util.spec_from_file_location("l9t5_hoe_contract_under_test", need(CDRAFT, "the contract draft"))
    cm = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(cm)
    for k in ("PINRSTF and CPURSTF set", "LPWRRSTF, WWDG1RSTF, IWDG1RSTF, SFTRSTF, PORRSTF, BORRSTF, D2RSTF and D1RSTF clear", "RMVF",
              "wait 122.6 us from that write", "no wait on VOSRDY", "at least 12 ms, else HOLD FAILED", "RTCSEL = LSI", "never the HSE",
              "PREDIV_A + 1 at most 8", "does not run the test again", "under 8.474 ms, NRST's rise bounded at 1.254 ms"):
        assert k in cm.FW_B23, k


def t_contract_draft_applies_after_t10_once():
    before = hashlib.sha256(open(need(CONTRACT, "the contract"), "rb").read()).hexdigest()
    with tempfile.TemporaryDirectory() as d:
        cp = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copy(CONTRACT, cp)
        r0 = subprocess.run([sys.executable, "-B", CDRAFT, cp, "--write"], capture_output=True)
        assert r0.returncode == 3 and b"T10 rows" in r0.stderr
        assert subprocess.run([sys.executable, "-B", CT10, cp, "--write"], capture_output=True).returncode == 0
        r1 = subprocess.run([sys.executable, "-B", CDRAFT, cp, "--write"], capture_output=True)
        assert r1.returncode == 0, r1.stderr[-300:]
        new = open(cp, encoding="utf-8").read()
        assert [l for l in new.splitlines() if l.startswith("| FW-B")][-1].startswith("| FW-B23 |")
        assert [l for l in new.splitlines() if l.startswith("| V-B")][-1].startswith("| V-B24 |")
        assert new.rstrip("\n").splitlines()[-1].startswith("| 2 (HO-E, P0) |")
        r2 = subprocess.run([sys.executable, "-B", CDRAFT, cp, "--write"], capture_output=True)
        assert r2.returncode == 3 and b"already applied" in r2.stderr
    assert hashlib.sha256(open(CONTRACT, "rb").read()).hexdigest() == before, "the tree's contract changed"


def t_register_rows_file():
    """W144's F3 and F6 (condition C5): the rows the coordinator enters, each with its task, deliverable, acceptance and dependency"""
    t = open(need(ROWS, "the register rows file"), encoding="utf-8").read()
    first = t.splitlines()[0]
    assert first.startswith("**") and "DONE:" in first and "NOT DONE:" in first and "NEXT:" in first, first[:200]
    for rid in ("R-1", "R-2", "R-3", "R-4"):
        sec = t.split("## " + rid)[1].split("\n## ")[0]
        for f in ("Task:", "Deliverable:", "Acceptance:", "Dependency:"):
            assert f in sec, (rid, f)
    assert "S-f" in t and "S-g" in t and "FW-B23" in t and "Table 56" in t
    r4 = t.split("## R-4")[1]
    assert "S-m" in r4 and "S2 extended" in r4 and "1000" in r4 and "zero escapes" in r4 and "twice" in r4, r4[:300]   # W150's F3
    r3 = t.split("## R-3")[1].split("\n## ")[0]
    assert "12 ms" in r3 and "LSI" in r3 and "7 ms" not in r3, r3[:300]                                             # W150's F4


def _t10():
    """T10's own model (l9t5_t10.py's figures, figures5 and mcu_i), imported by path; nothing of it is changed"""
    if "t10" not in _C:
        sys.path.insert(0, REC)
        sp = importlib.util.spec_from_file_location("l9t5_hoe_t10_under_test", need(os.path.join(REC, "l9t5_t10.py"), "T10's script"))
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        P = m.figures()
        _C["t10"] = (m, P, m.figures5(P))
    return _C["t10"]


def _bisect(g, lo, hi):
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if g(mid) > 0:
            lo = mid
        else:
            hi = mid
    return hi


def t_loop_rise_with_t10_feedback():
    """W150's F2: the loop's mean junction re-solved here on T10's temperature-dependent current, TJ = air + theta x V x ((1 - d) x I(TJ)
    + d x 0.550 A) at the rail's top, against the output's 101.01 C, 0.806 K and S1's loop limit 3.05 K/W from that mean state"""
    T, P, Q = _t10()
    text_ = _out()
    air, th, V = P["air"], P["theta_mcu"], 3.3577
    i = lambda tj: T.mcu_i(P, Q, "V", tj)
    tb = _bisect(lambda tj: air + th * V * i(tj) - tj, air, 125.0)
    t_resp = _num(r"t_resp = 17 \+ 0\.5 \+ [\d.]+ \+ 0\.3 us = ([\d.]+) us", text_) * 1e-6
    d = t_resp / 0.014
    tm = _bisect(lambda tj: air + th * V * ((1 - d) * i(tj) + d * 0.550) - tj, air, 125.0)
    z = (105.0 - tm) / (V * (0.550 - i(tm)))
    assert abs(_num(r"the loop's mean junction solves TJ = .*?: ([\d.]+) C at I", text_) - round(tm, 2)) < 1e-9
    assert abs(_num(r"a rise of ([\d.]+) K over the bounded state's", text_) - round(tm - tb, 3)) < 1e-9
    assert abs(_num(r"S1's limit at t_resp becomes \(105 - [\d.]+\) / \([\d.]+ V x \([\d.]+ - [\d.]+\) A\) = ([\d.]+) K/W", text_) - round(z, 2)) < 1e-9
    assert round(tm, 2) == 101.01 and round(tm - tb, 3) == 0.806 and round(z, 2) == 3.05, (tm, tm - tb, z)   # W150's reading reproduced
    assert z < (105.0 - tb - d * V * (0.550 - i(tb)) * th) / (V * (0.550 - i(tb))), "the feedback must lower the limit"


def t_local_air_pair():
    """W150's F1: S1's limits as a function of U-02's local air (the output's table), each falling with the air, the loop's zero
    re-solved here under the bounded state's, and C2 restated as a pair on the page and in the output"""
    T, P, Q = _t10()
    text_ = _out()
    V, th = 3.3577, P["theta_mcu"]
    i = lambda tj: T.mcu_i(P, Q, "V", tj)
    t_resp = _num(r"t_resp = 17 \+ 0\.5 \+ [\d.]+ \+ 0\.3 us = ([\d.]+) us", text_) * 1e-6
    d = t_resp / 0.014
    tab = text_.split("local air   bounded state")[1].split("at ")[0]
    rows = re.findall(r"^\s+([\d.]+) C\s+([\d.]+) C\s+(\S+)(?: K/W)?\s+(\S+)(?: K/W)?\s+(\S+) K/W\s*$", tab, re.M)
    assert [r[0] for r in rows] == ["76.25", "77.00", "78.00", "79.00"], rows
    for a, tb_s, lc, lk, ld in rows:
        a = float(a)
        tb = _bisect(lambda tj: a + th * V * i(tj) - tj, a, 125.0)
        assert abs(float(tb_s) - round(tb, 2)) < 1e-9 and abs(float(lc) - round((105.0 - tb) / (V * (0.550 - i(tb))), 2)) < 1e-9
        assert abs(float(ld) - round((125.0 - tb) / (V * (0.544 - i(tb))), 2)) < 1e-9
    lims = [float(r[2]) for r in rows]
    assert lims == sorted(lims, reverse=True) and rows[3][3] == "none" and float(rows[0][3]) < float(rows[0][2])
    mean = lambda a: _bisect(lambda tj: a + th * V * ((1 - d) * i(tj) + d * 0.550) - tj, a, 125.0)
    a0 = _bisect(lambda a: 105.0 - mean(a), 70.0, 85.0)
    ab = _bisect(lambda a: 105.0 - _bisect(lambda tj: a + th * V * i(tj) - tj, a, 125.0), 70.0, 85.0)
    assert abs(_num(r"at ([\d.]+) C local air the loop's mean junction reaches 105 C", text_) - round(a0, 2)) < 0.011
    assert round(ab, 2) == 79.32 and 76.25 < a0 < ab, (a0, ab)
    assert "C2 (F2; W150's F1), a pair" in text_
    page = open(need(PAGE, "the comparison page"), encoding="utf-8").read()
    assert "C2 (F2; W150's F1), a pair:" in page and "| 77.00 C | 101.38 C | 2.78 K/W | 2.17 K/W | 18.39 K/W |" in page


def t_self_reset_loop_has_its_own_row():
    """W150's F3: W148-F4's case is S-m, a VOS1 or VOS0 state with a printed current and no printed cadence, CONDITIONAL on S2 extended
    (specimen, quantity, pass limit), filed under R-4 and no longer under S-g"""
    text_ = _out()
    sec = text_.split("5i. THE SELF-RESET LOOP")[1].split("5h. THE HOLD, COMPARED")[0]
    for k in ("S2 EXTENDED (SESSION W152-3)", "three supervisors", "76 C and at -40 C", "1000 self-reset cycles", "zero escapes",
              "at least 2x the longest unregistered", "not S-g's kind", "credited nothing"):
        assert k in sec, k
    fnd = text_.split("9. FINDINGS")[1]
    assert "NOT S-g's kind (W148's classification withdrawn)" in fnd and "S-g's kind (no printed current for an image outside FW-B20), not" not in fnd
    assert "EXTENDED for S-m" in fnd


def t_hold_check_on_the_lsi():
    """W150's F4: the hold check's time base re-read from ST's committed pages (RM0433 Rev 8 pp.426, 428, 1932; DS12110 Rev 11 Table
    136, p.233), its PASSED reading and its budget re-solved, the HSE excluded, no LSE crystal drawn"""
    p426 = _txt(ST, "st-rm0433-rev8.layout.p426.txt")
    p428 = _txt(ST, "st-rm0433-rev8.layout.p428.txt")
    p1932 = _txt(ST, "st-rm0433-rev8.layout.p1932.txt")
    p233 = _txt(ST, "st-stm32h743xi-datasheet-rev11.layout.p233.txt")
    assert "426/3353" in p426 and _has(p426, "Any other internal or external reset will not have any effect on these bits.")
    assert _has(p426, "If HSE is selected as RTC clock: this clock is lost when the system is in Stop mode or in case of a pin reset (NRST).")
    assert "428/3353" in p428 and _has(p428, "if there is a request for LSI clock by the Clock Security System on LSE or by the Low Speed Watchdog or by the RTC.")
    assert "1932/3353" in p1932 and _has(p1932, "System reset: not affected") and _has(p1932, "ck_apre frequency = RTCCLK frequency/(PREDIV_A+1)")
    m = re.search(r"^\s+([\d.]+)\s+-\s+([\d.]+)\s*\n\s+3\.6 V\s*\n\s+LSI oscillator", p233, re.M)
    f_lo, f_hi, f_nom = float(m.group(1)) * 1e3, float(m.group(2)) * 1e3, 32e3
    assert (f_lo, f_hi) == (29400.0, 33600.0) and "233/357" in p233
    step = 8 / f_nom
    pass_min = 0.014 * f_lo / f_nom - step
    r_max = (0.012 - step) * f_nom / f_hi
    text_ = _out()
    assert pass_min >= 0.012 and abs(_num(r"= ([\d.]+) ms: over the 12 ms threshold", text_) - round(pass_min * 1e3, 3)) < 1e-9
    assert abs(_num(r"kHz = ([\d.]+) ms; that interval is", text_) - round(r_max * 1e3, 3)) < 1e-9
    t_rise = _num(r"NRST's rise to VIH 0\.7 x VDD \(Table 147, p\.241\)\s+at most ([\d.]+) ms", text_) * 1e-3
    assert abs(t_rise - 8.6779e3 * 120e-9 * math.log(1 / 0.3)) < 2e-6, t_rise       # 10.5 k parallel 50 k into 120 nF, 0 V to 0.7 VDD
    t_resp = _num(r"t_resp = 17 \+ 0\.5 \+ [\d.]+ \+ 0\.3 us = ([\d.]+) us", text_) * 1e-6
    budget = r_max - t_resp - 40e-6 - 1.3e-3 - t_rise
    assert abs(_num(r"while those last two stay under ([\d.]+) ms", text_) - round(budget * 1e3, 3)) < 1e-9 and budget > 0
    assert "board B draws no LSE crystal" in text_ and "FW-B23's hold check takes the LSI (5e, W152-1): yes" in text_


def t_reader_reads_fail_on_a_part_not_fitted():
    """W150's F5: ohms() refuses an empty value (SystemExit, which the band reader turns into FAIL) instead of raising IndexError; the
    two functions are taken from the script's own source with ast (the script is not imported, so no extraction site is reached here)"""
    ns = {"re": re, "sys": sys}
    for node in ast.parse(open(need(SCRIPT, "the HO-E script"), encoding="utf-8").read()).body:
        if isinstance(node, ast.FunctionDef) and node.name in ("refuse", "ohms"):
            exec(compile(ast.Module([node], []), SCRIPT, "exec"), ns)
    assert "ohms" in ns and "refuse" in ns
    err = sys.stderr
    try:
        sys.stderr = open(os.devnull, "w")
        for bad in ("", "  "):
            try:
                ns["ohms"](bad)
            except SystemExit as e:
                assert e.code == 2
            else:
                raise AssertionError("ohms(%r) did not refuse" % bad)
    finally:
        sys.stderr.close()
        sys.stderr = err
    assert ns["ohms"]("390R 1%") == 390.0 and ns["ohms"]("39.2k 0.1% 25ppm") == 39200.0
    src = open(SCRIPT, encoding="utf-8").read()
    assert "if not CHK.value(nl, rs):" in src and "is not fitted: the hold stage's RESET reaches no NRST" in src


def t_revision_codes_quoted():
    """W150's F6: C3 cites ST ES0392 Rev 15 Table 2 (p.1) for the revision codes; Y and W excluded"""
    t = _txt(ST, "st-es0392-rev15.layout.p1.txt")
    assert "ES0392 - Rev 15 - September 2025" in t and "Table 2. Device variants" in t
    codes = dict((k, re.search(r"^\s+%s\s+(0x[0-9A-F]{4})\s*$" % re.escape(k), t, re.M).group(1)) for k in ("Y, W", "X", "V"))
    assert codes == {"Y, W": "0x1003", "X": "0x2001", "V": "0x2003"}, codes
    text_ = _out()
    assert "codes (ES0392 Rev 15 Table 2, p.1, W150's F6): marking V, REV_ID 0x2003; X, 0x2001; Y and W, 0x1003, which CON-017 (5) excludes" in text_
