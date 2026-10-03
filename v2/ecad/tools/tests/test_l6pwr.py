#!/usr/bin/env python3
"""The Layer 6 record of the power parts' identities (MESHSAT-1357, record l6pwr, 3 October 2026).

Properties, pinned on fixtures and on the committed record, never on today's counts:

  * the identity block `drafted_identities_l4_power` in pcb_part_identities.yaml is the one l6pwr_parts.py renders (the yaml and the
    record cannot disagree), and the tool's own check still reads the table as before (the block is outside `selections`);
  * every row of the block has the table's vocabulary: a status in STATUSES; a RESOLVED one a maker, a part number and a document with
    path, sha256 and page; an UNRESOLVED one a reason class in REASONS, a reason and a next action;
  * rule D-2 holds on every RESOLVED binding whose document is on this host: the cited page prints the part number (read, not trusted);
    a held-back document that is absent reads UNREAD, never READ;
  * a DECODE_NOTE binding names a page that does NOT print the part number (else it would be PRINTED), and the sheet is present or held;
  * the record's text carries no em or en dash and no private path or host (the public-tree rules);
  * the designator detector reads drafts by PARSING them (ast): on a fixture of two drafts that share a designator it finds the
    collision, on a fixture that shares none it finds nothing, and it never reads a designator out of prose;
  * the grade verdict is the envelope's: strictly inside is INSIDE, an end met exactly is AT_LIMIT, a range that misses an end is OUTSIDE;
  * the catalogue readings the record cites are in the tree with the fields the record prints (code, model, brand, package, stock,
    price ladder, read time), and no reading is newer than the record's output (the output is derived from them);
  * set 28 (F-13): every L4-E7 figure the record states is PARSED from L4-E7's output and guard draft (no placeholder is left, the INP
    figure is the rating table's own), the INP reader reads both the earlier and the set 27 row layouts on fixtures and refuses a file
    without the row.
Run: env -C v2/ecad/tools/tests python3 run.py test_l6pwr"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(REPO, "v2", "docs", "records", "l6pwr")
sys.path.insert(0, TOOLS)
import part_identities as PI  # noqa: E402


def _load(name):
    path = os.path.join(REC, name)
    if not os.path.exists(path): raise Skip("%s is not in the tree" % path)
    sp = importlib.util.spec_from_file_location("l6pwr_" + name[:-3], path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def _table():
    import yaml
    return yaml.safe_load(open(PI.TABLE, encoding="utf-8"))


def _block():
    t = _table()
    b = t.get("drafted_identities_l4_power")
    assert b, "pcb_part_identities.yaml carries no drafted_identities_l4_power block"
    return b


def t_the_block_is_the_one_the_record_renders():
    import yaml
    r = subprocess.run([sys.executable, "-B", os.path.join(REC, "l6pwr_parts.py"), "--identities"], cwd=REPO, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-300:]
    rendered = yaml.safe_load(r.stdout)["drafted_identities_l4_power"]
    assert json.dumps(rendered, sort_keys=True, default=str) == json.dumps(_block(), sort_keys=True, default=str), "the yaml block differs from the record's render"


def t_the_block_is_outside_the_selections_and_the_check_still_reads_the_table():
    t = _table()
    ids = {s["id"] for s in t["selections"]}
    for row in _block()["rows"]:
        assert row["id"] not in ids, "%s is both a selection and a drafted identity" % row["id"]
        assert row["id"].startswith("L6P-")
    # the check reads scope, inputs, selections and counts and never the block
    assert t["counts"]["selections"] == len(t["selections"])


def t_every_row_has_the_tables_vocabulary():
    for row in _block()["rows"]:
        i = row["identity"]
        assert i["status"] in PI.STATUSES, (row["id"], i["status"])
        if i["status"] == "RESOLVED":
            ds = i.get("datasheet") or {}
            assert i.get("maker") and i.get("mpn"), row["id"]
            assert ds.get("path") and ds.get("sha256") and ds.get("page"), "%s is RESOLVED without a path, sha256 and page" % row["id"]
            assert ds.get("binding") == "PRINTED", "%s is RESOLVED on a %s binding" % (row["id"], ds.get("binding"))
            assert ds.get("held_back") or os.path.exists(os.path.join(REPO, ds["path"])), "%s cites a document not in the tree" % row["id"]
        else:
            assert i.get("reason_class") in PI.REASONS, (row["id"], i.get("reason_class"))
            assert i.get("reason") and i.get("next_action"), row["id"]
        assert row.get("selected_by") and row.get("draft") and row.get("provisional") is not None, row["id"]


def t_rule_d2_holds_on_every_resolved_binding_present_here():
    read = unread = 0
    for row in _block()["rows"]:
        i = row["identity"]
        if i["status"] != "RESOLVED": continue
        ds = dict(i["datasheet"])
        r = PI.read_binding(ds, i["mpn"], root=REPO)
        if r["state"] == "UNREAD":
            assert ds.get("held_back"), "%s reads UNREAD without being held back" % row["id"]
            unread += 1; continue
        assert r["state"] == "READ", "%s: %s" % (row["id"], r.get("why"))
        read += 1
    assert read + unread > 0
    if read == 0: raise Skip("every RESOLVED document is held back and not fetched here (%d UNREAD)" % unread)


def t_a_decode_note_binding_names_a_page_that_does_not_print_the_part_number():
    n = 0
    for row in _block()["rows"]:
        i = row["identity"]
        ds = i.get("datasheet") or {}
        if ds.get("binding") != "DECODE_NOTE": continue
        assert i["status"] == "UNRESOLVED" and i["reason_class"] == "PART_NUMBER_INFERRED", row["id"]
        full = os.path.join(REPO, ds["path"])
        if not os.path.exists(full):
            assert ds.get("held_back"); continue
        ok, _ = PI.names_part(PI.page_text(full, int(ds["page"])), i["mpn"])
        assert not ok, "%s: page %s prints %s after all, so the binding is PRINTED, not a decode note" % (row["id"], ds["page"], i["mpn"])
        n += 1
    assert n >= 1 or any((r["identity"].get("datasheet") or {}).get("binding") == "DECODE_NOTE" for r in _block()["rows"])


def t_the_record_carries_no_dash_and_no_private_path():
    """The patterns are stored encoded, as test_public_hygiene stores them: a test that spelled them out would be a public copy of
    what it keeps out."""
    import base64
    private = [base64.b64decode(e).decode() for e in ('L2hvbWUvY2xhdWRlLXJ1bm5lcg==', 'L3RtcC9jbGF1ZGUt', 'bmxsZWkwMQ==')]
    dashes = (chr(0x2013), chr(0x2014))
    bad = []
    for root, _, files in os.walk(REC):
        for f in files:
            p = os.path.join(root, f)
            if f.endswith((".png", ".pdf")): continue
            s = open(p, encoding="utf-8", errors="replace").read()
            if any(d in s for d in dashes): bad.append(("dash", os.path.relpath(p, REPO)))
            for pat in private:
                if pat in s: bad.append(("private", os.path.relpath(p, REPO)))
    assert not bad, bad


def t_the_designator_detector_parses_and_finds_a_shared_designator():
    m = _load("l6pwr_parts.py")
    with tempfile.TemporaryDirectory() as d:
        bank = os.path.join(d, "bank.py"); chg = os.path.join(d, "charger.py"); clean = os.path.join(d, "clean.py")
        open(bank, "w").write('"""R221 to R226 must be unused: prose, not a reservation."""\nRB_REFS = ("R221", "R222")\n')
        open(chg, "w").write('"""adds R221 in prose only"""\nEDITS = [("old", \'r("R221", "11k 0.1%", "EF_ILIM", "GND")\\n\')]\n')
        open(clean, "w").write('EDITS = [("old", \'r("R301", "11k", "A", "B")\\n\')]\n')
        rel = lambda p: os.path.relpath(p, m.TOP)
        # the detector reads only string constants and the RB_REFS assignment, never the docstrings' prose
        assert m.reserved_refs(rel(bank)) == {"R221", "R222"}
        assert m.designators_added(rel(chg)) == {"R221"}
        assert m.designators_added(rel(clean)) == {"R301"}
        assert m.reserved_refs(rel(bank)) & m.designators_added(rel(chg)) == {"R221"}
        assert not (m.reserved_refs(rel(bank)) & m.designators_added(rel(clean)))


def t_the_grade_verdict_is_the_envelopes():
    m = _load("l6pwr_parts.py")
    assert m.verdict(-40, 125) == "INSIDE"
    assert m.verdict(-20, 125) == "AT_LIMIT"
    assert m.verdict(-40, 62.1) == "AT_LIMIT"
    assert m.verdict(-10, 60) == "OUTSIDE"
    assert m.verdict(0, 70) == "OUTSIDE"
    assert m.verdict(None, 125) == "NOT READ"
    assert m.margins_covered((-55, 150, "x", 1, "y")).startswith("covers")
    assert m.margins_covered((-20, 45, "x", 1, "y")).startswith("does NOT")


def t_the_catalogue_readings_are_in_the_tree_and_the_output_is_derived_from_them():
    m = _load("l6pwr_parts.py")
    out = os.path.join(REC, "l6pwr_parts.out")
    assert os.path.exists(out), "the record's output is missing"
    text = open(out, encoding="utf-8").read()
    for rel in (m.LCSC_READING, m.JLC_READING, m.SAMSUNG_READING):
        p = os.path.join(REPO, rel)
        assert os.path.exists(p), rel
        d = json.load(open(p, encoding="utf-8"))
        assert d.get("what") and d.get("read_by"), rel
        # the output pins each reading by its current sha256 (regen_out's rule R4)
        sha = PI.sha256(p)
        assert re.search(re.escape(sha) + r"\s+" + re.escape(rel), text), "%s is not pinned in the output at its current sha256" % rel
    lcsc = json.load(open(os.path.join(REPO, m.LCSC_READING), encoding="utf-8"))
    for r in lcsc["rows"]:
        if "error" in r: continue
        for k in ("code", "model", "brand", "package", "stock", "price_usd", "read_utc"):
            assert k in r, (r["code"], k)


def t_every_part_names_what_the_brief_asks():
    m = _load("l6pwr_parts.py")
    for p in m.PARTS:
        for k in ("id", "board", "refs", "maker", "mpn", "package", "land", "draft", "selected_by", "ratings", "codes", "need_per_kit",
                  "alternative", "obligations", "rationale", "identity"):
            assert p.get(k) not in (None, "", []) or k in ("codes",), (p["id"], k)
        assert p["grade"] is None or ("op" in p["grade"] and "kind" in p["grade"]), p["id"]
        assert p["identity"][0] in PI.STATUSES
        if p["identity"][0] == "UNRESOLVED": assert p["identity"][1] in PI.REASONS, p["id"]
        if p["doc"]: assert p["doc"][0] in m.DOCS and p["doc"][2] in ("PRINTED", "DECODE_NOTE"), p["id"]
    ids = [p["id"] for p in m.PARTS]
    assert len(ids) == len(set(ids))


def t_every_l4e7_figure_is_parsed_from_l4e7s_output():
    m = _load("l6pwr_parts.py")
    F = m.fill_parts()
    for p in m.PARTS:
        for k, v in p.items():
            assert "<<" not in json.dumps(v), (p["id"], k)
    v, line, tol, margin, holds = F["inp"]
    assert F["placeholders"]["INP_REF"] == "%.4f" % v and abs((line - v) - margin) < 1e-3, (v, line, margin)
    assert F["R97"]["mpn"] != "none" and F["R97"]["tol"] == tol, F["R97"]


def t_the_inp_reader_reads_both_row_layouts_and_refuses_a_file_without_the_row():
    m = _load("l6pwr_parts.py")
    rows = {"old": "         - U21's INP (R96 over R97)                            17.9046 of  18.0000, margin  0.0954; holds from 3.25 uH\n",
            "new": "         - U21's INP (R96 over R97, both at 0.1 %)             18.2878 of  18.0000, margin -0.2878; holds from 3.58 uH\n"}
    with tempfile.TemporaryDirectory() as td:
        got = {}
        for k, line in rows.items():
            p = os.path.join(td, k + ".out"); open(p, "w", encoding="utf-8").write("x\n" + line)
            got[k] = m.inp_line_from_out(p)
        assert got["old"][:3] == (17.9046, 18.0, None) and got["new"][:3] == (18.2878, 18.0, 0.1), got
        assert got["new"][3] == -0.2878 and got["new"][4] == "3.58 uH", got
        p = os.path.join(td, "none.out"); open(p, "w", encoding="utf-8").write("nothing\n")
        try:
            m.inp_line_from_out(p)
        except SystemExit as e:
            assert e.code == 3
        else:
            raise AssertionError("a file without the INP row was read")
