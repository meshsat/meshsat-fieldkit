"""Layer 5's power pass (MESHSAT-1357, set 27, 3 October 2026; v2/docs/records/l5pwr/): Layer 4's power results written into
pcb_interfaces.yaml, HW-FW-CONTRACT.md and PANEL.md section 10, held as predicates on what the record's reader computes and on the
contract files themselves.

The predicates: the committed l5pwr_contracts.out is what the script prints; every excerpt of the table is in its target file and
every figure it cites is printed by a cited Layer 4 source (the script refuses otherwise); every mark is one of the declared words
and every PROVISIONAL entry names its invalidation trigger; the `pins` maps of the dock contract equal the committed netlists' (a
property that survives the drafts' application: when the generators and netlists change, the map changes with them); the drafted pin
1 is its own field until then; the eleven power lines of L4-E9 section 4 have their states; the contract rows added carry their
tables' cell counts with unique ids, FW-C08 and FW-A14 carry the restated texts and the old FW-A16 rule is gone; PANEL.md section 10
carries the hold sentence; the page's table equals the script's; the apply scripts refuse a second run on the tree and apply once to
the base they were written against; no em or en dash in the record. Set 28's restatement (finding F-12): every restated row is a
row of the table, its withdrawn figures are figures it cites, every replacing text is matched once in its source with figures
parsed from the match, no figure is typed in the restatement's prose or patterns, S27-02b's replacing text is L4-E11's PWM-duty
ramp, a withdrawn text still in a target names its finding, and the page's section 4a equals the script's. L5-F09 and L5-F10
(apply_l5pwr2_contracts.py) and L5-F11 (apply_l5f11_contracts.py, after it): no withdrawn text of theirs is in the tree's contract
files, nor any wording of set 28's sweep, the tree carries both restatements as the Layer 4 files printed them when the scripts
were applied ("already applied"; their Layer 4 reads pinned at a49a2b13 since W1) on every text W8 did not restate, and on the five
W8 restated (L5-F09 a to d, F11-09; its change record row "| 2 (W8, L5-F14) |") three properties in their place (W14, 6 October
2026: on that tree the first script refuses by its docstring's rule and the second at its ORDER check, whose proposed correction is
test_w14l5.PATCH_L5F11_ORDER), each script applies once to the files it was
written against and is idempotent, and the second refuses before the first. W1 (6 October 2026): S27-B6 reads L4-E9's D-10 as set 31
left it, refusing set 28's sentence on the page and set 31's on a copy that carries set 28's.
Software predicates on text: they establish no electrical property and accept nothing.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l5pwr")
SCRIPT = os.path.join(REC, "l5pwr_contracts.py")
OUT = os.path.join(REC, "l5pwr_contracts.out")
PAGE = os.path.join(REC, "L5-POWER-CONTRACTS.md")
APPLY = os.path.join(REC, "apply_l5pwr.py")
APPLY_CONOPS = os.path.join(REC, "apply_conops_l5pwr.py")
APPLY2 = os.path.join(REC, "apply_l5pwr2_contracts.py")
BASE2 = "97dbcc43"         # fnd/l5pwr2 before apply_l5pwr2_contracts.py: the contract files it was written against
APPLY3 = os.path.join(REC, "apply_l5f11_contracts.py")
BASE3 = "1c4e0ff2"         # fnd/l5pwr2 after apply_l5pwr2_contracts.py, before apply_l5f11_contracts.py
# set 28's sweep: wordings Layer 4 withdrew in set 27, none of which the contract files may carry (a property of the files, not of a
# commit): the guard's pass from a loop, the hard short as a ceiling, R-176's old row 2 and 3 bounds, the 1.0 A branch and its drop,
# the per-fan start rule's wording, the B6 case NOT CLOSED, the fans unnamed, U22 left out of the start and the domain
WITHDRAWN = [r"a pass only (from|for) a (source )?loop", r"\(a ceiling, no inductance credited", r"PV_F at most 75 V", r"at most 61 A, within",
             r"VSYS_E at least 9\.539", r"0\.1486 V", r"1\.0 A declared", r"with a PWM ramp", r"never while U12 starts",
             r"guard-on case NOT CLOSED", r"no fan is named", r"the other and U12 settled", r"the fans and U12 on VSYS_E",
             r"the mixer fans, D7 and D8\)", r"at most 0\.5713 A", r"at most 0\.3356 A"]
YAML = os.path.join(TOOLS, "pcb_interfaces.yaml")
HWFW = os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md")
PANEL = os.path.join(ROOT, "v2", "docs", "PANEL.md")
BASE = "2c240414"          # fnd/l4e9 before this pass: the files the apply scripts were written against
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
MARKS = ("MAKER", "INFERRED", "MODELED", "PROVISIONAL", "RULE", "TEST", "NETLIST", "VERIFIED")
NEW_FW = ["FW-A19", "FW-A20", "FW-A21", "FW-A22", "FW-A23", "FW-C15", "FW-E11", "FW-E12", "FW-E13"]
NEW_V = ["V-A11", "V-C15", "V-E11", "V-E12", "V-E13", "V-E14", "V-E15", "V-E16"]
LINES = ["SLOT_EN1..3", "SHORE_INHIBIT", "CHG_INHIBIT", "CHRG_INHIBIT_bit_and_ChargeCurrent", "EN_OOA", "DCIN_PGD", "HOT_R1",
         "VSYS_DOCK", "FAN1_SW_FAN2_SW", "U34_restart_guard", "SWEN"]


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l5pwr record")
        sp = importlib.util.spec_from_file_location("l5pwr_contracts_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l5pwr_contracts.py refused (exit %s): an excerpt is not in its target or a figure is not in its source" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _yaml():
    import yaml
    return yaml.safe_load(open(YAML, encoding="utf-8"))


def _cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def _git_show(rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, rel)], capture_output=True)
    if r.returncode != 0:
        raise Skip("commit %s is not in this repository" % BASE)
    return r.stdout


def _run(args, cwd=None):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True, text=True, cwd=cwd)


def t_output_reproduced_byte_for_byte():
    _M()
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l5pwr_contracts.out is not what the script prints"


def t_every_excerpt_is_in_its_target_and_every_figure_in_a_source():
    m = _M()
    R = _C["R"]
    assert len(R["rows"]) == len(m.T) >= 40 and R["nfig"] >= 150
    assert all(e["ok_text"] and not e["lost"] for e in R["rows"])
    for key in ("yaml", "hwfw", "panel"):
        rel, h = R["pins"][key]
        assert re.fullmatch(r"[0-9a-f]{64}", h) and h in _C["text"], "the output does not pin %s" % rel
    assert set(e["target"] for e in R["rows"]) == {"yaml", "hwfw", "panel"}


def t_marks_triggers_and_criteria_are_well_formed():
    m = _M()
    for e in list(m.T) + _C["R"]["rows"]:   # as written, and as restated at set 28 (F-12)
        assert any(w in e["mark"] for w in MARKS) or e["mark"].startswith("DRAFTED"), (e["id"], e["mark"])
        assert set(e["criteria"]) <= set(m.CRITERIA) and e["criteria"], e["id"]
        if "PROVISIONAL" in e["mark"]:
            assert re.search(r"(R-\d+|E11-\d+|B6-ENG-1|PANEL-ACC|PWR-F\d+|Q-TI-\d+|U-0\d|V-A0\d|T-H1|M2)", e["trigger"]), \
                "%s is PROVISIONAL but its trigger names no row or measurement: %r" % (e["id"], e["trigger"])
    prov = [e for e in _C["R"]["rows"] if "PROVISIONAL" in e["mark"]]
    assert len(prov) == len(_C["R"]["prov"]) >= 15
    for c, st in m.CRITERIA_STATE.items():
        assert c in m.CRITERIA and len(st) > 60


def _netlist_pins(stem_dir, stem, ref, pins):
    """{pin: net} of one connector from a committed KiCad netlist, by the same regexes check_contracts.py uses."""
    p = os.path.join(ROOT, "v2", "ecad", stem_dir, "out", stem + ".net")
    need(p, "the committed netlist")
    txt = open(p, encoding="utf-8", errors="replace").read()
    out = {}
    for mm in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', txt, re.S):
        name = mm.group(1).lstrip("/")
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', mm.group(2)):
            if n.group(1) == ref and n.group(2) in pins:
                out[n.group(2)] = name
    return out


def t_the_dock_pins_map_is_the_committed_netlists_and_the_drafted_pin_one_is_its_own_field():
    d = _yaml()
    dock = d["board_to_board"]["contracts"]["IF-AE-DOCK"]
    alias = {tuple(sorted(a[:2])) for a in dock["aliases"]}
    a = _netlist_pins("pcb-a-power-a23", "pcb-a-power", "J_DOCK", {str(i) for i in range(1, 13)})
    e = _netlist_pins("pcb-e1-dock-e7", "pcb-e1-dock", "J_BLK", {str(i) for i in range(1, 13)})
    for i in range(1, 13):
        want = dock["pins"][i]
        assert a.get(str(i)) == want, "A J_DOCK pin %d: the contract says %s, the committed netlist %s" % (i, want, a.get(str(i)))
        got_e = e.get(str(i))
        assert got_e == want or tuple(sorted((got_e, want))) in alias, "E J_BLK pin %d: %s against %s" % (i, got_e, want)
    blk = dock["pin1_vsys_dock"]
    for s in ("VSYS_DOCK", "VSYS_E", "U42", "TPS16630", "1.4713", "1.8018", "apply_pcb_interfaces_dock.py", "PROVISIONAL", "E11-38"):
        assert s in blk, s
    # the drafted assignment is consistent with the drawn one: the field says which the map above is, and names its own state
    assert ("pins map above stays the committed netlists' (pin 1 GND)" in " ".join(blk.split())) == (dock["pins"][1] == "GND")


def t_the_power_lines_of_l4e9_section_4_have_their_states():
    d = _yaml()
    pls = d["board_to_board"]["power_line_states"]
    assert all(ln in pls for ln in LINES), [ln for ln in LINES if ln not in pls]   # a later round may add lines (record l5r2 added one)
    for ln, v in pls.items():
        for k in ("default", "firmware", "source"):
            assert v.get(k), (ln, k)
        assert "reset" in v or "threshold" in v, ln
        assert "cable_out" in v or ln in ("U34_restart_guard", "SWEN"), ln
    hold = pls["SLOT_EN1..3"]["hold"]   # its state moves with the circuit: OWED at this pass, DRAFTED once a record draws it (l8gnd)
    assert ("OWED" in hold or "DRAFTED" in hold or "DRAWN" in hold) and "FW-C02" in hold
    assert "DRAFTED" in pls["VSYS_DOCK"]["reset"] and "FW-E11" in pls["VSYS_DOCK"]["firmware"]
    assert "never a charge hold" in " ".join(pls["SHORE_INHIBIT"]["assert"].split())


def t_the_four_touched_contracts_carry_every_pass_two_field():
    d = _yaml()
    cs = d["board_to_board"]["contracts"]
    req = ["title", "kind", "ends", "harness", "levels", "current", "default_state", "sequencing", "mating", "hot_plug", "judged_by", "tbd", "findings", "serves"]
    for cid in ("IF-EXT-DC", "IF-AE-DOCK", "IF-PE-PACK", "IF-EXT-USB", "IF-AB-POWER"):
        for f in req:
            assert f in cs[cid], "%s lacks %s" % (cid, f)
        for f in ("firmware", "bench"):
            if cid != "IF-AB-POWER":
                assert cs[cid].get(f), "%s lacks %s" % (cid, f)
    for s in ("the drawn value text's 'about 6 A for 100 W at 18 V' is superseded", "A-3(c), a COMPONENT_LIMITATION"):
        assert s in " ".join(str(cs["IF-EXT-DC"]).split()), s
    assert "monitor" in cs["IF-AB-POWER"]["currents"][-1] and "R227" in cs["IF-AB-POWER"]["currents"][-1]["monitor"]


def t_the_contract_rows_added_have_their_tables_cells_and_unique_ids():
    t = open(HWFW, encoding="utf-8").read()
    lines = t.split("\n")
    width, ids, first = None, {}, {}
    for l in lines:
        c = _cells(l)
        if c is None:
            width = None
            continue
        if width is None:
            width = len(c)
        elif not all(x.strip("-") == "" for x in c):
            assert len(c) == width, "a row has %d cells under a header of %d: %s" % (len(c), width, l[:60])
        if re.match(r"^(FW|V)-[A-Z]\d\d$", c[0]):
            assert c[0] not in ids, "row %s occurs twice" % c[0]
            ids[c[0]] = c
    for k in NEW_FW + NEW_V + ["FW-A18", "V-A06", "V-A10"]:
        assert k in ids, "row %s is missing" % k
    assert len(ids["FW-A19"]) == 6 and len(ids["V-E16"]) == 3
    f = lambda k: " ".join(" | ".join(ids[k]).split())
    assert "Asserted only on the operator's 'inputs off' and on the water-on-floor isolation" in f("FW-C08")
    assert "never as a charge hold" in f("FW-A14") and "never while the pack cannot discharge" in f("FW-A14")
    assert "IIN_HOST is written 4.70 A only on a board A whose netlist carries the ILIM_HIZ network" in f("FW-A16")
    assert "the 9 V figure while VIN_RAW is unknown" not in t and "0.80 x 4.80 A x 0.93 x VIN_RAW / 20.7 V (1.55 A at 9 V" not in t
    assert "7.24 V" in f("V-A08") and "LM5069's TIMER never reaches" not in f("V-A08")
    assert "R227" in f("FW-A09") and "16.384" in f("FW-A09")
    assert "### 4.1 What Layer 4's power drafts change in these rows" in t and "(FW-A01 to FW-A23)" in t
    assert "(FW-C01 to FW-C15)" in t and "(FW-E01 to FW-E13)" in t
    assert "| 2 (L5-PWR) |" in t
    for k in NEW_FW:
        assert ids[k][5].split("(")[0].strip().split(";")[0].split(",")[0] in ("FIRMWARE", "DRAFTED", "DRAWN"), (k, ids[k][5][:40])


def t_panel_section_ten_carries_the_hold_sentence():
    t = " ".join(open(PANEL, encoding="utf-8").read().split())
    sec = t.split("## 10. Shore charge inhibit and the pack")[1].split("## 11.")[0]
    assert "No hold uses the CHG_INHIBIT line or SHORE_INHIBIT." in sec
    assert "assert SHORE_INHIBIT only for 'inputs off' and the water-on-floor isolation" in sec
    assert "when the operator sets \"no charge\", and clears it with hysteresis" not in sec


def t_the_pages_table_equals_the_scripts():
    m = _M()
    page = open(PAGE, encoding="utf-8").read()
    i, j = page.index("<!-- l5pwr-table:begin -->"), page.index("<!-- l5pwr-table:end -->")
    block = [l for l in page[i:j].split("\n")[1:] if l.strip()]
    assert block == m.md_rows(_C["R"]), "the page's table is not the script's"
    i, j = page.index("<!-- l5pwr-restated:begin -->"), page.index("<!-- l5pwr-restated:end -->")
    block = [l for l in page[i:j].split("\n")[1:] if l.strip()]
    assert block == m.md_restated(_C["R"]), "the page's section 4a is not the script's"
    for s in ("PASS 99 of 99", "## 9.", "PROVISIONAL", "check_contracts.py"):
        assert s in page, s


def t_the_set28_restatement_parses_its_figures_and_types_none():
    """F-12: a row whose cited figure set 27's Layer 4 corrections changed is restated beside the table, its figures parsed."""
    m = _M()
    R = _C["R"]
    ids = {e["id"] for e in m.T}
    assert set(m.RESTATED) <= ids and "S27-02b" in m.RESTATED
    page = open(PAGE, encoding="utf-8").read()
    rows = {e["id"]: e for e in R["rows"]}
    for i, rs in m.RESTATED.items():
        e = rows[i]
        r = e["restated"]
        assert r and rs["withdrawn"] and set(rs["withdrawn"]) <= set(e["figures"]), i
        assert len(r["cites"]) == len(rs["now"]) and any(c["figures"] for c in r["cites"]), i
        for c in r["cites"]:
            assert c["text"] in " ".join(open(os.path.join(ROOT, c["file"]), encoding="utf-8").read().split()), (i, c["text"][:50])
            assert all(f in c["text"] for f in c["figures"]), i
        for key, pat in rs["now"]:
            assert m.figures_in(pat.replace("\\", "")) == [], "%s: a figure is typed in a pattern: %r" % (i, pat[:60])
        for kind, key, pat in rs["target"]:
            assert kind in ("restated", "stale") and m.figures_in(pat.replace("\\", "")) == [], (i, pat[:60])
        for f in ("why", "value", "mark", "trigger", "where"):
            assert m.figures_in(rs[f]) == [], "%s: a figure is typed in the restatement's %s: %s" % (i, f, m.figures_in(rs[f]))
        assert r["state"] in ("RESTATED IN PLACE", "SUPERSEDED IN PLACE", "NOT RESTATED"), i
        if r["state"] == "NOT RESTATED" or any(c["kind"] == "stale" for c in r["tchecks"]):
            assert r["finding"] and ("| %s |" % r["finding"]) in page, "%s: a withdrawn text still in a target needs its finding" % i
        assert e["mark"] == rs["mark"] and e["trigger"] == rs["trigger"] and e["was"]["mark"] != "", i
    b = rows["S27-02b"]["restated"]
    assert any(c["key"] == "l4e11out" and "PWM-duty ramp into the fan's PWM input" in c["text"] for c in b["cites"])
    assert "PWM ramp" in b["withdrawn"]
    assert "1a. RESTATED AT SET 28" in _C["text"] and "4a. THE RESTATEMENT AS MARKDOWN" in _C["text"]


def t_the_apply_script_refuses_a_second_run_on_the_tree_and_applies_once_to_the_base():
    need(APPLY, "the patch script")
    need(os.path.join(ROOT, ".git"), "a git checkout")
    for tree in (YAML, HWFW, PANEL):
        r = _run([APPLY, tree, "--check"])
        assert r.returncode == 3 and "already applied" in r.stderr, (tree, r.returncode, r.stderr[-200:])
    d = tempfile.mkdtemp(prefix="l5pwr-apply-")
    try:
        y = os.path.join(d, "pcb_interfaces.yaml")
        h = os.path.join(d, "HW-FW-CONTRACT.md")
        p = os.path.join(d, "PANEL.md")
        open(y, "wb").write(_git_show("v2/ecad/tools/pcb_interfaces.yaml"))
        open(h, "wb").write(_git_show("v2/docs/HW-FW-CONTRACT.md"))
        open(p, "wb").write(_git_show("v2/docs/PANEL.md"))
        r = _run([APPLY, h, "--check"])
        assert r.returncode == 3 and "ORDER" in r.stderr, "the contract patch must require L4-E5's draft first: %s" % r.stderr[-200:]
        r = _run([os.path.join(ROOT, "v2", "docs", "records", "l4e5", "apply_fw_a16.py"), h, "--write"])
        assert r.returncode == 0, r.stderr[-300:]
        for f in (y, h, p):
            r = _run([APPLY, f, "--check"])
            assert r.returncode == 0 and "CHECK OK" in r.stdout, (f, r.stderr[-300:])
            r = _run([APPLY, f, "--write"])
            assert r.returncode == 0, (f, r.stderr[-300:])
            r = _run([APPLY, f, "--check"])
            assert r.returncode == 3 and "already applied" in r.stderr
        # the base files patched read as the files this pass committed (L5PWR_COMMIT, in this branch's history): the script is the
        # whole change. Not the tree's files: a later round (record l5r2) edits them in place, and a rule that fails when its subject
        # moves on is a rule about history.
        for f, rel in ((y, "v2/ecad/tools/pcb_interfaces.yaml"), (h, "v2/docs/HW-FW-CONTRACT.md"), (p, "v2/docs/PANEL.md")):
            r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (_M().L5PWR_COMMIT, rel)], capture_output=True)
            assert r.returncode == 0, "%s is not readable at the pass's commit" % rel
            assert open(f, "rb").read() == r.stdout, "%s patched from the base differs from the pass's commit" % os.path.basename(rel)
        # L4-E11's dock draft still applies to the patched yaml
        r = _run([os.path.join(ROOT, "v2", "docs", "records", "l4e11", "apply_pcb_interfaces_dock.py"), y, "--check"])
        assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr[-200:]
    finally:
        shutil.rmtree(d)


# W14 (6 October 2026): the evidence basis of the restatement of the two tests below (the coordinator's brief W14; W10's adoption
# read, _runs/int31/PLAN.draft.md section 5). W8 (fnd/w8l5 8840adda, adopted in the NEXT set; finding L5-F14 of this record)
# restated, in pcb_interfaces.yaml IF-EXT-DC `protection`, `bench` and `l4_defects` and in HW-FW-CONTRACT.md section 4.1's R-173 row
# and V-E16, five texts the two contract scripts wrote (apply_l5pwr2_contracts.py L5-F09 a to d, apply_l5f11_contracts.py F11-09) to
# L4-E9's D-10 as set 31 left it, and kept the superseded wording verbatim as dated history in the change record row
# "| 2 (W8, L5-F14) |". Reproduced on W14's base 27cd9cd2 (`run.py test_l5pwr.`: 14 passed, 2 failed, 0 skipped): line 341 failed
# with (3, '', '... L5-F09 a: old text 0 time(s), new text absent; ... refusing, nothing written') and line 392 with (3, '',
# 'apply_l5f11_contracts: ORDER: apply_l5pwr2_contracts.py is not applied to these files (...)'). The scripts' rule
# (apply_l5pwr2_contracts.py docstring lines 24 to 26, apply_l5f11_contracts.py lines 32 and 33) reads "already applied" only while
# every new text stands verbatim and refuses anything else, and decision 11's Reverse (b) of L5-POWER-CONTRACTS.md has both refuse
# "until the contracts and the scripts are restated". So each test now expects the script's answer on the tree as W8 left it, and
# holds what the old "already applied" held on what W8 did not touch (verbatim) and, on what W8 restated, three properties in its
# place: every Layer 4 value the script's text printed still stands in the field, the superseded part of the script's text is in
# W8's change record row and gone from the field, and the field claims no more (OPEN, PROVISIONAL, no loop claimed to pass).
# apply_l5pwr2's answer is the one its docstring prescribes (decision (a)); apply_l5f11's refusal is right but its ORDER reason is
# not (decision (b)): test_w14l5.py carries the proposed correction PATCH_L5F11_ORDER and checks it on copies, never on the script.
W8_ROW = "| 2 (W8, L5-F14) |"
W8_RESTATED = ("L5-F09 a", "L5-F09 b", "L5-F09 c", "L5-F09 d", "F11-09")


def _w14_load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _w14_live(flat, tg, where, texts):
    """The live text an edit targets: the YAML field parsed (a contract's key, or a full key path), or the one table row whose first
    cell `where` opens."""
    if tg == "yaml":
        import yaml
        node = yaml.safe_load(texts["yaml"])
        for k in (("board_to_board", "contracts") + tuple(where) if len(where) == 2 else where):
            node = node[k]
        return flat(node if isinstance(node, str) else str(node))
    rows = [ln for ln in texts["hwfw"].split("\n") if ln.startswith(where)]
    assert len(rows) == 1, "%d rows open with %r" % (len(rows), where)
    return flat(rows[0])


def _w14_history(flat, texts):
    """The quoted superseded wordings of W8's change record row (one row)."""
    rows = [ln for ln in texts["hwfw"].split("\n") if ln.startswith(W8_ROW)]
    assert len(rows) == 1, "%d change record rows %s" % (len(rows), W8_ROW)
    return [flat(q) for q in re.findall(r'"([^"]+)"', rows[0])]


def _w14_restated(flat, i, new, live, quotes, values, nopass, withdrawn=()):
    """An edit W8 restated: every Layer 4 value its text printed still in the field (a value in `withdrawn`, one set 31 withdrew,
    instead recorded in W8's row and gone from the field), the superseded part in W8's row and not in the field, and the field no
    wider than the script's text (OPEN, PROVISIONAL, no loop claimed to pass)."""
    vals = [v for v in values if len(v) > 1 and v in new]
    for v in vals:
        if v in withdrawn:
            assert v not in live and any(v in q for q in quotes), "%s: %r is neither gone nor recorded as history" % (i, v)
        else:
            assert v in live, "%s: a value the script printed is gone: %r" % (i, v)
    hist = [q for q in quotes if q in flat(new) or flat(new) in q]   # a part of the script's text, or the whole of it in context
    assert hist, "%s: W8's change record row quotes none of the script's text" % i
    assert not [q for q in hist if q in live], "%s: a superseded wording is still in the field" % i
    for w in ("OPEN", "PROVISIONAL", nopass):
        assert w in live, "%s: the restated field lacks %r" % (i, w)
    return vals


def _w14_l5f11_state(a, V, texts):
    """apply_l5f11_contracts.py's own per-edit state on `texts`, read with its own functions as its main() reads it after the ORDER
    check (lines 195 to 209): (id, old matches, new text present)."""
    st = []
    for i, tg, _w, old, new in a.edits(V):
        if isinstance(new, tuple):
            _k, applied, build = new
            ms = list(a.rx(old).finditer(texts[tg]))
            mm = list(a.rx(applied).finditer(texts[tg]))
            kept = ms[0].group(1) if len(ms) == 1 else (mm[0].group(1) if len(mm) == 1 else "?")
            new = build(a.flat(kept), V)
        st.append((i, len(list(a.rx(old).finditer(texts[tg]))), a.flat(new) in a.flat(texts[tg])))
    return st


def _w14_l5pwr2_answer(E):
    """apply_l5pwr2_contracts.py's refusal on the tree as W8 left it, as its main() prints it (lines 251 to 254)."""
    return "apply_l5pwr2_contracts: not in the state this script applies to: %s; refusing, nothing written\n" % "; ".join(
        "%s: old text 0 time(s), new text %s" % (i, "absent" if i in W8_RESTATED else "present") for i, _t, _w, _o, _n in E)


def t_the_contract_restatement_of_l5f09_and_l5f10_is_in_the_tree_and_idempotent():
    """No withdrawn text of L5-F09 or L5-F10 in the tree's contract files; the script writes nothing on the tree; the tree carries
    L5-F10's two texts as the Layer 4 files printed them when the script was applied, and L5-F09's four as W8 restated them with
    every Layer 4 value the script printed still in them; the script applies once to the files at BASE2 and a second run writes
    nothing.

    Evidence basis of the narrowed reading (W1, 6 October 2026): until set 31 the script read the tree's Layer 4 files and this test
    read "the restatement as the Layer 4 files print it now". Set 31 (v2/docs/records/l4e9/SET31-CHANGES.md items 2 and 23) restated
    L4-E9's D-10, so the D-10 sentence the script quotes is matched 0 times on the tree and the script refused, although the contracts
    carry what it wrote (the integration's log of 6 October 2026). The script now reads the Layer 4 files at its L4_AT (a49a2b13,
    where both contract scripts had been applied), and that the contracts lag the page is finding L5-F14 of L5-POWER-CONTRACTS.md,
    which t_s27b6_reads_d10_as_set31_left_it holds on the page.

    W14 (6 October 2026), decision (a): W8 restated L5-F09 a to d (the comment above these helpers), so on the tree the script answers
    what its docstring prescribes for a state that is neither (lines 24 to 26): exit 3, nothing written, each edit's state named
    (L5-F10 a and b applied verbatim, L5-F09 a to d with their old texts gone and their new texts absent). That answer is correct, and
    it is now the expectation, exact to the character; "already applied" was true until W8 and is what test_w14l5 shows the files at
    W8's base still read. Nothing the old assertion held is dropped: no old text (unchanged), L5-F10's texts verbatim (unchanged),
    and in place of L5-F09's verbatim texts the three properties of _w14_restated."""
    import collections
    import hashlib
    need(APPLY2, "the contract script")
    a = _w14_load(APPLY2, "apply_l5pwr2_under_test")
    E = a.edits(collections.defaultdict(str))
    assert len(E) == 6
    tree = {"yaml": open(YAML, encoding="utf-8").read(), "hwfw": open(HWFW, encoding="utf-8").read()}
    for i, tg, _w, old, _n in E:
        assert not a.rx(old).search(tree[tg]), "%s: a withdrawn text is still in %s" % (i, tg)
    shas = [hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (YAML, HWFW)]
    r = _run([APPLY2, "--check"])
    assert r.returncode == 3 and r.stdout == "" and r.stderr == _w14_l5pwr2_answer(E), (r.returncode, r.stdout[-200:], r.stderr[-400:])
    assert shas == [hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (YAML, HWFW)], "the check wrote a contract file"
    V = a.l4()
    quotes = _w14_history(a.flat, tree)
    for i, tg, where, _old, new in a.edits(V):
        live = _w14_live(a.flat, tg, where, tree)
        if i in W8_RESTATED:
            assert a.flat(new) not in live, "%s: the script's text stands verbatim, so W8 did not restate it" % i
            assert _w14_restated(a.flat, i, new, live, quotes, V.values(), "no loop is claimed to pass"), i
        else:
            assert a.flat(new) in live, "%s: the text the script wrote is not in the tree" % i
    d = tempfile.mkdtemp(prefix="l5pwr2-apply-")
    try:
        y = os.path.join(d, "pcb_interfaces.yaml")
        h = os.path.join(d, "HW-FW-CONTRACT.md")
        for f, rel in ((y, "v2/ecad/tools/pcb_interfaces.yaml"), (h, "v2/docs/HW-FW-CONTRACT.md")):
            g = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE2, rel)], capture_output=True)
            if g.returncode != 0:
                raise Skip("commit %s is not in this repository" % BASE2)
            open(f, "wb").write(g.stdout)
        args = ["--yaml", y, "--hwfw", h]
        r = _run([APPLY2, "--check"] + args)
        assert r.returncode == 0 and "CHECK OK, 6 edit(s)" in r.stdout, r.stderr[-300:]
        r = _run([APPLY2, "--write"] + args)
        assert r.returncode == 0 and "WRITTEN" in r.stdout, r.stderr[-300:]
        r = _run([APPLY2, "--write"] + args)
        assert r.returncode == 0 and "already applied" in r.stdout, r.stderr[-300:]
        import yaml
        doc = yaml.safe_load(open(y, encoding="utf-8").read())
        prot = " ".join(doc["board_to_board"]["contracts"]["IF-EXT-DC"]["protection"].split())
        assert "D-10's guard-on case is OPEN" in prot and "no loop is claimed to pass" in prot and "PROVISIONAL, OPEN (B6-ENG-1" in prot
        dock = " ".join(doc["board_to_board"]["contracts"]["IF-AE-DOCK"]["pin1_vsys_dock"].split())
        assert "is a resistive extrapolation, not a bound" in dock and "never while U12 or U22 starts" in dock
        # a mixed state is refused: the old text of one edit put back beside the new texts
        t = open(h, encoding="utf-8").read()
        open(h, "w", encoding="utf-8").write(t + "\n| x | y | the backstop's trip and the guard's six bench rows; row 3 a pass only from a 3.30 uH loop until B6-ENG-1 |\n")
        r = _run([APPLY2, "--check"] + args)
        assert r.returncode == 3 and "not in the state" in r.stderr, r.stderr[-300:]
    finally:
        shutil.rmtree(d)


def t_the_l5f11_restatement_and_the_sweep_hold_on_the_tree_and_the_script_is_idempotent():
    """L5-F11 and set 28's sweep: no withdrawn wording in the tree's contract files; the second script writes nothing on the tree,
    and its own state there reads thirteen of its fourteen texts verbatim and F11-09 as W8 restated it; it applies once to the files
    at BASE3, writes nothing on a second run, and refuses on the files at BASE2 (ORDER).

    W14 (6 October 2026), decision (b): on the tree as W8 left it the script refuses at its ORDER check (lines 187 to 191), because
    apply_l5pwr2_contracts.py no longer answers "already applied" there (t_the_contract_restatement_of_l5f09_and_l5f10_is_in_the_tree_
    and_idempotent). The refusal is right (nothing may be written), its reason is not: every old text of apply_l5pwr2_contracts.py is
    gone from the tree, so it WAS applied, and four of its texts were then restated by W8. The detector tests the first script's
    verbatim texts where it should test the presence of what that script did (its old texts removed), the way set 30 corrected
    apply_l4e9_changelist_p0.py's applied_state(). The script is record l5pwr's and pinned, so it is not edited here: this test expects
    its CURRENT answer, exact to the character, and the proposed correction is test_w14l5.PATCH_L5F11_ORDER (checked there on copies;
    with it applied the answer becomes "not in the state this script applies to: F11-01: old text 0 time(s), new text present; ...",
    naming its fourteen edits with F11-09's new text absent, and this expectation changes with it). In place of the old "already
    applied": the script's own state, read with its own functions as its main() reads it after the ORDER check, is every old text
    gone, F11-01 to F11-08 and F11-10 to F11-14 verbatim, and F11-09
    restated by W8 with the properties of _w14_restated (its one Layer 4 value, L4-E9 8a's D-10 sentence at L4_AT, is the sentence
    set 31 withdrew, decision 11 of the page, and stands in W8's history row instead)."""
    import collections
    import re as _re
    need(APPLY3, "the L5-F11 script")
    a = _w14_load(APPLY3, "apply_l5f11_under_test")
    E = a.edits(collections.defaultdict(str))
    assert len(E) == 14
    tree = {"yaml": open(YAML, encoding="utf-8").read(), "hwfw": open(HWFW, encoding="utf-8").read()}
    for i, tg, _w, old, _n in E:
        assert not a.rx(old).search(tree[tg]), "%s: a withdrawn text is still in %s" % (i, tg)
    for k, t in tree.items():
        flat = " ".join(t.split())
        for pat in WITHDRAWN:
            assert not _re.search(pat, flat), "%s carries a withdrawn wording: %s" % (k, pat)
    b = _w14_load(APPLY2, "apply_l5pwr2_for_order")
    E2 = b.edits(collections.defaultdict(str))
    assert not [i for i, tg, _w, old, _n in E2 if b.rx(old).search(tree[tg])], "an old text of apply_l5pwr2_contracts.py is in the tree"
    # Restated by W35 (6 October 2026, set 31). Basis: f0d0e54e applied test_w14l5.PATCH_L5F11_ORDER to the script (its ORDER check
    # now reads the first script's old texts gone), so on this tree it no longer refuses at ORDER but with its own state, as the
    # docstring above says ("this expectation changes with it"). Quoted from a run on fnd/int31regen at 0f5b512c
    # (`apply_l5f11_contracts.py --check`: exit 3, stdout empty), stderr: "apply_l5f11_contracts: not in the state this script applies
    # to: F11-01: old text 0 time(s), new text present; [F11-02 to F11-08 the same]; F11-09: old text 0 time(s), new text absent;
    # [F11-10 to F11-14 the same as F11-01]; refusing, nothing written". Still exact to the character: each of its fourteen edits in
    # its own order, F11-09's new text absent (W8 restated it), every other new text present.
    want = "apply_l5f11_contracts: not in the state this script applies to: %s; refusing, nothing written\n" % "; ".join(
        "%s: old text 0 time(s), new text %s" % (i, "absent" if i in W8_RESTATED else "present") for i, _t, _w, _o, _n in E)
    r = _run([APPLY3, "--check"])
    assert r.returncode == 3 and r.stdout == "" and r.stderr == want, (r.returncode, r.stdout[-200:], r.stderr[-400:])
    V = a.l4()
    assert _w14_l5f11_state(a, V, tree) == [(i, 0, i not in W8_RESTATED) for i, _t, _w, _o, _n in E]
    quotes = _w14_history(a.flat, tree)
    for i, tg, where, _old, new in a.edits(V):
        if i in W8_RESTATED:
            live = _w14_live(a.flat, tg, where, tree)
            assert _w14_restated(a.flat, i, new, live, quotes, V.values(), "no loop claimed to pass", withdrawn=(V["d10"],)), i
    d = tempfile.mkdtemp(prefix="l5f11-apply-")
    try:
        y = os.path.join(d, "pcb_interfaces.yaml")
        h = os.path.join(d, "HW-FW-CONTRACT.md")
        args = ["--yaml", y, "--hwfw", h]
        for base, want in ((BASE2, "ORDER"), (BASE3, "CHECK OK, 14 edit(s)")):
            for f, rel in ((y, "v2/ecad/tools/pcb_interfaces.yaml"), (h, "v2/docs/HW-FW-CONTRACT.md")):
                g = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (base, rel)], capture_output=True)
                if g.returncode != 0:
                    raise Skip("commit %s is not in this repository" % base)
                open(f, "wb").write(g.stdout)
            r = _run([APPLY3, "--check"] + args)
            assert want in (r.stdout + r.stderr), (base, r.stdout[-200:], r.stderr[-300:])
        r = _run([APPLY3, "--write"] + args)
        assert r.returncode == 0 and "WRITTEN" in r.stdout, r.stderr[-300:]
        r = _run([APPLY3, "--write"] + args)
        assert r.returncode == 0 and "already applied" in r.stdout, r.stderr[-300:]
        for f in (y, h):
            flat = " ".join(open(f, encoding="utf-8").read().split())
            for pat in WITHDRAWN:
                assert not _re.search(pat, flat), "%s carries %s after the two scripts" % (os.path.basename(f), pat)
        import yaml
        doc = yaml.safe_load(open(y, encoding="utf-8").read())
        assert "guard-on case OPEN (L4-E9 8a" in " ".join(doc["board_to_board"]["contracts"]["IF-EXT-DC"]["l4_defects"].split())
        assert "never while U12 or U22 starts" in " ".join(doc["board_to_board"]["power_line_states"]["FAN1_SW_FAN2_SW"]["start"].split())
        assert "| 2 (L5-PWR, set 28) |" in open(h, encoding="utf-8").read()
    finally:
        shutil.rmtree(d)


def t_the_conops_draft_applies_once_to_a_copy_or_the_tree_already_carries_it():
    need(APPLY_CONOPS, "the CONOPS draft")
    d = tempfile.mkdtemp(prefix="l5pwr-conops-")
    try:
        cp = os.path.join(d, "CONOPS.md")
        shutil.copyfile(os.path.join(ROOT, "v2", "docs", "CONOPS.md"), cp)
        r = _run([APPLY_CONOPS, cp, "--check"])
        if r.returncode == 3:
            assert "already applied" in r.stderr, r.stderr[-200:]
        else:
            assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr[-200:]
            r = _run([APPLY_CONOPS, cp, "--write"])
            assert r.returncode == 0
            assert "**The margin hold (E5), a mode beyond the envelope.**" in open(cp, encoding="utf-8").read()
            r = _run([APPLY_CONOPS, cp, "--check"])
            assert r.returncode == 3 and "already applied" in r.stderr
    finally:
        shutil.rmtree(d)


def t_no_dashes_in_the_record_or_the_texts_written():
    files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(REC) for f in fs if f.endswith((".md", ".py", ".out", ".txt"))]
    files += [os.path.abspath(__file__)]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
    m = _M()
    for e in m.T:
        for s in (e["text"], e["mark"], e["trigger"]):
            assert chr(0x2014) not in s and chr(0x2013) not in s, e["id"]
    for p in (YAML, HWFW, PANEL):
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, os.path.relpath(p, ROOT)


# W1 (record l5pwr's correction, 6 October 2026): the evidence basis of the regression test below. Set 31 (fnd/l4e9s31 17ce29d5,
# merged into the candidate at 6fe398e9; v2/docs/records/l4e9/SET31-CHANGES.md items 2 and 23, PC-15, the owner's part 23) restated
# L4-E9's D-10. Until bbba3e53 the page's section 6 D-10 row read (line 838 there): "OPEN for the guard-on case: an absolute-rating
# violation at a connector fault (round 2's 3.30 uH WITHDRAWN as a passing floor; there U5's pins -0.3021 to +0.2591 V, past the
# -0.3 V absolute maximum; no loop claimed to pass; ..."; since set 31 it reads (line 839): "OPEN: an UNRESOLVED PROTECTION DEFECT in
# the present model, the receiving company's remaining engineering item E-1: the guard's port-level transient (F1 and F2
# absolute-rating violations below about 2.4 uH, ...". SET28_D10 is the pattern l5pwr_contracts.py held for the first (at 53a68c7c),
# which the set 30 integration's regen_out refused ("S27-B6: the replacing text is matched 0 times (not once)"); SET28_D10_TEXT is the
# opening of that sentence as bbba3e53's page printed it, used only to build a scratch copy of the page.
L4E9_PAGE = os.path.join(ROOT, "v2", "docs", "records", "l4e9", "L4-POWER-ARCHITECTURE.md")
L4E7_REC = os.path.join(ROOT, "v2", "docs", "records", "l4e7")
SET28_D10 = r"OPEN for the guard-on case: an absolute-rating violation at a connector fault \(round 2's \d+\.\d+ uH WITHDRAWN as a passing floor"
SET28_D10_TEXT = ("OPEN for the guard-on case: an absolute-rating violation at a connector fault (round 2's 3.30 uH WITHDRAWN as a passing "
                  "floor; there U5's pins -0.3021 to +0.2591 V, past the -0.3 V absolute maximum; no loop claimed to pass")


def t_s27b6_reads_d10_as_set31_left_it():
    """S27-B6's replacing texts are the page's as set 31 left them: each matched once (the script's rule, applied here without
    compute(), so the test names the failing pattern), one of them set 31's D-10 sentence with E-1, F1 to F4 and R-240, its parsed
    figures printed by record l4e7; set 28's pattern matches nothing on the page, and on a scratch copy carrying set 28's sentence in
    place of set 31's the old pattern matches once and the new one not at all. The row's meaning is kept (OPEN, NOT CLOSED, no loop
    claimed to pass, PROVISIONAL) and the withdrawn R-186 is named withdrawn in S27-B6's and S27-03's triggers."""
    need(SCRIPT, "the l5pwr record")
    need(L4E9_PAGE, "L4-E9's page")
    sp = importlib.util.spec_from_file_location("l5pwr_contracts_w1", SCRIPT)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    page = open(L4E9_PAGE, encoding="utf-8").read()
    rs = m.RESTATED["S27-B6"]
    assert all(k == "l4e9md" for k, _p in rs["now"]), "S27-B6's replacing texts are all L4-E9's page's"
    for _k, pat in rs["now"]:
        n = len(list(m.rx(pat).finditer(page)))
        assert n == 1, "S27-B6: the replacing text is matched %d times (not once) in the page: %r" % (n, pat[:70])
    d10 = [pat for _k, pat in rs["now"] if pat.startswith("OPEN: an UNRESOLVED PROTECTION DEFECT in the present model")]
    assert len(d10) == 1, "S27-B6 does not quote set 31's D-10 sentence"
    mo = next(m.rx(d10[0]).finditer(page))
    txt = m.flat(mo.group(0))
    for s in ("the receiving company's remaining engineering item E-1", "F1 and F2 absolute-rating violations", "F3", "F4",
              "corrected in draft by P0-7 (R-240)"):
        assert s in txt, s
    figs = m.figures_in(txt)
    l4e7 = " ".join(m.flat(open(os.path.join(L4E7_REC, f), encoding="utf-8").read()) for f in ("l4e7_p0sol.out", "L4E7-P0SOL.md"))
    assert len(figs) >= 6 and all(f in l4e7 for f in figs), "figures record l4e7 does not print: %s" % [f for f in figs if f not in l4e7]
    # set 28's pattern on the page as set 31 left it: no match (the refusal this corrects)
    assert not list(m.rx(SET28_D10).finditer(page)), "set 28's D-10 sentence is printed again; S27-B6 would quote the wrong one"
    # a scratch copy of the page with set 28's sentence where set 31's stands: the old pattern once, the new one never
    old_page = page[:mo.start()] + SET28_D10_TEXT + page[mo.end():]
    assert len(list(m.rx(SET28_D10).finditer(old_page))) == 1
    assert not list(m.rx(d10[0]).finditer(old_page)), "the D-10 pattern also matches set 28's sentence: it does not read set 31's"
    # the row's meaning, kept and not widened
    assert "OPEN" in rs["mark"] and "PROVISIONAL" in rs["mark"] and "NOT CLOSED" in rs["value"]
    assert "no loop is claimed to pass" in rs["value"] and "before any passing claim" in rs["trigger"]
    for i in ("S27-B6", "S27-03"):
        tr = m.RESTATED[i]["trigger"]
        assert "R-186 WITHDRAWN under R-240" in tr and "R-186 Analog Devices" not in tr, i
    page5 = open(PAGE, encoding="utf-8").read()
    assert "| L5-F14 |" in page5, "the contracts' lag behind set 31's D-10 needs its finding"
