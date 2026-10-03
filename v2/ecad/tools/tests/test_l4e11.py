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
settings and its bound holds only inside TI's row condition. The dependency round adds: one row per specification left to a
maker (D1 to D10) with all seven columns and its cited record lines; the bounded fallback holds the worst admitted step for at
least the assumed response and keeps the pack's inrush under ASCD; U-04 stays an architecture-level choice resting on D1 and D3;
the POR value is TI's 256 mA; the TI draft asks only what REVIEW-REQUEST.md does not. The consolidation round adds: TI's BQ25730
differs from the drawn BQ25731 at pin 21 alone and keeps every electrical row the drafted settings rest on; each of the three
modes has a printed bound on VSYS whose floor clears the converters' assumed one; the start into VSYS's capacitance never
latches; the battery FET meets TI's selection rule, its thermal bar and its LDO-mode floor follow from its sheet in closed form,
and its docking pulse exceeds IDM and is named a gap; Figure 14's reader is independent of poppler's serialisation; the
cost is the catalogues'; the charger draft composes with the guard
draft in either order; (B1) is selected and U-04 becomes a downstream qualification test. The fix round for the consolidation
review cx36 adds: board E's auxiliary domain leaves CELL_F for VSYS on the dock's pin 1 (the three drafts agree, and no kit load
stays on the pack); the start is bounded by the input clamp, the retries and a bench acceptance, the 502.3 ms withdrawn; the
battery FET's RDS(on) is bounded by the two chords of the makers' printed maxima at BATDRV's 8.5 V and the pair is selected on its
bar; the inhibited acceptance is piecewise; the precharge counts R17's tolerance. The fix round for the review of the provisional
fixes (L4-F02, L4-F03) adds: the battery FET's RDS(on) figure is an allowance that no printed point bounds and a measurement gates;
the thermal basis is the device's own Zth(j-mb) with the two FETs' coupling inside the measured sum, and the service and every fault
history from the hot state fit it; Ciss is not shown under TI's 5 nF near 0 V; the docking pulse is taken whole in one FET with no
I2t conversion; the dock's VSYS branch sits behind an eFuse whose printed limit keeps the contact inside its rating, the fuse and the
PTC fail on their printed rows, and the feed's drop clears U12; the record states each item's status. The second review (L4-CP01 to
L4-CP03) adds: U42's fault envelope rests only on printed limits and states its inferred ceiling; the fans' start fits U42's least limit;
the docking waveform's qualification exceeds the waveform; the charger draft writes none of the withdrawn statements; each measurement
row names its specimen and blocks only the final release. The fans' feed round (section 18) adds: the mixers' rail covers VSYS_E's
range and holds the fans' printed window, its RUN divider sits between the floor and U12's start, the inductor's saturation sits over the
regulator's limit, the branch's declared current with the rail's input at the floor stays under U42's least limit, the board E draft writes
the rail and the four-wire fans and no flyback, and board B's feed is read as not covering the coolers. Nothing here writes into the tree:
drafts run on temporary copies.
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
DRAFTS = (("apply_gen_sch_e_entry.py", GEN_E, True), ("apply_gen_sch_e_timer.py", GEN_E, False), ("apply_gen_sch_a_guard.py", GEN_A, False),
          ("apply_gen_sch_a_charger.py", GEN_A, False), ("apply_gen_sch_e_aux.py", GEN_E, False))
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
        m = re.match(r"^(\d{1,2})\. ", ln)
        if m:
            sec, i = int(m.group(1)), i + 1
            continue
        grp, j = [ln], i + 1
        while j < len(text) and text[j].strip() and ind(text[j]) > ind(ln) and not re.match(r"^\d{1,2}\. ", text[j]):
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
              "Layer 8 board E generator owner", "Layer 8 board B generator owner", "Layer 9 pre-layout analysis", "prototype bench", "firmware owner", "CONOPS owner"}
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
              "20.51", "56.93", "58.51", "64.21", "1.2567", "50.99", "69.73", "72.41", "7.378", "6.754 / 6.944 / 7.139", "0.908691", "0.88021",
              "12.054", "17.375", "20.54", "0.221", "4.1792", "6.2468", "12.057", "14.41", "7.744", "9.216", "242.9", "17.7", "502.3",
              "0.916", "10.44", "120.9", "107.8", "170.3", "184.4", "0.302",
              "34.42", "21.136", "0.33616", "5.632", "11.96", "3.062", "0.848", "119.8", "9.688", "12.179", "0.1408", "2.406", "28.32",
              "33.12", "126.7", "0.2589", "1.3571", "10.753", "3.785", "0.703", "5.74", "123.3", "1.501", "1.8018", "1.4713", "9.539",
              "0.1486", "152.8", "51.5", "80.9", "566", "1.441", "41.1", "0.3356", "0.5713", "9.494", "267.2", "37.2",
              "1.3208", "0.5208", "89.8", "0.1504", "9.508", "8.33", "6.89", "12.001", "0.72 W", "97.4", "37.7", "8.54", "11.512", "12.431"):
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


DEP_PHRASES = {"D1": "| absent, or both FETs open", "D2": "**R-c.**", "D3": "| S2 | on | off |", "D4": "**ChargeCurrent() at POR.**",
               "D5": "| E11-07 |", "D6": "**R-d.**", "D7": "| (iii) |", "D8": "| (ii) |", "D9": "| overcurrent delay |",
               "D10": "| a start into a hard short"}


def t_the_dependency_table_has_one_row_per_missing_specification_with_its_claim_lines():
    R = _R()
    m = _M()
    rows = m.dep_rows(R)
    assert [r["id"] for r in rows] == ["D%d" % k for k in range(1, 11)]
    for r in rows:
        for k in ("name", "missing", "claim", "maker", "bench", "cannot", "method", "negative"):
            assert len(r[k]) > 10, "%s lacks %s" % (r["id"], k)
    lines = open(PAGE, encoding="utf-8").read().split("\n")
    s11 = lines.index([l for l in lines if l.startswith("## 11. ")][0])
    e11 = lines.index([l for l in lines if l.startswith("### 11a. ")][0])
    table = [l for l in lines[s11:e11] if re.match(r"^\| D\d+", l)]
    assert [re.match(r"^\| (D\d+)", l).group(1) for l in table] == ["D%d" % k for k in range(1, 11)]
    for l in table:
        assert l.count("|") == 8, "a dependency row does not carry the seven columns: %s" % l[:40]
        rid = re.match(r"^\| (D\d+)", l).group(1)
        cites = re.findall(r"line (\d+):", l)
        assert len(cites) == 1, "%s cites no record line" % rid
        assert DEP_PHRASES[rid] in lines[int(cites[0]) - 1], "%s's cited line does not hold its claim" % rid
        assert "**can:**" in l and "**Cannot:**" in l, "%s does not separate what a sample can and cannot establish" % rid


def t_the_fallback_holds_the_worst_admitted_step_and_keeps_the_pack_under_ascd():
    R = _R()
    m = _M()
    G = R["G"]
    assert G["worst"][0].startswith("USB-C PD") and abs(G["worst"][1] - 3.0 * 15.0 / 0.93) < 1e-9
    pa = [ok for nm, dp, ok in G["admit"] if nm.startswith("PA rail")][0]
    assert pa is False, "the PA's step is admitted in S4: the worst step would be another"
    k = 0.8 * 0.7 * 0.9
    c_bank = 4 * 470e-6 * k
    v1 = 16.8 * 0.995 - 4 * 0.01 * 470 * 25e-6 * 330.0
    v2 = 12.3 + 0.55 + 0.10
    e = c_bank * (0.5 * (v1 ** 2 - v2 ** 2) - 0.65 * (v1 - v2)) + 0.5 * 180e-6 * k * ((16.8 * 0.995) ** 2 - 12.3 ** 2)
    assert abs(e - G["e_tot"]) < 1e-12
    assert G["worst_hold"] >= m.T_RESP, "the fallback does not hold the worst admitted step for the assumed response"
    assert dict(G["cans_for"])[1e-3] == m.BANK_N, "the bank is not the least that meets 1 ms"
    assert G["c_dir_eff"] * 1e6 >= R["B"]["csys_uf"], "the direct can does not give TI's 50 uF by itself"
    assert G["t_over_ascd"] < G["ascd_us"], "the pack's inrush stays over ASCD longer than its delay"
    assert G["p_ch_pk"] <= G["p_rc2512"] and R["F"]["air_hot"] <= 70.0, "R_CH runs over its rating"
    direct4 = G["r_loop"] * (G["c_pack_side_max"] + 4 * 470e-6 * 1.2) * math.log(G["i_conn_pk"] / G["ascd_a"])
    assert direct4 > G["ascd_us"], "four cans directly on VSYS would not trip ASCD: the isolation's reason would be wrong"
    assert G["s9_deficit"] > 0 and G["s2_vsys"][0] <= 10.0 + 1e-9


def t_u04_stays_an_architecture_level_choice_resting_on_d1_and_d3():
    out = open(OUT, encoding="utf-8").read()
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "U-04 STAYS AN ARCHITECTURE-LEVEL CHOICE" in out and "U-04 stays an ARCHITECTURE-LEVEL CHOICE" in page
    assert "with none: D1 and D3, whose negative answers return (B)" in out
    assert "**With none:** D1 and D3" in page


def t_the_por_value_is_tis_256_ma_and_the_ti_draft_asks_only_what_is_missing():
    R = _R()
    assert R["G"]["por_ma"] == 256.0
    page = open(PAGE, encoding="utf-8").read()
    assert "ChargeCurrent() is 0 A" not in page and "0 A at POR, and at" not in page, "the POR error is still stated as fact"
    assert "ChargeCurrent() is 256 mA" in page.replace("\n", " ")
    draft = open(os.path.join(REC, "clarification", "TI-QUESTIONS.md"), encoding="utf-8").read()
    review = open(os.path.join(ROOT, "v2", "docs", "review-packets", "battery", "REVIEW-REQUEST.md"), encoding="utf-8").read()
    for q in ("Q-TI-11", "Q-TI-12", "Q-TI-13", "Q-TI-14"):
        assert ("**%s" % q) in draft and q not in review, "%s is not a question REVIEW-REQUEST.md lacks" % q
    assert "Q-TI-3, addendum" in draft and "not sent" in draft


def t_the_bq25730_differs_only_at_pin_21_and_keeps_every_row_the_drafted_settings_rest_on():
    R = _R()
    m = _M()
    H = R["H"]
    assert H["pins_diff"] == [(21, "NC", "BATDRV")]
    assert H["u3"]["21"] == "NC" and H["u3"]["22"] == "VBAT"
    assert all(k in H["ec_same"] for k in m.EC_RESTS_ON)
    assert sorted(H["ec_diff"]) == sorted(m.EC_CHANGED)
    assert H["ichg_pct"] == ["-12%", "13.5%", "-18%", "21.5%"]
    assert H["ichg_por"] == "0000" and H["devid"] == "D5" and H["devid31"] == "D6"
    assert H["rm"] == (3.6, 25.0, 4.2) and 68.4 < R["strap"][2] < 81.5, "the 4S strap would read battery removal"


def t_each_mode_has_a_printed_vsys_bound_and_the_floor_clears_the_converters():
    R = _R()
    H = R["H"]
    assert abs(H["floor"] - 12.30 * 0.98) < 1e-12 and H["floor"] > 10.0
    assert abs(H["vsys_top"] - (R["cv_max"] + 0.150) * 1.02) < 1e-12 and H["vsys_top"] < R["B"]["sysovp4s"]
    assert H["ec_tj"] == (-40.0, 125.0), "VSYS_MIN's floor would not hold over the cold"
    assert H["smin_max_printed"] == "-2", "the printed gap in VSYS_MIN_REG_ACC's maximum is not what the record names"
    assert H["regs"]["EN_OOA"][0] == 1, "the boot write of EN_OOA would not be needed"
    assert H["regs"]["BATFETOFF_HIZ"][0] == 0 and H["regs"]["BATFET_ENZ"][0] == 0 and H["regs"]["EN_LDO"][0] == 1
    out = open(OUT, encoding="utf-8").read()
    assert out.count("BOUNDED (MAKER, INFERRED)") == 3
    page = open(PAGE, encoding="utf-8").read()
    rows = [l for l in page.splitlines() if l.startswith("| (1) battery present") or l.startswith("| (2) battery absent") or l.startswith("| (3) battery present")]
    assert len(rows) == 3 and all("**BOUNDED**" in l for l in rows) and all(l.count("|") == 6 for l in rows)


def t_the_start_into_vsys_never_latches():
    R = _R()
    H = R["H"]
    u = H["uvp"]
    assert (u["v"], u["iin"], u["deg"], u["off"], u["on"], u["n"]) == (2.4, 0.5, 2e-3, 0.5, 10e-3, 7)
    c = H["c_vsys_nom"] * 1.1 + 180e-6 * 1.2
    assert abs(H["c_vsys_max"] - c) < 1e-15
    t = c * 2.4 / 0.5
    assert abs(H["t_2v4"] - t) < 1e-15 and t <= u["on"], "VSYS could not reach 2.4 V inside one retry"
    assert H["hiccups"] == (0 if t <= u["deg"] else 1) and H["start_bound"] < u["n"] * u["off"]


def t_the_battery_fet_meets_tis_rule_and_its_bars_follow_from_its_sheet():
    R = _R()
    H, Q = R["H"], R["H"]["Q"]
    air = R["F"]["air_hot"]
    assert Q["ciss"] < H["bf_ciss"] and Q["vds"] >= H["bf_v"] and Q["vds"] > R["B"]["sysovp4s"] and H["drv"][2] < Q["vgs"]
    assert abs(Q["z10"] - Q["rja10"]) <= 0.02 * Q["rja10"]
    assert abs(Q["rja_need_20"] - (150.0 - air) / (20.0 ** 2 * Q["rds125"])) < 1e-9
    assert abs(Q["rja_need_18"] - (150.0 - air) / (18.0 ** 2 * Q["rds125"])) < 1e-9
    assert Q["rja_need_20"] < Q["rja_ss"], "the sheet's own board would carry OCD1 held: no bar would be needed"
    assert abs(Q["tj_10a_ss"] - (air + 100.0 * Q["rds125"] * Q["rja_ss"])) < 1e-9 and Q["tj_10a_ss"] < 150.0
    ocd1 = [r for r in Q["prot"] if r[0] == "the gauge's OCD1"][0]
    assert ocd1[4] < 150.0 < ocd1[5], "OCD1 is either carried after 10 A held or not even from the air"
    assert 0 < Q["t18_hot"] < Q["t18_air"]
    for _n, i, w, fr in Q["prof"]:
        assert abs(w - i * i * Q["rds125"]) < 1e-12 and fr < 0.005
    i_pre = 0.256 * 1.30
    assert abs(Q["i_pre"] - i_pre) < 1e-12
    assert abs(Q["ldo_floor"] - (12.3 * 1.02 - (150.0 - air) / (Q["rja_ss"] * i_pre))) < 1e-9
    assert Q["ldo_floor3"] > Q["ldo_floor"] and Q["ldo_floor"] < R["P"]["vsys_shut"][0] < R["P"]["vsys_cuv"][0]
    assert Q["i_dock"] > Q["idm"] and Q["t_over_idm"] > 0, "the docking pulse would sit under IDM: E11-30 would be no gap"
    assert abs(Q["t_over_idm"] - Q["tau"] * math.log(Q["i_dock"] / Q["idm"])) < 1e-15


def t_the_cost_is_the_catalogues_and_the_bank_is_what_b1_withdraws():
    R = _R()
    H = R["H"]
    import json
    def p10(name):
        j = json.load(open(os.path.join(REC, "inputs", name), encoding="utf-8"))
        lad = j["price_usd"]
        return float(lad["10"] if "10" in lad else lad[sorted(lad, key=int)[0]])
    a = p10("lcsc-C2871872-2026-10-02.json") + 4 * p10("lcsc-C242138-price-2026-10-02.json") + p10("lcsc-C72264-price-2026-10-02.json") \
        + p10("lcsc-C137025-price-2026-10-02.json") + p10("lcsc-C242139-price-2026-10-02.json")
    b = p10("lcsc-C5219071-2026-10-02.json") + p10("lcsc-C404364-2026-10-02.json") + p10("lcsc-C242139-price-2026-10-02.json")
    assert abs(H["cost"][0] - a) < 1e-9 and abs(H["cost"][1] - b) < 1e-9 and b < a
    assert H["bank_b1"] < 1e-3 < R["G"]["worst_hold"], "at B1's floor the bank would still carry the assumed millisecond"


def t_the_charger_draft_composes_with_the_guard_in_either_order():
    _M()
    ch, gd = os.path.join(REC, "apply_gen_sch_a_charger.py"), os.path.join(REC, "apply_gen_sch_a_guard.py")
    with tempfile.TemporaryDirectory() as d:
        a, b = os.path.join(d, "a.py"), os.path.join(d, "b.py")
        shutil.copy(GEN_A, a)
        shutil.copy(GEN_A, b)
        for s_ in (ch, gd):
            assert _run([s_, a, "--write"]).returncode == 0
        for s_ in (gd, ch):
            assert _run([s_, b, "--write"]).returncode == 0
        assert open(a, "rb").read() == open(b, "rb").read(), "the order of the two board A drafts changes the result"
        txt = open(a, encoding="utf-8").read()
        for want in ('"21": "CH_BATDRV", "22": "VBAT"', '"C5219071")', 'for _qb in ("Q39", "Q40"): nfet(_qb, ',
                     '"CH_BATDRV", "CH_BATQ", "VBAT", fp="LFPAK56", lcsc="C3278350")', '"LFPAK56": "Package_TO_SOT_SMD:LFPAK56"',
                     '"CH_BATQ", "CELL_FUSED", "RS2512")', 'r("R149", "10R", "CH_BATQ", "CH_SRP_F")', 'c("C236", ',
                     '_intent.rail("CH_BATQ", 14.4, 10.0, 18.0, "R17"', '"Q39", always_on=True', 'fed_from="CH_BATQ"',
                     '"R17", "Q39", "Q40", "C236", "U42", "R228", "C237", "C238", "C239", "D23", "C16"', '{"1": "VSYS_DOCK", "2": "GND", "3": "GND"', 'loads={"U42": 1.32, "U4": 2.0'):
            assert txt.count(want) == 1, want
        assert '"21": "NC"' not in txt and "C2871872" not in txt


def t_b1_is_selected_and_u04_becomes_a_downstream_qualification_test():
    out = open(OUT, encoding="utf-8").read()
    page = " ".join(open(PAGE, encoding="utf-8").read().split())
    assert "SELECTED (SESSION): (B1), TI's BQ25730 in U3's land with Q39 (the fix round, 15c: Q39 and Q40, two BUK6Y10-30P; 15a: board E on VSYS)." in out
    assert "U-04 BY THE OWNER'S EXIT DEFINITION: A DOWNSTREAM QUALIFICATION TEST WITH BOUNDED EVIDENCE AND A WORKABLE FALLBACK" in out
    assert "**SELECTED (SESSION): (B1), TI's BQ25730 in U3's land with the battery FET Q39** (the fix round: Q39 and Q40" in page
    assert "**U-04 by the owner's exit definition: A DOWNSTREAM QUALIFICATION TEST WITH BOUNDED EVIDENCE AND A WORKABLE FALLBACK**" in page
    assert "NONE FOUND" in out and "none found" in page
    lines = open(PAGE, encoding="utf-8").read().splitlines()
    i = lines.index("## 13. Three approaches compared (out 13)")
    rows = [l.split(" | ")[0][2:] for l in lines[i:] if l.startswith("| D")]
    assert rows[:9] == ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9, D10"]
    removed = [l.split(" | ")[0][2:] for l in lines[i:] if l.startswith("| D") and "**removed" in l]
    assert removed == ["D1", "D3", "D4", "D7"]



def t_the_battery_fets_figure_14_reads_the_same_from_either_poppler_serialisation():
    m = _M()
    real = subprocess.run

    def p22(svg):
        def el(mo):
            t = re.sub(r",\s+", ",", mo.group(0))
            a = re.search(r' stroke="([^"]*)"', t)
            return t.replace(a.group(0), ' style="stroke:%s;"' % a.group(1)) if a and ' style="' not in t else t
        return re.sub(r"<path[^>]*>", el, svg)

    def p24(svg):
        def el(mo):
            t = mo.group(0)
            st = re.search(r' style="([^"]*)"', t)
            if st:
                kv = [p.split(":", 1) for p in st.group(1).split(";") if ":" in p]
                t = t.replace(st.group(0), "".join(' %s="%s"' % (k.strip(), v.strip()) for k, v in kv))
            return re.sub(r",(?=\S)", ", ", t)
        return re.sub(r"<path[^>]*>", el, svg)
    ts = (2.44e-4, 1e-3, 0.02, 1.0, 2.0, 10.0, 60.0, 1000.0)
    z, span = m.z_ja_aons()
    base = [z(t) for t in ts]
    for rw in (p22, p24):
        def fake(cmd, *a, **k):
            r = real(cmd, *a, **k)
            if cmd and cmd[0] == "pdftocairo" and "-svg" in cmd:
                r = subprocess.CompletedProcess(r.args, r.returncode, rw(r.stdout.decode("utf-8", "replace")).encode("utf-8"), r.stderr)
            return r
        m.subprocess.run = fake
        try:
            z2, span2 = m.z_ja_aons()
        except SystemExit as e:
            raise AssertionError("z_ja_aons refused (exit %s) on the %s form" % (e.code, rw.__name__))
        finally:
            m.subprocess.run = real
        assert span2 == span and [z2(t) for t in ts] == base, "Figure 14 reads differently from the %s form" % rw.__name__
    assert all(a < b for a, b in zip(base, base[1:])), "ZthJA does not rise with the pulse"


def _apply(script, target):
    r = _run([os.path.join(REC, script), target, "--write"])
    assert r.returncode == 0, r.stderr.decode()[-300:]


def t_board_es_aux_domain_leaves_cell_f_for_vsys_and_the_three_drafts_agree():
    R = _R()
    K = R["K"]
    assert K["aux"] == {"U12": 0.8, "J_FAN1": 0.1, "J_FAN2": 0.1} and abs(K["aux_a"] - 1.0) < 1e-12
    assert abs(K["i_div"] - R["cv_max"] / (122e3 * 0.99)) < 1e-15
    assert K["ret"][2][2] > K["ret"][0][2] and K["ret"][3][4] < 85.0, "seven ground contacts with one open would pass the 813's 85 C at 51 C"
    with tempfile.TemporaryDirectory() as d:
        a, e, y, c = (os.path.join(d, x) for x in ("gen_sch_a.py", "gen_sch_e.py", "pcb_interfaces.yaml", "check_contracts.py"))
        shutil.copy(GEN_A, a)
        shutil.copy(GEN_E, e)
        shutil.copy(os.path.join(TOOLS, "pcb_interfaces.yaml"), y)
        shutil.copy(os.path.join(TOOLS, "check_contracts.py"), c)
        _apply("apply_gen_sch_a_charger.py", a)
        _apply("apply_gen_sch_e_aux.py", e)
        _apply("apply_pcb_interfaces_dock.py", y)
        _apply("apply_pcb_interfaces_dock.py", c)
        ta, te = open(a, encoding="utf-8").read(), open(e, encoding="utf-8").read()
        assert '"POGO12",\n     {"1": "VSYS_DOCK", "2": "GND"' in ta
        assert '"1": "VBAT", "2": "VBAT", "3": "VBAT"' in ta and '"18": "VSYS_DOCK", "19": "VSYS_DOCK", "20": "VSYS_DOCK"' in ta, "U42 is not between VBAT and VSYS_DOCK"
        assert 'r("R228", "11k 0.1%", "EF_ILIM", "GND")' in ta and 'loads={"J_DOCK": 1.32}' in ta and 'loads={"U42": 1.32, "U4": 2.0' in ta
        assert '"POGO_T6",\n     {"1": "VSYS_E", "2": "GND"' in te
        assert '{"1": "+5V_E6", "2": "VSYS_E", "3": "VSYS_E"' in te and 'c("C31", "10u 25V 1210", "VSYS_E", "GND", "C1210")' in te
        assert 'loads={"P_CP": 9.0},' in te and '{"1": "+12V_FAN", "2": "GND", "3": "FAN%s_PWM_OD" % n, "4": "FAN%s_TACH" % n}' in te
        assert '_intent.rail("VSYS_E", 14.4, 1.32, 1.32, "J_BLK"' in te and 'loads={"U12": 0.8, "U22": 0.52}' in te
        assert '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "L4"' in te and 'ic("U22", 21, "LTC3115EFE-1' in te
        assert 'part("D%s" % ("7" if n == "1" else "8")' not in te and te.count("FAN%s_SW") == 1, "the chopped supply's flybacks or nodes survive"
        left = set()
        for ln in te.splitlines():
            for st in re.split(r"\);\s*", ln):
                m2 = re.match(r'\s*(?:ic|part|c|r|ph|tp)\("([A-Z][A-Z0-9_]*)"', st)
                if m2 and '"CELL_F"' in st:
                    left.add(m2.group(1))
        assert left == {"F3", "P_CP", "C1", "D3", "R42", "TP8"}, "the parts left on CELL_F: %s" % sorted(left)
        doc = yaml.safe_load(open(y, encoding="utf-8").read())
        dock = None
        if dock is None:
            stack = [doc]
            while stack:
                o = stack.pop()
                if isinstance(o, dict):
                    if "IF-AE-DOCK" in o:
                        dock = o["IF-AE-DOCK"]
                        break
                    stack.extend(o.values())
                elif isinstance(o, list):
                    stack.extend(o)
        assert dock["pins"][1] == "VSYS_DOCK" and ["VSYS_DOCK", "VSYS_E", "A's VSYS through its eFuse U42 to E's auxiliary domain on pin 1 (L4-E11)"] in dock["aliases"]
        assert "2.238 A, 2.406 A" in dock["aux_feed"] and "%s to %s V" % ("9.688", "17.375") in dock["aux_feed"] and "1.32 A declared" in dock["aux_feed"]
        assert '({"VSYS_DOCK", "VSYS_E"},' in open(c, encoding="utf-8").read()
    for tree in (os.path.join(TOOLS, "pcb_interfaces.yaml"), os.path.join(TOOLS, "check_contracts.py")):
        r = _run([os.path.join(REC, "apply_pcb_interfaces_dock.py"), tree, "--write"])
        assert r.returncode == 3 and b"NOT RELEASED" in r.stderr


def t_the_held_state_feeds_no_kit_load_from_the_pack_and_the_start_ends_in_vsys_min_or_a_latch():
    R = _R()
    K, H = R["K"], R["H"]
    assert abs(K["held_dv"] - (R["cv_max"] - (R["cv_max"] + 0.15) * 0.98)) < 1e-12 and K["held_dv"] > 0
    assert K["held_bounded_a"] < 1e-3, "the bounded drains alone exceed the bench acceptance"
    u = H["uvp"]
    assert abs(K["t_latch"] - (u["deg"] + (u["n"] - 1) * (u["off"] + u["on"]))) < 1e-12
    out = open(OUT, encoding="utf-8").read()
    assert "the 502.3 ms of 12c withdrawn: 0.5 A is an input ceiling, not a delivered current" in out
    assert "bounded at 502.3 ms and never latches" not in out
    row = [x for x in _M().downstream(R) if x[0] == "E11-31"][0][3]
    assert "Fault VSYS_UVP clear" in row and "the held pack current at most 1 mA" in row


def t_the_fet_bound_is_the_two_chords_and_the_pair_is_selected_on_its_bar():
    R = _R()
    m = _M()
    K = R["K"]
    kg = (10.0 + (25.0 - 10.0) * 1.5 / 5.5) / 10.0
    rb = kg * (10.0 + 6.0 * 125.0 / 150.0) * 1e-3
    sel = K["sel"]
    assert sel["key"] == "c" and abs(sel["rb"] - rb) < 1e-12 and sel["n"] == 2
    a, b = K["cands"][0], K["cands"][1]
    assert a["tjlim"] == 125.0, "AONS21357 judged above its last printed row"
    assert a["bar"]["route"] < 0.2 * a["rboard"] and b["bar"]["route"] < 0.2 * b["rboard"]
    assert sel["bar"]["route"] > 3 * max(a["bar"]["route"], b["bar"]["route"])
    assert all(cd["ciss_ok"] for cd in K["cands"]) and 3 * sel["rdef"]["ciss"] > R["H"]["bf_ciss"], "a third FET would fit TI's Ciss"
    z = K["z"]
    p = sel["p"]
    budget = 150.0 - K["air"]["route"]
    bar = min(budget / p["p10"], budget / (p["p10"] + (p["p18"] - p["p10"]) * z[60.0]), budget / p["p20"],
              budget / (p["p20"] + (p["p24"] - p["p20"]) * z[1.0]), budget / (p["p20"] + (p["p30"] - p["p20"]) * z[0.02]),
              budget / (p["p20"] + (p["pscd"] - p["p20"]) * z[2.44e-4]))
    assert abs(bar - sel["bar"]["route"]) < 1e-9
    assert abs(p["p18"] - 81.0 * rb) < 1e-12, "the pair's 18 A is not split in two"
    d = K["dock"]
    assert d["i2t_pulse"] <= d["i2t_rect"] and R["H"]["Q"]["i_dock"] <= sel["rdef"]["ism"], "all of the pulse in one FET would not fit at 25 C"
    assert abs(d["der"] - (175.0 - 70.0) / 150.0) < 1e-12 and 0.5 < d["s_max"] < 1.0
    assert abs(m.sel_tj_18(K) - (K["air"]["route"] + sel["bar"]["route"] * (p["p10"] + (p["p18"] - p["p10"]) * z[60.0]))) < 1e-9


def t_the_inhibited_acceptance_is_piecewise_and_the_precharge_counts_r17s_tolerance():
    R = _R()
    K, H = R["K"], R["H"]
    assert abs(K["lo_v"] - 12.3 * 0.98) < 1e-12 and abs(K["hi_v"] - 12.3 * 1.02) < 1e-12
    assert abs(K["inh_floor"] - min(12.3 * 0.98, (12.3 * 0.98 + 0.15) * 0.98)) < 1e-12 and K["inh_floor"] < H["floor"]
    assert abs(K["review_case"] - 10.353) < 1e-9
    assert abs(K["i_pre"] - 0.256 * 1.30 / 0.99) < 1e-12
    sel = K["sel"]
    assert abs(K["ldo_floor"] - (12.3 * 1.02 - (150.0 - K["air"]["route"]) / (sel["bar"]["route"] * K["i_pre"]))) < 1e-9
    assert K["rb_floor"] == max(math.ceil(K["ldo_floor"] * 10) / 10.0, 4.0) and K["rb_floor"] < 7.8
    page = open(PAGE, encoding="utf-8").read()
    assert "between the two: either mode, so at least **11.96 V**" in page.replace("\n  ", " ").replace("Between", "between")



def t_l4f02_the_rds_figure_is_an_allowance_no_printed_point_bounds_and_a_measurement_gates():
    R = _R()
    m = _M()
    K, L = R["K"], R["L"]
    nxp = K["sel"]["rdef"]
    assert abs(L["ra"] - K["sel"]["rb"]) < 1e-6, "the allowance is not the figure the rest of the record is sized to"
    # what the sheet prints: hot only at -10 V, low drive only at 25 C; BATDRV's least drive is under 10 V
    assert nxp["t_hot"] == 175.0 and R["H"]["drv"][0] < 10.0 and nxp["r45_25"] > nxp["r10_hot"]
    pm = L["plan_miss"]
    assert pm["tj20"] > m.F16_TJ_HELD and abs(pm["tj20"] - (K["air"]["route"] + 100.0 * m.F16_RA_ALT * L["plan"]["zsum"])) < 1e-9
    out = open(OUT, encoding="utf-8").read()
    assert "WITHDRAWN AS A BOUND" in out
    row = [x for x in m.downstream(R) if x[0] == "E11-36"][0]
    assert "-8.5 V" in row[3] and "%s mOhm" % m.fmt(m.F16_RA * 1e3, 3) in row[3]


def t_l4f02_the_thermal_basis_is_the_devices_own_and_every_hot_history_fits_it():
    R = _R()
    m = _M()
    K, L, Q0 = R["K"], R["L"], R["H"]["Q"]
    zf = L["zf"]
    ts = [1e-6 * 10 ** (k / 10.0) for k in range(0, 81)]
    zs = [zf(x) for x in ts]
    assert all(a <= b + 1e-12 for a, b in zip(zs, zs[1:])), "Zth(j-mb) does not rise with the pulse"
    assert abs(zf(60.0) - 1.4) < 1e-12 and max(zs) <= 1.4 + 1e-12, "the curve is not scaled to Table 6's maximum"
    air, pl = K["air"]["route"], L["plan"]
    pb = lambda i: (i / 2.0) ** 2 * L["ra"]
    zsum = (m.F16_TJ_HELD - air) / pb(20.0)
    assert abs(pl["zsum"] - zsum) < 1e-9 and abs(pl["tj20"] - m.F16_TJ_HELD) < 1e-9
    tj18 = air + pb(10.0) * zsum + (pb(Q0["i_peak"]) - pb(10.0)) * zsum
    assert abs(pl["tj18"] - tj18) < 1e-9 and tj18 < 150.0, "the 18 A for 60 s from the hot state passes the limit"
    for lab, i_, t_, p_, allow, zd, room in pl["ev"]:
        assert abs(allow - (150.0 - m.F16_TJ_HELD) / (pb(i_) - pb(20.0))) < 1e-9
        assert room > 0, "%s: the device alone takes the whole allowance" % lab
    assert L["ldo_floor16"] < K["rb_floor"], "R-b' no longer keeps the LDO precharge under the limit"
    row = [x for x in m.downstream(R) if x[0] == "E11-29"][0][3]
    assert "Zself + Zmut" in row and "case-rise reading at 10 A alone does not close it" in row


def t_l4f02_ciss_is_not_shown_under_tis_figure_and_the_item_stays_open():
    R = _R()
    L, H = R["L"], R["H"]
    assert 2 * L["ciss_t"] < H["bf_ciss"] < 2 * L["ciss_0"], "the typical Ciss near 0 V does not exceed TI's figure"
    assert L["ciss_0"] < H["bf_ciss"] and L["one_rja"] < 0.5 * L["plan"]["zsum"]
    out = open(OUT, encoding="utf-8").read()
    assert "STATUS: OPEN; the pair stays selected" in out


def t_l4f02_the_docking_pulse_is_taken_whole_in_one_fet_with_no_i2t_conversion():
    R = _R()
    K, L, Q0 = R["K"], R["L"], R["H"]["Q"]
    rise, energy, ppk, t_pk = L["dock_k1"]
    assert abs(ppk - L["vsd_max"] * Q0["i_dock"] / L["vsd_is"] * Q0["i_dock"]) < 1e-6, "the peak power is not the concave VF bound's"
    q = Q0["i_dock"] * Q0["tau"]
    assert energy < L["vf_pk_bound"] * q and energy > L["vsd_max"] * 0.5 * q
    assert K["air"]["route"] + rise < 150.0 and abs(L["k_max"] * rise - (150.0 - K["air"]["route"])) < 1e-9
    assert Q0["i_dock"] < K["sel"]["rdef"]["ism"] and L["i_at_tp"] > L["is_dc"]
    out = open(OUT, encoding="utf-8").read()
    assert "as an I2t of 1.024 A2s is WITHDRAWN" in out and "no sharing is credited" in out


def t_l4f03_the_efuse_keeps_the_contact_inside_its_rating_and_the_fuse_and_ptc_do_not():
    R = _R()
    m = _M()
    K, L = R["K"], R["L"]
    lo, hi = L["ilim"]
    typ = 18.0 / m.F16_RILIM_K
    assert abs(lo - typ * (1 - L["ilim_rel"]) / (1 + m.F16_RILIM_TOL)) < 1e-12 and abs(hi - typ * (1 + L["ilim_rel"]) / (1 - m.F16_RILIM_TOL)) < 1e-12
    assert abs(L["ilim_rel"] - 0.1) < 1e-9, "the wider printed spread is not the 30 kOhm row's"
    assert K["aux_a"] < lo and hi < L["c813"] and L["t_lim"]["margin 65 C"] < 85.0
    # the fuse: 175 to 200 percent of 2 A straddles the contact's 3.5 A for up to the 135 percent row's time
    assert 1.75 * 2.0 <= L["c813"] < 2.0 * 2.0 and L["fuse_tc"]["t135"] > 1.0
    # the PTC: its hot hold under the load, its cold trip over the contact, its interrupt under the pack's current
    assert L["ptc_h"][70] < K["aux_a"] and L["ptc_trip_cold"] > L["c813"] and L["ptc"]["imax"] < R["H"]["Q"]["i_dock"]
    drop = K["aux_a"] * (L["ron"][2] + L["r813"] * 2.0) + K["ret"][3][2] * L["r813"]
    assert abs(L["drop"] - drop) < 1e-12 and L["vsys_e_min"] > K["ap_vin"][0]
    assert L["t_ramp"][0] < L["t_ramp"][1] and L["i_inrush"] < lo
    page = open(PAGE, encoding="utf-8").read()
    assert "**0.1408 mA is the quantified subset of the held-pack drain**" in page and "at most 1 mA" in page
    assert os.path.isfile(os.path.join(TOOLS, "check_contracts.py")), "check_contracts.py is not in the tree"


def t_the_record_states_each_review_items_status():
    page = open(PAGE, encoding="utf-8").read()
    sec = page[page.index("## 16. The fix round for the review of the provisional fixes"):]
    for item, status in (("objection 1", "**CONDITIONAL**"), ("objection 2", "**CLOSED as an analysis basis"), ("objection 3", "**OPEN**"),
                         ("objection 4", "**CONDITIONAL**"), ("service from the hot state", "**CONDITIONAL**"),
                         ("L4-F03", "**sustained-overload remedy drafted; fault qualification open**")):
        rows = [l for l in sec.splitlines() if l.startswith("|") and item in l]
        assert rows and status in rows[0], "%s has no status row" % item
    assert sec.count("| Affected circuit or function |") == 1


def t_cp01_u42s_envelope_rests_on_printed_limits_and_states_its_inferred_ceiling():
    R = _R()
    m = _M()
    L, M, K, H = R["L"], R["M"], R["K"], R["H"]
    assert abs(M["i_pk"] - H["vsys_top"] / (L["ron"][0] + M["r_path_min"])) < 1e-9 and L["ron"][0] < L["ron"][2]
    assert abs(M["i2t_pk"] - M["i_pk"] ** 2 * L["tsoft"]) < 1e-12
    assert M["treg"][1] > L["tcl"][1], "the start into a short does not time out later than the overload timer"
    assert abs(M["duty_start"] - M["treg"][1] / (M["treg"][1] + L["tretry"][0])) < 1e-12 and M["rise_retry"] < M["rise_steady"]
    out17 = open(OUT, encoding="utf-8").read().split("17a. ")[1].split("17b. ")[0]
    assert "EXTRAPOLATION, not a bound" in out17 and "TARGET for the recorded peak" in out17 and "no duty is claimed" in out17 and "NOT PRINTED" in out17
    assert M["v_in_pk"] < M["abs_in"], "the input spike at the ceiling passes U42's absolute maximum"
    assert 2 * M["fan_simul"] + K["aux"]["U12"] <= L["ilim"][0] + 1e-12 and M["fan_stag"] > M["fan_simul"] > K["aux"]["J_FAN1"]
    assert M["vsys_e_lim"] < L["vsys_e_min"] and M["vsys_e_lim"] > K["ap_vin"][0]
    out = open(OUT, encoding="utf-8").read()
    assert "NOT an instantaneous ceiling" in out and "0.0091" not in out.split("16e. ")[1], "the typical 45 A still bounds a pulse"
    assert "STATUS: sustained-overload remedy drafted; fault qualification open" in out
    row = [x for x in m.downstream(R) if x[0] == "E11-38"][0][3]
    for case in ("(b) an operating overload", "(c) a 10 mOhm short applied", "(d) a start into that short", "(e) one hour of retry", "(f) with the fans"):
        assert case in row, case


def t_cp02_the_docking_qualification_exceeds_the_whole_waveform():
    R = _R()
    m = _M()
    M, Q0 = R["M"], R["H"]["Q"]
    assert M["dock_q"][0] > Q0["i_dock"] and M["dock_q"][1] > Q0["tau"] and m.F17_TMB > R["K"]["air"]["route"]
    assert M["dock_q_t80"] > R["L"]["t_over_is"]
    row = [x for x in m.downstream(R) if x[0] == "E11-30"][0][3]
    assert "WHOLE hot docking waveform" in row and "Q-NXP-1" in row and "board P" in row
    assert "judged on TJ alone" not in row


def t_cp03_the_charger_draft_writes_none_of_the_withdrawn_statements():
    R = _R()
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "gen_sch_a.py")
        shutil.copy(GEN_A, a)
        _apply("apply_gen_sch_a_charger.py", a)
        txt = open(a, encoding="utf-8").read()
    for w in R["M"]["withdrawn"]:
        assert w not in txt, "the draft still writes %r" % w
    assert "SIZED to an RDS(on) allowance" in txt and "33.12 K/W" in txt and "no sharing credited" in txt


def t_every_measurement_row_names_its_specimen_and_blocks_only_the_final_release():
    page = open(PAGE, encoding="utf-8").read()
    sec = page[page.index("### 17d. "):]
    assert "| Row | Specimen | Represents | Transfers | Blocks only |" in sec
    for iid in ("E11-29", "E11-30", "E11-36", "E11-37", "E11-38", "E11-35"):
        rows = [l for l in sec.splitlines() if l.startswith("| Row %s |" % iid)]
        assert len(rows) == 1 and rows[0].count("|") == 6, iid
        assert "release" in rows[0].split("|")[5] or "selection" in rows[0].split("|")[5] or "choice" in rows[0].split("|")[5], iid


def t_the_board_a_drafts_add_disjoint_designators():
    """Every board A draft under records/l4e* applied to a copy of gen_sch_a.py (L4-E8's bank after L4-E6's R12, its stated order);
    the designators each adds are read from the text it writes, and no two drafts add the same one (L6P-F01)."""
    _M()
    import glob
    pat = re.compile(r"\b([RCDLQU]\d{1,3}|J_[A-Z0-9]+)\b")
    drafts = sorted(glob.glob(os.path.join(ROOT, "v2", "docs", "records", "l4e*", "apply_gen_sch_a_*.py")))
    assert os.path.join(REC, "apply_gen_sch_a_charger.py") in drafts and len(drafts) >= 7
    r12 = [d for d in drafts if d.endswith("apply_gen_sch_a_r12.py")]
    added = {}
    for d in drafts:
        with tempfile.TemporaryDirectory() as td:
            a = os.path.join(td, "gen_sch_a.py")
            shutil.copy(GEN_A, a)
            pre = r12 if d.endswith("apply_gen_sch_a_bank.py") else []
            for s in pre:
                assert _run([s, a, "--write"]).returncode == 0, s
            before = set(pat.findall(open(a, encoding="utf-8").read()))
            r = _run([d, a, "--write"])
            assert r.returncode == 0, "%s: %s" % (os.path.relpath(d, ROOT), r.stderr.decode()[-200:])
            added[os.path.relpath(d, ROOT)] = set(pat.findall(open(a, encoding="utf-8").read())) - before
    mine = added[os.path.relpath(os.path.join(REC, "apply_gen_sch_a_charger.py"), ROOT)]
    assert {"R228", "U42", "C236", "C237", "C238", "C239", "D23", "Q39", "Q40"} <= mine and "R221" not in mine
    names = sorted(added)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            both = added[x] & added[y]
            assert not both, "%s and %s both add %s" % (x, y, sorted(both))


def t_the_fans_rail_covers_vsys_e_and_the_branch_stays_under_u42s_least_limit():
    R = _R()
    m = _M()
    N, L, K, H = R["N18"], R["L"], R["K"], R["H"]
    assert N["vin"][0] <= N["vsys_e_at_lim"] and N["vin"][1] >= H["vsys_top"], "the rail's input range does not cover VSYS_E"
    assert m.L7_FAN["v_lo"] < N["vout"][0] and N["vout"][2] < m.L7_FAN["v_hi"], "the rail at FB's limits leaves the fans' printed window"
    lo = N["vfb"][0] * (1 + m.F18_FB[0] * 0.99 / (m.F18_FB[1] * 1.01))
    assert abs(N["vout"][0] - lo) < 1e-9 and N["vout"][0] < N["vfb"][0] * (1 + m.F18_FB[0] / m.F18_FB[1]), "the divider's tolerance is not in the window"
    assert N["run_on"][2] < N["vsys_e_at_lim"] and N["run_off"][0] > K["ap_vin"][0], "the RUN divider is not between the floor and U12's start"
    assert N["l_isat"] > N["ilim"][2], "the inductor saturates under the regulator's limit"
    assert abs(N["i_decl"] - (K["aux"]["U12"] + N["p_fans"] / (m.F18_ETA * N["vsys_e_floor"]) + m.F18_IQ_PWM)) < 1e-9
    assert N["i_decl"] < L["ilim"][0] and N["i_decl"] > 1.0, "the branch's declared current is not between the old 1.0 A and U42's least limit"
    assert N["t63_vin"][1] < H["vsys_top"], "TPS63070's range would cover VSYS_E"
    assert N["b_slot_v"] < m.L7_FAN["v_lo"] and not N["b_has_12v"], "board B's slot rail covers the coolers, or a +12V net exists"
    page = open(PAGE, encoding="utf-8").read()
    assert "| E11-40 | implementation | Layer 8 board B generator owner |" in page
    row = [x for x in m.downstream(R) if x[0] == "E11-38"][0][3]
    assert "(g) one fan stalled" in row and "U22 never disables" in row and "(h) an intermittent short" in row and "regulated current recorded" in row


def t_the_board_e_drafts_add_disjoint_designators():
    """Every board E draft under records/l4e* composed on a copy of gen_sch_e.py in L4-E9's change-list order (q1, u5_grade, hold,
    input_limit, backstop, f1, hotswap, entry, solar_guard, aux; the timer as the LM5069 alternative after hotswap); the designators each
    adds are read from the text it writes, in part-call position and as tokens outside comments, and no two drafts add the same one
    (Astra's recheck of set 27, blocking discrepancy 1: the aux draft once took U18, R59 to R65 and C65 to C71 from the solar drafts)."""
    _M()
    recs = os.path.join(ROOT, "v2", "docs", "records")
    main = [("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
            ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux")]
    alt = [("l4e9", "hotswap"), ("l4e11", "timer")]
    call = re.compile(r'(?:ic|part|c|r|ph|tp|nfet|q)\("([A-Z][A-Z0-9_]*)"')
    tok = re.compile(r"\b([RCDLQU]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3})\b(?!-)")
    strip = lambda s: "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())
    added = {}
    for seq in (main, alt):
        with tempfile.TemporaryDirectory() as d:
            a = os.path.join(d, "gen_sch_e.py")
            shutil.copy(GEN_E, a)
            before = open(a, encoding="utf-8").read()
            c0, t0 = set(call.findall(before)), set(tok.findall(strip(before)))
            for rec, name in seq:
                s = os.path.join(recs, rec, "apply_gen_sch_e_%s.py" % name)
                need(s, "board E's draft %s/%s" % (rec, name))
                r = _run([s, a, "--write"])
                assert r.returncode == 0, "%s/%s refused: %s" % (rec, name, r.stderr.decode()[-200:])
                after = open(a, encoding="utf-8").read()
                c1, t1 = set(call.findall(after)), set(tok.findall(strip(after)))
                added.setdefault("%s/%s" % (rec, name), set()).update((c1 - c0) | (t1 - t0))
                c0, t0 = c1, t1
    mine = added["l4e11/aux"]
    assert {"U22", "L4", "R103", "R109", "C135", "C141"} <= mine and not ({"U18", "R59", "R65", "C65", "C71"} & mine), sorted(mine)
    names = sorted(added)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            if {x, y} == {"l4e11/entry", "l4e11/timer"}:
                continue        # alternatives that refuse each other, never on one board
            both = added[x] & added[y]
            assert not both, "%s and %s both add %s" % (x, y, sorted(both))


def t_every_specimen_block_names_its_thermal_boundaries_and_its_re_test_trigger():
    """L4-QR01 (the owner's review of 3 October): every measurement row's block in 17d records its specimen, lot, operating point,
    mounting, thermal boundaries, uncertainty, permitted extrapolation and re-test triggers; E11-29's names the five boundaries and a
    comparison rule; the pulse test stays prototype evidence; no current text calls a result layout-independent."""
    page = open(PAGE, encoding="utf-8").read()
    sec = page[page.index("### 17d. "):page.index("### 17e. ")]
    blocks = re.split(r"\n#### Block ", sec)[1:]
    ids = [b.split(":", 1)[0] for b in blocks]
    assert sorted(ids) == sorted(["E11-29", "E11-30", "E11-36", "E11-37", "E11-38", "E11-35"]), ids
    for b in blocks:
        bid = b.split(":", 1)[0]
        assert "**Thermal boundaries:**" in b or "thermal boundaries:**" in b, "%s names no thermal boundaries" % bid
        assert "**Re-test when:**" in b, "%s names no re-test trigger" % bid
        assert "uncertainty:**" in b and "extrapolation" in b, "%s lacks its uncertainty or its extrapolation" % bid
    b29 = [b for b in blocks if b.startswith("E11-29")][0]
    for w in ("device spacing", "copper connectivity", "neighbouring sources", "airflow", "enclosure coupling", "the comparison rule", "M-matrix"):
        assert w in b29, "E11-29's block omits %r" % w
    b30 = [b for b in blocks if b.startswith("E11-30")][0]
    assert "not a\n  production limit" in b30 or "not a production limit" in b30
    current = sec.replace('"layout-independent", and that E11-29', "")
    assert "layout-independent" not in current and "layout-independent" not in page.replace('"layout-independent", and that E11-29', "")
    out = open(OUT, encoding="utf-8").read()
    assert "17d. L4-QR01" in out and "not a production limit" in out
