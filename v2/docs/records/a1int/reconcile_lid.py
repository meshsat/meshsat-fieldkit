#!/usr/bin/env python3
"""Option A(i): the electrical model re-run for the lid packs the mechanical package found will fit (MESHSAT-1357, 29 September
2026, the coordinator's reconciliation of streams a1elec and a1mech). a1elec's energy_two_pack.py was written for a 4S12P lid;
a1mech found 35 lid cells (4S8P) with both owner-approved lid functions kept (HF 16a, tablet 16d), 56 with the tablet out (B)
and 58 with the QMX out (C), so 4S14P in either. This script imports energy_two_pack.py unchanged (it pins energy_budget.py
itself), changes only its lid parallel count and, with it, the lid's charge current at the model's own capacity-proportional
value per string (its lid charge current over its 12 strings, printed below), and runs its own design case (400 Wp, 200 W stage, entry
E2 re-rated, the base at +20 C, the lid at the September mean day's minimum air and swept) with its own functions. It prints,
per lid size, the result, each pack's lowest point and the lowest lid temperature that still meets M1. A reference-day model
result, not a demonstration. Run from the repository root: python3 v2/docs/records/a1int/reconcile_lid.py"""
import os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "a1elec"))
import energy_two_pack as TP

PER_CELL = TP.v("chg_a_lid") / TP.NP_L          # the model's own allocation, per lid string


def case(n_lid, t_l):
    TP.NP_L = n_lid; TP.NP_T = TP.NP_B + n_lid
    d, pack, res4, t2m = TP.load_model()
    prof = res4["months"][TP.MONTH]["profile"]
    cfg = TP.base_cfg(); cfg["chg_a_l"] = PER_CELL * n_lid
    rs = TP.both(d, pack, res4, prof, 400.0, 200.0, TP.v("t_base_c"), t_l, cfg)
    return rs, t2m


def main():
    n0 = TP.NP_L
    _, t2m = case(n0, 20.0)
    tmin = round(min(t2m), 2)
    out = ["OPTION A(i), THE LID SIZES THAT FIT (reconcile_lid.py). Model: a1elec's energy_two_pack.py, unchanged but for the lid's",
           "parallel count and its charge current at %.4f A a string. Design case: 400 Wp, 200 W stage, entry E2, base at +%.0f C," % (PER_CELL, TP.v("t_base_c")),
           "lid at %.2f C (the September mean day's minimum air), both start hours, 42.8 W, aged 80 percent." % tmin, ""]
    for n, what in ((8, "4S8P lid: both owner-approved lid functions kept (a1mech: 35 places), 4S14P in all"),
                    (12, "4S12P lid: a1elec's assumption, 4S18P in all"),
                    (14, "4S14P lid: the tablet out of the lid (B, 56 places), 4S20P in all"),
                    (15, "4S15P lid: the QMX out of the lid (C, 61 places after the mechanical check), 4S21P in all")):
        rs, _ = case(n, tmin)
        out.append("%s" % what)
        out.append("   at %.2f C: %s" % (tmin, TP.fmt_run(rs)))
        lo, hi = -10.0, 40.0
        if not TP.verdict(case(n, hi)[0]):
            out.append("   does not meet M1 even with the lid at +40 C")
        else:
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                if TP.verdict(case(n, mid)[0]): hi = mid
                else: lo = mid
            out.append("   lowest lid temperature that still meets M1: %+.1f C" % hi)
        out.append("")
    out.append("4S9P lid: both functions kept with P2 allowed under the tablet (the independent check of a1mech found 39 places),")
    out.append("4S15P in all, at the arrays beyond A(i)'s 400 Wp too, with the lid at its basis and at the base's +20 C:")
    for wp in (400.0, 650.0, 1000.0):
        for tl in (tmin, 20.0):
            TP.NP_L = 9; TP.NP_T = TP.NP_B + 9
            d, pack, res4, _ = TP.load_model(); prof = res4["months"][TP.MONTH]["profile"]
            cfg = TP.base_cfg(); cfg["chg_a_l"] = PER_CELL * 9
            rs = TP.both(d, pack, res4, prof, wp, 200.0, TP.v("t_base_c"), tl, cfg)
            out.append("   %4d Wp, lid %.2f C: %s" % (wp, tl, TP.fmt_run(rs)))
    out.append("")
    TP.NP_L = n0; TP.NP_T = TP.NP_B + n0
    out.append("END. Each line is the model's arithmetic on the September reference day; nothing is measured.")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
