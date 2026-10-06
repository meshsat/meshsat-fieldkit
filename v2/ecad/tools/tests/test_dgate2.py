"""Draft 2 of Layer 4's DESK-gate assessment (MESHSAT-1357, 6 October 2026), held as predicates on its text and on the files it
cites: v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md (draft 2, L4-DESK-GATE-ASSESSMENT.draft2.md, renamed at its adoption).

Restated by W27 at the adoption on the promoted revision PROM = dd1aed00 (6 October 2026; basis: the coordinator's values of
10:40:38 CEST, INTEGRATED = CANDIDATE = PROMOTED = dd1aed00d0a0a521063b5792550bc510c4707c59): the header predicate reads the adopted
status and no placeholder sha left; the verdict predicate holds the judgement HELD (the placeholder in its line, the two stopped
sentences named against the ledger at PROM) or, once the coordinator inserts it, its five headings and no placeholder; the
acceptance predicate takes the coordinator's verdict words NOT PASSED as it takes the filed NOT CLOSED, and still refuses a bare
PASSED; and the facts the adoption re-read at PROM are held by their own predicates beside the facts W12 read at CAND, which stay
as W12 read them (CAND keeps its revision: W12's citations are read there).

Draft 2 is Slot L's draft re-read on the committed integration commit 6bc4424e (CAND below); it is record text for the
coordinator, not the assessment. It cites files by alias, `[ALIAS:N]` or `[ALIAS:N-M]`, through its own alias table: revision `cand`
names a file at CAND, revision `base` a file at set 30's integration 2a (BASE, dated history), and an eight-hex revision a file on
another branch, cited as text only. This module reads every cited file AT ITS REVISION with git show, never the working tree. A
commit absent from this clone's object store is checked for form only (a clone holding only the candidate's history has none of the
coordination branches; stated here so that the reduced reading is never mistaken for the full one).

The predicates: the header says DRAFT 2 and not the assessment and names the candidate in full; every alias row names a file that
exists at its revision; L4-E9's page at CAND is set 31's page byte for byte; every citation uses an alias of the table and lies
inside its file; every quotation of twelve characters or more is found verbatim (emphasis marks and whitespace aside) within two lines
of the range of the first citation after it; each of the four parts states its counts and carries exactly that many items; the K
table has 28 rows of seven cells, its Standing column reads yes or no and never reads closed, a "no" names the candidate's own
correction with a citation at CAND and never rests on a next-set branch alone, a "yes" is either restated on a next-set branch (cited
there) or reads none, and the stated counts (standing, restated, unrestated, YES) agree with the table and with A1.4; Slot G's
sixteen items each have one row; the twenty remaining-engineering items and the annex's four each have one acceptance row; the
verdict placeholder appears once and the completion claims read as briefed; the five fixed words of the design gate appear in
section 7 only; nothing outside a quotation reads as an acceptance; every sha named in backticks or in the alias table and every
`fnd/` branch named exists in git; the pre-freeze branches are ancestors of CAND and the next-set commits are not; and the facts the
draft read with git at CAND hold there (the eighteen stability digests equal their files, L4-E9's output pins four cascade outputs
at other bytes, record l4e7's cache was last committed at set 29's freeze and its output before it, L4-E11's output at the bytes
record l4e7 read, seventeen fetch_held_back.py scripts, E11-37 named once in the annex and placed in the ledger as HO-L, twelve RE
and eight HO remaining-engineering rows in the ledger's summary). No em or en dash. These are software predicates on record text:
they establish no electrical or thermal property and close nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_dgate2.`) and under pytest (each t_ function has a test_
alias). Without git, or without CAND in the object store, the rules that read it skip with their reason. When 2b is committed, the
coordinator moves CAND to it and re-reads what fails (the draft's section 9)."""
import hashlib
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
DRAFT = os.path.join(ROOT, "v2", "docs", "records", "l4close", "L4-DESK-GATE-ASSESSMENT.md")  # draft 2 renamed at the adoption
CAND = "6bc4424ec64592e1a501af5db2246f3391c525a0"  # where W12 read draft 2 (the aliases `cand`)
PROM = "dd1aed00d0a0a521063b5792550bc510c4707c59"  # the promoted revision (the values file), the adoption's reading
BASE = "bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45"
SLOT_L = "249e9e4785a170238c69316742a422250908cd1f"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

ALIAS_ROW = re.compile(r"^\| ([A-Z][A-Z0-9]*) \| (cand|base|[0-9a-f]{8}) \| `(v2/[^`]+)`", re.M)
CITE = re.compile(r"\[([A-Z][A-Z0-9]*)(?::(\d+)(?:-(\d+))?)?\]")
DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
PLACEHOLDER = "[COORDINATOR: DESK-gate verdict]"
CLAIMS = ("- documents and editable artifacts: on main as a DESK candidate",
          "- design reviewed and accepted: NO",
          "- implemented: NONE",
          "- physical qualification: NONE",
          "- fabrication release: BLOCKED",
          "- power-design closure: BLOCKED")
FIXED = ("C1 CONDITIONAL", "C2 FAIL", "C3 PASS", "C4 PASS", "C5 CONDITIONAL")  # the coordinator's words, as the INBOX gives them
# the next-set branches' commits (NOT in the candidate) and the pre-freeze branches' tips (in it), as the coordinator's note names them
NEXT_SET = ("686de0a2", "786aed2f", "cd19df59", "3e566c55", "1ab30f35", "02b0d30d", "85b6f258")
PRE_FREEZE = ("6ab17e21", "2080a0ff", "9802dfde", "99bbc0c6", "17ce29d5")
STAB = "v2/docs/records/l9t5/stability/DIGESTS-cr3.txt"
L4O = "v2/docs/records/l4e9/l4e9_power_path.out"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
CACHE = (("v2/docs/records/l4e7/l4e7_stage_settings.results.json", "69921ce8"),
         ("v2/docs/records/l4e7/l4e7_stage_settings.out", "914a2f5a"))
REM = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
DIGEST16 = ("40ca9c0311440ca0",)  # a sha256/16 the draft names, not a commit
_C = {}


def _draft():
    if "d" not in _C:
        _C["d"] = open(need(DRAFT, "the DESK-gate assessment draft 2"), encoding="utf-8").read()
    return _C["d"]


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git on this host (%s)" % e)
    if r.returncode != 0:
        raise Skip("git %s: %s" % (a[0], r.stderr.decode(errors="replace")[:100].strip()))
    return r.stdout.decode("utf-8")


def _rc(*a):
    try:
        return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True).returncode
    except OSError:
        return -1


def _has(rev):
    k = ("has", rev)
    if k not in _C:
        _C[k] = _rc("cat-file", "-e", rev + "^{commit}") == 0
    return _C[k]


def _cand_ok():
    if not _has(CAND):
        raise Skip("the candidate %s is not in this clone's object store" % CAND[:8])


def _show(rev, path):
    """The text of path at rev, or None when rev has no such file."""
    k = ("s", rev, path)
    if k not in _C:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)], capture_output=True)
        _C[k] = r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None
    return _C[k]


def _showb(rev, path):
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _aliases():
    """alias -> (revision, path)."""
    out = {}
    for a, rev, path in ALIAS_ROW.findall(_draft()):
        out[a] = ({"cand": CAND, "base": BASE}.get(rev, rev), path)
    return out


def _norm(t):
    return " ".join(t.replace("*", "").replace("`", "").split())


def _quotes():
    return [(m.group(1), m.end()) for m in re.finditer(r'"([^"]*)"', _draft())]


def _unquoted():
    return re.sub(r'"[^"]*"', '""', _draft())


def _section(n):
    t = _draft()
    i = t.find("\n## %d. " % n)
    assert i >= 0, "no section %d" % n
    j = t.find("\n## ", i + 4)
    return t[i:] if j < 0 else t[i:j]


def _before_section(n):
    t = _draft()
    return t[:t.find("\n## %d. " % n)]


def t_the_header_says_what_it_is():
    # restated at the adoption: the head is the text before "Two gates, never one" (the adopted status paragraph made it longer
    # than the draft's 2400 characters); the status reads ADOPTED on PROM with the judgement HELD or inserted; the placeholders
    # __INTEGRATED__ and __PROMOTED__ are bound (to PROM) and appear nowhere; draft 2's own paragraph is kept as filed.
    d = _draft()
    head = " ".join(d[:d.find("**Two gates, never one.**")].split())
    assert head.startswith("# Layer 4's DESK gate (the owner's part 19): the assessment on the promoted revision `dd1aed00`"), "the title"
    assert ("**Status: ADOPTED on the promoted revision `%s`; the coordinator's judgement HELD (section 6).**" % PROM) in head \
        or ("**Status: ADOPTED on the promoted revision `%s`.**" % PROM) in head, "the adopted status"
    assert "**Draft 2 as filed.** It is Slot L's draft" in head, "draft 2's own paragraph"
    assert CAND in head and SLOT_L in head and PROM in head, "the candidate, Slot L's tip or the promoted revision is not named in full"
    assert "Prototype framing" in head and "nothing in the kit has been built, bought, powered or measured" in head
    assert "__INTEGRATED__" not in d and "__PROMOTED__" not in d, "a placeholder sha left"


def t_every_alias_row_names_an_existing_file():
    al = _aliases()
    assert len(al) >= 60, "the alias table is not read (%d rows)" % len(al)
    _cand_ok()
    missing = []
    for a, (rev, path) in sorted(al.items()):
        if not _has(rev):
            continue  # another branch's commit absent from this clone: form only (see the module docstring)
        if _show(rev, path) is None:
            missing.append("%s %s:%s" % (a, rev[:8], path))
    assert not missing, "alias rows naming no file: %s" % missing


def t_the_page_at_the_candidate_is_set_31s():
    _cand_ok()
    if not _has("17ce29d5"):
        raise Skip("set 31's tip 17ce29d5 is not in this clone")
    assert _showb(CAND, PAGE) == _showb("17ce29d5", PAGE), "L4-E9's page at the candidate differs from set 31's"


def t_every_citation_uses_an_alias_and_lies_inside_its_file():
    al = _aliases()
    _cand_ok()
    bad = []
    n = 0
    for m in CITE.finditer(_draft()):
        a, lo, hi = m.group(1), m.group(2), m.group(3)
        if a == "ALIAS":
            continue  # the citation form's own placeholder
        if a not in al:
            bad.append("unknown alias %s" % m.group(0))
            continue
        n += 1
        rev, path = al[a]
        if not _has(rev):
            continue
        t = _show(rev, path)
        if t is None:
            bad.append("%s: no file" % m.group(0))
            continue
        if lo:
            last = int(hi or lo)
            if int(lo) < 1 or last < int(lo) or last > len(t.splitlines()):
                bad.append("%s: outside %d lines" % (m.group(0), len(t.splitlines())))
    assert n >= 350, "too few citations read (%d)" % n
    assert not bad, "bad citations: %s" % bad[:12]


def t_every_quotation_is_found_where_its_citation_points():
    al = _aliases()
    _cand_ok()
    d = _draft()
    bad = []
    checked = 0
    for q, end in _quotes():
        nq = _norm(q)
        if len(nq) < 12:
            continue
        assert "\n|" not in q, "a quotation runs across a table row: %r" % q[:60]
        m = CITE.search(d, end)
        if not m or m.start() - end > 400:
            bad.append("no citation after %r" % nq[:50])
            continue
        if m.group(1) not in al:
            bad.append("unknown alias after %r" % nq[:50])
            continue
        rev, path = al[m.group(1)]
        if not _has(rev):
            continue
        t = _show(rev, path)
        if t is None:
            bad.append("no file for %r" % nq[:50])
            continue
        lines = t.splitlines()
        if m.group(2):
            lo, hi = int(m.group(2)), int(m.group(3) or m.group(2))
            seg = "\n".join(lines[max(0, lo - 3):hi + 2])
        else:
            seg = t
        checked += 1
        if nq not in _norm(seg):
            bad.append("%r not at %s" % (nq[:60], m.group(0)))
    assert checked >= 80, "too few quotations checked (%d)" % checked
    assert not bad, "quotations not found: %s" % bad[:8]


def t_each_part_carries_its_stated_counts():
    for k in (1, 2, 3, 4):
        s = _section(k)
        mf = re.search(r"\*\*For acceptance at the desk gate \((\d+)\)\.\*\*", s)
        ma = re.search(r"\*\*Against \((\d+)\)\.\*\*", s)
        assert mf and ma, "part %d: no stated counts" % k
        f = re.findall(r"^- F%d\.(\d+) " % k, s, re.M)
        a = re.findall(r"^- A%d\.(\d+) " % k, s, re.M)
        assert [int(x) for x in f] == list(range(1, int(mf.group(1)) + 1)), "part %d: F items %s" % (k, f)
        assert [int(x) for x in a] == list(range(1, int(ma.group(1)) + 1)), "part %d: A items %s" % (k, a)


def _k_rows():
    """(id, [cells]) for each K row: Sources, contradiction, Standing, Restated, Class, Stumble."""
    out = []
    for kid, rest in re.findall(r"^\| (K-\d\d) \|(.*)\|$", _section(5), re.M):
        out.append((kid, [c.strip() for c in rest.split(" | ")]))
    return out


def _cite_revs(text):
    al = _aliases()
    return [al[m.group(1)][0] for m in CITE.finditer(text) if m.group(1) in al]


def t_the_k_table_has_its_columns():
    rows = _k_rows()
    assert [r[0] for r in rows] == ["K-%02d" % i for i in range(1, 29)], "K ids: %s" % [r[0] for r in rows]
    for kid, c in rows:
        assert len(c) == 6, "%s: %d cells after the id" % (kid, len(c))
        assert re.match(r"^(yes|no)\b", c[2]), "%s: Standing reads %r" % (kid, c[2][:30])
        assert "closed" not in c[2].lower(), "%s: Standing reads closed" % kid
        assert c[5].startswith("YES") or c[5].startswith("NO"), "%s: Stumble" % kid


def t_standing_never_reads_closed_on_a_next_set_restatement_alone():
    rows = _k_rows()
    for kid, c in rows:
        standing, restated = c[2], c[3]
        revs = _cite_revs(restated)
        if standing.startswith("no"):
            assert restated.startswith("in the candidate:"), "%s: a no without the candidate's own correction" % kid
            assert CAND in revs, "%s: a no with no citation at the candidate" % kid
            assert not restated.startswith("next set"), kid
        else:
            assert restated.startswith("next set:") or restated.startswith("none"), "%s: Restated reads %r" % (kid, restated[:30])
            if restated.startswith("next set:"):
                assert any(r in NEXT_SET for r in revs), "%s: a next-set restatement cited on no next-set commit" % kid
                assert CAND not in revs or "in the candidate" not in restated, kid
        if kid in ("K-03", "K-15", "K-16", "K-17", "K-18", "K-22"):
            assert standing.startswith("yes") and restated.startswith("none"), "%s: an item left to another file" % kid


def t_the_stated_counts_agree_with_the_k_table():
    rows = _k_rows()
    s5 = " ".join(_section(5).split())
    stand = [r for r in rows if r[1][2].startswith("yes")]
    rest = [r for r in stand if r[1][3].startswith("next set:")]
    yes = [r for r in rows if r[1][5].startswith("YES")]
    m = re.search(r"The list has (\d+) entries", s5)
    assert m and int(m.group(1)) == len(rows) == 28, "the stated count"
    m = re.search(r"(\d+) entries stand on the candidate and (\d+) do not; of the (\d+), (\d+) have a restatement on a next-set "
                  r"branch and (\d+) have none", s5)
    assert m, "no stated standing counts"
    got = tuple(int(x) for x in m.groups())
    want = (len(stand), len(rows) - len(stand), len(stand), len(rest), len(stand) - len(rest))
    assert got == want, "stated %s, table %s" % (got, want)
    m = re.search(r"(\d+) read YES on the candidate", s5)
    assert m and int(m.group(1)) == len(yes), "the YES count"
    for n in re.findall(r"\((\d+) stand at YES", _draft()):
        assert int(n) == len(yes), "section 6 states %s at YES, table %d" % (n, len(yes))
    words = {"Nineteen": 19, "twenty-eight": 28, "seventeen": 17, "thirteen": 13, "nineteen": 19}
    a14 = re.search(r"- A1\.4 (\w+) of the ([\w-]+) contradictions of section 5 still stand on the candidate, (\w+) of them read YES "
                    r"in the column\s+Stumble; (\w+) of the (\w+) have a restatement", _draft())
    assert a14, "A1.4's counts"
    assert [words.get(w) for w in a14.groups()] == [len(stand), len(rows), len(yes), len(rest), len(stand)], "A1.4's words disagree"


def t_slot_g_items_each_have_one_row():
    s = _section(5)
    for i in range(1, 17):
        assert len(re.findall(r"^\| PC-%02d " % i, s, re.M)) == 1, "PC-%02d's row" % i


HANDED = ["RE-%d" % i for i in (1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18)] + ["HO-%s" % c for c in "ABCDEFGL"] + [
    "U-01", "U-02", "U-04", "E11-29"]


def t_every_handed_over_item_has_one_acceptance_row():
    s = _section(4)
    for it in HANDED:
        assert len(re.findall(r"^\| %s \| (remaining engineering|external architecture fact|qualification) \|" % re.escape(it), s, re.M)) == 1, it
    assert len(re.findall(r"^\| (?:RE|HO|U|E11)-[0-9A-Z]+ \| ", s, re.M)) == len(HANDED), "rows beyond the ledger's and the annex's items"
    assert "ledger's twenty remaining-engineering items" in " ".join(s.split())


JUDGEMENT_HEADS = ("### Layer 4's DESK gate: NOT PASSED", "### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
                   "### Power-design closure: BLOCKED. Fabrication release: BLOCKED.",
                   "### Y6, item by item: is a desk-solvable defect parked in the handover?",
                   "### The consequence the owner decides (reported, not asked)")


def t_the_placeholder_and_the_completion_claims():
    # restated at the adoption: section 6 is the coordinator's judgement on PROM. HELD (W27 stopped on two sentences): the
    # placeholder stands in the verdict line on `dd1aed00` and in the header as code, and the note names the two sentences with
    # the ledger's lines at PROM. INSERTED (the coordinator's step): no placeholder, the judgement's five headings, no HELD note.
    d = _draft()
    s6 = _section(6)
    assert s6.startswith("\n## 6. The coordinator's judgement on the promoted revision\n"), "section 6's heading"
    if "**HELD at the adoption" in s6:
        assert d.count(PLACEHOLDER) == 2, "the placeholder: once in the header (as code) and once as the verdict"
        assert d.count("`%s`" % PLACEHOLDER) == 1, "the header names the placeholder as code once"
        assert ("assessed on `dd1aed00`: %s" % PLACEHOLDER) in s6, "the verdict line does not carry the placeholder"
        flat = " ".join(s6.split())
        for c in ("[REMP:100]", "[REMP:649]", "[REMP:669]", "[REMP:692]", "[REMP:693-695]"):
            assert c in flat, "the held note does not cite %s" % c
        assert all(h not in s6 for h in JUDGEMENT_HEADS), "a judgement heading in the held state"
    else:
        assert PLACEHOLDER not in d, "the judgement inserted beside the placeholder"
        assert all(h in s6 for h in JUDGEMENT_HEADS), "the judgement's five headings"
    assert "### The draft's proposal, re-read" in s6, "W12's proposal kept below the judgement"
    for c in CLAIMS:
        assert len(re.findall("^" + re.escape(c), s6, re.M)) == 1, "the claim %r" % c
    assert "<INTEGRATED-SHA>`" not in d.replace("`<INTEGRATED-SHA>` with", ""), "Slot L's placeholder left in use"


def t_the_fixed_words_are_in_section_7_only():
    s7 = _section(7)
    for w in FIXED:
        assert len(re.findall(r"^- %s: " % re.escape(w), s7, re.M)) == 1, "section 7 lacks %r as an item" % w
    rest = _before_section(7) + _draft()[_draft().find("\n## 8. "):]
    for w in FIXED:
        assert w not in rest, "%r outside section 7" % w
    flat = " ".join(rest.split())
    assert not re.search(r"criterion \d (PASS|FAIL|CONDITIONAL)", flat), "a criterion verdict outside section 7"
    assert "[DG1:414]" in s7, "C2's reason is not cited to Slot L's draft"


def t_nothing_outside_a_quotation_reads_as_an_acceptance():
    # restated at the adoption: the coordinator's verdict words NOT PASSED (its judgement of 10:45 CEST, recorded in section 6)
    # are taken out first, as the filed NOT CLOSED is below; a bare PASSED still fails.
    u = re.sub(r"\bNOT PASSED\b", "", _unquoted())
    for w in ("ACCEPTED", "ACCEPTS", "PASSES", "PASSED", "QUALIFIED:", "RELEASED"):
        assert w not in u, "the draft says %s outside a quotation" % w
    rest = re.sub(r"NOT CLOSED|CLOSED BY THE CORRECTION|CLOSED AS CONDITIONAL", "", u)
    assert "CLOSED" not in rest, "a CLOSED outside the filed verdict words"
    assert not re.search(r"DESK gate[^.\n]{0,30}\b(passes|is passed|is met|is accepted)\b", u), "the desk gate read as passed"


def _named_shas():
    d = _draft()
    shas = set(re.findall(r"`([0-9a-f]{8}|[0-9a-f]{40})`", d))
    shas |= {r for _, r, _ in ALIAS_ROW.findall(d) if r not in ("cand", "base")}
    return sorted(s for s in shas if s not in DIGEST16)


def t_every_named_sha_and_branch_exists():
    _cand_ok()
    shas = _named_shas()
    assert len(shas) >= 30, "too few shas read (%d)" % len(shas)
    absent = [s for s in shas if not _has(s)]
    if len(absent) == len(shas) - sum(1 for s in shas if _rc("merge-base", "--is-ancestor", s, CAND) == 0) and absent:
        raise Skip("this clone holds none of the coordination branches' commits (%d absent)" % len(absent))
    assert not absent, "shas not in git: %s" % absent
    branches = sorted(set(re.findall(r"`(fnd/[a-z0-9]+)`", _draft())))
    assert len(branches) >= 14, "too few branches read (%d)" % len(branches)
    missing = [b for b in branches if _rc("rev-parse", "--verify", "--quiet", "refs/heads/" + b) != 0]
    if len(missing) == len(branches):
        raise Skip("this clone has no coordination branches")
    assert not missing, "branches not in git: %s" % missing


def t_pre_freeze_in_the_candidate_next_set_not():
    _cand_ok()
    for s in PRE_FREEZE:
        if _has(s):
            assert _rc("merge-base", "--is-ancestor", s, CAND) == 0, "%s is not in the candidate" % s
    for s in NEXT_SET:
        if _has(s):
            assert _rc("merge-base", "--is-ancestor", s, CAND) != 0, "%s is in the candidate" % s
    assert _rc("merge-base", "--is-ancestor", BASE, CAND) == 0, "the base is not in the candidate's history"


def t_the_stability_digests_equal_their_files_at_the_candidate():
    _cand_ok()
    rows = re.findall(r"^(v2/\S+) pass 1: sha256=([0-9a-f]{64}); pass 2: sha256=([0-9a-f]{64}); equal$", _show(CAND, STAB), re.M)
    assert len(rows) == 18, "DIGESTS-cr3 rows: %d" % len(rows)
    bad = [p for p, a, b in rows if a != b or hashlib.sha256(_showb(CAND, p) or b"").hexdigest() != b]
    assert not bad, "outputs differing from DIGESTS-cr3 at the candidate: %s" % bad


def t_l4e9_pins_four_outputs_at_other_bytes_at_the_candidate():
    _cand_ok()
    lines = _show(CAND, L4O).splitlines()
    for n in (55, 64, 67, 106):
        m = re.match(r"^\s+\w+\s+([0-9a-f]{16})\s+(v2/\S+)$", lines[n - 1])
        assert m, "line %d is not a pin" % n
        b = _showb(CAND, m.group(2))
        assert b is not None, m.group(2)
        assert hashlib.sha256(b).hexdigest()[:16] != m.group(1), "line %d's pin matches its file at the candidate (2b?)" % n


def t_the_l4e7_cache_was_last_committed_before_the_p0_round():
    _cand_ok()
    for p, want in CACHE:
        h = _git("log", "-1", "--format=%H", CAND, "--", p).strip()
        assert h.startswith(want), "%s last committed at %s" % (p, h[:8])
        assert "`%s`" % want in _draft(), "the draft does not name %s" % want


def t_l4e11_output_has_the_bytes_l4e7_read_at_the_candidate():
    _cand_ok()
    assert hashlib.sha256(_showb(CAND, "v2/docs/records/l4e11/l4e11_power.out")).hexdigest()[:16] == "40ca9c0311440ca0"
    assert "40ca9c0311440ca0" in _show(CAND, "v2/docs/records/l4e7/l4e7_p0sol.out").splitlines()[31]
    assert "`40ca9c0311440ca0`" in _draft()


def t_seventeen_fetch_held_back_scripts_at_the_candidate():
    _cand_ok()
    names = [n for n in _git("ls-tree", "-r", "--name-only", CAND, "v2/docs/records").split()
             if n.endswith("/fetch_held_back.py")]
    assert len(names) == 17, "fetch_held_back.py scripts: %d" % len(names)
    assert "seventeen such scripts" in _draft()


def t_e11_37_is_placed_in_the_ledger_and_named_once_in_the_annex():
    _cand_ok()
    assert "### HO-L: E11-37" in _show(CAND, REM), "the ledger has no HO-L"
    assert "E11-37" not in _show(BASE, REM), "the base's ledger named E11-37 (the draft calls that history)"
    hits = [i + 1 for i, l in enumerate(_show(CAND, ANX).splitlines()) if "E11-37" in l]
    assert hits == [73], "the annex names E11-37 at %s" % hits


def t_the_ledger_summary_has_twelve_re_and_eight_ho_rows():
    _cand_ok()
    t = _show(CAND, REM)
    s = t[t.find("## 5. Summary"):t.find("## 6.")]
    rows = re.findall(r"^\| ((?:RE|HO)-[0-9A-Z]+) \| remaining engineering \|", s, re.M)
    assert len([r for r in rows if r.startswith("RE-")]) == 12, rows
    assert sorted(r for r in rows if r.startswith("HO-")) == ["HO-%s" % c for c in "ABCDEFGL"], rows
    assert "Counts: remaining engineering 20;" in s


def t_no_em_or_en_dash():
    assert not any(d in _draft() for d in DASHES), "a dash in the draft"
    s = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in s for d in DASHES), "a dash in this module"


def _prom_ok():
    if not _has(PROM):
        raise Skip("the promoted revision %s is not in this clone's object store" % PROM[:8])


def t_the_adoption_reads_the_promoted_revision():
    """The facts the adoption re-read at PROM (A2.3 and K-28 restated, the ticks of section 9, the basis resolutions)."""
    _prom_ok()
    d = " ".join(_draft().split())
    lines = _show(PROM, L4O).splitlines()
    for n in (55, 64, 67, 106):
        m = re.match(r"^\s+\w+\s+([0-9a-f]{16})\s+(v2/\S+)$", lines[n - 1])
        assert m, "line %d is not a pin at PROM" % n
        assert hashlib.sha256(_showb(PROM, m.group(2))).hexdigest()[:16] == m.group(1), "line %d's pin differs at PROM" % n
        assert ("%s" % m.group(1)) in d and ("[L4OP:%d]" % n) in d, "A2.3's restatement lacks pin %d" % n
    con = _show(PROM, "v2/docs/records/l9t5/l9t5_connected.out").splitlines()
    assert "L4-E9's own output refuses on this tree at its L4-E11 pin" in con[361], "K-28's sentence at PROM"
    assert "its KEY holds on this tree: no part differs" in _show(PROM, "v2/docs/records/l4e7/l4e7_p0sol.out").splitlines()[30]
    h = _git("log", "-1", "--format=%H", PROM, "--", CACHE[0][0]).strip()
    assert h.startswith("c2a532a9") and "`c2a532a9`" in _draft(), "the cache's last commit at PROM"
    rows = re.findall(r"^(v2/\S+) pass 1: sha256=([0-9a-f]{64}); pass 2: sha256=([0-9a-f]{64}); equal$", _show(PROM, STAB), re.M)
    differ = [p for p, a, b in rows if hashlib.sha256(_showb(PROM, p) or b"").hexdigest() != b]
    assert len(rows) == 18 and len(differ) == 17 and "differ from seventeen of them at `dd1aed00`" in d, "the digests at PROM"
    assert _showb(PROM, PAGE) == _showb(CAND, PAGE), "L4-E9's page moved after the candidate"
    for s in NEXT_SET:
        if _has(s):
            assert _rc("merge-base", "--is-ancestor", s, PROM) != 0, "%s is in the promoted revision" % s
    assert _show(PROM, "v2/docs/records/l4close/P0-POWER-LIST.md").startswith("# P0: the power architecture's current blockers (one compact list; revision 2")
    assert _show(PROM, "v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md") == _show(CAND, "v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md")
    rem = _show(PROM, REM)
    assert "Counts: remaining engineering 20; qualification 1; external architecture fact 3; closed 4; conditional 2." in rem.splitlines()[668]


def t_the_y6_table_has_one_row_per_ledger_item():
    """Section 6a: one row per RE item of the ledger at PROM, every REMP citation of a row inside that item's own lines, the class
    the summary's row of that item, and the coordinator's reading at its end."""
    _prom_ok()
    t = _draft()
    i = t.find("\n## 6a. ")
    assert i >= 0, "no section 6a"
    s = t[i:t.find("\n## 7. ")]
    rem = _show(PROM, REM).splitlines()
    spans, cur = {}, None
    for n, l in enumerate(rem, 1):
        m = re.match(r"^### (RE-\d+) ", l)
        if m:
            cur = m.group(1)
            spans[cur] = [n, n]
        elif l.startswith("## ") or l.startswith("### "):
            cur = None
        elif cur:
            spans[cur][1] = n
    summ = {m.group(1): n for n, l in enumerate(rem, 1) for m in [re.match(r"^\| (RE-\d+) \| remaining engineering \|", l)] if m}
    rows = re.findall(r"^\| (RE-\d+) \|(.*)\|$", s, re.M)
    assert [r for r, _ in rows] == sorted(spans, key=lambda k: spans[k][0]) and len(rows) == 12, "the Y6 rows: %s" % [r for r, _ in rows]
    for rid, rest in rows:
        c = [x.strip() for x in rest.split(" | ")]
        assert len(c) == 6, "%s: %d cells" % (rid, len(c))
        for cell in c[:5]:
            for m in re.finditer(r"\[REMP:(\d+)(?:-(\d+))?\]", cell):
                a, b = int(m.group(1)), int(m.group(2) or m.group(1))
                assert spans[rid][0] <= a <= b <= spans[rid][1], "%s cites %s outside its item" % (rid, m.group(0))
        assert c[5] == "remaining engineering [REMP:%d]" % summ[rid], "%s: class cell %r" % (rid, c[5])
    assert s.rstrip().endswith("> The coordinator's reading: carried under an ended method, not parked."), "the coordinator's reading"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
