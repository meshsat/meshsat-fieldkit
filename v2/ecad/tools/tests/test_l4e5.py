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
prints; the draft apply script checks without writing, applies once to a copy and refuses a second application. Nothing
here writes into the tree.
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
    assert abs(w["POR reset"] - 3.25) < 1e-12 and abs(w["after every adapter removal (reset)"] - 3.25) < 1e-12
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
        assert "| FW-A18 |" in text and "| V-A09 |" in text and "| 1 (L4-E5) |" in text
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


def t_no_dash_characters_in_the_record():
    need(REC, "the L4-E5 record")
    for name in sorted(os.listdir(REC)):
        p = os.path.join(REC, name)
        if os.path.isfile(p):
            s = open(p, encoding="utf-8").read()
            assert "\u2013" not in s and "\u2014" not in s, "%s holds a dash character" % name
