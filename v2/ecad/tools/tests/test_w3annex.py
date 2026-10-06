"""W3 (MESHSAT-1357, 6 October 2026): the supplier annex's amendment and TP-E11-29's re-quotation, held as predicates on their text.

The two pages: v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md (sections 6 to 8 added; sections 1 to 5 edited inside
their lines only) and v2/docs/test-procedures/TP-E11-29.md (the quotes of R-159's Acceptance and 5d's Specimen re-taken on set 31's
restatement; the status, section 2's first consequence and section 8's first condition restated; section 9's note on R17's target).
Written for the NEXT set: the branch is not in set 30's freeze, so the coordinator re-pins and regenerates what reads these pages.

The predicates, each run on the tree (it must hold) and on broken copies (it must refuse them, the old defect included where the
base revision 53a68c7c is in the object store):

- every [ALIAS:N] or [ALIAS:N-M] citation of the annex's sections 6 to 8 names an alias of its table, an existing file and lines
  that exist; every quotation followed by its citation is found, whitespace aside, in the cited lines, and every other citation
  holds the anchor text this module names for it;
- the citations of files on other branches (Slot L's DESK-gate draft, Slot M's ledger amendment) read what they say where that
  commit is in the object store;
- sections 1 to 5 keep their lines: each base line's words appear, in order, in the same line now, and the texts other records
  quote by line are where they were;
- R17's design target: record l4e11 prints one computed figure at two roundings (the generator's fmt calls on z17_t, parsed with
  ast), both pages print both with the derivation, and neither prints it to more places than the record;
- E11-37 has its row in the annex's form (class, open case, the bound from the printed limit, Q-TI-17 UNSENT, the receiving company's
  task and acceptance), each figure found on the record line the section cites;
- the lower-source back-feed is placed as the ledger's HO-F places it (remaining engineering inside E-1; S1's row (b) its later
  validation, not a substitute), with the owner's part 23 quoted;
- the set 30 note is dated and carries the placeholder __INTEGRATED__ for the coordinator;
- TP-E11-29's quotes all hold against their sources (the procedures' own verifier), R-159's cell is E11-29's row word for word as
  the page now says, and the procedure stays NOT EXECUTABLE;
- no em or en dash in the two pages or this module.

These are predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import ast
import difflib
import importlib.util
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
TP29 = "v2/docs/test-procedures/TP-E11-29.md"
E11 = "v2/docs/records/l4e11/l4e11_power.out"
E11PY = "v2/docs/records/l4e11/l4e11_power.py"
BASE = "53a68c7ce8a8b964d8d3905b4a769b50db096040"     # set 30's integration commit 2c, this branch's base
DGA = ("249e9e4785a170238c69316742a422250908cd1f", "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md")
REM_M = ("99bbc0c6059aff0bf780f2cd6b0b102092f54f37", "v2/docs/records/l4close/REMAINING-ENGINEERING.md")
CITE = re.compile(r"\[([A-Z][A-Z0-9]*):(\d+)(?:-(\d+))?\]")
QCITE = re.compile(r"\"([^\"]{4,600}?)\"[^\"\[\]]{0,40}?\[([A-Z][A-Z0-9]*):(\d+)(?:-(\d+))?\]")  # a short gap allowed
DASHES = (chr(0x2013), chr(0x2014))
_C = {}


def _read(rel):
    if rel not in _C:
        p = need(os.path.join(ROOT, rel), "a file this module reads")
        _C[rel] = open(p, encoding="utf-8").read()
    return _C[rel]


def _norm(s):
    return " ".join(s.split())


def _git_show(commit, rel):
    """The file at a commit, or None when this host has no git or not that commit (a code-only checkout, a box clone)."""
    try:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (commit, rel)], capture_output=True)
    except OSError:
        return None
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def _amendment(text):
    """The annex's sections 6 to 8 (from the section 6 heading to the end)."""
    i = text.find("\n## 6. Amendment of 6 October 2026")
    return text[i:] if i >= 0 else ""


def _section(text, head, stop="\n## "):
    i = text.find(head)
    if i < 0:
        return ""
    j = text.find(stop, i + len(head))
    return text[i:] if j < 0 else text[i:j]


def _aliases(text):
    """The alias table of section 6: alias -> path."""
    out = {}
    for m in re.finditer(r"^\| ([A-Z][A-Z0-9]*) \| `([^`]+)`", _amendment(text), re.M):
        out[m.group(1)] = m.group(2)
    return out


def _lines(rel, a, b):
    ls = _read(rel).split("\n")
    if a < 1 or b > len(ls) or a > b:
        return None
    return _norm(" ".join(ls[a - 1:b]))


# ---- the predicates (each returns its failures; empty means it holds)

def cite_fails(text):
    """Every citation of sections 6 to 8 names a table alias, an existing file and existing lines."""
    al, fails = _aliases(text), []
    body = _amendment(text)
    if not body:
        return ["the annex has no section 6 (the amendment of 6 October 2026)"]
    for m in CITE.finditer(body):
        a, n, k = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        if a not in al:
            fails.append("%s: alias %s is not in the table" % (m.group(0), a))
            continue
        p = os.path.join(ROOT, al[a])
        if not os.path.isfile(p):
            fails.append("%s: %s is not in the tree" % (m.group(0), al[a]))
            continue
        if (_read(al[a]) if a != "ANX" else text).count("\n") + 1 < k or n > k or n < 1:
            fails.append("%s: lines %d to %d are not in %s" % (m.group(0), n, k, al[a]))
    return fails


def quote_fails(text):
    """Every quotation followed directly by its citation is found in the cited lines (whitespace aside)."""
    al, fails = _aliases(text), []
    body = _norm(_amendment(text))
    for m in QCITE.finditer(body):
        q, a, n, k = m.group(1), m.group(2), int(m.group(3)), int(m.group(4) or m.group(3))
        if a not in al or not os.path.isfile(os.path.join(ROOT, al[a])):
            fails.append("%r: its citation %s:%d does not resolve" % (q[:50], a, n))
            continue
        src = text if a == "ANX" else _read(al[a])
        ls = src.split("\n")
        seg = _norm(" ".join(ls[n - 1:k])) if k <= len(ls) else ""
        if _norm(q) not in seg:
            fails.append("%r is not in %s lines %d to %d" % (q[:60], al[a], n, k))
    return fails


ANCHORS = {  # every citation of sections 6 to 8 that no quotation checks: the text its cited lines must hold
    # five keys moved with W23's re-cite of the annex (fnd/int31cite 1b2d5123; the ledger re-cited at 92b754c5, W4's rewrite of
    # record l4e7's pages at 786aed2f): REM 520 to 552 to 549 to 581, P11 44 to 72, 110 to 144, 120 to 123 to 154 to 160, whose words W4
    # rewrote ("(b) the panel withdrawn" is now "(b) the lower-source back-feed"); every range read at this tree by W25
    "[REM:549-581]": ("### HO-H: E11-29", "### HO-K: U-04"),
    "[ANX:73]": ("E11-37's own row is section 7",),
    "[ANX:87]": ("D-06 in this section is the foundation decision of the pack",),
    "[ANX:93]": ("D-06's pocket (58 x 160 x 48 mm under B16's overhang)",),
    "[ANX:96]": ("D-06's pocket",),
    "[ANX:105]": ("R17 at most 0.294 K/W", "0.29 K/W"),
    "[ANX:113]": ("Asked of the owner: nothing.",),
    # four keys restated by W42 (set 32, 6 October 2026; basis: W34's edit of l4e11_power.py on fnd/w34pdftext moved every cited
    # line by 62, read from aed4bd23 to 886704ea with difflib's equal blocks; the anchors unchanged, the annex re-cited to match)
    "[E11PY:6029]": ('S["z17_t"] = solve(',),
    "[E11PY:6182]": ('fmt(S["z17_t"], 3)',),
    "[E11PY:6375]": ('fmt(S["z17_t"], 3)',),
    "[E11PY:6444]": ('fmt(R["S26"]["z17_t"], 2)',),
    "[TP29:130-133]": ('col="Specimen"', "with the three gates brought out apart"),
    "[TP29:207-208]": ("R17's coupling at most 0.294",),
    "[TP29:613-666]": ('row="R-159" col="Acceptance"', "L4-E11's E11-29 row, word for word"),
    "[TP29:713]": ("R17's coupling at most 0.29 K/W",),
    "[TP29:718-724]": ("(1) The limits: set 31 restated R-159's cell", "set, not before."),
    "[TP29:738]": ("| R17 | the largest coupling plus U | 1 K/W |",),
    "[TP29:785]": ("| R17's coupling | 0.294 K/W | 0.353 K/W | 119.9 % |",),
    "[TP29:839-840]": ("If TP-E11-37's answer is negative:", "with two gates against the fallback line"),
    "[SET31:111-112]": ("D-06 the decision against D-06 the defect",),
    "[SET31:120-122]": ("45.88 K/W outside PC-05's stated places", "U-04's choice row"),
    "[P11:72]": ("every part within its makers' absolute maximum ratings during the fault",),
    "[P11:144]": ("**S1, a stiff 36 V source stepping onto the port with the guard on",),
    "[P11:154-160]": ("(b) the lower-source back-feed", "Q12's body-diode current inside its pulsed rating"),
    "[L4E9:1022]": ("| D-06 | the vehicle entry's interconnect",),
    "[L4E9:1380]": ("| D-06 | RESOLVED |",),
    "[E11:508]": ("E11-37 | EVIDENCE", "at -20, 25 and 70 C"),
    "[E11:944]": ("RBATDRV_ON at most 6 kOhm, RBATDRV_OFF at most 2.1 kOhm",),
    "[E11:1110-1116]": ("19d. E11-37 REBOUND TO THE THREE-DEVICE NETWORK",),
    "[E11:1112]": ("42.48 us on (-15 V), 51.66 us on near 0 V, 18.08 us off (MAKER, INFERRED)",),
    "[E11:1450-1451]": ("Q49 moves at most 192 nC", "sinks at most 3.83 mA"),
    "[TIQ:74-78]": ("**Q-TI-17 (E11-37, BQ25730).**",),
    "[TIQ:96-110]": ("Q-TI-17 extended to three devices", "(d) Record section 19h"),
    "[TIQ:100-102]": ("QG(tot) at most 192 nC at -10 V for the three (64 nC each)",),
    "[TIQ:112-125]": ("Q-TI-17 (e) and (f)", "**Q-TI-17 (f) (E11-37, BQ25730).**"),
    "[REG:279]": ("| R-183 | EVIDENCE |",),
    "[E11P:1673-1690]": ("#### Block E11-37: BATDRV with the three", "**Re-test when:**"),
    "[E11P:1680]": ("at -20, 25 and 70 C ambient",),
    "[E11P:1683-1687]": ("each FET's drain current read", "each drain current within 2 %"),
    "[E11P:1687]": ("probes with at least 100 MHz bandwidth",),
}


def anchor_fails(text):
    """Every citation no quotation checks holds its anchor text in the cited lines, and has an anchor here."""
    al, fails = _aliases(text), []
    body = _norm(_amendment(text))
    quoted = set("[%s:%s%s]" % (q[1], q[2], ("-" + q[3]) if q[3] else "") for q in QCITE.findall(body))
    for m in CITE.finditer(body):
        c = m.group(0)
        if c in quoted:
            continue
        if c not in ANCHORS:
            fails.append("%s is checked by neither a quotation nor an anchor" % c)
            continue
        a, n, k = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
        if a not in al:
            fails.append("%s: alias %s is not in the table" % (c, a))
            continue
        ls = (text if a == "ANX" else _read(al[a])).split("\n")
        seg = _norm(" ".join(ls[n - 1:k])) if k <= len(ls) else ""
        for anc in ANCHORS[c]:
            if _norm(anc) not in seg:
                fails.append("%s does not hold %r" % (c, anc[:50]))
    return fails


def r17_fails(annex, tp):
    """R17's design target: both prints and the derivation on both pages; no print with more places than the record's."""
    fails = []
    s62 = _section(annex, "### 6.2 R17's design target", "\n### ")
    note = _section(tp, "**R17's design target: one computed figure at two roundings**", "\n\n")
    for name, t in (("the annex's 6.2", s62), ("TP-E11-29's note", note)):
        if not t:
            fails.append("%s is missing" % name)
            continue
        flat = _norm(t)
        for need_ in ("0.294", "0.29 K/W", "0.294 + 2 x 0.353 = 1.000 K/W", "1 K/W", "SESSION"):
            if need_ not in flat:
                fails.append("%s lacks %r" % (name, need_))
        if "two targets" not in flat:
            fails.append("%s does not say the two prints are not two targets" % name)
    line105 = annex.split("\n")[104] if annex.count("\n") > 104 else ""
    if "0.29 K/W" not in line105 or "section 6.2" not in line105:
        fails.append("the annex's line 105 does not name the row's two-place print beside 0.294 K/W")
    for name, t in (("the annex", annex), ("TP-E11-29", tp)):
        if re.search(r"0\.29[0-9]{2,}", t):
            fails.append("%s prints R17's target to more places than the record" % name)
    return fails


E1137_FACTS = [  # (text the annex's section 7 states, the record line it cites, the text found there)
    ("7.08 nF typical at -15 V", (E11, 1111, 1111), "Ciss 7.08 nF typical at -15 V"),
    ("about 8.61 nF near 0 V", (E11, 1111, 1111), "about 8.61 nF near 0 V"),
    ("192 nC for the three", ("v2/docs/records/l4e11/clarification/TI-QUESTIONS.md", 100, 102), "QG(tot) at most 192 nC at -10 V for the three"),
    ("RBATDRV_ON at most 6 kOhm and RBATDRV_OFF at most 2.1 kOhm", (E11, 944, 944), "RBATDRV_ON at most 6 kOhm, RBATDRV_OFF at most 2.1 kOhm"),
    ("42.48 us on", (E11, 1112, 1112), "42.48 us on (-15 V)"),
    ("51.66 us on near 0 V", (E11, 1112, 1112), "51.66 us on near 0 V"),
    ("18.08 us off", (E11, 1112, 1112), "18.08 us off"),
    ("Q49 moves at most 192 nC", (E11, 1450, 1451), "Q49 moves at most 192 nC"),
    ("3.83 mA", (E11, 1450, 1451), "sinks at most 3.83 mA"),
    ("its bar 20.39 K/W measured on the coupon, Q42 removed", (E11, 1462, 1463), "its bar 20.39 K/W measured on the coupon, Q42 removed"),
    ("at -20, 25 and 70 C", (E11, 508, 508), "at -20, 25 and 70 C"),
]


def e1137_fails(annex):
    """E11-37's row in the annex's form, consistent with the ledger's HO-L."""
    s7 = _section(annex, "## 7. E11-37")
    if not s7:
        return ["the annex has no section 7 for E11-37"]
    flat, fails = _norm(s7), []
    head = s7.split("\n")[0]
    if "REMAINING ENGINEERING" not in head or "P0-8" not in head:
        fails.append("section 7's heading does not carry the class REMAINING ENGINEERING and the P0 row")
    for need_ in ("**Class.**", "**The open case.**", "**The bound from the printed limit", "**The vendor question, drafted and UNSENT.**",
                  "**The receiving company's task", "**On a negative answer", "**Outputs kept PROVISIONAL or OPEN",
                  "Q-TI-17", "UNSENT", "NOT a demonstrated failure", "not one of the P0 list's ARCH rows", "TYPICAL", "(MAKER, INFERRED)",
                  "E11-37 STAYS OPEN", "\"E11-37 OPEN (TI or the bench)\""):
        if need_ not in flat:
            fails.append("section 7 lacks %r" % need_)
    for said, (rel, n, k), there in E1137_FACTS:
        if said not in flat:
            fails.append("section 7 does not state %r" % said)
        elif there not in (_lines(rel, n, k) or ""):
            fails.append("%r is not on %s lines %d to %d" % (there, rel, n, k))
    sec5 = _section(annex, "## 5. What this annex asks", "\n## 6.")
    if "E11-37" not in sec5:
        fails.append("section 5's hand-over list does not name E11-37")
    return fails


def backfeed_fails(annex):
    """The lower-source back-feed placed as the ledger's HO-F places it."""
    s = _norm(_section(annex, "### 6.4 The lower-source back-feed", "\n### "))
    if not s:
        return ["the annex has no section 6.4"]
    fails = []
    for need_ in ("REMAINING ENGINEERING inside E-1", "not a substitute for it", "as part of E-1's correction",
                  "Supplier item S1 must carry that engineering problem, rather than presenting it solely as an unperformed validation test.",
                  "A planned measurement alone does not establish that the selected protection works.",
                  "D-10's E-1 retains F1-F4 and the lower-source back-feed case.", "sets no limit"):
        if need_ not in s:
            fails.append("section 6.4 lacks %r" % need_)
    return fails


def note_fails(annex, tp):
    """The set 30 note: dated, the placeholder for the coordinator, and both pages saying they are for the next set."""
    fails = []
    s61 = _section(annex, "### 6.1 The set 30 note", "\n### ")
    if "`__INTEGRATED__`" not in s61 or "(dated 6 October 2026)" not in s61:
        fails.append("section 6.1 lacks the dated note or the __INTEGRATED__ placeholder")
    if "NOT merged into set 30's freeze" not in annex.split("\n")[9]:
        fails.append("the annex's header (line 10) does not say it is for the next set")
    head = tp[:tp.find("## 1. Purpose")]
    if "NOT merged into set 30's freeze" not in _norm(head):
        fails.append("TP-E11-29's header does not say it is for the next set")
    return fails


ANX_KEPT = [  # (first line, last line, text other records quote by this line)
    (16, 16, "A desk-fixable defect is never parked here."),
    (43, 43, "demonstrates that THAT arrangement fails under those conditions, nothing more"),
    (81, 81, "D-06's pocket"),
    (101, 101, "(a QUALIFICATION, kept apart from the architecture blockers)"),
    (103, 104, "written and NOT EXECUTABLE until L4-E9 restates R-159 and a supplier agrees in writing to the fixture requirement"),
    (105, 105, "Zw at most 37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm"),
    (108, 109, "lower-resistance FETs or a fourth, a design change inside UDC-1, not an architecture change"),
    (113, 113, "Asked of the owner: nothing."),
    (121, 121, "a desk-solvable defect is never moved into this annex"),
]


def kept_fails(annex, base=None):
    """Sections 1 to 5 keep their lines (and, given the base text, every base line's words in order on the same line)."""
    ls, fails = annex.split("\n"), []
    for a, b, q in ANX_KEPT:
        if q not in _norm(" ".join(ls[a - 1:b])):
            fails.append("%r is no longer at the annex's lines %d to %d" % (q[:50], a, b))
    if len(ls) < 123 or not ls[122].startswith("## 6. Amendment"):
        fails.append("section 6 does not begin right after the 121 lines of sections 1 to 5")
    if base is not None:
        for i, old in enumerate(base.split("\n")[:121]):
            ops = difflib.SequenceMatcher(None, old, ls[i], autojunk=False).get_opcodes()
            if any(tag not in ("equal", "insert") for tag, *_r in ops):
                fails.append("line %d is not the base line with text inserted" % (i + 1))
    return fails


def _tp_check():
    if "tp" not in _C:
        p = need(os.path.join(ROOT, "v2", "docs", "test-procedures", "tp_check.py"), "the procedures' checker")
        sp = importlib.util.spec_from_file_location("tp_check_for_w3annex", p)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C["tp"] = m
    return _C["tp"]


def tp_fails(tp):
    """TP-E11-29: every quote holds, the two re-taken cells are quoted, R-159's cell is E11-29's row word for word as the page
    says, and the procedure stays NOT EXECUTABLE."""
    T = _tp_check()
    src = T.Sources(ROOT)
    tq, _n_table, _n_text, fails = T.verify_quotes(src, TP29, tp)
    fails = list(fails)
    for key in ((T.REG, "R-159", "Acceptance"), (T.ARCH, "E11-29 (R-159)", "Specimen")):
        if key not in tq:
            fails.append("TP-E11-29 does not quote %s" % (key,))
    reg, e1 = src.cell(T.REG, "R-159", "Acceptance")
    row, e2 = src.cell("v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md", "E11-29", "Acceptance")
    if e1 or e2 or not T.norm(reg).startswith("L4-E11's E11-29 row, word for word: " + T.norm(row)):
        fails.append("R-159's cell is not E11-29's row word for word, which section 8 now says")
    flat = _norm(tp)
    for need_ in ("**NOT EXECUTABLE.**", "a supplier's written agreement", "the two quotes above now carry the same acceptance",
                  "No supplier has agreed to the fixture of section 5"):
        if need_ not in flat:
            fails.append("TP-E11-29 lacks %r" % need_)
    if "The two quotes above differ" in flat or "predates rounds 13 and 14" in flat:
        fails.append("TP-E11-29 still states the cells before set 31's restatement")
    return fails


# ---- the tests

def _pages():
    return _read(ANX), _read(TP29)


def t_the_amendments_citations_resolve_and_their_quotes_are_found():
    annex, _ = _pages()
    assert not cite_fails(annex), cite_fails(annex)[:5]
    assert not quote_fails(annex), quote_fails(annex)[:5]
    assert not anchor_fails(annex), anchor_fails(annex)[:5]
    assert len(CITE.findall(_amendment(annex))) >= 100, "fewer citations than written"
    assert len(QCITE.findall(_norm(_amendment(annex)))) >= 25, "fewer checked quotations than written"


def t_the_other_branch_citations_read_what_they_say():
    expect = [(DGA, 258, "- A4.4 P0-8, E11-37"), (DGA, 261, "- A4.5 The lower-source back-feed"), (DGA, 316, "| K-06 |"),
              (DGA, 319, "| K-09 |"), (DGA, 322, "| K-12 |"), (DGA, 333, "| K-23 |"), (DGA, 311, "| K-01 |"), (DGA, 338, "| K-28 |"),
              (REM_M, 584, "### HO-L: E11-37"), (REM_M, 586, "- **Class, and why (SESSION, this ledger's reading).**"),
              (REM_M, 522, "- **The back-feed, this ledger's reading"), (REM_M, 720, "- **E. The lower-source back-feed's placement.**")]
    seen = 0
    for (commit, rel), n, start in expect:
        t = _git_show(commit, rel)
        if t is None:
            continue
        seen += 1
        assert t.split("\n")[n - 1].startswith(start), "%s:%s line %d does not start %r" % (commit[:8], rel, n, start)
    if not seen:
        raise Skip("neither other-branch commit is in this object store")


def t_sections_1_to_5_keep_their_lines():
    annex, _ = _pages()
    base = _git_show(BASE, ANX)
    assert not kept_fails(annex, base), kept_fails(annex, base)[:5]


def t_r17_is_one_computed_figure_printed_at_two_roundings():
    annex, tp = _pages()
    assert not r17_fails(annex, tp), r17_fails(annex, tp)
    e11 = _read(E11).split("\n")
    assert "R17's coupling at most 0.29 K/W" in e11[499] and "0.294" not in e11[499], "the row E11-29 no longer prints 0.29 K/W"
    for n in (1913, 1922, 1975):
        assert "0.294" in e11[n - 1], "line %d of the output no longer prints 0.294" % n
    # the generator prints the one solved figure at two precisions (parsed, not grepped)
    tree = ast.parse(_read(E11PY))
    places, solves = set(), 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "fmt" and len(node.args) == 2:
            if "z17_t" in ast.unparse(node.args[0]) and isinstance(node.args[1], ast.Constant):
                places.add(node.args[1].value)
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Subscript):
            if ast.unparse(node.targets[0]) == "S['z17_t']" and isinstance(node.value, ast.Call) \
                    and getattr(node.value.func, "id", "") == "solve":
                solves += 1
    assert places == {2, 3}, "the record prints z17_t at %s places" % sorted(places)
    assert solves == 1, "the target is solved %d times" % solves
    # the derivation on the printed figures: 0.294 + 2 x 0.353 within their rounding of 1 K/W
    assert abs(0.294 + 2 * 0.353 - 1.0) <= 0.0005 + 2 * 0.0005


def t_e1137_has_its_row_in_the_annexs_form():
    annex, _ = _pages()
    assert not e1137_fails(annex), e1137_fails(annex)


def t_the_back_feed_is_placed_as_the_ledger_places_it():
    annex, _ = _pages()
    assert not backfeed_fails(annex), backfeed_fails(annex)


def t_the_set_30_note_is_dated_and_carries_the_placeholder():
    annex, tp = _pages()
    assert not note_fails(annex, tp), note_fails(annex, tp)
    assert _amendment(annex).count("`__INTEGRATED__`") >= 2


def t_tp_e11_29_quotes_hold_and_it_stays_not_executable():
    _, tp = _pages()
    assert not tp_fails(tp), tp_fails(tp)[:5]


def t_no_long_dash_in_the_pages_or_this_module():
    for rel in (ANX, TP29, os.path.relpath(os.path.abspath(__file__), ROOT)):
        t = _read(rel)
        for d in DASHES:
            assert d not in t, "%s carries U+%04X" % (rel, ord(d))


def t_the_predicates_refuse_broken_pages():
    """Each predicate refuses a broken copy; on the base revision (when in the object store) the old pages fail them."""
    annex, tp = _pages()
    am = _amendment(annex)
    broken = [
        ("cite", cite_fails, (annex.replace("[E11:1459]", "[E11:99999]", 1),)),
        ("cite", cite_fails, (annex.replace("| TIQ | `v2/docs/records/l4e11/clarification/TI-QUESTIONS.md` |", "", 1),)),
        ("quote", quote_fails, (annex.replace("E11-37 STAYS OPEN: no printed figure", "E11-37 IS CLOSED: no printed figure", 1),)),
        ("anchor", anchor_fails, (annex.replace("[TP29:738]", "[TP29:742]", 1),)),
        ("anchor", anchor_fails, (annex.replace("[E11PY:6444]", "[E11PY:6443]", 1),)),
        ("r17", r17_fails, (annex.replace("0.294 + 2 x 0.353 = 1.000 K/W", "0.294 K/W", 1), tp)),
        ("r17", r17_fails, (annex, tp.replace("one figure, not two targets", "one figure", 1))),
        ("r17", r17_fails, (annex.replace("R17 at most 0.294 K/W, the pours", "R17 at most 0.2941 K/W, the pours", 1), tp)),
        ("e1137", e1137_fails, (annex.replace("drafted and UNSENT.**", "drafted and SENT.**", 1),)),
        ("e1137", e1137_fails, (annex.replace("7.08 nF typical at -15 V and about", "6.08 nF typical at -15 V and about", 1),)),
        ("e1137", e1137_fails, (annex.replace(", E11-37's statement or bench (section 7)", "", 1),)),
        ("backfeed", backfeed_fails, (re.sub(r"not a substitute\s+for it", "a substitute for it", annex, count=1),)),
        ("note", note_fails, (annex.replace("`__INTEGRATED__`", "`deadbeef`"), tp)),
        ("kept", kept_fails, (annex.replace("A desk-fixable defect is never parked here.", "", 1),)),
        ("kept", kept_fails, ("\n" + annex,)),
        ("tp", tp_fails, (tp.replace("at most 40.78 K/W steady with the band carrying 23.93 A", "at most 41.78 K/W steady with the band "
                                     "carrying 23.93 A", 1),)),
        ("tp", tp_fails, (tp.replace("the two quotes above now carry the same acceptance", "The two quotes above differ", 1),)),
    ]
    for name, pred, args in broken:
        assert args[0] != annex or (len(args) > 1 and args[1] != tp), "the %s mutation changed nothing" % name
        assert pred(*args), "the %s predicate accepted a broken copy" % name
    assert am and am in annex
    base_anx, base_tp = _git_show(BASE, ANX), _git_show(BASE, TP29)
    if base_anx is None or base_tp is None:
        raise Skip("the base revision %s is not in this object store (the synthetic copies above were refused)" % BASE[:8])
    for name, f in (("E11-37", lambda: e1137_fails(base_anx)), ("back-feed", lambda: backfeed_fails(base_anx)),
                    ("set 30 note", lambda: note_fails(base_anx, base_tp)), ("R17", lambda: r17_fails(base_anx, base_tp)),
                    ("TP-E11-29", lambda: tp_fails(base_tp))):
        assert f(), "the base revision passes the %s predicate: it would not have caught the old defect" % name
