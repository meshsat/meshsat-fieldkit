#!/usr/bin/env python3
"""l4e7_p0sol.py: task P0-7 of MESHSAT-1357 (5 October 2026): the solar stage's two open defects, D-10 (a stiff source stepping onto
the panel port with the solar guard already on, the reviews' B6 and L4-F01) and D-16 (the input current sense out of its range in
normal operation, B6-ENG-2), by a bounded comparison of circuit alternatives (the owner's P0 instruction of 5 October 2026, part
15, sections 3 to 6, and its scope amendment, part 19). The lead-inductance method is ENDED: no loop is searched and no passing
loop is claimed; the record's own transient model is run only at the record's own reference loop and the envelope's ends, to
check a changed circuit against the same failure case.

PROTOTYPE DESIGN, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry or rendered page in the
tree is edited (apply_gen_sch_e_p0sol.py beside this file is a draft for board E's generator owner, composed here on scratch copies
only). Every figure carries its basis: PRINTED LIMIT (a maker's minimum or maximum), TYPICAL (a maker's typical row or curve),
MEASURED (none exists), ASSUMPTION (a figure no document gives), MODELED (a model's answer), INFERRED (method stated), SESSION (a
design rule of this record, with its reason), NETLIST (the composed netlist), CATALOGUE (a filed distributor reading).

Section 0 reproduces both failing cases on the base before any change: the record's results cache against this tree (the one
input that differs, and the figures compute() parses from it, equal in both versions), render(cache) against the committed .out
byte for byte, D-16 by the record's own sense_ripple and D-10 by the record's own guard_event_b with every bank rebuilt from the
makers' held curves, each equal to the cached figure. Exit 4 if a reproduction or a predicate fails, 3 if an input cannot be read,
2 if a pinned input is not the pinned file.

Run from anywhere:  python3 v2/docs/records/l4e7/l4e7_p0sol.py > v2/docs/records/l4e7/l4e7_p0sol.out
(regenerate the committed output only through the integration's regen_out.py). Takes about two minutes on a loaded host; needs
pdftotext and the held documents (the record's fetch_held_back.py and fetch_maker_curves.py)."""
import cmath
import hashlib
import importlib.util
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
try:
    os.nice(10)
except OSError:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
REC = "v2/docs/records/l4e7"
LS_PY = REC + "/l4e7_stage_settings.py"
LS_OUT = REC + "/l4e7_stage_settings.out"
LS_CACHE = REC + "/l4e7_stage_settings.results.json"
DRAFT = REC + "/apply_gen_sch_e_p0sol.py"
GEN_E = "v2/ecad/tools/gen_sch_e.py"
NET_E = "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"
GEN_NETLIST = "v2/docs/records/l8p/gen_netlist.py"
NETREAD = "v2/docs/records/l8p/check_l8p_netlist.py"
L4E11_OUT = "v2/docs/records/l4e11/l4e11_power.out"
CACHE_AT = "69921ce8"          # set 29's freeze: the commit whose l4e11_power.out the record's cache KEY holds (in this branch's history)
LT = "v2/vendor/power/lt8705a.pdf"
I169 = "v2/vendor/ti/held/ti-ina169-sbos181f.pdf"
TPS = "v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf"
T48 = "v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf"
WSL = "v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf"
XAL = "v2/vendor/power/coilcraft-xal1510.pdf"
SAMH = "v2/vendor/passives/held/samsung-%s-2026-10-02.json"
RTJ = (REC + "/inputs/jlc-search-rt0603brd07-2026-10-01.json", REC + "/inputs/jlc-search-rt0603brd07-30k-2026-10-01.json")
LC44322 = REC + "/inputs/lcsc-C44322-2026-10-01.json"
# L4-E9's change list for board E (records/l4e9/L4-POWER-ARCHITECTURE.md section 3), in application order, with this draft after the
# solar guard (R-173) and before L4-E11's aux (R-177); d8dec31's drafts take the committed netlist as their second argument
ORDER_E = (("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
           ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e7", "p0sol"), ("l4e11", "aux"), ("l8r2", "packrtn"),
           ("l8p", "enable"), ("d8dec31", "cin"), ("l6r2", "xal_land"), ("l6r2", "lcsc"))
L_TIE = 1e-6                   # SESSION, the model's tie for a removed RSENSE1 (Ohm): the record's chain keeps its node, 1 uOhm joins it
V_LINE_REF = 12.0              # l4e_replay.py's V_LINE_REF: the VIN the LT8705A's page header prints the references at


def refuse(code, msg):
    sys.stderr.write("l4e7_p0sol: %s\n" % msg)
    sys.exit(code)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def load(name, rel):
    sp = importlib.util.spec_from_file_location(name, os.path.join(TOP, rel))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def need(text, pat, what):
    m = re.search(pat, text, re.M | re.S)
    if not m:
        refuse(3, "%s not found" % what)
    return m


def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=TOP, capture_output=True)
    if r.returncode != 0:
        refuse(3, "git %s failed" % " ".join(args))
    return r.stdout


# ------------------------------------------------------------------------------------------------------------------------ models
def ladder(cu, cd, i_in, vin, vout, f, L, t_rf, rb, lb, r59, l59, bulk, dt=1e-9, periods=25):
    """MODELED, P0-7: the record's periodic operating model (sense_ripple, round 3 of B6), written out so that the bank's own
    inductance lb and a missing RSENSE1 (r59 None: one node behind the bank) can be taken, and returning the last period's
    waveforms: the bank's current, the voltage across the bank (rb i + lb di/dt, what a Kelvin pair at its pads reads), the voltage
    across RSENSE1 and its current. With lb = 0 and r59 given it is sense_ripple's network term for term (verified in section 2d).
    Nodes: P (the bulk (esr, C) and the source, a current source), A (cu: (C, ESR, ESL), or none), C (cd, and M1's pulsed draw)."""
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
    esr_b, cb = bulk
    Cd, rd_, ld = cd
    Cu, ru, lu = (1.0, 1e12, 0.0) if cu is None else cu
    vb = vu = vd = vin
    iu = idn = i59 = ib = 0.0
    n = int(round(T / dt))
    out = []
    for k in range(n * periods):
        t = (k + 1) * dt
        im = i_m1(t)
        zb, eb = dt / cb + esr_b, vb
        zu, eu = dt / Cu + ru + lu / dt, vu - (lu / dt) * iu
        zd, ed = dt / Cd + rd_ + ld / dt, vd - (ld / dt) * idn
        zk, ek = rb + lb / dt, -(lb / dt) * ib                     # the bank, with its own inductance (lb = 0: the record's rb)
        if r59 is None:
            # two nodes: P and S (cu and cd both on S, M1 drawn from S)
            a11, a12, b1 = 1.0 / zb + 1.0 / zk, -1.0 / zk, i_in + eb / zb + ek / zk
            a21, a22, b2 = 1.0 / zk, -1.0 / zk - 1.0 / zu - 1.0 / zd, im + ek / zk - eu / zu - ed / zd
            det = a11 * a22 - a12 * a21
            vP, vS = (b1 * a22 - a12 * b2) / det, (a11 * b2 - a21 * b1) / det
            vA = vC = vS
            ib = (vP - vS - ek) / zk
            i59 = ib
        else:
            z59, e59 = r59 + l59 / dt, -(l59 / dt) * i59
            a11, a12, b1 = 1.0 / zb + 1.0 / zk, -1.0 / zk, i_in + eb / zb + ek / zk
            a21, a22, a23, b2 = 1.0 / zk, -1.0 / zk - 1.0 / zu - 1.0 / z59, 1.0 / z59, -ek / zk - eu / zu - e59 / z59
            a32, a33, b3 = 1.0 / z59, -1.0 / z59 - 1.0 / zd, im + e59 / z59 - ed / zd
            m_ = a21 / a11
            a22p, b2p = a22 - m_ * a12, b2 - m_ * b1
            m2_ = a32 / a22p
            vC = (b3 - m2_ * b2p) / (a33 - m2_ * a23)
            vA = (b2p - a23 * vC) / a22p
            vP = (b1 - a12 * vA) / a11
            ib = (vP - vA - ek) / zk
            i59 = (vA - vC - e59) / z59
        iu, idn = (vA - eu) / zu, (vC - ed) / zd
        vb += (vP - eb) / zb * dt / cb
        vu += iu * dt / Cu
        vd += idn * dt / Cd
        if k >= n * (periods - 1):
            out.append((ib, vP - vA, vA - vC, i59))
    return dict(ib=[o[0] for o in out], vbank=[o[1] for o in out], v59=[o[2] for o in out], i59=[o[3] for o in out],
                i_v=i_v, i_p=i_p, il_avg=il_avg, dI=dI, D=D)


def clip_avg(xs, lo=0.0, hi=None):
    return sum(min(max(x, lo), hi) if hi is not None else max(x, lo) for x in xs) / len(xs)


def lowpass(xs, tau, dt):
    """A first-order filter run twice around one period (the periodic steady state), backward Euler."""
    y = sum(xs) / len(xs)
    for _ in range(2):
        out = []
        for x in xs:
            y += (x - y) * dt / (tau + dt)
            out.append(y)
    return out


# ------------------------------------------------------------------------------------------------------------------------ compute
def compute():
    O = {}
    LS = load("l4e7_stage_settings_for_p0sol", LS_PY)
    for rel, pin_ in ((LT, LS.PINS[LT]), (T48, LS.PINS[T48]), (XAL, LS.PINS[XAL])):
        if sha(rel) != pin_:
            refuse(2, "%s is not the file the L4-E7 record pins" % rel)
    for pn in ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN"):
        if sha(SAMH % pn) != LS.PINS[SAMH % pn]:
            refuse(2, "%s is not the file the L4-E7 record pins (its fetch_maker_curves.py)" % (SAMH % pn))
    for rel in (I169, TPS, WSL):
        if not os.path.isfile(os.path.join(TOP, rel)):
            refuse(3, "%s is not held (the L4-E7 record's fetch_held_back.py)" % rel)
    O["pins"] = [(sha(rel), rel) for rel in (LS_PY, LS_OUT, LS_CACHE, DRAFT, REC + "/apply_gen_sch_e_p0sol_b2.py", GEN_E, NET_E, L4E11_OUT, LT, I169, TPS, T48, WSL, XAL)
                 + tuple(SAMH % pn for pn in ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN")) + RTJ + (LC44322,)]
    data = json.load(open(os.path.join(TOP, LS_CACHE), encoding="utf-8"))
    R = LS._dec(data["R"])
    # ================================================================== 0. REPRODUCTION ON THE BASE
    # 0a. the cache's KEY: the parts that differ on this tree, and the figures compute() reads from the one input that changed
    parts_now = LS.key_parts(data["parts"]["files"])
    O["key_holds"] = LS.key_of(parts_now) == data["key"]
    diff = []
    for part_ in data["parts"]:
        if part_ == "files":
            diff += [("files", f_, data["parts"]["files"][f_], parts_now["files"].get(f_)) for f_ in sorted(data["parts"]["files"])
                     if data["parts"]["files"][f_] != parts_now["files"].get(f_)]
        elif data["parts"][part_] != parts_now[part_]:
            diff.append((part_, None, None, None))
    O["key_diff"] = diff
    if [(d_[0], d_[1]) for d_ in diff] != [("files", L4E11_OUT)]:
        refuse(4, "the cache's KEY differs from this tree in more than %s: %s" % (L4E11_OUT, [(d_[0], d_[1]) for d_ in diff]))
    src_ls = open(os.path.join(TOP, LS_PY), encoding="utf-8").read()
    pats = ((r"UVLO: on at ([\d.]+) / ([\d.]+) / ([\d.]+) V, off at", "UVLO rising"),
            (r"UVLO: on at [\d.]+ / [\d.]+ / [\d.]+ V, off at ([\d.]+) / ([\d.]+) / ([\d.]+) V of DC_P", "UVLO falling"),
            (r"the start: slew ([\d.]+) / ([\d.]+) / ([\d.]+) V/ms", "the start's slew"),
            (r"INP high from DC_P ([\d.]+) V", "INP high"),
            (r"short circuit ([\d.]+) / ([\d.]+) / ([\d.]+) A;", "the short-circuit threshold"),
            (r"overcurrent ([\d.]+) / ([\d.]+) / ([\d.]+) A \(the printed row", "the overcurrent threshold"))
    old_o11 = LS.flat(git("show", "%s:%s" % (CACHE_AT, L4E11_OUT)).decode("utf-8"))
    new_o11 = LS.flat(open(os.path.join(TOP, L4E11_OUT), encoding="utf-8").read())
    rows0 = []
    for pat_, what_ in pats:
        if repr(pat_)[1:-1].replace("\\\\", "\\") not in src_ls and pat_ not in src_ls:
            refuse(4, "the record no longer reads %s with the pattern used here" % what_)
        a_, b_ = re.search(pat_, old_o11), re.search(pat_, new_o11)
        if not a_ or not b_:
            refuse(3, "%s not found in one version of %s" % (what_, L4E11_OUT))
        rows0.append((what_, a_.groups(), b_.groups()))
    O["o11"] = rows0
    O["o11_sha"] = (hashlib.sha256(git("show", "%s:%s" % (CACHE_AT, L4E11_OUT))).hexdigest(), sha(L4E11_OUT))
    if any(a_ != b_ for _w, a_, b_ in rows0):
        refuse(4, "a figure the record reads from %s changed: the cache is stale" % L4E11_OUT)
    # 0b. render(cache) against the committed .out
    text_ = "\n".join(LS.render(R)) + "\n"
    committed = open(os.path.join(TOP, LS_OUT), encoding="utf-8").read()
    O["render_same"] = text_ == committed
    if not O["render_same"]:
        refuse(4, "render(cache) is not the committed %s" % LS_OUT)
    O["out_sha"] = hashlib.sha256(committed.encode("utf-8")).hexdigest()
    # 0c. D-16, recomputed by the record's sense_ripple on its cached parameters
    b6 = R["remedy"]["b6"]
    r3 = b6["r3"]
    G6 = dict(b6["G6"])
    row0, rowF = r3["rows"][0], r3["rows"][6]
    if not row0["lab"].startswith("A, as drafted") or not rowF["lab"].startswith("Figure 1"):
        refuse(3, "the cached round-3 rows are not the as-drafted split and Figure 1")
    r59_hi, rb_lo, bulk_op = G6["r59"], G6["rb"], r3["bulk_op"]
    i_reg_hi, i_op, v_oc, lo_h = r3["i_reg_hi"], r3["i_op"], r3["v_oc"], r3["lo_h"]
    F_LO, L1_LO, T_RF, L59 = r3["F_LO"], r3["L1_LO"], r3["T_RF"], r3["L59"]
    rep16 = []
    for vo_ in r3["V_OUTS"]:
        for ii_ in (i_reg_hi, i_op):
            s_ = LS.sense_ripple(row0["cu"], row0["cd"], ii_, v_oc, vo_, F_LO, L1_LO, T_RF, r59_hi, L59, rb_lo, bulk_op)
            c_ = row0["op"][(vo_, ii_)]
            rep16.append((vo_, ii_, s_, max(abs(s_[k_] - c_[k_]) for k_ in ("peak", "trough", "avg", "avg_clip", "r_peak"))))
    edge = LS.sense_ripple(row0["cu"], row0["cd"], i_reg_hi, v_oc, 12.0, F_LO, L1_LO, 10e-9, r59_hi, L59, rb_lo, bulk_op, dt=0.5e-9)
    O["d16"] = dict(rows=rep16, edge=edge, edge_diff=abs(edge["trough"] - r3["op_edge"]["trough"]),
                    r_peak=(row0["r_peak_reg"], row0["r_peak_trip"]), pins=(row0["op_trough"], row0["op_peak"]),
                    err=(row0["err_reg"], row0["err_trip"]), fig1=(rowF["r_peak_reg"], rowF["op_trough"], rowF["op_peak"]))
    if max(d_[3] for d_ in rep16) > 0.0 or O["d16"]["edge_diff"] > 0.0:
        refuse(4, "D-16 does not reproduce: %s" % [(d_[0], d_[1], d_[3]) for d_ in rep16])
    # 0d. D-10, recomputed by the record's guard_event_b with every bank rebuilt from the held curves at the cached bounds
    SAM = {pn: json.load(open(os.path.join(TOP, SAMH % pn), encoding="utf-8")) for pn in ("CL31B106KBHNNN", "CL32B106KBJNNN", "CL32B225KCJSNN")}
    BAND = b6["BAND"]

    def part(cnt_, cn_, pn_, side_):
        if pn_ is None:
            return (cnt_, cn_, None, 1.10, 1.10)
        lo_, hi_ = b6["bounds"][pn_][0]
        fac_ = 0.90 * (1 - BAND) * lo_ if side_ == "lo" else 1.10 * (1 + BAND) * hi_
        return (cnt_, cn_, SAM[pn_]["dc_bias_V_percent"], fac_, 1.10)

    def banks_q(sF_, sP_, sS_, sC_, merged=False):
        nc_ = lambda c_, cn_: (c_, cn_, None, 1.10 if sC_ == "hi" else 0.25, 1.10)
        bS_ = [part(4, 10e-6, "CL32B106KBJNNN", sS_)]
        bC_ = [part(2, 10e-6, "CL31B106KBHNNN", sC_), nc_(1, 4.7e-6), nc_(1, 0.1e-6)]
        return dict(bF=LS.CerBank([part(4, 2.2e-6, "CL32B225KCJSNN", sF_)]), bP=LS.CerBank([part(2, 10e-6, "CL32B106KBJNNN", sP_)]),
                    bS=LS.CerBank(bS_), bC=LS.CerBank(bC_))
    GA = dict(G6, **banks_q("lo", "lo", "lo", "hi"))
    for k_, (lo_, hi_) in (("F_lo", (36.0, 75.0)), ("P_lo", (7.46, 30.0)), ("S_lo", (7.46, 30.0)), ("C_hi", (7.46, 30.0))):
        bk_ = {"F_lo": GA["bF"], "P_lo": GA["bP"], "S_lo": GA["bS"], "C_hi": GA["bC"]}[k_]
        if abs(bk_.C(lo_) - b6["ceff"][k_][0]) > 1e-15 or abs(bk_.C(hi_) - b6["ceff"][k_][1]) > 1e-15:
            refuse(4, "a rebuilt bank is not the record's (%s)" % k_)
    c_bulk_max = R["decision"]["c"]["c_bulk_max"]
    bk6 = ((0.0, c_bulk_max), b6["bulk_cold"], bulk_op)
    st6 = ((b6["uvf_lo"], 0.0), (lo_h, 0.0), (lo_h, i_op), (v_oc, 0.0), (v_oc, i_op))
    d11h, d11c = b6["d11"]
    R_CASES = tuple(b6["r_cases"])
    ERR = b6["ERR"]
    L_KEL = r3["L_KEL"]
    keys_max = ("vF", "vP", "vS", "i4", "e4", "i11", "e11", "iQ", "iL", "vds", "slew", "u5", "u18", "di59", "di59_up", "u5L")
    keys_min = ("vFmin", "vdsmin", "u5n", "u18n", "di59_dn", "u5Ln")

    def evalR(L_, g_, starts=st6, cases=R_CASES, cold=False, bulks=None, ramp=None):
        W_ = {k_: -1e9 for k_ in keys_max}
        W_.update({k_: 1e9 for k_ in keys_min})
        W_["case"] = {}
        for (v0_, i0_), rl_ in itertools.product(starts, cases):
            for bk_ in (bulks or (bk6[:1] if cold else bk6)):
                for d11_ in (d11h, d11c):
                    g2_ = dict(g_, d11=d11_, r_lead=rl_)
                    r_ = LS.guard_event_b(g2_, v0_, i0_, L_, bk_, cold=cold)
                    for k_ in keys_max:
                        W_[k_] = max(W_[k_], r_[k_])
                    for k_ in keys_min:
                        W_[k_] = min(W_[k_], r_[k_])
                    c_ = W_["case"].setdefault(rl_, dict(u18=-1e9, u5=-1e9))
                    c_["u18"], c_["u5"] = max(c_["u18"], r_["u18"]), max(c_["u5"], r_["u5"])
        return W_
    L_REF = b6["L_REF"]
    WA = evalR(L_REF, dict(GA, l59=L59))
    pA0 = evalR(L_REF, dict(GA, l59=L59), cases=(0.0,))
    pAr = evalR(L_REF, dict(GA, l59=L59), cases=(R_CASES[1],))
    budget = lambda W_: (W_["u5Ln"] - ERR + L_KEL * W_["di59_dn"], W_["u5L"] + ERR + L_KEL * W_["di59_up"])
    rep10 = dict(u5=WA["u5"], u5_err=WA["u5"] + ERR, pins0=budget(pA0), pinsr=budget(pAr), vF=WA["vF"], iQ=WA["iQ"], u18=WA["u18"],
                 vS=WA["vS"], vP=WA["vP"], vds=WA["vds"], slew=WA["slew"], kinp=b6["kinp"])
    cache10 = dict(u5=b6["W"]["u5"], pins0=(r3["parA0"]["lo"], r3["parA0"]["hi"]), pinsr=(r3["parAr"]["lo"], r3["parAr"]["hi"]),
                   vF=b6["W"]["vF"], iQ=b6["W"]["iQ"], u18=b6["W"]["u18"])
    d10_diff = max(abs(rep10["u5"] - cache10["u5"]), abs(rep10["vF"] - cache10["vF"]), abs(rep10["iQ"] - cache10["iQ"]),
                   abs(rep10["u18"] - cache10["u18"]), max(abs(a_ - b_) for a_, b_ in zip(rep10["pins0"] + rep10["pinsr"], cache10["pins0"] + cache10["pinsr"])))
    # the cold connection at the envelope's least loop, a fault at the connector, the port bank at its least and its largest
    grid6 = [0.30e-6 * 1.1 ** j_ for j_ in range(38)]
    bF_hi = LS.CerBank([part(4, 2.2e-6, "CL32B225KCJSNN", "hi")])
    cold_st = ((0.0, 0.0), (v_oc, 0.0))
    Wc = [evalR(grid6[0], dict(GA, bF=bf_), starts=cold_st, cases=(0.0,), cold=True) for bf_ in (GA["bF"], bF_hi)]
    cold = dict(vF=max(w_["vF"] for w_ in Wc), slew=max(w_["slew"] for w_ in Wc))
    cold_diff = max(abs(cold["vF"] - b6["cold_c"]["vF"]), abs(cold["slew"] - b6["cold_c"]["slew"]) * 1e-6)
    O["d10"] = dict(rep=rep10, cache=cache10, diff=d10_diff, cold=cold, cold_diff=cold_diff, L_REF=L_REF, ERR=ERR, grid=(grid6[0], grid6[-1]),
                    W1=b6["W1u"], W03=b6["W03"], n=len(st6) * len(R_CASES) * len(bk6) * 2, lsA=b6["lsA"], pvf80=b6["pvf80"],
                    cold_from=b6["cold_from"], slew_abs=b6["slew_abs"], pin_abs=R["remedy"]["T48"]["pin_abs"], vs_rec=b6["vs_rec"])
    if d10_diff > 1e-9 or cold_diff > 1e-6:
        refuse(4, "D-10 does not reproduce (%.3g, %.3g)" % (d10_diff, cold_diff))

    # ================================================================== the makers' rows used from here (each read from its held sheet)
    lt2, lt4, lt5 = LS.flat(LS.pg(LT, 2, False)), LS.flat(LS.pg(LT, 4)), LS.flat(LS.pg(LT, 5))
    lt12, lt29, lt30, lt31 = (LS.flat(LS.pg(LT, p_, False)) for p_ in (12, 29, 30, 31))
    abs_cs = float(need(lt2, r"VCSP-VCSN, VCSPIN-VCSNIN, VCSPOUT-VCSNOUT\.+ .0\.3V to (0\.3)V", "8705af p.2 the sense pins' differential").group(1))
    abs_imon = float(need(lt2, r"IMON_IN, IMON_OUT Voltage\.+ .0\.3V to (\d)V", "8705af p.2 IMON_IN's voltage").group(1))
    v_op = float(need(lt5, r"CSPIN, CSNIN Differential Operating Voltage Range l .(\d+) (\d+) mV", "8705af p.5 the operating range").group(2)) * 1e-3
    vreg = tuple(float(x_) for x_ in need(lt4, r"Regulation Voltages for IMON_IN and IMON_OUT VC = 1\.2V l ([\d.]+) ([\d.]+) ([\d.]+) V", "8705af p.4 IMON_IN's regulation").groups())
    line_p = float(need(lt4, r"Line Regulation for IMON_IN and IMON_OUT Error Amp VIN = 12V to 80V; Not Switching [\d.]+ ([\d.]+) %/V", "8705af p.4 the line regulation").group(1))
    ovt = tuple(float(x_) for x_ in need(lt5, r"IMON_IN Overvoltage Threshold l ([\d.]+) ([\d.]+) ([\d.]+) V", "8705af p.5 IMON_IN's fault").groups())
    ea2 = float(need(lt5, r"IMON_IN Error Amp EA2 Voltage Gain (\d+) V/V", "8705af p.5 EA2's gain (typical)").group(1))
    need(lt12, r"Connect this pin to VIN when not in use", "8705af p.12 CSPIN and CSNIN to VIN when not in use")
    need(lt29, r"Tie both pins to VIN if they are not being used", "8705af p.29 CSPIN and CSNIN to VIN")
    need(lt30, r"do not place resistors in series with any of the CSxIN or CSxOUT pins", "8705af p.30 no series resistor")
    need(lt31, r"tie the CSPIN and CSNIN pins to VIN and tie the IMON_IN pin to ground when the input current sensing is not in use", "8705af p.31 the unused arrangement")
    need(lt31, r"Negative CSPIN to CSNIN voltages are not multiplied and no current flows out of IMON_IN in that case", "8705af p.31 A7 never sinks")
    need(lt31, r"IMON_IN voltages exceeding 1\.208V \(typical\) cause the VC voltage to reduce", "8705af p.31 EA2 acts on the pin's voltage")
    need(lt31, r"Additional capacitance, bringing the CIMON_IN total to 0\.1.F to 1.F, may be necessary to maintain loop stability", "8705af p.31 CIMON_IN 0.1 to 1 uF")
    j6, j4 = LS.flat(LS.pg(I169, 6)), LS.flat(LS.pg(I169, 4))
    need(j6, r"INA169: all other characteristics at TA = .40.C to \+85.C V\+ = 5 V, VIN\+ = 12 V, and ROUT = 25 k[ΩΩ]", "INA169 p.6 the header")
    cmr169 = float(need(j6, r"INA169: (\d+) 120 dB VIN\+ = 2\.7 V to 60 V, VSENSE = 50 mV", "INA169 p.6 CMR").group(1))
    vos169 = float(need(j6, r"INA169 ±0\.2 ±(\d+) vs\. temperature", "INA169 p.6 offset").group(1)) * 1e-3
    psr169 = float(need(j6, r"INA169: 0\.1 (\d+) µV/V V\+ = 2\.7 V to 60 V, VSENSE = 50 mV", "INA169 p.6 PSR").group(1)) * 1e-6
    gm169 = tuple(float(x_) * 1e-6 for x_ in need(j6, r"VSENSE = 10 mV . 150 mV (\d+) 1000 (\d+) µA/V", "INA169 p.6 transconductance").groups())
    nl169 = float(need(j6, r"INA169 ±0\.01% ±([\d.]+)%", "INA169 p.6 nonlinearity").group(1)) / 100.0
    fs169 = float(need(j6, r"Full-scale sense voltage VSENSE = VIN\+ . VIN. 100 (\d+) mV", "INA169 p.6 full-scale sense voltage").group(1)) * 1e-3
    bw169 = float(need(j6, r"Bandwidth ROUT = 20 k[ΩΩ] (\d+) kHz", "INA169 p.6 bandwidth at 20 kOhm (typical)").group(1)) * 1e3
    ro169 = float(need(j6, r"Output impedance (\d+) \|\| 5 G[ΩΩ] \|\| pF", "INA169 p.6 output impedance (typical)").group(1)) * 1e9
    iq169 = float(need(j6, r"Quiescent current VSENSE = 0, IO = 0 \d+ (\d+) µA", "INA169 p.6 quiescent").group(1)) * 1e-6
    abs169 = tuple(float(x_) for x_ in need(j4, r"\(2\) Common-mode .0\.3 (\d+) V Analog inputs, INA169 Differential \(VIN\+\) . \(VIN.\) .40 (\d+) V", "INA169 p.4 absolute maxima").groups())
    t5 = LS.flat(LS.pg(TPS, 5))
    vit = need(t5, r"VIT\+\(INB\) INB pin positive input threshold voltage VDD = 1\.8 V to 36 V (\d+) (\d+) (\d+) mV", "TPS3701 p.5 VIT+(INB)").groups()
    vth = (float(vit[0]) * 1e-3, float(vit[2]) * 1e-3)
    iin_t = float(need(t5, r"VDD = 1\.8 V and 36 V, VINA, VINB = 6\.5 V .(\d+) \+1 \+\d+ nA", "TPS3701 p.5 input current").group(1)) * 1e-9
    w2, w3 = LS.flat(LS.pg(WSL, 2)), LS.flat(LS.pg(WSL, 3))
    wtcr = float(need(w2, r"± (\d+) for 7 mΩ to 500 mΩ", "WSL p.2 TCR").group(1)) * 1e-6
    wlife = tuple(float(x_) for x_ in need(w3, r"Load life 1000 h at rated power, \+ 70 °C.*?± \(([\d.]+) % \+ ([\d.]+) Ω\)", "WSL p.3 load life").groups())
    wsold = tuple(float(x_) for x_ in need(w3, r"Resistance to solder heat .*?± \(([\d.]+) % \+ ([\d.]+) Ω\)", "WSL p.3 solder heat").groups())
    w1 = LS.flat(LS.pg(WSL, 1))
    wsl_l = tuple(float(x_) * 1e-9 for x_ in need(w1, r"(0\.5) nH to (5) nH", "WSL p.1 the inductance (typical span)").groups())
    t48_6 = LS.flat(LS.pg(T48, 9))
    inp_h = float(need(t48_6, r"V\(INP_H\) ([\d.]+) ([\d.]+) V", "TPS4811 p.9 V(INP_H)").group(2))
    inp_l = float(need(t48_6, r"V\(INP_L\) ([\d.]+) ([\d.]+) V", "TPS4811 p.9 V(INP_L)").group(1))
    imon_os = float(need(t48_6, r"V\(OS_SET\) .(\d+) (\d+) .V", "TPS4811 p.9 IMON's offset").group(2)) * 1e-6
    imon_ge = float(need(t48_6, r"V\(GE_SET\) Gain error \(VSNS to V\(IMON\) scaling\) .*?.([\d.]+) ([\d.]+) %", "TPS4811 p.9 IMON's gain error").group(2)) / 100.0
    xal1 = LS.flat(LS.pg(XAL, 1))
    xrow = need(xal1, r"XAL1510-103ME_\s+10\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", "XAL1510 p.1 the 10 uH row").groups()
    O["rows"] = dict(abs_cs=abs_cs, abs_imon=abs_imon, v_op=v_op, vreg=vreg, line_p=line_p, ovt=ovt, ea2=ea2, cmr169=cmr169, vos169=vos169,
                     psr169=psr169, gm169=gm169, nl169=nl169, fs169=fs169, bw169=bw169, ro169=ro169, iq169=iq169, abs169=abs169, vth=vth,
                     iin_t=iin_t, wtcr=wtcr, wlife=wlife, wsold=wsold, wsl_l=wsl_l, inp_h=inp_h, inp_l=inp_l, imon_os=imon_os, imon_ge=imon_ge,
                     xal=xrow)
    # the record's resistor conventions (YAGEO RT: 0.1 %, 25 ppm/K, its printed load-life and solder-heat limits), its two ends
    tol_y, tcr_y, life_y, sold_y = R["tol_y"], R["tcr_y"], R["life_y"], R["sold_y"]
    t_cold, t_air = R["t_cold"], R["t_air"]
    dt_end = max(abs(t_cold - 25.0), abs(t_air - 25.0))
    G_CM = R["decision"]["c"]["g_cm"]
    dvc = 1.5                                        # VC's range the replay takes (L4-E7's corner check, EA2 at its gain), V
    EA2_DIV, LINE_MUL = LS.EA2_FLOOR_DIV, LS.LINE_FLOOR_MUL

    def rtf(r_, sgn, aged):
        f_ = (1 + sgn * tol_y) * (1 + sgn * tcr_y * dt_end)
        if aged:
            f_ *= (1 + sgn * (life_y[0] + life_y[1] / r_)) * (1 + sgn * (sold_y[0] + sold_y[1] / r_))
        return f_
    cdec = R["decision"]["c"]
    rp, nb, R66 = cdec["rp"], cdec["n"], cdec["r66"]
    R65 = 16900.0

    def rdrift(sgn, aged):
        f_ = (1 + sgn * 0.01) * (1 + sgn * wtcr * dt_end)
        if aged:
            f_ *= (1 + sgn * (wsold[0] / 100.0 + wsold[1] / rp)) * (1 + sgn * (wlife[0] / 100.0 + wlife[1] / rp))
        return f_
    rbank = rp / nb
    rb_hi, rb_lo = rbank * rdrift(1, True), rbank * rdrift(-1, True)

    def ina_out(v, base, sgn):
        """The INA169's terms on top of base (V of sense), at input and supply voltage v, the record's vs_trip terms: offset, CMR and
        PSR (printed at VSENSE 50 mV), and the move between the 50 mV row and base (G_CM, the record's SESSION assumption)."""
        rej = 10 ** (-cmr169 / 20.0) * abs(v - 12.0) + psr169 * abs(v - 5.0)
        d1 = G_CM * abs(base + sgn * (vos169 + rej) - 0.050)
        return base + sgn * (vos169 + rej + d1)

    def vs_trip(v, sgn, aged):
        """The record's trip (L4-E7R's vs_trip): U19's INB threshold and input current through R66; U18 into R65 + R66."""
        vit_ = vth[1] if sgn > 0 else vth[0]
        gm_ = (gm169[0] if sgn > 0 else gm169[1]) * (1 - sgn * nl169)
        rr = R66 * rtf(R66, -sgn, aged)
        base = (vit_ + sgn * iin_t * rr) / (gm_ * rr)
        out_ = ina_out(v, base, sgn)
        return out_ + sgn * base * abs(R65 * rtf(R65, -sgn, aged) + rr - 25e3) / ro169
    trip_check = (vs_trip(v_oc, -1, True), vs_trip(v_oc, 1, True), vs_trip(v_oc, -1, True) / rb_hi, vs_trip(v_oc, 1, True) / rb_lo)
    if abs(trip_check[0] - cdec["vs_lo"]) > 1e-12 or abs(trip_check[1] - cdec["vs_hi"]) > 1e-12 or abs(trip_check[2] - cdec["i_lo_aged"]) > 1e-9 \
            or abs(trip_check[3] - cdec["i_hi25"]) > 1e-9:
        refuse(4, "the trip does not reproduce the record's: %s against %s" % (trip_check, (cdec["vs_lo"], cdec["vs_hi"], cdec["i_lo_aged"], cdec["i_hi25"])))
    O["trip"] = dict(lo=trip_check[0], hi=trip_check[1], i_lo=trip_check[2], i_hi=trip_check[3], rb=(rb_lo, rbank, rb_hi))

    # ================================================================== 1. THE ALTERNATIVES' COMMON TOOL: M2 (CS101) WITH THE SENSE MOVED
    cs = R["cs101"]
    gm2, a5, R5v, v_out = cs["gm2"], cs["a5"], cs["r5"], cs["v_out"]
    za_esr, c_can = 0.040, 33e-6 * 1.2 * 1.3            # the record's ZA bulk part (esr from new_20 x 3; c_can_max)
    if abs(bulk_op[0] * 3 - za_esr) > 1e-12 or abs(3 * c_can - c_bulk_max) > 1e-12:
        refuse(4, "the bulk's figures are not the record's")
    c_a, c66_, c_b = 4 * 10e-6 * 1.10, 0.1e-6 * 1.10, (10e-6 + 10e-6 + 4.7e-6 + 0.1e-6) * 1.10
    v101, v150, fk = 10 ** (126.0 / 20) * 1e-6, 10 ** (96.5 / 20) * 1e-6, 5e3
    need(open(os.path.join(TOP, LS_OUT), encoding="utf-8").read().replace("\n", " "), r"curve 2 \(sources of 28 V or below\): 126 dBuV, 2\.00 V rms, at\s+the EUT's input to the knee \(read from Figure CS101-1 at 5 kHz\), then the straight line to 96\.5 dBuV at 150 kHz", "the record's CS101 levels")
    V101 = lambda f_: v101 if f_ <= fk else v101 * (v150 / v101) ** (math.log(f_ / fk) / math.log(150e3 / fk))

    def zvc(w_):
        return 1.0 / (gm2 / ea2 + 1j * w_ * 100e-12 + 1.0 / (10e3 + 1.0 / (1j * w_ * 4.7e-9)))

    def loop_t(f_, gsense, rm_, cim_, vin_, f_amp=None):
        """MODELED, typical rows (the record's loop_t): the sense's gain (A/A into IMON_IN) into RIMON_IN with CIMON_IN, EA2, VC's
        network, A5 over R5 and the duty; f_amp, an amplifier's own pole (the INA169's, TYPICAL bandwidth)."""
        w_ = 2 * math.pi * f_
        zim = rm_ / (1 + 1j * w_ * rm_ * cim_)
        amp = 1.0 / (1 + 1j * f_ / f_amp) if f_amp else 1.0
        return gsense * amp * zim * gm2 * zvc(w_) * (a5 / R5v) * min(1.0, v_out / vin_)

    def y_bulk(w_):
        return 3.0 / (za_esr + 1.0 / (1j * w_ * c_can))

    def s1_old(f_, i_, vin_):
        """The accepted design (the record's y_behind, layout 'ahead'): R59's branch inside the loop, C71 to C74 and C66 outside it."""
        w_ = 2 * math.pi * f_
        T_ = loop_t(f_, 1e-3 * R["rs"], 31600.0, 100e-9, vin_)
        y_ = 1j * w_ * (c_a + c66_) + (1j * w_ * c_b - i_ / vin_) / (1 + T_)
        return V101(f_) * math.sqrt(2) / abs(rbank + 1.0 / y_)

    def s1_port(f_, gsense, rm_, cim_, i_, vin_):
        """The sense ahead of the bulk (alternative A; or C at R87): the loop holds the port current, the bulk's and the bank's."""
        w_ = 2 * math.pi * f_
        T_ = loop_t(f_, gsense, rm_, cim_, vin_)
        yx, yc = 1j * w_ * (c_a + c66_ + c_b), -i_ / vin_
        return V101(f_) * math.sqrt(2) * abs(((yx + yc) - T_ * y_bulk(w_)) / ((1 + T_) + rbank * (yx + yc)))

    def s1_bank(f_, rm_, cim_, i_, vin_, ls_=1.0, cu_=0.1e-6 * 1.10):
        """The selected sensing (C): the loop holds the bank's own current, everything behind the bank inside it."""
        w_ = 2 * math.pi * f_
        T_ = loop_t(f_, 1e-3 * rbank, rm_, cim_, vin_, f_amp=bw169 * 20e3 / rm_)
        yx = ls_ * (1j * w_ * (c_a + c66_ + c_b + cu_) - i_ / vin_)
        return V101(f_) * math.sqrt(2) / abs(rbank + (1 + T_) / yx)
    best = cs["best"]
    tau_lo = best["tau"][0]
    m2_rep = max(abs(max(s1_old(f_, i_reg_hi, v_) for v_ in (lo_h, v_oc)) - r_) / r_ for f_, r_, _rf in best["rip"])
    if m2_rep > 1e-12:
        refuse(4, "the record's CS101 spectrum does not reproduce (%.3g)" % m2_rep)
    freqs = [f_ for f_, _r, _rf in best["rip"]]
    H = lambda f_: 1.0 / abs(1 + 1j * 2 * math.pi * f_ * tau_lo)

    def spectrum(fn):
        return [(f_, max(fn(f_, v_) for v_ in (lo_h, v_oc))) for f_ in freqs]
    sp_old = [(f_, r_) for f_, r_, _rf in best["rip"]]
    sp_A = spectrum(lambda f_, v_: s1_port(f_, 1e-3 * R["rs"], 31600.0, 100e-9, i_reg_hi, v_))
    G_C1 = 0.9 / 100.0 * 4.5e-3                       # U21's IMON (TPS4811 eq. 13, RSET 100 Ohm) on R87 4.5 mOhm, A/A
    rm_C1 = 1e-3 * R["rs"] * 31600.0 / G_C1           # the same volts per amp at IMON_IN as the accepted setting
    sp_C1 = spectrum(lambda f_, v_: s1_port(f_, G_C1, rm_C1, 100e-9 * 31600.0 / rm_C1, i_reg_hi, v_))
    worst = lambda sp_: max(((f_, r_, r_ * H(f_)) for f_, r_ in sp_), key=lambda x_: x_[2])
    O["m2"] = dict(rep=m2_rep, old=worst(sp_old), A=worst(sp_A), C1=worst(sp_C1), margin_old=best["m"], loop_old=best["loop_be"], tau=tau_lo,
                   rm_C1=rm_C1, G_C1=G_C1, n=len(freqs), sp_old=sp_old, sp_A=sp_A, sp_C1=sp_C1,
                   lowA=[(f_, r_, r_ * H(f_)) for f_, r_ in sp_A if r_ * H(f_) > best["m"]])

    # ================================================================== (A) the sense ahead of every bank: the fault case on the record's model
    GAa = dict(GA, r_on=G6["r_on"] + r59_hi, l59=0.0)
    WAa = evalR(L_REF, GAa)
    O["A"] = dict(u5=WAa["iQ"] * r59_hi, iQ=WAa["iQ"], abs_cs=abs_cs)
    # its normal case: the sense carries the port's current, the bulk and every ceramic behind it (Figure 1 extended to the bulk)
    cd_all = rowF["cd"]
    # (INFERRED: the source behind the lead is a current source at the switching frequency (the record's operating model), so a sense
    # ahead of the bulk reads the source's own flat current; the port bank's share of the ripple through R87, Q12 and the sense is left out)
    O["A"].update(op=i_reg_hi * r59_hi)

    # ================================================================== (B) the guard-on event bounded or removed
    xal_isat = float(xrow[3])
    isc_hi = G6["isc"]
    t_sc = G6["t_sc"]
    dv_step = 36.0 - b6["uvf_lo"]
    l_ch = 10e-6 * 0.80                               # XAL1510-103 at its -20 % (the sheet's tolerance)
    i_cut_b1 = isc_hi + dv_step / (l_ch + grid6[0]) * t_sc
    c_entry = cdec["c_entry_max"]
    f_res = [1.0 / (2 * math.pi * math.sqrt((l_ + 3.30e-6) * c_entry)) for l_ in (l_ch, 10e-6 * 1.2)]
    O["B"] = dict(isat=xal_isat, i_cut=i_cut_b1, isc=isc_hi, t_sc=t_sc, l_ch=l_ch, f_res=f_res, c_entry=c_entry, inp_l=inp_l, dv=dv_step)

    # ================================================================== (C) the selected circuit
    # C's sensing: U23 (INA169) on the bank into IMON_IN, R16 and C65; U5's CSPIN and CSNIN tied to VIN (TRK_VS)
    RT = {}
    for rel in RTJ:
        for r_ in json.load(open(os.path.join(TOP, rel), encoding="utf-8"))["rows"]:
            RT[LS.rvalue(r_["model"])] = (r_["code"], r_["model"], r_["stock"])
    lc169 = json.load(open(os.path.join(TOP, LC44322), encoding="utf-8"))
    draft = load("apply_gen_sch_e_p0sol_read", DRAFT)
    R16v = float(draft.R16_NEW[0].rstrip("k")) * 1e3
    R97v = float(draft.R97_NEW[0].rstrip("k")) * 1e3
    if RT.get(R16v, (None,))[0] != draft.R16_NEW[1] or RT.get(R97v, (None,))[0] != draft.R97_NEW[1]:
        refuse(3, "the draft's R16 or R97 code is not the filed JLCPCB reading")
    C65v = 100e-9

    def vreg_c(v, sgn, rm_, aged=True, a7z=0.0):
        """The regulation's sense voltage across the bank (V) at input voltage v, sgn +1 its highest, -1 its lowest: EA2's regulation
        voltage at its printed end, its line term at twice its printed maximum and EA2 at half its typical gain (the record's design
        floor), U23's transconductance and nonlinearity at the end that raises the sense, R16 with tolerance, TCR and aging, and the
        INA169's offset, CMR, PSR and G_CM terms; a7z, A7's own output at zero differential (it only adds to IMON_IN)."""
        vref = vreg[2] if sgn > 0 else vreg[0]
        v_im = vref * (1 + sgn * LINE_MUL * line_p * 1e-2 * (v - V_LINE_REF)) + sgn * dvc / (ea2 / EA2_DIV)
        gm_ = (gm169[0] if sgn > 0 else gm169[1]) * (1 - sgn * nl169)
        rr = rm_ * rtf(rm_, -sgn, aged)
        base = (v_im / rr - a7z) / gm_
        return ina_out(v, base, sgn) + sgn * base * abs(rr - 25e3) / ro169
    vgrid = [lo_h + (v_oc - lo_h) * k_ / 40.0 for k_ in range(41)]

    def margin_c(rm_, a7z=0.0):
        """The correlated margin, A: the trip's least sense voltage less the regulation's highest, over the bank at its highest
        resistance (the same bank under both), the least over the regulation's input range; a7z < 0: A7 sinking (A)."""
        return min((vs_trip(v, -1, True) - vreg_c(v, 1, rm_, a7z=a7z)) / rb_hi for v in vgrid)
    cands = sorted(v_ for v_ in RT if 30e3 <= v_ <= 36e3 and RT[v_][2] >= LS.STOCK_MIN)
    sp_C = {rm_: spectrum(lambda f_, v_, rm_=rm_: s1_bank(f_, rm_, C65v, max(vreg_c(vv_, 1, rm_) / rb_lo for vv_ in (lo_h, v_oc)), v_))
            for rm_ in (R16v,)}
    wC = worst(sp_C[R16v])

    def loop_room(rm_):
        """How many times the loop branch (everything behind the bank, inside the loop) may exceed its typical model before the
        filtered peak spends the margin (the record's loop room)."""
        m_ = margin_c(rm_)
        i_ = max(vreg_c(vv_, 1, rm_) / rb_lo for vv_ in (lo_h, v_oc))
        lo_, hi_ = 1.0, 50.0
        for _ in range(50):
            mid_ = 0.5 * (lo_ + hi_)
            pk_ = max(max(s1_bank(f_, rm_, C65v, i_, v_, ls_=mid_) for v_ in (lo_h, v_oc)) * H(f_) for f_ in freqs)
            lo_, hi_ = (mid_, hi_) if pk_ <= m_ else (lo_, mid_)
        return lo_
    reg = {}
    for rm_ in cands:
        reg[rm_] = dict(nom=vreg[1] / (1e-3 * rm_ * rbank), hi=max(vreg_c(v, 1, rm_) / rb_lo for v in vgrid),
                        lo=min(vreg_c(v, -1, rm_) / rb_hi for v in vgrid), m=margin_c(rm_), code=RT[rm_][0], stock=RT[rm_][2])
    reg_sel = reg[R16v]
    room_sel = loop_room(R16v)
    # the accepted regulation (L4-E7R) for comparison: its nominal and highest, from the cache
    acc = dict(nom=cdec["inom"], hi=cdec["reg_hi25"], m=best["m"], loop=best["loop_be"])
    # A7's output at zero differential: one-sided (8705af p.31), unprinted; its break-even against the accepted nominal
    a7z_rows = [(a_, vreg_c(v_oc, -1, R16v, a7z=a_ * 1e-6) / rb_hi) for a_ in (0.0, 0.5, 1.0, 2.0, 5.0)]

    def sink_be(target_):
        """The sink of A7 (uA) at which the correlated margin falls to target_ (A); A7 is not expected to sink (p.31), INFERRED."""
        lo_, hi_ = 0.0, 50.0
        for _ in range(60):
            mid_ = 0.5 * (lo_ + hi_)
            lo_, hi_ = (mid_, hi_) if margin_c(R16v, a7z=-mid_ * 1e-6) > target_ else (lo_, mid_)
        return lo_
    sink_rows = [(a_, margin_c(R16v, a7z=-a_ * 1e-6)) for a_ in (0.5, 1.0, 2.0)]
    # the static bound and check (b)'s allowance with U23 added: U23's VIN+ pin on PV_P ahead of the bank carries its output current
    # (at the trip's highest sense voltage, its highest transconductance) and its input bias (the record's SESSION assumption, 1 mA),
    # both bypassing the bank as U18's do; C79 adds to the capacitor input energy
    i_b169 = cdec["i_b"]
    pb23 = max(v * (gm169[1] * (1 + nl169) * vs_trip(v, 1, True) + i_b169) for v in vgrid)
    p_static_new = cdec["p_static"] + pb23
    e_cap_new = cdec["e_cap"] + 0.1e-6 * 1.10 * v_oc ** 2
    W_AVG = R["decision"]["w_avg"]
    t_allow_new = ((100.0 - p_static_new) * W_AVG - e_cap_new - cdec["e_f"]) / (cdec["p_src"] - p_static_new)
    t_allow_rep = ((100.0 - cdec["p_static"]) * W_AVG - cdec["e_cap"] - cdec["e_f"]) / (cdec["p_src"] - cdec["p_static"])
    if abs(t_allow_rep - cdec["t_allow"]) > 1e-12:
        refuse(4, "check (b)'s allowance does not reproduce the record's (%.9f against %.9f)" % (t_allow_rep, cdec["t_allow"]))
    O["C"] = dict(R16=R16v, R16code=draft.R16_NEW[1], R97=R97v, R97code=draft.R97_NEW[1], reg=reg, sel=reg_sel, room=room_sel, acc=acc,
                  sink=sink_rows, sink_be_acc=sink_be(best["m"]), pb23=pb23, p_static=(cdec["p_static"], p_static_new),
                  t_allow=(cdec["t_allow"], t_allow_new), t_need=cdec["t_fac"] * cdec["t_resp_typ"], i_b169=i_b169,
                  worst=wC, sp=sp_C[R16v], a7z=a7z_rows, lc169=(lc169.get("model"), lc169.get("stock")), cands=cands,
                  f_amp=bw169 * 20e3 / R16v)
    # (C1) the same alternative with its sense at the port's R87 (U21's IMON), for the record: the regulation would hold the port
    # current, and the loop would push the bulk's CS101 current through the bank (sp_C1 above)
    # (C3) the same alternative with its sense on the drafted RSENSE1 (R59 kept, read by a second INA169 instead of A7; R16 31.6k):
    # the accepted split and M2 topology kept, the regulation independent of the trip; evaluated on both cases, not selected
    tol_h, tcr_h, life_h, sold_h = R["tol_h"], R["tcr_h"], R["life_h"], R["sold_h"]
    r59_lo3 = R["rs"] * (1 - tol_h) * (1 - 2.0 * tcr_h * dt_end) * (1 - life_h) * (1 - sold_h)   # the record's cold-end TCR at twice the printed (ASSUMPTION, as L4-E7's qualification)
    reg3_hi = max(vreg_c(v, 1, 31600.0) / r59_lo3 for v in vgrid)
    m3 = min(vs_trip(v, -1, True) / rb_hi - vreg_c(v, 1, 31600.0) / r59_lo3 for v in vgrid)
    sp3 = spectrum(lambda f_, v_: V101(f_) * math.sqrt(2) / abs(rbank + 1.0 / (1j * 2 * math.pi * f_ * (c_a + c66_ + 0.11e-6) + (1j * 2 * math.pi * f_ * c_b - reg3_hi / v_)
                                                                              / (1 + loop_t(f_, 1e-3 * R["rs"], 31600.0, 100e-9, v_, f_amp=bw169 * 20e3 / 31600.0)))))
    clip3 = {}
    for mult_ in (1.0, 3.0, 10.0, None):
        w3_ = 0.0
        for vo_ in r3["V_OUTS"]:
            for ii_ in (i_reg_hi, i_op):
                l3_ = ladder(row0["cu"], row0["cd"], ii_, v_oc, vo_, F_LO, L1_LO, T_RF, rb_lo, 0.0, r59_hi, L59, bulk_op)
                x_ = l3_["v59"] if mult_ is None else lowpass(l3_["v59"], 1.0 / (2 * math.pi * mult_ * bw169 * 20e3 / 31600.0), 1e-9)
                w3_ = max(w3_, clip_avg(x_) / (sum(l3_["v59"]) / len(l3_["v59"])) - 1.0)
        clip3[mult_] = w3_
    W3l = {L_: evalR(L_, dict(GA, l59=L59)) for L_ in (grid6[0], grid6[-1])}
    pins3 = {L_: budget(w_) for L_, w_ in W3l.items()}
    pins3[L_REF] = (min(rep10["pins0"][0], rep10["pinsr"][0]), max(rep10["pins0"][1], rep10["pinsr"][1]))
    O["C3"] = dict(r59_lo=r59_lo3, hi=reg3_hi, nom=vreg[1] / (1e-3 * 31600.0 * R["rs"]), m=m3, worst=worst(sp3), clip=clip3, pins=pins3,
                   line=abs169[1] * 0.9)
    # C2's own averaging against the INA169's bandwidth (the same multiples)
    clip2 = {}
    for mult_ in (1.0, 3.0, 10.0, None):
        w2_ = 0.0
        for vo_ in r3["V_OUTS"]:
            for ii_ in (reg_sel["hi"], i_op):
                l2_ = ladder(None, cd_all, ii_, v_oc, vo_, F_LO, L1_LO, T_RF, rb_lo, wsl_l[1], None, None, bulk_op)
                x_ = l2_["vbank"] if mult_ is None else lowpass(l2_["vbank"], 1.0 / (2 * math.pi * mult_ * bw169 * 20e3 / R16v), 1e-9)
                w2_ = max(w2_, clip_avg(x_) / (sum(l2_["vbank"]) / len(l2_["vbank"])) - 1.0)
        clip2[mult_] = w2_
    O["C"]["clip"] = clip2

    # --- the fault case on the selected circuit: the record's model with RSENSE1's branch tied (1 uOhm, no inductance)
    GC = dict(GA, r59=L_TIE, l59=0.0)
    loops = (grid6[0], grid6[13], L_REF, grid6[-1])
    WC = {L_: evalR(L_, GC) for L_ in loops}
    WA_l = {grid6[0]: b6["W03"], grid6[13]: b6["W1u"], L_REF: b6["W"]}
    # the bank's corner search at the reference loop (the sixteen combinations of the four banks' bounds)
    cnr = []
    for cq_ in itertools.product(("lo", "hi"), repeat=4):
        Wq_ = evalR(L_REF, dict(GC, **banks_q(*cq_)))
        cnr.append((cq_, Wq_["u18"], Wq_["vF"], Wq_["vS"], Wq_["u5"]))
    k97 = R97v * (1 + tol_y) / (100e3 * (1 - tol_y) + R97v * (1 + tol_y))
    on97 = inp_h * (100e3 * (1 + tol_y) + R97v * (1 - tol_y)) / (R97v * (1 - tol_y))
    off97 = inp_l * (100e3 * (1 - tol_y) + R97v * (1 + tol_y)) / (R97v * (1 + tol_y))
    # IMON_IN under the fault: the charge U23 can put on C65 over the whole event (60 us), its sense at the event's highest, linear
    imon_q = {L_: gm169[1] * (1 + nl169) * WC[L_]["u18"] * 60e-6 / (C65v * 0.90) for L_ in loops}
    O["Cfault"] = dict(W=WC, WA=WA_l, cnr=cnr, k97=k97, on97=on97, off97=off97, kinp_old=b6["kinp"], imon_q=imon_q, loops=loops, ken=b6["ken"],
                       u18_lim=abs169[1] * 0.9, abs169=abs169, hold_lo=r3["lo_h"], cold=cold, d4=G6["d4"][0], L_TIE=L_TIE)

    # --- the normal case on the selected circuit: the ladder verified against the record's sense_ripple, then the bank's sense
    lad0 = ladder(row0["cu"], row0["cd"], i_reg_hi, v_oc, 12.0, F_LO, L1_LO, T_RF, rb_lo, 0.0, r59_hi, L59, bulk_op)
    s0 = row0["op"][(12.0, i_reg_hi)]
    lad_rep = max(abs(max(lad0["v59"]) - s0["peak"]), abs(min(lad0["v59"]) - s0["trough"]), abs(sum(lad0["v59"]) / len(lad0["v59"]) - s0["avg"]),
                  abs(max(r59_hi * i_ for i_ in lad0["i59"]) - s0["r_peak"]))
    if lad_rep > 1e-12:
        refuse(4, "the ladder model does not reproduce the record's sense_ripple (%.3g)" % lad_rep)
    opC = {}
    for vo_ in r3["V_OUTS"]:
        for ii_ in (reg_sel["hi"], i_op):
            for lb_ in (0.0, wsl_l[0] / nb, wsl_l[1] / nb, wsl_l[1]):
                lad_ = ladder(None, cd_all, ii_, v_oc, vo_, F_LO, L1_LO, T_RF, rb_lo, lb_, None, None, bulk_op)
                vb_ = lad_["vbank"]
                avg_ = sum(vb_) / len(vb_)
                filt_ = lowpass(vb_, 1.0 / (2 * math.pi * bw169 * 20e3 / R16v), 1e-9)
                opC[(vo_, ii_, lb_)] = dict(vmax=max(vb_), vmin=min(vb_), imax=max(lad_["ib"]), imin=min(lad_["ib"]), avg=avg_,
                                            err_raw=clip_avg(vb_) / avg_ - 1.0, err_bw=clip_avg(filt_) / avg_ - 1.0)
    hold_C = ladder(None, cd_all, reg_sel["hi"], lo_h, v_out, F_LO, L1_LO, T_RF, rb_lo, wsl_l[1] / nb, None, None, bulk_op)
    edge_C = ladder(None, cd_all, reg_sel["hi"], v_oc, 12.0, F_LO, L1_LO, 10e-9, rb_lo, wsl_l[1] / nb, None, None, bulk_op, dt=0.5e-9)
    O["Cnormal"] = dict(rep=lad_rep, op=opC, hold=(max(hold_C["vbank"]), min(hold_C["vbank"])), edge=(max(edge_C["vbank"]), min(edge_C["vbank"])),
                        lb=(wsl_l[0] / nb, wsl_l[1] / nb, wsl_l[1]))
    # --- the start and the ratings: the bank's start current (the record's, the capacitors behind it at their largest, C79 added)
    i_start_bank = R["remedy"]["i_bank_slew"] * (c_a + c66_ + c_b + 0.11e-6) / (c_a + c66_ + c_b)
    v_im_start = gm169[1] * (1 + nl169) * (i_start_bank * rb_hi + vos169) * R16v * rtf(R16v, 1, True)
    O["Cstart"] = dict(i=i_start_bank, v_im=v_im_start, ovt_lo=ovt[0], p23=iq169 * 31.8, r59_loss=r59_hi * i_reg_hi ** 2)

    # ================================================================== 5. ROUTE B2 (the coordinator's task of 5 October 2026, 17:12)
    # the withdrawn plug: INP from its highest while the guard is on (PV_F at the cut-off's highest, the divider's highest ratio) falls
    # through R97 (aged, at its highest) and C80 (C0G, +5 % and its 30 ppm/K) under V(INP_L)'s least, then U21's INP turn-off delay and
    # Q12's gate fall (the record's); on the next plug INP rises through R96 || R97 with C80 only once the presence pair has made
    c80 = 10e-9 * 1.05 * (1 + 30e-6 * dt_end)
    v_inp0 = G6["ov"] * k97
    tau_off = R97v * rtf(R97v, 1, True) * c80
    t_inp_off = tau_off * math.log(v_inp0 / inp_l)
    t_off = t_inp_off + b6["tinp"] * 1e-6 + G6["t_f"]
    r_par = 1.0 / (1.0 / (100e3 * rtf(100e3, 1, True)) + 1.0 / (R97v * rtf(R97v, 1, True)))
    t_on_hold = r_par * c80 * math.log((lo_h * k97) / (lo_h * k97 - inp_h)) if lo_h * k97 > inp_h else None
    # the arriving source: the record's cold connection (Q12 never conducts; the port's own network) over the record's whole grid of
    # source loops, both fault positions, the port bank at its least and its largest, from a discharged port and from 25 V (a
    # back-fed PV_F after a withdrawal lies between), D11 at both ends; INP read through R97 24.9k and EN through R94 over R95
    arr = []
    for L_ in grid6:
        W_ = [evalR(L_, dict(GA, bF=bf_), starts=cold_st, cases=R_CASES, cold=True) for bf_ in (GA["bF"], bF_hi)]
        arr.append(dict(L=L_, vF=max(w_["vF"] for w_ in W_), slew=max(w_["slew"] for w_ in W_), vFmin=min(w_["vFmin"] for w_ in W_),
                        iL=max(w_["iL"] for w_ in W_), e11=max(w_["e11"] for w_ in W_)))
    ken = b6["ken"]
    lines_b2 = (("PV_F at VS, CS+, CS- and ISCP", lambda a_: a_["vF"], 100.0, 90.0, "V"),
                ("PV_F against the recommended operating VS row", lambda a_: a_["vF"], None, rw_vs_rec(R), "V"),
                ("the slew at CS+, CS- and ISCP", lambda a_: 1e-6 * a_["slew"], 1e-6 * b6["slew_abs"], 0.9e-6 * b6["slew_abs"], "V/us"),
                ("INP (R96 over R97 24.9k)", lambda a_: a_["vF"] * k97, rw_pin_abs(R), 0.9 * rw_pin_abs(R), "V"),
                ("EN/UVLO (R94 over R95)", lambda a_: a_["vF"] * ken, rw_pin_abs(R), 0.9 * rw_pin_abs(R), "V"))

    def holds_from(f_, lim_):
        j_ = len(arr)
        while j_ > 0 and f_(arr[j_ - 1]) <= lim_:
            j_ -= 1
        return None if j_ == len(arr) else (arr[j_]["L"] if j_ > 0 else 0.0)
    b2rows = []
    for lab_, f_, abs_, line_, unit_ in lines_b2:
        worst_ = max(f_(a_) for a_ in arr)
        b2rows.append(dict(lab=lab_, worst=worst_, abs=abs_, line=line_, unit=unit_, abs_ok=(abs_ is None or worst_ <= abs_),
                           line_ok=worst_ <= line_, from_=holds_from(f_, line_)))
    O["B2"] = dict(c80=c80, v_inp0=v_inp0, tau_off=tau_off, t_inp_off=t_inp_off, t_off=t_off, t_on_hold=t_on_hold, rows=b2rows,
                   floor=min(a_["vFmin"] for a_ in arr), grid=(grid6[0], grid6[-1], len(grid6)), n=len(arr) * 2 * len(cold_st) * len(R_CASES) * 2,
                   t_ov=G6["t_ov"], tinp=b6["tinp"], ov_hi=G6["ov"], inp_l=inp_l, inp_h=inp_h, i_l=max(a_["iL"] for a_ in arr),
                   e11=max(a_["e11"] for a_ in arr), cold_rep=(max(a_["vF"] for a_ in arr), max(a_["slew"] for a_ in arr)),
                   i_start=b6["i_start"])
    if abs(O["B2"]["cold_rep"][0] - b6["cold"]["vF"]) > 1e-9 or abs(O["B2"]["cold_rep"][1] - b6["cold"]["slew"]) > 1e-3:
        refuse(4, "the arriving-source case does not reproduce the record's cold connection over its grid")
    return O, R, b6, r3


def rw_vs_rec(R):
    """The TPS4811-Q1's recommended operating maximum for VS, CS+ and CS- (SLUSEE5E 6.2), as the record read it."""
    return R["remedy"]["b6"]["vs_rec"]


def rw_pin_abs(R):
    """The TPS4811-Q1's absolute maximum for its input pins (OV, EN/UVLO, INP; SLUSEE5E 6.1), as the record read it."""
    return R["remedy"]["T48"]["pin_abs"]


# ------------------------------------------------------------------------------------------------------------------------ composition
MUTS_C2 = (("U5's CSNIN on a net of its own", '"32": "TRK_VS", "33": "TRK_VS", "34": "TRK_VS"', '"32": "TRK_VIN", "33": "TRK_VS", "34": "TRK_VS"'),
           ("U23's VIN- off the bank's pad", '"3": "PV_P", "4": "TRK_VS", "5": "TRK_VS"}, "C44322")\nc("C79"',
            '"3": "PV_P", "4": "TRK_SHDN", "5": "TRK_VS"}, "C44322")\nc("C79"'),
           ("R59 back between TRK_VS and U5's CSNIN", 'ic("U23", 5,',
            'r("R59", "15mOhm 1% 2512 (RSENSE1)", "TRK_VS", "TRK_CSNX", "RS2512", "C2903494"); ic("U23", 5,'),
           ("U23's output off IMON_IN", '{"1": "TRK_IMONI", "2": "GND", "3": "PV_P"', '{"1": "TRK_ISO", "2": "GND", "3": "PV_P"'))
# route B2 (the coordinator's task of 5 October 2026, 17:12): the presence loop composed after the C2 draft; its own mutations
DRAFT_B2 = REC + "/apply_gen_sch_e_p0sol_b2.py"
ORDER_E_B2 = tuple(x for y in ORDER_E for x in ((y, ("l4e7", "p0sol_b2")) if y == ("l4e7", "p0sol") else (y,)))
MUTS_B2 = (("R96 straight onto INP (the loop bypassed)", '"PV_F", "PV_PRA", "R"); ', '"PV_F", "PV_INP", "R"); '),
           ("the loop bridged on the board (J_SOLP pin 1 on INP)", '{"1": "PV_PRA", "2": "PV_INP"}, "C158012")', '{"1": "PV_INP", "2": "PV_INP"}, "C158012")'),
           ("R97 off INP (no pull-down when the loop opens)", '"PV_INP", "GND", "R", "C136967")', '"PV_INPX", "GND", "R", "C136967")'),
           ("C80 off INP (the filter gone)", '"PV_INP", "GND", "C10u50", lcsc="C184799")', '"PV_UVLO", "GND", "C10u50", lcsc="C184799")'))


def compose_and_check(order=ORDER_E, judge_fn=None, muts=MUTS_C2, draft=DRAFT, tag="p0sol"):
    """Board E's generator composed in L4-E9's change-list order with this record's draft(s), on a scratch copy; the netlist written
    by record l8p's gen_netlist.py (no KiCad); the changed nets read and judged; each mutation applied to the composed text and
    regenerated must fail the judge."""
    judge_fn = judge_fn or judge
    nr = load("netread_for_p0sol", NETREAD)
    res = dict(steps=[], checks=None, mutations=[])
    with tempfile.TemporaryDirectory() as td:
        gp = os.path.join(td, "gen_sch_e.py")
        shutil.copy(os.path.join(TOP, GEN_E), gp)
        for rec_, nm_ in order:
            s_ = os.path.join(TOP, "v2/docs/records", rec_, "apply_gen_sch_e_%s.py" % nm_)
            args_ = [s_, gp, os.path.join(TOP, NET_E)] if rec_ == "d8dec31" else [s_, gp, "--write"]
            r_ = subprocess.run([sys.executable, "-B"] + args_, capture_output=True, text=True)
            res["steps"].append(("%s/%s" % (rec_, nm_), r_.returncode))
            if r_.returncode != 0:
                res["refused"] = (rec_, nm_, (r_.stderr.strip().splitlines() or [""])[-1].replace(td, "<scratch>"))
                return res
        composed = open(gp, encoding="utf-8").read()
        res["second"] = subprocess.run([sys.executable, "-B", os.path.join(TOP, draft), gp, "--check"], capture_output=True, text=True).returncode

        def netlist(text_, tag_):
            p_ = os.path.join(td, tag_ + "_gen.py")
            open(p_, "w", encoding="utf-8").write(text_)
            o_ = os.path.join(td, tag_ + ".net")
            r_ = subprocess.run([sys.executable, "-B", os.path.join(TOP, GEN_NETLIST), p_, o_], capture_output=True, text=True)
            if r_.returncode != 0:
                return None, (r_.stderr.strip().splitlines() or [""])[-1].replace(td, "<scratch>")
            return nr.read_netlist(open(o_, "rb").read()), (r_.stdout.strip().splitlines() or [""])[-1].replace(td, "<scratch>")
        nl, msg = netlist(composed, tag)
        res["gen"] = msg
        if nl is None:
            return res
        res["checks"] = judge_fn(nl)
        for lab_, old_, new_ in muts:
            if composed.count(old_) != 1:
                res["mutations"].append((lab_, "NOT APPLICABLE (the text occurs %d times)" % composed.count(old_)))
                continue
            mt_ = composed.replace(old_, new_)
            if lab_.startswith("R59"):
                mt_ = mt_.replace('"32": "TRK_VS", "33": "TRK_VS", "34": "TRK_VS"', '"32": "TRK_CSNX", "33": "TRK_VS", "34": "TRK_VS"')
            nlm_, m_ = netlist(mt_, "m%d" % len(res["mutations"]))
            if nlm_ is None:
                res["mutations"].append((lab_, "the generator refused: %s" % m_))
                continue
            fails_ = [c_ for c_, ok_ in judge_fn(nlm_) if not ok_]
            res["mutations"].append((lab_, ("FAILS: " + "; ".join(fails_)) if fails_ else "PASSES (the check is blind to it)"))
    return res


def compose_and_check_b2():
    return compose_and_check(order=ORDER_E_B2, judge_fn=judge_b2, muts=MUTS_B2, draft=DRAFT_B2, tag="p0sol_b2")


def judge_b2(nl):
    """Route B2's predicates on top of C2's: INP fed only through the presence loop, held low by R97 when it opens, filtered by C80;
    U21's OV and UVLO dividers as drafted."""
    pin = lambda r_, p_: nl["pins"].get(r_, {}).get(p_)
    out = list(judge(nl))
    inp = pin("U21", "3")
    pra = [n_ for n_ in nl["pins"].get("R96", {}).values() if n_ != "PV_F"]
    out.append(("R96 from PV_F to the presence loop's outgoing net, not to INP (%s)" % inp,
                sorted(nl["pins"].get("R96", {}).values()) == sorted(["PV_F"] + pra) and len(pra) == 1 and pra[0] != inp))
    out.append(("J_SOLP pin 1 on R96's loop net and pin 2 on U21's INP (pin 3), the loop's only path to INP",
                bool(pra) and pin("J_SOLP", "1") == pra[0] and pin("J_SOLP", "2") == inp and sorted(nl["on"].get(pra[0], ())) == ["J_SOLP", "R96"]))
    out.append(("INP's net holds U21, R97, C80 and J_SOLP only, R97 and C80 to GND",
                inp is not None and sorted(nl["on"].get(inp, ())) == ["C80", "J_SOLP", "R97", "U21"]
                and sorted(nl["pins"].get("R97", {}).values()) == sorted([inp, "GND"]) and sorted(nl["pins"].get("C80", {}).values()) == sorted([inp, "GND"])))
    out.append(("U21's OV (pin 2) on R98 to R100's divider and UVLO (pin 1) on R94 over R95, as drafted",
                pin("U21", "2") == "PV_OVLO" and pin("U21", "1") == "PV_UVLO" and pin("R100", "1") in ("PV_OVLO",) and "PV_UVLO" in nl["pins"].get("R95", {}).values()))
    return out


def judge(nl):
    """The selected circuit's predicates on a netlist, each a (statement, holds) pair."""
    pin = lambda r_, p_: nl["pins"].get(r_, {}).get(p_)
    out = []
    vin = pin("U5", "34")
    out.append(("U5's CSNIN (pin 32), CSPIN (pin 33) and VIN (pin 34) on one net, %s" % vin, vin is not None and pin("U5", "32") == vin == pin("U5", "33")))
    out.append(("no RSENSE1 (R59) and no net TRK_VIN", "R59" not in nl["comps"] and "TRK_VIN" not in nl["on"]))
    out.append(("U5's input net is the bank's far side: R60 to R64 between PV_P and it, U18's VIN- on it",
                all(sorted(nl["pins"].get("R6%d" % k_, {}).values()) == sorted(["PV_P", vin]) for k_ in range(5)) and pin("U18", "4") == vin and pin("U18", "3") == "PV_P"))
    out.append(("U23 on the bank's pads as U18 is (VIN+ PV_P, VIN- and V+ on U5's input), GND", pin("U23", "3") == "PV_P" and pin("U23", "4") == vin
                and pin("U23", "5") == vin and pin("U23", "2") == "GND" and "INA169" in nl["comps"].get("U23", {}).get("value", "")))
    imon = pin("U5", "38")
    out.append(("U23's output on U5's IMON_IN (pin 38), %s, with R16 and C65 to GND and nothing else" % imon,
                imon is not None and pin("U23", "1") == imon and sorted(nl["on"].get(imon, ())) == ["C65", "R16", "U23", "U5"]
                and sorted(nl["pins"]["R16"].values()) == sorted([imon, "GND"]) and sorted(nl["pins"]["C65"].values()) == sorted([imon, "GND"])))
    out.append(("R16 34.0k, R97 24.9k (INP's bottom, PV_INP to GND)", nl["comps"].get("R16", {}).get("value", "").startswith("34.0k")
                and nl["comps"].get("R97", {}).get("value", "").startswith("24.9k") and sorted(nl["pins"].get("R97", {}).values()) == ["GND", "PV_INP"]))
    out.append(("C79 from U5's input net to GND (U23's V+ bypass)", sorted(nl["pins"].get("C79", {}).values()) == sorted([vin, "GND"])))
    out.append(("M1's drain (Q3 pins 5 to 8), C13 to C15, C64, C71 to C74 and D4 on U5's input net",
                all(pin("Q3", p_) == vin for p_ in "5678") and all(vin in nl["pins"].get(c_, {}).values()
                                                                    for c_ in ("C13", "C14", "C15", "C64", "C71", "C72", "C73", "C74", "D4"))))
    out.append(("U18 and the trip unchanged (U18 pin 1 on TRK_ISO into R65 and R66)", pin("U18", "1") == "TRK_ISO"
                and sorted(nl["on"].get("TRK_ISO", ())) == ["R65", "U18"]))
    return out


# ------------------------------------------------------------------------------------------------------------------------ render
def render(O, K, R, b6, r3, K2):
    lines = []
    P = lines.append

    def wrap(first, rest, text, width=130):
        words, cur, pre = text.split(), "", first
        for w_ in words:
            if cur and len(pre) + len(cur) + 1 + len(w_) > width:
                P(pre + cur)
                cur, pre = w_, rest
            else:
                cur = (cur + " " + w_) if cur else w_
        if cur:
            P(pre + cur)
    rw = O["rows"]
    P("L4-E7 / P0-7: THE SOLAR STAGE'S D-10 AND D-16 BY CIRCUIT ALTERNATIVES (MESHSAT-1357, 5 October 2026)")
    wrap("", "", "Prototype design, desk arithmetic: nothing is bought, built, powered or measured; no generator, registry or page of "
         "the tree is edited (apply_gen_sch_e_p0sol.py is a draft, composed here on scratch copies only). Bases: PRINTED LIMIT, "
         "TYPICAL, MEASURED (none exists), ASSUMPTION, MODELED, INFERRED, SESSION, NETLIST, CATALOGUE. The lead-inductance method is "
         "ended: no loop is searched and none is claimed to pass; the record's transient model runs only at its reference loop and "
         "the envelope's ends, on the changed circuit, against the same failure case.")
    P("")
    P("INPUTS (sha256, the first 16 hex digits)")
    for h_, rel in O["pins"]:
        P("  %s %s" % (h_[:16], rel))
    P("")
    # ---------------------------------------------------------------- 0
    P("0. REPRODUCTION ON THE BASE (fnd/p0base e132db0e), before any change")
    d_ = O["key_diff"][0]
    wrap("  0a ", "     ", "The record's results cache (l4e7_stage_settings.results.json): its KEY %s on this tree. The only part that differs "
         "is the file %s (%s at %s, set 29's freeze, against %s here: L4-E11's rounds 12 to 16). The figures compute() reads from it, "
         "with its own patterns, in both versions: %s. EQUAL in both, so the cached results are this base's results; the cache is "
         "not re-keyed here (the record's own recompute, 30 to 50 core-minutes, is the integrator's on a rented box, and the "
         "record's tests read the cache through results(), which recomputes whenever the KEY does not hold)." % ("does NOT hold" if not O["key_holds"] else "holds", d_[1], d_[2][:16], CACHE_AT, (d_[3] or "missing")[:16],
                                "; ".join("%s %s" % (w_, "/".join(a_)) for w_, a_, _b in O["o11"])))
    wrap("  0b ", "     ", "render(cache) against the committed l4e7_stage_settings.out: BYTE-IDENTICAL (sha256 %s)." % O["out_sha"][:16])
    d16 = O["d16"]
    wrap("  0c ", "     ", "D-16 recomputed by the record's own sense_ripple on its cached parameters (the as-drafted split; 25 V in, the "
         "oscillator's least 170 kHz, L1 at -20 %%, M1's edges 20 ns, RSENSE1 at its highest with 5 nH, the bulk new at 20 C): every "
         "figure equal to the cached one (largest difference %.1g):" % max(r_[3] for r_ in d16["rows"]))
    for vo_, ii_, s_, _d in d16["rows"]:
        P("       bus %.2f V, %.4f A: resistive peak %.4f V, the pins %+.4f to %+.4f V, the clipped monitor's average %+.1f %%" % (
            vo_, ii_, s_["r_peak"], s_["trough"], s_["peak"], 100 * (s_["avg_clip"] / s_["avg"] - 1)))
    P("       M1's edges at 10 ns: the pins reach %+.4f V (equal to the cached %+.4f V); the sheet's Figure 1 arrangement: resistive %.4f V,"
      % (d16["edge"]["trough"], d16["edge"]["trough"], d16["fig1"][0]))
    P("       the pins %+.4f to %+.4f V. Against: the operating range +-%.0f mV (8705af p.5, PRINTED LIMIT), the absolute maximum +-%.1f V (p.2)."
      % (d16["fig1"][1], d16["fig1"][2], 1e3 * rw["v_op"], rw["abs_cs"]))
    P("       REPRODUCED: D-16 stands on the base (%.4f V resistive at the regulation's highest, over the %.0f mV range)." % (d16["r_peak"][0], 1e3 * rw["v_op"]))
    d10 = O["d10"]
    rep = d10["rep"]
    wrap("  0d ", "     ", "D-10 recomputed by the record's own guard_event_b, every ceramic bank rebuilt from Samsung's held curves at the "
         "record's cached bounds (each bank's effective capacitance equal to the record's), the selected corner, every start the guard "
         "is on in, the three bulk corners, D11 at both ends and both fault positions (%d events) at the reference loop %.2f uH: "
         "U5's resistive peak %.6f V (+ the numerical error %.6f: %.4f V); the pins' complete budget (RSENSE1 5 nH, the Kelvin pair 1 nH) "
         "%+.4f to %+.4f V at a fault at the connector and %+.4f to %+.4f V at the lead's far end; PV_F %.2f V, Q12 off at %.2f A, the "
         "bank's differential %.4f V. Every figure equal to the cached one (largest difference %.1g)." % (
             d10["n"], 1e6 * d10["L_REF"], rep["u5"], d10["ERR"], rep["u5_err"], rep["pins0"][0], rep["pins0"][1], rep["pinsr"][0],
             rep["pinsr"][1], rep["vF"], rep["iQ"], rep["u18"], d10["diff"]))
    wrap("     ", "     ", "The cold connection at the envelope's least loop (%.2f uH), a fault at the connector, the port bank at its least "
         "and its largest: PV_F %.2f V, its slew %.2f V/us, INP %.2f V (R97 28.0k); equal to the cached maxima over the whole grid "
         "(difference %.1g). Against: the slew's %.0f V/us absolute and 54 V/us margin line, INP's %.0f V absolute and 18 V line." % (
             1e6 * d10["grid"][0], d10["cold"]["vF"], 1e-6 * d10["cold"]["slew"], d10["cold"]["vF"] * rep["kinp"], d10["cold_diff"],
             1e-6 * d10["slew_abs"], d10["pin_abs"]))
    wrap("     ", "     ", "REPRODUCED: D-10 stands on the base: %+.4f V on U5's pins at a connector fault, past their -%.1f V absolute "
         "maximum; INP %.2f V (guard on) and %.2f V (cold) over the 18 V line; the cold slew %.1f V/us over 54 V/us." % (
             rep["pins0"][0], rw["abs_cs"], rep["vF"] * rep["kinp"], d10["cold"]["vF"] * rep["kinp"], 1e-6 * d10["cold"]["slew"]))
    P("")
    # ---------------------------------------------------------------- 1
    m2 = O["m2"]
    A_, B_, C_ = O["A"], O["B"], O["C"]
    P("1. THE COMPARISON: THREE MATERIALLY DIFFERENT CIRCUIT ALTERNATIVES, EACH ON THE FAULT CASE (D-10) AND THE NORMAL CASE (D-16)")
    wrap("  ", "  ", "What both defects share: RSENSE1 puts U5's own input amplifier, whose pins are rated -0.3 to +0.3 V absolute and "
         "-100 to +100 mV operating (8705af p.2, p.5: PRINTED LIMIT), in the path of a current the stage does not bound on printed "
         "figures: the charge a stiff source pushes into whatever sits behind RSENSE1 (D-10, set by a loop no document bounds) and "
         "M1's pulsed draw (D-16). Splitting the ceramics around RSENSE1 cannot satisfy both (round 3, result (ii)). The alternatives "
         "below change what carries the sense, where, or whether the event can happen. M2 (CS101) is judged on the record's own "
         "accepted model (MODELED, typical loop rows), reproduced first: the accepted spectrum over its %d frequencies to %.1g." % (m2["n"], m2["rep"]))
    P("")
    wrap("  (A) ", "      ", "THE SENSE MOVED AHEAD OF EVERY BANK (route 3's wider form, R-187; the sheet's Figure 1 taken past the bulk): "
         "RSENSE1 between Q12 and PV_P, so it carries the port's own current. Normal case: the source behind the lead is a current "
         "source at the switching frequency, so RSENSE1 reads the flat input current, %.4f V at the regulation's highest (inside "
         "+-100 mV; D-16 MEETS). Fault case, the record's model at the reference loop with RSENSE1 in Q12's branch: Q12's current "
         "reaches %.2f A and U5's resistive differential %.4f V, %.1f times the %.1f V absolute maximum (D-10 WORSE). M2: the "
         "regulation would hold the port current, the bulk's and the bank's together, so within the loop's bandwidth the bank carries "
         "the bulk's CS101 current inverted: the filtered peak %.4f A at %.0f Hz against the accepted margin %.4f A, over it at %d of the "
         "%d frequencies from %.0f Hz (the accepted design: %.4f A at %.0f Hz). REJECTED: fails D-10 by the same mechanism made larger, "
         "and undoes the accepted CS101 correction." % (A_["op"], A_["iQ"], A_["u5"], A_["u5"] / A_["abs_cs"], A_["abs_cs"], m2["A"][2],
                                                        m2["A"][0], m2["margin_old"], len(m2["lowA"]), m2["n"], m2["lowA"][0][0] if m2["lowA"] else 0.0,
                                                        m2["old"][2], m2["old"][0]))
    P("")
    wrap("  (B) ", "      ", "THE GUARD-ON EVENT BOUNDED OR REMOVED AT THE PORT (the source's step limited before it reaches the stage's "
         "capacitance, or made impossible): (B1) a series choke at the port, the board's own L1 part, Coilcraft XAL1510-103 (10 uH "
         "+-20 %%, Isat %.1f A, PRINTED): with the choke at its least (%.1f uH) and the envelope's least source loop, the short-circuit "
         "trip's highest (%.2f A) plus the %.2f V step over the trip's %.1f us propagation reaches %.1f A at the cut, over the choke's "
         "Isat, where its inductance is no longer the printed one; its resonance with the entry's capacitance (%.1f uF at its largest) "
         "and the lead falls at %.2f to %.2f kHz, inside CS101's 2 to 5 kHz band where the accepted M2 immunity is decided; and it "
         "leaves D-16 as it is. (B2) a presence contact pair in the solar receptacle carrying U21's INP: the plug's withdrawal pulls "
         "INP low (V(INP_L) %.1f V least, PRINTED; turn-off within tPD(INP_L)) before any other source can mate, so a source can only "
         "ever arrive cold, the case whose absolute ratings the record shows held; it would prevent the guard-on step only for a source "
         "arriving through the loop's mating points (a partial measure), not for a second source on the same lead, and it does not "
         "change the port's response when a step happens; it needs the receptacle's contact set and a rule that every plug for it "
         "bridges the pair (Layer 7's harness, R-180 rewritten), and it leaves D-16 as it is. NOT SELECTED as the correction: B1 is not "
         "supported on printed figures; B2 is an unapproved PARTIAL interface proposal (section 5), and neither resolves D-10 "
         "(section 3)." % (B_["isat"], 1e6 * B_["l_ch"], B_["isc"], B_["dv"], 1e6 * B_["t_sc"], B_["i_cut"], 1e6 * B_["c_entry"],
                                            1e-3 * B_["f_res"][1], 1e-3 * B_["f_res"][0], B_["inp_l"]))
    P("")
    sel = C_["sel"]
    wrap("  (C) ", "      ", "U5'S OWN INPUT SENSE RETIRED, THE REGULATION'S SENSE AN AMPLIFIER WHOSE PINS TOLERATE THE STEP: CSPIN and "
         "CSNIN tied to VIN, as the sheet asks when the input sense is not in use (8705af p.12, p.29, p.31), so their differential is "
         "zero in every state by construction, and RSENSE1 removed; the input-current regulation fed into IMON_IN by a current-output "
         "amplifier, EA2 unchanged (p.31: \"IMON_IN voltages exceeding 1.208V (typical) cause the VC voltage to reduce\"). Its sense "
         "point decides M2: (C1) at the port's R87 through U21's own IMON (the TPS48110-Q1's monitor, gain error +-%.2f %%, offset "
         "+-%.0f uV, PRINTED) holds the port current like (A): filtered CS101 peak %.4f A at %.0f Hz, over any margin the accepted "
         "coordination gives: REJECTED; (C2) a second INA169 (U23, U18's part) on the backstop's own bank R60 to R64, where the loop "
         "holds the bank's current and the trip reads the same bank: SELECTED (below). The INA169's differential is rated +%.0f V / "
         "-%.0f V (SBOS181F p.4, PRINTED), seven times U5's, and its rows are printed over VSENSE 10 to 150 mV (gm %.0f to %.0f uA/V, "
         "offset +-%.0f mV, nonlinearity +-%.1f %%), where A7's are printed only at 50 mV." % (100 * rw["imon_ge"], 1e6 * rw["imon_os"],
                                                                                               m2["C1"][2], m2["C1"][0], rw["abs169"][1], 40.0,
                                                                                               1e6 * rw["gm169"][0], 1e6 * rw["gm169"][1],
                                                                                               1e3 * rw["vos169"], 100 * rw["nl169"]))
    c3 = O["C3"]
    wrap("      ", "      ", "(C3) the same INA169 reading the drafted RSENSE1 instead of A7 (R59 and the accepted split kept, R16 31.6k): "
         "the regulation stays independent of the trip and the accepted M2 topology is kept (filtered peak %.4f A at %.0f Hz against its "
         "own independent margin %.4f A); in the fault case U23's differential is the record's U5 budget, %+.3f to %+.3f V at the "
         "envelope's least loop, %+.3f to %+.3f V at the reference loop, inside the INA169's +2 V / -40 V at every loop (its 1.8 V line "
         "held); in normal operation RSENSE1's own current never reverses, but its 5 nH puts negative spikes across the pins, and the "
         "average U23 regulates on reads high by %+.2f %% at the INA169's typical bandwidth, %+.2f %% at three times it, %+.2f %% at ten "
         "times it and %+.2f %% if it followed every edge: the regulation's accuracy then rests on a bandwidth printed only as typical. "
         "C2's own average, the same way (the bank at 5 nH, no sharing credited): %+.2f / %+.2f / %+.2f / %+.2f %% (the bank's current is "
         "smooth at the 25 V corner)." % (
             c3["worst"][2], c3["worst"][0], c3["m"], c3["pins"][O["d10"]["grid"][0]][0], c3["pins"][O["d10"]["grid"][0]][1],
             c3["pins"][O["d10"]["L_REF"]][0], c3["pins"][O["d10"]["L_REF"]][1], 100 * c3["clip"][1.0], 100 * c3["clip"][3.0],
             100 * c3["clip"][10.0], 100 * c3["clip"][None], 100 * C_["clip"][1.0], 100 * C_["clip"][3.0], 100 * C_["clip"][10.0],
             100 * C_["clip"][None]))
    P("")
    wrap("  THE SELECTION (SESSION, the owner's rule: the simplest supported correction with useful margin and the fewest new uncertain "
         "dependencies): ", "  ", "(C2). It removes U5's absolute-rating violation of D-10 and D-16's operating-range exceedance by "
         "construction, at every source loop, with no new loop dependency; it adds one part the design already carries (an INA169) and "
         "one 100 nF, removes one (RSENSE1, whose inductance no maker prints) and changes two values; its one new unprinted term (A7's "
         "own output at zero differential) lowers the regulation if A7 sources, and a sink, which p.31's text excludes (INFERRED), "
         "would have to reach %.2f uA to bring the margin to the accepted design's (section 2h). Over (C3): C2's averaging does "
         "not depend on the amplifier's unprinted bandwidth and its CS101 margin is %.1f times C3's; C3 keeps the regulation "
         "independent of the trip and holds U23's rating at the envelope's least loop, where the port itself fails (section 3). The "
         "price of C2, stated: the regulation and the 100 W trip share the bank, so a short across the bank, which already defeats the "
         "trip (the record's single-fault list), now also defeats the regulation (never credited for the 100 W bound); Layer 8's fault "
         "table carries it. Reversal: to (C3), the same draft with U23 on R59's pads and R59 kept, if Layer 8's fault analysis rules the "
         "shared shunt out; the drafted RSENSE1 with A7 returns only with a measured or maker-stated bound that keeps U5's pins inside "
         "+-0.3 V for the declared envelope." % (C_["sink_be_acc"], C_["sel"]["m"] / O["C3"]["m"]))
    P("")
    # ---------------------------------------------------------------- 2
    P("2. THE SELECTED CIRCUIT (C2) ON BOTH CASES")
    K_ = K
    wrap("  2a ", "     ", "COMPOSITION, NETLIST AND MUTATIONS. Board E's generator composed in L4-E9's change-list order with the draft "
         "after the solar guard (R-173) and before L4-E11's aux (R-177): %s. The draft refuses a second application (exit %d). The "
         "generator ran to its end on the composed text (record l8p's gen_netlist.py: %s). The changed nets, read in that netlist "
         "(NETLIST):" % (", ".join("%s %s" % (s_, "OK" if rc_ == 0 else "REFUSED") for s_, rc_ in K_["steps"]), K_.get("second", -1),
                         K_.get("gen", "?")))
    for st_, ok_ in K_["checks"] or []:
        P("       %s: %s" % ("holds" if ok_ else "FAILS", st_))
    P("     Mutations, each applied to the composed text and regenerated (each must fail the check):")
    for lab_, res_ in K_["mutations"]:
        P("       %s: %s" % (lab_, res_))
    cf = O["Cfault"]
    wrap("  2b ", "     ", "THE FAULT CASE, D-10, ON THE SELECTED CIRCUIT. U5's CSPIN to CSNIN: 0 V in every state (NETLIST: both pins and VIN "
         "on one net with no element between them; the record's model ties RSENSE1's former branch at %.0g Ohm and reads it at most "
         "%.1g V, the tie's own drop). The record's model with that tie, every start, bulk corner, D11 end and both fault positions, at "
         "the envelope's least loop, about 1 uH, the reference loop and the envelope's largest (MODELED; information about the port, no "
         "loop claimed):" % (cf["L_TIE"], max(cf["W"][L_]["u5"] for L_ in cf["loops"])))
    P("       loop uH   bank (U18, U23) V   PV_F V    INP V (R97 24.9k)   Q12 VDS V   TRK_VS V   D4 A     the as-drafted bank / PV_F")
    for L_ in cf["loops"]:
        w_ = cf["W"][L_]
        wa_ = cf["WA"].get(L_)
        P("       %6.2f    %8.4f            %7.2f   %7.2f             %7.2f     %6.2f     %6.2f   %s" % (
            1e6 * L_, w_["u18"], w_["vF"], w_["vF"] * cf["k97"], w_["vds"], w_["vS"], w_["i4"],
            ("%.4f / %.2f" % (wa_["u18"], wa_["vF"])) if wa_ else "-"))
    cw_ = max(cf["cnr"], key=lambda c_: c_[1])
    wrap("     ", "     ", "Against: the bank's differential %.1f V (U18's and U23's +%.0f V absolute maximum less 10 %%, PRINTED); PV_F 90 V "
         "(the exclusion line) and the TPS4811-Q1's recommended 80 V VS row; INP 18 V (20 V less 10 %%); TRK_VS under D4's least "
         "breakdown at the cold end, %.2f V. The bank's corner search at the reference loop, the sixteen combinations of the four banks' "
         "bounds: its highest differential %.4f V at the corner %s (PV_F %.2f V, TRK_VS %.2f V). At the reference loop every rating but "
         "one holds its line on the selected circuit: U5 by construction, the bank, INP (with R97 24.9k), VDS, TRK_VS, D4; PV_F %.2f V "
         "stays over the recommended 80 V row (L6P-F10, OPEN, unchanged by this round). At the envelope's least loop the port's own "
         "ratings fail as they did (PV_F %.1f V; the bank %.2f V, over U18's and U23's +2 V): that is the guard-on event's port-level "
         "residual, section 3." % (cf["u18_lim"], cf["abs169"][1], cf["d4"], cw_[1], "/".join(cw_[0]), cw_[2], cw_[3],
                                   cf["W"][cf["loops"][2]]["vF"], cf["W"][cf["loops"][0]]["vF"], cf["W"][cf["loops"][0]]["u18"]))
    w3r_ = cf["W"][cf["loops"][2]]
    wrap("     ", "     ", "The other ratings at the reference loop on the selected circuit: PV_F's slew %.1f V/us (54), EN/UVLO %.2f V (18), "
         "PV_P %.2f V (45: the bulk's 50 V, U18's and U23's common mode), PV_F's least %.2f V (-1): all inside their lines." % (
             1e-6 * w3r_["slew"], w3r_["vF"] * cf["ken"], w3r_["vP"], w3r_["vFmin"]))
    wrap("     ", "     ", "INP with R97 24.9k (0.1 %%, 25 ppm/K): its divider's highest ratio %.5f (was %.5f), so INP stays at or under 18 V "
         "for every PV_F up to %.1f V, past PV_F's own 90 V exclusion line: INP no longer fails anywhere PV_F holds. The cold connection's "
         "INP at its worst (PV_F %.2f V): %.2f V (was %.2f V). U21 turns on by %.2f V at the most (V(INP_H) %.1f V, PRINTED; was 9.16 "
         "V), over the stage's own enable (about 9.5 V) and under the hold's least %.2f V: no operating point is lost; it turns off by "
         "INP only under %.2f V, below the UVLO's 7.46 V, so the UVLO still sets the turn-off." % (
             cf["k97"], cf["kinp_old"], 18.0 / cf["k97"], cf["cold"]["vF"], cf["cold"]["vF"] * cf["k97"], cf["cold"]["vF"] * cf["kinp_old"],
             cf["on97"], rw["inp_h"], cf["hold_lo"], cf["off97"]))
    wrap("  2c ", "     ", "IMON_IN UNDER THE FAULT. U23's output can add at most its highest transconductance times the bank's highest "
         "differential for the whole 60 us event, on C65 at its least (90 nF): %s; from the IMON_IN fault's highest (%.2f V) that stays "
         "under the pin's %.0f V absolute maximum (8705af p.2, PRINTED) at every loop listed, at most %.2f V (a bound, INFERRED: "
         "linear, no saturation credited)." % (", ".join("%.2f uH %.3f V" % (1e6 * L_, q_) for L_, q_ in sorted(cf["imon_q"].items())),
                                               rw["ovt"][2], rw["abs_imon"], rw["ovt"][2] + max(cf["imon_q"].values())))
    cn = O["Cnormal"]
    wrap("  2d ", "     ", "THE NORMAL CASE, D-16, ON THE SELECTED CIRCUIT. The periodic model written out (ladder) reproduces the "
         "record's sense_ripple on the as-drafted split to %.1g V, then takes the selected network: the bulk new at 20 C ahead of "
         "the bank, every ceramic behind it at its least (C71 to C74, C13 to C15, C64; the most pulse through the bank), U5's input on "
         "that node, the bank 14 mOhm at its least with its own inductance (Vishay's WSL prints 0.5 to 5 nH a part, TYPICAL span: "
         "five in parallel %.1f and %.1f nH, and 5 nH for no sharing credited). U5's pins: 0 V. The bank's sense (what U23 reads), "
         "25 V in (MODELED):" % (cn["rep"], 1e9 * cn["lb"][0], 1e9 * cn["lb"][1]))
    P("       bus V   input A   bank L nH   sense min / max mV   bank current min / max A   U23's clipped average, raw / at its bandwidth")
    for (vo_, ii_, lb_), d_ in sorted(cn["op"].items()):
        P("       %5.2f   %.4f    %4.1f        %+7.2f / %+7.2f      %+6.3f / %+6.3f             %+.2f %% / %+.2f %%" % (
            vo_, ii_, 1e9 * lb_, 1e3 * d_["vmin"], 1e3 * d_["vmax"], d_["imin"], d_["imax"], 100 * d_["err_raw"], 100 * d_["err_bw"]))
    worst_vmax = max(d_["vmax"] for d_ in cn["op"].values())
    worst_err = max(d_["err_raw"] for d_ in cn["op"].values())
    wrap("     ", "     ", "Against: U5's +-100 mV operating range, met by construction (0 V); U23's printed linear range 10 to 150 mV for "
         "the average it regulates (%.1f to %.1f mV at the regulation's band) with instantaneous peaks to %.1f mV inside its %.0f mV "
         "full-scale sense voltage (SBOS181F p.6) and far inside its +2 V / -40 V absolute maxima; the negative excursions it cannot "
         "follow make its average read HIGH by at most %+.2f %% (raw clipping, the bound; the INA169 outputs no current for a negative "
         "sense), so the regulation errs to a LOWER input current, never toward the trip. At the hold (16.97 V in, the drawn setpoint "
         "out) the sense spans %+.2f to %+.2f mV. M1's 10 ns edges: %+.1f to %+.1f mV at the bank's Kelvin pads, inside the INA169's "
         "absolute maxima; U5 sees none of it. D-16: CORRECTED on the drafted circuit (U5's operating range met by construction; the "
         "regulation's error in the safe direction and bounded above)." % (
             1e3 * sel["lo"] * O["trip"]["rb"][0], 1e3 * sel["hi"] * O["trip"]["rb"][2], 1e3 * worst_vmax, 1e3 * rw["fs169"], 100 * worst_err,
             1e3 * cn["hold"][1], 1e3 * cn["hold"][0], 1e3 * cn["edge"][1], 1e3 * cn["edge"][0]))
    tr = O["trip"]
    acc = C_["acc"]
    wrap("  2e ", "     ", "THE REGULATION ON PRINTED ROWS (U23 into R16 %.1fk, 0.1 %%, 25 ppm/K, aged; EA2's regulation voltage %.3f / %.3f "
         "/ %.3f V and its line term at twice its printed maximum, EA2 at half its typical gain: the record's design floor; the INA169's "
         "printed gm, nonlinearity, offset, CMR and PSR, and the record's G_CM assumption): nominal %.4f A, highest %.4f A, lowest "
         "%.4f A over the regulation's input range (the accepted drafted regulation: nominal %.4f A, highest %.4f A). The trip reads the "
         "same bank, so the bank's tolerance, TCR, aging and heating cancel between them: the margin is the trip's least sense voltage "
         "less the regulation's highest, over the bank at its highest resistance, %.4f A at its least over the input range (the "
         "accepted design's independent margin %.4f A). The record's trip reproduces exactly (%.6f / %.6f V, %.4f / %.4f A)." % (
             C_["R16"] / 1e3, rw["vreg"][0], rw["vreg"][1], rw["vreg"][2], sel["nom"], sel["hi"], sel["lo"], acc["nom"], acc["hi"],
             sel["m"], acc["m"], tr["lo"], tr["hi"], tr["i_lo"], tr["i_hi"]))
    P("       RIMON_IN candidates (stocked RT0603BRD07, JLCPCB of 1 October 2026): value, code, nominal / highest / lowest A, correlated margin A")
    for rm_ in C_["cands"]:
        g_ = C_["reg"][rm_]
        P("         %5.1fk %-9s %.4f / %.4f / %.4f   %.4f%s" % (rm_ / 1e3, g_["code"], g_["nom"], g_["hi"], g_["lo"], g_["m"],
                                                         "   <- drafted (SESSION: keeps the accepted regulation's band, nominal within 0.5 %)" if rm_ == C_["R16"] else ""))
    wC = C_["worst"]
    wrap("  2f ", "     ", "M2 (CS101) WITH THE SELECTED SENSING (MODELED, the record's model and typical loop rows, U23's typical "
         "bandwidth as a pole at %.0f kHz): the loop now holds the bank's own current, everything behind the bank inside it. The "
         "filtered peak %.4f A at %.0f Hz against the correlated margin %.4f A; the loop branch may be %.2f times its typical model before "
         "the margin is spent (the accepted design: %.4f A at %.0f Hz against %.4f A, room %.2f). Below the loop's crossover the bank's "
         "CS101 current falls far under the accepted one (30 Hz: %.5f A against %.5f A); near the crossover it rises over it (the loop's "
         "typical peak now acts on the ceramics too), inside the larger margin. M2: HOLDS on the accepted model, CONDITIONAL on its "
         "typical loop rows as the accepted design was." % (1e-3 * C_["f_amp"], wC[2], wC[0], sel["m"], C_["room"], m2["old"][2],
                                                             m2["old"][0], acc["m"], acc["loop"], C_["sp"][0][1], m2["sp_old"][0][1]))
    st = O["Cstart"]
    wrap("  2g ", "     ", "THE START, THE RATINGS AND THE WINDOW. The start through Q12 puts at most %.3f A through the bank (the record's "
         "figure with C79 added): U23 then holds IMON_IN at most %.3f V even with no filter, under the IMON_IN fault's least %.2f V, "
         "so the start never trips U5. U23 sits on U18's nets pin for pin, so every rating check (c) and the surge rounds give for U18 "
         "holds for U23 (NETLIST); its supply draw at most %.1f mW. RSENSE1's loss (%.3f W at the regulation's highest) is gone. The "
         "100 W bound, re-run: U23's VIN+ pin, like U18's, takes its output current and its input bias (the record's SESSION "
         "assumption, %.0f mA) from ahead of the bank, so the static bound rises by at most %.4f W, from %.4f W to %.4f W, and check "
         "(b)'s response allowance, with C79's charge added, falls from %.3f ms to %.3f ms, still over the ten typical sums' %.3f ms. "
         "Unchanged: the hold (R8, R9; FBIN on PV_P), the cut-off's band (28.55 to 31.06 V rising, 27.07 V or more falling), the "
         "trip itself, REQ-016's window, D4, the guard's start." % (
             st["i"], st["v_im"], st["ovt_lo"], 1e3 * st["p23"], st["r59_loss"], 1e3 * C_["i_b169"], C_["pb23"], C_["p_static"][0],
             C_["p_static"][1], 1e3 * C_["t_allow"][0], 1e3 * C_["t_allow"][1], 1e3 * C_["t_need"]))
    wrap("  2h ", "     ", "THE ONE NEW UNPRINTED TERM: A7's own output with CSPIN = CSNIN. The sheet prints no current out of IMON_IN for a "
         "negative differential and no figure at zero (p.31); whatever A7 sources at zero ADDS to U23's current and lowers the "
         "regulated input current, away from the trip. The regulation's lowest at 25 V with A7 sourcing (ASSUMPTION, "
         "a sensitivity): %s. That A7 cannot sink is read from p.31's statement that a negative differential drives no current out of "
         "the pin (INFERRED, asked of Analog Devices); were it to sink, the regulation would rise toward the trip: the correlated "
         "margin with A7 sinking %s, and it falls to the accepted design's %.4f A only at a sink of %.2f uA. A bounded PROVISIONAL "
         "choice (the scope amendment, point 2): the regulation's band above holds with A7 at 0 uA; the energy at the limit falls by "
         "about 3 %% per uA sourced. Supplier validation: the IMON_IN pin current of five LT8705AIUHF parts with CSPIN = CSNIN = VIN = "
         "16 V and 25 V and IMON_IN held at 1.20 V, at -20, +25 and +62 C; pass from -0.5 uA (sinking) to +1.0 uA (sourcing): the "
         "regulation within 3 %% of its setting and the margin to the trip at least %.4f A; the clarification to Analog Devices is "
         "drafted, item 8, UNSENT." % (", ".join("%.1f uA %.4f A" % (a_, i_) for a_, i_ in C_["a7z"]),
                                       ", ".join("%.1f uA %.4f A" % (a_, m_) for a_, m_ in C_["sink"]), C_["acc"]["m"], C_["sink_be_acc"],
                                       C_["sink"][0][1]))
    P("")
    # ---------------------------------------------------------------- 3
    P("3. D-10: AN UNRESOLVED PROTECTION DEFECT IN THE PRESENT MODEL (the owner's review of checkpoint 4, part 23)")
    cf_ = O["Cfault"]
    w0_, w1_, w3_ = (cf_["W"][L_] for L_ in cf_["loops"][:3])
    wrap("  ", "  ", "D-10 is not a case that merely lacks evidence: the record's own model, on the circuit as now drafted (C2 composed), "
         "puts parts outside their printed limits. It is written as the receiving company's remaining engineering item E-1 "
         "(SUPPLIER-P1-1-P0SOL.md), with the failing cases, the requirements, the correction needed before any passing claim, and the "
         "outputs that stay PROVISIONAL:")
    wrap("    (a) ", "        ", "THE FAILING CASES (MODELED, a stiff 36 V source, a fault at the connector, no source resistance credited): "
         "F1, stepping onto the port with the guard on at the envelope's least loop %.2f uH: PV_F %.1f V, Q12's VDS %.1f V, INP %.1f V, "
         "TRK_VS %.2f V with D4 carrying %.1f A, the sense bank %.2f V (U21's 100 V and 20 V, the port bank's 100 V, Q12's 100 V, D4, "
         "U18's and U23's +2 V); F2, the same at %.2f uH: PV_F %.1f V, VDS %.1f V, INP %.1f V; F3, at the reference loop %.2f uH: PV_F "
         "%.2f V over the TPS4811-Q1's recommended operating %.0f V VS row (L6P-F10), every other rating inside its line; F4, a source "
         "arriving with the guard off at the least loop: the slew %.2f V/us over the 54 V/us SESSION line (inside %.0f V/us absolute). "
         "Claims hit: IF-01's protection of the solar entry against D-10, R-173's guard as a protection, the backstop's sensing "
         "through the event." % (1e6 * cf_["loops"][0], w0_["vF"], w0_["vds"], w0_["vF"] * cf_["k97"], w0_["vS"], w0_["i4"], w0_["u18"],
                                 1e6 * cf_["loops"][1], w1_["vF"], w1_["vds"], w1_["vF"] * cf_["k97"], 1e6 * cf_["loops"][2], w3_["vF"],
                                 d10["vs_rec"], O["B2"]["rows"][2]["worst"], 1e-6 * d10["slew_abs"]))
    wrap("    (b) ", "        ", "THE REQUIREMENTS, UNCHANGED: L4-E9's single fault D-10 from REQ-015's declared 9 to 36 V source "
         "class; the owner's amendment of 2 October 2026, item 3 (a bounded analysis against the approved fault exposure and "
         "component ratings; REQ-016's window kept; fault protection does not extend the operating range); every part inside its "
         "absolute maximum ratings, the controller inside its recommended conditions while it must act, the record's SESSION 10 % "
         "lines. The envelope stays the record's (0.30 to 10.20 uH, both fault positions, every start the guard is on in); no new "
         "exclusion is adopted to avoid a failure.")
    wrap("    (c) ", "        ", "THE CORRECTION OR JUSTIFIED MODEL REVISION NEEDED BEFORE ANY PASSING CLAIM: something must bound the "
         "current the source drives into the stage's capacitance through the closed guard, or the energy and voltage it delivers to "
         "the port when Q12 opens, at every loop. B1 is rejected at the desk (section 1); B2 is a PARTIAL proposal (section 5); a "
         "supplier may investigate a choke rated over the cut current and damped against CS101, a lower-impedance clamp or a snubber "
         "sized for the port's energy, a different cut-off element or method, or a model revision on measured loops and "
         "resistances only. S1 and S2 then qualify the correction; M2 and M3 are re-run wherever it changes the port.")
    wrap("    (d) ", "        ", "PROVISIONAL until then: IF-01's D-10 protection claim, R-173 as a protection, R-176 rows 2 and 3, "
         "R-180, the port's parts and their Layer 6 rows, board E's port layout and Layer 8 fault table, the guard's Layer 9 rows, "
         "route B2's draft. Completed independently on the present port network: D-16's correction (section 2), the regulation and "
         "its correlated margin, the 100 W bound re-run, M2 with the selected sensing (re-run only if the correction changes the "
         "port), INP's divider ratio.")
    P("")
    P("4. VERDICTS")
    P("  D-16 (B6-ENG-2): CORRECTED on the drafted circuit (composition, netlist and mutations in 2a; electrical acceptance in 2d to 2f), PROVISIONAL in")
    P("    one term (A7's zero-differential output, 2h): sourcing lowers the regulation (energy only); a sink, excluded by p.31's text")
    P("    (INFERRED), is covered by the margin up to %.2f uA." % C_["sink_be_acc"])
    P("  D-10 (B6, L4-F01): an UNRESOLVED PROTECTION DEFECT in the present model, the remaining engineering item E-1 (section 3).")
    P("    CORRECTED within it: U5's absolute-rating violation (0 V by construction, every loop) and INP's margin line (R97 24.9k).")
    P("    Route B2 (section 5) is an unapproved PARTIAL interface proposal; adopting or declining it does not resolve D-10.")
    P("")
    # ---------------------------------------------------------------- 5
    b2 = O["B2"]
    K2_ = K2
    P("5. ROUTE B2: THE SOLAR RECEPTACLE'S PRESENCE PAIR FEEDING U21'S INP (an unapproved PARTIAL proposal; the coordinator's task of")
    P("   5 October 2026, 17:12; it does not resolve D-10, section 3)")
    wrap("  5a ", "     ", "AUTHORITY (B2-PRESENCE.md section 1): reserved.json protects no connector or contact arrangement; but B2 "
         "changes the kit's external interface (BUILD.md and appendix 32.32: the panel, an accessory of the owner's choice, on the "
         "shore plug's second pair; with B2 a panel charges only through a plug that bridges the presence pair), changes the "
         "owner-accepted pick of the wall receptacle (appendix 32.21: D38999/20FC4PN, insert 13-4, four size 16 contacts) and adds "
         "cost, and more than one option stands after the measurement (B2; the drawn interface with the residual measured by S1). By "
         "the owner's two-part test of 21 September 2026 it is the owner's: the owner item is written, and B2 is an unapproved PARTIAL "
         "proposal.")
    wrap("  5b ", "     ", "THE DRAFT (apply_gen_sch_e_p0sol_b2.py, 4 edits): R96, INP's top, from PV_F to the loop's outgoing net PV_PRA; "
         "J_SOLP (JST-XH 1x2, C158012) takes the loop to the inside lead and back to INP (PV_INP); C80 10 nF C0G 100 V (C184799) filters "
         "INP. Composed in L4-E9's order after the C2 draft: %s. The draft refuses a second application (exit %d); the generator runs "
         "(%s). The netlist (NETLIST):" % (", ".join("%s %s" % (s_, "OK" if rc_ == 0 else "REFUSED") for s_, rc_ in K2_["steps"][8:11]),
                                           K2_.get("second", -1), K2_.get("gen", "?")))
    for st_, ok_ in (K2_["checks"] or [])[-4:]:
        P("       %s: %s" % ("holds" if ok_ else "FAILS", st_))
    P("       (and the nine predicates of section 2a, each holds: %s)" % ("yes" if all(ok_ for _s, ok_ in (K2_["checks"] or [])[:-4]) else "NO"))
    P("     Mutations (each must fail the check):")
    for lab_, res_ in K2_["mutations"]:
        P("       %s: %s" % (lab_, res_))
    wrap("  5c ", "     ", "THE WITHDRAWN PLUG. With the presence pair open INP has no source but R97 to GND (and U21's own pull-down, not "
         "credited): from its highest while the guard is on, %.2f V (PV_F at the cut-off's highest %.2f V), it falls under V(INP_L)'s "
         "least %.1f V (PRINTED) in at most %.3f ms through R97 aged and C80 at its largest (%.2f nF), and U21 then pulls Q12's gate "
         "(tPD(INP_L) at most %.0f us, PRINTED; the gate's fall, the record's): Q12 is off at most %.3f ms after the pair opens. A "
         "broken or shorted presence core can only hold INP low: the guard off, never on. On the next plug INP rises only when the "
         "pair makes, last; at the hold's least it crosses V(INP_H)'s most %.1f V in at most %.3f ms, a delay nothing in service sees." % (
             b2["v_inp0"], b2["ov_hi"], b2["inp_l"], 1e3 * b2["t_inp_off"], 1e9 * b2["c80"], b2["tinp"], 1e3 * b2["t_off"], b2["inp_h"],
             1e3 * (b2["t_on_hold"] or 0.0)))
    wrap("  5d ", "     ", "THE ARRIVING SOURCE (the cold connection recomputed as the case every arrival becomes): a stiff 36 V source "
         "meets Q12 off; the power contacts make first (the contact requirement R-180: the pair makes last at every mating point of "
         "the loop), so PV_F is at the source when the pair makes and U21's OV, at or under %.2f V and acting within %.0f us "
         "(PRINTED), holds Q12 off (and BST until it charges, at least 50 ms from discharged, the record's); a source under the "
         "cut-off starts the stage through Q12's gate slew once the pair has made, the record's start (at most %.3f A, under the "
         "breaker's least); "
         "the port's own ring is the record's cold connection, re-run here over the record's whole grid (%.2f to %.2f uH, %d loops), "
         "both fault positions, the port bank at its least and its largest, from a discharged port and from 25 V (%d events; the "
         "worst equals the record's cold maxima):" % (b2["ov_hi"], 1e6 * b2["t_ov"], b2["i_start"], 1e6 * b2["grid"][0], 1e6 * b2["grid"][1],
                                                  b2["grid"][2], b2["n"]))
    P("       quantity                                            worst      absolute     line     the line holds from")
    for r_ in b2["rows"]:
        P("       %-50s  %7.2f %-4s %s   %7.2f   %s" % (r_["lab"], r_["worst"], r_["unit"], ("%7.2f HELD" % r_["abs"]) if r_["abs"] is not None else "   n/a     ",
                                                         r_["line"], "everywhere" if r_["from_"] in (None, 0.0) and r_["line_ok"] else
                                                         ("%.2f uH" % (1e6 * r_["from_"]) if r_["from_"] else "nowhere")))
    wrap("     ", "     ", "PV_F's least %.2f V (VS, CS+, CS- and ISCP rated -1 V to GND): held; the lead's current in the ring at most "
         "%.1f A and D11 at most %.1f mJ (the record's figures). Every absolute rating holds over the whole envelope. The 54 V/us "
         "SESSION margin line on the slew holds only from the loop the table names (at the least loop %.1f V/us, inside the 60 V/us "
         "absolute maximum), and PV_F stays over the recommended 80 V row below the loop the table names: both are carried as "
         "PROVISIONAL, validated by S2 (the arriving source at 0.30 uH on the specimen)." % (
             b2["floor"], b2["i_l"], 1e3 * b2["e11"], b2["rows"][2]["worst"]))
    wrap("  5e ", "     ", "WHAT B2 DOES NOT COVER, OPEN: a second stiff source added on the same lead while a panel holds the presence "
         "loop closed (a parallel connection behind the plug) steps onto the port with the guard on, exactly section 2b's case; and a "
         "stiff source BELOW the stage's voltage arriving after a withdrawal draws the stage's charge back through Q12's body diode "
         "(PV_P back-feeds PV_F through it while the guard is off), the reverse of the step, not computed here. Validation: P1-1's S1 "
         "(both added to its rows).")
    return lines


def main():
    O, R, b6, r3 = compute()
    K = compose_and_check()
    K2 = compose_and_check_b2()
    for k_ in (K, K2):
        if k_.get("refused") or k_.get("checks") is None:
            refuse(4, "the composition does not run: %s %s" % (k_.get("refused"), k_.get("gen")))
        if not all(ok_ for _s, ok_ in k_["checks"]) or not all(r_.startswith("FAILS") or r_.startswith("the generator refused") for _l, r_ in k_["mutations"]):
            refuse(4, "the netlist check does not hold or a mutation passes: %s %s" % (k_["checks"], k_["mutations"]))
        if k_.get("second") != 3:
            refuse(4, "a draft does not refuse a second application")
    sys.stdout.write("\n".join(render(O, K, R, b6, r3, K2)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
