#!/usr/bin/env python3
"""A01: node voltage of every PCA9555-driven enable at power-up (I/O = input, internal pull-up to VCC
against the board's pull-down and the driven pin's own current), against the driven pin's thresholds.

Sources (all read in this adjudication):
  PCA9555 (fitted: TI PCA9555PWR, LCSC C2864778, JLC-CERTIFIED.tsv): TI SCPS131J (March 2021),
    Fig 8-2: 100 k from VCC to the I/O pin (drawn, no tolerance); 6.5: IIL (VI = GND) MAX -100 uA,
    no MIN, no TYP; ICC standby 'low inputs' (16 inputs at GND) 3.6 V: TYP 0.7 mA, MAX 1.3 mA.
  AP64500 (Diodes DS, v2/vendor/diodes/diodes-ap64500.pdf): VEN_H 1.18 typ / 1.25 max, VEN_L 1.03 min /
    1.09 typ; IEN (sourced, internal pull-up) 1 / 1.5 / 2 uA at VEN = 1 V, 5.5 uA typ at VEN = 1.5 V.
  TPS2596 (SLVSET8A): VUVLO(R) 1.18 / 1.20 / 1.22 V, IENLKG +-0.1 uA.
  LM5176 (SNVSAI1D): VEN(STBY) 0.55 / 0.82 / 0.97 V, IEN(STBY) 1 / 2 / 3 uA sourced,
    VEN(OP) 1.17 / 1.22 / 1.29 V.
  SN74LVC08A (SCAS283W): VIH 2.0 V, VIL 0.8 V at VCC 2.7 to 3.6 V, II +-5 uA.
  TPS2065C (SLVS490K): VIH 2.0 V, VIL 0.8 V.
  2N7002 (fitted: CJ, LCSC C8545, datasheet rev J Sep 2016): Vth(GS) 1.0 / 1.6 / 2.5 V at 250 uA.
  +3V3 on A: TPS62933 VREF 0.8 V, R48 31.6k / R49 10k -> 3.328 V.
"""
VCC = 0.8 * (1 + 31.6 / 10.0)          # 3.328 V, A's +3V3 (gen_sch_a.py:441)

# pull-up cases (resistor model, as TI draws it)
RPU = [
    ("33.3k  IIL spec bound (100 uA at 0 V)", VCC / 100e-6),
    ("44k    ICC max 1.3 mA/16 at 3.6 V (derived)", 3.6 / (1.3e-3 / 16)),
    ("82k    ICC typ 0.7 mA/16 at 3.6 V (derived)", 3.6 / (0.7e-3 / 16)),
    ("100k   drawn value, Fig 8-2", 100e3),
    ("150k   1.5x drawn", 150e3),
    ("200k   2x drawn", 200e3),
]

def node(rpu, rd, isrc=0.0):
    """V at the node: pull-up rpu to VCC, pull-down rd to GND, isrc sourced INTO the node by the driven pin."""
    return (VCC / rpu + isrc) / (1.0 / rpu + 1.0 / rd)

def rpu_break(rd, vth, isrc=0.0):
    """largest pull-up that still lifts the node to vth: (VCC - vth)/rpu = vth/rd - isrc"""
    need = vth / rd - isrc
    return float("inf") if need <= 0 else (VCC - vth) / need

LINES = [
    # name, where, rd_eff, isrc (worst case for OFF, i.e. minimum source), on-threshold (max), off-threshold, verdict text
    ("DEV_EN",      "A U27.11 -> U7 AP64500 EN",        100e3,               1.0e-6, 1.25, 1.03, "AP64500 VEN_H max 1.25 / VEN_L min 1.03"),
    ("HEAT_EN",     "A U27.6 -> U22 TPS259631 EN/UVLO", 100e3,              -0.1e-6, 1.22, 1.08, "TPS2596 VUVLO(R) max 1.22"),
    ("MON_EN",      "A U27.5 -> U21 TPS259631 EN/UVLO", 100e3,              -0.1e-6, 1.22, 1.08, "TPS2596 VUVLO(R) max 1.22"),
    ("D8_EN",       "A U27.7 -> U23 TPS259631 EN/UVLO", 100e3,              -0.1e-6, 1.22, 1.08, "TPS2596 VUVLO(R) max 1.22"),
    ("POE_EN",      "A U27.8 -> U16 LM5176 EN/UVLO",    1/(1/100e3+1/10e3),  3.0e-6, 1.17, 0.55, "LM5176 VEN(OP) MIN 1.17 (worst for OFF), R75 10k + R114 100k"),
    ("PD_EN",       "A U28.13 -> U19 LM5176 EN/UVLO",   1/(1/100e3+1/10e3),  3.0e-6, 1.17, 0.55, "LM5176 VEN(OP) MIN 1.17 (worst for OFF), R134 10k + R143 100k"),
    ("PA_SW_EN",    "A U27.9 -> U26 LVC08 1B",          100e3,               5.0e-6, 2.0, 0.8,  "LVC08 VIH 2.0 / VIL 0.8"),
    ("HF_SW_EN",    "A U27.10 -> U26 LVC08 2B",         100e3,               5.0e-6, 2.0, 0.8,  "LVC08 VIH 2.0 / VIL 0.8"),
    ("CHG_INHIBIT", "A U27.4 -> Q6 2N7002 gate",        100e3,               0.0,    2.5, 1.0,  "2N7002 Vth 1.0 / 1.6 / 2.5"),
]

def main():
    out = []
    out.append("VCC (A +3V3) = %.3f V" % VCC)
    out.append("")
    for name, where, rd, isrc, von, voff, thr in LINES:
        out.append("%s  (%s), Rd_eff %.2fk, pin source %+.1f uA; %s" % (name, where, rd / 1e3, isrc * 1e6, thr))
        for lab, rpu in RPU:
            v = node(rpu, rd, isrc)
            state = "ON" if v >= von else ("OFF" if v <= voff else "UNDEFINED")
            out.append("   Rpu %-44s V = %.3f V  -> %s" % (lab, v, state))
        rb_on = rpu_break(rd, von, isrc)
        rb_off = rpu_break(rd, voff, isrc)
        out.append("   guaranteed ON needs Rpu <= %s; OFF needs Rpu >= %s" % (
            "%.0fk" % (rb_on / 1e3) if rb_on != float("inf") else "any",
            "%.0fk" % (rb_off / 1e3) if rb_off != float("inf") else "any"))
        out.append("")
    # DEV_EN with the AP64500's typical source and after turn-on (hysteresis current)
    out.append("DEV_EN typical: Rpu 100k, IEN 1.5 uA -> %.3f V; after turn-on IEN 5.5 uA -> %.3f V" % (
        node(100e3, 100e3, 1.5e-6), node(100e3, 100e3, 5.5e-6)))
    out.append("DEV_EN typical: Rpu 82k,  IEN 1.5 uA -> %.3f V" % node(82.3e3, 100e3, 1.5e-6))
    out.append("DEV_EN with U27 unpowered (+3V3 off, rail at 0 V through its loads): IEN 1..2 uA x (100k || 100k) = %.3f..%.3f V" % (
        1e-6 * 50e3, 2e-6 * 50e3))
    out.append("DEV_EN if a PCA9535 (no pull-up) were fitted and R42 kept: IEN 1..2 uA x 100k = %.2f..%.2f V < VEN_L 1.03 V: deadlock" % (0.1, 0.2))
    out.append("DEV_EN fix R42 100k to +3V3 instead of GND: V = VCC = %.2f V (any Rpu), >> 1.25 V" % VCC)
    out.append("DEV_EN fix with +3V3 off: IEN 2 uA x (R42 100k + R48/R49 41.6k to GND) = %.2f V < 1.03 V" % (2e-6 * 141.6e3))
    out.append("")
    # proposed 4.7k pull-downs, worst case pull-up (IIL bound) and current-source bound
    for rd in (10e3, 4.7e3):
        out.append("pull-down %.1fk: resistive worst (Rpu 33.3k) %.3f V; current-source worst (100 uA) %.3f V; drive cost %.2f mA" % (
            rd / 1e3, node(VCC / 100e-6, rd, 5e-6), 100e-6 * rd + 5e-6 * rd, VCC / rd * 1e3))
    out.append("")
    # eFuse OVLO trip on the VBAT-fed eFuses: R 100k / 10k (gen_sch_a.py:526)
    for vth, lab in ((1.17, "min"), (1.20, "typ"), (1.22, "max")):
        out.append("U21/U22 OVLO trips at VBAT = %.2f V (VOVLO(R) %s %.2f V, 100k/10k)" % (vth * 11, lab, vth))
    for vth, lab in ((1.08, "min"), (1.10, "typ"), (1.13, "max")):
        out.append("U21/U22 OVLO releases below VBAT = %.2f V (VOVLO(F) %s %.2f V)" % (vth * 11, lab, vth))
    out.append("VBAT declared 14.4 V nominal, v_work 16.8 V (gen_sch_a.py:28)")
    out.append("U23 (from +5V_DEV 5.1 V): OVLO pin = %.3f V (recommended range 0.5 to 2 V)" % (5.1 / 11))
    for rt in (143e3,):
        r = rt / 10e3
        out.append("proposal %.0fk/10k: trip %.1f to %.1f V, release %.1f to %.1f V" % (rt / 1e3, 1.17 * (1 + r), 1.22 * (1 + r), 1.08 * (1 + r), 1.13 * (1 + r)))
    out.append("")
    # LM5176 divider as F-SQ-04 would restore it: 62k over 10k from a 3.3 V logic line
    out.append("F-SQ-04 divider restored literally (62k over 10k from a 3.328 V logic high): EN/UVLO = %.3f V < VEN(OP) min 1.17 V: stage never runs" % (VCC * 10 / 72))
    print("\n".join(out))

if __name__ == "__main__":
    main()
