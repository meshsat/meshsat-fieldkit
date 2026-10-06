"""The draft of Layer 4's DESK-gate assessment (MESHSAT-1357, 6 October 2026), held as predicates on its text and on the files it
cites: v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md.

The draft is record text for the coordinator, who adopts, edits or rejects it at promotion; it is not the assessment. It cites
files by alias, `[ALIAS:N]` or `[ALIAS:N-M]`, through its own alias table. An alias whose revision reads `base` names a file at
set 30's integration commit 2a (BASE below), which is in this branch's history: this module reads every such file AT THAT COMMIT
(git show), never the working tree, so a later edit of a cited record leaves the draft's citations true of the revision they name.
An alias with another commit names a file on another branch, cited as text only by the worker rule: its citations are checked
when that commit is in the object store, and otherwise only their form and the alias table are (a clone that holds only the
candidate's history has none of those branches; this is stated here so that the reduced reading is never mistaken for the full
one).

The predicates: the header says DRAFT and not the assessment and names the base; every alias row names a file that exists at its
revision; every citation uses an alias of the table and lies inside its file; every quotation of twelve characters or more is
found verbatim (emphasis marks and whitespace aside) within two lines of the range of the first citation after it; each of the
four parts states its counts of evidence for and against and carries exactly that many items, numbered in order; the
contradictions K-01 to K-NN are numbered in order, their stated count and their count of YES agree with the table, and every row
reads YES or NO; Slot G's sixteen items each have one row; the nineteen remaining-engineering items and the annex's four
each have one acceptance row; the verdict placeholder appears once and the completion claims read as
briefed; the design gate's verdict words appear in its own section only; nothing outside a quotation reads as an acceptance; and
the facts the draft read with git at the base hold there (the eighteen stability digests equal their files, L4-E9's output pins
four cascade outputs at other bytes, record l4e7's cache was last committed at set 29's freeze and its output before it, L4-E11's output at the bytes record l4e7 read, seventeen fetch_held_back.py
scripts, E11-37 named once in the annex and not in the ledger, twelve RE and seven HO remaining-engineering rows in the ledger's
summary). No em or en dash. These are software predicates on record text: they establish no electrical or thermal property and
close nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_dgate.`) and under pytest (each t_ function has a test_
alias). Without git, or without the base commit in the object store, the rules that read the base skip with their reason."""
import hashlib
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
DRAFT = os.path.join(ROOT, "v2", "docs", "records", "l4close", "L4-DESK-GATE-ASSESSMENT.draft.md")
BASE = "bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

ALIAS_ROW = re.compile(r"^\| ([A-Z][A-Z0-9]*) \| (base|[0-9a-f]{8}) \| `(v2/[^`]+)`", re.M)
CITE = re.compile(r"\[([A-Z][A-Z0-9]*)(?::(\d+)(?:-(\d+))?)?\]")
DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
PLACEHOLDER = "[COORDINATOR: DESK-gate verdict]"
CLAIMS = ("- documents and editable artifacts: on main as a DESK candidate",
          "- design reviewed and accepted: NO",
          "- implemented: NONE",
          "- physical qualification: NONE",
          "- fabrication release: BLOCKED",
          "- power-design closure: BLOCKED")
DESIGN_WORDS = ("criterion 1 CONDITIONAL", "criterion 2 FAIL", "criterion 3 PASS", "criterion 4 PASS", "criterion 5 CONDITIONAL")
STAB = "v2/docs/records/l9t5/stability/DIGESTS-cr3.txt"
L4O = "v2/docs/records/l4e9/l4e9_power_path.out"
CACHE = (("v2/docs/records/l4e7/l4e7_stage_settings.results.json", "69921ce8"),
         ("v2/docs/records/l4e7/l4e7_stage_settings.out", "914a2f5a"))
REM = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
_C = {}


def _draft():
    if "d" not in _C:
        _C["d"] = open(need(DRAFT, "the DESK-gate assessment draft"), encoding="utf-8").read()
    return _C["d"]


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git on this host (%s)" % e)
    if r.returncode != 0:
        raise Skip("git %s: %s" % (a[0], r.stderr.decode(errors="replace")[:100].strip()))
    return r.stdout.decode("utf-8")


def _has(rev):
    k = ("has", rev)
    if k not in _C:
        try:
            r = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", rev + "^{commit}"], capture_output=True)
            _C[k] = r.returncode == 0
        except OSError:
            _C[k] = False
    return _C[k]


def _base_ok():
    if not _has(BASE):
        raise Skip("the base %s is not in this clone's object store" % BASE[:8])


def _show(rev, path):
    """The text of path at rev, or None when rev has no such file."""
    k = ("s", rev, path)
    if k not in _C:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)], capture_output=True)
        _C[k] = r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else None
    return _C[k]


def _aliases():
    """alias -> (revision, path); revision BASE for a `base` row."""
    out = {}
    for a, rev, path in ALIAS_ROW.findall(_draft()):
        out[a] = (BASE if rev == "base" else rev, path)
    return out


def _norm(t):
    return " ".join(t.replace("*", "").replace("`", "").split())


def _quotes():
    """Every double-quoted span of the draft with its end offset, in order."""
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
    head = _draft()[:1500]
    assert head.startswith("# Layer 4's DESK gate"), "the title"
    assert "**Status: DRAFT. This file is not the assessment.**" in head
    assert BASE in head, "the base is not named in full"
    assert "Prototype framing" in head and "nothing in the kit has been built, bought, powered or measured" in head


def t_every_alias_row_names_an_existing_file():
    al = _aliases()
    assert len(al) >= 40, "the alias table is not read (%d rows)" % len(al)
    _base_ok()
    missing = []
    for a, (rev, path) in sorted(al.items()):
        if rev != BASE and not _has(rev):
            continue  # another branch's commit absent from this clone: form only (see the module docstring)
        if _show(rev, path) is None:
            missing.append("%s %s:%s" % (a, rev[:8], path))
    assert not missing, "alias rows naming no file: %s" % missing


def t_every_citation_uses_an_alias_and_lies_inside_its_file():
    al = _aliases()
    _base_ok()
    bad = []
    n = 0
    for m in CITE.finditer(_draft()):
        a, lo, hi = m.group(1), m.group(2), m.group(3)
        if a == "ALIAS":
            continue  # the citation form's own placeholder, in the paragraph that defines it
        if a not in al:
            bad.append("unknown alias %s" % m.group(0))
            continue
        n += 1
        rev, path = al[a]
        if rev != BASE and not _has(rev):
            continue
        t = _show(rev, path)
        if t is None:
            bad.append("%s: no file" % m.group(0))
            continue
        if lo:
            last = int(hi or lo)
            if int(lo) < 1 or last < int(lo) or last > len(t.splitlines()):
                bad.append("%s: outside %d lines" % (m.group(0), len(t.splitlines())))
    assert n >= 300, "too few citations read (%d)" % n
    assert not bad, "bad citations: %s" % bad[:12]


def t_every_quotation_is_found_where_its_citation_points():
    al = _aliases()
    _base_ok()
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
        if rev != BASE and not _has(rev):
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
    assert checked >= 60, "too few quotations checked (%d)" % checked
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
    return re.findall(r"^\| (K-\d\d) \|(.*)\|$", _section(5), re.M)


def t_the_contradictions_list_agrees_with_its_counts():
    s = _section(5)
    rows = _k_rows()
    ids = [r[0] for r in rows]
    assert ids == ["K-%02d" % i for i in range(1, len(ids) + 1)], "K ids out of order: %s" % ids
    m = re.search(r"The list has (\d+) entries; (\d+) read YES", s)
    assert m, "no stated count"
    assert int(m.group(1)) == len(rows), "stated %s entries, table %d" % (m.group(1), len(rows))
    stumble = [r[1].rsplit("|", 1)[1].strip() for r in rows]
    assert all(x.startswith("YES") or x.startswith("NO") for x in stumble), "a Stumble cell reads neither YES nor NO"
    yes = sum(1 for x in stumble if x.startswith("YES"))
    assert int(m.group(2)) == yes, "stated %s YES, table %d" % (m.group(2), yes)
    for n in re.findall(r"\((\d+) stand at YES", _draft()):
        assert int(n) == yes, "section 6 states %s at YES, table %d" % (n, yes)
    words = ("Seventeen", 17), ("twenty-eight", 28)
    a14 = re.search(r"- A1\.4 (\w+) of the ([\w-]+) contradictions", _draft())
    assert a14, "A1.4's counts"
    assert dict(words).get(a14.group(1)) == yes and dict(words).get(a14.group(2)) == len(rows), "A1.4's words disagree"


def t_slot_g_items_each_have_one_row():
    s = _section(5)
    for i in range(1, 17):
        assert len(re.findall(r"^\| PC-%02d " % i, s, re.M)) == 1, "PC-%02d's row" % i


HANDED = ["RE-%d" % i for i in (1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18)] + ["HO-%s" % c for c in "ABCDEFG"] + [
    "U-01", "U-02", "U-04", "E11-29"]


def t_every_handed_over_item_has_one_acceptance_row():
    s = _section(4)
    for it in HANDED:
        assert len(re.findall(r"^\| %s \| (remaining engineering|external architecture fact|qualification) \|" % re.escape(it), s, re.M)) == 1, it
    assert len(re.findall(r"^\| (?:RE|HO|U|E11)-[0-9A-Z]+ \| ", s, re.M)) == len(HANDED), "rows beyond the ledger's and the annex's items"


def t_the_placeholder_and_the_completion_claims():
    d = _draft()
    assert d.count(PLACEHOLDER) == 2, "the placeholder: once in the header (as code) and once as the verdict"
    assert d.count("`%s`" % PLACEHOLDER) == 1, "the header names the placeholder as code once"
    s6 = _section(6)
    assert ("<INTEGRATED-SHA>`: %s" % PLACEHOLDER) in s6, "the verdict line does not carry the placeholder"
    for c in CLAIMS:
        assert len(re.findall("^" + re.escape(c), s6, re.M)) == 1, "the claim %r" % c


def t_the_design_gate_words_are_in_their_own_section():
    s7 = " ".join(_section(7).split())
    for w in DESIGN_WORDS:
        assert w in s7, "section 7 lacks %r" % w
    rest = " ".join((_before_section(7) + _draft()[_draft().find("\n## 8. "):]).split())
    for w in DESIGN_WORDS:
        assert w not in rest, "%r outside section 7" % w
    assert not re.search(r"criterion \d (PASS|FAIL|CONDITIONAL)", rest), "a criterion verdict outside section 7"


def t_nothing_outside_a_quotation_reads_as_an_acceptance():
    u = _unquoted()
    for w in ("ACCEPTED", "ACCEPTS", "PASSES", "PASSED", "QUALIFIED:", "RELEASED"):
        assert w not in u, "the draft says %s outside a quotation" % w
    rest = re.sub(r"NOT CLOSED|CLOSED BY THE CORRECTION|CLOSED AS CONDITIONAL", "", u)
    assert "CLOSED" not in rest, "a CLOSED outside the filed verdict words"
    assert not re.search(r"DESK gate[^.\n]{0,30}\b(passes|is passed|is met|is accepted)\b", u), "the desk gate read as passed"


def t_the_stability_digests_equal_their_files_at_the_base():
    _base_ok()
    rows = re.findall(r"^(v2/\S+) pass 1: sha256=([0-9a-f]{64}); pass 2: sha256=([0-9a-f]{64}); equal$", _show(BASE, STAB), re.M)
    assert len(rows) == 18, "DIGESTS-cr3 rows: %d" % len(rows)
    bad = []
    for path, a, b in rows:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, path)], capture_output=True)
        if a != b or r.returncode != 0 or hashlib.sha256(r.stdout).hexdigest() != b:
            bad.append(path)
    assert not bad, "outputs differing from DIGESTS-cr3 at the base: %s" % bad


def t_l4e9_pins_four_outputs_at_other_bytes_at_the_base():
    _base_ok()
    lines = _show(BASE, L4O).splitlines()
    for n in (55, 64, 67, 106):
        m = re.match(r"^\s+\w+\s+([0-9a-f]{16})\s+(v2/\S+)$", lines[n - 1])
        assert m, "line %d is not a pin" % n
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, m.group(2))], capture_output=True)
        assert r.returncode == 0, m.group(2)
        assert hashlib.sha256(r.stdout).hexdigest()[:16] != m.group(1), "line %d's pin matches its file at the base" % n


def t_the_l4e7_cache_was_last_committed_before_the_p0_round():
    _base_ok()
    for p, want in CACHE:
        h = _git("log", "-1", "--format=%H", BASE, "--", p).strip()
        assert h.startswith(want), "%s last committed at %s" % (p, h[:8])
        assert "`%s`" % want in _draft(), "the draft does not name %s" % want


def t_l4e11_output_has_the_bytes_l4e7_read_at_the_base():
    _base_ok()
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/records/l4e11/l4e11_power.out" % BASE], capture_output=True)
    assert r.returncode == 0
    assert hashlib.sha256(r.stdout).hexdigest()[:16] == "40ca9c0311440ca0", "l4e11_power.out moved at the base"
    assert "40ca9c0311440ca0" in _show(BASE, "v2/docs/records/l4e7/l4e7_p0sol.out").splitlines()[31]
    assert "`40ca9c0311440ca0`" in _draft()


def t_seventeen_fetch_held_back_scripts_at_the_base():
    _base_ok()
    names = [n for n in _git("ls-tree", "-r", "--name-only", BASE, "v2/docs/records").split()
             if n.endswith("/fetch_held_back.py")]
    assert len(names) == 17, "fetch_held_back.py scripts: %d" % len(names)
    assert "seventeen such scripts" in _draft()


def t_e11_37_is_not_a_task_of_the_ledger_or_the_annex():
    _base_ok()
    assert "E11-37" not in _show(BASE, REM), "the ledger names E11-37"
    hits = [i + 1 for i, l in enumerate(_show(BASE, ANX).splitlines()) if "E11-37" in l]
    assert hits == [73], "the annex names E11-37 at %s" % hits


def t_the_ledger_summary_has_twelve_re_and_seven_ho_rows():
    _base_ok()
    t = _show(BASE, REM)
    s = t[t.find("## 5. Summary"):t.find("## 6.")]
    rows = re.findall(r"^\| ((?:RE|HO)-[0-9A-Z]+) \| remaining engineering \|", s, re.M)
    assert len([r for r in rows if r.startswith("RE-")]) == 12, rows
    assert len([r for r in rows if r.startswith("HO-")]) == 7, rows


def t_no_em_or_en_dash():
    assert not any(d in _draft() for d in DASHES), "a dash in the draft"
    s = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in s for d in DASHES), "a dash in this module"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
