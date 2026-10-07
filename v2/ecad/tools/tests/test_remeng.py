"""The remaining-engineering ledger of Layer 4's power candidate after cx46 (MESHSAT-1357, 5 October 2026), held as
predicates on its text: v2/docs/records/l4close/REMAINING-ENGINEERING.md.

The owner's part 24 (v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md): an unsupported correction is handed over as
remaining engineering "with the failed cases, attempted correction, unresolved fact or design decision, and affected
provisional outputs", the receiving company able to reproduce and change the design, qualification-only items kept apart.
The recheck cx46 (filed as received in the same folder) left twelve findings NOT CLOSED, four CLOSED BY THE CORRECTION and
two CLOSED AS CONDITIONAL.

The predicates: every alias of the ledger names an existing file and every citation [ALIAS:N-M] lies inside its file;
every repository path the ledger names exists; the twelve NOT CLOSED findings of the filed cx46 JSON are exactly the
ledger's RE sections, each quoting its classification entry and evidence verbatim, each blocker quoted in a section of one
of its items, each section carrying every field the owner's words require and no closure word; the four closed and two
conditional findings each have one row quoting its entry; the cases the brief names are handed over; the summary carries
every item once with one of the five classes and its counts line agrees; every quotation in the ledger is found verbatim
in a file it cites; the seven open fault rows of the connected output are all ledger items; no em or en dash. The
amendment of 6 October 2026 (branch fnd/ledgerfix from 6fe398e9): E11-37 is handed over as HO-L with its rows in sections 4
and 5, each key citation of it reading the line it names; HO-F carries the back-feed as remaining engineering inside E-1
with S1's row (b) its later validation, and section 6's item E keeps the disagreement named. These are software predicates
on record text: they establish no electrical or thermal property and close nothing.

Runs under the suite's runner (`env -C v2/ecad/tools/tests python3 run.py test_remeng`) and under pytest (each t_
function has a test_ alias)."""
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4close")
LEDGER = os.path.join(REC, "REMAINING-ENGINEERING.md")
CX46 = os.path.join(REC, "CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md")
CONNECTED = os.path.join(ROOT, "v2", "docs", "records", "l9t5", "l9t5_connected.out")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

NOT_CLOSED = {1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18}   # the brief's list, held against the filed JSON below
CLOSED = {3, 11, 12, 15}
CONDITIONAL = {14, 16}
CLASSES = ("remaining engineering", "qualification", "external architecture fact", "closed", "conditional")
RE_FIELDS = ("**Check's words.**", "**Failed case", "**Attempted correction", "**Unresolved", "**Affected",
             "**Receiving company's task", "**Reproduce.**", "**State on this tip.**")
HANDED_OVER = ("L8P-R9-F1", "retry heating", "L9T5-F21", "latent stuck comparator", "VOS0", "D-10", "F1 to F4",
               "back-feed", "P2 and P3", "E11-29", "U-01", "U-02", "U-04", "E11-37")
CITE = re.compile(r"\[([A-Z][A-Z0-9]*)(?::(\d+)(?:-(\d+))?)?\]")
ALIAS = re.compile(r"^\| ([A-Z][A-Z0-9]*) \| `(v2/[^`]+)` \|$", re.M)
DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
_C = {}


def _norm(t):
    return " ".join(t.split())


def _ledger():
    if "l" not in _C:
        _C["l"] = open(need(LEDGER, "the remaining-engineering ledger"), encoding="utf-8").read()
    return _C["l"]


def _aliases():
    return dict(ALIAS.findall(_ledger()))


def _cx46():
    if "j" not in _C:
        t = open(need(CX46, "the filed recheck cx46"), encoding="utf-8").read()
        _C["j"] = json.loads(t.split("```json", 1)[1].split("```", 1)[0])
    return _C["j"]


def _states():
    """cx46's classification, item number -> (item text, evidence, state word)."""
    out = {}
    for c in _cx46()["classification"]:
        n = int(c["item"].split(".", 1)[0])
        st = c["item"].rsplit(": ", 1)[1]
        out[n] = (c["item"], c["evidence"], st)
    return out


def _sections(prefix):
    """The ledger's '### <prefix>...' sections, id -> text up to the next heading."""
    t = _ledger(); out = {}
    for m in re.finditer(r"^### (%s[0-9A-Z]+)\b.*$" % re.escape(prefix), t, re.M):
        end = re.compile(r"^#{2,3} ", re.M).search(t, m.end())
        out[m.group(1)] = t[m.start():end.start() if end else len(t)]
    return out


def _section(title):
    t = _ledger(); i = t.index(title)
    j = re.compile(r"^## ", re.M).search(t, i + len(title))
    return t[i:j.start() if j else len(t)]


def t_every_alias_names_an_existing_file():
    a = _aliases()
    assert len(a) >= 25, "the alias table lost its rows: %d" % len(a)
    missing = [k for k, p in a.items() if not os.path.isfile(os.path.join(ROOT, p))]
    assert not missing, "aliases naming no file: %s" % missing


def t_every_citation_lies_inside_its_file():
    a = _aliases(); bad = []; n = 0
    sizes = {k: len(open(os.path.join(ROOT, p), encoding="utf-8").read().splitlines()) for k, p in a.items()}
    text = re.sub(r"`[^`]*`", "", _ledger())   # the citation form's own description is written in code spans
    for m in CITE.finditer(text):
        k, s, e = m.group(1), m.group(2), m.group(3)
        if k not in a:
            bad.append("undefined alias %s" % m.group(0)); continue
        n += 1
        if s:
            s = int(s); e = int(e) if e else s
            if not (1 <= s <= e <= sizes[k]):
                bad.append("%s outside 1..%d" % (m.group(0), sizes[k]))
    assert n >= 200, "the ledger cites less than it did: %d citations" % n
    assert not bad, "; ".join(bad[:8])


def t_every_repository_path_named_exists():
    paths = set(re.findall(r"`(v2/[^`\s]+)`", _ledger()))
    missing = sorted(p for p in paths if not os.path.exists(os.path.join(ROOT, p.rstrip("/"))))
    assert not missing, "paths naming nothing in the tree: %s" % missing


def t_the_twelve_not_closed_are_the_re_sections():
    st = _states()
    assert {n for n, v in st.items() if v[2] == "NOT CLOSED"} == NOT_CLOSED, "cx46's NOT CLOSED set differs from the brief"
    assert {n for n, v in st.items() if v[2] == "CLOSED BY THE CORRECTION"} == CLOSED
    assert {n for n, v in st.items() if v[2] == "CLOSED AS CONDITIONAL"} == CONDITIONAL
    re_ids = set(_sections("RE-"))
    assert re_ids == {"RE-%d" % n for n in NOT_CLOSED}, "RE sections %s" % sorted(re_ids)
    heads = re.findall(r"^### (RE-\d+) \(cx46 item (\d+)\)", _ledger(), re.M)
    assert len(heads) == 12 and all(a == "RE-" + b for a, b in heads), heads


def t_each_re_section_quotes_its_entry_and_evidence():
    st = _states(); sec = _sections("RE-")
    for n in NOT_CLOSED:
        s = _norm(sec["RE-%d" % n])
        assert '"%s"' % _norm(st[n][0]) in s, "RE-%d does not quote cx46's entry as filed" % n
        assert '"%s"' % _norm(st[n][1]) in s, "RE-%d does not quote cx46's evidence as filed" % n


def t_every_blocker_is_quoted_in_a_section_of_its_items():
    sec = {k: _norm(v) for k, v in _sections("RE-").items()}
    for r in _section("## 3.").splitlines():
        m = re.match(r"^\| C[LO]-(\d+) \|", r)
        if m: sec["RE-" + m.group(1)] = _norm(r)   # a closed or conditional finding's blocker sits in its row
    for b in _cx46()["blockers"]:
        items = [int(x) for x in re.match(r"^(\d+(?: and \d+)*)\.", b).group(1).split(" and ")]
        assert any('"%s"' % _norm(b) in sec.get("RE-%d" % i, "") for i in items), "blocker not quoted: %s" % b[:60]


def t_each_re_section_carries_every_field_and_no_closure():
    for k, s in _sections("RE-").items():
        missing = [f for f in RE_FIELDS if f not in s]
        assert not missing, "%s lacks %s" % (k, missing)
        state = s.split("**State on this tip.**", 1)[1]
        rest = state.replace("NOT CLOSED", "")
        assert "CLOSED" not in rest and "ACCEPTED" not in rest.upper(), "%s's state reads as a closure" % k


def t_closed_and_conditional_rows_quote_their_entries():
    st = _states(); t = _section("## 3.")
    for n in CLOSED | CONDITIONAL:
        rid = ("CL-%d" if n in CLOSED else "CO-%d") % n
        rows = [r for r in t.splitlines() if r.startswith("| %s |" % rid)]
        assert len(rows) == 1, "%s has %d rows" % (rid, len(rows))
        assert '"%s"' % st[n][0] in rows[0], "%s does not quote cx46's entry" % rid


def t_the_handed_over_cases_are_named():
    ho = _sections("HO-")
    heads = " ".join(s.splitlines()[0] for s in ho.values())
    missing = [c for c in HANDED_OVER if c not in heads]
    assert not missing, "handed-over cases without a section: %s" % missing
    for k, s in ho.items():
        first = s.splitlines()[0].upper()
        assert any(c.upper() in first for c in CLASSES), "%s's heading names no class" % k


def t_the_summary_carries_every_item_once_with_its_class():
    t = _section("## 5. Summary")
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in t.splitlines()
            if re.match(r"^\| (RE|HO|CL|CO)-[0-9A-Z]+ \|", r)]
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids)), "an item appears twice in the summary"
    defined = set(_sections("RE-")) | set(_sections("HO-")) | {"CL-%d" % n for n in CLOSED} | {"CO-%d" % n for n in CONDITIONAL}
    assert set(ids) == defined, "summary %s against sections %s" % (sorted(set(ids) ^ defined), "")
    for r in rows:
        assert r[1] in CLASSES, "%s carries the class %r" % (r[0], r[1])
        want = {"RE": "remaining engineering", "CL": "closed", "CO": "conditional"}.get(r[0][:2])
        if want: assert r[1] == want, "%s reads %s" % (r[0], r[1])
        assert all(r[2:5]), "%s has an empty cell" % r[0]
    counts = dict((c, sum(1 for r in rows if r[1] == c)) for c in CLASSES)
    line = re.search(r"^Counts: (.+)\.$", t, re.M).group(1)
    stated = dict((m.group(1), int(m.group(2))) for m in re.finditer(r"([a-z ]+?) (\d+)(?:;|$)", line))
    stated = {k.strip(): v for k, v in stated.items()}
    assert stated == counts, "counts line %s against the rows %s" % (stated, counts)
    assert counts["qualification"] >= 1 and counts["external architecture fact"] == 3


def t_every_quotation_is_found_in_a_cited_file():
    a = _aliases(); t = _ledger()
    corpus = [_norm(open(os.path.join(ROOT, p), encoding="utf-8").read().replace("\\n", " ")) for p in a.values()]
    pos = [i for i, c in enumerate(t) if c == '"']
    assert len(pos) % 2 == 0, "an unpaired quotation mark"
    bad = []
    for i, j in zip(pos[0::2], pos[1::2]):
        q = _norm(t[i + 1:j])
        if len(q) >= 12 and not any(q in c for c in corpus): bad.append(q[:80])
    assert not bad, "quotations found in no cited file: %s" % bad[:5]


def t_the_connected_open_rows_are_all_ledger_items():
    rows = re.findall(r"cx46 item (\d+): NOT CLOSED; it removes or weakens", open(need(CONNECTED, "the connected output"),
                                                                              encoding="utf-8").read())
    assert len(rows) == 7, "the connected output lists %d open rows, not seven" % len(rows)
    re_ids = set(_sections("RE-"))
    assert all("RE-%s" % n in re_ids for n in rows), "an open connected row has no ledger item: %s" % rows


def t_the_header_says_what_it_is_and_is_not():
    head = _ledger().split("## 0.", 1)[0]
    for w in ("**What this file is.**", "**What it is not.**", "It is not an acceptance, a closure",
              "nothing in the kit has been built, bought, powered or measured", "1c6d56f5", "4d0ff8a2"):
        assert w in _norm(head), "the header lacks: %s" % w


HO_L_FIELDS = ("**Class, and why", "**The open case.**", "**What is bounded, and from which printed figure.**",
               "**Attempted correction", "**The vendor question, drafted and UNSENT.**", "**Affected provisional outputs.**",
               "**Receiving company's task and acceptance.**", "**Reproduce.**", "**State on this tip.**")
# The amendment's key citations (read at 6fe398e9), each with a phrase the cited line or range carries: a citation that
# drifts off its subject (a revised P0 list, a re-cut record) fails here and is re-cited, never left pointing elsewhere.
AMENDMENT_CITES = (
    # the adoption of 6 October 2026 moved revision 3 onto the list's path and kept revision 2 at its dated name; the ledger's
    # statements about the list describe revision 2 and cite P0L2 (the key added to the ledger's table); the lines are revision 2's
    ("P0L2", 25, 25, "| P0-8 | E11-37"), ("P0L2", 11, 11, "missing evidence boundable at the desk"),
    ("E11", 576, 576, "E11-37 | EVIDENCE"), ("E11", 1178, 1184, "E11-37 REBOUND TO THE THREE-DEVICE NETWORK"),
    ("E11", 1527, 1527, "E11-37 STAYS OPEN"), ("E11", 1533, 1533, "E11-37 OPEN (TI or the bench)"),
    ("E11P", 1551, 1551, "| Row E11-37 |"), ("E11P", 1673, 1690, "Block E11-37"),
    ("TIQ", 74, 74, "Q-TI-17 (E11-37"), ("TIQ", 96, 110, "Q-TI-17, extended"), ("TIQ", 112, 125, "Q-TI-17 (f)"),
    ("ANX", 73, 73, "E11-37"), ("L4E9", 1134, 1134, "with E11-37 OPEN"), ("L4E9", 1401, 1401, "R-183"),
    ("REG", 279, 279, "| R-183 |"),
    ("CX46", 95, 95, "lower-source back-feed"), ("CX46", 188, 188, "lower-source back-feed"),
    # B2 and P11 re-cited by W23 (fnd/int31cite 1b2d5123; the ledger at 92b754c5) after W4's rewrite of record l4e7's pages (786aed2f,
    # adopted in set 31): B2-PRESENCE.md 168 to 170 moved to 181 to 190, SUPPLIER-P1-1-P0SOL.md 120 to 123 to 154 to 160 (W20-N3a and
    # N3b, candidate A, the coordinator's N3 decision; the end and start lines as W23 re-cited them, read at this tree by W25)
    ("B2", 181, 190, "below the stage's voltage"), ("SOLO", 399, 404, "BELOW the stage's voltage"),
    ("P11", 154, 160, "back-feeding PV_F through Q12's body diode"),
    # the owner file's lines moved by one at 6bc4424e (origin/main's b0a67a45 filed part 26 with a table row at line 26); the ledger's
    # citations were shifted the same way in commit 2b; the phrases are unchanged (lines 681 and 826 of the file at that merge)
    ("OWN", 681, 681, "Supplier item S1 must carry that engineering problem"),
    ("OWN", 826, 826, "D-10 remains receiving-company engineering item E-1."),
)


def _rows(title, rid):
    return [r for r in _section(title).splitlines() if r.startswith("| ") and rid in r]


def t_e11_37_is_handed_over_with_its_rows():
    ho = _sections("HO-")
    assert "HO-L" in ho, "E11-37 has no handed-over section"
    s = ho["HO-L"]; head = s.splitlines()[0]
    assert "E11-37" in head and "REMAINING ENGINEERING" in head and "P0-8" in head, head
    missing = [f for f in HO_L_FIELDS if f not in s]
    assert not missing, "HO-L lacks %s" % missing
    vendor = _norm(s.split("**The vendor question, drafted and UNSENT.**", 1)[1].split("\n- **", 1)[0])
    assert "Q-TI-17" in vendor and "UNSENT" in vendor, "HO-L's vendor field does not keep Q-TI-17 UNSENT"
    assert "NOT a demonstrated failure" in _norm(s), "HO-L's class widens the claim to a demonstrated failure"
    assert len(_rows("## 4.", "HO-L")) == 1, "section 4 has no single row weakened by HO-L"
    row = [r for r in _rows("## 5. Summary", "HO-L") if r.startswith("| HO-L |")]
    assert len(row) == 1 and row[0].split("|")[2].strip() == "remaining engineering", row


def t_the_amendments_citations_read_what_they_cite():
    a = _aliases(); t = _ledger(); bad = []
    for k, s, e, phrase in AMENDMENT_CITES:
        cite = "[%s:%d]" % (k, s) if s == e else "[%s:%d-%d]" % (k, s, e)
        if cite not in t:
            bad.append("%s not in the ledger" % cite); continue
        lines = open(os.path.join(ROOT, a[k]), encoding="utf-8").read().splitlines()
        if _norm(phrase) not in _norm(" ".join(lines[s - 1:e])):
            bad.append("%s does not read %r" % (cite, phrase))
    assert not bad, "; ".join(bad)


def t_the_back_feed_reads_as_engineering_inside_e1():
    f = _norm(_sections("HO-")["HO-F"])
    for w in ("REMAINING ENGINEERING inside E-1", "the later validation of that computation, not a substitute for it",
              "It is an open case, not a failed one"):
        assert w in f, "HO-F lacks: %s" % w
    assert "reclassifies nothing" not in f, "HO-F still leaves the back-feed unplaced"
    row = [r for r in _rows("## 5. Summary", "HO-F") if r.startswith("| HO-F |")]
    assert len(row) == 1 and "back-feed" in row[0] and "not a substitute" in row[0], row
    e = _norm(_section("## 6.").split("- **E.", 1)[1].split("- **F.", 1)[0])
    for w in ("[CX46:95]", "[P11:154-160]", "is the narrower one", "Record l4e7's own text stands as written"):   # W23's re-cite, 1b2d5123
        assert w in e, "section 6, item E lacks: %s" % w


def t_no_em_or_en_dash():
    for p in (LEDGER, os.path.abspath(__file__)):
        s = open(p, encoding="utf-8").read()
        assert not any(d in s for d in DASHES), "a dash in %s" % os.path.basename(p)


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
