#!/usr/bin/env python3
"""energy_runs.py: the energy model's design cases with the chosen array's performance ratio, and the planes the array
may face (stream a1solar, MESHSAT-1357, 29 September 2026; second issue after the independent AI check of 9f93a9fc).

PROTOTYPE DESIGN, AI arithmetic: nothing is built, ordered or measured, and nothing printed is a measurement.

The design basis of SELECTION.md is four Renogy RNG-100DB-H panels wired 2S2P (400 Wp) into board E's LT8705A stage held
at a fixed input voltage by its FBIN divider, drafted in ARRAY.md (array_calc.py's R8_DRAFT and R9_DRAFT). The energy
model's performance ratio 0.9417 is PVGIS's for a panel held at its maximum-power point; this script computes, with
array_calc.py's single-diode fits imported unchanged, what the fixed point keeps of the maximum-power energy on each
plane's own September mean day, multiplies it in, and runs the design cases, each script imported, not edited:
  * records/energy/energy_architecture.py (section 9's aggregate 4S18P, 400 Wp, 200 W window; pinned by sha256);
  * records/a1elec/energy_two_pack.py of branch fnd/a1elec at 06568798 (two packs, 4S6P base at +20 C and 4S12P lid at
    its 13.23 C basis, the entry re-rated E2; pinned by sha256), looked for under A1ELEC_ROOT (default: this
    repository's root, which holds it once fnd/a1elec is merged).
The two cases of the ratio:
  * TYPICAL (B): section 3's fit, the drafted typical set point, NOCT 45 C, a 5 m lead;
  * ADVERSE (C): the worst of the three fits (Rs 0, 0.1, 0.2 ohm) at the worse end of the set-point window (FBIN's range
    and 1 percent resistors), cells 10 K hotter than the NOCT model, a 10 m lead, AND the hotter cells' own loss of
    maximum-power energy (the lower of the model's and the maker's -0.42 %/K), which the first issue did not charge.
Planes (section 6): each plane's own PVGIS DRcalc mean-day profile (the query of the anchor file, localtime=0), scaled by
the model's own September factor found on the 40/0 anchor (which it must reproduce exactly). Before printing, the
scripts' own published design-case figures are reproduced with the unchanged ratio (exit 4 otherwise).

Third issue (stream s119, S-119, 29 September 2026): both pins moved to the scripts' second issues, which carry board A's
charger U3 at 0.979 (was 0.98, through energy_inputs.yaml) and the lid charger U3B at 0.961 (was 0.975), each from the
drawn or drafted FETs' losses (records/s117/efficiency.out); the reproduction checks of section 0 take the regenerated
figures (4S18P 90.9 Wh, was 91.0; the two-pack design case 31.0 Wh, was 31.1). The ratios of section 2 do not depend on
the chargers; nothing else changed.

Run from the repository root:  python3 v2/docs/records/a1solar/energy_runs.py > v2/docs/records/a1solar/energy_runs.out
Exit 3: a pinned script or input changed or is missing; exit 4: a reproduction check failed."""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EDIR = os.path.join(ROOT, "v2", "docs", "records", "energy")
A1ROOT = os.environ.get("A1ELEC_ROOT", ROOT)
TPDIR = os.path.join(A1ROOT, "v2", "docs", "records", "a1elec")
EA_SHA = "18851486ce4304f1d802bb1faab8284f9eeaddaf43786252c7f5236f2833199d"   # energy_architecture.py, second issue (s119; was 5cab5edf)
TP_SHA = "2c8e52c8eec8d753c0bdeac43170c8f9f330ea9c4fe1be619e17c5dc360786f3"   # energy_two_pack.py, second issue (s119; was 81694b2b, fnd/a1elec 06568798)
ANCHOR = "v2/docs/records/a1solar/inputs/pvgis-leiden-daily-profile-2005-2020.json"
ANCHOR_SHA = "4d974567cc49315dade4a63736b0d428fce9b5e645362052390c94c56fde1210"   # the file energy_inputs.yaml names (40/0)
PLANE_DIR = "v2/vendor/solar/pvgis-planes"
PLANE_PINS = {   # PVGIS 5.2 DRcalc answers filed by this stream (sources.txt lines), sha256
    "pvgis-leiden-drcalc-2005-2020-slope0-aspect0.json": "9a0d8f00d95e6f9fa74827dbe166c404ed4c853ccb50e7439cf5a9ecea430ae0",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect-45.json": "b7d6b440da4f4824604d46623d21aad1d08f615420b6f9eb74e5fc4e4263a655",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect-30.json": "cc9a757fa661095a99446aa5eb3457833c651af473e3428bca5c4fc6699830c9",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect-15.json": "b5e1a82ff47fb8d58531dab771c6e27f5a4018d060e86b13dcbca8e1b3e9b920",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect0.json": "98e37bbe72a6357b4aff9c1dbb13189ecc4f1f45e727cfe0935e458d7661ed4c",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect15.json": "eee3278ea12ba35e5b407a5696dda19604b84ae345e6e0cd6aadded758791089",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect30.json": "2893c6966aa09e1b29de857b9189e577e74f22314ee4c0103a7154d1cbde89ab",
    "pvgis-leiden-drcalc-2005-2020-slope10-aspect45.json": "bd0db3c2ba9eb9959fc90f123f046d0e9a781a8ab2c1fc6780775e67a6ad0dab",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect-45.json": "2e58094a4bd6a396ed5b30424b49969fe499c9c4506107ec5c240d874a972892",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect-30.json": "1d4d95d475d7a2bf8ad1ffc37a7f80917a25be325eb5b345d2ab8c2ccece765b",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect-15.json": "a9b322e6013d91cee7294be714b34457279d829e7946381aec3d3963803f56d8",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect0.json": "25d06a3c276487b787d389e4679b09a7e3f16b819e43aa2d8207988d689f32c6",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect15.json": "ad9d29fae471bacefdb6a2cf18158c1bab690474a40dd81f2111ca5643b5c327",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect30.json": "29371e7d3753818f9f0f17691fffc9d6ad95d66d3b182f03f844895a05790036",
    "pvgis-leiden-drcalc-2005-2020-slope20-aspect45.json": "4ef01b3b956affad574ee1657c51e016298e865564e087850961ed10099e2213",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect-45.json": "384f1ace55ad6ec004f5ebe5a4338908c84381150c7025ef59f424be0e885ac7",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect-30.json": "c8cb7f169df8b1f300bb82ea719d90468a3fccd334563b1127a81d806593ecb0",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect-15.json": "aac2471f4b28e8053d3e63b86bcd8b10c0d77f1f142a3febc82d70b09683dfb7",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect0.json": "bdfcb34881eeab567c089960e0eb3da394fa59e2481d5e4c5892406f086c8eb3",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect15.json": "2d34d7678efeba844d0522eb02d839c6cd0faf55d4f2473a72162fc477655623",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect30.json": "1485bbe5192c421ace4a964217ee6d88606dc0c61d055512c7d73495f052c5b6",
    "pvgis-leiden-drcalc-2005-2020-slope30-aspect45.json": "72b7a1e9973b6b44fccf01b834dea41bb01a217895b0cf1c4f0335cbb829c81a",
    "pvgis-leiden-drcalc-2005-2020-slope40-aspect-45.json": "692989144c4faa8b4b93e751322733510a120d662b4c0ddd2517dca7106e8d22",
    "pvgis-leiden-drcalc-2005-2020-slope40-aspect-30.json": "2c8cf091dddefcf439896ef136593b22a1ac9d0d2d06e818035f9f2a8ddfd898",
    "pvgis-leiden-drcalc-2005-2020-slope40-aspect-15.json": "bdb5c4ade8214786f497964ab594970dc30f7f3b178f19ed597e4f8468523f56",
    "pvgis-leiden-drcalc-2005-2020-slope40-aspect15.json": "e9ed1d4a7ee2b9cde0376ca85b8613ebe0ed88e3578868b43b750fe3c3cf43c0",
    "pvgis-leiden-drcalc-2005-2020-slope40-aspect30.json": "b9b229176d2657704b503b717f26cb73fa0666527c0e4c8f7c65a4e881076924",
    "pvgis-leiden-drcalc-2005-2020-slope40-aspect45.json": "86a4c3aec2e1732c93cb1f37b356196de88e2f4c5111f1bdc59aecf70e5dfcbd",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect-45.json": "1e761284638964d874cda1d7f204417a362ee2e2317574fea4dc1bffbf82da67",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect-30.json": "93df51121d614afdb488b8c9f8bc5ecd9db469b70aca3fa8bc21ce3e717445cd",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect-15.json": "7045479353d9f72603b698cc1aa28017ada806be1af04773177d808f847f958c",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect0.json": "e951be50b39a3f6b6e1be37f4585454f2427bb102e808ef0e21a0c69653679d3",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect15.json": "09ea9573ac23a72cc2470fae31226b3649fa272c119e6e40dc95481c71aea3cb",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect30.json": "0f435599888934ad4f40a220df384bf99a5c70083dadee80342893569412b001",
    "pvgis-leiden-drcalc-2005-2020-slope50-aspect45.json": "467f1f828c4582048338320ef7eb003f84df4883b0dcb88e1a83b78b62bffcc9",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect-45.json": "f253f62fba83edebfd9fd92a81ba9b45794c419b258767e09eb3c7fda10dfd2e",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect-30.json": "b7bbf8bd1f51e5ce6cc8fbd7adc985e9f142060f35319eda084a509bd190a35d",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect-15.json": "0887cd4039002562e25ac48d4616fef0dca2bfe485d6e0c486ee2c0d7a93307e",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect0.json": "fc01d0ae25a5b75149cd83721b9372c5dd7b154a5852381b9c702828bd1ba838",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect15.json": "87670e2ce8048983f25c27f9910ddf84daac5e5b22ffe66d2790d9a0d7a93833",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect30.json": "f0d7e72761526bd33d9ce98072c8be38ee319c291271b2a1c517931a2c63976f",
    "pvgis-leiden-drcalc-2005-2020-slope60-aspect45.json": "be4e746c908f11bbf6132a97f796ee7bb769849f57078cc7e68b1b87b4997757",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect-45.json": "6f338d7685278e47708aa84069ed47dd7f8578e54b3553e7ee1156f64c9310ca",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect-30.json": "a68c2dcd8751776c58570bcfca41cc77dd3b4f872ff1ebaf4d0b3251ec215383",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect-15.json": "21ae41ee803e48ca1398a189b5dbe77b6612ef14294004b7299af4b7f8419b76",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect0.json": "56b56ae16b93fe4bea0f6a60731c557d39f35e61ad5899eeb0a64a3fea285afe",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect15.json": "89b23274240d53224bd475aa8ed3c7a49965642fcb603d0af5524109c46b1240",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect30.json": "f052a0c7e14307c9b7167663030a52215235b61b1d75e254dd7b6e88295a018c",
    "pvgis-leiden-drcalc-2005-2020-slope70-aspect45.json": "bec1d2c6f180571cf52515289cafd96cec5c3f376e2eef152598e8f1ddc5bb13",
}
NS, NP = 2, 2
KEY = "REN100"
SLOPES = (0, 10, 20, 30, 40, 50, 60, 70)
ASPECTS = (-45, -30, -15, 0, 15, 30, 45)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def pinned_import():
    for path, want in ((os.path.join(EDIR, "energy_architecture.py"), EA_SHA), (os.path.join(TPDIR, "energy_two_pack.py"), TP_SHA)):
        if not os.path.exists(path) or sha(path) != want:
            sys.stderr.write("energy_runs: %s missing or changed; refusing\n" % os.path.relpath(path, A1ROOT if path.startswith(A1ROOT) else ROOT))
            sys.exit(3)
    for rel, want in [(ANCHOR, ANCHOR_SHA)] + [(PLANE_DIR + "/" + n, h) for n, h in sorted(PLANE_PINS.items())]:
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full) or sha(full) != want:
            sys.stderr.write("energy_runs: %s missing or changed; refusing\n" % rel)
            sys.exit(3)
    sys.path.insert(0, HERE)
    sys.path.insert(0, EDIR)
    sys.path.insert(0, TPDIR)
    import array_calc as AC            # noqa: E402
    import energy_architecture as EA   # noqa: E402
    import energy_two_pack as TP       # noqa: E402
    return AC, EA, TP


def plane_file(slope, aspect):
    if (slope, aspect) == (40, 0):
        return ANCHOR
    return "%s/pvgis-leiden-drcalc-2005-2020-slope%d-aspect%d.json" % (PLANE_DIR, slope, aspect)


def september(rel):
    dj = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    rows = [r for r in dj["outputs"]["daily_profile"] if r["month"] == 9]
    assert len(rows) == 24, rel
    pl = dj["inputs"]["plane"]["fixed"]
    return [r["G(i)"] for r in rows], [r["T2m"] for r in rows], (pl["slope"]["value"], pl["azimuth"]["value"])


class Ratios:
    """The fixed-point ratios for the design array on one plane's September day (array_calc's model, imported)."""

    def __init__(self, AC, G, TA):
        self.AC, self.G, self.TA = AC, G, TA
        self.c = AC.CAND[KEY]
        self.noct = self.c["noct"]
        self.fits = AC.renogy_fits()
        self.win = AC.vset_window(AC.R8_DRAFT, AC.R9_DRAFT)

    def tc(self, add):
        return [self.AC.t_cell(self.TA[h], self.G[h], self.noct + add) for h in range(24)]

    def e_mpp(self, d, tc, ns=NS, np_=NP):
        return sum(self.AC.arr_mpp(d, ns, np_, self.G[h], tc[h])[0] for h in range(24))

    def e_fix(self, d, v, tc, lead_k, ns=NS, np_=NP):
        return sum(self.AC.arr_power(d, ns, np_, v, self.G[h], tc[h], lead_k * self.AC.lead_r()) for h in range(24))

    def typical(self, v=None, lead_k=1.0, ns=NS, np_=NP):
        d = self.fits[0][1]
        t0 = self.tc(0.0)
        return self.e_fix(d, self.win[1] if v is None else v, t0, lead_k, ns, np_) / self.e_mpp(d, t0, ns, np_)

    def hot_loss(self):
        d = self.fits[0][1]
        t0, t10 = self.tc(0.0), self.tc(10.0)
        model = self.e_mpp(d, t10) / self.e_mpp(d, t0)
        maker = self.AC.hot_loss_maker(self.G, t0, t10, self.AC.coef(self.c, "gamma_p")[0])
        return model, maker, min(model, maker)

    def adverse(self):
        t10 = self.tc(10.0)
        worst = None
        for _lab, d in self.fits:
            em = self.e_mpp(d, t10)
            for v in (self.win[0], self.win[2]):
                r = self.e_fix(d, v, t10, 2.0) / em
                worst = r if worst is None else min(worst, r)
        return worst * self.hot_loss()[2], worst


def main():
    AC, EA, TP = pinned_import()
    AC.check_pins()
    o = []
    P = o.append
    d, pack, res4 = EA.load_model()
    prof = res4["months"][9]["profile"]
    d2, pack2, res4b, t2m = TP.load_model()
    pr0 = res4["pr"]
    t_basis = round(min(t2m), 2)
    ga, ta, _pl = september(ANCHOR)
    k_scale = sum(prof) / sum(ga)
    if max(abs(k_scale * ga[h] - prof[h]) for h in range(24)) > 1e-9:
        sys.stderr.write("energy_runs: the anchor file scaled does not reproduce the model's September profile; refusing\n")
        return 4

    def with_prof(r4, pr, pl_prof):
        r = dict(r4)
        r["pr"] = pr
        if pl_prof is not None:
            r["months"] = dict(r4["months"])
            r["months"][9] = dict(r4["months"][9])
            r["months"][9]["profile"] = pl_prof
        return r

    def ea_case(pr, t_c, pl_prof=None):
        ok, out = EA.meets(d, pack, with_prof(res4, pr, pl_prof), 42.8, 400, 200.0, 18, t_c)
        return ok, min(sm["lowest"] for sm, _ in out), max(sm["short_wh"] for sm, _ in out)

    def ea_tmin(pr):
        r = with_prof(res4, pr, None)
        if not EA.meets(d, pack, r, 42.8, 400, 200.0, 18, 40.0)[0]:
            return None
        lo, hi = -10.0, 40.0
        for _ in range(40):
            m = 0.5 * (lo + hi)
            if EA.meets(d, pack, r, 42.8, 400, 200.0, 18, m)[0]:
                hi = m
            else:
                lo = m
        return hi

    def tp_case(pr, wp=400, t_l=None, pl_prof=None):
        r = dict(res4b)
        r["pr"] = pr
        rs = TP.both(d2, pack2, r, prof if pl_prof is None else pl_prof, wp, 200.0, TP.v("t_base_c"),
                     t_basis if t_l is None else t_l, TP.base_cfg())
        return TP.verdict(rs), TP.fmt_run(rs), rs

    def tp_tmin(pr, wp=400):
        r = dict(res4b)
        r["pr"] = pr
        cfg = TP.base_cfg()
        if not TP.verdict(TP.both(d2, pack2, r, prof, wp, 200.0, TP.v("t_base_c"), 40.0, cfg)):
            return None
        lo, hi = -10.0, 40.0
        for _ in range(40):
            m = 0.5 * (lo + hi)
            if TP.verdict(TP.both(d2, pack2, r, prof, wp, 200.0, TP.v("t_base_c"), m, cfg)):
                hi = m
            else:
                lo = m
        return hi

    ok20, low20, _ = ea_case(pr0, 20.0)
    ok15, low15, _ = ea_case(pr0, 15.0)
    tpok, tpline, _ = tp_case(pr0)
    checks = [("energy_architecture 4S18P 400 Wp 200 W +20 C MEETS 90.9 Wh", ok20 and abs(low20 - 90.9) < 0.05),
              ("energy_architecture +15 C MEETS 26.8 Wh", ok15 and abs(low15 - 26.8) < 0.05),
              ("energy_two_pack design case MEETS, both 31.0 Wh", tpok and "both   31.0 Wh" in tpline),
              ("the 40/0 anchor scaled by %.6f reproduces the model's September profile" % k_scale, True)]
    P("THE ENERGY MODEL'S DESIGN CASES WITH THE CHOSEN ARRAY'S PERFORMANCE RATIO, AND THE PLANES (energy_runs.py, stream a1solar,")
    P("MESHSAT-1357, third issue). PROTOTYPE DESIGN: nothing built, ordered or measured. Reference-day MODEL results (September at")
    P("Leiden, PVGIS mean days), AI arithmetic, not a qualified review. Both scripts imported unchanged (sha256 pinned).")
    P("")
    P("0. REPRODUCTION OF THE PUBLISHED FIGURES WITH THE PINNED RATIO %.4f" % pr0)
    for name, good in checks:
        P("   %-78s %s" % (name, "reproduced" if good else "NOT REPRODUCED"))
    if not all(g for _n, g in checks):
        sys.stdout.write("\n".join(o) + "\n")
        sys.stderr.write("energy_runs: a reproduction check failed; refusing to print results\n")
        return 4
    P("")
    R = Ratios(AC, ga, ta)
    win = R.win
    P("1. THE RATIO FOR THE DESIGN ARRAY (%s, %dS%dP, 400 Wp) ON THE 40/0 PLANE (array_calc.py's model)" % (KEY, NS, NP))
    P("   drafted FBIN divider R8 %.0fk over R9 %.2fk: %.2f / %.2f / %.2f V (FBIN's range and 1 percent resistors)" % (
        AC.R8_DRAFT / 1e3, AC.R9_DRAFT / 1e3, win[0], win[1], win[2]))
    r_typ = R.typical()
    r_nolead = R.typical(lead_k=0.0)
    hot_md, hot_mk, hot = R.hot_loss()
    r_adv, r_adv_fix = R.adverse()
    P("   B typical (section 3's fit, %.2f V, NOCT 45 C, 5 m lead):                       %.4f" % (win[1], r_typ))
    P("     the stage's fixed point alone (no lead):                                       %.4f" % r_nolead)
    P("   C adverse, the fixed point's share (worst fit, worse window end, NOCT +10 K, 10 m): %.4f" % r_adv_fix)
    P("     the hotter cells' own MPP-energy loss: model %.4f, maker's -0.42 %%/K %.4f; charged %.4f" % (hot_md, hot_mk, hot))
    P("   C adverse, all at once (the product):                                             %.4f" % r_adv)
    vs_gen = AC.vset_window(AC.R8_R9[0], AC.R8_R9[1])
    r_4p_gen = R.typical(v=vs_gen[1], ns=1, np_=4)
    r_4p_best = max(R.typical(v=15.0 + 0.05 * k, ns=1, np_=4) for k in range(80))
    P("   the alternative 1S4P (all parallel), 5 m lead: at board E's generated %.2f V %.4f; at its best fixed point %.4f" % (vs_gen[1], r_4p_gen, r_4p_best))
    cases = [("A  energy_inputs.yaml as pinned (MPPT assumed)", pr0),
             ("B  2S2P at the drafted point, typical", pr0 * r_typ),
             ("C  2S2P, adverse, all at once", pr0 * r_adv),
             ("E  1S4P at board E's generated 17.6 V point", pr0 * r_4p_gen),
             ("F  1S4P at its best fixed point", pr0 * r_4p_best)]
    P("")
    P("2. THE PERFORMANCE RATIOS RUN (the flat plane is in section 6, on its own profile)")
    for n, pr in cases:
        P("   %-58s %.4f" % (n, pr))
    P("")
    P("3. energy_architecture.py's DESIGN CASE: 4S18P, 400 Wp, 200 W window, 42.8 W, both starts (single aggregate pack)")
    for n, pr in cases:
        a20 = ea_case(pr, 20.0)
        a15 = ea_case(pr, 15.0)
        tm = ea_tmin(pr)
        P("   %-58s +20 C %-8s lowest %6.1f Wh; +15 C %-8s lowest %6.1f Wh (unserved %5.1f); meets down to %s" % (
            n[:58], "MEETS" if a20[0] else "NOT MET", a20[1], "MEETS" if a15[0] else "NOT MET", a15[1], a15[2],
            ("%+.1f C" % tm) if tm is not None else "none up to +40 C"))
    P("")
    P("4. energy_two_pack.py's DESIGN CASE: base 4S6P +20 C, lid 4S12P at %.2f C, entry E2, 400 Wp, 200 W" % t_basis)
    for n, pr in cases:
        ok, line, _rs = tp_case(pr)
        tm = tp_tmin(pr)
        P("   %s" % n)
        P("      %s" % line)
        P("      lowest lid temperature meeting M1: %s" % (("%+.1f C" % tm) if tm is not None else "none up to +40 C"))
    P("")
    P("5. THE ARRAY AND THE TWO-PACK CASE'S LID TEMPERATURE THRESHOLD (E2, 200 W, ratio of case B)")
    t_ref = tp_tmin(pr0)
    P("   with the pinned ratio at 400 Wp the lid meets down to %+.1f C" % t_ref)
    for wp in (400, 450, 500, 600):
        tm = tp_tmin(pr0 * r_typ, wp)
        ok, _line, _ = tp_case(pr0 * r_typ, wp)
        P("   %4d Wp: %s; lid meets down to %s" % (wp, "MEETS at the basis" if ok else "NOT MET at the basis",
                                                    ("%+.1f C" % tm) if tm is not None else "none up to +40 C"))
    P("   (400 Wp is four 100 W panels; 600 Wp is 2S3P; the rows between are arithmetic on the model, not buildable steps.)")
    P("")
    P("6. THE PLANES: the two-pack design case (lid at its basis) on each plane's OWN PVGIS DRcalc September mean day, scaled")
    P("   by the model's factor %.6f found on the 40/0 anchor; each plane's fixed-point ratios computed on its own day." % k_scale)
    P("   PVGIS's other losses (0.9417: angle of incidence, spectrum, temperature at a free-standing mount) are those of the")
    P("   40/0 plane and are kept for every plane, labelled. B typical, C adverse as in section 1.")
    P("   %5s %6s %10s %7s %7s %-26s %-26s" % ("slope", "azim", "kWh/m2/d", "B ratio", "C ratio", "B: verdict, both / lid Wh", "C: verdict, both / lid Wh"))
    table = {}
    for sl in SLOPES:
        for az in ASPECTS:
            if sl == 0 and az != 0:
                continue
            rel = plane_file(sl, az)
            G, TA, pl = september(rel)
            assert (int(pl[0]), int(pl[1])) == (sl, az), (rel, pl)
            Rp = Ratios(AC, G, TA)
            rb = Rp.typical()
            rc, _rcf = Rp.adverse()
            pp = [k_scale * g for g in G]
            okb, _lb, rsb = tp_case(pr0 * rb, pl_prof=pp)
            okc, _lc, rsc = tp_case(pr0 * rc, pl_prof=pp)
            lb = min(r["low_t"] for r in rsb)
            ll_b = min(r["low_l"] for r in rsb)
            lc = min(r["low_t"] for r in rsc)
            ll_c = min(r["low_l"] for r in rsc)
            table[(sl, az)] = (okb, okc)
            P("   %5d %+6d %10.3f %7.4f %7.4f %-26s %-26s" % (
                sl, az, k_scale * sum(G) / 1000.0, rb, rc,
                "%s %6.1f / %5.1f" % ("MEETS  " if okb else "NOT MET", lb, ll_b),
                "%s %6.1f / %5.1f" % ("MEETS  " if okc else "NOT MET", lc, ll_c)))
    P("")
    P("   THE PLANES THAT MEET IN BOTH CASES, by slope (azimuth in degrees, negative east of south):")
    for sl in SLOPES:
        azs = [az for az in ASPECTS if (sl, az) in table and all(table[(sl, az)])]
        only_b = [az for az in ASPECTS if (sl, az) in table and table[(sl, az)][0] and not table[(sl, az)][1]]
        P("   slope %2d: both %-32s typical only %s" % (sl, (", ".join("%+d" % a for a in azs) or "none"),
                                                     (", ".join("%+d" % a for a in only_b) or "none")))
    flat = table[(0, 0)]
    P("   flat (slope 0): typical %s, adverse %s" % ("MEETS" if flat[0] else "NOT MET", "MEETS" if flat[1] else "NOT MET"))
    P("   The 15 degree steps of the grid are the resolution: a plane between two grid points that both meet is not itself run.")
    print("\n".join(o))
    return 0


if __name__ == "__main__":
    sys.exit(main())
