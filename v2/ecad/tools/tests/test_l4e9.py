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

Round 2 (2 October 2026): part A's three proposals (Q1, F1, U17) hold on the read figures and their drafts apply once, refuse
the tree and compose; the selected OVLO band clears CS101 at 36 V and stays under D10; the selected solutions (L4-E7R, L4-E8,
part A) are in the rows and only L4-E7R's CS101 follow-up (D-01) stays PENDING; L4-E10 and MESHSAT-1478 enter as unresolved
choices, never as register tasks, and a gate that PASSes on one is refused; the page's defect and choice tables are the
script's; every figure a choice or a defect states is printed by the reconciliation outside the gate. These are software
predicates on the record's own text and arithmetic: they establish no electrical or thermal property.

Fix round (2 October 2026, the focused check's B1 to B4): the hot-swap draft applies once and composes; the drawn power limit
is under TI's 5 mV and the selected one at or above it, the complete pulse sits inside Figure 10 at the same voltage and the
derived case temperature, and IF-05 reads CONDITIONAL; no file cites ASM-001 as an exemption and D-06 stays open; R227's
transients stay inside the INA226's limits for every required event; U-04 is a choice in criteria 1 and 5; the check is filed.
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
F1 = os.path.join(REC, "apply_gen_sch_e_f1.py")
U17 = os.path.join(REC, "apply_gen_sch_a_u17.py")
HS = os.path.join(REC, "apply_gen_sch_e_hotswap.py")
GEN_A = os.path.join(ROOT, "v2", "ecad", "tools", "gen_sch_a.py")
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
        for key, (rel, _sha) in m.PINS.items():
            if "/held/" in rel and not os.path.exists(os.path.join(ROOT, rel)):
                raise Skip("%s is held back (fetch_held_back.py fetches it)" % rel)
        for key, ref in m.FROM_COMMIT.items():
            if subprocess.run(["git", "-C", ROOT, "cat-file", "-e", ref], capture_output=True).returncode != 0:
                raise Skip("%s's selected commit %s is not in this checkout" % (key, ref))
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
    assert D["f1_v"] == F["ovlo_sel"][2] and F["f297_v"] < F["ovlo"][2] < D["f1_v"], "F1 against the selected OVLO maximum; the drawn MINI fails the drawn one"
    r20 = 2 * F["cable_m"] * m.CU_RHO_20C / F["cable_mm2"] + 2 * F["lead_mm"] / 1000.0 * m.CU_RHO_20C / m.AWG18_MM2
    assert abs(D["f1_ipf"] - F["ovlo_sel"][2] / (r20 * (1 + m.CU_ALPHA * (m.T_COLD - 20.0)))) < 1e-6
    assert D["f1_ipf"] > F["ovlo_sel"][2] / r20, "the cold copper must give the larger current"


def t_every_downstream_item_has_an_owner_and_an_acceptance():
    m = _M()
    rows = _md_rows(REG, "| ID | Kind |")
    assert len(rows) >= 40
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids)), "register ids repeat"
    for r in rows:
        assert len(r) == 8, "%s does not have eight columns" % r[0]
        rid, kind, item, frm, owner, acc, state, order = r
        assert re.fullmatch(r"R-\d{2,3}", rid), rid
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
    for n in ("apply_gen_sch_e_q1.py", "apply_gen_sch_e_f1.py", "apply_gen_sch_a_u17.py", "apply_gen_sch_e_hotswap.py"):
        assert any("`%s`" % n in r[3] for r in rows), "this record's own draft %s is not registered" % n


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


def _run(script, *args):
    return subprocess.run([sys.executable, "-B", script] + list(args), capture_output=True, text=True)


def _check_write_once_refuse(script, gen, label):
    """A draft writes nothing in check mode, applies once to a copy, refuses a second application and the tree's own
    generator (no release record)."""
    with tempfile.TemporaryDirectory() as td:
        a = os.path.join(td, os.path.basename(gen))
        shutil.copy(gen, a)
        before = open(a, encoding="utf-8").read()
        r = _run(script, a)
        assert r.returncode == 0 and open(a, encoding="utf-8").read() == before, "%s: check mode must write nothing" % label
        r = _run(script, a, "--write")
        assert r.returncode == 0, "%s: %s" % (label, r.stderr)
        after = open(a, encoding="utf-8").read()
        ast.parse(after)
        assert _run(script, a, "--write").returncode == 3, "%s: a second application must be refused" % label
    r = _run(script, gen, "--write")
    assert r.returncode == 3 and "NOT RELEASED" in r.stderr, "%s: the tree's generator must be refused until a release record" % label
    return after


def t_u17_draft_moves_the_monitor_to_the_stage_input_and_composes():
    need(U17, "the U17 draft")
    need(GEN_A, "board A's generator")
    after = _check_write_once_refuse(U17, GEN_A, "U17")
    tree = ast.parse(after)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
    first = lambda c: c.args[0].value if c.args and isinstance(c.args[0], ast.Constant) else None
    u17 = [c for c in calls if c.func.id == "ic" and first(c) == "U17"]
    assert len(u17) == 1
    pins = ast.literal_eval(u17[0].args[4])
    assert pins["10"] == "VBAT" and pins["9"] == "POE_VIN" and pins["8"] == "POE_VIN", "U17's IN+ on VBAT, IN- and VBUS on POE_VIN"
    assert "+54V_POE" not in pins.values() and "POE_OUT" not in pins.values(), "U17 keeps no pin on the 54 V side"
    r227 = [c for c in calls if c.func.id == "r" and first(c) == "R227"]
    assert len(r227) == 1 and [ast.literal_eval(x) for x in r227[0].args[2:4]] == ["VBAT", "POE_VIN"]
    assert "5mOhm" in ast.literal_eval(r227[0].args[1]), "R227 is the 5 mOhm part part A chose"
    poe = [c for c in calls if c.func.id == "lm5176" and first(c) == "POE"]
    assert len(poe) == 1 and ast.literal_eval(poe[0].args[2]) == "POE_VIN"
    kw = {k.arg: k.value for k in poe[0].keywords}
    assert ast.literal_eval(kw["bias"]) == "POE_VIN", "U16's BIAS moves with its input"
    assert after.find('_intent.rail("POE_VIN"') < after.find('_intent.rail("+54V_POE"'), "POE_VIN declared ahead of the rail it feeds"
    l4 = os.path.join(ROOT, "v2", "docs", "records")
    steps = [os.path.join(l4, "l4e6", "apply_gen_sch_a_r12.py"), os.path.join(l4, "l4e4", "apply_gen_sch_a_r11.py")]
    for p in steps:
        need(p, os.path.basename(p))
    with tempfile.TemporaryDirectory() as td:
        bank = os.path.join(td, "apply_gen_sch_a_bank.py")
        rb = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/records/l4e8/apply_gen_sch_a_bank.py" % _M().L4E8_COMMIT], capture_output=True)
        if rb.returncode != 0:
            raise Skip("L4-E8's commit is not in this checkout")
        open(bank, "wb").write(rb.stdout)
        x, y = os.path.join(td, "x.py"), os.path.join(td, "y.py")
        shutil.copy(GEN_A, x)
        shutil.copy(GEN_A, y)
        order = steps + [bank, os.path.join(l4, "l4e4", "apply_gen_sch_a_r138.py"), U17]
        for p in order:
            r = _run(p, x, "--write")
            assert r.returncode == 0, "%s in the release order: %s" % (os.path.basename(p), r.stderr)
        assert _run(U17, y, "--write").returncode == 0
        for p in order[:-1]:
            r = _run(p, y, "--write")
            assert r.returncode == 0, "%s after U17: %s" % (os.path.basename(p), r.stderr)
        assert ast.dump(ast.parse(open(x).read())) == ast.dump(ast.parse(open(y).read())), "U17 first and U17 last differ"


def t_f1_draft_names_the_58_v_part_and_composes():
    need(F1, "the F1 draft")
    need(GEN_E, "board E's generator")
    after = _check_write_once_refuse(F1, GEN_E, "F1")
    calls = [n for n in ast.walk(ast.parse(after)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "part"]
    f1 = [c for c in calls if c.args and isinstance(c.args[0], ast.Constant) and c.args[0].value == "F1"]
    assert len(f1) == 1
    val = ast.literal_eval(f1[0].args[3])
    assert "0997010" in val and "58 V DC" in val and "1000 A" in val and "3568" in val
    assert ast.literal_eval(f1[0].args[5]) == {"1": "DC_IN", "2": "DC_F"}, "F1's nets are untouched"
    cin = os.path.join(ROOT, "v2", "docs", "records", "d8dec31", "apply_gen_sch_e_cin.py")
    need(cin, "d8dec31's input capacitor draft")
    need(NET_E, "board E's netlist")
    with tempfile.TemporaryDirectory() as td:
        e7r = []
        for n in ("apply_gen_sch_e_u5_grade.py", "apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py", "apply_gen_sch_e_backstop.py"):
            rb = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/records/l4e7/%s" % (_M().FROM_COMMIT["l4e7r"], n)], capture_output=True)
            if rb.returncode != 0:
                raise Skip("L4-E7R's drafts are not in this checkout")
            e7r.append(os.path.join(td, n))
            open(e7r[-1], "wb").write(rb.stdout)
        x, y = os.path.join(td, "x.py"), os.path.join(td, "y.py")
        shutil.copy(GEN_E, x)
        shutil.copy(GEN_E, y)
        assert subprocess.run([sys.executable, "-B", cin, x, NET_E], capture_output=True).returncode == 0
        for p in [Q1] + e7r + [F1]:
            r = _run(p, x, "--write")
            assert r.returncode == 0, "%s: %s" % (os.path.basename(p), r.stderr)
        assert _run(F1, y, "--write").returncode == 0
        assert subprocess.run([sys.executable, "-B", cin, y, NET_E], capture_output=True).returncode == 0
        for p in [Q1] + e7r:
            r = _run(p, y, "--write")
            assert r.returncode == 0, "%s after F1: %s" % (os.path.basename(p), r.stderr)
        assert ast.dump(ast.parse(open(x).read())) == ast.dump(ast.parse(open(y).read())), "F1 first and F1 last differ"


def t_part_a_conditions_hold_on_the_read_figures():
    m = _M()
    F, D = _C["F"], _C["D"]
    A = m.partA(F, D, m._C_TEXT)
    # Q1: reverse inside the part and the controller; normal junction inside its maximum; the drive inside VGS
    assert A["q1_rev"] <= F["csd19532_vds"] and A["q1_rev"] <= F["ld_ac_rec"] <= F["ld_ca_abs"]
    assert A["q1_tj"] < A["tj_max"] and F["entry_lim"][1] <= A["id_cont"]
    assert A["plim_hi"] <= A["soa_hot_w"], "the hot swap's power limit with its spread inside Q7's hot 10 ms SOA"
    assert A["cs101_top"] > F["ovlo"][0] and A["cs101_top_src"] < F["ovlo"][0], "the CS101 finding is the range's top, not curve 2's boundary"
    lo, hi = A["r23_win"]
    assert lo < A["r23_e192"] < hi and A["ovlo_e192"][0] > A["cs101_top"] and A["ovlo_e192"][1] < F["SMCJ40A"]["vbr_min"]
    assert abs(A["ovlo_check"][0] - F["ovlo"][0]) < 0.01 and abs(A["ovlo_check"][1] - F["ovlo"][2]) < 0.01, "the band re-derived as s120 prints it"
    # F1: a DC rating at the OVLO maximum, an interrupting rating at the cold cable's current, the next higher derating column
    assert A["f_v"] >= D["f1_v"] and A["f_int"] >= D["f1_ipf"]
    above = [x for x in A["f_amb"] if x >= F["air"][1]]
    assert A["f_col"] == min(above) and A["f_allow"] >= F["entry_lim"][1], "the derating column is the next higher, never interpolated"
    assert A["f_startup_i2t"] < A["f_i2t"]
    assert A["f_min_fault_9v"] >= 6.0 * 10.0 and A["f_tc"][600][1] is not None, "the lowest stiff fault sits in the 600 % row"
    # U17: its common mode at the highest VBAT bound, its differential at the stage's fault bound, R227 inside its derated power
    assert max(F["sysovp"][2], D["pack_open"]["v_end"]) <= F["ina_cm_op"] < F["ina_abs"]
    assert A["u17_mv_norm"] < A["u17_mv_fault"] <= F["ina_fs_mv"]
    assert A["u17_buck_valley_a"] < A["u17_fault_a"], "the buck-mode bound under the boost bound"
    assert A["u17_p_fault"] <= A["hojlr_avail"]
    assert abs(A["u17_cal"] - round(A["u17_cal"])) < 1e-6 and A["u17_fs_a"] > A["u17_fault_a"]


def t_the_part_a_page_agrees_with_the_output():
    _M()
    page = open(os.path.join(REC, "L4E9-ENTRY-PROPOSALS.md"), encoding="utf-8").read()
    sec = _C["text"].split("11. PART A")[1]
    for fig in ("66.15", "0.361", "80.2", "38.83", "30.83", "569.8", "7.3 A", "0.309", "85.9", "18.59", "72.38", "1.037", "16.384", "2048", "1.475",
                "6.346", "6.458", "39.04", "43.92", "39.71", "43.18", "42.4 V",
                "4.7429", "5.06", "0.913", "0.675", "94.3", "29.14", "2.05", "17.77", "33.77", "2.879", "1.731", "3.025", "623.9", "22.412"):
        assert fig in sec, "the output lacks %s" % fig
        assert fig in page, "the part A page lacks %s" % fig
    for part in ("CSD19532Q5B", "0997010.WXN", "C2903482", "R227"):
        assert part in page and part in sec
    for sha in ("437b1fd2c8cb3ef16107ec14d096b31ef3c3cb83893325234e880deb7540393e", _M().PINS["csd19532"][1], _M().PINS["ina226"][1]):
        assert sha in page, "the part A page does not pin %s" % sha[:16]


def t_the_ovlo_band_selected_clears_cs101_and_stays_under_d10():
    m = _M()
    F, D = _C["F"], _C["D"]
    A = m.partA(F, D, m._C_TEXT)
    lo, nom, hi = F["ovlo_sel"]
    assert lo < nom < hi
    assert A["cs101_top"] < lo, "the selected OVLO minimum clears 36 V plus CS101's peak"
    assert hi < F["SMCJ40A"]["vbr_min"], "the selected OVLO maximum stays under D10's breakdown minimum at 25 C"
    assert 40.0 < A["d10_cold_vbr"], "D10 stays off at REQ-015's 40 V when cold"
    assert A["r23_win"][0] < m.R23_NEW_K < A["r23_win"][1], "R23 inside the window computed at 1 %"
    assert abs(A["ovlo_new"][0] - lo) < 1e-9 and abs(A["ovlo_new"][1] - hi) < 1e-9, "part A and the rows use one band"
    for r in _C["R"]:
        for c in r["checks"]:
            if c.scope == "selected" and "OVLO maximum" in c.what and c.unit == "V" and isinstance(c.a, float):
                assert abs(c.a - round(hi, 2)) < 1e-9, "%s: a selected check on the drawn OVLO maximum" % r["id"]


def t_the_selected_solutions_are_in_the_rows_and_only_d01_is_pending():
    _M()
    F = _C["F"]
    rows = {r["id"]: r for r in _C["R"]}
    pend = [(r["id"], c) for r in _C["R"] for c in r["checks"] if c.cls == "PENDING"]
    assert pend, "L4-E7R's CS101 follow-up must keep its rows PENDING until it lands"
    for rid, c in pend:
        assert rid in ("IF-01", "IF-02") and "CS101 follow-up" in c.src, "%s is PENDING on something other than D-01" % rid
    st = _C["st"]
    assert st["IF-01"][1] == "PENDING" and st["IF-02"][1] == "PENDING"
    by_what = {c.what: c for c in rows["IF-02"]["checks"]}
    sb = [c for c in rows["IF-02"]["checks"] if "static bound" in c.what][0]
    assert sb.a == F["static_bound"] and sb.b == 100.0 and sb.cls == "CONDITIONAL", "the backstop's static bound, CONDITIONAL"
    rg = [c for c in rows["IF-02"]["checks"] if "under the backstop's lowest trip" in c.what][0]
    assert rg.a == F["reg"][1] and rg.b == F["bs_trip"][0] and rg.met
    hot = [c for c in rows["IF-01"]["checks"] if "with the sheet's power tolerance inside F2" in c.what][0]
    assert hot.a == F["isc_hot_tol"] and hot.met
    for rid in ("IF-04", "IF-13"):
        sel = [c for c in rows[rid]["checks"] if c.scope == "selected"]
        assert all(c.met is not False for c in sel), "%s: a selected check fails" % rid
        assert all(c.cls != "PENDING" for c in sel)
    drawn = [c for c in rows["IF-04"]["checks"] + rows["IF-13"]["checks"] if c.scope == "drawn" and c.met is False]
    assert len(drawn) >= 4, "the as-drawn defects (Q1, F1, U17, the OVLO under CS101) stay visible"
    text = _C["text"]
    assert "%s / %s / %s Wh" % tuple(_C["M"].fmt(x) for x in F["e7r_day"]) in text, "L4-E7R's energy in the endurance"
    assert "2.09 W" in text.split("8. THE ENDURANCE")[1].split("9. THE CLOSURE")[0], "L4-E8's losses in the budgets"


def t_l4e10_and_meshsat_1478_enter_as_choices_not_tasks():
    m = _M()
    F = _C["F"]
    rows = {r["id"]: r for r in _C["R"]}
    c11 = [c for c in rows["IF-11"]["checks"] if "MESHSAT-1478" in c.what][0]
    assert c11.a == F["corner_air"][1] and c11.b == F["parts_hot"] and c11.met is False and "U-02" in c11.src
    c10 = [c for c in rows["IF-10"]["checks"] if "FEA-008" in c.what][0]
    assert c10.met is None and c10.cls == "CONDITIONAL" and "U-01" in c10.src
    ids = [c["id"] for c in m.CHOICES]
    assert ids == ["U-01", "U-02", "U-03", "U-04"]
    assert "FEA-008" in m.CHOICES[0]["title"] and "MESHSAT-1478" in m.CHOICES[1]["title"]
    for g in m.GATE:
        if g["n"] in (1, 5):
            assert set(g["choices"]) == set(ids) and g["verdict"] != "PASS"
    bad = copy.deepcopy(m.GATE)
    bad[4]["verdict"] = "PASS"
    bad[4]["rows"] = []
    assert m.gate_violations(bad, _C["st"]), "a PASS while an unresolved choice stands must be refused"
    bad = copy.deepcopy(m.GATE)
    bad[1]["verdict"] = "PASS"
    bad[1]["rows"] = ["IF-13"]
    assert m.gate_violations(bad, _C["st"]), "criterion 2 PASS while D-01 is open must be refused"
    assert abs(F["corner_heat"] - (F["corner_air"][0] - F["e3o_amb"]) * F["th1"]) < 1e-9
    assert "%s K on the inside air" % m.fmt(round(F["ballast_w"] / F["th1"], 2)) in _C["text"], "the ballasts' heat at T-H1's floor"


def t_the_two_categories_are_kept_apart_on_the_page_and_in_the_register():
    m = _M()
    reg_rows = _md_rows(REG, "| ID | Kind |")
    assert not any(r[0].startswith("U-") for r in reg_rows), "a choice is not a register item"
    reg = open(REG, encoding="utf-8").read()
    for c in m.CHOICES:
        assert c["id"] in reg.split("## The release order")[0], "the register's category note misses %s" % c["id"]
    for r in reg_rows:
        if r[7] == "U-01" or "U-01" in r[7]:
            assert "U-01" in r[2] or "U-01" in r[5] or "under U-01" in r[2].replace("U-01's", "U-01"), r[0]
    page = open(PAGE, encoding="utf-8").read()
    ch = m.md_table(page, "| Choice | What |")
    assert [r[0] for r in ch] == [c["id"] for c in m.CHOICES]
    for r, c in zip(ch, m.CHOICES):
        assert r[1] == c["title"] and r[2] == c["constraint"] and r[3] == c["settles"] and r[4] == c["alternatives"], c["id"]
        assert r[5] == c["owner"] and r[6] == c["overturns"], c["id"]
    de = m.md_table(page, "| Defect | What |")
    assert [r[0] for r in de] == [d["id"] for d in m.DEFECTS]
    for r, d in zip(de, m.DEFECTS):
        assert r[1] == d["title"] and r[2] == d["constraint"] and r[3] == d["options"], d["id"]
        assert r[4].split(":")[0].split(",")[0].split(" ")[0] == d["state"].split(" ")[0], d["id"]
    assert [d["id"] for d in m.DEFECTS if d["state"] == "OPEN"] == ["D-01", "D-06"]


def t_choice_and_defect_figures_are_printed_by_the_reconciliation():
    m = _M()
    text = _C["text"]
    body = text.split("9. THE CLOSURE GATE")[0] + text.split("11. PART A")[1]
    for c in m.CHOICES:
        for k in ("constraint", "settles", "alternatives", "owner", "overturns"):
            for fig in re.findall(r"\d+\.\d+", c[k]):
                assert fig in body, "%s's %s figure %s is not printed outside the gate" % (c["id"], k, fig)
    for d in m.DEFECTS:
        for fig in re.findall(r"\d+\.\d+", d["constraint"]):
            assert fig in body, "%s's figure %s is not printed outside the gate" % (d["id"], fig)


def t_the_hotswap_draft_applies_once_refuses_the_tree_and_composes():
    need(HS, "the hot-swap draft")
    need(GEN_E, "board E's generator")
    after = _check_write_once_refuse(HS, GEN_E, "hot swap")
    calls = [n for n in ast.walk(ast.parse(after)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "r"]
    val = {c.args[0].value: c.args[1].value for c in calls if len(c.args) > 1 and isinstance(c.args[0], ast.Constant) and isinstance(c.args[1], ast.Constant)}
    assert val["R22"].startswith("100k 0.1%") and val["R23"].startswith("%sk 0.1%%" % ("%g" % _M().R23_NEW_K)) and val["R24"].startswith("%gk 1%%" % _M().R24_NEW_K)
    assert val["R20"] == "100k 1%" and val["R21"].startswith("38.3k 1%"), "the UVLO divider is untouched"
    cin = os.path.join(ROOT, "v2", "docs", "records", "d8dec31", "apply_gen_sch_e_cin.py")
    need(cin, "d8dec31's input capacitor draft")
    with tempfile.TemporaryDirectory() as td:
        e7r = []
        for n in ("apply_gen_sch_e_u5_grade.py", "apply_gen_sch_e_hold.py", "apply_gen_sch_e_input_limit.py", "apply_gen_sch_e_backstop.py"):
            rb = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/records/l4e7/%s" % (_M().FROM_COMMIT["l4e7r"], n)], capture_output=True)
            if rb.returncode != 0:
                raise Skip("L4-E7R's drafts are not in this checkout")
            e7r.append(os.path.join(td, n))
            open(e7r[-1], "wb").write(rb.stdout)
        x, y = os.path.join(td, "x.py"), os.path.join(td, "y.py")
        shutil.copy(GEN_E, x)
        shutil.copy(GEN_E, y)
        assert subprocess.run([sys.executable, "-B", cin, x, NET_E], capture_output=True).returncode == 0
        for p in [Q1, F1] + e7r + [HS]:
            r = _run(p, x, "--write")
            assert r.returncode == 0, "%s: %s" % (os.path.basename(p), r.stderr)
        assert _run(HS, y, "--write").returncode == 0
        assert subprocess.run([sys.executable, "-B", cin, y, NET_E], capture_output=True).returncode == 0
        for p in [Q1, F1] + e7r:
            r = _run(p, y, "--write")
            assert r.returncode == 0, "%s after the hot-swap draft: %s" % (os.path.basename(p), r.stderr)
        assert ast.dump(ast.parse(open(x).read())) == ast.dump(ast.parse(open(y).read())), "the hot-swap draft first and last differ"


def t_b1_the_power_limit_and_the_complete_pulse_at_one_voltage_and_temperature():
    m = _M()
    F, D = _C["F"], _C["D"]
    A = m.partA(F, D, m._C_TEXT)
    assert A["vsns_drawn"] < A["vsns_min"] <= A["vsns_new_low"] < A["vsns_new_nom"], "drawn under 5 mV; the selected low corner at or above it"
    assert A["rpwr_min"] <= m.R24_NEW_K * 1e3 * (1 - m.R24_TOL), "R24's low corner above Equation 9's least RPWR"
    assert abs(A["pulse_w"] - m.TI_SOA_MARGIN * A["plim_new_hi"]) < 1e-9 and abs(A["pulse_a"] * F["ovlo_sel"][2] - A["pulse_w"]) < 1e-9
    assert {"10ms", "1ms", "10us"} <= set(A["soa_labels"]) and A["soa_1ms"] > A["soa_tflt_25"] > A["soa_10ms"] > 0, "the pulse lies between the 1 and 10 ms lines"
    assert 0 < A["soa_m"] < 1
    assert abs(A["tc_max"] - (A["t_hot"] + A["q1_p"] * A["rja"])) < 1e-9 and A["t_hot"] >= F["air"][1]
    assert A["pulse_a"] <= A["soa_tflt_hot"] and A["cb_a"] <= A["cb_10us_hot"]
    sel = {c.what: c for c in [c for r in _C["R"] if r["id"] == "IF-05" for c in r["checks"]]}
    pulse = [c for w, c in sel.items() if "complete hot-short pulse" in w][0]
    assert pulse.cls == "CONDITIONAL" and _C["st"]["IF-05"][1] == "CONDITIONAL", "IF-05 does not read MEETS on an unresolved board assumption"
    assert any(c.scope == "drawn" and c.met is False and "20k" in w for w, c in sel.items()), "the drawn setting's shortfall stays visible"


def t_b2_no_exemption_is_claimed_and_the_weak_source_band_is_open():
    m = _M()
    files = [OUT, PAGE, REG, HAND, os.path.join(REC, "L4E9-ENTRY-PROPOSALS.md")]
    for p in files:
        t = open(p, encoding="utf-8").read()
        for bad in ("(ASM-001)", "fault, ASM-001", "requirement (ASM-001)"):
            assert bad not in t, "%s still cites ASM-001 as an exemption (%s)" % (os.path.basename(p), bad)
    d6 = [d for d in m.DEFECTS if d["id"] == "D-06"][0]
    assert d6["state"] == "OPEN" and "IF-04" in d6["rows"]
    rows = {r["id"]: r for r in _C["R"]}
    assert any("D-06" in c.src and c.met is None for c in rows["IF-04"]["checks"])
    assert any("R-115" in c.src for c in rows["IF-04"]["checks"]), "F1's let-through is CONDITIONAL on the maker's figure"
    A = m.partA(_C["F"], _C["D"], m._C_TEXT)
    assert A["f_rating"] < A["f_i2"] < A["f_200"] and max(a for _n, a in A["wk"]) < A["f_200"], "the weak elements sit inside the fuse's long-time band"
    assert A["f1_ipf_awg16"] < A["f_int"]


def t_b3_r227_transients_are_bounded_for_every_required_event():
    m = _M()
    F, D = _C["F"], _C["D"]
    A = m.partA(F, D, m._C_TEXT)
    req = [t for t in A["tr"] if t[6]]
    assert len(req) >= 2
    for nm, v0, v1, dv, ring, e_mj, _r in req:
        assert dv <= A["ina_diff_abs"] and ring <= F["ina_abs"], nm
        assert abs(e_mj - 0.5 * A["poe_c_uf"] * 1e-6 * dv ** 2 * 1e3) < 1e-9
    assert A["buck_p"] <= A["hojlr_avail"] and A["buck_peak_steady"] < A["l10_isat"]
    assert A["short_peak"] > A["l10_isat"], "the hard short's lower bound is past Isat and is carried as CONDITIONAL"
    rows = {r["id"]: r for r in _C["R"]}
    assert _C["st"]["IF-13"][1] == "CONDITIONAL" and any("R-101" in c.src for c in rows["IF-13"]["checks"])


def t_b4_source_only_operation_is_an_unresolved_choice():
    m = _M()
    u4 = [c for c in m.CHOICES if c["id"] == "U-04"][0]
    assert "Q-TI-3" in u4["constraint"] and u4["alternatives"] and u4["overturns"]
    for g in m.GATE:
        if g["n"] in (1, 5):
            assert "U-04" in g["choices"]
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert "12 V and 24 V" in reg["R-85"][5] and "does not settle U-04" in reg["R-85"][2]
    assert "SOURCE-ONLY AND DEAD-PACK OPERATION" in _C["text"]


def t_the_check_is_filed_with_its_blockers():
    p = os.path.join(REC, "checks", "astra-check-l4e9-1.md")
    need(p, "the filed check")
    t = open(p, encoding="utf-8").read()
    assert t.splitlines()[0] == "accepted: no"
    for b in ("B1, G1/G5", "B2, G1/G2/G5", "B3, G3/G5", "B4, G5"):
        assert b in t, b
    assert "astra-check-l4e9-1.md" in open(os.path.join(REC, "README.md"), encoding="utf-8").read()


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
