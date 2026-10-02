"""Layer 4's findings ledger (MESHSAT-1357, 2 October 2026; v2/docs/records/l4close/), held as predicates on its text.

The owner's item 3 of 2 October 2026: for the final candidates, map every previously rejected material finding to its
correction and targeted verification, name the reviewer and the exact revision, and preserve the collaborator's original
verdicts. FINDINGS-LEDGER.md does that for L4-E7, L4-E7Q, L4-E7R, L4-E8, L4-E9, L4-E10, L4-E11, L4-E12 and L4-E13;
findings_inventory.py lists the blocking items of every collaborator (Astra) check of those tasks from the filed check files.

The predicates: every blocking item the inventory finds has exactly one row, by check file and item ID, and no row names an
item the inventory does not find; every row quotes its check file's first line as filed, and names the job and the revision
the check read; every row's key agrees with its file (task and check number); every row carries one of the four residual
states (CLOSED, CLOSED AS CONDITIONAL, OPEN DOWNSTREAM, STILL OPEN); every cross-reference names an existing row; the
summary's counts equal the rows'; every STILL OPEN row appears under "Concrete remaining risks"; no em or en dash in the
ledger, the inventory script or this module. These are software predicates on the record's own text: they establish no
electrical or thermal property and close no finding.

The independent verification of 2 October 2026 (VERIFICATION-2026-10-02.md, its code verify_risks.py and its output
verify_risks.out): the page has one section for each of the concrete risks 2 to 7, 9 and 11 it took, each with exactly one
verdict (CONFIRMED, DIFFERS, CANNOT VERIFY, or NOT YET VERIFIED (paused) at a checkpoint) that agrees with the page's table;
every ledger row that cites one of its items cites a section that exists and is settled, and every settled item is cited by
a ledger row; every figure a settled section lists as printed appears in verify_risks.out; and the three files carry no em
or en dash. Again predicates on text: the verification's engineering content is the page's, not this module's.

Added on set 27 (the verification resumed): each item's verdict agrees with the ledger state of the rows its table names (a
DIFFERS item leaves its rows STILL OPEN; a CONFIRMED item leaves none of them STILL OPEN); and verify_risks.py loads no record
it checks as code (its one loaded module is Layer 3's records/hc2/pwr_red2.py, an input) and runs no Python child.
"""
import importlib.util
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
RECORDS = os.path.join(ROOT, "v2", "docs", "records")
REC = os.path.join(RECORDS, "l4close")
LEDGER = os.path.join(REC, "FINDINGS-LEDGER.md")
INVENTORY = os.path.join(REC, "findings_inventory.py")
VERIF = os.path.join(REC, "VERIFICATION-2026-10-02.md")
VERIF_PY = os.path.join(REC, "verify_risks.py")
VERIF_OUT = os.path.join(REC, "verify_risks.out")
VERIF_ITEMS = (2, 3, 4, 5, 6, 7, 9, 11)
VERDICTS = ("CONFIRMED", "DIFFERS", "CANNOT VERIFY", "NOT YET VERIFIED (paused)")
PAUSED = "NOT YET VERIFIED (paused)"
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

STATES = ("CLOSED AS CONDITIONAL", "OPEN DOWNSTREAM", "STILL OPEN", "CLOSED")
KEY = re.compile(r"^(L4-E\d+[QR]?):([12])\.(\d+) `([^`]+)`$")
FILE = re.compile(r"`(astra-check-l4e[0-9a-z]+-[0-9]+\.md)`")
VERDICT = re.compile(r"filed `(accepted: (?:yes|no))`")
STATE = re.compile(r"^\*\*(%s)\*\*" % "|".join(re.escape(s) for s in STATES))
REF = re.compile(r"\bL4-E\d+[QR]?:[12]\.\d+\b")
DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
_C = {}


def _inventory():
    if "inv" not in _C:
        need(INVENTORY, "the findings inventory")
        sp = importlib.util.spec_from_file_location("l4close_findings_inventory_under_test", INVENTORY)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C["inv"] = m.inventory()
    return _C["inv"]


def _text():
    if "text" not in _C:
        need(LEDGER, "the findings ledger")
        with open(LEDGER, encoding="utf-8") as fh:
            _C["text"] = fh.read()
    return _C["text"]


def _rows():
    """Every finding row of the ledger: its key, label, the five cells, the file and the verdict it quotes, its state."""
    if "rows" not in _C:
        rows = []
        for ln in _text().splitlines():
            if not ln.startswith("| L4-E"):
                continue
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            m = KEY.match(cells[0])
            if not m:
                continue
            assert len(cells) == 5, "row %s has %d cells, not 5" % (cells[0], len(cells))
            files = FILE.findall(cells[1])
            verdicts = VERDICT.findall(cells[1])
            st = STATE.match(cells[4])
            rows.append({
                "key": "%s:%s.%s" % (m.group(1), m.group(2), m.group(3)),
                "task": m.group(1), "check": m.group(2), "label": m.group(4), "cells": cells,
                "file": files[0] if len(files) == 1 else None,
                "verdict": verdicts[0] if len(verdicts) == 1 else None,
                "state": st.group(1) if st else None,
            })
        _C["rows"] = rows
    return _C["rows"]


def _section(title):
    text = _text()
    i = text.find("\n## %s" % title)
    assert i >= 0, "the ledger has no section %r" % title
    j = text.find("\n## ", i + 1)
    return text[i:j if j >= 0 else len(text)]


def _folder(name):
    return re.match(r"astra-check-(l4e\d+)", name).group(1)


def t_every_blocking_item_has_exactly_one_row():
    want = [(name, ident) for name, _v, _m, items in _inventory() for ident, _t in items]
    assert want, "the inventory found no blocking item"
    assert len(set(want)) == len(want), "the inventory lists one item twice"
    got = [(r["file"], r["label"]) for r in _rows()]
    for r in _rows():
        assert r["file"], "row %s names no single check file in its finding cell" % r["key"]
    dup = sorted(set(g for g in got if got.count(g) > 1))
    assert not dup, "items with more than one row: %s" % dup
    missing = sorted(set(want) - set(got))
    assert not missing, "blocking items with no row: %s" % missing
    extra = sorted(set(got) - set(want))
    assert not extra, "rows naming no blocking item of the check files: %s" % extra
    keys = [r["key"] for r in _rows()]
    assert len(set(keys)) == len(keys), "a row key is used twice"


def t_every_row_quotes_its_checks_first_line():
    for r in _rows():
        assert r["verdict"], "row %s quotes no single filed verdict" % r["key"]
        path = os.path.join(RECORDS, _folder(r["file"]), "checks", r["file"])
        need(path, "the filed check %s" % r["file"])
        with open(path, encoding="utf-8") as fh:
            first = fh.readline().strip()
        assert r["verdict"] == first, "row %s quotes %r, the file's first line is %r" % (r["key"], r["verdict"], first)


def t_every_row_names_the_job_and_the_revision_read():
    meta = {name: m for name, _v, m, _i in _inventory()}
    for r in _rows():
        m = meta[r["file"]]
        assert m["job"] and m["job"] in r["cells"][1], "row %s does not name the job %s" % (r["key"], m["job"])
        assert m["revision"] and "`%s`" % m["revision"] in r["cells"][1], \
            "row %s does not name the revision read, %s" % (r["key"], m["revision"])


def t_every_row_key_agrees_with_its_file():
    for r in _rows():
        m = re.match(r"astra-check-(l4e[0-9]+[qr]?)-([0-9]+)\.md$", r["file"])
        assert m, r["file"]
        assert r["task"].replace("-", "").lower() == m.group(1), "row %s sits in the wrong task for %s" % (r["key"], r["file"])
        assert r["check"] == m.group(2), "row %s carries check %s, its file is check %s" % (r["key"], r["check"], m.group(2))


def t_every_row_carries_one_of_the_four_states():
    for r in _rows():
        assert r["state"] in STATES, "row %s: its residual cell does not open with one of %s: %r" % (
            r["key"], STATES, r["cells"][4][:60])


def t_every_cross_reference_names_a_row():
    keys = set(r["key"] for r in _rows())
    bad = sorted(set(ref for ref in REF.findall(_text()) if ref not in keys))
    assert not bad, "references to rows that do not exist: %s" % bad


def t_the_summary_counts_the_rows():
    counts = {}
    for r in _rows():
        c = counts.setdefault(r["task"], dict((s, 0) for s in STATES))
        c[r["state"]] += 1
    order = ("CLOSED", "CLOSED AS CONDITIONAL", "OPEN DOWNSTREAM", "STILL OPEN")
    seen, total = set(), dict((s, 0) for s in STATES)
    for ln in _section("Summary").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")] if ln.startswith("| ") else []
        if len(cells) != 6 or not (cells[0].startswith("L4-E") or cells[0] == "All"):
            continue
        nums = [int(x) for x in cells[1:]]
        if cells[0] == "All":
            want = [sum(total.values())] + [total[s] for s in order]
            assert nums == want, "the summary's All row reads %s, the rows give %s" % (nums, want)
            seen.add("All")
            continue
        c = counts.get(cells[0])
        assert c, "the summary names %s, which has no row" % cells[0]
        want = [sum(c.values())] + [c[s] for s in order]
        assert nums == want, "the summary's %s row reads %s, the rows give %s" % (cells[0], nums, want)
        for s in STATES:
            total[s] += c[s]
        seen.add(cells[0])
    assert seen == set(counts) | {"All"}, "the summary misses %s" % sorted(set(counts) | {"All"} - seen)


def t_every_still_open_row_is_a_concrete_risk():
    risks = _section("Concrete remaining risks")
    for r in _rows():
        if r["state"] == "STILL OPEN":
            assert r["key"] in risks, "row %s is STILL OPEN and absent from the concrete risks" % r["key"]


def _verif():
    if "verif" not in _C:
        need(VERIF, "the independent verification page")
        with open(VERIF, encoding="utf-8") as fh:
            text = fh.read()
        secs = {}
        for m in re.finditer(r"^## Item (\d+)\n(.*?)(?=^## |\Z)", text, re.M | re.S):
            secs[int(m.group(1))] = m.group(2)
        table = dict((int(a), b.strip()) for a, b in re.findall(r"^\| (\d+) \| [^|]+ \| ([^|]+) \|$", text, re.M))
        _C["verif"] = (text, secs, table)
    return _C["verif"]


def _verdict(body):
    v = re.findall(r"^\*\*Verdict:\*\* (.+)$", body, re.M)
    assert len(v) == 1, "a section carries %d verdict lines, not one" % len(v)
    return v[0].strip()


def t_the_verification_has_one_section_and_one_verdict_per_item():
    _text, secs, table = _verif()
    assert sorted(secs) == sorted(VERIF_ITEMS), "the verification's item sections are %s, not %s" % (sorted(secs), list(VERIF_ITEMS))
    for n in VERIF_ITEMS:
        v = _verdict(secs[n])
        assert v in VERDICTS, "item %d's verdict %r is not one of %s" % (n, v, VERDICTS)
        assert table.get(n) == v, "item %d: the page's table reads %r, its section %r" % (n, table.get(n), v)


def t_the_ledger_cites_every_settled_item_and_no_paused_one():
    _text, secs, _t = _verif()
    settled = set(n for n in VERIF_ITEMS if _verdict(secs[n]) != PAUSED)
    cited = set()
    for r in _rows():
        for n in re.findall(r"VERIFICATION-2026-10-02\.md`?,? Item (\d+)", " ".join(r["cells"][2:])):
            n = int(n)
            assert n in secs, "row %s cites Item %d, which the page does not have" % (r["key"], n)
            assert n in settled, "row %s cites Item %d, which is %s" % (r["key"], n, PAUSED)
            cited.add(n)
    assert settled <= cited, "settled items no ledger row cites: %s" % sorted(settled - cited)


def t_every_printed_figure_is_in_the_output():
    _text, secs, _t = _verif()
    need(VERIF_OUT, "the verification's output")
    with open(VERIF_OUT, encoding="utf-8") as fh:
        out = fh.read()
    for n in VERIF_ITEMS:
        if _verdict(secs[n]) == PAUSED:
            continue
        lines = [ln for ln in secs[n].splitlines() if ln.startswith("Printed figures:")]
        assert len(lines) == 1, "settled item %d lists its printed figures %d times, not once" % (n, len(lines))
        figs = re.findall(r"`([^`]+)`", lines[0])
        assert figs, "settled item %d lists no printed figure" % n
        for f in figs:
            assert f in out, "item %d: %r is not in verify_risks.out" % (n, f)


def t_each_verdict_agrees_with_its_rows_states():
    text, secs, _t = _verif()
    states = dict((r["key"], r["state"]) for r in _rows())
    rows_of = dict((int(a), [k.strip() for k in b.split(",")]) for a, b in re.findall(r"^\| (\d+) \| ([^|]+) \| [^|]+ \|$", text, re.M))
    for n in VERIF_ITEMS:
        v = _verdict(secs[n])
        keys = rows_of.get(n)
        assert keys, "item %d's table row names no ledger row" % n
        for k in keys:
            assert k in states, "item %d names %s, which the ledger does not have" % (n, k)
            if v == "DIFFERS":
                assert states[k] == "STILL OPEN", "item %d DIFFERS but %s reads %s" % (n, k, states[k])
            if v == "CONFIRMED":
                assert states[k] != "STILL OPEN", "item %d is CONFIRMED but %s still reads STILL OPEN" % (n, k)


def t_the_verifier_loads_no_record_it_checks():
    import ast
    need(VERIF_PY, "the verification's code")
    with open(VERIF_PY, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    loaded = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "spec_from_file_location":
            loaded.extend(c.value for c in ast.walk(node) if isinstance(c, ast.Constant) and isinstance(c.value, str) and c.value.endswith(".py"))
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "run" and node.args and isinstance(node.args[0], ast.List):
            first = node.args[0].elts[0] if node.args[0].elts else None
            assert not (isinstance(first, ast.Attribute) and first.attr == "executable"), "verify_risks.py runs a Python child"
            assert not (isinstance(first, ast.Constant) and str(first.value).startswith("python")), "verify_risks.py runs a Python child"
    assert loaded == ["v2/docs/records/hc2/pwr_red2.py"], "verify_risks.py loads %s as code, not only Layer 3's model" % loaded


def t_no_em_or_en_dash():
    for path in (LEDGER, INVENTORY, os.path.abspath(__file__), VERIF, VERIF_PY, VERIF_OUT):
        need(path, os.path.basename(path))
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        for d in DASHES:
            assert d not in text, "%s carries U+%04X" % (os.path.relpath(path, ROOT), ord(d))
