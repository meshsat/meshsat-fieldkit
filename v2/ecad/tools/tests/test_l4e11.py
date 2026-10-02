"""Layer 4 task L4-E11 (MESHSAT-1357, 2 October 2026; v2/docs/records/l4e11/): source-only and dead-pack operation (U-04),
the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09), held as predicates on the values
l4e11_power.py computes, recomputed here in closed form where the property is arithmetic.

The predicates (the fix round and the final round of 2 October 2026 included): the committed .out is what the script prints; no mandatory
requirement names a load state for a source alone and the record quotes REQ-015 as the registry holds it; the charger's rows
are the maker's and CHRG_OK names no battery; the charge holds are a state table that keeps the source carrying the kit (B2);
rule R-b's register value bounds the actual current and Q2's junction where 3 A would not (B5); the LM5069 cannot start from a
9.00 V plug by TI's Equations 38 to 40 and POREN (B1); the selected entry sits between the in-service maximum and F1, and its
pass FET carries a start into a resistive fault where the drawn one does not; the corrected knee and the guard clear the plug's
operating point and the functional warm-up is carried at its plan figure (B3); the plug's 9 V through the drawn knee gives less
than VIN_RAW's; no owner question is forced and the losses lower every ceiling; the weak-source envelope is monotone (B4), the
drawn interconnect fails it, and a stiff source stays under F1's 1000 A only with the resistance floor; the selected timer pair
meets both ends and is the only stocked set of at most two parts that does; the start counts the new capacitors and the load;
each draft checks, applies once, refuses twice and refuses the tree's own generator, and they compose with L4-E9's hot-swap
draft as stated, the entry and timer drafts excluding each other; every figure carries a class; every downstream item has one
owner and an acceptance; no em or en dash and no claim word. The final round adds: the efficiency floor couples the current
and the voltage and reproduces the check's 6.36376 A at 0.908691; the breaker's delay is TI's loaded row and the scan carries the
short-circuit filter and the delays; REQ-015 at the plug is a CONDITIONAL CANDIDATE on a bounded shedding sequence; the
specified resistance floor keeps a stiff source at 900 A and the last interval and the obligations reach it; R-b permits two
settings and its bound holds only inside TI's row condition. Nothing here writes into the tree: drafts run on temporary copies.
Software tests establish this record's own behaviour only.
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
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
DRAFTS = (("apply_gen_sch_e_entry.py", GEN_E, True), ("apply_gen_sch_e_timer.py", GEN_E, False), ("apply_gen_sch_a_guard.py", GEN_A, False))
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


def t_the_charge_holds_are_a_state_table_that_keeps_the_source_carrying_the_kit():
    R = _R()
    assert "below 0 C" in R["fwc08"], "FW-C08 as written no longer asserts SHORE_INHIBIT on the cold hold"
    out = open(OUT, encoding="utf-8").read()
    for s in ("S1 charge on, discharge on", "S2 charge on, discharge off", "S3 charge off, discharge on", "S4 charge off, discharge off"):
        assert s in out, "the state table lacks %r" % s
    assert "so the gauge does NOT hold the charge" in out, "S2's counterexample (a warm CUV) is not stated"
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "Finding U4-F1" in page and "never for a temperature or 'no charge' hold" in page
    assert "| S2 |" in page and "N2" in page and "OPEN" in page, "the record's state table does not keep N2 open for S2"
    assert "THE ONE EXCEPTION" in out and "THE HOLD PERSISTS ACROSS STATES" in out, "S4's exception or the hold's persistence is not stated"
    assert "The one exception to the bit" in page and "The hold persists across states" in page
    assert "CHRG_INHIBIT bit" in page and "the CHG_INHIBIT line (HIZ) and SHORE_INHIBIT are never a charge hold" in page
    assert "carried by the pack either way" not in page, "the first round's REQ-077 fallback is still in the record"


def t_rule_rb_bounds_the_actual_current_and_keeps_q2_under_its_maximum_where_three_amps_would_not():
    R = _R()
    P, N = R["P"], R["N"]
    air = R["F"]["air_hot"]
    assert N["rb_err"] == (0.18, 0.215), "the 0x0200 row is not TI's -18 / +21.5 %"
    assert abs(N["rb_max"] - 1.024 * 1.215 / 0.99) < 1e-12 and abs(N["rb_max"] - 1.2567) < 1e-4
    assert air + N["rb_max"] * P["vsd_max"] * P["rja"] < P["tj_max"], "R-b's actual maximum does not keep Q2 under its TJ"
    rows = {round(i, 3): (w, dt) for i, w, dt in P["q2"]}
    assert air + rows[3.0][1] > P["tj_max"], "3 A through the diode would be inside TJ: R-b would not be needed"
    assert abs(P["rb_imbalance"] - 0.25) < 1e-9
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "0x0000 (no charge) and 0x0200" in page and "0 to 85 C" in page and "21.22 W" in page
    assert N["rb_temp"] == (0.0, 85.0), "the accuracy row's temperature condition is not TI's 0 to 85 C"
    assert abs(N["dead_charge_w_max"] - N["rb_max"] * R["cv_max"]) < 1e-12 and abs(N["dead_charge_w_max"] - 21.2186) < 1e-3
    out = open(OUT, encoding="utf-8").read()
    assert "(ii) SRN at or above VSYS_MIN with the charger outside 0 to 85 C" in out and "INCONCLUSIVE" in out
    assert "CONDITIONAL: on R-b's bound holding" in out, "Q2's junction is not kept conditional"


def t_the_lm5069_cannot_start_from_a_nine_volt_plug():
    R = _R()
    E, N = R["E"], R["N"]
    uv, hy = E["uv_rows"], E["hy_rows"]
    rise_hi = lambda r21: uv[2] * (1 + 100e3 * 1.01 / (r21 * 0.99)) + hy[2] * 100e3 * 1.01      # SNVS452G Equation 38 at its corners
    for r21, got in ((38.3e3, N["uvlo_drawn"]), (42.2e3, N["uvlo_withdrawn"])):
        assert abs(rise_hi(r21) - got[0][2]) < 1e-9 and rise_hi(r21) > 9.0
        assert abs(uv[1] * (1 + 100e3 / r21) - got[1][1]) < 1e-9, "the falling threshold is not Equation 39"
    assert abs(rise_hi(38.3e3) - 12.372) < 1e-3 and abs(rise_hi(42.2e3) - 11.745) < 1e-3, "not the check's reproduced corners"
    assert N["poren"] == (8.4, 9.0) and abs(N["vin_ic_max"] - (9.0 - 0.013)) < 1e-12 and not N["poren_met"]
    assert not os.path.exists(os.path.join(REC, "apply_gen_sch_e_uvlo.py")), "the withdrawn R21 draft is still in the record"
    src = open(SCRIPT, encoding="utf-8").read()
    assert "uvlo_new" not in src and "R21_NEW_K" not in src, "the obsolete UVLO model is still in the script"


def t_the_selected_entry_sits_between_the_in_service_maximum_and_f1():
    R = _R()
    N, F = R["N"], R["F"]
    lo = 29.2e-3 * (1 - 0.002 - 0.005) / (4.5e-3 * 1.01 * (1 + 50e-6 * 50))
    hi = 31.5e-3 * (1 + 0.002 + 0.005) / (4.5e-3 * 0.99 * (1 + 50e-6 * (-45)))
    assert abs(N["ioc"][0] - lo) < 1e-9 and abs(N["ioc"][2] - hi) < 1e-9
    assert N["i9"] < N["ioc"][0] and N["ioc"][2] <= F["f_hot_a"], "the breaker is not between the in-service maximum and F1"
    assert N["imax_all"] == max(e["i_max"] for e in N["env"].values()) and N["imax_all"] < N["ioc"][0]
    assert N["uv_rise"][2] < N["dcp_noload"] and N["uv_fall"][2] < N["dcp9"], "the UVLO does not clear the plug's 9 V"
    assert N["cs101_peak"] < N["ov_rise"][0] and N["ov_rise"][2] < N["d10"][1] and N["ov_fall"][0] > 36.0
    assert N["t63_ilim"][0] < N["i9"], "the TPS1663 would carry the in-service maximum: its rejection is wrong"
    assert N["isc"][0] > N["ioc"][2] and max(N["pins_at_clamp"]) < N["t48_pin_abs"] and N["inp_on_at"] < N["uv_rise"][0]
    assert N["l2_rise"] + F["air_hot"] < 105.0 and N["cbst_need"] < 1e-6


def t_the_selected_fet_carries_a_fault_start_where_the_drawn_one_does_not():
    R = _R()
    N = R["N"]
    (d_name, d_worst, d_start), (k_name, k_worst, k_start) = N["scan"]
    assert "CSD19532Q5B" in d_name and "CSD19536KTT" in k_name
    assert d_worst[0] > 1.0, "the drawn FET would carry a fault start: the FET change would not be needed"
    assert k_worst[0] < 1.0 and k_start < 1.0, "the selected FET does not carry a fault start on its derated chart"
    assert "short-circuit trip" in k_worst[3] or "overcurrent" in k_worst[3]
    assert N["hs_start"][2] < 1.0 and N["hs_start"][0] > N["isc"][2], "the start into a hard short is not bounded past the threshold"
    assert abs(N["ktt_at"]["1ms"] - 20.02) < 0.05 and abs(N["ktt_at"]["10ms"] - 6.228) < 0.01


def t_the_efficiency_floor_couples_current_and_voltage_and_reproduces_the_check():
    R = _R()
    N, E = R["N"], R["E"]
    it = N["ioc"][0]
    pout, rr = 46.83613751272727, 0.141525                       # the fix round's own point, as the check reproduced it
    assert abs(N["fix_pout"] - pout) < 1e-9
    eta = pout / (it * (9.0 - it * rr))
    assert abs(eta - 0.908691) < 5e-7 and abs(N["fix_eta"] - eta) < 1e-12
    i_at = (9.0 - (81.0 - 4 * rr * pout / 0.908691) ** 0.5) / (2 * rr)
    assert abs(i_at - 6.36376) < 5e-6 and abs(N["fix_i"] - i_at) < 1e-9, "the boundary does not reproduce 6.36376 A at 0.908691"
    assert abs(N["i_at_eta"](N["eta_floor"]) - it) < 1e-9 and abs(N["i_at_eta"](E["eta_fe"]) - N["i9"]) < 1e-6
    assert N["eta_floor"] < E["eta_fe"] and N["ioc_margin"] > 0.05, "the final round's margin is not the one the record states"
    assert N["trip_min_r19_f1"] < N["ioc"][0] * 1.03, "R19 would buy more than the record says"
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "0.908691" in page and "6.36376" in page and "0.88021" in page and "0.906 scaled" in page


def t_the_breakers_timing_is_tis_loaded_row_and_the_scan_carries_the_filter():
    R = _R()
    N = R["N"]
    assert abs(N["t48_toc22"] - 370e-6) < 1e-12 and abs(N["t48_toc0"][0] - 25e-6) < 1e-12 and abs(N["t48_toc0"][1] - 30e-6) < 1e-12
    assert abs(N["toc"][1] - 370e-6) < 1e-12 and abs(N["toc"][0] - N["toc_eq7"][0]) < 1e-15
    assert abs(N["toc"][2] - N["toc_eq7"][2] * 370e-6 / N["toc_eq7"][1]) < 1e-12 and N["toc"][2] > N["toc_eq7"][2]
    assert abs(N["tau"][1] - 3.01e3 * 1e-9) < 1e-15
    assert abs(N["filt_14"] - 14.19e-6) < 0.01e-6, "the check's 14 A example does not reproduce"
    assert abs(N["l_min"] - N["v_on_max"] * (N["tau"][2] + N["t48_tsc"][1]) / (N["idm"] * R["T9"]["derate"] - N["isc"][2])) < 1e-15
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "5 us + 3RC" in page and "The threshold is where the trip begins" in page and "0.247 ms" in page and "7.24 V" in page


def t_req015_at_the_plug_is_a_conditional_candidate_on_a_bounded_shedding_sequence():
    R = _R()
    N = R["N"]
    e9 = N["env"][9.0]
    assert N["func"][1] <= e9["w_lo"] and N["func_margin"] > 0.5, "the warm-up's plan figure is not carried with margin"
    assert N["shed"][2] > e9["w_lo"], "the hi corner's shed state is carried: the record's CONDITIONAL would be wrong"
    assert abs(N["shed_room"] - (e9["w_lo"] - N["heater_w"])) < 1e-12
    assert N["surplus"][0] > 0 and N["it_need"] <= 1.82 and N["top_margin"] > 0 and N["guard_margin"] >= 0.1
    assert N["guard_levels"][1] > N["guard_levels"][2] and N["guard_levels"][3] > N["ven_op"]
    assert N["air_m20"][1] < 0, "the inside air reaches 0 C: the thermal statement would be wrong"
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "CONDITIONAL CANDIDATE" in page and "met with drafts" not in page.replace('"met with drafts"', "")


def t_nine_volts_at_the_plug_gives_less_than_at_vin_raw():
    R = _R()
    E = R["E"]
    for k in ("drawn", "selected"):
        pl = E["plug"][k]
        assert pl["vin"] < 9.0 and pl["w"] < E["env"][9.0]["w_lo"], "the plug's 9 V is not the finding the record states"
        assert pl["knee_top"] < 9.0
    assert E["plug"]["selected"]["r"] < E["plug"]["drawn"]["r"]


def t_no_owner_question_is_forced_and_the_losses_lower_every_ceiling():
    R = _R()
    F, N = R["F"], R["N"]
    assert F["owner_question"] is False
    for (lab, ia, rr, vr, w), (ia2, wref) in zip(N["caps"], N["check_ref"]):
        assert ia == ia2 and w < wref, "%s: the losses do not lower the ceiling" % lab
    assert [round(w, 2) for _i, w in N["check_ref"]] == [53.9, 69.79, 76.96], "not the check's reference figures"
    plans = {n: pl for n, (_lo, pl, _hi) in R["E"]["states"].items()}
    assert max(plans.values()) < N["caps"][2][4], "a 15 A part would not lift the 9 V ceiling over every state"


def t_d06_the_weak_source_envelope_is_monotone_with_its_energies():
    R = _R()
    N, D = R["N"], R["D"]
    assert [(lo, hi, t) for lo, hi, t in N["intervals"]] == [(None, 13.5, None), (13.5, 20.0, 600.0), (20.0, 35.0, 5.0), (35.0, 60.0, 0.5), (60.0, N["i_pf_spec"], 0.1)]
    assert abs(N["i_pf_spec"] - 900.0) < 1e-9 and N["i2t_top"][4][3] == 900.0 ** 2 * 0.1
    assert [i2t for _l, _h, _t, i2t in N["i2t_top"]][1:4] == [240000.0, 6125.0, 1800.0]
    eq = {hi: e for _lo, hi, _t, e in N["contact_eq"]}
    assert abs(eq[35.0] - 35.0 ** 2 * 5.0 / 23.0 ** 2) < 1e-9 and abs(eq[60.0] - 60.0 ** 2 * 0.5 / 23.0 ** 2) < 1e-9
    assert abs(N["loop_floor20"] - 43.18 / 900.0 / (1 - 0.00393 * 40.0)) < 1e-12
    assert abs(N["acc"][0] - N["loop_floor20"] * (1.02 + 0.00393 * 2)) < 1e-12 and abs(N["acc"][1] - 0.066 / (1.02 + 0.00393 * 2)) < 1e-12
    assert N["acc"][0] < N["constr"][0] < N["constr"][1] < N["acc"][1], "the construction is not inside the measured window"
    assert 43.18 / (N["loop_floor20"] * (1 - 0.00393 * 40.0)) <= 0.9 * D["interrupt_a"] + 1e-9
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "35 A for 5 s" in page and "60 A for 0.5 s" in page and "crimp" in page and "four-wire" in page


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
    assert abs(ipf(3.05, 2.081) - D["sel_ipf"]) < 0.05 and D["sel_ipf"] <= 900.0
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


def _hotswap(d):
    m = _M()
    rel, want = m.GIT_PINS["l4e9_hotswap"]
    blob = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (m.L4E9_COMMIT, rel)], capture_output=True).stdout
    assert hashlib.sha256(blob).hexdigest() == want
    hs = os.path.join(d, "hotswap.py")
    open(hs, "wb").write(blob)
    return hs


def t_each_draft_checks_applies_once_refuses_twice_and_refuses_the_tree():
    _R()
    before = {g: _sha(g) for g in (GEN_E, GEN_A)}
    with tempfile.TemporaryDirectory() as d:
        hs = _hotswap(d)
        for name, gen, after_hotswap in DRAFTS:
            tgt = os.path.join(d, "gen_" + name)
            shutil.copy(gen, tgt)
            if after_hotswap:
                assert _run([hs, tgt, "--write"]).returncode == 0
            pre = _sha(tgt)
            script = os.path.join(REC, name)
            r = _run([script, tgt])
            assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-300:]
            assert _sha(tgt) == pre, "--check wrote"
            r = _run([script, tgt, "--write"])
            assert r.returncode == 0 and b"WRITTEN" in r.stdout
            r = _run([script, tgt, "--write"])
            assert r.returncode == 3, "a second application was not refused"
            r = _run([script, gen, "--write"])
            assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
    assert all(_sha(g) == s for g, s in before.items()), "a draft wrote into the tree"


def t_the_drafts_compose_with_l4e9s_hotswap_draft_and_the_entry_and_timer_exclude_each_other():
    _M()
    en, tm = os.path.join(REC, "apply_gen_sch_e_entry.py"), os.path.join(REC, "apply_gen_sch_e_timer.py")
    with tempfile.TemporaryDirectory() as d:
        hs = _hotswap(d)
        a, b, c, e = (os.path.join(d, x) for x in ("a.py", "b.py", "c.py", "e.py"))
        for p in (a, b, c, e):
            shutil.copy(GEN_E, p)
        for s in (hs, en):
            assert _run([s, a, "--write"]).returncode == 0
        txt = open(a, encoding="utf-8").read()
        assert 'ic("U6", 20, "TPS48110AQDGXRQ1' in txt and '"CSD19536KTT' in txt and 'r("R24", "39.7k 0.1%' in txt and "SRF1260-1R0Y" in txt
        assert '"9": "HS_TIMER"' in txt and '"8": "HS_IWRN"' in txt and 'lcsc="C2985708"' in txt and "_VEH_T, _VEH_P = 7.14, 7.14" in txt
        assert _run([tm, a, "--write"]).returncode == 3, "the timer draft did not refuse after the entry draft"
        for s in (hs, tm):
            assert _run([s, b, "--write"]).returncode == 0
        for s in (tm, hs):
            assert _run([s, c, "--write"]).returncode == 0
        assert open(b, "rb").read() == open(c, "rb").read(), "the timer draft's order with L4-E9's changes the result"
        assert _run([en, b, "--write"]).returncode == 3, "the entry draft did not refuse after the timer draft"
        assert _run([en, e, "--write"]).returncode == 3, "the entry draft ran before L4-E9's draft (the stated order)"


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
    owners = {"Layer 4 coordinator", "Layer 5 interfaces", "Layer 6 components", "Layer 7 mechanical", "Layer 8 board A generator owner",
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
    for s in ("4.927 to 14.653", "1236.9", "9.91 / 11.13 / 12.37", "9.33 / 10.52 / 11.74", "8.987", "3.062", "4.593",
              "0.71 A", "6.364", "7.136", "5.983", "0.704", "3.08", "0.743", "73.4 A", "2.08 uH", "29.09", "42.52", "43.82", "35.24",
              "20.51", "56.93", "58.51", "64.21", "1.2567", "50.99", "69.73", "72.41", "7.378", "6.754 / 6.944 / 7.139", "0.908691", "0.88021"):
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
