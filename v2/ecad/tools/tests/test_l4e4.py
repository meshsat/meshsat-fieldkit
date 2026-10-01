"""Layer 4 task L4-E4 (MESHSAT-1357, 1 October 2026; v2/docs/records/l4e4/): board A's current-limit coordination and the
USB-C outlet's trip, held as predicates on the values l4e4_limits.py computes.

The predicates: r11_dep.out is reproduced byte for byte before any figure is used; U3's IIN_HOST setting is a register
code whose INFERRED minimum in board current, with U3's own sense resistor R16 at its highest (tolerance and TCR over
r11_dep.py's envelope), covers REQ-016's window at the declared efficiencies (check astra-check-l4e4-1, B1: the first
round's 4.65 A passed only because R16 was left out, and fails once it is in); the chosen R11's stacked minimum (VSNS
minimum less the ISNS offset, R11 at its read tolerance and TCR, the taps) lies above U3's maximum board current plus
C-9's 0.079 A at -20, 25 and 62.1 C and at r11_dep.py's own envelope, and the larger catalogue values do not; C-1's
recomputed allowance is no tighter than the one already accepted; R138's trip window lies above every PDO's current and
below the ratings of what it protects, and the drawn 10 mOhm does not (DR-03, the negative case); the outlet's bench
procedure holds VBUS inside the maker's windows with U19 out of the path (B2); the committed .out is
what the script prints; the two draft apply scripts check without writing, apply once to a copy and refuse a second
application. Nothing here writes into the tree: the apply scripts run on copies in a temporary directory.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import hashlib
import importlib.util

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e4")
SCRIPT = os.path.join(REC, "l4e4_limits.py")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E4 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the scripts find the tree by git)")
        need(os.path.join(ROOT, "v2", "vendor", "ti", "ti-tps25740.pdf"), "the TPS25740 sheet")
        need(os.path.join(ROOT, "v2", "ecad", "pcb-a-power-a23", "out", "pcb-a-power.net"), "board A's netlist")
        if shutil.which("pdftotext") is None or shutil.which("pdftoppm") is None:
            raise Skip("pdftotext and pdftoppm are needed")
        sp = importlib.util.spec_from_file_location("l4e4_limits_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            _CACHE["R"] = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e4_limits.py refused (exit %s)" % e.code)
        _CACHE["M"] = m
    return _CACHE["R"]


def t_r11_dep_out_reproduced_byte_for_byte():
    R = _R()
    assert R["r0a"] and R["r0b"], "r11_dep.out not reproduced"


def t_iin_host_setting_is_a_register_code_that_covers_the_window():
    R = _R()
    assert abs(R["setting"] - 4.70) < 1e-9 and R["code"] == 94 and R["word"] == 0x5E00, (R["setting"], R["code"], hex(R["word"]))
    assert abs(R["lsb"] - 0.05) < 1e-12 and abs(R["code"] * R["lsb"] - R["setting"]) < 1e-9
    assert R["u3min_inf"] >= R["req"], "U3's INFERRED board minimum %.3f A under the window's %.3f A" % (R["u3min_inf"], R["req"])
    assert abs(R["u3max"] - max(R["setting"] + 0.1, R["setting"] * 1.025)) < 1e-9, "U3's maximum not by r11_dep.py's rule"
    assert abs(R["bmax"] - R["u3max"] / R["r16_lo"]) < 1e-12 and abs(R["serv"] - R["bmax"] - R["loads4"]) < 1e-12
    # the code is the smallest one that covers the need with R16: one code lower does not
    fn = R["fn"]
    assert fn["board_min"](R["setting"] - R["lsb"]) < R["req"] <= fn["board_min"](R["setting"])


def t_r11_stacked_minimum_above_u3_maximum_plus_c9_at_three_temperatures():
    R = _R()
    temps = [round(t["t"], 1) for t in R["per_t"]]
    assert temps == [-20.0, 25.0, 62.1], temps
    assert abs(R["serv"] - (R["fn"]["u3_max"](R["setting"]) / R["r16_lo"] + R["loads4"])) < 1e-12, "R16 not in U3's bound"
    for t in R["per_t"]:
        for k in ("m_alone", "m_kel", "m_full"):
            assert t[k] > 0, "%s at %.1f C: %+.4f A" % (k, t["t"], t[k])
    lo = R["r11_pick"]["band"][0]
    assert lo > R["serv"], "the 75 K envelope's stacked minimum %.3f A not above %.3f A" % (lo, R["serv"])
    assert abs(R["r11"] - 0.008) < 1e-12 and R["r11_pick"]["code"] == "C2904240"


def t_r11_larger_catalogue_values_fail_the_same_predicate():
    R = _R()
    bad = [c for c in R["cands"] if c["r"] > R["r11"] + 1e-12]
    assert bad, "no larger value to test against"
    for c in bad:
        assert not c["ok"], "%s eligible" % c["model"]
        assert c["tap"][2] < R["c1_prior"]
    ten = [c for c in bad if abs(c["r"] - 0.010) < 1e-12][0]
    assert ten["band"][0] < R["serv"], "the held 10 mOhm reads coordinated"
    assert R["r11_pick"]["band"][2] < R["prop_band"][2], "the chosen R11's highest permitted current is not under the 6.2 mOhm proposal's"


def t_r11_c1_allowance_recomputed_no_tighter_than_accepted():
    R = _R()
    tap25 = R["r11_pick"]["tap"][2]
    assert tap25 >= R["c1_prior"], (tap25, R["c1_prior"])
    assert R["kel"] <= tap25, "kelvin_check's own 1 % per tap is not the stricter"
    assert all(t["t_rip"] < 100.0 for t in R["per_t"]), "R11 past r11_dep.py's ASSUMED 100 C"


def t_r138_trip_window_above_every_pdo_and_below_the_ratings():
    R = _R()
    assert R["pdo_max"] == 3.0 and len(R["pdo"]) == 4
    lo, hi = R["w3"]
    for v, i in R["pdo"]:
        assert lo > i, "trip minimum %.3f A not above the %.0f V PDO's %.1f A" % (lo, v, i)
    assert hi < R["rec_a"] and hi < R["q27_id"] and hi < R["r138_rated"], (hi, R["rec_a"], R["q27_id"], R["r138_rated"])
    assert abs(R["r138"] - 0.005) < 1e-12 and R["r138_read"]["code"] == "C2903482"


def t_r138_as_drawn_fails_the_same_predicate():
    R = _R()
    assert R["drawn"][1] < R["pdo_max"], "the drawn 10 mOhm's trip is not under the 3 A contracts"


def t_committed_out_is_what_the_script_prints():
    R = _R()
    text = "\n".join(_CACHE["M"].render(R)) + "\n"
    committed = open(os.path.join(REC, "l4e4_limits.out"), encoding="utf-8").read()
    assert text == committed, "l4e4_limits.out is not the script's current output"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def t_apply_scripts_check_apply_once_and_refuse_a_second_application():
    need(GEN_A, "board A's generator")
    before = _sha(GEN_A)
    for name in ("apply_gen_sch_a_r11.py", "apply_gen_sch_a_r138.py"):
        script = need(os.path.join(REC, name), "the draft apply script")
        d = tempfile.mkdtemp(prefix="l4e4-apply-")
        try:
            cp = os.path.join(d, "gen_sch_a.py")
            shutil.copyfile(GEN_A, cp)
            orig = _sha(cp)

            def run(*a):
                return subprocess.run([sys.executable, "-B", script, cp] + list(a), capture_output=True, text=True, cwd=d)
            r = run("--check")
            assert r.returncode == 0 and "CHECK OK" in r.stdout, (name, r.returncode, r.stderr)
            assert _sha(cp) == orig, "%s --check wrote" % name
            r = run("--write")
            assert r.returncode == 0 and _sha(cp) != orig, (name, r.returncode, r.stderr)
            r = run("--write")
            assert r.returncode == 3 and "already applied" in r.stderr, (name, r.returncode, r.stderr)
            r = run("--check")
            assert r.returncode == 3, (name, r.returncode)
            open(cp, "w", encoding="utf-8").write("x = 1\n")
            r = run("--check")
            assert r.returncode == 3 and "occurs 0 times" in r.stderr, (name, r.returncode, r.stderr)
        finally:
            shutil.rmtree(d)
    assert _sha(GEN_A) == before, "the tree's generator changed"


def t_r16_tolerance_old_bounds_fail_new_bounds_pass():
    """Check B1: the first round's bounds left R16's tolerance and TCR out. Under those bounds its choice (4.65 A, the
    0.542 mOhm allowance) passed; with R16 in it fails both ways (the minimum under the need, the hot full-tap margin
    negative), and the second round's choice passes."""
    R = _R()
    fn, req, m_inf, l4 = R["fn"], R["req"], R["margin_inf"], R["loads4"]
    old_s, r11 = R["old_setting"], R["r11"]
    assert abs(old_s - 4.65) < 1e-9 and abs(R["r16_hi"] - 1.01 * (1 + 50e-6 * 75)) < 1e-12 and abs(R["r16_lo"] - 0.99 * (1 - 50e-6 * 75)) < 1e-12
    # the old bounds (R16 nominal): passed
    old_nom_serv = fn["u3_max"](old_s) + l4
    old_tap = fn["tap_rule"](r11, old_nom_serv)[2]
    assert old_s - m_inf >= req
    assert all(t["m_full"] > 0 for t in fn["margins_for"](old_nom_serv, r11, old_tap))
    # the new bounds (R16 at its corners): the old choice fails
    assert fn["board_min"](old_s) < req, "the old setting still covers the need with R16 in"
    assert fn["margins_for"](fn["serv_of"](old_s), r11, old_tap)[-1]["m_full"] < 0, "the old allowance still clears at 62.1 C"
    # and the new choice passes under the new bounds
    new_tap = R["r11_pick"]["tap"][2]
    assert fn["board_min"](R["setting"]) >= req
    assert all(t["m_full"] > 0 and t["m_kel"] > 0 and t["m_alone"] > 0 for t in fn["margins_for"](fn["serv_of"](R["setting"]), r11, new_tap))
    assert 0.38e-3 <= new_tap < 0.3804e-3, "the C-1 allowance is not the recomputed 0.380 mOhm: %.5f" % (new_tap * 1e3)


def t_tolerance_is_read_not_typed():
    """Minor 1: the tolerance comes from the sheet and the LCSC answers, and r11_dep.py's band() equals the band at it."""
    R = _R()
    assert R["tol"] == 0.01 and R["tol_s"] == "\u00b11%" and R["tol138"] == R["tol"]
    src = open(SCRIPT, encoding="utf-8").read()
    assert "1.01" not in src and "0.99" not in src, "a typed tolerance in l4e4_limits.py"
    b = R["fn"]["band"](0.008)
    lo = (R["vsns"][0] - R["offs"]) / (0.008 * (1 + R["tol"]) * (1 + R["tcr"] * R["dt_env"]))
    assert abs(b[0] - lo) < 1e-12


def t_outlet_bench_isolates_u18():
    """Check B2: the stage ahead overlaps both trip windows, so the procedure takes U19 out of the path, holds VBUS inside
    the maker's windows strictly (above the slow UVP and the falling threshold, below the SMALLER of the fast and the slow
    OVP minima: the recheck astra-check-l4e4-2 found the 15 V window reaching 16.3 V past the fast OVP's 16.2 V) and closes
    on the measured differential threshold; the delivered configuration then holds 3 A on each advertised voltage."""
    R = _R()
    st = R["stage_band"]
    assert st[0] < R["w3"][1] and st[2] > R["w5"][0], "the stage no longer overlaps the windows: revisit the procedure"
    assert R["hold"] == {5: (3.9, 5.5), 9: (7.1, 10.0), 15: (12.2, 16.2)}, R["hold"]
    for v, (lo, hi) in R["hold"].items():
        assert lo < v < hi
        rw = R["ovrows"][v]
        assert hi == min(rw["fovp"][0], rw["sovp"][0]) and lo == max(rw["suvp"][2], R["fth_max"]), (v, rw)
    counts = R["fn"]["vbus_counts"]
    assert not counts(15, 16.25), "a 16.25 V excursion on the 15 V contract counts (past the fast OVP minimum)"
    assert not counts(15, 16.3), "the first window's 16.3 V counts"
    assert counts(15, 16.15)
    for v, (lo, hi) in R["hold"].items():            # strictly inside: the boundaries themselves do not count
        assert not counts(v, lo) and not counts(v, hi) and counts(v, (lo + hi) / 2)
    out = open(os.path.join(REC, "l4e4_limits.out"), encoding="utf-8").read()
    for phrase in ("U19 held in shutdown", "regulated", "differential sense voltage", "PD_GDNG", "VBUS stays STRICTLY inside",
                   "12.2 V < VBUS < 16.2 V (the upper bound the fast OVP minimum)", "3.9 V < VBUS < 5.5 V", "7.1 V < VBUS < 10.0 V",
                   "the supply never limits", "the demonstrated threshold, lies in 19.2 to 22.6 mV",
                   "3.0 A held on each advertised voltage"):
        assert phrase in out, phrase
