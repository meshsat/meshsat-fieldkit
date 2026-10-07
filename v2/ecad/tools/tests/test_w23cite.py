"""W23 (MESHSAT-1357, 6 October 2026): set 31's citation re-take of the remaining-engineering ledger and the supplier annex, held
as predicates on their text.

The pages: v2/docs/records/l4close/REMAINING-ENGINEERING.md (the ledger) and
v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md (the annex). Set 31's merges moved the lines both pages cite:
record l8p's breaker page (W5's merge), record l4e7's three pages (W4's merge, which also rewrote the passages on the lower-source
back-feed and on what is completed independently), the owner file (part 26) and the ledger itself (HO-L and set 30's 2b). The
coordinator's decision N3 (queue, 05:28): a citation names the current line of the file it cites. This branch re-cites every
citation that no longer read its words, changes no figure, claim, class or verdict, and applies W20's two Q-21 rows (W20-13 and
W20-14 of records/int30/NEXT-SET-SMALL-ITEMS.patch.md) as written.

The predicates, each run on the tree (it must hold) and on broken copies (it must refuse them, the base page included when the base
commit a6e3a066 is in the object store):

- every citation this branch wrote resolves to an alias of its page's table, an existing file and lines that exist;
- a citation moved with its lines reads, at the cited lines, exactly the lines it cited at the commit that wrote it (when that
  commit is in the object store); a citation whose passage was rewritten reads the anchor text this module names for it, copied
  from the cited file;
- every quotation directly followed by a citation this branch wrote is found, whitespace aside, on the cited lines;
- no old citation string this branch replaced is left on its page, and the one the ledger keeps on purpose ([P11:89-92]: the
  passage it cited now reads otherwise) is still there once, named in the ledger's citation form;
- W20-13 and W20-14 stand once each with their old texts gone; the annex keeps its line count, the ledger gains W20-14's one line;
- no em or en dash in the two pages or this module.

These are predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
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

LED = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
BASE = "a6e3a066a827b8504e8ce804f82c77dac6955c93"   # fnd/int31's tip, this branch's base
CITE = re.compile(r"\[([A-Z][A-Z0-9]*):(\d+)(?:-(\d+))?\]")
QCITE = re.compile(r"\"([^\"]{4,600}?)\"[^\"\[\]]{0,40}?\[([A-Z][A-Z0-9]*):(\d+)(?:-(\d+))?\]")
DASHES = (chr(0x2013), chr(0x2014))
_C = {}
LINE10_OLD = "and fills the promoted sha where section 6 reads `__INTEGRATED__`."     # W3's placeholder sentence (line 10)
LINE10_NEW = "and fills the promoted sha into section 6 (`dd1aed00`, filled in set 31)."   # W41's fill

# (new citation, old citation, times on the page, the commit that wrote the old citation): lines moved unchanged
# Restated by the coordinator (7 October 2026, set 33's integration; basis: row (c)'s rounds in L8P-BREAKER.md, merged with
# fnd/l4rowc 653cb1bc, put six lines above every BRK passage the ledger cites; recite33.py re-cited the ledger's 25 BRK citations by
# their text from 46d4fe58, each quotation checked): each BRK row's NEW citation is six lines later; its old citation is unchanged.
LED_MOVED = [
    ("[BRK:1345-1350]", "[BRK:1317-1322]", 1), ("[BRK:1349-1350]", "[BRK:1321-1322]", 2), ("[BRK:1351-1355]", "[BRK:1323-1327]", 1),
    ("[BRK:1356-1361]", "[BRK:1328-1333]", 1), ("[BRK:1362-1373]", "[BRK:1334-1345]", 1), ("[BRK:1375-1428]", "[BRK:1347-1400]", 1),
    ("[BRK:1387-1390]", "[BRK:1359-1362]", 1), ("[BRK:1397-1401]", "[BRK:1369-1373]", 1), ("[BRK:1404-1407]", "[BRK:1376-1379]", 1),
    ("[BRK:1406-1408]", "[BRK:1378-1380]", 1), ("[BRK:1408]", "[BRK:1380]", 1), ("[BRK:1408-1409]", "[BRK:1380-1381]", 1),
    ("[BRK:1408-1412]", "[BRK:1380-1384]", 2), ("[BRK:1409-1412]", "[BRK:1381-1384]", 1), ("[BRK:1412]", "[BRK:1384]", 1),
    ("[BRK:1413]", "[BRK:1385]", 1), ("[BRK:1413-1415]", "[BRK:1385-1387]", 1), ("[BRK:1415-1419]", "[BRK:1387-1391]", 1),
    ("[BRK:1419-1420]", "[BRK:1391-1392]", 1), ("[BRK:1423-1425]", "[BRK:1395-1397]", 1), ("[BRK:1426-1428]", "[BRK:1398-1400]", 3),
    ("[B2:34-37]", "[B2:22-25]", 3), ("[B2:36-37]", "[B2:24-25]", 1), ("[B2:39-41]", "[B2:27-29]", 1),
    ("[B2:122-141]", "[B2:110-129]", 1), ("[B2:143-164]", "[B2:131-152]", 1), ("[B2:148-152]", "[B2:136-140]", 1),
    ("[B2:157-164]", "[B2:145-152]", 4), ("[B2:163]", "[B2:151]", 1), ("[B2:193-194]", "[B2:173-174]", 1),
    ("[P0SOL:233]", "[P0SOL:179]", 1),
    ("[P11:42-51]", "[P11:25-34]", 1), ("[P11:46-51]", "[P11:29-34]", 2), ("[P11:68-77]", "[P11:40-49]", 1),
    ("[P11:72]", "[P11:44]", 1), ("[P11:87-99]", "[P11:58-70]", 1), ("[P11:91-99]", "[P11:62-70]", 1), ("[P11:160]", "[P11:123]", 1),
]
LED_REF = {"[P11:72]": "99bbc0c6059aff0bf780f2cd6b0b102092f54f37", "[P11:160]": "99bbc0c6059aff0bf780f2cd6b0b102092f54f37"}
LED_REF_DEFAULT = "a1b68e75459766cfa79a082e63791744bec87d73"
# (new citation, old citation, times on the page, anchors copied from the cited lines): passages rewritten, read and re-cited
LED_READ = [
    ("[B2:181-190]", "[B2:168-170]", 4, ("A stiff source below the stage's voltage arriving after a withdrawal", "Not computed here",
                                         "validation P1-1's S1 (row added)")),
    ("[P0SOL:121-162]", "[P0SOL:99-121]", 1, ("## 4. D-10: an unresolved protection defect", "on the C2 circuit",
                                              "S1 and S2 then qualify the correction.")),
    ("[P0SOL:156-161]", "[P0SOL:117-121]", 1, ("something must bound the current the source", "open to a supplier's investigation")),
    ("[P0SOL:176-188]", "[P0SOL:132-143]", 1, ("withdrawn plug turns Q12 off at most 0.544 ms", "it does not resolve D-10.")),
    ("[P11:33-126]", "[P11:19-92]", 1, ("## REMAINING ENGINEERING E-1 (D-10)", "INP under 18 V wherever PV_F is under 90 V).")),
    ("[P11:79-85]", "[P11:51-56]", 1, ("**(c) The correction or justified model revision needed before any passing claim**",
                                       "each must be shown against cases F1 to F4")),
    ("[P11:79-109]", "[P11:51-80]", 1, ("**(c) The correction or justified model revision", "never by assertion.")),
    ("[P11:114-119]", "[P11:85-89]", 2, ("**(d) What stays PROVISIONAL", "PROVISIONAL until E-1's correction and S1",
                                         "the guard's Layer 9 bench rows.")),
    ("[P11:144-154]", "[P11:110-120]", 1, ("**S1, a stiff 36 V source stepping onto the port with the guard on",
                                           "the bank's differential under 1.8 V")),
    ("[P11:154-160]", "[P11:120-123]", 3, ("(a) the 36 V source added at the solar tail in parallel with a connected bench panel",
                                           "(b) the lower-source back-feed", "back-feeding PV_F through Q12's body diode",
                                           "Q12's body-diode current inside its pulsed rating")),
    ("[P11:186-191]", "[P11:149-152]", 1, ("E-1 is accepted only when", "every case F1 to F4 reads",
                                           "until then D-10 stays an unresolved protection defect.")),
]
W3A, W3B = "406d9f90dafef87663c58c0700f2df30772bbd86", "686de0a264e71e364d33e6292a85a653aefc265f"   # W3's two commits
LED_KEPT = [("[P11:89-92]", 2)]   # left as it was (named in the citation form): the passage it cited is rewritten at a6e3a066
# Restated by W41 (6 October 2026; basis: W38's F1 and the coordinator's merge d5d9c252 of main eff28be3): main's adoption 836f711b
# put three lines into the ledger above HO-H (lines 53, 54 and 62) and rewrote [P0L:n] to [P0L2:n] on three lines inside HO-H to HO-K,
# so the annex's [REM:549-581] is re-cited to [REM:552-584] and [REM:669] to [REM:672]; the range no longer reads byte for byte what
# [REM:520-552] read at W3A, so it moves from ANX_MOVED to ANX_READ and is held by its two headings, this module's anchors for it.
W41_GONE = ("[REM:549-581]", "[REM:669]")    # W23's two ledger citations of the annex, re-cited by W41
# set 33's re-cites (the coordinator, 7 October 2026, recite33.py): the citations they replaced, never left on their page
SET33_ANX_GONE = ("[REM:672]",)
SET33_LED_GONE = ("[BRK:1339-1344]", "[BRK:1343-1344]", "[BRK:1345-1349]", "[BRK:1350-1355]", "[BRK:1356-1367]", "[BRK:1369-1422]", "[BRK:1381-1384]", "[BRK:1391-1395]", "[BRK:1398-1401]", "[BRK:1400-1402]", "[BRK:1402]", "[BRK:1402-1403]", "[BRK:1402-1406]", "[BRK:1403-1406]", "[BRK:1406]", "[BRK:1407]", "[BRK:1407-1409]", "[BRK:1409-1413]", "[BRK:1413-1414]", "[BRK:1417-1419]", "[BRK:1420-1422]",)
ANX_MOVED = [
    ("[OWN:681]", "[OWN:680]", 1, W3A), ("[OWN:702]", "[OWN:701]", 1, W3B),
    ("[P11:72]", "[P11:44]", 1, W3A), ("[P11:144]", "[P11:110]", 1, W3A), ("[P11:160]", "[P11:123]", 1, W3A),
]
ANX_READ = [
    # set 33 (the coordinator, 7 October 2026): the ledger's three applies (L4K-4, L4S-3, ROWB-1) put eleven lines above its summary,
    # so recite33.py re-cited the annex's [REM:672] to [REM:683] by its text from 503e86de
    ("[REM:683]", "[REM:585]", 1, ("Counts: remaining engineering 20; qualification 1; external architecture fact 3",)),
    ("[REM:552-584]", "[REM:520-552]", 1, ("### HO-H: E11-29", "### HO-K: U-04")),
    ("[B2:183-186]", "[B2:170]", 3, ("Not computed here", "validation P1-1's S1 (row added)")),
    ("[P11:154-160]", "[P11:120-123]", 2, ("(b) the lower-source back-feed", "Q12's body-diode current inside its pulsed rating")),
]
ANX_ANCHOR = {"[REM:552-584]": ("### HO-H: E11-29", "### HO-K: U-04"), "[P11:144]": ("**S1, a stiff 36 V source stepping onto",),
              "[OWN:681]": ("Supplier item S1 must carry that engineering problem",),
              "[OWN:702]": ("A planned measurement alone does not establish that the selected protection works.",),
              "[P11:72]": ("every part within its makers' absolute maximum ratings during the fault",),
              "[P11:160]": ("Q12's body-diode current inside its pulsed rating",)}
W20_13 = ("sets no new limit and, as written, changes no record's text (6 October 2026: once `fnd/w4l4e7` at `786aed2f` is adopted, "
          "record l4e7's own page places the back-feed the same way, \"It is REMAINING ENGINEERING inside E-1\" ([P0SOL:144-145] at "
          "`786aed2f`)).", "sets no new limit and changes no record's text.")
W20_14 = ("coordinator's to carry to the next set. (6 October 2026: once `fnd/w4l4e7` at `786aed2f` is adopted, record l4e7's "
          "L4E7-P0SOL.md\n  section 4 (a) carries this reading ([P0SOL:141-149] at `786aed2f`), which answers the contradiction on "
          "record l4e7's side.)", "coordinator's to carry to the next set.\n")


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


def _aliases(page, text):
    if page == LED:
        return dict(re.findall(r"^\| ([A-Z][A-Z0-9]*) \| `(v2/[^`]+)` \|$", text, re.M))
    i = text.find("\n## 6. Amendment of 6 October 2026")
    return dict(re.findall(r"^\| ([A-Z][A-Z0-9]*) \| `([^`]+)`", text[i:], re.M)) if i >= 0 else {}


def _parse(c):
    m = CITE.fullmatch(c)
    return m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))


def _seg(lines, s, e):
    return _norm(" ".join(lines[s - 1:e])) if 1 <= s <= e <= len(lines) else None


def _tables(page):
    return (LED_MOVED, LED_READ) if page == LED else ([(n, o, k) for n, o, k, _r in ANX_MOVED], ANX_READ)


# ---- the predicates (each returns its failures; empty means it holds)

def resolve_fails(page, text):
    """Every citation this branch wrote names a table alias, an existing file and existing lines, as often as written."""
    al, fails = _aliases(page, text), []
    moved, read = _tables(page)
    for row in list(moved) + list(read):
        new, k = row[0], row[2]
        a, s, e = _parse(new)
        if text.count(new) < k:
            fails.append("%s is on the page %d times, not %d" % (new, text.count(new), k))
        if a not in al or not os.path.isfile(os.path.join(ROOT, al[a])):
            fails.append("%s: alias %s names no file" % (new, a)); continue
        if _seg(_read(al[a]).split("\n"), s, e) is None:
            fails.append("%s: lines outside %s" % (new, al[a]))
    return fails


def moved_fails(page, text):
    """A moved citation reads at its new lines exactly what its old lines read at the commit that wrote it."""
    al, fails, seen = _aliases(page, text), [], 0
    rows = [(n, o, LED_REF.get(n, LED_REF_DEFAULT)) for n, o, _k in LED_MOVED] if page == LED else \
        [(n, o, r) for n, o, _k, r in ANX_MOVED]
    for new, old, ref in rows:
        a, s, e = _parse(new); _a, os_, oe = _parse(old)
        if new not in text:
            fails.append("%s is not on the page" % new); continue
        then = _git_show(ref, al.get(a, ""))
        if then is None:
            continue
        seen += 1
        now = _read(al[a]).split("\n")
        if then.split("\n")[os_ - 1:oe] != now[s - 1:e]:
            fails.append("%s does not read what %s read at %s" % (new, old, ref[:8]))
    return fails, seen


def read_fails(page, text):
    """A re-cited passage holds the anchors copied from the cited file; the annex's moved citations hold theirs too."""
    al, fails = _aliases(page, text), []
    rows = [(n, anc) for n, _o, _k, anc in (LED_READ if page == LED else ANX_READ)]
    if page == ANX:
        rows += list(ANX_ANCHOR.items())
    for new, anchors in rows:
        a, s, e = _parse(new)
        if new not in text:
            fails.append("%s is not on the page" % new); continue
        seg = _seg(_read(al[a]).split("\n"), s, e) if a in al else None
        for anc in anchors:
            if seg is None or _norm(anc) not in seg:
                fails.append("%s does not hold %r" % (new, anc[:50]))
    return fails


def quote_fails(page, text):
    """Every quotation directly followed by a citation this branch wrote is found on the cited lines."""
    al, fails = _aliases(page, text), []
    moved, read = _tables(page)
    mine = set(r[0] for r in list(moved) + list(read))
    body = text if page == LED else text[text.find("\n## 6. Amendment of 6 October 2026"):]
    n = 0
    for m in QCITE.finditer(_norm(body)):
        c = "[%s:%s%s]" % (m.group(2), m.group(3), ("-" + m.group(4)) if m.group(4) else "")
        if c not in mine:
            continue
        n += 1
        a, s, e = _parse(c)
        seg = _seg(_read(al[a]).split("\n"), s, e) if a in al else None
        if seg is None or _norm(m.group(1)) not in seg:
            fails.append("%r is not on %s" % (m.group(1)[:60], c))
    return fails, n


def stale_fails(page, text):
    """No old citation string this branch replaced stays on its page; the one kept on purpose is there and named."""
    moved, read = _tables(page)
    news = set(r[0] for r in list(moved) + list(read))
    fails = ["%s is still on the page" % r[1] for r in list(moved) + list(read) if r[1] not in news and r[1] in text]
    if page == ANX:
        fails += ["%s is still on the page (re-cited by W41)" % c for c in W41_GONE if c in text]
        fails += ["%s is still on the page (re-cited in set 33)" % c for c in SET33_ANX_GONE if c in text]
    if page == LED:
        fails += ["%s is still on the page (re-cited in set 33)" % c for c in SET33_LED_GONE if c in text]
        for c, k in LED_KEPT:
            if text.count(c) != k:
                fails.append("%s is on the ledger %d times, not %d (once in the text, once named in the citation form)" %
                             (c, text.count(c), k))
        head = text.split("| Alias | File |", 1)[0]
        if "apart from [P11:89-92], which still names the lines of `1c6d56f5`" not in head:
            fails.append("the ledger's citation form does not name the citation it keeps")
    return fails


def rows_fails(text, base=None):
    """W20-13 and W20-14 once each, their old texts gone; the ledger one line longer than its base (W20-14's line)."""
    fails = []
    for new, old in (W20_13, W20_14):
        if text.count(new) != 1:
            fails.append("a Q-21 row is on the ledger %d times: %r" % (text.count(new), new[:50]))
        if old in text:
            fails.append("a Q-21 row's old text is still on the ledger: %r" % old[:50])
    # Restated by W41 (6 October 2026; basis: W38's F1): the coordinator's merge d5d9c252 brought main's adoption 836f711b, which put
    # three lines into the ledger (746 to 749 lines on main); so the ledger is its base plus W20-14's one plus those three.
    # Restated by the coordinator (7 October 2026; basis: set 33's chain applied L4K-4, L4S-3 and ROWB-1 to the ledger under the
    # coordinator's APPLY rulings, 750 to 761 lines at C1 9df37826): plus those eleven.
    if base is not None and text.count("\n") != base.count("\n") + 1 + 3 + 11:
        fails.append("the ledger has %d lines against its base's %d plus W20-14's one, 836f711b's three and set 33's eleven" % (
            text.count("\n"), base.count("\n")))
    return fails


# ---- the tests

def _both():
    return ((LED, _read(LED)), (ANX, _read(ANX)))


def t_every_citation_written_here_resolves():
    for page, text in _both():
        assert not resolve_fails(page, text), resolve_fails(page, text)[:5]


def t_moved_citations_read_the_lines_they_read():
    seen = 0
    for page, text in _both():
        f, n = moved_fails(page, text); seen += n
        assert not f, f[:5]
    if not seen:
        raise Skip("none of the commits that wrote the old citations is in this object store")


def t_rewritten_passages_hold_their_anchors():
    for page, text in _both():
        assert not read_fails(page, text), read_fails(page, text)[:5]


def t_quotations_stand_on_the_cited_lines():
    total = 0
    for page, text in _both():
        f, n = quote_fails(page, text); total += n
        assert not f, f[:5]
    assert total >= 10, "fewer checked quotations than written: %d" % total


def t_no_stale_citation_string_is_left():
    for page, text in _both():
        assert not stale_fails(page, text), stale_fails(page, text)[:5]


def t_the_two_q21_rows_stand_and_the_annex_keeps_its_lines():
    led, anx = _read(LED), _read(ANX)
    base_led, base_anx = _git_show(BASE, LED), _git_show(BASE, ANX)
    assert not rows_fails(led, base_led), rows_fails(led, base_led)
    if base_anx is not None:
        assert anx.count("\n") == base_anx.count("\n"), "the annex's line count moved: a citation of it by line would drift"
        # Restated by W41 (6 October 2026; basis: W10's plan R0 and W38's F2): line 10's placeholder is filled with the promoted sha;
        # sections 1 to 5 are otherwise the base's, byte for byte.
        assert LINE10_OLD in base_anx.split("\n")[9] and LINE10_NEW in anx.split("\n")[9], "line 10's fill"
        assert anx.split("\n## 6. Amendment")[0] == base_anx.split("\n## 6. Amendment")[0].replace(LINE10_OLD, LINE10_NEW, 1), \
            "sections 1 to 5 of the annex changed"


def t_no_long_dash_in_the_pages_or_this_module():
    for rel in (LED, ANX, os.path.relpath(os.path.abspath(__file__), ROOT)):
        t = _read(rel)
        for d in DASHES:
            assert d not in t, "%s carries U+%04X" % (rel, ord(d))


def t_the_predicates_refuse_broken_pages():
    """Each predicate refuses a broken copy; the base pages (when in the object store) fail them as the old defect."""
    led, anx = _read(LED), _read(ANX)
    broken = [
        ("resolve", lambda: resolve_fails(LED, led.replace("[P11:72]", "[P11:9999]", 1))),
        ("resolve", lambda: resolve_fails(ANX, anx.replace("[B2:183-186]", "[B2:184-186]", 1))),
        ("moved", lambda: moved_fails(LED, led.replace("[BRK:1408]", "[BRK:1407]"))[0]),   # set 33: [BRK:1402] re-cited to [BRK:1408]
        ("stale", lambda: stale_fails(LED, led.replace("[BRK:1408]", "[BRK:1402]", 1))),   # set 33: the position it left
        ("read", lambda: read_fails(LED, led.replace("[P11:154-160]", "[P11:155-160]"))),
        ("read", lambda: read_fails(ANX, anx.replace("[REM:552-584]", "[REM:552-577]"))),
        ("stale", lambda: stale_fails(ANX, anx.replace("[REM:683]", "[REM:672]", 1))),
        ("quote", lambda: quote_fails(LED, led.replace("something must bound the current", "something must limit the current", 1))[0]),
        ("quote", lambda: quote_fails(ANX, anx.replace("A planned measurement alone does not", "A planned measurement does not", 1))[0]),
        ("stale", lambda: stale_fails(ANX, anx.replace("[P11:144]", "[P11:110]", 1))),
        ("stale", lambda: stale_fails(LED, led.replace("[P11:89-92]", "[P11:119-126]", 1))),
        ("rows", lambda: rows_fails(led.replace(W20_13[0], W20_13[1], 1))),
        ("rows", lambda: rows_fails(led.replace(W20_14[0], W20_14[1], 1))),
    ]
    for name, f in broken:
        assert f(), "the %s predicate accepted a broken copy" % name
    base_led, base_anx = _git_show(BASE, LED), _git_show(BASE, ANX)
    if base_led is None or base_anx is None:
        raise Skip("the base %s is not in this object store (the synthetic copies above were refused)" % BASE[:8])
    assert stale_fails(LED, base_led) and stale_fails(ANX, base_anx), "the base pages pass the stale predicate"
    assert rows_fails(base_led), "the base ledger passes the Q-21 predicate"
    assert read_fails(LED, base_led) or resolve_fails(LED, base_led), "the base ledger passes the anchors"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
