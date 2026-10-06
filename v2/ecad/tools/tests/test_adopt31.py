"""Set 31's adoption pages, prepared before its promotion (MESHSAT-1357, worker W65 resuming W58's queue item Q-77, branch
fnd/adopt31, 6 October 2026), held as predicates on their text: the two entry pages v2/docs/handover/START-HERE.md and
v2/docs/handover/supplier/SUPPLIER-HANDOVER.md, the blocks headed "After set 31" of v2/docs/handover/LAYER-STATUS.md and set 31's
entry in v2/docs/EXECUTION-PLAN.md.

What the pages are: the two entry pages are main's copies at eff28be3 (v2/docs/records/int31/inputs/, held by test_res31) with
every row of v2/docs/records/int31/ENTRY-PAGES.patch.md applied (W39's rows S-01 to S-11 and U-01 to U-13) and the EXTRA rows
below, nothing else. The layer-status page gains a head paragraph and one block for each of Layers 4, 5, 8, 9 and 12, directly
under the layer's heading; the plan gains one milestone entry at its end. Set 31's candidate and adoption commits do not exist
yet, so the pages carry the coordinator's tokens: __CANDIDATE__ (the tested revision: the candidate commit, which main is
fast-forwarded to), __ADOPTION__ (the adoption commit) and __GATE__ (a gate's log line), the names W63's
`_runs/int31/freeze/fill_res31.py` fills (the coordinator's ruling, authority SESSION, in its brief to W65; W39's rows used
__PROMOTED__ for the tested revision and were renamed, test_res31's PATCH_TOKENS with them).

The predicates: every row and extra is applied on the entry page it names, located by its TEXT, not by a line number (W103,
7 October 2026, below): its new text reads exactly once on that page, every token literal or filled with one commit throughout
both pages; its old text survives neither on the line or lines that hold the new text nor anywhere on the page beyond what the
copy with every row applied keeps; and the rows of a page stand in their copy's order; each row and extra reads once on its copy's
line and its new text differs; each page carries only its
declared tokens and none carries __PROMOTED__ or __REKEY__; fill_res31.py (where the run folder exists) knows the tokens;
the set 31 blocks sit first under their headings, one per layer named and none elsewhere, the head paragraph between W21's
paragraph and the reading guide; every dated citation of set 31's text resolves at its commit (the lineage 31928583 or fnd/res31's
5f910eb5, both in this branch's history) and its quote is on the cited lines; the three claims and the DESK gate are the
assessment's lines verbatim at the lineage and in the tree; the counts typed (103 commits to the lineage, 104 to the cache commit, 106
classified to the second candidate, 25 REVIEWED-INPUT CHANGED; W83) are the classification's and git's; the eight next-set branches are in the lineage and the cache commit follows it; the plan's entry is
one, last, and states the three claims and the gate apart; set 31's text carries no em or en dash, no acceptance word outside a
quotation and no percentage. Fixtures show that each checker refuses the defect it is for. These are software predicates on
record text: they establish no electrical or thermal property and accept, close or promote nothing.

Restated by W103 (7 October 2026; basis: W99's note N1, `_runs/claude/w99readpatch32/REPORT-FULL-AS-RECEIVED.md`): the entry
pages were compared WHOLE with their copies, so set 32's own branches, which edit the supplier page (fnd/w34pdftext adds seven lines
to its section 7; the chain's step a5 rewrites one line of section 0e), failed this module on the integrated tree before any set 32
row ("line 931 reads ..." before a5, "line 761 ..." after it), although every set 31 row stood applied. The row check now locates
each row by its text, the copy's line kept only as a hint in the message; a row whose new text is missing, doubled or on the other
page, a row whose old text survives, a token filled with two values and two rows out of their copy's order still fail (fixtures in
t_the_checkers_refuse_their_defects). What it no longer judges, taken under the owner's standing rule of 26 September 2026
(authority SESSION, W103): an edit outside every row of the two pages, which a later set makes by its own rows and holds by its own
tests (test_patch32 for set 32); reversed by restoring the whole-page comparison (`page_errors`, kept below) in
t_the_entry_pages_are_the_copies_with_every_row_applied.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_adopt31.`) and under pytest (each t_ function has a
test_ alias). Without git or a cited commit, the predicates that read it skip with their reason."""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

START = "v2/docs/handover/START-HERE.md"
SUPPLIER = "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md"
LS = "v2/docs/handover/LAYER-STATUS.md"
PLAN = "v2/docs/EXECUTION-PLAN.md"
REC = "v2/docs/records/int31"
PATCH = REC + "/ENTRY-PAGES.patch.md"
CLASS = REC + "/CLASSIFICATION.md"
RESULT = REC + "/RESULT.md"
ASSESS = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
COPIES = {START: REC + "/inputs/START-HERE-eff28be3.md", SUPPLIER: REC + "/inputs/SUPPLIER-HANDOVER-eff28be3.md"}
BASE = "dd1aed00d0a0a521063b5792550bc510c4707c59"          # set 30's promoted revision, set 31's base
LINEAGE = "31928583c612ea43df17df5d7e0cbb2f66090f8e"       # W41's converged commit, the lineage the record reads
RES31 = "5f910eb5"                                          # fnd/res31 at W56's commit, merged into this branch at 1e8fa025
CACHE = "aa3322806da156d12f2b23dbe9fc98a8805926f0"         # record l4e7's results cache re-keyed on the lineage (rekey10)
FIRST = "d0e283aa52ceb7f303358862b539161b721475e5"         # set 31's first candidate: the re-key's dependents (its gate FAILED)
CAND = "5f25daf3762ecd69c8764bf60de81a80f4119eab"          # set 31's second candidate: the coordinator's test correction (W83)
NEXT_SET = ("786aed2f", "cd19df59", "910f08ef", "85b6f258", "56ab0d01", "57bcdbfc", "150e908b", "686de0a2")
# the coordinator's tokens per file (W63's fill_res31.py names them so)
TOKENS = {START: {"__CANDIDATE__", "__ADOPTION__"}, SUPPLIER: {"__CANDIDATE__", "__ADOPTION__"},
          LS: {"__CANDIDATE__", "__GATE__"}, PLAN: {"__CANDIDATE__", "__GATE__"}, PATCH: {"__CANDIDATE__", "__ADOPTION__"}}
HEXTOK = ("__CANDIDATE__", "__ADOPTION__")                  # filled with a commit, one value per token across both entry pages
# Edits beside W39's rows (W65, 6 October 2026): (page, line at the copy, old text, new text, basis). An insertion is never used.
EXTRA = (
    (SUPPLIER, 133, "### 0e. How to reproduce set 30's figures", "### 0e. How to reproduce set 31's figures",
     "W52's finding P1: section 0e names the revision it applies to (its checkout line is U-10's); W42's 0e script matches the "
     "prefix \"### 0e. How to reproduce\""),
    (START, 177, "revision is set 30.", "revision is set 31 (section 0 states set 30's revision and what set 31 changes).",
     "W58's read: a stale sentence the rows miss"),
    (SUPPLIER, 42, "first as adopted in the adoption commit `836f711b` (the Adopted row)",
     "first as adopted in set 30's adoption commit `836f711b` (the Adopted row's dated history) and, for set 31's records, in "
     "set 31's adoption commit (the Adopted row)", "W58's read: a stale sentence the rows miss (U-05 moves 836f711b to dated history)"),
    (START, 187, "**since set 30** the blocks headed \"After set 30\" before them)",
     "**since set 30** the blocks headed \"After set 30\" before them, and **since set 31** the blocks headed \"After set 31\" "
     "before those)", "the reading guide names the layer-status page's set 31 blocks, which this branch adds"),
    # W69, 6 October 2026, from W68's finding F2: section 0 was written for set 30; once set 31's paragraph and revision rows are in
    # it, its heading and the sentences naming the tested and the promoted revision say whose they are (set 30's), so that no
    # sentence calls set 30 the current revision
    (START, 91, "## 0. Set 30 (6 October 2026): what this revision hands over",
     "## 0. Set 30's revision (6 October 2026): what it hands over, and set 31 over it", "W68's F2: the heading named set 30 as this revision"),
    (START, 97, "line N at the tested revision `dd1aed00`", "line N at set 30's tested revision `dd1aed00`", "W68's F2"),
    (START, 99, "is the promoted commit (main was", "is set 30's promoted commit (main was", "W68's F2"),
    (START, 116, "What the promoted revision is, and is not,", "What set 30's promoted revision is, and is not,", "W68's F2"),
    (START, 132, "which records the coordinator's judgement on the", "which records the coordinator's judgement on set 30's", "W68's F2"),
    (SUPPLIER, 27, "line N at the tested revision `dd1aed00`", "line N at set 30's tested revision `dd1aed00`", "W68's F2"),
    (SUPPLIER, 28, "`dd1aed00d0a0a521063b5792550bc510c4707c59` is the", "`dd1aed00d0a0a521063b5792550bc510c4707c59` is set 30's", "W68's F2"),
    (SUPPLIER, 50, "**What the promoted revision is, and is not**", "**What set 30's promoted revision is, and is not**", "W68's F2"),
    (SUPPLIER, 68, "which records the coordinator's judgement on the", "which records the coordinator's judgement on set 30's", "W68's F2"),
)
L31 = {"4": "## Layer 4. System architecture\n", "5": "## Layer 5. Partitioning and interfaces\n", "8": "## Layer 8. Schematics\n",
       "9": "## Layer 9. Pre-layout design analysis\n",
       "12": "## Layer 12. Firmware, bring-up, test plans and build documentation\n"}
NOT31 = ("## Layer 1.", "## Layer 2.", "## Layer 3.", "## Layer 6.", "## Layer 7.")
HEAD31 = "**After set 31 (6 October 2026, an adoption of record text over set 30, MESHSAT-1357).**"
W21HEAD = "**After set 30, at the integration's tip (dated 6 October 2026, folded by W21"
GUIDE = "**How to read this page after H2.**"
BLOCK31 = "**After set 31 (6 October 2026): IN_PROGRESS"
PLANHEAD = "### Milestone, 6 October 2026: integration set 31 promoted as a DESK candidate (main `%s`)"
# the assessment's lines (set 31 changes no line of it): the DESK gate and the three completion claims
CLAIMS = {492: "### Layer 4's DESK gate: NOT PASSED",
          496: "### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
          498: "\"Ready\" here means complete and internally consistent as a package of open items, not that any item is resolved.",
          500: "### Power-design closure: BLOCKED. Fabrication release: BLOCKED."}
DCITE = re.compile(r"`([0-9a-f]{7,40}):([^`\s:]+):(\d+(?:-\d+)?)`(?:\s+`([^`]+)`)?")
PH = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
_C = {}


def _norm(t):
    return " ".join(t.split())


def _read(p):
    if p not in _C:
        _C[p] = open(need(os.path.join(ROOT, p), p), encoding="utf-8").read()
    return _C[p]


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git on this host (%s)" % e)
    return r


def _show(sha, path):
    k = ("show", sha, path)
    if k not in _C:
        if _git("cat-file", "-e", sha + "^{commit}").returncode != 0:
            raise Skip("commit %s is not in this object store" % sha)
        r = _git("show", "%s:%s" % (sha, path))
        _C[k] = r.stdout.decode("utf-8") if r.returncode == 0 else None
    return _C[k]


# ------------------------------------------------------------------------------------------------- the rows and the pages
def patch_rows(text):
    """W39's rows: (id, page, line, old, new); the parse test_res31 uses."""
    rows = []
    for blk in re.split(r"\n### ", text)[1:]:
        m = re.match(r"([SU]-\d\d)\. `([^`]+)`, (?:after )?line (\d+):", blk.split("\n", 1)[0])
        olds = re.findall(r"Old text:\n```text\n(.*?)\n```", blk, re.S)
        news = re.findall(r"New text:\n```text\n(.*?)\n```", blk, re.S)
        if m and len(olds) == 1 and len(news) == 1:
            rows.append((m.group(1), m.group(2), int(m.group(3)), olds[0], news[0]))
    return rows


def all_rows(patch_text):
    return [r[1:] for r in patch_rows(patch_text)] + [x[:4] for x in EXTRA]


def apply_rows(copy_text, page, rows):
    """The copy with every row of this page applied on its line; refuses an old text not once on its line or a new text that does
    not differ."""
    lines = copy_text.split("\n")
    for p, n, old, new in rows:
        if p != page:
            continue
        assert 1 <= n <= len(lines) and lines[n - 1].count(old) == 1, "%s:%d does not read %r once" % (page, n, old[:50])
        assert new != old, "%s:%d: the new text does not differ" % (page, n)
        lines[n - 1] = lines[n - 1].replace(old, new, 1)
    return "\n".join(lines)


def expected(page):
    return apply_rows(_read(COPIES[page]), page, all_rows(_read(PATCH)))


def fill_pattern(text):
    """A regex for the text in which each token of HEXTOK reads literally or as one commit throughout."""
    out, seen, k = [], set(), 0
    for m in re.finditer("|".join(re.escape(t) for t in HEXTOK), text):
        out.append(re.escape(text[k:m.start()]))
        name = m.group(0).strip("_")
        out.append("(?P=%s)" % name if name in seen else "(?P<%s>%s|[0-9a-f]{8,40})" % (name, re.escape(m.group(0))))
        seen.add(name)
        k = m.end()
    out.append(re.escape(text[k:]))
    return "".join(out)


def page_errors(want, got):
    if re.fullmatch(fill_pattern(want), got, re.S):
        return []
    a, b = want.split("\n"), got.split("\n")
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y and not re.fullmatch(fill_pattern(x), y):
            return ["line %d reads %r, the rows give %r" % (i + 1, y[:70], x[:70])]
    return ["%d lines, the rows give %d (or a token filled with two values)" % (len(b), len(a))]


def row_errors(rows, pages, copies):
    """W103: every row located on its page by its TEXT. rows: (page, line at the copy, old, new); pages: {page: its text now};
    copies: {page: the copy the rows were written against}. A row's new text must read exactly once on the page the row names (each
    token of HEXTOK literal or one commit, the same throughout every page); the line or lines holding it must carry the old text no
    more often than the copy's line with the row applied; the page must carry the old text no more often than the copy with every
    row applied; and the rows of a page stand in their copy's order. The copy's line number is a hint in the messages only."""
    errs, vals, at = [], {}, {}
    want = {p: apply_rows(copies[p], p, rows) for p in copies}
    for p, n, old, new in rows:
        t = pages[p]
        ms = list(re.finditer(fill_pattern(new), t))
        hint = "%s, the row of the copy's line %d" % (p, n)
        if len(ms) != 1:
            errs.append("%s: its new text reads %d times on the page, not once: %r" % (hint, len(ms), new[:60]))
            continue
        m = ms[0]
        now = t.count("\n", 0, m.start()) + 1
        for k, v in m.groupdict().items():
            if v is not None:
                vals.setdefault(k, set()).add(v)
        at.setdefault(p, []).append((n, m.start(), now))
        a = t.rfind("\n", 0, m.start()) + 1
        b = t.find("\n", m.end())
        held = t[a:len(t) if b < 0 else b]
        line = copies[p].split("\n")[n - 1].replace(old, new, 1)
        if held.count(old) > line.count(old):
            errs.append("%s (now line %d): its old text survives on the line that holds the new text: %r" % (hint, now, old[:60]))
        if t.count(old) > want[p].count(old):
            errs.append("%s (new text now at line %d): its old text reads %d times on the page, the rows leave %d: %r"
                        % (hint, now, t.count(old), want[p].count(old), old[:60]))
    for p, xs in at.items():
        xs.sort()
        for (n1, s1, l1), (n2, s2, l2) in zip(xs, xs[1:]):
            if s2 <= s1:
                errs.append("%s: the row of the copy's line %d (now line %d) stands before the row of line %d (now line %d)"
                            % (p, n2, l2, n1, l1))
    for k, v in sorted(vals.items()):
        if len(v) > 1:
            errs.append("__%s__ reads as %d values across the pages: %s" % (k, len(v), sorted(v)))
    return errs


# ------------------------------------------------------------------------------------------------------ set 31's text
def _section(t, h):
    i = t.index(h)
    j = min(x for x in (t.find("\n---\n", i), t.find("\n## ", i + 1), len(t)) if x >= 0)
    return t[i:j]


def block31(t, n):
    """Layer n's set 31 block: from the line after its heading to the next set's block."""
    s = _section(t, L31[n])
    body = s[len(L31[n]) + 1:]
    ends = [x for x in (body.find("\n**After set 30 (6 October 2026"), body.find("\n**After set 29 (4 October 2026")) if x >= 0]
    return body[:min(ends) + 1] if ends else body


def placement_errors(t):
    errs = []
    if t.count(HEAD31) != 1:
        errs.append("the set 31 head paragraph is missing or doubled")
    elif not (t.index(W21HEAD) < t.index(HEAD31) < t.index(GUIDE)):
        errs.append("the set 31 head paragraph is not between W21's paragraph and the reading guide")
    if t.count(BLOCK31) != len(L31):
        errs.append("%d set 31 blocks, not %d" % (t.count(BLOCK31), len(L31)))
    for n, h in L31.items():
        s = _section(t, h)
        if not s.startswith(h + "\n" + BLOCK31):
            errs.append("layer %s: the set 31 block is not directly under the heading" % n)
            continue
        b = block31(t, n)
        if "**After set 30 (6 October 2026" in b or "**After set 29" in b or b.count(BLOCK31) != 1:
            errs.append("layer %s: the set 31 block runs into another set's block" % n)
        if n == "5" and "After set 30" in b:
            errs.append("layer 5's set 31 block names a set 30 block (test_lstat31: none in Layer 5)")
    for h in NOT31:
        if "After set 31" in _section(t, "\n" + h)[1:]:
            errs.append("%s carries a set 31 block" % h)
    return errs


def _plan_entry(t):
    hs = [m for m in re.finditer(r"^### Milestone, 6 October 2026: integration set 31 promoted as a DESK candidate \(main `([^`]+)`\)$",
                                 t, re.M)]
    assert len(hs) == 1, "set 31's plan entry is missing or doubled"
    return t[hs[0].start():]


def text31():
    """Every text set 31's adoption adds: the head paragraph, the five blocks, the plan entry and the entry pages' changed lines."""
    t = _read(LS)
    i = t.index(HEAD31)
    parts = [t[i:t.index("\n", i)]] + [block31(t, n) for n in L31] + [_plan_entry(_read(PLAN))]
    for p in COPIES:
        old = set(_read(COPIES[p]).split("\n"))
        parts.append("\n".join(x for x in _read(p).split("\n") if x not in old))
    return "\n\n".join(parts)


def citation_errors(s, show=None):
    show = show or _show
    bad, n = [], 0
    for m in DCITE.finditer(s):
        sha, path, spec, quote = m.groups()
        if not (LINEAGE.startswith(sha) or sha == RES31):
            bad.append("%s:%s is cited at a commit that is neither the lineage nor fnd/res31's" % (sha, path)); continue
        text = show(sha, path)
        if text is None:
            bad.append("%s:%s: no such file" % (sha, path)); continue
        ls = text.split("\n")
        a, _, b = spec.partition("-")
        a, b = int(a), int(b or a)
        n += 1
        if not 1 <= a <= b <= len(ls):
            bad.append("%s:%s:%s outside 1..%d" % (sha, path, spec, len(ls))); continue
        if quote is None:
            bad.append("%s:%s:%s quotes nothing" % (sha, path, spec))
        elif _norm(quote) not in _norm(" ".join(ls[a - 1:b])):
            bad.append("%s:%s:%s lacks %r" % (sha, path, spec, _norm(quote)[:60]))
    return bad, n


def word_errors(s):
    errs = []
    if any(d in s for d in DASHES):
        errs.append("a dash")
    flat = re.sub(r"`[^`]*`", " ", s)
    flat = re.sub(r"\"[^\"]*\"", " ", flat)
    for w in ("ACCEPTED", "ACCEPTS", "PASSES", "QUALIFIED:", "RELEASED", "COMPLETE:"):
        if w in flat:
            errs.append("set 31's text says %s" % w)
    if "CLOSED" in re.sub(r"NOT CLOSED", "", flat):
        errs.append("a CLOSED outside NOT CLOSED")
    if re.search(r"\d\s*(?:%|per ?cent)", flat):
        errs.append("a percentage")
    return errs


def token_errors(name, text):
    got = set(PH.findall(text))
    errs = ["%s carries %s, not one of its tokens %s" % (name, t, sorted(TOKENS[name])) for t in sorted(got - TOKENS[name])]
    for t in ("__PROMOTED__", "__REKEY__"):
        if t in text:
            errs.append("%s carries %s" % (name, t))
    return errs


# ---------------------------------------------------------------------------------------------------------------- tests
def t_each_row_and_extra_reads_once_on_its_copy_line_and_changes_it():
    rows = patch_rows(_read(PATCH))
    assert [r[0] for r in rows] == ["S-%02d" % i for i in range(1, 12)] + ["U-%02d" % i for i in range(1, 14)], [r[0] for r in rows]
    for p in COPIES:
        expected(p)   # apply_rows asserts each row
    keys = [(p, n) for p, n, _, _ in all_rows(_read(PATCH))]
    assert len(keys) == len(set(keys)), "two rows on one line of one page"
    for p, n, old, new, basis in EXTRA:
        assert basis and new != old and "\n" not in new, (p, n)


def t_the_entry_pages_are_the_copies_with_every_row_applied():
    # W103 (W99's N1): each row located by its text on the page it names, no longer the whole page against the copy (docstring)
    errs = row_errors(all_rows(_read(PATCH)), {p: _read(p) for p in COPIES}, {p: _read(COPIES[p]) for p in COPIES})
    assert not errs, errs


def t_the_pages_carry_only_their_declared_tokens():
    errs = []
    for name in (START, SUPPLIER, PATCH):
        errs += token_errors(name, _read(name))
    errs += token_errors(LS, "\n".join(block31(_read(LS), n) for n in L31))
    errs += token_errors(PLAN, _plan_entry(_read(PLAN)))
    assert not errs, errs
    t = _read(LS)
    outside = t
    for n in L31:
        outside = outside.replace(block31(t, n), "", 1)
    assert not PH.findall(outside), "a token outside set 31's blocks: %s" % PH.findall(outside)[:3]
    res = open(os.path.join(TOOLS, "tests", "test_res31.py"), encoding="utf-8").read()
    m = re.search(r"^PATCH_TOKENS = \(([^)]*)\)", res, re.M)
    assert m and set(re.findall(r"\"(__[A-Z]+__)\"", m.group(1))) == TOKENS[PATCH], "test_res31's PATCH_TOKENS differ"
    # W69 (W68's F9): the run folder is beside the worktrees, one level above this tree (it read two levels up, so never ran)
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(ROOT), "_runs")
    fill = os.path.join(runs, "int31", "freeze", "fill_res31.py")
    if os.path.isfile(fill):   # the coordinator's fill script, read where the run folder exists
        src = open(fill, encoding="utf-8").read()
        names = set(re.search(r"TOK = re\.compile\(r\"__\(([A-Z|]+)\)__\"\)", src).group(1).split("|"))
        assert {"CANDIDATE", "ADOPTION", "GATE"} <= names, "fill_res31.py does not fill %s" % names


def t_the_set_31_blocks_sit_first_under_their_headings():
    errs = placement_errors(_read(LS))
    assert not errs, errs


def t_every_dated_citation_resolves_and_its_quote_is_found():
    bad, n = citation_errors(text31())
    assert n >= 30, "set 31's text cites less than written: %d" % n
    assert not bad, bad[:6]


def t_the_claims_are_the_assessments_lines_verbatim():
    a = _show(LINEAGE, ASSESS).split("\n")
    tree = _read(ASSESS).split("\n")
    l4 = _norm(block31(_read(LS), "4"))
    for n, w in CLAIMS.items():
        assert w in a[n - 1] and w in tree[n - 1], "the assessment's line %d does not read %r" % (n, w)
        assert ("`%s:%s:%d` `%s`" % (LINEAGE[:8], ASSESS, n, _norm(w))) in l4, "Layer 4's set 31 block does not quote line %d" % n
    plan = _norm(_plan_entry(_read(PLAN)))
    for w in ("engineering-handover readiness READY AS A DESK PACKAGE OF OPEN ITEMS", "power-design closure BLOCKED",
              "fabrication release BLOCKED", "Layer 4's DESK gate NOT PASSED"):
        assert w in plan, "the plan entry lacks %r" % w
    for p in COPIES:   # the entry pages keep set 30's four claims in the coordinator's words (test_w30entry holds the block)
        for w in ("\"Layer 4's DESK gate: NOT PASSED\"", "\"Power-design closure: BLOCKED.\"", "\"Fabrication release: BLOCKED.\""):
            assert _read(p).count(w) == 1, "%s: %s" % (p, w)
    assert "Set 31 closes NO power item." in _read(RESULT) and "\"Set 31 closes NO power item.\"" in plan


def t_the_counts_are_the_classifications_and_gits():
    # restated by W69 (6 October 2026, from W68's finding F1; basis: the classification gained row 34, the re-key's cache commit
    # aa332280, classed DIGEST RE-PIN, so it counts 104 commits to the cache commit; the lineage's 103 to 31928583 stand as typed).
    # Restated by W83 (6 October 2026; basis: the classification gained rows 35, the first candidate d0e283aa, REVIEWED-INPUT CHANGED,
    # and 36, the coordinator's test correction 5f25daf3, TEST, so it counts 106 commits to the second candidate, 25 of them
    # REVIEWED-INPUT CHANGED; the 103 and the 104 stand as typed history, and W56's quoted "None of the 24" stays a dated quotation)
    c = _read(CLASS)
    assert "| `REVIEWED-INPUT CHANGED` | 25 | 25 |" in c and re.search(r"^\| total \| 106 \| \|$", c, re.M), "the classification's counts"
    k = _git("rev-list", "--count", "%s..%s" % (BASE, LINEAGE))
    kc = _git("rev-list", "--count", "%s..%s" % (BASE, CACHE))
    kn = _git("rev-list", "--count", "%s..%s" % (BASE, CAND))
    if k.returncode != 0 or kc.returncode != 0 or kn.returncode != 0:
        raise Skip("the lineage is not in this object store")
    assert k.stdout.decode().strip() == "103" and kc.stdout.decode().strip() == "104" and kn.stdout.decode().strip() == "106"
    assert _git("rev-parse", FIRST + "^1").stdout.decode().strip() == CACHE, "the first candidate does not follow the cache commit"
    assert _git("rev-parse", CAND + "^1").stdout.decode().strip() == FIRST, "the second candidate does not follow the first"
    l4 = _norm(block31(_read(LS), "4"))
    assert "None of the 24 REVIEWED-INPUT CHANGED commits" in l4 and "103 commits over the base" in l4
    assert "104 commits over the base" in l4 and "classes the 106 commits of `dd1aed00..5f25daf3`" in l4
    assert "106 commits over the base" in l4 and "(reading A): 25 REVIEWED-INPUT CHANGED" in l4 and "four-log gate FAILED" in l4
    plan = _norm(_plan_entry(_read(PLAN)))
    assert "counts 25 REVIEWED-INPUT CHANGED commits over `dd1aed00..5f25daf3`" in plan and "106 commits over the base" in plan
    assert "whose four-log gate FAILED" in plan
    for p in COPIES:
        t = _norm(_read(p))
        assert t.count("25 commits that change what cx46 read") == 2 and "over the 106 commits of `dd1aed00..5f25daf3`" in t, p
        assert "31928583" not in t, "%s names the lineage 31928583 where the classification reads to the candidate" % p


def t_the_merged_branches_the_cache_commit_and_the_contract():
    if _git("cat-file", "-e", LINEAGE + "^{commit}").returncode != 0:
        raise Skip("the lineage is not in this object store")
    for s in NEXT_SET:
        assert _git("merge-base", "--is-ancestor", s, LINEAGE).returncode == 0, "%s is not in the lineage" % s
    assert _git("rev-parse", CACHE + "^1").stdout.decode().strip() == LINEAGE, "the cache commit does not follow the lineage"
    assert _git("merge-base", "--is-ancestor", CACHE, "HEAD").returncode == 0, "the cache commit is not in this branch"
    hw = _show(LINEAGE, "v2/docs/HW-FW-CONTRACT.md")
    for x in ("FW-B20", "FW-B21", "FW-B22"):
        assert x not in hw, "%s is in HW-FW-CONTRACT.md at the lineage" % x


def t_the_plan_entry_is_one_and_last():
    t = _read(PLAN)
    e = _plan_entry(t)
    assert t.index("### Milestone, 6 October 2026 10:36:57 CEST: integration set 30 promoted") < t.index(e), "out of order"
    assert "\n### " not in e[4:], "a heading after set 31's entry"
    head = e.split("\n", 1)[0]
    assert re.fullmatch(re.escape(PLANHEAD % "\x00").replace("\x00", "(?:__CANDIDATE__|[0-9a-f]{8,40})"), head), head


def t_set_31s_text_carries_no_dash_no_acceptance_word_and_no_percentage():
    errs = word_errors(text31())
    assert not errs, errs
    m = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in m for d in DASHES), "a dash in this module"


# ----------------------------------------------------------------------------- the checkers refuse what they are for
def t_the_checkers_refuse_their_defects():
    # a page: a changed word, a token filled with two values, a filled token, a stray line
    want = "a `__CANDIDATE__` b\nc `__ADOPTION__` d `__CANDIDATE__`"
    assert not page_errors(want, want)
    assert not page_errors(want, "a `0123abcd` b\nc `__ADOPTION__` d `0123abcd`")
    assert page_errors(want, "a `0123abcd` b\nc `__ADOPTION__` d `4567abcd`")
    assert page_errors(want, want.replace(" b\n", " B\n"))
    assert page_errors(want, want + "\nmore")
    # a row: an old text not on its line, or a new text that does not differ
    for rows in (((START, 1, "zz", "y"),), ((START, 1, "a", "a"),)):
        try:
            apply_rows("a\nb", START, rows)
        except AssertionError:
            continue
        raise AssertionError("a bad row applied: %r" % (rows,))
    # W103: a row located by its text. Lines moved above the rows pass; a new text missing, doubled or on the other page, an old
    # text that survives (on the row's line or elsewhere on the page), a token filled with two values and two rows out of their
    # copy's order each fail
    cp = {START: "h\nold one here\nmid\nkeep two\nend `__CANDIDATE__` x", SUPPLIER: "s\nthird old\nt"}
    rs = [(START, 2, "old one", "new one `__ADOPTION__`"), (START, 4, "keep two", "keep two\nadded `__CANDIDATE__` line"),
          (SUPPLIER, 2, "third old", "third new `__CANDIDATE__`")]
    good = {p: apply_rows(cp[p], p, rs) for p in cp}
    assert not row_errors(rs, good, cp)
    filled = {p: good[p].replace("__CANDIDATE__", "0123abcd").replace("__ADOPTION__", "4567abcd") for p in good}
    moved = dict(filled, **{START: "seven\nnew\nlines\nmove\nevery\nrow\ndown\n" + filled[START], SUPPLIER: "x\n" + filled[SUPPLIER]})
    assert not row_errors(rs, moved, cp), row_errors(rs, moved, cp)
    mutants = {
        "a new text missing (the row not applied)": dict(good, **{START: good[START].replace("new one", "old one")}),
        "a new text doubled": dict(good, **{START: good[START] + "\nnew one `__ADOPTION__`"}),
        "an old text surviving elsewhere on the page": dict(good, **{START: good[START] + "\nthe old one again"}),
        "an old text surviving on the row's line": dict(good, **{SUPPLIER: good[SUPPLIER].replace("third new", "third old third new")}),
        "a new text on the other page": {START: good[START].replace("\nnew one `__ADOPTION__` here", "\n here"),
                                         SUPPLIER: good[SUPPLIER] + "\nnew one `__ADOPTION__`"},
        "a token filled with two values": dict(filled, **{SUPPLIER: good[SUPPLIER].replace("__CANDIDATE__", "89abcdef")}),
        "a token literal on one page and filled on the other": dict(good, **{SUPPLIER: filled[SUPPLIER]}),
        "two rows out of their copy's order": dict(good, **{START: "h\nkeep two\nadded `__CANDIDATE__` line\nmid\nnew one `__ADOPTION__` "
                                                                    "here\nend `__CANDIDATE__` x"}),
    }
    for name, pages in mutants.items():
        assert row_errors(rs, pages, cp), "row_errors accepts %s" % name
    # tokens: an undeclared one, __PROMOTED__
    assert token_errors(START, "x `__GATE__`") and token_errors(START, "x `__PROMOTED__`") and not token_errors(START, "`__ADOPTION__`")
    # placement: the real page passes; set 31's Layer 9 block moved below its set 30 block fails
    t = _read(LS)
    assert not placement_errors(t)
    b9 = block31(t, "9")
    moved = t.replace(L31["9"] + "\n" + b9, L31["9"] + "\n", 1)
    i = moved.index("\n**After set 29 (4 October 2026)", moved.index(L31["9"]))
    assert placement_errors(moved[:i + 1] + b9 + moved[i + 1:])
    # citations: a changed quote, a line out of range, another commit
    fake = {"x.md": "one\ntwo words here\nthree"}
    show = lambda sha, p: fake.get(p)  # noqa: E731
    assert not citation_errors("`%s:x.md:2` `two words`" % RES31, show)[0]
    assert citation_errors("`%s:x.md:2` `two other`" % RES31, show)[0]
    assert citation_errors("`%s:x.md:9` `two`" % RES31, show)[0]
    assert citation_errors("`0123abcd:x.md:2` `two`", show)[0]
    # words: a dash, an acceptance word outside a quotation, a percentage
    assert word_errors("a " + DASHES[1]) and word_errors("the gate PASSES") and word_errors("90 % done")
    assert not word_errors("`Layer 4's DESK gate: PASSES` and \"RELEASED\" quoted; CORRECTIONS NOT CLOSED")


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
