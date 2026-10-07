"""W8 (MESHSAT-1357, 6 October 2026): the Layer 5 contract files' stale D-10 and R-186 statements restated to L4-E9's D-10 as set
31 left it (finding L5-F14 of record l5pwr, read at fnd/w1l5pwr 6ab17e21 as text only).

ADOPTED IN THE NEXT SET, NOT IN THE SET 30 CANDIDATE: pcb_interfaces.yaml is a CONFIG_INPUT pinned by the registry and by records,
and HW-FW-CONTRACT.md is pinned by records; the re-pins of the readers that pin either file and the interfaces.py re-take come with
this branch's adoption. Base: integration commit 2c, 53a68c7c on fnd/p0pwr.

The five statements (base line numbers): pcb_interfaces.yaml IF-EXT-DC `protection` (1255 to 1262), `bench` (1291) and `l4_defects`
(1296 to 1297); HW-FW-CONTRACT.md section 4.1's R-173 row (261) and V-E16 (313). Their sources, in this tree: L4-E9's page
`v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md` (section 6 D-10 line 839, 8a D-10 line 1026, D-16 line 1031, the history note line
1045, the ledger rows HO-F line 1353 and D-10 line 1384), `v2/docs/records/l4e9/SET31-CHANGES.md` (items 2, 10 and 23),
`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md` (R-186 line 282: WITHDRAWN 6 October 2026, set 31, obsolete under R-240; R-176 line 272,
unchanged by set 31), `v2/docs/records/l4e7/L4E7-P0SOL.md` (section 4 lines 99 to 126, line 157, section 5 lines 161 to 168) and
`v2/docs/records/l4close/REMAINING-ENGINEERING.md` (HO-F lines 484 to 505).

The predicates (software predicates on text; they establish no electrical property and accept nothing):
1. The tree's five statements carry none of set 28's D-10 or R-186 wordings, every R-186 they name is WITHDRAWN, every B6-ENG-2 is
   answered at the desk, every B6-ENG-1 sits beside its set 31 name E-1, and each states D-10 as set 31 does: OPEN, an UNRESOLVED
   PROTECTION DEFECT, E-1, R-240, PROVISIONAL, no loop claimed to pass. The detector PARSES (the YAML by a YAML reader, the page by
   its table rows), so the change record's dated history is never read as a live statement.
2. The detector both ways: on the files at the base it reports every one of the five; on the tree none; a scratch copy of the tree
   with set 28's R-186 clause put back is reported.
3. The protection field's quotation is L4-E9's section 6 D-10 row verbatim, matched once in the page, and every figure it prints is
   printed by record l4e7.
4. Narrower, never wider: no statement calls D-10 closed, met, resolved, passing or addressed in drafts.
5. Nothing else moved (between the base and W8_COMMIT, both in this branch's history): the parsed YAML differs only in those three
   fields; HW-FW-CONTRACT.md only in the R-173 row's third cell, V-E16's parenthetical after row 3 and one appended change record
   row; every table row keeps its cell count; V-E16's rows 2 and 3 are still the register's R-176 rows verbatim (no bench figure,
   level, pin, capacity or sequencing text changed).
6. The change record row keeps the superseded wordings verbatim as dated history and says the branch is adopted in the NEXT set.
7. No em or en dash in the two files or this module.
"""
import os
import re
import subprocess
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
YAML_REL = "v2/ecad/tools/pcb_interfaces.yaml"
HWFW_REL = "v2/docs/HW-FW-CONTRACT.md"
PAGE = os.path.join(ROOT, "v2", "docs", "records", "l4e9", "L4-POWER-ARCHITECTURE.md")
REG = os.path.join(ROOT, "v2", "docs", "records", "l4e9", "DOWNSTREAM-REGISTER.md")
L4E7 = [os.path.join(ROOT, "v2", "docs", "records", "l4e7", f) for f in ("L4E7-P0SOL.md", "l4e7_p0sol.out")]
BASE = "53a68c7c"     # integration commit 2c on fnd/p0pwr: the files as set 28 left the five statements
W8_COMMIT = "8840adda"   # fnd/w8l5: the commit carrying the restatement (in this branch's history); None reads the tree
FIELDS = ("protection", "bench", "l4_defects")
ROWS = ("| R-173 the solar guard", "| V-E16 |")

from harness import need, Skip  # noqa: E402

# set 28's wordings (record l5pwr's apply_l5pwr2_contracts.py edits L5-F09 a to d and apply_l5f11_contracts.py F11-09, as the
# files at BASE carry them): a live statement that carries one of these names a superseded reason or a withdrawn route (L5-F14)
STALE = [r"D-10's guard-on case is OPEN since L4-E7's round \d+, an absolute-rating violation at a connector fault",
         r"B6-ENG-1, the engineer's stage question",
         r"R-186 Analog Devices' answer",
         r"its wider form B6-ENG-2, R-189, D-16",
         r"B6-ENG-1 decides: PROVISIONAL, OPEN, B6-ENG-1 and B6-ENG-2",
         r"guard-on case OPEN \(L4-E9 8a: an absolute-rating violation at a connector fault",
         r"PROVISIONAL: B6-ENG-1, B6-ENG-2",
         r"D-10 \(a stiff \d+ V source on the solar port\) and D-11 \(a reversed panel\) addressed in drafts",
         r"B6-ENG-1 decides \(PROVISIONAL, OPEN: B6-ENG-1, B6-ENG-2\)",
         r"PROVISIONAL, OPEN: D-10's guard-on case;",
         r"B6-ENG-1 and B6-ENG-2: R-180, R-186, R-187, R-189"]
# what set 31 states (L4-POWER-ARCHITECTURE.md line 839 and 1026; SET31-CHANGES.md items 2 and 23)
WANT = ("UNRESOLVED PROTECTION DEFECT", "E-1", "R-240", "PROVISIONAL", "OPEN")
WIDER = r"D-10(?: is|'s guard-on case)? (?:is )?(?:CLOSED|closed|MET|met|resolved|RESOLVED|passes|PASS|addressed in drafts)"


def flat(s):
    return " ".join(s.split())


def git_show(commit, rel):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    if r.returncode != 0:
        raise Skip("commit %s is not in this repository" % commit)
    return r.stdout.decode("utf-8")


def tree(rel):
    p = os.path.join(ROOT, rel)
    need(p, rel)
    return open(p, encoding="utf-8").read()


def cells(line):
    s = line.strip()
    return [c.strip() for c in s[1:-1].split("|")] if s.startswith("|") and s.endswith("|") else None


def statements(ytext, htext):
    """{name: text} of the five statements: the three IF-EXT-DC fields by a YAML reader, the two contract rows by their first cell."""
    import yaml
    c = yaml.safe_load(ytext)["board_to_board"]["contracts"]["IF-EXT-DC"]
    out = {f: flat(c[f]) for f in FIELDS}
    for w in ROWS:
        ls = [ln for ln in htext.split("\n") if ln.startswith(w)]
        assert len(ls) == 1, "%d rows start with %r" % (len(ls), w)
        out[w.strip("| ").split(" ")[0]] = flat(" | ".join(cells(ls[0])))
    return out


def findings(st):
    """Every stale statement: (name, what). Empty when the five read as set 31 states D-10."""
    bad = []
    for k, t in st.items():
        for p in STALE:
            if re.search(p, t):
                bad.append((k, "set 28's wording: " + p))
        for m in re.finditer(r"R-186", t):
            if not t[m.end():].startswith(" WITHDRAWN"):
                bad.append((k, "R-186 named as a live item"))
        for m in re.finditer(r"B6-ENG-2", t):
            if not t[m.end():].startswith(" answered at the desk"):
                bad.append((k, "B6-ENG-2 not answered at the desk"))
        for m in re.finditer(r"B6-ENG-1", t):
            near = t[max(0, m.start() - 300):m.end() + 300]
            if not re.search(r"(?<![\w-])E-1\b", near) or "set 29's" not in near:
                bad.append((k, "B6-ENG-1 without its set 31 name E-1"))
        for w in WANT:
            if w not in t:
                bad.append((k, "lacks %r" % w))
        if not re.search(r"no loop (is )?claimed to pass", t):
            bad.append((k, "lacks: no loop claimed to pass"))
        if re.search(WIDER, t):
            bad.append((k, "a wider claim: " + re.search(WIDER, t).group(0)))
    return bad


def t_the_tree_states_d10_as_set31_does_in_all_five():
    st = statements(tree(YAML_REL), tree(HWFW_REL))
    assert set(st) == {"protection", "bench", "l4_defects", "R-173", "V-E16"}
    bad = findings(st)
    assert not bad, bad
    for k in ("protection", "V-E16"):
        assert "R-186 WITHDRAWN under R-240" in st[k], k
    for k in st:
        assert "PROVISIONAL on S3 and S4" in st[k] and "D-16 ADDRESSED IN DRAFTS" in st[k], k
        assert "S1 and S2" in st[k], k


def t_the_detector_reports_each_of_set_28s_statements_and_a_mutation():
    st0 = statements(git_show(BASE, YAML_REL), git_show(BASE, HWFW_REL))
    hit = {k for k, _w in findings(st0)}
    assert hit == {"protection", "bench", "l4_defects", "R-173", "V-E16"}, hit
    for k in st0:
        assert any(w.startswith("set 28's wording") for kk, w in findings({k: st0[k]})), k
    # a scratch copy of the tree with set 28's R-186 clause put back into V-E16 is reported
    h = tree(HWFW_REL)
    d = tempfile.mkdtemp(prefix="w8l5-")
    try:
        p = os.path.join(d, "HW-FW-CONTRACT.md")
        mut = h.replace("R-186 WITHDRAWN under R-240; B6-ENG-2 answered at the desk: L4-E9's",
                        "R-186 Analog Devices' answer; B6-ENG-2 answered at the desk: L4-E9's", 1)
        assert mut != h, "the mutation's anchor is not in V-E16"
        open(p, "w", encoding="utf-8").write(mut)
        bad = findings(statements(tree(YAML_REL), open(p, encoding="utf-8").read()))
        assert ("V-E16", "R-186 named as a live item") in bad and any(k == "V-E16" and "set 28" in w for k, w in bad), bad
    finally:
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
        os.rmdir(d)


def t_the_quotation_is_the_pages_d10_row_and_its_figures_are_record_l4e7s():
    need(PAGE, "L4-E9's page")
    st = statements(tree(YAML_REL), tree(HWFW_REL))
    m = re.search(r"in L4-E9's words '(.+?)' \(L4-POWER-ARCHITECTURE\.md section 6, D-10", st["protection"])
    assert m, "the protection field does not quote L4-E9's D-10 row"
    q = m.group(1)
    rows = [flat(" | ".join(cells(ln))) for ln in open(PAGE, encoding="utf-8").read().split("\n")
            if cells(ln) and cells(ln)[0] == "D-10"]
    assert sum(r.count(q) for r in rows) == 1, "the quotation is not matched once in the page's D-10 rows"
    assert q.startswith("an UNRESOLVED PROTECTION DEFECT in the present model, the receiving company's remaining engineering item E-1")
    assert "corrected in draft by P0-7 (R-240)" in q and "the lower-source back-feed" in q
    figs = re.findall(r"\d+(?:\.\d+)? (?:uH|V/us|V)\b", q)
    src = " ".join(flat(open(f, encoding="utf-8").read()) for f in L4E7 if os.path.isfile(f))
    need(L4E7[0], "record l4e7")
    assert len(figs) >= 7 and all(f in src for f in figs), [f for f in figs if f not in src]


def t_nothing_else_moved_and_the_bench_rows_are_still_the_registers():
    import yaml
    ytx = git_show(W8_COMMIT, YAML_REL) if W8_COMMIT else tree(YAML_REL)
    htx = git_show(W8_COMMIT, HWFW_REL) if W8_COMMIT else tree(HWFW_REL)
    y0, h0 = git_show(BASE, YAML_REL), git_show(BASE, HWFW_REL)
    d0, d1 = yaml.safe_load(y0), yaml.safe_load(ytx)
    c0, c1 = d0["board_to_board"]["contracts"]["IF-EXT-DC"], d1["board_to_board"]["contracts"]["IF-EXT-DC"]
    assert sorted(k for k in set(c0) | set(c1) if c0.get(k) != c1.get(k)) == sorted(FIELDS)
    d1["board_to_board"]["contracts"]["IF-EXT-DC"] = c0
    assert d1 == d0, "a YAML field other than IF-EXT-DC's protection, bench and l4_defects changed"
    l0, l1 = h0.split("\n"), htx.split("\n")
    assert len(l1) == len(l0) + 1 and l0[-1] == "" and l1[-1] == ""
    moved = [(a, b) for a, b in zip(l0[:-1], l1[:-2]) if a != b]   # every line but the appended change record row
    assert [a.split(" | ")[0] for a, _b in moved] == ["| R-173 the solar guard (`records/l4e7/apply_gen_sch_e_solar_guard.py`); R-12, R-19 to R-21, R-98 the stage's settings", "| V-E16"]
    for a, b in moved:
        ca, cb = cells(a), cells(b)
        assert len(ca) == len(cb) and ca[:-1] == cb[:-1], "a cell other than the last moved"
    # R-173: the cell keeps its text up to row 3's no-pass clause; V-E16: everything but the parenthetical after row 3
    a, b = cells(moved[0][0])[-1], cells(moved[0][1])[-1]
    keep = "at row 3 no loop is claimed to pass (round 5)"
    assert a[:a.index(keep) + len(keep)] == b[:b.index(keep) + len(keep)]
    a, b = cells(moved[1][0])[-1], cells(moved[1][1])[-1]
    head, tail = "B6-ENG-1 decides (", "; (4) a reversed bench panel's curve"
    assert a[:a.index(head)] == b[:b.index(head)] and a[a.index(tail):] == b[b.index(tail):]
    # V-E16's rows 2 and 3 are the register's R-176 rows 2 and 3, verbatim (record l5pwr's L5-F09 d wrote them so): stated on the
    # fixture, the register AS IT STOOD AT W8_COMMIT, because the register moved afterwards by one intended change: the coordinator's
    # N1a (set 31, commit b2564b59, 6 Oct 2026) annotated row 3's U5 line alone, and the live comparison failed on exactly that
    # (a rule that fails when its subject is fixed is a rule about history). The live register is then checked to differ from W8's by
    # N1A_WORDS and nothing else; carrying the annotation into V-E16 itself is set 32's (it moves l4e11_power.out and the l4e7 KEY).
    N1A_WORDS = " (under R-240, drafted, not applied: under 10 mV in magnitude, a layout check, L4E7-P0SOL.md section 5)"
    REG_REL = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
    def r176_rows(text):
        rows = [cells(ln) for ln in text.split("\n") if ln.startswith("| R-176 | TEST |")]
        assert len(rows) == 1
        rr = rows[0][2]
        return rr[rr.index("(2) "):rr.index("; (4) ")]
    want = r176_rows(git_show(W8_COMMIT, REG_REL) if W8_COMMIT else tree(REG_REL))
    assert b[b.index("(2) "):b.index(" (PROVISIONAL until E-1's correction")] == want
    need(REG, "the register")
    live = r176_rows(open(REG, encoding="utf-8").read())
    assert live.count(N1A_WORDS) == 1 and live.replace(N1A_WORDS, "") == want, "the live register's R-176 rows 2 and 3 differ from W8's by more than N1a's annotation"
    # Q-55 (set 32, record s32small, applied by apply_q55_ve16.py): V-E16's row 3 carries N1a's annotation at the place the
    # register's R-176 row 3 carries it, so V-E16 read from the TREE equals the live register's rows 2 and 3 verbatim; the
    # fixture form above stays for W8's own change. Basis: the record's own invariant, V-E16 mirrors the register (record
    # l5pwr's L5-F09 d wrote it so), and the coordinator's decision of 6 October 2026 15:22 CEST (QUEUE line Q-55).
    ve16 = [cells(ln) for ln in tree(HWFW_REL).split("\n") if ln.startswith("| V-E16 |")]
    assert len(ve16) == 1, "%d V-E16 rows in the tree" % len(ve16)
    v = ve16[0][-1]
    assert v[v.index("(2) "):v.index(" (PROVISIONAL until E-1's correction")] == live, "V-E16's rows 2 and 3 in the tree are not the live register's R-176 rows 2 and 3"
    # Q-55's change record row (W47, QUEUE line Q-65): one row in the form of W8's (three cells), dated, after W8's row,
    # carrying N1a's words and the wording before; the assertion on W8's row below reads W8_COMMIT, not the tree. And
    # TP-SOLAR.md quotes the register's annotated U5 line once as a text quote (tp_check.py's C3 holds it verbatim there).
    h = tree(HWFW_REL).split("\n")
    q55 = [k for k, ln in enumerate(h) if ln.startswith("| 2 (Q-55, set 32) |")]
    w8 = [k for k, ln in enumerate(h) if ln.startswith("| 2 (W8, L5-F14) |")]
    assert len(q55) == 1 and len(w8) == 1 and q55[0] > w8[0], "Q-55's change record row is not once, after W8's"
    c = cells(h[q55[0]])
    assert len(c) == 3 and c[1] == "6 October 2026" and c[2].count(N1A_WORDS.strip()) == 1, "Q-55's row is not in W8's form"
    assert "\"U5's CSPIN to CSNIN within +-0.240 V, U21 turning Q12 off\"" in c[2], "Q-55's row lacks the wording before"
    qs = [flat(re.sub(r"(?m)^\s*>", "", b)) for b in re.findall(r'<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER\.md" -->\n(.*?)\n<!-- /q -->', tree("v2/docs/test-procedures/TP-SOLAR.md"), re.S)]
    assert qs.count(flat("U5's CSPIN to CSNIN within +-0.240 V" + N1A_WORDS)) == 1, "TP-SOLAR.md does not quote the register's annotated U5 line once"
    # the change record: one row appended, three cells
    assert l1[-2].startswith("| 2 (W8, L5-F14) |") and len(cells(l1[-2])) == 3 and l1[-1] == ""


def t_the_change_record_keeps_the_superseded_wording_and_names_the_next_set():
    rows = [ln for ln in tree(HWFW_REL).split("\n") if ln.startswith("| 2 (W8, L5-F14) |")]
    assert len(rows) == 1
    c = cells(rows[0])
    assert len(c) == 3 and c[1] == "6 October 2026" and "adopted in the NEXT set" in c[2]
    for p in STALE:
        assert re.search(p, c[2]), "the change record does not keep %s" % p


def t_no_em_or_en_dash():
    for t in (tree(YAML_REL), tree(HWFW_REL), open(os.path.abspath(__file__), encoding="utf-8").read()):
        assert chr(0x2014) not in t and chr(0x2013) not in t
