#!/usr/bin/env python3
"""Set 30's records pack (MESHSAT-1357, 6 October 2026): what the two drafts cite exists, what they quote is quoted, what they classify
is complete.

The drafts are `v2/docs/records/int30/RESULT.draft2.md` (the review bound to the integrated revision: the revisions, every commit after
the reviewed revision classified, the equivalence, the gate lines left as placeholders) and
`v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md` (the P0 list's revision 3 refreshed to the candidate's commit 2a). They cite
`path:N` or `path:N-M` as line N (to M) of that file at their base BASE, `<sha>:path:N` as a line at that revision, and a bare `:N` as a
line of the path cited last before it; a `<worktrees>/...` token names a file outside the tree, so a bare `:N` after it is not read here.
The anchors are read with git at their revision, never in the working tree, which later integration commits move; the drafts themselves
are read in the tree. If the coordinator renames a draft at adoption, DRAFTS below follows it.

What fails here: a cited path or line range that does not exist at its revision; a quoted anchor that is not on its cited lines; a
commit named in a table that is not in the repository; a classification that misses, adds or double-counts a commit after the reviewed
revision or after the base, a merge classed (a) while it carries a (b) commit, an (a) row touching a generator or a circuit draft, or an
(a) row touching a test without saying so; totals that do not match the table; a check's verdict quoted in words the filed check does
not contain; a P0 list that drops, reorders or rewords one of revision 2's twelve rows; a placeholder filled; an em or en dash; a
closure claimed.

The tables name main's four commits after `0d5f855e` and set 31's (S1 to S4); the integrated candidate holds them in its history once the
runbook's merge of main is made. No pytest is needed (tests/run.py runs the `t_` functions); `test_` aliases let pytest collect the same
functions. A checkout without git or without BASE raises Skip."""
import json
import os
import re
import subprocess

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REVIEWED = "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"      # cx46's candidate
BASE = "bbba3e53e396d3fe0f8ddd2f38d0c169bcc99c45"          # the candidate's integration commit 2a: the drafts' base
S31 = "6fe398e9f624160429411e975c26564e553714d3"           # the candidate branch's tip when the drafts were written (set 31 merged)
RESULT = "v2/docs/records/int30/RESULT.draft2.md"
LIST3 = "v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md"
DRAFTS = (RESULT, LIST3)
LIST2 = "v2/docs/records/l4close/P0-POWER-LIST.md"
CX45 = "v2/docs/records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md"
CX46 = "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
OWN = "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md"
PAGE = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
GEN = "v2/docs/records/l4e9/l4e9_power_path.py"
GOUT = "v2/docs/records/l4e9/l4e9_power_path.out"
APPLIER = "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py"
CON = "v2/docs/records/l9t5/l9t5_connected.out"
T10 = "v2/docs/records/l9t5/l9t5_t10.out"
F01 = "v2/docs/records/l9t5/l9t5_f01.out"
S31REC = "v2/docs/records/l4e9/SET31-CHANGES.md"
PLACEHOLDERS = ("__INTEGRATED__", "__COMMIT2B__", "__REKEY__", "__GUARD_RECORD__", "__GUARD_CHECK__", "__PASSA__", "__PASSB__",
                "__RUNNER__", "__GATE__", "__PROMO__")

# (revision, path, first line, last line, words that must be on those lines, whitespace flattened): the anchors the drafts lean on
ANCHORS = [
    (BASE, CX46, 8, 8, '"base_commit": "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e"'),
    (BASE, CX46, 10, 10, '"summary": "P0 RECHECK: CORRECTIONS NOT CLOSED.'),
    (BASE, CX46, 183, 183, "retain or reproduce successful byte-identical repeated output runs on these inputs"),
    (BASE, CX46, 206, 206, "Do not repeat this review method or relabel these tasks as qualification only."),
    (BASE, CX45, 8, 8, '"base_commit": "e132db0e73da723cf18d32788aa8c9252c0bcfbe"'),
    (BASE, CX45, 10, 10, '"summary": "P0 CANDIDATE: NOT CONFIRMED.'),
    (BASE, CX45, 20, 20, "HEAD is 06077cee85d0ed44c74c2a06c9fbb2030a0dedbc"),
    (BASE, CX45, 105, 105, "U5's residual internal-amplifier output is properly PROVISIONAL on S3."),
    (BASE, OWN, 844, 844, "Use the existing integration gate to record the reviewed and integrated revisions and the intervening changes."),
    (BASE, OWN, 844, 844, "Passing the software suite alone cannot transfer an engineering verdict to altered claims."),
    (BASE, OWN, 834, 838, "B2 need not remain an outstanding owner action"),
    (BASE, OWN, 798, 798, "Assess desk-handover readiness separately from power-design closure and fabrication release."),
    (BASE, OWN, 788, 788, "The Layer 4 desk-handover gate can then be assessed"),
    (BASE, "v2/docs/EXECUTION-CONSTITUTION.md", 23, 23, "Report engineering-handover readiness, power-design closure and fabrication release separately"),
    (BASE, "v2/docs/EXECUTION-CONSTITUTION.md", 76, 76, "The required order is"),
    (BASE, CON, 4, 4, "power-design closure and fabrication release stay BLOCKED"),
    (BASE, CON, 21, 21, "2aa78a957e497677 v2/docs/records/l9t5/l9t5_f01.out"),
    (BASE, CON, 336, 336, "THE CONNECTED ELECTRICAL VERDICT: REMAINING ENGINEERING."),
    (BASE, CON, 350, 350, "rev X on V-B20"),
    (BASE, CON, 359, 360, "no owner item"),
    (BASE, CON, 361, 362, "L4-E9's change-list rows: drafted"),
    (BASE, CON, 361, 362, "L4-E9's own output refuses on this tree at its L4-E11 pin"),
    (BASE, "v2/docs/records/l9t5/l9t5_f01_drafts.out", 11, 11, "3f373dc60e39f6f4 v2/docs/records/l9t5/l9t5_f01.py"),
    (BASE, "v2/docs/records/l9t5/README.md", 1, 1, "CANDIDATE READY 3: ac8efbca"),
    (BASE, "v2/docs/records/l9t5/README.md", 1, 1, "L9T5-F13, F16 and F17 OPEN"),
    (BASE, "v2/docs/records/l9t5/stability/DIGESTS-cr3.txt", 1, 1, "started 22:26, pass 1 ended 22:36, pass 2 22:45"),
    (BASE, "v2/docs/records/l9t5/stability/DIGESTS-cr3.txt", 15, 15, "v2/docs/records/l9t5/l9t5_f01.out pass 1: sha256=2aa78a957e497677"),
    (BASE, PAGE, 883, 883, "The power-design closure gate: BLOCKED."),
    (BASE, PAGE, 884, 884, "Fabrication release: BLOCKED."),
    (BASE, PAGE, 972, 972, "Layer 4's power architecture closes: NO"),
    (BASE, PAGE, 967, 967, "three material defects are open"),
    (BASE, PAGE, 975, 976, "none open since the update round"),
    (BASE, PAGE, 979, 979, "criterion 2 has no open defect"),
    (BASE, PAGE, 840, 840, "| D-16 |"),
    (BASE, PAGE, 1283, 1283, "| D-16 | OPEN | KNOWN ENGINEERING DEFECT |"),
    (BASE, PAGE, 1278, 1278, "ASSIGN to the supplier's phase 1, task P1-1"),
    (BASE, PAGE, 422, 422, "**The P0 round (record l9t5, Slot A, 5 October 2026"),
    (BASE, REG, 314, 314, "| R-220 |"),
    (BASE, REG, 338, 338, "| R-245 |"),
    (BASE, REG, 334, 334, "the receiving company's engineering item E-1 (its later validation step is S1"),
    (BASE, GEN, 112, 112, "aab5ae6b3b9ef0d10ad24b9af6d1dca5661125cdcfdbb16066407ad53bef86c4"),
    (BASE, GEN, 122, 122, "1938c400d1404eae57cb05cfe4460829f5c2799f0332770ee75ad1e1c1ebb6f6"),
    (BASE, GEN, 125, 125, "31883eca9d5309b533bbbc6e204a8cebf1a8efc509b6a804f906da2c5dcc05cb"),
    (BASE, GEN, 180, 180, '"l4e7p0": ("v2/docs/records/l4e7/l4e7_p0sol.out", "28a5b9fd93dd7b50'),
    (BASE, GEN, 2418, 2418, 'one(T["l4e7p0"])'),
    (BASE, GEN, 4288, 4296, "OPEN: AN UNRESOLVED PROTECTION DEFECT in the present model"),
    (BASE, GEN, 4294, 4294, "and an owner item"),
    (BASE, GEN, 4391, 4394, "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7 (R-240"),
    (BASE, GEN, 5614, 5614, 'elif state == "WITHDRAWN"'),
    (BASE, GEN, 5630, 5630, "ASSIGN to the receiving company's remaining engineering item E-1"),
    (BASE, GEN, 5635, 5635, "VERIFY at layer 9 and on the bench"),
    (BASE, GEN, 6609, 6610, "unapproved partial interface proposal, the owner's item"),
    (BASE, GOUT, 560, 560, "constraint: three material defects are open"),
    (BASE, GOUT, 572, 572, "17, 2 open; 5 addressed in drafts (D-11, D-13, D-14, D-16, D-15"),
    (BASE, GOUT, 600, 600, "and an owner item"),
    (BASE, GOUT, 615, 615, "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7"),
    (BASE, GOUT, 1017, 1017, "criterion 2 CONDITIONAL with 2 defects open"),
    (BASE, GOUT, 1310, 1310, "117 changes; none APPLIED"),
    (BASE, APPLIER, 23, 23, "unapproved PARTIAL proposal"),
    (BASE, APPLIER, 47, 47, "PY_EDITS = ["),
    (REVIEWED, APPLIER, 47, 47, "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7"),
    (BASE, APPLIER, 107, 107, "def applied_state(root):"),
    (BASE, APPLIER, 117, 121, "the register carries R-220 but the applied texts are not this draft's"),
    (BASE, APPLIER, 160, 160, "APPLIED BEFORE"),
    (BASE, "v2/docs/records/l9t5/l9t5_connected.py", 178, 178, "patch_all(ROOT)"),
    (BASE, "v2/docs/records/l4close/REMAINING-ENGINEERING.md", 11, 16, "designs nothing, computes no new figure, consumes no review and changes no verdict"),
    (BASE, "v2/docs/records/l4close/REMAINING-ENGINEERING.md", 85, 85, "## 1. The twelve cx46 findings NOT CLOSED"),
    (BASE, "v2/docs/records/l4close/REMAINING-ENGINEERING.md", 619, 619, "## 6. Gaps and contradictions"),
    (BASE, "v2/ecad/tools/tests/test_l9t5.py", 956, 956, "which is NOT a bound on the cap"),
    (BASE, "v2/docs/records/h3/public_check.py", 14, 14, "An answer is true at the time printed on its first line, not later"),
    (BASE, "v2/docs/records/int29/RESULT.md", 13, 13, "four historical outputs declared unbound by path"),
    (BASE, "v2/docs/records/int29/RESULT.md", 67, 67, "## 5. Five claims, apart"),
    (BASE, "v2/docs/records/l4e7/B2-PRESENCE.md", 4, 6, "UNSELECTED and WITHDRAWN AS DRAFTED"),
    (BASE, T10, 620, 620, "127.54 C, OVER 125 C"),
    (BASE, T10, 645, 645, "(f) THE ROWS MADE TO AGREE"),
    # W53 (6 October 2026): kept. Basis: this anchor is read with git at BASE (bbba3e53), where the output printed these words, and
    # RESULT.draft2.md quotes them as that revision's; W53 restates the generator (l9t5_t10.py 10j: "Q3: cx45 'P0-3: NOT CONFIRMED',
    # cx46's items 5 to 8 'NOT CLOSED'", W38's F10), which moves the tree's output at set 32's regeneration, never BASE's bytes
    (BASE, T10, 662, 662, "DISPOSITION (10j, after cx46): cx45's Q3 NOT CLOSED"),
    (BASE, T10, 684, 684, "the B7b residual reads 120.0 C on rev V, inside 125 C"),
    (REVIEWED, T10, 655, 655, "the B7b residual is tolerated by SESSION decision L9T5-D5"),
    (BASE, F01, 134, 134, "which is NOT a bound on the cap"),
    (BASE, F01, 145, 145, "need 15.1308 V"),
    (BASE, F01, 226, 226, "at most 6.351 A (the band's floor 6.3518 A rounded DOWN, cx46)"),
    (BASE, "v2/docs/records/l9t5/l9t5_case.out", 193, 193, "need 15.1308 V"),
    (BASE, LIST2, 18, 18, "the case at 15.1307 V"),
    (BASE, "v2/docs/records/l8r2/l8r2_dist.out", 125, 125, "DISPOSITION OF V6-B1 AFTER cx46"),
    (BASE, "v2/docs/records/l8p/l8p_c4.out", 355, 355, "DISPOSITION (10c, after the recheck cx46"),
    (BASE, "v2/docs/records/l4e11/l4e11_power.out", 1459, 1459, "E11-37 STAYS OPEN"),
    (BASE, "v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md", 103, 103, "TP-E11-29"),
    (BASE, "v2/docs/test-procedures/TP-E11-29.md", 19, 19, "**NOT EXECUTABLE.**"),
    (S31, GOUT, 600, 600, "Route B2 (not a baseline row) is UNSELECTED and WITHDRAWN AS DRAFTED, with no protection credit and no owner item"),
    (S31, GEN, 4243, 4244, "Route B2 (not a baseline row) is UNSELECTED and"),
    (S31, PAGE, 1005, 1005, "Layer 4's power architecture closes: NO"),
    (S31, PAGE, 1007, 1007, "Set 29's inconsistency, corrected in the text"),
    (S31, PAGE, 1384, 1384, "ASSIGN to the receiving company's remaining engineering item E-1"),
    (S31, PAGE, 1389, 1389, "| D-16 | ADDRESSED IN DRAFTS |"),
    (S31, REG, 336, 336, "item l4e7's E-1"),
    (S31, GOUT, 559, 559, "bounded supporting calculations: FAIL;"),
    (S31, GOUT, 560, 560, "two material defects are open: D-10 (E-1) and D-17 (RE-2)"),
    (S31, GOUT, 621, 621, "OPEN (REMAINING ENGINEERING, RE-2): a correction DRAFTED and PROVISIONAL"),
    (S31, S31REC, 16, 16, "every one here narrows a claim or states an open state"),
    (S31, S31REC, 20, 20, "**How it was run.**"),
    (S31, S31REC, 32, 32, "criterion 2 CONDITIONAL to FAIL"),
    (S31, S31REC, 33, 33, "D-10, D-16 and D-17 restated"),
    (S31, S31REC, 41, 41, "D-16 ADDRESSED IN DRAFTS"),
    (S31, S31REC, 45, 45, "R-246, board P's ideal diode (DD-5)"),
    (S31, S31REC, 54, 54, "D-10 as P0-7 states it"),
    (S31, S31REC, 60, 60, "**The test expectations changed"),
    (S31, S31REC, 80, 81, "still NOT EXECUTABLE until its quotation and check are re-taken against the restatement and a supplier agrees the fixture requirement"),
    (S31, S31REC, 118, 119, "records l4e10 and l4e11 pin this page's sha256"),
]


def _git(*a, ok=(0,)):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git here (%s)" % e)
    if r.returncode not in ok:
        raise Skip("git %s: %s" % (" ".join(a[:2]), r.stderr.decode()[:100].strip()))
    return r


def _need_history():
    if _git("cat-file", "-e", BASE + "^{commit}", ok=(0, 1, 128)).returncode != 0:
        raise Skip("this checkout does not hold the drafts' base %s" % BASE[:8])


def _is_commit(s):
    return _git("cat-file", "-e", s + "^{commit}", ok=(0, 1, 128)).returncode == 0


_BLOBS = {}


def _blob(rev, path):
    if (rev, path) not in _BLOBS:
        r = _git("show", "%s:%s" % (rev, path), ok=(0, 128))
        _BLOBS[(rev, path)] = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
    return _BLOBS[(rev, path)]


def _draft(path):
    p = os.path.join(REPO, path)
    if not os.path.exists(p):
        raise AssertionError("the draft %s is missing" % path)
    return open(p, encoding="utf-8").read()


def _flat(s):
    return " ".join(s.split())


_TOK = re.compile(r"`(?:([0-9a-f]{8}):)?(v2/[^`\s:]+)(?::(\d+)(?:-(\d+))?)?`|`:(\d+)(?:-(\d+))?`|`<worktrees>/[^`]*`")


def _citations(text):
    """[(revision, path, first line or None, last line or None)]; a bare `:N` is resolved to the path cited last before it, and is
    skipped (revision None) after a `<worktrees>/...` token"""
    out, last = [], None
    for m in _TOK.finditer(text):
        if m.group(2):
            rev = m.group(1) or BASE
            last = (rev, m.group(2).rstrip("/.,;"))
            a = int(m.group(3)) if m.group(3) else None
            out.append((last[0], last[1], a, int(m.group(4)) if m.group(4) else a))
        elif m.group(5):
            assert last is not None, "a bare line anchor `:%s` before any cited path" % m.group(5)
            if last[0] is None:
                continue                                  # a line of a file outside the tree
            a = int(m.group(5))
            out.append((last[0], last[1], a, int(m.group(6)) if m.group(6) else a))
        else:
            last = (None, None)
    return out


def t_the_drafts_exist_carry_no_dash_keep_the_placeholders_and_claim_no_closure():
    for d in DRAFTS:
        t = _draft(d)
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % d
        assert "BLOCKED" in t, "%s does not state the blocked gates" % d
        for bad in ("closure: PASS", "closure gate: PASS", "release: PASS", "fabrication release: READY", "closure is reached",
                    "power architecture closes: YES", "ACCEPTED AS CLOSED"):
            assert bad not in t, "%s claims %r" % (d, bad)
        for priv in ("/home/", "/tmp/"):
            assert priv not in t, "%s names a host path (%s)" % (d, priv)
    flat = _flat(_draft(RESULT).replace("*", ""))
    assert "Power-design closure: BLOCKED. Fabrication release: BLOCKED" in flat
    assert "Promotion of set 30 closes no power item and releases nothing." in flat
    for p in PLACEHOLDERS:
        assert p in _draft(RESULT), "the placeholder %s is not kept literal in %s" % (p, RESULT)
    assert "Power-design closure: BLOCKED. Fabrication release: BLOCKED" in _flat(_draft(LIST3).replace("*", ""))


def t_every_cited_path_and_line_range_exists_at_its_revision():
    _need_history()
    n = 0
    for d in DRAFTS:
        for rev, path, a, b in _citations(_draft(d)):
            if path in DRAFTS:
                assert a is None, "%s cites a line of a draft (%s:%s); drafts are cited by section" % (d, path, a)
                assert os.path.exists(os.path.join(REPO, path)), path
                continue
            assert _is_commit(rev), "%s cites revision %s, which is not a commit here" % (d, rev)
            kind = _git("cat-file", "-t", "%s:%s" % (rev, path), ok=(0, 128))
            assert kind.returncode == 0, "%s cites %s, which is not in the tree at %s" % (d, path, rev[:8])
            if a is not None:
                assert kind.stdout.decode().strip() == "blob", "%s cites a line of the folder %s" % (d, path)
                body = _blob(rev, path)
                lines = body.count("\n") + (0 if body.endswith("\n") else 1)
                assert 1 <= a <= b <= lines, "%s cites %s:%d-%d; the file has %d lines at %s" % (d, path, a, b, lines, rev[:8])
            n += 1
    assert n > 200, "too few citations read (%d): the citation reader no longer finds them" % n


def t_the_quoted_anchors_are_on_their_cited_lines():
    _need_history()
    for rev, path, a, b, text in ANCHORS:
        assert _is_commit(rev), "%s is not a commit here" % rev[:8]
        body = _blob(rev, path)
        assert body is not None, "%s is not at %s" % (path, rev[:8])
        got = _flat(" ".join(body.split("\n")[a - 1:b]))
        assert _flat(text) in got, "%s:%d-%d at %s does not read %r (it reads %r)" % (path, a, b, rev[:8], text, got[:160])


def t_every_commit_named_in_a_table_is_in_the_repository():
    _need_history()
    seen = set()
    for d in DRAFTS:
        for line in _draft(d).splitlines():
            if not line.startswith("|"):
                continue
            for tok in re.findall(r"`([0-9a-f]+)`", line):
                if len(tok) in (8, 40):                     # 16 and 64 characters are digests, not commits
                    seen.add(tok)
    assert {REVIEWED[:8], BASE[:8], "06077cee", "e132db0e", S31[:8]} <= {s[:8] for s in seen}, "the bound revisions are not named"
    missing = sorted(s for s in seen if not _is_commit(s))
    assert not missing, "named in a table but not a commit here: %s" % missing


def _rows(prefix):
    """{40-hex sha: (row id, class cell)} of the RESULT's classification rows whose id matches prefix"""
    rows = {}
    for line in _draft(RESULT).splitlines():
        m = re.match(r"^\| (%s) \| `([0-9a-f]{40})` \|" % prefix, line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cls = cells[5]
        assert cls.startswith("(a)") or cls.startswith("(b)"), "row %s's class cell reads %r" % (m.group(1), cls[:40])
        assert m.group(2) not in rows, "%s is classified twice" % m.group(2)
        rows[m.group(2)] = (m.group(1), cls)
    return rows


def _check_classes(rows):
    for sha, (rid, cls) in rows.items():
        parents = _git("rev-list", "--parents", "-n", "1", sha).stdout.decode().split()[1:]
        files = _git("show", "--format=", "--name-only", "--first-parent", sha).stdout.decode().split()
        if cls.startswith("(a)"):
            assert not any("/apply_gen_sch_" in f or re.search(r"/gen_sch_[a-z]+\.py$", f) for f in files), (
                "row %s is classed (a) but touches a circuit draft or a generator" % rid)
            if any(f.startswith("v2/ecad/tools/tests/") for f in files):
                assert "test" in cls, "row %s is classed (a) and touches a test without saying so" % rid
        for p in parents[1:]:
            carried = _git("rev-list", "%s..%s" % (parents[0], p)).stdout.decode().split()
            if any(rows.get(c, ("", ""))[1].startswith("(b)") for c in carried):
                assert cls.startswith("(b)"), "the merge %s carries a substantive commit but is classed %s" % (rid, cls[:3])


def t_the_classification_covers_exactly_the_commits_after_the_reviewed_revision_and_after_the_base():
    _need_history()
    rows = _rows(r"\d+")
    after = _git("rev-list", "%s..%s" % (REVIEWED, BASE)).stdout.decode().split()
    assert after and sorted(rows) == sorted(after), "classified %d, the history has %d: missing %s, extra %s" % (
        len(rows), len(after), sorted(set(after) - set(rows))[:3], sorted(set(rows) - set(after))[:3])
    na = sum(1 for _r, c in rows.values() if c.startswith("(a)"))
    nb = sum(1 for _r, c in rows.values() if c.startswith("(b)"))
    flat = _flat(_draft(RESULT))
    assert "(a) BINDINGS OR PRESENTATION %d; (b) SUBSTANTIVE CHANGE %d." % (na, nb) in flat.replace("*", ""), "the counts line"
    assert "**Totals in this history:** (a) %d:" % na in _draft(RESULT) and "(b) %d: rows" % nb in flat, "the totals line"
    _check_classes(rows)
    if not _is_commit(S31):
        raise AssertionError("the set 31 merge %s is not a commit here" % S31[:8])
    srows = _rows(r"S\d")
    s_after = _git("rev-list", "%s..%s" % (BASE, S31)).stdout.decode().split()
    assert sorted(srows) == sorted(s_after), "rows S cover %d commits, %s..%s holds %d" % (len(srows), BASE[:8], S31[:8], len(s_after))
    _check_classes(dict(list(rows.items()) + list(srows.items())))
    mrows = _rows(r"M\d")
    for sha in mrows:
        assert _is_commit(sha), sha
        files = _git("show", "--format=", "--name-only", sha).stdout.decode().split()
        if mrows[sha][1].startswith("(a) UNRELATED"):
            assert not any(f.startswith("v2/") for f in files), "row %s is UNRELATED but touches v2/" % mrows[sha][0]


def t_the_quoted_verdicts_are_the_checks_own_words():
    _need_history()
    cx45, cx46 = _blob(BASE, CX45), _blob(BASE, CX46)
    assert cx45 and cx46
    flat45, flat46 = _flat(cx45), _flat(cx46)
    n = 0
    for line in _draft(LIST3).splitlines():
        if not re.match(r"^\| (P0-\d|U-0\d|E11-29) \|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        for col, src in ((4, flat45), (5, flat46)):
            for q in re.findall(r'"([^"]+)"', cells[col]):
                assert _flat(q) in src, "the list's quote %r is not in the filed check" % q[:60]
                n += 1
    assert n >= 8, "too few quoted verdicts read (%d)" % n
    for q in ("P0 RECHECK: CORRECTIONS NOT CLOSED.", "P0 CANDIDATE: NOT CONFIRMED."):
        assert q in _draft(RESULT) and (q in flat45 or q in flat46)
    J = json.loads(cx46.split("```json", 1)[1].split("```", 1)[0])
    state = {c["item"].split(".")[0]: c["item"].rsplit(": ", 1)[1] for c in J["classification"]}
    closed = sorted(int(k.split()[0]) for k, v in state.items() if v == "CLOSED BY THE CORRECTION")
    cond = sorted(int(k.split()[0]) for k, v in state.items() if v == "CLOSED AS CONDITIONAL")
    assert closed == [3, 11, 12, 15] and cond == [14, 16], (closed, cond)
    assert "CLOSED BY THE CORRECTION 3, 11, 12, 15 (four); CLOSED AS CONDITIONAL 14, 16 (two)" in _flat(_draft(RESULT))


def t_the_list_keeps_revision_2s_twelve_rows_and_names_its_base():
    _need_history()
    rev2 = _blob(BASE, LIST2)
    ids2 = re.findall(r"^\| (P0-\d|U-0\d|E11-29) \|", rev2, re.M)
    ids3 = re.findall(r"^\| (P0-\d|U-0\d|E11-29) \|", _draft(LIST3), re.M)
    assert len(ids2) == 12 and ids3 == ids2, (ids2, ids3)
    for line in _draft(LIST3).splitlines():
        m = re.match(r"^\| (P0-\d|U-0\d|E11-29) \| ([^|]+) \| ([^|]+) \|", line)
        if m:
            row2 = [r for r in rev2.splitlines() if r.startswith("| %s |" % m.group(1))][0]
            c2 = [c.strip() for c in row2.strip().strip("|").split("|")]
            assert m.group(2).strip() == c2[1] and m.group(3).strip() == c2[9], "%s's finding or class differs from revision 2" % m.group(1)
            state = [c.strip() for c in line.strip().strip("|").split("|")][7]
            assert any(w in state for w in ("REMAINING ENGINEERING", "CONDITIONAL", "CLOSED IN SCOPE", "EXTERNAL", "OPEN")), (
                "%s has no state word" % m.group(1))
    head = _flat(_draft(LIST3).split("\n| Id |", 1)[0])
    assert ("Base: `%s`" % BASE) in head.replace("*", ""), "the list does not name its base"
    assert "`path:N` is line N at `bbba3e53`" in head, "the list's citation base is not bbba3e53"
    assert "RESULT.draft.md" not in _draft(LIST3), "the list still points at the first draft's file"


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


test_the_drafts_exist_carry_no_dash_keep_the_placeholders_and_claim_no_closure = _pytest(
    t_the_drafts_exist_carry_no_dash_keep_the_placeholders_and_claim_no_closure)
test_every_cited_path_and_line_range_exists_at_its_revision = _pytest(t_every_cited_path_and_line_range_exists_at_its_revision)
test_the_quoted_anchors_are_on_their_cited_lines = _pytest(t_the_quoted_anchors_are_on_their_cited_lines)
test_every_commit_named_in_a_table_is_in_the_repository = _pytest(t_every_commit_named_in_a_table_is_in_the_repository)
test_the_classification_covers_exactly_the_commits_after_the_reviewed_revision_and_after_the_base = _pytest(
    t_the_classification_covers_exactly_the_commits_after_the_reviewed_revision_and_after_the_base)
test_the_quoted_verdicts_are_the_checks_own_words = _pytest(t_the_quoted_verdicts_are_the_checks_own_words)
test_the_list_keeps_revision_2s_twelve_rows_and_names_its_base = _pytest(t_the_list_keeps_revision_2s_twelve_rows_and_names_its_base)
