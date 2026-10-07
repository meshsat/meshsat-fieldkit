"""W28 (MESHSAT-1357, 6 October 2026): set 31's Q-40 text items, held as predicates on the pages' text.

The pages: v2/docs/records/l4close/REMAINING-ENGINEERING.md (the ledger), record l4e7's three P0 pages
(v2/docs/records/l4e7/L4E7-P0SOL.md, SUPPLIER-P1-1-P0SOL.md and B2-PRESENCE.md) and the supplier annex
(v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md). The items, the coordinator's queue row Q-40 from W23's report:

- the ledger's HO-F line that read "completed independently: D-16's correction and its rows ([P11:89-92])" is restated to W4's
  passage, where record l4e7's P11 page now reads D-16's correction "ADDRESSED IN DRAFTS, PROVISIONAL, not completed"
  ([P11:119-126]); the pre-W4 words, "Completed independently of E-1", are kept and marked as standing at [P11:89-92] on 1c6d56f5;
- the ledger's [T10:638] and [T10R:51-54] re-cited to the lines where their quoted words stand ([T10R:153], [T10R:224]; the
  second keeps [T10R:51-54] for the claim it carries, "that would admit any revision");
- record l4e7's owner-file citations moved by one line with the owner file (part 26's table row at line 26, b0a67a45): :680 to
  :681, :708 to :709, :838 to :839 (W23 listed eight; L4E7-P0SOL.md line 26 carries a ninth :838, moved the same way);
- the annex's section 6.4 sentence ("stand as written") and section 8's K-23 pointer each carry one dated note that W4's rewrite
  of record l4e7's pages at 786aed2f overtook them, quoting the pages at their lines.

The predicates, each run on the tree (it must hold) and on broken copies (it must refuse them; the base pages too where the base
b0d85054 is in the object store):

- each changed ledger citation is directly preceded by its quotation and the cited lines carry those words at HEAD; the old claim
  and the old citations are gone; the pre-W4 words stand at [P11:89-92] on 1c6d56f5 and not at those lines now;
- every owner-file citation of the three pages names a line that carries the words it cites (681, 709, 839) and none names
  680, 708 or 838; a quotation directly before one is on the cited line itself;
- each annex note is dated, names 786aed2f, sits in its own section, and each quotation in it is on the cited lines now and at
  786aed2f (the rewrite it names); the ledger and the annex keep their base line counts (other records cite both by line);
- no em or en dash in the five pages or this module.

These are predicates on record text: they establish no electrical or thermal property, change no figure, class or verdict, close
nothing and accept nothing.
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need, Skip  # noqa: E402

LED = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
REC7 = "v2/docs/records/l4e7/"
PAGES = ("L4E7-P0SOL.md", "SUPPLIER-P1-1-P0SOL.md", "B2-PRESENCE.md")
P11 = REC7 + "SUPPLIER-P1-1-P0SOL.md"
B2 = REC7 + "B2-PRESENCE.md"
OWN = "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md"
T10R = "v2/docs/records/l9t5/T10-ROUND5.md"
BASE = "b0d85054700af7abe19adef467795ee732a5e0b1"   # fnd/int31tests, this branch's base
PRE_W4 = "1c6d56f5c4208349d382ecdb5c34ffaa4bb0037e"   # the ledger's tip read, where [P11:89-92] was written
W4 = "786aed2fb32e45e1fba04a516e04c8eff8e89c3a"       # W4's rewrite of record l4e7's pages
DASHES = (chr(0x2013), chr(0x2014))
_C = {}

# (quotation on the ledger, the citation that follows it, file, first line, last line): read at HEAD
LED_CITES = [
    ("ADDRESSED IN DRAFTS, PROVISIONAL, not completed", "[P11:119-126]", P11, 119, 126),
    ("measurements, NOT an acceptance", "[T10R:153]", T10R, 153, 153),
    ("admits any revision", "[T10R:224]", T10R, 224, 224),
]
LED_PASSAGE = (P11, 119, 126, ("Independent of E-1", "D-16's correction (U5's input sense", "not completed"))
LED_KEPT = ("that would admit any revision", T10R, 51, 54)   # the claim [T10R:51-54] still carries, in its own words
PRE_W4_WORDS = ("Completed independently of E-1", P11, 89, 92)
LED_GONE = ("completed independently: D-16's correction and its rows ([P11:89-92])", "[T10:638]",
            "\"admits any revision\" shortcut would have admitted it ([T10R:51-54])")
LED_MARK = "the pre-W4 reading, \"Completed independently of E-1\", stood at [P11:89-92] on `1c6d56f5`"

# the owner file's lines the pages cite, with the words each carries (after part 26's row at line 26 moved them by one)
OWN_WORDS = {681: "Supplier item S1 must carry that engineering problem",
             709: "which stable outputs can be completed independently",
             839: "mark B2 unselected/withdrawn as drafted"}
OWN_COUNTS = {681: 6, 709: 1, 839: 2}
OWN_OLD = (680, 708, 838)
OWN_CITE = re.compile(r"OWNER-INSTRUCTION-2026-10-05\.md:(\d+)`")

# (section heading, its end, the note's head, [(quotation, citation, file, line)])
ANX_NOTES = [
    ("### 6.4 The lower-source back-feed", "\n### 6.5",
     "Dated note, 6 October 2026 (set 31's Q-40): W4's rewrite of record l4e7's pages at `786aed2f` overtook this sentence:",
     [("P1-1's S1 row (b) is the later validation of that computation", "[B2:185]", B2, 185),
      ("S1's added row (b) is the later validation of that computation", "[P11:63]", P11, 63)]),
    ("## 8. What this amendment leaves to other files", None,
     "dated note, 6 October 2026 (set 31's Q-40): W4's rewrite of record l4e7's pages at `786aed2f` overtook this pointer:",
     [("It is REMAINING ENGINEERING inside E-1", "[P11:60]", P11, 60),
      ("REMAINING ENGINEERING inside E-1", "[B2:184]", B2, 184)]),
]


def _norm(s):
    return " ".join(s.split())


def _read(rel):
    if rel not in _C:
        _C[rel] = open(need(os.path.join(ROOT, rel), "a file this module reads"), encoding="utf-8").read()
    return _C[rel]


def _git_show(commit, rel):
    """The file at a commit, or None when this host has no git or not that commit."""
    try:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    except OSError:
        return None
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def _seg(text, a, b):
    ls = text.split("\n")
    return _norm(" ".join(ls[a - 1:b])) if 1 <= a <= b <= len(ls) else ""


def _quoted_cite(text, q, c, gap=60):
    """The quotation q directly followed (within a short gap, no other quotation or bracket) by the citation c."""
    return re.search(re.escape('"%s"' % q) + r'[^"\[\]]{0,%d}?' % gap + re.escape(c), _norm(text)) is not None


# ---- the predicates (each returns its failures; empty means it holds)

def ledger_fails(text):
    fails = []
    for q, c, rel, a, b in LED_CITES:
        if not _quoted_cite(text, q, c):
            fails.append("%r is not followed by %s on the ledger" % (q, c))
        if _norm(q) not in _seg(_read(rel), a, b):
            fails.append("%s does not read %r" % (c, q))
    rel, a, b, words = LED_PASSAGE
    for w in words:
        if _norm(w) not in _seg(_read(rel), a, b):
            fails.append("the restated passage %s:%d-%d lacks %r" % (rel, a, b, w))
    w, rel, a, b = LED_KEPT
    if "[T10R:51-54]" not in text or _norm(w) not in _seg(_read(rel), a, b):
        fails.append("[T10R:51-54] no longer carries its claim")
    for g in LED_GONE:
        if _norm(g) in _norm(text):
            fails.append("the old text is still on the ledger: %r" % g[:60])
    if _norm(LED_MARK) not in _norm(text):
        fails.append("the pre-W4 reading is not kept and marked")
    if text.count("[P11:89-92]") != 2:
        fails.append("[P11:89-92] is on the ledger %d times, not twice (the citation form and the marked line)" % text.count("[P11:89-92]"))
    head = text.split("| Alias | File |", 1)[0]
    if "on set 31's Q-40, 6 October 2026, HO-F's line is restated to W4's passage, [P11:119-126]" not in head:
        fails.append("the citation form does not say the line was restated")
    return fails


def pre_w4_fails():
    """The pre-W4 words stood at [P11:89-92] on 1c6d56f5 and are not at those lines now (None: the commit is not here)."""
    w, rel, a, b = PRE_W4_WORDS
    then = _git_show(PRE_W4, rel)
    if then is None:
        return None
    fails = []
    if _norm(w) not in _seg(then, a, b):
        fails.append("%r was not at %s:%d-%d on %s" % (w, rel, a, b, PRE_W4[:8]))
    if _norm(w) in _seg(_read(rel), a, b):
        fails.append("%r is still at %s:%d-%d: nothing was rewritten" % (w, rel, a, b))
    return fails


def pages_fails(texts, own):
    fails, counts = [], {}
    ol = own.split("\n")
    for nm in PAGES:
        raw = texts[nm]
        for m in OWN_CITE.finditer(raw):
            n = int(m.group(1))
            counts[n] = counts.get(n, 0) + 1
            if n in OWN_OLD:
                fails.append("%s still cites the owner file's line %d" % (nm, n))
                continue
            if n not in OWN_WORDS or OWN_WORDS[n] not in ol[n - 1]:
                fails.append("%s cites the owner file's line %d, which does not carry its words" % (nm, n))
                continue
            pre = raw[max(0, m.start() - 400):m.start()]
            q = re.search(r'"([^"]{12,})"[,.]?\s*\(?`?(?:v2/docs/handover/)?$', pre)
            if q and _norm(q.group(1)) not in _norm(ol[n - 1]):
                fails.append("%s: %r is not on the owner file's line %d" % (nm, q.group(1)[:50], n))
    if counts != OWN_COUNTS:
        fails.append("the pages cite the owner file %s, not %s" % (sorted(counts.items()), sorted(OWN_COUNTS.items())))
    return fails


def annex_fails(text, w4_pages=None):
    fails = []
    for head, stop, note, cites in ANX_NOTES:
        i = text.find(head)
        if i < 0:
            fails.append("the annex has no %r" % head); continue
        j = text.find(stop, i) if stop else len(text)
        sec = text[i:j if j >= 0 else len(text)]
        if _norm(note) not in _norm(sec):
            fails.append("%s lacks its dated note naming 786aed2f" % head[:30])
        for q, c, rel, n in cites:
            if not _quoted_cite(sec, q, c, gap=10):
                fails.append("%s: %r is not followed by %s" % (head[:12], q[:40], c))
            if _norm(q) not in _seg(_read(rel), n, n):
                fails.append("%s does not read %r now" % (c, q[:40]))
            if w4_pages is not None and _norm(q) not in _seg(w4_pages[rel], n, n):
                fails.append("%s did not read %r at 786aed2f" % (c, q[:40]))
    return fails


def counts_fails(led, anx):
    """The ledger and the annex keep their base line counts (None: the base is not in the object store)."""
    bl, ba = _git_show(BASE, LED), _git_show(BASE, ANX)
    if bl is None or ba is None:
        return None
    fails = []
    # Restated by W41 (6 October 2026; basis: W38's F1): the coordinator's merge d5d9c252 brought main's adoption 836f711b, which put
    # three lines into the ledger (746 to 749 on main), so the ledger is its base plus those three; the annex keeps its count.
    # Restated by the coordinator (7 October 2026; basis: set 33's chain applied L4K-4, L4S-3 and ROWB-1 to the ledger under the
    # coordinator's APPLY rulings, 750 to 761 lines at C1 9df37826): plus those eleven.
    if led.count("\n") != bl.count("\n") + 3 + 11:
        fails.append("the ledger has %d lines, the base %d plus 836f711b's three and set 33's eleven" % (led.count("\n"), bl.count("\n")))
    if anx.count("\n") != ba.count("\n"):
        fails.append("the annex has %d lines, the base %d" % (anx.count("\n"), ba.count("\n")))
    return fails


def _pages():
    return {nm: _read(REC7 + nm) for nm in PAGES}


def _w4_pages():
    got = {rel: _git_show(W4, rel) for rel in (P11, B2)}
    return None if any(v is None for v in got.values()) else got


# ---- the tests

def t_the_ledgers_changed_citations_read_their_words():
    f = ledger_fails(_read(LED))
    assert not f, f[:5]


def t_the_pre_w4_words_stood_at_the_old_lines_and_were_rewritten():
    f = pre_w4_fails()
    if f is None:
        raise Skip("%s is not in this object store" % PRE_W4[:8])
    assert not f, f


def t_the_pages_owner_citations_name_the_lines_with_their_words():
    f = pages_fails(_pages(), _read(OWN))
    assert not f, f[:5]


def t_the_annex_notes_are_dated_and_read_w4s_lines():
    f = annex_fails(_read(ANX), _w4_pages())
    assert not f, f[:5]


def t_the_ledger_and_the_annex_keep_their_lines():
    f = counts_fails(_read(LED), _read(ANX))
    if f is None:
        raise Skip("the base %s is not in this object store" % BASE[:8])
    assert not f, f


def t_no_long_dash():
    for rel in [LED, ANX] + [REC7 + nm for nm in PAGES] + [os.path.relpath(os.path.abspath(__file__), ROOT)]:
        t = _read(rel)
        for d in DASHES:
            assert d not in t, "%s carries U+%04X" % (rel, ord(d))


def t_the_predicates_refuse_broken_pages():
    """Each predicate refuses a broken copy; the base pages (when in the object store) fail them as the old defect."""
    led, anx, pages, own = _read(LED), _read(ANX), _pages(), _read(OWN)
    p0 = dict(pages)
    p0["L4E7-P0SOL.md"] = p0["L4E7-P0SOL.md"].replace("05.md:839`", "05.md:838`", 1)
    p11 = dict(pages)
    p11["SUPPLIER-P1-1-P0SOL.md"] = p11["SUPPLIER-P1-1-P0SOL.md"].replace("05.md:709`", "05.md:710`", 1)
    pq = dict(pages)
    pq["L4E7-P0SOL.md"] = pq["L4E7-P0SOL.md"].replace("\"Supplier item S1 must carry that engineering",
                                                      "\"Supplier item S1 must carry an engineering", 1)
    assert pq["L4E7-P0SOL.md"] != pages["L4E7-P0SOL.md"], "the quotation mutation changed nothing"
    broken = [
        ("ledger", lambda: ledger_fails(led.replace("[T10R:153]", "[T10:638]", 1))),
        ("ledger", lambda: ledger_fails(led.replace("([T10R:224]) would", "would", 1))),
        ("ledger", lambda: ledger_fails(led.replace("\"ADDRESSED IN DRAFTS, PROVISIONAL, not completed\"", "completed independently", 1))),
        ("ledger", lambda: ledger_fails(led.replace(", stood at [P11:89-92] on `1c6d56f5`", "", 1))),
        ("pages", lambda: pages_fails(p0, own)),
        ("pages", lambda: pages_fails(p11, own)),
        ("pages", lambda: pages_fails(pq, own)),
        ("pages", lambda: pages_fails(pages, "\n" + own)),
        ("annex", lambda: annex_fails(anx.replace("at `786aed2f` overtook this sentence", "overtook this sentence", 1))),
        ("annex", lambda: annex_fails(anx.replace("\" [P11:60]", "\" [P11:61]", 1))),
        ("annex", lambda: annex_fails(anx.replace("is the later validation of that computation\" [B2:185]",
                                                  "is the validation of that computation\" [B2:185]", 1))),
    ]
    for name, f in broken:
        assert f(), "the %s predicate accepted a broken copy" % name
    bl, ba = _git_show(BASE, LED), _git_show(BASE, ANX)
    bp = {nm: _git_show(BASE, REC7 + nm) for nm in PAGES}
    if bl is None or ba is None or any(v is None for v in bp.values()):
        raise Skip("the base %s is not in this object store (the synthetic copies above were refused)" % BASE[:8])
    assert ledger_fails(bl), "the base ledger passes the ledger predicate"
    assert pages_fails(bp, own), "the base pages pass the owner-citation predicate"
    assert annex_fails(ba), "the base annex passes the notes predicate"
    assert counts_fails(led + "\n", anx), "a moved line count is not refused"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
