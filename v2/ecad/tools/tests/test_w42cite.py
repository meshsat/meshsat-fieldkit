"""W42 (MESHSAT-1357, set 32, 6 October 2026): the line citations W34's generator edits moved, re-taken in the live pages, and the
supplier page's section 0e pointer, held as predicates on their text.

W34 (branch fnd/w34pdftext, aed4bd23 to 6dc69ad2) changed how 25 record generators read the makers' PDF text, which moved their lines.
The live pages that cite those generators by line and whose own citation rule re-cites moved lines are the supplier annex
(v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md, alias E11PY: record l4e11's generator) and the remaining-engineering
ledger (v2/docs/records/l4close/REMAINING-ENGINEERING.md, alias PAL: record l9t5's l9t5_paloop.py). The record of this re-take is
v2/docs/records/w42cite/README.md.

The predicates, each run on the tree (it must hold) and on broken copies (it must refuse them):

- every re-pointed citation names an alias of its page's table that is the generator, and its cited lines hold the words this
  module names for it; the PAL range is record l9t5's cap() from its def, inside the function (parsed with ast); the old citation
  string is gone from its page;
- each moved citation's old lines at aed4bd23 (the generators before W34's edit) are its new lines at the tip, byte for byte, where
  that commit is in the object store (a clone without it runs the other predicates only);
- each page's citation-form paragraph states set 32's re-cite inside the line that states set 31's, so no line of either page moved;
- the citations bound to a commit stay as written: the ledger's four line numbers inside cx46's quoted words stand on the ledger and
  in the filed check, and the next set's patch file still reads l4e11_power.py:7128 "at c4492dd3", where that line is E11-43's row
  (when c4492dd3 is in the object store);
- the section 0e pointer: apply_supplier_0e_pointer.py adds its one sentence inside section 0e's item 1 of a fixture page and keeps
  every line, refuses a second run, a page without section 0e, a page whose section 7 lacks the re-take step and old words outside
  section 0e; on the tree, a page with a section 0e carries the sentence there, and a page without one carries the re-take step the
  sentence points to;
- no em or en dash in the two pages, the record folder or this module.

These are predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import ast
import importlib.util
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

LED = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
CX46 = "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
NSS = "v2/docs/records/int30/NEXT-SET-SMALL-ITEMS.patch.md"
E11PY = "v2/docs/records/l4e11/l4e11_power.py"
PAL = "v2/docs/records/l9t5/l9t5_paloop.py"
SUPPLIER = "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md"
APPLY = "v2/docs/records/w42cite/apply_supplier_0e_pointer.py"
README = "v2/docs/records/w42cite/README.md"
GEN_BASE = "aed4bd234644c80fa494299b21099acf6d2454c1"     # W34's base: the 25 generators before W34's edit
C4492 = "c4492dd370c592e9899a8e526113958f4dc20554"        # the integration the next set's patch file reads its rows at
DASHES = (chr(0x2013), chr(0x2014))
_C = {}

# (page, alias, generator, old lines, new lines, words that stand on the new lines)
RECITED = [
    (ANX, "E11PY", E11PY, "5957", "6019", ("R17's design target: its line passes with twice its U",)),
    (ANX, "E11PY", E11PY, "5967", "6029", ('S["z17_t"] = solve(',)),
    (ANX, "E11PY", E11PY, "6120", "6182", ("R17's coupling target", 'fmt(S["z17_t"], 3)')),
    (ANX, "E11PY", E11PY, "6313", "6375", ('fmt(S["z17_t"], 3)',)),
    (ANX, "E11PY", E11PY, "6382", "6444", ('fmt(R["S26"]["z17_t"], 2)',)),
    (LED, "PAL", PAL, "186-255", "201-270", ("def cap(S, r_top=R_SET_TOP, r_bot=R_SET_BOT):", 'L["ios_printed"] = math.fsum(')),
]
# set 32's sentence in each page's citation-form paragraph, and the words of set 31's sentence it must share a line with
BINDING = {
    ANX: ("on set 32, 6 October 2026, the five citations under E11PY, which W34's edit of record l4e11's generator on "
          "`fnd/w34pdftext` moved by 62 lines, are re-cited to their lines there, the cited words unchanged",
          "on set 31, 6 October 2026, the citations under REM, B2, P11 and OWN"),
    LED: ("On set 32 (6 October 2026) the citation under PAL is re-cited to its lines on `fnd/w34pdftext`, where W34's edit of the "
          "generator moved them by 15 lines, the cited words unchanged",
          "On set 31 (6 October 2026) the citations under BRK, B2, P11 and P0SOL are re-cited"),
}
# cx46's own line numbers inside its quoted words, kept as quoted (bound to the candidate it read, 4d0ff8a2)
CX46_BOUND = ("l9t5_paloop.py:193-245", "v2/docs/records/l9t5/l9t5_paloop.py:198-205,224-245", "l9t5_t10.py:1176-1188",
              "l9t5_t10.py:1181-1191")
NSS_BOUND = "record l4e11's E11-43 (`v2/docs/records/l4e11/l4e11_power.py:7128`, `l4e11_power.out:514`, " \
            "`L4E11-SOURCE-ONLY-AND-ENTRY.md:733` at `c4492dd3`)"


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


def _norm(s):
    return re.sub(r"\s+", " ", s).strip()


def _aliases(text):
    return dict(re.findall(r"^\| ([A-Z][A-Z0-9]*) \| `(v2/[^`]+)`", text, re.M))


def _span(n):
    a, _, b = n.partition("-")
    return int(a), int(b or a)


def recite_fails(page, text, files=None):
    """Each re-pointed citation of the page stands once, resolves to its generator and reads its words; the old string is gone."""
    files, fails, al = files or {}, [], _aliases(text)
    for pg, alias, gen, old, new, words in RECITED:
        if pg != page:
            continue
        if al.get(alias) != gen:
            fails.append("%s: the alias %s does not name %s" % (page, alias, gen))
            continue
        if text.count("[%s:%s]" % (alias, new)) != 1:
            fails.append("%s: [%s:%s] does not stand once" % (page, alias, new))
        if "[%s:%s]" % (alias, old) in text:
            fails.append("%s: the old citation [%s:%s] is still there" % (page, alias, old))
        src = files.get(gen) or _read(gen)
        ls = src.split("\n")
        a, b = _span(new)
        if b > len(ls):
            fails.append("[%s:%s]: %s has %d lines" % (alias, new, gen, len(ls)))
            continue
        seg = _norm(" ".join(ls[a - 1:b]))
        for w in words:
            if _norm(w) not in seg:
                fails.append("[%s:%s]: %r is not on %s lines %d to %d" % (alias, new, w, gen, a, b))
        if alias == "PAL":
            caps = [f for f in ast.walk(ast.parse(src)) if isinstance(f, ast.FunctionDef) and f.name == "cap"]
            if len(caps) != 1 or caps[0].lineno != a or caps[0].end_lineno < b:
                fails.append("[PAL:%s] is not cap() from its def, inside the function" % new)
    return fails


def moved_fails(base_files, tip_files):
    """Each moved citation's old lines at the generators' base are its new lines at the tip, byte for byte."""
    fails = []
    for _pg, alias, gen, old, new, _w in RECITED:
        (a0, b0), (a1, b1) = _span(old), _span(new)
        bl, tl = base_files[gen].split("\n"), tip_files[gen].split("\n")
        if b0 - a0 != b1 - a1 or bl[a0 - 1:b0] != tl[a1 - 1:b1]:
            fails.append("[%s:%s] is not [%s:%s] of the base moved unchanged" % (alias, new, alias, old))
    return fails


def binding_fails(page, text):
    """Set 32's sentence stands once, on the line that states set 31's re-cite (no line added)."""
    new, old = BINDING[page]
    hit = [ln for ln in text.split("\n") if new in ln]
    if len(hit) != 1:
        return ["%s: set 32's sentence stands %d times" % (page, len(hit))]
    return [] if old in hit[0] else ["%s: set 32's sentence is not on the line of set 31's" % page]


def bound_fails(led, cx46, nss):
    """The citations bound to a commit stay as written."""
    fails = []
    for c in CX46_BOUND:
        if c not in led or c not in cx46:
            fails.append("%r is not kept as cx46 wrote it" % c)
    if nss.count(NSS_BOUND) != 1:
        fails.append("the patch file's E11-43 citation at c4492dd3 is not kept")
    return fails


def _apply_mod():
    if "apply" not in _C:
        sp = importlib.util.spec_from_file_location("w42_apply_0e", need(os.path.join(ROOT, APPLY), "the section 0e apply script"))
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C["apply"] = m
    return _C["apply"]


def _fixture(m, old_in_0e=True, retake=True):
    item1 = "1. **The makers' sheets held back by their terms.** A record fetches them with its own script;\n   %s" % m.OLD
    return ("# A page\n\n## 0. This revision\n\n### 0d. What we ask\n\nText.\n\n### 0e. How to reproduce set 30's figures\n\n"
            + (item1 if old_in_0e else "1. Fetch.") + "\n2. **A record's figures.** Run it.\n\n## 1. The product\n\n"
            + ("" if old_in_0e else m.OLD + "\n") + "## 7. How to check the claims\n\n2. Re-take: `python3 v2/docs/records/_lib/"
            + ("retake_pdf_text.py" if retake else "other.py") + " v2/docs/records/<record>`.\n\n## 8. Next\n")


def pointer_fails(m, page):
    """The tree's page: with a section 0e, the sentence stands there once; without one, section 7 carries the re-take step."""
    span = m._section(page, m.HEAD_0E)
    if span is not None:
        return [] if page.count(m.SENTENCE) == 1 and span[0] <= page.find(m.SENTENCE) < span[1] else \
            ["the page has a section 0e without the pointer (run %s)" % APPLY]
    s7 = m._section(page, m.HEAD_7)
    return [] if s7 is not None and m.RETAKE in page[s7[0]:s7[1]] else ["section 7 lacks the re-take step the pointer names"]


# ---- the tests

def t_the_re_pointed_citations_read_their_words_at_the_tip():
    for page in (ANX, LED):
        assert not recite_fails(page, _read(page)), recite_fails(page, _read(page))


def t_each_moved_citation_is_its_base_lines_unchanged():
    tip = {g: _read(g) for g in (E11PY, PAL)}
    base = {g: _git_show(GEN_BASE, g) for g in (E11PY, PAL)}
    if any(v is None for v in base.values()):
        return      # the base commit is not in this object store: the tip predicates above still hold the words
    assert not moved_fails(base, tip), moved_fails(base, tip)


def t_the_citation_forms_state_set_32_inside_their_lines():
    for page in (ANX, LED):
        assert not binding_fails(page, _read(page)), binding_fails(page, _read(page))


def t_citations_bound_to_a_commit_are_kept():
    assert not bound_fails(_read(LED), _read(CX46), _read(NSS)), bound_fails(_read(LED), _read(CX46), _read(NSS))
    old = _git_show(C4492, E11PY)
    if old is not None:
        assert old.split("\n")[7127].lstrip().startswith('("E11-43", "IMPLEMENTATION"'), "line 7128 at c4492dd3 is not E11-43"


def t_the_section_0e_pointer_applies_once_and_refuses_the_rest():
    m = _apply_mod()
    page = _fixture(m)
    new = m.apply(page)
    assert new.count(m.SENTENCE) == 1 and new.count("\n") == page.count("\n")
    s0e = m._section(new, m.HEAD_0E)
    assert s0e[0] <= new.find(m.SENTENCE) < s0e[1], "the sentence is not inside section 0e"
    assert new.find(m.SENTENCE) < new.find("2. **A record's figures.**"), "the sentence is not in item 1"
    for broken, why in ((new, "a second run"), (page.replace("### 0e. How to reproduce", "### 0f. How to see"), "no section 0e"),
                        (_fixture(m, retake=False), "no re-take step"), (_fixture(m, old_in_0e=False), "old words outside 0e")):
        try:
            m.apply(broken)
        except m.Refused:
            continue
        raise AssertionError("the apply script accepted %s" % why)
    for d in DASHES:
        assert d not in m.SENTENCE


def t_the_supplier_page_carries_the_pointer_or_its_target():
    m = _apply_mod()
    assert not pointer_fails(m, _read(SUPPLIER)), pointer_fails(m, _read(SUPPLIER))


def t_no_long_dash_in_the_pages_the_record_or_this_module():
    for rel in (ANX, LED, APPLY, README, os.path.relpath(os.path.abspath(__file__), ROOT)):
        t = _read(rel)
        for d in DASHES:
            assert d not in t, "%s carries U+%04X" % (rel, ord(d))


def t_the_predicates_refuse_broken_pages():
    anx, led = _read(ANX), _read(LED)
    m = _apply_mod()
    broken = [
        ("recite", lambda: recite_fails(ANX, anx.replace("[E11PY:6029]", "[E11PY:5967]", 1))),
        ("recite", lambda: recite_fails(ANX, anx.replace("[E11PY:6444]", "[E11PY:6443]", 1))),
        ("recite", lambda: recite_fails(LED, led.replace("[PAL:201-270]", "[PAL:186-255]", 1))),
        ("recite", lambda: recite_fails(LED, led.replace("[PAL:201-270]", "[PAL:202-270]", 1))),
        ("recite", lambda: recite_fails(ANX, anx.replace("| E11PY | `v2/docs/records/l4e11/l4e11_power.py` |", "", 1))),
        ("moved", lambda: moved_fails({E11PY: "\n".join(["x"] * 7000), PAL: _read(PAL)}, {E11PY: _read(E11PY), PAL: _read(PAL)})),
        ("binding", lambda: binding_fails(ANX, anx.replace(BINDING[ANX][0], "", 1))),
        ("binding", lambda: binding_fails(LED, led.replace(" " + BINDING[LED][0], "\n" + BINDING[LED][0], 1))),
        ("bound", lambda: bound_fails(led.replace("l9t5_t10.py:1176-1188", "l9t5_t10.py:1186-1198", 1), _read(CX46), _read(NSS))),
        ("bound", lambda: bound_fails(led, _read(CX46), _read(NSS).replace("l4e11_power.py:7128", "l4e11_power.py:7192", 1))),
        ("pointer", lambda: pointer_fails(m, _fixture(m))),
        ("pointer", lambda: pointer_fails(m, "# A page\n\n## 7. How to check the claims\n\nNothing.\n")),
    ]
    for name, f in broken:
        assert f(), "the %s predicate accepted a broken copy" % name
    assert not pointer_fails(m, m.apply(_fixture(m))), "the pointer predicate refuses the applied fixture"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
