"""Layer 9 task T5, record l9t5 (MESHSAT-1357, 4 October 2026; v2/docs/records/l9t5/): C-ALLTX rev 2 and C-DEV rev 1, held as
predicates on what l9t5_case.py computes.

The predicates: the committed .out is what the script prints and every pinned input is present at the sha256 the output names; the
copies in inputs/ carry the sha256 SOURCES.txt names; every predicate the script states holds; the case row's parts sum to the cells'
EMF plus the deficit and its allowance is re-solved here; the gauge's terms are re-solved here from the figures the script read;
A1's PA figures are the loop's high end over the maker's efficiency; C-DEV's two options are re-solved from VSNS and R43; the page
carries the output's figures; the record carries no long dash, no claim word outside the copies and no private path. These are
software predicates on the record's arithmetic: they establish no property of any board, converter, PA or pack.
"""
import hashlib
import importlib.util
import math
import os
import re
import shutil
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l9t5_case.py")
OUT = os.path.join(REC, "l9t5_case.out")
PAGE = os.path.join(REC, "L9T5-CASES.md")
README = os.path.join(REC, "README.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l9t5 record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l9t5_case_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l9t5 record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l9t5_case.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def t_output_reproduced_byte_for_byte():
    _M()
    need(OUT, "the committed output")
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l9t5_case.out is not what the script prints"


def t_every_input_is_pinned_and_present():
    m = _M()
    for key, rel in m.PINS.items():
        sha = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["text"], "%s is not pinned at its current sha256" % rel
    src = open(os.path.join(ROOT, m.PINS["sources"]), encoding="utf-8").read()
    for k in m.COPIES:
        full = hashlib.sha256(open(os.path.join(ROOT, m.PINS[k]), "rb").read()).hexdigest()
        assert "%s sha256 %s" % (os.path.basename(m.PINS[k]), full) in src, k


def t_every_predicate_holds():
    _M()
    P = _C["R"]["pred"]
    assert len(P) >= 16
    bad = [k for k, v in P.items() if not v]
    assert not bad, "false: %s" % "; ".join(bad)
    assert all(("   %s" % k) in _C["text"] for k in P)


def t_the_case_row_closes_and_its_allowance_is_re_solved():
    _M()
    c, R = _C["R"]["case"], _C["R"]
    assert abs(c["load"] + c["conv"] + c["path_w"] + c["cell_w"] - c["emf_w"] - c["deficit"]) < 1e-9
    i, v = R["I"], R["V"]
    assert abs(c["allow"] - i * (v - i * (c["r_path"] + 4 * 0.06 / 3.0))) < 1e-9 and round(c["allow"], 3) == 240.747
    assert abs(c["need"] - (c["p"] / i + i * (c["r_path"] + c["r_cells"]))) < 1e-9
    assert abs(c["vbat"] * i - c["p"]) < 1e-6, "the converters are evaluated at the VBAT the case sets"
    assert abs(sum(x for _l, x in R["conv_parts"]) - c["conv"]) < 1e-9
    q = R["case_quote_row"]
    assert round(q["V_rest"]["hi"], 3) == 16.214 and round(c["need"], 4) == 15.5162


def t_the_gauge_terms_are_re_solved_from_the_read_figures():
    _M()
    I, U = _C["R"]["in"], _C["R"]["U"]
    fsr = I["g_vref1"] / I["g_fsr_div"]
    terms = dict((lab.split(",")[0], x) for lab, x in U["gauge_terms"])
    assert abs(terms["gain error"] - I["g_gain"] * fsr / I["r10"]) < 1e-12 and round(terms["gain error"], 3) == 0.486
    assert abs(terms["integral nonlinearity"] - I["g_inl"] * I["g_lsb"] / I["r10"]) < 1e-12
    assert abs(U["gauge_uncal"] - sum(x for _l, x in U["gauge_terms"])) < 1e-12
    assert U["gauge_uncal_row"]["i"] == 18.0 - U["gauge_uncal"] and U["gauge_uncal_row"]["need"] > U["gauge_cal_row"]["need"] > _C["R"]["case"]["need"]


def t_a1_is_the_loops_high_end_over_the_makers_efficiency():
    m = _M()
    I, A = _C["R"]["in"], _C["R"]["A"]
    assert abs(A["a1_ex_w"] - I["pa_ex_vdd"] * sum(I["pa_ex_idd"])) < 1e-12 and round(A["a1_ex_w"], 1) == 75.0
    assert A["a1_pa_now"] == 113.0 and abs(I["pa_pout_max"] / I["pa_eta_min"] - 112.5) < 1e-9
    for a in A["a1"]:
        assert abs(a["p_hi"] - m.PA_SERVICE_W * 10 ** (2 * a["db"] / 10.0)) < 1e-12
        assert abs(a["p_dc"] - a["p_hi"] / I["pa_ex_eta"]) < 1e-12
        assert a["unc"]["i"] < 18.0
        # the loop's high end at +-0.25 and +-0.5 dB is under today's 113 W; at +-1 dB it passes the 45 W rating and the PA draws more
        assert (a["nom"]["p"] < _C["R"]["case"]["p"]) == (a["db"] < 1.0), a["db"]
        assert (a["p_hi"] > I["pa_pout_max"]) == (a["db"] == 1.0), a["db"]


def t_cdev_options_are_re_solved():
    _M()
    C = _C["R"]["C"]
    lo, hi = C["vsns"][0], C["vsns"][2]
    assert abs(C["lim_min"] - lo / (C["rs"] * (1 + C["tol"]))) < 1e-12
    assert abs(C["a_need_max"] - lo / (C["i_least"] * (1 + C["tol"]))) < 1e-12
    assert abs(C["a_need_min"] - hi / (10.0 * (1 - C["tol"]))) < 1e-12 and C["a_need_max"] < C["a_need_min"]
    assert abs(C["b_i_least"] - (C["i_least"] - C["ioc_in_w"] / C["v_least"])) < 1e-12 and C["b_margin"] > 1.0


def t_the_page_carries_the_outputs_figures():
    _M()
    R = _C["R"]
    need(PAGE, "the page")
    page = open(PAGE, encoding="utf-8").read()
    c, U, A, C = R["case"], R["U"], R["A"], R["C"]
    by = {a["db"]: a for a in A["a1"]}
    for s in ("%.4f V" % c["need"], "%.3f" % c["allow"], "%.3f" % c["p"], "%+.3f W" % c["deficit"], "%.4f V" % U["gauge_uncal_row"]["need"],
              "%.4f A" % U["gauge_uncal"], "%.4f V" % U["comb_printed"]["need"], "%.4f V" % by[0.5]["unc"]["need"], "%.4f V" % by[0.25]["m8"]["need"],
              "%.4f A against %.4f A" % (C["b_i_least"], C["lim_min"]), "%.4f mOhm" % (C["a_need_max"] * 1000), "%.4f mOhm" % (C["a_need_min"] * 1000),
              "%.3f mOhm" % (A["a2_band"][2] * 1000), "%.4f V" % A["a3_unc"]["need"], "16.214", "C-ALLTX rev 2", "C-DEV rev 1"):
        assert s in page, "the page does not carry %r" % s
    need(README, "the README")
    assert "%.4f V" % c["need"] in open(README, encoding="utf-8").read()


def t_record_hygiene():
    files = [SCRIPT, OUT, PAGE, README, os.path.abspath(__file__)]
    inputs = os.path.join(REC, "inputs")
    copies = [os.path.join(inputs, f) for f in sorted(os.listdir(inputs))] if os.path.isdir(inputs) else []
    for p in files + copies:
        need(p, os.path.basename(p))
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)
        if p in (SCRIPT, OUT, PAGE, README):
            mm = CLAIM.search(t)
            assert not mm, "a claim word %r in %s" % (mm.group(0), os.path.basename(p))
