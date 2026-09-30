#!/usr/bin/env python3
"""l4e_replay.py: layer 4 task L4-E2, the energy architecture comparison under ONE assumption set (MESHSAT-1357,
written 30 September and 1 October 2026). It replays the checked layer 3 energy model with the solar stage's input
clipped at REQ-016's 100 W instead of the 200 W window of proposal P-03, for the two architectures the collaborator's
L4-E1 assessment names:

  A1  D-06's single 4S3P pack of Samsung INR18650-35E in the east pocket (no owner ruling changes);
  A2  the base 4S6P plus a separately protected lid 4S9P, both lid functions kept (an explicit proposal that changes
      D-06 only; Option A(i)'s arrangement A of a1mech).

PROTOTYPE DESIGN, desk arithmetic: nothing is built, bought, powered or measured. Every energy figure is MODELED on
a1elec's energy_two_pack.py through l3plane's energy_basis.py set-up (both pinned, imported unchanged). The corrected
power path is HYPOTHETICAL; every WE figure is CONDITIONAL on the three undocumented efficiencies (C-8).

Before any result it proves (exit 4 otherwise):
  0a  l3batt's runtime.py, re-run in a child process, reproduces the checked runtime.out byte for byte;
  0b  this harness reproduces runtime.out section 1's D06 and A35 rows, all twenty cells of section 2 (400 Wp, 200 W)
      and section 3's least lid at 48 h and 72 h for NOM, WE and NOM90 (TYP and WAB);
  0c  this harness reproduces three_cases.out's AS DRAWN rows at WE for the both-kept lid (the drawn case used here);
  0d  the single-pack use of the two-pack model (A1: the lid off) reproduces energy_budget.out section 5b's two
      PS-IDLE-SPEC September rows (a 100 Wp panel in the 100 W window, the record's chain): first stop and unserved Wh.
Only then does it change one input, the stage window, from 200 W to 100 W, and print the comparison.

Run from the repository root:  python3 v2/docs/records/l4e/l4e_replay.py > v2/docs/records/l4e/l4e_replay.out
Deterministic; standard library plus PyYAML (through the imported model). About one minute, most of it 0a.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction failed."""
import hashlib
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
try:
    os.nice(10)                 # a shared host: stay behind interactive work
except OSError:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = os.path.join(TOP, "v2", "docs", "records")
PINS = {
    "l3batt/runtime.py": "885bd4fadf9000cf45f7f66e2ba518b7b390e1092e9a0246e6f6a52c760897ee",
    "l3batt/runtime.out": "87d9c1ee590597638c57aa97c384c217af9eb36044a2db39e27194a88047fc13",
    "l3plane/energy_basis.py": "7e2f19bff6b63ba5bfdb7ce430dc32e143613f2339cd1bc88e15f71dd022fb47",
    "l3plane/three_cases.py": "2395d75e48c9787773373aefcd02aeaeb04f5cfcf9d7c4a948617e1547bfab68",
    "l3plane/three_cases.out": "8119987a20fad08cae0edc928726c847b1f5ec41f81cfd9552849793567e96be",
    "energy/energy_budget.out": "5b11a90df10fee7bcafbb4e9931e05eafbc91120083e6e33815b12bce943e4dd",
    "r11dep/r11_dep.out": "f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209",
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def refuse(code, msg):
    sys.stderr.write("l4e_replay: %s; refusing\n" % msg)
    sys.exit(code)


for _rel, _want in PINS.items():
    if sha(os.path.join(REC, _rel)) != _want:
        refuse(2, "%s is not the pinned file" % _rel)
sys.path.insert(0, os.path.join(REC, "l3plane"))
import energy_basis as EBS  # noqa: E402
TP, ER = EBS.TP, EBS.ER
BUD = TP.EB                 # records/energy/energy_budget.py, as energy_two_pack.py imports it
EF = EBS.EF                 # records/s117/efficiency.py

RUNTIME_OUT = "v2/docs/records/l3batt/runtime.out"
THREE_OUT = "v2/docs/records/l3plane/three_cases.out"
BUDGET_OUT = "v2/docs/records/energy/energy_budget.out"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
WP_TRACE = 400.0            # the checked availability series: 400 Wp in 2S2P (P-03), runtime.py's call
WIN_P03 = 200.0             # P-03's stage window, the one runtime.out used
T_COLD = -10.0              # REQ-072's battery-only cold case (REQ-046's discharge floor)
LID_A = 9                   # a1mech arrangement A (HF and the tablet kept): 4S9P
BASE_A2 = 6                 # the base pockets' 4S6P (energy_two_pack.NP_B)
BASE_A1 = 3                 # D-06's 4S3P
U3_TOL = 0.1                # three_cases.py: U3's minimum 0.1 A under its setting (INFERRED from SLUSE66A p.80's maximum)


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not parsed" % what)
    return m


def main():
    o = []
    P = o.append

    # ------------------------------------------------------------------------------------------ 0a: runtime.py again
    rt = subprocess.run([sys.executable, "-B", os.path.join(REC, "l3batt", "runtime.py")], cwd=TOP, capture_output=True)
    rt_ok = rt.returncode == 0 and rt.stdout == open(os.path.join(TOP, RUNTIME_OUT), "rb").read()
    if not rt_ok:
        refuse(4, "runtime.py's re-run does not reproduce runtime.out (exit %d)" % rt.returncode)

    # ------------------------------------------------------------------------------------------ the model, as runtime.py sets it up
    D0, PACK0, RES0, t2m = TP.load_model()
    EBS.D0, EBS.PACK0, EBS.RES0 = D0, PACK0, RES0
    EBS.TMIN = round(min(t2m), 2)
    notes = " ".join(EBS.head_equal(EBS.PANEL).split())
    m = need(notes, r"0\.01 h step lowers the lowest stores by about ([\d.]+) to ([\d.]+) Wh \(B\) and ([\d.]+) to ([\d.]+) Wh \(C\)", "NOTES step")
    md = need(notes, r"standby drain \(about ([\d.]+) to ([\d.]+) Wh over 72 h\)", "NOTES drain")
    EBS.FLOOR = FLOOR = max(float(m.group(2)), float(m.group(4)))
    drain_w = float(md.group(2)) / D0["mission"]["hours"]
    vr = EBS.VR.compute()
    AC, _e, _t = ER.pinned_import()
    AC.check_pins()
    pr0 = RES0["pr"]
    v_min, v_nom = vr["bands"][0][4], vr["nominal"]
    rd = EBS.bracket(TP.PAR["r_lid_dsg"][1], "r_lid_dsg")
    rc_ = EBS.bracket(TP.PAR["r_lid_chg"][1], "r_lid_chg")
    vak = tuple(float(x) / 1000.0 for x in need(TP.PAR["v_ak"][1], r"([\d]+) / ([\d]+) / ([\d]+) mV", "v_ak").groups())
    ch = D0["solar"]["chain"]
    ce = D0["pack"]["charge"]["energy_efficiency"]
    win_req016 = float(D0["solar"]["window"]["stage_max_w_in"]["value"])
    if win_req016 != 100.0 or "REQ-016" not in D0["solar"]["window"]["stage_max_w_in"]["src"]:
        refuse(3, "energy_inputs.yaml's stage window is not REQ-016's 100 W")
    chg_a1_cell = D0["pack"]["charge"]["current_a"]["value"] / D0["pack"]["parallel"]   # 3.06 A / 3 = 1.02 A a cell
    r11 = EBS.head_equal(R11_OUT)
    held = tuple(float(x) for x in need(r11, r"held, R11 10\.0 mOhm:\s+([\d.]+) / ([\d.]+) / ([\d.]+) A", "r11_dep.out held band").groups())
    other = float(need(r11, r"plus ([\d.]+) A of VBUS20's other loads", "r11_dep.out other loads").group(1))
    fe_held = held[0] - other
    u3_e1, u3_e2 = TP.v("u3_iin_e1_a"), TP.v("u3_iin_draft_a")
    load0 = TP.LOAD

    def we(v, i, extra=None):
        x = {"eta_u3": EBS.u3_day(v, i, "lower"), "eta_b": TP.v("eta_u3b_lo"), "v_ak": vak[2], "r_dsg": rd[1], "r_chg": rc_[1],
             "drain_w": drain_w}
        x.update(extra or {})
        return x
    lo3 = {"eta_st": ch[0]["low"], "eta_fe": ch[1]["low"], "chg_eta": ce["low"]}
    hi3 = {"eta_st": ch[0]["high"], "eta_fe": ch[1]["high"], "chg_eta": ce["high"]}
    one3 = {"eta_st": 1.0, "eta_fe": 1.0, "chg_eta": 1.0}
    # (bus, U3's input limit, overrides): runtime.py's five cases, three_cases.py's AS DRAWN at WE, and the sensitivities
    CASES = {
        "DRAWN": (v_nom, u3_e1, {"eta_u3": EBS.u3_day(v_nom, u3_e1, "TI"), "fe_i": fe_held}),
        "NOM": (v_nom, u3_e2, {"eta_u3": EBS.u3_day(v_nom, u3_e2, "TI")}),
        "NOM90": (v_nom, u3_e2, dict({"eta_u3": EBS.u3_day(v_nom, u3_e2, "TI")}, **lo3)),
        "WE": (v_min, 6.1, we(v_min, 6.1)),
        "WE90": (v_min, 6.1, we(v_min, 6.1, lo3)),
        "DRAWN-WE": (v_min, u3_e1 - U3_TOL, we(v_min, min(u3_e1 - U3_TOL, fe_held), {"fe_i": fe_held})),
        "WE97": (v_min, 6.1, we(v_min, 6.1, hi3)),
        "WE100": (v_min, 6.1, we(v_min, 6.1, one3)),
        "REC": (v_nom, u3_e2, {}),
    }
    node0 = TP.node_power

    def node_collapse(d, res4, g, wp, window, entry):
        """r11dep A-2 / B-5's inferred collapse (three_cases.py's bound): the charge path delivers U3's cap or nothing."""
        if entry is None:
            return node0(d, res4, g, wp, window, entry)
        e_st, e_fe, e_ch = TP.chain(d)
        avail = min(BUD.panel_w(g, wp, res4["pr"]), window) * e_st * e_fe
        cap = min(entry["fe_out_w"], entry["u3_in_w"])
        return cap * e_ch if avail >= cap else 0.0

    G40, TA40, _ = ER.september(ER.plane_file(40, 0))
    R40 = ER.Ratios(AC, G40, TA40)
    rat40 = {"TYP": R40.typical(), "WAB": R40.adverse()[0]}
    prof0 = RES0["months"][TP.MONTH]["profile"]

    def run(arch, key, n, build, start, hours, window, wp=WP_TRACE, collapse=False, load_w=None, chg_cell=None,
            account=False, ratio=None, entry=None, ov_extra=None, t_l=None):
        """One run of energy_two_pack.sim(). arch A2: the base 4S6P and a lid of n in parallel at the lid's temperature;
        arch A1: one pack of n in parallel at the base temperature, no lid (so no lid path and no lid drain)."""
        vb, iin, ov = CASES[key]
        ov = dict(ov, **(ov_extra or {}))
        pr = pr0 * (rat40[build] if ratio is None else ratio)
        vals = [prof0[(start + h) % 24] for h in range(hours)]
        saved = (TP.NP_B, TP.NP_L, TP.NP_T, TP.LOAD, TP.node_power)
        try:
            if arch == "A2":
                d, pack, r, cfg = EBS.setup(n, pr, vb, iin, ov)
                drain = ov.get("drain_w", 0.0)
            else:
                d, pack, r, cfg = EBS.setup(0, pr, vb, iin, ov)
                TP.NP_B, TP.NP_L, TP.NP_T = n, 0, n
                cfg["lid"] = False
                cfg["chg_a_b"] = (chg_a1_cell if chg_cell is None else chg_cell) * n
                drain = 0.0
            if entry is not None:
                cfg["entry"] = entry
            d = dict(d)
            d["mission"] = dict(d["mission"], hours=hours)
            TP.LOAD = (load0 if load_w is None else load_w) + drain
            if collapse:
                TP.node_power = node_collapse
            tr = [] if account else None
            res = TP.sim(d, pack, r, EBS.Series(vals), wp, window, start, TP.v("t_base_c"), EBS.TMIN if t_l is None else t_l, cfg, tr)
            if account:
                res["acct"] = acct(d, r, cfg, res, tr, vals, wp, window, collapse, TP.LOAD, hours)
            res["load"] = TP.LOAD
            return res
        finally:
            TP.NP_B, TP.NP_L, TP.NP_T, TP.LOAD, TP.node_power = saved

    def acct(d, r, cfg, res, tr, vals, wp, window, collapse, load, hours):
        """The per-pack and kit energy account of one run, from the model's own chain and hour trace (Wh)."""
        e_st, e_fe, e_ch = TP.chain(d)
        ent = TP.ENTRIES[cfg["entry"]]
        cap = min(ent["fe_out_w"], ent["u3_in_w"]) if ent is not None else float("inf")
        a = dict.fromkeys(("arr", "clip", "stage_in", "bus_avail", "not_taken", "u3_loss", "node", "sun_load", "offered",
                           "accepted", "spill", "stored", "drawn", "cap_hours", "full_h"), 0.0)
        eb, el = res["eb_full"], res["el_full"]
        cut_b = cut_l = None
        worst_dev = 0.0
        for i, row in enumerate(tr):
            h, _hh, p_sun, ld, a_b, a_l, _d_b, _d_l, e_b, e_l, running = row
            g = vals[i]
            p_arr = BUD.panel_w(g, wp, r["pr"])
            p_in = min(p_arr, window)
            avail = p_in * e_st * e_fe
            taken = ((cap if avail >= cap else 0.0) if collapse else min(avail, cap)) if ent is not None else avail
            worst_dev = max(worst_dev, abs(taken * e_ch - p_sun))
            a["arr"] += p_arr
            a["clip"] += p_arr - p_in
            a["stage_in"] += p_in
            a["bus_avail"] += avail
            a["not_taken"] += avail - taken
            a["u3_loss"] += taken * (1.0 - e_ch)
            a["node"] += p_sun
            a["cap_hours"] += 1.0 if (ent is not None and avail > cap) else 0.0
            a["sun_load"] += min(p_sun, ld)
            a["offered"] += max(0.0, p_sun - ld)
            a["accepted"] += a_b + a_l
            dlt = (e_b + e_l) - (eb + el)
            if dlt >= 0:
                a["stored"] += dlt
            else:
                a["drawn"] -= dlt
            eb, el = e_b, e_l
            if cfg["base"] and cut_b is None and e_b <= 1e-9:
                cut_b = h
            if cfg["lid"] and cut_l is None and e_l <= 1e-9:
                cut_l = h
            if ld > 0 and running:
                a["full_h"] += 1
        a["spill"] = a["offered"] - a["accepted"]
        a["chg_loss"] = a["accepted"] - a["stored"]
        a["dsg_path"] = res["loss"]["dsg_path"]
        a["asked"] = load * hours
        a["unserved"] = res["short"]
        a["served"] = a["asked"] - res["short"]
        a["start"] = res["eb_full"] + res["el_full"]
        a["end"] = res["end_b"] + res["end_l"]
        a["closure"] = a["start"] + a["stored"] - a["drawn"] - a["end"]
        a["cut_b"], a["cut_l"] = cut_b, cut_l
        a["node_dev"] = worst_dev
        return a

    def meanday(arch, key, n, build, hours, window, **kw):
        rs = [run(arch, key, n, build, s, hours, window, **kw) for s in (6, 18)]
        stops = [r_["first_stop"] for r_ in rs if r_["first_stop"] is not None]
        return {"ok": all(r_["ok"] for r_ in rs), "both": min(r_["low_t"] for r_ in rs), "base": min(r_["low_b"] for r_ in rs),
                "lid": min(r_["low_l"] for r_ in rs), "short": max(r_["short"] for r_ in rs), "stop": min(stops) if stops else None,
                "stops": [r_["first_stop"] for r_ in rs], "shorts": [r_["short"] for r_ in rs],
                "el": rs[0]["el_full"], "eb": rs[0]["eb_full"], "rs": rs}

    def cellx(s):
        if s["ok"]:
            return "%.1f (base %.1f, lid %.1f) %s/%s" % (s["both"], s["base"], s["lid"], "Y" if s["both"] > FLOOR else "N",
                                                         "Y" if s["base"] > FLOOR and s["lid"] > FLOOR else "N")
        return "NOT MET, stops at h %s, %.1f unserved" % ("/".join("-" if x is None else str(x) for x in s["stops"]), s["short"])

    def least(arch, key, build, hours, window, lo, hi, iters, **kw):
        def ok(x):
            s = meanday(arch, key, x, build, hours, window, **kw)
            return s["ok"] and s["both"] > FLOOR
        if not ok(hi):
            return None
        for _ in range(iters):
            mid = 0.5 * (lo + hi)
            if ok(mid):
                hi = mid
            else:
                lo = mid
        return hi

    # ------------------------------------------------------------------------------------------ 0b to 0d: this harness
    rto = open(os.path.join(TOP, RUNTIME_OUT), encoding="utf-8").read()
    bad = []
    pk = PACK0
    # section 1: D06 and A35 (runtime.py's own arithmetic, reproduced here)
    e20 = pk.usable_wh(load0, 20.0, pk.age80, "3v00", BASE_A1)[0]
    ecd = pk.usable_wh(load0, T_COLD, pk.age80, "3v00", BASE_A1)[0]

    def lid_loss(p_l, v_l):
        i = p_l / v_l
        return (i * vak[1] + i * i * TP.v("r_lid_dsg")) / p_l
    pb, pl = load0 * BASE_A2 / (BASE_A2 + LID_A), load0 * LID_A / (BASE_A2 + LID_A)
    v_l = pk.n_s * 3.60
    a2_only = []
    for t_ in (20.0, T_COLD):
        eb_ = pk.usable_wh(pb, t_, pk.age80, "3v00", BASE_A2)[0]
        el_ = pk.usable_wh(pl, t_, pk.age80, "3v00", LID_A)[0] * (1 - lid_loss(pl, v_l))
        a2_only.append((eb_, el_))
    a1_bo = (e20, ecd, e20 / load0, ecd / load0)
    ld2 = load0 + drain_w
    a2_bo = (sum(a2_only[0]), sum(a2_only[1]), sum(a2_only[0]) / ld2, sum(a2_only[1]) / ld2)
    for lab, row in (("D06: D-06's 4S3P of 35E (12 cells), no lid pack", a1_bo), ("A35: A(i) base 4S6P + lid 4S9P of 35E (60 cells)", a2_bo)):
        want = "   %-58s usable %6.1f Wh / %6.1f Wh: %5.2f h at +20 C, %5.2f h at %.0f C" % ((lab,) + row + (T_COLD,))
        if want not in rto:
            bad.append("runtime.out 1 %s" % lab[:3])
    # section 2: twenty cells
    sec2 = rto.split("\n2. BATTERY PLUS SOLAR", 1)[1].split("\n3. ", 1)[0]
    for hours in (48, 72):
        blk = sec2.split("   %d HOURS\n" % hours, 1)[1]
        for key in ("DRAWN", "NOM", "NOM90", "WE", "WE90"):
            line = "     %-8s TYP %-52s WAB %s" % (key, cellx(meanday("A2", key, LID_A, "TYP", hours, WIN_P03)),
                                                   cellx(meanday("A2", key, LID_A, "WAB", hours, WIN_P03)))
            if line not in blk:
                bad.append("runtime.out 2 %s %d h" % (key, hours))
    # section 3: the least lid, 48 and 72 h, NOM, WE, NOM90, TYP and WAB (runtime.py's bounds: 1 to 40, 30 steps)
    sec3 = rto.split("\n3. THE STORE THAT CARRIES", 1)[1].split("\n4. ", 1)[0]
    n3 = 0
    for hours in (48, 72):
        for key in ("NOM", "WE", "NOM90"):
            for b in ("TYP", "WAB"):
                x = least("A2", key, b, hours, WIN_P03, 1.0, 40.0, 30)
                s9, sx = meanday("A2", key, LID_A, b, hours, WIN_P03), meanday("A2", key, x, b, hours, WIN_P03)
                line = "     %d h %-6s %s: lid 4S%.2fP, against the both-kept 4S9P: %+.1f 35E cells, %+.1f Wh usable" % (
                    hours, key, b, x, 4 * (x - LID_A), sx["el"] - s9["el"])
                n3 += 1
                if line not in sec3:
                    bad.append("runtime.out 3 %s %s %d h" % (key, b, hours))
    # 0c: three_cases.out, AS DRAWN at WE inputs, the both-kept lid
    tco = EBS.head_equal(THREE_OUT)
    blk = tco.split("AS DRAWN, WE inputs:", 1)[1].split("\n   DERATED", 1)[0]
    mrow = need(blk, r"^\s+4S9P both kept\s+TYP NOT MET,\s+([\d.]+) unserved\s+N/N\s+WAB NOT MET,\s+([\d.]+) unserved", "three_cases.out drawn WE 4S9P")
    tc_rep = [meanday("A2", "DRAWN-WE", LID_A, b, 72, WIN_P03) for b in ("TYP", "WAB")]
    tc_ok = all((not s["ok"]) and "%.1f" % s["short"] == mrow.group(1 + i) for i, s in enumerate(tc_rep))
    if not tc_ok:
        bad.append("three_cases.out AS DRAWN WE 4S9P")
    # 0d: the single-pack use (A1 with the lid off) against energy_budget.out 5b (100 Wp, 100 W, the record's chain, E3)
    bo = EBS.head_equal(BUDGET_OUT)
    b5 = {}
    for st in ("06:00", "18:00"):
        mm = need(bo, r"^\s+PS-IDLE-SPEC\s+42\.8\s+September\s+%s\s+([\d.]+)\s+[\d.]+\s+\d+\s+[\d.]+\s+(\d+)\s+(\d+)\s+([\d.]+)\s+NOT MET" % st,
                  "energy_budget.out 5b %s" % st)
        b5[st] = mm.groups()
    rep_d = {}
    for st, s_h in (("06:00", 6), ("18:00", 18)):
        rr = run("A1", "REC", BASE_A1, "TYP", s_h, 72, win_req016, wp=100.0, ratio=1.0, entry="E3", account=True)
        rep_d[st] = ("%.1f" % rr["eb_full"], str(rr["first_stop"]), "%d" % rr["acct"]["full_h"], "%.1f" % rr["short"])
    # the E3 run must carry the record's own chain, not a case's: check it
    d_chk = EBS.setup(0, pr0, v_nom, u3_e2, {})[0]
    chain_ok = abs(TP.chain(d_chk)[0] * TP.chain(d_chk)[1] * TP.chain(d_chk)[2] - RES0["eta"]) < 1e-12
    b5_ok = chain_ok and all(rep_d[st] == b5[st] for st in b5)
    if not b5_ok:
        bad.append("energy_budget.out 5b")
    if bad:
        sys.stdout.write("REPRODUCTION FAILED: %s\n" % "; ".join(bad))
        refuse(4, "%d reproduction check(s) failed" % len(bad))

    # ------------------------------------------------------------------------------------------ the header and section 0
    P("L4-E2: THE ENERGY ARCHITECTURE REPLAY UNDER REQ-016'S 100 W WINDOW (l4e_replay.py, layer 4, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing built, bought, powered or measured. MODELED on a1elec's energy_two_pack.py through l3plane's")
    P("energy_basis.py set-up (both pinned, imported unchanged). The corrected power path is HYPOTHETICAL; every WE figure is")
    P("CONDITIONAL on the three undocumented efficiencies (C-8). The author's analysis, AI arithmetic; not a qualified review and")
    P("not the independent check.")
    P("")
    P("0. REPRODUCTION (before any result)")
    P("   0a l3batt's runtime.py re-run in a child process reproduces runtime.out byte for byte (sha256 %s): yes" % PINS["l3batt/runtime.out"][:16])
    P("   0b this harness reproduces runtime.out section 1's D06 and A35 rows, the twenty cells of section 2 (400 Wp, 200 W) and")
    P("      section 3's %d least-lid lines (48 and 72 h; NOM, WE, NOM90; TYP and WAB): yes" % n3)
    P("   0c this harness reproduces three_cases.out's AS DRAWN rows at WE inputs, the both-kept lid, 72 h: TYP %.1f, WAB %.1f Wh" % (
        tc_rep[0]["short"], tc_rep[1]["short"]))
    P("      unserved: yes")
    P("   0d the single-pack use (the lid off) reproduces energy_budget.out 5b, PS-IDLE-SPEC, September, a 100 Wp panel in the")
    P("      100 W window on the record's own chain: 06 UTC usable %s Wh, first stop h %s, %s h run, %s Wh unserved; 18 UTC first" % (
        rep_d["06:00"][0], rep_d["06:00"][1], rep_d["06:00"][2], rep_d["06:00"][3]))
    P("      stop h %s, %s h run, %s Wh unserved: yes (so 'full service' below counts hours as the record's 'h run' does)" % (
        rep_d["18:00"][1], rep_d["18:00"][2], rep_d["18:00"][3]))
    P("")

    # ------------------------------------------------------------------------------------------ 1. the assumption set
    u3we = CASES["WE"][2]["eta_u3"]
    u3dw = CASES["DRAWN-WE"][2]["eta_u3"]
    P("1. THE ONE ASSUMPTION SET (both architectures; only the stage window differs from runtime.out section 2)")
    P("   load       PS-IDLE-SPEC %.1f W at the pack terminals over its 39 loads (REQ-072's objective_profile); HF available, not" % load0)
    P("              receiving; the tablet not charged, the USB-C outlet off; A2 adds the lid path's standby drain %.3f W (WE)" % drain_w)
    P("   store      full at the start, aged to %.0f %% (REQ-014), each pack to its 3.00 V line with the %.0f %% reserve; the base at" % (
        100 * pk.age80, 100 * pk.rsoc))
    P("              +%.0f C, A2's lid at %.2f C (SC-37's air minimum); battery-only both at +20 C, then both at %.0f C" % (
        TP.v("t_base_c"), EBS.TMIN, T_COLD))
    P("   sun        SC-37's mean September day at Leiden, one plane 40/0, repeated; TYP the case, WAB a sensitivity (build ratio")
    P("              %.4f / %.4f on PVGIS's %.4f); starts 06 and 18 UTC; the availability series is the checked 400 Wp 2S2P trace" % (
        rat40["TYP"], rat40["WAB"], pr0))
    P("   window     the stage's input clipped at REQ-016's %.0f W (energy_inputs.yaml: '%s')" % (
        win_req016, D0["solar"]["window"]["stage_max_w_in"]["src"][:60]))
    P("   CORRECTED  HYPOTHETICAL, ENERGY-BASIS 6c's WE: bus %.3f V, U3's limit 6.1 A, U3 %.4f, U3B %.3f, stage %.2f, front end" % (
        v_min, u3we, TP.v("eta_u3b_lo"), ch[0]["eta"]))
    P("              %.2f, charge %.2f (CONDITIONAL), lid loops %.3f / %.3f Ohm, V(AK) %.0f mV; U3's cap %.1f W" % (
        ch[1]["eta"], ce["value"], rd[1], rc_[1], 1000 * vak[2], 6.1 * v_min))
    P("   AS DRAWN   board A as generated: R11 10 mOhm (front end's stacked minimum %.3f A less %.3f A of other loads = %.3f A)," % (
        held[0], other, fe_held))
    P("              U3 at its INFERRED minimum %.2f A (set 4.15 A), U3 %.4f; the other WE inputs as above (three_cases.py's" % (
        u3_e1 - U3_TOL, u3dw))
    P("              DRAWN at WE); cap %.1f W. UPPER BOUND: min(available, cap) kept, which A-2 says the drawn path does not" % (
        min(u3_e1 - U3_TOL, fe_held) * v_min))
    P("              guarantee. LOWER BOUND: A-2's inferred collapse, an hour whose power at VBUS20 is under the cap delivers nothing")
    P("   A1         one pack at +20 C, charged at %.2f A a cell (energy_inputs.yaml's D-06 figure, 3.06 A for 4S3P), no lid path" % chg_a1_cell)
    P("   A2         base 4S6P at +20 C (U3, %.3f A) and lid 4S9P at %.2f C (U3B, %.3f A, IIN %.1f A; the join of TOPOLOGY.md)" % (
        TP.v("chg_a_base"), EBS.TMIN, TP.v("chg_a_lid"), TP.v("iin_lid_a")))
    P("   pass line  COMB (the kit never stops and the lowest combined store stays above the %.1f Wh floor), as runtime.py" % FLOOR)
    P("")

    # ------------------------------------------------------------------------------------------ 2. battery only
    P("2. BATTERY-ONLY ENDURANCE (runtime.out section 1, reproduced in 0b; no solar)")
    P("   A1 D-06's 4S3P: usable %.1f Wh at +20 C, %.1f Wh at %.0f C: %.2f h and %.2f h" % (a1_bo[0], a1_bo[1], T_COLD, a1_bo[2], a1_bo[3]))
    P("   A2 base 4S6P + lid 4S9P: usable %.1f Wh at +20 C, %.1f Wh at %.0f C: %.2f h and %.2f h" % (a2_bo[0], a2_bo[1], T_COLD, a2_bo[2], a2_bo[3]))
    P("   against 48 h: A1 short by %.1f h (%.0f Wh at +20 C), A2 short by %.1f h (%.0f Wh at +20 C); against 72 h: A1 %.1f h (%.0f Wh)," % (
        48 - a1_bo[2], 48 * load0 - a1_bo[0], 48 - a2_bo[2], 48 * ld2 - a2_bo[0], 72 - a1_bo[2], 72 * load0 - a1_bo[0]))
    P("   A2 %.1f h (%.0f Wh). Battery-only closes neither end at any temperature; the objective is a solar-assisted one." % (
        72 - a2_bo[2], 72 * ld2 - a2_bo[0]))
    P("")

    # ------------------------------------------------------------------------------------------ 3. solar-assisted, 100 W
    P("3. SOLAR-ASSISTED, THE STAGE INPUT CLIPPED AT %.0f W: A CONDITIONAL SCREENING STIMULUS (section 7: the series is the 400 Wp" % win_req016)
    P("   2S2P trace, which REQ-016 does not admit). First interruption per start (hour from the start, and its UTC hour), unserved")
    P("   Wh at 48 h and at 72 h per start, and the hours of full service in each horizon")
    paths = (("CORRECTED, HYPOTHETICAL, WE", "WE", False), ("AS DRAWN, WE, upper bound", "DRAWN-WE", False),
             ("AS DRAWN, WE, lower bound (A-2 collapse)", "DRAWN-WE", True))
    archs = (("A1", "A1 D-06's 4S3P", BASE_A1), ("A2", "A2 base 4S6P + lid 4S9P", LID_A))
    main = {}
    for ak, alab, n in archs:
        for plab, key, col in paths:
            for b in ("TYP", "WAB"):
                s48 = meanday(ak, key, n, b, 48, win_req016, collapse=col, account=True)
                s72 = meanday(ak, key, n, b, 72, win_req016, collapse=col, account=True)
                main[(ak, key, col, b)] = (s48, s72)
            s48, s72 = main[(ak, key, col, "TYP")]
            w48, w72 = main[(ak, key, col, "WAB")]
            P("   %-26s %s" % (alab, plab))
            for i, st in enumerate((6, 18)):
                fs = s72["stops"][i]
                P("     TYP from %02d UTC: first interruption %s; unserved %6.1f Wh at 48 h, %6.1f Wh at 72 h; full service %2d of 48 h, %2d of 72 h" % (
                    st, "none" if fs is None else "h %2d (%02d UTC)" % (fs, (st + fs) % 24), s48["shorts"][i], s72["shorts"][i],
                    s48["rs"][i]["acct"]["full_h"], s72["rs"][i]["acct"]["full_h"]))
            P("     WAB (sensitivity): first interruption h %s; unserved at 48 h %s Wh, at 72 h %s Wh (06 / 18 UTC)" % (
                "/".join("-" if x is None else str(x) for x in w72["stops"]), " / ".join("%.1f" % x for x in w48["shorts"]),
                " / ".join("%.1f" % x for x in w72["shorts"])))
    P("   The same cases in runtime.out's window (200 W, P-03), for the difference the window alone makes (TYP, 06 / 18 UTC):")
    p03 = {}
    for ak, alab, n in archs:
        for plab, key, col in paths[:2]:
            a48 = meanday(ak, key, n, "TYP", 48, WIN_P03, collapse=col)
            a72 = meanday(ak, key, n, "TYP", 72, WIN_P03, collapse=col)
            p03[(ak, key)] = (a48, a72)
            P("     %-26s %-28s first interruption h %s; unserved %s Wh at 48 h, %s Wh at 72 h" % (
                alab, plab.split(",")[0] + ("" if key == "WE" else " (UB)"), "/".join("-" if x is None else str(x) for x in a72["stops"]),
                " / ".join("%.1f" % x for x in a48["shorts"]), " / ".join("%.1f" % x for x in a72["shorts"])))
    P("")

    # ------------------------------------------------------------------------------------------ 4. least additional storage
    P("4. THE LEAST ADDITIONAL USABLE STORAGE (COMB line, both starts, the %.0f W window; continuous parallel count; A1 grows its" % win_req016)
    P("   one pack at +20 C, A2 grows its lid at %.2f C with the base held at 4S6P, as runtime.py section 3; usable Wh aged)" % EBS.TMIN)
    lst = {}
    for ak, alab, n in archs:
        for plab, key, col in paths:
            for hours in (48, 72):
                for b in ("TYP", "WAB"):
                    if b == "WAB" and key != "WE":
                        continue
                    x = least(ak, key, b, hours, win_req016, 1.0, 160.0, 34, collapse=col)
                    s0 = meanday(ak, key, n, b, hours, win_req016, collapse=col)
                    if x is None:
                        lst[(ak, key, col, hours, b)] = None
                        P("     %-4s %-40s %d h %s: none up to %d in parallel" % (ak, plab, hours, b, 160))
                        continue
                    sx = meanday(ak, key, x, b, hours, win_req016, collapse=col)
                    k = "el" if ak == "A2" else "eb"
                    add = sx[k] - s0[k]
                    lst[(ak, key, col, hours, b)] = (x, add, sx["eb"] + sx["el"])
                    P("     %-4s %-40s %d h %s: %s 4S%.2fP; %+7.1f Wh usable (%+5.1f 35E cells) over %s, store %.1f Wh in all" % (
                        ak, plab, hours, b, "lid" if ak == "A2" else "pack", x, add, 4 * (x - n), "4S9P lid" if ak == "A2" else "4S3P",
                        sx["eb"] + sx["el"]))
    P("   What the records say fits (not changed here): A1's east pocket holds the ruled 4S3P block alone (packfit_west.out);")
    P("   A2 is the largest in-case store found with both lid functions kept: base 4S6P (M4a, M5, M6w OPEN) and 39 lid places")
    P("   (36 used; a1mech 1 and 2; the check's bound with P2 costing nothing, 43 places); no 21700 lid beats it (SHORTLIST.md 3)")
    P("")

    # ------------------------------------------------------------------------------------------ 5. energy accounts
    P("5. THE ENERGY ACCOUNT, TYP, 72 h, the %.0f W window (Wh over the run; per start; kit and per pack)" % win_req016)
    P("   array = the 400 Wp trace at the array; clip = above the window; stage in = into the stage; bus = at VBUS20 before the")
    P("   entry's cap (stage and front end losses taken); not taken = refused by the entry's cap or its collapse; U3 = U3's loss;")
    P("   node = at the system node; to load = the node's sun used by the load in the hour; accepted = taken into charge at the")
    P("   node; spill = offered to charge but refused (packs full or tapering, or the charge ceiling); stored = into the cells;")
    P("   chg loss = accepted less stored (U3B, the lid loop, the 0.95 charge efficiency); drawn = out of the cells; lid path =")
    P("   the lid's discharge path loss; cut = the first hour each pack stands at its line (the kit's stop puts both there);")
    P("   closure = start + stored - drawn - end")
    for ak, alab, n in archs:
        for plab, key, col in paths:
            s72 = main[(ak, key, col, "TYP")][1]
            for i, st in enumerate((6, 18)):
                a = s72["rs"][i]["acct"]
                P("   %s %s, from %02d UTC" % (ak, plab, st))
                P("     array %.1f, clip %.1f, stage in %.1f, bus %.1f, not taken %.1f, U3 %.1f, node %.1f (hours the cap binds: %d)" % (
                    a["arr"], a["clip"], a["stage_in"], a["bus_avail"], a["not_taken"], a["u3_loss"], a["node"], a["cap_hours"]))
                P("     to load %.1f, accepted %.1f, spill %.1f, stored %.1f, chg loss %.1f; drawn %.1f, lid path %.1f; start %.1f, end %.1f" % (
                    a["sun_load"], a["accepted"], a["spill"], a["stored"], a["chg_loss"], a["drawn"], a["dsg_path"], a["start"], a["end"]))
                P("     asked %.1f, served %.1f, unserved %.1f; cut base h %s, lid h %s, kit stop h %s; closure %.2e" % (
                    a["asked"], a["served"], a["unserved"], "-" if a["cut_b"] is None else a["cut_b"],
                    ("-" if a["cut_l"] is None else a["cut_l"]) if ak == "A2" else "(no lid)",
                    "-" if s72["rs"][i]["first_stop"] is None else s72["rs"][i]["first_stop"], a["closure"]))
                if abs(a["closure"]) > 1e-6 or a["node_dev"] > 1e-9:
                    refuse(4, "the energy account does not close (%s %s %d)" % (ak, key, st))
    P("   (every account closes to under 1e-6 Wh and its node power equals the model's in every hour)")
    P("")

    # ------------------------------------------------------------------------------------------ 6. thresholds
    P("6. WHERE A RESULT COULD TURN ON AN UNDOCUMENTED FIGURE (TYP, 100 W; the corrected path unless named)")
    for ak, alab, n in archs:
        for key, lab in (("WE90", "the three at their 0.90 bracket"), ("WE97", "stage and front end 0.97, charge 0.98 (the high bracket)"),
                         ("WE100", "all three at 1.00 (no conversion or charge loss at all: a physical bound)")):
            s48 = meanday(ak, key, n, "TYP", 48, win_req016)
            s72 = meanday(ak, key, n, "TYP", 72, win_req016)
            k = "el" if ak == "A2" else "eb"
            adds = []
            for hours in (48, 72):
                x = least(ak, key, "TYP", hours, win_req016, 1.0, 160.0, 34)
                adds.append("none up to 160 in parallel" if x is None else "%+.1f" % (
                    meanday(ak, key, x, "TYP", hours, win_req016)[k] - meanday(ak, key, n, "TYP", hours, win_req016)[k]))
            P("   %s, %s: 48 h %s; 72 h %s; least addition %s / %s Wh" % (
                ak, lab, "MET" if s48["ok"] else "NOT MET (%.1f)" % s48["short"], "MET" if s72["ok"] else "NOT MET (%.1f)" % s72["short"],
                adds[0], adds[1]))
    # U3's efficiency re-weighted over the 100 W day by the same method (s117's efficiency.py, TI's equations)
    e_st0, e_fe0, _ = TP.chain(D0)

    def u3_day_w(vin, ilim, reading, window):
        cap = min(0.043 / (TP.v("fe_r11_draft_mohm") / 1000.0) * vin, ilim * vin)
        pin = pout = 0.0
        for g in prof0:
            p = min(min(BUD.panel_w(g, WP_TRACE, pr0), window) * e_st0 * e_fe0, cap)
            if p < 1.0:
                continue
            e = EF.eta("buck", vin, p / vin, 14.5, min(3.968, p * 0.95 / 14.5), EF.CHOSEN_U3, EF.U3["ind"], EF.U3["f"],
                       EF.U3["r_in"], EF.U3["r_chg"], reading)
            pin += p
            pout += p * e
        return pout / pin
    if abs(u3_day_w(v_min, 6.1, "lower", WIN_P03) - u3we) > 1e-12:
        refuse(4, "u3_day_w does not reproduce energy_basis.u3_day at 200 W")
    u3w100 = u3_day_w(v_min, 6.1, "lower", win_req016)
    for ak, alab, n in archs:
        s72 = meanday(ak, "WE", n, "TYP", 72, win_req016, ov_extra={"eta_u3": u3w100})
        s48 = meanday(ak, "WE", n, "TYP", 48, win_req016, ov_extra={"eta_u3": u3w100})
        base72 = main[(ak, "WE", False, "TYP")]
        P("   %s, U3 re-weighted over the 100 W day (%.4f against WE's %.4f, TI's method at the makers' maxima): unserved %s at 48 h" % (
            ak, u3w100, u3we, " / ".join("%.1f" % x for x in s48["shorts"])))
        P("      and %s at 72 h (was %s and %s)" % (" / ".join("%.1f" % x for x in s72["shorts"]),
                                                 " / ".join("%.1f" % x for x in base72[0]["shorts"]), " / ".join("%.1f" % x for x in base72[1]["shorts"])))
    # A1's charge setting
    s_a = meanday("A1", "WE", BASE_A1, "TYP", 72, win_req016)
    s_b = meanday("A1", "WE", BASE_A1, "TYP", 72, win_req016, chg_cell=TP.v("chg_a_base") / BASE_A1)
    P("   A1 charged at %.3f A (code 31, %.2f A a cell, the generator's 4 A class) instead of 3.06 A: unserved at 72 h %s Wh" % (
        TP.v("chg_a_base"), TP.v("chg_a_base") / BASE_A1, " / ".join("%.1f" % x for x in s_b["shorts"])))
    P("      against %s (06 / 18 UTC)" % " / ".join("%.1f" % x for x in s_a["shorts"]))
    # the steady load each store carries (the discriminating measurement: the loads with no document)
    P("   The steady load at the pack terminals each store carries through the horizon (COMB, TYP, the profile's load replaced):")
    for ak, alab, n in archs:
        for plab, key, col in paths[:2]:
            vals = []
            for hours in (48, 72):
                lo, hi = 1.0, load0
                okf = lambda L: (lambda s: s["ok"] and s["both"] > FLOOR)(meanday(ak, key, n, "TYP", hours, win_req016, collapse=col, load_w=L))
                if okf(hi):
                    vals.append(">= %.1f" % hi)
                    continue
                for _ in range(30):
                    mid = 0.5 * (lo + hi)
                    if okf(mid):
                        lo = mid
                    else:
                        hi = mid
                vals.append("%.1f" % lo)
            P("     %s %-40s 48 h %s W, 72 h %s W (PS-IDLE-SPEC: PLAN %.1f, LOW 33.1, HIGH 82.8 W)" % (ak, plab, vals[0], vals[1], load0))
    P("")

    # ------------------------------------------------------------------------------------------ 7. what the stimulus represents
    P("7. WHAT THE 100 W RESULT REPRESENTS: the series is the 400 Wp 2S2P trace (a1solar's build, fixed point %.2f V, ratio %.4f TYP)" % (
        R40.win[1], rat40["TYP"]))
    e_st, e_fe = ch[0]["eta"], ch[1]["eta"]
    p_arr = [BUD.panel_w(g, WP_TRACE, pr0 * rat40["TYP"]) for g in prof0]
    arr, c200, c100 = sum(p_arr), sum(min(x, WIN_P03) for x in p_arr), sum(min(x, win_req016) for x in p_arr)
    hclip, pk_ = sum(1 for x in p_arr if x > win_req016), max(p_arr)
    P("   the stimulus: %.1f Wh a day at the array (peak %.1f W); %.1f Wh into the stage at 200 W; %.1f Wh at 100 W, clipped in %d hours" % (
        arr, pk_, c200, c100, hclip))
    node100 = c100 * e_st * e_fe * u3we
    ceil100 = sum(min(BUD.panel_w(g, 20000.0, pr0 * rat40["TYP"]), win_req016) for g in prof0) * e_st * e_fe * u3we
    demand = load0 * 24
    P("   at the node on WE: %.1f Wh a day through the 100 W window; the window's ceiling with a 20 kWp array (energy_budget.out 4's" % node100)
    P("   method, on WE's chain) %.1f. PS-IDLE-SPEC asks %.1f Wh a day at the pack terminals (%.1f with A2's drain): under WE no" % (
        ceil100, demand, demand + 24 * drain_w))
    P("   array carries the day's demand through this window, so each day ends shorter than it began and the store must hold the")
    P("   first night plus each later day's deficit (at the node, before charge losses, %.1f Wh a day with the stimulus)" % (demand - node100))
    need_wp = [(h, 100.0 / (prof0[h] / 1000.0 * pr0 * rat40["TYP"])) for h in range(24) if prof0[h] > 0.0]
    P("   the array needed to reach 100 W in an hour at the trace's ratio: %s" % ", ".join("%02d UTC %.0f Wp" % x for x in need_wp if x[1] < 2000.0))
    P("   REQ-016 admits a panel of at most 25 V open circuit at its coldest, held at 17.6 V, at most 100 W into the stage")
    P("   (acceptance: a bench supply on a 100 W panel's curve, MPP 17.6 V, Voc 25 V). The trace is 2S2P at %.2f V: 51.28 V cold" % R40.win[1])
    P("   (a1solar ARRAY.md 1), outside it. The held panel is outside it even alone (25.64 V at -20 C cells); a1solar ARRAY.md 5")
    P("   reads the SunPower (24.05 V) and PowerFilm's 15 V model (24.86 V) as admitted at -20 C, none at -40 C; neither has an")
    P("   availability trace in the tree. The records read an array above about 150 Wp of the 12 V class as re-rating the")
    P("   entry's 10 A (energy_budget.out 4), which REQ-016's acceptance names. So the 100 W result is a CONDITIONAL SCREENING")
    P("   STIMULUS: it stands for a compliant source only if one delivers, in every hour, at least min(the 400 Wp trace, 100 W).")
    P("   Sensitivity on the held panel's fit held at 17.6 V (a1solar's ratio method, INFERRED; the panel itself is not compliant):")
    for npar in (1, 2, 4):
        rr = R40.typical(v=17.6, ns=1, np_=npar)
        wp_ = 100.0 * npar
        for ak, alab, n in archs:
            s48 = meanday(ak, "WE", n, "TYP", 48, win_req016, wp=wp_, ratio=rr)
            s72 = meanday(ak, "WE", n, "TYP", 72, win_req016, wp=wp_, ratio=rr)
            p_arr = [BUD.panel_w(g, wp_, pr0 * rr) for g in prof0]
            P("     1S%dP %3.0f Wp, ratio %.4f, %.1f Wh a day into the stage: %s first interruption h %s; unserved %s at 48 h, %s at 72 h" % (
                npar, wp_, rr, sum(min(x, win_req016) for x in p_arr), ak, "/".join("-" if x is None else str(x) for x in s72["stops"]),
                " / ".join("%.1f" % x for x in s48["shorts"]), " / ".join("%.1f" % x for x in s72["shorts"])))
    P("   (1S4P of the held panel: 25.64 V at -20 C cells and a 40 A entry by a1solar ARRAY.md 5; shown for the energy only)")
    P("")

    # ------------------------------------------------------------------------------------------ 8. the charge path REQ-016 needs
    P("8. THE CHARGE PATH REQ-016'S WINDOW NEEDS (TYP, 100 W, the lowest bus %.3f V)" % v_min)
    for lab, es, efe in (("declared 0.93 x 0.93", ch[0]["eta"], ch[1]["eta"]), ("high bracket 0.97 x 0.97", ch[0]["high"], ch[1]["high"]),
                         ("no loss, 1.00 x 1.00", 1.0, 1.0)):
        p_bus = max(min(BUD.panel_w(g, WP_TRACE, pr0 * rat40["TYP"]), win_req016) for g in prof0) * es * efe
        setting = 0.05 * math.ceil((p_bus / v_min + U3_TOL) / 0.05 - 1e-9)
        P("   %-26s the largest power at VBUS20 %.1f W: U3's input minimum at least %.3f A; the 50 mA setting at least %.2f A," % (
            lab, p_bus, p_bus / v_min, setting))
        P("   %-26s its maximum %.2f A, so through R11 %.3f A (0.060 A of other loads) to %.3f A (C-9's 0.079 A)" % (
            "", setting + U3_TOL, setting + U3_TOL + 0.060, setting + U3_TOL + 0.079))
    P("   the held front end (R11 10 mOhm) gives %.3f A to U3 at its stacked minimum; the drafted 6.2 mOhm gives 6.733 A; the" % fe_held)
    P("   corrected path's 6.1 A cap (%.1f W) never binds at 100 W: %s" % (6.1 * v_min, "yes" if all(
        main[(ak, "WE", False, b)][h]["rs"][i]["acct"]["cap_hours"] == 0 for ak, _l, _n in archs for b in ("TYP", "WAB") for h in (0, 1) for i in (0, 1)) else "NO"))
    P("")
    # ------------------------------------------------------------------------------------------ 9. the layer 3 headline cases
    P("9. THE LAYER 3 HEADLINE CASES AT REQ-016'S WINDOW: runtime.out section 2's rows (A2, 4S9P lid, TYP), only the window moved")
    for key, lab in (("DRAWN", "DRAWN, NOM inputs (runtime.out's AS DRAWN, an upper bound)"), ("NOM", "NOM, CORRECTED PATH, HYPOTHETICAL"),
                     ("WE", "WE, CORRECTED PATH, HYPOTHETICAL, CONDITIONAL")):
        r200 = [meanday("A2", key, LID_A, "TYP", h, WIN_P03) for h in (48, 72)]
        r100 = [meanday("A2", key, LID_A, "TYP", h, win_req016) for h in (48, 72)]
        P("   %-58s 200 W: stops h %s, %.1f / %.1f Wh unserved at 48 / 72 h" % (
            lab, "/".join("-" if x is None else str(x) for x in r200[1]["stops"]), r200[0]["short"], r200[1]["short"]))
        P("   %-58s 100 W: stops h %s, %.1f / %.1f Wh unserved at 48 / 72 h" % (
            "", "/".join("-" if x is None else str(x) for x in r100[1]["stops"]), r100[0]["short"], r100[1]["short"]))
    P("   (each figure the larger of the two starts, as runtime.out prints it)")
    P("")

    # ------------------------------------------------------------------------------------------ 10. the levers together
    P("10. THE IN-CONSTRAINT LEVERS TOGETHER, A2, CORRECTED, TYP, 100 W: each at its favourable end, none established")
    levers = (("WE as above (4S9P lid at %.2f C)" % EBS.TMIN, "WE", LID_A, None),
              ("+ the lid at the base's +20 C (a bound: no heating energy counted)", "WE", LID_A, 20.0),
              ("+ 4S10P in the lid (the check's 43-place bound, a1mech README 1)", "WE", 10, 20.0),
              ("+ stage and front end 0.97, charge 0.98 (the high bracket)", "WE97", 10, 20.0))
    for lab, key, n, tl in levers:
        r_ = [meanday("A2", key, n, "TYP", h, win_req016, t_l=tl) for h in (48, 72)]
        x = [least("A2", key, "TYP", h, win_req016, 1.0, 160.0, 34, t_l=tl) for h in (48, 72)]
        add = ["%+.1f" % (meanday("A2", key, x[i], "TYP", h, win_req016, t_l=tl)["el"] - r_[i]["el"]) if x[i] is not None else "none"
               for i, h in enumerate((48, 72))]
        loads = []
        for h in (48, 72):
            lo, hi = 1.0, load0
            okf = lambda L, h=h: (lambda s_: s_["ok"] and s_["both"] > FLOOR)(meanday("A2", key, n, "TYP", h, win_req016, t_l=tl, load_w=L))
            if okf(hi):
                loads.append(">= %.1f" % hi)
                continue
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                if okf(mid):
                    lo = mid
                else:
                    hi = mid
            loads.append("%.1f" % lo)
        P("   %-66s store %.1f Wh; unserved %.1f / %.1f Wh at 48 / 72 h;" % (lab, r_[0]["eb"] + r_[0]["el"], r_[0]["short"], r_[1]["short"]))
        P("   %-66s least addition %s / %s Wh; steady load carried %s / %s W" % ("", add[0], add[1], loads[0], loads[1]))
    P("")
    P("END. Each line is the model's arithmetic; nothing is measured. No result here is demonstrated capability: the circuit as")
    P("drawn fails; the corrected path is HYPOTHETICAL and CONDITIONAL on three undocumented efficiencies; the 100 W results rest")
    P("on a series REQ-016 does not admit and are a screening stimulus only.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
