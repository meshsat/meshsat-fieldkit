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
L4-CP03) adds: U42's fault envelope rests only on printed limits and states its inferred extrapolation; the fans' start fits U42's least limit;
the docking waveform's qualification exceeds the waveform; the charger draft writes none of the withdrawn statements; each measurement
row names its specimen and blocks only the final release. The fans' feed round (section 18) adds: the mixers' rail covers VSYS_E's
range and holds the fans' printed window, its RUN divider sits between the floor and U12's start, the inductor's saturation sits over the
regulator's limit, the branch's declared current with the rail's input at the floor stays under U42's least limit, the board E draft writes
the rail and the four-wire fans and no flyback, and board B's feed is read as not covering the coolers. Round 9 (section 19, 4 October 2026) adds: record l8p's L8P-F02 and L8P-F03 are
corrected, and board A composed in L4-E9's order runs to its end (board E too, with L4-E7's defect stood in); the third battery FET Q42 sits
on record l9stk's junction limit, reproduced, and E11-29 carries it; E11-37 is bound to the three-device network and stays open; DD-3's
one design-out attempt fails on L2 and stays open with its condition, J_DCIN drafted as the XT60-F; IF-1's hold outlasts the breaker's
start, its levels clear every threshold they meet, and the defect it answers is shown on the drafts as they stood. Round 10 (section 20)
adds: DD-7's board A side redrawn against record l8p's L8P-F04 and L8P-F05 composes in L4-E9's order, reads DRAWN in the regenerated
netlist and FAIL on five mutations, and holds on C-PROT (the held return sets the inhibit within 1 ms, the hold outlasts the restart,
the latch keeps CELL+ dead whatever the LM5069's resistor); T2's 9/8 is read in closed form. Round 11 (section 21) adds: E-1 holds at its
case on C-PROT rev 1 over a scan of every split of the three FETs' RDS(on) under the allowance, at the charger's printed least drive, with
the bar 40.78 K/W, and fails with the even split's bar, a bar 1 % looser, the split read as even or the drive read at 10 V; unequal
coupling is bounded by the largest of each impedance; E11-37 stays open with Q-TI-17 (e) and (f) and its fallback conditional on a
typical figure; V1's minors (R84 pulse-rated; R256's 6.8k superseded) read in the netlist with more mutations failing. Round 12 (section
22, the independent check V2's V2-B1) adds: the bleed of CELL+ counts the sources into the node (the round refuses the no-source bleed, and the
no-source figure is shown to pass where the sourced one fails); V2's figures reproduce; of V2's three corrections the selected one, R256
back at 4.7 kOhm, keeps the bleed at the hot bound inside the hold's least and U47's RESET within TI's recommended current in every state
without a second fault, the battery FETs' orientation read in the netlist; the minors V2-m1 to m5 are carried. Round 13 (section 23, the
owner's supplier-delta review's DELTA-02) adds: the body-diode method heats and reads nothing 'alone' on the common nets the draft and the
regenerated netlist show, and the round refuses to select it; the selected method addresses one device by its own gate, on a specimen
whose gates are apart and not on board A as drafted; its budget, powers and currents reproduce in closed form; the procedure TP-E11-29
quotes this record word for word and stays NOT EXECUTABLE; section 20c is restated on the PTC's printed points. Round 14 (section 24, the
independent recheck V2R) adds: round 13's fixture joins the pours in a reading and the redrawn one leaves the device under test alone in
every state, with its margins on the printed rows; each junction is judged at its own row's worst split, which a scan confirms, with the
baseline in the limit's line, and a search on a fresh seed finds no specimen accepted over 150 C while round 13's lines accept some; the
minors are answered and the procedure keeps the recheck among its preconditions. Nothing here writes into the tree: drafts run on
temporary copies.
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
        for who, c in m.R9_COMMITS.items():
            if subprocess.run(["git", "-C", ROOT, "cat-file", "-e", c], capture_output=True).returncode != 0:
                raise Skip("record %s's commit %s is not in this repository" % (who, c[:8]))
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
    # FW-C08 "as written" is the contract's own behaviour cell, read from the tree, never typed. Before set 28 it asserted SHORE_INHIBIT on
    # the cold hold (the record's finding U4-F1 and E11-03, which asked Layer 5 to restate it); Layer 5's power pass (records/l5pwr,
    # 3 October 2026) restated it, so the cell now says never for a temperature hold. The first version of this predicate pinned the
    # old wording and failed on the day the restatement landed: a rule about history. The property is that the record quotes the
    # contract's cell and that the cell is in one of the two states the record knows.
    hw = " ".join(open(os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md"), encoding="utf-8").read().split())
    cell = re.search(r"\| FW-C08 \| (.*?) \| (.*?) \| ", hw).group(2)
    assert R["fwc08"] == cell, "FW-C08 as written is not the contract's FW-C08 behaviour cell"
    assert ("below 0 C" in cell) or ("never for a temperature" in cell), \
        "FW-C08 neither asserts the cold hold on SHORE_INHIBIT (U4-F1 open) nor says never for a temperature hold (U4-F1 resolved by E11-03)"
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
        for want in ('"21": "CH_BATDRV", "22": "VBAT"', '"C5219071")', 'for _qb in ("Q39", "Q40", "Q42"): nfet(_qb, ',
                     '"CH_BATDRV", "CH_BATQ", "VBAT", fp="LFPAK56", lcsc="C3278350")', '"LFPAK56": "Package_TO_SOT_SMD:LFPAK56"',
                     '"CH_BATQ", "CELL_FUSED", "RS2512")', 'r("R149", "10R", "CH_BATQ", "CH_SRP_F")', 'c("C236", ',
                     '_intent.rail("CH_BATQ", 14.4, 10.0, 18.0, "R17"', '"Q39", always_on=True', 'fed_from="CH_BATQ"',
                     '"R17", "Q39", "Q40", "Q42", "C236", "U42", "R228", "C237", "C238", "C239", "D23", "R88", "R89", "U46", "R86", "R87", "C105", "R105", "D24", "Q43", "C16"',
                     '{"1": "VSYS_DOCK", "2": "GND", "3": "GND"', 'loads={"U42": 1.32, "U4": 2.0', 'loads={"Q39": 3.34, "Q40": 3.33, "Q42": 3.33}',
                     '"7": "EF_UVLO"', '_intent.rail("VSYS_DOCK", 14.4, 1.32, 1.32, "U42", source_ic='):
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
        assert '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "U22", source_ic=' in te and 'ic("U22", 21, "LTC3115EFE-1' in te
        assert '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "L4"' not in te, "L8P-F03: +12V_FAN still names L4"
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


def t_cp01_u42s_envelope_rests_on_printed_limits_and_states_its_inferred_extrapolation():
    R = _R()
    m = _M()
    L, M, K, H = R["L"], R["M"], R["K"], R["H"]
    assert abs(M["i_pk"] - H["vsys_top"] / (L["ron"][0] + M["r_path_min"])) < 1e-9 and L["ron"][0] < L["ron"][2]
    assert abs(M["i2t_pk"] - M["i_pk"] ** 2 * L["tsoft"]) < 1e-12
    assert M["treg"][1] > L["tcl"][1], "the start into a short does not time out later than the overload timer"
    assert abs(M["duty_start"] - M["treg"][1] / (M["treg"][1] + L["tretry"][0])) < 1e-12 and M["rise_retry"] < M["rise_steady"]
    out17 = open(OUT, encoding="utf-8").read().split("17a. ")[1].split("17b. ")[0]
    assert "EXTRAPOLATION, not a bound" in out17 and "TARGET for the recorded peak" in out17 and "no duty is claimed" in out17 and "NOT PRINTED" in out17
    assert M["v_in_pk"] < M["abs_in"], "the input spike at the extrapolation passes U42's absolute maximum"
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
    assert "SIZED to an RDS(on) allowance" in txt and "no sharing credited" in txt
    assert "45.88 K/W" in txt and "20.39 K/W" in txt and "33.12 K/W target at +70 C air is withdrawn" in txt


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
            if d.endswith("apply_gen_sch_a_dd7.py"):        # round 9: after this record's charger and record l8p's PTC draft (its commit)
                pre = [os.path.join(REC, "apply_gen_sch_a_charger.py"), _l8p_ptc(td)]
            for s in pre:
                assert _run([s, a, "--write"]).returncode == 0, s
            before = set(pat.findall(open(a, encoding="utf-8").read()))
            r = _run([d, a, "--write"])
            assert r.returncode == 0, "%s: %s" % (os.path.relpath(d, ROOT), r.stderr.decode()[-200:])
            added[os.path.relpath(d, ROOT)] = set(pat.findall(open(a, encoding="utf-8").read())) - before
    dd7 = added[os.path.relpath(os.path.join(REC, "apply_gen_sch_a_dd7.py"), ROOT)]
    assert {"Q44", "Q45", "Q46", "Q47", "Q48", "Q49", "R82", "R83", "R106", "R107", "R108", "R109", "R144", "D25",
            "U47", "U48", "Q50", "Q51", "Q52", "D26", "D27", "R84", "R85", "R233", "R249", "R250", "R251", "R252", "R253", "R254", "R255",
            "R256", "C241", "C248"} <= dd7, sorted(dd7)
    mine = added[os.path.relpath(os.path.join(REC, "apply_gen_sch_a_charger.py"), ROOT)]
    assert {"R228", "U42", "C236", "C237", "C238", "C239", "D23", "Q39", "Q40", "Q42", "Q43", "U46", "R86", "R87", "R88", "R89", "R105", "C105", "D24"} <= mine
    assert "R221" not in mine and not ({"Q41", "U44", "U45", "RT1"} & mine), sorted(mine)
    names = sorted(added)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            both = added[x] & added[y]
            assert not both, "%s and %s both add %s" % (x, y, sorted(both))


def _l8p_ptc(d):
    """Record l8p's board A PTC draft, read from its commit by sha256 (the enable loop's two nets and RT1; round 9's DD-7 draft follows it)."""
    m = _M()
    rel, want = "v2/docs/records/l8p/apply_gen_sch_a_ptc.py", "c8e4eeb499491eab773332b090ef1ebb8f0d14975ffedf9e750f5c64ff89d92f"
    blob = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (m.R9_COMMITS["l8p"], rel)], capture_output=True).stdout
    assert hashlib.sha256(blob).hexdigest() == want, "record l8p's PTC draft is not the one this record composed with"
    p = os.path.join(d, "l8p_apply_gen_sch_a_ptc.py")
    open(p, "wb").write(blob)
    return p


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
    """Every board E draft the tree carries, composed on a copy of gen_sch_e.py in L4-E9's change-list order (d8dec31's cin, q1, u5_grade,
    hold, input_limit, backstop, f1, hotswap, entry, solar_guard, aux; the timer only as the LM5069 alternative after hotswap): the designators
    each adds are read from the text it writes, as new names (in part-call position and as tokens outside comments, which catches a loop
    such as the solar guard's `for _cf in (...)`) and as duplicate literal part calls (which catches a draft that writes a name another draft
    already took). No designator this record's drafts add may meet another draft's (Astra's recheck of set 27, blocking discrepancy 1; the
    set 27 run's C135 and C136). Collisions between other records' drafts are theirs: the record's 17e names the one known (C65)."""
    _M()
    recs = os.path.join(ROOT, "v2", "docs", "records")
    net = os.path.join(ROOT, "v2", "ecad", "pcb-e1-dock-e7", "out", "pcb-e1-dock.net")
    main = [("d8dec31", "cin"), ("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"),
            ("l4e9", "f1"), ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux")]
    alt = [("l4e9", "hotswap"), ("l4e11", "timer")]
    call = re.compile(r'(?:ic|part|c|r|ph|tp|nfet|q)\("([A-Z][A-Z0-9_]*)"')
    lit = re.compile(r'(?<![A-Za-z_.])(?:ic|part|c|r|ph|tp|nfet)\(\s*"([A-Z][A-Z0-9_]*)"')
    tok = re.compile(r"\b([RCDLQU]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3})\b(?!-)")
    strip = lambda s: "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())
    added, dup_mine = {}, []
    for seq in (main, alt):
        with tempfile.TemporaryDirectory() as d:
            a = os.path.join(d, "gen_sch_e.py")
            shutil.copy(GEN_E, a)
            before = open(a, encoding="utf-8").read()
            c0, t0 = set(call.findall(before)), set(tok.findall(strip(before)))
            for rec, name in seq:
                s = os.path.join(recs, rec, "apply_gen_sch_e_%s.py" % name)
                need(s, "board E's draft %s/%s" % (rec, name))
                r = _run([s, a, net] if rec == "d8dec31" else [s, a, "--write"])
                assert r.returncode == 0, "%s/%s refused: %s" % (rec, name, r.stderr.decode()[-200:])
                after = open(a, encoding="utf-8").read()
                c1, t1 = set(call.findall(after)), set(tok.findall(strip(after)))
                added.setdefault("%s/%s" % (rec, name), set()).update((c1 - c0) | (t1 - t0))
                c0, t0 = c1, t1
            final = open(a, encoding="utf-8").read()
            seen = {}
            for ln in strip(final).splitlines():
                for ref in lit.findall(ln):
                    seen[ref] = seen.get(ref, 0) + 1
            mine_all = added.get("l4e11/aux", set()) | added.get("l4e11/entry", set()) | added.get("l4e11/timer", set())
            dup_mine += [ref for ref, k in seen.items() if k > 1 and ref in mine_all]
    mine = added["l4e11/aux"]
    assert {"U22", "L4", "R103", "R109", "C142", "C148"} <= mine and not ({"C135", "C136", "C141"} & mine), sorted(mine)
    assert not dup_mine, "this record's designators written twice: %s" % sorted(set(dup_mine))
    for x in sorted(k for k in added if k.startswith("l4e11/")):
        for y in sorted(added):
            if y == x or {x, y} == {"l4e11/entry", "l4e11/timer"}:
                continue        # the entry and the timer are alternatives that refuse each other, never on one board
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


WITHDRAWN_PHRASES = ("up to 1.5 s", "at most 1.5 s", "duty at most 0.75", "duty of at most 0.75", "layout-independent")


def t_the_withdrawn_fault_and_transfer_phrases_appear_only_in_withdrawal_sentences():
    """The coordinator's residue check of a1d15601: the 566 A as a ceiling, the start into a short as lasting up to (or at most) 1.5 s,
    a retry duty of 0.75 and a layout-independent pulse result were withdrawn in 17a and 17d; in the record, the README, the printed
    output and the drafts' text each may appear only in a sentence that says it is withdrawn (or historical)."""
    files = [PAGE, OUT, os.path.join(REC, "README.md")] + [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.startswith("apply_")]
    bad = []
    for p in files:
        flat = " ".join(open(p, encoding="utf-8").read().replace("\\n", " ").split())
        for sent in re.split(r"(?<=[.;:!?])\s+(?=[*A-Z(])", flat):
            low = sent.lower()
            hit = [w for w in WITHDRAWN_PHRASES if w in low]
            if any("566" in cl and "ceiling" in cl.lower() for cl in re.split(r"[.;]\s+", sent)):
                hit.append("566 A as a ceiling")
            if hit and "withdrawn" not in low and "historical" not in low:
                bad.append("%s: %s: %s" % (os.path.basename(p), hit, sent[:120]))
    assert not bad, bad[:4]


# ---- round 9 (section 19, 4 October 2026)
_STUB = '''"""stand-in schlayout (test_l4e11, round 9): records the part table, lays out nothing"""
import json, os
def run(parts, sections, power, bypass, header, phase, board_title):
    json.dump(dict(parts=[dict(ref=p["ref"], nets=p["nets"], value=p["value"]) for p in parts]), open(os.environ["L4E11_PARTS_JSON"], "w"))
    return ("A3", 1, 1, 1)
'''
_RUNNER = '''import importlib.util, os, runpy, sys
_here = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("schlayout", os.path.join(_here, "stub_schlayout.py"))
_m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m); sys.modules["schlayout"] = _m
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
'''
# L4-E9's change list per board (records/l4e9/L4-POWER-ARCHITECTURE.md section 3), the drafts on main.
# Round 12 (the independent check V2's V2-m9): on the candidate's line (fnd/v2cand at dfa1eef2) the list's rows 24 to 33 name record
# l8r2's packrtn (R-201), slotlm (R-199) and fb01 (R-200) where this order has l8r2's d8v3 and vbus20ov. Those three drafts are NOT in
# this branch's tree (fnd/l8r3 at 89924e40), so board A is composed here in main's order, the one this tree can show. The list's order is
# r12, guard, charger, r11, bank, r138, u17, gnd002, hotr1, packrtn, slotlm, fb01, then record l8p's ptc and this record's dd7
# (_compose10), mainpb, lcsc; V2 composed it on the candidate (778 parts, DRAWN). In that order slotlm sets the references higher, so
# the round 10 test's reading of mainpb's references (R257 and C249) is main's order's and moves with it (the integrator's change).
_ORDER9 = {"a": [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
                 ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("d8dec31", "mainpb"), ("l6r2", "lcsc")],
           "e": [("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
                 ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("d8dec31", "cin"), ("l6r2", "xal_land"),
                 ("l6r2", "lcsc")]}
_NET9 = {"a": os.path.join(ROOT, "v2", "ecad", "pcb-a-power-a23", "out", "pcb-a-power.net"), "e": os.path.join(ROOT, "v2", "ecad", "pcb-e1-dock-e7", "out", "pcb-e1-dock.net")}
# L4-E7's backstop draft leaves C66 to C68 without a G14 class (record l8p's finding L8P-F01, L4-E7's to correct): a scratch stand-in so
# board E's generator runs on; it is never a draft and never applied
_F01 = ('_DEC_RULED = ("R", "D", "L", "A", "B1", "B2")',
        'for _e in _intent._I["bypass"]: _DEC_CLASS.setdefault(_e["cap"], ("D", "test stand-in, not a class"))\n_DEC_RULED = ("R", "D", "L", "A", "B1", "B2")')


def _compose9(board, d):
    g = os.path.join(d, "gen_sch_%s.py" % board)
    shutil.copy(os.path.join(TOOLS, "gen_sch_%s.py" % board), g)
    for rec, name in _ORDER9[board]:
        s = os.path.join(ROOT, "v2", "docs", "records", rec, "apply_gen_sch_%s_%s.py" % (board, name))
        need(s, "board %s's draft %s/%s" % (board.upper(), rec, name))
        r = _run([s, g, _NET9[board]] if rec == "d8dec31" else [s, g, "--write"])
        assert r.returncode == 0, "%s/%s refused: %s" % (rec, name, r.stderr.decode()[-200:])
    return g


def _run_generator9(g, project, d):
    """The composed generator run to its end with a stand-in layout (kisch, intent and the checks are the tree's own); the part table."""
    open(os.path.join(d, "stub_schlayout.py"), "w", encoding="utf-8").write(_STUB)
    open(os.path.join(d, "run_stub.py"), "w", encoding="utf-8").write(_RUNNER)
    js = os.path.join(d, "parts.json")
    env = dict(os.environ, PYTHONPATH=TOOLS, L4E11_PARTS_JSON=js, KICAD_SYMBOLS=os.path.join(d, "no-kicad-symbols"), PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-B", os.path.join(d, "run_stub.py"), g, os.path.join(d, project + ".kicad_sch"), project],
                       capture_output=True, cwd=d, env=env)
    log = (r.stdout + r.stderr).decode("utf-8", "replace")
    assert r.returncode == 0 and os.path.isfile(js), "the composed generator refused: %s" % log[-400:]
    assert os.path.isfile(os.path.join(d, "out", project + "-intent.json")), "intent.write did not run"
    import json
    return {p["ref"]: p for p in json.load(open(js, encoding="utf-8"))["parts"]}, json.load(open(os.path.join(d, "out", project + "-intent.json"), encoding="utf-8"))


def t_round9_l8p_f02_and_f03_the_composed_generators_run_to_their_end():
    """L8P-F02 and L8P-F03: board A composed in L4-E9's order runs to its end with intent.write (VSYS_DOCK after VBAT, with source_ic);
    board E too, with L4-E7's L8P-F01 stood in; +12V_FAN's source is U22, which is on the net."""
    _M()
    with tempfile.TemporaryDirectory() as d:
        ga = _compose9("a", d)
        txt = open(ga, encoding="utf-8").read()
        assert txt.index('_intent.rail("VBAT", ') < txt.index('_intent.rail("VSYS_DOCK", '), "VSYS_DOCK is declared before VBAT"
        parts, it = _run_generator9(ga, "pcb-a-power", d)
        assert it["rails"]["VSYS_DOCK"]["source"] == "U42" and it["rails"]["VSYS_DOCK"]["fed_from"] == "VBAT"
        assert set(it["rails"]["CH_BATQ"]["loads"]) == {"Q39", "Q40", "Q42"} and it["rails"]["VBAT"]["fed_from"] == "CH_BATQ"
        assert parts["U42"]["nets"]["7"] == "EF_UVLO" and parts["U46"]["nets"]["5"] == "EF_UVLO" and parts["U46"]["nets"]["2"] == "EF_UVLO"
        assert parts["Q43"]["nets"]["3"] == "RAIL_EN" and parts["Q43"]["nets"]["1"] == parts["U46"]["nets"]["4"] == "SYS_HOLD_G"
        for q in ("Q39", "Q40", "Q42"):
            assert parts[q]["nets"] == {"1": "VBAT", "2": "VBAT", "3": "VBAT", "4": "CH_BATDRV", "5": "CH_BATQ"}, q
        assert any(b["cap"] == "C238" and b["part"] == "U46" and b["class"] == "D" for b in it["bypass"])
    with tempfile.TemporaryDirectory() as d:
        ge = _compose9("e", d)
        t2 = open(ge, encoding="utf-8").read()
        assert t2.count(_F01[0]) == 1
        open(ge, "w", encoding="utf-8").write(t2.replace(_F01[0], _F01[1]))
        parts, it = _run_generator9(ge, "pcb-e1-dock", d)
        assert it["rails"]["+12V_FAN"]["source"] == "U22" and "+12V_FAN" in parts["U22"]["nets"].values()
        assert "+12V_FAN" not in parts["L4"]["nets"].values()
        assert parts["J_DCIN"]["nets"] == {"1": "DC_IN", "2": "GND_V"} and "XT60-F" in parts["J_DCIN"]["value"]


def t_round9_the_third_fet_sits_on_l9stks_junction_limit_and_e11_29_carries_it():
    R = _R()
    m = _M()
    S = R["S19"]
    for n_ in (2, 3):
        pe = (S["i"] / n_) ** 2 * m.F16_RA
        assert abs(S[n_]["p"] - pe) < 1e-12
        assert abs(S[n_]["apart"] - (150.0 - S["t0"] - S["band"] - S["r17_allow"] * S["pr17"]) / pe) < 1e-9
        assert abs(S[n_]["apart"] - S["rec"][n_][2]) <= 0.001 * S["rec"][n_][2] + 0.011, "record l9stk's allowance is not reproduced"
    assert S["rec"][3][2] > S["zsum_pair_old"] > S["rec"][2][2], "the three's allowance is not looser than the pair's former target"
    row = [x for x in m.downstream(R) if x[0] == "E11-29"][0][3]
    assert "45.88 K/W" in row and "20.39 K/W" in row and "Q42" in row and "23.93 A from 76.25 C" in row and "withdrawn" in row
    page = open(PAGE, encoding="utf-8").read()
    b29 = page.split("#### Block E11-29")[1].split("#### Block E11-30")[0]
    assert "Q42" in b29 and "45.88 K/W" in b29 and "R17" in b29 and "band" in b29


def t_round9_e11_37_is_bound_to_the_three_and_stays_open():
    R = _R()
    m = _M()
    S, L, H = R["S19"], R["L"], R["H"]
    assert abs(S["ciss3"][0] - 3 * L["ciss_t"]) < 1e-15 and abs(S["ciss3"][1] - 3 * L["ciss_0"]) < 1e-15
    assert S["ciss_ratio"][0] > 1.0 and S["ciss_ratio"][1] > S["ciss_ratio"][0], "the three are not shown over TI's 5 nF"
    row = [x for x in m.downstream(R) if x[0] == "E11-37"][0][3]
    assert "three-device network" in row and "share of the current" in row and "a result with the pair does not transfer" in row
    page = open(PAGE, encoding="utf-8").read()
    b37 = page.split("#### Block E11-37")[1].split("#### Block E11-38")[0]
    assert "current sharing" in b37 and "thermal coupling" in b37 and "Thermal improvement does not close the gate-drive question" in b37
    assert "Q-TI-17, extended" in open(os.path.join(REC, "clarification", "TI-QUESTIONS.md"), encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read().split("19d. ")[1].split("19e. ")[0]
    assert "STATUS: OPEN" in out


def t_round9_dd3_one_attempt_fails_on_l2_and_j_dcin_is_drawn():
    R = _R()
    m = _M()
    S, N = R["S19"], R["N"]
    assert S["l2_t_trip"] > S["l2_tmax"] >= S["l2_t_service"], "L2's verdict is not the one the record states"
    assert N["ioc"][0] < S["l2_i_max"] < N["ioc"][2], "L2's limit is not between the breaker's thresholds"
    assert abs(S["l2_irms_need"] - N["ioc"][2] * math.sqrt(S["l2_rise_rated"] / (S["l2_tmax"] - S["t0"]))) < 1e-12
    cont = [r for r in S["r19_rows"] if r[2] is None]
    assert len(cont) == 3 and all(r[4] < 1.0 for r in cont), "R19's continuous rows do not hold on its maker's sheet"
    assert abs(S["r19_der"] - 3.0 * (170.0 - S["t_r19"]) / 100.0) < 1e-12
    with tempfile.TemporaryDirectory() as d:
        hs = _hotswap(d)
        e = os.path.join(d, "e.py")
        shutil.copy(GEN_E, e)
        for s in (hs, os.path.join(REC, "apply_gen_sch_e_entry.py")):
            assert _run([s, e, "--write"]).returncode == 0
        te = open(e, encoding="utf-8").read()
    assert '"XT60F", {"1": "DC_IN", "2": "GND_V"}, "C98734")' in te and '"XT60F": "Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical"' in te
    assert '"C274411")' not in te.split('part("J_DCIN"')[1].split("\n")[0]
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("### 19e. ")[1].split("### 19f. ")[0]
    assert "**RESULT: the attempt FAILS on L2**" in sec and "**DD-3 stays OPEN**" in sec and "E11-41" in sec
    assert [x for x in m.downstream(R) if x[0] == "E11-41"][0][2] == "prototype bench"


def t_round9_if1_the_hold_outlasts_the_start_and_its_levels_clear_every_threshold():
    R = _R()
    m = _M()
    S, H, L = R["S19"], R["H"], R["L"]
    assert S["u42_w"] > S["plim"][0], "the defect IF-1 answers is not shown on the drafts as they stood"
    assert S["hold"][0] > S["start"]["tmax"] and S["hold_margin"] > 0.03
    assert S["rise"][2] < H["floor"] and S["rise"][2] < 9.494, "the hold's release threshold is over VBAT's floor in service"
    assert S["own_on_max"] < S["fall"][0], "U42's own UVLO is not under U46's"
    assert S["ef_release"] > S["uvlor"][2] and S["ef_release"] > 0.808 and m.R9_VOL < S["uvlof"][0] and m.R9_VOL < S["ov_fall_min"]
    assert S["ef_clamp"] < 60.0 and S["ef_sink"] < 5e-3
    assert S["vz"][1] < S["vgs_max"] and S["q43_overdrive"] > 1.0 and S["rail_held_vdd"] < S["ven_fall"]
    assert S["redock_w"] < S["plim"][0] and S["kill_left"] > 0.2 and S["redock_room"] > 1.0
    assert S["static_sum"] < 0.01 * S["if1_room"], "board A's static draw while held is not small against IF-1's room"
    assert abs(S["static_sum"] - sum(x for _l, x, _c in S["static"])) < 1e-15 and len(S["static"]) >= 15
    assert abs(S["redock_room"] - (S["plim"][0] / (S["vpk"] - S["fall"][0]) - S["start"]["inrush"])) < 1e-12
    lo, hi = S["dvdt"]
    assert abs(S["vmax"] - S["start"]["tmax"] * lo) < 1e-12 and hi > lo
    row = [x for x in m.downstream(R) if x[0] == "E11-42"][0][3]
    assert "78.6 ms" in row and "(b) an undocking and redocking" in row and "(c) MAIN held" in row
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("### 19f. ")[1].split("### 19g. ")[0]
    assert "**PGD is not used (SESSION):**" in sec and "U46" in sec


def t_round9_the_record_carries_the_outputs_numbers():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    for s in ("45.88", "20.39", "7.08", "8.61", "42.48", "51.66", "18.08", "112.37", "6.367", "8.42", "78.6", "201.2", "37.9", "207.7",
              "8.476", "8.309", "7.856", "30.3 W", "37.7 mA", "4.55 A", "1.831", "0.729", "0.935", "6.004", "0.8832", "2.513",
              "6.90", "5.95", "3.921", "0.758", "101.64", "12.3 V", "0.907", "1.149", "0.948", "3.98", "0.81 A", "8.944", "4.746"):
        assert s in page and s in out, "%s is not in both the record and the output" % s


L8P3_PTC = ("v2/docs/records/l8p/apply_gen_sch_a_ptc.py", "d9c43966985172876ad1ea7339b417d31ecf10cd85824da1b983c3b1eb8b73d6")
L8P3_GEN = ("v2/docs/records/l8p/gen_netlist.py", "f3339d09604757d370ff5526f1311dbf03bd1685b22c1019d6af506ac0dd5dca")
DD7_CHECK = os.path.join(REC, "check_dd7_netlist.py")


def _l8p3(pin):
    """A file of record l8p's round 3 (fnd/l8p2 at a46597e2, merged into this branch), by sha256."""
    path = os.path.join(ROOT, pin[0])
    need(path, "record l8p's round 3 (%s)" % pin[0])
    assert _sha(path) == pin[1], "%s is not the one this record composed with" % pin[0]
    return path


def _compose10(d):
    """Board A in L4-E9's order with record l8p's PTC (round 3, the tree's) and this record's DD-7 draft before d8dec31's mainpb."""
    ptc = _l8p3(L8P3_PTC)
    dd7 = os.path.join(REC, "apply_gen_sch_a_dd7.py")
    g = os.path.join(d, "gen_sch_a.py")
    shutil.copy(GEN_A, g)
    for rec, name in _ORDER9["a"]:
        if (rec, name) == ("d8dec31", "mainpb"):
            for s in (ptc, dd7):
                r = _run([s, g, "--write"])
                assert r.returncode == 0, "%s: %s" % (s, r.stderr.decode()[-300:])
            assert _run([dd7, g, "--write"]).returncode == 3, "a second application was not refused"
        s = os.path.join(ROOT, "v2", "docs", "records", rec, "apply_gen_sch_a_%s.py" % name)
        r = _run([s, g, _NET9["a"]] if rec == "d8dec31" else [s, g, "--write"])
        assert r.returncode == 0, "%s/%s refused: %s" % (rec, name, r.stderr.decode()[-200:])
    return g


def _netlist10(g, d, tag):
    """The composed generator run to its end by record l8p's gen_netlist.py; the regenerated netlist's path."""
    out = os.path.join(d, "a-%s.net" % tag)
    r = _run([_l8p3(L8P3_GEN), g, out, "pcb-a-power"])
    assert r.returncode == 0 and b"intent written" in r.stdout, "the composed generator refused: %s" % (r.stdout + r.stderr).decode()[-400:]
    return out


def t_round10_dd7_composes_runs_to_its_end_and_reads_drawn_and_its_mutations_fail():
    """Closure credit (a) and (b) for L8P-F04 and L8P-F05: DD-7's redrawn draft is refused without record l8p's loop and on the tree,
    composes in L4-E9's order after l8p's PTC (round 3) and before d8dec31's mainpb, the generator runs to its end, and the regenerated
    netlist reads DRAWN in check_dd7_netlist.py; eight circuit mutations (two for V1's minors and the check V2's V2-B1, one for the
    battery FETs' orientation, round 12), each a defect the correction removes or the interface forbids, read FAIL; the committed netlist reads NOT DRAWN; mainpb takes the references after DD-7's highest."""
    _M()
    dd7 = os.path.join(REC, "apply_gen_sch_a_dd7.py")
    with tempfile.TemporaryDirectory() as d:
        bare = os.path.join(d, "bare.py")
        shutil.copy(GEN_A, bare)
        r = _run([dd7, bare, "--write"])
        assert r.returncode == 3 and b"apply l8p's PTC draft" in r.stderr, r.stderr.decode()[-200:]
        r = _run([dd7, GEN_A, "--write"])
        assert r.returncode == 3 and b"NOT RELEASED" in r.stderr
        g = _compose10(d)
        net = _netlist10(g, d, "drawn")
        r = _run([DD7_CHECK, net])
        assert r.returncode == 0 and b"DD-7 on board A (L4-E11 round 10): DRAWN" in r.stdout, r.stdout.decode()[-600:]
        raw = open(net, encoding="utf-8").read()
        refs = set(re.findall(r'\(comp \(ref "([^"]+)"\)', raw))
        dd7_r = [int(x[1:]) for x in refs if re.match(r"R\d+$", x) and x in ("R252", "R256", "R233", "R254", "R85", "R84", "R253", "R251", "R250", "R249", "R255")]
        assert "R%d" % (max(dd7_r) + 1) in refs and "C249" in refs, "d8dec31's mainpb did not take the next free references after DD-7's"
        text = open(g, encoding="utf-8").read()
        mutations = [
            ("U48's SENSE1 on DOCK_EN_OUT (the trigger reads the wrong conductor)", '"2": "DOCK_EN_RET", "3": "DD7_OS"', '"2": "DOCK_EN_OUT", "3": "DD7_OS"'),
            ("Q47's gate on DD7_T (the inhibit no longer gated by the powered loop)",
             'reaches the charge inhibit (1 G, 2 S, 3 D)", "SOT23", {"1": "DD7_LP"', 'reaches the charge inhibit (1 G, 2 S, 3 D)", "SOT23", {"1": "DD7_T"'),
            ("R108's foot on ground (a dead CELL+ sets the inhibit again: L8P-F05)", 'r("R108", "100k 1%", "DD7_CS", "DD7_REF"', 'r("R108", "100k 1%", "DD7_CS", "GND"'),
            ("R256 removed (the latch reads the LM5069's leak again)", 'r("R256", "4.7k 1%", "CELL+", "DD7_BL", fp="RS")', 'pass'),
            ("a 100 kOhm load on DOCK_EN_RET (the interface's 1 MOhm)", 'tp("TP1", "DD7_H")', 'r("R260", "100k", "DOCK_EN_RET", "GND", lcsc="C25803"); tp("TP1", "DD7_H")'),
            # rounds 11 and 12 (V1's minors of round 10, the check V2's V2-B1): the values the check reads
            ("R256 at round 11's 6.8k (the bleed of CELL+ inside the hold only for sources under 87 uA: V2-B1)",
             'r("R256", "4.7k 1%", "CELL+", "DD7_BL", fp="RS")', 'r("R256", "6.8k 1%", "CELL+", "DD7_BL", fp="RS")'),
            ("R84 without its pulse rating (the 71 us arm pulse on a part with no printed pulse curve)", 'r("R84", "56R 1% pulse-rated", "DD7_K"',
             'r("R84", "56R 1%", "DD7_K"'),
            # round 12: the states in which U47's RESET sinks rest on the battery FETs' body diodes pointing from CELL+ to VBAT
            ("a battery FET drawn reversed (its body diode from VBAT to CELL+: VBAT could lift CELL+ with the inhibit set)",
             '"CH_BATDRV", "CH_BATQ", "VBAT", fp="LFPAK56"', '"CH_BATDRV", "VBAT", "CH_BATQ", fp="LFPAK56"'),
        ]
        for k, (why, old, rep) in enumerate(mutations):
            assert text.count(old) == 1, why
            gm = os.path.join(d, "gen_sch_a_m%d.py" % k)
            open(gm, "w", encoding="utf-8").write(text.replace(old, rep))
            r = _run([DD7_CHECK, _netlist10(gm, d, "m%d" % k)])
            assert r.returncode == 4 and b"FAIL" in r.stdout, "%s: the check did not fail: %s" % (why, r.stdout.decode()[-400:])
    r = _run([DD7_CHECK, _NET9["a"]])
    assert r.returncode == 3 and b"NOT DRAWN" in r.stdout, "the committed netlist does not read NOT DRAWN"


def t_round10_c_prot_the_held_return_sets_the_inhibit_and_the_latch_holds_cell_dead():
    """Closure credit (c) on C-PROT: the failure reproduced on round 9's draft, then the redrawn circuit against the same cases, from the
    makers' printed figures: the held return at 7.6 and 10.6 V sets the inhibit within the interface's 1 ms, the hold outlasts 1.0 s and
    the restart, CELL+ with the breaker off at 16.8 V and 29.2 V stays dead under the latch, the service never triggers, the parts stay
    within their limits."""
    R = _R()
    m = _M()
    S, S9 = R["S20"], R["S19"]
    # the failure, as record l8p found it (round 9's readings) and as this record recomputes it
    assert S["f04"][0] < S["f04"][2] and S["f04"][1] < S["f04"][2], "L8P-F04 is not reproduced"
    assert S["f05"]["v"] > S["f05"]["dead"] and S["f05"]["v_clamp"] > S["f05"]["dead"], "L8P-F05 is not reproduced"
    held = dict(S["out_held"])
    assert held[7.6] / 2 < S9["vth"][2] and held[10.6] / 2 < S9["vth"][2], "round 9's sense would read the held loop"
    # the correction on the same cases
    assert held[7.6] > S["out_rel"][1] + 0.5 and held[10.6] > S["out_rel"][1] + 1.5, "the held loop is not read powered"
    assert S["out_rel"][1] <= S["if_out"] and S["out_ast"][0] > 0.5, "the powered reading leaves the interface's 2.0 V"
    assert S["held"] < S["ret_low"] - 0.7 and S["ret_low"] < S["if_ret_lo"] and S["ret_high"] < S["if_ret_hi"]
    assert S["t_set"] < 1e-3 and S["t_set_min"] > 4.5 * S["tau_arm"], "the set is late or the arm may not complete before it"
    assert S["hold_min"] > S["if_hold"] + 0.3 and S["hold_min"] > S["restart"] + 0.35 and S["leak_x"] > 2.5
    assert S["rest_margin"] > 0.3, "the hold may never end"
    for (vin, vc), (_v, rmin) in zip(S["latch_cell"], S["rint_min"]):
        assert vc < S["dead"] - 3.5 and rmin < 0.05 * S["r_int"], "the latch leans on the LM5069's resistor at %s V" % vin
    assert S["dead"] < S["alive"] < 9.0, "the release on CELL+ alive is not where the breaker drives it"
    S22 = R["S22"]
    assert S22["sel"]["t_hot"] < S["hold_min"], "the bleed with the sources at their hot bound outlasts the hold's least (V2-B1)"
    assert S["charge_end"] < 10e-3, "the charge through the off breaker outlasts E-14's 10 ms"
    # the service: no trigger at the bound point, none on a back-fed ramp while RT1 is in its printed 25 C band, none before the guard
    assert S["bound"][1] > 2.5 + 0.35 and S["bound_margin"] > 2.0, "the loads move l9stk's bound point or the service reads held"
    assert S["window_rt1"] > 1.5 * S9["rt1"][1] and S["ldo_ret"] > S["ret_high"] + 1.0
    assert all(g > i_[2] for (_v, g), i_ in zip(S["guard_rt1"], S["inv_rt1"])), "board A reads held before board P's guard"
    # the interface's literal box contains a closed loop: the reason board A's reading is narrower
    assert abs(S["box_rt1"] - S9["r_ret"]) < 1.0 and all(v < 4.0 for _rt, v in S["box_vin"])
    # the parts within their limits
    assert S["vgs_p"][1] < S["p_vgs"] and S9["vbat_clamp"] < S["p_vds"] and S["arm_peak"] < S["ifsm"][1] and S["arm_i2t"] < S["ifsm"][1] ** 2 * 1e-3
    assert S["n_sink"][0] < S["i_rec"] and S22["sel"]["need2"] and S["n_sink"][1] < S22["i_abs"], "U47's RESET over TI's recommended current in a state without a second fault, or over its absolute maximum"
    assert S["bleed_w"][1] < S["r1206_hot"], "R256 over its rating"
    assert S["static_frac"] < 0.01
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("## 20. Round 10")[1]
    out = open(OUT, encoding="utf-8").read()
    for s in ("0.7755", "1.981", "0.85 ms", "1.341", "0.846", "19.9", "34.5", "4.076", "4.774", "2.894", "25.8", "1.41 ms", "11.145", "0.807",
              "2.545", "3.535", "157.7", "61.3", "269", "4.08"):
        assert s in sec and s in out, "%s is not in both section 20 and the output" % s
    for f_ in ("L4E11-R10-F1", "L4E11-R10-F2", "L4E11-R10-F3", "C-PROT", "NOT\nSETTLED"):
        assert re.search(f_.replace(" ", r"\s+"), sec), f_
    row = [x for x in m.downstream(R) if x[0] == "E11-45"][0][3]
    assert "(c2)" in row and "route R1" in row and "(e) L8P-F04" in row and "(f) L8P-F05" in row and "(h) the hold timed" in row


def t_round10_t2_one_fet_of_three_may_take_nine_eighths():
    """T2, recorded: with one FET at r and two at R the one dissipates I^2 R^2 r / (R + 2 r)^2, largest at r = R / 2, 9/8 of the even
    split; with two FETs the even split is the largest; read in closed form and by a scan."""
    R = _R()
    S = R["S20"]
    p3 = lambda r, rr=1.0: rr * rr * r / (rr + 2 * r) ** 2
    p2 = lambda r, rr=1.0: rr * rr * r / (rr + r) ** 2
    scan3 = max(p3(k / 1000.0) for k in range(1, 5000))
    scan2 = max(p2(k / 1000.0) for k in range(1, 5000))
    assert abs(scan3 / p3(1.0) - 9.0 / 8.0) < 1e-4 and abs(p3(0.5) / p3(1.0) - 9.0 / 8.0) < 1e-12
    assert abs(scan2 - p2(1.0)) < 1e-6, "with two FETs the even split is not the worst case"
    assert abs(S["t2"] - 9.0 / 8.0) < 1e-12 and S["t2_tj"] > 150.0
    row = [x for x in _M().downstream(R) if x[0] == "E11-29"][0][3]
    # round 11 (section 21d) restated the row: round 10's OPEN is kept as its history, the 9/8 as its reason
    assert "recorded OPEN in round 10 (section 20i)" in row and "9/8" in row


def t_round9_dd7_the_pulse_resets_the_latch_and_the_inhibit_holds_every_later_latch():
    R = _R()
    m = _M()
    S, H, N = R["S19"], R["H"], R["N"]
    assert S["pulse"][0] > S["uvlo_fall"] * 10 and S["pulse"][0] > S["inv2_on"] * 1000 and S["pulse_vs_timer"] > 0, "the pulse does not reset the latch with margin"
    assert abs(S["grace"][1] - 0.907) < 1e-9 and abs(S["dd7_restart"] - 0.948) < 1e-9, "not record l9stk's figures at 0d72880b"
    assert abs(S["dd7_total"] - (S["pulse"][2] + S["grace"][1] + S["start"]["tmax"])) < 1e-12
    assert S["alive_off"] < S["alive_on"] < S["pack_lo"] * 0.5, "the terminal's threshold does not sit between dead and alive"
    assert S["inh_g_lo"] > S["vth"][2] + 1.0, "the loop's sense does not turn Q47 on firmly"
    assert S["q49_vgs"][0] > 2.5 and S["q49_vgs"][1] < 12.0, "Q49's gate drive is out of its window"
    assert S["ret_bound"][1] > 2.5 and S["ret_bound"][0] - S["ret_bound"][1] < 0.02, "the loop's load moves record l9stk's inverter bound too far"
    assert S["batdrv_sink"] < 5e-3
    tj = {lab: x for lab, _i, _w, x in S["e14"]}
    assert all(x < 150.0 for x in tj.values()), "E-14 at the charger's POR or R-b's largest passes 150 C"
    assert S["t0"] + 4.0 * S["vsd"] * S["rja_brk"] > 150.0, "the checker's 4 A case no longer needs the inhibit"
    # the inhibit's reach: a source holding VSYS into the breaker's least-limit resistive fault keeps CELL+ over Q48's release, so the case
    # stays open; the routes' window is R-b's largest to the latched FET's 150 C
    assert abs(S["v_fault"] - math.sqrt(S["p_src"] * S["r_fault"])) < 1e-12 and S["v_fault"] > S["alive_on"], "the open case is not shown"
    assert abs(S["r_assert"] - S["alive_off"] ** 2 / S["p_src"]) < 1e-15 and S["r_assert"] < 0.1
    assert S["capwin"][0] < S["capwin"][1] and abs(S["capwin"][1] - (150.0 - S["t0"]) / (S["vsd"] * S["rja_brk"])) < 1e-12
    sec19 = open(PAGE, encoding="utf-8").read().split("### 19h. ")[1]
    assert "**B-R2 stays OPEN for that case**" in sec19 and "| **R1 (SESSION: preferred)** |" in sec19 and "PGD reads high in that state too" in sec19
    for s in ("10.4 V", "33 mOhm", "1.405 A", "0.915 ohm"):
        assert s in sec19 and s in open(OUT, encoding="utf-8").read(), s
    row = [x for x in m.downstream(R) if x[0] == "E11-45"][0][3]
    assert "(c) E-14 extended" in row and "at most 1 mA" in row
    page = open(PAGE, encoding="utf-8").read()
    sec = page.split("### 19h. ")[1]
    assert "**No firmware.**" in sec and "**the signal**" in sec and "**the threshold**" in sec and "**where it acts**" in sec
    for s in ("78.6", "1.149", "0.948", "3.829", "7.735", "4.07", "9.86", "3.83 mA", "2.939", "142.2", "89.7", "5.05", "1.98", "154.6", "C-1c"):
        assert s in sec and s in open(OUT, encoding="utf-8").read(), s


# ---- round 11 (section 21, task T2): E-1 on C-PROT rev 1 with the worst sharing, and E11-37

def _hottest(rs, zs, zm):
    """The hottest of three paralleled FETs' junction rise per unit I^2 for RDS(on) values rs, self impedance zs and mutual zm (a
    number for equal coupling, or a 3x3 table of the mutual impedances): each FET takes the current share of its conductance."""
    g = [1.0 / r for r in rs]
    gs = sum(g)
    pw = [gi / gs ** 2 for gi in g]                     # I^2 g_k / G^2 = I_k^2 r_k
    zmt = zm if isinstance(zm, (list, tuple)) else [[zm] * 3 for _ in range(3)]
    return max(pw[k] * zs + sum(pw[j] * zmt[k][j] for j in range(3) if j != k) for k in range(3))


_M_GRID = (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.4)


def _e1_worst_tj(R, bar, ra=None):
    """E-1 on C-PROT rev 1, recomputed apart from the script: the hottest junction held at the breaker's 23.93 A from L4-E12's 76.25 C
    with the band and R17 in place, each FET's installed (Zself + 2 Zmut) at bar, over every split of the three RDS(on) values under the
    allowance (a 24-step grid on each, plus the closed form's worst point) and the coupling ratios of _M_GRID. ra is the RDS(on) the FETs
    actually reach (the allowance at the charger's printed least drive unless a mutation passes another)."""
    m = _M()
    S9 = R["S19"]
    ra = m.F16_RA if ra is None else ra
    i_ = S9["i"]
    base = S9["t0"] + S9["band"] + S9["r17_allow"] * S9["pr17"]
    worst = (None, -1.0)
    for mm in _M_GRID:
        zs = bar / (1.0 + 2.0 * mm)
        zm = mm * zs
        ks = sorted(set([k / 24.0 for k in range(1, 25)] + [1.0 / max(1.0, 2.0 - 4.0 * mm)]))
        for a in ks:
            for b in ks:
                for c in ks:
                    tj = base + i_ ** 2 * ra * _hottest((a, b, c), zs, zm) * 1.0
                    if tj > worst[1]:
                        worst = ((mm, a, b, c), tj)
    return worst


def t_round11_e1_holds_on_c_prot_over_every_split_and_its_mutations_fail():
    """T2's correction against the same failure case (C-PROT rev 1, record l9stk's E-1): with the installed bar 40.78 K/W the hottest
    junction stays at most 150 C held at 23.93 A from 76.25 C for every split of the three RDS(on) values under the allowance, at the
    charger's printed least gate drive (SLUSE65A's VBATDRV_ON minimum); the even split's 45.88 K/W, a bar 1 % looser, the script's split
    replaced by the even one, and the allowance read at a 10 V drive each FAIL; unequal coupling is bounded by the largest impedance."""
    R = _R()
    m = _M()
    S, S9, H = R["S21"], R["S19"], R["H"]
    # the drive: the allowance is section 15c's figure at TI's printed least VBATDRV_ON, not at the typical 10 V
    assert S["vg"] == H["drv"][0] == 8.5 and abs(S["ra"] - m.F16_RA) < 1e-15
    assert S["ra_10v"] < S["ra"] / 1.3, "the 10 V figure is not the looser one"
    # the closed form against a scan, and the failure on round 10's bar (the defect reproduced)
    for mm in _M_GRID:
        f_, x_ = m.worst_share(mm)
        scan = max(m.split_share(1.0 + k / 400.0, mm) for k in range(0, 1201))
        assert abs(scan - max(f_, 1.0)) < 2e-5 and (mm >= 0.25 or abs(x_ - (2.0 - 4.0 * mm)) < 1e-12), mm
    (pt, tj_old) = _e1_worst_tj(R, S["bar_old"])
    assert tj_old > 157.0 and abs(tj_old - S["tj_old_worst"]) < 0.05, "the even split's bar does not fail at its case (%.2f C)" % tj_old
    # the correction on the same case
    (pt, tj_new) = _e1_worst_tj(R, S["bar_new"])
    assert tj_new <= 150.0 + 1e-9, "E-1 fails at 40.78 K/W: %.3f C at %s" % (tj_new, pt)
    assert tj_new > 149.9, "the bar is looser than the case needs (not the worst split's)"
    assert abs(S["bar_new"] - S["bar_old"] / 1.125) < 1e-12 and "%.2f" % S["bar_new"] == "40.78"
    # mutations: each FAILS the same acceptance
    assert _e1_worst_tj(R, S["bar_new"] * 1.01)[1] > 150.0, "a bar 1 % looser still passes: the acceptance does not bind"
    assert _e1_worst_tj(R, S["bar_new"] * S["ra"] / S["ra_10v"])[1] > 150.0, "the bar sized at a 10 V drive passes at the least drive"
    keep = m.worst_share
    try:
        m.worst_share = lambda mm: (1.0, 1.0)                     # the split read as even (round 10's defect)
        Sm = m.fix21_round(R, None)
    finally:
        m.worst_share = keep
    assert abs(Sm["bar_new"] - S["bar_old"]) < 1e-12 and _e1_worst_tj(R, Sm["bar_new"])[1] > 150.0, "the even split's mutation passes"
    # unequal coupling (the middle FET has two neighbours): the hottest rise over every split stays under the bound taken with the
    # largest mutual impedance, as the record's block E11-29 states
    zs = 1.0
    for z12, z13, z23 in ((0.2, 0.05, 0.2), (0.1, 0.0, 0.1), (0.24, 0.12, 0.24), (0.3, 0.1, 0.3)):
        zt = [[0, z12, z13], [z12, 0, z23], [z13, z23, 0]]
        zmax = max(z12, z13, z23)
        ks = [k / 24.0 for k in range(1, 25)]
        asym = max(_hottest((a, b, c), zs, zt) for a in ks for b in ks for c in ks)
        sym = max(m.worst_share(zmax / zs)[0], 1.0) * (zs + 2 * zmax) / 9.0
        assert asym <= sym + 1e-12, (z12, z13, z23)
    # the record and the drafts carry it
    row = [x for x in m.downstream(R) if x[0] == "E11-29"][0][3]
    assert ("%.2f K/W" % S["bar_new"]) in row and "ANY split" in row and "the largest of each" in row and "CONDITIONAL" in row
    with tempfile.TemporaryDirectory() as d:
        a = os.path.join(d, "gen_sch_a.py")
        shutil.copy(GEN_A, a)
        _apply("apply_gen_sch_a_charger.py", a)
        txt = open(a, encoding="utf-8").read()
    assert "(Zself + 2 Zmut) at most\n# 40.78 K/W" in txt and "for ANY split of the RDS(on) spread" in txt
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    b29 = page.split("#### Block E11-29")[1].split("#### Block E11-30")[0]
    assert "**40.78 K/W**" in b29 and "for any split of the RDS(on) spread" in b29.replace("\n  ", " ")
    s20i = out.split("   20i. ")[1].split("   20j. ")[0]
    assert "Zself / 4" in s20i and "Zself / 4" in page.split("### 20i. ")[1].split("### 20j. ")[0]
    sec = page.split("## 21. Round 11")[1]
    o21 = out.split("21. ROUND 11")[1]
    for v in ("157.7", "40.78", "1.125", "1.5129", "32.85", "20.39", "4.72", "5.74", "1.0045", "0.9643", "15 mOhm", "8.5 V", "1.0651",
              "42.62", "44.04", "45.06", "45.68", "4.47 mA", "6.39 mA", "0.597", "1.228", "0.112", "87.4 uA", "WITHDRAWN", "14.6 W", "11.1 %"):
        assert v in sec and v in o21, "%s is not in both section 21 and out 21" % v
    assert "C-PROT rev 1" in sec and "C-PROT rev 1" in o21


def t_round11_e11_37_stays_open_with_q_ti_17_e_and_f_and_the_fallback_rests_on_a_typical_figure():
    """E11-37 is not closed by this round: three FETs stay over TI's 5 nF on typical figures; the fallback pair is under it only at the
    sheet's -15 V and on a typical figure, so it is CONDITIONAL and Q-TI-17 (e) names it; (iii) has no printed basis (SLUSE65A names
    no buffer on BATDRV) and Q-TI-17 (f) asks; the questions are drafted, not sent."""
    R = _R()
    m = _M()
    S, S9, H, L = R["S21"], R["S19"], R["H"], R["L"]
    assert S9["ciss_ratio"][0] > 1.0, "the three are not over TI's 5 nF"
    under = [lab for lab, _c, _c2, ok in S["two"] if ok]
    assert under == ["BUK6Y10-30P (Nexperia)"], under
    assert S["pair_ciss"][0] < H["bf_ciss"] < S["pair_ciss"][1], "the pair's near-0 V typical is not shown over 5 nF"
    assert abs(S["pair_ciss"][0] - 2 * L["ciss_t"]) < 1e-15 and S["buffer_mentions"] == 0
    assert abs(S["pair_vs_three"] - S["pair_bar"] / S["bar_new"]) < 1e-12 and S["pair_vs_three"] < 0.55
    o21 = open(OUT, encoding="utf-8").read().split("21. ROUND 11")[1]
    assert "E11-37 STAYS OPEN" in o21 and "E11-37 OPEN" in o21 and "on a TYPICAL figure" in o21 and "NOT SENT" in o21
    row = [x for x in m.downstream(R) if x[0] == "E11-37"][0][3]
    assert "Q-TI-17 (e) and (f)" in row and "round 11's (ii)" in row and "a result with the pair does not transfer" in row
    ti = open(os.path.join(REC, "clarification", "TI-QUESTIONS.md"), encoding="utf-8").read()
    r11 = ti.split("## Round 11")[1]
    assert "**Q-TI-17 (e)" in r11 and "**Q-TI-17 (f)" in r11 and "Drafted, not sent." in r11
    for v in ("4.72 nF", "5.74 nF", "2.36 nF", "2.87 nF", "192 nC"):
        assert v in r11, v


# ---- round 12 (section 22): the independent check V2's V2-B1 (the bleed of CELL+ with the sources into it) and its minors

def _bleed12(r, c, v0, vdead, vinf):
    """The test's own bleed: CELL+ from v0 under vdead through r into c, falling towards vinf; None when it never gets there."""
    return None if vinf >= vdead else r * c * math.log((v0 - vinf) / (vdead - vinf))


def t_round12_v2b1_the_bleed_counts_the_sources_and_the_selected_correction_meets_both_needs():
    """V2-B1 on C-PROT rev 1: round 11 gave the bleed with no source beside a static limit. Here the sources at their hot bound come from
    the makers' printed rows (Nexperia's 125 C row, TI's one 25 C row with record l8p's ASSUMED doubling, the LM5069's 1 MOhm); the bleed
    is recomputed apart from the script; round 11's 6.8 kOhm fails it where the no-source figure passed; the round refuses a no-source
    bleed; the selected 4.7 kOhm holds it and keeps U47's RESET within TI's recommended current in every state without a second fault."""
    R = _R()
    m = _M()
    S, S20, S9 = R["S22"], R["S20"], R["S19"]
    assert abs(S["bat"][0] - 3e-6) < 1e-12 and abs(S["bat"][1] - 30e-6) < 1e-12 and abs(S["brk25"] - 2e-6) < 1e-12, "the printed IDSS rows"
    hot = 16.8 / 1e6 + 30e-6 + 2e-6 * 2 ** ((101.0 - 25.0) / 10.0)
    assert abs(S["src"]["hot"] - hot) < 1e-10 and abs(hot - 434.8e-6) < 0.05e-6
    hold, vs, c = S20["hold_min"], S20["vs_max"], S20["c_cell"] * 1.2
    sel, a, cc = S["sel"], S["opts"]["a"], S["opts"]["c"]
    assert sel["key"] == m.R12_SELECT == "b" and sel["v"]["rbl"] == m.R10_RBL == 4.7e3 and a["v"]["rbl"] == 6.8e3
    # the selected correction, on the same failure case
    r = sel["v"]["rbl"] * 1.01
    t = _bleed12(r, c, vs, sel["v"]["dead"], sel["v"]["v_ref"] + hot * r)
    assert abs(t - sel["t_hot"]) < 1e-9 and t < hold - 0.1, "the bleed at the hot bound is not 0.1 s inside the hold's least: %.3f s" % t
    assert abs(_bleed12(r, c, vs, sel["v"]["dead"], sel["v"]["v_ref"] + sel["lim"] * r) - hold) < 1e-6, "the coupled limit is not where the bleed takes the hold"
    assert _bleed12(r, c, vs, sel["v"]["dead"], sel["v"]["v_ref"] + 1.05 * sel["lim"] * r) > hold, "sources over the coupled limit still pass"
    assert _bleed12(r, c * 1.15, vs, sel["v"]["dead"], sel["v"]["v_ref"] + hot * r) > hold, "a capacitance 15 % over the assumed most still passes"
    assert hot < sel["lim"] < sel["v"]["isrc_max"], "the coupled limit is not between the hot bound and the static limit"
    # round 11's 6.8 kOhm: the failure, and the no-source bleed that hid it
    ra = a["v"]["rbl"] * 1.01
    ta = _bleed12(ra, c, vs, a["v"]["dead"], a["v"]["v_ref"] + hot * ra)
    assert abs(ta - a["t_hot"]) < 1e-9 and ta > hold and not a["need1"], "6.8 kOhm does not fail at the hot bound"
    assert a["t_air"] > hold and a["lim"] < S["src"]["air"] < S["src"]["hot"], "6.8 kOhm does not fail at the air's sources"
    t0 = _bleed12(ra, c, vs, a["v"]["dead"], 0.0)
    assert abs(t0 - a["v"]["bleed_zero"]) < 1e-9 and t0 < hold, "the no-source figure is not the one that passed at 6.8 kOhm"
    keep = m.bleed_time
    try:
        m.bleed_time = lambda r_, c_, v0_, vd_, vinf_: r_ * c_ * math.log(v0_ / vd_)        # the no-source bleed of rounds 10 and 11
        try:
            m.fix22_round(R, None)
            raise AssertionError("the round accepts a bleed that does not count the sources")
        except SystemExit as e:
            assert e.code == 4
    finally:
        m.bleed_time = keep
    # V2's figures, reproduced by the script and here for three of them
    for lab, mine, theirs, _unit in S["rep"]:
        assert abs(mine - theirs) <= 0.012 * theirs, lab
    assert abs(_bleed12(ra, c, vs, a["v"]["dead"], a["v"]["v_ref"] + 19.8e-6 * ra) - 1.257) < 0.002
    assert abs(_bleed12(ra, c, vs, a["v"]["dead"], a["v"]["v_ref"] + 404.8e-6 * ra) - 2.06) < 0.01
    assert abs(_bleed12(r, c, vs, sel["v"]["dead"], sel["v"]["v_ref"] + 404.8e-6 * r) - 1.18) < 0.005
    # need 2: the sink by state, recomputed (R256 at -1 %; R82 with R83 300 kOhm from VBAT, R254 and R255 1 MOhm from 12.7 V, R107 with R108)
    sink = lambda vc, vb, rr: vc / (rr * 0.99) + vb / 300e3 + 2 * 12.7 / 1e6 + vc / 564e3
    vst = S["v_states"]
    for k_, vc, vb in (("set", vs, vs), ("run", S9["vpk"], vs), ("ovp", vst["sysovp"], vst["sysovp"]), ("clamp", S9["vbat_clamp"], S9["vbat_clamp"])):
        assert abs(sink(vc, vb, 4.7e3) - sel["sink"][k_]) < 1e-9 and abs(sink(vc, vb, 6.8e3) - a["sink"][k_]) < 1e-9, k_
    assert max(sel["sink"]["set"], sel["sink"]["run"], sel["sink"]["ovp"]) < S20["i_rec"] - 0.5e-3 and sel["need2"] and not sel["need2_all"]
    assert S20["i_rec"] < sel["sink"]["clamp"] < S["i_abs"] and S["i_abs"] == 10e-3 and S20["i_rec"] == 5e-3
    assert sel["v_5ma"] > vst["sysovp"] + 2.5 and sel["v_5ma"] > vst["pack_diode"] + 4.0 and sel["t_over"] < 0.2
    assert a["need2_all"] and a["sink"]["clamp"] < S20["i_rec"], "6.8 kOhm's side of the trade is not shown"
    # (c): it holds need 1 too, by moving the hold's readers; R85 alone does not
    assert cc["need1"] and cc["v"]["hold_max"] > 2 * S20["hold_max"] and cc["v"]["arm_frac"] < 0.95 and not S["opts"]["c2"]["need1"]
    # the selection: the widest allowance for the unprinted leakage, and no correction holds without it
    assert sel["pair_allow"] > cc["pair_allow"] > S["brk"][1] > a["pair_allow"]
    assert 101.0 < sel["pair_t"] < 106.0, "the margin on the assumed doubling is misstated"
    # the record carries it: the output, the page, the row, the draft
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    o22, p22 = out.split("22. ROUND 12")[1], page.split("## 22. Round 12")[1]
    for v_ in ("434.8", "520.7", "87.4", "1.218", "2.189", "0.123", "473.9", "103.9", "3.85 mA", "3.72 mA", "4.32 mA", "6.45 mA", "22.51",
               "0.846", "0.597", "12.8 s", "451.2", "C-PROT rev 1", "E-14c", "9.63", "2.312", "1.248", "1.381", "0.934", "0.396", "0.155"):
        assert v_ in o22 and v_ in p22, "%s is not in both section 22 and out 22" % v_
    assert "SELECTED: (b)" in o22 and "OPEN" in o22.split("22g. ")[1].split("22h. ")[0] and "ASSUMED" in o22
    o20e = out.split("   20e. ")[1].split("   20f. ")[0]
    assert "with the sources at their hot bound" in o20e and "under the hold's least" not in o20e
    row = [x for x in m.downstream(R) if x[0] == "E11-45"][0][3]
    assert "(f2, round 12" in row and "at most 521 uA" in row and "0.1 s longer than (f2)'s bleed" in row
    dd7 = open(os.path.join(REC, "apply_gen_sch_a_dd7.py"), encoding="utf-8").read()
    assert 'r("R256", "4.7k 1%", "CELL+", "DD7_BL", fp="RS")' in dd7 and '"6.8k 1%"' not in dd7


def t_round12_the_minors_v2_m1_to_m5_are_carried():
    """V2-m1: Vishay's printed Ciss maxima are the figures judged; V2-m2: Nexperia's hot IDSS row is quoted where the record said 'not
    printed'; V2-m3: the dd7 draft's comment carries the script's sink figures; V2-m4: V1's two unowned minors are named with an owner and
    a next action, the hysteresis reading's figures reproduced; V2-m5: E11-29's coupon reads the PTC's site with one FET heated alone."""
    R = _R()
    m = _M()
    S, S21, S20 = R["S22"], R["S21"], R["S20"]
    two = {lab: (c_, ok) for lab, c_, _c2, ok in S21["two"]}
    assert abs(two["SQJ403EP (Vishay)"][0] - 4500e-12) < 1e-15 and abs(two["SQJ407EP (Vishay)"][0] - 10700e-12) < 1e-15, "Vishay's maxima are not the figures judged"
    assert S21["two_note"]["SQJ403EP (Vishay)"] == (3400e-12, "maximum") and S21["two_note"]["SQJ407EP (Vishay)"] == (8200e-12, "maximum")
    assert [lab for lab, (_c, ok) in two.items() if ok] == ["BUK6Y10-30P (Nexperia)"], "the verdict moved"
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    o21 = out.split("21. ROUND 11")[1].split("22. ROUND 12")[0]
    assert "4.5 nF maximum (3.4 nF typical), two 9 nF" in o21 and "10.7 nF maximum (8.2 nF typical), two 21.4 nF" in o21
    p21 = page.split("## 21. Round 11")[1].split("## 22. Round 12")[0]
    assert "4.5 nF maximum" in p21 and "10.7 nF maximum" in p21 and "except SQJ403EP's and SQJ407EP's printed maxima" not in p21
    for text_ in (out.split("   20e. ")[1].split("   20f. ")[0], page.split("### 20e. ")[1].split("### 20f. ")[0]):
        assert "10 uA at Tj 125 C" in " ".join(text_.split()) and "hot off leakage (not printed)" not in text_, "Nexperia's hot row is not quoted in 20e"
    dd7 = open(os.path.join(REC, "apply_gen_sch_a_dd7.py"), encoding="utf-8").read()
    sel = S["sel"]
    for k_, lab in (("set", "%s mA at the set"), ("ovp", "%s mA with CELL+ at SYSOVP"), ("clamp", "%s mA only with CELL+ at VBAT")):
        assert (lab % m.fmt(sel["sink"][k_] * 1e3, 2)) in dd7, "the dd7 draft's comment does not carry %s" % k_
    assert "4.4 mA at the clamp" not in dd7
    h = S["hys_alt"]
    assert abs(h["ret_low"] - 0.7643) < 0.0006 and abs(h["out_hi"] - 2.008) < 0.001 and abs(h["window"] - 25.1e3) < 60.0
    o22h = out.split("   22h. ")[1].split("   22i. ")[0]
    assert o22h.count("OWNER") == 2 and o22h.count("NEXT") == 2 and "Q-TI-19" in o22h and "CONOPS" in o22h
    p22h = page.split("### 22h. ")[1].split("### 22i. ")[0]
    assert "**Owner:**" in p22h and p22h.count("**Next action:**") == 2 and "Q-TI-19" in p22h and "CONOPS" in p22h
    ti = open(os.path.join(REC, "clarification", "TI-QUESTIONS.md"), encoding="utf-8").read()
    assert "**Q-TI-19" in ti.split("## Round 12")[1] and "Drafted, not sent." in ti.split("## Round 12")[1]
    row = [x for x in m.downstream(R) if x[0] == "E11-29"][0][3]
    assert "the PTC's site" in row and "one FET heated alone" in row and "V2-m5" in row
    b29 = page.split("#### Block E11-29")[1].split("#### Block E11-30")[0]
    assert "the PTC's site" in " ".join(b29.split()) and "1.513 W" in b29
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    assert "V2's findings answered" in readme and "V2-B1" in readme and "V2-m9" in readme
    # V2-m9: L4-E9's change-list order as the candidate lists it. Where record l8r2's packrtn, slotlm and fb01 are in the tree (the
    # candidate's line) the list's order composes, the generator runs to its end, the netlist reads DRAWN and three mutations FAIL;
    # where they are not (this branch's own tree) the script says so and the tests above compose main's order
    lo = os.path.join(REC, "compose_in_list_order.py")
    have = all(os.path.isfile(os.path.join(ROOT, "v2", "docs", "records", "l8r2", "apply_gen_sch_a_%s.py" % n_)) for n_ in ("packrtn", "slotlm", "fb01"))
    with tempfile.TemporaryDirectory() as d:
        r = _run([lo, ROOT, d])
    if have:
        assert r.returncode == 0 and b"intent written; DD-7 on board A (L4-E11 round 10): DRAWN" in r.stdout and r.stdout.count(b": FAIL") == 3, \
            "board A does not compose in L4-E9's list order: %s" % r.stdout.decode()[-400:]
    else:
        assert r.returncode == 1 and b"l8r2/packrtn is not in this tree" in r.stdout, r.stdout.decode()[-300:]
        assert "NOT in this branch's tree" in open(OUT, encoding="utf-8").read().split("   22h. ")[1]


# ---- round 13 (section 23): the owner's supplier-delta review, DELTA-02: E11-29's method on three body diodes in parallel

TP29 = os.path.join(ROOT, "v2", "docs", "test-procedures", "TP-E11-29.md")


def t_round13_delta02_the_body_diode_method_is_refused_and_the_selected_method_addresses_one_device():
    """DELTA-02: Q39, Q40 and Q42 have common gate, drain and source nets in the draft (read by ast) and in the regenerated netlist (read
    by the S-expression reader), so a body-diode step addresses no single device; the rule says so for the old method on the drafted nets
    and with the gates apart; the selected method (B) addresses one device where the gates are apart and not on board A as drafted; the
    round refuses to select the old method or (C); E11-29's row is the selected method's text and no longer states the body-diode one."""
    R = _R()
    m = _M()
    S = R["S23"]
    f_ = S["fets"]
    assert f_["refs"] == ["Q39", "Q40", "Q42"] and (f_["G"], f_["D"], f_["S"]) == ("CH_BATDRV", "CH_BATQ", "VBAT") and "P-FET" in f_["value"]
    assert f_["sha"] == _sha(os.path.join(REC, "apply_gen_sch_a_charger.py")), "the topology is not read from the draft's present bytes"
    # the same topology in the regenerated netlist of board A, composed as round 10's test composes it
    spec = importlib.util.spec_from_file_location("check_dd7_netlist_under_test", DD7_CHECK)
    chk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chk)
    with tempfile.TemporaryDirectory() as d:
        g = _compose10(d)
        _comps, pins, _on = chk.read_netlist(open(_netlist10(g, d, "r13"), "rb").read())
    term = {"S": ("1", "2", "3"), "G": ("4",), "D": ("5",)}
    nets = {t: {tuple(pins[q][x] for x in px) for q in ("Q39", "Q40", "Q42")} for t, px in term.items()}
    private = tuple(t for t in ("S", "G", "D") if len(nets[t]) == 3)
    assert private == () == S["board_private"], "a battery FET has a terminal on a net of its own: %s" % nets
    assert nets["S"] == {("VBAT",) * 3} and nets["G"] == {("CH_BATDRV",)} and nets["D"] == {("CH_BATQ",)}
    # the rule on the old method: not per-device on the drafted nets, nor with the gates apart (a diode has no selecting terminal)
    old, a_, b_, c_ = (m.R13_METHODS[k] for k in ("old", "A", "B", "C"))
    for step in ("heat", "sense"):
        assert not m.per_device(old[step], private)[0] and not m.per_device(old[step], ("G",))[0], "the body-diode %s step reads as per-device" % step
        assert not m.per_device(c_[step], c_["private"])[0] and c_["private"] == ()
        assert m.per_device(a_[step], a_["private"])[0] and "S" in a_["private"]
        assert m.per_device(b_[step], b_["private"])[0] and b_["private"] == ("G",), "method (B) does not address one device with the gates apart"
        assert not m.per_device(b_[step], private)[0], "method (B) reads as per-device on board A as drafted (its gates share one net)"
        # mutations of the selected method's statement: current entering at the drain (the unselected body diodes conduct), no selecting gate
        assert not m.per_device(dict(b_[step], direction="drain to source"), ("G",))[0]
        assert not m.per_device(dict(b_[step], select=None), ("G",))[0]
        assert not m.per_device(dict(b_[step], path="body diode"), ("G",))[0]
    assert m.R13_SELECT == "B" and S["judge"]["B"]["heat"][0] and S["judge"]["B"]["sense"][0] and not S["judge"]["B"]["heat_board"][0]
    # the round refuses a selected method that heats or senses 'alone' on common nets
    keep = m.R13_SELECT
    for bad in ("old", "C"):
        try:
            m.R13_SELECT = bad
            try:
                m.fix23_round(R, None)
                raise AssertionError("the round accepts %r as the selected method" % bad)
            except SystemExit as e:
                assert e.code == 4
        finally:
            m.R13_SELECT = keep
    # the maker's sheet: the pinning, the diode rows, the threshold row
    assert S["pin_p"] == 2 and S["vsd"] == (80.0, 0.7, 1.2) and S["is"] == 80.0 and S["vth"] == (250e-6, 1.5, 2.0, 3.0) and S["id100"] == 57.0
    # E11-29's row and block
    row = [x for x in m.downstream(R) if x[0] == "E11-29"][0][3]
    assert m.e11_29_method(R) in row and "by the body diode's VSD method" not in row and "its three gates can be driven apart" in row
    assert "WITHDRAWN" in m.e11_29_method(R) and "selected by its gate" in m.e11_29_method(R) and "threshold voltage" in m.e11_29_method(R)
    page = open(PAGE, encoding="utf-8").read()
    b29 = " ".join(page.split("#### Block E11-29")[1].split("#### Block E11-30")[0].split())
    assert "the three gate traces brought out apart" in b29 and "is **withdrawn**" in b29 and "selected by its gate" in b29
    assert "each FET heated through its body diode at the held limit" not in b29 and "junction read by VSD at a small sense current" not in b29


def t_round13_method_b_powers_currents_and_budget_reproduce():
    """The figures E11-29 now carries, in closed form: the worst split's powers, method (B)'s heating currents under the part's ID, the
    ripple bound, the budget's six terms and the reading that passes the 40.78 K/W bar; (A)'s budget; (C)'s bracket wider than the gap
    between the bar's two forms."""
    R = _R()
    m = _M()
    S, S9, S21, L = R["S23"], R["S19"], R["S21"], R["L"]
    i_, ra = S9["i"], m.F16_RA
    assert abs(S["p"]["even"] - i_ ** 2 * ra / 9) < 1e-12 and abs(S["p"]["hot"] - i_ ** 2 * ra / 8) < 1e-12 and abs(S["p"]["other"] - i_ ** 2 * ra / 16) < 1e-12
    assert abs(S["p"]["hot"] + 2 * S["p"]["other"] - S["slot_w"][1]) < 1e-12 and abs(3 * S["p"]["even"] - S["slot_w"][0]) < 1e-12
    for got, p_ in ((S["i_single"], S["p"]["hot"]), (S["i_td"][0], S["slot_w"][0]), (S["i_td"][1], S["slot_w"][1])):
        assert abs(got[0] - math.sqrt(p_ / ra)) < 1e-12 and abs(got[1] - math.sqrt(p_ / 8e-3)) < 1e-12 and got[1] < S["id100"]
    assert abs(S["ripple"][0] - S["slot_w"][0] * L["z"][2.44e-4]) < 1e-12 and m.R13_B["slot"] == 2.44e-4
    rise = S21["bar_new"] * S["p"]["even"]
    assert abs(rise - S["rise_bar"]) < 1e-12 and abs(S["rise_total"] - (150.0 - S9["t0"])) < 1e-12
    u_b = math.sqrt(0.02 ** 2 + 0.01 ** 2 + (1.0 / rise) ** 2 + (0.5 / rise) ** 2 + (0.3 / rise) ** 2 + (S["ripple"][0] / 2 / rise) ** 2)
    u_a = math.sqrt(0.02 ** 2 + 0.01 ** 2 + (1.0 / rise) ** 2)
    assert abs(S["u"]["B"] - u_b) < 1e-12 and abs(S["u"]["A"] - u_a) < 1e-12 and len(S["terms"]["B"]) == 6
    assert abs(S["pass"]["B"] - S21["bar_new"] / (1 + u_b)) < 1e-12 and "%.2f" % S["pass"]["B"] == "39.51" and "%.2f" % (u_b * 100) == "3.22"
    assert abs(S["pass_even"] - S21["bar_old"] / (1 + u_b)) < 1e-12 and abs(S["pass_rise"] - S["rise_total"] / (1 + u_b)) < 1e-12
    assert S["u"]["B"] < S["bar_gap"] / 2 < S["c_frac"], "(B) does not resolve the bar's two forms, or (C) does"
    assert abs(S["c_bracket"] - 8.617333e-5 * 423.15 * math.log(3.0) / 2e-3) < 1e-9
    assert abs(S["leak_frac"] - 2 * 10e-6 / 1e-3) < 1e-12 and S["sense_k"] < 0.2
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    o23, p23 = out.split("23. ROUND 13")[1], page.split("## 23. Round 13")[1]
    for v_ in ("39.51", "3.22 %", "54.84", "40.78", "45.88", "44.45", "71.45", "73.75", "1.513", "0.756", "8.46", "13.75", "13.82", "22.46",
               "11.96", "19.45", "1.04 K", "0.2589", "2.89 %", "39.64", "20 K", "11.1 %", "DELTA-02", "C-PROT rev 1", "NOT EXECUTABLE"):
        assert v_ in o23 and v_ in p23, "%s is not in both section 23 and out 23" % v_
    assert "SELECTED: (B)" in o23 and "no coefficient is printed" in o23 and "No temperature coefficient is printed" in p23


def t_round13_section_20c_stands_on_the_ptcs_printed_points():
    """Record l9stk's round 4 corrected its reading of Murata's sheet: 47 kOhm is not a point of the PRF15BB103. 20c and 20f no longer
    use it as a bound; on the printed points the first inverter is not defined at 100 kOhm and 10.6 V, and a tripped PTC is read held
    with the loop powered (a guard trip sets DD-7's inhibit); the selected switch's reading on DD-7 is named as owed."""
    R = _R()
    S, S20, S9 = R["S23"], R["S20"], R["S19"]
    by = {(r_["rt"], r_["vin"]): r_ for r_ in S["ptc_rows"]}
    assert len(by) == 8 and by[(100e3, 10.6)]["inv"] == "not defined" and by[(100e3, 16.8)]["inv"] == "on"
    assert all(by[(rt, v)]["a"] == "closed" and by[(rt, v)]["inv"] == "on" for rt in (5e3, 15e3) for v in (10.6, 16.8))
    assert all(by[(4.7e6, v)]["a"] == "held" and by[(4.7e6, v)]["inv"] == "off" and by[(4.7e6, v)]["powered"] for v in (10.6, 16.8))
    assert abs(by[(100e3, 10.6)]["ret"] - (10.6 * 22e3 / 132e3)) < 0.06, "the return at 100 kOhm is not the divider's reading less the loads"
    assert S["switch"] == (127.8, 132.2) and all(o > S20["out_rel"][1] and r_ > S20["ret_high"] for _v, o, r_ in S["sw_rows"])
    mine = (S["inv_loaded"][0][1], S["inv_loaded"][1][1], S["inv_loaded"][0][2], S["inv_loaded"][1][2])
    assert all(abs(a_ / 1e3 - b_) <= 0.10 * b_ for a_, b_ in zip(mine, S["l9_inv"])) and S["l9_inv"] == (58.4, 110.9, 203.4, 341.2)
    assert abs(S9["rt1"][2] - 47e3) < 1e-6 and abs(S["withdrawn"][1] - S20["bound"][1]) < 1e-12
    out = open(OUT, encoding="utf-8").read()
    page = open(PAGE, encoding="utf-8").read()
    o20c = out.split("   20c. ")[1].split("   20d. ")[0]
    o20f = out.split("   20f. ")[1].split("   20g. ")[0]
    assert "WITHDRAWN as a bound by round 13" in o20c and "the bound point (l9stk" not in o20c
    assert "which bounds nothing" in o20f and "read closed with" not in o20f
    p20 = " ".join(page.split("## 20. Round 10")[1].split("## 21. Round 11")[0].split())
    assert "withdrawn as a bound by round 13" in p20 and "which bounds nothing" in p20 and "**The bound point** (record l9stk" not in p20
    o23g = out.split("   23g. ")[1].split("   23h. ")[0]
    assert "WHAT NO LONGER STANDS" in o23g and "OWED READING" in o23g and "NOT DRAFTED" in o23g and "L8P-F07" in o23g
    for v_ in ("1.714", "2.737", "59.2", "112.3", "190.2", "319.5", "4.532", "127.8", "132.2"):
        assert v_ in o23g and v_ in page.split("### 23g. ")[1], v_


def t_round13_the_procedure_quotes_this_record_and_stays_not_executable():
    """TP-E11-29 is rewritten on method (B) in this round: every quote it makes of THIS record is the record's text (the procedures'
    own verifier), it carries the proposal mark and the NOT EXECUTABLE status with what must happen first, and it no longer instructs a
    body-diode heating or a VSD reading. Its quotes of L4-E9's cells are that record's, on the line it is integrated on."""
    need(TP29, "the procedure TP-E11-29")
    tpdir = os.path.dirname(TP29)
    spec = importlib.util.spec_from_file_location("tp_check_for_l4e11", os.path.join(tpdir, "tp_check.py"))
    tp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tp)
    text = open(TP29, encoding="utf-8").read()
    _tq, n_table, n_text, fails = tp.verify_quotes(tp.Sources(ROOT), "v2/docs/test-procedures/TP-E11-29.md", text)
    mine = [f_ for f_ in fails if "records/l4e11/" in f_ or "well-formed" in f_]
    assert not mine, "the procedure misquotes this record: %s" % mine
    quotes = [(dict(tp.ATTR_RX.findall(a)), b) for a, b in tp.Q_RX.findall(text)]
    own = [q for q, _b in quotes if q.get("src") == "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md"]
    assert len(own) >= 10 and any(q.get("row") == "E11-29" and q.get("col") == "Acceptance" for q in own), "the row's acceptance is not quoted"
    assert tp.MARK in text and "**NOT EXECUTABLE.**" in text and "the independent check" in text and "a supplier's written agreement" in text
    body = "\n".join(l for l in text.split("\n") if not l.startswith(">"))       # the procedure's own words, its quotes apart
    for gone in ("heated through its body diode", "body diode VSD", "the VSD sense taps", "gate tied to its source for the whole run"):
        assert gone not in body, "the procedure still instructs %r" % gone
    # round 14 (the recheck V2R's V2R-m4): the pass rule is the reading plus the ACHIEVED U, so round 13's fixed "39.51 K/W" left the
    # procedure's own words; the rule itself is what stays
    for kept in ("gate k on CH_BATQ", "One FET is read per interruption", "V2 | reciprocity", "plus its achieved U", "No temperature coefficient is printed",
                 "Neither pour is cut", "RT1's land"):
        assert kept in body, "the procedure lacks %r" % kept
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    assert "DELTA-02" in readme and "TP-E11-29" in readme and "what the method cannot bound" in readme.lower()


# ---- round 14 (5 October 2026): the recheck V2R's V2R-B1 and V2R-B2 on TP-E11-29's fixture and pass rules, and its minors
# Round 13's statements as they stood at 4def5975, kept here as fixtures so each check is shown to refuse them (no git needed).
_R13_FIXTURE_TEXT = ("heating supply I_H (+) ---+ ... (one at a time) ... shunt (heating) ... heating supply (-) -------+        bypass switch across "
                     "the heating supply: closed before the last channel opens. Calibration and sensing: the heating supply bypassed; gate k on "
                     "CH_BATQ, the other two gates on VBAT")
_R13_STEP14_TEXT = ("For each FET the sum S_k = Zself,k + the two Zmut into k (the record's \"Zself + 2 Zmut\" with each actual mutual term in place "
                    "of an assumed equal one). The bar: with m = the largest Zmut over the largest Zself, the bar is the record's formula (section 1's "
                    "quote): 40.78 K/W at m = 0, rising to 45.88 K/W from m = 1/4; without m, 40.78 K/W.")


def _tp_body():
    text = open(TP29, encoding="utf-8").read()
    return text, "\n".join(l for l in text.split("\n") if not l.startswith(">"))


def _fixture_isolates(body):
    """A procedure's fixture isolates the heating supply for a reading: a series switch in the supply's lead, a bypass on the supply's
    side of it, an interlock that ties a gate to its drain only with the series switch open, the gate tied at its own drain tap; and
    none of round 13's statements (a bypass across the supply with its leads left on the pours, a clamped supply)."""
    flat_ = " ".join(body.split())
    need_ = ("series switch SW_S", "SW_B", "interlock", "tied to its own drain tap", "a gate is tied to its drain tap only while the series switch SW_S is open")
    gone = ("bypass switch across the heating supply", "or the supply is clamped", "the heating supply bypassed")
    return all(n in flat_ for n in need_) and not any(g in flat_ for g in gone)


def _rule_is_per_junction(body):
    """A procedure's reduction judges each junction at its own row's m_k, judges the baseline in the limit's line, and no longer gives
    every S_k the bar at the largest Zmut over the largest Zself."""
    flat_ = " ".join(body.split())
    return ("m_k = D_k / (2 C_k)" in flat_ and "over step 6's baseline B_k" in flat_ and "T_k = B_k + z17_k" in flat_
            and "with m = the largest Zmut over the largest Zself, the bar is" not in flat_)


def t_round14_v2r_b1_the_old_fixture_joins_the_pours_and_the_redrawn_one_leaves_the_device_alone():
    """V2R-B1: with round 13's fixture (a bypass across the heating supply, its leads on both pours) the pours are joined outside the FETs
    in calibration and sensing, so the sense current never reaches a threshold; the redrawn fixture (a series switch in the supply's
    lead, the bypass on the supply's side) joins them in no state. In each state the device under test is the only conductor of
    consequence on Nexperia's printed rows and the fixture's proposed limits, recomputed here; a fixture that closes SW_S in a reading,
    or a procedure that keeps round 13's statements, FAILS."""
    R = _R()
    m = _M()
    S, S23 = R["S24"], R["S23"]
    for st in ("calibration", "sensing"):
        joined, path = m.r14_state("old", st)
        assert joined and path == ["the heating supply's + lead", "the bypass switch across the heating supply", "the shunt and the - lead"], (st, path)
    assert not m.r14_state("old", "heating")[0]
    assert not any(m.r14_state("new", st)[0] for st in ("calibration", "heating", "sensing")), "the redrawn fixture joins the pours"
    # mutation: SW_S left closed in a reading joins the pours again
    keep = m.R14_FIXTURES["new"]
    try:
        m.R14_FIXTURES["new"] = [(n, a, b, k, ("heating", "sensing") if n.startswith("the series switch") else c) for n, a, b, k, c in keep]
        assert m.r14_state("new", "sensing")[0], "a closed series switch in a reading is not seen joining the pours"
    finally:
        m.R14_FIXTURES["new"] = keep
    # the margins, recomputed from the printed rows and the proposals
    assert abs(S["idss"][0] - 1e-6) < 1e-15 and abs(S["idss"][1] - 10e-6) < 1e-15 and abs(S["igss"] - 100e-9) < 1e-15
    assert S["leak_p"] == 6 and S["vgs_abs"] == 20.0
    tot = 2 * 10e-6 + 100e-9 + 1e-6 + 6 * 1e-6 + 3 * 3.0 / 10e6
    assert abs(S["sense_sum"] - tot) < 1e-12 and S["sense_frac"] < 0.03 and abs(S["sense_ratio"] - 100.0) < 1e-9
    assert abs(S["old_v"] - 20e-6) < 1e-12 and S["old_v"] < S23["vth"][1] / 1e4, "the old loop's voltage is not far under the least threshold"
    assert S["clamp_p"][0] > 20.0 and abs(S["clamp_p"][0] - S23["i_td"][0][0] * 1.5) < 1e-9
    assert S["heat_ratio"] > 1e5 and abs(S["t_settle"] - (3 * R["L"]["ciss_0"] + 3e-9) * 3.0 / 1e-3) < 1e-12 and S["t_settle"] < 0.5e-4
    assert S["v_sw_open"] < m.R14_SW["v_block"] and abs(S["duty_lost"] - 0.010012) < 1e-9
    # the procedure: round 13's statements refused, the redrawn fixture carried
    text, body = _tp_body()
    assert not _fixture_isolates(_R13_FIXTURE_TEXT), "the check accepts round 13's fixture"
    assert _fixture_isolates(body), "the procedure's fixture does not isolate the heating supply"
    fx = body.split("2. **The fixture, drawn for the supplier's agreement**")[1].split("3. **The states**")[0]
    assert "SW_S" in fx and "SW_B" in fx and "dummy leg" in fx and "tap Dk's own line" in fx
    page = open(PAGE, encoding="utf-8").read()
    p23f = " ".join(page.split("### 23f. ")[1].split("### 23g. ")[0].split())
    assert "or the supply is clamped" not in p23f and "a series switch isolates the" in p23f
    out = open(OUT, encoding="utf-8").read()
    o23f = out.split("   23f. ")[1].split("   23g. ")[0]
    assert "or the supply is clamped" not in o23f


def _scan_row(z, grid):
    """The largest of sum(z_i x_i) / (sum x_i)^2 times 9 over a grid of conductance ratios for the three FETs (each at least 1)."""
    best = 0.0
    for a in grid:
        for b in grid:
            for c in grid:
                s = a + b + c
                best = max(best, 9.0 * (z[0] * a + z[1] * b + z[2] * c) / (s * s))
    return best


def t_round14_v2r_b2_each_junction_at_its_own_worst_split_and_a_search_proves_the_rule():
    """V2R-B2: the closed form of each junction's worst split equals a scan of every split of three RDS(on) values (rows physical and
    not); V2R's example passes every round 13 line at 152.3 C and fails round 14's limit line; on a fresh seed the search finds no
    specimen accepted over 150 C by round 14's lines (readings perturbed within U, and exact), none refused that meets the limit and both
    allocations, and round 13's step 14 and its lines together accepting specimens over the limit; a line 2 that takes the band's
    budgeted 9.16 K instead of the measured baseline, or judges every junction at round 13's fixed split, FAILS; the procedure's
    reduction is round 14's and refuses round 13's step 14."""
    import random
    R = _R()
    m = _M()
    S, S21 = R["S24"], R["S21"]
    K = S["K"]
    rnd = random.Random(77)
    grid = [1.0 + k / 12.0 for k in range(0, 25)]
    for _ in range(30):
        zs = rnd.uniform(5.0, 50.0)
        z = [zs, rnd.uniform(0.0, 1.0) * zs, rnd.uniform(0.0, 1.0) * zs] if rnd.random() < 0.8 else [rnd.uniform(1.0, 50.0) for _k in range(3)]
        zw, x, mk = m.worst_row(z)
        g = sorted(set(grid + [x]))
        sc = _scan_row(z, g)
        assert sc <= zw * (1 + 1e-12) and sc >= zw * (1 - 1e-9) - 1e-9, (z, zw, sc)
        if z[0] == max(z):
            assert abs(sum(z) - m.bar_at(mk, zw)) < 1e-9 * zw or mk >= 0.25, "Zw is not S_k at 21b's bar at m_k"
    # V2R's example
    e = S["ex"]
    assert abs(e["case_f"] - 65.3) < 0.05 and abs(e["even"] - 76.03) < 0.05 and abs(e["tj"] - 152.28) < 0.05 and not e["new"][0]
    Zx = [[20.0 if i == j else 12.0 for j in range(3)] for i in range(3)]
    assert m.r13_step14(Zx, 0.0, K) and m.r13_direct(Zx, [14.0] * 3, [1.0] * 3, 0.0, K)[0], "round 13's lines no longer pass the example"
    # the search on a fresh seed
    sr = m.r14_search(K, S["u"], 4242, 2500)
    assert sr["new_over"] == 0 and sr["new0_over"] == 0 and sr["new0_miss"] == 0 and sr["rec_over"] == 0, sr
    assert sr["new_acc"] > 500 and sr["s14_over"] > 0 and sr["old_over"] > 0, "the search does not show round 13's lines failing"
    # mutations of the rule, each FAILS on the same search
    keep = m.r14_lines

    def no_baseline(Z, B, z17, u, K_, extra=(0.0, 0.0, 0.0)):
        return keep(Z, [R["S19"]["band"]] * 3, z17, u, K_, extra)

    def fixed_split(Z, B, z17, u, K_, extra=(0.0, 0.0, 0.0)):
        # every junction judged at round 13's fixed split (x = 2: 1.513 / 0.756 / 0.756 W), whatever its own row's m_k
        zw = [9.0 * (2.0 * max(Z[k]) + sum(Z[k]) - max(Z[k])) / 16.0 for k in range(3)]
        t_ = [B[k] + z17[k] * K_["p17"] + K_["p_even"] * zw[k] + extra[k] for k in range(3)]
        return (max(zw) * (1 + u) <= K_["bar_even"] and max(t_) * (1 + u) <= K_["rise"] and max(z17) * (1 + u) <= K_["z17"]), 0.0, 0.0, 0.0
    try:
        for mut in (no_baseline, fixed_split):
            m.r14_lines = mut
            assert m.r14_search(K, S["u"], 4242, 2500)["new_over"] > 0, "%s passes the search" % mut.__name__
    finally:
        m.r14_lines = keep
    # the record's own counts
    sr0 = S["search"]
    assert sr0["new_over"] == sr0["new0_over"] == sr0["new0_miss"] == sr0["rec_over"] == 0 and sr0["old_over"] == 2845 and sr0["s14_over"] == 2043
    # the procedure
    _text, body = _tp_body()
    assert not _rule_is_per_junction(_R13_STEP14_TEXT), "the check accepts round 13's step 14"
    assert _rule_is_per_junction(body), "the procedure's reduction is not round 14's"
    s8 = body.split("## 8. Pass, fail and inconclusive")[1].split("## 9.")[0]
    assert "Zw_k" in s8 and "T_k" in s8 and "73.75 K" in s8 and "achieved" in s8 and "cases F39, F40 and F42" in s8
    for v_ in ("0.333", "45.88", "40.78"):
        assert v_ in open(PAGE, encoding="utf-8").read().split("## 24. Round 14")[1]


def t_round14_the_minors_the_budget_and_the_procedures_status():
    """V2R-m1 (20g on 22c's set, 21d's mark), m3 (the tie at tap Dk, 2.4 mV), m4 (the budget's nine terms, the control run, the
    reading plus the achieved U), m5 (the rise over the baseline), m6 (65.9 uF across the node; the first prototype populated as the
    coupon), m7 (the leads' heat flow and the pours' third); the page and the output carry section 24's figures; TP-E11-29 stays NOT
    EXECUTABLE with the recheck among its preconditions; the README answers V2R's findings."""
    R = _R()
    m = _M()
    S, S22, S23 = R["S24"], R["S22"], R["S23"]
    assert S["m1"] == (S22["sel"]["sink"]["run"], S22["sel"]["sink"]["ovp"], S22["sel"]["sink"]["clamp"])
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    p20g = page.split("### 20g. ")[1].split("### 20h. ")[0]
    o20g = out.split("   20g. ")[1].split("   20h. ")[0]
    for t_ in (p20g, o20g):
        assert "3.72 mA" in t_ and "6.45 mA" in t_ and "3.73 mA" not in t_ and "6.39 mA" not in t_
    row21d = [l for l in page.split("### 21d. ")[1].split("### 21e. ")[0].split("\n") if "R256 6.8 kOhm" in l][0]
    assert "**SUPERSEDED** by round 12" in row21d
    assert abs(S["tie_mv"] - 0.1e-3 * 23.93 * 1e3) < 1e-9
    rise = S23["rise_bar"]
    terms = [0.02, 0.01, 1.0 / rise, 0.5 / rise, 0.3 / rise, S23["ripple"][0] / 2 / rise, 0.5 / rise, 0.5 / rise, 0.1 / rise]
    u = math.sqrt(sum(x * x for x in terms))
    assert abs(S["u"] - u) < 1e-12 and len(S["terms"]) == 9 and "%.2f" % (u * 100) == "3.47"
    assert "%.2f" % S["pass_bar"] == "39.41" and "%.2f" % S["pass_rise"] == "71.28" and "%.2f" % S["pass_even"] == "44.34"
    assert abs(S["m6_c"] - 180e-6 * 104e-6 / 284e-6) < 1e-15 and abs(S["m6_dv"] - 1e-3 * 0.2 / S["m6_c"]) < 1e-12
    assert abs(S["lead_dt"] - 0.02 * S23["p"]["hot"] * 0.02 / (390.0 * 4e-6)) < 1e-12
    assert abs(S["pour_frac"][0] - (S23["i_td"][0][0] / 23.93) ** 2) < 1e-12 and abs(S["pour_frac"][0] - 1.0 / 3.0) < 0.001
    p24 = page.split("## 24. Round 14")[1]
    o24 = out.split("24. ROUND 14")[1]
    for v_ in ("20 uV", "20.7 W", "97.2 %", "34.8 us", "65.3 K", "152.3 C", "3.47 %", "39.41", "71.28", "44.34", "65.9 uF", "2.4 mV",
               "0.39 K", "2.17 W/m", "0.881", "11.6 %", "159.9 C", "C-PROT rev 1", "NOT EXECUTABLE"):
        assert v_ in p24 and v_ in o24, "%s is not in both section 24 and out 24" % v_
    for v_ in ("2,845", "2,043", "3,455", "20,850"):
        assert v_ in p24 and v_.replace(",", "") in o24, v_
    b29 = " ".join(page.split("#### Block E11-29")[1].split("#### Block E11-30")[0].split())
    assert "Nothing else joins the two pours" in b29 and "populated as the coupon is" in b29 and "the fixture's heavy leads" in b29
    assert "ACHIEVED expanded uncertainty" in b29 and "tied to its own drain tap" in b29 and "junction by junction" in b29
    row = [x for x in m.downstream(R) if x[0] == "E11-29"][0][3]
    assert m.e11_29_method(R) in row and "its OWN m_k" in row and "THE LIMIT" in row and "series switch" in row and "achieved" in row
    text, body = _tp_body()
    assert "**NOT EXECUTABLE.**" in text and "the independent recheck of the fixture of section 5 and the pass" in " ".join(text.split())
    for kept in ("control run C0", "| V8 |", "| V9 |", "| V7 |", "heavy lead", "over step 6's baseline B_k", "populated as the coupon is"):
        assert kept in body, "the procedure lacks %r" % kept
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    assert "V2R's findings answered" in readme and "V2R-B1" in readme and "V2R-B2" in readme and "ROUND 14" in readme
