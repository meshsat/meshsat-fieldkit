#!/usr/bin/env python3
"""Set 30's RESULT draft 3 (MESHSAT-1357, 6 October 2026): the draft names only commits that exist where it says, quotes only what
its sources print, keeps the three completion claims apart and lists exactly W15's unreviewed changes.

The draft is `v2/docs/records/int30/RESULT.draft3.md`, written on the integration's commit 2b `d83d9f2d` for the coordinator's
adoption as `records/int30/RESULT.md`. A citation `<sha>:path:N` followed by a code span quotes line N of that file at that revision;
`<worktrees>/_runs/<path>:N` followed by a code span quotes line N of a coordinator's log outside the tree, and the growing queue file
is quoted by its dated entry (`<worktrees>/_runs/int30/QUEUE.md`, entry "...", followed by the quote, found anywhere in the file).

What fails here: an em or en dash; a placeholder outside the fixed set, or one of the set missing; a commit sha in a code span that is
neither in fnd/p0pwr's history at 2b nor in the history of the `fnd/<branch>` written just before it; a quote not on its cited line
at its revision or not in its log; a test count ("N passed, M failed") or a time HH:MM:SS that is not in a verified quote, a cited log
or a commit date of the integration; a completion claim missing, doubled, blended with a percentage or carrying another state word;
an unreviewed-change list that differs from W15's REVIEWED-INPUT CHANGED rows, or a NOT ONLY NARROWING mark that differs from W15's
list of six; W16's FINDINGS not verbatim. Each predicate is also run on a mutant of the draft that it must refuse.

Read-only: git is read with `git show`, `git log`, `git cat-file` and `git merge-base`; the logs under `<worktrees>/_runs` are read
when present (a checkout without them raises Skip for the predicates that need them). Nothing is written. No pytest is needed
(tests/run.py runs the `t_` functions); `test_` aliases let pytest collect them."""
import os
import re
import subprocess

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
RUNS = os.path.join(os.path.dirname(os.path.dirname(REPO)), "meshsat-fieldkit", "_runs")
DRAFT = "v2/docs/records/int30/RESULT.draft3.md"
INTEG = "d83d9f2d720878ca5267dbf59bdc571c6890fd92"        # commit 2b, the integration's committed tip when the draft was written
W15 = "57bcdbfce095c461b4c3b6804ea8cc3508762577"          # W15's classification
W15_FILE = "v2/docs/records/int30/CLASSIFICATION.draft.md"
FIRST_INTEGRATION = "3d2746c9bdd9a17ad81e19889892e5691973eb63"
FIXED = ("__CANDIDATE__", "__PROMOTED__", "__MIRROR__", "__KEY__", "__GATE_BOX_PY312__", "__GATE_BOX_PY311__",
         "__GATE_RUNNER__", "__G7__", "__L6R2_FIX__", "__W19__")
CLAIMS = {"Engineering-handover readiness": "NOT YET ASSESSED", "Power-design closure": "BLOCKED",
          "Fabrication release": "BLOCKED"}

GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
RUN_ANCHOR = re.compile(r"`<worktrees>/_runs/([^`:\s]+)(?::(\d+))?`(?:, entry \"([^\"]+)\",)? `([^`]+)`")
SHA_SPAN = re.compile(r"`([0-9a-f]{7,40})`")
COUNT = re.compile(r"\d+ passed, \d+ failed")
TIME = re.compile(r"(?<![\d:])\d\d:\d\d:\d\d(?![\d:])")


def _flat(s):
    return " ".join(s.split())


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    return r


def _need_git():
    for sha in (INTEG, W15):
        if _git("cat-file", "-e", sha + "^{commit}").returncode != 0:
            raise Skip("commit %s not in this checkout" % sha[:8])


def _need_runs():
    if not os.path.isdir(os.path.join(RUNS, "int30")):
        raise Skip("the coordinator's logs (_runs) are not on this host")


def _draft():
    with open(os.path.join(REPO, DRAFT), encoding="utf-8") as f:
        return f.read()


def _show(sha, path):
    r = _git("show", "%s:%s" % (sha, path))
    if r.returncode != 0:
        return None
    return r.stdout


def _ancestor(sha, ref):
    return _git("merge-base", "--is-ancestor", sha, ref).returncode == 0


def _run_text(rel):
    p = os.path.join(RUNS, rel)
    if not os.path.isfile(p):
        return None
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


# ---------------------------------------------------------------- predicates (each returns a list of problems)

def p_hygiene(text):
    bad = []
    if "\u2014" in text or "\u2013" in text:
        bad.append("an em or en dash")
    if not text.startswith("**DONE:**"):
        bad.append("the first line is not the DONE / NOT DONE / NEXT line")
    for w in ("**NOT DONE:**", "**NEXT:**"):
        if w not in text.splitlines()[0]:
            bad.append("the first line lacks %s" % w)
    return bad


def p_placeholders(text):
    found = set(re.findall(r"__[A-Z0-9_]+__", text))
    bad = ["placeholder outside the fixed set: %s" % p for p in sorted(found - set(FIXED))]
    bad += ["placeholder of the fixed set missing: %s" % p for p in FIXED if p not in found]
    return bad


def p_shas(text):
    bad = []
    for m in SHA_SPAN.finditer(text):
        sha = m.group(1)
        if _git("cat-file", "-e", sha + "^{commit}").returncode != 0:
            bad.append("no such commit: %s" % sha)
            continue
        if _ancestor(sha, INTEG):
            continue
        before = text[max(0, m.start() - 60):m.start()]
        b = re.search(r"(fnd/[\w-]+)[ |]*$", before)
        if b and _git("rev-parse", "--verify", "-q", b.group(1)).returncode == 0 and _ancestor(sha, b.group(1)):
            continue
        bad.append("%s is neither in fnd/p0pwr's history at 2b nor in the branch named before it" % sha)
    return bad


def _verified_quotes(text, bad):
    """Check every anchor; return the list of quotes that were found where they are cited."""
    ok = []
    for m in GIT_ANCHOR.finditer(text):
        sha, path, n, quote = m.group(1), m.group(2), int(m.group(3)), m.group(4).replace("\\|", "|")
        body = _show(sha, path)
        if body is None:
            bad.append("%s:%s does not exist" % (sha, path))
            continue
        lines = body.splitlines()
        if n < 1 or n > len(lines) or _flat(quote) not in _flat(lines[n - 1]):
            bad.append("%s:%s:%d does not read %r" % (sha[:8], path, n, quote[:60]))
            continue
        ok.append(quote)
    for m in RUN_ANCHOR.finditer(text):
        rel, n, entry, quote = m.group(1), m.group(2), m.group(3), m.group(4)
        body = _run_text(rel)
        if body is None:
            bad.append("_runs/%s is missing" % rel)
            continue
        if entry and _flat(entry) not in _flat(body):
            bad.append("_runs/%s has no entry %r" % (rel, entry))
            continue
        if n:
            lines = body.splitlines()
            k = int(n)
            if k < 1 or k > len(lines) or _flat(quote) not in _flat(lines[k - 1]):
                bad.append("_runs/%s:%s does not read %r" % (rel, n, quote[:60]))
                continue
        elif _flat(quote) not in _flat(body):
            bad.append("_runs/%s does not carry %r" % (rel, quote[:60]))
            continue
        ok.append(quote)
    return ok


def p_anchors(text):
    bad = []
    q = _verified_quotes(text, bad)
    if len(q) < 30:
        bad.append("only %d anchors verified" % len(q))
    return bad


def _integration_times():
    env = dict(os.environ, TZ="Europe/Amsterdam")
    r = subprocess.run(["git", "-C", REPO, "log", "--date=format-local:%H:%M:%S", "--format=%cd",
                        FIRST_INTEGRATION + "^.." + INTEG], capture_output=True, text=True, env=env)
    return set(r.stdout.split())


def p_counts_and_times(text):
    bad = []
    quotes = _verified_quotes(text, [])
    cited = set(m.group(1) for m in RUN_ANCHOR.finditer(text))
    cited |= set(re.findall(r"<worktrees>/_runs/([\w./-]+\.(?:log|md|txt|sh|targeted))", text))
    logs = " ".join(_flat(_run_text(r) or "") for r in cited)
    for m in COUNT.finditer(text):
        if not any(m.group(0) in _flat(q) for q in quotes):
            bad.append("count %r is in no verified quote" % m.group(0))
    dates = _integration_times()
    for m in TIME.finditer(text):
        t = m.group(0)
        if any(t in q for q in quotes) or t in logs or t in dates:
            continue
        bad.append("time %s is in no verified quote, cited log or integration commit date" % t)
    return bad


def _section(text, head, nxt):
    a = text.index(head)
    b = text.index(nxt, a)
    return text[a:b]


def p_claims(text):
    bad = []
    try:
        sec = _section(text, "## 6. What set 30 closes", "## 7. The records")
    except ValueError:
        return ["section 6 missing"]
    if "%" in sec:
        bad.append("a percentage in section 6")
    for claim, state in CLAIMS.items():
        rows = [ln for ln in sec.splitlines() if ln.startswith("| %s |" % claim)]
        if len(rows) != 1:
            bad.append("%s: %d rows" % (claim, len(rows)))
            continue
        cells = [c.strip() for c in rows[0].strip("|").split("|")]
        if len(cells) < 3 or cells[1] != state:
            bad.append("%s: state %r, expected %r" % (claim, cells[1] if len(cells) > 1 else None, state))
    return bad


def _w15_rows():
    body = _show(W15, W15_FILE)
    rows, six = {}, None
    for ln in body.splitlines():
        if ln.startswith("| ") and "REVIEWED-INPUT CHANGED" in ln:
            cells = [c.strip() for c in ln.strip("|").split("|")]
            if cells[0].isdigit() and cells[6].startswith("REVIEWED-INPUT CHANGED"):
                rows[cells[1].split("`")[1]] = int(cells[0])
        if ln.startswith("- **They do not only narrow (6):**"):
            six = set(re.findall(r"`([0-9a-f]{8})`", ln))
    return rows, six


def p_unreviewed(text):
    bad = []
    rows, six = _w15_rows()
    try:
        sec = _section(text, "**The 13 REVIEWED-INPUT CHANGED commits", "Three merges bring them")
    except ValueError:
        return ["the unreviewed-change table is missing"]
    mine, marked = {}, set()
    for ln in sec.splitlines():
        if not re.match(r"\| \d+ \| `", ln):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        sha = cells[1].strip("`")
        mine[sha] = int(cells[0])
        if cells[2] == "NOT ONLY NARROWING":
            marked.add(sha)
        elif cells[2] != "narrows":
            bad.append("%s: reading %r" % (sha, cells[2]))
    if mine != rows:
        bad.append("the list differs from W15's: missing %s, extra %s" % (
            sorted(set(rows) - set(mine)), sorted(set(mine) - set(rows))))
    if marked != six:
        bad.append("NOT ONLY NARROWING marks %s differ from W15's six %s" % (sorted(marked), sorted(six or ())))
    if "UNREVIEWED CHANGES" not in text or "None of these 13 was checked by an independent checker after cx46" not in text:
        bad.append("the unreviewed-changes statement is missing")
    return bad


def p_findings(text):
    body = _run_text("int30/REVIEW-2B.md")
    if body is None:
        return ["REVIEW-2B.md is missing"]
    lines = body.splitlines()
    i = lines.index("## FINDINGS")
    want = lines[i + 1:]
    while want and not want[-1].strip():
        want.pop()
    got = [ln[2:] if ln.startswith("> ") else ln[1:] for ln in text.splitlines() if ln.startswith(">")]
    return [] if got == want else ["W16's FINDINGS are not quoted verbatim (%d lines quoted, %d filed)" % (len(got), len(want))]


# ---------------------------------------------------------------- tests

def _mutant_fails(pred, text, old, new, count=1):
    assert old in text, "the mutation's anchor %r is not in the draft" % old[:60]
    assert pred(text.replace(old, new, count)), "%s accepted a mutant (%r -> %r)" % (pred.__name__, old[:40], new[:40])


def t_the_draft_has_no_dash_and_opens_with_its_state_line():
    text = _draft()
    assert not p_hygiene(text), p_hygiene(text)
    _mutant_fails(p_hygiene, text, "## 1. The candidate", "## 1. The candidate \u2014 bound")


def t_every_placeholder_is_of_the_fixed_set_and_every_one_is_kept():
    text = _draft()
    assert not p_placeholders(text), p_placeholders(text)
    _mutant_fails(p_placeholders, text, "`__G7__`", "`G7 PASS`", -1)        # a gate line filled everywhere
    _mutant_fails(p_placeholders, text, "`__KEY__`", "`__REKEY__`")         # a placeholder outside the fixed set


def t_every_sha_named_is_in_the_integration_or_in_the_branch_named_before_it():
    _need_git()
    text = _draft()
    assert not p_shas(text), p_shas(text)
    _mutant_fails(p_shas, text, "| I1 | `3d2746c9` |", "| I1 | `57bcdbfc` |")
    _mutant_fails(p_shas, text, "| I1 | `3d2746c9` |", "| I1 | `deadbeef` |")


def t_every_quote_is_on_its_cited_line_or_in_its_log():
    _need_git()
    _need_runs()
    text = _draft()
    assert not p_anchors(text), p_anchors(text)
    _mutant_fails(p_anchors, text, "`tests: 364 passed, 1 failed, 0 skipped;", "`tests: 365 passed, 1 failed, 0 skipped;")
    _mutant_fails(p_anchors, text, "`criterion 2 FAIL with 2 defects open`", "`criterion 2 PASS with 2 defects open`")


def t_every_test_count_and_time_is_in_a_cited_source():
    _need_git()
    _need_runs()
    text = _draft()
    assert not p_counts_and_times(text), p_counts_and_times(text)
    _mutant_fails(p_counts_and_times, text, "## 5. Compute", "## 5. Compute\n\nThe passes read 2900 passed, 0 failed at 05:59:59.\n")


def t_the_three_claims_each_carry_their_own_state_and_no_percentage():
    text = _draft()
    assert not p_claims(text), p_claims(text)
    _mutant_fails(p_claims, text, "| Fabrication release | BLOCKED |", "| Fabrication release | RELEASED |")
    _mutant_fails(p_claims, text, "| Engineering-handover readiness | NOT YET ASSESSED |",
                  "| Engineering-handover readiness | 80% READY |")
    _mutant_fails(p_claims, text, "| Power-design closure | BLOCKED |", "| Power design | BLOCKED |")


def t_the_unreviewed_changes_are_w15s_reviewed_input_changed_rows():
    _need_git()
    text = _draft()
    assert not p_unreviewed(text), p_unreviewed(text)
    _mutant_fails(p_unreviewed, text, "| 31 | `2f74beb5` | narrows |", "| 31 | `9802dfde` | narrows |")
    _mutant_fails(p_unreviewed, text, "| 23 | `53a68c7c` | NOT ONLY NARROWING |", "| 23 | `53a68c7c` | narrows |")


def t_w16s_findings_are_quoted_verbatim():
    _need_runs()
    text = _draft()
    assert not p_findings(text), p_findings(text)
    _mutant_fails(p_findings, text, "Severity: **fix before the candidate commit** (deduplicate",
                  "Severity: **note for the next set** (deduplicate")


def _pytest(fn):
    def run():
        try:
            fn()
        except Skip:
            pass
    run.__name__ = fn.__name__.replace("t_", "test_", 1)
    return run


for _n, _f in list(globals().items()):
    if _n.startswith("t_") and callable(_f):
        globals()[_n.replace("t_", "test_", 1)] = _pytest(_f)
