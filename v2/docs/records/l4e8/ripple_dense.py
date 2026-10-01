#!/usr/bin/env python3
"""ripple_dense.py: layer 4 task L4-E8 (MESHSAT-1357, 1 October 2026). Board A's VBUS20 bulk bank re-sized so that finding B-4
of v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md closes (every EEHZK1V331P at most its 2.8 A rating at the 2:1 ESR spread at
R11 8 mOhm). Each capacitor's current is DERIVED from the node's topology as gen_sch_a.py draws it, the operating conditions
and the makers' equations; the figures of the generator's lost dense analysis (drafts/scripts/ripple_dense.py of the third
fix-up of 26 September 2026, in neither this tree nor its history) are a CONSISTENCY CHECK, reconciled where they differ, never
a target a constant is tuned to.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry, rendered page or
record of L4-E4 to L4-E7 is edited (apply_gen_sch_a_bank.py beside this file is a draft for board A's generator owner). Labels:
MAKER (document, revision, page), NETLIST (board A's committed netlist), GENERATOR (gen_sch_a.py, parsed), RECORD (a figure or
band the generator's own record carries: gen_sch_a.py's comments and v2/docs/records/r4a/r4-decisions.md), INFERRED (a method
stated beside it), ASSUMPTION (a figure no document gives), SESSION (a choice this record makes), MODELED, INCONCLUSIVE.

THE DERIVATION: each converter's switch current built from its topology (the front end's boost output current, the inductor
current during 1 - D, SNVSAI1D Equation 19's waveform, or its buck triangle; the charger's buck input current, the inductor
current during D, SLUSE66A Equation 4's waveform; each with its triangular ripple from L, fSW and the duty), split harmonic by
harmonic to the 60th between every capacitor of the three-node network the netlist draws (FE_OUT, R11 and L11, VBUS20, R16 and
L16, CH_ACN), each part a branch ESR + jwESL + 1/(jwC); the two converters are not synchronised, so each part's mean square is
the front end's largest over (VIN, fSW) plus the charger's largest over (VBAT, fCH), the exact maximum over those corners. The
harmonics are a 4096-point midpoint DFT, as in the predecessor's recovered draft (inputs/recovered/, cited, never run).
ITS ACCEPTANCE is its convergence: every reported maximum is re-taken on source grids four to ten times finer and with twice
the harmonics, climbed again there, and the finer grids are themselves checked against finer ones still (section 4b).

THE SEARCH (SESSION, the coarsening stated as the task requires on this shared host): the passive bands are 332,100 sets on
the drawn node; their full enumeration in pure Python takes several CPU minutes per run. Each run is searched instead: (1)
every set of a COARSE grid (polymer ESL every 0.5 nH, ceramic C every 1 uF, every other band at all its corners) is bounded
from above (the per-harmonic largest weights); (2) the K sets with the highest bounds, one per corner of the other bands, are
evaluated exactly and climbed on the DENSE grid (ESL 0.05 nH, C 0.125 uF, and one band at a time over its corners) to a local
maximum; (3) at the best set the whole dense ESL x C slice is bounded and every set whose bound exceeds it is evaluated
exactly, re-climbing until none does. Section 4 also enumerates the second fix-up's node in full (110,700 sets).

THE RATING (MAKER, the ZK sheet): applied at the harmonics' actual frequencies through p.2's correction table and at the can's
temperature through p.1, p.5 and p.6 (the rating at 125 C with no uplift taken, the loss against the rated condition's, the
life equation from the worst inside air of pcb_envelope.yaml).

Run from the repository root:  python3 v2/docs/records/l4e8/ripple_dense.py > v2/docs/records/l4e8/ripple_dense.out
Needs pdftotext and PyYAML (the imported L4-E4 record needs pdftoppm and Pillow as well). About six minutes on the runner,
one process, the search coarsened as stated above.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import ast
import cmath
import contextlib
import hashlib
import importlib.util
import io
import itertools
import math
import operator
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import netlist_sexp as N  # noqa: E402

GEN_A = "v2/ecad/tools/gen_sch_a.py"
NET_A = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
R4DEC = "v2/docs/records/r4a/r4-decisions.md"
LM5176 = "v2/vendor/ti/lm5176-datasheet.pdf"
BQ25731 = "v2/vendor/ti/bq25731-datasheet.pdf"
EEHZK = "v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf"
L4E4_PY = "v2/docs/records/l4e4/l4e4_limits.py"
L4E4_OUT = "v2/docs/records/l4e4/l4e4_limits.out"
L4E6_PY = "v2/docs/records/l4e6/l4e6_fault_handling.py"
L4E6_OUT = "v2/docs/records/l4e6/l4e6_fault_handling.out"
R11_PY = "v2/docs/records/r11dep/r11_dep.py"
R11_OUT = "v2/docs/records/r11dep/r11_dep.out"
ENVELOPE = "v2/ecad/tools/pcb_envelope.yaml"
PINS = {   # the files this record reads; after any of them changes (a regeneration of board A, above all) it refuses by design
    GEN_A: "6a136feec6c9cf4e2011ed8c45a1f2e0adc3e263718c355b4b909872ee5d3c4b",
    NET_A: "6c40250c47195ebb7b2ae1388e284dc7f2fba9f2e683f654a47c98444290e8c5",
    R4DEC: "2e5a0c20fc9d4f25d70d3defda2aaee056ed6b340584447fddc711898377bee2",
    LM5176: "98191bec36d43771affa3e1540f6e1737347c19a1602747ffb4327509550a820",
    BQ25731: "3e5e927fdf63cf6a2397630987c58e947ebc80d5a1cfc93fb1fb58d98bb58973",
    EEHZK: "5455014606c0b676ca1df345f1969ee1b056403b8ee424bb29245115facda389",
    L4E4_PY: "d4a484439a7b53030423b596769bf748469134a45a46b3c91724e2b80d9e2a42",
    L4E4_OUT: "f68bf6951a6361caf6c41db14d86d735f9e3e9736723984ef61234aa10a80694",
    R11_PY: "c5e9d5713abfcb07a15276c489ce9774a20bff029b11d205a9e9877a21ed2684",
    R11_OUT: "f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209",
    L4E6_PY: "5f97b5b34fb1d0e555411a7dbd93554fd36a45af8801e3497cccf93ef0cc0995",
    L4E6_OUT: "4f7cefb270f326d1956a7c5b1e11c8901e4f21a0ff3feb4fcb6d66fb78728c66",
    ENVELOPE: "35cf43a2b7098a76abb4919685ece4d6e352331628f5f242c1492d9fcbbf2864",
}
# The predecessor's recovered drafts, filed beside this record as cited inputs (their sha256 checked, their code never run here):
# the second fix-up's bulk_ripple.py and the fix-up's loop_design.py, as a session transcript holds them (README.md, provenance).
RECOVERED = {
    "v2/docs/records/l4e8/inputs/recovered/bulk_ripple-r4a-fixup-A-1136.py": "c6b55794a762ecee48f36f4a445a22f3d8f80ffcf68f2c905cd9718827d15e34",
    "v2/docs/records/l4e8/inputs/recovered/loop_design-r4a-fixup-A-1024.py": "fe0d946bc020d4b68c3a4e417b4c2e7dfd98eeabd2352ff849de4ef0d781d7da",
}
PINS.update(RECOVERED)

# ---------------------------------------------------------------------------------------------------- SESSION constants
# The validation tolerances, FIXED BEFORE THE VALIDATION WAS RUN (L4E8-BANK.md, "The rebuild and its validation"):
TOL_DENSE = 0.02      # A: the record prints the dense figures to 0.01 A (rounding +-0.005 A) and does not give the interior
                      # spacing of its VBAT, fch and fsw grids (ASSUMPTION: even spacing) or the search's resolution
TOL_POINT = 0.0005    # A: the re-review's point is one evaluation, printed to 0.001 A in the record
TOL_LOOP = dict(pm=0.1, gm=0.1, mm=0.01, fc_lo=0.01, fc_hi=0.05, z=1.0)   # deg, dB, -, kHz, kHz, mOhm: half a printed digit and more
NH = 60               # RECORD: harmonics to the 60th
NS = 4096             # INFERRED: the recovered predecessor's midpoint DFT length
COARSE_ESL = (0, 10, 20, 30, 40)      # SESSION search: dense indices of the coarse grid (every 0.5 nH)
COARSE_C = (0, 8, 16, 24)             # (every 1 uF)
SEEDS = 6                             # SESSION search: seeds climbed per run, metric and current
MARGIN_PER_A = TOL_DENSE / 5.7        # SESSION decision rule: a candidate meets the rating with the validation tolerance as margin,
                                      # scaled from the record's 5.7 A to the current judged (a reading inside the tolerance of the
                                      # limit cannot be told from the limit by this rebuild)
# The candidate banks (cans, ceramics on VBUS20, ceramics on FE_OUT), in groups ordered by the change they make (SESSION: added
# cans first, the can being the dominant space and height item, then added ceramics, in threes; within a group the split between
# VBUS20 and FE_OUT; the generator owner places them). The groups are screened in order at the 2:1 spread and the first group
# holding a bank that meets the rating less the margin at every spread gives the bank; within it the lowest worst can is taken.
# The 7 mOhm list starts at one added can with twelve ceramics: every reading there is at a higher current and a lower R11 than
# the 8 mOhm reading of the same bank, both of which raise the can's current (section 5), so the 8 mOhm screen bounds it.
# A group of +n cans is opened only after the same cans with twelve more ceramics failed: more ceramics took current off the
# cans in every screen of this record (INFERRED from them), so +12 bounds every smaller ceramic change of that can count.
CANDIDATES_8 = [((0, 12), [(6, 30, 3), (6, 27, 6)]), ((1, 12), [(7, 30, 3), (7, 27, 6)]), ((2, 0), [(8, 18, 3), (8, 15, 6)]),
                ((2, 3), [(8, 21, 3), (8, 18, 6)]), ((2, 6), [(8, 24, 3), (8, 21, 6)])]
CANDIDATES_7 = [((2, 12), [(8, 30, 3), (8, 27, 6)]), ((3, 0), [(9, 18, 3), (9, 15, 6)]), ((3, 3), [(9, 21, 3), (9, 18, 6)]),
                ((3, 6), [(9, 24, 3), (9, 21, 6)]), ((4, 0), [(10, 18, 3), (10, 15, 6)])]
# THE SHARING BASIS (SESSION, L4E8-BANK.md): the cans' ESR within 2:1 (the spread, held by reading each can at 100 kHz before
# fitting) AND every can's branch within LAYOUT of every other's, both against the one can that has the lowest ESR and the
# shortest branch. LAYOUT is a layout rule for board A: a 10 mm wide VBUS20 pour 0.2 mm over its plane is about 25 pH/mm
# (mu0 h / w), so 0.5 nH is a 20 mm path difference; 0.5 mOhm is two squares of 2 oz copper. A symmetric placement about one
# VBUS20 entry (the record's O-01) holds both; the routed board's extracted branches verify it.
LAYOUT = (0.5e-9, 0.5e-3)
# The decision runs search the passive bands on finer source grids still (SESSION): VBAT every 0.2 V, fSW every 2.5 kHz, the
# charger every 5 kHz; the screens use the record's grids.
DECIDE = dict(vbat=0.2, fsw=2.5e3, fch=5e3)
GEOM = (1.0e-9, 1.0e-3)   # ASSUMPTION, the layout's stress: twice LAYOUT (a 40 mm path difference, or a narrower pour)
STRESS = dict(esl_lo=1.0, cer_lo=3.0)   # ASSUMPTION, the bands' stress: the cans' ESL down to 1.0 nH, the ceramics' C down to 3.0 uF
MUL = operator.mul
WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
                                    "fifteen sixteen seventeen eighteen nineteen twenty".split())}


def refuse(code, msg):
    sys.stderr.write("ripple_dense: %s; refusing\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


_PAGES = {}


def page(rel, n):
    key = (rel, n)
    if key not in _PAGES:
        _PAGES[key] = subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"],
                                     capture_output=True, text=True, check=True).stdout
    return _PAGES[key]


def need(text, pat, what, flags=re.M):
    m = re.search(pat, text, flags)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def flat(text):
    return " ".join(text.split())


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def si(value, unit):
    """'10uH ...' -> 1e-05; '330u 35V ...' -> 0.00033; '10mOhm ...' -> 0.01; '40.2k ...' -> 40200.0"""
    m = re.match(r"^([\d.]+)\s*([pnumk]?)" + unit, value)
    if not m:
        refuse(3, "value %r has no %s figure" % (value, unit or "plain"))
    return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "": 1.0}[m.group(2)]


# ============================================================================================================== the core
_TW = []


def dft_basis(kind, d, nh=NH, cache={}):
    """The switch current's harmonics 1..NH (complex, /NS) for an inductor average of 1 A and no ripple (G), and for no average
    and a 1 A peak-to-peak triangle (H); d the high-side (buck) or low-side (boost) duty. The waveform is linear in the two, so
    any (average, ripple) is il G + dil H. kind: boost_out (IL during 1 - D), buck_out (IL always), buck_in (IL during D)."""
    key = (kind, d, nh)
    if key in cache:
        return cache[key]
    if not _TW:
        _TW.extend(cmath.exp(-2j * math.pi * m / NS) for m in range(NS))
    idx, tri = [], []
    for j in range(NS):
        t = (j + 0.5) / NS
        rise = t < d
        tr = (-0.5 + t / d) if rise else (0.5 - (t - d) / (1 - d))
        on = (not rise) if kind == "boost_out" else (True if kind == "buck_out" else rise)
        if on:
            idx.append(j)
            tri.append(tr)
    G, H = [], []
    for k in range(1, nh + 1):
        sg = sh = 0j
        for j, tr in zip(idx, tri):
            tw = _TW[(k * j) % NS]
            sg += tw
            sh += tr * tw
        G.append(sg / NS)
        H.append(sh / NS)
    cache[key] = (G, H)
    return G, H


class Model:
    """The two sources over their grids: VBUS20 (vout), L1 and L2, VIN and fsw (the front end), VBAT and fch (the charger)."""
    def __init__(self, vout, l1, l2, vins, fsws, vbats, fchs, nh=NH):
        self.vout, self.l1, self.l2, self.nh = vout, l1, l2, nh
        self.vins, self.fsws, self.vbats, self.fchs = list(vins), list(fsws), list(vbats), list(fchs)
        F = [k * f for f in self.fsws for k in range(1, nh + 1)] + [k * f for f in self.fchs for k in range(1, nh + 1)]
        self.F = F
        self.W = [2 * math.pi * f for f in F]
        self.nfeW = len(self.fsws) * nh

    def fe(self, vin, fsw, iout):
        """the front end's output switch current: (harmonic weights 2|c_k|^2, its own rms ac, SNVSAI1D Equation 19's value)"""
        v = self.vout
        if vin < v:
            d = 1 - vin / v
            il, dil, kind = iout / (1 - d), vin * d / (self.l1 * fsw), "boost_out"
        else:
            d = v / vin
            il, dil, kind = iout, v * (1 - d) / (self.l1 * fsw), "buck_out"
        G, H = dft_basis(kind, d, self.nh)
        w = [2.0 * abs(il * g + dil * h) ** 2 for g, h in zip(G, H)]
        return w, (iout * math.sqrt(v / vin - 1) if vin < v else dil / math.sqrt(12))

    def ch(self, vbat, fch, iout):
        """the charger's input switch current (buck, VBUS20 to VBAT; its average is the front end's output current) and
        SLUSE66A Equation 4's value"""
        v = self.vout
        d2 = vbat / v
        il2, dil2 = iout / d2, v * d2 * (1 - d2) / (fch * self.l2)
        G, H = dft_basis("buck_in", d2, self.nh)
        return [2.0 * abs(il2 * g + dil2 * h) ** 2 for g, h in zip(G, H)], il2 * math.sqrt(d2 * (1 - d2))

    def weights(self, iout):
        if not hasattr(self, "_w"):
            self._w = {}
        if iout in self._w:
            return self._w[iout]
        self._w[iout] = self._weights(iout)
        return self._w[iout]

    def _weights(self, iout):
        fe = [[self.fe(vin, f, iout)[0] for vin in self.vins] for f in self.fsws]
        ch = [[self.ch(vb, f, iout)[0] for vb in self.vbats] for f in self.fchs]
        return dict(fe=fe, ch=ch, fe_max=[[max(c) for c in zip(*b)] for b in fe], ch_max=[[max(c) for c in zip(*b)] for b in ch], iout=iout)


def zinv(W, c, esr, esl):
    return [1.0 / complex(esr, w * esl - 1.0 / (w * c)) for w in W]


class Node:
    """One network: nb cans (one at the corner's ESR, its siblings at spread x it), nv ceramics on VBUS20, no on FE_OUT; R11 +
    L11 from FE_OUT to VBUS20, R16 + L16 from VBUS20 to CH_ACN, the half bridge's parts at CH_ACN. The front end injects at
    FE_OUT, the charger draws at CH_ACN. Set key: (ESL, C, C_can, ESR_can, ceramic ESL, ceramic ESR, L16, L11) band indices."""
    def __init__(self, model, bands, bank, r11, r16, spread, hf, sib_dl=0.0, sib_dr=0.0):
        self.m, self.b, self.s, self.dl, self.dr = model, bands, spread, sib_dl, sib_dr
        self.cap = max(20, int(300 * 1500 / len(model.W)))       # the caches' size, by the frequency list's length
        self.nb, self.nv, self.no = bank
        W = self.W = model.W
        self.yhf = [sum(t) for t in zip(*[zinv(W, *p) for p in hf])]
        self.y11 = {i: [1.0 / complex(r11, w * l) for w in W] for i, l in enumerate(bands["l11"])}
        y16 = {i: [1.0 / complex(r16, w * l) for w in W] for i, l in enumerate(bands["l16"])}
        self.k16 = {i: [a / (h + a) for a, h in zip(y, self.yhf)] for i, y in y16.items()}
        self.yce = {i: [h * k for h, k in zip(self.yhf, kk)] for i, kk in self.k16.items()}
        self._cer, self._rest, self._bank = {}, {}, {}
        self.dims = dict(ie=len(bands["esl_b"]), ic=len(bands["cer_c"]), icb=len(bands["cb_k"]), ier=len(bands["esr_k"]),
                         il=len(bands["cer_esl"]), ir=len(bands["cer_esr"]), i16=len(bands["l16"]), i11=len(bands["l11"]) if self.no else 1)

    def rest(self, key):
        v = self._rest.get(key)
        if v is not None:
            return v
        if len(self._rest) > self.cap:
            self._rest.clear()
        ic, il, ir, i16, i11 = key
        b, nf = self.b, self.m.nfeW
        ck = (ic, il, ir)
        yc = self._cer.get(ck)
        if yc is None:
            yc = self._cer[ck] = zinv(self.W, b["cer_c"][ic], b["cer_esr"][ir], b["cer_esl"][il])
        k16, yce = self.k16[i16], self.yce[i16]
        yc2 = [abs(c) ** 2 for c in yc]
        if self.no:
            y11 = self.y11[i11]
            yo = [self.no * y for y in yc]
            den = [a + c for a, c in zip(yo, y11)]
            k11 = [a / d for a, d in zip(y11, den)]
            r = [self.nv * c + o * k + e for c, o, k, e in zip(yc, yo, k11, yce)]
            k11_2 = [abs(k) ** 2 for k in k11]
            kk = k11_2[:nf] + [abs(k) ** 2 for k in k16[nf:]]
            q = [a * k for a, k in zip(y11[:nf], k11[:nf])]
            oofe = [c2 / abs(d) ** 2 for c2, d in zip(yc2[:nf], den[:nf])]
            ooch = [a * abs(c) ** 2 * c2 for a, c, c2 in zip(k11_2[nf:], k16[nf:], yc2[nf:])]
        else:
            r = [self.nv * c + e for c, e in zip(yc, yce)]
            kk = [1.0] * nf + [abs(k) ** 2 for k in k16[nf:]]
            q = oofe = ooch = None
        v = self._rest[key] = (r, kk, [a * c for a, c in zip(kk, yc2)], q, oofe, ooch)
        return v

    def bank(self, key):
        v = self._bank.get(key)
        if v is not None:
            return v
        if len(self._bank) > 3 * self.cap:
            self._bank.clear()
        ie, icb, ier = key
        b = self.b
        c, esr, esl = b["cb_k"][icb] * b["c_can"], b["esr_k"][ier] * b["esr_can"], b["esl_b"][ie]
        yo = zinv(self.W, c, esr, esl)
        if self.s == 1.0 and not (self.dl or self.dr):
            ys, yb = yo, [self.nb * y for y in yo]
        else:
            ys = zinv(self.W, c, esr * self.s + self.dr, esl + self.dl)
            yb = [a + (self.nb - 1) * y for a, y in zip(yo, ys)]
        yo2 = [abs(y) ** 2 for y in yo]
        v = self._bank[key] = (yb, yo2, yo2 if ys is yo else [abs(y) ** 2 for y in ys], esr, esr * self.s + self.dr)
        return v

    def vectors(self, s, metrics):
        """per-frequency squared current per ampere of source, for each metric: odd (the can at the corner's ESR), sib (one
        of its siblings), cerv (one VBUS20 ceramic), cero (one FE_OUT ceramic)"""
        ie, ic, icb, ier, il, ir, i16, i11 = s
        yb, yo2, ys2, eo, es = self.bank((ie, icb, ier))
        r, kk, kkc, q, oofe, ooch = self.rest((ic, il, ir, i16, i11))
        inv = [1.0 / abs(a + c) ** 2 for a, c in zip(yb, r)]
        out = {}
        if {"odd", "sib", "podd", "psib"} & set(metrics):
            out["odd"] = [i * k * y for i, k, y in zip(inv, kk, yo2)]
            out["sib"] = out["odd"] if ys2 is yo2 else [i * k * y for i, k, y in zip(inv, kk, ys2)]
            if "podd" in metrics:
                out["podd"] = [x * eo for x in out["odd"]]    # the can's own loss per ampere squared of source: ESR x its current squared
            if "psib" in metrics:
                out["psib"] = [x * es for x in out["sib"]]
        if "cerv" in metrics:
            out["cerv"] = [i * k for i, k in zip(inv, kkc)]
        if "cero" in metrics and self.no:
            nf = self.m.nfeW
            out["cero"] = ([abs(a + c + x) ** 2 * o * i for a, c, x, o, i in zip(yb, r, q, oofe, inv)]
                           + [o * i for o, i in zip(ooch, inv[nf:])])
        return out


def bound(vec, wt):
    n = len(wt["fe_max"][0])
    off = len(wt["fe_max"]) * n
    return (max(sum(map(MUL, w, vec[i * n:(i + 1) * n])) for i, w in enumerate(wt["fe_max"]))
            + max(sum(map(MUL, w, vec[off + i * n:off + (i + 1) * n])) for i, w in enumerate(wt["ch_max"])))


def exact(vec, wt):
    """(mean square, (FE's, (VIN index, fsw index)), (charger's, (VBAT index, fch index)))"""
    n = len(wt["fe_max"][0])
    bf = (-1.0, None)
    for i, blk in enumerate(wt["fe"]):
        seg = vec[i * n:(i + 1) * n]
        for j, w in enumerate(blk):
            x = sum(map(MUL, w, seg))
            if x > bf[0]:
                bf = (x, (j, i))
    off = len(wt["fe"]) * n
    bc = (-1.0, None)
    for i, blk in enumerate(wt["ch"]):
        seg = vec[off + i * n:off + (i + 1) * n]
        for j, w in enumerate(blk):
            x = sum(map(MUL, w, seg))
            if x > bc[0]:
                bc = (x, (j, i))
    return bf[0] + bc[0], bf, bc


def search(node, wts, metrics, slice_check=True):
    """The worst set per (metric, current index): stage 1 bounds on the coarse grid, stage 2 seeds climbed on the dense grid,
    stage 3 the dense ESL x C slice at the best set, re-climbed from any set the slice finds above it until none is (rounds).
    Returns {(metric, c): dict(ms, set, fe, ch, rounds, n1)}."""
    d = node.dims
    order = ("ie", "ic", "icb", "ier", "il", "ir", "i16", "i11")
    memo = {}

    def ex(s, m, c):
        k = (s, m, c)
        v = memo.get(k)
        if v is None:
            v = memo[k] = exact(node.vectors(s, (m,))[m], wts[c])
        return v

    rec = {(m, c): [] for m in metrics for c in range(len(wts))}
    n1 = 0
    for ic, il, ir, i16, i11 in itertools.product(COARSE_C, range(d["il"]), range(d["ir"]), range(d["i16"]), range(d["i11"])):
        for ie, icb, ier in itertools.product(COARSE_ESL, range(d["icb"]), range(d["ier"])):
            s = (ie, ic, icb, ier, il, ir, i16, i11)
            v = node.vectors(s, metrics)
            n1 += 1
            for m in metrics:
                for c in range(len(wts)):
                    rec[(m, c)].append((bound(v[m], wts[c]), s))
    res = {}
    for (m, c), lst in sorted(rec.items()):
        lst.sort(reverse=True)
        seeds, seen = [], set()
        for _u, s in lst:
            if s[2:] in seen:
                continue
            seen.add(s[2:])
            seeds.append((ex(s, m, c)[0], s))
            if len(seeds) >= SEEDS:
                break
        def climb(cur, curv):
            while True:
                nbr = [(cur[0] + a, cur[1] + b) + cur[2:] for a, b in itertools.product((-1, 0, 1), repeat=2)
                       if (a or b) and 0 <= cur[0] + a < d["ie"] and 0 <= cur[1] + b < d["ic"]]
                for pos, name in enumerate(order[2:], start=2):
                    nbr += [cur[:pos] + (x,) + cur[pos + 1:] for x in range(d[name]) if x != cur[pos]]
                cand = max((ex(x, m, c)[0], x) for x in nbr)
                if cand[0] <= curv:
                    return curv, cur
                curv, cur = cand

        best = max(climb(s0, v0) for v0, s0 in seeds)
        rounds = 0
        while slice_check:
            better = None
            for ie, ic in itertools.product(range(d["ie"]), range(d["ic"])):
                s = (ie, ic) + best[1][2:]
                if bound(node.vectors(s, (m,))[m], wts[c]) > best[0]:
                    e = ex(s, m, c)[0]
                    if e > best[0] + 1e-12 and (better is None or e > better[0]):
                        better = (e, s)
            if better is None:
                break
            rounds += 1
            best = climb(better[1], better[0])
        tot, fe, ch = ex(best[1], m, c)
        res[(m, c)] = dict(ms=tot, set=best[1], fe=fe, ch=ch, rounds=rounds, n1=n1)
    return res


def worst_can(res, c=0):
    """the worst can of a run: the larger of the can at the corner's ESR and its siblings"""
    return max((res[(m, c)] for m in ("odd", "sib") if (m, c) in res), key=lambda x: x["ms"])


# Finer source grids for the convergence of each reported maximum (SESSION): VBAT every 0.05 V, fSW every 0.5 kHz, the charger
# every 2 kHz; and the harmonics doubled. FINER checks that FINE has itself converged.
FINE = dict(vbat=0.05, fsw=0.5e3, fch=2e3, nh=2 * NH)
FINER = dict(vbat=0.02, fsw=0.25e3, fch=1e3)


def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def fine_model(m, rows, g=FINE):
    """the same sources as model m on finer grids (rows: the charger's FSW rows, (min, max) each)"""
    nf = int(round((m.fsws[-1] - m.fsws[0]) / g["fsw"])) + 1
    nb = int(round((m.vbats[-1] - m.vbats[0]) / g["vbat"])) + 1
    fch = []
    for lo, hi in rows:
        fch += lin(lo, hi, int(round((hi - lo) / g["fch"])) + 1)
    return Model(m.vout, m.l1, m.l2, m.vins, lin(m.fsws[0], m.fsws[-1], nf), lin(m.vbats[0], m.vbats[-1], nb), fch)


def converge(mk_node, model, s0, metric, iout):
    """the reported maximum re-taken on a model with finer source grids: the set re-evaluated, then climbed on the dense
    passive grid (one band at a time) to the local maximum there. Returns (mean square at s0, (mean square, set, fe, ch))."""
    node = mk_node(model)
    wt = model.weights(iout)
    d = node.dims
    order = ("ie", "ic", "icb", "ier", "il", "ir", "i16", "i11")
    memo = {}

    def ex(x):
        if x not in memo:
            memo[x] = exact(node.vectors(x, (metric,))[metric], wt)
        return memo[x]
    cur, curv = s0, ex(s0)[0]
    first = curv
    while True:
        nbr = [(cur[0] + a, cur[1] + b) + cur[2:] for a, b in itertools.product((-1, 0, 1), repeat=2)
               if (a or b) and 0 <= cur[0] + a < d["ie"] and 0 <= cur[1] + b < d["ic"]]
        for pos, name in enumerate(order[2:], start=2):
            nbr += [cur[:pos] + (x,) + cur[pos + 1:] for x in range(d[name]) if x != cur[pos]]
        cand = max((ex(x)[0], x) for x in nbr)
        if cand[0] <= curv:
            break
        curv, cur = cand
    tot, fe, ch = ex(cur)
    return first, (tot, cur, fe, ch, model)


# ============================================================================================================== the loop
def loop_model(cfg):
    """SNVSAI1D's small-signal model as the generator's lost loop_design.py carried it (its recovered draft and r4-decisions.md):
    T = kFB gmEA g Zc Gc Zll; Gc = H/Ri (buck) or (1-D)/Ri (1 - s/wRHP) H (boost, the load at R/2), H the sampling double pole
    at Fsw/2 with Q; Zll the local node (ceramics, n cans, the load); Zc = (Rc1 + 1/sCc1) || 1/sCc2 || ROUT."""
    fsw0, flo, fhi = cfg["fsw"]
    nf = 1100
    a, b = 1.0, math.log10(fhi / 2)
    F = [10.0 ** (a + i * (b - a) / (nf - 1)) for i in range(nf)]
    F[-1] = 10.0 ** b
    S = [2j * math.pi * f for f in F]
    return F, S


def _unwrap(p):
    out, corr = [p[0]], 0.0
    for x, y in zip(p[:-1], p[1:]):
        dd = y - x
        dm = (dd + math.pi) % (2 * math.pi) - math.pi
        if dm == -math.pi and dd > 0:
            dm = math.pi
        corr += 0.0 if abs(dd) < math.pi else dm - dd
        out.append(y + corr)
    return out


def loop_eval(cfg, nbulk, ncer, rcs, rc1, cc1, cc2, qs=(0.4, 0.8), lks=(1.0,)):
    F, S = loop_model(cfg)
    fsw0, flo, fhi = cfg["fsw"]
    gm, ro, acs, L = cfg["gm"], cfg["ro"], cfg["acs"], cfg["L"]
    cl_band = [c * ncer / cfg["ncer0"] for c in cfg["cl0"]]
    zc = [1.0 / (1.0 / (rc1 + 1.0 / (s * cc1)) + s * cc2 + 1.0 / ro) for s in S]
    bulk = [(cfg["c_can"] * k, cfg["esr_can"] * e) for k in (0.8, 1.2) for e in (0.3, 2.0)]
    pm = gmd = pmi = gmi = 999.0
    mm = 1e9
    flo_i, fhi_i = 1e12, 0.0
    flo_c, fhi_c, zpk, zr, ceil_ok, all_cross = 1e12, 0.0, 0.0, 0.0, True, True
    for (mode, vin), cl, iout, q, fsw, g, lk, (cb, eb) in itertools.product(cfg["modes"], cl_band, cfg["iouts"], qs, (flo, fhi),
                                                                          (0.8, 1.2), lks, bulk):
        vout, kfb = cfg["vout"], cfg["kfb"]
        rl = vout / iout * (0.5 if mode == "boost" else 1.0)
        ri = acs * rcs
        wn = math.pi * fsw
        if mode == "boost":
            dd = 1 - vin / vout
            wrhp = (vout / iout) * (1 - dd) ** 2 / (L * lk)
            rhp3 = wrhp / (2 * math.pi) / 3.0
        else:
            rhp3 = 1e12
        t, mag, zl = [], [], []
        for s, z in zip(S, zc):
            h = 1.0 / (1 + s / (wn * q) + (s / wn) ** 2)
            yl = 1.0 / (1.0 / (s * cl) + cfg["esr_l"]) + nbulk / (1.0 / (s * cb) + eb) + 1.0 / rl
            zll = 1.0 / yl
            gc = h / ri if mode == "buck" else (1 - dd) / ri * (1 - s / wrhp) * h
            tv = kfb * gm * g * gc * zll * z
            t.append(tv)
            mag.append(abs(tv))
            zl.append(abs(zll / (1 + tv)))
        ph = [x * 180 / math.pi for x in _unwrap([cmath.phase(x) for x in t])]
        sh = 360 * round((ph[0] + 90) / 360)
        ph = [x - sh for x in ph]
        fh = 0.0
        for j in range(len(F) - 1):
            if (mag[j] - 1) * (mag[j + 1] - 1) <= 0:
                pm = min(pm, 180 + ph[j])
                flo_c = min(flo_c, F[j])
                fh = max(fh, F[j])
                la, lb = math.log10(mag[j]), math.log10(mag[j + 1])      # the crossing interpolated in log |T| over log f
                x = la / (la - lb) if la != lb else 0.0
                pmi = min(pmi, 180 + ph[j] + x * (ph[j + 1] - ph[j]))
                fci = 10 ** (math.log10(F[j]) + x * (math.log10(F[j + 1]) - math.log10(F[j])))
                flo_i, fhi_i = min(flo_i, fci), max(fhi_i, fci)
            for k in (-180.0, -540.0):
                if (ph[j] - k) * (ph[j + 1] - k) <= 0:
                    gmd = min(gmd, -20 * math.log10(max(mag[j], 1e-12)))
                    x = (k - ph[j]) / (ph[j + 1] - ph[j]) if ph[j + 1] != ph[j] else 0.0
                    gmi = min(gmi, -20 * (math.log10(max(mag[j], 1e-12)) + x * (math.log10(max(mag[j + 1], 1e-12)) - math.log10(max(mag[j], 1e-12)))))
        fhi_c = max(fhi_c, fh)
        ceil_ok = ceil_ok and fh <= min(fsw0 / 20.0, rhp3)
        all_cross = all_cross and fh > 0
        mm = min(mm, min(abs(1 + x) for x in t))
        zpk = max(zpk, max(zl))
        zr = max(zr, max(zl) / (vout ** 2 / cfg["p_bound"] / 3.0))
    return dict(pm=pm, gm=gmd, mm=mm, fc_lo=flo_c / 1e3, fc_hi=fhi_c / 1e3, z=zpk * 1e3, z_ratio=zr, ceil_ok=ceil_ok, all_cross=all_cross,
                pm_i=pmi, gm_i=gmi, fc_lo_i=flo_i / 1e3, fc_hi_i=fhi_i / 1e3)


# ============================================================================================================== the inputs
def call_index(tree):
    """every call in gen_sch_a.py by its function's name, with its literal arguments where they are literals"""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
            out.append((name, n))
    return out


def lit(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def read_generator(R):
    src = open(os.path.join(TOP, GEN_A), encoding="utf-8").read()
    tree = ast.parse(src)
    calls = call_index(tree)
    fd = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "lm5176"]
    if len(fd) != 1:
        refuse(3, "gen_sch_a.py: lm5176() not found once")
    args = fd[0].args
    defaults = dict(zip([a.arg for a in args.args][-len(args.defaults):], [lit(x) for x in args.defaults]))
    fe = [n for name, n in calls if name == "lm5176" and n.args and lit(n.args[0]) == "FE"]
    if len(fe) != 1:
        refuse(3, "gen_sch_a.py: the front end's lm5176() call not found once")
    fe = fe[0]
    pos = [lit(a) for a in fe.args]
    kw = {k.arg: lit(k.value) for k in fe.keywords}
    refs = pos[10]
    co = tuple(refs[22:25])
    ker = dict(defaults)
    ker.update(kw)
    bulk_zk = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "BULK_ZK" for t in n.targets)]
    bzk = lit(bulk_zk[0].value)
    can_value = bzk[ker["bulk_part"]][0]
    vbus_cer = [c for c in co + tuple(ker["cout_extra"]) if c not in ker["cout_pre"]]
    # the charger's C20 to C22: a loop of c() calls on VBUS20 (evaluated for its loop variable)
    ch_in = []
    for n in ast.walk(tree):
        if isinstance(n, ast.For) and isinstance(n.iter, ast.Call) and getattr(n.iter.func, "id", "") == "range":
            for b in n.body:
                v = b.value if isinstance(b, ast.Expr) else None
                if isinstance(v, ast.Call) and getattr(v.func, "id", "") == "c" and len(v.args) >= 3 and lit(v.args[2]) == "VBUS20":
                    var = n.target.id
                    for k in range(lit(n.iter.args[0])):
                        ref = eval(compile(ast.Expression(v.args[0]), GEN_A, "eval"), {"__builtins__": {}}, {var: k})
                        ch_in.append((ref, lit(v.args[1])))
    one = {}
    for name, n in calls:
        if name in ("c", "r", "part") and n.args and lit(n.args[0]) in ("C190", "C191", "R16", "L2"):
            one[lit(n.args[0])] = [lit(a) for a in n.args]
    rails = {}
    for name, n in calls:
        if name == "rail" and n.args and lit(n.args[0]) in ("VBUS20", "VBAT"):
            rails[lit(n.args[0])] = dict(volts=lit(n.args[1]), **{k.arg: lit(k.value) for k in n.keywords if lit(k.value) is not None})
    rt = [lit(n.args[1]) for name, n in call_index(fd[0]) if name == "r" and len(n.args) > 1 and isinstance(n.args[0], ast.Name) and n.args[0].id == "rrt"]
    if len(rt) != 1 or len(ch_in) != 3 or set(one) != {"C190", "C191", "R16", "L2"} or set(rails) != {"VBUS20", "VBAT"}:
        refuse(3, "gen_sch_a.py: the node's parts not read (RT %s, charger inputs %s, %s, rails %s)" % (rt, ch_in, sorted(one), sorted(rails)))
    g = flat(" ".join(l.strip().lstrip("#").strip() for l in src.splitlines()))
    R["gen"] = dict(src=src, flat=g, defaults=defaults, kw=kw, pos=pos, co=co, bulk=tuple(kw["bulk"]), bulk_part=kw["bulk_part"],
                    can_value=can_value, cout=ker["cout"], cout_extra=tuple(kw["cout_extra"]), cout_pre=tuple(kw["cout_pre"]),
                    vbus_cer=vbus_cer, ch_in=ch_in, one=one, rails=rails, rt=rt[0], isns=ker["isns"], rcs=ker["rcs"], comp=kw["comp"],
                    css=kw["css"], lval=pos[7], rfb_top=pos[5], rfb_bot=ker["rfb_val"])


def read_netlist(R):
    a = N.load(os.path.join(TOP, NET_A))
    ca, nets = a["components"], a["nets"]
    G = R["gen"]

    def on(net):
        return sorted({r for r, _p, _f, _t in nets[net]})
    vb, fo, cn = on("VBUS20"), on("FE_OUT"), on("CH_ACN")
    cans = [r for r in vb if ca[r]["value"] == G["can_value"]]
    vcer = [r for r in vb if ca[r]["value"] == G["cout"]]
    ocer = [r for r in fo if ca[r]["value"] == G["cout"]]
    hf = [r for r in cn if r.startswith("C")]
    facts = [
        ("the cans on VBUS20 are the front end's bulk=%s, each '%s'" % (len(G["bulk"]), G["can_value"]), sorted(cans) == sorted(G["bulk"])),
        ("the VBUS20 ceramics are the stage's C13 to C15 and cout_extra less cout_pre, with the charger's %s, each '%s'"
         % ("/".join(r for r, _v in G["ch_in"]), G["cout"]),
         sorted(vcer) == sorted(G["vbus_cer"] + [r for r, _v in G["ch_in"]]) and all(v == G["cout"] for _r, v in G["ch_in"])),
        ("the FE_OUT ceramics are cout_pre, before R11", sorted(ocer) == sorted(G["cout_pre"])),
        ("CH_ACN carries C190 '%s' and C191 '%s' and no other capacitor" % (G["one"]["C190"][1], G["one"]["C191"][1]), sorted(hf) == ["C190", "C191"]),
        ("R11 '%s' FE_OUT to VBUS20; R16 '%s' VBUS20 to CH_ACN" % (ca["R11"]["value"], ca["R16"]["value"]),
         ca["R11"]["value"].startswith(G["isns"] + "Ohm") and {p["net"] for p in a["pins"]["R11"].values()} == {"FE_OUT", "VBUS20"}
         and ca["R16"]["value"] == G["one"]["R16"][1] and {p["net"] for p in a["pins"]["R16"].values()} == {"VBUS20", "CH_ACN"}),
        ("L1 '%s', L2 '%s'" % (ca["L1"]["value"], ca["L2"]["value"]), ca["L1"]["value"] == G["lval"] and ca["L2"]["value"] == G["one"]["L2"][3]),
    ]
    other_c = [r for r in vb if r.startswith("C") and r not in cans and r not in vcer]
    if not all(ok for _f, ok in facts):
        refuse(3, "the netlist and the generator disagree: %s" % [f for f, ok in facts if not ok])
    R["net"] = dict(facts=[f for f, _ in facts], other_c=[(r, ca[r]["value"]) for r in other_c], n_vb=len(vb))


def read_record(R):
    d = flat(open(os.path.join(TOP, R4DEC), encoding="utf-8").read().replace("**", ""))
    g = R["gen"]["flat"]
    m = need(d, r"Bands: polymer ESL ([\d.]+) to ([\d.]+) nH in ([\d.]+) nH steps \((\d+)\), ceramic effective C ([\d.]+) to ([\d.]+) uF in "
                r"([\d.]+) uF steps \((\d+)\), ceramic ESL ([\d.]+) / ([\d.]+) / ([\d.]+) nH, ceramic ESR (\d+) and (\d+) mOhm, L16 (\d+) and "
                r"(\d+) nH, bulk C x([\d.]+) / ([\d.]+) / ([\d.]+), bulk ESR x([\d.]+) / ([\d.]+) / ([\d.]+); VIN_RAW (\d+) to (\d+) V \((\d+)\), "
                r"fsw (\d+) points over (\d+) to (\d+) kHz, VBAT (\d+) to ([\d.]+) V \((\d+)\), fch (\d+) points over each charger band",
             "r4-decisions.md the dense bands", 0)
    x = [float(v) for v in m.groups()]
    l11 = [float(v) for v in need(d, r"L11 INFERRED (\d+) to (\d+) nH", "r4-decisions.md L11", 0).groups()]
    vins = [float(v) for v in need(d, r"Corners: VIN_RAW ([\d., ]+) V;", "r4-decisions.md the VIN_RAW corners", 0).group(1).split(", ")]
    need(d, r"one can at the corner's ESR, its siblings at s times it", "r4-decisions.md the spread's definition", 0)
    bands = dict(esl_b=[(x[0] + x[2] * i) * 1e-9 for i in range(int(x[3]))], cer_c=[(x[4] + x[6] * i) * 1e-6 for i in range(int(x[7]))],
                 cer_esl=[v * 1e-9 for v in x[8:11]], cer_esr=[v * 1e-3 for v in x[11:13]], l16=[v * 1e-9 for v in x[13:15]],
                 cb_k=x[15:18], esr_k=x[18:21], l11=[(l11[0] + (l11[1] - l11[0]) * i / 2) * 1e-9 for i in range(3)])
    if abs(bands["esl_b"][-1] - x[1] * 1e-9) > 1e-15 or abs(bands["cer_c"][-1] - x[5] * 1e-6) > 1e-15 or len(vins) != int(x[23]) \
            or (vins[0], vins[-1]) != (x[21], x[22]):
        refuse(3, "r4-decisions.md: the bands do not close on their ends")
    grid = dict(n_fsw=int(x[24]), fsw_rec=(x[25], x[26]), vbat=(x[27], x[28]), n_vbat=int(x[29]), n_fch=int(x[30]), vins=vins)
    rec = {}
    m = need(g, r"Worst can over the whole bands at 5\.7 A: ([\d.]+) A, (\d+) percent of 2\.8 A matched; ([\d.]+) A \((\d+) percent\) at a 1\.5:1"
                r" spread and ([\d.]+) A \((\d+) percent\) at 2:1; at the declared 5 A ([\d.]+) / ([\d.]+) / ([\d.]+) A", "gen_sch_a.py the worst can", 0)
    rec["third"] = {(1.0, 5.7): float(m.group(1)), (1.5, 5.7): float(m.group(3)), (2.0, 5.7): float(m.group(5)),
                    (1.0, 5.0): float(m.group(7)), (1.5, 5.0): float(m.group(8)), (2.0, 5.0): float(m.group(9))}
    m = need(g, r"The second fix-up's node reads ([\d.]+) A, (\d+) percent, and ([\d.]+) A at a 2:1 ESR spread", "gen_sch_a.py the second fix-up's node", 0)
    rec["second"] = {(1.0, 5.7): float(m.group(1)), (2.0, 5.7): float(m.group(3))}
    m = need(d, r"reads ([\d.]+) A rms, (\d+) percent \(ESL ([\d.]+) nH, ceramic ([\d.]+) uF, the charger at (\d+) kHz, VIN (\d+) V, VBAT (\d+) V; "
                r"([\d,]+) of ([\d,]+) passive sets over 2\.8 A\), ([\d.]+) A \((\d+) percent\) at 5 A, and ([\d.]+) A \((\d+) percent\) at a 2:1 ESR spread",
             "r4-decisions.md the second fix-up's dense figures", 0)
    if float(m.group(1)) != rec["second"][(1.0, 5.7)] or float(m.group(12)) != rec["second"][(2.0, 5.7)]:
        refuse(3, "the generator's and the record's second fix-up figures differ")
    rec["second"][(1.0, 5.0)] = float(m.group(10))
    rec["second_corner"] = dict(esl=float(m.group(3)), cer=float(m.group(4)), fch=float(m.group(5)), vin=float(m.group(6)), vbat=float(m.group(7)))
    rec["second_count"] = (int(m.group(8).replace(",", "")), int(m.group(9).replace(",", "")))
    m = need(d, r"Worst can over the whole bands: ([\d.]+) A rms, (\d+) percent of 2\.8 A at 5\.7 A \(ESL ([\d.]+) nH, ceramic ([\d.]+) uF, VIN (\d+) V, "
                r"fsw (\d+) kHz, VBAT (\d+) V, the charger at (\d+) kHz: the FE's share ([\d.]+) A, the charger's ([\d.]+) A\); ([\d.]+) A \((\d+) percent\) "
                r"at a 1\.5:1 spread; ([\d.]+) A \((\d+) percent\) at a 2:1 spread \(ESL ([\d.]+) nH, the charger at (\d+) kHz\)",
             "r4-decisions.md the third fix-up's corners", 0)
    rec["third_corner"] = dict(esl=float(m.group(3)), cer=float(m.group(4)), vin=float(m.group(5)), fsw=float(m.group(6)), vbat=float(m.group(7)),
                               fch=float(m.group(8)), fe=float(m.group(9)), ch=float(m.group(10)), esl2=float(m.group(15)), fch2=float(m.group(16)))
    rec["third_count"] = tuple(int(v.replace(",", "")) for v in need(d, r"(\d+) of ([\d,]+) passive sets exceed 2\.8 A in any of these six runs",
                                                                       "r4-decisions.md the third fix-up's count", 0).groups())
    m = need(d, r"at the re-review's point \(ESL ([\d.]+) nH, ceramic ([\d.]+) uF, C x([\d.]+), ([\d.]+) A, ([\d.]+) V, (\d+) kHz, a (\d+) V pack, the "
                r"charger at (\d+) kHz\) gives ([\d.]+) A, the re-review's ([\d.]+) A", "r4-decisions.md the re-review's point", 0)
    rec["point"] = dict(esl=float(m.group(1)), cer=float(m.group(2)), ck=float(m.group(3)), iout=float(m.group(4)), vin=float(m.group(5)),
                        fsw=float(m.group(6)), vbat=float(m.group(7)), fch=float(m.group(8)), value=float(m.group(9)), rr=float(m.group(10)))
    if "the re-review's %.2f A point included" % rec["point"]["rr"] not in g:
        refuse(3, "gen_sch_a.py does not name the re-review's point")
    m = need(g, r"Worst ceramic ([\d.]+) A on VBUS20 and ([\d.]+) A on FE_OUT", "gen_sch_a.py the worst ceramic", 0)
    rec["ceramic"] = (float(m.group(1)), float(m.group(2)))
    m = need(g, r"Rc1 15 k, Cc1 220 nF, Cc2 680 pF read PM ([\d.]+) degrees, GM ([\d.]+) dB, \|1 \+ T\| ([\d.]+), crossover ([\d.]+) to ([\d.]+) kHz, "
                r"(\d+) mOhm against ([\d.]+) Ohm; on the widened band PM ([\d.]+), GM ([\d.]+) dB, \|1 \+ T\| (\d+\.\d+)", "gen_sch_a.py the loop", 0)
    rec["loop"] = dict(pm=float(m.group(1)), gm=float(m.group(2)), mm=float(m.group(3)), fc_lo=float(m.group(4)), fc_hi=float(m.group(5)),
                       z=float(m.group(6)), zb=float(m.group(7)))
    rec["loop_wide"] = dict(pm=float(m.group(8)), gm=float(m.group(9)), mm=float(m.group(10)))
    m = need(d, r"Taken: (\w+) EEHZK1V331P and (\w+) more 10u 50V\. .{0,900}?With C20 to C22 the node carries (\w+) ceramics", "r4-decisions.md the second fix-up's node", 0)
    rec["second_bank"] = (WORDS[m.group(1)], WORDS[m.group(3)], 0)
    m = need(d, r"loop_design\.py's FE stage is re-described \((\w+) local ceramics, (\d+) to (\d+) uF; no remote capacitance, only the 11 nF behind "
                r"R16; ([\d.]+) A; Middlebrook's bound at (\d+) W, ([\d.]+) Ohm\)", "r4-decisions.md the FE loop stage", 0)
    rec["loop_stage"] = dict(ncer0=WORDS[m.group(1)], cl0=(float(m.group(2)) * 1e-6, float(m.group(3)) * 1e-6), iout=float(m.group(4)), p=float(m.group(5)))
    need(d, r"the band scaled from fifteen to 21 parts; the three FE_OUT parts sit behind 10 mOhm, nothing beside their reactance at the loop's "
            r"frequencies, so they count with the local bank", "r4-decisions.md the loop's ceramic scaling", 0)
    m = need(d, r"widened band \(Q ([\d.]+) to ([\d.]+), L ([\d.]+) to ([\d.]+)\) PM", "r4-decisions.md the widened band", 0)
    rec["wide"] = dict(q=(float(m.group(1)), float(m.group(2))), lk=(float(m.group(3)), float(m.group(4))))
    m = need(d, r"Rejected: five cans .{0,120}?seven \((\d+) more points at a 2:1 spread for one more can, and a ([\d.]+) mF node for the soft start\)",
             "r4-decisions.md seven cans rejected", 0)
    rec["seven_rejected"] = (int(m.group(1)), float(m.group(2)))
    # the soft start, the bleed and the restart ring as recorded (gen_sch_a.py), and the BIAS draw (r4-decisions.md)
    m = need(g, r"the ramp's own draw \(charging plus the controller's BIAS\) at the end of the ramp is ([\d.]+) percent of the entry's floor at 9 V, "
                r"([\d.]+) at 12 V and ([\d.]+) at 13\.8 V, every worst corner stacked \(C \+(\d+) percent and unbiased ceramics, ISS maximum, CSS "
                r"-([\d.]+) percent, VBUS20 ([\d.]+) V, efficiency ([\d.]+)\)", "gen_sch_a.py the soft start's draw", 0)
    rec["ss"] = dict(pct=(float(m.group(1)), float(m.group(2)), float(m.group(3))), ck=1 + float(m.group(4)) / 100, css_k=1 - float(m.group(5)) / 100,
                     vbus=float(m.group(6)), eta=float(m.group(7)))
    rec["entry"] = float(need(g, r"\(([\d.]+) A with R19's 1 percent\)", "gen_sch_a.py the entry's floor", 0).group(1))
    m = need(d, r"(\d+\.\d+) mF at its largest: six cans at \+20 percent, (\d+) ceramics unbiased at \+(\d+) percent", "r4-decisions.md the node's largest", 0)
    rec["node_max"] = (float(m.group(1)), int(m.group(2)), 1 + float(m.group(3)) / 100)
    rec["bias"] = float(need(d, r"BIAS ([\d.]+) A INFERRED", "r4-decisions.md the BIAS draw", 0).group(1))
    m = need(g, r"(\d+) to (\d+) Ohm, ([\d.]+) W per part at (\d+) V and 5 percent low, ([\d.]+) J per part per event; tau ([\d.]+) to ([\d.]+) s and "
                r"([\d.]+) to ([\d.]+) s to the release level", "gen_sch_a.py the bleed", 0)
    rec["bleed"] = dict(r=(float(m.group(1)), float(m.group(2))), v=float(m.group(4)), j=float(m.group(5)), tau=(float(m.group(6)), float(m.group(7))),
                        t=(float(m.group(8)), float(m.group(9))))
    m = need(g, r"VBUS20 keeps ([\d.]+) to ([\d.]+) V on ([\d.]+) to ([\d.]+) mF", "gen_sch_a.py the bank's range", 0)
    rec["bank_range"] = (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
    rec["release"] = tuple(float(v) for v in need(g, r"until VBUS20 is under ([\d.]+) / ([\d.]+) / ([\d.]+) V", "gen_sch_a.py the release level", 0).groups())
    m = need(g, r"a start from at most ([\d.]+) V is the bank ringing into L1 through the buck low side \(([\d.]+) A peak at L1 -(\d+) percent and the "
                r"bank's \+(\d+) percent, under Isat ([\d.]+) A; ([\d.]+) mJ", "gen_sch_a.py the restart ring", 0)
    rec["ring"] = dict(v=float(m.group(1)), pk=float(m.group(2)), lk=1 - float(m.group(3)) / 100, ck=1 + float(m.group(4)) / 100,
                       isat=float(m.group(5)), mj=float(m.group(6)))
    need(g, r"The 3\.3 uH XAL6030-332ME drawn here until today", "gen_sch_a.py S-117's record of the charger's old inductor", 0)
    rec["l2_old"] = 3.3e-6
    rec["css_aged"] = float(need(g, r"rested on CSS at ([\d.]+) of nominal", "gen_sch_a.py CSS's aged corner", 0).group(1))
    R.update(bands=bands, grid=grid, rec=rec)


def read_makers(R):
    p6 = page(LM5176, 6)
    need(page(LM5176, 1), r"SNVSAI1D . JUNE 2017 . REVISED AUGUST 2021", "SNVSAI1D's revision on p.1")
    fsw_row = tuple(float(v) * 1e3 for v in need(p6, r"fSW\(1\)\s+Switching frequency 1\s+RT = (\d+) k\S+\s+(\d+)\s+(\d+)\s+(\d+)", "p.6 fSW(1)").groups()[1:])
    rt_row = float(need(p6, r"fSW\(1\)\s+Switching frequency 1\s+RT = (\d+) k", "p.6 fSW(1) RT").group(1)) * 1e3
    gm = float(need(p6, r"gmEA\s+Error amplifier gm\s+([\d.]+)\s+mS", "p.6 gmEA").group(1)) * 1e-3
    ro = float(need(p6, r"ROUT\s+Amplifier output resistance\s+(\d+)\s+M", "p.6 ROUT").group(1)) * 1e6
    vref = tuple(float(v) for v in need(p6, r"VREF\s+Feedback reference voltage\s+FB = COMP\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "p.6 VREF").groups())
    iss = tuple(float(v) * 1e-6 for v in need(p6, r"ISS\s+Soft-start pullup current\s+VSS = 0 V\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "p.6 ISS").groups())
    p17 = page(LM5176, 17)
    need(p17, r"190 ns", "p.17 Equation 5's 190 ns")
    need(p17, r"116 pF\s+\(5\)", "p.17 Equation 5's 116 pF")
    acs = float(need(page(LM5176, 24), r"(\d+)\s+m\S\s+u\s+(\d+)\s+\(26\)", "p.24 Equation 26's ACS").group(2))
    need(page(LM5176, 23), r"ICOUT\(RMS\)", "p.23 Equation 19")
    need(page(LM5176, 23), r"\(19\)", "p.23 Equation 19's number")
    need(flat(page(LM5176, 30)), r"When using the average current loop, divide the overall capacitor \(CIN or COUT\) between the two sides of the sense "
                                 r"resistor to ensure small cycle-by-cycle ripple", "p.30 9.1's division")
    need(flat(page(LM5176, 27)), r"\(44\)", "p.27 Equation 44")
    b16 = page(BQ25731, 16)
    f0 = tuple(float(v) * 1e3 for v in need(b16, r"Reg0x01\[1\] = 0\s+(\d+)\s+(\d+)\s+(\d+)\s+kHz", "SLUSE66A p.16 FSW at 800 kHz").groups())
    f1 = tuple(float(v) * 1e3 for v in need(b16, r"Reg0x01\[1\] = 1\s+(\d+)\s+(\d+)\s+(\d+)\s+kHz", "SLUSE66A p.16 FSW at 400 kHz").groups())
    need(page(BQ25731, 2), r"SLUSE66A", "SLUSE66A's number")
    need(page(BQ25731, 85), r"ICIN = ICHG\s*\S\s+D\s*\S\s*\(1 - D\)\s+\(4\)", "SLUSE66A p.85 Equation 4")
    need(flat(page(BQ25731, 85)), r"should be placed in front of RAC current sensing", "SLUSE66A p.85 the input capacitor in front of RAC")
    need(page(BQ25731, 27), r"4\.7 \S+H \(recommended for 400 kHz\)", "SLUSE66A p.27 Table 9-4's 4.7 uH row")
    p43 = flat(page(BQ25731, 43))
    need(p43, r"1 PWM_FREQ R/W 1b Switching Frequency Selection: Recommend 800 kHz with 2\.2 \S+H, and 400 kHz with 4\.7 \S+H\. 0b: 800kHz 1b: 400 kHz<default at POR>",
         "SLUSE66A p.43 PWM_FREQ")
    z1, z2, z7 = page(EEHZK, 1), page(EEHZK, 2), flat(page(EEHZK, 7))
    row = need(z2, r"(\d+)\s+10\.0\s+10\.2\s+10\.5\s+G\s+(\d+)\s+(\d+)\s+([\d.]+)\s+EEHZK1V331P", "EEHZK p.2 the 331P row")
    need(z1, r"Capacitance tolerance\s+±20 % \(120 Hz / \+20 ℃\)", "EEHZK p.1 capacitance +-20 %")
    need(z2, r"\*1: Ripple current \(100 kHz / \+125 ℃\)", "EEHZK p.2 the ripple condition")
    need(z2, r"\*2: ESR \(100 kHz / \+20 ℃\)", "EEHZK p.2 the ESR condition")
    rows100 = [l.split() for l in z2.splitlines() if l.strip().startswith("100 μF ≦ C")]
    need(z2, r"100 kHz ≦ f < 500 kHz\s+500 kHz ≦ f", "EEHZK p.2 the correction columns from 100 kHz")
    if len(rows100) != 4:
        refuse(3, "EEHZK p.2: the four correction rows for 100 uF and more not read")
    last = rows100[-1][-2:]
    need(z1, r"ESR\s+≦ 200 % of the initial limit", "EEHZK p.1 ESR after endurance")
    corr = []
    heads = [l for l in z2.splitlines() if "Frequency (f)" in l]
    if len(heads) != 4:
        refuse(3, "EEHZK p.2: four frequency headings not read")
    for h_, r_ in zip(heads, rows100):
        lows = [float(v) * (1e3 if u == "kHz" else 1.0) for v, u in re.findall(r"(\d+) (Hz|kHz) ≦ f", h_)]
        vals = [float(v) for v in r_[-4:]]
        if len(lows) != 4:
            refuse(3, "EEHZK p.2: a correction heading's four columns not read")
        corr += list(zip(lows, vals))
    life_h, t_cat = (float(v) for v in need(z1, r"Endurance : (\d+) h at (\d+) ℃", "EEHZK p.1 endurance").groups())
    need(flat(page(EEHZK, 5)), r"In general, a 10 ℃ drop in the temperature will double the life", "EEHZK p.5 the life rule")
    need(page(EEHZK, 6), r"L2 = L1 x 2", "EEHZK p.6 the life equation")
    cap_y = float(need(flat(page(EEHZK, 6)), r"the estimated service life is not longer than (\d+) years", "EEHZK p.6 the 15 years").group(1))
    need(z7, r"use capacitors with the same part number", "EEHZK p.7 parallel parts")
    need(page(EEHZK, 2), r"01-Apr-22", "EEHZK the sheet's date")
    R["mk"] = dict(fsw_row=fsw_row, rt_row=rt_row, gm=gm, ro=ro, vref=vref, iss=iss, acs=acs, f800=f0, f400=f1,
                   c_can=float(row.group(1)) * 1e-6, rip=float(row.group(2)) / 1000.0, esr_can=float(row.group(3)) * 1e-3,
                   corr_hi=tuple(float(v) for v in last), corr=sorted(corr), life_h=life_h, t_cat=t_cat, life_cap_y=cap_y)


# ============================================================================================================== compute
def compute():
    for rel, want in PINS.items():
        if sha(rel) != want:
            refuse(2, "%s is not the pinned file" % rel)
    R = {}
    # ---------------------------------------------------------------- 0. the highest permitted currents (L4-E4's band(), as L4-E6 takes them)
    L4 = load("l4e4_limits_for_l4e8", L4E4_PY)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        R4 = L4.compute()
    if buf.getvalue():
        refuse(4, "l4e4_limits.compute() printed")
    band = R4["fn"]["band"]
    t6 = open(os.path.join(TOP, L4E6_OUT), encoding="utf-8").read()
    s6 = ast.parse(open(os.path.join(TOP, L4E6_PY), encoding="utf-8").read())
    takes = [n for n in ast.walk(s6) if isinstance(n, ast.keyword) and n.arg == "hi" and ast.unparse(n.value) == "band(r)[2]"]
    maps = [n for n in ast.walk(s6) if isinstance(n, ast.Dict) and [ast.unparse(k) for k in n.keys] == ["'8'", "'7'"]
            and [ast.unparse(v) for v in n.values] == ["R4['r11']", "R4['alt']['r']"]]
    if len(takes) != 1 or len(maps) != 1:
        refuse(4, "l4e6_fault_handling.py does not take o['hi'] as band(r)[2] of L4-E4's two R11 values")
    out = []
    for key, r in (("8", R4["r11"]), ("7", R4["alt"]["r"])):
        hi = band(r)[2]
        m = need(t6, r"R11 %s mOhm \((C\d+)\): band [\d.]+ / [\d.]+ / ([\d.]+) A; the highest permitted current ([\d.]+) A" % key, "L4-E6's %s mOhm line" % key)
        if not ("%.3f" % hi == m.group(2) == m.group(3)):
            refuse(4, "L4-E6 prints %s A at %s mOhm, L4-E4's band() gives %.6f A" % (m.group(3), key, hi))
        out.append(dict(key=key, r11=r, code=m.group(1), hi=hi))
    R["outcomes"] = out
    # ---------------------------------------------------------------- the node, the record, the makers
    read_generator(R)
    read_netlist(R)
    read_record(R)
    read_makers(R)
    G, rec, mk, bands, grid = R["gen"], R["rec"], R["mk"], R["bands"], R["grid"]
    bands.update(c_can=mk["c_can"], esr_can=mk["esr_can"])
    # r11_dep.py's linear scaling, from the same recorded figures, checked against L4-E6's printed B-4 lines
    a57 = [rec["third"][(s, 5.7)] for s in (1.0, 1.5, 2.0)]
    a50 = [rec["third"][(s, 5.0)] for s in (1.0, 1.5, 2.0)]
    can_k = [max(x / 5.7, y / 5.0) for x, y in zip(a57, a50)]
    for o in out:
        o["lin"] = [k * o["hi"] for k in can_k]
        m = need(t6, r"R11 %s mOhm, %.3f A: worst can ([\d.]+) A matched, ([\d.]+) A at 1\.5:1, ([\d.]+) A at 2:1 against 2\.8 A" % (o["key"], o["hi"]), "L4-E6's B-4 line")
        if ["%.2f" % v for v in o["lin"]] != list(m.groups()):
            refuse(4, "r11_dep.py's scaling as rebuilt here does not print L4-E6's B-4 line at %s mOhm" % o["key"])
    R["can_k"] = can_k
    rating = mk["rip"]
    # the front end's fSW band: p.6's row at RT 40 k carried to the drawn RT by Equation 5 (INFERRED)
    rt = si(G["rt"], "")
    fsw0 = 1.0 / (rt * 116e-12 + 190e-9)
    fsw_lo, fsw_hi = fsw0 * mk["fsw_row"][0] / mk["fsw_row"][1], fsw0 * mk["fsw_row"][2] / mk["fsw_row"][1]
    R["fsw"] = (fsw0, fsw_lo, fsw_hi)
    lin = lambda a, b, n: [a + (b - a) * i / (n - 1) for i in range(n)]
    fsws = lin(fsw_lo, fsw_hi, grid["n_fsw"])
    fch_both = lin(mk["f400"][0], mk["f400"][2], grid["n_fch"]) + lin(mk["f800"][0], mk["f800"][2], grid["n_fch"])
    vbats = lin(grid["vbat"][0], grid["vbat"][1], grid["n_vbat"])
    if abs(grid["vbat"][1] - G["rails"]["VBAT"]["v_work"]) > 1e-9:
        refuse(3, "the record's VBAT top is not the VBAT rail's v_work")
    vout = G["rails"]["VBUS20"]["volts"]
    l1, l2 = si(G["lval"], "H"), si(G["one"]["L2"][3], "H")
    r11_drawn, r16 = si(G["isns"] + "Ohm", "Ohm"), si(G["one"]["R16"][1], "Ohm")
    hf = [(si(G["one"]["C190"][1], ""), 0.020, 0.5e-9), (si(G["one"]["C191"][1], ""), 0.050, 0.5e-9)]   # ESR, ESL: ASSUMPTION (the predecessor's)
    drawn = (len(G["bulk"]), len(G["vbus_cer"]) + len(G["ch_in"]), len(G["cout_pre"]))
    R.update(fsws=fsws, fch_both=fch_both, vbats=vbats, vout=vout, l1=l1, l2=l2, r11_drawn=r11_drawn, r16=r16, hf=hf, drawn=drawn, rating=rating)
    vins = grid["vins"]
    # ---------------------------------------------------------------- 4. validation
    Mv = Model(vout, l1, rec["l2_old"], vins, fsws, vbats, fch_both)
    wv = [Mv.weights(5.7), Mv.weights(5.0)]
    # the model's own totals against SNVSAI1D Equation 19 and SLUSE66A Equation 4 at 9 V, 5.7 A, a 10 V pack
    w9, eq19 = Mv.fe(9.0, fsw0, 5.7)
    wc, eq4 = Mv.ch(10.0, mk["f400"][1], 5.7)
    R["totals"] = (math.sqrt(sum(w9)), eq19, math.sqrt(sum(wc)), eq4)
    # the re-review's point: one evaluation; the record does not state its damping corners, so all of them are read
    p = rec["point"]
    Mp = Model(vout, l1, rec["l2_old"], [p["vin"]], [fsw_hi], [p["vbat"]], [p["fch"] * 1e3])
    wp = Mp.weights(p["iout"])
    bp = dict(bands)
    bp.update(esl_b=[p["esl"] * 1e-9], cer_c=[p["cer"] * 1e-6], cb_k=[p["ck"]])
    pts = []
    for ier, il, ir, i16 in itertools.product(range(3), range(len(bands["cer_esl"])), range(2), range(2)):
        nd = Node(Mp, bp, rec["second_bank"], r11_drawn, r16, 1.0, hf)
        pts.append((math.sqrt(exact(nd.vectors((0, 0, 0, ier, il, ir, i16, 0), ("odd",))["odd"], wp)[0]), (ier, il, ir, i16)))
    pts.sort(reverse=True)
    near = [x for x in pts if abs(x[0] - p["value"]) <= TOL_POINT]
    R["point"] = dict(pts=pts, near=near, fsw=fsw_hi)
    # the dense runs
    V = {}
    for name, bank in (("third", drawn), ("second", rec["second_bank"])):
        for s in (1.0, 1.5, 2.0):
            if name == "second" and s == 1.5:
                continue
            mets = ("odd", "sib", "cerv", "cero") if (name == "third" and s == 1.0) else ("odd", "sib")
            nd = Node(Mv, bands, bank, r11_drawn, r16, s, hf)
            V[(name, s)] = search(nd, wv, mets)
    R["V"] = V
    rows = []
    for name in ("third", "second"):
        for (s, i), want in sorted(rec[name].items(), key=lambda kv: (kv[0][1] != 5.7, kv[0][0])):
            got = math.sqrt(worst_can(V[(name, s)], 0 if i == 5.7 else 1)["ms"])
            rows.append(dict(name=name, s=s, i=i, want=want, got=got, ok=abs(got - want) <= TOL_DENSE))
    rows.append(dict(name="point", s=1.0, i=p["iout"], want=p["value"], got=near[0][0] if near else pts[0][0], ok=len(near) == 1))
    R["vrows"] = rows
    # the second fix-up's node enumerated in full: the record's count of sets over the rating, and the full grid's maximum
    nd = Node(Mv, bands, rec["second_bank"], r11_drawn, r16, 1.0, hf)
    search_max = worst_can(V[("second", 1.0)], 0)["ms"]
    over, full_max, nset = 0, search_max, 0
    thr = rating ** 2
    for ic, il, ir, i16 in itertools.product(range(nd.dims["ic"]), range(nd.dims["il"]), range(nd.dims["ir"]), range(nd.dims["i16"])):
        for ie, icb, ier in itertools.product(range(nd.dims["ie"]), range(nd.dims["icb"]), range(nd.dims["ier"])):
            vec = nd.vectors((ie, ic, icb, ier, il, ir, i16, 0), ("odd",))["odd"]
            nset += 1
            if bound(vec, wv[0]) > min(thr, full_max):
                e = exact(vec, wv[0])[0]
                over += e > thr
                full_max = max(full_max, e)
    R["count"] = dict(over=over, n=nset, full_max=math.sqrt(full_max), above_search=full_max > search_max)
    # the loop
    lcfg = dict(fsw=(fsw0, fsw_lo, fsw_hi), gm=mk["gm"], ro=mk["ro"], acs=mk["acs"], L=l1, vout=mk["vref"][1] * (1 + si(G["rfb_top"], "") / si(G["rfb_bot"], "")),
                kfb=si(G["rfb_bot"], "") / (si(G["rfb_top"], "") + si(G["rfb_bot"], "")), modes=[("boost", 9.0), ("buck", 36.0), ("buck", 24.0)],
                iouts=[rec["loop_stage"]["iout"], 0.25], cl0=rec["loop_stage"]["cl0"], ncer0=rec["loop_stage"]["ncer0"], esr_l=0.0004,
                c_can=mk["c_can"], esr_can=mk["esr_can"], p_bound=rec["loop_stage"]["p"])
    comp = tuple(si(v, u) for (v, _l), u in zip(G["comp"], ("", "", "")))
    rcs_drawn = si(G["rcs"] + "Ohm", "Ohm")
    ncer_drawn = sum(drawn[1:])
    lv = loop_eval(lcfg, drawn[0], ncer_drawn, rcs_drawn, *comp)
    lw = loop_eval(lcfg, drawn[0], ncer_drawn, rcs_drawn, *comp, qs=rec["wide"]["q"], lks=rec["wide"]["lk"])
    lrows = [(k, rec["loop"][k], lv[k], TOL_LOOP[k]) for k in ("pm", "gm", "mm", "fc_lo", "fc_hi", "z")] + \
            [("wide " + k, rec["loop_wide"][k], lw[k], TOL_LOOP[k]) for k in ("pm", "gm", "mm")]
    R.update(lcfg=lcfg, comp=comp, rcs_drawn=rcs_drawn, loop_drawn=(lv, lw), lrows=lrows)
    R["consistent"] = all(r["ok"] for r in rows) and all(abs(g - w) <= t for _k, w, g, t in lrows)
    # ---------------------------------------------------------------- 4b. the derivation's own convergence: finer source grids, more harmonics
    rows_ch = [(mk["f400"][0], mk["f400"][2]), (mk["f800"][0], mk["f800"][2])]
    Mvf = fine_model(Mv, rows_ch)
    Mvh = Model(vout, l1, rec["l2_old"], vins, fsws, vbats, fch_both, nh=FINE["nh"])
    CV = {}
    for (s_, ci, m_) in ((1.0, 0, "odd"), (1.5, 0, "odd"), (2.0, 0, "odd"), (1.0, 1, "odd"), (1.5, 1, "odd"), (2.0, 1, "odd"), (1.0, 0, "cerv"), (1.0, 0, "cero")):
        r_ = V[("third", s_)][(m_, ci)]
        mkn = (lambda sp: (lambda mm: Node(mm, bands, drawn, r11_drawn, r16, sp, hf)))(s_)
        i_ = wv[ci]["iout"]
        first, conv = converge(mkn, Mvf, r_["set"], m_, i_)
        nh2 = exact(mkn(Mvh).vectors(r_["set"], (m_,))[m_], Mvh.weights(i_))[0]
        CV[(s_, ci, m_)] = dict(base=r_["ms"], fine_at=first, conv=conv, nh2=nh2)
    R["CV"] = CV
    Mvx = fine_model(Mv, rows_ch, FINER)
    R["CV2"] = {k: math.sqrt(exact(Node(Mvx, bands, drawn, r11_drawn, r16, k[0], hf).vectors(CV[k]["conv"][1], (k[2],))[k[2]], Mvx.weights(wv[k[1]]["iout"]))[0])
                for k in ((1.0, 0, "odd"), (2.0, 0, "odd"), (1.0, 0, "cerv"))}
    # ---------------------------------------------------------------- 5. the drawn bank at the highest permitted currents
    Me = Model(vout, l1, l2, vins, fsws, vbats, fch_both)
    E = {}
    for o in out:
        we = [Me.weights(o["hi"])]
        for s in (1.0, 1.5, 2.0):
            nd = Node(Me, bands, drawn, o["r11"], r16, s, hf)
            E[(o["key"], s)] = search(nd, we, ("odd", "sib", "cerv", "cero") if s == 1.0 else ("odd", "sib"))
    R["E"] = E
    Mef0 = fine_model(Me, [(mk["f400"][0], mk["f400"][2]), (mk["f800"][0], mk["f800"][2])])
    EC = {}
    for o in out:
        for s in (1.0, 1.5, 2.0):
            w_ = worst_can(E[(o["key"], s)])
            m_ = "odd" if w_ is E[(o["key"], s)][("odd", 0)] else "sib"
            mkn = (lambda r11x, spx: (lambda mm: Node(mm, bands, drawn, r11x, r16, spx, hf)))(o["r11"], s)
            EC[(o["key"], s)] = max(math.sqrt(w_["ms"]), math.sqrt(converge(mkn, Mef0, w_["set"], m_, o["hi"])[1][0]))
    R["EC"] = EC
    # what moves the drawn bank off r11_dep.py's scaling: the network of the record (L2 3.3 uH, R11 10 mOhm), then L2 4.7 uH
    o8 = out[0]
    D = {}
    for tag, l2x, r11x in (("record", rec["l2_old"], r11_drawn), ("L2", l2, r11_drawn)):
        Mx = Model(vout, l1, l2x, vins, fsws, vbats, fch_both)
        for s in (1.0, 2.0):
            D[(tag, s)] = math.sqrt(worst_can(search(Node(Mx, bands, drawn, r11x, r16, s, hf), [Mx.weights(o8["hi"])], ("odd", "sib"), slice_check=False))["ms"])
    # the 400 kHz row alone (PWM_FREQ's power-on value), the drawn bank at 8 mOhm
    M4 = Model(vout, l1, l2, vins, fsws, vbats, fch_both[:grid["n_fch"]])
    for s in (1.0, 2.0):
        D[("400", s)] = math.sqrt(worst_can(search(Node(M4, bands, drawn, o8["r11"], r16, s, hf), [M4.weights(o8["hi"])], ("odd", "sib"), slice_check=False))["ms"])
    R["D"] = D
    # ---------------------------------------------------------------- 6. the re-size (on the sharing basis; decided on finer grids)
    Mef = fine_model(Me, rows_ch)
    Md = fine_model(Me, rows_ch, DECIDE)
    lay = dict(sib_dl=LAYOUT[0], sib_dr=LAYOUT[1])

    def decide(bank, o, basis, grid=None):
        """the bank at every spread: a full search (on the decision grids at the binding 2:1 spread, on the record's grids at the
        others), then each spread's worst can converged on FINE"""
        outc = {}
        for sp in (1.0, 1.5, 2.0):
            g_ = grid or (Md if sp == 2.0 else Me)
            res = search(Node(g_, bands, bank, o["r11"], r16, sp, hf, **basis), [g_.weights(o["hi"])], ("odd", "sib"))
            w_ = worst_can(res)
            m_ = "odd" if w_ is res[("odd", 0)] else "sib"
            mkn = (lambda bk, r11x, spx: (lambda mm: Node(mm, bands, bk, r11x, r16, spx, hf, **basis)))(bank, o["r11"], sp)
            _f, cv = converge(mkn, Mef, w_["set"], m_, o["hi"])
            outc[sp] = dict(res=res, search=math.sqrt(w_["ms"]), conv=math.sqrt(cv[0]), fig=max(math.sqrt(w_["ms"]), math.sqrt(cv[0])), metric=m_, cv=cv)
        return outc
    scr, dec_all, chosen = {}, {}, {}
    for o, groups in ((out[0], CANDIDATES_8), (out[1], CANDIDATES_7)):
        lim = rating - MARGIN_PER_A * o["hi"]
        we = [Me.weights(o["hi"])]
        pick = None
        for grp, banks in groups:
            for bank in banks:
                scr[(o["key"], bank)] = math.sqrt(worst_can(search(Node(Me, bands, bank, o["r11"], r16, 2.0, hf, **lay), we, ("odd",), slice_check=False))["ms"])
            for bank in banks:
                if scr[(o["key"], bank)] <= lim:      # the 7 mOhm contingency on the record's grids, converged (runtime on this host)
                    dec_all[(o["key"], bank)] = decide(bank, o, lay, grid=None if o["key"] == "8" else Me)
            ok = [b_ for b_ in banks if (o["key"], b_) in dec_all and all(x["fig"] <= lim for x in dec_all[(o["key"], b_)].values())]
            if ok:
                bank = min(ok, key=lambda b_: max(x["fig"] for x in dec_all[(o["key"], b_)].values()))
                pick = dict(bank=bank, group=grp, conv=dec_all[(o["key"], bank)], lim=lim)
                pick["full"] = {sp: pick["conv"][sp]["res"] for sp in (1.0, 1.5, 2.0)}
                ce = search(Node(Me, bands, bank, o["r11"], r16, 1.0, hf, **lay), we, ("cerv", "cero"))
                pick["cer"] = {m_: max(math.sqrt(ce[(m_, 0)]["ms"]), math.sqrt(converge(
                    (lambda bk, r11x: (lambda mm: Node(mm, bands, bk, r11x, r16, 1.0, hf, **lay)))(bank, o["r11"]), Mef, ce[(m_, 0)]["set"], m_, o["hi"])[1][0]))
                               for m_ in ("cerv", "cero")}
                break
        if pick is None:
            refuse(4, "no candidate bank meets the rule at %s mOhm" % o["key"])
        chosen[o["key"]] = pick
    R["scr"], R["dec_all"] = scr, dec_all
    # the lumped node (no layout mismatch), as the lost analysis judged it: the smallest +1-can banks
    LU = {}
    LU["screen"] = math.sqrt(worst_can(search(Node(Me, bands, (7, 18, 3), out[0]["r11"], r16, 2.0, hf), [Me.weights(out[0]["hi"])], ("odd",), slice_check=False))["ms"])
    LU[(7, 21, 3)] = decide((7, 21, 3), out[0], {}, grid=Me)
    R["LU"] = LU
    # sensitivity, not gating: VIN only where the average limit sets the fault current at both outcomes once L4-E6's R12 is in
    bnd = [float(need(t6, r"above ([\d.]+) V the average limit, not the peak limit, sets the fault current; at 9 V the output is held to ([\d.]+) A", "L4-E6's boundary").group(i))
           for i in (1, 2)]
    bnd7 = float(re.findall(r"above ([\d.]+) V the average limit, not the peak limit, sets the fault current", t6)[-1])
    Mh = Model(vout, l1, l2, [v for v in vins if v > max(bnd[0], bnd7)], fsws, vbats, fch_both)
    H = {}
    for tag, bank, basis in (("drawn", drawn, {}), ("8", chosen["8"]["bank"], lay)):
        for sp in (1.0, 2.0):
            H[(tag, sp)] = math.sqrt(worst_can(search(Node(Mh, bands, bank, out[0]["r11"], r16, sp, hf, **basis), [Mh.weights(out[0]["hi"])], ("odd", "sib"), slice_check=False))["ms"])
    at9 = [worst_can(r_)["fe"][1][0] == 0 for r_ in list(E.values()) + [chosen[k]["full"][sp] for k in ("8", "7") for sp in (1.0, 1.5, 2.0)]]
    R["H"] = dict(vals=H, vins=Mh.vins, b8=bnd[0], b7=bnd7, i9=bnd[1], all9=all(at9), n9=(sum(at9), len(at9)))
    # the 8 mOhm bank at 7 mOhm, all spreads (what V-A07's failure would leave)
    o7 = out[1]
    b8 = chosen["8"]["bank"]
    chosen["8_at_7"] = {s: math.sqrt(worst_can(search(Node(Me, bands, b8, o7["r11"], r16, s, hf, **lay), [Me.weights(o7["hi"])], ("odd", "sib"), slice_check=False))["ms"])
                        for s in (1.0, 1.5, 2.0)}
    R["chosen"] = chosen
    # ---------------------------------------------------------------- 6b. the selected (8 mOhm) bank: its loss, the rating at frequency and temperature, the stresses
    o8 = out[0]
    we8 = [Me.weights(o8["hi"])]
    PD = {}
    for sp in (1.0, 1.5, 2.0):
        r_ = search(Node(Me, bands, b8, o8["r11"], r16, sp, hf, **lay), we8, ("podd", "psib"), slice_check=False)
        best = max((r_[(m_, 0)] for m_ in ("podd", "psib")), key=lambda x: x["ms"])
        m_ = "podd" if best is r_[("podd", 0)] else "psib"
        mkn = (lambda spx: (lambda mm: Node(mm, bands, b8, o8["r11"], r16, spx, hf, **lay)))(sp)
        PD[sp] = max(best["ms"], converge(mkn, Mef, best["set"], m_, o8["hi"])[1][0])
    p_rated = rating ** 2 * mk["esr_can"]
    env = yaml.safe_load(open(os.path.join(TOP, ENVELOPE), encoding="utf-8"))
    t_air = max(env["worst_inside_air_c"]["lid_open"], env["worst_inside_air_c"]["lid_closed"])
    t_local = float(need(t6, r"so the qualifying temperature is (\d+) C", "L4-E6's L1 qualifying temperature").group(1))

    def life(t):
        return min(mk["life_h"] * 2 ** ((mk["t_cat"] - t) / 10.0), mk["life_cap_y"] * 8760.0)
    fmin = min(min(Me.fsws), min(fch_both))
    corr_at = [f_ for f_, _c in mk["corr"] if f_ <= fmin][-1]
    corr_min = min(c_ for f_, c_ in mk["corr"] if f_ >= corr_at)
    R["sel"] = dict(PD=PD, p_rated=p_rated, t_air=t_air, t_local=t_local, life=(life(t_air), life(t_local)), fmin=fmin, corr_at=corr_at, corr_min=corr_min)
    # the stresses (not the decision's basis; each says whether it would flip the selection)
    SX = {}
    geo = dict(sib_dl=GEOM[0], sib_dr=GEOM[1])
    for sp in (1.0, 2.0):
        SX[("geometry", sp)] = math.sqrt(worst_can(search(Node(Me, bands, b8, o8["r11"], r16, sp, hf, **geo), we8, ("odd", "sib"), slice_check=False))["ms"])
    SX["robust"] = None
    for bank in ((b8[0] + 1, b8[1], b8[2]), (b8[0] + 1, b8[1] + 3, b8[2]), (b8[0] + 2, b8[1], b8[2])):
        if math.sqrt(worst_can(search(Node(Me, bands, bank, o8["r11"], r16, 2.0, hf, **geo), we8, ("odd",), slice_check=False))["ms"]) > rating - MARGIN_PER_A * o8["hi"]:
            continue
        vals = [math.sqrt(worst_can(search(Node(Me, bands, bank, o8["r11"], r16, sp, hf, **geo), we8, ("odd", "sib"), slice_check=False))["ms"]) for sp in (1.0, 1.5, 2.0)]
        if max(vals) <= rating - MARGIN_PER_A * o8["hi"]:
            SX["robust"] = (bank, vals)
            break
    b33 = dict(bands)
    b33["esr_k"] = [bands["esr_k"][0]]
    SX[("3.3", 0)] = math.sqrt(worst_can(search(Node(Me, b33, b8, o8["r11"], r16, 1.0 / bands["esr_k"][0], hf, **lay), we8, ("odd", "sib"), slice_check=False))["ms"])
    SX[("3.3 drawn", 0)] = math.sqrt(worst_can(search(Node(Me, b33, drawn, o8["r11"], r16, 1.0 / bands["esr_k"][0], hf), we8, ("odd", "sib"), slice_check=False))["ms"])
    bx = dict(bands)
    bx["esl_b"] = [(STRESS["esl_lo"] + 0.05 * i) * 1e-9 for i in range(int(round((bands["esl_b"][-1] * 1e9 - STRESS["esl_lo"]) / 0.05)) + 1)]
    bx["cer_c"] = [(STRESS["cer_lo"] + 0.125 * i) * 1e-6 for i in range(int(round((bands["cer_c"][-1] * 1e6 - STRESS["cer_lo"]) / 0.125)) + 1)]
    for sp in (1.0, 2.0):
        r_ = worst_can(search(Node(Me, bx, b8, o8["r11"], r16, sp, hf, **lay), we8, ("odd", "sib"), slice_check=False))
        SX[("bands", sp)] = (math.sqrt(r_["ms"]), bx["esl_b"][r_["set"][0]] * 1e9, bx["cer_c"][r_["set"][1]] * 1e6)
    R["SX"] = SX
    # ---------------------------------------------------------------- 7. the loop on the re-sized banks, R12 as drawn and at L4-E6's 12 mOhm
    r12_e6 = 0.012
    L7 = {}
    for key in ("8", "7"):
        bk = chosen[key]["bank"]
        for rcs in (rcs_drawn, r12_e6):
            L7[(key, rcs)] = (loop_eval(lcfg, bk[0], bk[1] + bk[2], rcs, *comp),
                              loop_eval(lcfg, bk[0], bk[1] + bk[2], rcs, *comp, qs=rec["wide"]["q"], lks=rec["wide"]["lk"]))
    L7[("drawn", r12_e6)] = (loop_eval(lcfg, drawn[0], ncer_drawn, r12_e6, *comp),
                             loop_eval(lcfg, drawn[0], ncer_drawn, r12_e6, *comp, qs=rec["wide"]["q"], lks=rec["wide"]["lk"]))
    R["L7"] = L7
    R["r12_e6"] = r12_e6
    # ---------------------------------------------------------------- 8. what else the bank's capacitance moves (first order, INFERRED)
    ss, ring, bl = rec["ss"], rec["ring"], rec["bleed"]
    div = 1 + si(G["rfb_top"], "") * 1.01 / (si(G["rfb_bot"], "") * 0.99)       # the divider at its 1 % corner (the record's stack)
    css = si(G["css"][0], "") * ss["css_k"]

    def cmax(bank):
        return bank[0] * mk["c_can"] * ss["ck"] + (bank[1] + bank[2]) * 10e-6 * rec["node_max"][2]

    def cmin(bank):
        return bank[0] * mk["c_can"] * 0.8 + (bank[1] + bank[2]) * bands["cer_c"][0]

    def ramp(bank):
        i = cmax(bank) * div * mk["iss"][2] / css + rec["bias"]
        return [100 * i * ss["vbus"] / ss["eta"] / v / rec["entry"] for v in (9.0, 12.0, 13.8)]

    def bleed(bank):
        tau = (bl["r"][0] * cmin(bank), bl["r"][1] * cmax(bank))
        return tau, (tau[0] * math.log(rec["bank_range"][0] / rec["release"][2]), tau[1] * math.log(bl["v"] / rec["release"][0]))

    def ringf(bank):
        c = cmax(bank)
        return ring["v"] * math.sqrt(c / (l1 * ring["lk"])), 0.5 * c * ring["v"] ** 2 * 1e3
    cons_banks = [("drawn", drawn), ("8", chosen["8"]["bank"]), ("7", chosen["7"]["bank"])]
    if R["SX"]["robust"]:
        cons_banks.append(("robust", R["SX"]["robust"][0]))
    R["cons"] = {tag: dict(bank=b, cmax=cmax(b), cmin=cmin(b), ramp=ramp(b), bleed=bleed(b), ring=ringf(b)) for tag, b in cons_banks}
    R["cons_ok"] = (all(abs(round(x, 1) - y) < 1e-9 for x, y in zip(R["cons"]["drawn"]["ramp"], ss["pct"]))
                    and abs(round(R["cons"]["drawn"]["ring"][0], 1) - ring["pk"]) < 1e-9 and abs(round(R["cons"]["drawn"]["ring"][1], 2) - ring["mj"]) < 1e-9
                    and abs(round(R["cons"]["drawn"]["cmax"] * 1e3, 2) - rec["node_max"][0]) < 1e-9
                    and abs(round(R["cons"]["drawn"]["bleed"][0][1], 2) - bl["tau"][1]) < 1e-9 and abs(round(R["cons"]["drawn"]["bleed"][0][0], 2) - bl["tau"][0]) < 1e-9)
    # ---------------------------------------------------------------- 9. predicates
    o8, o7 = out
    e8 = {s: EC[("8", s)] for s in (1.0, 1.5, 2.0)}
    e7 = {s: EC[("7", s)] for s in (1.0, 1.5, 2.0)}
    c8 = {s: chosen["8"]["conv"][s]["fig"] for s in (1.0, 1.5, 2.0)}
    c7 = {s: chosen["7"]["conv"][s]["fig"] for s in (1.0, 1.5, 2.0)}
    cv_can = [(k, math.sqrt(v["conv"][0]) - math.sqrt(v["base"]), wv[k[1]]["iout"]) for k, v in CV.items() if k[2] == "odd"]
    R["cv_can"] = cv_can
    R.update(e8=e8, e7=e7, c8=c8, c7=c7)
    rounds = [v["rounds"] for res in list(V.values()) + list(E.values()) + [ch_["full"][s_] for ch_ in (chosen["8"], chosen["7"]) for s_ in (1.0, 1.5, 2.0)]
              for v in res.values()]
    R["rounds"] = (sum(1 for x in rounds if x), len(rounds), sum(rounds))
    P = [
        ("consistency: the derivation meets every recorded dense can figure within %.2f A and the re-review's point within %.4f A" % (TOL_DENSE, TOL_POINT),
         all(r["ok"] for r in R["vrows"])),
        ("consistency: the loop model meets the recorded margins within the stated tolerances", all(abs(g - w) <= t for _k, w, g, t in lrows)),
        ("convergence: on the finer source grids every can figure of the drawn node moves by less than the rule's margin",
         all(abs(dv) <= MARGIN_PER_A * i_ for _k, dv, i_ in cv_can)),
        ("the full enumeration of the second fix-up's node equals the search's maximum and counts the record's sets over the rating",
         not R["count"]["above_search"] and (over, nset) == rec["second_count"]),
        ("the drawn bank does NOT meet 2.8 A at the 2:1 spread at either R11 outcome on the rebuild", e8[2.0] > rating and e7[2.0] > rating),
        ("no ceramics-only change (six cans) meets 2.8 A at the 2:1 spread at 8 mOhm", all(scr[("8", b)] > rating for _g, bs in CANDIDATES_8 for b in bs if b[0] == 6)),
        ("the chosen 8 mOhm bank meets 2.8 A less the margin at every spread on the converged figures, at %.3f A" % o8["hi"], all(v <= chosen["8"]["lim"] for v in c8.values())),
        ("the chosen 7 mOhm bank meets 2.8 A less the margin at every spread on the converged figures, at %.3f A" % o7["hi"], all(v <= chosen["7"]["lim"] for v in c7.values())),
        ("the rating applies unmodified: every harmonic at or above %.0f kHz, where the sheet's correction is %.2f; each can's loss under the rated"
         " condition's (rating squared times the maximum ESR), so its rise is under the rated one" % (R["sel"]["fmin"] / 1e3, R["sel"]["corr_min"]),
         R["sel"]["corr_min"] == 1.0 and all(v <= R["sel"]["p_rated"] for v in R["sel"]["PD"].values())),
        ("the chosen banks keep one can part number and at least the drawn three ceramics on FE_OUT (SNVSAI1D 9.1's division)",
         all(chosen[k]["bank"][2] >= drawn[2] for k in ("8", "7"))),
        ("the loop keeps PM >= 50 deg, GM >= 10 dB, |1+T| >= 0.5, every crossover under its ceilings and the impedance under its bound on both "
         "re-sized banks at R12 5 and 12 mOhm, default and widened bands",
         all(x["pm"] >= 50 and x["gm"] >= 10 and x["mm"] >= 0.5 and x["ceil_ok"] and x["all_cross"] and x["z_ratio"] <= 1.0 for v in L7.values() for x in v)),
        ("the first-order consequences reproduce the generator's recorded soft-start draw, bleed tau, node maximum and restart ring", R["cons_ok"]),
    ]
    R["preds"] = P
    if not all(ok for _p, ok in P):
        refuse(4, "a predicate failed: %s" % [p_ for p_, ok in P if not ok])
    return R


# ============================================================================================================== render
def corner_text(R, res, model_fsws, model_fchs):
    b = R["bands"]
    ie, ic, icb, ier, il, ir, i16, i11 = res["set"]
    (fe, (jv, jf)), (ch, (jb, jc)) = res["fe"], res["ch"]
    return ("ESL %.2f nH, ceramic %.3f uF, can C x%.1f, ESR x%.1f, ceramic ESL %.2f nH / ESR %.0f mOhm, L16 %.0f nH, L11 %.0f nH; VIN %.1f V, fsw %.1f kHz,"
            " VBAT %.2f V, fch %.0f kHz; the front end's share %.2f A, the charger's %.2f A" % (
                b["esl_b"][ie] * 1e9, b["cer_c"][ic] * 1e6, b["cb_k"][icb], b["esr_k"][ier], b["cer_esl"][il] * 1e9, b["cer_esr"][ir] * 1e3,
                b["l16"][i16] * 1e9, b["l11"][i11] * 1e9, R["grid"]["vins"][jv], model_fsws[jf] / 1e3, R["vbats"][jb], model_fchs[jc] / 1e3,
                math.sqrt(fe), math.sqrt(ch)))


def render(R):
    out = []
    P = out.append
    G, rec, mk, b, grid = R["gen"], R["rec"], R["mk"], R["bands"], R["grid"]
    o8, o7 = R["outcomes"]
    rating = R["rating"]
    P("L4-E8: BOARD A'S VBUS20 BULK BANK RE-SIZED ON A REBUILT DENSE NODE ANALYSIS (ripple_dense.py, MESHSAT-1357, 1 October 2026).")
    P("PROTOTYPE DESIGN: nothing bought, built, powered or measured; no generator, registry, rendered page or L4-E4 to L4-E7 record edited.")
    P("Labels: MAKER, NETLIST, GENERATOR, RECORD, INFERRED, ASSUMPTION, SESSION, MODELED, INCONCLUSIVE.")
    P("")
    P("0. INPUTS AND REPRODUCTIONS")
    for rel, want in PINS.items():
        P("   %-48s sha256 %s (pinned)" % (rel, want[:16]))
    P("   (the two recovered drafts are pinned as cited inputs; their code is not run here)")
    P("   L4-E4's l4e4_limits.compute(), run in this process (it reproduces r11_dep.out in a child and prints nothing): band(r)[2], the")
    P("     highest permitted current, which l4e6_fault_handling.py takes as o['hi'] for its two R11 values (its source parsed):")
    for o in R["outcomes"]:
        P("     R11 %s mOhm (%s): %.4f A; L4-E6 prints %.3f A: equal" % (o["key"], o["code"], o["hi"], o["hi"]))
    P("   r11_dep.py's linear scaling rebuilt from gen_sch_a.py's recorded figures (the larger of the 5.7 A and 5.0 A points per ampere):")
    P("     %.4f / %.4f / %.4f A per A (matched / 1.5:1 / 2:1); it prints L4-E6's B-4 lines:" % tuple(R["can_k"]))
    for o in R["outcomes"]:
        P("     R11 %s mOhm, %.3f A: %.2f / %.2f / %.2f A (L4-E6: the same)" % ((o["key"], o["hi"]) + tuple(o["lin"])))
    P("")
    P("1. THE NODE AS THE GENERATOR DRAWS IT (GENERATOR: gen_sch_a.py parsed; NETLIST: %s agrees)" % NET_A)
    P("   cans on VBUS20: %d x '%s' (bulk=%s, bulk_part %s)" % (len(G["bulk"]), G["can_value"], ", ".join(G["bulk"]), G["bulk_part"]))
    P("   ceramics on VBUS20: %d x '%s' (%s; the charger's %s)" % (R["drawn"][1], G["cout"], ", ".join(G["vbus_cer"]), ", ".join(r for r, _v in G["ch_in"])))
    P("   ceramics on FE_OUT, before R11: %d (cout_pre %s)" % (R["drawn"][2], ", ".join(G["cout_pre"])))
    P("   R11 %.0f mOhm (FE_OUT to VBUS20), R16 %.0f mOhm (VBUS20 to CH_ACN); CH_ACN: C190 '%s', C191 '%s'; L1 %.1f uH, L2 %.1f uH; RT '%s'" % (
        R["r11_drawn"] * 1e3, R["r16"] * 1e3, G["one"]["C190"][1], G["one"]["C191"][1], R["l1"] * 1e6, R["l2"] * 1e6, G["rt"]))
    P("   VBUS20 %.1f V (its rail declaration); compensation Rc1 %s, Cc1 %s, Cc2 %s; R12 '%s' (the lm5176() default); CSS '%s'" % (
        R["vout"], G["comp"][0][0], G["comp"][1][0], G["comp"][2][0], G["rcs"], G["css"][0]))
    for f in R["net"]["facts"]:
        P("   NETLIST: %s: holds" % f)
    P("   not modelled (%d parts on VBUS20 in all): %s, under 0.01 %% of the ceramic bank" % (R["net"]["n_vb"], ", ".join("%s '%s'" % x for x in R["net"]["other_c"])))
    P("")
    P("2. THE MAKERS' ROWS")
    P("   MAKER Panasonic ZK series sheet (%s, 01-Apr-22): EEHZK1V331P %.0f uF +-20 %% (p.1), ESR %.0f mOhm max at 100 kHz and +20 C," % (EEHZK, mk["c_can"] * 1e6, mk["esr_can"] * 1e3))
    P("     ripple %.1f A rms at 100 kHz and +125 C (p.2); frequency correction %s and %s from 100 to 500 kHz and above (p.2), so every" % (rating, *("%.2f" % v for v in mk["corr_hi"])))
    P("     harmonic here (the lowest %.0f kHz) counts at the full rating; ESR after endurance at most 200 %% of the initial limit (p.1);" % (R["fsw"][1] / 1e3))
    P("     parallel parts: 'use capacitors with the same part number' (p.7)")
    P("   MAKER TI SNVSAI1D rev. D (%s): fSW(1) %.0f / %.0f / %.0f kHz at RT %.0f k (p.6), Equation 5's 116 pF and 190 ns (p.17)," % (
        LM5176, mk["fsw_row"][0] / 1e3, mk["fsw_row"][1] / 1e3, mk["fsw_row"][2] / 1e3, mk["rt_row"] / 1e3))
    P("     so RT %s sets %.2f kHz and the row carried there is %.2f to %.2f kHz (INFERRED); gmEA %.2f mS, ROUT %.0f MOhm, VREF %.3f V," % (
        G["rt"].split()[0], R["fsw"][0] / 1e3, R["fsw"][1] / 1e3, R["fsw"][2] / 1e3, mk["gm"] * 1e3, mk["ro"] / 1e6, mk["vref"][1]))
    P("     ISS %.2f / %.2f / %.2f uA (p.6); ACS %.0f (p.24, Equation 26); Equation 19, ICOUT(RMS) (p.23); 9.1, 'divide the overall" % (
        mk["iss"][0] * 1e6, mk["iss"][1] * 1e6, mk["iss"][2] * 1e6, mk["acs"]))
    P("     capacitor (CIN or COUT) between the two sides of the sense resistor' (p.30); the loop's Equations 38 to 44 (p.27)")
    P("   MAKER TI SLUSE66A (%s): FSW %.0f / %.0f / %.0f kHz (Reg0x01[1] = 0) and %.0f / %.0f / %.0f kHz (= 1) (p.16); Equation 4," % (
        BQ25731, *(v / 1e3 for v in mk["f800"]), *(v / 1e3 for v in mk["f400"])))
    P("     ICIN = ICHG x sqrt(D (1 - D)), the input capacitor 'in front of RAC' (p.85); 4.7 uH 'recommended for 400 kHz' (p.27, Table")
    P("     9-4); PWM_FREQ is R/W, 400 kHz at power-on (p.43): a host can write 800 kHz, so both bands are judged (SESSION)")
    tot = R["totals"]
    P("   the model's own totals at 9 V and 5.7 A: the front end's %.2f A against Equation 19's %.2f A; the charger's %.2f A against" % (tot[0], tot[1], tot[2]))
    P("     Equation 4's %.2f A at a 10 V pack (the waveform's own rms with its ripple, against the equations' ripple-free forms)" % tot[3])
    P("")
    P("3. THE MODEL, ITS BANDS AND THE SEARCH")
    P("   MODELED: three nodes, FE_OUT (the front end injects), R11 + L11, VBUS20, R16 + L16, CH_ACN (the charger draws); each part")
    P("     ESR + jwESL + 1/(jwC); %d harmonics by a %d-point midpoint DFT; the FE's mean square at its worst (VIN, fsw) plus the" % (NH, NS))
    P("     charger's at its worst (VBAT, fch), per part (the two are not synchronised)")
    P("   RECORD (r4-decisions.md section 6 B3, the lost analysis's bands; each INFERRED there, no maker figure held):")
    P("     polymer ESL %.2f to %.2f nH in %d steps; ceramic effective C %.3f to %.3f uF in %d steps (the 10u 50V X7R 1210 at 20 V: no" % (
        b["esl_b"][0] * 1e9, b["esl_b"][-1] * 1e9, len(b["esl_b"]), b["cer_c"][0] * 1e6, b["cer_c"][-1] * 1e6, len(b["cer_c"])))
    P("     DC-bias curve for it is held); ceramic ESL %s nH, ESR %s mOhm; L16 %s nH; L11 %s nH (the record gives 1 to 5 nH;" % (
        " / ".join("%.2f" % (v * 1e9) for v in b["cer_esl"]), " / ".join("%.0f" % (v * 1e3) for v in b["cer_esr"]),
        " / ".join("%.0f" % (v * 1e9) for v in b["l16"]), " / ".join("%.0f" % (v * 1e9) for v in b["l11"])))
    P("     three points, ASSUMPTION, from its 332,100 sets); can C x%s (MAKER +-20 %%), ESR x%s (1.0 the sheet's maximum, 2.0 its" % (
        " / ".join("%.1f" % v for v in b["cb_k"]), " / ".join("%.1f" % v for v in b["esr_k"])))
    P("     endurance limit, 0.3 a good part, the lost analysis's least-damping corner)")
    P("   the grids: VIN_RAW %s V (RECORD, REQ-015's 9 to 36 V); fsw %d points over the carried row; VBAT %d points over %.1f to %.1f V" % (
        ", ".join("%g" % v for v in grid["vins"]), grid["n_fsw"], grid["n_vbat"], grid["vbat"][0], grid["vbat"][1]))
    P("     (RECORD; %.1f V the VBAT rail's v_work, 4S full); fch %d points over each SLUSE66A row; the spacing of fsw, VBAT, fch and L11" % (
        grid["vbat"][1], grid["n_fch"]))
    P("     even (ASSUMPTION: the record gives the counts and the ends only)")
    P("   ASSUMPTION (the predecessor's values; no maker figure held): C190 and C191 at 20 and 50 mOhm, 0.5 nH; the ceramic bank's 0.4")
    P("     mOhm and the light load 0.25 A in the loop; the loop's corners (Q 0.4 / 0.8, gm x0.8 / 1.2, cans C x0.8 / 1.2, ESR x0.3 / 2.0)")
    P("   the spread (RECORD): one can at the corner's ESR, its siblings at s times it; 'worst can' is the larger of the two")
    P("   SESSION search: stage 1 bounds every set of the coarse grid (ESL indices %s, C indices %s, every other band at all its" % (
        ",".join(str(x) for x in COARSE_ESL), ",".join(str(x) for x in COARSE_C)))
    P("     corners); stage 2 climbs the %d best-bounded sets (one per corner of the other bands) on the dense grid; stage 3 bounds the" % SEEDS)
    P("     whole dense ESL x C slice at the best and evaluates every set whose bound exceeds it (validation and evaluation runs)")
    P("")
    P("4. CONSISTENCY WITH THE RECORD (a check on the derivation, not its acceptance; tolerances fixed before the run: %.2f A on the" % TOL_DENSE)
    P("   dense figures, %.4f A on the re-review's point; the derivation's own acceptance is its convergence, section 4b)" % TOL_POINT)
    P("   | node | spread | current | recorded | derived | difference | within |")
    for r in R["vrows"]:
        lab = {"third": "drawn (third fix-up)", "second": "second fix-up", "point": "re-review's point"}[r["name"]]
        P("   | %s | %s | %.1f A | %s | %.4f A | %+.4f A | %s |" % (lab, "%g:1" % r["s"], r["i"],
                                                              ("%.3f A" % r["want"]) if r["name"] == "point" else ("%.2f A" % r["want"]),
                                                              r["got"], r["got"] - r["want"], "yes" if r["ok"] else "NO"))
    P("   the re-review's point (ESL %.1f nH, ceramic %.1f uF, C x%.1f, %.1f A, %.0f V, fsw %.1f kHz, a %.0f V pack, the charger at %.0f kHz):" % (
        rec["point"]["esl"], rec["point"]["cer"], rec["point"]["ck"], rec["point"]["iout"], rec["point"]["vin"], R["point"]["fsw"] / 1e3, rec["point"]["vbat"], rec["point"]["fch"]))
    P("     the record does not state its damping corners; of the %d (can ESR, ceramic ESL, ceramic ESR, L16), %d gives %.3f A to %.4f A:" % (
        len(R["point"]["pts"]), len(R["point"]["near"]), rec["point"]["value"], TOL_POINT))
    for v, (ier, il, ir, i16) in R["point"]["near"]:
        P("     ESR x%.1f, ceramic ESL %.2f nH, ESR %.0f mOhm, L16 %.0f nH: %.4f A (the least damping corner of each band); the next %.4f A" % (
            b["esr_k"][ier], b["cer_esl"][il] * 1e9, b["cer_esr"][ir] * 1e3, b["l16"][i16] * 1e9, v, R["point"]["pts"][1][0]))
    V = R["V"]
    t = V[("third", 1.0)]
    c1 = worst_can(t, 0)
    tc = rec["third_corner"]
    P("   the drawn node's worst can at 5.7 A, matched, rebuilt at: %s" % corner_text(R, c1, R["fsws"], R["fch_both"]))
    P("     RECORD: ESL %.1f nH, ceramic %.1f uF, VIN %.0f V, fsw %.0f kHz, VBAT %.0f V, the charger at %.0f kHz, shares %.2f and %.2f A" % (
        tc["esl"], tc["cer"], tc["vin"], tc["fsw"], tc["vbat"], tc["fch"], tc["fe"], tc["ch"]))
    c2 = worst_can(V[("third", 2.0)], 0)
    P("   at 2:1, rebuilt at: %s" % corner_text(R, c2, R["fsws"], R["fch_both"]))
    P("     RECORD: ESL %.1f nH, the charger at %.0f kHz" % (tc["esl2"], tc["fch2"]))
    c3 = worst_can(V[("second", 1.0)], 0)
    sc = rec["second_corner"]
    P("   the second fix-up's node at 5.7 A, rebuilt at: %s" % corner_text(R, c3, R["fsws"], R["fch_both"]))
    P("     RECORD: ESL %.1f nH, ceramic %.1f uF, the charger at %.0f kHz, VIN %.0f V, VBAT %.0f V" % (sc["esl"], sc["cer"], sc["fch"], sc["vin"], sc["vbat"]))
    cnt = R["count"]
    P("   the second fix-up's node ENUMERATED IN FULL (%d sets, 5.7 A, matched): %d over %.1f A (RECORD: %d of %d); its maximum %.4f A," % (
        cnt["n"], cnt["over"], rating, rec["second_count"][0], rec["second_count"][1], cnt["full_max"]))
    P("     the search's: %s" % ("the same" if not cnt["above_search"] else "BELOW IT"))
    P("   the drawn node's six runs: %d of the record's %d sets over 2.8 A in any of them (RECORD); the search's stage 3 re-climbed in" % rec["third_count"])
    P("     %d of its %d validation, evaluation and chosen-bank runs (%d round(s) in all); every maximum reported holds its whole dense" % R["rounds"])
    P("     ESL x C slice under it")
    cv, co = math.sqrt(t[("cerv", 0)]["ms"]), math.sqrt(t[("cero", 0)]["ms"])
    P("   the worst ceramic at 5.7 A, matched: VBUS20 %.2f A (RECORD %.2f A, %+.2f A: DIFFERS, reconciled in 4b), FE_OUT %.2f A (RECORD" % (
        cv, rec["ceramic"][0], cv - rec["ceramic"][0], co))
    P("     %.2f A, %+.2f A). The VBUS20 figure sits at an interior VBAT point: %s" % (
        rec["ceramic"][1], co - rec["ceramic"][1], corner_text(R, t[("cerv", 0)], R["fsws"], R["fch_both"])))
    P("     No MLCC ripple rating is held, so no ceramic figure is judged against one")
    P("   the loop (FE stage, six cans, 21 ceramics counted local, Rc1 %s, Cc1 %s, Cc2 %s, R12 %s):" % (G["comp"][0][0], G["comp"][1][0], G["comp"][2][0], G["rcs"]))
    P("   | figure | recorded | derived on the record's grid | tolerance | within |")
    for k, w, g_, tol in R["lrows"]:
        P("   | %s | %g | %.3f | %g | %s |" % (k, w, g_, tol, "yes" if abs(g_ - w) <= tol else "NO"))
    lv_, lw_ = R["loop_drawn"]
    P("   the same loop with each crossing interpolated (log |T| over log f), the derivation's figure: PM %.2f deg, GM %.2f dB, crossover" % (lv_["pm_i"], lv_["gm_i"]))
    P("     %.3f to %.3f kHz; widened PM %.2f deg, GM %.2f dB (the record's and the grid's figures are the grid point below each crossing)" % (
        lv_["fc_lo_i"], lv_["fc_hi_i"], lw_["pm_i"], lw_["gm_i"]))
    P("   CONSISTENCY: %s" % ("every can figure, the re-review's point and the loop within tolerance; the VBUS20 ceramic differs (4b)" if R["consistent"]
                             else "a figure is outside its tolerance (reconciled in 4b and the page)"))
    P("")
    P("4b. THE DERIVATION'S CONVERGENCE (the drawn node as recorded, L2 %.1f uH; each reported maximum re-taken on finer source grids," % (rec["l2_old"] * 1e6))
    P("   VBAT every %.1f V, fSW every %.0f kHz, the charger every %.0f kHz, then climbed on the dense passive grid; and with %d harmonics)" % (
        FINE["vbat"], FINE["fsw"] / 1e3, FINE["fch"] / 1e3, FINE["nh"]))
    P("   | figure | record's grids | same set, finer grids | finer grids, climbed | %d harmonics | where the climbed maximum sits |" % FINE["nh"])
    for (s_, ci, m_), v in sorted(R["CV"].items(), key=lambda kv: (kv[0][2] != "odd", kv[0][1], kv[0][0])):
        tot, st, fe_, ch_, mdl = v["conv"]
        lab = {"odd": "worst can", "cerv": "VBUS20 ceramic", "cero": "FE_OUT ceramic"}[m_]
        P("   | %s, %g:1, %.1f A | %.4f A | %.4f A | %.4f A | %.4f A | VBAT %.2f V, fch %.0f kHz, fsw %.1f kHz, ESL %.2f nH, C %.3f uF |" % (
            lab, s_, (5.7, 5.0)[ci], math.sqrt(v["base"]), math.sqrt(v["fine_at"]), math.sqrt(tot), math.sqrt(v["nh2"]),
            mdl.vbats[ch_[1][0]], mdl.fchs[ch_[1][1]] / 1e3, mdl.fsws[fe_[1][1]] / 1e3, b["esl_b"][st[0]] * 1e9, b["cer_c"][st[1]] * 1e6))
    P("   the cans' figures move by at most %.4f A on the finer grids (the rule's margin is %.4f A per A); the harmonics beyond the" % (
        max(abs(x[1]) for x in R["cv_can"]), MARGIN_PER_A))
    P("     60th add under %.4f A anywhere" % max(abs(math.sqrt(v["nh2"]) - math.sqrt(v["base"])) for v in R["CV"].values()))
    P("   the finer grids themselves converged: on VBAT every %.2f V, fSW every %.2f kHz and the charger every %.0f kHz the climbed sets" % (
        FINER["vbat"], FINER["fsw"] / 1e3, FINER["fch"] / 1e3))
    P("     read %s" % "; ".join("%s %g:1 %.4f A (%+.4f A)" % ({"odd": "worst can", "cerv": "VBUS20 ceramic"}[k[2]], k[0], v, v - math.sqrt(R["CV"][k]["conv"][0]))
                               for k, v in sorted(R["CV2"].items(), key=lambda kv: (kv[0][2] != "odd", kv[0][0]))))
    P("")
    P("5. THE DRAWN BANK AT L4-E6'S HIGHEST PERMITTED CURRENTS, ON THE REBUILD (L2 %.1f uH as drawn since S-117, R11 at each outcome in" % (R["l2"] * 1e6))
    P("   the network, both charger rows, the current at every VIN: the fault case of B-4, U3 the load)")
    for o, e in ((o8, R["e8"]), (o7, R["e7"])):
        P("   R11 %s mOhm, %.3f A: %.3f / %.3f / %.3f A (matched / 1.5:1 / 2:1, converged) against %.1f A: %s; r11_dep.py's scaling %.2f / %.2f / %.2f A" % (
            o["key"], o["hi"], e[1.0], e[1.5], e[2.0], rating, ", ".join("%s %s" % (lab, "met" if e[s] <= rating else "NOT MET")
                                                                            for lab, s in (("matched", 1.0), ("1.5:1", 1.5), ("2:1", 2.0))), *o["lin"]))
        E = R["E"]
        P("     worst at 2:1: %s" % corner_text(R, worst_can(E[(o["key"], 2.0)]), R["fsws"], R["fch_both"]))
        P("     worst ceramic (matched): VBUS20 %.2f A, FE_OUT %.2f A" % (math.sqrt(E[(o["key"], 1.0)][("cerv", 0)]["ms"]), math.sqrt(E[(o["key"], 1.0)][("cero", 0)]["ms"])))
    D = R["D"]
    P("   why the rebuild reads above the scaling at %.3f A (worst can, matched / 2:1, MODELED):" % o8["hi"])
    P("     the record's network (L2 %.1f uH, R11 %.0f mOhm): %.3f / %.3f A, the scaling's own basis (it reads %.2f / %.2f A)" % (
        rec["l2_old"] * 1e6, R["r11_drawn"] * 1e3, D[("record", 1.0)], D[("record", 2.0)], o8["lin"][0], o8["lin"][2]))
    P("     with L2 %.1f uH: %.3f / %.3f A; with R11 %s mOhm as well (section 5's figure): %.3f / %.3f A. R11's own resistance in the" % (
        R["l2"] * 1e6, D[("L2", 1.0)], D[("L2", 2.0)], o8["key"], R["e8"][1.0], R["e8"][2.0]))
    P("     network isolates FE_OUT from VBUS20: lowering it lets more of the front end's switch current into the cans")
    P("     the 400 kHz row alone (PWM_FREQ's power-on value): %.3f / %.3f A: the 2:1 worst is on that row (340 kHz) either way" % (D[("400", 1.0)], D[("400", 2.0)]))
    P("")
    P("6. THE RE-SIZE (SESSION). The sharing basis: the cans' ESR within 2:1 (read at 100 kHz before fitting) AND each can's branch")
    P("   within %.1f nH and %.1f mOhm of every other's (a layout rule: a 10 mm VBUS20 pour 0.2 mm over its plane is about 25 pH/mm, so" % (
        LAYOUT[0] * 1e9, LAYOUT[1] * 1e3))
    P("   0.5 nH is a 20 mm path difference; 0.5 mOhm two squares of 2 oz copper), both against the one can with the lowest ESR and the")
    P("   shortest branch. The rule: every can at most %.1f A less the consistency tolerance scaled to the current (%.4f A per A) at every" % (
        rating, MARGIN_PER_A))
    P("   spread, on the larger of a full search (at the binding 2:1 spread on the decision grids, VBAT every %.1f V, fSW every %.1f kHz," % (
        DECIDE["vbat"], DECIDE["fsw"] / 1e3))
    P("   the charger every %.0f kHz; at the others on the record's) and its maximum converged on 4b's grids; the groups screened in" % (DECIDE["fch"] / 1e3))
    P("   order of the change at the 2:1 spread on the record's grids;")
    P("   the first group with a bank that meets the rule gives the bank, the lowest worst can within it")
    for o, groups in ((o8, CANDIDATES_8), (o7, CANDIDATES_7)):
        ch = R["chosen"][o["key"]]
        P("   R11 %s mOhm, %.3f A: the rule's limit %.4f A" % (o["key"], o["hi"], ch["lim"]))
        for grp, banks in groups:
            if all((o["key"], bk) not in R["scr"] for bk in banks):
                continue
            P("     +%d can(s), +%d ceramics: %s" % (grp[0], grp[1], "; ".join("%d cans, %d + %d ceramics %.3f A at 2:1%s" % (
                bk[0], bk[1], bk[2], R["scr"][(o["key"], bk)], "" if (o["key"], bk) not in R["dec_all"] else " (decided: %s)" % " / ".join(
                    "%.3f" % R["dec_all"][(o["key"], bk)][s]["fig"] for s in (1.0, 1.5, 2.0))) for bk in banks)))
        bk = ch["bank"]
        cvb = ch["conv"]
        P("     CHOSEN: %d EEHZK1V331P, %d ceramics on VBUS20, %d on FE_OUT (%+d can(s), %+d on VBUS20, %+d on FE_OUT against the drawn %d / %d / %d)" % (
            bk[0], bk[1], bk[2], bk[0] - R["drawn"][0], bk[1] - R["drawn"][1], bk[2] - R["drawn"][2], *R["drawn"]))
        P("       worst can %s A (matched / 1.5:1 / 2:1), %s %% of %.1f A; the search %s A, converged %s A%s" % (
            " / ".join("%.3f" % cvb[s]["fig"] for s in (1.0, 1.5, 2.0)), " / ".join("%.0f" % (100 * cvb[s]["fig"] / rating) for s in (1.0, 1.5, 2.0)), rating,
            " / ".join("%.3f" % cvb[s]["search"] for s in (1.0, 1.5, 2.0)), " / ".join("%.3f" % cvb[s]["conv"] for s in (1.0, 1.5, 2.0)),
            "" if o["key"] == "8" else " (the contingency: every spread searched on the record's grids)"))
        tot, st, fe_, ch_, mdl = cvb[2.0]["cv"]
        P("       at 2:1, converged: ESL %.2f nH, ceramic %.3f uF, VIN %.1f V, fsw %.1f kHz, VBAT %.2f V, fch %.0f kHz" % (
            b["esl_b"][st[0]] * 1e9, b["cer_c"][st[1]] * 1e6, R["grid"]["vins"][fe_[1][0]], mdl.fsws[fe_[1][1]] / 1e3, mdl.vbats[ch_[1][0]], mdl.fchs[ch_[1][1]] / 1e3))
        P("       worst ceramic (matched, converged): VBUS20 %.2f A, FE_OUT %.2f A (no MLCC ripple rating held: not judged)" % (ch["cer"]["cerv"], ch["cer"]["cero"]))
    lu = R["LU"]
    P("   the lumped node (no layout mismatch, as the lost analysis judged it) at 8 mOhm: 7 cans, 18 + 3 ceramics %.3f A at 2:1 (the" % lu["screen"])
    P("     record's grids); 7 cans, 21 + 3 ceramics %s A (matched / 1.5:1 / 2:1, the search on the record's grids and converged): one" % (
        " / ".join("%.3f" % lu[(7, 21, 3)][s]["fig"] for s in (1.0, 1.5, 2.0))))
    P("     more can would serve an ideal layout; the layout basis is what takes the second")
    Hs = R["H"]
    P("   SENSITIVITY, not gating (the decision takes no credit for it): the cans at %.3f A with VIN at %s V only, above %.1f V (8 mOhm)" % (
        o8["hi"], ", ".join("%g" % v for v in Hs["vins"]), Hs["b8"]))
    P("     and %.1f V (7 mOhm), where L4-E6's average limit, not its R12's peak limit, sets the fault current (at 9 V the peak limit" % Hs["b7"])
    P("     holds the output to %.2f A, L4-E6): the drawn bank %.3f / %.3f A, the chosen %.3f / %.3f A (matched / 2:1). The worst" % (
        Hs["i9"], Hs["vals"][("drawn", 1.0)], Hs["vals"][("drawn", 2.0)], Hs["vals"][("8", 1.0)], Hs["vals"][("8", 2.0)]))
    P("     can in sections 5 and 6 sits at %s (%d of %d runs), with the highest permitted current there, which L4-E6's R12 would" % (
        "9 V" if Hs["all9"] else "9 V in", Hs["n9"][0], Hs["n9"][1]))
    P("     not let through: the decision holds whether or not that draft is applied")
    a7 = R["chosen"]["8_at_7"]
    P("   the 8 mOhm bank if V-A07 fails (7 mOhm, %.3f A): %.3f / %.3f / %.3f A: %s" % (o7["hi"], a7[1.0], a7[1.5], a7[2.0],
                                                                                   "met" if max(a7.values()) <= rating else "NOT MET, so 7 mOhm needs its own bank"))
    P("")
    ch8, sel, SX = R["chosen"]["8"], R["sel"], R["SX"]
    bk = ch8["bank"]
    P("6b. THE SELECTED BANK (%d cans, %d + %d ceramics, R11 8 mOhm, %.3f A): EACH CAN, ITS LOSS, THE RATING AT FREQUENCY AND TEMPERATURE," % (bk[0], bk[1], bk[2], o8["hi"]))
    P("    THE STRESSES")
    P("   | spread | the can with the lowest ESR and shortest branch | each sibling | margin to %.1f A (the worse, converged) | largest loss in a can | of the rated condition's |" % rating)
    for sp in (1.0, 1.5, 2.0):
        f_ = ch8["full"][sp]
        io, isb = math.sqrt(f_[("odd", 0)]["ms"]), math.sqrt(f_[("sib", 0)]["ms"])
        P("   | %g:1 | %.3f A | %.3f A | %.3f A | %.1f mW | %.0f %% |" % (sp, io, isb, rating - ch8["conv"][sp]["fig"], 1e3 * sel["PD"][sp], 100 * sel["PD"][sp] / sel["p_rated"]))
    P("   the worst ceramic (matched, converged): VBUS20 %.2f A, FE_OUT %.2f A; no MLCC ripple rating is held for the 10u 50V X7R 1210, so" % (
        ch8["cer"]["cerv"], ch8["cer"]["cero"]))
    P("     no margin is stated for a ceramic (their loss at the band's 5 mOhm: %.0f and %.0f mW a part, INFERRED)" % (
        1e3 * ch8["cer"]["cerv"] ** 2 * b["cer_esr"][-1], 1e3 * ch8["cer"]["cero"] ** 2 * b["cer_esr"][-1]))
    P("   FREQUENCY (MAKER p.2): every harmonic of both sources lies at or above %.1f kHz (the front end's lowest fSW; the charger's" % (sel["fmin"] / 1e3))
    P("     lowest is %.0f kHz); the sheet's correction for 100 uF and more is %.2f from %.0f kHz up, so the current referred to the" % (
        min(R["fch_both"]) / 1e3, sel["corr_min"], sel["corr_at"] / 1e3))
    P("     rating's 100 kHz, the root of the sum of each harmonic over its factor squared, equals the rms itself: no derating applies")
    P("   TEMPERATURE (MAKER p.1, p.5, p.6; INFERRED where said): the rating is the sheet's at %.0f C, the category's top, with no uplift" % mk["t_cat"])
    P("     printed for a cooler can, so none is taken. Each can's loss is at most %.0f %% of the rated condition's (%.1f A squared times the" % (
        100 * max(sel["PD"].values()) / sel["p_rated"], rating))
    P("     %.0f mOhm maximum, %.0f mW), so its own rise is under the rated one (INFERRED: the same can, the same thermal path). On p.6's" % (
        mk["esr_can"] * 1e3, 1e3 * sel["p_rated"]))
    P("     equation the expected life is then at least L1 x 2^((T1 - T2) / 10): %.0f h at the worst inside air, %.1f C (%s), and %.0f h" % (
        sel["life"][0], sel["t_air"], ENVELOPE, sel["life"][1]))
    P("     at %.0f C, L1's own temperature at the fault (L4-E6; a can beside it, ASSUMPTION), each against the sheet's %.0f-year cap (%.0f h)," % (
        sel["t_local"], mk["life_cap_y"], mk["life_cap_y"] * 8760))
    P("     with the highest permitted current held continuously, which is the fault and not the kit's service")
    P("   THE SPREAD AND THE GEOMETRY (SESSION): the sheet prints the ESR's maximum, 20 mOhm, and its endurance limit, 200 % of it, and")
    P("     no minimum or typical; its remedy is one part number and no 'partiality of cable impedances' (p.7). A can that ages or runs")
    P("     hotter rises in ESR and takes LESS current, so the ESR spread corrects itself in service; the branch inductance does not.")
    P("     Stressed (not the decision's basis), each against %.1f A and the rule's %.4f A:" % (rating, ch8["lim"]))
    P("     the layout at twice its rule, every sibling's branch %.1f nH and %.1f mOhm longer: %.3f A matched, %.3f A at 2:1: %s" % (
        GEOM[0] * 1e9, GEOM[1] * 1e3, SX[("geometry", 1.0)], SX[("geometry", 2.0)],
        "holds" if max(SX[("geometry", 1.0)], SX[("geometry", 2.0)]) <= ch8["lim"] else "FLIPS the selection"))
    if SX["robust"]:
        rb, rv = SX["robust"]
        P("       the smallest bank that holds the rule there: %d cans, %d + %d ceramics, %s A (the record's grids, matched / 1.5:1 / 2:1)" % (
            rb[0], rb[1], rb[2], " / ".join("%.3f" % v for v in rv)))
    else:
        P("       no bank of up to two more cans holds the rule there")
    P("     the record's extreme ESR spread, one can at the low-ESR corner with its siblings at the sheet's maximum (%.1f:1), on the" % (1.0 / b["esr_k"][0]))
    P("       layout basis: %.3f A (the drawn bank, lumped: %.3f A): the reason the fitted set is read and held within 2:1" % (SX[("3.3", 0)], SX[("3.3 drawn", 0)]))
    P("     the bands widened, ESL down to %.1f nH and the ceramics' C down to %.1f uF: %.3f A matched (at %.2f nH, %.3f uF), %.3f A at 2:1" % (
        STRESS["esl_lo"], STRESS["cer_lo"], SX[("bands", 1.0)][0], SX[("bands", 1.0)][1], SX[("bands", 1.0)][2], SX[("bands", 2.0)][0]))
    P("       (at %.2f nH, %.3f uF): %s" % (SX[("bands", 2.0)][1], SX[("bands", 2.0)][2],
                                          "holds" if max(SX[("bands", 1.0)][0], SX[("bands", 2.0)][0]) <= ch8["lim"] else "FLIPS the selection"))
    P("")
    P("7. THE LOOP WITH THE RE-SIZED BANK (the compensation unchanged; R12 as drawn %s and L4-E6's draft %.0f mOhm)" % (G["rcs"], R["r12_e6"] * 1e3))
    P("   (PM and GM interpolated at each crossing; the grid point's figure in brackets)")
    P("   | bank | R12 | PM | GM | abs(1+T) min | crossover | Zout peak / bound | widened PM | widened GM | widened abs(1+T) |")
    lv, lw = R["loop_drawn"]
    rows = [("drawn %d cans, %d ceramics" % (R["drawn"][0], sum(R["drawn"][1:])), R["rcs_drawn"], lv, lw)]
    rows.append(("drawn %d cans, %d ceramics" % (R["drawn"][0], sum(R["drawn"][1:])), R["r12_e6"]) + R["L7"][("drawn", R["r12_e6"])])
    for key in ("8", "7"):
        bk = R["chosen"][key]["bank"]
        for rcs in (R["rcs_drawn"], R["r12_e6"]):
            rows.append(("%s mOhm's %d cans, %d ceramics" % (key, bk[0], bk[1] + bk[2]), rcs) + R["L7"][(key, rcs)])
    for name, rcs, d_, w_ in rows:
        P("   | %s | %.0f mOhm | %.1f (%.1f) deg | %.1f (%.1f) dB | %.2f | %.2f to %.2f kHz | %.0f mOhm / %.2f Ohm | %.1f deg | %.1f dB | %.2f |" % (
            name, rcs * 1e3, d_["pm_i"], d_["pm"], d_["gm_i"], d_["gm"], d_["mm"], d_["fc_lo_i"], d_["fc_hi_i"], d_["z"], R["lcfg"]["vout"] ** 2 / R["lcfg"]["p_bound"] / 3.0,
            w_["pm_i"], w_["gm_i"], w_["mm"]))
    P("   every row: PM >= 50 deg, GM >= 10 dB, |1+T| >= 0.5, every crossover under Fsw/20 and fRHP/3, the impedance under its bound;")
    P("   the compensation stays (the margins do not require a change); MODELED on the rebuilt model, the bench loop row is owed")
    P("")
    P("8. WHAT ELSE THE BANK'S CAPACITANCE MOVES (INFERRED, first order, each reproduced on the drawn node first)")
    cs = R["cons"]
    P("   | node | largest / smallest | soft-start draw at 9 / 12 / 13.8 V | bleed tau | bleed to release | restart ring in L1 |")
    labs = {"drawn": "drawn", "8": "8 mOhm's", "7": "7 mOhm's", "robust": "the layout-robust"}
    for tag in [t_ for t_ in ("drawn", "8", "7", "robust") if t_ in cs]:
        c = cs[tag]
        lab = "%s (%d cans, %d ceramics)" % (labs[tag], c["bank"][0], sum(c["bank"][1:]))
        P("   | %s | %.2f / %.2f mF | %.1f / %.1f / %.1f %% of %.2f A | %.2f to %.2f s | %.2f to %.2f s | %.1f A (%.0f %% of %.1f A), %.2f mJ |" % (
            lab, c["cmax"] * 1e3, c["cmin"] * 1e3, *c["ramp"], rec["entry"], c["bleed"][0][0], c["bleed"][0][1], c["bleed"][1][0], c["bleed"][1][1],
            c["ring"][0], 100 * c["ring"][0] / rec["ring"]["isat"], rec["ring"]["isat"], c["ring"][1]))
    P("   RECORD for the drawn node: %.1f / %.1f / %.1f %%, %.2f mF, tau %.2f to %.2f s, %.2f to %.2f s, %.1f A, %.2f mJ: reproduced" % (
        *rec["ss"]["pct"], rec["node_max"][0], *rec["bleed"]["tau"], *rec["bleed"]["t"], rec["ring"]["pk"], rec["ring"]["mj"]))
    P("   the soft-start draw is the ramp's own (charging plus BIAS %.2f A) at the end of the ramp, ISS max, CSS at %.3f of '%s'," % (rec["bias"], rec["ss"]["css_k"], G["css"][0]))
    P("     the divider at its 1 %% corner, VBUS20 %.1f V, efficiency %.2f; the start-up totals with the charger converting are re-taken" % (rec["ss"]["vbus"], rec["ss"]["eta"]))
    P("     under L4-E5's FW-A16 in the same circuit round (bench V-A09). The restart ring: a start from %.3f V, L1 at %.0f %% of nominal" % (
        rec["ring"]["v"], 100 * rec["ring"]["lk"]))
    P("     and the bank at +%.0f %%, through the buck low side; its peak against L1's typical Isat at 25 C (C-5's temperature derating" % (100 * (rec["ring"]["ck"] - 1)))
    P("     is not held)")
    P("")
    P("9. PREDICATES")
    for p_, ok in R["preds"]:
        P("   %s: %s" % (p_, "yes" if ok else "NO"))
    return out


def main():
    R = compute()
    text = "\n".join(render(R)) + "\n"
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
