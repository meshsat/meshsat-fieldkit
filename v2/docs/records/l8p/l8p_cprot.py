#!/usr/bin/env python3
"""l8p_cprot.py: record l8p, round 11 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68; MESHSAT-1357, 7 October 2026).

L8P-R10-F1 (record l8p round 10, L8P-BREAKER.md 15c): at the breaker's held 23.93 A from the 76.25 C inside air the three 25 A MINI
blades carry 103.6 % of their printed rerated current. This round treats it as an unresolved design choice (constitution section 4:
at most three materially different approaches, none lowering a protection, the 18 A service or a printed rating's margin), selects
one as SESSION with its end condition, and draws it (apply_gen_sch_p_ocheld.py, release-guarded, composed with board P's drafts,
read by check_l8p_ocn and mutated). L4A-67: C-PROT rev 1 re-evaluated on the corrected circuit, every series part below and above
the trip on its printed limits or its missing figure named. L4A-68: the guard's allowance (record l8p 10c) printed for its consumers;
the replay of L4-E11's 20f, 22 and 28 is record l4e11's l4e11_rowc.py.

ROUND 12 (W149, 7 October 2026, after the focused check L4A-69, W147's F1 to F12): 4c' bounds a source's share of the crowbar's
current (the path that holds VSYS is the charger, not board E's entry) and restates R140's single pulse (E-6b) and Q111's row; 4i
states the BRK_VIN range the event can happen at, the band under 9.43 V where the crowbar's own current can hold the trip with the
-1 out of its limit, and the on-time bound drawn against it (channel 2 also disarms once the trip has been asserted: D106, R143,
C120 at 22 nF); check_l8p_och.py reads R10, R135, C117, C119 and C120 into the window and the delays, with the new mutations; 4g
carries a shorted crowbar with a source (L8P-R12-F1) and 4h the RC hold's stretch; the verdicts state L4A-67's latent-failure
clause NOT MET and name E-10 among L8P-R11-D1's conditions. The constitution was read and applied (sections 3 to 5 and 8).

ROUND 13 (W156, 7 October 2026, after the targeted recheck L4A-69, W153's F1, F2, F4 and notes F3, F5 to F8): 4j shows OCH_S2's level
while PGD is low in round 12's drawing with the leakage that reaches it at the record's site (Q112's off leakage on the record's
doubling rule, BAT46W's printed reverse current, the PGD pin's printed off leakage), compares three corrections on printed figures and
draws the selected one (OCH_S2 pulled up from BRK_VIN by R143 330 kOhm, held low while PGD is low by Q114, its gate PGD inverted by
Q113 with R144 and the zener D107); check_l8p_och.py reads that level with its mutations (a shorted D106 among them); 4i states the
band's upper edge with the loop's printed resistances and E-12s's specimen count, temperature, the unit's limit and uncertainty; 4c'
puts E-6b on one basis and states the nine-part count's; 4j also carries the start service, the PGD leakage basis of both levels,
SNVSBJ1E 8.3.5.1 and the cycling load on Vishay's continuous-pulse line; section 8 lists L8P-R12-F1 and the PGD-low disarm among
L8P-R10-F1's conditions and corrects round 12's "the service untouched".

This script prints:
  0. its pins (the records and the makers' documents it reads, sha256);
  1. the finding and the case (RECORD: record l8p round 10, l8p_rowc.py's own computation, records l9stk and l8p);
  2. the three approaches on printed figures: (A) a fuse or a holder arrangement, (B) a held-overcurrent trip into the -1's own latch,
     (C) a controller with a tighter printed current-limit spread;
  3. the selection (SESSION) and its end condition;
  4. the selected trip on printed figures: its window, its delays, the crowbar into the -1's latch, the arming on PGD, the parts'
     ratings and leakages, power-up and the start, its standing current, its own single failures; round 12 adds 4c' (a source's
     share, R140's restated pulse with a read candidate part, Q111's row) and 4i (the BRK_VIN range, the band, the on-time bound);
     round 13 adds 4j (the PGD-low disarm on leakage: round 12's level, three corrections, the selection and its levels);
  5. the draft composed in L4-E9's order, read by check_l8p_netlist.py and check_l8p_och.py, and its mutations;
  6. L4A-67: C-PROT rev 1 for the guard on the corrected circuit, part by part, with the trip intact and with it latently failed;
  7. L4A-68: the guard's allowance as its consumers are to restate it (the texts of the two apply scripts);
  8. the verdicts;
  9. the predicates.
Labels: PRINTED (a maker's printed limit or maximum), TYPICAL (never a limit), READING (this record's reading of a maker's drawing),
INFERRED (arithmetic on printed figures by a stated rule), MODEL, RECORD (another record's figure, read from its file), ASSUMED.
Nothing has been built, bought or measured; no V2 board exists.

Run from anywhere:  python3 v2/docs/records/l8p/l8p_cprot.py   (l8p_cprot.out is its output, regenerated with _bin/regen_out.py).
Exit 0: printed, whatever the verdicts; 3: refused (an input missing, a sha256 that differs, a printed row not found, a draft that
does not compose)."""
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import l8p_rowc as RC          # noqa: E402  round 10's computation, read, never retyped
import l8p_drafts as D         # noqa: E402  the composition helpers and L4-E9's board P order
import check_l8p_netlist as C  # noqa: E402
import check_l8p_och as O      # noqa: E402
import gen_netlist as GN       # noqa: E402


class Refused(Exception):
    pass


def refuse(msg):
    raise Refused(msg)


RECS = {
    "rowc": "v2/docs/records/l8p/l8p_rowc.out",
    "e11": "v2/docs/records/l4e11/l4e11_power.out",
    "c4": "v2/docs/records/l8p/l8p_c4.out",
    "prot": "v2/docs/records/l9stk/l9stk_protection.out",
    "stk": "v2/docs/records/l9stk/L9-STACKUPS.md",
    "draft": "v2/docs/records/l8p/apply_gen_sch_p_ocheld.py",
    "brk": "v2/docs/records/l8p/apply_gen_sch_p_breaker.py",
    "dio": "v2/docs/records/l8p/apply_gen_sch_p_idealdiode.py",
    "och": "v2/docs/records/l8p/check_l8p_och.py",
    "gen_p": "v2/ecad/tools/gen_sch_p.py",
    "l9g": "v2/docs/records/l8p/inputs/l9stk-section15.9-bb6d2c8f.md",
    "a5": "v2/docs/records/l8p/apply_pcb_interfaces_guard_allowance.py",
    "a9": "v2/docs/records/l8p/apply_l9stk_guard_allowance.py",
    "arch": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
}
DOCS = {
    "tps37": ("v2/vendor/ti/ti-tps37-snvsbj1e.pdf", "TI TPS37, SNVSBJ1E (August 2023)"),
    "opa187": ("v2/vendor/ti/held/ti-opa187-sbos807e.pdf", "TI OPA187, SBOS807E (held back)"),
    "lm5069": ("v2/vendor/ti/ti-lm5069.pdf", "TI LM5069, SNVS452G"),
    "lm5066i": ("v2/vendor/ti/held/ti-lm5066i-snvs950c.pdf", "TI LM5066I, SNVS950C (held back, fetch_held_back_rowc.py)"),
    "ao3401a": ("v2/vendor/power/aos-ao3401a-p-mosfet.pdf", "AOS AO3401A"),
    "n7002": ("v2/vendor/power/jscj-2n7002-c8545.pdf", "JSCJ 2N7002 (C8545)"),
    "csd": ("v2/vendor/battery/ti-csd18510q5b.pdf", "TI CSD18510Q5B, SLPS632"),
    "bzt": ("v2/vendor/diodes/diodes-bzt52c-ds18004.pdf", "Diodes BZT52C series, DS18004"),
    "lf297": ("v2/vendor/keystone/littelfuse-297-ficcorp.pdf", "Littelfuse MINI 297"),
    "bq25730": ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "TI BQ25730, SLUSE65A (held back, record l4e11's fetch_held_back.py)"),
    "bat46w": ("v2/vendor/diodes/diodes-bat46w.pdf", "Diodes BAT46W, DS30044 Rev. 20-2"),
    "crcwhp": ("v2/vendor/passives/held/vishay-crcw-hp-e3-20043-2026-03-17.pdf", "Vishay CRCW-HP e3, 20043 (17-Mar-2026; held back, fetch_held_back_rowc.py)"),
}
PIN = {"lm5066i": "a759a5d04fe5b81577af575153fd528f0f03f147c892040eac6c51e400693628",
       "bq25730": "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f",
       "crcwhp": "86a39a559a7be1ff772c95fd77ce386dad5a7744e848bab9eb27af55362df1a1"}

# ---------------------------------------------------------------- the trip as drawn (read back from the draft below)
G_RIN, G_RF = 1.00e3, 19.3e3
C_CTS1, C_CTS2, C_TOL = 4.7e-9, 22e-9, 0.05           # C0G, 5 % (C120 47 nF in round 11, 22 nF since round 12: the on-time bound)
R136, R137, R138, R139, R141, R142, R140 = 47e3, 100e3, 4.7e3, 1e6, 1e6, 1e3, 0.39
R143 = 330e3                                           # round 13: BRK_VIN to OCH_S2 (round 12: 2.2 MOhm from BRK_PGD, withdrawn)
R144 = 200e3                                           # round 13: BRK_VIN to OCH_PN, Q114's gate (PGD inverted by Q113)
R143_R12 = 2.2e6                                       # round 12's value, for 4j's showing of its PGD-low level
CISS_Q110_TYP, CISS_Q111_MAX = 645e-12, 11.4e-9        # AO3401A Ciss TYPICAL only (no maximum printed); CSD18510Q5B Ciss 11400 pF MAX
Q110_CISS_FACTOR = 2.0                                 # ASSUMED: twice the AO3401A's typical Ciss bounds its gate charge (no maximum printed)
TCL_RECORD = 50e-6                                     # tCL taken 50 us: 45 us TYPICAL, no maximum printed (RECORD, l9stk prot 3; F12)
PACK_LEAST, PACK_MOST, CLAMP = 10.6, 16.8, 29.2
SERVICE_TRUE = O.SERVICE_TRUE                          # 18.80 A: record l9stk condition C4
DOUBLING_K = 10.0                                      # the record's ASSUMED doubling of an off leakage every 10 K (l8p 12j, l9stk 15.9)
SITE = 86.25                                           # the site the record counts small parts' leakage at (the air plus 10 K)
BRK_LEAST_V, T_AIR_C = 7.6, 76.25                      # the -1's least BRK_VIN under C-PROT rev 1 (12d); the inside air (record l9stk)


def p(rel):
    return os.path.join(ROOT, rel)


def sha(path, n=64):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()[:n]


def read(rel):
    if not os.path.exists(p(rel)):
        refuse("missing input %s" % rel)
    with open(p(rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def doc(key):
    rel = DOCS[key][0]
    if not os.path.exists(p(rel)):
        refuse("missing maker's document %s (%s)" % (rel, DOCS[key][1]))
    if key in PIN and sha(p(rel)) != PIN[key]:
        refuse("%s: sha256 %s, pinned %s" % (rel, sha(p(rel), 16), PIN[key][:16]))
    return p(rel)


def pdftext(key, first=None, last=None):
    args = ["pdftotext", "-layout"]
    if first:
        args += ["-f", str(first), "-l", str(last or first)]
    r = subprocess.run(args + [doc(key), "-"], capture_output=True)
    if r.returncode != 0:
        refuse("pdftotext failed on %s" % DOCS[key][0])
    return r.stdout.decode("utf-8", "replace")


def need(text, pat, what, flags=re.S):
    m = re.search(pat, text, flags)
    if not m:
        refuse("%s: not found (%s)" % (what, pat[:70]))
    return m


def flat(s):
    return re.sub(r"\s+", " ", s)


def crcw2512_single_pulse(which=0):
    """READING of Vishay's CRCW-HP e3 single-pulse chart (document 20043, page 5, the upper chart 'Single Pulse') from its vector paths
    (pdftocairo -svg): the frame is the 0.96 pt rectangle; the time axis runs 1 us to 100 s over its width (the printed labels
    0.000001 to 100, eight decades), the power axis 0.01 W to 10 000 W over its height (the left labels, six decades; the right
    labels '10' to '10000' belong to a template's secondary axis titled 'Axis Title', and on it the 2512's line would read 122 W at
    100 s against its printed 1.5 W rating: the left axis is the one whose long-pulse end meets the printed P70 rows); the 2512's line
    is the 1.44 pt curve whose colour the legend's first sample carries (the legend's first text is CRCW2512-HP). Returns a function
    of the pulse duration in seconds, and the long-pulse reading at 100 s."""
    page = flat(pdftext("crcwhp", 5, 5))
    need(page, r"Single Pulse Axis Title 10 000 10000 CRCW2512-HP CRCW1218-HP 1000 CRCW2010-HP CRCW1210-HP CRCW1206-HP", "the single-pulse chart's legend order")
    need(page, r"0\.000001 0\.00001 0\.0001 0\.001 0\.01 0\.1 1 10 100 ti - Pulse Duration \(s\)", "the time axis labels")
    need(page, r"Maximum pulse load, single pulse; applicable if P \u2192 0 and n < 1000 and \u00db \u2264 \u00dbmax", "the curve's conditions")
    t1 = flat(pdftext("crcwhp", 1, 1))
    need(t1, r"Rated dissipation, P70 \(1\) 0\.2 W \(2\) 0\.33 W 0\.5 W 0\.75 W \(3\) 0\.75 W 1\.5 W 1\.0 W 1\.5 W", "the P70 row (2512: 1.5 W)")
    need(t1, r"Resistance range 1 [\u2126\u03a9] to 1 M[\u2126\u03a9]", "the resistance range")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "p.svg")
        r = subprocess.run(["pdftocairo", "-svg", "-f", "5", "-l", "5", doc("crcwhp"), out], capture_output=True)
        if r.returncode != 0:
            refuse("pdftocairo failed on the CRCW-HP sheet")
        svg = open(out, encoding="utf-8").read()
    frames, legend, curves = [], [], []
    for el in re.findall(r"<path[^>]*/>", svg):
        mcol = re.search(r"stroke:(rgb\([^)]*\))", el)
        mw = re.search(r"stroke-width:([\d.]+)", el)
        mt = re.search(r'transform="matrix\(([^)]*)\)"', el)
        md = re.search(r' d="([^"]*)"', el)
        if not (mcol and mw and md):
            continue
        a, b, c, dd, e, f = [float(x) for x in mt.group(1).split(",")] if mt else (1, 0, 0, 1, 0, 0)
        nums = [float(x) for x in re.findall(r"-?[\d.]+", md.group(1))]
        pts = [(a * x + c * y + e, 792 - (b * x + dd * y + f)) for x, y in zip(nums[0::2], nums[1::2])]
        if mcol.group(1) == "rgb(0%,0%,0%)" and mw.group(1) == "0.96":
            frames.append(pts)
        elif mw.group(1) == "1":
            legend.append((mcol.group(1), pts[0]))
        elif mw.group(1) == "1.44":
            curves.append((mcol.group(1), pts))
    if not frames:
        refuse("the CRCW-HP chart's frame was not found")
    if which:
        need(page, r"Maximum pulse load, continuous pulses; applicable if", "the continuous-pulse chart's conditions")
    tops = sorted(frames, key=lambda q: -max(y for _x, y in q))
    if len(tops) <= which:
        refuse("the CRCW-HP chart %d was not found" % which)
    top = tops[which]
    x0, x1 = min(x for x, _y in top), max(x for x, _y in top)
    y0, y1 = min(y for _x, y in top), max(y for _x, y in top)
    leg = [(col, pt) for col, pt in legend if y0 < pt[1] < y1]
    if len(leg) != 8:
        refuse("the single-pulse chart's legend does not read eight lines")
    col2512 = max(leg, key=lambda q: q[1][1])[0]
    pts = [p_ for col, p_ in curves if col == col2512 and y0 - 1 < p_[0][1] < y1 + 1]
    if len(pts) != 1 or (which == 0 and len(pts[0]) != 25) or (len(pts[0]) - 1) % 3 or len(pts[0]) < 4:
        refuse("the 2512's %s line was not read" % ("single-pulse", "continuous-pulse")[which])
    P = pts[0]
    dx, dy = (x1 - x0) / 8.0, (y1 - y0) / 6.0

    def watts(t):
        x = x0 + dx * math.log10(t / 1e-6)
        for k in range(0, len(P) - 1, 3):
            p0, p1, p2, p3 = P[k:k + 4]
            if p0[0] - 1e-6 <= x <= p3[0] + 1e-6:
                lo, hi = 0.0, 1.0
                for _ in range(60):
                    u = (lo + hi) / 2
                    xu = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
                    lo, hi = (u, hi) if xu < x else (lo, u)
                y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
                return 0.01 * 10 ** ((y - y0) / dy)
        refuse("a pulse duration outside the chart: %g s" % t)
    return watts, watts(100.0)


# ---------------------------------------------------------------- the computation
def compute():
    R = {"pins": []}
    for k, rel in RECS.items():
        read(rel)
        R["pins"].append((sha(p(rel), 16), rel))
    for k in DOCS:
        doc(k)
        R["pins"].append((sha(p(DOCS[k][0]), 16), DOCS[k][0]))
    W = RC.compute()                                     # round 10's own figures (its pins checked by it)
    R["W"] = W
    I, T_AIR = W["I"], W["T_AIR"]

    # 1. the case (RECORD)
    rowc = flat(read(RECS["rowc"]))
    need(rowc, r"23\.93 A held is 103\.6 % of the rerated current at the air \(OVER by 0\.83 A, 3\.6 %\)", "round 10's finding (l8p_rowc.out 3a)")
    prot = flat(read(RECS["prot"]))
    m = need(prot, r"current limit ([\d.]+) / ([\d.]+) / ([\d.]+) A \(VCL ([\d.]+) to ([\d.]+) mV", "the breaker's limits")
    LIM = tuple(float(m.group(k)) for k in (1, 2, 3))
    VCL = (float(m.group(4)), float(m.group(5)))
    m = need(prot, r"breaker ([\d.]+) to ([\d.]+) A \(VCB ([\d.]+) to ([\d.]+) mV\)", "the circuit breaker")
    CB = (float(m.group(1)), float(m.group(2)))
    m = need(prot, r"clearing ([\d.]+) ms at most from the limit's onset \(tCL ([\d.]+) us typical, no maximum printed\)", "the clearing")
    CLEAR, TCL_TYP = float(m.group(1)) * 1e-3, float(m.group(2)) * 1e-6
    m = need(prot, r"the fault pulse: ([\d.]+) W for ([\d.]+) ms against ([\d.]+) W derated: ([\d.]+)", "the fault pulse")
    PULSE = tuple(float(m.group(k)) for k in (1, 2, 3, 4))
    m = need(prot, r"VIN to SENSE's 0\.3 V maximum is passed above ([\d.]+) A", "VIN to SENSE's 0.3 V")
    VSNS_I = float(m.group(1))
    m = need(prot, r"acts only while PGD is low \(the breaker off, starting or in a fault: VDS over ([\d.]+) to ([\d.]+) V\)", "PGD's VDS")
    PGD_VDS = (float(m.group(1)), float(m.group(2)))
    need(prot, r"a persistent fault on the -1 \(selected\) \| one event, then latched until UVLO or VIN cycles", "the -1's latch row")
    need(prot, r"recovery: redocking, the input's return \(DD-7\), the guard's cycle", "the -1's recovery")
    stk = flat(read(RECS["stk"]))
    m = need(stk, r"\| 50 A for 600 s \(gauge failed\) \| ([\d.]+) C steady, reached before clearance \| \*\*OVER\*\* \| within \|", "the copper's 50 A row")
    CU50 = float(m.group(1))
    need(stk, r"board A's pack bands \| 105 C \| 125 C \|", "board A's band limits")
    need(stk, r"board E's pack bands \| 105 C \| 120 C \|", "board E's band limits")
    m = need(stk, r"\| Sense RS \| 4 mOhm and 7\.5 mOhm in parallel, 2\.6087 mOhm, 1 % and at most 50 ppm/K: plus or minus 1\.5 % for the parts only .*? \| its window ([\d.]+) to ([\d.]+) mOhm \|", "RS's window")
    RS = (float(m.group(1)), float(m.group(2)))
    c4 = flat(read(RECS["c4"]))
    m = need(c4, r"cold at most ([\d.]+) uA \(U60 16, U61 2\.25, the pull-up's leakage 1\.16, Q61 off 5\.58\), ([\d.]+) uA with the clamp's gates doubled; path 1 tripped at most ([\d.]+) uA \(the pull-up across 435\.6 kOhm\), ([\d.]+) uA with one of its resistors shorted\. Allowances taken: (\d+) uA cold, (\d+) uA tripped", "the guard's draw (l8p 10c)")
    DRAW = tuple(float(m.group(k)) for k in (1, 2, 3, 4))
    ALLOW = (float(m.group(5)), float(m.group(6)))
    m = need(c4, r"U62 LM26LVQISDX-130/NOPB on the same pour, supplied by U63 TPS70950DBVR from VBAT", "path 2 on VBAT (l8p 10c)")
    l9g = flat(read(RECS["l9g"]))
    need(l9g, r"The switch and the regulator draw 18\.25 uA at their printed maxima, against the 30 uA this round allows the guard\.",
         "record l9stk 15.9's allowance sentence (inputs copy at bb6d2c8f)")
    e11 = flat(read(RECS["e11"]))
    m = need(e11, r"overcurrent ([\d.]+) / ([\d.]+) / ([\d.]+) A \(the printed row, the 0\.1 % parts.*?short circuit ([\d.]+) / ([\d.]+) / ([\d.]+) A",
             "the entry's overcurrent and short-circuit rows (record l4e11 3c)")
    ENTRY = (float(m.group(1)), float(m.group(3)), float(m.group(4)), float(m.group(6)))
    R.update(LIM=LIM, VCL=VCL, CB=CB, CLEAR=CLEAR, TCL_TYP=TCL_TYP, PULSE=PULSE, VSNS_I=VSNS_I, PGD_VDS=PGD_VDS, CU50=CU50, RS=RS,
             DRAW=DRAW, ALLOW=ALLOW, ENTRY=ENTRY)

    # 2A. a fuse or a holder arrangement (Littelfuse's printed rerating; record l9stk's copper)
    need_f = I / 25.0
    cu60 = T_AIR + (CU50 - T_AIR) * (60.0 / 50.0) ** 2           # the copper's steady rise at the 30 A blade's 200 % (I^2, the record's own scaling)
    R.update(need_f=need_f, f_air=W["f_air"], f_band=W["f_band"], b30=W["blade30_rr"], b30_135=W["blade30_135"], cu60=cu60,
             band_pinned=(125.0, 120.0))

    # 2C. a controller with a tighter printed limit spread (TI LM5066I)
    t = flat(pdftext("lm5066i"))
    m = need(t, r"Current limit threshold voltage CL = VDD ([\d.]+) ([\d.]+) ([\d.]+) VCL mV \(VVIN_K \u2013 VSENSE\) CL = GND ([\d.]+) ([\d.]+) ([\d.]+)",
             "LM5066I VCL rows")
    V66 = (float(m.group(4)), float(m.group(6)))
    m = need(t, r"VIN, SENSE, OUT voltage ([\d.]+) ([\d.]+) V", "LM5066I recommended VIN")
    VIN66 = float(m.group(1))
    rs_spread = RS[1] / RS[0]
    most_at = lambda least: V66[1] / (V66[0] / least / rs_spread) if False else least * (V66[1] / V66[0]) * rs_spread
    R.update(V66=V66, VIN66=VIN66, rs_spread=rs_spread, c_most_1832=most_at(LIM[0]), c_most_1880=most_at(SERVICE_TRUE),
             c_need=W["I_rr_air"] / LIM[0])

    # 4a. the window (check_l8p_och's own arithmetic on the drawn values)
    dr = read(RECS["draft"])
    for pat in (r'r\("R132", "1\.00k 0\.1% 25ppm', r'r\("R133", "19\.3k 0\.1% 25ppm', r'c\("C119", "4\.7n 50V C0G 5%', r'c\("C120", "22n 50V C0G 5%', r'r\("R143", "330k 1%", "BRK_VIN", "OCH_S2"\)', r'nfet\("Q113", "BRK_PGD", "PACK_N", "OCH_PN"', r'r\("R144", "200k 1%", "BRK_VIN", "OCH_PN"\)',
                r'part\("D107", "Device", "D_Zener", "BZT52C12-7-F', r'nfet\("Q114", "OCH_PN", "PACK_N", "OCH_S2"',
                r'part\("D106", "Device", "D_Schottky", "BAT46W-7-F',
                r'r\("R136", "47k"', r'r\("R137", "100k"', r'r\("R142", "1k", "OCH_GD", "OCH_CG"\); r\("R138", "4\.7k"',
                r'r\("R140", "0\.39R 1% ', r'r\("R139", "1M", "BRK_VIN", "OCH_EG"\); r\("R141", "1M", "OCH_EG", "PACK_N"\)'):
        need(dr, pat, "the draft's value %s" % pat[3:9])
    t37 = flat(pdftext("tps37"))
    need(t37, r"VITP \(Overvoltage\) VIT = 800 mV \(3\) 0\.792 0\.800 0\.808 V", "TPS37 VITP at 800 mV")
    need(t37, r"RCTS 88 100 122 Kohms", "TPS37 RCTS")
    need(t37, r"tCTSx \(min\) = -ln \(0\.31\) x RCTSx \(min\) x CCTSx_EXT \(min\)", "TPS37 Equation 5")
    need(t37, r"tCTSx \(max\) = -ln \(0\.25\) x RCTSx \(max\) x CCTSx_EXT \(max\)", "TPS37 Equation 6")
    need(t37, r"VIT = 800 mV CCTS1 = CCTS2 = Open 8 17 [µμ]s", "TPS37 tCTS without a capacitor")
    need(t37, r"tSD Startup Delay \(4\) 2 ms", "TPS37 tSD")
    need(t37, r"tCTR \(CTR1/MR, CTR2/MR\) \(2\) VIT = 800 mV CCTR1 = CCTR2 = Open 40 [\u00b5\u03bc]s", "TPS37 tCTR without a capacitor")
    need(cs_pre := flat(pdftext("csd")), r"Ciss Input capacitance 8770 11400 pF", "CSD18510Q5B Ciss")
    need(t37, r"VRESET = 5\.5 V 300 nA Open-Drain leakage", "TPS37 open-drain leakage")
    need(t37, r"Current IRESET1, IRESET2, IRESET1, IRESET2 0 ±5 mA", "TPS37 recommended RESET current")
    need(t37, r"Voltage VDD 2\.7 65 V", "TPS37 VDD range")
    need(t37, r"ISENSE VIT = 800 mV 100 nA", "TPS37 ISENSE")
    need(t37, r"VIT = 800 mV 1 2\.6 [µμ]A", "TPS37 IDD at 800 mV")
    o = flat(pdftext("opa187"))
    need(o, r"OFFSET VOLTAGE ±1 ±10 [µμ]V VOS Input offset voltage TA = \u201340°C to \+125°C ±0\.001 ±0\.015 [µμ]V/°C", "OPA187 VOS and drift")
    need(o, r"\(V\u2013\) \u2013 0\.1 \(V\+\) \u2013 2 V", "OPA187 VCM")
    need(o, r"IO = 0 mA, TA = \u201340°C to \+125°C 150 [µμ]A", "OPA187 IQ")
    lo, hi = O.window({"comps": {"R132": {"value": "1.00k"}, "R133": {"value": "19.3k"}, "R135": {"value": "1k"},
                                 "R10": {"value": "2m 2512 2W (sense)"}}, "pins": {}, "on": {}})   # the drafted values; section 5 reads the netlist
    gd = O.GAIN_TOL + O.GAIN_TCR * O.GAIN_DT
    vos_tot = O.VOS
    r10_hi = (O.VITP[0] - (1 + G_RF / G_RIN * (1 + gd) / (1 - gd)) * vos_tot - O.IB * G_RF * (1 + gd) - O.ISENSE * 1e3) / \
             ((G_RF / G_RIN * (1 + gd) / (1 - gd)) * SERVICE_TRUE)
    r10_lo = (O.VITP[2] + (1 + G_RF / G_RIN * (1 + gd) / (1 - gd)) * vos_tot + O.IB * G_RF * (1 + gd) + O.ISENSE * 1e3) / \
             ((G_RF / G_RIN * (1 - gd) / (1 + gd)) * O.BLADE_BAND)
    R.update(win=(lo, hi), r10_room=(r10_lo / O.R10_NOM - 1, r10_hi / O.R10_NOM - 1),
             r10_assumed=O.R10_TOL + O.R10_TCR * O.R10_DT, out_service=G_RF / G_RIN * SERVICE_TRUE * O.R10_NOM,
             out_18=G_RF / G_RIN * 18.0 * O.R10_NOM, out_10=G_RF / G_RIN * 10.0 * O.R10_NOM)

    # 4b. the delays (TI's Equations 5 and 6; the no-capacitor delay's least is not printed, taken 0)
    tcts1 = (-math.log(0.31) * 88e3 * C_CTS1 * (1 - C_TOL), -math.log(0.25) * 122e3 * C_CTS1 * (1 + C_TOL) + 17e-6)
    tcts2 = (-math.log(0.31) * 88e3 * C_CTS2 * (1 - C_TOL), -math.log(0.25) * 122e3 * C_CTS2 * (1 + C_TOL) + 17e-6)
    R.update(tcts1=tcts1, tcts2=tcts2, e10=0.282e-3, tsd=2e-3)

    # 4c. the crowbar into the -1's latch
    i_c = lambda v, r=R140 * 1.01: v / r
    R.update(ic_least=i_c(PACK_LEAST), ic_16=i_c(PACK_MOST), ic_clamp=i_c(CLAMP, R140 * 0.99),
             peak_16=i_c(PACK_MOST, R140 * 0.99) + LIM[2], peak_clamp=i_c(CLAMP, R140 * 0.99) + LIM[2],
             vlim=LIM[2] * R140 * 1.01)
    p_lim = R["vlim"] ** 2 / (R140 * 0.99)
    e_lim = p_lim * (CLEAR + TCL_RECORD)
    c_kit = 593e-6
    e_cap = 0.5 * c_kit * R["vlim"] ** 2
    e_spike = R["peak_clamp"] ** 2 * R140 * 16.5e-6                # round 11's arithmetic: the crowbar's peak with the load's (an overcount)
    R.update(p_lim=p_lim, e_lim=e_lim, e_cap=e_cap, e_spike=e_spike, e_n=e_lim + e_cap + e_spike)
    # the sequence: the trip's sense delay, the gate drive, the -1's clearing; the arming's delay after PGD falls
    t_gate = 75e-9 / ((PACK_LEAST - 4.5) / R142)                  # Qg(4.5 V) 75 nC at most through R142 from BRK_VIN
    R.update(t_gate=t_gate, t_event=tcts1[1] + t_gate + CLEAR, arm_margin=tcts2[0] - (t_gate + CLEAR))
    # the crowbar's turn-off once RESET1 releases or RESET2 disarms (round 12 adds Q110's own turn-off, which round 11 left out): tCTR1
    # without a capacitor at most 40 us (PRINTED); Q110's gate pulled up through R136 (+1 %) from its drive to 0.5 V with twice its
    # TYPICAL Ciss (ASSUMED: no maximum printed); Q111's gate through R138 (+1 %) for five time constants of its PRINTED 11.4 nF maximum
    t_q110 = max(math.log(v * R136 / (R136 + R137) / 0.5) for v in (PACK_LEAST, PACK_MOST, CLAMP)) * R136 * 1.01 * Q110_CISS_FACTOR * CISS_Q110_TYP
    t_off = 40e-6 + t_q110 + 5 * R138 * 1.01 * CISS_Q111_MAX
    R.update(t_q110=t_q110, t_off=t_off, t_src=R["t_event"] + t_off)
    need(t37, r"VOL \(5\) Low level output voltage 300 mV", "TPS37 VOL")
    need(t37, r"tCTR \(CTR1/MR, CTR2/MR\) \(2\) VIT = 800 mV CCTR1 = CCTR2 = Open 40", "TPS37 tCTR at 800 mV")
    need(flat(pdftext("ao3401a")), r"Ciss Input Capacitance 645 pF", "AO3401A Ciss (TYPICAL only)")

    # 4c'. A SOURCE'S SHARE OF THE CROWBAR'S CURRENT (round 12; the check's F1). The path that holds VSYS (L4-E9's power edges): board
    # E's entry feeds VIN_RAW, board A's front end makes VBUS20 and the charger U3 holds VSYS; board E's thresholds bound VIN_RAW's
    # current two conversions upstream, not the current a source pushes from VSYS through board A's battery FETs into PACK_P
    arch = flat(read(RECS["arch"]))
    need(arch, r"\| P06 \| ENTRY \| VINRAW \| R19, L2 to VIN_RAW \|", "L4-E9's edge P06: the entry feeds VIN_RAW")
    need(arch, r"\| P07 \| VINRAW \| FE \| the dock's pins, U2's input \|", "L4-E9's edge P07: VIN_RAW into the front end")
    need(arch, r"\| P10 \| CHG \| VBAT \| U3's output, VSYS \|", "L4-E9's edge P10: the charger holds VSYS")
    need(arch, r"\| P11 \| VBAT \| PACK \| \(B1\) Q39 and Q40 to CH_BATQ, then R17, A F1, the pack pins, board P \|", "L4-E9's edge P11: VSYS to the pack")
    m = need(e11, r"to ([\d.]+) V \(the pack at ChargeVoltage's ([\d.]+) V plus 150 mV, \+2 %, p\.9\): BOUNDED", "VSYS's most (L4-E11 12c)")
    vsys_max = float(m.group(1))
    m = need(e11, r"into a resistive fault at sqrt\(P x R\): ([\d.]+) V at the breaker's least-limit fault of ([\d.]+) ohm with the front end's "
             r"([\d.]+) W \(its ([\d.]+) A ISNS maximum\)", "the source's settled power into a resistive fault (L4-E11, B-R2's reach)")
    p_src = float(m.group(3))
    inh_v = float(need(e11, r"the inhibit sets only when CELL\+ falls under ([\d.]+) V", "the DD-7 inhibit's CELL+ threshold (L4-E11)").group(1))
    bq = flat(pdftext("bq25730"))
    need(bq, r"Pre-charge current REG0x03/02\(\) = 0x00C0H 384 mA regulation accuracy \u22652S \u201325\.0% 25\.0%", "BQ25730 IPRECHRG_REG_ACC at 384 mA")
    need(bq, r"CONVERTER OVER-CURRENT COMPARATOR \(Q2\) Converter Over- Reg0x32\[5\]=1b 150 mV", "BQ25730 VOCP_lim_Q2 (a TYPICAL only)")
    pre_max = 0.384 * 1.25
    r_lo, r_hi = R140 * 0.99, R140 * 1.01
    # the crowbar conducts until RESET1 releases (after the -1 latches, the cells' current through R10 stops) or RESET2 disarms
    # (round 12): while the -1 conducts, PACK_P is under BRK_VIN; once latched it is at most VSYS. No printed figure bounds the
    # source's current inside the event (the charger's and the front end's regulation loops print no settling time; the charger's
    # cycle-by-cycle comparators print a typical only), so R140's power is bounded on VOLTAGE over the bounded on-time
    p_on, p_after = PACK_MOST ** 2 / r_lo, vsys_max ** 2 / r_lo
    R.update(vsys_max=vsys_max, p_src=p_src, inh_v=inh_v, pre_max=pre_max, p_on=p_on, p_after=p_after,
             v_settled=math.sqrt(p_src * r_hi), i_settled=math.sqrt(p_src / r_hi),
             e_n_src=p_on * (t_gate + CLEAR + TCL_RECORD) + p_after * t_off + e_spike)

    # 4i. THE BRK_VIN RANGE AND THE ON-TIME BOUND (round 12; the check's F2). The -1 runs from 7.6 V (record l8p 12d, C-PROT rev 1;
    # LM5069's PORIT, typical) to the pack's 16.8 V; the crowbar's own current exceeds the most limit only from LIM x R140 (+1 %)
    l69 = flat(pdftext("lm5069"))
    need(l69, r"PORIT VIN increasing 7\.6 8 V", "LM5069 PORIT")
    v_force = R["LIM"][2] * r_hi
    lim, w_lo = R["LIM"][2], R["win"][0]
    # the band where the crowbar's own current lies between the trip's least and a unit's most limit (no source); with a source's
    # settled share on the record's B-R2 basis (p_src into the pack side) the -1 can stay under its limit up to v_band_src; a held
    # overload that persists through the bound needs the source to carry (V / R140 + the window's least - the most limit) x V
    v_band_src = (lim * r_hi + math.sqrt((lim * r_hi) ** 2 + 4 * p_src * r_hi)) / 2
    a_ = 1 / r_hi
    v_resid = (-(w_lo - lim) + math.sqrt((w_lo - lim) ** 2 + 4 * a_ * p_src)) / (2 * a_)
    R.update(v_floor=7.6, v_force=v_force, band=(w_lo * r_lo, v_force), v_band_src=v_band_src, v_resid=v_resid)
    t2 = tcts2
    R.update(t_on_max=t2[1] + t_off, arm_cover=t2[0] - (t_gate + CLEAR))
    p_stall = R["LIM"][2] ** 2 * r_hi                                  # the crowbar's own current under the most limit, no source
    R.update(p_stall=p_stall, e_s=p_stall * (t2[1] + t_off), e_w=p_on * t2[1] + p_after * t_off + e_spike,
             p_peak=CLAMP ** 2 / r_lo, i_q111_src=vsys_max / r_lo,
             p_q111_off=vsys_max ** 2 / (4 * r_lo), p_q111_off_settled=p_src * r_hi / (4 * r_lo),
             p_q111_off_nosrc=v_force ** 2 / (4 * r_lo), t_q111_off=5 * R138 * 1.01 * CISS_Q111_MAX)
    # round 13 (the recheck's F3): E-6b on ONE basis, the voltage bound throughout: VSYS's most on R140 at its least for the whole
    # bounded on-time (the trip's gate, the arming's most and the turn-off), and the onset at the clamp as round 11 counts it
    R["e_v"] = p_after * (t2[1] + t_off) + e_spike
    R["e_r140"] = max(R["e_n"], R["e_s"], R["e_w"], R["e_v"])
    # the named part (round 12; READING of Vishay's single-pulse line for the 2512 size): each of n equal parts in parallel carries 1/n
    # of R140's power; the most power of each case over its duration against the line at that duration
    watts, w100 = crcw2512_single_pulse()
    cases = (("n", R["p_lim"], t_gate + CLEAR + TCL_RECORD), ("nsrc", p_after, t_gate + CLEAR + TCL_RECORD + t_off),
             ("s", p_stall, t2[1] + t_off), ("w", p_after, t2[1] + t_off), ("peak", CLAMP ** 2 / r_lo, 16.5e-6))
    R["crcw"] = {k: (pw, t_, watts(t_), math.ceil(pw / watts(t_))) for k, pw, t_ in cases}
    R["crcw_w100"] = w100
    R["crcw_n"] = max(v[3] for v in R["crcw"].values())
    need(dr, r"single pulse of at least %s J in %s ms with %s kW for 16\.5 us" % (re.escape(fmt(R["e_r140"], 2)), re.escape(fmt(R["t_on_max"] * 1e3, 2)),
         re.escape(fmt(R["p_peak"] / 1e3, 2))), "the draft's R140 stating this round's pulse")
    # D106's low level and R143's levels (check_l8p_och's own arithmetic on the drawn values)
    bt = flat(pdftext("bat46w"))
    need(bt, r"0\.25 IF = 0\.1mA Forward Voltage VF", "BAT46W VF at 0.1 mA")
    need(flat(pdftext("n7002")), r"Gate-Threshold Voltage Vth\(GS\) VDS=VGS, ID=250 \u00b5A 1 1\.6 2\.5", "2N7002 Vth(GS)")
    # 4d. ratings and leakages
    vgs110 = (PACK_LEAST * R136 / (R136 + R137), CLAMP * R136 / (R136 + R137))
    leak_n = 80e-9 * 2 ** ((SITE - 25.0) / DOUBLING_K)             # 2N7002 80 nA at 25 C (PRINTED), doubled (ASSUMED)
    leak_p = 5e-6 * 2 ** ((SITE - 55.0) / DOUBLING_K)              # AO3401A 5 uA at 55 C (PRINTED), doubled (ASSUMED)
    leak_p101 = 5e-6 * 2 ** ((101.0 - 55.0) / DOUBLING_K)
    R.update(vgs110=vgs110, leak_n=leak_n, leak_p=leak_p, v_off110=(leak_n + 0.3e-6) * R136, v_cg_off=leak_p * R138,
             v_cg_off101=leak_p101 * R138, vth_p=0.5, vth_csd=1.2, ireset1=CLAMP / (R136 + R137), ireset2=CLAMP / R139,
             vgs112=CLAMP / 2, vcg=12.7, ig110=(CLAMP - 11.4) / R142 + 12.7 / R138, iz=(CLAMP - 11.4) / R142,
             stand=(150e-6, 2.6e-6, PACK_MOST / (R139 + R141)))
    need(flat(pdftext("ao3401a")), r"Gate-Source Voltage VGS ±12 V", "AO3401A VGS")
    need(flat(pdftext("ao3401a")), r"VGS\(th\) Gate Threshold Voltage VDS=VGS ID=-250mA -0\.5 -0\.9 -1\.3 V", "AO3401A VGS(th)")
    need(flat(pdftext("ao3401a")), r"TJ=55°C -5", "AO3401A IDSS at 55 C")
    need(flat(pdftext("n7002")), r"Zero Gate Voltage Drain Current IDSS VDS=60 V, VGS=0 V 80 nA", "2N7002 IDSS")
    need(flat(pdftext("n7002")), r"Gate-Source Voltage VGS ±20 V", "2N7002 VGS")
    cs = flat(pdftext("csd"))
    need(cs, r"VGS\(th\) Gate-to-source threshold voltage VDS = VGS, ID = 250 μA 1\.2 1\.7 2\.3 V", "CSD18510Q5B VGS(th)")
    need(cs, r"Qg Gate charge total \(4\.5 V\) 58 75 nC", "CSD18510Q5B Qg")
    need(cs, r"IDM Pulsed Drain Current, TA = 25°C\(2\) 400 A", "CSD18510Q5B IDM")
    need(cs, r"IDSS Drain-to-source leakage current VGS = 0 V, VDS = 32 V 1 μA", "CSD18510Q5B IDSS")
    need(flat(pdftext("bzt")), r"BZT52C12 WH 12 11\.4 12\.7", "BZT52C12 VZ")
    l69 = flat(pdftext("lm5069"))
    need(l69, r"When the external MOSFET VDS increases above 2\.5 V the PGD indicator switches low", "LM5069 PGD")
    need(l69, r"If the voltage across RS reaches 55 mV the load current is limited and the fault timer activates", "LM5069 SENSE")
    # 4h. the drawn UVLO node at a start (record l8p's own C-1b; not this round's circuit): UVLOHYS 12 to 30 uA PRINTED (enabled below
    # the threshold, SNVS452G 8.3.4), R104 200 kOhm +1 %, D102's 0.715 V and UVLOTH's 2.55 V as record l9stk reads them, and the off
    # leakage of Q104 and Q105 (2N7002, drains on BRK_UVLO) at 80 nA at 25 C PRINTED, doubled every 10 K (ASSUMED, the record's rule)
    need(l69, r"UVLOHYS UVLO hysteresis current UVLO = 1 V 12 21 30", "LM5069 UVLOHYS")
    need(l69, r"When VSYS is below the UVLO level, the internal 21-.A current source at UVLO is enabled", "LM5069 UVLO sink below the level")
    need(prot, r"settles at 4\.6 V, over 2\.55 V and the diode's 0\.715 V", "record l9stk's H at 10.6 V (the sink alone)")

    def uvlo_at(site, vin=PACK_LEAST, n=2, rf=1.01):
        leak = 80e-9 * 2 ** ((site - 25.0) / DOUBLING_K)
        h = vin - 200e3 * rf * (30e-6 + n * leak)
        return h, h - 0.715
    lo_t, hi_t = 25.0, 150.0
    for _ in range(80):
        mid = (lo_t + hi_t) / 2
        lo_t, hi_t = (mid, hi_t) if uvlo_at(mid)[1] >= 2.55 else (lo_t, mid)
    R.update(uvlo_air=uvlo_at(76.25), uvlo_site=uvlo_at(SITE), uvlo_t=lo_t, uvlo_sink_only=uvlo_at(-273.0, n=0, rf=1.0))

    # the RC hold's release on the same rule (round 12; the check's F8): BRK_H charges through R104 (+1 %) into C103 (3.3 uF +10 %,
    # record l9stk's CAP_TOL) toward its settled value and releases at UVLOTH's 2.55 V plus D102's 0.715 V
    def hold_t(site, n=2, rf=1.01):
        h = uvlo_at(site, n=n, rf=rf)[0]
        need_h = 2.55 + 0.715
        return float("inf") if h <= need_h else 200e3 * 1.01 * 3.3e-6 * 1.10 * math.log(h / (h - need_h))
    R.update(hold_sink_only=hold_t(-273.0, n=0, rf=1.0), hold_air=hold_t(76.25), hold_site=hold_t(SITE))

    # 4j. ROUND 13 (the targeted recheck's F1): THE PGD-LOW DISARM ON LEAKAGE. First round 12's drawing: OCH_S2 pulled to BRK_PGD's low
    # through R143 2.2 MOhm only; whatever leaks into OCH_S2 lifts it by I x R143. Sources: Q112's off leakage into OCH_R once Q112 is
    # off (through D106 reversed), D106's own reverse current while Q112 holds OCH_R up; sinks at their printed maxima only help.
    need(t37, r"\(Undervoltage\) VIT = 800 mV \(3\) 0\.792 0\.800 0\.808 V", "TPS37 VITN at 800 mV")
    need(t37, r"VIT > 26 V ISENSE 2 [µμ]A", "TPS37 ISENSE's largest printed row")
    need(t37, r"needs to be greater than 10% of the programmed sense time delay", "TPS37 8.3.5.1 (a CTS capacitor not fully discharged)")
    need(bt, r"0\.3 VR = 1\.5V 5\.0 VR = 1\.5V, TJ = \+60°C 0\.5 VR = 10V 7\.5 VR = 10V, TJ = \+60°C", "BAT46W IR at 1.5 and 10 V")
    need(bt, r"1\.0 VR = 50V 15 VR = 50V, TJ = \+60°C", "BAT46W IR at 50 V")
    need(bt, r"0\.45 V IF = 10mA", "BAT46W VF at 10 mA")
    n7 = flat(pdftext("n7002"))
    need(n7, r"VGS=5 V, ID=50mA 1\.1 7", "2N7002 RDS(on) at VGS 5 V")
    need(n7, r"Gate-body Leakage lGSS VDS=0 V, VGS=±20 V ±80 nA", "2N7002 IGSS")
    need(flat(pdftext("bzt")), r"BZT52C12 WH 12 11\.4 12\.7 5 25 150 1\.0 0\.1 8\.0", "BZT52C12 IR at VR 8 V")
    need(l69, r"PGDVOL Output low voltage ISINK = 2 mA 60 150 mV", "LM5069 PGD VOL")
    need(l69, r"PGDIOH Off leakage current VPGD = 80 V 5 [µμ]A", "LM5069 PGD off leakage")
    need(l69, r"During turnon, the Power Good pin \(PGD\) is high until the voltage at VIN increases above", "LM5069 PGD at turn-on")
    need(cs, r"VGS = 4\.5 V, ID = 32 A 1\.2 1\.6 RDS\(on\) Drain-to-source on resistance mΩ VGS = 10 V, ID = 32 A 0\.79 0\.96", "CSD18510Q5B RDS(on)")
    vitn = 0.792
    i_lift0 = (vitn - O.VOL_PGD) / (R143_R12 * 1.01)                 # no sink: the least current that lifts OCH_S2 over VITN
    i_lift1 = i_lift0 + O.ILKG_OD + O.ISENSE                         # RESET1's and SENSE2's printed maxima as sinks
    t_at = lambda i, i25=80e-9: 25.0 + DOUBLING_K * math.log2(i / i25)
    R.update(r12_lift=(i_lift0, i_lift1), r12_t=(t_at(i_lift0), t_at(i_lift1)), q112_site=leak_n,
             bat_ir={"1.5/25": 0.3e-6, "1.5/60": 5.0e-6, "10/25": 0.5e-6, "10/60": 7.5e-6, "50/25": 1.0e-6, "50/60": 15e-6},
             d106_site=O.IR_D106_HOT, r12_level=min(O.VOL_PGD + leak_n * R143_R12 * 1.01, BRK_LEAST_V / 2))
    # approach (1): a small FET pulls OCH_S2 from the crowbar's gate, D106 removed, R143 2.2 MOhm from BRK_PGD: its off leakage sinks
    # OCH_S2's armed level through R143 and BRK_PGD's 0.5 MOhm
    a1_arm = BRK_LEAST_V / 2 - (O.IDSS_HOT + O.ILKG_OD + O.ISENSE) * (0.5e6 + R143_R12 * 1.01)
    a1_need = (BRK_LEAST_V / 2 - O.REL_MAX) / (0.5e6 + R143_R12 * 1.01) - O.ILKG_OD - O.ISENSE
    R.update(a1_arm=a1_arm, a1_t=t_at(a1_need))
    # approach (2): R143 from BRK_PGD lowered with a pull-down Rp, judged leniently (OCH_S2 at D106's 0.55 V while the trip asserts, no
    # sink on the armed level, PGD's VOL taken 0): BRK_PGD over Q106's 2.5 V while D106 pulls needs R143 at least r_min; the armed
    # level over the release needs Rp at least k/(1-k) of (0.5 MOhm + R143); the PGD-low level then tolerates at most i_max of
    # leakage into OCH_S2, largest at R143 = r_min
    v_d = O.VOL + O.VF_D106
    r_min = 0.5e6 * (O.VTH_Q106 - v_d) / (BRK_LEAST_V / 2 - O.VTH_Q106)
    k_ = O.REL_MAX / (BRK_LEAST_V / 2)
    rp_min = k_ / (1 - k_) * (0.5e6 + r_min)
    a2_imax = vitn * (1 / r_min + 1 / rp_min)
    R.update(a2=(r_min, rp_min, a2_imax))
    # approach (3), selected: the levels are the reader's on the composed netlist (section 5, K["levels"]); the PGD leakage basis
    # (the recheck's F6): with the PGD pin's printed 5 uA (at 80 V; a loose bound at 3.8 to 8.4 V) BRK_PGD's released level clears
    # Q106's and Q113's 2.5 V from v_pgd5 up; round 11 armed from about 6.8 V and round 12 from about 8.8 V on it (W153, RECORD)
    R["v_pgd5"] = 2 * (O.VTH_Q106 + 0.5e6 * (5e-6 + 2 * O.IGSS))
    # the start (the recheck's "service at a start"): the start's own current (RECORD l9stk: 0.659 A for 40.7 ms) is under the window;
    # the disarm asserts within the arming delay of PGD's fall plus Q114's gate rise to its 2.5 V maximum threshold through R144 into
    # an ASSUMED 1 nF (Q114's Ciss 50 pF is listed by JSCJ as unverifiable, D107's capacitance is not printed)
    need(prot, r"insertion 4\.23 to 15\.25 ms \(3 to 8 uA\)", "the insertion time (record l9stk)")
    need(prot, r"a start \(the gauge's FET on, a retry, assembly\) \| 0\.659 A at most for 40\.7 ms", "the start's current (record l9stk)")
    g_fin = BRK_LEAST_V - R144 * 1.01 * (O.IDSS_HOT + O.IR_ZENER_HOT)
    t_rise = R144 * 1.01 * 1e-9 * math.log(g_fin / (g_fin - O.VTH_Q106))
    R.update(ins_least=4.23e-3, start_i=0.659, t_rise=t_rise, t_disarm_start=tcts2[1] + t_rise, g_fin=g_fin)
    # the band's upper edge with the loop (the recheck's F2): the most-limit unit's VCL at its limit (PRINTED 61.5 mV), the -1's two
    # FETs in parallel (0.96 mOhm at VGS 10 V and 25 C, PRINTED), Q111 (1.6 mOhm at VGS 4.5 V and 25 C, PRINTED; its gate at 0.82 of
    # BRK_VIN, 7.9 V at the edge) with R140 at +1 %; hot: both FETs at twice those (ASSUMED: TI prints a typical curve only) and 1 mOhm
    # of copper (ASSUMED: the loop is Layer 9's to draw)
    r_fet, r_q111 = 0.96e-3 / 2, 1.6e-3
    edge_cold = R["VCL"][1] * 1e-3 + R["LIM"][2] * (R140 * 1.01 + r_fet + r_q111)
    edge_hot = R["VCL"][1] * 1e-3 + R["LIM"][2] * (R140 * 1.01 + 2 * (r_fet + r_q111) + 1.0e-3)
    R.update(edge=(edge_cold, edge_hot), vcg_edge=edge_cold * R138 / (R138 + R142))
    # E-6b's count (the recheck's F3): with 1 % parts the worst share of nine; Vishay's 70 to 155 C derating applied to the line
    # (INFERRED: the chart states no ambient) gives the part temperature up to which nine hold
    share = (1 / 0.99) / (1 / 0.99 + 8 / 1.01)                     # nine equal parts, one at -1 % and eight at +1 %
    worst = R["p_after"] * share
    line_t = R["crcw"]["w"][2]
    t_nine = 155.0 - 85.0 * worst / line_t
    R.update(share_worst=worst, t_nine=t_nine, derate_air=(155.0 - T_AIR_C) / 85.0)
    # the cycling load (the recheck's F7): Vishay's continuous-pulse line at the bounded on-time, and its average condition (P mean
    # at most the rated dissipation at the ambient: nine parts at P70 1.5 W derated to the air); the least period of a train is the
    # trip's least sense delay plus the arming's least (the turn-off and the re-arm taken 0)
    watts_c, w100_c = crcw2512_single_pulse(1)
    t_min = tcts1[0] + tcts2[0]
    p_rated = 9 * 1.5 * R["derate_air"]
    R.update(cont_line=watts_c(R["t_on_max"]), cont_w100=w100_c, train_tmin=t_min, train_mean=R["e_s"] / t_min,
             train_need=R["e_s"] / p_rated, train_need_src=R["e_v"] / p_rated, p_rated=p_rated, part_band=R["p_stall"] / 9)
    return R


def compose():
    """The draft composed in L4-E9's board P order (this record's breaker and ideal diode at the list's slot, then this round's draft,
    then Layer 6's two tables), read by check_l8p_netlist and check_l8p_och, mutated, and its refusals."""
    out = {}
    with tempfile.TemporaryDirectory() as d:
        seq = D.order("p", "fwd")
        mine = D.mine_seq("p")
        i = max(seq.index(x) for x in mine)
        seq = seq[:i + 1] + [p(RECS["draft"])] + seq[i + 1:]
        gen, res = D.compose("p", seq, d, "och")
        out["steps"] = [(os.path.relpath(s, os.path.join(ROOT, "v2", "docs", "records")), r) for s, (_n, r) in zip(seq, res)]
        if any(not r.startswith("OK") for _n, r in res) or len(res) != len(seq):
            refuse("the composition stopped: %s" % res)
        rc, net, table = D.netlist_text("p", gen, d, "och")
        if rc:
            refuse("board P's generator stopped on the composition: %s" % net)
        nl = C.read_netlist(open(net, "rb").read())
        out["parts"] = len(nl["comps"])
        kit, verdicts = C.run({"p": net}, out=open(os.devnull, "w"))
        out["l8p"] = verdicts["p"]
        lines = []
        _v, lines = C.judge("p", nl)
        out["l8p_lines"] = lines
        out["och"] = O.judge(nl)["OCH"]
        out["win_drawn"] = O.window(nl)
        out["delays"] = O.delays(nl)
        out["levels"] = O.bound_levels(nl)
        muts = []
        for name, ops in MUTATIONS:
            q = D.mutate_ops(net, d, "m%d" % len(muts), ops)
            v, why = O.judge(C.read_netlist(open(q, "rb").read()))["OCH"]
            muts.append((name, v, why[0] if why else ""))
        out["muts"] = muts
        # refusals: without the breaker and the ideal diode; a second time; the repository's own generator
        bare = os.path.join(d, "bare_gen_sch_p.py")
        shutil.copy(D.GEN["p"], bare)
        r1 = subprocess.run([sys.executable, "-B", p(RECS["draft"]), bare], capture_output=True)
        r2 = subprocess.run([sys.executable, "-B", p(RECS["draft"]), gen], capture_output=True)
        r3 = subprocess.run([sys.executable, "-B", p(RECS["draft"]), D.GEN["p"], "--write"], capture_output=True)
        out["refusals"] = [(r1.returncode, (r1.stderr.decode().strip().splitlines() or [""])[-1][:90]),
                           (r2.returncode, (r2.stderr.decode().strip().splitlines() or [""])[-1][:90]),
                           (r3.returncode, (r3.stderr.decode().strip().splitlines() or [""])[-1][:90])]
        out["net_sha"] = sha(net, 16)
    return out


MUTATIONS = (
    ("the crowbar's resistor on BRK_VIN, upstream of the sense pair (the breaker could never end it)", [("move", "R140", "1", "BRK_VIN")]),
    ("the amplifier's input and reference exchanged (R132 from PACK_N, R134 from GND)", [("move", "R132", "1", "PACK_N"), ("move", "R134", "1", "GND")]),
    ("RESET1 on UVLO instead of the arming FET (a sink on UVLO; a retry, not the -1's latch)", [("move", "U107", "4", "BRK_UVLO")]),
    ("the arming on BRK_VIN instead of PGD (the crowbar armed at power-up)", [("move", "U107", "3", "BRK_VIN")]),
    ("the crowbar at 2 Ohm (its own current under the breaker's most limit)", [("value", "R140", "2.0R 1% 2512")]),
    ("the sense delay capacitor removed", [("drop", "C119")]),
    ("the crowbar's gate clamp removed", [("drop", "D105")]),
    ("the gain at 10 kOhm (the window off)", [("value", "R133", "10.0k 0.1% 25ppm")]),
    ("the crowbar's drain on DOCK_EN_OUT (a sink on the enable loop)", [("move", "R140", "2", "DOCK_EN_OUT")]),
    # round 12 (the check's F3 and F2): the values the window and the delays are now read from, and the on-time bound
    ("R10 at 1 mOhm (round 12: the window read from R10's drawn value, about 40 to 43 A)", [("value", "R10", "1m 2512 2W (sense)")]),
    ("R135 at 1 MOhm (round 12: SENSE1's input current through it moves the window)", [("value", "R135", "1M")]),
    ("C117 at 100 nF (round 12: SENSE1's filter over its share of the sense delay)", [("value", "C117", "100n 50V C0G (SENSE1's filter)")]),
    ("C120 at 47 nF (round 12: round 11's value, the on-time past R140's figure)", [("value", "C120", "47n 50V C0G 5% (CTS2)")]),
    ("D106 removed (round 12: the on-time bound lost)", [("drop", "D106")]),
    ("R143 at 100 kOhm (round 12: BRK_PGD under Q106's threshold; round 13: D106's current past its 0.1 mA row)", [("value", "R143", "100k 1%")]),
    ("SENSE2 back on BRK_PGD (round 12: round 11's arming, no on-time bound)", [("move", "U107", "3", "BRK_PGD")]),
    # round 13 (the recheck's F1): the PGD-low level under leakage, the pull-down's gate, a shorted D106, a resistor back on BRK_PGD
    ("round 12's drawing (R143 2.2 MOhm from BRK_PGD, Q114 removed: OCH_S2 lifted by leakage while PGD is low)",
     [("move", "R143", "1", "BRK_PGD"), ("value", "R143", "2.2M 1%"), ("drop", "Q114")]),
    ("Q114 removed (round 13: OCH_S2 not held low while PGD is low)", [("drop", "Q114")]),
    ("R144 at 1 MOhm (round 13: Q114's gate under 5 V with Q113's and D107's leakage at the site)", [("value", "R144", "1M 1%")]),
    ("D106 shorted (round 13: RESET1's node merged into OCH_S2)",
     [("move", "U107", "4", "OCH_S2"), ("move", "Q112", "2", "OCH_S2"), ("move", "D106", "1", "OCH_S2")]),
    ("R143 on BRK_PGD at 330 kOhm (round 13: a resistor of the trip on BRK_PGD again)", [("move", "R143", "1", "BRK_PGD")]),
)


def fmt(x, n=2):
    return ("%%.%df" % n) % x


def render(R, K):
    W = R["W"]
    o = []
    w = o.append
    I, T_AIR = W["I"], W["T_AIR"]
    lo, hi = R["win"]
    w("l8p_cprot: record l8p round 11, Layer 4 register row (c): L8P-R10-F1 as a design choice, L4A-67 (C-PROT rev 1 for the guard on the")
    w("corrected circuit) and L4A-68 (the guard's allowance for its consumers) (MESHSAT-1357, 7 October 2026). Desk arithmetic on the makers'")
    w("printed figures and the records' own; nothing was built, bought or measured. LABELS: PRINTED; TYPICAL (never a limit); READING;")
    w("INFERRED; MODEL; RECORD; ASSUMED.")
    w("")
    w("0. PINS (sha256/16)")
    for s_, rel in R["pins"]:
        w("   %s  %s" % (s_, rel))
    w("")
    w("1. THE FINDING AND THE CASE (RECORD)")
    w("   L8P-R10-F1 (record l8p round 10, l8p_rowc.out 3a, computed again here by l8p_rowc.py): at the breaker's held %s A from %s C the three" % (fmt(I), fmt(T_AIR)))
    w("     25 A MINI blades (P's F1, E's F3, A's F1; Littelfuse 297) carry %s %% of their printed rerated current (%s A at the air, %s A at the" % (
        fmt(100 * I / W["I_rr_air"], 1), fmt(W["I_rr_air"]), fmt(W["I_rr_band"])))
    w("     band's %s C): OVER by %s A; the 18 A service is %s %% of it: within" % (fmt(W["t_band_a"]), fmt(W["over_air_a"]), fmt(100 * W["f_18"], 1)))
    w("   the case: C-PROT rev 1 (the breaker's band %s to %s A held from %s C, board P's FETs welded, no firmware, 10 A held and 18 A for 60 s" % (
        fmt(R["LIM"][0]), fmt(R["LIM"][2]), fmt(T_AIR)))
    w("     never interrupted; record l9stk's condition C4: an indicated 18 A may be a true %s A)" % fmt(SERVICE_TRUE))
    w("   what may not move (the brief, constitution 4): no protection lowered, not the 18 A service, no printed rating's margin")
    w("")
    w("2. THREE APPROACHES ON PRINTED FIGURES (constitution section 4: at most three, materially different)")
    w("   (A) A FUSE OR A HOLDER ARRANGEMENT THAT CARRIES %s A ON ITS PRINTED RERATING" % fmt(I))
    w("     a 25 A element needs a printed rerating of at least %s at %s C (and at the band's %s C); the held MINI 297 prints %s and %s" % (
        fmt(R["need_f"], 4), fmt(T_AIR), fmt(W["t_band_a"]), fmt(R["f_air"], 4), fmt(R["f_band"], 4)))
    w("       (READING of its line); no other maker's sheet held or read prints a 25 A element at or above it: NOT AVAILABLE ON PRINTED FIGURES")
    w("     a 30 A element (0297030) carries it on its own row (%s A rerated at the air), but the copper was sized and coordinated at the 25 A" % fmt(R["b30"]))
    w("       blade (record l9stk 14.4 to 14.6): the 30 A blade's 135 %% to 200 %% band runs from %s A to 60 A for up to 600 s, and the bands'" % fmt(R["b30_135"]))
    w("       steady reading at 60 A, scaled by the current squared from the record's own 50 A row (%s C), is %s C over board A's %s C and" % (
        fmt(R["CU50"]), fmt(R["cu60"], 1), fmt(R["band_pinned"][0], 0)))
    w("       board E's %s C with the plating pinned: a protection lowered: REFUSED (round 10's (a)); the copper's weight is the open OWNER" % fmt(R["band_pinned"][1], 0))
    w("       DECISION (L9STK CU), not this record's to move")
    w("     a holder or busbar that cools the blade: Littelfuse's rerating curve is drawn against the AMBIENT temperature (READING of its axis);")
    w("       no printed figure of the 297 sheet or the 3568's credits a holder or busbar with a lower blade temperature, and the 76.25 C air")
    w("       is every blade's ambient inside the sealed case: NO PRINTED BASIS")
    w("     verdict (A): NOT SUPPORTED on printed figures")
    w("   (B) A HELD-OVERCURRENT TRIP ON BOARD P THAT ENDS IN THE -1'S OWN LATCH (apply_gen_sch_p_ocheld.py; section 4)")
    w("     the held current is ended over a window of %s to %s A (printed maxima; R10 as the record assumes it, E-6), inside %s A (the" % (fmt(lo), fmt(hi), fmt(SERVICE_TRUE)))
    w("       service's true current, C4) and %s A (the blades at the band); above it a single event per recovery, the -1's own" % fmt(O.BLADE_BAND))
    w("     verdict (B): SUPPORTED on printed figures, CONDITIONAL as section 4 names")
    w("   (C) A CONTROLLER WITH A TIGHTER PRINTED CURRENT-LIMIT SPREAD (TI LM5066I, SNVS950C, the record's E-5 fallback)")
    w("     its VCL at CL = GND %s to %s mV (PRINTED, -40 to 125 C) with RS's window spread %s (record l9stk 15.4): the least kept at %s A" % (
        fmt(R["V66"][0], 0), fmt(R["V66"][1], 0), fmt(R["rs_spread"], 4), fmt(R["LIM"][0])))
    w("       gives a most of %s A: under the air's %s A by %s A, OVER the band's %s A; at the service's true %s A the most is %s A, over both" % (
        fmt(R["c_most_1832"]), fmt(W["I_rr_air"]), fmt(W["I_rr_air"] - R["c_most_1832"]), fmt(W["I_rr_band"]), fmt(SERVICE_TRUE), fmt(R["c_most_1880"])))
    w("     its recommended VIN starts at %s V, %s V under the pack's least %s V; and it replaces the whole breaker of record l9stk 15.4 to 15.6" % (
        fmt(R["VIN66"], 1), fmt(PACK_LEAST - R["VIN66"], 1), fmt(PACK_LEAST, 1)))
    w("       (its power limit, timer, SOA, latch and the drafts of rounds 1 to 4)")
    w("     verdict (C): NOT SELECTED (fails the band reading and C4's service current on printed figures; the largest redesign of the three)")
    w("")
    w("3. THE SELECTION (SESSION, decision L8P-R11-D1): (B)")
    w("   why: the one approach that ends every held current under the blades' printed rerated current at both readings without moving the")
    w("     breaker, the copper, the 18 A service or any printed margin; it adds a protection and lowers none; every part type is in the kit")
    w("   END CONDITION (any one): (1) R10's maker sheet (E-6) reads a tolerance with its temperature coefficient over 130 K outside %s to %s %%;" % (
        fmt(100 * R["r10_room"][0], 1), fmt(100 * R["r10_room"][1], 1)))
    w("     (2) Layer 6 finds no R140 whose maker prints a single pulse of at least %s J in %s ms (round 12, 4c'; 0.40 J in 1.4 ms in round 11);" % (
        fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("     (3) a check of this round finds a held current over %s A, a trip at or under %s A, or a crowbar event that ends neither in" % (
        fmt(O.BLADE_BAND), fmt(SERVICE_TRUE)))
    w("     the -1's latch nor within the on-time bound (round 12), and a second negative check of the same trip follows; then (C) with its")
    w("     band reading resolved, or the blades' evidence route (round 10's (c)) as the supplier's")
    w("")
    w("4. THE TRIP ON PRINTED FIGURES (B)")
    w("   4a. THE WINDOW (INFERRED on PRINTED rows; R10 ASSUMED): OCH_A = %s x I x R10 (U106 inverting, R133 over R132); U107's VITP %s to %s V" % (
        fmt(G_RF / G_RIN, 1), fmt(O.VITP[0], 3), fmt(O.VITP[2], 3)))
    w("     (TI SNVSBJ1E 7.5, -40 to 125 C); R132 and R133 at 0.1 %% and 25 ppm/K over 100 K; OPA187's VOS %s uV in all (10 uV, 0.015 uV/C over" % fmt(O.VOS * 1e6, 1))
    w("     100 K, CMRR 126 dB at VCM V-), IB 7.5 nA, U107's ISENSE 100 nA through R135; R10 2 mOhm at 1 % and 75 ppm/K over 130 K (ASSUMED,")
    w("     record l8p 12c; no maker's sheet held, E-6): the held current is ended from %s A at the least to %s A at the most" % (fmt(lo, 3), fmt(hi, 3)))
    w("     (round 12, the check's F3: check_l8p_och.py reads R10's, R132's, R133's and R135's DRAWN values into this window and C117's,")
    w("     C119's and C120's into the delays; round 11 read R132 and R133 only, so R10 at 1 mOhm or R135 at 1 MOhm still read DRAWN)")
    w("     margins: %s A over the service's true %s A; %s A under the blades' %s A at the band (%s A under %s A at the air)" % (
        fmt(lo - SERVICE_TRUE), fmt(SERVICE_TRUE), fmt(O.BLADE_BAND - hi), fmt(O.BLADE_BAND), fmt(W["I_rr_air"] - hi), fmt(W["I_rr_air"])))
    w("     robustness: the window stays inside both while R10 reads within %s %% to +%s %% (the record assumes +-%s %%)" % (
        fmt(100 * R["r10_room"][0], 1), fmt(100 * R["r10_room"][1], 1), fmt(100 * R["r10_assumed"], 2)))
    w("     OCH_A in the service: %s V at 10 A, %s V at 18 A, %s V at the true %s A: under the least %s V" % (
        fmt(R["out_10"], 3), fmt(R["out_18"], 3), fmt(R["out_service"], 3), fmt(SERVICE_TRUE), fmt(O.VITP[0], 3)))
    w("   4b. THE DELAYS (TI's Equations 5 and 6, C0G at 5 %%; the no-capacitor least not printed, taken 0): the trip's sense delay %s to %s ms," % (
        fmt(R["tcts1"][0] * 1e3, 3), fmt(R["tcts1"][1] * 1e3, 3)))
    w("     longer than E-10's %s ms excursions (record l9stk 15.7: the key-down current's excursions above %s A each under it), so the trip," % (
        fmt(R["e10"] * 1e3, 3), fmt(R["LIM"][0])))
    w("     whose least is over %s A, is never more sensitive than the breaker's least unit INSIDE E-10's bound (E-10 is a bench item: an" % fmt(R["LIM"][0]))
    w("     excursion over the window lasting from %s ms up to the -1's own timer would be ended by the trip where the breaker alone" % fmt(R["tcts1"][0] * 1e3, 3))
    w("     would ride it out; the check's F7: E-10 is a condition of L8P-R11-D1); the arming's delay after PGD falls OR THE TRIP ASSERTS")
    w("     %s to %s ms (C120 22 nF C0G since round 12; round 11's 47 nF gave 4.60 to 8.36 ms after PGD's fall only)" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["tcts2"][1] * 1e3, 2)))
    w("   4c. THE CROWBAR INTO THE -1'S LATCH: R140 %s Ohm and Q111; its own current %s A at %s V, %s A at %s V, %s A at the %s V clamp," % (
        fmt(R140, 2), fmt(R["ic_least"], 1), fmt(PACK_LEAST, 1), fmt(R["ic_16"], 1), fmt(PACK_MOST, 1), fmt(R["ic_clamp"], 1), fmt(CLAMP, 1)))
    w("     each over the breaker's most limit %s A WHATEVER THE LOAD: U101 enters its current limit (its circuit breaker from %s A) and the" % (
        fmt(R["LIM"][2]), fmt(R["CB"][0])))
    w("     fault timer latches the -1 off, clearing %s ms at most from the limit's onset plus tCL (%s us typical, no maximum: RECORD, l9stk" % (
        fmt(R["CLEAR"] * 1e3, 3), fmt(R["TCL_TYP"] * 1e6, 0)))
    w("     prot 3): the row 'an overload over the unit's limit' (%s W for %s ms against %s W derated: %s) and, from %s A, the hot-short" % (
        fmt(R["PULSE"][0]), fmt(R["PULSE"][1], 3), fmt(R["PULSE"][2], 1), fmt(R["PULSE"][3]), fmt(R["CB"][0])))
    w("     row's release in 16.5 us; the crowbar's peak with the most limit's load %s A at %s V, %s A at the clamp, under the %s A where VIN to" % (
        fmt(R["peak_16"], 1), fmt(PACK_MOST, 1), fmt(R["peak_clamp"], 1), fmt(R["VSNS_I"], 1)))
    w("     SENSE passes its 0.3 V: no row of record l9stk 15.6 is newly reached; ONCE per recovery (redocking, an input's return, the guard's")
    w("     cycle: the -1's own); no retry train")
    w("     the gate: Q111's Qg(4.5 V) 75 nC at most through R142 from BRK_VIN at %s V: %s us; the event from the held current's onset at most" % (
        fmt(PACK_LEAST, 1), fmt(R["t_gate"] * 1e6, 1)))
    w("       %s ms (the trip's delay, the gate, the clearing) plus tCL; PGD falls only when VDS passes %s to %s V (RECORD); the arming's" % (
        fmt(R["t_event"] * 1e3, 3), fmt(R["PGD_VDS"][0], 2), fmt(R["PGD_VDS"][1], 2)))
    w("       least delay, now counted from the trip's assertion (round 12), %s ms, leaves %s ms for tCL past the gate and the clearing" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["arm_margin"] * 1e3, 2)))
    w("       (tCL 45 us TYPICAL, no maximum printed: the 50 us taken is RECORD, the check's F12): the crowbar stays until the latch")
    w("     R140's single pulse WITHOUT A SOURCE (INFERRED): PACK_P under the limit at most %s V (the most limit through R140 alone), %s W" % (
        fmt(R["vlim"], 2), fmt(R["p_lim"], 0)))
    w("       for %s ms plus tCL (50 us, RECORD: 45 us TYPICAL, no maximum printed; the check's F12): %s J; the kit's %s uF on PACK_P from" % (
        fmt(R["CLEAR"] * 1e3, 3), fmt(R["e_lim"], 3), fmt(593, 0)))
    w("       %s V: %s J; the onset at the clamp, the crowbar's peak with the most limit's load for 16.5 us (an overcount: the load's current" % (
        fmt(R["vlim"], 2), fmt(R["e_cap"], 3)))
    w("       does not pass R140): %s J (round 11 printed 'under 0.003 J' beside this same arithmetic: corrected); %s J in all: ROUND 11'S" % (
        fmt(R["e_spike"], 3), fmt(R["e_n"], 2)))
    w("       FIGURE, which left out a source's share (the check's F1) and the band of 4i (F2): restated in 4c' and 4i")
    w("   4c'. A SOURCE'S SHARE (round 12, the check's F1; C-PROT rev 1: each source present or absent)")
    w("     the path that holds VSYS (RECORD, L4-E9's power edges): P06 the entry to VIN_RAW, P07 VIN_RAW into the front end U2, P10 the")
    w("       charger U3 onto VSYS, P11 VSYS through the battery FETs, R17 and A's F1 to the pack: THE CHARGER holds VSYS; board E's entry")
    w("       (its overcurrent 6.364 to 7.136 A, its short-circuit 10.36 to 13.87 A) acts on VIN_RAW two conversions upstream, so its")
    w("       thresholds bound VIN_RAW's current, not the current a source pushes from VSYS into PACK_P (round 11's 4e and the check's")
    w("       estimate read them as VSYS's: WITHDRAWN as the path's reading)")
    w("     the charger's printed figures are regulations: the pre-charge clamp at 384 mA +-25 % (PRINTED, IPRECHRG_REG_ACC, 0 to 85 C:" )
    w("       at most %s A) acts only while a charge is commanded and VBAT is under VSYS_MIN; its cycle-by-cycle comparators (VOCP_lim) print" % fmt(R["pre_max"], 2))
    w("       a typical only; neither its loops nor the front end's ISNS loop print a settling time. SETTLED, on the record's B-R2 basis")
    w("       (L4-E11: the charger holds a resistive load on the pack side at sqrt(P x R) with the front end's %s W, RECORD), a source alone" % fmt(R["p_src"], 0))
    w("       holds R140 at %s V, %s A; INSIDE THE EVENT no printed figure bounds its current, so R140 is bounded on VOLTAGE:" % (
        fmt(R["v_settled"], 2), fmt(R["i_settled"], 1)))
    w("       while the -1 conducts PACK_P is under BRK_VIN (at most %s V: %s W in R140 at its least), once latched at most VSYS's %s V" % (
        fmt(PACK_MOST, 1), fmt(R["p_on"], 0), fmt(R["vsys_max"], 3)))
    w("       (RECORD, L4-E11 12c: %s W), for the crowbar's on-time, which 4i bounds" % fmt(R["p_after"], 0))
    w("     the turn-off (round 12 adds Q110's own, left out in round 11): tCTR1 40 us PRINTED, Q110's gate through R136 %s ms (twice its" % fmt(R["t_q110"] * 1e3, 3))
    w("       TYPICAL Ciss, ASSUMED: no maximum printed), Q111's gate through R138, five time constants of its PRINTED 11.4 nF: %s ms in all" % fmt(R["t_off"] * 1e3, 3))
    w("     R140's single pulse, each case (INFERRED; the time from the trip's assertion):")
    w("       no source, the -1 latched (round 11, above)                                   %s J in %s ms" % (fmt(R["e_n"], 3), fmt((R["t_gate"] + R["CLEAR"] + TCL_RECORD) * 1e3, 3)))
    w("       a source present, the -1 latched                                              %s J in %s ms" % (fmt(R["e_n_src"], 3), fmt((R["t_gate"] + R["CLEAR"] + TCL_RECORD + R["t_off"]) * 1e3, 3)))
    w("       no source, the band of 4i, ended by the on-time bound                         %s J in %s ms" % (fmt(R["e_s"], 3), fmt(R["t_on_max"] * 1e3, 3)))
    w("       a source present, the -1 held out of its limit, ended by the on-time bound    %s J in %s ms" % (fmt(R["e_w"], 3), fmt(R["t_on_max"] * 1e3, 3)))
    w("       the voltage bound throughout (round 13, the recheck's F3: ONE basis)          %s J in %s ms" % (fmt(R["e_v"], 3), fmt(R["t_on_max"] * 1e3, 3)))
    w("       E-6b RESTATED (round 12) ON ONE BASIS (round 13): VSYS's most %s V on R140 at its least for the whole bounded on-time, %s W" % (
        fmt(R["vsys_max"], 3), fmt(R["p_after"], 0)))
    w("       held and %s W for 16.5 us at the clamp: a part whose maker prints a single pulse of at least %s J in %s ms (round 12's 3.32 J" % (
        fmt(R["p_peak"], 0), fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("       took PACK_P at most 16.8 V while the -1 conducts beside a 782 W held figure, two bases: replaced by this one);")
    w("       round 11's 0.40 J in 1.4 ms is withdrawn. A NAMED PART (Layer 6 selects): Vishay's CRCW2512-HP e3 pulse proof chip (1 Ohm")
    w("       to 1 MOhm, P70 1.5 W), its single-pulse line READ from its vector path (document 20043, page 5; the curve's own conditions: no")
    w("       preload, under 1000 pulses, the pulse voltage under its limit; its long-pulse end %s W at 100 s meets the printed 1.5 W row);" % fmt(R["crcw_w100"], 2))
    w("       n equal parts in parallel each carry 1/n of R140's power:")
    for k, lab in (("n", "no source, the -1 latched"), ("nsrc", "a source present, the -1 latched"), ("s", "no source, the band of 4i"),
                   ("w", "a source present, the -1 held out of its limit"), ("peak", "the onset at the clamp")):
        pw, t_, rd, n_ = R["crcw"][k]
        w("         %-48s %6s W for %8s ms against the line's %7s W: %d part%s" % (lab, fmt(pw, 0), fmt(t_ * 1e3, 4), fmt(rd, 1), n_, "" if n_ == 1 else "s"))
    w("       so the restated pulse needs %d of them in parallel (each %s Ohm for %s Ohm), a power package whose maker prints the pulse, or" % (
        R["crcw_n"], fmt(R140 * R["crcw_n"], 2), fmt(R140, 2)))
    w("       E-12s's reading of a source's settling narrowing the bound (the chart states no ambient: the line's temperature basis at")
    w("       the 76.25 C air is Layer 6's question to Vishay); until Layer 6 selects, R140 stays CONDITIONAL on E-6b")
    w("       THE COUNT'S BASIS (round 13, the recheck's F3): nine at the line's own basis (no ambient stated) with equal shares; with 1 %")
    w("         parts the worst share is %s W against the line's %s W at %s ms; Vishay's 70 to 155 C derating applied to the line (INFERRED)" % (
        fmt(R["share_worst"], 1), fmt(R["crcw"]["w"][2], 1), fmt(R["t_on_max"] * 1e3, 2)))
    w("         holds nine to a part temperature of %s C (%s of the line at the %s C air); above it ten or more: Layer 6 states the part's" % (
        fmt(R["t_nine"], 1), fmt(R["derate_air"], 3), fmt(T_AIR_C, 2)))
    w("         own temperature with the count")
    w("     Q111 (CSD18510Q5B, PRINTED): IDM 400 A against %s A at the onset and %s A held with a source; VDS 40 V against PACK_P's %s V" % (
        fmt(R["peak_clamp"], 1), fmt(R["i_q111_src"], 1), fmt(CLAMP, 1)))
    w("       clamp; VGS 20 V against D105's 12.7 V; its own turn-off crosses at most V^2/4R: %s W without a source (at %s V), WITHIN the" % (
        fmt(R["p_q111_off_nosrc"], 1), fmt(R["v_force"], 2)))
    w("       record's derated %s W of the same part at %s ms (l9stk 15.6) for at most %s ms; %s W on the settled source basis, WITHIN;" % (
        fmt(R["PULSE"][2], 1), fmt(R["PULSE"][1], 3), fmt(R["t_q111_off"] * 1e3, 3), fmt(R["p_q111_off_settled"], 1)))
    w("       %s W on the voltage bound with a source: NOT SHOWN (its SOA at %s ms or less is not read: CONDITIONAL, with E-2 and E-3)" % (
        fmt(R["p_q111_off"], 0), fmt(R["t_q111_off"] * 1e3, 2)))
    w("   4d. THE ARMING AND THE GATE DRIVE (PRINTED limits; leakages ASSUMED to double every 10 K at the record's %s C site)" % fmt(SITE))
    w("     Q110 (AO3401A) driven at VGS -%s V at %s V to -%s V at the clamp (R136 over R137), against its +-12 V and its -2.5 V RDS(on) row" % (
        fmt(R["vgs110"][0], 2), fmt(PACK_LEAST, 1), fmt(R["vgs110"][1], 2)))
    w("     Q110 held off: RESET1's 300 nA and Q112's off leakage %s uA through R136: %s V, under its least threshold %s V" % (
        fmt(R["leak_n"] * 1e6, 2), fmt(R["v_off110"], 3), fmt(R["vth_p"], 1)))
    w("     the crowbar held off: Q110's off leakage %s uA (5 uA at 55 C PRINTED) through R138: %s V (%s V at a 101 C site), under Q111's least" % (
        fmt(R["leak_p"] * 1e6, 1), fmt(R["v_cg_off"], 3), fmt(R["v_cg_off101"], 3)))
    w("       threshold %s V (25 C row; the threshold falls with temperature, TYPICAL Figure 6: a layout condition keeps both off the pad)" % fmt(R["vth_csd"], 1))
    w("     U107's RESET1 sinks at most %s mA and RESET2 %s mA (TI recommends 5 mA); U107's VDD and SENSE at most %s V against 65 V;" % (
        fmt(R["ireset1"] * 1e3, 3), fmt(R["ireset2"] * 1e3, 3), fmt(CLAMP, 1)))
    w("       Q112's gate at most %s V against 20 V; OCH_CG under D105's %s V; R142 and D105 carry at most %s mA for the event" % (
        fmt(R["vgs112"], 1), fmt(R["vcg"], 1), fmt(R["iz"] * 1e3, 1)))
    w("   4e. POWER-UP, THE START AND A LATCHED BREAKER: U107 holds RESET1 and RESET2 asserted for tSD (2 ms at most) and RESET2 while PGD is")
    w("     low (round 12: or while RESET1 is asserted, through D106; round 13: OCH_S2 held low by Q114 while PGD is low, 4j: round 12's")
    w("     2.2 MOhm node let leakage lift it), so Q112 is off and the crowbar disarmed whenever the breaker is not")
    w("     running: at a gauge's wake, at a docking (the RC hold's 0.110 s and the start), during a start (PGD low while VDS is high), once")
    w("     latched, and %s ms at most after the trip asserts (4i); the trip touches neither the enable loop nor" % fmt(R["tcts2"][1] * 1e3, 2))
    w("     UVLO (check_l8p_och's APART): L4-E11 20c's window, its readings and the RC hold's 0.110 to 0.907 s are unchanged")
    w("     EACH SOURCE PRESENT OR ABSENT (C-PROT rev 1): with a source holding VSYS and board A's battery FETs on, the crowbar also loads the")
    w("       source through those FETs, CELL+, the dock and the lead, for the event and the crowbar's turn-off after the latch (%s ms," % fmt(R["t_off"] * 1e3, 2))
    w("       4c'), %s ms at most when the -1 latches, %s ms at most when it does not (4i); that current returns through board A's ground," % (
        fmt(R["t_src"] * 1e3, 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("       not R10, so it never holds the trip; THE CHARGER holds VSYS (L4-E9's P10, 4c'): board E's entry (overcurrent %s to %s A," % (
        fmt(R["ENTRY"][0], 3), fmt(R["ENTRY"][1], 3)))
    w("       short-circuit %s to %s A, record l4e11 3c, RECORD) meets it only through the front end and the charger, two conversions" % (
        fmt(R["ENTRY"][2], 2), fmt(R["ENTRY"][3], 2)))
    w("       upstream (round 11 read it as a short on VSYS: corrected); the source's share and R140's pulse are 4c''s; the battery FETs")
    w("       carry at most that source current, reversed, inside their held rows; afterwards a charge through the latched")
    w("       breaker's body diodes is route R1's (round 3: the detector holds the return, board A's inhibit sets), as after any latch")
    w("     THE GAUGE: R10 carries the event, so the gauge's AFE reads it as it reads any short on PACK_P (IF-6); its levels are unchanged")
    w("       (IF-4), and if its ASCD acts Q2 opens behind the latched breaker; the gauge's recovery is the battery stream's")
    w("   4f. THE STANDING CURRENT from BRK_VIN: U106 %s uA, U107 %s uA, R139 with R141 %s uA at %s V (PRINTED maxima): beside the detector's" % (
        fmt(R["stand"][0] * 1e6, 0), fmt(R["stand"][1] * 1e6, 1), fmt(R["stand"][2] * 1e6, 1), fmt(PACK_MOST, 1)))
    w("     0.47 mA (record l8p round 3), a standby load on the pack for the battery stream; round 13 adds R144 %s uA while PGD is high or" % fmt(PACK_MOST / (R144 * 0.99) * 1e6, 0))
    w("     R143 %s uA while PGD is low (at %s V): the trip's standing current at most %s mA" % (
        fmt(PACK_MOST / (R143 * 0.99) * 1e6, 0), fmt(PACK_MOST, 1),
        fmt((150e-6 + 2.6e-6 + PACK_MOST / (R139 + R141) + max(PACK_MOST / (R144 * 0.99), PACK_MOST / (R143 * 0.99))) * 1e3, 3)))
    w("   4g. ITS OWN SINGLE FAILURES (INFERRED from the circuit as drawn):")
    for a, b in FAILS:
        w("     %-52s %s" % (a, b))
    w("     so a latent first failure returns the design to round 10's rows at %s A held (the blades at %s %% of their rerated current, no part" % (
        fmt(I), fmt(100 * I / W["I_rr_air"], 1)))
    w("       the guard protects exposed: M-A holds the FETs at %s A on a board whose path meets E-1's bar); no automatic diagnostic is" % fmt(I))
    w("       drawn and THE TRIP'S SILENT FAILURES HAVE NO DETECTION INTERVAL beyond E-12f at commissioning and at each service: L4A-67's")
    w("       acceptance ('fails on any latent first failure left without its interval') reads NOT MET on that clause (the check's F6);")
    w("       an automatic test is REMAINING ENGINEERING with HO-A's pattern")
    w("     Q110 OR Q111 SHORTED WITH A SOURCE (the check's F11): the -1 latches (found at the next start); while a source holds VSYS with")
    w("       the battery FETs on when the failure comes, CELL+ stays tied to VSYS and the charger holds R140 as a resistive load: on the")
    w("       record's settled B-R2 basis %s V, %s A, %s W held (L4-E11: the DD-7 inhibit sets only under %s V on CELL+, and does not here)," % (
        fmt(R["v_settled"], 2), fmt(R["i_settled"], 1), fmt(R["p_src"], 0), fmt(R["inh_v"], 2)))
    w("       until R140 opens (then the crowbar's open failure, latent, as the second row) or the source goes; the charger's pre-charge")
    w("       clamp (at most %s A, PRINTED) holds it under %s W only while a charge is commanded with VBAT under VSYS_MIN, which nothing" % (
        fmt(R["pre_max"], 2), fmt(R["pre_max"] ** 2 * R140 * 1.01, 3)))
    w("       drawn forces; when the failure precedes the source, CELL+ is dead, the DD-7 inhibit holds the battery FETs off and only their")
    w("       off leakage flows. FINDING L8P-R12-F1 (new, OPEN; the record's B-R2 state with R140 as its resistive fault): smallest")
    w("       corrections for the next round, none drafted here: a series element whose maker's curve passes the event's pulse and opens")
    w("       the held %s A inside R140's printed short-time rating (chosen with R140's part, E-6b), or route R1's blocking element" % fmt(R["i_settled"], 1))
    w("   4h. A FINDING ON THE DRAWN UVLO NODE (L8P-R11-F1, this record's own C-1b of round 2; OPEN; not this round's circuit, which adds")
    w("     nothing on UVLO): below its threshold U101 sinks UVLOHYS, 12 to 30 uA PRINTED, so at a start H settles under R104 with that sink and")
    w("     every off leakage on BRK_UVLO; record l9stk counts the sink alone (H %s V at %s V, R104 nominal). Q104's and Q105's drains sit on BRK_UVLO: at" % (
        fmt(R["uvlo_sink_only"][0], 2), fmt(PACK_LEAST, 1)))
    w("     the 2N7002's 80 nA at 25 C (PRINTED) doubled every 10 K (ASSUMED, the record's own rule), R104 +1 %, D102's 0.715 V and UVLOTH's")
    w("     2.55 V (RECORD): at %s V UVLO reaches %s V with both at the 76.25 C air (%s V of margin) and %s V at the %s C site: NOT RELEASED;" % (
        fmt(PACK_LEAST, 1), fmt(R["uvlo_air"][1], 2), fmt(R["uvlo_air"][1] - 2.55, 2), fmt(R["uvlo_site"][1], 2), fmt(SITE)))
    w("     the release at the pack's least fails above a site of %s C on that rule: a docking with board P warm and the pack low would not" % fmt(R["uvlo_t"], 1))
    w("     start the breaker (the service, not a protection). Smallest corrections, for this record's next round (none drafted here): R104")
    w("     lowered with C103 raised to keep the hold's 0.110 to 0.907 s, or inverters whose maker prints the hot off leakage, or both;")
    w("     evidence: Q104's and Q105's IDSS at 86.25 and 101 C on board P's specimen (E-12's bench)")
    w("     IT ALSO STRETCHES THE RC HOLD (the check's F8; the same rule, INFERRED): BRK_H settles at %s V at the 76.25 C air against the" % fmt(R["uvlo_air"][0], 2))
    w("       3.265 V the release needs, so the hold takes %s s (R104 +1 %%, C103 +10 %%), against the %s s the record's sink-only figure" % (
        fmt(R["hold_air"], 2), fmt(R["hold_sink_only"], 3)))
    w("       gives and L4-E11's DD-7 restart timeline (at most 1.149 s) uses: an affected output of L8P-R11-F1 (L4-E11 20d's timeline")
    w("       and record l9stk's 0.110 to 0.907 s); never released at the %s C site" % fmt(SITE))
    w("   4i. THE BRK_VIN RANGE AND THE ON-TIME BOUND (round 12, the check's F2)")
    w("     the event can happen from BRK_VIN %s V (C-PROT rev 1: the -1 runs from its power-on threshold, record l8p 12d; PORIT %s V is" % (
        fmt(R["v_floor"], 1), fmt(7.6, 1)))
    w("       a TYPICAL with an 8 V maximum and no minimum printed) to the pack's %s V, the clamp's %s V in a surge" % (fmt(PACK_MOST, 1), fmt(CLAMP, 1)))
    w("     from %s V up (the most limit through R140 at +1 %%; round 13, the recheck's F2: about %s to %s V with the loop, below) the" % (
        fmt(R["v_force"], 2), fmt(R["edge"][0], 2), fmt(R["edge"][1], 2)))
    w("       crowbar's own current exceeds every unit's limit: the -1 limits and")
    w("       latches whatever the load (no source). UNDER IT the latch rests on the faulted load persisting as PACK_P falls; if the load")
    w("       drops out (a constant-power load under its own UVLO, another protection acting) a unit whose limit is over the crowbar's own")
    w("       current leaves its limit, and the crowbar's own current through R10, over the window's least, HOLDS THE TRIP: the band")
    w("       %s to %s V (the window's least through R140 at -1 %%, the most limit through it at +1 %%), %s W in R140 held in round 11's" % (
        fmt(R["band"][0], 2), fmt(R["band"][1], 2), fmt(R["p_stall"], 0)))
    w("       drawing: a DEMONSTRATED DEFECT of the draft (no source); with a source's settled share on the record's B-R2 basis the -1 can")
    w("       stay out of its limit up to %s V, and inside the event's unprinted transient up to the pack's %s V (4c')" % (fmt(R["v_band_src"], 2), fmt(PACK_MOST, 1)))
    w("     THE BAND'S UPPER EDGE WITH THE LOOP (round 13, the recheck's F2): the loop from BRK_VIN to PACK_N also holds the most-limit unit's")
    w("       sense drop at its limit (VCL %s mV PRINTED), its two FETs in parallel (0.96 mOhm at VGS 10 V and 25 C PRINTED: 0.48 mOhm) and" % fmt(R["VCL"][1], 1))
    w("       Q111 (1.6 mOhm at VGS 4.5 V and 25 C PRINTED; its gate at %s V there): %s V on those maxima; %s V with both FETs at twice them" % (
        fmt(R["vcg_edge"], 1), fmt(R["edge"][0], 2), fmt(R["edge"][1], 2)))
    w("       and 1 mOhm of copper (ASSUMED: TI prints the hot RDS(on) as a typical curve only; the loop's copper is Layer 9's): THE BAND RUNS")
    w("       FROM %s TO ABOUT %s TO %s V; the on-time bound acts at every BRK_VIN, so the design is unaffected; E-12s's 10.6 V lies over it" % (
        fmt(R["band"][0], 2), fmt(R["edge"][0], 2), fmt(R["edge"][1], 2)))
    w("     three approaches (constitution section 4): (a) R140 under 7.6 V / (23.93 A x 1.01) = %s Ohm, so the crowbar alone exceeds the" % fmt(7.6 / (R["LIM"][2] * 1.01), 4))
    w("       limit from 7.6 V: its peak at the clamp, %s A with the most limit's load, passes the %s A where VIN to SENSE exceeds its 0.3 V" % (
        fmt(CLAMP / (7.6 / (R["LIM"][2] * 1.01) * 0.99) + R["LIM"][2], 1), fmt(R["VSNS_I"], 1)))
    w("       absolute maximum (a row newly reached), and a source can still hold the -1 out of its limit: NOT SELECTED; (b) the trip armed")
    w("       only above %s V: the blades' held 23.93 A stays uncorrected under it, L8P-R10-F1 open in that band: NOT SELECTED; (c) THE" % fmt(R["v_force"], 2))
    w("       ON-TIME BOUND, SELECTED (SESSION L8P-R12-D1): channel 2 also reads the trip, through D106 (BAT46W: VF at most 0.25 V at 0.1 mA,")
    w("       PRINTED, with RESET1's VOL at most 0.3 V: OCH_S2 under 0.55 V against SENSE2's least 0.792 V) and R143 2.2 MOhm from BRK_PGD")
    w("       (round 13: R143 330 kOhm from BRK_VIN and Q114 holding OCH_S2 low while PGD is low, 4j),")
    w("       so RESET2 disarms the crowbar %s to %s ms after the trip asserts whatever the breaker does; it re-arms only once RESET1 has" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["tcts2"][1] * 1e3, 2)))
    w("       released (R10 under the window: the dropped load) and PGD is high, so no retry train; the least delay covers the gate and the")
    w("       -1's clearing with %s ms for tCL; the crowbar conducts at most %s ms" % (fmt(R["arm_cover"] * 1e3, 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("     its levels (check_l8p_och.py's arithmetic on the drawn R143): BRK_PGD stays over Q106's 2.5 V threshold maximum (JSCJ, PRINTED)")
    w("       at BRK_VIN 7.6 V while D106 pulls (so the restart inhibit stays gated during the event), and OCH_S2 armed stays over SENSE2's")
    w("       release with RESET1's 300 nA and SENSE2's 100 nA through R143 (PRINTED) (round 12's levels; round 13's in 4j and section 5)")
    w("     WHAT STAYS: a held overload that persists through the bound with the -1 out of its limit leaves the trip disarmed until it falls")
    w("       under the window (round 10's rows meanwhile): it needs a source to carry (V / R140 + the window's least - the most limit) x V")
    w("       for %s ms, on the record's settled basis only at BRK_VIN under %s V (the -1's floor %s V), otherwise only inside the source's" % (
        fmt(R["tcts2"][0] * 1e3, 2), fmt(R["v_resid"], 2), fmt(R["v_floor"], 1)))
    w("       unprinted settling: CONDITIONAL, evidence E-12s (new): board P with boards A and E, a source at its IIN_HOST, a held overload")
    w("       over the window at BRK_VIN 7.6, 10.6 and 16.8 V, ten events each: the -1 latched inside %s ms, the source's current into the" % fmt(R["tcts2"][0] * 1e3, 2))
    w("       pack lead and R140's voltage recorded")
    w("       (round 13, the recheck's F8) E-12s's specimens: three board P specimens with boards A and E, the -1's current limit read on each")
    w("       first (E-9's method) and the events run on the specimen whose limit reads highest (a high-limit unit keeps out of its limit")
    w("       longest: the worst case), the result transferring only to units whose limit reads at or under it; at 25 C and in a chamber at")
    w("       the 76.25 C air; ten events at each BRK_VIN; pass: in every event the -1 latched inside %s ms of the trip's assertion (TP110 to" % fmt(R["tcts2"][0] * 1e3, 2))
    w("       the breaker's gate), and where it stays out of its limit TP111's pulse ended inside %s ms; the timing read at 10 us or better" % fmt(R["t_on_max"] * 1e3, 2))
    w("       (a 1 MS/s record), an uncertainty of about 1 %% of the %s ms left for tCL" % fmt(R["arm_cover"] * 1e3, 2))
    L = K["levels"]
    w("   4j. THE PGD-LOW DISARM ON LEAKAGE (round 13, the targeted recheck's F1; leakages at the record's %s C site, each off leakage" % fmt(SITE))
    w("     doubled every 10 K from its printed row: ASSUMED, the record's rule)")
    w("     ROUND 12'S DRAWING, SHOWN FIRST: OCH_S2 was pulled toward BRK_PGD's low (PGD's VOL at most 0.150 V, PRINTED) through R143 2.2 MOhm")
    w("       only, so any current into OCH_S2 lifts it by I x R143: %s uA lifts it over SENSE2's least VITN 0.792 V with no sink, %s uA" % (
        fmt(R["r12_lift"][0] * 1e6, 2), fmt(R["r12_lift"][1] * 1e6, 2)))
    w("       with RESET1's 300 nA and SENSE2's 100 nA (PRINTED maxima) as sinks. What reaches it, through D106 reversed (anode on OCH_S2,")
    w("       cathode on OCH_R):")
    w("         Q112 off (RESET2 asserted, PGD low): Q112's off leakage into OCH_R, %s uA at the site (80 nA at 60 V and 25 C PRINTED); it" % fmt(R["q112_site"] * 1e6, 2))
    w("           passes the two lifts at %s C and %s C on the rule" % (fmt(R["r12_t"][0], 1), fmt(R["r12_t"][1], 1)))
    w("         Q112 on (armed as PGD falls): OCH_R held near half BRK_VIN less Q112's VGS, so D106's own reverse current flows: PRINTED")
    w("           0.3 uA at 1.5 V and 25 C (already over %s uA), 5.0 uA at 1.5 V and 60 C, 7.5 uA at 10 V and 60 C, 15 uA at 50 V and 60 C;" % fmt(R["r12_lift"][0] * 1e6, 2))
    w("           %s uA at the site from the 50 V row" % fmt(R["d106_site"] * 1e6, 1))
    w("         the PGD pin's printed off leakage (5 uA at 80 V) does not enter: PGD sinks while low (the recheck's F6)")
    w("       so OCH_S2 sat up to %s V (OCH_R's level, where D106's reverse bias collapses) while PGD was low: RESET2 released, Q112 armed:" % fmt(R["r12_level"], 2))
    w("       the crowbar armed after tSD at power-up, through a start and on a latched breaker, from about %s C on the rule and at any" % fmt(R["r12_t"][0], 0))
    w("       temperature on BAT46W's printed maximum with Q112 on as PGD falls: round 12's 'never at power-up, during a start or on a latched")
    w("       breaker' NOT SHOWN in its drawing (no protection lowered; the service at a start not shown). A shorted D106 there put OCH_S2 on")
    w("       OCH_R, which Q112 holds near half BRK_VIN while PGD is low: the PGD-low disarm lost, LATENT (round 12's 4g 'as drawn' withdrawn)")
    w("     THREE CORRECTIONS ON PRINTED FIGURES (constitution section 4: at most three, materially different):")
    w("       (1) a disarm FET (2N7002) from OCH_S2 to PACK_N driven from the crowbar's gate, D106 removed, R143 2.2 MOhm from BRK_PGD kept: no")
    w("         current flows into OCH_S2 while PGD is low, but the FET's off leakage sinks the ARMED level through R143 and BRK_PGD's")
    w("         0.5 MOhm: %s V at BRK_VIN 7.6 V at the site, under the release from a %s C site on the rule; and its gate falls when the" % (
        fmt(R["a1_arm"], 2), fmt(R["a1_t"], 1)))
    w("         disarm turns the crowbar off, so OCH_S2 rises while RESET1 is still asserted: a re-arm with the overload held, a pulse train")
    w("         (round 12's 'no retry train' lost); from RESET1 instead it needs an inverter and keeps the armed-level failure: NOT SELECTED")
    w("       (2) R143 from BRK_PGD lowered with a pull-down Rp, judged leniently (OCH_S2 at D106's 0.55 V in the event, no sink on the armed")
    w("         level, PGD's VOL 0): BRK_PGD over Q106's 2.5 V while D106 pulls needs R143 of %s MOhm or more; the armed level over the" % fmt(R["a2"][0] / 1e6, 3))
    w("         release then needs Rp of %s MOhm or more; the PGD-low level then tolerates at most %s uA into OCH_S2, against Q112's %s uA" % (
        fmt(R["a2"][1] / 1e6, 3), fmt(R["a2"][2] * 1e6, 2), fmt(R["q112_site"] * 1e6, 2)))
    w("         at the site and BAT46W's printed 5.0 uA at 60 C: no pair meets the three levels together: NOT SUPPORTED")
    w("       (3) OCH_S2 PULLED UP FROM BRK_VIN BY R143 330 kOhm AND HELD LOW WHILE PGD IS LOW BY A CONDUCTING FET: Q114 (2N7002) from OCH_S2")
    w("         to PACK_N, its gate OCH_PN PGD inverted by Q113 (2N7002, gate on BRK_PGD) against R144 200 kOhm from BRK_VIN, the zener D107")
    w("         (BZT52C12) keeping it under 12.7 V; D106 kept for the on-time bound: SELECTED (SESSION L8P-R13-D1)")
    w("     THE SELECTION'S LEVELS (check_l8p_och.py on the composed netlist, section 5; BRK_VIN 7.6 V unless stated):")
    w("       PGD low: Q114's gate at least %s V with Q113's off leakage and D107's reverse current at the site through R144 at +1 %%" % fmt(L["gate"], 2))
    w("         (BZT52C12 0.1 uA at 8 V and 25 C PRINTED), at or over the 5 V where JSCJ prints 7 Ohm: OCH_S2 at most %s mV with R143's" % fmt(L["pgd_low"] * 1e3, 2))
    w("         current at the clamp and D106's %s uA through it; the level holds for any on-resistance up to %s kOhm, so the hot rise of" % (
        fmt(R["d106_site"] * 1e6, 1), fmt(0.792 / (L["pgd_low"] / O.RDS_5V) / 1e3, 2)))
    w("         the 7 Ohm (not printed) does not decide it: NO LEAKAGE INTO OCH_S2 CAN LIFT IT while PGD is low (a conducting FET, not a")
    w("         2.2 MOhm node)")
    w("       armed (PGD high, RESET1 released): OCH_S2 %s V with Q114's off leakage at the site, RESET1's 300 nA and SENSE2's largest" % fmt(L["armed"], 2))
    w("         printed 2 uA (ASSUMED to bound the 0.8 V variant far over its threshold) through R143 at +1 %%, over the release %s V; Q113" % fmt(O.REL_MAX, 3))
    w("         holds OCH_PN low with BRK_PGD on its gate: its 7 Ohm PRINTED where BRK_PGD reaches 5 V (BRK_VIN 10.2 V up), under it the")
    w("         record's convention for Q106 (a gate over the 2.5 V threshold maximum), whose failure direction is a disarm, never a crowbar")
    w("       the trip asserted: OCH_S2 at most %s V (RESET1's VOL 0.3 V at its 5 mA row, D106's VF 0.25 V at 0.1 mA for its %s uA at the" % (
        fmt(L["low"], 2), fmt(L["i_d106"] * 1e6, 0)))
    w("         clamp, 90 mV for -20 C INFERRED), under 0.792 V: the on-time bound as round 12's; RESET1 carries at most %s mA" % fmt(
        (CLAMP / ((R136 + R137) * 0.99) + L["i_d106"]) * 1e3, 3))
    w("       BRK_PGD carries only Q106's and Q113's gates (80 nA each PRINTED at 25 C and 20 V): %s V in every state of the trip, over Q106's" % fmt(L["pgd"], 2))
    w("         2.5 V threshold maximum (round 12: 3.20 V while D106 pulled through R143): L8P-R12-D1's reversal 'BRK_PGD under Q106's")
    w("         threshold during the event' can no longer come from the trip")
    w("       THE PGD LEAKAGE BASIS OF BOTH LEVELS (the recheck's F6): the PGD-low level does not depend on the PGD pin's off leakage (PGD")
    w("         sinks); the armed level needs BRK_PGD over Q113's 2.5 V as Q106 does, and on the pin's printed 5 uA (at 80 V, a loose bound")
    w("         at 3.8 to 8.4 V) BRK_PGD's released level clears it from BRK_VIN %s V up, for Q106 (the breaker's draft) and Q113 alike;" % fmt(R["v_pgd5"], 2))
    w("         under it the trip disarms (a lost trip, never a crowbar); round 11 armed from about 6.8 V and round 12 from about 8.8 V on")
    w("         that bound (W153, RECORD); evidence: the pin's off leakage at 3.8 to 8.4 V (a vendor fact for TI, or a reading on board P's")
    w("         specimen with E-12b)")
    w("     THE START (the recheck's 'service at a start'): the start's own current is at most %s A for 40.7 ms (RECORD, record l9stk), under" % fmt(R["start_i"], 3))
    w("       the window's least %s A, so a start never asserts the trip by itself; the disarm now holds whenever PGD has been low for the" % fmt(R["win"][0], 3))
    w("       arming delay: Q114's gate reaches its 2.5 V threshold maximum %s ms after PGD falls (R144 into 1 nF, ASSUMED: JSCJ lists Ciss" % fmt(R["t_rise"] * 1e3, 3))
    w("       as unverifiable and D107's capacitance is not printed), RESET2 asserts at most %s ms after PGD's fall, inside the insertion" % fmt(R["t_disarm_start"] * 1e3, 2))
    w("       time's least %s ms (record l9stk: it runs when VIN passes PORIT, the gate held low) and the RC hold's 0.110 s at a docking:" % fmt(R["ins_least"] * 1e3, 2))
    w("       THE START SERVICE SHOWN on those figures (in round 12's drawing not shown, the recheck's F1); the LM5069 releases PGD itself")
    w("       under about 5 V of VIN (SNVS452G 8.3.6, no figure printed): armed with the -1's gate held off, no discharge over the window")
    w("       through R10, as in rounds 11 and 12")
    w("     SNVSBJ1E 8.3.5.1 (the recheck's F5): a CTS capacitor not fully discharged when a fault returns gives a shorter next delay; TI asks")
    w("       the time between faults over 10 %% of the programmed delay: channel 1's least %s ms exceeds 10 %% of channel 2's most (%s ms)," % (
        fmt(R["tcts1"][0] * 1e3, 3), fmt(R["tcts2"][1] * 1e2, 3)))
    w("       and the -1's own timer discharges at 1.25 to 3.75 uA against 51 to 120 uA charging, so a repeated fault shortens the -1's")
    w("       clearing more than channel 2's bound: covered")
    w("     THE CYCLING LOAD (the recheck's F7): a load that drops out at each trip and returns over the window at each re-arm makes a train")
    w("       of bounded pulses at least %s ms apart (the trip's least sense delay and the arming's least; the turn-off and re-arm taken 0)," % fmt(R["train_tmin"] * 1e3, 2))
    w("       each at most %s J in the band (no source) and %s J on the voltage bound; Vishay's CONTINUOUS-PULSE line for the 2512 (page 5," % (
        fmt(R["e_s"], 3), fmt(R["e_v"], 2)))
    w("       READ from its vector path; its long-pulse end %s W at 100 s meets the printed P70) gives %s W a part at %s ms against the" % (
        fmt(R["cont_w100"], 2), fmt(R["cont_line"], 1), fmt(R["t_on_max"] * 1e3, 2)))
    w("       band's %s W a part, but its condition holds the mean under the rated dissipation at the ambient: nine parts at P70 1.5 W derated" % fmt(R["part_band"], 1))
    w("       to the air (%s), %s W: a train needs a period of %s ms or more (%s ms with a source), against the %s ms a load could make:" % (
        fmt(R["derate_air"], 3), fmt(R["p_rated"], 1), fmt(R["train_need"] * 1e3, 1), fmt(R["train_need_src"] * 1e3, 0), fmt(R["train_tmin"] * 1e3, 2)))
    w("       a faster train is NOT BOUNDED (named: the kit's loads, Layer 7's list, must show none re-enters the window within %s ms of a" % fmt(R["train_need_src"] * 1e3, 0))
    w("       trip; the smallest correction for a next round, not drafted: a re-arm hold-off on U107's CTR2 longer than that period)")
    w("")
    w("5. THE DRAFT COMPOSED IN L4-E9'S ORDER (board P; INFERRED from the regenerated netlist)")
    for name, r in K["steps"]:
        w("   %-58s %s" % (name, r))
    w("   board P regenerated: %d parts; netlist sha256/16 %s" % (K["parts"], K["net_sha"]))
    w("   check_l8p_netlist.py on it: %s" % "; ".join(l.strip() for l in K["l8p_lines"]))
    w("   check_l8p_och.py on it: OCH %s%s; the window from the drawn values %s to %s A" % (
        K["och"][0], (": " + "; ".join(K["och"][1])) if K["och"][1] else "", fmt(K["win_drawn"][0], 3), fmt(K["win_drawn"][1], 3)))
    w("     (round 12) the drawn delays: SENSE1's filter %s us, the sense delay %s to %s ms, the arming and on-time delay %s to %s ms;" % (
        fmt(K["delays"]["filter"] * 1e6, 1), fmt(K["delays"]["cts1"][0] * 1e3, 3), fmt(K["delays"]["cts1"][1] * 1e3, 3),
        fmt(K["delays"]["cts2"][0] * 1e3, 2), fmt(K["delays"]["cts2"][1] * 1e3, 2)))
    w("     the bound's levels at BRK_VIN 7.6 V: OCH_S2 %s V with RESET1 asserted, BRK_PGD %s V, OCH_S2 armed %s V; (round 13) OCH_S2" % (
        fmt(K["levels"]["low"], 2), fmt(K["levels"]["pgd"], 2), fmt(K["levels"]["armed"], 2)))
    w("       %s mV while PGD is low with every leakage at the site, Q114's gate %s V" % (fmt(K["levels"]["pgd_low"] * 1e3, 2), fmt(K["levels"]["gate"], 2)))
    w("   the mutations, each read by check_l8p_och.py:")
    for name, v, why in K["muts"]:
        w("     %-100s OCH %s: %s" % (name + ",", v, why[:90]))
    w("   the draft refuses a board P without the breaker and the ideal diode (exit %d: %s), a second application (exit %d: %s) and the" % (
        K["refusals"][0][0], K["refusals"][0][1][:70], K["refusals"][1][0], K["refusals"][1][1][:60]))
    w("     repository's own generator while unreleased (exit %d: %s)" % (K["refusals"][2][0], K["refusals"][2][1][:80]))
    w("")
    w("6. L4A-67: C-PROT REV 1 FOR THE GUARD ON THE CORRECTED CIRCUIT (the delta of round 9, M-A of round 10, the trip of this round)")
    w("   the states: (i) the trip intact: no current is HELD over %s A; above it one event per recovery as 4c; (ii) the trip latently failed" % fmt(hi))
    w("     (4g): round 10's rows at the breaker's held %s A. Each row: below the trip (held) | above the trip (the event) | verdict" % fmt(I))
    for row in R["rows"]:
        w("   %s" % row[0])
        for line in row[1:]:
            w("       %s" % line)
    w("   the guard's own claims (rounds 8 and 9, 10c): unchanged by the trip, which touches neither its pour nor the loop; with the trip")
    w("     intact the hottest battery FET reads at most %s C at E-1's bar and %s C at the design target held (the guard: no trip under" % (
        fmt(R["tj_trip_bar"], 1), fmt(R["tj_trip_tgt"], 1)))
    w("     127.8 C at its die, surely tripped from 132.2 C); a held overload over the window is ended by the trip within %s ms plus tCL," % fmt(R["t_event"] * 1e3, 2))
    w("     long before the pour's own time; the guard keeps its own case (the pour's temperature at any current, a pour worse than the bar")
    w("     included); its latent failures (L8P-R9-F1) expose no part at the held currents M-A holds ON A BOARD WHOSE INSTALLED PATH MEETS")
    w("     E-1's BAR (round 12, the check's F5: a per-built-board check of the battery FETs' path, E11-29u, names it); on a board that")
    w("     misses the bar (a void or a tab joint E11-29's coupon does not see) the guard's own silent failures, with no detection")
    w("     interval, stay a residual (REMAINING ENGINEERING, HO-A's pattern)")
    w("")
    w("7. L4A-68: THE GUARD'S ALLOWANCE FOR ITS CONSUMERS (RECORD, record l8p 10c; the texts the apply scripts write)")
    w("   the draw on DOCK_EN_OUT at printed maxima, the off leakage at the doubling: cold %s uA (%s uA with the clamp's gates doubled), tripped" % (
        fmt(R["DRAW"][0]), fmt(R["DRAW"][1])))
    w("     %s uA (%s uA with one of path 1's pull-up resistors shorted): the allowances %s uA cold and %s uA tripped (10c)" % (
        fmt(R["DRAW"][2]), fmt(R["DRAW"][3]), fmt(R["ALLOW"][0], 0), fmt(R["ALLOW"][1], 0)))
    w("   the capacitance on DOCK_EN_OUT: C261 and C268, 330 nF each, and U61's 4.7 uF C262 behind its input in dropout (L4-E11 28d)")
    w("   path 2's load is on VBAT, not on the loop: U62 16 uA and U63 2.25 uA at their printed table maxima (10c)")
    w("   the round 11 trip adds nothing on DOCK_EN_OUT or DOCK_EN_RET (check_l8p_och's APART); the consumers' texts:")
    w("     Layer 5 (IF-AE-DOCK, apply_pcb_interfaces_guard_allowance.py): '%s'" % LAYER5_TEXT)
    w("     record l9stk 15.9 (apply_l9stk_guard_allowance.py, three edits: this restatement after the supply bullet, the acceptance item")
    w("       and the Layer 5 row of its correction scope, each keeping the round's 30 uA as history): '%s'" % L9STK_TEXT)
    w("   the replay of L4-E11's 20f, 22 and 28 at these figures: record l4e11's round 19 (l4e11_rowc.py)")
    w("")
    w("8. VERDICTS")
    w("   L8P-R10-F1: CORRECTED IN DRAFT by (B), SESSION L8P-R11-D1: composed in L4-E9's order, read DRAWN, %d of %d mutations FAIL; electrical" % (
        sum(1 for _n, v, _w in K["muts"] if v == "FAIL"), len(K["muts"])))
    w("     acceptance on printed figures: no current held over %s A, %s %% of the blades' rerated current at the band, the held service" % (
        fmt(hi), fmt(100 * hi / O.BLADE_BAND, 1)))
    w("     untouched (round 13 corrects round 12's 'the service untouched': at a start it was not shown in round 12's drawing, the recheck's")
    w("     F1; with round 13's disarm it is shown, 4j); CONDITIONAL on E-6 (R10's sheet within -7.3 to +8.3 %), E-6b (R140's printed pulse,")
    w("     RESTATED in round 12, on one basis in round 13: %s J in %s ms), L8P-R12-F1 (4g: R140 held near 118 W after a shorted crowbar with" % (
        fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2)))
    w("     a source, a single-failure hazard the trip itself adds; its series element named as Layer 6's, chosen with R140's part), the")
    w("     PGD-low disarm of 4j (the recheck's F1, corrected in draft by round 13, UNVERIFIED until its one bounded check), E-10")
    w("     (the key-down excursions under 0.282 ms: a bench item, the check's F7), E-12f, E-12s (round 12, 4i) and the latent-failure")
    w("     residual of 4g; round 12 corrects the band of 4i (a demonstrated defect of round 11's drawing) by the on-time bound, composed,")
    w("     read DRAWN and mutated (section 5); UNVERIFIED until the targeted recheck (L4A-69); the approaches (A) NOT SUPPORTED and (C) NOT")
    w("     SELECTED on printed figures")
    w("   L4A-67: C-PROT rev 1 for the guard on the corrected circuit: every series part within its printed limits below and above the trip")
    w("     where a printed figure exists; NOT SHOWN, each missing figure named and CONDITIONAL: board P's switches' hot RDS(on) (E-8, E-11),")
    w("     R10, R101, R102 and R140 (E-6, E-6b), the 12 AWG wires (a maker's ampacity at 76.25 C with its insulation class), the dock pins'")
    w("     split (E-4), Q111's turn-off with a source (its SOA); the battery FETs at most 150 C on the held state, CONDITIONAL on E-05,")
    w("     E11-29, E11-36 and E-9 (round 12, the check's F4); THE REGISTER'S ACCEPTANCE READS NOT MET on its latent-failure clause: the")
    w("     trip's silent failures (4g) and the guard's on a board that misses E-1's bar have no detection interval (REMAINING ENGINEERING;")
    w("     the check's F6; round 11's 'DONE on the desk' withdrawn); L8P-R12-F1 (a shorted crowbar with a source, 4g) OPEN")
    w("   L4A-68: the allowance stated for its consumers (section 7, two apply scripts, NOT APPLIED); the replay is record l4e11's round 19")
    w("")
    w("9. PREDICATES")
    for name, ok in R["preds"]:
        w("   %-118s %s" % (name, "yes" if ok else "NO"))
    return "\n".join(o) + "\n"


FAILS = (
    ("U106 or U107 dead, Rin open, RESET1 stuck high", "the trip lost, LATENT: round 10's rows (the blades over by 0.83 A)"),
    ("Q112, Q110, R142, Q111 or R140 open; D105 short", "the crowbar lost, LATENT: as above"),
    ("U106's output stuck high, Rf open", "a trip at every running start: the -1 latches, the kit dark (found)"),
    ("Q110 or Q111 shorted", "the crowbar at every start: the -1 latches in its start (found); with a source, 4g's last lines"),
    ("Q112 shorted, RESET2 stuck high", "the arming and the on-time bound lost: a crowbar for tSD at a gauge's wake on a live PACK_P"),
    ("RESET2 stuck low, C120 shorted", "the crowbar disarmed, LATENT: as the first row"),
    ("C119 open", "the sense delay 17 us at most: a trip on an excursion E-10 allows (found)"),
    ("D106 open (rounds 12 and 13)", "the on-time bound lost, LATENT: round 11's state, 4i's band unbounded (E-12f reads TP112)"),
    ("R143 open (round 13)", "OCH_S2 without its pull-up: armed or disarmed on leakage alone while PGD is high, LATENT (E-12f: TP112 running)"),
    ("C120 open (round 12)", "the bound at 17 us: the crowbar too short to latch the -1: the trip lost, LATENT (E-12f: TP111's pulse)"),
    ("R143 shorted (round 13)", "OCH_S2 on BRK_VIN: both disarms lost; Q114 at PGD's next fall, D106 and RESET1 at the next trip overstressed (E-12f)"),
    ("D106 shorted (round 13; round 12's 'as drawn' withdrawn)", "OCH_S2 on OCH_R: both disarms still act; while armed a fall of PGD drives the crowbar through Q114 for"),
    ("", "  the arming delay: one pulse inside E-6b at each breaker turn-off (the line's n < 1000), LATENT (E-12f: TP111 at a turn-off)"),
    ("Q113 shorted, R144 open, D107 shorted, Q114 open (r13)", "the PGD-low disarm lost, LATENT: the crowbar armed through starts (E-12f: TP112 with the breaker off)"),
    ("Q113 open, Q114 shorted (round 13)", "OCH_S2 held low: the trip disarmed, LATENT: as RESET2 stuck low (E-12f: TP112 while running)"),
    ("D107 open (round 13)", "Q114's gate at BRK_VIN while PGD is low: within 20 V to the pack's 16.8 V, over it only in a clamp surge"),
)

import apply_pcb_interfaces_guard_allowance as A5   # noqa: E402  Layer 5's text, one source
import apply_l9stk_guard_allowance as A9           # noqa: E402  record l9stk 15.9's restatement, one source
LAYER5_TEXT = A5.TEXT
L9STK_TEXT = " ".join(A9._NEW_1.split("\n", 1)[1].replace("**", "").split())


def rows(R):
    """C-PROT rev 1, part by part, on the corrected circuit."""
    W = R["W"]
    I, T_AIR = W["I"], W["T_AIR"]
    lo, hi = R["win"]
    k = (hi / I) ** 2
    tj_bar = T_AIR + k * (W["TJ_bar"] - T_AIR)
    tj_tgt = T_AIR + k * (W["TJ_tgt"] - T_AIR)
    R["tj_trip_bar"], R["tj_trip_tgt"] = tj_bar, tj_tgt
    # R17 on ROHM's lower printed line at the trip's most (round 10's function, the TCR above 60 C ASSUMED)
    p17 = lambda tk: hi ** 2 * W["R17_MAX"] * (1 + 50e-6 * max(0.0, tk - 60.0))
    allowed = lambda tk: min(7.0 if tk <= 70 else 7.0 * (170 - tk) / 100.0, 5.0 if tk <= 110 else 5.0 * (170 - tk) / 60.0)
    a, b = 25.0, 170.0
    for _ in range(80):
        m_ = (a + b) / 2
        a, b = (m_, b) if p17(m_) <= allowed(m_) else (a, m_)
    share = 9.0 / hi
    pin_ratio = (1 - share) / (3 * share)
    xt_rise = 85.0 * (hi / 35.0) ** 2
    q1k = (150.0 - T_AIR) / (50.0 * 2 * hi ** 2 * W["q1_r"])
    q101k = (150.0 - T_AIR) / (50.0 * 2 * (hi / 2) ** 2 * W["q101_r"])
    R["rows_num"] = dict(tk=a, pin=pin_ratio, xt=T_AIR + xt_rise, q1k=q1k, q101k=q101k, cell=8.0 * 0.997 * hi / I)
    ev = "the event: at most %s A for %s ms plus tCL, the crowbar's peak %s A for 16.5 us at most" % (
        fmt(I), fmt(R["t_event"] * 1e3, 2), fmt(R["peak_clamp"], 1))
    return [
        ["Q39, Q40, Q42 (BUK6Y10-30P; round 10's 15a, PRINTED device maxima)",
         "held: at most %s A: the hottest junction %s C at E-1's bar, %s C at the design target (trip intact); %s C at the bar with the" % (fmt(hi), fmt(tj_bar, 1), fmt(tj_tgt, 1), fmt(W["TJ_bar"], 2)),
         "  trip failed (round 10) | %s: at most the held %s A state by superposition (round 10's 15e) | WITHIN 150 C, CONDITIONAL on" % (ev, fmt(I)),
         "  E-05, E11-29, E11-36, E-9 (the -1's as-built most limit: the trip failed, the FETs hold the breaker's limit; round 12, the check's",
         "  F4) and, for the claim that the guard's silent failures expose nothing, each built board's path meeting E-1's bar (E11-29u; F5)"],
        ["R17 (ROHM GMR100HJAAFD5L00, PRINTED derating)",
         "held: %s W at %s A on its printed maximum; its terminals admitted to %s C on the lower line (round 10: 128.5 C at %s A) | the" % (fmt(p17(a), 3), fmt(hi), fmt(a, 1), fmt(I)),
         "  event: within its held state's energy for 2.2 ms; the 16.5 us spike inside the hot-short row the record carries | WITHIN its",
         "  derating, CONDITIONAL on the terminal reading (E11-29's coupon)"],
        ["the pour and the vias (MODEL; record l9stk's conductor model)",
         "held: the band %s K over the air at %s A (round 10: 9.16 K at %s A) | the event: as the held state | WITHIN on the model; the" % (fmt(W["BAND"] * k, 2), fmt(hi), fmt(I)),
         "  laminate's limit NOT HELD (L9-STACKUPS 14.3)"],
        ["the three 25 A MINI blades (Littelfuse 297, PRINTED rerating READ)",
         "held: at most %s A, %s %% of the rerated %s A at the air, %s %% of %s A at the band (trip intact); round 10's %s %% with the trip" % (
             fmt(hi), fmt(100 * hi / W["I_rr_air"], 1), fmt(W["I_rr_air"]), fmt(100 * hi / W["I_rr_band"], 1), fmt(W["I_rr_band"]), fmt(100 * I / W["I_rr_air"], 1)),
         "  failed | the event: one excursion per recovery of at most 2.2 ms at 103.6 %% of the rerated current and 16.5 us at %s A, inside" % fmt(R["peak_clamp"], 1),
         "  the printed rows' least opening times (135 %: 0.75 s; 600 %: 30 ms) | WITHIN with the trip intact (L8P-R10-F1 CORRECTED IN DRAFT);",
         "  OVER by 0.83 A on the trip's latent failure (4g)"],
        ["the Keystone 3568 holders (M65 p.42, PRINTED UL 30 A, -50 to +145 C)",
         "held: %s %% of 30 A | the event: as the blades | WITHIN on current" % fmt(100 * hi / 30.0, 1)],
        ["the dock pins J_CP1 to 4, J_CN1 to 4 (Mill-Max 0858, 9 A continuous PRINTED, no minimum resistance)",
         "held: %s A a pin evenly; no pin over 9 A needs the split ratio at least %s (round 10: 0.553 at %s A) | the event: at most %s A a" % (
             fmt(hi / 4.0), fmt(pin_ratio, 3), fmt(I), fmt(R["peak_clamp"] / 4.0, 1)),
         "  pin for 16.5 us, inside the hot-short row | WITHIN evenly, CONDITIONAL on E-4"],
        ["the XT60 J_BATT (Amass, PRINTED 30 A; 35 A at a rise under 85 K)",
         "held: %s %% of 30 A; the rise scaled from the 35 A row %s K (INFERRED), %s C, %s K under its 120 C | the event: as the blades |" % (
             fmt(100 * hi / 30.0, 1), fmt(xt_rise, 1), fmt(T_AIR + xt_rise, 1), fmt(120.0 - T_AIR - xt_rise, 1)),
         "  WITHIN on current, its temperature INFERRED"],
        ["the 12 AWG wires (W_P, W_N, P_CP)",
         "no maker's sheet held: MISSING the wire maker's ampacity at a 76.25 C ambient for its insulation class (Layer 6, the harness",
         "  supplier) | NOT SHOWN, CONDITIONAL (the held current now at most %s A)" % fmt(hi)],
        ["Q1, Q2, Q109 (CSD17570Q5B, PRINTED 0.69 mOhm at 25 C only; hot TYPICAL)",
         "held: the 150 C junction admits a hot factor up to %s with both losses through the common pad at %s A (round 10: 1.866 at %s A)," % (fmt(q1k, 3), fmt(hi), fmt(I)),
         "  against the typical 1.8 | the event: the held state's bound | NOT SHOWN on printed maxima: MISSING TI's maximum RDS(on) at",
         "  125 or 150 C, or E-8's joint-case reading on board P's first specimen (TJ under 150 C at the held current from 76.25 C); CONDITIONAL"],
        ["Q101, Q102 (CSD18510Q5B, the breaker's FETs)",
         "held: a hot factor up to %s admitted to 150 C (round 10: 5.37) | the event: l9stk 15.6's 'over the unit's limit' row, 0.57 of" % fmt(q101k, 2),
         "  the derated SOA (RECORD) | NOT SHOWN on printed maxima (E-11, the installed path at most 52.5 C/W, and the hot RDS(on)); the",
         "  event's SOA reading CONDITIONAL on E-2 and E-3 (record l9stk)"],
        ["Q111 (CSD18510Q5B, the crowbar; round 11, restated in round 12)",
         "held: off (IDSS 1 uA at 25 C PRINTED) | the event: %s A at the onset and %s A held with a source (4c') against IDM 400 A PRINTED; its" % (
             fmt(R["peak_clamp"], 1), fmt(R["i_q111_src"], 1)),
         "  turn-off crossing %s W without a source, WITHIN the same part's derated %s W at %s ms; %s W with a source on the voltage" % (
             fmt(R["p_q111_off_nosrc"], 1), fmt(R["PULSE"][2], 1), fmt(R["PULSE"][1], 3), fmt(R["p_q111_off"], 0)),
         "  bound (%s W on the settled basis) | WITHIN on current; the turn-off with a source NOT SHOWN (its SOA at %s ms not read)" % (
             fmt(R["p_q111_off_settled"], 1), fmt(R["t_q111_off"] * 1e3, 2))],
        ["D106 (BAT46W), R143 (330 kOhm since round 13), Q113, Q114 (2N7002), R144 (200 kOhm), D107 (BZT52C12; round 13)",
         "held: D106 reverse at most the clamp's 29.2 V against 100 V, forward at most %s uA against 150 mA; R143 %s mW and R144 %s mW at" % (
             fmt(CLAMP / (R143 * 0.99) * 1e6, 0), fmt(CLAMP ** 2 / (R143 * 0.99) * 1e3, 2), fmt(CLAMP ** 2 / (R144 * 0.99) * 1e3, 2)),
         "  the clamp; Q113 and Q114 VDS at most 29.2 V against 60 V, VGS at most 14.6 V (Q113) and 12.7 V (Q114) against 20 V, Q114 at",
         "  most %s mA against 115 mA; D107 at most %s uA, %s mW | WITHIN" % (
             fmt((CLAMP / (R143 * 0.99) + O.IR_D106_HOT) * 1e3, 3), fmt((CLAMP - 11.4) / (R144 * 0.99) * 1e6, 0),
             fmt((CLAMP - 11.4) / (R144 * 0.99) * 12.7 * 1e3, 2))],
        ["R10 (2 mOhm 2512 2 W, the gauge's sense and the trip's)",
         "held: %s W at %s A | the event: the hot-short row's 16.5 us | NOT SHOWN: MISSING its maker's sheet (tolerance, temperature" % (fmt(hi ** 2 * 2e-3, 2), fmt(hi)),
         "  coefficient, derating at the band; E-6); the trip's window holds for R10 within -7.3 to +8.3 %"],
        ["R101, R102 (the breaker's sense pair; no part chosen)",
         "held: %s and %s W at %s A | NOT SHOWN: MISSING the parts (Layer 6: 2 W each at the band's temperature, 1 %%, at most 50 ppm/K; E-6)" % (
             fmt(W["SNS_REC"][0] * k, 2), fmt(W["SNS_REC"][1] * k, 2), fmt(hi))],
        ["R140 (the crowbar's resistor; round 11, restated in round 12)",
         "held: no current | the event: at most %s J in %s ms (4c': a source present, the -1 held out of its limit; %s J without a source" % (
             fmt(R["e_r140"], 2), fmt(R["t_on_max"] * 1e3, 2), fmt(R["e_n"], 2)),
         "  and the -1 latched) | NOT SHOWN: MISSING a part whose maker prints that single pulse (E-6b restated; round 11's 0.40 J withdrawn)"],
        ["F2 (Eaton SCF9550, 30 A, -20 to +60 C PRINTED)",
         "held: %s %% of 30 A; its printed range ends 16.25 K under the 76.25 C air at any current: the pack's thermal environment (record" % fmt(100 * hi / 30.0, 1),
         "  l4e10 section 9), not a held-current row"],
        ["the cells",
         "held: E-5's split at %s A (round 10: 0.997 of 8 A at %s A, here %s of 8 A per cell evenly, INFERRED) | the battery stream's" % (
             fmt(hi), fmt(I), fmt(hi / I * 0.997, 3)),
         "  and U-01's (outside M-A)"],
    ]


def predicates(R, K):
    W = R["W"]
    lo, hi = R["win"]
    return [
        ("round 10's finding reproduces: the blades over their rerated current at the held breaker limit", W["over_air"] > 0 and W["over_band"] > 0),
        ("a 25 A element would need a rerating over the MINI 297's printed one at the air", R["need_f"] > R["f_air"]),
        ("a 30 A blade's 60 A row puts the copper over both pinned band limits (approach A refused)", R["cu60"] > max(R["band_pinned"])),
        ("the LM5066I's printed spread fails the band reading at the record's least limit (approach C)", R["c_most_1832"] > W["I_rr_band"]),
        ("the LM5066I's printed spread fails the air reading at the service's true current (approach C)", R["c_most_1880"] > W["I_rr_air"]),
        ("the trip's least is over the service's true current (C4)", lo > SERVICE_TRUE),
        ("the trip's most is under the blades' rerated current at the band", hi < W["I_rr_band"]),
        ("the trip's most is under the blades' rerated current at the air", hi < W["I_rr_air"]),
        ("the window from the drawn netlist equals the computed one", abs(K["win_drawn"][0] - lo) < 1e-6 and abs(K["win_drawn"][1] - hi) < 1e-6),
        ("the window tolerates R10 over the record's assumed error", R["r10_room"][0] < -R["r10_assumed"] and R["r10_room"][1] > R["r10_assumed"]),
        ("the trip's least sense delay is over E-10's excursion bound", R["tcts1"][0] > R["e10"]),
        ("the crowbar's own current at the pack's least exceeds the breaker's most limit", R["ic_least"] > R["LIM"][2]),
        ("the crowbar's peak stays under the current where VIN to SENSE passes 0.3 V", R["peak_clamp"] < R["VSNS_I"]),
        ("the arming's least delay, from the trip's assertion, covers the gate, the clearing and 0.5 ms for tCL (round 12)", R["arm_margin"] > O.ARM_MARGIN),
        ("Q110's VGS at the clamp is within its 12 V", R["vgs110"][1] < 12.0),
        ("Q110 stays off under the leakages at the site", R["v_off110"] < R["vth_p"]),
        ("the crowbar stays off under Q110's leakage at the site", R["v_cg_off"] < R["vth_csd"]),
        ("U107's RESET currents are within TI's recommended 5 mA", max(R["ireset1"], R["ireset2"]) < 5e-3),
        ("the crowbar's peak is within Q111's printed IDM", R["peak_clamp"] < 400.0),
        ("the composition ran in L4-E9's order and board P reads its earlier groups DRAWN", K["l8p"] == "DRAWN"),
        ("check_l8p_och reads the composed board P DRAWN", K["och"][0] == "DRAWN"),
        ("every mutation FAILS", all(v == "FAIL" for _n, v, _w in K["muts"])),
        ("the draft refuses without its predecessors, twice, and on the tree's generator", all(rc == 3 for rc, _m in K["refusals"])),
        ("the battery FETs stay at or under 150 C with the trip intact and failed", R["tj_trip_bar"] <= 150.0 + 1e-9 and W["TJ_bar"] <= 150.0 + 1e-9),
        ("the allowance read from 10c is 40 uA cold and 50 uA tripped", R["ALLOW"] == (40.0, 50.0)),
        ("record l9stk's H at 10.6 V with the sink alone reproduces 4.6 V (R104 nominal)", abs(R["uvlo_sink_only"][0] - 4.6) < 0.05),
        ("L8P-R11-F1: the drawn UVLO node is not released at 10.6 V with its inverters at the 86.25 C site (the rule ASSUMED)", R["uvlo_site"][1] < 2.55),
        # round 12
        ("F8: the RC hold's sink-only release reproduces the record's 0.907 s", abs(R["hold_sink_only"] - 0.907) < 1e-3),
        ("F8: on the same leakage rule the hold at the 76.25 C air is longer than DD-7's 0.907 s", R["hold_air"] > 0.907),
        ("F2: round 11's band exists: the window's least through R140 is under the most limit through it", R["band"][0] < R["band"][1]),
        ("F2: the band lies inside the BRK_VIN range the -1 runs at (from 7.6 V)", R["band"][1] > R["v_floor"]),
        ("F2: approach (a)'s peak at the clamp passes VIN to SENSE's 0.3 V current", CLAMP / (7.6 / (R["LIM"][2] * 1.01) * 0.99) + R["LIM"][2] > R["VSNS_I"]),
        ("F2: the on-time bound's most is the one R140's restated pulse is stated for", R["tcts2"][1] <= O.T_ON_BOUND),
        ("F1: R140's restated pulse is the largest of the four cases and over round 11's", R["e_r140"] >= max(R["e_n"], R["e_s"], R["e_w"], R["e_n_src"]) and R["e_r140"] > R["e_n"]),
        ("F1: the source's settled voltage on R140 is under VSYS's most and over the DD-7 inhibit's threshold (L8P-R12-F1)", R["inh_v"] < R["v_settled"] < R["vsys_max"]),
        ("F1: Q111's turn-off without a source is within the same part's derated point", R["p_q111_off_nosrc"] < R["PULSE"][2] and R["t_q111_off"] < R["PULSE"][1] * 1e-3),
        ("F3: the reader computes the window, the delays and the bound from the drawn values", K["delays"] is not None and K["levels"] is not None),
        ("F2: D106's low level is under SENSE2's least threshold", K["levels"]["low"] < O.VITP[0]),
        # round 13
        ("R13 F1: round 12's PGD-low level is lifted over VITN by Q112's off leakage at the site", R["q112_site"] > R["r12_lift"][1]),
        ("R13 F1: BAT46W's printed 0.3 uA at 25 C already passes the no-sink lift of round 12's drawing", 0.3e-6 > R["r12_lift"][0]),
        ("R13 F1: approach (1)'s armed level fails at the site", R["a1_arm"] < O.REL_MAX),
        ("R13 F1: approach (2) tolerates less leakage than BAT46W's printed 5.0 uA at 60 C", R["a2"][2] < 5.0e-6),
        ("R13 F1: the selection holds OCH_S2 under VITN while PGD is low, Q114's gate at 5 V or more at the site",
         K["levels"]["pgd_low"] < 0.792 and K["levels"]["gate"] >= O.VGS_RDS),
        ("R13 F1: the selection's armed level is over the release with Q114's leakage at the site", K["levels"]["armed"] > O.REL_MAX),
        ("R13 F1: BRK_PGD carries no resistor or diode of the trip and stays over Q106's threshold",
         not K["levels"]["pgd_other"] and K["levels"]["pgd"] > O.VTH_Q106),
        ("R13 F1: the disarm asserts inside the insertion time's least at a start", R["t_disarm_start"] < R["ins_least"]),
        ("R13 F1: the start's own current is under the window", R["start_i"] < R["win"][0]),
        ("R13 F2: the band's upper edge with the loop lies over R140's alone and under E-12s's 10.6 V", R["v_force"] < R["edge"][0] < R["edge"][1] < 10.6),
        ("R13 F3: E-6b on one basis is the largest case and nine parts' worst share is under the read line",
         R["e_r140"] == R["e_v"] and R["share_worst"] < R["crcw"]["w"][2]),
        ("R13 F7: the continuous-pulse mean condition needs a period longer than a load could make", R["train_need"] > R["train_tmin"]),
        ("R13 F7: the 2512's continuous-pulse line's long end meets its printed 1.5 W", abs(R["cont_w100"] - 1.5) < 0.05),
    ]


def main():
    try:
        R = compute()
        K = compose()
        R["rows"] = rows(R)
        R["preds"] = predicates(R, K)
    except (Refused, RC.Refused) as e:
        sys.stderr.write("l8p_cprot: REFUSED: %s\n" % e)
        return 3
    sys.stdout.write(render(R, K))
    return 0


if __name__ == "__main__":
    sys.exit(main())
