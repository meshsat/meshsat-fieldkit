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

Update round (2 October 2026, the accepted L4-E10, L4-E11 and L4-E12): the selected entry's figures are L4-E11's, read from its
output; E11-19's inductance bound reproduces L4-E11's and every start and fault pulse sits far under F1's melting I2t; the LM5069's
checks print only as drawn or as the alternative, IF-05 reads CONDITIONAL and no material defect is open (D-06 resolved in
design, D-07 and D-09 superseded); IF-11 carries L4-E12's binding line; every E11 item, every L4-E10 and L4-E12 owner row is in
the register or the owner's list; the owner's items are kept apart with their documents pinned; L4-E11's entry draft applies on
this record's hot-swap draft and not before it.

Update round 3 (2 October 2026, L4-E13 accepted): U-03 is a CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC) with L4-E13's
figures read from its pinned output; criteria 1 and 5 name exactly the architecture-level choices (a gate naming U-03 there, or
leaving one of U-01, U-02, U-04 out, is refused); the register carries PANEL-ACC (R-35, R-52, R-148, R-149) at 139 items; the
owner's list carries the panel's purchase and the two route-1 drafts; the gate reads NOT CLOSED. Update round 4: L4-E13's update
after set 25 is pinned with its check 4, its citation of L4-E7R equals L4-E7R's own figures, and the nominal hold's day under the
accepted stage is 336.6 Wh wherever this record cites it on that basis.

Update round 5 (the dependency rounds of L4-E10, L4-E12 and L4-E11, each accepted by a check 4): their inputs are pinned at those
commits; U-01, U-02 and U-04 each give their question, their evidence by vendor, physical and owner, who supplies it, the fallback
and what they could overturn, quoting the rounds' figures as printed (a choice quoting another figure, or missing a source of
evidence, is refused); U-02's fallback is the session's down to its floor and the owner's below E3-O's; U-04 turns on D1 and D3;
the register carries L4-E12's drafted fan row, T-H1's procedure, E11-24, E11-26, L4-E10's charge drafts and four items of the
findings ledger, at 146 items; the TI request and T-H1's bench are owner's items; the bullet L4-E10 reads back is unchanged.

The consolidation (the owner's instruction of 2 October 2026): one diagram covering every interface row, one budget on pinned
inputs with its reconciliation, one change list covering every apply script in order, the behaviour, the handover and the exit
held equal to the script. Its fourth result, L4-E12's heat-rejection comparison (check 6 at 589f18ac): the thresholds at the
profile's heat are read from its output with their targets equal to its needs; the exit opens with the precise bounded question
and its executable path (P1, the combined route, the owner's options); the combined route's three items are register rows under
the reading and in the change list (a list missing one is refused); T-H1's handover runs P1 first and keeps P2's bands; the heat
table carries each approach's conductance beside the bound. Set 27 adds L4-E7's panel-lead surge derivation: its verdicts are
read from L4-E7's output; IF-01 reads NOT MET only on the two known single faults D-10 and D-11, open defects whose remedy is
pending L4-E7's round (the owner's amendment of 14:20: no remedy selected here); R-173 holds the remedy's place in board E's round
after the drafted entry (a list putting it first is refused); R-156 is restated and OWED, the CS116 and CS115 test is a layer 8
row; the exit carries the open defects beside U-01, U-02 and U-04.
"""
import ast
import copy
import glob
import hashlib
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
                "4.7429", "5.06", "0.777", "0.675", "94.3", "29.14", "2.05", "17.77", "33.77", "2.879", "1.731", "3.025", "623.9", "22.412",
                "13.131", "11.871", "2.035", "3.814", "3.167", "4.189", "8.976"):
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


def t_the_selected_solutions_are_in_the_rows_and_nothing_is_pending():
    _M()
    F = _C["F"]
    rows = {r["id"]: r for r in _C["R"]}
    assert not [r["id"] for r in _C["R"] for c in r["checks"] if c.cls == "PENDING"], "L4-E7R is accepted: no row waits on it"
    assert all(st[1] != "PENDING" for st in _C["st"].values())
    sb = [c for c in rows["IF-02"]["checks"] if "static bound" in c.what][0]
    assert sb.a == F["static_bound"] and sb.b == 100.0 and sb.cls == "CONDITIONAL", "the backstop's static bound, CONDITIONAL"
    rg = [c for c in rows["IF-02"]["checks"] if "under the backstop's lowest trip" in c.what][0]
    assert rg.a == F["reg"][1] and rg.b == F["bs_trip"][0] and rg.met
    m2 = [c for c in rows["IF-01"]["checks"] if "TEST-PLAN M2" in c.what][0]
    assert m2.a == F["m2_ripple"] and m2.b == F["m2_margin"] and m2.met and m2.cls == "CONDITIONAL", "D-01's correction in IF-01, on the loop's typical rows"
    hot = [c for c in rows["IF-01"]["checks"] if "with the sheet's power tolerance inside F2" in c.what][0]
    assert hot.a == F["isc_hot_tol"] and hot.met
    for rid in ("IF-04", "IF-13"):
        sel = [c for c in rows[rid]["checks"] if c.scope == "selected"]
        assert all(c.met is not False for c in sel), "%s: a selected check fails" % rid
    drawn = [c for c in rows["IF-04"]["checks"] + rows["IF-13"]["checks"] if c.scope == "drawn" and c.met is False]
    assert len(drawn) >= 4, "the as-drawn defects (Q1, F1, U17, the OVLO under CS101) stay visible"
    text = _C["text"]
    assert "%s / %s / %s Wh" % tuple(_C["M"].fmt(x) for x in F["e7r_day"]) in text, "L4-E7R's energy in the endurance"
    assert "2.09 W" in text.split("8. THE ENDURANCE")[1].split("9. THE CLOSURE")[0], "L4-E8's losses in the budgets"
    d1 = [d for d in _C["M"].DEFECTS if d["id"] == "D-01"][0]
    assert d1["state"].startswith("RESOLVED") and "91e9a4b5" in d1["resolution"]


def t_l4e10_and_meshsat_1478_enter_as_choices_not_tasks():
    m = _M()
    F = _C["F"]
    rows = {r["id"]: r for r in _C["R"]}
    c11 = [c for c in rows["IF-11"]["checks"] if "MESHSAT-1478" in c.what][0]
    assert c11.a == F["e5_line"] and c11.b == F["parts_hot"] and c11.met and c11.cls == "CONDITIONAL" and "U-02" in c11.src
    floor = [c for c in rows["IF-11"]["checks"] if "LO-01a's floor" in c.what][0]
    assert floor.scope == "drawn" and floor.met is False and floor.a == F["floor_air"][1], "the design as it stands stays visible"
    c10 = [c for c in rows["IF-10"]["checks"] if "FEA-008" in c.what][0]
    assert c10.met is None and c10.cls == "CONDITIONAL" and "U-01" in c10.src
    ids = [c["id"] for c in m.CHOICES]
    assert ids == ["U-01", "U-02", "U-03", "U-04"]
    assert "FEA-008" in m.CHOICES[0]["title"] and "MESHSAT-1478" in m.CHOICES[1]["title"]
    for g in m.GATE:
        if g["n"] in (1, 5):
            assert set(g["choices"]) == {c["id"] for c in m.CHOICES if c["class"] == m.ARCH} and g["verdict"] != "PASS"
    bad = copy.deepcopy(m.GATE)
    bad[4]["verdict"] = "PASS"
    bad[4]["rows"] = []
    assert m.gate_violations(bad, _C["st"]), "a PASS while an unresolved choice stands must be refused"
    bad = copy.deepcopy(m.GATE)
    bad[1]["verdict"] = "PASS"
    bad[1]["rows"] = ["IF-13"]
    assert m.gate_violations(bad, _C["st"]), "criterion 2 PASS on a CONDITIONAL row must be refused"
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
    ch = m.md_table(page, "| Choice | Class |")
    assert [r[0] for r in ch] == [c["id"] for c in m.CHOICES]
    for r, c in zip(ch, m.CHOICES):
        assert r[1] == c["class"] and r[2] == c["title"] and r[3] == c["question"] and r[4] == c["constraint"], c["id"]
        assert r[5] == m.evidence_text(c) and r[6] == c["supplier"] and r[7] == c["fallback"] and r[8] == c["overturns"], c["id"]
    de = m.md_table(page, "| Defect | What |")
    assert [r[0] for r in de] == [d["id"] for d in m.DEFECTS]
    for r, d in zip(de, m.DEFECTS):
        assert r[1] == d["title"] and r[2] == d["constraint"] and r[3] == d["options"], d["id"]
        assert r[4].split(":")[0].split(",")[0].split(" ")[0] == d["state"].split(" ")[0], d["id"]
    # the update round left no material defect open; since set 27 D-10 and D-11 are the known open defects, their remedy pending L4-E7's round
    assert [d["id"] for d in m.DEFECTS if d["state"] == "OPEN"] == ["D-10", "D-11"], "only the solar faults are open"
    st = {d["id"]: d["state"] for d in m.DEFECTS}
    assert st["D-06"].startswith("RESOLVED") and st["D-07"].startswith("SUPERSEDED") and st["D-09"].startswith("SUPERSEDED")


def t_choice_and_defect_figures_are_printed_by_the_reconciliation():
    m = _M()
    text = _C["text"]
    body = text.split("9. THE CLOSURE GATE")[0] + text.split("11. PART A")[1]
    for c in m.CHOICES:
        fields = dict(c, evidence=m.evidence_text(c))
        for k in ("question", "constraint", "evidence", "supplier", "fallback", "overturns"):
            for fig in re.findall(r"\d+\.\d+", fields[k]):
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
    assert A["pulse_a"] <= A["soa_tenv_hot"] <= A["soa_tflt_hot"], "the power-limit part at the timer envelope's maximum, the longer time the lower line"
    assert abs(A["tflt_env"][1] - F["timer_ms"][2] * A["c_hi_f"]) < 1e-9 and abs(A["tflt_env"][0] - F["timer_ms"][0] * A["c_lo_f"]) < 1e-9
    assert A["c_hi_f"] > 1 + A["c_tol"], "C5's envelope carries more than its tolerance"
    assert abs(A["cb_thr"] - A["vcb_max"] * 1e-3 / (A["rs"] * 0.99)) < 1e-9
    rows = {r["id"]: r for r in _C["R"]}
    sel = {c.what: c for c in rows["IF-05"]["checks"]}
    part = [c for w, c in sel.items() if "power-limit part" in w][0]
    assert part.scope == "alternative" and part.cls == "CONDITIONAL" and part.met and part.a == F["alt_pulse"] and part.b == F["alt_soa"]
    cb = [c for w, c in sel.items() if "breaker's event" in w][0]
    assert cb.scope == "alternative" and cb.met is None and "R-118" in cb.src, "the LM5069's breaker event stays OPEN evidence for the alternative"
    stt = [c for w, c in sel.items() if "fault time's minimum" in w][0]
    assert stt.scope == "alternative" and stt.met and stt.a == F["alt_tflt"][0] and stt.b == F["alt_need"], "D-09 resolved for the LM5069 by L4-E11's C5 and C121"
    assert A["tflt_env"][0] < A["start_need"], "this record's round-two reading of C5 alone stays printed as found"
    assert _C["st"]["IF-05"][1] == "CONDITIONAL", "IF-05 reads CONDITIONAL on the selected entry"
    assert any(c.scope == "drawn" and c.met is False and "20k" in w for w, c in sel.items()), "the drawn setting's shortfall stays visible"
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert "E11-17" in reg["R-118"][3] and "R-119" in reg["R-118"][5] and "C5" in reg["R-119"][2] and reg["R-119"][7] == "LM5069 alternative"


def t_b2_no_exemption_is_claimed_and_the_weak_source_band_is_open():
    m = _M()
    files = [OUT, PAGE, REG, HAND, os.path.join(REC, "L4E9-ENTRY-PROPOSALS.md")]
    for p in files:
        t = open(p, encoding="utf-8").read()
        for bad in ("(ASM-001)", "fault, ASM-001", "requirement (ASM-001)"):
            assert bad not in t, "%s still cites ASM-001 as an exemption (%s)" % (os.path.basename(p), bad)
    d6 = [d for d in m.DEFECTS if d["id"] == "D-06"][0]
    assert d6["state"].startswith("RESOLVED") and "IF-04" in d6["rows"] and "E11-10 to E11-16" in d6["resolution"]
    rows = {r["id"]: r for r in _C["R"]}
    sel = [c for c in rows["IF-04"]["checks"] if c.scope == "selected"]
    assert any("E11-16" in c.src and c.met is None and c.cls == "CONDITIONAL" for c in sel), "the interconnect's short-time evidence stays OPEN"
    assert any("D-06" in c.src and c.met and c.cls == "CONDITIONAL" for c in sel), "D-06 resolved in design, CONDITIONAL on the makers' ratings"
    assert any(c.scope == "drawn" and c.met is False and "13 A test current" in c.what for c in rows["IF-04"]["checks"]), "the drawn interconnect stays visible"
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
    assert any("R-120" in c.src for c in rows["IF-13"]["checks"]), "L10's own assignment is named"
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    l10 = [r for r in reg.values() if "L10" in r[2]]
    assert l10 and any("L(I)" in r[2] or "L against current" in r[2] for r in l10), "an L10 assignment with its L(I)"
    assert any("R227" in r[2] and "temperature" in r[2] and "pins" in r[2] for r in l10), "R227's stress and U17's pins at temperature"
    for p in (OUT, PAGE, REG, os.path.join(REC, "L4E9-ENTRY-PROPOSALS.md")):
        t = open(p, encoding="utf-8").read()
        assert "R-65 extended" not in t and "R-65's sweep extended" not in t, "%s still promises an R-65 extension" % os.path.basename(p)
    assert "mJ NOMINAL" in _C["text"] and "UNRESOLVED" in _C["text"], "R227's energy labelled nominal, its maximum unresolved"
    assert A["tr"][0][5] * A["c_hi_f"] > A["tr"][0][5] * (1 + A["c_tol"]) > A["tr"][0][5]


def t_b4_source_only_operation_is_an_unresolved_choice():
    m = _M()
    u4 = [c for c in m.CHOICES if c["id"] == "U-04"][0]
    assert "Q-TI-3" in u4["constraint"] and u4["fallback"] and u4["overturns"]
    for g in m.GATE:
        if g["n"] in (1, 5):
            assert "U-04" in g["choices"]
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert "12 V and 24 V" in reg["R-85"][5] and "does not settle U-04" in reg["R-85"][2]
    assert "SOURCE-ONLY AND DEAD-PACK OPERATION" in _C["text"]


def t_the_checks_are_filed_with_their_blockers():
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    for name, blockers in (("astra-check-l4e9-1.md", ("B1, G1/G5", "B2, G1/G2/G5", "B3, G3/G5", "B4, G5")),
                           ("astra-check-l4e9-2.md", ("B1, R1/R5", "B3, R3/R5", "B3, R5"))):
        p = os.path.join(REC, "checks", name)
        need(p, "the filed check %s" % name)
        t = open(p, encoding="utf-8").read()
        assert t.splitlines()[0] == "accepted: no"
        for b in blockers:
            assert b in t, (name, b)
        assert name in readme


def t_e11_19_the_selected_entry_is_rejudged_and_no_defect_is_open():
    m = _M()
    F, D = _C["F"], _C["D"]
    A = m.partA(F, D, m._C_TEXT)
    E = m.rejudge(F, D, A)
    hs = F["e_hs_svc"]
    assert abs(E["l_min_uh"] - hs["l_uh"]) < 0.005, "the hot short's inductance bound reproduces L4-E11's"
    assert abs(hs["v"] - F["e_ov_off"][2]) < 1e-9 and abs(hs["lim"] - hs["idm"] * F["e_derate"]) < 0.05
    assert E["i2t_max"] < 0.1 * A["f_i2t"] and len(E["i2t"]) == 5, "every start and fault pulse far under F1's melting I2t"
    assert E["tc_break"] > A["tc_max"] and F["e_q7_tj"] > A["tj_max"], "the derating carried to a part rated hotter stays conservative"
    assert F["e_ov_off"][0] > A["cs101_top"] and F["e_ov_off"][2] < A["d10_cold_vbr"] < F["SMCJ40A"]["vbr_min"], "D-02 on the selected OV"
    assert F["e_oc"][2] <= A["f_allow"] and F["e_svc"][1] < F["e_oc"][0], "the breaker under F1's column, the service under the breaker"
    rows = {r["id"]: r for r in _C["R"]}
    sel = [c for c in rows["IF-05"]["checks"] if c.scope == "selected"]
    assert not any("LM5069" in c.what or "R24" in c.what for c in sel), "no LM5069 check counts toward the selected entry"
    hot = [c for c in sel if "hard short in service" in c.what][0]
    assert hot.met is None and hot.cls == "CONDITIONAL" and "E11-20" in hot.src
    starts = [c for c in sel if "of the chart" == c.unit]
    assert len(starts) == 3 and all(c.met and c.b == 1.0 for c in starts)
    assert _C["st"]["IF-05"][1] == "CONDITIONAL" and _C["st"]["IF-11"][1] == "CONDITIONAL"
    # the update round left no row NOT MET; since set 27 IF-01 reads NOT MET on the two known single faults D-10 and D-11 only
    assert [k for k, v in _C["st"].items() if v[1] == "NOT MET"] == ["IF-01"], "only IF-01 reads NOT MET"
    bad = [c for c in rows["IF-01"]["checks"] if c.scope == "selected" and c.met is False]
    assert len(bad) == 2 and "D-10" in bad[0].what and "D-11" in bad[1].what, "IF-01 fails only on D-10 and D-11"
    sec = _C["text"].split("12. THE UPDATE ROUND")[1]
    assert "new material defects from E11-19: none" in sec and "E11-20" in sec
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert "E11-20" in reg["R-134"][3] and "2.08" in reg["R-134"][2]


def _rows_of(commit, path, header):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, path)], capture_output=True)
    if r.returncode != 0:
        raise Skip("%s is not at %s in this checkout" % (path, commit))
    return _M().md_table(r.stdout.decode("utf-8"), header)


def t_the_register_carries_the_accepted_records_items():
    m = _M()
    reg = _md_rows(REG, "| ID | Kind |")
    ids = {r[0] for r in reg}
    for eid, _kind, _owner in _C["F"]["e11_items"]:
        if eid in m.E11_ANSWERED_HERE:
            assert eid in _C["text"].split("12. THE UPDATE ROUND")[1], "%s is not answered in out 12" % eid
            continue
        assert any(re.search(r"\b%s\b" % eid, r[3]) for r in reg), "%s is not in the register's From column" % eid
    ow = {o["id"] for o in m.OWNER_ITEMS}
    for commit, path, header, mp in ((m.FROM_COMMIT["l4e10md"], "v2/docs/records/l4e10/L4E10-CELL-THERMAL.md", "| Owner | Item |", m.E10_MAP),
                                     (m.FROM_COMMIT["l4e12md"], "v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md", "| Owner | Item |", m.E12_MAP)):
        owners = [r[0] for r in _rows_of(commit, path, header)]
        assert owners and set(owners) == set(mp), "%s: its owner rows %s are not the map's" % (path, sorted(set(owners) ^ set(mp)))
        for refs in mp.values():
            for x in refs:
                assert (x in ids) if x.startswith("R-") else (x in ow) if x.startswith("OW-") else x.startswith("this record"), x
    assert len(reg) == len(ids) >= 139


def t_the_thermal_line_is_l4e12s_binding_line():
    m = _M()
    F = _C["F"]
    assert abs(F["e5_hold_wb"] / (F["e5_line"] - F["e5_amb"]) - F["gc"]) < 0.0005, "the line from E5's heat under the hold and the ballasts"
    assert abs(F["e3o_wb"] / (F["e5_line"] - F["e3o_amb12"]) - F["g_e3o"]) < 0.0005, "E3-O's line from the heat stage and the ballasts"
    assert F["g_e3o"] < F["gc"] < F["g_a"] and F["th1"] < F["lo01a_ball"] < F["gc"]
    text = _C["text"]
    bud = text.split("8. THE ENDURANCE")[1].split("9. THE CLOSURE")[0]
    assert "THE THERMAL BUDGET" in bud and "%s W/K" % m.fmt(F["gc"]) in bud and "%s W" % m.fmt(round(F["e5_hold_wb"], 3)) in bud
    assert "THE ENERGY BUDGET" in bud
    u2 = [c for c in m.CHOICES if c["id"] == "U-02"][0]
    assert m.fmt(F["gc"]) in u2["constraint"] and "CFL-002" in u2["evidence"][2]


def t_the_owner_items_are_kept_apart_with_their_documents_pinned():
    m = _M()
    reg = _md_rows(REG, "| ID | Kind |")
    assert not any(r[0].startswith("OW-") for r in reg), "an owner item is not a register task"
    labels = " ".join(lab for o in m.OWNER_ITEMS for _k, lab in o["docs"])
    for name in ("Topwell", "Pervasive Displays", "Sensirion", "Analog Devices", "Milliohm", "Vishay", "Texas Instruments", "Eaton",
                 "Ground Control", "NiceRF", "Bulgin", "SunPower", "Solbian"):
        assert name in labels, "the owner's list misses %s" % name
    for o in m.OWNER_ITEMS:
        for key, _lab in o["docs"]:
            assert key in m.PINS and re.fullmatch(r"[0-9a-f]{64}", m.PINS[key][1]), key
            assert m.PINS[key][1][:16] in _C["text"], "the output does not print %s's pin" % key
    assert "CFL-002" in m.OWNER_ITEMS[0]["what"] and all(x in m.OWNER_ITEMS[0]["what"] for x in ("A, ", "B, ", "C, "))
    page = _md_rows(PAGE, "| Item | The decision or action |")
    assert [r[0] for r in page] == [o["id"] for o in m.OWNER_ITEMS] and all(r[1] == o["what"] for r, o in zip(page, m.OWNER_ITEMS))


def t_u03_is_a_downstream_unit_selection_and_the_gate_stays_not_closed():
    m = _M()
    F = _C["F"]
    for key in ("l4e13", "l4e13md", "l4e13chk", "l4e13chk4", "cl_sunpower", "cl_solbian"):
        rel, sha = m.PINS[key]
        assert rel.startswith("v2/docs/records/l4e13/") and key not in m.FROM_COMMIT and re.fullmatch(r"[0-9a-f]{64}", sha), key
        assert sha[:16] in _C["text"].split("1. THE MAKERS")[0], "%s's pin is not printed" % key
    u3 = [c for c in m.CHOICES if c["id"] == "U-03"][0]
    assert u3["class"] == m.DOWNSTREAM == "CONDITIONAL DOWNSTREAM UNIT SELECTION (PANEL-ACC)" and u3["rows"] == ["IF-01"]
    assert [c["id"] for c in m.CHOICES if c["class"] == m.ARCH] == ["U-01", "U-02", "U-04"]
    for fig in ("%s" % F["e13_a1"], "%.3f" % F["e13_a1_lim"], "%s" % F["e13_win"][0], "%s" % F["e13_win"][1], "%s" % F["e13_a3"][2]):
        assert fig in u3["constraint"], fig
    assert F["e13_a1"] + F["e13_a1_margin"] == F["e13_a1_lim"] and F["e13_a3"][1] <= 10.0 < F["e13_a3"][2]
    assert "not the topology" in u3["overturns"] and "L4E13-06" in u3["overturns"]
    for g in m.GATE:
        assert "U-03" not in g["choices"], "criterion %d names U-03 as a choice that could overturn the architecture" % g["n"]
    bad = copy.deepcopy(m.GATE)
    bad[4]["choices"] = bad[4]["choices"] + ["U-03"]
    assert m.gate_violations(bad, _C["st"]), "naming the downstream selection in criterion 5 must be refused"
    bad = copy.deepcopy(m.GATE)
    bad[0]["choices"] = ["U-02", "U-04"]
    assert m.gate_violations(bad, _C["st"]), "criterion 1 leaving out an architecture-level choice must be refused"
    rows = {r["id"]: r for r in _C["R"]}
    a1 = [c for c in rows["IF-01"]["checks"] if "PANEL-ACC A-1" in c.what][0]
    assert a1.a == F["e13_a1"] and a1.b == F["e13_a1_lim"] and a1.met and a1.cls == "CONDITIONAL" and "R-35" in a1.src
    a3c = [c for c in rows["IF-01"]["checks"] if "A-3(c)" in c.what][0]
    assert a3c.met is None and "R-148" in a3c.src
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert "PANEL-ACC" in reg["R-35"][2] and reg["R-35"][4] == "Layer 6 components" and "25.000 V" in reg["R-35"][5]
    assert "trace rerun" in reg["R-52"][2] and "13.82 A" in reg["R-148"][5] and "n at or under 2" in reg["R-149"][5]
    assert "8.1817 A" in reg["R-29"][5]
    assert len(reg) >= 139
    ho = {r[0]: r for r in _md_rows(HAND, "| ID | Target |")}
    assert "13.82 A" in ho["LH-02"][2] and "R-148" in ho["LH-02"][2] and len(ho) == 11, "J_SOLAR's rating amends LH-02, no new row"
    ow = {o["id"]: o for o in m.OWNER_ITEMS}
    assert "SunPower SPR-E-Flex-100" in ow["OW-6"]["what"] and ow["OW-6"]["docs"][0][0] == "l4e13md"
    sec = _C["text"].split("13. UPDATE ROUND 3")[1]
    assert "the gate: NOT CLOSED" in sec and "U-01, U-02, U-04" in sec
    assert F["e13_day_e7r"] == F["e7r_day"][1] and F["e13_reg"][0] == F["reg"][0] and F["e13_trip"] == F["bs_trip"]
    assert F["e13_reg"][0] < F["e13_reg"][1] < F["e13_trip"][1] < F["e13_a3"][0] <= 10.0, "A-3(a)'s ordering"
    assert F["e13_static"][0] == F["static_bound"] and F["e13_corner"] == F["reg_corner"]
    for fig in ("%s" % F["e13_reg"][1], "%s" % F["e13_trip"][1], "%s" % F["static_bound"]):
        assert fig in u3["constraint"], fig
    assert "%.1f Wh a day under L4-E7R's accepted regulation" % F["e13_day_e7r"] in sec
    assert "336.6 Wh at the nominal hold under L4-E7R" in reg["R-52"][5] and "96.25" not in reg["R-52"][5]
    assert "L4-E7R's regulation and backstop" in reg["R-35"][5] and "2.9337 A" in ho["LH-02"][2]
    assert "Layer 4's power architecture closes: NO" in _C["text"]
    page = open(PAGE, encoding="utf-8").read()
    assert "pending L4-E13" not in page and "L4-E13 (U-03) is pending" not in page


def t_the_entry_draft_applies_on_the_hotswap_draft_and_not_before_it():
    m = _M()
    need(HS, "the hot-swap draft")
    need(GEN_E, "board E's generator")
    cin = os.path.join(ROOT, "v2", "docs", "records", "d8dec31", "apply_gen_sch_e_cin.py")
    need(cin, "d8dec31's input capacitor draft")
    need(NET_E, "board E's netlist")
    with tempfile.TemporaryDirectory() as td:
        got = {}
        for commit, rel in ((m.FROM_COMMIT["l4e7r"], "v2/docs/records/l4e7/apply_gen_sch_e_u5_grade.py"),
                            (m.FROM_COMMIT["l4e7r"], "v2/docs/records/l4e7/apply_gen_sch_e_hold.py"),
                            (m.FROM_COMMIT["l4e7r"], "v2/docs/records/l4e7/apply_gen_sch_e_input_limit.py"),
                            (m.FROM_COMMIT["l4e7r"], "v2/docs/records/l4e7/apply_gen_sch_e_backstop.py"),
                            (m.FROM_COMMIT["e11entry"], "v2/docs/records/l4e11/apply_gen_sch_e_entry.py"),
                            (m.FROM_COMMIT["e11entry"], "v2/docs/records/l4e11/apply_gen_sch_e_timer.py")):
            rb = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
            if rb.returncode != 0:
                raise Skip("%s is not at %s in this checkout" % (rel, commit))
            got[os.path.basename(rel)] = os.path.join(td, os.path.basename(rel))
            open(got[os.path.basename(rel)], "wb").write(rb.stdout)
        entry, timer = got.pop("apply_gen_sch_e_entry.py"), got.pop("apply_gen_sch_e_timer.py")
        x, y = os.path.join(td, "x.py"), os.path.join(td, "y.py")
        shutil.copy(GEN_E, x)
        shutil.copy(GEN_E, y)
        assert _run(entry, y, "--write").returncode == 3, "the entry draft must refuse a generator without the hot-swap draft"
        assert subprocess.run([sys.executable, "-B", cin, x, NET_E], capture_output=True).returncode == 0
        for p in [Q1, F1] + list(got.values()) + [HS, entry]:
            r = _run(p, x, "--write")
            assert r.returncode == 0, "%s in the release order: %s" % (os.path.basename(p), r.stderr)
        assert _run(timer, x, "--write").returncode == 3, "the LM5069's timer draft must refuse the selected entry"
        after = open(x, encoding="utf-8").read()
        assert "TPS48110AQDGXRQ1" in after and "CSD19536KTT" in after and "LM5069MM-2 hot-swap controller" not in after


def t_round5_the_dependency_rounds_restate_the_choices_and_the_register():
    m = _M()
    F = _C["F"]
    r5 = F["r5"]
    for key, commit in (("l4e10", "1c321773"), ("l4e10md", "1c321773"), ("cl_topwell", "e464ff88"), ("l4e11", "5aa18a69"),
                        ("l4e11md", "5aa18a69"), ("l4e12", "589f18ac"), ("l4e12md", "589f18ac")):
        assert m.FROM_COMMIT[key] == commit, key
        rel, sha = m.PINS[key]
        rb = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
        if rb.returncode != 0:
            raise Skip("%s is not at %s in this checkout" % (rel, commit))
        # the pin is the file at its accepted commit, or the tree's file after an integration re-pin (set 27: L4-E10's and
        # L4-E12's outputs re-pinned to each other's integrated pages, only their pin lines changed); the script refuses any other
        tree = open(os.path.join(ROOT, rel), "rb").read() if os.path.exists(os.path.join(ROOT, rel)) else b""
        assert sha in (hashlib.sha256(rb.stdout).hexdigest(), hashlib.sha256(tree).hexdigest()), "%s is not pinned at %s" % (key, commit)
    for key in ("l4e10chk4", "l4e12chk4", "l4e11chk4", "th1proc", "cl_tiq"):
        assert key in m.PINS and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    arch = [c for c in m.CHOICES if c["class"] == m.ARCH]
    assert [c["id"] for c in arch] == ["U-01", "U-02", "U-04"]
    for c in m.CHOICES:
        assert c["question"] and c["supplier"] and c["fallback"] and len(c["evidence"]) == 3 and all(c["evidence"]), c["id"]
    exp = m.round5_expect(F)
    for c in arch:
        whole = " ".join([c["question"], c["constraint"], m.evidence_text(c), c["supplier"], c["fallback"], c["overturns"]])
        for s in exp[c["id"]]:
            assert " ".join(s.split()) in whole, (c["id"], s)
    u1, u2, u4 = arch
    assert "%s Wh (%s h) against the 35E's %s Wh" % (r5["hl"] + (r5["e35"][0],)) in u1["constraint"]
    assert abs(float(r5["e35"][0]) - float(r5["hl"][0]) - float(r5["growth"])) < 1e-9
    assert "session's" in u2["fallback"] and "down to %s" % r5["f4"][3] in u2["fallback"] and "the remaining option is the owner's" in u2["fallback"]
    assert float(r5["f4"][3]) < float(r5["f4"][1]) < F["gc"] < float(r5["pass"][0])
    assert "arrangement (A) with its dependency round stands" in u4["fallback"] and r5["remedy"][1:] == ("D1", "D3")
    assert "CFL-002" in u2["evidence"][2] and "OW-8" in u2["evidence"][2] and "OW-7" in u4["evidence"][2]
    bad = copy.deepcopy(m.CHOICES)
    for c in bad:
        if c["id"] == "U-02":
            c["fallback"] = c["fallback"].replace(r5["f4"][3], "1.000")
    whole = " ".join(" ".join([c["question"], c["constraint"], m.evidence_text(c), c["supplier"], c["fallback"], c["overturns"]]) for c in bad if c["id"] == "U-02")
    assert any(" ".join(s.split()) not in whole for s in exp["U-02"]), "a choice quoting another fallback figure must be caught"
    bad = copy.deepcopy(m.CHOICES)
    bad[1]["evidence"] = bad[1]["evidence"][:2]
    saved = m.CHOICES
    try:
        m.CHOICES = bad
        assert m.gate_violations(m.GATE, _C["st"]), "a choice without its evidence by vendor, physical and owner must be refused"
    finally:
        m.CHOICES = saved
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert len(reg) >= 146 and [x for x in reg if 150 <= int(x[2:]) <= 156] == ["R-150", "R-151", "R-152", "R-153", "R-154", "R-155", "R-156"]
    k, what, frm, own, acc = r5["fanrow"]
    assert reg["R-150"][1] == k and what in reg["R-150"][2] and own.startswith(reg["R-150"][4]) and acc.lower() in reg["R-150"][5].lower()
    assert "T-H1-PROCEDURE-DRAFT.md" in reg["R-151"][2] and "%s W/K" % r5["pass"][0] in reg["R-151"][5] and reg["R-151"][4] == "TEST-PLAN owner"
    assert "E11-24" in reg["R-152"][3] and "%s ms" % r5["hold_ms"][0] in reg["R-152"][5] and reg["R-152"][6] == "MISSING DRAFT"
    assert "E11-26" in reg["R-153"][3] and "E11-25" in reg["R-114"][3] and "TI-QUESTIONS.md" in reg["R-114"][2]
    assert "U-01" in reg["R-154"][2] and reg["R-154"][4] == "firmware owner" and r5["ranges"][0][7] in reg["R-154"][2]
    for rid, item in (("R-102", 8), ("R-139", 5), ("R-155", 10), ("R-156", 1)):
        assert "FINDINGS-LEDGER item %d" % item in reg[rid][3], (rid, item)
    assert "per-can ripple bound" in reg["R-102"][5] and "worst phase" in reg["R-102"][5]
    assert "61 s" in reg["R-139"][5] and "intervals" in reg["R-155"][2] and reg["R-156"][6] == "OWED" and "L4-E7's surge round" in reg["R-156"][2]
    assert reg["R-156"][4] == "Layer 8 board E generator owner" and "TRN-001" in reg["R-156"][5]
    ow = {o["id"]: o for o in m.OWNER_ITEMS}
    assert [k for k, _ in ow["OW-7"]["docs"]] == ["ti_review", "cl_tiq"] and [k for k, _ in ow["OW-8"]["docs"]] == ["th1proc"]
    assert "ten questions" in ow["OW-2"]["what"] and r5["tw_q"] == list(range(1, 11))
    assert not any(k in ("cl_topwell", "ti_review") for k, _ in ow["OW-4"]["docs"]), "Topwell's and TI's requests are their own items"
    sec = _C["text"].split("14. UPDATE ROUND 5")[1]
    assert "the gate: NOT CLOSED" in sec and "%d items" % len(reg) in sec and "Layer 4's power architecture closes: NO" in _C["text"]
    page = open(PAGE, encoding="utf-8").read()
    assert "**Under U-01's recommended cell** (CONDITIONAL, not taken): usable %s Wh against the 35E's %s Wh" % (m.fmt(F["cell_usable"][1]), m.fmt(F["cell_usable"][0])) in page, \
        "the bullet L4-E10 reads back keeps its first chain's figures"


def t_consolidation_the_one_diagram_covers_every_interface_row():
    m = _M()
    F, st = _C["F"], _C["st"]
    N, E, C, NP = m.cons_diagram(F, st)
    svg = m.cons_svg(N, E, C, NP, st)
    path = os.path.join(REC, m.SVG_NAME)
    assert open(path, encoding="utf-8").read() == svg, "the committed diagram is not the script's"
    assert hashlib.sha256(svg.encode("utf-8")).hexdigest()[:16] in _C["text"].split("15. THE CONNECTED DESIGN")[1].split("\n")[0]
    assert sorted({r for e in E for r in e[3]}) == sorted(st), "a power edge for every interface row"
    blocks = {n[0] for n in N}
    assert all(e[1] in blocks and e[2] in blocks for e in E) and all(c[1] in blocks and c[2] in blocks for c in C)
    for src in ("SRC_PV", "SRC_DC", "SRC_USB"):
        assert src in blocks, "every source is in the figure, %s" % src
    for e in E:
        assert ">%s<" % e[3][0] in svg or ">%s/" % e[3][0] in svg or e[3][0] in svg, "%s's row is drawn on its edge" % e[0]
    for c in C:
        assert c[0] in svg and c[4] in ("firmware", "hardware", "firmware and hardware", "hardware (the gauge's own firmware)"), c[0]
    page = open(PAGE, encoding="utf-8").read()
    assert "](%s)" % m.SVG_NAME in page, "the page shows the one figure"
    edges = m.md_table(page, "| Edge |")
    assert [r[0] for r in edges] == [e[0] for e in E] + [x[0] for x in NP]
    for r, e in zip(edges, E):
        assert r[1:4] == [e[1], e[2], e[4]] and r[4] == ", ".join("%s (%s)" % (x, st[x][1]) for x in e[3]), e[0]
    ctl = m.md_table(page, "| Control |")
    assert [tuple(r) for r in ctl] == [tuple(c) for c in C], "the page's control table is the script's"
    blk = m.md_table(page, "| Block |")
    assert [r[0] for r in blk] == [n[0] for n in N] and all(r[2] == "; ".join(n[4]) for r, n in zip(blk, N))


def t_consolidation_one_budget_with_pinned_inputs_and_the_reconciliation():
    m = _M()
    F, st = _C["F"], _C["st"]
    for key in ("budget", "trace", "replay", "tablet", "l4e10", "l4e12", "l4e13", "l4e11", "l4e7r", "l4e8", "hwfw"):
        assert key in m.PINS and re.fullmatch(r"[0-9a-f]{64}", m.PINS[key][1]) and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    for _rid, _q, figs, _k, _w in m.RECON:
        for val, key, _b in figs:
            assert key in m.PINS and re.search(r"(?<![\d.])%s(?![\d])" % re.escape(val), m._C_TEXT[key]), (val, key)
    named = {v for _r, _q, figs, _k, _w in m.RECON for v, _k2, _b in figs}
    for a, b in (("107.9", "108.1"), ("350.0", "336.6"), ("2.9337", "2.9318"), ("90.2", "90.4")):
        assert a in named and b in named and any({a, b} <= {v for v, _k2, _b in figs} for _r, _q, figs, _k, _w in m.RECON), (a, b)
    page = open(PAGE, encoding="utf-8").read()
    T = m.cons_budget_tables(F, _C["D"], st)
    for head, lines in T.items():
        rows = m.md_table(page, head)
        assert rows == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], "the page's %s table is not the script's" % head.strip()
    modes, energy, ef, heat = m.cons_budget(F, st)
    ids = [e[0] for e in energy]
    assert any(i.startswith("B") for i in ids) and any(i.startswith("S") for i in ids) and any(i.startswith("P") for i in ids), "battery-only, solar-assisted, the proposal"
    assert all("PROPOSAL" in e[1] or "proposed" not in e[1] for e in energy) and "PROPOSAL" in energy[ids.index("P1")][1]
    assert ef["steady"] == F["steady"][2] and abs(ef["deficit"] - (F["idle"][1] - F["steady"][2])) < 1e-9
    assert [mm[0] for mm in modes] == ["M1", "M2", "M3", "M4", "M5", "M6"]
    assert "NOT MET" in _C["text"].split("16b ENERGY")[1] and "A charger change does not close it" in _C["text"]
    assert any(h[2] == F["e5_hold_wb"] and "BINDING" in h[3] for h in heat), "the binding line in the heat budget"


def t_consolidation_the_change_list_covers_every_apply_script_in_order():
    m = _M()
    reg = _md_rows(REG, "| ID | Kind |")
    ch = m.cons_changes(reg)
    impl = {r[0] for r in reg if r[1] == "IMPLEMENTATION"}
    assert impl <= {c[2] for c in ch} and len({c[2] for c in ch}) == len(ch), "every implementation row once"
    scripts = " ".join(c[4] for c in ch)
    for p in glob.glob(os.path.join(ROOT, "v2", "docs", "records", "l4e*", "apply_*.py")) + [os.path.join(ROOT, "v2", "docs", "records", "d8dec31", "apply_gen_sch_e_cin.py")]:
        assert os.path.basename(p) in scripts, "%s is not in the change list" % os.path.relpath(p, ROOT)
    assert not any("APPLIED" == c[8].split(" ")[0] for c in ch), "nothing is applied"
    pos = {c[2]: c[0] for c in ch}
    assert pos["R-01"] < pos["R-04"] and pos["R-01"] < pos["R-07"] and pos["R-94"] < pos["R-123"] and pos["R-17"] < pos["R-13"]
    for c in ch:
        assert c[3] and c[5] and c[6] and c[7], "each change names its board, dependency, guard and what it changes: %s" % c[2]
    page = m.md_table(open(PAGE, encoding="utf-8").read(), "| # | Step | Row |")
    assert page == [["%d" % c[0]] + [str(x) for x in c[1:]] for c in ch], "the page's change list is the script's"
    bad = list(m.CHANGE_ORDER)
    i, j = [k for k, c in enumerate(bad) if c[1] in ("R-94", "R-123")]
    bad[i], bad[j] = bad[j], bad[i]
    saved = m.CHANGE_ORDER
    try:
        m.CHANGE_ORDER = bad
        try:
            m.cons_changes(reg)
            raise AssertionError("the entry before the hot swap must be refused")
        except SystemExit:
            pass
    finally:
        m.CHANGE_ORDER = saved


def t_consolidation_the_operating_behaviour_ties_each_row_to_a_record_and_a_figure():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    B = m.cons_behaviour(F, D, st)
    assert sorted(B) == ["4a", "4b", "4c", "4d", "4e", "4f", "4g"]
    for key, rows in B.items():
        assert rows, key
        for r in rows:
            assert r[-1].strip(), "%s %s names no record" % (key, r[0])
            assert re.search(r"\d", " ".join(r[1:-1])), "%s %s carries no figure" % (key, r[0])
    page = open(PAGE, encoding="utf-8").read()
    for head, lines in m.cons_behaviour_tables(F, D, st).items():
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], head
    a = " ".join(r[0] for r in B["4a"])
    for ev in ("plug in", "plug out", "dawn", "dusk", "pack connected", "pack disconnected"):
        assert ev in a, ev
    assert any("graceful" in r[0] and "%.2f V" % F["cb"]["bh"]["graceful"] in r[2] for r in B["4d"])
    assert any("stalls" not in r[0] and "watchdog" in r[1] for r in B["4g"])


def t_consolidation_the_handover_the_exit_and_the_status():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    page = open(PAGE, encoding="utf-8").read()
    for name in ("cons_handover_tables", "cons_exit_table"):
        for head, lines in getattr(m, name)(F, D, st).items():
            assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], head
    reg = _md_rows(REG, "| ID | Kind |")
    hand = m.cons_handover(reg)
    assert sum(int(r[2].split(":")[0]) for r in hand) == len(reg), "every register row reaches a later layer once"
    assert all(r[4].endswith("APPLIED 0") for r in hand)
    ex = m.cons_exit(F)
    assert [e[0] for e in ex] == [c["id"] for c in m.CHOICES if c["class"] == m.ARCH]
    for e in ex:
        assert e[1] in (m.QUALIFICATION, m.CONDITION, m.QUALIFICATION_ONCE, m.SUPPORTED) and all(x.strip() for x in e[2:]), e[0]
    assert m.OWNER_DEFINITION in page.replace("\n", " ").replace("  ", " ") or m.OWNER_DEFINITION[:80] in page.replace("\n", " ")
    assert "**Status: %s.**" % m.STATUS in page and m.STATUS in _C["text"].split("20. THE EXIT")[1]
    if any(e[1] == m.CONDITION for e in ex):
        assert "power closure is not reached" in page and "NOT reached" in _C["text"]
    short = page.split("## In short\n")[1].split("\n## 1. ")[0].strip().split("\n")
    assert [s[2:] for s in short] == m.cons_in_short(F, D, st, reg), "the page's In short is the script's"
    assert "**Under U-01's recommended cell** (CONDITIONAL, not taken)" in page.split("## Appendix A.")[1], "the bullet L4-E10 reads stays, in the history"


def t_consolidation_the_charger_selection_and_the_thermal_verdict_are_carried():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    b1, tb = F["cb"]["b1"], F["cb"]["tb"]
    for key in ("l4e11chk5", "l4e12chk5", "e11charger"):
        assert key in m.PINS and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    assert m.FROM_COMMIT["l4e11"] == "5aa18a69" and m.FROM_COMMIT["l4e12"] == "589f18ac"
    N, E, C, NP = m.cons_diagram(F, st)
    blk = {n[0]: " ".join(n[4]) for n in N}
    assert "BQ25730" in blk["CHG"] and "Q39" in blk["VBAT"] and "%s" % b1["vsys_min"] in blk["VBAT"], "(B1) is in the figure"
    assert "Q39" in [e for e in E if e[0] == "P11"][0][4]
    reg = _md_rows(REG, "| ID | Kind |")
    ch = m.cons_changes(reg)
    pos = {c[2]: (c[0], c[1]) for c in ch}
    assert pos["R-157"][1] == "3a" and pos["R-157"][0] < pos["R-11"][0] and pos["R-157"][0] < pos["R-158"][0], "the charger in board A's round"
    assert pos["R-152"][1] == "ALT" and "apply_gen_sch_a_charger.py" in [c for c in ch if c[2] == "R-157"][0][4]
    for rid in ("R-163", "R-164", "R-165", "R-166", "R-111", "R-141"):
        assert rid in {r[0] for r in reg}, rid
    modes, energy, ef, heat = m.cons_budget(F, st)
    assert "%s W more on battery" % b1["q39_idle"][1] in modes[0][4]
    assert "%.3f h with (B1)'s Q39" % (F["a1_bat"][0] / (F["idle"][1] + b1["q39_idle"][1])) in energy[0][4]
    assert all(len(h) == 7 and h[5].strip() and h[6].strip() for h in heat), "each mode against the conservative bound and the approaches"
    assert "%s C" % tb["air_e3o"][0] in [h for h in heat if h[0] == "H3"][0][5] and "%.3f W/K" % tb["all_e3o"][3] in [h for h in heat if h[0] == "H3"][0][5]
    ex = {e[0]: e for e in m.cons_exit(F)}
    assert ex["U-04"][1] == m.QUALIFICATION_ONCE and ex["U-02"][1] == m.CONDITION and ex["U-01"][1] == m.SUPPORTED
    for a, _rise, _t, _w in (tb["bands"][0], tb["bands"][1], tb["bands"][4]):
        assert a in ex["U-02"][3], a
    assert "%s W/K" % tb["e5"][0] in ex["U-02"][2] and "%s V" % b1["vsys_min"] in ex["U-04"][4]
    u4 = [c for c in m.CHOICES if c["id"] == "U-04"][0]
    assert "(B1)" in u4["constraint"] and "arrangement (A) with its dependency round stands" in u4["fallback"]
    named = {v for _r, _q, figs, _k, _w in m.RECON for v, _k2, _b in figs}
    assert {"2.416", "2.462", "1.22", "0.566", "0000h"} <= named
    page = open(PAGE, encoding="utf-8").read()
    assert "T-H1 decides" in page and "(B1)" in page and "**Status: %s.**" % m.STATUS in page


def t_consolidation_the_cell_route_and_normal_operation():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    cb = F["cb"]
    u1, tb = cb["u1"], cb["tb"]
    for key in ("l4e10chk5", "cl_saft"):
        assert key in m.PINS and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    assert m.FROM_COMMIT["l4e10"] == "1c321773"
    modes, energy, ef, heat = m.cons_budget(F, st)
    e = {x[0]: x for x in energy}
    assert "PROPOSAL" in e["P4"][1] and "%s to %s h" % (m.fmt(u1["energy"][3]), m.fmt(u1["energy"][4])) in e["P4"][4], "the Saft route beside the ruled pack"
    assert e["B1"][1].startswith("ruled 35E") and "S4" in e and "CONDITIONAL on T-H1" in e["S4"][6]
    ex = {x[0]: x for x in m.cons_exit(F)}
    assert ex["U-01"][1] == m.SUPPORTED and "mock-up" in ex["U-01"][3] and "18 A for 60 s" in ex["U-01"][3] and "T-H1" in ex["U-01"][3]
    assert "UNSUITABLE" in ex["U-01"][2]
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    for rid in ("R-167", "R-168", "R-169"):
        assert reg[rid][7] == "U-01" and "Saft route" in reg[rid][2], rid
    rows, ceil, cols, stmt = m.cons_normal_op(F)
    assert [r[0] for r in rows] == ["N1", "N2", "N3", "N4", "N5"]
    q, ta = cb["idle_heat"], cb["env_top"]
    assert "%.3f W/K" % (q / (F["parts_hot"] - ta)) in stmt[1] and "deciding fact" in stmt[1]
    assert abs((float(F["r5"]["thr"][5]) - q / tb["env"][0]) - u1["charge_start"]) < 0.05, "the charge start on the bound reproduces L4-E10's"
    page = open(PAGE, encoding="utf-8").read()
    for head, lines in m.cons_normal_tables(F, D, st).items():
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], head
    for name, lines in (("normal", stmt), ("deciding", m.cons_deciding(F))):
        blk = page.split("<!-- gen:%s:begin -->" % name)[1].split("<!-- gen:%s:end -->" % name)[0].strip()
        assert blk == "\n\n".join(lines), name
    assert page.index("<!-- gen:deciding:begin -->") < page.index("**The owner's definition**"), "the deciding experiment heads the exit statement"


def t_consolidation_the_heat_rejection_result():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    cb = F["cb"]
    tb, hr = cb["tb"], cb["hr"]
    th, ap = hr["thr"], hr["ap"]
    assert "l4e12chk6" in m.PINS and m.PINS["l4e12chk6"][1][:16] in _C["text"].split("1. THE MAKERS")[0]
    assert m.FROM_COMMIT["l4e12"] == "589f18ac" and "check 6" in m.COMMIT_LABEL["589f18ac"]
    # the readings: three thresholds at the profile's heat, ascending, their targets 10a's needs; six bands at E5's hold kept
    assert len(th) == 3 and [float(x[0]) for x in th] == sorted(float(x[0]) for x in th) and len(tb["bands"]) == 6
    assert abs(float(th[0][2]) - hr["g_need"]) < 5e-4 and (float(th[1][2]), float(th[2][2])) == hr["g_chg"]
    assert all(float(a) > float(tg) for a, _r, tg, _w in th), "each threshold is its target plus its uncertainty"
    assert abs(float(ap["all"][3]) + hr["best"][3] - hr["g_need"]) < 1.5e-3 and float(ap["all"][3]) < hr["g_need"]
    assert max(float(ap[k][3]) for k in ap) == float(ap["all"][3]), "the combined route is the best of the approaches"
    assert hr["alt"][0] + hr["alt"][2] == hr["alt"][1] or abs(hr["alt"][0] + hr["alt"][2] - hr["alt"][1]) < 1e-6
    assert hr["day"] == cb["day_air"] and abs(hr["q"] - cb["idle_heat"]) < 0.05
    # the exit: the precise bounded question and its executable path at the top
    dec = m.cons_deciding(F)
    assert dec[0].startswith("**The precise bounded question (U-02)") and ap["none"][3] in dec[0] and "%.3f" % tb["cap"][0] in dec[0]
    assert dec[1].startswith("**Its executable resolution path.**")
    for x in [a for a, _r, _t, _w in th] + ["R-170 to R-172", "%s W" % m.fmt(hr["heaters"]), "%s W" % m.fmt(hr["alt"][0]), "requirement change", "ALTERNATIVE duty cycle"]:
        assert x in dec[1], x
    assert dec[1].index(th[0][0]) < dec[1].index("R-170 to R-172") < dec[1].index("ALTERNATIVE duty cycle"), "the path runs P1, the route, the owner"
    assert all(a in dec[2] for a, _r, _t, _w in th + tb["bands"]) and "supersedes" in dec[2], "both points' readings stated"
    ex = {e[0]: e for e in m.cons_exit(F)}
    assert ex["U-02"][1] == m.CONDITION and th[0][0] in ex["U-02"][3] and "R-170 to R-172" in ex["U-02"][3] and ap["all"][3] in ex["U-02"][4]
    assert "589f18ac" in m.EXIT_PENDING["U-02"]
    # the combined route's three items: register rows conditional on the reading, in the change list at Layer 7's step
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    for rid in ("R-170", "R-171", "R-172"):
        r = reg[rid]
        assert r[1] == "IMPLEMENTATION" and r[4] == "Layer 7 mechanical" and r[6] == "OWED" and r[7] == "8, U-02", rid
        assert r[2].startswith("Under a T-H1 reading under %s W/K at the profile's heat only" % th[0][0]) and "589f18ac" in r[3], rid
    ch = {c[2]: c for c in m.cons_changes(list(reg.values()))}
    assert all(ch[r][1] == "8" and "conditional on T-H1's reading" in ch[r][6] for r in ("R-170", "R-171", "R-172"))
    saved = m.CHANGE_ORDER
    try:
        m.CHANGE_ORDER = [c for c in saved if c[1] != "R-171"]
        try:
            m.cons_changes(list(reg.values()))
            raise AssertionError("a change list without the route's item must be refused")
        except SystemExit:
            pass
    finally:
        m.CHANGE_ORDER = saved
    acc = reg["R-104"][5]
    assert acc.index(th[0][0]) < acc.index(tb["bands"][0][0]) and "42.4 W" in acc and "R-170 to R-172" in acc, "R-104 runs P1 first, P2 after"
    assert all(a in acc for a, _r, _t, _w in th) and all(b[0] in acc for b in (tb["bands"][0], tb["bands"][1], tb["bands"][4]))
    # the handover: T-H1's points in order, both stated, the page equal to the script
    rows, note = m.cons_th1(F)
    assert [r[0].split(",")[0] for r in rows][:5] == ["P1", "P1", "P1", "P1R", "P2"] and rows[-1][0] == "P3 to P8"
    assert [r[2] for r in rows if r[0].startswith("P1,")] == ["at least %s W/K (%s K rise)" % (a, rr) for a, rr, _t, _w in th]
    assert [r[2] for r in rows if r[0].startswith("P2, then")] == ["at least %s W/K (%s K rise)" % (a, rr) for a, rr, _t, _w in tb["bands"]]
    assert "supersedes" in note and "both points stated" in note
    page = open(PAGE, encoding="utf-8").read()
    blk = page.split("<!-- gen:th1:begin -->")[1].split("<!-- gen:th1:end -->")[0].strip()
    assert blk == note
    assert m.md_table(page, "| T-H1 point |") == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in m.cons_handover_tables(F, D, st)["| T-H1 point |"][2:]]
    # the budget's heat table: each approach's conductance beside the bound
    modes, energy, ef, heat = m.cons_budget(F, st)
    h1 = [h for h in heat if h[0] == "H1"][0]
    assert all(ap[k][3] in h1[6] for k in ap) and "%s W/K" % m.fmt(hr["g_need"]) in h1[6]
    h7 = [h for h in heat if h[0] == "H7"][0]
    assert ap["all"][5] in h7[6] and ap["all"][7] in h7[6] and th[1][0] in h7[6] and th[2][0] in h7[6]
    apr = m.cons_approaches(F)
    assert [r[0] for r in apr] == ["none", "a2", "a3", "b", "ba", "c", "all", "need"] and all(ap[r[0]][3] in r[2] for r in apr[:-1])
    for head in ("| Approach | ", "| Heat | "):
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in m.cons_budget_tables(F, D, st)[head][2:]], head
    named = {v for _r, _q, figs, _k, _w in m.RECON for v, _k2, _b in figs}
    assert {"0.767", "1.509", "1.516", "43.413"} <= named, "the reconciliation names the figures that differ"
    rows_n, ceil, cols, stmt = m.cons_normal_op(F)
    assert any(th[0][0] in c for c in cols) and any(ap["all"][3] in c for c in cols) and th[0][0] in stmt[1]
    assert "the +70 C class" == ceil[2][0] and ceil[2][cols.index([c for c in cols if th[0][0] in c][0]) + 2] == "40.0 C", "P1's first threshold holds the class to +40 C"
    short = page.split("## In short\n")[1].split("\n## 1. ")[0]
    assert th[0][0] in short and ap["all"][3] in short


def t_consolidation_the_panel_lead_surge():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    sv = F["sv"]
    # the verdicts as L4-E7 printed them, against REQ-016's criterion
    assert sv["lim_drawn"] < sv["d1"][0] <= sv["lim"] and sv["lim_drawn"] < sv["d2"][0] <= sv["lim"], "CS116 and CS115 inside the drafted 50 V, over the drawn 35 V"
    assert all(pw > sv["d4_cap"][0] for _n, _v, _i, pw in sv["d4_rows"]) and len(sv["d4_rows"]) == 4, "a 36 V source over D4's capability at every breakdown"
    assert sv["d5"][2] < 0.2 and sv["d4_cold"] < sv["src"][1] and sv["u18"] == (40.0, F["u18_vin"])
    # the known open defects and IF-01
    de = {d["id"]: d for d in m.DEFECTS}
    for did in ("D-10", "D-11"):
        assert de[did]["state"] == "OPEN" and "pending" in de[did]["resolution"] and "R-173" in de[did]["resolution"] and de[did]["rows"] == ["IF-01"]
    assert de["D-12"]["state"].startswith("RESOLVED") and "R-21" in de["D-12"]["resolution"]
    assert st["IF-01"][1] == "NOT MET"
    g2 = [g for g in m.GATE if g["n"] == 2][0]
    assert g2["verdict"] != "PASS" and all(x in g2["constraint"] for x in ("D-10", "D-11", "R-173", "no remedy selected here"))
    # the register and the change list
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    r156, r173, r174 = reg["R-156"], reg["R-173"], reg["R-174"]
    assert r156[6] == "OWED" and "INA169" in r156[5] and "75 V" in r156[5] and "INA250" not in r156[5], "R-156's U18 corrected"
    assert r173[1] == "IMPLEMENTATION" and r173[4] == "Layer 8 board E generator owner" and r173[6] == "PENDING" and r173[7] == "4d"
    assert "No remedy is selected here" in r173[2] and "SMCJ36A" in r173[2] and "disconnect" in r173[2]
    assert r174[1] == "TEST" and m.LAYER_OF[r174[4]] == "8" and "CS116" in r174[2] and "CS115" in r174[2] and "M1 to M5" in r174[2]
    ch = m.cons_changes(list(reg.values()))
    pos = {c[2]: c[0] for c in ch}
    assert pos["R-21"] < pos["R-173"] < pos["R-22"] and pos["R-98"] < pos["R-173"]
    saved = m.CHANGE_ORDER
    try:
        order = [c for c in saved if c[1] != "R-173"]
        i = [k for k, c in enumerate(order) if c[1] == "R-21"][0]
        m.CHANGE_ORDER = order[:i] + [c for c in saved if c[1] == "R-173"] + order[i:]
        try:
            m.cons_changes(list(reg.values()))
            raise AssertionError("the remedy's place before the drafted entry must be refused")
        except SystemExit:
            pass
    finally:
        m.CHANGE_ORDER = saved
    # the verdicts and the two remedies as L4-E7 names them; none selected
    verdicts, remedies, sel = m.cons_surge(F)
    assert [v[0] for v in verdicts][:5] == ["D1", "D2", "D3", "D4", "D5"]
    assert [r[0] for r in remedies] == ["(i)", "(ii)"] and remedies[0][3] == "not closed" and remedies[1][3] == "closed"
    assert "pending" in sel and "selects neither" in sel and "SELECTED" not in " ".join(" ".join(r) for r in remedies)
    text = _C["text"].split("23. THE PANEL LEAD'S SURGE")[1]
    assert "SELECTED" not in text and "decision 19" not in text
    page = open(PAGE, encoding="utf-8").read()
    assert "decision 19" not in page and "selected direction" not in page
    for head, lines in m.cons_surge_tables(F, D, st).items():
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], head
    blk = page.split("<!-- gen:surge:begin -->")[1].split("<!-- gen:surge:end -->")[0].strip()
    assert blk == sel
    # the exit carries the open defects beside U-01, U-02 and U-04
    exd = m.cons_exit_defects(F)
    assert [d[0] for d in exd] == ["D-10", "D-11", "D-12"] and all(d[2].startswith("OPEN") and "pending" in d[2] and "not yet a draft" in d[2] for d in exd[:2])
    assert m.md_table(page, "| Defect | Its fault |") == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in m.cons_exit_table(F, D, st)["| Defect | Its fault |"][2:]]
    sec6 = page.split("## 6. The exit statement")[1].split("## 7. ")[0]
    assert sec6.index("| U | Class |") < sec6.index("| Defect | Its fault |")
    assert "their remedy pending L4-E7's round" in _C["text"].split("20. THE EXIT")[1].split("21. IN SHORT")[0]
    short = page.split("## In short\n")[1].split("\n## 1. ")[0]
    assert "KNOWN OPEN DEFECTS" in short and "R-173" in short and "pending" in short and "**Status: %s.**" % m.STATUS in short


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
