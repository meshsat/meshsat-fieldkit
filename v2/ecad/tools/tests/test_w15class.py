#!/usr/bin/env python3
"""Set 30's commit classification after cx46 (MESHSAT-1357, 6 October 2026): the record covers every commit between the reviewed
candidate and the promoted revision, its columns are git's, its classes are the fixed set, its quotes are on their cited lines.

The record is `v2/docs/records/int30/CLASSIFICATION.md`, W15's draft (`CLASSIFICATION.draft.md` at fnd/w15class 57bcdbfc, rows 1 to
38 over `git rev-list 4d0ff8a2..6bc4424e`) renamed at the adoption, its two placeholder rows (commit 2b and the candidate commit)
replaced by rows 39 to 45 (the seven commits after 6bc4424e) and its summary recomputed: one row per commit of
`git rev-list 4d0ff8a2..dd1aed00` (merges and their second parents' commits included), the class of each from the brief's fixed set,
and a summary. A citation `<sha>:path:N` followed by a code span quotes line N of that file at that revision (a `\\|` in the span is
a `|` of the file); `cx46:N` is line N of the filed check of cx46.

Restated at the adoption (W26, fnd/adopt30a): the draft-stage predicates "both placeholder rows kept, each 'not determined'" and "the
first line is the DONE / NOT DONE / NEXT line" became "no placeholder and no 'not determined' cell remains, the record opens with its
title" and "the rows of commit 2b, the candidate, the re-key, the l6r2 correction and W19's merge stand and carry the shas the
coordinator saved in `<worktrees>/_runs/int30/ADOPTION-VALUES.md`" (that file is outside the tree: without it that predicate raises
Skip, the git ones still run). The range's tip moved from 6bc4424e to the promoted dd1aed00; every other predicate is unchanged.

What fails here: a commit of the range missing, doubled or out of order, or a sha that is not in the range; a short sha that is not
its full sha's prefix; a date, subject or file count that is not git's; a class word outside the fixed set; a merge not classed MERGE
or a commit classed MERGE that is not a merge; an OUTSIDE P0 row touching v2/docs/records or v2/ecad; a REVIEWED-INPUT CHANGED row
without an old and a new quote; a quote that is not on its cited line at its revision; a `cx46:N` the test does not know, or one whose
line does not carry the item it is cited for; summary counts that differ from the table; a placeholder filled or dropped; an em or en
dash. Each predicate is also run on a mutant of the record that it must refuse.

Read-only: git is read with `git show`, `git log`, `git diff` and `git rev-list`; nothing is written. A checkout without git or without
the two bounds' commits raises Skip. No pytest is needed (tests/run.py runs the `t_` functions); `test_` aliases let pytest collect
them."""
import os
import re
import subprocess
from collections import Counter

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
RUNS = os.path.join(os.path.dirname(os.path.dirname(REPO)), "meshsat-fieldkit", "_runs")
VALUES = os.path.join(RUNS, "int30", "ADOPTION-VALUES.md")
DRAFT = "v2/docs/records/int30/CLASSIFICATION.md"
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
TIP = "dd1aed00d0a0a521063b5792550bc510c4707c59"           # the promoted revision (INTEGRATED = CANDIDATE = PROMOTED)
W15_TIP = "6bc4424ec64592e1a501af5db2246f3391c525a0"       # the integration's committed tip when W15 wrote rows 1 to 38
CX46 = "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT (restatement)", "GENERATOR DATA (text)", "TEST / FIXTURE",
         "DIGEST RE-PIN / REGENERATED OUTPUT", "MERGE", "OUTSIDE P0")
PLACEHOLDERS = ("__2B__", "__CANDIDATE__", "__REKEY__")

# Every `cx46:N` the draft may cite, with words that must be on that line of the filed check.
CX46_LINES = {
    17: '"command": "git diff 06077cee 4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"',
    55: '"name": "Draft syntax and baseline composition membership"',
    60: "Board E baseline orders agree and exclude B2.",
    100: '"1. v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:663',
    101: '"2. v2/docs/records/l9t5/l9t5_paloop.py:198-205,224-245',
    104: '"6. v2/docs/records/l9t5/apply_hw_fw_contract_t10.py:80-81',
    107: '"9. v2/docs/records/l4e11/l4e11_power.out:2036-2060',
    111: '"18. v2/docs/records/l4e7/B2-PRESENCE.md:3-4,10-11,45-49',
    116: '"item": "1. Missing governing inputs and twelve-row states: NOT CLOSED"',
    121: '"item": "2. Q1 reference loading, resistor corners and propagation: NOT CLOSED"',
    131: '"item": "4. Q2 return placement and distributed solution: NOT CLOSED"',
    141: '"item": "6. Q3 independent clock/share/excess-current protection: NOT CLOSED"',
    146: '"item": "7. Q3 sustained peak junction and qualification envelope: NOT CLOSED"',
    161: '"item": "10. Q5 common-path faults and automatic diagnostic: NOT CLOSED"',
    176: '"item": "13. Q7 connected coordination and service claims: NOT CLOSED"',
    181: '"item": "14. Q7 regeneration and stable bindings: CLOSED AS CONDITIONAL"',
    201: '"item": "18. B2 uniformly unselected and withdrawn outside baseline: NOT CLOSED"',
}

ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _flat(s):
    return " ".join(s.split())


def _git(*args, env=None):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True, env=env)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def _need_git():
    try:
        for sha in (REVIEWED, TIP):
            r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True)
            if r.returncode != 0:
                raise Skip("commit %s is not in this checkout" % sha[:8])
    except OSError as e:
        raise Skip("no git here: %s" % e)


def _draft():
    p = os.path.join(REPO, DRAFT)
    if not os.path.isfile(p):
        raise AssertionError("the draft %s is missing" % DRAFT)
    return open(p, encoding="utf-8").read()


_CACHE = {}


def _range():
    """The range as git gives it: [(full sha, parents, date, subject, file names)] oldest first, topological."""
    if "range" in _CACHE:
        return _CACHE["range"]
    _need_git()
    env = dict(os.environ, TZ="Europe/Amsterdam")
    log = _git("log", "--topo-order", "--reverse", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%H%x09%P%x09%ad%x09%s",
               "%s..%s" % (REVIEWED, TIP), env=env)
    out = []
    for line in log.split("\n"):
        if not line:
            continue
        sha, parents, date, subj = line.split("\t", 3)
        ps = parents.split()
        if len(ps) > 1:
            names = _git("diff", "--name-only", ps[0], sha).split()
        else:
            names = _git("show", "--name-only", "--format=", sha).split()
        out.append((sha, ps, date, subj, names))
    _CACHE["range"] = out
    return out


def _rows(text):
    """The table's rows: (number cell, cells) for every line of section 1 that starts with '| ' and is not the header."""
    rows = []
    sec = text.split("## 1. ", 1)[1].split("\n## 2. ", 1)[0]
    for line in sec.split("\n"):
        if not line.startswith("| ") or line.startswith("| # ") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in CELL_SPLIT.split(line.strip())[1:-1]]
        rows.append(cells)
    return rows


def _row_sha(cells):
    m = re.match(r"`([0-9a-f]{8})` / `([0-9a-f]{40})`$", cells[1])
    return m.groups() if m else None


def _classes(cells):
    return [c.strip() for c in cells[6].split(" + ")]


# ---- predicates: each returns a list of problems (empty when the draft holds) ----

def p_hygiene(text):
    bad = []
    if "\u2014" in text or "\u2013" in text:
        bad.append("an em or en dash")
    if not text.startswith("# Set 30: every commit between the REVIEWED candidate and the PROMOTED revision, classified"):
        bad.append("the record does not open with its title")
    if "**DONE:**" in text or "**NOT DONE:**" in text:
        bad.append("a draft's DONE / NOT DONE / NEXT line is left in the record")
    for ph in PLACEHOLDERS:
        if ph in text:
            bad.append("the placeholder %s is left in the record" % ph)
    for c in _rows(text):
        if len(c) < 8 or c[6] == "not determined" or c[2] == "pending":
            bad.append("row %s is not determined" % c[0])
    return bad


def _values():
    """The coordinator's saved values: {name: sha} read from ADOPTION-VALUES.md (Skip when the file is not on this host)."""
    if not os.path.isfile(VALUES):
        raise Skip("the coordinator's values file is not on this host")
    v = open(VALUES, encoding="utf-8").read()
    out = {}
    pats = {"CANDIDATE": r"INTEGRATED = CANDIDATE = PROMOTED = MIRROR \(GitHub main\): ([0-9a-f]{40})",
            "2B": r"2b ([0-9a-f]{40})", "L6R2": r"the l6r2 correction ([0-9a-f]{8})",
            "W19": r"W19's regression ([0-9a-f]{8}) merged at", "W19M": r"merged at ([0-9a-f]{8})",
            "REKEY": r"the re-keyed l4e7 cache ([0-9a-f]{40})", "DEPS": r"the re-key's dependents ([0-9a-f]{40})"}
    for k, pat in pats.items():
        m = re.search(pat, v)
        if not m:
            raise AssertionError("the values file carries no %s" % k)
        out[k] = m.group(1)
    return out


def p_values(text, vals):
    """Rows 39 to 45 stand and carry the coordinator's saved shas: 2b first, the candidate last, the re-key, its dependents, the l6r2
    correction and W19's regression with its merge each in a row of its own, classed."""
    bad = []
    rows = [c for c in _rows(text) if _row_sha(c)]
    full = [_row_sha(c)[1] for c in rows]
    short = [_row_sha(c)[0] for c in rows]
    if len(rows) < 45:
        return ["only %d rows" % len(rows)]
    if full[38] != vals["2B"]:
        bad.append("row 39 is %s, not commit 2b %s" % (full[38][:8], vals["2B"][:8]))
    if full[-1] != vals["CANDIDATE"]:
        bad.append("the last row is %s, not the candidate %s" % (full[-1][:8], vals["CANDIDATE"][:8]))
    for k in ("REKEY", "DEPS"):
        if vals[k] not in full[38:]:
            bad.append("no row after 6bc4424e for %s %s" % (k, vals[k][:8]))
    for k in ("L6R2", "W19", "W19M"):
        if vals[k] not in short[38:]:
            bad.append("no row after 6bc4424e for %s %s" % (k, vals[k]))
    for c in rows[38:]:
        if not _classes(c) or _classes(c)[0] not in FIXED:
            bad.append("row %s carries no class of the fixed set" % c[0])
    return bad


def p_coverage(text, rng):
    bad = []
    rows = [c for c in _rows(text) if c[1] not in ["`%s`" % p for p in PLACEHOLDERS]]
    want = [r[0] for r in rng]
    got = []
    for i, c in enumerate(rows, 1):
        s = _row_sha(c)
        if not s:
            bad.append("row %d has no `short` / `full` sha cell" % i)
            continue
        if not s[1].startswith(s[0]):
            bad.append("row %d: %s is not the prefix of %s" % (i, s[0], s[1]))
        if c[0] != str(i):
            bad.append("row %d is numbered %s" % (i, c[0]))
        got.append(s[1])
    if got != want:
        missing = [x[:8] for x in want if x not in got]
        extra = [x[:8] for x in got if x not in want]
        doubled = [x[:8] for x, k in Counter(got).items() if k > 1]
        bad.append("the rows are not the range in git's order (missing %s, not in the range %s, doubled %s)" % (missing, extra, doubled))
    return bad


def p_columns(text, rng):
    bad = []
    by = {r[0]: r for r in rng}
    for c in _rows(text):
        s = _row_sha(c)
        if not s or s[1] not in by:
            continue
        sha, ps, date, subj, names = by[s[1]]
        if c[2] != date:
            bad.append("%s: date %r is not git's %r" % (sha[:8], c[2], date))
        if c[3].replace("\\|", "|") != subj:
            bad.append("%s: the subject is not git's" % sha[:8])
        m = re.match(r"(\d+):", c[5])
        if not m or int(m.group(1)) != len(names):
            bad.append("%s: file count %r is not git's %d" % (sha[:8], c[5][:12], len(names)))
    return bad


def p_classes(text, rng):
    bad = []
    by = {r[0]: r for r in rng}
    for c in _rows(text):
        s = _row_sha(c)
        if not s:
            continue
        cls = _classes(c)
        for w in cls:
            if w not in FIXED:
                bad.append("%s: %r is not a class of the fixed set" % (s[0], w))
        if len(set(cls)) != len(cls):
            bad.append("%s: a class twice" % s[0])
        if s[1] not in by:
            continue
        sha, ps, date, subj, names = by[s[1]]
        if (len(ps) > 1) != ("MERGE" in cls):
            bad.append("%s: MERGE %s but the commit has %d parents" % (s[0], "given" if "MERGE" in cls else "missing", len(ps)))
        if "MERGE" in cls and cls != ["MERGE"]:
            bad.append("%s: a merge carries a second class" % s[0])
        if "OUTSIDE P0" in cls and any(n.startswith("v2/docs/records/") or n.startswith("v2/ecad/") for n in names):
            bad.append("%s: OUTSIDE P0 but it touches v2/docs/records or v2/ecad" % s[0])
        if "REVIEWED-INPUT CHANGED" in cls:
            revs = {m.group(1)[:8] for m in ANCHOR.finditer(c[7])}
            if len(list(ANCHOR.finditer(c[7]))) < 2 or len(revs) < 2:
                bad.append("%s: REVIEWED-INPUT CHANGED without an old and a new quote at two revisions" % s[0])
    return bad


def p_anchors(text):
    bad = []
    files = {}
    n = 0
    for m in ANCHOR.finditer(text):
        rev, path, line, quote = m.group(1), m.group(2), int(m.group(3)), m.group(4).replace("\\|", "|")
        key = (rev, path)
        if key not in files:
            try:
                files[key] = _git("show", "%s:%s" % (rev, path)).split("\n")
            except RuntimeError as e:
                bad.append("%s:%s cannot be read: %s" % (rev, path, e))
                files[key] = []
        lines = files[key]
        n += 1
        if not (1 <= line <= len(lines)) or _flat(quote) not in _flat(lines[line - 1]):
            bad.append("%s:%s:%d does not carry %r" % (rev, path, line, quote[:60]))
    if n == 0:
        bad.append("no quoted anchor found")
    return bad


def p_cx46(text):
    bad = []
    lines = _git("show", "%s:%s" % (TIP, CX46)).split("\n")
    for m in re.finditer(r"`cx46:(\d+)`", text):
        k = int(m.group(1))
        if k not in CX46_LINES:
            bad.append("cx46:%d is not a line this test knows" % k)
        elif CX46_LINES[k] not in lines[k - 1]:
            bad.append("cx46:%d does not carry %r" % (k, CX46_LINES[k]))
    return bad


def p_summary(text):
    bad = []
    rows = [c for c in _rows(text) if _row_sha(c)]
    first = Counter(_classes(c)[0] for c in rows)
    anyc = Counter(w for c in rows for w in _classes(c))
    summ = text.split("## 2. Summary", 1)[1]
    seen = set()
    for m in re.finditer(r"^\| `([^`]+)` \| (\d+) \| (\d+) \|$", summ, re.M):
        w, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        seen.add(w)
        if first[w] != a or anyc[w] != b:
            bad.append("summary %s: %d / %d, the table %d / %d" % (w, a, b, first[w], anyc[w]))
    if seen != set(FIXED):
        bad.append("the summary table does not list the fixed set: %s" % sorted(set(FIXED) ^ seen))
    m = re.search(r"^\| total \| (\d+) \|", summ, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the summary's total is not the table's %d rows" % len(rows))
    ric = [_row_sha(c)[0] for c in rows if "REVIEWED-INPUT CHANGED" in _classes(c)]
    m = re.search(r"\*\*The `REVIEWED-INPUT CHANGED` rows: (\d+), not empty\.\*\* In order: ([^.]+)\.", summ)
    if not m or int(m.group(1)) != len(ric) or re.findall(r"`([0-9a-f]{8})`", m.group(2)) != ric:
        bad.append("the summary's REVIEWED-INPUT CHANGED list is not the table's %s" % ric)
    st = re.search(r"^> Between REVIEWED .*$", summ, re.M)
    merges = sum(1 for c in rows if _classes(c) == ["MERGE"])
    if not st:
        bad.append("the statement for RESULT.md is missing")
    else:
        s = st.group(0)
        want = "the %d commits of `git rev-list 4d0ff8a2..%s` (%d commits, %d merges)" % (len(rows), TIP[:8], len(rows) - merges, merges)
        if want not in s:
            bad.append("the statement does not read %r" % want)
        if "change what cx46 read in %d commits" % len(ric) not in s:
            bad.append("the statement's count of changed rows is not %d" % len(ric))
    return bad


# ---- the tests ----

def t_the_record_carries_no_dash_no_placeholder_and_opens_with_its_title():
    text = _draft()
    assert p_hygiene(text) == [], p_hygiene(text)
    row39 = [l for l in text.split("\n") if l.startswith("| 39 | `")][0]
    cls39 = "| REVIEWED-INPUT CHANGED + DIGEST RE-PIN / REGENERATED OUTPUT + RECORD TEXT (restatement) + TEST / FIXTURE |"
    assert cls39 in row39, "the mutation's anchor is not in row 39"
    assert p_hygiene(text.replace(row39, row39.replace(cls39, "| not determined |", 1), 1)), "a row left not determined passed"
    assert p_hygiene(text.replace("`d83d9f2d` / ", "`__2B__` / ", 1)), "a placeholder left in passed"
    assert p_hygiene("**DONE:** x; **NOT DONE:** y; **NEXT:** z\n\n" + text), "a draft state line passed"
    assert p_hygiene(text + "\nx \u2014 y\n"), "an em dash passed"


def t_the_rows_after_6bc4424e_carry_the_coordinators_saved_shas():
    _need_git()
    text = _draft()
    vals = _values()
    assert p_values(text, vals) == [], p_values(text, vals)
    rows = [l for l in text.split("\n") if re.match(r"\| 4[0-5] \| `", l)]
    assert p_values(text.replace(rows[-1] + "\n", "", 1), vals), "a dropped candidate row passed"
    swapped = dict(vals, CANDIDATE=vals["DEPS"])
    assert p_values(text, swapped), "a candidate sha other than the saved one passed"
    assert p_values(text, dict(vals, L6R2="00000000")), "a missing l6r2 correction row passed"


def t_the_table_covers_exactly_the_commits_between_the_bounds_in_gits_order():
    text = _draft()
    rng = _range()
    assert p_coverage(text, rng) == [], p_coverage(text, rng)
    rows = [l for l in text.split("\n") if re.match(r"\| \d+ \| `[0-9a-f]{8}`", l)]
    assert p_coverage(text.replace(rows[5] + "\n", "", 1), rng), "a dropped commit passed"
    assert p_coverage(text.replace(rows[5], rows[5] + "\n" + rows[5], 1), rng), "a doubled commit passed"
    fake = rows[0].replace(rng[0][0], "0" * 40).replace("`%s`" % rng[0][0][:8], "`00000000`")
    assert p_coverage(text.replace(rows[0], fake, 1), rng), "a sha outside the range passed"


def t_dates_subjects_and_file_counts_are_gits():
    text = _draft()
    rng = _range()
    assert p_columns(text, rng) == [], p_columns(text, rng)
    sha, ps, date, subj, names = rng[3]
    row = [l for l in text.split("\n") if ("`%s`" % sha) in l][0]
    assert p_columns(text.replace(row, row.replace(" | %d: " % len(names), " | %d: " % (len(names) + 1), 1), 1), rng), \
        "a wrong file count passed"
    assert p_columns(text.replace(row, row.replace(date, date[:-2] + "00" if not date.endswith("00") else date[:-2] + "01"), 1),
                     rng), "a wrong date passed"


def t_every_class_is_of_the_fixed_set_merges_are_merges_and_outside_p0_stays_outside():
    text = _draft()
    rng = _range()
    assert p_classes(text, rng) == [], p_classes(text, rng)
    assert p_classes(text.replace("| RECORD TEXT (restatement) |", "| PRESENTATION |", 1), rng), "a class outside the set passed"
    merge = [r for r in rng if len(r[1]) > 1][0]
    row = [l for l in text.split("\n") if ("`%s`" % merge[0]) in l][0]
    assert p_classes(text.replace(row, row.replace("| MERGE |", "| RECORD TEXT (restatement) |", 1), 1), rng), \
        "a merge not classed MERGE passed"
    ric = [l for l in text.split("\n") if "| REVIEWED-INPUT CHANGED" in l][0]
    stripped = ANCHOR.sub("`x`", ric)
    assert p_classes(text.replace(ric, stripped, 1), rng), "a REVIEWED-INPUT CHANGED row without quotes passed"


def t_every_quoted_value_is_on_its_cited_line_at_its_revision():
    _need_git()
    text = _draft()
    assert p_anchors(text) == [], p_anchors(text)
    m = next(ANCHOR.finditer(text))
    assert p_anchors(text.replace(m.group(0), m.group(0)[:-1] + " NOT ON THE LINE`", 1)), "a misquoted anchor passed"
    m2 = list(ANCHOR.finditer(text))[1]
    moved = m2.group(0).replace(":%s`" % m2.group(3), ":%d`" % (int(m2.group(3)) + 3), 1)
    assert p_anchors(text.replace(m2.group(0), moved, 1)), "an anchor at the wrong line passed"


def t_the_cx46_lines_cited_carry_the_items_named():
    _need_git()
    text = _draft()
    assert p_cx46(text) == [], p_cx46(text)
    assert p_cx46(text + "\n`cx46:99`\n"), "an unknown cx46 line passed"


def t_the_summary_counts_and_statement_are_the_tables():
    text = _draft()
    assert p_summary(text) == [], p_summary(text)
    m = re.search(r"^\| `MERGE` \| (\d+) \| (\d+) \|$", text, re.M)
    assert p_summary(text.replace(m.group(0), "| `MERGE` | %d | %s |" % (int(m.group(1)) + 1, m.group(2)), 1)), \
        "a wrong summary count passed"
    s = re.search(r"change what cx46 read in (\d+) commits", text)
    assert p_summary(text.replace(s.group(0), "change what cx46 read in %d commits" % (int(s.group(1)) - 1), 1)), \
        "a wrong statement count passed"


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


test_the_record_carries_no_dash_no_placeholder_and_opens_with_its_title = _pytest(
    t_the_record_carries_no_dash_no_placeholder_and_opens_with_its_title)
test_the_rows_after_6bc4424e_carry_the_coordinators_saved_shas = _pytest(t_the_rows_after_6bc4424e_carry_the_coordinators_saved_shas)
test_the_table_covers_exactly_the_commits_between_the_bounds_in_gits_order = _pytest(
    t_the_table_covers_exactly_the_commits_between_the_bounds_in_gits_order)
test_dates_subjects_and_file_counts_are_gits = _pytest(t_dates_subjects_and_file_counts_are_gits)
test_every_class_is_of_the_fixed_set_merges_are_merges_and_outside_p0_stays_outside = _pytest(
    t_every_class_is_of_the_fixed_set_merges_are_merges_and_outside_p0_stays_outside)
test_every_quoted_value_is_on_its_cited_line_at_its_revision = _pytest(t_every_quoted_value_is_on_its_cited_line_at_its_revision)
test_the_cx46_lines_cited_carry_the_items_named = _pytest(t_the_cx46_lines_cited_carry_the_items_named)
test_the_summary_counts_and_statement_are_the_tables = _pytest(t_the_summary_counts_and_statement_are_the_tables)
