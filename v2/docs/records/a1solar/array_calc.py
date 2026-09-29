#!/usr/bin/env python3
"""array_calc.py: Option A(i)'s panel candidates, their array wirings and the fixed-voltage stage's penalty
(stream a1solar, MESHSAT-1357, 29 September 2026).

PROTOTYPE DESIGN, AI arithmetic: nothing is bought, built or measured, and nothing printed is a measurement.

What it does, from the makers' figures held under v2/vendor/solar/ (each quoted below with its file):
  1. the candidates' published figures, and the bounds taken where a maker publishes none;
  2. for every wiring of each candidate that gives about 400 Wp: the cold open-circuit voltage (cells at -20 C), the
     open-circuit voltage by the maker's 1.25 clause, the hot short-circuit current (1000 W/m2, cells at +70 C), the
     edge-of-cloud current (x 1.25, SunPower's installation clause), the entry fuse and connector current (1.25 x
     that), the reverse current into one string from the others against the module's series fuse rating, the
     maximum-power voltage over the envelope, and the stage's input current at 200 W;
  3. a single-diode model of each fully specified panel (series resistance, ideality, no shunt term) fitted to the
     maker's STC points, used to compute what board E's LT8705A stage gives when it holds the array at a FIXED input
     voltage (the FBIN loop, R8 and R9) instead of at its maximum-power point, hour by hour on the September reference
     day (PVGIS DRcalc's mean-day G(i) and T2m at Leiden, the file energy_inputs.yaml names, pinned below), with the
     cells at the NOCT model's temperature, and with the lead from the array to the case in series;
  4. the performance ratio that follows for the energy model (energy_inputs.yaml's 0.9417 times the fixed-voltage
     and lead ratio) and the flat-panel factor from the pinned PVGIS monthly file.

Deterministic, standard library only; no network. Run from the repository root:
  python3 v2/docs/records/a1solar/array_calc.py > v2/docs/records/a1solar/array_calc.out
Exit 3 when a pinned input is missing or changed."""
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

PINNED = {
    "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json": "bb2f165c642a36f0f48a9a628b259baf3108b26fb54e138070a1a24a694cd035",
    "v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json": "4d974567cc49315dade4a63736b0d428fce9b5e645362052390c94c56fde1210",
    "v2/vendor/solar/victron-bluesolar-monocrystalline-panels-datasheet-en.pdf": "ad32cb7fe0ec45ceb325b3b61ba71e60b9d9a53c6a7808404a632cb0d727e191",
    "v2/vendor/solar/renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf": "8891821cf70f4124fdb1f02e2fbc7a4a0f4102c51f33ad39c2bfa32e6b60a29f",
    "v2/vendor/solar/powerfilm-f16-7200-120w-foldable-15v-spec.pdf": "56b3722542a369a1eaf7b600c4f7eb0d13c982c5a2f7fe455b4e80b6e2aef37f",
    "v2/vendor/solar/powerfilm-120w-foldable-30v-spec.pdf": "fcea662ebd5a5bdee3932b4f8e8e092a6d70827d73f34cc6687977b645648097",
}

# HELD BACK from the public tree (publication decision of the second issue, sources.txt): SunPower's documents, read
# and quoted, pinned here by sha256; fetch_held_back.py puts them in v2/vendor/solar/held/ (ignored). This script does
# not read them; when present they must be the pinned files, when absent the figures quoted from them stand as recorded.
HELD = {
    "sunpower-spr-e-flex-100-datasheet-523809-revd.pdf": "da06e5e2d9bca625f54a756105e009950a2352e4764868853cb26921372ff605",
    "sunpower-flex-safety-installation-524958-revf.pdf": "b8ebdfb7019a399accd75e564a4a764eed565f7066dfd25b131fe65365ec6dd9",
    "sunpower-flex-safety-installation-524958-reva.pdf": "74e09944eac53e737082957be82549a46e9e0ddbea42bb9931751335314b8369",
}
T_COLD = -20.0        # the brief: cold open-circuit voltage at -20 C cells (the envelope's coldest)
T_COLD_PANEL = -40.0  # the panels' own lower operating limit (Renogy p.2, SunPower guide 5.1): REQ-016's other reading
T_HOT = 70.0          # the brief: cells to +70 C for the hot short-circuit current
K_EOC = 1.25          # SunPower 524958 Rev F section 3.0: Isc and Voc "multiplied by a factor of 1.25 when determining
                      # component voltage ratings, conductor capacities, fuse sizes" (the maker's clause for conditions
                      # above STC, the edge-of-cloud case among them); the only such factor in a held document
K_RATING = 1.25       # the brief: fuse and connector at 1.25 x the array's (edge-of-cloud) Isc; the same guide names
                      # NEC 690-8's "additional 1.25 Safety factor" (NEC itself not held)
STAGE_W = 200.0       # Option A(i)'s stage window
PR_BASE = 0.9417      # energy_inputs.yaml solar.panel.performance_ratio.typ (PVGIS PVcalc's panel losses, MPPT assumed)
VFBIN = (1.184, 1.205, 1.226)   # LT8705A 8705af p.4 "Regulation Voltage for FBIN", min / typ / max over temperature
R8_R9 = (102e3, 7.50e3)         # gen_sch_e.py:575, the FBIN divider as generated (17.6 V)
R8_DRAFT, R9_DRAFT = 232e3, 8.45e3   # the second issue's draft (section 12: an E96 pair whose worst case across the fits
                                     # and the set-point window equals the best of the candidates, 187k / 6.81k); the first issue drafted 205k / 7.50k
RES_TOL = 0.01                  # R8 and R9 at 1 percent (gen_sch_e.py:575 "1%")
LEAD_M = 5.0          # ESTIMATE: array combiner to the case's wall connector, one way
LEAD_MM2 = 4.0        # ESTIMATE: 4 mm2 (12 AWG class, the size the Renogy and SunPower leads use)
RHO_CU_20 = 0.01724   # ohm mm2 / m, annealed copper at 20 C (IEC 60028's 1/58)
ALPHA_CU = 0.00393    # per K
T_LEAD = 40.0         # ESTIMATE: the lead's temperature in the sun
Q_OVER_K = 1.602176634e-19 / 1.380649e-23


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def check_pins():
    for rel, want in PINNED.items():
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full) or sha(full) != want:
            sys.stderr.write("array_calc: pinned input %s missing or changed; refusing\n" % rel)
            sys.exit(3)
    for name, want in HELD.items():
        full = os.path.join(ROOT, "v2/vendor/solar/held", name)
        if os.path.exists(full) and sha(full) != want:
            sys.stderr.write("array_calc: held-back document %s present but not the pinned file; refusing\n" % name)
            sys.exit(3)


def vset_window(r8, r9):
    """(min, typ, max) of the FBIN loop's input point with FBIN's temperature range (8705af p.4) AND R8 and R9 at 1 %."""
    k = r8 / r9
    return (VFBIN[0] * (1.0 + k * (1.0 - RES_TOL) / (1.0 + RES_TOL)), VFBIN[1] * (1.0 + k),
            VFBIN[2] * (1.0 + k * (1.0 + RES_TOL) / (1.0 - RES_TOL)))


# ------------------------------------------------------------------------------------------------ the candidates
# Units: W, V, A; beta_voc and gamma_p in fraction per K of the STC value unless *_abs (V/K or A/K); None = not published.
CAND = {
    "VIC150": dict(name="Victron BlueSolar Mono 150W-12V (SPM041501200), rigid, the 12 V class reference",
                   doc="victron-bluesolar-monocrystalline-panels-datasheet-en.pdf, p.1 table and coefficient rows",
                   p=150.0, vmp=18.2, imp=8.25, voc=22.3, isc=8.69, cells=36,
                   gamma_p=-0.0045, beta_voc=-0.0035, alpha_isc=+0.0004, noct=None,
                   t_range=(-40, 85), size="1485 x 668 x 30 mm, rigid glass and aluminium frame", mass=11.0,
                   ip="not stated (\"sealed, waterproof, multi-functional junction box\")", conn="MC4 (PV-ST01), 900 mm",
                   vsys=1000.0, fuse=None, tech="mono c-Si"),
    "REN100": dict(name="Renogy RNG-100DB-H 100 W flexible (semi-rigid), 12 V class",
                   doc="renogy-rng-100db-h-flexible-100w-datasheet-2018.pdf, p.2 Electrical, Thermal, Mechanical",
                   p=100.0, vmp=18.9, imp=5.29, voc=22.5, isc=5.75, cells=36,
                   gamma_p=-0.0042, beta_voc=-0.0031, alpha_isc=+0.0005, noct=45.0,
                   t_range=(-40, 85), size="1219 x 549 x 2 mm, frameless flexible laminate", mass=1.9,
                   ip="junction box IP68, connectors IP67 (30 A, 1000 V)", conn="\"Solar Connectors\" (MC4 class), 12 AWG leads",
                   vsys=600.0, fuse=15.0, tech="mono c-Si"),
    "SPR100": dict(name="SunPower SPR-E-Flex-100 flexible (semi-rigid), 12 V class, 32 IBC cells",
                   doc="sunpower-spr-e-flex-100-datasheet-523809-revd.pdf and sunpower-flex-safety-installation-524958-revf.pdf Table 1",
                   p=100.0, vmp=17.1, imp=5.9, voc=21.4, isc=6.3, cells=32,
                   gamma_p=-0.0035, beta_voc_abs=-0.0589, alpha_isc_abs=+0.0026, noct=None,
                   t_range=(-40, 85), size="1153 x 556 x 20 mm with the box, 2 mm without", mass=2.0,
                   ip="junction box IP67 (guide 5.2)", conn="Tyco PV4-S, 4 mm2, 450 mm",
                   vsys=45.0, fuse=15.0, tech="mono c-Si (IBC)"),
    "PF120L": dict(name="PowerFilm 120W Foldable F16-7200 (15.4 V), amorphous, military tested",
                   doc="powerfilm-f16-7200-120w-foldable-15v-spec.pdf, p.2",
                   p=120.0, vmp=15.4, imp=7.2, voc=21.9, isc=9.1, cells=None,
                   gamma_p=-0.0020, beta_voc=-0.0030, alpha_isc=+0.00109, noct=None,
                   t_range=None, size="2197 x 1397 mm unfolded, 368 x 356 x 76 mm folded", mass=2.9,
                   ip="not stated; \"Not designed for use in the rain\"", conn="Aptiv Weather Pack",
                   vsys=None, fuse=None, tech="amorphous Si"),
    "PF120H": dict(name="PowerFilm 120W Foldable (30V) F32-3600 as printed (F16-3600 on the maker's page), amorphous",
                   doc="powerfilm-120w-foldable-30v-spec.pdf, p.2",
                   p=120.0, vmp=30.8, imp=3.6, voc=43.7, isc=4.6, cells=None,
                   gamma_p=-0.0020, beta_voc=-0.0030, alpha_isc=+0.00109, noct=None,
                   t_range=None, size="2197 x 1397 mm unfolded, 368 x 356 x 76 mm folded", mass=2.9,
                   ip="not stated; \"Not designed for use in the rain\"", conn="Aptiv Metri-Pack",
                   vsys=None, fuse=None, tech="amorphous Si"),
    "BLU420": dict(name="BLUETTI PV420 one-piece folding, 420 W",
                   doc="bluetti-pv420-product-page-2026-09-29.md (the maker's page, transcribed)",
                   p=420.0, vmp=None, imp=None, voc=44.3, isc=12.2, cells=None,
                   gamma_p=None, beta_voc=None, alpha_isc=None, noct=None,
                   t_range=(-10, 65), size="2675 x 975 mm unfolded, 975 x 660 x 45 mm folded", mass=14.0,
                   ip="IP65", conn="MC4", vsys=None, fuse=None, tech="mono c-Si"),
}
# The bound for a coefficient a maker does not publish: the worst value among the monocrystalline documents held
# (Victron -0.35 %/K on Voc and -0.45 %/K on power; Renogy +0.05 %/K on Isc, the largest rise). A bound, named as one.
BOUND = dict(beta_voc=-0.0035, gamma_p=-0.0045, alpha_isc=+0.0005)
NOCT_ASSUMED = 47.0   # INFERRED for panels whose maker publishes none: Renogy's 45 +- 2 C at its upper end


def coef(c, key):
    """(value as a fraction per K of the STC figure, kind) for beta_voc, alpha_isc, gamma_p."""
    base = {"beta_voc": "voc", "alpha_isc": "isc", "gamma_p": "p"}[key]
    if c.get(key) is not None:
        return c[key], "MAKER"
    if c.get(key + "_abs") is not None:
        return c[key + "_abs"] / c[base], "MAKER (absolute, as a fraction of the STC value)"
    return BOUND[key], "BOUND (worst held mono c-Si value; not published by the maker)"


def voc_at(c, t):
    b, _k = coef(c, "beta_voc")
    return c["voc"] * (1.0 + b * (t - 25.0))


def isc_at(c, t, g=1000.0):
    a, _k = coef(c, "alpha_isc")
    return c["isc"] * g / 1000.0 * (1.0 + a * (t - 25.0))


# ------------------------------------------------------------------------------------------- the single-diode model
class Diode:
    """I = Iph - I0 (exp((V + I Rs) / A) - 1), no shunt term, fitted to the maker's Isc, Voc, Vmp, Imp at STC with
    dP/dV = 0 at (Vmp, Imp). A = n Ns k T / q for the module. Temperature: Voc(T) by the maker's coefficient (I0 follows),
    Isc(T) by the maker's coefficient, A proportional to absolute temperature, Rs constant. Irradiance: Iph in
    proportion to G."""

    def __init__(self, c):
        self.c = c
        isc, voc, vmp, imp = c["isc"], c["voc"], c["vmp"], c["imp"]

        def rs_of(a):
            i0 = isc / (math.exp(voc / a) - 1.0)
            return (a * math.log((isc - imp) / i0 + 1.0) - vmp) / imp, i0

        def f(a):
            rs, i0 = rs_of(a)
            g = i0 / a * math.exp((vmp + imp * rs) / a)
            return imp - vmp * g / (1.0 + g * rs)

        # scan A for a sign change of f with Rs >= 0
        lo, hi, prev = None, None, None
        grid = [voc / 200.0 * k for k in range(1, 200)]
        for a in grid:
            try:
                rs, _i0 = rs_of(a)
                val = f(a)
            except (OverflowError, ValueError, ZeroDivisionError):
                continue
            if rs < 0:
                prev = None
                continue
            if prev is not None and (prev[1] > 0) != (val > 0):
                lo, hi = prev[0], a
                break
            prev = (a, val)
        self.fit_note = "exact fit: dP/dV = 0 at the maker's (Vmp, Imp), Rs >= 0"
        if lo is None:
            # no root with Rs >= 0: Rs = 0 and A from the Voc and Vmp points only
            self.rs = 0.0
            a_lo, a_hi = 0.01 * voc, 1.0 * voc
            for _ in range(200):
                a = 0.5 * (a_lo + a_hi)
                i0 = isc / (math.exp(voc / a) - 1.0)
                imp_m = isc - i0 * (math.exp(vmp / a) - 1.0)
                if imp_m > imp:
                    a_lo = a
                else:
                    a_hi = a
            self.a_ref = 0.5 * (a_lo + a_hi)
            self.fit_note = "fallback: Rs = 0, A through (Vmp, Imp); dP/dV = 0 not at the maker's point"
        else:
            for _ in range(200):
                m = 0.5 * (lo + hi)
                if (f(lo) > 0) == (f(m) > 0):
                    lo = m
                else:
                    hi = m
            self.a_ref = 0.5 * (lo + hi)
            self.rs, _ = rs_of(self.a_ref)

    def params(self, g, t):
        a = self.a_ref * (t + 273.15) / 298.15
        voc_t = voc_at(self.c, t)
        isc_1000 = isc_at(self.c, t, 1000.0)
        i0 = isc_1000 / (math.exp(voc_t / a) - 1.0)
        iph = isc_at(self.c, t, g)
        return iph, i0, a

    def current(self, v, g, t, r_extra=0.0):
        """Current at terminal voltage v (after r_extra in series); 0 if v is above the open-circuit point."""
        iph, i0, a = self.params(g, t)
        rs = self.rs + r_extra
        lo, hi = 0.0, iph
        if iph - i0 * (math.exp(v / a) - 1.0) <= 0.0:
            return 0.0
        for _ in range(80):
            m = 0.5 * (lo + hi)
            # residual r(I) = Iph - I0 (exp((v + I rs)/a) - 1) - I, decreasing in I
            r = iph - i0 * (math.exp((v + m * rs) / a) - 1.0) - m
            if r > 0:
                lo = m
            else:
                hi = m
        return 0.5 * (lo + hi)

    def mpp(self, g, t, r_extra=0.0):
        iph, i0, a = self.params(g, t)
        voc = a * math.log(iph / i0 + 1.0)
        lo, hi = 0.0, voc
        for _ in range(80):     # golden-section search on P(V)
            m1 = lo + (hi - lo) * 0.381966
            m2 = lo + (hi - lo) * 0.618034
            if m1 * self.current(m1, g, t, r_extra) < m2 * self.current(m2, g, t, r_extra):
                lo = m1
            else:
                hi = m2
        v = 0.5 * (lo + hi)
        return v, self.current(v, g, t, r_extra), voc


class DiodeVmp(Diode):
    """The fit-sensitivity alternative: Rs = 0 and A chosen so that the model's maximum-power VOLTAGE at STC equals the
    maker's VMPP (its IMPP and Pmax then differ from the maker's); used only to show how far the fixed-point ratio
    depends on the fit."""

    def __init__(self, c):
        self.c = c
        self.rs = 0.0
        lo, hi = 0.02 * c["voc"], 0.5 * c["voc"]
        for _ in range(60):
            self.a_ref = 0.5 * (lo + hi)
            v, _i, _voc = self.mpp(1000.0, 25.0)
            if v > c["vmp"]:
                lo = self.a_ref      # a larger A lowers the MPP voltage
            else:
                hi = self.a_ref
        self.a_ref = 0.5 * (lo + hi)
        self.fit_note = "sensitivity: Rs = 0, A so that the model's MPP voltage equals the maker's VMPP"


class DiodeRs(Diode):
    """The Rs > 0 bracket (check item 2): a FIXED series resistance and A chosen so that the curve passes through the
    maker's (VMPP, IMPP) with the maker's Voc and Isc; its maximum then sits near, not at, the maker's point."""

    def __init__(self, c, rs):
        self.c = c
        self.rs = rs
        isc, voc, vmp, imp = c["isc"], c["voc"], c["vmp"], c["imp"]
        lo, hi = 0.02 * voc, 0.5 * voc
        for _ in range(100):
            m = 0.5 * (lo + hi)
            i0 = isc / (math.exp(voc / m) - 1.0)
            if isc - i0 * (math.exp((vmp + imp * rs) / m) - 1.0) - imp > 0:
                lo = m
            else:
                hi = m
        self.a_ref = 0.5 * (lo + hi)
        self.fit_note = "bracket: Rs = %.2f ohm fixed, A through (VMPP, IMPP)" % rs


def renogy_fits():
    c = CAND["REN100"]
    return [("Rs 0 (section 3)", Diode(c)), ("Rs 0.1", DiodeRs(c, 0.1)), ("Rs 0.2", DiodeRs(c, 0.2))]


def hot_loss_maker(G, tc, tc_hot, gamma):
    """The panel's own Pmax loss at hotter cells by the maker's coefficient, irradiance-weighted over the day."""
    num = sum(G[h] * (1.0 + gamma * (tc_hot[h] - 25.0)) for h in range(24))
    den = sum(G[h] * (1.0 + gamma * (tc[h] - 25.0)) for h in range(24))
    return num / den


def arr_power(d, ns, np_, v_set, g, t, r_lead):
    """Array of ns in series x np_ in parallel of identical panels, held at v_set at the board (after the lead). The
    lead's resistance is shared: per panel it is r_lead * np_ / ns in series with each panel at 1/ns of the voltage."""
    if g <= 0.0:
        return 0.0
    v_panel = v_set / ns
    i = d.current(v_panel, g, t, r_lead * np_ / ns)
    return v_set * i * np_


def arr_mpp(d, ns, np_, g, t):
    if g <= 0.0:
        return 0.0, 0.0
    v, i, _voc = d.mpp(g, t)
    return v * i * ns * np_, v * ns


def lead_r():
    return 2.0 * LEAD_M * RHO_CU_20 / LEAD_MM2 * (1.0 + ALPHA_CU * (T_LEAD - 20.0))


def t_cell(ta, g, noct):
    return ta + (noct - 20.0) / 800.0 * g


def wirings(c):
    n_opts = sorted(set([max(1, int(round(400.0 / c["p"]))), max(1, int(math.ceil(400.0 / c["p"])))]))
    if c["p"] < 150 and int(round(400.0 / c["p"])) * c["p"] < 400:
        n_opts = sorted(set(n_opts + [n_opts[-1] + 1]))
    out = []
    for n in n_opts:
        for ns in range(1, n + 1):
            if n % ns == 0:
                out.append((ns, n // ns))
    return out


def main():
    check_pins()
    o = []
    P = o.append
    dr = json.load(open(os.path.join(ROOT, "v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json"), encoding="utf-8"))
    prof = {}
    for mo in (6, 9, 12):
        rows = [r for r in dr["outputs"]["daily_profile"] if r["month"] == mo]
        prof[mo] = ([r["G(i)"] for r in rows], [r["T2m"] for r in rows])
    monthly = json.load(open(os.path.join(ROOT, "v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json"), encoding="utf-8"))

    P("OPTION A(i): PANEL CANDIDATES, ARRAY WIRINGS AND THE FIXED-VOLTAGE STAGE (array_calc.py, stream a1solar, MESHSAT-1357).")
    P("PROTOTYPE DESIGN: nothing bought, built or measured. AI arithmetic on the makers' published figures; not a qualified review.")
    P("")
    P("0. CONSTANTS")
    P("   cold cells %.0f C; hot cells %+.0f C at 1000 W/m2; edge-of-cloud factor %.2f (SunPower 524958 Rev F 3.0); rating factor %.2f" % (T_COLD, T_HOT, K_EOC, K_RATING))
    P("   stage window %.0f W; energy model's performance ratio %.4f (MPPT assumed); LT8705A FBIN %.3f / %.3f / %.3f V (8705af p.4)" % ((STAGE_W, PR_BASE) + VFBIN))
    vs_gen = tuple(vf * (1.0 + R8_R9[0] / R8_R9[1]) for vf in VFBIN)
    P("   board E as generated: R8 102k over R9 7.50k holds the input at %.2f / %.2f / %.2f V (min / typ / max)" % vs_gen)
    P("   lead ESTIMATE: %.0f m each way of %.0f mm2 copper at %.0f C = %.4f ohm loop" % (LEAD_M, LEAD_MM2, T_LEAD, lead_r()))
    P("   coefficient bound where unpublished: Voc %.2f %%/K, Pmax %.2f %%/K, Isc %+.2f %%/K (worst held mono c-Si values)" % (
        100 * BOUND["beta_voc"], 100 * BOUND["gamma_p"], 100 * BOUND["alpha_isc"]))
    P("")
    P("1. THE CANDIDATES (maker's STC figures; coefficient kind in brackets)")
    for key, c in CAND.items():
        P("   %s  %s" % (key, c["name"]))
        P("      document: v2/vendor/solar/%s" % c["doc"])
        P("      Pmax %.0f W, Vmp %s, Imp %s, Voc %.2f V, Isc %.2f A, cells %s, %s" % (
            c["p"], "%.2f V" % c["vmp"] if c["vmp"] else "not published", "%.2f A" % c["imp"] if c["imp"] else "not published",
            c["voc"], c["isc"], c["cells"] if c["cells"] else "not published", c["tech"]))
        for k in ("beta_voc", "alpha_isc", "gamma_p"):
            val, kind = coef(c, k)
            P("      %-9s %+.3f %%/K  [%s]" % (k, 100 * val, kind))
        P("      operating range %s; NOCT %s; %s; %.1f kg; %s; %s; max system voltage %s; series fuse %s" % (
            "%d to %+d C" % c["t_range"] if c["t_range"] else "not published",
            "%.0f C" % c["noct"] if c["noct"] else "not published", c["size"], c["mass"], c["ip"], c["conn"],
            "%.0f V" % c["vsys"] if c["vsys"] else "not published", "%.0f A" % c["fuse"] if c["fuse"] else "not published"))
        P("      Wp per kg %.1f" % (c["p"] / c["mass"]))
    P("")
    P("2. THE WIRINGS THAT GIVE ABOUT 400 Wp")
    P("   Voc cold = Ns x Voc at %.0f C cells; Voc x1.25 = the maker's clause on the STC figure; V rating = the larger." % T_COLD)
    P("   Isc hot = Np x Isc at %+.0f C and 1000 W/m2; Isc eoc = x%.2f; I rating (fuse, connector) = x%.2f of Isc eoc." % (T_HOT, K_EOC, K_RATING))
    P("   Backfeed = (Np - 1) x Isc eoc into one faulted string, against the module's series fuse rating.")
    P("   %-7s %-5s %6s %9s %9s %9s %8s %8s %9s %10s %12s" % ("panel", "NsxNp", "Wp", "Voc cold", "Voc x1.25", "V rating", "Isc hot", "Isc eoc", "I rating", "backfeed", "vs fuse"))
    rows2 = {}
    for key, c in CAND.items():
        for ns, np_ in wirings(c):
            wp = c["p"] * ns * np_
            vcold = ns * voc_at(c, T_COLD)
            v125 = ns * c["voc"] * K_EOC
            vr = max(vcold, v125)
            ihot = np_ * isc_at(c, T_HOT)
            ieoc = K_EOC * ihot
            irat = K_RATING * ieoc
            back = (np_ - 1) * K_EOC * isc_at(c, T_HOT)
            if np_ == 1:
                vsf = "one string"
            elif c["fuse"] is None:
                vsf = "fuse n/p"
            else:
                vsf = "UNDER %.0f A" % c["fuse"] if back <= c["fuse"] else "OVER %.0f A" % c["fuse"]
            rows2[(key, ns, np_)] = dict(wp=wp, vcold=vcold, v125=v125, vr=vr, ihot=ihot, ieoc=ieoc, irat=irat, back=back)
            P("   %-7s %dx%-3d %6.0f %9.2f %9.2f %9.2f %8.2f %8.2f %9.2f %10.2f %12s" % (key, ns, np_, wp, vcold, v125, vr, ihot, ieoc, irat, back, vsf))
    P("")
    P("   Limits the wirings meet or break (each named with its source):")
    P("   - LT8705A VIN 80 V absolute maximum and 5.5 to 80 V operating (8705af pp.2, 3); SW1 81 V.")
    P("   - board E as generated on PV_P: Q3 BSC028N06NS 60 V, C11/C12 35 V polymer, C13/C14 50 V, D4 SMCJ28A 28 V standoff")
    P("     (gen_sch_e.py:478-480, 495); REQ-016: 25 V cold Voc, 100 W, F2 and J_SOLAR 10 A.")
    P("   - module maximum system voltage (Victron 1000 V, Renogy 600 V, SunPower 45 V with its note that the flex panels are")
    P("     not UL or IEC certified; PowerFilm and BLUETTI do not publish one).")
    P("   - 60 V: the coordinator's safety-extra-low-voltage ceiling (README of this folder); the standard behind it is not held.")
    P("")
    P("3. THE SINGLE-DIODE FITS (no shunt term; A = n Ns kT/q of the module)")
    fits = {}
    for key, c in CAND.items():
        if c["vmp"] is None:
            P("   %-7s not fitted: the maker publishes no Vmp or Imp" % key)
            continue
        if c["tech"].startswith("amorphous"):
            P("   %-7s not fitted: its fill factor %.3f comes from shunt conduction that a no-shunt model assigns to ideality, which" % (
                key, c["vmp"] * c["imp"] / (c["voc"] * c["isc"])))
            P("           makes the model's voltage fall steeply at low light (a-Si's makers state the opposite); no fixed-voltage")
            P("           figure is printed for it rather than a figure of the model's own making")
            continue
        d = Diode(c)
        fits[key] = d
        v, i, voc = d.mpp(1000.0, 25.0)
        v70, i70, _ = d.mpp(1000.0, 70.0)
        gam = (v70 * i70 / (v * i) - 1.0) / 45.0
        gm, gk = coef(c, "gamma_p")
        n_eff = d.a_ref / ((c["cells"] or 1) * 298.15 / Q_OVER_K) if c["cells"] else float("nan")
        P("   %-7s A %.4f V, Rs %.4f ohm (%s); model at STC: Pmp %.2f W at %.2f V (maker %.1f W at %.2f V), Voc %.2f V" % (
            key, d.a_ref, d.rs, d.fit_note, v * i, v, c["p"], c["vmp"], voc))
        P("           implied Pmax coefficient %+.3f %%/K against the maker's %+.3f %%/K [%s]; ideality per cell %s" % (
            100 * gam, 100 * gm, gk, "%.2f" % n_eff if c["cells"] else "n/a (cells not published)"))
    P("   The model's temperature slope of Pmax differs from the makers' (milder for Victron and Renogy, steeper for SunPower):")
    P("   its absolute losses are used only for the hotter cells' loss of section 6, charged at the lower of the model's and")
    P("   the maker's figure; elsewhere only the RATIO of the fixed-voltage power to the maximum-power power at the same cells.")
    P("")
    P("4. THE MAXIMUM-POWER VOLTAGE OVER THE ENVELOPE (model, per wiring), V")
    P("   %-7s %-5s %11s %11s %11s %11s %11s %11s" % ("panel", "NsxNp", "1000/-20C", "1000/25C", "1000/70C", "200/25C", "200/70C", "100/10C"))
    vmpp = {}
    for key, d in fits.items():
        for ns, np_ in wirings(CAND[key]):
            pts = [(1000, -20), (1000, 25), (1000, 70), (200, 25), (200, 70), (100, 10)]
            vv = [d.mpp(g, t)[0] * ns for g, t in pts]
            vmpp[(key, ns, np_)] = vv
            P("   %-7s %dx%-3d " % (key, ns, np_) + " ".join("%11.2f" % x for x in vv))
    P("")
    P("5. THE STAGE AT 200 W (input current at the fixed input voltage, and at the hot maximum-power voltage)")
    for key, d in fits.items():
        for ns, np_ in wirings(CAND[key]):
            vv = vmpp[(key, ns, np_)]
            P("   %-7s %dx%-3d  200 W at the hot Vmpp %.2f V = %.2f A; the array's own maximum at 1000 W/m2 and 70 C: %.1f W" % (
                key, ns, np_, vv[2], STAGE_W / vv[2], arr_mpp(d, ns, np_, 1000.0, 70.0)[0]))
    P("")
    P("6. THE FIXED INPUT VOLTAGE ON THE SEPTEMBER REFERENCE DAY (PVGIS DRcalc mean day G(i), T2m; NOCT cell model)")
    P("   ratio = energy delivered at the board with the stage holding the array at V_set, through the lead, over the energy")
    P("   the array gives at its maximum-power point with no lead, the same cells and hours. The energy model's 0.9417")
    P("   already carries the MPPT panel's temperature, spectral and angle losses; the ratio multiplies it.")
    rl = lead_r()
    res6 = {}
    for key, d in fits.items():
        c = CAND[key]
        noct = c["noct"] or NOCT_ASSUMED
        for ns, np_ in wirings(c):
            G, TA = prof[9]
            e_mpp = 0.0
            tc = [t_cell(TA[h], G[h], noct) for h in range(24)]
            mpps = [arr_mpp(d, ns, np_, G[h], tc[h])[0] for h in range(24)]
            e_mpp = sum(mpps)
            best = None
            v_lo = 0.55 * ns * c["vmp"]
            v_hi = 1.05 * ns * c["vmp"]
            steps = 200
            for k in range(steps + 1):
                vs = v_lo + (v_hi - v_lo) * k / steps
                e = sum(arr_power(d, ns, np_, vs, G[h], tc[h], rl) for h in range(24))
                if best is None or e > best[1]:
                    best = (vs, e)
            vs_opt = best[0]
            e_opt = best[1]
            e_opt_nolead = sum(arr_power(d, ns, np_, vs_opt, G[h], tc[h], 0.0) for h in range(24))
            gen = [ns * x for x in vs_gen] if ns == 1 else [ns * x for x in vs_gen]
            e_gen = [sum(arr_power(d, ns, np_, vg, G[h], tc[h], rl) for h in range(24)) for vg in gen]
            # the set point's own tolerance: FBIN's range and R8, R9 at 1 percent (the drafted divider's relative window)
            wmin, wtyp, wmax = vset_window(R8_DRAFT, R9_DRAFT)
            e_tol = [sum(arr_power(d, ns, np_, vs_opt * wf / wtyp, G[h], tc[h], rl) for h in range(24)) for wf in (wmin, wmax)]
            # hotter mounting: NOCT + 10 K (ESTIMATE, a flexible panel on an insulating surface), same set point
            tc_h = [t_cell(TA[h], G[h], noct + 10.0) for h in range(24)]
            e_mpp_h = sum(arr_mpp(d, ns, np_, G[h], tc_h[h])[0] for h in range(24))
            e_h = sum(arr_power(d, ns, np_, vs_opt, G[h], tc_h[h], rl) for h in range(24))
            # both at once: the FBIN extreme that is worse and the hotter mounting, with a 10 m lead (ESTIMATE)
            e_hw = min(sum(arr_power(d, ns, np_, vs_opt * wf / wtyp, G[h], tc_h[h], 2.0 * rl) for h in range(24)) for wf in (wmin, wmax))
            gam, _gk = coef(c, "gamma_p")
            hot_mk = hot_loss_maker(G, tc, tc_h, gam)
            hot_md = e_mpp_h / e_mpp
            hot = min(hot_mk, hot_md)
            res6[(key, ns, np_)] = dict(vs_opt=vs_opt, r_opt=e_opt / e_mpp, r_nolead=e_opt_nolead / e_mpp,
                                        r_gen=[x / e_mpp for x in e_gen], r_tol=[x / e_mpp for x in e_tol],
                                        r_hot=e_h / e_mpp_h, r_worst=e_hw / e_mpp_h * hot, hot=hot, e_mpp=e_mpp, noct=noct, tc_max=max(tc))
            P("   %-7s %dx%-3d NOCT %.0f C (cells to %.1f C): best V_set %.2f V -> ratio %.4f (%.4f without the lead); window min/max %.4f / %.4f;" % (
                key, ns, np_, noct, max(tc), vs_opt, e_opt / e_mpp, e_opt_nolead / e_mpp, e_tol[0] / e_mpp, e_tol[1] / e_mpp))
            P("                 board E as generated (%.2f / %.2f / %.2f V x Ns): %.4f / %.4f / %.4f; NOCT +10 K at the same V_set: %.4f; MPP day %.0f Wh" % (
                vs_gen[0], vs_gen[1], vs_gen[2], e_gen[0] / e_mpp, e_gen[1] / e_mpp, e_gen[2] / e_mpp, e_h / e_mpp_h, e_mpp))
            P("                 the hotter cells' own MPP loss (NOCT +10 K over NOCT): model %.4f, maker's Pmax coefficient %.4f; charged %.4f" % (hot_md, hot_mk, hot))
            P("                 all at once (the window's worse extreme, NOCT +10 K, a 10 m lead, and that loss charged): %.4f" % (e_hw / e_mpp_h * hot))
    P("")
    P("7. THE SAME SET POINTS IN JUNE AND DECEMBER (the September optimum kept; ratio as in section 6)")
    for key, d in fits.items():
        c = CAND[key]
        noct = c["noct"] or NOCT_ASSUMED
        for ns, np_ in wirings(c):
            vs = res6[(key, ns, np_)]["vs_opt"]
            parts = []
            for mo in (6, 12):
                G, TA = prof[mo]
                tc = [t_cell(TA[h], G[h], noct) for h in range(24)]
                e_m = sum(arr_mpp(d, ns, np_, G[h], tc[h])[0] for h in range(24))
                e_f = sum(arr_power(d, ns, np_, vs, G[h], tc[h], rl) for h in range(24))
                parts.append("%s %.4f" % ({6: "June", 12: "December"}[mo], e_f / e_m))
            P("   %-7s %dx%-3d V_set %.2f V: %s" % (key, ns, np_, vs, ", ".join(parts)))
    P("")
    P("8. THE RATIO AT FIXED IRRADIANCE LEVELS (the mean day averages clear and cloudy hours; a real day is a mix)")
    for key in ("REN100", "SPR100"):
        d = fits[key]
        for ns, np_ in wirings(CAND[key]):
            vs = res6[(key, ns, np_)]["vs_opt"]
            cells = []
            for g in (100, 200, 400, 600, 800, 1000):
                t = t_cell(14.5, g, CAND[key]["noct"] or NOCT_ASSUMED)
                pm = arr_mpp(d, ns, np_, g, t)[0]
                pf = arr_power(d, ns, np_, vs, g, t, rl)
                cells.append("%d: %.3f" % (g, pf / pm))
            P("   %-7s %dx%-3d V_set %.2f V, air 14.5 C: %s" % (key, ns, np_, vs, "; ".join(cells)))
    P("")
    P("9. THE PLANE: a panel laid flat against the energy model's 40 degree south plane (pinned PVGIS monthly, 2015 to 2020)")
    for mo in (6, 9, 12):
        rs = [r for r in monthly["outputs"]["monthly"] if r["month"] == mo]
        hh = sum(r["H(h)_m"] for r in rs) / len(rs)
        ho = sum(r["H(i_opt)_m"] for r in rs) / len(rs)
        P("   month %2d: horizontal %.2f, 40 degrees %.2f kWh/m2 a month; flat / inclined = %.4f" % (mo, hh, ho, hh / ho))
    P("")
    P("10. THE PERFORMANCE RATIO FOR THE ENERGY MODEL (September, the design month)")
    for key in fits:
        for ns, np_ in wirings(CAND[key]):
            r = res6[(key, ns, np_)]
            P("   %-7s %dx%-3d at its best V_set %.2f V: %.4f x %.4f = %.4f (all at once %.4f); at board E's 17.6 V point x Ns: %.4f" % (
                key, ns, np_, r["vs_opt"], PR_BASE, r["r_opt"], PR_BASE * r["r_opt"], PR_BASE * r["r_worst"], PR_BASE * r["r_gen"][1]))
    P("")
    P("11. FIT SENSITIVITY FOR THE DESIGN BASIS (REN100): the September ratio under the second fit of DiodeVmp and the")
    P("    Rs > 0 bracket of section 12 (the fits with Rs 0.1 and 0.2 ohm)")
    G, TA = prof[9]
    for label, dd in (("section 3's fit", fits["REN100"]), ("DiodeVmp", DiodeVmp(CAND["REN100"])),
                      ("Rs 0.1", DiodeRs(CAND["REN100"], 0.1)), ("Rs 0.2", DiodeRs(CAND["REN100"], 0.2))):
        v, i, voc = dd.mpp(1000.0, 25.0)
        tc = [t_cell(TA[h], G[h], CAND["REN100"]["noct"]) for h in range(24)]
        cells = []
        for ns, np_, vset in ((2, 2, 34.14), (2, 2, vset_window(R8_DRAFT, R9_DRAFT)[1]), (1, 4, vs_gen[1])):
            e_m = sum(arr_mpp(dd, ns, np_, G[h], tc[h])[0] for h in range(24))
            e_f = sum(arr_power(dd, ns, np_, vset, G[h], tc[h], rl) for h in range(24))
            best = max(sum(arr_power(dd, ns, np_, ns * (15.0 + 0.05 * k), G[h], tc[h], rl) for h in range(24)) for k in range(80))
            cells.append("%dx%d at %.2f V %.4f (best %.4f)" % (ns, np_, vset, e_f / e_m, best / e_m))
        P("   %-16s A %.4f V, Rs %.4f ohm, STC MPP %.2f W at %.2f V: %s" % (label, dd.a_ref, dd.rs, v * i, v, "; ".join(cells)))
    P("")
    P("12. THE FBIN DIVIDER FOR 2S2P: E96 pairs, their set-point window (FBIN's range and 1 percent resistors), and the")
    P("    ratio across the three fits (Rs 0, 0.1, 0.2 ohm) at the window's three points; the draft is the best worst case")
    tcs = [t_cell(TA[h], G[h], CAND["REN100"]["noct"]) for h in range(24)]
    rf = renogy_fits()
    emp = [sum(arr_mpp(dd, 2, 2, G[h], tcs[h])[0] for h in range(24)) for _l, dd in rf]
    for lab, dd in rf:
        v, i, _voc = dd.mpp(1000.0, 25.0)
        P("   fit %-17s A %.4f V (ideality %.2f a cell), Rs %.2f ohm, STC maximum %.2f W at %.2f V" % (
            lab, dd.a_ref, dd.a_ref / (36 * 298.15 / Q_OVER_K), dd.rs, v * i, v))
    best = None
    for r8, r9 in ((205e3, 7.50e3), (210e3, 7.50e3), (232e3, 8.45e3), (187e3, 6.81e3), (165e3, 5.90e3), (200e3, 7.15e3)):
        win = vset_window(r8, r9)
        grid = []
        for vs in win:
            grid.append([sum(arr_power(dd, 2, 2, vs, G[h], tcs[h], rl) for h in range(24)) / emp[j] for j, (_l, dd) in enumerate(rf)])
        worst = min(min(g) for g in grid)
        P("   R8 %5.0fk R9 %.2fk: %.2f / %.2f / %.2f V; at the typical point %.4f to %.4f across the fits; worst in the window %.4f%s" % (
            r8 / 1e3, r9 / 1e3, win[0], win[1], win[2], min(grid[1]), max(grid[1]), worst,
            "   <- the draft" if (r8, r9) == (R8_DRAFT, R9_DRAFT) else ""))
    P("   (a set point between the E96 steps, about 34.6 V, is the fits' common optimum; the E96 pairs give 34.14 or 34.29 V")
    P("    or about 34.9 V, and the window of about +-3.7 percent dominates the choice)")
    P("")
    P("13. REQ-016'S 'COLDEST OPERATING TEMPERATURE': the envelope's -20 C cells (pcb_envelope.yaml in_use min, used above)")
    P("    against the panels' own lower limit, -40 C (Renogy p.2; SunPower guide 5.1; Victron p.1), open-circuit V per wiring")
    for key, ns, np_ in (("REN100", 2, 2), ("REN100", 1, 4), ("SPR100", 1, 4), ("PF120L", 1, 4), ("VIC150", 1, 3), ("BLU420", 1, 1)):
        c = CAND[key]
        P("   %-7s %dx%-3d at -20 C %6.2f V; at -40 C %6.2f V; 1.25 x STC %6.2f V" % (
            key, ns, np_, ns * voc_at(c, T_COLD), ns * voc_at(c, T_COLD_PANEL), ns * c["voc"] * K_EOC))
    print("\n".join(o))


if __name__ == "__main__":
    main()
