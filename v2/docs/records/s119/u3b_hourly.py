#!/usr/bin/env python3
"""u3b_hourly.py: U3B's efficiency over the energy model's own hours (stream s119, S-119, MESHSAT-1357, 29 September 2026;
the second round, answering item M1 of the stream's independent check).

PROTOTYPE DESIGN, AI arithmetic on the makers' figures: nothing is built or measured.

The first round carried U3B at its worst mode at the model's PEAK hour (55.3 W from VBAT), U3B's most favourable load.
This script takes U3B's efficiency hour by hour instead: TI's SLUSE66A Equations 6 to 22 (printed pages 86 to 88), as
records/s117/efficiency.py implements them (imported, pinned by sha256; its stage() and eta() only), on U3B as the S-119
decision draws it (the 400 kHz row: L2B XAL1010-472ME, R16B 10 mOhm, R17B 5 mOhm, Q7B and Q9B CSD17578Q5A, Q8B and Q10B
CSD17577Q5A), in the buck-boost bound (all four FETs switching, the worst of the three modes at every load, since the lid
sits beside VBAT on this model), at VIN = the model's node voltage and VOUT = its lid voltage, for three readings (the
makers' maxima, TI's, the most favourable). It then runs a1elec's energy_two_pack.py (pinned) with that efficiency as a
function of U3B's input power in each hour, for both lid options that fit (4S14P, 4S15P), both ratio cases (B typical,
C adverse, read from records/a1solar/energy_runs.out), U3 at its 6.1 A minimum and both start hours, and weights each
hour's efficiency by the energy U3B takes in that hour. The carried figure is the lowest weighted figure over those
cases, rounded down to three places; its bracket is the lowest weighted figure at the makers' maxima and the highest at
the most favourable reading. The way (a) row (800 kHz, CSD17578Q5A x 4) is printed beside it for comparison with the
check's own figures. The inductor's core loss and light-load PFM are excluded, as in efficiency.py: every figure is high
by the first and low by the second at the lightest hours.

Run from the repository root: python3 v2/docs/records/s119/u3b_hourly.py > v2/docs/records/s119/u3b_hourly.out"""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
RECS = os.path.join(TOP, "v2", "docs", "records")
PINS = {"s117/efficiency.py": "PIN_EFF", "a1elec/energy_two_pack.py": "PIN_TP"}
PIN_EFF = "c24d5cfe209be3db7437c39c6762ef4257dd881d561cba047284aa7cc08b5809"
PIN_TP = "a3426880bf607d38b08449ec0a880f10a064ee2767324afad2c250cd5a9444f4"
for rel, name in PINS.items():
    if hashlib.sha256(open(os.path.join(RECS, rel), "rb").read()).hexdigest() != globals()[name]:
        sys.stderr.write("u3b_hourly: %s is not the pinned file; refusing\n" % rel)
        sys.exit(2)
sys.path.insert(0, os.path.join(RECS, "s117"))
sys.path.insert(0, os.path.join(RECS, "a1elec"))
import efficiency as EF  # noqa: E402
import energy_two_pack as TP  # noqa: E402

RUNS = "v2/docs/records/a1solar/energy_runs.out"
READS = (("lower", "the makers' maxima"), ("TI", "TI's reading"), ("upper", "the most favourable"))
ROWS = {"400": (EF.U3B_400_SET, EF.U3B_400, "the 400 kHz row (the S-119 decision)"),
        "800": (EF.U3B_800_SET, EF.U3B_DRAFT, "way (a), 800 kHz, CSD17578Q5A x 4 (not drawn)")}
STEP = 0.25


def ratios():
    text = open(os.path.join(TOP, RUNS), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + RUNS], capture_output=True, text=True).stdout
    if text != head:
        sys.stderr.write("u3b_hourly: %s differs from HEAD's; refusing\n" % RUNS)
        sys.exit(3)
    sec = text.split("2. THE PERFORMANCE RATIOS RUN", 1)[1].split("\n3. ", 1)[0]
    got = {}
    for line in sec.split("\n"):
        m = re.match(r"\s+([ABC])\s+(.*?)\s+(0\.\d{4})\s*$", line)
        if m:
            got[m.group(1)] = float(m.group(3))
    if set(got) != {"A", "B", "C"}:
        sys.exit(3)
    return got


class Curve:
    """U3B's efficiency against its input power from VBAT, tabulated every STEP W from TI's equations, linear between."""

    def __init__(self, row, v_b, v_l, reading):
        fets, r, _ = ROWS[row]
        self.tab = [0.0]
        p = STEP
        while p <= 200.0 + 1e-9:
            e = 0.97
            for _ in range(3):   # the charge current through R17B follows the output
                e = EF.eta("bb", v_b, p / v_b, v_l, p * e / v_l, fets, r["ind"], r["f"], r["r_in"], r["r_chg"], reading)
            self.tab.append(max(0.0, e))
            p += STEP

    def __call__(self, p):
        if p <= 0.0:
            return self.tab[1]
        k = min(int(p / STEP), len(self.tab) - 2)
        f = p / STEP - k
        return self.tab[k] + (self.tab[k + 1] - self.tab[k]) * f


def run(n, pr, eb, start, trace):
    TP.NP_L = n
    TP.NP_T = TP.NP_B + n
    d, pack, res4, t2m = TP.load_model()
    r = dict(res4)
    r["pr"] = pr
    TP.ENTRIES["_u3"] = {"fe_out_w": TP.ENTRIES["E2"]["fe_out_w"], "u3_in_w": 6.1 * TP.V_BUS20, "what": ""}
    cfg = TP.base_cfg()
    cfg["entry"] = "_u3"
    cfg["eta_b"] = eb
    return TP.sim(d, pack, r, res4["months"][TP.MONTH]["profile"], 400.0, 200.0, start, TP.v("t_base_c"), round(min(t2m), 2), cfg, trace=trace)


def main():
    rat = ratios()
    n0 = TP.NP_L
    o = []
    P = o.append
    P("U3B'S EFFICIENCY OVER THE MODEL'S OWN HOURS (u3b_hourly.py, stream s119, S-119, second round). AI arithmetic on the")
    P("makers' figures (SLUSE66A Equations 6 to 22 via records/s117/efficiency.py); nothing built or measured; core loss and")
    P("light-load PFM excluded. Buck-boost bound at every hour; VIN the model's node voltage, VOUT its lid voltage. The")
    P("weighting takes every hour; at the lightest (under 5 W, the taper's tail) fixed losses dominate and the equations read")
    P("low, down to 0 where they exceed the input, which PFM would soften; those hours carry little energy (printed).")
    P("")
    res = {}
    for row in ("400", "800"):
        P("%s" % ROWS[row][2])
        for n in (14, 15):
            probe = run(n, rat["B"], 0.97, 6, None)
            v_b, v_l = probe["v_b"], probe["v_l"]
            curves = {rd: Curve(row, v_b, v_l, rd) for rd, _ in READS}
            if row == "400" and n == 14:
                P("   the curve at 4S%dP's node %.2f V and lid %.2f V (input W: lower / TI / upper):" % (n, v_b, v_l))
                for p in (2.0, 5.0, 10.0, 20.0, 30.0, 40.0, 55.0, 60.0, 80.0):
                    P("      %5.1f W: %s" % (p, " / ".join("%.3f" % curves[rd](p) for rd, _ in READS)))
            for k in "BC":
                for start in (6, 18):
                    tr = []
                    rs = run(n, rat[k], curves["TI"], start, tr)
                    hours = [(x[5]) for x in tr if x[5] > 0.0]
                    ein = sum(hours)
                    w = {rd: sum(p * curves[rd](p) for p in hours) / ein for rd, _ in READS}
                    big = [p for p in hours if p >= 5.0]
                    small = [p for p in hours if p < 5.0]
                    worst = min(curves["TI"](p) for p in big)
                    res[(row, n, k, start)] = (w, worst, ein, max(hours), rs["ok"])
                    P("   4S%dP, ratio %s, start %02d UTC: %d hours, %.0f Wh into U3B over 72 h, peak %.1f W; weighted %s; worst hour of 5 W or more %.3f (TI); %d hours under 5 W carry %.1f Wh" % (
                        n, k, start, len(hours), ein, max(hours), " / ".join("%.4f" % w[rd] for rd, _ in READS), worst, len(small), sum(small)))
        P("")
    ti = [v[0]["TI"] for kk, v in res.items() if kk[0] == "400"]
    lo = [v[0]["lower"] for kk, v in res.items() if kk[0] == "400"]
    hi = [v[0]["upper"] for kk, v in res.items() if kk[0] == "400"]
    floor3 = lambda x: int(x * 1000.0 + 1e-9) / 1000.0
    P("THE FIGURE CARRIED (the 400 kHz row): the lowest weighted TI figure over the eight cases, rounded down, %.3f (range" % floor3(min(ti)))
    P("%.4f to %.4f); bracket %.3f (the lowest at the makers' maxima) to %.3f (the highest at the most favourable reading)." % (
        min(ti), max(ti), floor3(min(lo)), floor3(max(hi))))
    ti8 = [v[0]["TI"] for kk, v in res.items() if kk[0] == "800"]
    P("Way (a) at 800 kHz on the same hours, for comparison: %.4f to %.4f; worst hour of 5 W or more %.3f." % (
        min(ti8), max(ti8), min(v[1] for kk, v in res.items() if kk[0] == "800")))
    P("The peak-hour figures of efficiency.out section 7 (0.974 at 400 kHz, 0.961 at 800 kHz) sit above these: the peak is")
    P("U3B's most favourable load, and its light hours cost more in proportion.")
    P("END.")
    TP.NP_L = n0
    TP.NP_T = TP.NP_B + n0
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
