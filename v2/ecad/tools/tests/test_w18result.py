#!/usr/bin/env python3
"""Set 30's RESULT (MESHSAT-1357, 6 October 2026): the record names only commits that exist where it says, quotes only what its
sources print, carries the values the coordinator saved, keeps the three completion claims apart in the coordinator's words and lists
exactly the classification's unreviewed changes.

The record is `v2/docs/records/int30/RESULT.md`: W18's draft 3 (`RESULT.draft3.md`, written on the integration's commit 2b
`d83d9f2d`) renamed at the adoption and filled by W26 on fnd/adopt30a from `<worktrees>/_runs/int30/ADOPTION-VALUES.md` and the
coordinator's Q-05 judgement `<worktrees>/_runs/int30/Q05-verdict.final.md`. A citation `<sha>:path:N` followed by a code span quotes line N of that file at that revision;
`<worktrees>/_runs/<path>:N` followed by a code span quotes line N of a coordinator's log outside the tree, and the growing queue file
is quoted by its dated entry (`<worktrees>/_runs/int30/QUEUE.md`, entry "...", followed by the quote, found anywhere in the file).

What fails here: an em or en dash; a draft's state line or any `__NAME__` placeholder left in the record; a filled value (the
candidate, the promotion, the mirror, the KEY, the four passes' lines, suite_gate's two lines, the l6r2 correction, W19's regression
and its merge) that is not the values file's; a commit sha in a code span that is neither in fnd/p0pwr's history at the promoted
revision nor in the history of the `fnd/<branch>` written just before it; a quote not on its cited line
at its revision or not in its log; a test count ("N passed, M failed") or a time HH:MM:SS that is not in a verified quote, a cited log
or a commit date of the integration; a completion claim missing, doubled, blended with a percentage or carrying a state word other
than the coordinator's Q-05 word, or not citing the assessment; the DESK gate's NOT PASSED missing; an unreviewed-change list that
differs from W15's REVIEWED-INPUT CHANGED rows, a NOT ONLY NARROWING mark that differs from W15's list of six, or a table of the
commits after 6bc4424e whose first classes differ from CLASSIFICATION.md's rows 39 to 45; W16's FINDINGS not verbatim. Each
predicate is also run on a mutant of the record that it must refuse.

Restated at the adoption (W26): the draft-stage predicates "the first line is the DONE / NOT DONE / NEXT line", "every placeholder of
the fixed set is kept" and "handover readiness NOT YET ASSESSED" became "no draft line and no placeholder remains", "each filled value
is the values file's" and "each claim carries the coordinator's word"; the integration's tip for the sha and time checks moved from 2b
to the promoted revision; no figure, sha or citation check was dropped.

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
DRAFT = "v2/docs/records/int30/RESULT.md"
VALUES_REL = "int30/ADOPTION-VALUES.md"
Q05_REL = "int30/Q05-verdict.final.md"
CLASS_FILE = "v2/docs/records/int30/CLASSIFICATION.md"
ASSESSMENT = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
INTEG = "dd1aed00d0a0a521063b5792550bc510c4707c59"        # the promoted revision (INTEGRATED = CANDIDATE = PROMOTED)
# Restated by W33 (6 October 2026; basis: W32's read of the adoption, REPORT-AS-RECEIVED.md, class 1, the insertion times, and the
# coordinator's ruling 1 in W33's brief): the record now names the adoption commit, where the coordinator inserted the Q-05 judgement
# whole (main fast-forwarded to it after the promotion), so p_shas accepts exactly this one commit when it is in this tree's history;
# every other sha keeps the rule (the integration's history at INTEG, or the fnd/ branch named before it).
ADOPTION = "836f711b406be48d9eb58c9cf6f7491fbcf7c5ec"
B2 = "d83d9f2d720878ca5267dbf59bdc571c6890fd92"           # commit 2b, the integration's committed tip when draft 3 was written
W15 = "57bcdbfce095c461b4c3b6804ea8cc3508762577"          # W15's classification
W15_FILE = "v2/docs/records/int30/CLASSIFICATION.draft.md"
FIRST_INTEGRATION = "3d2746c9bdd9a17ad81e19889892e5691973eb63"
FILLED = ("__CANDIDATE__", "__PROMOTED__", "__MIRROR__", "__KEY__", "__GATE_BOX_PY312__", "__GATE_BOX_PY311__",
          "__GATE_RUNNER__", "__G7__", "__L6R2_FIX__", "__W19__")     # draft 3's placeholders, all filled at the adoption
CLAIMS = {"Engineering-handover readiness": "READY AS A DESK PACKAGE OF OPEN ITEMS", "Power-design closure": "BLOCKED",
          "Fabrication release": "BLOCKED"}
Q05_HEADS = {"Engineering-handover readiness": "## Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
             "Power-design closure": "## Power-design closure: BLOCKED.", "Fabrication release": "Fabrication release: BLOCKED.",
             "DESK gate": "## Layer 4's DESK gate: NOT PASSED"}

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
    for sha in (INTEG, B2, W15):
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
    if not text.startswith("# Set 30: the result of the integration (MESHSAT-1357)\n"):
        bad.append("the record does not open with its title")
    for w in ("**DONE:**", "**NOT DONE:**", "**NEXT:**", "**Status: DRAFT"):
        if w in text:
            bad.append("a draft's line is left in the record: %s" % w)
    return bad


def p_placeholders(text):
    found = sorted(set(re.findall(r"__[A-Z0-9_]+__", text)))
    return ["a placeholder is left in the record: %s" % p for p in found]


def _values():
    """The coordinator's saved values, each read from ADOPTION-VALUES.md by its pattern (Skip when the file is not on this host)."""
    body = _run_text(VALUES_REL)
    if body is None:
        raise Skip("the coordinator's values file is not on this host")

    def one(pat):
        m = re.search(pat, body)
        assert m, "the values file carries no %r" % pat
        return m.group(1)
    return {
        "CANDIDATE": one(r"INTEGRATED = CANDIDATE = PROMOTED = MIRROR \(GitHub main\): ([0-9a-f]{40})"),
        "KEY": one(r"l4e7 KEY: (MATCH [0-9a-f]{16})"),
        "GATE_A": one(r'box pass A \([^)]*\): "([^"]+)"'), "GATE_B": one(r'box pass B \([^)]*\): "([^"]+)"'),
        "GATE_REC": one(r'the records box \([^)]*\): "([^"]+)"'), "GATE_RUNNER": one(r'the runner \([^)]*\): "([^"]+)"'),
        "G7": one(r"modules \d+ of \d+ ran / (suite_gate: PASS)"), "G7_TOTALS": one(r"\(_runs/int30s1/suite_gate.txt\): (suite_gate: [^/]+ran)"),
        "GUARD": one(r'candidate_guard, every host: "([^"]+)"'),
        "L6R2": one(r"the l6r2 correction ([0-9a-f]{8})"), "W19": one(r"W19's regression ([0-9a-f]{8}) merged at"),
        "W19M": one(r"merged at ([0-9a-f]{8})"), "REKEY": one(r"the re-keyed l4e7 cache ([0-9a-f]{40})"),
    }


def _row(text, section_head, label):
    sec = text[text.index(section_head):]
    rows = [ln for ln in sec.splitlines() if ln.startswith("| %s" % label)]
    return rows[0] if len(rows) == 1 else None


def p_filled(text, vals):
    """Each filled value stands where draft 3 kept its placeholder and is the values file's."""
    bad = []
    s1, s4 = "## 1. The candidate", "## 4. The freeze and the gates"
    want = [
        (s1, "INTEGRATED = CANDIDATE:", ["`%s`" % vals["CANDIDATE"]]),
        (s1, "PROMOTED:", ["`%s` (mirror `%s`)" % (vals["CANDIDATE"], vals["CANDIDATE"])]),
        (s1, "I12 |", ["`%s`" % vals["L6R2"]]), (s1, "I13 |", ["`%s`" % vals["W19M"], "`%s`" % vals["W19"]]),
        (s1, "I14 |", ["`%s`" % vals["REKEY"][:8]]), (s1, "I16 |", ["`%s`" % vals["CANDIDATE"][:8]]),
        (s4, "W16's finding 1:", ["`%s`" % vals["L6R2"]]), (s4, "W16's finding 3:", ["`%s`, merged at `%s`" % (vals["W19"], vals["W19M"])]),
        (s4, "The re-key, its KEY", ["`l4e7 KEY: %s" % vals["KEY"]]), (s4, "The candidate commit", ["`%s`" % vals["CANDIDATE"]]),
        (s4, "candidate_guard check, every host", ["`%s`" % vals["GUARD"]]),
        (s4, "Box pass A, Python 3.12", ["`%s`" % vals["GATE_A"]]), (s4, "Box pass B, Python 3.11", ["`%s`" % vals["GATE_B"]]),
        (s4, "Records box pass", ["`%s`" % vals["GATE_REC"]]), (s4, "Runner pass", ["`%s`" % vals["GATE_RUNNER"]]),
        (s4, "suite_gate with G7", ["`%s`" % vals["G7"], "`%s`" % vals["G7_TOTALS"].strip()]),
        (s4, "Promotion:", ["`%s`" % vals["CANDIDATE"]]),
    ]
    for head, label, needles in want:
        try:
            row = _row(text, head, label)
        except ValueError:
            bad.append("section %r is missing" % head)
            continue
        if row is None:
            bad.append("no single row %r in %r" % (label, head))
            continue
        for n in needles:
            if n not in row:
                bad.append("row %r does not carry the values file's %r" % (label, n[:60]))
    if text.count("`%s`" % vals["GUARD"]) < 4:
        bad.append("the guard's line is not quoted for the four hosts")
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
        if ADOPTION.startswith(sha) and _ancestor(sha, "HEAD"):   # W33: the adoption commit, by its full sha's prefix only
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
            k = int(n)
            # A coordinator's log that _bin/vast_watchdog.py caps and rotates (LOG_CAP; <log>.1 to <log>.3 kept, owner's rule of 1 Oct
            # 2026) keeps its lines in the rotated file: the quote must stand on line N of the log or of one file of its rotation chain
            # (the coordinator, Amendment 8 T1a, 7 Oct 2026: a false positive fixed at its source; never a quote found elsewhere).
            found = False
            for body_k in [body] + [b for b in (_run_text("%s.%d" % (rel, i)) for i in (1, 2, 3)) if b is not None]:
                lines = body_k.splitlines()
                if 1 <= k <= len(lines) and _flat(quote) in _flat(lines[k - 1]):
                    found = True
                    break
            if not found:
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


def p_claims(text, q05=None):
    """The three claims apart, each with the coordinator's word and citing the assessment; the DESK gate NOT PASSED, apart from them;
    with the Q-05 file at hand, each word is also on that file's heading."""
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
        elif ASSESSMENT not in cells[2]:
            bad.append("%s: the basis does not cite %s" % (claim, ASSESSMENT))
        if q05 is not None and Q05_HEADS[claim] not in q05:
            bad.append("%s: the Q-05 file carries no %r" % (claim, Q05_HEADS[claim]))
        if q05 is not None and state not in Q05_HEADS[claim]:
            bad.append("%s: %r is not the Q-05 heading's word" % (claim, state))
    gate = [ln for ln in sec.splitlines() if ln.startswith("**Layer 4's DESK gate, on the promoted revision: NOT PASSED.**")]
    if len(gate) != 1:
        bad.append("the DESK gate's NOT PASSED line is missing or doubled")
    if "`<worktrees>/_runs/int30/Q05-verdict.final.md:5` `## Layer 4's DESK gate: NOT PASSED`" not in sec:
        bad.append("the DESK gate's word is not quoted from the Q-05 file")
    if q05 is not None and Q05_HEADS["DESK gate"] not in q05:
        bad.append("the Q-05 file carries no DESK gate heading")
    path = os.path.join(REPO, ASSESSMENT)
    if os.path.isfile(path):          # once the other adoption author's file is in the tree, it carries the same words
        body = open(path, encoding="utf-8").read()
        for w in ("NOT PASSED", "READY AS A DESK PACKAGE OF OPEN ITEMS", "BLOCKED"):
            if w not in body:
                bad.append("%s does not carry %r" % (ASSESSMENT, w))
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
        # restated by W33 (6 October 2026): the table now closes at "Four merges bring them" (basis: W32's count finding,
        # `git log 2ccf0f20^1..2ccf0f20^2` prints 9802dfde, 2f74beb5 and 3088ee79, and CLASSIFICATION.md's rows 30 and 31 are
        # REVIEWED-INPUT CHANGED, so merge 2ccf0f20 is a fourth that brings them); the table and its rows are unchanged
        sec = _section(text, "**The 13 REVIEWED-INPUT CHANGED commits", "Four merges bring them")
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
    bad += _after_6bc4424e(text)
    return bad


def _class_rows_after():
    """CLASSIFICATION.md's rows 39 to 45 in this tree: {short sha: (row, first class, NOT ONLY NARROWING listed)}"""
    with open(os.path.join(REPO, CLASS_FILE), encoding="utf-8") as f:
        body = f.read()
    rows = {}
    for ln in body.splitlines():
        m = re.match(r"\| (\d+) \| `([0-9a-f]{8})` / `[0-9a-f]{40}` \|", ln)
        if m and int(m.group(1)) >= 39:
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip())[1:-1]]
            rows[m.group(2)] = (int(m.group(1)), cells[6])
    six = re.search(r"\*\*They do not only narrow \([^)]*\):\*\* ([^(]+)\(", body)
    return rows, set(re.findall(r"`([0-9a-f]{8})`", six.group(1))) if six else set()


def _after_6bc4424e(text):
    bad = []
    try:
        sec = _section(text, "**The seven commits after `6bc4424e`**", "**So the promoted revision carries")
    except ValueError:
        return ["the table of the commits after 6bc4424e is missing"]
    want, nonnarrow = _class_rows_after()
    got = {}
    for ln in sec.splitlines():
        m = re.match(r"\| (\d+) \| `([0-9a-f]{8})` \| ([^|]+) \|", ln)
        if m:
            got[m.group(2)] = (int(m.group(1)), m.group(3).strip())
    if sorted(got) != sorted(want):
        bad.append("the commits after 6bc4424e %s are not CLASSIFICATION.md's rows 39 to 45 %s" % (sorted(got), sorted(want)))
    for sha, (n, cls) in got.items():
        if sha in want and (want[sha][0] != n or want[sha][1] != cls):
            bad.append("%s: row %d %r, CLASSIFICATION.md row %d %r" % (sha, n, cls[:40], want[sha][0], want[sha][1][:40]))
    ric = [s for s, (n, c) in want.items() if c.startswith("REVIEWED-INPUT CHANGED")]
    total = 13 + len(ric)
    if "**So the promoted revision carries %d UNREVIEWED CHANGES, not 13:**" % total not in text:
        bad.append("the count of unreviewed changes on the promoted revision is not 13 + %d" % len(ric))
    if not set(ric) <= nonnarrow:
        bad.append("a REVIEWED-INPUT CHANGED row after 6bc4424e is not in CLASSIFICATION.md's NOT ONLY NARROWING list")
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


def t_the_record_has_no_dash_and_no_draft_line():
    text = _draft()
    assert not p_hygiene(text), p_hygiene(text)
    _mutant_fails(p_hygiene, text, "## 1. The candidate", "## 1. The candidate \u2014 bound")
    assert p_hygiene("**DONE:** x; **NOT DONE:** y; **NEXT:** z\n\n" + text), "a draft state line passed"


def t_no_placeholder_is_left_and_every_filled_value_is_the_values_files():
    text = _draft()
    assert not p_placeholders(text), p_placeholders(text)
    for ph in FILLED:
        assert p_placeholders(text + "\n" + ph + "\n"), "a placeholder %s left in passed" % ph
    _need_runs()
    vals = _values()
    assert not p_filled(text, vals), p_filled(text, vals)
    _mutant_fails(lambda t: p_filled(t, vals), text, "`tests: 2770 passed, 0 failed, 2 skipped`", "`tests: 2771 passed, 0 failed, 2 skipped`")
    _mutant_fails(lambda t: p_filled(t, vals), text, "`suite_gate: PASS`", "`suite_gate: FAIL`")
    _mutant_fails(lambda t: p_filled(t, vals), text, "| INTEGRATED = CANDIDATE: the candidate commit (the re-keyed record l4e7 cache, its dependents and the pack rule installed) | `%s`" % vals["CANDIDATE"],
                  "| INTEGRATED = CANDIDATE: the candidate commit (the re-keyed record l4e7 cache, its dependents and the pack rule installed) | `%s`" % vals["REKEY"])
    _mutant_fails(lambda t: p_filled(t, vals), text, "`l4e7 KEY: %s" % vals["KEY"], "`l4e7 KEY: MISMATCH", -1)


def t_every_sha_named_is_in_the_integration_or_in_the_branch_named_before_it():
    _need_git()
    text = _draft()
    assert not p_shas(text), p_shas(text)
    _mutant_fails(p_shas, text, "| I1 | `3d2746c9` |", "| I1 | `57bcdbfc` |")
    _mutant_fails(p_shas, text, "| I1 | `3d2746c9` |", "| I1 | `e91a77e1` |")      # the adoption's own merge: not the integration's
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


def t_the_three_claims_carry_the_coordinators_words_apart_and_the_desk_gate_is_not_passed():
    text = _draft()
    q05 = _run_text(Q05_REL)
    assert not p_claims(text, q05), p_claims(text, q05)
    _mutant_fails(p_claims, text, "| Fabrication release | BLOCKED |", "| Fabrication release | RELEASED |")
    _mutant_fails(p_claims, text, "| Engineering-handover readiness | READY AS A DESK PACKAGE OF OPEN ITEMS |",
                  "| Engineering-handover readiness | 80% READY |")
    _mutant_fails(p_claims, text, "| Engineering-handover readiness | READY AS A DESK PACKAGE OF OPEN ITEMS |",
                  "| Engineering-handover readiness | READY |")
    _mutant_fails(p_claims, text, "| Power-design closure | BLOCKED |", "| Power design | BLOCKED |")
    _mutant_fails(p_claims, text, "**Layer 4's DESK gate, on the promoted revision: NOT PASSED.**",
                  "**Layer 4's DESK gate, on the promoted revision: PASSED.**")
    _mutant_fails(p_claims, text, "| Power-design closure | BLOCKED | the coordinator's judgement, "
                  "`<worktrees>/_runs/int30/Q05-verdict.final.md:13` `## Power-design closure: BLOCKED. Fabrication release: BLOCKED.`, "
                  "recorded in `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md`; ", "| Power-design closure | BLOCKED | ")
    if q05 is not None:
        assert p_claims(text, q05.replace("READY AS A DESK PACKAGE OF OPEN ITEMS", "READY")), "a word off the Q-05 heading passed"


def t_the_unreviewed_changes_are_w15s_reviewed_input_changed_rows():
    _need_git()
    text = _draft()
    assert not p_unreviewed(text), p_unreviewed(text)
    _mutant_fails(p_unreviewed, text, "| 31 | `2f74beb5` | narrows |", "| 31 | `9802dfde` | narrows |")
    _mutant_fails(p_unreviewed, text, "| 23 | `53a68c7c` | NOT ONLY NARROWING |", "| 23 | `53a68c7c` | narrows |")
    _mutant_fails(p_unreviewed, text, "| 39 | `d83d9f2d` | REVIEWED-INPUT CHANGED +", "| 39 | `d83d9f2d` | DIGEST RE-PIN / REGENERATED OUTPUT +")
    _mutant_fails(p_unreviewed, text, "**So the promoted revision carries 14 UNREVIEWED CHANGES, not 13:**",
                  "**So the promoted revision carries 13 UNREVIEWED CHANGES, not 13:**")


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
