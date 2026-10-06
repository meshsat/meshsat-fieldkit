"""The two entry pages adopted on the promoted revision (MESHSAT-1357, set 30, queue item Q-04b, 6 October 2026), held as
predicates on their text: v2/docs/handover/START-HERE.md and v2/docs/handover/supplier/SUPPLIER-HANDOVER.md.

Slot N wrote set 30's passages of both pages with the literal placeholder __INTEGRATED__ (7 on START-HERE, 8 on the supplier
page) and marked the records written at adoption "(at adoption)". Worker W30 filled every placeholder with the promoted commit
the coordinator saved for the adoption (`<worktrees>/_runs/int30/ADOPTION-VALUES.md`: INTEGRATED = CANDIDATE = PROMOTED =
MIRROR, dd1aed00d0a0a521063b5792550bc510c4707c59), pointed the passages at the records' final paths, stated what the promoted
revision is and is not in the integration record's words (`v2/docs/records/int30/RESULT.md`, sections 1, 2 and 6), and stated
Layer 4's DESK gate and the three completion claims in the coordinator's words (`<worktrees>/_runs/int30/Q05-verdict.final.md`,
6 October 2026, 10:45 CEST), citing the DESK-gate assessment.

The predicates: no placeholder and no "(at adoption)" mark is left, and the promoted commit stands at each of the 15 places;
every repository path either page names exists (or is the readings folder git ignores), or is one of the records that land with the other two adoption branches (W26's
fnd/adopt30a, W27's fnd/adopt30b), held by the branch commit that carries it and refused once that commit is in the tree; no
draft path of the adopted records is cited; the four claims stand on each page in the coordinator's exact words, beside the
assessment's path and the date, and in the verdict file (when the coordinator's logs are on the host) and in the assessment
(once it is in the tree); the integration record's words stand on each page and in RESULT.md (in the tree, or at W26's commit
until it lands); the P0 list the pages call revision 3 is revision 3 (in the tree, or at W27's commit until it lands); no em or
en dash. Fixtures show that each checker refuses the defect it is for. These are software predicates on record text: they
establish no electrical or thermal property and accept, close or promote nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_w30entry.`) and under pytest (each t_ function has a
test_ alias)."""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

START = "v2/docs/handover/START-HERE.md"
SUPPLIER = "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md"
PAGES = (START, SUPPLIER)
PROMOTED = "dd1aed00d0a0a521063b5792550bc510c4707c59"     # ADOPTION-VALUES.md: INTEGRATED = CANDIDATE = PROMOTED = MIRROR
FILLED = {START: 7, SUPPLIER: 8}                           # Slot N's placeholders per page at fnd/entrypage 1b82c61b
PLACEHOLDER = "__INTEGRATED__"
DASHES = (chr(0x2013), chr(0x2014))                        # the en dash and the em dash, by code point

RESULT = "v2/docs/records/int30/RESULT.md"
CLASS = "v2/docs/records/int30/CLASSIFICATION.md"
P0 = "v2/docs/records/l4close/P0-POWER-LIST.md"
P0R2 = "v2/docs/records/l4close/P0-POWER-LIST.rev2-2026-10-05.md"
DGATE = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
LS = "v2/docs/handover/LAYER-STATUS.md"
FINAL = (RESULT, CLASS, P0, DGATE, LS)                     # the records' final paths after the adoption (the coordinator's INBOX)
DRAFTS = ("RESULT.draft2.md", "RESULT.draft3.md", "CLASSIFICATION.draft.md", "P0-POWER-LIST.rev3.draft2.md",
          "P0-POWER-LIST.rev3.draft3.md", "P0-POWER-LIST.rev3.patch.md", "L4-DESK-GATE-ASSESSMENT.draft.md",
          "L4-DESK-GATE-ASSESSMENT.draft2.md")

W26 = "b7769c8cf9039683872a997d32acccc4d08264da"           # fnd/adopt30a's tip: RESULT.md and CLASSIFICATION.md adopted
W27_P0 = "28b7043f2c3e0505106ab7a69d719ce7a81bedd0"        # fnd/adopt30b: the P0 list's revision 3, revision 2 kept dated
W27_DG = "fc49f616c54a3907bc43252fdcb6baeec8090ff3"        # fnd/adopt30b: the DESK-gate assessment at its final name
# a record the pages cite that this branch does not carry: the adoption branch and the commit that carries it at that path
LANDS_WITH = {RESULT: ("W26, fnd/adopt30a", W26), CLASS: ("W26, fnd/adopt30a", W26),
              DGATE: ("W27, fnd/adopt30b", W27_DG), P0R2: ("W27, fnd/adopt30b", W27_P0)}

GITIGNORED = ("v2/ecad/out/",)                            # START-HERE names it as the gitignored readings folder (H3's text)
# the coordinator's words (Q05-verdict.final.md, its three headings; 6 October 2026, 10:45 CEST), one bullet each
CLAIMS = ("Layer 4's DESK gate: NOT PASSED", "Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
          "Power-design closure: BLOCKED.", "Fabrication release: BLOCKED.")
LIMIT = '"Ready" here means complete and internally consistent as a package of open items, not that any item is resolved.'
DATED = "dated 6 October 2026, 10:45 CEST"
# the integration record's words on what the promoted revision is and is not (RESULT.md at W26: lines 33, 335, 112 and 95)
ISNOT = ("a DESK candidate, not an accepted power design", "Set 30 closes NO power item.",
         "the promoted revision carries 14 UNREVIEWED CHANGES",
         "never as checked, never credited, each owing its own targeted verification before any credit")
RUNS = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "meshsat-fieldkit", "_runs")
Q05 = os.path.join(RUNS, "int30", "Q05-verdict.final.md")
VALUES = os.path.join(RUNS, "int30", "ADOPTION-VALUES.md")

PATH_TOK = re.compile(r"`((?:v2/|records/)[^`\s:]+)(?::(\d+)(?:-(\d+))?)?`")
UNDERS = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
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
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)


def _show(commit, path):
    r = _git("show", "%s:%s" % (commit, path))
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def _exists(p):
    return os.path.exists(os.path.join(ROOT, p))


def landing_error(p, exists=_exists, show=_show, landed=None):
    """None when the path exists in the tree, or is a record that lands with another adoption branch: that branch's commit
    carries it at this path and is not yet in this tree. Otherwise the reason."""
    if exists(p):
        return None
    if p in GITIGNORED and _git("check-ignore", "-q", p).returncode == 0:   # a readings folder the page calls gitignored
        return None
    if p not in LANDS_WITH:
        return "%s does not exist and lands with no adoption branch" % p
    who, sha = LANDS_WITH[p]
    if show(sha, p) is None:
        return "%s does not exist, and %s's commit %s does not carry it (or is not in this checkout)" % (p, who, sha[:8])
    if landed is None:
        landed = _git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0
    if landed:
        return "%s's commit %s is in this tree, but %s is absent" % (who, sha[:8], p)
    return None


def _paths(text):
    return sorted(set(_repo(m.group(1)) for m in PATH_TOK.finditer(text) if "<" not in m.group(1) and "*" not in m.group(1)))


def _placeholder_errors(name, text, n):
    errs = []
    if PLACEHOLDER in text:
        errs.append("%s still carries %s" % (name, PLACEHOLDER))
    for tok in set(UNDERS.findall(text)):
        errs.append("%s carries a placeholder %s" % (name, tok))
    if "(at adoption)" in text:
        errs.append("%s still marks a record (at adoption)" % name)
    if text.count(PROMOTED) != n:
        errs.append("%s names the promoted commit %d times, not %d" % (name, text.count(PROMOTED), n))
    return errs


def _claims_block(text):
    """The list of the four claims: the paragraph naming the assessment and the date, then the four bullets."""
    m = re.search(r"`(?:v2/docs/)?records/l4close/L4-DESK-GATE-ASSESSMENT\.md`, which records the coordinator's judgement on the\n"
                  r"promoted revision, %s:[^\n]*\n[^\n]*\n\n((?:- \"[^\n]+\"\n){4})" % re.escape(DATED), text)
    return [ln[3:-1] for ln in m.group(1).strip("\n").split("\n")] if m else None


def _claims_errors(text):
    got = _claims_block(text)
    if got is None:
        return ["no list of the four claims under the assessment's path and the date"]
    return ["claim %d reads %r, not %r" % (i + 1, g, w) for i, (g, w) in enumerate(zip(got, CLAIMS)) if g != w]


# ------------------------------------------------------------------------------------------------------- the placeholders
def t_every_placeholder_is_filled_with_the_promoted_commit():
    for p in PAGES:
        errs = _placeholder_errors(p, _page(p), FILLED[p])
        assert not errs, errs
    if os.path.exists(VALUES):     # the coordinator's saved value, read where the logs are on this host
        txt = open(VALUES, encoding="utf-8").read()
        assert "INTEGRATED = CANDIDATE = PROMOTED = MIRROR (GitHub main): %s" % PROMOTED in txt, "the values file names another commit"
    assert _git("cat-file", "-e", PROMOTED + "^{commit}").returncode == 0, "%s is not in this checkout" % PROMOTED[:8]
    assert _git("merge-base", "--is-ancestor", PROMOTED, "HEAD").returncode == 0, "the promoted commit is not in this tree"


def t_the_revision_rows_name_the_promoted_commit():
    for p in PAGES:
        t = _page(p)
        for label in ("Tested", "Packaged"):
            assert re.search(r"^\| %s \| `%s` \|" % (label, PROMOTED), t, re.M), "%s: the %s row is not the promoted commit" % (p, label)
        assert "| Documents and editable artifacts | on main as a DESK candidate (`%s`) |" % PROMOTED in t, p


# ------------------------------------------------------------------------------------------------------------ the paths
def t_every_cited_path_exists_or_lands_with_its_adoption_branch():
    for p in PAGES:
        bad = [e for e in (landing_error(q) for q in _paths(_page(p))) if e]
        assert not bad, "%s: %s" % (p, bad)


def t_the_final_paths_are_cited_and_no_draft_path():
    for p in PAGES:
        t = _page(p)
        named = _paths(t)
        for f in FINAL:
            assert f in named, "%s does not cite %s" % (p, f)
        for d in DRAFTS:
            assert d not in t, "%s still cites the draft %s" % (p, d)


def t_the_p0_list_the_pages_call_revision_3_is_revision_3():
    for p in PAGES:
        assert re.search(r"revision 3, adopted on 6 October 2026", _page(p)), "%s does not call the P0 list revision 3" % p
    head = open(os.path.join(ROOT, P0), encoding="utf-8").readline()
    if "(revision 3" in head:
        return
    at = _show(W27_P0, P0)
    assert at is not None and "(revision 3" in at.split("\n")[0], "the P0 list is not revision 3 here or at W27's commit"
    assert _git("merge-base", "--is-ancestor", W27_P0, "HEAD").returncode != 0, "W27's commit is in the tree, its revision 3 is not"


# ------------------------------------------------------------------------------------------------------------ the words
def t_the_four_claims_stand_in_the_coordinators_words():
    for p in PAGES:
        errs = _claims_errors(_page(p))
        assert not errs, "%s: %s" % (p, errs)
        assert _norm(LIMIT) in _norm(_page(p)), "%s lacks the readiness word's limit" % p
    if os.path.exists(Q05):        # the coordinator's file, read where the logs are on this host
        q = open(Q05, encoding="utf-8").read()
        for w in CLAIMS + (LIMIT,):
            assert w in q, "the verdict file does not read %r" % w
    if os.path.exists(os.path.join(ROOT, DGATE)):   # once the assessment is in the tree it carries the words the pages cite it for
        a = _norm(open(os.path.join(ROOT, DGATE), encoding="utf-8").read())
        miss = [w for w in CLAIMS if _norm(w) not in a]
        assert not miss, "%s does not carry the coordinator's words %s" % (DGATE, miss)


def t_what_the_promoted_revision_is_and_is_not_in_results_words():
    src = open(os.path.join(ROOT, RESULT), encoding="utf-8").read() if os.path.exists(os.path.join(ROOT, RESULT)) else _show(W26, RESULT)
    assert src is not None, "RESULT.md is neither in the tree nor at W26's commit"
    src = _norm(src)
    assert _norm(LIMIT) in src, "RESULT.md does not quote the readiness word's limit"
    for p in PAGES:
        t = _norm(_page(p))
        assert "in the integration record's words" in t, "%s does not attribute the words to RESULT.md" % p
        for w in ISNOT:
            assert _norm(w) in t, "%s lacks %r" % (p, w)
            assert _norm(w) in src, "RESULT.md does not read %r" % w


def t_no_em_or_en_dash():
    for p in list(PAGES) + [os.path.relpath(os.path.abspath(__file__), ROOT)]:
        s = open(os.path.join(ROOT, p), encoding="utf-8").read()
        assert not any(d in s for d in DASHES), "a dash in %s" % p


# ----------------------------------------------------------------------------- the checkers refuse what they are for
def t_the_checkers_refuse_their_defects():
    good = "`%s` and `%s`" % (PROMOTED, PROMOTED)
    assert not _placeholder_errors("a", good, 2)
    for bad, words in ((good + " `__INTEGRATED__`", "still carries"), (good + " `__PROMOTED__`", "a placeholder"),
                       (good + " `records/int30/RESULT.md` (at adoption)", "(at adoption)"), ("`%s`" % PROMOTED, "1 times")):
        errs = _placeholder_errors("a", bad, 2)
        assert any(words in e for e in errs), (bad, errs)
    # an absent path: refused unless an adoption branch carries it and has not landed
    no = lambda q: False  # noqa: E731
    assert "lands with no adoption branch" in landing_error("v2/docs/NOPE.md", exists=no)
    assert landing_error(RESULT, exists=no, show=lambda c, q: "x", landed=False) is None
    assert "does not carry it" in landing_error(RESULT, exists=no, show=lambda c, q: None, landed=False)
    assert "is in this tree" in landing_error(RESULT, exists=no, show=lambda c, q: "x", landed=True)
    # the claims: the real block passes, a changed word, a dropped claim and a missing date each fail
    block = ("`records/l4close/L4-DESK-GATE-ASSESSMENT.md`, which records the coordinator's judgement on the\npromoted revision, "
             "%s: the gate\nand more:\n\n%s\n" % (DATED, "\n".join('- "%s"' % c for c in CLAIMS)))
    assert not _claims_errors(block)
    assert _claims_errors(block.replace("NOT PASSED", "PASSED"))
    assert _claims_errors(block.replace('- "Fabrication release: BLOCKED."\n', ""))
    assert _claims_errors(block.replace(DATED, "dated 6 October 2026"))
    assert _claims_errors(block.replace("READY AS A DESK PACKAGE OF OPEN ITEMS", "READY"))


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
