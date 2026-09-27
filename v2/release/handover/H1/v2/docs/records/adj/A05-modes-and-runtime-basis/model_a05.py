#!/usr/bin/env python3
"""A05 adjudication model (MESHSAT-1357): independent re-implementation of W2's budget and runtime model.

PROVISIONAL. Load values are transcribed from W2's draft table (wt/w2/drafts/w2-power.md section 5, lines 164 to 189),
NOT from W2's scratch script, and every value carries a basis tier:
  S = a datasheet figure of the picked part at a defined state (idle, receive, typical, maximum)
  D = a generator declaration (a rail current or an outlet contract), taken as the load; INFERRED
  T = no document for the part, a 32.52 placeholder, or a duty-cycle assumption; TBD
Runtime equations are W2's assumptions A1 to A10 (w2-runtime.md lines 33 to 50), re-coded here, checked against the
Samsung INR18650-35E spec Ver. 1.1 (v2/vendor/battery/samsung-35e-orbtronic.pdf, sha256 5ec577b9...).
Temperature: +20 C. The spec's standard test condition is 23 +- 3 C (section 6.1), so a cell at +20 C is inside the
condition the 3,350 mAh minimum is stated at; at +20 C ambient the cells of a running kit sit at +30 to +36 C
(W2 A7), where spec 7.5 gives the same 97 % at 1C as at 23 C. Either reading: temperature factor 1.00.
"""
import json, sys

S5, S33, S10, LDO = 0.90, 0.90 * 0.88, 0.90 * 0.85, 0.90 * 0.66
STATES = ["IDLE", "TYP", "RED", "EMCON", "ALLTX", "ALLTX_OUT"]   # W2 M1, M2, M3, M4, M5, M6

# name: (eta, values per state, tiers per state)
L = {
    "CM5 x3":            (S5,  [6.0, 13.5, 4.5, 13.5, 24.0, 24.0],   "SSSSDD"),
    "slot fans x3":      (S5,  [1.5, 1.5, 0.5, 1.5, 1.5, 1.5],        "TTTTTT"),
    "PCIe switch x3":    (0.78, [1.86, 1.86, 0.62, 1.86, 3.21, 3.21], "SSSSSS"),
    "NVMe x3":           (S33, [0.9, 3.0, 1.0, 3.0, 12.0, 12.0],      "TTTTTT"),
    "WiFi AW7915 x2":    (S33, [2.0, 6.0, 0.0, 2.0, 20.0, 20.0],      "TTTTTT"),
    "5G RM520N-GL":      (S33, [0.2, 1.5, 0.0, 0.02, 5.0, 5.0],       "STSSSS"),
    "LimeSDR Mini 2.4":  (S5,  [0.0, 3.0, 0.0, 3.0, 4.5, 4.5],        "TTTTTT"),
    "LoRa E22":          (S5,  [0.07, 0.3, 0.07, 0.07, 3.25, 3.25],   "STSSSS"),
    "RockBLOCK 9704":    (S5,  [0.06, 0.1, 0.06, 0.06, 1.4, 1.4],     "STSSSS"),
    "E72 x2":            (S33, [0.26, 0.26, 0.26, 0.26, 1.0, 1.0],    "DDDDDD"),
    "LG290P":            (S33, [0.33, 0.33, 0.33, 0.33, 0.33, 0.33],  "SSSSSS"),
    "TUSB8041 x3":       (0.80, [0.3, 1.5, 0.3, 1.5, 3.0, 3.0],       "TSTSSS"),   # 0.1 W per hub idle is between Suspend and HS-only rows of SLLSEE4E 7.7
    "KSZ9897R":          (0.72, [1.8, 1.8, 1.8, 1.8, 1.8, 1.8],       "TTTTTT"),
    "B logic":           (LDO, [1.5, 1.5, 1.5, 1.5, 1.5, 1.5],        "DDDDDD"),
    "panel board C":     (0.85, [1.5, 3.0, 1.5, 3.0, 5.0, 5.0],       "DDDDDD"),
    "APRS board D":      (S5,  [0.6, 0.8, 0.6, 0.6, 3.3, 3.3],        "DDDDDD"),
    "camera":            (S5,  [0.0, 1.0, 0.0, 1.0, 2.5, 2.5],        "TTTTTT"),
    "QMX USB, HDMI 5 V": (S5,  [0.3, 0.3, 0.3, 0.3, 0.3, 0.3],        "DDDDDD"),
    "Xenarc 709GNK":     (1.00, [4.0, 6.0, 0.0, 6.0, 10.0, 10.0],     "TTTTSS"),
    "E always-on":       (0.75, [0.8, 0.8, 0.8, 0.8, 1.5, 1.5],       "DDDDDD"),
    "E mixer fans x2":   (1.00, [0.0, 1.4, 1.4, 1.4, 2.9, 2.9],       "TTTTTT"),
    "A logic":           (0.88, [0.5, 0.5, 0.5, 0.5, 1.0, 1.0],       "DDDDDD"),
    "QMX (+12V_HF)":     (0.93, [0.0, 1.0, 0.0, 1.0, 12.0, 12.0],     "SSSSTT"),
    "30 W PA":           (0.93, [0.0, 0.0, 0.0, 0.0, 75.0, 75.0],     "SSSSSS"),
    "PoE out":           (0.88, [0.0, 0.0, 0.0, 0.0, 0.0, 32.0],      "DDDDDD"),
    "USB-C PD out":      (0.93, [0.0, 0.0, 0.0, 0.0, 0.0, 45.0],      "DDDDDD"),
}
R_DIST, V_PACK = 0.020, 14.4

def state_vals(k):
    return {n: (eta, v[k], t[k]) for n, (eta, v, t) in L.items()}

def variant(base_k, overrides):
    d = state_vals(base_k)
    for n, val in overrides.items():
        eta, _, t = d[n]
        d[n] = (eta, val, t)
    return d

def battery(d):
    pl = sum(v for _, v, _ in d.values())
    pb0 = sum(v / eta for eta, v, _ in d.values())
    tier = {"S": 0.0, "D": 0.0, "T": 0.0}
    for eta, v, t in d.values():
        tier[t] += v / eta
    pb = pb0
    for _ in range(50):
        pb = pb0 + (pb / V_PACK) ** 2 * R_DIST
    return pl, pb, tier, pb - pb0

# cell: Samsung INR18650-35E Ver. 1.1
C_MIN = 3.35                                          # Ah, 3.1 and 7.2 (0.2C, 2.65 V, 23 C)
RATE = [(0.68, 1.00), (3.4, 0.97), (6.8, 0.95), (8.0, 0.92)]   # 7.8
V_NOM, R_DC, RESERVE = 3.60, 0.05, 0.05               # 3.3; R_DC INFERRED (W2 A3); reserve W2 A5

def rate_f(i):
    if i <= RATE[0][0]:
        return 1.0
    for (a, fa), (b, fb) in zip(RATE, RATE[1:]):
        if i <= b:
            return fa + (fb - fa) * (i - a) / (b - a)
    return RATE[-1][1]

def runtime(pb, p, age=1.0, f_t=1.0):
    i = pb / (4 * V_NOM) / p
    e = 4 * p * C_MIN * rate_f(i) * (V_NOM - i * R_DC) * f_t * age * (1 - RESERVE)
    return e / pb, e, i

rows = []
defs = [
    ("PS-IDLE", "W2 M1", state_vals(0)),
    ("PS-TYP", "W2 M2", state_vals(1)),
    ("PS-RED (envelope: one module)", "W2 M3", state_vals(2)),
    ("PS-RED-b (32.53: cluster idle, monitor off)", "W2 M1 with the monitor at 0", variant(0, {"Xenarc 709GNK": 0.0})),
    ("PS-EMCON (W2 as drafted)", "W2 M4", state_vals(3)),
    ("PS-EMCON (as generated: gated rails off)", "W2 M4 less LimeSDR, QMX, LoRa, RockBLOCK, E72",
     variant(3, {"LimeSDR Mini 2.4": 0.0, "QMX (+12V_HF)": 0.0, "LoRa E22": 0.0, "RockBLOCK 9704": 0.0, "E72 x2": 0.0})),
    ("PS-ALLTX", "W2 M5", state_vals(4)),
    ("PS-ALLTX-OUT", "W2 M6", state_vals(5)),
    ("PS-IDLE, monitor at 6 W (V2-SPEC 'monitor on')", "W2 M1 with the monitor at 6 W", variant(0, {"Xenarc 709GNK": 6.0})),
]
# V2-SPEC.md:23 words on today's three-module kit: monitor on (6 W, 32.52 placeholder), radios idle, APRS beacons.
# Beacon average: 32.52 item 3 gives "APRS with the PA 1.5" W typical against board D's 0.6 W receive in W2's M1,
# so 0.9 W average on +13V8_PA (eta 0.93) is added as a TBD placeholder (beacon interval TBD, CONOPS line 166).
_d = variant(0, {"Xenarc 709GNK": 6.0, "30 W PA": 0.9})
_d["30 W PA"] = (0.93, 0.9, "T")
defs.append(("PS-IDLE as V2-SPEC words it (monitor on, APRS beacons)", "W2 M1 + monitor 6 W + 0.9 W beacon average", _d))
for name, src, d in defs:
    pl, pb, tier, i2r = battery(d)
    r = {"state": name, "source": src, "load_W": round(pl, 2), "battery_W": round(pb, 2),
         "battery_W_S": round(tier["S"], 2), "battery_W_D": round(tier["D"], 2), "battery_W_T": round(tier["T"], 2),
         "distribution_I2R_W": round(i2r, 2)}
    for p in (3, 4):
        for age, lab in ((1.0, "BOL"), (0.8, "EOL80")):
            h, e, i = runtime(pb, p, age)
            r[f"4S{p}P_{lab}_h"] = round(h, 2)
            r[f"4S{p}P_{lab}_Wh_usable"] = round(e, 1)
            r[f"4S{p}P_Icell_A"] = round(i, 2)
        r[f"4S{p}P_bare_h"] = round(4 * p * C_MIN * V_NOM / pb, 2)   # no rate, sag, reserve or age: cross-check only
    rows.append(r)

# off with the pack connected (W2 section 5 line 195: 0.37 to 1.87 W at the battery, board E always-on TBD)
for pb in (0.37, 1.87):
    r = {"state": f"PS-OFF {pb} W", "source": "W2 M0", "battery_W": pb}
    for p in (3, 4):
        for age, lab in ((1.0, "BOL"), (0.8, "EOL80")):
            h, e, i = runtime(pb, p, age)
            r[f"4S{p}P_{lab}_days"] = round(h / 24, 1)
    rows.append(r)

# heater overlays (W2 section 5: 10.8 W at the battery), shown at +20 C only for completeness of the power column
for name, k in (("PS-TYP + heater", 1), ("PS-RED + heater", 2)):
    d = state_vals(k)
    d["heater mat"] = (1.0, 10.8, "D")
    pl, pb, tier, i2r = battery(d)
    rows.append({"state": name, "source": "W2 section 5 line 196", "load_W": round(pl, 2), "battery_W": round(pb, 2),
                 "battery_W_S": round(tier["S"], 2), "battery_W_D": round(tier["D"], 2), "battery_W_T": round(tier["T"], 2)})

# 32.52 item 3 arithmetic check (appendix line 2846)
typ = [18, 6, 3, 3, 3, 0.5, 0.5, 1, 1.5, 6, 2.5]
peak = [36, 10, 10, 10, 3, 6.5, 5, 12, 75, 8, 2.5]
chk = {"sum_typ": sum(typ), "sum_peak": sum(peak), "typ_x1.12": round(sum(typ) * 1.12, 1),
       "peak_x1.12": round(sum(peak) * 1.12, 1), "typ_div0.88": round(sum(typ) / 0.88, 1),
       "peak_div0.88": round(sum(peak) / 0.88, 1), "peak_plus_outlets_x1.12": round((sum(peak) + 90) * 1.12, 1),
       "peak_x1.12_plus_outlets": round(sum(peak) * 1.12 + 90, 1),
       "BB2590_32.52_5to6h_x50W_Wh": [250, 300], "BB2590_32.49_8to9.5h_x29W_Wh": [29 * 8, 29 * 9.5],
       "BB2590_32.49_11to13.5h_x20W_Wh": [20 * 11, 20 * 13.5], "BB2590_energy_32.49_item12_Wh": [250, 300]}

json.dump({"rows": rows, "check_32_52": chk}, open(sys.argv[1] if len(sys.argv) > 1 else "a05_results.json", "w"), indent=1)
for r in rows:
    print(json.dumps(r))
print(json.dumps(chk))
