#!/usr/bin/env python3
"""A known component mismatch survives a re-run and a regeneration (MESHSAT-1357, round 8, 26 September 2026).

Review of the 22:35 progress report, finding D1: "Known part mismatches are corrected manually in output. Fourteen rows
were marked WRONG_MODEL, but `jlc_certify.py` would certify them again. Put the exact known mismatches and supported
compatibility decisions into authoritative machine-readable inputs consumed by the checker. Re-running certification
must preserve their unresolved status." And: "Add focused regression checks for these actual failure modes: an
unresolved mismatch survives regeneration".

The fourteen rows are JLC-CERTIFIED.tsv's at 2aaa7b7f whose note opens "MISMATCH under owner condition 1, not a pass"
(codes C594232, C265283, C5251182, C580654, C2287 and board B's U80 on C350562), with board P's J_TS2 as a fifteenth
that carries the same reason beside a parser refusal. The declared input is tools/jlc-mismatch.yaml; jlc_certify and
lcsc_fill both read it. Every fixture below runs offline: the catalogue answers are the ones the parts stream's re-take
received on 26 September 2026 (SOURCES.yaml jlc_retake_45bde541, the tool's cache of that run), and a fixture that
would ask JLCPCB anything else fails instead of asking.

Also here, because they are the same stream's fixes and share the fixtures: the parser defect of the parts stream's
draft 01 (eleven rows refused for a document number, a finding id, a ppm figure, a package name or a far-end part), the
frequency guard that could not read the catalogue's description, and lcsc_fill's MAP (a repeated key, entries hidden in
comments, and the two fill codes the declaration refuses).
"""
import ast, contextlib, copy, csv, datetime, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, tokenize

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import jlc_certify as jc

TODAY = datetime.date.today().isoformat()
ALIASES = jc.declared(jc.ALIASES)
TABLE = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "release", "revA", "order", "JLC-CERTIFIED.tsv")


def _answer(code, model, spec, stock=10000, brand="x", describe=None):
    a = {"componentCode": code, "componentModelEn": model, "componentBrandEn": brand, "componentSpecificationEn": spec,
         "componentLibraryType": "expand", "stockCount": stock, "initialPrice": 1.0}
    if describe is not None:
        a["describe"] = describe
    return a


# The catalogue's answers for the declared codes, as the re-take of 26 September 2026 received them.
ANSWERS = {
    "C594232": _answer("C594232", "B4B-XH-A-G", "Plugin,P=2.5mm", 17517, "JST"),
    "C265283": _answer("C265283", "B2B-XH-A-GU", "Plugin,P=2.5mm", 5984, "JST"),
    "C5251182": _answer("C5251182", "B2B-PH-K-S-GW", "Plugin,P=2mm", 37049, "JST"),
    "C580654": _answer("C580654", "LTC2954ITS8-1#TRMPBF", "TSOT-23-8", 197, "Analog Devices"),
    "C2287": _answer("C2287", "KT-0603Y", "0603", 83461, "Hubei KENTO Elec"),
    "C350562": _answer("C350562", "SN74LVC86APWR", "TSSOP-14", 4080, "Texas Instruments"),
    "C144395": _answer("C144395", "B4B-XH-A(LF)(SN)", "Plugin,P=2.5mm", 108974, "JST"),
    "C131337": _answer("C131337", "B2B-PH-K-S(LF)(SN)", "Plugin,P=2mm", 86610, "JST"),
}


def _cache(*codes):
    return {c: {"asked": TODAY, "list": [ANSWERS[c]]} for c in codes}


def _certify(comment, fp, code, cache=None, qty=1, mismatches=None):
    return jc.certify({"comment": comment, "fp": fp, "code": code, "qty": qty}, cache if cache is not None else _cache(code),
                      {}, ALIASES, mismatches=mismatches)


# ---------------------------------------------------------------- the declared input against the table's marks
def _marked_rows():
    rows = list(csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t"))
    return [r for r in rows if r["note"].startswith(jc.CONDITION_1) or ("also a " + jc.CONDITION_1) in r["note"]]


def t_every_row_the_table_marks_is_declared_and_still_refused():
    """Every row the table records as a condition 1 mismatch is matched by an uncleared declaration (a mark the tool
    does not read is the defect of 2aaa7b7f), and reads WRONG_MODEL. Stated as a property and not as a count: a row
    whose code moves to the recommended part leaves this list, which is the fix, not a regression."""
    decl = jc.mismatch_declarations()
    marked = _marked_rows()
    bad = []
    for r in marked:
        hits = [e for e in jc.declared_hits({"comment": r["comment"], "fp": r["fp"], "code": r["bom_code"]}, {}, decl)
                if e["id"] not in decl["cleared"]]
        if not hits: bad.append("undeclared: %s %s" % (r["bom_code"], r["comment"][:50]))
        if r["verdict"] != "WRONG_MODEL": bad.append("not refused: %s %s reads %s" % (r["bom_code"], r["comment"][:50], r["verdict"]))
    assert not bad, "; ".join(bad)


def t_no_table_row_certifies_a_declared_code_on_a_row_it_declares():
    decl = jc.mismatch_declarations()
    bad = []
    for r in csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t"):
        if r["verdict"] not in ("CERTIFIED", "HAND_FIT", "BENCH_FITTED"): continue
        hits = [e for e in jc.declared_hits({"comment": r["comment"], "fp": r["fp"], "code": r["bom_code"]},
                                            {"code": r["code"]}, decl) if e["id"] not in decl["cleared"]]
        if hits: bad.append("%s %s %s (%s)" % (r["verdict"], r["code"] or r["bom_code"], r["comment"][:50], hits[0]["id"]))
    assert not bad, "the table passes a row the declaration refuses: %s" % "; ".join(bad)


# ---------------------------------------------------------------- one row at a time
def t_a_declared_code_the_catalogue_answers_as_the_part_reads_wrong_model():
    """DEFECTIVE: each of these read CERTIFIED under the tool of fc144600 (every character of the part the row names is
    in the model), and was marked by hand. ACCEPTABLE: the recommended code on the same row is certified."""
    rows = [("SMBus lead to board P, JST-XH 1x4 (B4B-XH-A), P's pin order: 1 SMBC, 2 SMBD, 3 GND, 4 PRES",
             "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C594232", "MM-01"),
            ("JST-XH 1x2 socket: the MAIN button lead from the panel, PB and GND", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
             "C265283", "MM-02"),
            ("JST-PH 1x2 socket: PA gate bias, VGG GND (the lead runs to the RA30H1317M1 VGG pin)",
             "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "C5251182", "MM-03"),
            ("LTC2954ITS8-1 push-button on/off controller, -40 to 85 C", "TSOT-23-8", "C580654", "MM-04"),
            ("amber record", "LED_0603_1608Metric", "C2287", "MM-05"),
            ("74LVC86APW quad exclusive-or: break-before-make on each bank's select", "TSSOP-14_4.4x5mm_P0.65mm", "C350562", "MM-06")]
    for c, fp, code, mid in rows:
        ev = _certify(c, fp, code)
        assert ev["verdict"] == "WRONG_MODEL", (code, ev)
        assert ev["note"].startswith(jc.CONDITION_1) and mid in ev["note"] and "the tool read CERTIFIED" in ev["note"], ev["note"]
        assert ev.get("declared_mismatch") == mid, ev
    ev = _certify(rows[0][0], rows[0][1], "C144395")
    assert ev["verdict"] == "CERTIFIED", ev
    ev = _certify(rows[2][0], rows[2][1], "C131337")
    assert ev["verdict"] == "CERTIFIED", ev


def t_a_scoped_declaration_leaves_the_same_code_alone_where_the_text_names_the_ordered_part():
    ev = _certify("yellow status", "LED_0603_1608Metric", "C2287")
    assert ev["verdict"] == "CERTIFIED", ev
    ev = _certify("SN74LVC86APWR quad exclusive-or: break-before-make", "TSSOP-14_4.4x5mm_P0.65mm", "C350562")
    assert ev["verdict"] == "CERTIFIED", ev
    ev = _certify("74LVC86APW,118 quad exclusive-or", "TSSOP-14_4.4x5mm_P0.65mm", "C350562")
    assert ev["verdict"] == "WRONG_MODEL", "Nexperia's own orderable text still names the part not ordered: %s" % ev


def t_a_search_that_picks_a_declared_code_is_held_too():
    """A row with no code whose search answers a declared code: the declaration binds the ANSWER, not only the BOM."""
    c, fp = "cell thermistor (JST-PH 1x2): the 103AT in the block", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical"
    saved = jc.PROJECT_ALLOW; jc.PROJECT_ALLOW = {}
    try:
        ev = jc.certify({"comment": c, "fp": fp, "code": "", "qty": 1},
                        {"B2B-PH-K": {"asked": TODAY, "list": [ANSWERS["C5251182"]]}}, {}, ALIASES)
    finally:
        jc.PROJECT_ALLOW = saved
    assert ev["verdict"] == "WRONG_MODEL" and ev.get("declared_mismatch") == "MM-03", ev


def t_a_row_refused_for_another_reason_keeps_its_verdict_and_gains_the_declaration():
    ev = _certify("LTC2954ITS8-1 push-button on/off controller", "TSOT-23-8", "C580654", qty=100)   # 197 in stock < 500
    assert ev["verdict"] == "WRONG_MODEL" and "NO_STOCK" in ev["note"], ev
    assert "the tool read NO_STOCK" in ev["note"], ev["note"]


# ---------------------------------------------------------------- a re-run and a regeneration, end to end
BOM_HDR = ["Comment", "Designator", "Footprint", "LCSC Part #"]
FIRST = [("SMBus lead to E6 J_SMB (JST-XH 1x4): SMBC SMBD GND(pack side of the shunt) PRES", "J_SMB",
          "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C594232"),
         ("second-level cell thermistor socket, JST-PH 1x2 (Semitec 103AT-2 on the hottest cell): 1 TS_SEC_J, 2 VSS",
          "J_TS2", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "C5251182"),
         ("amber record", "LED2", "LED_0603_1608Metric", "C2287"),
         ("yellow status", "LED9", "LED_0603_1608Metric", "C2287"),
         ("JST-XH 1x4 service lead", "J_SVC", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C144395")]
# A regeneration: references renumbered, a quantity changed, two comments reworded as a generator rewrite would.
REGEN = [("SMBus lead to board E J_SMB (JST-XH 1x4), regenerated: SMBC SMBD GND PRES", "J_SMB1,J_SMB2",
          "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C594232"),
         ("second-level cell thermistor socket, JST-PH 1x2: TS_SEC_J VSS", "J_TS3",
          "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "C5251182"),
         ("amber record (regenerated)", "LED12", "LED_0603_1608Metric", "C2287"),
         ("yellow status", "LED19", "LED_0603_1608Metric", "C2287"),
         ("JST-XH 1x4 service lead", "J_SVC", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C144395")]
HELD = {"J_SMB": "MM-01", "J_TS2": "MM-03", "J_TS3": "MM-03", "LED2": "MM-05", "LED12": "MM-05", "J_SMB1,J_SMB2": "MM-01"}


def _world(d, lines):
    """A tree with one declared folder (board P's declared phase, P4) whose BOM carries `lines`."""
    boards = os.path.join(d, "boards")
    phase = jc.declared_phase("p")
    f = os.path.join(boards, "meshsat-pcb-p-revA-%s" % phase)
    shutil.rmtree(boards, ignore_errors=True); os.makedirs(f)
    with open(os.path.join(f, "pcb-p-pack-bom.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(BOM_HDR); w.writerows(lines)
    return boards


@contextlib.contextmanager
def _patched(**kw):
    saved = {k: getattr(jc, k) for k in kw}
    try:
        for k, v in kw.items(): setattr(jc, k, v)
        yield
    finally:
        for k, v in saved.items(): setattr(jc, k, v)


def _offline_query(keyword, cache, refresh=False):
    if keyword not in ANSWERS:
        raise AssertionError("the fixture would have asked JLCPCB for %r" % keyword)
    return [copy.deepcopy(ANSWERS[keyword])], TODAY


def _run_main(d, boards, table, mismatch=None):
    out = os.path.join(d, "verdicts")
    kw = dict(BOARDS_DIR=boards, CACHE=os.path.join(d, "cache.json"), query=_offline_query, PROJECT_ALLOW={})
    if mismatch: kw["MISMATCH"] = mismatch
    buf = io.StringIO()
    with _patched(**kw), contextlib.redirect_stdout(buf):
        rc = jc.main(["--table", table, "--out-dir", out])
    return rc, buf.getvalue(), out


def _table(path):
    return {r["comment"]: r for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t")}


def t_an_unresolved_mismatch_survives_a_re_run_and_a_regeneration():
    """DEFECTIVE, as it stood at 2aaa7b7f: the table said WRONG_MODEL by hand and the tool would say CERTIFIED. Here the
    table beside the run says CERTIFIED for every row (what the old tool wrote), the tool is run, the board is
    regenerated (references, quantities and wording move), and the tool is run again: the declared rows are refused
    both times and the yellow LED on the same code, and the recommended code, stay certified."""
    d = tempfile.mkdtemp(prefix="certify-mismatch-")
    try:
        table = os.path.join(d, "JLC-CERTIFIED.tsv")
        with open(table, "w", encoding="utf-8") as fh:
            fh.write("verdict\tcomment\tfp\tboards\tqty\tneed\tbom_code\tcode\tmodel\tbrand\tpkg\tlib\tstock\tprice\tasked\tnote\n")
            for c, _r, fp, code in FIRST:
                fh.write("CERTIFIED\t%s\t%s\tP\t1\t5\t%s\t%s\tx\tx\tx\texpand\t1\t1\t%s\t\n" % (c, fp, code, code, TODAY))
        for lines in (FIRST, REGEN):
            boards = _world(d, lines)
            rc, log, out = _run_main(d, boards, table)
            got = _table(table)
            for c, refs, fp, code in lines:
                r = got[c]
                if refs in HELD:
                    assert r["verdict"] == "WRONG_MODEL" and HELD[refs] in r["note"] and r["note"].count(jc.CONDITION_1) >= 1, (refs, r["verdict"], r["note"][:120])
                else:
                    assert r["verdict"] == "CERTIFIED", (refs, r["verdict"], r["note"][:120])
            v = json.load(open(os.path.join(out, "jlc_certify.verdict.json")))
            assert v["verdict"] == "FAIL", v["verdict"]
            assert (v["inputs"].get("declared_mismatches") or {}).get("sha256_16"), "the verdict does not name the declaration's bytes"
            assert "held WRONG_MODEL by them" in log, log[-400:]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_declaration_that_cannot_be_read_stops_the_run_before_the_table_is_written():
    d = tempfile.mkdtemp(prefix="certify-mismatch-")
    try:
        table = os.path.join(d, "JLC-CERTIFIED.tsv")
        open(table, "w").write("the table as it stood\n")
        bad = os.path.join(d, "jlc-mismatch.yaml")
        open(bad, "w").write("schema_version: 1\nmismatches:\n  - id: MM-X\n    code: C594232\n    record: r\n")   # no reason
        boards = _world(d, FIRST)
        rc, log, out = _run_main(d, boards, table, mismatch=bad)
        v = json.load(open(os.path.join(out, "jlc_certify.verdict.json")))
        assert v["verdict"] == "INCONCLUSIVE" and "reason" in (v.get("missing_input") or ""), v
        assert open(table).read() == "the table as it stood\n", "the table was rewritten by a run that could not read its declarations"
        open(bad, "w").write("schema_version: 1\nmismatches: []\n")
        os.remove(bad)
        rc, log, out = _run_main(d, boards, table, mismatch=bad)
        assert json.load(open(os.path.join(out, "jlc_certify.verdict.json")))["verdict"] == "INCONCLUSIVE", "a missing declaration file passed"
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------- lcsc_fill reads the declaration, not only the table
def _fill_world(d, lines, with_declaration=True):
    t = os.path.join(d, "v2", "ecad", "tools"); os.makedirs(t)
    for f in ("lcsc_fill.py", "verdict.py", "jlc_certify.py", "lcsc-blocked.txt") + (("jlc-mismatch.yaml",) if with_declaration else ()):
        shutil.copy(os.path.join(TOOLS, f), t)
    o = os.path.join(d, "v2", "release", "revA", "order"); os.makedirs(o)
    with open(os.path.join(o, "JLC-CERTIFIED.tsv"), "w", encoding="utf-8") as fh:
        fh.write("verdict\tcomment\tfp\tboards\tqty\tneed\tbom_code\tcode\tmodel\tbrand\tpkg\tlib\tstock\tprice\tasked\tnote\n")
        for c, _r, fp, code in lines:     # the table an old run wrote: every row CERTIFIED
            fh.write("CERTIFIED\t%s\t%s\tP\t1\t5\t%s\t%s\tx\tx\tx\texpand\t1\t1\t%s\t\n" % (c, fp, code, code, TODAY))
    bom = os.path.join(d, "proj", "out", "jlc", "x-bom.csv"); os.makedirs(os.path.dirname(bom))
    with open(bom, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(BOM_HDR); w.writerows(lines)
    vd = os.path.join(d, "verdicts")
    r = subprocess.run([sys.executable, os.path.join(t, "lcsc_fill.py"), bom], capture_output=True, text=True, cwd=d,
                       env=dict(os.environ, VERDICT_DIR=vd))
    return r, json.load(open(os.path.join(vd, "lcsc_fill.verdict.json")))


def t_lcsc_fill_refuses_a_declared_code_that_the_table_beside_it_certifies():
    """DEFECTIVE: lcsc_fill read only the table, so a table rewritten by a run that did not read the declarations made
    it accept (and fill) the declared codes again. Here the table certifies every row and lcsc_fill still refuses the
    three declared rows of the regenerated BOM, naming each declaration."""
    d = tempfile.mkdtemp(prefix="fill-mismatch-")
    try:
        r, v = _fill_world(d, REGEN)
        assert v["verdict"] == "FAIL" and v["counts"]["rejected_code"] == 3, (v, r.stdout[-600:])
        for mid in ("MM-01", "MM-03", "MM-05"):
            assert any(mid in e for e in v["evidence"]), (mid, v["evidence"])
        assert not any("LED19" in e or "J_SVC" in e for e in v["evidence"]), v["evidence"]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_lcsc_fill_stops_on_a_declaration_it_cannot_read():
    d = tempfile.mkdtemp(prefix="fill-mismatch-")
    try:
        t = os.path.join(d, "v2", "ecad", "tools"); os.makedirs(t)
        for f in ("lcsc_fill.py", "verdict.py", "jlc_certify.py", "lcsc-blocked.txt"):
            shutil.copy(os.path.join(TOOLS, f), t)
        open(os.path.join(t, "jlc-mismatch.yaml"), "w").write("schema_version: 1\nmismatches:\n  - {id: MM-X, code: C1}\n")
        bom = os.path.join(d, "proj", "out", "jlc", "x-bom.csv"); os.makedirs(os.path.dirname(bom))
        with open(bom, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(BOM_HDR); w.writerows(REGEN)
        vd = os.path.join(d, "verdicts")
        subprocess.run([sys.executable, os.path.join(t, "lcsc_fill.py"), bom], capture_output=True, text=True, cwd=d,
                       env=dict(os.environ, VERDICT_DIR=vd))
        v = json.load(open(os.path.join(vd, "lcsc_fill.verdict.json")))
        assert v["verdict"] == "INCONCLUSIVE", v
    finally:
        shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------- a compatibility decision needs its evidence
def _decl_with(d, compat):
    import yaml
    doc = {"schema_version": 1,
           "mismatches": [{"id": "MM-T", "code": "C594232", "reason": "a gold variant the held catalogue does not list",
                           "record": "fixture", "named": "B4B-XH-A", "ordered": "B4B-XH-A-G"}],
           "compatibility": compat}
    p = os.path.join(d, "jlc-mismatch.yaml")
    yaml.safe_dump(doc, open(p, "w"))
    return jc.mismatch_declarations(p, root=d)


def t_a_compatibility_entry_without_evidence_is_refused():
    d = tempfile.mkdtemp(prefix="compat-")
    try:
        doc = os.path.join(d, "v2", "vendor", "jst", "order-guide.pdf"); os.makedirs(os.path.dirname(doc))
        open(doc, "wb").write(b"JST lists B4B-XH-A-G as the gold-plated B4B-XH-A, mating the XH housing")
        sha = hashlib.sha256(open(doc, "rb").read()).hexdigest()
        good_ev = {"path": "v2/vendor/jst/order-guide.pdf", "sha256": sha, "finding": "lists B4B-XH-A-G as the gold B4B-XH-A"}
        base = {"clears": "MM-T", "ruled_by": "SESSION", "ruled_on": "2026-09-26", "why": "the maker lists the variant"}
        refused = {
            "no evidence": dict(base),
            "an empty evidence list": dict(base, evidence=[]),
            "a file not in the tree": dict(base, evidence=[dict(good_ev, path="v2/vendor/jst/missing.pdf")]),
            "a sha the file does not have": dict(base, evidence=[dict(good_ev, sha256="0" * 64)]),
            "a path outside the repository": dict(base, evidence=[dict(good_ev, path="../outside.pdf")]),
            "no finding": dict(base, evidence=[dict(good_ev, finding="")]),
            "no ruled_by": dict({k: v for k, v in base.items() if k != "ruled_by"}, evidence=[good_ev]),
            "an unknown mismatch": dict(base, clears="MM-NONE", evidence=[good_ev]),
        }
        row = ("SMBus lead to board P, JST-XH 1x4 (B4B-XH-A)", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "C594232")
        for what, c in refused.items():
            decl = _decl_with(d, [c])
            assert not decl["cleared"] and len(decl["refused"]) == 1, (what, decl["refused"], decl["cleared"])
            ev = _certify(*row, mismatches=decl)
            assert ev["verdict"] == "WRONG_MODEL", (what, ev)
            if c.get("clears") == "MM-T":
                assert "was refused" in ev["note"], (what, ev["note"])
        decl = _decl_with(d, [dict(base, evidence=[good_ev])])
        assert decl["cleared"] and not decl["refused"], decl["refused"]
        ev = _certify(*row, mismatches=decl)
        assert ev["verdict"] == "CERTIFIED" and "cleared by a compatibility decision" in ev["note"] and sha[:12] in ev["note"], ev
        open(doc, "ab").write(b" edited later")                     # the evidence moves: the decision stops lifting
        decl = _decl_with(d, [dict(base, evidence=[good_ev])])
        assert not decl["cleared"] and "sha256" in decl["refused"][0][1], decl
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_the_tree_s_declaration_clears_nothing_without_evidence():
    decl = jc.mismatch_declarations()
    assert not decl["refused"], "the tree's declaration carries a refused compatibility decision: %s" % decl["refused"]
    for mid, c in decl["cleared"].items():
        assert c.get("evidence"), mid


# ---------------------------------------------------------------- the parser rows of draft 01, before and after
# Each: board, comment, land, code, the model the re-take received, its package, stock. Under the tool of fc144600
# every one read WRONG_MODEL, "asked for" the token in the fourth column of the comment below.
PARSER_ROWS = [
    ("D", "10.7k 0.1% 25ppm", "R_0603_1608Metric", "C861078", "RT0603BRD0710K7L", "0603", 1011, "25ppm"),
    ("B", "100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)", "C_0402_1005Metric", "C60474", "CC0402KRX7R7BB104", "0402", 15519580, "DS40068"),
    ("B", "220n 16V (PCIe AC coupling at the switch transmitter, W3-F01)", "C_0402_1005Metric", "C696846", "TCC0402X7R224K160AT", "0402", 192168, "W3-F01"),
    ("B", "33.2R 1% (HCSL series Rs, DS40068 Table 8-1, W3-F03)", "R_0603_1608Metric", "C23004", "0603WAF332JT5E", "0603", 49957, "DS40068"),
    ("B", "49.9R 1% (HCSL shunt Rp, DS40068 Table 8-1, W3-F03)", "R_0603_1608Metric", "C23185", "0603WAF499JT5E", "0603", 2362519, "DS40068"),
    ("D", "56.2k 0.1% 25ppm", "R_0603_1608Metric", "C705784", "RT0603BRD0756K2L", "0603", 10885, "25ppm"),
    ("D", "6 MHz HC-49S-SMD passive (CL 20 pF, 80 Ohm; C1 = C2 = 27 pF and Rd 1.0k, SLLS413 figure 6 re-chosen for this part's ESR)",
     "Crystal_SMD_HC49-SD", "C252308", "6CS06000F20UCG", "HC-49S-SMD", 325, "HC-49S-SMD"),
    ("D", "6 MHz HC-49S-SMD passive (codec clock, CL 20 pF; C1 = C2 = 27 pF)", "Crystal_SMD_HC49-SD", "C252308",
     "6CS06000F20UCG", "HC-49S-SMD", 325, "HC-49S-SMD"),
    ("P", "JST-PH 1x5 socket for the four cell thermistors (Semitec 103AT-2, one per series group of the 4S3P block): TS1 TS2 TS3 TS4 VSS",
     "JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical", "C157993", "B5B-PH-K-S(LF)(SN)", "Plugin,P=2mm", 161943, "103AT-2"),
    ("E", "JST-XH 1x2 (B2B-XH-A): lid and tamper reed sensor lead, Littelfuse 59140-1-S-05-A normally open under the frame, 57140-000 magnet in the lid: 1 lead, 2 GND",
     "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "C158012", "B2B-XH-A(LF)(SN)", "Plugin,P=2.5mm", 363735, "59140-1-S-05-A"),
    ("P", "second-level cell thermistor socket, JST-PH 1x2 (Semitec 103AT-2 on the hottest cell): 1 TS_SEC_J, 2 VSS",
     "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "C5251182", "B2B-PH-K-S-GW", "Plugin,P=2mm", 37049, "103AT-2"),
]
# The catalogue line JLCPCB returns for C252308 (read live on 26 September 2026, round 8): its describe field names 6 MHz.
C252308_DESCRIBE = "-40℃~+85℃ 20pF 6MHz Crystal Oscillator ±20ppm ±30ppm HC-49S-SMD Crystals ROHS"


def _parser_row(t, describe=None):
    _b, c, fp, code, model, spec, stock, _tok = t
    a = _answer(code, model, spec, stock, describe=describe if describe is not None else (C252308_DESCRIBE if code == "C252308" else None))
    return jc.certify({"comment": c, "fp": fp, "code": code, "qty": 1}, {code: {"asked": TODAY, "list": [a]}}, {}, ALIASES)


def t_the_eleven_rows_are_identified_by_their_own_parts():
    """DEFECTIVE under fc144600: all eleven WRONG_MODEL, each "asked for" a token that is not its part. Now ten are
    CERTIFIED, and board P's J_TS2 stays WRONG_MODEL, for the declared condition 1 mismatch of its -GW code (MM-03),
    not for the thermistor at the other end of its lead."""
    got = [(t, _parser_row(t)) for t in PARSER_ROWS]
    bad = []
    for t, ev in got:
        if "asked for %s" % t[7] in (ev.get("note") or ""):
            bad.append("%s still asked for %s" % (t[1][:40], t[7]))
        want = "WRONG_MODEL" if t[3] == "C5251182" else "CERTIFIED"
        if ev["verdict"] != want:
            bad.append("%s reads %s (%s)" % (t[1][:40], ev["verdict"], (ev.get("note") or "")[:90]))
    assert not bad, "; ".join(bad)
    j = dict((t[3], ev) for t, ev in got)
    assert j["C5251182"].get("declared_mismatch") == "MM-03", j["C5251182"]
    assert "59140-1-S-05-A" in j["C158012"]["note"] and "103AT-2" in j["C157993"]["note"], "the far-end part is dropped from the note"


def t_the_crystal_is_compared_by_the_frequency_the_catalogue_describes():
    """ACCEPTABLE above: the 6 MHz row on SJK's 6MHz part. DEFECTIVE: the same row answered by a part whose catalogue
    line describes 25 MHz, which the guard could not see before the description was kept."""
    t = PARSER_ROWS[6]
    ev = _parser_row(t, describe="-20℃~+70℃ 20pF 25MHz Crystal ±20ppm HC-49S-SMD Crystals ROHS")
    assert ev["verdict"] == "WRONG_MODEL" and "25 MHz" in ev["note"], ev


def t_query_keeps_the_description_the_frequency_guard_reads():
    class R: pass
    def fake_run(*a, **k):
        r = R(); r.stdout = json.dumps({"data": {"componentPageInfo": {"list": [dict(_answer("C1", "M", "HC-49S-SMD"),
                                         describe="6MHz crystal", erpComponentName="6MHz ±20ppm 20pF")]}}}); return r
    saved = jc.subprocess.run; jc.subprocess.run = fake_run
    try:
        lst, _asked = jc.query("C1", {}, refresh=True)
    finally:
        jc.subprocess.run = saved
    assert lst[0].get("describe") == "6MHz crystal" and lst[0].get("erpComponentName"), lst[0]


def t_the_hc49_land_and_the_catalogue_s_package_are_one_family_with_the_mounting():
    assert jc.norm_pkg("Crystal_SMD_HC49-SD") == jc.norm_pkg("HC-49S-SMD") == "HC-49-SMD"
    assert jc.norm_pkg("Crystal:Crystal_HC49-U_Vertical") == jc.norm_pkg("HC-49U") != jc.norm_pkg("HC-49S-SMD")


PARTS_STILL_PARTS = [
    ("DS3231MZ+ holdover clock (I2C 0x68), CR2032 backed", "DS3231MZ"),   # a Maxim part in the DS range, not a document
    ("SMBJ18A (VBUS clamp at the outlet)", "SMBJ18A"),
    ("SMAJ15A clamp", "SMAJ15A"),
    ("SMCJ40A (vehicle input)", "SMCJ40A"),
    ("DO1608C-472 inductor", "DO1608C-472"),
    ("74LVC86APW quad exclusive-or", "74LVC86APW"),
    ("HDMI type A receptacle (Molex 208658-1001): cable to the Xenarc 709GNK pass-through", "208658-1001"),
    ("SOS locking toggle, maintained (APEM 5636ADKB-2V, both positions latched)", "5636ADKB-2V"),
    ("3 mOhm 1% 3 W 2512 shunt (RALEC LR2512-23R003F4): gauge SRP/SRN Kelvin (32.24 AV)", "LR2512-23R003F4"),
    ("USB switch (Texas Instruments TPS2065CDBV), port 3", "TPS2065CDBV"),
    ("Ebyte E22-900M30S 1 W LoRa (SX1262)", "E22-900M30S"),
    ("M.2 B-key 3052 socket, TE 1-2199119-5, M2.5 standoff", "1-2199119-5"),
    ("Touch Display 2 FPC 22-pin 0.5 mm (Hirose FH12-22S-0.5SH), Standard-Mini 22-to-15 cable", "FH12-22S-0.5SH"),
]
NOT_PARTS = ["25ppm", "HC-49S-SMD", "SOT-23-5", "DO-214AB", "TO-92-3", "QFN-32", "TSSOP-14", "W3-F01", "R4A-N15",
             "F-IN-02", "SLUSC67B", "SCPS131J", "SLVSAU6I", "SLLS413"]


def t_what_is_a_part_is_still_read_as_one_and_the_new_shapes_are_not():
    bad = ["%r read %r, not %r" % (c, jc.intended_part(c), w) for c, w in PARTS_STILL_PARTS if jc.intended_part(c) != w]
    bad += ["%s is read as a part" % t for t in NOT_PARTS if not jc.NOT_PART.match(t)]
    assert not bad, "; ".join(bad)


def t_a_pin_count_gives_way_to_a_part_the_row_names():
    """DEFECTIVE until round 8's second pass: board B's Touch Display FPC row read "22-pin" as its part, ahead of the
    Hirose part its land is drawn for, and needed the first pass's land rule to be read at all. ACCEPTABLE, and kept as
    it was: a row whose only candidate is a pin count (board B's RockBLOCK bracket header) still returns it, because
    `rows_to_check` drops an IDC, lead or header row that names nothing, and that would take a declared bench header
    out of the table (a limit of LEAD, recorded)."""
    c, fp = "Touch Display 2 FPC 22-pin 0.5 mm (Hirose FH12-22S-0.5SH), Standard-Mini 22-to-15 cable", \
        "Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal"
    assert jc.intended_part(c) == "FH12-22S-0.5SH" and jc.value_land_conflict(c, fp) is None, jc.intended_part(c)
    assert jc.PIN_COUNT.match("22-pin") and jc.PIN_COUNT.match("16-pin") and not jc.PIN_COUNT.match("FH12-22S")
    assert jc.intended_part("RockBLOCK 9704 16-pin (IDC 2x8)") == "16-pin"


def t_a_land_s_own_part_with_more_ordering_still_decides_against_the_land():
    """Board A's SMA jacks name 132134-11 and JLCPCB answers 132134: the row's part is the land's with more ordering, so
    the row's part decides and the answer is refused, as before."""
    c, fp = "SMA jack, Amphenol 132134-11 vertical (pigtail to the GNSS device)", "SMA_Amphenol_132134-11_Vertical"
    ev = jc.certify({"comment": c, "fp": fp, "code": "C3174425", "qty": 1},
                    {"C3174425": {"asked": TODAY, "list": [_answer("C3174425", "132134", "Plugin", 1792, "Amphenol ICC")]}},
                    {}, ALIASES)
    assert ev["verdict"] == "WRONG_MODEL" and "132134-11" in ev["note"], ev


# ---------------------------------------------------------------- the far-end rule, narrowed (round 8, second pass)
# The independent check of the first pass (27 September 2026): the land rule let a land drawn for one maker's part
# identify ANY row whose words named an unrelated part, so a genuine conflict between the value and the land read
# CERTIFIED with a note. Reproduced offline against the fc144600 tool: all three below WRONG_MODEL there and CERTIFIED
# after the first pass. Each is a substitution under the owner's condition 1 (the schematic names X, the order is Y).
# Each: what it is, comment, land, code, the model the code answers, package, the part the words name, the land's part.
CONFLICTS = [
    ("the E22-900M30S module on the E22-900M33S land with the M33S code (the sibling class of finding W6-F3)",
     "Ebyte E22-900M30S 1 W LoRa (SX1262)", "RF_Module:Ebyte_E22-900M33S", "C9999", "E22-900M33S", "SMD",
     "E22-900M30S", "E22-900M33S"),
    ("an XH socket named on the PH land with the PH code",
     "JST B4B-XH-A socket", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "C157992", "B4B-PH-K-S(LF)(SN)", "Plugin,P=2mm",
     "B4B-XH-A", "B4B-PH-K"),
    ("a Molex part named on a JST PH 12-pin land with the JST code",
     "Molex 502382-1270 12-pin panel lead", "JST_PH_B12B-PH-K_1x12_P2.00mm_Vertical", "C8888", "B12B-PH-K-S(LF)(SN)",
     "Plugin,P=2mm", "502382-1270", "B12B-PH-K"),
    ("the value's own module ordered, on a land drawn for its sibling: the order matches the words, the copper does not",
     "Ebyte E22-900M30S 1 W LoRa (SX1262)", "RF_Module:Ebyte_E22-900M33S", "C7777", "E22-900M30S", "SMD",
     "E22-900M30S", "E22-900M33S"),
    ("far-end WORDING alone, with nothing in the words naming the land's part: not enough",
     "Ebyte E22-900M30S on the LoRa carrier", "RF_Module:Ebyte_E22-900M33S", "C9999", "E22-900M33S", "SMD",
     "E22-900M30S", "E22-900M33S"),
    ("the land's series named, but the other part carries the land's own maker and no far-end word",
     "JST-PH 1x4 socket (JST B4B-XH-A)", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical", "C157992", "B4B-PH-K-S(LF)(SN)",
     "Plugin,P=2mm", "B4B-XH-A", "B4B-PH-K"),
    ("the land's series named, and a bare part number beside it that nothing places away from the land",
     "JST-PH 1x2 socket, 103AT-2", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "C131337", "B2B-PH-K-S(LF)(SN)",
     "Plugin,P=2mm", "103AT-2", "B2B-PH-K"),
    # The second independent check (27 September 2026): a placement word whose OBJECT is the land itself was read as
    # 'away from the land', so both of these read CERTIFIED under the second pass where fc144600 refused them. The
    # words put the M30S ON the copper drawn for the M33S: the W6-F3 sibling substitution.
    ("a placement whose object names the land's part and the word land: the part sits ON the land",
     "Ebyte E22-900M30S on the E22-900M33S land", "RF_Module:Ebyte_E22-900M33S", "C9999", "E22-900M33S", "SMD",
     "E22-900M30S", "E22-900M33S"),
    ("a placement whose object is the land's footprint: the part sits IN the footprint",
     "Ebyte E22-900M30S in the E22-900M33S footprint", "RF_Module:Ebyte_E22-900M33S", "C9999", "E22-900M33S", "SMD",
     "E22-900M30S", "E22-900M33S"),
]


def _conflict_ev(t):
    _what, c, fp, code, model, spec, _named, _lp = t
    return jc.certify({"comment": c, "fp": fp, "code": code, "qty": 1},
                      {code: {"asked": TODAY, "list": [_answer(code, model, spec, 100000, "x")]}}, {}, ALIASES,
                      mismatches={"entries": [], "cleared": {}, "refused": [], "path": jc.MISMATCH})


def t_a_value_that_conflicts_with_its_land_is_refused_with_both_parts_named():
    """DEFECTIVE after the first pass of round 8: the first three read CERTIFIED, the land's part identifying the row
    with a note. Now every one is WRONG_MODEL, as at fc144600, and the note names the part the words name AND the part
    the land is drawn for, so the reader sees the conflict and not only the answer."""
    bad = []
    for t in CONFLICTS:
        ev = _conflict_ev(t)
        named, lp = t[6], t[7]
        if ev["verdict"] != "WRONG_MODEL":
            bad.append("%s reads %s (%s)" % (t[0], ev["verdict"], (ev.get("note") or "")[:120]))
        note = ev.get("note") or ""
        if named not in note or lp not in note:
            bad.append("%s: the note does not name both %s and %s: %s" % (t[0], named, lp, note[:160]))
        if "value and the land disagree" not in note:
            bad.append("%s: the note does not say the value and the land disagree: %s" % (t[0], note[:160]))
        if jc.row_part(t[1], t[2]) != (named, None):
            bad.append("%s: row_part reads %r" % (t[0], jc.row_part(t[1], t[2])))
    assert not bad, "; ".join(bad)


def t_a_catalogue_pass_over_an_unmarked_conflict_is_refused_whatever_path_wrote_it():
    """The guard in `certify`, for the path a later change adds: `_certify` cannot pass these rows today (the answer
    cannot be both parts), so the guard is proved by handing it a pass. DEFECTIVE: a CERTIFIED verdict with a model over
    the E22 conflict. ACCEPTABLE: the same verdict over a row whose words mark the other part as the far end, and a
    declared verdict with no model (a hand-fit route on a row with no code), which keeps its verdict and gains the
    sentence, as at fc144600."""
    saved = jc._certify
    try:
        jc._certify = lambda rec, *a, **k: dict(verdict="CERTIFIED", model="E22-900M30S", code="C1", note="")
        ev = jc.certify({"comment": CONFLICTS[3][1], "fp": CONFLICTS[3][2], "code": "C1", "qty": 1}, {}, {}, ALIASES,
                        mismatches={"entries": [], "cleared": {}, "refused": [], "path": jc.MISMATCH})
        assert ev["verdict"] == "WRONG_MODEL" and "the tool read CERTIFIED" in ev["note"], ev
        jc._certify = lambda rec, *a, **k: dict(verdict="CERTIFIED", model="B5B-PH-K-S(LF)(SN)", code="C157993", note="")
        c = PARSER_ROWS[8][1]
        ev = jc.certify({"comment": c, "fp": PARSER_ROWS[8][2], "code": "C157993", "qty": 1}, {}, {}, ALIASES,
                        mismatches={"entries": [], "cleared": {}, "refused": [], "path": jc.MISMATCH})
        assert ev["verdict"] == "CERTIFIED" and "103AT-2" in ev["note"] and "Semitec" in ev["note"], ev
        jc._certify = lambda rec, *a, **k: dict(verdict="HAND_FIT", note="bought from the maker")
        ev = jc.certify({"comment": CONFLICTS[0][1], "fp": CONFLICTS[0][2], "code": "", "qty": 1}, {}, {}, ALIASES,
                        mismatches={"entries": [], "cleared": {}, "refused": [], "path": jc.MISMATCH})
        assert ev["verdict"] == "HAND_FIT" and "value and the land disagree" in ev["note"], ev
    finally:
        jc._certify = saved


# The rows of JLC-CERTIFIED.tsv (round 8) whose words name a part unrelated to their land's part, each with the part
# the land rule must still identify it by and the evidence it must find. The independent check read all twenty and
# found each a genuine far-end part or a non-part; the twentieth, board B's Touch Display FPC, is no longer a conflict
# at all, since "22-pin" is a pin count and not a part (its Hirose part decides, below).
FAR_END_ROWS = [
    ("SMA jack (Amphenol 132134, vertical), pigtail from the 5G-DIV device", "SMA_Amphenol_132134-11_Vertical", "132134-11", "pigtail from the"),
    ("shore DC in 9-36 V, lead from the D38999/20FC4PN wall receptacle DC pair (JST-VH, 10 A): + -", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "B2P-VH", "lead from the"),
    ("DCF77 remote (XH2.5): 3V3 GND T P1", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical", "B4B-XH-A", "remote"),
    (PARSER_ROWS[8][1], PARSER_ROWS[8][2], "B5B-PH-K", "Semitec"),
    (PARSER_ROWS[9][1], PARSER_ROWS[9][2], "B2B-XH-A", "Littelfuse"),
    (PARSER_ROWS[10][1], PARSER_ROWS[10][2], "B2B-PH-K", "Semitec"),
    ("cell thermistor (JST-PH 1x2): the 103AT in the block", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical", "B2B-PH-K", "in the"),
    ("module thermistor lead (XH2.5): 103AT to the charger TS pin over the block", "JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", "B2B-XH-A", "to the"),
    ("BB-2590/U cable (BTA-70762-2) on XT60-M: pin 2 (the pad nearer the fuse F3) is +, pin 1 is the return", "AMASS_XT60-M_1x02_P7.20mm_Vertical", "XT60-M", "cable"),
    ("CR2032 holder Keystone 3034 (VBAT, also the NEO-M9N V_BCKP)", "BatteryHolder_Keystone_3034_1x20mm", "3034", "holder"),
]


def t_the_far_end_rows_are_still_identified_by_their_land_and_say_why():
    bad = []
    for c, fp, lp, mark in FAR_END_ROWS:
        got = jc.row_part(c, fp)
        vl = jc.value_land_conflict(c, fp)
        if got[0] != lp or not got[1]:
            bad.append("%s reads %r" % (c[:50], got))
        elif not vl or not vl[2] or mark not in vl[2]:
            bad.append("%s: the reason is %r, not one that finds %r" % (c[:50], vl and vl[2], mark))
    assert not bad, "; ".join(bad)


def t_no_row_of_the_table_passes_over_an_unmarked_conflict():
    """The table as a property: a row whose words name a part unrelated to its land's part either carries the words'
    evidence that the part is away from the land, or does not read a catalogue pass. Stated on the rows, not as a
    count: a row whose value is corrected leaves the set, which is the fix."""
    rows = list(csv.DictReader(open(TABLE, encoding="utf-8"), delimiter="\t"))
    bad = []
    for r in rows:
        vl = jc.value_land_conflict(r["comment"], r["fp"])
        if vl and not vl[2] and r["verdict"] == "CERTIFIED":
            bad.append("%s on %s reads CERTIFIED over %s against %s" % (r["comment"][:50], r["fp"], vl[0], vl[1]))
        if vl and vl[2] and r["verdict"] == "CERTIFIED" and vl[0] not in r["note"]:
            bad.append("%s: the far-end part %s is not in the note" % (r["comment"][:50], vl[0]))
    assert not bad, "; ".join(bad)


# ---------------------------------------------------------------- lcsc_fill's MAP
def _map_node():
    src = open(os.path.join(TOOLS, "lcsc_fill.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MAP" for t in n.targets):
            return src, n
    raise AssertionError("lcsc_fill.py has no MAP")


def t_the_fill_map_carries_no_key_twice():
    """DEFECTIVE until round 8: ('^4\\.7u$', 'C_0805') was a key twice (C354262 with its reason, then C1779), and a dict
    literal keeps the later one silently, so the reasoned line never applied."""
    _src, n = _map_node()
    keys = [ast.literal_eval(k) for k in n.value.keys]
    dup = sorted({repr(k) for k in keys if keys.count(k) > 1})
    assert not dup, "keys given twice in lcsc_fill's MAP (Python keeps the later): %s" % ", ".join(dup)


def t_no_fill_rule_is_hidden_in_a_comment():
    """DEFECTIVE until round 8: four rules (green, red and two ferrites) sat after a `#` on another rule's line, where a
    reader sees a rule and Python sees text. A rule kept in a comment ON PURPOSE says so with the word RETIRED (the
    BC847BS line of 12 September 2026 does)."""
    src, n = _map_node()
    lines = src.splitlines(True)
    span = "".join(lines[n.lineno - 1:n.end_lineno])
    rule = re.compile(r'\(r?"[^"]+"\s*,\s*"[^"]+"\)\s*:\s*"C\d+"')
    hidden = []
    for tok in tokenize.generate_tokens(io.StringIO(span).readline):
        if tok.type == tokenize.COMMENT and rule.search(tok.string) and "RETIRED" not in tok.string:
            hidden.append("line %d: %s" % (n.lineno + tok.start[0] - 1, tok.string[:80]))
    assert not hidden, "fill rules written inside comments: %s" % "; ".join(hidden)


def t_no_fill_rule_writes_a_declared_mismatch():
    """DEFECTIVE until round 8: the SMBus lead and cell thermistor rules filled C594232 and C5251182, which the
    declaration refuses, so lcsc_fill refused what its own MAP wrote."""
    _src, n = _map_node()
    m = ast.literal_eval(n.value)
    decl = jc.mismatch_declarations()
    unscoped = {e["code"]: e["id"] for e in decl["entries"] if e["_rx"] is None and e["id"] not in decl["cleared"]}
    bad = ["%r on %s -> %s (%s)" % (rx, fp, code, unscoped[code]) for (rx, fp), code in m.items() if code in unscoped]
    assert not bad, "; ".join(bad)
