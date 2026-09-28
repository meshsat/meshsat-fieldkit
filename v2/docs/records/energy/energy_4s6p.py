#!/usr/bin/env python3
"""energy_4s6p.py: the second 4S3P block in the west pocket wired IN PARALLEL with the first, under the ONE existing
board P in the east pocket: one 4S6P pack (stream energy, MESHSAT-1357, section 8 of ENERGY-RECONCILIATION.md).

PROTOTYPE DESIGN: nothing in this kit has been built, powered or measured. Every figure printed is arithmetic on
makers' figures, generator declarations and stated assumptions (an AI review, not a qualified one).

What it prints (the items of section 8):
  1  electrical: the gauge's capacity words, balancing, the currents per cell at 6P and with one block isolated,
     the charge current the gauge's OCC allows, the charge time, the two strings' current sharing, F1 against the
     cells' limit (S-85 item 3)
  2  mechanical: the pockets and the corridor between them, the harness length bound, its resistance, drop, loss
     and adiabatic rise at 18 A for 60 s, the overlap with the west jumpers' drop zone
  3  energy: the usable energy of 4S6P new and aged, and the hour-by-hour runs of energy_budget.py (imported
     unchanged) for M1 as written, the night state as in sets 1 to 3, and a day and night schedule, with ONE
     charger current (one board P, one gauge OCC) instead of the record's doubled 6.12 A
  4  consequences: mass, the key-down rise per minute, the heater branch with two mats, cost ESTIMATE lines

Inputs: pinned by sha256 below (and energy_inputs.yaml's own pinned list, checked as energy_budget.py checks it);
refuses to run, naming the file, if any changed. Deterministic: no date, host or absolute path in the output.
Usage: energy_4s6p.py [--root <repository root>]   (python3 with PyYAML; a few seconds)
"""
import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
PINS = {
    "v2/docs/records/energy/energy_budget.py": "36cede1b5fd59cf8728179b32ffa763a2e5b09457748d243d1ecfc84bc2c1fff",
    "v2/docs/records/energy/energy_inputs.yaml": "64dd014bee56d855023d43caeaf848cfd6dc54f65b58e341d6696851460f7470",
    "v2/ecad/tools/gen_sch_p.py": "740817ada5c8e14af8c8e001b775e09cbae94d6a03ad462ee2e1c1755bc935a3",
    "v2/ecad/tools/pcb_pack_protection.yaml": "ab1dbc3f3f69aa4687a4fa9745c0cbdc96d0521146dc5d3f84698656e33c484b",
    "v2/ecad/tools/gen_sch_a.py": "9684e7a9606aede6fdd41972f12530365f9b883e94e0174b2fddb621199c4e55",
    "v2/ecad/tools/panel1450.py": "3bdb88df9826024484326e8e7d67c74789ae20f610ce3e4ed69988bfc9f0340f",
    "v2/docs/records/adj/A06-pack-geometry/drafts/pack_fit.py": "a2a050dc24c461f207bb0485ef98851f238641f449f30151605042970bccf02c",
}

# Typed figures, each with the document it comes from (read by an AI; none measured):
TYPED = {
    "design_cap_max": (32767, "SLUUAQ3A 14.13.5.1 and 14.13.5.2: Design Capacity mAh and cWh, I2, maximum 32767"),
    "r_cb_ohm": (200.0, "SLUSC67B 6.10: RCB, internal cell balance resistance, RDS(ON) of the internal FET switch at 2 V < VDS < 4 V, 200 ohm"),
    "r_tap_ohm": (100.0, "gen_sch_p.py, the cell sense filters R1 to R4: 100R each"),
    "r_cell_ohm": ((0.035, 0.06), "POWER-THERMAL.md section 7.2: R_cell 0.035 to 0.06 Ohm (the cell sheet's 35 mOhm AC, Ver. 1.1 7.4, is the low end)"),
    "cp_j_gk": ((0.8, 1.1), "POWER-THERMAL.md section 7.2: 0.8 to 1.1 J/gK, INFERRED, no Samsung figure"),
    "rho_cu": (1.724e-8, "annealed copper at 20 C, IACS (a physical constant; no wire standard such as IEC 60228 is held in the tree)"),
    "awg12_mm2": (3.31, "12 AWG = 3.31 mm2 (the gauge's definition); board P's W_P, W_N, W_BP, W_BN are 12 AWG lands (gen_sch_p.py), the pack lead 12 AWG silicone (ASSEMBLY.md section 3)"),
    "cu_density_g_cm3": (8.96, "copper, a physical constant"),
    "cu_cp_j_gk": (0.385, "copper, a physical constant"),
    "flat_floor_y": (114.49, "CASE-MARGINS.md 2.1 and 2.3: the flat floor ends at Y +-114.49 (fillet tangent)"),
    "drop_zone": ((-165.0, 98.0), "CASE-MARGINS.md 3.4 (West): the drop zone, X -165 to the west wall at |Y| up to 98 from the floor to Z 54, is the west jumpers'"),
    "key_peak_a": (18.0, "PWR-F12: 18 A for 60 s for every PA key-down (pcb_pack_protection.yaml declared_peak_a)"),
    "heater_w": (7.5, "RS PRO 245-556: 7.5 W at 12 V, 50 x 150 mm (v2/vendor/battery/heater/rs-pro-245-556-heater-mat-sheet.pdf)"),
    "tps2596_rilm": ((903.0, 0.0112), "gen_sch_a.py at efuse(): TPS2596 equation 7, RILM = 903 / (ILIM + 0.0112) ohm"),
}


class InputError(Exception):
    pass


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_pins(root):
    bad = []
    for rel, want in sorted(PINS.items()):
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            bad.append("%s (missing)" % rel)
        elif sha256_of(full) != want:
            bad.append("%s (changed: %s)" % (rel, sha256_of(full)[:16]))
    if bad:
        raise InputError("pinned input(s) missing or changed, refusing to run: " + "; ".join(bad))
    d = yaml.safe_load(open(os.path.join(root, "v2/docs/records/energy/energy_inputs.yaml"), encoding="utf-8"))
    for p in d["pinned"]:
        full = os.path.join(root, p["path"])
        if not os.path.exists(full):
            bad.append("%s (missing)" % p["path"])
        elif sha256_of(full) != p["sha256"]:
            bad.append("%s (changed: %s)" % (p["path"], sha256_of(full)[:16]))
    if bad:
        raise InputError("energy_inputs.yaml's pinned input(s) missing or changed, refusing to run: " + "; ".join(bad))
    return d


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m


def literal_assigns(path, names):
    """Module-level NAME = <literal> assignments, read with ast (no grep)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in names:
                out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


def calls_with_first_arg(path, func_names, first):
    """Every call to one of func_names whose first positional argument is the string `first` (ast)."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if nm in func_names and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == first:
                hits.append(node)
    return hits


def kw(node, name):
    for k in node.keywords:
        if k.arg == name:
            return ast.literal_eval(k.value)
    return None


# ------------------------------------------------------------------------------------------ the hour-by-hour run
def sim_sched(eb, d, pack, prof, load_of_hh, wp, window, eta, pr, start_h, t_c, age, hours, dod, n_p, chg_total_a):
    """energy_budget.simulate's algorithm with a load that may change by hour of day (load_of_hh) and a TOTAL charge
    current (one charger, one gauge). The usable energy and the pack voltage are taken at the schedule's highest load
    (the conservative choice). A constant schedule reproduces energy_budget.simulate exactly (checked in main)."""
    p_ref = max(load_of_hh(hh) for hh in range(24))
    e_full, _ = pack.usable_wh(p_ref, t_c, age, dod, n_p)
    v_pack = pack.n_s * eb.interp(pack.vmean, pack.cell_current(p_ref, n_p))
    chg_max_w = chg_total_a * v_pack
    can_charge = d["pack"]["charge_window_c"]["low"] <= t_c <= d["pack"]["charge_window_c"]["high"]
    e = e_full
    lowest = e_full
    running = True
    first_stop = None
    short_wh = 0.0
    hours_run = 0
    asked = 0.0
    for h in range(hours):
        hh = (start_h + h) % 24
        p_load = load_of_hh(hh)
        asked += p_load
        p_sun = eb.node_w(prof[hh], wp, pr, window, eta)
        if not running and (p_sun >= p_load or e >= 0.5 * e_full):
            running = True
        load = p_load if running else 0.0
        if not running:
            short_wh += max(0.0, p_load - p_sun)
        if p_sun >= load:
            surplus = p_sun - load
            soc = e / e_full
            cap = chg_max_w if soc < pack.taper else chg_max_w * max(0.0, (1.0 - soc) / (1.0 - pack.taper))
            chg = min(surplus, cap) * pack.chg_eta if can_charge else 0.0
            e = min(e_full, e + chg)
        else:
            deficit = load - p_sun
            if e >= deficit:
                e -= deficit
            else:
                short_wh += deficit - e
                e = 0.0
                running = False
                if first_stop is None:
                    first_stop = h
        if running:
            hours_run += 1
        lowest = min(lowest, e)
    return {"e_full": e_full, "first_stop": first_stop, "short_wh": short_wh, "hours_run": hours_run, "ok": first_stop is None,
            "lowest": lowest, "asked": asked, "chg_max_w": chg_max_w}


def verdict(r):
    if r["ok"]:
        return "MET, lowest %.1f Wh" % r["lowest"]
    return "NOT MET, stop h %d, ran %d h, unserved %.0f of %.0f Wh" % (r["first_stop"], r["hours_run"], r["short_wh"], r["asked"])


# ------------------------------------------------------------------------------------------------------ main
def run(root):
    d = check_pins(root)
    eb = load_module("energy_budget", os.path.join(root, "v2/docs/records/energy/energy_budget.py"))
    pf = load_module("pack_fit", os.path.join(root, "v2/docs/records/adj/A06-pack-geometry/drafts/pack_fit.py"))
    prot = yaml.safe_load(open(os.path.join(root, "v2/ecad/tools/pcb_pack_protection.yaml"), encoding="utf-8"))
    pan = literal_assigns(os.path.join(root, "v2/ecad/tools/panel1450.py"), {"A_OUTLINE", "B_OUTLINE", "E_OUTLINE"})
    monthly = json.load(open(os.path.join(root, d["pinned"][0]["path"]), encoding="utf-8"))
    o = eb.Out()
    T = {k: v[0] for k, v in TYPED.items()}

    o("SECTION 8: ONE 4S6P PACK UNDER ONE BOARD P (the west block in parallel with the east block). PROTOTYPE DESIGN:")
    o("nothing built, ordered or measured; AI review. Inputs pinned (sha256, first 16):")
    for rel in sorted(PINS):
        o("  %s  %s" % (PINS[rel][:16], rel))
    o("  and energy_inputs.yaml's own pinned list (%d files), checked as energy_budget.py checks it." % len(d["pinned"]))
    o("Typed figures (not parsed; each with its source):")
    for k in sorted(TYPED):
        o("  %-18s %-22s %s" % (k, TYPED[k][0], TYPED[k][1]))
    o()

    # the loads and the profiles, from energy_budget.py's own sections (their printout discarded)
    pack = eb.Pack(d)
    with contextlib.redirect_stdout(io.StringIO()):
        res1 = eb.section1(eb.Out(), d)
        res4 = eb.section4(eb.Out(), d, monthly)
    pr, eta, hours = res4["pr"], res4["eta"], d["mission"]["hours"]
    ms = d["model_states"]
    p_idle, p_night = ms["PS-IDLE-SPEC"]["plan"], ms["PS-NIGHT-RELAY"]["plan"]

    # self-check: the scheduled run with a constant load and the record's charge rule equals energy_budget.simulate
    chk = []
    for (m, pl, wp, win, n_p) in ((9, p_idle, 100.0, 100.0, 3), (9, p_night, 200.0, 100.0, 6), (6, p_night, 100.0, 100.0, 6), (12, p_night, 330.0, 300.0, 6)):
        t_c = d["mission"]["cell_temp_c_by_month"][m]
        a = eb.simulate(d, pack, res4["months"][m]["profile"], pl, wp, win, eta, pr, 6, t_c, pack.age80, hours, dod="2v80", n_p=n_p)[1]
        b = sim_sched(eb, d, pack, res4["months"][m]["profile"], lambda hh, pl=pl: pl, wp, win, eta, pr, 6, t_c, pack.age80, hours, "2v80", n_p,
                      pack.chg_a * n_p / pack.n_p)
        same = all(abs(a[k] - b[k]) < 1e-9 if a[k] is not None and b[k] is not None else a[k] == b[k] for k in ("e_full", "first_stop", "short_wh", "hours_run", "lowest"))
        chk.append(same)
    if not all(chk):
        raise InputError("self-check failed: the scheduled run does not reproduce energy_budget.simulate")
    o("Self-check: the scheduled run reproduces energy_budget.simulate on 4 cases (constant load, the record's charge rule): %s" % ("PASS" if all(chk) else "FAIL"))
    o()

    # ================================================================================== 1. ELECTRICAL
    cell = prot["cell"]["limits"]
    i_chg_cell_max = cell["max_charge_current_ma"]["value"] / 1000.0
    i_dis_cell_max = cell["max_continuous_discharge_ma"]["value"] / 1000.0
    fn = {f["id"]: f for f in prot["functions"]}
    occ = fn["PACK_OVER_CURRENT_CHARGE"]["threshold"]["value"]
    ocd = fn["PACK_OVER_CURRENT_DISCHARGE"]["threshold"]["value"]
    pchg = fn["PRECHARGE_WINDOW"]["threshold"]["current_a"]
    f1_open = fn["FUSE_OVER_CURRENT_DISCHARGE"]["threshold"]["value"]
    c_min = d["pack"]["capacity_min_ah"]["value"]
    c_typ = d["pack"]["capacity_typ_ah"]["value"]
    o("1. ELECTRICAL")
    o()
    o("1a. The pack and the gauge's capacity words (BQ4050 data flash; SLUUAQ3A 14.13.5):")
    for n_p in (3, 6):
        dc_mah = n_p * c_min * 1000.0
        dc_cwh = 4 * n_p * c_min * 3.60 * 100.0
        o("   4S%dP: %d cells, nominal %.1f Wh (%d x %.2f Ah x 3.60 V); Design Capacity %.0f mAh (min) or %.0f (typ %.2f Ah), %.0f cWh; limit %d: %s" % (
            n_p, 4 * n_p, 4 * n_p * c_min * 3.60, 4 * n_p, c_min, dc_mah, n_p * c_typ * 1000.0, c_typ, dc_cwh, T["design_cap_max"],
            "fits" if max(dc_mah, dc_cwh) <= T["design_cap_max"] else "EXCEEDS"))
    o()
    i_bal = 3.9 / (T["r_cb_ohm"] + 2 * T["r_tap_ohm"])
    o("1b. Balancing: the internal bypass (RCB %.0f ohm) through two %.0f ohm tap filters at 3.9 V: %.2f mA (SLUSC67B 8.2.2.3.1: the series" % (
        T["r_cb_ohm"], T["r_tap_ohm"], i_bal * 1000))
    o("   resistors set the current). Time to move 1 percent of a series group's minimum capacity: 4S3P %.1f h, 4S6P %.1f h." % (
        0.01 * 3 * c_min / i_bal, 0.01 * 6 * c_min / i_bal))
    o("   It acts on a west group only through the equalising link of that node (the gauge's taps are on the east block).")
    o()
    o("1c. Currents per cell (the pack's current is the kit's load: parallel cells share it, the ratings do not rise):")
    rows = []
    for lab, i_pack in (("declared continuous", prot["pack"]["declared_continuous_a"]), ("declared peak (PWR-F12)", prot["pack"]["declared_peak_a"]),
                        ("gauge OCD1 trip", ocd), ("F1 opens from (135 percent)", f1_open)):
        rows.append([lab, "%.2f" % i_pack, "%.2f" % (i_pack / 3), "%.2f" % (i_pack / 6), "%.2f" % i_dis_cell_max])
    o.table(["discharge", "pack A", "A a cell, 4S3P or 6P with a block isolated", "A a cell, 4S6P even share", "cell limit A"], rows)
    o()
    rb = [4 * r / 3 for r in T["r_cell_ohm"]]
    L_lo, L_hi = 0.35, 0.55
    r_m = T["rho_cu"] / (T["awg12_mm2"] * 1e-6)
    r_h = [2 * L * r_m for L in (L_lo, L_hi)]
    shares = []
    for rblk in rb:
        for rh in r_h:
            shares.append((rblk + rh) / (2 * rblk + rh))
    s_hi = max(shares)
    o("1d. Sharing between the two strings: block resistance 4 x R_cell / 3 = %.1f to %.1f mOhm (cells only); the west string adds" % (rb[0] * 1e3, rb[1] * 1e3))
    o("   its harness, out and back, %.1f to %.1f mOhm (12 AWG, %.2f mOhm/m, route %.2f to %.2f m, item 2 below); the east string takes %.1f to %.1f" % (
        r_h[0] * 1e3, r_h[1] * 1e3, r_m * 1e3, L_lo, L_hi, 100 * min(shares), 100 * s_hi))
    o("   percent of the pack current (string fuses of equal rating in both strings cancel). East cell at the 18 A peak: %.2f A." % (
        T["key_peak_a"] * s_hi / 3))
    i_pack_at_limit = 3 * i_dis_cell_max / s_hi
    o()
    o("1e. S-85 item 3 (W4DP-F2): does an element acting without firmware open at or below the cells' continuous rating?")
    o("   healthy 4S6P: the east block's cells reach %.1f A each at a pack current of %.1f A; F1 opens from %.2f A (in 0.75 to 600 s)" % (
        i_dis_cell_max, i_pack_at_limit, f1_open))
    o("   and holds 27.5 A for 360,000 s at least: %s." % ("F1 opens BELOW the cells' limit" if f1_open < i_pack_at_limit else "the gap remains"))
    o("   one block isolated (its string fuse or its lead open, or a block not fitted): 4S3P again, cells' limit %.1f A against F1's %.2f:" % (
        3 * i_dis_cell_max, f1_open))
    o("   %s. The gauge's thresholds therefore stay at the 3P values (parallel_min 3)." % ("the gap of S-85 item 3 remains for that case" if f1_open > 3 * i_dis_cell_max else "closed"))
    o()
    o("1f. Charge current (one charger, BQ25731 on board A; one gauge OCC1 at %.1f A, set for 3P, pcb_pack_protection.yaml):" % occ)
    rows = []
    for lab, ic_ in (("FW-A02 as written (3P cycle life)", 3.0), ("this study's setting: OCC1 kept", 4.0), ("the record's two-pack runs", 2 * d["pack"]["charge"]["current_a"]["value"]),
                     ("6P cycle life (1.02 A a cell)", 6 * d["pack"]["charge_a_per_cell_cycle_life"]["value"])):
        per6, per3 = ic_ / 6, ic_ / 3
        rows.append([lab, "%.2f" % ic_, "%.2f" % per6, "%.2f" % per3, "yes" if ic_ < occ else "NO (OCC1 trips; raising it lets a 3P pack take %.2f A a cell)" % (ic_ / 3),
                     "yes" if per3 <= i_chg_cell_max else "NO"])
    o.table(["setting", "pack A", "A a cell at 6P", "A a cell with a block isolated", "below OCC1 %.1f A" % occ, "isolated block within 2.0 A a cell"], rows)
    o("   Pre-charge stays %.1f A: %.3fC of 4S6P (the guideline's window is 0.1C to 0.5C; lower is the gentle side), %.3fC of 3P." % (
        pchg, pchg / (6 * c_typ), pchg / (3 * c_typ)))
    o()
    o("1g. Charge time from the graceful line to 95 percent of the usable energy, the model's charge rule (CC to 85 percent, then")
    o("   linear taper, 0.95 into the cells), at constant pack voltage (INFERRED; the charger's own termination is the host's):")
    rows = []
    for ic_ in (3.0, 4.0, 6.12):
        for age_lab, age in (("new", 1.0), ("aged 80", pack.age80)):
            e_full = pack.usable_wh(p_idle, 20.0, age, "3v00", 6)[0]
            v = pack.n_s * eb.interp(pack.vmean, pack.cell_current(p_idle, 6))
            e, t = 0.0, 0.0
            dt = 1.0 / 60.0
            while e < 0.95 * e_full and t < 100:
                soc = e / e_full
                cap = ic_ * v if soc < pack.taper else ic_ * v * max(0.0, (1 - soc) / (1 - pack.taper))
                e += cap * pack.chg_eta * dt
                t += dt
            rows.append(["%.2f" % ic_, age_lab, "%.1f" % e_full, "%.1f" % (ic_ * v), "%.1f" % t])
    o.table(["charge A", "pack", "usable Wh", "CC power W", "hours to 95 percent"], rows)
    o()

    # ================================================================================== 2. MECHANICAL
    o("2. MECHANICAL (the pockets from A06's pack_fit.py, the outlines from panel1450.py)")
    ax0, ay0, ax1, ay1 = pan["A_OUTLINE"]
    bx0, by0, bx1, by1 = pan["B_OUTLINE"]
    ex0, ey0, ex1, ey1 = pan["E_OUTLINE"]
    o("   east pocket X %.0f..%.0f Y %.0f..%.0f; west pocket X %.0f..%.0f Y %.0f..%.0f; board B's underside Z %.2f (pack_fit.B_UNDER)" % (
        pf.EAST["x"][0], pf.EAST["x"][1], pf.EAST["y"][0], pf.EAST["y"][1], pf.WEST["x"][0], pf.WEST["x"][1], pf.WEST["y"][0], pf.WEST["y"][1], pf.B_UNDER))
    o("   board A X %.0f..%.0f Y %.0f..%.0f; board B X %.0f..%.0f Y %.0f..%.0f; board E (dock strip) X %.0f..%.0f Y %.0f..%.0f" % (
        ax0, ax1, ay0, ay1, bx0, bx1, by0, by1, ex0, ex1, ey0, ey1))
    gap_x = pf.EAST["x"][0] - pf.WEST["x"][1]
    corr_w = T["flat_floor_y"] - ay1
    o("   between the pockets: %.0f mm in X. Candidate corridor at the floor along the back wall: outboard of board A (Y %.0f) and" % (gap_x, ay1))
    o("   inboard of the flat floor's edge (Y %.2f), %.2f mm wide, under board B (Z %.2f less its underside parts); shared with the" % (
        T["flat_floor_y"], corr_w, pf.B_UNDER))
    o("   RJ45 patch lead and the connector plate's lead drops (CASE-MARGINS.md 3.3); the floor plan is not drawn (its section 6).")
    o("   Under board A the floor is the RF jumpers' lane to E6's clamps (CASE-MARGINS.md 3.4) and E6's strip is at Y %.0f..%.0f." % (ey0, ey1))
    blk_y = 133.50
    west_n = pf.WEST["y"][1] - (pf.WEST["y"][0] + blk_y)
    o("   Route length bound: %.0f (between the pockets) plus up to %.1f in the west pocket (the block's free Y) plus up to 205.5 along the" % (gap_x, west_n))
    o("   east group to board P, less what the placement saves: %.2f to %.2f m taken (ESTIMATE; no route is drawn)." % (L_lo, L_hi))
    dz_x, dz_y = T["drop_zone"]
    ov_x = min(pf.WEST["x"][1], dz_x) - pf.WEST["x"][0]
    o("   The west jumpers' drop zone (X %.0f to the wall, |Y| <= %.0f, floor to Z 54) overlaps the west pocket over %.0f mm of X: a block" % (dz_x, dz_y, ov_x))
    o("   of %.2f in a %.0f pocket cannot leave it (X spare 1.35), so the block takes the drop zone the seven west jumpers were given." % (
        56.65, pf.WEST["x"][1] - pf.WEST["x"][0]))
    o()
    rows = []
    for L in (L_lo, L_hi):
        r_loop = 2 * L * r_m
        for lab, i in (("east string open: the whole peak on the west", T["key_peak_a"]), ("even share, the peak", T["key_peak_a"] * (1 - min(shares))),
                       ("PS-IDLE-SPEC, west share", p_idle / 14.4 / 2)):
            rows.append(["%.2f" % L, lab, "%.2f" % i, "%.1f" % (r_loop * 1e3), "%.0f" % (i * r_loop * 1e3), "%.2f" % (i * i * r_loop)])
    o.table(["route m", "case", "A", "loop mOhm", "drop mV", "loss W"], rows)
    mass_g_m = T["awg12_mm2"] * T["cu_density_g_cm3"]
    rise = T["key_peak_a"] ** 2 * r_m / (mass_g_m * T["cu_cp_j_gk"]) * 60.0
    o("   12 AWG at %.0f A for 60 s, adiabatic (no loss to the air, copper only): %.1f K. The pack lead is already 12 AWG at this current." % (T["key_peak_a"], rise))
    o()

    # ================================================================================== 3. ENERGY
    o("3. ENERGY: 4S6P, the chain of energy_budget.py section 2 at n_p = 6 (one pack, 24 cells)")
    rows = []
    for st in ("PS-IDLE-SPEC", "PS-NIGHT-RELAY"):
        pl = ms[st]["plan"]
        for t in (20.0, 5.0, 0.0, -10.0):
            new = pack.usable_wh(pl, t, 1.0, "3v00", 6)[0]
            a80 = pack.usable_wh(pl, t, pack.age80, "3v00", 6)[0]
            a60 = pack.usable_wh(pl, t, pack.age60, "3v00", 6)[0]
            a80b = pack.usable_wh(pl, t, pack.age80, "2v80", 6)[0]
            one = pack.usable_wh(pl, t, pack.age80, "3v00", 3)[0]
            rows.append([st, "%.2f" % pl, "%+.0f" % t, "%.1f" % new, "%.1f" % a80, "%.1f" % a80b, "%.1f" % a60, "%.1f" % one, "%.2f" % (a80 / pl)])
    o.table(["state", "W", "cells C", "new Wh", "aged 80 Wh (3.00 V)", "aged 80 Wh (2.80 V)", "aged 60 Wh", "4S3P aged 80 Wh", "h aged 80"], rows)
    o()
    panels = ((100.0, 100.0, "100 Wp, 100 W window"), (200.0, 100.0, "200 Wp, 100 W (route B)"), (330.0, 300.0, "330 Wp, 300 W path"), (400.0, 1e9, "400 Wp, no window"))
    months = ((9, 20.0), (6, 20.0), (12, 5.0), (12, 20.0))

    def one_run(m, t_c, load_of_hh, wp, win, dod, ic_, start=6, age=None):
        return sim_sched(eb, d, pack, res4["months"][m]["profile"], load_of_hh, wp, win, eta, pr, start, t_c, pack.age80 if age is None else age, hours, dod, 6, ic_)

    o("3a. M1 AS WRITTEN: PS-IDLE-SPEC %.1f W for 72 h, from a full aged 4S6P pack, charge %.1f A (1f), 2.80 V line unless stated:" % (p_idle, 4.0))
    rows = []
    for m, t_c in months:
        for wp, win, lab in panels:
            r6 = one_run(m, t_c, lambda hh: p_idle, wp, win, "2v80", 4.0, 6)
            r18 = one_run(m, t_c, lambda hh: p_idle, wp, win, "2v80", 4.0, 18)
            rows.append([eb.MONTHS[m - 1], "%+.0f" % t_c, lab, verdict(r6), verdict(r18)])
    r_design = one_run(9, 20.0, lambda hh: p_idle, 100.0, 100.0, "3v00", 4.0, 6)
    rows.append(["September", "+20", "design case, 3.00 V line", verdict(r_design), ""])
    r_new = one_run(9, 20.0, lambda hh: p_idle, 400.0, 1e9, "2v80", 4.0, 6, age=1.0)
    rows.append(["September", "+20", "400 Wp, no window, NEW pack", verdict(r_new), ""])
    r_lo = one_run(6, 20.0, lambda hh: ms["PS-IDLE-SPEC"]["low"], 400.0, 1e9, "2v80", 4.0, 6)
    rows.append(["June", "+20", "400 Wp, no window, PS-IDLE-SPEC LOW %.1f W" % ms["PS-IDLE-SPEC"]["low"], verdict(r_lo), ""])
    o.table(["month", "cells C", "panel", "start 06:00", "start 18:00"], rows)
    n_diff, n_all = 0, 0
    for m, t_c in months:
        for wp, win, lab in panels:
            for st_h in (6, 18):
                rs = [one_run(m, t_c, lambda hh: p_idle, wp, win, "2v80", ic_, st_h) for ic_ in (3.0, 4.0, 6.12)]
                n_all += 1
                if len(set((r["ok"], r["first_stop"], r["hours_run"]) for r in rs)) > 1:
                    n_diff += 1
    o("   The charge current (3.0, 4.0 or 6.12 A) changes the verdict, first stop or hours run in %d of these %d runs." % (n_diff, n_all))
    o()
    o("   The largest constant load the aged 4S6P pack carries for 72 h (2.80 V line, charge 4.0 A, start 06:00):")
    rows = []
    for m, t_c in months:
        cells = []
        for wp, win, lab in panels:
            lo, hi = 0.0, p_idle
            for _ in range(40):
                mid = 0.5 * (lo + hi)
                if one_run(m, t_c, lambda hh, mid=mid: mid, wp, win, "2v80", 4.0)["ok"]:
                    lo = mid
                else:
                    hi = mid
            cells.append("%.2f W" % lo)
        rows.append([eb.MONTHS[m - 1], "%+.0f" % t_c] + cells)
    o.table(["month", "cells C"] + [p[2] for p in panels], rows)
    o("   One night by hand, September: sun-down 11.28 h x %.1f W = %.0f Wh against %.1f Wh aged (4S6P, 3.00 V line, +20 C)." % (
        p_idle, 11.28 * p_idle, pack.usable_wh(p_idle, 20.0, pack.age80, "3v00", 6)[0]))
    o()

    o("3b. THE NIGHT STATE as in the record's sets 1 to 3 (%.2f W constant; LOW %.2f, HIGH %.2f), 2.80 V line, start 06:00, aged," % (
        p_night, ms["PS-NIGHT-RELAY"]["low"], ms["PS-NIGHT-RELAY"]["high"]))
    o("   with ONE charge current: 3.0 A (FW-A02), 4.0 A (1f) and 6.12 A (the record's two-pack runs, which one gauge's OCC1 refuses):")
    sets = ((100.0, 100.0, "set 1: 100 Wp"), (200.0, 100.0, "set 2: 200 Wp, 100 W"), (330.0, 300.0, "set 3: 330 Wp, 300 W"), (400.0, 1e9, "400 Wp, no window"))
    rows = []
    for m, t_c in months:
        for wp, win, lab in sets:
            cells = [verdict(one_run(m, t_c, lambda hh: p_night, wp, win, "2v80", ic_)) for ic_ in (3.0, 4.0, 6.12)]
            rows.append([eb.MONTHS[m - 1], "%+.0f" % t_c, lab] + cells)
    o.table(["month", "cells C", "set", "3.0 A", "4.0 A", "6.12 A"], rows)
    o()
    rows = []
    for lab_l, load in (("LOW", ms["PS-NIGHT-RELAY"]["low"]), ("HIGH", ms["PS-NIGHT-RELAY"]["high"])):
        for m, t_c in months:
            for wp, win, lab in sets[1:3]:
                rows.append([lab_l, "%.2f" % load, eb.MONTHS[m - 1], "%+.0f" % t_c, lab, verdict(one_run(m, t_c, lambda hh, load=load: load, wp, win, "2v80", 4.0))])
    o.table(["night state", "W", "month", "cells C", "set", "4.0 A"], rows)
    o()

    def tmin(m, wp, win, load, ic_, dod="2v80"):
        f = lambda t: one_run(m, t, lambda hh: load, wp, win, dod, ic_)["ok"]
        return eb.bisect(f, 0.0, 20.0)

    def wmax(m, t_c, wp, win, ic_):
        lo, hi = 0.0, 40.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if one_run(m, t_c, lambda hh, mid=mid: mid, wp, win, "2v80", ic_)["ok"]:
                lo = mid
            else:
                hi = mid
        return lo
    o("   Set 2's conditions on 4S6P (September, 200 Wp, 100 W, 2.80 V line):")
    rows = []
    for ic_ in (3.0, 4.0, 6.12):
        t = tmin(9, 200.0, 100.0, p_night, ic_)
        rows.append(["%.2f" % ic_, ("%.2f C" % t) if t is not None else "none at or below +20 C", "%.2f W" % wmax(9, 20.0, 200.0, 100.0, ic_),
                     verdict(one_run(9, 15.0, lambda hh: p_night, 200.0, 100.0, "2v80", ic_))])
    o.table(["charge A", "least cell temperature that meets it", "largest night load met at +20 C", "cells at +15 C"], rows)
    o()

    o("3c. A DAY AND NIGHT SCHEDULE (this study's; not in the record): PS-IDLE-SPEC in every hour the PVGIS mean-day profile is lit,")
    o("   the night state otherwise; usable energy at the day load; 2.80 V line, charge 4.0 A, aged, start 06:00:")
    rows = []
    for m, t_c in months:
        prof = res4["months"][m]["profile"]
        lit = sum(1 for g in prof if g > 0)
        sched = lambda hh, prof=prof: p_idle if prof[hh] > 0 else p_night
        for wp, win, lab in panels:
            rows.append([eb.MONTHS[m - 1], "%+.0f" % t_c, "%d" % lit, lab, verdict(one_run(m, t_c, sched, wp, win, "2v80", 4.0))])
    o.table(["month", "cells C", "lit hours", "panel", "72 h"], rows)
    o()
    o("   and SUN-FOLLOWING: PS-IDLE-SPEC only in the hours the panel alone carries it at the node, the night state otherwise:")
    rows = []
    for m, t_c in months:
        prof = res4["months"][m]["profile"]
        for wp, win, lab in panels:
            carried = [hh for hh in range(24) if eb.node_w(prof[hh], wp, pr, win, eta) >= p_idle]
            sched = lambda hh, carried=carried: p_idle if hh in carried else p_night
            rows.append([eb.MONTHS[m - 1], "%+.0f" % t_c, lab, "%d" % len(carried), verdict(one_run(m, t_c, sched, wp, win, "2v80", 4.0))])
    o.table(["month", "cells C", "panel", "hours at PS-IDLE-SPEC a day", "72 h"], rows)
    o()

    # ================================================================================== 4. CONSEQUENCES
    o("4. CONSEQUENCES")
    m_cell = d["pack"]["cell_mass_g_max"]["value"]
    o("4a. Mass: 12 more cells at %.0f g maximum each (spec 3.10): +%.0f g of cells, %.0f g for 24; harness, strip, wrap, fuses, the" % (m_cell, 12 * m_cell, 24 * m_cell))
    o("   second mat and the second second-level parts are not weighed here (ESTIMATE under 150 g with the harness's copper at")
    o("   %.1f g/m per 12 AWG conductor)." % mass_g_m)
    o()
    o("4b. Key-down at the %.0f A peak, the cells' own I2R, adiabatic (POWER-THERMAL 7.2's method):" % T["key_peak_a"])
    rows = []
    for lab, n_cells, i_cell in (("4S3P (the record)", 12, T["key_peak_a"] / 3), ("4S6P, even share", 24, T["key_peak_a"] / 6), ("4S6P, the east block at its share", 12, T["key_peak_a"] * s_hi / 3)):
        k_lo = (i_cell ** 2 * T["r_cell_ohm"][0]) / (m_cell * T["cp_j_gk"][1]) * 60.0
        k_hi = (i_cell ** 2 * T["r_cell_ohm"][1]) / (m_cell * T["cp_j_gk"][0]) * 60.0
        rows.append([lab, "%.2f" % i_cell, "%.2f to %.2f" % (k_lo, k_hi), "%.0f to %.0f" % (5.0 / k_hi * 60, 5.0 / k_lo * 60)])
    o.table(["pack", "A a cell", "K per minute", "s for the 5 K from 55 to 60 C"], rows)
    o()
    rilm_a, rilm_b = T["tps2596_rilm"]
    hv = calls_with_first_arg(os.path.join(root, "v2/ecad/tools/gen_sch_a.py"), {"rail"}, "VHEAT")
    hvin = calls_with_first_arg(os.path.join(root, "v2/ecad/tools/gen_sch_a.py"), {"rail"}, "VHEAT_IN")
    u22 = calls_with_first_arg(os.path.join(root, "v2/ecad/tools/gen_sch_a.py"), {"efuse"}, "U22")
    if len(hv) != 1 or len(hvin) != 1 or len(u22) != 1:
        raise InputError("gen_sch_a.py: expected one VHEAT rail, one VHEAT_IN rail and one U22 efuse call, found %d, %d, %d" % (len(hv), len(hvin), len(u22)))
    eff = kw(hv[0], "efficiency")
    vh_a = ast.literal_eval(hv[0].args[2])
    vhin_a = ast.literal_eval(hvin[0].args[2])
    ilim_txt = ast.literal_eval(u22[0].args[6])
    r_ilm = float(ilim_txt.split("R")[0])
    ilim = rilm_a / r_ilm - rilm_b
    o("4c. The heater branch on board A (gen_sch_a.py, parsed): VHEAT declared %.2f A at 12 V (efficiency %.2f), VHEAT_IN %.2f A at 14.4 V," % (vh_a, eff, vhin_a))
    o("   U22's ILM resistor %s gives %.2f A (TPS2596 equation 7; the generator's note rounds it to 1.0 A). Two mats (one under each block, %.1f W each at 12 V):" % (ilim_txt.split(" (")[0], ilim, T["heater_w"]))
    rows = []
    for n in (1, 2):
        p_out = n * T["heater_w"]
        for v in (14.4, 12.0):
            i_in = p_out / eff / v
            rows.append(["%d" % n, "%.1f" % p_out, "%.2f" % (p_out / 12.0), "%.1f" % v, "%.2f" % i_in, "yes" if i_in <= ilim else "NO"])
    o.table(["mats", "W at 12 V", "VHEAT A", "pack V", "VHEAT_IN A", "under U22's limit"], rows)
    r_new = rilm_a / (2.0 + rilm_b)
    o("   A 2.0 A limit needs RILM %.0f ohm (the 453R the same comment lists). At full duty (the mats' rating, an upper bound; the" % r_new)
    o("   duty is set by the loss, which no held figure gives) the heater at the pack is %.1f W with one mat and %.1f W with two:" % (T["heater_w"] / eff, 2 * T["heater_w"] / eff))
    rows = []
    for m in (12, 1, 9):
        # the night lengths of energy_budget section 3 (15th of the month, sunrise and sunset at -0.833 degrees)
        doy = sum(eb.DAYS[:m - 1]) + 15
        night = 24.0 - eb.day_length_h(d["solar"]["latitude_deg"], eb.declination_deg(doy), -0.833)
        rows.append([eb.MONTHS[m - 1], "%.2f" % night, "%.0f" % (night * T["heater_w"] / eff), "%.0f" % (night * 2 * T["heater_w"] / eff),
                     "%.0f" % pack.usable_wh(p_night, 5.0, pack.age80, "3v00", 3)[0], "%.0f" % pack.usable_wh(p_night, -10.0, pack.age80, "3v00", 3)[0]])
    o.table(["month", "sun-down h", "one mat Wh a night", "two mats Wh a night", "second block adds, aged, +5 C, Wh", "at -10 C, Wh"], rows)
    o()
    o("4d. Cost, ESTIMATE (no quotation held except the JLC figures gen_sch_p.py quotes): 12 cells about 50 EUR (the record's");
    o("   section 6); the second level for the west block (BQ7720700DSSR 2.12 USD at JLC per gen_sch_p.py, its filters, NTC and")
    o("   sockets) under 10 EUR; string and link fuses with holders under 25 EUR; the harness (about 1.5 m of 12 AWG silicone and")
    o("   sense wire, housings) under 20 EUR; a second heater mat (no price held) under 30 EUR; wrap, strip and hold-down under")
    o("   15 EUR: under 150 EUR of parts, plus a second block build and the protection commissioning of TEST-PLAN.md section 5.")
    o()
    o("END. REQ-072 as written: FAIL on these figures (section 8 of ENERGY-RECONCILIATION.md).")
    return o.text()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.normpath(os.path.join(HERE, "..", "..", "..", "..")))
    a = ap.parse_args()
    try:
        sys.stdout.write(run(a.root))
    except InputError as e:
        sys.stderr.write("energy_4s6p: %s\n" % e)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
