#!/usr/bin/env python3
"""Set 33's rows for the adoption pages (MESHSAT-1357, 7 October 2026, W165): `v2/docs/records/int33/ENTRY-PAGES.patch.md` holds
exact rows (S-nn for START-HERE.md, U-nn for SUPPLIER-HANDOVER.md, L-nn for LAYER-STATUS.md, P-nn for EXECUTION-PLAN.md), each with
its page, its line, one line of old text (or a part of one), the new text and its basis, in set 32's form
(`records/int32/ENTRY-PAGES.patch.md`, W95 and W102; its test `test_patch32.py`).

The pages the rows are written for are set 32's adoption's on main (AT, 46d4fe58, main after set 32's adoption and its dependency
pass; W170, queue item Q-192, moved AT from fnd/adopt32's cb78bc49, against which W165 wrote the rows: the four pages are the same bytes
at both, `git diff --stat cb78bc49 46d4fe58` naming none of them), read through git; none of set 33's branches changes them. Which pages are read besides is decided by the tree's own START-HERE.md, its line 3, when the
tree holds AT: "Current revision: set 32" the tree's own pages before the rows (every row must hold there too); "Current revision:
set 33" the rows applied (every row's new text must stand on its page, a token or the value filled). Where AT is absent (a host
without the adoption branch's objects), Skip with that reason.

What fails here: a row whose page, line or old text does not hold (the old text not exactly once on its line); two rows on one line;
an old text that is not one line or carries a token; a new text equal to its old text; an "after line" row whose new text does not
begin with the whole old text and a line break; a row id out of order or a count per page that is not the record's; a token other than
CANDIDATE, ADOPTION and GATE; ADOPTION outside the Adopted rows; P-01's three GATE lines without the words the fill tool and the
adoption script key on; the rows applied (bottom-up per page) leaving a new text off its page; an em or en dash. Each predicate is
run on a mutant it must refuse. Read-only (git show, git merge-base); tests/run.py runs the `t_` functions; `test_` aliases for pytest."""
import os
import re
import subprocess

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
PATCH = "v2/docs/records/int33/ENTRY-PAGES.patch.md"
AT = "46d4fe58a233f1417f28e5932b862e884940cd62"      # main after set 32's adoption (W170; was fnd/adopt32's cb78bc49, the same four pages)
AT32 = "cb78bc49b799097df0fe158754d73c2bb72f9e5a"    # fnd/adopt32 after set 32's second fill run: W165's reading, held equal to AT's pages
PAGES = {"S": "v2/docs/handover/START-HERE.md", "U": "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md",
         "L": "v2/docs/handover/LAYER-STATUS.md", "P": "v2/docs/EXECUTION-PLAN.md"}
COUNTS = {"S": 8, "U": 6, "L": 2, "P": 1}
IDS = ("S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "S-07", "S-11", "U-01", "U-02", "U-03", "U-04", "U-05", "U-10", "L-01", "L-02", "P-01")
ADOPTED_ROWS = ("S-07", "U-05")
ALLOWED = ("CANDIDATE", "ADOPTION", "GATE")
GATE_WORDS = ("the promotion log's line", "suite_gate with G7", "candidate_guard check, every host")
TOK = re.compile(r"__([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)__")
HEAD = re.compile(r"^### ([SULP])-(\d\d)\. `([^`]+)`, (after )?line (\d+): (.+)$", re.M)
BODY = re.compile(r"\A\s*Old text:\n```text\n(.*?)\n```\nNew text:\n```text\n(.*?)\n```\nBasis: (\S.*?)\s*\Z", re.S)
DASHES = ("—", "–")


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def _has(sha):
    return subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True).returncode == 0


def _read(rel):
    return open(os.path.join(REPO, rel), encoding="utf-8").read()


def _rows(text):
    heads = list(HEAD.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = re.split(r"\n## (?:START-HERE|SUPPLIER-HANDOVER|LAYER-STATUS|EXECUTION-PLAN)\.md\n", text[m.end():end], maxsplit=1)[0]
        b = BODY.match(body)
        out.append({"id": "%s-%s" % (m.group(1), m.group(2)), "letter": m.group(1), "page": m.group(3), "after": bool(m.group(4)),
                    "line": int(m.group(5)), "old": b.group(1) if b else None, "new": b.group(2) if b else None,
                    "basis": b.group(3) if b else None})
    return out


def p_rows(text):
    bad = []
    rows = _rows(text)
    seen = {}
    for r in rows:
        if r["old"] is None:
            bad.append("%s: no Old text / New text / Basis body" % r["id"])
            continue
        if PAGES[r["letter"]] != r["page"]:
            bad.append("%s names %s, not its page %s" % (r["id"], r["page"], PAGES[r["letter"]]))
        seen.setdefault(r["letter"], []).append(int(r["id"][2:]))
        if "\n" in r["old"] or TOK.search(r["old"]):
            bad.append("%s: its old text is not one line without a token" % r["id"])
        if r["new"] == r["old"]:
            bad.append("%s: its new text equals its old text" % r["id"])
        if r["after"] and not r["new"].startswith(r["old"] + "\n"):
            bad.append("%s: an after-line row whose new text does not begin with the old text and a line break" % r["id"])
        toks = TOK.findall(r["new"])
        if any(t not in ALLOWED for t in toks):
            bad.append("%s carries a token outside %s: %s" % (r["id"], ALLOWED, toks))
        if "__ADOPTION__" in text and ("ADOPTION" in toks) != (r["id"] in ADOPTED_ROWS):   # before the fill's second run
            bad.append("%s: ADOPTION belongs to the Adopted rows %s only" % (r["id"], ADOPTED_ROWS))
    for k, ns in seen.items():
        if ns != sorted(ns) or len(set(ns)) != len(ns) or len(ns) != COUNTS[k]:
            bad.append("the %s rows are %s, not %d in order" % (k, ns, COUNTS[k]))
    if tuple(r["id"] for r in rows) != IDS:
        bad.append("the row ids are %s, not the record's %s" % ([r["id"] for r in rows], IDS))
    lines = [(r["page"], r["line"]) for r in rows]
    if len(set(lines)) != len(lines):
        bad.append("two rows name one line")
    p01 = [r for r in rows if r["id"] == "P-01"]
    if p01:
        for ln in p01[0]["new"].split("\n"):
            if "__GATE__" in ln and not any(w in ln for w in GATE_WORDS):
                bad.append("P-01's GATE line %r carries none of the words the fill tool and the adoption script key on" % ln[:60])
        for w in GATE_WORDS:   # the words stay after the fill; the token with them before it
            if not [ln for ln in p01[0]["new"].split("\n") if w in ln and ("__GATE__" in ln or "__GATE__" not in p01[0]["new"])]:
                bad.append("P-01 has no GATE line carrying %r" % w)
    return bad


def p_hygiene(text):
    bad = ["the patch file carries %r" % d for d in DASHES if d in text]
    head = text.split("\n\n", 2)[1]
    for w in ("**DONE:**", "**NOT DONE:**", "**NEXT:**"):
        if w not in head:
            bad.append("the state paragraph lacks %s" % w)
    if "nothing in the kit has been" not in text:
        bad.append("no prototype framing")
    return bad


def p_pages(rows, pages):
    bad = []
    for r in rows:
        ls = pages[r["page"]]
        if r["line"] > len(ls) or ls[r["line"] - 1].count(r["old"]) != 1:
            bad.append("%s: its old text is not once on %s line %d" % (r["id"], r["page"], r["line"]))
    return bad


def _apply(rows, pages):
    out = {p: list(ls) for p, ls in pages.items()}
    for r in sorted(rows, key=lambda x: -x["line"]):
        ls = out[r["page"]]
        ls[r["line"] - 1:r["line"]] = ls[r["line"] - 1].replace(r["old"], r["new"], 1).split("\n")
    return out


def _loose(new):
    """The new text with each token as a wildcard (the value the fill writes there), for a page after the fill."""
    return re.compile(".*?".join(re.escape(part) for part in TOK.split(new)[::2]), re.S)


def p_applied(rows, pages):
    bad = []
    for r in rows:
        text = "\n".join(pages[r["page"]])
        if r["new"] not in text and not _loose(r["new"]).search(text):
            bad.append("%s: its new text does not stand on %s" % (r["id"], r["page"]))
    return bad


def _at_pages():
    if not _has(AT):
        raise Skip("%s (main after set 32's adoption) is not in this repository" % AT[:8])
    return {p: _git("show", "%s:%s" % (AT, p)).split("\n") for p in PAGES.values()}


def _tree_state():
    if not _has(AT) or subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", AT, "HEAD"], capture_output=True).returncode:
        return None
    line3 = _read(PAGES["S"]).split("\n")[2]
    return 33 if line3.startswith("**Current revision: set 33") else 32 if line3.startswith("**Current revision: set 32") else None


def _mutant_refused(pred, text, old, new, *extra):
    assert old in text, "the mutation's anchor %r is not in the text" % old[:60]
    assert pred(text.replace(old, new, 1), *extra), "%s passed a mutant (%r)" % (pred.__name__, new[:60])


def t_the_rows_are_well_formed():
    text = _read(PATCH)
    assert not p_rows(text), p_rows(text)
    assert not p_hygiene(text), p_hygiene(text)
    _mutant_refused(p_rows, text, "### U-10. ", "### U-11. ")
    _mutant_refused(p_rows, text, "set 33's promoted revision (set 32's was", "set 33's promoted revision `__ADOPTION__` (set 32's was")
    _mutant_refused(p_rows, text, "set 33's promoted revision (set 32's was", "set 33's promoted revision `__PROMOTED__` (set 32's was")
    _mutant_refused(p_rows, text, "Gated by suite_gate with G7 (`_bin/suite_gate.py`)", "Gated by the suite gate (`_bin/suite_gate.py`)")
    _mutant_refused(p_hygiene, text, "**NOT DONE:**", "**NOT DONE:** —")


def t_every_row_holds_on_set_32s_adopted_pages():
    rows = _rows(_read(PATCH))
    pages = _at_pages()
    assert not p_pages(rows, pages), p_pages(rows, pages)
    applied = _apply(rows, pages)
    assert not p_applied(rows, applied), p_applied(rows, applied)
    if _has(AT32):   # W170's basis for moving AT: the four pages are the same bytes at cb78bc49 and at main 46d4fe58
        assert {p: _git("show", "%s:%s" % (AT32, p)).split("\n") for p in PAGES.values()} == pages, "the pages moved between cb78bc49 and AT"
    bad = [dict(r) for r in rows]
    bad[0]["line"] += 1
    assert p_pages(bad, pages), "p_pages passed a row moved one line"
    assert p_applied(rows, pages), "p_applied passed pages without the rows"
    st = _tree_state()
    if st == 32:
        tree = {p: _read(p).split("\n") for p in PAGES.values()}
        assert not p_pages(rows, tree), p_pages(rows, tree)
    elif st == 33:
        tree = {p: _read(p).split("\n") for p in PAGES.values()}
        assert not p_applied(rows, tree), p_applied(rows, tree)


def _pytest(fn):
    def run():
        try:
            fn()
        except Skip as e:
            import pytest
            pytest.skip(str(e))
    run.__name__ = "test_" + fn.__name__[2:]
    run.__doc__ = fn.__doc__
    return run


test_the_rows_are_well_formed = _pytest(t_the_rows_are_well_formed)
test_every_row_holds_on_set_32s_adopted_pages = _pytest(t_every_row_holds_on_set_32s_adopted_pages)
