"""Record l4reg (Layer 4 task L4A-56 re-scoped by W135's CHANGE-METHOD; RE-6 and RE-7; MESHSAT-1357, 7 October 2026, W138;
v2/docs/records/l4reg/): the supervisors' regulator stage compared over three approaches, the selection, and its draft on board B,
v2/docs/records/l9t5/apply_gen_sch_b_regstage.py. A desk design on printed figures; nothing here is a measurement or an acceptance.

The predicates: the committed .out is what the script prints (where the held-back sheets' texts are present); the acceptance judge
holds on the selected stage and FAILS (refusing it at J0) a TYPICAL figure used as a limit, the AP2112K at the new current, the order code without
M3 and a thermal resistance one step over the requirement; the limiter's band and the regulator's requirement reproduce W135's
figures; the draft composes after record l9t5's iocguard and reads DRAWN by pin and value, while the state before it and every
mutation FAIL; it composes with W137's canmb in either order to the same netlist; it refuses a generator without iocguard, a second
application and the tree's own generator; the fetch script pins exactly the held sheets the script declares; the page carries the
output's key figures, no em or en dash and no claim word. Nothing here writes the tree."""
import ast
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4reg")
SCRIPT = os.path.join(REC, "l4reg_compare.py")
OUT = os.path.join(REC, "l4reg_compare.out")
PAGE = os.path.join(REC, "L4REG.md")
FETCH = os.path.join(REC, "fetch_held_back.py")
DRAFT = os.path.join(ROOT, "v2", "docs", "records", "l9t5", "apply_gen_sch_b_regstage.py")
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
_C = {}


def _M():
    if "m" not in _C:
        need(SCRIPT, "record l4reg's comparison script")
        sp = importlib.util.spec_from_file_location("l4reg_compare_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C["m"] = m
    return _C["m"]


def _texts():
    """Skip where a declared text is absent (the held-back sheets are fetched by fetch_held_back.py, their texts re-taken)."""
    m = _M()
    absent = [t for t, digest, _held in m.PT.inputs(ROOT, m.PDFTEXT) if digest is None]
    if absent:
        raise Skip("the declared texts are absent (%s): python3 v2/docs/records/l4reg/fetch_held_back.py, then "
                   "python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4reg" % ", ".join(absent))
    if "S" not in _C:
        _C["S"] = m.sheets()
    return m, _C["S"]


def _base(m, S):
    lo, hi = m.band_of(m.R_ILIM, S)
    reg = dict(rja=(S["rja_new"][0]["DCQ"], "PRINTED", "5.4"), vdo1a=S["vdo_new"], acc=S["acc_new"])
    st = dict(ios_lo=(lo, "PRINTED", "row"), ios_hi=(hi, "PRINTED", "row"), rja=reg["rja"], vdo1a=reg["vdo1a"], acc=reg["acc"],
              iout=S["iout"], icl_min=(S["icl"][0][0], "PRINTED", "5.6"), vin_max=(S["vin"][0][1], "PRINTED", "5.3"),
              t_latch=(S["tlatch"][0][2], "PRINTED", "7.5"), lim_rja=S["lim_rja"], ron=S["ron"], short=S["short_dur"])
    T, D = m.T, m.D
    P, DP, G = T.figures(), D.figures(), D.gndret()
    E = m.rows()
    avail, (lo14, nom14, hi14), _r, _f = m.path(E, P, DP, G)
    drop = hi14 - 3.3 * P["vout_lo"]
    served = {"S1": E["s1"][0], "S2": E["bab_v"][0], "f1": E["f1"][0]}
    served.update({f: E["held"][f][0] - E["share"][0] + P["can_dom_hi"] for f in ("B1", "B2", "B3", "B4", "B5")})
    R = dict(air=E["air"][0], tj=T.TJ_GOAL, drop=drop, served=served, avail=avail, hi14=hi14, u601=E["u601"][0], vh=E["vh"][0])
    return st, R, P, (lo, hi)


def t_the_committed_output_is_what_the_script_prints():
    _texts()
    with tempfile.TemporaryDirectory(prefix="t_l4reg_") as d:
        env = dict(os.environ, TMPDIR=d)
        r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True, cwd=ROOT, env=env)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l4reg_compare.out is not what l4reg_compare.py prints; regenerate it with _bin/regen_out.py"
    t = r.stdout.decode()
    for s in ("against 3.7486 V on the AP2112's rows: EQUAL to W135's printed figures", "TPS73733DCQRM3 (SOT-223, new silicon)         76.0     115.0",
              "SELECTED (SESSION W138-1): A", "A's verdict on its rows: HOLDS", "B's verdict: NOT SUPPORTED ON PRINTED FIGURES",
              "C's verdict: FAILS", "read by pin and value: DRAWN", "l4reg_compare: done"):
        assert s in t, s
    assert " NO\n" not in t.split("11. THE PREDICATES")[1], "a predicate reads NO"


def t_the_band_and_the_requirement_reproduce_w135():
    m, S = _texts()
    lo, hi = m.band_of(m.R_ILIM, S)
    assert abs(lo - 0.4702) < 5e-5 and abs(hi - 0.5878) < 5e-5, (lo, hi)      # W159 (W157-F2): the envelope, TI's Equation 1 at 49.4 kOhm
    w_lo, w_hi = m.band_row(S["ios49"][0], S["ios_eq"][0], m.R_TOL)
    assert abs(w_lo - 0.4702) < 5e-5 and abs(w_hi - 0.5704) < 5e-5 and hi > w_hi, "W135's rule alone understates TI's printed maximum"
    assert m.band_of(m.R_ILIM, S) != m.band_row(S["ios49"][0], S["ios_eq"][0], 0.0), "the resistor's 1 % must widen the tested row"
    lo102, hi102 = m.band_of(102.0, S)
    assert hi102 < 0.31 and lo102 < 0.23, (lo102, hi102)       # W135's band under the AP2112K: no served peak fits under it
    W = m.w135()
    assert abs(W["theta_need"] - 98.6) < 1e-9 and abs(W["ios"][1] - w_hi) < 5e-5


def t_the_judge_holds_and_its_mutations_refuse_or_fail():
    m, S = _texts()
    st, R, P, (lo, hi) = _base(m, S)
    v, rr = m.judge(st, R)
    assert v == "HOLDS", rr
    # a TYPICAL figure used as a limit is refused, whatever its value
    for k, val in (("ios_hi", (S["ios49"][0][1], "TYPICAL", "7.5")), ("vdo1a", S["vdo_new_typ"]), ("rja", (60.0, "TYPICAL", "x"))):
        bad = dict(st)
        bad[k] = val
        v, rr = m.judge(bad, R)
        assert v == "FAILS" and rr[0][0] == "J0" and not rr[0][1] and "REFUSED" in rr[0][2], (k, rr)
    # the old AP2112K at the new current fails its junction
    ap = dict(st)
    ap["rja"] = (P["theta_ldo"], "PRINTED", "DS39724 p.3")
    v, rr = m.judge(ap, R)
    assert v == "FAILS" and not dict((c, h) for c, h, _t in rr)["J2"], rr
    # the order code without M3: the legacy silicon's dropout and band fail T10-A3 at the limit
    leg = dict(st)
    leg.update(vdo1a=S["vdo_leg"], acc=S["acc_leg"])
    v, rr = m.judge(leg, R)
    assert v == "FAILS" and not dict((c, h) for c, h, _t in rr)["J4"], rr
    # one step over the requirement fails, the requirement itself holds
    over = dict(st)
    req = (R["tj"] - R["air"]) / (R["drop"] * hi)
    over["rja"] = (req + 0.05, "PRINTED", "a mutation")
    assert m.judge(over, R)[0] == "FAILS"
    at = dict(st)
    at["rja"] = (req - 0.01, "PRINTED", "a mutation")
    assert m.judge(at, R)[0] == "HOLDS"
    # a served peak over the limiter's minimum is limited: J1 fails
    R2 = dict(R)
    R2["served"] = dict(R["served"], extra=lo + 0.001)
    assert not dict((c, h) for c, h, _t in m.judge(st, R2)[1])["J1"]


def _compose(m, d, tag, extra):
    T, D = m.T, m.D
    seq = D.seq_of("b", "slot")
    at = seq.index(D.MINE["b"]) + 1
    pre = seq[:at] + [T.PRE["b"], T.SHDN, T.SET % "b", T.GUARD_B]
    p, res, ok = D.compose("b", pre + extra + seq[at:], d, tag)
    assert ok, [r for r in res if r[1] != "OK"]
    rc, net, _t = D.netlist("b", p, d, tag)
    assert rc == 0, net
    return p, net, m.CHK.read(open(net, "rb").read())


def t_the_draft_reads_drawn_and_the_old_state_and_every_mutation_fail():
    m, S = _texts()
    with tempfile.TemporaryDirectory(prefix="t_l4reg_") as d:
        _p, net, nl = _compose(m, d, "reg", [DRAFT])
        assert m.regstage_check(nl, S)[0] == "DRAWN", m.regstage_check(nl, S)[1][:3]
        _p0, _n0, nl0 = _compose(m, d, "guard", [])
        assert m.regstage_check(nl0, S)[0] == "FAIL"
        for i, sw in enumerate(([(("U40", "1"), ("U45", "1"))], [(("U40", "5"), ("U40", "3"))], [(("U45", "6"), ("U45", "1"))],
                                [(("R66", "1"), ("R602", "1"))])):
            q = m.D.mutate(net, d, "tm%d" % i, sw)
            assert m.regstage_check(m.CHK.read(open(q, "rb").read()), S)[0] == "FAIL", sw
        for i, (ref, val) in enumerate((("R621", "102k 1%"), ("U60", "AP2112K-3.3 LDO"), ("U50", "TPS73733DCQR 1 A LDO"), ("U55", "TPS2553 not latch-off"))):
            q = m.set_value(net, d, "tv%d" % i, ref, val)
            assert m.regstage_check(m.CHK.read(open(q, "rb").read()), S)[0] == "FAIL", ref


def t_the_draft_composes_with_canmb_in_either_order():
    m, S = _texts()
    canmb = need(os.path.join(REC, "inputs", "l9t5-apply_gen_sch_b_canmb-9367f3ab.py"), "W137's canmb as copied")
    with tempfile.TemporaryDirectory(prefix="t_l4reg_") as d:
        _a, _na, a = _compose(m, d, "cr", [canmb, DRAFT])
        _b, _nb, b = _compose(m, d, "rc", [DRAFT, canmb])
        assert m.regstage_check(a, S)[0] == "DRAWN" and m.regstage_check(b, S)[0] == "DRAWN"
        assert m.pins_by_ref(a) == m.pins_by_ref(b)


def t_the_draft_refuses_where_it_must_and_is_not_released():
    with tempfile.TemporaryDirectory(prefix="t_l4reg_") as d:
        bare = os.path.join(d, "gen_sch_b.py")
        shutil.copy(os.path.join(TOOLS, "gen_sch_b.py"), bare)
        r = subprocess.run([sys.executable, "-B", DRAFT, bare, "--write"], capture_output=True)
        assert r.returncode == 3 and b"iocguard" in r.stderr, r.stderr
        assert open(bare, encoding="utf-8").read() == open(os.path.join(TOOLS, "gen_sch_b.py"), encoding="utf-8").read()
    before = open(os.path.join(TOOLS, "gen_sch_b.py"), "rb").read()
    r = subprocess.run([sys.executable, "-B", DRAFT, os.path.join(TOOLS, "gen_sch_b.py"), "--write"], capture_output=True)
    assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, r.stderr
    assert open(os.path.join(TOOLS, "gen_sch_b.py"), "rb").read() == before
    src = open(DRAFT, encoding="utf-8").read()
    assert "None is APPLIED" in src and "NOT APPLIED" in src
    tree = ast.parse(src)
    names = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    assert {"ADDS", "REMOVES", "EDITS", "LIMITER", "REGULATOR"} <= names


def t_the_fetch_script_pins_exactly_the_held_sheets_declared():
    m = _M()
    src = open(need(FETCH, "the fetch script"), encoding="utf-8").read()
    listed = set(re.findall(r'"(v2/vendor/[^"]+\.pdf)"', src))
    held = {p for p in m.PDFTEXT if "/held/" in p}
    assert listed == held, (sorted(listed), sorted(held))
    for p in held:
        assert re.search(r'"%s", "https://www\.ti\.com/lit/ds/symlink/[a-z0-9]+\.pdf",\s*\n\s*"[0-9a-f]{64}"' % re.escape(p), src), p
    assert all(m.PT.FETCH.get(p) and "l4reg" in m.PT.FETCH[p] for p in held), "pdftext.FETCH lacks record l4reg for a held sheet"


def t_the_page_carries_the_figures_no_dash_and_no_claim():
    t = open(need(PAGE, "the record's page"), encoding="utf-8").read()
    o = open(need(OUT, "the record's output"), encoding="utf-8").read()
    for s in ("TPS73733DCQRM3", "TPS2553-1", "115.0 C", "95.7 C/W", "0.4702 to 0.5878 A", "SESSION W138-1", "authority_why", "ruled_by",
              "ruled_on", "reversed_by", "End condition", "L4REG-F1", "L4REG-F7"):
        assert s in t, s
    for s in ("115.0", "95.7", "0.4702 to 0.5878 A", "+0.1072 V"):
        assert s in o, s
    for p in (PAGE, SCRIPT, OUT, DRAFT, FETCH):
        x = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in x and chr(0x2013) not in x, "an em or en dash in %s" % os.path.basename(p)
    hits = [m.group(0) for m in CLAIM.finditer(t)]
    assert not hits, hits
