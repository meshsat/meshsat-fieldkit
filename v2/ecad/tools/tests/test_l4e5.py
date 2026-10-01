"""Layer 4 task L4-E5 (MESHSAT-1357, 1 October 2026; v2/docs/records/l4e5/): source control for board A's charger on the
ORed bus, held as predicates on the values l4e5_source_control.py computes.

The predicates: l4e4_limits.out and r11_dep.out are reproduced byte for byte in child processes, and l4e4_limits.py and
l4e_replay.py print their records in-process, before any figure is used; the drawn telemetry cannot separate the sources;
each source's envelope is as the page states (the front end's input inside the vehicle entry's FW-A16 basis at every
VIN_RAW from 9 to 36 V, the solar bus settling above the knee at every power the pin's error allows and above 12 V from the
stated power); the knee fits between the restart guard's latch and REQ-015's floor; the startup, source-change and
stale-telemetry rules never hold U3's IIN_HOST above L4-E4's 4.70 A, and the fallback never asks the entry past its basis;
the highest IIN_HOST against L4-E4's 4.70 A, the pin path re-run through L4-E4's own functions, and FW-A16 as written as the
negative case; the chosen mechanism gives up the least solar energy on both traces; the committed .out is what the script
prints; the draft apply script checks without writing, applies once to a copy and refuses a second application. After the
check astra-check-l4e5-1: V-A09's HIZ entry, exit and zero-current thresholds agree with the knee's transfer function and
TI's levels (B1); V-A10's telemetry fault injection is bounded and its fallback never passes 4.70 A (B2); the 12 V solar
boundary is H3's, and the check's source-blind example trades the 12 V vehicle for it (B3); the POR value is kept apart
from the removal reset (minor 1); the collapse times are nominal estimates (minor 2). After the recheck
astra-check-l4e5-2: HIZ release is never asserted as conversion below TI's printed regulation range (B1), and V-A10's boot
case permits FW-A16's initialization from POR before it forbids telemetry-caused changes (B2). Nothing here writes into the
tree.
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e5")
SCRIPT = os.path.join(REC, "l4e5_source_control.py")
APPLY = os.path.join(REC, "apply_fw_a16.py")
CONTRACT = os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E5 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the scripts find the tree by git)")
        for rel in ("v2/vendor/ti/bq25731-datasheet.pdf", "v2/vendor/power/lt8705a.pdf", "v2/vendor/ti/ti-lm5069.pdf",
                    "v2/vendor/ti/ti-lm74700-q1.pdf", "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net",
                    "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"):
            need(os.path.join(ROOT, rel), "an input of the L4-E5 record")
        if shutil.which("pdftotext") is None or shutil.which("pdftoppm") is None:
            raise Skip("pdftotext and pdftoppm are needed")
        sp = importlib.util.spec_from_file_location("l4e5_source_control_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            _CACHE["R"] = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e5_source_control.py refused (exit %s)" % e.code)
        _CACHE["M"] = m
    return _CACHE["R"]


def t_l4e4_and_r11_outputs_reproduced_byte_for_byte():
    R = _R()
    assert R["r0a"], "l4e4_limits.out not reproduced in a child process"
    assert R["r0b"], "r11_dep.out not reproduced in a child process"
    assert R["r0c"] and R["r0d"], "l4e4_limits.py or l4e_replay.py does not print its record in-process"


def t_drawn_telemetry_cannot_separate_the_sources():
    R = _R()
    f = " ".join(R["facts"])
    assert "U5 pins 25 to 28 (SRVO_FBIN, SRVO_IIN, SRVO_IOUT, SRVO_FBOUT) unconnected" in f
    assert "source pins 1-3 on DC_HS, drain pin 5 on HS_S" in f, "the body-diode back-feed path is not as read"
    assert "no reading of VIN_RAW on board A" in f
    lo, _ty, hi = R["v_trk"]
    assert 9.0 < lo and hi < 36.0, "the tracker's output lies inside REQ-015's 9 to 36 V, so no voltage band is its alone"
    assert R["e04"] / R["t_fault"][0] > 100, "FW-E04's period is not orders above the entry's fault timeout"
    assert all(t < 0.011 for _dp, t in R["t_col"]), "the collapse is not milliseconds"


def t_vehicle_envelope_inside_the_entry_basis_at_every_volt():
    R = _R()
    for r in R["env"]:
        assert r["fe_h"] <= R["i_ent"], "H3 asks %.3f A of the entry at %.1f V" % (r["fe_h"], r["v"])
        assert r["fe_h"] < R["ent_lim"][0], "H3 reaches the LM5069's minimum limit at %.1f V" % r["v"]
        assert r["fe_b"] <= R["i_ent"], "the fallback rule asks %.3f A at %.1f V" % (r["fe_b"], r["v"])
    assert R["fe_h_max"] <= R["i_ent"], "H3's highest front-end input %.3f A over 9 to 36 V" % R["fe_h_max"]
    assert R["eta_at_basis"] < R["eta"], "the efficiency margin at 9 V is not stated against the declared 0.93"
    assert R["pin_v_clamp"] <= R["pin_rmax"] and R["v_pin_disable"] > 36.0


def t_solar_envelope_settles_above_the_knee_and_admits_the_window():
    R = _R()
    for p, vn, lo, hi, _i in R["settle"]:
        if p > R["thr_h3"]:
            assert lo is not None and lo > R["latch"][2], "at %.1f W the bus can settle at or under the latch" % p
        if p >= R["thr12"]:
            assert lo >= 12.0, "at %.1f W the bus can settle under 12 V" % p
    win = max(R["settle"], key=lambda s: s[0])
    assert win[3] is not None and win[3] <= R["v_trk2"][0], "the window's highest settle %.2f V is above the tracker's lowest ceiling" % win[3]
    assert R["v_trk2"][2] <= 36.0 and R["v_trk2"][0] >= R["v_need"]
    assert R["thr_h3"] < R["thr"], "the knee does not lower the collapse threshold"
    # the drawn ceiling cannot admit the window under the same line (O-33)
    assert R["keys"]["H1"][2] < R["keys"]["H3"][2] and R["o33_nom_w"] < 60.0


def t_knee_fits_between_the_latch_and_reqs_floor():
    R = _R()
    m = _CACHE["M"]
    assert R["v_hiz_lo"] >= R["latch"][2] + m.LATCH_MARGIN, "HIZ at %.3f V is not clear of the latch's %.2f V" % (R["v_hiz_lo"], R["latch"][2])
    assert R["v_unhiz_hi"] < R["vk1"] and m.V_K0 * (1 + m.T_KNEE) < R["vk1"]
    assert R["floor_min"] > 0, "REQ-015: the pack is not charged at the 9 V floor"


def t_startup_source_change_and_stale_rules_never_exceed_their_limits():
    R = _R()
    w = R["writes"]
    assert abs(w["after every adapter removal (one-time reset, p.26, p.80)"] - 3.25) < 1e-12
    por = R["por"]
    assert set(por) == {"2000h (p.80 heading)", "4100h (p.80 figure)"} and R["por_table_code"] == 0x20, "minor 1: the POR annotations"
    assert abs(por["2000h (p.80 heading)"][0] - 3.2) < 1e-9 and abs(por["4100h (p.80 figure)"][1] - 3.25) < 1e-9
    assert all(b <= R["setting"] for _r5, b in por.values()), "a POR reading is above L4-E4's setting"
    assert abs(w["at POR, RSNS_RAC = 1b, board current (the larger annotation)"] - max(b for _r5, b in por.values())) < 1e-12
    assert all(v <= R["setting"] + 1e-12 for v in w.values()), "a value U3 holds is above L4-E4's setting"
    assert R["code"] == 94 and R["word"] == 0x5E00
    # the stale rule changes nothing, and its diagnostic fallback (FW-A16's line clipped at 4.70 A) stays inside the basis
    for r in R["env"]:
        assert r["reg_b"] <= R["setting"] + 1e-12 and r["fe_b"] <= R["i_ent"]


def t_highest_iin_host_against_l4e4_and_the_pin_path():
    R = _R()
    L = R["l4e4"]
    assert abs(R["max_written"] - 4.70) < 1e-12 and R["max_written"] <= L["setting"] + 1e-12
    assert all(m1 > 0 and m2 > 0 and m3 > 0 for _t, m1, m2, m3 in L["per_t"]), "L4-E4's own margins not positive"
    X = R["cross"]
    assert X["serv"] > L["serv"], "the pin path is not above U3's own maximum"
    assert X["ok_alone"] and X["ok_kel"] and not X["ok_full"], "the pin path's verdicts are not as the page states"
    assert X["r11_ok"] is not None and abs(X["r11_ok"][0] - 0.007) < 1e-12 and X["r11_ok"][2] > X["hi_now"]
    # the negative case: FW-A16 as written passes L4-E4's setting and breaks R11's coordination
    a = R["cand_a"]
    assert a["s"] > L["setting"] and a["worst"] < 0 and a["v_over"] < 36.0


def t_chosen_mechanism_gives_up_the_least_solar():
    R = _R()
    for tk in ("screen", "cand"):
        E = R["ER"][tk]
        h3 = E["H3"]["lo"][0]
        for k in ("A", "B", "H1", "H2"):
            assert h3 >= E[k]["lo"][0] - 1e-9, "%s: %s's lower bound takes more than H3's" % (tk, k)
        assert E["avail"] - h3 <= E["e_h3"] + 1e-6, "%s: H3 gives up more than its HIZ hours" % tk
        assert abs(E["avail"] - E["H3"]["up"][0]) < 1e-6
    assert R["ER"]["screen"]["A"]["up"][0] < R["ER"]["screen"]["avail"] - 300.0, "O-33's cap no longer binds on the screening day"


def t_committed_out_is_what_the_script_prints():
    R = _R()
    text = "\n".join(_CACHE["M"].render(R)) + "\n"
    committed = open(os.path.join(REC, "l4e5_source_control.out"), encoding="utf-8").read()
    assert text == committed, "l4e5_source_control.out is not the script's current output"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def t_apply_script_checks_applies_once_and_refuses_a_second():
    need(CONTRACT, "the hardware and firmware contract")
    need(APPLY, "the draft apply script")
    before = _sha(CONTRACT)
    d = tempfile.mkdtemp(prefix="l4e5-apply-")
    try:
        cp = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copyfile(CONTRACT, cp)
        orig = _sha(cp)

        def run(*a):
            return subprocess.run([sys.executable, "-B", APPLY, cp] + list(a), capture_output=True, text=True, cwd=d)
        r = run("--check")
        assert r.returncode == 0 and "CHECK OK" in r.stdout, (r.returncode, r.stderr)
        assert _sha(cp) == orig, "--check wrote"
        r = run("--write")
        assert r.returncode == 0 and _sha(cp) != orig, (r.returncode, r.stderr)
        text = open(cp, encoding="utf-8").read()
        assert "| FW-A18 |" in text and "| V-A09 |" in text and "| V-A10 |" in text and "| 1 (L4-E5) |" in text
        assert "\u2013" not in text and "\u2014" not in text
        r = run("--write")
        assert r.returncode == 3 and "already applied" in r.stderr, (r.returncode, r.stderr)
        r = run("--check")
        assert r.returncode == 3, r.returncode
        open(cp, "w", encoding="utf-8").write("x\n")
        r = run("--check")
        assert r.returncode == 3, r.returncode
    finally:
        shutil.rmtree(d)
    assert _sha(CONTRACT) == before, "the tree's contract changed"


def _apply_rows():
    sp = importlib.util.spec_from_file_location("apply_fw_a16_under_test", need(APPLY, "the draft apply script"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _has(text, v):
    """The figure printed to three decimals, as a whole number in the text."""
    import re
    return re.search(r"(?<![\d.])%s(?![\d])" % re.escape("%.3f" % v), text) is not None


def t_v_a09_thresholds_agree_with_the_knee():
    """B1: the zero-current target, HIZ entry and HIZ exit sit where the knee puts the pin at 1.0, 0.4 and 0.8 V, each with
    the network's tolerance carried; at 8.70 V HIZ is not the specified state; V-A09 and FW-A18 carry those numbers."""
    R = _R()
    m = _CACHE["M"]
    K = R["knee"]
    tab = dict(K["table"])
    pin = lambda v: R["pin_off"] + R["s_k"] * (v - m.V_K0)
    assert abs(pin(K["zero"][1]) - 1.0) < 1e-9 and abs(pin(K["entry"][1]) - R["hiz"][0]) < 1e-9 and abs(pin(K["exit"][1]) - R["hiz"][1]) < 1e-9
    assert abs(R["hiz"][0] - 0.4) < 1e-12 and abs(R["hiz"][1] - 0.8) < 1e-12
    for key in ("zero", "entry", "exit", "rng"):
        lo, nom, hi = K[key]
        assert abs(lo - nom * (1 - m.T_KNEE)) < 1e-12 and abs(hi - nom * (1 + m.T_KNEE)) < 1e-12, key
    assert abs(tab[8.70] - 0.87578) < 1e-4 and tab[8.70] > R["hiz"][0] and 8.70 > R["v_hiz_lo"], "B1's 8.70 V reading"
    assert abs(R["v_hiz_lo"] - K["entry"][0]) < 1e-12 and abs(R["v_unhiz_hi"] - K["exit"][2]) < 1e-12
    assert K["entry"][1] < K["exit"][1] < K["zero"][1] < K["rng"][1] < R["vk1"]
    A = _apply_rows()
    for v in (K["entry"][1], K["entry"][0], K["entry"][2], K["exit"][1], K["exit"][0], K["exit"][2], K["zero"][1], K["zero"][0],
              K["zero"][2], K["rng"][2]):
        assert _has(A.V_A09, v), "V-A09 does not carry %.3f V" % v
    assert _has(A.FW_A18, R["v_hiz_lo"]) and _has(A.FW_A18, R["v_unhiz_hi"])
    assert "below 8.75 V" not in A.V_A09 and "8.43 V" not in A.V_A08 + A.FW_A18
    for word in ("RSNS_RAC", "before FW-A01", "2000h", "4100h", "falling", "rising"):
        assert word in A.V_A09, word


def t_v_a10_fault_injection_is_bounded():
    """B2: one bounded row covers stale and missing telemetry and the network seen to fail, and its fallback values never
    pass 4.70 A."""
    R = _R()
    D = R["diag"]
    assert D["max_fallback"] <= R["setting"] + 1e-12 and abs(D["stale"] - 1.55) < 1e-12
    assert abs(D["fallback"][12.0] - 2.05) < 1e-12 and D["trip12"] < D["pin_off_board"], "the injected failure would not trip"
    A = _apply_rows()
    row = A.V_A10
    for word in ("stopped for 30 s", "absent from boot", "two readings", "the third in a row", "%.3f A" % (D["trip12"] - _CACHE["M"].DIAG_A), "%.3f A" % D["trip12"],
                 "2.05 A at 12 V", "1.55 A", "older than 3 s", "no write above 4.70 A", "at most 10 s"):
        assert word in row, "V-A10 lacks: %s" % word
    assert "V-A10" in A.FW_A16 and "V-A10" in A.FW_A18


def t_b3_the_12_v_boundary_is_h3s_and_the_example_trades_the_vehicle():
    R = _R()
    F = R["flat"]
    assert abs(F["b12_h3"] - 49.7195) < 1e-3 and abs(F["b12"] - 38.74834) < 1e-4 and abs(F["s40"] - 12.34226) < 1e-4
    assert F["fe_max"] <= R["fe_h_max"] + 1e-12, "the example leaves the vehicle envelope"
    assert F["at"][1][1] < F["at"][1][2] and F["p12"][0] < F["p12"][1], "the example does not trade the 12 V vehicle"
    assert F["trk"][0] >= F["v_need"] and F["trk"][2] <= 36.0 and F["c35"] > max(f for _r, _v, rt, f in R["trk_parts"] if rt > 30)
    page = open(os.path.join(REC, "L4E5-SOURCE-CONTROL.md"), encoding="utf-8").read()
    assert "by any source-blind mechanism" not in page and "Meeting 12 V needs source identity" not in page
    assert "restricted to H3" in page and "not necessary" in page


def t_collapse_times_are_nominal_estimates():
    out = open(os.path.join(REC, "l4e5_source_control.out"), encoding="utf-8").read()
    assert "nominal estimates pending evidence of the effective capacitance" in out
    assert "the nominal capacitance an upper bound" not in out


def t_hiz_release_is_not_asserted_as_conversion():
    """Recheck B1: above the HIZ exit U3 is out of HIZ (with EN_HIZ = 0b), not proven to convert; regulation by the pin is
    asserted only from the start of TI's printed range, and between the two the behaviour is recorded."""
    import re
    R = _R()
    A = _apply_rows()
    page = open(os.path.join(REC, "L4E5-SOURCE-CONTROL.md"), encoding="utf-8").read()
    out = open(os.path.join(REC, "l4e5_source_control.out"), encoding="utf-8").read()
    bad = re.compile(r"converting (at every VIN_RAW )?above|certainly converting|converting at every")
    for name, text in (("the page", page), ("FW-A18", A.FW_A18), ("V-A09", A.V_A09), ("the output", out)):
        assert not bad.search(text), "%s asserts conversion at HIZ release: %s" % (name, bad.search(text).group(0))
    for name, text in (("FW-A18", A.FW_A18), ("V-A09", A.V_A09)):
        assert "out of HIZ above 8.713 V" in text or "out of HIZ at every VIN_RAW above 8.713 V" in text, name
        assert "EN_HIZ" in text, name
    rng_top = R["knee"]["rng"][2]
    assert _has(A.V_A09, rng_top) and "regulating its input current by the pin" in A.V_A09 and "conversion not asserted" in A.V_A09
    assert R["knee"]["exit"][2] < rng_top, "the regulation range would start below the HIZ release"
    assert "Out of HIZ is not proven conversion" in out and "out of HIZ (with EN_HIZ = 0" in out
    assert "Out of HIZ is not proven conversion" in page


def t_v_a10_boot_permits_initialization():
    """Recheck B2: telemetry absent from boot is split into (2i) the normal initialization from POR, permitted, verified and
    logged, and (2ii) no telemetry-caused change after it, every write at or under 4.70 A."""
    A = _apply_rows()
    row = A.V_A10
    i1, i2, i3 = row.find("(2i)"), row.find("(2ii)"), row.find("(3)")
    assert 0 < row.find("(1) after initialization") < i1 < i2 < i3, "V-A10's parts are not (1) after initialization, (2i), (2ii), (3)"
    seg_i, seg_ii = row[i1:i2], row[i2:i3]
    for word in ("permitted and verified", "logged from POR", "RSNS_RAC = 0b", "IIN_HOST 4.70 A", "VINDPM", "InputVoltage",
                 "at or under 4.70 A"):
        assert word in seg_i, "(2i) lacks: %s" % word
    assert "no write" not in seg_i and "no further write" not in seg_i, "(2i) forbids the initialization writes"
    for word in ("after initialization", "no change caused by the missing telemetry", "at or under 4.70 A"):
        assert word in seg_ii, "(2ii) lacks: %s" % word
    assert "absent from boot: no write" not in row
    page = open(os.path.join(REC, "L4E5-SOURCE-CONTROL.md"), encoding="utf-8").read()
    assert "(2i) Normal initialization from POR, permitted and verified" in page
    assert "In both cases there must be no write" not in page


def t_no_dash_characters_in_the_record():
    need(REC, "the L4-E5 record")
    for name in sorted(os.listdir(REC)):
        p = os.path.join(REC, name)
        if os.path.isfile(p):
            s = open(p, encoding="utf-8").read()
            assert "\u2013" not in s and "\u2014" not in s, "%s holds a dash character" % name
