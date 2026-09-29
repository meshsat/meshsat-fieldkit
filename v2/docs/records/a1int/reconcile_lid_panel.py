#!/usr/bin/env python3
"""Option A(i): the lid options of reconcile_lid.py re-run with the chosen array's performance ratios (MESHSAT-1357,
29 September 2026, the coordinator's reconciliation after stream a1solar). reconcile_lid.py ran the two-pack model at the
pinned ratio 0.9417 (PVGIS's, a panel held at its maximum-power point). Stream a1solar chose four Renogy RNG-100DB-H in
2S2P at a fixed input point and computed the ratios B (typical) and C (everything adverse at once) on the 40 degree south
plane; this script reads them from the committed `records/a1solar/energy_runs.out` (section 2, never typed here, the file
asserted equal to HEAD's), and runs each lid option (4S9P both functions kept, 4S14P tablet out, 4S15P QMX out) with
reconcile_lid.py's own method: a1elec's energy_two_pack.py unchanged but for the lid's parallel count, its charge current
per string, and the ratio. It prints the verdict and lowest points at the September lid basis and the lowest lid
temperature that still meets M1. Model results on the reference day at the 40 degree south plane (the deployment rule of
records/a1solar/ARRAY.md 7 is where they hold); nothing is measured. Run from the repository root:
python3 v2/docs/records/a1int/reconcile_lid_panel.py"""
import os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(HERE, "..", "a1elec"))
import energy_two_pack as TP

OUT = "v2/docs/records/a1solar/energy_runs.out"
PER_CELL = TP.v("chg_a_lid") / TP.NP_L


def ratios():
    text = open(os.path.join(TOP, OUT), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + OUT], capture_output=True, text=True).stdout
    if text != head:
        sys.stderr.write("reconcile_lid_panel: %s differs from HEAD's; refusing\n" % OUT); sys.exit(3)
    sec = text.split("2. THE PERFORMANCE RATIOS RUN", 1)[1].split("\n3. ", 1)[0]
    got = {}
    for line in sec.split("\n"):
        m = re.match(r"\s+([ABC])\s+(.*?)\s+(0\.\d{4})\s*$", line)
        if m: got[m.group(1)] = (m.group(2), float(m.group(3)))
    if set(got) != {"A", "B", "C"}:
        sys.stderr.write("reconcile_lid_panel: ratios A, B, C not all found in %s; refusing\n" % OUT); sys.exit(3)
    return got


def run(n_lid, t_l, pr):
    TP.NP_L = n_lid; TP.NP_T = TP.NP_B + n_lid
    d, pack, res4, t2m = TP.load_model()
    prof = res4["months"][TP.MONTH]["profile"]
    r = dict(res4); r["pr"] = pr
    cfg = TP.base_cfg(); cfg["chg_a_l"] = PER_CELL * n_lid
    return TP.both(d, pack, r, prof, 400.0, 200.0, TP.v("t_base_c"), t_l, cfg), t2m


def main():
    n0 = TP.NP_L
    rat = ratios()
    _, t2m = run(n0, 20.0, rat["A"][1])
    tmin = round(min(t2m), 2)
    out = ["OPTION A(i), THE LID OPTIONS WITH THE CHOSEN ARRAY'S RATIOS (reconcile_lid_panel.py). Model: a1elec's energy_two_pack.py,",
           "unchanged but for the lid's parallel count, its charge current (%.4f A a string) and the ratio; 400 Wp, 200 W stage, entry E2," % PER_CELL,
           "base at +%.0f C, lid at %.2f C (the September mean day's minimum air), both start hours, 42.8 W, aged 80 percent; the" % (TP.v("t_base_c"), tmin),
           "40 degree south plane. Ratios read from %s section 2:" % OUT]
    for k in "ABC":
        out.append("   %s  %-55s %.4f" % (k, rat[k][0], rat[k][1]))
    out.append("")
    for n, what in ((9, "4S9P lid: both owner-approved lid functions kept (39 places), 4S15P in all"),
                    (14, "4S14P lid: the tablet out of the lid (B), 4S20P in all"),
                    (15, "4S15P lid: the QMX out of the lid (C), 4S21P in all")):
        out.append(what)
        for k in "ABC":
            pr = rat[k][1]
            rs, _ = run(n, tmin, pr)
            line = "   %s at %.2f C: %s" % (k, tmin, TP.fmt_run(rs))
            if not TP.verdict(run(n, 40.0, pr)[0]):
                line += "\n      does not meet M1 even with the lid at +40 C"
            else:
                lo, hi = -10.0, 40.0
                for _ in range(30):
                    mid = 0.5 * (lo + hi)
                    if TP.verdict(run(n, mid, pr)[0]): hi = mid
                    else: lo = mid
                line += "\n      lowest lid temperature that still meets M1: %+.1f C" % hi
            out.append(line)
        out.append("")
    TP.NP_L = n0; TP.NP_T = TP.NP_B + n0
    out.append("END. Each line is the model's arithmetic on the September reference day; nothing is measured.")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
