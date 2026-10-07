"""Record l8p round 10 (Layer 4 AI-scope register row (c), tasks L4A-66 and L4A-65; MESHSAT-1357, 7 October 2026;
v2/docs/records/l8p/l8p_rowc.py, l8p_rowc.out, L8P-BREAKER.md section 15).

The predicates: the committed .out is what the script prints; the battery FETs' figures reproduce the records' own (the 21.136 mOhm
allowance from the printed rows, record l9stk's even-split bar, E-1's 40.78 K/W, the 2.12 K lead on the printed Rth(j-mb) maximum) and
the three hold the breaker's held 23.93 A at or under 150 C at E-1's bar; the Zth curve is read from the sheet's own vector drawing,
never reaches the printed maximum, and a bound read on it is refused (relabelling the curve as a maximum makes the script accept it,
which this test's predicate catches); the superposition bound section 5 rests on holds on passive networks under pulse trains and is
tight for long on-times; R17's admitted terminal temperature comes from the lower of ROHM's two printed derating lines; the 25 A
blades read OVER their printed rerated current at the 76.25 C air while the 18 A service and a 30 A blade read within, and the
breaker's printed VCL span cannot fit the 18.32 A least under the rerated current; the pins' split ratio and the XT60 row; page 12o's
20.53 A is record l9stk's pair figure; a changed maker's sheet is refused; the page carries the output's numbers and the SESSION
decisions; no em or en dash and no claim word in the round's files."""
import importlib.util
import math
import os
import random
import re
import subprocess
import sys

import yaml

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l8p")
SCRIPT = os.path.join(REC, "l8p_rowc.py")
OUT = os.path.join(REC, "l8p_rowc.out")
PAGE = os.path.join(REC, "L8P-BREAKER.md")
README = os.path.join(REC, "README.md")
FETCH = os.path.join(REC, "fetch_held_back_rowc.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _M():
    if "M" not in _C:
        need(SCRIPT, "record l8p's round 10")
        import shutil
        for tool in ("pdftotext", "pdftocairo"):
            if shutil.which(tool) is None:
                raise Skip("%s is needed" % tool)
        sp = importlib.util.spec_from_file_location("l8p_rowc_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for _k, (rel, _s, _w) in m.DOCS.items():
            need(os.path.join(ROOT, rel), "a maker's sheet of the round (held back: records/l4e11/fetch_held_back.py, fetch_held_back_rowc.py)")
        _C["M"] = m
    return _C["M"]


def _R():
    if "R" not in _C:
        m = _M()
        try:
            _C["R"] = m.compute()
        except m.Refused as e:
            raise AssertionError("l8p_rowc.py refused: %s" % e)
    return _C["R"]


def t_the_committed_output_is_what_the_script_prints():
    _M()
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout.decode("utf-8") == open(OUT, encoding="utf-8").read(), "l8p_rowc.out is stale: regenerate with _bin/regen_out.py"
    assert all(line.rstrip().endswith("yes") for line in r.stdout.decode().split("7. PREDICATES")[1].strip().splitlines())


def t_the_fets_reproduce_the_records_figures_and_hold_the_breakers_limit():
    R = _R()
    assert abs(R["RA"] * 1e3 - 21.136) < 0.0005
    assert (R["r25"], R["r175"], R["r45"], R["rth_max"]) == (10.0, 16.0, 25.0, 1.4)
    assert abs(R["zbar_even"] / R["EVEN_BAR_REC"] - 1) < 1e-3 and abs(R["zbar_even"] * 8 / 9 / R["BAR"] - 1) < 1e-3
    assert abs(R["lead"] - 2.12) < 0.005
    assert abs(R["TJ_bar"] - 150.0) < 1e-6
    assert 136.0 < R["TJ_tgt"] < 137.5 and R["I150_tgt"] > R["I"]
    # the worst split's 9/8: one FET at R/x among three, the hottest loss over x, largest at x = 2
    best = max(range(100, 1001), key=lambda k: (k / 100.0) / (k / 100.0 + 2) ** 2)
    assert abs(best / 100.0 - 2.0) < 0.011 and abs(R["P_hot"] / R["P_even"] - 9 / 8) < 1e-9


def t_the_zth_curve_is_read_from_the_drawing_and_a_bound_on_it_is_refused():
    m = _M()
    R = _R()
    assert R["zmax_all"] < R["rth_max"] and R["z_1s"] > R["rth_typ"] and 1.25 < R["z_1s"] < 1.35
    assert R["zcls"] == "TYPICAL" and R["typ_bound_refused"]
    # mutation: the curve relabelled a maximum; the script then accepts the bound, and the predicate reads NO
    Rm = m.compute(zth_class="PRINTED")
    assert not Rm["typ_bound_refused"]
    pred = dict(m.PREDICATES)["a bound read on Fig. 4 is refused as a limit"]
    assert not pred(Rm) and pred(R)
    try:
        m.limit(1.3, "TYPICAL", "a mutated reading")
        raise AssertionError("a typical accepted as a limit")
    except m.GuardError:
        pass


def t_the_superposition_bound_holds_on_passive_networks():
    m = _M()
    rnd = random.Random(1357)
    for _ in range(300):
        n = rnd.randint(1, 5)
        rs = [rnd.uniform(0.01, 20.0) for _ in range(n)]
        taus = [10 ** rnd.uniform(-5, 3) for _ in range(n)]
        on = rnd.uniform(1e-4, 0.0438)
        period = on + rnd.uniform(0.110, 2.0)
        peak = m.foster_peak(rs, taus, on, period, 400, 1.0)
        assert peak <= sum(rs) + 1e-9, (rs, taus, on, period, peak)
    # tight for an on-time long against every time constant: the train reaches the held state
    peak = m.foster_peak([1.4, 39.4], [0.01, 0.02], 0.0438 * 10, 0.0438 * 10 + 0.11, 50, 1.0)
    assert peak > 0.99 * 40.8
    # and a train never exceeds its own held state even started from that state's history (the per-cycle lift is bounded)
    assert m.foster_peak([1.4], [0.004], 0.0438, 0.154, 10, 1.513) <= 1.513 * 1.4 + 1e-12


def t_r17_on_rohms_printed_derating():
    R = _R()
    assert 128.0 < R["tk_max"] < 129.0 and R["tk_max"] < R["tk_fig2_only"]
    assert abs(R["P17_20"] - 23.93 ** 2 * 5.05e-3) < 1e-9
    assert R["p17_at_band"] <= R["allow_at_band"]
    # mutation: the 7 W line alone at 70 C taken flat (no derating) would admit any terminal temperature: the script's line derates it
    assert 7.0 * (170 - R["tk_max"]) / 100 >= R["P17_tk"] - 1e-6


def t_the_blades_are_over_their_rerated_current_and_the_corrections_compared():
    R = _R()
    assert abs(R["f_25"] - 1.0) < 0.005 and 0.92 < R["f_air"] < 0.93
    assert R["I"] > R["I_rr_air"] and R["over_air_a"] > 0.8
    assert R["f_18"] < 1.0 and R["blade30_frac"] < 1.0
    assert R["vcl_ratio"] < R["need_ratio_margin"] and R["vcl_ratio"] > R["need_ratio_bare"]
    # the line read from the drawing runs from 110 % at -40 C to about 85 % at about +123 C
    assert abs(R["F0r"] - 110) < 0.2 and abs(R["T0"] + 40) < 0.3 and 84.5 < R["F1r"] < 86 and 122 < R["T1"] < 124
    # mutation: a 25 C inside air would leave the blades within their rerated current
    f25 = (R["F0r"] + (R["F1r"] - R["F0r"]) * (25 - R["T0"]) / (R["T1"] - R["T0"])) / 100
    assert R["I"] < 25.0 * f25


def t_the_pins_the_xt60_and_board_p():
    R = _R()
    assert abs(R["pin_ratio"] - 0.5527) < 0.001 and abs(R["pin_even"] - 5.9825) < 1e-3
    assert R["xt_frac"] < 1.0 and R["xt_margin"] > 0
    assert R["q1_k_pad"] > R["k_typ"] > 1.0 and R["q101_k125"] > R["k_typ"]
    assert abs(R["Q1_REC"][2] - 147.4) < 1e-9


def t_the_exposure_restated_and_the_guards_scope():
    R = _R()
    assert abs(R["EXPO_PAIR"] - 20.53) < 1e-9 and R["EXPO_PAIR"] == R["PAIR_EXPO_SRC"]
    assert R["mb_rr_tgt"] < R["TRIP_DIE"]


def t_a_changed_makers_sheet_is_refused():
    m = _M()
    saved = dict(m.DOCS)
    try:
        rel, s, w = m.DOCS["lf297"]
        m.DOCS["lf297"] = (rel, "0" * 64, w)
        try:
            m.compute()
            raise AssertionError("a changed sha256 was not refused")
        except m.Refused as e:
            assert "pinned" in str(e)
    finally:
        m.DOCS.clear()
        m.DOCS.update(saved)


def t_the_page_carries_the_outputs_numbers_and_the_session_decisions():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    assert "### 15. Round 10" in page
    sec = page.split("### 15. Round 10")[1]
    for s in ("21.136", "40.78", "37.59", "136.79", "2.12 K", "128.5", "14.9 K/W", "23.10 A", "0.83 A", "103.6 %", "27.71 A",
              "0.7886", "0.7932", "0.553", "1.866", "132.64", "20.53 A", "43.8 ms", "0.154 s"):
        assert s in sec, s
        assert s.split(" ")[0] in out, s
    docs = yaml.safe_load(re.search(r"```yaml\n(.*?)```", sec, re.S).group(1))
    assert isinstance(docs, list) and len(docs) >= 2
    for dct in docs:
        for k in ("id", "title", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by", "outcome"):
            assert k in dct and str(dct[k]).strip(), (dct.get("id"), k)
        assert dct["authority"] == "SESSION"
    # the README's first paragraph stays set 30's note (test_w5l8p holds it there); round 10's status is its own paragraph
    paras = open(README, encoding="utf-8").read().split("\n\n")
    r10 = [x for x in paras if x.startswith("**ROUND 10")]
    assert len(r10) == 1 and all(w in r10[0] for w in ("DONE", "NOT DONE", "NEXT")) and paras.index(r10[0]) == 1


CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b", re.I)


def t_no_dashes_and_no_claim_words():
    sec = open(PAGE, encoding="utf-8").read().split("### 15. Round 10")[1]
    for p, t in ((SCRIPT, None), (OUT, None), (FETCH, None), (os.path.abspath(__file__), None), (PAGE, sec)):
        t = t if t is not None else open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, p
        if p in (PAGE, OUT):
            for line in t.splitlines():
                for mm in CLAIM.finditer(line):
                    assert re.search(r"(not|never|no|nothing)\b[^.]*" + mm.group(0), line, re.I) or "qualification" in line.lower(), (p, line[:120])
