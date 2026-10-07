"""Record l9t5, round 10 (MESHSAT-1357, 7 October 2026, W151; v2/docs/records/l9t5/T10-ROUND10.md): Layer 4 tasks L4A-57 (RE-6 and
RE-7's acceptance on the selected regulator stage) and L4A-61 (row (b)'s propagation), held as predicates on l9t5_t10.out section 11a,
l9t5_connected.out section 11a, the three apply scripts and the page, with the MUTANTS the brief names, each of which must FAIL: a
TYPICAL figure used as a bound (the limiter's response time, the regulator's ground current) and a guideline used as the site's theta.

The predicates: section 11a's six round 10 predicates and the connected section's three read yes; the stage's figures are re-solved
here from the printed values the output names and TI's printed limiter equations (IOS's band with RILIM's 1 %, the junction at constant
maximum dissipation, the ground current 125 C admits, the theta 125 C needs, E-17's Zth limit, T10-A3 on both dropout readings) and agree
with the output; the judge holds on its rows and FAILS each mutant; the connected window is re-solved from the figures its section names;
the contract script applies once after t10's and canq's on a scratch copy, refuses a second time, refuses without canq's and refuses the
tree's page, keeps W139's stop and W143's DAR text, re-parses, and places FW-B24 after HO-E's FW-B23 when one is present; the IOHA script
adds rows 21 to 24 once and refuses twice; the ledger script adds its table once, its citations read what they cite, and
test_remeng's predicates hold on the applied copy; the page carries the output's figures; the round's files carry no long dash, no
private path and no claim word outside quotations. These are software predicates on DRAFTS and a desk MODEL: they establish no property
of any board, regulator, limiter or controller, and nothing in the kit has been built, bought, powered or measured.

Runs under the suite's runner (`env -C v2/ecad/tools python3 tests/run.py test_l9t5_rowb.`); a few seconds (it runs no generator; the
outputs' reproduction is test_l9t5's)."""
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
T10 = os.path.join(REC, "l9t5_t10.py")
T10_OUT = os.path.join(REC, "l9t5_t10.out")
CON = os.path.join(REC, "l9t5_connected.py")
CON_OUT = os.path.join(REC, "l9t5_connected.out")
PAGE = os.path.join(REC, "T10-ROUND10.md")
A_T10 = os.path.join(REC, "apply_hw_fw_contract_t10.py")
A_CANQ = os.path.join(REC, "apply_hw_fw_contract_canq.py")
A_ROWB = os.path.join(REC, "apply_hw_fw_contract_rowb.py")
A_IOHA = os.path.join(REC, "apply_ioha_fmea_rowb.py")
A_REM = os.path.join(REC, "apply_remeng_rowb.py")
CONTRACT = os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md")
IOHA = os.path.join(ROOT, "v2", "docs", "ARCH-PCB-B-IOHA.md")
LEDGER = os.path.join(ROOT, "v2", "docs", "records", "l4close", "REMAINING-ENGINEERING.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
# TI SLVS841F 9.5.1's printed equations (W135's reading, record l4reg's inputs): IOSmin = 25230 / R^1.016, IOSmax = 22980 / R^0.94 (mA,
# R in kOhm); with a tested row at the nominal resistor, the resistor's 1 % moves the band by the exponents (W135's rule)
EXP_MIN, EXP_MAX, R_TOL = 1.016, 0.94, 0.01


def _text(p):
    return open(need(p, os.path.basename(p)), encoding="utf-8").read()


def _sec(path, head, end):
    t = _text(path)
    assert head in t, "%s carries no %r" % (os.path.basename(path), head[:40])
    return t.split(head, 1)[1].split(end, 1)[0]


def _t11a():
    if "t" not in _C:
        _C["t"] = _sec(T10_OUT, "\n11a. ROUND 10", "\n12. THE PREDICATES")
    return _C["t"]


def _c11a():
    if "c" not in _C:
        _C["c"] = _sec(CON_OUT, "\n11a. ROW (b)'S DRAFTS", "\n12. THE PREDICATES")
    return _C["c"]


def _f(pat, s, n=1, flags=re.S):
    m = re.search(pat, s, flags)
    assert m, "not found: %s" % pat[:70]
    return float(m.group(n))


def _mod(path, name):
    if name not in _C:
        sp = importlib.util.spec_from_file_location(name, need(path, os.path.basename(path)))
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C[name] = m
    return _C[name]


def _run(script, *args):
    return subprocess.run([sys.executable, "-B", script] + list(args), cwd=ROOT, capture_output=True)


def t_the_round_10_predicates_read_yes():
    pred = _text(T10_OUT).split("12. THE PREDICATES", 1)[1]
    r10 = [l for l in pred.splitlines() if l.strip().startswith("round 10")]
    assert len(r10) == 6 and all(l.rstrip().endswith(" yes") for l in r10), r10
    cp = _text(CON_OUT).split("12. THE PREDICATES", 1)[1]
    rb = [l for l in cp.splitlines() if l.strip().startswith("row (b) (L4A-61)")]
    assert len(rb) == 3 and all(l.rstrip().endswith(" yes") for l in rb), rb
    assert "L4A-57: DONE AS CONDITIONAL on E-17." in _t11a()


def t_the_stage_figures_are_re_solved_from_the_printed_rows():
    """the band, the junction at constant maximum dissipation, IGND's admitted range, the theta 125 C needs, E-17's Zth limit and T10-A3"""
    s = " ".join(_t11a().split())
    m = re.search(r"\bios49 ([\d.]+) / [\d.]+ / ([\d.]+) PRINTED SLVS841F 7\.5", s)
    assert m, "the tested IOS row at 49.9 kOhm"
    lo_r, hi_r = float(m.group(1)), float(m.group(2))
    lo, hi = lo_r * (1 + R_TOL) ** -EXP_MIN, hi_r * (1 - R_TOL) ** -EXP_MAX
    assert abs(lo - _f(r"IOS ([\d.]+) to [\d.]+ A", s)) < 6e-5 and abs(hi - _f(r"IOS [\d.]+ to ([\d.]+) A", s)) < 6e-5, (lo, hi)
    rja = float(re.search(r"\brja ([\d.]+) PRINTED SBVS067W 5\.4", s).group(1))
    acc = float(re.search(r"\bacc ([\d.]+) PRINTED", s).group(1))
    hi14 = _f(r"pre-regulator's top ([\d.]+) V", s)
    air = _f(r"in still air at ([\d.]+) C", s)
    drop = hi14 - 3.3 * (1 - acc)
    p0 = drop * hi
    tj0 = air + rja * p0
    assert abs(drop - _f(r"the drop ([\d.]+) V, [\d.]+ W at IGND = 0", s)) < 6e-5
    assert abs(tj0 - _f(r"the junction ([\d.]+) C at IGND = 0", s)) < 0.06 and tj0 < 125.0
    g = ((125.0 - air) / rja - p0) / (3.3 * (1 - acc))
    assert abs(g * 1e3 - _f(r"every IGND up to ([\d.]+) mA", s)) < 0.06 and g > 0
    assert "IGND: TI prints the ground current as TYPICAL only" in s and "ignd 0.00088 TYPICAL" in s
    need_th = (125.0 - air) / p0
    assert abs(need_th - _f(r"with IGND = 0: ([\d.]+) C/W", s)) < 0.06 and need_th > rja
    zth = (150.0 - tj0) / (hi14 * hi)
    assert abs(zth - _f(r"Zth\(10 ms\) at most ([\d.]+) C/W", s)) < 0.06
    # T10-A3: the 1 A row as the bound and the INFERRED linear dropout, against the available input the output prints
    at = _f(r"at IOSmax on all three: ([\d.]+) V against", s)
    vdo = float(re.search(r"\bvdo1a ([\d.]+) PRINTED", s).group(1))
    nd_b, nd_i = 3.3 * (1 + acc) + vdo, 3.3 * (1 + acc) + vdo * hi
    assert abs(nd_b - _f(r"at IOSmax on all three: [\d.]+ V against ([\d.]+) V on the 1 A row", s)) < 6e-5
    assert abs(nd_i - _f(r"and against ([\d.]+) V on the INFERRED linear dropout", s)) < 6e-5
    assert at >= nd_b >= nd_i
    # the window: IOSmin over the largest served row, less row (b)'s enabled set
    served = _f(r"over the largest served ([\d.]+) A by", s)
    en = _f(r"taken at 3 times \(ASSUMPTION\): at most ([\d.]+) A", s)
    assert abs((lo - served - en) - _f(r"the window after it ([\d.]+) A", s)) < 1.5e-4 and lo - served - en > 0


def t_the_judge_holds_and_fails_each_mutant():
    m = _mod(T10, "l9t5_t10_rowb_test")
    s = " ".join(_t11a().split())
    st = {"ios_lo": (0.4702, "PRINTED", "x"), "ios_hi": (0.5704, "PRINTED", "x"), "rja": (76.0, "PRINTED", "x"), "ron": (0.135, "PRINTED", "x"),
          "t_latch": ((0.005, 0.0075, 0.010), "PRINTED", "x"), "vdo1a": (0.25, "PRINTED", "x"), "acc": (0.015, "PRINTED", "x"),
          "iout": (1.0, "PRINTED", "x"), "icl_min": (1.05, "PRINTED", "x"), "vin_max": (5.5, "PRINTED", "x"), "lim_rja": (182.6, "PRINTED", "x"),
          "tj_op": (125.0, "PRINTED", "x"), "short": ("Indefinite", "PRINTED", "x")}
    R = {"served": {"S3'": 0.4240}, "air": 76.25, "drop": 0.8669, "tj": 125.0, "vout_lo": 3.2505, "cm_i": 0.50, "vin_hi": 4.1174,
         "avail": lambda i_s, i_l, r: 3.6082 + 0.135 * 0.5704 - r * i_s, "u601": 3.0, "vh": 10.0}
    v, rows = m.r10_judge(st, R)
    assert v == "HOLDS" and [r[0] for r in rows] == ["K%d" % i for i in range(10)], rows
    mutants = {"tIOS TYPICAL as the response bound": dict(st, t_resp=(2e-6, "TYPICAL", "x")),
               "IGND TYPICAL as its maximum": dict(st, ignd_max=(0.00088, "TYPICAL", "x")),
               "Figure 7-9's guideline as the theta": dict(st, rja=(60.0, "GUIDELINE", "x")),
               "the old regulator's theta": dict(st, rja=(184.0, "PRINTED", "x")),
               "a band under the served peak": dict(st, ios_lo=(0.2274, "PRINTED", "x"), ios_hi=(0.3002, "PRINTED", "x")),
               "a limit over the regulator's 125 C current": dict(st, ios_hi=(0.80, "PRINTED", "x"))}
    for lab, mst in mutants.items():
        assert m.r10_judge(mst, R)[0] == "FAILS", lab
    for lab in ("a TYPICAL response time (tIOS) used as the response bound", "the TYPICAL ground current used as its maximum",
                "Figure 7-9's guideline used as the site's theta", "the AP2112K's 184 C/W on the stage", "RILIM at 102 kOhm"):
        assert re.search(r"mutated, %s[^:]*: FAILS" % re.escape(lab), s), lab
    for lab in ("RILIM at 102 kOhm (a band under the served peak)", "the AP2112K-3.3 back on U40", "U40 ordered without M3"):
        assert re.search(r"mutated, %s[^:]*: FAIL\b" % re.escape(lab), s), lab
    assert "round 6's rail trip absent: DRAWN" in s


def t_the_connected_window_is_re_solved():
    s = " ".join(_c11a().split())
    w0 = _f(r"and ([\d.]+) A after row \(b\)'s enabled set", s)
    canen = _f(r"record l4canen ([\d.]+) A with canmb's", s)
    hod = _f(r"record l4hod ([\d.]+) mA", s) / 1e3
    r6 = _f(r"over round 6's ([\d.]+) A less its limiters' pull-ups", s)
    pu = _f(r"less its limiters' pull-ups ([\d.]+) mA", s) / 1e3
    add = canen + hod - (r6 - pu)
    assert abs(add - _f(r"at most ([\d.]+) A \(record l4canen", s)) < 6e-5
    win = _f(r"the window ([+-][\d.]+) A, no served state limited", s)
    assert abs((w0 - add) - win) < 1.5e-4 and win > 0
    assert "THE WORST-CASE MARGIN ROW RESTATED" in s and "CONDITIONAL on E-17" in s
    for item in (6, 7, 5, 17):
        assert re.search(r"item +%d \([^)]*, NOT CLOSED\):" % item, s), item


def _compose_contract(d, with_hoe=False):
    p = os.path.join(d, "HW-FW-CONTRACT.md")
    shutil.copy(CONTRACT, p)
    for a in (A_T10, A_CANQ):
        r = _run(a, p, "--write")
        assert r.returncode == 0, (os.path.basename(a), r.stderr.decode()[-200:])
    if with_hoe:
        # a stand-in for HO-E's rows (fnd/l4hoe's own text is not in this tree): FW-B23 and V-B24 with their cell counts
        t = open(p, encoding="utf-8").read()
        b22 = [l for l in t.splitlines(True) if l.startswith("| FW-B22 |")][0]
        v23 = [l for l in t.splitlines(True) if l.startswith("| V-B23 |")][0]
        t = t.replace(b22, b22 + "| FW-B23 | stand-in | stand-in | stand-in | V-B24 | stand-in |\n")
        t = t.replace(v23, v23 + "| V-B24 | FW-B23 | stand-in |\n")
        t = t.replace("(FW-B01 to FW-B22)\n", "(FW-B01 to FW-B23)\n")
        open(p, "w", encoding="utf-8").write(t)
    return p


def t_the_contract_rows_apply_once_after_canq():
    tree_before = _text(CONTRACT)
    with tempfile.TemporaryDirectory(prefix="t_rowb_") as d:
        bare = os.path.join(d, "bare.md")
        shutil.copy(CONTRACT, bare)
        assert _run(A_ROWB, bare, "--write").returncode == 3           # t10's and canq's rows absent
        only = os.path.join(d, "t10only.md")
        shutil.copy(CONTRACT, only)
        assert _run(A_T10, only, "--write").returncode == 0
        assert _run(A_ROWB, only, "--write").returncode == 3           # canq's absent
        p = _compose_contract(d)
        before = open(p, encoding="utf-8").read()
        r = _run(A_ROWB, p, "--write")
        assert r.returncode == 0, r.stderr.decode()[-300:]
        t = open(p, encoding="utf-8").read()
        assert _run(A_ROWB, p, "--write").returncode == 3              # a second time
        assert open(p, encoding="utf-8").read() == t
        b = [l.split(" | ")[0][2:] for l in t.splitlines() if l.startswith("| FW-B")]
        assert b == ["FW-B%02d" % i for i in range(1, 23)] + ["FW-B24"], b[-3:]
        v = [l.split(" | ")[0][2:] for l in t.splitlines() if l.startswith("| V-B")]
        assert v[-5:] == ["V-B20", "V-B21", "V-B22", "V-B23", "V-B25"], v[-5:]
        b20 = [l for l in t.splitlines() if l.startswith("| FW-B20 |")][0]
        b21 = [l for l in t.splitlines() if l.startswith("| FW-B21 |")][0]
        b22 = [l for l in t.splitlines() if l.startswith("| FW-B22 |")][0]
        vb23 = [l for l in t.splitlines() if l.startswith("| V-B23 |")][0]
        assert "TPS73733DCQRM3" in b20 and "AP2112K" not in b20 and "rail trip" in b20 and "TIM3" in b20 and "BOR at level 2" in b20
        assert "transmit-share limiter (`apply_gen_sch_b_iocguard.py`" not in b21 and "2-of-2 vote" in b21
        assert "more than 3 windows (300 ms, FW-B22's loss count" in b21                     # W139's stop kept
        assert "ES0392 Rev 15 2.24.5's printed workaround (page 48/73" in b22                  # W143's DAR text kept
        assert "never on a peer under the in-service limiter test (FW-B24)" in b22
        assert "0.30 A" not in vb23 and "WITHDRAWN" in vb23 and "0.4702 and 0.5704 A" not in vb23 and "0.4702 to 0.5704 A" in vb23
        assert "| 4 (row b) |" in t.rstrip("\n").splitlines()[-1]
        # only the rows this draft names changed
        changed = {l.split(" | ")[0] for l in set(t.splitlines()) ^ set(before.splitlines()) if l.startswith("| ")}
        assert changed <= {"| FW-B20", "| FW-B21", "| FW-B22", "| FW-B24", "| V-B20", "| V-B21", "| V-B23", "| V-B25", "| 4 (row b)"}, changed
        # with HO-E's pair present, FW-B24 and V-B25 follow it
        d2 = os.path.join(d, "hoe")
        os.mkdir(d2)
        p2 = _compose_contract(d2, with_hoe=True)
        assert _run(A_ROWB, p2, "--write").returncode == 0
        t2 = open(p2, encoding="utf-8").read()
        assert [l.split(" | ")[0][2:] for l in t2.splitlines() if l.startswith("| FW-B")][-3:] == ["FW-B22", "FW-B23", "FW-B24"]
        assert [l.split(" | ")[0][2:] for l in t2.splitlines() if l.startswith("| V-B")][-3:] == ["V-B23", "V-B24", "V-B25"]
    assert _run(A_ROWB).returncode == 3 and _text(CONTRACT) == tree_before   # the tree's page: refused, untouched


def t_the_ioha_rows_apply_once():
    tree_before = _text(IOHA)
    with tempfile.TemporaryDirectory(prefix="t_rowb_") as d:
        p = os.path.join(d, "IOHA.md")
        shutil.copy(IOHA, p)
        assert _run(A_IOHA, p, "--write").returncode == 0
        t = open(p, encoding="utf-8").read()
        assert _run(A_IOHA, p, "--write").returncode == 3 and open(p, encoding="utf-8").read() == t
        sec = t.split("\n## 12. FMEA\n", 1)[1].split("\n## 13.", 1)[0]
        nums = [int(l.split(" | ")[0][2:]) for l in sec.splitlines() if re.match(r"^\| \d+ \|", l)]
        assert nums == list(range(1, 25)), nums
        old = tree_before.split("\n## 12. FMEA\n", 1)[1].split("\n## 13.", 1)[0]
        assert all(l in sec for l in old.splitlines() if re.match(r"^\| \d+ \|", l))          # rows 1 to 20 word for word
        for w in ("L9T5-F21", "1.310 ms", "0.4702 to 0.5704 A", "3602.341 s", "2.60 s", "V-B25"):
            assert w in sec, w
        assert t.split("\n## 12. FMEA\n", 1)[0] == tree_before.split("\n## 12. FMEA\n", 1)[0]
    assert _run(A_IOHA).returncode == 0 and _text(IOHA) == tree_before                    # --check only on the tree


def t_the_ledger_table_applies_once_and_remeng_holds():
    tree_before = _text(LEDGER)
    rem = _mod(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_remeng.py"), "test_remeng_on_rowb")
    with tempfile.TemporaryDirectory(prefix="t_rowb_") as d:
        p = os.path.join(d, "REMAINING-ENGINEERING.md")
        shutil.copy(LEDGER, p)
        assert _run(A_REM, p, "--write").returncode == 0
        t = open(p, encoding="utf-8").read()
        assert _run(A_REM, p, "--write").returncode == 3 and open(p, encoding="utf-8").read() == t
        t10 = _text(T10_OUT).splitlines()
        con = _text(CON_OUT).splitlines()
        sub = t.split("**Row (b)'s drafts restate six of these claims", 1)[1].split("\n## 5. Summary", 1)[0]
        cites = re.findall(r"\[(T10|CON):(\d+)(?:-(\d+))?\]", sub)
        assert len(cites) == 10, cites
        for k, s_, e_ in cites:
            lines = (t10 if k == "T10" else con)[int(s_) - 1:int(e_ or s_)]
            assert lines and ("11a" in " ".join(lines) or lines[0].startswith("   (") or lines[0].startswith("     ")), (k, s_)
        assert any("L4A-57: DONE AS CONDITIONAL on E-17." in l for k, s_, e_ in cites if k == "T10"
                   for l in t10[int(s_) - 1:int(e_ or s_)])
        # test_remeng's predicates on the applied copy (its module reads its LEDGER path; pointed at the copy here, then restored)
        old, cache = rem.LEDGER, dict(rem._C)
        try:
            rem.LEDGER = p
            rem._C.clear()
            ran = 0
            for n in sorted(dir(rem)):
                if n.startswith("t_") and callable(getattr(rem, n)):
                    getattr(rem, n)()
                    ran += 1
            assert ran >= 17, ran
        finally:
            rem.LEDGER = old
            rem._C.clear()
            rem._C.update(cache)
    assert _run(A_REM).returncode == 0 and _text(LEDGER) == tree_before                   # --check only on the tree


def t_the_page_carries_the_outputs_figures():
    pg = " ".join(_text(PAGE).split())
    s = " ".join(_t11a().split())
    for pat in (r"the junction ([\d.]+) C at IGND = 0", r"every IGND up to ([\d.]+) mA", r"with IGND = 0: ([\d.]+) C/W",
                r"Zth\(10 ms\) at most ([\d.]+) C/W", r"the window after it ([\d.]+) A"):
        v = re.search(pat, s).group(1)
        assert v in pg, (pat, v)
    assert re.search(r"the window ([+-][\d.]+) A", " ".join(_c11a().split())).group(1) in pg
    assert pg.startswith("**ROUND 10") and "DONE AS CONDITIONAL on E-17" in pg and "NOT DONE:" in pg and "NEXT:" in pg
    for w in ("W151-1", "authority SESSION", "ruled_by W151", "reversed_by none", "E-17, named", "Specimen", "Pass limits"):
        assert w in pg, w


def t_record_hygiene():
    files = [PAGE, A_ROWB, A_IOHA, A_REM, os.path.abspath(__file__), T10, T10_OUT, CON, CON_OUT]
    for p in files:
        t = _text(p)
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p != os.path.abspath(__file__):
            mm = CLAIM.search(re.sub(r"\"[^\"\n]*\"", "", t))
            assert not mm, "a claim word %r in %s" % (mm.group(0), os.path.basename(p))


# pytest aliases
for _n, _f_ in list(globals().items()):
    if _n.startswith("t_") and callable(_f_):
        globals()["test_" + _n[2:]] = _f_
