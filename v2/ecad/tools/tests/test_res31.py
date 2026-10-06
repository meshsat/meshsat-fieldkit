#!/usr/bin/env python3
"""Set 31's result record (MESHSAT-1357, 6 October 2026, W39): `v2/docs/records/int31/RESULT.md`, its classification
`CLASSIFICATION.md` and the entry pages' rows `ENTRY-PAGES.patch.md` hold what they type.

What fails here: a commit of `dd1aed00..TIP` missing, doubled or out of the first-parent order with each merge's branch commits under
it; a short sha that is not its full sha's prefix; a date, subject or file count that is not git's; a class outside the brief's fixed
set, a merge not classed MERGE or a MERGE that is not a merge; a row that touches a file cx46 read without the words "UNREVIEWED since
cx46", or a REVIEWED-INPUT CHANGED row that touches none; summary counts or the bound statement's numbers that are not the table's; a
count typed in the records that is not git's; a commit named that this repository does not hold (outside the declared list of main's
commits); a quote that is not on its cited line at its revision or in its verbatim copy; the three claims not quoted verbatim from the
assessment; a placeholder outside the declared tokens; a patch row whose old text is not on its line of the copied page; an em or en
dash. Each predicate is also run on a mutant it must refuse.

The coordinator's logs (`<worktrees>/_runs`, outside the repository) are read by ONE test, which raises Skip where they are absent
(a rented box): run it in the runner pass (the record's section 8). When the coordinator adds the rows after `f0748b49` at the
adoption, TIP below moves with them.

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
TIP = "f0748b490e183082b2da4361a5d24ee60d5fba40"           # set 31's lineage when the record was written
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
CX45 = "06077cee"                                           # the delta cx46 read: git diff 06077cee 4d0ff8a2 (its line 17)
L4E9_EXTRA = ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l4e9/l4e9_power_path.out")
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT", "GENERATOR DATA (text)", "TEST", "DIGEST RE-PIN", "MERGE", "TOOLING")
DECLARED = ("__CANDIDATE__", "__REKEY__", "__PROMOTED__", "__GATE__", "__ADOPTION__")
PATCH_TOKENS = ("__PROMOTED__", "__ADOPTION__")
# main's commits named by the record, not in this branch's history until main is merged into set 31's lineage
OUTSIDE = {"eff28be3b80f882db545a849b0da1def0217f63d": "main's follow-up after set 30's adoption, the copies' source",
           "836f711b406be48d9eb58c9cf6f7491fbcf7c5ec": "set 30's adoption commit on main"}
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


def _placeholder_row(cells):
    return bool(re.match(r"`__[A-Z]+__`$", cells[1]))


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


def p_placeholders(texts):
    bad = []
    for name, t in texts.items():
        for tok in set(PH.findall(t)):
            if tok not in DECLARED:
                bad.append("%s: %s is not a declared placeholder" % (name, tok))
            if name == PATCH and tok not in PATCH_TOKENS:
                bad.append("%s: %s is not one of the patch's two tokens" % (name, tok))
    for c in _rows(texts[CLASS]):
        if _placeholder_row(c) and (c[6] != "not determined" or c[2] != "not determined"):
            bad.append("the placeholder row %s carries a class or a date" % c[1])
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
        if rv and "UNREVIEWED since cx46" not in c[7]:
            bad.append("%s touches %d reviewed file(s) and does not say UNREVIEWED since cx46" % (sha[:8], len(rv)))
        if cls[0] == "REVIEWED-INPUT CHANGED" and not rv:
            bad.append("%s is REVIEWED-INPUT CHANGED but touches no file cx46 read" % sha[:8])
    return bad


def p_summary(text):
    bad = []
    rows = [c for c in _rows(text) if not _placeholder_row(c)]
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    sec = text.split("\n## 2. ", 1)[1]
    for k in FIXED:
        m = re.search(r"^\| `%s` \| (\d+) \| (\d+) \|$" % re.escape(k), sec, re.M)
        if not m or int(m.group(1)) != first[k] or int(m.group(2)) != carry[k]:
            bad.append("the summary row of %s is not the table's (%d, %d)" % (k, first[k], carry[k]))
    m = re.search(r"^\| total \| (\d+) \|", sec, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the summary's total is not the table's %d" % len(rows))
    ri = [c for c in rows if _classes(c)[0] == "REVIEWED-INPUT CHANGED"]
    m = re.search(r"\*\*The `REVIEWED-INPUT CHANGED` rows: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?)\. By what", sec, re.S)
    if not m or int(m.group(1)) != len(ri):
        bad.append("the REVIEWED-INPUT CHANGED count line is not the table's %d" % len(ri))
    else:
        named = re.findall(r"`([0-9a-f]{8})`\s\(([\d.]+)\)", m.group(2))
        if named != [(_sha_cell(c)[0], c[0]) for c in ri]:
            bad.append("the REVIEWED-INPUT CHANGED list is not the table's rows in order")
    merges = [c for c in rows if _classes(c)[0] == "MERGE"]
    stmt = re.search(r"the (\d+) commits of `git rev-list dd1aed00\.\.f0748b49` \((\d+)\n?> ?commits, (\d+) merges\) change a file cx46 read in (\d+) commits", sec)
    if not stmt or [int(x) for x in stmt.groups()] != [len(rows), len(rows) - len(merges), len(merges), len(ri)]:
        bad.append("the bound statement's commit counts are not the table's")
    other = re.search(r"The other (\d+) rows change no", sec)
    if not other or int(other.group(1)) != len(rows) - len(ri):
        bad.append("the bound statement's other rows are not %d" % (len(rows) - len(ri)))
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
    want = ["`git rev-list --count dd1aed00..f0748b49` prints %d: %d commits and %d merges" % (n, n - merges, merges),
            "`--first-parent` prints %d" % fp, "the other %d are the branch commits" % (n - fp),
            "the %d files of `git diff --name-only 06077cee 4d0ff8a2`" % delta,
            "%d of the range's %d changed files are in that set" % (inrev, files)]
    for w in want:
        if w not in " ".join(t.split()):
            bad.append("CLASSIFICATION.md does not read %r (git's numbers)" % w)
    r = " ".join(texts[RESULT].split())
    rows = [c for c in _rows(t) if not _placeholder_row(c)]
    first = Counter(_classes(c)[0] for c in rows)
    line = ("73 commits of `git rev-list dd1aed00..f0748b49` (%d commits and %d merges)" % (n - merges, merges)).replace("73", str(n))
    if line not in r:
        bad.append("RESULT.md section 2 does not read %r" % line)
    cl = ("REVIEWED-INPUT CHANGED %d; RECORD TEXT %d; GENERATOR DATA (text) %d; TEST %d; DIGEST RE-PIN %d; MERGE %d; TOOLING %d; total %d"
          % tuple([first[k] for k in FIXED] + [len(rows)]))
    if cl not in r:
        bad.append("RESULT.md section 2's class counts are not the table's: %r" % cl)
    for sha, label in (("aed4bd23", "The commit** `aed4bd23` (%d files"), ("562edf6a", "The commit** `562edf6a` (%d files")):
        k = len(_git("show", "--name-only", "--format=", sha).split())
        if label % k not in r:
            bad.append("RESULT.md's file count of %s is not git's %d" % (sha, k))
    for a, b, span in (("10:59:11", "12:30:22", "1 h 31 min 11 s"), ("12:41:57", "15:09:03", "2 h 27 min 6 s"),
                       ("12:24:18", "15:10:11", "2 h 45 min 53 s")):
        s = [int(x) for x in a.split(":")]
        e = [int(x) for x in b.split(":")]
        d = (e[0] - s[0]) * 3600 + (e[1] - s[1]) * 60 + e[2] - s[2]
        if "%d h %d min %d s" % (d // 3600, d % 3600 // 60, d % 60) != span or span not in r:
            bad.append("the elapsed time %s to %s is not %s" % (a, b, span))
    return bad


def p_commits_named(texts):
    bad = []
    hist = set(_git("rev-list", TIP).split())
    for name, t in texts.items():
        if "/inputs/" in name:
            continue
        for tok in set(HEXTOK.findall(t)):
            if len(tok) not in (8, 40):
                continue                       # 12- and 16-character tokens are file digests, not commits
            full = [s for s in hist if s.startswith(tok)]
            if len(full) == 1:
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
    _mutant_refused(p_placeholders, texts, RESULT, "`__GATE__`", "`__GATE_LINE__`")
    _mutant_refused(p_placeholders, texts, PATCH, "`__ADOPTION__`", "`__GATE__`")


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


def t_the_summary_and_the_bound_statement_are_the_tables():
    t = _read(CLASS)
    assert not p_summary(t), p_summary(t)
    assert p_summary(t.replace("| `TOOLING` | 2 | 3 |", "| `TOOLING` | 3 | 3 |", 1)), "a wrong summary count passed"
    assert p_summary(t.replace("The other 59 rows change no", "The other 58 rows change no", 1)), "a wrong statement count passed"


def t_every_count_typed_is_gits():
    texts = _texts()
    order = _order()
    assert not p_counts(texts, order), p_counts(texts, order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "prints 73: 58 commits", "prints 73: 57 commits", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "1 h 31 min 11 s", "1 h 31 min 12 s", order)


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
test_the_table_is_the_range_in_first_parent_order_with_gits_columns_and_classes = _pytest(
    t_the_table_is_the_range_in_first_parent_order_with_gits_columns_and_classes)
test_the_summary_and_the_bound_statement_are_the_tables = _pytest(t_the_summary_and_the_bound_statement_are_the_tables)
test_every_count_typed_is_gits = _pytest(t_every_count_typed_is_gits)
test_every_commit_named_is_in_the_history_or_declared_outside_it = _pytest(t_every_commit_named_is_in_the_history_or_declared_outside_it)
test_every_quote_is_on_its_cited_line = _pytest(t_every_quote_is_on_its_cited_line)
test_the_copies_are_mains_bytes_and_the_three_claims_are_quoted_verbatim = _pytest(
    t_the_copies_are_mains_bytes_and_the_three_claims_are_quoted_verbatim)
test_every_patch_row_reads_against_the_copied_page = _pytest(t_every_patch_row_reads_against_the_copied_page)
test_every_cited_log_exists_and_carries_its_quote = _pytest(t_every_cited_log_exists_and_carries_its_quote)
