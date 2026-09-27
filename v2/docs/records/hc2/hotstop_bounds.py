#!/usr/bin/env python3
"""The hot stop's thresholds and the ambients at which it acts (MESHSAT-1357, 27 September 2026).

Answers Review A of layer 2, finding P2-B2, and Review B of layer 3, finding B1: past the heat stage the kit acts on
the pack's measured cell temperature on every input state (CONOPS.md section 4c, "The hot stop"). This script does
two things, both arithmetic on figures already in the tree, stdlib only:

1. The thresholds against the gauge's error budget. THERMAL-COORDINATION.md section 3 (the battery review packet)
   sums the PUBLISHED terms of the gauge's temperature reading on the hot side to 2.07 K (thermistor
   interchangeability 0.71, pull-up drift 0.40, sensor lag 0.80, detection 0.16) and takes OTD at 57.5 C against the
   cells' 60 C limit. The hot stop reads the SAME four thermistors through the gauge (the sensor controller reads the
   gauge's cell temperatures over the pack SMBus), so the same budget applies to it, and the order of C1's cell
   trigger, the two hot-stop steps and OTD is fixed in the reading itself whatever the sensor's error.
2. The ambients at which each step acts, from records/hc2/pwr_red2.out (the layer-2 closer's figures, produced by
   records/hc2/pwr_red2.py from records/rv-pwr/pwr_budget.py): on an input the pack carries no current and its cells
   sit at about the inside air (INFERRED: the model's cell rise over the air is the pack's own I2R, zero at no
   current); on the pack they sit above the air by the model's cell rise (its cells_at_20C less 20 C).

Usage: python3 hotstop_bounds.py [path to pwr_red2.out]   (default: pwr_red2.out beside this file)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "pwr_red2.out")

# THERMAL-COORDINATION.md section 3 (VERIFIED on main a8652172): the published hot-side terms and OTD
BUDGET_TERMS_K = {"thermistor interchangeability": 0.71, "pull-up drift": 0.40, "sensor lag": 0.80,
                  "detection (the gauge's 1 s decision plus 2 s delay)": 0.16}
BUDGET_K = 2.07          # the packet's own rounded sum of the terms above (0.71 + 0.40 + 0.80 + 0.16 = 2.07)
LIMIT_C = 60.0           # the cells' discharge limit at the cell surface (Samsung INR18650-35E Ver. 1.1 3.12)
OTD_C = 57.5             # the gauge's discharge over-temperature, SC-12 on main (THERMAL-COORDINATION.md section 5)
C1_CELL_C = 55.0         # C1's cell trigger (feasibility/POWER-THERMAL.md section 9.3; CONOPS.md section 4c)
H1_C = 56.5              # the hot stop, first step: shed to the minimum load (taken by the session)
H2_C = 57.0              # the hot stop, second step: the kit's controlled shutdown (taken by the session)
RELEASE_C = 46.5         # the hot stop released: 10 K under H1 (taken by the session)
ENVELOPE_HOT_C = 40.0    # the use envelope's hot edge (OPERATING-ENVELOPE.md section 2)
# The stop's own detection (the sensor controller reads the gauge's cell temperatures once a second and asks for two
# readings in a row; the line and the panel controller add under 0.2 s) against the gauge's own (1 s plus 2 s): at
# most 1.2 s more, at the budget's heating rate of 3.2 K per minute (THERMAL-COORDINATION.md section 3)
EXTRA_DETECTION_S = 1.2
RATE_K_PER_MIN = 3.2

STATES = {"PS-SURV (slot 2 alone, the heat stage as board B is generated)": "PS-SURV (slot 2 alone)",
          "PS-SURV-R (slot 3 alone, the heat stage after BANK-R1)": "PS-SURV-R (slot 3 alone after BANK-R1)"}


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    out = {"source": os.path.basename(SRC), "model_sha256": d.get("model_sha256")}
    s = round(sum(BUDGET_TERMS_K.values()), 2)
    assert s == BUDGET_K, s
    extra_k = round(EXTRA_DETECTION_S / 60.0 * RATE_K_PER_MIN, 2)
    thr = {}
    for name, t in (("C1 cell trigger", C1_CELL_C), ("hot stop H1 (shed)", H1_C), ("hot stop H2 (shutdown)", H2_C),
                    ("gauge OTD", OTD_C)):
        true_max = round(t + BUDGET_K, 2)
        thr[name] = {"reading_C": t, "true_cell_at_most_C": true_max, "inside_60C_by_K": round(LIMIT_C - true_max, 2)}
    thr["hot stop H1 (shed)"]["with_its_own_extra_detection_K"] = extra_k
    thr["hot stop H2 (shutdown)"]["with_its_own_extra_detection_K"] = extra_k
    order = [C1_CELL_C, H1_C, H2_C, OTD_C]
    assert order == sorted(order) and len(set(order)) == 4
    out["budget"] = {"published_terms_K": BUDGET_TERMS_K, "sum_K": BUDGET_K,
                     "two_TBD_terms": "the gauge's own ADC and fit, the sensed cell to the hottest cell (P14)",
                     "stop_extra_detection_K": extra_k}
    out["thresholds"] = thr
    out["spacing_in_the_reading_K"] = {"C1 to H1": round(H1_C - C1_CELL_C, 2), "H1 to H2": round(H2_C - H1_C, 2),
                                       "H2 to OTD": round(OTD_C - H2_C, 2), "H1 release below H1": round(H1_C - RELEASE_C, 2)}
    amb = {}
    for label, key in STATES.items():
        st = d["states"][key]
        amb[label] = {}
        for enc in ("closed_fans", "open_fans"):
            e = st[enc]
            # on the pack: the cells' rise over the ambient is the model's cells_at_20C less 20 C
            pack_rise = {"W4": [round(e["cells_at_20C_W4"][0] - 20.0, 2), round(e["cells_at_20C_W4"][1] - 20.0, 2)],
                         "3253": [round(e["cells_at_20C_3253"][0] - 20.0, 2), round(e["cells_at_20C_3253"][1] - 20.0, 2)]}
            # on an input: the cells at the inside air
            input_rise = {"W4": list(e["rise_W4_K"]), "3253": list(e["rise_3253_K"])}
            # self-check against the model's own 60 C ceiling (pack case), which pwr_red2.py printed
            ceil = e["ambient_ceilings_C"]["cells discharge 60 C"]
            assert abs((LIMIT_C - pack_rise["W4"][1]) - ceil["W4_worst_to_best"][0]) <= 0.11, (key, enc)
            assert abs((LIMIT_C - pack_rise["W4"][0]) - ceil["W4_worst_to_best"][1]) <= 0.11, (key, enc)
            row = {}
            for src, rise in (("on the pack", pack_rise), ("on an input", input_rise)):
                r = {}
                for step, t in (("H1 at", H1_C), ("H2 at", H2_C)):
                    r[step] = {"independent_bound_worst_to_best": [round(t - rise["W4"][1], 1), round(t - rise["W4"][0], 1)],
                               "design_record_3253_worst_to_best": [round(t - rise["3253"][1], 1), round(t - rise["3253"][0], 1)]}
                r["cells_at_40C_ambient_C"] = {"independent_bound_worst_to_best": [round(ENVELOPE_HOT_C + rise["W4"][1], 1),
                                                                                    round(ENVELOPE_HOT_C + rise["W4"][0], 1)],
                                               "design_record_3253_worst_to_best": [round(ENVELOPE_HOT_C + rise["3253"][1], 1),
                                                                                     round(ENVELOPE_HOT_C + rise["3253"][0], 1)]}
                w = r["H1 at"]
                r["H1 acts inside the envelope (at or below +40 C)"] = {
                    "independent_bound_worst": w["independent_bound_worst_to_best"][0] <= ENVELOPE_HOT_C,
                    "independent_bound_best": w["independent_bound_worst_to_best"][1] <= ENVELOPE_HOT_C,
                    "design_record_3253_worst": w["design_record_3253_worst_to_best"][0] <= ENVELOPE_HOT_C,
                    "design_record_3253_best": w["design_record_3253_worst_to_best"][1] <= ENVELOPE_HOT_C}
                row[src] = r
            amb[label]["lid closed" if enc == "closed_fans" else "lid open"] = row
    out["ambients_C"] = amb
    out["reading"] = ("INFERRED. The hot stop's first step acts inside the envelope at the independent bound's worst "
                      "corner in every configuration, and at no corner of the design record's own conductance (appendix "
                      "32.53); where between them the enclosure lies is FEA-004's, measured by the empty-case "
                      "heat-balance test (TEST-PLAN.md T-H1). No figure here is a measurement.")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
