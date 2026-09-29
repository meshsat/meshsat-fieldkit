#!/usr/bin/env python3
"""recheck_two_pack.py: an independent re-computation of energy_two_pack.py's design case (stream a1elec, MESHSAT-1357).

A second implementation written separately from energy_two_pack.py's sim(): it shares no function with it. From
energy_budget.py (imported unchanged) it takes only the inputs' readers (Pack's curve points, the scaled September
profile, the chain) and recomputes everything else in closed form: each store's usable energy from the curve points,
the lid's charge and discharge losses by the quadratic formula instead of bisection, the allocation by explicit
arithmetic. It then compares its lowest points, stop hours and unserved energy with the figures energy_two_pack.out
prints for the same cases, and exits 1 on any difference above 0.05 Wh or any differing stop hour.

Run from the repository root: python3 v2/docs/records/a1elec/checks/recheck_two_pack.py > v2/docs/records/a1elec/checks/recheck_two_pack.out
AI arithmetic; a check of the model's arithmetic, not of its assumptions."""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "energy"))
import yaml  # noqa: E402
import energy_budget as EB  # noqa: E402

LOAD = 42.8


def lin(points, x):
    if x <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return points[-1][1]


def store(d, p_share, n_p, t_c):
    """Usable Wh at constant power p_share, 3.00 V line, aged 80 percent; the cell current found by the same fixed
    point energy_budget describes (three passes from 3.60 V)."""
    pk = d["pack"]
    v = 4 * 3.60
    for _ in range(3):
        i = p_share / v / n_p
        v = 4 * lin(pk["mean_v_points"]["points"], i)
    f_dod = min(lin(pk["end_of_discharge"]["fraction_at_3v00"]["points"], i), 1.0 - pk["end_of_discharge"]["graceful"]["rsoc_reserve"])
    wh = (4 * n_p * pk["capacity_min_ah"]["value"] * lin(pk["rate_factor"]["points"], i) * lin(pk["temperature_factor"]["points"], t_c)
          * lin(pk["mean_v_points"]["points"], i) * f_dod * pk["ageing"]["aged_80"]["factor"])
    return wh, 4 * lin(pk["mean_v_points"]["points"], i)


def run(d, prof, cap_node, wp, window, start, t_b, t_l, cfg):
    pr = d["solar"]["panel"]["performance_ratio"]["typ"]
    c = d["solar"]["chain"]
    e_b_full, v_b = store(d, LOAD * 6 / 18, 6, t_b)
    e_l_full, v_l = store(d, LOAD * 12 / 18, 12, t_l)
    tp = d["pack"]["charge"]["taper_from_soc"]
    ce = d["pack"]["charge"]["energy_efficiency"]["value"]
    e_b, e_l = e_b_full, e_l_full
    lo_b, lo_l, lo_t = e_b, e_l, e_b + e_l
    running, stop, short = True, None, 0.0
    for h in range(72):
        g = prof[(start + h) % 24]
        p_in = min(wp * g / 1000.0 * pr, window)
        p_fe = p_in * c[0]["eta"] * c[1]["eta"]
        if cap_node is not None:
            p_fe = min(p_fe, cap_node)
        sun = p_fe * c[2]["eta"]
        if not running and (sun >= LOAD or e_b + e_l >= 0.5 * (e_b_full + e_l_full)):
            running = True
        load = LOAD if running else 0.0
        if not running:
            short += max(0.0, LOAD - sun)
        if sun >= load:
            s = sun - load
            sb, sl = e_b / e_b_full, e_l / e_l_full
            cb = cfg["ib"] * v_b * (1.0 if sb < tp else max(0.0, (1 - sb) / (1 - tp)))
            ct = cfg["il"] * v_l * (1.0 if sl < tp else max(0.0, (1 - sl) / (1 - tp)))   # at the lid's terminals
            cl = (ct + (ct / v_l) ** 2 * cfg["rc"]) / cfg["eta"]                           # node power U3B draws for it
            cl = min(cl, cfg["iin"] * v_b)
            ab, al = min(s / 3.0, cb), min(2.0 * s / 3.0, cl)
            ab += min(s - ab - al, cb - ab)
            al += min(s - ab - al, cl - al)
            e_b = min(e_b_full, e_b + ab * ce)
            if al > 0:
                x = al * cfg["eta"]                     # t + (t/v)^2 r = x, solved for t
                r = cfg["rc"]
                t = x if r == 0 else (-1.0 + math.sqrt(1.0 + 4.0 * r * x / v_l ** 2)) * v_l ** 2 / (2.0 * r)
                e_l = min(e_l_full, e_l + t * ce)
        else:
            dfc = load - sun
            r, vak = cfg["rd"], cfg["vak"]
            # the most the lid can put on the node from e_l: p + p vak / v + p^2 r / v^2 = e_l
            a2, a1 = r / v_l ** 2, 1.0 + vak / v_l
            av_l = (-a1 + math.sqrt(a1 * a1 + 4 * a2 * e_l)) / (2 * a2) if e_l > 0 else 0.0
            if e_b > 0 and av_l > 0:
                db, dl = min(dfc / 3.0, e_b), min(2.0 * dfc / 3.0, av_l)
            else:
                db, dl = min(dfc, e_b), 0.0
            rest = dfc - db - dl
            x = min(rest, e_b - db); db += x; rest -= x
            x = min(rest, av_l - dl); dl += x; rest -= x
            if rest > 1e-9:
                short += rest
                e_b = e_l = 0.0
                running = False
                stop = h if stop is None else stop
            else:
                e_b -= db
                e_l = max(0.0, e_l - (dl + dl / v_l * vak + (dl / v_l) ** 2 * r))
        lo_b, lo_l, lo_t = min(lo_b, e_b), min(lo_l, e_l), min(lo_t, e_b + e_l)
    return {"stop": stop, "lo_b": lo_b, "lo_l": lo_l, "lo_t": lo_t, "short": short}


def main():
    d = yaml.safe_load(open(os.path.join(ROOT, "v2", "docs", "records", "energy", "energy_inputs.yaml"), encoding="utf-8"))
    monthly = json.load(open(os.path.join(ROOT, d["pinned"][0]["path"]), encoding="utf-8"))
    prof = EB.profile(d, monthly, 9)[0]
    cfg = {"ib": 4.0, "il": 8.0, "iin": 8.0, "eta": 0.975, "rc": 0.028, "rd": 0.030, "vak": 0.020}
    # (case, node cap in W at the front end's output or None, lid temperature, the .out's figures: stops, lowest base,
    #  lowest lid, lowest both, unserved), read from energy_two_pack.out sections 3a, 3f and 5
    cases = [
        ("E2, lid 13.23 C", None, 13.23, 20.0, [None, None], 30.3, 0.7, 31.1, 0.0),
        ("E2, lid 20.00 C", None, 20.0, 20.0, [None, None], 30.3, 58.7, 89.0, 0.0),
        ("E2, lid 7.50 C", None, 7.5, 20.0, [24, 36], 0.0, 0.0, 0.0, 35.5),
        ("E2, base 15 C, lid 13.23 C", None, 13.23, 15.0, [None, None], 8.9, 0.7, 9.7, 0.0),
        ("E1 (U3 in at 5.40 A x 20.7 V), lid 13.23 C", 5.40 * 20.7, 13.23, 20.0, [48, 59], 0.0, 0.0, 0.0, 35.8),
    ]
    bad = 0
    print("RE-CHECK OF energy_two_pack.py (independent closed-form implementation; 400 Wp, 200 W window, both starts)")
    for name, cap, t_l, t_b, stops, lb, ll, lt, sh in cases:
        rs = [run(d, prof, cap, 400, 200.0, st, t_b, t_l, cfg) for st in (6, 18)]
        got = ([r["stop"] for r in rs], round(min(r["lo_b"] for r in rs), 1), round(min(r["lo_l"] for r in rs), 1),
               round(min(r["lo_t"] for r in rs), 1), round(max(r["short"] for r in rs), 1))
        want = (stops, lb, ll, lt, sh)
        ok = got[0] == want[0] and all(abs(a - b) <= 0.05 + 1e-9 for a, b in zip(got[1:], want[1:]))
        bad += 0 if ok else 1
        print("  %-44s recomputed stops %-12s base %6.1f lid %6.1f both %6.1f unserved %6.1f   .out %s   %s" % (
            name, got[0], got[1], got[2], got[3], got[4], want, "AGREES" if ok else "DIFFERS"))
    r_l = 4 * 0.035 / 12 + 0.030
    r_b = 4 * 0.035 / 6 + 0.0025 + 0.002 + 2 * 0.00069 + 0.002 + 0.003 + 0.005
    i02 = 0.20 / (r_l + r_b)
    ok = abs(i02 - 2.47) <= 0.005
    bad += 0 if ok else 1
    print("  join current at 0.20 V: %.2f A (.out 8: 2.47 A)   %s" % (i02, "AGREES" if ok else "DIFFERS"))
    print("RESULT: %s" % ("every figure agrees" if bad == 0 else "%d DIFFER" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
