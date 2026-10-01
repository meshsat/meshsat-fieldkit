"""Layer 4 task L4-E8 (MESHSAT-1357, 1 October 2026; v2/docs/records/l4e8/): board A's VBUS20 bank re-sized on a derived dense
node analysis, held as predicates on properties the tests recompute.

The predicates: the derivation meets the re-review's point to the record's 0.001 A and the drawn node's recorded worst can at its
recorded corner within the stated tolerance (consistency, recomputed from the module's own functions); the committed output's
consistency table holds every can figure within the stated tolerance and its finer grids have themselves converged; the chosen
8 mOhm bank meets 2.8 A less the margin at the 2:1 spread at R11 8 mOhm on the sharing basis, recomputed here by the script's own
search on the decision grids and converged, the drawn bank does not, and the layout rule binds (the bank fails at twice it); the
rating applies unmodified at the harmonics' frequencies and each can's loss is under the rated condition's; the draft apply
script checks without writing, applies once to a copy, refuses a second application, refuses the repository's own generator
without a RELEASE.md, adds only unused designators, changes only the bank's arguments, keeps the 8 mOhm bank inside the 7 mOhm
one, and composes with L4-E4's and L4-E6's drafts in every order on disjoint lines; no em or en dash and no claim word in the
record. That the committed .out is what the script prints is checked by running `ripple_dense.py` (about five minutes;
README.md's run order), not here. Nothing here writes into the tree.
"""
import ast
import difflib
import hashlib
import importlib.util
import itertools
import math
import os
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


def _chosen(t, key):
    m_ = re.search(r"R11 %s mOhm, [\d.]+ A: the rule's limit ([\d.]+) A.*?CHOSEN: (\d+) EEHZK1V331P, (\d+) ceramics on VBUS20, (\d+) on FE_OUT" % key, t, re.S)
    assert m_, "no chosen bank at %s mOhm in the output" % key
    return float(m_.group(1)), tuple(int(m_.group(i)) for i in (2, 3, 4))


def t_the_chosen_bank_meets_the_rule_at_2_to_1_at_8_mohm_and_the_drawn_does_not():
    m, R = _m()
    t = _out()
    lim, bank = _chosen(t, "8")
    hi = float(re.search(r"R11 8 mOhm \(C\d+\): ([\d.]+) A; L4-E6 prints", t).group(1))
    assert lim < R["mk"]["rip"] and bank[2] >= 3 and bank[0] >= 6
    M, _f, _ch = _model()
    mk = R["mk"]
    rows = [(mk["f400"][0], mk["f400"][2]), (mk["f800"][0], mk["f800"][2])]
    Md = m.fine_model(M, rows, m.DECIDE)
    lay = dict(sib_dl=m.LAYOUT[0], sib_dr=m.LAYOUT[1])
    res = m.search(m.Node(Md, R["bands"], bank, 0.008, 0.010, 2.0, _hf(m, R), **lay), [Md.weights(hi)], ("odd", "sib"))
    w = m.worst_can(res)
    met = "odd" if w is res[("odd", 0)] else "sib"
    mkn = lambda mm: m.Node(mm, R["bands"], bank, 0.008, 0.010, 2.0, _hf(m, R), **lay)
    conv = m.converge(mkn, m.fine_model(M, rows), w["set"], met, hi)[1][0]
    got = max(math.sqrt(w["ms"]), math.sqrt(conv))
    assert got <= lim + 1e-9, "the chosen bank's worst can at 2:1 is %.4f A against the rule's %.4f A" % (got, lim)
    drawn = (len(R["gen"]["bulk"]), len(R["gen"]["vbus_cer"]) + len(R["gen"]["ch_in"]), len(R["gen"]["cout_pre"]))
    got0 = math.sqrt(m.worst_can(m.search(m.Node(M, R["bands"], drawn, 0.008, 0.010, 2.0, _hf(m, R)), [M.weights(hi)], ("odd",), slice_check=False))["ms"])
    assert got0 > R["mk"]["rip"], "the drawn bank reads %.3f A at 2:1: B-4 would not be open" % got0
    geo = dict(sib_dl=m.GEOM[0], sib_dr=m.GEOM[1])
    got2 = math.sqrt(m.worst_can(m.search(m.Node(M, R["bands"], bank, 0.008, 0.010, 2.0, _hf(m, R), **geo), [M.weights(hi)], ("odd",), slice_check=False))["ms"])
    assert got2 > lim, "the layout rule does not bind: the bank holds at twice it (%.3f A)" % got2


def t_the_rating_applies_unmodified_at_frequency_and_each_loss_is_under_the_rated():
    m, R = _m()
    t = _out()
    _M, (f0, lo, hi), fchs = _model()
    fmin = min(lo, min(fchs))
    corr = R["mk"]["corr"]
    assert all(c == 1.0 for f, c in corr if f >= 100e3) and fmin >= 100e3, (fmin, corr)
    assert any(f == 100e3 for f, _c in corr), "the 100 kHz column of p.2 was not read"
    pct = int(re.search(r"Each can's loss is at most (\d+) % of the rated condition's", t).group(1))
    assert pct < 100
    rows = re.findall(r"^   \| ([\d.]+):1 \| ([\d.]+) A \| ([\d.]+) A \| ([\d.]+) A \| ([\d.]+) mW \| (\d+) % \|$", t, re.M)
    assert len(rows) == 3 and all(float(r[3]) > 0 and int(r[5]) < 100 for r in rows), rows


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
    for bank in ("8", "7"):
        d = tempfile.mkdtemp(prefix="l4e8-apply-")
        try:
            cp = os.path.join(d, "gen_sch_a.py")
            shutil.copyfile(GEN_A, cp)
            orig = _sha(cp)
            r = _run(cp, "--check", "--bank", bank)
            assert r.returncode == 0 and "CHECK OK" in r.stdout and _sha(cp) == orig, (bank, r.returncode, r.stderr)
            r = _run(cp, "--write", "--bank", bank)
            assert r.returncode == 0 and _sha(cp) != orig, (bank, r.returncode, r.stderr)
            r = _run(cp, "--write", "--bank", bank)
            assert r.returncode == 3 and "already applied" in r.stderr, (bank, r.returncode, r.stderr)
            open(cp, "w", encoding="utf-8").write(open(GEN_A, encoding="utf-8").read() + "\n# C236 already here\n")
            r = _run(cp, "--check", "--bank", bank)
            assert r.returncode == 3 and "already used" in r.stderr, (bank, r.returncode, r.stderr)
            open(cp, "w", encoding="utf-8").write("x = 1\n")
            r = _run(cp, "--check", "--bank", bank)
            assert r.returncode == 3 and "occurs 0 times" in r.stderr, (bank, r.returncode, r.stderr)
        finally:
            shutil.rmtree(d)
    assert not os.path.exists(os.path.join(REC, "RELEASE.md")), "RELEASE.md exists: this test assumes the bank is not released"
    r = _run(GEN_A, "--write")
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, (r.returncode, r.stderr)
    assert _run("x", "--bank", "9").returncode == 2
    assert _sha(GEN_A) == before, "the tree's gen_sch_a.py changed"


def t_the_draft_changes_only_the_banks_arguments_by_the_chosen_counts_and_keeps_8_inside_7():
    m, R = _m()
    t = _out()
    D = _load(DRAFT, "apply_bank_t1")
    src = open(GEN_A, encoding="utf-8").read()
    for key in ("8", "7"):
        _lim, bank = _chosen(t, key)
        new = D.patched(src, key)
        a, b = ast.parse(src), ast.parse(new)
        call = lambda tree: [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "lm5176"
                             and n.args and ast.literal_eval(n.args[0]) == "FE"][0]
        ka = {k.arg: ast.literal_eval(k.value) for k in call(a).keywords}
        kb = {k.arg: ast.literal_eval(k.value) for k in call(b).keywords}
        changed = sorted(k for k in set(ka) | set(kb) if ka.get(k) != kb.get(k))
        assert changed and set(changed) <= {"bulk", "cout_extra", "cout_pre"}, changed
        assert [ast.dump(x) for x in call(a).args] == [ast.dump(x) for x in call(b).args]
        strip = lambda tree: [ast.dump(s) for s in tree.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                                                                     and getattr(s.value.func, "id", "") == "lm5176" and ast.literal_eval(s.value.args[0]) == "FE")]
        assert strip(a) == strip(b), "the draft changes something besides the front end's call"
        co = ("C13", "C14", "C15")
        kb.setdefault("cout_extra", ka["cout_extra"])
        vbus = [c for c in co + tuple(kb["cout_extra"]) if c not in kb["cout_pre"]]
        got = (len(kb["bulk"]), len(vbus) + len(R["gen"]["ch_in"]), len(kb["cout_pre"]))
        assert got == bank, "--bank %s draws %s, the output chose %s" % (key, got, bank)
        assert set(kb["cout_pre"]) <= set(co + tuple(kb["cout_extra"])), "a cout_pre part is not one of the stage's ceramics"
        added = (set(kb["bulk"]) | set(kb["cout_extra"])) - (set(ka["bulk"]) | set(ka["cout_extra"]))
        assert all(not re.search(r"\b%s\b" % r, src) for r in added), "a new designator is used already"
        assert kb["bulk_part"] == ka["bulk_part"] == "V331", "one can part number"
    kw = {}
    for key in ("8", "7"):
        call = [n for n in ast.walk(ast.parse(D.patched(src, key))) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "lm5176"
                and n.args and ast.literal_eval(n.args[0]) == "FE"][0]
        kw[key] = {k.arg: ast.literal_eval(k.value) for k in call.keywords}
    assert all(set(kw["8"][k]) <= set(kw["7"][k]) for k in ("bulk", "cout_extra", "cout_pre")), "the 7 mOhm bank does not keep the 8 mOhm bank's parts"


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
    fns = [(os.path.basename(p), (lambda mm: (lambda x: mm.patched(x)))(mm)) for p, mm in zip(OTHERS, mods)] + [("bank", lambda x: D.patched(x, "8"))]
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
