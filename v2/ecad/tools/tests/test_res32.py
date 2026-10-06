#!/usr/bin/env python3
"""Set 32's result record (MESHSAT-1357, 6 October 2026, W44; restated by W73 from 20:23 CEST over the five branches set 32's chain
pins): `v2/docs/records/int32/RESULT.md` and its classification `CLASSIFICATION.md` hold what they type.

The basis of each predicate (W73's restatement): every row's sha, date, subject and file count is compared with git over the five
ranges in the chain's merge order (each range's base is its merge base with set 31's lineage tip aa332280, or for fnd/s32attr with
fnd/w34pdftext's tip, which the chain merges first); the declared tokens are fill_res31.py's (`_runs/int31/freeze/fill_res31.py`, its
TOK pattern without the name INTEGRATED, which it fills only inside quoted subjects), so the same fill tool can be pointed at set 32 (the
runner pass reads the tool and compares); the class counts are recomputed from the table; row 14's carried change names a source row
that set 30's adopted record classes REVIEWED-INPUT CHANGED; the chain's pinned merges are the five ranges' branches, each pin inside
its range (fnd/res32's own later commits are placeholder row 31's).

What fails here: a commit of set 32's five branch ranges missing, doubled or out of order; a short sha that is not its full sha's prefix; a
date, subject or file count that is not git's; a class outside W39's fixed set; a row that touches a file cx46 read without the words
"UNREVIEWED since cx46"; a REVIEWED-INPUT CHANGED row that touches no file of the reviewed tree (present at 4d0ff8a2), or one that
touches none of cx46's delta without classing a carried change with its source row and the delta membership; a rule paragraph that is not
set 30's line 11 verbatim (`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`, read as the coordinator ruled on 6 October 2026,
reading A), or that drops set 30's row 44 as the precedent, the wider reading's answer or the placeholder rows' note; summary counts, per-branch counts or the bound statement's
numbers that are not the table's; a count typed in the records that is not git's; a commit named that is in no history this record
reads; a quote that is not on its cited line at its revision; the three claims not quoted verbatim from the assessment; a placeholder
outside the five tokens fill_res31.py fills; an em or en dash. Each predicate is also run on a mutant it must refuse.

The coordinator's files (`<worktrees>/_runs`, outside the repository) are read by ONE test, which raises Skip where they are absent (a
rented box): run it in the runner pass (the record's section 8); so does the fill tool's test. The five branch tips below are the ones
the record read; a commit a branch gains later is outside these ranges, so the coordinator adds its row and moves the tip here at the
adoption.

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
LINEAGE = "aa3322806da156d12f2b23dbe9fc98a8805926f0"         # set 31's lineage tip as W73 read it (fnd/int31regen, the re-key's cache)
ASSESS_AT = "3057ae43f4fb7fc5e3d6282ce52d448c8ee27929"       # the revision the three claims are quoted at (an ancestor of LINEAGE)
# (branch, base, tip, against): base = git merge-base <against> <tip>; the chain's merge order (_runs/int32/chain.sh, steps a2 to a3c)
BRANCHES = (("fnd/w34pdftext", "aed4bd234644c80fa494299b21099acf6d2454c1", "b397aada17befd8c6ee8be09550a785139c45066", LINEAGE),
            ("fnd/s32attr", "5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac", "9210ab541e8144af530f928c1da98b96f90c89fd",
             "b397aada17befd8c6ee8be09550a785139c45066"),
            ("fnd/s32small", "eff28be3b80f882db545a849b0da1def0217f63d", "7b7219a7d0a695b6b866435116905964a68f5578", LINEAGE),
            ("fnd/res32", "3057ae43f4fb7fc5e3d6282ce52d448c8ee27929", "7ae6175814b7824b3a9f69357ec75e9810a41da4", LINEAGE),
            ("fnd/l4e7cache", "31928583c612ea43df17df5d7e0cbb2f66090f8e", "5ee1e66eb8787a788647305509ae6c2700144d9a", LINEAGE))
CHAIN_LABELS = {"pdftext": "fnd/w34pdftext", "s32attr": "fnd/s32attr", "s32small": "fnd/s32small", "res32": "fnd/res32",
                "l4e7cache": "fnd/l4e7cache"}                # chain.sh's merge_one labels and the branch each merges
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
CX45 = "06077cee"                                           # the delta cx46 read: git diff 06077cee 4d0ff8a2
L4E9_EXTRA = ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l4e9/l4e9_power_path.out")
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT", "GENERATOR DATA (text)", "TEST", "DIGEST RE-PIN", "MERGE", "TOOLING")
DECLARED = ("__REKEY__", "__CANDIDATE__", "__GATE__", "__PROMOTED__", "__ADOPTION__")   # fill_res31.py's TOK, INTEGRATED apart
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
    for sha in (LINEAGE, ASSESS_AT, REVIEWED) + tuple(b[1] for b in BRANCHES) + tuple(b[2] for b in BRANCHES):
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
    """[(row number, branch, full sha, parents, date, subject, names)]: each branch's range oldest first, in the chain's merge order."""
    if "order" in _C:
        return _C["order"]
    _need_git()
    out = []
    n = 0
    for name, base, tip, _against in BRANCHES:
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
        bad.append("the rows are not the five ranges in their order (missing or misnumbered %s, extra %s)" % (miss, extra))
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
    for name, _base, _tip, _against in BRANCHES:
        br = [c for c in rows if c[4].startswith(name + " (")]
        f = Counter(_classes(c)[0] for c in br)
        part = ", ".join("%s %d" % (k, f[k]) for k in FIXED if f[k])
        want = "%s, %d rows: %s" % (name, len(br), part)
        if want not in flat:
            bad.append("the per-branch line does not read %r" % want)
    touch = [c for c in rows if "UNREVIEWED since cx46" in c[7]]
    m = re.search(r"\*\*The rows that touch a file cx46 read: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?); (\d+) files", flat)
    nfiles = 0
    if not m or int(m.group(1)) != len(touch):
        bad.append("the touching-rows line is not the table's %d" % len(touch))
    else:
        named = re.findall(r"`([0-9a-f]{8})` \(([\d.]+)\)", m.group(2))
        if named != [(_sha_cell(c)[0], c[0]) for c in touch]:
            bad.append("the touching-rows list is not the table's rows in order")
        nfiles = sum(int(re.search(r"reviewed files it touches \((\d+)\)", c[7]).group(1)) for c in touch)
        if int(m.group(3)) != nfiles:
            bad.append("the touching rows name %d files, not %s" % (nfiles, m.group(3)))
    nb = [sum(1 for c in rows if c[4].startswith(b[0] + " (")) for b in BRANCHES]
    want = "carry %d commits over their bases (%s; no merge)" % (len(rows), ", ".join(
        "%s %d over `%s`" % (b[0], n, b[1][:8]) for b, n in zip(BRANCHES, nb)))
    if want not in flat:
        bad.append("the bound statement does not read %r" % want)
    want = "By first class: " + ", ".join("%d %s first" % (first[k], k) for k in FIXED if first[k]) + "."
    if want not in flat:
        bad.append("the bound statement's class counts do not read %r" % want)
    ri = [c for c in rows if _classes(c)[0] == RIC]
    if not ri and "None is classed REVIEWED-INPUT CHANGED" not in flat:
        bad.append("the bound statement does not say that none is REVIEWED-INPUT CHANGED")
    if len(ri) == 1 and ("The one REVIEWED-INPUT CHANGED row is" not in flat or "(row %s," % ri[0][0] not in flat):
        bad.append("the bound statement does not name the one REVIEWED-INPUT CHANGED row %s" % ri[0][0])
    if "%d of the %d touch a file cx46 read (%d files:" % (len(touch), len(rows), nfiles) not in flat:
        bad.append("the bound statement's touch counts are not the table's (%d of %d, %d files)" % (len(touch), len(rows), nfiles))
    return bad

def p_counts(texts, order):
    """Every count both records type about git, recomputed from git over the five ranges."""
    bad = []
    t = " ".join(texts[CLASS].split())
    r = " ".join(texts[RESULT].split())
    cnt, allf = [], set()
    merges = 0
    for name, base, tip, against in BRANCHES:
        cnt.append(int(_git("rev-list", "--count", "%s..%s" % (base, tip))))
        merges += int(_git("rev-list", "--count", "--merges", "%s..%s" % (base, tip)))
        allf |= set(_git("diff", "--name-only", base, tip).split())
        mb = _git("merge-base", against, tip).strip()
        if mb != base:
            bad.append("%s: its base %s is not its merge base %s with %s" % (name, base[:8], mb[:8], against[:8]))
    if merges:
        bad.append("a branch holds %d merge(s); the records say none" % merges)
    kinds = [f for f in allf if f.endswith(".out") or f.endswith(".net") or "/apply_gen_sch_" in f or "/gen_sch_" in f]
    if kinds:
        bad.append("the branches change an output, a netlist, a circuit draft or a board generator: %s" % sorted(kinds)[:5])
    rv = allf & _reviewed()
    delta = len(set(_git("diff", "--name-only", CX45, REVIEWED).split()))
    pa = BRANCHES[0]
    fa = set(_git("diff", "--name-only", pa[1], pa[2]).split())
    tree = _git("ls-tree", "-r", "-l", pa[2]).split("\n")
    vend = [l.split() for l in tree if "/pdftext/" in l]
    texts_ = [x for x in vend if x[-1].endswith(".txt")]
    side = [x for x in vend if x[-1].endswith(".meta.json")]
    gens = [f for f in fa if f.startswith("v2/docs/records/") and f.endswith(".py") and "/_lib/" not in f and "/w42cite/" not in f]
    rows = _real(texts[CLASS])
    first = Counter(_classes(c)[0] for c in rows)
    touch = [c for c in rows if "UNREVIEWED since cx46" in c[7]]
    want_c = ["`git rev-list --count %s..%s` prints %d" % (b[1][:8], b[2][:8], n) for b, n in zip(BRANCHES, cnt)]
    want_c += ["%s `%s`, %d commits over `%s`" % (b[0], b[2][:8], n, b[1][:8]) for b, n in zip(BRANCHES, cnt)]
    want_c += ["the %d files of `git diff --name-only 06077cee 4d0ff8a2`" % delta,
               "%d of the five ranges' %d changed files are in that set" % (len(rv), len(allf)),
               "**DONE:** the %d commits of the five branches" % sum(cnt),
               "(%d texts, %d sidecars)" % (len(texts_), len(side)), "The %d vendor files" % len(vend),
               "each named in its row (%d distinct)" % len(rv)]
    for w in want_c:
        if w not in t:
            bad.append("CLASSIFICATION.md does not read %r (git's numbers)" % w)
    want_r = ["%d commits over `%s`" % (n, b[1]) for b, n in zip(BRANCHES, cnt)]
    want_r += ["%d commits of the five branches over their bases (%s; no merge)" % (sum(cnt), ", ".join(
                   "%s %d" % (b[0], n) for b, n in zip(BRANCHES, cnt))),
               ("REVIEWED-INPUT CHANGED %d; RECORD TEXT %d; GENERATOR DATA (text) %d; TEST %d; DIGEST RE-PIN %d; MERGE %d; TOOLING %d; total %d"
                % tuple([first[k] for k in FIXED] + [len(rows)])),
               "%d of the %d touch a file cx46 read (%d distinct files:" % (len(touch), len(rows), len(rv)),
               "%d record generators read each maker's PDF text" % len(gens),
               "%d extractions committed beside their PDFs with a sidecar each (%d files)" % (len(texts_), len(vend)),
               "a change of how %d record generators read" % len(gens)]
    for w in want_r:
        if w not in r:
            bad.append("RESULT.md does not read %r (git's numbers)" % w)
    if len(texts_) != len(side) or len(gens) != 26:
        bad.append("the tip holds %d texts, %d sidecars, %d converted generators (W34's 25 and W55's l8p_c4)" % (len(texts_), len(side), len(gens)))
    tb_bytes = sum(int(x[3]) for x in texts_)
    inv = _show(pa[2], "v2/docs/records/_lib/PDFTEXT-INVENTORY.md")
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
               ("7b7219a7", "v2/docs/records/s32small/README.md", "(+%d -%d)"),
               ("4f558357", "v2/docs/records/l8p/l8p_c4.py", "(+%d -%d)"),
               ("f26a52c4", "v2/ecad/tools/tests/test_pdftext_input.py", "(+%d -%d)"),
               ("b397aada", "v2/docs/records/_lib/PDFTEXT-INVENTORY.md", "(+%d -%d)"),
               ("9210ab54", "v2/ecad/tools/tests/test_l9t5.py", "(+%d -%d)"),
               ("849e66c7", "v2/docs/records/l4e7/l4e7_stage_settings.py", "(+%d -%d)"),
               ("849e66c7", "v2/ecad/tools/tests/test_l4e7_cachekey.py", "(%d lines, new)"),
               ("2178cae5", "v2/docs/records/l4e7/l4e7_p0sol.py", "(+%d -%d)"),
               ("935584bf", "v2/ecad/tools/tests/test_l4e7.py", "(+%d -%d)"),
               ("5ee1e66e", "v2/docs/records/l4e7/CACHE-BOUNDARY-L4E11.md", "(+%d -%d)"))


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
    hist = set(_git("rev-list", LINEAGE, *[b[2] for b in BRANCHES]).split())
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
        if "`%s:%s:%d` `%s`" % (ASSESS_AT[:8], ASSESS, n, words) not in result:
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


def p_carried(text, s30_lines):
    """A row classed REVIEWED-INPUT CHANGED for a carried change names set 30's source row, and set 30's adopted record classes that
    row REVIEWED-INPUT CHANGED (W51's method: a carried word is looked up in the reasons of the REVIEWED-INPUT CHANGED rows)."""
    bad = []
    s30 = {}
    for l in s30_lines:
        m = re.match(r"\| (\d+) \| `([0-9a-f]{8})` / `[0-9a-f]{40}` \|", l)
        if m:
            s30[m.group(1)] = (m.group(2), [c.strip() for c in CELL_SPLIT.split(l.strip())[1:-1]][6])
    for c in _real(text):
        if _classes(c)[0] != RIC or "second sentence" not in c[7]:
            continue
        m = re.search(r"set 30's row (\d+)'s change \(`([0-9a-f]{8})`", c[7])
        if not m:
            bad.append("row %s: no set 30 source row named as `set 30's row N's change (`sha``" % c[0])
            continue
        n, sha = m.groups()
        if n not in s30 or s30[n][0] != sha or not s30[n][1].startswith(RIC):
            bad.append("row %s: set 30's row %s (%s) is not a REVIEWED-INPUT CHANGED row of set 30's record" % (c[0], n, sha))
    return bad


def _fill_tokens(src):
    """The names fill_res31.py's TOK pattern fills, read with ast (the re.compile call assigned to TOK)."""
    import ast
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "TOK" for x in node.targets):
            pat = node.value.args[0].value
            m = re.fullmatch(r"__\(([A-Z|]+)\)__", pat)
            return set(m.group(1).split("|")) if m else None
    return None


def p_fill(src):
    names = _fill_tokens(src)
    if names is None:
        return ["fill_res31.py has no TOK pattern of the form __(A|B)__"]
    want = set(d.strip("_") for d in DECLARED)
    if names - {"INTEGRATED"} != want:
        return ["the declared tokens %s are not fill_res31.py's %s (without INTEGRATED)" % (sorted(want), sorted(names))]
    return []


def p_chain(sh):
    """chain.sh's merges are the five ranges' branches, each pinned inside its range (fnd/res32's later commits are row 31's)."""
    bad = []
    labels = set(re.findall(r'merge_one (\w+) "\$PIN_', sh))
    if labels != set(CHAIN_LABELS):
        bad.append("chain.sh merges %s, not the record's five %s" % (sorted(labels), sorted(CHAIN_LABELS)))
    var = {"PDFTEXT": "pdftext", "ATTR": "s32attr", "SMALL": "s32small", "RES": "res32", "L4E7CACHE": "l4e7cache"}
    pins = dict(re.findall(r"^SRC_(\w+)=\$\{SRC_\w+:-([0-9a-f]{7,40})\}", sh, re.M))
    for v, lab in var.items():
        br = [b for b in BRANCHES if b[0] == CHAIN_LABELS[lab]][0]
        if v not in pins:
            bad.append("chain.sh pins no default for SRC_%s" % v)
            continue
        try:
            full = _git("rev-parse", "--verify", pins[v] + "^{commit}").strip()
        except RuntimeError:
            bad.append("SRC_%s=%s is not a commit here" % (v, pins[v]))
            continue
        if lab == "res32":
            ok = _git("merge-base", br[2], full).strip() == br[2]
        else:
            ok = full in _git("rev-list", "%s..%s" % (br[1], br[2])).split()
        if not ok:
            bad.append("SRC_%s=%s is outside the record's range %s..%s of %s" % (v, pins[v], br[1][:8], br[2][:8], br[0]))
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


def t_the_table_is_the_five_ranges_in_order_with_gits_columns_and_classes():
    order = _order()
    t = _read(CLASS)
    bad = p_coverage(t, order) + p_columns(t, order)
    assert not bad, bad
    row = [l for l in t.split("\n") if l.startswith("| 7 |")][0]
    assert p_coverage(t.replace(row + "\n", "", 1), order), "a dropped row passed"
    r16 = [l for l in t.split("\n") if l.startswith("| 16 |")][0]
    assert p_columns(t.replace(r16, r16.replace("| TOOLING + RECORD TEXT + TEST |", "| TOOLS + RECORD TEXT + TEST |"), 1), order), \
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
    assert p_summary(t.replace("| `TOOLING` | 12 | 15 |", "| `TOOLING` | 11 | 15 |", 1)), "a wrong summary count passed"
    assert p_summary(t.replace("fnd/s32small, 4 rows: RECORD TEXT 3, TOOLING 1", "fnd/s32small, 4 rows: RECORD TEXT 2, TOOLING 2", 1)), \
        "a wrong per-branch count passed"
    assert p_summary(t.replace("15 RECORD TEXT first", "14 RECORD TEXT first", 1)), \
        "a wrong statement count passed"
    r = [l for l in t.split("\n") if l.startswith("| 8 |")][0]
    assert p_summary(t.replace(r, r.replace("| RECORD TEXT |", "| TOOLING |"), 1)), "a re-classed row with the old counts passed"


def t_every_count_typed_is_gits():
    _need_git()
    texts = _texts()
    order = _order()
    assert not p_counts(texts, order), p_counts(texts, order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "prints 13;", "prints 12;", order)
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
    lines = _show(ASSESS_AT, ASSESS)
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


def t_a_carried_change_names_a_reviewed_input_row_of_set_30():
    _need_git()
    t = _read(CLASS)
    s30 = _show(S30, S30C)
    assert not p_carried(t, s30), p_carried(t, s30)
    assert [c[0] for c in _real(t) if _classes(c)[0] == RIC] == ["14"], "the REVIEWED-INPUT CHANGED rows are not row 14 alone"
    assert p_carried(t.replace("set 30's row 8's change (`6b768b1e`", "set 30's row 9's change (`9cf3982a`", 1), s30), \
        "a source row that is a merge passed"


def t_the_declared_tokens_are_the_fill_tools():
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    tool = os.path.join(runs, "int31", "freeze", "fill_res31.py")
    if not os.path.isfile(tool):
        raise Skip("the coordinator's fill tool (_runs/int31/freeze/fill_res31.py) is not on this host")
    src = open(tool, encoding="utf-8").read()
    assert not p_fill(src), p_fill(src)
    assert p_fill(src.replace("|ADOPTION|", "|", 1)), "a tool that fills one token fewer passed"


def t_the_chain_merges_the_five_branches_pinned_inside_their_ranges():
    _need_git()
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    sh_p = os.path.join(runs, "int32", "chain.sh")
    if not os.path.isfile(sh_p):
        raise Skip("the coordinator's chain (_runs/int32/chain.sh) is not on this host")
    sh = open(sh_p, encoding="utf-8").read()
    assert not p_chain(sh), p_chain(sh)
    m = re.search(r"^SRC_ATTR=\$\{SRC_ATTR:-([0-9a-f]+)\}", sh, re.M)
    assert p_chain(sh.replace(m.group(0), "SRC_ATTR=${SRC_ATTR:-%s}" % BRANCHES[0][1][:8], 1)), "a pin outside its range passed"
    assert p_chain(sh.replace('merge_one s32attr "$PIN_', 'merge_one s32attrX "$PIN_', 1)), "a sixth merge label passed"


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
test_the_table_is_the_five_ranges_in_order_with_gits_columns_and_classes = _pytest(
    t_the_table_is_the_five_ranges_in_order_with_gits_columns_and_classes)
test_the_summary_and_the_bound_statement_are_the_tables = _pytest(t_the_summary_and_the_bound_statement_are_the_tables)
test_every_count_typed_is_gits = _pytest(t_every_count_typed_is_gits)
test_every_commit_named_is_in_the_histories_read_or_declared_outside_them = _pytest(
    t_every_commit_named_is_in_the_histories_read_or_declared_outside_them)
test_every_quote_is_on_its_cited_line = _pytest(t_every_quote_is_on_its_cited_line)
test_the_three_claims_are_quoted_verbatim_from_the_assessment = _pytest(t_the_three_claims_are_quoted_verbatim_from_the_assessment)
test_every_cited_file_of_the_coordinator_exists_and_carries_its_quote = _pytest(
    t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote)
test_a_carried_change_names_a_reviewed_input_row_of_set_30 = _pytest(t_a_carried_change_names_a_reviewed_input_row_of_set_30)
test_the_declared_tokens_are_the_fill_tools = _pytest(t_the_declared_tokens_are_the_fill_tools)
test_the_chain_merges_the_five_branches_pinned_inside_their_ranges = _pytest(
    t_the_chain_merges_the_five_branches_pinned_inside_their_ranges)
