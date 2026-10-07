#!/usr/bin/env python3
"""Set 32's adoption pages on the working tree (MESHSAT-1357, worker W105, branch fnd/adopt32, 7 October 2026), held as predicates
on their text: v2/docs/handover/START-HERE.md, v2/docs/handover/supplier/SUPPLIER-HANDOVER.md, v2/docs/handover/LAYER-STATUS.md and
v2/docs/EXECUTION-PLAN.md, with the 38 rows of v2/docs/records/int32/ENTRY-PAGES.patch.md (S-01 to S-15, U-01 to U-16, L-01 to L-06,
P-01; W95, corrected by W102 on W99's read) applied before set 32's promotion, their tokens left for the coordinator's fill
(`_bin/fill_res.py --set 32`, which reaches the four pages since W103).

Why this module: set 31's page tests (test_adopt31, test_entrypage, test_w30entry, test_lstat31) judge set 31's rows where set 31's
adoption made them, at its adoption commits 73941afc and ad757edb through git (W103's form, restated by W105 for the predicates set
32's rows broke), so what stands on the working tree after set 32's rows needs a test of its own. test_patch32 holds the rows (their
form, quotes, citations, counts, claims and the fill) and, once they are applied, that each row's new text is on its page and set 32's
blocks and milestone are placed; it does not hold that NOTHING ELSE changed. This module does: each of the four pages equals set 31's
adopted page (main ad757edb, read through git) with exactly these changes and no other: the own change of each branch set 32's chain
pins that the judged revision contains (its diff from its merge base with ad757edb, as test_patch32 applies them in memory), the
chain's step a5 where the page carries its sentence (W42's apply() from the script at 62300318), and the 38 rows, each located by
its old text (exactly once on the page, the line a hint), applied bottom-up, two rows on one line in the given order. So every text
of set 31 that no set 32 row replaces (W106's N-d: W68's F2 attributions on both entry pages, among them) is held on the working tree
too. A token of the rows matches itself or the value the fill wrote: CANDIDATE and ADOPTION one commit throughout the four pages, a
GATE token any text without a backtick or a line break. The fill's stage is read from set 32's RESULT.md, section 1 role rows (as
test_patch32 reads it): stage 0, every token of the rows stands literally; stage 1, the CANDIDATE and GATE tokens are filled and the
ADOPTION token stands; stage 2, no token stands. The text the rows add carries no em or en dash, no acceptance word outside a
quotation or a code span and no percentage (test_adopt31's word rule). Fixtures show that each checker refuses the defect it is for.

Which revision is judged: the working tree while its START-HERE.md line 3 names set 32 as the current revision; once a later set's
rows change that line, the newest commit of START-HERE.md whose line 3 still names set 32 (through git), so a later set's own edits
never fail this module (W100's B2: a rule about history); Skip with the reason when no revision holds set 32's rows or a commit it
needs is absent from the object store. Taken under the owner's standing rule of 26 September 2026 (authority SESSION, W105, on the
brief's form for set 32's rows); reversed by deleting this module and reading the tree's pages again in the set 31 predicates W105
restated.

These are software predicates on record text: they establish no electrical or thermal property and accept, close or promote
nothing; prototype framing: nothing in the kit has been built, bought, powered or measured. This file never writes a fill token
literally (it builds them with T()). Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_adopt32.`) and under
pytest (each t_ function has a test_ alias)."""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip  # noqa: E402
import test_patch32 as P32  # noqa: E402  (the rows' parser, the pins, step a5, the hunks and the fill stage, read-only)
from test_adopt31 import word_errors  # noqa: E402

START = P32.PAGES["S"]
ORDER = ("S", "U", "L", "P")
HEAD32 = "**Current revision: set 32, the revision `"
SEP = "\n\x00 the next page \x00\n"
DASHES = (chr(0x2013), chr(0x2014))


def T(name):
    """A fill-tool token by its name (never written literally in this file)."""
    return "__%s__" % name


HEX_TOKENS = ("CANDIDATE", "ADOPTION")
TOKEN_RE = re.compile(r"__(CANDIDATE|ADOPTION|GATE)__")
_C = {}


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git on this host (%s)" % e)
    return r


def _has(sha):
    return _git("cat-file", "-e", sha + "^{commit}").returncode == 0


def _show(c, p):
    k = ("show", c, p)
    if k not in _C:
        if not _has(c):
            raise Skip("commit %s is not in this object store" % c[:8])
        r = _git("show", "%s:%s" % (c, p))
        _C[k] = r.stdout.decode("utf-8") if r.returncode == 0 else None
    return _C[k]


def _tree(p):
    path = os.path.join(ROOT, p)
    if not os.path.isfile(path):
        raise AssertionError("%s is missing" % p)
    return open(path, encoding="utf-8").read()


def judged():
    """None for the working tree (its START-HERE line 3 names set 32), else the newest commit of START-HERE.md whose line 3 does."""
    if "judged" not in _C:
        lines = _tree(START).split("\n")
        if len(lines) > 2 and lines[2].startswith(HEAD32):
            _C["judged"] = None
        else:
            r = _git("log", "--format=%H", "--", START)
            found = None
            for c in r.stdout.decode().split() if r.returncode == 0 else ():
                t = _show(c, START)
                if t is not None and len(t.split("\n")) > 2 and t.split("\n")[2].startswith(HEAD32):
                    found = c
                    break
            if found is None:
                raise Skip("no revision of START-HERE.md names set 32 as the current revision (set 32's rows are not applied)")
            _C["judged"] = found
    return _C["judged"]


def _at(p):
    c = judged()
    if c is None:
        return _tree(p)
    t = _show(c, p)
    assert t is not None, "%s: no %s" % (c[:8], p)
    return t


def _contains(pin):
    """Whether the judged revision holds the pinned commit."""
    c = judged()
    return _git("merge-base", "--is-ancestor", pin, c or "HEAD").returncode == 0


# ---------------------------------------------------------------------------------------------------- the expected pages
def apply_rows(pages, rows):
    """{prefix: page} with every row applied, each located by its old text (exactly once on its page), bottom-up by its located
    line, two rows on one line in the given order. Refuses a row whose old text is not once on its page."""
    work = {k: v.split("\n") for k, v in pages.items()}
    located = []
    for i, (rid, pre, _n, _p, _after, line, old, new, _b) in enumerate(rows):
        ls = work[pre]
        hits = [k for k, x in enumerate(ls) if old in x]
        total = sum(x.count(old) for x in ls)
        assert total == 1, "%s: its old text stands %d times on its page, not once (line %d a hint): %r" % (rid, total, line, old[:60])
        located.append((pre, -hits[0], i, rid, hits[0], old, new))
    for pre, _neg, _i, rid, at, old, new in sorted(located):
        ls = work[pre]
        assert ls[at].count(old) == 1, "%s: the row before it on line %d consumed its old text" % (rid, at + 1)
        ls[at] = ls[at].replace(old, new, 1)
    return {k: "\n".join(v) for k, v in work.items()}


def base_pages(page_s=None):
    """Set 31's adopted pages at main ad757edb, with the own change of each pinned branch the judged revision holds; step a5 where
    the judged supplier page (page_s) carries its sentence."""
    out = {}
    for k in ORDER:
        t = _show(P32.AT, P32.PAGES[k])
        assert t is not None, "%s: no %s" % (P32.AT[:8], P32.PAGES[k])
        for pin in P32.PINS:
            if not _contains(pin):
                continue
            mb = _git("merge-base", P32.AT, pin).stdout.decode().strip()
            d = _git("diff", "-U3", mb, pin, "--", P32.PAGES[k]).stdout.decode()
            t = P32._apply_hunks(t, P32._hunks(d), "%s at %s" % (P32.PAGES[k], pin[:8]))
        out[k] = t
    if page_s is not None and _contains(P32.A5[0]):
        src = _show(P32.A5[0], P32.A5[1])
        ns = {"__name__": "a5_in_memory"}
        exec(compile(src, P32.A5[1], "exec"), ns)
        if ns["SENTENCE"] in page_s:
            out["U"] = ns["apply"](out["U"])
    return out


def _line_pattern(line):
    out, k = [], 0
    for m in TOKEN_RE.finditer(line):
        out.append(re.escape(line[k:m.start()]))
        name = m.group(1)
        if name in HEX_TOKENS:
            out.append("(?P<%s_%d>%s|[0-9a-f]{8,40})" % (name, len(out), re.escape(m.group(0))))
        else:
            out.append("(?:%s|[^`\\n]+?)" % re.escape(m.group(0)))
        k = m.end()
    out.append(re.escape(line[k:]))
    return "".join(out)


def page_errors(want, got):
    """want, got: {prefix: page}. Each page line for line: equal, or the expected line with each token literal or filled (CANDIDATE
    and ADOPTION one commit across the four pages, GATE a text with no backtick and no line break)."""
    errs, vals = [], {}
    for k in ORDER:
        a, b = want[k].split("\n"), got[k].split("\n")
        if len(a) != len(b):
            errs.append("%s: %d lines, set 31's adopted page with set 32's rows gives %d" % (P32.PAGES[k], len(b), len(a)))
            continue
        for i, (x, y) in enumerate(zip(a, b), 1):
            if x == y:
                continue
            m = re.fullmatch(_line_pattern(x), y) if TOKEN_RE.search(x) else None
            if not m:
                errs.append("%s:%d reads %r, the rows give %r" % (P32.PAGES[k], i, y[:70], x[:70]))
                continue
            for g, v in m.groupdict().items():
                vals.setdefault(g.split("_")[0], set()).add(v)
    for name, vs in sorted(vals.items()):
        filled = sorted(v for v in vs if v != T(name))
        if len(filled) > 1 or (filled and len(vs) > 1):
            errs.append("%s reads as %s across the pages, not one value" % (T(name), sorted(vs)))
    return errs


def stage_errors(st, want, got):
    """The fill's stage: 0, every token of the rows literal; 1, CANDIDATE and GATE filled, ADOPTION literal; 2, no token."""
    if st is None:
        return ["set 32's RESULT.md role rows are neither all tokens, nor all but ADOPTION filled, nor all filled"]
    errs = []
    for k in ORDER:
        for name in ("CANDIDATE", "ADOPTION", "GATE"):
            w, g = want[k].count(T(name)), got[k].count(T(name))
            keep = {0: True, 1: name == "ADOPTION", 2: False}[st]
            if g != (w if keep else 0):
                errs.append("fill stage %d: %s carries %s %d times, not %d" % (st, P32.PAGES[k], T(name), g, w if keep else 0))
    return errs


def added_text(rows):
    """The text the rows add: each new text with its old text taken out once."""
    return "\n\n".join(new.replace(old, "", 1) for _rid, _pre, _n, _p, _a, _line, old, new, _b in rows)


def _rows():
    rows = P32._rows(_at(P32.PATCH))
    assert rows and not isinstance(rows[0], str), rows
    return rows


def _got():
    return {k: _at(P32.PAGES[k]) for k in ORDER}


# ---------------------------------------------------------------------------------------------------------------- tests
def t_the_pages_are_set_31s_adopted_pages_with_set_32s_rows_and_nothing_else():
    rows = _rows()
    assert len(rows) == 38, len(rows)
    got = _got()
    want = apply_rows(base_pages(got["U"]), rows)
    errs = page_errors(want, got)
    assert not errs, errs[:6]


def t_the_tokens_stand_as_the_fill_stage_leaves_them():
    rows = _rows()
    got = _got()
    want = apply_rows(base_pages(got["U"]), rows)
    st = P32._fill_stage(_at(P32.RESULT))[0]
    errs = stage_errors(st, want, got)
    assert not errs, errs


def t_the_text_set_32_adds_carries_no_dash_no_acceptance_word_and_no_percentage():
    s = added_text(_rows())
    assert not any(d in s for d in DASHES), "a dash in set 32's text"
    errs = [e.replace("set 31's text", "set 32's text") for e in word_errors(s)]
    assert not errs, errs
    m = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in m for d in DASHES), "a dash in this module"


# ----------------------------------------------------------------------------- the checkers refuse what they are for
def _template_rows():
    """The rows as the newest committed patch file still holding the CANDIDATE token gives them (test_patch32's template): the
    fixtures below need the tokens, which the fill takes out of the tree's patch file."""
    if "tmpl" not in _C:
        _C["tmpl"] = None
        here = _at(P32.PATCH)
        if T("CANDIDATE") in here:
            _C["tmpl"] = here
        else:
            r = _git("log", "--format=%H", judged() or "HEAD", "--", P32.PATCH)
            for c in r.stdout.decode().split() if r.returncode == 0 else ():
                t = _show(c, P32.PATCH)
                if t is not None and "`%s`" % T("CANDIDATE") in t:
                    _C["tmpl"] = t
                    break
    t = _C["tmpl"]
    assert t is not None, "no revision of the patch file holds the tokens"
    rows = P32._rows(t)
    assert rows and not isinstance(rows[0], str), rows
    return rows


def t_the_checkers_refuse_their_defects():
    rows = _rows()
    got = _got()
    assert not page_errors(apply_rows(base_pages(got["U"]), rows), got)
    rows = _template_rows()
    want = apply_rows(base_pages(got["U"]), rows)
    filled = {k: v.replace(T("CANDIDATE"), "0123abcd").replace(T("ADOPTION"), "4567abcd").replace(T("GATE"), "a gate line")
              for k, v in want.items()}
    assert not page_errors(want, filled), page_errors(want, filled)[:3]
    s01 = [r for r in rows if r[0] == "S-01"][0]
    l02 = [r for r in rows if r[0] == "L-02"][0]
    mutants = {
        "a row not applied (its old text back)": dict(want, S=want["S"].replace(s01[7], s01[6], 1)),
        "a row's new text doubled": dict(want, L=want["L"] + "\n" + l02[7]),
        "a set 31 text no row replaces changed (W106's N-d, W68's F2)":
            dict(want, S=want["S"].replace("is set 30's promoted commit (main was", "is the promoted commit (main was", 1)),
        "a supplier attribution changed (W106's N-d)":
            dict(want, U=want["U"].replace("which records the coordinator's judgement on set 30's", "which records the coordinator's judgement on the", 1)),
        "a line added": dict(want, P=want["P"] + "\nan added line"),
        "set 32's Layer 9 block below set 31's": dict(want, L=_move_l9(want["L"])),
        "CANDIDATE filled with two values": dict(filled, U=filled["U"].replace("0123abcd", "89abcdef", 1)),
        "a token filled with a non-commit": dict(want, S=want["S"].replace(T("CANDIDATE"), "the candidate", 1)),
    }
    for name, pages in mutants.items():
        assert page_errors(want, pages), "page_errors accepts %s" % name
    # the stage: stage 0 refuses a filled token, stage 1 a literal CANDIDATE or a filled ADOPTION, stage 2 any token
    assert not stage_errors(0, want, want)
    assert stage_errors(0, want, dict(want, S=want["S"].replace(T("CANDIDATE"), "0123abcd", 1)))
    one = {k: v.replace(T("CANDIDATE"), "0123abcd").replace(T("GATE"), "a gate line") for k, v in want.items()}
    assert not stage_errors(1, want, one)
    assert stage_errors(1, want, dict(one, L=one["L"] + T("CANDIDATE")))
    assert stage_errors(1, want, dict(one, S=one["S"].replace(T("ADOPTION"), "4567abcd", 1)))
    assert not stage_errors(2, want, filled) and stage_errors(2, want, want)
    assert stage_errors(None, want, want)
    # the rows' application: an old text found twice, or consumed by a row before it on its line, refuses
    base = base_pages(got["U"])
    try:
        apply_rows(dict(base, S=base["S"] + "\n" + s01[6]), rows)
        raise RuntimeError("an old text standing twice was applied")
    except AssertionError:
        pass
    # the words: a dash, an acceptance word outside a quotation, a percentage
    assert word_errors("a " + DASHES[1]) and word_errors("the gate PASSES") and word_errors("90 % done")


def _move_l9(t):
    head = "## Layer 9. Pre-layout design analysis\n\n"
    i = t.index(head) + len(head)
    j = t.index("\n**After set 31 (6 October 2026): IN_PROGRESS", i) + 1
    block = t[i:j]
    k = t.index("\n**After set 30 (6 October 2026): IN_PROGRESS", j) + 1
    return t[:i] + t[j:k] + block + t[k:]


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
