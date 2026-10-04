"""Layer 8 record l8p (MESHSAT-1357, 4 October 2026; v2/docs/records/l8p/): W4DP-F2's breaker drawn as release-guarded drafts for
board P (an LM5069-2 breaker and the make-last enable loop's inverters and RC hold), board E (the loop through J_SMB to the dock)
and board A (the loop's thermal guard RT1), from record l9stk section 15 (fnd/l9stk at 2c8b29fb).

The predicates: the committed .out is what the script prints; each draft checks, applies once on a scratch copy, refuses twice and
refuses the tree's own generator; each board composes in L4-E9's change-list order with this record's draft in its place, first
and last; the designators are this record's sets and disjoint from every other draft's; every value is found in record l9stk's
copied text and the copies are the bytes SOURCES.txt pins; the netlist check reads NOT DRAWN on the committed netlists, DRAWN on
the netlists regenerated from the patched generators (the loop across the three boards included) and FAIL on a mutated one; the
page carries no em or en dash and no claim word, and names the interface rows owed. No KiCad: generator text, the generators'
own part tables and netlist text, on scratch copies; the tree is never written."""
import hashlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l8p")
SCRIPT = os.path.join(REC, "l8p_drafts.py")
OUT = os.path.join(REC, "l8p_drafts.out")
PAGE = os.path.join(REC, "L8P-BREAKER.md")
GEN = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "pea"}
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
_C = {}


def _mod(name, fname):
    if name not in _C:
        p = need(os.path.join(REC, fname), "a file of the l8p record")
        if REC not in sys.path:
            sys.path.insert(0, REC)
        sp = importlib.util.spec_from_file_location(name, p)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _C[name] = m
    return _C[name]


def _M():
    return _mod("l8p_drafts_under_test", "l8p_drafts.py")


def _CHK():
    return _mod("check_l8p_netlist_under_test", "check_l8p_netlist.py")


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _run(args):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True)


def _need_inputs():
    m = _M()
    for b in "pea":
        need(GEN[b], "board %s's generator" % b.upper()); need(m.NET[b], "board %s's committed netlist" % b.upper())
        for r, n in m.ORDER[b]:
            need(m.draft(r, n, b), "a board %s draft L4-E9's order composes" % b.upper())
    return m


def t_the_committed_output_is_what_the_script_prints():
    _need_inputs()
    before = {b: _sha(GEN[b]) for b in "pea"}
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l8p_drafts.out is not what l8p_drafts.py prints; regenerate it with _bin/regen_out.py"
    assert all(_sha(GEN[b]) == s for b, s in before.items()), "the script wrote into the tree"
    t = r.stdout.decode()
    for s in ("record l9stk's copies equal the sha256 SOURCES.txt pins: yes", "the tree's generators are unchanged: yes",
              "board P, this record's against every other draft's: DISJOINT", "board E, this record's against every other draft's: DISJOINT",
              "board A, this record's against every other draft's: DISJOINT", "record l8p's breaker and enable loop on the netlists: NOT DRAWN",
              "       LOOP DRAWN", "all KiCad's names for open pins: yes; footprints differing: 0", "(R248, C247)",
              "L8P-F01 board E", "L8P-F02 board A", "L8P-F03 board E"):
        assert s in t, s
    assert t.count("record l8p's breaker and enable loop on the netlists: DRAWN") == 2, "the alone and the composed readings"
    assert t.count("record l8p's breaker and enable loop on the netlists: FAIL") == 2, "the two mutations"
    assert "REFUSED" not in t.split("4. COMPOSITION")[1].split("5. DESIGNATORS")[0], "a composition step refused"


def t_each_draft_checks_applies_once_refuses_twice_and_refuses_the_tree():
    m = _M()
    before = {b: _sha(GEN[b]) for b in "pea"}
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            s = m.MINE[b]
            tgt = os.path.join(d, os.path.basename(s) + ".gen.py"); shutil.copy(GEN[b], tgt); pre = _sha(tgt)
            r = _run([s, tgt]); assert r.returncode == 0 and b"CHECK OK" in r.stdout, r.stderr.decode()[-300:]
            assert _sha(tgt) == pre, "--check wrote"
            r = _run([s, tgt, "--write"]); assert r.returncode == 0 and b"WRITTEN" in r.stdout, r.stderr.decode()[-300:]
            assert _run([s, tgt, "--write"]).returncode == 3, "a second application was not refused"
            r = _run([s, GEN[b], "--write"]); assert r.returncode == 3 and b"NOT RELEASED" in r.stderr, "the tree's own generator was not refused"
            compile(open(tgt, encoding="utf-8").read(), tgt, "exec")
    assert not os.path.exists(os.path.join(REC, "RELEASE.md")), "a release record exists: the drafts are no longer guarded"
    assert all(_sha(GEN[b]) == s for b, s in before.items()), "a draft wrote into the tree"


def t_each_board_composes_in_l4e9s_order_in_its_place_first_and_last():
    m = _need_inputs()
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            seq = [m.draft(r, n, b) for r, n in m.ORDER[b]]
            for tag, order in (("fwd", seq[:m.SLOT[b]] + [m.MINE[b]] + seq[m.SLOT[b]:]), ("first", [m.MINE[b]] + seq), ("last", seq + [m.MINE[b]])):
                p, res = m.compose(b, order, d, tag)
                assert len(res) == len(order) and all(v.startswith("OK") for _s, v in res), (b, tag, res)
                compile(open(p, encoding="utf-8").read(), p, "exec")


def t_the_designators_are_this_records_sets_and_disjoint():
    m = _need_inputs()
    want = {"p": {"U101", "Q101", "Q102", "Q103", "Q104", "D101"} | {"R%d" % k for k in range(101, 110)} | {"C%d" % k for k in range(101, 106)}
            | {"TP%d" % k for k in range(101, 105)}, "e": set(), "a": {"RT1"}}
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            seq = [m.draft(r, n, b) for r, n in m.ORDER[b]]
            fwd = seq[:m.SLOT[b]] + [m.MINE[b]] + seq[m.SLOT[b]:]
            p = os.path.join(d, "g_%s.py" % b); shutil.copy(GEN[b], p)
            before = open(p, encoding="utf-8").read(); adds = {}
            for s in fwd:
                assert m.run(s, p, b)[0] == 0, s
                after = open(p, encoding="utf-8").read(); adds[s] = m.added(before, after, s); before = after
            mine = adds[m.MINE[b]]
            assert mine == want[b], (b, sorted(mine ^ want[b]))
            for s, a in adds.items():
                assert s == m.MINE[b] or not (a & mine), "%s meets this record's %s" % (s, sorted(a & mine))
            assert not m.duplicates(before), (b, m.duplicates(before))


def t_every_value_is_the_records_and_the_copies_are_pinned():
    m = _M(); chk = _CHK()
    for f, full in m.SOURCES_SHA.items():
        assert _sha(os.path.join(REC, f)) == full, f
        assert full in open(os.path.join(REC, "inputs", "SOURCES.txt"), encoding="utf-8").read(), "SOURCES.txt does not pin %s" % f
    texts = {k: open(os.path.join(REC, v), encoding="utf-8").read() for k, v in m.INPUT_FILES.items()}
    drafts = {b: open(m.MINE[b], encoding="utf-8").read() for b in "pea"}
    for b, ref, pre, src, pat, key in chk.VALUES:
        assert re.search(pat, texts[key]), "l9stk no longer reads %s's value (%s)" % (ref, src)
        call = re.search(r'(?:ic|r|c|part|pfet5|nfet)\(\\?"%s\\?", ' % re.escape(ref), drafts[b])
        assert call, "%s is not drawn in the board %s draft" % (ref, b.upper())
    assert "R_G = 1e6" in texts["constants"] and "R_E1, R_E2 = 10e3, 22e3" in texts["constants"]


def t_the_netlist_check_reads_not_drawn_drawn_and_fail():
    m = _need_inputs(); chk = _CHK()
    kit, v = chk.run(m.NET, ROOT, io.StringIO())
    assert kit == "NOT DRAWN" and set(v.values()) == {"NOT DRAWN"}, v
    with tempfile.TemporaryDirectory() as d:
        paths = {}
        for b in "pea":
            t = os.path.join(d, "gen_sch_%s.py" % b); shutil.copy(GEN[b], t)
            assert m.run(m.MINE[b], t, b)[0] == 0
            rc, path, table = m.netlist_text(b, t, d, "t")
            assert rc == 0 and table["intent_written"] and not table["unplaced"], (b, path)
            paths[b] = path
        buf = io.StringIO(); kit, v = chk.run(paths, ROOT, buf)
        assert kit == "DRAWN" and v.get("loop") == "DRAWN", buf.getvalue()
        bad = m.mutate(paths["e"], d, "mut_e", [(("J_BLK", "4"), ("J_BLK", "5"))])
        kit, v = chk.run({"e": bad}, ROOT, io.StringIO())
        assert kit == "FAIL", "the ground between J_BLK's loop pins moved and the check did not fail"
        raw = open(paths["p"], encoding="utf-8").read().replace('(node (ref "D101") (pin "1"))', '(node (ref "D101") (pin "9"))')
        open(os.path.join(d, "mut_p.net"), "w", encoding="utf-8").write(raw)
        kit, v = chk.run({"p": os.path.join(d, "mut_p.net")}, ROOT, io.StringIO())
        assert kit == "FAIL", "the input clamp left BRK_VIN and the check did not fail"


def t_the_unpatched_generators_reproduce_the_committed_netlists():
    m = _need_inputs(); chk = _CHK()
    with tempfile.TemporaryDirectory() as d:
        for b in "pea":
            rc, path, _t = m.netlist_text(b, GEN[b], d, "base")
            assert rc == 0, path
            a, k = chk.read_netlist(open(path, "rb").read()), chk.read_netlist(open(m.NET[b], "rb").read())
            pa, pk = m.pins_of(a), m.pins_of(k)
            diff = [x for x in set(pa) | set(pk) if pa.get(x) != pk.get(x)]
            assert all(pa.get(x) is None and str(pk.get(x)).startswith("unconnected-") for x in diff), (b, sorted(diff)[:5])
            assert all(a["comps"][r]["footprint"] == k["comps"][r]["footprint"] for r in a["comps"]), b


def t_the_page_is_clean_and_names_the_rows_owed():
    page = open(need(PAGE, "the l8p record page"), encoding="utf-8").read()
    for p in [PAGE, os.path.join(REC, "README.md")] + [os.path.join(REC, f) for f in os.listdir(REC) if f.endswith(".py")]:
        t = open(p, encoding="utf-8").read()
        assert "—" not in t and "–" not in t, "an em or en dash in %s" % os.path.basename(p)
    assert not CLAIM.search(page), CLAIM.search(page).group(0)
    for s in ("**Status: DRAFTED, not applied.**", "**The fifth to seventh J_SMB contacts:**", "**The dock enable contacts:**",
              "**PACK_P live only while docked:**", "**The make-last contact's 1 mm (C1):**", "**The mating order C1, both ways:**",
              "**The third battery FET's designator**", "**IF-1:**", "**IF-2:**", "L8P-F01", "L8P-F02", "L8P-F03"):
        assert s in page, s
    for ref in ("U101", "R101", "R102", "Q101, Q102", "R103", "C101", "C102", "D101", "R104", "C103", "R106", "R107", "Q103", "Q104",
                "R105", "R108, R109", "RT1 (board A)"):
        assert "| %s" % ref in page, "the value table omits %s" % ref
