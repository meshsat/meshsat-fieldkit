#!/usr/bin/env python3
"""Board A round 4, second fix-up (MESHSAT-1357, 26 September 2026, re-review of the fix-up, blocking item): the
RMS ripple current in every hybrid-polymer bulk capacitor the LM5176 stages carry, against the maker's rating.

QUESTION: at the worst corner of each stage's operating range, how much ripple current does each local bulk
capacitor carry, and is it at or under the rated ripple current of its part; and for the front end (VBUS20), which
bulk choice passes, counting BOTH currents that node's capacitors supply: the LM5176 FE stage's output switch
current and the BQ25731 charger's input switch current?

SOURCES.
  TI SNVSAI1D (v2/vendor/ti/lm5176-datasheet.pdf) 8.2.2.5 Equation 19: ICOUT(RMS) = IOUT x sqrt(VOUT/VIN - 1) in boost
    mode, the whole output capacitance's ripple; this script computes that total from the switch waveform itself (the
    Equation 19 value is printed beside it as the check) and then splits it harmonic by harmonic between the
    capacitors by their impedances.
  TI SLUSE66A (bq25731.pdf) 10.2.2.4 Equation 4: ICIN = I x sqrt(D (1 - D)), the charger's input capacitor ripple,
    "half of the charging current (plus system current there is any system load) when duty cycle is 0.5"; and
    "Input capacitor ... should be placed in front of RAC current sensing ... Capacitance after RAC before power
    stage half bridge should be limited to 10 nF + 1 nF" (Figure 10-1: 6 x 10 uF before RAC). So the charger's input
    ripple is supplied by the capacitors on VBUS20, the FE stage's output node (R4A-N8 moves C20 to C22 there).
    Charger switching: PWM_FREQ 400 kHz at POR or 800 kHz (Table 9-8; Table 9-4/9-5 pair the 3.3 uH inductor with
    800 kHz); both are corners. L2 3.3 uH (XAL6030-332ME).
  Panasonic ZK series sheet (v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf, 01-Apr-22, Characteristics list):
    rated ripple current (100 kHz, +125 C), ESR maximum (100 kHz, +20 C), capacitance +-20 percent; the frequency
    correction factor is 1.00 from 100 kHz up for C >= 100 uF, so every harmonic here (the lowest is 180 kHz) counts
    at the full rating; "Do not allow an excessively large ripple current (larger than the rated ripple current
    specified in the specifications)", and for parallel parts "use capacitors with the same part number" so the
    current does not concentrate on the low-impedance side. The PASS test is the per-part current at or under the
    rated figure at +125 C, with no uplift for a cooler case (the sheet gives none).

MODEL. Each source is a periodic current waveform built from its topology (boost output: the inductor current during
the off time 1 - D, zero during D; buck output: the inductor current, a triangle; buck input: the inductor current
during D, zero during 1 - D; each with its triangular ripple dIL), decomposed into 60 harmonics. The capacitors are
branches R + jwL + 1/(jwC), one per part. FE's node is a two-node network: VBUS20 (the FE ceramics, the bulk, and
after R4A-N8 the charger's C20 to C22) joined by R16 (10 mOhm) and board inductance to CH_ACN (the half-bridge's
10 nF + 1 nF after R4A-N8; before it, C20 to C22). The FE source injects at VBUS20, the charger source draws at
CH_ACN. Every harmonic of every source is solved separately and each part's RMS is the root of the sum of squares
(the two converters are not synchronised).
INFERRED, not held (each one a corner, the worst taken): ceramic effective capacitance under DC bias (the bands of
loop_design.py), ceramic ESR 2 to 5 mOhm and ESL 0.8 to 1.5 nH per part, polymer ESL 1.5 to 3.5 nH, R16's board
inductance 5 to 20 nH. Bulk corners: C at 0.8 and 1.2 of nominal, ESR at 0.3, 1.0 and 2.0 of the sheet maximum (the
loop model's corners; 0.3 is a good part and draws the largest share).

Run: python3 bulk_ripple.py [--fe-only] [--json out.json]   (numpy; about a minute over every corner; run it on the
KiCad box, not the shared runner).
"""
import itertools, json, math, sys
import numpy as np
import loop_design as LD

NH = 60
RATING_A = {   # ZK series Characteristics list: rated ripple current, mA rms at 100 kHz / +125 C, and the sheet's ESR max
    "V101": (1.700, 0.035), "E151": (1.800, 0.030), "V181": (2.000, 0.027), "E471": (2.800, 0.020), "V331": (2.800, 0.020)}

def harmonics(kind, i_avg, d, dil, n=4096):
    """rms amplitude of harmonics 1..NH of the source waveform. kind: 'boost_out' (IL during 1-D), 'buck_out'
    (IL always), 'buck_in' (IL during D). i_avg is the INDUCTOR's average current; d the high-side (buck) or
    low-side (boost) duty; dil the peak-to-peak inductor ripple."""
    t = (np.arange(n) + 0.5) / n
    rise = t < d
    il = np.where(rise, i_avg - dil / 2 + dil * t / d, i_avg + dil / 2 - dil * (t - d) / (1 - d))
    if kind == "boost_out":
        i = np.where(rise, 0.0, il)
    elif kind == "buck_out":
        i = il
    elif kind == "buck_in":
        i = np.where(rise, il, 0.0)
    else:
        raise ValueError(kind)
    c = np.fft.rfft(i) / n
    amps = 2 * np.abs(c[1:NH + 1]) / math.sqrt(2)
    ac = float(np.sqrt(np.mean((i - i.mean()) ** 2)))
    return amps, ac

def z_part(w, c, esr, esl):
    return esr + 1j * w * esl + 1.0 / (1j * w * c)

def split_two_node(w, a_parts, b_parts, zab, inj_a, inj_b):
    """node a (VBUS20) with parts a_parts, node b (CH_ACN) with parts b_parts, joined by zab; a current inj_a into a
    and inj_b into b (complex, per harmonic). Returns per-part currents (lists) for a and b."""
    ya = sum(1.0 / z_part(w, *p) for p in a_parts)
    yb = sum(1.0 / z_part(w, *p) for p in b_parts) if b_parts else 0.0
    yab = 1.0 / zab
    det = (ya + yab) * (yb + yab) - yab * yab
    va = ((yb + yab) * inj_a + yab * inj_b) / det
    vb = (yab * inj_a + (ya + yab) * inj_b) / det
    return [va / z_part(w, *p) for p in a_parts], [vb / z_part(w, *p) for p in b_parts]

def fe_case(vin, iout, fsw, vbat, fch, bulk_key, nbulk, cb_k, esr_k, esl_b, cer_c, cer_esr, cer_esl, l16, topology="fixed", mismatch=False):
    """per-part RMS currents on the FE node. topology 'fixed' (R4A-N8: C20-C22 on VBUS20, 10 nF + 1 nF at CH_ACN) or
    'as_built' (C20-C22 on CH_ACN behind R16, the fix-up's netlist). Returns a dict of part -> A rms."""
    vout = 20.0
    c_nom, esr_max = LD.BULK_PARTS[bulk_key]["c"], LD.BULK_PARTS[bulk_key]["esr"]
    bulk = []
    for k in range(nbulk):
        e = esr_max * (esr_k if (k == 0 or not mismatch) else 1.0)
        bulk.append((c_nom * cb_k, e, esl_b))
    fe_cer = [(cer_c[0], cer_esr, cer_esl)] * 3          # the FE stage's own three 10u 50V (C13 to C15)
    ch_cer = [(cer_c[1], cer_esr, cer_esl)] * 3          # the charger's C20 to C22, 10u 35V
    hf = [(10e-9, 0.02, 0.5e-9), (1e-9, 0.05, 0.5e-9)]   # TI Figure 10-3's 10 nF + 1 nF at the half bridge
    if topology == "fixed":
        a_parts = bulk + fe_cer + ch_cer; b_parts = hf
    else:
        a_parts = bulk + fe_cer; b_parts = ch_cer
    names_a = ["bulk%d" % k for k in range(nbulk)] + ["fe_cer%d" % k for k in range(3)] + (["ch_cer%d" % k for k in range(3)] if topology == "fixed" else [])
    names_b = (["hf10n", "hf1n"] if topology == "fixed" else ["ch_cer%d" % k for k in range(3)])
    acc = {n: 0.0 for n in names_a + names_b}
    # FE source
    L = LD.STAGES["FE"]["L"]
    if vin < vout:
        d = 1 - vin / vout; il = iout / (1 - d); dil = vin * d / (L * fsw); kind = "boost_out"
    else:
        d = vout / vin; il = iout; dil = vout * (1 - d) / (L * fsw); kind = "buck_out"
    a1, ac1 = harmonics(kind, il, d, dil)
    # charger source (buck from VBUS20 to VBAT; its average input current is the FE's output current)
    d2 = vbat / vout; il2 = iout / d2; dil2 = vout * d2 * (1 - d2) / (fch * 3.3e-6)
    a2, ac2 = harmonics("buck_in", il2, d2, dil2)
    for k in range(NH):
        for (amp, f, into) in ((a1[k], fsw * (k + 1), "a"), (a2[k], fch * (k + 1), "b")):
            w = 2 * math.pi * f
            zab = 0.010 + 1j * w * l16
            ia, ib = split_two_node(w, a_parts, b_parts, zab, amp if into == "a" else 0.0, -amp if into == "b" else 0.0)
            for n, i in zip(names_a, ia): acc[n] += abs(i) ** 2
            for n, i in zip(names_b, ib): acc[n] += abs(i) ** 2
    out = {n: math.sqrt(v) for n, v in acc.items()}
    out["_fe_ac_total"] = ac1; out["_ch_ac_total"] = ac2
    out["_eq19"] = iout * math.sqrt(vout / vin - 1) if vin < vout else dil / math.sqrt(12)
    out["_eq4"] = il2 * math.sqrt(d2 * (1 - d2))
    return out

def fe_sweep(bulk_key, nbulk, topology="fixed", iouts=(5.0, 5.7), vins=(9.0, 10.0, 12.0, 13.8, 16.0, 24.0, 36.0),
             vbats=(10.0, 12.0, 14.4, 16.8), fchs=(400e3, 800e3), mismatch=False, with_charger=True):
    """worst per-part bulk current over every corner, the corner that gives it, and the worst ceramic current."""
    worst = (-1.0, None); worst_cer = (-1.0, None)
    for vin, iout, fsw, vbat, fch, cb_k, esr_k, esl_b, cer_esr, cer_esl, l16 in itertools.product(
            vins, iouts, (LD.FSW_LO, LD.FSW, LD.FSW_HI), vbats, fchs, (0.8, 1.2), (0.3, 1.0, 2.0), (1.5e-9, 3.5e-9),
            (0.002, 0.005), (0.8e-9, 1.5e-9), (5e-9, 20e-9)):
        for cer_c in ((4e-6, 4e-6), (7e-6, 6e-6)):
            r = fe_case(vin, iout if with_charger or True else iout, fsw, vbat, fch, bulk_key, nbulk, cb_k, esr_k, esl_b, cer_c, cer_esr, cer_esl, l16,
                        topology, mismatch)
            if not with_charger:
                pass
            b = max([r["bulk%d" % k] for k in range(nbulk)] or [0.0])
            cmax = max(v for n, v in r.items() if "cer" in n)
            corner = dict(vin=vin, iout=iout, fsw=fsw, vbat=vbat, fch=fch, c_k=cb_k, esr_k=esr_k, esl_b=esl_b, cer_c=cer_c,
                          cer_esr=cer_esr, cer_esl=cer_esl, l16=l16, fe_ac=r["_fe_ac_total"], ch_ac=r["_ch_ac_total"],
                          eq19=r["_eq19"], eq4=r["_eq4"])
            if b > worst[0]: worst = (b, corner)
            if cmax > worst_cer[0]: worst_cer = (cmax, corner)
    return worst, worst_cer

# ---- the other stages: one source (the stage's own output switch current), their own node and remote -----------------
def stage_case(name, bulk_key, nbulk, vin, vout, iout, fsw, cb_k, esr_k, esl_b, cl_total, cer_esr, cer_esl, remote):
    st = LD.STAGES[name]; L = st["L"]
    c_nom, esr_max = LD.BULK_PARTS[bulk_key]["c"], LD.BULK_PARTS[bulk_key]["esr"]
    ncer = 3 + (2 if name == "POE" else 0)
    parts = [(c_nom * cb_k, esr_max * esr_k, esl_b)] * nbulk + [(cl_total / ncer, cer_esr, cer_esl)] * ncer
    names = ["bulk%d" % k for k in range(nbulk)] + ["cer%d" % k for k in range(ncer)]
    if vin < vout:
        d = 1 - vin / vout; il = iout / (1 - d); dil = vin * d / (L * fsw); kind = "boost_out"
    else:
        d = vout / vin; il = iout; dil = vout * (1 - d) / (L * fsw); kind = "buck_out"
    a, ac = harmonics(kind, il, d, dil)
    acc = {n: 0.0 for n in names}
    for k in range(NH):
        w = 2 * math.pi * fsw * (k + 1)
        if remote:
            b_parts = [(remote["cr"], remote["esr_r"], 1e-9)]; zab = remote["rlead"] + 1j * w * remote["llead"]
            ia, _ = split_two_node(w, parts, b_parts, zab, a[k], 0.0)
        else:
            ia, _ = split_two_node(w, parts, [], 1e9, a[k], 0.0)
        for n, i in zip(names, ia): acc[n] += abs(i) ** 2
    out = {n: math.sqrt(v) for n, v in acc.items()}
    out["_ac_total"] = ac
    out["_eq19"] = iout * math.sqrt(vout / vin - 1) if vin < vout else dil / math.sqrt(12)
    return out

def stage_sweep(name, bulk_key, nbulk, iouts=None):
    st = LD.STAGES[name]
    worst = (-1.0, None); worst_cer = (-1.0, None)
    vins = sorted({v for _, v in st["modes"]} | ({9.0} if name == "FE" else set()))
    for (vout, _k), vin, iout, fsw, cb_k, esr_k, esl_b, cl, cer_esr, cer_esl, rem in itertools.product(
            st["vouts"], vins, iouts or [max(st["iout"])], (LD.FSW_LO, LD.FSW, LD.FSW_HI), (0.8, 1.2), (0.3, 1.0, 2.0),
            (1.5e-9, 3.5e-9), st["cl"], (0.002, 0.005), (0.8e-9, 1.5e-9), st["remote"]):
        if name == "POE": cl = cl * 5 / 3
        r = stage_case(name, bulk_key, nbulk, vin, vout, iout, fsw, cb_k, esr_k, esl_b, cl, cer_esr, cer_esl, rem or None)
        b = max([r["bulk%d" % k] for k in range(nbulk)] or [0.0])
        cmax = max(v for n, v in r.items() if n.startswith("cer"))
        corner = dict(vin=vin, vout=vout, iout=iout, fsw=fsw, c_k=cb_k, esr_k=esr_k, esl_b=esl_b, cl=cl, remote=bool(rem),
                      ac=r["_ac_total"], eq19=r["_eq19"])
        if b > worst[0]: worst = (b, corner)
        if cmax > worst_cer[0]: worst_cer = (cmax, corner)
    return worst, worst_cer

if __name__ == "__main__":
    report = {"ratings_A_rms_100kHz_125C": RATING_A}
    fe_only = "--fe-only" in sys.argv
    # the FE node: every candidate bulk, with R4A-N8 (C20-C22 before RAC) and, for the record, as built in the fix-up
    fe = {}
    for topo in ("as_built", "fixed"):
        for key, nb in (("V101", 1), ("V101", 2), ("V101", 3), ("V181", 1), ("V181", 2), ("V181", 3), ("V331", 1), ("V331", 2), ("V331", 3)):
            (b, cb), (cc, ccb) = fe_sweep(key, nb, topo)
            rate = RATING_A[key][0]
            fe["%s %dx%s" % (topo, nb, key)] = dict(worst_bulk_A=b, rating_A=rate, ratio=b / rate, worst_corner=cb,
                                                    worst_ceramic_A=cc, ceramic_corner=ccb, pass_=b <= rate)
            print("FE %-8s %d x %s: worst bulk %.2f A rms (rated %.2f, %.0f %%) at vin %.1f iout %.1f vbat %.1f fch %.0fk esr x%.1f; worst ceramic %.2f A"
                  % (topo, nb, key, b, rate, 100 * b / rate, cb["vin"], cb["iout"], cb["vbat"], cb["fch"] / 1e3, cb["esr_k"], cc), flush=True)
    # the same with the FE stage alone (the charger's ripple left out), the reviewer's question, for comparison
    for key, nb in (("V101", 1),):
        (b, cb), _ = fe_sweep(key, nb, "as_built", vbats=(16.8,), fchs=(800e3,))
        fe["as_built 1xV101, charger at 16.8 V / 800 kHz only"] = dict(worst_bulk_A=b, worst_corner=cb)
    report["FE"] = fe
    if not fe_only:
        others = {}
        for name, key, nb in (("S2", "E151", 3), ("SD", "E151", 3), ("PA", "E471", 2), ("HF", "E151", 2), ("PD", "E471", 2)):
            (b, cb), (cc, ccb) = stage_sweep(name, key, nb)
            rate = RATING_A[key][0]
            others[name] = dict(bulk="%d x %s" % (nb, key), worst_bulk_A=b, rating_A=rate, ratio=b / rate, worst_corner=cb,
                                worst_ceramic_A=cc, ceramic_corner=ccb, pass_=b <= rate)
            print("%-3s %d x %s: worst bulk %.2f A rms (rated %.2f, %.0f %%) at vin %.1f vout %.1f iout %.1f; total ac %.2f (Eq. 19 %.2f); worst ceramic %.2f A"
                  % (name, nb, key, b, rate, 100 * b / rate, cb["vin"], cb["vout"], cb["iout"], cb["ac"], cb["eq19"], cc), flush=True)
        (b, cb), (cc, ccb) = stage_sweep("POE", "V101", 0)
        others["POE"] = dict(bulk="none (five 10u 100V)", worst_ceramic_A=cc, ceramic_corner=ccb)
        print("POE five ceramics: worst ceramic %.2f A rms at vin %.1f" % (cc, ccb["vin"]), flush=True)
        report["others"] = others
    if "--json" in sys.argv:
        json.dump(report, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=float)
