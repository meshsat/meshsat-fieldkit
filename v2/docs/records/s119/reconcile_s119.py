#!/usr/bin/env python3
"""reconcile_s119.py: Option A(i)'s lid reconciliation on the restated charger rows, with the change from the accepted
figures, U3B hour by hour, the failing case, the sensitivity, the room for the excluded core loss and the planes (stream
s119, S-119, MESHSAT-1357, 29 September 2026; second round after the stream's independent check, items M1, M2 and M4).

PROTOTYPE DESIGN, AI arithmetic: nothing is built, ordered or measured, and nothing printed is a measurement.

What it does. It imports a1elec's energy_two_pack.py (second issue, pinned by sha256) exactly as
records/a1int/reconcile_lid_panel.py (third issue) does and runs the same cases: the lid's parallel count (4S9P both lid
functions kept, 4S14P the tablet out, 4S15P the QMX out), the chosen array's ratios read from
records/a1solar/energy_runs.out section 2 (A, B typical, C adverse), and U3's input limit at its nominal 6.2 A, its
minimum 6.1 A and the 6.0 A bracket. Then:
  1. it proves that its own central rows are byte-identical to the committed reconcile_lid_panel.out (exit 5 otherwise);
  2. it reads the accepted figures (reconcile_lid_panel.out's second issue, from git history) and prints the change;
  3. U3B HOUR BY HOUR: the same cases with U3B's efficiency a function of its input power in each hour (the curve of
     u3b_hourly.py, TI's equations on the 400 kHz row, buck-boost bound), at TI's reading and at both ends, beside the
     carried figure, and the 800 kHz way (a) the same way for comparison;
  4. the failing case: U3 and U3B at the figures of the FETs as first drawn and drafted (CSD18510Q5B), which must read
     NOT MET for both lid options in both ratio cases (exit 6 otherwise: the instrument would not discriminate);
  5. the sensitivity grid of U3 and U3B over their brackets;
  6. the room for the excluded core loss: the lowest efficiency each charger may fall to at every hour, and, hour by
     hour, the largest constant loss in watts each charger may add in every hour it runs (U3B on its hourly curve);
     the least current into U3;
  7. the deployment rule's planes (20 to 50 degrees, within 15 degrees of south, and flat) for the two lid options, with
     energy_runs.py's own plane machinery imported (pinned), U3B hour by hour;
  8. U3B's largest input current over every run, against its 6.2 A limit and the 6.35 A clamp.
Every charger figure is PARSED from records/s117/efficiency.out section 7 or records/s119/u3b_hourly.out (none is typed
here) and checked against the rows the model carries (energy_inputs.yaml's U3 row and energy_two_pack.py's eta_u3b).

Run from the repository root:  python3 v2/docs/records/s119/reconcile_s119.py > v2/docs/records/s119/reconcile_s119.out
Deterministic. Exit 2: a pinned script is not the pinned file; 3: an input differs from HEAD or cannot be parsed; 5: the
central rows do not reproduce reconcile_lid_panel.out; 6: the failing case reads MEETS somewhere."""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
RECS = os.path.join(TOP, "v2", "docs", "records")
PINS = {"a1elec/energy_two_pack.py": "a3426880bf607d38b08449ec0a880f10a064ee2767324afad2c250cd5a9444f4",
        "a1solar/energy_runs.py": "d0fd1949efce71868a143c57cd9e5a2db516daec774db1085541d1a5a920ffcb",
        "s119/u3b_hourly.py": "4b435e4f0e272050733541bfe1f985eed5e681daa6818ee57b914dcbb6211892"}
for _rel, _want in PINS.items():
    if hashlib.sha256(open(os.path.join(RECS, _rel), "rb").read()).hexdigest() != _want:
        sys.stderr.write("reconcile_s119: %s is not the pinned file; refusing\n" % _rel)
        sys.exit(2)
sys.path.insert(0, os.path.join(RECS, "a1elec"))
sys.path.insert(0, os.path.join(RECS, "a1solar"))
sys.path.insert(0, HERE)
import energy_two_pack as TP  # noqa: E402
import energy_runs as ER  # noqa: E402
import u3b_hourly as UH  # noqa: E402

RUNS = "v2/docs/records/a1solar/energy_runs.out"
PANEL = "v2/docs/records/a1int/reconcile_lid_panel.out"
EFF = "v2/docs/records/s117/efficiency.out"
UHO = "v2/docs/records/s119/u3b_hourly.out"
U3_LIMITS = (("nominal", TP.v("u3_iin_draft_a")), ("minimum", 6.1), ("bracket", 6.0))
LIDS = ((9, "4S9P lid: both owner-approved lid functions kept (39 places), 4S15P in all"),
        (14, "4S14P lid: the tablet out of the lid (B), 4S20P in all"),
        (15, "4S15P lid: the QMX out of the lid (C), 4S21P in all"))
TMIN = None
CURVES = {}
PEAK_U3B_A = [0.0, ""]


def head_equal(rel):
    text = open(os.path.join(TOP, rel), encoding="utf-8").read()
    head = subprocess.run(["git", "-C", TOP, "show", "HEAD:" + rel], capture_output=True, text=True).stdout
    if text != head:
        sys.stderr.write("reconcile_s119: %s differs from HEAD's; refusing\n" % rel)
        sys.exit(3)
    return text


def ratios():
    sec = head_equal(RUNS).split("2. THE PERFORMANCE RATIOS RUN", 1)[1].split("\n3. ", 1)[0]
    got = {}
    for line in sec.split("\n"):
        m = re.match(r"\s+([ABC])\s+(.*?)\s+(0\.\d{4})\s*$", line)
        if m:
            got[m.group(1)] = (m.group(2), float(m.group(3)))
    if set(got) != {"A", "B", "C"}:
        sys.stderr.write("reconcile_s119: ratios A, B, C not all found in %s\n" % RUNS)
        sys.exit(3)
    return got


def efficiency_rows():
    """Section 7 of efficiency.out: label to (lower, TI, upper), parsed from its table's fixed layout."""
    sec = head_equal(EFF).split("7. WHAT THE ENERGY MODEL SHOULD CARRY", 1)[1].split("\n8. ", 1)[0]
    rows = {}
    for line in sec.split("\n"):
        m = re.match(r"\s{3}(U3B?[ ,].*?)\s+(0\.\d{3})\s+(0\.\d{3})\s+(0\.\d{3})\s+(0\.\d{3})", line)
        if m:
            rows[m.group(1).strip()] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    need = {"U3, chosen FETs, day at E2", "U3, drawn FETs (S-117's row), day at E2", "U3B, drafted (800 kHz, CSD18510Q5B)",
            "U3B, CSD17578Q5A x 4, 800 kHz", "U3B, 78/77 pairs, 400 kHz row"}
    if not need <= set(rows):
        sys.stderr.write("reconcile_s119: efficiency.out section 7 lacks %s\n" % sorted(need - set(rows)))
        sys.exit(3)
    return rows


def hourly_row():
    """u3b_hourly.out's carried figure and bracket, parsed from its closing sentence."""
    text = " ".join(head_equal(UHO).split())
    m = re.search(r"rounded down, (0\.\d{3}) \(range (0\.\d{4}) to (0\.\d{4})\); bracket (0\.\d{3}) \(the lowest at the "
                  r"makers' maxima\) to (0\.\d{3})", text)
    if not m:
        sys.stderr.write("reconcile_s119: %s's carried figure not found\n" % UHO)
        sys.exit(3)
    return float(m.group(4)), float(m.group(1)), float(m.group(5))


def curve(n, reading, row="400"):
    """U3B's efficiency against its input power for lid option n (u3b_hourly.Curve at that option's node and lid voltage)."""
    key = (n, reading, row)
    if key not in CURVES:
        probe = run(n, 0.93, 6.1, eta_b=0.97)[0]
        CURVES[key] = UH.Curve(row, probe["v_b"], probe["v_l"], reading)
    return CURVES[key]


def run(n_lid, pr, u3_a, eta_u3=None, eta_b=None, t_l=None, prof=None, u3_loss=0.0):
    """One lid option, both starts, as reconcile_lid_panel.run() does; eta_u3 and eta_b override the carried rows (eta_b
    may be a function of U3B's input power); u3_loss adds a constant loss in watts to U3 in every hour it runs."""
    TP.NP_L = n_lid
    TP.NP_T = TP.NP_B + n_lid
    d, pack, res4, t2m = TP.load_model()
    if eta_u3 is not None:
        d["solar"]["chain"][2]["eta"] = eta_u3
    pf = res4["months"][TP.MONTH]["profile"] if prof is None else prof
    r = dict(res4)
    r["pr"] = pr
    TP.ENTRIES["_u3"] = {"fe_out_w": TP.ENTRIES["E2"]["fe_out_w"], "u3_in_w": u3_a * TP.V_BUS20, "what": ""}
    cfg = TP.base_cfg()
    cfg["entry"] = "_u3"
    if eta_b is not None:
        cfg["eta_b"] = eta_b
    orig = TP.node_power
    if u3_loss > 0.0:
        def lossy(d_, res_, g, wp, window, entry):
            p = orig(d_, res_, g, wp, window, entry)
            return max(0.0, p - u3_loss) if p > 0.0 else p
        TP.node_power = lossy
    try:
        return TP.both(d, pack, r, pf, 400.0, 200.0, TP.v("t_base_c"), TMIN if t_l is None else t_l, cfg)
    finally:
        TP.node_power = orig


def with_loss(cv, c):
    """U3B's hourly curve with a constant loss of c watts in every hour it runs."""
    return lambda p: max(0.0, cv(p) - c / p) if p > 0.0 else cv(p)


def tmin_meets(n, pr, u3_a, **kw):
    """reconcile_lid_panel.tmin_meets, the same bisection."""
    if not TP.verdict(run(n, pr, u3_a, t_l=40.0, **kw)):
        return None
    lo, hi = -10.0, 40.0
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if TP.verdict(run(n, pr, u3_a, t_l=mid, **kw)):
            hi = mid
        else:
            lo = mid
    return hi


def bisect_max(ok, lo, hi, n=30):
    """The largest x in [lo, hi] with ok(x) true, ok monotone falling; None if ok(lo) is false."""
    if not ok(lo):
        return None
    if ok(hi):
        return hi
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if ok(mid):
            lo = mid
        else:
            hi = mid
    return lo


def low_both(rs):
    return min(r["low_t"] for r in rs)


def cell(rs):
    return ("MEETS %6.1f" % low_both(rs)) if TP.verdict(rs) else "NOT MET"


def note_peak(rs, what):
    for r in rs:
        a = r["peak"]["a_l"] / r["v_b"]
        if a > PEAK_U3B_A[0]:
            PEAK_U3B_A[0], PEAK_U3B_A[1] = a, what


def accepted():
    """reconcile_lid_panel.out as its second issue printed it (the accepted figures), from git history."""
    log = subprocess.run(["git", "-C", TOP, "log", "--format=%H", "--", PANEL], capture_output=True, text=True, check=True).stdout.split()
    for c in log:
        text = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (c, PANEL)], capture_output=True, text=True).stdout
        if "(reconcile_lid_panel.py, second issue)" in text.split("\n", 1)[0]:
            return c, text
    sys.stderr.write("reconcile_s119: no second issue of %s in git history\n" % PANEL)
    sys.exit(3)


def parse_panel(text):
    """(lid, ratio, U3 case) to (verdict, base, lid, both, threshold or None) from a reconcile_lid_panel.out."""
    out, lid = {}, None
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"4S(\d+)P lid:", line)
        if m:
            lid = int(m.group(1))
            continue
        m = re.match(r"\s+([ABC]), U3 (\w+)\s+[\d.]+ A, at [\d.]+ C: (MEETS|NOT MET)\s.*?lowest base\s+([\d.]+) Wh.*?lid\s+([\d.]+) Wh.*?both\s+([\d.]+) Wh", line)
        if m and lid is not None:
            t = re.search(r"meets M1: ([+-][\d.]+) C", lines[i + 1])
            out[(lid, m.group(1), m.group(2))] = (m.group(3), float(m.group(4)), float(m.group(5)), float(m.group(6)),
                                                  float(t.group(1)) if t else None)
    return out


def main():
    global TMIN
    n0 = TP.NP_L
    d0, _p, _r, t2m = TP.load_model()
    TMIN = round(min(t2m), 2)
    rat = ratios()
    eff = efficiency_rows()
    b_lo, b_c, b_hi = hourly_row()
    u3_row = d0["solar"]["chain"][2]
    u3_ch, u3_drawn = eff["U3, chosen FETs, day at E2"], eff["U3, drawn FETs (S-117's row), day at E2"]
    b_800, b_draft, b_400 = eff["U3B, CSD17578Q5A x 4, 800 kHz"], eff["U3B, drafted (800 kHz, CSD18510Q5B)"], eff["U3B, 78/77 pairs, 400 kHz row"]
    if (u3_row["low"], u3_row["eta"], u3_row["high"]) != u3_ch or (TP.v("eta_u3b_lo"), TP.v("eta_u3b"), TP.v("eta_u3b_hi")) != (b_lo, b_c, b_hi):
        sys.stderr.write("reconcile_s119: the model's rows are not the parsed figures\n")
        sys.exit(3)
    o = []
    P = o.append
    P("OPTION A(i)'S LID RECONCILIATION ON THE RESTATED CHARGER ROWS (reconcile_s119.py, stream s119, S-119, second round).")
    P("PROTOTYPE DESIGN: nothing built, ordered or measured; AI arithmetic on the record's model, not a review by a person.")
    P("Model: records/a1elec/energy_two_pack.py second issue (sha256 %s...), as reconcile_lid_panel.py third issue runs" % PINS["a1elec/energy_two_pack.py"][:16])
    P("it: 400 Wp, 200 W stage, entry E2 (R11 6.2 mOhm), base +%.0f C, lid at %.2f C (the September mean day's minimum air)," % (TP.v("t_base_c"), TMIN))
    P("both start hours, 42.8 W, aged 80 percent, the 40 degree south plane unless section 7 says otherwise.")
    P("")
    P("0. THE CHARGER ROWS (lower / TI's reading / upper; the inductor's core loss EXCLUDED, so each figure is high by it)")
    P("   U3 as drawn (decision 57), the day at E2 (%s section 7):                     %.3f / %.3f / %.3f  carried %.3f" % (EFF, u3_ch[0], u3_ch[1], u3_ch[2], u3_row["eta"]))
    P("   U3B on the 400 kHz row (the S-119 decision), weighted over the model's hours (%s): %.3f / %.3f / %.3f  carried %.3f" % (UHO, b_lo, b_c, b_hi, TP.v("eta_u3b")))
    P("   for comparison, at the model's peak hour: the 400 kHz row %.3f (%.3f to %.3f); way (a), 800 kHz, CSD17578Q5A x 4, %.3f" % (b_400[1], b_400[0], b_400[2], b_800[1]))
    P("   the failing case, the FETs first drawn and drafted (CSD18510Q5B): U3 %.3f, U3B %.3f (TI's readings)" % (u3_drawn[1], b_draft[1]))
    P("   ratios (%s section 2): %s" % (RUNS, "; ".join("%s %.4f" % (k, rat[k][1]) for k in "ABC")))
    P("")

    # 1. the per-lid table, reproducing reconcile_lid_panel.out
    panel_now = head_equal(PANEL)
    P("1. PER LID OPTION, U3B AT ITS CARRIED FIGURE (each line reproduced byte for byte from %s, checked)" % PANEL)
    new = {}
    for n, what in LIDS:
        P(what)
        for k in "ABC":
            for uk, ua in U3_LIMITS:
                if k == "A" and uk != "nominal":
                    continue
                rs = run(n, rat[k][1], ua)
                note_peak(rs, "4S%dP, %s, U3 %s" % (n, k, uk))
                t = tmin_meets(n, rat[k][1], ua)
                l1 = "   %s, U3 %-7s %.1f A, at %.2f C: %s" % (k, uk, ua, TMIN, TP.fmt_run(rs))
                l2 = "      %s" % ("does not meet M1 even with the lid at +40 C" if t is None else "lowest lid temperature that still meets M1: %+.1f C" % t)
                if (l1 + "\n" + l2 + "\n") not in panel_now:
                    sys.stdout.write("\n".join(o) + "\n")
                    sys.stderr.write("reconcile_s119: this row is not in %s: %s\n" % (PANEL, l1))
                    return 5
                P(l1)
                P(l2)
                new[(n, k, uk)] = (TP.verdict(rs), min(r["low_b"] for r in rs), min(r["low_l"] for r in rs), low_both(rs), t)
        P("")

    # 2. the change from the accepted figures
    c_acc, text_acc = accepted()
    old = parse_panel(text_acc)
    P("2. THE CHANGE FROM THE ACCEPTED FIGURES (%s at %s, the second issue: U3 0.98, U3B 0.975), U3 at its" % (PANEL, c_acc[:8]))
    P("   6.1 A minimum, U3B at its carried figure; lowest store of both packs in Wh and the lowest lid temperature meeting M1")
    P("   %-44s %-24s %-24s %-24s %-24s" % ("lid option", "B typical, accepted", "B typical, now", "C adverse, accepted", "C adverse, now"))
    for n, what in LIDS:
        cells = []
        for k in "BC":
            ov, nv = old[(n, k, "minimum")], new[(n, k, "minimum")]
            for v, ok in ((ov, ov[0] == "MEETS"), (nv, nv[0])):
                cells.append(("MEETS %6.1f, %+.1f C" % (v[3], v[4])) if ok else "NOT MET")
        P("   %-44s %-24s %-24s %-24s %-24s" % (what.split(":")[0] + (", both kept" if n == 9 else (", tablet out" if n == 14 else ", QMX out")), *cells))
    for n in (14, 15):
        for k in "BC":
            ov, nv = old[(n, k, "minimum")], new[(n, k, "minimum")]
            P("   4S%dP %s: lowest both %.1f to %.1f Wh (%+.1f); base %.1f to %.1f; lid %.1f to %.1f; threshold %+.1f to %+.1f C" % (
                n, k, ov[3], nv[3], nv[3] - ov[3], ov[1], nv[1], ov[2], nv[2], ov[4], nv[4]))
    P("   the 6.0 A bracket: 4S14P C %.1f to %.1f Wh, 4S15P C %.1f to %.1f Wh; the nominal 6.2 A: 4S14P C %.1f to %.1f, 4S15P C %.1f to %.1f" % (
        old[(14, "C", "bracket")][3], new[(14, "C", "bracket")][3], old[(15, "C", "bracket")][3], new[(15, "C", "bracket")][3],
        old[(14, "C", "nominal")][3], new[(14, "C", "nominal")][3], old[(15, "C", "nominal")][3], new[(15, "C", "nominal")][3]))
    P("")

    # 3. U3B hour by hour
    P("3. U3B HOUR BY HOUR (U3 at 6.1 A): U3B's efficiency a function of its input power in each hour (u3b_hourly.py's curve,")
    P("   the buck-boost bound at the option's node and lid voltages); lowest store of both packs in Wh or NOT MET, and for TI's")
    P("   reading the lowest lid temperature that still meets M1")
    P("   %-24s %-16s %-24s %-16s %-16s %-22s" % ("case", "carried %.3f" % b_c, "hourly, TI", "hourly, maxima", "hourly, upper", "800 kHz way (a), TI"))
    hourly = {}
    for n, what in LIDS:
        for k in "BC":
            rs_c = run(n, rat[k][1], 6.1)
            rs_t = run(n, rat[k][1], 6.1, eta_b=curve(n, "TI"))
            note_peak(rs_t, "4S%dP, %s, hourly" % (n, k))
            t = tmin_meets(n, rat[k][1], 6.1, eta_b=curve(n, "TI")) if n != 9 else None
            rs_l = run(n, rat[k][1], 6.1, eta_b=curve(n, "lower"))
            rs_u = run(n, rat[k][1], 6.1, eta_b=curve(n, "upper"))
            rs_8 = run(n, rat[k][1], 6.1, eta_b=curve(n, "TI", "800"))
            hourly[(n, k)] = (TP.verdict(rs_t), low_both(rs_t), t)
            P("   %-24s %-16s %-24s %-16s %-16s %-22s" % (
                "4S%dP, ratio %s" % (n, k), cell(rs_c), cell(rs_t) + ("" if t is None else ", %+.1f C" % t), cell(rs_l), cell(rs_u), cell(rs_8)))
    P("   The hourly figures are the model's most faithful reading of U3B; the carried figure is its day-weighted equivalent.")
    P("")

    # 4. the failing case
    P("4. THE FAILING CASE: the chargers at the FETs first drawn and drafted (U3 %.3f, U3B %.3f), U3 at 6.1 A; it must read" % (u3_drawn[1], b_draft[1]))
    P("   NOT MET for both lid options in both ratio cases, or the instrument would not tell the circuits apart")
    bad = 0
    for n in (14, 15):
        for k in "BC":
            rs = run(n, rat[k][1], 6.1, eta_u3=u3_drawn[1], eta_b=b_draft[1])
            bad += 1 if TP.verdict(rs) else 0
            P("   4S%dP, %s: %s" % (n, k, TP.fmt_run(rs)))
    P("   %s" % ("every case NOT MET: the instrument discriminates" if bad == 0 else "%d case(s) MEET: the instrument does NOT discriminate" % bad))
    P("   The two halves apart (U3 at 6.1 A):")
    for lab, e3, eb in (("U3 as drawn %.3f, U3B with the FETs first drafted %.3f" % (u3_ch[1], b_draft[1]), u3_ch[1], b_draft[1]),
                        ("U3 with the FETs first drawn %.3f, U3B carried %.3f" % (u3_drawn[1], b_c), u3_drawn[1], b_c)):
        for n in (14, 15):
            for k in "BC":
                P("   %-60s 4S%dP %s: %s" % (lab, n, k, TP.fmt_run(run(n, rat[k][1], 6.1, eta_u3=e3, eta_b=eb))))
    P("")
    if bad:
        sys.stdout.write("\n".join(o) + "\n")
        sys.stderr.write("reconcile_s119: the failing case meets M1 somewhere; refusing\n")
        return 6

    # 5. sensitivity
    u3s = (u3_ch[0], u3_ch[1], u3_ch[2])
    u3bs = (b_lo, b_c, b_hi, b_800[1])
    P("5. SENSITIVITY (U3 at 6.1 A, U3B at a figure): lowest store of both packs in Wh, or NOT MET, over U3 %s and U3B %s" % (
        " / ".join("%.3f" % x for x in u3s), " / ".join("%.3f" % x for x in u3bs)))
    P("   (U3: the makers' maxima, TI's reading, the most favourable; U3B: the same on the 400 kHz row weighted over the")
    P("   model's hours, then way (a)'s 800 kHz peak-hour figure of the first round)")
    for n in (14, 15):
        for k in "BC":
            P("   4S%dP, ratio %s" % (n, k))
            P("      %-10s %s" % ("U3 \\ U3B", "".join("%12.3f" % b for b in u3bs)))
            for e3 in u3s:
                cells = []
                for eb in u3bs:
                    rs = run(n, rat[k][1], 6.1, eta_u3=e3, eta_b=eb)
                    cells.append("%12s" % (("%.1f" % low_both(rs)) if TP.verdict(rs) else "NOT MET"))
                P("      %-10.3f %s" % (e3, "".join(cells)))
    P("")

    # 6. the room for the excluded core loss
    P("6. THE ROOM FOR THE EXCLUDED CORE LOSS (U3 at 6.1 A, lid at %.2f C)" % TMIN)
    P("   6a. The lowest efficiency, each charger alone and the same at every hour, at which the option still meets M1 (the")
    P("       other charger at its carried figure; the watts are an indication at the peak hour only):")
    for n in (14, 15):
        for k in "BC":
            u3min = bisect_max(lambda x: TP.verdict(run(n, rat[k][1], 6.1, eta_u3=u3_row["eta"] - x)), 0.0, 0.2)
            bmin = bisect_max(lambda x: TP.verdict(run(n, rat[k][1], 6.1, eta_b=TP.v("eta_u3b") - x)), 0.0, 0.2)
            pk_b = max(r["peak"]["a_l"] for r in run(n, rat[k][1], 6.1))
            P("       4S%dP, %s: U3 down to %.4f (%.1f W at 126.3 W in); U3B down to %s (%.1f W at %.1f W in)" % (
                n, k, u3_row["eta"] - u3min, u3min * 126.3,
                ("%.4f" % (TP.v("eta_u3b") - bmin)) if bmin < 0.2 else "%.3f or lower (the search's floor)" % (TP.v("eta_u3b") - 0.2),
                bmin * pk_b, pk_b))
    P("   6b. HOUR BY HOUR: the largest constant loss in watts, added in every hour the charger runs, that still meets M1 (U3")
    P("       at its carried figure plus the loss; U3B on its hourly TI curve plus the loss). A core loss is closer to constant")
    P("       in watts than in percent, so these are the figures to hold it against:")
    for n in (14, 15):
        for k in "BC":
            cv = curve(n, "TI")
            c_u3 = bisect_max(lambda c: TP.verdict(run(n, rat[k][1], 6.1, eta_b=cv, u3_loss=c)), 0.0, 30.0)
            c_b = bisect_max(lambda c: TP.verdict(run(n, rat[k][1], 6.1, eta_b=with_loss(cv, c))), 0.0, 30.0)
            both05 = run(n, rat[k][1], 6.1, eta_b=with_loss(cv, 0.5), u3_loss=0.5)
            both10 = run(n, rat[k][1], 6.1, eta_b=with_loss(cv, 1.0), u3_loss=1.0)
            c_eq = bisect_max(lambda c: TP.verdict(run(n, rat[k][1], 6.1, eta_b=with_loss(cv, c), u3_loss=c)), 0.0, 30.0)
            P("       4S%dP, %s: U3 alone %s W; U3B alone %s W; the same loss in both %s W; 0.5 W in each: %s; 1.0 W in each: %s" % (
                n, k, "none" if c_u3 is None else "%.1f" % c_u3, "none" if c_b is None else "%.1f" % c_b,
                "none" if c_eq is None else "%.1f" % c_eq, cell(both05), cell(both10)))
    for n in (14, 15):
        need = []
        for k in "BC":
            x = bisect_max(lambda a: TP.verdict(run(n, rat[k][1], 6.35 - a)), 0.0, 3.35, 40)
            need.append("not met even at 6.35 A" if x is None else "%.2f A (%.1f W)" % (6.35 - x, (6.35 - x) * TP.V_BUS20))
        P("   6c. 4S%dP: the least current into U3 at VBUS20's 20.7 V (a limit held at its minimum) that still meets M1: B %s, C %s" % (n, need[0], need[1]))
    P("")

    # 7. the planes of the deployment rule
    AC, _EA, _TP = ER.pinned_import()
    AC.check_pins()
    ga, _ta, _pl = ER.september(ER.ANCHOR)
    prof0 = TP.load_model()[2]["months"][TP.MONTH]["profile"]
    k_scale = sum(prof0) / sum(ga)
    pr0 = rat["A"][1]
    P("7. THE DEPLOYMENT RULE'S PLANES (records/a1solar/energy_runs.py's plane files and fixed-point ratios, imported, pinned;")
    P("   each plane's own September mean day scaled by %.6f; U3 at 6.1 A; lid at %.2f C; U3B HOUR BY HOUR on its TI curve)." % (k_scale, TMIN))
    P("   Lowest both / lid in Wh or NOT MET; the carried figure gives the same verdict on every plane unless marked *")
    P("   %5s %5s %8s %8s   %-22s %-22s %-22s %-22s" % ("slope", "azim", "B ratio", "C ratio", "4S14P B", "4S14P C", "4S15P B", "4S15P C"))
    planes = [(0, 0)] + [(sl, az) for sl in (20, 30, 40, 50) for az in (-15, 0, 15)]
    allmeet = {14: True, 15: True}
    for sl, az in planes:
        G, TA, pl = ER.september(ER.plane_file(sl, az))
        assert (int(pl[0]), int(pl[1])) == (sl, az)
        Rp = ER.Ratios(AC, G, TA)
        rb = Rp.typical()
        rc, _f = Rp.adverse()
        pp = [k_scale * g for g in G]
        cells = []
        for n in (14, 15):
            for pr in (pr0 * rb, pr0 * rc):
                rs = run(n, pr, 6.1, prof=pp, eta_b=curve(n, "TI"))
                note_peak(rs, "4S%dP plane %d/%+d" % (n, sl, az))
                ok = TP.verdict(rs)
                same = TP.verdict(run(n, pr, 6.1, prof=pp)) == ok
                if sl != 0:
                    allmeet[n] = allmeet[n] and ok
                cells.append((("MEETS %6.1f / %5.1f" % (low_both(rs), min(r["low_l"] for r in rs))) if ok else "NOT MET") + ("" if same else " *"))
        P("   %5d %+5d %8.4f %8.4f   %-22s %-22s %-22s %-22s" % (sl, az, rb, rc, *cells))
    P("   inside the rule (20 to 50 degrees, azimuth -15 to +15 on the grid), both cases: 4S14P %s; 4S15P %s" % (
        "every plane MEETS" if allmeet[14] else "NOT every plane meets", "every plane MEETS" if allmeet[15] else "NOT every plane meets"))
    P("")

    # 8. U3B's input current
    P("8. U3B'S LARGEST INPUT CURRENT over every run above: %.2f A from VBAT (%s), against its IIN_HOST of 6.2 A (6.3 A" % tuple(PEAK_U3B_A))
    P("   maximum) and the 6.35 A clamp of the 400 kHz row's 10 mOhm sense (SLUSE66A 9.3.5, page 25).")
    P("")
    P("END. Each line is the model's arithmetic on the September reference day; nothing is measured.")
    TP.NP_L = n0
    TP.NP_T = TP.NP_B + n0
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
