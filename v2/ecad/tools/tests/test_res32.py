#!/usr/bin/env python3
"""Set 32's result record (MESHSAT-1357, 6 October 2026, W44; restated by W73 from 20:23 CEST over the five branches set 32's chain
pins): `v2/docs/records/int32/RESULT.md` and its classification `CLASSIFICATION.md` hold what they type.

The basis of each predicate (W73's restatement): every row's sha, date, subject and file count is compared with git over the five
ranges in the chain's merge order (each range's base is its merge base with set 31's lineage tip aa332280, or for fnd/s32attr with
fnd/w34pdftext's tip, which the chain merges first); the declared tokens are the fill tool's, `_bin/fill_res.py` (W76's generalisation
of set 31's `_runs/int31/freeze/fill_res31.py`, the same TOK pattern; W79's N3), without the name INTEGRATED, which it fills only inside
quoted subjects, so the tool fills set 32 (the runner pass reads the tool and compares), and set 31's promoted revision is the PROMOTED
token in section 1's BASE row alone; the class counts are recomputed from the table; row 14's carried change names a source row
that set 30's adopted record classes REVIEWED-INPUT CHANGED; the chain's pinned merges are the five ranges' branches, each pin inside
its range (fnd/res32's own later commits are placeholder row 31's).

W78's restatement (6 October 2026, from 21:03 CEST, on W75's independent read and the coordinator's ruling on its F2): the dates are
git's AUTHOR dates (`%ad`, the one that matches git on all 30 rows; row 2's committer date differs, W75's F5) and the record says so;
row 15 is REVIEWED-INPUT CHANGED by the ruling (it quotes row 14's restated words into two test files of cx46's delta), so a carried
change may name this table's own REVIEWED-INPUT CHANGED row as its source (row 15: row 14) as well as set 30's; the two wider readings'
totals are recomputed from the table and the rows they name (W75's F3); every PROMOTED line but the BASE row names set 32 (F9); row 31
carries no token (F11); the record's statement of the fill tool's template counts equals the tokens in the two files; the 21 are file
touches and the 16 distinct files (F8); the fill tool read is `_bin/fill_res.py` (W76), its TOK and its set 32 file list read with ast.

W80's restatement (6 October 2026, from 21:30 CEST, on W79's N4 and condition C3, as W69 did for set 31 from W68's F1): the test holds
at three stages, which it reads from RESULT's section 1 (the five role rows: BASE, the re-key's cache commit, the candidate, set 32's
promotion, the adoption): stage 0, every role row its token; stage 1, after the fill tool's first run (`fill_res.py --set 32 ... --apply`),
the four commits named and ADOPTION its token (DEFER); stage 2, after its second run, all five named; any other mix is a partial fill and
refused. The unclassified rows are 31 (text, no token), 32 and 33: a sha cell of ONE code span holding the token or the commit the fill
wrote (a classified row's is `short` / `full`), date and class "not determined", never counted. A filled commit must stand where its role
puts it (p_filled): set 31's promoted revision follows set 31's lineage tip LINEAGE on the first-parent line; the re-key's cache commit
follows it there and holds the five branch tips; the candidate follows the re-key there; set 32's promotion is the candidate (main
fast-forwarded to it); the adoption descends from the candidate; rows 32 and 33 name the same values as RESULT's re-key and candidate
rows. Only commits that pass are accepted as named commits. The PROMOTED rule of W75's F9 holds on the filled commits too (set 32's
promotion only on lines naming set 32, set 31's only on lines naming set 31), and section 8's template statement is compared with the
files before the fill and, after it, with the newest committed revision of RESULT.md that still holds the tokens (git). The mutations
whose anchor was a token the fill removes use anchors that stay, or the cell the stage holds; each refuses at every stage. W79's N1
(p_alternatives reads which rows carry which row's change) and N2 (p_carried: a REVIEWED-INPUT CHANGED row without the second sentence's
source must carry the first sentence's old and new value and its cx46 item) are added, each with the mutant W79 found passing.

W85's restatement (6 October 2026, from 22:26 CEST, queue item Q-104, after the coordinator moved the chain's pin SRC_PDFTEXT to W81's
62300318): fnd/w34pdftext's range is aed4bd23..62300318 (17 commits); W81's four commits after W73's tip b397aada are rows 13.1 to 13.4
(DOTTED: numbered after row 13 so that no later row moves, as set 31's rows 3.4 and 3.5), so _order() numbers them so and the row lists
of the wider readings read dotted rows (_nums, _rk); fnd/s32attr's base is its merge base with the new tip (still 5b3153aa). The counts
follow from git as before. p_counts separates the three declaration-only modules W81 added (l5r4_pdftext.py, l8p_pdftext.py,
l8r2_pdftext.py: a module docstring and a PDFTEXT dict and nothing else, read with ast) from the 26 converted generators, whose count it
still requires; it reads the committed texts at the tip (176 with 176 sidecars) and at W34_TIP (b397aada: 171, the count W34's rows
gave and the inventory's totals line states with its bytes), and section 9's "and 176 committed (171 before)" at the tip.

W95's restatement (6 October 2026, from 23:35 CEST): the record names its patch file `int32/ENTRY-PAGES.patch.md` (the rows for the four
adoption pages, held by test_patch32), so the fill tool's template covers it; section 8's template statement counts it as a third
file (p_placeholders, and _template_texts reads it at the template's commit). Nothing else here changes.

W113's restatement (7 October 2026, from 01:43 CEST, on W109's F2 to F4 and W110's C1): the record names the chain's base, main's tip
at the run's start (CHAIN_BASE, be07863b, the chain's log's first line), apart from its BASE row (set 31's promoted revision); the
chain's base is declared in OUTSIDE (it is in no history this record's branch reads until main is merged), and a mutant naming a
commit that is neither is refused. W110's B2: p_filled read "the re-key's cache commit follows BASE on the first-parent line", which
no true re-key meets on the lineage the chain builds (set 31's promoted revision is a second parent of main's merge of set 31's
adoption, never on main's first-parent line); restated: BASE is an ancestor of the re-key's cache commit and of the chain's base, and
the chain's base is on the re-key's first-parent line before it (a mutant naming the chain's base itself as the re-key is refused).

W128's restatement (7 October 2026, from 03:44 CEST, on W109's phase 2 finding 4, `<worktrees>/_runs/claude/w109read32/
REPORT-PHASE2A-AS-RECEIVED.md`, and the coordinator's ruling on W110's N3): the coordinator merged fnd/l3r5keep (W114's restoration of
test_l3r5.py and the inventory's note) after C1, so the record names commits that are in no history this branch reads until the
adoption: OUTSIDE declares them (the lineage after the five merges, C1, the two commits and their merge; never C1b, which did not exist
when the rows were written). The two commits are the integration's rows 31.7.1 and 31.7.2, written in full from git in section 3 under
their merge's row 31.7 and not in section 1, whose five ranges, counts and the pages' branch-only count (test_patch32) stay as they
are; p_prepared reads them back as p_columns reads section 1's rows (sha, author date, subject, file count, the fixed classes, the
branch, UNREVIEWED since cx46 where a file of cx46's delta is touched), checks that they are exactly the commits the merge brings from
its second parent (git rev-list), and that they follow the merge's row, which names them. No existing predicate changes.

W154's restatement (7 October 2026, from 10:09 CEST, queue item Q-176, on W132's condition 2, `<worktrees>/_runs/claude/
w132rechkadopt/REPORT-FULL-AS-RECEIVED.md`; the NEXT line of both records): the classification's row 31 is replaced, before the
adoption, by the integration's rows written from git (rows 31.1 to 31.9.1), and rows 32 and 33 carry git's date, subject, files and a
class while their sha cells keep the fill tool's tokens. The basis of each changed expectation: (1) _real() reads the branch rows alone
(the rows of the five ranges; the integration's rows 31.x are read by p_integ), because the branch counts, the bound statement and the
four pages' "34 commits of its five branches" stay over the branch commits (test_patch32), so p_coverage, p_summary, p_counts,
p_row_numbers, p_carried and p_alternatives keep their scope; (2) p_integration_rows: the rows whose sha cell is one code span are rows
32 and 33 alone, ending the table after the rows 31.x, no row 31 left (W80's "31, 32 and 33" with row 31's "not determined" no longer
holds: row 31 is gone); (3) p_placeholders: rows 32 and 33 carry a date and a class of the fixed set (W80's "not determined" held while
no commit existed; the commits are C3 and C4, REKEY_AT and CAND_AT below), and no row 31.x carries a token; (4) p_integ (new): the
integration's rows are git's, row for row: the first-parent commits of CHAIN_BASE..INTEG_TIP oldest first as 31.1 onward, after each
merge the commits its second parent brings that no branch range holds (31.<n>.<k>, their branch named by the merge's subject), then
REKEY_AT (32, its first parent INTEG_TIP) and CAND_AT (33, its first parent REKEY_AT); each row's sha (rows 32 and 33: the token, or
after the fill the same commit), author date, subject, branch, file count against the first parent, fixed classes, MERGE exactly on
two-parent commits, UNREVIEWED since cx46 with the count of cx46's files where it touches any, a REVIEWED-INPUT CHANGED row classed by
the second sentence with its source rows (earlier rows of this table or set 31's) and the delta membership, and a merge naming the first
row it brings; (5) p_integ_summary (new): section 2's integration table, touching rows, file touches and whole-table count are the
rows'; (6) p_nofill (new): no fill-in cell is left in either record; (7) OUTSIDE declares the integration's commits that are not in this
branch's history until the adoption merges the candidate, and p_commits_named reads fnd/res32 as merged at row 31.4 (RES32_MERGED, in
this branch's history). Each new predicate has mutants it refuses; the old mutants anchored on row 31 are restated on rows 31.x.

What fails here: a commit of set 32's five branch ranges missing, doubled or out of order; a short sha that is not its full sha's prefix; a
date, subject or file count that is not git's; a class outside W39's fixed set; a row that touches a file cx46 read without the words
"UNREVIEWED since cx46"; a REVIEWED-INPUT CHANGED row that touches no file of the reviewed tree (present at 4d0ff8a2), or one that
touches none of cx46's delta without classing a carried change with its source row and the delta membership; a rule paragraph that is not
set 30's line 11 verbatim (`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`, read as the coordinator ruled on 6 October 2026,
reading A), or that drops set 30's row 44 as the precedent, the wider reading's answer or the placeholder rows' note; summary counts, per-branch counts or the bound statement's
numbers that are not the table's; a count typed in the records that is not git's; a commit named that is in no history this record
reads; a quote that is not on its cited line at its revision; the three claims not quoted verbatim from the assessment; a placeholder
outside the five tokens fill_res.py fills; a PROMOTED line other than the BASE row that does not name set 32; a token in a row 31.x;
an integration row that is not git's or a fill-in cell left (W154); a
template count that is not the files'; a wider reading's totals that are not the table's; an em or en dash. Each predicate is also run on
a mutant it must refuse.

The coordinator's files (`<worktrees>/_runs`, outside the repository) are read by ONE test, which raises Skip where they are absent (a
rented box): run it in the runner pass (the record's section 8); so does the fill tool's test (`<worktrees>/_bin/fill_res.py`). The five branch tips below are the ones
the record read; a commit a branch gains later is outside these ranges, so the coordinator adds its row and moves the tip here at the
adoption.

Read-only: git is read with `git log`, `git show`, `git diff`, `git rev-list`, `git merge-base`, `git ls-tree` and `git cat-file`;
nothing is written. No pytest is needed (tests/run.py runs the `t_` functions); `test_` aliases let pytest collect them."""
import ast
import os
import re
import subprocess
from collections import Counter

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = "v2/docs/records/int32"
RESULT = REC + "/RESULT.md"
CLASS = REC + "/CLASSIFICATION.md"
PATCH = REC + "/ENTRY-PAGES.patch.md"     # W95: the rows for the four adoption pages, named by RESULT so the fill tool reaches them
LINEAGE = "aa3322806da156d12f2b23dbe9fc98a8805926f0"         # set 31's lineage tip as W73 read it (fnd/int31regen, the re-key's cache)
ASSESS_AT = "3057ae43f4fb7fc5e3d6282ce52d448c8ee27929"       # the revision the three claims are quoted at (an ancestor of LINEAGE)
# (branch, base, tip, against): base = git merge-base <against> <tip>; the chain's merge order (_runs/int32/chain.sh, steps a2 to a3c)
BRANCHES = (("fnd/w34pdftext", "aed4bd234644c80fa494299b21099acf6d2454c1", "62300318cbf256a178659d7635ecfd4a318c47d3", LINEAGE),
            ("fnd/s32attr", "5b3153aa4136f08ab186a2b5da53c1c4f0c3ecac", "9210ab541e8144af530f928c1da98b96f90c89fd",
             "62300318cbf256a178659d7635ecfd4a318c47d3"),
            ("fnd/s32small", "eff28be3b80f882db545a849b0da1def0217f63d", "7b7219a7d0a695b6b866435116905964a68f5578", LINEAGE),
            ("fnd/res32", "3057ae43f4fb7fc5e3d6282ce52d448c8ee27929", "7ae6175814b7824b3a9f69357ec75e9810a41da4", LINEAGE),
            ("fnd/l4e7cache", "31928583c612ea43df17df5d7e0cbb2f66090f8e", "5ee1e66eb8787a788647305509ae6c2700144d9a", LINEAGE))
# W85: W81's commits after W73's tip of fnd/w34pdftext are rows 13.1 to 13.4: {branch: (the commit after which rows are dotted, the
# row they follow)}; W34_TIP ends W34's to W55's rows (171 committed texts, the inventory's totals line)
W34_TIP = "b397aada17befd8c6ee8be09550a785139c45066"
DOTTED = {"fnd/w34pdftext": (W34_TIP, 13)}
CHAIN_LABELS = {"pdftext": "fnd/w34pdftext", "s32attr": "fnd/s32attr", "s32small": "fnd/s32small", "res32": "fnd/res32",
                "l4e7cache": "fnd/l4e7cache"}                # chain.sh's merge_one labels and the branch each merges
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
CX45 = "06077cee"                                           # the delta cx46 read: git diff 06077cee 4d0ff8a2
L4E9_EXTRA = ("v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md", "v2/docs/records/l4e9/l4e9_power_path.out")
FIXED = ("REVIEWED-INPUT CHANGED", "RECORD TEXT", "GENERATOR DATA (text)", "TEST", "DIGEST RE-PIN", "MERGE", "TOOLING")
DECLARED = ("__REKEY__", "__CANDIDATE__", "__GATE__", "__PROMOTED__", "__ADOPTION__")   # fill_res.py's TOK (W76), INTEGRATED apart
# W113 (W109's F4, W110's B2): the chain's base, main's tip at the chain's start, as its log's first line prints it
# (`<worktrees>/_runs/int32/real-0115.log:1`, `base be07863bbca206a81ab42b9f96a7684c5c10a746`); set 31's promoted revision is the
# record's BASE row (RESULT section 1), an ancestor of this commit but never on main's first-parent line (it is a second parent)
CHAIN_BASE = "be07863bbca206a81ab42b9f96a7684c5c10a746"
# set 31's record draft, named by the record, on fnd/res31: in this branch's history only after set 31's adoption
OUTSIDE = {"4196e9dfbb125cc50b091bdea47a34e432162970": "fnd/res31's tip, set 31's RESULT and CLASSIFICATION drafts (W39)",
           # W78 (W75's F2 and F4): set 31's classification at W75's read and set 31's candidate, after this record's lineage tip
           "f535bbcabab190f2489e168c09caa45fcc6e6d31": "fnd/res31 at W75's read, set 31's CLASSIFICATION with its caveat on row 44",
           "d0e283aa52ceb7f303358862b539161b721475e5": "set 31's candidate, l4e7_p0sol.out's paragraph 0a and its KNOWN ITEM",
           # W102 (W99's B1 and C4): main after set 31's adoption, the pages the patch file's rows are read against with the pins
           "ad757edb1be7e0fe3b586f986d2d704c9836fdcf": "main after set 31's adoption (the fill's second run), set 32's integration base",
           # W113 (W109's F4, W110's C1 and B2): the chain's base, main's tip at the run's start (_runs/int32/real-0115.log:1), a
           # descendant of set 31's promoted revision (the record's BASE row): named in RESULT's section 3b and the classification's bounds
           CHAIN_BASE: "main's tip at set 32's chain's start, the chain's base (W100's S1, W104)",
           # W128 (W109's phase 2 finding 4): the commits after the chain's stop that the record names, on fnd/int32's lineage and in no
           # history this branch reads until the adoption merges the candidate (`<worktrees>/_runs/int30/QUEUE.md`, entries "03:23:27
           # (clock) C1 COMMITTED on fnd/int32" and "03:23:37 (clock) fnd/l3r5keep 5a0aacd9 MERGED into fnd/int32"): the lineage after the
           # five merges (fnd/l3r5keep's base), C1, fnd/l3r5keep's two commits and the coordinator's merge of them. C1b is not here: it
           # did not exist when W128 wrote the rows, and the record names it only as a [FILL]
           "258e9a7d3a5ad95c0130d4ead3aa295ffd694d5a": "fnd/int32 after the five merges (step a3c), fnd/l3r5keep's base",
           "ed17ac0499269fbe9174ce368fddd66e2ae0daa3": "C1, the chain's converged outputs (CLASSIFICATION row 31.6)",
           "2dcb41313bbef9b2f76cab344926c81e8d7e23c7": "fnd/l3r5keep, W114: test_l3r5.py at its reviewed content (row 31.7.1)",
           "5a0aacd968746e18285fb788ae39fcad0ba16599": "fnd/l3r5keep, the coordinator: the inventory's note (row 31.7.2)",
           "4c8196a00fa5f629a049bb2e803cb47814992e60": "the coordinator's merge of fnd/l3r5keep after C1 (row 31.7)",
           # W154 (Q-176, W132's condition 2): the integration's first-parent commits, the commit the last merge brings, the re-key's
           # cache commit and the candidate, written as rows 31.1 to 33 from git before the adoption (`<worktrees>/_runs/int30/QUEUE.md`,
           # entries "04:37:48 (clock) C1b COMMITTED", "04:43:29 (clock) fnd/s32applier MERGED", "07:10:53 (clock) C3", "09:30:37 (clock) C4")
           "834c86ae332d788da41ee10edfb14764a8e91ad5": "the chain's merge of fnd/w34pdftext (row 31.1)",
           "19649d37f0190697227120c131dbb9ac16c2a0e0": "the chain's merge of fnd/s32attr (row 31.2)",
           "d1f6a2205ea0345d2404c3e9f89d262b1781af05": "the chain's merge of fnd/s32small (row 31.3)",
           "4f021464b524a359f6a77e785a93fa7096ef9885": "the chain's merge of fnd/res32 (row 31.4)",
           "1d177f6b01df13f7f6ac09be4896194efb4f26c5": "C1b, the L4 pin chain and the targeted pass on r1's moves (row 31.8)",
           "06d064ffa58a1211139d0f1d8e7b536675a67948": "the coordinator's merge of fnd/s32applier, C2 (row 31.9)",
           "c205ff65636e914ef26c87eca3209ea4c7d096de": "fnd/s32applier, W134: test_applier_state's fixture (row 31.9.1)",
           "a598ada042acf35a1af59818a6ebdd26192e7996": "the re-key's cache commit C3 (row 32)",
           "f08e396175dd418434061d731e08111d006d6efa": "set 32's candidate C4 (row 33)",
           # W154: fnd/adopt32 at W128's tip, the baseline of W154's template comparison (RESULT section 8)
           "2766847182980fe48f32e63ace253463cdde4c74": "fnd/adopt32 at W128's tip (RESULT section 8, W154's template baseline)"}
# W154: the integration's rows read from git (p_integ): the first-parent line from CHAIN_BASE to INTEG_TIP (C2, the last commit before the
# re-key), then REKEY_AT (C3) and CAND_AT (C4) as rows 32 and 33; RES32_MERGED is fnd/res32 as the chain merged it (row 31.4)
INTEG_TIP = "06d064ffa58a1211139d0f1d8e7b536675a67948"
REKEY_AT = "a598ada042acf35a1af59818a6ebdd26192e7996"
CAND_AT = "f08e396175dd418434061d731e08111d006d6efa"
RES32_MERGED = "607cd15726c39b6077de414b806b2a4c22ca6653"
INTEG_ROW = re.compile(r"31(?:\.\d+)+")
# W128 (W109's phase 2 finding 4): the integration's rows written in full from git before the adoption, outside the five ranges: the
# commits fnd/l3r5keep brings at the coordinator's merge after C1 (section 3, under that merge's row 31.7; section 1 once section 3
# moves there), each (row, commit, the branch cell's start); L3R5_MERGE is the merge whose second parent's commits they are
PREPARED = (("31.7.1", "2dcb41313bbef9b2f76cab344926c81e8d7e23c7", "fnd/l3r5keep ("),
            ("31.7.2", "5a0aacd968746e18285fb788ae39fcad0ba16599", "fnd/l3r5keep ("))
L3R5_MERGE = "4c8196a00fa5f629a049bb2e803cb47814992e60"
ASSESS = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
S30 = "eff28be3b80f882db545a849b0da1def0217f63d"              # set 30's adopted classification, its rule at line 11
S30C = "v2/docs/records/int30/CLASSIFICATION.md"
RIC = "REVIEWED-INPUT CHANGED"
CLAIMS = {492: "### Layer 4's DESK gate: NOT PASSED",
          496: "### Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS",
          500: "### Power-design closure: BLOCKED. Fabrication release: BLOCKED."}

GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
RUN_ANCHOR = re.compile(r"`<worktrees>/_runs/([^`:\s]+)(?::(\d+))?`(?:, entry \"([^\"]+)\",)? `([^`]+)`")
RUN_PATH = re.compile(r"`(?:<worktrees>/)?_runs/([\w./-]+\.(?:log|md|txt|sh|tsv))")
HEXTOK = re.compile(r"`([0-9a-f]{7,40})`")
PH = re.compile(r"__[A-Z0-9]+(?:_[A-Z0-9]+)*__")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
DASHES = ("\u2014", "\u2013")


def _git(*args):
    env = dict(os.environ, TZ="Europe/Amsterdam")
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True, env=env)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def _has(sha):
    try:
        r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    return r.returncode == 0


def _need_git():
    for sha in (LINEAGE, ASSESS_AT, REVIEWED) + tuple(b[1] for b in BRANCHES) + tuple(b[2] for b in BRANCHES):
        if not _has(sha):
            raise Skip("commit %s is not in this checkout" % sha[:8])


def _read(rel):
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        raise AssertionError("%s is missing" % rel)
    return open(p, encoding="utf-8").read()


_C = {}


def _show(rev, path):
    k = (rev, path)
    if k not in _C:
        _C[k] = _git("show", "%s:%s" % (rev, path)).split("\n")
    return _C[k]


def _order():
    """[(row number, branch, full sha, parents, date, subject, names)]: each branch's range oldest first, in the chain's merge order."""
    if "order" in _C:
        return _C["order"]
    _need_git()
    out = []
    n = 0
    for name, base, tip, _against in BRANCHES:
        dot = DOTTED.get(name)
        after = set(_git("rev-list", "%s..%s" % (dot[0], tip)).split()) if dot else set()
        k = 0
        for c in _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (base, tip)).split():
            if c in after:             # W85: a dotted row follows its anchor's row; the anchor must be that row
                k += 1
                num = "%d.%d" % (n, k) if n == dot[1] else "%d+%d" % (n, k)
            else:
                n += 1
                num = str(n)
            ps = _git("rev-list", "--parents", "-n1", c).split()[1:]
            date, subj = _git("log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%ad%x09%s", c).rstrip("\n").split("\t", 1)
            names = _git("show", "--name-only", "--format=", c).split()
            out.append((num, name, c, ps, date, subj, names))
    _C["order"] = out
    return out


def _reviewed():
    if "rev" not in _C:
        _C["rev"] = set(_git("diff", "--name-only", CX45, REVIEWED).split()) | set(L4E9_EXTRA)
    return _C["rev"]


def _tree():
    """The files present at cx46's candidate: "a file of the reviewed tree" in set 30's rule."""
    if "tree" not in _C:
        _C["tree"] = set(_git("ls-tree", "-r", "--name-only", REVIEWED).split("\n")) - {""}
    return _C["tree"]


def _rows(text):
    sec = text.split("## 1. ", 1)[1].split("\n## 2. ", 1)[0]
    rows = []
    for line in sec.split("\n"):
        if not line.startswith("| ") or line.startswith("| # ") or line.startswith("|---"):
            continue
        rows.append([c.strip() for c in CELL_SPLIT.split(line.strip())[1:-1]])
    return rows


def _sha_cell(cells):
    m = re.match(r"`([0-9a-f]{8})` / `([0-9a-f]{40})`$", cells[1])
    return m.groups() if m else None


def _classes(cells):
    return [c.strip() for c in cells[6].split(" + ")]


PH_CELL = re.compile(r"`(__[A-Z0-9]+(?:_[A-Z0-9]+)*__|[0-9a-f]{8,40})`$")


def _placeholder_row(cells):
    """A row of the integration's commits that the table does not classify (W80, on W79's N4): its sha cell ONE code span holding a
    token the fill fills or the commit it wrote there (a classified row's sha cell is `short` / `full`), or (row 31, several commits;
    W75's F11) the words 'not determined'. Its date and class read "not determined" (p_placeholders); p_integration_rows says which."""
    return bool(PH_CELL.match(cells[1])) or cells[1] == "not determined"


def _real(text):
    """The branch rows: section 1's rows of the five ranges (W154: the integration's rows 31.x are read by p_integ, so the branch counts
    and the bound statement keep their scope, the 34 branch commits)."""
    return [c for c in _rows(text) if not _placeholder_row(c) and not INTEG_ROW.fullmatch(c[0])]


# the integration's rows whose sha cell is the fill tool's token: (row, the token before the fill, the RESULT role that names the same
# value); W154: row 31 ("not determined", W75's F11) is replaced by the rows 31.x written from git, so rows 32 and 33 alone
INTEG = (("32", "__REKEY__", "REKEY"), ("33", "__CANDIDATE__", "CANDIDATE"))
# RESULT's section 1 role rows, by the words before the revision cell (they stay through the fill), and each one's token
ROLES = (("BASE", "| BASE (the REVIEWED role of the brief's form): set 31's promoted revision |", "__PROMOTED__"),
         ("REKEY", "| The re-key's cache commit |", "__REKEY__"),
         ("CANDIDATE", "| INTEGRATED = CANDIDATE: the candidate commit |", "__CANDIDATE__"),
         ("PROMOTED", "| PROMOTED: main after the fast-forward, set 32's promotion |", "__PROMOTED__"),
         ("ADOPTION", "| ADOPTED: the commit that adopts this record |", "__ADOPTION__"))


def _roles(result):
    """{role: the code span's content in its revision cell (the token or a commit)}, or a list of problems."""
    sec = result.split("\n## 1. ", 1)[1].split("\n## 2. ", 1)[0] if "\n## 1. " in result else ""
    out, bad = {}, []
    for role, words, tok in ROLES:
        ls = [l for l in sec.split("\n") if l.startswith(words)]
        if len(ls) != 1:
            bad.append("section 1 has %d rows %r, not one" % (len(ls), words[:50]))
            continue
        cell = CELL_SPLIT.split(ls[0].strip())[2].strip()
        m = PH_CELL.match(cell)
        if not m or (m.group(1).startswith("__") and m.group(1) != tok):
            bad.append("the %s row's revision cell %r is neither %s nor one commit" % (role, cell[:40], tok))
            continue
        out[role] = m.group(1)
    return bad or out


def _stage(result):
    """0 before the fill (every role its token), 1 after its first run (ADOPTION deferred), 2 after its second; None otherwise."""
    r = _roles(result)
    if isinstance(r, list):
        return None
    filled = tuple(not r[k].startswith("__") for k in ("BASE", "REKEY", "CANDIDATE", "PROMOTED", "ADOPTION"))
    return {(False,) * 5: 0, (True,) * 4 + (False,): 1, (True,) * 5: 2}.get(filled)


def _full(sha):
    return _git("rev-parse", "--verify", sha + "^{commit}").strip() if _has(sha) else None


def _fp(sha):
    return _git("rev-list", "--first-parent", sha).split()


def p_filled(texts):
    """W80: each commit the fill wrote stands where its role puts it (stage 1 and 2); before the fill (stage 0) every role is its token."""
    r = _roles(texts[RESULT])
    if isinstance(r, list):
        return r
    st = _stage(texts[RESULT])
    if st is None:
        return ["a partial fill: the role rows %s" % ", ".join("%s %s" % (k, v[:12]) for k, v in r.items())]
    if st == 0:
        return []
    bad = []
    f = {k: _full(v) for k, v in r.items() if not v.startswith("__")}
    for k, v in f.items():
        if not v:
            bad.append("the %s row names %s, not a commit of this repository" % (k, r[k]))
    if bad:
        return bad
    if f["BASE"] == LINEAGE or LINEAGE not in _fp(f["BASE"]):
        bad.append("BASE %s does not follow set 31's lineage tip %s on the first-parent line" % (r["BASE"], LINEAGE[:8]))
    # W113 (W110's B2): set 32's chain runs on main's tip at its start (CHAIN_BASE), whose first-parent line never holds set 31's
    # promoted revision (a second parent of main's merge of set 31's adoption): BASE must be an ancestor of the re-key's cache commit
    # and of the chain's base, and the chain's base must be on the re-key's first-parent line, before it
    anc = lambda a, b: subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", a, b], capture_output=True).returncode == 0
    if f["REKEY"] == f["BASE"] or not anc(f["BASE"], f["REKEY"]):
        bad.append("the re-key's cache commit %s does not descend from BASE %s" % (r["REKEY"], r["BASE"]))
    if not _has(CHAIN_BASE) or not anc(f["BASE"], CHAIN_BASE):
        bad.append("the chain's base %s is absent or does not descend from BASE %s" % (CHAIN_BASE[:8], r["BASE"]))
    elif f["REKEY"] == CHAIN_BASE or CHAIN_BASE not in _fp(f["REKEY"]):
        bad.append("the re-key's cache commit %s does not follow the chain's base %s on the first-parent line" % (r["REKEY"], CHAIN_BASE[:8]))
    for b in BRANCHES:
        if subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", b[2], f["REKEY"]], capture_output=True).returncode:
            bad.append("the re-key's cache commit %s does not hold %s's tip %s" % (r["REKEY"], b[0], b[2][:8]))
    if f["CANDIDATE"] == f["REKEY"] or f["REKEY"] not in _fp(f["CANDIDATE"]):
        bad.append("the candidate %s does not follow the re-key's cache commit on the first-parent line" % r["CANDIDATE"])
    if f["PROMOTED"] != f["CANDIDATE"]:
        bad.append("set 32's promotion %s is not the candidate (main fast-forwarded to it)" % r["PROMOTED"])
    if st == 2 and (f["ADOPTION"] == f["CANDIDATE"] or subprocess.run(
            ["git", "-C", REPO, "merge-base", "--is-ancestor", f["CANDIDATE"], f["ADOPTION"]], capture_output=True).returncode):
        bad.append("the adoption commit %s does not descend from the candidate" % r["ADOPTION"])
    return bad


def _accepted(texts):
    """The full shas of the role commits p_filled accepts (none before the fill or when it refuses)."""
    r = _roles(texts[RESULT])
    if isinstance(r, list) or not _stage(texts[RESULT]) or p_filled(texts):
        return set()
    return {_full(v) for v in r.values() if not v.startswith("__")}


def p_integration_rows(texts):
    """W80 (W69's p_candidate_row for set 31), restated by W154: the rows whose sha cell is one code span are rows 32 and 33 alone, after
    the integration's rows 31.x (row 31 itself replaced by them); rows 32 and 33 hold their token before the fill and the commit
    RESULT's re-key and candidate rows name after it (p_filled places those commits on the lineage; p_integ reads their other cells)."""
    bad = []
    rows = _rows(texts[CLASS])
    ph = [c for c in rows if _placeholder_row(c)]
    # W154: rows 32 and 33 alone hold one code span (or 'not determined') in their sha cell, and end the table after the rows 31.x
    if [c[0] for c in ph] != [i[0] for i in INTEG]:
        return ["the rows whose sha cell is one code span or 'not determined' are %s, not rows 32 and 33" % [c[0] for c in ph]]
    nums = [c[0] for c in rows]
    if "31" in nums or nums[-2:] != ["32", "33"] or not INTEG_ROW.fullmatch(nums[-3]):
        bad.append("rows 32 and 33 do not end the table after the integration's rows 31.x, or a row 31 stands: %s" % nums[-4:])
    r = _roles(texts[RESULT])
    for c, (n, tok, role) in zip(ph, INTEG):
        v = PH_CELL.match(c[1])
        v = v.group(1) if v else c[1]
        if v.startswith("__"):
            if v != tok:
                bad.append("row %s's token is %s, not %s" % (n, v, tok))
            if isinstance(r, dict) and r.get(role) != tok:
                bad.append("row %s holds %s while RESULT's %s row names %s" % (n, v, role, r.get(role)))
        elif not isinstance(r, dict) or r.get(role, "").startswith("__") or _full(v) is None or _full(v) != _full(r[role]):
            bad.append("row %s names %s, not the commit RESULT's %s row names" % (n, v, role))
    return bad


def _table_rows(text):
    """W128: every eight-cell row of the file's tables (section 1 and section 3), as cells; row numbers may be dotted or 'prepared'."""
    rows = []
    for line in text.split("\n"):
        if not line.startswith("| ") or line.startswith("| # ") or line.startswith("|---"):
            continue
        c = [x.strip() for x in CELL_SPLIT.split(line.strip())[1:-1]]
        if len(c) == 8 and re.fullmatch(r"\d+(?:\.\d+)*(?: \(prepared\))?", c[0]):
            rows.append(c)
    return rows


def p_prepared(text):
    """W128 (W109's phase 2 finding 4): the rows written in full from git outside the five ranges (PREPARED) hold git's sha, author date,
    subject and file count, a class of the fixed set (no MERGE: each has one parent), their branch, and UNREVIEWED since cx46 with its
    count where they touch a file of cx46's delta (p_columns' rule for section 1's rows); they are exactly the commits L3R5_MERGE brings
    (`git rev-list` from its first parent to its second, oldest first) and follow the merge's row 31.7, which names them."""
    bad = []
    rows = _table_rows(text)
    nums = [c[0] for c in rows]
    by = {c[0]: c for c in rows}
    for n, full, branch in PREPARED:
        c = by.get(n)
        if not c:
            bad.append("row %s is missing" % n)
            continue
        s = _sha_cell(c)
        if not s or s[1] != full or not full.startswith(s[0]):
            bad.append("row %s's sha cell is not `%s` / `%s`" % (n, full[:8], full))
            continue
        if not _has(full):
            raise Skip("commit %s is not in this checkout" % full[:8])
        date, subj = _git("log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%ad%x09%s", full).rstrip("\n").split("\t", 1)
        names = _git("show", "--name-only", "--format=", full).split()
        if c[2] != date:
            bad.append("row %s: date %r is not git's author date %r" % (n, c[2], date))
        if c[3].replace("\\|", "|") != subj:
            bad.append("row %s: the subject is not git's" % n)
        if not c[4].startswith(branch):
            bad.append("row %s: the branch cell does not start %r" % (n, branch))
        m = re.match(r"(\d+):", c[5])
        if not m or int(m.group(1)) != len(names):
            bad.append("row %s: file count %r is not git's %d" % (n, c[5][:12], len(names)))
        cls = _classes(c)
        if any(k not in FIXED for k in cls) or len(set(cls)) != len(cls) or "MERGE" in cls:
            bad.append("row %s: a class outside the fixed set, one twice, or MERGE on a one-parent commit: %s" % (n, cls))
        rv = [x for x in names if x in _reviewed()]
        if rv and ("UNREVIEWED since cx46" not in c[7] or ("(%d):" % len(rv)) not in c[7]):
            bad.append("row %s touches %d file(s) of cx46's delta without UNREVIEWED since cx46 and their count" % (n, len(rv)))
    if _has(L3R5_MERGE):
        p1, p2 = _git("rev-list", "--parents", "-n1", L3R5_MERGE).split()[1:3]
        brought = _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (p1, p2)).split()
        if brought != [p[1] for p in PREPARED]:
            bad.append("the merge %s brings %s, not the prepared rows' %s" % (L3R5_MERGE[:8], [b[:8] for b in brought],
                                                                              [p[1][:8] for p in PREPARED]))
    want = ["31.7"] + [p[0] for p in PREPARED]
    at = [nums.index(x) if x in nums else -1 for x in want]
    if -1 in at or at != sorted(at) or at[-1] - at[0] != len(want) - 1:
        bad.append("rows %s do not follow one another in that order" % want)
    elif "brings rows 31.7.1 and 31.7.2" not in by["31.7"][7]:
        bad.append("the merge's row 31.7 does not name the rows it brings")
    return bad


def _integ_order():
    """W154: the integration's rows from git, [(row, branch, full sha, parents, date, subject, names against the first parent)]: the
    first-parent commits of CHAIN_BASE..INTEG_TIP oldest first as rows 31.1 onward (branch fnd/int32), after each merge the commits its
    second parent brings that no branch range holds as rows 31.<n>.<k> (their branch from the merge's subject, "fnd/<name> <sha> merged"),
    then REKEY_AT (row 32) and CAND_AT (row 33)."""
    if "integ" in _C:
        return _C["integ"]
    for s in (CHAIN_BASE, INTEG_TIP, REKEY_AT, CAND_AT):
        if not _has(s):
            raise Skip("commit %s is not in this checkout" % s[:8])
    ranged = {o[2] for o in _order()}
    out = []

    def one(num, branch, c):
        ps = _git("rev-list", "--parents", "-n1", c).split()[1:]
        date, subj = _git("log", "-1", "--date=format-local:%Y-%m-%d %H:%M:%S", "--format=%ad%x09%s", c).rstrip("\n").split("\t", 1)
        out.append((num, branch, c, ps, date, subj, _git("diff", "--name-only", ps[0], c).split()))
    for i, c in enumerate(_git("rev-list", "--first-parent", "--reverse", "%s..%s" % (CHAIN_BASE, INTEG_TIP)).split(), 1):
        one("31.%d" % i, "fnd/int32", c)
        ps, subj = out[-1][3], out[-1][5]
        if len(ps) > 1:
            m = re.search(r"(fnd/[\w-]+) [0-9a-f]{8} merged", subj)
            brought = [s for s in _git("rev-list", "--topo-order", "--reverse", "%s..%s" % (ps[0], ps[1])).split() if s not in ranged]
            for k, s in enumerate(brought, 1):
                one("31.%d.%d" % (i, k), m.group(1) if m else "(no branch in the merge's subject)", s)
    one("32", "fnd/int32", REKEY_AT)
    one("33", "fnd/int32", CAND_AT)
    _C["integ"] = out
    return out


def p_integ(text):
    """W154 (W132's condition 2): the integration's rows are git's, row for row (_integ_order): sha cells (rows 32 and 33: their token,
    or after the fill the same commit), author dates, subjects, branches, file counts against the first parent, classes of the fixed
    set with MERGE exactly on two-parent commits, UNREVIEWED since cx46 with the count where a file of cx46's delta is touched, a
    REVIEWED-INPUT CHANGED row classed by the second sentence with earlier source rows and the delta membership, a merge naming the
    first row it brings; and the lineage: row 32's first parent the last row 31.x on the first-parent line, row 33's row 32."""
    bad = []
    order = _integ_order()
    got = [c for c in _table_rows(text) if INTEG_ROW.fullmatch(c[0]) or c[0] in ("32", "33")]
    if [c[0] for c in got] != [o[0] for o in order]:
        return ["the integration's rows are %s, not git's %s" % ([c[0] for c in got], [o[0] for o in order])]
    nums = [c[0] for c in _table_rows(text)]
    if _git("rev-list", "--parents", "-n1", REKEY_AT).split()[1:2] != [INTEG_TIP] or \
            _git("rev-list", "--parents", "-n1", CAND_AT).split()[1:2] != [REKEY_AT]:
        bad.append("the re-key's cache commit and the candidate are not the next commits on the first-parent line after %s" % INTEG_TIP[:8])
    for c, (num, branch, full, ps, date, subj, names) in zip(got, order):
        if num in ("32", "33"):
            v = PH_CELL.match(c[1])
            tok = dict((i[0], i[1]) for i in INTEG)[num]
            if not v or (v.group(1).startswith("__") and v.group(1) != tok) or (not v.group(1).startswith("__") and _full(v.group(1)) != full):
                bad.append("row %s's sha cell %r is neither %s nor %s" % (num, c[1][:30], tok, full[:8]))
        else:
            s = _sha_cell(c)
            if not s or s[1] != full or not full.startswith(s[0]):
                bad.append("row %s's sha cell is not `%s` / `%s`" % (num, full[:8], full))
        if c[2] != date:
            bad.append("row %s: date %r is not git's author date %r" % (num, c[2], date))
        if c[3].replace("\\|", "|") != subj:
            bad.append("row %s: the subject is not git's" % num)
        if not c[4].startswith(branch + (": " if branch == "fnd/int32" else " (")):
            bad.append("row %s: the branch cell does not name %s" % (num, branch))
        m = re.match(r"(\d+):", c[5])
        if not m or int(m.group(1)) != len(names):
            bad.append("row %s: file count %r is not git's %d" % (num, c[5][:12], len(names)))
        cls = _classes(c)
        if any(k not in FIXED for k in cls) or len(set(cls)) != len(cls):
            bad.append("row %s: a class outside the fixed set, or one twice: %s" % (num, cls))
        if (cls[0] == "MERGE") != (len(ps) > 1) or ("MERGE" in cls[1:]):
            bad.append("row %s: MERGE and the commit's parents disagree" % num)
        rv = [n for n in names if n in _reviewed()]
        if rv and ("UNREVIEWED since cx46" not in c[7] or ("(%d):" % len(rv)) not in c[7]):
            bad.append("row %s touches %d file(s) of cx46's delta without UNREVIEWED since cx46 and their count" % (num, len(rv)))
        if not rv and "UNREVIEWED since cx46" in c[7]:
            bad.append("row %s says UNREVIEWED since cx46 but touches no file of cx46's delta" % num)
        if cls[0] == RIC:
            src = re.search(r"\(?rows? (\d+(?:\.\d+)*)(?: and (\d+(?:\.\d+)*))? the source rows?", c[7])
            if not [n for n in names if n in _tree()] or "second sentence" not in c[7] or "in the delta cx46 read" not in c[7] or not src:
                bad.append("row %s is %s without the second sentence, its source rows and the delta membership" % (num, RIC))
            elif any(x and (x not in nums or nums.index(x) >= nums.index(num)) for x in src.groups()):
                bad.append("row %s: its source rows %s are not earlier rows of this table" % (num, src.groups()))
        if len(ps) > 1 and any(o[0].startswith(num + ".") for o in order) and \
                not re.search(r"\brows? %s\.1\b" % re.escape(num), c[7]):
            bad.append("the merge's row %s does not name the first row it brings, %s.1" % (num, num))
    return bad


def p_integ_summary(text):
    """W154: section 2's part for the integration's rows is the table's: per class first and carried, the total, the touching rows in
    table order (a row whose sha cell is the fill's token is named by its number), their file touches, and the whole table's count."""
    bad = []
    rows = [c for c in _table_rows(text) if INTEG_ROW.fullmatch(c[0]) or c[0] in ("32", "33")]
    sec = text.split("\n## 2. ", 1)[1]
    if "**The integration's rows**" not in sec or "**Not determined here:**" not in sec:
        return ["section 2 has no part for the integration's rows"]
    part = sec.split("**The integration's rows**", 1)[1].split("**Not determined here:**", 1)[0]
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    for k in FIXED:
        m = re.search(r"^\| `%s` \| (\d+) \| (\d+) \|$" % re.escape(k), part, re.M)
        if not m or int(m.group(1)) != first[k] or int(m.group(2)) != carry[k]:
            bad.append("the integration's summary row of %s is not the table's (%d, %d)" % (k, first[k], carry[k]))
    m = re.search(r"^\| integration total \| (\d+) \|", part, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the integration's total is not the table's %d" % len(rows))
    flat = " ".join(part.split())
    touch = [c for c in rows if "UNREVIEWED since cx46" in c[7]]
    m = re.search(r"\*\*The integration's rows that touch a file cx46 read: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?); "
                  r"(\d+) file touches", flat)
    nft = sum(int(re.search(r"reviewed files it (?:touches|brings) \((\d+)\)", c[7]).group(1)) for c in touch)
    if not m or int(m.group(1)) != len(touch) or int(m.group(3)) != nft:
        bad.append("the integration's touching-rows line is not the table's %d rows and %d file touches" % (len(touch), nft))
    else:
        named = re.findall(r"`([0-9a-f]{8})` \(([\d.]+)\)|row (\d+) \(the candidate", m.group(2))
        want = [((_sha_cell(c) or ("", ""))[0], c[0], "") if _sha_cell(c) else ("", "", c[0]) for c in touch]
        if named != want:
            bad.append("the integration's touching-rows list is not the table's rows in order")
    m = re.search(r"\*\*The whole table:\*\* (\d+) rows, the (\d+) branch rows of the five ranges and the integration's (\d+)\.", flat)
    nb = len(_real(text))
    if not m or (int(m.group(1)), int(m.group(2)), int(m.group(3))) != (nb + len(rows), nb, len(rows)):
        bad.append("the whole table's count is not %d (%d branch rows and %d integration rows)" % (nb + len(rows), nb, len(rows)))
    return bad


def p_nofill(texts):
    """W154 (W132's F2): no fill-in cell of the coordinator's ("[FILL") is left in either record."""
    return ["%s holds %d fill-in cell(s)" % (n, t.count("[FILL")) for n, t in texts.items() if "[FILL" in t]


# ---- predicates: each returns a list of problems (empty when the record holds) ----

def p_hygiene(texts):
    bad = []
    for name, t in texts.items():
        if any(d in t for d in DASHES):
            bad.append("%s carries an em or en dash" % name)
        paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", t) if p.strip()]
        first = paras[1] if len(paras) > 1 else ""
        if not first.startswith("**DONE:**") or "**NOT DONE:**" not in first or "**NEXT:**" not in first:
            bad.append("%s: the paragraph after the title is not the DONE / NOT DONE / NEXT line" % name)
    return bad


def p_placeholders(texts):
    bad = []
    for name, t in texts.items():
        for tok in set(PH.findall(t)):
            if tok not in DECLARED:
                bad.append("%s: %s is not a declared placeholder" % (name, tok))
    # W154: rows 32 and 33 (W80: date and class "not determined" while their commits did not exist) carry git's date and a class of the
    # fixed set since the re-key's cache commit and the candidate exist (p_integ compares them with git)
    for c in _rows(texts[CLASS]):
        if _placeholder_row(c) and (c[2] == "not determined" or any(k not in FIXED for k in _classes(c))):
            bad.append("the token row %s carries no date or a class outside the fixed set" % c[0])
    st = _stage(texts[RESULT])
    if st is None:
        bad.append("the role rows of RESULT's section 1 are neither all tokens, nor all but ADOPTION filled, nor all filled (a partial fill)")
    # PROMOTED stands for set 31's promoted revision only in section 1's BASE row (the fill tool fills it there by its line)
    base = [l for l in texts[RESULT].split("\n") if l.startswith("| BASE ")]
    s31 = [l for l in texts[RESULT].split("\n") if "__PROMOTED__" in l and "set 31's promoted revision" in l]
    if st == 0 and (len(base) != 1 or "`__PROMOTED__`" not in base[0] or s31 != base):
        bad.append("set 31's promoted revision is not section 1's BASE row alone as the PROMOTED token")
    # W80: after the fill no token is left but ADOPTION's (stage 1, in RESULT) or none (stage 2)
    left = {1: Counter({"__ADOPTION__": len(PH.findall(texts[RESULT]))}), 2: Counter()}
    if st in left and (Counter(PH.findall(texts[RESULT]) + PH.findall(texts[CLASS])) != left[st] or (st == 1 and not left[1]["__ADOPTION__"])):
        bad.append("stage %d of the fill leaves %s, not %s" % (st, dict(Counter(PH.findall(texts[RESULT]) + PH.findall(texts[CLASS]))),
                                                            "the ADOPTION token alone in RESULT.md" if st == 1 else "none"))
    if st and len(base) != 1:
        bad.append("RESULT.md has %d BASE rows, not one" % len(base))
    # W78 (W75's F9): every other PROMOTED line names set 32, the rule RESULT's paragraph "Placeholders" states for the fill by its line
    for l in texts[RESULT].split("\n"):
        if "__PROMOTED__" in l and not l.startswith("| BASE ") and "set 32" not in l:
            bad.append("a PROMOTED line other than the BASE row does not name set 32: %r" % l[:80])
    # W80: the same rule on the commits the fill wrote: set 32's promotion only on lines naming set 32, set 31's only on lines naming set 31
    r = _roles(texts[RESULT])
    if st and isinstance(r, dict):
        for role, words in (("PROMOTED", "set 32"), ("BASE", "set 31")):
            full = _full(r[role])
            for l in texts[RESULT].split("\n"):
                named = [t for t in HEXTOK.findall(l) if len(t) in (8, 40) and full and full.startswith(t)]
                if named and words not in l:
                    bad.append("a line naming the %s commit %s does not name %s: %r" % (role, r[role], words, l[:80]))
    # W78 (W75's F11): row 31 stood for several commits, so no single value a fill could type: no token in it; W154: its rows 31.x,
    # written from git, carry none either
    for c in _rows(texts[CLASS]):
        if (c[0] == "31" or INTEG_ROW.fullmatch(c[0])) and any(PH.search(x) for x in c):
            bad.append("row %s carries a token" % c[0])
    # W78: section 8's statement of the fill tool's template rows equals the tokens in the two files (one row per occurrence, no KEEP);
    # W80: it states the template BEFORE the fill, so after the fill it is compared with the newest committed revision of RESULT.md that
    # still holds the re-key's token (git), its two files read at that commit
    # W95: the tool's template covers the patch file the record names too (fill_res.py's set_files), so the statement counts it
    flat = " ".join(texts[RESULT].split())
    m = re.search(r"before the fill, the tool's template rows are (\d+) \(RESULT\.md (\d+), CLASSIFICATION\.md (\d+), ENTRY-PAGES\.patch\.md (\d+); "
                  r"GATE (\d+), REKEY (\d+), PROMOTED (\d+), CANDIDATE (\d+), ADOPTION (\d+); no KEEP row\)", flat)
    src = dict(texts, **{PATCH: texts.get(PATCH, _read_opt(PATCH))}) if st == 0 else _template_texts()
    if src is None:
        bad.append("after the fill, no committed revision of RESULT.md holds the template (the re-key's token)")
        return bad
    cr, cc, cp = Counter(PH.findall(src[RESULT])), Counter(PH.findall(src[CLASS])), Counter(PH.findall(src[PATCH]))
    al = cr + cc + cp
    want = (sum(al.values()), sum(cr.values()), sum(cc.values()), sum(cp.values())) + tuple(al["__%s__" % k] for k in ("GATE", "REKEY", "PROMOTED", "CANDIDATE", "ADOPTION"))
    if not m or tuple(int(x) for x in m.groups()) != want:
        bad.append("section 8's template rows are not the %s tokens %s" % ("files'" if st == 0 else "template revision's", want))
    return bad


def _read_opt(rel):
    """W95: a file of the record that may not exist yet (the patch file before W95's commit): its text, or the empty string."""
    p = os.path.join(REPO, rel)
    return open(p, encoding="utf-8").read() if os.path.isfile(p) else ""


def _template_texts():
    """The files at the newest commit touching RESULT.md whose RESULT.md still holds `__REKEY__` (the template the fill filled); W95:
    with the patch file at that commit (empty where it did not exist there)."""
    if "tmpl" not in _C:
        _C["tmpl"] = None
        for c in _git("log", "--format=%H", "--", RESULT).split():
            t = "\n".join(_show(c, RESULT))
            if "`__REKEY__`" in t:
                has = PATCH in _git("ls-tree", "-r", "--name-only", c, "--", PATCH).split("\n")
                _C["tmpl"] = {RESULT: t, CLASS: "\n".join(_show(c, CLASS)), PATCH: "\n".join(_show(c, PATCH)) if has else ""}
                break
    return _C["tmpl"]


def p_coverage(text, order):
    bad = []
    want = [(o[0], o[2]) for o in order]
    got = []
    for c in _real(text):
        s = _sha_cell(c)
        if not s:
            bad.append("row %s has no `short` / `full` sha cell" % c[0])
            continue
        if not s[1].startswith(s[0]):
            bad.append("row %s: %s is not the prefix of %s" % (c[0], s[0], s[1]))
        got.append((c[0], s[1]))
    if got != want:
        miss = [w[1][:8] for w in want if w not in got]
        extra = [g[1][:8] for g in got if g not in want]
        bad.append("the rows are not the five ranges in their order (missing or misnumbered %s, extra %s)" % (miss, extra))
    return bad


def p_columns(text, order):
    bad = []
    by = {o[2]: o for o in order}
    for c in _rows(text):
        s = _sha_cell(c)
        if not s or s[1] not in by:
            continue
        num, branch, sha, ps, date, subj, names = by[s[1]]
        if c[2] != date:
            bad.append("%s: date %r is not git's %r" % (sha[:8], c[2], date))
        if c[3].replace("\\|", "|") != subj:
            bad.append("%s: the subject is not git's" % sha[:8])
        if not c[4].startswith(branch + " ("):
            bad.append("%s: the branch cell does not name %s" % (sha[:8], branch))
        m = re.match(r"(\d+):", c[5])
        if not m or int(m.group(1)) != len(names):
            bad.append("%s: file count %r is not git's %d" % (sha[:8], c[5][:12], len(names)))
        cls = _classes(c)
        if any(k not in FIXED for k in cls) or len(set(cls)) != len(cls):
            bad.append("%s: a class outside the fixed set, or one twice: %s" % (sha[:8], cls))
        if (cls[0] == "MERGE") != (len(ps) > 1):
            bad.append("%s: MERGE and the commit's parents disagree" % sha[:8])
        rv = [n for n in names if n in _reviewed()]
        if rv and "UNREVIEWED since cx46" not in c[7]:
            bad.append("%s touches %d reviewed file(s) and does not say UNREVIEWED since cx46" % (sha[:8], len(rv)))
        if rv and ("(%d):" % len(rv)) not in c[7]:
            bad.append("%s: its reason does not count its %d reviewed file(s)" % (sha[:8], len(rv)))
        if cls[0] != RIC:
            continue
        if "UNREVIEWED since cx46" not in c[7]:
            bad.append("%s is %s and does not say UNREVIEWED since cx46" % (sha[:8], RIC))
        if not [n for n in names if n in _tree()]:
            bad.append("%s is %s but touches no file of the reviewed tree" % (sha[:8], RIC))
        carried = "second sentence" in c[7]
        if not rv and not carried:
            bad.append("%s is %s, touches none of cx46's delta and does not class a carried change" % (sha[:8], RIC))
        if carried and (not re.search(r"set 30's rows? \d+|\brows? \d+(?:\.\d+)?\b", c[7]) or "in the delta cx46 read" not in c[7]):
            bad.append("%s: a carried change without its source row or the delta membership" % sha[:8])
    return bad


def p_rule(text, s30_lines, tree_lines):
    """The class is set 30's line 11 quoted verbatim (the tree's copy equal to main's), read as ruled, with row 44 the precedent."""
    bad = []
    if len(s30_lines) < 68 or not s30_lines[10].startswith("- `REVIEWED-INPUT CHANGED`:"):
        return ["set 30's record has no REVIEWED-INPUT CHANGED rule at its line 11"]
    if tree_lines[:len(s30_lines)] != s30_lines:
        bad.append("the tree's copy of set 30's record is not main's at eff28be3")
    head = text.split("## 1. ", 1)[0]
    flat = " ".join(head.split())
    if "`eff28be3:v2/docs/records/int30/CLASSIFICATION.md:11`):\n\n> " + s30_lines[10] + "\n" not in head:
        bad.append("the rule paragraph does not quote set 30's line 11 verbatim")
    for w in ("reading A", "set 30's row 44", "set 30's rows 1, 13 and 44 did not take it",
              "each placeholder row is classed under the second sentence when filled",
              "(1) set 30's rule covers a change carried into any file of the reviewed tree",
              "(2) set 30's rule requires each such reason to name the source row and whether the file was in the delta cx46 read"):
        if w not in flat:
            bad.append("the rule paragraph does not read %r" % w)
    if "no figure or verdict word moved" not in s30_lines[67]:
        bad.append("set 30's row 44 (line 68) does not read 'no figure or verdict word moved'")
    return bad


def p_summary(text):
    bad = []
    rows = _real(text)
    first = Counter(_classes(c)[0] for c in rows)
    carry = Counter(k for c in rows for k in set(_classes(c)))
    sec = text.split("\n## 2. ", 1)[1]
    flat = " ".join(sec.replace("\n> ", "\n").split())
    for k in FIXED:
        m = re.search(r"^\| `%s` \| (\d+) \| (\d+) \|$" % re.escape(k), sec, re.M)
        if not m or int(m.group(1)) != first[k] or int(m.group(2)) != carry[k]:
            bad.append("the summary row of %s is not the table's (%d, %d)" % (k, first[k], carry[k]))
    m = re.search(r"^\| total \| (\d+) \|", sec, re.M)
    if not m or int(m.group(1)) != len(rows):
        bad.append("the summary's total is not the table's %d" % len(rows))
    for name, _base, _tip, _against in BRANCHES:
        br = [c for c in rows if c[4].startswith(name + " (")]
        f = Counter(_classes(c)[0] for c in br)
        part = ", ".join("%s %d" % (k, f[k]) for k in FIXED if f[k])
        want = "%s, %d rows: %s" % (name, len(br), part)
        if want not in flat:
            bad.append("the per-branch line does not read %r" % want)
    touch = [c for c in rows if "UNREVIEWED since cx46" in c[7]]
    # W78 (W75's F8): the 21 are file touches (one per reviewed file per row), the 16 distinct files are p_counts' (git's)
    m = re.search(r"\*\*The rows that touch a file cx46 read: (\d+), all UNREVIEWED since cx46\.\*\* In table order: (.*?); (\d+) file touches ", flat)
    nfiles = 0
    if not m or int(m.group(1)) != len(touch):
        bad.append("the touching-rows line is not the table's %d" % len(touch))
    else:
        named = re.findall(r"`([0-9a-f]{8})` \(([\d.]+)\)", m.group(2))
        if named != [(_sha_cell(c)[0], c[0]) for c in touch]:
            bad.append("the touching-rows list is not the table's rows in order")
        nfiles = sum(int(re.search(r"reviewed files it touches \((\d+)\)", c[7]).group(1)) for c in touch)
        if int(m.group(3)) != nfiles:
            bad.append("the touching rows name %d files, not %s" % (nfiles, m.group(3)))
    nb = [sum(1 for c in rows if c[4].startswith(b[0] + " (")) for b in BRANCHES]
    want = "carry %d commits over their bases (%s; no merge)" % (len(rows), ", ".join(
        "%s %d over `%s`" % (b[0], n, b[1][:8]) for b, n in zip(BRANCHES, nb)))
    if want not in flat:
        bad.append("the bound statement does not read %r" % want)
    want = "By first class: " + ", ".join("%d %s first" % (first[k], k) for k in FIXED if first[k]) + "."
    if want not in flat:
        bad.append("the bound statement's class counts do not read %r" % want)
    ri = [c for c in rows if _classes(c)[0] == RIC]
    if not ri and "None is classed REVIEWED-INPUT CHANGED" not in flat:
        bad.append("the bound statement does not say that none is REVIEWED-INPUT CHANGED")
    if len(ri) == 1 and ("The one REVIEWED-INPUT CHANGED row is" not in flat or "(row %s," % ri[0][0] not in flat):
        bad.append("the bound statement does not name the one REVIEWED-INPUT CHANGED row %s" % ri[0][0])
    words = {2: "two", 3: "three", 4: "four"}
    if len(ri) > 1 and ("The %s REVIEWED-INPUT CHANGED rows are" % words.get(len(ri), str(len(ri))) not in flat
                        or any("(row %s," % c[0] not in flat for c in ri)):
        bad.append("the bound statement does not name the REVIEWED-INPUT CHANGED rows %s" % [c[0] for c in ri])
    if "%d of the %d touch a file cx46 read (%d file touches," % (len(touch), len(rows), nfiles) not in flat:
        bad.append("the bound statement's touch counts are not the table's (%d of %d, %d file touches)" % (len(touch), len(rows), nfiles))
    return bad

def p_counts(texts, order):
    """Every count both records type about git, recomputed from git over the five ranges."""
    bad = []
    t = " ".join(texts[CLASS].replace("\n> ", "\n").split())    # the bound statement's quote markers dropped (W78)
    r = " ".join(texts[RESULT].split())
    cnt, allf = [], set()
    merges = 0
    for name, base, tip, against in BRANCHES:
        cnt.append(int(_git("rev-list", "--count", "%s..%s" % (base, tip))))
        merges += int(_git("rev-list", "--count", "--merges", "%s..%s" % (base, tip)))
        allf |= set(_git("diff", "--name-only", base, tip).split())
        mb = _git("merge-base", against, tip).strip()
        if mb != base:
            bad.append("%s: its base %s is not its merge base %s with %s" % (name, base[:8], mb[:8], against[:8]))
    if merges:
        bad.append("a branch holds %d merge(s); the records say none" % merges)
    kinds = [f for f in allf if f.endswith(".out") or f.endswith(".net") or "/apply_gen_sch_" in f or "/gen_sch_" in f]
    if kinds:
        bad.append("the branches change an output, a netlist, a circuit draft or a board generator: %s" % sorted(kinds)[:5])
    rv = allf & _reviewed()
    delta = len(set(_git("diff", "--name-only", CX45, REVIEWED).split()))
    pa = BRANCHES[0]
    fa = set(_git("diff", "--name-only", pa[1], pa[2]).split())
    tree = _git("ls-tree", "-r", "-l", pa[2]).split("\n")
    vend = [l.split() for l in tree if "/pdftext/" in l]
    texts_ = [x for x in vend if x[-1].endswith(".txt")]
    side = [x for x in vend if x[-1].endswith(".meta.json")]
    pys = [f for f in fa if f.startswith("v2/docs/records/") and f.endswith(".py") and "/_lib/" not in f and "/w42cite/" not in f]
    decl = sorted(f for f in pys if _decl_only("\n".join(_show(pa[2], f))))      # W85: W81's declaration-only modules
    gens = [f for f in pys if f not in decl]
    w34 = [l.split() for l in _git("ls-tree", "-r", "-l", W34_TIP).split("\n") if "/pdftext/" in l]
    w34t = [x for x in w34 if x[-1].endswith(".txt")]
    rows = _real(texts[CLASS])
    first = Counter(_classes(c)[0] for c in rows)
    touch = [c for c in rows if "UNREVIEWED since cx46" in c[7]]
    want_c = ["`git rev-list --count %s..%s` prints %d" % (b[1][:8], b[2][:8], n) for b, n in zip(BRANCHES, cnt)]
    want_c += ["%s `%s`, %d commits over `%s`" % (b[0], b[2][:8], n, b[1][:8]) for b, n in zip(BRANCHES, cnt)]
    want_c += ["the %d files of `git diff --name-only 06077cee 4d0ff8a2`" % delta,
               "%d of the five ranges' %d changed files are in that set" % (len(rv), len(allf)),
               "**DONE:** the %d commits of the five branches" % sum(cnt),
               "(%d texts, %d sidecars)" % (len(texts_), len(side)), "The %d vendor files" % len(vend),
               "each named in its row (%d distinct files)" % len(rv),
               "(%d file touches, %d distinct files:" % (sum(int(re.search(r"reviewed files it touches \((\d+)\)", c[7]).group(1))
                                                         for c in touch), len(rv)),
               "Dates are the author dates (git's `%ad`)"]      # W78 (W75's F5): _order() reads %ad, the date matching git on all 30
    for w in want_c:
        if w not in t:
            bad.append("CLASSIFICATION.md does not read %r (git's numbers)" % w)
    want_r = ["%d commits over `%s`" % (n, b[1]) for b, n in zip(BRANCHES, cnt)]
    want_r += ["%d commits of the five branches over their bases (%s; no merge)" % (sum(cnt), ", ".join(
                   "%s %d" % (b[0], n) for b, n in zip(BRANCHES, cnt))),
               ("REVIEWED-INPUT CHANGED %d; RECORD TEXT %d; GENERATOR DATA (text) %d; TEST %d; DIGEST RE-PIN %d; MERGE %d; TOOLING %d; total %d"
                % tuple([first[k] for k in FIXED] + [len(rows)])),
               "%d of the %d touch a file cx46 read (%d distinct files:" % (len(touch), len(rows), len(rv)),
               "%d record generators read each maker's PDF text" % len(gens),
               "%d extractions committed beside their PDFs with a sidecar each (%d files)" % (len(texts_), len(vend)),
               "%d extractions committed beside their PDFs with a sidecar each (%d files)" % (len(w34t), len(w34)),
               "in %d declaration-only modules (%s:" % (len(decl), ", ".join("`%s`" % os.path.basename(f) for f in decl)),
               "a change of how %d record generators read" % len(gens)]
    for w in want_r:
        if w not in r:
            bad.append("RESULT.md does not read %r (git's numbers)" % w)
    if len(texts_) != len(side) or len(gens) != 26 or len(decl) != 3:
        bad.append("the tip holds %d texts, %d sidecars, %d converted generators (W34's 25 and W55's l8p_c4), %d declaration-only modules "
                   "(W81's 3)" % (len(texts_), len(side), len(gens), len(decl)))
    if 2 * len(w34t) != len(w34):
        bad.append("W34_TIP holds %d texts in %d files, not one sidecar each" % (len(w34t), len(w34)))
    tb_bytes = sum(int(x[3]) for x in w34t)
    inv = _show(W34_TIP, "v2/docs/records/_lib/PDFTEXT-INVENTORY.md")
    if not any(("%s committed (%s bytes of text" % (len(w34t), format(tb_bytes, ","))) in l for l in inv):
        bad.append("the inventory's total at W34_TIP is not its %d texts of %d bytes" % (len(w34t), tb_bytes))
    inv = " ".join("\n".join(_show(pa[2], "v2/docs/records/_lib/PDFTEXT-INVENTORY.md")).split())
    if "and %d committed (%d before)." % (len(texts_), len(w34t)) not in inv:
        bad.append("the inventory's section 9 at the tip does not read %d committed (%d before)" % (len(texts_), len(w34t)))
    for a, b, span in (("16:32:57", "16:33:50", "53 s"),):
        s = [int(x) for x in a.split(":")]
        e = [int(x) for x in b.split(":")]
        d = (e[0] - s[0]) * 3600 + (e[1] - s[1]) * 60 + e[2] - s[2]
        if "%d s" % d != span or ("%s to %s, %s" % (a, b, span)) not in r:
            bad.append("the elapsed time %s to %s is not %s" % (a, b, span))
    return bad

def _decl_only(src):
    """W85: a declaration-only module (W81's class): a module docstring and one PDFTEXT dict assignment, nothing else (ast)."""
    try:
        b = ast.parse(src).body
    except SyntaxError:
        return False
    return (len(b) == 2 and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) and isinstance(b[0].value.value, str)
            and isinstance(b[1], ast.Assign) and [getattr(x, "id", None) for x in b[1].targets] == ["PDFTEXT"]
            and isinstance(b[1].value, ast.Dict))


ROW_NUMSTAT = (("82e1e1c6", "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md", "(+%d -%d)"),
               ("886704ea", "v2/docs/records/_lib/PDFTEXT-INVENTORY.md", "(+%d -%d)"),
               ("a7a485ab", "v2/docs/records/s32small/apply_q55_ve16.py", "(%d lines)"),
               ("a7a485ab", "v2/docs/records/s32small/README.md", "(%d lines)"),
               ("44891f15", "v2/docs/records/s32small/apply_q55_ve16.py", "(+%d -%d)"),
               ("44891f15", "v2/docs/records/s32small/README.md", "(+%d -%d)"),
               ("7b7219a7", "v2/docs/records/s32small/README.md", "(+%d -%d)"),
               ("4f558357", "v2/docs/records/l8p/l8p_c4.py", "(+%d -%d)"),
               ("f26a52c4", "v2/ecad/tools/tests/test_pdftext_input.py", "(+%d -%d)"),
               ("b397aada", "v2/docs/records/_lib/PDFTEXT-INVENTORY.md", "(+%d -%d)"),
               ("9210ab54", "v2/ecad/tools/tests/test_l9t5.py", "(+%d -%d)"),
               ("849e66c7", "v2/docs/records/l4e7/l4e7_stage_settings.py", "(+%d -%d)"),
               ("849e66c7", "v2/ecad/tools/tests/test_l4e7_cachekey.py", "(%d lines, new)"),
               ("2178cae5", "v2/docs/records/l4e7/l4e7_p0sol.py", "(+%d -%d)"),
               ("935584bf", "v2/ecad/tools/tests/test_l4e7.py", "(+%d -%d)"),
               ("5ee1e66e", "v2/docs/records/l4e7/CACHE-BOUNDARY-L4E11.md", "(+%d -%d)"),
               # W85: W81's four rows
               ("2184a968", "v2/docs/records/l8p/l8p_drafts.py", "(+%d -%d"),
               ("877d81c5", "v2/ecad/tools/tests/test_l8r2.py", "(+%d -%d)"),
               ("877d81c5", "v2/ecad/tools/tests/test_l3r5.py", "(+%d -%d)"),
               ("877d81c5", "v2/ecad/tools/tests/test_l5r4.py", "(+%d -%d)"),
               ("877d81c5", "v2/docs/records/l8r2/l8r2_drafts.py", "(+%d -%d"),
               ("877d81c5", "v2/docs/records/l5r4/l5r4_pdftext.py", "(%d lines)"),
               ("da81447d", "v2/docs/records/l8p/l8p_pdftext.py", "(%d lines)"),
               ("da81447d", "v2/docs/records/l8r2/l8r2_pdftext.py", "(%d lines)"),
               ("da81447d", "v2/docs/records/l8p/l8p_drafts.py", "(+%d -%d)"),
               ("da81447d", "v2/docs/records/l8r2/l8r2_drafts.py", "(+%d -%d)"),
               ("da81447d", "v2/ecad/tools/tests/test_l8p.py", "(+%d -%d)"),
               ("da81447d", "v2/ecad/tools/tests/test_l8r2.py", "(+%d -%d)"),
               ("da81447d", "v2/ecad/tools/tests/test_pdftext_input.py", "(+%d -%d)"),
               ("62300318", "v2/docs/records/_lib/PDFTEXT-INVENTORY.md", "(+%d -%d)"),
               ("62300318", "v2/ecad/tools/tests/test_pdftext_input.py", "(+%d -%d)"))


def p_row_numbers(text):
    """The per-row numbers the reasons type: the committed extractions and their files, and the line counts named."""
    bad = []
    rows = {(_sha_cell(c) or ("", ""))[0]: c for c in _real(text)}
    for short, c in rows.items():
        m = re.search(r"(\d+) committed extractions with (?:their )?sidecars \((\d+) files", c[7])
        if m:
            names = _git("show", "--name-only", "--format=", short).split()
            pt = [n for n in names if "/pdftext/" in n]
            want = (len([n for n in pt if n.endswith(".txt")]), len(pt))
            if (int(m.group(1)), int(m.group(2))) != want:
                bad.append("%s: %s extractions in %s files typed, git has %d in %d" % (short, m.group(1), m.group(2), want[0], want[1]))
    for short, path, form in ROW_NUMSTAT:
        add, rem = _git("diff", "--numstat", short + "^", short, "--", path).split()[:2]
        want = form % ((int(add), int(rem)) if form.count("%d") == 2 else (int(add),))
        if short not in rows or want not in rows[short][7]:
            bad.append("%s: the reason does not read %r for %s" % (short, want, path))
    return bad


def p_commits_named(texts):
    bad = []
    # W154: fnd/res32 as the chain merged it (row 31.4, in this branch's history) holds rows 31.4.1 to 31.4.12
    hist = set(_git("rev-list", LINEAGE, RES32_MERGED, *[b[2] for b in BRANCHES]).split())
    hist |= _accepted(texts)               # W80: the commits the fill wrote, each where its role puts it (p_filled), and only then
    for name, t in texts.items():
        for tok in set(HEXTOK.findall(t)):
            if len(tok) not in (8, 40):
                continue                       # 12- and 16-character tokens are file digests, not commits
            full = [s for s in hist if s.startswith(tok)]
            if len(full) == 1:
                continue
            # W154: the re-key's cache commit and the candidate are declared for the classification (rows 32 and 33 and row 33's
            # citations); in RESULT they stand only where the fill writes them, accepted through p_filled alone (W80's rule)
            out = [s for s in OUTSIDE if s.startswith(tok) and not (name == RESULT and s in (REKEY_AT, CAND_AT))]
            if out:
                if _has(out[0]) and _git("cat-file", "-t", out[0]).strip() != "commit":
                    bad.append("%s: %s is not a commit" % (name, tok))
                continue
            bad.append("%s: `%s` names no commit of the histories this record reads and is not declared outside them" % (name, tok))
    return bad


def p_quotes(texts):
    bad = []
    for name, t in texts.items():
        for sha, path, n, q in GIT_ANCHOR.findall(t):
            q = q.replace("\\|", "|")
            if not _has(sha):
                if any(o.startswith(sha) for o in OUTSIDE):
                    continue                   # a declared commit outside this branch's history, absent on this host
                bad.append("%s: %s is not in this repository" % (name, sha))
                continue
            lines = _show(sha, path)
            if int(n) > len(lines) or q not in lines[int(n) - 1]:
                bad.append("%s: %r is not on %s:%s:%s" % (name, q[:60], sha[:8], path, n))
    return bad


def p_claims(result, assess_lines):
    bad = []
    for n, words in CLAIMS.items():
        if assess_lines[n - 1].rstrip() != words:
            bad.append("the assessment's line %d is not %r" % (n, words))
        if "`%s:%s:%d` `%s`" % (ASSESS_AT[:8], ASSESS, n, words) not in result:
            bad.append("RESULT.md does not quote line %d verbatim: %r" % (n, words))
    sec = result.split("\n## 6. ", 1)[1].split("\n## 7. ", 1)[0]
    for claim, state in (("Engineering-handover readiness", "READY AS A DESK PACKAGE OF OPEN ITEMS"),
                         ("Power-design closure", "BLOCKED"), ("Fabrication release", "BLOCKED")):
        if "| %s | %s |" % (claim, state) not in sec:
            bad.append("section 6 does not give %s as %s" % (claim, state))
    if "**Set 32 closes NO power item.**" not in sec or "**Layer 4's DESK gate stays NOT PASSED**" not in sec:
        bad.append("section 6 does not say that set 32 closes no power item and the DESK gate stays NOT PASSED")
    for wrong in ("DESK gate: PASSED", "DESK gate PASSED", "closure: CLOSED", "release: RELEASED", "Set 32 closes the"):
        if wrong in result:
            bad.append("RESULT.md reads %r" % wrong)
    return bad


def p_logs(texts, runs):
    bad = []
    for name, t in texts.items():
        for rel, n, entry, q in RUN_ANCHOR.findall(t):
            p = os.path.join(runs, rel)
            if not os.path.isfile(p):
                bad.append("%s: _runs/%s is missing" % (name, rel))
                continue
            body = open(p, encoding="utf-8", errors="replace").read()
            if n:
                lines = body.split("\n")
                if int(n) > len(lines) or q not in lines[int(n) - 1]:
                    bad.append("%s: _runs/%s:%s does not read %r" % (name, rel, n, q[:60]))
            elif entry:
                if entry not in body or q not in body:
                    bad.append("%s: _runs/%s has no entry %r carrying %r" % (name, rel, entry[:40], q[:40]))
            elif q not in body:
                bad.append("%s: _runs/%s does not carry %r" % (name, rel, q[:60]))
        for rel in set(RUN_PATH.findall(t)):
            if not os.path.isfile(os.path.join(runs, rel)):
                bad.append("%s: the cited file _runs/%s is missing" % (name, rel))
    return bad


def p_carried(text, s30_lines):
    """A row classed REVIEWED-INPUT CHANGED for a carried change names its source row, and that row is classed REVIEWED-INPUT CHANGED
    (W51's method: a carried word is looked up in the reasons of the REVIEWED-INPUT CHANGED rows): set 30's row in set 30's adopted
    record, or (W78, on the coordinator's ruling on W75's F2: row 15 quotes row 14's words) an earlier row of this table."""
    bad = []
    s30 = {}
    for l in s30_lines:
        m = re.match(r"\| (\d+) \| `([0-9a-f]{8})` / `[0-9a-f]{40}` \|", l)
        if m:
            s30[m.group(1)] = (m.group(2), [c.strip() for c in CELL_SPLIT.split(l.strip())[1:-1]][6])
    own = {c[0]: c for c in _real(text)}
    for c in _real(text):
        if _classes(c)[0] != RIC:
            continue
        if "second sentence" not in c[7]:
            # W80 (W79's N2): a row classed by the first sentence quotes the old and the new value with file and line ("`a:f:N` `old`
            # now `b:f:N` `new`") and names the cx46 item that read it or says none names it, both outside the quotes
            bare = GIT_ANCHOR.sub("", c[7])
            pair = re.search(r"`[0-9a-f]{8,40}:[^`:\s]+:\d+` `(?:[^`\\]|\\.)+` now `[0-9a-f]{8,40}:[^`:\s]+:\d+` `", c[7])
            if not pair or not re.search(r"cx46's items? \d+|none names it", bare):
                bad.append("row %s is %s with neither the second sentence's source row nor the first sentence's old and new value and "
                           "cx46 item" % (c[0], RIC))
            continue
        m = re.search(r"this table's row (\d+)'s change \(`([0-9a-f]{8})`", c[7])
        if m:
            n, sha = m.groups()
            src = own.get(n)
            if not src or _sha_cell(src)[0] != sha or _classes(src)[0] != RIC or _rk(n) >= _rk(c[0]):
                bad.append("row %s: this table's row %s (%s) is not an earlier REVIEWED-INPUT CHANGED row of this table" % (c[0], n, sha))
            continue
        m = re.search(r"set 30's row (\d+)'s change \(`([0-9a-f]{8})`", c[7])
        if not m:
            bad.append("row %s: no source row named as `set 30's row N's change (`sha`` or `this table's row N's change (`sha``" % c[0])
            continue
        n, sha = m.groups()
        if n not in s30 or s30[n][0] != sha or not s30[n][1].startswith(RIC):
            bad.append("row %s: set 30's row %s (%s) is not a REVIEWED-INPUT CHANGED row of set 30's record" % (c[0], n, sha))
    return bad


def _rk(s):
    """A row number as a sort key: '13.2' after '13' and before '14' (W85)."""
    return tuple(int(x) for x in str(s).split("."))


def _nums(s):
    """'2, 3, 4, 9, 11, 13.2, 25, 27 and 29' or '2 to 5, 7, 13.1 to 13.3, 14 to 16 and 29' as a list of row numbers (strings; W85: a
    range runs over the last part of numbers that share the rest)."""
    out = []
    for part in re.split(r",\s*|\s+and\s+", s.strip()):
        part = part.strip()
        m = re.fullmatch(r"(\d+(?:\.\d+)?) to (\d+(?:\.\d+)?)", part)
        if m:
            a, b = _rk(m.group(1)), _rk(m.group(2))
            if len(a) != len(b) or a[:-1] != b[:-1] or a[-1] > b[-1]:
                raise AssertionError("not a row range: %r" % part)
            out += [".".join(str(x) for x in a[:-1] + (i,)) for i in range(a[-1], b[-1] + 1)]
        elif re.fullmatch(r"\d+(?:\.\d+)?", part):
            out.append(part)
        else:
            raise AssertionError("not a row list: %r" % s)
    return out


def _totals(s):
    return {k: int(v) for k, v in re.findall(r"(REVIEWED-INPUT CHANGED|RECORD TEXT|GENERATOR DATA \(text\)|TEST|DIGEST RE-PIN|MERGE|TOOLING) (\d+)", s)}


def p_alternatives(text, order):
    """W78 (W75's F3): the two wider readings the rule paragraph states, recomputed from the table: (1) a touched file of cx46's delta
    alone (the rows saying UNREVIEWED since cx46), (2) any row's change carried into a file present at 4d0ff8a2 (the rows it names, each
    touching such a file, git's names); each reading's totals by first class are the table's with the named rows moved."""
    bad = []
    flat = " ".join(text.split("## 1. ", 1)[0].split())
    rows = _real(text)
    first = {c[0]: _classes(c)[0] for c in rows}
    ric = {n for n, k in first.items() if k == RIC}

    def moved(to):
        f = Counter(RIC if n in to else k for n, k in first.items())
        return {k: v for k, v in f.items() if v}
    m = re.search(r"rows ([\d., and]+?) would be REVIEWED-INPUT CHANGED too \((\d+) rows with rows ([\d., and]+?); by first class ([^)]+)\)", flat)
    touch = {c[0] for c in rows if "UNREVIEWED since cx46" in c[7]}
    if not m:
        bad.append("the first wider reading (a touched file of the delta alone) is not stated with its rows and totals")
    else:
        added, withr = set(_nums(m.group(1))), set(_nums(m.group(3)))
        if withr != ric or added & ric or added | ric != touch or int(m.group(2)) != len(touch):
            bad.append("the first wider reading's rows are not the touching rows %s" % sorted(touch, key=_rk))
        if _totals(m.group(4)) != moved(touch):
            bad.append("the first wider reading's totals are not the table's %s" % moved(touch))
    m = re.search(r"present at `4d0ff8a2` \(rows ([^)]+)\) finds the same (\d+) rows, ([\d., and]+?):", flat)
    m2 = re.search(r"By first class under that reading: ([^.]+)\.", flat)
    if not m or not m2:
        bad.append("the second wider reading (any row's change) is not stated with its rows and totals")
        return bad
    by = {o[0]: o for o in order}
    intree = sorted((n for n, o in by.items() if [x for x in o[6] if x in _tree()]), key=_rk)
    named = set(_nums(m.group(3)))
    if _nums(m.group(1)) != intree:
        bad.append("the rows touching a file present at 4d0ff8a2 are git's %s, not %s" % (intree, m.group(1)))
    if int(m.group(2)) != len(named) or not named <= set(intree) or not ric <= named:
        bad.append("the second wider reading's rows %s are not a set of rows touching the reviewed tree holding the table's %s"
                   % (sorted(named, key=_rk), sorted(ric, key=_rk)))
    if _totals(m2.group(1)) != moved(named):
        bad.append("the second wider reading's totals are not the table's %s" % moved(named))
    # W80 (W79's N1): the clauses after the list say which row carries which row's change; the rows they name as carriers (and "as
    # above", the REVIEWED-INPUT CHANGED rows) are the listed rows, each carrying an EARLIER row of the table
    seg = flat[m.end():].split(" By first class under that reading", 1)[0].split(" Rows 2 to 5 and 11 ", 1)[0]
    carriers = set()
    for clause in seg.split("; "):
        a = re.match(r"\s*rows? ([\d.]+(?:(?:, | and )[\d.]+)*) as above\b", clause)
        if a:
            if set(_nums(a.group(1))) != ric:
                bad.append("the rows 'as above' %s are not the table's REVIEWED-INPUT CHANGED rows %s" % (a.group(1), sorted(ric, key=_rk)))
            carriers |= set(_nums(a.group(1)))
            continue
        k = re.match(r"\s*rows? ([\d.]+(?:(?:, | and )[\d.]+)*)(?:'s [a-z ]+?)? (?:carry|carries|restate|restates) rows? "
                     r"([\d.]+(?:(?:, | and )[\d.]+)*)'s ", clause)
        if not k:
            bad.append("a clause of the second wider reading names no carrier and source: %r" % clause[:60])
            continue
        who, src = _nums(k.group(1)), _nums(k.group(2))
        if any(_rk(s) >= _rk(w) or s not in first for w in who for s in src):
            bad.append("rows %s do not carry earlier rows of the table (%s)" % (who, src))
        carriers |= set(who)
    if carriers != named:
        bad.append("the second wider reading lists rows %s but its clauses carry rows %s" % (sorted(named, key=_rk), sorted(carriers, key=_rk)))
    return bad


def _fill_tokens(tree):
    """The names fill_res.py's TOK pattern fills, read with ast (the re.compile call assigned to TOK)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "TOK" for x in node.targets):
            pat = node.value.args[0].value
            m = re.fullmatch(r"__\(([A-Z|]+)\)__", pat)
            return set(m.group(1).split("|")) if m else None
    return None


def _strval(e, consts):
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        return e.value
    if isinstance(e, ast.Name):
        return consts.get(e.id)
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Add):
        a, b = _strval(e.left, consts), _strval(e.right, consts)
        return a + b if a is not None and b is not None else None
    return None


def _fill_files(tree, key):
    """fill_res.py's SETS[key]["files"], each entry resolved through the module's string constants (R31, R32 = "...", "...")."""
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            tg, v = node.targets[0], node.value
            if isinstance(tg, ast.Tuple) and isinstance(v, ast.Tuple):
                for n, x in zip(tg.elts, v.elts):
                    if isinstance(n, ast.Name) and _strval(x, consts) is not None:
                        consts[n.id] = _strval(x, consts)
            elif isinstance(tg, ast.Name) and _strval(v, consts) is not None:
                consts[tg.id] = _strval(v, consts)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "SETS" for x in node.targets) \
                and isinstance(node.value, ast.Dict):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key and isinstance(v, ast.Dict):
                    for k2, v2 in zip(v.keys, v.values):
                        if isinstance(k2, ast.Constant) and k2.value == "files" and isinstance(v2, ast.List):
                            return [_strval(e, consts) for e in v2.elts]
    return None


def p_fill(src):
    """W78 (W75's F11): the fill tool is _bin/fill_res.py (W76); its TOK fills the declared tokens and its set 32 files are this record's."""
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["fill_res.py does not parse: %s" % e]
    names = _fill_tokens(tree)
    if names is None:
        return ["fill_res.py has no TOK pattern of the form __(A|B)__"]
    bad = []
    want = set(d.strip("_") for d in DECLARED)
    if names - {"INTEGRATED"} != want:
        bad.append("the declared tokens %s are not fill_res.py's %s (without INTEGRATED)" % (sorted(want), sorted(names)))
    files = _fill_files(tree, "32")
    if files != [RESULT, CLASS]:
        bad.append("fill_res.py's set 32 files are %s, not %s" % (files, [RESULT, CLASS]))
    return bad


def p_chain(sh):
    """chain.sh's merges are the five ranges' branches, each pinned inside its range (fnd/res32's later commits are row 31's)."""
    bad = []
    labels = set(re.findall(r'merge_one (\w+) "\$PIN_', sh))
    if labels != set(CHAIN_LABELS):
        bad.append("chain.sh merges %s, not the record's five %s" % (sorted(labels), sorted(CHAIN_LABELS)))
    var = {"PDFTEXT": "pdftext", "ATTR": "s32attr", "SMALL": "s32small", "RES": "res32", "L4E7CACHE": "l4e7cache"}
    pins = dict(re.findall(r"^SRC_(\w+)=\$\{SRC_\w+:-([0-9a-f]{7,40})\}", sh, re.M))
    for v, lab in var.items():
        br = [b for b in BRANCHES if b[0] == CHAIN_LABELS[lab]][0]
        if v not in pins:
            bad.append("chain.sh pins no default for SRC_%s" % v)
            continue
        try:
            full = _git("rev-parse", "--verify", pins[v] + "^{commit}").strip()
        except RuntimeError:
            bad.append("SRC_%s=%s is not a commit here" % (v, pins[v]))
            continue
        if lab == "res32":
            ok = _git("merge-base", br[2], full).strip() == br[2]
        else:
            ok = full in _git("rev-list", "%s..%s" % (br[1], br[2])).split()
        if not ok:
            bad.append("SRC_%s=%s is outside the record's range %s..%s of %s" % (v, pins[v], br[1][:8], br[2][:8], br[0]))
    return bad


def _texts():
    return {RESULT: _read(RESULT), CLASS: _read(CLASS)}


def _mutant_refused(pred, texts, name, old, new, *extra):
    t = dict(texts)
    assert old in t[name], "the mutation's anchor %r is not in %s" % (old[:50], name)
    t[name] = t[name].replace(old, new, 1)
    assert pred(t, *extra), "%s passed a mutant (%r)" % (pred.__name__, new[:50])


# ---- tests ----

def t_the_records_carry_no_dash_and_open_with_their_state_lines():
    texts = _texts()
    assert not p_hygiene(texts), p_hygiene(texts)
    _mutant_refused(p_hygiene, texts, RESULT, "Set 32 closes NO power item", "Set 32 closes NO power item \u2014")
    _mutant_refused(p_hygiene, texts, CLASS, "**NOT DONE:**", "**NOT YET:**")


def t_the_rule_is_set_30s_line_11_verbatim_read_as_ruled():
    _need_git()
    t = _read(CLASS)
    s30 = _show(S30, S30C)
    tree = _read(S30C).split("\n")
    assert not p_rule(t, s30, tree), p_rule(t, s30, tree)
    assert p_rule(t.replace("is different now; the reason quotes", "is different now: the reason quotes", 1), s30, tree), \
        "a changed quote passed"
    assert p_rule(t.replace("did not take it (each touched", "took it (each touched", 1), s30, tree), \
        "a wider reading without set 30's answer passed"
    assert p_rule(t, s30, [l.replace("a verdict word", "a verdict") for l in tree]), "a changed copy of set 30's record passed"


def _mut(text, old, new):
    """W85: one replacement whose anchor must be in the text (a mutant that changes nothing would test nothing)."""
    assert old in text, "the mutation's anchor %r is not in the text" % old[:50]
    return text.replace(old, new, 1)


def _line(text, start):
    ls = [l for l in text.split("\n") if l.startswith(start)]
    assert len(ls) == 1, "%d lines start with %r" % (len(ls), start[:40])
    return ls[0]


def _cell(line):
    """The second cell of a table row (a role row's revision, a table row's sha cell), as written."""
    return CELL_SPLIT.split(line.strip())[2].strip()


def t_every_placeholder_is_a_declared_token():
    texts = _texts()
    st = _stage(texts[RESULT])
    assert st is not None, p_filled(texts)
    assert not p_placeholders(texts), p_placeholders(texts)
    # W80: anchors that stay through the fill (W69's method for set 31); the refused defect is unchanged at every stage
    _mutant_refused(p_placeholders, texts, RESULT, "**Set 32 closes NO power item.**", "**Set 32 closes NO power item.** `__GATE_LINE__`")
    r32 = _line(texts[CLASS], "| 32 |")
    # W154: row 32 carries git's date and class since the re-key's cache commit exists (W80's mutant gave it a date while it read "not
    # determined"); restated: its date or its class taken back to "not determined" is refused
    _mutant_refused(p_placeholders, texts, CLASS, r32, r32.replace("| %s | 2026-10-07 07:10:50 |" % _cell(r32), "| %s | not determined |" % _cell(r32), 1))
    _mutant_refused(p_placeholders, texts, CLASS, r32, r32.replace("| DIGEST RE-PIN |", "| not determined |", 1))
    base = _line(texts[RESULT], "| BASE ")      # the BASE row's cell another token: the wrong token before the fill, a partial fill after
    _mutant_refused(p_placeholders, texts, RESULT, base, base.replace("| %s |" % _cell(base), "| `__GATE__` |", 1))
    # W78: a PROMOTED line that does not name set 32 (W75's F9), a token back in row 31 (F11), a template count not the files' (section 8)
    _mutant_refused(p_placeholders, texts, RESULT, "(a DESK candidate once set 32 is promoted, ", "(a DESK candidate once promoted, ")
    _mutant_refused(p_placeholders, texts, RESULT, "(set 32's promotion) |", "(the promotion) |")
    # W154: row 31 is replaced by the rows 31.x; a token in one of them (C1's row) is refused as it was in row 31
    r316 = _line(texts[CLASS], "| 31.6 |")
    _mutant_refused(p_placeholders, texts, CLASS, r316, r316.replace("; UNREVIEWED since cx46 |", "; UNREVIEWED since cx46 `__GATE__` |", 1))
    _mutant_refused(p_placeholders, texts, RESULT, "ENTRY-PAGES.patch.md 25; GATE 66,", "ENTRY-PAGES.patch.md 25; GATE 65,")
    _mutant_refused(p_placeholders, texts, RESULT, "CLASSIFICATION.md 2, ENTRY-PAGES.patch.md 25;", "CLASSIFICATION.md 2, ENTRY-PAGES.patch.md 24;")
    if st == 0:
        _mutant_refused(p_placeholders, texts, RESULT, "`__GATE__`", "`__GATE_LINE__`")
    else:
        # after the fill: a token left that the stage does not leave, and set 31's promoted revision on a line naming set 32
        _mutant_refused(p_placeholders, texts, RESULT, "**Set 32 closes NO power item.**", "**Set 32 closes NO power item.** `__REKEY__`")
        _mutant_refused(p_placeholders, texts, RESULT, "(a DESK candidate once set 32 is promoted, `%s`)" % _roles(texts[RESULT])["PROMOTED"],
                        "(a DESK candidate once set 32 is promoted, `%s`)" % _roles(texts[RESULT])["BASE"])


def t_the_integration_rows_and_the_filled_commits():
    """W80: rows 32 and 33 hold the fill's tokens or its commits; the commits the fill writes stand where their roles put them (W154:
    row 31 is replaced by the rows 31.x written from git, which t_the_integration_rows_are_gits reads)."""
    _need_git()
    texts = _texts()
    st = _stage(texts[RESULT])
    bad = p_integration_rows(texts) + p_filled(texts)
    assert not bad, bad
    r32, r33 = _line(texts[CLASS], "| 32 |"), _line(texts[CLASS], "| 33 |")
    _mutant_refused(p_integration_rows, texts, CLASS, r33, r33 + "\n" + r33.replace("| 33 |", "| 34 |", 1))
    _mutant_refused(p_integration_rows, texts, CLASS, r32, r32.replace("| %s |" % _cell(r32), "| %s |" % _cell(r33), 1))
    _mutant_refused(p_integration_rows, texts, CLASS, r32, r32.replace("| %s |" % _cell(r32), "| `%s` |" % LINEAGE[:8], 1))
    # W154: a row 31 put back ("not determined", W75's F11), and a row 31.x whose sha cell is one code span, are refused
    r311, r316 = _line(texts[CLASS], "| 31.1 |"), _line(texts[CLASS], "| 31.6 |")
    _mutant_refused(p_integration_rows, texts, CLASS, r311,
                    "| 31 | not determined | not determined | the integration's commits | fnd/int32 | not determined | not determined | text |\n" + r311)
    _mutant_refused(p_integration_rows, texts, CLASS, r316, r316.replace("| %s |" % _cell(r316), "| `%s` |" % _cell(r316)[1:9], 1))
    _mutant_refused(p_integration_rows, texts, CLASS, r32, r32.replace("| 32 |", "| 32.1 |", 1))
    if st == 0:     # a fill of rows 32 and 33 without RESULT's rows, and RESULT's rows without the others: a partial fill
        _mutant_refused(p_integration_rows, texts, CLASS, r33, r33.replace("| `__CANDIDATE__` |", "| `%s` |" % LINEAGE[:8], 1))
        rk = _line(texts[RESULT], ROLES[1][1])
        _mutant_refused(p_filled, texts, RESULT, rk, rk.replace("`__REKEY__`", "`%s`" % LINEAGE[:8], 1))
        return
    r = _roles(texts[RESULT])
    rows = {x[0]: _line(texts[RESULT], x[1]) for x in ROLES}

    def moved(role, value):
        _mutant_refused(p_filled, texts, RESULT, rows[role], rows[role].replace("`%s`" % r[role], "`%s`" % value, 1))
    moved("BASE", LINEAGE[:8])                 # set 31's lineage tip itself, not its promoted revision
    moved("BASE", r["REKEY"])                  # a later commit as the base
    moved("REKEY", r["BASE"])                  # the re-key at the base itself
    moved("REKEY", CHAIN_BASE[:8])             # W113 (W110's B2): the re-key at the chain's base itself, not after it
    moved("REKEY", BRANCHES[4][2][:8])         # a commit that is not on the lineage after the base
    moved("CANDIDATE", r["REKEY"])             # the candidate equal to the re-key
    moved("PROMOTED", r["BASE"])               # set 32's promotion naming set 31's
    moved("PROMOTED", r["REKEY"])              # not the candidate main is fast-forwarded to
    moved("ADOPTION", r["CANDIDATE"])          # the adoption commit is not the candidate (at stage 1 the mutant makes stage 2)
    if st == 2:
        moved("ADOPTION", r["BASE"])           # nor an earlier commit


def t_the_rows_written_from_git_after_the_chains_stop_are_gits():
    """W128 (W109's phase 2 finding 4): fnd/l3r5keep's two commits, merged by the coordinator after C1, are rows 31.7.1 and 31.7.2
    under their merge's row 31.7, each cell git's; the basis is git itself (the commits and the merge exist on fnd/int32)."""
    t = _read(CLASS)
    assert not p_prepared(t), p_prepared(t)
    r1, r2 = _line(t, "| 31.7.1 |"), _line(t, "| 31.7.2 |")
    assert p_prepared(_mut(t, r1, r1.replace("| 2026-10-07 01:55:24 |", "| 2026-10-07 02:04:02 |", 1))), \
        "the committer date in place of the author date passed"
    assert p_prepared(_mut(t, r2, r2.replace("reversed (W114's 2dcb4131", "reversed (W114's commit", 1))), "a subject that is not git's passed"
    assert p_prepared(_mut(t, r1, r1.replace("| 2: v2/ecad/tools/ (2) |", "| 3: v2/ecad/tools/ (3) |", 1))), "a wrong file count passed"
    assert p_prepared(_mut(t, r1, r1.replace("| TEST |", "| MERGE |", 1))), "MERGE on a one-parent commit passed"
    assert p_prepared(_mut(t, r2, r2.replace("| fnd/l3r5keep (", "| fnd/int32 (", 1))), "a row outside its branch passed"
    assert p_prepared(t.replace(r2 + "\n", "", 1)), "row 31.7.2 dropped passed"
    assert p_prepared(_mut(t, r1, r1.replace("2dcb41313bbef9b2f76cab344926c81e8d7e23c7", "2dcb41313bbef9b2f76cab344926c81e8d7e23c8", 1))), \
        "a full sha that is not the commit passed"
    assert p_prepared(t.replace(r1 + "\n" + r2, r2 + "\n" + r1, 1)), "the two rows out of git's order passed"
    assert p_prepared(_mut(t, "brings rows 31.7.1 and 31.7.2", "brings rows 31.7.1")), "a merge row not naming its rows passed"


def t_the_integration_rows_are_gits():
    """W154 (W132's condition 2): rows 31.1 to 33 are git's row for row, section 2's integration part is theirs, and no fill-in cell
    is left; the basis is git itself (the commits exist on fnd/int32) and the table."""
    texts = _texts()
    t = texts[CLASS]
    bad = p_integ(t) + p_integ_summary(t) + p_nofill(texts)
    assert not bad, bad
    r = {n: _line(t, "| %s |" % n) for n in ("31.1", "31.4.1", "31.6", "31.8", "31.9", "31.9.1", "32", "33")}
    assert p_integ(_mut(t, r["31.6"], r["31.6"].replace("| 2026-10-07 03:23:27 |", "| 2026-10-07 03:23:28 |", 1))), "a wrong date passed"
    assert p_integ(_mut(t, r["32"], r["32"].replace("| 2026-10-07 07:10:50 |", "| 2026-10-07 07:10:53 |", 1))), \
        "row 32 with the queue's clock in place of git's author date passed"
    assert p_integ(_mut(t, r["33"], r["33"].replace("| 7: ", "| 6: ", 1))), "row 33 with a wrong file count passed"
    # the sha cells through _cell, never a typed token (placeholders_check.py's deferral list types this module's count of the
    # candidate's token), so each mutant holds before the fill (the tokens) and after it (the commits the fill wrote)
    assert p_integ(_mut(t, r["33"], r["33"].replace("| %s |" % _cell(r["33"]), "| %s |" % _cell(r["32"]), 1))), "row 33 with row 32's sha cell passed"
    assert p_integ(_mut(t, r["32"], r["32"].replace("| %s |" % _cell(r["32"]), "| `%s` |" % CAND_AT[:8], 1))), "row 32 naming the candidate passed"
    assert p_integ(t.replace(r["31.9"] + "\n", "", 1)), "the unforeseen merge's row 31.9 dropped passed"
    assert p_integ(t.replace(r["31.9.1"] + "\n", "", 1)), "the commit the last merge brings dropped passed"
    assert p_integ(_mut(t, r["31.9"], r["31.9"].replace("| MERGE |", "| TEST |", 1))), "a merge not classed MERGE passed"
    assert p_integ(_mut(t, r["31.9.1"], r["31.9.1"].replace("| fnd/s32applier (", "| fnd/int32: (", 1))), "a brought commit outside its branch passed"
    assert p_integ(_mut(t, r["31.8"], r["31.8"].replace("reviewed files it touches (20)", "reviewed files it touches (19)", 1))), \
        "C1b counting the facts table's 19 reviewed files (the 60 without the L4-E9 output) passed"
    assert p_integ(_mut(t, r["31.6"], r["31.6"].replace("(row 14 the source row; in the delta cx46 read)", "(in the delta cx46 read)", 1))), \
        "C1's REVIEWED-INPUT CHANGED without its source row passed"
    assert p_integ(_mut(t, r["33"], r["33"].replace("rows 27 and 29 the source rows", "rows 27 and 34 the source rows", 1))), \
        "a source row that is not an earlier row passed"
    assert p_integ(_mut(t, r["31.4.1"], r["31.4.1"].replace("| `021a910b` / ", "| `021a910c` / ", 1))), "a short sha not its full sha's passed"
    assert p_integ(_mut(t, r["31.1"], r["31.1"].replace("; UNREVIEWED since cx46 |", " |", 1))), "a merge bringing cx46's files without UNREVIEWED passed"
    assert p_integ(_mut(t, "brings rows 20 to 24 and rows 31.4.1 to 31.4.12", "brings rows 20 to 24 and this record's later commits")), \
        "a merge not naming the rows it brings passed"
    assert p_integ_summary(_mut(t, "| integration total | 26 |", "| integration total | 25 |")), "a wrong integration total passed"
    assert p_integ_summary(_mut(t, "| `MERGE` | 7 | 7 |", "| `MERGE` | 6 | 7 |")), "a wrong integration class count passed"
    assert p_integ_summary(_mut(t, "; 70 file touches", "; 66 file touches")), "a wrong count of file touches passed"
    assert p_integ_summary(_mut(t, "**The whole table:** 60 rows", "**The whole table:** 59 rows")), "a wrong whole-table count passed"
    assert p_integ_summary(_mut(t, r["31.9"], r["31.9"].replace("| MERGE |", "| TEST |", 1))), "a re-classed row with the old counts passed"
    assert p_nofill(dict(texts, **{RESULT: texts[RESULT] + "\n[FILL: a value]\n"})), "a fill-in cell left passed"


def t_the_table_is_the_five_ranges_in_order_with_gits_columns_and_classes():
    order = _order()
    t = _read(CLASS)
    bad = p_coverage(t, order) + p_columns(t, order)
    assert not bad, bad
    row = [l for l in t.split("\n") if l.startswith("| 7 |")][0]
    assert p_coverage(t.replace(row + "\n", "", 1), order), "a dropped row passed"
    r16 = [l for l in t.split("\n") if l.startswith("| 16 |")][0]
    assert p_columns(t.replace(r16, r16.replace("| TOOLING + RECORD TEXT + TEST |", "| TOOLS + RECORD TEXT + TEST |"), 1), order), \
        "a class outside the fixed set passed"
    r3 = [l for l in t.split("\n") if l.startswith("| 3 |")][0]
    assert p_columns(t.replace(r3, r3.replace("UNREVIEWED since cx46", "unreviewed"), 1), order), \
        "a reviewed row without UNREVIEWED since cx46 passed"
    r8 = [l for l in t.split("\n") if l.startswith("| 8 |")][0]
    assert p_columns(t.replace(r8, r8.replace("| RECORD TEXT |", "| REVIEWED-INPUT CHANGED |"), 1), order), \
        "a REVIEWED-INPUT CHANGED row touching no reviewed file passed"
    assert p_columns(t.replace(r8, r8.replace("| 2026-10-06 15:42:51 |", "| 2026-10-06 15:42:52 |"), 1), order), "a wrong date passed"
    r2 = [l for l in t.split("\n") if l.startswith("| 2 |")][0]     # W78 (W75's F5): row 2's committer date is not its author date
    assert p_columns(t.replace(r2, r2.replace("| 2026-10-06 12:41:26 |", "| 2026-10-06 12:41:33 |"), 1), order), \
        "a committer date in place of the author date passed"
    # W85: W81's rows 13.1 to 13.4: a dotted row renumbered, a row of them without UNREVIEWED since cx46, one dropped
    r132 = _line(t, "| 13.2 |")
    assert p_coverage(t.replace(r132, r132.replace("| 13.2 |", "| 14 |", 1), 1), order), "a dotted row renumbered passed"
    r133 = _line(t, "| 13.3 |")
    assert p_columns(t.replace(r133, r133.replace("UNREVIEWED since cx46", "unreviewed"), 1), order), \
        "row 13.3, touching test_l8p.py and test_l8r2.py, passed without UNREVIEWED since cx46"
    assert p_columns(t.replace(r133, r133.replace("reviewed files it touches (2)", "reviewed files it touches (1)"), 1), order), \
        "row 13.3 counting one reviewed file passed"
    assert p_coverage(t.replace(_line(t, "| 13.4 |") + "\n", "", 1), order), "row 13.4 dropped passed"


def t_the_summary_and_the_bound_statement_are_the_tables():
    t = _read(CLASS)
    assert not p_summary(t), p_summary(t)
    assert p_summary(_mut(t, "| `TOOLING` | 15 | 18 |", "| `TOOLING` | 14 | 18 |")), "a wrong summary count passed"
    assert p_summary(t.replace("fnd/s32small, 4 rows: RECORD TEXT 3, TOOLING 1", "fnd/s32small, 4 rows: RECORD TEXT 2, TOOLING 2", 1)), \
        "a wrong per-branch count passed"
    assert p_summary(_mut(t, "16 RECORD TEXT first", "15 RECORD TEXT first")), \
        "a wrong statement count passed"
    assert p_summary(_mut(t, "(24 file touches, 17", "(23 file touches, 17")), "a wrong file-touch count passed"
    assert p_summary(_mut(t, "fnd/w34pdftext, 17 rows: RECORD TEXT 6, TEST 1, TOOLING 10", "fnd/w34pdftext, 13 rows: RECORD TEXT 5, TEST 1, TOOLING 7")), \
        "the per-branch line without W81's rows passed"
    r133 = _line(t, "| 13.3 |")       # W85: row 13.3 re-classed with the counts left as they are
    assert p_summary(t.replace(r133, r133.replace("| TOOLING + TEST |", "| REVIEWED-INPUT CHANGED + TOOLING + TEST |", 1), 1)), \
        "a re-classed W81 row with the old counts passed"
    assert p_summary(t.replace("(row 15, carrying row 14)", "(carrying row 14)", 1)), "an unnamed REVIEWED-INPUT CHANGED row passed"
    r = [l for l in t.split("\n") if l.startswith("| 8 |")][0]
    assert p_summary(t.replace(r, r.replace("| RECORD TEXT |", "| TOOLING |"), 1)), "a re-classed row with the old counts passed"


def t_every_count_typed_is_gits():
    _need_git()
    texts = _texts()
    order = _order()
    assert not p_counts(texts, order), p_counts(texts, order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "prints 17;", "prints 13;", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "171 extractions committed", "172 extractions committed", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "16:33:50, 53 s", "16:33:50, 54 s", order)
    t = texts[CLASS]
    assert not p_row_numbers(t), p_row_numbers(t)
    assert p_row_numbers(t.replace("68 committed extractions with their sidecars (136 files)",
                                   "68 committed extractions with their sidecars (138 files)", 1)), "a wrong file count in a reason passed"
    assert p_row_numbers(t.replace("(+69 -21)", "(+69 -20)", 1)), "a wrong line count in a reason passed"
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "Dates are the author dates", "Dates are the committer dates", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "(17 distinct files)", "(16 distinct files)", order)
    # W85: the tip's texts, W81's declaration-only modules, the vendor files
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "176 extractions committed", "175 extractions committed", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, RESULT, "in 3 declaration-only modules", "in 2 declaration-only modules", order)
    _mutant_refused(lambda tx, o: p_counts(tx, o), texts, CLASS, "The 352 vendor files", "The 342 vendor files", order)
    assert p_row_numbers(_mut(t, "`test_pdftext_input.py` (+528 -1)", "`test_pdftext_input.py` (+529 -1)")), "a wrong W81 line count passed"


def t_every_commit_named_is_in_the_histories_read_or_declared_outside_them():
    _need_git()
    texts = _texts()
    assert not p_commits_named(texts), p_commits_named(texts)
    _mutant_refused(p_commits_named, texts, RESULT, "`6dc69ad2`", "`6dc69ad3`")
    # W113 (W109's F4): the chain's base is named as itself; a near miss of it is no commit this record may name
    _mutant_refused(p_commits_named, texts, RESULT, "start (`be07863b`, a descendant", "start (`be07863c`, a descendant")
    # W128 (W109's phase 2 finding 4): the commits after the chain's stop are named as themselves; a near miss is refused
    _mutant_refused(p_commits_named, texts, CLASS, "by fnd/l3r5keep `2dcb4131` (row 31.7.1", "by fnd/l3r5keep `2dcb4132` (row 31.7.1")  # W154: the note no longer names section 3
    if _stage(texts[RESULT]):                  # W80: the commits the fill wrote are accepted only while p_filled accepts them
        base = _line(texts[RESULT], "| BASE ")
        _mutant_refused(p_commits_named, texts, RESULT, base, base.replace("| %s |" % _cell(base), "| `%s` |" % LINEAGE[:8], 1))


def t_every_quote_is_on_its_cited_line():
    _need_git()
    texts = _texts()
    assert not p_quotes(texts), p_quotes(texts)
    _mutant_refused(p_quotes, texts, CLASS, "`[E11PY:6019]`", "`[E11PY:6020]`")
    _mutant_refused(p_quotes, texts, RESULT, ":498` `\"Ready\" here means", ":497` `\"Ready\" here means")


def t_the_three_claims_are_quoted_verbatim_from_the_assessment():
    _need_git()
    result = _read(RESULT)
    lines = _show(ASSESS_AT, ASSESS)
    assert not p_claims(result, lines), p_claims(result, lines)
    if os.path.isfile(os.path.join(REPO, ASSESS)):            # the tree's assessment holds the three headings too
        tree = _read(ASSESS).split("\n")
        for words in CLAIMS.values():
            assert words in [l.rstrip() for l in tree], "the tree's assessment lacks %r" % words
    assert p_claims(result.replace("| Power-design closure | BLOCKED |", "| Power-design closure | CLOSED |", 1), lines), \
        "a changed claim passed"
    assert p_claims(result, [l.replace("NOT PASSED", "PASSED") for l in lines]), "a changed assessment line passed"


def t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote():
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    if not os.path.isdir(os.path.join(runs, "int32")):
        raise Skip("the coordinator's files (_runs) are not on this host")
    texts = _texts()
    assert not p_logs(texts, runs), p_logs(texts, runs)
    _mutant_refused(p_logs, texts, RESULT, "`round 1 would select: 31 pairs`", "`round 1 would select: 32 pairs`", runs)


def t_a_carried_change_names_a_reviewed_input_row_of_set_30():
    _need_git()
    t = _read(CLASS)
    s30 = _show(S30, S30C)
    assert not p_carried(t, s30), p_carried(t, s30)
    # the basis (W78): the coordinator's ruling on W75's F2 (queue, 21:03, reading A as ruled for set 31) classes row 15, whose tests quote
    # row 14's restated words into test_l9t5.py and test_l8p.py (files of cx46's delta), REVIEWED-INPUT CHANGED beside row 14
    assert [c[0] for c in _real(t) if _classes(c)[0] == RIC] == ["14", "15"], "the REVIEWED-INPUT CHANGED rows are not rows 14 and 15"
    assert p_carried(t.replace("set 30's row 8's change (`6b768b1e`", "set 30's row 9's change (`9cf3982a`", 1), s30), \
        "a source row that is a merge passed"
    assert p_carried(t.replace("this table's row 14's change (`4d07a401`", "this table's row 13's change (`b397aada`", 1), s30), \
        "a source row of this table that is not REVIEWED-INPUT CHANGED passed"
    # W80 (W79's N2, its mutant passed at b279819e): row 15 without the second sentence and its source, and without the first sentence's
    # old and new value and cx46 item, still REVIEWED-INPUT CHANGED
    assert p_carried(t.replace("classed REVIEWED-INPUT CHANGED under set 30's rule's second sentence as ruled (reading A; the coordinator's "
                               "ruling on W75's F2): it quotes this table's row 14's change (`4d07a401`, which carries set 30's row 8's)",
                               "classed REVIEWED-INPUT CHANGED: it quotes words", 1), s30), "a REVIEWED-INPUT CHANGED row with no basis passed"


def t_the_wider_readings_are_the_tables():
    _need_git()
    t = _read(CLASS)
    order = _order()
    assert not p_alternatives(t, order), p_alternatives(t, order)
    assert p_alternatives(_mut(t, "TEST 1, TOOLING 6)", "TEST 1, TOOLING 7)"), order), "a wrong first reading's total passed"
    assert p_alternatives(_mut(t, "REVIEWED-INPUT CHANGED 6, RECORD TEXT 14,", "REVIEWED-INPUT CHANGED 6, RECORD TEXT 15,"), order), \
        "a wrong second reading's total passed"
    assert p_alternatives(_mut(t, "11, 13.1 to 13.3, 14 to 16, 25 to 27 and 29)", "11, 14 to 16, 25 to 27 and 29)"), order), \
        "a list of rows touching the reviewed tree without W81's rows passed"
    assert p_alternatives(_mut(t, "13.2, 13.3, 25, 27 and 29 would be", "25, 27 and 29 would be"), order), \
        "the first wider reading without W81's touching rows passed"
    # W80 (W79's N1, its probe passed at b279819e): row 26 listed for row 27, the same first class, so the totals do not move
    assert p_alternatives(t.replace("finds the same 6 rows, 7, 9, 14, 15, 27 and 29", "finds the same 6 rows, 7, 9, 14, 15, 26 and 29", 1), order), \
        "a listed row that no clause says carries a change passed"
    assert p_alternatives(t.replace("rows 27 and 29 carry row 25's new KEY", "rows 27 and 29 carry row 28's new KEY", 1), order), \
        "a carried change from a later row passed"


def t_the_declared_tokens_are_the_fill_tools():
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    tool = os.path.join(os.environ.get("MESHSAT_BIN") or os.path.join(os.path.dirname(runs), "_bin"), "fill_res.py")
    if not os.path.isfile(tool):
        raise Skip("the coordinator's fill tool (_bin/fill_res.py) is not on this host")
    src = open(tool, encoding="utf-8").read()
    assert not p_fill(src), p_fill(src)
    assert p_fill(src.replace("|ADOPTION|", "|", 1)), "a tool that fills one token fewer passed"
    assert p_fill(src.replace('R32 + "CLASSIFICATION.md"', 'R32 + "CLASS.md"', 1)), "a tool whose set 32 files are not this record's passed"


def t_the_chain_merges_the_five_branches_pinned_inside_their_ranges():
    _need_git()
    runs = os.environ.get("MESHSAT_RUNS") or os.path.join(os.path.dirname(REPO), "_runs")
    sh_p = os.path.join(runs, "int32", "chain.sh")
    if not os.path.isfile(sh_p):
        raise Skip("the coordinator's chain (_runs/int32/chain.sh) is not on this host")
    sh = open(sh_p, encoding="utf-8").read()
    assert not p_chain(sh), p_chain(sh)
    m = re.search(r"^SRC_ATTR=\$\{SRC_ATTR:-([0-9a-f]+)\}", sh, re.M)
    assert p_chain(sh.replace(m.group(0), "SRC_ATTR=${SRC_ATTR:-%s}" % BRANCHES[0][1][:8], 1)), "a pin outside its range passed"
    assert p_chain(sh.replace('merge_one s32attr "$PIN_', 'merge_one s32attrX "$PIN_', 1)), "a sixth merge label passed"


def _pytest(fn):
    def run():
        try:
            fn()
        except Skip as e:
            import pytest
            pytest.skip(str(e))
    run.__name__ = "test_" + fn.__name__[2:]
    run.__doc__ = fn.__doc__
    return run


test_the_records_carry_no_dash_and_open_with_their_state_lines = _pytest(t_the_records_carry_no_dash_and_open_with_their_state_lines)
test_every_placeholder_is_a_declared_token = _pytest(t_every_placeholder_is_a_declared_token)
test_the_integration_rows_and_the_filled_commits = _pytest(t_the_integration_rows_and_the_filled_commits)
test_the_rule_is_set_30s_line_11_verbatim_read_as_ruled = _pytest(t_the_rule_is_set_30s_line_11_verbatim_read_as_ruled)
test_the_rows_written_from_git_after_the_chains_stop_are_gits = _pytest(t_the_rows_written_from_git_after_the_chains_stop_are_gits)
test_the_integration_rows_are_gits = _pytest(t_the_integration_rows_are_gits)
test_the_table_is_the_five_ranges_in_order_with_gits_columns_and_classes = _pytest(
    t_the_table_is_the_five_ranges_in_order_with_gits_columns_and_classes)
test_the_summary_and_the_bound_statement_are_the_tables = _pytest(t_the_summary_and_the_bound_statement_are_the_tables)
test_every_count_typed_is_gits = _pytest(t_every_count_typed_is_gits)
test_every_commit_named_is_in_the_histories_read_or_declared_outside_them = _pytest(
    t_every_commit_named_is_in_the_histories_read_or_declared_outside_them)
test_every_quote_is_on_its_cited_line = _pytest(t_every_quote_is_on_its_cited_line)
test_the_three_claims_are_quoted_verbatim_from_the_assessment = _pytest(t_the_three_claims_are_quoted_verbatim_from_the_assessment)
test_every_cited_file_of_the_coordinator_exists_and_carries_its_quote = _pytest(
    t_every_cited_file_of_the_coordinator_exists_and_carries_its_quote)
test_a_carried_change_names_a_reviewed_input_row_of_set_30 = _pytest(t_a_carried_change_names_a_reviewed_input_row_of_set_30)
test_the_wider_readings_are_the_tables = _pytest(t_the_wider_readings_are_the_tables)
test_the_declared_tokens_are_the_fill_tools = _pytest(t_the_declared_tokens_are_the_fill_tools)
test_the_chain_merges_the_five_branches_pinned_inside_their_ranges = _pytest(
    t_the_chain_merges_the_five_branches_pinned_inside_their_ranges)
