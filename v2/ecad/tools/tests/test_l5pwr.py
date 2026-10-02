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
the base they were written against; no em or en dash in the record. Software predicates on text: they establish no electrical
property and accept nothing.
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
    for e in m.T:
        assert any(w in e["mark"] for w in MARKS) or e["mark"].startswith("DRAFTED"), (e["id"], e["mark"])
        assert set(e["criteria"]) <= set(m.CRITERIA) and e["criteria"], e["id"]
        if "PROVISIONAL" in e["mark"]:
            assert re.search(r"(R-\d+|E11-\d+|B6-ENG-1|PANEL-ACC|PWR-F\d+|Q-TI-\d+|U-0\d|V-A0\d|T-H1|M2)", e["trigger"]), \
                "%s is PROVISIONAL but its trigger names no row or measurement: %r" % (e["id"], e["trigger"])
    prov = [e for e in m.T if "PROVISIONAL" in e["mark"]]
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
    assert list(pls) == LINES, list(pls)
    for ln, v in pls.items():
        for k in ("default", "firmware", "source"):
            assert v.get(k), (ln, k)
        assert "reset" in v or "threshold" in v, ln
        assert "cable_out" in v or ln in ("U34_restart_guard", "SWEN"), ln
    assert "OWED" in pls["SLOT_EN1..3"]["hold"] and "FW-C02" in pls["SLOT_EN1..3"]["hold"]
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
    for s in ("PASS 99 of 99", "## 9.", "PROVISIONAL", "check_contracts.py"):
        assert s in page, s


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
        # the base files patched read as the tree's files: the script is the whole change
        for f, tree in ((y, YAML), (h, HWFW), (p, PANEL)):
            assert open(f, "rb").read() == open(tree, "rb").read(), "%s patched from the base differs from the tree" % os.path.basename(tree)
        # L4-E11's dock draft still applies to the patched yaml
        r = _run([os.path.join(ROOT, "v2", "docs", "records", "l4e11", "apply_pcb_interfaces_dock.py"), y, "--check"])
        assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr[-200:]
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
