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
field-weather reliability claim. Run from the repository root:
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

EB_SHA256 = "cf6c377fa1015a468a61dc83f1c735e54b5f778eb3bb39834495ee2eb24d02c1"   # the model section 9 pinned
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
    "chg_a_base": (4.0, "SESSION (section 8a): U3 ChargeCurrent at most 4.0 A for the 4S6P base, OCC1 5.0 A unchanged; register code 31 x 128 mA = 3.968 A (SLUSE66A Table 9-7) is the nearest at or below"),
    "chg_a_lid": (8.0, "SESSION: U3B ChargeCurrent 8.0 A for the 4S12P lid, the same 0.67 A a cell as the base; code 62 x 128 mA = 7.936 A; the lid gauge's OCC1 at 10.0 A true (GAUGE.md)"),
    "iin_lid_a": (8.0, "SESSION: U3B IIN_HOST 8.0 A nominal from VBAT, code 80 (seven bits of 100 mA with RAC 5 mOhm, RSNS_RAC = 1b, SLUSE66A 9.6.22 Table 9-50, page 80; 8.2 A maximum with the 200 mA the register text adds); 3.3 uH on IADPT's 169 k so that Table 9-1 allows 10 A"),
    "eta_u3b": (0.975, "MAKER, read from a plot: SLUSE66A Figure 8-3 (VIN 15 V, VOUT 14.8 V, RAC = RSR = 5 mOhm, 4.7 uH, 400 kHz) reads about 98.5 percent from 3 to 6 A and 98 at 8 A (AI reading of the page image); 0.975 carries board A's 3.3 uH and layout; bracket 0.96 to 0.985"),
    "r_lid_dsg": (0.030, "ESTIMATE, ohm: the lid's discharge loop: hinge harness 12 AWG 2 x 0.6 m at 5.21 mOhm/m (6.3), two inline blade fuses (2 x 3.0, no maker resistance held), two XT60 pairs (2 x 0.5), board PL's F1, F2, Q1, Q2 and R10 (3.0 + 2.0 + 0.69 + 0.69 + 2.0 at the makers' maxima where held), the LM5069 FET 0.96 and its sense 5.6 mOhm; bracket 0.020 to 0.045"),
    "r_cl": (0.0056, "SESSION: the LM5069's sense resistor, 5.6 mOhm: VCL 48.5 / 55 / 61.5 mV (SNVS452G page 6) gives 8.7 / 9.8 / 11.0 A, so a join can never push more than 11.0 A (1.83 A a base cell, under the 35E's 2.0 A maximum charge, spec 3.7) into the base, and the lid's share of the kit's 10 A continuous (6.7 A) stays under the 8.7 A minimum"),
    "v_ak": (0.020, "MAKER: LM74700-Q1 regulated forward V(AK) 13 / 20 / 29 mV (SNOSD17G 6.5, page 6): the ideal diode holds 20 mV across its FET until the FET is fully on"),
    "r_lid_chg": (0.028, "ESTIMATE, ohm: the lid's charge loop: U3B's RSR 5 mOhm, the same harness, fuses and connectors (14.3), board PL's F1, F2, Q1, Q2, R10 (8.4); bracket 0.020 to 0.045"),
    "fe_out_w": (5.7 * 20.7, "GEN: board A's front end U2 limits at VSNS 57 mV over R11 10 mOhm, 5.7 A at 20.7 V (gen_sch_e.py:104-107 as energy_inputs.yaml front_end_draw_w reads it)"),
    "u3_iin_max_a": (6.35, "MAKER: with RAC 10 mOhm (R16 as generated, RSNS_RAC = 0b) IIN_HOST is clamped at 6.35 A (SLUSE66A 9.3.5 and Table 9-1, pages 25 and 26)"),
    "u3_iin_e1_a": (5.40, "SESSION: U3 IIN_HOST 5.40 A with R16 as generated (10 mOhm, 50 mA steps), about 5 percent under the front end's 5.7 A so that U3's input loop, not the front end's current limit, holds the bus (the LM5176's VSNS tolerance is not read here: a desk item)"),
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
           "what": "board A as generated, FW-A16 revised for the panel: U3's IIN_HOST at 5.40 A under the front end's 5.7 A (111.8 W into U3)"},
    "E2": None,
}
ENTRY_WHAT_E2 = "the entry re-rated (TOPOLOGY.md / CHARGER.md drafts): nothing under the stage's window caps the node"


# ------------------------------------------------------------------------------------------- the two stores
def taper(cap, soc, t):
    return cap if soc < t else cap * max(0.0, (1.0 - soc) / (1.0 - t))


def lid_node_from_terminal(t_w, v_l, eta_b, r):
    """Node power U3B must draw to put t_w into the lid pack's terminals (conversion, then the charge loop's I2R)."""
    i = t_w / v_l
    return (t_w + i * i * r) / eta_b


def lid_terminal_from_node(a_w, v_l, eta_b, r):
    """The inverse of lid_node_from_terminal, by bisection (monotone)."""
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
                cl = min(lid_node_from_terminal(cl_t, v_l, cfg["eta_b"], cfg["r_chg"]), cfg["iin_l"] * v_b)
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
                t_w = lid_terminal_from_node(a_l, v_l, cfg["eta_b"], cfg["r_chg"])
                loss["u3b"] += a_l * (1.0 - cfg["eta_b"])
                loss["chg_loop"] += a_l * cfg["eta_b"] - t_w
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
                "eta_b": 1.0, "r_dsg": 0.0, "v_ak": 0.0, "r_chg": 0.0, "entry": "E2"})
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
    for k in ("E0", "E1"):
        e = ENTRIES[k]
        P("   entry %s: front end out at most %.1f W, U3 input at most %.1f W: %s" % (k, e["fe_out_w"], e["u3_in_w"], e["what"]))
    P("   entry E2: %s" % ENTRY_WHAT_E2)
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
                      ("U3B at 0.96, loops at 45 mOhm, V(AK) 29 mV", {"eta_b": 0.96, "r_dsg": 0.045, "r_chg": 0.045, "v_ak": 0.029}),
                      ("U3B at 0.985, loops at 20 mOhm", {"eta_b": 0.985, "r_dsg": 0.020, "r_chg": 0.020}),
                      ("ceilings at the cycle-life 1.02 A a cell (6.12 A, 12.24 A; U3B input 10 A)", {"chg_a_b": 6.12, "chg_a_l": 12.24, "iin_l": 10.0}),
                      ("base ceiling at FW-A02's 3.0 A as filed", {"chg_a_b": 3.0})):
        cfg = base_cfg(); cfg.update(over)
        P("   %-72s %s" % (lab + ":", fmt_run(both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg))))
    P("")
    P("5. THE ENTRY INTO BOARD A (the node's cap), 400 Wp, 200 W, lid at the basis")
    for ek in ("E0", "E1", "E2"):
        cfg = base_cfg(); cfg["entry"] = ek
        rs = both(d, pack, res4, prof, 400, 200.0, v("t_base_c"), t_basis, cfg)
        what = ENTRIES[ek]["what"] if ENTRIES[ek] else ENTRY_WHAT_E2
        P("   %s (%s):" % (ek, what))
        P("       %s; peak node %.1f W" % (fmt_run(rs), max(r["peak"]["node"] for r in rs)))
        l2 = lowest_tl(400, 200.0, {"entry": ek})
        P("       lowest lid temperature meeting M1: %s" % ("%+.1f C" % l2 if l2 is not None else "none up to +40 C"))
    for wp in (650, 800):
        cfg = base_cfg(); cfg["entry"] = "E1"
        rs = both(d, pack, res4, prof, wp, 200.0, v("t_base_c"), t_basis, cfg)
        P("   E1 with %d Wp: %s" % (wp, fmt_run(rs)))
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
        t_w = lid_terminal_from_node(a_l, r["v_l"], cfg["eta_b"], cfg["r_chg"]) if a_l > 0 else 0.0
        i_l = t_w / r["v_l"]
        P("   %s: hour %d (%02d UTC), the sun offers %.1f W at the node: stage in %.1f W; front end out %.1f W = %.2f A on VBUS20 at %.1f V (its as-generated limit 5.7 A);" % (
            lab, h, hh, p_sun, p_stage_in, p_fe, i_in, V_BUS20))
        P("       front end loss %.1f W (at 0.93); U3 in %.2f A through R16 (10 mOhm: %.2f W; 5 mOhm: %.2f W), U3 loss %.1f W (at 0.98);" % (
            p_fe * (1.0 / e_fe - 1.0), i_in, i_in * i_in * 0.010, i_in * i_in * 0.005, p_fe * (1.0 - e_ch)))
        P("       U3 out %.1f W = %.2f A at the node's %.2f V (load %.1f W, base %.1f W = %.2f A through R17: %.2f W; U3B %.1f W = %.2f A from VBAT);" % (
            p_node, i_out, vb, load, a_b, i_b, i_b * i_b * 0.005, a_l, i_u3b_in))
        P("       U3B loss %.1f W (at %.3f), R16B 5 mOhm %.2f W, lid charge %.2f A (R17B 5 mOhm %.2f W), charge loop I2R %.2f W" % (
            a_l * (1.0 - cfg["eta_b"]), cfg["eta_b"], i_u3b_in * i_u3b_in * 0.005, i_l, i_l * i_l * 0.005, i_l * i_l * cfg["r_chg"]))
        for fsw in (400e3, 800e3):
            ripple = (V_BUS20 - vb) * vb / (V_BUS20 * 3.3e-6 * fsw)
            P("       U3's L2 (3.3 uH, Isat 12.2 A by its value text) in buck mode at %.0f kHz: average %.2f A, ripple %.2f A p-p, peak %.2f A" % (
                fsw / 1e3, i_out, ripple, i_out + ripple / 2.0))
    ld = LOAD * NP_L / NP_T / r["v_l"]
    P("   the lid's discharge path at the night's share (%.2f A): LM74700-Q1 %.3f W (20 mV), LM5069 FET %.3f W (0.96 mOhm max)," % (
        ld, ld * v("v_ak"), ld * ld * 0.00096))
    icl = 0.0615 / v("r_cl")
    P("       its %.1f mOhm sense %.3f W; at the lid path's largest current, its limit's maximum %.1f A: %.2f W, %.2f W, %.2f W" % (
        1e3 * v("r_cl"), ld * ld * v("r_cl"), icl, icl * v("v_ak"), icl * icl * 0.00096, icl * icl * v("r_cl")))
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
    for dv in (0.05, 0.10, 0.20, 0.30, 0.50, 1.00, 2.00, 4.80):
        i = min(dv / (r_l + r_b), 0.0615 / v("r_cl"))
        P("   %8.2f %10.2f %14.2f %22s %22s" % (dv, i, i / NP_B, "trips" if i > 5.0 else "holds", "EXCEEDED" if i / NP_B > 2.0 else "within"))
    P("   A lid pack fuller than the base by 0.20 V (50 mV a cell) pushes at most %.1f A into the base: under U3's 4.0 A setting." % (0.20 / (r_l + r_b)))
    P("")
    P("END. Every row is the record's model on the reference day with the stated departures; none is a demonstration.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
