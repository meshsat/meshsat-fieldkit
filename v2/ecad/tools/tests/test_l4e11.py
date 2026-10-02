"""Layer 4 task L4-E11 (MESHSAT-1357, 2 October 2026; v2/docs/records/l4e11/): source-only and dead-pack operation (U-04),
the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09), held as predicates on the values
l4e11_power.py computes, recomputed here in closed form where the property is arithmetic.

The predicates: the committed .out is what the script prints; no mandatory requirement names a load state for a source alone
and the record quotes REQ-015 as the registry holds it; the charger's rows are the maker's and CHRG_OK names no battery; the
holds never cut the source while the pack cannot discharge (the drafts say so); rule R-b keeps Q2's junction under its
maximum where 3 A would not; the drawn UVLO's maximum is over 9 V and the drafted one under it; the plug's 9 V gives less than
VIN_RAW's; no owner question is forced and the reason is a part choice, not a capability; the drawn interconnect fails the
weak-source band and the selected one covers it while a stiff source stays under F1's 1000 A only with the length floor; the
selected timer pair meets both ends and is the only stocked set of at most two parts that does; the start counts the new
capacitors and the load, and the front end cannot overlap it; each draft checks, applies once, refuses twice and refuses the
tree's own generator, and both compose with L4-E9's hot-swap draft in the stated order; every figure carries a class; every
downstream item has one owner and an acceptance; no em or en dash and no claim word. Nothing here writes into the tree:
drafts run on temporary copies. Software tests establish this record's own behaviour only.
"""
import hashlib
import importlib.util
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e11")
SCRIPT = os.path.join(REC, "l4e11_power.py")
OUT = os.path.join(REC, "l4e11_power.out")
PAGE = os.path.join(REC, "L4E11-SOURCE-ONLY-AND-ENTRY.md")
GEN_E = os.path.join(TOOLS, "gen_sch_e.py")
DRAFTS = ("apply_gen_sch_e_uvlo.py", "apply_gen_sch_e_timer.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_CACHE = {}


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _M():
    if "M" not in _CACHE:
        need(SCRIPT, "the L4-E11 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script reads L4-E9's commit with git)")
        for tool in ("pdftotext", "pdftocairo"):
            if shutil.which(tool) is None:
                raise Skip("%s is needed" % tool)
        sp = importlib.util.spec_from_file_location("l4e11_power_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for _k, (rel, _s) in m.PINS.items():
            need(os.path.join(ROOT, rel), "an input of the L4-E11 record (held documents: its fetch_held_back.py)")
        if subprocess.run(["git", "-C", ROOT, "cat-file", "-e", m.L4E9_COMMIT], capture_output=True).returncode != 0:
            raise Skip("L4-E9's commit %s is not in this repository" % m.L4E9_COMMIT[:8])
        _CACHE["M"] = m
    return _CACHE["M"]


def _R():
    if "R" not in _CACHE:
        m = _M()
        _CACHE["gen_before"] = _sha(GEN_E)
        try:
            _CACHE["R"] = m.compute()
        except SystemExit as e:
            raise AssertionError("l4e11_power.py refused (exit %s)" % e.code)
    return _CACHE["R"]


def t_the_committed_output_is_what_the_script_prints():
    _M()
    r = subprocess.run([sys.executable, SCRIPT], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l4e11_power.out is not what l4e11_power.py prints"


def t_no_mandatory_requirement_names_a_source_only_load_and_req015_is_quoted_verbatim():
    R = _R()
    assert R["no_mandatory_state"]
    reg = yaml.safe_load(open(os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml"), encoding="utf-8"))
    r15 = [r for r in reg["records"] if r.get("id") == "REQ-015"][0]
    stmt = " ".join(str(r15["statement"]).split())
    assert R["req015"][0] == stmt
    assert not re.search(r"\bPS-[A-Z]", stmt + " " + str(r15["acceptance"])), "REQ-015 names a power state"
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert stmt in page, "the record does not quote REQ-015's statement as the registry holds it"
    objective = [row for row in R["req_rows"] if row[1] == "OBJECTIVE"]
    assert [row[0] for row in objective] == ["REQ-072"], "only REQ-072 is an objective"


def t_the_charger_rows_are_the_makers_and_chrg_ok_names_no_battery():
    R = _R()
    B = R["B"]
    assert abs(B["iclamp"] - 0.384) < 1e-9 and B["vsysmin4s"] == 12.3 and B["cv4s"] == 16.8 and B["csys_uf"] == 50.0
    assert "the system is powered from adapter through the charger" in B["sec11_text"]
    assert "batter" not in B["chrgok_text"].lower() and "VBUS is above" in B["chrgok_text"]
    assert R["strap"][2] > 68.4 and R["strap"][2] < 81.5, "the strap is not in the 4S window"


def t_the_holds_never_cut_the_source_while_the_pack_cannot_discharge():
    R = _R()
    assert "below 0 C" in R["fwc08"], "FW-C08 as written no longer asserts SHORE_INHIBIT on the cold hold"
    page = open(PAGE, encoding="utf-8").read()
    assert "Finding U4-F1" in page and "never for a temperature or 'no charge' hold" in page
    assert "never while the pack cannot discharge" in page
    assert "R-a." in page and "never assert" in page


def t_rule_rb_keeps_q2_under_its_maximum_where_three_amps_would_not():
    R = _R()
    P = R["P"]
    air = R["F"]["air_hot"]
    rows = {round(i, 3): (w, dt) for i, w, dt in P["q2"]}
    w1, dt1 = rows[1.0]
    w3, dt3 = rows[3.0]
    assert w1 <= 1.0 + 1e-9 and air + dt1 < P["tj_max"], "R-b's 1.0 A does not keep Q2 under its TJ"
    assert air + dt3 > P["tj_max"], "3 A through the diode would be inside TJ: R-b would not be needed"
    assert abs(P["rb_imbalance"] - 0.25) < 1e-9


def t_the_uvlo_draft_puts_the_entry_on_under_nine_volts():
    R = _R()
    E = R["E"]
    uv = E["uv_rows"]
    hi = lambda r21: uv[2] * (1 + 100e3 * 1.01 / (r21 * 0.99))
    assert abs(hi(38.3e3) - E["uvlo_drawn"][0][2]) < 1e-9 and hi(38.3e3) > 9.0, "the drawn UVLO's maximum is not over 9 V"
    assert hi(42.2e3) < 9.0, "the drafted UVLO's maximum is not under 9 V"
    falling_hi = E["uvlo_new"][1][2]
    assert falling_hi < E["k0"] and falling_hi < 7.86, "the drafted UVLO's falling band reaches the knee or the guard"
    draft = open(os.path.join(REC, "apply_gen_sch_e_uvlo.py"), encoding="utf-8").read()
    assert "on by %.2f V" % E["uvlo_new"][0][2] in draft, "the draft's label is not the computed maximum"


def t_nine_volts_at_the_plug_gives_less_than_at_vin_raw():
    R = _R()
    E = R["E"]
    for k in ("drawn", "selected"):
        pl = E["plug"][k]
        assert pl["vin"] < 9.0 and pl["w"] < E["env"][9.0]["w_lo"], "the plug's 9 V is not the finding the record states"
        assert pl["knee_top"] < 9.0
    assert E["plug"]["selected"]["r"] < E["plug"]["drawn"]["r"]


def t_no_owner_question_is_forced_and_the_reason_is_a_part_choice():
    R = _R()
    F = R["F"]
    assert F["owner_question"] is False
    plans = {n: pl for n, (_lo, pl, _hi) in R["E"]["states"].items()}
    assert max(plans.values()) < F["cap9_15a_hot_w"], "a 15 A part would not lift the hottest cap over every state"
    assert all(pl <= F["cap9_cold_w"] for n, pl in plans.items() if "cold" in n or "warm-up" in n)


def t_d06_the_drawn_interconnect_fails_and_the_selected_one_covers_the_band():
    R = _R()
    D = R["D"]
    assert not D["drawn_met"]
    assert D["cont_need"] == 13.5 and D["band"][0] == (13.5, 600.0) and D["band"][1][0] == 20.0
    assert D["c12"] >= 20.0 >= D["cont_need"] and D["xt60"] >= 20.0 and D["c16"] < D["cont_need"]
    assert D["sel_ok"]


def t_d06_a_stiff_source_stays_under_f1_only_with_the_length_floor():
    R = _R()
    D = R["D"]
    rho = 0.01724 * (1 + 0.00393 * (-20.0 - 20.0))
    ipf = lambda cable_m, mm2: 43.18 / ((2 * cable_m + 1.0) * rho / mm2)
    assert abs(ipf(3.0, 2.081) - D["sel_ipf"]) < 0.05 and D["sel_ipf"] <= 1000.0
    assert ipf(2.0, 2.081) > 1000.0, "the floor is not load-bearing: 2 m of AWG 14 already stays under 1000 A"
    assert D["min_len_14"] <= 3.0 and ipf(D["min_len_14"], 2.081) <= 1000.0 + 1e-6
    assert D["min_fault_9v"] >= 6.0 * D["rating"], "the lowest stiff fault at 9 V is not past the 600 % row"


def t_d09_the_selected_pair_meets_both_ends_and_is_the_only_one():
    R = _R()
    T = R["T9"]
    S = T["sel"]
    tmin = S["lo"] * 3.76 / 120e-6
    tmax = S["hi"] * 4.16 / 51e-6
    assert abs(tmin - S["tmin"]) < 1e-12 and abs(tmax - S["tmax"]) < 1e-12
    assert tmin >= 1.5 * T["start_max"], "the fault time's minimum is under TI's half-again margin"
    soa = T["i10"] * (10e-3 / tmax) ** (math.log(T["i1"] / T["i10"]) / math.log(10.0)) * T["derate"]
    assert soa >= T["pulse_a"], "the pulse passes Figure 10 at the fault time's maximum"
    ok = [r["lab"] for r in T["cands"] if r["start_ok"] and r["soa_ok"] and len(r["parts"]) <= 2]
    assert ok == [S["lab"]], ok
    assert T["sel_codes"] == ("C907944", "C3847777")
    assert T["c5_l9"][0] < T["need"], "C5 as drawn would meet the margin: D-09 would not be a defect"


def t_d09_the_start_counts_the_new_capacitors_the_load_and_no_front_end():
    R = _R()
    T = R["T9"]
    assert abs(T["c_uf"] - 34.0) < 1e-9
    refs = sorted((b, r) for b, r, _n, _c in T["caps"])
    assert ("E", "C6") in refs and ("A", "C207") in refs and ("A", "C210") in refs
    assert T["start_max"] > T["start_max_noload"] > T["start_l9"][1]
    assert T["ctr2_ms"][0] * 1e-3 > 10.0 * T["start_max"], "U34's release could overlap the start"


def _run(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, cwd=cwd)


def t_each_draft_checks_applies_once_refuses_twice_and_refuses_the_tree():
    _R()
    before = _sha(GEN_E)
    with tempfile.TemporaryDirectory() as d:
        for name in DRAFTS:
            tgt = os.path.join(d, "gen_" + name)
            shutil.copy(GEN_E, tgt)
            script = os.path.join(REC, name)
            r = _run([script, tgt])
            assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-300:]
            assert _sha(tgt) == before, "--check wrote"
            r = _run([script, tgt, "--write"])
            assert r.returncode == 0 and b"WRITTEN" in r.stdout
            r = _run([script, tgt, "--write"])
            assert r.returncode == 3, "a second application was not refused"
            r = _run([script, GEN_E, "--write"])
            assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
    assert _sha(GEN_E) == before, "a draft wrote into the tree"


def t_both_drafts_compose_with_l4e9s_hotswap_draft_in_the_stated_order():
    m = _M()
    rel, want = m.GIT_PINS["l4e9_hotswap"]
    blob = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (m.L4E9_COMMIT, rel)], capture_output=True).stdout
    assert hashlib.sha256(blob).hexdigest() == want
    uv, tm = (os.path.join(REC, n) for n in DRAFTS)
    with tempfile.TemporaryDirectory() as d:
        hs = os.path.join(d, "hotswap.py")
        open(hs, "wb").write(blob)
        a, b, c = (os.path.join(d, x) for x in ("a.py", "b.py", "c.py"))
        for p in (a, b, c):
            shutil.copy(GEN_E, p)
        for s in (hs, uv, tm):
            assert _run([s, a, "--write"]).returncode == 0
        for s in (tm, hs, uv):
            assert _run([s, b, "--write"]).returncode == 0
        assert open(a, "rb").read() == open(b, "rb").read(), "the timer draft's order changes the result"
        txt = open(a, encoding="utf-8").read()
        assert 'r("R21", "42.2k 1%' in txt and 'r("R24", "22k 1%' in txt and 'c("C121", "68n C0G 5%' in txt
        assert _run([uv, c, "--write"]).returncode == 0
        assert _run([hs, c, "--write"]).returncode == 3, "L4-E9's draft after this one should refuse (the stated order)"


def t_every_figure_carries_a_class():
    text = open(OUT, encoding="utf-8").read().splitlines()
    fig = re.compile(r"\d(?:\.\d+)?\s*(?:V|A|W|ms|s|K|C|ohm|mOhm|uF|nF|mm2|%|A2s|mA|uA|mV|k|m)\b")
    cls = re.compile(r"\b(MAKER|CATALOGUE|NETLIST|REQUIREMENT|RECORD|INFERRED|CONDITIONAL|ASSUMPTION|SESSION|PENDING)\b")
    ind = lambda s: len(s) - len(s.lstrip(" "))
    sec, bad, i = None, [], 0
    while i < len(text):
        ln = text[i]
        m = re.match(r"^(\d)\. ", ln)
        if m:
            sec, i = int(m.group(1)), i + 1
            continue
        grp, j = [ln], i + 1
        while j < len(text) and text[j].strip() and ind(text[j]) > ind(ln) and not re.match(r"^\d\. ", text[j]):
            grp.append(text[j])
            j += 1
        if sec not in (None, 0, 8) and any(fig.search(g) for g in grp) and not cls.search(" ".join(grp)):
            bad.append(ln.strip()[:90])
        i = j
    assert not bad, "figures without a class: %s" % bad[:5]


def t_every_downstream_item_has_one_owner_and_an_acceptance():
    R = _R()
    m = _M()
    owners = {"Layer 4 coordinator", "Layer 5 interfaces", "Layer 6 components", "Layer 7 mechanical",
              "Layer 8 board E generator owner", "Layer 9 pre-layout analysis", "prototype bench", "firmware owner", "CONOPS owner"}
    items = m.downstream(R)
    assert [x[0] for x in items] == ["E11-%02d" % k for k in range(1, len(items) + 1)]
    page = open(PAGE, encoding="utf-8").read()
    for iid, kind, owner, acc in items:
        assert owner in owners, "%s: owner %r" % (iid, owner)
        assert len(acc) > 40, "%s has no acceptance" % iid
        row = [l for l in page.splitlines() if l.startswith("| %s |" % iid)]
        assert len(row) == 1 and ("| %s |" % owner) in row[0], "%s is not in the record's table with its owner" % iid


def t_the_record_carries_the_outputs_numbers():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    for s in ("4.927 to 14.653", "883.5", "1236.9", "8.14 / 8.42 / 8.71", "8.72 / 9.03 / 9.34", "19.7 to 36.6", "3.062", "4.593",
              "0.71 A", "59.5 W", "89.6 W", "8.318", "8.465"):
        assert s in page and s in out, "%s is not in both the record and the output" % s


CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def t_no_dashes_and_no_claim_words():
    reg = yaml.safe_load(open(os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml"), encoding="utf-8"))
    quoted = [" ".join(str(r.get("statement", "")).split()) for r in reg["records"] if r.get("id") in ("REQ-015",)]
    files = [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.endswith((".md", ".py", ".out"))]
    files += [os.path.join(REC, "inputs", f) for f in sorted(os.listdir(os.path.join(REC, "inputs")))]
    files.append(os.path.abspath(__file__))
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
        if p != os.path.abspath(__file__):
            flat = " ".join(t.split())
            for q in quoted:
                flat = flat.replace(q, "")      # a quoted approved requirement is the owner's text, not this record's claim
            m = CLAIM.search(flat)
            assert not m, "%s carries a claim word: %r" % (os.path.relpath(p, ROOT), m.group(0))
