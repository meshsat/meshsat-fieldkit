"""Record l8p round 11 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68, finding L8P-R10-F1; MESHSAT-1357, 7 October 2026;
v2/docs/records/l8p/l8p_cprot.py, l8p_cprot.out, apply_gen_sch_p_ocheld.py, check_l8p_och.py, the two allowance apply scripts,
L8P-BREAKER.md section 16).

The predicates: the committed .out is what the script prints and every predicate it prints reads yes; the trip's window comes from the
drawn values and the printed rows and moves out of its bounds when the gain does (so the reader fails on the defect it guards: a trip
inside the 18 A service or over the blades' rerated current); the composed board P reads DRAWN and each mutation FAILS; the draft
refuses its own misuse; the crowbar's resistor must carry the breaker past its most limit alone; approaches (A) and (C) fail on the
printed figures the page names; the two allowance apply scripts apply once on their targets' copies and refuse a second run, and the
l9stk one refuses this tree's page (its section 15.9 is not merged here); the page and the README carry the output's numbers and the
SESSION decisions; no em or en dash and no claim word in the round's files."""
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
    nl = lambda rf: {"comps": {"R132": {"value": "1.00k 0.1% 25ppm"}, "R133": {"value": rf}}, "pins": {}, "on": {}}
    lo, hi = O.window(nl("19.3k 0.1% 25ppm"))
    assert 19.9 < lo < 20.0 and 21.5 < hi < 21.6, (lo, hi)
    assert lo > O.SERVICE_TRUE and hi < O.BLADE_BAND
    lo2, _hi2 = O.window(nl("20.9k 0.1% 25ppm"))         # a higher gain trips inside the service's true current
    assert lo2 < O.SERVICE_TRUE, lo2
    _lo3, hi3 = O.window(nl("17.6k 0.1% 25ppm"))         # a lower gain lets a held current pass the blades at the band
    assert hi3 > O.BLADE_BAND, hi3
    assert O.window({"comps": {"R132": {"value": "x"}, "R133": {"value": "19.3k"}}, "pins": {}, "on": {}}) is None


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


def t_the_crowbar_alone_passes_the_breakers_most_limit_and_the_arming_covers_the_clearing():
    R, _K = _R()
    assert R["ic_least"] > R["LIM"][2] > R["LIM"][0], (R["ic_least"], R["LIM"])
    assert R["peak_clamp"] < R["VSNS_I"] and R["peak_clamp"] < 400.0
    assert R["tcts2"][0] > R["t_gate"] + R["CLEAR"] + 1e-3
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
    assert paras[1].startswith("**ROUND 10") and paras[2].startswith("**ROUND 11")
    assert all(w in paras[2] for w in ("DONE", "NOT DONE", "NEXT"))


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
