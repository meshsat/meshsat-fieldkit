"""W17 (MESHSAT-1357, 6 October 2026): the P0 list's revision 3, draft 3, held as predicates on record text.

The file: v2/docs/records/l4close/P0-POWER-LIST.rev3.draft3.md, Slot K's draft 2 with W7's rows R-01 to R-09 of
v2/docs/records/l4close/P0-POWER-LIST.rev3.patch.md applied, every citation, figure and class re-read at the candidate's commit 2b
d83d9f2d. Each predicate is run on the draft and on a mutant of it that it must refuse:

- the revision block carries the two placeholders, the REVIEWED sha, revision 3 and the no-closure sentence, and names exactly the
  rows whose table cell is marked changed after the review;
- every line citation resolves: a bare `path:N` reads the same lines at bbba3e53 (draft 2's convention) and at the candidate, except
  the three the draft lists as reading at bbba3e53 only, whose quotations are on their lines there and whose candidate lines are
  given beside them; a `<sha>:path:N` names lines that exist at that revision (a `:N` continues the citation before it);
- every figure with a unit (or a range of them) in a paragraph or table row is on a line that paragraph or row cites, at the
  revision the citation names (a bare citation at the candidate, a listed one at bbba3e53); the revision block's figures each occur
  in a checked paragraph;
- every quotation followed by a citation is on the cited lines at that revision;
- every row's ledger column gives the ledger's class for each item (the summary table of REMAINING-ENGINEERING.md at the
  candidate), every ledger item sits in exactly one row and on the row its own identifier or heading names, and the bold class
  words of the row's state cell are the classes of its items;
- the nine patch rows' new texts are present and their old texts absent (outside the new texts);
- no em or en dash, the prototype framing, the first line DONE / NOT DONE / NEXT.

Read-only: git is read with `git show`; nothing is written. A checkout without git or without the commits raises Skip. These are
predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

D3 = "v2/docs/records/l4close/P0-POWER-LIST.rev3.draft3.md"
P0P = "v2/docs/records/l4close/P0-POWER-LIST.rev3.patch.md"
LEDGER = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
BASE = "bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45"       # draft 2's convention
CAND = "d83d9f2d720878ca5267dbf59bdc571c6890fd92"       # the integration's commit 2b, read as the candidate
REVIEWED = "4d0ff8a2"
DASHES = (chr(0x2013), chr(0x2014))
MARK = "changed after the review"
EXC_HEAD = "## Citations that read at `bbba3e53` only"
CLASS_WORDS = {"REMAINING ENGINEERING": "remaining engineering", "CLOSED IN SCOPE": "closed", "CONDITIONAL": "conditional",
               "EXTERNAL": "external architecture fact", "QUALIFICATION": "qualification"}
# The ledger heading words that place each handed-over item on its row (the ledger's own headings at the candidate).
HO_ANCHOR = {"HO-A": ("P0-5", "inside RE-10"), "HO-B": ("P0-5", "inside RE-10"), "HO-C": ("P0-3", "inside RE-5"),
             "HO-D": ("P0-3", "inside RE-5"), "HO-E": ("P0-3", "VOS0"), "HO-F": ("P0-7", "D-10"), "HO-G": ("P0-7", "B2"),
             "HO-H": ("E11-29", "E11-29"), "HO-I": ("U-01", "U-01"), "HO-J": ("U-02", "U-02"), "HO-K": ("U-04", "U-04"),
             "HO-L": ("P0-8", "P0-8")}
_C = {}


def _git_show(commit, rel):
    k = (commit, rel)
    if k not in _C:
        try:
            r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
        except OSError:
            raise Skip("no git here")
        _C[k] = r.stdout.decode("utf-8") if r.returncode == 0 else None
    return _C[k]


def _need_commits():
    for sha in (BASE, CAND, REVIEWED):
        try:
            r = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", sha + "^{commit}"], capture_output=True)
        except OSError:
            raise Skip("no git here")
        if r.returncode != 0:
            raise Skip("commit %s is not in this object store" % sha[:8])


def _draft():
    return open(need(os.path.join(ROOT, D3), "the draft"), encoding="utf-8").read()


def _norm(s):
    return " ".join(s.replace("**", "").replace("\\|", "|").split())


SPAN = re.compile(r"`([^`]+)`")
CIT = re.compile(r"^(?:([0-9a-f]{8,40}):)?(v2/[^\s:`]+|):(\d+)(?:-(\d+))?$")


def _cites(text):
    """Every line citation in order: (line number in the draft, sha or None, path, a, b, start offset in that line)."""
    out, path, sha = [], None, None
    for ln, line in enumerate(text.split("\n"), 1):
        for m in SPAN.finditer(line):
            c = CIT.match(m.group(1))
            if not c:
                continue
            if c.group(2):
                path, sha = c.group(2), c.group(1)
            if path is None:
                continue
            out.append((ln, sha, path, int(c.group(3)), int(c.group(4) or c.group(3)), m.start()))
    return out


def _exceptions(text):
    """The bare citations the draft lists as reading at bbba3e53 only: {(path, line)}."""
    if EXC_HEAD not in text:
        return set()
    sec = text.split(EXC_HEAD, 1)[1].split("\n## ", 1)[0]
    return {(p, a) for (_, s, p, a, b, _) in _cites(sec) if s is None}


def _lines(sha, path, a, b):
    f = _git_show(sha, path)
    if f is None:
        return None
    L = f.split("\n")
    if b > len(L) or a < 1:
        return None
    return L[a - 1:b]


def _rev(sha, path, a, exc):
    """The revision a citation reads at: its own sha, else bbba3e53 for a listed exception, else the candidate."""
    if sha:
        return sha
    return BASE if (path, a) in exc else CAND


# ---- predicates (each returns a list of problems) ----

def p_revision_block(text):
    bad = []
    head = text.split("**Revision block.**", 1)[-1].split("**Draft 3**", 1)[0]
    for w in ("__CANDIDATE__", "__PROMOTED__", "Revision: **3**", "`4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e`",
              "**No row is closed by this revision.**", "Power-design closure: BLOCKED", "Fabrication release: BLOCKED"):
        if w not in head:
            bad.append("revision block lacks %r" % w)
    named = set(re.findall(r"\*\*(P0-\d|U-0\d|E11-29)\*\* \(", head))
    marked = {ln.split(" | ")[0][2:] for ln in text.split("\n") if ln.startswith("| ") and MARK in ln}
    if not named or named != marked:
        bad.append("rows named %s, rows marked %s" % (sorted(named), sorted(marked)))
    if REVIEWED + "`" not in head:
        bad.append("REVIEWED sha")
    return bad


def p_citations(text):
    bad = []
    exc = _exceptions(text)
    if len(exc) != 3:
        bad.append("exceptions %d" % len(exc))
    sec = text.split(EXC_HEAD, 1)[1].split("\n## ", 1)[0] if EXC_HEAD in text else ""
    for (ln, sha, path, a, b, _) in _cites(text):
        if sha:
            if _lines(sha, path, a, b) is None:
                bad.append("%d: %s:%s:%d-%d does not exist" % (ln, sha, path, a, b))
            continue
        x, y = _lines(BASE, path, a, b), _lines(CAND, path, a, b)
        if x is None or y is None:
            bad.append("%d: %s:%d-%d missing" % (ln, path, a, b))
        elif x != y and (path, a) not in exc:
            bad.append("%d: %s:%d-%d reads differently at the candidate" % (ln, path, a, b))
    # each exception's bullet: the old quote on its line at bbba3e53, the candidate's quote on the candidate line it gives
    for bullet in [l for l in sec.split("\n") if l.startswith("- R-0")]:
        qs = re.findall(r"\"([^\"]+)\"", bullet)
        cs = _cites(bullet)
        if len(qs) != 2 or len(cs) != 2:
            bad.append("exception bullet shape: %s" % bullet[:40])
            continue
        (_, s0, p0, a0, b0, _), (_, s1, p1, a1, b1, _) = cs
        if s0 is not None or not s1 or not CAND.startswith(s1):
            bad.append("exception bullet citations: %s" % bullet[:40])
            continue
        if qs[0] not in " ".join(_lines(BASE, p0, a0, b0)) or qs[0] in " ".join(_lines(CAND, p0, a0, b0)):
            bad.append("exception old quote: %s" % qs[0][:40])
        if qs[1] not in " ".join(_lines(CAND, p1, a1, b1)):
            bad.append("exception candidate quote: %s" % qs[1][:40])
    return bad


UNIT = r"(?:mOhm|K/W|mA|uA|mV|ms|nF|uH|kOhm|V|A|C|K|W|s|%)"
FIG = re.compile(r"(?<![\w.])(\d+\.\d+|\d+(?= ?ms\b))(?: to (\d+\.\d+))? ?(" + UNIT + r")(?![\w/])")


def _units(text):
    """Paragraphs: a table row alone, a list item alone, else blank-line separated prose."""
    units, cur = [], []
    for line in text.split("\n"):
        if line.startswith("|") or line.startswith("- ") or not line.strip() or line.startswith("#"):
            if cur:
                units.append("\n".join(cur))
                cur = []
            if line.startswith("|") or line.startswith("#"):
                units.append(line)
                continue
            if line.startswith("- "):
                cur = [line]
            continue
        cur.append(line)
    if cur:
        units.append("\n".join(cur))
    return units


def _figs(unit):
    out = []
    for m in FIG.finditer(unit):
        for g in (m.group(1), m.group(2)):
            if g:
                out.append(g)
    return out


def p_figures(text):
    bad, found = [], set()
    exc = _exceptions(text)
    head = text.split("**Draft 3**", 1)[0]
    body = text[len(head):]
    for unit in _units(body):
        figs = _figs(unit)
        if not figs:
            continue
        segs = []
        for (_, sha, path, a, b, _) in _cites(unit):
            L = _lines(_rev(sha, path, a, exc), path, a, b)
            if L is not None:
                segs.append(_norm(" ".join(L)))
        if not segs:
            bad.append("figures without a citation: %s" % unit[:60])
            continue
        for f in figs:
            if any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", s) for s in segs):
                found.add(f)
            else:
                bad.append("%s is on no line its paragraph cites: %s" % (f, unit[:50]))
    for f in _figs(head):
        if f not in found:
            bad.append("revision block figure %s is not checked in a row" % f)
    return bad


QPROSE = re.compile(r"\"([^\"]{8,400}?)\"[^\"`|]{0,60}?\(?`(?:([0-9a-f]{8,40}):)?(v2/[^`:\s]+):(\d+)(?:-(\d+))?`")


def p_quotations(text):
    bad, n = [], 0
    exc = _exceptions(text)
    for unit in _units(text):
        flat = " ".join(unit.split())
        for m in QPROSE.finditer(flat):
            sha, path, a = m.group(2), m.group(3), int(m.group(4))
            b = int(m.group(5) or a)
            L = _lines(_rev(sha, path, a, exc), path, a, b)
            if L is None:
                bad.append("quote target missing %s:%d" % (path, a))
                continue
            seg = _norm(" ".join(L))
            for part in _norm(m.group(1)).split("..."):
                part = part.strip()
                if part and part not in seg:
                    bad.append("%r is not on %s:%d-%d" % (part[:50], path, a, b))
            n += 1
    if n < 20:
        bad.append("only %d quotations read" % n)
    return bad


def _ledger():
    f = _git_show(CAND, LEDGER)
    if f is None:
        raise Skip("the ledger at the candidate is not readable")
    summ = f.split("## 5. Summary", 1)[1].split("\n## ", 1)[0]
    cls = {}
    for ln in summ.split("\n"):
        c = [x.strip() for x in ln.split("|")]
        if len(c) > 3 and re.match(r"^(RE|HO|CL|CO)-\w+$", c[1]):
            cls[c[1]] = c[2]
    heads = {m.group(1): m.group(0) for m in re.finditer(r"^### (HO-[A-L]):.*$", f, re.M)}
    return cls, heads


def _table(text):
    rows = {}
    for ln in text.split("\n"):
        if ln.startswith("| ") and not ln.startswith("| Id ") and not ln.startswith("|---"):
            c = [x.strip() for x in re.split(r"(?<!\\)\|", ln)[1:-1]]
            rows[c[0]] = c
    return rows


def p_classes(text):
    bad = []
    cls, heads = _ledger()
    rows = _table(text)
    seen = {}
    for rid, c in rows.items():
        if len(c) != 9:
            bad.append("%s: %d columns" % (rid, len(c)))
            continue
        items = []
        for part in c[8].split(";"):
            m = re.match(r"^\s*((?:RE|HO|CL|CO)-\w+): (.+?)\s*$", part)
            if not m:
                bad.append("%s: ledger cell %r" % (rid, part))
                continue
            items.append((m.group(1), m.group(2)))
        for item, word in items:
            if cls.get(item) != word:
                bad.append("%s: %s reads %r, the ledger %r" % (rid, item, word, cls.get(item)))
            if item in seen:
                bad.append("%s in %s and %s" % (item, seen[item], rid))
            seen[item] = rid
            if item[:2] in ("RE", "CL", "CO"):
                n = item.split("-")[1]
                if not re.search(r"\b[Ii]tems? (?:[\d, ]+and )?[\d, ]*\b%s\b" % n, c[5]):
                    bad.append("%s: cx46 item %s is not in the row's cx46 cell" % (rid, n))
            else:
                want_row, anchor = HO_ANCHOR[item]
                if rid != want_row or anchor not in heads.get(item, ""):
                    bad.append("%s: %s placed against its ledger heading" % (rid, item))
        state = set(CLASS_WORDS[w] for w in re.findall(r"\*\*(REMAINING ENGINEERING|CLOSED IN SCOPE|CONDITIONAL|EXTERNAL|QUALIFICATION)\*\*", c[7]))
        if state != set(w for _, w in items):
            bad.append("%s: state words %s, ledger classes %s" % (rid, sorted(state), sorted(set(w for _, w in items))))
    if set(seen) != set(cls):
        bad.append("ledger items not placed: %s; unknown: %s" % (sorted(set(cls) - set(seen)), sorted(set(seen) - set(cls))))
    return bad


def _patch_rows():
    p = open(need(os.path.join(ROOT, P0P), "W7's patch"), encoding="utf-8").read()
    parts = re.split(r"^### (R-\d\d)\.", p, flags=re.M)
    rows = {}
    for i in range(1, len(parts), 2):
        b = parts[i + 1]
        blocks = re.findall(r"```text\n(.*?)\n```", b, re.S)
        rows[parts[i]] = dict(kind=re.search(r"^- Kind: (\w+)", b, re.M).group(1), old=blocks[0], new=blocks[1])
    return rows


def p_patch_rows(text):
    bad = []
    rows = _patch_rows()
    if sorted(rows) != ["R-%02d" % i for i in range(1, 10)]:
        bad.append("rows %s" % sorted(rows))
    for rid, r in rows.items():
        n = text.count(r["new"])
        if (n < 16) if r["kind"] == "every" else (n != 1):
            bad.append("%s: new text %d times" % (rid, n))
        if r["old"] in text.replace(r["new"], ""):
            bad.append("%s: old text present" % rid)
    return bad


def p_hygiene(text):
    bad = []
    if any(ch in text for ch in DASHES):
        bad.append("a dash")
    if not text.startswith("**DONE:**") or "**NOT DONE:**" not in text.split("\n")[0] or "**NEXT:**" not in text.split("\n")[0]:
        bad.append("first line")
    if "Prototype framing" not in _norm(text):
        bad.append("prototype framing")
    return bad


# ---- the tests: each predicate holds on the draft and refuses its mutant ----

def _both(pred, mutate):
    _need_commits()
    t = _draft()
    probs = pred(t)
    assert not probs, probs[:6]
    m = mutate(t)
    assert m != t, "the mutant changed nothing"
    assert pred(m), "the mutant was not refused"


def t_revision_block_and_marks():
    _both(p_revision_block, lambda t: t.replace("- Promoted: `__PROMOTED__`", "- Promoted: pending", 1))
    _both(p_revision_block, lambda t: t.replace("; **changed after the review**: the rail trip's average and transient (row note)", "", 1))


def t_every_citation_reads_at_the_candidate():
    _both(p_citations, lambda t: t.replace(EXC_HEAD, "## Citations", 1))


def t_every_figure_is_on_its_cited_lines():
    _both(p_figures, lambda t: t.replace("\"a 1.17 s average\"", "\"a 1.1 s average\"", 1))
    _both(p_figures, lambda t: t.replace("IDD at 30.0 W at most 6.351 A", "IDD at 30.0 W at most 6.352 A", 1))


def t_every_quotation_reads_on_its_cited_lines():
    _both(p_quotations, lambda t: t.replace("\"criterion 2 FAIL with 2 defects open\"", "\"criterion 2 CONDITIONAL with 2 defects open\"", 1))


def t_classes_equal_the_ledgers():
    _both(p_classes, lambda t: t.replace("| **REMAINING ENGINEERING** (the ledger's HO-L)", "| **EXTERNAL** (the ledger's HO-L)", 1))
    _both(p_classes, lambda t: t.replace("HO-L: remaining engineering", "HO-L: external architecture fact", 1))


def t_the_nine_patch_rows_applied():
    rows = _patch_rows()
    _both(p_patch_rows, lambda t: t.replace(rows["R-04"]["new"], rows["R-04"]["old"], 1))


def t_no_dashes_and_the_framing():
    _both(p_hygiene, lambda t: t.replace("Prototype framing", "Framing"))
    me = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(ch in me for ch in DASHES)


test_revision_block_and_marks = t_revision_block_and_marks
test_every_citation_reads_at_the_candidate = t_every_citation_reads_at_the_candidate
test_every_figure_is_on_its_cited_lines = t_every_figure_is_on_its_cited_lines
test_every_quotation_reads_on_its_cited_lines = t_every_quotation_reads_on_its_cited_lines
test_classes_equal_the_ledgers = t_classes_equal_the_ledgers
test_the_nine_patch_rows_applied = t_the_nine_patch_rows_applied
test_no_dashes_and_the_framing = t_no_dashes_and_the_framing
