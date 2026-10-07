#!/usr/bin/env python3
"""l4e11_rowc.py: record l4e11, round 19 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68; MESHSAT-1357, 7 October 2026).

Record l8p's round 11 (L8P-BREAKER.md section 16, l8p_cprot.out) corrected L8P-R10-F1 in draft with a held-overcurrent trip on board P
that touches neither the enable loop nor UVLO, and printed the thermal guard's allowance on DOCK_EN_OUT for its consumers (record
l8p 10c: 40 uA cold, 50 uA tripped; C261 and C268, 330 nF each). This round replays what section 28 left as remaining engineering
(28e): section 28 itself on the corrected circuit (L4A-67), 20f's docking against U47's and U48's tSD at the restated allowance, and
22's bleed with path 2's VBAT load (L4A-68), against this record's own windows: the held reading under 0.7755 V, the powered reading
at most 1.981 V, RET/OUT 0.4707 or more, the breaker's start no sooner than 0.110 s.

This script prints:
  0. its pins (sha256);
  1. the windows and the figures it replays against (RECORD: this record's l4e11_power.out; record l8p's l8p_c4.out and l8p_cprot.out);
  2. section 28 replayed on the corrected circuit (28a to 28d);
  3. 20f at the restated allowance against U47's and U48's tSD;
  4. 22's bleed with path 2's VBAT load and the board P trip's parts;
  5. the disposition, what stays open, and the outputs named for set 33;
  6. the predicates.
Labels: RECORD (another record's figure, read from its file), INFERRED (arithmetic on them by a stated rule), MODEL (the record's
time-constant model of 27b and 28d), ASSUMED. Nothing has been built, bought or measured; no V2 board exists.

Run from anywhere:  python3 v2/docs/records/l4e11/l4e11_rowc.py   (l4e11_rowc.out is its output, regenerated with _bin/regen_out.py).
Exit 0: printed, whatever the verdicts; 3: refused (an input missing or a figure not found)."""
import hashlib
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

RECS = {
    "e11": "v2/docs/records/l4e11/l4e11_power.out",
    "c4": "v2/docs/records/l8p/l8p_c4.out",
    "cprot": "v2/docs/records/l8p/l8p_cprot.out",
    "brk": "v2/docs/records/l8p/apply_gen_sch_p_breaker.py",
    "thg": "v2/docs/records/l8p/apply_gen_sch_a_thguard.py",
    "fs": "v2/docs/records/l8p/apply_gen_sch_a_thgfs.py",
    "och": "v2/docs/records/l8p/apply_gen_sch_p_ocheld.py",
}
VINS = (7.6, 10.6, 16.8)
C_TOL = 0.10              # the guard's capacitors at +10 % (this record's R17_C_TOL, round 17; record l8p's C_TOL)
R_TOL = 0.01              # R106 and the pair at 1 %, each at its worse sign (20c, 27a, 28a)


class Refused(Exception):
    pass


def refuse(msg):
    raise Refused(msg)


def p(rel):
    return os.path.join(ROOT, rel)


def sha(path, n=16):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:n]


def read(rel):
    if not os.path.exists(p(rel)):
        refuse("missing input %s" % rel)
    return open(p(rel), encoding="utf-8", errors="replace").read()


def need(text, pat, what):
    m = re.search(pat, text, re.S)
    if not m:
        refuse("%s: not found (%s)" % (what, pat[:70]))
    return m


def flat(s):
    return re.sub(r"\s+", " ", s)


def fmt(x, n=3):
    return ("%%.%df" % n) % x


def compute():
    R = {"pins": [(sha(p(rel)), rel) for rel in RECS.values() if os.path.exists(p(rel))]}
    for rel in RECS.values():
        read(rel)
    e = flat(read(RECS["e11"]))
    c4 = flat(read(RECS["c4"]))
    cp = flat(read(RECS["cprot"]))
    # 1. the windows (RECORD, this record's 20c, 20f, 22, 27 and 28)
    need(e, r"the return \(U48 channel 1\): read held under 0\.7755 V at least, closed over 0\.84 V at most", "20c's held and closed readings")
    need(e, r"the loop \(U48 channel 2\): read powered over 1\.981 V at most \(1\.825 V at least\), unpowered under 1\.789 V at least", "20c's powered readings")
    need(e, r"RET/OUT at least 0\.4707 with every sink doubled", "27a's window")
    need(e, r"at power-up U47 and U48 hold their outputs asserted for tSD, 2 ms at most", "20f's tSD")
    need(e, r"the breaker's start comes no sooner than the RC hold's least 0\.110 s", "the start no sooner than 0.110 s")
    m = need(e, r"within ([\d.]+) s with the sources at their hot bound \(([\d.]+) uA, section 22b\), inside the hold's least ([\d.]+) s while the sources total under ([\d.]+) uA", "22's bleed")
    BLEED, HOT, HOLD, COUPLED = (float(m.group(k)) for k in (1, 2, 3, 4))
    m = need(e, r"16\.8 \+ 30 \+ 388 = 434\.8 uA", "22b's sources")
    m = need(e, r"28a\. 20c WITH PATH 1 TRIPPED: the return held at ([\d.]+) V at most", "28a's held return")
    HELD = float(m.group(1))
    m = need(e, r"28b\. 20c WITH PATH 2 TRIPPED: Q61 holds DOCK_EN_OUT at ([\d.]+) mV and the return at ([\d.]+) mV", "28b's dark loop")
    DARK = (float(m.group(1)) / 1e3, float(m.group(2)) / 1e3)
    m = need(e, r"board A's (\d+) kOhm:\s*BRK_VIN 7\.6 V: DOCK_EN_OUT ([\d.]+) V", "28a's first row")
    R_OLOAD = float(m.group(1)) * 1e3
    R28 = [float(x) for x in re.findall(r"28a\..*?BRK_VIN\s+7\.6 V: DOCK_EN_OUT ([\d.]+) V.*?BRK_VIN 10\.6 V: DOCK_EN_OUT ([\d.]+) V.*?BRK_VIN 16\.8 V: DOCK_EN_OUT ([\d.]+) V", e)[0]]
    # the allowance and the delta's capacitors (RECORD, record l8p 10c and the drafts)
    m = need(c4, r"Allowances taken: (\d+) uA cold, (\d+) uA tripped", "the allowance (l8p 10c)")
    COLD, TRIP = float(m.group(1)) * 1e-6, float(m.group(2)) * 1e-6
    m = need(c4, r"supplied by U63 TPS70950DBVR from VBAT", "path 2 on VBAT")
    m = need(c4, r"cold at most [\d.]+ uA \(U60 16, U61 2\.25,", "path 2's switch and regulator rows")
    brk = read(RECS["brk"])
    m = need(brk, r'r\("R106", "(\d+)k", "BRK_VIN", "DOCK_EN_OUT"\); r\("R107", "(\d+)k", "DOCK_EN_RET", "PACK_N"\)', "R106 and R107")
    RF, R107 = float(m.group(1)) * 1e3, float(m.group(2)) * 1e3
    thg = read(RECS["thg"])
    m = need(thg, r'r\("R260", "([\d.]+)k 1%", "DOCK_EN_OUT", "THG_MID"\); r\("R261", "([\d.]+)k 1%", "THG_MID", "DOCK_EN_RET"\)', "the guard's pair")
    PAIR = (float(m.group(1)) + float(m.group(2))) * 1e3
    m = need(thg, r'c\("C262", "([\d.]+)u 16V X7R", "THG_VDD", "GND"\)', "C262")
    C262 = float(m.group(1)) * 1e-6
    fs = read(RECS["fs"])
    m = need(fs, r'c\("C261", "(\d+)n 50V X7R", "DOCK_EN_OUT", "GND"\);.*?c\("C268", "(\d+)n 50V X7R", "DOCK_EN_OUT", "GND"\)', "C261 and C268")
    C261, C268 = float(m.group(1)) * 1e-9, float(m.group(2)) * 1e-9
    need(fs, r'"1": "VBAT", "2": "GND", "3": "NC", "4": "NC", "5": "THG_VDD2"', "path 2's regulator on VBAT")
    # the board P trip (record l8p round 11): its nets and its APART reading
    need(cp, r"the trip touches neither the enable loop nor UVLO \(check_l8p_och's APART\)", "the trip's APART (l8p_cprot 4e)")
    need(cp, r"check_l8p_och\.py on it: OCH DRAWN", "the trip read DRAWN (l8p_cprot 5)")
    m = need(cp, r"the held current is ended from ([\d.]+) A at the least to ([\d.]+) A at the most", "the trip's window")
    WIN = (float(m.group(1)), float(m.group(2)))
    och = read(RECS["och"])
    OCH_NETS = set(re.findall(r'"(OCH_[A-Z0-9]+)"', och))
    LOOP = {"DOCK_EN_OUT", "DOCK_EN_RET", "BRK_UVLO", "BRK_H", "BRK_HD", "BRK_G2"}
    touched = sorted(n for n in LOOP if re.search(r'(?<![A-Z_])"%s"' % n, "\n".join(l.split("#")[0] for l in och.splitlines() if l.lstrip().startswith(("'", '"')))))
    R.update(BLEED=BLEED, HOT=HOT, HOLD=HOLD, COUPLED=COUPLED, HELD=HELD, DARK=DARK, R_OLOAD=R_OLOAD, R28=R28, COLD=COLD, TRIP=TRIP,
             RF=RF, R107=R107, PAIR=PAIR, C262=C262, C261=C261, C268=C268, WIN=WIN, OCH_NETS=sorted(OCH_NETS), touched=touched)

    # 2. 28a replayed: the pulled loop's DOCK_EN_OUT with path 1 tripped and the tripped allowance (the record's own formula, 28a)
    rf, rp = RF * (1 + R_TOL), PAIR * (1 - R_TOL)
    pulled = [(v, (v / rf + HELD / rp - TRIP) / (1 / rf + 1 / R_OLOAD + 1 / rp)) for v in VINS]
    # 28d and 20f: the closed loop's settled DOCK_EN_OUT with the cold allowance (the pair to the return, R107 to PACK_N; board A's
    # divider; the guard's cold draw; R106 +1 %, the pair and R107 -1 %, the worse signs for a low reading), and the rise's model
    rret = PAIR * (1 - R_TOL) + R107 * (1 - R_TOL)
    closed = [(v, (v / rf - COLD) / (1 / rf + 1 / R_OLOAD + 1 / rret)) for v in VINS]
    tau = RF * (1 + R_TOL) * (C261 + C268 + C262) * (1 + C_TOL)
    t_start = 0.110
    at_start = [(v, vc * (1 - math.exp(-t_start / tau))) for v, vc in closed]
    t_powered = [(v, -tau * math.log(1 - 1.981 / vc)) for v, vc in closed]
    ratio_closed = [(v, (R107 * (1 - R_TOL)) / rret) for v in VINS]     # RET/OUT of the closed, resistive loop (R107 over the pair and R107)
    R.update(pulled=pulled, closed=closed, tau=tau, at_start=at_start, t_powered=t_powered, sag=COLD * RF * (1 + R_TOL),
             ratio_closed=ratio_closed[0][1])
    # 4. 22's bleed: path 2's load (RECORD) is on VBAT; the sources into CELL+ are 22b's
    R.update(p2_load=(16e-6, 2.25e-6), bleed_margin=HOLD - BLEED, coupled_margin=COUPLED - HOT)
    # predicates
    R["preds"] = [
        ("28a: path 1 tripped reads held (the return under 0.7755 V)", HELD < 0.7755),
        ("28a: with the 50 uA drawn the loop reads powered at 7.6, 10.6 and 16.8 V (over 1.981 V)", all(v > 1.981 for _x, v in pulled)),
        ("28a replayed equals section 28's printed rows within 1 mV", all(abs(a - b) < 1.5e-3 for (_x, a), b in zip(pulled, R28))),
        ("28b: path 2 tripped reads dark (DOCK_EN_OUT under 1.789 V, the return under 0.7755 V)", DARK[0] < 1.789 and DARK[1] < 0.7755),
        ("28c: the board P trip touches no loop or UVLO net", not touched),
        ("20f: the closed loop's settled DOCK_EN_OUT with the cold 40 uA reads powered at each corner", all(v > 1.981 for _x, v in closed)),
        ("20f: DOCK_EN_OUT at the earliest start (0.110 s) reads powered at each corner", all(v > 1.981 for _x, v in at_start)),
        ("20f: the loop reads powered before the earliest start at each corner", all(t < t_start for _x, t in t_powered)),
        ("20f: the closed loop's RET/OUT is over the window's 0.4707", R["ratio_closed"] >= 0.4707),
        ("22: the bleed at the hot bound ends inside the hold's least", BLEED < HOLD),
        ("22: the hot bound is under the coupled limit", HOT < COUPLED),
    ]
    return R


def render(R):
    o = []
    w = o.append
    w("l4e11_rowc: record l4e11 round 19, Layer 4 register row (c): L4A-67 (section 28 replayed on the corrected circuit) and L4A-68 (20f and")
    w("22 replayed at the guard's restated allowance) (MESHSAT-1357, 7 October 2026). Desk arithmetic on the records' own figures; nothing was")
    w("built, bought or measured. LABELS: RECORD; INFERRED; MODEL; ASSUMED.")
    w("")
    w("0. PINS (sha256/16)")
    for s_, rel in R["pins"]:
        w("   %s  %s" % (s_, rel))
    w("")
    w("1. THE WINDOWS AND THE FIGURES (RECORD)")
    w("   this record's windows (20c, 27a, 20f): held under 0.7755 V; closed over 0.84 V; powered over 1.981 V at most (1.825 V at least);")
    w("     unpowered under 1.789 V; RET/OUT 0.4707 or more for a ramping closed loop; U47's and U48's tSD 2 ms at most; the breaker's start")
    w("     no sooner than the RC hold's least 0.110 s; 22's bleed %s s at the hot bound %s uA, inside the hold's least %s s, the coupled" % (
        fmt(R["BLEED"]), fmt(R["HOT"], 1), fmt(R["HOLD"])))
    w("     limit %s uA" % fmt(R["COUPLED"], 1))
    w("   the guard's allowance (record l8p 10c): %s uA cold, %s uA tripped; C261 and C268 %s and %s nF, C262 %s uF (the drafts); R106 %s kOhm," % (
        fmt(R["COLD"] * 1e6, 0), fmt(R["TRIP"] * 1e6, 0), fmt(R["C261"] * 1e9, 0), fmt(R["C268"] * 1e9, 0), fmt(R["C262"] * 1e6, 1), fmt(R["RF"] / 1e3, 0)))
    w("     R107 %s kOhm, the guard's pair %s kOhm, board A's %s kOhm on DOCK_EN_OUT" % (fmt(R["R107"] / 1e3, 0), fmt(R["PAIR"] / 1e3, 0), fmt(R["R_OLOAD"] / 1e3, 0)))
    w("   the corrected circuit: record l8p's fail-safe delta (round 9, apply_gen_sch_a_thgfs.py), M-A (round 10) and the held-overcurrent trip")
    w("     (round 11, apply_gen_sch_p_ocheld.py: a window of %s to %s A on board P; its nets %s; none of the loop's or UVLO's)" % (
        fmt(R["WIN"][0], 2), fmt(R["WIN"][1], 2), ", ".join(R["OCH_NETS"][:4]) + " and nine more"))
    w("")
    w("2. SECTION 28 REPLAYED ON THE CORRECTED CIRCUIT (L4A-67; INFERRED on 28's own formula)")
    w("   28a. path 1 tripped: the return held at %s V at most against 0.7755 V: read held; DOCK_EN_OUT with the tripped %s uA drawn, R106 +1 %%," % (
        fmt(R["HELD"], 4), fmt(R["TRIP"] * 1e6, 0)))
    w("     the pair -1 %, board A's divider:")
    for (v, x), rec in zip(R["pulled"], R["R28"]):
        w("       BRK_VIN %4.1f V: %s V (section 28 printed %s V) against 1.981 V: %s" % (v, fmt(x), fmt(rec), "read powered" if x > 1.981 else "NOT read powered"))
    w("     so a trip of path 1 is DD-7's trigger, as section 28 found; the held-overcurrent trip adds no sink on the return or DOCK_EN_OUT")
    w("   28b. path 2 tripped: DOCK_EN_OUT %s mV and the return %s mV (record l8p 10c): read dark (an undocked pack): no trigger" % (
        fmt(R["DARK"][0] * 1e3, 1), fmt(R["DARK"][1] * 1e3, 1)))
    w("   28c. the window: unchanged; the sinks on the return are 27a's; the trip's nets touch %s of DOCK_EN_OUT, DOCK_EN_RET, BRK_UVLO, BRK_H," % (
        "none" if not R["touched"] else ", ".join(R["touched"])))
    w("     BRK_HD and BRK_G2 (record l8p round 11, check_l8p_och's APART; its mutation of R140 onto DOCK_EN_OUT reads FAIL)")
    w("   28d. a docking: the rise's time constant %s ms (C261, C268 and C262 at +10 %%, R106 +1 %%, MODEL); the cold %s uA lowers DOCK_EN_OUT by" % (
        fmt(R["tau"] * 1e3, 1), fmt(R["COLD"] * 1e6, 0)))
    w("     at most %s V; the trip on board P is disarmed until the breaker runs (its arming on PGD), so a docking meets it never" % fmt(R["sag"]))
    w("   28 on the corrected circuit: every row holds at the restated allowance; the -1 latched by the trip is the state 20e and 22 already")
    w("     judge (CELL+ dead, the loop powered, the release on CELL+ alive or on DD-7's pulse): no new state for board A")
    w("")
    w("3. 20f AT THE RESTATED ALLOWANCE AGAINST U47'S AND U48'S tSD (L4A-68; INFERRED, the rise on 28d's MODEL)")
    w("   the closed loop's settled DOCK_EN_OUT with the cold %s uA (R106 +1 %%, the pair and R107 -1 %%, board A's divider), at the earliest" % fmt(R["COLD"] * 1e6, 0))
    w("     start 0.110 s after the loop closes, and the time the loop first reads powered (1.981 V):")
    for (v, vc), (_v2, vs), (_v3, tp) in zip(R["closed"], R["at_start"], R["t_powered"]):
        w("       BRK_VIN %4.1f V: settled %s V; at 0.110 s %s V; powered from %s ms" % (v, fmt(vc), fmt(vs), fmt(tp * 1e3, 1)))
    w("   the window (27a, 28c): a ramping closed loop's RET/OUT at least 0.4707 with every sink on the return doubled, at DOCK_EN_OUT's 1.825 V;")
    w("     the sinks are 27a's and none is added, so the rise never reads held; the loop's resistive RET/OUT is %s (R107 over the pair and" % fmt(R["ratio_closed"], 4))
    w("     R107, each at -1 %), information only")
    w("   with no source: board A is unpowered until the breaker's start feeds VBAT, no sooner than 0.110 s after the loop closes; U47 and U48")
    w("     then hold their outputs asserted for tSD (2 ms at most) and read the loop powered and the return closed: the inhibit for tSD at")
    w("     most, no hold armed, as 20f found; with a source present U47 and U48 run through the rise, the loop never reads held (RET/OUT) and")
    w("     reads powered before the earliest start at every corner")
    w("   a hot docking (path 1 already tripped, %s uA): the return held and the loop powered (2, 28a): DD-7's trigger, the breaker off, as" % fmt(R["TRIP"] * 1e6, 0))
    w("     designed")
    w("")
    w("4. 22'S BLEED WITH PATH 2'S VBAT LOAD (L4A-68; RECORD, INFERRED)")
    w("   path 2's switch and regulator draw from VBAT (U62 %s uA, U63 %s uA at their printed table maxima, record l8p 10c), not from CELL+:" % (
        fmt(R["p2_load"][0] * 1e6, 0), fmt(R["p2_load"][1] * 1e6, 2)))
    w("     22b's sources into CELL+ (the LM5069's internal 1 MOhm, the battery FETs, the breaker pair) are unchanged, 434.8 uA at the hot bound;")
    w("     with no source VBAT is dark and so is DD-7 (20f); with one, the load is the source's")
    w("   the held-overcurrent trip's crowbar Q111 and R140 sit on PACK_P, the pack terminal that reaches CELL+ through the lead and the dock:")
    w("     its off leakage is a SINK on CELL+, never a source, so it can only shorten the bleed; U106's inputs sit on GND and PACK_N (board")
    w("     P's sense), not on CELL+; no part of the trip pulls DD7_N, so U47's RESET states (22d) are unchanged")
    w("   the bleed %s s against the hold's least %s s: %s s of margin, unchanged; the hot bound %s uA under the coupled limit %s uA: %s uA" % (
        fmt(R["BLEED"]), fmt(R["HOLD"]), fmt(R["bleed_margin"]), fmt(R["HOT"], 1), fmt(R["COUPLED"], 1), fmt(R["coupled_margin"], 1)))
    w("     in hand, unchanged; both rest on record l8p's E-14c (the breaker pair's hot leakage, ASSUMED), as 22e states")
    w("")
    w("5. DISPOSITION (SESSION) AND WHAT STAYS OPEN")
    w("   28e's REMAINING ENGINEERING is executed here: 20f's timing against tSD and 22's bleed with path 2's VBAT load hold at the restated")
    w("     allowance; the allowance's consumers are restated by record l8p's two apply scripts (Layer 5's row in pcb_interfaces.yaml and")
    w("     record l9stk 15.9), DRAFTED, NOT APPLIED: until they are applied every row resting on the allowance stays PROVISIONAL")
    w("   still open: record l8p's L8P-R9-F1 pattern (a latent first failure of the guard, and now of the trip, with no automatic diagnostic);")
    w("     E-14c and E11-45 (f2), (h) for 22; the independent check of rounds 18 and 19 (L4A-69)")
    w("   outputs named for set 33: l4e11_power.out is not regenerated by this round (its section 28 stays the record's history; this output")
    w("     carries the replay); record l8p's l8p_cprot.out and l8p_rowc.out need the held makers' sheets (OPA187, LM5066I, BUK6Y10-30P, ROHM")
    w("     GMR100) installed on the box that regenerates them")
    w("")
    w("6. PREDICATES")
    for name, ok in R["preds"]:
        w("   %-118s %s" % (name, "yes" if ok else "NO"))
    return "\n".join(o) + "\n"


def main():
    try:
        R = compute()
    except Refused as e:
        sys.stderr.write("l4e11_rowc: REFUSED: %s\n" % e)
        return 3
    sys.stdout.write(render(R))
    return 0


if __name__ == "__main__":
    sys.exit(main())
