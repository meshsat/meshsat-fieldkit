#!/usr/bin/env python3
"""ripple_dense.py: layer 4 task L4-E8 (MESHSAT-1357, 1 October 2026; the fix rounds after the collaborator's check of 5ff06474
and its recheck of cc95fe1f, checks/astra-check-l4e8-1.md and -2.md). Board A's VBUS20 bulk bank re-sized so that finding B-4 of
v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md closes (every EEHZK1V331P at most its 2.8 A rating, at both R11 outcomes of
L4-E4 and L4-E6, every can independent over the ZK sheet's printed range). Each capacitor's current is DERIVED from the node's topology as gen_sch_a.py draws it, the operating conditions
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
L16, CH_ACN), each part a branch ESR + jwESL + 1/(jwC). The harmonics are a 4096-point midpoint DFT, as in the predecessor's
recovered draft (inputs/recovered/, cited, never run).
THE COMBINATION (B1, section 5b): the record's rule adds the front end's largest mean square over (VIN, fSW) to the charger's
over (VBAT, fCH); it is kept for the consistency check only. The rating is thermal and the two oscillators are independent over
continuous bands, so exact coincidences p fSW = q fCH are permitted and coincident harmonics add at their worst common phase
(coherent(), every ratio with p <= 20 along its line; section 6's bound takes every order).
THE FREQUENCY (B3): SNVSAI1D p.6's row at RT 40 k carried by Equation 5 to RT 40.2k with RT's tolerance and TCR (section 5).
THE SHARING (B2): every can independent over the ZK sheet's C, its ESR from 0 (no floor is printed) to size G's cold limit
after endurance, and the ESL band; without a floor no bank is bounded, so each can gets a ballast resistor.
THE BOUND (R1/R2, section 6, BoundNode): a conservative bound on every can's current over ARBITRARY independent branches, every
passive in its region, by convex enclosures of each branch's admittance per frequency bin and branch-and-bound on the coupled
terms; checked against a seeded brute-force sample (brute_check). The ballast is chosen on it, not on any search.
THE LOOP (R4, section 7): the compensation checked over the whole cold envelope of the cans' ESR; Cc2 chosen on it.
THE SEARCH's acceptance (sections 4 and 5, the drawn node and the consistency with the record) is its convergence: the drawn
node's maxima are re-taken on source grids four to ten times finer and with twice the harmonics, climbed again there, the finer
grids checked against finer ones still (section 4b). The chosen bank rests on the bound alone.

THE SEARCH (SESSION, sections 4 and 5 only; the coarsening stated as the task requires): the passive bands are 332,100 sets on
the drawn node; their full enumeration in pure Python takes several CPU minutes per run. Each run is searched instead: (1)
every set of a COARSE grid (polymer ESL every 0.5 nH, ceramic C every 1 uF, every other band at all its corners) is bounded
from above (the per-harmonic largest weights); (2) the K sets with the highest bounds, one per corner of the other bands, are
evaluated exactly and climbed on the DENSE grid (ESL 0.05 nH, C 0.125 uF, and one band at a time over its corners) to a local
maximum; (3) at the best set the whole dense ESL x C slice is bounded and every set whose bound exceeds it is evaluated
exactly, re-climbing until none does. Section 4 also enumerates the second fix-up's node in full (110,700 sets).

THE RATING (MAKER, the ZK sheet): applied at the harmonics' actual frequencies through p.2's correction table; at temperature
the rating at 125 C with no uplift taken; the life equation of p.6 tabulated as a lower bound for a MEASURED rise of the can
(CONDITIONAL, B4: the rated rise is not printed).

Run from the repository root:  python3 v2/docs/records/l4e8/ripple_dense.py > v2/docs/records/l4e8/ripple_dense.out
Needs pdftotext and PyYAML (the imported L4-E4 record needs pdftoppm and Pillow as well). About six minutes on the runner,
one process, the search coarsened as stated above.
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import ast
import bisect
import cmath
import contextlib
import hashlib
import heapq
import importlib.util
import io
import itertools
import json
import math
import operator
import os
import random
import re
import subprocess
import sys
from fractions import Fraction

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
LCSC_FILL = "v2/ecad/tools/lcsc_fill.py"
UNIROYAL = "v2/vendor/passives/held/uniroyal-series-11cd644d.pdf"     # held back by the maker's terms (installed with the held evidence)
HOJLR = "v2/vendor/passives/milliohm-hojlr2512-series.pdf"
JLC_HOJLR = "v2/docs/records/l4e4/inputs/jlc-search-hojlr2512-3w-2026-10-01.json"
# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options ([] is pdftotext's
# plain reading order). Each text is a verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its
# PDF (a held-back sheet's text is held back with it, under held/); _lib/pdftext.py returns it byte for byte and refuses when it is
# absent, so this script's own page() reads (listed from its source) never run pdftotext; section 0 prints each text's sha256 after
# the pins. L4-E4's compute(), run here, still reaches r11dep/r11_dep.py, which extracts at run time (the l4e7 KEY's group, not
# converted by W34)
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4e8
PDFTEXT = {
    "v2/vendor/passives/held/uniroyal-series-11cd644d.pdf": [["-layout", "-f", "6", "-l", "6"]],
    "v2/vendor/passives/milliohm-hojlr2512-series.pdf": [["-layout", "-f", "2", "-l", "2"]],
    "v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf": [["-layout", "-f", "1", "-l", "1"], ["-layout", "-f", "2", "-l", "2"], ["-layout", "-f", "5", "-l", "5"], ["-layout", "-f", "6", "-l", "6"], ["-layout", "-f", "7", "-l", "7"]],
    "v2/vendor/ti/bq25731-datasheet.pdf": [["-layout", "-f", "2", "-l", "2"], ["-layout", "-f", "16", "-l", "16"], ["-layout", "-f", "27", "-l", "27"], ["-layout", "-f", "43", "-l", "43"], ["-layout", "-f", "85", "-l", "85"]],
    "v2/vendor/ti/lm5176-datasheet.pdf": [["-layout", "-f", "1", "-l", "1"], ["-layout", "-f", "6", "-l", "6"], ["-layout", "-f", "17", "-l", "17"], ["-layout", "-f", "23", "-l", "23"], ["-layout", "-f", "24", "-l", "24"], ["-layout", "-f", "27", "-l", "27"], ["-layout", "-f", "30", "-l", "30"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(TOP, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
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
    LCSC_FILL: "eb1f5e9f5e1ca9ae1c3caafc954633b9aec3f86f39b252d2302558f816150216",
    UNIROYAL: "11cd644d5d8a34a6d12775afb80bf58d8fc11f0c3b700dbd0f7a59942ceaa5ef",
    HOJLR: "3224518dbc8bdc858a96cfde88de2611494550f95406f6b65130c232cdfc93fb",
    JLC_HOJLR: "98f9d91eea739772db67ab224f5187235412ee1b2800ac21d192d0468d276d66",
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
# THE SHARING (B2): every can independent over the bands the ZK sheet supports, C and ESR read from it in read_makers(); its ESL is
# not printed, so the record's band is kept (INFERRED). LAYOUT is the copper's allowance between branches (a layout rule): a 10 mm
# VBUS20 pour 0.2 mm over its plane is about 25 pH/mm (mu0 h / w), so 0.5 nH is a 20 mm path difference; 0.5 mOhm two squares of
# 2 oz copper; the siblings carry it against the target.
LAYOUT = (0.5e-9, 0.5e-3)
RB_ESL = (0.5e-9, 1.5e-9)     # INFERRED: a 2512 chip resistor's inductance, mu0 l h / w with l 6.3 mm, w 3.2 mm, h 0.25 to 0.75 mm
RB_RANGE = (10e-3, 100e-3)    # SESSION: the ballast values considered, from the catalogue reading of L4-E4 (in stock only)
RB_DT = 75.0                  # ASSUMPTION: the ballast's excursion from 25 C, to an assumed 100 C (r11_dep.py's convention for R11)
R12_E6 = 0.012                # L4-E6's R12 (its record, drafted): the loop is checked at it as well
RB_START = 0.038              # SESSION: the bound's scan starts at the first round's ballast (below it a feasible configuration is over the limit)
LOOP_STEP = 0.020             # SESSION: the cold envelope of the loop scanned in 20 mOhm steps of the cans' intrinsic ESR
CC2_TOL = (0.75, 1.25)        # ASSUMPTION: Cc2's X7R tolerance (+-10 %) and temperature coefficient (+-15 %) together
TYPICAL = dict(vin=13.8, iout=3.0, vbat=14.4, fch=400e3, can_l=3.5e-9, cer=(5.5e-6, 3.5e-3, 1.15e-9), l16=12.5e-9, l11=3e-9)   # SESSION:
                              # the energy term's illustration at nominal parts (fsw the envelope's nominal); not a measurement
LIFE_DT = (0.0, 5.0, 10.0, 20.0, 30.0)   # the can's own rise, K, for which the lifetime's lower bound is tabulated (CONDITIONAL)
COH_PMAX = 20        # SESSION: coincidence orders p <= 20 searched exactly (fch / fsw = p / q) in section 5; section 6 bounds all
COH_DF = 0.5e3       # SESSION: fsw sampled every 0.5 kHz along each coincidence line
COH_NTH = 256        # SESSION: the common time shift sampled at 256 points, then refined
TAU_TH = 1.0         # ASSUMPTION: the can's shortest thermal time constant, 1 s (the sheet prints none); a beat slower than
                     # 1 / (2 pi TAU_TH), 0.16 Hz, is quasi-static and heats as coherent; both bands are continuous, so exact
                     # coincidence is permitted and the worst case sits on it whatever TAU_TH is
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
        _PAGES[key] = PT.pdf_text(TOP, rel, ["-layout", "-f", str(n), "-l", str(n)], PDFTEXT, "v2/docs/records/l4e8", universal_newlines=True)
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


# ============================================================================================================== independent cans (B2)
class GNode(Node):
    """Every can independent (the check's B2): a target can at (C, R, L) and its n - 1 siblings at their own (C, R, L), each branch
    a ballast resistor (rb, at its tolerance's low end for the target and its high end for the siblings) in series with the can's
    ESR, ESL and C; the siblings' branches carry the layout's path difference. box: the per-can grids (absolute values). Set
    key: (target C, R, L, sibling C, R, L, ceramic C, ESL, ESR, L16, L11) indices. Without a ballast (rb 0) and with no ESR floor,
    the node is undamped, which section 5 shows."""
    ORDER = ("tc", "tr", "tl", "oc", "or_", "ol", "ic", "il", "ir", "i16", "i11")

    def __init__(self, model, bands, bank, r11, r16, hf, box, rb, rb_tol, path):
        Node.__init__(self, model, bands, bank, r11, r16, 1.0, hf)
        self.r11, self.r16, self.hf = r11, r16, hf
        self.box, self.rbt, self.rbo, self.path = box, rb * (1 - rb_tol), rb * (1 + rb_tol), path
        self._br = {}
        self.dims = dict(tc=len(box["c"]), tr=len(box["r"]), tl=len(box["l"]), oc=len(box["c"]), or_=len(box["r"]), ol=len(box["l"]),
                         ic=len(bands["cer_c"]), il=len(bands["cer_esl"]), ir=len(bands["cer_esr"]), i16=len(bands["l16"]),
                         i11=len(bands["l11"]) if self.no else 1)

    def branch_rcl(self, ic, ir, il, role):
        c, r, l = self.box["c"][ic], self.box["r"][ir], self.box["l"][il]
        if role == "t":
            return c, r + self.rbt, l
        return c, r + self.rbo + self.path[1], l + self.path[0]

    def branch(self, ic, ir, il, role):
        k = (ic, ir, il, role)
        v = self._br.get(k)
        if v is None:
            if len(self._br) > 3 * self.cap:
                self._br.clear()
            y = zinv(self.W, *self.branch_rcl(ic, ir, il, role))
            v = self._br[k] = (y, [abs(x) ** 2 for x in y])
        return v

    def params(self, s):
        tc, tr, tl, oc, or_, ol, ic, il, ir, i16, i11 = s
        b = self.b
        return dict(t=self.branch_rcl(tc, tr, tl, "t"), o=self.branch_rcl(oc, or_, ol, "o"), cer=(b["cer_c"][ic], b["cer_esr"][ir], b["cer_esl"][il]),
                    l16=b["l16"][i16], l11=b["l11"][i11])

    def vectors(self, s, metrics):
        tc, tr, tl, oc, or_, ol, ic, il, ir, i16, i11 = s
        yt, yt2 = self.branch(tc, tr, tl, "t")
        yo, yo2 = self.branch(oc, or_, ol, "o")
        n1 = self.nb - 1
        r, kk, kkc, q, oofe, ooch = self.rest((ic, il, ir, i16, i11))
        yb = [a + n1 * c for a, c in zip(yt, yo)]
        inv = [1.0 / abs(a + x) ** 2 for a, x in zip(yb, r)]
        out = {}
        if "odd" in metrics:
            out["odd"] = [i * k * y for i, k, y in zip(inv, kk, yt2)]
        if "sib" in metrics:
            out["sib"] = [i * k * y for i, k, y in zip(inv, kk, yo2)]
        if "cerv" in metrics:
            out["cerv"] = [i * k for i, k in zip(inv, kkc)]
        if "cero" in metrics and self.no:
            nf = self.m.nfeW
            out["cero"] = ([abs(a + c + x) ** 2 * o * i for a, c, x, o, i in zip(yb, r, q, oofe, inv)]
                           + [o * i for o, i in zip(ooch, inv[nf:])])
        return out


def node_params(nd, s):
    """a set's physical parameters, for either node: the target can, a sibling, the ceramics, L16 and L11"""
    if isinstance(nd, GNode):
        return nd.params(s)
    ie, ic, icb, ier, il, ir, i16, i11 = s
    b = nd.b
    c, esr, esl = b["cb_k"][icb] * b["c_can"], b["esr_k"][ier] * b["esr_can"], b["esl_b"][ie]
    return dict(t=(c, esr, esl), o=(c, esr * nd.s + nd.dr, esl + nd.dl), cer=(b["cer_c"][ic], b["cer_esr"][ir], b["cer_esl"][il]),
                l16=b["l16"][i16], l11=b["l11"][i11])


def box_grid(c_k, r_hi, l_band, nc=5, dr=5e-3, dl=0.1e-9):
    """the per-can grids: C over c_k (fractions of the nominal), R from 0 to r_hi, L over l_band"""
    nr = int(round(r_hi / dr)) + 1
    nl = int(round((l_band[1] - l_band[0]) / dl)) + 1
    return dict(c=[c_k[0] + (c_k[1] - c_k[0]) * i / (nc - 1) for i in range(nc)], r=[r_hi * i / (nr - 1) for i in range(nr)],
                l=[l_band[0] + (l_band[1] - l_band[0]) * i / (nl - 1) for i in range(nl)])


def gsearch(nd, wt, metric="odd", K=SEEDS):
    """the worst set of a GNode for one metric: stage 1 bounds a coarse grid (each can's C at three points, R at its ends, L at
    three points; the ceramics' C at four points and ESL at its ends; the least-damping copper corners), stage 2 climbs the K
    best-bounded sets, one per can configuration, one coordinate at a time and the two inductances together, stage 3 bounds the
    whole (target L x sibling L) slice at the best and re-climbs from anything above it. Returns (mean square, set, fe, ch)."""
    d, order = nd.dims, GNode.ORDER
    memo = {}

    def ex(x):
        if x not in memo:
            memo[x] = exact(nd.vectors(x, (metric,))[metric], wt)
        return memo[x]
    three = lambda n: sorted({0, (n - 1) // 2, n - 1})
    rec = []
    for tc, tr, tl, oc, or_, ol in itertools.product(three(d["tc"]), (0, d["tr"] - 1), three(d["tl"]), three(d["oc"]), (0, d["or_"] - 1), three(d["ol"])):
        for ic, il in itertools.product(COARSE_C, (0, d["il"] - 1)):
            x = (tc, tr, tl, oc, or_, ol, ic, il, 0, d["i16"] - 1, d["i11"] - 1)
            rec.append((bound(nd.vectors(x, (metric,))[metric], wt), x))
    rec.sort(reverse=True)
    seeds, seen = [], set()
    for _u, x in rec:
        if x[:6] in seen:
            continue
        seen.add(x[:6])
        seeds.append(x)
        if len(seeds) >= K:
            break

    def climb(cur):
        curv = ex(cur)[0]
        while True:
            nbr = []
            for pos, name in enumerate(order):
                n = d[name]
                vals = range(n) if n <= 3 else (cur[pos] - 1, cur[pos] + 1)
                nbr += [cur[:pos] + (x,) + cur[pos + 1:] for x in vals if 0 <= x < n and x != cur[pos]]
            for a, c in itertools.product((-1, 1), repeat=2):
                x, y = cur[2] + a, cur[5] + c
                if 0 <= x < d["tl"] and 0 <= y < d["ol"]:
                    nbr.append(cur[:2] + (x,) + cur[3:5] + (y,) + cur[6:])
            cand = max((ex(x)[0], x) for x in nbr)
            if cand[0] <= curv:
                return curv, cur
            curv, cur = cand
    best = max(climb(x) for x in seeds)
    rounds = 0
    while True:
        better = None
        for tl, ol in itertools.product(range(d["tl"]), range(d["ol"])):
            x = best[1][:2] + (tl,) + best[1][3:5] + (ol,) + best[1][6:]
            if bound(nd.vectors(x, (metric,))[metric], wt) > best[0]:
                e = ex(x)[0]
                if e > best[0] + 1e-12 and (better is None or e > better[0]):
                    better = (e, x)
        if better is None:
            break
        rounds += 1
        best = climb(better[1])
    tot, fe, ch = ex(best[1])
    return dict(ms=tot, set=best[1], fe=fe, ch=ch, rounds=rounds, n1=len(rec))


def ctransfer(nd, pr, f, can="t"):
    """the complex current per ampere of source into one can (the target or a sibling) at frequency f, for the front end
    injecting at FE_OUT and for the charger drawing at CH_ACN: one network solve, the same network as the vectors"""
    w = 2 * math.pi * f
    z = lambda c, r, l: complex(r, w * l - 1.0 / (w * c))
    yt, yo = 1 / z(*pr["t"]), 1 / z(*pr["o"])
    yc = 1 / z(*pr["cer"])
    YO = nd.no * yc
    y11 = 1 / complex(nd.r11, w * pr["l11"])
    y16 = 1 / complex(nd.r16, w * pr["l16"])
    yh = sum(1 / z(*p) for p in nd.hf)
    k11 = y11 / (YO + y11)
    k16 = y16 / (yh + y16)
    yt_all = yt + (nd.nb - 1) * yo + nd.nv * yc + YO * k11 + yh * k16
    y = yt if can == "t" else yo
    return k11 / yt_all * y, -k16 / yt_all * y


def phasors(model, vin, fsw, vbat, fch, iout):
    """the two sources' rms harmonic phasors (1..NH): the front end's output switch current and the charger's input current"""
    v = model.vout
    if vin < v:
        d = 1 - vin / v
        il, dil, kind = iout / (1 - d), vin * d / (model.l1 * fsw), "boost_out"
    else:
        d = v / vin
        il, dil, kind = iout, v * (1 - d) / (model.l1 * fsw), "buck_out"
    G, H = dft_basis(kind, d)
    a = [math.sqrt(2) * (il * g + dil * h) for g, h in zip(G, H)]
    d2 = vbat / v
    il2, dil2 = iout / d2, v * d2 * (1 - d2) / (fch * model.l2)
    G2, H2 = dft_basis("buck_in", d2)
    return a, [math.sqrt(2) * (il2 * g + dil2 * h) for g, h in zip(G2, H2)]


def theta_max(cs, nth=COH_NTH):
    """max over the common time shift of 2 sum Re(c_m e^(j m theta)), m = 1.., sampled then refined by golden section"""
    mags = [(abs(x), cmath.phase(x)) for x in cs]
    f = lambda th: sum(2 * mg * math.cos((i + 1) * th + ph) for i, (mg, ph) in enumerate(mags))
    ths = [2 * math.pi * j / nth for j in range(nth)]
    vals = [f(t) for t in ths]
    j = max(range(nth), key=lambda i: vals[i])
    a, b = ths[j] - 2 * math.pi / nth, ths[j] + 2 * math.pi / nth
    g = (math.sqrt(5) - 1) / 2
    for _ in range(40):
        c, d = b - g * (b - a), a + g * (b - a)
        if f(c) > f(d):
            b = d
        else:
            a = c
    return max(vals[j], f((a + b) / 2))


def coincidence_ratios(flo, fhi, rows, pmax):
    """every ratio fch / fsw = p / q (lowest terms, p <= pmax) the two frequency bands permit"""
    rmin, rmax = rows[0][0] / fhi, rows[-1][1] / flo
    return sorted({Fraction(p, q) for p in range(1, pmax + 1) for q in range(1, p + 1) if rmin <= p / q <= rmax})


def coherent(nd, s, model, iout, rows, can="t", pmax=COH_PMAX, df=COH_DF, op=None):
    """The can's worst mean square on EXACT coincidences p fsw = q fch (B1): the front end's harmonic p m and the charger's q m
    share a frequency, their relative phase set by one common time shift, maximised; every other harmonic adds in mean
    square. Every permitted ratio with p <= pmax, fsw along each ratio's line every df inside both bands, every VIN and VBAT
    of the model. op = (ratio, fsw, vin, vbat) evaluates one point only. Returns (mean square, (ratio, fsw, fch, vin, vbat))."""
    pr = node_params(nd, s)
    flo, fhi = model.fsws[0], model.fsws[-1]
    pts = []
    if op is None:
        for r in coincidence_ratios(flo, fhi, rows, pmax):
            for lo_c, hi_c in rows:
                a0, a1 = max(flo, lo_c / float(r)), min(fhi, hi_c / float(r))
                if a0 <= a1:
                    n = max(2, int(math.ceil((a1 - a0) / df)) + 1)
                    pts += [(r, a0 + (a1 - a0) * i / (n - 1)) for i in range(n)]
        vins, vbats = model.vins, model.vbats
    else:
        pts, vins, vbats = [(op[0], op[1])], [op[2]], [op[3]]
    best = (0.0, None)
    for r, fsw in pts:
        p, q = r.numerator, r.denominator
        fch = fsw * p / q
        pairs = [(p * k, q * k) for k in range(1, NH + 1) if p * k <= NH and q * k <= NH]
        TF = [ctransfer(nd, pr, k * fsw, can)[0] for k in range(1, NH + 1)]
        TC = [ctransfer(nd, pr, k * fch, can)[1] for k in range(1, NH + 1)]
        Bs = []
        for vbat in vbats:
            bb = phasors(model, vins[0], fsw, vbat, fch, iout)[1]
            B = [x * t for x, t in zip(bb, TC)]
            Bs.append((vbat, B, sum(abs(x) ** 2 for x in B)))
        for vin in vins:
            a = phasors(model, vin, fsw, vbats[0], fch, iout)[0]
            A = [x * t for x, t in zip(a, TF)]
            fe = sum(abs(x) ** 2 for x in A)
            for vbat, B, ch in Bs:
                cs = [A[k1 - 1] * B[k2 - 1].conjugate() for k1, k2 in pairs]
                if fe + ch + 2 * sum(abs(x) for x in cs) <= best[0]:
                    continue
                tot = fe + ch + (theta_max(cs) if cs else 0.0)
                if tot > best[0]:
                    best = (tot, (r, fsw, fch, vin, vbat))
    return best


def fsw_envelope(row, rt_row, rt, tol, tcr, dt):
    """SNVSAI1D p.6's fSW(1) row at RT 40 k carried by Equation 5 (p.17) to RT at its tolerance and TCR (INFERRED: the row's
    spread at 40 k kept, Equation 5 scaling each end)"""
    eq5 = lambda r: r * 116e-12 + 190e-9
    rt_hi, rt_lo = rt * (1 + tol) * (1 + tcr * dt), rt * (1 - tol) * (1 - tcr * dt)
    return row[0] * eq5(rt_row) / eq5(rt_hi), row[1] * eq5(rt_row) / eq5(rt), row[2] * eq5(rt_row) / eq5(rt_lo)


# ============================================================================================================== the bound (R1/R2, the recheck)
# A conservative bound on every can's current over ARBITRARY independent branches (the recheck's R1/R2): no sampling decides it.
# Per frequency bin [f1, f2] every branch's impedance R + jX lies in a rectangle (X = wL - 1/(wC) is monotone in w, L and C,
# each taken over its own interval, the bin's w included, branch by branch); its admittance in the image of that rectangle under
# 1/z, a region bounded by circular arcs, enclosed by the hull of arc samples dilated by their largest sagitta (inv_hull). Sums
# of independent branches lie in the Minkowski sum of their enclosures. The source side's Norton factor k = 1/(1 + Zl Ya) is
# bounded from below over its link's rectangle and its shunt's enclosure (kmin_bb), the target can's ratio |Y|/|Y + Yrest|
# from above over its rectangle and the rest's enclosure (tmax_bb); each harmonic takes its own worst set (only an overstatement).
BOUND = dict(f0=170e3, f_end=3.2e9, steps=((3e6, 0.005), (30e6, 0.01), (float("inf"), 0.04)), rel=1e-4, nh=120, p0=20,
             dfs=0.5e3, dfc=2e3, dvb=0.05, kmin_tol=1e-3, t_rtol=1e-3, cell_thr=1.05, cheap_ok=1.5, l11_cell=1.08, l16_cell=1.10,
             c190_cell=1.05, block=1.02)
# SESSION: the front end's VIN grid for the bound, the record's points with every 0.5 V of the boost range added (20 V itself, the
# buck-boost transition, is the waveform's limit with no ripple and no switching edge, so it is left out)
VIN_BOUND = tuple(sorted({9.0 + 0.5 * i for i in range(22)} | {13.8, 24.0, 30.0, 36.0}))
# ASSUMPTION (no maker figure held for C57112 or C1588): the half bridge's 0603 X7R parts as regions: C from 0.8 x (the K
# tolerance and the 20 V bias) to 1.1 x nominal; ESR from the predecessor's value (the least damping) to four times it; ESL 0.5
# to 1.0 nH
HF_BAND = dict(c=(0.8, 1.1), esr=(1.0, 4.0), esl=(0.5e-9, 1.0e-9))


def _cr(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def cvx_hull(pts):
    """the convex hull, counter-clockwise (Andrew's monotone chain)"""
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and _cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and _cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def mink(P, Q):
    """the Minkowski sum of two convex polygons (edges merged by angle; exact for convex sets)"""
    if len(P) < 3 or len(Q) < 3:
        return cvx_hull([(p[0] + q[0], p[1] + q[1]) for p in P for q in Q])
    st = lambda X: X[min(range(len(X)), key=lambda k: (X[k][1], X[k][0])):] + X[:min(range(len(X)), key=lambda k: (X[k][1], X[k][0]))]
    P, Q = st(P), st(Q)
    n, m = len(P), len(Q)
    i = j = 0
    out = []
    while i < n or j < m:
        a, b = P[i % n], Q[j % m]
        out.append((a[0] + b[0], a[1] + b[1]))
        if i >= n:
            j += 1
            continue
        if j >= m:
            i += 1
            continue
        ea = (P[(i + 1) % n][0] - a[0], P[(i + 1) % n][1] - a[1])
        eb = (Q[(j + 1) % m][0] - b[0], Q[(j + 1) % m][1] - b[1])
        c = ea[0] * eb[1] - ea[1] * eb[0]
        if c >= 0:
            i += 1
        if c <= 0:
            j += 1
    return cvx_hull(out)


def pscale(P, k):
    return [(k * x, k * y) for x, y in P]


def pdilate(P, e):
    """P grown by a square of half side e (it holds the disk of radius e)"""
    return P if e <= 0 else cvx_hull([(x + sx * e, y + sy * e) for x, y in P for sx in (-1, 1) for sy in (-1, 1)])


def pdist(px, py, P):
    """the distance from (px, py) to the convex polygon P (counter-clockwise), 0 inside"""
    n = len(P)
    if n == 1:
        return math.hypot(px - P[0][0], py - P[0][1])
    inside, best = n >= 3, float("inf")
    ax, ay = P[-1]
    for bx, by in P:
        ex, ey, wx, wy = bx - ax, by - ay, px - ax, py - ay
        if ex * wy - ey * wx < 0:
            inside = False
        ee = ex * ex + ey * ey
        t = min(1.0, max(0.0, (wx * ex + wy * ey) / ee)) if ee > 0 else 0.0
        dx, dy = wx - t * ex, wy - t * ey
        best = min(best, dx * dx + dy * dy)
        ax, ay = bx, by
    return 0.0 if inside else math.sqrt(best)


def zrect(r0, r1, x0, x1):
    return [(r0, x0), (r1, x0), (r1, x1), (r0, x1)]


def inv_hull(P, tol):
    """An OUTER convex polygon of {1/z : z in the convex polygon P}, 0 not in P. Each edge's image is an arc of the circle through
    the origin of radius 1/(2d), d the edge line's distance from the origin; equal steps of the angle seen from the origin are
    equal steps of twice that angle on the arc, chosen so that every chord's sagitta is at most tol. Every boundary point of the
    image lies within the largest sagitta of a chord, so the samples' hull grown by that sagitta holds the image's hull."""
    pts, eps = [], 0.0
    n = len(P)
    for k in range(n):
        a, b = complex(*P[k]), complex(*P[(k + 1) % n])
        e = b - a
        if abs(e) == 0:
            y = 1 / a
            pts.append((y.real, y.imag))
            continue
        d = abs((a.conjugate() * e).imag) / abs(e)
        ab = a.conjugate() * b
        span = math.atan2(ab.imag, ab.real)
        N = 1 if (d <= 0 or 2 * d * tol >= 2) else max(1, int(math.ceil(abs(span) / math.acos(1 - 2 * d * tol))))
        th0 = math.atan2(a.imag, a.real)
        for i in range(N + 1):
            if i == 0 or i == N:
                z = a if i == 0 else b
            else:
                u = cmath.exp(1j * (th0 + span * i / N))
                z = a - ((a.conjugate() * u).imag / (e.conjugate() * u).imag) * e
            y = 1 / z
            pts.append((y.real, y.imag))
        if d > 0:
            eps = max(eps, (1 - math.cos(span / N)) / (2 * d))
    return pdilate(cvx_hull(pts), eps)


def ihull(P):
    """inv_hull with the sagitta tolerance BOUND['rel'] of the image's largest modulus"""
    return inv_hull(P, BOUND["rel"] / pdist(0.0, 0.0, P))


def branch_rect(reg, w1, w2):
    """a branch's impedance rectangle over the bin [w1, w2] and its region (r, l, c intervals)"""
    return zrect(reg["r"][0], reg["r"][1], w1 * reg["l"][0] - 1 / (w1 * reg["c"][0]), w2 * reg["l"][1] - 1 / (w2 * reg["c"][1]))


def disk_inv(c, r):
    """the image of the disk (c, r) under 1/z: a disk, if 0 is outside"""
    m = abs(c) ** 2 - r * r
    return None if m <= 0 else (c.conjugate() / m, r / m)


def _split(b):
    r0, r1, x0, x1 = b
    if (r1 - r0) >= (x1 - x0):
        return [(r0, (r0 + r1) / 2, x0, x1), ((r0 + r1) / 2, r1, x0, x1)]
    return [(r0, r1, x0, (x0 + x1) / 2), (r0, r1, (x0 + x1) / 2, x1)]


def kmin_bb(Z, A, tol, cap=6000):
    """a LOWER bound on min |1 + z y| over z in the rectangle Z and y in the convex polygon A: branch and bound over Z; for a
    sub-rectangle with enclosing disk (c, r), |1 + z y| >= min over A of |1 + c y| - r max |A|, and min over A of |1 + c y| is
    |c| times the distance from -1/c to A (exact). The smallest open bound when the search stops is returned."""
    amax = max(math.hypot(x, y) for x, y in A)

    def ev(b):
        c = complex((b[0] + b[1]) / 2, (b[2] + b[3]) / 2)
        r = math.hypot(b[1] - b[0], b[3] - b[2]) / 2
        q = -1 / c
        v = abs(c) * pdist(q.real, q.imag, A)
        return v - r * amax, v
    b = (Z[0][0], Z[1][0], Z[0][1], Z[2][1])
    lb, best = ev(b)
    pq, n = [(lb, b)], 0
    while pq:
        lb, b = heapq.heappop(pq)
        if lb >= best * (1 - tol) or n >= cap:
            return max(0.0, min(lb, best))
        n += 1
        for k in _split(b):
            l_, v = ev(k)
            best = min(best, v)
            heapq.heappush(pq, (l_, k))
    return max(0.0, best)


def tmax_bb(T, Q, rtol, cap=20000):
    """an UPPER bound on max |y| / |y + q| over y = 1/z, z in the rectangle T, q in the convex polygon Q: branch and bound over
    T; a sub-rectangle's enclosing disk maps to a disk (c, r) under 1/z, and |y| / |y + q| <= (|c| + r) / (dist(-c, Q) - r). Returns
    (upper bound, the largest value met at a sub-rectangle's centre)."""
    def ev(b):
        cz = complex((b[0] + b[1]) / 2, (b[2] + b[3]) / 2)
        rz = math.hypot(b[1] - b[0], b[3] - b[2]) / 2
        y = 1 / cz
        lbv = abs(y) / max(pdist(-y.real, -y.imag, Q), 1e-300)
        di = disk_inv(cz, rz)
        if di is None:
            return float("inf"), lbv
        den = pdist(-di[0].real, -di[0].imag, Q) - di[1]
        return (float("inf") if den <= 0 else (abs(di[0]) + di[1]) / den), lbv
    b = (T[0][0], T[1][0], T[0][1], T[2][1])
    ub, best = ev(b)
    pq, n, dropped = [(-ub, b)], 0, 0.0
    while pq:
        nub, b = heapq.heappop(pq)
        if -nub <= best * (1 + rtol) or n >= cap:
            return max(-nub, dropped), best
        n += 1
        for k in _split(b):
            u, l_ = ev(k)
            best = max(best, l_)
            if u > best * (1 + rtol):
                heapq.heappush(pq, (-u, k))
            else:
                dropped = max(dropped, u)
    return max(best, dropped), best


def disk_of(P):
    cx = (min(x for x, _ in P) + max(x for x, _ in P)) / 2
    cy = (min(y for _, y in P) + max(y for _, y in P)) / 2
    return complex(cx, cy), max(math.hypot(x - cx, y - cy) for x, y in P)


def kmax_cell(Z, A, tol):
    """1 / kmin_bb, after a cheap disk enclosure of both: when the cheap bound is already at most BOUND['cheap_ok'] it is used"""
    cz, rz = disk_of(Z)
    ca, ra = disk_of(A)
    den = abs(1 + cz * ca) - (abs(cz) * ra + abs(ca) * rz + rz * ra)
    if den > 0 and 1 / den <= BOUND["cheap_ok"]:
        return 1 / den
    return 1 / kmin_bb(Z, A, tol)


def bound_edges():
    e = [BOUND["f0"]]
    while e[-1] < BOUND["f_end"]:
        e.append(e[-1] * (1 + next(w for lim, w in BOUND["steps"] if e[-1] < lim)))
    return e


def geo_cells(lo, hi, ratio):
    out, x = [], lo
    while x < hi * (1 - 1e-12):
        y = min(x * ratio, hi)
        out.append((x, y))
        x = y
    return out


# the switch currents' Fourier coefficients in closed form (exact for the piecewise-linear waveforms; the DFT of sections 3 to 5
# differs from them by under 3e-4 of the average current)
_FC = {}


def fourier(kind, d, nh):
    key = (kind, d, nh)
    if key in _FC:
        return _FC[key]
    G, H = [], []
    for k in range(1, nh + 1):
        w = 2 * math.pi * k
        E = lambda a, b: (cmath.exp(-1j * w * a) - cmath.exp(-1j * w * b)) / (1j * w)
        T1 = lambda a, b: ((-b * cmath.exp(-1j * w * b) / (1j * w) + cmath.exp(-1j * w * b) / w ** 2)
                           - (-a * cmath.exp(-1j * w * a) / (1j * w) + cmath.exp(-1j * w * a) / w ** 2))
        hr = -0.5 * E(0, d) + T1(0, d) / d
        hf = (0.5 + d / (1 - d)) * E(d, 1) - T1(d, 1) / (1 - d)
        if kind == "boost_out":
            G.append(E(d, 1))
            H.append(hf)
        elif kind == "buck_out":
            G.append(0j)
            H.append(hr + hf)
        else:
            G.append(E(0, d))
            H.append(hr)
    _FC[key] = (G, H)
    return G, H


def src_fe(vout, l1, vin, fsw, iout, nh):
    """the front end's output switch current: rms per harmonic, and (sum of jumps, sum of slope jumps) for the 1/m envelope"""
    if vin < vout:
        d = 1 - vin / vout
        il, dil, kind = iout / (1 - d), vin * d / (l1 * fsw), "boost_out"
        jk = (il + 0.5 * dil + abs(il - 0.5 * dil), 2 * dil / (1 - d))
    else:
        d = vout / vin
        il, dil, kind = iout, vout * (1 - d) / (l1 * fsw), "buck_out"
        jk = (0.0, 2 * dil * (1 / d + 1 / (1 - d)))
    G, H = fourier(kind, d, nh)
    return [math.sqrt(2) * abs(il * g + dil * h) for g, h in zip(G, H)], jk


def src_ch(vout, l2, vbat, fch, iout, nh):
    d2 = vbat / vout
    il2, dil2 = iout / d2, vout * d2 * (1 - d2) / (fch * l2)
    G, H = fourier("buck_in", d2, nh)
    return [math.sqrt(2) * abs(il2 * g + dil2 * h) for g, h in zip(G, H)], (il2 + 0.5 * dil2 + abs(il2 - 0.5 * dil2), 2 * dil2 / d2)


def block_ms(J, K, ma, mb):
    """the sum over m = ma..mb of 2 |c_m|^2 with |c_m| <= J / (2 pi m) + K / (2 pi m)^2 (integration by parts over a period with
    jumps J and slope jumps K), each term bounded by the integral from m - 1"""
    a, b, m0 = J / (2 * math.pi), K / (2 * math.pi) ** 2, ma - 1
    return 2 * (a * a * (1 / m0 - 1 / mb) + a * b * (1 / m0 ** 2 - 1 / mb ** 2) + b * b / 3 * (1 / m0 ** 3 - 1 / mb ** 3))


class BoundNode:
    """The bound's bins, the source sides' cells, the target's term per ballast, and the combination over the sources."""

    def __init__(self, regs, vout, l1, l2):
        self.regs, self.vout, self.l1, self.l2 = regs, vout, l1, l2
        self.E = bound_edges()
        self.nb = len(self.E) - 1
        self.P = []
        for k in range(self.nb):
            w1, w2 = 2 * math.pi * self.E[k], 2 * math.pi * self.E[k + 1]
            Hcer = ihull(branch_rect(regs["cer"], w1, w2))
            A = pscale(Hcer, regs["n_fe"])
            H191 = ihull(branch_rect(regs["c191"], w1, w2))
            A2 = mink(ihull(branch_rect(regs["c190"], w1, w2)), H191)
            Z16 = zrect(regs["r16"][0], regs["r16"][1], w1 * regs["l16"][0], w2 * regs["l16"][1])
            HY2 = ihull(mink(Z16, ihull(A2)))
            self.P.append(dict(w1=w1, w2=w2, A=A, iA=ihull(A), H191=H191, kch=1 / kmin_bb(Z16, A2, BOUND["kmin_tol"]),
                               S0=mink(pscale(Hcer, regs["n_vb"]), HY2)))
        self.band = [k for k in range(self.nb) if self.P[k]["kch"] > BOUND["cell_thr"]]
        self.ch_cells = [(a, b) for a in geo_cells(regs["l16"][0], regs["l16"][1], BOUND["l16_cell"])
                         for b in geo_cells(regs["c190"]["c"][0], regs["c190"]["c"][1], BOUND["c190_cell"])]
        self.KC = []
        h190 = {}
        for lc, cc in self.ch_cells:
            row = {}
            for k in self.band:
                p = self.P[k]
                if (k, cc) not in h190:
                    h190[(k, cc)] = mink(ihull(branch_rect(dict(regs["c190"], c=cc), p["w1"], p["w2"])), p["H191"])
                Z16 = zrect(regs["r16"][0], regs["r16"][1], p["w1"] * lc[0], p["w2"] * lc[1])
                row[k] = kmax_cell(Z16, h190[(k, cc)], BOUND["kmin_tol"])
            self.KC.append(row)
        self.R1, self.FC, self.T = {}, {}, {}

    def set_r11(self, r11):
        regs, out = self.regs, []
        r0, r1 = r11 * (1 - regs["r_tol"]), r11 * (1 + regs["r_tol"])
        for p in self.P:
            Zl = zrect(r0, r1, p["w1"] * regs["l11"][0], p["w2"] * regs["l11"][1])
            out.append(dict(HY1=ihull(mink(Zl, p["iA"])), kfe=1 / kmin_bb(Zl, p["A"], BOUND["kmin_tol"])))
        self.R1[r11] = out
        fband = [k for k in range(self.nb) if out[k]["kfe"] > BOUND["cell_thr"]]
        cells = geo_cells(regs["l11"][0], regs["l11"][1], BOUND["l11_cell"])
        K = []
        for lc in cells:
            row = {}
            for k in fband:
                p = self.P[k]
                Zl = zrect(r0, r1, p["w1"] * lc[0], p["w2"] * lc[1])
                row[k] = kmax_cell(Zl, p["A"], BOUND["kmin_tol"])
            K.append(row)
        self.FC[r11] = (cells, K)

    def set_target(self, r11, can):
        T = []
        for p, q in zip(self.P, self.R1[r11]):
            Hcan = ihull(branch_rect(can, p["w1"], p["w2"]))
            Q = mink(mink(p["S0"], pscale(Hcan, self.regs["n_can"] - 1)), q["HY1"])
            T.append(tmax_bb(branch_rect(can, p["w1"], p["w2"]), Q, BOUND["t_rtol"]))
        self.T[(r11, can["r"][0])] = T
        return T

    def rng(self, x, y):
        E = self.E
        i = min(self.nb - 1, max(0, bisect.bisect_right(E, x) - 1))
        j = min(self.nb - 1, max(0, bisect.bisect_right(E, y) - 1))
        return i, j

    def tails(self, Bg, fa, fb, J, K):
        """the harmonics above BOUND['nh']: blocks of ratio BOUND['block'] up to the last bin, each at the largest bin bound it
        meets; then |T| <= 1 above the last bin (above every branch's series resonance, every branch inductive)"""
        nh, tot, ma = BOUND["nh"], 0.0, BOUND["nh"] + 1
        mend = int(self.E[-1] // fb)
        while ma <= mend:
            mb = min(mend, max(ma, int(ma * BOUND["block"])))
            i, j = self.rng(ma * fa, mb * fb)
            tot += block_ms(J, K, ma, mb) * max(Bg[i:j + 1]) ** 2
            ma = mb + 1
        a, b, M = J / (2 * math.pi), K / (2 * math.pi) ** 2, mend
        return tot + 2 * (a * a / M + a * b / M ** 2 + b * b / (3 * M ** 3))

    def combine(self, r11, rbt, iout, fsw_band, rows, vbats):
        """the can's mean square bound over every VIN of VIN_BOUND, every fSW in fsw_band (intervals of BOUND['dfs'], each harmonic's
        amplitude the larger of its ends: convex in the ripple, which is 1/fSW), every fCH in the rows (intervals of BOUND['dfc']),
        every VBAT of vbats; per harmonic the bin bounds over the harmonic's frequency interval; the FE's and the charger's cells
        each maximised; exact coincidences of order p <= BOUND['p0'] added coherently (|a| + |c| per coincident frequency, any
        phase), higher orders by Cauchy-Schwarz, the harmonics above BOUND['nh'] by tails()"""
        nh, P0 = BOUND["nh"], BOUND["p0"]
        T = [t[0] for t in self.T[(r11, rbt)]]
        kfe = [q["kfe"] for q in self.R1[r11]]
        BFg = [k * t for k, t in zip(kfe, T)]
        BCg = [p["kch"] * t for p, t in zip(self.P, T)]
        cells, K = self.FC[r11]
        BFc = [[row.get(b, kfe[b]) * T[b] for b in range(self.nb)] for row in K]
        BCc = [[row.get(b, self.P[b]["kch"]) * T[b] for b in range(self.nb)] for row in self.KC]
        bandset = set(self.band)
        nfs = int(round((fsw_band[1] - fsw_band[0]) / BOUND["dfs"]))
        fs = [fsw_band[0] + (fsw_band[1] - fsw_band[0]) * i / nfs for i in range(nfs + 1)]
        FE = []
        for v in VIN_BOUND:
            amps = [src_fe(self.vout, self.l1, v, f, iout, nh) for f in fs]
            for i in range(nfs):
                A = [max(x, y) for x, y in zip(amps[i][0], amps[i + 1][0])]
                R_ = [self.rng((k + 1) * fs[i], (k + 1) * fs[i + 1]) for k in range(nh)]
                J, Kj = amps[i][1]
                tl = self.tails(BFg, fs[i], fs[i + 1], J, Kj)
                best, abar = -1.0, [0.0] * nh
                for Bc in BFc:
                    a = [x * max(Bc[r[0]:r[1] + 1]) for x, r in zip(A, R_)]
                    best = max(best, sum(x * x for x in a))
                    abar = [max(x, y) for x, y in zip(abar, a)]
                FE.append((v, i, abar, best + tl, tl))
        CH = []
        for lo, hi in rows:
            n = int(round((hi - lo) / BOUND["dfc"]))
            fc = [lo + (hi - lo) * i / n for i in range(n + 1)]
            amps = {b: [src_ch(self.vout, self.l2, b, f, iout, nh) for f in fc] for b in vbats}
            for i in range(n):
                R_ = [self.rng((k + 1) * fc[i], (k + 1) * fc[i + 1]) for k in range(nh)]
                bandk = [k for k, r in enumerate(R_) if any(b in bandset for b in range(r[0], r[1] + 1))]
                bs = set(bandk)
                nonb = [k for k in range(nh) if k not in bs]
                Bg = [max(BCg[r[0]:r[1] + 1]) for r in R_]
                Av = {b: [max(x, y) for x, y in zip(amps[b][i][0], amps[b][i + 1][0])] for b in vbats}
                base = {b: sum((Av[b][k] * Bg[k]) ** 2 for k in nonb) for b in vbats}
                env = [max(Av[b][k] for b in vbats) for k in range(nh)]
                J = max(amps[b][i][1][0] for b in vbats)
                Kj = max(amps[b][i][1][1] for b in vbats)
                tl = self.tails(BCg, fc[i], fc[i + 1], J, Kj)
                cells_b = [[max(Bc[R_[k][0]:R_[k][1] + 1]) for k in bandk] for Bc in BCc]
                cbb = [0.0] * nh
                for k in nonb:
                    cbb[k] = env[k] * Bg[k]
                for Bb in cells_b:
                    for k, x in zip(bandk, Bb):
                        cbb[k] = max(cbb[k], env[k] * x)
                order = sorted(range(len(cells_b)), key=lambda c: -sum((env[k] * x) ** 2 for k, x in zip(bandk, cells_b[c])))
                bmax, best = max(base.values()), -1.0
                for c in order:
                    Bb = cells_b[c]
                    if bmax + sum((env[k] * x) ** 2 for k, x in zip(bandk, Bb)) <= best:
                        continue
                    for b in vbats:
                        best = max(best, base[b] + sum((Av[b][k] * x) ** 2 for k, x in zip(bandk, Bb)))
                CH.append((fc[i], fc[i + 1], cbb, best + tl, tl))
        feM = max(x[3] for x in FE)
        chM = max(x[3] for x in CH)
        rmax, rmin = rows[-1][1] / fsw_band[0], rows[0][0] / fsw_band[1]
        qmin = int(math.ceil((P0 + 1) / rmax))
        fehi = max(sum(x * x for x in a[P0:]) + tl for _v, _i, a, _m, tl in FE)
        chhi = max(sum(x * x for x in c[qmin - 1:]) + tl for _a, _b, c, _m, tl in CH)
        best = (feM + chM + 2 * math.sqrt(fehi * chhi), None)
        ratios = sorted({Fraction(p, q) for p in range(1, P0 + 1) for q in range(1, p + 1) if rmin <= p / q <= rmax})
        for r in ratios:
            p, q = r.numerator, r.denominator
            for v, i, a, fms, tl in FE:
                Ia, Ib = fs[i], fs[i + 1]
                for ja, jb, c, cms, ctl in CH:
                    if ja / Ib <= p / q <= jb / Ia:
                        tot = fms + cms + 2 * sum(a[k * p - 1] * c[k * q - 1] for k in range(1, nh // p + 1) if k * q <= nh) + 2 * math.sqrt(tl * ctl)
                        if tot > best[0]:
                            best = (tot, (r, v, Ia, ja))
        fe_at = max(FE, key=lambda x: x[3])
        return dict(ms=best[0], fig=math.sqrt(best[0]), where=best[1], feM=feM, chM=chM, fehi=fehi, chhi=chhi, nocoh=feM + chM + 2 * math.sqrt(fehi * chhi),
                    fe_at=(fe_at[0], fs[fe_at[1]]), ch_at=max(CH, key=lambda x: x[3])[:2], tail=(max(x[4] for x in FE), max(x[4] for x in CH)))


# a seeded pseudo-random sample of fully independent configurations, against the bound (R1/R2's test); SESSION
BRUTE = dict(seed=20261001, bins=(172e3, 344e3, 600e3, 816e3, 2.5e6, 11e6, 18e6, 100e6), n_bin=300, n_e2e=120, p_ext=0.7)


def net_t(cfg, w):
    """the exact three-node network for explicit branch values: the can's current per ampere of each source"""
    z = lambda b: complex(b[0], w * b[1] - 1 / (w * b[2]))
    yk = 1 / z(cfg["t"])
    ya = sum(1 / z(b) for b in cfg["cer_o"])
    yc = 1 / z(cfg["c190"]) + 1 / z(cfg["c191"])
    k11 = 1 / (1 + complex(cfg["r11"], w * cfg["l11"]) * ya)
    k16 = 1 / (1 + complex(cfg["r16"], w * cfg["l16"]) * yc)
    tot = yk + sum(1 / z(b) for b in cfg["sib"]) + sum(1 / z(b) for b in cfg["cer_v"]) + ya * k11 + yc * k16
    return k11 * yk / tot, k16 * yk / tot


def brute_check(BN, regs, can, out, fswb, rows, vbats, sel, cfg):
    """(1) per bin: random configurations (every branch independent, each parameter at an end of its interval with probability
    p_ext, else uniform) at a random frequency inside the bin, each source's transfer against the bin's bound for the cells the
    sample lies in; (2) end to end: random configurations and operating points (VIN from VIN_BOUND, fSW uniform in the band, VBAT
    from the grid, fCH uniform in a row), half of them with L16 set so that its series resonance with C190 falls on one of the
    charger's harmonics and half at an exact coincidence fch = (p/q) fsw with p, q <= 4 added at |a| + |c|; the can's rms with 120
    harmonics in closed form against the outcome's figure. Returns the largest ratios found."""
    rnd = random.Random(cfg["seed"])
    def u(lo, hi):
        x = rnd.random()
        return lo if x < cfg["p_ext"] / 2 else hi if x < cfg["p_ext"] else lo + rnd.random() * (hi - lo)
    br = lambda reg: (u(*reg["r"]), u(*reg["l"]), u(*reg["c"]))

    def draw(r11):
        return dict(t=br(can), sib=[br(can) for _ in range(regs["n_can"] - 1)], cer_v=[br(regs["cer"]) for _ in range(regs["n_vb"])],
                    cer_o=[br(regs["cer"]) for _ in range(regs["n_fe"])], r11=u(r11 * (1 - regs["r_tol"]), r11 * (1 + regs["r_tol"])),
                    l11=u(*regs["l11"]), c190=br(regs["c190"]), c191=br(regs["c191"]), r16=u(*regs["r16"]), l16=u(*regs["l16"]))
    worst_bin, worst_e2e = 0.0, 0.0
    for o in out:
        r11 = o["r11"]
        T = BN.T[(r11, can["r"][0])]
        kfe = [q["kfe"] for q in BN.R1[r11]]
        fcells, fK = BN.FC[r11]
        for f in cfg["bins"]:
            k, _j = BN.rng(f, f)
            f1, f2 = BN.E[k], BN.E[k + 1]
            for _ in range(cfg["n_bin"]):
                c = draw(r11)
                w = 2 * math.pi * (f1 + rnd.random() * (f2 - f1))
                tf, tc = net_t(c, w)
                fi = next(i for i, (a, b) in enumerate(fcells) if a <= c["l11"] <= b)
                ci = next(i for i, ((a, b), (cc0, cc1)) in enumerate(BN.ch_cells) if a <= c["l16"] <= b and cc0 <= c["c190"][2] <= cc1)
                bfe = fK[fi].get(k, kfe[k]) * T[k][0]
                bch = BN.KC[ci].get(k, BN.P[k]["kch"]) * T[k][0]
                worst_bin = max(worst_bin, abs(tf) / bfe, abs(tc) / bch)
        for n in range(cfg["n_e2e"]):
            c = draw(r11)
            vin = rnd.choice(VIN_BOUND)
            fsw = fswb[0] + rnd.random() * (fswb[1] - fswb[0])
            vbat = rnd.choice(vbats)
            lo, hi = rnd.choice(rows)
            if n % 2:
                pq = rnd.choice([Fraction(p, q) for p in range(1, 5) for q in range(1, 5) if lo / fswb[1] <= p / q <= hi / fswb[0]])
                fsw = min(max(fsw, lo / float(pq)), hi / float(pq), fswb[1])
                fch = fsw * pq
            else:
                fch = lo + rnd.random() * (hi - lo)
                nres = rnd.randint(5, 40)
                lt = 1 / ((2 * math.pi * nres * fch) ** 2 * c["c190"][2]) - c["c190"][1]
                if regs["l16"][0] <= lt <= regs["l16"][1]:
                    c["l16"] = lt
            a, _ = src_fe(BN.vout, BN.l1, vin, fsw, o["hi"], BOUND["nh"])
            b, _ = src_ch(BN.vout, BN.l2, vbat, fch, o["hi"], BOUND["nh"])
            A = {round((m + 1) * fsw, 3): abs(x * net_t(c, 2 * math.pi * (m + 1) * fsw)[0]) for m, x in enumerate(a)}
            C = {round((m + 1) * fch, 3): abs(x * net_t(c, 2 * math.pi * (m + 1) * fch)[1]) for m, x in enumerate(b)}
            ms = sum(x * x for f_, x in A.items() if f_ not in C) + sum(x * x for f_, x in C.items() if f_ not in A)
            ms += sum((A[f_] + C[f_]) ** 2 for f_ in A if f_ in C)
            worst_e2e = max(worst_e2e, math.sqrt(ms) / sel[o["key"]]["fig"])
    return dict(bin=worst_bin, e2e=worst_e2e, n_bin=len(out) * len(cfg["bins"]) * cfg["n_bin"], n_e2e=len(out) * cfg["n_e2e"])


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


def loop_eval(cfg, nbulk, ncer, rcs, rc1, cc1, cc2, qs=(0.4, 0.8), lks=(1.0,), bulk=None, iouts=None, p_bound=None, fsw=None, banks=None):
    """banks: a list of mixed banks, each [(count, C, R), ...], in place of nbulk identical cans at each (C, R) of bulk"""
    cfg = dict(cfg, fsw=fsw or cfg["fsw"])
    F, S = loop_model(cfg)
    fsw0, flo, fhi = cfg["fsw"]
    gm, ro, acs, L = cfg["gm"], cfg["ro"], cfg["acs"], cfg["L"]
    cl_band = [c * ncer / cfg["ncer0"] for c in cfg["cl0"]]
    zc = [1.0 / (1.0 / (rc1 + 1.0 / (s * cc1)) + s * cc2 + 1.0 / ro) for s in S]
    bulk = bulk or [(cfg["c_can"] * k, cfg["esr_can"] * e) for k in (0.8, 1.2) for e in (0.3, 2.0)]
    items = banks or [[(nbulk, cb, eb)] for cb, eb in bulk]
    pb = p_bound or cfg["p_bound"]
    pm = gmd = pmi = gmi = 999.0
    mm = 1e9
    flo_i, fhi_i = 1e12, 0.0
    flo_c, fhi_c, zpk, zr, ceil_ok, all_cross = 1e12, 0.0, 0.0, 0.0, True, True
    for (mode, vin), cl, iout, q, fsw, g, lk, item in itertools.product(cfg["modes"], cl_band, iouts or cfg["iouts"], qs, (flo, fhi),
                                                                      (0.8, 1.2), lks, items):
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
        n0, c0, e0 = item[0]
        one = len(item) == 1
        for s, z in zip(S, zc):
            h = 1.0 / (1 + s / (wn * q) + (s / wn) ** 2)
            yb = n0 / (1.0 / (s * c0) + e0) if one else sum(n_ / (1.0 / (s * c_) + e_) for n_, c_, e_ in item)
            yl = 1.0 / (1.0 / (s * cl) + cfg["esr_l"]) + yb + 1.0 / rl
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
        zr = max(zr, max(zl) / (vout ** 2 / pb / 3.0))
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
    c_tol = float(need(z1, r"Capacitance tolerance\s+±(\d+) %", "EEHZK p.1 capacitance tolerance").group(1)) / 100.0
    c_life = float(need(z1, r"Capacitance change\s+Within ±(\d+)% of the initial value", "EEHZK p.1 endurance capacitance change").group(1)) / 100.0
    esr_life = float(need(z1, r"ESR\s+≦ (\d+) % of the initial limit", "EEHZK p.1 endurance ESR").group(1)) / 100.0
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
    size = need(z2, r"\d+\s+10\.0\s+10\.2\s+10\.5\s+(\S+)\s+\d+\s+\d+\s+[\d.]+\s+EEHZK1V331P", "EEHZK p.2 the 331P size code").group(1)
    zl = z1.splitlines()
    ic = [i for i, l in enumerate(zl) if "100 kHz)(-" in l]
    if len(ic) != 1:
        refuse(3, "EEHZK p.1: the cold row of ESR after endurance not read")
    codes, cold = zl[ic[0] - 1].split(), zl[ic[0] + 1].split()
    if size not in codes or len(cold) != len(codes):
        refuse(3, "EEHZK p.1: the cold ESR row's size codes do not carry %s" % size)
    t_cold = -float(need(zl[ic[0]], r"\(-(\d+) ℃", "EEHZK p.1 the cold row's temperature").group(1))
    need(z1, r"Characteristics dependencies in frequency and low temperature are as small as polymer type", "EEHZK p.1 the low temperature line")
    need(page(EEHZK, 2), r"01-Apr-22", "EEHZK the sheet's date")
    R["mk"] = dict(fsw_row=fsw_row, rt_row=rt_row, gm=gm, ro=ro, vref=vref, iss=iss, acs=acs, f800=f0, f400=f1,
                   c_can=float(row.group(1)) * 1e-6, rip=float(row.group(2)) / 1000.0, esr_can=float(row.group(3)) * 1e-3,
                   corr_hi=tuple(float(v) for v in last), corr=sorted(corr), life_h=life_h, t_cat=t_cat, life_cap_y=cap_y,
                   c_tol=c_tol, c_life=c_life, esr_life=esr_life, size=size, esr_cold=float(cold[codes.index(size)]), t_cold=t_cold)


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
    # ---------------------------------------------------------------- B3: the front end's frequency envelope, from the row and RT
    lc = open(os.path.join(TOP, LCSC_FILL), encoding="utf-8").read()
    mrt = need(lc, r'^ \(r"\^40\\\.2k", "R_0603"\): "(C\d+)",\s+# (\S+) (\S+), (\d+)%', "lcsc_fill.py RT's code and tolerance")
    rt_tol = float(mrt.group(4)) / 100.0
    u6 = page(UNIROYAL, 6)
    k6 = u6.find("0603\uff1a")
    if k6 < 0 or "Coefficient" not in u6[k6:k6 + 300]:
        refuse(3, "UNI-ROYAL p.6: the 0603 temperature coefficient row not found")
    rt_tcr = float(need(u6[k6:], r">10\S*:\s*\S*?(\d+)\s*PPM", "UNI-ROYAL p.6 the 0603 TCR above 10 Ohm").group(1)) * 1e-6
    env = yaml.safe_load(open(os.path.join(TOP, ENVELOPE), encoding="utf-8"))
    t_min = float(env["ambient_c"]["in_use"]["min"])
    t_air = max(env["worst_inside_air_c"]["lid_open"], env["worst_inside_air_c"]["lid_closed"])
    dt_rt = max(25.0 - t_min, t_air - 25.0)
    fenv = fsw_envelope(mk["fsw_row"], mk["rt_row"], rt, rt_tol, rt_tcr, dt_rt)
    fsws_e = lin(fenv[0], fenv[2], grid["n_fsw"])
    R["b3"] = dict(code=mrt.group(1), part=mrt.group(2) + " " + mrt.group(3), tol=rt_tol, tcr=rt_tcr, dt=dt_rt, t_min=t_min, t_air=t_air, env=fenv,
                   scale=(mk["rt_row"] * 116e-12 + 190e-9) / (rt * 116e-12 + 190e-9))
    Me = Model(vout, l1, l2, vins, fsws_e, vbats, fch_both)
    Mef = fine_model(Me, rows_ch)
    lcfg_e = dict(lcfg, fsw=(fenv[1], fenv[0], fenv[2]))
    # ---------------------------------------------------------------- 5. the drawn bank, the record's sharing, step by step at 7.262 A
    o8, o7 = out

    def rss_run(model, bank, r11x, sp, iout, conv=None):
        r_ = search(Node(model, bands, bank, r11x, r16, sp, hf), [model.weights(iout)], ("odd", "sib"), slice_check=False)
        w_ = worst_can(r_)
        res = dict(ms=w_["ms"], set=w_["set"], metric="odd" if w_ is r_[("odd", 0)] else "sib", fe=w_["fe"], ch=w_["ch"])
        if conv is not None:
            mkn = (lambda mm: Node(mm, bands, bank, r11x, r16, sp, hf))
            res["conv"] = converge(mkn, conv, w_["set"], res["metric"], iout)[1][0]
        return res
    Mrec_old = Model(vout, l1, rec["l2_old"], vins, fsws, vbats, fch_both)
    Mrec = Model(vout, l1, l2, vins, fsws, vbats, fch_both)
    D = {}
    for sp in (1.0, 1.5, 2.0):
        D[("record", sp)] = math.sqrt(rss_run(Mrec_old, drawn, r11_drawn, sp, o8["hi"])["ms"])
        D[("L2", sp)] = math.sqrt(rss_run(Mrec, drawn, r11_drawn, sp, o8["hi"])["ms"])
        x = rss_run(Mrec, drawn, o8["r11"], sp, o8["hi"], conv=fine_model(Mrec, rows_ch))
        D[("R11", sp)], D[("grids", sp)] = math.sqrt(x["ms"]), math.sqrt(max(x["ms"], x["conv"]))
    E = {}
    for o in out:
        for sp in (1.0, 1.5, 2.0):
            x = rss_run(Me, drawn, o["r11"], sp, o["hi"], conv=Mef)
            nd = Node(Me, bands, drawn, o["r11"], r16, sp, hf)
            nd.r11, nd.r16, nd.hf = o["r11"], r16, hf
            ch_ = coherent(nd, x["set"], Me, o["hi"], rows_ch, can="t" if x["metric"] == "odd" else "o")
            E[(o["key"], sp)] = dict(rss=math.sqrt(max(x["ms"], x["conv"])), coh=math.sqrt(max(ch_[0], x["ms"])), op=ch_[1], fe=x["fe"], ch=x["ch"], set=x["set"])
            if o["key"] == "8":
                D[("B3", sp)], D[("coh", sp)] = E[(o["key"], sp)]["rss"], E[(o["key"], sp)]["coh"]
    R["D"], R["E"] = D, E
    # the independent box with no ESR floor and no ballast: the drawn six cans and the first round's eight
    CAN_C_LIFE = ((1 - mk["c_tol"]) * (1 - mk["c_life"]), (1 + mk["c_tol"]) * (1 + mk["c_life"]))
    CAN_ESL = (bands["esl_b"][0], bands["esl_b"][-1])
    BOX_SHEET = dict(c_k=CAN_C_LIFE, r_hi=mk["esr_life"] * mk["esr_can"], l_can=CAN_ESL)
    R["box_sheet"] = BOX_SHEET
    box0 = box_grid([k * mk["c_can"] for k in CAN_C_LIFE], BOX_SHEET["r_hi"], CAN_ESL)
    U = {}
    for nb_ in (drawn[0], drawn[0] + 2):
        nd = GNode(Me, bands, (nb_,) + drawn[1:], o8["r11"], r16, hf, box0, 0.0, 0.0, LAYOUT)
        U[nb_] = gsearch(nd, Me.weights(o8["hi"]))
    R["U"], R["box0"] = U, box0
    # the check's counterexample, reproduced (B1): its eight-can corner at 198.8 / 816 kHz, then 204 / 816 and 204 / 408 kHz
    bxc = dict(c=[1.2 * mk["c_can"]], r=[0.3 * mk["esr_can"], 2 * 0.3 * mk["esr_can"]], l=[bands["esl_b"][0]])
    cx = {}
    for tag, fsw_, fch_, op_ in (("rss", 198.8e3, 816e3, None), ("4", 204e3, 816e3, (Fraction(4), 204e3, 9.0, 10.0)), ("2", 204e3, 408e3, (Fraction(2), 204e3, 9.0, 10.0))):
        Mc = Model(vout, l1, l2, [9.0], [fsw_], [10.0], [fch_])
        nd = GNode(Mc, bands, (8,) + drawn[1:], o8["r11"], r16, hf, bxc, 0.0, 0.0, LAYOUT)
        sx = (0, 0, 0, 0, 1, 0, 0, bands["cer_esl"].index(max(bands["cer_esl"])), 0, len(bands["l16"]) - 1, len(bands["l11"]) - 1)
        rss_ = exact(nd.vectors(sx, ("odd",))["odd"], Mc.weights(o8["hi"]))[0]
        coh_ = coherent(nd, sx, Mc, o8["hi"], rows_ch, op=op_)[0] if op_ else rss_
        cx[tag] = (math.sqrt(rss_), math.sqrt(coh_))
    # B2's counterexample: the same corner with the siblings' own ESL at the band's top (3.5 nH, plus the layout's 0.5 nH)
    Mc = Model(vout, l1, l2, [9.0], [198.8e3], [10.0], [816e3])
    nd = GNode(Mc, bands, (8,) + drawn[1:], o8["r11"], r16, hf, dict(bxc, l=[bands["esl_b"][0], bands["esl_b"][-1]]), 0.0, 0.0, LAYOUT)
    sx = (0, 0, 0, 0, 1, 1, 0, bands["cer_esl"].index(max(bands["cer_esl"])), 0, len(bands["l16"]) - 1, len(bands["l11"]) - 1)
    cx["esl"] = (math.sqrt(exact(nd.vectors(sx, ("odd",))["odd"], Mc.weights(o8["hi"]))[0]),) * 2
    R["cx"] = cx
    # ---------------------------------------------------------------- 6. the bound (the recheck's R1/R2): every can over arbitrary independent siblings
    cat = json.load(open(os.path.join(TOP, JLC_HOJLR), encoding="utf-8"))
    hoj = flat(page(HOJLR, 2))
    hoj_tcr = float(need(hoj, r"±(\d+) \(2mR~500mR\)", "HoJLR2512 sheet p.2 TCR from 2 to 500 mOhm").group(1)) * 1e-6
    need(hoj, r"Resistance range 0\.5mR~500mR", "HoJLR2512 sheet p.2 the range")
    need(hoj, r"Rated power 2W\S3W", "HoJLR2512 sheet p.2 the rated power")
    t_op = [float(v) for v in need(hoj, r"Operating Temperature Range -(\d+)℃~\+(\d+)℃", "HoJLR2512 sheet p.2 the operating range").groups()]
    t_knee = float(need(hoj, r"电阻温度达到 (\d+)℃时降功率", "HoJLR2512 sheet p.2 the derating knee").group(1))
    vals = sorted({(float(mm.group(1)) * 1e-3, row["code"]) for row in cat["rows"] for mm in [re.fullmatch(r"HoJLR2512-3W-([\d.]+)mR-1%", row["model"])]
                   if mm and row["stock"] and RB_RANGE[0] <= float(mm.group(1)) * 1e-3 <= RB_RANGE[1]})
    rb_tol = 0.01 + hoj_tcr * RB_DT
    can_l = (CAN_ESL[0] + RB_ESL[0], CAN_ESL[1] + RB_ESL[1] + LAYOUT[0])
    can_c = (CAN_C_LIFE[0] * mk["c_can"], CAN_C_LIFE[1] * mk["c_can"])

    def can_reg(rb_):
        """one can's branch region: its ballast at either end of its tolerance, its ESR from 0 to the sheet's cold limit, the
        layout's allowance, its ESL with the ballast's, C over the sheet's tolerance and endurance; every can the same region"""
        return dict(r=(rb_ * (1 - rb_tol), rb_ * (1 + rb_tol) + mk["esr_cold"] + LAYOUT[1]), l=can_l, c=can_c)
    hfv = [(si(G["one"][k][1], ""), e) for k, e in (("C190", hf[0][1]), ("C191", hf[1][1]))]
    regs = dict(cer=dict(r=(bands["cer_esr"][0], bands["cer_esr"][-1]), l=(bands["cer_esl"][0], bands["cer_esl"][-1]),
                         c=(bands["cer_c"][0], bands["cer_c"][-1])),
                c190=dict(c=(HF_BAND["c"][0] * hfv[0][0], HF_BAND["c"][1] * hfv[0][0]), r=(HF_BAND["esr"][0] * hfv[0][1], HF_BAND["esr"][1] * hfv[0][1]),
                          l=HF_BAND["esl"]),
                c191=dict(c=(HF_BAND["c"][0] * hfv[1][0], HF_BAND["c"][1] * hfv[1][0]), r=(HF_BAND["esr"][0] * hfv[1][1], HF_BAND["esr"][1] * hfv[1][1]),
                          l=HF_BAND["esl"]),
                l11=(bands["l11"][0], bands["l11"][-1]), l16=(bands["l16"][0], bands["l16"][-1]), r16=(r16 * (1 - rb_tol), r16 * (1 + rb_tol)),
                r_tol=rb_tol, n_fe=drawn[2], n_vb=drawn[1], n_can=drawn[0])
    BN = BoundNode(regs, vout, l1, l2)
    for o in out:
        BN.set_r11(o["r11"])
    lim = {o["key"]: rating - MARGIN_PER_A * o["hi"] for o in out}
    vbats_b = lin(grid["vbat"][0], grid["vbat"][1], int(round((grid["vbat"][1] - grid["vbat"][0]) / BOUND["dvb"])) + 1)

    def bfig(rb_, o):
        can = can_reg(rb_)
        if (o["r11"], can["r"][0]) not in BN.T:
            BN.set_target(o["r11"], can)
        return BN.combine(o["r11"], can["r"][0], o["hi"], (fenv[0], fenv[2]), rows_ch, vbats_b)

    def feasible(rb_, o):
        """ONE configuration inside every region (a lower value): the target at the ballast's low end, no ESR, the shortest
        branch and the largest C; its five siblings at the region's top R and L, the largest C; ceramics at 4 uF, 2 mOhm, 1.5 nH;
        L16 20 nH, L11 5 nH; the front end's fundamental on the charger's at fch = 2 fsw, the envelope's low corner, VIN 9 V, VBAT
        10 V, at the worst phase (60 harmonics)"""
        bx = dict(c=[can_c[1]], r=[0.0, mk["esr_cold"]], l=[can_l[0], can_l[1] - LAYOUT[0]])
        Mc = Model(vout, l1, l2, [vins[0]], [fenv[0]], [grid["vbat"][0]], [2 * fenv[0]])
        nd = GNode(Mc, bands, drawn, o["r11"], r16, hf, bx, rb_, rb_tol, LAYOUT)
        sx = (0, 0, 0, 0, 1, 1, 0, len(bands["cer_esl"]) - 1, 0, len(bands["l16"]) - 1, len(bands["l11"]) - 1)
        return math.sqrt(coherent(nd, sx, Mc, o["hi"], rows_ch, op=(Fraction(2), fenv[0], vins[0], grid["vbat"][0]))[0])
    # the decision (SESSION): catalogue values ascending from RB_START, the binding 7 mOhm outcome first; the first whose bound meets
    # the rule at BOTH outcomes is taken. Below RB_START a feasible configuration is over the limit at 7 mOhm, so no bound can meet it
    BF, pick = {}, None
    for rb_, code in [v for v in vals if v[0] >= RB_START - 1e-12]:
        BF[("7", rb_)] = bfig(rb_, o7)
        if BF[("7", rb_)]["fig"] > lim["7"]:
            continue
        BF[("8", rb_)] = bfig(rb_, o8)
        if BF[("8", rb_)]["fig"] <= lim["8"]:
            pick = (rb_, code)
            break
    if pick is None:
        refuse(4, "no catalogue ballast's bound meets the rule at both outcomes")
    rb = pick[0]
    FEAS = {("7", v): feasible(v, o7) for v, _c in vals if v < RB_START - 1e-12}
    FEAS.update({(o["key"], v): feasible(v, o) for o in out for v, _c in vals if RB_START - 1e-12 <= v <= rb + 1e-12})
    R.update(BF=BF, FEAS=FEAS, pick=pick, lim=lim, vals=vals, rb_tol=rb_tol, hoj_tcr=hoj_tcr, regs=regs, can_reg=can_reg(rb), nbins=BN.nb,
             ncells=(len(BN.FC[o8["r11"]][0]), len(BN.ch_cells)), band=(BN.E[BN.band[0]], BN.E[BN.band[-1] + 1]), vin_b=VIN_BOUND, vbat_b=vbats_b)
    sel = {o["key"]: BF[(o["key"], rb)] for o in out}
    # the bound checked against brute-force sampling (a seeded pseudo-random sample of fully independent configurations)
    R["brute"] = brute_check(BN, regs, can_reg(rb), out, (fenv[0], fenv[2]), rows_ch, vbats_b, sel, BRUTE)
    # 6b. the rating at frequency and temperature, the ballast, the energy term
    t_air = R["b3"]["t_air"]

    def life(t2, dt):
        return min(mk["life_h"] * 2 ** ((mk["t_cat"] - (t2 + dt)) / 10.0), mk["life_cap_y"] * 8760.0)
    t_local = float(need(t6, r"so the qualifying temperature is (\d+) C", "L4-E6's L1 qualifying temperature").group(1))
    R["life"] = dict(t_air=t_air, t_local=t_local, table=[(dt, life(t_air, dt), life(t_local, dt)) for dt in LIFE_DT])
    fmin = min(fenv[0], rows_ch[0][0])
    corr_at = [f_ for f_, _c in mk["corr"] if f_ <= fmin][-1]
    R["freq"] = dict(fmin=fmin, corr_at=corr_at, corr_min=min(c_ for f_, c_ in mk["corr"] if f_ >= corr_at))
    figmax = max(sel[k]["fig"] for k in sel)
    p_rb = figmax ** 2 * rb * (1 + rb_tol)
    derate = lambda t: 3.0 * min(1.0, max(0.0, (t_op[1] - t) / (t_op[1] - t_knee)))
    R["ballast"] = dict(p=p_rb, t_op=t_op, knee=t_knee, rating=[(t, derate(t)) for t in (t_air, t_local, 100.0)], t_lo=R["b3"]["t_min"],
                        dt=RB_DT, sum_upper=drawn[0] * p_rb)
    # the energy model's term: an illustration at nominal parts (not a measurement), RSS (no coincidence at these frequencies)
    tp = dict(TYPICAL, fsw=fenv[1])
    Mt = Model(vout, l1, l2, [tp["vin"]], [tp["fsw"]], [tp["vbat"]], [tp["fch"]])
    bxt = dict(c=[mk["c_can"]], r=[mk["esr_can"]], l=[tp["can_l"]])
    bnd_t = dict(bands, cer_c=[tp["cer"][0]], cer_esr=[tp["cer"][1]], cer_esl=[tp["cer"][2]], l16=[tp["l16"]], l11=[tp["l11"]])
    ndt = GNode(Mt, bnd_t, drawn, o8["r11"], r16, hf, bxt, rb, 0.0, (0.0, 0.0))
    mst = exact(ndt.vectors((0,) * 11, ("odd",))["odd"], Mt.weights(tp["iout"]))[0]
    R["typical"] = dict(tp, ms=mst, p=drawn[0] * mst * rb)
    # ---------------------------------------------------------------- 7. the loop with the ballast over the cold envelope (R4)
    lc_ = open(os.path.join(TOP, LCSC_FILL), encoding="utf-8").read()
    cc2_vals = sorted({(si(mm.group(1).replace("\\", "") + mm.group(2), ""), mm.group(1).replace("\\", "") + mm.group(2), mm.group(3))
                       for mm in re.finditer(r'\(r"\^([\d\\.]+)([pn])\$?", "C_0603"\): "(C\d+)"', lc_)})
    comp_drawn = comp

    def bulk_of(rb_, e):
        """the loop's bulk corners: C at the sheet's extremes, each branch the ballast at either end of its tolerance plus the
        can's intrinsic ESR e"""
        return [(k * mk["c_can"], x) for k in CAN_C_LIFE for x in (rb_ * (1 - rb_tol) + e, rb_ * (1 + rb_tol) + e)]

    def lp(rcs, ld, cmp_, bulk=None, banks=None):
        return tuple(loop_eval(lcfg_e, drawn[0], ncer_drawn, rcs, *cmp_, bulk=bulk, banks=banks, iouts=ld, p_bound=vout * ld[0], **kw)
                     for kw in ({}, dict(qs=rec["wide"]["q"], lks=rec["wide"]["lk"])))

    def lok(pair):
        return all(x["pm"] >= 50 and x["gm"] >= 10 and x["mm"] >= 0.5 and x["ceil_ok"] and x["all_cross"] and x["z_ratio"] <= 1.0 for x in pair)
    loads = sorted({o7["hi"], o8["hi"], rec["loop_stage"]["iout"], 0.25}, reverse=True)
    rec_loads = [rec["loop_stage"]["iout"], 0.25]
    ends = (0.0, mk["esr_cold"])
    env_e = [round(i * LOOP_STEP, 6) for i in range(int(round(mk["esr_cold"] / LOOP_STEP)) + 1)]
    LD = {e: lp(R12_E6, loads, comp_drawn, bulk=bulk_of(rb, e)) for e in ends}
    # the compensation (SESSION): Cc2 ascending through lcsc_fill.py's 0603 capacitors from the drawn value, Rc1 and Cc1 kept; the
    # first that meets every margin at both ends of the envelope and then over the whole envelope, its tolerance and mixed banks
    LCMP, cpick = {}, None
    for cval, ctext, ccode in [x for x in cc2_vals if x[0] >= comp_drawn[2] * (1 - 1e-9)]:
        cmp_ = (comp_drawn[0], comp_drawn[1], cval)
        if cval == comp_drawn[2]:
            LCMP[ctext] = LD
        else:
            LCMP[ctext] = {e: lp(R12_E6, loads, cmp_, bulk=bulk_of(rb, e)) for e in ends}
        if all(lok(LCMP[ctext][e]) for e in ends):
            cpick = (cval, ctext, ccode)
            break
    if cpick is None:
        refuse(4, "no 0603 Cc2 of lcsc_fill.py meets the loop's margins at both ends of the cold envelope")
    cmp_new = (comp_drawn[0], comp_drawn[1], cpick[0])
    LENV = {e: (LCMP[cpick[1]][e] if e in ends else lp(R12_E6, loads, cmp_new, bulk=bulk_of(rb, e))) for e in env_e}
    LTOL = {(k, e): lp(R12_E6, loads, (comp_drawn[0], comp_drawn[1], cpick[0] * k), bulk=bulk_of(rb, e)) for k in CC2_TOL for e in ends}
    mixes = [[(nk, can_c[ia], rb * (1 - rb_tol)), (drawn[0] - nk, can_c[ib], rb * (1 + rb_tol) + mk["esr_cold"])]
             for nk in range(1, drawn[0]) for ia in (0, 1) for ib in (0, 1)]
    LMIX = lp(R12_E6, loads, cmp_new, banks=mixes)
    LORD = {e: lp(rcs_drawn, rec_loads, cmp_new, bulk=bulk_of(rb, e)) for e in ends}
    R.update(LD=LD, LCMP=LCMP, cpick=cpick, LENV=LENV, LTOL=LTOL, LMIX=LMIX, LORD=LORD, loads=loads, rec_loads=rec_loads, r12_e6=R12_E6,
             rcs_drawn=rcs_drawn, comp_drawn=comp_drawn, env_e=env_e, nmix=len(mixes))
    # ---------------------------------------------------------------- 8. what the bank's capacitance moves: unchanged (first order, INFERRED)
    ss, ring, bl = rec["ss"], rec["ring"], rec["bleed"]
    div = 1 + si(G["rfb_top"], "") * 1.01 / (si(G["rfb_bot"], "") * 0.99)
    css = si(G["css"][0], "") * ss["css_k"]
    cmax = drawn[0] * mk["c_can"] * ss["ck"] + (drawn[1] + drawn[2]) * 10e-6 * rec["node_max"][2]
    cmin = drawn[0] * mk["c_can"] * 0.8 + (drawn[1] + drawn[2]) * bands["cer_c"][0]
    i_ = cmax * div * mk["iss"][2] / css + rec["bias"]
    ramp = [100 * i_ * ss["vbus"] / ss["eta"] / v / rec["entry"] for v in (9.0, 12.0, 13.8)]
    tau = (bl["r"][0] * cmin, bl["r"][1] * cmax)
    bleed = (tau[0] * math.log(rec["bank_range"][0] / rec["release"][2]), tau[1] * math.log(bl["v"] / rec["release"][0]))
    ringv = (ring["v"] * math.sqrt(cmax / (l1 * ring["lk"])), 0.5 * cmax * ring["v"] ** 2 * 1e3)
    R["cons"] = dict(cmax=cmax, cmin=cmin, ramp=ramp, tau=tau, bleed=bleed, ring=ringv)
    # the same first-order consequences over the cans' endurance range (the decision's C range), not only their initial +-20 %
    cmax_e = drawn[0] * mk["c_can"] * CAN_C_LIFE[1] + (drawn[1] + drawn[2]) * 10e-6 * rec["node_max"][2]
    cmin_e = drawn[0] * mk["c_can"] * CAN_C_LIFE[0] + (drawn[1] + drawn[2]) * bands["cer_c"][0]
    i_e = cmax_e * div * mk["iss"][2] / css + rec["bias"]
    tau_e = (bl["r"][0] * cmin_e, bl["r"][1] * cmax_e)
    R["cons_e"] = dict(cmax=cmax_e, cmin=cmin_e, ramp9=100 * i_e * ss["vbus"] / ss["eta"] / 9.0 / rec["entry"], tau=tau_e,
                       bleed=(tau_e[0] * math.log(rec["bank_range"][0] / rec["release"][2]), tau_e[1] * math.log(bl["v"] / rec["release"][0])),
                       ring=(ring["v"] * math.sqrt(cmax_e / (l1 * ring["lk"])), 0.5 * cmax_e * ring["v"] ** 2 * 1e3), isat=ring["isat"])
    R["cons_ok"] = (all(abs(round(x, 1) - y) < 1e-9 for x, y in zip(ramp, ss["pct"])) and abs(round(ringv[0], 1) - ring["pk"]) < 1e-9
                    and abs(round(ringv[1], 2) - ring["mj"]) < 1e-9 and abs(round(cmax * 1e3, 2) - rec["node_max"][0]) < 1e-9
                    and abs(round(tau[1], 2) - bl["tau"][1]) < 1e-9 and abs(round(tau[0], 2) - bl["tau"][0]) < 1e-9)
    # ---------------------------------------------------------------- 9. predicates
    cv_can = [(k, math.sqrt(v["conv"][0]) - math.sqrt(v["base"]), wv[k[1]]["iout"]) for k, v in CV.items() if k[2] == "odd"]
    R["cv_can"] = cv_can
    P = [
        ("consistency: the derivation meets every recorded dense can figure within %.2f A and the re-review's point within %.4f A" % (TOL_DENSE, TOL_POINT),
         all(r["ok"] for r in R["vrows"])),
        ("consistency: the loop model meets the recorded margins within the stated tolerances", all(abs(g - w) <= t for _k, w, g, t in lrows)),
        ("convergence: on the finer source grids every can figure of the drawn node moves by less than the rule's margin",
         all(abs(dv) <= MARGIN_PER_A * i_ for _k, dv, i_ in cv_can)),
        ("the full enumeration of the second fix-up's node equals the search's maximum and counts the record's sets over the rating",
         not R["count"]["above_search"] and (over, nset) == rec["second_count"]),
        ("B1: the check's counterexample reproduces, 2.8546 A on its 204 / 816 kHz coincidence against its 2.7375 A in mean square",
         abs(cx["4"][1] - 2.854635) < 0.0005 and abs(cx["rss"][0] - 2.738774) < 0.0005 and abs(cx["2"][1] - 2.813686) < 0.0005),
        ("B2: the check's ESL counterexample reproduces, 3.5870 A with the siblings at 3.5 nH plus the layout's 0.5 nH",
         abs(cx["esl"][0] - 3.586976) < 0.0005),
        ("B3: the envelope covers the specified row's low corner carried to RT, under the record's 180.3 kHz", fenv[0] < fsw_lo and fenv[2] > fenv[1] > fenv[0]),
        ("the drawn bank does NOT meet 2.8 A at the 2:1 spread at either outcome on the corrected model", E[("8", 2.0)]["coh"] > rating and E[("7", 2.0)]["coh"] > rating),
        ("B2: without a resistance floor no can count bounds the per-can current (the drawn six and eight cans both read over 10 A)",
         all(math.sqrt(U[n_]["ms"]) > 10.0 for n_ in U)),
        ("R1/R2: the BOUND over arbitrary independent branches meets the rule at both outcomes with the chosen ballast",
         all(sel[k]["fig"] <= lim[k] for k in sel)),
        ("R1/R2: no smaller catalogue value can be shown to meet it: below %.0f mOhm a feasible configuration is over the limit at"
         " 7 mOhm, from it to the chosen value the bound is over it" % (RB_START * 1e3),
         all(FEAS[("7", v)] > lim["7"] for v, _c in vals if v < RB_START - 1e-12)
         and all(BF[("7", v)]["fig"] > lim["7"] or BF[("8", v)]["fig"] > lim["8"] for v, _c in vals if RB_START - 1e-12 <= v < rb - 1e-12)),
        ("R1/R2: the bound is conservative against the seeded brute-force sample, per bin and end to end",
         R["brute"]["bin"] <= 1.0 and R["brute"]["e2e"] <= 1.0),
        ("the rating applies unmodified in frequency: every harmonic at or above %.0f kHz, where the sheet's correction is %.2f" % (fmin / 1e3, R["freq"]["corr_min"]),
         R["freq"]["corr_min"] == 1.0 and fmin >= R["freq"]["corr_at"]),
        ("the ballast's own loss is under a fifth of its derated rating at 100 C", p_rb <= derate(100.0) / 5),
        ("R4: with the chosen Cc2 the loop meets PM >= 50 deg, GM >= 10 dB, |1+T| >= 0.5, every crossover ceiling and the impedance"
         " bound over the whole cold envelope, Cc2's tolerance and the mixed banks, at R12 %.0f mOhm, loads to the highest permitted"
         " current, default and widened bands" % (R12_E6 * 1e3),
         all(lok(v) for v in LENV.values()) and all(lok(v) for v in LTOL.values()) and lok(LMIX)),
        ("R4: the drawn compensation with the ballast misses GM >= 10 dB at the cold end of the envelope", LD[mk["esr_cold"]][1]["gm"] < 10),
        ("the first-order consequences reproduce the generator's recorded soft-start draw, bleed tau, node maximum and restart ring", R["cons_ok"]),
        ("the consequences over endurance reproduce the recheck's 1.1928 to 3.3198 mF, 16.1338 A, 1.0412 mJ, 10.2748 % and 0.455 to 1.494 s",
         abs(R["cons_e"]["cmin"] - 1.1928e-3) < 1e-7 and abs(R["cons_e"]["cmax"] - 3.3198e-3) < 1e-7 and abs(R["cons_e"]["ring"][0] - 16.1338) < 1e-3
         and abs(R["cons_e"]["ring"][1] - 1.0412) < 1e-3 and abs(R["cons_e"]["ramp9"] - 10.2748) < 1e-3
         and abs(R["cons_e"]["bleed"][0] - 0.455) < 1e-3 and abs(R["cons_e"]["bleed"][1] - 1.494) < 1e-3),
        ("ORDER: on the drawn R12 the ballast with the chosen Cc2 misses a margin at an end of the envelope (so they go in with L4-E6's R12)",
         not all(lok(v) for v in LORD.values())),
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
    P("L4-E8: BOARD A'S VBUS20 BULK BANK RE-SIZED ON A DERIVED DENSE NODE ANALYSIS, FIX ROUND (ripple_dense.py, MESHSAT-1357, 1 October 2026).")
    P("PROTOTYPE DESIGN: nothing bought, built, powered or measured; no generator, registry, rendered page or L4-E4 to L4-E7 record edited.")
    P("Labels: MAKER, NETLIST, GENERATOR, RECORD, INFERRED, ASSUMPTION, SESSION, MODELED, INCONCLUSIVE.")
    P("")
    P("0. INPUTS AND REPRODUCTIONS")
    for rel, want in PINS.items():
        P("   %-48s sha256 %s (pinned)" % (rel, want[:16]))
    for t, h, _held in PT.inputs(TOP, PDFTEXT):
        P("   %-48s sha256 %s (pinned)" % (t, (h or "ABSENT")[:16]))
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
    P("     harmonic here (the lowest %.1f kHz, B3's envelope) counts at the full rating; ESR after endurance at most 200 %% of the initial" % (R["b3"]["env"][0] / 1e3))
    P("     limit (p.1), and at most %.0f mOhm at %.0f C after endurance for size %s (p.1, the 331P's size code on p.2);" % (
        mk["esr_cold"] * 1e3, mk["t_cold"], mk["size"]))
    P("     parallel parts: 'use capacitors with the same part number' (p.7)")
    P("   MAKER TI SNVSAI1D rev. D (%s): fSW(1) %.0f / %.0f / %.0f kHz at RT %.0f k (p.6), Equation 5's 116 pF and 190 ns (p.17)," % (
        LM5176, mk["fsw_row"][0] / 1e3, mk["fsw_row"][1] / 1e3, mk["fsw_row"][2] / 1e3, mk["rt_row"] / 1e3))
    P("     so RT %s sets %.2f kHz; the first round's band %.2f to %.2f kHz (sections 3 and 4 only; B3's envelope, section 5); gmEA %.2f mS, ROUT %.0f MOhm, VREF %.3f V," % (
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
    P("     charger's at its worst (VBAT, fch), per part (the two are not synchronised): the record's rule, used in sections 4 and 4b;")
    P("     section 5b adds the coincident harmonics at the worst phase (B1)")
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
    vr = [x["rounds"] for v in R["V"].values() for x in v.values()]
    P("   the drawn node's six runs: %d of the record's %d sets over 2.8 A in any of them (RECORD); the search's stage 3 re-climbed in" % rec["third_count"])
    P("     %d of its %d validation runs (%d round(s) in all); every maximum of this section holds its whole dense ESL x C slice under it" % (
        sum(1 for x in vr if x), len(vr), sum(vr)))
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
    P("   VBAT every %.2f V, fSW every %.1f kHz, the charger every %.0f kHz, then climbed on the dense passive grid; and with %d harmonics)" % (
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
    P("5. THE DRAWN BANK ON THE CORRECTED MODEL")
    b3 = R["b3"]
    P("   B3, the front end's frequency envelope: SNVSAI1D p.6's fSW(1) %.0f / %.0f / %.0f kHz at RT %.0f k, carried by Equation 5 (p.17) to RT" % (
        mk["fsw_row"][0] / 1e3, mk["fsw_row"][1] / 1e3, mk["fsw_row"][2] / 1e3, mk["rt_row"] / 1e3))
    P("     %s at %.0f %% (%s, %s, lcsc_fill.py) and %.0f ppm/K over %.1f K (UNI-ROYAL sheet p.6, 0603 above 10 Ohm; %.0f C in use to %.1f C" % (
        G["rt"].split()[0], 100 * b3["tol"], b3["part"], b3["code"], b3["tcr"] * 1e6, b3["dt"], b3["t_min"], b3["t_air"]))
    P("     inside air): %.2f / %.2f / %.2f kHz (INFERRED: the row's spread kept, Equation 5 scaling each end; nominal RT's factor %.5f)." % (
        b3["env"][0] / 1e3, b3["env"][1] / 1e3, b3["env"][2] / 1e3, b3["scale"]))
    P("     The first round's 180.29 to 231.81 kHz recentred the row on Equation 5's %.2f kHz, as the lost loop script did (INFERRED from" % (R["fsw"][0] / 1e3))
    P("     its recovered draft); section 4 keeps that band only to compare with the record")
    D = R["D"]
    P("   the record's sharing (one can at the corner's ESR, its siblings at s times it), at %.3f A, step by step (RSS until the last row):" % o8["hi"])
    P("   | step | matched | 1.5:1 | 2:1 |")
    P("   | r11_dep.py's linear scaling of the recorded figures | %.3f A | %.3f A | %.3f A |" % tuple(o8["lin"]))
    for tag, lab in (("record", "the record's network (L2 %.1f uH, R11 %.0f mOhm) on the record's grids" % (rec["l2_old"] * 1e6, R["r11_drawn"] * 1e3)),
                     ("L2", "with L2 %.1f uH, as drawn since S-117" % (R["l2"] * 1e6)), ("R11", "with R11 %s mOhm in the network" % o8["key"]),
                     ("grids", "on converged source grids (4b's)"), ("B3", "on B3's envelope (converged)"), ("coh", "with the coincidences at worst phase (B1)")):
        P("   | %s | %.3f A | %.3f A | %.3f A |" % (lab, D[(tag, 1.0)], D[(tag, 1.5)], D[(tag, 2.0)]))
    E = R["E"]
    for o in R["outcomes"]:
        e = [E[(o["key"], sp)] for sp in (1.0, 1.5, 2.0)]
        P("   R11 %s mOhm, %.3f A, corrected: %s A (matched / 1.5:1 / 2:1; mean square %s A) against %.1f A: %s" % (
            o["key"], o["hi"], " / ".join("%.3f" % x["coh"] for x in e), " / ".join("%.3f" % x["rss"] for x in e), rating,
            "NOT MET at 2:1" if e[2]["coh"] > rating else "met"))
        op = e[2]["op"]
        if op:
            P("     2:1's worst coincidence: fch / fsw = %s at %.2f / %.2f kHz, VIN %g V, VBAT %.2f V" % (op[0], op[1] / 1e3, op[2] / 1e3, op[3], op[4]))
    U, bx0 = R["U"], R["box0"]
    P("   B2, every can independent over the sheet's bands (C %.2f to %.2f x %.0f uF, ESR 0 to %.0f mOhm with NO floor, ESL %.1f to %.1f nH;" % (
        R["box_sheet"]["c_k"][0], R["box_sheet"]["c_k"][1], mk["c_can"] * 1e6, R["box_sheet"]["r_hi"] * 1e3, bx0["l"][0] * 1e9, bx0["l"][-1] * 1e9))
    P("     no ballast), at %.3f A:" % o8["hi"])
    for nb_, g in sorted(U.items()):
        pr = g["set"]
        P("     %d cans: %.1f A, the target at ESR %.0f mOhm, the siblings at %.0f mOhm: with no resistance floor the node is undamped" % (
            nb_, math.sqrt(g["ms"]), bx0["r"][pr[1]] * 1e3, bx0["r"][pr[4]] * 1e3))
    P("     and no number of cans bounds a can's current; screening the ESR before fitting does not bound it over life (p.1's 200 %)")
    P("   the check's B2 counterexample (the eight-can corner printed in 5b, with the siblings' own ESL at the band's %.1f nH plus the" % (
        b["esl_b"][-1] * 1e9))
    P("     layout's %.1f nH, ESR still 2:1): %.4f A in mean square at 198.8 / 816 kHz (the check: 3.586976). Section 6's box spans that" % (
        LAYOUT[0] * 1e9, R["cx"]["esl"][0]))
    P("     corner's can parameters, every branch adding its ballast's own inductance")
    P("")
    P("5b. B1, THE COMBINATION RULE (SESSION, from what the rating is)")
    P("   The 2.8 A is a thermal rating (MAKER p.1: 4000 h at 125 C with the rated ripple applied). Two harmonics at f1 and f2 heat as")
    P("   i^2: their cross term beats at |f1 - f2|, and the can's temperature follows a beat slower than its thermal time constant and")
    P("   averages a faster one. The sheet prints no time constant; %.0f s is taken as its shortest (ASSUMPTION), so a beat under" % TAU_TH)
    P("   1 / (2 pi tau) = %.2f Hz heats as coherent at the worst relative phase, and a faster one in mean square. Both converters'" % (1 / (2 * math.pi * TAU_TH)))
    P("   frequencies are continuous bands and the two oscillators are independent, so EXACT coincidence p fsw = q fch is permitted:")
    P("   the worst case sits on it, whatever the time constant. The rule: on every permitted ratio p / q with p <= %d, fsw along the" % COH_PMAX)
    P("   line every %.1f kHz inside both bands, every VIN and VBAT, the coincident pairs (p m, q m) add with one common time shift" % (COH_DF / 1e3))
    P("   maximised, the rest in mean square (section 5's drawn bank); section 6's bound takes every order, p > %d by Cauchy-Schwarz" % COH_PMAX)
    cx = R["cx"]
    P("   the check's counterexample (eight cans, 396 uF, the low-ESR can 6 mOhm and 1.5 nH, its siblings 12.5 mOhm and 2.0 nH, ceramics")
    P("     4 uF, 2 mOhm, 1.5 nH; VIN 9 V, VBAT 10 V, %.4f A): %.4f A in mean square at 198.8 / 816 kHz (the check: 2.738774); %.4f A at" % (
        o8["hi"], cx["rss"][0], cx["4"][1]))
    P("     204 / 816 kHz, the front end's 4th harmonic on the charger's fundamental (the check: 2.854635); %.4f A at 204 / 408 kHz" % cx["2"][1])
    P("     (the check: 2.813686). The rule puts both inside: exact coincidences, coherent at the worst phase; that bank fails")
    P("")
    P("6. THE BOUND (the recheck's R1/R2): EVERY CAN OVER ARBITRARY INDEPENDENT SIBLINGS, NO SAMPLING DECIDES IT")
    rg, cr = R["regs"], R["can_reg"]
    P("   The regions, every branch independent of every other (each harmonic may take its own worst set: only an overstatement):")
    P("   - each can: R %.2f to %.2f mOhm (its ballast at either end of %.2f %%, its ESR 0 to size %s's %.0f mOhm, the layout's %.1f mOhm)," % (
        cr["r"][0] * 1e3, cr["r"][1] * 1e3, 100 * R["rb_tol"], mk["size"], mk["esr_cold"] * 1e3, LAYOUT[1] * 1e3))
    P("     L %.1f to %.1f nH (the can's INFERRED band, the ballast's, the layout's %.1f nH), C %.1f to %.1f uF (MAKER, +-%.0f %% and +-%.0f %%)" % (
        cr["l"][0] * 1e9, cr["l"][1] * 1e9, LAYOUT[0] * 1e9, cr["c"][0] * 1e6, cr["c"][1] * 1e6, 100 * mk["c_tol"], 100 * mk["c_life"]))
    P("   - each ceramic, %d on VBUS20 and %d on FE_OUT: C %.1f to %.1f uF, ESR %.0f to %.0f mOhm, ESL %.2f to %.2f nH (RECORD, INFERRED)" % (
        rg["n_vb"], rg["n_fe"], rg["cer"]["c"][0] * 1e6, rg["cer"]["c"][1] * 1e6, rg["cer"]["r"][0] * 1e3, rg["cer"]["r"][1] * 1e3,
        rg["cer"]["l"][0] * 1e9, rg["cer"]["l"][1] * 1e9))
    P("   - C190 %.1f to %.1f nF, %.0f to %.0f mOhm; C191 %.2f to %.2f nF, %.0f to %.0f mOhm; both %.1f to %.1f nH (ASSUMPTION: no maker figure" % (
        rg["c190"]["c"][0] * 1e9, rg["c190"]["c"][1] * 1e9, rg["c190"]["r"][0] * 1e3, rg["c190"]["r"][1] * 1e3, rg["c191"]["c"][0] * 1e9,
        rg["c191"]["c"][1] * 1e9, rg["c191"]["r"][0] * 1e3, rg["c191"]["r"][1] * 1e3, HF_BAND["esl"][0] * 1e9, HF_BAND["esl"][1] * 1e9))
    P("     held for C57112 or C1588; the predecessor's ESR the least damping end)")
    P("   - L11 %.0f to %.0f nH and L16 %.0f to %.0f nH (RECORD, INFERRED); R11 and R16 at +-%.2f %% (the HoJLR2512's 1 %% and 50 ppm/K over %.0f K)" % (
        rg["l11"][0] * 1e9, rg["l11"][1] * 1e9, rg["l16"][0] * 1e9, rg["l16"][1] * 1e9, 100 * rg["r_tol"], RB_DT))
    P("   The method, per bin of frequency (%d bins from %.0f kHz to %.1f GHz, 0.5 %% wide to 3 MHz, 1 %% to 30 MHz, 4 %% above):" % (
        R["nbins"], BOUND["f0"] / 1e3, BOUND["f_end"] / 1e9))
    P("   - a branch's impedance R + jX lies in a rectangle (X = wL - 1/(wC) rises with w, L and C, each over its interval, the bin's w")
    P("     taken branch by branch); its admittance in the image under 1/z, bounded by arcs of circles through the origin, enclosed by")
    P("     the hull of arc samples grown by their largest sagitta (sagitta at most %.0e of the image's largest modulus)" % BOUND["rel"])
    P("   - sums of independent branches in the Minkowski sum of their enclosures (n alike: n times one); the sources' links in")
    P("     rectangles; a source side's shunt Y_s = 1/(Z_link + 1/Y_shunt) in the hull of the inverted sum")
    P("   - the can's current per ampere of a source: k Y / (Y + Y_rest); |k| = 1 / |1 + Z_link Y_shunt| bounded by a branch and bound")
    P("     over the link's rectangle (exact distance to the shunt's polygon, the sub-rectangle's radius by the triangle inequality);")
    P("     |Y| / |Y + Y_rest| bounded by a branch and bound over the can's rectangle (each sub-rectangle's disk inverted exactly)")
    P("   - the source sides' resonances are not decoupled across harmonics: L11 in %d cells, (L16, C190) in %d cells, each cell's" % R["ncells"])
    P("     bound per bin, the worst cell taken (the charger side's factor exceeds %.2f from %.1f to %.1f MHz: the L16 and C190 series" % (
        BOUND["cell_thr"], R["band"][0] / 1e6, R["band"][1] / 1e6))
    P("     resonance and C191's above it)")
    P("   - the sources: closed-form Fourier coefficients to the %dth harmonic; fSW in %.1f kHz intervals over B3's envelope and fCH in %.0f kHz" % (
        BOUND["nh"], BOUND["dfs"] / 1e3, BOUND["dfc"] / 1e3))
    P("     intervals over both rows, each harmonic at the larger of its ends (convex in the ripple, which is 1/f) and at the largest bin")
    P("     bound over its frequency interval; VIN %g to %g V on %d points (every 0.5 V of the boost range) and VBAT every %.2f V (the" % (
        R["vin_b"][0], R["vin_b"][-1], len(R["vin_b"]), BOUND["dvb"]))
    P("     operating grid: sampled, not bounded); exact coincidences fch / fsw = p / q, p <= %d, added coherently (|a| + |c| at every" % BOUND["p0"])
    P("     coincident frequency, any phase), every higher order by Cauchy-Schwarz; above the %dth harmonic |c_m| <= J/(2 pi m) +" % BOUND["nh"])
    P("     K/(2 pi m)^2 (J the waveform's jumps, K its slope jumps) at the bins' bound, and |T| <= 1 above %.1f GHz (every branch inductive" % (
        BOUND["f_end"] / 1e9))
    P("     there, so no sum of them is smaller than one of them)")
    P("   The decision (SESSION): catalogue values ascending from %.0f mOhm, the binding 7 mOhm outcome first; the first whose bound meets" % (RB_START * 1e3))
    P("   the rule at both outcomes is taken. Below %.0f mOhm one feasible configuration (feasible() in the source) is over the limit at" % (RB_START * 1e3))
    P("   7 mOhm, so no bound can meet it:")
    P("   | ballast | 7 mOhm, 8.300 A: bound | feasible | 8 mOhm, 7.262 A: bound | feasible | outcome |")
    for v, code in R["vals"]:
        if v > R["pick"][0] + 1e-12:
            break
        b7, b8 = R["BF"].get(("7", v)), R["BF"].get(("8", v))
        f7, f8 = R["FEAS"].get(("7", v)), R["FEAS"].get(("8", v))
        if v == R["pick"][0]:
            outc = "TAKEN"
        elif b7 is not None and b7["fig"] > R["lim"]["7"]:
            outc = "the bound does not meet the rule at 7 mOhm"
        elif b8 is not None and b8["fig"] > R["lim"]["8"]:
            outc = "the bound does not meet the rule at 8 mOhm"
        else:
            outc = "excluded: feasible over %.4f A" % R["lim"]["7"]
        P("   | %.0f mOhm (%s) | %s | %s | %s | %s | %s |" % (v * 1e3, code, ("%.4f A" % b7["fig"]) if b7 else "-", ("%.4f A" % f7) if f7 is not None else "-",
                                                     ("%.4f A" % b8["fig"]) if b8 else "-", ("%.4f A" % f8) if f8 is not None else "-", outc))
    rb_, code_ = R["pick"]
    P("   CHOSEN: six EEHZK1V331P as drawn, each in series with a %.0f mOhm 1 %% 2512 ballast, Milliohm HoJLR2512-3W-%.0fmR-1%%, LCSC %s" % (rb_ * 1e3, rb_ * 1e3, code_))
    P("     (in stock in L4-E4's catalogue reading); the ceramics as drawn")
    for o in R["outcomes"]:
        bf = R["BF"][(o["key"], rb_)]
        P("   R11 %s mOhm, %.3f A: every can at most %.4f A against %.4f A (%s); the FE's part %.3f A^2, the charger's %.3f A^2 (each at its" % (
            o["key"], o["hi"], bf["fig"], R["lim"][o["key"]], "meets" if bf["fig"] <= R["lim"][o["key"]] else "FAILS", bf["feM"], bf["chM"]))
        P("     worst interval), harmonics above the %dth %.4f / %.4f A^2; %s" % (BOUND["nh"], bf["tail"][0], bf["tail"][1],
            ("the worst: no coincidence of order p <= %d" % BOUND["p0"]) if bf["where"] is None else
            ("the worst at fch / fsw = %s, VIN %g V, fsw %.1f kHz, fch %.1f kHz" % (bf["where"][0], bf["where"][1], bf["where"][2] / 1e3, bf["where"][3] / 1e3))))
        P("     the FE's worst interval at VIN %g V, fsw from %.1f kHz; the charger's at fch %.0f to %.0f kHz" % (
            bf["fe_at"][0], bf["fe_at"][1] / 1e3, bf["ch_at"][0] / 1e3, bf["ch_at"][1] / 1e3))
    br_ = R["brute"]
    P("   CONSERVATIVE, CHECKED: %d seeded random fully independent configurations per bin at %d bins read at most %.4f of the bin's bound;" % (
        br_["n_bin"], len(BRUTE["bins"]), br_["bin"]))
    P("     %d end-to-end configurations and operating points (half with the L16 and C190 resonance on a charger harmonic, half at an" % br_["n_e2e"])
    P("     exact coincidence) read at most %.4f of the figure" % br_["e2e"])
    P("   WHERE THE BOUND IS LOOSE: from the first round's %.0f mOhm up to the chosen value the feasible worst is under the limit and the" % (RB_START * 1e3))
    P("     bound over it. The gap is each harmonic taking its own worst passive set (the can's own parameters, its siblings', the")
    P("     ceramics') and each source harmonic the larger end of its frequency interval; the bound is not claimed tight")
    P("")
    P("6b. THE CHOSEN BANK: THE RATING AT FREQUENCY AND TEMPERATURE, THE BALLAST, THE ENERGY TERM")
    fq = R["freq"]
    P("   FREQUENCY (MAKER p.2): every harmonic at or above %.1f kHz; the correction for 100 uF and more is %.2f from %.0f kHz up, so" % (
        fq["fmin"] / 1e3, fq["corr_min"], fq["corr_at"] / 1e3))
    P("     the current referred to the rating's 100 kHz is the rms itself: no derating applies")
    lf = R["life"]
    P("   TEMPERATURE AND LIFE: CONDITIONAL (B4). The rating is the sheet's at %.0f C with no uplift taken. The sheet's 20 mOhm is a maximum" % mk["t_cat"])
    P("     at +20 C, not the can's ESR in service, and its rated rise is not printed, so the can's own rise is not established here.")
    P("     p.6: L2 = L1 x 2^((T1 - (T2 + dT)) / 10), T1 the category temperature plus the rated rise; taking the rated rise as zero")
    P("     bounds L2 from below for the can's MEASURED rise dT (capped at the sheet's %.0f years):" % mk["life_cap_y"])
    P("   | dT | at %.1f C inside air | at %.0f C (L1's temperature at the fault, a can beside it) |" % (lf["t_air"], lf["t_local"]))
    for dt, a, c in lf["table"]:
        P("   | %.0f K | %.0f h | %.0f h |" % (dt, a, c))
    P("     the obligation: the can's top temperature at the worst ripple (bench 7b.8), which gives dT")
    bl_ = R["ballast"]
    P("   THE BALLAST (MAKER, the HoJLR2512 sheet p.2): 3 W, derated from %.0f C to zero at %.0f C, operating range -%.0f to +%.0f C. At the" % (
        bl_["knee"], bl_["t_op"][1], bl_["t_op"][0], bl_["t_op"][1]))
    P("     bound's worst can each resistor dissipates at most %.3f W, against %s." % (
        bl_["p"], ", ".join("%.2f W at %.1f C" % (r_, t) for t, r_ in bl_["rating"])))
    P("     Its temperature envelope: %.0f C in use up to its own surface temperature, which the sheet does not give (a bench reading," % bl_["t_lo"])
    P("     7b.8); its tolerance carries 50 ppm/K over %.0f K from 25 C (ASSUMPTION: to 100 C)" % bl_["dt"])
    tp = R["typical"]
    P("   THE ENERGY MODEL'S TERM (REQ-072's owner): the six ballasts dissipate sum I_k^2 R_k, which depends on the operating point. Upper")
    P("     sum at the bound's worst corner %.2f W (six resistors at the worst can's bound); an illustration at nominal parts (cans 330 uF," % bl_["sum_upper"])
    P("     20 mOhm, %.1f nH; ceramics %.1f uF; L11 %.0f nH, L16 %.1f nH) at VIN %.1f V, %.1f A, VBAT %.1f V, fsw %.2f kHz, fch %.0f kHz: %.4f W" % (
        tp["can_l"] * 1e9, tp["cer"][0] * 1e6, tp["l11"] * 1e9, tp["l16"] * 1e9, tp["vin"], tp["iout"], tp["vbat"], tp["fsw"] / 1e3, tp["fch"] / 1e3, tp["p"]))
    P("     (not a measurement). Not to be counted twice once a measured converter efficiency includes it")
    P("")
    P("7. THE LOOP WITH THE BALLAST OVER THE COLD ENVELOPE (the recheck's R4), B3's envelope, R12 %.0f mOhm (L4-E6), loads %s A" % (
        R["r12_e6"] * 1e3, " / ".join("%.3f" % x for x in R["loads"])))
    P("   (Middlebrook's bound at %.0f W); the bank's corners C %.2f / %.2f x 330 uF, each branch the ballast at either end of its" % (
        R["vout"] * R["loads"][0], R["box_sheet"]["c_k"][0], R["box_sheet"]["c_k"][1]))
    P("   tolerance plus the can's intrinsic ESR e, e from 0 to size %s's %.0f mOhm (the -40 C endurance limit taken down to -20 C, INFERRED)" % (
        mk["size"], mk["esr_cold"] * 1e3))
    cd = R["comp_drawn"]
    P("   the drawn compensation (Rc1 %.0f k, Cc1 %.0f nF, Cc2 %.0f pF) with the ballast:" % (cd[0] / 1e3, cd[1] * 1e9, cd[2] * 1e12))
    P("   | e | PM | GM | abs(1+T) min | crossover | widened PM | widened GM | widened abs(1+T) | every margin |")
    rowf = lambda e, d_, w_: "   | %.0f mOhm | %.1f deg | %.1f dB | %.2f | %.2f to %.2f kHz | %.1f deg | %.1f dB | %.2f | %s |" % (
        e * 1e3, d_["pm_i"], d_["gm_i"], d_["mm"], d_["fc_lo_i"], d_["fc_hi_i"], w_["pm_i"], w_["gm_i"], w_["mm"],
        "yes" if all(x["pm"] >= 50 and x["gm"] >= 10 and x["mm"] >= 0.5 and x["ceil_ok"] and x["all_cross"] and x["z_ratio"] <= 1.0 for x in (d_, w_)) else "NO")
    for e, (d_, w_) in sorted(R["LD"].items()):
        P(rowf(e, d_, w_))
    cp = R["cpick"]
    P("   the compensation (SESSION): Cc2 ascending through lcsc_fill.py's 0603 capacitors, Rc1 and Cc1 kept (the smallest change: one")
    P("   part); the ends of the envelope first: %s" % "; ".join(
        "%s %s" % (k, "meets" if all(all(x["pm"] >= 50 and x["gm"] >= 10 and x["mm"] >= 0.5 and x["ceil_ok"] and x["all_cross"] and x["z_ratio"] <= 1.0
                                         for x in pr) for pr in v.values()) else "fails") for k, v in R["LCMP"].items()))
    P("   CHOSEN: Cc2 %s (%s, lcsc_fill.py), over the whole envelope in %.0f mOhm steps:" % (cp[1], cp[2], LOOP_STEP * 1e3))
    P("   | e | PM | GM | abs(1+T) min | crossover | widened PM | widened GM | widened abs(1+T) | every margin |")
    for e, (d_, w_) in sorted(R["LENV"].items()):
        P(rowf(e, d_, w_))
    for (k, e), (d_, w_) in sorted(R["LTOL"].items()):
        P("   Cc2 x%.2f (its tolerance and temperature), e %.0f mOhm: PM %.1f / %.1f deg, GM %.1f / %.1f dB, abs(1+T) %.2f / %.2f (default / widened)" % (
            k, e * 1e3, d_["pm_i"], w_["pm_i"], d_["gm_i"], w_["gm_i"], d_["mm"], w_["mm"]))
    d_, w_ = R["LMIX"]
    P("   %d mixed banks (1 to 5 cans at the ballast's low end and no ESR, the rest at its high end and %.0f mOhm, C at either extreme):" % (
        R["nmix"], mk["esr_cold"] * 1e3))
    P("     PM %.1f / %.1f deg, GM %.1f / %.1f dB, abs(1+T) %.2f / %.2f" % (d_["pm_i"], w_["pm_i"], d_["gm_i"], w_["gm_i"], d_["mm"], w_["mm"]))
    P("   with the drawn R12 (%.0f mOhm) and the record's loads: %s" % (R["rcs_drawn"] * 1e3, "; ".join(
        "e %.0f mOhm GM %.1f / %.1f dB, PM %.1f / %.1f deg" % (e * 1e3, d_["gm_i"], w_["gm_i"], d_["pm_i"], w_["pm_i"]) for e, (d_, w_) in sorted(R["LORD"].items()))))
    P("   ORDER: on the drawn R12 the ballast and Cc2 miss a margin (above), so they go in with L4-E6's R12, where the loop is verified;")
    P("   the draft refuses the tree without it. MODELED;")
    P("   the bench loop row owed. The cold-ESR reading then confirms the envelope: the bank's ESR envelope at -20 C over service life at")
    P("   or below the modelled envelope (every can at most %.0f mOhm at 100 kHz)" % (mk["esr_cold"] * 1e3))
    P("")
    P("8. WHAT THE BANK'S CAPACITANCE MOVES: THE SIX CANS KEPT (INFERRED, first order: lossless, constant inductance, not saturation aware)")
    cs = R["cons"]
    P("   INITIAL CAPACITANCE ONLY (the cans at their +-20 %%, as the generator's record took them): largest %.2f mF, smallest %.2f mF; the" % (
        cs["cmax"] * 1e3, cs["cmin"] * 1e3))
    P("   soft start's own draw %.1f / %.1f / %.1f %% of %.2f A at 9 / 12 / 13.8 V; the bleed's tau %.2f to %.2f s, %.2f to %.2f s to release; the" % (
        cs["ramp"][0], cs["ramp"][1], cs["ramp"][2], rec["entry"], cs["tau"][0], cs["tau"][1], cs["bleed"][0], cs["bleed"][1]))
    P("   restart ring %.1f A (%.0f %% of L1's %.1f A typical Isat at 25 C), %.2f mJ: as recorded" % (
        cs["ring"][0], 100 * cs["ring"][0] / rec["ring"]["isat"], rec["ring"]["isat"], cs["ring"][1]))
    ce = R["cons_e"]
    P("   OVER ENDURANCE (the cans at %.2f to %.2f x 330 uF, the bound's range): %.4f to %.4f mF; the soft start's own draw %.4f %% at 9 V;" % (
        R["box_sheet"]["c_k"][0], R["box_sheet"]["c_k"][1], ce["cmin"] * 1e3, ce["cmax"] * 1e3, ce["ramp9"]))
    P("   the bleed %.3f to %.3f s to release; the restart ring %.4f A (%.0f %% of L1's typical Isat), %.4f mJ. These carry the restart" % (
        ce["bleed"][0], ce["bleed"][1], ce["ring"][0], 100 * ce["ring"][0] / ce["isat"], ce["ring"][1]))
    P("   obligation (L4-E6's C-5 sweep, saturation aware, to %.1f A); the ballasts' damping is not credited" % ce["ring"][0])
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
