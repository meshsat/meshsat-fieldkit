#!/usr/bin/env python3
"""The PCM2912A's supply floor on board D behind U41, U23 and the two drop budgets (stream s99a, check fix 1).

AI engineering arithmetic, prototype design (nothing built or measured). Positive quantities are volts and amperes.
Chain: U41's regulation point (+5V_D8IN at its divider) -> +5V_D8IN copper (declared budget 2 percent of 5.0 V) ->
U23's pass FET (RON x I) -> +5V_D8 copper on boards A and D (declared budget 6 percent of 5.0 V, shared) -> the codec.
Sources: U41's DC set-point minimum from u41_divider.py (SLUSEA4D p.6); U23's RON from TI SLVSET8A (revised August
2019) printed p.7, VIN > 4 V, IOUT 0.2 A: 89 mOhm typical and 92.6 mOhm maximum at 25 C, 115.3 mOhm maximum over
-40 to 85 C, 131 mOhm maximum over -40 to 125 C; PCM2912A VBUS 4.35 V minimum (SLES230A 7.3 p.5); budgets from
gen_sch_a.py (+5V_D8IN budget=0.02) and both boards' +5V_D8 (budget=0.06). dc_drop judges a budget at the rail's
TYPICAL current (dc_drop.py lines 258 to 264), so two readings at the 2.0 A peak: (i) each budget read as a fixed
voltage bar, (ii) each budget spent in full at the 1.0 A typical, a resistive drop that doubles at 2.0 A.
The pre-split source is board A's LM5176 stage: VREF 0.788 V minimum (SNVSAI1D p.5), 53.6k over 10k at 1 percent,
100 ppm/C over 65 K (the checker's figure, reproduced here). Writes nothing.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("u41", Path(__file__).with_name("u41_divider.py"))
u41 = importlib.util.module_from_spec(_s); _s.loader.exec_module(u41)

VMIN_U41 = u41.band(56.2e3, 10.7e3, 0.001, 25e-6, u41.VFB["-40-150C"], tc=True)[0]
_d = 0.01 + 100e-6 * 65
VMIN_OLD = 0.788 * (1 + 53.6e3 * (1 - _d) / (10e3 * (1 + _d)))
RON = (("typ 25 C", 0.089), ("max 25 C", 0.0926), ("max -40..85 C", 0.1153), ("max -40..125 C", 0.131))
B_IN, B_D8, I_TYP, CODEC = 0.02 * 5.0, 0.06 * 5.0, 1.0, 4.35


def floor(vsrc, i, ron, b_in, b_d8, scale):
    k = (i / I_TYP) if scale else 1.0
    return vsrc - b_in * k - ron * i - b_d8 * k


def main():
    print("U41 DC set-point minimum %.6f V (u41_divider.py); pre-split LM5176 minimum %.6f V" % (VMIN_U41, VMIN_OLD))
    print("%-7s %-15s %-34s %9s %9s" % ("I (A)", "U23 RON", "budgets", "codec V", "margin V"))
    for i in (1.0, 1.59, 2.0):
        for rn, r in RON:
            for lab, b_in, scale in (("6% only, bars", 0.0, False), ("6% + D8IN 2%, bars", B_IN, False),
                                     ("6% + D8IN 0.5%, bars", 0.025, False), ("6% + D8IN 2%, scaled from 1 A", B_IN, True)):
                if i == 1.0 and scale: continue
                v = floor(VMIN_U41, i, r, b_in, B_D8, scale)
                print("%-7.2f %-15s %-34s %9.4f %+9.4f" % (i, rn, lab, v, v - CODEC))
    print()
    for rn, r in RON[2:]:
        v = floor(VMIN_OLD, 2.0, r, 0.0, B_D8, False)
        print("PRE-SPLIT 2.00 A, U23 RON %s, 6%% bar only: codec %.4f V, margin %+.4f V" % (rn, v, v - CODEC))
    top = 5.23; ratio = 5.1329 / 4.8718
    print("OPTION raise U41 so its top is 5.23 V (same 0.1 percent class, band ratio %.4f): bottom %.4f V" % (ratio, top / ratio))
    vlo = u41.band(53.6e3, 10e3, 0.001, 25e-6, u41.VFB["-40-150C"], tc=True)[0]
    for rn, r in RON[2:]:
        for b_in in (0.025, B_IN):
            v = floor(vlo, 2.0, r, b_in, B_D8, False)
            print("OPTION 53.6k/10k 0.1%% (bottom %.4f V), 2.00 A, RON %s, D8IN %.3f V bar: codec %.4f V, margin %+.4f V"
                  % (vlo, rn, b_in, v, v - CODEC))


if __name__ == "__main__":
    main()
