"""Record l8p round 11 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68, finding L8P-R10-F1; MESHSAT-1357, 7 October 2026;
v2/docs/records/l8p/l8p_cprot.py, l8p_cprot.out, apply_gen_sch_p_ocheld.py, check_l8p_och.py, the two allowance apply scripts,
L8P-BREAKER.md section 16).

The predicates: the committed .out is what the script prints and every predicate it prints reads yes; the trip's window comes from the
drawn values and the printed rows and moves out of its bounds when the gain does (so the reader fails on the defect it guards: a trip
inside the 18 A service or over the blades' rerated current); the composed board P reads DRAWN and each mutation FAILS; the draft
refuses its own misuse; the crowbar's resistor must carry the breaker past its most limit alone; approaches (A) and (C) fail on the
printed figures the page names; the two allowance apply scripts apply once on their targets' copies and refuse a second run, and the
l9stk one refuses this tree's page (its section 15.9 is not merged here); the page and the README carry the output's numbers and the
SESSION decisions; no em or en dash and no claim word in the round's files.

Round 12 (W149, 7 October 2026, after the focused check L4A-69, W147's F1 to F12): the reader computes the window from R10's and
R135's drawn values and the delays from C117's, C119's and C120's, so R10 at 1 mOhm, R135 at 1 MOhm and C117 at 100 nF each FAIL (F3);
the on-time bound (D106, R143, C120 at 22 nF) is read and its removal FAILS (F2); a source's share is bounded on voltage over the
bounded on-time and R140's restated pulse is the largest case (F1); the RC hold's stretch is printed (F8). The arming's least delay
now counts from the trip's assertion and must cover the gate, the clearing and 0.5 ms (round 11 asked 1 ms after PGD's fall: the
basis changed with the circuit, L8P-BREAKER.md 16i, because the same delay now bounds R140's pulse).

Round 13 (W156, 7 October 2026, after the targeted recheck L4A-69, W153's F1, F2, F3, F7, F8): the reader computes OCH_S2's level while
PGD is low with every leakage that can reach it at the record's 86.25 C site, so round 12's drawing (R143 2.2 MOhm from BRK_PGD) FAILS
and round 13's (R143 330 kOhm from BRK_VIN, Q114 holding OCH_S2 low through PGD inverted by Q113, R144 and D107) reads DRAWN; five
mutations are added (round 12's drawing, Q114 removed, R144 at 1 MOhm, a shorted D106, a resistor on BRK_PGD) and each FAILS on its
electrical predicate. Changed expectations and their basis (constitution section 8): round 12's level test took R143 2.2 MOhm from
BRK_PGD; R143 now sits on BRK_VIN, so the same three requirements (OCH_S2 under the threshold while the trip asserts, BRK_PGD over
Q106's threshold, OCH_S2 armed over the release) are asserted on round 13's values, and R143 at 100 kOhm now fails on D106's current
past its printed 0.1 mA VF row rather than on BRK_PGD, which it no longer touches; E-6b is stated on one basis (the recheck's F3), so
R140's pulse is the voltage-bound case, larger than round 12's split case.

Round 14 (W161, 7 October 2026, after Q-179, W158's one bounded check; NO CIRCUIT CHANGED): the reader counts Q114's own IGSS in its
gate level (W158's F5), so the gate reads 5.046 V where round 13's reader read 5.062 V: the regression below fails against round 13's
reader and passes on round 14's; 4k's figures (the provisional choice under 10.16 V, the compared divider, the gate's margins, D107's
bound at the site, E-12f's interval), 4g's new rows and scope, the start's scope, row (c)'s restated status, page section 16k and the
README's round 14 paragraph are read; the drafts' values are read unchanged (no circuit moved). No earlier expectation changed."""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l8p")
SCRIPT = os.path.join(REC, "l8p_cprot.py")
OUT = os.path.join(REC, "l8p_cprot.out")
PAGE = os.path.join(REC, "L8P-BREAKER.md")
README = os.path.join(REC, "README.md")
DRAFT = os.path.join(REC, "apply_gen_sch_p_ocheld.py")
CHECK = os.path.join(REC, "check_l8p_och.py")
A5 = os.path.join(REC, "apply_pcb_interfaces_guard_allowance.py")
A9 = os.path.join(REC, "apply_l9stk_guard_allowance.py")
L9COPY = os.path.join(REC, "inputs", "l9stk-section15.9-bb6d2c8f.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _mod(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _M():
    if "M" not in _C:
        need(SCRIPT, "record l8p's round 11")
        for tool in ("pdftotext", "pdftocairo"):
            if shutil.which(tool) is None:
                raise Skip("%s is needed" % tool)
        sys.path.insert(0, REC)
        m = _mod("l8p_cprot_under_test", SCRIPT)
        for _k, (rel, _w) in m.DOCS.items():
            need(os.path.join(ROOT, rel), "a maker's sheet of the round (held back: fetch_held_back_rowc.py, records/l4e11/fetch_held_back.py)")
        for _k, (rel, _s, _w) in m.RC.DOCS.items():
            need(os.path.join(ROOT, rel), "a maker's sheet of round 10 (held back)")
        _C["M"] = m
    return _C["M"]


def _R():
    if "R" not in _C:
        m = _M()
        try:
            _C["R"] = m.compute()
            _C["K"] = m.compose()
        except (m.Refused, m.RC.Refused) as e:
            raise AssertionError("l8p_cprot.py refused: %s" % e)
    return _C["R"], _C["K"]


def _O():
    if "O" not in _C:
        sys.path.insert(0, REC)
        _C["O"] = _mod("check_l8p_och_under_test", CHECK)
    return _C["O"]


def t_the_committed_output_is_what_the_script_prints():
    _M()
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout.decode("utf-8") == open(OUT, encoding="utf-8").read(), "l8p_cprot.out is stale: regenerate with _bin/regen_out.py"
    preds = r.stdout.decode().split("9. PREDICATES")[1].strip().splitlines()
    assert len(preds) >= 25 and all(line.rstrip().endswith("yes") for line in preds), [l for l in preds if not l.rstrip().endswith("yes")]


def t_the_window_reads_the_drawn_gain_and_fails_outside_its_bounds():
    O = _O()
    nl = lambda rf, r10="2m 2512 2W (sense)", r135="1k": {"comps": {"R132": {"value": "1.00k 0.1% 25ppm"}, "R133": {"value": rf},
                                                               "R10": {"value": r10}, "R135": {"value": r135}}, "pins": {}, "on": {}}
    lo, hi = O.window(nl("19.3k 0.1% 25ppm"))
    assert 19.9 < lo < 20.0 and 21.5 < hi < 21.6, (lo, hi)
    assert lo > O.SERVICE_TRUE and hi < O.BLADE_BAND
    lo2, _hi2 = O.window(nl("20.9k 0.1% 25ppm"))         # a higher gain trips inside the service's true current
    assert lo2 < O.SERVICE_TRUE, lo2
    _lo3, hi3 = O.window(nl("17.6k 0.1% 25ppm"))         # a lower gain lets a held current pass the blades at the band
    assert hi3 > O.BLADE_BAND, hi3
    assert O.window({"comps": {"R132": {"value": "x"}, "R133": {"value": "19.3k"}, "R10": {"value": "2m"}, "R135": {"value": "1k"}},
                     "pins": {}, "on": {}}) is None
    # round 12 (F3): R10's and R135's drawn values enter the window; round 11's reader kept them constant
    lo4, hi4 = O.window(nl("19.3k 0.1% 25ppm", r10="1m 2512 2W (sense)"))
    assert lo4 > 39 and hi4 > O.BLADE_BAND, (lo4, hi4)
    _lo5, hi5 = O.window(nl("19.3k 0.1% 25ppm", r135="1M"))
    assert hi5 > O.BLADE_BAND, hi5
    assert O.window(nl("19.3k 0.1% 25ppm", r10="x")) is None


def t_the_composed_board_reads_drawn_and_every_mutation_fails():
    R, K = _R()
    assert K["l8p"] == "DRAWN" and K["och"][0] == "DRAWN", (K["l8p"], K["och"])
    assert len(K["muts"]) >= 9 and all(v == "FAIL" for _n, v, _w in K["muts"]), K["muts"]
    names = " ".join(n for n, _v, _w in K["muts"])
    for s in ("UVLO", "DOCK_EN_OUT", "BRK_VIN", "2 Ohm", "gate clamp", "sense delay"):
        assert s in names, s
    assert all(rc == 3 for rc, _m in K["refusals"]), K["refusals"]
    assert "RELEASE-R11.md" in K["refusals"][2][1], K["refusals"][2]
    assert abs(K["win_drawn"][0] - R["win"][0]) < 1e-9 and abs(K["win_drawn"][1] - R["win"][1]) < 1e-9


def O_ARM_MARGIN():
    return _O().ARM_MARGIN


def t_the_crowbar_alone_passes_the_breakers_most_limit_and_the_arming_covers_the_clearing():
    R, _K = _R()
    assert R["ic_least"] > R["LIM"][2] > R["LIM"][0], (R["ic_least"], R["LIM"])
    assert R["peak_clamp"] < R["VSNS_I"] and R["peak_clamp"] < 400.0
    assert R["tcts2"][0] > R["t_gate"] + R["CLEAR"] + O_ARM_MARGIN()      # round 12: from the trip's assertion (module docstring)
    assert R["tcts1"][0] > R["e10"]
    O = _O()
    # a 2 Ohm crowbar would not force the limit on its own: the reader's own predicate refuses it
    assert 10.6 / (2.0 * 1.01) < O.VCL_MAX_LIMIT


def t_the_approaches_a_and_c_fail_on_the_printed_figures_named():
    R, _K = _R()
    W = R["W"]
    assert R["need_f"] > R["f_air"] > R["f_band"]
    assert R["cu60"] > max(R["band_pinned"]) and R["b30"] > W["I"]
    assert R["c_most_1832"] > W["I_rr_band"] and R["c_most_1880"] > W["I_rr_air"] and R["VIN66"] < 10.6


def t_l8p_r11_f1_the_uvlo_node_with_its_inverters_hot_is_not_released():
    R, _K = _R()
    assert abs(R["uvlo_sink_only"][0] - 4.6) < 0.05
    assert R["uvlo_air"][1] > 2.55 > R["uvlo_site"][1]
    assert 76.25 < R["uvlo_t"] < 86.25


def t_the_allowance_scripts_apply_once_on_copies_and_refuse_the_trees_l9stk_page():
    a5, a9 = _mod("a5_under_test", A5), _mod("a9_under_test", A9)
    with tempfile.TemporaryDirectory() as d:
        y = os.path.join(d, "pcb_interfaces.yaml")
        shutil.copy(os.path.join(TOOLS, "pcb_interfaces.yaml"), y)
        r = subprocess.run([sys.executable, "-B", A5, y, "--write"], capture_output=True)
        assert r.returncode == 0, r.stderr.decode()
        doc = yaml.safe_load(open(y, encoding="utf-8"))
        assert "40 uA" in doc["board_to_board"]["contracts"]["IF-AE-DOCK"]["dock_en_guard"]
        assert subprocess.run([sys.executable, "-B", A5, y], capture_output=True).returncode == 3
        m = os.path.join(d, "l9.md")
        shutil.copy(L9COPY, m)
        assert subprocess.run([sys.executable, "-B", A9, m, "--write"], capture_output=True).returncode == 0
        t = open(m, encoding="utf-8").read()
        assert "40 uA cold and 50 uA tripped" in t and "the 30 uA this round allows the guard" in t
        assert subprocess.run([sys.executable, "-B", A9, m], capture_output=True).returncode == 3
    r = subprocess.run([sys.executable, "-B", A9, os.path.join(ROOT, "v2", "docs", "records", "l9stk", "L9-STACKUPS.md")], capture_output=True)
    if "### 15.9 The guard round" not in open(os.path.join(ROOT, "v2", "docs", "records", "l9stk", "L9-STACKUPS.md"), encoding="utf-8").read():
        assert r.returncode == 3 and b"not in the target" in r.stderr
    else:
        assert r.returncode in (0, 3)
    assert "TPS70950" not in open(A5, encoding="utf-8").read() and "LM26LV" not in open(A9, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    assert " ".join(a5.TEXT.split()) in " ".join(out.split())


def t_the_page_and_readme_carry_the_outputs_numbers_and_the_session_decisions():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    assert "### 16. Round 11" in page
    sec = page.split("### 16. Round 11")[1]
    for s in ("19.965", "21.521", "0.9572", "0.9238", "134.4 C", "22.85 A", "23.45 A", "-7.3 to +8.3 %", "0.460 to 0.852 ms",
              "4.60 to 8.36 ms", "26.9 A", "99.6 A", "116.8 A", "0.40 J", "135.9 C", "125.2 C", "93.2 %", "94.6 %", "0.464", "2.308",
              "6.63", "2.70 V", "1.57 V", "78.0 C", "4.224", "5.999", "9.666", "2.46 ms", "10.36 to 13.87 A"):
        assert s in sec, s
    for s in ("19.965", "21.521", "0.9572", "134.4", "22.85", "23.45", "26.9", "99.6", "0.40 J", "135.9", "93.2", "0.464", "2.308", "78.0"):
        assert s in out, s
    docs = yaml.safe_load(re.search(r"```yaml\n(.*?)```", sec, re.S).group(1))
    assert isinstance(docs, list) and len(docs) == 3
    for dct in docs:
        for k in ("id", "title", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by", "outcome"):
            assert k in dct and str(dct[k]).strip(), (dct.get("id"), k)
        assert dct["authority"] == "SESSION"
    seven = page.split("## 7. Interface rows owed")[1].split("## 8. ")[0]
    assert "**Round 11 (16f, L8P-R9-F2" in seven and "40 uA with the guard cold and 50 uA tripped" in seven
    item1 = page.split("\n## 6. Order constraints")[1].split("\n2. **Board P")[0]
    for f in ("apply_gen_sch_p_ocheld.py", "apply_pcb_interfaces_guard_allowance.py", "apply_l9stk_guard_allowance.py", "RELEASE-R11.md"):
        assert f in item1, f
    paras = open(README, encoding="utf-8").read().split("\n\n")
    heads = [q for q in paras if q.startswith("**ROUND 1")]
    r10 = [q for q in heads if q.startswith("**ROUND 10")]
    r11 = [q for q in heads if q.startswith("**ROUND 11")]
    r12 = [q for q in heads if q.startswith("**ROUND 12")]
    assert r10 and r11 and r12 and paras.index(r12[0]) == paras.index(r11[0]) + 1, [q[:12] for q in heads]   # set 30's note stays first (test_w5l8p)
    assert all(w in r11[0] for w in ("DONE", "NOT DONE", "NEXT")) and all(w in r12[0] for w in ("DONE", "NOT DONE", "NEXT"))


CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b", re.I)


def t_no_dashes_and_no_claim_words():
    sec = open(PAGE, encoding="utf-8").read().split("### 16. Round 11")[1]
    for p, t in ((SCRIPT, None), (OUT, None), (DRAFT, None), (CHECK, None), (A5, None), (A9, None), (os.path.abspath(__file__), None),
                 (PAGE, sec)):
        t = t if t is not None else open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, p
        if p in (PAGE, OUT):
            for line in t.splitlines():
                for mm in CLAIM.finditer(line):
                    assert re.search(r"(not|never|no|nothing)\b[^.]*" + mm.group(0), line, re.I) or "qualification" in line.lower(), (p, line[:120])


def t_round12_the_reader_reads_the_drawn_delays_and_the_bound_and_fails_on_them():
    O = _O()
    base = {"R135": "1k", "C117": "10n 50V C0G (SENSE1's filter)", "C119": "4.7n 50V C0G 5%", "C120": "22n 50V C0G 5%", "R143": "330k 1%",
            "R144": "200k 1%"}   # round 13's values (module docstring)
    nl = lambda **kw: {"comps": {k: {"value": kw.get(k, v)} for k, v in base.items()}, "pins": {}, "on": {}}
    d = O.delays(nl())
    assert abs(d["filter"] - 10e-6) < 1e-12 and 0.45e-3 < d["cts1"][0] < d["cts1"][1] < 0.86e-3
    assert d["cts2"][0] > O.T_GATE + O.CLEAR + O.ARM_MARGIN and d["cts2"][1] <= O.T_ON_BOUND
    assert O.delays(nl(C117="100n"))["filter"] > O.FILTER_SHARE * d["cts1"][0]          # SENSE1's filter over its share
    assert O.delays(nl(C120="47n"))["cts2"][1] > O.T_ON_BOUND                           # round 11's value: past R140's figure
    assert O.delays(nl(C120="15n"))["cts2"][0] < O.T_GATE + O.CLEAR + O.ARM_MARGIN      # too short to let the -1 latch first
    b = O.bound_levels(nl())
    assert b["low"] < O.VITP[0] and b["pgd"] > O.VTH_Q106 and b["armed"] > O.REL_MAX, b
    assert O.bound_levels(nl(R143="100k"))["low"] >= O.VITP[0]                           # round 13: D106 past its 0.1 mA VF row
    assert b["pgd_low"] < O.VITP[0] and b["gate"] >= O.VGS_RDS, b                        # round 13: PGD low, every leakage at the site
    assert O.bound_levels(nl(R144="1M"))["pgd_low"] >= O.VITP[0]                         # Q114's gate under 5 V with the leakage
    r12 = {"comps": {"R143": {"value": "2.2M 1%"}}, "pins": {"R143": {"1": "BRK_PGD", "2": "OCH_S2"}}, "on": {"BRK_PGD": {"R143"}}}
    b12 = O.bound_levels(r12)                                                             # round 12's drawing: lifted by leakage
    assert b12["on_pgd"] and b12["pgd_low"] >= O.VITP[0] and b12["pgd_other"] == ["R143"], b12
    assert O.bound_levels(nl(R143="10M"))["armed"] < O.REL_MAX                           # the bound never re-arms
    assert abs(O.ohms("2m 2512 2W (sense)") - 2e-3) < 1e-12 and O.ohms("0.39R 1%") == 0.39 and abs(O.farads("4.7n 50V") - 4.7e-9) < 1e-18


def t_round12_the_on_time_bound_ends_the_band_and_its_mutations_fail():
    R, K = _R()
    lo_b, hi_b = R["band"]
    assert R["v_floor"] < lo_b < hi_b, R["band"]                 # round 11's band is inside the -1's run: the defect is real
    assert abs(hi_b - R["v_force"]) < 1e-9 and R["v_band_src"] > hi_b
    assert R["tcts2"][1] <= _O().T_ON_BOUND and R["arm_cover"] > _O().ARM_MARGIN
    names = " ".join(n for n, _v, _w in K["muts"])
    for s_ in ("R10 at 1 mOhm", "R135 at 1 MOhm", "C117 at 100 nF", "C120 at 47 nF", "D106 removed", "R143 at 100 kOhm", "SENSE2 back on BRK_PGD"):
        assert s_ in names, s_
    assert all(v == "FAIL" for _n, v, _w in K["muts"]) and len(K["muts"]) == 21          # round 13 adds five (module docstring)
    assert K["delays"] is not None and K["levels"]["low"] < 0.792


def t_round12_a_sources_share_is_bounded_on_voltage_and_r140s_pulse_restated():
    R, _K = _R()
    assert R["e_r140"] == max(R["e_n"], R["e_s"], R["e_w"], R["e_v"]) == R["e_v"] and R["e_n_src"] < R["e_w"] < R["e_v"]   # round 13: one basis
    assert abs(R["e_n"] - 0.399) < 0.002                         # round 11's figure reproduces
    assert R["p_on"] < R["p_after"] and abs(R["vsys_max"] - 17.375) < 1e-9 and abs(R["p_src"] - 118.0) < 1e-9
    assert R["inh_v"] < R["v_settled"] < R["vsys_max"]          # L8P-R12-F1: the DD-7 inhibit does not set on the settled source
    # a typical gate charge is never a limit: Q110's turn-off is labelled ASSUMED on twice its typical Ciss, and moves with it
    m = _M()
    assert m.Q110_CISS_FACTOR == 2.0 and R["t_off"] > 40e-6 + 5 * 4.7e3 * 11.4e-9
    out = open(OUT, encoding="utf-8").read()
    for s_ in ("4c'. A SOURCE'S SHARE", "THE CHARGER holds VSYS", "E-6b RESTATED", "4i. THE BRK_VIN RANGE", "L8P-R12-D1", "L8P-R12-F1",
               "E-12s", "E11-29u", "E-9", "TYPICAL Ciss, ASSUMED", "IT ALSO STRETCHES THE RC HOLD", "reads NOT MET on that clause"):
        assert s_ in out, s_


def t_round12_the_hold_stretch_and_the_page_section():
    R, _K = _R()
    assert abs(R["hold_sink_only"] - 0.907) < 1e-3 and R["hold_air"] > 2.0 and R["hold_site"] == float("inf")
    page = open(PAGE, encoding="utf-8").read()
    assert "#### 16i. Round 12" in page
    sec = page.split("#### 16i. Round 12")[1]
    for s_ in ("3.32 J", "4.41 ms", "7.71 to 9.43 V", "2.15 to 3.92 ms", "6.82 V", "17.3 A", "118 W", "2.31 s", "E-9", "E11-29u",
               "NOT MET", "E-10", "L8P-R12-D1", "L8P-R12-F1", "E-12s", "RECORD"):
        assert s_ in sec, s_
    docs = yaml.safe_load(re.search(r"```yaml\n(.*?)```", sec, re.S).group(1))
    assert isinstance(docs, list) and len(docs) >= 2
    for dct in docs:
        for k in ("id", "title", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by", "outcome"):
            assert k in dct and str(dct[k]).strip(), (dct.get("id"), k)
        assert dct["authority"] == "SESSION"


def t_round13_the_pgd_low_disarm_holds_under_leakage_and_its_mutations_fail():
    R, K = _R()
    O = _O()
    # round 12's drawing, shown first: the leakage that reaches OCH_S2 lifts it over VITN while PGD is low
    assert R["q112_site"] > R["r12_lift"][1] > R["r12_lift"][0] and 0.3e-6 > R["r12_lift"][0]
    assert 40.0 < R["r12_t"][0] < R["r12_t"][1] < 60.0, R["r12_t"]
    # the two compared corrections fail on printed figures; the selection's levels hold on the composed netlist
    assert R["a1_arm"] < O.REL_MAX and R["a2"][2] < 5.0e-6 < R["q112_site"] + 5.0e-6
    L = K["levels"]
    assert L["pgd_low"] < 0.792 and L["gate"] >= O.VGS_RDS and L["armed"] > O.REL_MAX and L["low"] < O.VITP[0], L
    assert L["pgd"] > O.VTH_Q106 and not L["pgd_other"] and not L["on_pgd"], L
    # the start, the band's edge with the loop, E-6b on one basis, the cycling load
    assert R["start_i"] < R["win"][0] and R["t_disarm_start"] < R["ins_least"]
    assert R["v_force"] < R["edge"][0] < R["edge"][1] < 10.6 and 9.5 < R["edge"][0] and R["edge"][1] < 9.7, R["edge"]
    assert R["share_worst"] < R["crcw"]["w"][2] and 76.25 < R["t_nine"] < 85.0
    assert R["train_need"] > R["train_tmin"] and abs(R["cont_w100"] - 1.5) < 0.05
    want = {"round 12's drawing": "while PGD is low", "Q114 removed (round 13": "while PGD is low", "R144 at 1 MOhm": "while PGD is low",
            "D106 shorted (round 13": "RESET1's node", "R143 on BRK_PGD at 330 kOhm": "OCH_S2 at"}
    for key, why_part in want.items():
        hit = [(v, w_) for n_, v, w_ in K["muts"] if key in n_]
        assert len(hit) == 1 and hit[0][0] == "FAIL" and why_part in hit[0][1], (key, hit)
    out = open(OUT, encoding="utf-8").read()
    for s_ in ("4j. THE PGD-LOW DISARM ON LEAKAGE", "L8P-R13-D1", "THE START SERVICE SHOWN", "NOT BOUNDED", "ON ONE BASIS",
               "THE BAND'S UPPER EDGE WITH THE LOOP", "THE COUNT'S BASIS", "SNVSBJ1E 8.3.5.1", "E-12s's specimens", "L8P-R12-F1 (4g"):
        assert s_ in out, s_
    draft = open(DRAFT, encoding="utf-8").read()
    assert 'r("R143", "330k 1%", "BRK_VIN", "OCH_S2")' in draft and '"BRK_PGD", "OCH_S2"' not in draft


def t_round13_the_page_section_and_the_readme():
    page = open(PAGE, encoding="utf-8").read()
    assert "#### 16j. Round 13" in page
    sec = page.split("#### 16j. Round 13")[1]
    for s_ in ("0.29", "0.69", "5.58 uA", "43.5", "56.1", "3.02 uA", "5.06 V", "1.27 mV", "4.97 V", "0.64 V", "3.72 V", "10.16 V",
               "4.06 ms", "4.23 ms", "9.54", "9.61", "3.51 J", "77.7 C", "79.6 ms", "L8P-R13-D1", "L8P-R12-F1", "UNVERIFIED"):
        assert s_ in sec, s_
    docs = yaml.safe_load(re.search(r"```yaml\n(.*?)```", sec, re.S).group(1))
    assert isinstance(docs, list) and len(docs) >= 1
    for dct in docs:
        for k in ("id", "title", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by", "outcome"):
            assert k in dct and str(dct[k]).strip(), (dct.get("id"), k)
        assert dct["authority"] == "SESSION"
    paras = open(README, encoding="utf-8").read().split("\n\n")
    heads = [q for q in paras if q.startswith("**ROUND 1")]
    r12 = [q for q in heads if q.startswith("**ROUND 12")]
    r13 = [q for q in heads if q.startswith("**ROUND 13")]
    assert r12 and r13 and paras.index(r13[0]) == paras.index(r12[0]) + 1
    assert all(w in r13[0] for w in ("DONE", "NOT DONE", "NEXT"))


def t_round14_the_reader_counts_q114s_igss_and_the_record_answers_q179():
    O = _O()
    base = {"R135": "1k", "C117": "10n 50V C0G (SENSE1's filter)", "C119": "4.7n 50V C0G 5%", "C120": "22n 50V C0G 5%", "R143": "330k 1%",
            "R144": "200k 1%"}
    nl = {"comps": {k: {"value": v} for k, v in base.items()}, "pins": {}, "on": {}}
    b = O.bound_levels(nl)
    g_r13 = 7.6 - 200e3 * 1.01 * (O.IDSS_HOT + O.IR_ZENER_HOT)                  # round 13's reader, IGSS left out
    g_r14 = 7.6 - 200e3 * 1.01 * (O.IDSS_HOT + O.IR_ZENER_HOT + O.IGSS)
    assert abs(b["gate"] - g_r14) < 1e-9 and b["gate"] < g_r13 and b["gate"] >= O.VGS_RDS, (b["gate"], g_r13)
    assert abs(g_r13 - 5.062) < 0.001 and abs(b["gate"] - 5.046) < 0.001
    R, K = _R()
    assert abs(K["levels"]["gate"] - R["g_igss"]) < 1e-9 and K["och"][0] == "DRAWN" and len(K["muts"]) == 21
    assert all(v == "FAIL" for _n, v, _w in K["muts"])
    assert 1.0 < R["marg_5v"] < 1.05 and 1.95 < R["marg_vth"] < 2.05, (R["marg_5v"], R["marg_vth"])
    assert abs(R["v_pgd5"] - 10.16) < 0.005 and R["v_pgd5"] < 10.6 and abs(R["pgd_i_max"] - 2.44e-6) < 0.005e-6
    assert abs(R["v_pgd5_200k"] - 6.03) < 0.01 and R["v_pgd5_200k"] < 7.6
    assert abs(R["div_add_run"] - 33.6e-6) < 0.1e-6 and abs(R["div_add_low"] - 66.6e-6) < 0.1e-6
    assert abs(R["vz_site"] - 13.3125) < 1e-9 and R["e12f_turnoffs"] == 999 and (0.792 - K["levels"]["low"]) / 0.792 < 0.20
    out = open(OUT, encoding="utf-8").read()
    for s_ in ("4k. ROUND 14", "THE BOUNDED PROVISIONAL CHOICE (SESSION L8P-R14-D1)", "E-12p", "COMPARED ALTERNATIVE, NOT ADOPTED",
               "R144 shorted (round 14", "Q113 gate-drain shorted", "Q113 gate-source shorted", "Q114 gate-drain shorted",
               "Q114 gate-source shorted", "4g's scope (round 14", "record l9stk's IF-1", "POWER-ON START only", "at a DOCKING", "13.31 V",
               "999 breaker turn-offs", "ROW (C) AS A WHOLE", "HO-L stays OPEN on E-05", "reads NOT MET on its latent-failure clause",
               "2.44 uA", "6.03 V", "33.6 uA", "66.6 uA", "5.046 V", "1.018x", "2.00x", "19.2 %"):
        assert s_ in out, s_
    page = open(PAGE, encoding="utf-8").read()
    assert "#### 16k. Round 14" in page
    sec = page.split("#### 16k. Round 14")[1]
    for s_ in ("2.44 uA", "10.16 V", "6.03 V", "33.6 uA", "66.6 uA", "5.046 V", "1.018x", "2.00x", "13.31 V", "19.2 %", "999", "IF-1",
               "E-12p", "NOT ADOPTED", "SUPPORTED AS", "NOT MET", "HO-L stays OPEN on E-05", "no verdict upgraded", "NO circuit"):
        assert s_ in sec, s_
    docs = yaml.safe_load(re.search(r"```yaml\n(.*?)```", sec, re.S).group(1))
    assert [d["id"] for d in docs] == ["L8P-R14-D1", "L8P-R14-D2", "L8P-R14-D3"], docs
    for dct in docs:
        for k in ("id", "title", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by", "outcome"):
            assert k in dct and str(dct[k]).strip(), (dct.get("id"), k)
        assert dct["authority"] == "SESSION"
    # no circuit moved: the drafts keep the values the provisional choices stand on
    draft = open(DRAFT, encoding="utf-8").read()
    brk = open(os.path.join(REC, "apply_gen_sch_p_breaker.py"), encoding="utf-8").read()
    assert 'r("R144", "200k 1%", "BRK_VIN", "OCH_PN")' in draft and 'r("R143", "330k 1%", "BRK_VIN", "OCH_S2")' in draft
    assert 'r("R116", "1M", "BRK_VIN", "BRK_PGD"); r("R117", "1M", "BRK_PGD", "PACK_N")' in brk
    paras = open(README, encoding="utf-8").read().split("\n\n")
    heads = [q for q in paras if q.startswith("**ROUND 1")]
    r13 = [q for q in heads if q.startswith("**ROUND 13")]
    r14 = [q for q in heads if q.startswith("**ROUND 14")]
    assert r13 and r14 and paras.index(r14[0]) == paras.index(r13[0]) + 1
    assert all(w in r14[0] for w in ("DONE", "NOT DONE", "NEXT"))
