"""Layer 5's second round (MESHSAT-1357, 3 October 2026; v2/docs/records/l5r2/): the pass-2 fields on every interface contract, the
fans after D-18 and L4-E11 section 18, the SLOT_EN keeper and GND-002 after record l8gnd, held as predicates on the contract files
and on what the record's reader computes.

The predicates: the committed l5r2_interfaces.out is what the reader prints (it refuses an excerpt not in its target, a figure no
cited source prints, a copied input whose body does not hash to its declared sha, a lost leaf of an old block and a tbd entry without
an owner); every contract in the file carries every pass-2 field and a part on every board end (hc5's own check); every contract's
`pins` map agrees with the committed netlists at its first two board ends (aliases allowed), a property that survives regeneration;
every entry of the yaml that rests on a commit outside this branch (b929d8be, 226e9143) says PROVISIONAL; the copied inputs name
their source and hash to their declaration; the SLOT_EN line carries the keeper's hold and the fans their regulated rail; the
HW-FW-CONTRACT rows the round touched keep their tables' cell counts, unique ids and the R228 name; the apply script applies once to
the base and refuses a second run; the page's table is the reader's; no em or en dash in the record. Software predicates on text:
they establish no electrical property and accept nothing.
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
REC = os.path.join(ROOT, "v2", "docs", "records", "l5r2")
SCRIPT = os.path.join(REC, "l5r2_interfaces.py")
OUT = os.path.join(REC, "l5r2_interfaces.out")
PAGE = os.path.join(REC, "L5-INTERFACES-R2.md")
APPLY = os.path.join(REC, "apply_l5r2.py")
YAML = os.path.join(TOOLS, "pcb_interfaces.yaml")
HWFW = os.path.join(ROOT, "v2", "docs", "HW-FW-CONTRACT.md")
HC5 = os.path.join(ROOT, "v2", "docs", "records", "hc5", "check_contract_fields.py")
NETS = {"a": "pcb-a-power-a23/out/pcb-a-power.net", "b": "pcb-b-compute-b19/out/pcb-b-compute.net",
        "c": "pcb-c-display-c8/out/pcb-c-display.net", "d": "pcb-d-aprs-d9/out/pcb-d-aprs.net", "e": "pcb-e1-dock-e7/out/pcb-e1-dock.net",
        "p": "pcb-p-pack-p2/out/pcb-p-pack.net"}
FOREIGN = ("b929d8be", "226e9143")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l5r2 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the reader reads the base from this branch's history)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l5r2_interfaces_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l5r2_interfaces.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _doc(path=YAML):
    import yaml
    return yaml.safe_load(open(path, encoding="utf-8"))


def _hc5():
    sp = importlib.util.spec_from_file_location("hc5_under_test", need(HC5, "hc5's field checker"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _cells(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return [c.strip() for c in s[1:-1].split("|")]


def t_output_reproduced_byte_for_byte():
    _M()
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l5r2_interfaces.out is not what the reader prints"


def t_every_contract_carries_every_pass_two_field_and_a_part_on_every_board_end():
    m = _hc5()
    cs = _doc()["board_to_board"]["contracts"]
    bad = {cid: m.check(cid, c, True) for cid, c in cs.items()}
    bad = {k: v for k, v in bad.items() if v}
    assert not bad, "contracts failing the field contract: %s" % {k: v[:2] for k, v in bad.items()}
    assert "IF-A-CHASSIS" in cs and cs["IF-A-CHASSIS"]["kind"] == "board_to_case"


def _pinmap(letter, ref):
    p = os.path.join(ROOT, "v2", "ecad", NETS[letter])
    need(p, "the committed netlist")
    txt = open(p, encoding="utf-8", errors="replace").read()
    out = {}
    for mm in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', txt, re.S):
        name = mm.group(1).lstrip("/")
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', mm.group(2)):
            if n.group(1) == ref:
                out[n.group(2)] = name
    return out


def t_every_pins_map_agrees_with_the_committed_netlists():
    cs = _doc()["board_to_board"]["contracts"]
    judged = 0
    for cid, c in cs.items():
        alias = {tuple(sorted(a[:2])) for a in (c.get("aliases") or [])}
        for e in c.get("ends", []):
            if not isinstance(e, dict) or e.get("board") not in NETS:
                continue
            ref = e.get("ref") if isinstance(e.get("ref"), str) else (e.get("refs") or [None])[0] if isinstance(e.get("refs"), list) else None
            pins = e.get("pins") if isinstance(e.get("pins"), dict) else c.get("pins")
            if not ref or not isinstance(pins, dict) or not all(isinstance(k, int) for k in pins):
                continue
            got = _pinmap(e["board"], ref)
            if not got:
                continue
            e = dict(e, ref=ref)
            for k, want in pins.items():
                have = got.get(str(k), "")
                assert have == str(want) or tuple(sorted((have, str(want)))) in alias, \
                    "%s: %s %s pin %s is %r in the netlist and %r in the contract" % (cid, e["board"], e["ref"], k, have, want)
            judged += 1
    assert judged >= 10, "too few pin maps judged (%d)" % judged


def _entries(doc):
    b = doc["board_to_board"]
    for k, v in (b.get("power_line_states") or {}).items():
        yield "power_line_states." + k, v
    for k, v in b["contracts"].items():
        yield k, v


def _text(o):
    if isinstance(o, dict):
        return " ".join(_text(v) for v in o.values())
    if isinstance(o, list):
        return " ".join(_text(v) for v in o)
    return " ".join(str(o).split())


def t_every_entry_resting_on_a_foreign_commit_says_provisional():
    hits = 0
    for name, v in _entries(_doc()):
        t = _text(v)
        if any(c in t for c in FOREIGN):
            hits += 1
            assert "PROVISIONAL" in t, "%s cites %s and is not marked PROVISIONAL" % (name, [c for c in FOREIGN if c in t])
    assert hits >= 8, hits


def t_the_copied_inputs_name_their_source_and_hash_to_their_declaration():
    import hashlib
    names = sorted(f for f in os.listdir(os.path.join(REC, "inputs")) if f.endswith(".md"))
    for need_ in ("l4e11-section-18-b929d8be.md", "l8gnd-sections-2-3-226e9143.md", "fw-panel-sections-5-6-42c27369.md",
                  "l8r2-section-3d-29ffb518.md"):
        assert need_ in names, need_
    for n in names:
        t = open(os.path.join(REC, "inputs", n), encoding="utf-8").read()
        head = t.split("<!-- BODY BEGIN -->")[0]
        for s in ("Source: branch", "at commit", "whose sha256 at that commit is", "no git command reads it"):
            assert s in head, (n, s)
        commit = n.rsplit("-", 1)[1][:-3]
        assert commit in head, (n, commit)
        m = re.search(r"the body's own sha256 is ([0-9a-f]{64})", head)
        body = t.split("<!-- BODY BEGIN -->\n", 1)[1].split("<!-- BODY END -->")[0]
        assert m and hashlib.sha256(body.encode("utf-8")).hexdigest() == m.group(1), n


def t_the_slot_en_line_carries_the_keeper_and_the_fans_their_rail():
    doc = _doc()
    pls = doc["board_to_board"]["power_line_states"]
    hold = " ".join(pls["SLOT_EN1..3"]["hold"].split())
    for s in ("U43", "R230 to R232", "2.547 V", "0.266 V", "NOT across a loss of the panel's supply", "PROVISIONAL", "FW-C02"):
        assert s in hold, s
    assert "U22_RUN_12V_FAN" in pls and "8.33 V" in pls["U22_RUN_12V_FAN"]["reset"]
    cs = doc["board_to_board"]["contracts"]
    ef = _text(cs["IF-E-FANS"])
    for s in ("9WL0612P4H001", "+12V_FAN", "10.8 to 13.2 V", "NOT READ", "PROVISIONAL"):
        assert s in ef, s
    bf = _text(cs["IF-B-FANS"])
    for s in ("9WPA0412P6G001", "E11-40", "PROVISIONAL", "+5V_Sn"):
        assert s in bf, s
    assert "R229" in _text(cs["IF-A-CHASSIS"]) and "CHASSIS" in _text(cs["IF-EXT-ETH"]["grounding"])


def t_the_contract_rows_touched_keep_their_tables():
    t = open(HWFW, encoding="utf-8").read()
    width, ids = None, {}
    for l in t.split("\n"):
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
            ids[c[0]] = " | ".join(c)
    assert "U43" in ids["FW-C02"] and "PROVISIONAL" in ids["FW-C02"] and "2.547 V" in ids["FW-C02"]
    assert "R228" in ids["FW-E11"] and "R221 11.0 kOhm" not in ids["FW-E11"] and "never while U12 or U22 starts" in ids["FW-E11"]
    assert "2.5 V" in ids["V-C02"] and "+12V_FAN" in ids["FW-E07"]
    assert "| 2 (L5-R2) |" in t and "Version 2, round 2" in t


def t_the_apply_script_applies_once_to_the_base_and_refuses_a_second_run():
    need(APPLY, "the patch script")
    for tree in (YAML, HWFW):
        r = subprocess.run([sys.executable, "-B", APPLY, tree, "--check"], capture_output=True, text=True)
        assert r.returncode == 3 and "already applied" in r.stderr, (tree, r.stderr[-200:])
    m = _M()
    d = tempfile.mkdtemp(prefix="l5r2-apply-")
    try:
        for rel in ("v2/ecad/tools/pcb_interfaces.yaml", "v2/docs/HW-FW-CONTRACT.md"):
            r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (m.BASE, rel)], capture_output=True)
            assert r.returncode == 0
            f = os.path.join(d, os.path.basename(rel))
            open(f, "wb").write(r.stdout)
            for flag, code in (("--check", 0), ("--write", 0), ("--check", 3)):
                r2 = subprocess.run([sys.executable, "-B", APPLY, f, flag], capture_output=True, text=True)
                assert r2.returncode == code, (rel, flag, r2.stderr[-300:])
        cs = _doc(os.path.join(d, "pcb_interfaces.yaml"))["board_to_board"]["contracts"]
        hc5 = _hc5()
        assert not [c for c in cs if hc5.check(c, cs[c], True)], "the patched base fails the field contract"
        r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, "v2", "docs", "records", "l4e11", "apply_pcb_interfaces_dock.py"),
                            os.path.join(d, "pcb_interfaces.yaml"), "--check"], capture_output=True, text=True)
        assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr[-200:]
    finally:
        shutil.rmtree(d)


def t_the_pages_table_is_the_readers():
    m = _M()
    page = open(PAGE, encoding="utf-8").read()
    i, j = page.index("<!-- l5r2-table:begin -->"), page.index("<!-- l5r2-table:end -->")
    block = [l for l in page[i:j].split("\n")[1:] if l.strip()]
    assert block == m.md_rows(_C["R"]), "the page's table is not the reader's"
    for s in ("PASS 99 of 99", "PROVISIONAL", "## 9.", "L5R2-F04"):
        assert s in page, s


def t_no_dashes_in_the_record():
    files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(REC) for f in fs if f.endswith((".md", ".py", ".out"))]
    files += [os.path.abspath(__file__), YAML, HWFW]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)


# ------------------------------------------------------------------------------------------------ round 3 (the panel's contract)
R3SCRIPT = os.path.join(REC, "l5r3_panel.py")
R3OUT = os.path.join(REC, "l5r3_panel.out")
R3PAGE = os.path.join(REC, "L5-PANEL-R3.md")
R3APPLY = os.path.join(REC, "apply_l5r3.py")
PANEL = os.path.join(ROOT, "v2", "docs", "PANEL.md")
ASSEMBLY = os.path.join(ROOT, "v2", "docs", "ASSEMBLY.md")


def _R3():
    if "R3" not in _C:
        sp = importlib.util.spec_from_file_location("l5r3_panel_under_test", need(R3SCRIPT, "the round 3 reader"))
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l5r3_panel.py refused (exit %s)" % e.code)
        _C.update(R3=m, R3R=R, R3text=m.render(R))
    return _C["R3"]


def t_r3_output_reproduced_and_every_finding_resolved():
    m = _R3()
    assert _C["R3text"] == open(R3OUT, encoding="utf-8").read(), "l5r3_panel.out is not what the reader prints"
    assert {f for e in m.T for f in m.FINDINGS if e["finding"].startswith(f + " ")} == set(m.FINDINGS)
    assert len(_C["R3R"]["cover"]) == 36 and all(_C["R3R"]["cover"].values())


def t_r3_the_panel_page_states_one_value_where_it_stated_two():
    t = " ".join(open(PANEL, encoding="utf-8").read().split())
    assert "never dimmed below 10 % duty" not in t, "the TX lamp's floor contradicting NVG's 2 % is back"
    assert "first writes the configuration registers so every LED bit is an input" not in t
    assert "for 3 s, a chirp, the battery bar" not in t and "a double chirp" in t
    warn = t.split("MASTER WARN flashes (3 to 5 Hz) for any unacknowledged red condition (")[1].split(";")[0]   # the list, not its note
    assert "slot fault" not in warn and "two compute modules lost" in warn
    assert "refresh at most once a minute," not in t and "a change of page refreshes at once" in t
    assert "SOS QUEUED: MARGIN HOLD, COOLING" in t and "slot 3 = `HDMI_SEL2` high" in t
    assert "until the operator acts." not in t


def t_r3_the_contract_rows_carry_the_decisions_and_their_tables_hold():
    t = open(HWFW, encoding="utf-8").read()
    rows = {}
    for l in t.split("\n"):
        c = _cells(l)
        if c and re.match(r"^(FW|V)-[A-Z]\d\d$", c[0]):
            assert c[0] not in rows, "row %s occurs twice" % c[0]
            rows[c[0]] = " ".join(" | ".join(c).split())
    assert "30 minutes have passed" in rows["FW-C14"] and "X_SA_PD 1" in rows["FW-D01"] and "X_MMUTE 0" in rows["FW-D01"]
    assert "SOS QUEUED: MARGIN HOLD, COOLING" in rows["FW-C15"] and "PI_BTN_n" in rows["FW-C03"]
    assert "### 3.8 Values adopted from the panel firmware" in t and "| 2 (L5-R3) |" in t


def t_r3_the_pi_texts_are_drafted_and_provisional_with_their_trigger():
    trig = "PROVISIONAL until l8r2's apply_gen_sch_c_pibtn.py is released and board C regenerated"
    for path, n in ((PANEL, 3), (ASSEMBLY, 1), (HWFW, 1)):
        t = " ".join(open(path, encoding="utf-8").read().split())
        assert t.count(trig) >= n, (os.path.basename(path), t.count(trig))
        assert "PI_BTN_n" in t or "U1 P1.3" in t


def t_r3_the_apply_script_refuses_a_second_run():
    for path in (PANEL, HWFW, ASSEMBLY):
        r = subprocess.run([sys.executable, "-B", need(R3APPLY, "the round 3 patch"), path, "--check"], capture_output=True, text=True)
        assert r.returncode == 3 and "already applied" in r.stderr, (path, r.stderr[-200:])


def t_r3_the_pages_table_is_the_readers():
    m = _R3()
    page = open(R3PAGE, encoding="utf-8").read()
    i, j = page.index("<!-- l5r3-table:begin -->"), page.index("<!-- l5r3-table:end -->")
    block = [l for l in page[i:j].split("\n")[1:] if l.strip()]
    assert block == m.md_rows(_C["R3R"]), "the round 3 page's table is not the reader's"
