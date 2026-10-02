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
row; the exit carries the defects beside U-01, U-02 and U-04. L4-E7's remedies (check 5): the guard's figures are read from L4-E7's
output; IF-01 no longer reads NOT MET, the faults staying visible as drawn; D-10 and D-11 read ADDRESSED IN DRAFTS; R-173 is the
drafted guard after the hot swap and the entry draft (a list putting it first is refused); the residual band is a layer 8 row. The owner's amendment of 14:20: L4-E12's reconciliation (check 7)
is read condition by condition and the framing of the profile at +40 C is withdrawn everywhere it stood (the exit's top, the heat
table, normal operation, the T-H1 points in the procedure's order, R-104 and the route's rows); L4-E10's comparison is the
budget's cell row as filed; the ledger's totals and its four still-open rows are in the exit; R-139 measures the reading's lag.
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


def _pin_held(m, key):
    """A property, not history: the key's selected commit is a labelled one, and the pinned bytes are the tree's file or that commit's."""
    rel, sha = m.PINS[key]
    p = os.path.join(ROOT, rel)
    in_tree = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == sha
    if key not in m.FROM_COMMIT:
        return in_tree
    if m.FROM_COMMIT[key] not in m.COMMIT_LABEL:
        return False
    if in_tree:
        return True
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (m.FROM_COMMIT[key], rel)], capture_output=True)
    return r.returncode == 0 and hashlib.sha256(r.stdout).hexdigest() == sha


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
    c11 = [c for c in rows["IF-11"]["checks"] if "M7's maker-stated line" in c.what][0]
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
    # no material defect is open: D-10 and D-11, open in set 27, are addressed in drafts since L4-E7's remedies (check 5)
    assert [d["id"] for d in m.DEFECTS if d["state"] == "OPEN"] == [], "no material defect is open"
    assert all(d["state"].startswith("ADDRESSED IN DRAFTS") for d in m.DEFECTS if d["id"] in ("D-10", "D-11"))
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
    assert not [k for k, v in _C["st"].items() if v[1] == "NOT MET"], "no interface row reads NOT MET (D-10 and D-11 addressed in drafts)"
    drawn = [c for c in rows["IF-01"]["checks"] if c.scope == "drawn" and c.met is False]
    assert any("D-10" in c.src for c in drawn) and any("D-11" in c.src for c in drawn), "the faults stay visible as drawn"
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
    # since L4-E12's fix round 2.159 W/K is M7's maker-stated line (the e-paper's row governs E5: a missing storage qualification)
    assert "%s W/K (at least" % m.fmt(F["gc"]) in u2["question"] and "CFL-002" in u2["evidence"][2]
    assert F["fx"]["modes"]["M7"]["stated"][1] == m.fmt(F["gc"]) and F["fx"]["modes"]["M7"]["ruled"][1] is None


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
    for key in ("l4e10", "l4e10md", "cl_topwell", "l4e11", "l4e11md", "l4e12", "l4e12md"):
        commit = m.FROM_COMMIT[key]
        assert _pin_held(m, key), key
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
    # L4-F04: the lines over the model are engineering and evidence tasks; only a demonstrated conflict goes to the owner
    assert m.CAT_MODEL.split(" OF ")[0] in u2["fallback"] and m.CAT_STORE in u2["fallback"] and m.CAT_CONFLICT in u2["fallback"] and "goes to the owner" in u2["fallback"]
    assert float(r5["f4"][3]) < float(r5["f4"][1]) < F["gc"] < float(r5["pass"][0])
    assert "arrangement (A) with its dependency round stands" in u4["fallback"] and r5["remedy"][1:] == ("D1", "D3")
    assert "CFL-002" in u2["evidence"][2] and "OW-8" in u2["evidence"][2] and "OW-7" in u4["evidence"][2]
    assert "only when a measurement demonstrates the conflict" in u2["evidence"][2]
    bad = copy.deepcopy(m.CHOICES)
    for c in bad:
        if c["id"] == "U-02":
            c["question"] = c["question"].replace(F["fx"]["modes"]["M1"]["ruled"][2], "1.000")
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
    # each required mode against its governing local limit (L4-E12's fix round): E5's heat under the hold is M7's, its maker-stated
    # alternative the +70 C line 2.159 W/K, the e-paper's row governing with no conductance
    assert [h[0] for h in heat] == ["M%d" % i for i in range(1, 10)] + ["A1", "A2", "A3"]
    h7 = [h for h in heat if h[0] == "M7"][0]
    assert abs(h7[2] - F["e5_hold_wb"]) < 1e-6 and "no conductance" in h7[4] and "%s W/K" % m.fmt(F["gc"]) in h7[6], "M7 in the heat budget"


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
        assert e[1] in (m.QUALIFICATION, m.CONDITION, m.CONDITION_U02, m.QUALIFICATION_ONCE, m.SUPPORTED) and all(x.strip() for x in e[2:]), e[0]
    assert m.OWNER_DEFINITION in page.replace("\n", " ").replace("  ", " ") or m.OWNER_DEFINITION[:80] in page.replace("\n", " ")
    assert "**Status: %s.**" % m.STATUS in page and m.STATUS in _C["text"].split("20. THE EXIT")[1]
    if any(e[1] in (m.CONDITION, m.CONDITION_U02) for e in ex):
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
    assert _pin_held(m, "l4e11") and _pin_held(m, "l4e12")
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
    fx = F["fx"]
    assert "%s W more on battery" % m.fmt(fx["pair_idle"][1]) in modes[0][4]
    assert "%.3f h with (B1)'s pair" % (F["a1_bat"][0] / (F["idle"][1] + fx["pair_idle"][1])) in energy[0][4]
    assert all(len(h) == 9 and all(x.strip() for x in h[3:]) for h in heat), "each mode with its lines, class and what remains"
    ex = {e[0]: e for e in m.cons_exit(F)}
    assert ex["U-04"][1] == m.QUALIFICATION_ONCE and ex["U-02"][1] == m.CONDITION_U02 and ex["U-01"][1] == m.SUPPORTED
    for p_ in ("M2 and M6", "M1, M4 and M3", "M7, M5, M8 and M9", "OW-10"):
        assert p_ in ex["U-02"][3], p_
    assert "%.3f W/K at K1's rise" % F["rc"]["capk1"][0] in ex["U-02"][4] and "%s V" % b1["vsys_min"] in ex["U-04"][4]
    u4 = [c for c in m.CHOICES if c["id"] == "U-04"][0]
    assert "(B1)" in u4["constraint"] and "arrangement (A) with its dependency round stands" in u4["fallback"]
    named = {v for _r, _q, figs, _k, _w in m.RECON for v, _k2, _b in figs}
    assert {"2.416", "2.462", "1.22", "0.566", "0000h"} <= named
    page = open(PAGE, encoding="utf-8").read()
    assert "T-H1 decides" in page and "(B1)" in page and "**Status: %s.**" % m.STATUS in page


def t_consolidation_the_cell_route_and_normal_operation():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    cb, rc = F["cb"], F["rc"]
    u1, tb = cb["u1"], cb["tb"]
    for key in ("l4e10chk5", "l4e10chk6", "cl_saft"):
        assert key in m.PINS and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    assert _pin_held(m, "l4e10")
    # the battery comparison as the budget's and the handover's cell row
    modes, energy, ef, heat = m.cons_budget(F, st)
    e = {x[0]: x for x in energy}
    assert "PROPOSAL" in e["P4"][1] and "%s to %s h" % (m.fmt(rc["saft_use"][2]), m.fmt(rc["saft_use"][3])) in e["P4"][4], "the Saft route beside the ruled pack"
    assert "MODELLED" in e["P4"][3] and e["B1"][1].startswith("ruled 35E") and "S4" in e and "CONDITIONAL on T-H1" in e["S4"][6]
    assert (rc["e35_nom"], rc["saft_nom"]) == (144.72, 81.76) and rc["e35_use"] == (107.9, 2.52) and rc["saft_use"] == (53.5, 58.8, 1.25, 1.37)
    cells = m.cons_cell_rows(F)
    assert len(cells) >= 10 and all(re.search(r"GUARANTEED|MODELLED|AWAITING|ASSUMPTION|compatible", r[1] + r[2]) for r in cells), "each item classed"
    page = open(PAGE, encoding="utf-8").read()
    assert m.md_table(page, "| Item | Approved pack (D-06) |") == [list(r) for r in cells], "the page carries L4-E10's table as filed"
    parts = {p_[0]: p_ for p_ in m.cons_parts(F)}
    assert "81.76 Wh" in parts["the cells"][5] and "not yet adoptable" in parts["the cells"][5] and "owner's approval" in parts["the cells"][5]
    ex = {x[0]: x for x in m.cons_exit(F)}
    assert ex["U-01"][1] == m.SUPPORTED and "NOT YET ADOPTABLE" in m.SUPPORTED and "mock-up" in ex["U-01"][3] and "18 A for 60 s" in ex["U-01"][2]
    assert "limited sample qualification" in ex["U-01"][3] and "temperature windows" in ex["U-01"][4]
    assert "UNSUITABLE" in ex["U-01"][2] and "AWAITING" not in ex["U-01"][5] and "NOT YET ADOPTABLE" in ex["U-01"][6]
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    for rid in ("R-167", "R-168", "R-169"):
        assert reg[rid][7] == "U-01" and "Saft route" in reg[rid][2], rid
    # normal operation on the reconciliation's conditions; the profile at +40 C withdrawn
    rows, stmt = m.cons_normal_op(F)
    assert [r[0] for r in rows] == ["K%d" % i for i in range(1, 11)] + ["X1", "X2", "X3"]
    assert stmt[0].startswith("**The 42.8 W profile is not a required state at +40 C**") and "withdrawn" in stmt[0]
    assert "screens" in stmt[1] and "K1 and K5" in stmt[1] and "LOCAL air" in stmt[1]
    assert rc["K"]["K6"]["need"] in stmt[2] and "ENERGY ONLY" in stmt[2] and rc["K"]["K7"]["need"] in stmt[3] and "CONDITIONAL" in stmt[3]
    assert "deciding fact" not in " ".join(stmt) and "not thermally feasible" not in " ".join(stmt)
    q = cb["idle_heat"]
    assert abs((float(F["r5"]["thr"][5]) - q / tb["env"][0]) - u1["charge_start"]) < 0.05, "the charge start on the bound reproduces L4-E10's"
    for head, lines in m.cons_normal_tables(F, D, st).items():
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], head
    for name, lines in (("normal", stmt), ("deciding", m.cons_deciding(F))):
        blk = page.split("<!-- gen:%s:begin -->" % name)[1].split("<!-- gen:%s:end -->" % name)[0].strip()
        assert blk == "\n\n".join(lines), name
    assert page.index("<!-- gen:deciding:begin -->") < page.index("**The owner's definition**"), "the thermal question heads the exit statement"


def t_consolidation_the_amendment_of_14_20():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    cb, rc = F["cb"], F["rc"]
    K, R, H = rc["K"], rc["R"], rc["H"]
    for key in ("l4e12chk7", "l4e10chk6", "ledger", "verify"):
        assert key in m.PINS and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    assert "check 7" in m.COMMIT_LABEL["6f8fd652"] and _pin_held(m, "l4e12")
    # 1. the thermal correction of check 7, as the fix round restates it: section 11's conditions read, K1 and K5 screens since 12a
    assert (K["K1"]["need"], K["K2"]["need"], K["K3"]["need"], K["K6"]["need"], K["K7"]["need"], K["K8"]["need"]) == ("1.806", "2.709", "0.903", "1.447", "1.810", "2.200")
    assert (R["K1"]["read"], R["K3"]["read"], R["K6"]["read"], R["K10"]["read"]) == ("1.958", "0.941", "1.508", "2.455") and H["M2"][1] == 25.136
    assert abs(K["K1"]["q"] - F["e3o_wb"]) < 1e-3 and K["X2"]["need"] == K["K6"]["need"] and rc["cap"][0] < float(K["K1"]["need"]) < rc["cap"][1]
    assert all(float(R[k]["read"]) > float(K[k]["need"]) for k in R), "each reading is its need plus its uncertainty"
    assert "SCREEN" in K["K1"]["what"] and "SCREEN" in K["K5"]["what"], "the SGP41's +55 C is a screen, never a line"
    dec = m.cons_deciding(F)
    assert "WITHDRAWN" in dec[0] and "heat stage" in dec[0] and K["K1"]["need"] in dec[0] and "screens" in dec[0]
    assert dec[1].startswith("**The governing lines**") and "Table 4" in dec[1] and "hot stop H1" in dec[1]
    assert dec[2].startswith("**Which lines a reading can pass at all**") and "OW-10" in dec[2]
    for name in (m.CAT_MODEL, m.CAT_STORE, m.CAT_CONFLICT):
        assert name in dec[2], name
    assert "none at present" in dec[2] and "class (iii)" not in dec[2] and "No measurement can pass" not in dec[2]
    text = _C["text"]
    exit_sec = text.split("20. THE EXIT")[1].split("21. IN SHORT")[0]
    assert "1.509 W/K" not in exit_sec.split("U-02:")[0], "the withdrawn reading heads nothing"
    sec24 = text.split("24. THE OWNER'S AMENDMENT")[1].split("25. THE FIX ROUND")[0]
    assert "CORRECTED by the fix round" in sec24 and "WITHDRAWN" in sec24, "the amendment's statement kept as dated history, marked"
    rows, note = m.cons_th1(F)
    assert [r[0] for r in rows[:7]] == [p_[0] for p_ in F["fx"]["pts"]] and "superseded" in note
    page = open(PAGE, encoding="utf-8").read()
    assert page.split("<!-- gen:th1:begin -->")[1].split("<!-- gen:th1:end -->")[0].strip() == note
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    acc = reg["R-104"][5]
    assert "12d" in acc and "CFL-002" in acc and "1.509" not in acc and "P1" not in acc and "a demonstrated conflict" in acc and "local air at its port" in acc
    for rid in ("R-170", "R-171", "R-172"):
        assert "1.509" not in reg[rid][2] + reg[rid][5] and "class (ii) line" in reg[rid][2], rid
    short = page.split("## In short\n")[1].split("\n## 1. ")[0]
    assert "four lines lie over the modelled capacity, none shown impossible" in short and "not thermally feasible" not in short and "deciding fact" not in short
    # 3. the ledger in the exit
    # the counts are the ledger's own (its "All" row), and the four states sum to its rows; set 27's integration moved them
    # from (58, 24, 19, 11, 4) to (58, 24, 23, 11, 0), so the value itself is not pinned here
    led = open(os.path.join(ROOT, "v2", "docs", "records", "l4close", "FINDINGS-LEDGER.md"), encoding="utf-8").read()
    allrow = [l for l in led.split("\n") if l.startswith("| All |")]
    assert len(allrow) == 1, "the ledger has no single All row"
    want = tuple(int(x) for x in allrow[0].strip("| ").split("|")[1:6])
    assert rc["ledger"] == want and sum(want[1:]) == want[0], (rc["ledger"], want)
    led = m.cons_ledger(F)
    for x in ("%d CLOSED," % want[1], "%d CLOSED AS CONDITIONAL" % want[2], "%d OPEN DOWNSTREAM" % want[3], "%d STILL OPEN" % want[4]):
        assert x in led, x
    if want[4] == 0:
        assert "L4-E12:1.3 and 2.2" in led and "L4-E7R:1.6 and L4-E7R:2.4" in led
    assert page.split("<!-- gen:ledger:begin -->")[1].split("<!-- gen:ledger:end -->")[0].strip() == led
    assert page.index("<!-- gen:ledger:begin -->") < page.index("**The exit: Layer 4 power closure is not reached")
    # 4. R-139's lag test
    r139 = reg["R-139"]
    assert "thermocouple" in r139[5] and "0.254167 K" in r139[5] and "83.0 s" in r139[5] and "71.0 s" in r139[5] and "DIFFERS" in r139[3]
    assert "from the TMP117's reading crossing 54.0 C to the part's off state" not in r139[5]
    assert rc["lag"] == (15.0, 61.0, 0.254167) and rc["tau_max"] == (83.0, 71.0)
    # the heat-rejection approaches stay beside the bound, their need now K6 (and K7, K8 corrected); the route's rows in the change list
    apr = m.cons_approaches(F)
    assert [r[0] for r in apr] == ["none", "a2", "a3", "b", "ba", "c", "all", "need"] and K["K6"]["need"] in apr[-1][2] and K["K7"]["need"] in apr[-1][3]
    assert all(F["fx"]["modes"]["M8"]["ruled"][1] in r[5] for r in apr[:-1]), "the approaches against T4's line too"
    for head in ("| Approach | ", "| Heat | ", "| Condition |"):
        tabs = dict(m.cons_budget_tables(F, D, st), **m.cons_normal_tables(F, D, st))
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in tabs[head][2:]], head
    ch = {c[2]: c for c in m.cons_changes(list(reg.values()))}
    assert all(ch[r][1] == "8" and reg[r][6] == "OWED" for r in ("R-170", "R-171", "R-172"))
    # the reconciliation names the figures that differ
    named = {v for _r, _q, figs, _k, _w in m.RECON for v, _k2, _b in figs}
    assert {"1.508", "1.509", "1.8102", "2.1997", "50.044", "52.134", "0.941", "0.98", "1.504", "1.856", "1.810", "2.455", "144.72", "81.76"} <= named
    assert m.STATUS == "known defects addressed in drafts; feasibility conditions remain open" and "**Status: %s.**" % m.STATUS in short


def t_consolidation_the_panel_lead_surge():
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    sv = F["sv"]
    rm = sv["rm"]
    for key in ("l4e7chk5", "l4e7md", "e7guard"):
        assert key in m.PINS and m.PINS[key][1][:16] in _C["text"].split("1. THE MAKERS")[0], key
    assert _pin_held(m, "l4e7r") and "L4-F01" in m.COMMIT_LABEL[m.FROM_COMMIT["l4e7r"]] and "check 5" in m.COMMIT_LABEL["573fd5b8"]
    # the derivation's figures as L4-E7 printed them, against REQ-016's criterion
    assert sv["lim_drawn"] < sv["d1"][0] <= sv["lim"] and sv["lim_drawn"] < sv["d2"][0] <= sv["lim"], "CS116 and CS115 inside the drafted 50 V, over the drawn 35 V"
    assert all(pw > sv["d4_cap"][0] for _n, _v, _i, pw in sv["d4_rows"]) and len(sv["d4_rows"]) == 4, "without the guard a 36 V source is over D4's capability"
    assert sv["u18"] == (40.0, F["u18_vin"])
    # the remedies: the cut-off's band between CS101's peak and the SMCJ30A's cold breakdown, falling back over 25 V; the clamps under 50 V
    assert F["cs101_pv"] < rm["rise"][0] < rm["rise"][1] < rm["s30"][3] < sv["src"][1] and rm["fall"][0] > F["pv"]["v_max"]
    # the margins as printed from the unrounded band: within the two-decimal figures' rounding
    assert abs(rm["rise"][0] - F["cs101_pv"] - rm["marg"][0]) < 0.006 and abs(rm["s30"][3] - rm["rise"][1] - rm["marg"][1]) < 0.006
    assert max(rm["d1d2"]) < sv["lim"] and rm["static"] == (93.5957, 93.5521) and rm["static"][0] <= 100.0
    assert rm["cs101"][0] < rm["cs101"][2] and rm["chkb"][0] > rm["chkb"][1] and rm["resid"] == 116.5 and rm["loss"][0] == 0.217
    # IF-01: no longer NOT MET; the faults as drawn stay visible; the guard's checks MEET
    st1 = st["IF-01"]
    assert st1[1] == "CONDITIONAL"
    rows = {r["id"]: r for r in _C["R"]}
    sel = [c for c in rows["IF-01"]["checks"] if c.scope == "selected"]
    assert all(c.met for c in sel if c.met is not None) and any("D-10" in c.what for c in sel) and any("D-11" in c.what and c.cls == "CONDITIONAL" for c in sel)
    # the defects: D-10 and D-11 addressed in drafts, D-11 conditional; D-12 with the SMCJ30A
    de = {d["id"]: d for d in m.DEFECTS}
    assert de["D-10"]["state"].startswith("ADDRESSED IN DRAFTS (a selected remedy, drafted, not applied)") and "R-173" in de["D-10"]["resolution"]
    assert de["D-11"]["state"].startswith("ADDRESSED IN DRAFTS") and "CONDITIONAL on Q13's leakage above +25 C" in de["D-11"]["state"]
    assert de["D-12"]["state"].startswith("RESOLVED (drafted)") and "41.91" in de["D-12"]["options"] and "SMCJ30A" in de["D-12"]["options"]
    g2 = [g for g in m.GATE if g["n"] == 2][0]
    assert g2["verdict"] != "PASS" and "no material defect is open" in g2["constraint"] and "R-175" in g2["constraint"]
    # the register and the change list: R-173 the drafted guard after the hot swap and the entry draft; R-175 the residual band at layer 8
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    r156, r173, r174, r175, r176 = (reg[x] for x in ("R-156", "R-173", "R-174", "R-175", "R-176"))
    assert r156[6] == "OWED" and "INA169" in r156[5] and "75 V" in r156[5] and "INA250" not in r156[5] and "drafted guard" in r156[5]
    assert r173[1] == "IMPLEMENTATION" and r173[6] == "DRAFTED" and r173[7] == "4e" and "apply_gen_sch_e_solar_guard.py" in r173[2] and r173[4] == "Layer 8 board E generator owner"
    assert r174[1] == "TEST" and m.LAYER_OF[r174[4]] == "8" and "CS116" in r174[2] and "CS115" in r174[2]
    assert m.LAYER_OF[r175[4]] == "8" and "116.5 W" in r175[2] and "TRN-001" in r175[5] and r176[4] == "prototype bench" and "Q13's leakage" in r176[2]
    ch = m.cons_changes(list(reg.values()))
    pos = {c[2]: c[0] for c in ch}
    assert pos["R-21"] < pos["R-173"] and pos["R-94"] < pos["R-173"] and pos["R-123"] < pos["R-173"] < pos["R-22"]
    assert [c for c in ch if c[2] == "R-173"][0][4] == "apply_gen_sch_e_solar_guard.py"
    saved = m.CHANGE_ORDER
    try:
        order = [c for c in saved if c[1] != "R-173"]
        i = [k for k, c in enumerate(order) if c[1] == "R-94"][0]
        m.CHANGE_ORDER = order[:i] + [c for c in saved if c[1] == "R-173"] + order[i:]
        try:
            m.cons_changes(list(reg.values()))
            raise AssertionError("the guard before the hot swap must be refused")
        except SystemExit:
            pass
    finally:
        m.CHANGE_ORDER = saved
    # the verdicts and the remedies as L4-E7 compared them; the selection L4-E7's
    verdicts, remedies, sel = m.cons_surge(F)
    v = {x[0]: x for x in verdicts}
    assert v["D4"][3].startswith("MEETS with the guard") and v["D5"][3].startswith("MEETS with Q13") and v["D4"][4] == "NOT MET" and "R-175" in v["the residual band"][5]
    assert [r[0] for r in remedies] == ["(1)", "(2)", "(3)", "TVS only"] and remedies[2][4].startswith("SELECTED by L4-E7")
    assert "selected and drafted, not applied" in sel and "R-175" in sel and "93.5957" in sel
    page = open(PAGE, encoding="utf-8").read()
    for head, lines in m.cons_surge_tables(F, D, st).items():
        assert m.md_table(page, head) == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines[2:]], head
    assert page.split("<!-- gen:surge:begin -->")[1].split("<!-- gen:surge:end -->")[0].strip() == sel
    # the diagram, the budget, the behaviour, the handover and the exit carry the guard
    N, E, C, NP = m.cons_diagram(F, st)
    blk = {n[0]: " ".join(n[4]) for n in N}
    assert "U21/Q12" in blk["SOL_IN"] and "Q13" in blk["SOL_IN"] and "SMCJ30A" in blk["SOL_IN"] and "guard" in [e for e in E if e[0] == "P01"][0][4]
    modes, energy, ef, heat = m.cons_budget(F, st)
    assert "%s Wh" % m.fmt(rm["day"][0]) in {x[0]: x for x in energy}["S2"][3]
    beh = " ".join(" ".join(r) for r in m.cons_behaviour(F, D, st)["4e"])
    assert "over-voltage cut-off" in beh and "Q13" in beh and "R-175" in beh
    parts = {p_[0]: p_ for p_ in m.cons_parts(F)}
    assert "U21, Q12 (board E)" in parts and "Q13 (board E)" in parts and "D4 (board E)" in parts
    exd = {d[0]: d for d in m.cons_exit_defects(F)}
    assert exd["D-10"][2].startswith("ADDRESSED IN DRAFTS") and "CONDITIONAL" in exd["D-11"][2] and "residual" in exd
    assert m.md_table(page, "| Defect | Its fault |") == [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in m.cons_exit_table(F, D, st)["| Defect | Its fault |"][2:]]
    assert "addressed in drafts" in _C["text"].split("20. THE EXIT")[1].split("21. IN SHORT")[0]
    short = page.split("## In short\n")[1].split("\n## 1. ")[0]
    assert "ADDRESSED IN DRAFTS" in short and "R-175" in short and "0 NOT MET" in short and "**Status: %s.**" % m.STATUS in short
    led = m.cons_ledger(F)   # the review's E6 cited; the four rows not claimed closed (the ledger file is the coordinator's)
    assert "L4-E7R:1.6 and L4-E7R:2.4 needing B6's condition" in led and "REGRESSED" in led and "does not claim those four rows closed" in led


def t_fix_round_the_layer4_review_integrated():
    """The Layer 4 review (astra-check-l4close-1, NOT YET on B1 to B7) as L4-E10, L4-E11 and L4-E12 answered it, carried here: B1 and
    B2 (board E on VSYS_E, the battery FET pair, the start bounded, the inhibited acceptance piecewise), B3, B4 and B7 (each required
    mode's governing local limit, the charging heat as a balance, the runtimes labelled, the four lines over the model), B5 (the Saft
    not yet adoptable), E2 and E4's corrections, the ledger's E6; the withdrawn statements gone from the current sections."""
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    fx = F["fx"]
    text = _C["text"]
    page = open(PAGE, encoding="utf-8").read()
    for key in ("l4e10", "l4e11", "l4e12"):
        assert _pin_held(m, key), key
    for key in ("e11aux", "e11dock"):
        assert key in m.PINS and m.PINS[key][1][:16] in text.split("1. THE MAKERS")[0], key
    # B1: board E's auxiliary domain on VSYS_E; the held pack's drains; the start bounded; the system node
    assert fx["vsys_rng"] == (9.688, 17.375) and fx["held"] == (0.1408, 1.0) and fx["latch_s"] == 3.062 and fx["pw"] == (12.054, 12.054, 12.546, 11.96)
    N, E, C, NP = m.cons_diagram(F, st)
    blk = {n[0]: " ".join(n[4]) for n in N}
    assert "9.688 to 17.375 V" in blk["VBAT"] and "Q40" in blk["VBAT"] and "VSYS_E" in blk["CTL_SENS"]
    p16 = [e for e in E if e[0] == "P16"][0]
    assert p16[1:3] == ("VBAT", "CTL_SENS") and "VSYS_E" in p16[4]
    svg = open(os.path.join(REC, m.SVG_NAME), encoding="utf-8").read()
    assert "9.688 to 17.375 V (B1)" in svg and "VSYS_E" in svg
    beh = m.cons_behaviour(F, D, st)
    a4 = " ".join(" ".join(r) for r in beh["4a"])
    assert "piecewise" in a4 and "at most 1 mA" in a4 and "VSYS_E" in a4 and "Q39 and Q40" in a4
    c4 = " ".join(" ".join(r) for r in beh["4c"])
    assert "a latch within 3.062 s" in c4 and "502.3 ms withdrawn" in c4 and "0.5 A is an input ceiling" in c4
    for f_ in (page, text, svg, open(REG, encoding="utf-8").read(), open(os.path.join(REC, "README.md"), encoding="utf-8").read()):
        assert "no battery FET" not in f_, "the statement withdrawn by L4-E11's fix round"
    # B2: the pair; R-159's fallback withdrawn; the service kept
    parts = {p_[0]: p_ for p_ in m.cons_parts(F)}
    assert "Q39, Q40 (board A), (B1)" in parts and "BUK6Y10-30PX" in parts["Q39, Q40 (board A), (B1)"][1]
    assert fx["bar"][0] == 34.42 and fx["svc_tj"] == 119.8 and fx["dock"] == (242.9, 320.0, 0.848) and fx["pre"] == (0.33616, 5.7)
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert "34.42 C/W" in reg["R-159"][2] and "withdrawn" in reg["R-159"][5] and "18 A for 60 s" in reg["R-159"][5]
    for rid, item, script in (("R-177", "E11-33", "apply_gen_sch_e_aux.py"), ("R-178", "E11-34", "apply_pcb_interfaces_dock.py"), ("R-179", "E11-35", None)):
        assert item in reg[rid][3] and (script is None or script in reg[rid][3]), rid
    ch = {c[2]: c for c in m.cons_changes(list(reg.values()))}
    assert ch["R-157"][0] < ch["R-177"][0] < ch["R-22"][0] and ch["R-178"][1] == "3a"
    de = {d["id"]: d for d in m.DEFECTS}
    assert de["D-13"]["state"].startswith("ADDRESSED IN DRAFTS") and de["D-14"]["state"].startswith("ADDRESSED IN DRAFTS")
    assert not [d for d in m.DEFECTS if d["state"] == "OPEN"]
    # B3: each required mode's governing local limit; the SGP41's +55 C a screen; four lines over the modelled capacity, by category
    modes, energy, ef, heat = m.cons_budget(F, st)
    hm = [h for h in heat if h[0].startswith("M")]
    assert len(hm) == 9 and not any("Table 5" in h[4] or "Table 5" in h[5] for h in hm), "no absolute rating stands as a line"
    assert [c["mode"] for c in fx["over"]] == ["M3", "M4", "M6", "M7"]
    u2 = [c for c in m.CHOICES if c["id"] == "U-02"][0]
    for c in fx["over"]:
        assert (c["short"][0] or "the whole") in u2["constraint"], c["mode"]
    ow = {o["id"]: o for o in m.OWNER_ITEMS}
    assert "OW-10" in ow and [k for k, _ in ow["OW-10"]["docs"]] == ["l4e12md"] and "NOT a forced owner question" in ow["OW-10"]["what"]
    ex = {e[0]: e for e in m.cons_exit(F)}
    assert "four lines over the modelled capacity" in ex["U-02"][1] and "OW-10" in ex["U-02"][1]
    # B4: the charging heat a balance on one boundary
    b = fx["bal"]
    assert abs(b[0] - b[1] - b[2] - b[3]) < 1.5e-3 and fx["bal_b"][1] == 52.134 and fx["modes"]["M8"]["q"] == 52.134
    # B7: every battery-only runtime labelled
    e = {x[0]: x for x in energy}
    for k in ("B1", "B2", "B3", "P1", "P2", "P4"):
        assert "ENERGY ONLY" in e[k][4], k
    assert "ENERGY AND THERMAL" in e["B1"][4] and "%s to %s h" % (m.fmt(fx["c1"][2]), m.fmt(fx["c1"][3])) in e["B1"][4]
    # B5: the Saft supported for the temperature windows, not yet adoptable; the qualification its evidence
    assert "NOT YET ADOPTABLE" in m.SUPPORTED and "limited sample qualification" in reg["R-168"][5]
    # E2 and E4: the shared charger limit; the 9 V source under the profile; the local air
    b4 = " ".join(" ".join(r) for r in beh["4b"])
    assert "ONE shared charger input limit" in b4 and "not two additive charger capacities" in b4 and "cannot sustain" in b4
    assert "LOCAL air" in " ".join(m.cons_normal_op(F)[1])
    # E6: the ledger's four rows cited, not claimed closed
    assert "REGRESSED" in m.cons_ledger(F) and "CLOSED AS CONDITIONAL: L4-E12" not in m.cons_ledger(F)
    # the withdrawn statements gone from the current sections (1 to 6 of the page; 15 to 21 and 25 of the output)
    cur = page.split("## 7. Standalone analyses")[0]
    for w in ("binding line", "1.627 to 1.977", "46.859 W with", "20.54 C/W", "with option C (the SGP41 kept powered)"):
        assert w not in cur, w
    assert "25. THE FIX ROUND OF THE LAYER 4 REVIEW" in text and "25l WITHDRAWN IN THIS RECORD" in text


def t_b6_the_solar_guard_already_on():
    """B6 and the external review's L4-F01 (L4-E7's round 2): held as properties, never as round 1's values. The margin is chosen
    before any value and the numerical error added to U5's reading; every rating at the floor sits inside its own margin and the
    floor is where the binding rating first holds; under it the case is NOT MET, so D-10's guard-on case reads NOT CLOSED wherever
    it is stated, never CONDITIONAL on a lead's inductance; the engineer's row has its six fields, the page carries it as printed,
    and its three routes are register rows; R-176's rows are L4-E7's, row 3 naming the floor; D-12's text is L4-E7's."""
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    rm = F["sv"]["rm"]
    b6 = rm["b6"]
    assert _pin_held(m, "l4e7r") and _pin_held(m, "l4e7md") and _pin_held(m, "e7guard")
    assert 0 < b6["margin"] < b6["u5_abs"] and 0 < b6["err"] < b6["u5_abs"] - b6["margin"]
    assert b6["env"][0] < b6["l_uh"] < b6["env"][1], "the floor lies inside the declared envelope"
    assert all(mg >= 0 for n_, w, lim, mg, h in b6["rows"]), "every rating inside its margin at the floor"
    u5 = [r for r in b6["rows"] if r[0] == b6["bind"]][0]
    assert u5[2] == b6["margin"] and u5[1] <= b6["margin"] and b6["at1"] > b6["u5_abs"] and b6["at03"][0] > b6["at1"], "under the floor U5 passes its absolute maximum"
    assert b6["d"][0] < b6["l_uh"] and b6["d"][1] > b6["margin"], "(D) lowers the floor and still fails at 1.00 uH"
    assert [k for k, _ in b6["eng"]] == ["affected circuit", "evidence and failed condition", "decision or measurement needed", "pass criterion",
                                         "consequence of failure", "work blocked"] and all(v for _, v in b6["eng"])
    want = ("CS116 MEETS with the block on and off; CS115 MEETS with the block off and, with it on, is CONDITIONAL on R-174 (the cable's "
            "recorded loop current under 15.68 A, or U5's differential measured under 0.3 V).")
    assert b6["d12"] == want
    floor = "%.2f uH" % b6["l_uh"]
    assert len(b6["r176"]) == 6 and "a pass only for a loop at or over %s until B6-ENG-1 is decided" % floor in b6["r176"][2]
    de = {d["id"]: d for d in m.DEFECTS}
    assert want in de["D-12"]["options"] and de["D-10"]["state"].startswith("ADDRESSED IN DRAFTS") and "NOT CLOSED" in de["D-10"]["state"]
    assert floor in de["D-10"]["state"] and "B6-ENG-1" in de["D-10"]["state"] and "CONDITIONAL on the panel lead" not in de["D-10"]["state"]
    for rid in ("R-173", "R-176", "R-180", "R-186", "R-187"):
        assert rid in de["D-10"]["resolution"] or rid in de["D-10"]["options"], rid
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    for part in ("CL32B225KCJSNNE", "CL32B106KBJNNNE", "R97 28.0k", "C126 330 pF", "8 edits"):
        assert part in reg["R-173"][2], part
    for i, row in enumerate(b6["r176"], 1):
        assert "(%d) %s" % (i, row) in reg["R-176"][2], i
    assert reg["R-180"][4] == "Layer 7 mechanical" and floor in reg["R-180"][2] and "route (2)" in reg["R-180"][2]
    assert reg["R-186"][1] == "EVIDENCE" and "route (1)" in reg["R-186"][2] and reg["R-187"][1] == "IMPLEMENTATION" and "route (3)" in reg["R-187"][2]
    ch = {c[2]: c for c in m.cons_changes(list(reg.values()))}
    assert ch["R-180"][1] == "8" and ch["R-187"][1] == "B6-ENG-1" and ch["R-173"][1] == "4e"
    rows = {r["id"]: r for r in _C["R"]}
    b6c = [c for c in rows["IF-01"]["checks"] if "already on" in c.what][0]
    assert b6c.cls == "CONDITIONAL" and b6c.met and b6c.a == u5[1] and b6c.b == b6["margin"] and "B6-ENG-1" in b6c.what
    exd = {d[0]: d for d in m.cons_exit_defects(F)}
    assert "NOT CLOSED" in exd["D-10"][2] and exd["D-12"][2].endswith(want)
    beh = " ".join(" ".join(r) for r in m.cons_behaviour(F, D, st)["4e"])
    assert "already on" in beh and want in beh and "NOT CLOSED" in beh
    page = open(PAGE, encoding="utf-8").read()
    short = page.split("## In short\n")[1].split("\n## 1. ")[0]
    assert want in short and "NOT CLOSED" in short and "B6-ENG-1" in short
    assert page.split("<!-- gen:b6eng:begin -->")[1].split("<!-- gen:b6eng:end -->")[0].strip() == m.cons_b6eng(F)
    cur = page.split("## 7. Standalone analyses")[0] + page.split("### 8a.")[1].split("### 8b.")[0]
    assert "2.47 uH" not in cur.replace("from a 2.47 uH lead", ""), "round 1's condition is not stated as current"
    assert "26d L4-F01" in _C["text"] and "PENDING L4-E7's round" not in _C["text"] and "25m B6" in _C["text"]


def t_the_review_of_the_provisional_fixes_l4f04_the_thermal_categories():
    """L4-F04: the lines over the modelled capacity carried by category, never as lines no reading can pass. Held as properties: the
    categories are L4-E12's as read from its output and match each line's property (an operating row INFERRED to cover an unpowered
    part is a missing storage qualification, a held local limit a modelled shortfall); no demonstrated conflict while nothing is
    measured; OW-10 and CFL-002 are not forced questions; U-02 stays a closure condition decided by T-H1 plus the storage evidence;
    the withdrawn category is gone from the page, the register, the README and the output's current sections."""
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    fx = F["fx"]
    assert _pin_held(m, "l4e12") and _pin_held(m, "l4e12md") and m.PINS["th1proc"][1][:16] in _C["text"].split("1. THE MAKERS")[0]
    for c in fx["over"]:
        want = m.CAT_STORE if "e-paper" in c["line"].lower() or "EPAPER" in c["line"] else m.CAT_MODEL
        assert c["cat"] == want, (c["mode"], c["cat"])
    assert not [c for c in fx["cls"] if c.get("cat") == m.CAT_CONFLICT], "no demonstrated conflict while nothing is measured"
    assert all(c["cls"] in ("i", "ii", "over") for c in fx["cls"])
    ow = {o["id"]: o for o in m.OWNER_ITEMS}
    assert "only when a measurement demonstrates a conflict" in ow["OW-1"]["what"] and "NOT a forced owner question" in ow["OW-10"]["what"]
    assert m.CONDITION_U02.startswith("(ii) a closure condition decided by T-H1 plus the storage evidence")
    u2 = [c for c in m.CHOICES if c["id"] == "U-02"][0]
    assert "only on a DEMONSTRATED CONFLICT" in u2["overturns"]
    page = open(PAGE, encoding="utf-8").read()
    reg = open(REG, encoding="utf-8").read()
    readme = open(os.path.join(REC, "README.md"), encoding="utf-8").read()
    cur_out = _C["text"].split("21. IN SHORT")[0] + _C["text"].split("26. THE REVIEW OF THE PROVISIONAL FIXES")[1]
    for f_ in (page, reg, readme, cur_out):
        assert "class (iii)" not in f_ and "no reading can pass" not in f_ and "No measurement can pass" not in f_
    for name in (m.CAT_MODEL, m.CAT_STORE, m.CAT_CONFLICT):
        assert name in page and name in _C["text"].split("26c L4-F04")[1], name
    rows = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    assert rows["R-185"][1] == "TEST" and "function read back" in rows["R-185"][2] and "for that lot" in rows["R-185"][5]


def t_the_review_of_the_provisional_fixes_l4f02_l4f03():
    """The external review of the provisional fixes (2 October 2026): L4-F02 and L4-F03 as L4-E11's round answers them, carried. Held
    as properties: D-14 reads CONDITIONAL on the three evidence rows with Ciss OPEN, D-15 is the dock branch's protection addressed in
    drafts, every E11 item L4-E11 prints is in the register with L4-E11's owner, the eFuse is its own change before board E's feed, the
    held pack's 0.1408 mA is nowhere a bound, and the texts L4-E11 16f drafted stand at their places."""
    m = _M()
    F, D, st = _C["F"], _C["D"], _C["st"]
    g = F["f02"]
    assert _pin_held(m, "l4e11") and _pin_held(m, "l4e11md")
    assert g["allow"] < g["rds_max"][0] and g["z_ev"][0][2] > g["z_ev"][1][2] > g["z_ev"][2][2] and g["svc"][0] < 150.0
    assert g["ef"][1] < g["ef"][0] < g["ef"][2] and g["ef_c"][0] < g["ef_c"][2] and g["cex"][0] > g["ef_c"][2]
    de = {d["id"]: d for d in m.DEFECTS}
    assert not [d for d in m.DEFECTS if d["state"] == "OPEN"]
    s14 = de["D-14"]["state"]
    assert s14.startswith("ADDRESSED IN DRAFTS") and "CONDITIONAL on E11-29, E11-30 and E11-36" in s14 and "E11-37" in s14 and "OPEN" in s14
    assert de["D-15"]["state"].startswith("ADDRESSED IN DRAFTS") and "E11-38" in de["D-15"]["state"] and "R-181" in de["D-15"]["resolution"]
    reg = {r[0]: r for r in _md_rows(REG, "| ID | Kind |")}
    owner_of = {i: o.strip() for i, _k, o in F["e11_items"]}
    for item in ("E11-35", "E11-36", "E11-37", "E11-38"):
        rows = [r for r in reg.values() if re.search(r"\b%s\b" % item, r[3])]
        assert rows and all(r[4] == owner_of[item] for r in rows), item
    r181 = reg["R-181"]
    assert r181[1] == "IMPLEMENTATION" and "apply_gen_sch_a_charger.py" in r181[3] and r181[6] == "DRAFTED"
    for part in ("U42", "R221", "C237", "VSYS_DOCK"):
        assert part in r181[2], part
    ch = {c[2]: c for c in m.cons_changes(list(reg.values()))}
    assert ch["R-181"][1] == "3a" and ch["R-181"][0] < ch["R-177"][0] and ch["R-181"][0] < ch["R-11"][0]
    page = open(PAGE, encoding="utf-8").read()
    for f_ in (page, _C["text"].split("25. THE FIX ROUND")[0], open(REG, encoding="utf-8").read()):
        assert "bounded at 0.1408" not in f_ and "drains total 0.1408" not in f_.split("25a B1")[0]
    cur = page.split("## 7. Standalone analyses")[0]
    for w in ("34.42", "0.848 hot", "at 119.8 C"):
        assert w not in cur, w
    assert "quantified subset" in cur and "quantified subset" in page.split("### 8b.")[0].split("### 8a.")[1]
    N, E, C, NP = m.cons_diagram(F, st)
    assert "U42" in [e for e in E if e[0] == "P16"][0][4]
    ex = page.split("**The exit: Layer 4 power closure is not reached")[1].split("## 7. ")[0]
    assert "quantified drains 0.1408 mA" in ex and "RDS(on) allowance of 21.136 mOhm" in ex and "(Zself + Zmut)" in ex
    u4 = {e[0]: e for e in m.cons_exit(F)}["U-04"]
    assert "Zself + Zmut" in u4[2] and "E11-37" in u4[2] and "quantified subset" in u4[4]
    assert len(g["f16"]) == 4 and len(g["g16"]) == 5
    sec = _C["text"].split("26. THE REVIEW OF THE PROVISIONAL FIXES")[1]
    assert "26a L4-F02" in sec and "26b L4-F03" in sec and "26d L4-F01" in sec


CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def t_no_dashes_and_no_claim_words_in_the_record():
    files = [os.path.join(REC, f) for f in sorted(os.listdir(REC)) if f.endswith((".md", ".py", ".out"))]
    files.append(os.path.abspath(__file__))
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
        if p != os.path.abspath(__file__):
            # L4-E10's battery comparison's class label GUARANTEED (a maker's printed limit; the owner's amendment of 2 October 2026),
            # carried verbatim as the budget's cell row, is a label, not a claim: only the exact uppercase word is admitted
            m = CLAIM.search(re.sub(r"\bGUARANTEED\b", "", t))
            assert not m, "%s carries a claim word: %r" % (os.path.relpath(p, ROOT), m.group(0))
