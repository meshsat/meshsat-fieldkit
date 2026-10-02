"""Layer 4 task L4-E8 (MESHSAT-1357, 1 October 2026, the fix rounds after the collaborator's check of 5ff06474 and its recheck of
cc95fe1f; v2/docs/records/l4e8/): board A's VBUS20 bank re-sized on a conservative bound, held as predicates on properties the
tests recompute.

The predicates:
  - consistency: the derivation meets the re-review's point to the record's 0.001 A and the drawn node's recorded worst can at
    its recorded corner within the stated tolerance; the committed output's consistency table holds every can figure and its
    finer grids have converged;
  - B1: the check's eight-can counterexample reproduces (2.738774 A in mean square, 2.854635 A at the 204 / 816 kHz
    coincidence, 2.813686 A at 204 / 408 kHz); B3: the front end's envelope is SNVSAI1D p.6's row carried to RT with its
    tolerance and TCR; B2: the check's ESL counterexample reproduces and lies in the bound's can region, and with no resistance
    floor no count of cans bounds a can; the drawn bank fails on the corrected model;
  - R1/R2: the bound's enclosures hold their sets (random points); a bin's bound is never exceeded by brute-force sampling of
    fully independent configurations (a seed of its own); no end-to-end sample of configurations and operating points exceeds
    the committed figure; the committed bound meets both limits with the chosen ballast and every smaller catalogue value is
    excluded (a feasible configuration over the limit, or the bound over it);
  - the rating applies unmodified at the harmonics' frequencies, and the lifetime is printed CONDITIONAL (B4);
  - R4: with the chosen Cc2 the loop meets its margins at both ends of the cold ESR envelope at L4-E6's R12, both bands, loads
    to the highest permitted current; the drawn Cc2 misses GM 10 dB at the cold end; the acceptance names the bank's envelope;
  - the draft checks without writing, applies once to a copy, refuses a second application, refuses the repository's own
    generator without a RELEASE.md and without L4-E6's R12, adds only unused designators, changes only the helper and the front
    end's call (the ballast and Cc2), draws the other stages as before, and composes with L4-E4's and L4-E6's drafts in every
    order on disjoint lines;
  - no em or en dash and no claim word in the record.
That the committed .out is what the script prints is checked by running `ripple_dense.py` (about eight minutes; README.md's run
order), not here. Nothing here writes into the tree.
"""
import ast
import difflib
import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e8")
SCRIPT = os.path.join(REC, "ripple_dense.py")
OUT = os.path.join(REC, "ripple_dense.out")
DRAFT = os.path.join(REC, "apply_gen_sch_a_bank.py")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
OTHERS = (os.path.join(ROOT, "v2", "docs", "records", "l4e4", "apply_gen_sch_a_r11.py"),
          os.path.join(ROOT, "v2", "docs", "records", "l4e4", "apply_gen_sch_a_r138.py"),
          os.path.join(ROOT, "v2", "docs", "records", "l4e6", "apply_gen_sch_a_r12.py"))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _m():
    """the record's module and its inputs (the generator, the netlist, the record, the makers' rows), read as the script reads them"""
    if "m" not in _C:
        need(SCRIPT, "the L4-E8 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script finds the tree by git)")
        for rel in ("v2/vendor/ti/lm5176-datasheet.pdf", "v2/vendor/ti/bq25731-datasheet.pdf", "v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf",
                    "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"):
            need(os.path.join(ROOT, rel), "an input of the L4-E8 record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("ripple_dense_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        R = {}
        try:
            for rel, want in m.PINS.items():
                assert m.sha(rel) == want, "%s is not the pinned file" % rel
            m.read_generator(R)
            m.read_netlist(R)
            m.read_record(R)
            m.read_makers(R)
        except SystemExit as e:
            raise AssertionError("ripple_dense.py refused its inputs (exit %s)" % e.code)
        R["bands"].update(c_can=R["mk"]["c_can"], esr_can=R["mk"]["esr_can"])
        _C["m"], _C["R"] = m, R
    return _C["m"], _C["R"]


def _model(l2=None, fch=None):
    m, R = _m()
    mk, grid, G = R["mk"], R["grid"], R["gen"]
    rt = m.si(G["rt"], "")
    f0 = 1.0 / (rt * 116e-12 + 190e-9)
    lo, hi = f0 * mk["fsw_row"][0] / mk["fsw_row"][1], f0 * mk["fsw_row"][2] / mk["fsw_row"][1]
    lin = lambda a, b, n: [a + (b - a) * i / (n - 1) for i in range(n)]
    fchs = lin(mk["f400"][0], mk["f400"][2], grid["n_fch"]) + lin(mk["f800"][0], mk["f800"][2], grid["n_fch"])
    M = m.Model(G["rails"]["VBUS20"]["volts"], m.si(G["lval"], "H"), l2 or m.si(G["one"]["L2"][3], "H"), grid["vins"],
                lin(lo, hi, grid["n_fsw"]), lin(grid["vbat"][0], grid["vbat"][1], grid["n_vbat"]), fch or fchs)
    return M, (f0, lo, hi), fchs


def _out():
    need(OUT, "the committed output")
    return open(OUT, encoding="utf-8").read()


def _hf(m, R):
    G = R["gen"]
    return [(m.si(G["one"]["C190"][1], ""), 0.020, 0.5e-9), (m.si(G["one"]["C191"][1], ""), 0.050, 0.5e-9)]


def t_the_model_reproduces_the_rereviews_point_to_its_printed_figure():
    m, R = _m()
    p = R["rec"]["point"]
    _M, (f0, lo, hi), _f = _model()
    Mp = m.Model(R["gen"]["rails"]["VBUS20"]["volts"], m.si(R["gen"]["lval"], "H"), R["rec"]["l2_old"], [p["vin"]], [hi], [p["vbat"]], [p["fch"] * 1e3])
    b = dict(R["bands"])
    b.update(esl_b=[p["esl"] * 1e-9], cer_c=[p["cer"] * 1e-6], cb_k=[p["ck"]])
    nd = m.Node(Mp, b, R["rec"]["second_bank"], 0.010, 0.010, 1.0, _hf(m, R))
    w = Mp.weights(p["iout"])
    vals = sorted(math.sqrt(m.exact(nd.vectors((0, 0, 0, ier, il, ir, i16, 0), ("odd",))["odd"], w)[0])
                  for ier, il, ir, i16 in itertools.product(range(3), range(3), range(2), range(2)))
    near = [v for v in vals if abs(v - p["value"]) <= m.TOL_POINT]
    assert len(near) == 1, "the re-review's %.3f A is matched by %d corners: %s" % (p["value"], len(near), vals[-3:])


def t_the_drawn_nodes_recorded_worst_can_recomputes_within_the_tolerance():
    """The record's corner (ESL 3.5 nH, ceramic 4.0 uF, at the least-damping corners), evaluated by the module, against 2.10 A."""
    m, R = _m()
    M, _f, _ch = _model(l2=R["rec"]["l2_old"])
    b = R["bands"]
    tc = R["rec"]["third_corner"]
    ie = min(range(len(b["esl_b"])), key=lambda i: abs(b["esl_b"][i] - tc["esl"] * 1e-9))
    ic = min(range(len(b["cer_c"])), key=lambda i: abs(b["cer_c"][i] - tc["cer"] * 1e-6))
    drawn = (len(R["gen"]["bulk"]), len(R["gen"]["vbus_cer"]) + len(R["gen"]["ch_in"]), len(R["gen"]["cout_pre"]))
    nd = m.Node(M, b, drawn, 0.010, 0.010, 1.0, _hf(m, R))
    w = M.weights(5.7)
    best = max(m.exact(nd.vectors((ie, ic, icb, ier, il, ir, i16, i11), ("odd",))["odd"], w)[0]
               for icb, ier, il, ir, i16, i11 in itertools.product(range(3), range(3), range(3), range(2), range(2), range(3)))
    want = R["rec"]["third"][(1.0, 5.7)]
    assert abs(math.sqrt(best) - want) <= m.TOL_DENSE, "%.4f A at the record's corner against %.2f A" % (math.sqrt(best), want)


def t_the_committed_consistency_holds_every_can_figure_and_the_finer_grids_converged():
    m, R = _m()
    t = _out()
    rows = re.findall(r"^   \| (drawn \(third fix-up\)|second fix-up|re-review's point) \| ([\d.:]+) \| ([\d.]+) A \| ([\d.]+) A \| ([\d.]+) A \| ([+-][\d.]+) A \| (yes|NO) \|$", t, re.M)
    rec = R["rec"]
    want = {("drawn (third fix-up)", s, i): v for (s, i), v in rec["third"].items()}
    want.update({("second fix-up", s, i): v for (s, i), v in rec["second"].items()})
    assert len(rows) == len(want) + 1, "the validation table has %d rows" % len(rows)
    for node, spread, cur, recd, got, _d, ok in rows:
        if node == "re-review's point":
            assert abs(float(recd) - rec["point"]["value"]) < 1e-9 and abs(float(got) - float(recd)) <= m.TOL_POINT and ok == "yes"
            continue
        s = 1.0 if spread == "1:1" else float(spread.split(":")[0])
        key = (node, s, float(cur))
        assert key in want and abs(float(recd) - want[key]) < 1e-9, "row %s does not carry the record's figure" % (key,)
        assert abs(float(got) - want[key]) <= m.TOL_DENSE and ok == "yes", "row %s: %s A against %s A" % (key, got, recd)
    loop = re.findall(r"^   \| ((?:wide )?\w+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| (yes|NO) \|$", t, re.M)
    assert len(loop) == 9 and all(abs(float(g) - float(w)) <= float(tol) and ok == "yes" for _k, w, g, tol, ok in loop), loop
    assert "CONSISTENCY: every can figure, the re-review's point and the loop within tolerance" in t
    conv = re.search(r"the finer grids themselves converged: .*?read (.*?)$", t, re.S | re.M)
    deltas = [float(x) for x in re.findall(r"\(([+-][\d.]+) A\)", conv.group(1))]
    assert len(deltas) == 3 and all(abs(x) <= 0.001 for x in deltas), deltas
    assert re.search(r"ENUMERATED IN FULL \(110700 sets, 5\.7 A, matched\): 4450 over 2\.8 A \(RECORD: 4450 of 110700\)", t)


def _corrected():
    """the corrected model as the script builds it: B3's envelope from the row, RT's tolerance and TCR, the in-use range"""
    if "me" not in _C:
        m, R = _m()
        mk, grid, G = R["mk"], R["grid"], R["gen"]
        lc = open(os.path.join(ROOT, m.LCSC_FILL), encoding="utf-8").read()
        tol = float(re.search(r'^ \(r"\^40\\\.2k", "R_0603"\): "C\d+",\s+# \S+ \S+, (\d+)%', lc, re.M).group(1)) / 100.0
        need(os.path.join(ROOT, m.UNIROYAL), "the held UNI-ROYAL sheet (RT's TCR)")
        u6 = m.page(m.UNIROYAL, 6)
        tcr = float(re.search(r">10\S*:\s*\S*?(\d+)\s*PPM", u6[u6.find("0603："):]).group(1)) * 1e-6
        import yaml
        env = yaml.safe_load(open(os.path.join(ROOT, m.ENVELOPE), encoding="utf-8"))
        t_air = max(env["worst_inside_air_c"]["lid_open"], env["worst_inside_air_c"]["lid_closed"])
        dt = max(25.0 - env["ambient_c"]["in_use"]["min"], t_air - 25.0)
        fenv = m.fsw_envelope(mk["fsw_row"], mk["rt_row"], m.si(G["rt"], ""), tol, tcr, dt)
        lin = lambda a, b, n: [a + (b - a) * i / (n - 1) for i in range(n)]
        fchs = lin(mk["f400"][0], mk["f400"][2], grid["n_fch"]) + lin(mk["f800"][0], mk["f800"][2], grid["n_fch"])
        Me = m.Model(G["rails"]["VBUS20"]["volts"], m.si(G["lval"], "H"), m.si(G["one"]["L2"][3], "H"), grid["vins"], lin(fenv[0], fenv[2], grid["n_fsw"]),
                     lin(grid["vbat"][0], grid["vbat"][1], grid["n_vbat"]), fchs)
        _C["me"] = (Me, fenv, [(mk["f400"][0], mk["f400"][2]), (mk["f800"][0], mk["f800"][2])])
    return _C["me"]


def _hi(t):
    return {k: float(re.search(r"R11 %s mOhm \(C\d+\): ([\d.]+) A; L4-E6 prints" % k, t).group(1)) for k in ("8", "7")}


def _pick(t):
    m_ = re.search(r"CHOSEN: six EEHZK1V331P as drawn, each in series with a (\d+) mOhm 1 % 2512 ballast, Milliohm HoJLR2512-3W-(\d+)mR-1%, LCSC (C\d+)", t)
    assert m_ and m_.group(1) == m_.group(2), "no chosen ballast in the output"
    return float(m_.group(1)) * 1e-3, m_.group(3)


def _gnode(m, R, model, rb, r11, rb_tol=None):
    mk, b = R["mk"], R["bands"]
    c_k = ((1 - mk["c_tol"]) * (1 - mk["c_life"]), (1 + mk["c_tol"]) * (1 + mk["c_life"]))
    box = m.box_grid([k * mk["c_can"] for k in c_k], mk["esr_life"] * mk["esr_can"], (b["esl_b"][0] + m.RB_ESL[0], b["esl_b"][-1] + m.RB_ESL[1]))
    box["r"] = sorted(set(box["r"]) | {mk["esr_cold"]})
    assert mk["esr_cold"] == 0.3 and mk["size"] == "G", "the sheet's cold limit for size G is not 300 mOhm"
    drawn = (len(R["gen"]["bulk"]), len(R["gen"]["vbus_cer"]) + len(R["gen"]["ch_in"]), len(R["gen"]["cout_pre"]))
    hoj = m.flat(m.page(m.HOJLR, 2))
    tcr = float(re.search(r"±(\d+) \(2mR~500mR\)", hoj).group(1)) * 1e-6
    return m.GNode(model, b, drawn, r11, 0.010, _hf(m, R), box, rb, 0.01 + tcr * m.RB_DT if rb_tol is None else rb_tol, m.LAYOUT)


def t_b1_the_checks_counterexample_reproduces_and_the_rule_counts_it():
    """The check's eight-can corner: 2.738774 A in mean square at 198.8 / 816 kHz, 2.854635 A at the 204 / 816 kHz coincidence and
    2.813686 A at 204 / 408 kHz; the rule (exact coincidences permitted, coherent at the worst phase) puts that bank over 2.8 A."""
    m, R = _m()
    mk, b, G = R["mk"], R["bands"], R["gen"]
    t = _out()
    hi8 = _hi(t)["8"]
    bxc = dict(c=[1.2 * mk["c_can"]], r=[0.3 * mk["esr_can"], 0.6 * mk["esr_can"]], l=[b["esl_b"][0]])
    sx = (0, 0, 0, 0, 1, 0, 0, b["cer_esl"].index(max(b["cer_esl"])), 0, len(b["l16"]) - 1, len(b["l11"]) - 1)
    got = {}
    for tag, fsw, fch, op in (("rss", 198.8e3, 816e3, None), ("4", 204e3, 816e3, (m.Fraction(4), 204e3, 9.0, 10.0)), ("2", 204e3, 408e3, (m.Fraction(2), 204e3, 9.0, 10.0))):
        Mc = m.Model(G["rails"]["VBUS20"]["volts"], m.si(G["lval"], "H"), m.si(G["one"]["L2"][3], "H"), [9.0], [fsw], [10.0], [fch])
        nd = m.GNode(Mc, b, (8, 18, 3), 0.008, 0.010, _hf(m, R), bxc, 0.0, 0.0, m.LAYOUT)
        got[tag] = math.sqrt(m.coherent(nd, sx, Mc, hi8, [(340e3, 460e3), (680e3, 920e3)], op=op)[0] if op else
                             m.exact(nd.vectors(sx, ("odd",))["odd"], Mc.weights(hi8))[0])
    assert abs(got["rss"] - 2.738774) < 5e-4 and abs(got["4"] - 2.854635) < 5e-4 and abs(got["2"] - 2.813686) < 5e-4, got
    assert got["4"] > R["mk"]["rip"] > got["rss"], "the coincidence does not flip that bank: %s" % got


def t_b2_the_checks_esl_counterexample_reproduces_inside_the_decision_box():
    """The check's C3 corner: the eight-can corner above with the siblings' own ESL at the band's 3.5 nH plus the layout's 0.5 nH,
    3.586976 A in mean square; that corner's can lies inside the bound's can region of the ballasted bank."""
    m, R = _m()
    mk, b, G = R["mk"], R["bands"], R["gen"]
    hi8 = _hi(_out())["8"]
    Mc = m.Model(G["rails"]["VBUS20"]["volts"], m.si(G["lval"], "H"), m.si(G["one"]["L2"][3], "H"), [9.0], [198.8e3], [10.0], [816e3])
    bxc = dict(c=[1.2 * mk["c_can"]], r=[0.3 * mk["esr_can"], 0.6 * mk["esr_can"]], l=[b["esl_b"][0], b["esl_b"][-1]])
    sx = (0, 0, 0, 0, 1, 1, 0, b["cer_esl"].index(max(b["cer_esl"])), 0, len(b["l16"]) - 1, len(b["l11"]) - 1)
    nd = m.GNode(Mc, b, (8, 18, 3), 0.008, 0.010, _hf(m, R), bxc, 0.0, 0.0, m.LAYOUT)
    got = math.sqrt(m.exact(nd.vectors(sx, ("odd",))["odd"], Mc.weights(hi8))[0])
    assert abs(got - 3.586976) < 5e-4, got
    rb, _code = _pick(_out())
    can = _regs(m, R)[1](rb)
    assert can["l"][0] <= b["esl_b"][0] + m.RB_ESL[0] + 1e-15 and can["l"][1] >= b["esl_b"][-1] + m.RB_ESL[1] + m.LAYOUT[0] - 1e-15 \
        and can["r"][1] >= rb + 0.6 * mk["esr_can"] and can["c"][0] <= 1.2 * mk["c_can"] <= can["c"][1], "the corner's can is outside the bound's region"


def t_b3_the_envelope_is_the_specified_row_carried_to_rt_with_its_tolerance():
    m, R = _m()
    _Me, fenv, _rows = _corrected()
    mk = R["mk"]
    eq5 = lambda r: r * 116e-12 + 190e-9
    plain = [x * eq5(mk["rt_row"]) / eq5(m.si(R["gen"]["rt"], "")) for x in mk["fsw_row"]]
    assert fenv[0] < plain[0] < fenv[1] < plain[2] < fenv[2], (fenv, plain)
    assert fenv[0] < 175e3 * eq5(mk["rt_row"]) / eq5(40.2e3) < 180e3, "the envelope does not reach below the record's 180.3 kHz"
    t = _out()
    shown = [float(x) * 1e3 for x in re.search(r"inside air\): ([\d.]+) / ([\d.]+) / ([\d.]+) kHz", t).groups()]
    assert all(abs(a - b_) < 10.0 for a, b_ in zip(shown, fenv)), (shown, fenv)


def t_b2_without_a_resistance_floor_no_count_of_cans_bounds_a_can():
    m, R = _m()
    Me, _f, _rows = _corrected()
    hi8 = _hi(_out())["8"]
    for nb in (6, 8):
        nd = _gnode(m, R, Me, 0.0, 0.008, rb_tol=0.0)
        nd.nb = nb
        g = m.gsearch(nd, Me.weights(hi8))
        assert math.sqrt(g["ms"]) > 10.0, "%d cans with no floor read %.2f A" % (nb, math.sqrt(g["ms"]))


def _regs(m, R):
    """the bound's regions as ripple_dense.py's compute() builds them (section 6), and the can's region for a ballast value"""
    mk, b, G = R["mk"], R["bands"], R["gen"]
    hoj = m.flat(m.page(m.HOJLR, 2))
    tol = 0.01 + float(re.search(r"±(\d+) \(2mR~500mR\)", hoj).group(1)) * 1e-6 * m.RB_DT
    c_k = ((1 - mk["c_tol"]) * (1 - mk["c_life"]), (1 + mk["c_tol"]) * (1 + mk["c_life"]))
    drawn = (len(G["bulk"]), len(G["vbus_cer"]) + len(G["ch_in"]), len(G["cout_pre"]))
    hf = _hf(m, R)
    band = lambda v, e: dict(c=(m.HF_BAND["c"][0] * v, m.HF_BAND["c"][1] * v), r=(m.HF_BAND["esr"][0] * e, m.HF_BAND["esr"][1] * e), l=m.HF_BAND["esl"])
    regs = dict(cer=dict(r=(b["cer_esr"][0], b["cer_esr"][-1]), l=(b["cer_esl"][0], b["cer_esl"][-1]), c=(b["cer_c"][0], b["cer_c"][-1])),
                c190=band(hf[0][0], hf[0][1]), c191=band(hf[1][0], hf[1][1]), l11=(b["l11"][0], b["l11"][-1]), l16=(b["l16"][0], b["l16"][-1]),
                r16=(0.010 * (1 - tol), 0.010 * (1 + tol)), r_tol=tol, n_fe=drawn[2], n_vb=drawn[1], n_can=drawn[0])
    can = lambda rb: dict(r=(rb * (1 - tol), rb * (1 + tol) + mk["esr_cold"] + m.LAYOUT[1]),
                          l=(b["esl_b"][0] + m.RB_ESL[0], b["esl_b"][-1] + m.RB_ESL[1] + m.LAYOUT[0]), c=(c_k[0] * mk["c_can"], c_k[1] * mk["c_can"]))
    return regs, can


def _bin_bound(m, regs, can, r11, f1, f2):
    """one bin's bound on each source's transfer to the can, every source-side cell together (the weakest claim the script makes)"""
    w1, w2 = 2 * math.pi * f1, 2 * math.pi * f2
    Hcer = m.ihull(m.branch_rect(regs["cer"], w1, w2))
    A = m.pscale(Hcer, regs["n_fe"])
    A2 = m.mink(m.ihull(m.branch_rect(regs["c190"], w1, w2)), m.ihull(m.branch_rect(regs["c191"], w1, w2)))
    Z16 = m.zrect(regs["r16"][0], regs["r16"][1], w1 * regs["l16"][0], w2 * regs["l16"][1])
    Zl = m.zrect(r11 * (1 - regs["r_tol"]), r11 * (1 + regs["r_tol"]), w1 * regs["l11"][0], w2 * regs["l11"][1])
    Q = m.mink(m.mink(m.mink(m.pscale(Hcer, regs["n_vb"]), m.ihull(m.mink(Z16, m.ihull(A2)))), m.pscale(m.ihull(m.branch_rect(can, w1, w2)), regs["n_can"] - 1)),
               m.ihull(m.mink(Zl, m.ihull(A))))
    T = m.tmax_bb(m.branch_rect(can, w1, w2), Q, 1e-3)[0]
    return T / m.kmin_bb(Zl, A, 1e-3), T / m.kmin_bb(Z16, A2, 1e-3)


def _draw(rnd, regs, can, r11, p_ext=0.7):
    def u(lo, hi):
        x = rnd.random()
        return lo if x < p_ext / 2 else hi if x < p_ext else lo + rnd.random() * (hi - lo)
    br = lambda reg: (u(*reg["r"]), u(*reg["l"]), u(*reg["c"]))
    return dict(t=br(can), sib=[br(can) for _ in range(regs["n_can"] - 1)], cer_v=[br(regs["cer"]) for _ in range(regs["n_vb"])],
                cer_o=[br(regs["cer"]) for _ in range(regs["n_fe"])], r11=u(r11 * (1 - regs["r_tol"]), r11 * (1 + regs["r_tol"])), l11=u(*regs["l11"]),
                c190=br(regs["c190"]), c191=br(regs["c191"]), r16=u(*regs["r16"]), l16=u(*regs["l16"]))


def t_r1_the_enclosures_hold_their_sets():
    """inv_hull holds every image point of its rectangle; mink equals the hull of the vertex sums"""
    m, _R = _m()
    rnd = random.Random(7)
    for _ in range(40):
        r0 = rnd.uniform(1e-3, 0.05)
        x0 = rnd.uniform(-0.5, 0.2)
        P = m.zrect(r0, r0 + rnd.uniform(0, 0.3), x0, x0 + rnd.uniform(0, 0.5))
        H = m.ihull(P)
        for _ in range(300):
            y = 1 / complex(rnd.uniform(P[0][0], P[1][0]), rnd.uniform(P[0][1], P[2][1]))
            assert m.pdist(y.real, y.imag, H) == 0.0, "a point of the image lies outside its enclosure"
    for _ in range(40):
        A = m.cvx_hull([(rnd.gauss(0, 1), rnd.gauss(0, 3)) for _ in range(rnd.randint(3, 20))])
        B = m.cvx_hull([(rnd.gauss(5, 2), rnd.gauss(0, 1)) for _ in range(rnd.randint(3, 20))])
        M, H = m.mink(A, B), m.cvx_hull([(a[0] + b_[0], a[1] + b_[1]) for a in A for b_ in B])
        assert max(m.pdist(x, y, M) for x, y in H) < 1e-9 and max(m.pdist(x, y, H) for x, y in M) < 1e-9


def t_r1_the_bin_bound_is_never_exceeded_by_brute_force_sampling():
    """fully independent branches, each parameter at an end of its interval with probability 0.7, at a random frequency in the
    bin: each source's transfer to the can at most the bin's bound (a seed of its own, not the script's)"""
    m, R = _m()
    rb, _code = _pick(_out())
    regs, canf = _regs(m, R)
    can = canf(rb)
    rnd = random.Random(424242)
    for r11 in (0.007, 0.008):
        for f in (190e3, 410e3, 610e3, 1.3e6, 9.6e6, 14e6, 40e6):
            f2 = f * 1.005
            bfe, bch = _bin_bound(m, regs, can, r11, f, f2)
            worst = 0.0
            for _ in range(250):
                c = _draw(rnd, regs, can, r11)
                tf, tc = m.net_t(c, 2 * math.pi * (f + rnd.random() * (f2 - f)))
                worst = max(worst, abs(tf) / bfe, abs(tc) / bch)
            assert worst <= 1.0, "at %.0f kHz a sample reads %.4f of the bound" % (f / 1e3, worst)


def t_r1_no_end_to_end_sample_exceeds_the_committed_figure():
    """random fully independent configurations and operating points (VIN from the bound's grid, fSW in B3's envelope, VBAT from
    10 V up, fCH in a row; half at an exact coincidence fch = (p/q) fsw added at |a| + |c|, half with L16 resonating with C190 on a
    charger harmonic): the can's rms with the bound's 120 harmonics at most the committed figure of its outcome"""
    m, R = _m()
    t = _out()
    rb, _code = _pick(t)
    regs, canf = _regs(m, R)
    can = canf(rb)
    hi = _hi(t)
    figs = {k: float(re.search(r"R11 %s mOhm, [\d.]+ A: every can at most ([\d.]+) A against" % k, t).group(1)) for k in ("8", "7")}
    _Me, fenv, rows = _corrected()
    G = R["gen"]
    vout, l1, l2 = G["rails"]["VBUS20"]["volts"], m.si(G["lval"], "H"), m.si(G["one"]["L2"][3], "H")
    rnd = random.Random(99)
    for key, r11 in (("8", 0.008), ("7", 0.007)):
        for n in range(60):
            c = _draw(rnd, regs, can, r11)
            vin, vbat = rnd.choice(m.VIN_BOUND), 10.0 + 0.05 * rnd.randint(0, 136)
            lo, hi_ = rnd.choice(rows)
            fsw = fenv[0] + rnd.random() * (fenv[2] - fenv[0])
            if n % 2:
                pq = rnd.choice([m.Fraction(p, q) for p in range(1, 5) for q in range(1, 5) if lo / fenv[2] <= p / q <= hi_ / fenv[0]])
                fsw = min(max(fsw, lo / float(pq)), hi_ / float(pq), fenv[2])
                fch = fsw * pq
            else:
                fch = lo + rnd.random() * (hi_ - lo)
                lt = 1 / ((2 * math.pi * rnd.randint(5, 40) * fch) ** 2 * c["c190"][2]) - c["c190"][1]
                if regs["l16"][0] <= lt <= regs["l16"][1]:
                    c["l16"] = lt
            a = m.src_fe(vout, l1, vin, fsw, hi[key], 120)[0]
            b_ = m.src_ch(vout, l2, vbat, fch, hi[key], 120)[0]
            A = {round((k + 1) * fsw, 3): abs(x * m.net_t(c, 2 * math.pi * (k + 1) * fsw)[0]) for k, x in enumerate(a)}
            C = {round((k + 1) * fch, 3): abs(x * m.net_t(c, 2 * math.pi * (k + 1) * fch)[1]) for k, x in enumerate(b_)}
            ms = sum(x * x for f_, x in A.items() if f_ not in C) + sum(x * x for f_, x in C.items() if f_ not in A) \
                + sum((A[f_] + C[f_]) ** 2 for f_ in A if f_ in C)
            assert math.sqrt(ms) <= figs[key], "R11 %s mOhm: a sample reads %.4f A against the figure %.4f A" % (key, math.sqrt(ms), figs[key])


def t_r1_the_committed_bound_meets_both_limits_and_smaller_values_are_excluded():
    m, R = _m()
    t = _out()
    rb, _code = _pick(t)
    for key in ("8", "7"):
        got = re.search(r"R11 %s mOhm, [\d.]+ A: every can at most ([\d.]+) A against ([\d.]+) A \(meets\)" % key, t)
        assert got and float(got.group(1)) <= float(got.group(2)), "the bound at %s mOhm does not meet its limit" % key
    rows = re.findall(r"^   \| (\d+) mOhm \(C\d+\) \| (\S+)(?: A)? \| (\S+)(?: A)? \| \S+(?: A)? \| \S+(?: A)? \| (.+) \|$", t, re.M)
    assert rows and rows[-1][0] == "%.0f" % (rb * 1e3) and rows[-1][3] == "TAKEN", rows[-3:]
    lim7 = float(re.search(r"R11 7 mOhm, [\d.]+ A: every can at most [\d.]+ A against ([\d.]+) A", t).group(1))
    for v, b7, f7, outc in rows[:-1]:
        assert (outc.startswith("excluded") and float(f7) > lim7) or (outc.startswith("the bound does not") and float(b7) > lim7), (v, b7, f7, outc)
    assert re.search(r"CONSERVATIVE, CHECKED: \d+ seeded random .* read at most (0\.\d+|1\.0000) of the bin's bound", t)


def t_the_drawn_bank_fails_on_the_corrected_model():
    m, R = _m()
    t = _out()
    Me, _f, _rows = _corrected()
    hi8 = _hi(t)["8"]
    drawn = (len(R["gen"]["bulk"]), len(R["gen"]["vbus_cer"]) + len(R["gen"]["ch_in"]), len(R["gen"]["cout_pre"]))
    res = m.search(m.Node(Me, R["bands"], drawn, 0.008, 0.010, 2.0, _hf(m, R)), [Me.weights(hi8)], ("odd",), slice_check=False)
    assert math.sqrt(res[("odd", 0)]["ms"]) > R["mk"]["rip"], "the drawn bank meets 2.8 A at 2:1"


def t_the_rating_applies_in_frequency_and_the_lifetime_is_conditional():
    m, R = _m()
    Me, fenv, rows = _corrected()
    fmin = min(fenv[0], rows[0][0])
    corr = R["mk"]["corr"]
    assert all(c == 1.0 for f, c in corr if f >= 100e3) and fmin >= 100e3 and any(f == 100e3 for f, _c in corr), (fmin, corr)
    t = _out()
    assert "TEMPERATURE AND LIFE: CONDITIONAL (B4)" in t and "the obligation: the can's top temperature at the worst ripple" in t
    assert "so its own rise is under the rated one" not in t


def _cc2(t):
    m_ = re.search(r"CHOSEN: Cc2 (\S+) \((C\d+), lcsc_fill\.py\)", t)
    assert m_, "no chosen Cc2 in the output"
    return m_.group(1), m_.group(2)


def t_r4_the_loop_holds_the_cold_envelope_with_the_chosen_cc2_and_not_with_the_drawn_one():
    """recomputed here at the envelope's two ends (the script scans it whole): the chosen ballast and Cc2, R12 12 mOhm, B3's
    envelope, loads to the highest permitted current, the cans' intrinsic ESR 0 and 300 mOhm, both bands; the drawn Cc2 misses
    GM 10 dB at the cold end"""
    m, R = _m()
    t = _out()
    rb, _code = _pick(t)
    cc2_text, cc2_code = _cc2(t)
    lc = open(os.path.join(ROOT, m.LCSC_FILL), encoding="utf-8").read()
    pat = cc2_text.replace(".", chr(92) + ".")
    assert any(('(r"^%s%s", "C_0603"): "%s"' % (pat, e, cc2_code)) in lc for e in ("$", "")), "the Cc2 code is not lcsc_fill.py's"
    hi = _hi(t)
    _Me, fenv, _rows = _corrected()
    mk, G, rec = R["mk"], R["gen"], R["rec"]
    si = m.si
    vout = G["rails"]["VBUS20"]["volts"]
    cfg = dict(fsw=(fenv[1], fenv[0], fenv[2]), gm=mk["gm"], ro=mk["ro"], acs=mk["acs"], L=si(G["lval"], "H"),
               vout=mk["vref"][1] * (1 + si(G["rfb_top"], "") / si(G["rfb_bot"], "")),
               kfb=si(G["rfb_bot"], "") / (si(G["rfb_top"], "") + si(G["rfb_bot"], "")), modes=[("boost", 9.0), ("buck", 36.0), ("buck", 24.0)],
               iouts=[rec["loop_stage"]["iout"], 0.25], cl0=rec["loop_stage"]["cl0"], ncer0=rec["loop_stage"]["ncer0"], esr_l=0.0004,
               c_can=mk["c_can"], esr_can=mk["esr_can"], p_bound=rec["loop_stage"]["p"])
    comp = tuple(si(v, "") for v, _l in G["comp"])
    new = (comp[0], comp[1], si(cc2_text, ""))
    assert new[2] > comp[2], "the chosen Cc2 is not larger than the drawn one"
    _regs_, canf = _regs(m, R)
    tol = _regs_["r_tol"]
    c_k = ((1 - mk["c_tol"]) * (1 - mk["c_life"]), (1 + mk["c_tol"]) * (1 + mk["c_life"]))
    nb, ncer = len(G["bulk"]), len(G["vbus_cer"]) + len(G["ch_in"]) + len(G["cout_pre"])
    loads = sorted({hi["8"], hi["7"], rec["loop_stage"]["iout"], 0.25}, reverse=True)
    ok = lambda x: x["pm"] >= 50 and x["gm"] >= 10 and x["mm"] >= 0.5 and x["ceil_ok"] and x["all_cross"] and x["z_ratio"] <= 1.0
    for e in (0.0, mk["esr_cold"]):
        bulk = [(k * mk["c_can"], x) for k in c_k for x in (rb * (1 - tol) + e, rb * (1 + tol) + e)]
        for kw in ({}, dict(qs=rec["wide"]["q"], lks=rec["wide"]["lk"])):
            x = m.loop_eval(cfg, nb, ncer, m.R12_E6, *new, bulk=bulk, iouts=loads, p_bound=vout * loads[0], **kw)
            assert ok(x), (e, kw, x)
    cold = [(k * mk["c_can"], x) for k in c_k for x in (rb * (1 - tol) + mk["esr_cold"], rb * (1 + tol) + mk["esr_cold"])]
    wc = m.loop_eval(cfg, nb, ncer, m.R12_E6, *comp, qs=rec["wide"]["q"], lks=rec["wide"]["lk"], bulk=cold, iouts=loads, p_bound=vout * loads[0])
    assert wc["gm"] < 10, "the drawn Cc2 holds GM %.2f dB at the cold end: the change would not be needed" % wc["gm"]
    assert "the bank's ESR envelope at -20 C over service life at" in t and "or below the modelled envelope" in t


def t_the_draft_refuses_the_tree_without_l4e6s_r12():
    need(GEN_A, "board A's generator")
    src = open(GEN_A, encoding="utf-8").read()
    D = _load(DRAFT, "apply_bank_t0")
    r12 = _load(OTHERS[2], "apply_r12_t0")
    assert D.fe_rcs(src) is None, "the drawn front end already sets rcs"
    try:
        D.order_ok(src)
        raise AssertionError("order_ok() passed the drawn R12")
    except SystemExit as e:
        assert e.code == 3
    with_r12 = r12.patched(src)
    assert D.fe_rcs(with_r12) == "12m"
    D.order_ok(with_r12)
    D.order_ok(D.patched(with_r12))


def _run(*a):
    return subprocess.run([sys.executable, "-B", DRAFT] + list(a), capture_output=True, text=True)


def _load(p, name):
    sp = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def t_the_draft_checks_applies_once_refuses_a_second_and_the_tree_without_release():
    need(GEN_A, "board A's generator")
    need(DRAFT, "the draft apply script")
    before = _sha(GEN_A)
    d = tempfile.mkdtemp(prefix="l4e8-apply-")
    try:
        cp = os.path.join(d, "gen_sch_a.py")
        shutil.copyfile(GEN_A, cp)
        orig = _sha(cp)
        r = _run(cp, "--check")
        assert r.returncode == 0 and "CHECK OK" in r.stdout and _sha(cp) == orig, (r.returncode, r.stderr)
        r = _run(cp, "--write")
        assert r.returncode == 0 and _sha(cp) != orig, (r.returncode, r.stderr)
        r = _run(cp, "--write")
        assert r.returncode == 3 and "already applied" in r.stderr, (r.returncode, r.stderr)
        open(cp, "w", encoding="utf-8").write(open(GEN_A, encoding="utf-8").read() + "\n# R221 already here\n")
        r = _run(cp, "--check")
        assert r.returncode == 3 and "already used" in r.stderr, (r.returncode, r.stderr)
        open(cp, "w", encoding="utf-8").write("x = 1\n")
        r = _run(cp, "--check")
        assert r.returncode == 3 and "occurs 0 times" in r.stderr, (r.returncode, r.stderr)
    finally:
        shutil.rmtree(d)
    assert not os.path.exists(os.path.join(REC, "RELEASE.md")), "RELEASE.md exists: this test assumes the bank is not released"
    r = _run(GEN_A, "--write")
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, (r.returncode, r.stderr)
    assert _run("a", "b").returncode == 2
    assert _sha(GEN_A) == before, "the tree's gen_sch_a.py changed"


def _fe_call(tree):
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "lm5176" and n.args
            and ast.literal_eval(n.args[0]) == "FE"][0]


def t_the_draft_adds_only_the_ballast_and_leaves_the_other_stages_as_drawn():
    m, R = _m()
    t = _out()
    rb, code = _pick(t)
    D = _load(DRAFT, "apply_bank_t1")
    src = open(GEN_A, encoding="utf-8").read()
    new = D.patched(src)
    a, b = ast.parse(src), ast.parse(new)
    ka = {k.arg: ast.literal_eval(k.value) for k in _fe_call(a).keywords}
    kb = {k.arg: ast.literal_eval(k.value) for k in _fe_call(b).keywords}
    assert sorted(k for k in set(ka) | set(kb) if ka.get(k) != kb.get(k)) == ["bulk_ballast", "comp"]
    assert kb["comp"][:2] == ka["comp"][:2] and kb["comp"][2] == _cc2(t), (ka["comp"], kb["comp"])
    refs, value, lcsc = kb["bulk_ballast"]
    assert len(refs) == len(kb["bulk"]) == len(R["gen"]["bulk"]) and kb["bulk_part"] == "V331"
    assert all(not re.search(r"\b%s\b" % r_, src) for r_ in refs), "a ballast designator is used already"
    assert m.si(value, "Ohm") == rb and lcsc == code, (value, lcsc, rb, code)
    fd = lambda tree: [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "lm5176"][0]
    fa, fb = fd(a), fd(b)
    assert [x.arg for x in fb.args.args] == [x.arg for x in fa.args.args] + ["bulk_ballast"] and ast.unparse(fb.args.defaults[-1]) == "None"
    old_part = [ast.dump(n) for n in ast.walk(fa) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "part" and n.args
                and isinstance(n.args[0], ast.Name) and n.args[0].id == "cb"]
    new_else = [ast.dump(n) for st in ast.walk(fb) if isinstance(st, ast.If) and ast.unparse(st.test) == "bulk_ballast" for n in st.orelse
                for n in ast.walk(n) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "part"]
    assert old_part and old_part == new_else, "without bulk_ballast the helper does not draw the cans as before"
    keep = lambda tree: [ast.dump(s) for s in tree.body if not (isinstance(s, ast.FunctionDef) and s.name == "lm5176")
                         and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and getattr(s.value.func, "id", "") == "lm5176"
                                  and ast.literal_eval(s.value.args[0]) == "FE")]
    assert keep(a) == keep(b), "the draft changes something besides the helper and the front end's call"
    other = lambda tree: [ast.dump(n) for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "lm5176"
                          and ast.literal_eval(n.args[0]) != "FE"]
    assert other(a) == other(b) and len(other(a)) == 6, "another stage's call changed"


def _changed_lines(src, new):
    out = set()
    for tag, i1, i2, _j1, _j2 in difflib.SequenceMatcher(None, src.splitlines(), new.splitlines(), autojunk=False).get_opcodes():
        if tag != "equal":
            out |= set(range(i1, max(i2, i1 + 1)))
    return out


def t_the_draft_composes_with_l4e4_and_l4e6_in_every_order_on_disjoint_lines():
    need(GEN_A, "board A's generator")
    for p in OTHERS:
        need(p, "a draft of L4-E4 or L4-E6")
    src = open(GEN_A, encoding="utf-8").read()
    mods = [_load(p, "other_%d" % i) for i, p in enumerate(OTHERS)]
    D = _load(DRAFT, "apply_bank_t2")
    fns = [(os.path.basename(p), (lambda mm: (lambda x: mm.patched(x)))(mm)) for p, mm in zip(OTHERS, mods)] + [("bank", D.patched)]
    lines = {name: _changed_lines(src, f(src)) for name, f in fns}
    names = [n for n, _f in fns]
    for a_, b_ in itertools.combinations(names, 2):
        assert not (lines[a_] & lines[b_]), "%s and %s touch the same lines %s" % (a_, b_, sorted(lines[a_] & lines[b_]))
    finals = set()
    for order in itertools.permutations(fns):
        x = src
        for _n, f in order:
            x = f(x)
        ast.parse(x)
        finals.add(x)
    assert len(finals) == 1, "the four drafts do not commute"


def t_no_em_or_en_dash_and_no_claim_word_in_the_record():
    words = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives|rated for)\b", re.I)
    need(REC, "the L4-E8 record")
    files = [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.endswith((".md", ".py", ".out"))]
    assert len(files) >= 6, files
    for p in files + [os.path.abspath(__file__)]:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % p
    for p in files:
        hits = words.findall(open(p, encoding="utf-8").read())
        assert not hits, "%s carries %s" % (p, hits)
