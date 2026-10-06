#!/usr/bin/env python3
"""Set 32's rows for the adoption pages (MESHSAT-1357, 6 October 2026, W95): `v2/docs/records/int32/ENTRY-PAGES.patch.md` holds
exact rows (S-nn for START-HERE.md, U-nn for SUPPLIER-HANDOVER.md, L-nn for LAYER-STATUS.md, P-nn for EXECUTION-PLAN.md), each with
its page, its line, one line of old text, the new text and its basis, in the form of set 31's rows
(`records/int31/ENTRY-PAGES.patch.md`, W39, applied by W65).

The revision the rows are written for is the pages as they read after set 31's adoption. Which pages this test reads is decided by
the tree's own START-HERE.md, its line 3:
  "Current revision: set 31"  the tree holds set 31's adoption: the rows are read against the tree's pages (the target revision);
  "Current revision: set 32"  the rows are applied: every row's new text must stand on its page (a token or the value filled);
  anything else               this branch before set 31's adoption reaches it: the pages of fnd/adopt31 at AT, read through git, with
                              set 31's fill values applied in memory (FILL31: the CANDIDATE and PROMOTED tokens, set 31's candidate
                              5f25daf3); set 31's ADOPTION and GATE occurrences are left as they stand, and no old text may reach
                              them (an old text carries no token). Where AT is absent from the repository, Skip with that reason.
The record (its paragraph "What the rows are read against") gives why git and not copies under `inputs/`: copies would carry set 31's
tokens into set 32's tree for good (taken under the owner's standing rule of 26 September 2026, W95; reversal named there).

What fails here: a row whose page, line or old text does not hold on the pages read (the old text not exactly once on its line, or
not once on the line the rows before it on that line left, applied bottom-up per page); an old text that is not one line or carries a
token; a new text equal to its old text; an "after line" row whose new text does not begin with the whole old text; a row id out of
sequence or a page other than its prefix's; a token in a new text other than the CANDIDATE, ADOPTION and GATE tokens; a token of the
set left after the fill's stage (read from RESULT's section 1 role rows, as test_res32 reads them) or a filled value that is not the
role's commit at the place the template revision holds the token; a citation `<sha>:path:N` whose quote is not on that line at that
commit; a quote followed by its file and section that is not in that section of that file; a count the rows type that is not the
classification's at REC_AT or the pages'; a set 32 block not directly under its layer's heading above the set 31 block, or the plan's
entry not after set 31's; the record not naming the patch file in the way the fill tool finds it; an em or en dash; the paragraph
after the title not the DONE / NOT DONE / NEXT line. Each predicate is also run on a mutant it must refuse.

This file never writes a token of the fill tool literally (it builds them with T()), so the placeholder check of set 32's chain needs
no deferral row for it. Read-only: git is read with `git show`, `git log`, `git cat-file`; nothing is written. No pytest is needed
(tests/run.py runs the `t_` functions); `test_` aliases let pytest collect them."""
import os
import re
import subprocess

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = "v2/docs/records/int32"
PATCH = REC + "/ENTRY-PAGES.patch.md"
RESULT = REC + "/RESULT.md"
CLASS = REC + "/CLASSIFICATION.md"
AT = "b06ee99fab04ab8fdfcbe39a30684efe9a1b8222"      # fnd/adopt31's tip when the rows were written (set 31's adoption pages)
REC_AT = "ee9407426c27541fb77404dee1bc7100672af42f"  # this record's revision the rows count from (the 34 commits of five branches)
S31_CAND = "5f25daf3"                                 # set 31's candidate = its promotion (main fast-forwarded to it)
PAGES = {"S": "v2/docs/handover/START-HERE.md", "U": "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md",
         "L": "v2/docs/handover/LAYER-STATUS.md", "P": "v2/docs/EXECUTION-PLAN.md"}
COUNTS = {"S": 15, "U": 16, "L": 6, "P": 1}
ALLOWED = ("CANDIDATE", "ADOPTION", "GATE")
LAYERS = ("## Layer 4. ", "## Layer 5. ", "## Layer 8. ", "## Layer 9. ", "## Layer 12. ")
TOK = re.compile(r"__([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)__")
HEAD = re.compile(r"^### ([SULP])-(\d\d)\. `([^`]+)`, (after )?line (\d+): (.+)$", re.M)
BODY = re.compile(r"\A\s*Old text:\n```text\n(.*?)\n```\nNew text:\n```text\n(.*?)\n```\nBasis: (\S.*?)\s*\Z", re.S)
GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
QUOTE_SEC = (re.compile(r"((?:\"[^\"]+\"; )*\"[^\"]+\") \(`([^`]+\.md)`,\s+section (\w+)\)"),
             re.compile(r"`([^`]+\.md)`, section (\w+): \"([^\"]+)\"\)"))
DASHES = ("—", "–")


def T(name):
    """A fill-tool token by its name (never written literally in this file)."""
    return "__%s__" % name


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def _has(sha):
    try:
        r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    return r.returncode == 0


_C = {}


def _show(rev, path):
    k = (rev, path)
    if k not in _C:
        _C[k] = _git("show", "%s:%s" % (rev, path))
    return _C[k]


def _read(rel):
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        raise AssertionError("%s is missing" % rel)
    return open(p, encoding="utf-8").read()


# ---- the rows ----

def _rows(text):
    """[(id, prefix, number, page, after, line, old, new, basis)] in file order, or a list of problems (strings) where a row is malformed."""
    heads = list(HEAD.finditer(text))
    rows, bad = [], []
    ends, pos, fence = [], 0, False      # the headings outside the code fences end a row's body
    for ln in text.split("\n"):
        if ln.startswith("```"):
            fence = not fence
        elif not fence and re.match(r"#{2,3} ", ln):
            ends.append(pos)
        pos += len(ln) + 1
    for m in heads:
        end = min([e for e in ends if e > m.start()] + [len(text)])
        body = BODY.match(text[m.end():end])
        rid = "%s-%s" % (m.group(1), m.group(2))
        if not body:
            bad.append("%s: its body is not Old text / New text / Basis" % rid)
            continue
        rows.append((rid, m.group(1), int(m.group(2)), m.group(3), bool(m.group(4)), int(m.group(5)), body.group(1), body.group(2),
                     " ".join(body.group(3).split())))
    return rows if not bad else bad


def _tokens(s):
    return TOK.findall(s)


def p_rows(text):
    rows = _rows(text)
    if rows and isinstance(rows[0], str):
        return rows
    bad = []
    seen = {}
    for rid, pre, num, page, after, line, old, new, basis in rows:
        seen.setdefault(pre, []).append(num)
        if page != PAGES[pre]:
            bad.append("%s names %s, not its prefix's page %s" % (rid, page, PAGES[pre]))
        if not old or "\n" in old:
            bad.append("%s: the old text is not one line" % rid)
        if "__" in old:
            bad.append("%s: the old text carries a token" % rid)
        if new == old:
            bad.append("%s: the new text equals the old text" % rid)
        if after and not new.startswith(old + "\n"):
            bad.append("%s: an 'after line' row whose new text does not begin with the whole old text" % rid)
        for t in _tokens(new):
            if t not in ALLOWED:
                bad.append("%s: the token %s is not one of the rows' tokens %s" % (rid, T(t), ALLOWED))
        for p in re.findall(r"`(v2/[^`\s]+)`", basis):
            if not os.path.exists(os.path.join(REPO, p.rstrip("/"))) and p.split("/")[3:4] != ["int31"]:
                bad.append("%s: its basis names %s, absent from the tree" % (rid, p))
        if not basis:
            bad.append("%s: no basis" % rid)
    for pre, n in COUNTS.items():
        if seen.get(pre) != list(range(1, n + 1)):
            bad.append("the %s rows are %s, not 01 to %02d in order" % (pre, seen.get(pre), n))
    return bad


def p_hygiene(text):
    bad = []
    if any(d in text for d in DASHES):
        bad.append("the patch file carries an em or en dash")
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text) if p.strip()]
    first = paras[1] if len(paras) > 1 else ""
    if not first.startswith("**DONE:**") or "**NOT DONE:**" not in first or "**NEXT:**" not in first:
        bad.append("the paragraph after the title is not the DONE / NOT DONE / NEXT line")
    return bad


# ---- the pages ----

def _stage_pages():
    """("A", pages) on the tree's own pages at set 31; ("S", pages) once the rows are applied; ("P", pages) at AT with FILL31."""
    head = _read(PAGES["S"]).split("\n")[2]
    if head.startswith("**Current revision: set 31 "):
        return "A", {k: _read(p) for k, p in PAGES.items()}
    if head.startswith("**Current revision: set 32"):
        return "S", {k: _read(p) for k, p in PAGES.items()}
    if not _has(AT):
        raise Skip("the tree's pages are not set 31's adoption and fnd/adopt31's %s is not in this repository" % AT[:8])
    out = {}
    for k, p in PAGES.items():
        t = _show(AT, p)
        for name in ("CANDIDATE", "PROMOTED"):
            t = t.replace(T(name), S31_CAND)
        out[k] = t
    return "P", out


def p_pages(rows, pages):
    """Every old text exactly once on its line; the rows of a page applied bottom-up (rows on one line in the given order)."""
    bad = []
    work = {k: v.split("\n") for k, v in pages.items()}
    order = sorted(range(len(rows)), key=lambda i: (rows[i][1], -rows[i][5], i))
    for i in order:
        rid, pre, _n, _page, after, line, old, new, _b = rows[i]
        ls = work[pre]
        if line < 1 or line > len(ls):
            bad.append("%s: line %d is outside the page (%d lines)" % (rid, line, len(ls)))
            continue
        if ls[line - 1].count(old) != 1:
            bad.append("%s: the old text is %d times on line %d, not once: %r" % (rid, ls[line - 1].count(old), line, old[:60]))
            continue
        ls[line - 1] = ls[line - 1].replace(old, new, 1)
    for k, p in pages.items():     # untouched pages read the same; every token left is one the stage leaves
        for t in _tokens(p):
            if t not in ("ADOPTION", "GATE"):
                bad.append("%s's page carries %s on the revision read" % (k, T(t)))
    return bad


def _loose(new):
    """The new text as a pattern: each token stands for itself or a value the fill wrote (a commit, or a GATE's text)."""
    parts = re.split(r"(__(?:CANDIDATE|ADOPTION|GATE)__)", new)
    pat = ""
    for x in parts:
        if x == T("GATE"):
            pat += r"(?:%s|[^`\n]+?)" % re.escape(x)
        elif x in (T("CANDIDATE"), T("ADOPTION")):
            pat += r"(?:%s|[0-9a-f]{8,40})" % re.escape(x)
        else:
            pat += re.escape(x)
    return pat


def p_applied(rows, pages):
    """Stage S: every row's new text stands on its page (rows S-07 and S-08 and U-05 and U-06 each their own part)."""
    bad = []
    for rid, pre, *_r in rows:
        new = _r[-2]
        if not re.search(_loose(new), pages[pre]):
            bad.append("%s: its new text is not on %s" % (rid, PAGES[pre]))
    return bad


def p_placement(rows, pages):
    """The set 32 head paragraph after set 31's; each layer block directly under its heading above the set 31 block; the plan's entry
    after set 31's milestone, at the page's end."""
    bad = []
    by = {r[0]: r for r in rows}
    lines = {k: v.split("\n") for k, v in pages.items()}
    l1 = by.get("L-01")
    if not l1 or not lines["L"][l1[5] - 1].startswith("**After set 31 (") or not l1[7].split("\n", 2)[-1].startswith("**After set 32 ("):
        bad.append("L-01 is not set 32's head paragraph placed after set 31's")
    heads = [r for r in rows if r[1] == "L" and r[0] != "L-01"]
    if sorted(h[6].split(". ")[0] + ". " for h in heads) != sorted(LAYERS):
        bad.append("the layer rows are %s, not Layers 4, 5, 8, 9 and 12" % [h[6] for h in heads])
    for h in heads:
        ls, i = lines["L"], h[5]
        nxt = next((x for x in ls[i:] if x.strip()), "")
        if not ls[i - 1].startswith("## Layer ") or not nxt.startswith("**After set 31 ("):
            bad.append("%s: line %d is not a layer heading followed by its set 31 block" % (h[0], i))
        if not h[7].startswith(h[6] + "\n\n**After set 32: IN_PROGRESS"):
            bad.append("%s: the set 32 block is not directly under the heading" % h[0])
    p1 = by.get("P-01")
    if p1:
        ls = lines["P"]
        prev = [x for x in ls[:p1[5]] if x.startswith("### ")]
        if not prev or not prev[-1].startswith("### Milestone, 6 October 2026: integration set 31 promoted") \
                or any(x.strip() for x in ls[p1[5]:]):
            bad.append("P-01 is not after set 31's milestone at the plan's end")
        if "\n### Milestone: integration set 32 promoted" not in p1[7]:
            bad.append("P-01 is not set 32's milestone")
    return bad


# ---- what the new texts quote and count ----

def p_citations(rows):
    bad = []
    for rid, *_r in rows:
        for sha, path, n, q in GIT_ANCHOR.findall(_r[-2]):
            if not _has(sha):
                raise Skip("%s cites %s, which is not in this repository" % (rid, sha))
            ls = _show(sha, path).split("\n")
            n = int(n)
            if n > len(ls) or " ".join(q.replace("\\`", "`").split()) not in " ".join(ls[n - 1].split()):
                bad.append("%s: %r is not on %s:%s:%d" % (rid, q[:50], sha[:8], path, n))
    return bad


def _section(text, sec):
    ls = text.split("\n")
    lvl = "##" if sec.isdigit() else "###"
    start = next((i for i, x in enumerate(ls) if x.startswith("%s %s. " % (lvl, sec))), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(ls)) if ls[i].startswith("## ") or (lvl == "###" and ls[i].startswith("### "))), len(ls))
    return " ".join(" ".join(ls[start:end]).split())


def _file(path):
    """A quoted file: the tree's, else (int31's records before set 31's adoption is merged) fnd/adopt31's at AT."""
    path = ("v2/docs/" + path) if path.startswith("records/") else path
    if os.path.isfile(os.path.join(REPO, path)):
        return _read(path)
    if _has(AT):
        return _show(AT, path)
    raise Skip("%s is not in the tree and %s is absent" % (path, AT[:8]))


def p_quotes(rows):
    """A quote with its file and section ("..." (`path`, section N), or (`path`, section N: "...")) is in that section of that file."""
    bad = []
    for rid, *_r in rows:
        new = " ".join(_r[-2].split())
        found = [(q, p, s) for qs, p, s in QUOTE_SEC[0].findall(new) for q in re.findall(r"\"([^\"]+)\"", qs)]
        found += [(q, p, s) for p, s, q in QUOTE_SEC[1].findall(new)]
        for q, p, s in found:
            sec = _section(_file(p), s)
            if sec is None or " ".join(q.split()) not in sec:
                bad.append("%s: %r is not in %s, section %s" % (rid, q[:50], p, s))
    return bad


def _class_counts():
    t = _show(REC_AT, CLASS)
    tot = re.search(r"^\| total \| (\d+) \|", t, re.M)
    ric = re.search(r"^\| `REVIEWED-INPUT CHANGED` \| (\d+) \|", t, re.M)
    touch = re.search(r"The rows that touch a file cx46 read: (\d+), all UNREVIEWED since cx46\.", t)
    return int(tot.group(1)), int(ric.group(1)), int(touch.group(1))


TYPED = (re.compile(r"of the (\d+) commits of its five branches, (\d+) touch a file cx46 read, (\d+) of them REVIEWED-INPUT CHANGED"),
         re.compile(r"counts (\d+) REVIEWED-INPUT CHANGED commits among the (\d+) of its five branches and\s+(\d+) that touch a file cx46 read"),
         re.compile(r"classes the (\d+)\s+commits of its five branches, `[^`]+` `(\d+) of the \d+ touch a file cx46 read`, (\d+) of\s+them REVIEWED-INPUT CHANGED"))


def p_counts(text, pages):
    """The counts the rows type: the classification's at REC_AT (34 rows, 2 REVIEWED-INPUT CHANGED, 12 touching), set 31's 25 and set
    30's 14 as the pages read them, and the 26 converted generators as set 32's record states them."""
    if not _has(REC_AT):
        raise Skip("%s is not in this repository" % REC_AT[:8])
    tot, ric, touch = _class_counts()
    bad, n = [], 0
    for m in TYPED[0].finditer(text):
        n += 1
        if tuple(int(x) for x in m.groups()) != (tot, touch, ric):
            bad.append("typed %s, the classification's (total, touching, RIC) %s" % (m.groups(), (tot, touch, ric)))
    for m in TYPED[1].finditer(text):
        n += 1
        if tuple(int(x) for x in m.groups()) != (ric, tot, touch):
            bad.append("typed %s, the classification's (RIC, total, touching) %s" % (m.groups(), (ric, tot, touch)))
    for m in TYPED[2].finditer(text):
        n += 1
        if tuple(int(x) for x in m.groups()) != (tot, touch, ric):
            bad.append("typed %s, the classification's (total, touching, RIC) %s" % (m.groups(), (tot, touch, ric)))
    if n != 4:
        bad.append("the classification's counts are typed %d times, not 4 (S-10, U-09, L-02, P-01)" % n)
    if "beside set 31's 25 and set 30's 14" in text and not ("counts 25 commits that change what cx46 read" in pages["S"]
                                                              and "(14 over the 45 commits of" in pages["S"]):
        bad.append("set 31's 25 or set 30's 14 is not the page's")
    if text.count("26 record generators") < 3 or "so 26 record generators read each maker's PDF text" not in _show(REC_AT, RESULT):
        bad.append("the 26 converted generators are not set 32's record's")
    return bad


# ---- the fill ----

def _role(result, words):
    ls = [x for x in result.split("\n") if x.startswith(words)]
    if len(ls) != 1:
        return None
    m = re.match(r"`([^`]+)`$", re.split(r"(?<!\\)\|", ls[0].strip())[2].strip())
    return m.group(1) if m else None


def _fill_stage(result):
    cand = _role(result, "| INTEGRATED = CANDIDATE: the candidate commit |")
    adopt = _role(result, "| ADOPTED: the commit that adopts this record |")
    if cand is None or adopt is None:
        return None, cand, adopt
    st = {(True, True): 0, (False, True): 1, (False, False): 2}.get((cand.startswith("__"), adopt.startswith("__")))
    return st, cand, adopt


def _template():
    """The patch file at the newest commit touching it that still holds the CANDIDATE token (the template the fill filled)."""
    if "tmpl" not in _C:
        _C["tmpl"] = None
        for c in _git("log", "--format=%H", "--", PATCH).split():
            t = _show(c, PATCH)
            if "`%s`" % T("CANDIDATE") in t:
                _C["tmpl"] = t
                break
    return _C["tmpl"]


def p_fill(text, result):
    """Stage 0: the three tokens present and no other; stage 1: the ADOPTION token alone; stage 2: none; after the fill, each line is
    the template's with CANDIDATE the role's commit, ADOPTION the role's commit (stage 2) and GATE some text."""
    st, cand, adopt = _fill_stage(result)
    if st is None:
        return ["RESULT's section 1 role rows are neither all tokens, nor all but ADOPTION filled, nor all filled"]
    bad = []
    left = sorted(set(_tokens(text)))
    want = {0: list(ALLOWED), 1: ["ADOPTION"], 2: []}[st]
    if left != sorted(want):
        bad.append("fill stage %d leaves %s in the patch file, not %s" % (st, left, sorted(want)))
    if st == 0:
        return bad
    tmpl = _template()
    if tmpl is None:
        return bad + ["after the fill, no committed revision of the patch file holds the template"]
    a, b = tmpl.split("\n"), text.split("\n")
    if len(a) != len(b):
        return bad + ["the filled patch file has %d lines, its template %d" % (len(b), len(a))]
    for i, (x, y) in enumerate(zip(a, b), 1):
        if x == y:
            continue
        pat = ""
        for part in re.split(r"(__(?:CANDIDATE|ADOPTION|GATE)__)", x):
            if part == T("CANDIDATE"):
                pat += re.escape(cand)
            elif part == T("ADOPTION"):
                pat += re.escape(adopt if st == 2 else part)
            elif part == T("GATE"):
                pat += r".+?"
            else:
                pat += re.escape(part)
        if not re.fullmatch(pat, y):
            bad.append("line %d is not its template line with the stage's values: %r" % (i, y[:80]))
    return bad


def p_named(result, klass):
    """The record names the patch file the way the fill tool finds it (`int32/<name>.patch.md` in RESULT or CLASSIFICATION)."""
    names = set(re.findall(r"int32/([A-Za-z0-9_.-]+\.patch\.md)", result + "\n" + klass))
    return [] if "ENTRY-PAGES.patch.md" in names else ["neither RESULT.md nor CLASSIFICATION.md names int32/ENTRY-PAGES.patch.md"]


# ---- tests ----

def _mut(text, old, new):
    assert old in text, "the mutation's anchor %r is not in the text" % old[:50]
    return text.replace(old, new, 1)


def _pt():
    return _read(PATCH)


def t_the_patch_file_carries_no_dash_and_opens_with_its_state_line():
    t = _pt()
    assert not p_hygiene(t), p_hygiene(t)
    assert p_hygiene(_mut(t, "Record text only:", "Record text only —")), "an em dash passed"
    assert p_hygiene(_mut(t, "**NOT DONE:**", "**NOT YET:**")), "a state line without NOT DONE passed"


def t_every_row_is_well_formed_with_its_tokens_and_basis():
    t = _pt()
    assert not p_rows(t), p_rows(t)
    s07 = [r for r in _rows(t) if r[0] == "S-07"][0]
    assert p_rows(_mut(t, "### S-03. ", "### S-04. ")), "a row id out of sequence passed"
    assert p_rows(_mut(t, "### U-02. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`", "### U-02. `v2/docs/handover/START-HERE.md`")), \
        "a row naming another prefix's page passed"
    assert p_rows(_mut(t, "set 32's paragraph in the edition history\n\nOld text:\n```text\n(`v2",
                       "set 32's paragraph in the edition history\n\nOld text:\n```text\n(`%s` `v2" % T("GATE"))), "an old text with a token passed"
    assert p_rows(_mut(t, s07[7], s07[7].replace(T("ADOPTION"), T("PROMOTED"), 1))), "a PROMOTED token passed"
    assert p_rows(_mut(t, "netlist changed.\n\n**Set 32** (the revision", "netlist changed!\n\n**Set 32** (the revision")), \
        "an after-line row not beginning with its old text passed"
    assert p_rows(_mut(t, "Basis: the Tested row (S-06).", "Basis: `v2/docs/records/int32/NOWHERE.md`.")), "a basis naming no file passed"


def t_every_old_text_holds_once_on_its_line_of_the_pages_read():
    """The revision read: set 31's adoption in the tree, else fnd/adopt31's AT with set 31's fill values in memory; or, once the rows
    are applied, every new text on its page."""
    t = _pt()
    rows = _rows(t)
    stage, pages = _stage_pages()
    if stage == "S":
        assert not p_applied(rows, pages), p_applied(rows, pages)
        return
    assert not p_pages(rows, pages), p_pages(rows, pages)
    assert p_pages([x if x[0] != "S-06" else x[:6] + (x[6].replace("set 31's", "set 30's", 1),) + x[7:] for x in rows], pages), \
        "an old text not on its line passed"
    assert p_pages([x if x[0] != "U-13" else x[:5] + (x[5] + 1,) + x[6:] for x in rows], pages), "a row on the wrong line passed"
    assert p_pages([x if x[0] != "S-08" else x[:5] + (x[5], "` | set 31's adoption commit") + x[7:] for x in rows] +
                   [x for x in rows if x[0] == "S-08"], pages), "a second row whose old text the first consumed passed"


def t_the_set_32_blocks_are_placed_newest_first_and_the_plan_entry_last():
    t = _pt()
    rows = _rows(t)
    stage, pages = _stage_pages()
    if stage == "S":
        raise Skip("the rows are applied; their placement was read before (the stage the page's line 3 gives)")
    assert not p_placement(rows, pages), p_placement(rows, pages)
    assert p_placement(_rows(_mut(t, "\n\n**After set 32: IN_PROGRESS.** Set 32 carries Q-55",
                                  "\n\n**After set 31 (6 October 2026): IN_PROGRESS.** Set 32 carries Q-55")), pages), \
        "a set 32 block not headed After set 32 passed"
    assert p_placement(_rows(_mut(t, "after line 352: Layer 4's", "after line 354: Layer 4's").replace(
        "line 352", "line 354", 1)), pages), "a block placed under the set 31 block passed"


def t_every_citation_is_on_its_cited_line():
    t = _pt()
    rows = _rows(t)
    assert not p_citations(rows), p_citations(rows)
    assert p_citations(_rows(_mut(t, "`34 commits of the five branches over their bases`", "`35 commits of the five branches over their bases`"))), \
        "a changed quote passed"
    assert p_citations(_rows(_mut(t, "RESULT.md:385` `**Set 32 closes NO power item.**`", "RESULT.md:386` `**Set 32 closes NO power item.**`"))), \
        "a quote on the wrong line passed"


def t_every_quote_with_its_section_is_in_that_section():
    t = _pt()
    rows = _rows(t)
    assert not p_quotes(rows), p_quotes(rows)
    assert p_quotes(_rows(_mut(t, "\"Set 32 closes NO power item.\" (`v2/docs/records/int32/RESULT.md`,",
                               "\"Set 32 closes no power item.\" (`v2/docs/records/int32/RESULT.md`,"))), "a changed quote passed"
    assert p_quotes(_rows(_mut(t, "\"Layer 4's DESK gate: NOT PASSED\"; \"Engineering-handover\nreadiness",
                               "\"Layer 4's DESK gate: PASSED\"; \"Engineering-handover\nreadiness"))), "a changed claim passed"
    assert p_quotes(_rows(_mut(t, "section 1: \"no independent check of its engineering\") |",
                               "section 2: \"no independent check of its engineering\") |"))), "a quote in the wrong section passed"


def t_every_count_typed_is_the_classifications_and_the_pages():
    t = _pt()
    _stage, pages = _stage_pages()
    assert not p_counts(t, pages), p_counts(t, pages)
    assert p_counts(_mut(t, "of the 34 commits of its five branches, 12", "of the 35 commits of its five branches, 12"), pages), \
        "a wrong total passed"
    assert p_counts(_mut(t, "counts 2 REVIEWED-INPUT CHANGED commits", "counts 3 REVIEWED-INPUT CHANGED commits"), pages), "a wrong RIC count passed"
    assert p_counts(_mut(t, "of the 34 commits of its five branches, 12", "of the 34 commits of its branches, 12"), pages), \
        "a count dropped from the pattern passed"


def t_the_tokens_are_the_rows_and_the_fill_stage_is_resultss():
    t = _pt()
    result = _read(RESULT)
    assert not p_fill(t, result), p_fill(t, result)
    st = _fill_stage(result)[0]
    if st == 0:
        assert p_fill(t.replace(T("GATE"), "a log line"), result), "a GATE token removed before the fill passed"
        assert p_fill(_mut(t, "the gate lines |", "the gate lines `%s` |" % T("REKEY")), result), "a REKEY token passed"
    else:
        assert p_fill(_mut(t, "set 32, the revision `", "set 32, the revision `0"), result), "a wrong filled value passed"


def t_the_record_names_the_patch_file_so_the_fill_reaches_it():
    result, klass = _read(RESULT), _read(CLASS)
    assert not p_named(result, klass), p_named(result, klass)
    assert p_named(result.replace("int32/ENTRY-PAGES.patch.md", "int32/ENTRY-PAGES.md"), klass), "an unnamed patch file passed"


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


test_the_patch_file_carries_no_dash_and_opens_with_its_state_line = _pytest(t_the_patch_file_carries_no_dash_and_opens_with_its_state_line)
test_every_row_is_well_formed_with_its_tokens_and_basis = _pytest(t_every_row_is_well_formed_with_its_tokens_and_basis)
test_every_old_text_holds_once_on_its_line_of_the_pages_read = _pytest(t_every_old_text_holds_once_on_its_line_of_the_pages_read)
test_the_set_32_blocks_are_placed_newest_first_and_the_plan_entry_last = _pytest(
    t_the_set_32_blocks_are_placed_newest_first_and_the_plan_entry_last)
test_every_citation_is_on_its_cited_line = _pytest(t_every_citation_is_on_its_cited_line)
test_every_quote_with_its_section_is_in_that_section = _pytest(t_every_quote_with_its_section_is_in_that_section)
test_every_count_typed_is_the_classifications_and_the_pages = _pytest(t_every_count_typed_is_the_classifications_and_the_pages)
test_the_tokens_are_the_rows_and_the_fill_stage_is_resultss = _pytest(t_the_tokens_are_the_rows_and_the_fill_stage_is_resultss)
test_the_record_names_the_patch_file_so_the_fill_reaches_it = _pytest(t_the_record_names_the_patch_file_so_the_fill_reaches_it)
