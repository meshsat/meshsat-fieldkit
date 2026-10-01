"""Layer 4 task L4-E10 (MESHSAT-1357, 2 October 2026; v2/docs/records/l4e10/): FEA-008, the cell and thermal design of the
battery path, held as predicates on properties of what l4e10_cell_thermal.py computes.

The predicates: the thermal records it rests on are reproduced byte for byte and the committed .out is what the script
prints; every LO row of Layer 3's cell modes table has a decision of a known kind; a row recorded as closed or free of
collision rests on MAKER or bounded MODELED evidence only, and a row resting on INFERRED or ASSUMPTION figures is never
recorded as closed; no cell change is recorded as taken, and any cell route names the owner's approval; the collisions
are recomputed here in closed form and agree with Layer 3's table; the coupling measure's figures are recomputed here from
the W4 constants and the block's dimensions; the feasibility screen covers every row, rejects powered means where no power
exists and shows the storage hold time shorter than the exposure; the conflict names its requirements and offers at most
three options with the session's recommendation marked as not adopted; the page's figures are the .out's; the held files
are ignored by git and pinned alike in the script and the fetcher; no dash or claim word is written. Nothing here writes
into the tree.
"""
import ast
import hashlib
import importlib.util
import math
import os
import re
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e10")
SCRIPT = os.path.join(REC, "l4e10_cell_thermal.py")
OUT = os.path.join(REC, "l4e10_cell_thermal.out")
PAGE = os.path.join(REC, "L4E10-CELL-THERMAL.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}
HELD = ("v2/vendor/battery/held/samsung-inr18650-30q6-v1.0-2020.pdf", "v2/vendor/battery/held/samsung-inr18650-30q-v1.0-2015.pdf",
        "v2/vendor/battery/held/samsung-inr18650-30q6-draft-v0.1-2024.pdf", "v2/vendor/battery/held/lg-inr18650hg2-rev0-2014.pdf")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _R():
    if "R" not in _CACHE:
        need(SCRIPT, "the L4-E10 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script finds the tree by git)")
        for rel in HELD:
            need(os.path.join(ROOT, rel), "a held cell specification (v2/docs/records/l4e10/fetch_held_back.py)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        try:
            import yaml  # noqa: F401
        except ImportError:
            raise Skip("PyYAML is needed")
        m = _load("l4e10_cell_thermal_under_test", SCRIPT)
        try:
            R = m.compute()
            text = "\n".join(m.render(R)) + "\n"
        except SystemExit as e:
            raise AssertionError("l4e10_cell_thermal.py refused (exit %s)" % e.code)
        _CACHE.update(R=R, M=m, text=text)
    return _CACHE["R"]


def t_records_reproduced_and_out_is_what_the_script_prints():
    R = _R()
    for k in ("r0a", "r0b", "r0c", "r0d"):
        assert R[k] is True, "reproduction %s failed" % k
    assert _CACHE["text"].encode("utf-8") == open(OUT, "rb").read(), "the committed .out is not what the script prints"


def t_every_lo_row_has_a_decision_of_a_known_kind():
    R = _R()
    import yaml
    l3 = yaml.safe_load(open(os.path.join(ROOT, "v2/docs/handover/layer3/l3r2.yaml"), encoding="utf-8"))
    ids = sorted(m["id"] for m in l3["cell_modes"])
    assert ids == sorted(R["dec"]), "decisions %s against Layer 3's rows %s" % (sorted(R["dec"]), ids)
    kinds = {"CLOSED", "CONDITIONAL", "NO_COLLISION", "NOT_CLOSABLE"}
    assert all(d["decision"] in kinds for d in R["dec"].values())
    for k in ("LO-01a", "LO-01d", "LO-01e", "LO-01f", "LO-01g", "LO-01h"):   # FEA-008's blocker rows
        assert R["dec"][k]["verify"], "%s has no verification" % k


def t_closed_rows_rest_on_maker_or_bounded_modeled_only():
    R = _R()
    for k, d in R["dec"].items():
        assert set(d["evidence"]) <= set(R["classes"]), "%s carries an unknown class" % k
        if d["decision"] in ("CLOSED", "NO_COLLISION"):
            assert set(d["evidence"]) <= {"MAKER", "MODELED"} and d["bounded"], "%s is %s on %s" % (k, d["decision"], d["evidence"])
        if {"INFERRED", "ASSUMPTION"} & set(d["evidence"]):
            assert d["decision"] != "CLOSED", "%s is closed on INFERRED or ASSUMPTION evidence" % k


def t_no_cell_change_is_taken_without_the_owner():
    R = _R()
    for k, d in R["dec"].items():
        cc = d["cell_change"]
        if cc is not None:
            assert cc["taken"] is False and cc["owner_approval_required"] is True, "%s records a cell change as taken" % k
    page = open(PAGE, encoding="utf-8").read()
    assert "no cell change is taken" in page
    assert not re.search(r"(?<!no )cell change (is|was) taken", page.replace("No row is recorded as CLOSED, and no cell change is taken", ""))
    b = " ".join(_CACHE["M"].option_lines(R))
    assert "spend approval" in b and "not adopted" in b


def t_collisions_recomputed_in_closed_form_agree_with_layer3():
    R = _R()
    qR, pR = R["heat"]["SURVR"]
    qS, pS = R["heat"]["SURV"]
    air = 40.0 + (qR + pR) / 1.06
    assert abs(math.floor(air * 10 + 1e-9) / 10 - R["modes"]["LO-01a"]["req_c"]) < 1e-9
    assert abs(air - 60.0 - R["gaps"]["LO-01a"]) < 1e-9
    cell = air + pR / R["blk"]["h"][0] / R["blk"]["A"]
    assert abs(cell - R["a"]["cell_closed_W4_pack"]) < 1e-9 and cell > air, "the cells on the pack are not above the air by their I2R"
    lo, hi = 55.0 + (qS + pS) / 3.3, 55.0 + (qR + pR) / 1.22
    assert abs(lo - R["d"]["air_lo"]) < 1e-9 and abs(hi - R["d"]["air_hi"]) < 1e-9
    assert abs(math.floor(hi * 10 + 1e-9) / 10 - R["modes"]["LO-01d"]["req_c"]) < 1e-9
    assert abs(round(60.0 + (qS + pS) / 3.3, 2) - R["modes"]["LO-01e"]["req_c"]) < 1e-9
    assert R["gaps"]["LO-01f"] == R["modes"]["LO-01f"]["req_c"] - R["modes"]["LO-01f"]["limit_c"] == 11.0
    assert R["gaps"]["LO-01g"][0] == R["modes"]["LO-01g"]["limit_c"] - R["modes"]["LO-01g"]["req_c"] == 13.0
    assert all(v[2] for v in R["agree"].values())


def t_coupling_measure_recomputed_from_its_inputs():
    R = _R()
    w4 = {}
    tree = ast.parse(open(os.path.join(ROOT, "v2/docs/records/w4/w4-scratch-thermal.py"), encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ("H_OUT_WALL", "H_OUT_FLOOR", "T_OVER_K_WALL", "H_IN_FANS"):
            w4[n.targets[0].id] = ast.literal_eval(n.value)
    X, Y, Z = R["blk"]["X"], R["blk"]["Y"], R["blk"]["Z"]
    aE, aB = Y * Z, X * Y
    aI = 2 * (X * Y + X * Z + Y * Z) - aE - aB
    m = _CACHE["M"]
    gE = 1 / (R["m4b_gap_max_mm"] / 1000 / (m.K_PAD * aE) + w4["T_OVER_K_WALL"] / aE + 1 / (w4["H_OUT_WALL"][0] * aE))
    gB = 1 / (m.T_MAT / (m.K_MAT * aB) + w4["T_OVER_K_WALL"] / aB + 1 / (w4["H_OUT_FLOOR"][0] * aB))
    gI = R["blk"]["h"][1] * aI
    assert abs(gE + gB - R["worst"]["g_amb"]) < 1e-12 and abs(gI - R["worst"]["g_in"]) < 1e-12
    f = gI / (gI + gE + gB)
    assert abs(f - R["worst"]["f"]) < 1e-12 and 0 < R["best"]["f"] < f < 1
    # the two-node model reduces to pwr_budget's cell_temp with no skin path, and the measure lowers the worst corner
    assert R["meas"]["two_node_matches_record"]
    assert R["meas"]["a_pack_worst"][1] < R["a"]["cell_closed_W4_pack"]
    assert R["meas"]["a_pack_worst"][1] <= 60.0 < R["a"]["cell_closed_W4_pack"], "the measure's stated effect on LO-01a"
    # it cannot close the +55 C margin: the cells stay above H1's reading at every corner
    assert R["meas"]["d_best"][1] > R["hot"]["H1"] and R["meas"]["d_worst"][1] > 60.0
    # the cold-end cost is carried, and charging at the cold end clears the panel's hold with the existing mat
    assert R["cold"]["meas"][1] < R["cold"]["base"][1] and R["cold"]["p_h"] > 0
    assert R["cchg"]["base"][1] > R["cchg"]["hold"] and R["cchg"]["meas"][1] > R["cchg"]["hold"]


def t_screen_covers_every_row_and_judges_power_and_hold_time():
    R = _R()
    rows = R["screen"]
    assert set(r["lo"] for r in rows if r["lo"]) == set(R["dec"])
    for r in rows:
        assert r["power"] and r["gap"] and r["result"], r["id"]
        if r["zero_power"]:
            assert r["power"].startswith("zero"), r["id"]
            assert not r["result"].startswith("CREDIBLE: thermal"), "%s credits a thermal design with no power" % r["id"]
    for k in ("LO-01d", "LO-01e", "LO-01f", "LO-01g"):
        rr = [r for r in rows if r["lo"] == k]
        assert rr and all(r["result"].startswith("REJECTED") for r in rr), "%s is not rejected for thermal design" % k
    H = R["hold"]
    assert 3 * H["tau_kit_s"][1] < R["f"]["hours"] * 3600.0 and 3 * H["tau_pack_s"][1] < H["e3o_s"]
    assert min(H["e_hold_cold_Wh"]) > H["pack_Wh_nom"]


def t_conflict_and_owner_options():
    R = _R()
    m = _CACHE["M"]
    c = " ".join(m.conflict_lines(R))
    for tok in ("D-02a", "SC-03", "D-06", "REQ-074", "REQ-051", "D-29", "F2"):
        assert tok in c, "the conflict does not name %s" % tok
    opts = [l for l in m.option_lines(R) if re.match(r"^[A-Z]\. ", l)]
    assert 1 <= len(opts) <= 3
    assert "Session's recommendation (not adopted" in " ".join(m.option_lines(R))
    assert R["meets"]["30Q6"]["LO-01h"] is False and R["meets"]["35E"]["LO-01h"] is True, "S2's year row"
    assert not any(R["meets"]["35E"][k] for k in ("LO-01d", "LO-01e", "LO-01f", "LO-01g"))
    assert R["maker_floor"] > R["g"]["amb"] and R["maker_top"] < R["f"]["amb"], "a held maker's sheet covers a storage margin"


def t_page_figures_are_the_outs():
    R = _R()
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    figs = ["63.29", "62.12", "56.22", "1.246", "1.164", "1.530", "1.410", "58.64", "51.99", "57.97", "0.824", "0.485", "61.94",
            "-10.24", "-5.52", "0.39 W", "14.69", "15.68", "6.7 to 13.7", "0.77 to 2.66", "1081 to 4457", "0.21 K", "0.18 K",
            "185 to 383", "218 to 452", "144.7", "127.4", "121.0", "108.1", "95.2", "90.4", "2.52", "2.22", "2.11", "11.9", "16.4",
            "44.3", "71.4", "1.37 to 3.24", "56.37 to 58.24", "61.63", "74.22", "66.63", "79.22", "1554 to 3773", "3.66"]
    for f in figs:
        assert f in out, "%s not in the .out" % f
        assert f in page, "%s not on the page" % f


def t_held_files_ignored_and_pinned_alike():
    R = _R()
    fhb = _load("l4e10_fetch_under_test", os.path.join(REC, "fetch_held_back.py"))
    pins = R["pins"]
    for rel, _url, want in fhb.DOCS:
        assert pins.get(rel) == want, "%s pinned differently in the script and the fetcher" % rel
        r = subprocess.run(["git", "-C", ROOT, "check-ignore", "-q", rel])
        assert r.returncode == 0, "%s is not ignored by git" % rel
    src = open(os.path.join(ROOT, "v2/vendor/sources.txt"), encoding="utf-8").read()
    for rel in list(HELD) + ["v2/vendor/battery/molicel-inr18650-p28a-v1.pdf"]:
        line = [l for l in src.splitlines() if l.startswith(rel[len("v2/vendor/"):] + " ")]
        assert line and hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest() in line[0], "no source line for %s" % rel


def t_no_dash_or_claim_word():
    files = [SCRIPT, OUT, PAGE, os.path.join(REC, "README.md"), os.path.join(REC, "fetch_held_back.py")]
    files += [os.path.join(REC, "clarification", f) for f in sorted(os.listdir(os.path.join(REC, "clarification")))]
    rx = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives|rated for)\b", re.I)
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert "–" not in t and "—" not in t, "%s carries an en or em dash" % p
        assert not rx.search(t), "%s carries a claim word: %s" % (p, rx.search(t).group(0))
