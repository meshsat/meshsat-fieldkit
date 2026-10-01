#!/usr/bin/env python3
"""Board A round 4 fix-up (MESHSAT-1357, 26 September 2026, review A blocking item 2): the LM5176 stages' voltage
loops, one compensation design per stage, and the local bulk each stage needs for it.

QUESTION: which Rc1 / Cc1 / Cc2, and how many local hybrid-polymer bulk capacitors (0 to 3 x Panasonic
EEHZK1V101XP, 100 uF 35 V, the part board E already carries), give each of board A's seven LM5176 stages a stable
voltage loop over its input range, its load range, the DC-bias band of its ceramics and the lead and remote
capacitance it drives, with a bounded output impedance; and what did the helper's single set (10 k, 10 nF,
100 pF) give?

SOURCE of every controller constant: TI SNVSAI1D (August 2021), v2/vendor/ti/lm5176-datasheet.pdf.
  gmEA 1.31 mS, EA output resistance 20 MOhm (6.5); ACS = 5 (7.2 block diagram, Eq. 26, Eq. 44);
  Fsw from Eq. 5: RT = (1/Fsw - 190 ns) / 116 pF, so RT 40.2 k is 206 kHz; fSW(1) 175 / 200 / 225 kHz at 40 k
  gives the band 180 to 232 kHz used here; the adaptive slope (7.3.x, SLOPE pin) keeps the current loop near
  dead-beat at any VIN and VOUT.
  8.2.2.14: boost output pole 2/(R C) (Eq. 38), RHP zero R (1-D)^2 / L (Eq. 40), buck output pole 1/(R C) (Eq. 41),
  "the crossover frequency should be less than 1/3 of the RHP zero frequency", and "compare the limits posed by
  the RHP zero (fRHP / 3) with 1/20 of the switching frequency and use the smaller of the two values as the
  achievable bandwidth"; Rc1 from Eq. 44; Cc2's pole "at seven to ten times of fbw" (Eq. 46 text).
  The model is the one Eq. 44 is the high-frequency asymptote of:
    buck:  i_c = v_comp / Ri * H(s)                       (Ri = ACS * RSENSE)
    boost: i_c = v_comp * (1-D) / Ri * (1 - s/wRHP) * H(s), with the load at R/2 (Eq. 38's pole)
    H(s): the current loop's sampling double pole at Fsw/2, Q 0.4 to 0.8 (dead-beat slope gives 2/pi = 0.64; this
    board's CSLOPE values sit 14 to 18 percent under dead-beat, Eq. 26, which lowers Q; 0.8 is margin).
    The output network is two nodes: the LOCAL node (the stage's ceramics, its local bulk if any, and the FB
    divider) and the REMOTE node (the lead's far end: the remote capacitance and the load), joined by the lead
    (R + sL). With no remote the load sits on the local node.
    T = RFB1/(RFB1+RFB2) * gmEA * Zc(s) * Gc(s) * Z_ll(s),   Zc = (Rc1 + 1/sCc1) || 1/sCc2 || 20 MOhm.
  VALIDATION: the same code run on TI's own worked example (8.2.1: 6 to 50 V in, 12 V, 6 A, L 4.7 uH, RSENSE
  8 mOhm, Rc1 10 k, Cc1 33 nF, Cc2 560 pF, COUT 412 uF, the value Eq. 44's 9.49 k implies) must give the 4 kHz
  boost crossover TI designed for, with positive margins; the script refuses to design anything if it does not.

Verdict per design: the worst case over every corner of: phase margin at every unity-gain crossing, gain margin
at every -180 degree crossing, the modulus margin min|1 + T|, the crossover against TI's two ceilings
(Fsw/20 at the nominal 206 kHz, and fRHP/3 at each boost corner), and the peak dynamic output impedance at the
load (the closed-loop impedance at the remote node less the lead's DC resistance, which is a wiring drop that
dc_drop judges, not a loop property).
PASS: PM >= 50 deg, GM >= 10 dB, modulus margin >= 0.5, every crossover under both TI ceilings, Cc2's pole at or
under Fsw/2 and at least 3 x the zero, and the output-impedance peak under the stage's bound. The bound is a
SESSION design target, stated per stage below: a 5 percent dynamic droop for the stage's declared load step,
and, where the load is a switching converter (a constant-power load), a third of its input impedance magnitude
V^2/P (Middlebrook's source-load criterion with 10 dB of separation). The smaller governs.
Among the passing sets for the smallest bulk count that passes, the one with the highest WORST-CASE (lowest)
crossover is taken, then the highest phase margin.
This is a paper design; TI's own words (8.2.2.14): "Each design should be tuned in the lab". Every capacitance
band below is an EFFECTIVE value (DC bias and temperature) and INFERRED: no maker DC-bias curve for these
ceramics is held.
Run: python3 loop_design.py [stage ...]  (numpy; minutes; run it on the KiCad box, not the shared runner).
"""
import itertools, json, math, sys
import numpy as np

GM = 1.31e-3; RO_EA = 20e6; ACS = 5.0
def fsw_of(rt): return 1.0 / (rt * 116e-12 + 190e-9)
FSW = fsw_of(40.2e3)                   # 206 kHz nominal (Eq. 5)
FSW_LO = FSW * 175.0 / 200.0           # fSW(1) minimum, scaled: 180 kHz
FSW_HI = FSW * 225.0 / 200.0           # fSW(1) maximum, scaled: 232 kHz
FC_CEIL = FSW / 20.0                   # TI 8.2.2.14: 1/20 of the switching frequency, 10.3 kHz
F = np.logspace(1, math.log10(FSW_HI / 2), 1100)
S = 2j * np.pi * F

# The E6/E12 values searched. Every one chosen is then read back from the JLCPCB parts API (drafts/jlc/).
R_VALUES = [330, 470, 680, 1000, 1500, 2200, 3300, 4700, 6800, 10000, 15000, 22000]
C1_VALUES = [2.2e-9, 3.3e-9, 4.7e-9, 6.8e-9, 10e-9, 15e-9, 22e-9, 33e-9, 47e-9, 68e-9, 100e-9, 150e-9, 220e-9, 470e-9]
C2_VALUES = [47e-12, 100e-12, 150e-12, 220e-12, 330e-12, 470e-12, 680e-12, 1e-9, 1.5e-9, 2.2e-9, 3.3e-9, 4.7e-9]

# Panasonic EEHZK1V101XP (v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf, ZK series table): 100 uF +-20 percent,
# 35 V, ESR 35 mOhm maximum at 100 kHz and +20 C, "ESR <= 200 % of the initial limit" after endurance. Hybrid
# polymer: no DC-bias loss. Corners per capacitor: 80 and 120 uF, 10 mOhm (a good part, least damping) and
# 70 mOhm (end of life, the 200 percent limit).
BULK_C = (80e-6, 120e-6); BULK_ESR = (0.010, 0.070)

def zcap(c, esr): return 1.0 / (S * c) + esr

def two_node(case):
    """Z_ll, Z_lr, Z_rr of the output network (local node l, remote node r) and the lead's DC resistance.
    Local: ceramics (C, ESR) || n x bulk (C, ESR) || nothing else. Remote: caps (C, ESR) || the load.
    The load is R (buck) or R/2 (boost, Eq. 38's small-signal output pole)."""
    rload = case["vout"] / case["iout"] * (0.5 if case["mode"] == "boost" else 1.0)
    yl = 1.0 / zcap(case["cl"], case["esr_l"])
    if case["nbulk"]:
        yl = yl + case["nbulk"] / zcap(case["cb"], case["esr_b"])
    if not case.get("cr"):
        yl = yl + 1.0 / rload
        z = 1.0 / yl
        return z, z, z, 0.0
    yr = 1.0 / zcap(case["cr"], case["esr_r"]) + 1.0 / rload
    zlead = case["rlead"] + S * case["llead"]
    yld = 1.0 / zlead
    det = (yl + yld) * (yr + yld) - yld * yld
    return (yr + yld) / det, yld / det, (yl + yld) / det, case["rlead"]

def loop_parts(st, case):
    """gv = kfb * gm * g * Gc(s) * Z_ll(s): everything but the compensation impedance; and the pieces the
    output impedance at the load needs."""
    ri = ACS * st["rcs"]
    wn = np.pi * case["fsw"]; q = case["q"]
    h = 1.0 / (1 + S / (wn * q) + (S / wn) ** 2)
    zll, zlr, zrr, rl = two_node(case)
    if case["mode"] == "buck":
        gc = h / ri
    else:
        d = 1 - case["vin"] / case["vout"]
        r = case["vout"] / case["iout"]
        wrhp = r * (1 - d) ** 2 / st["L"]
        gc = (1 - d) / ri * (1 - S / wrhp) * h
    gv = case["kfb"] * GM * case["g"] * gc * zll
    return gv, zll, zlr, zrr, rl

def zc(rc1, cc1, cc2):
    return 1.0 / (1.0 / (rc1 + 1.0 / (S * cc1)) + S * cc2 + 1.0 / RO_EA)

def margins(t):
    """t: (cases, freqs). PM at every unity crossing, GM at every -180/-540 crossing, the modulus margin, and each
    case's lowest and highest crossover."""
    mag = np.abs(t); ph = np.unwrap(np.angle(t), axis=1) * 180 / np.pi
    ph = ph - 360 * np.round((ph[:, :1] + 90) / 360)      # the integrator: low-frequency phase on the -90 branch
    x = (mag[:, :-1] - 1) * (mag[:, 1:] - 1) <= 0
    pm = float(np.min(np.where(x, 180 + ph[:, :-1], 999.0)))
    fgrid = np.broadcast_to(F[:-1], x.shape)
    fc_hi_each = np.max(np.where(x, fgrid, 0.0), axis=1)
    fc_lo_each = np.min(np.where(x, fgrid, 1e12), axis=1)
    gm_db = 999.0
    for k in (-180.0, -540.0):
        y = (ph[:, :-1] - k) * (ph[:, 1:] - k) <= 0
        if y.any():
            gm_db = min(gm_db, float(np.min(np.where(y, -20 * np.log10(np.maximum(mag[:, :-1], 1e-12)), 999.0))))
    mm = float(np.min(np.abs(1 + t)))
    return dict(pm=pm, gm=gm_db, mm=mm, fc_lo=float(np.min(fc_lo_each)), fc_hi=float(np.max(fc_hi_each)),
                fc_hi_each=fc_hi_each)

def corners(st, nbulk):
    out = []
    bulk = [(None, None)] if nbulk == 0 else list(itertools.product(BULK_C, BULK_ESR))
    for mode, vin in st["modes"]:
        for vout, kfb in st["vouts"]:
            if mode == "boost" and vin >= vout: continue
            if mode == "buck" and vin <= vout: continue
            for cl in st["cl"]:
                for rem in st["remote"]:
                    for iout in st["iout"]:
                        for q in (0.4, 0.8):
                            for fsw in (FSW_LO, FSW_HI):
                                for g in (0.8, 1.2):
                                    for cb, eb in bulk:
                                        c = dict(mode=mode, vin=vin, vout=vout, kfb=kfb, cl=cl, esr_l=st["esr_l"], iout=iout,
                                                 q=q, fsw=fsw, g=g, nbulk=nbulk, cb=cb, esr_b=eb)
                                        c.update(rem)
                                        out.append(c)
    return out

class Stage:
    def __init__(self, st, nbulk):
        self.st = st; self.cases = corners(st, nbulk)
        parts = [loop_parts(st, c) for c in self.cases]
        self.gv = np.array([p[0] for p in parts]); self.zll = np.array([p[1] for p in parts])
        self.zlr = np.array([p[2] for p in parts]); self.zrr = np.array([p[3] for p in parts])
        self.rl = np.array([p[4] for p in parts])[:, None]
        self.zmax = np.array([st["zmax"](c) for c in self.cases])
        self.rhp3 = np.array([self._rhp3(c) for c in self.cases])
    def _rhp3(self, c):
        if c["mode"] != "boost": return 1e12
        d = 1 - c["vin"] / c["vout"]; r = c["vout"] / c["iout"]
        return r * (1 - d) ** 2 / self.st["L"] / (2 * np.pi) / 3.0
    def evaluate(self, rc1, cc1, cc2, full=False):
        t = self.gv * zc(rc1, cc1, cc2)[None, :]
        w = margins(t)
        w["ceiling_ok"] = bool(np.all(w["fc_hi_each"] <= np.minimum(FC_CEIL, self.rhp3)))
        # dynamic output impedance at the load: Z_rr - Z_rl Z_lr / Z_ll * T/(1+T), less the lead's DC resistance
        zo = self.zrr - self.zlr * self.zlr / self.zll * (t / (1 + t))
        dyn = np.abs(zo - self.rl)
        w["zout_ratio"] = float(np.max(np.max(dyn, axis=1) / self.zmax))
        w["zout_peak_mohm"] = float(np.max(dyn)) * 1e3
        if not full: del w["fc_hi_each"]
        else: w["fc_hi_each"] = None
        return w

def ok(w):
    return w["pm"] >= 50 and w["gm"] >= 10 and w["mm"] >= 0.5 and w["ceiling_ok"] and w["zout_ratio"] <= 1.0

def fb(top, bot=10e3): return 0.8 * (1 + top / bot), bot / (top + bot)
LEAD_150 = [dict(llead=0.08e-6, rlead=0.008), dict(llead=0.3e-6, rlead=0.04)]   # 16 AWG pair, 150 mm, JST-VH both ends
LEAD_300 = [dict(llead=0.15e-6, rlead=0.015), dict(llead=0.5e-6, rlead=0.06)]
def remotes(leads, crs, esr=0.002, absent=True):
    out = [dict()] if absent else []
    for ld in leads:
        for cr in crs:
            d = dict(ld); d.update(cr=cr, esr_r=esr); out.append(d)
    return out
def zbound(step_a, p_w=None):
    """the session's output-impedance bound: 5 percent of VOUT over the load step, and V^2/P / 3 for a
    constant-power (switching converter) load of P watts at that output"""
    def f(c):
        b = 0.05 * c["vout"] / step_a
        if p_w: b = min(b, c["vout"] ** 2 / p_w / 3.0)
        return b
    return f

# ---- the seven stages (gen_sch_a.py, the lm5176() calls; capacitances EFFECTIVE, INFERRED bands) --------------
STAGES = {
 # FE: VIN_RAW 9 to 36 V -> VBUS20 (240k/10k), 5 A; local 3 x 10u 50 V at 20 V: 4 to 7 uF each; the charger's
 # C20-C22 (3 x 10u 35 V, 4 to 6 uF each at 20 V) behind R16 (10 mOhm) and board copper. Load: the BQ25731,
 # a switching charger, 100 W at most (5 A x 20 V): constant power. Step 5 A.
 "FE": dict(L=10e-6, rcs=0.005, vouts=[fb(240e3)], modes=[("boost", 9.0), ("buck", 36.0), ("buck", 24.0)],
            cl=[12e-6, 21e-6], esr_l=0.002, iout=[5.0, 0.25],
            remote=[dict(llead=0.02e-6, rlead=0.012, cr=12e-6, esr_r=0.002), dict(llead=0.02e-6, rlead=0.012, cr=18e-6, esr_r=0.002)],
            zmax=zbound(5.0, 100.0), bulk_ok=True),
 # S2: VBAT 10 to 16.8 V -> 5.09 V (53.6k/10k), 5.8 A burst; local 3 x 22u 25 V at 5.1 V: 11 to 19 uF each;
 # board B's slot bulk across the 150 mm lead: 4 x 100u 10 V 1206 + 4 x 10u and the three bucks' inputs,
 # 120 to 300 uF effective at 5 V (gen_sch_b.py C(1)..C(8)), or absent. Load: board B's bucks (constant power),
 # 29.5 W; step 3 A (a 5G burst, INFERRED).
 "S2": dict(L=6.8e-6, rcs=0.005, vouts=[fb(53.6e3)], modes=[("buck", 16.8), ("buck", 10.0)],
            cl=[33e-6, 57e-6], esr_l=0.002, iout=[5.8, 0.3],
            remote=remotes(LEAD_150, [120e-6, 300e-6]), zmax=zbound(3.0, 29.5), bulk_ok=True),
 # SD: the same stage into the device rail; board B's C1, C2 (100u 10 V), C4 and the downstream inputs,
 # 60 to 200 uF effective, plus the D8 mezzanine and the Glenair port on board A. 35 W; step 3 A.
 "SD": dict(L=6.8e-6, rcs=0.005, vouts=[fb(53.6e3)], modes=[("buck", 16.8), ("buck", 10.0)],
            cl=[33e-6, 57e-6], esr_l=0.002, iout=[6.9, 0.3],
            remote=remotes(LEAD_150, [60e-6, 200e-6]), zmax=zbound(3.0, 35.0), bulk_ok=True),
 # PA: VBAT -> 13.76 V (162k/10k), 6 A; local 3 x 10u 50 V at 13.8 V: 5 to 8 uF each; the RA30H1317M1's own
 # decoupling on the plate (not held: 0 to 100 uF) across the 300 mm lead. Load: an RF power module (not a
 # converter); step 5.4 A (key-up of a 30 W carrier at 40 percent).
 "PA": dict(L=6.8e-6, rcs=0.005, vouts=[fb(162e3)], modes=[("boost", 10.0), ("boost", 12.0), ("buck", 16.8)],
            cl=[15e-6, 24e-6], esr_l=0.002, iout=[6.0, 0.3],
            remote=remotes(LEAD_300, [10e-6, 100e-6], esr=0.01), zmax=zbound(5.4), bulk_ok=True),
 # HF: VBAT -> 12.0 V (140k/10k), 2 A; local as PA at 12 V; the QMX's input (not held: 0 to 100 uF) across the lid
 # harness (300 mm to 1 m). Load: a transceiver with its own regulators, 24 W; step 2 A.
 "HF": dict(L=6.8e-6, rcs=0.005, vouts=[fb(140e3)], modes=[("boost", 10.0), ("buck", 16.8)],
            cl=[15e-6, 25e-6], esr_l=0.002, iout=[2.0, 0.1],
            remote=remotes([dict(llead=0.15e-6, rlead=0.015), dict(llead=1.0e-6, rlead=0.12)], [10e-6, 100e-6], esr=0.01),
            zmax=zbound(2.0, 24.0), bulk_ok=True),
 # POE: VBAT -> 54.0 V (665k/10k), 0.6 A, boost only, RCS 10 mOhm, 22 uH; local 3 x 10u 100 V at 54 V: 2.5 to 5 uF
 # each; board B's C35 10u 100 V (2.5 to 5 uF) across the 150 mm lead. Load: the PSE and a PD's converter, 32 W;
 # step 0.6 A. The 35 V bulk part cannot sit on 54 V.
 "POE": dict(L=22e-6, rcs=0.010, vouts=[fb(665e3)], modes=[("boost", 10.0), ("boost", 16.8)],
             cl=[7.5e-6, 15e-6], esr_l=0.003, iout=[0.6, 0.03],
             remote=remotes(LEAD_150, [2.5e-6, 5e-6], esr=0.003), zmax=zbound(0.6, 32.4), bulk_ok=False),
 # PD: VBAT -> 5.0 / 9.0 / 15.0 V (105k over 20k, 20k||21k, 20k||21k||14k), 3 A; local 3 x 10u 50 V: 6 to 9 uF each;
 # C120 (10u 25 V) behind Q27 and R138, then the sink across a USB-C cable (0.5 to 1.5 uH, 1 to 100 uF). Load: a
 # sink's charger (constant power), 45 W at 15 V, 15 W at 5 V; step 3 A.
 "PD": dict(L=6.8e-6, rcs=0.005, vouts=[(5.0, 0.8 / 5.0), (9.0, 0.8 / 9.0), (15.0, 0.8 / 15.0)],
            modes=[("buck", 16.8), ("buck", 10.0), ("boost", 10.0), ("boost", 12.0)],
            cl=[18e-6, 27e-6], esr_l=0.002, iout=[3.0, 0.1],
            remote=[dict(), dict(llead=0.02e-6, rlead=0.02, cr=6e-6, esr_r=0.003),
                    dict(llead=1.5e-6, rlead=0.15, cr=100e-6, esr_r=0.02), dict(llead=0.5e-6, rlead=0.05, cr=10e-6, esr_r=0.005)],
            zmax=lambda c: min(0.05 * c["vout"] / 3.0, c["vout"] ** 2 / (3.0 * c["vout"]) / 3.0), bulk_ok=True),
}
HELPER = (10e3, 10e-9, 100e-12)   # the single set every stage carried until this round

def validate_ti():
    """TI's worked example (SNVSAI1D 8.2.1 and 8.2.2.14): 6 V in (boost, DMAX 0.5), 12 V, 6 A, 4.7 uH, 8 mOhm,
    Rc1 10 k, Cc1 33 nF, Cc2 560 pF, COUT 412 uF (Eq. 44's 9.49 k for 4 kHz). Nominal corner only."""
    st = dict(L=4.7e-6, rcs=0.008)
    c = dict(mode="boost", vin=6.0, vout=12.0, kfb=10e3 / 150e3, cl=412e-6, esr_l=0.005, iout=6.0, q=0.64,
             fsw=300e3, g=1.0, nbulk=0, cb=None, esr_b=None)
    gv = np.array([loop_parts(st, c)[0]])
    w = margins(gv * zc(10e3, 33e-9, 560e-12)[None, :])
    return {"fc_hz": w["fc_hi"], "pm_deg": w["pm"], "gm_db": w["gm"]}

def design(name, nbulk):
    st = STAGES[name]; sg = Stage(st, nbulk)
    old = sg.evaluate(*HELPER)
    best = None
    for rc1, cc1, cc2 in itertools.product(R_VALUES, C1_VALUES, C2_VALUES):
        fz = 1 / (2 * np.pi * rc1 * cc1); fp2 = 1 / (2 * np.pi * rc1 * cc2)
        if not (fz * 3 < fp2 <= FSW_LO / 2): continue   # TI 8.2.2.14: Cc2's pole attenuates the ripple on COMP
        w = sg.evaluate(rc1, cc1, cc2)
        if not ok(w): continue
        key = (round(w["fc_lo"], -1), round(min(w["pm"], 70), 0), round(min(w["mm"], 0.8), 2))
        if best is None or key > best[0]:
            best = (key, (rc1, cc1, cc2), w)
    return len(sg.cases), old, best

def main():
    only = sys.argv[1:] or list(STAGES)
    v = validate_ti()
    print("TI worked example (expect about 4 kHz, positive margins):", {k: round(x, 1) for k, x in v.items()})
    if not (3.0e3 < v["fc_hz"] < 5.5e3 and v["pm_deg"] > 30 and v["gm_db"] > 6):
        raise SystemExit("the model does not reproduce TI's own worked example; no design is reported")
    report = {"fsw_nominal_hz": FSW, "fsw_band_hz": [FSW_LO, FSW_HI], "fc_ceiling_hz": FC_CEIL, "ti_example": v, "stages": {}}
    for name in only:
        st = STAGES[name]; rep = {"designs": {}}
        for nb in ((0, 1, 2, 3) if st["bulk_ok"] else (0,)):
            n, old, best = design(name, nb)
            rep["designs"][nb] = {"corners": n, "helper_10k_10n_100p": old,
                                  "chosen": None if best is None else {"rc1": best[1][0], "cc1": best[1][1], "cc2": best[1][2], "worst": best[2]}}
            print("%s bulk %d corners %d" % (name, nb, n))
            print("  helper 10k/10n/100p :", {k: (round(x, 2) if isinstance(x, float) else x) for k, x in old.items()})
            if best:
                print("  chosen Rc1 %.0f Cc1 %.3g Cc2 %.3g :" % best[1], {k: (round(x, 2) if isinstance(x, float) else x) for k, x in best[2].items()})
                rep["taken_bulk"] = nb
                break
            print("  NO design in the value set passes with %d bulk" % nb)
        report["stages"][name] = rep
    json.dump(report, open("loop_design.json", "w"), indent=1, default=float)

if __name__ == "__main__":
    main()
