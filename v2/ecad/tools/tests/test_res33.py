#!/usr/bin/env python3
"""Set 33's result record (MESHSAT-1357, 7 October 2026, W165, queue item Q-187): `v2/docs/records/int33/RESULT.md`, its
classification `CLASSIFICATION.md` and its adoption-page statement `ENTRY-PAGES.patch.md` hold what they type.

The basis of each predicate: every classified row's sha, date, subject, file count and folders, and the closing clauses of its reason
(the outputs and drafts it commits, the files of the reviewed tree it touches, the reviewed files it touches with "UNREVIEWED since
cx46", or "no file cx46 read"), are compared with git over the four ranges in the chain's merge order: fnd/l4k `be07863b..ff0c79f0`,
fnd/l4hoe `06d064ff..531c4754`, fnd/l4hod `06d064ff..92d81690` read on its first-parent line with each merge's branch commits under it
(the commits of `<first parent>..<second parent>`, numbered <merge>.1 onward, set 31's form), and fnd/l4rowc `be07863b..653cb1bc`.
W170 (queue item Q-192, 7 October 2026) brought the record from W165's tips (fnd/l4hoe `003338e3`, fnd/l4hod `23384006`) to the pins
set 33's chain uses: the commits a range gains past W165's tip are numbered after that tip's row with a letter, in the range's order
(`531c4754` row 17a; `e1687b89` and `92d81690` rows 47a and 47b), so that rows 1 to 66 keep the numbers the record's prose, the fill
tool's set 33 suggestions (rows 65 and 66) and the deferral list cite (SESSION decision W170-D1, CLASSIFICATION.md's decisions).

W219's restatement (8 October 2026, queue item Q-242, the ONE writer of fnd/adopt33 cut at set 33's candidate b5b4b2a0; the NEXT line of
both records; W154's form for set 32): the classification's row 64 is replaced, before the adoption, by the integration's rows written from
git (rows 64.1 to 64.7.6 with 64.5.1 to 64.5.9 and 64.7.1.1), and rows 65 and 66 carry git's date, subject, files and a class while their
sha cells keep the fill tool's tokens. The basis of each changed expectation: (1) _real() reads the branch rows alone (the four ranges' 78
rows; the integration's rows are read by p_integ), because the branch counts, the bound statement and RESULT's "first class per row" sentence
stay over the branch commits, so p_coverage, p_columns and p_summary keep their scope; (2) p_coverage: the rows whose sha cell is one code
span are rows 65 and 66 alone (row 64, "not determined", is gone: several commits that did not exist, W75's F11, now exist and have rows);
(3) p_placeholders: no row 64.x carries a token, and rows 65 and 66 carry a date and a class of the fixed set (the re-key's cache commit
and the candidate exist: REKEY_AT and CAND_AT below); (4) p_integ (new): the integration's rows are git's, row for row: the first-parent
commits of CHAIN_BASE..CAND_AT oldest first, the first six as 64.1 to 64.6 and the rest before the re-key as 64.7.1 onward (the prepared
row 64.7's "each further first-parent commit before the re-key, one row each"), after each merge the commits its second parent brings that
no branch range holds (<row>.<k>, their branch from the merge's subject), then REKEY_AT (65) and CAND_AT (66); each row's sha (65 and 66:
the token, or after the fill the same commit), author date, subject, branch with its tip holding the commit, file count and folders against
the first parent, classes of the fixed set with MERGE exactly on two-parent commits, the reviewed files it touches or brings with
"UNREVIEWED since cx46" or "no file cx46 read" as p_columns requires of a branch row, the files of the reviewed tree outside the delta, a
REVIEWED-INPUT CHANGED row quoting a line under reading A with earlier source rows and the delta membership, and a merge naming the first
row it brings; the outputs and drafts a row names are prose, not an enumerated closing clause (D-W219-1); (5) p_integ_summary (new):
section 2's integration table, touching rows, file touches, distinct files and whole-table count are the rows'; (6) p_nofill (new): no
fill-in cell is left in either record; (7) p_prepared and section 3 are gone with the section. Each new predicate has mutants it refuses.

The reviewed set is set 32's 62 files (`git diff --name-only 06077cee 4d0ff8a2` plus the L4-E9 page and its output); "the reviewed tree" is
`git ls-tree -r 4d0ff8a2`. The class counts, the per-branch counts, the touching rows and the rows of new engineering content are
recomputed from the table and compared with section 2 and with RESULT's restatement of them. The rule paragraph is set 30's line 11
verbatim. Every `<sha>:path:N` quote is on its line; every commit named resolves; every token is one the fill tool fills; the three
claims are the assessment's lines at `f08e3961`; the integration's rows are git's (W219).

Through the fill (set 32's W80 rule): the test reads the stage from RESULT's role rows (the re-key, the candidate, set 33's promotion,
the adoption): stage 0, every role its token; stage 1, the first three named and ADOPTION its token; stage 2, all four named; any other
mix is a partial fill and refused. A named role commit must resolve; the candidate and the promotion name the same commit; the re-key and
the candidate hold the four tips; the adoption descends from the candidate. The mutants whose anchor is a token use anchors that stay.

What fails here: a commit of the four ranges missing, doubled or out of order; a short sha that is not its full sha's prefix; a date,
subject, file count, folder list or closing clause that is not git's; a row's branch label whose tip does not hold its commit; a class
outside W39's fixed set or a MERGE that is not a merge; a REVIEWED-INPUT CHANGED row that touches no file of the reviewed tree; counts
that are not the table's; a quote not on its cited line; a placeholder outside the fill tool's tokens or a PROMOTED on a BASE row; an integration row that is not git's, a token in a row 64.x
or a fill-in cell left (W219); an em or en dash. Each predicate is run on a mutant it must refuse.

The coordinator's files (`<worktrees>/_runs`, `<worktrees>/_bin`) are read by two tests, which raise Skip where they are absent (a
rented box): run them in the runner pass (RESULT.md section 8). Read-only: git is read with `git log`, `git show`, `git diff`,
`git rev-list`, `git merge-base`, `git ls-tree` and `git cat-file`; nothing is written. tests/run.py runs the `t_` functions; `test_`
aliases let pytest collect them."""
import ast
import os
import re
import subprocess
from collections import Counter

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = "v2/docs/records/int33"
RESULT, CLASS, PATCH = REC + "/RESULT.md", REC + "/CLASSIFICATION.md", REC + "/ENTRY-PAGES.patch.md"
BE, B06 = "be07863bbca206a81ab42b9f96a7684c5c10a746", "06d064ffa58a1211139d0f1d8e7b536675a67948"
# The tips: W170's restatement (Q-192) of W165's (basis: the pins of W170's brief, `_runs/claude/w170res33b/BRIEF.md` line 8, and the
# coordinator's clerical verification of W167's round, QUEUE.md "12:59 (clock)": ROW (b) FINAL fnd/l4hod 92d81690, HO-E FINAL
# fnd/l4hoe 531c4754). fnd/l4hoe was 003338e3 and fnd/l4hod 23384006 in W165's draft; LATE names those old tips, whose ranges keep
# their row numbers, and the commits past them take a letter (W170-D1).
BRANCHES = (("fnd/l4k", BE, "ff0c79f0242e7990e111c89f49b281c4a2953d2b", False),
            ("fnd/l4hoe", B06, "531c4754a61847261678597f572e9596d16b0db1", False),
            ("fnd/l4hod", B06, "92d816900925f94a690c00cdae7a1e52e814c610", True),
            ("fnd/l4rowc", BE, "653cb1bcfe2791728a7ba9aeafbf427830d06dd3", False))
LATE = {"fnd/l4hoe": "003338e3f92a86d6bf687385ab752be5eab0c206", "fnd/l4hod": "2338400687ba71b07889b4185dd86beda311c557"}
LABEL_TIPS = {"fnd/l4k": "ff0c79f0", "fnd/l4hoe": "531c4754", "fnd/l4canmb": "664d4019", "fnd/l4canq": "efce7c7a", "fnd/l4reg": "86dbcdff",
              "fnd/l4hod": "92d81690", "fnd/l4small": "77866143", "fnd/l4lim": "aa6704b2", "fnd/l4fet": "49d4f9e6", "fnd/l4rowc": "653cb1bc"}
PROMOTED32 = "f08e396175dd418434061d731e08111d006d6efa"   # set 32's promoted revision, this record's branch point
# W219 (Q-242): the integration's rows read from git (p_integ): the chain's base (main after set 32's adoption, the chain's log line 1),
# the first-parent line to the candidate; REKEY_AT is the re-key's cache commit (row 65), CAND_AT set 33's candidate C4 (row 66), the
# tips of fnd/res33 and fnd/s33cite the commits the chain's and the coordinator's merges brought (rows 64.5 and 64.7.1)
CHAIN_BASE = "46d4fe58a233f1417f28e5932b862e884940cd62"
REKEY_AT = "d9ab507053bef835023c5399bd2a574ee77785de"
CAND_AT = "b5b4b2a01e54231d17201082f1ecdf25612440fa"
INTEG_TIPS = {"fnd/int33": CAND_AT, "fnd/res33": "5e5db712e8a8699b1b3cf5cc7454166d63dcb75c", "fnd/s33cite": "31356a264a56ca7ae166115aa196eaa2679aac55"}
INTEG_ROW = re.compile(r"64(?:\.\d+)+")
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"     # cx46's candidate
CX45 = "06077cee85d0ed44c74c2a06c9fbb2030a0dedbc"         # the base of the delta cx46 read
L4E9_EXTRA = ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l4e9/l4e9_power_path.out")
S30, S30C = "eff28be3", "v2/docs/records/int30/CLASSIFICATION.md"
ASSESS = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
CLAIMS = {492: "### Layer 4's DESK gate: NOT PASSED",
          496: "### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
          500: "### Power-design closure: BLOCKED. Fabrication release: BLOCKED."}
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT", "GENERATOR DATA (text)", "TEST", "DIGEST RE-PIN", "MERGE", "TOOLING")
RIC = "REVIEWED-INPUT CHANGED"
DECLARED = ("__REKEY__", "__CANDIDATE__", "__GATE__", "__PROMOTED__", "__ADOPTION__")   # fill_res.py's TOK, INTEGRATED apart
INTEG_TOK = {"65": DECLARED[0], "66": DECLARED[1]}   # W219: through DECLARED, so the deferral list's count of this module's literal tokens holds
NEW = "new engineering content (outside the reviewed tree):"
NONCOMMIT = {"6e11114faadda427", "fe15b1f03875940e", "8c8e26858293", "c8956b14b0e7", "99f9075f2ff85a69"}  # KEYs and digests the record names
GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
RUN_ANCHOR = re.compile(r"`<worktrees>/_runs/([^`:\s]+)(?::(\d+))?`(?:, entry \"([^\"]+)\",)? `([^`]+)`")
HEXTOK = re.compile(r"`([0-9a-f]{7,40})`")
PH = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
DASHES = ("—", "–")
ROLES = (("REKEY", "| The re-key's cache commit |", "__REKEY__"), ("CANDIDATE", "| INTEGRATED = CANDIDATE: the candidate commit |", "__CANDIDATE__"),
         ("PROMOTED", "| PROMOTED: main after the fast-forward, set 33's promotion |", "__PROMOTED__"),
         ("ADOPTION", "| ADOPTED: the commit that adopts this record |", "__ADOPTION__"))
PAGES = ("v2/docs/handover/START-HERE.md", "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md", "v2/docs/handover/LAYER-STATUS.md",
         "v2/docs/EXECUTION-PLAN.md")


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
        return subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True).returncode == 0
    except OSError as e:
        raise Skip("no git here: %s" % e)


def _anc(a, b):
    return subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", a, b], capture_output=True).returncode == 0


def _need_git():
    for sha in (PROMOTED32, REVIEWED, CX45) + tuple(b[1] for b in BRANCHES) + tuple(b[2] for b in BRANCHES) + tuple(LATE.values()):
        if not _has(sha):
            raise Skip("commit %s is not in this checkout" % sha[:8])


def _read(rel):
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        raise AssertionError("%s is missing" % rel)
    return open(p, encoding="utf-8").read()


_C = {}


def _show(rev, path):
    if (rev, path) not in _C:
        _C[(rev, path)] = _git("show", "%s:%s" % (rev, path)).split("\n")
    return _C[(rev, path)]


def _facts(c):
    ps = _git("rev-list", "--parents", "-n1", c).split()[1:]
    date, subj = _git("log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%ad%x09%s", c).rstrip("\n").split("\t", 1)
    st = _git("diff", "--name-status", ps[0], c) if len(ps) > 1 else _git("show", "--name-status", "--format=", c)
    files = [(ln.split("\t")[0][0], ln.split("\t")[-1]) for ln in st.splitlines() if ln.strip()]
    return ps, date, subj, files


def _order():
    """[(row number, branch, full sha, parents, date, subject, [(status, path)])] in the chain's merge order."""
    if "order" in _C:
        return _C["order"]
    _need_git()
    out, n = [], 0
    for name, base, tip, firstparent in BRANCHES:
        old = set(_git("rev-list", "%s..%s" % (base, LATE[name])).split()) if name in LATE else None
        late = []
        if not firstparent:
            for c in _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (base, tip)).split():
                if old is not None and c not in old:
                    late.append(c)
                    continue
                n += 1
                out.append((str(n), name, c) + _facts(c))
        else:
            for c in _git("rev-list", "--first-parent", "--reverse", "%s..%s" % (base, tip)).split():
                if old is not None and c not in old:
                    late.append(c)
                    continue
                n += 1
                f = _facts(c)
                out.append((str(n), name, c) + f)
                if len(f[0]) > 1:
                    for k, b in enumerate(_git("rev-list", "--topo-order", "--reverse", "%s..%s" % (f[0][0], f[0][1])).split(), 1):
                        out.append(("%d.%d" % (n, k), name, b) + _facts(b))
        for k, c in enumerate(late):   # W170-D1: past W165's tip, the old tip's row number with a letter (none of them is a merge)
            f = _facts(c)
            if len(f[0]) > 1:
                raise AssertionError("a merge %s past %s's old tip: its branch commits would need rows of their own" % (c[:8], name))
            out.append(("%d%s" % (n, "abcdefghij"[k]), name, c) + f)
    _C["order"] = out
    return out


def _reviewed():
    if "rev" not in _C:
        _C["rev"] = set(_git("diff", "--name-only", CX45, REVIEWED).split()) | set(L4E9_EXTRA)
    return _C["rev"]


def _tree():
    if "tree" not in _C:
        _C["tree"] = set(_git("ls-tree", "-r", "--name-only", REVIEWED).split("\n")) - {""}
    return _C["tree"]


def _rows(text):
    sec = text.split("\n## 1. ", 1)[1].split("\n## 2. ", 1)[0]
    return [[c.strip() for c in CELL_SPLIT.split(ln.strip())[1:-1]] for ln in sec.split("\n")
            if ln.startswith("| ") and not ln.startswith("| # ")]


def _placeholder_row(cells):
    return cells[1] == "not determined" or bool(re.match(r"`(__[A-Z]+__|[0-9a-f]{8,40})`$", cells[1]))


def _real(text):
    """The branch rows: section 1's rows of the four ranges (W219: the integration's rows 64.x are read by p_integ, so the branch counts
    and the bound statement keep their scope, the 78 branch commits)."""
    return [c for c in _rows(text) if not _placeholder_row(c) and not INTEG_ROW.fullmatch(c[0])]


def _line(text, prefix):
    return [ln for ln in text.split("\n") if ln.startswith(prefix)][0]


def _classes(cells):
    return [c.strip() for c in cells[6].split(" + ")]


def _folder(p):
    if p.startswith("v2/vendor/"):
        return "v2/vendor/"
    if p.startswith("v2/ecad/tools/"):
        return "v2/ecad/tools/"
    return os.path.dirname(p) + "/"


def _texts():
    return {RESULT: _read(RESULT), CLASS: _read(CLASS), PATCH: _read(PATCH)}


def _mutant_refused(pred, texts, name, old, new, *extra):
    t = dict(texts)
    assert old in t[name], "the mutation's anchor %r is not in %s" % (old[:60], name)
    t[name] = t[name].replace(old, new, 1)
    assert pred(t, *extra), "%s passed a mutant (%r)" % (pred.__name__, new[:60])


# ---- predicates (each returns the list of what is wrong) ----

def p_hygiene(texts):
    bad = []
    for name, t in texts.items():
        for d in DASHES:
            if d in t:
                bad.append("%s carries %r" % (name, d))
        head = t.split("\n\n", 2)[1] if "\n\n" in t else ""
        for w in ("**DONE:**", "**NOT DONE:**", "**NEXT:**"):
            if w not in head:
                bad.append("%s's state paragraph lacks %s" % (name, w))
        if "nothing in the kit" not in t.lower() and "nothing in the kit has been" not in t:
            bad.append("%s lacks the prototype framing" % name)
    return bad


def _stage(result):
    named = {}
    for role, anchor, tok in ROLES:
        line = [ln for ln in result.split("\n") if ln.startswith(anchor)]
        if len(line) != 1:
            return None, "the role row %r is not there once" % anchor
        cell = CELL_SPLIT.split(line[0])[2].strip()
        if cell == "`%s`" % tok:
            named[role] = None
        else:
            m = re.match(r"`([0-9a-f]{8,40})`$", cell)
            if not m:
                return None, "the role row %r reads %r" % (anchor, cell)
            named[role] = m.group(1)
    seq = [named[r] is not None for r, _a, _t in ROLES]
    if seq == [False] * 4:
        return 0, named
    if seq == [True, True, True, False]:
        return 1, named
    if seq == [True] * 4:
        return 2, named
    return None, "a partial fill: %s" % named


def p_placeholders(texts):
    bad = []
    st, named = _stage(texts[RESULT])
    if st is None:
        return [named]
    for name, t in texts.items():
        for m in PH.finditer(t):
            if m.group(0) not in DECLARED:
                bad.append("%s carries an undeclared token %s" % (name, m.group(0)))
        for ln in t.split("\n"):
            if "__PROMOTED__" in ln and "| BASE (the REVIEWED role" in ln:
                bad.append("%s gives PROMOTED a BASE row (adopt33.sh's rule would fill set 32's revision there)" % name)
    # W219: no integration row 64.x carries a token (W78's rule for row 31 of set 32, kept for the rows that replace row 64), and rows
    # 65 and 66 carry git's date and a class of the fixed set since their commits exist (W80's "not determined" held while none did)
    for c in _rows(texts[CLASS]):
        if INTEG_ROW.fullmatch(c[0]) and any(PH.search(x) for x in c):
            bad.append("row %s carries a token" % c[0])
        if _placeholder_row(c) and (c[2] == "not determined" or any(k not in FIXED for k in _classes(c))):
            bad.append("the token row %s carries no date or a class outside the fixed set" % c[0])
    if st == 0:
        cl = texts[CLASS]
        for tok in ("__REKEY__", "__CANDIDATE__"):
            if cl.count(tok) != 1:
                bad.append("the classification carries %s %d times, not once (rows 65 and 66)" % (tok, cl.count(tok)))
        if texts[RESULT].count("__ADOPTION__") != 1:
            bad.append("RESULT carries ADOPTION %d times, not once" % texts[RESULT].count("__ADOPTION__"))
    if st >= 1:
        for name, t in texts.items():
            for tok in ("__REKEY__", "__CANDIDATE__", "__PROMOTED__", "__GATE__"):
                if tok in t:
                    bad.append("%s still carries %s at stage %d" % (name, tok, st))
    if st == 2 and any("__ADOPTION__" in t for t in texts.values()):
        bad.append("ADOPTION left at stage 2")
    for role, sha in named.items():
        if sha and not _has(sha):
            bad.append("the role %s names %s, which is not a commit here" % (role, sha))
    if named.get("CANDIDATE") and named.get("PROMOTED") and not named["CANDIDATE"].startswith(named["PROMOTED"][:8]):
        bad.append("set 33's promotion is not the candidate")
    for role in ("REKEY", "CANDIDATE"):
        if named.get(role) and _has(named[role]):
            for b in BRANCHES:
                if not _anc(b[2], named[role]):
                    bad.append("the %s %s does not hold %s's tip" % (role, named[role][:8], b[0]))
    if named.get("ADOPTION") and named.get("CANDIDATE") and not _anc(named["CANDIDATE"], named["ADOPTION"]):
        bad.append("the adoption does not descend from the candidate")
    return bad


def p_coverage(text, order):
    rows = _real(text)
    got = [(c[0], (re.match(r"`([0-9a-f]{8})` / `([0-9a-f]{40})`$", c[1]) or re.match("(x)(x)", "xx")).group(2)) for c in rows]
    want = [(o[0], o[2]) for o in order]
    if got != want:
        miss = [w for w in want if w not in got][:3]
        extra = [g for g in got if g not in want][:3]
        return ["the table is not the four ranges in order: missing %s, extra %s" % (miss, extra)]
    # W219: row 64 ("not determined", W75's F11) is replaced by the rows 64.x written from git (p_integ), so the rows whose sha cell is
    # one code span are 65 and 66 alone
    tail = [c[0] for c in _rows(text) if _placeholder_row(c)]
    if tail != ["65", "66"]:
        return ["the token rows are %s, not 65 and 66" % tail]
    return []


def _tail(files, merge):
    rev = sorted({os.path.basename(p) for _s, p in files if p in _reviewed()})
    tree = sorted({p for _s, p in files if p in _tree() and p not in _reviewed()})
    outs = sorted({os.path.basename(p) for _s, p in files if p.endswith(".out")})
    drafts = sorted({os.path.basename(p) for _s, p in files if os.path.basename(p).startswith("apply_gen_sch_") and "/inputs/" not in p})
    return rev, tree, outs, drafts, "brings" if merge else "touches"


def _named(reason, lead):
    m = re.search(re.escape(lead) + r" \((\d+)(?:, [^)]*)?\): (.*?)(?:;|$)", reason)
    return (int(m.group(1)), re.findall(r"`([^`]+)`", m.group(2))) if m else (0, [])


def p_columns(text, order):
    bad = []
    by = {o[0]: o for o in order}
    for c in _real(text):
        o = by.get(c[0])
        if not o or len(c) != 8:
            bad.append("row %s is not one of the ranges' commits or has %d cells" % (c[0], len(c)))
            continue
        num, branch, full, ps, date, subj, files = o
        if c[1] != "`%s` / `%s`" % (full[:8], full):
            bad.append("row %s's sha cell is not git's" % num)
        if c[2] != date:
            bad.append("row %s's date %s is not git's %s" % (num, c[2], date))
        if c[3] != subj.replace("|", "\\|"):
            bad.append("row %s's subject is not git's" % num)
        lab = c[4].split(" (", 1)[0]
        if lab not in LABEL_TIPS or not _anc(full, LABEL_TIPS[lab]):
            bad.append("row %s's branch label %s does not hold its commit" % (num, lab))
        cnt = Counter(_folder(p) for _s, p in files)
        fc = "%d: %s" % (len(files), ", ".join("%s (%d)" % (k, cnt[k]) for k in sorted(cnt)))
        if c[5] != fc:
            bad.append("row %s's files cell %r is not git's %r" % (num, c[5][:60], fc[:60]))
        cls = _classes(c)
        if any(x not in FIXED for x in cls) or len(set(cls)) != len(cls):
            bad.append("row %s's classes %s are not W39's fixed set" % (num, cls))
        if (cls[0] == "MERGE") != (len(ps) > 1):
            bad.append("row %s: MERGE first is not the merge commits" % num)
        rev, tree, outs, drafts, verb = _tail(files, len(ps) > 1)
        reason = c[7]
        n, names = _named(reason, "reviewed files it %s" % verb)
        if rev:
            if n != len(rev) or sorted(names) != rev or not reason.endswith("UNREVIEWED since cx46"):
                bad.append("row %s: its reviewed files %s are not git's %s, or it lacks UNREVIEWED since cx46" % (num, names, rev))
        elif not reason.endswith("no file cx46 read") or "UNREVIEWED since cx46" in reason:
            bad.append("row %s touches no file cx46 read but does not end so" % num)
        n, names = _named(reason, "files of the reviewed tree outside the delta cx46 read it %s" % verb)
        if sorted(names) != tree:
            bad.append("row %s: its files of the reviewed tree %s are not git's %s" % (num, names, tree))
        if sorted(_named(reason, "outputs committed")[1]) != outs:
            bad.append("row %s: its outputs are not git's %s" % (num, outs))
        if sorted(_named(reason, "circuit drafts touched")[1]) != drafts:
            bad.append("row %s: its drafts are not git's %s" % (num, drafts))
        if cls[0] == RIC and not any(p in _tree() for _s, p in files):
            bad.append("row %s is REVIEWED-INPUT CHANGED but touches no file of the reviewed tree" % num)
        if cls[0] == RIC and not GIT_ANCHOR.search(reason):
            bad.append("row %s is REVIEWED-INPUT CHANGED but quotes no line" % num)
    return bad


def _first(text):
    return Counter(_classes(c)[0] for c in _real(text))


def _branch_of(num):
    n = int(re.match(r"\d+", num).group(0))   # W170-D1: a row past an old tip reads 17a or 47b
    return "fnd/l4k" if n <= 5 else "fnd/l4hoe" if n <= 17 else "fnd/l4hod" if n <= 47 else "fnd/l4rowc"


def _touching(text, order):
    by = {o[0]: o for o in order}
    out = []
    for c in _real(text):
        files = by[c[0]][6]
        if len(by[c[0]][3]) == 1 and any(p in _reviewed() for _s, p in files):
            out.append((c[0], by[c[0]][2], sorted({p for _s, p in files if p in _reviewed()})))
    return out


def p_summary(texts, order):
    bad = []
    text, result = texts[CLASS], texts[RESULT]
    real = _real(text)
    first = _first(text)
    anyc = Counter(x for c in real for x in set(_classes(c)))
    sec = text.split("\n## 2. ", 1)[1].split("\n## 3. ", 1)[0]
    for cls in FIXED:
        if "| `%s` | %d | %d |" % (cls, first[cls], anyc[cls]) not in sec:
            bad.append("section 2's row for %s is not the table's %d and %d" % (cls, first[cls], anyc[cls]))
    if "| total | %d | |" % len(real) not in sec:
        bad.append("section 2's total is not %d" % len(real))
    per = {}
    for c in real:
        per.setdefault(_branch_of(c[0]), Counter())[_classes(c)[0]] += 1
    for b, cnt in per.items():
        words = ", ".join("%s %d" % (k, cnt[k]) for k in FIXED if cnt[k])
        if "%s, %d rows: %s" % (b, sum(cnt.values()), words) not in sec:
            bad.append("section 2's per-branch line for %s is not %r" % (b, words))
    t = _touching(text, order)
    touches = sum(len(x[2]) for x in t)
    distinct = len({p for x in t for p in x[2]})
    listed = ", ".join("`%s` (%s)" % (x[1][:8], x[0]) for x in t)
    if " ".join(listed.split()) not in " ".join(sec.split()):
        bad.append("section 2's touching rows are not the table's: %s" % listed[:80])
    if "**The rows that touch a file cx46 read: %d, all UNREVIEWED since cx46.**" % len(t) not in sec:
        bad.append("section 2 does not count %d touching rows" % len(t))
    flat = " ".join(sec.split())
    if "%d file touches among them" % touches not in flat or "(%d distinct files)" % distinct not in flat.replace("(%d distinct\nfiles)" % distinct, ""):
        bad.append("section 2's file touches or distinct files are not %d and %d" % (touches, distinct))
    newc = sum(1 for c in real if c[7].startswith(NEW))
    if "**The rows of new engineering content outside the reviewed tree (D-W165-1): %d**" % newc not in sec:
        bad.append("section 2's new-engineering count is not %d" % newc)
    bound = " ".join(sec.split("**The statement RESULT.md binds**", 1)[1].split("**Not determined here:**", 1)[0].replace(">", " ").split())
    want = ("By first class: %d REVIEWED-INPUT CHANGED first, %d RECORD TEXT first, %d TEST first, %d MERGE first, %d TOOLING first."
            % (first[RIC], first["RECORD TEXT"], first["TEST"], first["MERGE"], first["TOOLING"]))
    for w in (want, "carry %d commits over their bases" % len(real), "%d of the %d touch a file cx46 read (%d file touches, %d distinct files)"
              % (len(t), len(real), touches, distinct), "%d rows carry new engineering content" % newc):
        if w not in bound:
            bad.append("the bound statement lacks %r" % w)
    r = " ".join(result.split())
    rw = ("first class per row: REVIEWED-INPUT CHANGED %d; RECORD TEXT %d; GENERATOR DATA (text) %d; TEST %d; DIGEST RE-PIN %d; MERGE %d; "
          "TOOLING %d; total %d." % (first[RIC], first["RECORD TEXT"], first["GENERATOR DATA (text)"], first["TEST"], first["DIGEST RE-PIN"],
                                    first["MERGE"], first["TOOLING"], len(real)))
    for w in (rw, "%d of the %d touch a file cx46 read (%d distinct files)" % (len(t), len(real), distinct),
              "%d rows carry new engineering content" % newc):
        if w not in r:
            bad.append("RESULT.md lacks %r" % w[:80])
    return bad


def p_quotes(texts):
    bad = []
    for name, t in texts.items():
        for sha, path, n, q in GIT_ANCHOR.findall(t):
            q = q.replace("\\|", "|")
            if not _has(sha):
                bad.append("%s: %s is not in this repository" % (name, sha))
                continue
            lines = _show(sha, path)
            if int(n) > len(lines) or q not in lines[int(n) - 1]:
                bad.append("%s: %r is not on %s:%s:%s" % (name, q[:60], sha[:8], path, n))
    return bad


def p_commits_named(texts):
    bad = []
    for name, t in texts.items():
        for h in set(HEXTOK.findall(t)):
            if h in NONCOMMIT or _has(h):
                continue
            bad.append("%s names %s, which is no commit here and no declared digest" % (name, h))
    return bad


def p_rule(text, s30_lines):
    want = s30_lines[10]
    if "> " + want not in text:
        return ["the rule is not set 30's line 11 verbatim"]
    if "reading A" not in text or "`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`" not in text:
        return ["the rule paragraph does not cite its line and reading A"]
    return []


def p_claims(result, assess_lines):
    bad = []
    for n, words in CLAIMS.items():
        if assess_lines[n - 1].rstrip() != words:
            bad.append("the assessment's line %d is not %r" % (n, words))
        if "`%s:%s:%d` `%s`" % (PROMOTED32[:8], ASSESS, n, words) not in result:
            bad.append("RESULT.md does not quote line %d verbatim" % n)
    sec = result.split("\n## 6. ", 1)[1].split("\n## 7. ", 1)[0]
    for claim, state in (("Engineering-handover readiness", "READY AS A DESK PACKAGE OF OPEN ITEMS"),
                         ("Power-design closure", "BLOCKED"), ("Fabrication release", "BLOCKED")):
        if "| %s | %s |" % (claim, state) not in sec:
            bad.append("section 6 does not give %s as %s" % (claim, state))
    if "**Set 33 closes NO power item.**" not in sec or "**Layer 4's DESK gate stays NOT PASSED**" not in sec:
        bad.append("section 6 does not say that set 33 closes no power item and the DESK gate stays NOT PASSED")
    for wrong in ("DESK gate: PASSED", "DESK gate PASSED", "closure: CLOSED", "release: RELEASED", "Set 33 closes the", "SUPPORTED AS CONDITIONAL AND ACCEPTED"):
        if wrong in result:
            bad.append("RESULT.md reads %r" % wrong)
    return bad


def p_bounds(text):
    """No board generator, netlist or schematic and no draft present at 4d0ff8a2 changed on the ranges; the new drafts are the ones named."""
    bad = []
    names = set()
    for _n, base, tip, _fp in BRANCHES:
        names |= set(_git("diff", "--name-only", base, tip).split())
    for p in names:
        b = os.path.basename(p)
        if b.startswith("gen_sch_") or p.endswith(".net") or p.endswith(".kicad_sch"):
            bad.append("the ranges change %s" % p)
        if b.startswith("apply_gen_sch_") and p in _tree():
            bad.append("the ranges change a draft present at 4d0ff8a2: %s" % p)
    drafts = sorted({os.path.basename(p) for p in names if os.path.basename(p).startswith("apply_gen_sch_") and "/inputs/" not in p})
    head = text.split("\n## 1. ", 1)[0]
    m = re.search(r"(\w+) NEW circuit drafts are\s+committed \((.*?)\) with one new", head, re.S)
    if not m or sorted(x for x in re.findall(r"`([^`]+)`", m.group(2)) if x.startswith("apply_gen_sch_")) != drafts:
        bad.append("the bounds' list of new drafts is not git's %s" % drafts)
    elif m.group(1) != {7: "seven"}.get(len(drafts)):
        bad.append("the bounds' draft count word is not git's %d" % len(drafts))
    return bad


def _integ_order():
    """W219: the integration's rows from git, [(row, branch, full sha, parents, date, subject, files)] in _order()'s shape: the first-parent
    commits of CHAIN_BASE..CAND_AT oldest first, the first six as rows 64.1 to 64.6 and the further ones before the re-key as 64.7.1 onward
    (the prepared row 64.7: each further first-parent commit before the re-key, one row each), after each merge the commits its second
    parent brings that no branch range holds as <row>.<k> (their branch from the merge's subject, "fnd/<name> <sha> merged"), then the
    re-key's cache commit (65) and the candidate (66)."""
    if "integ" in _C:
        return _C["integ"]
    for s in (CHAIN_BASE, REKEY_AT, CAND_AT) + tuple(INTEG_TIPS.values()):
        if not _has(s):
            raise Skip("commit %s is not in this checkout" % s[:8])
    ranged = {o[2] for o in _order()}
    fp = _git("rev-list", "--first-parent", "--reverse", "%s..%s" % (CHAIN_BASE, CAND_AT)).split()
    if fp[-2:] != [REKEY_AT, CAND_AT]:
        raise AssertionError("the first-parent line %s..%s does not end with the cache commit and the candidate" % (CHAIN_BASE[:8], CAND_AT[:8]))
    out = []
    for i, c in enumerate(fp[:-2], 1):
        num = "64.%d" % i if i <= 6 else "64.7.%d" % (i - 6)
        f = _facts(c)
        out.append((num, "fnd/int33", c) + f)
        if len(f[0]) > 1:
            m = re.search(r"(fnd/[\w-]+) [0-9a-f]{8} merged", f[2])
            brought = [s for s in _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (f[0][0], f[0][1])).split() if s not in ranged]
            for k, s in enumerate(brought, 1):
                out.append(("%s.%d" % (num, k), m.group(1) if m else "(no branch in the merge's subject)", s) + _facts(s))
    out.append(("65", "fnd/int33", REKEY_AT) + _facts(REKEY_AT))
    out.append(("66", "fnd/int33", CAND_AT) + _facts(CAND_AT))
    _C["integ"] = out
    return out


def _integ_rows(text):
    return [c for c in _rows(text) if INTEG_ROW.fullmatch(c[0]) or c[0] in ("65", "66")]


def p_integ(text):
    """W219 (Q-242): the integration's rows are git's, row for row (_integ_order): sha cells (rows 65 and 66: their token, or after the fill
    the same commit), author dates, subjects, branches whose tips hold the commit, file counts and folders against the first parent,
    classes of the fixed set with MERGE exactly on two-parent commits, the reviewed files touched or brought with UNREVIEWED since cx46
    (or "no file cx46 read"), the files of the reviewed tree outside the delta, a REVIEWED-INPUT CHANGED row quoting a line under reading
    A with earlier source rows and the delta membership, a merge naming the first row it brings; and the lineage: 65's first parent the
    last row 64.x on the first-parent line, 66's row 65."""
    bad = []
    order = _integ_order()
    got = _integ_rows(text)
    if [c[0] for c in got] != [o[0] for o in order]:
        return ["the integration's rows are %s, not git's %s" % ([c[0] for c in got], [o[0] for o in order])]
    nums = [c[0] for c in _rows(text)]
    last64 = [o for o in order if o[1] == "fnd/int33" and o[0] not in ("65", "66")][-1][2]
    if _git("rev-list", "--parents", "-n1", REKEY_AT).split()[1:2] != [last64] or _git("rev-list", "--parents", "-n1", CAND_AT).split()[1:2] != [REKEY_AT]:
        bad.append("the cache commit and the candidate are not the next commits on the first-parent line after %s" % last64[:8])
    for c, (num, branch, full, ps, date, subj, files) in zip(got, order):
        if len(c) != 8:
            bad.append("row %s has %d cells" % (num, len(c)))
            continue
        if num in INTEG_TOK:
            m = re.match(r"`(__[A-Z]+__|[0-9a-f]{8,40})`$", c[1])
            if not m or (m.group(1).startswith("__") and m.group(1) != INTEG_TOK[num]) or (not m.group(1).startswith("__") and not full.startswith(m.group(1))):
                bad.append("row %s's sha cell %r is neither its token nor %s" % (num, c[1][:30], full[:8]))
        elif c[1] != "`%s` / `%s`" % (full[:8], full):
            bad.append("row %s's sha cell is not git's" % num)
        if c[2] != date:
            bad.append("row %s's date %s is not git's %s" % (num, c[2], date))
        if c[3] != subj.replace("|", "\\|"):
            bad.append("row %s's subject is not git's" % num)
        if not c[4].startswith(branch + (": " if branch == "fnd/int33" else " (")) or branch not in INTEG_TIPS or not _anc(full, INTEG_TIPS[branch]):
            bad.append("row %s's branch cell does not name %s, or its tip does not hold the commit" % (num, branch))
        cnt = Counter(_folder(p) for _s, p in files)
        fc = "%d: %s" % (len(files), ", ".join("%s (%d)" % (k, cnt[k]) for k in sorted(cnt)))
        if c[5] != fc:
            bad.append("row %s's files cell %r is not git's %r" % (num, c[5][:60], fc[:60]))
        cls = _classes(c)
        if any(x not in FIXED for x in cls) or len(set(cls)) != len(cls):
            bad.append("row %s's classes %s are not W39's fixed set" % (num, cls))
        if (cls[0] == "MERGE") != (len(ps) > 1) or "MERGE" in cls[1:]:
            bad.append("row %s: MERGE and the commit's parents disagree" % num)
        rev, tree, _outs, _drafts, verb = _tail(files, len(ps) > 1)
        reason = c[7]
        n, names = _named(reason, "reviewed files it %s" % verb)
        if rev:
            if n != len(rev) or sorted(names) != rev or not reason.endswith("UNREVIEWED since cx46"):
                bad.append("row %s: its reviewed files %s are not git's %s, or it lacks UNREVIEWED since cx46" % (num, names, rev))
        elif not reason.endswith("no file cx46 read") or "UNREVIEWED since cx46" in reason:
            bad.append("row %s touches no file cx46 read but does not end so" % num)
        n, names = _named(reason, "files of the reviewed tree outside the delta cx46 read it %s" % verb)
        if sorted(names) != tree:
            bad.append("row %s: its files of the reviewed tree %s are not git's %s" % (num, names, tree))
        if cls[0] == RIC:
            src = re.search(r"\(rows? ([\d., a-z]+?) the source rows?; in the delta cx46 read\)", reason)   # row numbers, "to", "and" only
            if not any(p in _tree() for _s, p in files) or not GIT_ANCHOR.search(reason) or "reading A" not in reason or not src:
                bad.append("row %s is %s without a quoted line, reading A, its source rows and the delta membership" % (num, RIC))
            elif any(x not in nums or nums.index(x) >= nums.index(num) for x in re.findall(r"\d+(?:\.\d+)*[a-z]?", src.group(1))):
                bad.append("row %s: its source rows %r are not earlier rows of this table" % (num, src.group(1)))
        if len(ps) > 1 and any(o[0].startswith(num + ".") for o in order) and not re.search(r"\brows? %s\.1\b" % re.escape(num), reason):
            bad.append("the merge's row %s does not name the first row it brings, %s.1" % (num, num))
    return bad


def p_integ_summary(text):
    """W219: section 2's part for the integration's rows is the table's: per class first and carried, the total, the touching rows in
    table order (a row whose sha cell is the fill's token is named by its number), their file touches and distinct files, and the whole
    table's count."""
    bad = []
    rows = _integ_rows(text)
    sec = text.split("\n## 2. ", 1)[1]
    if "**The integration's rows**" not in sec or "**Not determined here:**" not in sec:
        return ["section 2 has no part for the integration's rows"]
    part = sec.split("**The integration's rows**", 1)[1].split("**Not determined here:**", 1)[0]
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    for k in FIXED:
        m = re.search(r"^\| `%s` \| (\d+) \| (\d+) \|$" % re.escape(k), part, re.M)
        if not m or int(m.group(1)) != first[k] or int(m.group(2)) != carry[k]:
            bad.append("the integration's summary row of %s is not the table's (%d, %d)" % (k, first[k], carry[k]))
    m = re.search(r"^\| integration total \| (\d+) \|", part, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the integration's total is not the table's %d" % len(rows))
    flat = " ".join(part.split())
    touch = [c for c in rows if c[7].endswith("UNREVIEWED since cx46")]
    named = [_named(c[7], "reviewed files it brings" if _classes(c)[0] == "MERGE" else "reviewed files it touches") for c in touch]
    nft, distinct = sum(n for n, _x in named), len({x for _n, xs in named for x in xs})
    m = re.search(r"\*\*The integration's rows that touch a file cx46 read: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?); "
                  r"(\d+) file touches among them, each named in its row \((\d+) distinct files", flat)
    if not m or (int(m.group(1)), int(m.group(3)), int(m.group(4))) != (len(touch), nft, distinct):
        bad.append("the integration's touching-rows line is not the table's %d rows, %d file touches, %d distinct files" % (len(touch), nft, distinct))
    else:
        got = re.findall(r"`([0-9a-f]{8})` \(([\d.]+)\)|row (\d+) \(the candidate", m.group(2))
        want = [(c[1][1:9], c[0], "") if not _placeholder_row(c) else ("", "", c[0]) for c in touch]
        if got != want:
            bad.append("the integration's touching-rows list is not the table's rows in order")
    m = re.search(r"\*\*The whole table:\*\* (\d+) rows, the (\d+) branch rows of the four ranges and the integration's (\d+)\.", flat)
    nb = len(_real(text))
    if not m or (int(m.group(1)), int(m.group(2)), int(m.group(3))) != (nb + len(rows), nb, len(rows)):
        bad.append("the whole table's count is not %d (%d branch rows and %d integration rows)" % (nb + len(rows), nb, len(rows)))
    return bad


def p_nofill(texts):
    """W219 (W132's F2 for set 32): no fill-in cell of the coordinator's ("[FILL") is left in either record."""
    return ["%s holds %d fill-in cell(s)" % (n, t.count("[FILL")) for n, t in texts.items() if "[FILL" in t]


def p_logs(texts, runs):
    bad = []
    for name, t in texts.items():
        for rel, n, entry, q in RUN_ANCHOR.findall(t):
            p = os.path.join(runs, rel)
            if not os.path.isfile(p):
                bad.append("%s: _runs/%s is missing" % (name, rel))
                continue
            body = open(p, encoding="utf-8", errors="replace").read()
            q = q.replace("\\|", "|")
            if n:
                lines = body.split("\n")
                if int(n) > len(lines) or q not in lines[int(n) - 1]:
                    bad.append("%s: _runs/%s:%s does not read %r" % (name, rel, n, q[:60]))
            elif entry:
                if not [ln for ln in body.split("\n") if entry in ln and q in ln]:
                    bad.append("%s: _runs/%s has no entry %r carrying %r on its line" % (name, rel, entry[:40], q[:40]))
            elif q not in body:
                bad.append("%s: _runs/%s does not carry %r" % (name, rel, q[:60]))
    return bad


def p_fill(src):
    """fill_res.py (or its .new) carries SETS["33"]: the record's two files, its patch folder and the four pages, read with ast."""
    tree = ast.parse(src)
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                consts[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
            if node.targets[0].id == "SETS":
                sets = node.value
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple) and isinstance(node.value, ast.Tuple):
            for k, v in zip(node.targets[0].elts, node.value.elts):
                if isinstance(k, ast.Name) and isinstance(v, ast.Constant):
                    consts[k.id] = v.value

    def val(e):
        if isinstance(e, ast.Constant):
            return e.value
        if isinstance(e, ast.Name):
            return consts.get(e.id)
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
            a, b = val(e.left), val(e.right)
            return a + b if isinstance(a, str) and isinstance(b, str) else None
        if isinstance(e, ast.List):
            return [val(x) for x in e.elts]
        return None
    for k, v in zip(sets.keys, sets.values):
        if val(k) == "33":
            d = {val(a): b for a, b in zip(v.keys, v.values)}
            bad = []
            if val(d["files"]) != [RESULT, CLASS]:
                bad.append("SETS['33'] files are %s" % val(d["files"]))
            if val(d["patches"]) != REC + "/":
                bad.append("SETS['33'] patches is %s" % val(d["patches"]))
            if tuple(val(d["pages"]) or ()) != PAGES:
                bad.append("SETS['33'] pages are %s" % val(d["pages"]))
            if val(d["test"]) != "test_res33":
                bad.append("SETS['33'] test is %s" % val(d["test"]))
            return bad
    return ["fill_res.py has no SETS['33']"]


# ---- tests ----

def t_the_records_carry_no_dash_and_open_with_their_state_lines():
    texts = _texts()
    assert not p_hygiene(texts), p_hygiene(texts)
    _mutant_refused(p_hygiene, texts, RESULT, "**Set 33 closes NO power item.**", "**Set 33 closes NO power item.** —")
    _mutant_refused(p_hygiene, texts, CLASS, "**NOT DONE:**", "**NOT YET:**")
    _mutant_refused(p_hygiene, texts, PATCH, "**NEXT:**", "**LATER:**")


def t_every_placeholder_is_a_declared_token_and_the_stage_holds():
    _need_git()
    texts = _texts()
    assert not p_placeholders(texts), p_placeholders(texts)
    _mutant_refused(p_placeholders, texts, RESULT, "| The chain's base: set 32's adopted tip on main |", "| The chain's base: set 32's adopted tip on main | `__BASE__` |")
    _mutant_refused(p_placeholders, texts, PATCH, "**The revision rows, as set 30's pages define them.**", "**The revision rows, as set 30's pages define them.** `__REVISION__`")
    _mutant_refused(p_placeholders, texts, RESULT, "| Set 32's promoted revision (the REVIEWED role of the brief's form) |",
                    "| BASE (the REVIEWED role of the brief's form) | `__PROMOTED__` |")
    _mutant_refused(p_placeholders, texts, RESULT, "| ADOPTED: the commit that adopts this record |", "| ADOPTED: the commit that adopts this record | `deadbeef`")
    # W219: a token in an integration row (C1's) and row 65's date taken back to "not determined" are refused
    r646, r65 = _line(texts[CLASS], "| 64.6 |"), _line(texts[CLASS], "| 65 |")
    _mutant_refused(p_placeholders, texts, CLASS, r646, r646.replace("; UNREVIEWED since cx46 |", "; UNREVIEWED since cx46 `__GATE__` |", 1))
    _mutant_refused(p_placeholders, texts, CLASS, r65, r65.replace("| 2026-10-07 21:39:14 |", "| not determined |", 1))


def t_the_table_is_the_four_ranges_in_order_with_gits_columns_and_classes():
    order = _order()
    # 78: W165's 75 and W167's three (basis: `git rev-list --count` 06d064ff..531c4754 13 and 06d064ff..92d81690 44, W170)
    assert len(order) == 78, len(order)
    assert [o[0] for o in order if not o[0].replace(".", "").isdigit()] == ["17a", "47a", "47b"], "the late rows are not 17a, 47a, 47b"
    text = _read(CLASS)
    assert not p_coverage(text, order), p_coverage(text, order)
    assert not p_columns(text, order), p_columns(text, order)[:5]
    t = {CLASS: text}
    rows = _real(text)
    r1 = "| " + " | ".join(rows[0]) + " |"
    assert r1 in text
    _mutant_refused(lambda x, o: p_coverage(x[CLASS], o), t, CLASS, r1 + "\n", "", order)
    r47b = [ln for ln in text.split("\n") if ln.startswith("| 47b | ")][0]   # W170: a late row dropped is refused too
    _mutant_refused(lambda x, o: p_coverage(x[CLASS], o), t, CLASS, r47b + "\n", "", order)
    # W219: a row 64 put back ("not determined", W75's F11) is refused: the token rows are 65 and 66 alone
    r65 = _line(text, "| 65 |")
    _mutant_refused(lambda x, o: p_coverage(x[CLASS], o), t, CLASS, r65,
                    "| 64 | not determined | not determined | the integration's commits | fnd/int33 | not determined | not determined | text |\n" + r65, order)
    _mutant_refused(lambda x, o: p_columns(x[CLASS], o), t, CLASS, "| 2026-10-07 04:39:01 |", "| 2026-10-07 04:39:02 |", order)
    _mutant_refused(lambda x, o: p_columns(x[CLASS], o), t, CLASS, "`l9t5_t10.out`, `l9t5_t10.py`; UNREVIEWED since cx46 |",
                    "`l9t5_t10.out`; UNREVIEWED since cx46 |", order)
    _mutant_refused(lambda x, o: p_columns(x[CLASS], o), t, CLASS, "| fnd/l4fet (W136, Q-158) |", "| fnd/l4lim (W136, Q-158) |", order)
    _mutant_refused(lambda x, o: p_columns(x[CLASS], o), t, CLASS, "(W143-F2, by its subject);",
                    "(W143-F2, by its subject); UNREVIEWED since cx46;", order)


def t_the_summary_and_the_bound_statement_are_the_tables():
    order = _order()
    texts = _texts()
    assert not p_summary(texts, order), p_summary(texts, order)
    # the anchors restated by W170 over the 78 rows (basis: the table with rows 17a, 47a, 47b read back by p_summary itself: 47a is a
    # REVIEWED-INPUT CHANGED row touching 5 reviewed files, 47b RECORD TEXT first, 17a TOOLING first and new engineering content)
    _mutant_refused(p_summary, texts, CLASS, "| `REVIEWED-INPUT CHANGED` | 12 | 12 |", "| `REVIEWED-INPUT CHANGED` | 11 | 12 |", order)
    _mutant_refused(p_summary, texts, CLASS, "fnd/l4k, 5 rows: RECORD TEXT 4, TEST 1", "fnd/l4k, 5 rows: RECORD TEXT 5", order)
    _mutant_refused(p_summary, texts, CLASS, "38 file touches among them", "33 file touches among them", order)
    _mutant_refused(p_summary, texts, RESULT, "RECORD TEXT 24; GENERATOR DATA (text) 0", "RECORD TEXT 23; GENERATOR DATA (text) 1", order)
    _mutant_refused(p_summary, texts, CLASS, "(D-W165-1): 39**", "(D-W165-1): 38**", order)


def t_every_quote_is_on_its_cited_line_and_every_commit_named_resolves():
    _need_git()
    texts = _texts()
    assert not p_quotes(texts), p_quotes(texts)[:5]
    assert not p_commits_named(texts), p_commits_named(texts)[:5]
    _mutant_refused(p_quotes, texts, RESULT, "`f08e3961:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:494` `The gate's own premise is not met.`",
                    "`f08e3961:v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md:495` `The gate's own premise is not met.`")
    _mutant_refused(p_quotes, texts, CLASS, "`06d064ff:v2/docs/records/l9t5/l9t5_t10.out:642` `T10-A3 at the trip's AVERAGE maximum",
                    "`06d064ff:v2/docs/records/l9t5/l9t5_t10.out:642` `T10-A3 at the trip's PEAK maximum")
    _mutant_refused(p_commits_named, texts, RESULT, "(fnd/l4k `ff0c79f0`,", "(fnd/l4k `ff0c79f1`,")


def t_the_rule_is_set_30s_line_11_verbatim_and_the_claims_the_assessments():
    _need_git()
    texts = _texts()
    s30 = _show(S30, S30C)
    assert not p_rule(texts[CLASS], s30), p_rule(texts[CLASS], s30)
    t = {CLASS: texts[CLASS]}
    _mutant_refused(lambda x, s: p_rule(x[CLASS], s), t, CLASS, "a circuit draft or a composition of drafts, a case row", "a circuit draft, a case row", s30)
    lines = _show(PROMOTED32, ASSESS)
    assert not p_claims(texts[RESULT], lines), p_claims(texts[RESULT], lines)
    r = {RESULT: texts[RESULT]}
    _mutant_refused(lambda x, a: p_claims(x[RESULT], a), r, RESULT, "| Power-design closure | BLOCKED |", "| Power-design closure | OPEN |", lines)
    _mutant_refused(lambda x, a: p_claims(x[RESULT], a), r, RESULT, "**Set 33 closes NO power item.**", "**Set 33 closes the power items.**", lines)


def t_the_bounds_are_gits():
    """W219: the prepared rows' half of this test (p_prepared, section 3) is gone with the section; the integration's rows are read by
    t_the_integration_rows_are_gits."""
    _need_git()
    text = _read(CLASS)
    assert not p_bounds(text), p_bounds(text)
    t = {CLASS: text}
    _mutant_refused(lambda x: p_bounds(x[CLASS]), t, CLASS, "`apply_gen_sch_b_hodtest.py`, `apply_gen_sch_a_fetpair.py`", "`apply_gen_sch_a_fetpair.py`")


def t_the_integration_rows_are_gits():
    """W219 (Q-242): rows 64.1 to 66 are git's row for row, section 2's integration part is theirs, and no fill-in cell is left; the
    basis is git itself (the commits exist on set 33's lineage, the candidate's) and the table."""
    texts = _texts()
    t = texts[CLASS]
    bad = p_integ(t) + p_integ_summary(t) + p_nofill(texts)
    assert not bad, bad
    r = {n: _line(t, "| %s |" % n) for n in ("64.3", "64.5", "64.5.1", "64.6", "64.7.1", "64.7.1.1", "65", "66")}
    mut = lambda old, new: t.replace(old, new, 1)
    assert p_integ(mut(r["64.6"], r["64.6"].replace("| 2026-10-07 17:49:27 |", "| 2026-10-07 17:49:28 |", 1))), "a wrong date passed"
    # the queue's clock (21:39:15) in place of git's author date (21:39:14) is refused
    assert p_integ(mut(r["65"], r["65"].replace("| 2026-10-07 21:39:14 |", "| 2026-10-07 21:39:15 |", 1))), "row 65 with the queue's clock passed"
    assert p_integ(mut(r["66"], r["66"].replace("| 6: ", "| 5: ", 1))), "row 66 with a wrong file count passed"
    c65, c66 = r["65"].split(" | ")[1], r["66"].split(" | ")[1]   # the sha cells as the stage holds them (tokens before the fill)
    assert p_integ(mut(r["66"], r["66"].replace("| %s |" % c66, "| %s |" % c65, 1))), "row 66 with row 65's sha cell passed"
    assert p_integ(t.replace(r["64.7.1"] + "\n", "", 1)), "the s33cite merge's row dropped passed"
    assert p_integ(t.replace(r["64.7.1.1"] + "\n", "", 1)), "the commit the s33cite merge brings dropped passed"
    assert p_integ(mut(r["64.7.1"], r["64.7.1"].replace("| MERGE |", "| TEST |", 1))), "a merge not classed MERGE passed"
    assert p_integ(mut(r["64.7.1.1"], r["64.7.1.1"].replace("| fnd/s33cite (", "| fnd/int33: (", 1))), "a brought commit outside its branch passed"
    # the facts table's 29 reviewed files (the 60 without the L4-E9 page and its output) in place of this table's 31 are refused
    assert p_integ(mut(r["64.6"], r["64.6"].replace("reviewed files it touches (31)", "reviewed files it touches (29)", 1))), "C1 with the facts table's count passed"
    assert p_integ(mut(r["64.6"], r["64.6"].replace("(rows 1, 37 to 39, 43.1 to 43.3, 45 and 47a the source rows; in the delta cx46 read)", "(in the delta cx46 read)", 1))), \
        "C1's REVIEWED-INPUT CHANGED without its source rows passed"
    assert p_integ(mut(r["66"], r["66"].replace("rows 1 and 64.6 the source rows", "rows 1 and 67 the source rows", 1))), "a source row that is not an earlier row passed"
    assert p_integ(mut(r["64.5.1"], r["64.5.1"].replace("| `799ae465` / ", "| `799ae466` / ", 1))), "a short sha not its full sha's passed"
    assert p_integ(mut(r["64.3"], r["64.3"].replace("; UNREVIEWED since cx46 |", " |", 1))), "a merge bringing cx46's files without UNREVIEWED passed"
    assert p_integ(mut("brings rows 64.5.1 to 64.5.9, this record's nine commits", "brings this record's nine commits")), "a merge not naming the rows it brings passed"
    assert p_integ_summary(mut("| integration total | 24 |", "| integration total | 23 |")), "a wrong integration total passed"
    assert p_integ_summary(mut("| `MERGE` | 7 | 7 |", "| `MERGE` | 6 | 7 |")), "a wrong integration class count passed"
    assert p_integ_summary(mut("; 57 file touches among them", "; 56 file touches among them")), "a wrong count of file touches passed"
    assert p_integ_summary(mut("**The whole table:** 102 rows", "**The whole table:** 101 rows")), "a wrong whole-table count passed"
    assert p_integ_summary(mut(r["64.7.1"], r["64.7.1"].replace("| MERGE |", "| TEST |", 1))), "a re-classed row with the old counts passed"
    assert p_nofill(dict(texts, **{RESULT: texts[RESULT] + "\n[FILL: a value]\n"})), "a fill-in cell left passed"


def t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote():
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    if not os.path.isdir(runs):
        raise Skip("the coordinator's _runs is not on this host (a rented box): the runner pass reads it")
    texts = _texts()
    assert not p_logs(texts, runs), p_logs(texts, runs)[:5]
    _mutant_refused(p_logs, texts, RESULT, "`<worktrees>/_runs/int33/dryrun-1120.log:17` `l4e7 KEY MATCH 6e11114faadda427`",
                    "`<worktrees>/_runs/int33/dryrun-1120.log:18` `l4e7 KEY MATCH 6e11114faadda427`", runs)
    _mutant_refused(p_logs, texts, RESULT, "`Verdict: SUPPORTED AS CONDITIONAL.**` | W145's", "`Verdict: SUPPORTED.**` | W145's", runs)


def t_the_fill_tool_carries_set_33():
    b = os.environ.get("MESHSAT_BIN") or os.path.join(os.path.dirname(REPO), "_bin")
    p = os.path.join(b, "fill_res.py")
    if os.path.isfile(p + ".new") and "\n    \"33\": {" not in open(p, encoding="utf-8").read():
        p += ".new"   # before the coordinator's swap: the record author's .new beside the live tool
    if not os.path.isfile(p):
        raise Skip("the coordinator's _bin is not on this host (a rented box): the runner pass reads it")
    src = open(p, encoding="utf-8").read()
    assert not p_fill(src), p_fill(src)
    assert p_fill(src.replace('"33": {"files": [R33 + "RESULT.md", R33 + "CLASSIFICATION.md"]', '"33": {"files": [R33 + "RESULT.md"]'))
    assert p_fill(src.replace('"test": "test_res33"', '"test": "test_res32x"'))


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
test_every_placeholder_is_a_declared_token_and_the_stage_holds = _pytest(t_every_placeholder_is_a_declared_token_and_the_stage_holds)
test_the_table_is_the_four_ranges_in_order_with_gits_columns_and_classes = _pytest(
    t_the_table_is_the_four_ranges_in_order_with_gits_columns_and_classes)
test_the_summary_and_the_bound_statement_are_the_tables = _pytest(t_the_summary_and_the_bound_statement_are_the_tables)
test_every_quote_is_on_its_cited_line_and_every_commit_named_resolves = _pytest(
    t_every_quote_is_on_its_cited_line_and_every_commit_named_resolves)
test_the_rule_is_set_30s_line_11_verbatim_and_the_claims_the_assessments = _pytest(
    t_the_rule_is_set_30s_line_11_verbatim_and_the_claims_the_assessments)
test_the_bounds_are_gits = _pytest(t_the_bounds_are_gits)
test_the_integration_rows_are_gits = _pytest(t_the_integration_rows_are_gits)
test_every_cited_file_of_the_coordinator_exists_and_carries_its_quote = _pytest(
    t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote)
test_the_fill_tool_carries_set_33 = _pytest(t_the_fill_tool_carries_set_33)
