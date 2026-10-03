#!/usr/bin/env python3
"""l4e7_stage_settings.py: layer 4 task L4-E7 (MESHSAT-1357, 1 October 2026). Implementable choice 3, REAL COMPONENT
SETTINGS for board E's solar stage, of v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md (finding O-2, "the stage's input power
is not controlled", status "B2: arithmetic corrected under stated assumptions (closed). O-2 physical compliance: OPEN";
the power review's L4-R01): the LT8705A's grade, RSENSE1 and RIMON_IN of its input-current limit, and R8 and R9 of its
input-voltage hold, chosen as catalogue parts with their makers' tolerance and TCR, and section 11's 100 W corner check of
l4e_replay.py re-run on the values those parts achieve, at both temperature ends.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry or rendered page in
the tree is edited (the apply_gen_sch_e_*.py drafts beside this file are for board E's generator owner). Every figure carries
its basis: MAKER (document, revision, page), NETLIST (the committed board E netlist), CATALOGUE (an LCSC or JLCPCB reading
filed under inputs/), MODELED (the energy model, through l4e_replay.py's own functions), INFERRED (method stated),
ASSUMPTION (a figure no document gives) or SESSION (a design rule this record sets, with its reason).

Section 0 proves, before any result (exit 4 otherwise):
  0a l4e_replay.py, re-run in a child process, reproduces l4e_replay.out byte for byte;
  0b l4e5_source_control.py, re-run in a child process, reproduces l4e5_source_control.out byte for byte;
  0c l4e_replay.main(), run here with its locals captured by l4e4_limits.run_main_captured(), prints l4e_replay.out byte
     for byte, so the functions this record uses (i_factor, ec_row, the hold, the candidate panel's trace, meanday and
     least) are the ones that printed the record. Nothing here compares a git hash with a recorded string.

Run from the repository root:  python3 v2/docs/records/l4e7/l4e7_stage_settings.py > v2/docs/records/l4e7/l4e7_stage_settings.out
Needs pdftotext and pdftocairo (poppler), PyYAML and the held documents (fetch_held_back.py beside this file, the Samsung
excerpts by fetch_maker_curves.py beside it, and the ones the imported records name). About nine minutes, most of it
section 0 and the guard's transients (B6, rounds 2 and 3).
Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed; 4: a reproduction or a predicate failed."""
import hashlib
import importlib.util
import itertools
import json
import math
import os
import re
import subprocess
import sys
import textwrap

sys.dont_write_bytecode = True
try:
    os.nice(10)                 # a shared host: stay behind interactive work
except OSError:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REPLAY_PY = "v2/docs/records/l4e/l4e_replay.py"
REPLAY_OUT = "v2/docs/records/l4e/l4e_replay.out"
L4E5_PY = "v2/docs/records/l4e5/l4e5_source_control.py"
L4E5_OUT = "v2/docs/records/l4e5/l4e5_source_control.out"
L4E4_PY = "v2/docs/records/l4e4/l4e4_limits.py"
GEN_E = "v2/ecad/tools/gen_sch_e.py"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
ENV = "v2/ecad/tools/pcb_envelope.yaml"
REQS = "v2/ecad/tools/pcb_requirements.yaml"
LT = "v2/vendor/power/lt8705a.pdf"
HOJ = "v2/vendor/passives/milliohm-hojlr2512-series.pdf"
RT = "v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf"
BSC039 = "v2/vendor/infineon/infineon-bsc039n06ns-rev2.4-c534330.pdf"
BSC028 = "v2/vendor/power/held/infineon-bsc028n06ns-rev2.1-c148250.pdf"
TPS48 = "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf"      # the solar-fault remedy's controller (held back; fetch_held_back.py)
LM747 = "v2/vendor/ti/ti-lm74700-q1.pdf"
CSD32 = "v2/vendor/power/ti-csd19532q5b-n-fet.pdf"
BZT = "v2/vendor/diodes/diodes-bzt52c-ds18004.pdf"
INP = "v2/docs/records/l4e7/inputs"
CLAR = "v2/docs/records/l4e7/clarification"
INP_L4E4 = "v2/docs/records/l4e4/inputs/jlc-search-hojlr2512-3w-2026-10-01.json"
PINS = {
    REPLAY_PY: "3de985e2e3e06453d2c9d576311c1f39935149ac1e9b7cff0431a40933bb8734",
    REPLAY_OUT: "59c6eeab16da98f8ddf16880ddcdc1d2a2c910f4256be9b69aade49dd4d2726d",
    L4E5_PY: "4315c900db1426f78b544baf7c40597e2ac06479258794bf554281a26e391fd1",
    L4E5_OUT: "f9c98ec5c43ada0e1a5a033a794c98b45f110ffcb0a67ff8c81a31fede134e71",
    L4E4_PY: "d4a484439a7b53030423b596769bf748469134a45a46b3c91724e2b80d9e2a42",
    GEN_E: "f846e138cb53a8c63247efb3ad7b5cc44a68cb73e71699c65fd53b63c01af186",
    NET_E: "2ed95a0e8069ebf8ad31f4567a14015e863182a83b6de7b3b13218488d8316d4",
    LT: "8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3",
    HOJ: "3224518dbc8bdc858a96cfde88de2611494550f95406f6b65130c232cdfc93fb",
    RT: "0a729d144519a7021c82a0ef242b064e467c70d44afcf9eabd6c7ffdc4b673a3",
    BSC039: "8d95c1da9c78b3afb037e1f80c3bea1ed0f874f689e3a0c96d926dafe6a437b9",
    BSC028: "2959653166e981f9de24cd9c141c44490ecc62acba5971ec8c0b263eca9708e0",
    TPS48: "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f",
    LM747: "e16b3a8c0023201fafa5825436f5f2dd6f885b92b84e65602b3f50d741c58b6f",
    CSD32: "353ce937cff0b719e730010829720d25c2ece3637ed92fb7ad8cc370438559d1",
    BZT: "0fbd7d137524820f0160594065cbceb8c6b3188757c328416d08fceb7418202f",
    INP_L4E4: None,             # read only; its codes are checked against the filed LCSC answer below
}
# The figures this record sets itself (each SESSION or ASSUMPTION, named where it is used):
EA2_FLOOR_DIV = 2.0      # SESSION: the setting's design floor takes EA2's and EA3's unprinted gains at half their typical
LINE_FLOOR_MUL = 2.0     # SESSION: and the references' line regulation (printed at 25 C, not switching) at twice its maximum
STOCK_MIN = 1000         # SESSION: a catalogue value is a candidate only with at least this many in stock at the reading
V_STEP = 0.01            # the corner check's voltage grid, V (the replay's own step)
I_RES = 0.001            # the old setting's grid, A (the replay's I_RES), for its row only
HOLD_RANGE = (15.5, 17.5)  # the NOT ADOPTED proposal's scan only: nominals inside the candidate's hourly MPP span +- about 1 V
OFFICIAL_URL = "https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf"   # the owner's named sheet
IA_SNAPSHOT = "20250322064938"   # the Internet Archive's copy of that URL (the live site resets this runner's connection)
CIMON = ("C65", "100n", "C14663")   # SESSION: CIMON_IN at the maker's 0.1 uF lower end (8705af p.31), the 0603 X7R board E uses
CER_PARTS = ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN")   # Samsung, the ceramics B6 round 2 bounds by their curves
SAMH = "v2/vendor/passives/held/samsung-%s-2026-10-02.json"           # their excerpts, held back (fetch_maker_curves.py)
PINS.update({SAMH % pn_: sha_ for pn_, sha_ in (
    ("CL31B106KBHNNN", "adccf37d9343f7e285c5ce0d6fa075fcf6a7799faf8e667838c1fbb7a06cbfaa"),
    ("CL32B106KBJNNN", "074ea4b6607c221b64f416f54f9eeaae70e154364b1b85e4cf0338aa4333fafd"),
    ("CL32B225KCJSNN", "f483cb318d868fc58e047a10e24a0d54959da353f102fb164c30395388fda0aa"))})
XAL = "v2/vendor/power/coilcraft-xal1510.pdf"                           # L1's sheet (B6 round 3: the inductor ripple the sense sees)
PINS[XAL] = "ccbf7fa97649e098de283ce9c9505201b149443fa34ed771b1e71aa6a8987892"


def refuse(code, msg):
    sys.stderr.write("l4e7_stage_settings: %s; refusing\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def pg(rel, n, layout=True):
    a = ["pdftotext"] + (["-layout"] if layout else []) + ["-f", str(n), "-l", str(n), os.path.join(TOP, rel), "-"]
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode != 0:
        refuse(3, "pdftotext could not read %s p.%d" % (rel, n))
    return r.stdout


def flat(t):
    return " ".join(t.split())


def need(text, pat, what):
    m = re.search(pat, text, re.M)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def catalogue(code):
    """A filed LCSC answer (inputs/lcsc-<code>-2026-10-01.json, or -10-02 for the third round's): model, stock, tolerance and TCR as the catalogue prints them."""
    p = os.path.join(TOP, INP, "lcsc-%s-2026-10-01.json" % code)
    if not os.path.isfile(p):
        p = os.path.join(TOP, INP, "lcsc-%s-2026-10-02.json" % code)
    if not os.path.isfile(p):
        refuse(3, "no filed catalogue reading for %s" % code)
    return json.load(open(p, encoding="utf-8"))


def rvalue(model):
    """The resistance of a YAGEO RT0603BRD07 model in ohms ('RT0603BRD0723K2L' is 23.2k)."""
    m = re.match(r"RT0603BRD07(\d+)K(\d*)L$", model)
    return float(m.group(1) + ("." + m.group(2) if m.group(2) else "")) * 1e3 if m else None


def bound_status(rows):
    """CONDITIONAL exactly when a row that affects the 100 W bound is not resolved by a guaranteed limit or a maker's statement."""
    return "CONDITIONAL" if any(r_["bound"] and not r_["resolved"] for r_ in rows) else "UNCONDITIONAL"


def soa_lines_csd32():
    """CSD19532Q5B Figure 10 (SLPS414B p.6), the SOA lines read from the sheet's vector drawing by L4-E9's method, as L4-E11's
    soa_lines() reads them (the same frame, legend and consistency checks), so every line is TI's own coordinates."""
    svg = subprocess.run(["pdftocairo", "-svg", "-f", "6", "-l", "6", os.path.join(TOP, CSD32), "-"], capture_output=True).stdout.decode("utf-8", "replace")
    tr = "matrix(0.097966,0,0,-0.097966,64.4,445.1)"
    paths = []
    for m in re.finditer(r"<path[^>]*>", svg):
        t = re.sub(r",\s+", ",", m.group(0))
        st = re.search(r'stroke(?::|=")(rgb\([^)]*\))', t)
        if tr not in t or not st:
            continue
        pts = [(float(a), float(b)) for a, b in re.findall(r"[ML] ([-\d.]+) ([-\d.]+)", re.search(r' d="([^"]*)"', t).group(1))]
        paths.append((st.group(1), pts))
    frames = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 5 and p[0] == p[-1]]
    if not frames:
        refuse(3, "CSD19532Q5B Figure 10's frame")
    fr = max(frames, key=lambda q: (max(a for a, _ in q) - min(a for a, _ in q)) * (max(b for _, b in q) - min(b for _, b in q)))
    x0, x1 = min(q[0] for q in fr), max(q[0] for q in fr)
    y0, y1 = min(q[1] for q in fr), max(q[1] for q in fr)
    lv = lambda x: -1.0 + 4.0 * (x - x0) / (x1 - x0)
    li = lambda y: -1.0 + 5.0 * (y - y0) / (y1 - y0)
    idm = [p for c, p in paths if c == "rgb(0%,0%,0%)" and len(p) == 3]
    if not idm or abs(10 ** li(idm[0][0][1]) - 400.0) > 4.0 or abs(10 ** lv(idm[0][1][0]) - 100.0) > 1.0:
        refuse(3, "CSD19532Q5B Figure 10's IDM and 100 V boundary")
    rows = [re.findall(r"(10us|100us|1ms|10ms|DC)\b", ln) for ln in pg(CSD32, 6).splitlines() if re.search(r"\b(10us|100us)\b", ln)]
    if len(rows) != 2:
        refuse(3, "CSD19532Q5B Figure 10's legend")
    legend = sorted(((p[0][1], p[0][0], c) for c, p in paths if len(p) == 2 and p[0][1] == p[1][1] and c != "rgb(0%,0%,0%)"
                     and 100 < p[1][0] - p[0][0] < 150 and p[0][1] > 1200), key=lambda q: (-q[0], q[1]))
    labels = rows[0] + rows[1]
    if len(legend) < len(labels):
        refuse(3, "CSD19532Q5B Figure 10's legend segments")
    out = {}
    for lab, (_y, _x, col) in zip(labels, legend):
        cands = [p for c, p in paths if c == col and len(p) >= 3 and abs(10 ** lv(p[-1][0]) - 100.0) < 1.0]
        if len(cands) != 1:
            refuse(3, "CSD19532Q5B Figure 10's %s line" % lab)
        out[lab] = [(lv(x), li(y)) for x, y in cands[0]]
    return {1e-5: out["10us"], 1e-4: out["100us"], 1e-3: out["1ms"], 1e-2: out["10ms"]}


def soa_t(lines, vds, t):
    """A line's current at vds for a pulse of t s (L4-E9's and L4-E11's method): log-log on the line, log-log between the
    printed lines in time; under the shortest line its value; below a line's first voltage its first current."""
    def at(line):
        lx = math.log10(vds)
        if lx < line[0][0]:
            return 10 ** line[0][1]
        for (xa, ya), (xb, yb) in zip(line, line[1:]):
            if xa <= lx <= xb:
                return 10 ** (ya + (yb - ya) * (lx - xa) / (xb - xa))
        refuse(3, "Figure 10 has no segment at %s V" % vds)
    ts = sorted(lines)
    if t <= ts[0]:
        return at(lines[ts[0]])
    for a, b in zip(ts, ts[1:]):
        if a <= t <= b:
            ia, ib = at(lines[a]), at(lines[b])
            return 10 ** (math.log10(ia) + (math.log10(ib) - math.log10(ia)) * (math.log10(t) - math.log10(a)) / (math.log10(b) - math.log10(a)))
    ia, ib = at(lines[ts[-2]]), at(lines[ts[-1]])
    return ib * (ts[-1] / t) ** (math.log10(ia / ib) / math.log10(ts[-1] / ts[-2]))


def guard_event(g, v0, i0, L, bulk, k, cold=False, ramp=None, dt=20e-9, t_end=60e-6):
    """MODELED (B6 of the consolidation review): a stiff source g["E"] arriving at J_SOLAR through the panel lead (g["r_lead"], L)
    with the solar guard already on (cold=False) or off (cold=True: Q12 never conducts, the port's capacitance alone), as a step
    at t = 0 or, with ramp (V/s), rising from v0 at that rate. Lumped parts, backward Euler on four nodes in a chain (PV_F,
    PV_P, TRK_VS, TRK_VIN, a tridiagonal system solved exactly each step), the clamps as straight lines (off below their
    breakdown) with their on/off state iterated to consistency inside the step:
      PV_F    C131 and C132 (g["c131"], no ESR) to GND, D11 (g["d11"]: breakdown, slope; both polarities), Q12 with R87 to PV_P
              (g["r_on"], R87 at its least, the FET's resistance not credited);
      PV_P    the bulk (bulk = (ESR, C)), g["n_pc"] 10 uF ceramics (each -10 % times the bias factor k, ESR g["esr_cer"]),
              the sense bank g["rb"] to TRK_VS;
      TRK_VS  C71 to C74 (g["n_ca"] ceramics, as above), D4 (g["d4"]: breakdown, slope), RSENSE1 g["r59"] to TRK_VIN;
      TRK_VIN C13 to C15 and C64 (C13 and C14 at the bias factor k, all at +10 %, no ESR), the stage drawing i0 throughout.
    The source's return is not credited (Q13, F2 and the body diode's drop left out: each would lower the drive). Q12 conducts
    fully until the earlier of the two comparators' commands, each at its latest: the OV comparator's first crossing of g["ov"] on
    PV_F plus g["t_ov"] (OV to PD), the short-circuit comparator's first crossing of g["isc"] by R87's current through the RISCP
    x CSCP filter (first order, g["tau"]) plus g["t_sc"] (to PD); then its conductance falls linearly to zero over g["t_f"]. Returns the peaks,
    the samples of Q12's (VDS, ID) while it conducts and the lead current's slope at the turn-off command."""
    E, rl = g["E"], g["r_lead"]
    esr_b, cb = bulk
    kp_, ka_, kc_ = k if isinstance(k, tuple) else (k, k, k)     # PV_P, TRK_VS and TRK_VIN bias factors (one, or one per bank)
    ca, ra = g["n_ca"] * 10e-6 * 0.9 * ka_, g["esr_cer"] / g["n_ca"]
    cc = (20e-6 * kc_ + 4.8e-6) * 1.10
    npc = g["n_pc"]
    cpc, rpc = npc * 10e-6 * 0.9 * kp_, (g["esr_cer"] / npc if npc else 0.0)
    rb, r59, ron = g["rb"], g["r59"], g["r_on"]
    vb4, rd4 = g["d4"]
    vb11, rd11 = g["d11"]
    io = 0.0 if cold else i0
    if cold:
        vF, vP, vS, vC, iL = v0, g["v_behind"], g["v_behind"], g["v_behind"], 0.0
    else:
        vP, vS = v0, v0 - io * rb
        vC, vF, iL = vS - io * r59, v0 + io * ron, io
    vB, vA, vPc = vP, vS, vP
    y, t_go, why, s11, s4, t_ovc, t_scc = io, None, None, 0, 0, None, None
    pk = dict(vF=vF, vFmin=vF, vP=vP, vS=vS, vC=vC, i4=0.0, e4=0.0, i11=0.0, e11=0.0, iQ=0.0, iL=abs(iL), vds=vF - vP, vdsmin=vF - vP,
              slew=0.0, u5=vS - vC, u5n=vS - vC, u18=vP - vS, u18n=vP - vS, di_go=None, i_go=None, t11=None)
    samp = []
    gl_ = (dt / L) / (1.0 + rl * dt / L)
    gC, gc = g["c131"] / dt, cc / dt
    gB, gA = 1.0 / (esr_b + dt / cb), 1.0 / (ra + dt / ca)
    gPc = 1.0 / (rpc + dt / cpc) if npc else 0.0
    g59, gbk = 1.0 / r59, 1.0 / rb
    il_prev = iL
    for kk in range(int(round(t_end / dt))):
        t = (kk + 1) * dt
        e_t = E if ramp is None else min(E, v0 + ramp * t)
        if cold:
            gq = 0.0
        elif t_go is None or t <= t_go:
            gq = 1.0 / ron
        else:
            gq = max(0.0, 1.0 - (t - t_go) / g["t_f"]) / ron
        jl = iL / (1.0 + rl * dt / L) + gl_ * e_t
        for _it in range(8):
            g11, j11 = (1.0 / rd11, s11 * vb11 / rd11) if s11 else (0.0, 0.0)
            g4, j4 = (1.0 / rd4, vb4 / rd4) if s4 else (0.0, 0.0)
            b0, c0, d0 = gl_ + gC + gq + g11, -gq, jl + gC * vF + j11
            a1, b1, c1, d1 = -gq, gq + gB + gPc + gbk, -gbk, gB * vB + gPc * vPc
            a2, b2, c2, d2 = -gbk, gbk + gA + g59 + g4, -g59, gA * vA + j4
            a3, b3, d3 = -g59, g59 + gc, gc * vC - io
            cp0, dp0 = c0 / b0, d0 / b0
            m1 = b1 - a1 * cp0
            cp1, dp1 = c1 / m1, (d1 - a1 * dp0) / m1
            m2 = b2 - a2 * cp1
            cp2, dp2 = c2 / m2, (d2 - a2 * dp1) / m2
            xC = (d3 - a3 * dp2) / (b3 - a3 * cp2)
            xS = dp2 - cp2 * xC
            xP = dp1 - cp1 * xS
            xF = dp0 - cp0 * xP
            n11 = 1 if xF > vb11 else (-1 if xF < -vb11 else 0)
            n4 = 1 if xS > vb4 else 0
            if (n11, n4) == (s11, s4):
                break
            s11, s4 = n11, n4
        iL = jl - gl_ * xF
        iQ = gq * (xF - xP)
        i11 = (xF - s11 * vb11) / rd11 if s11 else 0.0
        i4 = (xS - vb4) / rd4 if s4 else 0.0
        vB += gB * (xP - vB) * dt / cb
        vA += gA * (xS - vA) * dt / ca
        if npc:
            vPc += gPc * (xP - vPc) * dt / cpc
        pk["slew"] = max(pk["slew"], abs(xF - vF) / dt)
        vF, vP, vS, vC = xF, xP, xS, xC
        if i11:
            pk["t11"] = (pk["t11"][0] if pk["t11"] else t, t)
        if not cold:
            y += (iQ - y) * dt / g["tau"]
            if t_ovc is None and vF >= g["ov"]:
                t_ovc = t + g["t_ov"]
            if t_scc is None and y >= g["isc"]:
                t_scc = t + g["t_sc"]
            cmd_ = [(x_, w_) for x_, w_ in ((t_ovc, "OV"), (t_scc, "SCP")) if x_ is not None]
            if cmd_:
                t_go, why = min(cmd_)
            if t_go is not None and pk["di_go"] is None and t >= t_go:
                pk["di_go"], pk["i_go"] = (iL - il_prev) / dt, iL
        il_prev = iL
        if gq > 0.0:
            samp.append((vF - vP, iQ))
        pk["vF"], pk["vFmin"] = max(pk["vF"], vF), min(pk["vFmin"], vF)
        pk["vP"], pk["vS"], pk["vC"] = max(pk["vP"], vP), max(pk["vS"], vS), max(pk["vC"], vC)
        pk["i4"], pk["e4"] = max(pk["i4"], i4), pk["e4"] + vS * i4 * dt
        pk["i11"], pk["e11"] = max(pk["i11"], abs(i11)), pk["e11"] + abs(vF * i11) * dt
        pk["iQ"], pk["iL"] = max(pk["iQ"], abs(iQ)), max(pk["iL"], abs(iL))
        pk["vds"], pk["vdsmin"] = max(pk["vds"], vF - vP), min(pk["vdsmin"], vF - vP)
        pk["u5"], pk["u5n"] = max(pk["u5"], vS - vC), min(pk["u5n"], vS - vC)
        pk["u18"], pk["u18n"] = max(pk["u18"], vP - vS), min(pk["u18n"], vP - vS)
    pk.update(why=why, t_go=t_go, t_on=len(samp) * dt, samp=samp)
    return pk


class CerBank:
    """A ceramic bank as charge against voltage (round 2 of B6, the external review's L4-F01). parts: [(count, C_nom, curve or
    None, factor, cap)]: each part's capacitance at v is C_nom x min(cap, factor x (1 + curve(v) / 100)), curve the maker's
    typical DC-bias change in percent (None: no derating). Tabulated every 0.1 V to 120 V; Q(v) is the integral, so a step
    from v_old to v_new moves the charge Q(v_new) - Q(v_old) (the chord capacitance), not C(v_old) x dv."""
    def __init__(self, parts, vmax=120.0, n=1200):
        self.dv, self.n = vmax / n, n

        def pc(curve, v):
            if curve is None:
                return 0.0
            if v >= curve[-1][0]:
                return curve[-1][1]
            for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
                if x0 <= v <= x1:
                    return y0 + (y1 - y0) * (v - x0) / (x1 - x0) if x1 > x0 else y0
            return curve[0][1]
        self.cs = [sum(cnt * cn * min(cap, fac * (1 + pc(cv, i * self.dv) / 100.0)) for cnt, cn, cv, fac, cap in parts) for i in range(n + 1)]
        self.q = [0.0]
        for i in range(n):
            self.q.append(self.q[-1] + 0.5 * (self.cs[i] + self.cs[i + 1]) * self.dv)

    def C(self, v):
        x = min(max(v, 0.0) / self.dv, self.n - 1e-9)
        i = int(x)
        return self.cs[i] + (self.cs[i + 1] - self.cs[i]) * (x - i)

    def Q(self, v):
        if v <= 0.0:
            return self.cs[0] * v
        x = min(v / self.dv, self.n - 1e-9)
        i = int(x)
        f = x - i
        return self.q[i] + (self.cs[i] + 0.5 * (self.cs[i + 1] - self.cs[i]) * f) * f * self.dv

    def chord(self, v_new, v_old):
        return self.C(v_old) if abs(v_new - v_old) < 1e-6 else (self.Q(v_new) - self.Q(v_old)) / (v_new - v_old)


def guard_event_b(g, v0, i0, L, bulk, cold=False, ramp=None, dt=20e-9, t_end=60e-6):
    """MODELED, round 2 of B6: guard_event's network and commands, with every ceramic bank a CerBank of its maker's curves at
    its own voltage (g["bF"] PV_F, g["bP"] PV_P, g["bS"] TRK_VS behind g["esrS"], g["bC"] TRK_VIN), PV_P's ceramics behind
    g["esrP"]. Backward Euler on the same chain of four nodes; inside each step the chord capacitances and the clamps' states
    are iterated to consistency (at most 12 passes, to 1 nV)."""
    E, rl = g["E"], g["r_lead"]
    esr_b, cb = bulk
    bF, bP, bS, bC = g["bF"], g["bP"], g["bS"], g["bC"]
    rP, rS, rb, r59, ron = g["esrP"], g["esrS"], g["rb"], g["r59"], g["r_on"]
    vb4, rd4 = g["d4"]
    vb11, rd11 = g["d11"]
    io = 0.0 if cold else i0
    if cold:
        vF, vP, vS, vC, iL = v0, g["v_behind"], g["v_behind"], g["v_behind"], 0.0
    else:
        vP, vS = v0, v0 - io * rb
        vC, vF, iL = vS - io * r59, v0 + io * ron, io
    vB, vA, vPc = vP, vS, vP
    y, t_go, why, s11, s4, t_ovc, t_scc = io, None, None, 0, 0, None, None
    pk = dict(vF=vF, vFmin=vF, vP=vP, vS=vS, vC=vC, i4=0.0, e4=0.0, i11=0.0, e11=0.0, iQ=0.0, iL=abs(iL), vds=vF - vP, vdsmin=vF - vP,
              slew=0.0, u5=vS - vC, u5n=vS - vC, u18=vP - vS, u18n=vP - vS, di_go=None, i_go=None, t11=None, di59=0.0,
              di59_up=0.0, di59_dn=0.0, u5L=vS - vC, u5Ln=vS - vC)
    samp = []
    gl_ = (dt / L) / (1.0 + rl * dt / L)
    gB, g59, gbk = 1.0 / (esr_b + dt / cb), 1.0 / r59, 1.0 / rb
    il_prev = iL
    i59_prev = (vS - vC) / r59
    l59 = g.get("l59", 0.0)                            # RSENSE1's own inductance (round 3): the pins read R i + L di/dt
    for kk in range(int(round(t_end / dt))):
        t = (kk + 1) * dt
        e_t = E if ramp is None else min(E, v0 + ramp * t)
        if cold:
            gq = 0.0
        elif t_go is None or t <= t_go:
            gq = 1.0 / ron
        else:
            gq = max(0.0, 1.0 - (t - t_go) / g["t_f"]) / ron
        jl = iL / (1.0 + rl * dt / L) + gl_ * e_t
        xF, xP, xS, xC, xA, xPc = vF, vP, vS, vC, vA, vPc
        for _it in range(12):
            cF, cA, cPc, cc = bF.chord(xF, vF), bS.chord(xA, vA), bP.chord(xPc, vPc), bC.chord(xC, vC)
            gC, gA, gPc, gc = cF / dt, 1.0 / (rS + dt / cA), 1.0 / (rP + dt / cPc), cc / dt
            g11, j11 = (1.0 / rd11, s11 * vb11 / rd11) if s11 else (0.0, 0.0)
            g4, j4 = (1.0 / rd4, vb4 / rd4) if s4 else (0.0, 0.0)
            b0, c0, d0 = gl_ + gC + gq + g11, -gq, jl + gC * vF + j11
            a1, b1, c1, d1 = -gq, gq + gB + gPc + gbk, -gbk, gB * vB + gPc * vPc
            a2, b2, c2, d2 = -gbk, gbk + gA + g59 + g4, -g59, gA * vA + j4
            a3, b3, d3 = -g59, g59 + gc, gc * vC - io
            cp0, dp0 = c0 / b0, d0 / b0
            m1 = b1 - a1 * cp0
            cp1, dp1 = c1 / m1, (d1 - a1 * dp0) / m1
            m2 = b2 - a2 * cp1
            cp2, dp2 = c2 / m2, (d2 - a2 * dp1) / m2
            nC = (d3 - a3 * dp2) / (b3 - a3 * cp2)
            nS = dp2 - cp2 * nC
            nP = dp1 - cp1 * nS
            nF = dp0 - cp0 * nP
            nA = vA + gA * (nS - vA) * dt / cA
            nPc = vPc + gPc * (nP - vPc) * dt / cPc
            n11 = 1 if nF > vb11 else (-1 if nF < -vb11 else 0)
            n4 = 1 if nS > vb4 else 0
            done = abs(nF - xF) + abs(nC - xC) + abs(nA - xA) + abs(nPc - xPc) < 1e-9 and (n11, n4) == (s11, s4)
            xF, xP, xS, xC, xA, xPc, s11, s4 = nF, nP, nS, nC, nA, nPc, n11, n4
            if done:
                break
        iL = jl - gl_ * xF
        iQ = gq * (xF - xP)
        i11 = (xF - s11 * vb11) / rd11 if s11 else 0.0
        i4 = (xS - vb4) / rd4 if s4 else 0.0
        vB += gB * (xP - vB) * dt / cb
        pk["slew"] = max(pk["slew"], abs(xF - vF) / dt)
        vF, vP, vS, vC, vA, vPc = xF, xP, xS, xC, xA, xPc
        if i11:
            pk["t11"] = (pk["t11"][0] if pk["t11"] else t, t)
        if not cold:
            y += (iQ - y) * dt / g["tau"]
            if t_ovc is None and vF >= g["ov"]:
                t_ovc = t + g["t_ov"]
            if t_scc is None and y >= g["isc"]:
                t_scc = t + g["t_sc"]
            cmd_ = [(x_, w_) for x_, w_ in ((t_ovc, "OV"), (t_scc, "SCP")) if x_ is not None]
            if cmd_:
                t_go, why = min(cmd_)
            if t_go is not None and pk["di_go"] is None and t >= t_go:
                pk["di_go"], pk["i_go"] = (iL - il_prev) / dt, iL
        il_prev = iL
        if gq > 0.0:
            samp.append((vF - vP, iQ))
        pk["vF"], pk["vFmin"] = max(pk["vF"], vF), min(pk["vFmin"], vF)
        pk["vP"], pk["vS"], pk["vC"] = max(pk["vP"], vP), max(pk["vS"], vS), max(pk["vC"], vC)
        pk["i4"], pk["e4"] = max(pk["i4"], i4), pk["e4"] + vS * i4 * dt
        pk["i11"], pk["e11"] = max(pk["i11"], abs(i11)), pk["e11"] + abs(vF * i11) * dt
        pk["iQ"], pk["iL"] = max(pk["iQ"], abs(iQ)), max(pk["iL"], abs(iL))
        pk["vds"], pk["vdsmin"] = max(pk["vds"], vF - vP), min(pk["vdsmin"], vF - vP)
        pk["u5"], pk["u5n"] = max(pk["u5"], vS - vC), min(pk["u5n"], vS - vC)
        pk["u18"], pk["u18n"] = max(pk["u18"], vP - vS), min(pk["u18n"], vP - vS)
        di59_ = ((vS - vC) / r59 - i59_prev) / dt
        pk["di59"] = max(pk["di59"], abs(di59_))
        pk["di59_up"], pk["di59_dn"] = max(pk["di59_up"], di59_), min(pk["di59_dn"], di59_)
        pk["u5L"], pk["u5Ln"] = max(pk["u5L"], vS - vC + l59 * di59_), min(pk["u5Ln"], vS - vC + l59 * di59_)
        i59_prev = (vS - vC) / r59
    pk.update(why=why, t_go=t_go, t_on=len(samp) * dt, samp=samp)
    return pk


def sense_ripple(cu, cd, i_in, vin, vout, f, L, t_rf, r59, l59, rb, bulk, dt=1e-9, periods=25, vlim=0.1):
    """MODELED, B6 round 3: what U5's sense pins see in operation at the buck region's corner. M1 draws the inductor current from
    the node behind RSENSE1 while it is on (a trapezoid: the valley to the peak over the on-time, edges of t_rf), nothing while
    it is off; the input current i_in is the period's average. The network at the switching timescale: the bulk (esr, C) and
    the source (a current source: the lead's inductance isolates it at these frequencies) on PV_P, the bank rb to TRK_VS, the
    ceramics ahead of RSENSE1 cu = (C, ESR, ESL) there, RSENSE1 r59 with its inductance l59 to TRK_VIN, the ceramics behind it
    cd = (C, ESR, ESL). cu None: nothing ahead of RSENSE1 but the bank (the sheet's Figure 1). Backward Euler; the last period
    after `periods` is read: the pins' peak and trough (the node difference across RSENSE1 and its inductance), the resistive
    part's peak, the period's average and the average of the waveform clipped at vlim (what an amplifier limited to vlim reads)."""
    T = 1.0 / f
    D = vout / vin
    il_avg = i_in / D
    dI = (vin - vout) * D * T / L
    i_v, i_p = il_avg - dI / 2.0, il_avg + dI / 2.0
    ton = D * T

    def i_m1(t):
        t = t % T
        if t < t_rf:
            return i_v * t / t_rf
        if t < ton:
            return i_v + (i_p - i_v) * (t - t_rf) / (ton - t_rf)
        if t < ton + t_rf:
            return i_p * (1.0 - (t - ton) / t_rf)
        return 0.0
    Cd, rd_, ld = cd
    Cu, ru, lu = (1.0, 1e12, 0.0) if cu is None else cu
    esr_b, cb = bulk
    vb = vu = vd = vin
    iu = idn = i59 = 0.0
    n = int(round(T / dt))
    out = []
    for k in range(n * periods):
        t = (k + 1) * dt
        im = i_m1(t)
        zb, eb = dt / cb + esr_b, vb
        zu, eu = dt / Cu + ru + lu / dt, vu - (lu / dt) * iu
        zd, ed = dt / Cd + rd_ + ld / dt, vd - (ld / dt) * idn
        z59, e59 = r59 + l59 / dt, -(l59 / dt) * i59
        # KCL at PV_P, TRK_VS, TRK_VIN (the unknowns vP, vA, vC), solved by elimination
        a11, a12, b1 = 1.0 / zb + 1.0 / rb, -1.0 / rb, i_in + eb / zb
        a21, a22, a23, b2 = 1.0 / rb, -1.0 / rb - 1.0 / zu - 1.0 / z59, 1.0 / z59, -eu / zu - e59 / z59
        a32, a33, b3 = 1.0 / z59, -1.0 / z59 - 1.0 / zd, im + e59 / z59 - ed / zd
        m_ = a21 / a11
        a22p, b2p = a22 - m_ * a12, b2 - m_ * b1
        m2_ = a32 / a22p
        vC = (b3 - m2_ * b2p) / (a33 - m2_ * a23)
        vA = (b2p - a23 * vC) / a22p
        vP = (b1 - a12 * vA) / a11
        ib, iu, idn, i59 = (vP - eb) / zb, (vA - eu) / zu, (vC - ed) / zd, (vA - vC - e59) / z59
        vb += ib * dt / cb
        vu += iu * dt / Cu
        vd += idn * dt / Cd
        if k >= n * (periods - 1):
            out.append((vA - vC, r59 * i59))
    vp = [o[0] for o in out]
    avg = sum(vp) / len(vp)
    return dict(peak=max(vp), trough=min(vp), avg=avg, avg_clip=sum(min(v_, vlim) for v_ in vp) / len(vp), r_peak=max(o[1] for o in out),
                i_v=i_v, i_p=i_p, il_avg=il_avg, dI=dI, D=D)


def compute():
    for rel, want in PINS.items():
        if want is not None and sha(rel) != want:
            refuse(2, "%s is not the pinned file%s" % (rel, (" (fetch it: v2/docs/records/l4e7/%s)" % (
                "fetch_maker_curves.py" if "/samsung-" in rel else "fetch_held_back.py")) if "/held/" in rel else ""))
    R = {}
    # ================================================================== 0: the reproductions
    outr = open(os.path.join(TOP, REPLAY_OUT), "rb").read()
    out5 = open(os.path.join(TOP, L4E5_OUT), "rb").read()
    cr = subprocess.run([sys.executable, "-B", os.path.join(TOP, REPLAY_PY)], cwd=TOP, capture_output=True)
    R["r0a"] = cr.returncode == 0 and cr.stdout == outr
    c5 = subprocess.run([sys.executable, "-B", os.path.join(TOP, L4E5_PY)], cwd=TOP, capture_output=True)
    R["r0b"] = c5.returncode == 0 and c5.stdout == out5
    if not (R["r0a"] and R["r0b"]):
        refuse(4, "a child re-run does not reproduce its record (replay %s, l4e5 %s)" % (R["r0a"], R["r0b"]))
    L4 = load("l4e4_limits_for_l4e7", L4E4_PY)
    RP = load("l4e_replay_for_l4e7", REPLAY_PY)
    rc, text, LR = L4.run_main_captured(RP)
    R["r0c"] = rc == 0 and text.encode("utf-8") == outr
    if not R["r0c"]:
        refuse(4, "l4e_replay.main() does not print its record in-process")

    # ================================================================== 1: board E as drawn (NETLIST) and the generator
    sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
    import netlist_sexp as N
    e = N.load(os.path.join(TOP, NET_E))

    def nets(ref):
        return {p: v["net"] for p, v in e["pins"][ref].items()}

    def members(net):
        return sorted({r for r, pins in e["pins"].items() for v in pins.values() if v["net"] == net})
    u5 = e["components"]["U5"]
    facts = [
        ("U5 pins 32 (CSNIN), 33 (CSPIN) and 34 (VIN) all on PV_P: the input-current sense is tied off, so as drawn no input "
         "limit acts (8705af p.12, p.31)", [nets("U5")[k] for k in ("32", "33", "34")] == ["PV_P"] * 3),
        ("U5 pin 38 (IMON_IN) on TRK_IMONI with R16 alone, 10k, and no CIMON_IN", members("TRK_IMONI") == ["R16", "U5"]
         and e["components"]["R16"]["value"] == "10k"),
        ("U5 pins 29 to 31 (EXTVCC, CSNOUT, CSPOUT) on TRK_OUT: INTVCC is regulated from the output (8705af p.32)",
         [nets("U5")[k] for k in ("29", "30", "31")] == ["TRK_OUT"] * 3),
        ("U5's LCSC field %s and its land %s" % (u5["fields"].get("LCSC"), u5["footprint"].split(":")[1]),
         u5["fields"].get("LCSC") == "C674164" and "QFN-38" in u5["footprint"]),
        ("R8 102k 1% from PV_P to TRK_FBIN, R9 7.50k 1% to GND", e["components"]["R8"]["value"].startswith("102k 1%")
         and nets("R8") == {"1": "PV_P", "2": "TRK_FBIN"} and e["components"]["R9"]["value"].startswith("7.50k 1%")
         and nets("R9") == {"1": "TRK_FBIN", "2": "GND"}),
        ("R12 215k (RT), the oscillator's 202 kHz row", e["components"]["R12"]["value"].startswith("215k")),
        ("Q3 and Q5 BSC028N06NS (M1, M3), Q4 and Q6 BSC039N06NS (M2, M4)", all("BSC028N06NS" in e["components"][q]["value"] for q in ("Q3", "Q5"))
         and all("BSC039N06NS" in e["components"][q]["value"] for q in ("Q4", "Q6"))),
        ("PV_P carries F2, D4, the bulk C11 to C15, C64, Q3's drain, R8, R14, TP5 and U5", members("PV_P") ==
         ["C11", "C12", "C13", "C14", "C15", "C64", "D4", "F2", "Q3", "R14", "R8", "TP5", "U5"]),
    ]
    bad = [f for f, ok in facts if not ok]
    if bad:
        refuse(3, "a netlist fact does not hold: %s" % bad)
    R["facts"] = [f for f, _ in facts]
    gse = open(os.path.join(TOP, GEN_E), encoding="utf-8").read()
    r10 = need(gse, r'r\("R10", "(\d+)k 1% \(RFBOUT1', "gen_sch_e.py R10").group(1)
    R["r10_gen"] = r10

    # ================================================================== 2: the makers' rows
    p2, p3, p6, p6r = flat(pg(LT, 2, False)), pg(LT, 3), flat(pg(LT, 6)), flat(pg(LT, 6, False))
    order = {}
    for ln in p3.split("\n"):
        m = re.match(r"(LT8705A(E|I|H|MP)(UHF|FE)#PBF)\s+\S+\s+\S+\s+(.*?)\s{2,}([\u2013-]\d+)\u00b0C to (\d+)\u00b0C", ln)
        if m:
            order.setdefault(m.group(2), []).append((m.group(3), m.group(1), int(m.group(5).replace("\u2013", "-")), int(m.group(6))))
    if sorted(order) != ["E", "H", "I", "MP"]:
        refuse(3, "8705af p.3's order table does not read as four grades: %s" % sorted(order))
    qfn = {g for g, rows in order.items() if any(pk == "UHF" for pk, *_ in rows)}
    note3 = need(p6r, r"Note 3: The LT8705AE is guaranteed to meet performance specifications from 0\u00b0C to 125\u00b0C junction "
                 r"temperature\. Specifications over the [\u2013-]40\u00b0C to 125\u00b0C operating junction temperature range are "
                 r"assured by design, characterization and correlation with statistical process controls\. The LT8705AI is "
                 r"guaranteed over the full [\u2013-]40\u00b0C to 125\u00b0C junction temperature range\.", "8705af p.6 Note 3").group(0)
    tja = float(need(p2, r"UHF PACKAGE 38-LEAD \(5mm \u00d7 7mm\) PLASTIC QFN TJMAX = 125\u00b0C, \u03b8JA = (\d+)\u00b0C/W", "8705af p.2 QFN theta-JA").group(1))
    iq = float(need(flat(p3), r"VIN Quiescent Current Not Switching, VEXTVCC = 0 [\d.]+ ([\d.]+) mA", "8705af p.3 VIN quiescent maximum").group(1))
    fosc = need(p6, r"RT = 215k l (\d+) (\d+) (\d+) kHz", "8705af p.6 fOSC at RT 215k").groups()
    f_max = float(fosc[2]) * 1e3
    pages = {n: RP.pdf_lines(LT, n) for n in (2, 3, 4, 5, 6)}
    ref_p = RP.ec_row(pages, 4, "Regulation Voltages for IMON_IN and IMON_OUT", None)
    line_p = RP.ec_row(pages, 4, "Line Regulation for IMON_IN and IMON_OUT Error Amp", None)["max"]
    a7 = {g: RP.ec_row(pages, 5, "VCSPIN-CSNIN to IMON_IN Amplifier A7 gm", g) for g in ("(All Grades)", "(LT8705AE, LT8705AI)", "(LT8705AH, LT8705AMP)")}
    ea2 = RP.ec_row(pages, 5, "IMON_IN Error Amp EA2 Voltage Gain", None)["typ"]
    fbin = RP.ec_row(pages, 4, "Regulation Voltage for FBIN", "(LT8705AE, LT8705AI)")
    ea3 = RP.ec_row(pages, 4, "FBIN Error Amp EA3 Voltage Gain", None)["typ"]
    iovm = RP.ec_row(pages, 5, "IMON_IN Overvoltage Threshold", None)
    ioutmin = RP.ec_row(pages, 5, "IMON_IN Maximum Output Current", None)["min"]
    csd = RP.ec_row(pages, 5, "CSPIN, CSNIN Differential Operating Voltage Range", None)
    # the replay's own reading must be the same (its locals)
    if (ref_p, line_p) != (LR["ref_p"], LR["line_p"]) or LR["fb_p"][0] != fbin or abs(LR["dvc"] - 1.5) > 1e-12:
        refuse(4, "this record's read of 8705af differs from the replay's")
    p31 = flat(pg(LT, 31, False))
    need(p31, r"IMON_IN voltages exceeding 1\.208V \(typical\) cause the VC voltage to reduce, thus limiting the inductor and input currents", "p.31 the limit")
    cim = need(p31, r"CIMON_IN should be chosen by the equation:\W*(\d+)\W*F CIMON_IN >", "p.31 CIMON_IN's minimum").group(1)
    need(p31, r"bringing the CIMON_IN total to 0\.1\u03bcF to 1\u03bcF, may be necessary to maintain loop stability if the IMON_IN pin is used in a constant-current regulation loop", "p.31 CIMON_IN 0.1 to 1 uF")
    need(flat(pg(LT, 30, False)), r"do not place resistors in series with any of the CSxIN or CSxOUT pins", "p.30 no series resistance")
    need(flat(pg(LT, 32, False)), r"INTVCC is regulated by the EXTVCC LDO instead", "p.32 INTVCC from EXTVCC")
    need(flat(pg(LT, 34, False)), r"The actual die temperature can deviate from the above equation by \u00b110\u00b0C", "p.34 the CLKOUT junction method")
    R.update(order=order, qfn=sorted(qfn), note3=note3.replace("\u2013", "-"), tja=tja, iq=iq * 1e-3, f_max=f_max, ref_p=ref_p, line_p=line_p, a7=a7,
             ea2=ea2, fbin=fbin, ea3=ea3, iovm=iovm, ioutmin=ioutmin, csd=csd, cim=float(cim))
    # Milliohm HoJLR2512 series sheet (Ho-A0)
    h1, h2, h4 = flat(pg(HOJ, 1)), flat(pg(HOJ, 2)), flat(pg(HOJ, 4))
    need(h1, r"F=\u00b11%", "HoJLR p.1 the F tolerance code")
    tcr_h = float(need(h2, r"T\.C\.R \( ppm / \u2103 \) \u00b1(\d+) \(2mR~500mR\)", "HoJLR p.2 TCR").group(1)) * 1e-6
    need(h2, r"Operating Temperature Range -50\u2103~\+170\u2103", "HoJLR p.2 operating range")
    tcr_h_span = need(h4, r"Temperature Coefficient IEC60115-1-4\.8 JIS-C5201-4\.8 \+25\u2103 ~ \+125\u2103", "HoJLR p.4 the TCR test span").group(0)
    life_h = float(need(h4, r"Load Life JIS-C5201-4\.25\.1 < \u00b1(\d+)%", "HoJLR p.4 load life").group(1)) / 100.0
    sold_h = float(need(h4, r"Resistance to Soldering IEC60115-1-4\.18 260\u00b15\u2103 for 10\u00b11 sec < \u00b1([\d.]+)%", "HoJLR p.4 soldering heat").group(1)) / 100.0
    k_r = (170.0 - 70.0) / 3.0         # INFERRED, as r11_dep.py: the derating line, 3 W at 70 C to 0 at 170 C (p.2), in K/W
    need(h2, r"70\u2103", "HoJLR p.2 the derating onset")
    # YAGEO RT series V.16 (held)
    y2, y5, y7, y8 = flat(pg(RT, 2)), flat(pg(RT, 5)), flat(pg(RT, 7)), flat(pg(RT, 8))
    tol_y = float(need(y2, r"B = \u00b1 ([\d.]+)%", "RT p.2 tolerance B").group(1)) / 100.0
    tcr_y = float(need(y2, r"D = (\d+) ppm/\u00b0C", "RT p.2 TCR D").group(1)) * 1e-6
    need(y2, r"R = Paper/PE taping reel", "RT p.2 packaging R")
    need(flat(pg(RT, 7)), r"At \+25/\u201355 \u00b0C and \+25/\+125 \u00b0C", "RT p.7 the TCR test span")
    life_y = need(y7, r"Life/Endurance IEC 60115-1 4\.25\.1 At 70\u00b1 5 \u00b0C for 1,000 hours, rated voltage applied \u00b1 \(([\d.]+)%\+([\d.]+) \u03a9\)", "RT p.7 life").groups()
    sold_y = need(y8, r"Resistance to IEC 60115-1 4\.18 Condition B, no pre-heat of samples\. \u00b1 \(([\d.]+)%\+([\d.]+) \u03a9\)",
                  "RT p.8 soldering heat").groups()
    need(y5, r"RT0603 1/10W 75V 150V", "RT p.5 the RT0603 row")
    # Infineon gate charges (maximum, VGS 0 to 10 V)
    qg039 = float(need(flat(pg(BSC039, 4)), r"Gate charge total 1\) Qg - \d+ (\d+) nC VDD=30\W?V,\W?ID=50\W?A,\W?VGS=0\W?to\W?10\W?V", "BSC039N06NS p.4 Qg").group(1)) * 1e-9
    qg028 = float(need(flat(pg(BSC028, 3)), r"Gate charge total Qg (\d+) (\d+) (\d+)", "BSC028N06NS p.3 Qg").group(3)) * 1e-9
    need(flat(pg(BSC028, 3)), r"V GS=0 to 10 V", "BSC028N06NS p.3 the gate charge's VGS")
    R.update(tcr_h=tcr_h, tcr_h_span=tcr_h_span, life_h=life_h, sold_h=sold_h, k_r=k_r, tol_y=tol_y, tcr_y=tcr_y,
             life_y=(float(life_y[0]) / 100.0, float(life_y[1])), sold_y=(float(sold_y[0]) / 100.0, float(sold_y[1])), qg039=qg039, qg028=qg028)
    # the envelope (as r11_dep.py reads it)
    import yaml
    env = yaml.safe_load(open(os.path.join(TOP, ENV), encoding="utf-8"))
    t_air = max(env["worst_inside_air_c"]["lid_open"], env["worst_inside_air_c"]["lid_closed"])
    t_cold = env["ambient_c"]["in_use"]["min"]
    t_amb_hi = env["ambient_c"]["in_use"]["max"]
    R.update(t_air=t_air, t_cold=t_cold, t_amb_hi=t_amb_hi)
    # L4-E5's raised ceiling, from its reproduced record (0b)
    o5 = out5.decode("utf-8")
    m5 = need(o5, r"so E96 (\d+) k: ceiling ([\d.]+) / ([\d.]+) / ([\d.]+) V", "l4e5_source_control.out the tracker's raised ceiling")
    R["r10_5"], R["ceil5"] = m5.group(1), tuple(float(m5.group(i)) for i in (2, 3, 4))
    R["out_drawn"] = tuple(float(x) for x in need(o5, r"([\d.]+) / ([\d.]+) / ([\d.]+) V: FBOUT [\d.]+ / [\d.]+ / [\d.]+ V, MAKER 8705af p\.4",
                                                  "l4e5_source_control.out the drawn output band").groups())

    # ================================================================== 3: the catalogue (filed readings) and the choices
    lc = {c: catalogue(c) for c in ("C674164", "C674169", "C674170", "C148250")}

    def verify_rt(code, val):
        """A chosen RT0603BRD07 value must have its own filed LCSC reading, naming the same value, 0.1 % and 25 ppm/K, and
        linking the held RT sheet."""
        c = catalogue(code)
        lc[code] = c
        if rvalue(c["model"]) != val or c["params"].get("Tolerance") != "\u00b10.1%" or c["params"].get("Temperature Coefficient") != "\u00b125ppm/\u2103" \
                or c["pdf_sha256"] != PINS[RT]:
            refuse(3, "the filed reading of %s is not the chosen %.0f Ohm RT0603BRD07 part" % (code, val))
    if lc["C674164"]["model"] != "LT8705AEUHF#TRPBF" or lc["C674169"]["model"] != "LT8705AIUHF#PBF" or lc["C674170"]["model"] != "LT8705AIUHF#TRPBF":
        refuse(3, "the LT8705A catalogue readings are not the grades named")
    if any(lc[c]["pdf_sha256"] != PINS[LT] for c in ("C674164", "C674169", "C674170")):
        refuse(3, "LCSC's sheet for the LT8705A codes is not the filed 8705af")
    hoj = json.load(open(os.path.join(TOP, INP_L4E4), encoding="utf-8"))["rows"]
    rtj = json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-2026-10-01.json"), encoding="utf-8"))["rows"]

    # the IC grade (SESSION, below): the drawn land is the QFN; H and MP exist only in the TSSOP (p.3)
    grade = "I"
    if grade not in qfn or "H" in qfn or "MP" in qfn:
        refuse(4, "the grade reasoning's premise (only E and I in the QFN) does not hold")
    gm_lo, gm_hi = a7["(LT8705AE, LT8705AI)"]["min"], a7["(LT8705AE, LT8705AI)"]["max"]
    if not (gm_lo <= a7["(All Grades)"]["min"] and a7["(All Grades)"]["max"] <= gm_hi):
        refuse(4, "A7's 25 C limits are not inside the I grade's full-range limits")
    R.update(grade=grade, gm_lo=gm_lo, gm_hi=gm_hi)

    # RSENSE1: the HoJLR2512-3W value that puts the zero-margin limit nearest A7's printed 50 mV test point (p.5)
    vref_n = ref_p["typ"]
    dvc = LR["dvc"]

    def corner_k(v, gain, lmul, rs_lo, rm_lo):
        """I_lim / I_nom at v, every term at the end that raises the current (the replay's i_factor)."""
        return RP.i_factor(v, ref_p["max"], vref_n, line_p * lmul, 1, dvc / gain, 1, gm_lo, rs_lo, rm_lo)

    def low_k(v, gain, lmul, rs_hi, rm_hi):
        return RP.i_factor(v, ref_p["min"], vref_n, line_p * lmul, -1, dvc / gain, -1, gm_hi, rs_hi, rm_hi)
    v_oc, p_win = LR["v_oc"], LR["p_win"]

    def rfac(tol, tcr, dt, life=0.0, sold=0.0, sgn=-1):
        return (1 + sgn * tol) * (1 + sgn * tcr * abs(dt)) * (1 + sgn * life) * (1 + sgn * sold)
    i_zero = p_win / v_oc / corner_k(v_oc, ea2, 1.0, rfac(0.01, tcr_h, t_cold - 25.0), rfac(tol_y, tcr_y, t_cold - 25.0))
    hoj_ok = [(float(re.search(r"-([\d.]+)mR-1%", r_["model"]).group(1)) * 1e-3, r_["code"], r_["stock"]) for r_ in hoj
              if re.search(r"HoJLR2512-3W-[\d.]+mR-1%$", r_["model"]) and r_["stock"] >= STOCK_MIN]
    rs, rs_code, rs_stock = min(hoj_ok, key=lambda t: (abs(t[0] * i_zero - 0.050), t[0]))
    lc[rs_code] = catalogue(rs_code)
    if lc[rs_code]["model"] != "HoJLR2512-3W-%gmR-1%%" % (rs * 1e3) or lc[rs_code]["pdf_sha256"] != PINS[HOJ]:
        refuse(3, "the filed reading of %s is not the chosen RSENSE1" % rs_code)
    tol_h = float(lc[rs_code]["params"]["Tolerance"].strip("\u00b1%")) / 100.0

    # the two temperature ends: every part at the in-use minimum (a cold start, no self-heating); the hot end at the worst
    # inside air, RSENSE1 plus its own rise at the highest current the limit passes, by the derating line (INFERRED)
    def ends(i_nom_, rm_val):
        """(label, RSENSE1's temperature, RIMON_IN's (and R8's, R9's) temperature, the air, RSENSE1's watts). The hot end's
        RSENSE1 carries the most current the limit can pass (the stack under the design floor with drifts) and sits above the
        air by the derating line's K/W, iterated to its fixed point (INFERRED)."""
        t = t_air
        for _ in range(30):
            i_hi = i_nom_ * corner_k(v_oc, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, rfac(tol_h, tcr_h, t - 25.0, life_h, sold_h),
                                     rfac(tol_y, tcr_y, t_air - 25.0, R["life_y"][0] + R["life_y"][1] / rm_val, R["sold_y"][0] + R["sold_y"][1] / rm_val))
            p_rs = i_hi ** 2 * rs * (1 + tol_h) * (1 + tcr_h * (t - 25.0))
            t = t_air + p_rs * k_r
        return (("the cold end", t_cold, t_cold, t_cold, 0.0), ("the hot end", t, t_air, t_air, p_rs))

    # RIMON_IN: the largest stocked RT0603BRD07 setting whose corner passes at both ends under the SESSION floor
    def stack(rm_val, end, floor, drifts, i_nom):
        _lab, t_rs, t_rm, _t3, _p = end
        rs_lo = rfac(tol_h, tcr_h, t_rs - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0)
        rm_lo = rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rm_val) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm_val) if drifts else 0.0)
        gain = ea2 / EA2_FLOOR_DIV if floor else ea2
        lmul = LINE_FLOOR_MUL if floor else 1.0
        return v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo)
    cands = sorted({(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in rtj if rvalue(r_["model"]) and 20e3 <= rvalue(r_["model"]) < 30e3})
    rows_rm = []
    for rm_val, code, stock in cands:
        i_nom = vref_n / (a7["(All Grades)"]["typ"] * 1e-3 * rs * rm_val)
        e2 = ends(i_nom, rm_val)
        worst_floor = max(stack(rm_val, en, True, True, i_nom) for en in e2)
        worst_typ = max(stack(rm_val, en, False, False, i_nom) for en in e2)
        rows_rm.append((rm_val, code, stock, i_nom, worst_typ, worst_floor))
    ok_rm = [r_ for r_ in rows_rm if r_[2] >= STOCK_MIN and r_[5] <= p_win + 1e-9]
    if not ok_rm:
        refuse(4, "BLOCKER: no stocked RIMON_IN passes the corner under the design floor")
    rm, rm_code, rm_stock, i_nom = min(ok_rm, key=lambda t: t[0])[:4]
    verify_rt(rm_code, rm)
    R.update(rs=rs, rs_code=rs_code, rs_stock=rs_stock, tol_h=tol_h, rm=rm, rm_code=rm_code, rm_stock=rm_stock, i_nom=i_nom, i_zero=i_zero,
             rows_rm=rows_rm)
    END = ends(i_nom, rm)
    R["ends"] = END

    # ================================================================== 4: the hold (R8 and R9), REQ-016's 17.6 V point kept
    hold, trace, dsp = LR["hold"], LR["trace"], LR["dsp"]
    r8n, r9n = LR["r8"], LR["r9"]

    def band(r8v, r9v, ea3div, drifts=False):
        """The hold's lowest, nominal and highest over both ends: FBIN's I-grade limits (p.4), its line regulation, the EA3
        allowance at its gain / ea3div, the FBIN bias, and R8 and R9 at 0.1 % and 25 ppm/K (and their drifts when asked), through
        the replay's own hold()."""
        los, his = [], []
        for _lab, _t_rs, t_rm, _t3, _p in END:
            dt = t_rm - 25.0
            for s8, s9 in itertools.product((-1, 1), (-1, 1)):
                k8 = r8v / (r8n * 1e3) * rfac(tol_y, tcr_y, dt, (R["life_y"][0] + R["life_y"][1] / r8v) if drifts else 0.0,
                                               (R["sold_y"][0] + R["sold_y"][1] / r8v) if drifts else 0.0, s8)
                k9 = r9v / (r9n * 1e3) * rfac(tol_y, tcr_y, dt, (R["life_y"][0] + R["life_y"][1] / r9v) if drifts else 0.0,
                                               (R["sold_y"][0] + R["sold_y"][1] / r9v) if drifts else 0.0, s9)
                los.append(hold(fbin["min"], -1, -ea3div, k8, k9, LR["fbbias_p"]))
                his.append(hold(fbin["max"], 1, ea3div, k8, k9, 0.0))
        return min(los), hold(fbin["typ"], 0, 0, r8v / (r8n * 1e3), r9v / (r9n * 1e3), 0.0), max(his)
    e_at = {}

    def energy(v, lim=None):
        if lim is None:
            k = round(v, 6)
            if k not in e_at:
                e_at[k] = trace(dsp, v, None)
            return e_at[k]
        return trace(dsp, v, lim)
    # REQ-016 (approved) holds the panel at 17.6 V, and D-34 keeps REQ-016's window unchanged unless the owner rules otherwise
    # (check astra-check-l4e7-1, B1): the hold keeps the drawn nominal ratio. SESSION: R8 and R9 at their drawn values as the
    # RT0603BRD07 parts (0.1 %, 25 ppm/K) with the most stock; only tolerance and drift change.
    reqs = open(os.path.join(TOP, REQS), encoding="utf-8").read()
    r016 = " ".join(reqs.split("  - id: REQ-016\n", 1)[1].split("\n  - id: ", 1)[0].split())
    need(r016, r"the panel held at 17\.6 V by the stage's input regulation", "REQ-016's 17.6 V hold")
    need(r016, r"the FBIN divider R8 and R9 sets the 17\.6 V operating point", "REQ-016's acceptance on R8 and R9")
    d34 = " ".join(reqs.split("  - id: D-34\n", 1)[1].split("\n  - id: ", 1)[0].split())
    need(d34, r"authority: OWNER", "D-34's authority")
    need(d34, r"REQ-016's approved solar window stays unchanged", "D-34's ruling")
    r8v, r9v = r8n * 1e3, r9n * 1e3

    def stocked(val):
        rows = [(r_["stock"], r_["code"]) for r_ in rtj if rvalue(r_["model"]) == val and r_["stock"] >= STOCK_MIN]
        if not rows:
            refuse(4, "BLOCKER: no stocked RT0603BRD07 part at %.0f Ohm" % val)
        return max(rows)[1]
    r8c, r9c = stocked(r8v), stocked(r9v)
    for code, val in ((r8c, r8v), (r9c, r9v)):
        verify_rt(code, val)
    hb = band(r8v, r9v, 1.0)                                  # EA3 at its typical, tolerance and TCR
    hb4 = band(r8v, r9v, 1.0, drifts=True)                    # EA3 at its typical, with the soldering and life drifts
    hb2 = band(r8v, r9v, EA2_FLOOR_DIV)                       # EA3 at half its typical
    hb3 = band(r8v, r9v, EA2_FLOOR_DIV, drifts=True)          # EA3 at half, with the drifts: the widest conditioned band
    # the drawn circuit (check astra-check-l4e7-1, M1): the replay's band takes H and MP's FBIN minimum; with the E grade's
    # (the netlist's C674164) and the replay's other terms, 1 % resistors
    rt_ = RP.R_TOL
    drawn_e_lo = min(hold(fbin["min"], -1, -1, s8, s9, LR["fbbias_p"]) for s8 in (1 - rt_, 1 + rt_) for s9 in (1 - rt_, 1 + rt_))
    # the FBIN bias as an energy sensitivity (check M2): the lower corner (EA3 typical) with no bias, the typical and ten times it
    k8lo = rfac(tol_y, tcr_y, t_cold - 25.0, sgn=-1)
    k9hi = rfac(tol_y, tcr_y, t_cold - 25.0, sgn=1)
    bias_rows = []
    for mult in (0.0, 1.0, 10.0):
        lo_b = min(hold(fbin["min"], -1, -1, s8 * r8v / (r8n * 1e3), s9 * r9v / (r9n * 1e3), LR["fbbias_p"] * mult)
                   for s8 in (k8lo, rfac(tol_y, tcr_y, t_air - 25.0, sgn=-1)) for s9 in (k9hi, rfac(tol_y, tcr_y, t_air - 25.0, sgn=1)))
        bias_rows.append((mult * LR["fbbias_p"], lo_b, sum(energy(lo_b)[0])))
    R.update(r8v=r8v, r9v=r9v, r8c=r8c, r9c=r9c, hb=hb, hb2=hb2, hb3=hb3, hb4=hb4, drawn_e_lo=drawn_e_lo, bias_rows=bias_rows,
             fbin_hmp_min=LR["fb_p"][1]["min"],
             hold_drawn=(LR["v_lo"], LR["v_nom_hold"], LR["v_hi_hold"]), stock={r_["code"]: r_["stock"] for r_ in rtj})

    # THE PROPOSAL, NOT ADOPTED: a lower hold would change REQ-016's 17.6 V point and needs the owner's ruling (D-34). Nothing
    # below depends on it and no draft carries it: the stocked pair whose band's worse end gives the most energy on SC-37's day.
    r8s = sorted({(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in rtj if rvalue(r_["model"]) and 90e3 <= rvalue(r_["model"]) < 120e3 and r_["stock"] >= STOCK_MIN})
    r9s = sorted({(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in rtj if rvalue(r_["model"]) and 6e3 <= rvalue(r_["model"]) < 10e3 and r_["stock"] >= STOCK_MIN})
    hold_rows = []
    for (a8, c8, s8_), (a9, c9, s9_) in itertools.product(r8s, r9s):
        nom = fbin["typ"] * (1 + a8 / a9)
        if not (HOLD_RANGE[0] <= nom <= HOLD_RANGE[1]):
            continue
        lo, nm, hi = band(a8, a9, 1.0)
        elo, ehi = sum(energy(lo)[0]), sum(energy(hi)[0])
        hold_rows.append((round(min(elo, ehi), 1), -min(s8_, s9_), a8, a9, c8, c9, lo, nm, hi, elo, ehi))
    hold_rows.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    pb = hold_rows[0]
    R["proposal"] = dict(r8=pb[2], r9=pb[3], c8=pb[4], c9=pb[5], band=(pb[6], pb[7], pb[8]), e_band=(pb[9], sum(energy(pb[7])[0]), pb[10]),
                         e_nom_kept=sum(energy(hb[1])[0]), n=len(hold_rows))
    # the hourly maximum-power voltage on SC-37's day (the model's own), for the hold's reason
    AC = LR["AC"]
    vmpp = [dsp.mpp(LR["prof0"][h], AC.t_cell(LR["TA40"][h], LR["prof0"][h], LR["noct"]))[0] for h in range(24) if LR["prof0"][h] >= 100.0]
    R["vmpp"] = (min(vmpp), max(vmpp))

    # ================================================================== 5: THE CORNER CHECK on the achieved values
    v_lo_env = min(hb[0], hb2[0], hb3[0], hb4[0])         # the widest conditioned band's lowest (check M3)
    grid = sorted(set([v_lo_env, v_oc] + [round(v_lo_env + V_STEP * k, 6) for k in range(int((v_oc - v_lo_env) / V_STEP) + 1)]))
    grid = [v for v in grid if v_lo_env - 1e-12 <= v <= v_oc + 1e-12]

    def check(gain, lmul, drifts, tcr_cold_h=None):
        """Every vertex at every grid voltage at one end: the reference, its line term's sign, A7, the two resistors' ends and
        the EA2 term's sign. Returns, per end, the worst (power, voltage, vertex) and the corner count."""
        out = []
        for lab, t_rs, t_rm, _t3, _p in END:
            th = tcr_cold_h if (tcr_cold_h is not None and t_rs < 25.0) else tcr_h
            rs_e = [rfac(tol_h, th, t_rs - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0, s) for s in (-1, 1)]
            rm_e = [rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                         (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0, s) for s in (-1, 1)]
            worst, n = None, 0
            for vref, ls, gm, r1, r2, es in itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi), rs_e, rm_e, (-1, 1)):
                for v in grid:
                    pw = v * i_nom * RP.i_factor(v, vref, vref_n, line_p * lmul, ls, (dvc / gain) if gain else 0.0, es, gm, r1, r2)
                    n += 1
                    if worst is None or pw > worst[0]:
                        worst = (pw, v, vref, ls, gm, r1, r2, es)
            out.append((lab, worst, n))
        return out
    main_chk = check(ea2, 1.0, False)
    for lab, w, _n in main_chk:
        if w[0] > p_win + 1e-9:
            refuse(4, "the achieved setting %.4f A takes %.4f W at %.3f V (%s): over REQ-016's %.0f W" % (i_nom, w[0], w[1], lab, p_win))
    R["main_chk"] = main_chk
    R["chk_printed"] = check(None, 0.0, False)          # the two unprinted rows left out: what the printed rows alone give
    R["chk_floor"] = check(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True)
    R["chk_drift"] = check(ea2, 1.0, True)
    for lab, w, _n in R["chk_floor"]:
        if w[0] > p_win + 1e-9:
            refuse(4, "the setting fails its own design floor at %s" % lab)

    def breakeven_gain(lmul, drifts, end_i):
        lab, t_rs, t_rm, _t3, _p = END[end_i]
        rs_lo = rfac(tol_h, tcr_h, t_rs - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0)
        rm_lo = rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        f = lambda g: v_oc * i_nom * corner_k(v_oc, g, lmul, rs_lo, rm_lo)
        if v_oc * i_nom * RP.i_factor(v_oc, ref_p["max"], vref_n, line_p * lmul, 1, 0.0, 1, gm_lo, rs_lo, rm_lo) > p_win:
            return None
        lo, hi = 0.01, 1e6
        for _ in range(200):
            mid = math.sqrt(lo * hi)
            if f(mid) > p_win:
                lo = mid
            else:
                hi = mid
        return hi
    R["be_gain"] = {(lm, dr): [breakeven_gain(lm, dr, k) for k in range(2)] for lm in (1.0, 2.0, 5.0, 10.0) for dr in (False, True)}

    def breakeven_line(gain):
        lab, t_rs, t_rm, _t3, _p = END[0]
        rs_lo, rm_lo = rfac(tol_h, tcr_h, t_rs - 25.0), rfac(tol_y, tcr_y, t_rm - 25.0)
        lo, hi = 0.0, 1e4
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if v_oc * i_nom * corner_k(v_oc, gain, mid, rs_lo, rm_lo) > p_win:
                hi = mid
            else:
                lo = mid
        return lo
    R["be_line"] = (breakeven_line(ea2), breakeven_line(ea2 / EA2_FLOOR_DIV))

    def breakeven_tcr_cold(gain, lmul, drifts):
        """RSENSE1's TCR below 25 C at which the cold 25 V corner (the worst, above) reaches 100 W under the named stack (check
        M2: each break-even states its stack); searched up to 10000 ppm/K, inside which the low end (1 - TCR x 45 K) stays positive
        and the power rises with the TCR."""
        dt = abs(END[0][1] - 25.0)
        rm_lo = rfac(tol_y, tcr_y, END[0][2] - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        f = lambda tc: v_oc * i_nom * corner_k(v_oc, gain, lmul, rfac(tol_h, tc, dt, life_h if drifts else 0.0, sold_h if drifts else 0.0), rm_lo)
        if f(0.01) <= p_win:
            return None
        lo, hi = 0.0, 0.01
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid) > p_win:
                hi = mid
            else:
                lo = mid
        return lo
    R["be_tcr_cold"] = breakeven_tcr_cold(ea2, 1.0, False)                                   # stack A
    R["be_tcr_cold_floor"] = breakeven_tcr_cold(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True)   # stack C, the design floor
    # the old setting on the achieved parts (information): 3.548 A on the replay's 1 mA grid, with these parts
    R["old_on_parts"] = max(v_oc * LR["i_set"] * corner_k(v_oc, ea2, 1.0, rfac(tol_h, tcr_h, en[1] - 25.0), rfac(tol_y, tcr_y, en[2] - 25.0)) for en in END)

    # ================================================================== 6: the conditions the mechanism needs (CONDITION rows)
    vd_lim_hi = i_nom * max(corner_k(v_oc, ea2, 1.0, 1.0, 1.0), 1.0) * rs * (1 + tol_h)
    dt_max = max(abs(en[1] - 25.0) for en in END)
    v_fault_max = iovm["max"] / (gm_lo * 1e-3 * rm * (1 - tol_y) * (1 - tcr_y * dt_max))       # the sense voltage at which IMON_IN reaches its fault maximum
    i_imon_lim = vd_lim_hi * gm_hi * 1e-3
    cim_min = R["cim"] / (float(fosc[0]) * 1e3 * rm)
    R.update(vd_lim_hi=vd_lim_hi, v_fault_max=v_fault_max, i_imon_lim=i_imon_lim, cim_min=cim_min, tau=rm * 100e-9)
    isc_hot = AC.isc_at(AC.CAND["SPR100"], 70.0)
    R["vd_isc"] = isc_hot * rs * (1 + tol_h) * (1 + tcr_h * dt_max)

    # ================================================================== 7: U5's junction (INFERRED) and RSENSE1's rise
    i_g = iq * 1e-3 + f_max * (2 * qg028 + 2 * qg039)
    p_ic = R["ceil5"][2] * i_g
    R.update(i_g=i_g, p_ic=p_ic, tj_hot=t_air + tja * p_ic, tj_hot_old=t_air + tja * R["out_drawn"][2] * i_g, tj_cold=t_cold)

    # ================================================================== 8: the energy (MODELED, the replay's trace and runs)
    lo_h, nom_h, hi_h = hb
    vert = list(itertools.product((ref_p["min"], ref_p["max"]), (-1, 1), (gm_lo, gm_hi), (-1, 1), (-1, 1), (-1, 1)))

    def lim_of(inom, rmv, which, gain=ea2, lmul=1.0):
        def f(v):
            vals = []
            for lab, t_rs, t_rm, _t3, _p in END:
                for a, b, gm, s1, s2, c_ in vert:
                    vals.append(RP.i_factor(v, a, vref_n, line_p * lmul, b, dvc / gain, c_, gm, rfac(tol_h, tcr_h, t_rs - 25.0, sgn=s1),
                                            rfac(tol_y, tcr_y, t_rm - 25.0, sgn=s2)))
            return inom * (min(vals) if which == "lo" else max(vals))
        return f
    # the zero-margin catalogue setting: the largest stocked value passing at the typical rows (no floor, no drifts)
    zero = min([r_ for r_ in rows_rm if r_[2] >= STOCK_MIN and r_[4] <= p_win + 1e-9], key=lambda t: t[0])
    R["zero"] = zero
    grid_e = []
    for hl, vh in (("lower hold corner", lo_h), ("nominal hold", nom_h), ("upper hold corner", hi_h),
                   ("lower, EA3 at its floor", hb2[0]), ("upper, EA3 at its floor", hb2[2]),
                   ("lower, EA3 floor, drifts", hb3[0]), ("upper, EA3 floor, drifts", hb3[2])):
        row = [hl, vh, sum(energy(vh)[0])]
        for inom, rmv in ((i_nom, rm), (zero[3], zero[0])):
            for which in ("lo", "nom", "hi"):
                lim = (lambda v, i=inom: i) if which == "nom" else lim_of(inom, rmv, which)
                tr, nl = energy(vh, lim)
                row.append((sum(tr), nl, tr))
        grid_e.append(row)
    R["grid_e"] = [(r_[0], r_[1], r_[2]) + tuple((x[0], x[1]) for x in r_[3:]) for r_ in grid_e]
    R["e_mpp"] = LR["e_mpp"]
    # the irradiance at which the limit's lowest begins to bind at the hold's nominal and lower corner (hour 12's air)
    ta12 = LR["TA40"][12]
    gb = []
    for inom, rmv in ((i_nom, rm), (zero[3], zero[0])):
        for vh in (lo_h, nom_h):
            lim = lim_of(inom, rmv, "lo")(vh)
            g_lo, g_hi = 50.0, 1500.0
            for _ in range(60):
                g = 0.5 * (g_lo + g_hi)
                if dsp.current(vh, g, AC.t_cell(ta12, g, LR["noct"]), LR["rl"]) > lim:
                    g_hi = g
                else:
                    g_lo = g
            gb.append((inom, vh, lim, g_hi))
    R["g_bind"], R["ta12"] = gb, ta12
    # A1 and A2 on the new traces, exactly as the replay's section 12 runs them (CORRECTED, WE, TYP, the service ledger)
    meanday, least, gs, archs, win = LR["meanday"], LR["least"], LR["gs"], LR["archs"], LR["win_req016"]
    tr_nom = grid_e[1][4][2]                            # the nominal hold, the limit nominal
    cands_w = [(r_[0] + ", limit at its lowest", r_[3][2]) for r_ in grid_e[:3]] + [(r_[0] + ", no limit", energy(r_[1])[0]) for r_ in grid_e[:3]]
    lab_w, tr_w = min(cands_w, key=lambda t: sum(t[1]))
    runs = {}
    tr_cond = energy(hb3[2])[0]                          # the conditioned envelope's upper end (EA3 at half, drifts): information
    for lab, tr in (("NEW nominal (hold %.3f V, limit %.3f A)" % (nom_h, i_nom), tr_nom), ("NEW least-energy corner (%s)" % lab_w, tr_w),
                    ("NEW conditioned upper end (%.3f V: EA3 at half, the resistors' drifts; information)" % hb3[2], tr_cond)):
        for ak, _alab, n in archs:
            r_ = [meanday(ak, "WE", n, "TYP", h, win, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            x = [least(ak, "WE", "TYP", h, win, 1.0, 160.0, 34, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0) for h in (48, 72)]
            kk = "el" if ak == "A2" else "eb"
            add = [(meanday(ak, "WE", x[i], "TYP", h, win, collapse=False, gser=gs(tr), wp=100.0, ratio=1.0)[kk] - r_[i][kk])
                   if x[i] is not None else None for i, h in enumerate((48, 72))]
            runs[(lab, ak)] = (sum(tr), r_[1]["stops"], r_[0]["uns"], r_[1]["uns"], add)
    R["runs"] = runs
    old = {}
    for k, (r_, add) in LR["ctr"].items():
        if k[0].startswith("CORRECTED, WE; O-2 nominal") or k[0].startswith("CORRECTED, WE; the least-energy corner"):
            old[(k[0].split(" (")[0] if "O-2 nominal" in k[0] else "CORRECTED, WE; the least-energy corner", k[1])] = (r_[1]["stops"], r_[0]["uns"], r_[1]["uns"], add)
    R["old_runs"] = old
    R["old_grid"] = [(g_[0], g_[1], g_[2], g_[3], g_[4]) for g_ in LR["grid_rows"]]

    # ================================================================== 10: QUALIFICATION OF THE 100 W BOUND (the owner's instruction,
    # 1 October 2026): each unprinted value classified by the outcome it affects, the sheet searched for a guaranteed limit
    # beyond the electrical table, a conservative assumption and the qualification it needs where none exists, the corners
    # shown to bound the permitted range, and the states outside them made a computed case or a bench obligation.
    ia = json.load(open(os.path.join(TOP, INP, "ia-8705af-20250322064938.json"), encoding="utf-8"))
    if ia["sha256"] != PINS[LT] or ia["url"] != OFFICIAL_URL or ia["snapshot"] != IA_SNAPSHOT:
        refuse(3, "the Internet Archive reading of 8705af is not the held sheet at the official URL")
    raw = {n: flat(pg(LT, n, False)) for n in range(1, 45)}
    if sum(1 for n in raw if "8705af" in raw[n]) != 44:
        refuse(3, "8705af does not print its code on each of its 44 pages")
    R["prov"] = dict(url=ia["url"], snapshot=ia["snapshot"], sha=ia["sha256"], read=ia["read_utc"])
    # what the sheet gives beyond the electrical table (each phrase read back; curves are TYPICAL, p.7 and p.8 headers)
    for n, phrase in ((7, "Feedback Voltages"), (7, "Inductor Current Sense Voltage at Minimum Duty Cycle"),
                      (7, "TA = 25\u00b0C unless otherwise specified"), (8, "Maximum VC vs SS"), (8, "IMON Output Currents"),
                      (8, "TA = 25\u00b0C unless otherwise specified"), (14, "which is the diode-AND of error amplifiers EA1-EA4"),
                      (15, "gradual ramp-up of the inductor current by gradually allowing the VC voltage to rise"),
                      (18, "synchronous switch M4 is held off whenever reverse current in the inductor is detected"),
                      (33, "The loop stability is affected by a number of factors"), (34, "reaches approximately 165\u00b0C")):
        need(raw[n], re.escape(phrase), "8705af p.%d '%s'" % (n, phrase))
    ec = {r_["id"]: r_ for r_ in RP.EC_ROWS}
    unprinted_rows = {k: (ec[k]["page"], ec[k]["full"], ec[k]["min"], ec[k]["typ"], ec[k]["max"]) for k in ("EA2_AV", "EA2_GM", "IMON_LINE", "EA3_AV", "FBIN_BIAS")}
    if any(v[1] for v in unprinted_rows.values()) or any(unprinted_rows[k][2] is not None for k in ("EA2_AV", "EA3_AV", "FBIN_BIAS")):
        refuse(4, "a row taken as unprinted carries a full-range limit or a minimum")
    R["unprinted_rows"] = unprinted_rows
    # (a) monotonicity: P(v) = v I_set F(v); dP/dv = I_set [Vref (1 + ls lam (2v - 12)) + es dVC / G] / (Vref_typ gm r1 r2) at every vertex
    def dpdv_min(gain, lmul):
        lam = line_p * lmul * 1e-2
        return min(a * (1 + ls * lam * (2 * v - V_LINE_REF)) + es * dvc / gain
                   for a in (ref_p["min"], ref_p["max"]) for ls in (-1, 1) for es in (-1, 1) for v in (v_lo_env, v_oc))
    V_LINE_REF = RP.V_LINE_REF
    R["dpdv"] = (dpdv_min(ea2, 1.0), dpdv_min(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL))
    if min(R["dpdv"]) <= 0:
        refuse(4, "the power is not increasing in the input voltage at every vertex")
    for nm, chk in (("A", R["main_chk"]), ("B", R["chk_printed"]), ("C", R["chk_floor"]), ("D", R["chk_drift"])):
        if any(abs(w[1] - v_oc) > 1e-9 for _l, w, _n in chk):
            refuse(4, "stack %s's dense check finds its worst below the 25 V vertex" % nm)
    # (b) RSENSE1's temperature: the break-even over the air, stacks A and C (a hot spot on the board beside L1 and the FETs)
    def rs_t_breakeven(gain, lmul, drifts):
        rm_lo = rfac(tol_y, tcr_y, t_air - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        f = lambda t: v_oc * i_nom * corner_k(v_oc, gain, lmul, rfac(tol_h, tcr_h, t - 25.0, life_h if drifts else 0.0, sold_h if drifts else 0.0), rm_lo)
        if f(170.0) <= p_win:
            return None
        lo, hi = 25.0, 170.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(mid) > p_win:
                hi = mid
            else:
                lo = mid
        return lo
    R["rs_t_be"] = (rs_t_breakeven(ea2, 1.0, False), rs_t_breakeven(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True))
    # (c) the conservative assumptions one at a time on stack A (the cold end, the worse), and together (stack C with RSENSE1's
    # cold TCR at twice its printed hot-side value)
    TCR_COLD_CONS = 2.0 * tcr_h
    def p_cold(gain, lmul, drifts, tcr_cold):
        dt = abs(END[0][1] - 25.0)
        rs_lo = rfac(tol_h, tcr_cold, dt, life_h if drifts else 0.0, sold_h if drifts else 0.0)
        rm_lo = rfac(tol_y, tcr_y, END[0][2] - 25.0, (R["life_y"][0] + R["life_y"][1] / rm) if drifts else 0.0,
                     (R["sold_y"][0] + R["sold_y"][1] / rm) if drifts else 0.0)
        return v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo)
    R["cons"] = dict(base=p_cold(ea2, 1.0, False, tcr_h), ea2=p_cold(ea2 / EA2_FLOOR_DIV, 1.0, False, tcr_h),
                     line=p_cold(ea2, LINE_FLOOR_MUL, False, tcr_h), tcr=p_cold(ea2, 1.0, False, TCR_COLD_CONS),
                     joint=p_cold(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, TCR_COLD_CONS), tcr_cons=TCR_COLD_CONS)
    if R["cons"]["joint"] > p_win:
        refuse(4, "the conservative assumptions together take the corner over 100 W")
    # (d) protection: the IMON_IN fault (p.5, full range) against the regulated point; the fault/limit ratio does not depend on RSENSE1
    reg_hi = ref_p["max"] * (1 + line_p * 1e-2 * (v_oc - V_LINE_REF))
    R["g_fault"] = dvc / (iovm["min"] - reg_hi)                         # EA2 gain below which regulation would reach the fault (safe side)
    R["k_fault"] = (iovm["min"] / ref_p["max"] - 1.0) / (line_p * 1e-2 * (v_oc - V_LINE_REF))
    R["tsd"], R["tj_margin"] = 165.0, 125.0 - R["tj_hot"]
    # the fault-to-limit ratio at its least (check astra-check-l4e7q-1, B2): the fault minimum over the regulated IMON_IN at its
    # highest, the line and EA2 allowances included (stack A, and the conservative assumptions together)
    reg_a = ref_p["max"] * (1 + line_p * 1e-2 * (v_oc - V_LINE_REF)) + dvc / ea2
    reg_c = ref_p["max"] * (1 + LINE_FLOOR_MUL * line_p * 1e-2 * (v_oc - V_LINE_REF)) + dvc / (ea2 / EA2_FLOOR_DIV)
    R["fault_ratio"] = dict(reg_a=reg_a, reg_c=reg_c, a=iovm["min"] / reg_a, c=iovm["min"] / reg_c)
    # RSENSE1's cold TCR from its printed 50 to the assumed 100 ppm/K at -20 C: the sense-path loop gain moves with RSENSE1 and the
    # current at which the fault trips with 1 / RSENSE1 (p.31); the comparator's threshold voltage (p.5) does not move
    dt_c = abs(END[0][1] - 25.0)
    rs50, rs100 = 1 - tcr_h * dt_c, 1 - TCR_COLD_CONS * dt_c
    R["tcr_effects"] = dict(loop=rs100 / rs50 - 1.0, trip=rs50 / rs100 - 1.0, dt=dt_c)
    # LINE: the setpoint moves with the source voltage, a coupling path into the loop: over the envelope's swing at most
    swing = v_oc - v_lo_env
    R["line_coupling"] = dict(swing=swing, printed=line_p * swing, assumed=LINE_FLOOR_MUL * line_p * swing)
    # A7 (check B1): its gm row is guaranteed at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V; the design runs CSPIN at the panel
    # voltage and about the sense voltage below. The effective gain may fall this far, other terms fixed, before 100 W
    need(raw[5], r"VCSPIN - VCSNIN = 50mV, VCSPIN = 5\.025V|VCSPIN \u2013 VCSNIN = 50mV, VCSPIN = 5\.025V", "8705af p.5 A7's test condition")
    need(raw[8], r"IMON Output Currents", "8705af p.8 the IMON output currents curve (TYPICAL, against the differential only)")
    a7_be = dict(a=[gm_lo * w[0] / p_win for _l, w, _n in R["main_chk"]], c=[gm_lo * w[0] / p_win for _l, w, _n in R["chk_floor"]],
                 joint=gm_lo * R["cons"]["joint"] / p_win)
    R["a7q"] = dict(be=a7_be, vd=R["vd_lim_hi"], cm=(v_lo_env, v_oc), cm_range=(R["csd"]["min"], R["csd"]["max"]),
                   loss=dict(a=[100 * (1 - g / gm_lo) for g in a7_be["a"]], c=[100 * (1 - g / gm_lo) for g in a7_be["c"]],
                             joint=100 * (1 - a7_be["joint"] / gm_lo)))
    # M1: the thermal coupling. The paired ends put both resistors in the same air at each end; the mixed envelope lets each take
    # its own worst end independently, and a dense air sweep (0.1 C, RSENSE1 with and without its rise) checks the pairing
    def rfac_end(tol, tcr_lo, tcr_hi, t, drifts_life, drifts_sold):
        return rfac(tol, tcr_lo if t < 25.0 else tcr_hi, t - 25.0, drifts_life, drifts_sold)

    def p_mixed(gain, lmul, drifts, tcr_cold):
        dl_h, ds_h = (life_h, sold_h) if drifts else (0.0, 0.0)
        dl_y, ds_y = ((R["life_y"][0] + R["life_y"][1] / rm), (R["sold_y"][0] + R["sold_y"][1] / rm)) if drifts else (0.0, 0.0)
        rs_lo = min(rfac_end(tol_h, tcr_cold, tcr_h, t_, dl_h, ds_h) for t_ in (END[0][1], END[1][1]))
        rm_lo = min(rfac_end(tol_y, tcr_y, tcr_y, t_, dl_y, ds_y) for t_ in (END[0][2], END[1][2]))
        return v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo)

    def p_sweep(gain, lmul, drifts, tcr_cold):
        dl_h, ds_h = (life_h, sold_h) if drifts else (0.0, 0.0)
        dl_y, ds_y = ((R["life_y"][0] + R["life_y"][1] / rm), (R["sold_y"][0] + R["sold_y"][1] / rm)) if drifts else (0.0, 0.0)
        best = 0.0
        for k in range(int(round((t_air - t_cold) * 10)) + 1):
            ta = t_cold + 0.1 * k
            for rise in (0.0, END[1][1] - t_air):
                rs_lo = rfac_end(tol_h, tcr_cold, tcr_h, ta + rise, dl_h, ds_h)
                rm_lo = rfac_end(tol_y, tcr_y, tcr_y, ta, dl_y, ds_y)
                best = max(best, v_oc * i_nom * corner_k(v_oc, gain, lmul, rs_lo, rm_lo))
        return best
    R["thermal"] = dict(
        paired=dict(a=R["main_chk"][0][1][0], c=R["chk_floor"][0][1][0], joint=R["cons"]["joint"]),
        mixed=dict(a=p_mixed(ea2, 1.0, False, tcr_h), c=p_mixed(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, tcr_h),
                   joint=p_mixed(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, TCR_COLD_CONS)),
        sweep=dict(a=p_sweep(ea2, 1.0, False, tcr_h), c=p_sweep(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, tcr_h),
                   joint=p_sweep(ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, TCR_COLD_CONS)))
    if max(R["thermal"]["mixed"].values()) > p_win:
        refuse(4, "the mixed-temperature envelope takes a corner over 100 W")
    need(raw[34], r"reaches approximately 165\u00b0C", "8705af p.34 the thermal shutdown")
    # (e) the hold's lowest against the 25 V corner (why EA3 and the FBIN bias do not reach the bound)
    def p_at(v, gain, lmul, drifts, tcr_cold):
        """The worst power at input v over both ends' resistor values and both line signs, the named stack (check M2: matching stacks)."""
        dl_h, ds_h = (life_h, sold_h) if drifts else (0.0, 0.0)
        dl_y, ds_y = ((R["life_y"][0] + R["life_y"][1] / rm), (R["sold_y"][0] + R["sold_y"][1] / rm)) if drifts else (0.0, 0.0)
        rs_lo = min(rfac(tol_h, tcr_cold if t_ < 25.0 else tcr_h, t_ - 25.0, dl_h, ds_h) for t_ in (END[0][1], END[1][1]))
        rm_lo = min(rfac(tol_y, tcr_y, t_ - 25.0, dl_y, ds_y) for t_ in (END[0][2], END[1][2]))
        return max(v * i_nom * RP.i_factor(v, ref_p["max"], vref_n, line_p * lmul, ls, dvc / gain, 1, gm_lo, rs_lo, rm_lo) for ls in (-1, 1))
    R["p_hold_lo"] = dict(c=p_at(v_lo_env, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, tcr_h),
                          joint=p_at(v_lo_env, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, True, 2.0 * tcr_h), a=p_at(v_lo_env, ea2, 1.0, False, tcr_h))
    # (f) states outside the corners
    voc40 = LR["voc40"]
    p40 = voc40 * i_nom * corner_k(voc40, ea2, 1.0, rfac(tol_h, tcr_h, -40.0 - 25.0), rfac(tol_y, tcr_y, -40.0 - 25.0))
    caps = 0.0
    for ref in ("C11", "C12", "C13", "C14", "C15", "C64"):
        m = re.match(r"([\d.]+)(u|n)", e["components"][ref]["value"])
        caps += float(m.group(1)) * (1e-6 if m.group(2) == "u" else 1e-9)
    cspr = AC.CAND["SPR100"]
    tol_p = float(need(" ".join(RP.pdf_lines(RP.SPR_PDF[0], 1)), r"Power Tolerance\s+\+(\d+)/", "the SunPower sheet's power tolerance").group(1)) / 100.0
    t_cell_cold = AC.t_cell(t_cold, 1000.0, LR["noct"])
    p_panel_cold = cspr["p"] * (1 + tol_p) * (1 + cspr["gamma_p"] * (t_cell_cold - 25.0))
    p_panel_soak = cspr["p"] * (1 + tol_p) * (1 + cspr["gamma_p"] * (t_cold - 25.0))     # a cold-soaked cell at -20 C, 1000 W/m2
    R["outside"] = dict(voc40=voc40, p40=p40, c_vin=caps, e_caps=0.5 * caps * v_oc ** 2, t_cell_cold=t_cell_cold, p_panel_cold=p_panel_cold,
                        tol_p=tol_p, p_panel_soak=p_panel_soak, gamma=cspr["gamma_p"])
    # (g) the design option that removes RSENSE1's cold TCR unknown: a stocked 15 mOhm 1 % 2512 whose maker states TCR from
    # -55 C, evaluated by the same rules (Vishay Dale WSL, Document Number 30100, Revision 23-Nov-2023, held)
    WSL = "v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf"
    if sha(WSL) != "1b5c68910aa562a0dcce11ec572b4dd1febe63cfb90d20f3eaf5f9c7e01b59ac":
        refuse(2, "%s is not the pinned file (fetch it: v2/docs/records/l4e7/fetch_held_back.py)" % WSL)
    w1, w2, w3 = flat(pg(WSL, 1)), flat(pg(WSL, 2)), flat(pg(WSL, 3))
    wp = float(need(w1, r"WSL2512 2512 ([\d.]+) \(1\) 0\.003 to 0\.5", "WSL p.1 WSL2512's P70").group(1))
    wtcr = float(need(w2, r"\u00b1 (\d+) for 7 m\u03a9 to 500 m\u03a9", "WSL p.2 TCR 7 to 500 mOhm").group(1)) * 1e-6
    need(w2, r"TCR measured from -55 \u00b0C to \+155 \u00b0C", "WSL p.2 the TCR's span")
    wtop = float(need(w2, r"Operating temperature range \u00b0C -65 to \+(\d+)", "WSL p.2 operating range").group(1))
    wlife = need(w3, r"Load life 1000 h at rated power, \+ 70 \u00b0C.*?\u00b1 \(([\d.]+) % \+ ([\d.]+) \u03a9\)", "WSL p.3 load life").groups()
    wsold = need(w3, r"Resistance to solder heat .*?\u00b1 \(([\d.]+) % \+ ([\d.]+) \u03a9\)", "WSL p.3 solder heat").groups()
    wc = catalogue("C844695")
    if wc["model"] != "WSL2512R0150FEA" or wc["params"].get("Tolerance") != "\u00b11%" or wc["pdf_sha256"] != sha(WSL):
        refuse(3, "the filed WSL reading is not the evaluated part")
    w_kr = (wtop - 70.0) / wp                                         # INFERRED, as for HoJLR: rated at 70 C to zero at the top of its range
    w_life = float(wlife[0]) / 100.0 + float(wlife[1]) / rs
    w_sold = float(wsold[0]) / 100.0 + float(wsold[1]) / rs

    def p_wsl(rmv, inom, floor):
        out = []
        t = t_air
        for _ in range(30):
            i_hi = inom * corner_k(v_oc, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, rfac(0.01, wtcr, t - 25.0, w_life, w_sold), 1.0)
            t = t_air + i_hi ** 2 * rs * 1.01 * w_kr
        for t_rs, t_rm in ((t_cold, t_cold), (t, t_air)):
            rs_lo = rfac(0.01, wtcr, t_rs - 25.0, w_life if floor else 0.0, w_sold if floor else 0.0)
            rm_lo = rfac(tol_y, tcr_y, t_rm - 25.0, (R["life_y"][0] + R["life_y"][1] / rmv) if floor else 0.0,
                         (R["sold_y"][0] + R["sold_y"][1] / rmv) if floor else 0.0)
            out.append(v_oc * inom * corner_k(v_oc, ea2 / EA2_FLOOR_DIV if floor else ea2, LINE_FLOOR_MUL if floor else 1.0, rs_lo, rm_lo))
        return max(out), t
    wa, w_t = p_wsl(rm, i_nom, False)
    wf, _ = p_wsl(rm, i_nom, True)
    w_ok = [(rv, c_, st, iv) for rv, c_, st, iv, _a, _b in rows_rm if st >= STOCK_MIN and p_wsl(rv, iv, True)[0] <= p_win]
    w_pick = min(w_ok, key=lambda t: t[0]) if w_ok else None
    R["wsl"] = dict(model=wc["model"], code="C844695", stock=wc["stock"], p70=wp, tcr=wtcr, life=w_life, sold=w_sold, kr=w_kr, t_hot=w_t,
                    p_a=wa, p_floor=wf, pick=w_pick, cost=(1.0 - w_pick[3] / i_nom) if w_pick else None)
    # the classification (each figure above; `resolved` is True only where the sheet or a maker's statement bounds the row)
    WARRANT = ("a limit the manufacturer warrants, with the conditions it applies to; characterization over production lots is "
               "supporting evidence, not a production guarantee, and the row stays CONDITIONAL until a warranted limit exists")
    rows = [
        dict(id="EA2", name="EA2's gain and VC's operating range", bound=True, stability=True, protection=False, other="energy, only in hours the limit binds",
             small={},
             why_bound="the regulated IMON_IN moves by (VC - 1.2 V) / gain (p.5, p.2): %.4f W at 130 V/V against %.4f W with the term left out (stack A, cold)" % (
                 R["main_chk"][0][1][0], R["chk_printed"][0][1][0]),
             why_stability="EA2 drives VC through the compensation network in the input-current loop; with no printed minimum gain or gm the loop's margin is not guaranteed (p.33: the loop stability is affected by a number of factors)",
             why_protection="the IMON_IN fault is a comparator on IMON_IN itself (p.5, 1.55 V minimum, full range), not through EA2; only a gain under %.2f V/V would hold the regulated point at the fault, which stops switching (the safe side)" % R["g_fault"],
             sheet="p.5 EA2 gain 130 V/V and gm 185 umho, typical only; p.4 the IMON_IN regulation, full range, printed at VC = 1.2 V; p.2 VC's absolute maximum -0.3 to 2.2 V; p.7 'Inductor Current Sense Voltage at Minimum Duty Cycle' against VC and p.8 'Maximum VC vs SS' plot VC within 0.5 to 2.0 V (TYPICAL, TA = 25 C; not a limit); p.31 the current-limiting text names 1.208 V typical and no gain bound",
             guaranteed=None,
             conservative="EA2 at least 65 V/V (half its typical) with VC anywhere in its absolute maximum range (the replay's allowance doubled)",
             qualification="Analog Devices: EA2's minimum gain, or the IMON_IN regulation point's shift with VC, over -40 to 125 C junction, as " + WARRANT + "; a bench reading of a few units (7b.10) checks the design only",
             margin_w=p_win - R["cons"]["ea2"], breakeven="%.6f V/V (stack A, cold), %.6f V/V (stack C's other terms, cold)" % (R["be_gain"][(1.0, False)][0], R["be_gain"][(2.0, True)][0]),
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="A7", name="A7's gain outside its test point (50 mV differential, CSPIN at 5.025 V)", bound=True, stability=True, protection=True,
             other="energy, only in hours the limit binds",
             small={},
             why_bound="the limit is 1.208 V / (gm x RSENSE1 x RIMON_IN) (p.31): the effective gain enters in proportion. The full-range gm row (0.94 / 1.06 mmho, E and I) is printed at a 50 mV differential with CSPIN at 5.025 V; the design runs CSPIN at the panel voltage, %.3f to %.0f V, and up to %.1f mV across RSENSE1. The CSPIN and CSNIN ranges, 1.5 to 80 V common mode and %.0f to %.0f mV differential (p.5), are operating ranges, not a gain guarantee" % (
                 R["a7q"]["cm"][0], R["a7q"]["cm"][1], 1e3 * R["a7q"]["vd"], R["a7q"]["cm_range"][0], R["a7q"]["cm_range"][1]),
             why_stability="the sense path's gain enters the input-current loop in proportion; an error outside the test point moves the loop gain by the same fraction",
             why_protection="the fault comparator's threshold voltage on IMON_IN (p.5) does not move; the input current at which it trips moves inversely with the effective gain, as the limit does",
             sheet="p.5 A7 gm 0.95 / 1.05 mmho at 25 C and 0.94 / 1.06 mmho over the full range (E, I), each at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V; p.5 CSPIN and CSNIN 1.5 to 80 V common mode and -100 to 100 mV differential (operating ranges); p.8 'IMON Output Currents' plots the output current against the differential only (TYPICAL, TA = 25 C); no curve against common mode, no transfer-error or offset row",
             guaranteed="the gm limits at the test point, over the full temperature range; nothing printed at the design's common mode and differential, or while switching",
             conservative="the test-point limits apply at the design's common mode and differential while switching (an extrapolation, ASSUMPTION)",
             qualification="Analog Devices: A7's transfer error (gm and offset) over the common mode, the differential, -40 to 125 C junction and switching the design uses, as " + WARRANT,
             margin_w=p_win - R["main_chk"][0][1][0],
             breakeven="the effective gain may fall to %.6f mmho (%.4f %% under 0.94) under stack A, %.6f mmho (%.4f %%) under stack C and %.6f mmho (%.4f %%) under every conservative assumption together, other terms fixed (cold)" % (
                 R["a7q"]["be"]["a"][0], R["a7q"]["loss"]["a"][0], R["a7q"]["be"]["c"][0], R["a7q"]["loss"]["c"][0], R["a7q"]["be"]["joint"], R["a7q"]["loss"]["joint"]),
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="LINE", name="the IMON_IN reference's line regulation while switching and at temperature", bound=True, stability=True, protection=False,
             other="energy, a fraction of a percent of the limit, only in hours it binds",
             small={"stability": "the setpoint moves with the source voltage: over the envelope's %.3f V swing at most %.4f %% printed, %.4f %% assumed" % (
                 R["line_coupling"]["swing"], R["line_coupling"]["printed"], R["line_coupling"]["assumed"])},
             why_bound="the reference moves with VIN from the 12 V it is printed at: at 25 V the printed maximum moves the corner by %.4f W" % (R["main_chk"][0][1][0] - p_cold(ea2, 0.0, False, tcr_h)),
             why_stability="small, not zero: the reference's VIN dependence couples a moving source voltage into the regulated current (a feedforward path, at most %.4f %% of the setpoint per volt assumed); the loop's margin is set elsewhere" % (
                 LINE_FLOOR_MUL * line_p),
             why_protection="the regulated point would reach the IMON_IN fault minimum only at %.0f times the printed maximum" % R["k_fault"],
             sheet="p.4 0.002 / 0.005 %/V, VIN 12 to 80 V, not switching, at 25 C (no bullet); p.4 the regulation itself is a full-range row at VIN = 12 V, so its temperature drift at 12 V is guaranteed; p.7 'Feedback Voltages' against temperature at VC = 1.2 V is TYPICAL",
             guaranteed="the full-range IMON_IN regulation row covers temperature at VIN = 12 V; the VIN dependence while switching and away from 25 C is not printed",
             conservative="twice the printed maximum (0.010 %/V), either sign, at every temperature and while switching",
             qualification="Analog Devices: the IMON_IN reference's line regulation while switching, over -40 to 125 C junction, as " + WARRANT,
             margin_w=p_win - R["cons"]["line"], breakeven="%.1f times the printed maximum (stack A, cold); %.1f with EA2 at 65 V/V" % R["be_line"],
             resolved=False, clarification="analog-devices-lt8705a.txt"),
        dict(id="TCR", name="RSENSE1's TCR below +25 C", bound=True, stability=True, protection=True,
             other="energy, a fraction of a percent of the limit, only in hours it binds",
             small={"stability": "the sense-path loop gain moves with RSENSE1: %+.4f %% from 50 to %.0f ppm/K at -20 C" % (100 * R["tcr_effects"]["loop"], TCR_COLD_CONS * 1e6),
                    "protection": "the current at which the fault trips moves with 1 / RSENSE1 (p.31): %+.4f %% from 50 to %.0f ppm/K at -20 C; the comparator's threshold does not move" % (
                        100 * R["tcr_effects"]["trip"], TCR_COLD_CONS * 1e6)},
             why_bound="RSENSE1 sits in the limit's denominator; at -20 C its TCR sets its low end",
             why_stability="small, not zero: the sense-path loop gain is proportional to RSENSE1, %+.4f %% from 50 to %.0f ppm/K at -20 C; the loop's margin is set by the compensation" % (
                 100 * R["tcr_effects"]["loop"], TCR_COLD_CONS * 1e6),
             why_protection="small, not zero: the fault comparator's threshold voltage (IMON_IN 1.55 / 1.61 / 1.67 V, p.5) does not move, but the input current at which it trips is proportional to 1 / RSENSE1 (p.31), %+.4f %% from 50 to %.0f ppm/K at -20 C. The fault-to-limit ratio does not depend on RSENSE1; at its least it is %.6f (stack A, regulation at most %.9f V) and %.6f with every conservative assumption (regulation at most %.9f V)" % (
                 100 * R["tcr_effects"]["trip"], TCR_COLD_CONS * 1e6, R["fault_ratio"]["a"], R["fault_ratio"]["reg_a"], R["fault_ratio"]["c"], R["fault_ratio"]["reg_c"]),
             sheet="HoJLR2512 Ho-A0 p.2 +-50 ppm/K (2 to 500 mOhm); p.4 the TCR test spans +25 to +125 C only; the catalogue prints no TCR for C2903494",
             guaranteed=None,
             conservative="+-%.0f ppm/K below +25 C (twice the printed hot-side value)" % (TCR_COLD_CONS * 1e6),
             qualification="Milliohm: the HoJLR2512 TCR from -40 to +25 C, as " + WARRANT + "; a bench reading of R59 at -20 C (7b.14) checks the design only",
             margin_w=p_win - R["cons"]["tcr"], breakeven="%.3f ppm/K (stack A), %.3f ppm/K (stack C)" % (R["be_tcr_cold"] * 1e6, R["be_tcr_cold_floor"] * 1e6),
             resolved=False, clarification="milliohm-hojlr2512.txt"),
        dict(id="HOLD", name="EA3's gain and the FBIN bias", bound=False, stability=True, protection=False, other="energy (the hold band)",
             small={},
             why_bound="they set the hold, the envelope's low end %.6f V, where the matching stacks (each resistor at its worst end) read %.4f W (A), %.4f W (C, drifts included) and %.4f W (every conservative assumption) against %.4f W, %.4f W and %.4f W at 25 V: the power rises with the input voltage at every vertex" % (
                 v_lo_env, R["p_hold_lo"]["a"], R["p_hold_lo"]["c"], R["p_hold_lo"]["joint"], R["main_chk"][0][1][0], R["chk_floor"][0][1][0], R["cons"]["joint"]),
             why_stability="EA3 closes the input-voltage loop through VC; its margin is part of the hold's bench row",
             why_protection="the hold is a regulation, not a protection; FBOUT's overvoltage and the IMON_IN fault are other pins",
             sheet="p.4 EA3 90 V/V and FBIN bias 10 nA, typical only; p.4 FBIN regulation 1.184 / 1.226 V, full range (I grade), at VC = 1.2 V",
             guaranteed="the FBIN reference is full range; the gain and the bias are typical",
             conservative="EA3 at half its typical with the resistors' drifts: the hold inside %.3f to %.3f V; the bias at ten times its typical moves the lower corner by %.1f mV" % (
                 hb3[0], hb3[2], 1e3 * (R["bias_rows"][2][1] - R["bias_rows"][1][1])),
             qualification="none for the bound; the hold's energy rows carry them as sensitivities and 7b.12 reads the hold",
             margin_w=None, breakeven=None, resolved=False, clarification=None),
        dict(id="TJ", name="U5's junction temperature", bound=True, stability=False, protection=True, other="lifetime (Note 3: derated above 125 C)",
             small={},
             why_bound="every LT8705A row the corner uses is a full-range row, guaranteed for the I grade from -40 to 125 C junction (p.6 Note 3); the bound needs only the junction inside that range, not its value",
             why_stability="the loop's gains move with temperature inside the unprinted EA2 and A7 rows already carried above",
             why_protection="the overtemperature protection acts at approximately 165 C (p.34, approximate): the estimate stays %.1f K under it" % (165.0 - R["tj_hot"]),
             sheet="p.2 theta-JA 34 C/W (UHF, a package figure on the maker's board); p.3 the VIN quiescent current, 4.2 mA maximum, printed at 25 C, not switching, EXTVCC = 0; p.6 Note 3 and Note 8; p.34 the CLKOUT method (+-10 C) and the thermal shutdown at approximately 165 C",
             guaranteed="the I grade's rows hold over -40 to 125 C junction; no junction temperature is printed for this board",
             conservative="an INFERRED estimate, TJ about %.1f C: the maximum gate charge at 10 V for all four FETs at the highest oscillator frequency, the VIN quiescent maximum (printed at 25 C, not switching, EXTVCC = 0, so an extrapolation), EXTVCC at L4-E5's %.2f V ceiling and theta-JA 34 C/W (board-dependent) in %.1f C air; not a demonstrated upper bound" % (
                 R["tj_hot"], R["ceil5"][2], t_air),
             qualification="a design verification of board E's thermal path (7b.13 by p.34's method, +-10 C), with the margin covering the unit spread the maximum gate charge already bounds",
             margin_w=None, margin_k=R["tj_margin"], breakeven="125 C junction (%.1f K above the estimate)" % R["tj_margin"], resolved=False, clarification=None),
    ]
    for r_ in rows:
        if r_["clarification"]:
            cp = os.path.join(TOP, CLAR, r_["clarification"])
            if not os.path.isfile(cp):
                refuse(3, "the clarification text %s is missing" % r_["clarification"])
            ct = open(cp, encoding="utf-8").read()
            if not ct.startswith("DRAFT FOR THE OWNER TO SEND.") or not any(k in ct for k in ("LT8705AIUHF", "HoJLR2512-3W-15mR-1%")):
                refuse(3, "the clarification text %s does not read as a draft naming its part" % r_["clarification"])
    R["qual_rows"] = rows
    R["bound_status"] = bound_status(rows)
    # ================================================================== 11: THE CONTROL DECISION (L4-E7R, the owner's instruction of
    # 1 October 2026; second round after checks/astra-check-l4e7r-1.md): the verdict on the present limit; at most three approaches,
    # each bound with every term classed by the maker's row for its own condition (a term no row bounds is CONDITIONAL and carried by
    # its break-even, never by a common multiplier); the chosen arrangement's static bound, its dynamics and averaging basis, its
    # supply sequencing, its coordination with the regulation, its energy on SC-37's day and a bright day, and the solar entry's
    # protection against the derived disturbance (each SESSION decision named where it is taken)
    INA, TPS = "v2/vendor/ti/held/ti-ina250-sbos511c.pdf", "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf"
    I169, T38 = "v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "v2/vendor/ti/ti-tps3808.pdf"
    LM69, SMC = "v2/vendor/ti/ti-lm5069.pdf", "v2/vendor/power/littelfuse-smcj-series-tvs.pdf"
    ZA = "v2/vendor/power/held/panasonic-za-eehza1h330xp-2017-11-07.pdf"
    for rel_, want_ in ((INA, "4690d49c0e10739b6dfc1da4d56bc2eeda8276d9b8816fb7b90db539c1eb0868"),
                        (TPS, "27c94a6c3a243bf539e98942d26f0bd9ed979c5775c12cf86b7c1a8c3d7d9560"),
                        (I169, "dbb74b6cdc5431353f17b044b7d762df1f2f9049d03d2d1611a53058e570d62c"),
                        (T38, "74d889c0f68af88032f1633c26381817cc03e10d9fd3b4c177a044ad3ed86eed"),
                        (LM69, "d60d8106a6e8113900ff8b9576dd959942fa7169742baf0beeb30684d4d64681"),
                        (SMC, "6e610db955ed876306999009c62b242f7de9bb05e2cd9717288a96586a5093ea"),
                        (ZA, "43628e509458b8995a5c5e1ade2334286c5acfddf859bf9aa4daf59d5653258a")):
        if sha(rel_) != want_:
            refuse(2, "%s is not the pinned file (fetch it: v2/docs/records/l4e7/fetch_held_back.py)" % rel_)
    # ---- the INA250 (approach B): every row read, then classed by its own condition
    i5, i6, i15 = flat(pg(INA, 5)), flat(pg(INA, 6)), flat(pg(INA, 15, False))
    need(i5, r"At TA = 25.C, VS = 5 V, VIN\+ = 12 V, VREF = 2\.5 V, ISENSE = IN\+ = 0 A, unless otherwise noted", "INA250 p.5 the test conditions")
    cmr = float(need(i5, r"INA250A2, VIN\+ = 0 V to 36 V, (\d+) \d+ TA = .40.C to 125.C", "INA250 p.5 CMR A2").group(1))
    ios = float(need(i5, r"INA250A2, ISENSE = 0 A \u00b1[\d.]+ \u00b1(\d+)", "INA250 p.5 offset A2").group(1)) * 1e-3
    dios = float(need(i5, r"dIOS/dT RTI versus temperature TA = .40.C to 125.C \d+ (\d+) \u03bcA/.C", "INA250 p.5 offset drift").group(1)) * 1e-6
    psr = float(need(i5, r"PSR VS = 2\.7 V to 36 V, TA = .40.C to 125.C \u00b1[\d.]+ \u00b1(\d+) mA/V", "INA250 p.5 PSR").group(1)) * 1e-3
    rsh_n = float(need(i5, r"Shunt resistance [\d.]+ (\d+) [\d.]+", "INA250 p.5 shunt").group(1)) * 1e-3
    st = need(i5, r"Shunt short time overload ISENSE = 30 A for 5 seconds \u00b1([\d.]+)% Shunt thermal shock .65.C to 150.C, 500 cycles \u00b1([\d.]+)% "
              r"Shunt resistance to solder 260.C solder, 10 s \u00b1([\d.]+)% heat Shunt high temperature 1000 hours, TA = 150.C \u00b1([\d.]+)% "
              r"exposure Shunt cold temperature 24 hours, TA = .65.C \u00b1([\d.]+)%", "INA250 p.5 the shunt's stress rows (typical only)").groups()
    stress_sh = sum(float(x) for x in st) / 100.0
    nl = float(need(i6, r"Nonlinearity error ISENSE = 0\.5 A to 10 A \u00b1([\d.]+)%", "INA250 p.6 nonlinearity (typical only)").group(1)) / 100.0
    ro = float(need(i6, r"RO Output impedance ([\d.]+) [\u2126\u03a9]", "INA250 p.6 output impedance (typical only)").group(1))
    g_ina = float(need(i6, r"INA250A2 (\d+) mV/A", "INA250 p.6 gain A2").group(1)) * 1e-3
    eg = float(need(i6, r"System gain error\(6\) \u00b1([\d.]+)% TA = .40.C to 125.C", "INA250 p.6 full-range system gain error").group(1)) / 100.0
    need(flat(pg(INA, 6, False)), r"System gain error does not include the stress related characteristics", "INA250 p.6 note 6")
    iq_ina = float(need(i6, r"IQ Quiescent current TA = .40.C to 125.C \d+ (\d+) \u03bcA", "INA250 p.6 IQ").group(1)) * 1e-6
    ib_ina = float(need(i5, r"IB Input bias current IB\+, IB., ISENSE = 0 A \u00b1[\d.]+ \u00b1(\d+) \u03bcA", "INA250 p.5 IB (25 C)").group(1)) * 1e-6
    abs_ina = float(need(flat(pg(INA, 4)), r"Analog inputs \(IN\+, IN.\) Common-mode GND . 0\.3 (\d+)", "INA250 p.4 IN+ and IN- absolute maximum").group(1))
    need(i15, r"For unidirectional operation, tie the REF pin to ground", "INA250 p.15 REF to ground for unidirectional operation")
    # ---- the TPS3701 (both B and C): its rows hold over TJ -40 to 125 C and VDD 1.8 to 36 V
    t5, t6 = flat(pg(TPS, 5)), flat(pg(TPS, 6))
    need(t5, r"Over the operating temperature range of TJ = .40.C to \+125.C, 1\.8 V \u2264 VDD < 36 V", "TPS3701 p.5 the full-range header")
    vit = need(t5, r"VIT\+\(INB\) INB pin positive input threshold voltage VDD = 1\.8 V to 36 V (\d+) (\d+) (\d+) mV", "TPS3701 p.5 VIT+(INB)").groups()
    vth = (float(vit[0]) * 1e-3, float(vit[2]) * 1e-3)
    vth_typ = float(vit[1]) * 1e-3
    via = need(t5, r"VIT.\(INA\) INA pin negative input threshold voltage VDD = 1\.8 V to 36 V (\d+) (\d+) (\d+) mV", "TPS3701 p.5 VIT-(INA)").groups()
    via_p = need(t5, r"VIT\+\(INA\) INA pin positive input threshold voltage VDD = 1\.8 V to 36 V (\d+) ([\d.]+) (\d+) mV", "TPS3701 p.5 VIT+(INA)").groups()
    vtha = (float(via[0]) * 1e-3, float(via_p[2]) * 1e-3)            # INA asserts below the first; releases above at most the second
    iin_t = float(need(t5, r"VDD = 1\.8 V and 36 V, VINA, VINB = 6\.5 V .(\d+) \+1 \+\d+ nA", "TPS3701 p.5 input current").group(1)) * 1e-9
    vol_max = float(need(t5, r"VDD = 5 V, IOUT = 5 mA \d+ (\d+) mV", "TPS3701 p.5 VOL").group(1)) * 1e-3
    vdd_t = float(need(t5, r"VDD Supply voltage range ([\d.]+) 36 V", "TPS3701 p.5 VDD").group(1))
    uvlo_t = need(t5, r"UVLO Undervoltage lockout \(2\) VDD falling ([\d.]+) ([\d.]+) ([\d.]+) V", "TPS3701 p.5 UVLO").groups()
    need(t5, r"When VDD falls below UVLO, OUTA is driven low and OUTB goes to high impedance", "TPS3701 p.5 note 2")
    st_t = float(need(flat(pg(TPS, 6, False)), r"VDD must exceed 1\.8 V for at least (\d+) [\u00b5\u03bc]s \(typical\)", "TPS3701 p.6 note 2 (start)").group(1)) * 1e-6
    tpd_lh = float(need(t6, r"tpd\(LH\) Low-to-high propagation delay \(1\) .*?([\d.]+) [\u00b5\u03bc]s", "TPS3701 p.6 tpd(LH) (typical)").group(1)) * 1e-6
    need(flat(pg(TPS, 6, False)), r"High-to-low and low-to-high refers to the transition at the input pins", "TPS3701 p.6 note 1 (the input edge)")
    # ---- the TPS3808 (both B and C): the supervisor, its reset delay with CT to VDD, its power-up reset
    s6, s7, s4 = flat(pg(T38, 6)), flat(pg(T38, 7)), flat(pg(T38, 4))
    need(s6, r"1\.7V \u2264 VDD \u2264 6\.5V, RLRESET = 100k\u2126, CLRESET = 50pF, over operating temperature range \(TJ = .40.C to 125.C\)", "TPS3808 p.6 the header")
    acc38 = float(need(s6, r"VIT \u2264 3\.3V .([\d.]+)% \u00b10\.5% ([\d.]+)%", "TPS3808 p.6 VIT accuracy (VIT up to 3.3 V, full range)").group(2)) / 100.0
    hys38 = float(need(s6, r"Fixed versions 1% ([\d.]+)%", "TPS3808 p.6 VHYS of the fixed versions").group(1)) / 100.0
    vit38 = float(need(flat(pg(T38, 3)), r"TPS3808G33 3\.3V ([\d.]+)V", "TPS3808 p.3 the G33 threshold").group(1))
    vpor38 = float(need(s6, r"VPOR Power-up reset voltage\(2\) VOL \(max\) = 0\.2V, I RESET = 15\u03bcA ([\d.]+)", "TPS3808 p.6 VPOR").group(1))
    need(flat(pg(T38, 6, False)), r"Trise\(VDD\) \u2265 15 \u03bcs/V", "TPS3808 p.6 the ramp condition of VPOR")
    vol38 = float(need(s6, r"1\.8V \u2264 VDD \u2264 6\.5V, IOL = 1mA ([\d.]+) V", "TPS3808 p.6 VOL at 1 mA").group(1))
    rmr38 = float(need(s6, r"R MR MR Internal pullup resistance (\d+) \d+ k\u2126", "TPS3808 p.6 MR pull-up minimum").group(1)) * 1e3
    td38 = need(s7, r"CT = VDD (\d+) (\d+) (\d+) ms", "TPS3808 p.7 td with CT to VDD").groups()
    td_min = float(td38[0]) * 1e-3
    vdd38 = float(need(s6, r"TJ < 125.C ([\d.]+) 6\.5 V VDD Input supply range", "TPS3808 p.6 VDD").group(1))
    ioh38 = float(need(s6, r"IOH RESET leakage current V RESET = 6\.5V, RESET not asserted (\d+) nA", "TPS3808 p.6 RESET leakage").group(1)) * 1e-9
    need(s4, r"Connecting this pin to VDD through a 40k\u2126 to 200k\u2126 resistor", "TPS3808 p.4 CT to VDD through 40k to 200k")
    need(s4, r"Driving the manual reset pin \( MR\) low asserts RESET", "TPS3808 p.4 MR")
    mr_ns = float(need(s7, r"MR to RESET VIH = 0\.7VDD, VIL = 0\.3VDD (\d+) ns", "TPS3808 p.7 MR to RESET (typical)").group(1)) * 1e-9
    # ---- the INA169 (approach C): every row at TA -40 to 85 C, V+ = 5 V, VIN+ = 12 V, ROUT = 25 kOhm; CMR and PSR printed at VSENSE = 50 mV
    j6, j4 = flat(pg(I169, 6)), flat(pg(I169, 4))
    need(j6, r"INA169: all other characteristics at TA = .40.C to \+85.C V\+ = 5 V, VIN\+ = 12 V, and ROUT = 25 k[\u2126\u03a9]", "INA169 p.6 the header")
    cmr169 = float(need(j6, r"INA169: (\d+) 120 dB VIN\+ = 2\.7 V to 60 V, VSENSE = 50 mV", "INA169 p.6 CMR at VSENSE = 50 mV").group(1))
    vos169 = float(need(j6, r"INA169 \u00b10\.2 \u00b1(\d+) vs\. temperature", "INA169 p.6 offset (RTI)").group(1)) * 1e-3
    psr169 = float(need(j6, r"INA169: 0\.1 (\d+) \u00b5V/V V\+ = 2\.7 V to 60 V, VSENSE = 50 mV", "INA169 p.6 PSR at VSENSE = 50 mV").group(1)) * 1e-6
    gm169 = need(j6, r"VSENSE = 10 mV . 150 mV (\d+) 1000 (\d+) \u00b5A/V", "INA169 p.6 transconductance").groups()
    gm169 = (float(gm169[0]) * 1e-6, float(gm169[1]) * 1e-6)                 # A/V
    nl169 = float(need(j6, r"INA169 \u00b10\.01% \u00b1([\d.]+)%", "INA169 p.6 nonlinearity").group(1)) / 100.0
    iq169 = float(need(j6, r"Quiescent current VSENSE = 0, IO = 0 \d+ (\d+) \u00b5A", "INA169 p.6 quiescent").group(1)) * 1e-6
    sw169 = float(need(j6, r"Swing to power supply, V\+ \(V\+\) . [\d.]+ \(V\+\) . ([\d.]+)", "INA169 p.6 swing to V+").group(1))
    swcm169 = float(need(j6, r"Swing to common-mode, VCM VCM . [\d.]+ VCM . ([\d.]+)", "INA169 p.6 swing to VCM").group(1))
    need(j6, r"Specification, TMIN to TMAX INA169 .40 85 .C", "INA169 p.6 the specified range")
    need(j6, r"Defined as the amount of voltage \(VSENSE\) to drive the output to zero", "INA169 p.6 note 1 (the offset)")
    abs169 = need(j4, r"\(2\) Common-mode .0\.3 (\d+) V Analog inputs, INA169 Differential \(VIN\+\) . \(VIN.\) .40 (\d+) V", "INA169 p.4 inputs' absolute maxima").groups()
    abs169 = (float(abs169[0]), float(abs169[1]))
    ipin169 = float(need(j4, r"Input current into any pin (\d+) mA", "INA169 p.4 input current into any pin").group(1)) * 1e-3
    vsabs169 = float(need(j4, r"Supply voltage, VS INA169 .0\.3 (\d+) V", "INA169 p.4 V+ absolute maximum").group(1))
    bw169 = float(need(j6, r"Bandwidth ROUT = 20 k[\u2126\u03a9] (\d+) kHz", "INA169 p.6 bandwidth at 20 kOhm (typical)").group(1)) * 1e3
    ro169 = float(need(j6, r"Output impedance (\d+) \|\| 5 G[\u2126\u03a9] \|\| pF", "INA169 p.6 output impedance (typical)").group(1)) * 1e9
    ts169 = float(need(j6, r"Settling time \(0\.1%\) 5-V step, ROUT = 20 k[\u2126\u03a9] (\d+) [\u00b5\u03bc]s", "INA169 p.6 settling at 20 kOhm (typical)").group(1)) * 1e-6
    # ---- the LT8705A rows the arrangement uses (all printed; none is an answer the drafts ask for)
    ldo = need(flat(p3), r"LDO33 Pin Voltage 5mA from LDO33 Pin l ([\d.]+) ([\d.]+) ([\d.]+) V", "8705af p.3 LDO33").groups()
    v_ldo = (float(ldo[0]), float(ldo[2]))
    ilim33 = float(need(flat(p3), r"LDO33 Pin Current Limit l (\d+) [\d.]+ (\d+) mA", "8705af p.3 LDO33 current limit").group(2)) * 1e-3
    uvi = float(need(flat(p3), r"INTVCC, GATEVCC Undervoltage Lockout INTVCC Falling, GATEVCC Connected to INTVCC l ([\d.]+)", "8705af p.3 INTVCC lockout").group(1))
    swen_r = RP.ec_row(pages, 4, "SWEN Rising Threshold Voltage (Note 5)", None)
    need(raw[12], r"SWEN \(Pin 36 QFN Only\): Switch Enable Pin\. Tie high to enable switching\. Ground to disable switching\. Don.t float this pin", "8705af p.12 SWEN")
    need(raw[14], r"In the initialize state, the SS \(soft-start\) pin is pulled low", "8705af p.14 the initialize state")
    need(raw[15], r"INITIALIZE . SS PULLED LOW", "8705af p.15 Figure 2 (SS pulled low)")
    csd_abs = float(need(p2, r"VCSP-VCSN, VCSPIN-VCSNIN, VCSPOUT-VCSNOUT\.+ .0\.3V to ([\d.]+)V", "8705af p.2 CSPIN-CSNIN absolute maximum").group(1))
    vin_abs = float(need(p2, r"VIN, EXTVCC Voltage\.+ .0\.3V to (\d+)V", "8705af p.2 VIN absolute maximum").group(1))
    fb_abs = float(need(p2, r"FBIN, SHDN Voltage\.+ .0\.3V to (\d+)V", "8705af p.2 FBIN and SHDN absolute maximum").group(1))
    r14_ = float(re.match(r"([\d.]+)k", e["components"]["R14"]["value"]).group(1)) * 1e3
    r15_ = float(re.match(r"([\d.]+)k", e["components"]["R15"]["value"]).group(1)) * 1e3
    # ---- the clamp D4 and the bulk the entry needs (the derived disturbance, below)
    l1, l2 = flat(pg(SMC, 1, False)), flat(pg(SMC, 2))
    need(l1, r"1500W peak pulse power capability at 10/1000[\u00b5\u03bc]s waveform", "SMCJ p.1 the 10/1000 us rating")
    d4row = need(l2, r"SMCJ28A SMCJ28CA GFG BFG (\d+\.\d) (\d+\.\d+) (\d+\.\d+) 1 (\d+\.\d) (\d+\.\d) (\d+) X", "SMCJ p.2 the SMCJ28A row").groups()
    d4 = dict(vr=float(d4row[0]), vbr=(float(d4row[1]), float(d4row[2])), vc=float(d4row[3]), ipp=float(d4row[4]), ir=float(d4row[5]) * 1e-6)
    z1, z2 = flat(pg(ZA, 1)), flat(pg(ZA, 2))
    zrow = need(z2, r"50 33 6\.3 7\.7 D8 (\d+) (\d+) [\d.]+ EEHZA1H330XP", "ZA p.2 the EEHZA1H330XP row").groups()
    za = dict(v=50.0, c=33e-6, ripple=float(zrow[0]) * 1e-3, esr=float(zrow[1]) * 1e-3)
    za["tol"] = float(need(z1, r"Capacitance tolerance \u00b1(\d+) % \(120 Hz/\+20 .C\)", "ZA p.1 capacitance tolerance").group(1)) / 100.0
    za["end_dc"] = float(need(z1, r"Capacitance change Within \u00b1(\d+)% of the initial value tan d < 200 % of the initial limit E\. S\. R\. < 200 % of the initial limit Endurance", "ZA p.1 endurance capacitance").group(1)) / 100.0
    za["esr_cold"] = float(need(z1, r"\(.40 .C\) 2\.0 1\.4 ([\d.]+) 0\.4 0\.3", "ZA p.1 ESR after endurance at -40 C (D8)").group(1))
    lm6 = flat(pg(LM69, 6))
    need(flat(pg(LM69, 5)), r"VIN = 48 V \(unless otherwise noted\)", "LM5069 p.5 the header")
    vcl69 = need(lm6, r"VCL Threshold voltage VIN-SENSE voltage ([\d.]+) (\d+) ([\d.]+) mV", "LM5069 p.6 VCL").groups()
    # ---- the parts' catalogue readings (filed under inputs/)
    lc_ina, lc_tps, lc169, lc38, lcza, lc104 = (catalogue(c_) for c_ in ("C2859736", "C132788", "C44322", "C43698", "C178637", "C14663"))
    if (lc_ina["model"], lc_tps["model"], lc169["model"], lc38["model"], lcza["model"]) != ("INA250A2PWR", "TPS3701DDCR", "INA169NA/3K", "TPS3808G33DBVR", "EEHZA1H330XP") \
            or lcza["params"].get("Voltage Rating") != "50V" or lc104["params"].get("Voltage Rating") != "50V":
        refuse(3, "the arrangement's catalogue readings are not the parts named")
    amps_pk = float(need(gse, r'_intent\.rail\(_pvn, 17\.6, 5\.68, ([\d.]+), "J_SOLAR" if _pvn == "PV_IN" else "F2"', "gen_sch_e.py the panel entry's amps_peak").group(1))
    dt_end = max(abs(t_cold - 25.0), abs(t_air - 25.0))

    # ---- shared models: the regulation's highest current under the joint assumptions at any RIMON_IN (each resistor at its own
    # worst end, the mixed envelope), the bright day (SESSION: the check's definition), and the energy of a setting on both days
    def inom_of(rmv):
        return vref_n / (a7["(All Grades)"]["typ"] * 1e-3 * rs * rmv)

    def reg_hi(rmv, v):
        rs_lo = min(rfac_end(tol_h, TCR_COLD_CONS, tcr_h, t_, life_h, sold_h) for t_ in (END[0][1], END[1][1]))
        rm_lo = min(rfac_end(tol_y, tcr_y, tcr_y, t_, R["life_y"][0] + R["life_y"][1] / rmv, R["sold_y"][0] + R["sold_y"][1] / rmv)
                    for t_ in (END[0][2], END[1][2]))
        return inom_of(rmv) * corner_k(v, ea2 / EA2_FLOOR_DIV, LINE_FLOOR_MUL, rs_lo, rm_lo)
    BRIGHT = [1000.0 * math.sin(math.pi * (h - 6) / 12.0) if 6 < h < 18 else 0.0 for h in range(24)]
    ta12 = round(LR["TA40"][12], 1)                         # 18.1 C, as the check states it

    def bright(vh, lim):
        """SESSION, the check's bright day (astra-check-l4e7r-1, D3): a twelve-hour sine to 1000 W/m2 at noon, the air constant at
        18.1 C (SC-37's hour-12 value to 0.1 C), NOCT 47 C, the replay's panel, lead and op_point, by the trace's a1solar convention."""
        out, nl_ = [], 0
        for h in range(24):
            g = BRIGHT[h]
            if g <= 0.0:
                out.append(0.0)
                continue
            tc = AC.t_cell(ta12, g, LR["noct"])
            pw, _v, _i, limited = LR["op_point"](dsp, g, tc, vh, lim, LR["rl"])
            out.append(RP.BUD.panel_w(g, 100.0, LR["pr0"]) * (pw / AC.arr_mpp(dsp, 1, 1, g, tc)[0]))
            nl_ += limited
        return out, nl_

    def day(inom_, rmv):
        out = []
        for lab, vh in (("lower", lo_h), ("nominal", nom_h), ("upper", hi_h)):
            tr, nl_ = energy(vh, lim_of(inom_, rmv, "lo"))
            out.append((lab, vh, sum(tr), nl_))
        btr, bnl = bright(nom_h, lim_of(inom_, rmv, "lo"))
        out.append(("bright", nom_h, sum(btr), bnl))
        return out
    gnoon = 1000.0
    tcn = AC.t_cell(ta12, gnoon, LR["noct"])

    def noon_power(inom_, rmv):
        """The stage's input at bright noon at the nominal hold, the regulation at its lowest (as the check reads it)."""
        return LR["op_point"](dsp, gnoon, tcn, nom_h, lim_of(inom_, rmv, "lo"), LR["rl"])[0]
    p_noon_now = noon_power(i_nom, rm)
    e_now = day(i_nom, rm)
    e_free = (sum(bright(nom_h, None)[0]))
    # ---- what is bounded (the owner's decision process of 2 October 2026, item 1): REQ-016's measurement boundary, its operating
    # conditions and its averaging window, read from the requirement and its verification; TRN-001's port table and the approved
    # test plan for the disturbances. Three checks follow, each with its own result: (a) normal operation, (b) startup, shutdown
    # and the fault response, (c) the parts' ratings during the specified disturbances
    reqs_ = yaml.safe_load(open(os.path.join(TOP, REQS), encoding="utf-8"))["records"]
    q16 = [x_ for x_ in reqs_ if x_.get("id") == "REQ-016"][0]
    st16, ac16 = " ".join(q16["statement"].split()), " ".join(q16["acceptance"].split())
    need(st16, r"the panel held at 17\.6 V by the stage's input regulation, and at most 100 W into the stage\.", "REQ-016 the bound, into the stage")
    need(st16, r"an open-circuit voltage of at most 25 V at the panel's coldest operating temperature", "REQ-016 the panel's window")
    need(ac16, r"Netlist \(board E\): the panel entry \(PV_IN and PV_P\)", "REQ-016 the entry its acceptance names")
    need(ac16, r"a bench supply set to a 100 W panel's curve with its maximum-power point at 17\.6 V and its open-circuit voltage at 25 V charges the pack", "REQ-016 its prototype measurement")
    need(ac16, r"the disturbance, its source impedance or current, its duration and the limit are derived at layer 4 and judged at layer 8 under TRN-001", "REQ-016 the disturbance's assignment")
    if re.search(r"averag|integrat|rms\b|over (?:any|each|every|a) \d", st16 + " " + ac16, re.I) or list(q16["verification_method"]) != ["CALCULATION", "PROTOTYPE_MEASUREMENT"]:
        refuse(3, "REQ-016 now states an averaging basis or another verification; the interpretation below must follow it")
    trn = [x_ for x_ in yaml.safe_load(open(os.path.join(TOP, "v2/ecad/tools/pcb_rules.yaml"), encoding="utf-8"))["rules"] if x_["id"] == "TRN-001"][0]
    need(" ".join(trn["acceptance_criteria"].split()), r"A port table: every external conductor, its working voltage, the threat it is exposed to", "TRN-001 the port table")
    need(open(os.path.join(TOP, "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"), encoding="utf-8").read(),
         r"\| J_SOLAR \| 1: PV_IN \| 2 \| EXTERNAL \| the solar input, a long outdoor lead by definition \|", "DECISION-31 board E's port table, J_SOLAR")
    tp_ = open(os.path.join(TOP, "v2/docs/TEST-PLAN.md"), encoding="utf-8").read()
    for pat_, what_ in ((r"\| M2 \| CS101, conducted susceptibility on the power leads, 30 Hz to 150 kHz \| laboratory \|", "M2"),
                        (r"\| M3 \| CS114, bulk cable injection on the antenna and power cables, 10 kHz to 200 MHz \| laboratory \|", "M3"),
                        (r"\| M7 \| Electrostatic discharge to every touchable surface and every exposed conductor, at decision 34's ruled level, IEC 61000-4-2 level 4: 8 kV contact and 15 kV air", "M7")):
        need(tp_, pat_, "TEST-PLAN.md row " + what_)
    # the panel lead's length: the records give a1solar's 5 m (array_calc.py, ESTIMATE; the panel lead's derivation below reads it);
    # no other document of v2/docs or the registries states a panel lead's length (this record's own folder left out), and one
    # that did would have to be read against it
    lead_hits = []
    for root_, dirs_, files_ in os.walk(os.path.join(TOP, "v2")):
        dirs_[:] = [d_ for d_ in dirs_ if d_ not in ("vendor", "release", "l4e7", ".git", "out")]
        for f_ in files_:
            if f_.endswith((".md", ".yaml")):
                t_ = open(os.path.join(root_, f_), encoding="utf-8", errors="replace").read()
                for m_ in re.finditer(r"(?:solar|panel)\W+(?:lead|cable|extension)", t_, re.I):
                    if re.search(r"\b\d+(?:\.\d+)? ?(?:m|metres?|meters?)\b", t_[max(0, m_.start() - 120):m_.end() + 160]):
                        lead_hits.append(os.path.relpath(os.path.join(root_, f_), TOP))
    if lead_hits:
        refuse(3, "a document now states the panel lead's length (%s); the derivation below must be read against it" % ", ".join(sorted(set(lead_hits))))
    M461 = "v2/vendor/power/held/mil-std-461g-2015-12-11.pdf"
    if sha(M461) != "491f015e386136b58af90e86066533ca073d31210913a766cb236cf05a876bb8":
        refuse(2, "%s is not the pinned file (fetch it: v2/docs/records/l4e7/fetch_held_back.py)" % M461)
    k61, k64, k65, k77 = (flat(pg(M461, n_, False)) for n_ in (61, 64, 65, 77))
    k80 = flat(pg(M461, 80))                         # Table VI read in layout order (its plain text runs down the columns)
    k111, k113 = flat(pg(M461, 111, False)), flat(pg(M461, 113, False))
    need(k61, r"This requirement is applicable from 30 Hz to 150 kHz for equipment and subsystem AC, limited to current draws . 30 amperes per phase, and DC input power leads, not including returns", "461G 5.7.1 CS101 applicability")
    need(k61, r"The requirement is also met when the power source is adjusted to dissipate the power level shown on Figure CS101-2 in a 0\.5 ohm load", "461G 5.7.2 the power limit")
    need(k61, r"e\. Capacitor, 10 [\u03bc\u00b5]F .* g\. Resistor, 0\.5 ohm h\. LISNs", "461G 5.7.3.2 the 10 uF return capacitor and the LISNs")
    c101 = need(k64, r"CURVE #2 Limit Level \(dB.?V\) (\d+) 120 110 106\.5 100 .*?28 VOLTS OR BELOW #2 ([\d.]+) 90", "461G Figure CS101-1, curve 2").groups()
    p101 = need(k65, r"MIL-STD-461G 100 (\d+) Limit level \(Watts\) 10 1 0\.1 ([\d.]+) 0\.01 150k", "461G Figure CS101-2").groups()
    c114 = need(k77, r"Curve 4 = (\d+) dB.A, Curve 3 = (\d+) dB.A", "461G 5.12.2 CS114's induced current at curves 4 and 3").groups()
    g114 = [need(k80, pat_, "461G Table VI, ground, Army").group(1) for pat_ in (r"A 5 5 2 2 2 1 (\d) 3 66 10 kHz to", r"MIL-STD-461G A 5 5 5 2 4 1 (\d) 3 2 MHz to", r"AF 5 3 - - - - 2 3 A 5 5 5 2 2 2 (\d) 3 30 MHz to")]
    need(k111, r"discharging from a 150 picofarads capacitor through a 330 ohm resistor with a circuit inductance not to exceed 5 microhenry", "461G 5.16.2 CS118 the network")
    need(k113, r"Level Test Voltage \(kV\) Method 1 2 3 4 .2 .4 .8 .15 Air Air Contact/Air Air", "461G Table VIII")
    t9 = need(k113, r".8 30 0\.6. tr .1\.0 (\d+) (\d+) 1/Rise time", "461G Table IX the contact current at 30 and 60 ns").groups()
    if g114 != ["3", "4", "4"]:
        refuse(3, "461G Table VI's ground column for the Army is not the one the derivation uses")
    dist = dict(v101=10 ** (float(c101[0]) / 20.0) * 1e-6, v101_150k=10 ** (float(c101[1]) / 20.0) * 1e-6, f_knee=5e3,
                p101=(float(p101[0]), float(p101[1])), i114=10 ** (float(c114[0]) / 20.0) * 1e-6, c114=c114, t9=(float(t9[0]), float(t9[1])),
                esd=(8e3, 15e3), r_esd=330.0, c_esd=150e-12)
    # ---- approach C: a sense bank of identical WSL2512 parts in parallel ahead of everything but R8, R9, TP5 and U18's VIN+ pin;
    # U18 an INA169 (current output into R65 + R66), U19's INB on R66; U19's INA watches TRK_VS; U19's outputs drive U20's MR;
    # U20 a TPS3808G33 on TRK_LDO33 (its own supply is what it watches), CT to VDD through R69 (the fixed delay); U20's RESET holds
    # SWEN low, R70 from TRK_LDO33 and R71 to ground set it when released. Check (a): ONE error budget for the whole chain
    wsl_rows = json.load(open(os.path.join(TOP, INP, "jlc-search-wsl2512-2026-10-01.json"), encoding="utf-8"))["rows"]
    W_AVG = 0.1                # SESSION interpretation of REQ-016's unstated window (the argument is printed), CONDITIONAL for layer 8
    G_CM = 0.01                # SESSION assumption: U18's gain moves at most 1 % between its printed point and V+ = VIN+ = v (break-even printed)
    I_B169 = 1e-3              # SESSION assumption: U18's VIN+ input bias at most 1 mA (10 uA typical, no maximum printed; break-even printed)
    R65 = rvalue("RT0603BRD0716K9L")
    verify_rt("C861156", R65)
    rt_rows = {rvalue(r_["model"]): (r_["code"], r_["stock"]) for r_ in json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-2026-10-01.json"), encoding="utf-8"))["rows"] if rvalue(r_["model"])}

    def rdrift(rp, sgn, aged):
        """A WSL part's factor at the end that moves the trip (sgn -1 lowers R): tolerance, TCR over the larger excursion, and, aged,
        the printed solder-heat and load-life test limits (each (x % + 0.5 mOhm)), Document 30100 pp.2, 3."""
        f = (1 + sgn * 0.01) * (1 + sgn * wtcr * dt_end)
        if aged:
            f *= (1 + sgn * (float(wsold[0]) / 100.0 + float(wsold[1]) / rp)) * (1 + sgn * (float(wlife[0]) / 100.0 + float(wlife[1]) / rp))
        return f

    def rtf(r_, sgn, aged):
        f = (1 + sgn * tol_y) * (1 + sgn * tcr_y * dt_end)
        if aged:
            f *= (1 + sgn * (R["life_y"][0] + R["life_y"][1] / r_)) * (1 + sgn * (R["sold_y"][0] + R["sold_y"][1] / r_))
        return f

    def vs_trip(v, sgn, aged, r66, g_cm=G_CM, parts=False):
        """The sense voltage at which U19 trips at input voltage v (sgn +1 its highest, -1 its lowest), the whole chain at once:
        U19's INB threshold and input current through R66 (full range); U18's transconductance and nonlinearity (printed over
        VSENSE 10 to 150 mV at V+ = 5 V, VIN+ = 12 V, ROUT = 25 kOhm); its offset (at the same point); the move of its output from
        V+ = 5 V and VIN+ = 12 V to v, printed as CMR and PSR at VSENSE = 50 mV, so warranted at 50 mV; the same move at the trip's
        own VSENSE, which no row prints (g_cm x |VSENSE - 50 mV|, the assumption G_CM); and the load R65 + R66 against the 25 kOhm
        of the gain row, through U18's output impedance (1 GOhm typical, a documented dependency on a typical row)."""
        vit_ = vth[1] if sgn > 0 else vth[0]
        gm_ = (gm169[0] if sgn > 0 else gm169[1]) * (1 - sgn * nl169)
        rr = r66 * rtf(r66, -sgn, aged)
        base = (vit_ + sgn * iin_t * rr) / (gm_ * rr)
        rej = 10 ** (-cmr169 / 20.0) * abs(v - 12.0) + psr169 * abs(v - 5.0)
        d1 = g_cm * abs(base + sgn * (vos169 + rej) - 0.050)      # at the corner's own sense voltage, against the rows' 50 mV
        dl = base * abs(R65 * rtf(R65, -sgn, aged) + rr - 25e3) / ro169
        out = base + sgn * (vos169 + rej + d1 + dl)
        return (out, dict(base=base, vos=vos169, rej=rej, d1=d1, dl=dl)) if parts else out

    def i_trip_c(v, rp, n, sgn, aged, r66, g_cm=G_CM):
        return vs_trip(v, sgn, aged, r66, g_cm) / (rp / n * rdrift(rp, -sgn, aged))
    r89_min = (R["r8v"] + R["r9v"]) * (1 - tol_y) * (1 - tcr_y * dt_end) * (1 - R["life_y"][0] - R["life_y"][1] / R["r8v"]) * (1 - R["sold_y"][0] - R["sold_y"][1] / R["r8v"])

    lay_flag = {"ahead": False}

    def pb_c(v, r66, ib=I_B169):
        """What enters the stage without crossing the bank: R8 and R9 (the hold draft's RT parts at their lowest), U18's VIN+ pin
        (its output current, the trip's sense voltage times its highest transconductance, and its input bias, an assumption) and,
        with the bulk ahead of the bank (the CS101 correction), the bulk's DC leakage at its printed maximum."""
        return v * v / r89_min + v * (vs_trip(v, 1, True, r66) * gm169[1] * (1 + nl169) + ib) + (v * 3 * leak_za if lay_flag["ahead"] else 0.0)

    def p_c(rp, n, r66, g_cm=G_CM, ib=I_B169):
        return max(v * i_trip_c(v, rp, n, 1, True, r66, g_cm) + pb_c(v, r66, ib) for v in grid)

    def bisect(f, lo_, hi_):
        for _ in range(60):
            mid = 0.5 * (lo_ + hi_)
            lo_, hi_ = (mid, hi_) if f(mid) else (lo_, mid)
        return lo_
    # the bank: the stocked WSL2512 value and count with the lowest aged trip that still holds the static bound under 100 W at the
    # present divider (R66 8.06k), unchanged from the second round's choice rule; then the setting is chosen against check (b)
    R66_0 = rvalue("RT0603BRD078K06L")
    banks = []
    for r_ in wsl_rows:
        m_ = re.match(r"WSL2512R(\d{4})FEA$", r_["model"])
        if not m_ or r_["stock"] < STOCK_MIN:
            continue
        rp = float("0." + m_.group(1))                    # "R0700" is 0.0700 Ohm
        for n in range(1, 7):
            if p_c(rp, n, R66_0) <= p_win:
                banks.append((min(i_trip_c(v, rp, n, -1, True, R66_0) for v in grid), -n, rp, r_["code"], r_["model"], r_["stock"]))
    if not banks:
        refuse(4, "BLOCKER: no stocked WSL2512 bank puts approach C's static bound under 100 W")
    bank = max(banks)
    nb, rpb, bcode, bmodel = -bank[1], bank[2], bank[3], bank[4]
    lcb = catalogue(bcode)
    if lcb["model"] != bmodel or lcb["params"].get("Tolerance") != "\u00b11%":
        refuse(3, "the bank part's filed reading is not the chosen part")
    rbank = rpb / nb
    # the entry's capacitance at its largest, as the capacitor input energy C x Vmax^2 of one charge (astra-check-l4e7r-2, B2):
    # the 50 V bulk C11, C12, C69 at +20 % and the +30 % endurance change, U18's bypass C66, the four ceramics ahead of RSENSE1
    # (C71 to C74, round 3) and C13 to C15 and C64 behind it, each ceramic at +10 % with no bias derating (the largest it can be)
    c_bulk_max = 3 * za["c"] * (1 + za["tol"]) * (1 + za["end_dc"])
    N_CA = 4                   # SESSION: four 10 uF ceramics on TRK_VS at RSENSE1's pad (check (c) sizes them)
    c_cer_ahead = N_CA * 10e-6
    c_cer_behind = 10e-6 + 10e-6 + 4.7e-6 + 0.1e-6
    c_entry_max = c_bulk_max + (0.1e-6 + c_cer_ahead + c_cer_behind) * 1.10
    e_cap = c_entry_max * v_oc ** 2
    # the source: REQ-016's window bounds the open-circuit voltage (25 V) and the power at the hold (100 W); the current comes from
    # the panel the window was ruled with (the SunPower 100 W of a1solar): its Isc at 1000 W/m2 at the hottest cell temperature the
    # trace uses (70 C) with the sheet's positive power tolerance on top, not the generator's 1.1 x 5.68 A
    i_src = isc_hot * (1 + tol_p)
    p_src = v_oc * i_src
    # the response (typical rows only): U18's settling (5 us, 5 V step at 20 kOhm), U19's INB rising edge (28.1 us at 10 mV
    # overdrive), U20's MR to RESET (150 ns), RESET pulling SWEN through the divider (its RC with SWEN's pin, under 1 us; INFERRED),
    # and one switching period of the LT8705A at its lowest printed frequency after SWEN falls (INFERRED: no SWEN timing row)
    t_resp_typ = ts169 + tpd_lh + mr_ns + 1e-6 + 1.0 / (float(fosc[0]) * 1e3)
    # C70 (round 3): 1 nF across R66, so a discharge's charge through the bank cannot lift U19's INB past its 7 V rating; its delay
    # on the trip is an RC of printed values (the catalogue's 10 % and the X7R class's 15 % over temperature), counted apart
    lc70 = catalogue("C1588")
    if lc70["model"] != "CL10B102KB8NNNC" or lc70["params"].get("Capacitance") != "1nF" or lc70["params"].get("Tolerance") != "\u00b110%" \
            or lc70["params"].get("Temperature Coefficient") != "X7R" or lc70["params"].get("Voltage Rating") != "50V":
        refuse(3, "the filed reading of C1588 is not the 1 nF X7R part C70 names")
    c70 = (1e-9 * 0.90 * 0.85, 1e-9 * 1.10 * 1.15)

    def t_rc(r66):
        """C70's delay on the trip for the event: INB rising toward the source current's level with R66 x C70 at their largest."""
        i_hi = i_trip_c(v_oc, rpb, nb, 1, True, r66)
        return r66 * rtf(r66, 1, True) * c70[1] * math.log(i_src / (i_src - i_hi)) if i_src > i_hi else float("inf")

    def allowance(ps_):
        """Check (b): the longest response for which the energy into the stage over any W_AVG window stays at or under 100 W x W_AVG,
        the stage at the static bound before the event, the source's whole power during the response, and one capacitor charge
        from zero to Vmax after it (a deliberate over-count: the capacitors sit at the hold voltage while the stage runs)."""
        return ((p_win - ps_) * W_AVG - e_cap) / (p_src - ps_)
    # the settings: the present divider and the next stocked values below the trip, each with its static bound, its margin, the
    # regulation coordinated under it, the energy on SC-37's day and the bright day, the noon reduction and check (b)'s allowance
    rm_rows = sorted([(r_[0], r_[1], r_[2]) for r_ in rows_rm] + [(rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in
                     json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-30k-2026-10-01.json"), encoding="utf-8"))["rows"]
                     if rvalue(r_["model"])], key=lambda t: t[0])

    def coordinate(trip_lo):
        for rv_, c_, s_ in rm_rows:
            if s_ >= STOCK_MIN and all(reg_hi(rv_, v) <= trip_lo(v) for v in grid):
                return rv_, c_, s_
        refuse(4, "no stocked RIMON_IN coordinates under the trip")
    settings = []
    for r66_ in sorted(k_ for k_ in rt_rows if 8.0e3 <= k_ <= 8.7e3 and rt_rows[k_][1] >= STOCK_MIN):
        ps_ = p_c(rpb, nb, r66_)
        rcx = coordinate(lambda v, r66_=r66_: i_trip_c(v, rpb, nb, -1, True, r66_))
        settings.append(dict(r66=r66_, code=rt_rows[r66_][0], stock=rt_rows[r66_][1], p_static=ps_, rm=rcx, inom=inom_of(rcx[0]),
                             i_hi25=i_trip_c(v_oc, rpb, nb, 1, True, r66_), i_lo=min(i_trip_c(v, rpb, nb, -1, True, r66_) for v in grid),
                             energy=day(inom_of(rcx[0]), rcx[0]), noon_red=1.0 - noon_power(inom_of(rcx[0]), rcx[0]) / p_noon_now,
                             t_allow=allowance(ps_), t_rc=t_rc(r66_)))
    T_FAC = 10.0                # SESSION: every typical-only timing link at ten times its typical value at once (why ten: the page)
    # ---- THE BACKSTOP UNDER CS101 (checks/check-l4e7r-3.md, the closing check's one defect; the owner's instruction of 2 October
    # 2026): M2's exposure through its own setup, the bank's current over 30 Hz to 150 kHz, the failing case, and the two remedies
    # (a) a filter on U19's INB (a capacitor across R66) and (b) capacitance ahead of the sense bank, then one candidate that holds
    # M2's line, check (b) and check (c) together. M2's line is "no upset of the kit's operation, no reset, no loss of a bearer"
    # (TEST-PLAN.md, REQ-063, characterisation under D-04): a trip stops the stage's switching for td each time, so solar charging
    # stops; that is an upset of the kit's operation (its charging function), not a reset of the kit and not a lost bearer
    need(tp_, r"\| M2 \| CS101, conducted susceptibility on the power leads, 30 Hz to 150 kHz \| laboratory \| no upset of the kit's operation, no reset, no loss of a bearer \|", "TEST-PLAN.md M2's pass line")
    need(flat(pg(M461, 67, False)), r"FIGURE CS101-4\. Signal injection, DC or single phase AC", "461G Figure CS101-4")
    need(flat(pg(M461, 36, False)), r"50 .H To Power Source To EUT 8 .F 0\.25 .F To 50 . Termination Or 50 . Input Of Measurement Receiver 5. 1k . Signal Output Port FIGURE 6\. LISN schematic",
         "461G Figure 6, the LISN (50 uH; 8 uF and 5 Ohm at the source; 0.25 uF and 50 Ohm at the EUT)")
    gm2 = RP.ec_row(pages, 5, "IMON_IN Error Amp EA2 gm", None)["typ"] * 1e-6       # typical only
    a5 = abs(RP.ec_row(pages, 4, "Gain from VC to Maximum Current Sense Voltage", "Buck Mode")["typ"]) * 1e-3   # V/V, typical only
    cmp_ = {k_: e["components"][k_]["value"] for k_ in ("R13", "C21", "C22", "R10", "R11")}
    if (cmp_["R13"], cmp_["C21"], cmp_["C22"]) != ("10k", "4.7n", "100p") or not cmp_["R10"].startswith("115k") or not cmp_["R11"].startswith("10.0k"):
        refuse(3, "board E's VC compensation or FBOUT divider is not the one the loop model reads")
    R5v = float(need(e["components"]["R5"]["value"], r"([\d.]+) mOhm", "R5's value").group(1)) * 1e-3
    v_out = 1.207 * (1 + 115e3 / 10e3)                  # the drawn output setpoint (R10 over R11), the buck's highest duty at the input's least
    c66_ = 0.1e-6 * 1.10
    c_a_max, c_b_max = N_CA * 10e-6 * 1.10, c_cer_behind * 1.10
    c_can_max = za["c"] * (1 + za["tol"]) * (1 + za["end_dc"])

    def loop_t(f_, rm_, vin_):
        """MODELED, typical rows: the IMON_IN loop's gain around R59's current: A7 (1 mA/V, printed at 50 mV) times RSENSE1 into
        RIMON_IN with CIMON_IN, EA2 (gm 185 umho and gain 130 V/V, typical only) into VC (R13, C21, C22), A5 (150 mV/V buck,
        typical) over R5 to the inductor, times the duty VOUT/VIN to the input. A documented dependency on typical rows."""
        w_ = 2 * math.pi * f_
        z_im = rm_ / (1 + 1j * w_ * rm_ * 100e-9)
        z_vc = 1.0 / (gm2 / ea2 + 1j * w_ * 100e-12 + 1.0 / (10e3 + 1.0 / (1j * w_ * 4.7e-9)))
        return a7["(All Grades)"]["typ"] * 1e-3 * rs * z_im * gm2 * z_vc * (a5 / R5v) * min(1.0, v_out / vin_)

    def y_behind(f_, layout, rm_, i_, vin_, ls_=1.0):
        """The stage's input admittance seen through the bank (S): the capacitors behind it at their largest (the bulk at its 20 C
        ESR, the ceramics with none), and R59's branch: C13 to C15 and C64 with the converter, whose input, with VC fixed, draws
        constant power (dI/dV = -I/V, INFERRED from the buck's duty VOUT/VIN), all inside the IMON_IN loop, which holds R59's
        current: that branch is divided by (1 + T)."""
        w_ = 2 * math.pi * f_
        y_ = 1j * w_ * (c_a_max + c66_) + ls_ * (1j * w_ * c_b_max - i_ / vin_) / (1 + loop_t(f_, rm_, vin_))
        if layout == "behind":
            y_ += 3.0 / (za["esr"] + 1.0 / (1j * w_ * c_can_max))
        return y_

    def z_ret(f_, zps):
        """Figure CS101-4's return path for the injected loop: the 10 uF across the leads, in parallel with the two LISNs (50 uH
        each, 461G Figure 6; their EUT-side 0.25 uF and 50 Ohm to the ground plane, in series pairs) and the power source between
        their source sides (zps; each LISN's 8 uF and 5 Ohm to the plane, in series pairs, across it)."""
        w_ = 2 * math.pi * f_
        z_src = 1.0 / (1.0 / zps + 1.0 / (10.0 + 1.0 / (1j * w_ * 4e-6))) if zps else (10.0 + 1.0 / (1j * w_ * 4e-6))
        z_lisn = 2 * 1j * w_ * 50e-6 + z_src
        z_meas = 100.0 + 1.0 / (1j * w_ * 0.125e-6)
        return 1.0 / (1j * w_ * 10e-6 + 1.0 / z_lisn + 1.0 / z_meas)

    def v101(f_):
        return dist["v101"] if f_ <= dist["f_knee"] else dist["v101"] * (dist["v101_150k"] / dist["v101"]) ** (math.log(f_ / dist["f_knee"]) / math.log(150e3 / dist["f_knee"]))

    def p101(f_):
        return dist["p101"][0] if f_ <= dist["f_knee"] else dist["p101"][0] * (dist["p101"][1] / dist["p101"][0]) ** (math.log(f_ / dist["f_knee"]) / math.log(150e3 / dist["f_knee"]))

    def cs101(f_, layout, rm_, i_, vin_, c_ahead=0.0, ls_=1.0):
        """The bank's current, peak, at frequency f_: (S1) the voltage limit across the EUT's input (the test's controlled
        quantity, whatever the source); (S2) Figure CS101-4 as drawn, the source an ideal EMF set to the calibrated power into
        0.5 Ohm, the loop closed through z_ret with the power source stiff and with it absent, the EUT's input voltage capped at
        the voltage limit. c_ahead: capacitance on PV_P ahead of the bank (remedy b; the bulk when it is ahead)."""
        w_ = 2 * math.pi * f_
        yb = y_behind(f_, layout, rm_, i_, vin_, ls_)
        z_b = rbank + 1.0 / yb
        y_a = (3.0 / (za["esr"] + 1.0 / (1j * w_ * c_can_max)) if layout == "ahead" else 0.0) + (1j * w_ * c_ahead if c_ahead else 0.0)
        z_eut = 1.0 / (1.0 / z_b + y_a) if y_a else z_b
        s1 = v101(f_) * math.sqrt(2) / abs(z_b)
        e_ = math.sqrt(p101(f_) * 0.5)
        v2 = max(min(v101(f_), e_ * abs(z_eut / (z_eut + z_ret(f_, zp_)))) for zp_ in (1e-3, None))
        return s1, v2 * math.sqrt(2) / abs(z_b)
    freqs = [30.0 * (150e3 / 30.0) ** (k_ / 120.0) for k_ in range(121)]
    v_ops = (lo_h, v_oc)                                 # the operating input voltage's ends in regulation (the hold's least to 25 V)

    def worst_ripple(layout, rm_, tau_, c_ahead=0.0):
        """The filtered peak over every frequency and both setups, against the operating points (the regulation at its highest)."""
        out = []
        for f_ in freqs:
            h_ = 1.0 / abs(1 + 1j * 2 * math.pi * f_ * tau_)
            r_ = max(max(cs101(f_, layout, rm_, max(reg_hi(rm_, v_) for v_ in v_ops), v_, c_ahead)) for v_ in v_ops)
            out.append((f_, r_, r_ * h_))
        return out

    def margin_of(r66_, rm_):
        return min(i_trip_c(v, rpb, nb, -1, True, r66_) - reg_hi(rm_, v) for v in grid)
    # the C0G part the filter is made of, and its tolerances (the catalogue's 5 %; C0G's 0 +-30 ppm/K, the class definition)
    lcf = catalogue("C170182")
    if lcf["model"] != "1206N104J500CT" or lcf["params"].get("Capacitance") != "100nF" or lcf["params"].get("Tolerance") != "\u00b15%" \
            or lcf["params"].get("Voltage Rating") != "50V":
        refuse(3, "the filed reading of C170182 is not the 100 nF NP0 part the filter names")
    CF_TOL, CF_TC = 0.05, 30e-6

    def taus(r66_, n_cf):
        """(the least, the largest) time constant of R66 with n_cf of the 100 nF C0G parts (and C70's 1 nF when n_cf = 0)."""
        c_n = n_cf * 100e-9 if n_cf else 1e-9
        lo_ = r66_ * rtf(r66_, -1, True) * c_n * ((1 - CF_TOL) * (1 - CF_TC * dt_end) if n_cf else 0.90 * 0.85)
        hi_ = r66_ * rtf(r66_, 1, True) * c_n * ((1 + CF_TOL) * (1 + CF_TC * dt_end) if n_cf else 1.10 * 1.15)
        return lo_, hi_
    leak_za = max(float(need(z1, r"DC leakage current I < (0\.01) CV or (3) \(.A\)", "ZA p.1 DC leakage").group(1)) * za["c"] * 1e6 * za["v"], 3.0) * 1e-6
    rm_cands = [t_ for t_ in rm_rows if 29.0e3 <= t_[0] <= 36.0e3 and t_[2] >= STOCK_MIN]
    spectra = {(lay_, t_[0]): [(f_, max(max(cs101(f_, lay_, t_[0], max(reg_hi(t_[0], v_) for v_ in v_ops), v_)) for v_ in v_ops)) for f_ in freqs]
               for lay_ in ("behind", "ahead") for t_ in rm_cands}
    e_cache = {}

    def energy_of(rm_):
        if rm_ not in e_cache:
            e_cache[rm_] = (day(inom_of(rm_), rm_), 1.0 - noon_power(inom_of(rm_), rm_) / p_noon_now)
        return e_cache[rm_]

    def evaluate(lay_, r66_, rmt, n_cf):
        """One candidate: its margin, the filtered CS101 ripple over both setups and every frequency, check (b) with the filter's
        excess (at most the trip's highest current times the largest time constant, whatever the waveform: a first-order filter
        holds at most tau x I_trip of charge above the trip before it crosses), and the two assumptions past their meaning."""
        rm_ = rmt[0]
        t_lo, t_hi = taus(r66_, n_cf)
        m_ = margin_of(r66_, rm_)
        rip = [(f_, r_, r_ / abs(1 + 1j * 2 * math.pi * f_ * t_lo)) for f_, r_ in spectra[(lay_, rm_)]]
        worst_f = max(rip, key=lambda x_: x_[2])
        ps_ = p_c(rpb, nb, r66_) + (v_oc * 3 * leak_za if lay_ == "ahead" else 0.0)
        ih_ = i_trip_c(v_oc, rpb, nb, 1, True, r66_)
        e_f = v_oc * ih_ * t_hi
        t_al = ((p_win - ps_) * W_AVG - e_cap - e_f) / (p_src - ps_)
        room_ = p_win - (e_cap + e_f + (p_src - ps_) * T_FAC * t_resp_typ) / W_AVG
        return dict(layout=lay_, r66=r66_, rm=rmt, n_cf=n_cf, tau=(t_lo, t_hi), m=m_, rip=rip, worst=worst_f, p_static=ps_, i_hi=ih_,
                    e_f=e_f, t_allow=t_al, room=room_, immune=m_ > 0 and worst_f[2] <= m_,
                    protect=t_al >= T_FAC * t_resp_typ and p_c(rpb, nb, r66_, g_cm=1.0) <= room_ - (ps_ - p_c(rpb, nb, r66_))
                    and p_c(rpb, nb, r66_, ib=ipin169) <= room_ - (ps_ - p_c(rpb, nb, r66_)))
    r66_cands = sorted(k_ for k_ in rt_rows if 8.0e3 <= k_ <= 9.1e3 and rt_rows[k_][1] >= STOCK_MIN)
    cands = []
    for lay_ in ("behind", "ahead"):
        for r66_ in r66_cands:
            for rmt in rm_cands:
                if margin_of(r66_, rmt[0]) <= 0:
                    continue
                for n_cf in range(0, 7):
                    x_ = evaluate(lay_, r66_, rmt, n_cf)
                    if x_["immune"] and x_["protect"]:
                        x_["energy"], x_["noon_red"] = energy_of(rmt[0])
                        cands.append(x_)
    if not cands:
        refuse(4, "BLOCKER: no candidate holds M2's line, check (b) and the assumptions together")
    # the choice (SESSION): the most energy on SC-37's day at the nominal hold and on the bright day; among those the filter's size
    # costs no energy but trades two quantities no row bounds against each other: the room for the IMON_IN loop's branch in the
    # immunity (its model uses typical rows) and the room for the response in check (b) (its delays are typical rows, here as the
    # allowance over ten times their sum). The choice takes the largest of the smaller of the two; then the fewest parts added
    top_e = max((round(x_["energy"][1][2], 6), round(x_["energy"][3][2], 6)) for x_ in cands)
    top = [x_ for x_ in cands if (round(x_["energy"][1][2], 6), round(x_["energy"][3][2], 6)) == top_e]

    def loop_room(x_):
        i_x = max(reg_hi(x_["rm"][0], v_) for v_ in v_ops)

        def fm(ls_):
            return max(max(max(cs101(f_, x_["layout"], x_["rm"][0], i_x, v_, 0.0, ls_)) for v_ in v_ops) / abs(1 + 1j * 2 * math.pi * f_ * x_["tau"][0])
                       for f_ in freqs)
        return bisect(lambda s_: fm(s_) <= x_["m"], 1.0, 50.0)
    for x_ in top:
        x_["loop_be"] = loop_room(x_)
    for x_ in top:
        x_["resp_room"] = x_["t_allow"] / (T_FAC * t_resp_typ)
    best = max(top, key=lambda x_: (round(min(x_["loop_be"], x_["resp_room"]), 3), -x_["n_cf"], x_["layout"] == "behind", x_["m"]))
    LAYOUT, N_CF = best["layout"], best["n_cf"]
    # the failing case (round 3's circuit as committed at 237cd9be) and the two remedies alone, on the same exposure
    fail = evaluate("behind", rvalue("RT0603BRD078K25L"), [t_ for t_ in rm_cands if t_[0] == 30000.0][0], 0)
    rem_a = [x_ for x_ in (evaluate("behind", fail["r66"], fail["rm"], n_) for n_ in range(0, 9)) if x_["t_allow"] >= T_FAC * t_resp_typ][-1]
    rem_b = evaluate("ahead", fail["r66"], fail["rm"], 0)
    C_AHEAD_DEMO = 2.2e-3                              # remedy (b) taken far: 2.2 mF added on PV_P, ten times the entry's own
    i_reg_f = max(reg_hi(30000.0, v_) for v_ in v_ops)
    rem_b_add = [(f_, cs101(f_, "behind", 30000.0, i_reg_f, lo_h), cs101(f_, "behind", 30000.0, i_reg_f, lo_h, C_AHEAD_DEMO)) for f_ in freqs]
    # the table, frequency by frequency, for the failing case, each remedy alone and the selection; each setup apart
    def rows_of(x_):
        i_r = max(reg_hi(x_["rm"][0], v_) for v_ in v_ops)
        out = []
        for f_ in freqs:
            s12 = [cs101(f_, x_["layout"], x_["rm"][0], i_r, v_) for v_ in v_ops]
            s1, s2 = max(s_[0] for s_ in s12), max(s_[1] for s_ in s12)
            h_ = 1.0 / abs(1 + 1j * 2 * math.pi * f_ * x_["tau"][0])
            out.append((f_, s1, s2, max(s1, s2) * h_, max(s1, s2) * h_ <= x_["m"]))
        return out
    tab = {k_: rows_of(x_) for k_, x_ in (("fail", fail), ("rem_a", rem_a), ("rem_b", rem_b), ("best", best))}
    # how far the converter's loop branch (typical rows) may exceed the model before the selection's margin is spent
    loop_be = best["loop_be"]
    # the coordinator's starting estimate (check-l4e7r-3.md: a corner near 180 Hz, about 0.2 ms to cross on a full step), tested on
    # round 3's circuit: the margin it used was the trip's highest less the regulation's; the trip acts at the trip's LOWEST
    tau180 = 1.0 / (2 * math.pi * 180.0)
    est = dict(tau=tau180, r30=spectra[("behind", 30000.0)][0][1] / abs(1 + 1j * 2 * math.pi * 30.0 * tau180),
               worst=max(r_ / abs(1 + 1j * 2 * math.pi * f_ * tau180) for f_, r_ in spectra[("behind", 30000.0)]),
               t_cross=tau180 * math.log((i_src - max(reg_hi(30000.0, v_) for v_ in grid)) / (i_src - fail["i_hi"])),
               m_hi=fail["i_hi"] - max(reg_hi(30000.0, v_) for v_ in grid))
    # the protection response with the filter, two ways: the held charge (above) and the step's crossing times at the largest tau
    i_rh = max(reg_hi(best["rm"][0], v_) for v_ in grid)
    t_step0 = best["tau"][1] * math.log(i_src / (i_src - best["i_hi"]))
    t_stepr = best["tau"][1] * math.log((i_src - i_rh) / (i_src - best["i_hi"]))
    R["cs101"] = dict(best=best, fail=fail, rem_a=rem_a, rem_b=rem_b, n_cands=len(cands), top_e=top_e, top=[(x_["layout"], x_["r66"], x_["rm"][0], x_["n_cf"], x_["loop_be"], x_["t_allow"], x_["resp_room"]) for x_ in top], rem_b_add=rem_b_add, freqs=freqs, tab=tab,
                      loop_be=loop_be, t_step0=t_step0, t_stepr=t_stepr, i_rh=i_rh, leak=3 * leak_za, gm2=gm2, a5=a5, r5=R5v, v_out=v_out,
                      c_ahead_demo=C_AHEAD_DEMO, e_best=energy_of(best["rm"][0]), e_fail=energy_of(30000.0), est=est)
    # the decision on the setting (SESSION, the owner's process of 2 October: a margin justified by what it must absorb, never a
    # percentage). Check (b) spends the static headroom on the capacitor charge and the response; what is left must carry the two
    # static assumptions past their physical meaning. The setting chosen is the one with the least energy cost for which (i) the
    # response allowance covers the response chain's typical sum with every typical-only link at ten times its typical value at
    # once (T_FAC, why ten on the page) plus C70's printed delay, and (ii) with that response spent, U18's unprinted gain move
    # would have to reach its whole gain (break-even at or over 100 %) and its VIN+ bias the pin's 10 mA absolute maximum (a
    # stress the maker calls damaging: a fault, not an operating value) before the bound reached 100 W

    def room(r66_):
        ps_ = p_c(rpb, nb, r66_)
        return p_win - (e_cap + (p_src - ps_) * (T_FAC * t_resp_typ + t_rc(r66_))) / W_AVG
    for s_ in settings:
        s_["vs_hi"], s_["vs_parts"] = vs_trip(v_oc, 1, True, s_["r66"], parts=True)
        rm_ = room(s_["r66"])
        s_["g_cm_be"] = bisect(lambda g_, r66_=s_["r66"]: p_c(rpb, nb, r66_, g_cm=g_) <= rm_, 0.0, 5.0)
        s_["i_b_be"] = bisect(lambda ib_, r66_=s_["r66"]: p_c(rpb, nb, r66_, ib=ib_) <= rm_, 0.0, 1.0)
        s_["ok"] = (s_["p_static"] <= p_win and s_["t_allow"] >= T_FAC * t_resp_typ + s_["t_rc"] and s_["g_cm_be"] >= 1.0 and s_["i_b_be"] >= ipin169)
    # round 3's table stops there (C70 only, the regulation at its least coordinated value); the CS101 correction's choice
    # (best, above) adds M2's immunity and may lower the regulation, so the setting is taken from it
    chosen = dict(r66=best["r66"], code=rt_rows[best["r66"]][0], rm=tuple(best["rm"]), energy=best["energy"], noon_red=best["noon_red"],
                  t_allow=best["t_allow"], ok=True)
    lay_flag["ahead"] = LAYOUT == "ahead"
    R66 = chosen["r66"]
    verify_rt(chosen["code"], R66)
    c = dict(rp=rpb, n=nb, rbank=rbank, code=bcode, model=bmodel, stock=lcb["stock"], r66=R66, r66_code=chosen["code"], settings=settings,
             t_fac=T_FAC, g_cm=G_CM, i_b=I_B169, layout=LAYOUT, n_cf=N_CF, tau=best["tau"], e_f=best["e_f"], m_cs=best["m"], leak=3 * leak_za)
    c["p_static"] = p_c(rpb, nb, R66)
    c["v_hi"] = max(grid, key=lambda v: v * i_trip_c(v, rpb, nb, 1, True, R66) + pb_c(v, R66))
    c["i_hi25"] = i_trip_c(v_oc, rpb, nb, 1, True, R66)
    c["i_lo_new"] = min(i_trip_c(v, rpb, nb, -1, False, R66) for v in grid)
    c["i_lo_aged"] = min(i_trip_c(v, rpb, nb, -1, True, R66) for v in grid)
    c["vs_hi"], c["vs_lo"] = vs_trip(v_oc, 1, True, R66), vs_trip(v_oc, -1, True, R66)
    c["vs_parts"] = vs_trip(v_oc, 1, True, R66, parts=True)[1]
    c["vs_nom"] = vth_typ / (1e-3 * R66)
    c["pb25"] = pb_c(v_oc, R66)
    c["r_load"] = (R65 + R66, R65 * rtf(R65, -1, True) + R66 * rtf(R66, -1, True), R65 * rtf(R65, 1, True) + R66 * rtf(R66, 1, True))
    # the error budget at the static bound's point (v = 25 V, aged): the trip current as the nominal chain times each term's factor
    i_nom_c = c["vs_nom"] / rbank
    i_100 = (p_win - c["pb25"]) / v_oc                                   # the trip current at which 25 V reaches 100 W
    c["budget"] = dict(i_nom=i_nom_c, i_100=i_100, e_tol=i_100 / i_nom_c - 1.0, e_sup=c["i_hi25"] / i_nom_c - 1.0,
                       e_bank=1.0 / rdrift(rpb, -1, True) - 1.0, p_margin=p_win - c["p_static"])
    c["budget"]["e_margin"] = c["budget"]["e_tol"] - c["budget"]["e_sup"]
    # the break-evens of the two assumptions: each alone, the other at its stated value, until the static bound reaches 100 W
    c["g_cm_be"] = bisect(lambda g_: p_c(rpb, nb, R66, g_cm=g_) <= p_win, 0.0, 5.0)
    c["i_b_be"] = bisect(lambda ib_: p_c(rpb, nb, R66, ib=ib_) <= p_win, 0.0, 1.0)
    # the same with check (b)'s capacitor charge and ten typical responses also taken from the headroom
    p_dyn_room = p_win - (e_cap + c["e_f"] + (p_src - c["p_static"]) * T_FAC * t_resp_typ) / W_AVG
    c["g_cm_be_b"] = bisect(lambda g_: p_c(rpb, nb, R66, g_cm=g_) <= p_dyn_room, 0.0, 5.0)
    c["i_b_be_b"] = bisect(lambda ib_: p_c(rpb, nb, R66, ib=ib_) <= p_dyn_room, 0.0, 1.0)
    c["vout_hi"] = c["vs_hi"] * gm169[1] * (1 + nl169) * c["r_load"][2]
    # check (b): startup, shutdown and the fault response, each with its own figure
    c.update(e_cap=e_cap, c_entry_max=c_entry_max, c_bulk_max=c_bulk_max, n_ca=N_CA, i_src=i_src, p_src=p_src, t_resp_typ=t_resp_typ,
             t_allow=((p_win - c["p_static"]) * W_AVG - e_cap - c["e_f"]) / (p_src - c["p_static"]), c70=c70)
    c["e_window_typ"] = c["p_static"] * W_AVG + c["e_f"] + (p_src - c["p_static"]) * t_resp_typ + e_cap
    # repeated source steps with SWEN low: the capacitors take energy again only after giving it up; with SWEN low they lose it to
    # the quiescent loads (bounded below) or back into the panel when its voltage falls under theirs (that energy leaves the stage);
    # each full swing between the hold's lowest and 25 V dissipates at most C x dV^2 inside, so the count the headroom allows:
    r_s_max = rbank * rdrift(rpb, 1, True) + za["esr_cold"] / 3.0
    dv_sw = v_oc - lo_h
    c["cycle_e"] = c_entry_max * dv_sw ** 2
    c["cycle_be"] = ((p_win - c["p_static"]) * W_AVG - e_cap - c["e_f"] - (p_src - c["p_static"]) * T_FAC * t_resp_typ) / c["cycle_e"]
    c["r_s_max"] = r_s_max
    # the startup window: the capacitors charge when the panel connects; U20 holds SWEN low for td after TRK_LDO33 is valid
    # (td at least 180 ms, longer than W_AVG), so no window holds both that charge and switching
    c["e_start"] = e_cap + v_oc * (iq169 + 2e-3) * W_AVG
    c["td_min"] = td_min
    c["coord"] = chosen["rm"]
    # what T_FAC stands on: the largest maximum-to-typical ratio of a timing row these parts print (TPS3808's td with CT to VDD,
    # the LT8705A's oscillator at RT 215k), so ten times typical is several times beyond any printed spread of the chain's makers
    c["t_spread"] = max(float(td38[2]) / float(td38[1]), float(fosc[1]) / float(fosc[0]))
    # the 0.1 s basis against the parts the bound protects: what the allowance admits at the source's current puts into one bank
    # part and into RSENSE1, against what their continuous ratings (1 W at 70 C; 3 W) carry in one window
    c["e_part_allow"] = (i_src / nb) ** 2 * rpb * rdrift(rpb, 1, True) * c["t_allow"]
    c["e_r59_allow"] = i_src ** 2 * rs * (1 + tol_h) * c["t_allow"]
    # ---- approach C's coordination: the smallest stocked RIMON_IN whose regulation, at its highest under the joint assumptions,
    # stays at or under C's lowest aged trip at every input voltage (the chosen setting's row above)
    rc_ = chosen["rm"]
    verify_rt(rc_[1], rc_[0])
    c["rm"], c["inom"] = rc_, inom_of(rc_[0])
    c["reg_hi25"] = reg_hi(rc_[0], v_oc)
    c["energy"] = chosen["energy"]
    c["noon_red"] = chosen["noon_red"]
    c["cur_red"] = 1.0 - c["inom"] / i_nom
    # the check's bright-day figures, reproduced by this model (astra-check-l4e7r-1, D3: 26.1k 495.3165 Wh, 28.7k 465.6367 Wh)
    c["check_repro"] = [(rv_, sum(bright(nom_h, lim_of(inom_of(rv_), rv_, "lo"))[0]), 1.0 - noon_power(inom_of(rv_), rv_) / p_noon_now) for rv_ in (26100.0, 28700.0)]
    c["exposed"] = [(h, BRIGHT[h], bright(nom_h, None)[0][h]) for h in range(24) if BRIGHT[h] > 0.0
                    and dsp.current(nom_h, BRIGHT[h], AC.t_cell(ta12, BRIGHT[h], LR["noct"]), LR["rl"]) > i_trip_c(nom_h, rpb, nb, -1, True, R66)]
    c["pk_day"] = max(dsp.current(vh, LR["prof0"][h], AC.t_cell(LR["TA40"][h], LR["prof0"][h], LR["noct"]), LR["rl"])
                      for vh in (lo_h, nom_h, hi_h) for h in range(24) if LR["prof0"][h] > 0)
    c["trip_lo_hold"] = min(i_trip_c(vh, rpb, nb, -1, True, R66) for vh in (lo_h, nom_h, hi_h))
    # the bank's conduction at the selected regulation's own currents (the minor of astra-check-l4e7r-2): the hourly input power of
    # the trace with the chosen regulation at its lowest (the energy rows' basis), at the nominal hold, through the bank's nominal
    lim_c = lim_of(c["inom"], rc_[0], "lo")
    c["loss"] = (sum((p_ / nom_h) ** 2 * rbank for p_ in energy(nom_h, lim_c)[0]), sum((p_ / nom_h) ** 2 * rbank for p_ in bright(nom_h, lim_c)[0]))
    c["p_bank_max"] = (c["i_hi25"] / nb) ** 2 * rpb * (1 + 0.01)          # one part at the highest trip current, W (its P70 is 1 W)
    # L4-E9's figures this round sets (its power-path output at fnd/l4e9 539dc57c, read only; the excerpt filed under inputs/)
    x9 = json.load(open(os.path.join(TOP, INP, "l4e9-power-path-539dc57c-excerpt.json"), encoding="utf-8"))
    if x9["commit"] != "539dc57cd7d1b989c6181862d4cfeb1b91ca407d" or x9["blob_sha256"] != "9b0c1e7029495ca93d5ef3abd4648d84978ccfc13584a0080002296ee7534652":
        refuse(3, "the L4-E9 excerpt is not the one read at 539dc57c")
    l9 = x9["lines"]
    for k_, pat_ in (("86", r"L4-E7: limit 3\.4713 A; 25 V corner 96\.2474 W \(stack A\), 99\.8992 W"), ("97", r"panel hot short circuit about 6\.42 A"),
                     ("99", r"D4 one-way clamp \(its 45\.4 V clamping against the 35 V bulk"), ("109", r"input limit 3\.4713 A \(L4-E7\)"),
                     ("113", r"99\.8992 <= 100 W; CONDITIONAL"), ("119", r"at the window 93 W out, at H3's lowest settle point \(22\.06 V\) 4\.216 A"),
                     ("307", r"L4-E7's settings, 350 Wh a day")):
        need(l9[k_], pat_, "L4-E9's line %s" % k_)
    c["l4e9"] = dict(lines=l9, reg_hi_hold=max(reg_hi(rc_[0], vh) for vh in (lo_h, nom_h, hi_h)), p_hold_hi=max(vh * reg_hi(rc_[0], vh) for vh in (lo_h, nom_h, hi_h)),
                     p_hold_nom=nom_h * c["inom"], p_reg25=v_oc * c["reg_hi25"])
    # ---- approach B, reclassed (the INA250 with the same trip chain and entry): every row at its printed value; the rows printed at
    # another condition, or typical only, are CONDITIONAL and named, with the gain error they may add before the bound reaches 100 W
    r60b, r61b = rvalue("RT0603BRD0728KL"), rvalue("RT0603BRD077K87L")
    for code, val in (("C705756", r60b), ("C861565", r61b)):
        verify_rt(code, val)

    def i_err_b(v):
        return ios + dios * dt_end + abs(v - 12.0) * 10 ** (-cmr / 20.0) / rsh_n + psr * (5.0 - v_ldo[0])

    def trip_b(v, sgn, aged, extra=0.0):
        def kk(s_t, s_b):
            def f(s_, r_):
                d = ((1 + s_ * (R["life_y"][0] + R["life_y"][1] / r_)) * (1 + s_ * (R["sold_y"][0] + R["sold_y"][1] / r_))) if aged else 1.0
                return (1 + s_ * tol_y) * (1 + s_ * tcr_y * dt_end) * d
            return r61b * f(s_b, r61b) / (r60b * f(s_t, r60b) + r61b * f(s_b, r61b))
        rth = r60b * r61b / (r60b + r61b)
        if sgn > 0:
            k_ = min(kk(a, b) for a in (-1, 1) for b in (-1, 1))
            return (vth[1] + iin_t * rth) / (k_ * g_ina * (1 - eg - extra)) + i_err_b(v)
        k_ = max(kk(a, b) for a in (-1, 1) for b in (-1, 1))
        return (vth[0] - iin_t * rth) / (k_ * g_ina * (1 + eg + extra)) - i_err_b(v)

    def pb_b(v):
        return v * v / r89_min + v * ib_ina
    b = dict(p_static=max(v * trip_b(v, 1, True) + pb_b(v) for v in grid))
    lo_, hi_ = 0.0, 0.2
    for _ in range(60):
        mid = 0.5 * (lo_ + hi_)
        if max(v * trip_b(v, 1, True, mid) + pb_b(v) for v in grid) + e_cap / W_AVG > p_win:
            hi_ = mid
        else:
            lo_ = mid
    b["gain_be"] = lo_                                     # the unprinted gain terms together may reach this before 100 W
    b["typ_gain"] = stress_sh + nl + ro / (r60b + r61b)    # what the typical-only rows print, for scale
    rb_ = coordinate(lambda v: trip_b(v, -1, True))
    verify_rt(rb_[1], rb_[0])
    b["rm"], b["inom"] = rb_, inom_of(rb_[0])
    b["energy"] = day(b["inom"], rb_[0])
    b["noon_red"], b["cur_red"] = 1.0 - noon_power(b["inom"], rb_[0]) / p_noon_now, 1.0 - b["inom"] / i_nom
    r_ina = 4.5e-3                                         # p.5, the package path, IN+ to IN-, the shunt included (typical)
    lim_b = lim_of(b["inom"], rb_[0], "lo")
    b["loss"] = (sum((p_ / nom_h) ** 2 * r_ina for p_ in energy(nom_h, lim_b)[0]), sum((p_ / nom_h) ** 2 * r_ina for p_ in bright(nom_h, lim_b)[0]))
    b["abs"] = abs_ina
    b["conditional"] = [
        "the system gain error and the offset at VS = 3.23 to 3.35 V and VREF = 0 V (both printed at VS = 5 V and VREF = 2.5 V, p.5)",
        "the common-mode rejection away from zero current (printed at ISENSE = 0 A, p.5)",
        "the integrated shunt's change after reflow, thermal cycling and life (typical only, %.3f %% summed; note 6 of p.6 excludes them from the gain error)" % (100 * stress_sh),
        "the nonlinearity (typical only, %.2f %%) and the output impedance (typical only, %.1f Ohm)" % (100 * nl, ro),
        "U18's VIN+ bias across temperature (%.0f uA printed at 25 C only)" % (ib_ina * 1e6),
    ]
    # ---- approach A: the present control with argued margins (unchanged method; its fault comparator's action has no printed timing)
    v_f = iovm["max"] * (1 + LINE_FLOOR_MUL * line_p * 1e-2 * (v_oc - V_LINE_REF))
    rs_lo_c = rfac(tol_h, TCR_COLD_CONS, abs(t_cold - 25.0), life_h, sold_h)
    need_rm = v_oc * v_f / (p_win * gm_lo * 1e-3 * rs * rs_lo_c)
    a30 = json.load(open(os.path.join(TOP, INP, "jlc-search-rt0603brd07-30k-2026-10-01.json"), encoding="utf-8"))["rows"]
    rm_a = None
    for rv_, c_, s_ in sorted((rvalue(r_["model"]), r_["code"], r_["stock"]) for r_ in a30 if rvalue(r_["model"]) and r_["stock"] >= STOCK_MIN):
        rm_lo_c = rfac(tol_y, tcr_y, abs(t_cold - 25.0), R["life_y"][0] + R["life_y"][1] / rv_, R["sold_y"][0] + R["sold_y"][1] / rv_)
        if v_oc * v_f / (gm_lo * 1e-3 * rs * rs_lo_c * rv_ * rm_lo_c) <= p_win:
            rm_a = (rv_, c_, s_, v_oc * v_f / (gm_lo * 1e-3 * rs * rs_lo_c * rv_ * rm_lo_c))
            break
    if rm_a is None:
        refuse(4, "no stocked RIMON_IN holds approach (a)'s argued bound")
    a_ = dict(v_f=v_f, need=need_rm, rm=rm_a, inom=vref_n / (1e-3 * rs * rm_a[0]), bound=rm_a[3])
    a_["energy"] = day(a_["inom"], rm_a[0])
    a_["noon_red"], a_["cur_red"] = 1.0 - noon_power(a_["inom"], rm_a[0]) / p_noon_now, 1.0 - a_["inom"] / i_nom
    # ---- approach C's supply sequencing (B3 of the checks), SWEN default off on printed rows: R71 holds SWEN to ground and R70
    # feeds it from TRK_LDO33 only, so SWEN is at most k_hi x TRK_LDO33 (plus what the pin itself might source, which no row
    # bounds: its break-even below); k_hi puts SWEN's least rising threshold above every TRK_LDO33 at which a sensing part is out
    # of its supply range; above that, U20's RESET (specified there) holds SWEN at its VOL until td after TRK_LDO33 passes VIT
    R70, R71, R67, R68, R69 = (rvalue("RT0603BRD07%sL" % x_) for x_ in ("8K06", "6K04", "110K", "9K53", "100K"))
    for code, val in (("C861587", R70), ("C728595", R71), ("C326736", R67), ("C705800", R68), ("C122538", R69)):
        verify_rt(code, val)
    swen_h = RP.ec_row(pages, 4, "SWEN Threshold Voltage Hysteresis (Note 5)", None)
    k_hi = R71 * rtf(R71, 1, True) / (R70 * rtf(R70, -1, True) + R71 * rtf(R71, 1, True))
    k_lo = R71 * rtf(R71, -1, True) / (R70 * rtf(R70, 1, True) + R71 * rtf(R71, -1, True))
    r_th = max(R70 * rtf(R70, s_, True) * R71 * rtf(R71, s_, True) / (R70 * rtf(R70, s_, True) + R71 * rtf(R71, s_, True)) for s_ in (-1, 1))
    vdd_sense = max(vdd_t, vdd38)                       # TPS3701 1.8 V, TPS3808 1.7 V: above it every sensing part is in range
    seq = dict(vit_lo=vit38 * (1 - acc38), vit_hi=vit38 * (1 + acc38), rel_hi=vit38 * (1 + acc38) * (1 + hys38), ldo_lo=v_ldo[0],
               vdd38=vdd38, vdd_t=vdd_t, vdd_sense=vdd_sense, td_min=td_min, vol38=vol38, rmr=rmr38, ioh=ioh38, k_hi=k_hi, k_lo=k_lo,
               r_th=r_th, swen=(swen_r["min"], swen_r["max"]), swen_hys=swen_h["typ"] * 1e-3 if swen_h["typ"] > 0.5 else swen_h["typ"])
    seq["guard_v"] = swen_r["min"] / k_hi               # SWEN cannot reach its least rising threshold below this TRK_LDO33
    seq["i_sw_be"] = (swen_r["min"] - k_hi * vdd_sense) / r_th          # a SWEN source current that could enable it at 1.8 V
    seq["i_sw_be_dead"] = swen_r["min"] / (R71 * rtf(R71, 1, True))     # the same with TRK_LDO33 floating (R71 alone)
    seq["sw_hi_min"] = k_lo * v_ldo[0]                  # SWEN released, at LDO33's least, against the highest rising threshold
    seq["i_sink_be"] = (seq["sw_hi_min"] - swen_r["max"]) / r_th        # a SWEN sink current that would keep the stage off (availability)
    seq["i_reset"] = v_ldo[1] / (R70 * rtf(R70, -1, True)) + seq["i_sw_be"]   # RESET's sink current, with the break-even pin current
    seq["hys_be"] = swen_r["min"] - vol38               # the hysteresis SWEN would need before RESET's VOL could fail to disable it
    # TRK_LDO33's load from the arrangement, at most, against the 5 mA its regulation row is printed at (8705af p.3)
    idd_t = float(need(t5, r"IDD Supply current VDD = 1\.8 V . 36 V \d+ (\d+) [\u00b5\u03bc]A", "TPS3701 p.5 IDD").group(1)) * 1e-6
    idd38 = float(need(s6, r"VDD = 3\.3V, RESET not asserted [\d.]+ (\d+) MR, RESET, CT open", "TPS3808 p.6 IDD at 3.3 V").group(1)) * 1e-6
    seq["i_ldo"] = idd_t + idd38 + v_ldo[1] / (R70 * rtf(R70, -1, True) + R71 * rtf(R71, -1, True)) + v_ldo[1] / rmr38 + v_ldo[1] / (R69 * rtf(R69, -1, True))
    seq["uv_ts_lo"] = vtha[0] * (1 + R67 * rtf(R67, -1, True) / (R68 * rtf(R68, 1, True)))
    seq["uv_ts_hi"] = vtha[1] * (1 + R67 * rtf(R67, 1, True) / (R68 * rtf(R68, -1, True)))
    seq["intvcc_uv"] = uvi
    seq["mr_vil"] = 0.3 * vdd_sense                     # U20's MR low threshold at the lowest sensed supply (0.3 VDD)
    if not (seq["guard_v"] > vdd_sense and seq["sw_hi_min"] > swen_r["max"] and seq["rel_hi"] < seq["ldo_lo"] and seq["i_ldo"] < 5e-3
            and seq["i_reset"] <= 1e-3 and vol38 < swen_r["min"] - seq["swen_hys"] and vol_max < seq["mr_vil"] and td_min > W_AVG
            and c["vout_hi"] < min(seq["uv_ts_lo"] - sw169, seq["uv_ts_lo"] - swcm169) and seq["uv_ts_lo"] > 2.7 and td_min > st_t):
        refuse(4, "approach C's supply sequencing does not hold on the printed rows")
    # ---- check (c): the parts' ratings during the specified disturbances (B6 of the checks). The panel lead is EXTERNAL in
    # TRN-001's port table (DECISION-31, a long outdoor lead); the records give a 5 m lead (a1solar), and the approved test plan's
    # levels for power leads do not depend on its length: M2 CS101 (461G curve 2, the voltage at the input; the
    # power limit with Figure CS101-4's 10 uF return capacitor), M3 CS114 (Table VI, ground, Army: curves 3 and 4) and M7 the
    # discharge at decision 34's level through 461G CS118's network; and, labelled apart, a capability scenario: D4's own
    # 10/1000 us rating, derated at the hot end, the entry's margin beyond the panel lead's derived surge (THE PANEL LEAD'S
    # DISTURBANCES, below: MIL-STD-461G CS116 and CS115, the row REQ-063 commits to, and the sustained sources). The stage's operating
    # current is superposed at the trip's highest (the most it carries in normal operation); the corrected network adds four
    # 10 uF ceramics on TRK_VS at RSENSE1's pad (C71 to C74), no part in series with CSPIN or CSNIN (8705af p.30)
    need(raw[30], r"all four of the current sense pins can draw bias current under normal operating conditions\. As such, do not place resistors in series with any of the CSxIN or CSxOUT pins", "8705af p.30 no series resistor at CSPIN or CSNIN")
    l4 = flat(pg(SMC, 4, False))
    need(l4, r"Figure 3 - Peak Pulse Power Derating Curve .*Peak Pulse Power \(PPP\) or Current \(IPP\) Derating in Percentage % 100 80 60 40 20 0 0 25 50 75 100 125 150 TJ - Initial Junction Temperature", "SMCJ p.4 Figure 3, the pulse derating curve")
    d4_der = 1.0 - 0.40 * (t_air - 25.0) / 125.0      # Figure 3 read as drawn: 100 % to 25 C, then a straight line to 60 % at 150 C (INFERRED from the figure)
    za_end_esr = float(need(z1, r"tan d < 200 % of the initial limit E\. S\. R\. < (\d+) % of the initial limit Endurance", "ZA p.1 ESR after endurance").group(1)) / 100.0
    zfl = pg(ZA, 2)
    zband = [(float(a_) * (1e3 if ua_ == "kHz" else 1.0), float(b_) * (1e3 if ub_ == "kHz" else 1.0))
             for a_, ua_, b_, ub_ in re.findall(r"(\d+) (Hz|kHz) < f < (\d+) (Hz|kHz)", zfl)]
    zfac = [float(x_) for row_ in re.findall(r"C < 47 .F\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", zfl) for x_ in row_]
    if len(zband) != 15 or len(zfac) != 16 or zband[0] != (100.0, 200.0) or zband[-1] != (100e3, 500e3):
        refuse(3, "ZA p.2's ripple frequency table is not the one read")
    def zripple(f_):
        for (a_, b_), k_ in zip(zband, zfac):
            if a_ <= f_ < b_:
                return za["ripple"] * k_
        return za["ripple"] * (zfac[0] if f_ < 100.0 else zfac[-1])
    ESR_CER = 0.010            # SESSION assumption: a 10 uF 50 V X7R ceramic's ESR at the events' frequencies at most 10 mOhm (no maker part chosen)
    r59_hi = rs * rfac(tol_h, TCR_COLD_CONS, dt_max, life_h, sold_h, sgn=1)
    rb_hi = rbank * rdrift(rpb, 1, True)
    i_op = c["i_hi25"]
    rd4 = (d4["vc"] - d4["vbr"][1]) / d4["ipp"]

    rb_lo = rbank * rdrift(rpb, -1, True)

    def entry_event(i_s, t_end, dt, esr_b, cb, n_ca, k_ca, lay=None, v0=None, iop=None):
        """MODELED: the entry as lumped parts with a disturbance current i_s(t) injected at PV_P on top of the operating current
        i_op (drawn from TRK_VIN, crossing the bank and RSENSE1): the bulk (esr_b, cb) on TRK_VS behind the bank or, with the
        CS101 correction, on PV_P ahead of it (the bank then at its least, which sends more current on toward R59), n_ca ceramics
        ahead of RSENSE1 (each at ESR_CER, at their least, -10 % times the bias factor k_ca), D4 at TRK_VS (off below its highest
        breakdown, 34.4 V, then the straight line to 45.4 V at 33.1 A), RSENSE1 at its highest to TRK_VIN with C13 to C15 and C64
        behind it (C13 and C14 the same 10 uF part and bias as the ceramics ahead, so the same factor; C15 and C64 at +10 % with
        none; no ESR behind, which sends more current through RSENSE1). The conservative direction is stated for every choice.
        v0 and iop (the panel lead's derivation): the start voltage and the operating current, by default the hold and i_op."""
        lay = lay or LAYOUT
        v0_ = nom_h if v0 is None else v0
        io_ = i_op if iop is None else iop
        ca = n_ca * 10e-6 * 0.9 * k_ca
        ra = ESR_CER / n_ca
        cc = (20e-6 * k_ca + 4.7e-6 + 0.1e-6) * 1.10
        pk = dict(d59=-1.0, d59n=1.0, id4=0.0, v=0.0, vp=0.0, ib=0.0, ibank=0.0, e_part=0.0, e_d4=0.0)
        fp_ = rdrift(rpb, 1, True)
        if lay == "behind":
            vb = va = v0_
            vcc = v0_ - io_ * r59_hi
            g_ = 1.0 / esr_b + 1.0 / ra + 1.0 / r59_hi
        else:
            vb = v0_
            va = v0_ - io_ * rb_lo
            vcc = va - io_ * r59_hi
            kk = esr_b / (esr_b + rb_lo)
            g_ = 1.0 / ra + 1.0 / r59_hi + kk / esr_b
        for k_ in range(int(t_end / dt)):
            iin = io_ + i_s(k_ * dt)
            if lay == "behind":
                j_ = iin + vb / esr_b + va / ra + vcc / r59_hi
            else:
                j_ = kk * iin + kk * vb / esr_b + va / ra + vcc / r59_hi
            v_ = j_ / g_
            if v_ > d4["vbr"][1]:
                v_ = (j_ + d4["vbr"][1] / rd4) / (g_ + 1.0 / rd4)
            if lay == "behind":
                ibk, vp_ = iin, v_
                ib_ = (v_ - vb) / esr_b
            else:
                ibk = kk * (iin + (vb - v_) / esr_b)
                vp_ = v_ + ibk * rb_lo
                ib_ = iin - ibk
            i59 = (v_ - vcc) / r59_hi
            vb += ib_ / cb * dt
            va += (v_ - va) / ra / ca * dt
            vcc += (i59 - io_) / cc * dt
            pk["d59"], pk["d59n"] = max(pk["d59"], i59 * r59_hi), min(pk["d59n"], i59 * r59_hi)
            pk["id4"] = max(pk["id4"], max(0.0, (v_ - d4["vbr"][1]) / rd4))
            pk["e_d4"] += v_ * max(0.0, (v_ - d4["vbr"][1]) / rd4) * dt
            pk["v"], pk["vp"], pk["ib"], pk["ibank"] = max(pk["v"], v_), max(pk["vp"], vp_), max(pk["ib"], abs(ib_)), max(pk["ibank"], abs(ibk))
            pk["e_part"] += (ibk / nb) ** 2 * rpb * fp_ * dt
        return pk
    t1s, t2s = 3.4e-6, 1.44e-3                         # the 10/1000 us shape as a double exponential (INFERRED shape)
    f_s = lambda t: math.exp(-t / t2s) - math.exp(-t / t1s)
    f_n = max(f_s(k_ * 1e-7) for k_ in range(2000))
    bulks = dict(cold_aged=(za["esr_cold"] / 3.0, 3 * za["c"] * (1 - za["tol"]) * (1 - za["end_dc"])),
                 new_20=(za["esr"] / 3.0, 3 * za["c"] * (1 - za["tol"])),
                 aged_20=(za["esr"] * za_end_esr / 3.0, 3 * za["c"] * (1 - za["tol"]) * (1 - za["end_dc"])))
    cases = []
    for lab_, amp_, bk_ in (("capability, cold end (D4 at its full rating, the bulk aged, -40 C row)", d4["ipp"], "cold_aged"),
                            ("capability, hot end (D4 derated to %.1f %% at %.1f C, the bulk new)" % (100 * d4_der, t_air), d4["ipp"] * d4_der, "new_20"),
                            ("capability, hot end (D4 derated, the bulk aged)", d4["ipp"] * d4_der, "aged_20")):
        for k_ in (1.0, 0.5, 0.25):
            pk_ = entry_event(lambda t, a_=amp_: a_ * f_s(t) / f_n, 250e-6, 10e-9, bulks[bk_][0], bulks[bk_][1], N_CA, k_)
            pk_["e_part"] = sum((i_op + amp_ * f_s(k2 * 1e-6) / f_n) ** 2 / nb ** 2 * rpb * rdrift(rpb, 1, True) * 1e-6 for k2 in range(4000))
            cases.append(dict(kind="capability", lab=lab_, amp=amp_, bulk=bk_, k=k_, **pk_))
    tau_esd = dist["r_esd"] * dist["c_esd"]
    esd_k = 1.0 + 0.30                                 # Table IX's +30 % on the currents at 30 and 60 ns
    for kv_ in dist["esd"]:
        for bk_ in ("cold_aged", "new_20"):
            for k_ in (1.0, 0.5, 0.25):
                pk_ = entry_event(lambda t, kv_=kv_: esd_k * kv_ / dist["r_esd"] * math.exp(-t / tau_esd), 1.5e-6, 0.5e-9, bulks[bk_][0], bulks[bk_][1], N_CA, k_)
                cases.append(dict(kind="M7", lab="discharge %.0f kV (%s)" % (kv_ / 1e3, "contact" if kv_ < 1e4 else "air, scaled from the contact waveform"), amp=esd_k * kv_ / dist["r_esd"], bulk=bk_, k=k_, **pk_))
    # the same network with two ceramics instead of four (the count's justification) and with none (the second round's network)
    alt_ca = {n_: max(entry_event(lambda t: esd_k * dist["esd"][1] / dist["r_esd"] * math.exp(-t / tau_esd), 1.5e-6, 0.5e-9, bulks[bk_][0], bulks[bk_][1], n_, k_)["d59"]
                      for bk_ in ("cold_aged", "new_20") for k_ in (1.0, 0.25)) for n_ in (2,)}
    # M2, CS101, as phasors over 30 Hz to 150 kHz, for the parts' ratings (the backstop's immunity is the CS101 block above): the
    # voltage at the input at curve 2 (S1, the bound) and Figure CS101-4 as drawn (S2); the bank's current from the same model
    # (the converter inside its IMON_IN loop, typical rows); D4 off (25 V + the peak stays under its 28 V stand-off)
    i_reg_c = max(reg_hi(rc_[0], v_) for v_ in v_ops)

    def v_eut_s2(f_, lay_, vin_):
        w_ = 2 * math.pi * f_
        z_b_ = rbank + 1.0 / y_behind(f_, lay_, rc_[0], i_reg_c, vin_)
        y_a_ = 3.0 / (za["esr"] + 1.0 / (1j * w_ * c_can_max)) if lay_ == "ahead" else 0.0
        z_eut_ = 1.0 / (1.0 / z_b_ + y_a_) if y_a_ else z_b_
        return max(min(v101(f_), math.sqrt(p101(f_) * 0.5) * abs(z_eut_ / (z_eut_ + z_ret(f_, zp_)))) for zp_ in (1e-3, None))
    rows101 = []
    for f_ in freqs:
        w_ = 2 * math.pi * f_
        z_can = za["esr"] + 1.0 / (1j * w_ * c_can_max)
        bank_ = max(cs101(f_, LAYOUT, rc_[0], i_reg_c, v_)[0] for v_ in v_ops) / math.sqrt(2)          # rms, S1
        bank2_ = max(cs101(f_, LAYOUT, rc_[0], i_reg_c, v_)[1] for v_ in v_ops) / math.sqrt(2)         # rms, S2
        i59_ = max(v101(f_) * abs((1j * w_ * c_b_max - i_reg_c / v_) / (1 + loop_t(f_, rc_[0], v_))) for v_ in v_ops)
        rows101.append(dict(f=f_, v=v101(f_), i_bound=bank_, i_drawn=bank2_, can_bound=v101(f_) / abs(z_can),
                            can_drawn=max(v_eut_s2(f_, LAYOUT, v_) for v_ in v_ops) / abs(z_can), i59=i59_, rip=zripple(f_)))
    w101 = max(rows101, key=lambda r_: r_["can_bound"] / r_["rip"])
    c101_ = dict(rows=rows101, worst=w101, d59=(i_op + math.sqrt(2) * max(r_["i59"] for r_ in rows101)) * r59_hi,
                 bank=(i_op + math.sqrt(2) * max(r_["i_bound"] for r_ in rows101)) * rb_hi,
                 part_w=max((i_op ** 2 + r_["i_bound"] ** 2) / nb ** 2 * rpb * rdrift(rpb, 1, True) for r_ in rows101),
                 v_pk=v_oc + math.sqrt(2) * dist["v101"], ratio_bound=max(r_["can_bound"] / r_["rip"] for r_ in rows101),
                 ratio_drawn=max(r_["can_drawn"] / r_["rip"] for r_ in rows101), trip_drawn=max(r_["i_drawn"] for r_ in rows101 if r_["f"] >= 1e3))
    # M3, CS114: the induced current on the lead at most curve 4's (103 dBuA, the larger of Table VI's ground Army curves), all of it
    # taken as differential through the entry (lumped; its parasitics at MHz are not modeled)
    c114_ = dict(i=math.sqrt(2) * dist["i114"], d59=(i_op + math.sqrt(2) * dist["i114"]) * r59_hi, bank=(i_op + math.sqrt(2) * dist["i114"]) * rb_hi)
    worst = max(cases, key=lambda x_: x_["d59"])
    k_inb = rb_hi * gm169[1] * (1 + nl169) * R66 * rtf(R66, 1, True)      # INB per ampere through the bank, steady (C70 charged)
    worst_app = max([x_ for x_ in cases if x_["kind"] == "M7"], key=lambda x_: x_["d59"])
    tin_abs = float(need(flat(pg(TPS, 4)), r"VINA, VINB .0\.3 \+(\d+)", "TPS3701 p.4 INA and INB absolute maximum").group(1))
    vds028 = float(need(flat(pg(BSC028, 1, False)), r"VDS (\d+) V RDS\(on\),max", "BSC028N06NS p.1 VDS").group(1))
    rating_hi = dict(csd=csd_abs, d169=abs169[1], cm169=abs169[0], vs169=vsabs169, za_v=za["v"], cer_v=50.0, vin=vin_abs, fb=fb_abs,
                     tps_in=tin_abs, q3=vds028)
    v_pk = max(x_["v"] for x_ in cases)
    i_pk = max(x_["ibank"] for x_ in cases)
    v_pvp = max(x_["v"] + x_["ibank"] * rb_hi for x_ in cases)
    v_bulk = v_pvp if LAYOUT == "ahead" else v_pk
    c_inb_min = taus(R66, N_CF)[0] / (R66 * rtf(R66, -1, True))       # the INB node's least capacitance (the filter, or C70)
    surge = dict(cases=cases, worst=worst, worst_app=worst_app, alt_ca=alt_ca, c101=c101_, c114=c114_, d4_der=d4_der, r59_hi=r59_hi, rb_hi=rb_hi,
                 i_op=i_op, esr_cer=ESR_CER, n_ca=N_CA, v_pk=v_pk, i_pk=i_pk, d169=i_pk * rb_hi, v_pvp=v_pvp, v_bulk=v_bulk, c_inb_min=c_inb_min,
                 v_fbin=v_pvp * R["r9v"] / (R["r8v"] + R["r9v"]), v_shdn=v_pk * r15_ / (r14_ + r15_),
                 v_inb=max(max(x_["ibank"] for x_ in cases if x_["kind"] == "capability") * k_inb,
                           i_op * k_inb + gm169[1] * (1 + nl169) * rb_hi * esd_k * max(dist["esd"]) * dist["c_esd"] / c_inb_min),
                 v_ina=v_pk * R68 / (R67 + R68),
                 e_part=max(x_["e_part"] for x_ in cases), ib_can=max(x_["ib"] for x_ in cases) / 3.0, rating=rating_hi,
                 d59_margin=csd_abs - worst["d59"], i_extra_be=(csd_abs - worst["d59"]) / r59_hi, dist=dist)
    surge["d59_op"] = i_op * r59_hi
    surge["v_inb_esd_add"] = gm169[1] * (1 + nl169) * rb_hi * esd_k * max(dist["esd"]) * dist["c_esd"] / c_inb_min
    over = [n_ for n_, bad_ in (("U5 sense differential", worst["d59"] > csd_abs), ("U5 negative differential", -min(x_["d59n"] for x_ in cases) > csd_abs),
                                ("U5 under CS101", c101_["d59"] > csd_abs), ("U18 differential", surge["d169"] > abs169[1]),
                                ("U18 common mode and supply", surge["v_pvp"] > min(abs169[0], vsabs169)), ("the bulk", v_bulk > za["v"]),
                                ("the ceramics", v_pk > 50.0), ("U19 INB", surge["v_inb"] > tin_abs), ("U19 INA", surge["v_ina"] > tin_abs),
                                ("D4", max(x_["id4"] for x_ in cases if x_["kind"] == "capability") > d4["ipp"]), ("a bank part under CS101", c101_["part_w"] > 1.0),
                                ("D4's stand-off under CS101", c101_["v_pk"] > d4["vr"]), ("U5's margin under its operating drop", surge["d59_margin"] < surge["d59_op"])) if bad_]
    if over:
        refuse(4, "at the derived disturbance: %s (U5 %.4f V, CS101 %.4f V, U18 %.3f V, %.2f V peak)" % (", ".join(over), worst["d59"], c101_["d59"], surge["d169"], v_pk))
    # ---- THE PANEL LEAD'S DISTURBANCES, DERIVED (the coordinator's surge round of 2 October 2026; the findings ledger's item 1,
    # L4-E7R's checks 1.6 and 2.4; L4-E9's register row R-156). REQ-016's acceptance gives layer 4 the derivation (the disturbance,
    # its source impedance or current, its duration and the limit) and layer 8 the judgement under TRN-001, and states the pass
    # criterion: D4's clamping voltage at the disturbance's current, with the part's tolerance, at or below the lowest limit on PV_P
    need(ac16, r"Surge and sustained over-voltage on the panel lead: no level is ruled \(DECISION-31 section 3; D-16 for the vehicle entry\), so the "
         r"disturbance, its source impedance or current, its duration and the limit are derived at layer 4 and judged at layer 8 under TRN-001", "REQ-016 the surge's assignment")
    need(ac16, r"It passes for a disturbance only when D4's clamping voltage at that disturbance's current \(from its source impedance, waveform and "
         r"duration, with the part's tolerance\) is at or below the lowest limit on PV_P, the capacitors' 35 V\.", "REQ-016 the pass criterion")
    # (1) the exposure: J_SOLAR is EXTERNAL (TRN-001's port table, read above); the lead is the one the records give, a1solar's
    # array record, through the replay's own loop resistance; the return is board E's GND and no board has a chassis net
    AC_ = LR["AC"]
    acs_ = open(os.path.join(TOP, "v2/docs/records/a1solar/array_calc.py"), encoding="utf-8").read()
    need(acs_, r"LEAD_M = 5\.0 +# ESTIMATE: array combiner to the case's wall connector, one way", "array_calc.py the lead's length (ESTIMATE)")
    need(acs_, r"LEAD_MM2 = 4\.0 +# ESTIMATE: 4 mm2 \(12 AWG class, the size the Renogy and SunPower leads use\)", "array_calc.py the lead's section (ESTIMATE)")
    if (AC_.LEAD_M, AC_.LEAD_MM2) != (5.0, 4.0) or abs(AC_.lead_r() - LR["rl"]) > 1e-12:
        refuse(3, "the lead the replay uses is not a1solar's 5 m of 4 mm2")
    gnd_ = flat(open(os.path.join(TOP, "v2/docs/GROUNDING-AND-SHIELDS.md"), encoding="utf-8").read())
    need(gnd_, r"The enclosure is a \*\*Peli 1450, which is plastic\*\*", "GROUNDING-AND-SHIELDS.md the plastic case")
    need(gnd_, r"There is no chassis net anywhere in this kit", "GROUNDING-AND-SHIELDS.md no chassis net")
    need(flat(open(os.path.join(TOP, "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"), encoding="utf-8").read()),
         r"The return is the board's ground directly \(J_SOLAR\.2 is GND, not GND_V\)", "DECISION-31 J_SOLAR's return")
    C0 = 299792458.0
    lead = dict(m=AC_.LEAD_M, mm2=AC_.LEAD_MM2, r=AC_.lead_r(), f_q=C0 / (4.0 * AC_.LEAD_M), f_h=C0 / (2.0 * AC_.LEAD_M))
    # (2) the basis: REQ-063 commits the kit's EMC characterisation to MIL-STD-461G's 'Ground, Army' row of Table V (transcribed in
    # v2/vendor/standards/, the same file as the held copy); that row marks CS115 and CS116 applicable to every interconnecting
    # cable, CS116 to each individual high side power lead, and CS117 (lightning induced) for the procuring activity to specify;
    # the plan runs M1 to M5 and no row of it runs CS115, CS116 or CS117
    q63 = [x_ for x_ in reqs_ if x_.get("id") == "REQ-063"][0]
    need(" ".join(q63["acceptance"].split()), r"Each of TEST-PLAN M1 to M5 is run against the limit MIL-STD-461G \(11 December 2015\) gives for the "
         r"'Ground, Army' installation of its Table V", "REQ-063 the edition and the installation row")
    mx_ = open(os.path.join(TOP, "v2/vendor/standards/mil-std-461g-requirement-matrix.md"), encoding="utf-8").read()
    need(mx_, r"sha256 of the file read \| `491f015e386136b58af90e86066533ca073d31210913a766cb236cf05a876bb8`", "the Table V transcription's file")
    hdr_ = need(mx_, r"\n\| Installation \|([^\n]+)\|\n", "Table V's header").group(1)
    row_ = need(mx_, r"\n\| Ground, Army \|([^\n]+)\|\n", "Table V's Ground, Army row").group(1)
    tv = dict(zip([h_.strip() for h_ in hdr_.split("|")], [c_.strip() for c_ in row_.split("|")]))
    if [tv.get(k_) for k_ in ("CS101", "CS114", "CS115", "CS116", "CS117")] != ["A", "A", "A", "A", "S"]:
        refuse(3, "Table V's Ground, Army row is not the one the derivation reads")
    if re.search(r"CS11[5-7]", tp_):
        refuse(3, "TEST-PLAN.md now names CS115, CS116 or CS117; the derivation below must use its row")
    # IEC 61000-4-5 is not held (no file of v2/vendor names it) and the envelope's surge row and CHO-003 decline it for the long leads
    if any("61000-4-5" in f_ or "61000_4_5" in f_ for _r, _d, fs_ in os.walk(os.path.join(TOP, "v2/vendor")) for f_ in fs_):
        refuse(3, "an IEC 61000-4-5 file is now held under v2/vendor; the basis below must be re-chosen against it")
    need(open(os.path.join(TOP, "v2/docs/OPERATING-ENVELOPE.md"), encoding="utf-8").read(), r"\| Surge on the conductors that leave the case on a long "
         r"lead \(shore and vehicle DC, PoE\) \| what the fitted part survives.*Asking instead for an IEC 61000-4-5 installation level is a ruling", "OPERATING-ENVELOPE.md the surge row")
    need(" ".join([x_ for x_ in reqs_ if x_.get("id") == "CHO-003"][0]["statement"].split()), r"Surge on long-lead conductors is described by the "
         r"fitted part \(SMCJ40A, 1500 W at 10/1000 us\), not constrained to an IEC 61000-4-5 level\.", "CHO-003")
    k86, k87, k88, k91, k92, k94, k95, k98, k249, k255 = (flat(pg(M461, n_, False)) for n_ in (86, 87, 88, 91, 92, 94, 95, 98, 249, 255))
    need(k86, r"This requirement is applicable to all aircraft, space, and ground system interconnecting cables, including power cables\.", "461G 5.13.1 CS115 applicability")
    need(k86, r"rise and fall times, pulse width, and amplitude as specified on Figure CS115-1 at a 30 Hz rate for one minute", "461G 5.13.2 CS115 limit")
    need(k86, r"a\. Pulse generator, 50 ohm, charged line \(coaxial\)", "461G 5.13.3.2 CS115 generator")
    need(k87, r"Adjust the pulse generator, as a minimum, for the amplitude setting", "461G 5.13.3.4c(2)(a)")
    need(k87, r"Record the peak current induced in the cable as indicated on the oscilloscope", "461G 5.13.3.4c(2)(e)")
    need(k88, r"30 ns\. \(Minimum\) 5 90% Limit Level \(Amps\) 4 REPETITION RATE = 30Hz 3 2 1 10% 0 .2 .2 Nanoseconds FIGURE CS115-1", "461G Figure CS115-1")
    need(k249, r"The 5 ampere amplitude \(500 V across 100 ohm loop impedance calibration fixture\)", "461G A.5.13 the 5 A amplitude")
    need(k91, r"This requirement is applicable from 10 kHz to 100 MHz for all interconnecting cables, including power cables, and individual "
         r"high side power leads\.", "461G 5.14.1 CS116 applicability")
    need(k91, r"Compliance shall be demonstrated at the following frequencies: 0\.01, 0\.1, 1, 10, 30, and 100 MHz\. If there are other frequencies "
         r"known to be critical to the equipment installation, such as platform resonances, compliance shall also be demonstrated at those frequencies\.", "461G 5.14.2 the frequencies")
    need(k91, r"The test signal repetition rate shall be no greater than one pulse per second and no less than one pulse every two seconds\. The "
         r"pulses shall be applied for a period of five minutes\.", "461G 5.14.2 the repetition")
    need(k91, r"a\. Damped sinusoid transient generator, . 100 ohm output impedance", "461G 5.14.3.2 CS116 generator (at most 100 ohm)")
    need(k92, r"Reduce the signal, if necessary, to produce the required current\.", "461G 5.14.3.4c(3)")
    need(k94, r"Normalized waveform: e -\( f t\)/Q sin\(2.ft\) Where: f = Frequency \(Hz\) t = Time \(sec\) Q = Damping factor, 15 .5", "461G Figure CS116-1")
    need(k95, r"Peak current \(Amperes\) 100 10 1 0\.1 0\.01 0\.1 1 10 100 Frequency \(MHz\) FIGURE CS116-2\. CS116 limit for all applications\.", "461G Figure CS116-2's axes")
    need(k98, r"This requirement is applicable to all safety-critical equipment interconnecting cables", "461G 5.15.1 CS117 applicability")
    need(k255, r"These levels and waveforms were derived from general and civil aviation experience and are considered applicable to military "
         r"aircraft equipment and subsystems\.", "461G A.5.15 CS117's origin")
    need(k255, r"However, for most equipment, testing with some combination of CS116 and CS115 may provide sufficient coverage to address the "
         r"environment for nearby lightning called out in MIL-STD-464\.", "461G A.5.15 nearby lightning")

    def ip116(f_):
        """Figure CS116-2 as drawn (INFERRED from the figure: its curve is a drawing, the text layer holds the axes only): 0.1 A at
        10 kHz rising 20 dB a decade to 10 A at 1 MHz, flat to 30 MHz, falling 20 dB a decade to 3 A at 100 MHz."""
        return 10.0 * min(1.0, f_ / 1e6) if f_ <= 30e6 else 10.0 * 30e6 / f_
    Q116 = (10.0, 20.0)                                # Figure CS116-1's Q, 15 +- 5, both ends
    f116 = sorted({1e4, 1e5, 1e6, 1e7, 3e7, 1e8, lead["f_q"]})
    A115, T115, E115 = 5.0, 30e-9, 2e-9                # Figure CS115-1: 5 A, 30 ns at least, edges at most 2 ns
    # the sustained source a mistaken connection puts on the port: the kit's own declared vehicle and shore range (V2-SPEC line 21)
    v_src = float(need(open(os.path.join(TOP, "v2/docs/V2-SPEC.md"), encoding="utf-8").read(), r"\| Inputs \| 9 to (\d+) V filtered vehicle and shore input",
                       "V2-SPEC line 21 the kit's source range").group(1))
    # the clamp's other rows (SMCJ p.1, the series' rows p.2)
    aT = float(need(l1, r"VBR @ TJ= VBR@25.C x \(1\+.T x \(TJ - 25\)\) \(.T:Temperature Coefficient, typical value is ([\d.]+)%\)", "SMCJ p.1 VBR's coefficient (typical)").group(1)) / 100.0
    pd4 = float(need(l1, r"Power Dissipation on Infinite Heat Sink at TL=50OC PD ([\d.]+) W", "SMCJ p.1 PD").group(1))
    tjmax = float(need(l1, r"Operating Temperature Range TJ -65 to (\d+) .C", "SMCJ p.1 the junction's range").group(1))
    rja = float(need(l1, r"Junction to Ambient R.JA (\d+) .C/W", "SMCJ p.1 RthJA (typical)").group(1))
    need(l1, r"Typical failure mode is short from over-specified voltage or current", "SMCJ p.1 the failure mode (typical)")
    smcj = {int(m_.group(1)): dict(vr=float(m_.group(2)), vbr=(float(m_.group(3)), float(m_.group(4))), vc=float(m_.group(5)), ipp=float(m_.group(6)))
            for m_ in re.finditer(r"SMCJ(\d+)A SMCJ\1CA \w+ \w+ (\d+\.\d) (\d+\.\d+) (\d+\.\d+) 1 (\d+\.\d) (\d+\.\d) \d+ X", l2)}
    if smcj.get(28) != dict(vr=d4["vr"], vbr=d4["vbr"], vc=d4["vc"], ipp=d4["ipp"]) or 36 not in smcj:
        refuse(3, "SMCJ p.2's rows are not the ones read")
    lim_drawn = float(need(gse, r'for k in range\(1, 3\): part\("C%d" % \(10 \+ k\), "Device", "C_Polarized", "100u (\d+)V Panasonic EEHZK1V101XP', "gen_sch_e.py C11 and C12 as drawn").group(1))
    lim_draft = min(za["v"], 50.0)                     # the drafted entry: the bulk on PV_P and C71 to C74 on TRK_VS

    def clamp(row_, i_, tj_):
        """INFERRED: the straight line from the highest part's breakdown (1 mA) to the printed clamping point, the breakdown moved by
        the sheet's typical coefficient at the junction temperature tj_ (the part's tolerance: the highest part; its temperature)."""
        return row_["vbr"][1] * (1 + aT * (tj_ - 25.0)) + (row_["vc"] - row_["vbr"][1]) / row_["ipp"] * i_

    def be_clamp(row_, lim_, tj_):
        """The current at which clamp() reaches lim_."""
        return (lim_ - row_["vbr"][1] * (1 + aT * (tj_ - 25.0))) / ((row_["vc"] - row_["vbr"][1]) / row_["ipp"])
    vbr_cold = d4["vbr"][0] * (1 + aT * (t_cold - 25.0))
    # the loaded network (MODELED, lumped, the corrected entry of check (c)): each start, bulk and bias, both polarities
    starts = (("operating at the hold, the trip's highest current", None, None), ("open circuit at the cold end, the stage off", v_oc, 0.0))

    def run_set(wave_, t_end, dt):
        out_ = []
        for lab_, v0_, io_ in starts:
            for bk_ in ("cold_aged", "new_20"):
                for k_ in (1.0, 0.25):
                    out_.append(dict(start=lab_, bulk=bk_, k=k_, **entry_event(wave_, t_end, dt, bulks[bk_][0], bulks[bk_][1], N_CA, k_, v0=v0_, iop=io_)))
        return out_

    def agg(runs_):
        return dict(d59=max(r_["d59"] for r_ in runs_), d59n=min(r_["d59n"] for r_ in runs_), v=max(r_["v"] for r_ in runs_),
                    vp=max(r_["vp"] for r_ in runs_), ibank=max(r_["ibank"] for r_ in runs_), id4=max(r_["id4"] for r_ in runs_),
                    e_d4=max(r_["e_d4"] for r_ in runs_))
    # D4's energy rating at its 10/1000 us row (VC x IPP over the shape's integral, INFERRED), scaled for a shorter event by the square
    # root of its duration (INFERRED: adiabatic heating of the junction), against a bound with the whole current in D4
    e_rating = d4["vc"] * d4["ipp"] * (t2s - t1s) / f_n
    r116 = []
    for f_ in f116:
        ip_ = ip116(f_)
        row116 = dict(f=f_, ip=ip_, d59_b=(i_op + ip_) * r59_hi, d169_b=(i_op + ip_) * rb_hi, vc25=clamp(d4, ip_, 25.0), vch=clamp(d4, ip_, t_air),
                      q_half=ip_ / (math.pi * f_), e_b=clamp(d4, ip_, t_air) * ip_ * max(Q116) / (math.pi * f_),
                      y_trip=2.0 * ip_ / (math.pi * f_) / best["tau"][0], lumped=f_ <= 1e6)
        row116["e_cap"] = e_rating * math.sqrt(min(1.0, max(Q116) / (math.pi * f_) / 1e-3))
        if f_ <= 1e6:                                   # the lumped model's reach (above it the board's parasitics decide)
            runs_ = []
            for q_ in Q116:
                for s_ in (1.0, -1.0):
                    runs_ += run_set(lambda t, a_=ip_, f2=f_, q2=q_, s2=s_: s2 * a_ * math.exp(-math.pi * f2 * t / q2) * math.sin(2 * math.pi * f2 * t),
                                     3.0 * q_ / (math.pi * f_) + 1.0 / f_, min(50e-9, 1.0 / (200.0 * f_)))
            row116.update(agg(runs_))
        r116.append(row116)

    def w115(t, s_=1.0, a_=A115):
        if t < E115:
            return s_ * a_ * t / E115
        if t < E115 + T115:
            return s_ * a_
        if t < 2 * E115 + T115:
            return s_ * a_ * (2 * E115 + T115 - t) / E115
        return 0.0
    runs115 = run_set(lambda t: w115(t, 1.0), 1e-6, 0.1e-9) + run_set(lambda t: w115(t, -1.0), 1e-6, 0.1e-9)
    l115 = agg(runs115)
    d59_base = {starts[0][0]: i_op * r59_hi, starts[1][0]: 0.0}
    be115_l = min(A115 * (csd_abs - d59_base[r_["start"]]) / (r_["d59"] - d59_base[r_["start"]]) for r_ in runs115 if r_["d59"] > d59_base[r_["start"]])
    r115 = dict(a=A115, t=T115, e=E115, q=A115 * (T115 + E115), d59_b=(i_op + A115) * r59_hi, d169_b=(i_op + A115) * rb_hi,
                vc25=clamp(d4, A115, 25.0), vch=clamp(d4, A115, t_air), be_l=be115_l, be_b=csd_abs / r59_hi - i_op,
                be_c50=be_clamp(d4, lim_draft, t_air), e_b=clamp(d4, A115, t_air) * A115 * (T115 + E115),
                y_trip=2.0 * A115 * (T115 + E115) / best["tau"][0], **l115)
    # the sustained over-voltage: (D3) the panel's own cold open circuit, REQ-016's window and L4-E13's check; (D4) a stiff source of
    # the kit's declared range on the port through the 5 m lead; (D5) a reversed panel, DECISION-31's note E-N1
    l13 = flat(open(os.path.join(TOP, "v2/docs/records/l4e13/L4E13-PANEL.md"), encoding="utf-8").read())
    g13 = float(need(l13, r"the disturbance check is implied by A-1 for every plane-of-array irradiance below (\d+) W/m2 \(n <= 2\)", "L4E13-PANEL.md the check").group(1))
    vbr13 = float(need(l13, r"conducts under 1 mA until its VBR \(([\d.]+) V cold minimum\)", "L4E13-PANEL.md the cold breakdown").group(1))
    if abs(vbr13 - vbr_cold) > 0.005:
        refuse(3, "L4-E13's cold breakdown is not this record's")
    p_ok = ((tjmax - t_air) / rja, (tjmax - t_cold) / rja)        # D4's continuous dissipation on the board, hot and cold ends (RthJA typical)

    def held(row_, vs_, vbr_):
        """A stiff source vs_ through the lead's loop into the clamp from breakdown vbr_ (INFERRED straight line, the same slope)."""
        rd_ = (row_["vc"] - row_["vbr"][1]) / row_["ipp"]
        i_ = max(0.0, (vs_ - vbr_) / (rd_ + lead["r"]))
        return i_, i_ * (vbr_ + rd_ * i_)
    src = [(lab_, vb_) + held(d4, v_src, vb_) for lab_, vb_ in (("the least part at the cold end", vbr_cold), ("the least part at 25 C", d4["vbr"][0]),
                                                                ("the highest part at 25 C", d4["vbr"][1]),
                                                                ("the least part at the junction's maximum", d4["vbr"][0] * (1 + aT * (tjmax - 25.0))))]
    # the smallest change for D4: the least row of the held series that stands off the source and does not break down at the cold end
    n36 = min(n_ for n_, r_ in smcj.items() if r_["vr"] >= v_src and r_["vbr"][0] * (1 + aT * (t_cold - 25.0)) > v_src)
    r36 = dict(smcj[n36])
    r36.update(n=n36, vbr_cold=r36["vbr"][0] * (1 + aT * (t_cold - 25.0)), vc116_25=clamp(r36, 10.0, 25.0), vc116_h=clamp(r36, 10.0, t_air),
               i50_25=be_clamp(r36, lim_draft, 25.0), i50_h=be_clamp(r36, lim_draft, t_air), iq3=be_clamp(r36, vds028, 25.0))
    z63 = need(z2, r"22 6\.3 7\.7 D8 (\d+) (\d+) [\d.]+ EEHZA1J220XP EEHZA1J220XV \d+ 63 ", "ZA p.2 the 63 V part in the D8 land").groups()
    r36["za63"] = dict(c=22e-6, ripple=float(z63[0]) * 1e-3, esr=float(z63[1]) * 1e-3)
    p_src36 = (v_src * reg_hi(rc_[0], v_src), v_src * i_trip_c(v_src, rpb, nb, 1, True, R66))
    rev = dict(i=c["i_src"], vf_be=p_ok[0] / c["i_src"])
    peak_v = max(max(r_["v"] for r_ in r116 if r_["lumped"]), r115["v"])
    peak_vp = max(max(r_["vp"] for r_ in r116 if r_["lumped"]), r115["vp"])
    v116 = max(r_["vch"] for r_ in r116)
    verd = [
        dict(id="D1", name="CS116 on PV_IN alone and on the J_SOLAR cable",
             ok=(v116 <= lim_draft and max(r_["d59_b"] for r_ in r116) < csd_abs and max(r_["d169_b"] for r_ in r116) < abs169[1]
                 and peak_v < vbr_cold and peak_vp < min(abs169[0], vsabs169) and max(r_["y_trip"] for r_ in r116) < best["m"]
                 and max(r_["e_b"] / r_["e_cap"] for r_ in r116) < 1.0 and max(r_["e_d4"] for r_ in r116 if r_["lumped"]) == 0.0),
             drawn=v116 <= lim_drawn),
        dict(id="D2", name="CS115 on the J_SOLAR cable",
             ok=(r115["vch"] <= lim_draft and r115["d59"] < csd_abs and r115["d59_b"] < csd_abs and r115["v"] < vbr_cold and r115["y_trip"] < best["m"]),
             drawn=r115["vch"] <= lim_drawn),
        dict(id="D3", name="the panel's own cold open circuit", ok=v_oc < d4["vr"] and v_oc < lim_draft, drawn=v_oc < lim_drawn),
        dict(id="D4", name="a stiff source of the kit's declared range on the port", ok=min(p_ for _l, _v, _i, p_ in src) <= p_ok[0], drawn=False),
        dict(id="D5", name="a reversed panel (DECISION-31, note E-N1)", ok=False, drawn=False),
    ]
    if [v_["ok"] for v_ in verd] != [True, True, True, False, False] or r36["vc116_h"] <= lim_draft or r36["vc116_25"] > lim_draft:
        refuse(4, "the panel lead's verdicts are not the ones the record states: %s" % [(v_["id"], v_["ok"]) for v_ in verd])
    R["lead"] = dict(lead=lead, tv=tv, f116=f116, q116=Q116, r116=r116, r115=r115, v_src=v_src, aT=aT, pd4=pd4, tjmax=tjmax, rja=rja, p_ok=p_ok,
                     vbr_cold=vbr_cold, lim_drawn=lim_drawn, lim_draft=lim_draft, src=src, r36=r36, p_src36=p_src36, rev=rev, g13=g13,
                     peak_v=peak_v, peak_vp=peak_vp, v116=v116, verd=verd, m_trip=best["m"], tau_lo=best["tau"][0],
                     smcj=sorted(smcj), i_op=i_op, v_oc=v_oc, n_runs=sum(1 for r_ in r116 if r_["lumped"]) * len(Q116) * 2 * 8 + len(runs115),
                     e_rating=e_rating)
    # ---- THE SOLAR-FAULT REMEDIES (the owner's amendment of 2 October 2026, 14:20, item 3: the 36 V source and the reversed panel are
    # open engineering defects; a selected remedy for each, its circuit changes and a bounded analysis against the approved fault
    # exposure and the parts' ratings; the interfaces and calculations re-checked; the normal window kept, fault protection never
    # extending the operating range). Three implementations on held sheets are compared; every figure is printed in section 10
    t48 = flat(subprocess.run(["pdftotext", "-layout", os.path.join(TOP, TPS48), "-"], capture_output=True).stdout.decode("utf-8", "replace"))

    def g3(t_, pat_, what_):
        return tuple(float(x_.replace(chr(0x2013), "-")) for x_ in need(t_, pat_, what_).groups())
    need(t48, r"VS, CS\+, CS., ISCP to GND .1 100", "TPS4811 6.1: VS, CS+, CS- and ISCP to GND")
    need(t48, r"SRC to GND .30 100", "TPS4811 6.1: SRC to GND")
    need(t48, r"VS, CS\+, CS. to GND 0 80 Input Pins EN/UVLO, OV to GND 0 15", "TPS4811 6.2")
    need(t48, r"Drives external back-to-back N-channel MOSFETs", "TPS4811 p.1: back-to-back FETs")
    need(t48, r"The TPS4811x-Q1 withstands output reverse voltages down to -30V\. With INP low, PD is pulled low to SRC", "TPS4811 8.3.7")
    need(t48, r"TI recommends RVS value around 100", "TPS4811 9.5: the VS filter")
    T48 = dict(ovr=g3(t48, r"V\(OVR\) Overvoltage threshold input, ris[Ii]ng ([\d.]+) ([\d.]+) ([\d.]+) V", "TPS4811 OVR"),
               ovf=g3(t48, r"V\(OVF\) Overvoltage threshold input, falling ([\d.]+) ([\d.]+) ([\d.]+) V", "TPS4811 OVF"),
               ovleak=g3(t48, r"I\(OV\) OV Input leakage current 0V < V\(OV\) < 5V (\d+) (\d+) nA", "TPS4811 OV leakage")[1] * 1e-9,
               iq=g3(t48, r"I\(Q\) Total System Quiescent current, I\(GND\) V\(EN/UVLO\) = 2V (\d+) (\d+) .A", "TPS4811 IQ")[1] * 1e-6,
               ics=g3(t48, r"I\(CS.\) CS. Input Bias current (\d+) (\d+) (\d+) .A", "TPS4811 CS- bias")[2] * 1e-6,
               iscp=g3(t48, r"I\(ISCP\) SCP Input Bias current ([\d.]+) ([\d.]+) ([\d.]+) .A", "TPS4811 ISCP bias")[2] * 1e-6,
               enleak=g3(t48, r"I\(EN/UVLO\) Enable input leakage current V\(EN/UVLO\) = 12V (\d+) (\d+) nA", "TPS4811 EN leakage")[1] * 1e-9,
               bst_i=g3(t48, r"I\(BST\) Charge Pump Supply current V\(BST . SRC\) = 10V (\d+) (\d+) (\d+) .A", "TPS4811 BST current"),
               bst_uv=g3(t48, r"UVLO voltage threshold, V\(BST_UVLOR\) ([\d.]+) ([\d.]+) ([\d.]+) V rising", "TPS4811 BST UVLO rising"),
               t_ov=g3(t48, r"tPD\(OV_OFF\) OV Turn Off propagation Delay OV . to PD ., CL = 47nF ([\d.]+) ([\d.]+) .s", "TPS4811 tPD(OV_OFF)"),
               wrn=g3(t48, r"RSET = 100 ., RIWRN = 39\.7k. ([\d.]+) ([\d.]+) ([\d.]+) mV", "TPS4811 OCP at 39.7k"),
               tmr_i=g3(t48, r"I\(TMR_SRC_CB\) TMR source current ([\d.]+) ([\d.]+) ([\d.]+) .A", "TPS4811 TMR source"),
               tmr_v=g3(t48, r"V\(TMR_OC\) ([\d.]+) ([\d.]+) ([\d.]+) V", "TPS4811 TMR threshold"),
               pin_abs=g3(t48, r"Input Pins OV, EN/UVLO, INP, INP_G, FLT_I , FLT_T to GND \S1 (\d+)", "TPS4811 input pins' maximum")[0])
    T48["cl"] = 47e-9
    lm5, lm6 = flat(pg(LM747, 5)), flat(pg(LM747, 6))
    need(lm5, r"ANODE to GND .65 65 V", "LM74700 6.1 ANODE")
    need(lm5, r"CATHODE to ANODE .5 75 V", "LM74700 6.1 CATHODE to ANODE")
    LM = dict(anode=-65.0, ca=75.0, vrev=g3(lm6, r"V\(AK REV\) (.\d+) (.\d+) (.\d+) mV", "LM74700 V(AK REV)"))
    q1_, q3_ = flat(pg(CSD32, 1)), flat(pg(CSD32, 3))
    QF = dict(vds=float(need(q1_, r"VDS Drain-to-Source Voltage (\d+) V", "CSD19532Q5B VDS").group(1)),
              vgs=float(need(q1_, r"VGS Gate-to-Source Voltage .(\d+) V", "CSD19532Q5B VGS").group(1)),
              idm=float(need(q1_, r"IDM Pulsed Drain Current\S* (\d+) A", "CSD19532Q5B IDM").group(1)),
              eas=float(need(q1_, r"Avalanche Energy, single pulse (\d+) mJ", "CSD19532Q5B EAS").group(1)) * 1e-3,
              idss=g3(q3_, r"IDSS Drain-to-Source Leakage Current VGS = 0 V, VDS = (\d+) V (\d+) .A", "CSD19532Q5B IDSS"),
              rds=g3(q3_, r"VGS = 6 V, ID = 17 A ([\d.]+) ([\d.]+) m. RDS\(on\) Drain-to-Source On Resistance VGS = 10 V, ID = 17 A ([\d.]+) ([\d.]+) m", "CSD19532Q5B RDS(on)"),
              ciss=g3(q3_, r"Ciss Input Capacitance (\d+) (\d+) pF", "CSD19532Q5B Ciss")[1] * 1e-12,
              coss=g3(q3_, r"Coss Output Capacitance VGS = 0 V, VDS = 50 V, . = 1 MHz (\d+) (\d+) pF", "CSD19532Q5B Coss")[1] * 1e-12)
    QF["rds_norm"] = 1.95        # Figure 8, normalized RDS(on) at 150 C, VGS 10 V (typical), L4-E9's reading (INFERRED from the figure)
    bz1 = flat(pg(BZT, 2))
    BZ = dict(vz=g3(bz1, r"BZT52C12 \w+ 12 ([\d.]+) ([\d.]+) 5", "BZT52C12 row"),
              pd=g3(bz1, r"Power Dissipation \(Note 8\) @TA = \+25.C PD (\d+) mW", "BZT52C PD")[0] * 1e-3)
    # the vehicle entry's TPS48110 network (L4-E11, accepted): the same values, so the same printed figures
    e11 = open(os.path.join(TOP, "v2/docs/records/l4e11/apply_gen_sch_e_entry.py"), encoding="utf-8").read()
    for pat_, what_ in ((r'TPS48110AQDGXRQ1 high-side driver with protection', "U6"), (r'"4\.5mOhm 1% 2512 3W 50ppm', "R19"),
                        (r'"59\.0k 1%".*?"10\.0k 1% \(UVLO', "the UVLO divider"), (r'"100k 1%", "DC_P", "HS_INP"\); r\("R85", "39k 1%', "the INP divider"),
                        (r'"100R 1% \(VS filter', "RVS"), (r'"22n C0G 5% 50V 1206 \(CTMR', "CTMR"), (r'"39\.7k 0\.1% \(RIWRN', "RIWRN"),
                        (r'"100R 0\.1% \(RSET\)"', "RSET"), (r'"3\.01k 1% \(RISCP', "RISCP"), (r'"1n C0G 100V \(CSCP', "CSCP"),
                        (r'"36\.5k 1% \(R1: gate slew\)"', "R1"), (r'"10R 1% \(R2: damping\)"', "R2"), (r'"10n C0G 5% 100V 1206 \(C1: gate slew', "C1"),
                        (r'"1u 25V X7R \(CBST', "CBST")):
        if not re.search(pat_, e11, re.S):
            refuse(3, "L4-E11's entry draft no longer carries %s" % what_)
    o11 = flat(open(os.path.join(TOP, "v2/docs/records/l4e11/l4e11_power.out"), encoding="utf-8").read())
    L11 = dict(uv=g3(o11, r"UVLO: on at ([\d.]+) / ([\d.]+) / ([\d.]+) V, off at", "L4-E11's UVLO"),
               uvf=g3(o11, r"UVLO: on at [\d.]+ / [\d.]+ / [\d.]+ V, off at ([\d.]+) / ([\d.]+) / ([\d.]+) V of DC_P", "L4-E11's UVLO falling"),
               slew=g3(o11, r"the start: slew ([\d.]+) / ([\d.]+) / ([\d.]+) V/ms", "L4-E11's slew"),
               inp=g3(o11, r"INP high from DC_P ([\d.]+) V", "L4-E11's INP")[0],
               cin_uv=(59.0e3, 10.0e3), inp_div=(100e3, 39e3), rsns=4.5e-3, rsns_tol=0.01, rsns_tcr=50e-6, cbst=1e-6, cbst_tol=0.10, ctmr=22e-9, ctmr_tol=0.05,
               riscp=3.01e3, cscp=1e-9, rvs=100.0, cvs=100e-9)
    # the stage's own enable (R14 and R15 on TRK_VS), as the generator draws it
    shdn_txt = need(gse, r'r\("R15", "15\.0k 1% \(SHDN: enable above about ([\d.]+) V\)"', "gen_sch_e.py R15").group(1)
    # (1) the comparison of three implementations (each on its held sheet)
    cs101_pk = c101_["v_pk"]
    vbr_cold_r = lambda row_: row_["vbr"][0] * (1 + aT * (t_cold - 25.0))
    rows_rt = {}
    for f_ in ("jlc-search-rt0603brd07-2026-10-01.json", "jlc-search-rt0603brd07-10k-2026-10-01.json", "jlc-search-rt0603brd07-30k-2026-10-01.json"):
        for r_ in json.load(open(os.path.join(TOP, INP, f_), encoding="utf-8"))["rows"]:
            v_ = rvalue(r_["model"])
            if v_ and r_["stock"] >= STOCK_MIN:
                rows_rt[v_] = (r_["code"], r_["stock"])

    def ov_band(a_, b_, rb_, aged):
        """The OV cut-off referred to the input: R_top = a_ + b_ in series over rb_ (RT 0.1 %, 25 ppm/K over the envelope, aged:
        the printed load-life and solder-heat limits), the comparator's printed rows, the pin's leakage either way through R_top."""
        rt_lo = a_ * rtf(a_, -1, aged) + b_ * rtf(b_, -1, aged)
        rt_hi = a_ * rtf(a_, 1, aged) + b_ * rtf(b_, 1, aged)
        k_lo = (rt_lo + rb_ * rtf(rb_, 1, aged)) / (rb_ * rtf(rb_, 1, aged))
        k_hi = (rt_hi + rb_ * rtf(rb_, -1, aged)) / (rb_ * rtf(rb_, -1, aged))
        lk_ = T48["ovleak"] * rt_hi
        return dict(rise=(T48["ovr"][0] * k_lo - lk_, T48["ovr"][2] * k_hi + lk_), fall=(T48["ovf"][0] * k_lo - lk_, T48["ovf"][2] * k_hi + lk_),
                    k=(k_lo, k_hi), rt=(rt_lo, rt_hi), cur=1.0 / (rt_hi + rb_ * rtf(rb_, 1, aged)))

    def ov_pick(d4row_, aged):
        """The stocked divider that leaves the most room on its worst side: over CS101's peak at the input (M2 never trips it), under
        the clamp's least breakdown at the cold end (a sustained source never reaches the clamp) and its falling threshold over 25 V
        (a panel inside the window is never locked out after a cut)."""
        tops = sorted(v_ for v_ in rows_rt if v_ >= 90e3)
        best_ = None
        for a_, b_ in itertools.combinations_with_replacement(tops, 2):
            for rb_ in sorted(v_ for v_ in rows_rt if v_ < 90e3):
                bd_ = ov_band(a_, b_, rb_, aged)
                m_ = (bd_["rise"][0] - cs101_pk, vbr_cold_r(d4row_) - bd_["rise"][1], bd_["fall"][0] - v_oc)
                key_ = (round(min(m_), 6), -a_ - b_, rb_)
                if best_ is None or key_ > best_[0]:
                    best_ = (key_, a_, b_, rb_, bd_, m_)
        return dict(a=best_[1], b=best_[2], rb=best_[3], band=best_[4], m=best_[5])
    ov28 = dict(new=ov_pick(d4, False), aged=ov_pick(d4, True))
    # the clamp D4 the cut-off needs: the least held SMCJ row whose aged band has room and whose clamp at the derived disturbances'
    # currents (D1's 10 A plateau, D2's 5 A) stays under the drafted entry's 50 V parts at the hot end (REQ-016's criterion)
    d4n = None
    for n_ in sorted(k_ for k_ in smcj if k_ >= 28):
        pk_ = ov_pick(smcj[n_], True)
        if min(pk_["m"]) > 0 and clamp(smcj[n_], 10.0, t_air) <= lim_draft and clamp(smcj[n_], A115, t_air) <= lim_draft:
            d4n, ovs = n_, pk_
            break
    if d4n is None:
        refuse(4, "BLOCKER: no held SMCJ row leaves the over-voltage cut-off room under REQ-016's criterion")
    D4N = dict(smcj[d4n], n=d4n, vbr_cold=vbr_cold_r(smcj[d4n]), v116=clamp(smcj[d4n], 10.0, t_air), v115=clamp(smcj[d4n], A115, t_air),
               v116_25=clamp(smcj[d4n], 10.0, 25.0), cap=min(smcj[d4n]["ipp"], be_clamp(smcj[d4n], lim_draft, 25.0)))
    bandN, bandA = ov_band(ovs["a"], ovs["b"], ovs["rb"], False), ovs["band"]
    D11 = dict(smcj[40], n=40, vbr_cold=vbr_cold_r(smcj[40]))
    # implementation 1: the TPS48110-Q1 alone on back-to-back FETs. As TI draws it (Figure 9-14) VS, CS+ and ISCP sit on the input,
    # rated -1 V to GND (6.1): a reversed panel takes them to minus its open circuit. Rearranged (VS behind a diode, the sense behind
    # the pair) SRC carries the reversal, -30 V at most (6.1, 8.3.7): the reversed panel itself, and the reversed connection's ring,
    # which only the input clamp bounds, at no less than its least breakdown at the cold end; the diode's drop (no minimum printed)
    # also sits inside the OV reference
    vf_diode = 0.715                                   # 1N4148W VF at 1 mA, the sheet's maximum (st-semtech-1n4148w-c81598.pdf)
    i1 = dict(pins=-v_oc, pins_abs=-1.0, src_rev=-v_oc, src_abs=-30.0, ring=-D11["vbr_cold"], ov_vf=vf_diode,
              ov_room=vbr_cold - cs101_pk)
    # implementation 2: the LM74700-Q1 ideal diode ahead of the TPS48110-Q1 (the vehicle entry's pair). Its reverse comparator
    # (V(AK REV) -17 to -2 mV) blocks every reverse current: CS116's negative lobes then find only the input clamp, and the
    # CATHODE-to-ANODE rating (75 V) carries the clamp's voltage plus what PV_R holds (up to the window's 25 V); and CS101's ripple
    # is rectified wherever the input falls faster than the stage drains the capacitance behind the diode
    i2 = dict(ca36_25=v_oc + clamp(smcj[36], 10.0, 25.0), ca36_hot=v_oc + clamp(smcj[36], 10.0, t_air), ca40_hot=v_oc + clamp(smcj[40], 10.0, t_air),
              c_total=c_bulk_max + c_a_max + c66_ + c_b_max, i_reg=max(reg_hi(rc_[0], v_) for v_ in v_ops))
    i2["f_rect"] = i2["i_reg"] / (i2["c_total"] * 2 * math.pi * (cs101_pk - v_oc))   # where the input falls faster than the stage drains C
    # (2) the selected block, implementation 3 (SESSION): U21, the TPS48110-Q1 over-voltage cut-off on the high side (TI's own
    # topology, the vehicle entry's network) with one CSD19532Q5B (Q12) behind R87, and a CSD19532Q5B return switch (Q13) in the
    # panel's return, its gate from PV_F through R101 100k over R102 100k, clamped by D12 BZT52C12-7-F; D11 SMCJ40CA across the
    # connector; C131 1 uF 100 V on PV_F (two 10 uF since B6, below); D4 to the SMCJ row the cut-off needs.
    # B6 (the consolidation review, astra-check-l4close-1; SESSION, the transient analysis below): U21's network is L4-E11's but
    # the OV divider, INP's bottom resistor R97 (39k to 30k: INP under its 20 V for PV_F up to 85 V) and CSCP C126 (1 nF to 330 pF:
    # the short-circuit trip's filter shorter, CS116's filtered sense still under the trip's least; SLUSEE5E 9.x lets CSCP be
    # tuned in the real system); round 1 made C131 two 10 uF 100 V parts; round 2 (L4-F01) makes the port bank C131, C132,
    # C135 and C136, four Samsung CL32B225KCJSNNE, R97 28.0k, and C133, C134 and C71 to C74 Samsung CL32B106KBJNNNE; C133 and
    # C134, two 10 uF 50 V ceramics (C13's part text and land), join the bulk on PV_P
    GD = dict(L11, inp_div=(L11["inp_div"][0], 28.0e3), cscp=330e-12)    # B6 round 2: R97 28.0k (INP 10 % under its 20 V)
    N_PC = 2
    rq11 = QF["rds"][3] * 1e-3 * QF["rds_norm"]        # VGS from the charge pump, at least 11 V: the 10 V row's maximum, at 150 C
    rq12 = QF["rds"][1] * 1e-3 * QF["rds_norm"]        # VGS at least 6 V in operation (below): the 6 V row's maximum, at 150 C
    rsn_hi = L11["rsns"] * (1 + L11["rsns_tol"]) * (1 + L11["rsns_tcr"] * dt_end)
    r_blk = rq11 + rq12 + rsn_hi
    R101, R102 = 100e3, 100e3
    vgs12_min = lo_h * R102 / (R101 + R102)                # at the hold's least corner, the stage's lowest operating input
    if vgs12_min < 6.0:
        refuse(4, "the return switch's gate is under 6 V at the hold's least corner")
    i_reg_hi, i_trip_hi = max(reg_hi(rc_[0], v_) for v_ in v_ops), c["i_hi25"]
    # what the block draws from the panel around the bank (at the window's top, every resistor at its least)
    i_uv = v_oc / (sum(L11["cin_uv"]) * 0.99)
    i_inp = v_oc / (sum(GD["inp_div"]) * 0.99)
    i_ovd = v_oc * ovs["band"]["cur"]
    i_g12 = v_oc / ((R101 + R102) * 0.99) + max(0.0, (v_oc * R102 / (R101 + R102) - BZ["vz"][0]) / R101)
    i_byp = T48["iq"] + T48["ics"] + T48["iscp"] + T48["enleak"] + T48["ovleak"] + i_uv + i_inp + i_ovd + i_g12 + 1e-6
    p_byp = v_oc * i_byp
    p_cond = (i_reg_hi ** 2 * r_blk, i_trip_hi ** 2 * r_blk)
    # the energy budget's entry: the block's conduction and bypass on SC-37's day and on the bright day at the selected setting
    tr_sel, _nl = energy(nom_h, lim_of(c["inom"], rc_[0], "lo"))
    br_sel, _nb = bright(nom_h, lim_of(c["inom"], rc_[0], "lo"))
    e_blk = tuple(sum(((w_ / nom_h) ** 2 * r_blk + nom_h * i_byp) for w_ in day_ if w_ > 0.0) for day_ in (tr_sel, br_sel))
    e_day = (sum(tr_sel), sum(br_sel))
    # the static bound and check (b) with the block at the panel entry: the boundary voltage stays at most 25 V (REQ-016's window),
    # so the block's series drop moves the bank's voltage, not the boundary's (the trip read at both), and its own currents around
    # the bank add at the boundary
    dv_blk = i_trip_hi * r_blk
    p_static_blk = max(v_ * max(i_trip_c(v_, rpb, nb, 1, True, R66), i_trip_c(max(v_ - dv_blk, grid[0]), rpb, nb, 1, True, R66)) + pb_c(v_, R66)
                       for v_ in grid) + p_byp
    c_in = 4 * 2.2e-6                                   # B6 round 2: C131, C132, C135, C136, four 2.2 uF 100 V X7R 1210 (nominal)
    c_pc_max = N_PC * 10e-6 * 1.10
    e_cap_blk = e_cap + (c_in * 1.10 + c_pc_max + L11["cvs"] * 1.10 + QF["coss"] + GD["cscp"]) * v_oc ** 2
    t_allow_blk = ((p_win - p_static_blk) * W_AVG - e_cap_blk - c["e_f"]) / (p_src - p_static_blk)
    slew_hi = L11["slew"][2] * 1e3                      # V/s
    c_behind_max = c_a_max + c66_ + c_b_max
    i_bank_slew = c_behind_max * slew_hi
    t_slew = v_oc / (L11["slew"][0] * 1e3)
    # the CS101 immunity re-run with the block in the path: its series resistance ahead of the bulk (S1 and S2), C_in across the input
    def cs101_blk(f_, i_, vin_, r_ser, cin_, cpc_=0.0):
        w_ = 2 * math.pi * f_
        z_b = rbank + 1.0 / y_behind(f_, LAYOUT, rc_[0], i_, vin_)
        y_a = 3.0 / (za["esr"] + 1.0 / (1j * w_ * c_can_max)) + (N_PC / (ESR_CER + 1.0 / (1j * w_ * cpc_)) if cpc_ else 0.0)
        z_eut = 1.0 / (1.0 / z_b + y_a)
        h_ = abs(z_eut / (z_eut + r_ser))
        z_in = 1.0 / (1.0 / (z_eut + r_ser) + 1j * w_ * cin_)
        e_ = math.sqrt(p101(f_) * 0.5)
        v2 = max(min(v101(f_), e_ * abs(z_in / (z_in + z_ret(f_, zp_)))) for zp_ in (1e-3, None))
        return v101(f_) * math.sqrt(2) * h_ / abs(z_b), v2 * math.sqrt(2) * abs(z_eut / (z_eut + r_ser)) / abs(z_b), h_
    tau_lo = best["tau"][0]
    cs_re = {}
    for lab_, r_, cin_ in (("none", 0.0, 0.0), ("least", QF["rds"][2] * 1e-3 * 2 + L11["rsns"] * (1 - L11["rsns_tol"]), c_in),
                           ("most", r_blk, c_in)):
        wr_ = []
        for f_ in freqs:
            hf_ = 1.0 / abs(1 + 1j * 2 * math.pi * f_ * tau_lo)
            cps_ = (0.0,) if lab_ == "none" else (0.0, c_pc_max / N_PC)    # C133 and C134 absent or at their largest
            s_ = max(max(cs101_blk(f_, i_reg_hi, v_, r_, cin_, cp_)[:2]) for v_ in v_ops for cp_ in cps_)
            wr_.append((f_, s_, s_ * hf_, max(cs101_blk(f_, i_reg_hi, v_, r_, cin_, cp_)[2] for v_ in v_ops for cp_ in cps_)))
        cs_re[lab_] = dict(worst=max(wr_, key=lambda x_: x_[2]), hmax=max(x_[3] for x_ in wr_), r=r_)
    if abs(cs_re["none"]["worst"][2] - best["worst"][2]) > 1e-9:
        refuse(4, "the CS101 re-run with no series resistance does not reproduce the accepted immunity")
    # the faults (D4 and D5 of the derivation) with the block
    st_min = L11["cbst"] * (1 - L11["cbst_tol"]) * T48["bst_uv"][0] / (T48["bst_i"][2] * 1e-6)   # the gate cannot rise before BST is charged
    f36 = dict(v=v_src, vds=v_src, vs=v_src, en=v_src * L11["cin_uv"][1] * 1.01 / (L11["cin_uv"][0] * 0.99 + L11["cin_uv"][1] * 1.01),
               inp=v_src * GD["inp_div"][1] * 1.01 / (GD["inp_div"][0] * 0.99 + GD["inp_div"][1] * 1.01),
               ov=v_src / bandA["k"][0], ring=D11["vc"], st_min=st_min, cut_hi=bandA["rise"][1], d4_room=D4N["vbr_cold"] - bandA["rise"][1])
    g_hs = 1.0 / (sum(L11["cin_uv"]) * 1.01) + 1.0 / (sum(GD["inp_div"]) * 1.01) + 1.0 / (bandA["rt"][1] + ovs["rb"] * rtf(ovs["rb"], 1, True)) + 1.0 / ((R101 + R102) * 1.01)
    rev = dict(v=v_oc, vds=v_oc, i_be=g_hs * 1.0, idss=QF["idss"][1] * 1e-6, idss_v=QF["idss"][0], q12_vds=QF["vds"], ring=D11["vc"],
               floor_c=-D11["vc"] * QF["coss"] / (c_in * 0.9))
    # CS116 and CS115 with the block on (in the path) and off (night, after a cut)
    t_rc = L11["riscp"] * 0.99 * GD["cscp"] * 0.95     # B6: the guard's CSCP, at its least (the least attenuation of CS116's lobes)
    scp3 = g3(o11, r"short circuit ([\d.]+) / ([\d.]+) / ([\d.]+) A;", "L4-E11's short-circuit threshold")   # the same RISCP and RSNS
    scp_lo = scp3[0]
    ocp11 = g3(o11, r"overcurrent ([\d.]+) / ([\d.]+) / ([\d.]+) A \(the printed row", "L4-E11's overcurrent threshold")
    scp_f = max(i_op + r_["ip"] * min(1.0, 1.0 / (math.pi * r_["f"] * t_rc)) for r_ in r116)
    ocp_lo = ocp11[0]
    t_over = max((max(Q116) / (math.pi * r_["f"])) * math.log(r_["ip"] / (ocp_lo - i_op)) for r_ in r116 if r_["ip"] > ocp_lo - i_op)
    v_tmr = T48["tmr_i"][2] * 1e-6 * t_over / (L11["ctmr"] * (1 - L11["ctmr_tol"]))
    ov_in116 = max(r_["vp"] for r_ in r116 if r_["lumped"]) + (i_op + 10.0) * r_blk
    def dv_hi(div_):
        """A 1 % divider's output fraction at its highest (top at -1 %, bottom at +1 %)."""
        return div_[1] * 1.01 / (div_[0] * 0.99 + div_[1] * 1.01)
    off116 = dict(v=clamp(D11, 10.0, t_air), en=clamp(D11, 10.0, t_air) * dv_hi(L11["cin_uv"]), inp=clamp(D11, 10.0, t_air) * dv_hi(GD["inp_div"]),
                  floor=-clamp(D11, 10.0, t_air) * QF["coss"] / (c_in * 0.9), v115=clamp(D11, A115, t_air),
                  e=clamp(D11, 10.0, t_air) * 10.0 * max(Q116) / (math.pi * 1e6))
    t_gate = T48["t_ov"][1] * 1e-6
    gate_load = QF["ciss"] + 10e-9 * 1.05
    rem = dict(T48=T48, LM=LM, QF=QF, BZ=BZ, L11=L11, shdn=float(shdn_txt), i1=i1, i2=i2, ov28=ov28, ovs=ovs, bandN=bandN, bandA=bandA, D4N=D4N, D11=D11,
               rq11=rq11, rq12=rq12, rsn_hi=rsn_hi, r_blk=r_blk, vgs12_min=vgs12_min, i_byp=i_byp, p_byp=p_byp, p_cond=p_cond, e_blk=e_blk, e_day=e_day,
               p_static_blk=p_static_blk, e_cap_blk=e_cap_blk, t_allow_blk=t_allow_blk, i_bank_slew=i_bank_slew, t_slew=t_slew, cs_re=cs_re,
               f36=f36, rev=rev, scp_f=scp_f, scp_lo=scp_lo, ocp_lo=ocp_lo, t_over=t_over, v_tmr=v_tmr, ov_in116=ov_in116, off116=off116,
               t_gate=t_gate, gate_load=gate_load, ocp11=ocp11, ring_en=D11["vc"] * dv_hi(L11["cin_uv"]), ring_inp=D11["vc"] * dv_hi(GD["inp_div"]), cs101_pk=cs101_pk, c_in=c_in, i_reg_hi=i_reg_hi, i_trip_hi=i_trip_hi,
               gap=(v_oc, bandA["rise"][1], bandA["rise"][1] * i_trip_c(bandA["rise"][1], rpb, nb, 1, True, R66)),
               hold_shift=i_reg_hi * r_blk, dv_blk=dv_blk, t_fac=T_FAC, t_resp_typ=c["t_resp_typ"], tau_lo=tau_lo, margin=best["m"], R101=R101, R102=R102,
               ov_codes=(rows_rt[ovs["a"]][0], rows_rt[ovs["b"]][0], rows_rt[ovs["rb"]][0]))
    # ---- B6, THE GUARD ALREADY ON, round 2 (the consolidation review's B6; the external review of the provisional fixes, L4-F01:
    # 0.3 % headroom, one bias factor for three banks with no maker basis, numerical error and the harness unbounded). MODELED by
    # guard_event_b: the selected network with every ceramic bank its maker's curves at its own voltage, each bank bounded on its
    # own, the timestep's error added, the whole envelope of the source's loop from 0.30 uH; three approaches compared
    U5_LIM, M_OTHER = 0.240, 0.10          # SESSION, decided before any value: U5 within +-0.240 V, every other rating 10 % clear
    slew_abs = float(need(t48, r"Voltage slew rate on drain side input pins \(VS, CS\+, CS.,\s*(\d+) V/.s ISCP\)", "TPS4811 6.1: the drain-side pins' slew").group(1)) * 1e6
    vsrc_ab = g3(t48, r"VS, CS\+, CS. to SRC .(\d+) (\d+)", "TPS4811 6.1: VS, CS+ and CS- to SRC")
    ics_abs = g3(t48, r"I\(CS\+\) to I\(CS.\) , 1msec .(\d+) (\d+)", "TPS4811 6.1: I(CS+) to I(CS-) for 1 ms")[1] * 1e-3
    cspm = g3(t48, r"CS\+ to CS. .(0\.3) (0\.3)", "TPS4811 6.1: CS+ to CS-")[1]
    need(t48, r"Current sense positive input\. Connect a 50 - 100. resistor across CS\+ 18 18 I CS\+ to the external current sense resistor", "TPS4811 5: CS+ through 50 to 100 Ohm")
    need(t48, r"TI recommends to add filter capacitor of 1nF \(CSCP\) across ISCP and CS. pins close to the device\. Because nuisance trips are "
              r"dependent on the system and layout parasitics, TI recommends to test the design in a real system and tweaked as necessary", "TPS4811 9: CSCP tuned in the real system")
    need(t48, r"Use of a TVS diode and input capacitor filter combination across input to and GND to absorb the energy and dampen the positive transients", "TPS4811 9: the input's TVS and capacitor")
    tsc6 = g3(t48, r"V\(SNS_SCP\) to PD ., (\d+) (\d+) .s Delay CL = 47nF, TPS48110.Q1 Only", "TPS4811 tSC (TPS48110-Q1)")
    tsc11 = g3(t48, r"V\(SNS_SCP\) to PD ., CL ([\d.]+) ([\d.]+) .s Delay = 47nF, TPS48111-Q1 Only", "TPS4811 tSC (TPS48111-Q1)")
    need(t48, r"OV must be connected to GND when not used", "TPS4811 5: OV on the TPS48110-Q1")
    need(t48, r"OV 2 . I below OV falling threshold then PU gets pulled up to BST", "TPS4811 5: pin 2 is OV on the TPS48110-Q1 only")
    need(t48, r"INP_G . 2 I G pulled to SRC when INP_G is left floating", "TPS4811 5: pin 2 is INP_G on the TPS48111-Q1")
    tinp = g3(t48, r"tPD\(INP_L\) INP Turn OFF propagation Delay INP . to PD ., CL = 47nF (\d+) .s", "TPS4811 tPD(INP_L)")[0]
    inph = g3(t48, r"V\(INP_H\) ([\d.]+) ([\d.]+) V", "TPS4811 V(INP_H)")
    # the sense pins of U5 (8705af p.30 and p.4): the pin-level limiter is judged on these printed statements
    need(raw[30], r"all four of the current sense pins can draw bias current under normal operating conditions\. As such, do not place resistors in series with any of the CSxIN or CSxOUT pins", "8705af p.30 no series resistor at CSxIN")
    need(raw[30], r"the CSNIN and CSPOUT pins are also connected", "8705af p.30 CSNIN and CSPOUT also feed the boost charge control")
    need(raw[30], r"to the Boost Capacitor Charge Control block \(also see Figure 1\) and can draw current in certain conditions", "8705af p.30 that block's draw")
    ibias_sum = float(need(raw[4], r"CSPIN, CSNIN Bias Current BOOST Capacitor Charge Control Block Not Active ICSPIN \+ ICSNIN, VCSPIN = VCSNIN = 12V (\d+) .A", "8705af p.4 CSPIN and CSNIN bias (typical sum)").group(1)) * 1e-6
    need(raw[34], r"Resistors greater than 10. should be avoided as this can increase offset voltages at the CSP/CSN pins\. The RC product should be kept to less than 30ns", "8705af p.34 the filter shown only for CSP and CSN")
    c32_ = flat(subprocess.run(["pdftotext", "-layout", os.path.join(TOP, CSD32), "-"], capture_output=True).stdout.decode("utf-8", "replace"))
    rja_q = float(need(c32_, r"R.JA Junction-to-Ambient Thermal Resistance \(1\) \(2\) (\d+)", "CSD19532Q5B RthJA").group(1))
    tjm_q = float(need(c32_, r"TJ, Operating Junction and .55 to (\d+) .C Tstg", "CSD19532Q5B TJ's maximum").group(1))
    soa_l = soa_lines_csd32()
    tc_q = (t_air + i_trip_hi ** 2 * rq11 * rja_q, t_air + i_trip_hi ** 2 * rq12 * rja_q)
    der_q = tuple((tjm_q - tc_) / (tjm_q - 25.0) for tc_ in tc_q)
    rd_ = lambda row_: (row_["vc"] - row_["vbr"][1]) / row_["ipp"]
    d11_hot = (smcj[40]["vbr"][1] * (1 + aT * (t_air - 25.0)), rd_(smcj[40]))
    d11_cold = (smcj[40]["vbr"][0] * (1 + aT * (t_cold - 25.0)), rd_(smcj[40]))
    t_f6 = 5 * 10.0 * 1.01 * QF["ciss"]                # INFERRED: a further 5 x R91 x Ciss after PD's 1 V (already under VGS(th)'s least)
    kov = ovs["rb"] * rtf(ovs["rb"], 1, True) / (bandA["rt"][0] + ovs["rb"] * rtf(ovs["rb"], 1, True))
    inp_on6 = inph[1] * (GD["inp_div"][0] * 1.01 + GD["inp_div"][1] * 0.99) / (GD["inp_div"][1] * 0.99)
    r_lead6 = lead["r"] * (1 + AC_.ALPHA_CU * (t_cold - 20.0)) / (1 + AC_.ALPHA_CU * (AC_.T_LEAD - 20.0))
    # the makers' curves (Samsung's typical characteristic data, held back under v2/vendor/passives/held/ by
    # fetch_maker_curves.py and pinned above): the DC-bias change, the change over
    # temperature under bias, the ESR. Bounds per bank, each on its own: the part's K tolerance (+-10 %, its code), the typical
    # curve's spread (BAND, ASSUMPTION: the maker prints no spread), the temperature at bias over the envelope
    SAM = {pn: json.load(open(os.path.join(TOP, SAMH % pn), encoding="utf-8")) for pn in CER_PARTS}
    for pn_, d_ in SAM.items():
        if d_["part"] != pn_ + "E" or len(d_["dc_bias_V_percent"]) < 50:
            refuse(3, "the filed Samsung reading of %s is not the one read" % pn_)
        for k_ in ("dc_bias_V_percent", "tcc_degC_percent", "bias_tcc_degC_percent", "esr_MHz_ohm", "z_MHz_ohm"):
            if d_[k_] != sorted(d_[k_]):                # the fetch sorts each series (the page can serve them out of order)
                refuse(3, "the held Samsung excerpt of %s is not sorted" % pn_)
    BAND = 0.15

    def interp(curve_, x_):
        for (x0, y0), (x1, y1) in zip(curve_, curve_[1:]):
            if x0 <= x_ <= x1:
                return y0 + (y1 - y0) * (x_ - x0) / (x1 - x0) if x1 > x0 else y0
        return curve_[0][1] if x_ < curve_[0][0] else curve_[-1][1]

    def tfac(pn_):
        bt_ = SAM[pn_]["bias_tcc_degC_percent"]
        ref_ = 1 + interp(bt_, 25.0) / 100.0
        vals_ = [(1 + interp(bt_, t_) / 100.0) / ref_ for t_ in (t_cold, t_cold + 0.25 * (t_air - t_cold), 25.0, t_air)]
        return min(vals_), max(vals_)

    def part(cnt_, cn_, pn_, side_):
        """One bank member: its count, nominal, maker curve and the factor at the side the bound needs."""
        if pn_ is None:                                 # no maker curve held: no derating, at +10 % (the record's convention)
            return (cnt_, cn_, None, 1.10, 1.10)
        lo_, hi_ = tfac(pn_)
        fac_ = 0.90 * (1 - BAND) * lo_ if side_ == "lo" else 1.10 * (1 + BAND) * hi_
        return (cnt_, cn_, SAM[pn_]["dc_bias_V_percent"], fac_, 1.10)
    N_F = 4                                             # C131, C132, C135, C136: Samsung CL32B225KCJSNNE, 2.2 uF 100 V X7R 1210
    bF_lo = CerBank([part(N_F, 2.2e-6, "CL32B225KCJSNN", "lo")])
    bF_hi = CerBank([part(N_F, 2.2e-6, "CL32B225KCJSNN", "hi")])
    bP_lo = CerBank([part(N_PC, 10e-6, "CL32B106KBJNNN", "lo")])            # C133, C134 (Samsung CL32B106KBJNNNE)
    bS_lo = CerBank([part(N_CA, 10e-6, "CL32B106KBJNNN", "lo")])            # C71 to C74 (the same part)
    bC_hi = CerBank([part(2, 10e-6, "CL31B106KBHNNN", "hi"), part(1, 4.7e-6, None, "hi"), part(1, 0.1e-6, None, "hi")])   # C13, C14 (C89632), C15, C64
    esr_d = {pn_: interp(SAM[pn_]["esr_MHz_ohm"], 0.1) for pn_ in CER_PARTS}

    def gparR(tsc_, cscp_):
        return dict(E=v_src, r_lead=r_lead6, bF=bF_lo, bP=bP_lo, bS=bS_lo, bC=bC_hi, esrP=ESR_CER / N_PC, esrS=ESR_CER / N_CA, rb=rb_lo,
                    r59=r59_hi, r_on=L11["rsns"] * (1 - L11["rsns_tol"]), d4=(D4N["vbr_cold"], rd_(D4N)), d11=d11_hot, ov=bandA["rise"][1],
                    isc=scp3[2], tau=L11["riscp"] * 1.01 * cscp_ * 1.05, t_ov=T48["t_ov"][1] * 1e-6, t_sc=tsc_, t_f=t_f6, v_behind=0.0)
    bk6 = (("the largest, no ESR credited", (0.0, c_bulk_max)), ("aged, at -40 C", bulks["cold_aged"]), ("new, at 20 C", bulks["new_20"]))
    st6 = (("U21's least turn-off, idle", L11["uvf"][0], 0.0), ("the hold's least corner, idle", lo_h, 0.0),
           ("the hold's least corner, at the trip's highest current", lo_h, i_op), ("REQ-016's open circuit, idle", v_oc, 0.0),
           ("REQ-016's open circuit, at the trip's highest current (a bound)", v_oc, i_op))

    def soa_r(samp_, t_on_, der_):
        return max((iq_ / (der_ * soa_t(soa_l, max(vd_, 0.1), max(t_on_, 1e-6))) for vd_, iq_ in samp_), default=0.0)

    def evalR(L_, g_, cold=False, starts_=None, soa=False, ramp=None, dt=20e-9):
        W_ = dict(vF=-1e9, vFmin=1e9, vP=-1e9, vS=-1e9, i4=0.0, e4=0.0, i11=0.0, e11=0.0, t11=0.0, iQ=0.0, iL=0.0, vds=-1e9, vdsmin=1e9,
                  slew=0.0, u5=-1e9, u5n=1e9, u18=-1e9, u18n=1e9, soa12=0.0, soa13=0.0, mono=True, ton=0.0, why=set(), n=0, arg=None, di59=0.0,
                  di59_up=0.0, di59_dn=0.0, u5L=-1e9, u5Ln=1e9)
        for _lab, v0_, i0_ in (starts_ or st6):
            for _bl, bk_ in (bk6[:1] if cold else bk6):
                for d11_ in ((d11_hot, d11_cold) if ramp is None else (d11_hot,)):
                    g_["d11"] = d11_
                    if ramp is None:
                        r_ = guard_event_b(g_, v0_, i0_, L_, bk_, cold=cold, dt=dt)
                    else:
                        r_ = guard_event_b(g_, v0_, i0_, L_, bk_, ramp=ramp, dt=(dt if ramp >= 1e6 else 5 * dt), t_end=(v_src - v0_) / ramp + 40e-6)
                    W_["n"] += 1
                    if r_["u5"] > W_["u5"]:
                        W_["arg"] = (v0_, i0_, bk_, d11_)
                    for kk_ in ("vF", "vP", "vS", "i4", "e4", "i11", "e11", "iQ", "iL", "vds", "slew", "u5", "u18", "di59", "di59_up", "u5L"):
                        W_[kk_] = max(W_[kk_], r_[kk_])
                    for kk_ in ("vFmin", "vdsmin", "u5n", "u18n", "di59_dn", "u5Ln"):
                        W_[kk_] = min(W_[kk_], r_[kk_])
                    if r_["t11"]:
                        W_["t11"] = max(W_["t11"], r_["t11"][1] - r_["t11"][0])
                    W_["ton"] = max(W_["ton"], r_["t_on"])
                    if not cold:
                        W_["why"].add(r_["why"])
                        if ramp is None and not (r_["di_go"] is not None and r_["di_go"] > 0.0):
                            W_["mono"] = False
                        if soa:
                            W_["soa12"] = max(W_["soa12"], soa_r(r_["samp"], r_["t_on"], der_q[0]))
        g_["d11"] = d11_hot
        W_["soa13"] = W_["iL"] / (der_q[1] * soa_t(soa_l, 1.0, max(W_["ton"], 1e-6)))
        return W_
    kinp, ken = dv_hi(GD["inp_div"]), dv_hi(L11["cin_uv"])
    # each rating: its value, its limit with the decided margin, the side it must stay on (+1 at or under, -1 at or over);
    # U5's two get the bounded numerical error on top (ERR, set by the timestep study below)
    ERR = [0.0]
    RT6 = (("pvf", "PV_F (U21's VS, CS+, CS-, ISCP; the port bank)", lambda W_: (W_["vF"], 100.0 * (1 - M_OTHER), 1)),
           ("slew", "PV_F's slew at CS-, CS+ and ISCP, V/us", lambda W_: (W_["slew"] / 1e6, slew_abs / 1e6 * (1 - M_OTHER), 1)),
           ("vds", "Q12's VDS (and VS, CS+, CS- to SRC)", lambda W_: (W_["vds"], min(QF["vds"], vsrc_ab[1]) * (1 - M_OTHER), 1)),
           ("inp", "U21's INP (R96 over R97)", lambda W_: (W_["vF"] * kinp, T48["pin_abs"] * (1 - M_OTHER), 1)),
           ("en", "U21's EN/UVLO (R94 over R95)", lambda W_: (W_["vF"] * ken, T48["pin_abs"] * (1 - M_OTHER), 1)),
           ("floor", "PV_F's least (VS, CS+, CS-, ISCP to GND)", lambda W_: (W_["vFmin"], -1.0, -1)),
           ("u5p", "U5's CSPIN to CSNIN, positive (+ numerical error)", lambda W_: (W_["u5"] + ERR[0], U5_LIM, 1)),
           ("u5n", "U5's CSPIN to CSNIN, negative (- numerical error)", lambda W_: (W_["u5n"] - ERR[0], -U5_LIM, -1)),
           ("d4", "D4's current, A (SMCJ30A, least, cold end)", lambda W_: (W_["i4"], 0.0, 1)),
           ("u18", "U18's differential", lambda W_: (W_["u18"], abs169[1] * (1 - M_OTHER), 1)),
           ("pvp", "PV_P (bulk, C133, C134, U18's common mode)", lambda W_: (W_["vP"], min(za["v"], abs169[0], vsabs169) * (1 - M_OTHER), 1)),
           ("trkvs", "TRK_VS (C71 to C74), under D4's least", lambda W_: (W_["vS"], D4N["vbr_cold"], 1)))

    def okr6(f_, W_):
        v_, l_, s_ = f_(W_)
        return (l_ - v_) * s_ >= -1e-12

    def ok6(W_):
        return {id_: okr6(f_, W_) for id_, _t, f_ in RT6}
    GA = gparR(tsc6[1] * 1e-6, GD["cscp"])             # the selected network (A): the TPS48110-Q1, its 5 us
    GD11 = gparR(tsc11[1] * 1e-6, GD["cscp"])          # approach D: the TPS48111-Q1's 1.6 us
    grid6 = [0.30e-6 * 1.1 ** j_ for j_ in range(38)]
    # the timestep's error: the selected network's worst case near its floor, from 40 ns down to 0.5 ns
    Wc_ = evalR(3.3e-6, GA)
    v0c_, i0c_, bkc_, d11c_ = Wc_["arg"]
    GA["d11"] = d11c_
    conv6 = [(dt_, guard_event_b(GA, v0c_, i0c_, 3.3e-6, bkc_, dt=dt_)["u5"]) for dt_ in (40e-9, 20e-9, 10e-9, 5e-9, 2e-9, 1e-9, 0.5e-9)]
    GA["d11"] = d11_hot
    u20_, ufin_ = conv6[1][1], conv6[-1][1]
    ERR[0] = 2.0 * max(abs(u_ - ufin_) for dt_, u_ in conv6 if dt_ <= 20e-9)
    if ERR[0] > 0.005 or abs(conv6[-2][1] - ufin_) > 0.25 * ERR[0]:
        refuse(4, "B6: the timestep study does not converge inside its bound: %s" % conv6)

    def floor_of(g_):
        evs_ = [evalR(L_, g_) for L_ in grid6]
        ls_ = {}
        for id_, _t, _f in RT6:
            j_ = len(grid6)
            while j_ > 0 and ok6(evs_[j_ - 1])[id_]:
                j_ -= 1
            if j_ == len(grid6):
                refuse(4, "B6: %s does not hold even at %.2f uH" % (id_, 1e6 * grid6[-1]))
            ls_[id_] = grid6[j_] if j_ > 0 else None
        jb_ = max((grid6.index(v_) for v_ in ls_.values() if v_ is not None), default=0)
        lo_, hi_ = (grid6[jb_ - 1], grid6[jb_]) if jb_ else (grid6[0], grid6[0])
        for _ in range(10 if jb_ else 0):
            mid_ = 0.5 * (lo_ + hi_)
            lo_, hi_ = (lo_, mid_) if all(ok6(evalR(mid_, g_)).values()) else (mid_, hi_)
        return math.ceil(hi_ * 1e8) / 1e8, ls_, evs_
    LA, lsA, evA = floor_of(GA)
    LD, lsD, evD = floor_of(GD11)
    WA = evalR(LA, GA, soa=True)
    if not all(ok6(WA).values()) or not WA["mono"]:
        refuse(4, "B6: the selected network does not hold at its own least inductance %.2f uH" % (1e6 * LA))
    # the corner search: no correlation between the four banks is supported, so each is bounded on its own and every one of the
    # sixteen combinations of their bounds is run at the floor over every start, bulk corner and D11 end. C15 and C64 carry no
    # maker curve: +10 % on their bank's upper side, a quarter of nominal on its lower (ASSUMPTION). The selected corner (the
    # port bank, PV_P and TRK_VS at their least, TRK_VIN at its largest) must be the worst on U5, and every combination must hold
    def banks_q(sF_, sP_, sS_, sC_):
        nc_ = lambda c_, cn_: (c_, cn_, None, 1.10 if sC_ == "hi" else 0.25, 1.10)
        return dict(bF=CerBank([part(N_F, 2.2e-6, "CL32B225KCJSNN", sF_)]), bP=CerBank([part(N_PC, 10e-6, "CL32B106KBJNNN", sP_)]),
                    bS=CerBank([part(N_CA, 10e-6, "CL32B106KBJNNN", sS_)]),
                    bC=CerBank([part(2, 10e-6, "CL31B106KBHNNN", sC_), nc_(1, 4.7e-6), nc_(1, 0.1e-6)]))
    cnr6 = []
    for cq_ in itertools.product(("lo", "hi"), repeat=4):
        Wq_ = evalR(LA, dict(GA, **banks_q(*cq_)))
        okq_ = ok6(Wq_)
        cnr6.append(dict(c=cq_, u5=Wq_["u5"], u5n=Wq_["u5n"], vF=Wq_["vF"], vS=Wq_["vS"], ok=all(okq_.values()) and Wq_["mono"],
                         fails=sorted(id_ for id_, v_ in okq_.items() if not v_)))
    cnr_w = max(cnr6, key=lambda c_: c_["u5"])
    cnr_sel = [c_ for c_ in cnr6 if c_["c"] == ("lo", "lo", "lo", "hi")][0]
    if cnr_w["c"] != ("lo", "lo", "lo", "hi") or abs(cnr_sel["u5"] - WA["u5"]) > 1e-12 or not all(c_["ok"] for c_ in cnr6):
        refuse(4, "B6: the corner search does not confirm the selected corner at %.2f uH: %s" % (1e6 * LA, [(c_["c"], c_["fails"]) for c_ in cnr6 if not c_["ok"]] or cnr_w["c"]))
    bindA = [id_ for id_, v_ in lsA.items() if v_ == max(x_ for x_ in lsA.values() if x_ is not None)]
    W1u = evA[grid6.index(min(grid6, key=lambda x_: abs(x_ - 1.0e-6)))]
    W03 = evA[0]
    fail1 = [id_ for id_, v_ in ok6(W1u).items() if not v_]
    W25 = evalR(LA, GA, starts_=(st6[3], st6[4]))
    # the cold connection: the port bank at its least and its largest, from a discharged port and from 25 V, over the grid
    cold6 = []
    for c_bank_ in (bF_lo, bF_hi):
        gc_ = dict(GA, bF=c_bank_)
        cold6.append([evalR(L_, gc_, cold=True, starts_=(("discharged", 0.0, 0.0), ("REQ-016's open circuit", v_oc, 0.0))) for L_ in grid6])
    Wc6 = cold6[0] + cold6[1]                           # the whole grid: the cold ring does not reach U5
    cold_max = dict(vF=max(c_["vF"] for c_ in Wc6), slew=max(c_["slew"] for c_ in Wc6), iL=max(c_["iL"] for c_ in Wc6), e11=max(c_["e11"] for c_ in Wc6),
                    vFmin=min(c_["vFmin"] for c_ in Wc6), t11=max(c_["t11"] for c_ in Wc6))
    cold_ok = (cold_max["vF"] <= 100.0 * (1 - M_OTHER) and cold_max["slew"] <= slew_abs * (1 - M_OTHER) and cold_max["vF"] * kinp <= T48["pin_abs"] * (1 - M_OTHER)
               and cold_max["vFmin"] >= -1.0)
    # ramps at the selected network's floor (the OV path's 4 us against D4's room, the short-circuit trip for every faster ramp)
    c_min6 = bulks["cold_aged"][1] + bP_lo.C(v_oc) + bS_lo.C(v_oc) + bC_hi.C(v_oc)      # near the least (it only centres the dense band)
    s_h6 = scp3[2] / c_min6
    rates6 = tuple(sorted({0.01e6, 0.05e6, 0.1e6, 0.3e6, 1e6, 3e6, 10e6} | {round(s_h6 * (0.7 + 0.01 * j_), -2) for j_ in range(41)}))
    ramp6 = []
    for rt_ in rates6:
        Wr_ = evalR(LA, GA, starts_=(st6[2], st6[3], st6[4]), ramp=rt_)
        ramp6.append(dict(rate=rt_, vS=Wr_["vS"], vP=Wr_["vP"], i4=Wr_["i4"], u5=Wr_["u5"], u5n=Wr_["u5n"], vF=Wr_["vF"], slew=Wr_["slew"], why=sorted(Wr_["why"]), ok=all(ok6(Wr_).values())))
    ramp_ok = all(r_["ok"] for r_ in ramp6)
    ramp_w = max(ramp6, key=lambda r_: r_["vS"])
    # the start's inrush through Q12 under U21's overcurrent (every capacitor behind Q12 at its largest, the gate's fastest slew)
    i_start6 = (c_bulk_max + c_pc_max + c_behind_max) * slew_hi
    # the round-1 network (11339ec7) and the review's witnesses, on guard_event with one constant factor per bank
    G1 = dict(E=v_src, r_lead=r_lead6, c131=2 * 10e-6 * 0.9 * 0.25, n_ca=N_CA, esr_cer=ESR_CER, n_pc=N_PC, rb=rb_lo, r59=r59_hi,
              r_on=L11["rsns"] * (1 - L11["rsns_tol"]), d4=(D4N["vbr_cold"], rd_(D4N)), d11=d11_hot, ov=bandA["rise"][1], isc=scp3[2],
              tau=L11["riscp"] * 1.01 * GD["cscp"] * 1.05, t_ov=T48["t_ov"][1] * 1e-6, t_sc=tsc6[1] * 1e-6, t_f=t_f6, v_behind=0.0)
    wit6 = [(lab_, guard_event(G1, L11["uvf"][0], 0.0, 2.47e-6, bulks["cold_aged"], k_, dt=dt_, t_end=60e-6)["u5"])
            for lab_, k_, dt_ in (("20 ns, one bias factor 1", 1.0, 20e-9), ("1 ns, the same", 1.0, 1e-9),
                                  ("20 ns, TRK_VS 0.99, PV_P and TRK_VIN 1.00", (1.0, 0.99, 1.0), 20e-9),
                                  ("20 ns, TRK_VS 0.95, PV_P and TRK_VIN 1.00", (1.0, 0.95, 1.0), 20e-9),
                                  ("20 ns, PV_P and TRK_VS 0.25, TRK_VIN 1.00", (0.25, 0.25, 1.0), 20e-9))]
    # the selected network at the round-1 witness's own case (2.47 uH, 7.46 V, idle, the aged bulk at -40 C)
    GA["d11"] = d11_hot
    witA = guard_event_b(GA, L11["uvf"][0], 0.0, 2.47e-6, bulks["cold_aged"])["u5"]
    # D11's energy against its 10/1000 us row derated at the hot end, scaled to the event by the square root of its duration
    e11_cap = smcj[40]["vc"] * smcj[40]["ipp"] * (t2s - t1s) / f_n * d4_der
    t11_6 = max(WA["t11"], cold_max["t11"])
    e11_6 = max(WA["e11"], cold_max["e11"])
    e11_room = e11_cap * math.sqrt(min(1.0, max(t11_6, 1e-6) / 1e-3))
    r_c6 = math.sqrt(lead["mm2"] * 1e-6 / math.pi)
    sp = lambda L_: 2 * r_c6 * math.cosh(L_ / (4e-7 * lead["m"]))
    rsns_v = WA["iQ"] * L11["rsns"] * (1 + L11["rsns_tol"]) * (1 + L11["rsns_tcr"] * dt_end)
    # the pin-level limiter (approach B), on the sheet's printed statements: series resistors at CSPIN and CSNIN are excluded by
    # 8705af p.30, and the error they would add rests on a typical sum of the two pins' bias currents with no maximum and no split,
    # plus an unprinted draw of CSNIN by the boost capacitor charge control; at 10 Ohm per pin the typical sum alone is
    lim_err = 10.0 * ibias_sum / (i_reg_hi * r59_hi)
    b6 = dict(G6=dict(GA), G1=dict(G1), bulk_cold=bulks["cold_aged"], uvf_lo=L11["uvf"][0], U5_LIM=U5_LIM, M_OTHER=M_OTHER, ERR=ERR[0], conv=conv6,
              conv_case=(v0c_, i0c_), LA=LA, LD=LD, lsA=lsA, lsD=lsD, bindA=bindA, W=WA, W25=W25, W1u=W1u, W03=W03, fail1=fail1,
              sA=sp(LA), sD=sp(LD), s1=sp(1.0e-6), r_lead=r_lead6, t_lead=AC_.T_LEAD, cold=cold_max, cold_ok=cold_ok, ramp=ramp6, ramp_ok=ramp_ok,
              ramp_w=ramp_w, s_h=s_h6, c_min=c_min6, rates=rates6, i_start=i_start6, wit=wit6, witA=witA, e11=e11_6, e11_cap=e11_cap,
              e11_room=e11_room, t11=t11_6, rsns_v=rsns_v, i_cs=rsns_v / (100.0 * 0.999), ics_abs=ics_abs, cspm=cspm, slew_abs=slew_abs,
              vsrc_ab=vsrc_ab, tsc=tsc6, tsc11=tsc11, tinp=tinp, inph=inph, inp_on=inp_on6, rja=rja_q, tjm=tjm_q, tc=tc_q, der=der_q,
              tau=(L11["riscp"] * 0.99 * GD["cscp"] * 0.95, L11["riscp"] * 1.01 * GD["cscp"] * 1.05), t_f=t_f6, kinp=kinp, ken=ken, kov=kov,
              grid=(grid6[0], grid6[-1], len(grid6)), d11=(d11_hot, d11_cold), N_F=N_F, BAND=BAND, GD=GD, cnr=cnr6, cnr_w=cnr_w,
              bounds={k_: (tfac(k_), esr_d[k_]) for k_ in CER_PARTS},
              csd_abs=csd_abs, ceff=dict(F25=bF_lo.C(25.0), F_lo=(bF_lo.C(36.0), bF_lo.C(75.0)), P_lo=(bP_lo.C(7.46), bP_lo.C(30.0)), S_lo=(bS_lo.C(7.46), bS_lo.C(30.0)),
                        C_hi=(bC_hi.C(7.46), bC_hi.C(30.0))),
              st=[s_[0] for s_ in st6], bk=[b_[0] for b_ in bk6], rt=[(id_, t_) for id_, t_, _f in RT6],
              valsA=[(id_,) + f_(WA) for id_, _t, f_ in RT6], vals1=[(id_,) + f_(W1u) for id_, _t, f_ in RT6],
              WD1=evD[grid6.index(min(grid6, key=lambda x_: abs(x_ - 1.0e-6)))], ibias_sum=ibias_sum, lim_err=lim_err,
              be115=csd_abs / r59_hi - i_op, d59_115=(i_op + A115) * r59_hi, d59_116=(i_op + 10.0) * r59_hi)
    # ================================================================== B6 ROUND 3: route 3, the sense moved off the stage's input capacitance
    # The coordinator's one design-convergence attempt (2 October 2026, evening). What RSENSE1 carries is the current into whatever
    # sits behind it: a stiff source arriving with the guard on charges that capacitance at a rate the loop sets (B6), and in
    # operation M1 draws its pulsed current from it (8705af p.27). The sheet asks for the input ceramics at the MOSFETs (p.36) and
    # for the sense differential inside its +-100 mV operating range (p.5, the full-range row; p.31). So the capacitance behind
    # RSENSE1 is bounded from above by the transient and from below by the operating range, and route 3 asks whether any split
    # of the input ceramics satisfies both. The printed statements the question rests on:
    r3_ec = RP.ec_row(pages, 5, "CSPIN, CSNIN Differential Operating Voltage Range", None)
    for pg_, pat_, what_ in ((31, r"should be kept below 100mV due to the limited amount of current that can be driven out of IMON_IN", "p.31 the 100 mV"),
                             (31, r"the input current often has ripple and discontinuities depending on the LT8705A.s region of operation", "p.31 ripple and discontinuities"),
                             (36, r"Connect the input capacitors, CIN, and output capacitors, COUT, closely to the power MOSFETs\. These capacitors carry the MOSFET AC current in the boost and buck regions", "p.36 CIN at the MOSFETs"),
                             (27, r"Discontinuous input current is highest in the buck region due to the M1 switch toggling on and off", "p.27 the buck region's input current"),
                             (27, r"A ceramic capacitor, of at least 1.F, should also be placed from VIN to GND as close to the LT8705A pins as possible", "p.27 the VIN bypass"),
                             (26, r"Typical values are 20ns to 40ns depending on the MOSFET capacitance and VIN voltage", "p.26 tRF1"),
                             (36, r"Route current sense traces \(CSP/CSN, CSPIN/CSNIN, CSPOUT/CSNOUT\) together with minimum PC trace spacing", "p.36 the sense traces"),
                             (36, r"Ensure accurate current sensing with Kelvin connections at the RSENSE resistors", "p.36 Kelvin")):
        need(raw[pg_], pat_, "8705af " + what_)
    xal_ = pg(XAL, 1, True)
    need(xal_, r"Part number1\s+\u00b120% \(\u00b5H\)", "XAL1510 p.1 the inductance tolerance header")
    xrow_ = need(xal_, r"XAL1510-103ME_\s+10\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "XAL1510 p.1 the 10 uH row").groups()
    gen_txt_ = open(os.path.join(TOP, GEN_E), encoding="utf-8").read()
    need(gen_txt_, r'_intent\.rail\("VIN_RAW", 12\.0, _VIN_T, _VIN_P', "board E's declared VIN_RAW 12.0 V")
    need(gen_txt_, r'part\("L1", "Device", "L", "10uH Coilcraft XAL1510-103MED \(Isat 26 A', "board E's L1")
    V_OP = (r3_ec["min"] * 1e-3, r3_ec["max"] * 1e-3)        # the sense differential's operating range, V
    L1_LO = 10e-6 * 0.80                                      # L1 at the XAL1510's -20 %
    F_LO = float(fosc[0]) * 1e3                               # the oscillator's least at RT 215k
    T_RF = 20e-9                                              # p.26: tRF1 typically 20 to 40 ns; the least typical taken, no minimum is printed
    L59_H = 5e-9      # RSENSE1's own inductance: Vishay's WSL prints 0.5 to 5 nH (held sheet p.1); the Milliohm HoJLR2512 prints none, ASSUMPTION at that bound
    L_TAP = 0.5e-9    # layout obligation (declared): each Kelvin tap at its pad and the ceramics at the pad, at most 0.5 nH between a tap and the plates
    L_KEL = 1.0e-9    # layout obligation (declared): the CSPIN/CSNIN pair routed together (p.36), its loop at most 1 nH
    V_OUTS = (12.0, v_out)                                    # the bus the stage delivers into: VIN_RAW's declared 12.0 V, and the drawn 15.1 V setpoint
    C_NOM3 = {"CL31B106KBHNNN": 10e-6, "CL32B106KBJNNN": 10e-6, "CL32B225KCJSNN": 2.2e-6}
    esl_d = {pn_: 1.0 / ((2 * math.pi * min(SAM[pn_]["z_MHz_ohm"], key=lambda p_: p_[1])[0] * 1e6) ** 2 * C_NOM3[pn_]) for pn_ in CER_PARTS}
    srf_d = {pn_: min(SAM[pn_]["z_MHz_ohm"], key=lambda p_: p_[1])[0] for pn_ in CER_PARTS}
    esl_max = max(esl_d.values())

    def op_bank(parts_, v_, side_):
        """(C, ESR, ESL) of a bank at the switching frequency: the parts' capacitance at v_ on the side the question needs (the
        record's bounds), the maker's typical ESR at F_LO (ESR_CER for a part with no curve), the ESL from each part's
        self-resonance (the largest held for a part with no curve), the tap inductance added."""
        c_ = CerBank([part(n_, cn_, pn_, side_) for n_, cn_, pn_ in parts_]).C(v_)
        g_ = sum(n_ / (interp(SAM[pn_]["esr_MHz_ohm"], F_LO / 1e6) if pn_ else ESR_CER) for n_, cn_, pn_ in parts_)
        gl_ = sum(n_ / (esl_d[pn_] if pn_ else esl_max) for n_, cn_, pn_ in parts_)
        return (c_, 1.0 / g_, 1.0 / gl_ + L_TAP)
    UP_A = [(N_CA, 10e-6, "CL32B106KBJNNN")]
    DOWN_A = [(2, 10e-6, "CL31B106KBHNNN"), (1, 4.7e-6, None), (1, 0.1e-6, None)]
    UP_3 = UP_A + [(2, 10e-6, "CL31B106KBHNNN"), (1, 4.7e-6, None)]
    C64_ = [(1, 0.1e-6, None)]
    splits = (("A, as drafted: C71 to C74 ahead, C13 to C15 and C64 behind", UP_A, DOWN_A),
              ("route 3: everything ahead, C64 alone behind", UP_3, C64_),
              ("route 3: one CL32B225KCJSNNE (2.2 uF) and C64 behind", UP_3, [(1, 2.2e-6, "CL32B225KCJSNN")] + C64_),
              ("route 3: two CL32B225KCJSNNE and C64 behind", UP_3, [(2, 2.2e-6, "CL32B225KCJSNN")] + C64_),
              ("route 3: one CL32B106KBJNNNE (10 uF) and C64 behind", UP_3, [(1, 10e-6, "CL32B106KBJNNN")] + C64_),
              ("route 3: two CL32B106KBJNNNE and C64 behind", UP_3, [(2, 10e-6, "CL32B106KBJNNN")] + C64_),
              ("Figure 1: nothing ahead but the bank, everything behind", None, UP_3 + C64_))
    bulk_op = bulks["new_20"]                                 # the bulk new, at 20 C: the most it can take of the pulse ahead of RSENSE1
    r3rows = []
    for lab_, up_, dn_ in splits:
        g3_ = dict(GA, bS=CerBank([part(n_, cn_, pn_, "lo") for n_, cn_, pn_ in (up_ or [(1, 1e-12, None)])]),
                   bC=CerBank([part(n_, cn_, pn_, "hi") for n_, cn_, pn_ in dn_]), esrS=ESR_CER / (sum(n_ for n_, _c, _p in up_) if up_ else 1), l59=L59_H)
        tr_ = {}
        for L_ in (0.30e-6, 1.0e-6, 3.3e-6):
            W3_ = evalR(L_, g3_)
            ok3_ = ok6(W3_)
            tr_[L_] = dict(u5=W3_["u5"], u5n=W3_["u5n"], vF=W3_["vF"], vS=W3_["vS"], i4=W3_["i4"], iQ=W3_["iQ"], di59=W3_["di59"], vds=W3_["vds"], slew=W3_["slew"],
                           inp=W3_["vF"] * kinp, di_up=W3_["di59_up"], di_dn=W3_["di59_dn"],
                           pins_hi=W3_["u5L"] + ERR[0] + L_KEL * W3_["di59_up"], pins_lo=W3_["u5Ln"] - ERR[0] + L_KEL * W3_["di59_dn"],
                           ok=all(ok3_.values()) and W3_["mono"], fails=sorted(id_ for id_, v_ in ok3_.items() if not v_))
        cu_ = None if up_ is None else op_bank(up_, v_oc, "hi")
        cd_ = op_bank(dn_, v_oc, "lo")
        op_ = {}
        for vo_ in V_OUTS:
            for ii_ in (i_reg_hi, i_op):
                op_[(vo_, ii_)] = sense_ripple(cu_, cd_, ii_, v_oc, vo_, F_LO, L1_LO, T_RF, r59_hi, L59_H, rb_lo, bulk_op)
        r3rows.append(dict(lab=lab_, up=up_, dn=dn_, cu=cu_, cd=cd_, tr=tr_, op=op_,
                           op_peak=max(o_["peak"] for o_ in op_.values()), op_trough=min(o_["trough"] for o_ in op_.values()),
                           r_peak_reg=max(o_["r_peak"] for (vo_, ii_), o_ in op_.items() if ii_ == i_reg_hi),
                           r_peak_trip=max(o_["r_peak"] for (vo_, ii_), o_ in op_.items() if ii_ == i_op),
                           low_reg=max(1.0 - o_["avg_clip"] / o_["avg"] for (vo_, ii_), o_ in op_.items() if ii_ == i_reg_hi),
                           low_trip=max(1.0 - o_["avg_clip"] / o_["avg"] for (vo_, ii_), o_ in op_.items() if ii_ == i_op)))
    # the hold's own operating point (17.6 V in, the drawn setpoint out), for the as-drafted split: where the sense is smooth enough
    op_hold = sense_ripple(r3rows[0]["cu"], r3rows[0]["cd"], i_reg_hi, lo_h, v_out, F_LO, L1_LO, T_RF, r59_hi, L59_H, rb_lo, bulk_op)
    op_edge = sense_ripple(r3rows[0]["cu"], r3rows[0]["cd"], i_reg_hi, v_oc, 12.0, F_LO, L1_LO, 10e-9, r59_hi, L59_H, rb_lo, bulk_op, dt=0.5e-9)
    op_noesl = sense_ripple((r3rows[0]["cu"][0], r3rows[0]["cu"][1], 0.0), (r3rows[0]["cd"][0], r3rows[0]["cd"][1], 0.0), i_reg_hi, v_oc, 12.0, F_LO, L1_LO, T_RF, r59_hi, 0.0, rb_lo, bulk_op)
    # the verification of the periodic model: a huge bank behind reads the average; a huge bank ahead and none behind reads M1
    vf1_ = sense_ripple(r3rows[0]["cu"], (1.0, 1e-4, 0.0), i_reg_hi, v_oc, 12.0, F_LO, L1_LO, T_RF, r59_hi, L59_H, rb_lo, bulk_op, periods=8)
    vf2_ = sense_ripple((1.0, 1e-4, 0.0), (1e-9, 1e-4, 0.0), i_reg_hi, v_oc, 12.0, F_LO, L1_LO, T_RF, r59_hi, 0.0, rb_lo, bulk_op, periods=8)
    if not (abs(vf1_["peak"] - vf1_["trough"]) < 0.002 and abs(vf2_["r_peak"] - vf2_["i_p"] * r59_hi) < 1e-6):
        refuse(4, "B6 round 3: the periodic model fails its limits: %s %s" % (vf1_, vf2_))
    # the floors of the splits that hold U5 at 0.30 uH, over the whole grid (no refusal: a rating that never holds reads None)

    def floor_r3(g_):
        evs_ = [evalR(L_, g_) for L_ in grid6]
        oks_ = [ok6(e_) for e_ in evs_]
        ls_ = {}
        for id_, _t, _f in RT6:
            j_ = len(grid6)
            while j_ > 0 and oks_[j_ - 1][id_]:
                j_ -= 1
            ls_[id_] = None if j_ == len(grid6) else (grid6[j_] if j_ > 0 else 0.0)
        return ls_
    r3_floors = {}
    for row_ in (r3rows[1], r3rows[2], r3rows[6]):
        g3_ = dict(GA, bS=CerBank([part(n_, cn_, pn_, "lo") for n_, cn_, pn_ in (row_["up"] or [(1, 1e-12, None)])]),
                   bC=CerBank([part(n_, cn_, pn_, "hi") for n_, cn_, pn_ in row_["dn"]]), esrS=ESR_CER / (sum(n_ for n_, _c, _p in row_["up"]) if row_["up"] else 1))
        r3_floors[row_["lab"]] = floor_r3(g3_)
    # route 3's verdict (SESSION): it holds only if, at 0.30 uH, every rating holds with its margin, U5 with the numerical error and
    # the parasitics' budget added, AND the sense stays inside its printed operating range in operation at the 25 V corner
    V_OP_M = V_OP[1] * (1 - M_OTHER)
    for row_ in r3rows:
        t3_ = row_["tr"][0.30e-6]
        row_["holds_u5"] = ("u5p" not in t3_["fails"] and "u5n" not in t3_["fails"] and t3_["pins_hi"] <= csd_abs and t3_["pins_lo"] >= -csd_abs)   # U5 alone, with RSENSE1's inductance and the Kelvin pickup
        row_["holds_tr"] = t3_["ok"] and row_["holds_u5"]                                  # every rating with its margin
        row_["holds_op"] = row_["r_peak_reg"] <= V_OP_M and row_["op_peak"] <= V_OP_M and -row_["op_trough"] <= V_OP_M
        row_["holds"] = row_["holds_tr"] and row_["holds_op"]
    # the selected network at its floor with RSENSE1's inductance: the pins read R i + L di/dt, the rise adding to the positive peak and
    # Q12's turn-off (the current collapsing within the gate's fall) swinging it negative; the largest inductance the margin holds for
    W_LA = evalR(LA, dict(GA, l59=L59_H))
    parA = dict(up=W_LA["di59_up"], dn=W_LA["di59_dn"], hi=W_LA["u5L"] + ERR[0] + L_KEL * W_LA["di59_up"], lo=W_LA["u5Ln"] - ERR[0] + L_KEL * W_LA["di59_dn"],
                l_up=L59_H * W_LA["di59_up"], l_dn=L59_H * W_LA["di59_dn"], k_up=L_KEL * W_LA["di59_up"], k_dn=L_KEL * W_LA["di59_dn"])
    l59_scan = []
    for l_ in (0.5e-9, 1e-9, 1.5e-9, 2e-9, 3e-9, 5e-9):
        Wl_ = evalR(LA, dict(GA, l59=l_))
        hi_, lo_ = Wl_["u5L"] + ERR[0] + L_KEL * Wl_["di59_up"], Wl_["u5Ln"] - ERR[0] + L_KEL * Wl_["di59_dn"]
        l59_scan.append((l_, hi_, lo_, lo_ >= -U5_LIM))         # ok: the turn-off's excursion inside the margin line (the side the inductance governs)
    l59_ok = max([l_ for l_, _h, _l, ok_ in l59_scan if ok_], default=None)
    op_l59 = {l_: sense_ripple(r3rows[0]["cu"], r3rows[0]["cd"], i_reg_hi, v_oc, 12.0, F_LO, L1_LO, T_RF, r59_hi, l_, rb_lo, bulk_op) for l_ in (1e-9, 2e-9, 5e-9)}
    b6["r3"] = dict(l59_scan=l59_scan, l59_ok=l59_ok, op_l59=op_l59, W_LA=dict((k_, W_LA[k_]) for k_ in ("u5", "u5n", "u5L", "u5Ln", "di59_up", "di59_dn")),
                    V_OP=V_OP, L1_LO=L1_LO, xrow=xrow_, F_LO=F_LO, T_RF=T_RF, L59=L59_H, L_TAP=L_TAP, L_KEL=L_KEL, esl=esl_d, srf=srf_d, V_OUTS=V_OUTS,
                    rows=r3rows, floors=r3_floors, op_hold=op_hold, op_edge=op_edge, op_noesl=op_noesl, vf=(vf1_, vf2_), parA=parA, di59A=WA["di59"],
                    i_reg_hi=i_reg_hi, i_op=i_op, bulk_op=bulk_op, holds=any(r_["holds"] for r_ in r3rows), V_OP_M=V_OP_M, v_oc=v_oc, lo_h=lo_h, t_f=t_f6,
                    edge_spike=(esl_max + L_TAP) * (r3rows[0]["op"][(12.0, i_reg_hi)]["i_v"] / T_RF))
    verd2 = [
        dict(id="D4", name="a stiff 36 V source, connected cold", ok=st_min > 1e-3 and f36["cut_hi"] < v_src and f36["d4_room"] > 0 and v_src < D11["vr"]
             and cold_ok and f36["en"] <= 15.0 and f36["inp"] < T48["pin_abs"]),
        dict(id="D5", name="a reversed panel", note=" (CONDITIONAL on Q13's leakage above 25 C)", ok=rev["vds"] < QF["vds"] and rev["i_be"] > rev["idss"] and rev["ring"] < QF["vds"]),
        dict(id="CS116/115 on", name="CS116 and CS115 with the block on", note=" (CS115 CONDITIONAL on R-174: its loop current under %.2f A, or U5's differential measured under %.1f V)" % (b6["be115"], csd_abs),
             ok=scp_f < scp_lo and v_tmr < T48["tmr_v"][0] and ov_in116 < bandA["rise"][0] and D4N["v116"] <= lim_draft and b6["d59_116"] < csd_abs),
        dict(id="CS116/115 off", name="CS116 and CS115 with the block off", ok=off116["v"] < QF["vds"] and off116["en"] <= 15.0 and off116["inp"] < T48["pin_abs"] and off116["floor"] > -1.0),
        dict(id="already on", name="a stiff 36 V source with the guard on (B6)",
             note=" (round 2: every rating with its margin for a source loop of at least %.2f uH, NOT MET below it; no approach within the makers' printed rules removes that floor: the engineer's row B6-ENG-1)" % (1e6 * b6["LA"]),
             ok=False, holds=gate_load < T48["cl"] and all(ok6(b6["W"]).values()) and b6["W"]["mono"] and ramp_ok and b6["W"]["soa12"] < 1.0
             and b6["W"]["soa13"] < 1.0 and e11_6 < e11_room and b6["i_cs"] < ics_abs and bool(b6["fail1"]) and b6["LD"] < b6["LA"]),
        dict(id="window", name="the window kept", ok=bandA["rise"][0] > cs101_pk and bandA["fall"][0] > v_oc and max(L11["uv"][2], inp_on6) < float(shdn_txt)
             and i_start6 < ocp_lo
             and p_static_blk < p_win and t_allow_blk >= T_FAC * c["t_resp_typ"] and i_bank_slew < c["i_lo_aged"]
             and max(cs_re[k_]["worst"][2] for k_ in ("least", "most")) < best["m"]),
    ]
    if [v_["ok"] for v_ in verd2] != [True, True, True, True, False, True] or not verd2[4]["holds"] or min(ov28["aged"]["m"]) >= 0 or d4n != 30:
        refuse(4, "the remedy's verdicts are not the ones the record states: %s, SMCJ28A aged %.3f, D4 SMCJ%dA" % (
            [(v_["id"], v_["ok"]) for v_ in verd2], min(ov28["aged"]["m"]), d4n))
    rem["verd"] = verd2
    rem["b6"] = b6
    R["remedy"] = rem
    # ---- the single faults (for layer 8's fault analysis; this record assigns them, it does not close them)
    faults = dict(
        defeat=["U18's output stuck low or open, or R65 open (no current reaches R66)", "R66 shorted", "U19's OUTB stuck open (high impedance)",
                "U20's RESET stuck open, or its MR input stuck high", "a short across the sense bank", "U5's SWEN input failed active",
                "a capacitor of the INB filter shorted (INB held at ground)"],
        guard=["R71 open (SWEN then follows TRK_LDO33 when RESET is released: the trip still acts through RESET, the supply guard is lost)"],
        stop=["U19's OUTA or OUTB stuck low", "U20's RESET stuck low", "R70 open (SWEN held to ground by R71)", "U18's output stuck high",
              "the whole sense bank open (one part open only raises the bank's resistance: the trip falls, charging continues)",
              "TRK_LDO33 lost (SWEN under its threshold by the divider, U20 holds the stage off above it)",
              "a ceramic of C71 to C74 shorted (TRK_VS to ground: the panel into a short through the bank, F2 above the panel's current)",
              "a capacitor of the INB filter open (less filtering: the trip may act under CS101's ripple; the bound is unchanged)",
              "a bulk can shorted (PV_P to ground ahead of the bank: the panel into a short, F2 above the panel's current)"],
        acceptance="Layer 8 lists each fault above with its effect; acceptance: no single fault both defeats the backstop and removes "
                   "the LT8705A's own input-current limit (a defeated backstop leaves the regulation, which holds the stage under the "
                   "trip when its unprinted values are inside the joint assumptions), and every fault that defeats the backstop or its "
                   "supply guard is found by the commissioning and periodic trip test (bench row 7b.15) at an interval layer 8 sets")
    # ---- the series disconnect, evaluated and not taken (the check's suggestion; SESSION)
    disc = dict(vcl=(float(vcl69[0]), float(vcl69[1]), float(vcl69[2])), vin_test=48.0,
                why="the LM5069 class hot-swap controller prints its current limit (VCL %s / %s / %s mV) at VIN = 48 V, not at the "
                    "panel's 17 to 25 V, and its spread (%.0f %% from typical to either end) would push the regulation further down than "
                    "C's; SWEN already removes the path from the panel to the pack (the four switches stop and M1's body diode blocks "
                    "the input), and the input capacitors' charge is bounded as an event (check (b)). A series FET would cover a shorted "
                    "switch of the LT8705A, a single fault layer 8 judges" % (vcl69[0], vcl69[1], vcl69[2], 100 * (float(vcl69[2]) / float(vcl69[1]) - 1)))
    # ---- the verdict on the present control (unchanged reading of section 9)
    verdict = dict(shown=False, depends=[(r_["id"], r_["breakeven"]) for r_ in R["qual_rows"] if r_["bound"] and not r_["resolved"]])
    terms = [
        ("U19 TPS3701 INB rising threshold, TJ -40 to 125 C, VDD 1.8 to 36 V", "397 to 403 mV", "warranted", "TPS3701 SBVS240C p.5"),
        ("U19 input current at INB, through R66", "+-%.0f nA" % (iin_t * 1e9), "warranted", "p.5"),
        ("U18 INA169 transconductance, VSENSE 10 to 150 mV, at V+ = 5 V, VIN+ = 12 V, ROUT = 25 kOhm", "%.0f to %.0f uA/V" % (gm169[0] * 1e6, gm169[1] * 1e6), "warranted", "INA169 SBOS181F p.6"),
        ("its nonlinearity", "+-%.1f %%" % (100 * nl169), "warranted", "p.6"),
        ("its offset referred to the input, at the same point", "+-%.0f mV" % (vos169 * 1e3), "warranted", "p.6"),
        ("its output's move from VIN+ = 12 V to 25 V, at VSENSE = 50 mV (CMR)", "%.0f dB minimum: %.0f uV" % (cmr169, 1e6 * 10 ** (-cmr169 / 20.0) * 13.0), "warranted (at 50 mV)", "p.6, VIN+ 2.7 to 60 V"),
        ("its output's move from V+ = 5 V to 25 V, at VSENSE = 50 mV (PSR)", "%.0f uV/V: %.0f uV" % (psr169 * 1e6, psr169 * 20.0 * 1e6), "warranted (at 50 mV)", "p.6, V+ 2.7 to 60 V"),
        ("the same move at the trip's own VSENSE (%.3f to %.3f mV): G_CM x |VSENSE - 50 mV|" % (1e3 * c["vs_lo"], 1e3 * c["vs_hi"]), "G_CM %.0f %%: %.1f uV" % (100 * G_CM, 1e6 * c["vs_parts"]["d1"]), "assumption", "no row; break-even printed"),
        ("the load R65 + R66 (%.2fk nominal, %.2fk to %.2fk with tolerance, drift and aging) against the 25 kOhm of the gain row" % (c["r_load"][0] / 1e3, c["r_load"][1] / 1e3, c["r_load"][2] / 1e3),
         "%.4f uV through the 1 GOhm output impedance" % (1e6 * c["vs_parts"]["dl"]), "documented dependency (typical row)", "p.6"),
        ("R66 %gk, 0.1 %%, 25 ppm/K over %.0f K, the printed solder-heat and life limits" % (R66 / 1e3, dt_end), "+-(0.5 % + 0.05 Ohm) each", "warranted (printed test limits)", "YAGEO RT V.16 pp.2, 7, 8"),
        ("the bank, %d x %s in parallel: 1 %%, %.0f ppm/K from -55 to +155 C" % (nb, bmodel, wtcr * 1e6), "%.4f mOhm" % (rbank * 1e3), "warranted", "Vishay WSL 30100 pp.1, 2"),
        ("the bank's solder-heat and load-life test limits", "+-(%s %% + %s Ohm) and +-(%s %% + %s Ohm) per part" % (wsold[0], wsold[1], wlife[0], wlife[1]), "warranted (printed test limits)", "WSL 30100 p.3"),
        ("R8 and R9 (the hold draft's RT parts) across 25 V, bypassing the bank", "%.2f mW" % (1e3 * v_oc ** 2 / r89_min), "warranted", "YAGEO RT V.16"),
        ("U18's VIN+ pin: its output current, bypassing the bank", "%.2f mW at 25 V" % (1e3 * v_oc * c["vs_hi"] * gm169[1] * (1 + nl169)), "warranted (from the rows above)", "p.6"),
        ("U18's VIN+ input bias (10 uA typical, no maximum printed)", "I_B169 %.0f mA: %.0f mW at 25 V" % (I_B169 * 1e3, 1e3 * v_oc * I_B169), "assumption", "no row; break-even printed"),
    ] + ([("the bulk's DC leakage, bypassing the bank (it is ahead of it)", "%.2f mW at 25 V" % (1e3 * v_oc * 3 * leak_za), "warranted", "ZA p.1, 0.01 CV after 2 minutes")]
         if LAYOUT == "ahead" else []) + [
        ("the input voltage at most 25 V", "REQ-016", "requirement", "REQ-016"),
    ]
    c["terms"] = terms
    R["decision"] = dict(
        verdict=verdict, chosen="C", w_avg=W_AVG, e_now=e_now, e_free=e_free, p_noon_now=p_noon_now, ta12=ta12,
        basis=dict(boundary="board E's panel entry (J_SOLAR, PV_IN): F2, the sense bank, the bulk, the ceramics and the LT8705A stage behind it",
                   window_printed=False, vm=list(q16["verification_method"]), lead_hits=len(lead_hits)),
        approaches=[
            dict(id="A", name="the present control with argued margins (the IMON_IN fault comparator bounds EA2; RIMON_IN raised)",
                 bound=a_["bound"], status="CONDITIONAL", setting=(rm_a[0], rm_a[1], a_["inom"]), energy=a_["energy"], independent=False,
                 noon_red=a_["noon_red"], cur_red=a_["cur_red"], loss=(0.0, 0.0),
                 classes={"warranted": ["IMON_IN fault maximum 1.67 V (8705af p.5, full range)", "RSENSE1 1 % and RIMON_IN 0.1 %", "the resistors' printed drifts"],
                          "assumption": ["A7 at its test-point limits away from its test point", "the fault threshold's VIN dependence (twice the reference's printed line regulation)",
                                         "RSENSE1's cold TCR at 100 ppm/K", "the fault comparator's response and restart, which print no timing"]},
                 parts="none added; R16 to %gk (%s)" % (rm_a[0] / 1e3, rm_a[1]),
                 failure="a regulation point past the fault minimum turns limiting into the fault's hiccup (switching stops: energy, not the bound)",
                 depends="Analog Devices (A7 away from its test point, the fault threshold away from VIN = 12 V, the fault's timing) and Milliohm (the cold TCR)",
                 surge="no part added; the entry needs the same correction as C"),
            dict(id="B", name="the INA250A2 (its own 2 mOhm shunt) with the same trip chain as C (TPS3701 into a TPS3808 on SWEN)",
                 bound=b["p_static"], status="CONDITIONAL", setting=(b["rm"][0], b["rm"][1], b["inom"]), energy=b["energy"], independent=False,
                 noon_red=b["noon_red"], cur_red=b["cur_red"], loss=b["loss"],
                 classes={"warranted": ["the TPS3701 and TPS3808 rows", "the divider's RT rows", "the offset's supply and common-mode rows (at ISENSE = 0 A)"],
                          "conditional": b["conditional"]},
                 parts="U18 INA250A2PWR, the trip chain of C, R60 28k and R61 7.87k; R16 to %gk" % (b["rm"][0] / 1e3),
                 failure="as C; and its integrated shunt carries the surge with the amplifier",
                 depends="Texas Instruments (the rows at VS = 3.3 V and VREF = 0 V, the stress rows); the coordination with Analog Devices and Milliohm",
                 surge="FAILS: U18's inputs are rated %.0f V and the capability scenario clamps at up to %.1f V" % (abs_ina, d4["vc"])),
            dict(id="C", name="a WSL2512 sense bank read by an INA169 into a TPS3701, a TPS3808 supervisor holding SWEN low",
                 bound=c["p_static"], status="CONDITIONAL", setting=(rc_[0], rc_[1], c["inom"]), energy=c["energy"], independent=False,
                 noon_red=c["noon_red"], cur_red=c["cur_red"], loss=c["loss"],
                 classes={"warranted": [t_[0] for t_ in terms if t_[2].startswith("warranted")],
                          "assumption": [t_[0] for t_ in terms if t_[2] == "assumption"],
                          "documented dependency": [t_[0] for t_ in terms if t_[2].startswith("documented")],
                          "requirement": ["the input voltage at most 25 V (REQ-016)"]},
                 parts="U18 INA169NA/3K, U19 TPS3701DDCR, U20 TPS3808G33DBVR, R60 to R64 (%d x %s), R65 16.9k, R66 %gk, R67 110k, R68 9.53k, "
                       "R69 100k, R70 8.06k, R71 6.04k, C66 to C68 100n, C71 to C74 10u 50V; C11, C12 and C69 the 50 V bulk; R16 to %gk" % (nb, bmodel, R66 / 1e3, rc_[0] / 1e3),
                 failure="a hiccup if the regulation's unprinted values exceed the joint assumptions (energy, not the bound); the single faults of the fault list",
                 depends="Texas Instruments for the two assumptions (G_CM and I_B169, each with its break-even); Analog Devices and Milliohm for the coordination and the energy; Vishay for the bank's pulse capability (the capability scenario only)",
                 surge="every part inside its rating at the approved levels and in the capability scenario; U5's sense differential at most %.4f V (MODELED, lumped)" % worst["d59"]),
        ],
        c=c, b=b, a=a_, seq=seq, surge=surge, faults=faults, disc=disc,
        rows=dict(st_t=st_t, vth=vth, vtha=vtha, iin_t=iin_t, vol_max=vol_max, tpd_lh=tpd_lh, uvlo_t=uvlo_t, vdd_t=vdd_t, vit38=vit38, acc38=acc38,
                  hys38=hys38, td38=td38, mr_ns=mr_ns, gm169=gm169, vos169=vos169, cmr169=cmr169, psr169=psr169, nl169=nl169,
                  iq169=iq169, sw169=sw169, swcm169=swcm169, ipin169=ipin169, bw169=bw169, ro169=ro169, ts169=ts169, v_ldo=v_ldo, ilim33=ilim33,
                  swen=(swen_r["min"], swen_r["max"]), d4=d4, za=za, wtcr=wtcr, wsold=wsold, wlife=wlife, amps_pk=amps_pk, fosc=fosc,
                  r65=R65, r66=R66, r67=R67, r68=R68, r69=R69, r70=R70, r71=R71, stock169=lc169["stock"], stock38=lc38["stock"],
                  stock_tps=lc_tps["stock"], stockza=lcza["stock"], isc_hot=isc_hot, tol_p=tol_p, t_air=t_air, t_cold=t_cold, rs=rs,
                  zband=zband, zfac=zfac))
    # the clarification drafts after the decision: no answer moves C's bound; Analog Devices' and Milliohm's answers set the coordination
    # and the energy; the Texas Instruments draft now asks about the INA169's VIN+ pin current only (supporting, not needed)
    ti_p, ad_p = os.path.join(TOP, CLAR, "texas-instruments-ina169.txt"), os.path.join(TOP, CLAR, "analog-devices-lt8705a.txt")
    if not os.path.isfile(ti_p) or os.path.isfile(os.path.join(TOP, CLAR, "texas-instruments-ina250.txt")):
        refuse(3, "the clarification drafts do not follow the decision (the INA169 draft, no INA250 draft)")
    ti_t, ad_t = open(ti_p, encoding="utf-8").read(), " ".join(open(ad_p, encoding="utf-8").read().split())
    if not ti_t.startswith("DRAFT FOR THE OWNER TO SEND.") or "INA169" not in ti_t:
        refuse(3, "the clarification text texas-instruments-ina169.txt does not read as a draft naming its part")
    if "SWEN" not in ad_t or "input current" not in ad_t:
        refuse(3, "the Analog Devices draft does not carry the SWEN question")
    # the drafts quote this round's figures; a stale figure refuses (each as the draft words it)
    vi_p = os.path.join(TOP, CLAR, "vishay-wsl2512.txt")
    vi_t = " ".join(open(vi_p, encoding="utf-8").read().split()) if os.path.isfile(vi_p) else ""
    ti_f = " ".join(ti_t.split())
    sg_, sq_ = R["decision"]["surge"], R["decision"]["seq"]
    cap_ = max((x_ for x_ in sg_["cases"] if x_["kind"] == "capability"), key=lambda x_: x_["ibank"])
    want_f = [(ti_f, "at our %.1f mV highest trip is %.1f uV referred to the input" % (1e3 * c["vs_hi"], 1e6 * c["vs_parts"]["d1"])),
              (ti_f, "reaches its limit only if that change exceeds 500 %" if c["g_cm_be_b"] >= 4.99 else
               "reaches its limit only if that change reaches about %.0f %%" % (100 * round(c["g_cm_be_b"], 1))),
              (ti_f, "reaches its limit only at about %.0f mA" % (10 * round(100 * c["i_b_be_b"]))),
              (ti_f, "may reach about %.2f V for tens of nanoseconds and %.2f V for about a millisecond" % (sg_["d169"], cap_["ibank"] * sg_["rb_hi"])),
              (vi_t, "of up to %.1f A peak, about %.1f mJ in the part" % (cap_["ibank"] / nb, 1e3 * sg_["e_part"])),
              (ad_t, "cannot reach its threshold below about %.2f V on LDO33" % sq_["guard_v"]),
              (ad_t, "under about %.0f uA sourced and %.0f uA sunk" % (1e6 * sq_["i_sw_be"], 1e6 * sq_["i_sink_be"]))]
    stale = [w_ for f_, w_ in want_f if w_ not in f_]
    if not vi_t.startswith("DRAFT FOR THE OWNER TO SEND.") or stale:
        refuse(3, "a clarification draft does not quote this round's figures: %s" % "; ".join(stale))
    R["decision"]["clar"] = ["analog-devices-lt8705a.txt", "milliohm-hojlr2512.txt", "texas-instruments-ina169.txt", "vishay-wsl2512.txt"]
    # ================================================================== 9: what the drafts change (read back from each)
    R["models"] = {c_: v_["model"] for c_, v_ in lc.items()}
    R["drafts"] = {}
    for nm in ("apply_gen_sch_e_u5_grade.py", "apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py"):
        m = load(nm[:-3] + "_for_l4e7", "v2/docs/records/l4e7/" + nm)
        new = m.patched(gse)
        want = {"apply_gen_sch_e_u5_grade.py": ["C674169"], "apply_gen_sch_e_hold.py": [r8c, r9c],
                "apply_gen_sch_e_input_limit.py": [rs_code, rm_code, CIMON[2]]}[nm]
        R["drafts"][nm] = (len(m.EDITS), "R10" in "".join(o_ for o_, _r in m.EDITS), new.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1,
                           all(new.count('"%s")' % c_) > gse.count('"%s")' % c_) for c_ in want), want)
        if nm == "apply_gen_sch_e_input_limit.py":
            after_il = new
    # the backstop's draft edits the hold and input limit drafts' text: read back on top of both, its codes the decision's
    nm = "apply_gen_sch_e_backstop.py"
    m = load(nm[:-3] + "_for_l4e7", "v2/docs/records/l4e7/" + nm)
    base_ = load("hold_for_backstop", "v2/docs/records/l4e7/apply_gen_sch_e_hold.py").patched(after_il)
    new = m.patched(base_)
    cd_ = R["decision"]["c"]
    want = ["C44322", "C132788", "C43698", cd_["code"], "C178637", cd_["rm"][1], cd_["r66_code"], "C861156", "C728595"] + (["C170182"] if cd_["n_cf"] else ["C1588"])
    R["drafts"][nm] = (len(m.EDITS), "R10" in "".join(o_ for o_, _r in m.EDITS), new.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1,
                       all(new.count('"%s")' % c_) > base_.count('"%s")' % c_) for c_ in want), want)
    R["backstop_draft"] = dict(swen='"36": "TRK_SWEN"' in new, cspin='"33": "TRK_VS"' in new, r59='"TRK_VS", "TRK_VIN", "RS2512"' in new,
                               bank=('for _bk in range(%d): r("R6%%d" %% _bk, ' % cd_["n"]) in new and new.count('"PV_P", "TRK_VS", "RS2512", "%s")' % cd_["code"]) == 1,
                               r16=('r("R16", "%gk 0.1%%' % (cd_["rm"][0] / 1e3)) in new, d4='"1": "TRK_VS", "2": "GND"}, "C224047")' in new,
                               bulk=new.count('"C178637")') == 2 and 'part("C69", ' in new, r14='r("R14", "100k 1%", "TRK_VS", "TRK_SHDN")' in new,
                               ca='for _ca in range(%d): c("C7%%d" %% (_ca + 1), "10u 50V", "TRK_VS", "GND", "C10u50")' % cd_["n_ca"] in new,
                               c70=('for _cf in (%s): c(_cf, "100n NP0 50V", "TRK_BKS", "GND", "C10u50", "C170182")' % ", ".join(
                                   '"%s"' % x_ for x_ in (["C70", "C75", "C76", "C77", "C78", "C79"][:cd_["n_cf"]]))) in new if cd_["n_cf"]
                               else 'c("C70", "1n", "TRK_BKS", "GND", "C", "C1588")' in new,
                               bulk_at=new.count('{"1": "%s", "2": "GND"}, "C178637")' % ("PV_P" if cd_["layout"] == "ahead" else "TRK_VS")) == 2,
                               r66=('r("R66", "%gk 0.1%% 25ppm' % (cd_["r66"] / 1e3)) in new and ('"TRK_BKS", "GND", "R", "%s")' % cd_["r66_code"]) in new,
                               guard='r("R70", "8.06k 0.1% 25ppm (SWEN supply guard top)", "TRK_LDO33", "TRK_SWEN", "R", "C861587")' in new
                               and 'r("R71", "6.04k 0.1% 25ppm (SWEN pull-down, the guard bottom)", "TRK_SWEN", "GND", "R", "C728595")' in new,
                               no_series=new.count('"33": "TRK_VS"') == 1 and new.count('"32": "TRK_VIN"') == 1 and "CSPF" not in new)
    # the solar-fault remedies' draft, read back on top of the backstop's, L4-E9's hotswap and L4-E11's entry drafts (the order its
    # docstring names); its codes and its OV divider and clamp the remedy's own
    nm = "apply_gen_sch_e_solar_guard.py"
    m = load(nm[:-3] + "_for_l4e7", "v2/docs/records/l4e7/" + nm)
    base2 = load("hotswap_for_l4e7", "v2/docs/records/l4e9/apply_gen_sch_e_hotswap.py").patched(new)
    base2 = load("entry_for_l4e7", "v2/docs/records/l4e11/apply_gen_sch_e_entry.py").patched(base2)
    new2 = m.patched(base2)
    rm_ = R["remedy"]
    want = ["C17556513", "C473333", "C2985708", "C80273", "C124196", "C184799", "C97929", "C861872"] + list(rm_["ov_codes"])
    R["drafts"][nm] = (len(m.EDITS), "R10" in "".join(o_ for o_, _r in m.EDITS), new2.count('r("R10", "115k 1% (RFBOUT1: 15.1 V)"') == 1,
                       all(new2.count('"%s")' % c_) > base2.count('"%s")' % c_) for c_ in want), want)
    ovv = (rm_["ovs"]["a"], rm_["ovs"]["b"], rm_["ovs"]["rb"])
    R["guard_draft"] = dict(rtn='"VH2", {"1": "PV_IN", "2": "PV_RTN"}, "C274411")' in new2, f2='"FUSE", {"1": "PV_IN", "2": "PV_F"})' in new2,
                            ov=[m.OV_TOP_A, m.OV_TOP_B, m.OV_BOT] == [("%gk" % (v_ / 1e3), c_) for v_, c_ in zip(ovv, rm_["ov_codes"])],
                            d4=('"SMCJ%dA (panel surge' % rm_["D4N"]["n"]) in new2 and 'part("D4", "Device", "D_Zener", "SMCJ28A' not in new2,
                            switch='{"switch": "U21", "enable_net": "PV_UVLO"}),' in new2 and new2.count('"always_on_why": "a photovoltaic panel') == 0,
                            q13='"PV_RG", "PV_RTN", "GND", lcsc="C473333")' in new2, d11='{"1": "PV_F", "2": "PV_RTN"}, "C80273")' in new2,
                            rails=all(('_intent.rail("%s"' % n_) in new2 for n_ in ("PV_F", "PV_SNS", "PV_RTN")),
                            u21='"13": "PV_P", "14": "PV_GATE", "15": "PV_PU"' in new2 and '"2": "PV_OVLO"' in new2,
                            b6=all(new2.count(s_) == 1 for s_ in ('c("C131", "2.2u 100V X7R 1210 Samsung CL32B225KCJSNNE', 'for _cf in ("C132", "C135", "C136"): c(_cf, "2.2u 100V X7R 1210 Samsung CL32B225KCJSNNE',
                                                                  'c("C126", "330p C0G 100V', 'r("R97", "28.0k 1%', 'c("C133", "10u 50V X7R 1210 Samsung CL32B106KBJNNNE',
                                                                  'c("C134", "10u 50V X7R 1210 Samsung CL32B106KBJNNNE"', 'c("C7%d" % (_ca + 1), "10u 50V X7R 1210 Samsung CL32B106KBJNNNE'))
                            and '"1u 100V 1210 (panel port' not in new2 and 'c("C7%d" % (_ca + 1), "10u 50V", ' not in new2)
    return R


def render(R):
    o = []
    P = o.append
    END = R["ends"]
    P("L4-E7: REAL COMPONENT SETTINGS FOR BOARD E'S SOLAR STAGE (layer 4, MESHSAT-1357, 1 October 2026)")
    P("prototype design, desk arithmetic; nothing bought, built, powered or measured. Bases: MAKER, NETLIST, CATALOGUE, MODELED,")
    P("INFERRED, ASSUMPTION, SESSION, as named on each line")
    P("")
    P("0. REPRODUCTIONS (before any figure)")
    P("   0a l4e_replay.py in a child process reproduces l4e_replay.out byte for byte: %s" % ("yes" if R["r0a"] else "NO"))
    P("   0b l4e5_source_control.py in a child process reproduces l4e5_source_control.out byte for byte: %s" % ("yes" if R["r0b"] else "NO"))
    P("   0c l4e_replay.main() in-process, locals captured, prints l4e_replay.out byte for byte: %s" % ("yes" if R["r0c"] else "NO"))
    P("   (the functions used below are the replay's: i_factor, ec_row, pdf_lines, hold, trace, meanday, least; no git hash compared)")
    P("")
    P("1. BOARD E AS DRAWN (NETLIST v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net, pinned)")
    for f in R["facts"]:
        P("   - " + f)
    P("   gen_sch_e.py's R10 reads %sk; L4-E5 (its record, reproduced in 0b) raises it to %sk, ceiling %.2f / %.2f / %.2f V" % (
        R["r10_gen"], R["r10_5"], *R["ceil5"]))
    P("")
    P("2. THE MAKERS' ROWS USED")
    P("   LT8705A 8705af (v2/vendor/power/lt8705a.pdf): p.3 order table: grades in the drawn QFN (UHF): %s; H and MP only in the" % ", ".join(R["qfn"]))
    P("     TSSOP (FE); p.6 Note 3, its U+2013 minus written -:")
    for ln in textwrap.wrap("\"" + R["note3"] + "\"", 118):
        P("       " + ln)
    P("   p.4 IMON_IN regulation %.3f / %.3f / %.3f V (full range); line regulation max %.3f %%/V (25 C, VIN 12 to 80 V, not switching);" % (
        R["ref_p"]["min"], R["ref_p"]["typ"], R["ref_p"]["max"], R["line_p"]))
    P("     p.5 A7 gm E, I %.2f / %.2f mmho (full range), all grades %.2f / %.2f (25 C); EA2 gain %.0f V/V TYP only; p.4 FBIN E, I" % (
        R["gm_lo"], R["gm_hi"], R["a7"]["(All Grades)"]["min"], R["a7"]["(All Grades)"]["max"], R["ea2"]))
    P("     %.3f / %.3f / %.3f V (full range); EA3 gain %.0f V/V TYP only; p.5 IMON_IN fault %.2f / %.2f / %.2f V; IMON_IN output" % (
        R["fbin"]["min"], R["fbin"]["typ"], R["fbin"]["max"], R["ea3"], R["iovm"]["min"], R["iovm"]["typ"], R["iovm"]["max"]))
    P("     current at least %.0f uA; CSPIN-CSNIN differential %.0f to %.0f mV; p.31 CIMON_IN > %.0f / (f x RIMON_IN), 0.1 to 1 uF in a" % (
        R["ioutmin"], R["csd"]["min"], R["csd"]["max"], R["cim"]))
    P("     current loop; p.2 QFN theta-JA %.0f C/W; p.3 VIN quiescent %.1f mA max; p.6 fOSC at RT 215k up to %.0f kHz" % (
        R["tja"], R["iq"] * 1e3, R["f_max"] / 1e3))
    P("   Milliohm HoJLR2512 series (v2/vendor/passives/milliohm-hojlr2512-series.pdf, Ho-A0): p.1 F = +-1 %%; p.2 TCR +-%.0f ppm/K" % (R["tcr_h"] * 1e6))
    P("     (2 to 500 mOhm), 3 W derating from 70 C to 0 at 170 C (%.1f K/W, INFERRED as r11_dep.py); p.4 the TCR test spans +25 to" % R["k_r"])
    P("     +125 C only; soldering heat < +-%.1f %%; load life < +-%.0f %%" % (100 * R["sold_h"], 100 * R["life_h"]))
    P("   YAGEO RT series V.16, May 06 2025 (held: v2/vendor/passives/held/yageo-rt-series-v16-2025-05-06.pdf): p.2 B = +-%.1f %%," % (100 * R["tol_y"]))
    P("     D = %.0f ppm/K; p.7 TCR tested at +25/-55 C and +25/+125 C; life +-(%.1f %% + %.2f Ohm); p.8 soldering heat +-(%.1f %% + %.2f Ohm)" % (
        R["tcr_y"] * 1e6, 100 * R["life_y"][0], R["life_y"][1], 100 * R["sold_y"][0], R["sold_y"][1]))
    P("   Infineon BSC028N06NS Rev.2.1 p.3 (held) Qg max %.0f nC; BSC039N06NS Rev.2.4 p.4 Qg max %.0f nC (both VGS 0 to 10 V)" % (
        R["qg028"] * 1e9, R["qg039"] * 1e9))
    P("   the envelope (v2/ecad/tools/pcb_envelope.yaml): ambient in use %.0f to %.0f C (REQ-024, D-02a); worst inside air %.1f C" % (
        R["t_cold"], R["t_amb_hi"], R["t_air"]))
    P("")
    P("3. THE DECISIONS")
    P("   GRADE: LT8705AI in the drawn QFN (LT8705AIUHF#PBF, LCSC C674169; #TRPBF C674170), replacing the netlist's C674164")
    P("     (LT8705AEUHF#TRPBF, the E grade). The H and MP grades exist only in the TSSOP, which is not the drawn land. Of E and I,")
    P("     only I is GUARANTEED (tested) below 0 C junction; the kit starts cold at %.0f C ambient, so its junction range starts at" % R["t_cold"])
    P("     %.0f C. With I fixed, A7's limits are %.2f / %.2f mmho (the replay stacked H and MP's %.2f because no grade was named)." % (
        R["tj_cold"], R["gm_lo"], R["gm_hi"], R["a7"]["(LT8705AH, LT8705AMP)"]["min"]))
    P("     Hot end (INFERRED): INTVCC from EXTVCC on TRK_OUT up to L4-E5's %.2f V; gate charge 2 x %.0f + 2 x %.0f nC at %.0f kHz plus" % (
        R["ceil5"][2], R["qg028"] * 1e9, R["qg039"] * 1e9, R["f_max"] / 1e3))
    P("     %.1f mA: %.1f mA, %.2f W, TJ estimated about %.1f C (INFERRED) in %.1f C air with theta-JA %.0f C/W (%.1f C at the drawn output's %.2f V), under" % (
        R["iq"] * 1e3, R["i_g"] * 1e3, R["p_ic"], R["tj_hot"], R["t_air"], R["tja"], R["tj_hot_old"], R["out_drawn"][2]))
    P("     125 C.")
    P("     So the I grade's tested range, -40 to 125 C junction, covers %.0f to %.1f C. Catalogue: stock 0 at LCSC on 1 October 2026" % (
        R["tj_cold"], R["tj_hot"]))
    P("     (U5 is bench-fitted; another distributor)")
    P("   RSENSE1 (new, R59): %.0f mOhm, Milliohm HoJLR2512-3W-15mR-1%%, LCSC %s (stock %d): +-%.0f %% (CATALOGUE and MAKER p.1)," % (
        R["rs"] * 1e3, R["rs_code"], R["rs_stock"], 100 * R["tol_h"]))
    P("     +-%.0f ppm/K (MAKER p.2). Rule (SESSION): the family value that puts the zero-margin limit (%.3f A) nearest A7's printed" % (
        R["tcr_h"] * 1e6, R["i_zero"]))
    P("     50 mV test point (p.5), since no A7 offset row is printed; at the chosen setting %.1f mV" % (R["i_nom"] * R["rs"] * 1e3))
    P("   RIMON_IN (R16): %gk, YAGEO %s, LCSC %s (stock %d): +-%.1f %%, +-%.0f ppm/K (MAKER p.2, CATALOGUE)." % (
        R["rm"] / 1e3, R["models"][R["rm_code"]], R["rm_code"], R["rm_stock"], 100 * R["tol_y"], R["tcr_y"] * 1e6))
    P("     Rule (SESSION): the largest stocked RT0603BRD07 setting whose 25 V corner stays at or under 100 W at both ends with every")
    P("     printed limit, the resistors' printed soldering-heat and life drifts stacked, EA2's gain at 1/%.0f of its typical and the" % EA2_FLOOR_DIV)
    P("     line regulation at %.0f times its printed maximum. ACHIEVED SETTING: 1.208 V / (1 mmho x %.0f mOhm x %.1fk) = %.4f A" % (
        LINE_FLOOR_MUL, R["rs"] * 1e3, R["rm"] / 1e3, R["i_nom"]))
    P("     candidates (setting A; worst corner at the typical rows / under the floor with drifts, W):")
    for rm_val, code, stock, inom, wt, wf in R["rows_rm"]:
        if 22e3 <= rm_val <= 24.9e3:
            P("       %5.1fk %-9s stock %6d  %.4f A  %7.3f / %7.3f%s" % (rm_val / 1e3, code, stock, inom, wt, wf,
                                                                    "  <- chosen" if code == R["rm_code"] else ("  (zero margin)" if code == R["zero"][1] else
                                                                    ("  (stock under %d)" % STOCK_MIN if stock < STOCK_MIN else ""))))
    P("     CIMON_IN (new, %s): %s, LCSC %s: above p.31's minimum %.1f nF at the slowest oscillator, at the 0.1 uF lower end; tau %.2f ms" % (
        CIMON[0], CIMON[1], CIMON[2], R["cim_min"] * 1e9, R["tau"] * 1e3))
    P("   THE HOLD: R8 %gk (%s, LCSC %s, stock %d) over R9 %gk (%s, LCSC %s, stock %d), 0.1 %%, 25 ppm/K: nominal %.3f V" % (
        R["r8v"] / 1e3, R["models"][R["r8c"]], R["r8c"], R["stock"][R["r8c"]], R["r9v"] / 1e3, R["models"][R["r9c"]], R["r9c"],
        R["stock"][R["r9c"]], R["hb"][1]))
    P("     Rule (SESSION, under REQ-016 \"the panel held at 17.6 V by the stage's input regulation\" and the owner's D-34, which keeps")
    P("     REQ-016's window unchanged; check astra-check-l4e7-1, B1): the drawn ratio 102k over 7.5k kept, each at its drawn value as")
    P("     the stocked RT0603BRD07 part (0.1 %, 25 ppm/K); only the tolerance and the drift change")
    P("     the band at both ends (FBIN's I-grade limits, its line term, the FBIN bias at its typical, R8 and R9 at 0.1 % and 25 ppm/K):")
    P("       EA3 at its typical %.0f V/V:                      %.6f / %.6f / %.6f V" % (R["ea3"], R["hb"][0], R["hb"][1], R["hb"][2]))
    P("       EA3 at its typical, soldering and life drifts:  %.6f / %.6f V" % (R["hb4"][0], R["hb4"][2]))
    P("       EA3 at half its typical:                       %.6f / %.6f V" % (R["hb2"][0], R["hb2"][2]))
    P("       EA3 at half, soldering and life drifts:        %.6f / %.6f V (the widest conditioned band)" % (R["hb3"][0], R["hb3"][2]))
    P("     as drawn (1 %% parts), the replay's legacy calculation with H and MP's FBIN minimum %.3f V: %.3f / %.3f / %.3f V; with the" % (
        R["fbin_hmp_min"], *R["hold_drawn"]))
    P("     E grade the netlist names (C674164, FBIN minimum %.3f V) and the replay's other terms, its lower corner is %.6f V" % (
        R["fbin"]["min"], R["drawn_e_lo"]))
    P("   PROPOSAL, NOT ADOPTED: it would change REQ-016's 17.6 V point and needs the owner's ruling (D-34). Not drafted; nothing here")
    P("     depends on it. Of %d stocked RT0603BRD07 pairs with a nominal from %.1f to %.1f V (the model's hourly maximum-power voltage on" % (
        R["proposal"]["n"], HOLD_RANGE[0], HOLD_RANGE[1]))
    P("     SC-37's day runs %.2f to %.2f V), the one whose band's worse end gives the most energy: %gk over %gk (%s, %s), band" % (
        R["vmpp"][0], R["vmpp"][1], R["proposal"]["r8"] / 1e3, R["proposal"]["r9"] / 1e3, R["proposal"]["c8"], R["proposal"]["c9"]))
    P("     %.3f / %.3f / %.3f V (EA3 typical), %.1f / %.1f / %.1f Wh a day; at nominal %+.1f Wh a day against the kept hold's %.1f Wh" % (
        *R["proposal"]["band"], *R["proposal"]["e_band"], R["proposal"]["e_band"][1] - R["proposal"]["e_nom_kept"], R["proposal"]["e_nom_kept"]))
    P("")
    P("4. THE 100 W CORNER CHECK ON THE ACHIEVED VALUES (section 11's physics: the replay's i_factor, 8705af p.31)")
    P("   envelope: %.6f V (the kept hold's lowest: EA3 at half, the resistors' drifts) to REQ-016's %.0f V in %.2f V steps; I grade;" % (
        min(R["hb"][0], R["hb2"][0], R["hb3"][0], R["hb4"][0]), 25.0, V_STEP))
    P("   both ends:")
    for lab, t_rs, t_rm, _t3, p_ in END:
        P("     %s: RSENSE1 at %.1f C, RIMON_IN at %.1f C%s" % (lab, t_rs, t_rm, "" if lab == "the cold end" else
                                                               " (RSENSE1 %.2f W x %.1f K/W over the air, INFERRED)" % (p_, R["k_r"])))

    def show(name, chk, basis):
        P("   %s (%s):" % (name, basis))
        for lab, w, n in chk:
            P("     %-12s worst %.4f W at %.3f V (ref %.3f V, line %s, gm %.2f, RSENSE1 x%.5f, RIMON_IN x%.5f, EA2 %s); margin %.4f W; %d corners" % (
                lab, w[0], w[1], w[2], "+" if w[3] > 0 else "-", w[4], w[5], w[6], "+" if w[7] > 0 else "-", 100.0 - w[0], n))
    show("A. THE CHECK", R["main_chk"], "printed limits; the two TYP-only rows as the replay carries them: EA2 at 130 V/V over VC's absolute range, line at its 25 C maximum")
    show("B. printed rows alone", R["chk_printed"], "information: EA2's and the line term left out")
    show("C. the design floor", R["chk_floor"], "EA2 at 65 V/V, line x2, the resistors' soldering and life drifts stacked: SESSION")
    show("D. drifts at the typical rows", R["chk_drift"], "information")
    P("   VERDICT: A PASSES at both ends with a margin of %.2f W, and C (the floor) passes; refused above 100 W" % (100.0 - max(w[0] for _l, w, _n in R["main_chk"])))
    P("   THE UNPRINTED ROWS, as break-even values for this setting (the corner reaches 100 W at the value shown), each with its stack:")
    for (lm, dr), (gc, gh) in sorted(R["be_gain"].items()):
        P("     EA2's gain; printed limits, line x%-4g%-28s cold end %s V/V, hot end %s V/V" % (
            lm, ", resistors' drifts stacked" if dr else (", no drifts (stack A)" if lm == 1.0 else ", no drifts"), "%.6f" % gc if gc else "none passes",
            "%.6f" % gh if gh else "none passes"))
    P("     the line regulation (cold end; printed limits, no drifts): with EA2 at 130 V/V (stack A) up to %.1f times its printed" % R["be_line"][0])
    P("     maximum (%.3f %%/V); with EA2 at 65 V/V, %.1f times" % (R["be_line"][0] * R["line_p"], R["be_line"][1]))
    P("     RSENSE1's TCR below 25 C (HoJLR prints its TCR from +25 to +125 C only, so the cold end applies it as an ASSUMPTION): the")
    P("     cold corner passes up to %s under stack A, and up to %s under stack C (EA2 65 V/V, line x2, drifts)" % (
        "%.3f ppm/K" % (R["be_tcr_cold"] * 1e6) if R["be_tcr_cold"] is not None else "10000 ppm/K and beyond",
        "%.3f ppm/K" % (R["be_tcr_cold_floor"] * 1e6) if R["be_tcr_cold_floor"] is not None else "10000 ppm/K and beyond"))
    P("   for comparison, the replay's 3.548 A on these parts would take %.3f W at the worse end" % R["old_on_parts"])
    P("   CONDITIONS: sense voltage at the limit's highest %.1f mV (operating range %.0f mV); IMON_IN %.1f uA at it (at least %.0f uA);" % (
        R["vd_lim_hi"] * 1e3, R["csd"]["max"], R["i_imon_lim"] * 1e6, R["ioutmin"]))
    P("     the fault (IMON_IN %.2f V maximum) at up to %.1f mV across RSENSE1; the candidate's hot short circuit through RSENSE1 %.1f mV," % (
        R["iovm"]["max"], R["v_fault_max"] * 1e3, R["vd_isc"] * 1e3))
    P("     inside the operating range; no resistor in series with CSPIN or CSNIN (p.30): R59's pads are their Kelvin taps")
    P("")
    P("5. THE ENERGY (MODELED: the replay's trace on SC-37's mean September day, the SunPower SPR-E-Flex-100, 1S1P, nominal sheet)")
    P("   Wh a day into the stage (hours the limit binds); PVGIS's maximum-power figure %.1f Wh. Columns: no limit; the chosen setting" % R["e_mpp"])
    P("   at its lowest / nominal / highest; the zero-margin catalogue setting (%.1fk, %.4f A) at its lowest / nominal / highest" % (R["zero"][0] / 1e3, R["zero"][3]))
    for row in R["grid_e"]:
        P("     %-24s %.3f V  %6.1f | %s | %s" % (row[0], row[1], row[2], " ".join("%6.1f (%d h)" % x for x in row[3:6]),
                                                 " ".join("%6.1f (%d h)" % x for x in row[6:9])))
    d_ = [row[3 + k][0] - row[6 + k][0] for row in R["grid_e"] for k in range(3)]
    P("   the margin's cost on this day: %.1f Wh at the most over the %d cells (chosen less zero-margin from %+.1f to %+.1f Wh:" % (
        max(0.0, -min(d_)), len(d_), min(d_), max(d_)))
    P("   %s)" % ("where the chosen limit binds below the panel's maximum-power point, the voltage rides up toward it" if max(d_) > 0.05
                     else "the limit binds in no hour of this day at any cell"))
    P("   as drawn (the replay, section 12, no input limit; its legacy band): %s" % "; ".join("%.1f Wh at %.3f V" % (g_[3], g_[1]) for g_ in R["old_grid"]
                                                                                       if g_[2] == "no input limit (as drawn)"))
    ge = {r_[0]: r_ for r_ in R["grid_e"]}
    P("   ENERGY SENSITIVITY of the two TYP-only hold rows (check M2: energy rows, not parameter break-evens; no input limit):")
    P("     EA3's gain from its typical to half: lower corner %.1f to %.1f Wh, upper corner %.1f to %.1f Wh (with the drifts %.1f / %.1f Wh)" % (
        ge["lower hold corner"][2], ge["lower, EA3 at its floor"][2], ge["upper hold corner"][2], ge["upper, EA3 at its floor"][2],
        ge["lower, EA3 floor, drifts"][2], ge["upper, EA3 floor, drifts"][2]))
    P("     the FBIN bias (out of the pin, lowering the hold; EA3 typical, the lower corner): %s" % "; ".join(
        "%.0f nA %.6f V %.1f Wh" % (b[0] * 1e9, b[1], b[2]) for b in R["bias_rows"]))
    P("   where the margin costs: the limit's lowest begins to bind above (hour 12's %.1f C air, the model's cells):" % R["ta12"])
    for inom, vh, lim, g in R["g_bind"]:
        P("     setting %.4f A, hold %.3f V: lowest %.4f A, above %.0f W/m2" % (inom, vh, lim, g))
    P("     (SC-37's day peaks at 520.7 W/m2); in an hour it binds, the stage's input falls in the ratio of the two settings, %.1f %%" % (
        100.0 * (1 - R["i_nom"] / R["zero"][3])))
    P("   A1 AND A2 ON THE NEW TRACES (CORRECTED, WE, TYP; the replay's meanday and least, unchanged; pairs 06 / 18 UTC):")
    for (lab, ak), (e_, stops, u48, u72, add) in sorted(R["runs"].items()):
        P("     %s, %s: %.1f Wh a day; first interruption h %s; unserved %s at 48 h, %s at 72 h; least addition %s Wh" % (
            lab, ak, e_, "/".join("-" if s is None else str(s) for s in stops), " / ".join("%.1f" % v for v in u48),
            " / ".join("%.1f" % v for v in u72), " / ".join("none" if a is None else "%+.1f" % a for a in add)))
    for (lab, ak), (stops, u48, u72, add) in sorted(R["old_runs"].items()):
        P("     was %s, %s: unserved %s at 48 h, %s at 72 h; least addition %s / %s Wh" % (
            lab, ak, " / ".join("%.1f" % v for v in u48), " / ".join("%.1f" % v for v in u72), add[0], add[1]))
    P("")
    P("6. THE INTERACTION WITH L4-E5 (R10 115k to 232k, the ceiling raised, C26 and C27 re-rated)")
    for nm, (n_e, touches, r10_once, codes_ok, codes) in sorted(R["drafts"].items()):
        P("   %s: %d edit(s); names R10: %s; R10's drawn line still present once after it: %s; carries %s: %s" % (
            nm, n_e, "yes" if touches else "no", "yes" if r10_once else "NO", ", ".join(codes), "yes" if codes_ok else "NO"))
    P("   U5's junction is taken at L4-E5's raised EXTVCC (%.2f V): %.1f C; the stage's input stays at or under REQ-016's window, so" % (
        R["ceil5"][2], R["tj_hot"]))
    P("   L4-E5's line (sized for the window's 100 W) covers it; the hold and the limit are on the input, R10 and C26/C27 on the output")
    P("")
    P("7. INCONCLUSIVE (no printed bound), each with the measurement that bounds it")
    P("   - EA2's voltage gain (130 V/V TYP, p.5) and VC's operating range: the corner passes for an EA2 gain at or above %.6f V/V" % R["be_gain"][(1.0, False)][0])
    P("     cold and %.6f V/V hot under stack A, and %.6f V/V cold and %.6f V/V hot with stack C's other terms (line x2, drifts)." % (
        R["be_gain"][(1.0, False)][1], R["be_gain"][(2.0, True)][0], R["be_gain"][(2.0, True)][1]))
    P("     Bench: in input-current limit at 25 V, step the load to move VC across its range, read VC and IMON_IN; the gain is")
    P("     dVC / dV(IMON_IN); accept at or above 65 V/V (the floor), and at least the break-even at every point")
    P("   - the IMON_IN reference's line regulation while switching and at both ends (printed at 25 C, not switching, p.4): the corner")
    P("     passes up to %.0f times its printed maximum (stack A, cold end). Bench: the limit's current at VIN 16 and 25 V, switching," % R["be_line"][0])
    P("     at both ends")
    P("   - RSENSE1's TCR below +25 C (HoJLR p.4 tests +25 to +125 C): passes up to %s (stack A) and %s (stack C). Bench: R59 at -20 C" % (
        "%.0f ppm/K" % (R["be_tcr_cold"] * 1e6) if R["be_tcr_cold"] is not None else "10000 ppm/K and beyond",
        "%.0f ppm/K" % (R["be_tcr_cold_floor"] * 1e6) if R["be_tcr_cold_floor"] is not None else "10000 ppm/K and beyond"))
    P("     and +25 C")
    P("   - EA3's gain (90 V/V TYP) and the FBIN bias (10 nA TYP): no compliance effect (the corner is at 25 V); an energy sensitivity")
    P("     only (section 5); the bench reads the hold at both ends (7b.12)")
    P("   - U5's junction (INFERRED from the gate charge at 10 V and theta-JA): the CLKOUT duty cycle method of p.34 (+-10 C)")
    P("   - the candidate panel's own source compliance (O-1) and every efficiency (C-8): unchanged by this record")
    P("")
    P("8. BENCH ROWS")
    P("   7b.9 (steady state): a PV emulator puts the loaded input at the limit from %.3f V (the kept hold's lowest: EA3 at half, the" % R["hb3"][0])
    P("     resistors' drifts) to 25 V, at the load's maximum, cold-soaked")
    P("     at %.0f C and in %.1f C air; V_in x I_in at or under 100 W at every point; the limit's current at 25 V at most %.3f A" % (
        R["t_cold"], R["t_air"], 100.0 / 25.0))
    P("   7b.9t (transients, recorded apart): a source step (open circuit to the limit) and irradiance steps to the two panel")
    P("     scenarios of section 9 (%.1f W, a warmed %.1f C cell; %.1f W, a cold-soaked -20 C cell; both at 1000 W/m2); the peak and" % (
        R["outside"]["p_panel_cold"], R["outside"]["t_cell_cold"], R["outside"]["p_panel_soak"]))
    P("     the time above 100 W against the filter's %.2f ms (SESSION: no fault trip, IMON_IN under %.2f V; above 100 W no longer" % (
        R["tau"] * 1e3, R["iovm"]["min"]))
    P("     than five time constants, %.1f ms)" % (5 * R["tau"] * 1e3))
    P("   7b.10 the EA2 gain row and 7b.11 the line row above; 7b.12 the hold, read at both ends: accepted inside %.3f to %.3f V (EA3 at" % (
        R["hb3"][0], R["hb3"][2]))
    P("     half, the resistors' drifts: the conditioned envelope); a reading outside %.3f to %.3f V (EA3 typical, new parts) is recorded" % (
        R["hb"][0], R["hb"][2]))
    P("     with EA3's gain it implies")
    P("   7b.13 U5's junction by CLKOUT at all four switches, EXTVCC at the ceiling, %.1f C air: at most 125 C less p.34's 10 C" % R["t_air"])
    P("   7b.14 R59 at -20 C and +25 C (a design check of the cold TCR; Milliohm's statement is the qualification)")
    P("")
    P("9. QUALIFICATION OF THE 100 W BOUND (the owner's instruction of 1 October 2026)")
    pv = R["prov"]

    def wrapP(first, rest, text, width=118):
        for k, ln in enumerate(textwrap.wrap(text, width)):
            P((first if k == 0 else rest) + ln)
    wrapP("   ", "     ", "THE SHEET: %s, read as the Internet Archive's snapshot %s (the id_ form; the live site resets this runner's "
          "connection), sha256 %s, byte-identical to the held v2/vendor/power/lt8705a.pdf; it prints its document code 8705af on "
          "each of its 44 pages and carries no revision table. Only its rows are used" % (pv["url"], pv["snapshot"], pv["sha"]))
    P("   THE CLASSIFICATION (Y: the value can move that outcome; small: it moves it by the stated fraction, nonzero; the reasons below):")
    P("     %-4s %-74s %-6s %-9s %-10s %s" % ("id", "unprinted value", "bound", "stability", "protection", "other"))

    def eff(r_, k):
        return ("small" if k in r_["small"] else "Y") if r_[k] else "N"
    for r_ in R["qual_rows"]:
        P("     %-4s %-74s %-6s %-9s %-10s %s" % (r_["id"], r_["name"][:74], "Y" if r_["bound"] else "N", eff(r_, "stability"),
                                                eff(r_, "protection"), r_["other"]))
    for r_ in R["qual_rows"]:
        P("   %s, %s" % (r_["id"], r_["name"]))
        for lab, key in (("the bound", "why_bound"), ("loop stability", "why_stability"), ("protection", "why_protection"),
                         ("the sheet", "sheet"), ("guaranteed limit", "guaranteed"), ("conservative assumption", "conservative"),
                         ("qualification needed", "qualification")):
            text = r_[key] if r_[key] is not None else "none printed"
            for k, ln in enumerate(textwrap.wrap("%s: %s" % (lab, text), 118)):
                P("     " + ("- " if k == 0 else "  ") + ln)
        for outcome in ("stability", "protection"):
            if outcome in r_["small"]:
                wrapP("     - ", "       ", "small effect on %s: %s" % ("loop stability" if outcome == "stability" else outcome, r_["small"][outcome]))
        if r_["bound"]:
            mtxt = ("%.4f W under its conservative assumption alone (stack A otherwise, cold end)" % r_["margin_w"]) if r_["margin_w"] is not None \
                else "%.1f K of junction" % r_["margin_k"]
            wrapP("     - ", "       ", "margin kept: %s; break-even %s" % (mtxt, r_["breakeven"]))
    cs = R["cons"]
    unres = [r_["id"] for r_ in R["qual_rows"] if r_["bound"] and not r_["resolved"]]
    a7 = R["a7q"]
    wrapP("   ", "   ", "THE RESULT: %s on %s. %.4f W (cold) and %.4f W (hot), %.4f W with each resistor at its own worst end (the mixed "
          "envelope), are calculated results under the assumptions listed below. "
          "Under each unresolved row's conservative assumption alone the cold corner reads %.4f / %.4f / %.4f W (EA2 / LINE / TCR); "
          "A7 at its test-point limits is stack A itself, and TJ moves no figure while the junction stays inside -40 to 125 C. All of "
          "them together with the resistors' drifts read %.4f W (stack C with RSENSE1's cold TCR at %.0f ppm/K): margin %.4f W, which "
          "A7 consumes at an effective gain %.4f %% under its printed minimum (%.6f mmho). The design floor stack C itself reads "
          "%.4f / %.4f W (cold / hot)" % (R["bound_status"], ", ".join(unres), R["main_chk"][0][1][0], R["main_chk"][1][1][0],
                                          R["thermal"]["mixed"]["a"], cs["ea2"],
                                          cs["line"], cs["tcr"], cs["joint"], cs["tcr_cons"] * 1e6, 100.0 - cs["joint"], a7["loss"]["joint"],
                                          a7["be"]["joint"], R["chk_floor"][0][1][0], R["chk_floor"][1][1][0]))
    P("   THE ASSUMPTIONS OF 96.25 W (stack A), in one list:")
    for k, a in enumerate((
            "8705af's full-range rows for the I grade: the IMON_IN regulation 1.187 / 1.229 V and A7's gm 0.94 / 1.06 mmho, with U5's junction inside -40 to 125 C (an INFERRED estimate of about %.1f C, not a demonstrated bound)" % R["tj_hot"],
            "A7's gm limits, printed at VCSPIN - VCSNIN = 50 mV and VCSPIN = 5.025 V, applied at the design's common mode %.3f to %.0f V and up to %.1f mV differential while switching (ASSUMPTION, condition A7)" % (
                R["a7q"]["cm"][0], R["a7q"]["cm"][1], 1e3 * R["a7q"]["vd"]),
            "the IMON_IN line regulation at its printed maximum (0.005 %/V, 25 C, not switching), applied while switching and at both ends (ASSUMPTION)",
            "EA2's gain at its typical 130 V/V as its bound, with VC anywhere in its absolute maximum range -0.3 to 2.2 V (ASSUMPTION)",
            "RSENSE1 15 mOhm +-1 %% and +-50 ppm/K, the TCR printed for +25 to +125 C applied at -20 C (ASSUMPTION); its hot end %.1f C by the derating line (INFERRED)" % END[1][1],
            "RIMON_IN 23.2k +-0.1 %, +-25 ppm/K (tested from -55 to +125 C); the resistors' soldering and life drifts not stacked (they are in C and D)",
            "both resistors in the same inside air at each end (the thermal coupling of the paired ends); the mixed envelope below drops it",
            "the envelope: the input from the hold's lowest %.3f V to REQ-016's 25 V, ambient -20 to +40 C (REQ-024), inside air at most %.1f C (pcb_envelope.yaml)" % (min(R["hb"][0], R["hb2"][0], R["hb3"][0], R["hb4"][0]), R["t_air"]),
            "nothing in series with CSPIN or CSNIN (p.30): R59's pads are their Kelvin taps (a layout obligation)",
            "steady state; transients are 7b.9t's",
            "the setting realised as drafted: R59 15 mOhm and R16 23.2k with C65 (the drafts applied in a circuit round)"), 1):
        for j, ln in enumerate(textwrap.wrap(a, 114)):
            P("     %s %s" % (("%d." % k) if j == 0 else "  ", ln))
    P("   WHY THE CORNERS BOUND THE PERMITTED RANGE")
    P("     - the input voltage: P = v x I_set x [Vref (1 + ls lam (v - 12)) + es dVC / G] / (Vref_typ gm r1 r2); its slope in v is")
    P("       I_set [Vref (1 + ls lam (2v - 12)) + es dVC / G] / (Vref_typ gm r1 r2), whose bracket is at least %.6f V (stack A) and" % R["dpdv"][0])
    P("       %.6f V (stack C) at every vertex over %.3f to 25 V: the power rises with v, so 25 V is the worst; no loaded voltage" % (
        R["dpdv"][1], min(R["hb"][0], R["hb2"][0], R["hb3"][0], R["hb4"][0])))
    P("       exceeds REQ-016's 25 V open circuit (the panel is PV_P's only source and in discontinuous mode M4 is held off on reverse")
    P("       current, p.18); the hold's lowest is the floor (there, with matching stacks and each resistor at its worst end: %.4f W" % R["p_hold_lo"]["a"])
    P("       A, %.4f W C with the drifts, %.4f W with every conservative assumption). The dense check (0.01 V) of each stack finds" % (
        R["p_hold_lo"]["c"], R["p_hold_lo"]["joint"]))
    P("       its worst at the 25 V vertex")
    P("     - every tolerance direction: P is monotonic in each term (up in Vref, in the line term for v above 12 V, in the EA2 term;")
    P("       down in gm, RSENSE1 and RIMON_IN), so the 64 vertices an end hold the extremes; a resistor's low end 1 - a|T - 25| is")
    P("       least at the end of its temperature span farthest from 25 C, so the two ends are enough")
    P("     - temperature: the air from %.0f C (no self-heating; self-heating only moves a part toward 25 C there) to %.1f C plus" % (R["t_cold"], R["t_air"]))
    P("       RSENSE1's own rise (%.1f C); the LT8705A rows are full range, so U5's junction enters only as the condition -40 to" % END[1][1])
    tb = ["%.1f C" % t_ if t_ is not None else "past its 170 C rating" for t_ in R["rs_t_be"]]
    P("       125 C. RSENSE1 would have to reach %s (stack A) or %s (stack C) for the corner to reach 100 W:" % tuple(tb))
    P("       a board hot spot beside L1 and the FETs is covered by that much")
    th = R["thermal"]
    wrapP("     - ", "       ", "the thermal coupling: the paired ends assume both resistors sit in the same inside air at each end "
          "(RSENSE1 adds its own rise). The mixed envelope drops that and lets each take its own worst end: %.9f W (A), %.9f W (C), "
          "%.9f W (every conservative assumption), against %.9f / %.9f / %.9f W paired; a dense air sweep from %.0f to %.1f C in "
          "0.1 C steps, RSENSE1 with and without its rise, finds %.9f / %.9f / %.9f W. The mixed envelope is the bound's figure" % (
              th["mixed"]["a"], th["mixed"]["c"], th["mixed"]["joint"], th["paired"]["a"], th["paired"]["c"], th["paired"]["joint"],
              R["t_cold"], R["t_air"], th["sweep"]["a"], th["sweep"]["c"], th["sweep"]["joint"]), 116)
    P("   STATES OUTSIDE THE CORNERS")
    o_ = R["outside"]
    P("     - below -20 C ambient: outside REQ-024's -20 to +40 C. Computed for information at -40 C (the I grade's least junction):")
    P("       the candidate's open circuit reaches %.2f V there, outside REQ-016's window; the corner at that voltage with both" % o_["voc40"])
    P("       resistors at -40 C reads %.4f W under stack A" % o_["p40"])
    P("     - a source step (a panel plugged in live): TRK_VIN's %.1f uF (NETLIST: C11, C12, C13, C14, C15, C64) charge through R59 at" % (o_["c_vin"] * 1e6))
    P("       most the panel's short circuit, %.1f mJ at 25 V; start-up ramps VC by the soft start (p.15). Bench 7b.9t" % (o_["e_caps"] * 1e3))
    P("     - an irradiance step, two scenarios of the candidate panel (%.0f W +%.0f %%, %.2f %%/K, 1000 W/m2; INFERRED from its sheet):" % (
        100.0, 100 * o_["tol_p"], 100 * o_["gamma"]))
    P("       %.1f W with a cell warmed to %.1f C by the NOCT model in -20 C air, and %.1f W with a cold-soaked -20 C cell; either" % (
        o_["p_panel_cold"], o_["t_cell_cold"], o_["p_panel_soak"]))
    P("       exceeds 100 W until the IMON_IN loop settles through CIMON_IN (tau %.2f ms). Bench 7b.9t, both scenarios" % (R["tau"] * 1e3))
    P("     - the hold transition: VC passes between EA3 and EA2 (the diode-AND, p.14); each side's steady state is bounded above.")
    P("       The handover is a transient: bench 7b.9t")
    P("     - an unstable current loop would break the steady-state premise: bench 7b.9t with p.33's load and line steps")
    w = R["wsl"]
    wrapP("   ", "     ", "THE DESIGN OPTION THAT REMOVES AN UNKNOWN (SESSION decision): RSENSE1's cold TCR. Of the stocked 15 mOhm 1 %% 2512 "
          "parts read, only Vishay Dale's WSL2512 (%s, LCSC %s, stock %d; Document 30100, Revision 23-Nov-2023, p.2) states its TCR "
          "from -55 C: +-%.0f ppm/K, %.1f W at 70 C (HoJLR: +25 to +125 C, Ho-A0 p.4; YAGEO PA V.10 p.9 and RALEC LR IE-SP-060 p.10: "
          "the hot side only). Its printed solder-heat and life limits each carry 0.5 mOhm (p.3): %.2f %% and %.2f %% of 15 mOhm. "
          "With it, stack A reads %.4f W (RSENSE1 at %.1f C by %.0f K/W, INFERRED) and the design floor %.4f W at 23.2k; the same "
          "rule would move RIMON_IN to %s" % (
              w["model"], w["code"], w["stock"], w["tcr"] * 1e6, w["p70"], 100 * w["sold"], 100 * w["life"], w["p_a"], w["t_hot"], w["kr"],
              w["p_floor"], ("%gk (%.4f A), %.1f %% less input in every hour the limit binds" % (w["pick"][0] / 1e3, w["pick"][3], 100 * w["cost"]))
              if w["pick"] else "no stocked value"))
    wrapP("     ", "     ", "NOT TAKEN: the swap trades an unknown with a large margin (break-even %.3f ppm/K under stack C, %.1f times the "
          "printed value) for a certain loss of setting; the unknown is qualified by Milliohm's statement instead (clarification/)" % (
              R["be_tcr_cold_floor"] * 1e6, R["be_tcr_cold_floor"] / R["tcr_h"]))
    P("   CLARIFICATION REQUESTS (text for the owner to send; the session contacts no one): clarification/analog-devices-lt8705a.txt,")
    P("     clarification/milliohm-hojlr2512.txt")
    P("   PROTOTYPE MEASUREMENTS ARE DOWNSTREAM OBLIGATIONS, NOT BLOCKERS: no architecture decision depends on 7b.9, 7b.9t, 7b.10,")
    P("     7b.11, 7b.12, 7b.13 or 7b.14 (R59 at -20 C and +25 C). The current-limit mechanism holds its bound under the conservative")
    P("     assumptions above; an adverse reading changes a value (RIMON_IN, the compensation), not the mechanism or the architecture")
    P("")
    P("10. THE CONTROL DECISION (L4-E7R, the owner's instruction of 1 October 2026 and his decision process of 2 October 2026; third")
    P("    round after checks/astra-check-l4e7r-2.md, with the CS101 correction after checks/check-l4e7r-3.md; SESSION decision)")
    d = R["decision"]
    c, b, a_, sq, sg, rw = d["c"], d["b"], d["a"], d["seq"], d["surge"], d["rows"]
    bu, ds = c["budget"], sg["dist"]
    wrapP("   ", "     ", "THE VERDICT ON THE CURRENT CONTROL: NOT SHOWN on warranted manufacturer limits alone. The LT8705A's input-current limit "
          "as set (RIMON_IN %gk, RSENSE1 %.0f mOhm) holds 100 W only under values no maker warrants: %s. Under all their conservative "
          "assumptions together the corner reads %.4f W (margin %.4f W)" % (
              R["rm"] / 1e3, R["rs"] * 1e3, "; ".join("%s (break-even %s)" % (i_, b_) for i_, b_ in d["verdict"]["depends"]),
              R["cons"]["joint"], 100.0 - R["cons"]["joint"]))
    wrapP("   ", "     ", "WHAT IS BOUNDED (item 1 of the owner's process): REQ-016 bounds 'at most 100 W into the stage'. The measurement "
          "boundary is %s (REQ-016's acceptance names the panel entry, PV_IN and PV_P); everything behind it is the stage. The operating "
          "conditions are a panel inside REQ-016's window (open circuit at most 25 V at its coldest, held at 17.6 V by the stage) over "
          "the envelope's %.0f to %.1f C, its prototype measurement a bench supply on a 100 W panel's curve (SC-36). The averaging "
          "window: REQ-016 states none, and neither of its verification methods (%s) names one. The interpretation (SESSION, "
          "CONDITIONAL for layer 8 to confirm): the mean power over any %.1f s, the shortest window a bench power reading forms; the "
          "parts the limit protects (the bank, RSENSE1, the stage's switches and inductor, F2, the pack's charge) heat over seconds and "
          "longer, and the excess the window admits after a trip (the response allowance below at the source's whole current) puts "
          "%.2f mJ into one bank part and %.2f mJ into RSENSE1, against %.0f mJ and %.0f mJ their continuous ratings (1 W at 70 C, 3 W) "
          "carry in one window. A longer window would be easier to meet and is not taken. Three checks follow, each with its own "
          "result: (a) normal operation, (b) startup, shutdown and the fault response, (c) the parts' ratings during the specified "
          "disturbances; an averaged pass never excuses an absolute maximum" % (
              d["basis"]["boundary"], rw["t_cold"], rw["t_air"], " and ".join(d["basis"]["vm"]).lower().replace("_", " "), d["w_avg"],
              1e3 * c["e_part_allow"], 1e3 * c["e_r59_allow"], 1e3 * 1.0 * d["w_avg"], 1e3 * 3.0 * d["w_avg"]))
    P("   THE COMPARISON (three approaches; each bound is the static input power at most, at 25 V; the energy is the stage's input on SC-37's")
    P("   day at the kept hold's corners and on the bright day at its nominal, the regulation at its lowest; hours bound in brackets):")
    P("     %-2s %-9s %-13s %-24s %-34s %-17s %s" % ("id", "bound W", "status", "regulating setting", "Wh SC-37 lower / nominal / upper",
                                                   "Wh bright", "noon I / P"))
    for x in d["approaches"]:
        e_ = x["energy"]
        P("     %-2s %-9.4f %-13s %-24s %-34s %-17s %s" % (
            x["id"], x["bound"], x["status"], "%gk %s %.4f A" % (x["setting"][0] / 1e3, x["setting"][1], x["setting"][2]),
            " / ".join("%.1f (%d)" % (y[2], y[3]) for y in e_[:3]), "%.1f (%d)" % (e_[3][2], e_[3][3]),
            "-%.1f / -%.1f %%" % (100 * x["cur_red"], 100 * x["noon_red"])))
    en = d["e_now"]
    P("     now 23.2k: SC-37 %s; bright %.1f (%d) Wh (the bright day unlimited: %.1f Wh); noon input %.2f W (bright noon, %.1f C air)" % (
        " / ".join("%.1f (%d)" % (y[2], y[3]) for y in en[:3]), en[3][2], en[3][3], d["e_free"], d["p_noon_now"], d["ta12"]))
    P("     (noon I / P: the regulating current's reduction against 23.2k and the input power's reduction it gives at bright noon)")
    for x in d["approaches"]:
        wrapP("   ", "       ", "(%s) %s" % (x["id"], x["name"]))
        for k_ in ("warranted", "documented dependency", "assumption", "requirement", "conditional"):
            if k_ in x["classes"]:
                wrapP("     - ", "       ", "%s: %s" % (k_, "; ".join(x["classes"][k_])))
        wrapP("     - ", "       ", "parts and board E: %s" % x["parts"])
        wrapP("     - ", "       ", "new failure mode: %s" % x["failure"])
        wrapP("     - ", "       ", "still depends on: %s" % x["depends"])
        wrapP("     - ", "       ", "the disturbances: %s" % x["surge"])
        if x["id"] == "B":
            wrapP("     - ", "       ", "its bound with every row at its printed value, %.4f W; the unprinted gain terms together may add %.3f %% before "
                  "100 W with the capacitor charge (they print %.3f %% typical, not a limit); the conduction of its 4.5 mOhm package path "
                  "(the shunt included, typical) at its own regulation %.4f / %.4f Wh a day" % (b["p_static"], 100 * b["gain_be"], 100 * b["typ_gain"], b["loss"][0], b["loss"][1]))
    wrapP("   ", "     ", "THE CHOICE: (C), CONDITIONAL on two named assumptions, each carried past its physical meaning (below). R60 to R64, "
          "%d %s (%s) in parallel, %.4f mOhm, carry everything entering the stage but the bulk (ahead of them on PV_P, the CS101 "
          "correction), R8, R9 and U18's VIN+ pin; U18 INA169 (SBOS181F) "
          "turns their voltage into a current into R65 %gk and R66 %gk (%.2fk together, %.2fk to %.2fk with tolerance, drift and aging, "
          "beside the 25 kOhm of its gain row), %d x 100 nF C0G across R66 (%s: the INB filter, %.3f to %.3f ms); U19 "
          "TPS3701 trips at INB on R66 and watches TRK_VS at INA (R67 %gk, "
          "R68 %gk); either output pulls U20 TPS3808G33's MR, whose RESET holds SWEN low; R70 %gk from TRK_LDO33 over R71 %gk set SWEN "
          "when released and hold it low with no supply. The LT8705A's own limit stays as the regulation, coordinated under the trip: "
          "RIMON_IN %gk (%s), %.4f A nominal" % (
              c["n"], c["model"], c["code"], c["rbank"] * 1e3, rw["r65"] / 1e3, rw["r66"] / 1e3, c["r_load"][0] / 1e3, c["r_load"][1] / 1e3,
              c["r_load"][2] / 1e3, c["n_cf"], ", ".join(["C70", "C75", "C76", "C77", "C78", "C79"][:c["n_cf"]]), 1e3 * c["tau"][0], 1e3 * c["tau"][1], rw["r67"] / 1e3, rw["r68"] / 1e3, rw["r70"] / 1e3, rw["r71"] / 1e3,
              c["rm"][0] / 1e3, c["rm"][1], c["inom"]))
    wrapP("   ", "     ", "WHY (C): its bound rests on printed limits at their own conditions plus two assumptions about one part, each with a "
          "break-even beyond its physical meaning; (A) rests on four assumptions about the LT8705A and RSENSE1 that set the bound "
          "itself; (B) on rows printed at another supply, reference or current and on typical-only rows, and its sensor's inputs fail "
          "the capability scenario. No answer from a maker is needed for (C)'s bound; the Texas Instruments draft asks for the envelope "
          "that would retire both assumptions")
    # ---- check (a)
    wrapP("   ", "     ", "CHECK (a), NORMAL OPERATION: ONE ERROR BUDGET for the whole limiting chain, the bank, U18, its load, R66 with "
          "its filter, U19 and the trip, every term at its end that raises the trip, at the static bound's point (25 V, parts aged):")
    for t_ in c["terms"]:
        wrapP("     - ", "       ", "%s: %s (%s; %s)" % t_)
    wrapP("   ", "     ", "the chain together: the trip's nominal current %.4f A (the nominal sense voltage %.3f mV over the bank's "
          "nominal); the trip current at which 25 V reaches 100 W, the bypass included, %.4f A: the combined error the setting can "
          "tolerate before 100 W is %.2f %% of nominal. The supported bound, every term above together (the bank alone %.2f %%), is "
          "%.2f %%: the trip at most %.4f A at 25 V (its sense voltage %.3f mV), the static bound %.4f W, the margin %.2f %% of nominal, "
          "%.4f W. The second round's multiplier on the rejection rows (the larger of their offset and gain readings; printed "
          "1.0507, applied 1.0240) is withdrawn: the rows enter at the 50 mV they are printed at, and their move at the trip's own "
          "sense voltage is the separate, named assumption G_CM" % (bu["i_nom"], 1e3 * c["vs_nom"], bu["i_100"], 100 * bu["e_tol"], 100 * bu["e_bank"], 100 * bu["e_sup"], c["i_hi25"],
                      1e3 * c["vs_hi"], c["p_static"], 100 * bu["e_margin"], bu["p_margin"]))
    wrapP("   ", "     ", "the two assumptions and their break-evens (each alone, the other at its stated value): U18's gain move between "
          "its printed point and V+ = VIN+ = 25 V at the trip's own sense voltage (G_CM, taken %.0f %%) reaches 100 W at %s on the "
          "static bound alone and at %.1f %% once check (b)'s capacitor charge and ten typical responses are taken from the headroom; "
          "U18's VIN+ bias (taken %.0f mA, 10 uA typical) at %.1f mA and %.1f mA. Their meaning: G_CM at 100 %% would be a gain change "
          "the size of the gain itself, with an offset change cancelling it exactly at 50 mV; a bias of 10 mA is the pin's absolute "
          "maximum, a stress the maker calls damaging (SBOS181F p.4), so beyond it the part is in a fault, layer 8's matter. Neither "
          "is a maker's limit; the Texas Instruments draft asks for the envelope" % (
              100 * c["g_cm"], "over 500 %" if c["g_cm_be"] >= 4.99 else "%.0f %%" % (100 * c["g_cm_be"]), 100 * c["g_cm_be_b"],
              1e3 * c["i_b"], 1e3 * c["i_b_be"], 1e3 * c["i_b_be_b"]))
    P("   ROUND 3'S SETTINGS (C70 1 nF only, the regulation at its least coordinated value; stocked RT0603BRD07 values for R66, each with")
    P("   its static bound, regulation, energy on SC-37's day and the bright day, noon reduction, allowance and the two break-evens):")
    P("     %-7s %-8s %-10s %-9s %-26s %-9s %-7s %-10s %-9s %-9s %s" % ("R66", "code", "trip mV", "bound W", "R16, nominal A", "Wh SC-37",
                                                               "bright", "noon P", "allow ms", "G_CM be", "I_B be mA"))
    for s_ in c["settings"]:
        P("     %-7s %-8s %-10.4f %-9.4f %-26s %-9s %-7.1f %-10s %-9.3f %-9s %-9.1f %s" % (
            "%gk" % (s_["r66"] / 1e3), s_["code"], 1e3 * s_["vs_hi"], s_["p_static"], "%gk %s %.4f" % (s_["rm"][0] / 1e3, s_["rm"][1], s_["inom"]),
            "%.1f" % s_["energy"][1][2], s_["energy"][3][2], "-%.1f %%" % (100 * s_["noon_red"]), 1e3 * s_["t_allow"],
            ">500 %" if s_["g_cm_be"] >= 4.99 else "%.1f %%" % (100 * s_["g_cm_be"]), 1e3 * s_["i_b_be"], "round 3's choice" if abs(s_["r66"] - 8250.0) < 1e-6 else ("meets" if s_["ok"] else "")))
    s0 = [s_ for s_ in c["settings"] if s_["r66"] < c["r66"]]
    s_prev = max(s0, key=lambda s_: s_["r66"]) if s0 else None
    s_next = min([s_ for s_ in c["settings"] if s_["r66"] > c["r66"]], key=lambda s_: s_["r66"], default=None)
    s825 = [s_ for s_ in c["settings"] if abs(s_["r66"] - 8250.0) < 1e-6][0]
    wrapP("   ", "     ", "THE SETTING (SESSION, the margin decided by what it must absorb, no percentage): round 3 took the least energy "
          "cost for which (i) check (b)'s response allowance covers the response chain's typical sum with every typical-only link at %.0f "
          "times its typical value at once, and (ii) with that response spent, both assumptions are carried past their meaning (G_CM's "
          "break-even at or over 100 %%, the bias's at or over the pin's 10 mA): R66 8.25k with RIMON_IN %gk (8.06k carries G_CM only to "
          "%.1f %%). Why ten: the largest maximum-to-typical ratio among the timing rows these makers print for the chain's parts is %.1f "
          "(TPS3808's td with CT to VDD; the LT8705A's oscillator). The CS101 correction (below) adds a third condition, M2's immunity, and "
          "searches the bulk's position, R66, RIMON_IN and the INB filter together; the least energy cost that holds all three is R66 %gk "
          "(%s) with RIMON_IN %gk (%s), %d x 100 nF across R66 and the bulk ahead of the bank: the trip's highest sense voltage %.3f mV, "
          "the static bound %.4f W, margin %.4f W, the response allowance after the filter's held charge %.3f ms" % (
              c["t_fac"], s825["rm"][0] / 1e3, 100 * c["settings"][0]["g_cm_be"], c["t_spread"], c["r66"] / 1e3, c["r66_code"],
              c["rm"][0] / 1e3, c["rm"][1], c["n_cf"], 1e3 * c["vs_hi"], c["p_static"], 100.0 - c["p_static"], 1e3 * c["t_allow"]))
    wrapP("   ", "     ", "the trip in normal operation: its lowest at the hold's voltages %.4f A with the parts aged (%.4f A at 25 V; %.4f A "
          "new), against the panel's highest current on SC-37's day at any hold corner, %.4f A: it never acts that day. One bank part "
          "carries at most %.3f W at the highest trip (its rating 1 W to 70 C). CAN A CONDITIONAL TERM OVERTURN THE SOLAR ARCHITECTURE: "
          "no. Each one, past its break-even, is answered by the next stocked R66 (the table's costs) or by a part, on the same "
          "topology: the arrangement, its parts and the stage stay" % (c["trip_lo_hold"], c["i_lo_aged"], c["i_lo_new"], c["pk_day"], c["p_bank_max"]))
    # ---- check (b)
    wrapP("   ", "     ", "CHECK (b), STARTUP, SHUTDOWN AND THE FAULT RESPONSE (the energy into the stage over any %.1f s): the capacitor "
          "INPUT energy of one charge from zero to 25 V, C x Vmax^2 (half stored, half lost in the charging path), with every capacitor "
          "on the entry at its largest: the 50 V bulk %.1f uF (+20 %% and the endurance row's +30 %%), C66, C71 to C74 and C13 to C15 "
          "with C64 at +10 %% and no bias derating, %.2f uF in all: %.1f mJ. The source: REQ-016's window bounds the open circuit "
          "(25 V); the current is the panel the window was ruled with (the SunPower 100 W of a1solar), its short circuit at 1000 W/m2 and "
          "the trace's hottest cell, 70 C, %.3f A, with the sheet's +%.0f %% power tolerance on it: %.3f A, %.2f W with 25 V (not the "
          "generator's 1.1 x 5.68 A)" % (d["w_avg"], 1e6 * c["c_bulk_max"], 1e6 * c["c_entry_max"], 1e3 * c["e_cap"], rw["isc_hot"],
                                       100 * rw["tol_p"], c["i_src"], c["p_src"]))
    wrapP("     - ", "       ", "the fault response (a trip): the stage at the static bound before it, the source's whole power while the chain "
          "responds, then one full capacitor charge (a deliberate over-count: the capacitors sit at the hold voltage while the stage "
          "runs). The response prints only typical rows: U18's settling %.0f us (5 V step at 20 kOhm), U19's INB rising edge %.1f us (at "
          "10 mV overdrive), U20's MR to RESET %.2f us, RESET pulling SWEN through the divider (under 1 us, INFERRED) and one switching "
          "period at the LT8705A's lowest printed frequency, %.2f us (INFERRED: no SWEN timing row): %.1f us; before them the INB filter "
          "holds at most %.4f J above the trip (the trip's highest current times the filter's largest time constant at 25 V, any "
          "waveform). The window holds its 10 J for a response up to %.3f ms after that, %.0f times the typical sum; at the typical sum "
          "the window reads %.4f J" % (
              1e6 * rw["ts169"], 1e6 * rw["tpd_lh"], 1e6 * rw["mr_ns"], 1e6 / (float(rw["fosc"][0]) * 1e3), 1e6 * c["t_resp_typ"], c["e_f"],
              1e3 * c["t_allow"], c["t_allow"] / c["t_resp_typ"], c["e_window_typ"]))
    wrapP("     - ", "       ", "startup: the capacitors charge when the panel connects; U20 holds SWEN low for td after TRK_LDO33 passes its "
          "threshold, at least %.0f ms (SBVS050N p.7, full range), longer than the window, so no window holds both that charge and "
          "switching: the connection's window reads at most %.4f J. Shutdown and repeated events: after a trip SWEN stays low at least "
          "%.0f ms, so one window holds one trip at most; each restart goes through the soft start (8705af Figure 2)" % (
              1e3 * c["td_min"], c["e_start"], 1e3 * c["td_min"]))
    wrapP("     - ", "       ", "repeated source steps with SWEN low: the capacitors take energy again only after giving it up; with SWEN low "
          "they lose it to the quiescent loads (in one window a fraction of a volt) or back into the panel when its voltage falls under "
          "theirs (that energy leaves the stage). Each full swing between the hold's lowest corner and 25 V loses at most C x dV^2 = "
          "%.2f mJ inside the stage, so the window holds after the trip and its charge %.1f such swings. No document bounds how often a "
          "panel's open circuit swings in %.1f s (it follows irradiance and cell temperature, which change over seconds): CONDITIONAL, "
          "bench row 7b.16 steps the bench supply's curve with SWEN held low" % (1e3 * c["cycle_e"], c["cycle_be"], d["w_avg"]))
    # ---- check (c)
    wrapP("   ", "     ", "CHECK (c), THE PARTS' RATINGS DURING THE SPECIFIED DISTURBANCES. The derivation (B6): TRN-001's port table "
          "(DECISION-31) lists J_SOLAR as EXTERNAL, a long outdoor lead; the records give a 5 m lead (a1solar's array record, ESTIMATE, "
          "the panel lead's derivation below), and the approved test plan's levels for power leads do not depend on its length: M2, MIL-STD-461G CS101 on DC input power leads, curve 2 (sources of 28 V or below): %.0f dBuV, %.2f V rms, at the "
          "EUT's input to the knee (read from Figure CS101-1 at 5 kHz), then the straight line to %.1f dBuV at 150 kHz, or the source "
          "set to Figure CS101-2's %.0f W into 0.5 Ohm, with the 10 uF return capacitor of Figure CS101-4; M3, CS114, the current "
          "induced on the lead at most curve 4's %s dBuA (%.0f mA rms; Table VI, ground, Army: curves 3 and 4); M7, the discharge at "
          "decision 34's level, 8 kV contact and 15 kV air, through CS118's 150 pF and 330 Ohm (Table IX's +30 %% on the contact "
          "current, the air level scaled from it). Surge and sustained over-voltage on the panel lead: derived below (THE PANEL "
          "LEAD'S DISTURBANCES: MIL-STD-461G CS116 and CS115, the row REQ-063 commits to, and the sustained sources); D4's own 10/1000 us "
          "rating stays here as a CAPABILITY SCENARIO, labelled, the entry's margin beyond that derived basis: %.1f A at an initial "
          "junction of 25 C or below, derated to %.1f %% (%.1f A) at the hot end's %.1f C (Figure 3 as drawn, INFERRED from the figure)" % (
              20 * math.log10(ds["v101"] * 1e6), ds["v101"], 20 * math.log10(ds["v101_150k"] * 1e6), ds["p101"][0], ds["c114"][0], 1e3 * ds["i114"],
              rw["d4"]["ipp"], 100 * sg["d4_der"], rw["d4"]["ipp"] * sg["d4_der"], rw["t_air"]))
    wrapP("     - ", "       ", "the corrected network: four 10 uF 50 V ceramics, C71 to C74 (the value text and land of C13 and C14), on TRK_VS "
          "at RSENSE1's pad, so a fast edge reaches R59 only through C13 to C15's share; nothing in series with CSPIN or CSNIN, which "
          "the maker forbids (8705af p.30: all four sense pins draw bias current); the INB filter across R66; the bulk ahead of the bank "
          "on PV_P (the CS101 correction). The model (MODELED, lumped): "
          "the stage's operating current superposed at the trip's highest, %.3f A; RSENSE1 at its highest; the bulk new at its 20 C row, "
          "after endurance at 200 %% of it, and after endurance at its -40 C row (%.1f Ohm a can); the ceramics ahead at -10 %% times a "
          "bias factor 1, 0.5 or 0.25 (C13 and C14 the same factor: the same part at the same bias), each at most %.0f mOhm (SESSION "
          "assumption: no maker part is chosen), those behind with none (more current through R59); D4 off below its highest breakdown, "
          "then the straight line to its clamping point" % (sg["i_op"], rw["za"]["esr_cold"], 1e3 * sg["esr_cer"]))
    P("     %-74s %-6s %-9s %-9s %-9s %-9s %s" % ("case (the worst of the bias factors and bulks shown per level)", "U5 V", "D4 A", "TRK_VS V", "bank A", "U18 V", "part mJ"))
    seen = {}
    for x_ in sg["cases"]:
        k_ = (x_["kind"], x_["lab"])
        if k_ not in seen or x_["d59"] > seen[k_]["d59"]:
            seen[k_] = x_
    for x_ in seen.values():
        P("     %-74s %-6.4f %-9.2f %-9.2f %-9.2f %-9.4f %.4f" % (x_["lab"][:74], x_["d59"], x_["id4"], x_["v"], x_["ibank"], x_["ibank"] * sg["rb_hi"], 1e3 * x_["e_part"]))
    c101 = sg["c101"]
    wrapP("     - ", "       ", "U5's sense differential, the rating that bounded the second round: at most %.4f V (%s), %.4f V at the approved "
          "discharge, %.4f V under CS101 and %.4f V under CS114, against %.1f V (8705af p.2); the operating current's own drop is %.4f V, "
          "so the margin, %.4f V, would take a further %.2f A of converter current at the event's peak (its loops print no input "
          "impedance). With two ceramics instead of four the approved 15 kV discharge reads %.4f V: four is the least count that keeps "
          "the margin over the operating drop. The negative differential stays at %.4f V or above" % (
              sg["worst"]["d59"], sg["worst"]["lab"], sg["worst_app"]["d59"], c101["d59"], sg["c114"]["d59"], sg["rating"]["csd"], sg["d59_op"],
              sg["d59_margin"], sg["i_extra_be"], sg["alt_ca"][2], min(x_["d59n"] for x_ in sg["cases"])))
    wrapP("     - ", "       ", "every other part at its worst case: TRK_VS %.2f V against the ceramics' 50 V, U5's VIN %.0f V and Q3's %.0f V "
          "(BSC028N06NS p.1); PV_P %.2f V against the bulk's %.0f V (on %s) and U18's VIN+ and V+ %.0f V; U18's differential %.3f V against %.0f V; U19's "
          "INB %.3f V (the filter holding a discharge's charge to %.2f mV) and INA %.3f V against %.0f V (SBVS240C p.4); FBIN %.2f V and SHDN "
          "%.2f V against %.0f V; D4 carries less than the scenario's whole current (its share at most %.2f A of %.1f A) and so stays inside "
          "its rating, derated or not; a bulk can %.1f A at the pulse's peak (no single-pulse row is printed; its voltage stays under its "
          "rating); one bank part %.2f mJ over the capability pulse, CONDITIONAL: Vishay prints its pulse capability only through an "
          "online calculator whose chart it marks illustrative (the Vishay draft asks)" % (
              sg["v_pk"], sg["rating"]["vin"], sg["rating"]["q3"], sg["v_pvp"], sg["rating"]["za_v"], "PV_P" if c["layout"] == "ahead" else "TRK_VS",
              sg["rating"]["vs169"], sg["d169"], sg["rating"]["d169"],
              sg["v_inb"], 1e3 * sg["v_inb_esd_add"],
              sg["v_ina"], sg["rating"]["tps_in"], sg["v_fbin"], sg["v_shdn"], sg["rating"]["fb"],
              max(x_["id4"] for x_ in sg["cases"]), rw["d4"]["ipp"], sg["ib_can"], 1e3 * sg["e_part"]))
    wrapP("     - ", "       ", "under CS101 the input reaches %.2f V at most (open circuit and the peak), under D4's %.0f V stand-off, so D4 "
          "never conducts; a bank part dissipates %.3f W at most against 1 W; R59 and the ceramics are far inside. The bulk's ripple: "
          "with the voltage limit at the input (any test source) a can carries up to %.2f times its ripple rating at that frequency "
          "(ZA p.2, %.0f mA at 100 kHz and 105 C, the frequency table), at %.0f Hz; with Figure CS101-4's setup and an ideal source at the "
          "calibrated power, %.2f times. The rating is the 10000 h endurance figure at 105 C, not an absolute maximum: the bounding "
          "case's heating depends on the cans' thermal resistance and the time the test spends in that band, neither printed nor ruled: "
          "CONDITIONAL, M2 records the cans' temperature (a larger can or a fourth is the remedy, on the same topology)" % (
              c101["v_pk"], rw["d4"]["vr"], c101["part_w"], c101["ratio_bound"], 1e3 * rw["za"]["ripple"], c101["worst"]["f"], c101["ratio_drawn"]))
    wrapP("     - ", "       ", "the backstop under CS101: corrected, see THE BACKSTOP UNDER CS101 below (no trip at the regulation's highest "
          "current at any frequency in either setup). Above the lumped model's reach (the discharge's first nanoseconds, CS114 at MHz) "
          "the board's parasitics decide, a layout matter: C71 to C74 at R59's pad and R59's Kelvin taps, M3 and M7 at layer 8. A "
          "reversed panel conducts through D4 as DECISION-31's note E-N1 records")
    # ---- the panel lead's disturbances, derived (the surge round)
    ld = R["lead"]
    le_, r115, r36, vd = ld["lead"], ld["r115"], ld["r36"], {v_["id"]: v_ for v_ in ld["verd"]}
    wrapP("   ", "     ", "THE PANEL LEAD'S DISTURBANCES, DERIVED (REQ-016's acceptance gives layer 4 the disturbance, its source impedance or "
          "current, its duration and the limit, and layer 8 the judgement under TRN-001; the findings ledger's item 1, L4-E7R's checks "
          "1.6 and 2.4, L4-E9's register row R-156). The criterion is REQ-016's own: a disturbance passes only when D4's clamping "
          "voltage at that disturbance's current, with the part's tolerance, is at or below the lowest limit on PV_P")
    wrapP("     - ", "       ", "the exposure: J_SOLAR (PV_IN on pin 1, the return on pin 2, board E's GND) is EXTERNAL in TRN-001's port table, "
          "a long outdoor lead by definition. The lead the records give: a1solar's %.0f m one way of %.0f mm2 copper (array_calc.py, "
          "ESTIMATE), %.4f Ohm in loop (the replay's own figure); unshielded and laid on the ground from the panel to the case (SESSION "
          "reading: a panel's own leads and an extension of their class carry no shield); no earth bond: the case is plastic and no board "
          "has a chassis net (GROUNDING-AND-SHIELDS.md), so the kit floats and a common-mode transient on the lead closes only through "
          "stray capacitance, while the high side lead against its return, through the entry, is the path that loads D4. The lead's "
          "quarter wave is %.1f MHz in free space (half wave %.1f MHz), lower on soil: inside CS116's flat band, so it is added to the "
          "test frequencies as 5.14.2's installation resonance" % (le_["m"], le_["mm2"], le_["r"], le_["f_q"] / 1e6, le_["f_h"] / 1e6))
    wrapP("     - ", "       ", "THE BASIS (SESSION, the reading of what the requirements commit to): REQ-063 commits the kit's EMC "
          "characterisation to MIL-STD-461G (11 December 2015) and the 'Ground, Army' row of its Table V (held; transcribed in "
          "v2/vendor/standards/mil-std-461g-requirement-matrix.md, the same file). That row marks CS116 %s (5.14, damped sinusoids from 10 "
          "kHz to 100 MHz on every interconnecting cable, power cables included, and on each individual high side power lead) and CS115 %s "
          "(5.13, an impulse on every interconnecting cable), and CS117 %s (5.15, lightning induced, for the procuring activity to "
          "specify). TEST-PLAN.md runs M1 to M5 and no row runs CS115, CS116 or CS117. The derivation takes CS116 and CS115 as the panel "
          "lead's surge: (1) they are the transients of the one edition and row the requirements commit to; (2) the standard's appendix "
          "says that 'for most equipment, testing with some combination of CS116 and CS115 may provide sufficient coverage to address the "
          "environment for nearby lightning called out in MIL-STD-464' (A.5.15), which is the exposure an outdoor lead adds; (3) IEC "
          "61000-4-5 is neither held in this tree nor freely published, and the envelope's surge row (decision 34) and CHO-003 decline to "
          "constrain the long leads to it; (4) CS117 is not taken: its levels 'were derived from general and civil aviation experience' "
          "for aircraft equipment (A.5.15), it applies to safety-critical equipment (5.15.1), and the row leaves it to the procuring "
          "activity. NOT COVERED, a residual for layer 8 and the register: a direct strike, or one nearer than MIL-STD-464's nearby "
          "lightning (CS117 covers neither, and CS116 with CS115 only 'may'); the kit's posture there is REQ-041's mast-down alarm" % (
              ld["tv"]["CS116"], ld["tv"]["CS115"], ld["tv"]["CS117"]))
    wrapP("     - ", "       ", "D1, CS116 on PV_IN alone and on the J_SOLAR cable: each pulse e^(-pi f t / Q) sin(2 pi f t), Q 15 +- 5 (both "
          "ends, %.0f and %.0f, run), at 0.01, 0.1, 1, 10, 30 and 100 MHz and the lead's %.1f MHz; its peak Ip from Figure CS116-2 as drawn "
          "(INFERRED from the figure: 0.1 A at 10 kHz rising 20 dB a decade to 10 A at 1 MHz, flat to 30 MHz, 3 A at 100 MHz); one pulse "
          "every 1 to 2 s for five minutes; the source a generator of at most 100 Ohm through the injection probe, and the current is "
          "the test's controlled quantity ('Reduce the signal, if necessary, to produce the required current', 5.14.3.4c(3)): the port "
          "sees a current source of Ip" % (ld["q116"][0], ld["q116"][1], le_["f_q"] / 1e6))
    wrapP("     - ", "       ", "D2, CS115 on the J_SOLAR cable: %.0f A, %.0f ns at least, edges at most %.0f ns (Figure CS115-1), 30 Hz for one "
          "minute; a 50 Ohm charged-line generator through the probe, set at least to the calibration's drive (5.13.3.4c(2)(a)), 500 V "
          "across the calibration fixture's 100 Ohm loop (A.5.13); the cable's peak current is recorded (5.13.3.4c(2)(e)), not limited" % (
              r115["a"], 1e9 * r115["t"], 1e9 * r115["e"]))
    wrapP("     - ", "       ", "D3, the panel's own cold open circuit: REQ-016's window, %.0f V at most at %.0f C, current-limited, held for "
          "hours (L4-E13's disturbance check against D4's standoff holds for every plane-of-array irradiance below %.0f W/m2)" % (
              ld["v_oc"], R["decision"]["rows"]["t_cold"], ld["g13"]))
    wrapP("     - ", "       ", "D4, a stiff source on the port by mistake (a vehicle or shore lead wired to the panel's receptacle): the kit's "
          "declared source range, 9 to %.0f V (V2-SPEC line 21), through the lead's %.4f Ohm loop and F2 (10 A), held" % (ld["v_src"], le_["r"]))
    wrapP("     - ", "       ", "D5, a reversed panel: DECISION-31's note E-N1, the panel's short-circuit current %.3f A (check (b)'s, with "
          "the sheet's power tolerance) forward through D4" % ld["rev"]["i"])
    wrapP("     ", "     ", "D1 frequency by frequency. The bound puts the disturbance's whole current in D4 (REQ-016's criterion) and in "
          "R59 and the bank on top of the operating current %.4f A (no capacitor credited); the loaded network is check (c)'s corrected "
          "entry (MODELED, lumped, to 1 MHz; above it the board's parasitics decide), from two starts, operating at the hold and open at "
          "%.0f V cold with the stage off, each bulk and bias factor, both polarities and both Q ends; the trip's filter excursion is "
          "the bound 2 x Ip / (pi f) / tau (the first half cycle's charge over the filter's least time constant, %.3f ms):" % (
              ld["i_op"], ld["v_oc"], 1e3 * ld["tau_lo"]))
    rbh_ = R["decision"]["surge"]["rb_hi"]
    P("     %-8s %-6s %-15s %-8s %-8s %-8s %-8s %-9s %-8s %-6s %-9s %s" % ("f MHz", "Ip A", "D4 at Ip V", "U5 bnd", "U18 bnd", "U5 V", "U18 V",
                                                                          "TRK_VS V", "PV_P V", "D4 A", "trip A", "D4 energy bound"))
    for r_ in ld["r116"]:
        lm = ("%-8.4f %-8.4f %-9.2f %-8.2f %-6.2f" % (r_["d59"], r_["ibank"] * rbh_, r_["v"], r_["vp"], r_["id4"])) if r_["lumped"] else \
             ("%-8s %-8s %-9s %-8s %-6s" % ("-", "-", "-", "-", "-"))
        P("     %-8g %-6.2f %-15s %-8.4f %-8.4f %s %-9.5f %.2f mJ (%.2f %% of its scaled rating)" % (
            r_["f"] / 1e6, r_["ip"], "%.2f / %.2f" % (r_["vc25"], r_["vch"]), r_["d59_b"], r_["d169_b"], lm, r_["y_trip"], 1e3 * r_["e_b"],
            100 * r_["e_b"] / r_["e_cap"]))
    wrapP("     ", "     ", "(D4 at Ip: the highest part at 25 C and at the hot end's %.1f C with the sheet's typical coefficient %.1f %%/C; "
          "U5 bnd and U18 bnd: R59's and the bank's differential with the whole current in them, against %.1f V and %.0f V; U5 V, U18 V, "
          "TRK_VS V, PV_P V and D4 A: the loaded network, worst case; the loaded network's D4 current is %.2f A at every lumped frequency: the "
          "entry's capacitors take the pulse and TRK_VS peaks at %.2f V, under D4's least breakdown at the cold end, %.2f V)" % (
              R["decision"]["rows"]["t_air"], 100 * ld["aT"], R["decision"]["surge"]["rating"]["csd"], R["decision"]["surge"]["rating"]["d169"],
              max(r_["id4"] for r_ in ld["r116"] if r_["lumped"]), max(r_["v"] for r_ in ld["r116"] if r_["lumped"]), ld["vbr_cold"]))
    wrapP("     ", "     ", "D2: D4 at %.0f A %.2f V (25 C) and %.2f V (hot end); the bound U5 %.4f V and U18 %.4f V; the loaded network U5 "
          "%.4f V, TRK_VS %.2f V, PV_P %.2f V, D4 %.2f A; the pulse's charge %.3f uC, the trip filter's excursion at most %.6f A; D4's "
          "energy with the whole pulse in it %.4f mJ. The loop current the test may drive is not limited by the standard: U5's rating "
          "is reached at %.1f A with the whole current through R59 (the bound) and at %.0f A in the loaded network; D4's clamp reaches "
          "the drafted entry's %.0f V at %.1f A" % (
              r115["a"], r115["vc25"], r115["vch"], r115["d59_b"], r115["d169_b"], r115["d59"], r115["v"], r115["vp"], r115["id4"],
              1e6 * r115["q"], r115["y_trip"], 1e3 * r115["e_b"], r115["be_b"], r115["be_l"], ld["lim_draft"], r115["be_c50"]))
    wrapP("     ", "     ", "D4 with the drafted SMCJ28A: a stiff %.0f V through the lead into the clamp (INFERRED straight line from each "
          "breakdown at the printed slope); D4's continuous capability on the board, from TJ %.0f C and RthJA %.0f C/W (typical, 8 x 8 "
          "mm pads), is %.2f W at the hot end's air and %.2f W at the cold end's (the sheet's %.1f W is on an infinite heat sink):" % (
              ld["v_src"], ld["tjmax"], ld["rja"], ld["p_ok"][0], ld["p_ok"][1], ld["pd4"]))
    for lab_, vb_, i_, p_ in ld["src"]:
        P("       %-44s breakdown %.2f V: %6.2f A, %7.1f W" % (lab_, vb_, i_, p_))
    wrapP("     ", "     ", "so D4 conducts amps at any junction temperature it can reach and is over its rating by two orders of magnitude; "
          "the sheet's typical failure mode is a short, which F2 then clears; every other part of the drafted entry is rated above %.0f V "
          "(the bulk and C71 to C74 %.0f V, U18 %.0f V, U5 %.0f V, Q3 %.0f V); as drawn, C11 and C12 are %.0f V, under it. The largest "
          "sustained source the drafted entry holds is D4's least breakdown at the cold end, %.2f V (under it D4 carries less than its 1 mA "
          "test current)" % (ld["v_src"], ld["lim_draft"], R["decision"]["surge"]["rating"]["vs169"], R["decision"]["surge"]["rating"]["vin"],
                              R["decision"]["surge"]["rating"]["q3"], ld["lim_drawn"], ld["vbr_cold"]))
    wrapP("     ", "     ", "THE TVS-ONLY CHANGE for D4, evaluated and not taken (superseded by THE SOLAR-FAULT REMEDIES below), read from "
          "the held series (Littelfuse SMCJ p.2): the least row that stands off %.0f V "
          "and does not break down at the cold end is SMCJ%dA (VR %.1f V, VBR %.2f to %.2f V, %.2f V at the cold end; VC %.1f V at %.1f A). "
          "Alone it does not hold the derived set on the drafted entry: under REQ-016's criterion D1's 10 A plateau puts its clamp at "
          "%.2f V at 25 C and %.2f V at the hot end (typical coefficient), against the %.0f V parts; the %.0f V parts are reached at %.2f A "
          "(25 C) and %.2f A (hot end), Q3's %.0f V at %.1f A. So the change that holds every derived disturbance is SMCJ%dA WITH the "
          "entry's %.0f V parts at the 63 V class: the bulk C11, C12 and C69 to EEHZA1J220XP (22 uF 63 V in the same 6.3 x 7.7 mm D8 "
          "land, ESR %.0f mOhm against %.0f, ZA p.2), which takes the bulk ahead of the bank from %.0f uF to %.0f uF and so re-opens the "
          "CS101 correction (re-run with it), and C71 to C74 at 63 V or more (no ceramic's sheet is held); and with it a %.0f V source "
          "runs the stage, whose input is "
          "then the regulation's %.2f W to the trip's %.2f W at %.0f V, outside REQ-016's window (a single fault for layer 8). The "
          "alternative that also closes D5 is an input over-voltage and reverse disconnect ahead of PV_P (a series FET with its "
          "controller): more parts, and no sheet for one is held" % (
              ld["v_src"], r36["n"], r36["vr"], r36["vbr"][0], r36["vbr"][1], r36["vbr_cold"], r36["vc"], r36["ipp"], r36["vc116_25"],
              r36["vc116_h"], ld["lim_draft"], ld["lim_draft"], r36["i50_25"], r36["i50_h"], R["decision"]["surge"]["rating"]["q3"], r36["iq3"],
              r36["n"], ld["lim_draft"], 1e3 * r36["za63"]["esr"], 1e3 * R["decision"]["rows"]["za"]["esr"], 3e6 * R["decision"]["rows"]["za"]["c"],
              3e6 * r36["za63"]["c"], ld["v_src"], ld["p_src36"][0], ld["p_src36"][1], ld["v_src"]))
    wrapP("     ", "     ", "D5: D4's forward path carries %.3f A held; on the board it can dissipate %.2f W at the hot end, so it holds only "
          "below a forward drop of %.3f V, which no silicon junction has at that current (INFERRED; the sheet prints the forward drop at "
          "100 A only): NOT MET as DECISION-31 recorded (E-N1, board E's owner); the keyed receptacle is the barrier against it" % (
              ld["rev"]["i"], ld["p_ok"][0], ld["rev"]["vf_be"]))
    P("     THE VERDICTS (each against REQ-016's criterion on the drafted entry, %.0f V; as drawn the lowest limit on PV_P is C11 and C12, %.0f V):" % (
        ld["lim_draft"], ld["lim_drawn"]))
    rows_v = (("D1", "CS116, PV_IN and the cable", "D4 at the disturbance's current %.2f V (10 A, hot end), D4 off in the loaded network" % ld["v116"], "MEETS", "NOT MET (%.2f > %.0f V)" % (ld["v116"], ld["lim_drawn"])),
              ("D2", "CS115, the cable", "D4 at the disturbance's current %.2f V (5 A, hot end), D4 off in the loaded network" % r115["vch"], "CONDITIONAL: the loop current under %.1f A (U5's bound)" % r115["be_b"],
               "NOT MET (%.2f > %.0f V)" % (r115["vch"], ld["lim_drawn"])),
              ("D3", "the panel's cold open circuit", "%.0f V, under D4's %.0f V standoff" % (ld["v_oc"], R["decision"]["rows"]["d4"]["vr"]), "MEETS (CONDITIONAL on PANEL-ACC)", "MEETS"),
              ("D4", "a %.0f V source on the port" % ld["v_src"], "D4 conducts %.1f to %.1f A" % (min(i_ for _l, _v, i_, _p in ld["src"]), max(i_ for _l, _v, i_, _p in ld["src"])),
               "NOT MET on the drafted entry: remedied below (the over-voltage cut-off)", "NOT MET"),
              ("D5", "a reversed panel (E-N1)", "D4 forward, %.3f A held" % ld["rev"]["i"], "NOT MET on the drafted entry: remedied below (the "
               "return switch)", "NOT MET"))
    for r_ in rows_v:
        wrapP("       - ", "         ", "%s, %s: %s: %s; as drawn, %s" % r_)
    wrapP("     ", "     ", "FOR L4-E9'S REGISTER (R-156 and its companions; the register is L4-E9's to write): (a) R-156's input is this "
          "derivation: D1 and D3 MEET, D2 CONDITIONAL on the recorded loop current, D4 and D5 NOT MET; R-156's text names the INA250's "
          "40 V, and the drafted U18 is the INA169 (%.0f V); (b) a TEST row owed at layer 8: CS116 on PV_IN alone and on the J_SOLAR "
          "cable at the six frequencies and the lead's %.1f MHz, and CS115 on the cable, recording the cable's peak current (TEST-PLAN "
          "runs M1 to M5 only, though the row REQ-063 commits to marks both A); (c) the remedies for D4 and D5: THE SOLAR-FAULT "
          "REMEDIES below; (d) the residual beyond the basis: a direct or nearer strike, the entry's margin there the port clamp's own "
          "rating with the remedies (D4's without them, check (c)'s capability rows)" % (
              R["decision"]["surge"]["rating"]["vs169"], le_["f_q"] / 1e6))
    # ---- the solar-fault remedies (the owner's amendment of 2 October 2026, item 3)
    rm = R["remedy"]
    T4, QF, L11, ovs, bA, bN, DN, D11 = rm["T48"], rm["QF"], rm["L11"], rm["ovs"], rm["bandA"], rm["bandN"], rm["D4N"], rm["D11"]
    rw10 = R["decision"]["rows"]
    wrapP("   ", "     ", "THE SOLAR-FAULT REMEDIES (the owner's amendment of 2 October 2026, 14:20, item 3: the 36 V source and the reversed "
          "panel are open engineering defects; a selected remedy for each, its circuit changes, a bounded analysis against the approved "
          "fault exposure and the parts' ratings, the interfaces and calculations re-checked; the normal window kept, fault protection "
          "never extending the operating range). D4 and D5 of the panel lead's derivation above; L4-E9's D-10, D-11 and R-173")
    wrapP("     - ", "       ", "THE COMPARISON, three implementations, each on its held sheet. (1) The TPS48110-Q1 alone driving back-to-back "
          "FETs: TI draws it (SLUSEE5E Figure 9-14) with VS, CS+ and ISCP on the input, and rates them %.0f V to GND (6.1): a reversed "
          "panel takes them to %.0f V. Rearranged (VS behind a diode, the sense behind the pair), the reversal lands on SRC, rated %.0f V "
          "(6.1; 8.3.7 prints that state, VIN 0 V, SRC pulled negative, INP low): the reversed panel's %.0f V fits with %.0f V to spare, "
          "but a reversed connection's ring is bounded only by the input clamp, which must stand off 36 V both ways and so breaks down "
          "no lower than %.1f V at the cold end; and the diode's drop, at most %.3f V and no minimum printed, enters the cut-off's "
          "reference, inside a room of %.2f V. NOT TAKEN. (2) The LM74700-Q1 ideal diode ahead of the TPS48110-Q1 (the vehicle "
          "entry's pair, L4-E9's suggestion): its reverse comparator (V(AK REV) %.0f to %.0f mV) blocks every reverse current, so "
          "CS116's negative lobes find only the input clamp, and CATHODE to ANODE (%.0f V, 6.1) then carries the clamp's voltage "
          "plus up to the window's 25 V held behind it: with the SMCJ36CA at 10 A, %.2f V at 25 C and %.2f V at the hot end; with "
          "the SMCJ40CA %.2f V; and it rectifies CS101's ripple wherever the input falls faster than the stage drains the %.0f uF "
          "behind it, above about %.0f Hz at the regulation's highest current, inside the band (2 to 5 kHz) where the accepted M2 "
          "immunity is decided, so the accepted linear analysis would no longer describe it. NOT TAKEN. (3) SELECTED (SESSION): one "
          "remedy for each fault, both from parts already in the design, the path linear when on, no control acting on a reverse "
          "current: for D4 the TPS48110-Q1 over-voltage cut-off on the high side in TI's own topology with the vehicle entry's "
          "network (L4-E11) and one CSD19532Q5B; for D5 a CSD19532Q5B in the panel's return, its gate from the input through a "
          "divider and a BZT52C12 clamp, which blocks a reversal with its %.0f V rating and no controller" % (
              rm["i1"]["pins_abs"], rm["i1"]["pins"], rm["i1"]["src_abs"], rm["i1"]["src_rev"], rm["i1"]["src_rev"] - rm["i1"]["src_abs"],
              rm["i1"]["ring"], rm["i1"]["ov_vf"], rm["i1"]["ov_room"], rm["LM"]["vrev"][0], rm["LM"]["vrev"][2], rm["LM"]["ca"],
              rm["i2"]["ca36_25"], rm["i2"]["ca36_hot"], rm["i2"]["ca40_hot"], 1e6 * rm["i2"]["c_total"], rm["i2"]["f_rect"], QF["vds"]))
    wrapP("     - ", "       ", "THE CUT-OFF'S BAND decides the clamp D4. It must sit over CS101's peak at the input, %.2f V (M2 never trips "
          "it), under D4's least breakdown at the cold end (a sustained source never reaches the clamp), and fall back over 25 V (a "
          "panel inside the window is never locked out after a cut). TPS48110 OV %.2f / %.2f / %.2f V rising and %.2f / %.2f / %.2f "
          "V falling (SLUSEE5E 6.5), the pin's leakage up to %.0f nA either way through the top resistor; the divider of stocked "
          "YAGEO RT 0.1 %% 25 ppm/K parts, aged by their printed load-life and solder-heat limits, the record's convention for a "
          "protection threshold. With D4 the drafted SMCJ28A (%.2f V at the cold end): new parts leave %.3f V on the worst side "
          "(L4-E9's 'about 0.4 V each side' less the leakage and the drift), aged parts %.3f V: NOT MET. So D4 becomes the next held "
          "row, SMCJ%dA (VR %.1f V, VBR %.2f to %.2f V, %.2f V at the cold end; VC %.1f V at %.1f A), and the divider R98 %gk + R99 "
          "%gk over R100 %gk (%s, %s, %s) puts the cut-off at %.2f to %.2f V rising and %.2f to %.2f V falling, aged (%.2f to %.2f V "
          "new): %.3f V over CS101's peak, %.3f V under the clamp, %.2f V over 25 V on the fall. Under REQ-016's criterion the "
          "SMCJ%dA clamps D1's 10 A plateau at %.2f V at the hot end and D2's 5 A at %.2f V, under the drafted entry's %.0f V parts "
          "(over the drawn %.0f V, as before), and stands off CS101's peak by %.2f V where the SMCJ28A did by %.2f V" % (
              rm["cs101_pk"], T4["ovr"][0], T4["ovr"][1], T4["ovr"][2], T4["ovf"][0], T4["ovf"][1], T4["ovf"][2], 1e9 * T4["ovleak"],
              R["lead"]["vbr_cold"], min(rm["ov28"]["new"]["m"]), min(rm["ov28"]["aged"]["m"]), DN["n"], DN["vr"], DN["vbr"][0], DN["vbr"][1],
              DN["vbr_cold"], DN["vc"], DN["ipp"], ovs["a"] / 1e3, ovs["b"] / 1e3, ovs["rb"] / 1e3, rm["ov_codes"][0], rm["ov_codes"][1],
              rm["ov_codes"][2], bA["rise"][0], bA["rise"][1], bA["fall"][0], bA["fall"][1], bN["rise"][0], bN["rise"][1], ovs["m"][0],
              ovs["m"][1], ovs["m"][2], DN["n"], DN["v116"], DN["v115"], R["lead"]["lim_draft"], R["lead"]["lim_drawn"],
              DN["vr"] - rm["cs101_pk"], rw10["d4"]["vr"] - rm["cs101_pk"]))
    wrapP("     - ", "       ", "THE CIRCUIT CHANGES (drafted in apply_gen_sch_e_solar_guard.py, never applied): J_SOLAR.2 becomes PV_RTN "
          "and F2 feeds PV_F; D11 SMCJ40CA (C80273) across PV_F and PV_RTN at the connector; C131, C132, C135 and C136, four Samsung "
          "CL32B225KCJSNNE (2.2 uF 100 V X7R 1210, LCSC code owed), on PV_F; U21 "
          "TPS48110AQDGXRQ1 (C17556513) with R87 %.1f mOhm (C2985708) from PV_F to PV_SNS, Q12 CSD19532Q5B (C473333) from PV_SNS to "
          "PV_P, RSET R88 100R 0.1 %%, RISCP R89 3.01k with C126 330 pF C0G 100 V, the gate slew R90 36.5k, R91 10R and C127 10 nF "
          "C0G 100 V (C184799), CBST C128 1 uF, CTMR C129 22 nF C0G (C97929) with RIWRN R92 39.7k 0.1 %% (C861872), the VS filter "
          "R93 100R and C130 100 nF 100 V, UVLO R94 59.0k over R95 10.0k, INP R96 100k over R97 28.0k, the OV divider R98, R99 and "
          "R100 above (L4-E11's vehicle-entry values but the OV divider, R97 and C126, the last two from B6, THE GUARD ALREADY ON below); C133 and "
          "C134, two Samsung CL32B106KBJNNNE (10 uF 50 V X7R 1210, code owed), on PV_P beside the bulk, and C71 to C74 (the backstop "
          "draft's) moved to the same part (B6 round 2); Q13 CSD19532Q5B (C473333) from "
          "PV_RTN to GND, its gate "
          "PV_RG from PV_F through R101 %.0fk and to GND through R102 %.0fk, D12 BZT52C12-7-F (C124196) gate to source; D4 to "
          "SMCJ%dA, its LCSC code owed (no catalogue reading of it is filed). Placement on board E: at J_SOLAR, ahead of F2's load, the "
          "bulk, the sense bank and D4; Q13 in the return pin's copper. Owed with it: U21's DGX-19 land (as L4-E11's E11-01), the "
          "regeneration and its gates. Read back here on a scratch copy after the five drafts it follows (this record's hold, input "
          "limit and backstop, L4-E9's hot swap, L4-E11's entry): %d edits; the return, F2, the OV divider and its codes, D4, PV_P's "
          "switch, Q13, D11, the rails, U21's pins and B6's parts: %s; R10 untouched: %s" % (
              1e3 * L11["rsns"], rm["R101"] / 1e3, rm["R102"] / 1e3, DN["n"], R["drafts"]["apply_gen_sch_e_solar_guard.py"][0],
              "yes" if all(R["guard_draft"].values()) else "NO", "yes" if R["drafts"]["apply_gen_sch_e_solar_guard.py"][2] else "NO"))
    vd = {v_["id"]: v_ for v_ in rm["verd"]}
    P("     THE BOUNDED ANALYSIS (the drafted entry with the block and D4 SMCJ%dA; each against the parts' printed ratings):" % DN["n"])
    b6 = rm["b6"]
    wc_ = (b6["cold"]["vF"], b6["cold"]["slew"] / 1e6, b6["cold"]["iL"], b6["cold"]["e11"])
    rows_r = (
        ("D4, a stiff %.0f V source through the %.4f Ohm lead, connected cold (the block off)" % (R["lead"]["v_src"], R["lead"]["lead"]["r"]),
         "the block never turns on: the gate cannot rise before BST charges, at least %.1f ms (1 uF -10 %% to %.1f V at %.0f uA), while "
         "the OV pin follows the input at once; the cut-off's highest %.2f V is %.2f V under the source; Q12 holds %.0f V of %.0f V; "
         "U21's VS %.0f V of 80 V, EN/UVLO %.2f V of 15 V, INP %.2f V of %.0f V; D11 at %.0f V under its %.0f V standoff. The "
         "connection's ring (MODELED, THE GUARD ALREADY ON below, any source loop from %.2f uH): PV_F at most %.1f V, its slew %.1f V/us of %.0f, INP "
         "%.2f V and EN/UVLO %.2f V of %.0f V, D11 at most %.1f mJ; Q13's body diode carries the ring, at most %.1f A; D4 and the bulk "
         "see nothing" % (
             1e3 * rm["f36"]["st_min"], T4["bst_uv"][0], T4["bst_i"][2], rm["f36"]["cut_hi"], R["lead"]["v_src"] - rm["f36"]["cut_hi"],
             rm["f36"]["vds"], QF["vds"], rm["f36"]["vs"], rm["f36"]["en"], rm["f36"]["inp"], T4["pin_abs"], R["lead"]["v_src"], D11["vr"],
             1e6 * b6["grid"][0], wc_[0], wc_[1], b6["slew_abs"] / 1e6, wc_[0] * b6["kinp"], wc_[0] * b6["ken"], T4["pin_abs"], 1e3 * wc_[3], wc_[2]), "MEETS"),
        ("D5, a reversed panel (%.3f A short circuit with tolerance, %.0f V open circuit)" % (R["lead"]["rev"]["i"], rm["rev"]["v"]),
         "Q13 off (its gate at or under its source), its body diode reverse biased: no current; it holds %.0f V of %.0f V, and a "
         "reversed connection's ring at most D11's %.1f V; the high side's pins stay within 1 V of GND while Q13 leaks under %.1f uA "
         "(the dividers' conductance), against %.0f uA printed at %.0f V and 25 C; on a fast ring the port bank holds them within %.3f V; D4 and "
         "the stage see no reversal" % (rm["rev"]["vds"], QF["vds"], rm["rev"]["ring"], 1e6 * rm["rev"]["i_be"], 1e6 * rm["rev"]["idss"],
                                         rm["rev"]["idss_v"], abs(rm["rev"]["floor_c"])),
         "MEETS, CONDITIONAL on Q13's leakage above 25 C (no row; %.0f times the printed one)" % (rm["rev"]["i_be"] / rm["rev"]["idss"])),
        ("CS116 and CS115, the block on (in the path)",
         "the short-circuit trip's sense, filtered by RISCP x CSCP (330 pF, at its shortest), at most %.2f A against its least %.2f A; "
         "the overcurrent timer at "
         "most %.3f V against %.3f V (the time over its least %.3f A, %.1f us at most); the input at most %.2f V against the cut-off's "
         "least %.2f V; Q12 and Q13 carry at most %.2f A against %.0f A; D4 (SMCJ%dA) at the disturbance's current %.2f V, under %.0f V; "
         "D4 off in the loaded network. U5: CS116's whole 10 A on the trip's highest current, the conservative screen, %.4f V of "
         "%.1f V. CS115's 5 A is the generator's calibration level, not a bound on the cable's current: U5 at 5 A reads %.4f V, and "
         "the cable may carry up to %.3f A more before %.1f V" % (rm["scp_f"], rm["scp_lo"], rm["v_tmr"], T4["tmr_v"][0], rm["ocp_lo"], 1e6 * rm["t_over"],
                                           rm["ov_in116"], bA["rise"][0], rm["i_trip_hi"] + 10.0, QF["idm"], DN["n"], DN["v116"],
                                           R["lead"]["lim_draft"], b6["d59_116"], 0.3, b6["d59_115"], b6["be115"], 0.3),
         "MEETS for CS116; CS115 CONDITIONAL on R-174 (its recorded loop current under %.2f A, or U5's differential measured under 0.3 V)" % b6["be115"]),
        ("CS116 and CS115, the block off (night, or after a cut)",
         "D11 clamps the port: at 10 A at the hot end %.2f V (5 A, %.2f V): Q12 holds it against %.0f V, U21's VS against 80 V, "
         "EN/UVLO %.2f V, INP %.2f V; D11 takes at most %.1f mJ a pulse; the port bank holds PV_F within %.3f V of GND against Q13's %.0f pF" % (
             rm["off116"]["v"], rm["off116"]["v115"], QF["vds"], rm["off116"]["en"], rm["off116"]["inp"], 1e3 * rm["off116"]["e"],
             abs(rm["off116"]["floor"]), 1e12 * QF["coss"]), "MEETS"),
        ("a stiff %.0f V source arriving with the block on (B6: a step from every state the guard is on in, and ramps)" % R["lead"]["v_src"],
         "MODELED in THE GUARD ALREADY ON, ROUND 2 below, every ceramic bank its maker's curves bounded on its own: every rating with its "
         "margin (U5 within +-%.3f V, the timestep's error added) for a source loop of at least %.2f uH: Q12 turns off at most %.1f A "
         "within %.1f us, PV_F at most %.1f V (slew %.1f V/us), PV_P %.2f V, TRK_VS %.2f V (D4's least breakdown at the cold end %.2f V: "
         "D4 carries no current), U5 %.4f V and %.4f V, Q12 at %.3f of its derated chart; a rising source cut with D4's room at least "
         "%.3f V at any rate. Under that loop U5 passes the margin and then the absolute maximum (at 1.00 uH %.4f V), and no approach "
         "within the makers' printed rules removes the floor" % (
             b6["U5_LIM"], 1e6 * b6["LA"], b6["W"]["iQ"], 1e6 * b6["W"]["ton"], b6["W"]["vF"], b6["W"]["slew"] / 1e6, b6["W"]["vP"],
             b6["W"]["vS"], DN["vbr_cold"], b6["W"]["u5"] + b6["ERR"], b6["W"]["u5n"] - b6["ERR"], b6["W"]["soa12"],
             DN["vbr_cold"] - b6["ramp_w"]["vS"], b6["W1u"]["u5"] + b6["ERR"]),
         "MEETS from %.2f uH; NOT MET under it (the engineer's row B6-ENG-1)" % (1e6 * b6["LA"])),
        ("the quiescent and conduction loss in normal operation",
         "the series path at most %.2f mOhm (Q12 %.2f, Q13 %.2f at VGS %.1f V or more, R87 %.2f; the FETs at their 150 C reading); "
         "%.3f W at the regulation's highest %.3f A and %.3f W at the trip's highest %.3f A; %.2f mA around the bank at 25 V (IQ, "
         "CS- and ISCP bias, the dividers, the gate network), %.1f mW; on SC-37's day %.2f Wh of %.1f Wh (%.2f %%), on the bright day "
         "%.2f Wh of %.1f Wh" % (1e3 * rm["r_blk"], 1e3 * rm["rq11"], 1e3 * rm["rq12"], rm["vgs12_min"], 1e3 * rm["rsn_hi"],
                                  rm["p_cond"][0], rm["i_reg_hi"], rm["p_cond"][1], rm["i_trip_hi"], 1e3 * rm["i_byp"], 1e3 * rm["p_byp"],
                                  rm["e_blk"][0], rm["e_day"][0], 100 * rm["e_blk"][0] / rm["e_day"][0], rm["e_blk"][1], rm["e_day"][1]),
         "an endurance cost (the energy budget's entry)"),
    )
    for lab_, txt_, v_ in rows_r:
        wrapP("       - ", "         ", "%s: %s: %s" % (lab_, txt_, v_))
    wrapP("     - ", "       ", "THE WINDOW KEPT. REQ-016's normal window is unchanged: open circuit at most 25 V at the panel's coldest, the "
          "hold at 17.6 V, at most 100 W. The cut-off rises at %.2f V at the least and falls back at %.2f V at the least, both over 25 "
          "V with their tolerance and drift, and its highest, %.2f V, is under every rating on the entry; above it the stage is off, "
          "not running. U21 turns on at %.2f V at the most (INP through R96 over R97 28.0k at V(INP_H)'s %.1f V; the UVLO by %.2f V, "
          "L4-E11's figure for the same divider) and off at %.2f V at the least, "
          "under the stage's own enable (R14 and R15, about %.1f V as drawn), so it narrows nothing. The hold: the panel sits at most "
          "%.3f V above PV_P at the regulation's highest current. 100 W: the static bound at the panel entry with the block's own "
          "currents around the bank and the trip read at both ends of its %.3f V drop, %.4f W (%.4f W without it). NOT CLAIMED, a "
          "residual named for layer 8: a stiff source between 25 V and the cut-off (outside the window, so a fault) runs the stage "
          "under the backstop's current trip, at most %.1f W at the cut-off's highest; no protection here extends the permitted "
          "range" % (bA["rise"][0], bA["fall"][0], bA["rise"][1], rm["b6"]["inp_on"], rm["b6"]["inph"][1], L11["uv"][2], L11["uvf"][0], rm["shdn"], rm["hold_shift"], rm["dv_blk"],
                     rm["p_static_blk"], R["decision"]["c"]["p_static"], rm["gap"][2]))
    cr_ = rm["cs_re"]
    wrapP("     - ", "       ", "THE INTERACTIONS, AND WHAT WAS RE-RUN. The backstop: the sense bank, U18, U19, U20 and SWEN are behind the "
          "block and see its cut as the panel's absence (as at dusk); a connection now rises at the gate's slew, %.2f to %.2f V/ms "
          "(L4-E11), so the bank carries at most %.3f A into the capacitors behind it, under the trip's least %.4f A, and U20 holds "
          "SWEN low 180 ms anyway; Q12 carries at most %.3f A into every capacitor behind it (C133 and C134 included, each at its "
          "largest), under U21's overcurrent least %.3f A, so the start never runs the breaker's timer. CS101 (M2), RE-RUN with the "
          "block's series resistance ahead of the bulk, the port bank across the input and C133 and C134 beside the bulk (absent or "
          "at their largest): "
          "the filtered peak %.4f A at %.0f Hz (least resistance %.4f A; the accepted %.4f A reproduced with none), against the margin "
          "%.4f A: the series element lifts the bank's share by at most %.2f %% where the entry's impedance has a negative real part (the converter's "
          "constant power), and the "
          "loop branch's room is read at M2 as accepted. Check (b), RE-RUN: the capacitors at the entry %.1f mJ (the port bank, C133, C134 and U21's "
          "filter added, at their largest), the response allowance %.3f ms against %.0f times the typical sum (%.3f ms), the accepted %.3f ms. The LT8705A: "
          "its own enable, the hold (FBIN on PV_P) and the IMON_IN regulation (R59 behind the block) are unchanged. The BQ25730 on "
          "VBUS20: no path couples; the stage's output reaches it only through U4 and Q2 into VIN_RAW and board A's front end, and the "
          "block's cut is the panel's absence. TRN-001's port table: J_SOLAR's pin 2 becomes PV_RTN (switched by Q13), the first "
          "parts at the port are D11 and the port bank, and note E-N1 is closed. STAYING VALID UNCHANGED: check (a)'s chain and its 93.5521 "
          "W at the stage; the supply sequencing; check (c)'s loaded network (D4 off, its breakdown now higher; C133 and C134 beside "
          "the bulk only take current from the paths it bounds); the M7 figures (the port bank ahead, at its least at 25 V, takes a discharge's 2.25 uC as "
          "about %.2f V); L4-E13's standoff check (now 30 V). CHANGED: D1 and D2 under REQ-016's "
          "criterion (SMCJ%dA, %.2f and %.2f V); the margin beyond the basis is now D11's own rating, %.1f A at 10/1000 us, since a "
          "pulse over the cut-off turns the block off within %.0f us" % (
              L11["slew"][0], L11["slew"][2], rm["i_bank_slew"], R["decision"]["c"]["i_lo_aged"], rm["b6"]["i_start"], rm["ocp_lo"],
              cr_["most"]["worst"][2], cr_["most"]["worst"][0], cr_["least"]["worst"][2], cr_["none"]["worst"][2], rm["margin"],
              100 * (cr_["most"]["hmax"] - 1.0), 1e3 * rm["e_cap_blk"], 1e3 * rm["t_allow_blk"], rm["t_fac"], 1e3 * rm["t_fac"] * rm["t_resp_typ"],
              1e3 * R["decision"]["c"]["t_allow"], 2.25e-6 / rm["b6"]["ceff"]["F25"], DN["n"], DN["v116"], DN["v115"], D11["ipp"], 1e6 * rm["t_gate"]))
    rtn_ = dict(b6["rt"])
    W6_ = b6["W"]
    LAu, LDu = 1e6 * b6["LA"], 1e6 * b6["LD"]
    wrapP("     - ", "       ", "THE GUARD ALREADY ON, ROUND 2 (the consolidation review's B6; the external review of the provisional fixes, "
          "L4-F01: 0.3 %% headroom at 2.47 uH, one bias factor for three banks with no maker basis, the timestep's error and the harness "
          "unbounded). THE MARGIN, decided before any value (SESSION): U5's CSPIN to CSNIN differential within +-%.3f V, %.0f %% under "
          "its +-%.1f V absolute maximum (8705af p.2), with the bounded numerical error added to the computed value; every other rating "
          "%.0f %% clear of its limit. The %.3f V covers what the lumped model leaves out at U5's pins: RSENSE1's own inductance and its "
          "Kelvin traces, the ceramics' ESL, the straight-line clamps, and the typical (not warranted) curves outside their bounds" % (
              b6["U5_LIM"], 100 * (1 - b6["U5_LIM"] / b6["csd_abs"]), b6["csd_abs"], 100 * b6["M_OTHER"], b6["csd_abs"] - b6["U5_LIM"]))
    wrapP("       ", "       ", "THE REVIEW'S WITNESSES (the round-1 network at 11339ec7, on guard_event with one constant bias factor per bank; a "
          "36 V step from U21's least turn-off, %.2f V, idle, 2.47 uH, the bulk aged at -40 C): %s. The selected network (below) at "
          "the same case: %.6f V" % (b6["uvf_lo"], "; ".join("%s %.6f V" % (lab_, u_) for lab_, u_ in b6["wit"]), b6["witA"]))
    bd_ = b6["bounds"]
    wrapP("       ", "       ", "THE PARTS AND THEIR BOUNDS (Samsung's typical characteristic data, held back under v2/vendor/passives/held/ by "
          "fetch_maker_curves.py, each excerpt's sha256 pinned; each bank bounded on "
          "its own, the side its bound needs): PV_F, C131, C132, C135, C136, four CL32B225KCJSNNE (2.2 uF 100 V X7R 1210), at their "
          "least for the guard-on step (%.2f uF at 36 V, %.2f uF at 75 V) and their largest for the cold ring; PV_P, C133 and C134, and "
          "TRK_VS, C71 to C74, CL32B106KBJNNNE (10 uF 50 V X7R 1210), at their least (PV_P %.2f uF at 7.46 V and %.2f uF at 30 V; "
          "TRK_VS %.2f and %.2f uF); TRK_VIN, C13 and C14 the drawn CL31B106KBHNNNE (C89632, 10 uF 50 V X7R 1206) at their largest, "
          "C15 (C132170, YAGEO) and C64 at +10 %% with no derating (no curve held for them), %.2f uF at 7.46 V and %.2f uF at 30 V. "
          "Each bound: the part's K tolerance (+-10 %%), the typical curve's spread +-%.0f %% (ASSUMPTION: the maker prints no spread), "
          "the change under bias over %.0f to %.1f C (its bias-TCC curve: %s), capped at +10 %% with no derating; ESR 10 mOhm a part "
          "against the maker's typical %s at 100 kHz (the higher value sends more of the event downstream)" % (
              1e6 * b6["ceff"]["F_lo"][0], 1e6 * b6["ceff"]["F_lo"][1], 1e6 * b6["ceff"]["P_lo"][0], 1e6 * b6["ceff"]["P_lo"][1],
              1e6 * b6["ceff"]["S_lo"][0], 1e6 * b6["ceff"]["S_lo"][1], 1e6 * b6["ceff"]["C_hi"][0], 1e6 * b6["ceff"]["C_hi"][1],
              100 * b6["BAND"], R["t_cold"], R["t_air"],
              ", ".join("%s %.3f to %.3f" % (k_, v_[0][0], v_[0][1]) for k_, v_ in sorted(bd_.items())),
              ", ".join("%s %.1f mOhm" % (k_, 1e3 * v_[1]) for k_, v_ in sorted(bd_.items()))))
    cv_ = b6["conv"]
    wrapP("       ", "       ", "THE ENVELOPE AND THE MODEL (MODELED, guard_event_b: the round-1 network's nodes, parts and U21's latest commands, "
          "every ceramic bank its curves at its own voltage, the chord capacitance iterated in each step): a stiff %.0f V source with "
          "no source impedance credited, its loop from %.2f to %.2f uH (%d values, 10 %% apart, the floor bisected), whether the fault "
          "sits at the connector (the loop is the source's own) or at the lead's far end (the lead's added), the lead's resistance at the "
          "cold end (%.4f Ohm; %.4f Ohm at a1solar's %.0f C); the starts %s; the bulk %s; D11 at both ends. THE TIMESTEP: the worst case "
          "near the floor (%.2f V, %.4f A) from 40 ns down to 0.5 ns, %s; the error bound added to U5 is twice the largest difference "
          "from the 0.5 ns value at 20 ns or less, %.6f V" % (
              R["lead"]["v_src"], 1e6 * b6["grid"][0], 1e6 * b6["grid"][1], b6["grid"][2], b6["r_lead"], R["lead"]["lead"]["r"], b6["t_lead"],
              "; ".join(b6["st"]), "; ".join(b6["bk"]), b6["conv_case"][0], b6["conv_case"][1],
              ", ".join("%g ns %.6f V" % (1e9 * dt_, u_) for dt_, u_ in cv_), b6["ERR"]))
    P("       THE SELECTED NETWORK (A) AT %.2f uH, the worst over every start and corner, against each limit with its margin (and the least loop each holds from):" % LAu)
    for id_, v_, l_, s_ in b6["valsA"]:
        ls_ = b6["lsA"][id_]
        P("         - %-50s %s, margin %7.4f; holds from %s" % (
            rtn_[id_], ("none" if id_ == "d4" and v_ == 0.0 else "%8.4f %s %8.4f" % (v_, "of" if s_ > 0 else "against", l_)),
            (l_ - v_) * s_, ("%.2f uH" % (1e6 * ls_)) if ls_ else "under %.2f uH" % (1e6 * b6["grid"][0])))
    cn_ = b6["cnr"]
    wrapP("       ", "       ", "THE CORNER SEARCH at %.2f uH (the four banks independent, no correlation supported: every one of the %d "
          "combinations of their bounds over every start, bulk corner and D11 end; C15 and C64, no curve held, at +10 %% on their bank's "
          "upper side and a quarter of nominal on its lower, ASSUMPTION): %d of %d hold every rating with its margin; U5 from %.4f to "
          "%.4f V before the numerical error, the worst at the selected corner (the port bank, PV_P and TRK_VS at their least, TRK_VIN "
          "at its largest); over them PV_F at most %.2f V and TRK_VS at most %.2f V" % (
              LAu, len(cn_), sum(1 for c_ in cn_ if c_["ok"]), len(cn_), min(c_["u5"] for c_ in cn_), b6["cnr_w"]["u5"],
              max(c_["vF"] for c_ in cn_), max(c_["vS"] for c_ in cn_)))
    wrapP("       ", "       ", "AT %.2f uH it holds, and so at every loop above it on the grid; under it it does not: at 1.00 uH %s (U5 %.4f V), "
          "at %.2f uH U5 %.4f V and PV_F %.1f V. Q12 while it conducts: %.3f of its derated chart (TI's Figure 10, the 10 us line for its "
          "%.2f us; derated %.3f for a case at %.1f C), %.1f A at the turn-off; Q13 in the third quadrant %.1f A, %.3f of its derated "
          "chart (channel and body diode together, the channel's row taken, INFERRED); D11 %.1f A and %.1f mJ against %.0f mJ; R87's "
          "%.3f V reaches CS+ through RSET, %.2f mA against %.0f mA for 1 ms; U18 %.3f V. THE REVIEWED CASE (from 25 V): Q12 off at "
          "%.1f A, TRK_VS %.2f V, %.3f V under D4" % (
              LAu, ", ".join(rtn_[i_] for i_ in b6["fail1"]), b6["W1u"]["u5"] + b6["ERR"], 1e6 * b6["grid"][0], b6["W03"]["u5"] + b6["ERR"],
              b6["W03"]["vF"], W6_["soa12"], 1e6 * W6_["ton"], b6["der"][0], b6["tc"][0], W6_["iQ"], W6_["iL"], W6_["soa13"], W6_["i11"],
              1e3 * b6["e11"], 1e3 * b6["e11_room"], b6["rsns_v"], 1e3 * b6["i_cs"], 1e3 * b6["ics_abs"], W6_["u18"], b6["W25"]["iQ"],
              b6["W25"]["vS"], DN["vbr_cold"] - b6["W25"]["vS"]))
    rw_ = b6["ramp_w"]
    wrapP("       ", "       ", "RAMPS at %.2f uH (%d rates, 0.01 to 10 V/us, densest around %.3f V/us): the closest TRK_VS comes to D4 is %.3f V at "
          "%.3f V/us (cut by %s), %.3f V under it; D4 never conducts; U5 at most %.4f V. THE COLD CONNECTION over the whole grid (the port "
          "bank at its least and largest, from a discharged port and from 25 V): PV_F at most %.1f V, its slew %.1f V/us, INP %.2f V; "
          "Q13's body diode at most %.1f A; D11 at most %.1f mJ. THE START: Q12 carries at most %.3f A into the capacitors behind it at "
          "the gate's fastest slew, under U21's overcurrent least %.3f A" % (
              LAu, len(b6["rates"]), b6["s_h"] / 1e6, rw_["vS"], rw_["rate"] / 1e6, " and ".join(rw_["why"]), DN["vbr_cold"] - rw_["vS"],
              max(r_["u5"] for r_ in b6["ramp"]), b6["cold"]["vF"], b6["cold"]["slew"] / 1e6, b6["cold"]["vF"] * b6["kinp"], b6["cold"]["iL"],
              1e3 * b6["cold"]["e11"], b6["i_start"], rm["ocp_lo"]))
    wrapP("       ", "       ", "THE THREE APPROACHES (at most three, the review's and the coordinator's): (A) SELECTED, the round-1 guard with "
          "parts a maker characterises, bounded bank by bank: every rating with its margin for a loop of at least %.2f uH (two conductors "
          "%.2f mm apart over 5 m); the floor stays. (B) A pin-level limiter (series resistors into CSPIN and CSNIN with a clamp or "
          "capacitor across the pins), which would bound the pins' differential whatever the loop: NOT TAKEN on the LT8705A's printed "
          "statements. 8705af p.30: \"all four of the current sense pins can draw bias current under normal operating conditions. As "
          "such, do not place resistors in series with any of the CSxIN or CSxOUT pins\", and CSNIN also feeds the boost capacitor "
          "charge control, which \"can draw current in certain conditions\" (no figure); p.4 prints only a typical sum of the two "
          "pins' bias, %.0f uA, with no maximum and no split (10 Ohm a pin on that sum alone is %.2f %% of the sense at the regulation's "
          "highest current, and the boost block's draw has no bound); the RC filter p.34 shows is for CSP and CSN only, 10 Ohm at most, "
          "under 30 ns. The question is drafted for Analog Devices (clarification/analog-devices-lt8705a.txt). (D) The TPS48111-Q1, its "
          "short-circuit propagation %.2f us at most against the TPS48110-Q1's %.0f us: the floor falls to %.2f uH (%.2f mm), but its "
          "pin 2 is INP_G, so it has no OV input and the cut-off would move to INP (%.0f us) through a reference whose response no held "
          "sheet prints: not taken. At 1.00 uH (D) still reads U5 %.4f V" % (
              LAu, 1e3 * b6["sA"], 1e6 * b6["ibias_sum"], 100 * b6["lim_err"], b6["tsc11"][1], b6["tsc"][1], LDu, 1e3 * b6["sD"],
              b6["tinp"], b6["WD1"]["u5"] + b6["ERR"]))
    wrapP("       ", "       ", "THE ENGINEER'S ROW B6-ENG-1 (no approach within the makers' printed rules holds the margin independent of the "
          "source's loop): affected circuit: board E's solar guard (U21, Q12, the port bank) and U5's input sense (RSENSE1, CSPIN, "
          "CSNIN, C13 to C15); evidence and failed condition: the selected network holds U5 within +-%.3f V only for a source loop of "
          "at least %.2f uH; at 1.00 uH it reads %.4f V, over U5's %.1f V absolute maximum, because any guard that is closed when a "
          "stiff source arrives charges the stage's capacitance at a rate only the loop sets; decision or measurement needed: either "
          "Analog Devices permits a sense-pin filter on CSPIN and CSNIN with a bounded error (then B makes the margin independent of the "
          "loop), or the kit's rules bound a stiff source's loop at J_SOLAR (the connector and the leads a source can arrive through, "
          "at least %.2f uH, measured), or the input current sense moves off the stage's input capacitance; pass criterion: U5's "
          "differential within +-%.3f V at the IC pins for the declared envelope, captured at layer 9 with the guard on and a 36 V "
          "supply stepped on from about 7.5 V and from 25 V; consequence of failure: U5's sense pins over their absolute maximum, the "
          "LT8705A possibly damaged and the solar stage lost (the 100 W bound and the backstop rest on it); work blocked: D-10's "
          "closure and R-176's step row; board E's other drafts are not blocked" % (
              b6["U5_LIM"], LAu, b6["W1u"]["u5"] + b6["ERR"], b6["csd_abs"], LAu, b6["U5_LIM"]))
    r3 = b6["r3"]
    wrapP("       ", "       ", "ROUND 3, ROUTE 3 (the coordinator's one design-convergence attempt, 2 October 2026: B6-ENG-1's third route, the input "
          "current sense moved off the stage's input capacitance, worked to the circuit). What RSENSE1 carries is the current into whatever "
          "sits behind it: the guard-on transient charges that capacitance at a rate the loop sets (B6), and in operation M1 draws its "
          "pulsed current from it (8705af p.27: \"Discontinuous input current is highest in the buck region due to the M1 switch toggling "
          "on and off\"). The sheet places the input ceramics at the MOSFETs (p.36: \"These capacitors carry the MOSFET AC current in the "
          "boost and buck regions\"), asks for at least 1 uF at the VIN pin (p.27), routes the sense pair together with Kelvin taps "
          "(p.36), and rates the sense differential's OPERATING range at %.0f to %.0f mV (p.5, the full-range row; p.31: it \"should be "
          "kept below 100mV due to the limited amount of current that can be driven out of IMON_IN\", and the input current \"often has "
          "ripple and discontinuities\" that CIMON_IN averages). So the capacitance behind RSENSE1 is bounded from above by the transient "
          "and from below by the operating range, and route 3 is the question whether any split of the input ceramics satisfies both. "
          "THE OPERATING MODEL (MODELED, sense_ripple): the buck region's corner, %.0f V in (REQ-016's open circuit) delivering into the "
          "bus at %.1f V (VIN_RAW's declared nominal) and at the drawn %.1f V setpoint, the input current at the regulation's highest "
          "%.4f A and at the trip's %.4f A, the oscillator at its least %.0f kHz, L1 at the XAL1510's -20 %% (%.1f uH; its row 10 uH, "
          "%s uH typical and %s uH at the saturation current), M1's edges %.0f ns (p.26: 20 to 40 ns typical, no minimum printed), "
          "RSENSE1 at its highest with %.0f nH (Vishay's WSL prints 0.5 to 5 nH; the Milliohm part prints none: ASSUMPTION at that bound), "
          "each ceramic's ESR the maker's typical at that frequency and its ESL from its self-resonance (%s), the taps %.1f nH each "
          "(a layout obligation, declared), the bulk new at 20 C ahead of the bank; the pins read the node difference across RSENSE1 and "
          "its inductance over the last of %d periods. Its limits: a huge bank behind reads the flat average (%.4f to %.4f V), a huge "
          "bank ahead and none behind reads M1's peak (%.4f V = %.2f A x RSENSE1)" % (
              1e3 * r3["V_OP"][0], 1e3 * r3["V_OP"][1], r3["v_oc"], r3["V_OUTS"][0], r3["V_OUTS"][1],
              r3["i_reg_hi"], r3["i_op"], r3["F_LO"] / 1e3, 1e6 * r3["L1_LO"], r3["xrow"][0], r3["xrow"][1], 1e9 * r3["T_RF"], 1e9 * r3["L59"],
              ", ".join("%s %.2f nH at %.2f MHz" % (k_, 1e9 * v_, r3["srf"][k_]) for k_, v_ in sorted(r3["esl"].items())), 1e9 * r3["L_TAP"], 25,
              r3["vf"][0]["trough"], r3["vf"][0]["peak"], r3["vf"][1]["r_peak"], r3["vf"][1]["i_p"]))
    P("       THE SPLITS (the ceramics ahead of RSENSE1 at their largest and behind it at their least for the operating range, the reverse for the")
    P("       transient; U5 resistive with the numerical error, then the pins with RSENSE1's 5 nH and the Kelvin pickup, from the rise to Q12's turn-off;")
    P("       the operating figures at the 25 V corner over both bus voltages):")
    for row_ in r3["rows"]:
        t3_, t1_, t33_ = row_["tr"][0.30e-6], row_["tr"][1.0e-6], row_["tr"][3.3e-6]
        P("         - %s" % row_["lab"])
        P("           ahead %6.2f uF, behind %6.2f uF at 25 V; transient U5 %.4f V at 0.30 uH (the pins %+.3f to %+.3f V)%s, %.4f V at 1.00 uH (%+.3f to %+.3f)%s, %.4f V at 3.30 uH (%+.3f to %+.3f)%s" % (
            1e6 * (row_["cu"][0] if row_["cu"] else 0.0), 1e6 * row_["cd"][0],
            t3_["u5"] + b6["ERR"], t3_["pins_lo"], t3_["pins_hi"], (" (fails: %s)" % ", ".join(t3_["fails"])) if t3_["fails"] else " (every rating holds)",
            t1_["u5"] + b6["ERR"], t1_["pins_lo"], t1_["pins_hi"], (" (fails: %s)" % ", ".join(t1_["fails"])) if t1_["fails"] else "",
            t33_["u5"] + b6["ERR"], t33_["pins_lo"], t33_["pins_hi"], (" (fails: %s)" % ", ".join(t33_["fails"])) if t33_["fails"] else ""))
        P("           at 0.30 uH: PV_F %.1f V, TRK_VS %.2f V, D4 %.1f A, Q12 off at %.1f A; in operation: RSENSE1's resistive peak %.4f V at the regulation's "
          "highest, %.4f V at the trip's; the pins %.4f to %+.4f V; the average read %.1f %% low at the regulation's current, %.1f %% at the trip's: %s" % (
              t3_["vF"], t3_["vS"], t3_["i4"], t3_["iQ"], row_["r_peak_reg"], row_["r_peak_trip"], row_["op_trough"], row_["op_peak"],
              100 * row_["low_reg"], 100 * row_["low_trip"],
              "HOLDS both" if row_["holds"] else ("holds the transient, NOT the operating range" if row_["holds_tr"] else (
                  ("holds U5's transient but not the port's ratings, NOT the operating range" if row_["holds_u5"] else "holds NEITHER") if not row_["holds_op"] else "holds the operating range, NOT the transient"))))
    fl_ = r3["floors"]
    wrapP("       ", "       ", "THE FLOORS of the splits that hold U5 at 0.30 uH, rating by rating over the grid (the least loop each holds from; none: it "
          "holds nowhere on the grid): %s" % "; ".join("%s: %s" % (lab_, ", ".join("%s %s" % (id_, ("%.2f uH" % (1e6 * v_)) if v_ else ("under %.2f uH" % (1e6 * b6["grid"][0]) if v_ == 0.0 else "none")) for id_, v_ in ls_.items() if v_ != 0.0)) for lab_, ls_ in fl_.items()))
    oh_ = r3["op_hold"]
    wrapP("       ", "       ", "THE AS-DRAFTED SPLIT AT THE HOLD (%.2f V in, %.1f V out, %.4f A): RSENSE1's resistive peak %.4f V, the pins %.4f to %+.4f V, the "
          "average read %.1f %% low: inside the operating range there. SENSITIVITIES at the 25 V corner, 12.0 V out, the regulation's current: M1's "
          "edges at 10 ns, the pins %.4f to %+.4f V; every inductance zero, %.4f to %+.4f V (the resistive share alone, %.4f V peak). The edge's "
          "inductive step at the pins, INFERRED as the ceramics' ESL and tap times the valley current over the edge: %.3f V" % (
              r3["lo_h"], r3["V_OUTS"][1], r3["i_reg_hi"], oh_["r_peak"], oh_["trough"], oh_["peak"],
              100 * (1 - oh_["avg_clip"] / oh_["avg"]), r3["op_edge"]["trough"], r3["op_edge"]["peak"], r3["op_noesl"]["trough"], r3["op_noesl"]["peak"],
              r3["op_noesl"]["r_peak"], r3["edge_spike"]))
    pa_ = r3["parA"]
    wrapP("       ", "       ", "THE PARASITICS' BUDGET at the selected network's floor (%.2f uH), linear worst case, the pins reading R i + L di/dt with "
          "RSENSE1's inductance at the WSL's printed bound %.0f nH and the Kelvin pair's loop %.0f nH (the layout obligation: the pair from the "
          "pad centres, together, over the ground return): RSENSE1's current rises at most %.2f A/us during the charging (RSENSE1's "
          "inductance %+.4f V, the pair %+.4f V) and falls at most %.1f A/us when Q12 turns off within its %.0f ns gate fall (%+.4f V and "
          "%+.4f V). The pins read at most %+.4f V on the rise (resistive %.4f, numerical %.6f) and %+.4f V at the turn-off, against +-%.1f V: "
          "the rise %s round 2's %.3f V margin line (by %+.4f V: the floor was bisected on the resistive value, and the rise's inductive "
          "and Kelvin terms, %.4f V at 5 nH, sit inside the 0.060 V between the line and the rating), the turn-off at 5 nH %s. Over RSENSE1's "
          "inductance at the floor (%s; OUT: the turn-off outside the line), the turn-off stays inside the margin line for an inductance at "
          "most %s. The ceramics' ESL and tap (%.2f nH a part at most, %.1f nH tap) move "
          "the node, not the pin difference, and are in the operating model above. So RSENSE1's inductance, printed by no maker for the "
          "chosen part, is a condition of B6's floor as much as the loop is" % (
              LAu, 1e9 * r3["L59"], 1e9 * r3["L_KEL"], 1e-6 * pa_["up"], pa_["l_up"], pa_["k_up"], 1e-6 * abs(pa_["dn"]), 1e9 * r3["t_f"], pa_["l_dn"], pa_["k_dn"],
              pa_["hi"], b6["W"]["u5"], b6["ERR"], pa_["lo"], b6["csd_abs"], "stays inside" if pa_["hi"] <= b6["U5_LIM"] else "EXCEEDS", b6["U5_LIM"],
              pa_["hi"] - b6["U5_LIM"], pa_["hi"] - b6["W"]["u5"] - b6["ERR"], "stays inside it" if pa_["lo"] >= -b6["U5_LIM"] else "does NOT",
              "; ".join("%.1f nH %+.3f to %+.3f V%s" % (1e9 * l_, lo_, hi_, "" if ok_ else " OUT") for l_, hi_, lo_, ok_ in r3["l59_scan"]),
              ("%.1f nH" % (1e9 * r3["l59_ok"])) if r3["l59_ok"] else "none of the values tried", 1e9 * max(r3["esl"].values()), 1e9 * r3["L_TAP"]))
    wrapP("       ", "       ", "IN OPERATION the same inductance sets the pins' swing at M1's edges for the as-drafted split (25 V in, 12.0 V out, the "
          "regulation's current): %s" % "; ".join("%.0f nH: %+.4f to %+.4f V" % (1e9 * l_, o_["trough"], o_["peak"]) for l_, o_ in sorted(r3["op_l59"].items())))
    rA_ = r3["rows"][0]
    wrapP("       ", "       ", "THE VERDICT ON ROUTE 3 (SESSION): %s. No split of the input ceramics holds both: the splits that hold U5's transient at "
          "0.30 uH leave at most a few microfarads behind RSENSE1, so in operation M1's pulses flow through it and the sense differential "
          "leaves its +-%.0f mV operating range at the 25 V corner (resistive peaks %.4f to %.4f V at the regulation's highest current); the "
          "splits that keep more behind it bring the transient back. The port's own ratings keep their floors whatever the split (at 0.30 uH "
          "PV_F reads %.1f V against %.0f V, Q12's VDS and INP with it), and that floor is the SOURCE loop's (the panel lead and whatever a "
          "stiff source arrives through), not one the kit's harness from J_SOLAR to the stage controls. B6-ENG-1 stands as written, with one "
          "item added to its decision from this round's budget: RSENSE1's inductance, which no maker prints for the chosen part, must be "
          "bounded (a part whose maker prints at most %s, or the fitted part measured) for the turn-off's excursion at the pins to stay "
          "inside the margin at the floor. No further desk round on B6 without new evidence. A NEW FINDING, independent of B6: THE "
          "AS-DRAFTED SPLIT'S SENSE IN OPERATION. At "
          "the 25 V corner the sheet's CIN placement cannot be met with these parts: at 25 V bias the 50 V X7R ceramics hold %.1f uF of their "
          "%.1f uF nominal behind RSENSE1 and %.1f uF of %.1f uF ahead, and even with everything behind (the sheet's Figure 1) the resistive "
          "peak is %.4f V at the regulation's current. For the as-drafted split the pins read %.4f to %+.4f V in operation and the "
          "amplifier, limited to %.0f mV, reads the average %.1f %% low at the regulation's highest current (%.1f %% at the trip's), so the "
          "input limit regulates above its setting there; the 100 W bound rests on the backstop (U18, U19, the bank), which does not read "
          "RSENSE1 and is unaffected; the regulation of L4-E7R is NOT MET at that corner on the sheet's operating range until the pulse "
          "share is measured or the sense arrangement changes: the engineer's row B6-ENG-2 (affected circuit: U5's input sense, RSENSE1, "
          "CSPIN, CSNIN, C13 to C15, C71 to C74; evidence: this model, the sheet's p.5 and p.31; decision or measurement needed: the pins' "
          "waveform in operation at 25 V in and the lowest bus, or Analog Devices' statement of what the amplifier reads above 100 mV, or "
          "enough low-derating capacitance behind RSENSE1 (which raises B6's floor); pass criterion: the pins within +-%.0f mV at every "
          "operating point, or the regulated input current measured within the error budget at the 25 V corner; consequence of failure: "
          "the input limit regulating up to the backstop's trip at high input and a low bus, repeated trips, no damage; work blocked: the "
          "regulation's acceptance row at layer 9, not the drafts)" % (
              "route 3 HOLDS over the whole envelope" if r3["holds"] else "route 3 does NOT hold over the whole envelope, result (ii)",
              1e3 * r3["V_OP"][1], min(r_["r_peak_reg"] for r_ in r3["rows"][1:6]), max(r_["r_peak_reg"] for r_ in r3["rows"][1:6]),
              r3["rows"][1]["tr"][0.30e-6]["vF"], 100.0 * (1 - b6["M_OTHER"]),
              ("%.1f nH" % (1e9 * r3["l59_ok"])) if r3["l59_ok"] else "an inductance under 0.5 nH",
              1e6 * rA_["cd"][0], 24.8, 1e6 * rA_["cu"][0], 40.0,
              r3["rows"][6]["r_peak_reg"], rA_["op_trough"], rA_["op_peak"], 1e3 * r3["V_OP"][1], 100 * rA_["low_reg"], 100 * rA_["low_trip"],
              1e3 * r3["V_OP"][1]))
    P("     THE VERDICTS, with the remedies:")
    for v_ in rm["verd"]:
        P("       %-14s %-44s %s" % (v_["id"], v_["name"], ("MEETS" if v_["ok"] else "NOT MET") + v_.get("note", "")))
    wrapP("     ", "     ", "FOR L4-E9'S REGISTER (its D-10, D-11, D-12, R-173, R-174 and R-176): D-10 and D-11 have a selected remedy, "
          "drafted (not applied): the cut-off U21 with Q12 and the return switch Q13, D11, the port bank C131, C132, C135 and C136 "
          "(Samsung CL32B225KCJSNNE), C133 and C134 on PV_P and C71 to C74 on TRK_VS (Samsung CL32B106KBJNNNE), D4 to SMCJ%dA, R97 "
          "28.0k and C126 330 pF. D-10's source arriving with the guard on is NOT CLOSED (B6 round 2): the selected network holds every "
          "rating with its margin for a source loop of at least %.2f uH and no approach within the makers' printed rules removes that "
          "floor; the engineer's row B6-ENG-1 carries it. D-12: CS116 MEETS with the block on and off; CS115 MEETS with the block off "
          "and, with it on, is CONDITIONAL on R-174 (the cable's recorded loop current under %.2f A, or U5's differential measured "
          "under 0.3 V; U5 reads %.4f V at CS115's 5 A calibration level). Owed with it: the LCSC codes of D4 and of the Samsung "
          "parts, U21's DGX-19 land, the regeneration and its gates, and R-176's bench rows, REVISED: (1) the cut-off's rise and fall "
          "on a ramped supply (%.2f to %.2f V rising, %.2f V or more falling); (2) a %.0f V supply connected cold: Q12 never conducts, D4 "
          "carries nothing, PV_F at most %.0f V; (3) at layer 9, the waveforms at the IC pins: a %.0f V supply stepped onto the port "
          "with the guard on, from about %.1f V and from 25 V, through a loop measured first: U5's CSPIN to CSNIN within +-%.3f V, U21 "
          "turning Q12 off (at most %.0f A, within %.0f us), D4 carrying nothing, PV_P under %.2f V, a pass only for a loop at or over "
          "%.2f uH until B6-ENG-1 is decided; (4) a reversed bench panel's curve (no current; the high side's pins against GND); (5) "
          "Q13's leakage at the hot end, under %.1f uA; (6) no short-circuit trip with C126 at 330 pF in operation and under CS116 "
          "(R-174)" % (
              DN["n"], 1e6 * b6["LA"], b6["be115"], b6["d59_115"], bA["rise"][0], bA["rise"][1], bA["fall"][0], R["lead"]["v_src"],
              b6["cold"]["vF"] + 0.5, R["lead"]["v_src"], L11["uvf"][0] + 0.05, b6["U5_LIM"], b6["W"]["iQ"] + 0.5, 1e6 * b6["W"]["ton"] + 0.5,
              DN["vbr_cold"], 1e6 * b6["LA"], 1e6 * rm["rev"]["i_be"]))
    # ---- sequencing
    # ---- the backstop under CS101 (the closing check's defect and its correction)
    cs, tb = R["cs101"], R["cs101"]["tab"]
    fl_, ra_, rb_, be_ = cs["fail"], cs["rem_a"], cs["rem_b"], cs["best"]
    wrapP("   ", "     ", "THE BACKSTOP UNDER CS101 (checks/check-l4e7r-3.md; the owner's instruction of 2 October 2026). The exposure is "
          "M2's own: MIL-STD-461G CS101 on the DC input power leads, curve 2, its Figure CS101-4 setup (the coupling transformer in the "
          "high lead, the 10 uF across the leads, the LISNs of Figure 6), the kit charging from the panel lead with the regulation at "
          "its highest current. Two setups, each frequency apart: (S1) the voltage limit across J_SOLAR, the test's own controlled "
          "quantity whatever the source; (S2) the drawn setup, the source an ideal EMF at the calibrated power into 0.5 Ohm, the loop "
          "closed through the 10 uF, the two LISNs and the power source (stiff, and absent), capped at the voltage limit. The stage "
          "behind the bank: the capacitors at their largest, and the converter, whose input with VC fixed draws constant power (dI/dV = "
          "-I/V), inside its IMON_IN loop, which holds R59's current (that branch divided by 1 + T; T from A7, RIMON_IN, CIMON_IN, EA2's "
          "gm %.0f umho and gain, R13, C21, C22, A5's %.0f mV/V over R5 and the duty: typical rows, a documented dependency). The trip "
          "acts when the filtered bank current reaches the trip's lowest (aged), so the operating margin is the trip's lowest less the "
          "regulation's highest, at every input voltage" % (1e6 * cs["gm2"], 1e3 * cs["a5"]))
    wrapP("     - ", "       ", "M2's line is 'no upset of the kit's operation, no reset, no loss of a bearer' (REQ-063; characterisation, D-04, "
          "no claim): each trip stops the stage's switching for td, at least %.0f ms, so solar charging stops while the test runs. That "
          "is an upset of the kit's operation (its charging function); it is not a reset of the kit (U20's RESET acts on SWEN only) and "
          "not a lost bearer. M2's scope and line stay as written" % (1e3 * d["seq"]["td_min"]))
    pick = [min(tb["best"], key=lambda r_: abs(r_[0] - f_)) for f_ in (30.0, 60.0, 120.0, 250.0, 500.0, 1000.0, 2121.0, 5000.0, 10000.0, 40000.0, 150000.0)]
    idx = [tb["best"].index(r_) for r_ in pick]
    P("     the bank's current, A peak, S1 / S2, and the filtered peak against the margin (y: under it, the trip does not act; N: it acts):")
    P("     %-9s %-27s %-27s %-27s %s" % ("f Hz", "failing case (round 3)", "(a) alone, its most filter", "(b) alone, bulk ahead", "selected (a) + (b) + margin"))
    for i_ in idx:
        cells = []
        for k_ in ("fail", "rem_a", "rem_b", "best"):
            f_, s1_, s2_, fl2, ok_ = tb[k_][i_]
            cells.append("%.3f / %.3f -> %.4f %s" % (s1_, s2_, fl2, "y" if ok_ else "N"))
        P("     %-9.0f %-27s %-27s %-27s %s" % (tb["best"][i_][0], cells[0], cells[1], cells[2], cells[3]))
    P("     margins: failing case %.4f A (R66 %gk, RIMON_IN %gk, C70 1 nF); (a) alone %.4f A (%d x 100 nF, the most check (b)'s energy" % (
        fl_["m"], fl_["r66"] / 1e3, fl_["rm"][0] / 1e3, ra_["m"], ra_["n_cf"]))
    P("     allows there); (b) alone %.4f A; selected %.4f A (R66 %gk, RIMON_IN %gk, %d x 100 nF, the bulk ahead of the bank)" % (
        rb_["m"], be_["m"], be_["r66"] / 1e3, be_["rm"][0] / 1e3, be_["n_cf"]))
    n_fail = sum(1 for r_ in tb["fail"] if not r_[4])
    wrapP("     - ", "       ", "the failing case, reproduced: at round 3's setting the margin is %.4f A and the bank carries %.3f A at 30 Hz "
          "rising to %.2f A at %.0f Hz; the trip acts at %d of the %d frequencies, every one from 30 Hz up. (a) alone fails at the low end: "
          "the bulk behind the bank puts %.3f A through it at 30 Hz, three times the margin, and a filter slow enough to cut 30 Hz holds "
          "more charge above the trip than check (b) allows (its most, %d x 100 nF, still leaves %.3f A at 30 Hz and %.3f A at %.0f Hz). "
          "(b) alone fails from %.0f Hz up: with the bulk ahead the bank's 30 Hz current falls to %.4f A, under the margin, "
          "but the ceramics and the converter behind it carry %.2f A at %.0f Hz unfiltered; and no capacitance ahead can lower S1 at all, "
          "because the voltage across J_SOLAR is what the test holds: %.1f mF added on PV_P leaves S1 at %.3f A at 1 kHz and lowers S2 "
          "there from %.3f A to %.3f A only" % (
              fl_["m"], tb["fail"][0][1], fl_["worst"][1], fl_["worst"][0], n_fail, len(tb["fail"]), tb["fail"][0][1], ra_["n_cf"],
              tb["rem_a"][0][3], ra_["worst"][2], ra_["worst"][0], min(r_[0] for r_ in tb["rem_b"] if not r_[4]), tb["rem_b"][0][1], rb_["worst"][1], rb_["worst"][0],
              1e3 * cs["c_ahead_demo"], min(cs["rem_b_add"], key=lambda r_: abs(r_[0] - 1000.0))[2][0],
              min(cs["rem_b_add"], key=lambda r_: abs(r_[0] - 1000.0))[1][1], min(cs["rem_b_add"], key=lambda r_: abs(r_[0] - 1000.0))[2][1]))
    es_ = cs["est"]
    wrapP("     - ", "       ", "the coordinator's starting estimate, tested: a single pole at 180 Hz (%.3f ms) on round 3's circuit passes %.3f A "
          "at 30 Hz (98.6 %% of it) and %.3f A at its worst frequency, against the margin %.4f A; its crossing time on a full step from "
          "the regulation's highest, %.3f ms, is confirmed, but the margin it used, the trip's highest less the regulation's, %.3f A, "
          "is not the one that decides: the trip acts at its LOWEST, so the low frequency end decides, as the owner's instruction "
          "foresaw" % (1e3 * es_["tau"], es_["r30"], es_["worst"], fl_["m"], 1e3 * es_["t_cross"], es_["m_hi"]))
    wrapP("     - ", "       ", "THE CONTROLLING TRADE-OFF: a first-order filter of time constant tau can hold at most tau x I_trip of charge above "
          "the trip before it crosses, whatever the waveform, and that charge is spent from check (b)'s headroom; the ripple it passes, "
          "at the high end about V x C_behind / tau, must stay under the margin between the regulation's highest and the trip's lowest. "
          "The bulk behind the bank makes C_behind %.0f uF; ahead of it, %.0f uF. So the correction is both remedies together and the "
          "margin bought with the regulation: the bulk ahead of the bank (no part added), the filter on INB, and the setting the search "
          "takes with the least energy cost among %d candidates that hold all three conditions. At that cost the filter's size trades "
          "two quantities no row bounds: the IMON_IN loop branch's room in the immunity and the response's room in check (b) (the "
          "allowance over ten typical sums). The choice takes the largest of the smaller of the two: %s" % (
              1e6 * (c["c_bulk_max"] + (0.1e-6 + 4 * 10e-6) * 1.10), 1e6 * (0.1e-6 + 4 * 10e-6) * 1.10, cs["n_cands"],
              "; ".join("%d x 100 nF, the loop branch %.2f times, the response %.2f times%s" % (n_, lb_, rr_, " (chosen)" if n_ == c["n_cf"] else "")
                        for _l, _r, _m, n_, lb_, _ta, rr_ in cs["top"])))
    wrow = min(tb["best"], key=lambda r_: abs(r_[0] - be_["worst"][0]))
    wrapP("     - ", "       ", "(i) NO UPSET under M2: with the selection the filtered peak is at most %.4f A at %.0f Hz (S%s) against the margin "
          "%.4f A, at the filter's least time constant (%.3f ms: R66 at its least, the capacitors' 5 %% and C0G's 30 ppm/K) and every "
          "capacitor at its largest. The worst frequency is where the IMON_IN loop's typical model peaks; its branch may be %.1f times "
          "the model before the margin is spent (CONDITIONAL on the typical rows: M2 reads it)" % (
              be_["worst"][2], be_["worst"][0], "1" if wrow[1] >= wrow[2] else "2", be_["m"], 1e3 * be_["tau"][0], cs["loop_be"]))
    wrapP("     - ", "       ", "(ii) PROTECTION under REQ-016's boundary and the 0.1 s window: the filter's held charge, at most the trip's "
          "highest (%.4f A) times its largest time constant (%.3f ms) at 25 V, is %.4f J; with the static bound (%.4f W, the bulk's "
          "printed leakage, %.2f mW, now counted as bypassing the bank), the capacitor charge (%.1f mJ, the bulk's included: moving it "
          "ahead of the sensor hides nothing from the boundary) and the chain's detection and shutdown at ten times typical, the window "
          "leaves %.3f ms for the response (was 3.78 ms). On a step to the source's whole current the filter crosses after %.3f ms from "
          "zero and %.3f ms from the regulation's highest (%.4f A); a slow ramp just over the trip is bounded by the held charge" % (
              be_["i_hi"], 1e3 * be_["tau"][1], be_["e_f"], c["p_static"], 1e3 * 25.0 * c["leak"], 1e3 * c["e_cap"], 1e3 * c["t_allow"],
              1e3 * cs["t_step0"], 1e3 * cs["t_stepr"], cs["i_rh"]))
    wrapP("     - ", "       ", "(iii) RATINGS and behaviour: check (c) below is re-run on the corrected entry (the bulk on PV_P, the filter on "
          "INB); the sequencing is unchanged (R70, R71, U20); the filter's capacitors see at most INB's %.2f V against their 50 V. What "
          "the sensor sees: everything into TRK_VS (D4, C71 to C74, C66, U18's supply, R14 and R67, R59 to the converter, C13 to C15 "
          "and C64); what it does not: the bulk's charge, ripple and leakage, R8 and R9, U18's VIN+ pin, TP5. The capacitance moved "
          "ahead: its charge at connection, at most %.1f mJ (C x V^2 at its largest), is counted at the boundary J_SOLAR and PV_IN in "
          "check (b); the inrush is the panel's own current, %.3f A at most (a current-limited source, through F2); its leakage is in "
          "the static bound; its CS101 ripple against its rating is check (c)'s CONDITIONAL item below; its parasitics, the cans' and "
          "the bank's inductance (a few nH, about %.1f mOhm at 150 kHz for 5 nH), are small against the stage's impedance over "
          "CS101's range and decide only the fast edges (layout, M7)" % (sg["v_inb"], 1e3 * c["c_bulk_max"] * 25.0 ** 2, c["i_src"],
                                                                          1e3 * 2 * math.pi * 150e3 * 5e-9))
    wrapP("     - ", "       ", "the cost against round 3: %.1f / %.1f / %.1f Wh on SC-37's day (lower / nominal / upper hold) and %.1f Wh on "
          "the bright day; the static bound falls to %.4f W" % (
              cs["e_fail"][0][0][2] - c["energy"][0][2], cs["e_fail"][0][1][2] - c["energy"][1][2], cs["e_fail"][0][2][2] - c["energy"][2][2],
              cs["e_fail"][0][3][2] - c["energy"][3][2], c["p_static"]))
    wrapP("   ", "     ", "THE SUPPLY SEQUENCING (B3), SWEN OFF BY DEFAULT, on printed rows: R71 %gk holds SWEN to ground and R70 %gk "
          "feeds it from TRK_LDO33 only, so SWEN is at most %.4f x TRK_LDO33 (both at their worst ends, aged). Below %.3f V on TRK_LDO33 "
          "SWEN cannot reach its least rising threshold, %.3f V (8705af p.4), whatever the ramp, the delays or U20's state; %.3f V is above "
          "every sensing part's least supply (U19 %.1f V, U20 %.1f V; U18 sits on TRK_VS, watched by U19's INA from %.3f V). Above it U19 "
          "and U20 are inside their ranges: U20 holds RESET at its VOL, %.1f V at 1 mA (SBVS050N p.6; RESET sinks at most %.3f mA here), "
          "while TRK_LDO33 is under its threshold (%.3f to %.3f V; it releases at %.3f V at most) and for td after; U19's outputs reach "
          "U20's MR at %.2f V at most (VOL at 1.8 V and 3 mA) against MR's %.2f V. So SWEN can rise only while the sensing chain is "
          "supplied and armed, with no condition on TRK_LDO33's ramp or sag rate and no use of U20's power-up row. Released, at LDO33's "
          "least (%.2f V) SWEN reads %.3f V against its highest threshold %.3f V. The one unprinted figure is SWEN's own pin current: it "
          "could enable the stage below %.2f V on TRK_LDO33 only by sourcing %.0f uA (%.0f uA with TRK_LDO33 floating), keep it off "
          "only by sinking %.0f uA, and RESET's VOL fails to disable it only if the threshold's hysteresis (22 mV typical) reached "
          "%.3f V; the Analog Devices draft asks. TRK_LDO33 carries at most %.0f uA of the arrangement, under the 5 mA its regulation "
          "row is printed at. U18's output at the highest trip, %.3f V into R65 + R66 at their largest, stays under its compliance where "
          "the chain is armed, %.2f V" % (
              rw["r71"] / 1e3, rw["r70"] / 1e3, sq["k_hi"], sq["guard_v"], sq["swen"][0], sq["guard_v"], sq["vdd_t"], sq["vdd38"], sq["uv_ts_lo"],
              sq["vol38"], 1e3 * sq["i_reset"], sq["vit_lo"], sq["vit_hi"], sq["rel_hi"], rw["vol_max"], sq["mr_vil"], sq["ldo_lo"],
              sq["sw_hi_min"], sq["swen"][1], sq["vdd_sense"], 1e6 * sq["i_sw_be"], 1e6 * sq["i_sw_be_dead"], 1e6 * sq["i_sink_be"], sq["hys_be"],
              1e6 * sq["i_ldo"], c["vout_hi"], sq["uv_ts_lo"] - rw["sw169"]))
    e_c = c["energy"]
    wrapP("   ", "     ", "THE COORDINATION (SESSION, one basis at both corners): the smallest stocked RIMON_IN whose regulation at its highest "
          "under the joint assumptions (EA2 and EA3 at half gain, the line at twice, RSENSE1's cold TCR at 100 ppm/K, the drifts, each "
          "resistor at its worst end) stays at or under C's lowest trip with its parts aged, at every input voltage: %gk, %.4f A at 25 V "
          "against %.4f A. If the regulation's unprinted values were worse than those assumptions, the overlap would be a hiccup: each "
          "trip stops the stage %.0f to %.0f ms (SBVS050N p.7) and restarts it through the soft start; the bright day's hours whose panel "
          "current at the nominal hold exceeds C's lowest trip are %s, %.1f Wh, the energy such an overlap would put at risk" % (
              c["rm"][0] / 1e3, c["reg_hi25"], c["i_lo_aged"], float(rw["td38"][0]), float(rw["td38"][2]),
              ", ".join("%02d" % h for h, _g, _p in c["exposed"]) or "none", sum(p_ for _h, _g, p_ in c["exposed"])))
    wrapP("   ", "     ", "THE ENERGY: on SC-37's day %.1f / %.1f / %.1f Wh at the lower, nominal and upper hold corners (%d / %d / %d h bound) "
          "against %.1f / %.1f / %.1f Wh with 23.2k (%.1f Wh less at the nominal hold, %.1f Wh at the lower corner); on the bright day "
          "%.1f Wh (%d h bound) against %.1f Wh (%.1f Wh less); at bright noon the input power falls %.1f %% (the current %.1f %%). The "
          "bank's conduction at the selected regulation's own currents (its nominal %.4f mOhm, the trace's hourly current at the nominal "
          "hold with the regulation at its lowest) costs %.4f Wh on SC-37's day and %.4f Wh on the bright day; R59 stays. The bright day "
          "is the check's own (astra-check-l4e7r-1, D3) and this model reproduces its figures: %s" % (
              e_c[0][2], e_c[1][2], e_c[2][2], e_c[0][3], e_c[1][3], e_c[2][3], en[0][2], en[1][2], en[2][2], en[1][2] - e_c[1][2],
              en[0][2] - e_c[0][2], e_c[3][2], e_c[3][3], en[3][2], en[3][2] - e_c[3][2],
              100 * c["noon_red"], 100 * c["cur_red"], 1e3 * c["rbank"], c["loss"][0], c["loss"][1],
              "; ".join("%gk %.4f Wh, the noon power %.2f %% under 23.2k" % (rv_ / 1e3, e_, 100 * nr_) for rv_, e_, nr_ in c["check_repro"])))
    l9 = c["l4e9"]
    wrapP("   ", "     ", "L4-E9'S FIGURES THIS ROUND SETS (its power-path output at fnd/l4e9 539dc57c, read only; excerpt in inputs/): "
          "line 86 and 109, 'limit 3.4713 A' becomes the regulation at RIMON_IN %gk, %.4f A nominal and %.4f A at its highest on the "
          "hold's corners (%.2f W at the nominal hold, %.2f W at most there); lines 86, 109 and 113, the 25 V corner's 96.2474 W and "
          "99.8992 W become the backstop's static bound, %.4f W (CONDITIONAL on G_CM and the VIN+ bias, break-evens above), with the "
          "regulation's own 25 V corner at %.4f W; line 97, the panel's hot short circuit 6.42 A, is %.3f A with the sheet's power "
          "tolerance (still under J_SOLAR's nearest stated 7 A); lines 99, 105 and 115, PENDING, become the drafted bank, the 50 V "
          "bulk on PV_P ahead of it, D4 and C71 to C74 on TRK_VS, the INB filter and the backstop (drafts, not applied); line 119's 93 W out 'at the window' is above what "
          "the stage converts at the hold (%.2f W in at most), so its current is a ceiling, not an expectation; line 307's 350 Wh a day "
          "becomes %.1f / %.1f / %.1f Wh (SC-37) and %.1f Wh on the bright day" % (
              c["rm"][0] / 1e3, c["inom"], l9["reg_hi_hold"], l9["p_hold_nom"], l9["p_hold_hi"], c["p_static"], l9["p_reg25"], c["i_src"],
              l9["p_hold_hi"], e_c[0][2], e_c[1][2], e_c[2][2], e_c[3][2]))
    di = d["disc"]
    wrapP("   ", "     ", "THE SERIES DISCONNECT (the check's suggestion, evaluated, not taken; SESSION): %s" % di["why"])
    fl = d["faults"]
    wrapP("   ", "     ", "THE SINGLE FAULTS (assigned to layer 8's fault analysis): those that defeat the backstop: %s. Those that remove "
          "the supply guard only: %s. Those that stop charging: %s. %s" % ("; ".join(fl["defeat"]), "; ".join(fl["guard"]), "; ".join(fl["stop"]), fl["acceptance"]))
    bd = R["backstop_draft"]
    n_e, _t, r10_once, codes_ok, codes = R["drafts"]["apply_gen_sch_e_backstop.py"]
    wrapP("   ", "     ", "THE DRAFT FOR BOARD E'S GENERATOR OWNER (drafted, never implemented here): apply_gen_sch_e_backstop.py, %d "
          "edit(s) on the text the hold and input limit drafts leave (it refuses a generator without them): the bank on PV_P to TRK_VS: "
          "%s; R59 and CSPIN behind it, nothing in series with CSPIN or CSNIN: %s; SWEN on TRK_SWEN with R70 and R71 as the guard: %s; "
          "D4 on TRK_VS: %s; the 50 V bulk on PV_P ahead of the bank: %s; C71 to C74 on TRK_VS: %s; the INB filter across R66: %s; R66 at "
          "%gk: %s; R14 on TRK_VS: %s; R16 "
          "at %gk: %s; carries %s: %s; R10 untouched: %s. Read back here on a scratch copy; never applied to the tree" % (
              n_e, "yes" if bd["bank"] else "NO", "yes" if (bd["cspin"] and bd["r59"] and bd["no_series"]) else "NO",
              "yes" if (bd["swen"] and bd["guard"]) else "NO", "yes" if bd["d4"] else "NO", "yes" if (bd["bulk"] and bd["bulk_at"]) else "NO",
              "yes" if bd["ca"] else "NO", "yes" if bd["c70"] else "NO", c["r66"] / 1e3, "yes" if bd["r66"] else "NO",
              "yes" if bd["r14"] else "NO", c["rm"][0] / 1e3, "yes" if bd["r16"] else "NO", ", ".join(codes), "yes" if codes_ok else "NO",
              "yes" if r10_once else "NO"))
    wrapP("   ", "     ", "PROTOTYPE MEASUREMENTS (REQ-016's second method; the exact downstream verification): 7b.15, on each built board, "
          "the input current at which SWEN falls, at 17.6 V and 25 V, against %.4f to %.4f A at 25 V, at commissioning and at layer 8's "
          "interval; 7b.16, the response from a current step over the trip to the last switching edge, against %.3f ms, and with R16 "
          "shorted (IMON_IN at 0 V, so neither the regulation nor its fault acts) the energy over every %.1f s at or under 10 J, through a "
          "trip, a panel connection and the bench supply's curve stepped with SWEN held low, each restart through the soft start; 7b.17, "
          "the regulation at %gk on a bench panel curve does not trip at 25 C and at the cold end; 7b.18, R59's differential (Kelvin "
          "at U5's pins) under the M7 discharge at J_SOLAR and under a 10/1000 us pulse at D4's rating, against %.1f V; 7b.19, SWEN at "
          "TRK_LDO33's power-up, sag and loss, against %.3f V while TRK_LDO33 is under %.2f V and U20's VOL above it. M2 (the laboratory "
          "validation of CS101, downstream, characterisation under D-04): the kit charging from a bench panel curve at the regulation's "
          "highest current, Figure CS101-4's setup on the solar lead, curve 2 or the calibrated power at every frequency of 30 Hz to "
          "150 kHz at Table III's rate; record the voltage across J_SOLAR, the lead's current (a current probe), SWEN, the stage's input "
          "current and charge rate, and the bulk cans' case temperature; the pass line is M2's own: SWEN never falls and charging never "
          "stops (no upset), no reset, no lost bearer; the least margin read at the worst frequency (the model puts it near %.0f Hz) is "
          "stated beside the model's %.4f A" % (c["i_lo_aged"], c["i_hi25"], 1e3 * c["t_allow"], d["w_avg"], c["rm"][0] / 1e3, sg["rating"]["csd"],
                                          sq["swen"][0], sq["guard_v"], R["cs101"]["best"]["worst"][0], R["cs101"]["best"]["m"] - R["cs101"]["best"]["worst"][2]))
    wrapP("   ", "     ", "THE DECISION (item 5): the selected solution is (C) at R66 %gk and RIMON_IN %gk, with the corrected entry (the "
          "bulk ahead of the bank), the INB filter and SWEN off by default, because it is the one arrangement whose bound needs no "
          "maker's answer, whose two assumptions are carried past their physical meaning and whose backstop holds through M2's CS101, "
          "at an energy cost of %.1f Wh a day at the nominal hold against round 3. M2: the filtered ripple at most %.4f A against the "
          "margin %.4f A, CONDITIONAL on the IMON_IN loop's typical model (its branch may be %.1f times it). (a) normal operation: %.4f W at "
          "most, margin %.4f W, CONDITIONAL on G_CM (break-even %.0f %%) and the VIN+ bias (%.0f mA); (b) startup, shutdown and the fault "
          "response: at most 10 J in any %.1f s for a response up to %.3f ms (%.0f times the typical sum), CONDITIONAL on the %.1f s "
          "interpretation (layer 8), the response's typical rows (7b.16) and the panel's swing rate with SWEN low (%.1f full swings per "
          "window); (c) the disturbances: every part inside its rating at the approved levels and in the capability scenario, U5's "
          "differential at most %.4f V, CONDITIONAL on the lumped model (layout, M3, M7, 7b.18), the bulk's heating under CS101's bounding "
          "case (M2) and the bank's pulse capability in the capability scenario (Vishay); the panel lead's derived disturbances: CS116 "
          "MEETS, CS115 CONDITIONAL on the loop current, the panel's cold open circuit MEETS, a stiff source of the kit's range on the "
          "port and a reversed panel NOT MET on the drafted entry and remedied (the over-voltage cut-off U21 with Q12, D4 to the "
          "SMCJ30A, and the return switch Q13; THE SOLAR-FAULT REMEDIES). Drafted: the board E edits above and four "
          "clarification texts; implemented: nothing in the tree. L4-E7R's architecture criterion: MET, CONDITIONAL on the named "
          "items, none of which can overturn the architecture (each resolves by a stocked setting or a part on the same topology). If "
          "the coordinator's closing check finds otherwise, the engineering alternative is the next stocked RIMON_IN for M2's margin and "
          "the next R66 for (a) and (b) (the search's costs), and a larger or added bulk can for (c)'s heating, before any change of "
          "arrangement" % (
              c["r66"] / 1e3, c["rm"][0] / 1e3, R["cs101"]["e_fail"][0][1][2] - c["energy"][1][2], R["cs101"]["best"]["worst"][2],
              R["cs101"]["best"]["m"], R["cs101"]["loop_be"], c["p_static"], bu["p_margin"],
              100 * c["g_cm_be_b"], 1e3 * c["i_b_be_b"], d["w_avg"], 1e3 * c["t_allow"], c["t_allow"] / c["t_resp_typ"], d["w_avg"], c["cycle_be"],
              sg["worst"]["d59"]))
    wrapP("   ", "     ", "THE CLARIFICATION DRAFTS (text for the owner to send, the session contacts no one): no answer moves C's bound "
          "into or out of 100 W. Texas Instruments: the warranted error envelope at V+ = VIN+ of 9 V to 25 V and the trip's sense voltage, "
          "the VIN+ current, the output past 150 mV (retiring both assumptions); Analog Devices: the coordination's and energy's rows, "
          "and SWEN's input current, falling threshold and delay; Milliohm: the cold TCR; Vishay: the bank's pulse capability (the "
          "capability scenario only): %s" % ", ".join("clarification/" + c_ for c_ in d["clar"]))
    return o


def main():
    R = compute()
    sys.stdout.write("\n".join(render(R)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
