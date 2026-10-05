"""Record efuse (task T12, MESHSAT-1357, 5 October 2026; v2/docs/records/efuse/): every eFuse and current-limit setting in the
schematic generators checked against its exact part's sheet, driven by finding SDR3-F04 on board B's U23.

The predicates: the committed .out is what the script prints (where the held-back sheets and pdftotext are present); every quote
is found in its sheet's own text; every TPS2596-family setting a generator draws on this tree is inside the printed 453 to 7869
Ohm, or its instance carries a finding this record registers OPEN; the band function refuses a setting outside the printed range
and passes one inside it (fixtures, so the property holds whether or not the tree's defects are corrected); the corrected value
of each draft holds (b) and (c) on its printed band; each draft checks, applies once on a scratch copy, refuses a second run and
refuses to write the tree's own generator; the netlist check reads PASS on the corrected netlist and FAIL on its mutations; the
page carries no em or en dash and no claim word, and its key figures are the output's. No KiCad: generator text and the
generators' own part tables on scratch copies; the tree is never written."""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "efuse")
SCRIPT = os.path.join(REC, "efuse_check.py")
OUT = os.path.join(REC, "efuse_check.out")
PAGE = os.path.join(REC, "EFUSE-SETTINGS.md")
DRAFTS = [os.path.join(REC, "apply_gen_sch_b_u23ilm.py"), os.path.join(REC, "apply_gen_sch_b_u24ilm.py")]
DRAFT_A = os.path.join(REC, "apply_gen_sch_a_u23ilm.py")
ASSEMBLY_DRAFT = os.path.join(REC, "apply_assembly_rb_pads.py")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
_C = {}


def _M():
    if "m" not in _C:
        need(SCRIPT, "record efuse's check script")
        sp = importlib.util.spec_from_file_location("efuse_check_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _C["m"] = m
    return _C["m"]


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _have_all_sheets():
    m = _M()
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is not on this host: the quotes cannot be read")
    absent = [k for k, v in m.SHEETS.items() if not os.path.isfile(os.path.join(ROOT, v[0]))]
    if absent:
        raise Skip("held-back sheets absent (%s): fetch with v2/docs/records/l4e11/fetch_held_back.py" % ", ".join(sorted(absent)))


def t_the_committed_output_is_what_the_script_prints():
    _have_all_sheets()
    before = _sha(GEN_B)
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "efuse_check.out is not what efuse_check.py prints; regenerate it with _bin/regen_out.py"
    assert _sha(GEN_B) == before, "the script wrote into the tree"
    t = r.stdout.decode()
    for s in ("quotes: 62 VERIFIED, 0 SHEET ABSENT, 0 NOT FOUND", "unregistered defects: 0",
              "the netlist reading and its mutations: every check reads as required",
              "the netlist reading and its mutations (board A): every check reads as required",
              "every EFUSE TPS2596 setting inside the range: YES", "EF-F01  DESIGN DEFECT, OPEN", "EF-F02  DESIGN DEFECT, OPEN",
              "EF-F03  DESIGN DEFECT, OPEN", "round 2: board B's full composition regenerates without a dropped draft: YES; the ASSEMBLY.md "
              "draft applies once: YES", "round 2: every EFUSE TPS2596 setting's corners inside the range: YES"):
        assert s in t, s
    # V6-m3, the regression: round 1 ran board B without fans12 because its chain stopped; the full chain runs now
    assert "THE COMPOSED GENERATOR REFUSES" not in t and "board B  l9t5/apply_gen_sch_b_iocpre.py" in t


def t_every_quote_is_in_its_sheet_and_the_committed_sheets_are_present():
    m = _M()
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is not on this host")
    v = m.verify_quotes()
    for qid, (key, _w, _q) in m.QUOTES.items():
        held = m.SHEETS[key][2]
        assert v[qid] == "VERIFIED" or (held and v[qid] == "SHEET ABSENT"), "%s reads %s" % (qid, v[qid])


def t_the_printed_figures_parse_as_the_maker_prints_them():
    F = _M().figures()
    assert F["t96_rilm"] == (453.0, 7869.0) and F["t96_range"] == (0.125, 2.0) and abs(F["t96_acc"] - 0.104) < 1e-12
    assert F["t96_eq"] == (903.0, 0.0112) and F["t96_imax"] == 2.0 and abs(F["t96_ron"] - 0.131) < 1e-12
    rows = {r[0]: r[1:4] for r in F["t96_rows"]}
    assert rows == {7870.0: (0.113, 0.125, 0.139), 3830.0: (0.224, 0.247, 0.269), 909.0: (0.949, 1.005, 1.051), 453.0: (1.83, 2.004, 2.147)}
    assert F["t61_rs"] == (0.255, 0.25) and F["l69_vcl"] == (0.0485, 0.055, 0.0615) and F["t65_ios"] == (1.2, 1.55, 1.9)
    assert F["c_usb3a"] == 1.8 and F["c_idc16"] == 1.0 and F["l_rb_dc"] == 0.5 and F["l_lime_w"] == 4.5 and F["l_lime_host"] == 0.9


def t_the_band_refuses_a_setting_outside_the_printed_range():
    m = _M(); F = m.figures()
    for r in (301.0, 440.0, 8200.0, 10000.0):
        basis, lo, nom, hi, _n = m.t96_band(F, r, 0.01, 100.0)
        assert lo is None and hi is None and basis.startswith("NONE"), (r, basis)
    for r, rowq in ((453.0, "T96_ROW_453"), (909.0, "T96_ROW_909"), (3830.0, "T96_ROW_3830")):
        basis, lo, nom, hi, _n = m.t96_band(F, r, 0.01, 100.0)
        assert basis.endswith(rowq) and lo < nom < hi, (r, basis)
    basis, lo, nom, hi, _n = m.t96_band(F, 750.0, 0.01, 100.0)
    assert basis.startswith("PRINTED RANGE-WIDE") and abs(nom - (903 / 750 + 0.0112)) < 1e-12
    assert abs(lo - (903 / (750 * 1.01 * 1.006) + 0.0112) * 0.896) < 1e-9 and abs(hi - (903 / (750 * 0.99 * 0.994) + 0.0112) * 1.104) < 1e-9


def _drawn_instances(gen_text, board, d, tag):
    m = _M()
    p = os.path.join(d, tag + ".py"); open(p, "w", encoding="utf-8").write(gen_text)
    table = m.table_of(p, os.path.join(d, tag + ".net"))
    return m.instances(table, board), table


def t_every_drawn_setting_is_inside_its_range_or_registered_open():
    """the property on the tree as it is: a TPS2596-family setting outside 453 to 7869 Ohm fails this test unless its instance
    carries a finding this record registers OPEN (EF-F01, EF-F02); a corrected instance passes it either way"""
    m = _M(); F = m.figures()
    with tempfile.TemporaryDirectory() as d:
        for b in "abcdep":
            insts, _t = _drawn_instances(open(os.path.join(TOOLS, "gen_sch_%s.py" % b), encoding="utf-8").read(), b, d, b)
            for i in insts:
                if i["family"] != "tps2596":
                    continue
                assert len(i["setting"]) == 1, (b, i["ref"], i["setting"])
                r = m.ohms(i["setting"][0]["value"])[0]
                inside = F["t96_rilm"][0] <= r <= F["t96_rilm"][1]
                f = m.FINDINGS.get(("DRAWN", b, i["ref"]))
                assert inside or (f and f[2] == "OPEN"), "board %s %s: %g Ohm outside 453 to 7869 Ohm with no OPEN finding" % (b.upper(), i["ref"], r)


def t_a_mutated_generator_leaves_the_range_and_is_caught():
    m = _M(); F = m.figures()
    src = open(GEN_B, encoding="utf-8").read()
    old = '"R43", "R44", "R45", "R46", "C62"], "301R 1% (ILM: 3.0 A)")'
    assert src.count(old) == 1
    with tempfile.TemporaryDirectory() as d:
        for val, ok in (("8.2k 1% (ILM: 0.12 A)", False), ("1.21k 1% (ILM: 0.76 A)", True)):
            insts, table = _drawn_instances(src.replace(old, old.replace("301R 1% (ILM: 3.0 A)", val)), "b", d, "mut")
            i = next(x for x in insts if x["ref"] == "U24")
            m.judge(i, F, m.meta(F, m.l9_loads()), m.meta_family(F), m.catalogue(), table.get("intent"), table, m.lcsc_map())
            assert (i["verdict"] == "PASS") == ok, (val, i["verdict"], i["a"], i["b"], i["c"])


def t_each_draft_checks_applies_once_and_refuses_the_tree():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "gen_sch_b.py"); shutil.copy(GEN_B, p)
        before = _sha(GEN_B)
        for s in DRAFTS:
            r = subprocess.run([sys.executable, "-B", s, p], capture_output=True)
            assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-200:]
            assert subprocess.run([sys.executable, "-B", s, p, "--write"], capture_output=True).returncode == 0
            r2 = subprocess.run([sys.executable, "-B", s, p, "--write"], capture_output=True)
            assert r2.returncode == 3 and b"already applied" in r2.stderr
            r3 = subprocess.run([sys.executable, "-B", s, GEN_B, "--write"], capture_output=True)
            assert r3.returncode == 3 and b"NOT RELEASED" in r3.stderr, r3.stderr.decode()[-200:]
        assert _sha(GEN_B) == before
        text = open(p, encoding="utf-8").read()
        assert '"750R 1% (ILM: 1.2 A)");' in text and '"1.21k 1% (ILM: 0.76 A)");' in text and "301R 1% (ILM: 3.0 A)" not in text
        compile(text, p, "exec")


def t_the_corrected_values_hold_b_and_c_on_their_printed_bands():
    m = _M(); F = m.figures(); M = m.meta(F, m.l9_loads())
    for ref, r in (("U23", 750.0), ("U24", 1210.0)):
        basis, lo, nom, hi, _n = m.t96_band(F, r, 0.01, 100.0)
        need_ = max(x[1] for x in M[("b", ref)]["demand"])
        cap = min([x[1] for x in M[("b", ref)]["down"]] + [F["t96_imax"]])
        assert basis.startswith("PRINTED") and lo >= need_ and hi <= cap, (ref, lo, hi, need_, cap)
    assert abs(max(x[1] for x in M[("b", "U23")]["demand"]) - 0.9534) < 5e-5


def t_the_netlist_check_reads_the_correction_and_fails_its_mutations():
    m = _M(); F = m.figures(); M = m.meta(F, m.l9_loads())
    need23 = max(x[1] for x in M[("b", "U23")]["demand"]); cap23 = min(x[1] for x in M[("b", "U23")]["down"])
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "g.py"); shutil.copy(GEN_B, p)
        for s in DRAFTS:
            assert subprocess.run([sys.executable, "-B", s, p, "--write"], capture_output=True).returncode == 0
        net = os.path.join(d, "g.net"); m.table_of(p, net)
        txt = open(net, encoding="utf-8").read()
        assert m.check_ilm(txt, F, "U23", "R36", need23, cap23)[0]
        assert not m.check_ilm(m.mutate_value(txt, "R36", "301R 1% (ILM: 3.0 A)"), F, "U23", "R36", need23, cap23)[0]
        assert not m.check_ilm(m.mutate_value(txt, "R36", "560R 1% (ILM: 1.6 A)"), F, "U23", "R36", need23, cap23)[0]
        assert not m.check_ilm(m.mutate_far_pin(txt, "R36", "+5V_LIME"), F, "U23", "R36", need23, cap23)[0]


def t_round2_the_corners_rule_makes_453_a_defect_and_511_a_pass():
    """V6-m6: EF-F01's rule at the resistor's corners. On fixtures (a copy of board A's generator with R98 at each value): 453 Ohm, the
    recommended minimum itself, reads DEFECT (a) (its corners reach 445.8 Ohm); 511 Ohm reads PASS; the old reading (PASS, EDGE) fails."""
    m = _M(); F = m.figures()
    src = open(GEN_A, encoding="utf-8").read()
    old = '["C102", "R98", "R99", "R100", "R101", "C103"], "453R 1% (ILM: 2.0 A)"'
    assert src.count(old) == 1
    M = m.meta(F, m.l9_loads())
    with tempfile.TemporaryDirectory() as d:
        for val, want in (("453R 1% (ILM: 2.0 A)", "DEFECT (a)"), ("511R 1% (ILM: 1.8 A)", "PASS")):
            insts, table = _drawn_instances(src.replace(old, old.replace("453R 1% (ILM: 2.0 A)", val)), "a", d, "r98")
            i = next(x for x in insts if x["ref"] == "U23")
            m.judge(i, F, M, m.meta_family(F), m.catalogue(), table.get("intent"), table, m.lcsc_map())
            assert i["verdict"] == want, (val, i["verdict"], i["a"])
            assert "EDGE" not in i["a"]
    lo, hi = m.r_corners(453.0, 0.01, 100.0)
    assert round(lo, 1) == 445.8 and lo < F["t96_rilm"][0]
    b = m.t96_band(F, 511.0, 0.01, 100.0)
    assert (round(b[1], 4), round(b[2], 4), round(b[3], 4)) == (1.5684, 1.7783, 1.9949) and b[3] <= F["t96_imax"]


def t_round2_board_a_draft_reads_on_the_netlist_and_fails_its_mutations():
    m = _M(); F = m.figures(); M = m.meta(F, m.l9_loads())
    need_ = max(x[1] for x in M[("a", "U23")]["demand"]); cap = min([x[1] for x in M[("a", "U23")]["down"]] + [F["t96_imax"]])
    assert abs(need_ - 0.6858) < 5e-5 and cap == 2.0
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ga.py"); shutil.copy(GEN_A, p)
        before = _sha(GEN_A)
        assert subprocess.run([sys.executable, "-B", DRAFT_A, p, "--write"], capture_output=True).returncode == 0
        assert subprocess.run([sys.executable, "-B", DRAFT_A, p, "--write"], capture_output=True).returncode == 3
        r = subprocess.run([sys.executable, "-B", DRAFT_A, GEN_A, "--write"], capture_output=True)
        assert r.returncode == 3 and b"NOT RELEASED" in r.stderr and _sha(GEN_A) == before
        net = os.path.join(d, "ga.net"); m.table_of(p, net)
        txt = open(net, encoding="utf-8").read()
        assert m.check_ilm(txt, F, "U23", "R98", need_, cap)[0]
        for mut in (m.mutate_value(txt, "R98", "453R 1% (ILM: 2.0 A)"), m.mutate_value(txt, "R98", "2k 1% (ILM: 0.46 A)"),
                    m.mutate_far_pin(txt, "R98", "+5V_D8")):
            assert not m.check_ilm(mut, F, "U23", "R98", need_, cap)[0]


def t_round2_the_inside_air_rows_are_re_solved_and_the_assembly_draft_applies_once():
    """V6-m4: at L4-E12's 76.25 C the receptacle's full-span reading is 0.6874 A, under the LimeSDR's own 0.9534 A (no eFuse setting
    answers it: a vendor condition, PROVISIONAL), and the harness's 0.5995 A covers the RockBLOCK's 0.500 A but not U24's top 0.8496 A.
    V6-m5: U24's foot holds the RockBLOCK's default charge current and not the bridged one; the ASSEMBLY.md draft applies once."""
    import math
    m = _M(); F = m.figures()
    assert (F["t_usb3a"], F["t_idc16"], F["t_rib16"], round(F["air"], 2)) == (85.0, 105.0, 105.0, 76.25)
    usb = F["c_usb3a"] * math.sqrt((F["t_usb3a"] - F["air"]) / (F["t_usb3a"] - 25.0))
    har = F["c_idc16"] * math.sqrt((F["t_idc16"] - F["air"]) / (F["t_idc16"] - 25.0))
    assert round(usb, 4) == 0.6874 and round(har, 4) == 0.5995
    b23 = m.t96_band(F, 750.0, 0.01, 100.0); b24 = m.t96_band(F, 1210.0, 0.01, 100.0)
    assert usb < 0.9534 < b23[3] and F["l_rb_dc"] <= har < b24[3]
    assert b24[1] >= F["l_rb_chg"] and b24[1] < F["l_rb_chg_up"]
    out = open(OUT, encoding="utf-8").read()
    for s in ("0.6874 A at 76.25 C", "0.5995 A at 76.25 C", "against the load's own demand 0.9534 A: NOT COVERED", "PROVISIONAL (amendment 1)",
              "a build condition, the pads OPEN"):
        assert s in out, s
    with tempfile.TemporaryDirectory() as d:
        page = os.path.join(ROOT, "v2", "docs", "ASSEMBLY.md")
        cp = os.path.join(d, "ASSEMBLY.md"); shutil.copy(page, cp)
        before = _sha(page)
        assert subprocess.run([sys.executable, "-B", ASSEMBLY_DRAFT, cp], capture_output=True).returncode == 0 and _sha(cp) == before
        assert subprocess.run([sys.executable, "-B", ASSEMBLY_DRAFT, cp, "--write"], capture_output=True).returncode == 0
        assert "charge-current pads stay OPEN" in open(cp, encoding="utf-8").read()
        assert subprocess.run([sys.executable, "-B", ASSEMBLY_DRAFT, cp, "--write"], capture_output=True).returncode == 3
        assert _sha(page) == before


def t_the_page_is_plain_and_carries_the_outputs_figures():
    page = open(need(PAGE, "record efuse's page"), encoding="utf-8").read()
    out = open(need(OUT, "record efuse's output"), encoding="utf-8").read()
    assert "\u2014" not in page and "\u2013" not in page, "an em or en dash on the page"
    assert not CLAIM.search(page), CLAIM.search(page).group(0)
    for s in ("EF-F01", "EF-F02", "DR-03", "EF-L01", "EF-L03", "EF-O01", "authority: SESSION", "C-DEV rev 1", "EF-F03", "PROVISIONAL",
              "The supplier's validation task", "charge-current pads"):
        assert s in page, s
    for s in ("1.0718 / 1.2152 / 1.3631 A", "0.6681 / 0.7575 / 0.8496 A", "1.8953 / - / 2.2897 A", "0.4359 / 0.4941 / 0.5541 A",
              "18.3525 / 21.0833 / 23.8848 A", "6.4054 / 6.8000 / 7.0920 A", "0.9534", "143.6 uF", "8.2 uF", "1.5684 / 1.7783 / 1.9949 A",
              "0.6874 A", "0.5995 A", "0.4098 A", "0.5375 A"):
        assert s in page and s in out, s
