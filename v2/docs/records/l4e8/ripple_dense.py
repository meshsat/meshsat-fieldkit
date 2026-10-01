#!/usr/bin/env python3
"""ripple_dense.py: layer 4 task L4-E8 (MESHSAT-1357, 1 October 2026). Board A's VBUS20 bulk bank re-sized so that finding B-4
of v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md closes (every EEHZK1V331P at most its 2.8 A rating at the 2:1 ESR spread at
R11 8 mOhm), on a REBUILD of the generator's lost dense node analysis (drafts/scripts/ripple_dense.py of the third fix-up of 26
September 2026, which is in neither this tree nor its history).

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry, rendered page or
record of L4-E4 to L4-E7 is edited (apply_gen_sch_a_bank.py beside this file is a draft for board A's generator owner). Labels:
MAKER (document, revision, page), NETLIST (board A's committed netlist), GENERATOR (gen_sch_a.py, parsed), RECORD (a figure or
band the generator's own record carries: gen_sch_a.py's comments and v2/docs/records/r4a/r4-decisions.md), INFERRED (a method
stated beside it), ASSUMPTION (a figure no document gives), SESSION (a choice this record makes), MODELED, INCONCLUSIVE.

THE MODEL is the lost analysis's as its record describes it (r4-decisions.md, section 6 B3): each converter's switch current
built from its topology (the front end's boost output current, the inductor current during 1 - D, or its buck triangle; the
charger's buck input current, the inductor current during D; each with its triangular ripple), split harmonic by harmonic to
the 60th between every capacitor of a three-node network (FE_OUT, R11 and L11, VBUS20, R16 and L16, CH_ACN), each part a
branch ESR + jwESL + 1/(jwC); the two converters are not synchronised, so each part's mean square is the FE's largest over
(VIN, fsw) plus the charger's largest over (VBAT, fch), which is the exact maximum over the product of those corners. The
harmonics are a 4096-point midpoint DFT, as in the recovered draft of its predecessor (bulk_ripple.py of the second fix-up,
recovered from a session transcript, not in this tree: <worktrees>/_recovered/older/r4a-fixup-A-1136/tree/drafts/scripts/
bulk_ripple.py, sha256 printed by nothing here; README.md names it).

THE SEARCH (SESSION, the coarsening stated as the task requires on this shared host): the passive bands are 332,100 sets on
the drawn node; their full enumeration in pure Python takes several CPU minutes per run. Each run is searched instead: (1)
every set of a COARSE grid (polymer ESL every 0.5 nH, ceramic C every 1 uF, every other band at all its corners) is bounded
from above (the per-harmonic largest weights); (2) the K sets with the highest bounds, one per corner of the other bands, are
evaluated exactly and climbed on the DENSE grid (ESL 0.05 nH, C 0.125 uF, and one band at a time over its corners) to a local
maximum; (3) at the best set the whole dense ESL x C slice is bounded and every set whose bound exceeds it is evaluated
exactly. The validation below is the test of the search: it must reproduce the record's dense figures, and section 4 also
enumerates the second fix-up's node in full (110,700 sets) for the record's count of sets over 2.8 A.

Run from the repository root:  python3 v2/docs/records/l4e8/ripple_dense.py > v2/docs/records/l4e8/ripple_dense.out
Needs pdftotext and PyYAML-free Python 3 (the imported L4-E4 record needs pdftoppm, Pillow and PyYAML). About four minutes.
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
}
RECOVERED = ("<worktrees>/_recovered/older/r4a-fixup-A-1136/tree/drafts/scripts/bulk_ripple.py",
             "c6b55794a762ecee48f36f4a445a22f3d8f80ffcf68f2c905cd9718827d15e34")   # not in the tree; cited, never read here

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
CANDIDATES_8 = [((0, 0), [(6, 15, 6)]), ((0, 3), [(6, 21, 3), (6, 18, 6)]), ((0, 6), [(6, 24, 3), (6, 21, 6)]),
                ((0, 9), [(6, 27, 3), (6, 24, 6)]), ((0, 12), [(6, 30, 3), (6, 27, 6)]), ((1, 0), [(7, 18, 3), (7, 15, 6)]),
                ((1, 3), [(7, 21, 3), (7, 18, 6)]), ((1, 6), [(7, 24, 3), (7, 21, 6)]), ((2, 0), [(8, 18, 3), (8, 15, 6)])]
CANDIDATES_7 = [((1, 12), [(7, 30, 3), (7, 27, 6)]), ((2, 0), [(8, 18, 3), (8, 15, 6)]), ((2, 3), [(8, 21, 3), (8, 18, 6)]),
                ((2, 6), [(8, 24, 3), (8, 21, 6)]), ((2, 9), [(8, 27, 3), (8, 24, 6)]), ((2, 12), [(8, 30, 3), (8, 27, 6)]),
                ((3, 0), [(9, 18, 3), (9, 15, 6)]), ((3, 3), [(9, 21, 3), (9, 18, 6)])]
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


def dft_basis(kind, d, cache={}):
    """The switch current's harmonics 1..NH (complex, /NS) for an inductor average of 1 A and no ripple (G), and for no average
    and a 1 A peak-to-peak triangle (H); d the high-side (buck) or low-side (boost) duty. The waveform is linear in the two, so
    any (average, ripple) is il G + dil H. kind: boost_out (IL during 1 - D), buck_out (IL always), buck_in (IL during D)."""
    key = (kind, d)
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
    for k in range(1, NH + 1):
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
    def __init__(self, vout, l1, l2, vins, fsws, vbats, fchs):
        self.vout, self.l1, self.l2 = vout, l1, l2
        self.vins, self.fsws, self.vbats, self.fchs = list(vins), list(fsws), list(vbats), list(fchs)
        F = [k * f for f in self.fsws for k in range(1, NH + 1)] + [k * f for f in self.fchs for k in range(1, NH + 1)]
        self.W = [2 * math.pi * f for f in F]
        self.nfeW = len(self.fsws) * NH

    def fe(self, vin, fsw, iout):
        """the front end's output switch current: (harmonic weights 2|c_k|^2, its own rms ac, SNVSAI1D Equation 19's value)"""
        v = self.vout
        if vin < v:
            d = 1 - vin / v
            il, dil, kind = iout / (1 - d), vin * d / (self.l1 * fsw), "boost_out"
        else:
            d = v / vin
            il, dil, kind = iout, v * (1 - d) / (self.l1 * fsw), "buck_out"
        G, H = dft_basis(kind, d)
        w = [2.0 * abs(il * g + dil * h) ** 2 for g, h in zip(G, H)]
        return w, (iout * math.sqrt(v / vin - 1) if vin < v else dil / math.sqrt(12))

    def ch(self, vbat, fch, iout):
        """the charger's input switch current (buck, VBUS20 to VBAT; its average is the front end's output current) and
        SLUSE66A Equation 4's value"""
        v = self.vout
        d2 = vbat / v
        il2, dil2 = iout / d2, v * d2 * (1 - d2) / (fch * self.l2)
        G, H = dft_basis("buck_in", d2)
        return [2.0 * abs(il2 * g + dil2 * h) ** 2 for g, h in zip(G, H)], il2 * math.sqrt(d2 * (1 - d2))

    def weights(self, iout):
        fe = [[self.fe(vin, f, iout)[0] for vin in self.vins] for f in self.fsws]
        ch = [[self.ch(vb, f, iout)[0] for vb in self.vbats] for f in self.fchs]
        return dict(fe=fe, ch=ch, fe_max=[[max(c) for c in zip(*b)] for b in fe], ch_max=[[max(c) for c in zip(*b)] for b in ch], iout=iout)


def zinv(W, c, esr, esl):
    return [1.0 / complex(esr, w * esl - 1.0 / (w * c)) for w in W]


class Node:
    """One network: nb cans (one at the corner's ESR, its siblings at spread x it), nv ceramics on VBUS20, no on FE_OUT; R11 +
    L11 from FE_OUT to VBUS20, R16 + L16 from VBUS20 to CH_ACN, the half bridge's parts at CH_ACN. The front end injects at
    FE_OUT, the charger draws at CH_ACN. Set key: (ESL, C, C_can, ESR_can, ceramic ESL, ceramic ESR, L16, L11) band indices."""
    def __init__(self, model, bands, bank, r11, r16, spread, hf):
        self.m, self.b, self.s = model, bands, spread
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
        if len(self._rest) > 300:
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
        ie, icb, ier = key
        b = self.b
        c, esr, esl = b["cb_k"][icb] * b["c_can"], b["esr_k"][ier] * b["esr_can"], b["esl_b"][ie]
        yo = zinv(self.W, c, esr, esl)
        if self.s == 1.0:
            ys, yb = yo, [self.nb * y for y in yo]
        else:
            ys = zinv(self.W, c, esr * self.s, esl)
            yb = [a + (self.nb - 1) * y for a, y in zip(yo, ys)]
        yo2 = [abs(y) ** 2 for y in yo]
        v = self._bank[key] = (yb, yo2, yo2 if ys is yo else [abs(y) ** 2 for y in ys])
        return v

    def vectors(self, s, metrics):
        """per-frequency squared current per ampere of source, for each metric: odd (the can at the corner's ESR), sib (one
        of its siblings), cerv (one VBUS20 ceramic), cero (one FE_OUT ceramic)"""
        ie, ic, icb, ier, il, ir, i16, i11 = s
        yb, yo2, ys2 = self.bank((ie, icb, ier))
        r, kk, kkc, q, oofe, ooch = self.rest((ic, il, ir, i16, i11))
        inv = [1.0 / abs(a + c) ** 2 for a, c in zip(yb, r)]
        out = {}
        if "odd" in metrics or "sib" in metrics:
            out["odd"] = [i * k * y for i, k, y in zip(inv, kk, yo2)]
            out["sib"] = out["odd"] if self.s == 1.0 else [i * k * y for i, k, y in zip(inv, kk, ys2)]
        if "cerv" in metrics:
            out["cerv"] = [i * k for i, k in zip(inv, kkc)]
        if "cero" in metrics and self.no:
            nf = self.m.nfeW
            out["cero"] = ([abs(a + c + x) ** 2 * o * i for a, c, x, o, i in zip(yb, r, q, oofe, inv)]
                           + [o * i for o, i in zip(ooch, inv[nf:])])
        return out


def bound(vec, wt):
    off = len(wt["fe_max"]) * NH
    return (max(sum(map(MUL, w, vec[i * NH:(i + 1) * NH])) for i, w in enumerate(wt["fe_max"]))
            + max(sum(map(MUL, w, vec[off + i * NH:off + (i + 1) * NH])) for i, w in enumerate(wt["ch_max"])))


def exact(vec, wt):
    """(mean square, (FE's, (VIN index, fsw index)), (charger's, (VBAT index, fch index)))"""
    bf = (-1.0, None)
    for i, blk in enumerate(wt["fe"]):
        seg = vec[i * NH:(i + 1) * NH]
        for j, w in enumerate(blk):
            x = sum(map(MUL, w, seg))
            if x > bf[0]:
                bf = (x, (j, i))
    off = len(wt["fe"]) * NH
    bc = (-1.0, None)
    for i, blk in enumerate(wt["ch"]):
        seg = vec[off + i * NH:off + (i + 1) * NH]
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
    pm = gmd = 999.0
    mm = 1e9
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
            for k in (-180.0, -540.0):
                if (ph[j] - k) * (ph[j + 1] - k) <= 0:
                    gmd = min(gmd, -20 * math.log10(max(mag[j], 1e-12)))
        fhi_c = max(fhi_c, fh)
        ceil_ok = ceil_ok and fh <= min(fsw0 / 20.0, rhp3)
        all_cross = all_cross and fh > 0
        mm = min(mm, min(abs(1 + x) for x in t))
        zpk = max(zpk, max(zl))
        zr = max(zr, max(zl) / (vout ** 2 / cfg["p_bound"] / 3.0))
    return dict(pm=pm, gm=gmd, mm=mm, fc_lo=flo_c / 1e3, fc_hi=fhi_c / 1e3, z=zpk * 1e3, z_ratio=zr, ceil_ok=ceil_ok, all_cross=all_cross)


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
    need(z7, r"use capacitors with the same part number", "EEHZK p.7 parallel parts")
    need(page(EEHZK, 2), r"01-Apr-22", "EEHZK the sheet's date")
    R["mk"] = dict(fsw_row=fsw_row, rt_row=rt_row, gm=gm, ro=ro, vref=vref, iss=iss, acs=acs, f800=f0, f400=f1,
                   c_can=float(row.group(1)) * 1e-6, rip=float(row.group(2)) / 1000.0, esr_can=float(row.group(3)) * 1e-3,
                   corr_hi=tuple(float(v) for v in last))


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
    R["validated"] = all(r["ok"] for r in rows) and all(abs(g - w) <= t for _k, w, g, t in lrows)
    if not R["validated"]:
        return R
    # ---------------------------------------------------------------- 5. the drawn bank at the highest permitted currents
    Me = Model(vout, l1, l2, vins, fsws, vbats, fch_both)
    E = {}
    for o in out:
        we = [Me.weights(o["hi"])]
        for s in (1.0, 1.5, 2.0):
            nd = Node(Me, bands, drawn, o["r11"], r16, s, hf)
            E[(o["key"], s)] = search(nd, we, ("odd", "sib", "cerv", "cero") if s == 1.0 else ("odd", "sib"))
    R["E"] = E
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
    # ---------------------------------------------------------------- 6. the re-size
    scr, full_all, chosen = {}, {}, {}
    for o, groups in ((out[0], CANDIDATES_8), (out[1], CANDIDATES_7)):
        lim = rating - MARGIN_PER_A * o["hi"]
        we = [Me.weights(o["hi"])]
        pick = None
        for grp, banks in groups:
            for bank in banks:
                scr[(o["key"], bank)] = math.sqrt(worst_can(search(Node(Me, bands, bank, o["r11"], r16, 2.0, hf), we, ("odd",), slice_check=False))["ms"])
            for bank in banks:
                if scr[(o["key"], bank)] > lim:
                    continue
                full_all[(o["key"], bank)] = {s: search(Node(Me, bands, bank, o["r11"], r16, s, hf), we, ("odd", "sib")) for s in (1.0, 1.5, 2.0)}
            ok = [b for b in banks if (o["key"], b) in full_all and all(math.sqrt(worst_can(full_all[(o["key"], b)][s])["ms"]) <= lim for s in (1.0, 1.5, 2.0))]
            if ok:
                bank = min(ok, key=lambda b: max(worst_can(full_all[(o["key"], b)][s])["ms"] for s in (1.0, 1.5, 2.0)))
                pick = dict(bank=bank, group=grp, full=full_all[(o["key"], bank)], lim=lim,
                            cer=search(Node(Me, bands, bank, o["r11"], r16, 1.0, hf), we, ("cerv", "cero")))
                break
        if pick is None:
            refuse(4, "no candidate bank meets the rating with margin at %s mOhm" % o["key"])
        pick["first_at_rating"] = next((b for _g, bs in groups for b in bs if (o["key"], b) in scr and scr[(o["key"], b)] <= rating), None)
        chosen[o["key"]] = pick
    R["scr"], R["full_all"] = scr, full_all
    # sensitivity, not gating: VIN only where the average limit sets the fault current at both outcomes once L4-E6's R12 is in
    bnd = [float(need(t6, r"above ([\d.]+) V the average limit, not the peak limit, sets the fault current; at 9 V the output is held to ([\d.]+) A", "L4-E6's boundary").group(i))
           for i in (1, 2)]
    bnd7 = float(re.findall(r"above ([\d.]+) V the average limit, not the peak limit, sets the fault current", t6)[-1])
    Mh = Model(vout, l1, l2, [v for v in vins if v > max(bnd[0], bnd7)], fsws, vbats, fch_both)
    H = {}
    for tag, bank in (("drawn", drawn), ("8", chosen["8"]["bank"])):
        for sp in (1.0, 2.0):
            H[(tag, sp)] = math.sqrt(worst_can(search(Node(Mh, bands, bank, out[0]["r11"], r16, sp, hf), [Mh.weights(out[0]["hi"])], ("odd", "sib"), slice_check=False))["ms"])
    at9 = [worst_can(r_)["fe"][1][0] == 0 for r_ in list(E.values()) + [chosen[k]["full"][sp] for k in ("8", "7") for sp in (1.0, 1.5, 2.0)]]
    R["H"] = dict(vals=H, vins=Mh.vins, b8=bnd[0], b7=bnd7, i9=bnd[1], all9=all(at9), n9=(sum(at9), len(at9)))
    # the 8 mOhm bank at 7 mOhm, all spreads (what V-A07's failure would leave)
    o7 = out[1]
    b8 = chosen["8"]["bank"]
    chosen["8_at_7"] = {s: math.sqrt(worst_can(search(Node(Me, bands, b8, o7["r11"], r16, s, hf), [Me.weights(o7["hi"])], ("odd", "sib"), slice_check=False))["ms"])
                        for s in (1.0, 1.5, 2.0)}
    R["chosen"] = chosen
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
    R["cons"] = {tag: dict(cmax=cmax(b), cmin=cmin(b), ramp=ramp(b), bleed=bleed(b), ring=ringf(b))
                 for tag, b in (("drawn", drawn), ("8", chosen["8"]["bank"]), ("7", chosen["7"]["bank"]))}
    R["cons_ok"] = (all(abs(round(x, 1) - y) < 1e-9 for x, y in zip(R["cons"]["drawn"]["ramp"], ss["pct"]))
                    and abs(round(R["cons"]["drawn"]["ring"][0], 1) - ring["pk"]) < 1e-9 and abs(round(R["cons"]["drawn"]["ring"][1], 2) - ring["mj"]) < 1e-9
                    and abs(round(R["cons"]["drawn"]["cmax"] * 1e3, 2) - rec["node_max"][0]) < 1e-9
                    and abs(round(R["cons"]["drawn"]["bleed"][0][1], 2) - bl["tau"][1]) < 1e-9 and abs(round(R["cons"]["drawn"]["bleed"][0][0], 2) - bl["tau"][0]) < 1e-9)
    # ---------------------------------------------------------------- 9. predicates
    o8, o7 = out
    e8 = {s: math.sqrt(worst_can(E[("8", s)])["ms"]) for s in (1.0, 1.5, 2.0)}
    e7 = {s: math.sqrt(worst_can(E[("7", s)])["ms"]) for s in (1.0, 1.5, 2.0)}
    c8 = {s: math.sqrt(worst_can(chosen["8"]["full"][s])["ms"]) for s in (1.0, 1.5, 2.0)}
    c7 = {s: math.sqrt(worst_can(chosen["7"]["full"][s])["ms"]) for s in (1.0, 1.5, 2.0)}
    R.update(e8=e8, e7=e7, c8=c8, c7=c7)
    rounds = [v["rounds"] for res in list(V.values()) + list(E.values()) + [ch_["full"][s_] for ch_ in (chosen["8"], chosen["7"]) for s_ in (1.0, 1.5, 2.0)]
              for v in res.values()]
    R["rounds"] = (sum(1 for x in rounds if x), len(rounds), sum(rounds))
    P = [
        ("the rebuild reproduces every recorded dense figure within %.2f A and the re-review's point within %.4f A" % (TOL_DENSE, TOL_POINT),
         all(r["ok"] for r in R["vrows"])),
        ("the loop rebuild reproduces the recorded margins within the stated tolerances", all(abs(g - w) <= t for _k, w, g, t in lrows)),
        ("the full enumeration of the second fix-up's node equals the search's maximum and counts the record's sets over the rating",
         not R["count"]["above_search"] and (over, nset) == rec["second_count"]),
        ("the drawn bank does NOT meet 2.8 A at the 2:1 spread at either R11 outcome on the rebuild", e8[2.0] > rating and e7[2.0] > rating),
        ("no ceramics-only change (six cans) meets 2.8 A at the 2:1 spread at 8 mOhm", all(scr[("8", b)] > rating for _g, bs in CANDIDATES_8 for b in bs if b[0] == 6)),
        ("the chosen 8 mOhm bank meets 2.8 A less the margin at every spread, at %.3f A" % o8["hi"], all(v <= chosen["8"]["lim"] for v in c8.values())),
        ("the chosen 7 mOhm bank meets 2.8 A less the margin at every spread, at %.3f A" % o7["hi"], all(v <= chosen["7"]["lim"] for v in c7.values())),
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
    P("   the predecessor's draft, cited and not read: %s, sha256 %s" % (RECOVERED[0], RECOVERED[1][:16]))
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
    P("4. VALIDATION (tolerances fixed before the run: %.2f A on the dense figures, %.4f A on the re-review's point)" % (TOL_DENSE, TOL_POINT))
    P("   | node | spread | current | recorded | rebuilt | difference | within |")
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
    P("   NOT GATING, the worst ceramic at 5.7 A, matched: VBUS20 %.2f A (RECORD %.2f A, %+.2f A: OUTSIDE the tolerance), FE_OUT %.2f A (RECORD" % (
        cv, rec["ceramic"][0], cv - rec["ceramic"][0], co))
    P("     %.2f A, %+.2f A). The VBUS20 figure sits at an interior VBAT point of the assumed even grid: %s" % (
        rec["ceramic"][1], co - rec["ceramic"][1], corner_text(R, t[("cerv", 0)], R["fsws"], R["fch_both"])))
    P("     its likely cause is the VBAT grid's interior points, which the record does not give (the cans' worst sit at 10.0 V, the")
    P("     band's end, and do not move); it is not tuned. No MLCC ripple rating is held, so no ceramic figure is judged against one")
    P("   the loop (FE stage, six cans, 21 ceramics counted local, Rc1 %s, Cc1 %s, Cc2 %s, R12 %s):" % (G["comp"][0][0], G["comp"][1][0], G["comp"][2][0], G["rcs"]))
    P("   | figure | recorded | rebuilt | tolerance | within |")
    for k, w, g_, tol in R["lrows"]:
        P("   | %s | %g | %.3f | %g | %s |" % (k, w, g_, tol, "yes" if abs(g_ - w) <= tol else "NO"))
    P("   VERDICT: the rebuild is %s" % ("VALIDATED: every gating figure within its stated tolerance" if R["validated"] else "UNVALIDATED"))
    if not R["validated"]:
        return out
    P("")
    P("5. THE DRAWN BANK AT L4-E6'S HIGHEST PERMITTED CURRENTS, ON THE REBUILD (L2 %.1f uH as drawn since S-117, R11 at each outcome in" % (R["l2"] * 1e6))
    P("   the network, both charger rows, the current at every VIN: the fault case of B-4, U3 the load)")
    for o, e in ((o8, R["e8"]), (o7, R["e7"])):
        P("   R11 %s mOhm, %.3f A: %.3f / %.3f / %.3f A (matched / 1.5:1 / 2:1) against %.1f A: %s; r11_dep.py's scaling %.2f / %.2f / %.2f A" % (
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
    P("6. THE RE-SIZE (SESSION decision rule: every can at most %.1f A less the validation tolerance scaled to the current, %.4f A per A," % (rating, MARGIN_PER_A))
    P("   at every spread; the groups screened in order of the change at the 2:1 spread, the first group with a bank that meets the")
    P("   rule at every spread gives the bank, the lowest worst can within it)")
    for o, groups in ((o8, CANDIDATES_8), (o7, CANDIDATES_7)):
        ch = R["chosen"][o["key"]]
        P("   R11 %s mOhm, %.3f A: the rule's limit %.4f A" % (o["key"], o["hi"], ch["lim"]))
        for grp, banks in groups:
            if all((o["key"], bk) not in R["scr"] for bk in banks):
                continue
            P("     +%d can(s), +%d ceramics: %s" % (grp[0], grp[1], "; ".join("%d cans, %d + %d ceramics %.3f A at 2:1%s" % (
                bk[0], bk[1], bk[2], R["scr"][(o["key"], bk)], "" if (o["key"], bk) not in R["full_all"] else " (all spreads: %s)" % " / ".join(
                    "%.3f" % math.sqrt(worst_can(R["full_all"][(o["key"], bk)][s])["ms"]) for s in (1.0, 1.5, 2.0))) for bk in banks)))
        bk = ch["bank"]
        f = ch["full"]
        P("     CHOSEN: %d EEHZK1V331P, %d ceramics on VBUS20, %d on FE_OUT (+%d can(s), %+d on VBUS20, %+d on FE_OUT against the drawn %d / %d / %d)" % (
            bk[0], bk[1], bk[2], bk[0] - R["drawn"][0], bk[1] - R["drawn"][1], bk[2] - R["drawn"][2], *R["drawn"]))
        P("       worst can %s A (matched / 1.5:1 / 2:1), %s %% of %.1f A" % (" / ".join("%.3f" % math.sqrt(worst_can(f[s])["ms"]) for s in (1.0, 1.5, 2.0)),
                                                                       " / ".join("%.0f" % (100 * math.sqrt(worst_can(f[s])["ms"]) / rating) for s in (1.0, 1.5, 2.0)), rating))
        P("       at 2:1: %s" % corner_text(R, worst_can(f[2.0]), R["fsws"], R["fch_both"]))
        P("       worst ceramic (matched): VBUS20 %.2f A, FE_OUT %.2f A (no MLCC ripple rating held: not judged)" % (
            math.sqrt(ch["cer"][("cerv", 0)]["ms"]), math.sqrt(ch["cer"][("cero", 0)]["ms"])))
        fr = ch["first_at_rating"]
        if fr is not None and fr != bk:
            P("       the first screened bank under %.1f A itself: %d cans, %d + %d ceramics at %.3f A, inside the tolerance of the limit" % (
                rating, fr[0], fr[1], fr[2], R["scr"][(o["key"], fr)]))
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
    P("7. THE LOOP WITH THE RE-SIZED BANK (the compensation unchanged; R12 as drawn %s and L4-E6's draft %.0f mOhm)" % (G["rcs"], R["r12_e6"] * 1e3))
    P("   | bank | R12 | PM | GM | abs(1+T) min | crossover | Zout peak / bound | widened PM | widened GM | widened abs(1+T) |")
    lv, lw = R["loop_drawn"]
    rows = [("drawn %d cans, %d ceramics" % (R["drawn"][0], sum(R["drawn"][1:])), R["rcs_drawn"], lv, lw)]
    rows.append(("drawn %d cans, %d ceramics" % (R["drawn"][0], sum(R["drawn"][1:])), R["r12_e6"]) + R["L7"][("drawn", R["r12_e6"])])
    for key in ("8", "7"):
        bk = R["chosen"][key]["bank"]
        for rcs in (R["rcs_drawn"], R["r12_e6"]):
            rows.append(("%s mOhm's %d cans, %d ceramics" % (key, bk[0], bk[1] + bk[2]), rcs) + R["L7"][(key, rcs)])
    for name, rcs, d_, w_ in rows:
        P("   | %s | %.0f mOhm | %.1f deg | %.1f dB | %.2f | %.2f to %.2f kHz | %.0f mOhm / %.2f Ohm | %.1f deg | %.1f dB | %.2f |" % (
            name, rcs * 1e3, d_["pm"], d_["gm"], d_["mm"], d_["fc_lo"], d_["fc_hi"], d_["z"], R["lcfg"]["vout"] ** 2 / R["lcfg"]["p_bound"] / 3.0, w_["pm"], w_["gm"], w_["mm"]))
    P("   every row: PM >= 50 deg, GM >= 10 dB, |1+T| >= 0.5, every crossover under Fsw/20 and fRHP/3, the impedance under its bound;")
    P("   the compensation stays (the margins do not require a change); MODELED on the rebuilt model, the bench loop row is owed")
    P("")
    P("8. WHAT ELSE THE BANK'S CAPACITANCE MOVES (INFERRED, first order, each reproduced on the drawn node first)")
    cs = R["cons"]
    P("   | node | largest / smallest | soft-start draw at 9 / 12 / 13.8 V | bleed tau | bleed to release | restart ring in L1 |")
    for tag, lab in (("drawn", "drawn (%d cans, %d ceramics)" % (R["drawn"][0], sum(R["drawn"][1:]))),
                     ("8", "8 mOhm's (%d, %d)" % (R["chosen"]["8"]["bank"][0], sum(R["chosen"]["8"]["bank"][1:]))),
                     ("7", "7 mOhm's (%d, %d)" % (R["chosen"]["7"]["bank"][0], sum(R["chosen"]["7"]["bank"][1:])))):
        c = cs[tag]
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
    return 0 if R["validated"] else 4


if __name__ == "__main__":
    sys.exit(main())
