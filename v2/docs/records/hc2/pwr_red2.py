#!/usr/bin/env python3
"""The reduced mode of CONOPS.md section 4 (session choice under S-24 and CFL-011, MESHSAT-1357, 27 September 2026),
computed with the power and thermal model of v2/docs/records/rv-pwr/pwr_budget.py, which is imported unchanged.

PROVISIONAL: nothing in this kit has been built, powered or measured. Stdlib only, well under a second.

Three states are computed, each lid closed with the fans on (the reduced mode's enclosure, POWER-THERMAL.md 9.1) and,
for the shed stages, lid open as well:

  PS-RED2   the reduced mode taken: slots 2 and 3 powered, slot 1 off. Slot 2 hosts bank 2 (home) and bank 1 (its
            failover host, ARCH-PCB-B-IOHA.md section 4), so Iridium, the panel controller (the SOS path) and GNSS have
            a host; slot 3 hosts bank 3 (home: APRS board D8, the sensor controller, the 5G management link) and the
            LoRa module on its SPI. The 5G module (slot 2's PCIe) is registered and idle; both WiFi link cards are
            unpowered (card 1 is on slot 1, card 2 is held off by software); monitor off; SDR, camera and HF idle or
            off as in pwr_budget's PS-RED; APRS position beacons on the PA rail at PS-IDLE-SPEC's average.
  PS-SURV   the second shed stage: slot 2 alone. Banks 1 and 2 on slot 2 (bank 1 by failover); bank 3 has no host
            (its home slot 3 and its failover slot 1 are both off), so APRS, the sensor controller's USB link and
            LoRa are lost; Iridium, GNSS, the panel (SOS) and 5G stay.
  PS-RED    pwr_budget's own state (slot 3 alone), reprinted for comparison.
  PS-EMCON  pwr_budget's EMCON state with the two WiFi link cards unpowered, as EMCON is generated since 458b2873.

Added on 27 September 2026 (pass 2, answering Review A's findings B5, B7 and m2,
v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md):

  PS-SURV-R the heat stage after board B's bank reallocation BANK-R1 (CONOPS.md section 4c): slot 3 alone, hosting
            bank 3 (home: APRS board D8, the sensor controller, and after BANK-R1 the panel controller) and bank 2 (its
            failover host: GNSS, both E72, and after BANK-R1 the RockBLOCK), with the LoRa module on its SPI. It is
            pwr_budget's own PS-RED (slot 3 alone) with the APRS position beacons added at PS-IDLE-SPEC's average;
            the bank a USB device hangs on changes nothing in the model, which feeds every device from its rail.
  COLD      the cold end of the inside air (finding B7): for the normal mode lid open with the fans on, with the two
            WiFi link cards and the LimeSDR held off (the carve-out), with the pack heater, and with a warm-up load
            (the three modules at their loaded figure), the heat inside and the lowest ambient at which the inside
            air reaches 0 C on each conductance of the record. The heater is taken at 8.5 W at the pack, the
            regulated mat of main since 458b2873 (feasibility/POWER-THERMAL.md section 7.1: "the mat adds 8.5 W on
            main, regulated"), not the model's unregulated 10.8 W, which would overstate the warming. A reference
            row reproduces POWER-THERMAL.md section 7.1's cold row (PS-TYP plus the unregulated mat: 2.9 to 5.2 C
            at -20 C on appendix 32.53's conductance).
  PS-EMCON  gains its aged-60 % runtime (minor finding m2).

Every figure it prints is at the pack terminals (battery W) unless it says otherwise, on pwr_budget's conventions.
Usage: pwr_red2.py [<path to pwr_budget.py>]   (default: ../rv-pwr/pwr_budget.py beside this file)
"""
import importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Filed as v2/docs/records/hc2/pwr_red2.py, beside records/rv-pwr/; drafted in the worktree's drafts/ folder.
CANDIDATES = [os.path.join(HERE, "..", "rv-pwr", "pwr_budget.py"),
              os.path.join(HERE, "..", "v2", "docs", "records", "rv-pwr", "pwr_budget.py")]
DEFAULT = next((c for c in CANDIDATES if os.path.exists(c)), CANDIDATES[0])
path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
spec = importlib.util.spec_from_file_location("pwr_budget", path)
pb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pb)
up, same, OFF = pb.up, pb.same, pb.OFF

CM5_ON = up(2.0, 4.5, 4.5, "S")          # as pwr_budget's PS-RED module: idle to typical
FAN = up(0.36, 0.51, 0.56, "R")
SW33 = up(0.355, 0.355, 0.390, "S")
SW10 = up(0.270, 0.270, 0.676, "S")
NV_IDLE = up(0.90, 0.90, 1.05, "S")
RM_IDLE = same(0.222, "S")                # RM520N-GL idle, HD v1.1 Table 43
BEACONS = up(0.1, 0.9, 0.9, "T")         # APRS beacons on the PA rail, PS-IDLE-SPEC's average (pwr_budget)


def slot(s, on):
    return {"CM5 slot %d" % s: CM5_ON if on else OFF,
            "cooler fan slot %d" % s: FAN if on else OFF,
            "PCIe switch 3.3 V slot %d" % s: SW33 if on else OFF,
            "PCIe switch 1.0 V slot %d" % s: SW10 if on else OFF,
            "NVMe slot %d" % s: NV_IDLE if on else OFF}


def hubs(kinds):
    h33, h11 = pb.hubs(kinds)
    return {"three TUSB8041 hubs VDD33": h33, "three TUSB8041 hubs VDD 1.1 V": h11}


RED2 = {**slot(1, False), **slot(2, True), **slot(3, True), **hubs(("hs4", "hs4", "hs4")),
        "5G RM520N-GL": RM_IDLE, "WiFi link card 1 (live)": OFF, "WiFi link card 2 (standby)": OFF,
        "VHF PA 30 W": BEACONS}
SURV = {**slot(1, False), **slot(2, True), **slot(3, False), **hubs(("hs4", "hs4", "disc")),
        "5G RM520N-GL": RM_IDLE, "WiFi link card 1 (live)": OFF, "WiFi link card 2 (standby)": OFF,
        "LoRa E22-900M30S": OFF, "board D (SA868 and logic)": same(0.2, "T"), "VHF PA 30 W": OFF}
SURVR = {"VHF PA 30 W": BEACONS}          # on pwr_budget's RED state (slot 3 alone): the APRS beacons added
STATES = [("PS-RED2 (slots 2 and 3)", RED2), ("PS-SURV (slot 2 alone)", SURV), ("PS-RED (slot 3 alone, pwr_budget)", {}),
          ("PS-SURV-R (slot 3 alone after BANK-R1)", SURVR)]

G, G32, GBLK = pb.G, pb.G_3253, pb.G_BLK
gmid = sum(GBLK) / 2
import hashlib
out = {"model": "v2/docs/records/rv-pwr/pwr_budget.py", "model_sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(), "states": {}}


def heat(ov, scen, charging=False, eta=None):
    f = pb.state_full("RED", scen, ov)
    q = f["pb"] - f["outside"]
    if charging:
        return f, q + pb.charge_heat(f["pb"], eta), 12 * (pb.ICHG / 3) ** 2 * pb.R_CELL["plan"]
    return f, q, pb.pack_i2r(f["pb"])


for label, ov in STATES:
    row = {}
    for scen in ("lo", "plan", "hi"):
        row["battery_W_" + scen] = round(pb.state_full("RED", scen, ov)["pb"], 2)   # 2 decimals, as pwr_budget's runtime
    rt = {}
    for scen in ("lo", "plan", "hi"):   # the method of pwr_budget.main's runtime block, unchanged
        w = row["battery_W_" + scen]
        rt[scen] = {"new_h": round(pb.usable(w, 3, 1.0, 1.0, pb.R_CELL["plan"])[0] / w, 2),
                    "aged80_h": round(pb.usable(w, 3, 0.8, 1.0, pb.R_CELL["plan"])[0] / w, 2),
                    "aged60_h": round(pb.usable(w, 3, 0.6, 1.0, pb.R_CELL["plan"])[0] / w, 2),
                    "cold_new_h_low_end": round(pb.usable(w, 3, 1.0, pb.COLD_LO, pb.R_CELL["plan"])[0] / w, 2)}
    row["runtime_h_20C"] = rt
    for enc in ("closed_fans", "open_fans"):
        glo, ghi = G[enc]
        g32 = G32[enc]
        _, qp, pp = heat(ov, "plan")
        _, qh, ph = heat(ov, "hi")
        r = {"heat_plan_W": round(qp + pp, 1), "rise_W4_K": (round((qp + pp) / ghi, 1), round((qp + pp) / glo, 1)),
             "rise_3253_K": (round((qp + pp) / g32[1], 1), round((qp + pp) / g32[0], 1)),
             "rise_worst_K": round((qh + ph) / glo, 1)}
        cells20 = (round(pb.cell_temp(20, qp, pp, ghi, GBLK[1]), 1), round(pb.cell_temp(20, qp, pp, glo, GBLK[0]), 1))
        r["cells_at_20C_W4"] = cells20
        r["cells_at_20C_3253"] = (round(pb.cell_temp(20, qp, pp, g32[1], gmid), 1), round(pb.cell_temp(20, qp, pp, g32[0], gmid), 1))
        ceil = {}
        for lname, lim, kind in (("SGP41 +55 C", 55.0, "air"), ("cells charge 45 C", 45.0, "chg"),
                                 ("cells discharge 60 C", 60.0, "cell"), ("C1 cell trigger +55 C", 55.0, "cell"),
                                 ("C1 air trigger +50 C", 50.0, "air")):
            chg = kind == "chg"
            _, qb, pb_ = heat(ov, "plan", chg, pb.ETA_FE[1])
            _, qw, pw = heat(ov, "plan", chg, pb.ETA_FE[0])
            _, qm, pm = heat(ov, "plan", chg, sum(pb.ETA_FE) / 2)
            if kind == "air":
                w4 = (round(lim - (qw + pw) / glo, 1), round(lim - (qb + pb_) / ghi, 1))
                s3 = (round(lim - (qm + pm) / g32[0], 1), round(lim - (qm + pm) / g32[1], 1))
            else:
                w4 = (round(pb.ceiling(lim, qw, pw, glo, GBLK[0]), 1), round(pb.ceiling(lim, qb, pb_, ghi, GBLK[1]), 1))
                s3 = (round(pb.ceiling(lim, qm, pm, g32[0], gmid), 1), round(pb.ceiling(lim, qm, pm, g32[1], gmid), 1))
            ceil[lname] = {"W4_worst_to_best": w4, "3253": s3}
        r["ambient_ceilings_C"] = ceil
        row[enc] = r
    out["states"][label] = row

# PS-EMCON as generated since 458b2873: EMCON removes the two WiFi link cards' supplies (Q111, Q311 on their bucks'
# enables; CONOPS.md section 4b), which pwr_budget's EMCON state still carries at 4.0 W (card 1, "T": its draw with
# W_DISABLE1# asserted unknown) and 1.0 W (card 2, standby), the circuit before 458b2873. Everything else as pwr_budget.
EMCON_MAIN = {"WiFi link card 1 (live)": OFF, "WiFi link card 2 (standby)": OFF}
em = {}
for scen in ("lo", "plan", "hi"):
    em["battery_W_" + scen + "_pwr_budget"] = round(pb.state_full("EMCON", scen, {})["pb"], 2)
    em["battery_W_" + scen + "_since_458b2873"] = round(pb.state_full("EMCON", scen, EMCON_MAIN)["pb"], 2)
w = em["battery_W_plan_since_458b2873"]
em["runtime_h_20C_since_458b2873"] = {"new_h": round(pb.usable(w, 3, 1.0, 1.0, pb.R_CELL["plan"])[0] / w, 2),
                                      "aged80_h": round(pb.usable(w, 3, 0.8, 1.0, pb.R_CELL["plan"])[0] / w, 2),
                                      "aged60_h": round(pb.usable(w, 3, 0.6, 1.0, pb.R_CELL["plan"])[0] / w, 2)}
out["PS-EMCON"] = em

# THE COLD END OF THE INSIDE AIR (added 27 September 2026, Review A finding B7). Lid open, fans on, the normal mode.
# The carve-out holds both WiFi link cards and the LimeSDR off until the inside air reads 0 C. Inside air at an ambient
# a is a + heat / G; it reaches 0 C from a = -heat / G. The coldest case is the HIGHEST conductance in the record:
# appendix 32.53's 3.3 W/K lid open with fans (its natural-convection estimate; wind on the case would raise it,
# INFERRED). Heat is PLAN battery W less what the outlets deliver outside, plus the cells' own I2R, as the rest of
# this file and pwr_budget's section 9.1.
HEAT_REG = same(8.5, "S")    # POWER-THERMAL.md 7.1: "the mat adds 8.5 W on main, regulated"
CARVE = {"WiFi link card 1 (live)": OFF, "WiFi link card 2 (standby)": OFF, "LimeSDR Mini 2.4": OFF}
LOADED = {"CM5 slot %d" % s: up(4.5, 8.0, 8.0, "D") for s in (1, 2, 3)}   # pwr_budget's BUSY figure per module
HEATER = "pack heater mat (cold overlay)"
COLD = [
    ("PS-IDLE-SPEC, link cards held off", "IDLESPEC", dict(CARVE)),
    ("PS-IDLE-SPEC, link cards held off, heater on", "IDLESPEC", {**CARVE, HEATER: HEAT_REG}),
    ("PS-TYP, link cards and SDR held off", "TYP", dict(CARVE)),
    ("PS-TYP, link cards and SDR held off, heater on", "TYP", {**CARVE, HEATER: HEAT_REG}),
    ("warm-up: PS-TYP, link cards and SDR held off, heater on, three modules loaded", "TYP", {**CARVE, HEATER: HEAT_REG, **LOADED}),
    ("PS-TYP, every load on, heater on (after the carve-out lifts)", "TYP", {HEATER: HEAT_REG}),
    ("reference: PS-TYP plus the unregulated mat, POWER-THERMAL.md 7.1's cold row", "TYP", {HEATER: pb.HEAT_ON}),
]
g32, gw4 = G32["open_fans"], G["open_fans"]
cold = {"enclosure": "lid open, fans on", "G_3253_W_per_K": list(g32), "G_W4_W_per_K": list(gw4), "rows": {}}
for label, base, ov in COLD:
    f = pb.state_full(base, "plan", ov)
    q = f["pb"] - f["outside"]
    h = q + pb.pack_i2r(f["pb"])
    w = round(f["pb"], 2)
    cold["rows"][label] = {
        "battery_W_plan": w,
        "heat_inside_W": round(h, 1),
        "air_reaches_0C_from_ambient_3253_worst_to_best": (round(-h / g32[1], 1), round(-h / g32[0], 1)),
        "air_reaches_0C_from_ambient_W4_worst_to_best": (round(-h / gw4[1], 1), round(-h / gw4[0], 1)),
        "air_at_minus20C_ambient_3253_worst_to_best": (round(-20 + h / g32[1], 1), round(-20 + h / g32[0], 1)),
        "aged80_runtime_h_20C": round(pb.usable(w, 3, 0.8, 1.0, pb.R_CELL["plan"])[0] / w, 2),
    }
out["COLD"] = cold
print(json.dumps(out, indent=1))
