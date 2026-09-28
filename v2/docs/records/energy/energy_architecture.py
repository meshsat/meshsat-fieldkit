#!/usr/bin/env python3
"""M1 from the requirement side (stream energy, section 9 of ENERGY-RECONCILIATION.md; MESHSAT-1357, 29 September 2026).

The owner's instruction of 29 September 2026: M1 and REQ-072 stay as written (72 hours in PS-IDLE-SPEC on battery and
solar from a full aged pack on the reference day, September at Leiden), reduced capability does not replace them, and
external DC stays optional. This script starts from that mission and derives what it asks of the kit: the usable
storage, the solar harvest, the charging capability and the consumption budget. It reuses energy_budget.py's own
model unchanged (its Pack, its September reference-day profile, its conversion chain and its hour-by-hour simulate()),
checks the same pinned inputs, and sweeps the free parameters:
  * storage: 4S x n_p of the ruled cell (Samsung INR18650-35E, D-06), n_p = 3 to 80; the charger's cycle-life current
    scales with n_p at 1.02 A a cell, as simulate() already does;
  * solar: panel STC rating 100 to 1500 Wp of the 12 V class, the fixed 40 degree south plane;
  * the input window: REQ-016's 100 W into board E's stage, and 200, 300, 400 W and no window, as alternatives;
  * the consumption: PS-IDLE-SPEC at its PLAN of 42.8 W, and lower figures for the engineering alternatives.
A combination MEETS M1 when the kit runs all 72 hours from both start hours (06:00 and 18:00 UTC) with the cells at
+20 C (REQ-014's condition) and aged to 80 percent. It prints, per window and consumption, the smallest pack for each
panel, the storage floor no panel removes, the charge power the passing run used, and the cells' count, mass and
volume. It decides nothing: it is arithmetic on the record's model and its assumptions (mean-day profile, efficiency
chain, cell curves), and every row is a MODEL result, not a demonstration. Run: python3 energy_architecture.py."""
import json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yaml
import energy_budget as EB

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
WINDOWS = [(100.0, "100 W (REQ-016)"), (200.0, "200 W"), (300.0, "300 W"), (400.0, "400 W"), (1e9, "no window")]
PANELS = list(range(100, 1501, 50))
LOADS = [42.8, 40.0, 37.5, 35.0, 30.0]
NP_MAX = 80
MONTH = 9


def load_model():
    d = yaml.safe_load(open(os.path.join(HERE, "energy_inputs.yaml"), encoding="utf-8"))
    if EB.sha256_of(os.path.join(HERE, "energy_inputs.yaml")) != EB.INPUTS_SHA256:
        raise SystemExit("energy_architecture: energy_inputs.yaml is not the file energy_budget.py pins; refusing")
    for p in d["pinned"]:
        full = os.path.join(ROOT, p["path"])
        if not os.path.exists(full) or EB.sha256_of(full) != p["sha256"]:
            raise SystemExit("energy_architecture: pinned input %s missing or changed; refusing" % p["path"])
    monthly = json.load(open(os.path.join(ROOT, d["pinned"][0]["path"]), encoding="utf-8"))
    pack = EB.Pack(d)
    res4 = EB.section4(EB.Out(), d, monthly)
    return d, pack, res4


def run(d, pack, res4, load, wp, window, n_p, start, t_c=20.0):
    prof = res4["months"][MONTH]["profile"]
    tr, sm = EB.simulate(d, pack, prof, load, wp, window, res4["eta"], res4["pr"], start, t_c, pack.age80,
                         d["mission"]["hours"], "3v00", n_p)
    peak_chg = max([f for (_h, _hh, _g, _ps, _l, f, _e, _r) in tr] + [0.0])
    return sm, peak_chg


def meets(d, pack, res4, load, wp, window, n_p, t_c=20.0):
    out = [run(d, pack, res4, load, wp, window, n_p, s, t_c) for s in (6, 18)]
    return all(sm["ok"] for sm, _ in out), out


def min_np(d, pack, res4, load, wp, window, t_c=20.0):
    for n_p in range(3, NP_MAX + 1):
        ok, out = meets(d, pack, res4, load, wp, window, n_p, t_c)
        if ok:
            return n_p, out
    return None, None


def cells(d, n_p):
    p = d["pack"]
    n = p["series"] * n_p
    vol_l = n * (p["cell_dia_mm_max"]["value"] ** 2) * p["cell_len_mm_max"]["value"] / 1e6
    return n, n * p["cell_mass_g_max"]["value"] / 1000.0, vol_l, 144.7 / 12.0 * n


def main():
    d, pack, res4 = load_model()
    prof = res4["months"][MONTH]["profile"]
    o = []
    o.append("M1 FROM THE REQUIREMENT SIDE (energy_architecture.py, MESHSAT-1357). PROTOTYPE DESIGN: nothing built, ordered")
    o.append("or measured. Every row is a MODEL result on energy_budget.py's September reference day (mean-day profile, efficiency")
    o.append("chain %.4f, performance ratio %.4f, cells at +20 C aged to 80 percent, the 3.00 V line with the 5 percent reserve)," % (res4["eta"], res4["pr"]))
    o.append("both start hours; AI arithmetic, not a qualified review.")
    o.append("")
    L = 42.8
    o.append("1. THE CONSUMPTION BUDGET THE MISSION STATES")
    o.append("   PS-IDLE-SPEC at the pack: %.1f W PLAN; 24 h = %.1f Wh; 72 h = %.1f Wh; September sun-down %.2f h = %.1f Wh." % (
        L, 24 * L, 72 * L, 11.28, 11.28 * L))
    e1 = pack.usable_wh(L, 20.0, pack.age80, "3v00", 1)[0]
    o.append("   One parallel string of the ruled cell (4S1P) delivers %.2f Wh usable aged at +20 C at this load." % e1)
    o.append("")
    o.append("2. THE STORAGE FLOOR NO PANEL REMOVES (the hours the sun at the node stays under the load, summed as deficit)")
    rows = []
    for wv, wn in WINDOWS:
        for wp in (200, 400, 800, 1500, 20000):
            p_sun = [EB.node_w(g, wp, res4["pr"], wv, res4["eta"]) for g in prof]
            below = [h for h in range(24) if p_sun[h] < L]
            deficit = sum(L - p_sun[h] for h in below)
            harvest = sum(p_sun)
            rows.append((wn, wp, len(below), deficit, harvest))
    o.append("   %-16s %8s %14s %22s %20s" % ("window", "panel Wp", "h below load", "deficit Wh per day", "node harvest Wh/day"))
    for r in rows:
        o.append("   %-16s %8d %14d %22.1f %20.1f" % r)
    o.append("   The day asks %.1f Wh; a combination whose harvest is under it cannot hold 72 h on any storage the pack can carry" % (24 * L))
    o.append("   except by spending the pack across the days; the deficit is what storage must carry every night.")
    o.append("")
    o.append("3. THE SMALLEST PACK THAT MEETS M1, per window and panel (4S x n_p of the 35E; both starts; +20 C; aged 80 percent)")
    frontier = {}
    for load in LOADS:
        for wv, wn in WINDOWS:
            o.append("   consumption %.1f W, window %s:" % (load, wn))
            o.append("     %8s %5s %7s %12s %10s %9s %13s %16s" % ("panel Wp", "n_p", "cells", "usable Wh", "nominal Wh", "cells kg", "cells L (box)", "peak charge W"))
            best = None
            for wp in PANELS:
                n_p, out = min_np(d, pack, res4, load, wp, wv)
                if n_p is None:
                    continue
                n, kg, vol, nom = cells(d, n_p)
                use = pack.usable_wh(load, 20.0, pack.age80, "3v00", n_p)[0]
                pk = max(pc for _, pc in out)
                o.append("     %8d %5d %7d %12.1f %10.1f %9.2f %13.2f %16.1f" % (wp, n_p, n, use, nom, kg, vol, pk))
                if best is None or n_p < best[1]:
                    best = (wp, n_p, use, pk)
            if best is None:
                o.append("     no panel up to %d Wp meets M1 with n_p up to %d" % (PANELS[-1], NP_MAX))
            frontier[(load, wn)] = best
            o.append("")
    o.append("4. THE FRONTIER: the fewest cells that meet M1 for each consumption and window, and the panel that reaches it")
    o.append("   %-8s %-16s %9s %5s %12s %16s" % ("load W", "window", "panel Wp", "n_p", "usable Wh", "peak charge W"))
    for (load, wn), b in frontier.items():
        if b is None:
            o.append("   %-8.1f %-16s %9s %5s %12s %16s" % (load, wn, "none", "-", "-", "-"))
        else:
            o.append("   %-8.1f %-16s %9d %5d %12.1f %16.1f" % (load, wn, b[0], b[1], b[2], b[3]))
    o.append("")
    o.append("5. SENSITIVITY OF ONE CANDIDATE (the cell temperature and the efficiency chain; window 300 W, 42.8 W)")
    for t_c in (10.0, 15.0, 20.0, 25.0):
        for wp in (400, 600):
            n_p, out = min_np(d, pack, res4, 42.8, wp, 300.0, t_c)
            o.append("   cells at %+5.1f C, panel %4d Wp: smallest n_p %s" % (t_c, wp, n_p if n_p else "none up to %d" % NP_MAX))
    eta0 = res4["eta"]
    for eta, lab in ((res4["eta_lo"], "low bracket"), (res4["eta_hi"], "high bracket")):
        res4["eta"] = eta
        for wp in (400, 600):
            n_p, _ = min_np(d, pack, res4, 42.8, wp, 300.0)
            o.append("   chain %.4f (%s), panel %4d Wp: smallest n_p %s" % (eta, lab, wp, n_p if n_p else "none up to %d" % NP_MAX))
    res4["eta"] = eta0
    o.append("")
    o.append("6. THE CONSUMPTION BUDGET EACH STORAGE ALLOWS (the largest steady load that meets M1; both starts; +20 C)")
    o.append("   %-26s %-10s %9s %14s" % ("storage", "window", "panel Wp", "largest load W"))
    for n_p, lab in ((3, "4S3P, D-06 (one pocket)"), (6, "4S6P, both base pockets"), (15, "4S15P, base and lid"), (18, "4S18P")):
        for wv, wn in ((100.0, "100 W"), (200.0, "200 W"), (300.0, "300 W")):
            for wp in (400, 650, 1000):
                lo, hi = 0.0, 80.0
                for _ in range(40):
                    mid = 0.5 * (lo + hi)
                    if meets(d, pack, res4, mid, wp, wv, n_p)[0]: lo = mid
                    else: hi = mid
                o.append("   %-26s %-10s %9d %14.2f" % (lab, wn, wp, lo))
    o.append("")
    o.append("7. THE CANDIDATE AND ITS MARGINS (4S15P and 4S16P at 42.8 W): lowest usable energy left over the 72 hours")
    for n_p in (15, 16, 18):
        for wv, wn in ((200.0, "200 W"), (300.0, "300 W")):
            for wp in (400, 650, 800):
                for t_c in (15.0, 20.0):
                    ok, out = meets(d, pack, res4, 42.8, wp, wv, n_p, t_c)
                    low = min(sm["lowest"] for sm, _ in out)
                    stop = [sm["first_stop"] for sm, _ in out]
                    o.append("   4S%dP, window %-6s, %4d Wp, cells %+5.1f C: %s, lowest %7.1f Wh, first stop %s" % (
                        n_p, wn, wp, t_c, "MEETS" if ok else "NOT MET", low, stop))
    o.append("")
    o.append("8. THE 2.80 V LINE (a setting inside the cell's 2.65 V specification cut-off, section 6b), 42.8 W, +20 C")
    for wv, wn in ((200.0, "200 W"), (300.0, "300 W")):
        for wp in (400, 650):
            n_found = None
            for n_p in range(3, NP_MAX + 1):
                if all(EB.simulate(d, pack, prof, 42.8, wp, wv, res4["eta"], res4["pr"], st, 20.0, pack.age80,
                                   d["mission"]["hours"], "2v80", n_p)[1]["ok"] for st in (6, 18)):
                    n_found = n_p
                    break
            o.append("   window %-6s, %4d Wp: smallest n_p with the 2.80 V line %s" % (wn, wp, n_found))
    o.append("")
    o.append("END. No combination on this page is a demonstration: each is the record's model on the reference day.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
