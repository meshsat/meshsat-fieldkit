#!/usr/bin/env python3
"""The charger's efficiency by operating point, with the drawn FETs and with the FETs chosen for it (stream s117, second
issue, MESHSAT-1357, 29 September 2026). Answers the independent check's blocking items B1 and the coordinator's items 1, 3
and 4. Desk arithmetic on the makers' figures: nothing is built or measured. Stdlib only, plus the energy model's own
reference day, read through v2/docs/records/a1elec/energy_two_pack.py UNCHANGED (its load_model() refuses a changed input).

THE METHOD is SLUSE66A 10.2.2.6, Equations 6 to 22 (printed pages 86 to 88), per mode: in buck mode Q1 and Q2 switch and Q4
is on (Table 9-3, page 27); in boost mode Q3 and Q4 switch and Q1 is on; in buck-boost all four switch, taken here as a
BOUND (both legs hard-switched every cycle). The inductor current is solved from the input power less the losses (not taken
at an efficiency of 1). Counted: the four FETs (conduction, V-I overlap, Qoss, reverse recovery, dead time, gate drive at
VIN as Equation 17 and its note write it), the inductor's copper, R16 (the 10 mOhm input sense) and R17 (the 5 mOhm charge
sense, at the charge current the point names), and 1 mA of controller draw. EXCLUDED, so every figure is high by them: the
inductor's core loss (Coilcraft publishes it only through its calculator, not held), the board's copper, and light-load PFM
(9.3.14, page 28), which the fixed-frequency equations overstate once the inductor current falls under half its ripple.

FOUR READINGS of the same equations, each saying what it rests on:
  lower   the makers' maximum figures: REGN at its 5.7 V minimum (8.5, p.11), both gate paths at their maxima (RDS_HI_ON 6
          Ohm with the FET's RG maximum, RDS_HI_OFF 2.2 Ohm maximum with it, p.16), Qg at 6 V scaled from the table's
          maxima, VSD at its maximum, RDS(on) at 125 C (the FET's own curve), the inductor's DCR maximum plus 20 percent
  TI      TI's method as written: Qsw = Qgd + Qgs (Equation 14), typical figures, 25 C
  Qgs2    the same with Qsw = Qgd + Qgs - Qg(th) (the charge past the threshold only)
  upper   Qsw = Qgd alone (the current rise ignored), half the table's Qrr, VSD 0.7 V, the inductor's typical DCR
Neither end is a guarantee: the lower end is the makers' corners stacked, the upper end ignores a term the physics has.

INFERRED inputs (readings of the makers' curves by this stream, marked where used): Qg at 6 V, the plateau, RDS(on) at 6 V
and 125 C, Qoss at 20.7 V from the Coss curve, the inductors' DC-bias fall. The drawn FET's figures are the independent
check's own readings (v2/docs/records/s117 README, second issue), so the drawn column reproduces its table.

Usage: python3 efficiency.py > efficiency.out   (deterministic; the committed .out is this script's output)"""
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# --------------------------------------------------------------------------------------------- the FETs (per 6 V drive)
# qg / qg_max: total gate charge at VGS 6 V, typical (curve reading) and scaled from the table's maxima as
# Qg(4.5)max + 1.5 x (Qg(10)max - Qg(4.5)max) / 5.5; qsw14 = Qgd + Qgs (Eq.14), qsw2 = that less Qg(th), qgd = Qgd.
FETS = {
    "CSD18510Q5B": dict(  # TI SLPS632 (March 2017), held v2/vendor/battery/ti-csd18510q5b.pdf: 5.1 p.3, Figures 2 to 7 p.5
        v=40, qg=75e-9, qg_max=96.3e-9, qsw14=49e-9, qsw2=34e-9, qgd=21e-9, qoss=35e-9, qrr=31e-9,
        rds=1.1e-3, rds_up=1.0e-3, rds_hot=1.5e-3, rg=0.9, rg_max=1.8, vplt=2.6, vplt_lo=2.45,
        src="SLPS632 p.3 (Qg 58/75 nC at 4.5 V, 118/153 at 10 V; Qgd 21, Qgs 28, Qg(th) 15, Qoss 35 at 20 V, Qrr 31 nC "
            "at 20 V 32 A; RG 0.9/1.8 Ohm); Figure 4 p.5: 75 nC at 6 V (INFERRED); Figures 2 and 7: 1.0 to 1.1 mOhm at 6 V, "
            "25 C, 1.5 at 125 C (INFERRED)"),
    "CSD17578Q5A": dict(  # TI SLPS526 (March 2015), held back: v2/vendor/ti/held/ti-csd17578q5a-slps526.pdf
        v=30, qg=10.3e-9, qg_max=10.3e-9 + 1.5 * (22.3e-9 - 10.3e-9) / 5.5, qsw14=5.1e-9, qsw2=3.4e-9, qgd=2.0e-9,
        qoss=4.9e-9, qrr=6.5e-9, rds=6.6e-3, rds_up=6.6e-3, rds_hot=10.0e-3, rg=1.8, rg_max=3.6, vplt=2.7, vplt_lo=2.55,
        src="SLPS526 5.1 p.3 (Qg 7.9/10.3 nC at 4.5 V, 17.2/22.3 at 10 V; Qgd 2.0, Qgs 3.1, Qg(th) 1.7; Qoss 4.2 nC at 15 V; "
            "Qrr 6.5 nC at 15 V, 10 A, 300 A/us; RDS(on) 7.9/9.3 mOhm at 4.5 V and 5.9/6.9 at 10 V; RG 1.8/3.6 Ohm); Figure 4 "
            "p.5: 10.3 nC at 6 V and a plateau of 2.6 to 2.8 V at 10 A (INFERRED); Figure 7 p.5: 6.6 mOhm at 6 V, 25 C, 10.0 "
            "at 125 C (INFERRED); Figure 5 p.5: Coss about 125 pF from 15 to 21 V, so Qoss at 20.7 V about 4.9 nC (INFERRED)"),
    "CSD17577Q5A": dict(  # TI SLPS516 (August 2014), held back: v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf
        v=30, qg=16.0e-9, qg_max=17e-9 + 1.5 * (35e-9 - 17e-9) / 5.5, qsw14=7.9e-9, qsw2=5.4e-9, qgd=2.8e-9,
        qoss=7.1e-9, qrr=8.2e-9, rds=3.9e-3, rds_up=3.9e-3, rds_hot=5.8e-3, rg=1.4, rg_max=2.8, vplt=2.6, vplt_lo=2.45,
        src="SLPS516 5.1 p.3 (Qg 13/17 nC at 4.5 V, 27/35 at 10 V; Qgd 2.8, Qgs 5.1, Qg(th) 2.5; Qoss 6 nC at 15 V; Qrr "
            "8.2 nC at 15 V, 18 A; RDS(on) 4.8/5.8 mOhm at 4.5 V and 3.5/4.2 at 10 V; RG 1.4/2.8 Ohm); Figure 4 p.5: 16 nC "
            "at 6 V, plateau 2.6 to 2.9 V at 18 A (INFERRED); Figure 7 p.5: 3.9 mOhm at 6 V, 25 C, 5.8 at 125 C (INFERRED); "
            "Figure 5 p.5: Coss about 190 pF from 15 to 21 V, so Qoss at 20.7 V about 7.1 nC (INFERRED)"),
}

# --------------------------------------------------------------------------------------------- the inductors
# Coilcraft 804-1 (XAL1010, revised 02/25/26): DCR typ / max; 804-2 curves read by this stream (INFERRED), in uH.
INDUCTORS = {
    "XAL1010-472ME": dict(L=4.7e-6, dcr=(5.20e-3, 5.70e-3), curve=[(0, 4.75), (5, 4.58), (10, 4.3), (15, 3.95), (20, 3.6), (25, 3.3)]),
    "XAL1010-332ME": dict(L=3.3e-6, dcr=(3.70e-3, 4.10e-3), curve=[(0, 3.35), (5, 3.25), (10, 3.07), (15, 2.85), (20, 2.52), (25, 2.28)]),
}


def lfrac(part, amps):
    pts = INDUCTORS[part]["curve"]
    for (a0, l0), (a1, l1) in zip(pts, pts[1:]):
        if amps <= a1:
            return (l0 + (l1 - l0) * (amps - a0) / (a1 - a0)) / pts[0][1]
    return pts[-1][1] / pts[0][1]


READINGS = ("lower", "TI", "Qgs2", "upper")


def fetp(name, reading):
    """The figures one reading takes for one FET."""
    f = FETS[name]
    if reading == "lower":
        return dict(qsw=f["qsw14"], qg=f["qg_max"], rds=f["rds_hot"], rg=f["rg_max"], vplt=f["vplt_lo"], qrr=f["qrr"], qoss=f["qoss"], vf=1.0)
    if reading == "TI":
        return dict(qsw=f["qsw14"], qg=f["qg"], rds=f["rds"], rg=f["rg"], vplt=f["vplt"], qrr=f["qrr"], qoss=f["qoss"], vf=0.8)
    if reading == "Qgs2":
        return dict(qsw=f["qsw2"], qg=f["qg"], rds=f["rds"], rg=f["rg"], vplt=f["vplt"], qrr=f["qrr"], qoss=f["qoss"], vf=0.8)
    return dict(qsw=f["qgd"], qg=f["qg"], rds=f["rds_up"], rg=f["rg"], vplt=f["vplt_lo"], qrr=f["qrr"] / 2, qoss=f["qoss"], vf=0.7)


def drive(reading):
    """REGN and the driver's own turn-on and turn-off resistances (SLUSE66A 8.5, pp.11 and 16)."""
    if reading == "lower":
        return 5.7, 6.0, 2.2
    return 6.0, 6.0, 1.3


def leg(v, il, di, f, hi, lo, reading):
    """One hard-switched leg at voltage v: the switching FET 'hi' (V-I overlap and Qoss, Eq.10 and 16) and the
    synchronous FET 'lo' (reverse recovery and dead time, Eq.21 and 22)."""
    regn, r_on, r_off = drive(reading)
    iv, ip = il - di / 2, il + di / 2
    ion = (regn - hi["vplt"]) / (r_on + hi["rg"])
    ioff = hi["vplt"] / (r_off + hi["rg"])
    ton, toff = hi["qsw"] / ion, hi["qsw"] / ioff
    return {"VI": 0.5 * v * iv * ton * f + 0.5 * v * ip * toff * f, "Qoss": 0.5 * v * hi["qoss"] * f,
            "Qrr": v * lo["qrr"] * f, "dead": lo["vf"] * iv * f * 40e-9 + lo["vf"] * ip * f * 30e-9}


def stage(mode, vin, iin, vout, ichg, fets, ind, f, r_in, r_chg, reading):
    """(loss W, terms, inductor current, per-FET dissipation) at one point. fets = (Q1, Q2, Q3, Q4) part names:
    Q1/Q2 the buck leg (board A's Q7/Q8), Q3/Q4 the boost leg (Q9/Q10)."""
    q = [fetp(n, reading) for n in fets]
    dcr = INDUCTORS[ind]["dcr"][1] * (1.2 if reading == "lower" else 1.0) if reading != "upper" else INDUCTORS[ind]["dcr"][0]
    pin = vin * iin
    il = pin / vout if mode == "buck" else iin
    for _ in range(60):
        L = INDUCTORS[ind]["L"] * lfrac(ind, il)
        t, per = {}, [0.0, 0.0, 0.0, 0.0]
        if mode == "buck":
            d = vout / vin
            di = vin * d * (1 - d) / (f * L)
            i2 = il * il + di * di / 12
            s = leg(vin, il, di, f, q[0], q[1], reading)
            per[0] = d * i2 * q[0]["rds"] + s["VI"] + s["Qoss"]
            per[1] = (1 - d) * i2 * q[1]["rds"] + s["Qrr"] + s["dead"]
            per[3] = i2 * q[3]["rds"]
            t["gates"] = vin * (q[0]["qg"] + q[1]["qg"]) * f
        elif mode == "boost":
            d = 1 - vin / vout
            di = vin * d / (f * L)
            i2 = il * il + di * di / 12
            s = leg(vout, il, di, f, q[2], q[3], reading)
            per[0] = i2 * q[0]["rds"]
            per[2] = d * i2 * q[2]["rds"] + s["VI"] + s["Qoss"]
            per[3] = (1 - d) * i2 * q[3]["rds"] + s["Qrr"] + s["dead"]
            t["gates"] = vin * (q[2]["qg"] + q[3]["qg"]) * f
        else:  # buck-boost BOUND: both legs hard-switched every cycle, each high side conducting the whole cycle
            di = 0.25 * vin / (f * L)
            i2 = il * il + di * di / 12
            s1 = leg(vin, il, di, f, q[0], q[1], reading)
            s2 = leg(vout, il, di, f, q[2], q[3], reading)
            per[0] = i2 * q[0]["rds"] + s1["VI"] + s1["Qoss"]
            per[1] = s1["Qrr"] + s1["dead"]
            per[2] = s2["VI"] + s2["Qoss"]
            per[3] = i2 * q[3]["rds"] + s2["Qrr"] + s2["dead"]
            t["gates"] = vin * sum(x["qg"] for x in q) * f
        t["FETs"] = sum(per)
        t["L copper"] = i2 * dcr
        t["R_in"] = iin * iin * r_in
        t["R_chg"] = ichg * ichg * r_chg
        t["Iq"] = vin * 1.0e-3
        tot = sum(t.values())
        il_new = (pin - tot) / vout if mode == "buck" else iin
        if abs(il_new - il) < 1e-7:
            break
        il = il_new
    return tot, t, il, per


def eta(*a, **k):
    tot = stage(*a, **k)[0]
    return 1 - tot / (a[1] * a[2])


# --------------------------------------------------------------------------------------------- the sets and the points
DRAWN = ("CSD18510Q5B",) * 4
CHOSEN_U3 = ("CSD17578Q5A", "CSD17577Q5A", "CSD17577Q5A", "CSD17577Q5A")   # Q7 the hard-switched high side; Q8 to Q10 low RDS(on)
U3B_800_SET = ("CSD17578Q5A",) * 4                                          # U3B at 800 kHz: REGN needs the smaller Qg everywhere
U3B_400_SET = ("CSD17578Q5A", "CSD17577Q5A", "CSD17578Q5A", "CSD17577Q5A")  # U3B at 400 kHz: fast parts where each leg hard-switches
U3 = dict(ind="XAL1010-472ME", f=400e3, r_in=0.010, r_chg=0.005)             # S-117's row, R16 10 mOhm, R17 5 mOhm
U3B_DRAFT = dict(ind="XAL1010-332ME", f=800e3, r_in=0.005, r_chg=0.005)      # a1elec TOPOLOGY.md 3b: R16B, R17B 5 mOhm
U3B_400 = dict(ind="XAL1010-472ME", f=400e3, r_in=0.010, r_chg=0.005)        # the alternative row (10 mOhm sense)

U3_POINTS = [  # label, VIN, IIN, VOUT, charge current through R17
    ("model peak (a1elec .out 7): 6.20 A in, node 14.5 V, base charge 1.91 A", 20.7, 6.20, 14.5, 1.91),
    ("reconciliation's minimum cap: 6.1 A in, 14.5 V, ChargeCurrent 3.968 A", 20.7, 6.1, 14.5, 3.968),
    ("pack range, low: 6.1 A in, node 12.0 V", 20.7, 6.1, 12.0, 3.968),
    ("pack range, high: 6.1 A in, node 16.8 V", 20.7, 6.1, 16.8, 3.968),
    ("entry E1: 4.15 A in, 14.5 V", 20.7, 4.15, 14.5, 3.968),
    ("load only: about 2.15 A in (42.8 W out), 14.5 V", 20.7, 2.15, 14.5, 0.0),
]


def profile():
    """The energy model's reference day (September, 400 Wp, the 200 W stage), per hour: U3's input in watts under the
    entries E2 (as drafted: 128.3 W) and E1 (as generated with FW-A16 revised: 85.9 W). Read through energy_two_pack.py."""
    sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "a1elec"))
    import energy_two_pack as T
    d, pack, res4, t2m = T.load_model()
    prof = res4["months"][T.MONTH]["profile"]
    e_st, e_fe, e_ch = T.chain(d)
    caps = {k: min(T.ENTRIES[k]["fe_out_w"], T.ENTRIES[k]["u3_in_w"]) for k in ("E2", "E1")}
    out = []
    for h, g in enumerate(prof):
        p_fe = min(T.EB.panel_w(g, 400, res4["pr"]), 200.0) * e_st * e_fe
        out.append((h, {k: min(p_fe, c) for k, c in caps.items()}))
    return out, caps, e_ch


def daily(fets, entry, prof, reading):
    """The day's energy-weighted efficiency: sum of the hours' outputs over the sum of their inputs."""
    pin = pout = 0.0
    for h, w in prof:
        p = w[entry]
        if p < 1.0:
            continue
        iin = p / 20.7
        ichg = min(3.968, p * 0.95 / 14.5)
        e = eta("buck", 20.7, iin, 14.5, ichg, fets, U3["ind"], U3["f"], U3["r_in"], U3["r_chg"], reading)
        pin += p
        pout += p * e
    return pout / pin, pin


def fmt_row(label, vals):
    return "   %-66s %s" % (label, "  ".join("%.3f" % x for x in vals))


def main():
    P = print
    P("THE CHARGER'S EFFICIENCY BY OPERATING POINT (efficiency.py, stream s117 second issue, MESHSAT-1357). Desk arithmetic")
    P("on the makers' figures (SLUSE66A Equations 6 to 22); nothing built or measured. Core loss, board copper and PFM EXCLUDED:")
    P("every figure is high by them. Readings: lower = the makers' maxima; TI = Equation 14 with typical figures; Qgs2; upper.")
    P("")
    prof, caps, e_ch = profile()
    for title, fets in (("1. U3 WITH THE DRAWN FETS (Q7 to Q10 CSD18510Q5B), S-117's row (XAL1010-472ME, 400 kHz), R16 10 mOhm, R17 5 mOhm", DRAWN),
                        ("2. U3 WITH THE CHOSEN FETS (Q7 CSD17578Q5A; Q8, Q9, Q10 CSD17577Q5A), the same row and sense resistors", CHOSEN_U3)):
        P(title)
        P("   %-66s %s" % ("operating point (20.7 V in, buck)", "  ".join("%5s" % r for r in READINGS)))
        for lab, vin, iin, vo, ich in U3_POINTS:
            P(fmt_row(lab, [eta("buck", vin, iin, vo, ich, fets, U3["ind"], U3["f"], U3["r_in"], U3["r_chg"], r) for r in READINGS]))
        for h, w in prof:
            p = w["E2"]
            if 1.0 <= p < caps["E2"] - 0.05:
                P(fmt_row("the reference day's hour %02d UTC under the E2 cap: %.1f W in, %.2f A" % (h, p, p / 20.7),
                          [eta("buck", 20.7, p / 20.7, 14.5, min(3.968, p * 0.95 / 14.5), fets, U3["ind"], U3["f"], U3["r_in"], U3["r_chg"], r) for r in READINGS]))
        P(fmt_row("buck-boost BOUND at 16.8 V (all four switching; TI states no threshold)",
                  [eta("bb", 20.7, 6.1, 16.8, 3.968, fets, U3["ind"], U3["f"], U3["r_in"], U3["r_chg"], r) for r in READINGS]))
        for entry in ("E2", "E1"):
            vals, pins = [], None
            for r in READINGS:
                e, pins = daily(fets, entry, prof, r)
                vals.append(e)
            P(fmt_row("the day, energy-weighted, entry %s (%.0f Wh into U3 a day)" % (entry, pins), vals))
        P("")
    P("   the reference day's hours (U3's input, W): E2 %s" % " ".join("%.0f" % w["E2"] for h, w in prof if w["E2"] >= 1.0))
    P("                                              E1 %s" % " ".join("%.0f" % w["E1"] for h, w in prof if w["E1"] >= 1.0))
    P("   (energy_two_pack.py's September reference day, 400 Wp, the 200 W stage, stage 0.93 and front end 0.93 as it carries them)")
    P("")
    P("3. THE BREAKDOWN AT THE MODEL'S PEAK (6.20 A in, 14.5 V), TI's reading, W")
    for lab, fets in (("drawn", DRAWN), ("chosen", CHOSEN_U3)):
        tot, t, il, per = stage("buck", 20.7, 6.20, 14.5, 1.91, fets, U3["ind"], U3["f"], U3["r_in"], U3["r_chg"], "TI")
        P("   %-7s total %.2f W (IL %.2f A): Q7 %.2f, Q8 %.2f, Q10 %.2f, gate drive %.2f, L2 copper %.2f, R16 %.2f, R17 %.2f, Iq %.2f"
          % (lab, tot, il, per[0], per[1], per[3], t["gates"], t["L copper"], t["R_in"], t["R_chg"], t["Iq"]))
    P("   the budget for 0.98 at this point: %.2f W" % (0.02 * 20.7 * 6.20))
    P("")
    P("4. U3B (Option A(i)'s lid charger, records/a1elec/TOPOLOGY.md 3b), VIN = VBAT 14.5 V, the model's 55.3 W at its peak hour,")
    P("   lid charge 3.69 A; the lid below VBAT runs buck, above it boost, near it buck-boost (bound)")
    for lab, fets, row in (("drafted: CSD18510Q5B x 4, 800 kHz, XAL1010-332ME, 5 mOhm sense", DRAWN, U3B_DRAFT),
                           ("CSD17578Q5A x 4, the drafted 800 kHz row", U3B_800_SET, U3B_DRAFT),
                           ("Q7B, Q9B CSD17578Q5A and Q8B, Q10B CSD17577Q5A, the 400 kHz row (4.7 uH, 10 mOhm sense)", U3B_400_SET, U3B_400)):
        P("   %s" % lab)
        for mode, vo, ml in (("buck", 13.0, "lid 13.0 V, buck"), ("buck", 14.0, "lid 14.0 V, buck"), ("boost", 15.5, "lid 15.5 V, boost"),
                             ("bb", 14.5, "lid about 14.5 V, buck-boost BOUND")):
            P(fmt_row("     " + ml, [eta(mode, 14.5, 55.3 / 14.5, vo, 3.69, fets, row["ind"], row["f"], row["r_in"], row["r_chg"], r) for r in READINGS]))
    P("")
    P("5. REGN'S GATE-DRIVE BUDGET (SLUSE66A 8.5 p.11: VREGN_REG specified for 0 to 60 mA; IREGN_LIM 50 min, 65 typ mA).")
    P("   I = sum of the switching FETs' Qg at 6 V x fS; typical Qg at the typical fS, the scaled maximum Qg at the maximum fS")
    for lab, fets, fk, modes in (("U3 drawn", DRAWN, (400e3, 460e3), ("buck", "bb")), ("U3 chosen", CHOSEN_U3, (400e3, 460e3), ("buck", "bb")),
                                 ("U3B drafted", DRAWN, (800e3, 920e3), ("buck", "bb")), ("U3B 800 kHz, 78 x 4", U3B_800_SET, (800e3, 920e3), ("buck", "bb")),
                                 ("U3B 400 kHz, 78/77", U3B_400_SET, (400e3, 460e3), ("buck", "bb")), ("U3B 800 kHz, 78/77", U3B_400_SET, (800e3, 920e3), ("buck", "bb"))):
        for m in modes:
            sw = (0, 1) if m == "buck" else (0, 1, 2, 3)
            typ = sum(FETS[fets[i]]["qg"] for i in sw) * fk[0] * 1e3
            mx = sum(FETS[fets[i]]["qg_max"] for i in sw) * fk[1] * 1e3
            P("   %-22s %-10s %6.1f mA typical, %6.1f mA at the maxima: %s" % (lab, "buck" if m == "buck" else "buck-boost", typ, mx,
                                                                              "inside 50 mA" if mx < 50 else ("typical inside, maxima OVER 50 mA" if typ < 50 else "OVER 50 mA")))
    P("")
    P("6. THE HOTTEST FET (the FETs' own dissipation; RthJA 50 C/W maximum on TI's 1 in2, 2 oz copper pad, SLPS526 and SLPS516")
    P("   5.2 p.3; board A's copper is not TI's pad, so the rise orders the cases and does not predict a temperature)")
    for lab, vin, iin, vo, ich in (U3_POINTS[0], ("G1: 5.7 A in, pack 10.0 V (the as-generated bound)", 20.7, 5.7, 10.0, 0.384),
                                   ("A2: 6.45 A in, pack 10.0 V (Option A(i)'s bound)", 20.7, 6.45, 10.0, 0.384)):
        P("   %s" % lab)
        for fl, fets in (("drawn", DRAWN), ("chosen", CHOSEN_U3)):
            for r in ("TI", "lower"):
                tot, t, il, per = stage("buck", vin, iin, vo, ich, fets, U3["ind"], U3["f"], U3["r_in"], U3["r_chg"], r)
                k = max(range(4), key=lambda i: per[i])
                P("     %-6s %-5s IL %5.2f A: Q7 %.2f W, Q8 %.2f W, Q10 %.2f W; hottest Q%d (%s) %.0f K over its surroundings at 50 C/W"
                  % (fl, r, il, per[0], per[1], per[3], (7, 8, 9, 10)[k], fets[k], per[k] * 50))
    P("")
    P("7. WHAT THE ENERGY MODEL SHOULD CARRY FOR THE CHARGERS (a table for the energy record's writer; core loss excluded)")
    P("   %-44s %-9s %-9s %-9s %s" % ("", "lower", "TI", "upper", "carry (TI's reading, the day's weighted)"))
    for lab, fets in (("U3, drawn FETs (S-117's row)", DRAWN), ("U3, chosen FETs", CHOSEN_U3)):
        for entry in ("E2", "E1"):
            v = [daily(fets, entry, prof, r)[0] for r in ("lower", "TI", "upper")]
            P("   %-44s %-9.3f %-9.3f %-9.3f %.3f" % ("%s, day at %s" % (lab, entry), v[0], v[1], v[2], v[1]))
    for lab, fets, row in (("U3B, drafted (800 kHz, CSD18510Q5B)", DRAWN, U3B_DRAFT), ("U3B, CSD17578Q5A x 4, 800 kHz", U3B_800_SET, U3B_DRAFT),
                           ("U3B, 78/77 pairs, 400 kHz row", U3B_400_SET, U3B_400)):
        v = [min(eta(m, 14.5, 55.3 / 14.5, vo, 3.69, fets, row["ind"], row["f"], row["r_in"], row["r_chg"], r) for m, vo in (("buck", 13.0), ("bb", 14.5), ("boost", 15.5)))
             for r in ("lower", "TI", "upper")]
        P("   %-44s %-9.3f %-9.3f %-9.3f %.3f (the worst of buck, buck-boost bound and boost at the peak hour)" % (lab, v[0], v[1], v[2], v[1]))
    P("   The energy chain's rows today: U3 0.98 (records/energy/energy_inputs.yaml, SLUSE66A Figure 8-4, FETs not named) and U3B")
    P("   0.975 (records/a1elec/energy_two_pack.py, Figure 8-3). Figure 8-4 at 4 A and 14.8 V loses about 0.96 W in all, less than")
    P("   the drawn FETs' gate drive alone (1.24 W at 400 kHz): the curve describes FETs of a much smaller gate charge.")


if __name__ == "__main__":
    main()
