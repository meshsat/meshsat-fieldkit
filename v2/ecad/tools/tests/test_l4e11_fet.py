"""Record l4e11 round FET (Layer 4 AI-scope register tasks L4A-70 and L4A-71; MESHSAT-1357, 7 October 2026; v2/docs/records/l4e11/
l4e11_fet.py, L4E11-ROUND-FET.md, fallback/apply_gen_sch_a_fetpair.py, fallback/check_fetpair_netlist.py,
fallback/apply_check_dd7_fetpair.py).

The predicates: the committed .out is what the script prints; the screen reproduces the records' own figures (the 21.136 mOhm
allowance, the three's 40.78 K/W worst-split bar, the pair's 20.39 K/W, round 15c's and 16a's allowances of the earlier parts); the
worst-split factor F0 = n^2 / (4 (n - 1)) is the largest of a brute-force search over the split and the coupling; no set of the 18
parts read meets TI's 5 nF on printed maxima, the 40.78 K/W bar and the held 23.93 A together, and every part with a printed Ciss
maximum sits above the class bound; a typical used as a limit is refused by the screen (a mutated table that relabels the
BUK6Y10-30P's typical Ciss as a maximum flips the pair to a pass, which this test's predicate catches) and by the fallback draft's
text check (a mutated comment that states the pair's 4.72 nF as a maximum fails); the fallback draft refuses a board without the
charger draft, a second application and the tree's own generator, composes after board A's drafts in L4-E9's order (record l8p's PTC,
this record's DD-7, record l8p's thermal guard and its fail-safe delta included), the composed generator runs to its end, the pair
reads DRAWN in check_fetpair_netlist.py and DD-7's check reads DRAWN on the pair, and five mutations fail (the three left drawn, a
third gate on BATDRV, a FET reversed, a gate off BATDRV, CH_BATQ's intent still naming Q42); the page carries the output's numbers
and the SESSION decision with its five fields; no em or en dash and no claim word in the round's files.
Round 12 of record l8p (W149, 7 October 2026; the focused check L4A-69's F9): the fallback's composition reads board A's order
from L4-E9's change list (section 3 of L4-POWER-ARCHITECTURE.md), every board A row whose draft it names, then Layer 6's table."""
import copy
import hashlib
import importlib.util
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e11")
SCRIPT = os.path.join(REC, "l4e11_fet.py")
OUT = os.path.join(REC, "l4e11_fet.out")
PAGE = os.path.join(REC, "L4E11-ROUND-FET.md")
PAIR = os.path.join(REC, "fallback", "apply_gen_sch_a_fetpair.py")
PCHK = os.path.join(REC, "fallback", "check_fetpair_netlist.py")
DD7C = os.path.join(REC, "fallback", "apply_check_dd7_fetpair.py")
DD7_CHECK = os.path.join(REC, "check_dd7_netlist.py")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
GEN_NET = os.path.join(ROOT, "v2", "docs", "records", "l8p", "gen_netlist.py")
NET_A = os.path.join(ROOT, "v2", "ecad", "pcb-a-power-a23", "out", "pcb-a-power.net")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _M():
    if "M" not in _C:
        need(SCRIPT, "record l4e11's round FET")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l4e11_fet_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for _k, (rel, _s, _kind, _t) in m.DOCS.items():
            need(os.path.join(ROOT, rel), "a held maker's sheet of the round (fetch_held_back.py, fetch_held_back_fet.py)")
        _C["M"] = m
    return _C["M"]


def _R():
    if "R" not in _C:
        m = _M()
        try:
            _C["R"] = m.compute()
        except m.Refused as e:
            raise AssertionError("l4e11_fet.py refused: %s" % e)
    return _C["R"]


def _run(args):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True)


def t_the_committed_output_is_what_the_script_prints():
    m = _M()
    _R()
    assert m.report(_R()) == open(OUT, encoding="utf-8").read(), "l4e11_fet.out is not what l4e11_fet.py prints (regen_out.py)"


def t_the_screen_reproduces_the_records_figures():
    m, R = _M(), _R()
    E = R["E"]
    assert abs(E["i"] - 23.93) < 1e-9 and abs(E["held_brk"] - 23.93) < 1e-9 and abs(E["t0"] - 76.25) < 1e-9 and abs(E["band"] - 9.16) < 1e-9
    assert abs(E["bar"] - 40.78) < 1e-9 and abs(E["bar_pair"] - 20.39) < 1e-9 and abs(E["ra"] - 21.136e-3) < 1e-12
    assert abs(m.bar(E, 3, E["ra"], 150.0) - E["bar"]) <= 0.001 * E["bar"] + 0.03
    assert abs(m.bar(E, 2, E["ra"], 150.0) - E["bar_pair"]) <= 0.001 * E["bar_pair"] + 0.02
    want = {"BUK6Y10-30P": 21.136, "PXP9R1-30QL": 15.619, "AONS21357": 12.384, "SQJ403EP": 19.166}   # L4-E11 15c, 16a and 21b
    got = {P["part"]: S["a"]["ra"] * 1e3 for P, S in R["res"] if S["a"]["ra"] is not None}
    for k, v in want.items():
        assert abs(got[k] - v) < 0.0006, (k, got[k], v)
    # the three hold E-1's current at their own bar (the bar is defined at it)
    assert abs(m.i_hold(E, 3, E["ra"], 150.0, m.bar(E, 3, E["ra"], 150.0)) - E["i"]) < 1e-9


def t_the_worst_split_factor_is_the_largest_of_a_search_over_split_and_coupling():
    m = _M()
    for n in (2, 3, 4, 6):
        best = 1.0
        for k in range(0, 41):
            mm = 0.5 * k / 40.0
            for j in range(0, 2001):
                x = 1.0 + 9.0 * j / 2000.0
                f = (x + mm * (n - 1)) * n * n / ((x + n - 1) ** 2 * (1 + mm * (n - 1)))
                best = max(best, f)
        assert best <= m.f0(n) + 1e-9 and best >= m.f0(n) - 1e-4, (n, best, m.f0(n))


def t_no_set_meets_the_three_limits_and_the_class_bound_holds():
    m, R = _M(), _R()
    E = R["E"]
    assert len(R["res"]) == 18 and not any(S["meets_all"] for _P, S in R["res"])
    for P, S in R["res"]:
        assert S["vds_ok"] and S["vgs_ok"], P["part"]
        if P["ciss"][1] is None:
            assert S["nc"] is None, "%s: a count under 5 nF without a printed Ciss maximum" % P["part"]
        else:
            assert S["nc"] * P["ciss"][1] < m.TI_CISS and (S["nc"] + 1) * P["ciss"][1] >= m.TI_CISS
            if P["ciss"][1] < m.TI_CISS:
                assert S["fom"] > S["fom_lim"], "%s can form a set and sits under the class bound" % P["part"]
            else:
                assert S["nc"] == 0 and S["bar"] is None, P["part"]
        if S["n"]:
            assert S["bar"] < E["bar"], P["part"]
            # an independent recomputation of the bar from the case
            B = S["a"]["tl"] - E["t0"] - E["band"] - E["r17c"] * E["i"] ** 2 * E["r17"]
            even = B / ((E["i"] / S["n"]) ** 2 * S["R_used"])
            assert abs(S["bar"] - even / m.f0(S["n"])) < 1e-9
        if S["a"]["ra"] is None:
            assert P["maker"] == "Infineon" and not S["T"]
    # the class bound at any count: the joint condition's limit rises with n to the value printed
    for tl in (150.0, 125.0):
        lim = m.class_limit(E, tl)
        B = tl - E["t0"] - E["band"] - E["r17c"] * E["i"] ** 2 * E["r17"]
        for n in (2, 3, 5, 12, 1000):
            assert m.TI_CISS * 1e9 * 4 * (n - 1) * B / (E["bar"] * E["i"] ** 2 * n) * 1e3 < lim
    out = open(OUT, encoding="utf-8").read()
    assert "sets meeting G, T and H together: NONE among the 18 parts read" in out
    assert "STAYS SELECTED and CONDITIONAL on E-05" in out


def t_a_typical_used_as_a_limit_is_refused():
    m, R = _M(), _R()
    E = R["E"]
    buk = m.PARTS[0]
    try:
        m.limit(buk["ciss"], "BUK6Y10-30P Ciss")
        raise AssertionError("the guard read a typical as a limit")
    except m.GuardError:
        pass
    S = m.screen(E, buk)
    assert S["nc"] is None and not S["G"], "the BUK6Y10-30P's typical Ciss gave a count under 5 nF"
    # the mutation: the typical relabelled as a maximum makes the pair pass G; this test's predicate above would then fail
    mut = copy.deepcopy(buk)
    mut["ciss"] = (buk["ciss"][0], buk["ciss"][0], buk["ciss"][2])
    Sm = m.screen(E, mut)
    assert Sm["nc"] == 2 and Sm["G"], "the mutation did not change the reading, so the predicate would not catch it"
    # the fallback draft's text: the pair's 4.72 nF is stated as a typical, never as a limit
    pair = _pair_mod()
    assert _no_typical_as_limit(pair._NEW_BLOCK)
    bad = pair._NEW_BLOCK.replace("(4.72 nF typical for the pair at\n# -15 V", "(4.72 nF at most for the pair at\n# -15 V")
    assert bad != pair._NEW_BLOCK and not _no_typical_as_limit(bad), "the text check passed a typical stated as a limit"


def _no_typical_as_limit(text):
    """Every clause of the draft's comment that states the pair's 4.72 nF calls it a typical and none states it as a maximum."""
    flat = re.sub(r"\s*\n#\s*", " ", text)
    s = [x for x in re.split(r";|\. ", flat) if "4.72" in x]
    return bool(s) and all("typical" in x and not re.search(r"4\.72 nF (at most|maximum)|(at most|maximum) 4\.72", x) for x in s)


def _pair_mod():
    sp = importlib.util.spec_from_file_location("fetpair_under_test", PAIR)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


ARCH = os.path.join(ROOT, "v2", "docs", "records", "l4e9", "L4-POWER-ARCHITECTURE.md")


def _order_a():
    """Board A's drafts in L4-E9's change-list order, read from its section 3 table (record l8p round 12, the focused check L4A-69's F9:
    the composition is taken from the list, never typed by hand), each found in the one record folder that holds it; Layer 6's
    order-independent table draft (l6r2's lcsc) after the list, as record l8p's l8p_drafts.py composes it."""
    need(ARCH, "L4-E9's change list")
    page = open(ARCH, encoding="utf-8").read()
    sec = page.split("## 3. The circuit-change list")[1].split("\n## 4. ")[0]
    names = []
    for line in sec.splitlines():
        if not re.match(r"\| \d+ \| ", line):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if cells[3].startswith("board A, gen_sch_a.py"):
            names += [n for n in re.findall(r"apply_gen_sch_a_(\w+)\.py", cells[4]) if n not in names]
    rec = os.path.join(ROOT, "v2", "docs", "records")
    out = []
    for n in names + ["lcsc"]:
        hits = [r_ for r_ in sorted(os.listdir(rec)) if os.path.isfile(os.path.join(rec, r_, "apply_gen_sch_a_%s.py" % n))]
        assert len(hits) == 1, "board A's draft %s is held by %s, not by one record" % (n, hits)
        out.append((hits[0], n))
    return out


def _compose(d):
    """Board A in L4-E9's change-list order (every board A row whose draft the list names), then Layer 6's table."""
    g = os.path.join(d, "gen_sch_a.py")
    shutil.copy(GEN_A, g)
    rec = os.path.join(ROOT, "v2", "docs", "records")
    order = _order_a()
    assert [n for _r, n in order][:3] == ["r12", "guard", "charger"] and ("d8dec31", "mainpb") in order and len(order) >= 20, order
    for r_, name in order:
        s = os.path.join(rec, r_, "apply_gen_sch_a_%s.py" % name)
        r = _run([s, g, NET_A] if r_ == "d8dec31" else [s, g, "--write"])
        assert r.returncode == 0, "%s/%s refused: %s" % (r_, name, r.stderr.decode()[-300:])
    return g


def _net(g, d, tag):
    out = os.path.join(d, "a-%s.net" % tag)
    r = _run([GEN_NET, g, out, "pcb-a-power"])
    return r.returncode, out, (r.stdout + r.stderr).decode("utf-8", "replace")


def _dd7_on(net, fets):
    sp = importlib.util.spec_from_file_location("dd7_under_test", DD7_CHECK)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    m.BATFETS = fets
    return m.judge(open(net, "rb").read())[0]


def t_the_fallback_composes_runs_reads_the_pair_and_its_mutations_fail():
    need(GEN_NET, "record l8p's gen_netlist.py")
    with tempfile.TemporaryDirectory() as d:
        bare = os.path.join(d, "bare.py")
        shutil.copy(GEN_A, bare)
        r = _run([PAIR, bare, "--write"])
        assert r.returncode == 3 and b"apply apply_gen_sch_a_charger.py first" in r.stderr
        r = _run([PAIR, GEN_A, "--write"])
        assert r.returncode == 3 and b"NOT RELEASED" in r.stderr
        g = _compose(d)
        three = open(g, encoding="utf-8").read()
        rc, net3, log3 = _net(g, d, "three")
        assert rc == 0, log3[-300:]
        assert _run([PCHK, net3, "--want", "three"]).returncode == 0, "the composed three do not read DRAWN as three"
        r = _run([PCHK, net3])
        assert r.returncode == 4 and b"FAIL" in r.stdout, "mutation 'the three left drawn' did not fail the pair's check"
        assert _run([PAIR, g, "--write"]).returncode == 0
        assert _run([PAIR, g, "--write"]).returncode == 3, "a second application was not refused"
        text = open(g, encoding="utf-8").read()
        assert "Q42" not in text and "Q42" in three
        rc, net, log = _net(g, d, "pair")
        assert rc == 0 and "intent written" in log, log[-300:]
        r = _run([PCHK, net])
        assert r.returncode == 0 and b"DRAWN" in r.stdout, r.stdout.decode()[-400:]
        n3 = int(re.search(r"(\d+) parts", log3).group(1))
        n2 = int(re.search(r"(\d+) parts", log).group(1))
        assert n2 == n3 - 1, "the pair's composition is not one part fewer than the three's (%d, %d)" % (n2, n3)
        assert _dd7_on(net, ("Q39", "Q40")) == "DRAWN" and _dd7_on(net, ("Q39", "Q40", "Q42")) == "FAIL"
        q40 = 'for _qb in ("Q39", "Q40"): nfet(_qb, '
        nf = 'nfet(_qb, "BUK6Y10-30PX 30 V P-FET (the BQ25730\'s battery FET, one of two in parallel: S on VSYS, D toward RSR)", "CH_BATDRV", "CH_BATQ", "VBAT", fp="LFPAK56", lcsc="C3278350")'
        assert text.count(q40) == 1 and text.count(nf) == 1
        muts = [
            ("a third gate on BATDRV (Q99, another P-FET on CH_BATDRV)", nf,
             nf + '\npart("Q99", "Transistor_FET", "AO3401A", "AO3401A P-FET", "SOT23", {"1": "CH_BATDRV", "2": "VBAT", "3": "CH_SRP_F"}, "C15127")', "check"),
            ("Q40 reversed (its body diode from VSYS to the pack)", q40,
             'nfet("Q40", "BUK6Y10-30PX 30 V P-FET (the BQ25730\'s battery FET, reversed)", "CH_BATDRV", "VBAT", "CH_BATQ", fp="LFPAK56", lcsc="C3278350")\nfor _qb in ("Q39",): nfet(_qb, ', "check"),
            ("Q40's gate off BATDRV (on VBAT)", q40,
             'nfet("Q40", "BUK6Y10-30PX 30 V P-FET (the BQ25730\'s battery FET, gate tied)", "VBAT", "CH_BATQ", "VBAT", fp="LFPAK56", lcsc="C3278350")\nfor _qb in ("Q39",): nfet(_qb, ', "check"),
            ("CH_BATQ's intent still naming Q42", 'loads={"Q39": 5.0, "Q40": 5.0},', 'loads={"Q39": 3.34, "Q40": 3.33, "Q42": 3.33},', "generator"),
        ]
        for k, (why, old, rep, where) in enumerate(muts):
            assert text.count(old) == 1, why
            gm = os.path.join(d, "gen_m%d.py" % k)
            open(gm, "w", encoding="utf-8").write(text.replace(old, rep))
            rc, netm, log = _net(gm, d, "m%d" % k)
            if where == "generator":
                assert rc != 0 and "names load Q42" in log, "%s: the generator did not refuse" % why
                continue
            assert rc == 0, "%s: the generator refused: %s" % (why, log[-300:])
            r = _run([PCHK, netm])
            assert r.returncode == 4 and b"FAIL" in r.stdout, "%s: the check did not fail: %s" % (why, r.stdout.decode()[-300:])
        # the DD-7 companion: on a copy, applied once, refused twice, refused on the tree's own check; DD-7 then reads the pair
        cp = os.path.join(d, "check_dd7_copy.py")
        shutil.copy(DD7_CHECK, cp)
        assert _run([DD7C, cp, "--write"]).returncode == 0 and _run([DD7C, cp, "--write"]).returncode == 3
        assert _run([DD7C, DD7_CHECK, "--write"]).returncode == 3
        r = _run([cp, net])
        assert r.returncode == 0 and b"DRAWN" in r.stdout, r.stdout.decode()[-300:]


def _decision(page):
    m = re.search(r"```yaml\n(.*?)```", page, re.S)
    assert m, "the page carries no decision block"
    return yaml.safe_load(m.group(1))


def t_the_page_carries_the_outputs_numbers_and_the_session_decision():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    first = page.splitlines()[0]
    assert first.startswith("**ROUND FET") and "DONE" in first and "NEXT" in first
    for s in ("40.78 K/W", "20.39 K/W", "23.93 A", "52.87", "31.45", "7.85 K/W", "7.94 K/W", "14.25 K/W", "16.93 A", "8.46 A", "E-05", "Q-TI-17 (e)"):
        assert s in page, s
        assert s.split(" ")[0] in out, s
    docs = _decision(page)
    assert isinstance(docs, list) and len(docs) == 2
    for dct in docs:
        for k in ("id", "title", "authority", "authority_why", "ruled_by", "ruled_on", "reversed_by", "outcome"):
            assert k in dct and str(dct[k]).strip(), (dct.get("id"), k)
        assert dct["authority"] == "SESSION"
    ids = [x["id"] for x in docs]
    assert ids == ["L4E11-FET-D1", "L4E11-FET-D2"]
    assert "M-A first" in docs[1]["outcome"] and "M-B second" in docs[1]["outcome"]
    assert "end condition" in docs[1]["outcome"].lower()


CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b", re.I)


def t_no_dashes_and_no_claim_words():
    for p in (SCRIPT, OUT, PAGE, PAIR, PCHK, DD7C, os.path.join(REC, "fetch_held_back_fet.py"), os.path.abspath(__file__)):
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, p
        if p in (PAGE, OUT):
            for line in t.splitlines():
                for mm in CLAIM.finditer(line):
                    assert re.search(r"(not|never|no|nothing)\b[^.]*" + mm.group(0), line, re.I) or "qualification" in line.lower(), (p, line[:120])
