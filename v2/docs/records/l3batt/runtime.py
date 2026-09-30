#!/usr/bin/env python3
"""runtime.py: battery-only endurance and battery-plus-solar results for the runtime-and-battery comparison of Layer 3
(stream l3batt, MESHSAT-1357, 30 September 2026; the owner's instruction of that day: "Compare two requirement options.
Option A: 48 hours minimum required; 72 hours desired. Option B: 72 hours required, using an upgraded battery arrangement
where necessary. Use the same approved functions and operating profile. Clearly separate battery-only endurance from
battery-plus-solar endurance and state the solar/weather assumptions.").

PROTOTYPE DESIGN, desk arithmetic: nothing is built, bought, powered or measured. Energy results are MODELED on a1elec's
energy_two_pack.py through energy_basis.py's set-up (imported, pinned), with the Samsung INR18650-35E pack model that
record carries; the other cells' usable energy is INFERRED by applying that model's end-of-discharge fraction to each
maker's minimum energy and cold figure (the makers' sheets are read here from filed or held files, pinned by sha256).

The arrangements, every one with HF and the tablet kept (arrangement A of a1mech: the QMX set and the 8 inch tablet
bracket in the lid, 39 lid places, 4S9P):
  D06    the ruled pack of D-06: one 4S3P of INR18650-35E in the east pocket, no lid pack
  A35    Option A(i)'s base 4S6P plus the lid 4S9P, all INR18650-35E (4S15P, 60 cells)
  A21-*  the base 4S6P of 35E plus a lid 4S6P of a 21700 cell: a1mech's lid generator re-run with the 21700's maximum
         diameter and length, every other input unchanged, holds 27 places in arrangement A (a scratch re-run, INFERRED;
         the constants are below); the base pockets' 21700 fit is not shown
  X-NH   A35 plus one or two Inspired Energy NH2054HD34 smart packs OUTSIDE the case: a PROPOSAL (an external battery)

Run from the repository root:  python3 v2/docs/records/l3batt/runtime.py > v2/docs/records/l3batt/runtime.out
Deterministic. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
L3 = os.path.join(TOP, "v2", "docs", "records", "l3plane")
PIN_EB = "7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47"
if hashlib.sha256(open(os.path.join(L3, "energy_basis.py"), "rb").read()).hexdigest() != PIN_EB:
    sys.stderr.write("runtime: energy_basis.py is not the pinned file; refusing\n")
    sys.exit(2)
sys.path.insert(0, L3)
import energy_basis as EB  # noqa: E402
TP, ER = EB.TP, EB.ER

EB_OUT = "v2/docs/records/l3plane/energy_basis.out"
WB_OUT = "v2/docs/records/l3plane/weather_basis.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
PWR_OUT = "v2/docs/records/rv-pwr/pwr_budget.out"
T_COLD = -10.0          # REQ-046: cells discharged only between -10 and +60 C at the cell surface; the 35E's one cold point
LID_A = 9               # a1mech arrangement A (HF and the tablet kept): 39 places, 4S9P
LID_A21 = 6             # the scratch re-run with 21700 cells: 27 places in arrangement A, 4S6P (INFERRED)

# The makers' figures (sheets pinned by sha256; HELD = held back from the tree by its terms, fetched by fetch_held_back.py)
CELLS = {
    # key: (label, sheet, sha256, held, min energy Wh a cell at the standard rate, its basis, cold factor at -10 C, its basis, mass kg, dia, len)
    "P45B": ("Molicel INR-21700-P45B", "v2/vendor/battery/molicel-inr21700-p45b-v1.2.pdf",
             "8b08963c0a198fd391ed7e62388be12cbd14c38d7b587982f9800b15c6821b4a", False,
             15.5, "Minimum 4300 mAh, 15.5 Wh (Version 1.2, p.1)", 0.91,
             "read by eye from the Discharge Temperature Characteristics at 4.5 A: about 4.2 Ah at -20 C against about 4.6 Ah at 23 C to 2.5 V (INFERRED; no -10 C curve)",
             0.070, 21.55, 70.15),
    "50E": ("Samsung SDI INR21700-50E", "v2/vendor/battery/held/samsung-inr21700-50e-v1.0.pdf",
            "f2feac1fe964b66db438d42c42d1b3713137a0c5ddc13334d54a4b794a889ec3", True,
            4.900 * 3.63, "standard discharge capacity min 4,900 mAh (7.2) at the nominal 3.63 V (3.4)", 0.70 / 0.97,
            "7.5: -10 C 70 %, 23 C 97 % at 1C (4,900 mA): 0.722", 0.0695, 21.25, 70.80),
    "M50LT": ("LG INR21700M50LT", "v2/vendor/battery/held/lg-inr21700-m50lt-2020-08-27.pdf",
              "1408ad2c1be0c92b168588224474e8d8ae5873395ac639ee7938d8d3efa9ea0b", True,
              17.6, "2.1 energy, min 17.6 Wh by standard charge and discharge", 0.70,
              "4.2: -10 C at least 70 % of Whmin (0 C 80 %)", 0.0692, 21.44, 70.60),
}
NH = ("Inspired Energy NH2054HD34", "v2/vendor/battery/held/inspired-energy-nh2054hd34-v1.8.pdf",
      "5be4472514b5557bc529d0b258a8117bd4f930b7880c2ebbb04a62ced448b9b3", True)
NH_AH, NH_V, NH_KG, NH_DIMS, NH_OCD = 6.136, 14.4, 0.435, (150.37, 77.39, 22.51), 8.25   # 3.1.2, 3.1.1, 3.6.1, p.24 drawing, discharge over-current


def refuse(code, msg):
    sys.stderr.write("runtime: %s; refusing\n" % msg)
    sys.exit(code)


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def crit(r):
    return (r["ok"], r["ok"] and r["low_t"] > EB.FLOOR, r["ok"] and r["low_b"] > EB.FLOOR and r["low_l"] > EB.FLOOR)


def main():
    D0, PACK0, RES0, t2m = TP.load_model()
    EB.D0, EB.PACK0, EB.RES0 = D0, PACK0, RES0
    EB.TMIN = round(min(t2m), 2)
    eb_out = EB.head_equal(EB_OUT)
    wb_out = EB.head_equal(WB_OUT)
    r11 = EB.head_equal(R11_OUT)
    notes = " ".join(EB.head_equal(EB.PANEL).split())
    m = need(notes, r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", "NOTES step")
    md = need(notes, r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", "NOTES drain")
    EB.FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_w = float(md.group(2)) / D0["mission"]["hours"]
    vr = EB.VR.compute()
    AC, _e, _t = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    v_min, v_nom = vr["bands"][0][4], vr["nominal"]
    rd = EB.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EB.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in need(TP.PAR["v_ak"][1], r"([\d]+) / ([\d]+) / ([\d]+) mV", "v_ak").groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    for k, c in CELLS.items():
        p = os.path.join(TOP, c[1])
        if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != c[2]:
            refuse(2, "%s's sheet is not the pinned file (held sheets: run fetch_held_back.py)" % c[0])
    p = os.path.join(TOP, NH[1])
    if not os.path.exists(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != NH[2]:
        refuse(2, "the NH2054HD34 sheet is not the pinned file (run fetch_held_back.py)")
    pwr = EB.head_equal(PWR_OUT)
    hf_rx = float(need(pwr.split("== shares PS-TYP", 1)[1], r"^\s+QMX HF\s+load\s+[\d.]+\s+battery\s+([\d.]+)\s+S", "pwr_budget.out the QMX receiving").group(1))
    held = float(need(r11, r"held, R11 10\.0 mOhm:\s+([\d.]+) /", "r11_dep.out held band").group(1))
    other = float(need(r11, r"plus ([\d.]+) A of VBUS20's other loads", "r11_dep.out other loads").group(1))
    fe_held = held - other
    u3_e1, u3_e2 = TP.v("u3_iin_e1_a"), TP.v("u3_iin_draft_a")

    def we(v, i, extra=None):
        x = {"eta_u3": EB.u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    lo3 = {"eta_st": ch[0]["low"], "eta_fe": ch[1]["low"], "chg_eta": ce["low"]}
    cases = {
        "DRAWN": ("AS DRAWN (R11 10 mOhm, U3 4.15 A), NOM inputs; min(available, cap) kept: an upper bound", v_nom, u3_e1,
                  {"eta_u3": EB.u3_day(v_nom, u3_e1, "TI"), "fe_i": fe_held}),
        "NOM": ("CORRECTED PATH, HYPOTHETICAL, NOM: CONDITIONAL on the three declared efficiencies", v_nom, u3_e2,
                {"eta_u3": EB.u3_day(v_nom, u3_e2, "TI")}),
        "NOM90": ("the same with the three efficiencies at their 0.90 bracket", v_nom, u3_e2, dict({"eta_u3": EB.u3_day(v_nom, u3_e2, "TI")}, **lo3)),
        "WE": ("CORRECTED PATH, HYPOTHETICAL, WE: CONDITIONAL on the three declared efficiencies", v_min, 6.1, we(v_min, 6.1)),
        "WE90": ("the same with the three efficiencies at their 0.90 bracket", v_min, 6.1, we(v_min, 6.1, lo3)),
    }

    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def sim1(key, n, pr, vals, start, t_l, hours):
        _t, vb, iin, ov = cases[key]
        d, pack, r, cfg = EB.setup(n, pr, vb, iin, ov)
        d = dict(d)
        d["mission"] = dict(d["mission"], hours=hours)
        load0 = TP.LOAD
        TP.LOAD = load0 + ov.get("drain_w", 0.0)
        try:
            return TP.sim(d, pack, r, EB.Series(vals), 400.0, 200.0, start, TP.v("t_base_c"), t_l, cfg)
        finally:
            TP.LOAD = load0

    def meanday(key, n, b, hours):
        rs = [sim1(key, n, pr0 * rat40[b], [prof0[(s + h) % 24] for h in range(hours)], s, EB.TMIN, hours) for s in (6, 18)]
        stops = [r_["first_stop"] for r_ in rs if r_["first_stop"] is not None]
        return {"ok": all(r_["ok"] for r_ in rs), "both": min(r_["low_t"] for r_ in rs), "base": min(r_["low_b"] for r_ in rs),
                "lid": min(r_["low_l"] for r_ in rs), "short": max(r_["short"] for r_ in rs), "stop": min(stops) if stops else None,
                "stops": [r_["first_stop"] for r_ in rs],
                "el": rs[0]["el_full"], "eb": rs[0]["eb_full"]}

    def cellx(s):
        if s["ok"]:
            return "%.1f (base %.1f, lid %.1f) %s/%s" % (s["both"], s["base"], s["lid"], "Y" if s["both"] > EB.FLOOR else "N",
                                                         "Y" if s["base"] > EB.FLOOR and s["lid"] > EB.FLOOR else "N")
        return "NOT MET, stops at h %s, %.1f unserved" % ("/".join("-" if x is None else str(x) for x in s["stops"]), s["short"])

    o = []
    P = o.append
    P("RUNTIME AND BATTERY: BATTERY-ONLY ENDURANCE AND BATTERY PLUS SOLAR, 48 AND 72 HOURS (runtime.py, stream l3batt, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, bought, powered or measured. MODELED on a1elec's energy_two_pack.py through energy_basis.py's")
    P("set-up (pinned); other cells INFERRED from their makers' figures. HF and the tablet kept in every arrangement (a1mech")
    P("arrangement A). The author's analysis, AI arithmetic; not a qualified review and not the independent check.")
    P("")

    # 0. reproduction
    bad = 0
    sec5 = eb_out.split("\n5. THE CASES ON THE REFERENCE PLANE", 1)[1].split("\n6. ", 1)[0]
    for key, ebk in (("NOM", "NOM"), ("WE", "WE")):
        row = need(sec5, r"^\s+4S9P\s+%s\s+NOT MET, ([\d.]+) unserved\s+N/N\s+NOT MET, ([\d.]+) unserved" % ebk, "energy_basis.out 4S9P %s" % ebk)
        for bi, b in enumerate(("TYP", "WAB")):
            s = meanday(key, LID_A, b, 72)
            if s["ok"] or "%.1f" % s["short"] != row.group(1 + bi):
                bad += 1
    P("0. REPRODUCTION: the 72 h mean-day runs of the both-kept lid (4S9P) reproduce energy_basis.out section 5's NOM and WE rows:")
    P("   %s" % ("yes" if bad == 0 else "NO (%d)" % bad))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "%d reproduction check(s) failed" % bad)
    P("")

    # 1. battery-only endurance
    P("1. BATTERY-ONLY ENDURANCE to the kit's shutdown (each pack to its own 3.00 V line with the 5 % reserve), PS-IDLE-SPEC")
    P("   %.1f W at the pack terminals plus the lid path's standby drain %.3f W where a lid pack exists; aged to 80 %% (REQ-014);" % (TP.LOAD, drain_w))
    P("   both packs at +20 C, then both at %.0f C (REQ-046's discharge floor). The 35E: the model's chain (C_min 3.35 Ah, rate," % T_COLD)
    P("   mean voltage, the 3.00 V fraction, the cold factor 0.4124 at 1C, a lower bound at the kit's 0.2 A a cell). The lid's")
    P("   discharge path loss (V(AK) and the loop) is charged on the lid's share. No solar.")
    pk = PACK0
    load = TP.LOAD

    def lid_loss(p_l, v_l):
        i = p_l / v_l
        return (i * vak[1] + i * i * TP.v("r_lid_dsg")) / p_l
    rows1 = {}

    def only(label, parts, extra_note=""):
        """parts: list of (name, usable Wh at +20 C, at the cold end); prints hours."""
        tot20 = sum(x[1] for x in parts)
        totc = sum(x[2] for x in parts)
        ld = load + (drain_w if len(parts) > 1 else 0.0)
        rows1[label] = (tot20, totc, tot20 / ld, totc / ld)
        P("   %-58s usable %6.1f Wh / %6.1f Wh: %5.2f h at +20 C, %5.2f h at %.0f C%s" % (label, tot20, totc, tot20 / ld, totc / ld, T_COLD, extra_note))
    # D-06, the ruled 4S3P alone
    e20 = pk.usable_wh(load, 20.0, pk.age80, "3v00", 3)[0]
    ecd = pk.usable_wh(load, T_COLD, pk.age80, "3v00", 3)[0]
    only("D06: D-06's 4S3P of 35E (12 cells), no lid pack", [("base", e20, ecd)])
    # A(i) both kept, 35E
    nb, nl = 6, LID_A
    pb, pl = load * nb / (nb + nl), load * nl / (nb + nl)
    v_l = pk.n_s * 3.60
    parts = []
    for t_ in (20.0, T_COLD):
        eb_ = pk.usable_wh(pb, t_, pk.age80, "3v00", nb)[0]
        el_ = pk.usable_wh(pl, t_, pk.age80, "3v00", nl)[0] * (1 - lid_loss(pl, v_l))
        parts.append((eb_, el_))
    only("A35: A(i) base 4S6P + lid 4S9P of 35E (60 cells)", [("base", parts[0][0], parts[1][0]), ("lid", parts[0][1], parts[1][1])])
    base20, basec = parts[0][0], parts[1][0]
    # the 35E's own per-cell usable at the lid's share, to carry its end-of-discharge fraction to the other cells
    info = pk.usable_wh(pl, 20.0, 1.0, "3v00", nl)[1]
    f_dod = info["f_dod"]
    for k, c in CELLS.items():
        nl21 = LID_A21
        pl21 = load * nl21 / (nb + nl21)
        pb21 = load * nb / (nb + nl21)
        eb20 = pk.usable_wh(pb21, 20.0, pk.age80, "3v00", nb)[0]
        ebc = pk.usable_wh(pb21, T_COLD, pk.age80, "3v00", nb)[0]
        el20 = 4 * nl21 * c[4] * f_dod * pk.age80 * (1 - lid_loss(pl21, v_l))
        elc = el20 * c[6]
        only("A21-%s: base 4S6P 35E + lid 4S6P %s" % (k, c[0].split(" ", 1)[1]), [("base", eb20, ebc), ("lid", el20, elc)])
    nh20 = NH_AH * NH_V * pk.age80 * (1 - pk.rsoc)
    nhc = nh20 * 0.4124
    for nn in (1, 2):
        only("X-NH%d: A35 + %d NH2054HD34 outside the case (PROPOSAL)" % (nn, nn),
             [("base", parts[0][0], parts[1][0]), ("lid", parts[0][1], parts[1][1])] + [("nh", nh20, nhc)] * nn)
    P("   the 21700 lids: each maker's minimum energy x the 35E model's end-of-discharge fraction %.3f at the lid's current x 0.80" % f_dod)
    P("   aged (INFERRED); the cold factor from each sheet: %s" % "; ".join("%s %.3f (%s)" % (k, c[6], c[7]) for k, c in CELLS.items()))
    P("   the NH2054HD34: its rated 6.136 Ah x 14.4 V to 11.0 V (3.1.2) x 0.80 aged x 0.95 reserve = %.1f Wh; its cold factor not" % nh20)
    P("   printed as text, the 35E's 0.4124 taken (INFERRED, a lower bound); its discharge over-current trips at %.2f A (the kit's" % NH_OCD)
    P("   PS-IDLE-SPEC draws about 3 A; a PA key-down draws about 10 A: a smart pack alone cannot carry a key-down)")
    P("")

    # 2. battery plus solar: the mean day, 48 and 72 h, both kept
    P("2. BATTERY PLUS SOLAR, SC-37's mean September day at Leiden on the 40 degree south plane, TYP (the case) and WAB (a")
    P("   sensitivity), 400 Wp in 2S2P into the model's 200 W stage window, the lid pack at %.2f C and the base at +%.0f C, both" % (EB.TMIN, TP.v("t_base_c")))
    P("   full and aged at the start, starts 06 and 18 UTC. HF and the tablet kept: base 4S6P + lid 4S9P of 35E. Each cell: the")
    P("   lowest store (base, lid) and COMB/EACH, or where the kit stops (hours from the 06 / 18 UTC starts: hour 23 of the 06 UTC")
    P("   start and hour 11 of the 18 UTC start are both 05 UTC, the first night's end) and the energy unserved")
    s0 = meanday("NOM", LID_A, "TYP", 72)
    dark = [h for h in range(24) if prof0[h] <= 60.0]
    P("   the store at the start (usable, aged): base %.1f Wh at +%.0f C and lid %.1f Wh at %.2f C, %.1f Wh together; the mean" % (
        s0["eb"], TP.v("t_base_c"), s0["el"], EB.TMIN, s0["eb"] + s0["el"]))
    P("   day's hours at or under 60 W/m2 on the plane (UTC): %s, %d of 24 (the profile: %s)" % (
        ", ".join("%02d" % h for h in dark), len(dark), ", ".join("%.0f" % g for g in prof0)))
    res2 = {}
    for hours in (48, 72):
        P("   %d HOURS" % hours)
        for key in ("DRAWN", "NOM", "NOM90", "WE", "WE90"):
            st = meanday(key, LID_A, "TYP", hours), meanday(key, LID_A, "WAB", hours)
            res2[(key, hours)] = st
            P("     %-8s TYP %-52s WAB %s" % (key, cellx(st[0]), cellx(st[1])))
    P("   the cases: %s" % "; ".join("%s = %s" % (k, cases[k][0]) for k in ("DRAWN", "NOM", "NOM90", "WE", "WE90")))
    P("")

    # 3. what store carries 72 h (and 48 h) on the corrected path: the least lid parallel count, continuous
    def least(key, b, hours, line):
        def ok(x):
            s = meanday(key, x, b, hours)
            return s["ok"] and (s["both"] > EB.FLOOR if line == "COMB" else True)
        lo, hi = 1.0, 40.0
        if not ok(hi):
            return None
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            if ok(mid):
                hi = mid
            else:
                lo = mid
        return hi
    P("3. THE STORE THAT CARRIES THE MEAN DAY (the least lid parallel count, continuous, the base held at 4S6P; its excess over the")
    P("   both-kept lid's 4S9P is the upgrade a 72 h requirement asks, in 35E-equivalent cells and usable Wh at the lid's %.2f C)" % EB.TMIN)
    res3 = {}
    for hours in (48, 72):
        for key in ("NOM", "WE", "NOM90"):
            for b in ("TYP", "WAB"):
                x = least(key, b, hours, "COMB")
                if x is None:
                    P("     %d h %-6s %s: none up to 4S40P" % (hours, key, b))
                    res3[(hours, key, b)] = None
                    continue
                s9, sx = meanday(key, LID_A, b, hours), meanday(key, x, b, hours)
                extra_cells = 4 * (x - LID_A)
                extra_wh = sx["el"] - s9["el"]
                res3[(hours, key, b)] = (x, extra_cells, extra_wh)
                P("     %d h %-6s %s: lid 4S%.2fP, against the both-kept 4S9P: %+.1f 35E cells, %+.1f Wh usable" % (
                    hours, key, b, x, extra_cells, extra_wh))
    P("   (a negative excess: the both-kept store already carries it; COMB line, the kit never stopping as well)")
    load0 = TP.LOAD
    TP.LOAD = load0 + hf_rx
    try:
        xs = {(h, k): least(k, "TYP", h, "COMB") for h in (48, 72) for k in ("NOM", "WE")}
    finally:
        TP.LOAD = load0
    P("   SENSITIVITY, the QMX receiving all the time (PS-TYP's QMX HF row, %.2f W at the battery, pwr_budget.out; PS-IDLE-SPEC" % hf_rx)
    P("   carries the QMX's USB and HDMI 5 V only): %s" % "; ".join("%d h %s TYP lid 4S%.2fP (%+.1f cells over 4S9P)" % (
        h, k, xs[(h, k)], 4 * (xs[(h, k)] - LID_A)) for h, k in sorted(xs)))
    P("")

    # 4. coverage, 864 windows, 48 and 72 h
    ser = os.path.join(TOP, EB.SERIES[0])
    if hashlib.sha256(open(ser, "rb").read()).hexdigest() != EB.SERIES[1]:
        refuse(2, "the filed series is not the pinned file")
    rows = json.load(open(ser, encoding="utf-8"))["outputs"]["hourly"]
    years = sorted({r_["time"][:4] for r_ in rows})
    by_year = {y: [r_ for r_ in rows if r_["time"][:4] == y] for y in years}
    dayrat = {}
    for y in years:
        for dd in range(30):
            Rp = ER.Ratios(AC, [r_["G(i)"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]], [r_["T2m"] for r_ in by_year[y][dd * 24:(dd + 1) * 24]])
            dayrat[(y, dd)] = (Rp.typical(), Rp.adverse()[0])
    wins = []
    for y in years:
        for dd in range(27):
            for st in (6, 18):
                i0 = dd * 24 + st
                seg = by_year[y][i0:i0 + 72]
                days = [(i0 + i) // 24 for i in range(72)]
                wins.append({"st": st, "seg": seg, "vals": [seg[i]["G(i)"] * dayrat[(y, days[i])][0] for i in range(72)]})

    def cover(key, n, hours):
        res = []
        for w in wins:
            t_l = round(min(r_["T2m"] for r_ in w["seg"][:hours]), 2)
            res.append(crit(sim1(key, n, pr0, w["vals"][:hours], w["st"], t_l, hours)))
        return [sum(1 for x in res if x[i]) for i in range(3)]
    # reproduction: 72 h, 4S14P, WE TYP against weather_basis.out
    secA = wb_out.split("\nA. THE MODELLED HISTORICAL COVERAGE", 1)[1].split("\nB. ", 1)[0]
    mm = need(secA, r"^\s+4S14P tablet out\s+WE TYP\s+(\d+) of \d+ \(\s*[\d.]+ %\)\s+(\d+) of \d+ \(\s*[\d.]+ %\)\s+(\d+) of", "weather_basis.out 4S14P WE TYP")
    rep = cover("WE", 14, 72)
    P("4. THE MODELLED HISTORICAL COVERAGE, %d September windows of 2005 to 2020 at 40/0, TYP (weather_basis.out A's windows, the" % len(wins))
    P("   first 48 h of each for 48 h; the lid at each window's own minimum air over its hours): kept (no STOP) / COMB / EACH.")
    P("   Reproduction: 72 h, the 4S14P lid at WE reads %s against weather_basis.out's %s: %s" % (
        "/".join(str(x) for x in rep), "/".join(mm.groups()), "yes" if [int(x) for x in mm.groups()] == rep else "NO"))
    if [int(x) for x in mm.groups()] != rep:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "the coverage reproduction failed")
    res4 = {}
    for hours in (48, 72):
        for key in ("DRAWN", "NOM", "NOM90", "WE", "WE90"):
            c3 = cover(key, LID_A, hours)
            res4[(key, hours)] = c3
            P("   %d h %-6s both kept (4S9P lid): %s" % (hours, key, " / ".join("%3d (%4.1f %%)" % (x, 100.0 * x / len(wins)) for x in c3)))
    P("   MODELLED HISTORICAL COVERAGE: the share of past September windows the model carries, not a probability of success.")
    P("")
    P("END. Each line is the model's arithmetic; nothing is measured. No result here is demonstrated capability: the circuit as")
    P("drawn fails; the corrected path is HYPOTHETICAL and CONDITIONAL on three undocumented efficiencies.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
