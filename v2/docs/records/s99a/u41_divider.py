#!/usr/bin/env python3
"""U41 (TPS62933, board A, +5V_D8IN) output band for candidate feedback dividers: stream s99a item 4.

AI engineering arithmetic, prototype design (nothing built or measured). Sources, all held:
  TI SLUSEA4D (June 2021, revised August 2022), v2/vendor/ti/ti-tps62933.pdf, printed p.6, 8.5: VFB 792/800/808 mV at
  TJ 25 C, 788/812 mV at 0 to 85 C, 784/800/816 mV at TJ -40 to 150 C; IFB 0.15 uA maximum at VFB 0.8 V (no sign given,
  so it is applied in both directions through the top resistor).
  Resistors: 1 percent UNI-ROYAL 0603WAF, 100 ppm/C (board D's U23 comment, C25803/C25804 read back from JLC);
  0.1 percent YAGEO RT0603BRD, 25 ppm/C (board D's R80/R81, C705784 and C861078, JLC-CERTIFIED.tsv). The 65 K
  excursion is board D's convention for the same arithmetic (gen_sch_d.py, the U23 OVLO comment).
Board D's window: v_work 5.23 V on +5V_D8 (gen_sch_d.py line 56) and the 4.90 V source worst case both boards' +5V_D8
notes assume (a 2 percent source tolerance). Board D's tightest consumer: PCM2912A VBUS 4.35 to 5.25 V recommended
(SLES230A, revised August 2015, 7.3 p.5), behind the 6 percent (0.300 V) drop budget.
Output positive, volts; Vout = VFB * (1 + Rt/Rb) + s * IFB * Rt, s in {-1, +1}.
"""
VFB = {"25C": (0.792, 0.808), "0-85C": (0.788, 0.812), "-40-150C": (0.784, 0.816)}
IFB = 0.15e-6
DT = 65.0
CANDS = [
    ("draft 53.6k/10k 1% 100ppm (C23074, 10k)", 53.6e3, 10e3, 0.01, 100e-6, "both certified on board A"),
    ("52.3k/10k 1% 100ppm", 52.3e3, 10e3, 0.01, 100e-6, "52.3k not certified in JLC-CERTIFIED.tsv"),
    ("53.6k/10k 0.1% 25ppm", 53.6e3, 10e3, 0.001, 25e-6, "neither value certified at 0.1 percent"),
    ("56.2k/10.7k 0.1% 25ppm (C705784, C861078)", 56.2e3, 10.7e3, 0.001, 25e-6, "both certified (board D's R80, R81)"),
]


def band(rt, rb, tol, tcr, vfb, tc=True):
    d = tol + (tcr * DT if tc else 0.0)
    kmax = rt * (1 + d) / (rb * (1 - d)); kmin = rt * (1 - d) / (rb * (1 + d))
    vmax = vfb[1] * (1 + kmax) + IFB * rt * (1 + d)
    vmin = vfb[0] * (1 + kmin) - IFB * rt * (1 + d)
    return vmin, vmax


def main():
    print("U41 output band, TJ -40 to 150 C reference (784 to 816 mV), IFB +/-0.15 uA through the top resistor")
    print("%-44s %8s %8s %8s %8s %8s  %s" % ("divider", "nominal", "min", "max", "min+TC", "max+TC", "parts"))
    for name, rt, rb, tol, tcr, parts in CANDS:
        nom = 0.8 * (1 + rt / rb)
        a = band(rt, rb, tol, tcr, VFB["-40-150C"], tc=False); b = band(rt, rb, tol, tcr, VFB["-40-150C"], tc=True)
        print("%-44s %8.4f %8.4f %8.4f %8.4f %8.4f  %s" % (name, nom, a[0], a[1], b[0], b[1], parts))
    print()
    print("Board D window [4.90, 5.23] V: ratio 5.23/4.90 = %.4f" % (5.23 / 4.90))
    r1 = (0.816 / 0.784) * ((1 + 5.36 * 1.01 / 0.99) / (1 + 5.36 * 0.99 / 1.01))
    print("Band ratio of any 1 percent divider near 5 V (reference only, no TC, no IFB): %.4f > window: no 1 percent "
          "divider fits both ends" % r1)
    k_lim = (5.23 / 0.816 - 1) / (1.01 / 0.99)
    print("1 percent divider ratio that keeps the maximum at 5.23 V without TC or IFB: Rt/Rb <= %.5f" % k_lim)
    rt, rb = 56.2e3, 10.7e3
    lo, hi = band(rt, rb, 0.001, 25e-6, VFB["-40-150C"], tc=True)
    print()
    print("CHOSEN 56.2k/10.7k 0.1%%: nominal %.4f V, %.4f to %.4f V; margin to v_work 5.23 V %.4f V; "
          "codec after the 0.300 V budget at the minimum %.4f V, %.4f V over PCM2912A 4.35 V"
          % (0.8 * (1 + rt / rb), lo, hi, 5.23 - hi, lo - 0.300, lo - 0.300 - 4.35))
    print("U23 OVLO pin (40.2k over 10k) in service: %.3f to %.3f V (0.5 to 2 V recommended, SLVSET8A 7.3)"
          % (lo * 10 / 50.2, hi * 10 / 50.2))
    vin = 16.8; L = 6.8e-6; f = 500e3; vo = 0.8 * (1 + rt / rb)
    rip = vo * (1 - vo / vin) / (L * f)
    print("Ripple at 16.8 V in, 500 kHz, 6.8 uH: %.3f A; peak at 2.0 A: %.3f A (IHS_LIMIT 4.2 A minimum, p.6); "
          "L at -20 percent: %.3f A" % (rip, 2.0 + rip / 2, 2.0 + rip / 2 / 0.8))
    print("U41 VBAT share at 1.0 A (declared typical), 0.90 (project efficiency), 14.4 V: %.6f A" % (1.0 * vo / (0.9 * 14.4)))


if __name__ == "__main__":
    main()
