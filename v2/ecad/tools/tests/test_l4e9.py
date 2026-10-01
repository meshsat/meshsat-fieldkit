"""Layer 4 task L4-E9 (MESHSAT-1357, 1 October 2026; v2/docs/records/l4e9/): the connected power architecture and Layer 4's
closure gate for it, held as predicates on properties, not on the figures' values.

The predicates: the committed l4e9_power_path.out is what the script prints, and every input it reads is pinned; every
interface row gives both sides' voltage and both sides' current, names the record that settles it and carries checks with a
class and a source; every row that waits on L4-E7R says so; the reverse-polarity finding is the raised ceiling plus the
reversed input, over the drawn FET and under the chosen one and the controller's limits; F1's specification is the OVLO
maximum and the kit cable's cold resistance; every downstream item has one named owner and an acceptance, and every draft
apply script of L4-E4 to L4-E8 is in the register, with L4-E5's two undrafted changes marked MISSING DRAFT; the gate covers
the five criteria, the page's gate table and the output agree, and nothing marked PASS rests on an ASSUMPTION, CONDITIONAL or
PENDING row (a gate mutated to break the rule is refused); the page's interface table agrees with the output; every Layer 5
handover entry names rows the reconciliation prints; the Q1 draft checks without writing, applies once to a copy, refuses a
second application and the tree's generator, and composes with d8dec31's input capacitor and L4-E7's three drafts in either
order; no em or en dash and no claim word in the record. Nothing here writes into the tree: drafts run on temporary copies.
"""
import ast
import copy
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e9")
PAGE = os.path.join(REC, "L4-POWER-ARCHITECTURE.md")
REG = os.path.join(REC, "DOWNSTREAM-REGISTER.md")
HAND = os.path.join(REC, "LAYER5-HANDOVER.md")
SCRIPT = os.path.join(REC, "l4e9_power_path.py")
OUT = os.path.join(REC, "l4e9_power_path.out")
Q1 = os.path.join(REC, "apply_gen_sch_e_q1.py")
GEN_E = os.path.join(ROOT, "v2", "ecad", "tools", "gen_sch_e.py")
NET_E = os.path.join(ROOT, "v2", "ecad", "pcb-e1-dock-e7", "out", "pcb-e1-dock.net")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _M():
    if "M" not in _C:
        need(SCRIPT, "the L4-E9 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the script finds the tree by git)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l4e9_power_path_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            text, F, D, R, st = m.main()
        except SystemExit as e:
            raise AssertionError("l4e9_power_path.py refused (exit %s)" % e.code)
        _C.update(M=m, text=text, F=F, D=D, R=R, st=st)
    return _C["M"]


def _md_rows(path, header):
    m = _M()
    return m.md_table(open(path, encoding="utf-8").read(), header)


def t_output_reproduced_byte_for_byte():
    _M()
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l4e9_power_path.out is not what the script prints"


def t_every_input_is_pinned():
    m = _M()
    for key, (rel, sha) in m.PINS.items():
        assert sha and re.fullmatch(r"[0-9a-f]{64}", sha), "%s (%s) is not pinned by sha256" % (key, rel)


def t_every_interface_row_has_both_sides_and_a_settling_record():
    _M()
    R = _C["R"]
    assert len(R) >= 12, "fewer interface rows than the blocks' interfaces"
    ids = [r["id"] for r in R]
    assert len(ids) == len(set(ids)), "row ids repeat"
    for r in R:
        for k in ("v", "i"):
            parts = r[k].split(" | ")
            assert len(parts) == 2 and all(p.strip() for p in parts), "%s's %s does not give both sides" % (r["id"], k)
        for k in ("a", "b", "loss", "therm", "prot_a", "prot_b", "settled"):
            assert r[k].strip(), "%s has no %s" % (r["id"], k)
        assert r["checks"], "%s carries no check" % r["id"]
        for c in r["checks"]:
            assert c.cls in _C["M"].ORDER and c.src.strip(), "%s: a check without a class or a source" % r["id"]


def t_pending_rows_wait_on_l4e7r():
    _M()
    for r in _C["R"]:
        if _C["st"][r["id"]][1] == "PENDING":
            assert any(c.cls == "PENDING" and "L4-E7R" in c.src for c in r["checks"]), "%s is PENDING without naming L4-E7R" % r["id"]
    assert "L4-E7R" in _C["text"].split("1. THE MAKERS")[0], "the inputs section does not name what is not read"


def t_the_reverse_finding_is_the_ceiling_plus_the_reversed_input():
    _M()
    F, D = _C["F"], _C["D"]
    assert abs(D["q1_rev"] - (F["trk_ceiling"][2] + F["vin_raw_e"]["v_work"])) < 1e-9
    assert abs(D["q1_rev_drawn"] - (F["trk_drawn"][2] + F["vin_raw_e"]["v_work"])) < 1e-9
    assert D["q1_rev_drawn"] <= F["bsc039_vds"] < D["q1_rev"], "the drawn ceiling must pass and the raised one fail on the drawn Q1"
    assert D["q1_rev"] <= F["csd19532_vds"] and D["q1_rev"] <= F["ld_ac_rec"] <= F["ld_ca_abs"], "the chosen Q1 and U3 must hold it"


def t_f1_specification_follows_the_ovlo_and_the_cold_cable():
    m = _M()
    F, D = _C["F"], _C["D"]
    assert D["f1_v"] == F["ovlo"][2] and F["f297_v"] < D["f1_v"], "the held MINI's rating against the OVLO maximum"
    r20 = 2 * F["cable_m"] * m.CU_RHO_20C / F["cable_mm2"] + 2 * F["lead_mm"] / 1000.0 * m.CU_RHO_20C / m.AWG18_MM2
    assert abs(D["f1_ipf"] - F["ovlo"][2] / (r20 * (1 + m.CU_ALPHA * (m.T_COLD - 20.0)))) < 1e-6
    assert D["f1_ipf"] > F["ovlo"][2] / r20, "the cold copper must give the larger current"


def t_every_downstream_item_has_an_owner_and_an_acceptance():
    m = _M()
    rows = _md_rows(REG, "| ID | Kind |")
    assert len(rows) >= 40
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids)), "register ids repeat"
    for r in rows:
        assert len(r) == 8, "%s does not have eight columns" % r[0]
        rid, kind, item, frm, owner, acc, state, order = r
        assert re.fullmatch(r"R-\d\d", rid), rid
        assert kind in ("IMPLEMENTATION", "LAYOUT", "TEST", "EVIDENCE", "RELEASE"), "%s kind %s" % (rid, kind)
        assert owner in m.OWNERS, "%s's owner %r is not a named layer and role" % (rid, owner)
        assert acc.strip() and item.strip() and frm.strip() and order.strip(), "%s lacks an item, a source, an acceptance or an order" % rid
        assert state in ("DRAFTED", "MISSING DRAFT", "PENDING", "OWED"), "%s state %s" % (rid, state)
    kinds = {r[1] for r in rows}
    assert {"IMPLEMENTATION", "LAYOUT", "TEST"} <= kinds


def t_the_page_counts_are_the_registers():
    _M()
    rows = _md_rows(REG, "| ID | Kind |")
    page = open(PAGE, encoding="utf-8").read()
    assert "holds %d items" % len(rows) in page and "%d items, each with one owner" % len(rows) in page, "the page's register count"
    m = re.search(r"register: (\d+) items", _C["text"])
    assert m and int(m.group(1)) == len(rows), "the output's register count"


def _drafts():
    names = set()
    for rec in ("l4e4", "l4e5", "l4e6", "l4e7"):
        d = os.path.join(ROOT, "v2", "docs", "records", rec)
        names |= {f for f in os.listdir(d) if f.startswith("apply_") and f.endswith(".py")}
    d8 = os.path.join(ROOT, "v2", "docs", "records", "l4e8")
    if os.path.isdir(d8):
        names |= {f for f in os.listdir(d8) if f.startswith("apply_") and f.endswith(".py")}
    else:
        r = subprocess.run(["git", "-C", ROOT, "ls-tree", "--name-only", _M().L4E8_COMMIT, "v2/docs/records/l4e8/"], capture_output=True)
        if r.returncode != 0:
            raise Skip("L4-E8's commit is not in this checkout")
        names |= {os.path.basename(p) for p in r.stdout.decode().split() if os.path.basename(p).startswith("apply_")}
    return names


def t_every_draft_of_l4e4_to_l4e8_is_registered_and_the_missing_ones_are_marked():
    text = open(REG, encoding="utf-8").read()
    drafts = _drafts()
    assert len(drafts) >= 9, drafts
    for n in sorted(drafts):
        assert "`%s`" % n in text, "the register misses %s" % n
    rows = _md_rows(REG, "| ID | Kind |")
    miss = [r for r in rows if r[6] == "MISSING DRAFT"]
    assert any("ILIM_HIZ" in r[2] for r in miss), "L4-E5's ILIM_HIZ network is not marked MISSING DRAFT"
    assert any("R10" in r[2] for r in miss), "L4-E5's R10 is not marked MISSING DRAFT"
    assert any("`apply_gen_sch_e_q1.py`" in r[3] for r in rows), "this record's own draft is not registered"


def t_the_release_order_puts_r12_before_the_ballast_and_l4e4s_release_first():
    rows = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    step = lambda rid: rows[rid][7]
    assert step("R-01") == "3a" and step("R-07") == "3c", "R12 (3a) before the ballasts (3c)"
    assert step("R-04") == "3b", "R11 after R12 and the line"
    assert step("R-90") == "1", "L4-E4's release record first"
    assert step("R-17") == "4a" and "4b" in step("R-13"), "Q1 no later than R10"
    text = open(REG, encoding="utf-8").read()
    assert "R12 12 mOhm and C147 330 pF (L4-E6)" in text and "R11 8 mOhm (L4-E4), never before" in text


def t_gate_covers_the_five_criteria_and_the_page_agrees():
    m = _M()
    assert sorted(g["n"] for g in m.GATE) == [1, 2, 3, 4, 5]
    page = _md_rows(PAGE, "| Criterion | Evidence | Verdict |")
    assert len(page) == 5, "the page's gate table has %d rows" % len(page)
    for row, g in zip(page, sorted(m.GATE, key=lambda x: x["n"])):
        assert row[0].startswith("%d." % g["n"]), row[0]
        assert row[2] == g["verdict"], "criterion %d: the page says %s, the script %s" % (g["n"], row[2], g["verdict"])
        if g["verdict"] != "PASS":
            assert row[3].strip() and row[4].strip(), "criterion %d not PASS without its constraint and overturn answer" % g["n"]
        line = re.search(r"^   %d\. .*?: (PASS|CONDITIONAL|FAIL); rows" % g["n"], _C["text"], re.M)
        assert line and line.group(1) == g["verdict"], "the output's gate line %d" % g["n"]


def t_nothing_marked_pass_rests_on_an_assumption_or_conditional_row():
    m = _M()
    st = _C["st"]
    assert m.gate_violations(m.GATE, st) == []
    for g in m.GATE:
        if g["verdict"] == "PASS":
            for rid in g["rows"]:
                cls, s = st[rid]
                assert s == "MEETS" and cls not in ("ASSUMPTION", "CONDITIONAL", "PENDING"), (g["n"], rid, cls, s)
    bad = copy.deepcopy(m.GATE)
    bad[0]["verdict"] = "PASS"
    assert m.gate_violations(bad, st), "a PASS on CONDITIONAL rows must be refused"
    bad = copy.deepcopy(m.GATE)
    bad[2]["rows"] = ["IF-11"]
    assert m.gate_violations(bad, st), "a PASS on an ASSUMPTION row must be refused"
    bad = copy.deepcopy(m.GATE)[:4]
    assert m.gate_violations(bad, st), "a gate of four criteria must be refused"


def t_the_page_interface_table_agrees_with_the_output():
    _M()
    rows = _md_rows(PAGE, "| Row | Interface |")
    st = _C["st"]
    assert [r[0] for r in rows] == [r["id"] for r in _C["R"]], "the page's rows are not the output's"
    for r in rows:
        status = r[-1].split(" (")[0]
        assert status == st[r[0]][1], "%s: the page says %s, the output %s" % (r[0], status, st[r[0]][1])
        assert len(r) == 9, "%s does not have the nine columns" % r[0]
        assert all(x.strip() for x in r[2:8]), "%s lacks a voltage, a current, losses, a thermal assumption, protection or a settling record on the page" % r[0]
        assert " / " in r[2] and " / " in r[3] and " / " in r[6], "%s does not give both sides on the page" % r[0]


def t_layer5_handover_entries_name_printed_rows():
    _M()
    rows = _md_rows(HAND, "| ID | Target |")
    assert len(rows) >= 6
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        rids = re.findall(r"IF-\d\d", r[3])
        assert rids, "%s names no interface row" % r[0]
        for rid in rids:
            assert rid in _C["st"], "%s names an unknown row %s" % (r[0], rid)
        assert r[4] in ("DRAFTED", "PENDING")
        if r[4] == "PENDING":
            assert any(_C["st"][x][1] == "PENDING" for x in rids), "%s is PENDING on rows that are not" % r[0]


def _q1(*args):
    return subprocess.run([sys.executable, "-B", Q1] + list(args), capture_output=True, text=True)


def t_q1_draft_checks_applies_once_refuses_the_tree_and_composes():
    need(Q1, "the Q1 draft")
    need(GEN_E, "board E's generator")
    with tempfile.TemporaryDirectory() as td:
        a = os.path.join(td, "gen_sch_e.py")
        shutil.copy(GEN_E, a)
        before = open(a, encoding="utf-8").read()
        r = _q1(a)
        assert r.returncode == 0 and open(a, encoding="utf-8").read() == before, "check mode must write nothing"
        r = _q1(a, "--write")
        assert r.returncode == 0, r.stderr
        after = open(a, encoding="utf-8").read()
        tree = ast.parse(after)
        consts = {n.targets[0].id: n.value for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
        ef = ast.literal_eval(consts["_ENTRY_FET"])
        assert "CSD19532Q5B 100 V" in ef[0] and ef[1] == "C473333"
        fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "ideal_diode"][0]
        assert [x.arg for x in fn.args.args][-1] == "fet" and 'anode == "DC_F"' in ast.get_source_segment(after, fn)
        assert after.count('ideal_diode("U4", "Q2", "C28", "R18", "TRK_OUT", "VIN_RAW", "GND")') == 1, "the tracker's ideal diode is untouched"
        assert _q1(a, "--write").returncode == 3, "a second application must be refused"
    r = _q1(GEN_E, "--write")
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, "the tree's generator must be refused until a release record"
    cin = os.path.join(ROOT, "v2", "docs", "records", "d8dec31", "apply_gen_sch_e_cin.py")
    l4e7 = [os.path.join(ROOT, "v2", "docs", "records", "l4e7", n) for n in
            ("apply_gen_sch_e_u5_grade.py", "apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py")]
    need(cin, "d8dec31's input capacitor draft")
    need(NET_E, "board E's netlist")
    with tempfile.TemporaryDirectory() as td:
        x, y = os.path.join(td, "x.py"), os.path.join(td, "y.py")
        shutil.copy(GEN_E, x)
        shutil.copy(GEN_E, y)
        assert subprocess.run([sys.executable, "-B", cin, x, NET_E], capture_output=True).returncode == 0
        assert _q1(x, "--write").returncode == 0, "Q1 after the input capacitor"
        assert _q1(y, "--write").returncode == 0
        assert subprocess.run([sys.executable, "-B", cin, y, NET_E], capture_output=True).returncode == 0, "the input capacitor after Q1"
        assert ast.dump(ast.parse(open(x).read())) == ast.dump(ast.parse(open(y).read())), "the two orders differ"
        for p in l4e7:
            r = subprocess.run([sys.executable, "-B", p, y, "--write"], capture_output=True, text=True)
            assert r.returncode == 0, "%s does not compose: %s" % (os.path.basename(p), r.stderr)


CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def t_no_dashes_and_no_claim_words_in_the_record():
    files = [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.endswith((".md", ".py", ".out"))]
    files.append(os.path.abspath(__file__))
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
        if p != os.path.abspath(__file__):
            m = CLAIM.search(t)
            assert not m, "%s carries a claim word: %r" % (os.path.relpath(p, ROOT), m.group(0))
