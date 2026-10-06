"""Record l4e7's three P0 pages made consistent with the set 30 candidate's state (MESHSAT-1357, 6 October 2026, worker W4 on
branch fnd/w4l4e7, adopted in the NEXT set), held as predicates on their text and on the tree files they cite.

The pages: v2/docs/records/l4e7/L4E7-P0SOL.md, SUPPLIER-P1-1-P0SOL.md and B2-PRESENCE.md. The findings they now answer (read with
git from the branches named, cited as text only): set 30's records pack, item 1 (fnd/recpack 35dca639, RESULT.draft2.md section 5);
the remaining-engineering ledger's HO-F and its section 6, item E (fnd/ledgerfix 99bbc0c6); the DESK-gate draft's K-08, K-13, K-23
and K-24 (fnd/dgate 249e9e47, section 5); set 31's change record (SET31-CHANGES.md, in this tree since the merge 6fe398e9).

The predicates: each page carries a dated set 30 note with the promoted sha (W4's placeholder, filled in set 31) and says it is adopted in the NEXT
set; route B2 has one wording (UNSELECTED and WITHDRAWN AS DRAFTED), never "partial proposal" in any case; no page says outside a
quotation that D-16's correction or anything else is "completed independently" (the owner's part 23 words "can be completed
independently" excepted), and D-16 reads CORRECTED IN DRAFT and PROVISIONAL with R-240 cited; the lower-source back-feed is
REMAINING ENGINEERING inside E-1 with S1's row (b) its later validation on each page, and never a failing case of its own; E-1 is
named apart from record l9stk's E-1; every `path:N` citation the pages carry names a tree file and lines inside it, and each quotation
directly before a citation is found on (or within two lines of) the cited lines; the quotations the ledger takes from these pages
survive; when the other branches' commits are in the object store, the findings read there say what the pages answer. No em or en
dash. These are software predicates on record text: they establish no electrical property, change no verdict and close nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_w4l4e7.`) and under pytest (each t_ function has a test_
alias). Without git, or without another branch's commit in the object store, the rules that read it skip with their reason."""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e7")
PAGES = ("L4E7-P0SOL.md", "SUPPLIER-P1-1-P0SOL.md", "B2-PRESENCE.md")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
# The quotations the remaining-engineering ledger (fnd/ledgerfix 99bbc0c6) takes from these pages and from no other file it cites;
# test_remeng's t_every_quotation_is_found_in_a_cited_file reads them in the working tree, so they must survive this branch's edits.
LEDGER_QUOTES = ("Route B2 is UNSELECTED and WITHDRAWN AS DRAFTED",
                 "asks no decision, recommends nothing for adoption and credits B2 with no protection",
                 "Not computed here",
                 "every part within its makers' absolute maximum ratings during the fault",
                 "Q12's body-diode current inside its pulsed rating")
OTHER = {"ledger": ("99bbc0c6", "v2/docs/records/l4close/REMAINING-ENGINEERING.md"),
         "dgate": ("249e9e47", "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md"),
         "recpack": ("35dca639", "v2/docs/records/int30/RESULT.draft2.md")}
CITE = re.compile(r"`((?:v2/[^`\s]+?)?):(\d+)(?:-(\d+))?`")
_C = {}


def _norm(t):
    return " ".join(t.replace("*", "").replace("`", "").split())


def _raw(nm):
    k = ("raw", nm)
    if k not in _C:
        _C[k] = open(need(os.path.join(REC, nm), "record l4e7's page"), encoding="utf-8").read()
    return _C[k]


def _page(nm):
    return _norm(_raw(nm))


def _para_from(nm, anchor):
    """The raw page's paragraph (blank-line bounded) that first holds `anchor` once normalised, from the anchor to the paragraph's end;
    the empty string when no paragraph holds it, so a rule keeps failing rather than passing on text it never found."""
    for para in re.split(r"\n[ \t]*\n", _raw(nm)):
        q = _norm(para)
        k = q.find(anchor)
        if k >= 0:
            return q[k:]
    return ""


def _unquoted(nm):
    return re.sub(r'"[^"]*"', '""', _page(nm))


def _show(rev, path):
    k = ("show", rev, path)
    if k not in _C:
        try:
            r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)], capture_output=True)
        except OSError as e:
            raise Skip("no git on this host (%s)" % e)
        if r.returncode != 0:
            raise Skip("%s is not in this clone's object store (%s)" % (rev, path))
        _C[k] = r.stdout.decode("utf-8", errors="replace")
    return _C[k]


def t_each_page_carries_a_dated_set30_note_for_the_next_set():
    for nm in PAGES:
        p = _page(nm)
        i = p.find("Set 30 note (6 October 2026")
        assert i >= 0, "%s: no dated set 30 note" % nm
        # The note is its own paragraph of the raw page: read from the anchor to that paragraph's end, never a fixed 1200 characters
        # (test_rule_windows; set 31's candidate d0e283aa failed it, 6 Oct 2026).
        note = _para_from(nm, "Set 30 note (6 October 2026")
        # W4 wrote the placeholder `__INTEGRATED__`. Restated by W41 (6 October 2026; basis: W10's plan R0, `_runs/int31/PLAN.draft.md`
        # lines 206 to 212, and W38's finding F2): it is filled with set 30's promoted sha, dd1aed00 (`_runs/int30/ADOPTION-VALUES.md`),
        # short as the note names its other commits, and the placeholder is gone from the page (the page is read without backticks).
        assert "__INTEGRATED__" not in p, "%s: the placeholder is not filled" % nm
        for w in ("the promoted sha dd1aed00", "NEXT set", "fnd/w4l4e7", "6fe398e9", "HO-F"):
            assert w in note, "%s: the set 30 note lacks %s" % (nm, w)
    assert _raw("L4E7-P0SOL.md").startswith("DONE:") and "NOT DONE:" in _raw("L4E7-P0SOL.md").splitlines()[0]
    assert "NEXT set" in _raw("L4E7-P0SOL.md").splitlines()[0]


def t_route_b2_has_one_wording():
    """Records pack item 1 and K-24: route B2 UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline (the owner's part 25)."""
    for nm in PAGES:
        p = _page(nm)
        assert not re.search(r"(?i)partial (interface )?proposal", p), nm
        assert "WITHDRAWN AS DRAFTED" in p, nm
    heads = [l for l in _raw("L4E7-P0SOL.md").splitlines() if l.startswith("## 4.")]
    assert len(heads) == 1 and "route B2 (UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline)" in heads[0], heads
    first = _raw("L4E7-P0SOL.md").splitlines()[0]
    assert "since withdrawn as drafted" not in first
    assert "route B2 drafted and checked; since round 5 UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline" in first


def t_nothing_reads_completed_and_d16_reads_provisional():
    """Item 1 and K-13: D-16's correction is ADDRESSED IN DRAFTS and PROVISIONAL on S3 (the register's R-240) and S4 (set 31),
    never "completed"; the owner's part 23 words "can be completed independently" are the only unquoted use."""
    for nm in PAGES:
        u = _unquoted(nm)
        assert not re.search(r"(?i)(?<!can be )completed independently", u), nm
    p0 = _page("L4E7-P0SOL.md")
    assert "D-16: CORRECTED IN DRAFT" in p0 and "D-16: CORRECTED." not in p0
    for nm in ("L4E7-P0SOL.md", "SUPPLIER-P1-1-P0SOL.md"):
        p = _page(nm)
        i = p.find("ADDRESSED IN DRAFTS, PROVISIONAL, not completed")
        assert i >= 0, nm
        span = _para_from(nm, "ADDRESSED IN DRAFTS, PROVISIONAL, not completed")  # its paragraph, not 700 characters (test_rule_windows)
        for w in ("S3 and S4", "R-240", "DOWNSTREAM-REGISTER.md:336", "L4-POWER-ARCHITECTURE.md:841"):
            assert w in span, (nm, w)


def t_the_back_feed_is_engineering_inside_e1_on_every_page():
    """Item 2, K-23 and the ledger's HO-F: the lower-source back-feed is REMAINING ENGINEERING inside E-1, S1's row (b) its later
    validation (the owner's part 23); it is an open case, never a failing case of its own."""
    for nm in PAGES:
        p = _page(nm)
        assert "REMAINING ENGINEERING inside E-1" in p, nm
        assert re.search(r"row \(b\) is the later validation of that computation, not a substitute for it", p), nm
        # W28 (set 31's Q-40, 6 October 2026): the owner file's lines moved by one at b0a67a45 (part 26's table row at line 26), so
        # the part 23 sentence W4 cited at :680 stands at :681; the pages' citations were moved with it (W23's finding)
        assert "OWNER-INSTRUCTION-2026-10-05.md:681" in p and "HO-F" in p, nm
        assert "F5" not in p, nm
        assert "Not computed here; validation P1-1's S1" not in p, nm
    assert "Added, whatever happens to route B2" not in _unquoted("SUPPLIER-P1-1-P0SOL.md")
    sup = _page("SUPPLIER-P1-1-P0SOL.md")
    acc = sup.split("## Acceptance", 1)[1]
    assert "the lower-source back-feed is computed on the corrected circuit" in acc and "no new limit" in acc
    table = sup.split("| Case | What the model reads |", 1)[1].split("The port's own ratings hold", 1)[0]
    assert "back-feed" not in table, "the back-feed entered the failing-case table"


def t_e1_is_named_apart_from_l9stk():
    """K-08: one identifier, two items; named apart, neither renamed."""
    for nm in ("L4E7-P0SOL.md", "SUPPLIER-P1-1-P0SOL.md"):
        p = _page(nm)
        assert "record l4e7's E-1" in p and "not record l9stk's E-1" in p, nm
        assert "DOWNSTREAM-REGISTER.md:255" in p, nm
    assert "REMAINING ENGINEERING E-1 (D-10)" in _page("SUPPLIER-P1-1-P0SOL.md")


def t_every_tree_citation_names_lines_inside_its_file_and_its_quotation():
    """Each `path:N` or `path:N-M` (a bare `:N` meaning the path cited last) names a tree file and lines inside it; a quotation
    directly before a citation is found within two lines of the cited range."""
    n = 0
    for nm in PAGES:
        raw = _raw(nm)
        last = None
        for m in CITE.finditer(raw):
            path = m.group(1) or last
            assert path, "%s: a bare citation with no path before it" % nm
            last = path
            fp = os.path.join(ROOT, path)
            assert os.path.exists(fp), "%s: %s does not exist" % (nm, path)
            lines = open(fp, encoding="utf-8").read().splitlines()
            a = int(m.group(2)); b = int(m.group(3) or a)
            assert 1 <= a <= b <= len(lines), "%s: %s:%d-%d outside its %d lines" % (nm, path, a, b, len(lines))
            pre = raw[max(0, m.start() - 400):m.start()]
            q = re.search(r'"([^"]{12,})"[,.]?\s*\(?\s*$', pre)
            if q:
                text = _norm(q.group(1))
                window = _norm("\n".join(lines[max(0, a - 3):b + 2]))
                assert text in window, "%s: %r not on %s:%d-%d" % (nm, text[:60], path, a, b)
                n += 1
    assert n >= 10, "only %d quotation-citation pairs were read" % n


def t_the_ledgers_quotations_survive():
    corpus = " ".join(_page(nm) for nm in PAGES)
    for q in LEDGER_QUOTES:
        assert _norm(q) in corpus, q


def t_the_findings_read_on_their_branches():
    """Text only: where the other branches' commits are in the object store, the findings these pages answer say so there."""
    led = _norm(_show(*OTHER["ledger"]))
    assert "The lower-source back-feed is REMAINING ENGINEERING inside E-1" in led
    assert "S1's row (b) is the later validation of that computation, not a substitute for it" in led
    dg = _show(*OTHER["dgate"])
    for k, cite in (("K-08", "[P0SOL:101-102]"), ("K-13", "[P11:89]"), ("K-23", "[P11:120-123]"), ("K-24", "[P0SOL:99]")):
        row = [l for l in dg.splitlines() if l.startswith("| %s |" % k)]
        assert len(row) == 1 and cite in row[0], k
    rp = _norm(_show(*OTHER["recpack"]))
    assert "L4E7-P0SOL.md:99's heading \"(a partial proposal)\"" in rp


def t_no_em_or_en_dash():
    for p in [os.path.join(REC, nm) for nm in PAGES] + [os.path.abspath(__file__)]:
        s = open(p, encoding="utf-8").read()
        assert not any(d in s for d in DASHES), "a dash in %s" % os.path.basename(p)


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
