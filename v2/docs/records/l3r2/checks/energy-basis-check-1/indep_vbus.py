#!/usr/bin/env python3
"""indep_vbus.py: the checker's own arithmetic of VBUS20's worst-case stack (CHECK-1, an AI check). Figures typed from the
pages read by the checker: SNVSAI1D p.6 (VREF 0.788/0.800/0.812 V, IBIAS(FB) 25 nA max, gm 1.31 mS and ROUT 20 MOhm typical,
VCC 7.88 V max), p.7 (VSNS 43/50/57 mV); YAGEO RC_L V.12 p.5 and UNI-ROYAL p.6 (100 ppm/K, t1 +25 C); YAGEO p.8 and
UNI-ROYAL p.7 (endurance +-(1 % + 0.05 Ohm)); the netlist (R6 240k, R7 10k, R11 10 mOhm); pcb_envelope.yaml (-20 C, 62.1 C,
13.16 to 35.58 K); the DRcalc T2m (13.23 to 18.33 C)."""
R6, R7 = 240e3, 10e3
VREF = (0.788, 0.800, 0.812)
IB, A, VCC = 25e-9, 1.31e-3 * 20e6, 7.88


def stack(dt, tol=0.01, tcr=100e-6, drift=0.0, ib=IB, gain=True):
    d = tol + tcr * dt + drift
    reg = VCC / A * (1 + R6 / R7) if gain else 0.0
    lo = VREF[0] * (1 + R6 * (1 - d) / (R7 * (1 + d))) - ib * R6 * (1 + d) - reg
    hi = VREF[2] * (1 + R6 * (1 + d) / (R7 * (1 - d))) + ib * R6 * (1 + d) + reg
    return lo, hi


print("nominal %.4f V" % (VREF[1] * (1 + R6 / R7)))
print("printed only (VREF, 1 %%): %.4f to %.4f V" % stack(0, tcr=0, ib=0, gain=False))
dt_env = max(abs(-20 - 25), abs(62.1 - 25))
dt_m1 = max(abs(13.23 + 13.16 - 25), abs(18.33 + 35.58 - 25))
print("envelope (dT %.2f K): %.4f to %.4f V" % ((dt_env,) + stack(dt_env)))
print("M1 day (dT %.2f K): %.4f to %.4f V" % ((dt_m1,) + stack(dt_m1)))
print("amplifier term %.2f mV, IBIAS term %.2f mV" % (VCC / A * 25 * 1e3, IB * R6 * 1e3))
print("envelope + a 20 K board rise (dT %.1f K): %.4f V min" % (dt_env + 20, stack(dt_env + 20)[0]))
print("envelope + the endurance limits (+-1 %% more, opposite): %.4f to %.4f V" % stack(dt_env, drift=0.01))
for r11 in (0.010, 0.0062):
    print("R11 %.1f mOhm: ISNS loop %.3f / %.3f / %.3f A" % ((r11 * 1e3,) + tuple(v / r11 for v in (0.043, 0.050, 0.057))))
