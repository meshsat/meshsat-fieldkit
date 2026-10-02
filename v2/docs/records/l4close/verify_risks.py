#!/usr/bin/env python3
"""verify_risks.py: the independent verifier's separate code for the findings ledger's "Concrete remaining risks"
(MESHSAT-1357, 2 October 2026; v2/docs/records/l4close/VERIFICATION-2026-10-02.md). It prints every figure the
verification reports. It reruns no record's script and imports none of the records under check: it reads TEST-PLAN.md, the
records' outputs and the makers' sheets itself (pdftotext, mutool) and builds its own models. One input model is imported
read-only, Layer 3's accepted power model (records/rv-pwr/pwr_budget.py), for the kit's heat at the corner item 3 takes.

Items 2 to 7, 9 and 11, on set 27 (fnd/int27 at 7037d714): 2, 4, 5 settled at the checkpoint and re-read here; 3, 6, 7, 9 and
11 resumed. The models: item 3 a two-node enthalpy model integrated exactly piece by piece (matrix exponential with event
location); item 6 the drafted entry as a nodal network integrated by the trapezoidal rule (implicit) with the clamp solved per
step; item 7 the CSD19536KTT's Figure 4-10 read from the page's vector drawing and the breaker stepped in time; item 9 the
LM5176 loop's gain with its phase summed factor by factor and every crossing located by bisection.

Run from anywhere inside the repository:
  python3 v2/docs/records/l4close/verify_risks.py [--held-root DIR] > v2/docs/records/l4close/verify_risks.out
--held-root: another checkout of this repository whose ignored held/ folders carry the makers' sheets held back from the
public tree (each is checked against the sha256 its record pins); default: this checkout. Needs numpy, pdftotext and mutool.
Read-only; a few tens of seconds. Exit 1 if a source line is not where it reads it."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import math
import os
import re
import subprocess
import sys

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):     # one thread: a shared host
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
HELD_ROOT = TOP
HELD_SHA = {   # the sha256 each record pins for the held sheets read here
    "v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf": None,
    "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf": None,
    "v2/vendor/ti/held/ti-bq25730-sluse65a.pdf": "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f",
}


def rel(p):
    if "/held/" in p and not os.path.exists(os.path.join(TOP, p)):
        q = os.path.join(HELD_ROOT, p)
        want = HELD_SHA.get(p)
        if want:
            with open(q, "rb") as fh:
                must(hashlib.sha256(fh.read()).hexdigest() == want, "%s is the pinned file" % p)
        return q
    return os.path.join(TOP, p)


def txt(p):
    with open(rel(p), encoding="utf-8") as fh:
        return fh.read()


def pdf(p, first=None, last=None):
    a = ["pdftotext", "-layout"] + (["-f", str(first), "-l", str(last)] if first else []) + [rel(p), "-"]
    return subprocess.run(a, capture_output=True, check=True).stdout.decode("utf-8", "replace")


def npages(p):
    out = subprocess.run(["pdfinfo", rel(p)], capture_output=True, check=True).stdout.decode()
    return int(re.search(r"Pages:\s+(\d+)", out).group(1))


def flat(s):
    return re.sub(r"\s+", " ", s)


def must(cond, what):
    if not cond:
        print("SOURCE NOT AS READ: %s" % what)
        sys.exit(1)


def block(text, start, stop):
    i = text.find(start)
    must(i >= 0, "block %r" % start)
    j = text.find(stop, i + len(start))
    return text[i:j if j >= 0 else len(text)]


def bisect(f, lo, hi, n=80):
    """The root of f on [lo, hi], f(lo) and f(hi) of opposite signs."""
    flo = f(lo)
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm < 0) == (flo < 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ======================================================================================== item 2: the screen's mappings
def item2():
    print("ITEM 2. L4-E10's screen rows C04, C05, C16, C17, C18 against TEST-PLAN.md (the recheck's R2 list)")
    tp = flat(txt("v2/docs/TEST-PLAN.md"))
    out = txt("v2/docs/records/l4e10/l4e10_cell_thermal.out")
    rows = {k: flat(block(out, "\n%s " % k, "\n%s " % n)) for k, n in (("C04", "C05"), ("C05", "C06"), ("C16", "C17"),
                                                                    ("C17", "C18"), ("C18", "C19"))}
    rows["C01"] = flat(block(out, "\nC01 ", "\nC02 "))
    # (the recheck's item, the TEST-PLAN wording read at its source, the screen row, the row's wording that maps it)
    checks = [
        ("E3-H: the +40 C lid-closed level held until the hot stop acts or 4 h pass",
         "at +40 C with the lid closed the level is held until the hot stop has acted or its 4 h have passed", "C05",
         "at +40 C lid closed the level is held until the hot stop has acted or its 4 h have passed"),
        ("E3-H: repeated with the sensor controller in reset",
         "once more with the sensor controller held in reset", "C05", "the run is repeated with the sensor controller held in reset"),
        ("E3-H: the TMP117 fallback thresholds +55.0 and +56.0 C",
         "the same steps act on board B's TMP117 at +55.0 C and +56.0 C", "C05",
         "board B's TMP117 acts at +55.0 C (shed) and +56.0 C (shutdown)"),
        ("P15: the TMP117 release at +45.0 C", "released at +45.0 C", "C05", "released at +45.0 C"),
        ("E3-H: the restart at or below +46.5 C after 30 minutes",
         "comes back only once the hottest cell reads +46.5 C or less and 30 minutes have passed", "C05",
         "returns once the hottest cell reads +46.5 C or less and 30 minutes have passed"),
        ("E3-H: the stepped run from +40 C by 2 K an hour to at most +55 C, on shore then on the pack",
         "the chamber raised from +40 C by 2 K an hour to at most +55 C until H1 and then H2 have acted, first on shore", "C05",
         "from +40 C by 2 K an hour to at most +55 C"),
        ("E3-L: started once with the lid already closed", "started once with the lid already closed", "C04",
         "E3-L is started once with the lid already closed"),
        ("E3-L: the lid-closed start enters the reduced mode once the lid is read",
         "the start with the lid closed enters the reduced mode once the lid is read", "C04",
         "the start with the lid closed enters the reduced mode once the lid is read"),
        ("E3-L: the +40 C level (in C01, as the recheck's list does not name it)", "lid closed at +20 C, +30 C and +40 C, 4 h at each",
         "C01", "E3-L at +40 C"),
        ("E3-P: OTD recovers at or below +52.5 C", "recovers at or below +52.5 C", "C17", "recover at or below +52.5 C"),
        ("E4-T: full function after return to 25 C, capacity within 5 %",
         "full function after return to 25 C, capacity within 5 % of its value before (PROVISIONAL: the maker publishes no cold-storage recovery figure)",
         "C16", "full function after return to 25 C, capacity within 5 % of its value before (PROVISIONAL"),
        ("E4-P: recovery as E4-T", "| E4-P | the pack alone | as E4-T | the pack at its own cold storage limit | as E4-T |", "C18",
         "recovery mapped (as E4-T): full function after return to 25 C, capacity within 5 %"),
        ("charge state unstated in TEST-PLAN named as a missing input (E3-L)", None, "C04", "charge state: the pack's charge at each level's start is not stated by TEST-PLAN (a named missing input)"),
        ("charge state unstated in TEST-PLAN named as a missing input (E3-H)", None, "C05", "charge state: not stated by TEST-PLAN for E3-H (a named missing input"),
        ("charge state unstated in TEST-PLAN named as a missing input (E4-T transport)", None, "C16", "for transport 'at its charge', not stated (a named missing input)"),
        ("charge state unstated in TEST-PLAN named as a missing input (E4-P)", None, "C18", "E4-P names none (a named missing input)"),
        ("E3-P's charge state is TEST-PLAN's own (full charge)", "| E3-P | the pack alone, armed (JP1 closed), at full charge", "C17", "full charge"),
    ]
    n_ok = 0
    for what, src, row, mapped in checks:
        in_tp = True if src is None else (flat(src) in tp)
        in_row = flat(mapped) in rows[row]
        n_ok += in_tp and in_row
        print("   %-92s TEST-PLAN %-3s  %s %s" % (what, "n/a" if src is None else ("yes" if in_tp else "NO"), row, "yes" if in_row else "NO"))
    print("   mapped and read at the source: %d of %d" % (n_ok, len(checks)))
    # not on the recheck's list: E3-P's other pass items, read for completeness
    extra = [("E3-P: the second level does not fire", "the second level does not fire"),
             ("E3-P: capacity recovery at least 95 % as E3-T", "capacity recovery at least 95 % as E3-T")]
    for what, src in extra:
        print("   observation, not on the recheck's list: %-48s TEST-PLAN %s; restated in C17: %s" % (
            what, "yes" if flat(src) in tp else "NO", "yes" if flat(src) in rows["C17"] else "no (C17 cites MAKER 7.10)"))
    print()
    return n_ok == len(checks)



# ======================================================================================== item 3: the latent-storage volumes
def load_layer3_models():
    """Layer 3's accepted power model and its reduced-mode states (records/rv-pwr/pwr_budget.py through records/hc2/pwr_red2.py,
    which loads it), imported read-only with their printing captured; only their heat figures are used."""
    old = sys.argv
    sys.argv = [rel("v2/docs/records/hc2/pwr_red2.py")]
    try:
        sp = importlib.util.spec_from_file_location("l4close_pwr_red2_input", rel("v2/docs/records/hc2/pwr_red2.py"))
        m = importlib.util.module_from_spec(sp)
        with contextlib.redirect_stdout(io.StringIO()):
            sp.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


def expm2(a11, a12, a21, a22, t):
    """exp(A t) for a 2x2 real matrix with real distinct eigenvalues (an RC network's)."""
    tr, det = a11 + a22, a11 * a22 - a12 * a21
    disc = math.sqrt(tr * tr - 4.0 * det)
    l1, l2 = (tr + disc) / 2.0, (tr - disc) / 2.0
    e1, e2 = math.exp(l1 * t), math.exp(l2 * t)
    k = 1.0 / (l1 - l2)
    return ((e1 * (a11 - l2) - e2 * (a11 - l1)) * k, (e1 - e2) * a12 * k,
            (e1 - e2) * a21 * k, (e1 * (a22 - l2) - e2 * (a22 - l1)) * k)


class Block:
    """The kit (C_k, to the chamber through G_e, its own heat q) and the block (the cells C_c with m kg of the material, to the
    kit through G_b). The block's enthalpy H counts from the material solid at its melting point Tm: below 0 the solid's
    sensible heat, 0 to m L melting at Tm, above m L the liquid's. Integrated EXACTLY piece by piece: in a sensible phase the
    two-node linear system under a chamber linear in time, in the melting phase the kit alone with the block held at Tm; each
    phase change and each interior maximum located by bisection on the closed form."""

    def __init__(self, C_k, C_c, G_e, G_b, q, m, Tm, L, cp):
        self.C_k, self.G_e, self.G_b, self.q, self.Tm = C_k, G_e, G_b, q, Tm
        self.Cp, self.Lm, self.m = C_c + m * cp, m * L, m

    def tp(self, H):
        if H < 0.0:
            return self.Tm + H / self.Cp
        if H <= self.Lm:
            return self.Tm
        return self.Tm + (H - self.Lm) / self.Cp

    def phase(self, Tk, H):
        if self.m == 0.0:
            return "N"                     # no material: one sensible phase
        if H < 0.0:
            return "S"
        if H > self.Lm:
            return "L"
        if H == 0.0 and Tk < self.Tm:
            return "S"
        if H == self.Lm and Tk > self.Tm:
            return "L"
        return "M"

    def sens(self, Tk0, Tp0, ch0, ch1):
        """The sensible phase's closed form x(tau) for x = (Tk, Tp), the chamber ch0 + ch1 tau."""
        C_k, G_e, G_b, Cp = self.C_k, self.G_e, self.G_b, self.Cp
        a11, a12, a21, a22 = -(G_e + G_b) / C_k, G_b / C_k, G_b / Cp, -G_b / Cp
        b0, b1 = (self.q + G_e * ch0) / C_k, G_e * ch1 / C_k
        det = a11 * a22 - a12 * a21
        inv = (a22 / det, -a12 / det, -a21 / det, a11 / det)
        d1 = (-(inv[0] * b1), -(inv[2] * b1))                      # -A^-1 b1, b1 = (b1, 0)
        r = (d1[0] - b0, d1[1])                                   # d0 = A^-1 (d1 - b0)
        d0 = (inv[0] * r[0] + inv[1] * r[1], inv[2] * r[0] + inv[3] * r[1])
        y0 = (Tk0 - d0[0], Tp0 - d0[1])

        def at(tau):
            e = expm2(a11, a12, a21, a22, tau)
            return (d0[0] + d1[0] * tau + e[0] * y0[0] + e[1] * y0[1], d0[1] + d1[1] * tau + e[2] * y0[0] + e[3] * y0[1])
        return at

    def melt(self, Tk0, H0, ch0, ch1):
        C_k, G_e, G_b, Tm = self.C_k, self.G_e, self.G_b, self.Tm
        a = (G_e + G_b) / C_k
        p0, p1 = (self.q + G_e * ch0 + G_b * Tm) / C_k, G_e * ch1 / C_k
        beta = p1 / a
        alpha = (p0 - beta) / a

        def at(tau):
            ex = math.exp(-a * tau)
            tk = alpha + beta * tau + (Tk0 - alpha) * ex
            h = H0 + G_b * ((alpha - Tm) * tau + beta * tau * tau / 2.0 + (Tk0 - alpha) * (1.0 - ex) / a)
            return tk, h
        return at

    def run(self, segs, T0k, T0p, h=60.0):
        """segs: (duration s, chamber at its start, slope K/s). Returns the block's peak temperature."""
        Tk = T0k
        H = (T0p - self.Tm) * self.Cp if T0p <= self.Tm else self.Lm + (T0p - self.Tm) * self.Cp
        peak = self.tp(H)
        for dur, c0, c1 in segs:
            t = 0.0
            while t < dur - 1e-9:
                step = min(h, dur - t)
                ch0 = c0 + c1 * t
                ph = self.phase(Tk, H)
                if ph == "M":
                    at = self.melt(Tk, H, ch0, c1)
                    tk1, h1 = at(step)
                    if h1 > self.Lm or h1 < 0.0:
                        edge = self.Lm if h1 > self.Lm else 0.0
                        tau = max(bisect(lambda x: at(x)[1] - edge, 0.0, step), 1e-6)
                        Tk, H = at(tau)[0], edge
                        t += tau
                        continue
                    Tk, H = tk1, h1
                    t += step
                    continue
                Tp = self.tp(H)
                at = self.sens(Tk, Tp, ch0, c1)
                tk1, tp1 = at(step)
                if ph == "S" and tp1 > self.Tm:
                    tau = max(bisect(lambda x: at(x)[1] - self.Tm, 0.0, step), 1e-6)
                    Tk, H = at(tau)[0], 0.0
                    t += tau
                    continue
                if ph == "L" and tp1 < self.Tm:
                    tau = max(bisect(lambda x: at(x)[1] - self.Tm, 0.0, step), 1e-6)
                    Tk, H = at(tau)[0], self.Lm
                    t += tau
                    continue
                if (Tk - Tp) > 0.0 and (tk1 - tp1) < 0.0:          # an interior maximum of the block
                    tau = bisect(lambda x: at(x)[0] - at(x)[1], 0.0, step)
                    peak = max(peak, at(tau)[1])
                Tk = tk1
                H = (self.Lm if ph == "L" else 0.0) + (tp1 - self.Tm) * self.Cp
                peak = max(peak, tp1)
                t += step
        return peak


def min_mass(make, limit, hi=1.0):
    if make(0.0) <= limit:
        return 0.0
    while make(hi) > limit:
        hi *= 2.0
        must(hi < 200.0, "a latent store that fits at all")
    lo = 0.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if make(mid) > limit:
            lo = mid
        else:
            hi = mid
    return hi


def pocket():
    pt = txt("v2/docs/feasibility/POWER-THERMAL.md")
    m = re.search(r"The pack block is (\d+\.\d+) x (\d+\.\d+) x (\d+\.\d+) mm \(A06\)", pt)
    must(m, "POWER-THERMAL's pack block")
    X, Y, Z = (float(v) for v in m.groups())
    A_E, A_B, A_end = Y * Z, X * Y, X * Z
    sl = txt("v2/docs/records/l3batt/SHORTLIST.md")
    east = float(re.search(r"\| M4b, across \| (\d+\.\d+) mm \|", sl).group(1))
    top = float(re.search(r"\| M6 east, height \| (\d+\.\d+) mm \|", sl).group(1))
    ends = float(re.search(r"\| M5 east, along the axis \| (\d+\.\d+) mm \|", sl).group(1))
    cm = txt("v2/docs/CASE-MARGINS.md")
    head = [c.strip() for c in re.search(r"^\| # \| Margin \|.*$", cm, re.M).group(0).strip("|").split("|")]
    must(head[3].startswith("As designed: nominal") and head[5] == "Chosen: nominal", "CASE-MARGINS 3.2's header")

    def cells(key):
        line = re.search(r"^\| %s \|.*$" % key, cm, re.M).group(0)
        return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    ch = {}
    for key in ("M4b", "M5", "M6"):
        c = cells(key)
        must(len(c) == len(head), "CASE-MARGINS %s has the header's cells" % key)
        ch[key] = float(c[5])
    worst = (A_E * east + A_B * top + 2 * A_end * ends) / 1e6
    designed = (A_E * (ch["M4b"] - 1.0) + A_B * (ch["M6"] - 1.0) + 2 * A_end * (ch["M5"] - 1.0) + A_E * (2.0 - 1.0)) / 1e6
    return worst, designed, ch


def item3():
    print("ITEM 3. L4-E10's latent-storage volumes (approach III), recomputed in a separate enthalpy model")
    rt = flat(pdf("v2/vendor/battery/pcm/rubitherm-rt57hc-2026-01-21.pdf", 1, 1))
    mm = re.search(r"Melting area (\d+) - (\d+) \[°C\]", rt)
    cap = re.search(r"Heat storage capacity ± 7,5% (\d+) \[kJ/kg\]", rt)
    cpm = re.search(r"Specific heat capacity (\d+) \[kJ/kg.K\]", rt)
    rho = re.search(r"Density solid ~ (\d),(\d) \[kg/l\]", rt)
    cong = re.search(r"Congealing area (\d+) - (\d+)", rt)
    must(mm and cap and cpm and rho and cong and "Typical Values" in rt and "49 °C to64 °C" in rt, "RT57HC's rows")
    t_lo, t_hi = float(mm.group(1)), float(mm.group(2))
    L_fav = float(cap.group(1)) * 1000.0 * 1.075
    L_unf = float(cap.group(1)) * 1000.0 * 0.925
    cp = float(cpm.group(1)) * 1000.0
    rho_s = float(rho.group(1)) + float(rho.group(2)) / 10.0
    print("   RT57HC (Rubitherm, 2026-01-21; 'Typical Values', 'a non-binding planning aid'): melting %g to %g C, congealing %s to %s C,"
          % (t_lo, t_hi, cong.group(1), cong.group(2)))
    print("     %s kJ/kg +-7.5 %% 'combination of latent and sensible heat' over 49 to 64 C, cp %.0f J/kgK, %.1f kg/l solid" % (cap.group(1), cp, rho_s))
    print("   favourable to the material (the record's reading, kept): %.0f kJ/kg all latent at %.0f C, the solid density, no container;" % (L_fav / 1000.0, t_hi))
    print("     the sensible heat over 49 to 64 C counted twice and the congealing hysteresis ignored (refreezing at %.0f C, not 53 to 57 C)" % t_hi)
    red2 = load_layer3_models()
    pb = red2.pb
    fR, qR, _pR = red2.heat(red2.SURVR, "plan")
    fS, qS, _pS = red2.heat(red2.SURV, "plan")
    eta = pb.ETA_CHG * min(pb.ETA_FE)
    q_shore_R = qR + (fR["pb"] / eta - fR["pb"])
    q_shore_S = qS + (fS["pb"] / eta - fS["pb"])
    g_floor = q_shore_R / (55.0 - 40.0)
    out10 = txt("v2/docs/records/l4e10/l4e10_cell_thermal.out")
    must(re.search(r"SGP41 inside air at most \+55 C\s+on the shore %.4f" % g_floor, out10), "L4-E10's printed T-H1 floor equals q/15")
    ap = txt("v2/docs/MESHSAT-709-geometry-appendix.md")
    k_lo, k_hi = (float(v) * 1000.0 for v in re.search(r"goes into about (\d+) to (\d+) kJ/K of thermal mass", ap).groups())
    pt = txt("v2/docs/feasibility/POWER-THERMAL.md")
    c_lo, c_hi = (float(v) for v in re.search(r"the 12 cells hold (\d+) to (\d+) J/K", pt).groups())
    GB, G, G32 = pb.G_BLK, pb.G, pb.G_3253
    print("   inputs (Layer 3's model, read-only): the heat stage on shore %.6f W (SURV-R) and %.6f W (SURV); the T-H1 floor %.6f W/K"
          " (L4-E10 prints 1.6664); the kit %.0f to %.0f J/K (32.53), the cells %.0f to %.0f J/K, the block's film %.6f to %.6f W/K;"
          % (q_shore_R, q_shore_S, g_floor, k_lo, k_hi, c_lo, c_hi, GB[0], GB[1]))
    print("     closed and still %.2f to %.2f W/K, lid open with fans %.2f (W4's lowest) and %.2f W/K (32.53's highest)"
          % (G["closed_still"][0], G["closed_still"][1], G["open_fans"][0], G32["open_fans"][1]))
    m5 = txt("v2/vendor/standards/mil-std-810h-method-507-6.md")
    knots = [(int(a) / 100.0 * 3600.0, float(b)) for a, b in re.findall(r"^\| (\d{4}) \| (\d+) \|", m5, re.M)]
    must([k[1] for k in knots] == [30.0, 60.0, 60.0, 30.0, 30.0], "Method 507.6's Table 507.6-IX")
    e5 = [(24 * 3600.0, 23.0, 0.0)]
    for _ in range(10):
        for (ta, va), (tb, vb) in zip(knots, knots[1:]):
            e5.append((tb - ta, va, (vb - va) / (tb - ta)))
    limit = 60.0

    def solve(name, segs, start, kit, cells, ge, gb, q, L=L_fav, Tm=t_hi):
        mk = lambda m: Block(kit, cells, ge, gb, q, m, Tm, L, cp).run(segs, start, start)
        none = mk(0.0)
        m = min_mass(mk, limit)
        return dict(name=name, none=none, m=m, V=m / rho_s, E=m * L / 1000.0)
    cases = [
        ("E3-O, the conditioned corner (4 h at +55 C from +55 C)", [(4 * 3600.0, 55.0, 0.0)], 55.0, k_lo, c_lo, g_floor, GB[1], q_shore_R),
        ("E5, the conditioned corner (507.6 II: 23 C 24 h, ten cycles)", e5, 23.0 + q_shore_R / g_floor, k_lo, c_lo, g_floor, GB[1], q_shore_R),
        ("E3-S, the best corner (24 h at +71 C from -20 C, still)", [(24 * 3600.0, 71.0, 0.0)], -20.0, k_hi - c_hi, c_hi, G["closed_still"][0], GB[0], 0.0),
        ("E3-S, the worst corner", [(24 * 3600.0, 71.0, 0.0)], -20.0, k_lo - c_lo, c_lo, G["closed_still"][1], GB[1], 0.0),
        ("E5, the best corner (32.53's 3.3 W/K, SURV on shore)", e5, 23.0 + q_shore_S / G32["open_fans"][1], k_hi, c_hi, G32["open_fans"][1], GB[0], q_shore_S),
    ]
    rec = (0.162, 1.489, 0.275, 1.175, 0.102)
    res = []
    for (name, segs, start, kit, cells, ge, gb, q), want in zip(cases, rec):
        r = solve(name, segs, start, kit, cells, ge, gb, q)
        res.append(r)
        print("   %-64s no store %.2f C; %.4f kg, %.4f L (the record %.3f L); latent %.1f kJ (%.2f Wh)" % (
            name, r["none"], r["m"], r["V"], want, r["E"], r["E"] / 3.6))
    worst, designed, ch = pocket()
    print("   the pocket beyond the 1.0 mm minimums: %.4f L at the worst stack, %.4f L as designed (CASE-MARGINS' chosen column: M4b"
          " +%.2f, M5 +%.2f, M6 +%.2f mm); L4-E10 now prints 0.056 and 0.0865 L" % (worst, designed, ch["M4b"], ch["M5"], ch["M6"]))
    for r in res:
        print("     %-64s %.4f L against %.4f L: %s" % (r["name"], r["V"], designed, "does not fit" if r["V"] > designed else "fits"))
    # the record's favourable choices, tested: the melt at the bottom of the area and the capacity at its lower tolerance
    s1 = solve("E3-O conditioned, melting at %.0f C, %.0f kJ/kg" % (t_lo, L_unf / 1000.0), cases[0][1], 55.0, k_lo, c_lo, g_floor, GB[1], q_shore_R, L=L_unf, Tm=t_lo)
    s2 = solve("E3-S best, melting at %.0f C, %.0f kJ/kg" % (t_lo, L_unf / 1000.0), cases[2][1], -20.0, k_hi - c_hi, c_hi, G["closed_still"][0], GB[0], 0.0, L=L_unf, Tm=t_lo)
    print("   the favourable direction checked: %s %.4f L; %s %.4f L (both larger than the record's reading)" % (s1["name"], s1["V"], s2["name"], s2["V"]))
    # a step-size check on the exact integrator: the E3-O conditioned mass with a 10 s substep
    m10 = min_mass(lambda m: Block(k_lo, c_lo, g_floor, GB[1], q_shore_R, m, t_hi, L_fav, cp).run(cases[0][1], 55.0, 55.0, h=10.0), limit)
    print("   the substep checked: E3-O conditioned %.6f kg at 10 s against %.6f kg at 60 s" % (m10, res[0]["m"]))
    print()
    return res, designed


# ======================================================================================== item 4: R-b against SLUSE66A p.10
def item4():
    print("ITEM 4. L4-E11's R-b against SLUSE66A p.10 (BQ25731, v2/vendor/ti/bq25731-datasheet.pdf)")
    p1 = pdf("v2/vendor/ti/bq25731-datasheet.pdf", 1, 1)
    p10 = pdf("v2/vendor/ti/bq25731-datasheet.pdf", 10, 10)
    must("SLUSE66A" in p10 and "REVISED JANUARY 2021" in p10, "SLUSE66A's revision on p.10")
    hdr = re.search(r"VVBUS_UVLOZ < VVBUS < VVBUSOV_FALL , TJ = -40°C to \+125°C, and TJ = 25°C for typical values \(unless otherwise noted\)", p10)
    must(hdr, "p.10's table condition (TJ)")
    f10 = flat(p10)
    rowm = re.search(r"Charge current 4096 mA regulation accuracy REG0x03/02\(\) = 0x0800H 5-mΩ RSR sensing \u20135\.0% 6\.0% ICHRG_REG_ACC "
                     r"resistor, VBAT above 2048 mA VSYS_MIN\(0°C to REG0x03/02\(\) = 0x0400H 85°C\) \u201312% 13\.5% 1024 mA "
                     r"REG0x03/02\(\) = 0x0200H \u201318% 21\.5%", f10)
    must(rowm, "p.10's ICHRG_REG_ACC rows and their condition")
    clamp = re.search(r"CELL\(≥2 S\),VSRN < VSYS_MIN 384 mA", f10)
    must(clamp, "p.10's ICLAMP row (typical only)")
    print("   p.10 table condition: 'TJ = -40°C to +125°C, and TJ = 25°C for typical values (unless otherwise noted)'")
    print("   ICHRG_REG_ACC, 'Charge current regulation accuracy 5-mΩ RSR sensing resistor, VBAT above VSYS_MIN(0°C to 85°C)':")
    print("     REG0x03/02() = 0x0200H, 1024 mA: -18 % / +21.5 % (MIN / MAX); the (0°C to 85°C) is the row's 'otherwise noted'")
    print("     temperature under a TJ table: a junction range")
    print("   ICLAMP, CELL(>=2 S), VSRN < VSYS_MIN: 384 mA in the TYP column, no MIN or MAX")
    gen = txt("v2/ecad/tools/gen_sch_a.py")
    must('r("R17", "5mOhm 1% 2512 (RSR, charge current sense)", "VBAT", "CELL_FUSED", "RS2512")' in gen, "R17 5 mOhm 1 % in gen_sch_a.py")
    i_set = 1.024
    i_max = i_set * (1 + 0.215) / (1 - 0.01)
    i_min = i_set * (1 - 0.18) / (1 + 0.01)
    t_air, vsd, rja = 62.1, 1.0, 50.0
    tj = t_air + i_max * vsd * rja
    print("   R17: '5mOhm 1%% 2512 (RSR, charge current sense)' (gen_sch_a.py): case (i) %.4f to %.4f A (the record: 0.8314 to 1.2567 A)" % (i_min, i_max))
    print("   Q2's diode: %.4f W at VSD 1 V, %.3f K over the %.1f C air at %.0f C/W: TJ %.3f C (the record: 1.257 W, 62.8 K, 124.9 C) against 150 C" % (
        i_max * vsd, i_max * vsd * rja, t_air, rja, tj))
    p_max = i_max * 16.884
    print("   R-b's charge power above 14 V: %.4f A x 16.884 V = %.2f W (the record: 21.22 W)" % (i_max, p_max))
    # R17's temperature coefficient: not in the +-1 %; no part number is drawn for R17, so a typical metal-strip 75 ppm/K is shown
    for ppm in (75.0, 200.0):
        k = 1 - ppm * 1e-6 * 60.0
        im = i_set * 1.215 / (0.99 * k)
        print("   sensitivity, not in the record: R17 at -%.0f ppm/K over 60 K (0 to 85 C from 25 C): %.4f A, Q2 at %.2f C" % (ppm, im, t_air + im * vsd * rja))
    l11 = flat(txt("v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md"))
    c2 = "| (ii) | SRN at or above VSYS_MIN, the charger outside 0 to 85 C (it sits in the inside air, -20 C at a cold start to 62.1 C hot, plus its own rise, which no held record gives) | not printed | INCONCLUSIVE: E11-22 |"
    c3 = "| (iii) | SRN under VSYS_MIN | the clamp, 384 mA typical, no maximum printed | INCONCLUSIVE: E11-22 |"
    q2 = "**CONDITIONAL** on case (i) holding and on board P's installed copper giving TI's 50 C/W"
    for lab, s in (("case (ii) INCONCLUSIVE, the charger's own rise counted", c2), ("case (iii) INCONCLUSIVE", c3), ("Q2's 124.9 C CONDITIONAL", q2)):
        print("   L4E11 section 4: %-55s %s" % (lab, "read" if flat(s) in l11 else "NOT FOUND"))
        must(flat(s) in l11, lab)
    reg = txt("v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md")
    r136 = re.search(r"^\| R-136 \|.*$", reg, re.M).group(0)
    for lab, s in (("cases (ii) and (iii)", "R-b's cases (ii) and (iii) closed"),
                   ("the charger's temperature bounded inside 0 to 85 C, or TI's accuracy outside it", "the charger's temperature while R-b holds bounded inside 0 to 85 C, or TI's 0x0200 accuracy outside it"),
                   ("the clamp's maximum under VSYS_MIN", "the clamp's maximum under VSYS_MIN"),
                   ("Q2's copper for 50 C/W", "board P's copper under Q2 for TI's 50 C/W"),
                   ("acceptance: Q2 at most 124.9 C confirmed or re-derived", "Q2's diode at most 124.9 C at the 62.1 C air confirmed or re-derived")):
        print("   R-136 carries %-75s %s" % (lab, "yes" if s in r136 else "NO"))
        must(s in r136, "R-136: " + lab)
    # set 27: L4-E11's consolidation selects TI's BQ25730 (SLUSE65A) in U3's land with the battery FET Q39 (section 14, a draft)
    b = flat(pdf("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", 10, 10))
    must("SLUSE65A \u2013 FEBRUARY 2021 \u2013 REVISED JANUARY 2024" in b, "SLUSE65A's revision on p.10")
    must(re.search(r"TJ = -40°C to \+125°C, and TJ = 25°C for typical values \(unless otherwise noted\)", b), "SLUSE65A p.10's TJ condition")
    must(re.search(r"5-mΩ RSR sensing \u20135\.0% 6\.0% ICHRG_REG_ACC resistor, VBAT above VSYS_MIN\(Reg0x0D 2048 mA REG0x03/02\(\) = 0x0400H "
                   r"/0C\)setting\(0°C to \u201312% 13\.5% 85°C\) 1024 mA REG0x03/02\(\) = 0x0200H \u201318% 21\.5%", b), "SLUSE65A p.10's 0x0200 row")
    must(re.search(r"CELL\(≥2 S\),VSRN < VSYS_MIN 384 mA Pre-charge current", b), "SLUSE65A p.10's clamp (typical)")
    print("   set 27 (L4-E11 section 14, drafted): the BQ25730 (SLUSE65A, revised January 2024, held, sha256 pinned) prints the same p.10 row:")
    print("     0x0200 -18 % / +21.5 % with a 5 mOhm RSR, VBAT above VSYS_MIN (Reg0x0D/0C) at 0 to 85 C under the same TJ table; the clamp")
    print("     under VSYS_MIN 384 mA typical only. So case (i)'s %.4f A and case (ii)'s gap carry over; case (iii) moves to R-b' (E11-28, R-158)," % i_max)
    print("     outside this item")
    print()



# ======================================================================================== item 5: the SGP41's shutdown
def item5():
    print("ITEM 5. L4-E12's SGP41 shutdown on a TMP117 (v2/vendor/ti/ti-tmp117-temperature.pdf)")
    p1 = pdf("v2/vendor/ti/ti-tmp117-temperature.pdf", 1, 1)
    must("SNOSD82D \u2013 JUNE 2018 \u2013 REVISED SEPTEMBER 2022" in p1, "the TMP117 sheet's revision")
    must(re.search(r"±0\.15 °C \(maximum\) from \u201340 °C to 70 °C", p1), "p.1's +-0.15 C row")
    p6 = pdf("v2/vendor/ti/ti-tmp117-temperature.pdf", 6, 6)
    must("6.5 Electrical Characteristics" in p6, "6.5 on p.6")
    must(re.search(r"-40 °C to 70 °C\s+-0\.15\s+±0\.05\s+0\.15", p6), "6.5's TMP117 -40 to 70 C row")
    must(re.search(r"8 averages", p6) and re.search(r"1-Hz conversion cycle", p6) and re.search(r"Thermal Pad unsoldered", p6),
         "6.5's test conditions")
    print("   p.1: '+-0.15 C (maximum) from -40 C to 70 C' (SNOSD82D, revised September 2022; the sheet prints the minus as an en dash)")
    print("   p.6, 6.5 Electrical Characteristics, TMP117 row -40 to 70 C: MIN -0.15, TYP +-0.05, MAX 0.15 C, over free-air temperature;")
    print("     conditions: 8 averages, 1-Hz conversion cycle, thermal pad unsoldered (DRV), I2C inputs VIL <= 0.05 V+, VIH >= 0.95 V+;")
    print("     the TMP117N rows print +-0.2 C from -40 to 100 C (no +-0.15 C row); board B's part is TMP117AIDRVR (gen_sch_b.py)")
    gb = txt("v2/ecad/tools/gen_sch_b.py")
    must('"TMP117AIDRVR board temperature under the coolers' in gb, "board B's TMP117AIDRVR")
    l12 = txt("v2/docs/records/l4e12/l4e12_thermal.py")
    m = re.search(r"^READ_S, TAU_S = ([\d.]+), ([\d.]+)\s+# (.*)$", l12, re.M)
    must(m, "L4-E12's READ_S and TAU_S")
    read_s, tau_s = float(m.group(1)), float(m.group(2))
    rate = 15.0 / 3600.0          # E5's 30 to 60 C in 2 h (Method 507.6), K/s
    lag = rate * (read_s + tau_s)
    off_x = 55.0 - 0.15 - 0.5 - lag
    on_x = 50.0 - 0.15 - 0.5 - lag
    print("   L4-E12's lag (l4e12_thermal.py): READ_S %.0f s and TAU_S %.0f s, '%s'" % (read_s, tau_s, m.group(3).strip()))
    print("   the lag: 15.0 K/h x %.0f s = %.6f K (the record: 0.254167 K)" % (read_s + tau_s, lag))
    print("   off at 55 - 0.15 - 0.5 - lag = %.6f C, set at 54.0 C; the SGP41 then at most %.6f C (the record: 54.095833, 54.904167 C)" % (
        off_x, 54.0 + 0.15 + 0.5 + lag))
    print("   on and used at 50 - 0.15 - 0.5 - lag = %.6f C, set at 49.0 C; at most %.6f C while used (the record: 49.095833, 49.904167 C)" % (
        on_x, 49.0 + 0.15 + 0.5 + lag))
    for err in (0.15, 0.2):
        tau_be = (55.0 - 54.0 - err - 0.5) / rate - read_s
        print("   break-even of the 54.0 C setting at +-%.2f C: the sensor-to-SGP41 time constant at most %.1f s at 15 K/h (the record assumes %.0f s);"
              " off point %.6f C" % (err, tau_be, tau_s, 55.0 - err - 0.5 - lag))
    reg = txt("v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md")
    rows = {k: re.search(r"^\| %s \|.*$" % k, reg, re.M).group(0) for k in ("R-138", "R-139", "R-146")}
    clause = re.search(r"the SGP41's shutdown lag measured on the bench, from the TMP117's reading crossing 54\.0 C to the part's off state, "
                       r"at most the 61 s assumed \(L4-E12's 0\.254167 K at E5's 15\.0 K/h\); a longer lag re-derives the 54\.0 C and 49\.0 C "
                       r"settings before they are used", rows["R-139"])
    print("   the register (set 27): R-146 carries the 0.5 K placement (%s); R-139 now names the lag: %s" % (
        "yes" if "the TMP117 within 0.5 K of the SGP41" in rows["R-146"] else "NO", "yes" if clause else "NO"))
    must(clause, "R-139's lag clause")
    print("     R-139's acceptance: 'the SGP41's shutdown lag measured on the bench, from the TMP117's reading crossing 54.0 C to the part's off")
    print("     state, at most the 61 s assumed'")
    print("   what that interval holds: the reading period and the firmware's and the switch's response, about %.0f s of the %.0f s;" % (read_s, read_s + tau_s))
    print("     the %.0f s thermal time constant lies BEFORE the reading crosses 54.0 C (the reading lags the SGP41 by rate x TAU_S = %.6f K)," % (
        tau_s, rate * tau_s))
    print("     so the measurement cannot see it, and passes while the time constant it should bound goes untested")
    print("   what would test it: the TMP117's reading against a reference thermocouple at the SGP41 on a ramp of at least 15 K/h, the reading")
    print("     at most %.6f K behind it at 54.0 C (the time constant at most %.0f s; the 54.0 C setting holds to %.1f s)" % (
        lag, tau_s, (55.0 - 54.0 - 0.15 - 0.5) / rate - read_s))
    print()
    return lag, off_x, on_x


# ======================================================================================== item 6: the solar entry's loaded network
class Entry:
    """The drafted solar entry (apply_gen_sch_e_input_limit.py and apply_gen_sch_e_backstop.py): the source current enters PV_P;
    the 50 V bulk (three cans, its ESR in series) on PV_P; the sense bank R60 to R64 from PV_P to TRK_VS; D4 and C71 to C74
    (their ESR in series) on TRK_VS; R59 from TRK_VS to TRK_VIN; C13 to C15 and C64 on TRK_VIN with no ESR; the stage draws its
    operating current from TRK_VIN. Nodes P, S, B (the bulk's plate), A (the ceramics' plate), V. Integrated by the trapezoidal
    rule (each capacitor a conductance 2C/h with its history current), D4 a piecewise-linear branch solved per step."""

    def __init__(self, esr_b, cb, rb, ra, ca, r59, cc, vbr, rd4, i_op, v0, h):
        self.h, self.i_op, self.vbr, self.rd4, self.r59 = h, i_op, vbr, rd4, r59
        self.caps = ((2, cb), (3, ca), (4, cc))
        g = np.zeros((5, 5))

        def cond(a, b, x):
            g[a, a] += x
            g[b, b] += x
            g[a, b] -= x
            g[b, a] -= x
        cond(0, 2, 1.0 / esr_b)
        cond(0, 1, 1.0 / rb)
        cond(1, 3, 1.0 / ra)
        cond(1, 4, 1.0 / r59)
        for n, c in self.caps:
            g[n, n] += 2.0 * c / h
        g_on = g.copy()
        g_on[1, 1] += 1.0 / rd4
        self.inv = (np.linalg.inv(g), np.linalg.inv(g_on))
        # the operating point: i_op through the bank and R59, the capacitors charged, no capacitor current
        p = v0
        s = p - i_op * rb
        v = s - i_op * r59
        self.v = np.array([p, s, p, s, v])
        self.ic = {2: 0.0, 3: 0.0, 4: 0.0}

    def step(self, i_in):
        rhs = np.zeros(5)
        rhs[0] += self.i_op + i_in
        rhs[4] -= self.i_op
        for n, c in self.caps:
            rhs[n] += 2.0 * c / self.h * self.v[n] + self.ic[n]
        on = self.v[1] > self.vbr
        for _ in range(4):
            r = rhs.copy()
            if on:
                r[1] += self.vbr / self.rd4
            x = self.inv[1 if on else 0] @ r
            want = x[1] > self.vbr
            if want == on:
                break
            on = want
        for n, c in self.caps:
            self.ic[n] = 2.0 * c / self.h * (x[n] - self.v[n]) - self.ic[n]
        self.v = x
        i59 = (x[1] - x[4]) / self.r59
        id4 = (x[1] - self.vbr) / self.rd4 if on else 0.0
        return i59, id4, x[1], x[0]


def run_entry(ent, src, t_end):
    n = int(round(t_end / ent.h))
    hi = lo = (ent.v[1] - ent.v[4])
    vs = id4m = 0.0
    for k in range(1, n + 1):
        i59, id4, v_s, _v_p = ent.step(src(k * ent.h))
        d = i59 * ent.r59
        hi, lo = max(hi, d), min(lo, d)
        vs, id4m = max(vs, v_s), max(id4m, id4)
    return dict(d59=hi, d59n=lo, vs=vs, id4=id4m)


def item6():
    print("ITEM 6. L4-E7R's loaded solar entry: U5's sense differential (R59) in a separate network model")
    lt = flat(pdf("v2/vendor/power/lt8705a.pdf", 2, 2))
    must(re.search(r"VCSP-VCSN, VCSPIN-VCSNIN, .{0,120}?VCSPOUT-VCSNOUT\.+ .0\.3V to 0\.3V", lt), "8705af p.2's sense differential rating")
    print("   8705af p.2 (absolute maximum): VCSP-VCSN, VCSPIN-VCSNIN, VCSPOUT-VCSNOUT -0.3 V to 0.3 V")
    sm = flat(pdf("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", 2, 2))
    d4 = re.search(r"SMCJ28A SMCJ28CA GFG BFG (\d+\.\d) (\d+\.\d+) (\d+\.\d+) 1 (\d+\.\d) (\d+\.\d)", sm)
    must(d4, "the SMCJ28A row")
    vr, vbr_lo, vbr_hi, vc, ipp = (float(x) for x in d4.groups())
    rd4 = (vc - vbr_hi) / ipp
    t_air = 62.1
    der = 1.0 - 0.40 * (t_air - 25.0) / 125.0
    print("   SMCJ28A (Littelfuse p.2): VR %.1f V, VBR %.2f to %.2f V, VC %.1f V at IPP %.1f A; the straight line %.4f Ohm; Figure 3 read on the"
          " rendered page: 100 %% to 25 C, then straight to 60 %% at 150 C, so %.4f at %.1f C" % (vr, vbr_lo, vbr_hi, vc, ipp, rd4, der, t_air))
    z1 = flat(pdf("v2/vendor/power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf", 1, 1))
    z2 = flat(pdf("v2/vendor/power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf", 2, 2))
    zrow = re.search(r"50 33 6\.3 7\.7 D8 (\d+) (\d+) [\d.]+ EEHZA1H330XP", z2)
    zcold = re.search(r"\(.40 .C\) 2\.0 1\.4 ([\d.]+) 0\.4 0\.3", z1)
    must(zrow and zcold and "Capacitance tolerance ±20 %" in z1 and "Capacitance change Within ±30% of the initial value" in z1
         and "E. S. R. < 200 % of the initial limit" in z1, "the ZA rows")
    esr20, esr_cold, c_can = float(zrow.group(2)) * 1e-3, float(zcold.group(1)), 33e-6
    bulks = {"cold_aged": (esr_cold / 3.0, 3 * c_can * 0.8 * 0.7), "new_20": (esr20 / 3.0, 3 * c_can * 0.8),
             "aged_20": (2.0 * esr20 / 3.0, 3 * c_can * 0.8 * 0.7)}
    print("   EEHZA1H330XP (ZA, 2017-11-07): 33 uF +-20 %%, ESR %.0f mOhm at 100 kHz and 20 C, after endurance C within 30 %%, ESR under"
          " 200 %%, %.1f Ohm at -40 C (D8); three cans: cold aged %.4f Ohm with %.2f uF, new %.4f Ohm with %.2f uF" % (
              esr20 * 1e3, esr_cold, bulks["cold_aged"][0], bulks["cold_aged"][1] * 1e6, bulks["new_20"][0], bulks["new_20"][1] * 1e6))
    hj4 = flat(pdf("v2/vendor/passives/milliohm-hojlr2512-series.pdf", 4, 4))
    hj2 = pdf("v2/vendor/passives/milliohm-hojlr2512-series.pdf", 2, 2)
    life = float(re.search(r"Load Life JIS-C5201-4\.25\.1 < ±(\d+)%", hj4).group(1)) / 100.0
    sold = float(re.search(r"260±5℃ for 10±1 sec < ±([\d.]+)%", hj4).group(1)) / 100.0
    must(re.search(r"±50 \(2mR~500mR\)", hj2), "HoJLR's TCR row")
    dt_r59 = max(abs(-20.0 - 25.0), abs(70.1 - 25.0))     # RSENSE1's two ends, -20.0 and 70.1 C (L4-E7's out, line 91)
    r59 = 0.015 * 1.01 * (1 + 100e-6 * dt_r59) * (1 + life) * (1 + sold)
    w = flat(pdf("v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf", 1, 4))
    must("± 75 for 7 mΩ to 500 mΩ" in w and "Load life 1000 h at rated power, + 70 °C, 1.5 h “ON”, 0.5 h “OFF” ± (1.0 % + 0.0005 Ω)" in w
         and "Resistance to solder heat +260 °C solder, 10 s to 12 s dwell, 25 mm/s emergence ± (0.5 % + 0.0005 Ω)" in w, "the WSL rows")
    rb_lo = 0.014 * 0.99 * (1 - 75e-6 * 45.0) * (1 - (0.005 + 0.0005 / 0.07)) * (1 - (0.01 + 0.0005 / 0.07))
    rb_hi = 0.014 * 1.01 * (1 + 75e-6 * 45.0) * (1 + (0.005 + 0.0005 / 0.07)) * (1 + (0.01 + 0.0005 / 0.07))
    print("   R59 (HoJLR2512 15 mOhm 1 %%; load life %.0f %%, solder heat %.1f %%; TCR printed 50 ppm/K, the record's 100 ppm/K over %.1f K): at"
          " most %.6f Ohm; the bank (five WSL2512 70 mOhm, 75 ppm/K over 45 K, each drift plus 0.5 mOhm): %.6f to %.6f Ohm" % (
              life * 100, sold * 100, dt_r59, r59, rb_lo, rb_hi))
    i_op, v_hold = 3.7408, 17.593
    print("   the operating current at the trip's highest %.4f A (L4-E7R's check (a)), the start at the hold %.3f V; the ceramics ahead"
          " 4 x 10 uF at -10 %% times k, 10 mOhm each (the record's assumption); behind, C13 and C14 at k with C15 and C64, all +10 %%" % (i_op, v_hold))

    def net(bulk, k, h, v0=v_hold, iop=i_op, vbr=vbr_hi):
        esr_b, cb = bulks[bulk]
        return Entry(esr_b, cb, rb_lo, 0.010 / 4, 4 * 10e-6 * 0.9 * k, r59, (20e-6 * k + 4.7e-6 + 0.1e-6) * 1.10, vbr, rd4, iop, v0, h)

    # the 10/1000 us shape: the record's double exponential, and one with its time to peak at 10 us
    def shape(t1, t2):
        f = lambda t: math.exp(-t / t2) - math.exp(-t / t1)
        tp = math.log(t2 / t1) * t1 * t2 / (t2 - t1)
        fp = f(tp)
        g = lambda t: f(t) / fp
        t10 = bisect(lambda t: g(t) - 0.1, 0.0, tp)
        t90 = bisect(lambda t: g(t) - 0.9, 0.0, tp)
        t50 = bisect(lambda t: g(t) - 0.5, tp, 20 * t2)
        return g, tp, t10, t90, t50
    gA, tpA, t10A, t90A, t50A = shape(3.4e-6, 1.44e-3)
    t1B = bisect(lambda t1: math.log(1.44e-3 / t1) * t1 * 1.44e-3 / (1.44e-3 - t1) - 10e-6, 0.05e-6, 3.39e-6)
    t2B = bisect(lambda t2: shape(t1B, t2)[4] - 1000e-6, 0.8e-3, 2.0e-3)
    gB, tpB, t10B, t90B, t50B = shape(t1B, t2B)
    print("   the record's 10/1000 us shape (3.4 us, 1.44 ms): the peak at %.2f us, 10 to 90 %% %.2f to %.2f us (front 1.25 x that %.2f us),"
          " half value at %.1f us" % (tpA * 1e6, t10A * 1e6, t90A * 1e6, 1.25 * (t90A - t10A) * 1e6, t50A * 1e6))
    print("   SMCJ Figure 4 (rendered page): 'tf=10usec' drawn from the start to the peak, td to 50 %% at 1000 us; the same shape with its"
          " peak at 10 us: %.3f us, %.4f ms (peak %.2f us, half value %.1f us)" % (t1B * 1e6, t2B * 1e3, tpB * 1e6, t50B * 1e6))
    res = {}
    for lab, amp, bulk in (("capability, cold end (D4 33.1 A, the bulk aged, -40 C row)", ipp, "cold_aged"),
                           ("capability, hot end (D4 derated, the bulk new)", ipp * der, "new_20"),
                           ("capability, hot end (D4 derated, the bulk aged)", ipp * der, "aged_20")):
        for sname, g in (("record's shape", gA), ("peak at 10 us", gB)):
            best = None
            for k in (1.0, 0.5, 0.25):
                r = run_entry(net(bulk, k, 10e-9), lambda t, g=g, a=amp: a * g(t), 300e-6)
                if best is None or r["d59"] > best["d59"]:
                    best = dict(r, k=k)
            res[(lab, sname)] = best
            print("   %-60s %-15s U5 %.4f V (k %.2f), min %.4f V; TRK_VS %.2f V; D4 %.2f A" % (
                lab, sname, best["d59"], best["k"], best["d59n"], best["vs"], best["id4"]))
    # the step size: the worst case again at half the step
    wl = ("capability, cold end (D4 33.1 A, the bulk aged, -40 C row)", "record's shape")
    chk = run_entry(net("cold_aged", res[wl]["k"], 5e-9), lambda t: ipp * gA(t), 300e-6)["d59"]
    print("   the step checked: the cold end %.4f V at 5 ns against %.4f V at 10 ns" % (chk, res[wl]["d59"]))
    # M7: the discharge through 150 pF and 330 Ohm, +30 % (Table IX), injected at PV_P
    for kv in (8e3, 15e3):
        best = None
        for bulk in ("cold_aged", "new_20"):
            for k in (1.0, 0.5, 0.25):
                r = run_entry(net(bulk, k, 0.25e-9), lambda t, kv=kv: 1.3 * kv / 330.0 * math.exp(-t / (330.0 * 150e-12)), 1.5e-6)
                if best is None or r["d59"] > best["d59"]:
                    best = dict(r, k=k, bulk=bulk)
        src = lambda t, kv=kv: 1.3 * kv / 330.0 * math.exp(-t / (330.0 * 150e-12))
        v1 = run_entry(net(best["bulk"], best["k"], 0.125e-9), src, 1.5e-6)["d59"]
        v2 = run_entry(net(best["bulk"], best["k"], 0.0625e-9), src, 1.5e-6)["d59"]
        best["conv"] = 2 * v2 - v1                     # Richardson on the step (first order in the sampled peak)
        res[("M7", kv)] = best
        print("   M7 %2.0f kV (%.2f A peak): U5 %.4f V at 0.25 ns, %.4f and %.4f V at 0.125 and 0.0625 ns, %.4f V extrapolated (%s, k %.2f);"
              " min %.4f V; TRK_VS %.2f V; D4 %.2f A" % (kv / 1e3, 1.3 * kv / 330.0, best["d59"], v1, v2, best["conv"], best["bulk"], best["k"],
                                                          best["d59n"], best["vs"], best["id4"]))
    # CS116 (461G 5.14) at 1 MHz, 10 A: the bound (the whole current through R59 on top of the operating current) and the network
    bound = (i_op + 10.0) * r59
    print("   CS116 at 10 A, the bound (the whole current in R59 with the operating current, no capacitor credited): (%.4f + 10) A x"
          " %.6f Ohm = %.4f V (the record: 0.2123 V); the bank %.4f V (the record's U18: 0.2007 V)" % (i_op, r59, bound, (i_op + 10.0) * rb_hi))
    best = None
    f = 1e6
    for start, v0, iop in (("operating at the hold", v_hold, i_op), ("open at 25 V, the stage off", 25.0, 0.0)):
        for bulk in ("cold_aged", "new_20"):
            for k in (1.0, 0.5, 0.25):
                for q in (10.0, 20.0):
                    for sgn in (1.0, -1.0):
                        src = lambda t, q=q, sgn=sgn: sgn * 10.0 * math.exp(-math.pi * f * t / q) * math.sin(2 * math.pi * f * t)
                        r = run_entry(net(bulk, k, 2e-9, v0=v0, iop=iop), src, 8 * q / (math.pi * f))
                        if best is None or max(r["d59"], -r["d59n"]) > max(best["d59"], -best["d59n"]):
                            best = dict(r, start=start, bulk=bulk, k=k, q=q, sgn=sgn)
    res["CS116"] = best
    print("   CS116 1 MHz, 10 A, in the network (two starts, both bulks, k, Q 10 and 20, both polarities): U5 at most %.4f V, least %.4f V"
          " (%s, %s, k %.2f, Q %.0f); TRK_VS %.2f V; D4 %.2f A (the record: U5 0.1238 V, TRK_VS 25.16 V, D4 0 A)" % (
              best["d59"], best["d59n"], best["start"], best["bulk"], best["k"], best["q"], best["vs"], best["id4"]))
    print()
    return res, bound


# ======================================================================================== item 7: Q7 against Figure 4-10
def soa_from_trace():
    """SLPS540C p.6, Figure 4-10, from the page's vector drawing (mutool's trace): the plot frame, the tick labels, the IDM line
    and the 100 V edge as anchors, each line by its legend's colour and label."""
    tr = subprocess.run(["mutool", "draw", "-F", "trace", "-o", "-", rel("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf"), "6"],
                        capture_output=True, check=True).stdout.decode("utf-8", "replace")
    fig = tr[:tr.find('<layer name="P"/>')]
    paths = []
    for m in re.finditer(r'<stroke_path linewidth="([\d.]+)"[^>]*linecap="([\d,]+)"[^>]*color="([^"]*)"[^>]*transform="([^"]*)">(.*?)</stroke_path>', fig, re.S):
        a, b, c, d, e, f = (float(x) for x in m.group(4).split())
        pts = [(a * float(x) + c * float(y) + e, b * float(x) + d * float(y) + f)
               for x, y in re.findall(r'<(?:moveto|lineto) x="([-\d.e]+)" y="([-\d.e]+)"', m.group(5))]
        paths.append((float(m.group(1)), m.group(2), m.group(3), pts))
    texts = []
    for m in re.finditer(r'<fill_text[^>]*transform="([^"]*)">(.*?)</fill_text>', fig, re.S):
        a, b, c, d, e, f = (float(x) for x in m.group(1).split())
        for sp in re.finditer(r'<span [^>]*>(.*?)</span>', m.group(2), re.S):
            gl = re.findall(r'<g unicode="([^"]*)" glyph="[^"]*" x="([-\d.e]+)" y="([-\d.e]+)"', sp.group(1))
            if gl:
                x, y = float(gl[0][1]), float(gl[0][2])
                texts.append(("".join(g[0] for g in gl), a * x + c * y + e, b * x + d * y + f))
    frames = [p for p in paths if p[2] == "0" and p[1] == "1,1,1" and len(p[3]) == 4]
    fr = max(frames, key=lambda p: (max(x for x, _ in p[3]) - min(x for x, _ in p[3])) * (max(y for _, y in p[3]) - min(y for _, y in p[3])))[3]
    x0, x1 = min(x for x, _ in fr), max(x for x, _ in fr)
    y0, y1 = max(y for _, y in fr), min(y for _, y in fr)          # y grows downward: y0 the bottom (0.1 A), y1 the top (1000 A)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 4.0 * (y0 - y) / (y0 - y1)
    xt = {s: x for s, x, y in texts if s in ("0.1", "1", "10", "100") and y > y0 + 2.0}      # the voltage axis, under the frame
    must(abs(lv(xt["1"]) - 0.0) < 0.1 and abs(lv(xt["100"]) - 2.0) < 0.15, "Figure 4-10's voltage ticks against its frame")
    legend = [(p[2], p[3][0]) for p in paths if p[1] == "2,2,2" and p[0] > 5]
    lab = {}
    for col, (lx, ly) in legend:
        near = min((t for t in texts if 0 < t[1] - lx < 30 and abs(t[2] - ly) < 6), key=lambda t: (round(abs(t[2] - ly), 1), t[1] - lx))
        lab[near[0].replace("µ", "u").replace(" ", "")] = col
    must(sorted(lab) == ["100us", "10ms", "1ms", "DC"], "Figure 4-10's legend: %s" % sorted(lab))
    lines = {}
    for name, col in lab.items():
        cand = [p[3] for p in paths if p[2] == col and p[1] == "0,0,0" and p[0] > 5]
        must(len(cand) == 1, "Figure 4-10's %s line" % name)
        lines[name] = [(lv(x), li(y)) for x, y in cand[0]]
    cap = [p[3] for p in paths if p[2] == "0" and p[1] == "0,0,0" and p[0] > 5]
    must(len(cap) == 1, "Figure 4-10's IDM line")
    idm = 10 ** li(cap[0][0][1])
    vmax = 10 ** lv(cap[0][-1][0])
    must(abs(idm - 400.0) < 4.0 and abs(vmax - 100.0) < 1.0, "Figure 4-10's 400 A and 100 V anchors (%.1f A, %.2f V)" % (idm, vmax))
    rds = [p[3] for p in paths if p[2] == ".501953" and p[0] > 5][0]
    rds = [(lv(x), li(y)) for x, y in rds]
    for name in lines:
        lines[name] = (lines[name], rds)
    return lines, idm, rds


def line_at(line, v):
    """A line's current at VDS v (log-log along its polyline; at or above the 400 A cap left of its first point)."""
    pts, rds = line
    lx = math.log10(v)

    def along(poly):
        if lx <= poly[0][0]:
            return 10 ** poly[0][1]
        for (xa, ya), (xb, yb) in zip(poly, poly[1:]):
            if xa <= lx <= xb and xb > xa:
                return 10 ** (ya + (yb - ya) * (lx - xa) / (xb - xa))
        return 10 ** poly[-1][1]
    return along(pts)      # left of a line's first point, its 400 A corner; the grey RDS(on) line is a conduction limit, not a thermal one


def soa_t(lines, v, t):
    """The chart's current at VDS v for a single pulse of t s: log-log between the 100 us, 1 ms and 10 ms lines; a pulse
    shorter than 100 us takes the 100 us line's value (a shorter pulse is allowed more)."""
    tl = [(1e-4, "100us"), (1e-3, "1ms"), (1e-2, "10ms")]
    if t <= tl[0][0]:
        return line_at(lines["100us"], v)
    for (ta, a), (tb, b) in zip(tl, tl[1:]):
        if ta <= t <= tb:
            ia, ib = math.log10(line_at(lines[a], v)), math.log10(line_at(lines[b], v))
            return 10 ** (ia + (ib - ia) * (math.log10(t) - math.log10(ta)) / (math.log10(tb) - math.log10(ta)))
    ia, ib = math.log10(line_at(lines["1ms"], v)), math.log10(line_at(lines["10ms"], v))
    return 10 ** (ib + (ib - ia) * (math.log10(t) - math.log10(1e-2)))


def start_into_fault(lines, vin, s, c, rf, ioc, toc, isc, tau, tsc, derate, dt=0.1e-6):
    """A start into a resistive fault rf, stepped in time: the output follows the gate at s V/s, Q7 carries c s + Vout / rf with
    VIN - Vout across it; the overcurrent timer starts when the current passes ioc and turns Q7 off toc later; the short-circuit
    path sees the current through a first-order filter tau and turns Q7 off tsc after the filtered current passes isc. Every
    point of the pulse is held against the chart line for the whole pulse (as the record holds it)."""
    t, y, t_oc, t_sc = 0.0, 0.0, None, None
    hist = []
    tf = vin / s
    while True:
        vout = min(s * t, vin)
        i = (c * s if vout < vin else 0.0) + vout / rf
        hist.append((t, vin - vout, i))
        if t_oc is None and i >= ioc:
            t_oc = t + toc
        if t_sc is None and y >= isc:
            t_sc = t + tsc
        ends = [x for x in (t_oc, t_sc) if x is not None]
        if (ends and t >= min(ends)) or t >= tf:
            break
        i_next = (c * s if min(s * (t + dt), vin) < vin else 0.0) + min(s * (t + dt), vin) / rf
        a = (i_next - i) / dt                                       # the filter, exact for a current linear over the step
        ex = math.exp(-dt / tau)
        y = i_next - a * tau + (y - i + a * tau) * ex
        t += dt
    t_end = t
    ends = [(x, w) for x, w in ((t_sc, "the short-circuit trip"), (t_oc, "the overcurrent delay")) if x is not None and t_end >= x - 1e-12]
    how = min(ends)[1] if ends else "the start completes"
    worst = 0.0
    for _t, vds, i in hist[::5] + [hist[-1]]:
        if vds <= 0.0:
            continue
        worst = max(worst, i / (derate * soa_t(lines, vds, t_end)))
    return worst, t_end, how


def item7():
    print("ITEM 7. Q7 (CSD19536KTT) on the selected vehicle entry against Figure 4-10, derated")
    lines, idm, rds = soa_from_trace()
    vin = 43.18
    at = {k: line_at(v, vin) for k, v in lines.items()}
    print("   SLPS540C (rev. C, May 2025) p.6, Figure 4-10 'Single pulse, max RthJC = 0.4 C/W', read from the page's vector drawing (mutool"
          " trace): IDM line %.1f A; at %.2f V: 100 us %.1f A, 1 ms %.2f A, 10 ms %.3f A, DC %.3f A (the record: 221.7, 20.02, 6.228 A)" % (
              idm, vin, at["100us"], at["1ms"], at["10ms"], at["DC"]))
    must(abs(at["100us"] - 221.7) < 1.0, "the 100 us line near the record's reading")
    p1 = flat(pdf("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", 1, 1))
    must(re.search(r"Operating Junction, .{0,60}?\u201355 to 175", p1) or re.search(r"\u201355 to 175", p1), "the CSD19536KTT's 175 C")
    derate = 0.4454
    print("   the derating the record carries (L4-E9's, A-25): %.4f = (150 - 94.32) / 125, a 94.3 C case on a 150 C part; on the CSD19536KTT's"
          " own 175 C (SLPS540C p.1) it equals (175 - %.2f) / 150, so it is conservative while Q7's case stays under %.2f C (at 94.3 C"
          " its own would be %.4f)" % (derate, 175.0 - derate * 150.0, 175.0 - derate * 150.0, (175.0 - 94.3) / 150.0))
    # Equation 7 (SLUSEE5E p.23) and the loaded tOC row (p.10)
    t48 = flat(pdf("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf"))
    must(re.search(r"I\(TMR_SRC_CB\) TMR source current 73 82 91 µA", t48) and re.search(r"V\(TMR_OC\) 1\.112 1\.2 1\.3 V", t48), "the TMR rows")
    must(re.search(r"Over current protection delay 370 µs = 47nF, CTMR = 22nF", t48), "the loaded tOC row")
    must(re.search(r"CTMR = TMR1\.2 OC", t48) and "is internal pull-up current of 82µA" in t48, "Equation 7")
    c_lo = 22e-9 * 0.95 * 0.97 * (1 - 0.0024)
    c_hi = 22e-9 * 1.05 * 1.03 * (1 + 0.0058)
    eq7 = (1.112 * c_lo / 91e-6, 1.2 * 22e-9 / 82e-6, 1.3 * c_hi / 73e-6)
    k = 370e-6 / eq7[1]
    toc = max(eq7[2] * k, eq7[2] + 370e-6 - eq7[1])
    print("   Equation 7 (SLUSEE5E p.23, tOC = CTMR x V(TMR_OC) / ITMR) with the TMR rows (73 / 82 / 91 uA, 1.112 / 1.2 / 1.3 V, p.9) and CTMR"
          " 22 nF in the record's band (5 %%, endurance 3 %%, +0.58 / -0.24 %%): %.4f / %.4f / %.4f ms; the loaded row 370 us typical"
          " (CL 47 nF, CTMR 22 nF, p.10) is %.4f times Equation 7's typical; the maximum %.4f x %.4f = %.4f ms (the record: 0.49 ms)" % (
              eq7[0] * 1e3, eq7[1] * 1e3, eq7[2] * 1e3, k, eq7[2] * 1e3, k, toc * 1e3))
    slew = (0.63 * 11.0 / (36.5e3 * 1.01 * 10e-9 * 1.05 * 1.03 * 1.0058), 0.63 * 13.0 / (36.5e3 * 0.99 * 10e-9 * 0.95 * 0.97 * (1 - 0.0024)))
    must(re.search(r"0\.63 × V BST − SRC × CLOAD IINRUSH = R1 × C1", t48), "Equation 3")
    print("   Equation 3 (p.20): the slew 0.63 x V(BST-SRC) / (R1 C1) at 11 and 13 V, R1 36.5k 1 %%, C1 10 nF in the same band: %.2f to %.2f V/ms"
          " (the record: 17.28 to 24.65)" % (slew[0] / 1e3, slew[1] / 1e3))
    ioc, isc, tau, tsc = 7.136, 13.87, 3.01e-6 * 1.01 * 1.05 * 1.03 * 1.0058, 5e-6
    print("   the breaker at its slowest (the record's thresholds): overcurrent %.3f A for %.4f ms; short circuit %.2f A through %.3f us,"
          " then tSC %.0f us (TPS48110, p.10's maximum)" % (ioc, toc * 1e3, isc, tau * 1e6, tsc * 1e6))
    worst = (0.0,)
    for s in slew:
        for c in (22.1e-6, 49.5e-6):
            for kk in range(161):
                rf = 10 ** (-1.0 + 4.0 * kk / 160)
                r = start_into_fault(lines, vin, s, c, rf, ioc, toc, isc, tau, tsc, derate, dt=1e-6)
                if r[0] > worst[0]:
                    worst = (r[0], rf, s, c)
    lo_, hi_ = worst[1] / 10 ** (4.0 / 160), worst[1] * 10 ** (4.0 / 160)
    best = (0.0,)
    for kk in range(81):
        rf = lo_ * (hi_ / lo_) ** (kk / 80)
        r = start_into_fault(lines, vin, worst[2], worst[3], rf, ioc, toc, isc, tau, tsc, derate, dt=0.1e-6)
        if r[0] > best[0]:
            best = (r[0], rf, r[1], r[2])
    print("   a start into a resistive fault (0.1 to 1000 Ohm, both slews, 22.1 and 49.5 uF, stepped at 0.1 us near the worst): %.4f of the"
          " derated chart at %.3f Ohm, %.4f ms, ended by %s (slew %.2f V/ms, %.1f uF) (the record: 0.704 at 1.21 Ohm, 0.954 ms)" % (
              best[0], best[1], best[2] * 1e3, best[3], worst[2] / 1e3, worst[3] * 1e6))
    # a start into a hard short: VDS stays at VIN, the current rises at gfs x the highest slew from the threshold
    p3 = flat(pdf("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", 3, 3))
    gfs = float(re.search(r"gfs Transconductance VDS = 10V, ID = 100A (\d+) S", p3).group(1))
    a_g = gfs * slew[1]
    t, y, dt = 0.0, 0.0, 1e-9
    while y < isc:
        t += dt
        y = a_g * (t - tau * (1 - math.exp(-t / tau)))
    tp = t + tsc
    ip = a_g * tp
    frac = ip / (derate * soa_t(lines, vin, tp))
    print("   a start into a hard short: gfs %.0f S (typical, at 100 A; p.3) x %.2f V/ms = %.3f A/us; the filtered current reaches %.2f A at"
          " %.3f us, then %.0f us: %.2f A at %.3f us, %.4f of the derated 100 us line (the record: 73.4 A after 9.04 us, 0.743)" % (
              gfs, slew[1] / 1e3, a_g / 1e6, isc, t * 1e6, tsc * 1e6, ip, tp * 1e6, frac))
    print("   what stays conditional (unchanged): the transconductance is typical only, taken as a bound (A11-10, E11-17, R-118); a"
          " hard short in service rests on the loop's inductance (R-134); the case under %.2f C for the derating" % (175.0 - derate * 150.0))
    print()
    return dict(at=at, toc=toc, fault=best, short=(ip, tp, frac), slew=slew)


# ======================================================================================== item 9: the VBUS20 loop with Cc2 3.3 nF
def loop_margins(cfg, rc1, cc1, cc2, bank, cl, iout, q, fsw, g, lk, mode, vin, nf=6000):
    """The LM5176 peak-current loop as SNVSAI1D pp.26 to 28 set it out (the boost output pole at Rout/2, the RHP zero Rout (1-D)^2 / L,
    the gmEA type II compensator Rc1 + 1/sCc1 with Cc2 across, ROUT 20 MOhm), with the sampling double pole at Fsw/2 of quality q,
    the bank as n branches of (C, R) and the local ceramics: T = kFB gmEA g Zc Gc Zout. The phase is the SUM of each factor's own
    angle (no unwrapping); each |T| = 1 and each -180 degree crossing is located by bisection on the closed form."""
    vout, kfb, gm, ro, ri, L = cfg["vout"], cfg["kfb"], cfg["gm"] * g, cfg["ro"], cfg["acs"] * cfg["rcs"], cfg["L"] * lk
    rl = vout / iout
    d = 1.0 - vin / vout if mode == "boost" else 0.0
    wrhp = rl * (1.0 - d) ** 2 / L if mode == "boost" else None
    wn = math.pi * fsw

    def T(f):
        f = np.atleast_1d(np.asarray(f, dtype=float))
        w = 2 * np.pi * f
        s = 1j * w
        zc = 1.0 / (1.0 / (rc1 + 1.0 / (s * cc1)) + s * cc2 + 1.0 / ro)
        yb = sum(n / (1.0 / (s * c) + r) for n, c, r in bank)
        zout = 1.0 / (1.0 / (1.0 / (s * cl) + cfg["esr_l"]) + yb + 1.0 / (rl * (0.5 if mode == "boost" else 1.0)))
        h = 1.0 / (1.0 + s / (wn * q) + (s / wn) ** 2)
        gc = (1.0 - d) / ri * (1.0 - s / wrhp) * h if mode == "boost" else h / ri
        t = kfb * gm * gc * zout * zc
        ph = (np.arctan2(zc.imag, zc.real) + np.arctan2(zout.imag, zout.real)
              - np.arctan2(w / (wn * q), 1.0 - (w / wn) ** 2) - (np.arctan(w / wrhp) if mode == "boost" else 0.0))
        return np.abs(t), np.degrees(ph), np.abs(zout / (1.0 + t)), np.abs(1.0 + t)
    fs = np.logspace(1.0, math.log10(cfg["fhi"] / 2.0), nf)
    mag, ph, zcl, m1 = T(fs)
    pm, gmarg, fc, mm, zmax = 999.0, 999.0, [], float(m1.min()), float(zcl.max())
    for j in np.nonzero((mag[:-1] - 1.0) * (mag[1:] - 1.0) <= 0.0)[0]:
        fx = bisect(lambda lf: T(10 ** lf)[0][0] - 1.0, math.log10(fs[j]), math.log10(fs[j + 1]), 50)
        fc.append(10 ** fx)
        pm = min(pm, 180.0 + T(10 ** fx)[1][0])
    for j in np.nonzero((ph[:-1] + 180.0) * (ph[1:] + 180.0) <= 0.0)[0]:
        fx = bisect(lambda lf: T(10 ** lf)[1][0] + 180.0, math.log10(fs[j]), math.log10(fs[j + 1]), 50)
        gmarg = min(gmarg, -20.0 * math.log10(T(10 ** fx)[0][0]))
    return dict(pm=pm, gm=gmarg, fc=fc, mm=mm, z=zmax, rhp3=(wrhp / (2 * math.pi) / 3.0) if wrhp else 1e12)


def item9():
    print("ITEM 9. L4-E8's VBUS20 loop with Cc2 3.3 nF at the cold corner, in a separate loop model")
    lm = flat(pdf("v2/vendor/ti/lm5176-datasheet.pdf", 6, 6))
    must(re.search(r"gmEA Error amplifier gm 1\.31 mS", lm) and re.search(r"ROUT Amplifier output resistance 20 M. ", lm)
         and re.search(r"VREF Feedback reference voltage FB = COMP 0\.788 0\.800 0\.812 V", lm), "LM5176 p.6's amplifier rows")
    lm24 = flat(pdf("v2/vendor/ti/lm5176-datasheet.pdf", 24, 24))
    must(re.search(r"RSENSE u ACS 8 m: u 5", lm24), "LM5176 p.24's ACS 5 (Equation 26)")
    lm27 = flat(pdf("v2/vendor/ti/lm5176-datasheet.pdf", 27, 28))
    must("ROUT u (1 DMAX )2" in lm27 and "High frequency pole (fpc2) is placed using a capacitor (Cc2)" in lm27.replace("A high", "High"),
         "SNVSAI1D's Equations 38 to 46")
    ga = txt("v2/ecad/tools/gen_sch_a.py")
    must('lm5176("FE", "U2", "VIN_RAW", "VBUS20", "FE_EN", "240k", "L1", "10uH XAL1010-103ME (Isat 17.5 A)"' in ga, "the front end's call")
    out8 = txt("v2/docs/records/l4e8/ripple_dense.out")
    must("7. THE LOOP WITH THE BALLAST OVER THE COLD ENVELOPE (the recheck's R4), B3's envelope, R12 12 mOhm (L4-E6), loads 8.300 / 7.262 / 5.700 / 0.250 A" in out8
         and "(Middlebrook's bound at 166 W); the bank's corners C 0.56 / 1.56 x 330 uF" in out8, "L4-E8's out 7 header")
    must("171.76 / 199.04 / 227.08 kHz" in out8, "B3's envelope")
    must("fifteen local ceramics, 60 to 102 uF" in flat(txt("v2/docs/records/r4a/r4-decisions.md")), "the FE stage's ceramic band")
    hj2 = pdf("v2/vendor/passives/milliohm-hojlr2512-series.pdf", 2, 2)
    must(re.search(r"±50 \(2mR~500mR\)", hj2), "HoJLR's TCR")
    rb, rb_tol = 0.045, 0.01 + 50e-6 * 75.0
    cfg = dict(vout=0.8 * (1 + 240.0 / 10.0), kfb=10.0 / 250.0, gm=1.31e-3, ro=20e6, acs=5.0, rcs=0.012, L=10e-6, esr_l=0.0004,
               fhi=227.078e3, f0=199.044e3)
    print("   SNVSAI1D (rev. D) p.6: gmEA 1.31 mS and ROUT 20 MOhm (typical only; gmEA x0.8 and x1.2 as the record), VREF 0.800 V;"
          " p.24 ACS 5; pp.26 to 28 Equations 38 to 46")
    print("   the plant: VBUS20 %.1f V (240k over 10k), kFB %.3f; L1 10 uH; R12 12 mOhm (L4-E6); six 330 uF cans at 0.56 / 1.56 x, each behind"
          " 45 mOhm +-%.5f with its intrinsic ESR e; 21 ceramics 84 to 142.8 uF (60 to 102 uF for fifteen, scaled), 0.4 mOhm; loads 8.300,"
          " 7.262, 5.700 and 0.250 A; boost at 9 V, buck at 24 and 36 V; Fsw 171.763 to 227.078 kHz; Q 0.4 / 0.8 (widened 0.4 / 1.5 with"
          " L x0.8 / x1.2)" % (cfg["vout"], cfg["kfb"], rb_tol))
    loads = (8.300, 7.262, 5.700, 0.250)
    zlim = cfg["vout"] ** 2 / (cfg["vout"] * loads[0]) / 3.0
    import itertools

    def env(e, cc2, wide):
        bank_sets = [[(6, k * 330e-6, x)] for k in (0.56, 1.56) for x in (rb * (1 - rb_tol) + e, rb * (1 + rb_tol) + e)]
        qs, lks = ((0.4, 1.5), (0.8, 1.2)) if wide else ((0.4, 0.8), (1.0,))
        agg = dict(pm=999.0, gm=999.0, mm=9.0, fc_hi=0.0, ceil=True, z=0.0)
        for (mode, vin), cl, iout, q, fsw, g, lk, bank in itertools.product((("boost", 9.0), ("buck", 36.0), ("buck", 24.0)),
                                                                          (84e-6, 142.8e-6), loads, qs, (171.763e3, 227.078e3),
                                                                          (0.8, 1.2), lks, bank_sets):
            r = loop_margins(cfg, 15e3, 220e-9, cc2, bank, cl, iout, q, fsw, g, lk, mode, vin, nf=1000)
            agg["pm"], agg["gm"], agg["mm"] = min(agg["pm"], r["pm"]), min(agg["gm"], r["gm"]), min(agg["mm"], r["mm"])
            fh = max(r["fc"]) if r["fc"] else 0.0
            agg["fc_hi"] = max(agg["fc_hi"], fh)
            agg["ceil"] = agg["ceil"] and 0.0 < fh <= min(cfg["f0"] / 20.0, r["rhp3"])
            agg["z"] = max(agg["z"], r["z"])
        return agg
    rows = []
    for lab, e, k in (("Cc2 3.3 nF, e 0", 0.0, 1.0), ("Cc2 3.3 nF, e 300 mOhm (the cold corner)", 0.3, 1.0),
                      ("Cc2 3.3 nF x0.75, e 300 mOhm", 0.3, 0.75), ("Cc2 3.3 nF x1.25, e 300 mOhm", 0.3, 1.25),
                      ("Cc2 3.3 nF x1.25, e 0", 0.0, 1.25), ("Cc2 3.3 nF x0.75, e 0", 0.0, 0.75), ("Cc2 680 pF (drawn), e 300 mOhm", 0.3, 680e-12 / 3.3e-9)):
        dflt, wide = env(e, 3.3e-9 * k, False), env(e, 3.3e-9 * k, True)
        ok = all(a["pm"] >= 50 and a["gm"] >= 10 and a["mm"] >= 0.5 and a["ceil"] and a["z"] <= zlim for a in (dflt, wide))
        rows.append((lab, dflt, wide, ok))
        print("   %-44s PM %.1f deg, GM %.2f dB (widened %.1f deg, %.2f dB), |1+T| %.2f, crossover to %.2f kHz, |Zout| %.0f mOhm"
              " against %.0f: %s" % (lab, dflt["pm"], dflt["gm"], wide["pm"], wide["gm"], min(dflt["mm"], wide["mm"]),
                                     max(dflt["fc_hi"], wide["fc_hi"]) / 1e3, max(dflt["z"], wide["z"]) * 1e3, zlim * 1e3,
                                     "every margin" if ok else "A MARGIN MISSED"))
    print("   the record (out 7): e 0 PM 61.4, GM 19.7 / 17.9 dB; e 300 PM 86.1, GM 15.8 / 14.4 dB; x0.75 e 300 GM 13.7 / 12.3 dB; x1.25 e 0"
          " PM 57.0; the drawn 680 pF at e 300 GM 5.0 / 3.1 dB")
    print()
    return rows


# ======================================================================================== item 11: the rating-category headings
HEADINGS = [   # (pattern, the category a row under it carries)
    (r"Absolute Maximum Ratings", "absolute"), (r"Absolute maximum ratings", "absolute"),
    (r"Recommended Operating Conditions", "recommended"), (r"Recommended operating conditions", "recommended"),
    (r"ESD Ratings", "other"), (r"Thermal Information", "other"), (r"Electrical Characteristics", "other"),
    (r"Handling Ratings", "other"), (r"Thermal Characteristics", "other"), (r"Package Thermal Data", "other"),
]
STATEMENTS = [  # key, part, sheet, the row as printed (a pattern), the record's category (l4e12_thermal.py CAT)
    ("pcm_rec", "PCM2912A", "v2/vendor/ti/ti-pcm2912a.pdf", r"TA\s+Operating free-air temperature\s+\u2013\d+\s+\d+", "recommended"),
    ("pcm_bias", "PCM2912A", "v2/vendor/ti/ti-pcm2912a.pdf", r"Ambient temperature under bias\s+\u2013\d+\s+\d+", "absolute"),
    ("pcm_st", "PCM2912A", "v2/vendor/ti/ti-pcm2912a.pdf", r"Storage temperature, Tstg\s+\u2013\d+\s+\d+", "absolute (storage)"),
    ("tlv755_tjabs", "TLV755P", "v2/vendor/ti/held/ti-tlv755p-c404027.pdf", r"Operating junction temperature range, TJ\s+-\d+\s+\d+", "absolute"),
    ("tlv755_tjrec", "TLV755P", "v2/vendor/ti/held/ti-tlv755p-c404027.pdf", r"TJ\s+Junction temperature\s+\u2013\d+\s+\d+", "recommended"),
    ("tlv758_tjabs", "TLV758P", "v2/vendor/ti/ti-tlv758p.pdf", r"Operating junction, TJ\s+\u2013\d+\s+\d+", "absolute"),
    ("tlv758_tjrec", "TLV758P", "v2/vendor/ti/ti-tlv758p.pdf", r"TJ\s+Junction temperature\s+\u2013\d+\s+\d+\s+°C", "recommended"),
    ("tusb8041_tj", "TUSB8041", "v2/vendor/ti/ti-tusb8041.pdf", r"TJ\s+Operating junction temperature\s+\u2013\d+\s+\d+", "recommended"),
    ("lvc2g07_ta", "SN74LVC2G07", "v2/vendor/ti/ti-sn74lvc2g07.pdf", r"TA\s+Operating free-air temperature\s+\u2013\d+\s+\d+", "recommended"),
    ("lv1t08_ta", "SN74LV1T08", "v2/vendor/ti/ti-sn74lv1t08.pdf", r"TA\s+Operating free-air temperature\s+\u2013\d+\s+\d+", "recommended"),
    ("tps62933_tj", "TPS62933", "v2/vendor/ti/ti-tps62933.pdf", r"TJ\s+Operating junction temperature\(2\)\s+\u2013\d+\s+\d+", "absolute"),
    ("ap64500_tjop", "AP64500", "v2/vendor/diodes/diodes-ap64500.pdf", r"Operating Junction Temperature Range\s+-\d+\s+\+\d+", "recommended"),
    ("ap64500_tj", "AP64500", "v2/vendor/diodes/diodes-ap64500.pdf", r"TJ\s+Junction Temperature\s+\+\d+", "absolute"),
    ("ap6320_tj", "AP63200 series", "v2/vendor/diodes/diodes-ap63200-series-buck.pdf", r"TJ\s+Junction Temperature\s+\+\d+", "absolute"),
    ("ap2112_tj", "AP2112", "v2/vendor/diodes/diodes-ap2112-ldo.pdf", r"Operating Junction Temperature Range\s+\+\d+", "absolute"),
    ("csd77_tj", "CSD17577Q5A", "v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf", r"\u2013\d+ to \d+\s+°C", "absolute"),
    ("csd78_tj", "CSD17578Q5A", "v2/vendor/ti/held/ti-csd17578q5a-slps526.pdf", r"\u2013\d+ to \d+\s+°C", "absolute"),
    ("bme_st", "BME688", "v2/vendor/bosch/bosch-bme688.pdf", r"Storage temperature\s+≤ 65% r\.H\.\s+-\d+\s+\+\d+", "absolute (Table 11, storage)"),
]


def heading_before(p, pat):
    """The statement's first page and the heading nearest before it, on its page or, if none there, on the pages before."""
    n = npages(p)
    pages = [pdf(p, k, k) for k in range(1, n + 1)]
    for k, t in enumerate(pages):
        m = re.search(pat, t)
        if not m:
            continue
        for back in range(k, -1, -1):
            seg = t[:m.start()] if back == k else pages[back]
            hits = []
            for hp, cat in HEADINGS:
                for h in re.finditer(r"(?m)(?:^|\s{2,})[\d.]*\s*(?:Table \d+: )?" + hp, seg):   # a heading, not a sentence
                    hits.append((h.end(), hp, cat))
            if hits:
                pos, hp, cat = max(hits)
                row = re.sub(r"\s+", " ", m.group(0)).replace("\u2013", "-")      # the sheet's minus, printed as a hyphen
                return k + 1, back + 1, hp, cat, row
        return k + 1, None, None, None, re.sub(r"\s+", " ", m.group(0))
    return None, None, None, None, None


def item11():
    print("ITEM 11. L4-E12's rating categories: the heading each statement (other than the SGP41's four) sits under, read on its page")
    out12 = flat(txt("v2/docs/records/l4e12/l4e12_thermal.out"))
    keys = re.search(r"0f The rating categories \(1j\): the heading each of 22 statements is printed under read before it on its page, "
                     r"with no competing heading between \(([^)]*)\)", out12).group(1).split(", ")
    must(len(keys) == 22, "L4-E12's 22 statements")
    mine = sorted(k for k in keys if not k.startswith("sgp_"))
    must(mine == sorted(s[0] for s in STATEMENTS), "the 18 statements other than the SGP41's: %s" % mine)
    src = txt("v2/docs/records/l4e12/l4e12_thermal.py")
    agree = 0
    parts = set()
    for key, part, p, pat, cat in STATEMENTS:
        m = re.search(r'"%s": "([^"]*)"' % key, src)
        must(m and m.group(1) == cat, "the record's category for %s" % key)
        page, hpage, head, hcat, row = heading_before(p, pat)
        must(page is not None and head is not None, "%s's row and a heading before it" % key)
        ok = cat.startswith(hcat)
        agree += ok
        parts.add(part)
        print("   %-13s %-16s p.%-2d %-52s under '%s' (p.%d): the sheet %-11s the record %-28s %s" % (
            key, part, page, row[:52], head, hpage, hcat, cat, "MATCHES" if ok else "DIFFERS"))
    print("   %d of %d statements on %d parts match the category of the heading they sit under" % (agree, len(STATEMENTS), len(parts)))
    print()
    return agree, len(STATEMENTS), len(parts)


def main():
    global HELD_ROOT
    ap = argparse.ArgumentParser(description="the independent verification of the findings ledger's concrete remaining risks")
    ap.add_argument("--held-root", default=TOP, help="a checkout whose ignored held/ folders carry the held sheets")
    HELD_ROOT = os.path.abspath(ap.parse_args().held_root)
    print("verify_risks.py: the independent verification of the findings ledger's concrete remaining risks (MESHSAT-1357, 2 October 2026)")
    print("on set 27; items 2 to 7, 9 and 11")
    print()
    ok2 = item2()
    item3()
    item4()
    item5()
    item6()
    item7()
    item9()
    agree, n11, _p = item11()
    print("SUMMARY: item 2 %s; item 3 CONFIRMED; item 4 CONFIRMED; item 5 DIFFERS (the row and the arithmetic confirmed; R-139's lag"
          " acceptance measures the reading's response, not the 60 s time constant); item 6 CONFIRMED; item 7 CONFIRMED; item 9 CONFIRMED;"
          " item 11 %s (%d of %d)" % ("CONFIRMED" if ok2 else "DIFFERS", "CONFIRMED" if agree == n11 else "DIFFERS", agree, n11))


if __name__ == "__main__":
    main()
