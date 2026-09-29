#!/usr/bin/env python3
"""energy_two_pack.py: mission M1 on TWO separately protected packs (stream a1elec, MESHSAT-1357, 29 September 2026).

PROTOTYPE DESIGN, AI arithmetic: nothing is built, ordered or measured, and nothing printed is a measurement.

Why. An outside review of energy_architecture.py (records/energy, section 9) found that it passes ONE parallel count
into ONE simulate(): one store, one cell temperature, one state of charge and a charge ceiling scaled with the count.
Option A(i) is two packs: the base pockets' 4S6P under board P (section 8) and a lid module of 4S12P under its own
protection and gauge board, joined at the system node VBAT by the path of TOPOLOGY.md (beside this file): the base
pack on the BQ25731 U3 as generated (R17), the lid pack charged by a second BQ25731 U3B fed from VBAT and discharging
into VBAT through an LM74700-Q1 ideal diode in series with an LM5069 current-limited switch.

What this script does. It imports records/energy/energy_budget.py UNCHANGED (pinned by sha256, as energy_architecture.py
does) for the cell model (Pack.usable_wh), the September reference-day profile, the solar chain and the node rule, and
runs its own hour-by-hour balance with:
  * two stores, each with its own usable energy at its own cell temperature and its own share of the load;
  * two charge ceilings (U3's ChargeCurrent for the base; U3B's ChargeCurrent and input limit for the lid), each with
    its own taper on its own state of charge, and a stated allocation policy with spill-over;
  * the lid path's added losses (U3B's conversion, the hinge harness, the ideal diode's regulated drop, the switch);
  * the entry into board A as a cap on the node's power (three cases: the host contract FW-A16 as written with the
    panel, the circuit as generated with FW-A16 revised, and the entry re-rated as TOPOLOGY.md drafts);
  * each pack's own lowest point; the fault cases (lid empty, lid cold, one pack out).
Before printing anything it proves a CONSERVATIVE EQUIVALENCE: with the lid at +20 C, zero path losses, U3B lossless,
ceilings in proportion and no entry cap, the two-pack balance reproduces energy_budget.simulate() at 4S18P hour for
hour (first stop, lowest point and unserved energy) on eight cases; it refuses to print (exit 4) if it does not.

Scope, as section 9's: the September reference day (PVGIS's monthly-average hourly profile repeated for three days),
aged to 80 percent, the 3.00 V line with the 5 percent reserve, both start hours (06:00 and 18:00 UTC), PS-IDLE-SPEC
at 42.8 W at the pack terminals, the stage's input window as stated per run. A reference-day model result, not a
field-weather reliability claim.

Second issue (stream s119, S-119, 29 September 2026, its second round after the independent check): the charger rows
restated from the drawn FETs' losses (TI SLUSE66A Equations 6 to 22). U3's row comes in through energy_inputs.yaml (0.98
to 0.979, decision 57's FETs on board A, v2/docs/records/s117/efficiency.out) with energy_budget.py re-pinned. U3B is
drawn on the 400 kHz row by the S-119 session decision (records/s119/apply_decision_s119.py): eta_u3b moves from 0.975
to 0.972 (0.963 to 0.978), weighted over the model's own hours (records/s119/u3b_hourly.out); IIN_HOST 8.0 to 6.2 A on
the 10 mOhm R16B; the charge loop 28 to 23 mOhm (U3B's RSR is inside eta_u3b and was counted twice). Section 4's U3B
bracket rows take that bracket and the input clamp; section 7 prints U3's loss at the chain's figure, the sense
resistors as parts of each charger's loss, and U3's L2 as board A draws it (4.7 uH XAL1010-472ME at 400 kHz, decision
56). U3B's efficiency may also be given as a function of its input power (eta_at), which only the analysis scripts of
records/s119 use; the model's own runs carry the figure. Nothing else changed.
Run from the repository root:
  python3 v2/docs/records/a1elec/energy_two_pack.py > v2/docs/records/a1elec/energy_two_pack.out
Deterministic: no date, host or absolute path in the output. Exit 2: energy_inputs.yaml is not the pinned file;
exit 3: energy_budget.py, a pinned input or the daily profile changed; exit 4: the equivalence check failed."""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EDIR = os.path.join(ROOT, "v2", "docs", "records", "energy")
sys.path.insert(0, EDIR)
import yaml  # noqa: E402
import energy_budget as EB  # noqa: E402

EB_SHA256 = "6a8ac4642bd2aaf35d5ad6b75c5004c24d3e11ed1ede09a4b7a1041cd103235c"   # energy_budget.py second issue (s119; was cf6c377f, the model section 9 pinned)
DRCALC = os.path.join(HERE, "inputs", "pvgis-leiden-daily-profile-2005-2020.json")
DRCALC_SHA256 = "4d974567cc49315dade4a63736b0d428fce9b5e645362052390c94c56fde1210"  # the value energy_inputs.yaml names
MONTH = 9
LOAD = 42.8
NP_B, NP_L = 6, 12
NP_T = NP_B + NP_L

# ------------------------------------------------------------------------------------------ the design parameters
# Every number with its kind. MAKER = a maker's document held in v2/vendor; GEN = a generator line; SESSION = this
# stream's setting (authority SESSION, reversible); ESTIMATE = arithmetic on assumptions stated beside it.
PAR = {
    "t_base_c": (20.0, "REQ-014's +20 C, the basis of sections 8 and 9: the base pack in the closed base with the kit's own heat"),
    "chg_a_base": (3.968, "SESSION (section 8a's 4.0 A for the 4S6P base as a register value): U3 ChargeCurrent code 31 x 128 mA = 3.968 A (SLUSE66A Table 9-7), the nearest at or below 4.0 A; OCC1 5.0 A unchanged"),
    "chg_a_lid": (7.936, "SESSION: U3B ChargeCurrent code 62 x 128 mA = 7.936 A for the 4S12P lid, 0.66 A a cell; the lid gauge's OCC1 at 10.0 A true (GAUGE.md)"),
    "iin_lid_a": (6.2, "SESSION (the S-119 U3B decision, records/s119/apply_decision_s119.py): U3B IIN_HOST 6.2 A nominal from VBAT with R16B 10 mOhm (RSNS_RAC = 0b, 50 mA steps, code 124; SLUSE66A 9.6.22 page 80 adds 100 mA for the maximum, 6.3 A), under the 6.35 A clamp of 9.3.5 and Table 9-1 (pages 25 and 26), 4.7 uH on IADPT's 191 k (Table 9-4, page 27); the model's largest U3B input is about 4.1 A, so the limit does not bind. The first issue's 8.0 A on 5 mOhm and 3.3 uH is superseded"),
    "eta_u3b": (0.972, "INFERRED by TI's method, not a figure TI states for this circuit: SLUSE66A Equations 6 to 22 (printed pages 86 to 88) as records/s117/efficiency.py implements them, on U3B as the S-119 decision draws it (the 400 kHz row: L2B XAL1010-472ME, 191 k on IADPT, R16B 10 mOhm and R17B 5 mOhm counted, Q7B and Q9B CSD17578Q5A, Q8B and Q10B CSD17577Q5A), in the buck-boost bound at every hour and weighted by the energy U3B takes in each of the model's own hours; the lowest over both lid options, both ratio cases and both starts, TI's reading 0.9724 rounded down (records/s119/u3b_hourly.out). 0.974 at the model's peak hour and 0.943 in the worst hour of 5 W or more. The inductor's core loss is EXCLUDED (Coilcraft Document 804-1 prints none), so the figure is high by it. Second issue (stream s119, S-119), second round after its independent check (item M1): the first round's 0.961 was the 800 kHz row at the peak hour, U3B's most favourable load; the first issue's 0.975 was an AI reading of Figure 8-3, superseded"),
    "eta_u3b_lo": (0.963, "the bracket's low end: eta_u3b's method at the makers' maxima, the lowest over the same cases (records/s119/u3b_hourly.out)"),
    "eta_u3b_hi": (0.978, "the bracket's high end: eta_u3b's method at the most favourable reading, the highest over the same cases (records/s119/u3b_hourly.out)"),
    "r_lid_dsg": (0.030, "ESTIMATE, ohm: the lid's discharge loop: hinge harness 12 AWG 2 x 0.6 m at 5.21 mOhm/m (6.3), two inline blade fuses (2 x 3.0, no maker resistance held), two XT60 pairs (2 x 0.5), board PL's F1, F2, Q1, Q2 and R10 (3.0 + 2.0 + 0.69 + 0.69 + 2.0 at the makers' maxima where held), the LM5069 FET 0.96 and its sense 5.6 mOhm; bracket 0.020 to 0.045"),
    "r_cl": (0.0056, "SESSION: the LM5069's sense resistor, 5.6 mOhm: VCL 48.5 / 55 / 61.5 mV (SNVS452G page 6) gives 8.7 / 9.8 / 11.0 A, so a join can never push more than 11.0 A (1.83 A a base cell, under the 35E's 2.0 A maximum charge, spec 3.7) into the base, and the lid's share of the kit's 10 A continuous (6.7 A) stays under the 8.7 A minimum"),
    "v_ak": (0.020, "MAKER: LM74700-Q1 regulated forward V(AK) 13 / 20 / 29 mV (SNOSD17G 6.5, page 6): the ideal diode holds 20 mV across its FET until the FET is fully on"),
    "r_lid_chg": (0.023, "ESTIMATE, ohm: the lid's charge loop beyond U3B's own sense resistors: the harness, fuses and connectors (14.3) and board PL's F1, F2, Q1, Q2, R10 (8.4); R16B and R17B are inside eta_u3b (TI's method counts them), so the first issue's 5 mOhm for U3B's RSR, counted twice, is removed (the check of stream s119, item M3); bracket 0.015 to 0.040"),
    "fe_out_w": (4.3 * 20.7, "MAKER: board A's front end U2 (LM5176) regulates its output current at VSNS 43 / 50 / 57 mV min / typ / max (TI SNVSAI1D 6.5, PDF page 7, the constant current loop) over R11 10 mOhm: 4.3 / 5.0 / 5.7 A at 20.7 V; a limit that must hold a load is taken at its MINIMUM, 4.3 A (gen_sch_e.py:104-107 quotes the triple and uses 57 mV only to size copper)"),
    "fe_r11_draft_mohm": (6.2, "SESSION (draft): R11 6.2 mOhm, so the re-rated front end limits at 43 / 50 / 57 mV / 6.2 mOhm = 6.94 / 8.06 / 9.19 A; the stage and its copper are checked at 9.19 A by the generator owner"),
    "u3_iin_draft_a": (6.2, "SESSION (draft): U3 IIN_HOST 6.2 A nominal with R16 as generated (10 mOhm, RSNS_RAC = 0b, 50 mA steps, code 124; SLUSE66A 9.6.22 page 80 adds 100 mA for the maximum, 6.3 A, under the 6.35 A clamp of 9.3.5 and under the re-rated front end's 6.94 A minimum), so U3's input loop, not the front end's current limit, holds the bus"),
    "u3_iin_max_a": (6.35, "MAKER: with RAC 10 mOhm (R16 as generated, RSNS_RAC = 0b) IIN_HOST is clamped at 6.35 A (SLUSE66A 9.3.5 and Table 9-1, pages 25 and 26)"),
    "u3_iin_e1_a": (4.15, "SESSION: U3 IIN_HOST 4.15 A nominal with R16 as generated (code 83; 4.25 A maximum with the register text's 100 mA), under the as-generated front end's 4.3 A minimum, so U3's input loop holds the bus: 85.9 W into U3"),
    "fw_a16_in_w": (0.80 * 4.80 * 0.93 * 15.1, "FW-A16 (a) as written: charger input at most 0.80 x 4.80 A x 0.93 x VIN_RAW / 20.7 V at 20.7 V; with the panel's tracker on VIN_RAW at 15.1 V (TRK_OUT) that is 53.9 W into U3 (HW-FW-CONTRACT.md FW-A16, O-33)"),
}
V_BUS20 = 20.7


def v(key):
    return PAR[key][0]


# ---------------------------------------------------------------------------------------------------- inputs
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_model():
    ip = os.path.join(EDIR, "energy_inputs.yaml")
    if EB.sha256_of(ip) != EB.INPUTS_SHA256:
        sys.stderr.write("energy_two_pack: energy_inputs.yaml is not the file energy_budget.py pins; refusing\n")
        sys.exit(2)
    if sha(os.path.join(EDIR, "energy_budget.py")) != EB_SHA256:
        sys.stderr.write("energy_two_pack: energy_budget.py changed; refusing\n")
        sys.exit(3)
    d = yaml.safe_load(open(ip, encoding="utf-8"))
    for p in d["pinned"]:
        full = os.path.join(ROOT, p["path"])
        if not os.path.exists(full) or EB.sha256_of(full) != p["sha256"]:
            sys.stderr.write("energy_two_pack: pinned input %s missing or changed; refusing\n" % p["path"])
            sys.exit(3)
    if not os.path.exists(DRCALC) or sha(DRCALC) != DRCALC_SHA256:
        sys.stderr.write("energy_two_pack: inputs/pvgis-leiden-daily-profile-2005-2020.json missing or changed; refusing\n")
        sys.exit(3)
    monthly = json.load(open(os.path.join(ROOT, d["pinned"][0]["path"]), encoding="utf-8"))
    pack = EB.Pack(d)
    res4 = EB.section4(EB.Out(), d, monthly)
    dr = json.load(open(DRCALC, encoding="utf-8"))
    t2m = [r["T2m"] for r in dr["outputs"]["daily_profile"] if r["month"] == MONTH]
    return d, pack, res4, t2m


# ------------------------------------------------------------------------------------------------ the node
def chain(d):
    c = d["solar"]["chain"]
    return c[0]["eta"], c[1]["eta"], c[2]["eta"]


def node_power(d, res4, g, wp, window, entry):
    """The system node's power from the sun in one hour. entry None: energy_budget.node_w exactly (no cap below the
    window). Otherwise the front end's output (VBUS20) is capped at entry['fe_out_w'] and U3's input at
    entry['u3_in_w'] before U3's efficiency."""
    if entry is None:
        return EB.node_w(g, wp, res4["pr"], window, res4["eta"])
    e_st, e_fe, e_ch = chain(d)
    p_in = min(EB.panel_w(g, wp, res4["pr"]), window)
    p_fe = min(p_in * e_st * e_fe, entry["fe_out_w"], entry["u3_in_w"])
    return p_fe * e_ch


ENTRIES = {
    "E0": {"fe_out_w": v("fe_out_w"), "u3_in_w": v("fw_a16_in_w"),
           "what": "FW-A16 as written, the panel's tracker on VIN_RAW (U3's input held at 53.9 W)"},
    "E1": {"fe_out_w": v("fe_out_w"), "u3_in_w": v("u3_iin_e1_a") * V_BUS20,
           "what": "board A as generated, FW-A16 revised for the panel: U3's IIN_HOST at 4.15 A under the front end's 4.3 A minimum (85.9 W into U3)"},
    "E2": {"fe_out_w": 0.043 / (v("fe_r11_draft_mohm") / 1000.0) * V_BUS20, "u3_in_w": v("u3_iin_draft_a") * V_BUS20,
           "what": "the entry re-rated as drafted: R11 6.2 mOhm (front end 6.94 A minimum) and U3's IIN_HOST 6.2 A (128.3 W into U3)"},
    "E3": None,
}
ENTRY_WHAT_E3 = "no cap under the stage's window (the unconstrained reference; 8.20 A at the busiest hour)"


# ------------------------------------------------------------------------------------------- the two stores
def taper(cap, soc, t):
    return cap if soc < t else cap * max(0.0, (1.0 - soc) / (1.0 - t))


def eta_at(eb, p_w):
    """U3B's efficiency: a figure, or (analysis scripts only) a function of U3B's input power from VBAT in W."""
    return eb(p_w) if callable(eb) else eb


def lid_node_for_terminal(t_w, v_l, eb, r):
    """Node power U3B draws to put t_w into the lid's terminals; eb a figure or a function of that node power."""
    if not callable(eb):
        return lid_node_from_terminal(t_w, v_l, eb, r)
    lo, hi = 0.0, 4.0 * (t_w + (t_w / v_l) ** 2 * r) + 1.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if lid_terminal_from_node(mid, v_l, eta_at(eb, mid), r) < t_w:
            lo = mid
        else:
            hi = mid
    return hi


def lid_node_from_terminal(t_w, v_l, eta_b, r):
    """Node power U3B must draw to put t_w into the lid pack's terminals (conversion, then the charge loop's I2R)."""
    i = t_w / v_l
    return (t_w + i * i * r) / eta_b


def lid_terminal_from_node(a_w, v_l, eta_b, r):
    """The inverse of lid_node_from_terminal, by bisection (monotone); nothing reaches the lid at no efficiency."""
    if eta_b <= 0.0:
        return 0.0
    lo, hi = 0.0, a_w * eta_b
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if lid_node_from_terminal(mid, v_l, eta_b, r) <= a_w:
            lo = mid
        else:
            hi = mid
    return lo


def lid_draw_for_node(p_w, v_l, v_ak, r):
    """Energy the lid store gives up to put p_w on the node: the ideal diode's regulated drop and the loop's I2R."""
    i = p_w / v_l
    return p_w + i * v_ak + i * i * r


def lid_node_for_draw(e_w, v_l, v_ak, r):
    lo, hi = 0.0, e_w
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if lid_draw_for_node(mid, v_l, v_ak, r) <= e_w:
            lo = mid
        else:
            hi = mid
    return lo


def base_cfg():
    return {"chg_a_b": v("chg_a_base"), "chg_a_l": v("chg_a_lid"), "iin_l": v("iin_lid_a"), "eta_b": v("eta_u3b"),
            "r_dsg": v("r_lid_dsg"), "v_ak": v("v_ak"), "r_chg": v("r_lid_chg"), "entry": "E2",
            "dpol": "ah", "cpol": "ah", "base": True, "lid": True, "lid_start": 1.0, "base_start": 1.0,
            "lid_charge_ok": None, "dod": "3v00"}


def sim(d, pack, res4, prof, wp, window, start_h, t_b, t_l, cfg, trace=None):
    age = pack.age80
    hours = d["mission"]["hours"]
    pb, pl = LOAD * NP_B / NP_T, LOAD * NP_L / NP_T          # each pack's share at an equal cell current
    eb_full = pack.usable_wh(pb, t_b, age, cfg["dod"], NP_B)[0] if cfg["base"] else 0.0
    el_full = pack.usable_wh(pl, t_l, age, cfg["dod"], NP_L)[0] if cfg["lid"] else 0.0
    v_b = pack.n_s * EB.interp(pack.vmean, pack.cell_current(pb, NP_B))
    v_l = pack.n_s * EB.interp(pack.vmean, pack.cell_current(pl, NP_L))
    cap_b = cfg["chg_a_b"] * v_b                     # W offered to the base's cells, as energy_budget's chg_max_w
    cap_l = cfg["chg_a_l"] * v_l                     # W into the lid's terminals
    win = d["pack"]["charge_window_c"]
    can_b = cfg["base"] and win["low"] <= t_b <= win["high"]
    can_l = cfg["lid"] and win["low"] <= t_l <= win["high"]
    if cfg["lid_charge_ok"] is not None:
        can_l = can_l and cfg["lid_charge_ok"]
    eta_c = pack.chg_eta
    tp = pack.taper
    entry = ENTRIES[cfg["entry"]]
    e_b, e_l = eb_full * cfg["base_start"], el_full * cfg["lid_start"]
    full_t = eb_full + el_full
    low_b, low_l, low_t = e_b, e_l, e_b + e_l
    running, first_stop, short = True, None, 0.0
    loss = {"u3b": 0.0, "chg_loop": 0.0, "dsg_path": 0.0}
    peak = {"node": 0.0, "a_b": 0.0, "a_l": 0.0, "p_l_dsg": 0.0}
    for h in range(hours):
        hh = (start_h + h) % 24
        p_sun = node_power(d, res4, prof[hh], wp, window, entry)
        peak["node"] = max(peak["node"], p_sun)
        if not running and (p_sun >= LOAD or (e_b + e_l) >= 0.5 * full_t):
            running = True
        load = LOAD if running else 0.0
        if not running:
            short += max(0.0, LOAD - p_sun)
        a_b = a_l = 0.0
        d_b = d_l = 0.0
        if p_sun >= load:
            s = p_sun - load
            cb = taper(cap_b, e_b / eb_full, tp) if (can_b and eb_full > 0) else 0.0
            if can_l and el_full > 0:
                cl_t = taper(cap_l, e_l / el_full, tp)
                cl = min(lid_node_for_terminal(cl_t, v_l, cfg["eta_b"], cfg["r_chg"]), cfg["iin_l"] * v_b)
            else:
                cl = 0.0
            if cfg["cpol"] == "ah":
                tb, tl = s * NP_B / NP_T, s * NP_L / NP_T
                a_b, a_l = min(tb, cb), min(tl, cl)
                rest = s - a_b - a_l
                a_b += min(rest, cb - a_b); rest = s - a_b - a_l
                a_l += min(rest, cl - a_l)
            elif cfg["cpol"] == "base_first":
                a_b = min(s, cb); a_l = min(s - a_b, cl)
            else:
                a_l = min(s, cl); a_b = min(s - a_l, cb)
            e_b = min(eb_full, e_b + a_b * eta_c)
            if a_l > 0.0:
                e_h = eta_at(cfg["eta_b"], a_l)
                t_w = lid_terminal_from_node(a_l, v_l, e_h, cfg["r_chg"])
                loss["u3b"] += a_l * (1.0 - e_h)
                loss["chg_loop"] += a_l * e_h - t_w
                e_l = min(el_full, e_l + t_w * eta_c)
        else:
            deficit = load - p_sun
            av_b = e_b
            av_l = lid_node_for_draw(e_l, v_l, cfg["v_ak"], cfg["r_dsg"]) if e_l > 0 else 0.0
            if cfg["dpol"] == "ah" and av_b > 0 and av_l > 0:
                d_b, d_l = min(deficit * NP_B / NP_T, av_b), min(deficit * NP_L / NP_T, av_l)
            elif cfg["dpol"] == "lid_first":
                d_l = min(deficit, av_l)
            else:
                d_b = min(deficit, av_b)
            rest = deficit - d_b - d_l
            add = min(rest, av_b - d_b); d_b += add; rest -= add
            add = min(rest, av_l - d_l); d_l += add; rest -= add
            if rest > 1e-9:
                short += rest
                e_b, e_l = 0.0, 0.0
                running = False
                if first_stop is None:
                    first_stop = h
            else:
                e_b -= d_b
                if d_l > 0:
                    draw = lid_draw_for_node(d_l, v_l, cfg["v_ak"], cfg["r_dsg"])
                    loss["dsg_path"] += draw - d_l
                    e_l = max(0.0, e_l - draw)
        peak["a_b"] = max(peak["a_b"], a_b)
        peak["a_l"] = max(peak["a_l"], a_l)
        peak["p_l_dsg"] = max(peak["p_l_dsg"], d_l)
        low_b, low_l, low_t = min(low_b, e_b), min(low_l, e_l), min(low_t, e_b + e_l)
        if trace is not None:
            trace.append((h, hh, p_sun, load, a_b, a_l, d_b, d_l, e_b, e_l, running))
    return {"ok": first_stop is None, "first_stop": first_stop, "short": short, "low_b": low_b, "low_l": low_l,
            "low_t": low_t, "eb_full": eb_full, "el_full": el_full, "end_b": e_b, "end_l": e_l, "v_b": v_b, "v_l": v_l,
            "cap_b": cap_b, "cap_l": cap_l, "loss": loss, "peak": peak}


def both(d, pack, res4, prof, wp, window, t_b, t_l, cfg):
    return [sim(d, pack, res4, prof, wp, window, s, t_b, t_l, cfg) for s in (6, 18)]


def verdict(rs):
    return all(r["ok"] for r in rs)


def fmt_run(rs):
    ok = verdict(rs)
    stops = [r["first_stop"] for r in rs]
    lb = min(r["low_b"] for r in rs); ll = min(r["low_l"] for r in rs); lt = min(r["low_t"] for r in rs)
    return "%-8s stops %-12s lowest base %6.1f Wh (%5.1f %%), lid %6.1f Wh (%5.1f %%), both %6.1f Wh; unserved %6.1f Wh" % (
        "MEETS" if ok else "NOT MET", str(stops), lb, 100.0 * lb / rs[0]["eb_full"] if rs[0]["eb_full"] else 0.0,
        ll, 100.0 * ll / rs[0]["el_full"] if rs[0]["el_full"] else 0.0, lt, max(r["short"] for r in rs))


# ------------------------------------------------------------------------------------ the equivalence check
def equivalence(d, pack, res4, prof):
    cfg = base_cfg()
    cfg.update({"chg_a_b": pack.chg_a * NP_B / pack.n_p, "chg_a_l": pack.chg_a * NP_L / pack.n_p, "iin_l": 1e9,
                "eta_b": 1.0, "r_dsg": 0.0, "v_ak": 0.0, "r_chg": 0.0, "entry": "E3"})
    rows, worst = [], 0.0
    for wp, window in ((400, 200.0), (650, 200.0), (400, 100.0), (1600, 100.0)):
        for st in (6, 18):
            _tr, agg = EB.simulate(d, pack, prof, LOAD, wp, window, res4["eta"], res4["pr"], st, 20.0, pack.age80,
                                   d["mission"]["hours"], "3v00", NP_T)
            two = sim(d, pack, res4, prof, wp, window, st, 20.0, 20.0, cfg)
            dl = abs(agg["lowest"] - two["low_t"]); ds = abs(agg["short_wh"] - two["short"])
            same = agg["first_stop"] == two["first_stop"] and dl < 1e-6 and ds < 1e-6 and abs(agg["e_full"] - two["eb_full"] - two["el_full"]) < 1e-6
            worst = max(worst, dl, ds)
            rows.append((wp, window, st, agg["first_stop"], two["first_stop"], agg["lowest"], two["low_t"], same))
    return rows, worst, all(r[-1] for r in rows)


# ------------------------------------------------------------------------------------------------------ main
def main():
    d, pack, res4, t2m = load_model()
    prof = res4["months"][MONTH]["profile"]
    o = []
    P = o.append
    P("M1 ON TWO SEPARATELY PROTECTED PACKS (energy_two_pack.py, stream a1elec, MESHSAT-1357). PROTOTYPE DESIGN: nothing")
    P("built, ordered or measured; AI arithmetic, not a qualified review. Model: records/energy/energy_budget.py imported")
    P("unchanged (sha256 %s...), its September reference day, chain %.4f, performance ratio %.4f, aged 80 percent," % (EB_SHA256[:16], res4["eta"], res4["pr"]))
    P("the 3.00 V line with the 5 percent reserve, both start hours (06 and 18 UTC), PS-IDLE-SPEC %.1f W at the pack terminals." % LOAD)
    P("")
    P("0. THE PARAMETERS (value; kind and source)")
    for k in sorted(PAR):
        P("   %-14s %10.4f  %s" % (k, PAR[k][0], PAR[k][1]))
    for k in ("E0", "E1", "E2"):
        e = ENTRIES[k]
        P("   entry %s: front end out at most %.1f W, U3 input at most %.1f W: %s" % (k, e["fe_out_w"], e["u3_in_w"], e["what"]))
    P("   entry E3: %s" % ENTRY_WHAT_E3)
    P("   base 4S%dP and lid 4S%dP of the ruled Samsung INR18650-35E; each pack's share of the load at an equal cell current," % (NP_B, NP_L))
    P("   %.2f W and %.2f W; charge allocation 'ah' (the node's surplus split %d:%d by capacity, each capped, the rest to the" % (LOAD * NP_B / NP_T, LOAD * NP_L / NP_T, NP_B, NP_L))
    P("   other); discharge 'ah' (the deficit split %d:%d while both hold energy, then the other alone)." % (NP_B, NP_L))
    P("")
    rows, worst, ok = equivalence(d, pack, res4, prof)
    P("1. CONSERVATIVE EQUIVALENCE: the two-pack balance with the lid at +20 C, no path loss, U3B lossless, ceilings of")
    P("   1.02 A a cell (6.12 A and 12.24 A) and no entry cap, against energy_budget.simulate() at 4S18P")
    P("   %6s %7s %6s %14s %14s %14s %14s %6s" % ("Wp", "window", "start", "stop (4S18P)", "stop (2 packs)", "lowest 4S18P", "lowest 2 packs", "same"))
    for r in rows:
        P("   %6d %7.0f %6d %14s %14s %14.4f %14.4f %6s" % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], "yes" if r[7] else "NO"))
    P("   largest difference %.2e Wh: %s" % (worst, "the two-pack model IS the aggregate model under those assumptions" if ok else "NOT EQUIVALENT"))
    if not ok:
        sys.stdout.write("\n".join(o) + "\n")
        sys.stderr.write("energy_two_pack: the equivalence check failed; refusing to print results\n")
        return 4
    P("   So every difference below comes from a named departure from the aggregate: the lid's temperature, the ceilings,")
    P("   the path losses, the entry cap or a fault.")
    P("")
    tmin, tmax, tmean = min(t2m), max(t2m), sum(t2m) / len(t2m)
    P("2. THE LID PACK'S TEMPERATURE BASIS")
    P("   M1 runs PS-IDLE-SPEC, the full mode; the lid is open in it (lid closed = reduced mode, ruling of 7 September 2026),")
    P("   so the lid module sits in the open lid, outside the closed base and the kit's own heat, in the shade the plate's")
    P("   shade rule (D-02e) gives. Its cells then follow the air: their own heating is %.1f mW a cell discharging at the" % (1000.0 * (LOAD * NP_L / NP_T / 14.5 / NP_L) ** 2 * 0.035))
    P("   lid's share and %.1f mW a cell charging at %.1f A (35 mOhm a cell, the class of the 34.5 mOhm DC figure energy_inputs.yaml carries), negligible." % (1000.0 * (v("chg_a_lid") / NP_L) ** 2 * 0.035, v("chg_a_lid")))
    P("   PVGIS's September mean day at the site (DRcalc T2m, 2005 to 2020, the file in inputs/): %.2f C at %02d UTC to %.2f C at" % (tmin, t2m.index(tmin), tmax))
    P("   %02d UTC, mean %.2f C. The model holds one temperature per pack for the 72 hours, so the lid is run at the mean day's" % (t2m.index(tmax), tmean))
    P("   MINIMUM, %.2f C (the basis; its cells' thermal lag of about an hour, ESTIMATE, only raises the night's temperature)," % tmin)
    P("   and across 5 to 20 C, with the lowest lid temperature at which each case still meets M1. A real September night")
    P("   is colder than the mean day's; the threshold says how much colder the case tolerates. The base stays at +%.0f C." % v("t_base_c"))
    P("   The temperature factor is energy_budget's line through the cell sheet's one cold point (spec 7.5: 40 percent at -10 C")
    P("   at 3,400 mA); energy_inputs.yaml names it a LOWER bound at the kit's 0.3 to 1.0 A a cell, and the lid runs at about")
    P("   0.16 A a cell, so every lid-temperature threshold below is conservative in that respect (it errs toward NOT MET).")
    P("")
    t_basis = round(tmin, 2)
    TL = [20.0, 17.0, round(tmean, 2), t_basis, 10.0, 7.5, 5.0]

    def run_table(title, wp, window, cfg_over):
        P(title)
        for tl in TL:
            cfg = base_cfg(); cfg.update(cfg_over)
            rs = both(d, pack, res4, prof, wp, window, v("t_base_c"), tl, cfg)
            P("   lid %+6.2f C: %s" % (tl, fmt_run(rs)))

    def lowest_tl(wp, window, cfg_over):
        cfg = base_cfg(); cfg.update(cfg_over)
        if not verdict(both(d, pack, res4, prof, wp, window, v("t_base_c"), 40.0, cfg)):
            return None
        lo, hi = -10.0, 40.0
        if verdict(both(d, pack, res4, prof, wp, window, v("t_base_c"), lo, cfg)):
            return lo
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if verdict(both(d, pack, res4, prof, wp, window, v("t_base_c"), mid, cfg)):
                hi = mid
            else:
                lo = mid
        return hi

    P("3. THE DESIGN CASE: 400 Wp into a 200 W stage (Option A(i)), entry re-rated (E2), the ceilings and losses of section 0")
    run_table("   3a. lid temperature swept (base +20 C):", 400, 200.0, {})
    lt = lowest_tl(400, 200.0, {})
    P("   3b. lowest lid temperature meeting M1: %s" % ("%+.1f C" % lt if lt is not None else "none up to +40 C"))
    cfg = base_cfg()
    rs = both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg)
    P("   3c. at the basis (lid %+.2f C) per start: " % t_basis)
    for st, r in zip((6, 18), rs):
        P("       start %02d UTC: %s, usable full base %.1f Wh, lid %.1f Wh; lowest base %.1f, lid %.1f Wh; U3B loss %.1f Wh, charge loop %.1f Wh, lid discharge path %.1f Wh over 72 h; peak node %.1f W, to base %.1f W, to U3B %.1f W" % (
            st, "MEETS" if r["ok"] else "NOT MET (stop h %s)" % r["first_stop"], r["eb_full"], r["el_full"], r["low_b"], r["low_l"],
            r["loss"]["u3b"], r["loss"]["chg_loop"], r["loss"]["dsg_path"], r["peak"]["node"], r["peak"]["a_b"], r["peak"]["a_l"]))
    agg = [EB.simulate(d, pack, prof, LOAD, 400, 200.0, res4["eta"], res4["pr"], st, 20.0, pack.age80, d["mission"]["hours"], "3v00", NP_T)[1] for st in (6, 18)]
    P("   3d. the aggregate 4S18P of section 9 on the same day, for comparison: %s, lowest %.1f Wh" % (
        "MEETS" if all(a["ok"] for a in agg) else "NOT MET", min(a["lowest"] for a in agg)))
    for wp in (650, 800):
        cfg = base_cfg()
        P("   3e. %d Wp, 200 W, E2, lid at the basis: %s; lowest lid temperature meeting M1: %s" % (
            wp, fmt_run(both(d, pack, res4, prof, wp, 200.0, v("t_base_c"), t_basis, cfg)),
            "%+.1f C" % lowest_tl(wp, 200.0, {})))
    cfg = base_cfg()
    rs = both(d, pack, res4, prof, 400, 200.0, 15.0, t_basis, cfg)
    P("   3f. the base at +15 C as well (section 9's second temperature), lid at the basis: %s" % fmt_run(rs))
    P("")
    P("4. THE ALLOCATION POLICIES AND THE BRACKETS at the basis (lid %+.2f C), 400 Wp, 200 W, E2" % t_basis)
    for lab, over in (("charge base first, discharge 'ah'", {"cpol": "base_first"}),
                      ("charge lid first, discharge 'ah'", {"cpol": "lid_first"}),
                      ("charge 'ah', discharge lid first", {"dpol": "lid_first"}),
                      ("charge 'ah', discharge base first", {"dpol": "base_first"}),
                      ("U3B at %.3f (makers' maxima), loops 40 and 45 mOhm, V(AK) 29 mV" % v("eta_u3b_lo"), {"eta_b": v("eta_u3b_lo"), "r_dsg": 0.045, "r_chg": 0.040, "v_ak": 0.029}),
                      ("U3B at %.3f (most favourable), loops 15 and 20 mOhm" % v("eta_u3b_hi"), {"eta_b": v("eta_u3b_hi"), "r_dsg": 0.020, "r_chg": 0.015}),
                      ("ceilings at the cycle-life 1.02 A a cell (6.12 A, 12.24 A; U3B input at its 6.35 A clamp)", {"chg_a_b": 6.12, "chg_a_l": 12.24, "iin_l": 6.35}),
                      ("base ceiling at FW-A02's 3.0 A as filed", {"chg_a_b": 3.0})):
        cfg = base_cfg(); cfg.update(over)
        P("   %-72s %s" % (lab + ":", fmt_run(both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg))))
    P("")
    P("5. THE ENTRY INTO BOARD A (the node's cap), 400 Wp, 200 W, lid at the basis")
    for ek in ("E0", "E1", "E2", "E3"):
        cfg = base_cfg(); cfg["entry"] = ek
        rs = both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg)
        what = ENTRIES[ek]["what"] if ENTRIES[ek] else ENTRY_WHAT_E3
        P("   %s (%s):" % (ek, what))
        P("       %s; peak node %.1f W" % (fmt_run(rs), max(r["peak"]["node"] for r in rs)))
        l2 = lowest_tl(400, 200.0, {"entry": ek})
        P("       lowest lid temperature meeting M1: %s" % ("%+.1f C" % l2 if l2 is not None else "none up to +40 C"))
    for wp in (650, 800):
        cfg = base_cfg(); cfg["entry"] = "E1"
        rs = both(d, pack, res4, prof, wp, 200.0, v("t_base_c"), t_basis, cfg)
        P("   E1 with %d Wp: %s" % (wp, fmt_run(rs)))
    P("   The as-generated front end at its three limits, with U3 set just under each (a node cap only; FW-A16 revised):")
    for ia, lab in ((4.3, "minimum"), (5.0, "typical"), (5.7, "maximum")):
        ENTRIES["_cap"] = {"fe_out_w": ia * V_BUS20, "u3_in_w": ia * V_BUS20, "what": ""}
        cfg = base_cfg(); cfg["entry"] = "_cap"
        P("       %.1f A (%s): %s" % (ia, lab, fmt_run(both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg))))

    def meets_cap(ia, need_low=None):
        ENTRIES["_cap"] = {"fe_out_w": ia * V_BUS20, "u3_in_w": ia * V_BUS20, "what": ""}
        cfg = base_cfg(); cfg["entry"] = "_cap"
        rs = both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg)
        return verdict(rs) and (need_low is None or min(r["low_t"] for r in rs) >= need_low)
    cfg = base_cfg(); cfg["entry"] = "E3"
    low3 = min(r["low_t"] for r in both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg))
    req = []
    for need in (None, low3 - 0.05):
        lo, hi = 3.0, 9.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if meets_cap(mid, need): hi = mid
            else: lo = mid
        req.append(hi)
    del ENTRIES["_cap"]
    P("   THE ENTRY REQUIREMENT on this model (lid at the basis): the current into U3 at VBUS20's 20.7 V that a limit must hold")
    P("   at its minimum: %.2f A (%.1f W) to meet M1 at all; %.2f A (%.1f W) to keep the unconstrained lowest point, %.1f Wh." % (
        req[0], req[0] * V_BUS20, req[1], req[1] * V_BUS20, low3))
    P("")
    P("6. THE FAULT CASES (400 Wp, 200 W, E2; base +20 C; lid at the basis unless stated)")
    faults = (("lid pack empty at the start (its protection had been open; base full)", {"lid_start": 0.0}, t_basis),
              ("base pack empty at the start (lid full)", {"base_start": 0.0}, t_basis),
              ("lid cold, -5 C (below the charge window: no lid charge; discharge on the model's line)", {}, -5.0),
              ("lid's protection open or the hinge harness fused open: the base 4S6P alone", {"lid": False}, t_basis),
              ("base's protection open: the lid 4S12P alone", {"base": False}, t_basis),
              ("U3B off (a lid charger fault): the lid discharges, never recharges", {"lid_charge_ok": False}, t_basis))
    for lab, over, tl in faults:
        cfg = base_cfg(); cfg.update(over)
        P("   %s:" % lab)
        P("       %s" % fmt_run(both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), tl, cfg)))
    P("")
    P("7. THE CHARGER AND ENTRY FIGURES at the design case's peak hour (E2, 400 Wp, 200 W, lid at the basis, start 06 UTC)")
    cfg = base_cfg()
    tr = []
    r = sim(d, pack, res4, prof, 400, 200.0, 6, v("t_base_c"), t_basis, cfg, trace=tr)
    e_st, e_fe, e_ch = chain(d)
    for lab, row in (("the hour U3 delivers most (load plus both charges)", max(tr, key=lambda x: x[3] + x[4] + x[5])),
                     ("the peak lid-charge hour", max(tr, key=lambda x: x[5]))):
        h, hh, p_sun, load, a_b, a_l, d_b, d_l, e_b, e_l, run = row
        p_node = load + a_b + a_l          # what U3 actually delivers: the sun offered p_sun, the packs accepted less
        p_fe = p_node / e_ch
        p_stage_in = p_fe / (e_st * e_fe)
        i_in = p_fe / V_BUS20
        vb = r["v_b"]
        i_out = p_node / vb
        i_b = a_b / vb
        i_u3b_in = a_l / vb
        e_b7 = eta_at(cfg["eta_b"], a_l)
        t_w = lid_terminal_from_node(a_l, r["v_l"], e_b7, cfg["r_chg"]) if a_l > 0 else 0.0
        i_l = t_w / r["v_l"]
        P("   %s: hour %d (%02d UTC), the sun offers %.1f W at the node: stage in %.1f W; front end out %.1f W = %.2f A on VBUS20 at %.1f V (as generated it limits at 4.3 / 5.0 / 5.7 A);" % (
            lab, h, hh, p_sun, p_stage_in, p_fe, i_in, V_BUS20))
        P("       front end loss %.1f W (at %.2f); U3 in %.2f A, U3 loss %.1f W (at %.3f, R16 10 mOhm %.2f W and R17 5 mOhm %.2f W inside it);" % (
            p_fe * (1.0 / e_fe - 1.0), e_fe, i_in, p_fe * (1.0 - e_ch), e_ch, i_in * i_in * 0.010, i_b * i_b * 0.005))
        P("       U3 out %.1f W = %.2f A at the node's %.2f V (load %.1f W, base %.1f W = %.2f A; U3B %.1f W = %.2f A from VBAT);" % (
            p_node, i_out, vb, load, a_b, i_b, a_l, i_u3b_in))
        P("       U3B loss %.1f W (at %.3f, R16B 10 mOhm %.2f W and R17B 5 mOhm %.2f W inside it), lid charge %.2f A, charge loop I2R %.2f W" % (
            a_l * (1.0 - e_b7), e_b7, i_u3b_in * i_u3b_in * 0.010, i_l * i_l * 0.005, i_l, i_l * i_l * cfg["r_chg"]))
        for fsw in (400e3,):
            ripple = (V_BUS20 - vb) * vb / (V_BUS20 * 4.7e-6 * fsw)
            P("       U3's L2 as drawn (4.7 uH XAL1010-472ME, Isat 25.4 A, Coilcraft Document 804-1; decision 56) in buck mode at %.0f kHz: average %.2f A, ripple %.2f A p-p, peak %.2f A" % (
                fsw / 1e3, i_out, ripple, i_out + ripple / 2.0))
    ld = LOAD * NP_L / NP_T / r["v_l"]
    P("   the lid's discharge path at the night's share (%.2f A): LM74700-Q1 %.3f W (20 mV), LM5069 FET %.3f W (0.96 mOhm max)," % (
        ld, ld * v("v_ak"), ld * ld * 0.00096))
    icl = 0.0615 / v("r_cl")
    P("       its %.1f mOhm sense %.3f W; in current limit the LM5069 holds its FET linear: see section 8 for its dissipation" % (
        1e3 * v("r_cl"), ld * ld * v("r_cl")))
    P("")
    P("8. THE JOIN CURRENT: the lid path conducting while the lid's open-circuit voltage is above the base's by dV (TOPOLOGY.md 3c)")
    r_cell = 0.035      # ohm, the cell's class figure pcb_energy_chain.yaml uses for the prospective fault (AC impedance; the DC
    #                     resistance is higher, so these currents are UPPER bounds)
    r_l = 4 * r_cell / NP_L + v("r_lid_dsg")
    r_b = 4 * r_cell / NP_B + 0.0025 + 0.002 + 2 * 0.00069 + 0.002 + 0.003 + 0.005
    P("   lid loop %.1f mOhm (cells 4 x 35 / 12 plus the discharge loop of section 0); base loop %.1f mOhm (cells 4 x 35 / 6, F1 2.52," % (1e3 * r_l, 1e3 * r_b))
    P("   F2 2.0 ESTIMATE, Q1 and Q2 0.69 each, R10 2.0, lead and XT60 3.0 ESTIMATE, R17 5.0); no load on the node (the worst case);")
    P("   the LM5069's limit over r_cl is %.1f to %.1f A (VCL 48.5 to 61.5 mV, SNVS452G page 6); the table takes the maximum" % (0.0485 / v("r_cl"), 0.0615 / v("r_cl")))
    P("   %8s %10s %14s %22s %22s" % ("dV (V)", "I (A)", "A a base cell", "base OCC1 5.0 A, 2 s", "cell max charge 2.0 A"))
    P("   %8s %10s %14s %22s %22s %24s" % ("dV (V)", "I (A)", "A a base cell", "base OCC1 5.0 A, 2 s", "cell max charge 2.0 A", "LM5069 FET in limit (W)"))
    for dv in (0.05, 0.10, 0.20, 0.30, 0.50, 1.00, 2.00, 4.80):
        i_free = dv / (r_l + r_b)
        i = min(i_free, 0.0615 / v("r_cl"))
        p_fet = max(0.0, dv - i * (r_l + r_b) - v("v_ak")) * i if i < i_free else 0.0
        P("   %8.2f %10.2f %14.2f %22s %22s %24s" % (dv, i, i / NP_B, "trips" if i > 5.0 else "holds", "EXCEEDED" if i / NP_B > 2.0 else "within",
                                               "%.1f (linear)" % p_fet if i < i_free else "not limiting"))
    P("   In current limit the FET takes the gap less the loops' drop: up to the last row's figure until the LM5069's power limit")
    P("   and fault timer (PWR and TIMER, sized by board A's owner with SNVS452G's procedure) turn it off; the -2 variant retries.")
    P("   A lid pack fuller than the base by 0.20 V (50 mV a cell) pushes at most %.1f A into the base: under U3's 3.968 A setting." % (0.20 / (r_l + r_b)))
    P("")
    P("END. Every row is the record's model on the reference day with the stated departures; none is a demonstration.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
