#!/usr/bin/env python3
"""Set 32's result record (MESHSAT-1357, 6 October 2026, W44): `v2/docs/records/int32/RESULT.md` and its classification
`CLASSIFICATION.md` hold what they type.

What fails here: a commit of set 32's two branch ranges missing, doubled or out of order; a short sha that is not its full sha's prefix; a
date, subject or file count that is not git's; a class outside W39's fixed set; a row that touches a file cx46 read without the words
"UNREVIEWED since cx46"; a REVIEWED-INPUT CHANGED row that touches no file of the reviewed tree (present at 4d0ff8a2), or one that
touches none of cx46's delta without classing a carried change with its source row and the delta membership; a rule paragraph that is not
set 30's line 11 verbatim (`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`, read as the coordinator ruled on 6 October 2026,
reading A), or that drops set 30's row 44 as the precedent, the wider reading's answer or the placeholder rows' note; summary counts, per-branch counts or the bound statement's
numbers that are not the table's; a count typed in the records that is not git's; a commit named that is in no history this record
reads; a quote that is not on its cited line at its revision; the three claims not quoted verbatim from the assessment; a placeholder
outside the five tokens the coordinator declared; an em or en dash. Each predicate is also run on a mutant it must refuse.

The coordinator's files (`<worktrees>/_runs`, outside the repository) are read by ONE test, which raises Skip where they are absent (a
rented box): run it in the runner pass (the record's section 8). The two branch tips below are the ones the record read; a commit a
branch gains later is outside these ranges, so the coordinator adds its row and moves the tip here at the adoption.

Read-only: git is read with `git log`, `git show`, `git diff`, `git rev-list`, `git merge-base`, `git ls-tree` and `git cat-file`;
nothing is written. No pytest is needed (tests/run.py runs the `t_` functions); `test_` aliases let pytest collect them."""
import os
import re
import subprocess
from collections import Counter

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = "v2/docs/records/int32"
RESULT = REC + "/RESULT.md"
CLASS = REC + "/CLASSIFICATION.md"
LINEAGE = "3057ae43f4fb7fc5e3d6282ce52d448c8ee27929"         # set 31's lineage, this record's base (the coordinator's INBOX)
BRANCHES = (("fnd/w34pdftext", "aed4bd234644c80fa494299b21099acf6d2454c1", "5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac"),
            ("fnd/s32small", "eff28be3b80f882db545a849b0da1def0217f63d", "7b7219a7d0a695b6b866435116905964a68f5578"))
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
CX45 = "06077cee"                                           # the delta cx46 read: git diff 06077cee 4d0ff8a2
L4E9_EXTRA = ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l4e9/l4e9_power_path.out")
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT", "GENERATOR DATA (text)", "TEST", "DIGEST RE-PIN", "MERGE", "TOOLING")
DECLARED = ("__S31_PROMOTED__", "__CANDIDATE__", "__REKEY__", "__GATE__", "__PROMOTED__")
# set 31's record draft, named by the record, on fnd/res31: in this branch's history only after set 31's adoption
OUTSIDE = {"4196e9dfbb125cc50b091bdea47a34e432162970": "fnd/res31's tip, set 31's RESULT and CLASSIFICATION drafts (W39)"}
ASSESS = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
S30 = "eff28be3b80f882db545a849b0da1def0217f63d"              # set 30's adopted classification, its rule at line 11
S30C = "v2/docs/records/int30/CLASSIFICATION.md"
RIC = "REVIEWED-INPUT CHANGED"
CLAIMS = {492: "### Layer 4's DESK gate: NOT PASSED",
          496: "### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
          500: "### Power-design closure: BLOCKED. Fabrication release: BLOCKED."}

GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
RUN_ANCHOR = re.compile(r"`<worktrees>/_runs/([^`:\s]+)(?::(\d+))?`(?:, entry \"([^\"]+)\",)? `([^`]+)`")
RUN_PATH = re.compile(r"`(?:<worktrees>/)?_runs/([\w./-]+\.(?:log|md|txt|sh|tsv))")
HEXTOK = re.compile(r"`([0-9a-f]{7,40})`")
PH = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
DASHES = ("\u2014", "\u2013")


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
    try:
        r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    return r.returncode == 0


def _need_git():
    for sha in (LINEAGE, REVIEWED) + tuple(b[1] for b in BRANCHES) + tuple(b[2] for b in BRANCHES):
        if not _has(sha):
            raise Skip("commit %s is not in this checkout" % sha[:8])


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
    """[(row number, branch, full sha, parents, date, subject, names)]: each branch's range oldest first, branch A then B."""
    if "order" in _C:
        return _C["order"]
    _need_git()
    out = []
    n = 0
    for name, base, tip in BRANCHES:
        for c in _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (base, tip)).split():
            n += 1
            ps = _git("rev-list", "--parents", "-n1", c).split()[1:]
            date, subj = _git("log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%ad%x09%s", c).rstrip("\n").split("\t", 1)
            names = _git("show", "--name-only", "--format=", c).split()
            out.append((str(n), name, c, ps, date, subj, names))
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


def _placeholder_row(cells):
    return bool(re.match(r"`__[A-Z0-9_]+__`$", cells[1]))


def _real(text):
    return [c for c in _rows(text) if not _placeholder_row(c)]


# ---- predicates: each returns a list of problems (empty when the record holds) ----

def p_hygiene(texts):
    bad = []
    for name, t in texts.items():
        if any(d in t for d in DASHES):
            bad.append("%s carries an em or en dash" % name)
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", t) if p.strip()]
        first = paras[1] if len(paras) > 1 else ""
        if not first.startswith("**DONE:**") or "**NOT DONE:**" not in first or "**NEXT:**" not in first:
            bad.append("%s: the paragraph after the title is not the DONE / NOT DONE / NEXT line" % name)
    return bad


def p_placeholders(texts):
    bad = []
    for name, t in texts.items():
        for tok in set(PH.findall(t)):
            if tok not in DECLARED:
                bad.append("%s: %s is not a declared placeholder" % (name, tok))
    for c in _rows(texts[CLASS]):
        if _placeholder_row(c) and (c[6] != "not determined" or c[2] != "not determined"):
            bad.append("the placeholder row %s carries a class or a date" % c[1])
    return bad


def p_coverage(text, order):
    bad = []
    want = [(o[0], o[2]) for o in order]
    got = []
    for c in _real(text):
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
        bad.append("the rows are not the two ranges in their order (missing or misnumbered %s, extra %s)" % (miss, extra))
    return bad


def p_columns(text, order):
    bad = []
    by = {o[2]: o for o in order}
    for c in _rows(text):
        s = _sha_cell(c)
        if not s or s[1] not in by:
            continue
        num, branch, sha, ps, date, subj, names = by[s[1]]
        if c[2] != date:
            bad.append("%s: date %r is not git's %r" % (sha[:8], c[2], date))
        if c[3].replace("\\|", "|") != subj:
            bad.append("%s: the subject is not git's" % sha[:8])
        if not c[4].startswith(branch + " ("):
            bad.append("%s: the branch cell does not name %s" % (sha[:8], branch))
        m = re.match(r"(\d+):", c[5])
        if not m or int(m.group(1)) != len(names):
            bad.append("%s: file count %r is not git's %d" % (sha[:8], c[5][:12], len(names)))
        cls = _classes(c)
        if any(k not in FIXED for k in cls) or len(set(cls)) != len(cls):
            bad.append("%s: a class outside the fixed set, or one twice: %s" % (sha[:8], cls))
        if (cls[0] == "MERGE") != (len(ps) > 1):
            bad.append("%s: MERGE and the commit's parents disagree" % sha[:8])
        rv = [n for n in names if n in _reviewed()]
        if rv and "UNREVIEWED since cx46" not in c[7]:
            bad.append("%s touches %d reviewed file(s) and does not say UNREVIEWED since cx46" % (sha[:8], len(rv)))
        if rv and ("(%d):" % len(rv)) not in c[7]:
            bad.append("%s: its reason does not count its %d reviewed file(s)" % (sha[:8], len(rv)))
        if cls[0] != RIC:
            continue
        if "UNREVIEWED since cx46" not in c[7]:
            bad.append("%s is %s and does not say UNREVIEWED since cx46" % (sha[:8], RIC))
        if not [n for n in names if n in _tree()]:
            bad.append("%s is %s but touches no file of the reviewed tree" % (sha[:8], RIC))
        carried = "second sentence" in c[7]
        if not rv and not carried:
            bad.append("%s is %s, touches none of cx46's delta and does not class a carried change" % (sha[:8], RIC))
        if carried and (not re.search(r"set 30's rows? \d+|\brows? \d+(?:\.\d+)?\b", c[7]) or "in the delta cx46 read" not in c[7]):
            bad.append("%s: a carried change without its source row or the delta membership" % sha[:8])
    return bad


def p_rule(text, s30_lines, tree_lines):
    """The class is set 30's line 11 quoted verbatim (the tree's copy equal to main's), read as ruled, with row 44 the precedent."""
    bad = []
    if len(s30_lines) < 68 or not s30_lines[10].startswith("- `REVIEWED-INPUT CHANGED`:"):
        return ["set 30's record has no REVIEWED-INPUT CHANGED rule at its line 11"]
    if tree_lines[:len(s30_lines)] != s30_lines:
        bad.append("the tree's copy of set 30's record is not main's at eff28be3")
    head = text.split("## 1. ", 1)[0]
    flat = " ".join(head.split())
    if "`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`):\n\n> " + s30_lines[10] + "\n" not in head:
        bad.append("the rule paragraph does not quote set 30's line 11 verbatim")
    for w in ("reading A", "set 30's row 44", "set 30's rows 1, 13 and 44 did not take it",
              "each placeholder row is classed under the second sentence when filled",
              "(1) set 30's rule covers a change carried into any file of the reviewed tree",
              "(2) set 30's rule requires each such reason to name the source row and whether the file was in the delta cx46 read"):
        if w not in flat:
            bad.append("the rule paragraph does not read %r" % w)
    if "no figure or verdict word moved" not in s30_lines[67]:
        bad.append("set 30's row 44 (line 68) does not read 'no figure or verdict word moved'")
    return bad


def p_summary(text):
    bad = []
    rows = _real(text)
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    sec = text.split("\n## 2. ", 1)[1]
    flat = " ".join(sec.replace("\n> ", "\n").split())
    for k in FIXED:
        m = re.search(r"^\| `%s` \| (\d+) \| (\d+) \|$" % re.escape(k), sec, re.M)
        if not m or int(m.group(1)) != first[k] or int(m.group(2)) != carry[k]:
            bad.append("the summary row of %s is not the table's (%d, %d)" % (k, first[k], carry[k]))
    m = re.search(r"^\| total \| (\d+) \|", sec, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the summary's total is not the table's %d" % len(rows))
    for name, _base, _tip in BRANCHES:
        br = [c for c in rows if c[4].startswith(name + " (")]
        f = Counter(_classes(c)[0] for c in br)
        part = ", ".join("%s %d" % (k, f[k]) for k in FIXED if f[k])
        want = "%s, %d rows: %s" % (name, len(br), part)
        if want not in flat:
            bad.append("the per-branch line does not read %r" % want)
    touch = [c for c in rows if "UNREVIEWED since cx46" in c[7]]
    m = re.search(r"\*\*The rows that touch a file cx46 read: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?); (\d+) files", flat)
    if not m or int(m.group(1)) != len(touch):
        bad.append("the touching-rows line is not the table's %d" % len(touch))
    else:
        named = re.findall(r"`([0-9a-f]{8})` \(([\d.]+)\)", m.group(2))
        if named != [(_sha_cell(c)[0], c[0]) for c in touch]:
            bad.append("the touching-rows list is not the table's rows in order")
        nfiles = sum(int(re.search(r"reviewed files it touches \((\d+)\)", c[7]).group(1)) for c in touch)
        if int(m.group(3)) != nfiles:
            bad.append("the touching rows name %d files, not %s" % (nfiles, m.group(3)))
    ri = sum(1 for c in rows if _classes(c)[0] == "REVIEWED-INPUT CHANGED")
    stmt = re.search(r"carry (\d+) commits over their bases \(fnd/w34pdftext (\d+) over `aed4bd23`, fnd/s32small (\d+) over `eff28be3`", flat)
    nb = [sum(1 for c in rows if c[4].startswith(b[0] + " (")) for b in BRANCHES]
    if not stmt or [int(x) for x in stmt.groups()] != [len(rows)] + nb:
        bad.append("the bound statement's commit counts are not the table's")
    if ri == 0 and "None is classed REVIEWED-INPUT CHANGED" not in flat:
        bad.append("the bound statement does not say that none is REVIEWED-INPUT CHANGED")
    m = re.search(r"(\d+) are TOOLING first .*? and (\d+) RECORD TEXT first .*? (\d+) of the (\d+) touch a file cx46 read \((\d+) files", flat)
    if not m or [int(x) for x in m.groups()] != [first["TOOLING"], first["RECORD TEXT"], len(touch), len(rows),
                                                 int(re.search(r"; (\d+) files", flat).group(1))]:
        bad.append("the bound statement's class and touch counts are not the table's")
    return bad


def p_counts(texts, order):
    """Every count both records type about git, recomputed from git."""
    bad = []
    t = " ".join(texts[CLASS].split())
    r = " ".join(texts[RESULT].split())
    (na, ba, ta), (nb_, bb, tb) = BRANCHES
    ca = int(_git("rev-list", "--count", "%s..%s" % (ba, ta)))
    cb = int(_git("rev-list", "--count", "%s..%s" % (bb, tb)))
    merges = int(_git("rev-list", "--count", "--merges", "%s..%s" % (ba, ta))) + int(_git("rev-list", "--count", "--merges", "%s..%s" % (bb, tb)))
    fa = set(_git("diff", "--name-only", ba, ta).split())
    fb = set(_git("diff", "--name-only", bb, tb).split())
    rv = (fa | fb) & _reviewed()
    delta = len(set(_git("diff", "--name-only", CX45, REVIEWED).split()))
    tree = _git("ls-tree", "-r", "-l", ta).split("\n")
    vend = [l.split() for l in tree if "/pdftext/" in l]
    texts_ = [x for x in vend if x[-1].endswith(".txt")]
    side = [x for x in vend if x[-1].endswith(".meta.json")]
    gens = [f for f in fa if f.startswith("v2/docs/records/") and f.endswith(".py") and "/_lib/" not in f and "/w42cite/" not in f]
    mb_a = _git("merge-base", LINEAGE, ta).strip()
    mb_b = _git("merge-base", LINEAGE, tb).strip()
    if mb_a != ba or mb_b != bb:
        bad.append("a branch's base is not its merge base with the lineage (%s, %s)" % (mb_a[:8], mb_b[:8]))
    if merges:
        bad.append("a branch holds %d merge(s); the records say none" % merges)
    kinds = [f for f in fa | fb if f.endswith(".out") or f.endswith(".net") or "/apply_gen_sch_" in f or "/gen_sch_" in f]
    if kinds:
        bad.append("the branches change an output, a netlist, a circuit draft or a board generator: %s" % sorted(kinds)[:5])
    want_c = ["`git rev-list --count aed4bd23..5b3153aa` prints %d" % ca, "`git rev-list --count eff28be3..7b7219a7` prints %d" % cb,
              "the %d files of `git diff --name-only 06077cee 4d0ff8a2`" % delta,
              "%d of the two ranges' %d changed files are in that set" % (len(rv), len(fa | fb)),
              "**DONE:** the %d commits of set 32's two branches" % (ca + cb),
              "fnd/w34pdftext `5b3153aa`, %d commits over `aed4bd23`; fnd/s32small `7b7219a7`, %d commits over `eff28be3`" % (ca, cb),
              "(%d texts, %d sidecars)" % (len(texts_), len(side)), "The %d vendor files" % len(vend)]
    for w in want_c:
        if w not in t:
            bad.append("CLASSIFICATION.md does not read %r (git's numbers)" % w)
    rows = _real(texts[CLASS])
    first = Counter(_classes(c)[0] for c in rows)
    want_r = ["%d commits over `%s` (its merge base with set 31's lineage)" % (ca, ba),
              "%d commits over `%s` (main's follow-up after set 30's adoption)" % (cb, bb),
              "%d commits of the two branches over their bases (fnd/w34pdftext %d, fnd/s32small %d; no merge)" % (ca + cb, ca, cb),
              ("REVIEWED-INPUT CHANGED %d; RECORD TEXT %d; GENERATOR DATA (text) %d; TEST %d; DIGEST RE-PIN %d; MERGE %d; TOOLING %d; total %d"
               % tuple([first[k] for k in FIXED] + [len(rows)])),
              "%d of the %d touch a file cx46 read (%d files:" % (len([c for c in rows if "UNREVIEWED since cx46" in c[7]]), len(rows), len(rv)),
              "%d record generators read each maker's PDF text" % len(gens),
              "%d extractions committed beside their PDFs with a sidecar each (%d files)" % (len(texts_), len(vend)),
              "a change of how %d record generators read" % len(gens)]
    for w in want_r:
        if w not in r:
            bad.append("RESULT.md does not read %r (git's numbers)" % w)
    if len(texts_) != len(side) or len(gens) != 25:
        bad.append("the tip holds %d texts, %d sidecars, %d converted generators" % (len(texts_), len(side), len(gens)))
    tb_bytes = sum(int(x[3]) for x in texts_)
    inv = _show(ta, "v2/docs/records/_lib/PDFTEXT-INVENTORY.md")
    if not any(("%s committed (%s bytes of text" % (len(texts_), format(tb_bytes, ","))) in l for l in inv):
        bad.append("the inventory's total is not the tip's %d texts of %d bytes" % (len(texts_), tb_bytes))
    for a, b, span in (("16:32:57", "16:33:50", "53 s"),):
        s = [int(x) for x in a.split(":")]
        e = [int(x) for x in b.split(":")]
        d = (e[0] - s[0]) * 3600 + (e[1] - s[1]) * 60 + e[2] - s[2]
        if "%d s" % d != span or ("%s to %s, %s" % (a, b, span)) not in r:
            bad.append("the elapsed time %s to %s is not %s" % (a, b, span))
    return bad


ROW_NUMSTAT = (("82e1e1c6", "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md", "(+%d -%d)"),
               ("886704ea", "v2/docs/records/_lib/PDFTEXT-INVENTORY.md", "(+%d -%d)"),
               ("a7a485ab", "v2/docs/records/s32small/apply_q55_ve16.py", "(%d lines)"),
               ("a7a485ab", "v2/docs/records/s32small/README.md", "(%d lines)"),
               ("44891f15", "v2/docs/records/s32small/apply_q55_ve16.py", "(+%d -%d)"),
               ("44891f15", "v2/docs/records/s32small/README.md", "(+%d -%d)"),
               ("7b7219a7", "v2/docs/records/s32small/README.md", "(+%d -%d)"))


def p_row_numbers(text):
    """The per-row numbers the reasons type: the committed extractions and their files, and the line counts named."""
    bad = []
    rows = {(_sha_cell(c) or ("", ""))[0]: c for c in _real(text)}
    for short, c in rows.items():
        m = re.search(r"(\d+) committed extractions with (?:their )?sidecars \((\d+) files", c[7])
        if m:
            names = _git("show", "--name-only", "--format=", short).split()
            pt = [n for n in names if "/pdftext/" in n]
            want = (len([n for n in pt if n.endswith(".txt")]), len(pt))
            if (int(m.group(1)), int(m.group(2))) != want:
                bad.append("%s: %s extractions in %s files typed, git has %d in %d" % (short, m.group(1), m.group(2), want[0], want[1]))
    for short, path, form in ROW_NUMSTAT:
        add, rem = _git("diff", "--numstat", short + "^", short, "--", path).split()[:2]
        want = form % ((int(add), int(rem)) if form.count("%d") == 2 else (int(add),))
        if short not in rows or want not in rows[short][7]:
            bad.append("%s: the reason does not read %r for %s" % (short, want, path))
    return bad


def p_commits_named(texts):
    bad = []
    hist = set(_git("rev-list", LINEAGE, BRANCHES[0][2], BRANCHES[1][2]).split())
    for name, t in texts.items():
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
            bad.append("%s: `%s` names no commit of the histories this record reads and is not declared outside them" % (name, tok))
    return bad


def p_quotes(texts):
    bad = []
    for name, t in texts.items():
        for sha, path, n, q in GIT_ANCHOR.findall(t):
            q = q.replace("\\|", "|")
            if not _has(sha):
                if any(o.startswith(sha) for o in OUTSIDE):
                    continue                   # a declared commit outside this branch's history, absent on this host
                bad.append("%s: %s is not in this repository" % (name, sha))
                continue
            lines = _show(sha, path)
            if int(n) > len(lines) or q not in lines[int(n) - 1]:
                bad.append("%s: %r is not on %s:%s:%s" % (name, q[:60], sha[:8], path, n))
    return bad


def p_claims(result, assess_lines):
    bad = []
    for n, words in CLAIMS.items():
        if assess_lines[n - 1].rstrip() != words:
            bad.append("the assessment's line %d is not %r" % (n, words))
        if "`%s:%s:%d` `%s`" % (LINEAGE[:8], ASSESS, n, words) not in result:
            bad.append("RESULT.md does not quote line %d verbatim: %r" % (n, words))
    sec = result.split("\n## 6. ", 1)[1].split("\n## 7. ", 1)[0]
    for claim, state in (("Engineering-handover readiness", "READY AS A DESK PACKAGE OF OPEN ITEMS"),
                         ("Power-design closure", "BLOCKED"), ("Fabrication release", "BLOCKED")):
        if "| %s | %s |" % (claim, state) not in sec:
            bad.append("section 6 does not give %s as %s" % (claim, state))
    if "**Set 32 closes NO power item.**" not in sec or "**Layer 4's DESK gate stays NOT PASSED**" not in sec:
        bad.append("section 6 does not say that set 32 closes no power item and the DESK gate stays NOT PASSED")
    for wrong in ("DESK gate: PASSED", "DESK gate PASSED", "closure: CLOSED", "release: RELEASED", "Set 32 closes the"):
        if wrong in result:
            bad.append("RESULT.md reads %r" % wrong)
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
                bad.append("%s: the cited file _runs/%s is missing" % (name, rel))
    return bad


def _texts():
    return {RESULT: _read(RESULT), CLASS: _read(CLASS)}


def _mutant_refused(pred, texts, name, old, new, *extra):
    t = dict(texts)
    assert old in t[name], "the mutation's anchor %r is not in %s" % (old[:50], name)
    t[name] = t[name].replace(old, new, 1)
    assert pred(t, *extra), "%s passed a mutant (%r)" % (pred.__name__, new[:50])


# ---- tests ----

def t_the_records_carry_no_dash_and_open_with_their_state_lines():
    texts = _texts()
    assert not p_hygiene(texts), p_hygiene(texts)
    _mutant_refused(p_hygiene, texts, RESULT, "Set 32 closes NO power item", "Set 32 closes NO power item \u2014")
    _mutant_refused(p_hygiene, texts, CLASS, "**NOT DONE:**", "**NOT YET:**")


def t_the_rule_is_set_30s_line_11_verbatim_read_as_ruled():
    _need_git()
    t = _read(CLASS)
    s30 = _show(S30, S30C)
    tree = _read(S30C).split("\n")
    assert not p_rule(t, s30, tree), p_rule(t, s30, tree)
    assert p_rule(t.replace("is different now; the reason quotes", "is different now: the reason quotes", 1), s30, tree), \
        "a changed quote passed"
    assert p_rule(t.replace("did not take it (each touched", "took it (each touched", 1), s30, tree), \
        "a wider reading without set 30's answer passed"
    assert p_rule(t, s30, [l.replace("a verdict word", "a verdict") for l in tree]), "a changed copy of set 30's record passed"


def t_every_placeholder_is_a_declared_token():
    texts = _texts()
    assert not p_placeholders(texts), p_placeholders(texts)
    _mutant_refused(p_placeholders, texts, RESULT, "`__GATE__`", "`__GATE_LINE__`")
    _mutant_refused(p_placeholders, texts, CLASS, "`__REKEY__` | not determined", "`__REKEY__` | 2026-10-06 18:00:00")


def t_the_table_is_the_two_ranges_in_order_with_gits_columns_and_classes():
    order = _order()
    t = _read(CLASS)
    bad = p_coverage(t, order) + p_columns(t, order)
    assert not bad, bad
    row = [l for l in t.split("\n") if l.startswith("| 7 |")][0]
    assert p_coverage(t.replace(row + "\n", "", 1), order), "a dropped row passed"
    r11 = [l for l in t.split("\n") if l.startswith("| 11 |")][0]
    assert p_columns(t.replace(r11, r11.replace("| TOOLING + RECORD TEXT + TEST |", "| TOOLS + RECORD TEXT + TEST |"), 1), order), \
        "a class outside the fixed set passed"
    r3 = [l for l in t.split("\n") if l.startswith("| 3 |")][0]
    assert p_columns(t.replace(r3, r3.replace("UNREVIEWED since cx46", "unreviewed"), 1), order), \
        "a reviewed row without UNREVIEWED since cx46 passed"
    r8 = [l for l in t.split("\n") if l.startswith("| 8 |")][0]
    assert p_columns(t.replace(r8, r8.replace("| RECORD TEXT |", "| REVIEWED-INPUT CHANGED |"), 1), order), \
        "a REVIEWED-INPUT CHANGED row touching no reviewed file passed"
    assert p_columns(t.replace(r8, r8.replace("| 2026-10-06 15:42:51 |", "| 2026-10-06 15:42:52 |"), 1), order), "a wrong date passed"


def t_the_summary_and_the_bound_statement_are_the_tables():
    t = _read(CLASS)
    assert not p_summary(t), p_summary(t)
    assert p_summary(t.replace("| `TOOLING` | 7 | 10 |", "| `TOOLING` | 6 | 10 |", 1)), "a wrong summary count passed"
    assert p_summary(t.replace("fnd/s32small, 4 rows: RECORD TEXT 3, TOOLING 1", "fnd/s32small, 4 rows: RECORD TEXT 2, TOOLING 2", 1)), \
        "a wrong per-branch count passed"
    assert p_summary(t.replace("and 7 RECORD TEXT first", "and 6 RECORD TEXT first", 1)), \
        "a wrong statement count passed"
    r = [l for l in t.split("\n") if l.startswith("| 8 |")][0]
    assert p_summary(t.replace(r, r.replace("| RECORD TEXT |", "| TOOLING |"), 1)), "a re-classed row with the old counts passed"


def t_every_count_typed_is_gits():
    _need_git()
    texts = _texts()
    order = _order()
    assert not p_counts(texts, order), p_counts(texts, order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "prints 10;", "prints 11;", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "171 extractions committed", "172 extractions committed", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "16:33:50, 53 s", "16:33:50, 54 s", order)
    t = texts[CLASS]
    assert not p_row_numbers(t), p_row_numbers(t)
    assert p_row_numbers(t.replace("68 committed extractions with their sidecars (136 files)",
                                   "68 committed extractions with their sidecars (138 files)", 1)), "a wrong file count in a reason passed"
    assert p_row_numbers(t.replace("(+69 -21)", "(+69 -20)", 1)), "a wrong line count in a reason passed"


def t_every_commit_named_is_in_the_histories_read_or_declared_outside_them():
    _need_git()
    texts = _texts()
    assert not p_commits_named(texts), p_commits_named(texts)
    _mutant_refused(p_commits_named, texts, RESULT, "`6dc69ad2`", "`6dc69ad3`")


def t_every_quote_is_on_its_cited_line():
    _need_git()
    texts = _texts()
    assert not p_quotes(texts), p_quotes(texts)
    _mutant_refused(p_quotes, texts, CLASS, "`[E11PY:6019]`", "`[E11PY:6020]`")
    _mutant_refused(p_quotes, texts, RESULT, ":498` `\"Ready\" here means", ":497` `\"Ready\" here means")


def t_the_three_claims_are_quoted_verbatim_from_the_assessment():
    _need_git()
    result = _read(RESULT)
    lines = _show(LINEAGE, ASSESS)
    assert not p_claims(result, lines), p_claims(result, lines)
    if os.path.isfile(os.path.join(REPO, ASSESS)):            # the tree's assessment holds the three headings too
        tree = _read(ASSESS).split("\n")
        for words in CLAIMS.values():
            assert words in [l.rstrip() for l in tree], "the tree's assessment lacks %r" % words
    assert p_claims(result.replace("| Power-design closure | BLOCKED |", "| Power-design closure | CLOSED |", 1), lines), \
        "a changed claim passed"
    assert p_claims(result, [l.replace("NOT PASSED", "PASSED") for l in lines]), "a changed assessment line passed"


def t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote():
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    if not os.path.isdir(os.path.join(runs, "int32")):
        raise Skip("the coordinator's files (_runs) are not on this host")
    texts = _texts()
    assert not p_logs(texts, runs), p_logs(texts, runs)
    _mutant_refused(p_logs, texts, RESULT, "`round 1 would select: 31 pairs`", "`round 1 would select: 32 pairs`", runs)


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
test_the_rule_is_set_30s_line_11_verbatim_read_as_ruled = _pytest(t_the_rule_is_set_30s_line_11_verbatim_read_as_ruled)
test_the_table_is_the_two_ranges_in_order_with_gits_columns_and_classes = _pytest(
    t_the_table_is_the_two_ranges_in_order_with_gits_columns_and_classes)
test_the_summary_and_the_bound_statement_are_the_tables = _pytest(t_the_summary_and_the_bound_statement_are_the_tables)
test_every_count_typed_is_gits = _pytest(t_every_count_typed_is_gits)
test_every_commit_named_is_in_the_histories_read_or_declared_outside_them = _pytest(
    t_every_commit_named_is_in_the_histories_read_or_declared_outside_them)
test_every_quote_is_on_its_cited_line = _pytest(t_every_quote_is_on_its_cited_line)
test_the_three_claims_are_quoted_verbatim_from_the_assessment = _pytest(t_the_three_claims_are_quoted_verbatim_from_the_assessment)
test_every_cited_file_of_the_coordinator_exists_and_carries_its_quote = _pytest(
    t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote)
