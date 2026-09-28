#!/usr/bin/env python3
"""night_bounds.py: the night state PS-NIGHT-RELAY computed with the tree's own power model (stream energy, MESHSAT-1357,
28 September 2026). PROTOTYPE DESIGN: nothing built, powered or measured; an AI review.

It imports v2/docs/records/rv-pwr/pwr_budget.py UNCHANGED (pinned by sha256, refused if it changed), exactly as
records/hc2/pwr_red2.py does, and evaluates the model's RED state (slot 3 alone) with the overrides below, at the model's
three scenarios LOW (every load at its documented lowest, efficiencies at 12 V), PLAN (14.4 V) and HIGH (every load at its
maximum at once, 16.8 V). So the night state carries the same kind of low-to-high bound as every other state in CONOPS 4a.
It first reproduces PS-SURV-R (RED plus the APRS beacons: 12.78 / 23.27 / 46.94 W in records/hc2/pwr_red2.out) as a check
of the method. Stdout only; deterministic. Usage: night_bounds.py (from anywhere; about 0.1 s).
"""
import hashlib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.normpath(os.path.join(HERE, "..", "rv-pwr", "pwr_budget.py"))
MODEL_SHA256 = "469d0820b046ef6ff5aceadf422b4166de3d6a02bc50fa5b0c3644704f0f9556"


def main():
    got = hashlib.sha256(open(MODEL, "rb").read()).hexdigest()
    if got != MODEL_SHA256:
        sys.stderr.write("night_bounds: v2/docs/records/rv-pwr/pwr_budget.py changed (sha256 %s), refusing to run\n" % got[:16])
        return 3
    spec = importlib.util.spec_from_file_location("pwr_budget", MODEL)
    pb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pb)
    up, same, OFF = pb.up, pb.same, pb.OFF
    beacons = up(0.1, 0.9, 0.9, "T")        # pwr_red2.py's BEACONS: PS-IDLE-SPEC's average on the PA rail
    lamps_decl = 0.7965                      # board C's lamps at their design currents, the intent's declared typical (d4energy energy_data.yaml, panel_lamps 'on')
    lamps_peak = 2.425                       # the same, declared peak (0.4619 A x 5.25 V)
    panel_plan = (1.50 - lamps_decl) + 0.15 * lamps_decl      # the declaration's logic share plus the lamps at NIGHT's 15 percent duty (PANEL.md section 8)
    panel_high = (5.00 - lamps_peak) + 0.15 * lamps_peak      # the declaration's peak 5.0 W with the lamps' peak at the same duty
    night = {
        "VHF PA 30 W": up(0.1, 0.125, 0.9, "T"),          # a fixed site: one 1 s beacon in ten minutes, 75 W / 600 (CONOPS section 5); HIGH the model's 0.9
        "two mixer fans": OFF,                              # a shaded, cool night (on in the heat)
        "Geiger module": OFF,                               # deferred from prototype 1's core by D-01
        "QMX USB and HDMI 5 V": OFF,                        # the QMX deferred by D-01; the monitor off
        "E72 x2 (Zigbee, Thread)": OFF,                     # not a bearer of M1
        "KSZ9897R AVDDH 2.5 V": up(0.050, 0.050, 0.825, "S"),          # energy-detect (DS00002330D Table 6-1); HIGH full operation
        "KSZ9897R VDDIO 3.3 V": up(0.099, 0.099, 0.264, "S"),
        "KSZ9897R AVDDL+DVDDL 1.2 V": up(0.216, 0.216, 1.452, "S"),
        "three STM32H743 supervisors and their parts": up(3 * (0.033 + 0.06) * 3.3, 3 * (0.033 + 0.06) * 3.3, 3 * (0.400 + 0.06) * 3.3, "R"),  # 200 MHz VOS3 (DS12110 Table 30); HIGH the model's
        "panel board C": up(panel_plan, panel_plan, panel_high, "D"),
        "RockBLOCK 9704": up(0.06, 0.1, 1.4, "R"),          # message driven: the planning duty of PS-TYP (a relay passes traffic at night)
        # the LoRa module keeps the model's RED figure up(0.07, 0.3, 3.25): receive plus about 9 percent airtime (CONOPS section 5)
    }
    out = []
    out.append("NIGHT STATE BOUNDS with the tree's model (records/rv-pwr/pwr_budget.py, sha256 %s, imported unchanged). AI review." % MODEL_SHA256[:16])
    out.append("battery W at the pack terminals: LOW / PLAN / HIGH (the model's scenarios)")
    rows = [("PS-SURV-R (check: pwr_red2.out 12.78 / 23.27 / 46.94)", {"VHF PA 30 W": beacons}),
            ("PS-NIGHT-RELAY", night)]
    for label, ov in rows:
        vals = [pb.state_full("RED", s, ov)["pb"] for s in ("lo", "plan", "hi")]
        out.append("  %-52s %6.2f / %6.2f / %6.2f" % (label, vals[0], vals[1], vals[2]))
    out.append("panel board C at night: %.3f W plan (the declaration's 1.50 W less the lamps' declared %.4f W, plus the lamps at 15 percent), %.3f W high" % (panel_plan, lamps_decl, panel_high))
    out.append("the LoRa module at the model's RED figure (0.3 W plan, receive plus about 9 percent airtime); the RockBLOCK at 0.1 W plan (one session in ten minutes)")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
