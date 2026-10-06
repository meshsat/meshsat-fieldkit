#!/usr/bin/env python3
"""Set 31's result record (MESHSAT-1357, 6 October 2026, W39): `v2/docs/records/int31/RESULT.md`, its classification
`CLASSIFICATION.md` and the entry pages' rows `ENTRY-PAGES.patch.md` hold what they type.

What fails here: a commit of `dd1aed00..TIP` missing, doubled or out of the first-parent order with each merge's branch commits under
it; a short sha that is not its full sha's prefix; a date, subject or file count that is not git's; a class outside the brief's fixed
set, a merge not classed MERGE or a MERGE that is not a merge; a row that touches a file cx46 read, or a REVIEWED-INPUT CHANGED row,
without the words "UNREVIEWED since cx46"; a REVIEWED-INPUT CHANGED row that touches no file of the reviewed tree (present at
4d0ff8a2), or one that touches none of cx46's delta without naming its source row and the delta membership (set 30's rule's second
sentence, `eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`, reading A by the coordinator's ruling of 6 October 2026); a rule
paragraph that is not set 30's line 11 verbatim; summary counts, the 73 and 28 split, the category and merge lists or the bound
statement's numbers that are not the table's (the merges recomputed from git), and counts in RESULT.md or the entry pages' patch
that are not the table's: every count is recomputed, none typed in the test; a count typed in the records that is not git's; a commit named that this repository does not hold (outside the declared list of main's
commits); a quote that is not on its cited line at its revision or in its verbatim copy; the three claims not quoted verbatim from the
assessment; a placeholder outside the declared tokens; a patch row whose old text is not on its line of the copied page; an em or en
dash. Each predicate is also run on a mutant it must refuse.

The coordinator's logs (`<worktrees>/_runs`, outside the repository) are read by ONE test, which raises Skip where they are absent
(a rented box): run it in the runner pass (the record's section 8). When the coordinator classes the candidate's row after the
adoption's fill, TIP below moves with it (the record last read the lineage at the re-key's cache commit, `aa332280`; W56 added rows 32
and 33, 6 October 2026, and the checks of the counts those rows move: the later rows' split, the W51 reversal's numbers, RESULT's
sections 2d, 4, 6 and 7, the third chain run's and the spent re-keys' elapsed times, each recomputed from the table, git or the logged
stamps; W69 added row 34 and the re-key's elapsed times, 6 October 2026, from W68's finding F1).

The candidate's row. W69 (6 October 2026, from W68's F1) kept the candidate commit an unclassified placeholder row 35 that the fill
named. Restated by W83 (6 October 2026; basis: the coordinator's brief after the first candidate's failed gate, which hands over the two
commits that followed `aa332280`, so both exist and are classified): the first candidate `d0e283aa` is row 35 and the coordinator's test
correction `5f25daf3`, the second candidate, is row 36, both full rows; TIP moves to `5f25daf3`. No row of the table is unclassified now
(a placeholder row is refused). The candidate's name is a cell of the last first-parent row: "set 31's candidate, named by the fill:"
followed by `__CANDIDATE__` before the fill, or after it by a commit that must be that row's own commit, which follows the superseded
first candidate on the first-parent line (never `d0e283aa`, `aa332280` or another commit; never in another row; never twice). Every
other predicate is unchanged in what it refuses; the mutations whose anchor was a token that the fill removes insert an undeclared
token beside a sentence that stays. After the fill's second run the patch rows name the adoption commit, which a commit named in the
records may be only there and only when it descends from the named candidate. W91 (6 October 2026, W86's N1) added section 4a's
predicate: the first candidate's FAILED gate and the coordinator's known item, each with a mutant it must refuse.

W98 (7 October 2026, W86's N6 and N2) added four predicates, each with mutants it must refuse: every REVIEWED-INPUT CHANGED row names
the cx46 item that read its change, with cx46's words on their line of the filed check and the number cx46 itself gives that line, or
says that none names it ("outside the 62" exactly for the rows that touch none of the 62; set 30's rule's first sentence); RESULT.md's
section 1 counts over the base, the rows it names and its first-parent table, by git; section 2's prose classes and the merge table's
annotations, by the table; the candidate as filled into RESULT.md, LAYER-STATUS.md and the plan, row 36's own commit and the
promotion log's line as quoted (the log itself read in the runner pass).

Read-only: git is read with `git log`, `git show`, `git diff`, `git rev-list` and `git cat-file`; nothing is written. No pytest is
needed (tests/run.py runs the `t_` functions); `test_` aliases let pytest collect them."""
import hashlib
import os
import re
import subprocess
from collections import Counter

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = "v2/docs/records/int31"
RESULT = REC + "/RESULT.md"
CLASS = REC + "/CLASSIFICATION.md"
PATCH = REC + "/ENTRY-PAGES.patch.md"
SOURCES = REC + "/inputs/SOURCES.txt"
BASE = "dd1aed00d0a0a521063b5792550bc510c4707c59"          # set 30's promoted revision, set 31's base
TIP = "5f25daf3762ecd69c8764bf60de81a80f4119eab"           # set 31's lineage as the record last read it (W83: the second candidate, row 36)
SUPERSEDED = "d0e283aa52ceb7f303358862b539161b721475e5"    # set 31's first candidate (row 35), its four-log gate FAILED
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
CX45 = "06077cee"                                           # the delta cx46 read: git diff 06077cee 4d0ff8a2 (its line 17)
L4E9_EXTRA = ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l4e9/l4e9_power_path.out")
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT", "GENERATOR DATA (text)", "TEST", "DIGEST RE-PIN", "MERGE", "TOOLING")
DECLARED = ("__CANDIDATE__", "__PROMOTED__", "__GATE__", "__ADOPTION__")     # W41's round filled (rows 32, 33); the re-key written (row 34); rows 35, 36 written (W83)
# Restated by W65 (6 October 2026, fnd/adopt31; basis: the coordinator's ruling in its brief to W65, authority SESSION): the entry
# pages name the tested revision with __CANDIDATE__, the name W63's fill_res31.py fills (W39 wrote __PROMOTED__; under a fast-forward
# it is the same commit), so the patch's rows carry __CANDIDATE__ and __ADOPTION__ (its dated note says so); test_adopt31 holds the
# pages to the rows.
PATCH_TOKENS = ("__CANDIDATE__", "__ADOPTION__")
# main's commits named by the record, not in this branch's history until main is merged into set 31's lineage
OUTSIDE = {"eff28be3b80f882db545a849b0da1def0217f63d": "main's follow-up after set 30's adoption, the copies' source",
           "836f711b406be48d9eb58c9cf6f7491fbcf7c5ec": "set 30's adoption commit on main",
           "4196e9dfbb125cc50b091bdea47a34e432162970": "fnd/res31 at W39's last commit, the counts before W50's reconciliation",
           "353b41dd2144dba237f2df9616dadd452f62569f": "fnd/res31 at W50's last commit, the counts before W51's five rows",
           "7155b626a6ef2036de8843de2f1d1d94b2d01d71": "fnd/res31 at W51's last commit, the counts over the 101 before rows 32 and 33",
           "5f910eb53c753bd1f3f12b4ce7b174d2c36d33e5": "fnd/res31 at W56's last commit, the counts over the 103 before row 34",
           "1a8dc1504a5e73956664dbfffab2524304549e7e": "fnd/res31 at W69's commit, the counts over the 104 before rows 35 and 36",
           "ad757edb1be7e0fe3b586f986d2d704c9836fdcf": "main at set 31's adoption (the fill's second run), W98's base (W86's N6)"}
S30 = "eff28be3b80f882db545a849b0da1def0217f63d"              # set 30's adopted classification, its rule at line 11
S30C = "v2/docs/records/int30/CLASSIFICATION.md"
RIC = "REVIEWED-INPUT CHANGED"
ASSESS_COPY = REC + "/inputs/L4-DESK-GATE-ASSESSMENT-eff28be3.md"
ASSESS_TREE = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
CLAIMS = {492: "### Layer 4's DESK gate: NOT PASSED",
          496: "### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
          500: "### Power-design closure: BLOCKED. Fabrication release: BLOCKED."}

GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
COPY_ANCHOR = re.compile(r"`(v2/docs/records/int31/inputs/[^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
RUN_ANCHOR = re.compile(r"`<worktrees>/_runs/([^`:\s]+)(?::(\d+))?`(?:, entry \"([^\"]+)\",)? `([^`]+)`")
RUN_PATH = re.compile(r"`(?:<worktrees>/)?_runs/([\w./-]+\.(?:log|md|txt|sh|tsv))")
HEXTOK = re.compile(r"`([0-9a-f]{7,40})`")
PH = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
DASHES = ("—", "–")


def _git(*args):
    env = dict(os.environ, TZ="Europe/Amsterdam")
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True, env=env)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def _has(sha):
    r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True)
    return r.returncode == 0


def _need_git():
    try:
        for sha in (BASE, TIP, REVIEWED):
            if not _has(sha):
                raise Skip("commit %s is not in this checkout" % sha[:8])
    except OSError as e:
        raise Skip("no git here: %s" % e)


def _read(rel):
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        raise AssertionError("%s is missing" % rel)
    return open(p, encoding="utf-8").read()


_C = {}


def _show(rev, path):
    k = (rev, path)
    if k not in _C:
        _C[k] = _git("show", "%s:%s" % (rev, path)).split("\n")
    return _C[k]


def _order():
    """[(row number, full sha, parents, date, subject, names)] first-parent, each merge's branch commits under it."""
    if "order" in _C:
        return _C["order"]
    _need_git()
    out = []
    fp = _git("rev-list", "--first-parent", "--reverse", "%s..%s" % (BASE, TIP)).split()

    def one(num, c):
        ps = _git("rev-list", "--parents", "-n1", c).split()[1:]
        date, subj = _git("log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%ad%x09%s", c).rstrip("\n").split("\t", 1)
        names = (_git("diff", "--name-only", ps[0], c) if len(ps) > 1 else _git("show", "--name-only", "--format=", c)).split()
        out.append((num, c, ps, date, subj, names))
        return ps

    for i, c in enumerate(fp, 1):
        ps = one(str(i), c)
        if len(ps) > 1:
            br = _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (ps[0], ps[1]), "^" + BASE).split()
            for j, b in enumerate(br, 1):
                one("%d.%d" % (i, j), b)
    _C["order"] = out
    return out


def _reviewed():
    if "rev" not in _C:
        _C["rev"] = set(_git("diff", "--name-only", CX45, REVIEWED).split()) | set(L4E9_EXTRA)
    return _C["rev"]


def _tree():
    """The files present at cx46's candidate: "a file of the reviewed tree" in set 30's rule."""
    if "tree" not in _C:
        _C["tree"] = set(_git("ls-tree", "-r", "--name-only", REVIEWED).split("\n")) - {""}
    return _C["tree"]


def _rows(text):
    sec = text.split("## 1. ", 1)[1].split("\n## 2. ", 1)[0]
    rows = []
    for line in sec.split("\n"):
        if not line.startswith("| ") or line.startswith("| # ") or line.startswith("|---"):
            continue
        rows.append([c.strip() for c in CELL_SPLIT.split(line.strip())[1:-1]])
    return rows


def _sha_cell(cells):
    m = re.match(r"`([0-9a-f]{8})` / `([0-9a-f]{40})`$", cells[1])
    return m.groups() if m else None


def _classes(cells):
    return [c.strip() for c in cells[6].split(" + ")]


PH_CELL = re.compile(r"`(__[A-Z0-9]+__|[0-9a-f]{8,40})`$")
CAND_CELL = re.compile(r"set 31's candidate, named by the fill: `(__[A-Z0-9]+__|[0-9a-f]{8,40})`")


def _placeholder_row(cells):
    """A row the table does not classify: its sha cell is ONE code span holding a token or a commit (a classified row's sha cell is
    `short` / `full`). Since W83 (rows 35 and 36 written) the table has none, and p_placeholders and p_candidate_row refuse one."""
    return bool(PH_CELL.match(cells[1]))


def _candidate(text):
    """The candidate commit the fill named in the candidate's cell, or None before the fill (the token) or when the cell is malformed."""
    hits = [m.group(1) for c in _rows(text) for m in CAND_CELL.finditer(" | ".join(c))]
    if len(hits) != 1 or hits[0].startswith("__") or not _has(hits[0]):
        return None
    return _git("rev-parse", hits[0] + "^{commit}").strip()


def p_candidate_row(text):
    """No unclassified row; exactly one candidate's cell, in the last first-parent row (TIP's row), reading `__CANDIDATE__` before the
    fill, or after it a commit that is that row's own commit and follows the superseded first candidate on the first-parent line
    (W83, 6 October 2026: never `d0e283aa`, an earlier commit or another row's)."""
    rows = _rows(text)
    ph = [c for c in rows if _placeholder_row(c)]
    if ph:
        return ["%d unclassified row(s): every commit to the candidate is classified since W83" % len(ph)]
    hits = [(c, m.group(1)) for c in rows for m in CAND_CELL.finditer(" | ".join(c))]
    if len(hits) != 1:
        return ["%d candidate cells, not one" % len(hits)]
    c, val = hits[0]
    bad = []
    last = max(int(r[0]) for r in rows if "." not in r[0])
    if c[0] != str(last):
        bad.append("the candidate's cell is in row %s, not the last first-parent row %d" % (c[0], last))
    s = _sha_cell(c)
    if not s or s[1] != TIP:
        bad.append("the candidate's row is not TIP's row (%s)" % TIP[:8])
    if val.startswith("__"):
        if val != "__CANDIDATE__":
            bad.append("the candidate's cell carries %s, not __CANDIDATE__" % val)
        return bad
    if not _has(val):
        return bad + ["the candidate's cell names %s, not a commit of this repository" % val]
    full_sha = _git("rev-parse", val + "^{commit}").strip()
    if not s or full_sha != s[1]:
        bad.append("the candidate's cell names %s, not its row's own commit" % val[:12])
    if full_sha == SUPERSEDED or SUPERSEDED not in _git("rev-list", "--first-parent", full_sha).split():
        bad.append("the candidate's cell names %s, which does not follow the superseded %s on the first-parent line" % (val[:12], SUPERSEDED[:8]))
    return bad


# ---- predicates: each returns a list of problems (empty when the record holds) ----

def p_hygiene(texts):
    bad = []
    for name, t in texts.items():
        if any(d in t for d in DASHES):
            bad.append("%s carries an em or en dash" % name)
        if name.endswith(".md") and "/inputs/" not in name:
            first = [l for l in t.split("\n") if l.strip()][1]
            if not first.startswith("**DONE:**"):
                bad.append("%s: the paragraph after the title is not the DONE / NOT DONE / NEXT line" % name)
    return bad


def _without_subjects(text):
    """The classification with each table row's subject cell blanked: a subject is git's text, and set 30's commits name their own
    placeholders in it (rows 31.6, 31.16, 31.17), which are not this record's."""
    out = []
    for line in text.split("\n"):
        if line.startswith("| ") and not line.startswith("| # ") and "\n## 1. " in text and line.count("|") > 8:
            cells = CELL_SPLIT.split(line)
            if len(cells) > 4 and re.match(r" `[0-9a-f]{8}` / `[0-9a-f]{40}` $", cells[2]):
                cells[4] = " "
                line = "|".join(cells)
        out.append(line)
    return "\n".join(out)


def p_placeholders(texts):
    bad = []
    for name, t in texts.items():
        if name == CLASS:
            t = _without_subjects(t)
        for tok in set(PH.findall(t)):
            if tok not in DECLARED:
                bad.append("%s: %s is not a declared placeholder" % (name, tok))
            if name == PATCH and tok not in PATCH_TOKENS:
                bad.append("%s: %s is not one of the patch's two tokens" % (name, tok))
    for c in _rows(texts[CLASS]):
        if _placeholder_row(c):          # W83: rows 35 and 36 are written; an unclassified row is refused (W69 required its words)
            bad.append("row %s is an unclassified placeholder row (%s)" % (c[0], c[1]))
    return bad


def p_coverage(text, order):
    bad = []
    rows = [c for c in _rows(text) if not _placeholder_row(c)]
    want = [(o[0], o[1]) for o in order]
    got = []
    for c in rows:
        s = _sha_cell(c)
        if not s:
            bad.append("row %s has no `short` / `full` sha cell" % c[0])
            continue
        if not s[1].startswith(s[0]):
            bad.append("row %s: %s is not the prefix of %s" % (c[0], s[0], s[1]))
        got.append((c[0], s[1]))
    if got != want:
        miss = [w[1][:8] for w in want if w not in got]
        extra = [g[1][:8] for g in got if g not in want]
        bad.append("the rows are not the range in its order (missing or misnumbered %s, extra %s)" % (miss, extra))
    return bad


def p_columns(text, order):
    bad = []
    by = {o[1]: o for o in order}
    for c in _rows(text):
        s = _sha_cell(c)
        if not s or s[1] not in by:
            continue
        num, sha, ps, date, subj, names = by[s[1]]
        if c[2] != date:
            bad.append("%s: date %r is not git's %r" % (sha[:8], c[2], date))
        if c[3].replace("\\|", "|") != subj:
            bad.append("%s: the subject is not git's" % sha[:8])
        m = re.match(r"(\d+):", c[5])
        if not m or int(m.group(1)) != len(names):
            bad.append("%s: file count %r is not git's %d" % (sha[:8], c[5][:12], len(names)))
        cls = _classes(c)
        if any(k not in FIXED for k in cls):
            bad.append("%s: a class outside the fixed set: %s" % (sha[:8], cls))
        if (cls[0] == "MERGE") != (len(ps) > 1) or ("MERGE" in cls and cls != ["MERGE"]):
            bad.append("%s: MERGE and the commit's parents disagree" % sha[:8])
        rv = [n for n in names if n in _reviewed()]
        if (rv or cls[0] == RIC) and "UNREVIEWED since cx46" not in c[7]:
            bad.append("%s touches %d reviewed file(s) or is %s and does not say UNREVIEWED since cx46" % (sha[:8], len(rv), RIC))
        if cls[0] != RIC:
            continue
        if not [n for n in names if n in _tree()]:
            bad.append("%s is %s but touches no file of the reviewed tree" % (sha[:8], RIC))
        carried = "second sentence" in c[7]
        if not rv and not carried:
            bad.append("%s is %s, touches none of cx46's delta and does not class a carried change" % (sha[:8], RIC))
        if carried and (not re.search(r"set 30's rows? \d+|\brows? \d+(?:\.\d+)?\b", c[7]) or "in the delta cx46 read" not in c[7]):
            bad.append("%s: a carried change without its source row or the delta membership" % sha[:8])
    return bad


def p_summary(text):
    bad = []
    rows = [c for c in _rows(text) if not _placeholder_row(c)]
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    sec = text.split("\n## 2. ", 1)[1]
    flat = " ".join(sec.replace("\n> ", "\n").split())   # the bound statement is a wrapped quotation: joined before it is read
    for k in FIXED:
        m = re.search(r"^\| `%s` \| (\d+) \| (\d+) \|$" % re.escape(k), sec, re.M)
        if not m or int(m.group(1)) != first[k] or int(m.group(2)) != carry[k]:
            bad.append("the summary row of %s is not the table's (%d, %d)" % (k, first[k], carry[k]))
    m = re.search(r"^\| total \| (\d+) \|", sec, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the summary's total is not the table's %d" % len(rows))
    ri = [c for c in rows if _classes(c)[0] == RIC]
    m = re.search(r"\*\*The `REVIEWED-INPUT CHANGED` rows: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?)\. By what", sec, re.S)
    if not m or int(m.group(1)) != len(ri):
        bad.append("the REVIEWED-INPUT CHANGED count line is not the table's %d" % len(ri))
    else:
        named = re.findall(r"`([0-9a-f]{8})`\s\(([\d.]+)\)", m.group(2))
        if named != [(_sha_cell(c)[0], c[0]) for c in ri]:
            bad.append("the REVIEWED-INPUT CHANGED list is not the table's rows in order")
    # the 73 commits to f0748b49 (rows 1 to 30 and their branch rows) and row 31's 28, each split by first class
    for label, part in (("Over the %d commits to `f0748b49` (rows 1 to 30 and their branch rows), before main's merge: ",
                         [c for c in rows if int(c[0].split(".")[0]) <= 30]),):
        f = Counter(_classes(c)[0] for c in part)
        want = label % len(part) + "; ".join("%s %d" % (k, f[k]) for k in FIXED) + "."
        if want not in flat:
            bad.append("the split line does not read %r" % want)
    r31 = [c for c in rows if int(c[0].split(".")[0]) == 31]
    f31 = Counter(_classes(c)[0] for c in r31)
    ric31 = [c[0] for c in r31 if _classes(c)[0] == RIC]
    want31 = "Row 31 and its %d branch rows" % (len(r31) - 1)
    if want31 not in flat or ("add: REVIEWED-INPUT CHANGED %d (rows %s)" % (len(ric31), _and(ric31))) not in flat or \
            ("RECORD TEXT %d, TEST %d, DIGEST RE-PIN %d" % (f31["RECORD TEXT"], f31["TEST"], f31["DIGEST RE-PIN"])) not in flat or \
            ("MERGE %d." % f31["MERGE"]) not in flat:
        bad.append("row 31's split is not the table's")
    later = [c for c in rows if int(c[0].split(".")[0]) > 31]
    fl = Counter(_classes(c)[0] for c in later)
    if later:
        bits = []
        for k in FIXED:
            if fl[k]:
                rr = [c[0] for c in later if _classes(c)[0] == k]
                bits.append("%s %d" % (k, fl[k]) + (" (rows %s)" % _and(rr) if k == RIC else ""))
        wantl = ("Rows %s (after `d5d9c252`: W41's two commits, the re-key's cache commit, the first candidate and the coordinator's test "
                 "correction) add: %s." % (_and([c[0] for c in later]), "; ".join(bits)))
        if wantl not in flat:
            bad.append("the later rows' split does not read %r" % wantl)
    rt = Counter(_classes(c)[0] for c in rows)["RECORD TEXT"]
    rev = "the count moves from %d to %d of the %d (RECORD TEXT from %d to %d;" % (len(ri), len(ri) + 3, len(rows), rt, rt - 3)
    if rev not in flat:
        bad.append("W51's reversal does not read %r (rows 31.14, 31.21 and 31.25 moved)" % rev)
    # the three kinds: each REVIEWED-INPUT CHANGED row in exactly one, each count the number of rows named in it
    kinds = (("narrow", r"- \*\*They narrow, tighten or restate a state to a weaker claim \((\d+)\):\*\*(.*?)(?=\n- \*\*)"),
             ("not only", r"- \*\*They do not only narrow \((\d+)\):\*\*(.*?)(?=\n- \*\*)"),
             ("re-adopt", r"- \*\*It re-adopts a governing list cx46 read \((\d+)\):\*\*(.*?)(?=\n- \*\*)"))
    rs = {_sha_cell(c)[0] for c in ri}
    seen, counts = [], {}
    for k, rx in kinds:
        b = re.search(rx, sec, re.S)
        if not b:
            bad.append("the kind %r is missing" % k)
            continue
        got = sorted(set(re.findall(r"`([0-9a-f]{8})`", b.group(2))) & rs)
        counts[k] = int(b.group(1))
        if counts[k] != len(got):
            bad.append("the kind %r counts %s but names %d rows" % (k, b.group(1), len(got)))
        seen += got
    if sorted(seen) != sorted(rs):
        bad.append("the kinds do not name each REVIEWED-INPUT CHANGED row exactly once")
    mb = re.search(r"- \*\*Merges that bring `REVIEWED-INPUT CHANGED` rows \((\d+)\):\*\*(.*?)(?=\n- \*\*)", sec, re.S)
    nm = re.findall(r"`([0-9a-f]{8})` \(", mb.group(2)) if mb else []
    if not mb or int(mb.group(1)) != len(nm):
        bad.append("the merge list's count is not the number of merges it names")
    fp = [c[0] for c in ri if "." not in c[0]]
    if not mb or ("the %d first-parent rows among them (%s) are brought by no merge" % (len(fp), _and(fp))) not in " ".join(mb.group(2).split()):
        bad.append("the first-parent rows brought by no merge are not the table's %s" % fp)
    merges = [c for c in rows if _classes(c)[0] == "MERGE"]
    lead = ("the %d commits of `git rev-list dd1aed00..%s` (%d commits, %d merges) change what cx46 read, or carry another row's change "
            "into a file of the reviewed tree, in %d commits classed REVIEWED-INPUT CHANGED" % (len(rows), TIP[:8], len(rows) - len(merges),
                                                                                              len(merges), len(ri)))
    if lead not in flat:
        bad.append("the bound statement's commit counts are not the table's")
    kinds_line = ("%d narrow, tighten or restate a state to a weaker claim, %d do not only narrow, and %d re-adopts the P0 list; %d merges "
                  "bring them. None of the %d was read" % (counts.get("narrow", -1), counts.get("not only", -1), counts.get("re-adopt", -1),
                                                           len(nm), len(ri)))
    if kinds_line not in flat:
        bad.append("the bound statement's kinds are not the lists' %r" % kinds_line)
    first = Counter(_classes(c)[0] for c in rows)
    parts = ["%d merges (the %d above among them)" % (first["MERGE"], len(nm)), "%d record text" % first["RECORD TEXT"],
             "%d tests" % first["TEST"]] + (["%d generator text" % first["GENERATOR DATA (text)"]] if first["GENERATOR DATA (text)"] else []) + \
        ["%d digest re-pins" % first["DIGEST RE-PIN"], "%d tooling" % first["TOOLING"]]
    other = "The other %d rows are classed as" % (len(rows) - len(ri))
    if other not in flat or (": " + ", ".join(parts[:-1]) + " and " + parts[-1] + ";") not in flat:
        bad.append("the bound statement's other rows are not the table's %d (%s)" % (len(rows) - len(ri), parts))
    if "transfers no engineering verdict to the %d changed rows" % len(ri) not in flat:
        bad.append("the bound statement's last count is not %d" % len(ri))
    return bad


def _and(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def p_merge_list(text, order):
    """The merges that bring REVIEWED-INPUT CHANGED rows, recomputed from git: a merge brings the rows of
    `git rev-list <first parent>..<second parent> ^dd1aed00`."""
    bad = []
    rows = [c for c in _rows(text) if not _placeholder_row(c)]
    ri = {_sha_cell(c)[1]: c[0] for c in rows if _classes(c)[0] == RIC}
    want = []
    for num, sha, ps, _d, _s, _n in order:
        if len(ps) > 1:
            br = set(_git("rev-list", "%s..%s" % (ps[0], ps[1]), "^" + BASE).split())
            hit = sorted((ri[s] for s in br if s in ri), key=lambda x: [int(y) for y in x.split(".")])
            if hit:
                want.append((sha[:8], hit))
    sec = text.split("\n## 2. ", 1)[1]
    mb = re.search(r"- \*\*Merges that bring `REVIEWED-INPUT CHANGED` rows \((\d+)\):\*\*(.*?)(?=\n- \*\*)", sec, re.S)
    if not mb:
        return ["the merge list is missing"]
    got = [(s, re.findall(r"\d+(?:\.\d+)?", rr)) for s, rr in re.findall(r"`([0-9a-f]{8})` \(((?:rows )?[\d., and]+)\)", " ".join(mb.group(2).split()))]
    if got != want:
        bad.append("the merge list is not git's: %s" % want)
    return bad


def p_rule(text, s30_lines):
    """The class is set 30's line 11 quoted verbatim, read as ruled; W39's earlier rule sentence is not the rule."""
    bad = []
    if len(s30_lines) < 11 or not s30_lines[10].startswith("- `REVIEWED-INPUT CHANGED`:"):
        return ["set 30's record has no REVIEWED-INPUT CHANGED rule at its line 11"]
    want = "(`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`):\n\n> " + s30_lines[10] + "\n"
    if want not in text:
        bad.append("the rule paragraph does not quote set 30's line 11 verbatim")
    if "reading A" not in text.split("## 1. ", 1)[0] or "set 30's row 26" not in text.split("## 1. ", 1)[0]:
        bad.append("the rule paragraph does not state reading A and its consequence for set 30's row 26")
    if "a reviewed input is a file cx46 read. This table" in text:
        bad.append("W39's earlier rule sentence is still given as the rule")
    return bad


def p_counts(texts, order):
    bad = []
    t = texts[CLASS]
    n = len(order)
    merges = sum(1 for o in order if len(o[2]) > 1)
    fp = sum(1 for o in order if "." not in o[0])
    files = len(_git("diff", "--name-only", BASE, TIP).split())
    delta = len(set(_git("diff", "--name-only", CX45, REVIEWED).split()))
    inrev = len([f for f in _git("diff", "--name-only", BASE, TIP).split() if f in _reviewed()])
    want = ["`git rev-list --count dd1aed00..%s` prints %d: %d commits and %d merges" % (TIP[:8], n, n - merges, merges),
            "`--first-parent` prints %d" % fp, "the other %d are the branch commits" % (n - fp),
            "the %d files of `git diff --name-only 06077cee 4d0ff8a2`" % delta,
            "%d of the range's %d changed files are in that set" % (inrev, files)]
    for w in want:
        if w not in " ".join(t.split()):
            bad.append("CLASSIFICATION.md does not read %r (git's numbers)" % w)
    r = " ".join(texts[RESULT].split())
    rows = [c for c in _rows(t) if not _placeholder_row(c)]
    first = Counter(_classes(c)[0] for c in rows)
    line = "%d commits of `git rev-list dd1aed00..%s` (%d commits and %d merges)" % (n, TIP[:8], n - merges, merges)
    if line not in r:
        bad.append("RESULT.md section 2 does not read %r" % line)
    cl = ("REVIEWED-INPUT CHANGED %d; RECORD TEXT %d; GENERATOR DATA (text) %d; TEST %d; DIGEST RE-PIN %d; MERGE %d; TOOLING %d; total %d"
          % tuple([first[k] for k in FIXED] + [len(rows)]))
    if cl not in r:
        bad.append("RESULT.md section 2's class counts are not the table's: %r" % cl)
    ri = first[RIC]
    r73 = sum(1 for c in rows if int(c[0].split(".")[0]) <= 30 and _classes(c)[0] == RIC)
    for w in ("over the %d commits to `f0748b49` alone, REVIEWED-INPUT CHANGED %d)" % (sum(1 for c in rows if int(c[0].split(".")[0]) <= 30), r73),
              "**None of the %d REVIEWED-INPUT CHANGED commits" % ri, "Its %d REVIEWED-INPUT CHANGED commits" % ri,
              "; %d REVIEWED-INPUT CHANGED (set 30's rule, reading A), UNREVIEWED since cx46;" % ri,
              "%d commits classified over `dd1aed00..%s`; %d REVIEWED-INPUT CHANGED" % (len(rows), TIP[:8], ri),
              "Targeted verification of the %d unreviewed changes of section 2" % ri, "and this set's %d);" % ri,
              "REVIEWED-INPUT CHANGED %d of %d." % (ri, len(rows)), "over the %d to `%s`, %d)" % (len(rows), TIP[:8], ri + 3),
              "It classes each of the %d commits" % len(rows)):
        if w not in r:
            bad.append("RESULT.md does not read %r (the table's count)" % w)
    pt = " ".join(texts[PATCH].split())
    for w, k in (("counts %d commits that change what cx46 read or carry another row's change" % ri, 2),
                 ("Set 31 adds its own: %d commits that change what cx46 read or carry another row's change" % ri, 2)):
        if pt.count(w) != k:
            bad.append("ENTRY-PAGES.patch.md does not read %r %d times (the table's count)" % (w, k))
    for sha, label in (("aed4bd23", "The commit** `aed4bd23` (%d files"), ("562edf6a", "The commit** `562edf6a` (%d files"),
                       ("31928583", "The commit** `31928583` (%d files")):
        k = len(_git("show", "--name-only", "--format=", sha).split())
        if label % k not in r:
            bad.append("RESULT.md's file count of %s is not git's %d" % (sha, k))
    for a, b, span in (("10:59:11", "12:30:22", "1 h 31 min 11 s"), ("12:41:57", "15:09:03", "2 h 27 min 6 s"),
                       ("12:24:18", "15:10:11", "2 h 45 min 53 s"), ("16:14:39", "18:02:33", "1 h 47 min 54 s"),
                       ("16:14:39", "18:10:37", "1 h 55 min 58 s"), ("15:22:20", "15:57:50", "35 min 30 s"),
                       ("15:15:17", "15:58:12", "42 min 55 s"), ("18:25:14", "18:58:29", "33 min 15 s"),
                       ("18:11:26", "18:59:12", "47 min 46 s")):
        s = [int(x) for x in a.split(":")]
        e = [int(x) for x in b.split(":")]
        d = (e[0] - s[0]) * 3600 + (e[1] - s[1]) * 60 + e[2] - s[2]
        got = ("%d h " % (d // 3600) if d >= 3600 else "") + "%d min %d s" % (d % 3600 // 60, d % 60)
        if got != span or span not in r:
            bad.append("the elapsed time %s to %s is not %s" % (a, b, span))
    return bad


def p_commits_named(texts):
    bad = []
    hist = set(_git("rev-list", TIP).split())
    cand = _candidate(texts[CLASS])
    if cand and not p_candidate_row(texts[CLASS]):
        hist.add(cand)                         # the candidate the fill named (main is fast-forwarded to it: PROMOTED too)
    else:
        cand = None
    for name, t in texts.items():
        if "/inputs/" in name:
            continue
        for tok in set(HEXTOK.findall(t)):
            if len(tok) not in (8, 40):
                continue                       # 12- and 16-character tokens are file digests, not commits
            full = [s for s in hist if s.startswith(tok)]
            if len(full) == 1:
                continue
            # the adoption commit, which the fill's second run writes into the patch rows (W69, 6 October 2026: a simulated second
            # run named it and this predicate refused it): accepted in the patch only, only once the candidate is named, and only
            # when it descends from the candidate (the adoption merges the candidate before its commit, FREEZE-PLAN step 12a)
            if name == PATCH and cand and _has(tok) and subprocess.run(
                    ["git", "-C", REPO, "merge-base", "--is-ancestor", cand, tok], capture_output=True).returncode == 0:
                continue
            out = [s for s in OUTSIDE if s.startswith(tok)]
            if out:
                if _has(out[0]) and _git("cat-file", "-t", out[0]).strip() != "commit":
                    bad.append("%s: %s is not a commit" % (name, tok))
                continue
            bad.append("%s: `%s` names no commit of this branch's history and is not declared outside it" % (name, tok))
    return bad


def p_quotes(texts):
    bad = []
    for name, t in texts.items():
        for sha, path, n, q in GIT_ANCHOR.findall(t):
            q = q.replace("\\|", "|")
            if not _has(sha):
                if any(s.startswith(sha) for s in OUTSIDE):
                    continue
                bad.append("%s: %s is not in this repository" % (name, sha))
                continue
            lines = _show(sha, path)
            if int(n) > len(lines) or q not in lines[int(n) - 1]:
                bad.append("%s: %r is not on %s:%s:%s" % (name, q[:60], sha[:8], path, n))
        for path, n, q in COPY_ANCHOR.findall(t):
            lines = _read(path).split("\n")
            if int(n) > len(lines) or q.replace("\\|", "|") not in lines[int(n) - 1]:
                bad.append("%s: %r is not on %s:%s" % (name, q[:60], path, n))
    return bad


def p_copies(src_text):
    bad = []
    rows = [l.split("\t") for l in src_text.split("\n") if l.count("\t") == 3]
    if len(rows) != 3:
        bad.append("SOURCES.txt names %d copies, not 3" % len(rows))
    for copy, source, blob, sha in rows:
        p = os.path.join(REPO, REC, "inputs", copy)
        data = open(p, "rb").read() if os.path.isfile(p) else b""
        if hashlib.sha256(data).hexdigest() != sha:
            bad.append("%s: its sha256 is not the one SOURCES.txt records" % copy)
        if hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest() != blob:
            bad.append("%s: its git blob is not %s" % (copy, blob[:12]))
    return bad


def p_claims(result, assess_lines):
    bad = []
    for n, words in CLAIMS.items():
        if assess_lines[n - 1].rstrip() != words:
            bad.append("the assessment's line %d is not %r" % (n, words))
        if "`%s:%d` `%s`" % (ASSESS_COPY, n, words) not in result:
            bad.append("RESULT.md does not quote line %d verbatim: %r" % (n, words))
    sec = result.split("\n## 6. ", 1)[1].split("\n## 7. ", 1)[0]
    for claim, state in (("Engineering-handover readiness", "READY AS A DESK PACKAGE OF OPEN ITEMS"),
                         ("Power-design closure", "BLOCKED"), ("Fabrication release", "BLOCKED")):
        if "| %s | %s |" % (claim, state) not in sec:
            bad.append("section 6 does not give %s as %s" % (claim, state))
    if "**Set 31 closes NO power item.**" not in sec or "**Layer 4's DESK gate stays NOT PASSED**" not in sec:
        bad.append("section 6 does not say that set 31 closes no power item and the DESK gate stays NOT PASSED")
    for wrong in ("DESK gate: PASSED", "DESK gate PASSED", "closure: CLOSED", "release: RELEASED", "Set 31 closes the"):
        if wrong in result:
            bad.append("RESULT.md reads %r" % wrong)
    return bad


def _patch_rows(text):
    rows = []
    for blk in re.split(r"\n### ", text)[1:]:
        head = blk.split("\n", 1)[0]
        m = re.match(r"([SU]-\d\d)\. `([^`]+)`, (?:after )?line (\d+):", head)
        olds = re.findall(r"Old text:\n```text\n(.*?)\n```", blk, re.S)
        news = re.findall(r"New text:\n```text\n(.*?)\n```", blk, re.S)
        rows.append((m.groups() if m else (head, None, None), olds, news, "\nBasis: " in blk))
    return rows


def p_patch(text):
    bad = []
    rows = _patch_rows(text)
    ids = [r[0][0] for r in rows]
    if ids != ["S-%02d" % i for i in range(1, 12)] + ["U-%02d" % i for i in range(1, 14)]:
        bad.append("the patch rows are not S-01 to S-11 and U-01 to U-13: %s" % ids)
    copies = {"v2/docs/handover/START-HERE.md": REC + "/inputs/START-HERE-eff28be3.md",
              "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md": REC + "/inputs/SUPPLIER-HANDOVER-eff28be3.md"}
    for (rid, path, n), olds, news, basis in rows:
        if path not in copies or len(olds) != 1 or len(news) != 1 or not basis:
            bad.append("%s: not one file, one old text, one new text and a basis" % rid)
            continue
        old, new = olds[0], news[0]
        lines = _read(copies[path]).split("\n")
        if "\n" in old or lines[int(n) - 1].count(old) != 1:
            bad.append("%s: the old text is not once on line %s of %s" % (rid, n, path))
        if new == old:
            bad.append("%s: the new text does not differ" % rid)
        if "after line" in text.split("### " + rid, 1)[1].split("\n", 1)[0] and not new.startswith(old + "\n"):
            bad.append("%s: an insertion row whose new text does not begin with the old line" % rid)
    return bad


def p_logs(texts, runs):
    bad = []
    for name, t in texts.items():
        for rel, n, entry, q in RUN_ANCHOR.findall(t):
            p = os.path.join(runs, rel)
            if not os.path.isfile(p):
                bad.append("%s: _runs/%s is missing" % (name, rel))
                continue
            body = open(p, encoding="utf-8", errors="replace").read()
            if n:
                lines = body.split("\n")
                if int(n) > len(lines) or q not in lines[int(n) - 1]:
                    bad.append("%s: _runs/%s:%s does not read %r" % (name, rel, n, q[:60]))
            elif entry:
                if entry not in body or q not in body:
                    bad.append("%s: _runs/%s has no entry %r carrying %r" % (name, rel, entry[:40], q[:40]))
            elif q not in body:
                bad.append("%s: _runs/%s does not carry %r" % (name, rel, q[:60]))
        for rel in set(RUN_PATH.findall(t)):
            if not os.path.isfile(os.path.join(runs, rel)):
                bad.append("%s: the cited log _runs/%s is missing" % (name, rel))
    return bad


# W91 (6 October 2026, W86's N1: no predicate pinned section 4a's statements; W86's mutants M20, the known-item paragraph removed, and
# M22, "FAILED its gate" softened, passed every test). Section 4a, from its heading to section 5's, must keep the first candidate's
# FAILED gate with suite_gate's last line, the sentence that it was not promoted and is superseded, and the coordinator's known item
# with the words that carry it (false for set 31's cache, to be corrected with set 32's single re-key). Matched on whitespace-normalised
# text between the two headings, never a fixed-size window.
SEC4A_HEAD = "### 4a. The first candidate `d0e283aa`: its gate FAILED; the correction, the re-take and the known item"
SEC4A = ("`<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:7` `suite_gate: FAIL`",
         "The first candidate FAILED its gate and was not promoted; it is SUPERSEDED by the second candidate below.",
         "**The coordinator's known item, carried and not corrected in set 31.**",
         "which is false for set 31's cache",
         "carried as a declared known item in the candidate's commit message and named here, to be corrected with set 32's single re-key")


def p_section4a(result):
    t = " ".join(result.split())
    a = t.find(SEC4A_HEAD)
    b = t.find("## 5. Compute", a + 1)
    if a < 0 or b < 0:
        return ["RESULT.md has no section 4a heading %r before section 5" % SEC4A_HEAD[:40]]
    s = t[a:b]
    return ["section 4a does not read %r" % w[:70] for w in SEC4A if w not in s]


# W98 (7 October 2026, W86's N6): set 30's rule's first sentence asks each REVIEWED-INPUT CHANGED reason to name the cx46 item that
# read the changed value, or to say that none names it. Each of the 25 rows carries one clause after CX46_SEG; the clause names an item,
# a blocker or a finding with a quotation of cx46's line (`cx46:N` `words`, line N of the filed check as filed at CX46_AT), or says
# "no cx46 item". The number named is held to cx46's own numbering of that line (an item's three lines, a blocker's line, a finding's
# line); a clause that says "outside the 62" belongs to a row whose files include none of the 62, and such a row says so.
CX46 = "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
CX46_AT = "0d5f855e"                                       # cx46 filed as received (set 30's row 3), in this branch's history
CX46_SEG = "the cx46 item (W98, W86's N6): "
CX46_ANCHOR = re.compile(r"`cx46:(\d+)` `((?:[^`\\]|\\.)+)`")
CX46_NAMED = re.compile(r"\b(?:items?|blockers?|findings?) (\d+)(?: and (\d+))? \(`cx46:(\d+)`")


def _cx46_numbering(lines):
    """{line number: the numbers cx46 itself gives that line}: a classification entry's "item" line and the two after it (its class
    and evidence), a line of the blockers list ("N." or "N and M."), a line of the evidence list ("Finding N", "Findings N and M",
    "Findings N, M and K")."""
    num, where = {}, None
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if s.startswith('"blockers": ['):
            where = "b"
            continue
        if s.startswith('"evidence": ['):
            where = "e"
            continue
        if s.startswith("],") or s.startswith("]"):
            where = None
        m = re.match(r'"item": "(\d+)\. ', s)
        if m:
            for k in (i, i + 1, i + 2):
                num[k] = {int(m.group(1))}
            continue
        if where == "b":
            m = re.match(r'"(\d+)(?: and (\d+))?\. ', s)
            if m:
                num[i] = {int(x) for x in m.groups() if x}
        elif where == "e":
            m = re.match(r'"Findings? ((?:\d+)(?:(?:, | and )\d+)*)', s)
            if m:
                num[i] = {int(x) for x in re.findall(r"\d+", m.group(1))}
    return num


def p_cx46_items(text, cx_lines, order=None):
    bad = []
    num = _cx46_numbering(cx_lines)
    names = {o[1]: o[5] for o in order} if order else {}
    for c in _rows(text):
        if _placeholder_row(c):
            continue
        ric = _classes(c)[0] == RIC
        k = c[7].count(CX46_SEG)
        if ric and k != 1:
            bad.append("row %s is %s and has %d cx46-item clauses, not one" % (c[0], RIC, k))
            continue
        if not ric:
            if k:
                bad.append("row %s is not %s but carries a cx46-item clause" % (c[0], RIC))
            continue
        seg = c[7].split(CX46_SEG, 1)[1]
        if not CX46_NAMED.search(seg) and "no cx46 item" not in seg:
            bad.append("row %s's clause names no cx46 item and does not say that none names it" % c[0])
        s = _sha_cell(c)
        if names and s and s[1] in names:
            in62 = [n for n in names[s[1]] if n in _reviewed()]
            says = re.match(r"no cx46 item(?: read the file)?: outside the 62", seg) is not None
            if says and in62:
                bad.append("row %s says outside the 62 but touches %d of the 62" % (c[0], len(in62)))
            if not in62 and not says:
                bad.append("row %s touches none of the 62 and its clause does not open with no cx46 item: outside the 62" % c[0])
    for n, q in CX46_ANCHOR.findall(text):
        n = int(n)
        if n > len(cx_lines) or q.replace("\\|", "|") not in cx_lines[n - 1]:
            bad.append("%r is not on cx46's line %d" % (q[:60], n))
    for a, b, n in CX46_NAMED.findall(text):
        got = {int(a)} | ({int(b)} if b else set())
        if not got <= num.get(int(n), set()):
            bad.append("cx46's line %s is not numbered %s by cx46 (it reads %s)" % (n, sorted(got), sorted(num.get(int(n), set()))))
    return bad


# W98 (7 October 2026, W86's N2): RESULT.md's section 1 counts and the classification rows it names, its first-parent table, section 2's
# prose classes and the merge table's annotations, and the candidate as the fill wrote it into RESULT.md, LAYER-STATUS.md and the plan,
# each held to git or to the table (W86's mutants M16, M17, M23, M33 and M39 to M41 passed every test before).
LS = "v2/docs/handover/LAYER-STATUS.md"
PLAN = "v2/docs/EXECUTION-PLAN.md"
CLASS_RX = "(REVIEWED-INPUT CHANGED|RECORD TEXT|GENERATOR DATA \\(text\\)|TEST|DIGEST RE-PIN|MERGE|TOOLING)"


def _fp_rows(order):
    return {o[1]: int(o[0]) for o in order if "." not in o[0]}


def p_section1(result, order):
    bad = []
    sec = result.split("\n## 1. The candidate", 1)[1].split("\n## 2. ", 1)[0]
    fp = _fp_rows(order)
    fpl = [o[1] for o in order if "." not in o[0]]
    head, tail = sec.split("**The lineage's first-parent line**", 1)
    seen = 0
    for line in head.split("\n"):
        if not line.startswith("| ") or line.startswith("| Role ") or line.startswith("|---"):
            continue
        c = [x.strip() for x in CELL_SPLIT.split(line.strip())[1:-1]]
        src = re.search(r"`git rev-list --count dd1aed00\.\.([0-9a-f]{8})`", c[3])
        if not src:
            continue
        seen += 1
        full = re.search(r"`([0-9a-f]{40})`", c[1])
        cnt = re.search(r"(\d+) commits over the base", c[2])
        if not full or not full.group(1).startswith(src.group(1)) or not cnt:
            bad.append("section 1: the row for %s has no full sha, count or matching rev-list" % src.group(1))
            continue
        k = int(_git("rev-list", "--count", "%s..%s" % (BASE, full.group(1))).strip())
        if int(cnt.group(1)) != k:
            bad.append("section 1: %s reads %s commits over the base, git counts %d" % (src.group(1), cnt.group(1), k))
        for a, b in re.findall(r"\brows 1 to (\d+)\b|\brow (\d+)\b", c[2]):
            if int(a or b) != fp.get(full.group(1)):
                bad.append("section 1: %s names row %s, its row is %s" % (src.group(1), a or b, fp.get(full.group(1))))
    if seen < 1:
        bad.append("section 1 has no row with its rev-list count")
    m = re.search(r"the (\d+) numbered rows of `CLASSIFICATION.md`", " ".join(tail.split()))
    if not m or int(m.group(1)) != len(fpl):
        bad.append("section 1 does not read the %d numbered rows" % len(fpl))
    want, got = list(range(1, len(fpl) + 1)), []
    for line in tail.split("\n"):
        mm = re.match(r"\| (\d+)(?: to (\d+))? \| ([^|]+) \|", line)
        if not mm:
            continue
        a, b = int(mm.group(1)), int(mm.group(2) or mm.group(1))
        shas = re.findall(r"`([0-9a-f]{8})`", mm.group(3))
        exp = [s[:8] for s in fpl[a - 1:b]]
        ok = (shas == [exp[0], exp[-1]] and " to " in mm.group(3)) if len(exp) > 2 and " to " in mm.group(3) else shas == exp
        if not ok:
            bad.append("section 1's first-parent table: rows %s are not %s" % (mm.group(0)[2:20], exp))
        got += list(range(a, b + 1))
    if got != want:
        bad.append("section 1's first-parent table does not cover rows 1 to %d once each in order" % len(fpl))
    return bad


def p_section2_prose(result, text, order):
    bad = []
    rows = {c[0]: _classes(c)[0] for c in _rows(text) if not _placeholder_row(c)}
    sec = result.split("\n## 2. ", 1)[1].split("\n## 3. ", 1)[0]
    para = " ".join(sec.split("**The classification is bound by its path:**", 1)[1].split("\n\n", 1)[0].split())
    named = set()
    for a, b, cls in re.findall(r"\brows? (\d+)(?: and (\d+))?,(?: [^,;]+,)? (?:are both |is an? |is )" + CLASS_RX, para):
        for r in (a, b):
            if r:
                named.add(r)
                if rows.get(r) != cls:
                    bad.append("section 2 classes row %s %s, the table's first class is %s" % (r, cls, rows.get(r)))
    later = {k for k in rows if "." not in k and int(k) > 31}
    if named != later:
        bad.append("section 2's prose classes rows %s, not the rows after the merge of main %s" % (sorted(named), sorted(later)))
    fp = _fp_rows(order)
    blk = sec.split("**The adopted branches, in W22's merge order**", 1)[1].split("\n\n", 2)[1]
    seen = 0
    for line in blk.split("\n"):
        m = re.match(r"\| `([0-9a-f]{8})` \|", line)
        if not m:
            continue
        seen += 1
        full = [s for s in fp if s.startswith(m.group(1))]
        if len(full) != 1:
            bad.append("section 2: merge %s is not a first-parent row" % m.group(1))
            continue
        n = str(fp[full[0]])
        last = [x.strip() for x in CELL_SPLIT.split(line.strip())[1:-1]][-1]
        ann = set()
        for grp in re.findall(r"((?:\d+\.\d+)(?:(?:, | and )\d+\.\d+)*) \(REVIEWED-INPUT CHANGED\)", last):
            ann |= set(re.findall(r"\d+\.\d+", grp))
        exp = {k for k, v in rows.items() if k.startswith(n + ".") and v == RIC}
        if ann != exp:
            bad.append("section 2: merge %s's rows annotated REVIEWED-INPUT CHANGED %s, the table's %s" % (m.group(1), sorted(ann), sorted(exp)))
    if seen != 10:
        bad.append("section 2's merge table has %d merges, not W22's ten" % seen)
    return bad


FILLED = ((RESULT, r"\| INTEGRATED = CANDIDATE: the candidate commit \| `([^`]+)` \|", "__CANDIDATE__"),
          (RESULT, r"\| PROMOTED: main after the fast-forward \| `([^`]+)` \|", "__PROMOTED__"),
          (RESULT, r"\| The candidate commit \| `git log` on fnd/int31regen \| `([^`]+)` \|", "__CANDIDATE__"),
          (RESULT, r"\| Promotion: fast-forward of main, push, the mirror, the guard on main \| `[^`]*` \| `([^`]+)` \|", "__PROMOTED__"),
          (RESULT, r"a DESK candidate once promoted, `([^`]+)`\)", "__PROMOTED__"),
          (LS, r"CANDIDATE: `([^`]+)`, the commit the gated release suite", "__CANDIDATE__"),
          (PLAN, r"### Milestone, 6 October 2026: integration set 31 promoted as a DESK candidate \(main `([^`]+)`\)", "__CANDIDATE__"),
          (PLAN, r"\*\*Promoted:\*\* main `([^`]+)`, the candidate on fnd/int31regen", "__CANDIDATE__"))
PROMOTE_LOG = "int31/promote-2257.log"
PROMOTE_QUOTED = ((RESULT, r"`_runs/int31/promote-2257\.log: GitHub main at ([0-9a-f]{40})`"),
                  (PLAN, r"`GitHub main at ([0-9a-f]{40}) \(_runs/int31/promote-2257\.log\)`"))


def p_candidate_filled(texts):
    """The candidate as filled: before the fill (the table's candidate cell the token) every place keeps its token; after it, every
    place names row 36's own commit (the table's candidate cell, `p_candidate_row`) and the promotion log's line, as RESULT.md and the
    plan quote it, names the same commit. A mixed state, or another commit in any one place (W86's M23, M39 to M41), is refused."""
    bad = []
    cand = _candidate(texts[CLASS])
    if cand and p_candidate_row(texts[CLASS]):
        cand = None
    filled = cand is not None
    flat = {k: " ".join(v.split()) for k, v in texts.items()}
    for name, rx, tok in FILLED:
        hits = re.findall(rx, flat[name])
        if len(hits) != 1:
            bad.append("%s: %d places for %r, not one" % (name, len(hits), rx[:50]))
            continue
        v = hits[0]
        if not filled and v != tok:
            bad.append("%s: %r before the fill, not %s" % (name, v, tok))
        if filled and not (re.match(r"[0-9a-f]{8,40}$", v) and cand.startswith(v)):
            bad.append("%s: %r is not row 36's commit %s" % (name, v, cand[:12]))
    for name, rx in PROMOTE_QUOTED:
        hits = re.findall(rx, flat[name])
        if filled and hits != [cand]:
            bad.append("%s: the promotion log's line as quoted names %s, not row 36's %s" % (name, hits, cand[:12]))
        if not filled and hits:
            bad.append("%s quotes the promotion log's line before the fill" % name)
    return bad


def p_promote_log(texts, runs):
    """The promotion log itself (the coordinator's, outside the repository) names the commit RESULT.md and the plan quote."""
    p = os.path.join(runs, PROMOTE_LOG)
    if not os.path.isfile(p):
        return ["_runs/%s is missing" % PROMOTE_LOG]
    body = open(p, encoding="utf-8", errors="replace").read()
    got = set(re.findall(r"^(?:GitHub main at|main fast-forwarded to) ([0-9a-f]{40})$", body, re.M))
    quoted = {h for name, rx in PROMOTE_QUOTED for h in re.findall(rx, " ".join(texts[name].split()))}
    return [] if got and got == quoted else ["the promotion log names %s, the records quote %s" % (sorted(got), sorted(quoted))]


def _texts():
    return {RESULT: _read(RESULT), CLASS: _read(CLASS), PATCH: _read(PATCH), SOURCES: _read(SOURCES)}


def _mutant_refused(pred, texts, name, old, new, *extra):
    t = dict(texts)
    assert old in t[name], "the mutation's anchor %r is not in %s" % (old[:50], name)
    t[name] = t[name].replace(old, new, 1)
    assert pred(t, *extra), "%s passed a mutant (%r)" % (pred.__name__, new[:50])


# ---- tests ----

def t_the_records_carry_no_dash_and_open_with_their_state_lines():
    texts = _texts()
    assert not p_hygiene(texts), p_hygiene(texts)
    _mutant_refused(p_hygiene, texts, RESULT, "Set 31 closes NO power item", "Set 31 closes NO power item —")


def t_every_placeholder_is_a_declared_token():
    texts = _texts()
    assert not p_placeholders(texts), p_placeholders(texts)
    # anchors that stay after the fill (W69: the earlier anchors were tokens the fill removes); the refused value is unchanged
    _mutant_refused(p_placeholders, texts, RESULT, "**Set 31 closes NO power item.**", "**Set 31 closes NO power item.** `__GATE_LINE__`")
    first = texts[PATCH].split("\n", 1)[0]
    _mutant_refused(p_placeholders, texts, PATCH, first, first + " `__GATE__`")
    # W83: an undeclared token in row 36's class cell, and an unclassified row in place of row 36's sha cell
    r = [l for l in texts[CLASS].split("\n") if l.startswith("| 36 |")][0]
    _mutant_refused(p_placeholders, texts, CLASS, r, r.replace("| TEST |", "| TEST `__CLASS__` |", 1))
    _mutant_refused(p_placeholders, texts, CLASS, r, r.replace(r.split(" | ")[1], "`__CANDIDATE__`", 1))


def t_the_candidates_row_is_its_placeholder_or_the_filled_candidate():
    """W83: the candidate's cell in row 36 (TIP's row), its token or the row's own commit; refused elsewhere, twice or naming another."""
    _need_git()
    t = _read(CLASS)
    assert not p_candidate_row(t), p_candidate_row(t)
    r = [l for l in t.split("\n") if l.startswith("| 36 |")][0]
    r35 = [l for l in t.split("\n") if l.startswith("| 35 |")][0]
    cell = CAND_CELL.search(r).group(0)
    val = CAND_CELL.search(r).group(1)

    def filled(v):
        return t.replace(r, r.replace(cell, cell.replace("`%s`" % val, "`%s`" % v), 1), 1)
    assert not p_candidate_row(filled(TIP)) and not p_candidate_row(filled(TIP[:8])), "the filled candidate (row 36's own commit) was refused"
    assert p_candidate_row(filled(SUPERSEDED)), "a filled cell naming the superseded first candidate passed"
    assert p_candidate_row(filled("aa3322806da156d12f2b23dbe9fc98a8805926f0")), "a filled cell naming an earlier commit passed"
    assert p_candidate_row(filled("__PROMOTED__")), "a candidate's cell with another token passed"
    assert p_candidate_row(t.replace(r35, r35.replace(" | REVIEWED-INPUT CHANGED +", " " + cell + " | REVIEWED-INPUT CHANGED +", 1), 1)), \
        "a second candidate's cell (row 35) passed"
    moved = t.replace(r, r.replace(cell, "set 31's candidate", 1), 1)
    assert p_candidate_row(moved.replace(r35, r35.replace(" | REVIEWED-INPUT CHANGED +", " " + cell + " | REVIEWED-INPUT CHANGED +", 1), 1)), \
        "the candidate's cell moved to row 35 passed"
    assert p_candidate_row(t.replace(r, r.replace(r.split(" | ")[1], "`__CANDIDATE__`", 1), 1)), "an unclassified row passed"


def t_the_table_is_the_range_in_first_parent_order_with_gits_columns_and_classes():
    order = _order()
    t = _read(CLASS)
    bad = p_coverage(t, order) + p_columns(t, order)
    assert not bad, bad
    row = [l for l in t.split("\n") if l.startswith("| 2.2 |")][0]
    assert p_coverage(t.replace(row + "\n", "", 1), order), "a dropped row passed"
    assert p_columns(t.replace("| 2.2 |", "| 2.2 |", 1).replace("| TEST | one new module, `test_w5l8p.py`", "| TESTS | one new module, `test_w5l8p.py`", 1), order), \
        "a class outside the fixed set passed"
    r = [l for l in t.split("\n") if l.startswith("| 11 |")][0]
    assert p_columns(t.replace(r, r.replace("UNREVIEWED since cx46", "unreviewed"), 1), order), \
        "a reviewed row without UNREVIEWED since cx46 passed"
    r = [l for l in t.split("\n") if l.startswith("| 2.2 |")][0]
    m = r.replace("| TEST |", "| REVIEWED-INPUT CHANGED + TEST |", 1)[:-2] + "; second sentence: row 2.1, not in the delta cx46 read; UNREVIEWED since cx46 |"
    assert any("touches no file of the reviewed tree" in b for b in p_columns(t.replace(r, m, 1), order)), \
        "a REVIEWED-INPUT CHANGED row touching no file of the reviewed tree passed"
    r = [l for l in t.split("\n") if l.startswith("| 31.3 |")][0]
    assert p_columns(t.replace(r, r.replace("the file was not in the delta cx46 read (the 62 files); ", ""), 1), order), \
        "a carried change without its delta membership passed"
    r = [l for l in t.split("\n") if l.startswith("| 35 |")][0]       # W83: the first candidate touches five reviewed files
    assert p_columns(t.replace(r, r.replace("UNREVIEWED since cx46", "unreviewed"), 1), order), "row 35 without UNREVIEWED since cx46 passed"
    r = [l for l in t.split("\n") if l.startswith("| 36 |")][0]
    assert p_columns(t.replace(r, r.replace("| 21:48:00 |", "| 21:48:01 |", 1).replace("2026-10-06 21:48:00", "2026-10-06 21:48:01", 1), 1), order), \
        "row 36 with a date that is not git's passed"


def t_the_summary_and_the_bound_statement_are_the_tables():
    t = _read(CLASS)
    assert not p_summary(t), p_summary(t)
    rows = [c for c in _rows(t) if not _placeholder_row(c)]
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    ri = first[RIC]
    a = "| `TOOLING` | %d | %d |" % (first["TOOLING"], carry["TOOLING"])
    assert a in t, "the mutation's anchor %r is not in the summary" % a
    assert p_summary(t.replace(a, "| `TOOLING` | %d | %d |" % (first["TOOLING"] + 1, carry["TOOLING"]), 1)), "a wrong summary count passed"
    o = "The other %d rows are classed" % (len(rows) - ri)
    assert o in t, "the mutation's anchor %r is not in the table's statement" % o
    assert p_summary(t.replace(o, "The other %d rows are classed" % (len(rows) - ri - 1), 1)), "a wrong statement count passed"
    r = [l for l in t.split("\n") if l.startswith("| 31.3 |")][0]
    assert p_summary(t.replace(r, r.replace("| REVIEWED-INPUT CHANGED + RECORD TEXT |", "| RECORD TEXT |"), 1)), \
        "a re-classed row with the old counts passed"
    k = re.search(r"weaker claim \((\d+)\):\*\* `bf44eb8c`", t)
    assert k, "the mutation's anchor (the first kind's count) is not in the summary"
    assert p_summary(t.replace(k.group(0), k.group(0).replace("(%s)" % k.group(1), "(%d)" % (int(k.group(1)) - 1)), 1)), \
        "a wrong kind count passed"
    r = [l for l in t.split("\n") if l.startswith("| 33 |")][0]
    assert p_summary(t.replace(r, r.replace("| REVIEWED-INPUT CHANGED + RECORD TEXT + DIGEST RE-PIN + TEST |", "| DIGEST RE-PIN + TEST |"), 1)), \
        "row 33 re-classed with the old counts passed"
    # W83: row 35 re-classed as set 30 classed its row 44, with the counts left as they are
    r = [l for l in t.split("\n") if l.startswith("| 35 |")][0]
    assert p_summary(t.replace(r, r.replace("| REVIEWED-INPUT CHANGED + GENERATOR DATA (text) + DIGEST RE-PIN |",
                                            "| DIGEST RE-PIN + GENERATOR DATA (text) |"), 1)), "row 35 re-classed with the old counts passed"


def t_the_merge_list_is_gits():
    order = _order()
    t = _read(CLASS)
    assert not p_merge_list(t, order), p_merge_list(t, order)
    assert p_merge_list(t.replace("`16afba29` (3.1),\n  `0ed29a78`", "`0ed29a78`", 1), order), "a merge list missing 16afba29 passed"


def t_the_rule_is_set_30s_line_11_verbatim_read_as_ruled():
    _need_git()
    t = _read(CLASS)
    s30 = _show(S30, S30C)
    assert not p_rule(t, s30), p_rule(t, s30)
    assert p_rule(t.replace("is different now; the reason quotes", "is different now: the reason quotes", 1), s30), "a changed quote passed"
    assert p_rule(t.replace("set 30's row 26", "set 30's row 62"), s30), "a rule without row 26's consequence passed"


def t_every_count_typed_is_gits():
    texts = _texts()
    order = _order()
    assert not p_counts(texts, order), p_counts(texts, order)
    n, m = len(order), sum(1 for o in order if len(o[2]) > 1)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "prints %d: %d commits" % (n, n - m), "prints %d: %d commits" % (n, n - m - 1), order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "35 min 30 s", "35 min 31 s", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "1 h 31 min 11 s", "1 h 31 min 12 s", order)
    ri = Counter(_classes(c)[0] for c in _rows(texts[CLASS]) if not _placeholder_row(c))[RIC]
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "**None of the %d REVIEWED-INPUT" % ri,
                    "**None of the %d REVIEWED-INPUT" % (ri - 6), order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, PATCH, "Set 31 adds its own: %d commits" % ri, "Set 31 adds its own: 15 commits", order)


def t_every_commit_named_is_in_the_history_or_declared_outside_it():
    _need_git()
    texts = _texts()
    assert not p_commits_named(texts), p_commits_named(texts)
    _mutant_refused(p_commits_named, texts, RESULT, "`f0748b49`", "`f0748b4a`")


def t_every_quote_is_on_its_cited_line():
    _need_git()
    texts = _texts()
    assert not p_quotes(texts), p_quotes(texts)
    _mutant_refused(p_quotes, texts, CLASS, "`**One release for the five drafts.**`", "`**One release for the six drafts.**`")
    _mutant_refused(p_quotes, texts, RESULT, ":498` `\"Ready\" here means", ":497` `\"Ready\" here means")


def t_the_copies_are_mains_bytes_and_the_three_claims_are_quoted_verbatim():
    assert not p_copies(_read(SOURCES)), p_copies(_read(SOURCES))
    result = _read(RESULT)
    lines = _read(ASSESS_COPY).split("\n")
    assert not p_claims(result, lines), p_claims(result, lines)
    if os.path.isfile(os.path.join(REPO, ASSESS_TREE)):          # once main's adoption is merged into the lineage
        tree = _read(ASSESS_TREE).split("\n")
        assert not p_claims(result, tree), "the tree's assessment: %s" % p_claims(result, tree)
    assert p_claims(result.replace("| Power-design closure | BLOCKED |", "| Power-design closure | CLOSED |", 1), lines), \
        "a changed claim passed"
    assert p_claims(result, [l.replace("NOT PASSED", "PASSED") for l in lines]), "a changed assessment line passed"
    assert p_copies(_read(SOURCES).replace("\taf96a293", "\taf96a294", 1)), "a wrong sha256 passed"


def t_every_patch_row_reads_against_the_copied_page():
    t = _read(PATCH)
    assert not p_patch(t), p_patch(t)
    assert p_patch(t.replace("2026, set 30); sections 1 to 9\n```", "2026, set 30) sections 1 to 9\n```", 1)), \
        "an old text not on its line passed"
    assert p_patch(t.replace("### U-13.", "### U-14.", 1)), "a renumbered row passed"


def t_every_cited_log_exists_and_carries_its_quote():
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    if not os.path.isdir(os.path.join(runs, "int31")):
        raise Skip("the coordinator's logs (_runs) are not on this host")
    texts = _texts()
    assert not p_logs(texts, runs), p_logs(texts, runs)
    _mutant_refused(p_logs, texts, RESULT, "`round 1: 18 replaced`", "`round 1: 19 replaced`", runs)
    _mutant_refused(p_logs, texts, RESULT, "targeted-w41-1623.log:22` `round 1: 15 replaced`", "targeted-w41-1623.log:22` `round 1: 16 replaced`", runs)
    _mutant_refused(p_logs, texts, RESULT, "tests-w41-1802-f8.log:127` `tests: 124 passed", "tests-w41-1802-f8.log:127` `tests: 125 passed", runs)
    # W98 (W86's N2): the promotion log names the commit RESULT.md and the plan quote from it
    tp = dict(texts)
    tp[PLAN] = _read(PLAN)
    assert not p_promote_log(tp, runs), p_promote_log(tp, runs)
    tp[RESULT] = " ".join(tp[RESULT].split()).replace("promote-2257.log: GitHub main at " + TIP, "promote-2257.log: GitHub main at " + SUPERSEDED, 1)
    assert p_promote_log(tp, runs), "a quoted promotion line naming another commit passed against the log"


def t_section_4a_keeps_the_failed_gate_and_the_known_item():
    """W91 (W86's N1): the first candidate's FAILED gate and the coordinator's known item, each refused when softened or removed."""
    r = _read(RESULT)
    assert not p_section4a(r), p_section4a(r)
    m22 = "The first candidate FAILED its gate and was not promoted"
    assert m22 in r, "the mutation's anchor is not in RESULT.md"
    assert p_section4a(r.replace(m22, "The first candidate did not complete its gate and was not promoted", 1)), "a softened FAILED passed (M22)"
    a = r.index("**The coordinator's known item, carried and not corrected in set 31.**")
    b = r.index("**The second candidate.**", a)
    assert p_section4a(r[:a] + r[b:]), "section 4a without the known-item paragraph passed (M20)"
    g = "\n- `<worktrees>/_runs/int31s1/superseded-d0e283aa/suite_gate.txt:7` `suite_gate: FAIL`"   # section 4a's bullet (section 1 cites it too)
    assert r.count(g) == 1, "the mutation's anchor (section 4a's last gate line) is not once in RESULT.md"
    assert p_section4a(r.replace(g, g.replace("FAIL`", "PASS`"), 1)), "a gate read PASS passed"
    k = "which is false for set 31's cache"
    assert p_section4a(r.replace(k, "which holds for set 31's cache", 1)), "the known item's falsity softened passed"


def t_each_reviewed_input_changed_row_names_its_cx46_item():
    """W98 (W86's N6): one clause per REVIEWED-INPUT CHANGED row naming cx46's item with its words, or that none names it; the words on
    their line of the filed check, the number cx46's own, "outside the 62" exactly for the rows that touch none of the 62."""
    _need_git()
    order = _order()
    t = _read(CLASS)
    cx = _show(CX46_AT, CX46)
    assert _read(CX46).split("\n") == cx, "the filed check is not its bytes at %s" % CX46_AT
    assert not p_cx46_items(t, cx, order), p_cx46_items(t, cx, order)
    r = [l for l in t.split("\n") if l.startswith("| 11 |")][0]
    seg = r.split(CX46_SEG, 1)[1].rsplit("; UNREVIEWED since cx46 |", 1)[0]
    assert p_cx46_items(t.replace("; " + CX46_SEG + seg, "", 1), cx, order), "a REVIEWED-INPUT CHANGED row without its clause passed"
    r = [l for l in t.split("\n") if l.startswith("| 2.2 |")][0]
    assert p_cx46_items(t.replace(r, r[:-2] + "; " + CX46_SEG + "no cx46 item |", 1), cx, order), "a TEST row with a clause passed"
    a = "item 15 (`cx46:188` `This disposition is correct"
    assert a in t, "the mutation's anchor (row 1.1's item) is not in the classification"
    assert p_cx46_items(t.replace(a, a.replace("item 15", "item 14"), 1), cx, order), "an item cx46 does not give that line passed"
    q = "`cx46:84` `The required rest voltage is 15.1308 V"
    assert q in t, "the mutation's anchor (row 4.1's quote) is not in the classification"
    assert p_cx46_items(t.replace(q, q.replace("15.1308", "15.1307"), 1), cx, order), "a misquoted cx46 line passed"
    o = CX46_SEG + "no cx46 item: outside the 62 (neither"
    assert o in t, "the mutation's anchor (row 3.1's clause) is not in the classification"
    assert p_cx46_items(t.replace(o, CX46_SEG + "no cx46 item: in the 62 (neither", 1), cx, order), \
        "a row outside the 62 without saying so passed"
    r = [l for l in t.split("\n") if l.startswith("| 12 |")][0]
    assert p_cx46_items(t.replace(r, r.replace(CX46_SEG + "no cx46 item:", CX46_SEG + "no cx46 item: outside the 62;", 1), 1), cx, order), \
        "outside the 62 said of a row that touches the 62 passed"
    assert p_cx46_items(t.replace(o, CX46_SEG + "none: outside the 62 (neither", 1), cx, order), \
        "a clause that neither names an item nor says no cx46 item passed"


def t_result_section_1_counts_are_gits():
    """W98 (W86's N2): section 1's commits over the base (W86's M16, M17), the classification rows it names, the numbered rows and the
    first-parent table, each recomputed from git."""
    order = _order()
    r = _read(RESULT)
    assert not p_section1(r, order), p_section1(r, order)
    for old in ("106 commits over the base, classified (section 2, row 36)", "105 commits over the base (row 35 of the classification)"):
        assert r.count(old) == 1, "the mutation's anchor %r is not once in RESULT.md" % old
        n = int(old.split()[0])
        assert p_section1(r.replace(old, old.replace(str(n), str(n + 1), 1), 1), order), "a count that is not git's passed (%d)" % n
    old = "(row 35 of the classification)"
    assert p_section1(r.replace(old, "(row 34 of the classification)", 1), order), "a classification row that is not the revision's passed"
    old = "the 36 numbered rows of `CLASSIFICATION.md`"
    assert old in r, "the mutation's anchor %r is not in RESULT.md" % old
    assert p_section1(r.replace(old, old.replace("36", "35"), 1), order), "a wrong numbered-row count passed"
    old = "| 35 | `d0e283aa` |"
    assert old in r, "the mutation's anchor %r is not in RESULT.md" % old
    assert p_section1(r.replace(old, "| 35 | `aa332280` |", 1), order), "a first-parent row naming another commit passed"


def t_result_section_2_prose_classes_are_the_tables():
    """W98 (W86's N2): section 2's prose classes of rows 32 to 36 (W86's M33) and the merge table's REVIEWED-INPUT CHANGED
    annotations, each the classification's first class."""
    order = _order()
    r = _read(RESULT)
    t = _read(CLASS)
    assert not p_section2_prose(r, t, order), p_section2_prose(r, t, order)
    old = "row 35, the re-key's dependents regenerated, is REVIEWED-INPUT CHANGED"
    assert old in r, "the mutation's anchor (M33) is not in RESULT.md"
    assert p_section2_prose(r.replace(old, old.replace("is REVIEWED-INPUT CHANGED", "is a DIGEST RE-PIN"), 1), t, order), \
        "row 35's prose class changed passed (M33)"
    old = "row 34, is a DIGEST RE-PIN"
    assert p_section2_prose(r.replace(old, "row 34, is REVIEWED-INPUT CHANGED", 1), t, order), "row 34's prose class changed passed"
    old = "| 4.1 and 4.4 (REVIEWED-INPUT CHANGED), 4.2, 4.3, 4.5 |"
    assert old in r, "the mutation's anchor (merge 4's rows) is not in RESULT.md"
    assert p_section2_prose(r.replace(old, "| 4.1 (REVIEWED-INPUT CHANGED), 4.2, 4.3, 4.4, 4.5 |", 1), t, order), \
        "a merge's annotation missing a REVIEWED-INPUT CHANGED row passed"
    r31 = [l for l in t.split("\n") if l.startswith("| 35 |")][0]
    assert p_section2_prose(r, t.replace(r31, r31.replace("| REVIEWED-INPUT CHANGED + GENERATOR DATA (text) + DIGEST RE-PIN |",
                                                         "| DIGEST RE-PIN + GENERATOR DATA (text) |"), 1), order), \
        "row 35 re-classed in the table with the prose left passed"


def t_the_filled_candidate_is_row_36s_commit_everywhere():
    """W98 (W86's N2): the candidate the fill wrote into RESULT.md, LAYER-STATUS.md and the plan is row 36's own commit and the
    promotion log's line as quoted; the first candidate in any one place (W86's M23, M39, M40, M41) is refused."""
    _need_git()
    texts = dict(_texts())
    texts[LS] = _read(LS)
    texts[PLAN] = _read(PLAN)
    assert not p_candidate_filled(texts), p_candidate_filled(texts)
    for name, rx, tok in FILLED:
        flat = " ".join(texts[name].split())
        m = re.search(rx, flat)
        assert m, "the anchor %r is not in %s" % (rx[:40], name)
        whole, val = m.group(0), m.group(1)
        t = dict(texts)
        t[name] = flat.replace(whole, whole.replace("`%s`" % val, "`%s`" % SUPERSEDED[:8], 1), 1)
        assert p_candidate_filled(t), "%s naming the first candidate passed (%r)" % (name, rx[:40])
        t[name] = flat.replace(whole, whole.replace("`%s`" % val, "`%s`" % ("__CANDIDATE__" if val != "__CANDIDATE__" else TIP[:8]), 1), 1)
        assert p_candidate_filled(t), "%s in a mixed state passed (%r)" % (name, rx[:40])
    for name, rx in PROMOTE_QUOTED:
        flat = " ".join(texts[name].split())
        m = re.search(rx, flat)
        if m:
            t = dict(texts)
            t[name] = flat.replace(m.group(0), m.group(0).replace(m.group(1), SUPERSEDED, 1), 1)
            assert p_candidate_filled(t), "%s quoting another commit as promoted passed" % name


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


test_the_records_carry_no_dash_and_open_with_their_state_lines = _pytest(t_the_records_carry_no_dash_and_open_with_their_state_lines)
test_every_placeholder_is_a_declared_token = _pytest(t_every_placeholder_is_a_declared_token)
test_the_candidates_row_is_its_placeholder_or_the_filled_candidate = _pytest(t_the_candidates_row_is_its_placeholder_or_the_filled_candidate)
test_the_table_is_the_range_in_first_parent_order_with_gits_columns_and_classes = _pytest(
    t_the_table_is_the_range_in_first_parent_order_with_gits_columns_and_classes)
test_the_summary_and_the_bound_statement_are_the_tables = _pytest(t_the_summary_and_the_bound_statement_are_the_tables)
test_the_merge_list_is_gits = _pytest(t_the_merge_list_is_gits)
test_the_rule_is_set_30s_line_11_verbatim_read_as_ruled = _pytest(t_the_rule_is_set_30s_line_11_verbatim_read_as_ruled)
test_every_count_typed_is_gits = _pytest(t_every_count_typed_is_gits)
test_every_commit_named_is_in_the_history_or_declared_outside_it = _pytest(t_every_commit_named_is_in_the_history_or_declared_outside_it)
test_every_quote_is_on_its_cited_line = _pytest(t_every_quote_is_on_its_cited_line)
test_the_copies_are_mains_bytes_and_the_three_claims_are_quoted_verbatim = _pytest(
    t_the_copies_are_mains_bytes_and_the_three_claims_are_quoted_verbatim)
test_every_patch_row_reads_against_the_copied_page = _pytest(t_every_patch_row_reads_against_the_copied_page)
test_every_cited_log_exists_and_carries_its_quote = _pytest(t_every_cited_log_exists_and_carries_its_quote)
test_section_4a_keeps_the_failed_gate_and_the_known_item = _pytest(t_section_4a_keeps_the_failed_gate_and_the_known_item)
test_each_reviewed_input_changed_row_names_its_cx46_item = _pytest(t_each_reviewed_input_changed_row_names_its_cx46_item)
test_result_section_1_counts_are_gits = _pytest(t_result_section_1_counts_are_gits)
test_result_section_2_prose_classes_are_the_tables = _pytest(t_result_section_2_prose_classes_are_the_tables)
test_the_filled_candidate_is_row_36s_commit_everywhere = _pytest(t_the_filled_candidate_is_row_36s_commit_everywhere)
