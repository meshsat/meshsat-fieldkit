"""Layer 4 task L4A-59, record l9t5 (MESHSAT-1357, W140, 7 October 2026; v2/docs/records/l9t5/): HO-E's comparison of three approaches
(H-1 a hardware-forced voltage scale, H-2 a firmware bound with an independent ending, H-3 a thermal-headroom part or heat path), the
selection SESSION W140-1 and its draft apply_gen_sch_b_vcoremon.py, held as predicates on what l9t5_hoe.py computes and on the files
of the task.

The predicates: the committed l9t5_hoe.out is what the script prints and every input it pins is present at the sha256 it names; every
predicate the script states reads yes (fourteen); the sentences H-1 rests on are re-found here in the makers' committed texts, page by
page, and no option-byte field selects a voltage scale; H-3's arithmetic is re-solved from Table 119 and Table 222; the monitor's
threshold band is re-solved from the TPS37's printed rows and the draft's own values and lies between VOS3's top and VOS1's bottom;
the draft applies to a copy of the tree's generator, refuses a second application and the tree's own generator, and leaves the tree
byte for byte; the six mutations read FAIL; the acceptance reads CONDITIONAL and never met; the page carries the selection's authority
fields and claims no closure; the task's new files carry no long dash, no private path and no claim word outside quotations. These are
software predicates on a DRAFT and its arithmetic: they establish no property of any board, monitor or controller, and nothing in the
kit has been built or measured.
"""
import ast
import hashlib
import importlib.util
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
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
ST = os.path.join(ROOT, "v2", "vendor", "st", "pdftext")
TI = os.path.join(ROOT, "v2", "vendor", "ti", "pdftext")
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
    assert len(rows) == 14, rows
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
    assert min(ja) > 2 * need_en
    assert "VERDICT H-3: FAILS on printed figures" in text_


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
        assert new.count("_VMON") >= 3 and "TPS37" in new and "IOC%s_MONRST" in new
        r2 = subprocess.run([sys.executable, "-B", DRAFT, cp, "--write"], capture_output=True)
        assert r2.returncode == 3 and b"already applied" in r2.stderr
    r3 = subprocess.run([sys.executable, "-B", DRAFT, GEN_B, "--write"], capture_output=True)
    assert r3.returncode == 3 and b"NOT RELEASED" in r3.stderr
    assert hashlib.sha256(open(GEN_B, "rb").read()).hexdigest() == before, "the tree's generator changed"
    dm = _draft()
    assert len(dm.ADDS) == 15 and len(set(dm.ADDS)) == 15


def t_mutations_fail_and_the_draft_reads_drawn():
    text_ = _out()
    sec = text_.split("the mutations (each must FAIL the reading):")[1].split("the draft on the tree's generator")[0]
    rows = [l for l in sec.splitlines() if l.strip()]
    assert len(rows) == 6 and all(l.rstrip().endswith("FAIL") for l in rows), rows
    assert "V): DRAWN; before the draft: FAIL" in text_
    assert "DRAWN; the two netlists identical" in text_
    assert "added 15: C810, C811, C812, R810, R811, R812, R820, R821, R822, R830, R831, R832, U810, U820, U830; removed 0" in text_


def t_acceptance_conditional_never_met():
    text_ = _out()
    acc = text_.split("6. THE ACCEPTANCE")[1].split("7. THE SELECTION")[0]
    for s_ in ("S-c", "S-d", "S-e"):
        row = [l for l in acc.splitlines() if l.strip().startswith(s_)][0]
        assert row.rstrip().split("  ")[-1].strip().startswith("CONDITIONAL"), row
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
    for s_ in ("H-1", "H-2", "H-3", "DROPS OUT", "FAILS", "PROVISIONAL", "CONDITIONAL", "SESSION W140-1", "authority_why", "ruled_by",
               "ruled_on", "reversed_by", "apply_gen_sch_b_vcoremon.py", "NOT APPLIED", "S1", "S2", "S3", "S4", "L4A-100", "L4REG-F7",
               "0.5704 A", "76.0 C/W", "p.560", "p.279", "p.344", "NOT CLOSED"):
        assert s_ in page, s_
    for bad in ("HO-E CLOSED", "desk acceptance MET", "hardware bar on VOS0 exists", "ACCEPTANCE: MET"):
        assert bad not in page, bad
    text_ = _out()
    for figure in re.findall(r"\b\d+\.\d+ (?:C/W|K/W|us)\b", page):
        assert figure in text_, "the page's figure %r is not in l9t5_hoe.out" % figure


def t_record_hygiene():
    files = [SCRIPT, OUT, DRAFT, PAGE, os.path.abspath(__file__)]
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
