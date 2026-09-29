#!/usr/bin/env python3
"""Option A(i): the lid options of reconcile_lid.py re-run with the chosen array's performance ratios (MESHSAT-1357,
29 September 2026, the coordinator's reconciliation after stream a1solar; second issue after its independent check,
`checks/check-a1int-1.md`). reconcile_lid.py ran the two-pack model at the pinned ratio 0.9417 (PVGIS's, a panel held at its
maximum-power point). Stream a1solar chose four Renogy RNG-100DB-H in 2S2P at a fixed input point and computed the ratios B
(typical) and C (everything adverse at once) on the 40 degree south plane; this script reads them from the committed
`records/a1solar/energy_runs.out` (section 2, never typed here, the file asserted equal to HEAD's) and runs each lid option
(4S9P both functions kept, 4S14P tablet out, 4S15P QMX out) on a1elec's energy_two_pack.py (pinned by sha256), changing only
the lid's parallel count and the ratio.

Second issue (the check's B1 and M3, M7): U3's input limit is taken at its minimum as CHARGER.md's rule asks. SLUSE66A prints
no accuracy row for the 10 mOhm sense resistor; its 5 mOhm rows are +-200 mA about the code (8.5, page 10) and 9.6.22 (page
80) adds 100 mA for the maximum at 10 mOhm, so the minimum is read as 6.1 A, with 6.0 A (the printed 5 mOhm spread) as the
bracket; entry E2's 6.2 A is the nominal. U3B's charge current stays at its recorded code 62, 7.936 A, for every lid (the
first issue scaled it per string, above the gauge's 8.0 A and, at 4S15P with +3 percent, OCC1's 10.0 A; the entry, not the
setting, sets the lid current, so no figure moved). It prints the verdict and lowest points at the September lid basis and
the lowest lid temperature that still meets M1. Model results on the reference day at the 40 degree south plane; nothing
is measured. Run from the repository root: python3 v2/docs/records/a1int/reconcile_lid_panel.py"""
import hashlib, os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TPDIR = os.path.join(HERE, "..", "a1elec")
TP_SHA = "81694b2bfc5dfef10c7f2895cd5fc4bae3682cc764e9d1c969757387c393f027"   # energy_two_pack.py, the pin energy_runs.py carries
if hashlib.sha256(open(os.path.join(TPDIR, "energy_two_pack.py"), "rb").read()).hexdigest() != TP_SHA:
    sys.stderr.write("reconcile_lid_panel: energy_two_pack.py is not the pinned file; refusing\n"); sys.exit(2)
sys.path.insert(0, TPDIR)
import energy_two_pack as TP

OUT = "v2/docs/records/a1solar/energy_runs.out"
U3 = (("nominal", TP.v("u3_iin_draft_a")), ("minimum", 6.1), ("bracket", 6.0))


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


def run(n_lid, t_l, pr, u3_a):
    TP.NP_L = n_lid; TP.NP_T = TP.NP_B + n_lid
    d, pack, res4, t2m = TP.load_model()
    prof = res4["months"][TP.MONTH]["profile"]
    r = dict(res4); r["pr"] = pr
    TP.ENTRIES["_u3"] = {"fe_out_w": TP.ENTRIES["E2"]["fe_out_w"], "u3_in_w": u3_a * TP.V_BUS20, "what": ""}
    cfg = TP.base_cfg(); cfg["entry"] = "_u3"          # chg_a_l stays at U3B's code 62, 7.936 A
    return TP.both(d, pack, r, prof, 400.0, 200.0, TP.v("t_base_c"), t_l, cfg), t2m


def tmin_meets(n, pr, u3_a):
    if not TP.verdict(run(n, 40.0, pr, u3_a)[0]):
        return None
    lo, hi = -10.0, 40.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if TP.verdict(run(n, mid, pr, u3_a)[0]): hi = mid
        else: lo = mid
    return hi


def main():
    n0 = TP.NP_L
    rat = ratios()
    _, t2m = run(n0, 20.0, rat["A"][1], U3[0][1])
    tmin = round(min(t2m), 2)
    out = ["OPTION A(i), THE LID OPTIONS WITH THE CHOSEN ARRAY'S RATIOS (reconcile_lid_panel.py, second issue). Model: a1elec's",
           "energy_two_pack.py (pinned), unchanged but for the lid's parallel count, the ratio and U3's input limit; U3B's charge",
           "current at code 62, %.3f A, for every lid; 400 Wp, 200 W stage, front end R11 6.2 mOhm (entry E2), base at +%.0f C," % (TP.v("chg_a_lid"), TP.v("t_base_c")),
           "lid at %.2f C (the September mean day's minimum air), both start hours, 42.8 W, aged 80 percent; the 40 degree south plane." % tmin,
           "U3's IIN_HOST: %s." % "; ".join("%s %.1f A" % (k, a) for k, a in U3),
           "Ratios read from %s section 2:" % OUT]
    for k in "ABC":
        out.append("   %s  %-55s %.4f" % (k, rat[k][0], rat[k][1]))
    out.append("")
    for n, what in ((9, "4S9P lid: both owner-approved lid functions kept (39 places), 4S15P in all"),
                    (14, "4S14P lid: the tablet out of the lid (B), 4S20P in all"),
                    (15, "4S15P lid: the QMX out of the lid (C), 4S21P in all")):
        out.append(what)
        for k in "ABC":
            for uk, ua in U3:
                if k == "A" and uk != "nominal": continue
                rs, _ = run(n, tmin, rat[k][1], ua)
                t = tmin_meets(n, rat[k][1], ua)
                out.append("   %s, U3 %-7s %.1f A, at %.2f C: %s" % (k, uk, ua, tmin, TP.fmt_run(rs)))
                out.append("      %s" % ("does not meet M1 even with the lid at +40 C" if t is None else "lowest lid temperature that still meets M1: %+.1f C" % t))
        out.append("")
    TP.NP_L = n0; TP.NP_T = TP.NP_B + n0
    out += ["NOTES (the independent check's minor items): the model evaluates the charge taper once an hour; a 0.01 h step lowers",
            "the lowest stores by about 0.8 Wh (B) and 2.4 Wh (C) and moves the lid thresholds by -0.1 to +0.2 K (at 0.1 h the 4S14P C",
            "threshold at the minimum U3 reads about +4.6 C: it is not stable to better than about 1.5 K). Node power offered to a full",
            "store is discarded at the clamp after U3B's loss is charged on it (23 to 58 Wh over 72 h); no energy is created and no",
            "lowest point moves. The lid path's standby drain and board PL's own supply (about 1.5 to 1.8 Wh over 72 h) are outside",
            "the 42.8 W. The results hold on the 40 degree south plane only.",
            "END. Each line is the model's arithmetic on the September reference day; nothing is measured."]
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
