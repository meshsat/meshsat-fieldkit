"""The supplier package's two entry pages at set 30 (MESHSAT-1357, 6 October 2026), held as predicates on their text:
v2/docs/handover/START-HERE.md and v2/docs/handover/supplier/SUPPLIER-HANDOVER.md.

A receiving company opens these two pages first. Set 30 brought them to the P0 power candidate after the targeted recheck
cx46 (section 0 of each page). The constitution's section 11 asks for the tested and the packaged revision to be stated; the
owner's part 25 binds the reviewed revision to the integrated one. The integrated revision is not known when the text is
written, so both pages carry the literal placeholder __INTEGRATED__, which the coordinator fills at adoption.

The predicates: every repository path either page names exists, or is one of the files written at adoption (named so on the
page, beside the literal placeholder) or a gitignored folder the page calls gitignored; every `path:N` citation names a line
that exists in its file at the commit the text was written from; every quotation listed below is on the page and in its
source at the cited lines, and still in the source file as it stands; every section a page points to exists; the
placeholder is literal and alone (no other __X__ token, no half-filled form), and once filled it is filled everywhere with
one commit that descends from the reviewed and the written-from commits, and the files written at adoption then exist; the
six states stand apart in each page with their exact words; the statements set 30 supersedes are marked as history in
place; no em or en dash. Fixtures show that each checker refuses the defect it is for. These are software predicates on
record text: they establish no electrical or thermal property and accept, close or promote nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_entrypage`) and under pytest (each t_ function
has a test_ alias)."""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402
# Restated by W30 at the adoption (Q-04b, 6 October 2026), only where this module pinned the placeholder: the placeholder is
# filled with the promoted commit and the "(at adoption)" marks are gone, so a file written at adoption that this branch does not
# carry is accepted only while it lands with its adoption branch (test_w30entry.landing_error: that branch's commit carries it
# and is not yet in the tree); the words "(at adoption)" and "revision 3 at adoption" are no longer required on the pages.
from test_w30entry import landing_error  # noqa: E402

START = "v2/docs/handover/START-HERE.md"
SUPPLIER = "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md"
PAGES = (START, SUPPLIER)
WRITTEN_AT = "6fe398e9f624160429411e975c26564e553714d3"   # the commit section 0 of each page was written from
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"     # the candidate cx46 read
PLACEHOLDER = "__INTEGRATED__"
AT_ADOPTION = ("v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md", "v2/docs/records/int30/RESULT.md")
GITIGNORED = ("v2/ecad/out/",)                            # START-HERE names it as the gitignored readings folder
DASHES = (chr(0x2013), chr(0x2014))                        # the en dash and the em dash, by code point
STATES = (("Documents and editable artifacts", "on main as a DESK candidate (`%s`, set 31)"),
          ("Design reviewed and accepted", "NO"), ("Implemented", "NONE"), ("Physical qualification", "NONE"),
          ("Fabrication release", "BLOCKED"), ("Power-design closure", "BLOCKED"))
NEW_CONTENTS = ("v2/docs/records/l4close/REMAINING-ENGINEERING.md", "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md",
                "v2/docs/records/l4close/P0-POWER-LIST.md", "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
                "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md", "v2/docs/handover/LAYER-STATUS.md",
                "v2/docs/records/int30/RESULT.md")

C46 = "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
C45 = "v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md"
OWN = "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md"
L4E9 = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
CONST = "v2/docs/EXECUTION-CONSTITUTION.md"
LS = "v2/docs/handover/LAYER-STATUS.md"
ADD = "v2/docs/handover/supplier/CURRENT-STATE-ADDENDUM-d834e6a7.md"
REM = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
ANX = "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
S, H, B, F = "S", "H", "SH", ""   # on the supplier page, on START-HERE, on both, a fact read in the source only
# Restated by W33 (6 October 2026). Basis: W32's read of the adoption (`<worktrees>/_runs/claude/w32read/REPORT-AS-RECEIVED.md`),
# finding 2 (the Packaged row named dd1aed00 as "the commit every file of this revision is taken from", while RESULT.md and both
# pages' section 0 are absent at dd1aed00) and its citation finding (the owner-file lines bound to 6fe398e9 are one line later at
# dd1aed00, part 26's inserted row), with the coordinator's rulings 2 and 6 in W33's brief. The revisions table names four
# revisions: Tested (the promoted commit), Adopted (the adoption commit), Packaged (the commit the supplier delta's README names in
# its header, cut after the adoption, so no page can carry it) and Reviewed. The owner-file citations of section 0 are written
# `dd1aed00:<path>:N` and read at the tested revision; the QUOTES rows of OWN below stay at WRITTEN_AT as history and are read
# again at the bound line (OWN_BOUND).
TESTED = "dd1aed00d0a0a521063b5792550bc510c4707c59"       # the promoted revision the suite and the gate ran on
ADOPTED = "836f711b406be48d9eb58c9cf6f7491fbcf7c5ec"      # the adoption commit (main after the adoption, 6 October 2026)
PACKAGED_CELL = "the commit the supplier delta's README names in its header"
PACKAGED_WHAT = "cut after the adoption; the README states its difference from the tested revision and which checks cover it"
# Restated by W65 (6 October 2026, fnd/adopt31; basis: W39's rows of v2/docs/records/int31/ENTRY-PAGES.patch.md with the
# coordinator's token ruling, applied as test_adopt31 holds them): set 31's rows put set 31's candidate in the Tested and
# documents rows (__CANDIDATE__) and its adoption commit in the Adopted row (__ADOPTION__), set 30's commits kept there as dated
# history (rows S-05, S-06, S-09, U-04, U-05, U-08); U-02 renames the supplier page's section 0 heading. Those two tokens are the
# only others a page may carry; the predicates below name each change where they make it.
SET31 = ("__CANDIDATE__", "__ADOPTION__")
OWN_BOUND = {844: 845, 470: 471, 480: 481, 483: 484, 485: 486, 786: 787}   # a line at WRITTEN_AT -> the same words at TESTED
BOUND_TOK = re.compile(r"`([0-9a-f]{8,40}):(v2/[^`\s:]+):(\d+)(?:-(\d+))?`")

# (file, first line, last line, the words, the pages that quote them); lines are at WRITTEN_AT
QUOTES = (
    (C46, 3, 3, "the second negative on the method, which ends it", B),
    (C46, 8, 8, REVIEWED, B),
    (C46, 10, 10, "P0 RECHECK: CORRECTIONS NOT CLOSED.", B),
    (C45, 10, 10, "P0 CANDIDATE: NOT CONFIRMED.", S),
    (C45, 20, 20, "06077cee85d0ed44c74c2a06c9fbb2030a0dedbc", S),
    (OWN, 844, 844, "Use the existing integration gate to record the reviewed and integrated revisions and the intervening "
     "changes. If changes are only verified bindings or presentation, record that equivalence. If they change a circuit, "
     "assumption, model, limit or substantive claim, the affected result needs targeted verification before being credited. "
     "Passing the software suite alone cannot transfer an engineering verdict to altered claims.", B),
    (OWN, 470, 470, "We are not undertaking or funding the physical validation now.", B),
    (OWN, 480, 480, "no supplier is assumed engaged", S),
    (OWN, 483, 483, "A thermal failure of the tested arrangement is a design failure, not automatically a conflict in my "
     "requirements.", S),
    (OWN, 485, 485, "Distinguish investigating or testing the Saft option from adopting its 4S1P pack. No pack change has been "
     "approved by this clarification.", S),
    (OWN, 786, 786, "If a correction remains unsupported, hand it over as **remaining engineering**", S),
    (L4E9, 965, 965, "power-design closure BLOCKED, fabrication release BLOCKED, design accepted NO, implemented NONE, physical "
     "qualification NONE", B),
    (L4E9, 401, 401, "None is APPLIED", S),
    (L4E9, 1005, 1005, "**Layer 4's power architecture closes: NO**: on the set 30 candidate **the power-design closure gate is "
     "BLOCKED**", B),
    (L4E9, 1003, 1003, "criterion 1 CONDITIONAL", S), (L4E9, 1003, 1003, "criterion 2 FAIL", S),
    (L4E9, 1003, 1003, "criterion 3 PASS", S), (L4E9, 1003, 1003, "criterion 4 PASS", S),
    (L4E9, 1003, 1003, "criterion 5 CONDITIONAL", S),
    (L4E9, 1003, 1003, "A PASS here is the DESIGN gate's reading of that criterion on the desk package, never a closure, a "
     "qualification or a release.", S),
    (L4E9, 37, 37, "D-10 is OPEN, an UNRESOLVED PROTECTION DEFECT in the present model, the receiving company's remaining "
     "engineering item E-1", S),
    (L4E9, 37, 37, "D-16 is ADDRESSED IN DRAFTS: corrected in draft by P0-7 (R-240, not applied;", S),
    (L4E9, 37, 37, "PROVISIONAL in A7's zero-differential output (S3) and in the regulation at 25 V (S4)", S),
    (L4E9, 37, 37, "the battery FETs, R-157 with Q42 since L4-E11's round 9 (R-209)", S),
    (L4E9, 37, 37, "D-14 CONDITIONAL on E11-29, E11-30 and E11-36 with the three's Ciss against TI's 5 nF OPEN, E11-37", S),
    (L4E9, 37, 37, "the eFuse U42, R-181, 1.4713 to 1.8018 A, sustained-overload remedy drafted; fault qualification open, "
     "E11-38", S),
    (L4E9, 37, 37, "D-17, decision D-11's all-transmit basis on the final drafts (Layer 9's L9P-F01), is OPEN", S),
    (L4E9, 37, 37, "round 7's raised floor is withdrawn as a correction (it narrowed the requirement)", S),
    (L4E9, 37, 37, "round 8's fan design-out (R-210 to R-212) is WITHDRAWN (FAN_OK rejected)", S),
    (L4E9, 37, 37, "with cx46 item 2 NOT CLOSED (remaining engineering RE-2)", S),
    (L4E9, 38, 38, "The objective of 48 to 72 h is NOT MET", S),
    (CONST, 23, 23, "A promoted integration set is none of those by itself.", S),
    (CONST, 94, 94, "Ask suppliers to confirm engineering scope, responsible personnel, deliverables, exclusions, cost and "
     "schedule. Do not assume ordinary fabrication/assembly includes circuit design or qualification.", S),
    (LS, 476, 476, "board B's coolers on a per-slot 12 V step-up with an eFuse (E11-40, R-190)", S),
    (LS, 476, 476, "Set 29: board A's slots 1 and 3 on slot 2's LM5176 stage with the coolers at full speed (L9P-F02, "
     "`apply_gen_sch_a_slotlm.py`)", S),
    (LS, 476, 476, "VBUS20's over-voltage cut-off in VIN_RAW (S-111, R-48)", S),
    (LS, 330, 330, "The connected power design is `v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md`", F),
    (REM, 11, 11, "is not an acceptance, a closure, a verdict, a check, a qualification or a release of anything", S),
    (ANX, 10, 10, "Nothing here is a request for a requirement change, a purchase, an outside contact, fabrication or "
     "energisation.", S),
    ("v2/docs/records/l4close/FINDINGS-LEDGER.md", 1, 1, "every rejected collaborator finding of L4-E7 to L4-E13", S),
    ("v2/docs/records/l9t5/fetch_held_back.py", 11, 11, "exit 0: present and checked; 3: a mismatch", S),
    ("v2/docs/records/l9t5/stability/regen_cascade.sh", 7, 7, "outside the tree", S),
    ("v2/docs/records/l9t5/stability/regen_cascade.sh", 9, 11, "for pair in l9stk/l9stk_copper", F),
    ("v2/docs/records/l9t5/README.md", 129, 132, "`stability/` keeps the cascade", F),
    ("v2/docs/records/l8p/gen_netlist.py", 5, 5, "gen_netlist.py GENERATOR OUT.net", B),
    ("v2/docs/records/l8p/gen_netlist.py", 15, 15, "It is not KiCad's netlist", B),
    ("v2/docs/records/l8p/gen_netlist.py", 17, 17, "is the reading of record", F),
    (ADD, 27, 27, "## 2. Entry-page rows this addendum supersedes", F),
    (ADD, 33, 33, "P8, board B's fans", F), (ADD, 34, 34, "P10, VBUS20", F), (ADD, 35, 35, "Section 7, item 3", F),
    (ADD, 36, 36, "Section 9, last bullet", F), (ADD, 37, 37, "the L9P-F02 row", F), (ADD, 38, 38, "WITHDRAWN", S),
    (ADD, 44, 44, "7.472 A against its 7.0957 A loop minimum", S),
    ("v2/docs/records/l4close/REVIEW-SUPPLIER-D834E6A7-AS-RECEIVED.md", 11, 11, "READY for an initial supplier engineering "
     "quotation, accompanied by a short current-state correction sheet. Power-design closure and fabrication release remain "
     "BLOCKED.", S),
    ("v2/docs/records/l4close/REVIEW-SUPPLIER-DELTA-AA76C894-AS-RECEIVED.md", 5, 5, "READY for supplier engineering review and "
     "quotation, with this review attached. Power-design closure and fabrication release remain BLOCKED.", S),
)

# (file, a heading it must carry, written at adoption)
ANCHORS = (
    (SUPPLIER, "## 0. This revision: set 31 over set 30", False), (SUPPLIER, "### 0a. The revisions", False),
    (SUPPLIER, "### 0b. The states, each apart", False), (SUPPLIER, "### 0c. What set 30 adds to the package", False),
    (SUPPLIER, "### 0d. What we ask of you, and what we do not", False), (SUPPLIER, "### 0e. How to reproduce", False),
    (SUPPLIER, "## 2. Requirements, operating modes and fixed constraints", False), (SUPPLIER, "## 4. Layer by layer", False),
    (SUPPLIER, "## 7. How to check the claims", False), (SUPPLIER, "4. **What the project tested", False),
    (SUPPLIER, "## 8. What we ask a supplier to quote for", False), (SUPPLIER, "## 10. Changes since the release-candidate", False),
    (START, "## 0. Set 30's revision (6 October 2026): what it hands over, and set 31 over it", False),  # W69 from W68's F2: set 30's (START, "## 6. Regenerating and verifying", False),
    (REM, "## 1. The twelve cx46 findings NOT CLOSED", False), (REM, "## 2. The cases the authors handed over", False),
    (REM, "## 5. Summary", False), (REM, "## 7. Reproducing the records", False),
    (ANX, "## 1. U-02, the sealed case's heat rejection", False), (ANX, "## 2. U-04, the charger", False),
    (ANX, "## 3. U-01, the cell", False), (ANX, "## 4. E11-29, the three paralleled battery FETs", False),
    (L4E9, "## 8. The closure gate in detail", False), (L4E9, "### 8e. The independent checks of the P0 candidate", False),
    ("v2/docs/EXECUTION-PLAN.md", "### Register additions, 4 October 2026 21:05 CEST", False),
    (LS, "**After set 30", True),
)

# a statement set 30 supersedes, and the mark it must carry in the same paragraph or table row (supplier page)
SUPERSEDED = (
    ("the floor rises to 16.1 V rest", "WITHDRAWN on 4 October 2026"),
    ("capped at 70 % by a firmware rule", "WITHDRAWN on 4 October 2026"),
    ("Work carried in the package's `branches/`", "History, 3 October 2026"),
    ("README names those branches and their tips", "history of 3 October 2026"),
    ("the device rail's 7.181 A against 7.096 A as before", "history of 3 October 2026"),
    ("The collaborator's targeted\nrecheck of this candidate read NOT YET", "History, 3 October 2026"),
)

PATH_TOK = re.compile(r"`((?:v2/|records/)[^`\s:]+)(?::(\d+)(?:-(\d+))?)?`")
CONT_TOK = re.compile(r"`:(\d+)(?:-(\d+))?`")
UNDERS = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
HALF = re.compile(r"(?<![_A-Za-z0-9])_{1,2}INTEGRATED_{0,2}(?![_A-Za-z0-9])|<INTEGRATED|\[COORDINATOR")
_C = {}


def _norm(t):
    return " ".join(t.split())


def _repo(p):
    return "v2/docs/" + p if p.startswith("records/") else p


def _page(p):
    if p not in _C:
        _C[p] = open(need(os.path.join(ROOT, p), "the entry page"), encoding="utf-8").read()
    return _C[p]


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git: %s" % e)
    return r


def _at(path, commit=WRITTEN_AT):
    key = (commit, path)
    if key not in _C:
        r = _git("show", "%s:%s" % (commit, path))
        if r.returncode != 0:
            if _git("cat-file", "-e", commit + "^{commit}").returncode != 0:
                raise Skip("the commit %s is not in this checkout (a snapshot without history)" % commit[:8])
            raise AssertionError("%s is not in the tree at %s" % (path, commit[:8]))
        _C[key] = r.stdout.decode("utf-8").split("\n")
    return _C[key]


def _paths(text):
    """Every repository path the text names in backticks, with a line citation where it has one."""
    return [(_repo(m.group(1)), m.group(2), m.group(3)) for m in PATH_TOK.finditer(text)
            if "<" not in m.group(1) and "*" not in m.group(1)]


def _citations(text):
    """Every `path:N` and `:N` citation of the text, the bare `:N` resolved to the last path named before it."""
    toks = sorted([(m.start(), "p", m) for m in PATH_TOK.finditer(text)] + [(m.start(), "c", m) for m in CONT_TOK.finditer(text)],
                  key=lambda x: x[0])
    last, out = None, []
    for _, kind, m in toks:
        if kind == "p":
            last = _repo(m.group(1))
            if m.group(2):
                out.append((last, int(m.group(2)), int(m.group(3) or m.group(2))))
        else:
            if last is None:
                out.append((None, int(m.group(1)), int(m.group(2) or m.group(1))))
            else:
                out.append((last, int(m.group(1)), int(m.group(2) or m.group(1))))
    return out


def _adoption_marked(text, p):
    """The text calls the file written at adoption: its path (full, or from records/) then "(at adoption)" within 40
    characters."""
    pat = re.escape(p)
    if p.startswith("v2/docs/records/"):
        pat = r"(?:v2/docs/)?" + re.escape(p[len("v2/docs/"):])
    return re.search(r"`" + pat + r"`[^`]{0,40}?\(at adoption\)", text) is not None


MARK_AFTER = re.compile(r"[^`]{0,40}?\(at adoption\)")


def _missing_paths(text, exists, lands=lambda p: False):
    """The paths the text names that are absent, less the declared exceptions: a file written at adoption while the text
    still carries the literal placeholder and calls it so at EVERY mention, and a gitignored folder."""
    filled = PLACEHOLDER not in text
    bad = []
    for m in PATH_TOK.finditer(text):
        if "<" in m.group(1) or "*" in m.group(1):
            continue
        p = _repo(m.group(1))
        if exists(p) or p in GITIGNORED:
            continue
        if p in AT_ADOPTION and not filled and MARK_AFTER.match(text, m.end()):
            continue
        if filled and lands(p):   # W30: filled, a record adopted on another adoption branch lands with it
            continue
        bad.append(p)
    return sorted(set(bad))


def _placeholder_errors(texts):
    """The placeholder is literal and alone; filled, it is filled everywhere with one commit."""
    errs = []
    for name, t in texts.items():
        for tok in set(UNDERS.findall(t)) - {PLACEHOLDER} - set(SET31):   # W65: set 31's tokens, held by test_adopt31
            errs.append("%s carries an unknown placeholder %s" % (name, tok))
        for m in HALF.finditer(t):
            if t[m.start():m.start() + len(PLACEHOLDER)] != PLACEHOLDER:
                errs.append("%s carries a half-filled placeholder %r" % (name, t[m.start():m.end() + 4]))
    held = [n for n, t in texts.items() if PLACEHOLDER in t]
    if held and len(held) != len(texts):
        errs.append("the placeholder is filled in %s but not in %s" % (sorted(set(texts) - set(held)), held))
    return errs


def _row(text, label):
    m = re.search(r"^\| %s \| (.+?) \|" % re.escape(label), text, re.M)
    return m.group(1) if m else None


def _section0(p):
    t = _page(p)
    i = t.find("\n## 0. ")
    j = t.find("\n## 1. ", i)
    assert i >= 0 and j > i, "%s has no section 0 before its section 1" % p
    return t[i:j]


def _commit_cell(cell):
    m = re.fullmatch(r"`([0-9a-f]{8,40}|%s|%s)`(?: \(`([0-9a-f]{40})`\))?" % (PLACEHOLDER, SET31[0]), cell.strip())
    return m and m.group(1)


# ------------------------------------------------------------------------------------------------------------ the tree
def t_every_cited_path_exists():
    for p in PAGES:
        bad = _missing_paths(_page(p), lambda q: os.path.exists(os.path.join(ROOT, q)), lambda q: landing_error(q) is None)
        assert not bad, "%s names %d path(s) that do not exist and are not declared: %s" % (p, len(bad), bad)


def t_every_line_citation_names_a_line_of_its_file():
    for p in PAGES:
        cites = _citations(_page(p))
        assert cites, "%s carries no line citation; the set 30 text cites its sources by line" % p
        for f, a, b in cites:
            assert f is not None, "%s: a `:%d` citation follows no path" % (p, a)
            lines = _at(f)
            assert 1 <= a <= b <= len(lines), "%s cites %s:%d-%d, which has %d lines at %s" % (p, f, a, b, len(lines), WRITTEN_AT[:8])


def t_every_quotation_is_on_its_page_and_in_its_source():
    for f, a, b, words, pages in QUOTES:
        src = _norm(" ".join(_at(f)[a - 1:b]))
        assert _norm(words) in src, "%s:%d-%d at %s does not read: %s" % (f, a, b, WRITTEN_AT[:8], words[:70])
        now = _norm(open(os.path.join(ROOT, f), encoding="utf-8").read())
        assert _norm(words) in now, "%s no longer reads (the page's quotation is stale): %s" % (f, words[:70])
        for k, p in (("S", SUPPLIER), ("H", START)):
            if k in pages:
                assert _norm(words) in _norm(_page(p)), "%s does not quote %s:%d: %s" % (p, f, a, words[:70])


def t_every_section_a_page_points_to_exists():
    filled = PLACEHOLDER not in _page(SUPPLIER)
    for f, head, adoption in ANCHORS:
        path = os.path.join(ROOT, f)
        if adoption and not filled:
            continue
        txt = open(need(path, "a file the entry pages point to"), encoding="utf-8").read()
        assert any(ln.startswith(head) for ln in txt.split("\n")), "%s has no heading %r" % (f, head)


# ------------------------------------------------------------------------------------------------------ the placeholder
def t_the_placeholder_is_literal_and_alone():
    texts = {p: _page(p) for p in PAGES}
    errs = _placeholder_errors(texts)
    assert not errs, errs
    held = PLACEHOLDER in _page(SUPPLIER)
    for p in PAGES:
        s0 = _section0(p)
        for label in ("Tested", "Packaged"):
            cell = _row(s0, label)
            assert cell is not None, "%s section 0 has no %s row" % (p, label)
            if label == "Packaged" and not held:   # W33: filled, the Packaged row is the README's commit, never a sha here
                errs = _packaged_errors(s0)
                assert not errs, "%s: %s" % (p, errs)
                continue
            got = _commit_cell(cell)
            assert got, "%s: the %s revision is neither the literal placeholder nor a commit: %s" % (p, label, cell)
            assert (got == PLACEHOLDER) == held, "%s: the %s revision reads %s while the pages %s the placeholder elsewhere" % (
                p, label, got, "carry" if held else "do not carry")
        assert REVIEWED in _row(s0, "Reviewed"), "%s: the Reviewed row does not carry %s" % (p, REVIEWED)
        doc = dict((r.split(" | ")[0], r) for r in re.findall(r"^\| (Documents and editable artifacts \| .+?) \|$", s0, re.M))
        assert (PLACEHOLDER in doc.get("Documents and editable artifacts", "")) == held, "%s: the documents row and the revisions disagree" % p


def t_a_filled_placeholder_names_one_promoted_commit_and_the_adopted_files():
    """Inactive while the placeholder stands. Once the coordinator fills it, the Tested rows of both pages name one commit, the
    promoted one; it exists, it descends from the reviewed commit and from the commit the text was written from, and the files the
    pages call 'at adoption' exist, with LAYER-STATUS's blocks headed After set 30. Restated by W33 (6 October 2026, W32's finding 2
    and the coordinator's ruling 2): the Packaged row names the commit by the supplier delta's README (cut after the adoption), and
    the Adopted row of both pages names the adoption commit, which descends from the tested one."""
    if PLACEHOLDER in _page(SUPPLIER):
        assert PLACEHOLDER in _page(START)
        return
    got, adopted = set(), set()
    for p in PAGES:   # W33: Tested names the promoted commit; Adopted the adoption commit; Packaged the README's commit
        got.add(_commit_cell(_row(_section0(p), "Tested")))
        adopted.add(_row(_section0(p), "Adopted"))
        errs = _packaged_errors(_section0(p))
        assert not errs, "%s: %s" % (p, errs)
    assert len(got) == 1, "the pages name more than one integrated commit: %s" % sorted(got)
    c = got.pop()
    # W65 (set 31; basis above SET31): the Tested row names set 31's candidate, __CANDIDATE__ until set 31's adoption fills it with a
    # commit that descends from set 30's promoted one; the Adopted row names __ADOPTION__ or a commit that descends from the tested
    # one; set 30's tested and adoption commits stand in those rows as dated history and keep their order
    for p in PAGES:
        s0 = _section0(p)
        assert ("set 30's was `%s`, kept as dated history" % TESTED) in s0, "%s: set 30's tested commit is not kept in the Tested row" % p
        assert ("set 30's was `%s`, 6 October 2026, 11:25 CEST, kept as dated history" % ADOPTED) in s0, "%s: set 30's adoption" % p
    assert _git("merge-base", "--is-ancestor", TESTED, ADOPTED).returncode == 0, "set 30's adoption does not follow its tested commit"
    if c != SET31[0]:
        assert _git("cat-file", "-e", c + "^{commit}").returncode == 0, "%s is not a commit of this repository" % c
        for anc in (REVIEWED, WRITTEN_AT, TESTED):
            assert _git("merge-base", "--is-ancestor", anc, c).returncode == 0, "%s does not descend from %s" % (c, anc[:8])
    assert len(adopted) == 1, "the Adopted rows differ: %s" % sorted(str(a) for a in adopted)
    cell = adopted.pop()
    if cell != "`%s`" % SET31[1]:
        a = _commit_cell(cell)
        assert a and a != SET31[0] and _git("cat-file", "-e", a + "^{commit}").returncode == 0, "the Adopted row reads %s" % cell
        if c != SET31[0]:
            assert _git("merge-base", "--is-ancestor", c, a).returncode == 0, "the adoption commit does not descend from the tested one"
    for f in AT_ADOPTION:   # W30: adopted in the tree, or landing with its adoption branch
        assert landing_error(f) is None, "filled, but %s is not adopted: %s" % (f, landing_error(f))
    assert "**After set 30" in open(os.path.join(ROOT, LS), encoding="utf-8").read(), "filled, but LAYER-STATUS has no After set 30"


def _packaged_errors(s0):
    """W33: the Packaged row names the commit by the README that carries it (cut after the adoption), never a sha on the page."""
    m = re.search(r"^\| Packaged \| (.+?) \| (.+?) \|$", s0, re.M)
    if not m:
        return ["no Packaged row"]
    errs = []
    if m.group(1) != PACKAGED_CELL:
        errs.append("the Packaged row reads %r, not %r" % (m.group(1)[:60], PACKAGED_CELL))
    if m.group(2) != PACKAGED_WHAT:
        errs.append("the Packaged row's definition reads %r" % m.group(2)[:60])
    if re.search(r"`[0-9a-f]{8,40}`", m.group(0)):
        errs.append("the Packaged row names a commit")
    return errs


def _bound_errors(s0, flag, at=None):
    """W33: section 0 cites the owner-instruction file only as `TESTED[:8]:<path>:N`; each QUOTES row of OWN quoted on this page
    is cited at its bound line, whose words are those of the row; no bare `path:N` citation of the file is left."""
    at = at or (lambda n: _at(OWN, TESTED)[n - 1] if 1 <= n <= len(_at(OWN, TESTED)) else "")
    errs = []
    if re.search(r"`%s:\d+" % re.escape(OWN), s0):
        errs.append("a bare citation of the owner file is left")
    cited = set()
    for m in BOUND_TOK.finditer(s0):
        if m.group(2) != OWN:
            continue
        if not TESTED.startswith(m.group(1)):
            errs.append("the owner file is cited at %s, not at the tested revision" % m.group(1))
        cited.add(int(m.group(3)))
    for f, a, b, words, pages in QUOTES:
        if f != OWN or flag not in pages:
            continue
        n = OWN_BOUND[a]
        if n not in cited:
            errs.append("line %d (%d at %s) is not cited" % (n, a, WRITTEN_AT[:8]))
        elif _norm(words) not in _norm(at(n)):
            errs.append("line %d at %s does not read %r" % (n, TESTED[:8], words[:40]))
    extra = cited - set(OWN_BOUND[a] for f, a, b, w, pg in QUOTES if f == OWN and flag in pg)
    if extra:
        errs.append("bound lines with no quotation row: %s" % sorted(extra))
    return errs


def t_the_owner_file_citations_are_bound_to_the_tested_revision():
    for p, flag in ((START, "H"), (SUPPLIER, "S")):
        errs = _bound_errors(_section0(p), flag)
        assert not errs, "%s: %s" % (p, errs)


# -------------------------------------------------------------------------------------------------------- the content
def t_the_six_states_stand_apart_in_each_page():
    for p in PAGES:
        s0 = _section0(p)
        m = re.search(r"^\| What \| State \|\n\|---\|---\|\n((?:\|.*\|\n)+)", s0, re.M)
        assert m, "%s section 0 has no states table" % p
        rows = [tuple(c.strip() for c in ln.strip("|").split("|")) for ln in m.group(1).strip("\n").split("\n")]
        assert [r[0] for r in rows] == [w for w, _ in STATES], "%s: the states table's rows are %s" % (p, [r[0] for r in rows])
        for (what, word), (_, got) in zip(STATES, rows):
            if "%s" in word:
                ok = re.fullmatch(re.escape(word).replace(re.escape("%s"), r"([0-9a-f]{8,40}|%s|%s)" % (PLACEHOLDER, SET31[0])), got)
            else:
                ok = got == word
            assert ok, "%s: %s reads %r, not %r" % (p, what, got, word)


def t_the_reviewed_revision_carries_its_verdict_and_the_binding_rule():
    rule = [q for q in QUOTES if q[0] == OWN and q[1] == 844][0][3]
    for p in PAGES:
        s0 = _norm(_section0(p))
        for w in ('"P0 RECHECK: CORRECTIONS NOT CLOSED."', rule, "int30/RESULT.md`", "4d0ff8a2"):   # W30: the mark is gone
            assert _norm(w) in s0, "%s section 0 lacks: %s" % (p, w[:60])


def t_the_new_contents_are_named_in_each_page():
    for p in PAGES:
        s0 = _section0(p)
        for f in NEW_CONTENTS:
            assert "`%s`" % f in s0, "%s section 0 does not name %s" % (p, f)
        for f in AT_ADOPTION:   # W30: while the placeholder stood, each was marked; filled, the mark is gone
            assert _adoption_marked(s0, f) == (PLACEHOLDER in s0), "%s: the at-adoption mark of %s disagrees with the placeholder" % (p, f)
        for w in ("K-01 to K-28", '"After set 30"', "revision 3"):   # W30: was "revision 3 at adoption"
            assert w in s0, "%s section 0 lacks %s" % (p, w)


def t_the_ask_and_what_is_not_asked():
    s0 = _norm(_section0(SUPPLIER))
    for w in ("confirm the engineering scope, the responsible personnel, the deliverables, the exclusions, the cost and the schedule",
              "take over the remaining engineering as the ledger scopes it", "U-01, U-02, U-04 and E11-29",
              "Nothing is ordered or funded", "We do NOT ask you", "fabricate, assemble or order any board",
              "qualification-only", "PROPOSAL"):
        assert w in s0, "the supplier page's section 0 lacks: %s" % w
    st = _norm(_section0(START))
    for w in ("Nothing is ordered or funded", "Not asked", "Asked"):
        assert w in st, "START-HERE section 0 lacks: %s" % w


def t_the_reproduction_routes_are_named():
    for p in PAGES:
        s0 = _section0(p)
        for w in ("fetch_held_back.py", "gen_netlist.py GENERATOR", "v2/ecad/tools/tests/run.py", "regen_cascade.sh"):
            assert w in s0, "%s section 0 does not name %s" % (p, w)


def t_the_superseded_statements_are_marked_where_they_stand():
    t = _page(SUPPLIER)
    blocks = [b for b in re.split(r"\n\s*\n", t)]
    for old, mark in SUPERSEDED:
        hit = [b for b in blocks if old in b]
        assert len(hit) == 1, "the superseded statement %r is found %d times" % (old[:40], len(hit))
        units = [ln for ln in hit[0].split("\n") if old in ln] if hit[0].lstrip().startswith("|") else [hit[0]]
        assert any(mark in u for u in units), "%r is not marked %r where it stands" % (old[:40], mark)
    st = _section0(START)
    assert '"This is handover H3" describes the edition of 27 September 2026' in _norm(st), "START-HERE does not date its H3 opening"


def t_each_page_keeps_a_dated_set_30_entry():
    assert "- **6 October 2026: set 30, the revision `%s`**" % PLACEHOLDER in _page(SUPPLIER) or \
        re.search(r"- \*\*6 October 2026: set 30, the revision `[0-9a-f]{8,40}`\*\*", _page(SUPPLIER)), "the supplier page's history lacks set 30"
    assert re.search(r"\*\*Set 30\*\* \(6 October 2026; the revision `([0-9a-f]{8,40}|%s)`\)" % PLACEHOLDER, _page(START)), \
        "START-HERE's edition history lacks set 30"


def t_no_em_or_en_dash():
    for p in list(PAGES) + [os.path.relpath(os.path.abspath(__file__), ROOT)]:
        s = open(os.path.join(ROOT, p), encoding="utf-8").read()
        assert not any(d in s for d in DASHES), "a dash in %s" % p


# ----------------------------------------------------------------------------- the checkers refuse what they are for
def t_the_checkers_refuse_their_defects():
    good = "x `__INTEGRATED__` y `v2/docs/records/int30/RESULT.md` (at adoption) z"
    assert not _placeholder_errors({"a": good, "b": good})
    for bad, words in (("x `__INTEGRATED_` y", "half-filled"), ("x `__PROMO__` y", "unknown placeholder"),
                       ("x `<INTEGRATED-SHA>` y", "half-filled"), ("x [COORDINATOR: verdict] y", "half-filled")):
        errs = _placeholder_errors({"a": bad + " " + good, "b": good})
        assert any(words in e for e in errs), (bad, errs)
    errs = _placeholder_errors({"a": good, "b": good.replace(PLACEHOLDER, "0123abcd")})
    assert any("filled in" in e for e in errs), errs
    # an absent path is refused, a file written at adoption only while the literal placeholder stands and the text says so
    assert _missing_paths("`v2/docs/NOPE.md`", lambda q: False) == ["v2/docs/NOPE.md"]
    assert _missing_paths(good, lambda q: False) == []
    assert _missing_paths(good + " and again `v2/docs/records/int30/RESULT.md` unmarked", lambda q: False) == \
        ["v2/docs/records/int30/RESULT.md"]
    assert _missing_paths(good.replace(PLACEHOLDER, "0123abcd"), lambda q: False) == ["v2/docs/records/int30/RESULT.md"]
    assert _missing_paths("`v2/docs/records/int30/RESULT.md`, written later; `__INTEGRATED__`", lambda q: False) == \
        ["v2/docs/records/int30/RESULT.md"]
    # a bare `:N` reads the last path named before it, and one with none before it is refused by the citation test
    c = _citations("`records/a/B.md:3` then (`:7-9`), then `v2/x/Y.md` and (`:2`)")
    assert c == [("v2/docs/records/a/B.md", 3, 3), ("v2/docs/records/a/B.md", 7, 9), ("v2/x/Y.md", 2, 2)], c
    assert _citations("(`:4`) first")[0][0] is None
    # the commit cell takes the literal placeholder or a hex commit, nothing else
    assert _commit_cell("`__INTEGRATED__`") == PLACEHOLDER and _commit_cell("`4d0ff8a2` (`%s`)" % REVIEWED) == "4d0ff8a2"
    assert not _commit_cell("`INTEGRATED`") and not _commit_cell("`the promoted commit`")
    # W33: the Packaged row in the README form passes; a sha, another wording or a missing definition is refused
    ok = "| Packaged | %s | %s |" % (PACKAGED_CELL, PACKAGED_WHAT)
    assert not _packaged_errors(ok)
    assert _packaged_errors("| Packaged | `%s` | the commit every file of this revision is taken from |" % TESTED)
    assert _packaged_errors(ok.replace("README names", "README states"))
    assert _packaged_errors(ok.replace(PACKAGED_WHAT, "cut after the adoption"))
    # W33: an owner-file citation at its bound line passes; the old line at the tested revision, a bare one or another revision fails
    words = [q for q in QUOTES if q[0] == OWN and q[1] == 844][0][3]
    lines = {845: words}
    at = lambda n: lines.get(n, "")  # noqa: E731
    good = "(`%s:%s:845`)" % (TESTED[:8], OWN)
    one = [r for r in QUOTES if r[0] == OWN and r[1] == 844]
    saved = list(QUOTES)
    try:
        globals()["QUOTES"] = tuple(one)
        assert not _bound_errors(good, "H", at)
        assert _bound_errors("(`%s:%s:844`)" % (TESTED[:8], OWN), "H", at), "the unshifted line passed"
        assert _bound_errors("(`%s:845`)" % OWN, "H", at), "a bare owner-file citation passed"
        assert _bound_errors("(`%s:%s:845`)" % (WRITTEN_AT[:8], OWN), "H", at), "a citation at another revision passed"
    finally:
        globals()["QUOTES"] = tuple(saved)


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
