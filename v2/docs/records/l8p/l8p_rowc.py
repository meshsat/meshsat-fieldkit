#!/usr/bin/env python3
"""l8p_rowc.py: record l8p, round 10 (Layer 4 AI-scope register row (c), tasks L4A-66 and L4A-65; MESHSAT-1357, 7 October 2026).

L4A-66, RE-10 and HO-A by method M-A (selected by record l4e11's decision L4E11-FET-D2, branch fnd/l4fet at 49d4f9e6): every series
part of the pack path held INDEFINITELY at the breaker's held 23.93 A from the 76.25 C inside air inside its PRINTED limits, the
battery FETs at most 150 C on the printed Zth and the printed RDS(on) at temperature, so that a latent failure of the thermal guard no
longer removes a protection a part needs. L4A-65, HO-B: path 2's retry energy alone (43.8 ms on in every 0.154 s or more, current up
to the breaker's limit, 76.25 C air) on the FETs' printed Zth: the junction's rise per on-time and its steady periodic peak bounded
against 150 C; a bound read on a typical curve FAILS.

This script prints:
  0. its pins (the records and the makers' documents it reads, sha256);
  1. the case and the acceptance (RECORD: records l9stk, l4e11 and l8p, read from this tree, never retyped);
  2. M-A for the guard's own parts: the three BUK6Y10-30P on printed maxima (the RDS(on) allowance reproduced from the printed rows,
     the junction-to-mounting-base lead on the printed Rth(j-mb) maximum, the installed path at E-1's bar and at E11-29's design
     target), the printed Zth curve read from the sheet's own vector drawing and classed, the pour and the vias, and R17 on ROHM's
     printed derating (the sheet read here for the first time: GMR100 HJ, rev. 006E);
  3. M-A for every other series part: the three 25 A MINI blades on Littelfuse's printed temperature rerating curve (read from the
     sheet's vector drawing) and their Keystone 3568 holders, the corrections compared for the blades, the dock block's spring pins,
     the XT60, the 12 AWG wires, board P's switches, shunts and F2, and the cells;
  4. which rows the guard ever protected (the exposure of page 12o restated: its 20.53 A is the pair's figure);
  5. L4A-65: path 2's retry train on the printed Zth (the rise per on-time, the steady periodic peak, the typical curve refused);
  6. the verdicts: M-A's acceptance part by part, what M-A closes once checked, what stays CONDITIONAL, M-B's entry condition;
  7. the predicates.
Labels: PRINTED (a maker's printed limit or maximum), TYPICAL (a maker's typical figure or an unlabelled curve, never a limit),
READING (this record's reading of a maker's drawing, from its vector paths), INFERRED (arithmetic on printed figures by a stated
rule), MODEL (a record's conductor model), RECORD (another record's figure, read from its file), ASSUMED. Nothing has been built,
bought or measured; no V2 board exists.

Run from anywhere:  python3 v2/docs/records/l8p/l8p_rowc.py   (l8p_rowc.out is its output, regenerated with _bin/regen_out.py).
Exit 0: printed, whatever the verdicts; 3: refused (an input missing, a sha256 that differs, a printed row not found on its page, a
guard tripped)."""
import hashlib
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


class Refused(Exception):
    pass


class GuardError(Exception):
    """A typical figure or an unlabelled curve offered as a limit."""


# ---------------------------------------------------------------- inputs (path, sha256)
RECS = {
    "prot": ("v2/docs/records/l9stk/l9stk_protection.out", None),
    "stk": ("v2/docs/records/l9stk/L9-STACKUPS.md", None),
    "e11": ("v2/docs/records/l4e11/l4e11_power.out", None),
    "fet": ("v2/docs/records/l4e11/l4e11_fet.out", None),
    "c4": ("v2/docs/records/l8p/l8p_c4.out", None),
    "brk": ("v2/docs/records/l8p/L8P-BREAKER.md", None),
    "gen_a": ("v2/ecad/tools/gen_sch_a.py", None),
    "gen_e": ("v2/ecad/tools/gen_sch_e.py", None),
    "gen_p": ("v2/ecad/tools/gen_sch_p.py", None),
    "chg": ("v2/docs/records/l4e11/apply_gen_sch_a_charger.py", None),
    "pbrk": ("v2/docs/records/l8p/apply_gen_sch_p_breaker.py", None),
}
DOCS = {
    "buk": ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf",
            "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40",
            "Nexperia BUK6Y10-30P product data sheet, 17 April 2020 (held back, records/l4e11/fetch_held_back.py)"),
    "gmr": ("v2/vendor/passives/held/rohm-gmr100hj-rev006e-2026-03-05.pdf",
            "3b5ac7258851583c154cc33c7ec7b8be4768702f633402ab72341c42ca525266",
            "ROHM GMR100 HJ series datasheet, Rev. GMR100J-IA-006E, 5 March 2026 (held back, fetch_held_back_rowc.py)"),
    "lf297": ("v2/vendor/keystone/littelfuse-297-ficcorp.pdf",
              "98a7e99bc5bbdf2abc9f329de5b779ea97fc78a3ba9aa8d8fecc0ec5b9c3a778",
              "Littelfuse MINI blade fuse rated 32 V (297 series)"),
    "ks": ("v2/vendor/keystone/M65p42.pdf",
           "caa141ea51ac68cf80ab6e14ad2075fcfc76206451f4bfe45330005c0deaf395",
           "Keystone catalogue M65, page 42 (MINI fuse clips and holders)"),
    "mm": ("v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf",
           "8ef40cd98d95c653ce506a1af457656b287a475342684ac110cf594f923782d6",
           "Mill-Max PR617 and catalogue page 28 (085X power spring pins)"),
    "mm58": ("v2/vendor/connectors/millmax-0858-product-page-20260927.html",
             "7a11ec390b01e69fd2fca595260d60a5aca2bd1f5b83a20670b30ad11ccc4883",
             "Mill-Max 0858 product page, read 27 September 2026"),
    "xt60": ("v2/vendor/battery/amass-xt60-spec-tme.pdf",
             "c2cbb5962c1f37da89e76e505c75184dd07e84eec3a6fe5f24569dafc6f6b9e9",
             "Amass specification, XT60-F and XT60-M"),
    "xt60b": ("v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf",
              "94e4568e3abe8ab516137588aea475872c0714cc2cc357be52e3a80e842c1780",
              "Amass XT60 product specification, version 2021V1 (LCSC C98733)"),
    "q1": ("v2/vendor/battery/ti-csd17570q5b.pdf",
           "596555c33dce1fcac6de3b6ecc3eeb443f202382b3e2091fd6e1c27d129f2436", "TI CSD17570Q5B"),
    "q101": ("v2/vendor/battery/ti-csd18510q5b.pdf",
             "cb747de812f6685995917335ec78c663fbf1cee0942db9a3e5b1c375147a601a", "TI CSD18510Q5B"),
    "scf": ("v2/vendor/battery/eaton-scf9550-elx1135.pdf",
            "3ecc2424acfa1753c2aec0b62d5706d4f25b7a08e731795c0d84d59938a3158e", "Eaton SCF9550 data sheet ELX1135"),
}

# ---------------------------------------------------------------- the readings of the makers' drawings (READING, vector paths)
# BUK6Y10-30P Fig. 4 (page 5), in the page coordinates pdftocairo's SVG gives: the decade grid lines (each read back below), and the
# eight curves' order by their start, top to bottom, against the figure's own labels (duty cycle = 1, 0.70, 0.50, 0.30, 0.10, 0.05,
# 0.02, 0.01). The figure prints no single-pulse curve and does not say whether its curves are typical or maximum.
ZTH_X_DECADES = {-5: 93.559, -4: 175.055, -3: 256.551, -2: 338.047, -1: 419.543, 0: 501.039}
ZTH_Y_DECADES = {1: 203.059, 0: 256.32, -1: 309.582, -2: 362.855}
ZTH_DUTIES = (1.0, 0.70, 0.50, 0.30, 0.10, 0.05, 0.02, 0.01)
# Littelfuse 297, page 2, the Temperature Rerating Curve: the grid (-40 to 140 C every 20 C; 70 to 120 % every 5 %), read back below.
RR_X = (361.918, 558.031, -40.0, 140.0)
RR_Y = (178.898, 323.949, 120.0, 70.0)

# ---------------------------------------------------------------- the case's constants that are not another record's figure
T_LIMIT = 150.0            # the battery FETs' limit (25 K under the BUK6Y10-30P's printed 175 C rating; records l9stk, l4e11)
N_FETS = 3                 # Q39, Q40, Q42 (L4-E11's charger draft, the drawn three, decision L4E11-FET-D1)
BLADE_A = 25.0             # the three blades' rating (gen_sch_a/e/p.py value texts, read back below)
SERVICE_A = 18.0           # the 18 A transient service (PWR-F12; C-PROT rev 1)


def refuse(msg):
    raise Refused(msg)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def p(rel):
    return os.path.join(ROOT, rel)


def read(rel):
    if not os.path.exists(p(rel)):
        refuse("missing input %s" % rel)
    with open(p(rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def doc(key):
    rel, want, _what = DOCS[key]
    if not os.path.exists(p(rel)):
        refuse("missing maker's document %s (%s)" % (rel, _what))
    got = sha(p(rel))
    if got != want:
        refuse("%s: sha256 %s, pinned %s" % (rel, got[:16], want[:16]))
    return p(rel)


def pdftext(key, page):
    r = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), doc(key), "-"], capture_output=True)
    if r.returncode != 0:
        refuse("pdftotext failed on %s page %d" % (DOCS[key][0], page))
    return r.stdout.decode("utf-8", "replace")


def row(key, page, *tokens):
    """A printed row read back: every token on one line of the page's text (pdftotext -layout)."""
    for line in pdftext(key, page).splitlines():
        if all(t in line for t in tokens):
            return line
    refuse("%s page %d: no line carries %r" % (DOCS[key][0], page, tokens))


def svg_paths(key, page):
    """The page's stroked paths in page coordinates (pdftocairo -svg): (style, [segments]) with each segment ('L', p0, p1) or
    ('C', p0, c1, c2, p3)."""
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "p.svg")
        r = subprocess.run(["pdftocairo", "-svg", "-f", str(page), "-l", str(page), doc(key), out], capture_output=True)
        if r.returncode != 0 or not os.path.exists(out):
            refuse("pdftocairo failed on %s page %d" % (DOCS[key][0], page))
        with open(out, encoding="utf-8") as f:
            s = f.read()
    paths = []
    for m in re.finditer(r'<path style="([^"]*)" d="([^"]*)"(?: transform="matrix\(([^)]*)\)")?', s):
        st, d, tr = m.groups()
        if "fill:none" not in st:
            continue
        a, b, c, dd, e, f = [float(x) for x in tr.split(",")] if tr else (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        toks = re.findall(r"[MLCZ]|-?[0-9.]+(?:e-?[0-9]+)?", d)
        segs, cur, i = [], None, 0

        def pt(i):
            x, y = float(toks[i]), float(toks[i + 1])
            return (a * x + c * y + e, b * x + dd * y + f)
        while i < len(toks):
            t = toks[i]
            if t == "M":
                cur = pt(i + 1); i += 3
            elif t == "L":
                q = pt(i + 1); segs.append(("L", cur, q)); cur = q; i += 3
            elif t == "C":
                c1, c2, q = pt(i + 1), pt(i + 3), pt(i + 5); segs.append(("C", cur, c1, c2, q)); cur = q; i += 7
            elif t == "Z":
                i += 1
            else:
                i += 1
        sw = re.search(r"stroke-width:([0-9.]+)", st)
        paths.append((float(sw.group(1)) if sw else 0.0, st, segs))
    return paths


def bez(seg, s):
    _k, p0, c1, c2, p3 = seg
    u = 1 - s
    return tuple(u ** 3 * p0[i] + 3 * u * u * s * c1[i] + 3 * u * s * s * c2[i] + s ** 3 * p3[i] for i in (0, 1))


def y_at_x(segs, x):
    """The path's y where it passes x (the curves run left to right; a segment is solved by bisection)."""
    for sg in segs:
        x0, x1 = sg[1][0], sg[-1][0]
        if min(x0, x1) - 1e-9 <= x <= max(x0, x1) + 1e-9:
            if sg[0] == "L":
                t = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
                return sg[1][1] + t * (sg[2][1] - sg[1][1])
            lo, hi = 0.0, 1.0
            for _ in range(60):
                mid = (lo + hi) / 2
                if (bez(sg, mid)[0] - x) * (x1 - x0) < 0:
                    lo = mid
                else:
                    hi = mid
            return bez(sg, (lo + hi) / 2)[1]
    return None


def num(text, pattern, what, group=1):
    m = re.search(pattern, text, re.S)
    if not m:
        refuse("%s: pattern not found (%s)" % (what, pattern[:60]))
    return float(m.group(group))


def limit(value, cls, what):
    """A value offered as a limit: refused unless its class is a printed maximum (or an INFERRED bound on printed maxima)."""
    if cls not in ("PRINTED", "INFERRED"):
        raise GuardError("%s: a %s figure is not a limit" % (what, cls))
    return value


# ---------------------------------------------------------------- the computation
def compute(zth_class=None):
    R = {"pins": []}
    for k, (rel, _w) in RECS.items():
        R["pins"].append((sha(p(rel))[:16] if os.path.exists(p(rel)) else "MISSING", rel))
        read(rel)
    for k, (rel, _w, what) in DOCS.items():
        doc(k)
        R["pins"].append((sha(p(rel))[:16], rel))

    # 1. the case (RECORD)
    prot, e11, c4, stk, brk, fetout = (read(RECS[k][0]) for k in ("prot", "e11", "c4", "stk", "brk", "fet"))
    I = num(prot, r"at most 150 C held at ([0-9.]+) A from ([0-9.]+) C, the band carrying the current \(([0-9.]+) K", "the held current")
    T_AIR = num(prot, r"at most 150 C held at ([0-9.]+) A from ([0-9.]+) C, the band", "the air", 2)
    BAND = num(prot, r"the band carrying the current \(([0-9.]+) K", "the band")
    BUDGET = num(prot, r"the budget for the FETs and R17's coupling is ([0-9.]+) K", "the budget")
    EVEN_BAR_REC = num(prot, r"three \(Zself \+ 2 Zmut\)\s+[0-9.]+ W each: FETs only [0-9.]+ K/W; R17 apart ([0-9.]+) K/W", "the even-split bar")
    BAR = num(e11, r"each FET's \(Zself \+ 2 Zmut\) at most ([0-9.]+) K/W steady", "E-1's worst-split bar")
    ZW_TGT = num(e11, r"each junction's worst-split figure Zw at most ([0-9.]+) K/W", "E11-29's design target")
    RC_TGT = num(e11, r"R17's coupling at most ([0-9.]+) K/W, so lines 1 and 2", "R17's coupling target")
    RC_MAX = num(e11, r"R17's coupling into each junction at most ([0-9.]+) K/W", "R17's coupling allowance")
    LIMIT_RISE = num(e11, r"at most ([0-9.]+) K over the air, and the same read directly", "E11-29's limit over the air")
    ON_MS = num(c4, r"the FETs carry current at most ([0-9.]+) ms in every ([0-9.]+) s or more", "path 2's on-time")
    PERIOD = num(c4, r"the FETs carry current at most ([0-9.]+) ms in every ([0-9.]+) s or more", "path 2's period", 2)
    HOLD = num(c4, r"no sooner than the RC hold's least ([0-9.]+) s", "the RC hold")
    TRIP_DIE = num(c4, r"surely tripped from ([0-9.]+) C at the die", "the guard's sure trip")
    NOTRIP_DIE = num(c4, r"10 A held [0-9.]+ C, [0-9.]+ K under ([0-9.]+) C", "the guard's no-trip limit")
    EXPO_PAIR = num(c4, r"without any guard the battery FETs reach 150 C held at ([0-9.]+) A", "page 12o's exposure")
    PAIR_EXPO_SRC = num(prot, r"150 C held at [0-9.]+ A from the \+70 C line and ([0-9.]+) A from 76.25 C", "record l9stk's pair figure")
    BAND_LIMIT_A = re.search(r"\| board A's pack bands \| ([0-9]+) C \| ([0-9]+) C \|", stk)
    BAND_LIMIT_E = re.search(r"\| board E's pack bands \| ([0-9]+) C \| ([0-9]+) C \|", stk)
    if not (BAND_LIMIT_A and BAND_LIMIT_E):
        refuse("L9-STACKUPS.md: the band limits' rows not found")
    BARREL_A = num(prot, r"the barrel field \(16 of 0.4 mm\)\s+([0-9.]+) A a barrel, ([0-9.]+) K", "the barrel field")
    BARREL_K = num(prot, r"the barrel field \(16 of 0.4 mm\)\s+([0-9.]+) A a barrel, ([0-9.]+) K", "the barrel field", 2)
    Q1_REC = re.search(r"\(CSD17570Q5B, 0.69 mOhm at 10 V, RthJA 50 C/W\) ([0-9.]+) W each; TJ ([0-9.]+) C on its own pad, ([0-9.]+) C with both losses through one pad", prot)
    Q101_REC = re.search(r"the breaker's FETs \(2 x CSD18510Q5B\)\s+([0-9.]+) W each; TJ ([0-9.]+) C", prot)
    R10_REC = num(prot, r"R10 on board P \(2 mOhm 2512, 2 W\)\s+([0-9.]+) W", "R10's loss")
    SNS_REC = re.search(r"([0-9.]+) W in 4 mOhm; ([0-9.]+) W in 7.5 mOhm", prot)
    if not (Q1_REC and Q101_REC and SNS_REC):
        refuse("l9stk_protection.out: a board P row not found")
    if "the breaker's held 23.93 A" not in brk:
        refuse("L8P-BREAKER.md: 'the breaker's held 23.93 A' not found")
    if abs(I - 23.93) > 1e-9:
        refuse("the held current read %.2f A, not the breaker's 23.93 A" % I)
    R.update(I=I, T_AIR=T_AIR, BAND=BAND, BUDGET=BUDGET, EVEN_BAR_REC=EVEN_BAR_REC, BAR=BAR, ZW_TGT=ZW_TGT, RC_TGT=RC_TGT,
             RC_MAX=RC_MAX, LIMIT_RISE=LIMIT_RISE, ON_MS=ON_MS, PERIOD=PERIOD, HOLD=HOLD, TRIP_DIE=TRIP_DIE,
             NOTRIP_DIE=NOTRIP_DIE, EXPO_PAIR=EXPO_PAIR, PAIR_EXPO_SRC=PAIR_EXPO_SRC,
             BAND_LIM_A=(float(BAND_LIMIT_A.group(1)), float(BAND_LIMIT_A.group(2))),
             BAND_LIM_E=(float(BAND_LIMIT_E.group(1)), float(BAND_LIMIT_E.group(2))),
             BARREL_A=BARREL_A, BARREL_K=BARREL_K,
             Q1_REC=tuple(float(x) for x in Q1_REC.groups()), Q101_REC=tuple(float(x) for x in Q101_REC.groups()),
             R10_REC=R10_REC, SNS_REC=tuple(float(x) for x in SNS_REC.groups()))
    m3 = re.search(r"the three's even split ([0-9.]+) K/W \(record ([0-9.]+)\), the worst split ([0-9.]+) K/W", fetout)
    if not m3:
        refuse("l4e11_fet.out: the reproduced bars not found")
    R["FET_OUT"] = tuple(float(x) for x in m3.groups())

    # the drawn parts, read from the generators and drafts (their value texts)
    gen_a, gen_e, gen_p, chg, pbrk = (read(RECS[k][0]) for k in ("gen_a", "gen_e", "gen_p", "chg", "pbrk"))
    for txt, ref, what in ((gen_a, 'part("F1", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder)', "board A's F1"),
                           (gen_e, 'part("F3", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder)', "board E's F3"),
                           (gen_p, 'part("F1", "Device", "Fuse", "25 A mini blade (Keystone 3568 holder)', "board P's F1"),
                           (gen_a, 'r("R17", "5mOhm 1% 2512 (RSR, charge current sense)"', "board A's R17"),
                           (gen_a, 'part("J_CP%d" % k, "Connector", "Conn_01x01_Pin", "9 A spring pin, CELL+ (Mill-Max 0858 class', "J_CP1 to J_CP4"),
                           (gen_e, '"Amass XT60-M', "board E's J_BATT"),
                           (gen_p, 'SCF9550-30-05 self-control fuse (Eaton, 30 A', "board P's F2"),
                           (gen_p, 'pfet5("Q1", "CSD17570Q5B 30 V N-FET, charge switch"', "board P's Q1"),
                           (gen_p, 'r("R10", "2m 2512 2W (sense)"', "board P's R10"),
                           (chg, '"CH_BATQ", 14.4, 10.0, 18.0, "R17"', "CH_BATQ from R17 to the three"),
                           (pbrk, 'r("R101", "4m 1% 2512', "board P's R101"),
                           (pbrk, 'pfet5("Q101", "CSD18510Q5B 40 V N-FET, breaker pass', "board P's Q101")):
        if ref not in txt:
            refuse("%s: %r not found" % (what, ref[:60]))

    # 2a. the battery FETs on printed maxima
    r25 = float(row("buk", 6, "VGS = -10 V; ID = -13.5 A; Tj = 25", "8", "10").split()[-2])
    r175 = float(row("buk", 6, "VGS = -10 V; ID = -13.5 A; Tj = 175", "13", "16").split()[-2])
    r45 = float(row("buk", 6, "VGS = -4.5 V; ID = -8.5 A; Tj = 25", "19", "25").split()[-2])
    rthjmb = row("buk", 5, "Rth(j-mb)", "1.1", "1.4").split()
    rth_typ, rth_max = float(rthjmb[-3]), float(rthjmb[-2])
    tj_rating = float(row("buk", 3, "Tj", "junction temperature", "175").split()[-2])
    if (r25, r175, r45, rth_typ, rth_max, tj_rating) != (10.0, 16.0, 25.0, 1.1, 1.4, 175.0):
        refuse("BUK6Y10-30P rows read %r" % ((r25, r175, r45, rth_typ, rth_max, tj_rating),))
    hot = 1 + (r175 / r25 - 1) * (T_LIMIT - 25) / (175 - 25)                      # the temperature chord (E11-36)
    gate = 1 + (r45 / r25 - 1) * (10 - 8.5) / (10 - 4.5)                         # the drive chord at BATDRV's least 8.5 V
    RA = r25 * hot * gate * 1e-3
    P_even = (I / N_FETS) ** 2 * RA
    P_hot = P_even * N_FETS ** 2 / (4 * (N_FETS - 1))                             # one FET at R/2 (round 11's worst split, F0 = 9/8)
    lead = P_hot * limit(rth_max, "PRINTED", "Rth(j-mb)")
    R17_NOM = 5.0e-3
    P17_nom = I ** 2 * R17_NOM
    zbar_even = (BUDGET - RC_MAX * P17_nom) / P_even
    TJ_bar = T_AIR + BAND + RC_MAX * P17_nom + P_even * zbar_even
    TJ_tgt = T_AIR + BAND + RC_TGT * P17_nom + P_even * ZW_TGT
    k_tgt = (T_LIMIT - T_AIR) / (BAND + RC_TGT * P17_nom + P_even * ZW_TGT)
    I150_tgt = I * math.sqrt(k_tgt)
    R.update(r25=r25, r175=r175, r45=r45, rth_typ=rth_typ, rth_max=rth_max, tj_rating=tj_rating, hot=hot, gate=gate, RA=RA,
             P_even=P_even, P_hot=P_hot, lead=lead, P17_nom=P17_nom, zbar_even=zbar_even, TJ_bar=TJ_bar, TJ_tgt=TJ_tgt,
             I150_tgt=I150_tgt, ID_hot=I * 2 / (N_FETS + 1), ID_row=13.5)

    # 2b. the printed Zth curve, read from the drawing (READING)
    paths = svg_paths("buk", 5)
    grid_x = [round(sg[1][0], 3) for w, st, sgs in paths for sg in sgs if sg[0] == "L" and abs(sg[1][0] - sg[2][0]) < 0.01]
    grid_y = [round(sg[1][1], 3) for w, st, sgs in paths for sg in sgs if sg[0] == "L" and abs(sg[1][1] - sg[2][1]) < 0.01]
    for v in ZTH_X_DECADES.values():
        if not any(abs(v - g) < 0.01 for g in grid_x):
            refuse("BUK6Y10-30P Fig. 4: no vertical grid line at %.3f" % v)
    for v in ZTH_Y_DECADES.values():
        if not any(abs(v - g) < 0.01 for g in grid_y):
            refuse("BUK6Y10-30P Fig. 4: no horizontal grid line at %.3f" % v)
    curves = [sgs for w, st, sgs in paths if abs(w - 1.08) < 1e-6 and sgs and all(s[0] == "C" for s in sgs)]
    if len(curves) != len(ZTH_DUTIES):
        refuse("BUK6Y10-30P Fig. 4: %d curves, %d labels" % (len(curves), len(ZTH_DUTIES)))
    curves.sort(key=lambda sgs: sgs[0][1][1])
    xd = sorted(ZTH_X_DECADES.items())
    yd = sorted(ZTH_Y_DECADES.items())
    xs = (xd[-1][1] - xd[0][1]) / (xd[-1][0] - xd[0][0])
    ys = (yd[0][1] - yd[-1][1]) / (yd[-1][0] - yd[0][0])

    def zth(duty, tp):
        c = curves[ZTH_DUTIES.index(duty)]
        x = xd[0][1] + (math.log10(tp) - xd[0][0]) * xs
        y = y_at_x(c, x)
        if y is None:
            refuse("Fig. 4: tp %.3g s outside the drawn curve" % tp)
        return 10 ** ((ZTH_Y_DECADES[0] - y) / ys)
    x_lo = max(min(sg[1][0] for sg in c) for c in curves)
    x_hi = min(max(sg[-1][0] for sg in c) for c in curves)
    tp_lo = 10 ** (xd[0][0] + (x_lo - xd[0][1]) / xs) * 1.0001
    tp_hi = 10 ** (xd[0][0] + (x_hi - xd[0][1]) / xs) / 1.0001
    tps = [tp_lo * (tp_hi / tp_lo) ** (k / 200.0) for k in range(201)]
    z1 = [zth(1.0, t) for t in tps]
    zmax_all = max(zth(d, t) for d in ZTH_DUTIES for t in tps)
    on = ON_MS * 1e-3
    duty_train = on / PERIOD
    z_on_03, z_on_01 = zth(0.30, on), zth(0.10, on)
    z_on_train = z_on_01 + (z_on_03 - z_on_01) * (duty_train - 0.10) / (0.30 - 0.10)
    zcls = zth_class or ("PRINTED" if zmax_all >= rth_max - 1e-9 else "TYPICAL")
    R.update(tp_lo=tp_lo, tp_hi=tp_hi, z_end=z1[-1], z_start=z1[0], zmax_all=zmax_all, z_on_03=z_on_03, z_on_01=z_on_01, z_on_train=z_on_train,
             duty_train=duty_train, zcls=zcls, z_1s=zth(1.0, tp_hi), z_10ms=zth(1.0, 0.01))

    # 2c. R17 on ROHM's printed derating
    rated = row("gmr", 1, "RATED", "7W")
    p7, tk7 = 7.0, 70.0
    if "at Tk=70" not in pdftext("gmr", 1) or "at Tk=110" not in pdftext("gmr", 1) or "5W" not in pdftext("gmr", 1):
        refuse("GMR100: the two rated-power rows not found")
    t1 = pdftext("gmr", 1)
    if "-65" not in t1 or "+170" not in t1 or "170°C" not in t1 or "F (±1%)" not in t1:
        refuse("GMR100: the operating range, the derating's end or the tolerance not found")
    t2 = pdftext("gmr", 2)
    if not re.search(r"5m≦R<10m\s+JA\s+0～\+50 \(20 to 60°C\)", t2):
        refuse("GMR100: the JA temperature coefficient row not found")
    if not re.search(r"5mΩ\s+A\s+D\s+5L00", t2):
        refuse("GMR100: the 5 mOhm ordering row (A, D, 5L00) not found")
    p5, tk5, tk_end = 5.0, 110.0, 170.0
    tol, tcr = 0.01, 50e-6
    R17_MAX = R17_NOM * (1 + tol)

    def p17(tk):
        return I ** 2 * R17_MAX * (1 + tcr * max(0.0, tk - 60.0))           # the TCR above 60 C ASSUMED to continue

    def allowed(tk):
        a1 = p7 if tk <= tk7 else p7 * (tk_end - tk) / (tk_end - tk7)
        a2 = p5 if tk <= tk5 else p5 * (tk_end - tk) / (tk_end - tk5)
        return min(a1, a2)
    lo, hi = 25.0, tk_end
    for _ in range(80):
        mid = (lo + hi) / 2
        if p17(mid) <= allowed(mid):
            lo = mid
        else:
            hi = mid
    tk_max = lo
    t_band_a = T_AIR + BAND
    R.update(rated_row=rated.strip(), R17_MAX=R17_MAX, P17_20=I ** 2 * R17_MAX, P17_tk=p17(tk_max), tk_max=tk_max,
             tk_head=tk_max - t_band_a, r17_req=(tk_max - t_band_a) / p17(tk_max), t_band_a=t_band_a,
             tk_fig2_only=tk_end - (tk_end - tk5) * p17(tk_max) / p5, p17_at_band=p17(t_band_a), allow_at_band=allowed(t_band_a))

    # 3a. the blades on the printed rerating curve (READING of the vector line)
    lf2 = pdftext("lf297", 2)
    if not re.search(r"0297025\._\s+25 A\s+86 mV\s+2\.36 m\S\s+625 A", lf2) or "Temperature Rerating Curve" not in lf2:
        refuse("Littelfuse 297 page 2: the 0297025 row or the rerating curve's title not found")
    lf1 = pdftext("lf297", 1)
    for tok in ("110", "360,000 s", "135", "0.75 s / 600 s", "1000A @ 32 VDC", "-40˚C to +125˚C (Sn=-40˚C to +105˚C)"):
        if tok not in lf1:
            refuse("Littelfuse 297 page 1: %r not found" % tok)
    lp = svg_paths("lf297", 2)
    gx = [round(sg[1][0], 3) for w, st, sgs in lp for sg in sgs if sg[0] == "L" and abs(sg[1][0] - sg[2][0]) < 0.01]
    gy = [round(sg[1][1], 3) for w, st, sgs in lp for sg in sgs if sg[0] == "L" and abs(sg[1][1] - sg[2][1]) < 0.01]
    for v in (RR_X[0], RR_X[1]):
        if not any(abs(v - g) < 0.01 for g in gx):
            refuse("297 rerating grid: no vertical line at %.3f" % v)
    for v in (RR_Y[0], RR_Y[1]):
        if not any(abs(v - g) < 0.01 for g in gy):
            refuse("297 rerating grid: no horizontal line at %.3f" % v)
    green = [sgs for w, st, sgs in lp if "stroke:rgb(0%,51.519775%,31.459045%)" in st and len(sgs) == 1 and sgs[0][0] == "L"
             and RR_X[0] - 1 < sgs[0][1][0] < RR_X[1] and RR_Y[0] < sgs[0][1][1] < RR_Y[1]]
    if len(green) != 1:
        refuse("297 rerating curve: %d candidate lines" % len(green))
    (_k, a0, a1), = green[0]

    def tx(x):
        return RR_X[2] + (x - RR_X[0]) * (RR_X[3] - RR_X[2]) / (RR_X[1] - RR_X[0])

    def ty(y):
        return RR_Y[2] + (y - RR_Y[0]) * (RR_Y[3] - RR_Y[2]) / (RR_Y[1] - RR_Y[0])
    T0, F0r, T1, F1r = tx(a0[0]), ty(a0[1]), tx(a1[0]), ty(a1[1])

    def rerate(t):
        if not (T0 - 1e-6 <= t <= T1 + 1e-6):
            refuse("the rerating curve is drawn from %.2f to %.2f C only" % (T0, T1))
        return (F0r + (F1r - F0r) * (t - T0) / (T1 - T0)) / 100.0
    f_air, f_band, f_25 = rerate(T_AIR), rerate(t_band_a), rerate(25.0)
    I_rr_air, I_rr_band = BLADE_A * f_air, BLADE_A * f_band
    sc_rr = (I_rr_air / I) ** 2
    R.update(TJ_rr_tgt=T_AIR + sc_rr * (BAND + RC_TGT * P17_nom + P_even * ZW_TGT), mb_rr_tgt=T_AIR + sc_rr * (BAND + RC_TGT * P17_nom + P_even * ZW_TGT - lead))
    R.update(T0=T0, F0r=F0r, T1=T1, F1r=F1r, f_air=f_air, f_band=f_band, f_25=f_25, I_rr_air=I_rr_air, I_rr_band=I_rr_band,
             over_air=I / I_rr_air - 1, over_band=I / I_rr_band - 1, over_air_a=I - I_rr_air, over_band_a=I - I_rr_band,
             hold110=1.10 * I_rr_air, blade30_rr=30.0 * f_air, blade30_frac=I / (30.0 * f_air), blade25_135=1.35 * BLADE_A,
             blade30_135=1.35 * 30.0, f_18=SERVICE_A / I_rr_air)
    ks = pdftext("ks", 1)
    if "CAT. NO. 3568" not in ks or ks.count("UL Current Rating: 30 Amps @ 500V AC") < 2 or "(-50°C to+145°C)" not in ks:
        refuse("Keystone M65 p.42: the 3568's ratings not found")
    R.update(hold_a=30.0, hold_t=145.0, hold_frac=I / 30.0)

    # 3b. the breaker's limit tightened (correction (c)): the LM5069's printed VCL 48.5 to 61.5 mV (record l9stk 15.3, read there)
    VCL_MIN, VCL_MAX = 48.5, 61.5
    if "16.5 us to the release" not in prot or "242.9 A peak, time constant 33.8 us" not in e11:
        refuse("the over-limit single events' rows not found (l9stk_protection.out, l4e11_power.out E11-30)")
    if "current limit 18.32 / 21.08 / 23.93 A (VCL 48.5 to 61.5 mV" not in prot:
        refuse("l9stk_protection.out: the breaker's limits row not found")
    R.update(vcl_ratio=VCL_MIN / VCL_MAX, need_ratio_margin=18.32 / I_rr_air, need_ratio_bare=SERVICE_A / I_rr_air,
             rs_lo=VCL_MAX / I_rr_air, rs_hi_margin=VCL_MIN / 18.32, rs_hi_bare=VCL_MIN / SERVICE_A)

    # 3c. the spring pins
    mmt = pdftext("mm", 1)
    if "capable of carrying 9 amps continuous cur-" not in mmt or "rent at a low 10° C temperature rise" not in mmt:
        refuse("Mill-Max PR617: the 9 A at 10 C rise sentence not found")
    m58 = read(DOCS["mm58"][0])
    doc("mm58")
    if "Operating Temperature Range: </span>" not in m58 and "-55/+125" not in m58:
        refuse("Mill-Max 0858 page: the operating range not found")
    if "82 - 12 Amp High Force Stainless Steel" not in m58:
        refuse("Mill-Max 0858 page: the spring 82 row not found")
    pin_a, pin_rise, pin_tmax, n_pins = 9.0, 10.0, 125.0, 4
    share = pin_a / I
    ratio = (1 - share) / ((n_pins - 1) * share)
    R.update(pin_even=I / n_pins, pin_ratio=ratio, pin_at9=t_band_a + pin_rise, pin_tmax=pin_tmax)

    # 3d. the XT60
    xa = pdftext("xt60", 1)
    xb = pdftext("xt60b", 1)
    if "30A" not in xa or "-20℃ to 120℃" not in xa:
        refuse("XT60 (TME): the rated current or the range not found")
    if "35A MAX（12AWG/△＜85℃）" not in xb or "≤1.0mΩ" not in xb:
        refuse("XT60 (2021V1): the 35 A row or the contact resistance not found")
    xt_rise = 85.0 * (I / 35.0) ** 2
    R.update(xt_frac=I / 30.0, xt_rise=xt_rise, xt_t=T_AIR + xt_rise, xt_margin=120.0 - (T_AIR + xt_rise),
             xt_p=I ** 2 * 1.0e-3)

    # 3f. board P's switches on TI's printed rows
    qa = pdftext("q1", 1)
    qb = pdftext("q101", 1)
    if not re.search(r"VGS = 10 V, ID = 50 A\s+0\.56\s+0\.69\s", pdftext("q1", 3)):
        refuse("CSD17570Q5B: the 10 V RDS(on) row not found")
    for k in ("q1", "q101"):
        if not re.search(r"R\S+JA\s+Junction-to-[Aa]mbient [Tt]hermal [Rr]esistance \(1\) \(2\)\s+50\b", pdftext(k, 3)):
            refuse("%s: the RthJA 50 C/W maximum row not found" % DOCS[k][0])
    if "\u201355 to 150" not in qa or "\u201355 to 150" not in qb:   # TI prints its minus as an en dash (U+2013)
        refuse("CSD17570Q5B or CSD18510Q5B: the junction range not found")
    q1_r = 0.69e-3
    m = re.search(r"VGS = 10 V, ID = 32 A\s+([0-9.]+)\s+([0-9.]+)", pdftext("q101", 3))
    if not m:
        refuse("CSD18510Q5B: the 10 V RDS(on) row not found")
    q101_r = float(m.group(2)) * 1e-3
    rja = 50.0
    q1_p25 = I ** 2 * q1_r
    q101_p25 = (I / 2) ** 2 * q101_r
    R.update(q1_r=q1_r, q101_r=q101_r, q1_p25=q1_p25, q101_p25=q101_p25,
             q1_k_own=(T_LIMIT - T_AIR) / (rja * q1_p25), q1_k_pad=(T_LIMIT - T_AIR) / (rja * 2 * q1_p25),
             q101_k150=(T_LIMIT - T_AIR) / (rja * 2 * q101_p25), q101_k125=(125.0 - T_AIR) / (rja * 2 * q101_p25),
             k_typ=1.8)
    sc = pdftext("scf", 4) + pdftext("scf", 2)
    if "+60" not in sc:
        refuse("SCF9550: the operating range's +60 C not found")
    R.update(scf_frac=I / 30.0, scf_over=T_AIR - 60.0)

    # 5. L4A-65: the retry train
    if abs(ON_MS / 1000.0 + HOLD - PERIOD) > 0.0015:
        refuse("the on-time and the hold do not make the period")
    R.update(rise_on_bound=P_hot * rth_max, rise_on_typ=P_hot * z_on_train, peak_bar=TJ_bar, peak_tgt=TJ_tgt,
             mean_frac=duty_train)
    try:
        limit(z_on_train, zcls, "Fig. 4 at %.1f ms" % ON_MS)
        R["typ_bound_refused"] = False
    except GuardError as e:
        R["typ_bound_refused"] = True
        R["typ_bound_msg"] = str(e)
    return R


# ---------------------------------------------------------------- the superposition bound used in section 5 (a property, tested)
def foster_peak(rs, taus, on, period, n_cycles, p_on):
    """The peak rise of a Foster network (sum of R_i (1 - exp(-t / tau_i))) under a train of n_cycles pulses (p_on for on, 0 for the
    rest of each period), sampled at every on-time's end: the largest rise the train reaches."""
    peak = 0.0
    state = [0.0] * len(rs)
    for _ in range(n_cycles):
        state = [r * p_on + (s - r * p_on) * math.exp(-on / t) for r, t, s in zip(rs, taus, state)]
        peak = max(peak, sum(state))
        state = [s * math.exp(-(period - on) / t) for t, s in zip(taus, state)]
    return peak


def render(R):
    o = []
    w = o.append
    w("l8p_rowc: record l8p round 10, Layer 4 register row (c): L4A-66 (RE-10 and HO-A by M-A) and L4A-65 (HO-B, path 2's retry energy)")
    w("(MESHSAT-1357, 7 October 2026). Desk arithmetic on the makers' printed figures and the records' own; nothing was built, bought or")
    w("measured. LABELS: PRINTED; TYPICAL (never a limit); READING (this record's reading of a maker's drawing from its vector paths);")
    w("INFERRED; MODEL (a record's conductor model); RECORD (another record's figure, read from its file); ASSUMED.")
    w("")
    w("0. PINS (sha256/16)")
    for h, rel in R["pins"]:
        w("   %s  %s" % (h, rel))
    w("")
    w("1. THE CASE AND THE ACCEPTANCE (RECORD)")
    w("   the breaker's held %.2f A from %.2f C (record l9stk B-P2; record l8p's breaker), the band %.2f K, R17 5 mOhm (%.3f W nominal) its" % (R["I"], R["T_AIR"], R["BAND"], R["P17_nom"]))
    w("     coupling into a junction at most %.1f K/W (E-1), the budget %.2f K for the FETs and R17's coupling (150 C less %.2f C and %.2f K)" % (R["RC_MAX"], R["BUDGET"], R["T_AIR"], R["BAND"]))
    w("   E-1's bar (L4-E11 E11-29): each FET's (Zself + 2 Zmut) at most %.2f K/W; the worst-split figure's limit %.2f K over the air; E11-29's" % (R["BAR"], R["LIMIT_RISE"]))
    w("     design target Zw at most %.2f K/W with R17's coupling at most %.2f K/W; record l9stk's even-split bar %.2f K/W" % (R["ZW_TGT"], R["RC_TGT"], R["EVEN_BAR_REC"]))
    w("   path 2's relaxation (record l8p 10c): the FETs carry current at most %.1f ms in every %.3f s or more; the RC hold's least %.3f s" % (R["ON_MS"], R["PERIOD"], R["HOLD"]))
    w("   M-A's acceptance (register row L4A-66; decision L4E11-FET-D2): every series part inside its PRINTED limits held indefinitely at %.2f A" % R["I"])
    w("     from %.2f C, the battery FETs at most %.0f C on the printed Zth and RDS(on) at temperature; a typical FAILS" % (R["T_AIR"], T_LIMIT))
    w("")
    w("2. M-A, THE GUARD'S OWN PARTS: Q39, Q40 AND Q42 (BUK6Y10-30P), THEIR POUR AND VIAS, R17")
    w("   2a. the FETs (PRINTED, Nexperia 17 April 2020): RDS(on) max %.0f mOhm at -10 V and 25 C (p.6), %.0f at 175 C, %.0f at -4.5 V and 25 C;" % (R["r25"], R["r175"], R["r45"]))
    w("       Rth(j-mb) %.1f typ, %.1f MAX K/W (p.5); Tj %.0f C (p.3), its limit here %.0f C" % (R["rth_typ"], R["rth_max"], R["tj_rating"], T_LIMIT))
    w("       the allowance at BATDRV's least -8.5 V and 150 C (INFERRED, two chords on printed maxima, E11-36): hot %.4f x drive %.4f: %.3f mOhm" % (R["hot"], R["gate"], R["RA"] * 1e3))
    w("       at %.2f A: %.4f W a FET on the even split; %.4f W in the hottest on the worst split (one at R/2, %.2f A, under the %.1f A row)" % (R["I"], R["P_even"], R["P_hot"], R["ID_hot"], R["ID_row"]))
    w("       the hottest junction over its mounting base on the printed Rth(j-mb) MAXIMUM: %.2f K (record l8p 12m: 2.12 K)" % R["lead"])
    w("       the even-split bar on the budget: %.2f K/W (record %.2f; record l4e11 round FET %.2f), the worst split's %.2f K/W (record %.2f)" % (R["zbar_even"], R["EVEN_BAR_REC"], R["FET_OUT"][0], R["zbar_even"] * 8 / 9, R["BAR"]))
    w("       the hottest junction held at %.2f A: at E-1's bar %.2f C (%.2f K under %.0f C, by construction); at E11-29's design target %.2f C" % (R["I"], R["TJ_bar"], T_LIMIT - R["TJ_bar"], T_LIMIT, R["TJ_tgt"]))
    w("         (%.2f K under %.0f C); at the design target the three reach %.0f C only at %.2f A held, over the breaker's %.2f A (INFERRED, the" % (T_LIMIT - R["TJ_tgt"], T_LIMIT, T_LIMIT, R["I150_tgt"], R["I"]))
    w("         150 C allowance kept at every current)")
    w("       the device's own figures are PRINTED maxima; the installed path (the pour, Zself and Zmut) is no maker's figure: it is E-1's bar,")
    w("         a layout requirement that E11-29's coupon decides (CONDITIONAL), and the allowance at -8.5 V rests on E11-36's chords; the three")
    w("         as a set rest on E-05 (TI's 5 nF, record l4e11 round FET)")
    w("   2b. the printed Zth curve, Fig. 4 (READING of its vector paths; %d curves, labelled duty 1 to 0.01; no single-pulse curve):" % len(ZTH_DUTIES))
    w("       duty 1: %.3f K/W at %.0f us, %.3f at 10 ms, %.3f at %.2f s; the largest of any curve %.3f K/W" % (R["z_start"], R["tp_lo"] * 1e6, R["z_10ms"], R["z_1s"], R["tp_hi"], R["zmax_all"]))
    w("       the curve never reaches the printed Rth(j-mb) maximum %.1f K/W and sits over its typical %.1f: it is not a maximum; the figure says" % (R["rth_max"], R["rth_typ"]))
    w("         neither typical nor maximum, so this record classes it %s (never a limit); a bound on it is refused (section 5)" % R["zcls"])
    w("   2c. the pour and the vias (MODEL: decision 35's conductor model in record l9stk; the limits are the parts' printed ones):")
    w("       the band carrying %.2f A: %.2f K over the air, %.2f C, against board A's band limit %.0f C as fitted (%.0f C with the blade's" % (R["I"], R["BAND"], R["t_band_a"], R["BAND_LIM_A"][0], R["BAND_LIM_A"][1]))
    w("         silver plating pinned): WITHIN; the barrel field at R17 (16 of 0.4 mm) %.2f A a barrel, %.2f K: WITHIN" % (R["BARREL_A"], R["BARREL_K"]))
    w("       CH_BATQ (R17 to the three) is a one-face hop at the parts' lands, inside E-1's installed path: E11-29's coupon carries the band and")
    w("         R17 in place; the laminate's own limit is NOT HELD (L9-STACKUPS 14.3)")
    w("   2d. R17 (PRINTED, ROHM GMR100 HJ, rev. 006E, 5 March 2026; GMR100HJAAFD5L00 = 5 mOhm, JA, F 1 %; first read by this record):")
    w("       rated 7 W at a terminal temperature Tk of 70 C, derated to 0 at 170 C (Fig. 1), or 5 W at Tk 110 C, derated to 0 at 170 C (Fig. 2);")
    w("       operating -65 to +170 C; TCR 0 to +50 ppm/C, printed for 20 to 60 C only (above 60 C ASSUMED to continue)")
    w("       at %.2f A on its printed maximum %.4f mOhm: %.3f W at 60 C, %.3f W at Tk %.1f C" % (R["I"], R["R17_MAX"] * 1e3, R["P17_20"], R["P17_tk"], R["tk_max"]))
    w("       the lower of the two printed derating lines admits it to Tk %.1f C (Fig. 2 alone would admit %.1f C): R17's terminals may rise" % (R["tk_max"], R["tk_fig2_only"]))
    w("         %.1f K over the band's %.2f C, so its terminal-to-band path at most %.1f K/W: a LAYOUT condition, read on E11-29's coupon with" % (R["tk_head"], R["t_band_a"], R["r17_req"]))
    w("         R17 dissipating in place; at the band's own temperature R17 is at %.0f %% of its derated power" % (100 * R["p17_at_band"] / R["allow_at_band"]))
    w("       record l9stk's '5 W printed at 25 C, derating NOT HELD (E-6)' is answered by the sheet: E-6 for R17 becomes the terminal reading above")
    w("")
    w("3. M-A, EVERY OTHER SERIES PART OF THE PACK PATH")
    w("   3a. the three 25 A MINI blades (board P's F1, board E's F3, board A's F1; 0297025, silver pinned), Littelfuse 297 (PRINTED):")
    w("       110 % holds 360,000 s at least; 135 % opens in 0.75 to 600 s; 1000 A at 32 V DC; -40 to +125 C (tin -40 to +105 C)")
    w("       the Temperature Rerating Curve (page 2; READING of its line: %.2f %% at %.2f C to %.2f %% at %.2f C, %.2f %% at 25 C):" % (R["F0r"], R["T0"], R["F1r"], R["T1"], 100 * R["f_25"]))
    w("         at the %.2f C air %.2f %%: the blade rated %.2f A; at the band's %.2f C %.2f %%: %.2f A" % (R["T_AIR"], 100 * R["f_air"], R["I_rr_air"], R["t_band_a"], 100 * R["f_band"], R["I_rr_band"]))
    w("       %.2f A held is %.1f %% of the rerated current at the air (OVER by %.2f A, %.1f %%), %.1f %% at the band (OVER by %.2f A)" % (R["I"], 100 * (1 + R["over_air"]), R["over_air_a"], 100 * R["over_air"], 100 * (1 + R["over_band"]), R["over_band_a"]))
    w("       what the sheet prints for it: no row between 100 %% and 110 %%; 110 %% of the rerated current (%.2f A, INFERRED reading of the table" % R["hold110"])
    w("         on the rerated basis) holds at least 360,000 s; past that, and for the blade's and its terminals' temperature, NOTHING PRINTED")
    w("       the 18 A service is %.1f %% of the rerated current: WITHIN" % (100 * R["f_18"]))
    w("       the Keystone 3568 holders (PRINTED, M65 p.42): UL %.0f A at 500 V AC, -50 to +%.0f C: %.1f %% of their rating: WITHIN on current" % (R["hold_a"], R["hold_t"], 100 * R["hold_frac"]))
    w("   3b. the blades' corrections compared (constitution section 4: at most three):")
    w("       (a) 30 A MINI blades (0297030, the same holder): rerated %.2f A at the air, %.2f A is %.1f %%: WITHIN on their own row; but the" % (R["blade30_rr"], R["I"], 100 * R["blade30_frac"]))
    w("           blades are the pack conductors' last protection behind a failed breaker, sized with the copper at the 25 A rating (the energy")
    w("           chain's check 3; L9-STACKUPS 14.4): no opening assured would rise from %.2f A to %.2f A, a protection lowered: REFUSED" % (R["blade25_135"], R["blade30_135"]))
    w("       (b) the breaker's most limit under the rerated %.2f A: the LM5069's printed VCL alone spans %.4f (48.5 / 61.5 mV); with the" % (R["I_rr_air"], R["vcl_ratio"]))
    w("           record's least limit 18.32 A kept the ratio needed is %.4f: INFEASIBLE with exact sense resistors; at an 18.00 A least the" % R["need_ratio_margin"])
    w("           sense window %.4f to %.4f mOhm exists only with no margin over the 18 A service, a service at its edge: REFUSED" % (R["rs_lo"], R["rs_hi_bare"]))
    w("       (c) evidence, not a correction: Littelfuse's statement of the 0297025's terminal and body temperature at %.0f %% of its rerated" % (100 * (1 + R["over_air"])))
    w("           current in %.2f C air, or a coupon (three 0297025.WXNV in 3568 holders on board A's band, %.2f A held from %.2f C to steady" % (R["T_AIR"], R["I"], R["T_AIR"]))
    w("           state and for 360,000 s; pass: each holder at most 145 C, each blade body at most 125 C, the band at the holder at most its")
    w("           limit, and either no opening or an opening inside the blade's 1000 A at 32 V DC rating)")
    w("       so the blades are OVER their printed rerated current at the held maximum and no compared correction keeps every protection and the")
    w("         service; the item is a finding for C-PROT rev 1 (register row L4A-67), the evidence (c) the supplier's")
    w("   3c. the dock block's spring pins J_CP1 to J_CP4 and J_CN1 to J_CN4 (Mill-Max 0858, spring 82; PRINTED: 085X family 9 A continuous at a")
    w("       10 C rise in free air, 20 mOhm max and no minimum, -55 to +125 C; the 0858 page: spring 82 '12 Amp', no condition printed):")
    w("       %.2f A a pin on the even split: WITHIN; the split is not bounded by any printed figure: for no pin over 9 A at %.2f A the lowest" % (R["pin_even"], R["I"]))
    w("         pin resistance must be at least %.3f of the highest (E-4 restated from 25 A's 0.593): CONDITIONAL on E-4; at 9 A the pin" % R["pin_ratio"])
    w("         reads %.2f C over the band (the free-air rise taken over the band, ASSUMED), under its %.0f C" % (R["pin_at9"], R["pin_tmax"]))
    w("   3d. the XT60 J_BATT (PRINTED: 30 A rated, -20 to 120 C; the 2021V1 sheet: 35 A max with 12 AWG at a rise under 85 K, contact 1.0 mOhm")
    w("       max): %.1f %% of 30 A: WITHIN on current; its rise at %.2f A NOT PRINTED: on the 35 A row scaled by the current squared (INFERRED)" % (100 * R["xt_frac"], R["I"]))
    w("       under %.1f K, %.1f C, %.1f K under 120 C; %.2f W a contact at most" % (R["xt_rise"], R["xt_t"], R["xt_margin"], R["xt_p"]))
    w("   3e. the 12 AWG pack lead (W_P, W_N to J_BATT) and board E's 12 AWG to the block (P_CP): no maker's sheet is held for the wire: its")
    w("       rating is NOT PRINTED here (the energy chain's 40 A is a convention, PACK_LEAD); a wire's insulation class is Layer 6's")
    w("   3f. board P (the pack), every part in the path at %.2f A held:" % R["I"])
    w("       Q1, Q2 (and Q109 beside Q1), CSD17570Q5B (PRINTED: %.2f mOhm max at 10 V and 25 C only; TJ -55 to 150 C; RthJA 50 C/W max on a" % (R["q1_r"] * 1e3))
    w("         1 in2 2 oz pad): %.3f W each at the 25 C maximum; their hot RDS(on) is printed only as a TYPICAL normalized curve, so NOT SHOWN on" % R["q1_p25"])
    w("         printed maxima; the 150 C junction admits a hot factor up to %.2f on its own pad, %.3f with both losses through one pad (the" % (R["q1_k_own"], R["q1_k_pad"]))
    w("         common drain), against the typical %.1f record l9stk reads (TJ %.1f C, RECORD; E-8)" % (R["k_typ"], R["Q1_REC"][2]))
    w("       Q101, Q102, CSD18510Q5B (PRINTED: %.2f mOhm max at 10 V and 25 C; RthJA 50 C/W max on 1 in2 2 oz; IF-2: at most 52.5 installed):" % (R["q101_r"] * 1e3))
    w("         %.3f W each at the 25 C maximum; NOT SHOWN on printed maxima (the same typical curve); the hot factor admitted %.2f to 150 C," % (R["q101_p25"], R["q101_k150"]))
    w("         %.2f to TI's 125 C (record l9stk: %.3f W, TJ %.1f C at the typical)" % (R["q101_k125"], R["Q101_REC"][0], R["Q101_REC"][1]))
    w("       R10 (2 mOhm 2512 2 W, no maker's sheet held: E-6), %.2f W (RECORD); R101 4 mOhm and R102 7.5 mOhm (no part chosen: 2 W each at the" % R["R10_REC"])
    w("         band's temperature, Layer 6), %.2f W and %.2f W (RECORD): NOT SHOWN, no printed derating" % R["SNS_REC"])
    w("       F2, Eaton SCF9550-30-05 (PRINTED: 30 A; operating -20 to +60 C): %.1f %% of its rating; its printed range ends %.2f K under the" % (100 * R["scf_frac"], R["scf_over"]))
    w("         %.2f C air at any current (record l4e10 section 9, Eaton's questions drafted): the pack's thermal environment, not a held-current row" % R["T_AIR"])
    w("       the cells: the breaker's and U-01's (W127's check 1c, finding 5), outside M-A")
    w("")
    w("4. WHICH ROWS THE GUARD EVER PROTECTED (INFERRED)")
    w("   the guard senses only board A's battery-FET pour: no trip under %.1f C at its die, surely tripped from %.1f C (record l8p 12m)" % (R["NOTRIP_DIE"], R["TRIP_DIE"]))
    w("   with the pour at E11-29's design target, at the blades' rerated %.2f A held the hottest FET reads %.2f C and its mounting base %.2f C;" % (R["I_rr_air"], R["TJ_rr_tgt"], R["mb_rr_tgt"]))
    w("     the guard's die is no hotter than the copper it sits on (its own heating 0.008 K, record l8p 9 (a)), so its trip is not assured")
    w("     there: a held overload from %.2f A to the breaker's %.2f A can persist with the guard intact, and the rows of section 3 read the" % (R["I_rr_air"], R["I"]))
    w("     same with or without it; only section 2's rows (the parts on the pour it senses) depend on it")
    w("   page 12o's exposure, 'the battery FETs reach 150 C held at %.2f A', is record l9stk's PAIR figure (its section 2: %.2f A, the pair on" % (R["EXPO_PAIR"], R["PAIR_EXPO_SRC"]))
    w("     the then 33.12 K/W target); for the drawn three at E-1's bar the figure is %.2f A, the breaker's own most limit" % R["I"])
    w("")
    w("5. L4A-65: PATH 2'S RETRY ENERGY ALONE (path 1 lost; current up to the breaker's %.2f A; %.2f C air)" % (R["I"], R["T_AIR"]))
    w("   the train (RECORD, record l8p 10c): on at most %.1f ms, off at least %.3f s, period at least %.3f s, duty at most %.3f" % (R["ON_MS"], R["HOLD"], R["PERIOD"], R["duty_train"]))
    w("   the rise per on-time over the mounting base, hottest FET at %.4f W: at most %.2f K on the printed Rth(j-mb) MAXIMUM (a passive" % (R["P_hot"], R["rise_on_bound"]))
    w("     network's transient impedance never exceeds its steady resistance, so Zth(j-mb) at %.1f ms is at most %.1f K/W) (INFERRED, PRINTED)" % (R["ON_MS"], R["rth_max"]))
    w("   Fig. 4 at %.1f ms (READING): %.3f K/W on duty 0.30, %.3f on 0.10, %.3f at the train's duty: %.2f K, class %s:" % (R["ON_MS"], R["z_on_03"], R["z_on_01"], R["z_on_train"], R["rise_on_typ"], R["zcls"]))
    w("     REFUSED as a limit (%s)" % (R.get("typ_bound_msg", "accepted")))
    w("   the steady periodic peak: any on and off pattern whose current never exceeds %.2f A heats every junction at most as the same current" % R["I"])
    w("     held does (superposition on a passive thermal network; the RDS(on) at its 150 C allowance at every instant), so the peak is at most")
    w("     the held state: %.2f C at E-1's bar, %.2f C at E11-29's design target: BOUNDED against %.0f C on printed device maxima, CONDITIONAL" % (R["peak_bar"], R["peak_tgt"], T_LIMIT))
    w("     on E11-29 (the pour), E11-36 (the allowance), E-05 (the three) and E-9 (the -1's as-built most limit: the train never exceeds")
    w("     it; round 12, the check's F4), as section 2a; bounded on the typical curve instead: FAILS")
    w("   the train's mean loss is at most %.3f of the held one; no credit is taken for it (the pour's own transient is no maker's figure)" % R["mean_frac"])
    w("   currents over %.2f A are single events outside the train, judged in their records: a fault's onset up to the breaker's 50.59 A for" % R["I"])
    w("     at most 16.5 us, after which the -1 latches off and a restart into the short is power-limited (record l9stk 15.3, its table); the")
    w("     docking pulse, 242.9 A once per docking (L4-E11 16d, E11-30)")
    w("   the breaker's own FETs under the train: each restart is judged under DD-8's restart inhibit (record l8p round 2, l9stk 15.4b),")
    w("     not here; board P's Q1 and Q2 under the train: at most their held row (section 3f), by the same superposition")
    w("")
    w("6. VERDICTS")
    w("   the guard's own parts (section 2): the three FETs HOLD %.2f A indefinitely at %.2f C at E-1's bar (%.2f C at the design target)," % (R["I"], R["TJ_bar"], R["TJ_tgt"]))
    w("     CONDITIONAL on E11-29, E11-36, E-05 and E-9 (round 12: the held current is the -1's as-built most limit, which the window counts")
    w("     at the parts' 1.5 % only; the check's F4); the pour and the vias WITHIN on the model; R17 WITHIN its printed derating while its")
    w("     terminals stay at or under %.1f C (CONDITIONAL, read on E11-29's coupon)" % R["tk_max"])
    w("   every other series part (section 3): the three 25 A blades OVER their printed rerated current by %.1f %% (%.2f A) at the air;" % (100 * R["over_air"], R["over_air_a"]))
    w("     NOT SHOWN on printed maxima: board P's Q1, Q2, Q109, Q101, Q102 (hot RDS(on) typical only), R10, R101 and R102 (no derating held),")
    w("     the wires (no sheet), the pins' split (E-4); WITHIN on printed current: the holders, the XT60 (its rise INFERRED), the pins evenly")
    w("   so M-A's acceptance as the register writes it ('every series part inside its PRINTED limits') is NOT MET on printed figures: the")
    w("     blades by %.2f A, the rest NOT SHOWN; each of those rows is independent of the guard (section 4), so none is HO-A's consequence" % R["over_air_a"])
    w("   L4A-65 (HO-B): BOUNDED on printed device maxima at the held state (%.2f C at the bar); FAILS on the typical curve, as it must" % R["peak_bar"])
    w("   what M-A closes once checked (L4A-69): HO-A's consequence for the parts the guard protects ON A BOARD WHOSE INSTALLED PATH MEETS")
    w("     E-1's BAR (the three FETs hold the breaker's most limit there, so a latent guard failure removes no protection they need) and HO-B")
    w("     (no retry exceeds a current they hold); the guard stays as defence in depth; CONDITIONAL on E-05, E11-29 (with R17's terminal")
    w("     reading), E11-36, E-9 (the -1's as-built most limit, round 12, the check's F4) and E11-29u (round 12, the check's F5: a check of")
    w("     EACH BUILT BOARD's path, since E11-29's coupon qualifies the design, not a board with a void or a poor tab joint: at production,")
    w("     an X-ray of the three FETs' tab joints against the voiding E11-29's coupon was built with, and at commissioning a per-unit")
    w("     reading, the three FETs carrying a known current for a known time from a known air with the guard's die (or the pour's NTC)")
    w("     read against E11-29's curve, pass: the bar met within the reading's stated uncertainty; round 13, the recheck's F8: every built")
    _u = 2 * math.sqrt(2 * (1.5 / math.sqrt(3)) ** 2 / 40.0 ** 2 + (0.01 / math.sqrt(3)) ** 2)
    w("     board, one reading each, from a known air of 15 to 35 C with a heating of at least 40 K; the unit's limit is E-1's bar itself;")
    w("     pass: the reading plus its expanded uncertainty (k = 2) at most the bar; the uncertainty budgeted at %.1f %% (%.2f K/W at the bar)" % (
        100 * _u, _u * 40.78))
    w("     from two temperature sensors of 1.5 K each (IEC 60584-1 class 1, ASSUMED: the supplier states its instruments) and the heating")
    w("     power within 1 %); on a board that misses the bar the")
    w("     guard is still needed and its silent failures, with no detection interval, stay a residual (REMAINING ENGINEERING, HO-A's pattern)")
    w("   M-B's entry condition (decision L4E11-FET-D2): (1) and (2) not met (E11-29, E11-36 and E-05 unanswered, none refused); (3) not met for")
    w("     the guard's parts; the blades' row is a part over its printed limit, but the guard does not assure its protection, nor would M-B:")
    w("     it enters C-PROT rev 1's re-evaluation (L4A-67), not M-B")
    w("")
    return o


PREDICATES = [
    ("the allowance reproduces record l4e11's 21.136 mOhm from the printed rows", lambda R: abs(R["RA"] * 1e3 - 21.136) < 0.0005),
    ("the even-split bar reproduces record l9stk's within 0.1 %", lambda R: abs(R["zbar_even"] / R["EVEN_BAR_REC"] - 1) < 1e-3),
    ("the worst split's bar reproduces E-1's 40.78 K/W within 0.1 %", lambda R: abs(R["zbar_even"] * 8 / 9 / R["BAR"] - 1) < 1e-3),
    ("the three hold the breaker's most limit at or under 150 C at E-1's bar", lambda R: R["TJ_bar"] <= T_LIMIT + 1e-6),
    ("at E11-29's design target the three reach 150 C only above the breaker's most limit", lambda R: R["I150_tgt"] > R["I"]),
    ("the junction's lead over its mounting base is 2.12 K on the printed Rth(j-mb) maximum", lambda R: abs(R["lead"] - 2.12) < 0.005),
    ("Fig. 4's curves never reach the printed Rth(j-mb) maximum (the curve is not a maximum)", lambda R: R["zmax_all"] < R["rth_max"]),
    ("a bound read on Fig. 4 is refused as a limit", lambda R: R["typ_bound_refused"]),
    ("R17 is within ROHM's lower derating line at the band's temperature", lambda R: R["p17_at_band"] <= R["allow_at_band"]),
    ("R17's admitted terminal temperature comes from the lower of the two printed lines", lambda R: R["tk_max"] < R["tk_fig2_only"]),
    ("the 25 A blades are over their printed rerated current at the 76.25 C air", lambda R: R["I"] > R["I_rr_air"]),
    ("the rerating line passes 100 % within 0.5 % at 25 C", lambda R: abs(R["f_25"] - 1.0) < 0.005),
    ("the 18 A service is within the blades' rerated current", lambda R: R["f_18"] < 1.0),
    ("a 30 A blade would carry the held current within its rerating", lambda R: R["blade30_frac"] < 1.0),
    ("the LM5069's printed VCL span cannot fit the 18.32 A least and the blades' rerated most", lambda R: R["vcl_ratio"] < R["need_ratio_margin"]),
    ("the pins' split ratio for 9 A at the held current is under 25 A's 0.593", lambda R: R["pin_ratio"] < 0.593),
    ("the XT60 is within its printed 30 A", lambda R: R["xt_frac"] < 1.0),
    ("at the blades' rerated current the guard's sure trip is not reached on the design target's pour", lambda R: R["mb_rr_tgt"] < R["TRIP_DIE"]),
    ("page 12o's 20.53 A is record l9stk's pair figure", lambda R: abs(R["EXPO_PAIR"] - R["PAIR_EXPO_SRC"]) < 1e-9),
    ("path 2's on-time and the RC hold make its period", lambda R: abs(R["ON_MS"] / 1000 + R["HOLD"] - R["PERIOD"]) < 0.0015),
    ("the retry train's peak is bounded by the held state on printed device maxima", lambda R: R["peak_bar"] <= T_LIMIT + 1e-6),
]


def main():
    try:
        R = compute()
    except Refused as e:
        sys.stderr.write("l8p_rowc: REFUSED: %s\n" % e)
        return 3
    o = render(R)
    o.append("7. PREDICATES")
    for text, f in PREDICATES:
        o.append("   %-118s %s" % (text, "yes" if f(R) else "NO"))
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
