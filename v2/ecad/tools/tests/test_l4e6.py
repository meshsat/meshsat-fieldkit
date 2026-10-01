"""Layer 4 task L4-E6 (MESHSAT-1357, 1 October 2026; v2/docs/records/l4e6/): the fault handling of board A's front end U2
(LM5176), findings B-1, B-2 and B-4, held as predicates on the values l4e6_fault_handling.py computes.

The predicates: l4e4_limits.out, l4e5_source_control.out and r11_dep.out are reproduced byte for byte in child processes,
and l4e4_limits.py and r11_dep.py print their records in-process, before any figure is used; hiccup alone (candidate (a))
neither engages for certain nor closes B-1 or B-2 at either R11 outcome, because hiccup counts cycle-by-cycle limits and the
highest permitted current is set by the average limit; the chosen R12 is the smallest catalogue value that closes B-1 at
25 C and B-2 at 9, 15.1 and 36 V at both outcomes while keeping service margin; B-1 at the part's temperature stays
INCONCLUSIVE; B-4 by the generator's node analysis as r11_dep.py carries it is not met on the drawn bank at 2:1 at either
outcome; the service margins and the order against L4-E5's line hold; the consequence for L4-E4 supports 8 mOhm with
V-A07's 0.071 A; the committed .out is what the script prints; the two draft apply scripts check without writing, apply once
to a copy, refuse a second application, leave MODE alone and compose with L4-E4's R11 draft in either order; no em or en
dash in the record. Nothing here writes into the tree: the apply scripts run on copies in a temporary directory.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e6")
SCRIPT = os.path.join(REC, "l4e6_fault_handling.py")
OUT = os.path.join(REC, "l4e6_fault_handling.out")
L4E4_R11 = os.path.join(ROOT, "v2", "docs", "records", "l4e4", "apply_gen_sch_a_r11.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E6 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the scripts find the tree by git)")
        for rel in ("v2/vendor/ti/lm5176-datasheet.pdf", "v2/vendor/power/coilcraft-xal1010.pdf", "v2/vendor/power/coilcraft-xal1510.pdf",
                    "v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "v2/vendor/ti/bq25731-datasheet.pdf", "v2/vendor/power/lt8705a.pdf",
                    "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"):
            need(os.path.join(ROOT, rel), "an input of the L4-E6 record")
        if shutil.which("pdftotext") is None or shutil.which("pdftoppm") is None:
            raise Skip("pdftotext and pdftoppm are needed")
        sp = importlib.util.spec_from_file_location("l4e6_fault_handling_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            _CACHE["R"] = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e6_fault_handling.py refused (exit %s)" % e.code)
        _CACHE["M"] = m
    return _CACHE["R"]


def t_three_outputs_reproduced_byte_for_byte():
    R = _R()
    assert R["r0a"], "l4e4_limits.out not reproduced in a child process"
    assert R["r0b"], "l4e5_source_control.out not reproduced in a child process"
    assert R["r0c"], "r11_dep.out not reproduced in a child process"
    assert R["r0d"] and R["r0e"], "l4e4_limits.py or r11_dep.py does not print its record in-process"
    assert R["r0f"], "the restated FET relations do not reprint r11_dep.out's nine FET lines"


def t_hiccup_alone_neither_engages_for_certain_nor_closes_b1_b2():
    R = _R()
    assert (R["n_trip"], R["n_off"]) == (128, 4000), "SNVSAI1D p.17's hiccup counts not read"
    isat = R["isat"]
    for o in R["outcomes"]:
        assert o["a"][9.0]["hic"] != "guaranteed", "hiccup at 9 V with R12 as drawn is stated as certain at %s mOhm" % o["key"]
        assert o["a"][9.0]["pk_act"] < R["drawn"]["boost"][2], "the average limit's 9 V peak passes the drawn peak limit's maximum"
        assert o["a_b1"] > 0.9 * isat, "candidate (a) would close B-1 at %s mOhm" % o["key"]
        assert not o["a_b2"], "candidate (a) would close B-2 at %s mOhm" % o["key"]
    lo, hi = R["mode931"]
    assert R["mode_hic"][0] < lo and hi < R["mode_hic"][1], "93.1 kOhm does not select hiccup at every corner of IMODE"


def t_chosen_r12_is_the_smallest_catalogue_value_that_closes_b1_and_b2_with_service_margin():
    R = _R()
    ch = R["chosen"]
    assert abs(ch["r"] - 0.012) < 1e-12 and ch["code"] == "C2904242", "the chosen R12 is not HoJLR2512-3W-12mR-1%"
    smaller = [c for c in R["cands"] if c["r"] < ch["r"]]
    assert smaller and all(not c["ok_b2"] for c in smaller), "a smaller catalogue R12 also closes B-2"
    larger = [c for c in R["cands"] if c["r"] > ch["r"]]
    assert larger and all(c["m_boost"] <= 0 for c in larger), "a larger catalogue R12 still keeps the boost service margin"
    assert ch["m_boost"] > 0 and ch["m_buck"] > 0 and ch["cs_v"] < R["cs_abs"]


def t_b1_met_at_25_c_and_inconclusive_at_temperature():
    R = _R()
    isat = R["isat"]
    for o in R["outcomes"]:
        assert o["c_b1"] <= 0.9 * isat, "B-1 not met at 25 C at %s mOhm" % o["key"]
        assert o["c_derate_need"] < 1.0 and o["c_delay_head"] > 0
    assert not R["derating_held"], "the record claims a temperature derating the held sheet does not carry"
    text = open(OUT, encoding="utf-8").read()
    assert "INCONCLUSIVE (C-5)" in text


def t_b2_met_at_9_15_and_36_v_at_both_outcomes_without_hiccup_credit():
    R = _R()
    for o in R["outcomes"]:
        gs = o["c"]["gs"]
        assert sorted(gs) == [9.0, 15.1, 36.0]
        assert gs[9.0]["who"] == "the cycle-by-cycle limit", "at 9 V the fault is not held by the peak limit"
        for v, g in gs.items():
            for f in g["fets"]:
                assert f["tj"] is not None and f["tj"] <= 150.0, "%s at %.1f V past 150 C at %s mOhm" % (f["name"], v, o["key"])
    assert R["rtja"] == 50.0, "the RthetaJA used is not the maker's 50 C/W (the stated ASSUMPTION for board A)"


def t_b4_by_the_generators_method_not_met_on_the_drawn_bank():
    R = _R()
    o8, o7 = R["outcomes"]
    rb = R["rip_bulk"]
    assert abs(round(o8["b4"][2], 2) - 3.11) < 1e-9, "the 2:1 figure at 7.262 A is not L4-E4's carried 3.11 A"
    assert o8["b4"][0] <= rb and o8["b4"][1] <= rb and o8["b4"][2] > rb
    assert all(v > rb for v in o7["b4"])
    assert o8["b4_need"][2] < 1.0 and o7["b4_need"][2] < o8["b4_need"][2]


def t_service_margins_and_the_order_against_l4e5s_line():
    R = _R()
    ch = R["chosen"]
    assert ch["lim"]["boost"][0] > R["svc_boost_pk"], "the peak limit's minimum is not above H3's in-service boost peak"
    assert ch["lim"]["buck"][0] > R["svc_valley"], "the valley limit's minimum is not above the pin path's valley"
    assert R["v_no_h3"] is not None and R["v_no_h3"] > 9.0, "the order against L4-E5's line is not stated"
    assert abs(R["veh_pk"] - R["veh"] - R["svc9"]["ripple"] / 2.0) < 1e-9


def t_consequence_for_l4e4_supports_8_mohm_with_v_a07():
    R = _R()
    o8, o7 = R["outcomes"]
    assert (o8["key"], o7["key"]) == ("8", "7") and abs(o8["hi"] - 7.262) < 0.0005 and abs(o7["hi"] - 8.300) < 0.0005
    assert abs(R["va07"] - 0.071) < 1e-12 and abs(R["pin_r11"] - 5.095) < 1e-12
    text = open(OUT, encoding="utf-8").read()
    assert "SUPPORTS R11 8 mOhm (C2904240)" in text and "it does not require 7 mOhm" in text
    assert all(ok for _p, ok in R["preds"])


def t_committed_out_is_what_the_script_prints():
    R = _R()
    m = _CACHE["M"]
    need(OUT, "the committed output")
    assert "\n".join(m.render(R)) + "\n" == open(OUT, encoding="utf-8").read(), "l4e6_fault_handling.out is not what the script prints"


def _run(script, target, flag):
    return subprocess.run([sys.executable, "-B", script, target, flag], capture_output=True, text=True)


def t_draft_apply_scripts_check_apply_once_refuse_a_second_and_compose():
    gen = need(os.path.join(TOOLS, "gen_sch_a.py"), "board A's generator")
    fill = need(os.path.join(TOOLS, "lcsc_fill.py"), "lcsc_fill.py")
    need(L4E4_R11, "L4-E4's R11 draft")
    for name, src in (("apply_gen_sch_a_r12.py", gen), ("apply_lcsc_fill_r12.py", fill)):
        script = need(os.path.join(REC, name), "the draft apply script")
        d = tempfile.mkdtemp(prefix="l4e6-apply-")
        try:
            tgt = os.path.join(d, os.path.basename(src))
            shutil.copy(src, tgt)
            before = open(tgt, encoding="utf-8").read()
            r = _run(script, tgt, "--check")
            assert r.returncode == 0 and open(tgt, encoding="utf-8").read() == before, "%s --check wrote or failed" % name
            r = _run(script, tgt, "--write")
            assert r.returncode == 0 and open(tgt, encoding="utf-8").read() != before, "%s --write did not apply" % name
            after = open(tgt, encoding="utf-8").read()
            for flag in ("--check", "--write"):
                r = _run(script, tgt, flag)
                assert r.returncode == 3, "%s accepted a second application (%s)" % (name, flag)
            assert open(tgt, encoding="utf-8").read() == after
            if name == "apply_gen_sch_a_r12.py":
                assert after.count('r(rmd, "100k (MODE: CCM)", N("MODE"), N("VCC"))') == 1, "the draft touches MODE"
                assert 'rcs="12m"' in after and 'cslope=("330p", "C1664")' in after
                assert _run(L4E4_R11, tgt, "--write").returncode == 0, "L4-E4's R11 draft does not apply after this one"
                tgt2 = os.path.join(d, "order2.py")
                shutil.copy(src, tgt2)
                assert _run(L4E4_R11, tgt2, "--write").returncode == 0 and _run(script, tgt2, "--write").returncode == 0, \
                    "this draft does not apply after L4-E4's R11 draft"
                assert open(tgt2, encoding="utf-8").read() == open(tgt, encoding="utf-8").read(), "the two orders differ"
        finally:
            shutil.rmtree(d)
    assert open(gen, encoding="utf-8").read().count('cslope=("680p", "C30816"), boot_diodes=("D9", "D10"),\n') == 1, "the tree's generator was edited"


def t_no_em_or_en_dash_in_the_record():
    bad = []
    for fn in sorted(os.listdir(REC)):
        p = os.path.join(REC, fn)
        if os.path.isfile(p):
            t = open(p, encoding="utf-8").read()
            if chr(0x2014) in t or chr(0x2013) in t:
                bad.append(fn)
    assert not bad, "em or en dash in %s" % bad
