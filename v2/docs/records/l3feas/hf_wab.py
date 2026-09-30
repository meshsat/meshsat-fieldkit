#!/usr/bin/env python3
"""hf_wab.py: the HF-plus-WAB feasibility assessment for Layer 3 (stream l3feas, MESHSAT-1357, 30 September 2026; the
owner's review of the decision brief: "Perform the bounded feasibility assessment needed to determine whether a credible
correction exists within the constraints. If no credible route exists, return a quantified trade-off to the owner. Do
not automatically delete HF, loosen installation conditions or mark the target satisfied.").

The combination: the tablet-out lid (4S14P, the HF set kept inside), SC-37's mean September day at 40/0, the WAB array
build, at energy_basis.py's WE on the CORRECTED PATH (case (iii), HYPOTHETICAL): NOT MET by 10.8 Wh.

PROTOTYPE DESIGN, desk arithmetic: nothing is built, powered or measured. Every energy figure is MODELED on a1elec's
energy_two_pack.py through energy_basis.py's set-up (imported, pinned); the electrical limits come from r11dep's
r11_dep.out (read, pinned to HEAD). Nothing here designs a correction or picks a target: it runs the two routes the
energy record already names, reports each pack hour by hour at the kit loads, and finds the evidence each route needs.

The routes (weather_basis.out C, the record's own rows):
  R1  U3's input limit at its 6.35 A clamp: a register setting inside the drafted entry. It stands on SLUSE66A 9.6.22
      (p.80: with a 10 mOhm sense, "50 mA to 6350 mA", "implemented through DAC clamp", no inductance condition) and on the
      6.35 A of every RSNS_RAC = 0b row of Table 9-1 (p.26). 9.3.5 (p.25) assumes both sense resistors at 10 mOhm where
      board A's R17 is 5 mOhm, and Table 9-1 has no row for board A's 4.7 uH, so neither is cited as its basis; its minimum INFERRED 100 mA under the setting as WE's 6.1 A is, and also at the front page's
      2.5 % (6.191 A), since SLUSE66A prints no minimum (r11dep C-7).
  R2  board E's stage at its maker curve's reading, 0.965 (curve_readings.out 2, INFERRED from another circuit): not a
      correction but a figure to establish (r11dep C-8).

Before any result it proves (exit 4 otherwise) that its runs reproduce energy_basis.out section 5's WE rows of the 4S14P
lid and weather_basis.out C's two rows for it.

Second issue (CHECK-1 of 24942a5f, B1 and minors 4 and 5): section 4 prints the Kelvin criterion each setting's current
through R11 needs, shows that the drafted criterion does not admit R1, gives the stage's input at each setting, cites the
6.35 A setting on SLUSE66A 9.6.22 and Table 9-1, and shows that ILIM_HIZ does not bind.

Run from the repository root:  python3 v2/docs/records/l3feas/hf_wab.py > v2/docs/records/l3feas/hf_wab.out
Deterministic. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
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
    sys.stderr.write("hf_wab: energy_basis.py is not the pinned file; refusing\n")
    sys.exit(2)
sys.path.insert(0, L3)
import energy_basis as EB  # noqa: E402
sys.path.insert(0, os.path.join(TOP, "v2", "ecad", "tools"))
import netlist_sexp as N  # noqa: E402
TP, ER = EB.TP, EB.ER

EB_OUT = "v2/docs/records/l3plane/energy_basis.out"
WB_OUT = "v2/docs/records/l3plane/weather_basis.out"
CURVES = "v2/docs/records/l3plane/curve_readings.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
N_LID = 14                  # the tablet-out lid, 4S14P: the HF set stays inside the kit
U3_TOL = 0.1                # SLUSE66A 9.6.22 p.80: 100 mA above the setting; the minimum mirrored (INFERRED), as WE's 6.1 A


def refuse(code, msg):
    sys.stderr.write("hf_wab: %s; refusing\n" % msg)
    sys.exit(code)


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def main():
    D0, PACK0, RES0, t2m = TP.load_model()
    EB.D0, EB.PACK0, EB.RES0 = D0, PACK0, RES0
    EB.TMIN = round(min(t2m), 2)
    eb_out = EB.head_equal(EB_OUT)
    wb_out = EB.head_equal(WB_OUT)
    curves = EB.head_equal(CURVES)
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
    v_min = vr["bands"][0][4]
    rd = EB.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EB.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in need(TP.PAR["v_ak"][1], r"([\d]+) / ([\d]+) / ([\d]+) mV", "v_ak").groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    st_mkr = float(need(curves, r"READING at 6 to 12 A on the 35 V curve \(board E's stage delivers up to about 12 A at 15\.1 V\): ([\d.]+) to", "the stage reading").group(1)) / 100.0
    clamp = TP.v("u3_iin_max_a")

    def we(i, extra=None):
        x = {"eta_u3": EB.u3_day(v_min, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    routes = {
        "WE": ("WE as restated, the combination's reference", 6.1, we(6.1)),
        "R1": ("R1: U3 at its %.2f A clamp, minimum %.2f A (INFERRED, 100 mA under, as WE's 6.1 A)" % (clamp, clamp - U3_TOL), clamp - U3_TOL, we(clamp - U3_TOL)),
        "R1lo": ("R1 at the front page's 2.5 %%: minimum %.3f A (INFERRED)" % (clamp * 0.975), clamp * 0.975, we(clamp * 0.975)),
        "R2": ("R2: board E's stage at its maker curve's reading %.3f (INFERRED, another circuit)" % st_mkr, 6.1, we(6.1, {"eta_st": st_mkr})),
    }

    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def run1(iin, ov, b, start, trace=None):
        d, pack, r, cfg = EB.setup(N_LID, pr0 * rat40[b], v_min, iin, ov)
        load0 = TP.LOAD
        TP.LOAD = load0 + ov.get("drain_w", 0.0)
        try:
            res = TP.sim(d, pack, r, EB.Series([prof0[(start + h) % 24] for h in range(72)]), 400.0, 200.0, start,
                         TP.v("t_base_c"), EB.TMIN, cfg, trace)
            ent = dict(TP.ENTRIES["_u3"])
            e_ch = TP.chain(d)[2]
            return res, ent, e_ch, TP.LOAD
        finally:
            TP.LOAD = load0

    def meanday(key, b, extra=None):
        _t, iin, ov = routes[key]
        ov = dict(ov)
        ov.update(extra or {})
        rs = [run1(iin, ov, b, s)[0] for s in (6, 18)]
        return {"ok": all(r_["ok"] for r_ in rs), "both": min(r_["low_t"] for r_ in rs), "base": min(r_["low_b"] for r_ in rs),
                "lid": min(r_["low_l"] for r_ in rs), "short": max(r_["short"] for r_ in rs)}

    def cellx(s):
        return ("%.1f (base %.1f, lid %.1f)" % (s["both"], s["base"], s["lid"])) if s["ok"] else ("NOT MET, %.1f unserved" % s["short"])

    def lines(s):
        return "STOP %s, COMB %s, EACH %s" % ("kept" if s["ok"] else "FAILS", "Y" if s["ok"] and s["both"] > EB.FLOOR else "N",
                                             "Y" if s["ok"] and s["base"] > EB.FLOOR and s["lid"] > EB.FLOOR else "N")

    o = []
    P = o.append
    P("THE HF-PLUS-WAB FEASIBILITY ASSESSMENT (hf_wab.py, stream l3feas, MESHSAT-1357). PROTOTYPE DESIGN: nothing built, powered")
    P("or measured. MODELED on a1elec's energy_two_pack.py through energy_basis.py's set-up (pinned), on the CORRECTED PATH (case")
    P("(iii), HYPOTHETICAL: every correction of r11dep's R11-DEPENDENCY.md assumed closed). The author's analysis, AI arithmetic;")
    P("not a qualified review and not the independent check. Nothing is designed and no target is picked.")
    P("")

    # 0. reproduction
    bad = 0
    sec5 = eb_out.split("\n5. THE CASES ON THE REFERENCE PLANE", 1)[1].split("\n6. ", 1)[0]
    row = need(sec5, r"^\s+4S14P\s+WE\s{2,}(.+?)\s{2,}[YN]/[YN]\s+(.+?)\s{2,}[YN]/[YN]\s*$", "energy_basis.out 4S14P WE")
    for bi, b in enumerate(("TYP", "WAB")):
        s = meanday("WE", b)
        want = row.group(1 + bi).strip()
        got = ("%6.1f (base %5.1f, lid %5.1f)" % (s["both"], s["base"], s["lid"])).strip() if s["ok"] else ("NOT MET, %5.1f unserved" % s["short"])
        if got != want:
            bad += 1
    secC = wb_out.split("\nC. CREDIBLE IMPROVEMENTS", 1)[1]
    for key, pat in (("R1", r"U3's input limit set to its 6\.35 A clamp.*?\s(\S+) / (\S+); \S+ / \S+\s"),
                     ("R2", r"board E's stage at its maker curve's reading 0\.965.*?\s(\S+) / (\S+); \S+ / \S+\s")):
        mm = need(secC, pat, "weather_basis.out C %s" % key)
        for bi, b in enumerate(("TYP", "WAB")):
            s = meanday(key, b)
            if ("%.1f" % s["both"] if s["ok"] else "NOT MET") != mm.group(1 + bi):
                bad += 1
    P("0. REPRODUCTION: energy_basis.out section 5's 4S14P WE row (TYP, WAB) and weather_basis.out C's clamp and stage rows for")
    P("   the 4S14P lid (TYP, WAB): %s" % ("yes" if bad == 0 else "NO (%d)" % bad))
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        refuse(4, "%d reproduction check(s) failed" % bad)
    P("")

    # 1. the combination and the routes, per pack
    P("1. EACH ROUTE AT THE KIT LOADS (the mean day at 40/0, the lid at %.2f C, the base at +%.0f C; PS-IDLE-SPEC %.1f W plus the" % (
        EB.TMIN, TP.v("t_base_c"), TP.LOAD))
    P("   lid path's standby drain %.3f W at the pack terminals; both packs full and aged at the start; each pack's store ends at" % drain_w)
    P("   its own 3.00 V line with the 5 % reserve, where the model stops drawing it and the kit runs on the other pack). Cells:")
    P("   both packs' lowest store (the base's, the lid's own lowest) in Wh, or the energy left unserved; the three lines: STOP")
    P("   (the kit never stops), COMB (both together above %.1f Wh), EACH (each pack above %.1f Wh)" % (EB.FLOOR, EB.FLOOR))
    res_all = {}
    for key in ("WE", "R1", "R1lo", "R2"):
        P("   %s" % routes[key][0])
        for b in ("TYP", "WAB"):
            s = meanday(key, b)
            res_all[(key, b)] = s
            P("     %s: %-40s %s" % (b, cellx(s), lines(s)))
    P("")

    # 2. hour by hour, WAB, the start with the lowest combined store
    P("2. HOUR BY HOUR, THE WAB BUILD (each start; UTC hours of the mean day; the node's power is U3's output):")
    for key in ("WE", "R1", "R2"):
        _t, iin, ov = routes[key]
        for start in (6, 18):
            tr = []
            res, ent, e_ch, load_w = run1(iin, ov, "WAB", start, tr)
            cap_node = min(ent["fe_out_w"], ent["u3_in_w"]) * e_ch
            at_cap = [x for x in tr if x[2] >= cap_node - 1e-6]
            lid_out = [x for x in tr if x[9] <= 1e-6]
            base_min = min(tr, key=lambda x: x[8])
            full_b = res["eb_full"]
            full_l = res["el_full"]
            P("   %s, start %02d UTC: U3's input cap %.1f W, %.1f W at the node; hours at the cap: %d of 72 (UTC %s)" % (
                key, start, min(ent["fe_out_w"], ent["u3_in_w"]), cap_node, len(at_cap),
                ", ".join(sorted({"%02d" % x[1] for x in at_cap}))))
            P("     base: full %.1f Wh, lowest %.1f Wh at hour %d (UTC %02d); lid: full %.1f Wh, lowest %.1f Wh; at its line for %d hours%s" % (
                full_b, base_min[8], base_min[0], base_min[1], full_l, res["low_l"], len(lid_out),
                (" (first at hour %d, UTC %02d; the base alone carries %.1f W then)" % (lid_out[0][0], lid_out[0][1], load_w)) if lid_out else ""))
            P("     the kit %s%s" % ("never stops" if res["ok"] else "STOPS at hour %d" % res["first_stop"],
                                    "" if res["ok"] else ", %.1f Wh unserved" % res["short"]))
    P("")

    # 3. what each route needs of the evidence: thresholds at WAB (and TYP), each input alone
    def thr(key, what, lo, hi, line):
        _t, iin, ov0 = routes[key]

        def ok(x):
            s = meanday(key, "WAB", {what: x})
            return s["ok"] and (s["both"] > EB.FLOOR if line == "COMB" else True)
        if not ok(hi):
            return None
        if ok(lo):
            return lo
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if ok(mid):
                hi = mid
            else:
                lo = mid
        return hi
    P("3. WHAT EACH ROUTE NEEDS OF THE MISSING EVIDENCE: the least value of each undocumented input, alone, at which the WAB")
    P("   build still passes (search 0.80 to 1.00; the rest at the route's values)")
    for key in ("WE", "R1", "R1lo", "R2"):
        parts = []
        for what, lab in (("chg_eta", "charge efficiency"), ("eta_st", "stage"), ("eta_fe", "front end")):
            for line in ("STOP", "COMB"):
                t = thr(key, what, 0.80, 1.00, line)
                parts.append("%s %s %s" % (lab, line, ("%.3f" % t) if t is not None else "none"))
        P("   %-5s %s" % (key, "; ".join(parts)))
    P("   the values WE carries: charge %.2f (INFERRED, no document), stage %.2f and front end %.2f (DECLARED); the makers' readings" % (
        ce["value"], ch[0]["eta"], ch[1]["eta"]))
    P("   of other circuits: stage %.3f (curve_readings.out 2), front end %s (curve_readings.out 1)" % (
        st_mkr, need(curves, r"READING at 5\.5 to 6 A \(board A's front end carries U3's 6\.1 A\): ([\d.]+) to ([\d.]+) %", "front end reading").group(1) + " %"))
    P("")

    # 4. R1 against the electrical record
    prop_min = float(need(r11, r"proposed, R11 6\.2 mOhm:\s+([\d.]+) /", "r11_dep.out proposed band").group(1))
    other = float(need(r11, r"plus ([\d.]+) A of VBUS20's other loads", "r11_dep.out other loads").group(1))
    loads4 = float(need(r11, r"with four FETs' ([\d.]+) A", "r11_dep.out four-FET loads").group(1))
    mk = need(r11, r"the worst can reaches 2\.8 A at a front end current of ([\d.]+) A matched and ([\d.]+) A at a 2:1 ESR spread", "r11_dep.out the bank")
    i_can0, i_can2 = float(mk.group(1)), float(mk.group(2))
    acc = 0.025
    u3_set = [clamp, TP.v("u3_iin_draft_a")]
    # the Kelvin budget's own terms, as r11_dep.out 3 states them
    vs_min = float(need(r11, r"VSNS (\d+) / \d+ / \d+ mV", "r11_dep.out VSNS").group(1)) * 1e-3
    offs = float(need(r11, r"the ISNS bias over the 100 Ohm filter \+-([\d.]+) mV", "r11_dep.out the bias offset").group(1)) * 1e-3
    tol = float(need(r11, r"R11 at \+-(\d+) %, its TCR over\s+(\d+) K", "r11_dep.out R11's tolerance").group(1)) / 100.0
    dt_r = float(need(r11, r"R11 at \+-\d+ %, its TCR over\s+(\d+) K", "r11_dep.out R11's temperature span").group(1))
    tcr = float(need(r11, r"TCR \+-(\d+) ppm/K for 2 to 500 mOhm", "r11_dep.out R11's TCR").group(1)) * 1e-6
    cu = float(need(r11, r"\(copper ([\d.]+) /K", "r11_dep.out copper's coefficient").group(1))
    t_hot = float(need(r11, r"an ASSUMED (\d+) C", "r11_dep.out R11's assumed temperature").group(1))
    t_air = float(need(r11, r"the worst inside air in use ([\d.]+) C", "r11_dep.out the worst inside air").group(1))
    crit25 = float(need(r11, r"the criterion is ([\d.]+) mOhm at 25 C", "r11_dep.out the drafted criterion").group(1)) * 1e-3
    r11_max = 0.0062 * (1 + tol) * (1 + tcr * dt_r)
    v_bus = float(need(r11, r"at VBUS20's ([\d.]+) V maximum, efficiency ([\d.]+) DECLARED", "r11_dep.out the bus").group(1))
    eta = float(need(r11, r"at VBUS20's [\d.]+ V maximum, efficiency ([\d.]+) DECLARED", "r11_dep.out the efficiency").group(1))
    P("4. R1 AGAINST THE ELECTRICAL RECORD (r11dep's r11_dep.out; INFERRED arithmetic)")
    for s_ in u3_set:
        mx = max(s_ + U3_TOL, s_ * (1 + acc))
        P("   U3 set at %.2f A: its maximum %.3f A (the larger of +100 mA, p.80, and +2.5 %%, p.1); through R11 %.3f A with the carried" % (s_, mx, mx + other))
        P("     %.3f A, %.3f A with four FETs' %.3f A; the front end's stacked minimum %.3f A leaves %+.3f A and %+.3f A (with Kelvin" % (
            other, mx + loads4, loads4, prop_min, prop_min - mx - other, prop_min - mx - loads4))
        P("     taps, r11dep C-1); VBUS20's bank reaches 2.8 A a can at %.2f A matched and %.2f A at a 2:1 spread: in service %s" % (
            i_can0, i_can2, "WITHIN" if mx + other <= i_can2 else ("OVER at a 2:1 spread (%.1f %% of 2.8 A), WITHIN matched" % (100.0 * (mx + other) / i_can2)
                                                                   if mx + other <= i_can0 else "OVER")))
        kel = [(vs_min - offs) / i_ - r11_max for i_ in (mx + other, mx + loads4)]
        P("     THE KELVIN CRITERION this current needs (the shared copper between R11's pads and its taps, both together, for the")
        P("     margin above to hold): %.3f mOhm working, %.3f mOhm at 25 C with the copper at %.0f C, %.3f mOhm at %.1f C (%.2f mV at 6.0 A);" % (
            kel[0] * 1e3, kel[0] / (1 + cu * (t_hot - 25.0)) * 1e3, t_hot, kel[0] / (1 + cu * (t_air - 25.0)) * 1e3, t_air,
            kel[0] / (1 + cu * (t_hot - 25.0)) * 6.0 * 1e3))
        P("     with four FETs' loads %.3f, %.3f and %.3f mOhm (%.2f mV at 6.0 A); the stage's input in service %.1f W (%.3f A at %.3f V" % (
            kel[1] * 1e3, kel[1] / (1 + cu * (t_hot - 25.0)) * 1e3, kel[1] / (1 + cu * (t_air - 25.0)) * 1e3,
            kel[1] / (1 + cu * (t_hot - 25.0)) * 6.0 * 1e3, (mx + other) * v_bus / eta / eta, mx + other, v_bus))
        P("     over %.2f twice)" % eta)
    i_r1 = max(clamp + U3_TOL, clamp * (1 + acc)) + other
    v_sensed = i_r1 * (r11_max + crit25 * (1 + cu * (t_hot - 25.0)))
    P("   THE DRAFTED CRITERION DOES NOT ADMIT R1: a layout that closes C-1 at its %.2f mOhm (25 C) senses %.2f mV at %.3f A with the" % (
        crit25 * 1e3, v_sensed * 1e3, i_r1))
    P("     copper at %.0f C, over the %.1f mV minimum (VSNS %.0f mV less the %.1f mV bias offset): the front end can limit first" % (
        t_hot, (vs_min - offs) * 1e3, vs_min * 1e3, offs * 1e3))
    # ILIM_HIZ does not bind
    bq = os.path.join(TOP, "v2", "vendor", "ti", "bq25731-datasheet.pdf")
    pg = {n: " ".join(subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), bq, "-"], capture_output=True, text=True,
                                     check=True).stdout.split()) for n in (6, 11, 26, 80)}
    need(pg[6], r"V\(ILIM_HIZ\) = 1 V \+ 40 × IDPM ×", "SLUSE66A p.6 the ILIM_HIZ formula")
    regn = tuple(float(x) for x in need(pg[11], r"VREGN_REG .*?VVBUS = 10 V ([\d.]+) (\d+) ([\d.]+) V", "SLUSE66A p.11 REGN").groups())
    need(pg[26], r"The actual input current limit being adopted by the device is the lower setting of IIN_DPM and ILIM_HIZ pin", "SLUSE66A p.26 9.3.6")
    need(pg[80], r"50 mA to 6350 mA, with 50-mA resolution\. The upper boundary is implemented through DAC clamp", "SLUSE66A p.80 the clamp")
    need(pg[80], r"pull ILIM_HIZ pin above 4\.0 V", "SLUSE66A p.80 the pin disabled above 4.0 V")
    na = N.load(os.path.join(TOP, "v2", "ecad", "pcb-a-power-a23", "out", "pcb-a-power.net"))
    ra = {r_: (na["components"][r_]["value"], {q: v_["net"] for q, v_ in na["pins"][r_].items()}) for r_ in ("R19", "R20", "R16")}
    if not (ra["R19"][1] == {"1": "REGN", "2": "CHG_ILIM"} and ra["R20"][1] == {"1": "CHG_ILIM", "2": "GND"} and ra["R16"][0].startswith("10mOhm")):
        refuse(3, "board A's ILIM_HIZ divider or RAC is not as read")
    r19 = float(ra["R19"][0].split("k")[0]) * 1e3
    r20 = float(ra["R20"][0].split("k")[0]) * 1e3
    v_lo, v_ty = regn[0] * r20 / (r19 + r20), regn[1] * r20 / (r19 + r20)
    P("   ILIM_HIZ does not bind (SLUSE66A 9.3.6, p.26: the lower of IIN_DPM and the pin): R19 %s from REGN over R20 %s (NETLIST) put the" % (
        ra["R19"][0].split(" ")[0], ra["R20"][0].split(" ")[0]))
    P("     pin at %.2f V at REGN's %.1f V minimum (p.11): %.2f A by V = 1 V + 40 x IDPM x RAC (p.6, RAC 10 mOhm), above R1's %.3f A;" % (
        v_lo, regn[0], (v_lo - 1.0) / 40.0 / 0.010, i_r1 - other))
    P("     at REGN's %.1f V typical %.2f V, above the 4.0 V that disables the pin (p.80)" % (regn[1], v_ty))
    P("   R1 raises U3's input by %.2f A over the drafted 6.2 A setting: the front end's output, the stage's and the copper's in-service" % (clamp - 6.2))
    pmax = {b: max(TP.EB.panel_w(g, 400.0, pr0 * rat40[b]) for g in prof0) for b in ("TYP", "WAB")}
    P("   currents rise by the same %.1f %% (INFERRED). The array's largest hour on the mean day is %.1f W (TYP) and %.1f W (WAB) into" % (
        100.0 * (clamp - 6.2) / 6.2, pmax["TYP"], pmax["WAB"]))
    P("     the stage, under the model's 200 W window, which board E does not implement (a1solar ARRAY.md 3): the window never binds")
    P("     on this day; U3's input cap does, in the hours section 2 lists")
    P("")
    P("END. Each line is the model's arithmetic on the corrected path; nothing is measured, designed or chosen.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
