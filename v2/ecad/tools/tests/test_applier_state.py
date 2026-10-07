"""Record l9t5's change-list draft apply_l4e9_changelist_p0.py held by fixtures: its in-memory patch of the pristine tree, its
applied-state reader and its refusals (worker W2 of the P0 round, MESHSAT-1357, 6 October 2026; v2/docs/records/l9t5/).

The draft adds L4-E9's change-list rows R-220 to R-239 and R-242 to R-245 (no R-241: route B2 is out of the baseline; R-240 was in
the tree before it) to the register, edits the script and puts the P0 note above the page's change-list table. Its history, which
each test below names as its evidence basis:
  - commit 3d2746c9, the last commit that carried the three files unapplied (the parent of 7070f106);
  - commit 7070f106 (set 30's integration 1) applied the draft to the tree and, in the same commit, named E-1 in the applied R-240
    row's item as record l4e7 names it (its subject classifies that one edit);
  - commit bbba3e53 (integration 2a) gave the draft an applied-state reader, so that its callers (l9t5_connected.py's
    change_list_order() and test_l9t5's _l4e9()) read the change list on the integrated tree: --check reads APPLIED, --write refuses;
  - commit 53a68c7c (integration 2c) made that reader test the PRESENCE of every row the draft adds (by id) and of the page's P0
    note, not the verbatim texts, because set 31 edited the applied texts;
  - the owner's part 25 of 5 October 2026 (v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md): the integration gate binds the
    reviewed and the integrated revisions with the intervening changes classified; test 8 binds the draft to what 7070f106 wrote;
  - commit d83d9f2d (integration 2b, D1) made the reader decide on the presence of EVERY added id (none = pristine, all = applied,
    some = refused naming the missing ids) where its parent 6bc4424e decided on R-220 alone; the tests t_d1_* hold that case,
    which W16's review of 2b (finding 3) found untested, with a mutant and the parent's draft read from history.

Every fixture is a minimal repository root in a temporary directory: the three files under v2/docs/records/l4e9/ (the tree's own,
or the committed ones at 3d2746c9 read from this repository's history), the helper v2/docs/records/_lib/pdftext.py copied from
this tree (the tree's generator loads it at import since W34's acdcb22e; see HELPER) and `git init`, because L4-E9's generator finds
its tree with `git rev-parse --show-toplevel` when it is imported. Nothing is written into the repository: every test compares the
repository's git status and the bytes of the three L4-E9 files and the draft before and after. Tests 1 to 8 hold the predicates on
the draft as it is; tests m1 to m8 show each predicate failing on a mutant of the draft (one changed line each, the regression the
predicate exists to catch). These are software predicates on a text draft and its reader: they establish no property of any board,
circuit or part. Prototype design: nothing built, ordered or measured.
"""
import contextlib
import importlib.util
import io
import os
import re
import subprocess
import sys
import tempfile

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
DRAFT = os.path.join(ROOT, "v2", "docs", "records", "l9t5", "apply_l4e9_changelist_p0.py")
L4 = "v2/docs/records/l4e9"
REG, PY, PAGE = "DOWNSTREAM-REGISTER.md", "l4e9_power_path.py", "L4-POWER-ARCHITECTURE.md"
NAMES = (REG, PY, PAGE)
PRISTINE = "3d2746c9"      # the three files unapplied (the parent of 7070f106)
APPLIED_AT = "7070f106"    # set 30's integration 1: the draft applied, R-240's item named E-1 in the same commit
ADDED = ["R-%d" % n for n in list(range(220, 240)) + list(range(242, 246))]   # the rows the draft adds, typed here apart from it
LISTED = sorted(ADDED + ["R-240"])   # the change list's rows R-220 to R-245: R-240 already in the tree, no R-241
NOTE_HEAD = "**The P0 round (record l9t5"
EDIT_OLD, EDIT_NEW = "Board B's three supervisor LDOs moved", "Board B's three supervisor LDOs (restated by a later round) moved"
NOTE_OLD, NOTE_NEW = "Rows R-220 to R-245 add the drafts", "Rows R-220 to R-245 (restated by a later round) add the drafts"
# The helper L4-E9's generator loads when it is imported. Basis: W34's acdcb22e (Q-41 item 1; in set 32 as fnd/w34pdftext 62300318,
# merged as 834c86ae) made l4e9_power_path.py load TOP/v2/docs/records/_lib/pdftext.py at import (its line 210 at 4c8196a0), TOP
# being `git rev-parse --show-toplevel`, so inside a fixture the fixture's root: without this file every fixture that imports the
# tree's generator stopped at [Errno 2] (W132's check 8 on set 32's 4c8196a0: t_2, t_6, t_m4 and t_m5). Run in a fixture, the
# generator's import and its cons_changes() open no other file of the fixture (the helper imports the standard library only; the
# glob of v2/docs/records/l4e*/apply_*.py in cons_changes() predates acdcb22e and finds none there; W134, 7 October 2026). A
# pristine generator (3d2746c9) does not load the helper, so the copy is inert there.
HELPER = "v2/docs/records/_lib/pdftext.py"
sys.dont_write_bytecode = True
_N = [0]


def _load(path):
    _N[0] += 1
    sp = importlib.util.spec_from_file_location("applier_state_under_test_%d" % _N[0], path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)


def _repo_state():
    """the repository's git status, the three L4-E9 files and the draft: a test that wrote the repository changes one of them"""
    st = _git("status", "--porcelain", "--untracked-files=all")
    if st.returncode != 0:
        raise Skip("not a git checkout (the fixtures need git)")
    return st.stdout, {n: open(os.path.join(ROOT, L4, n), "rb").read() for n in NAMES}, open(DRAFT, "rb").read()


def _at(commit):
    """the three files as committed at `commit`, read from this repository's history"""
    out = {}
    for n in NAMES:
        r = _git("show", "%s:%s/%s" % (commit, L4, n))
        if r.returncode != 0:
            raise Skip("commit %s is not in this repository's history (the fixture's texts are read from it)" % commit)
        out[n] = r.stdout.decode("utf-8")
    return out


def _tree():
    """the three files as this tree carries them (the applied state since 7070f106)"""
    return {n: open(os.path.join(ROOT, L4, n), encoding="utf-8").read() for n in NAMES}


def _write(root, texts):
    for n, t in texts.items():
        with open(os.path.join(root, L4, n), "w", encoding="utf-8") as fh:
            fh.write(t)


def _root(td, texts):
    """a minimal repository root: the three files, this tree's HELPER and `git init` (L4-E9's generator runs git rev-parse and loads
    HELPER at import)"""
    os.makedirs(os.path.join(td, L4))
    _write(td, texts)
    os.makedirs(os.path.join(td, os.path.dirname(HELPER)))
    with open(os.path.join(ROOT, HELPER), "rb") as src, open(os.path.join(td, HELPER), "wb") as dst:
        dst.write(src.read())
    r = subprocess.run(["git", "init", "-q", td], capture_output=True)
    assert r.returncode == 0, "git init: %r" % r.stderr[-200:]
    return td


def _read(root):
    return {n: open(os.path.join(root, L4, n), "rb").read() for n in NAMES}


def _snap(root):
    """every file of the fixture outside .git with its bytes and its modification time (a rewrite of the same bytes moves the time)"""
    out = {}
    for d, subs, fs in os.walk(root):
        subs[:] = [s for s in subs if s != ".git"]
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = (open(p, "rb").read(), os.stat(p).st_mtime_ns)
    return out


def _path(root, n):
    return os.path.join(root, L4, n)


def _patch_all(draft, root):
    """the draft's patch_all(root) in this process: ((files, changes, module), None), or (None, (exit code, stderr)) on a refusal"""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            return _load(draft).patch_all(root), None
    except SystemExit as e:
        return None, (e.code, err.getvalue())


def _cli(draft, root, *flags):
    """the draft as a process: (exit code, stdout, stderr)"""
    r = subprocess.run([sys.executable, "-B", draft, root] + list(flags), capture_output=True)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def _in_range(ch):
    """the change list's rows R-220 to R-245, in sorted order with repeats kept"""
    return sorted(c[2] for c in ch if re.fullmatch(r"R-\d+", c[2]) and 220 <= int(c[2][2:]) <= 245)


def _drop_line(text, head):
    lines = text.split("\n")
    k = [i for i, l in enumerate(lines) if l.startswith(head)]
    assert len(k) == 1, "%d lines start with %r" % (len(k), head)
    return "\n".join(lines[:k[0]] + lines[k[0] + 1:])


def _edit_line(text, head, old, new):
    lines = text.split("\n")
    k = [i for i, l in enumerate(lines) if l.startswith(head)]
    assert len(k) == 1 and lines[k[0]].count(old) == 1, "the line %r does not carry %r once" % (head, old)
    lines[k[0]] = lines[k[0]].replace(old, new)
    return "\n".join(lines)


def _patched_pristine(draft):
    """the three texts the draft writes on the pristine tree (3d2746c9), computed in memory"""
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, _at(PRISTINE))
        got, ref = _patch_all(draft, root)
        assert ref is None, "the draft refused the pristine tree: exit %s, %s" % (ref[0], ref[1][-300:])
        return {n: got[0][_path(root, n)] for n in NAMES}


def _held(pred, draft=None):
    """run a predicate on the draft (or a mutant) and require the repository unchanged"""
    before = _repo_state()
    pred(draft or DRAFT)
    assert _repo_state() == before, "the test changed the repository (its git status, the L4-E9 files or the draft)"


def _fails(pred, old, new):
    """the predicate fails by its own assertion on the draft with `old` replaced by `new` (the anchor must occur once)"""
    src = open(DRAFT, encoding="utf-8").read()
    assert src.count(old) == 1, "the mutation's anchor is not in the draft exactly once: %r" % old[:80]
    before = _repo_state()
    with tempfile.TemporaryDirectory() as td:
        mutant = os.path.join(td, "apply_l4e9_changelist_p0_mutant.py")
        with open(mutant, "w", encoding="utf-8") as fh:
            fh.write(src.replace(old, new))
        try:
            pred(mutant)
        except AssertionError:
            assert _repo_state() == before, "the mutant changed the repository"
            return
    raise AssertionError("the predicate passed on its mutant (%r replaced)" % old[:80])


# ---- the predicates (each takes the draft's path, so that a mutant can be put in its place) ----

def p1_pristine(draft):
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, _at(PRISTINE))
        before = _snap(root)
        assert b"| R-220 |" not in _read(root)[REG], "the pristine register carries R-220"
        got, ref = _patch_all(draft, root)
        assert ref is None, "the draft refused the pristine tree: exit %s, %s" % (ref[0], ref[1][-300:])
        files, ch, m = got
        assert _snap(root) == before, "patch_all wrote the pristine tree"
        assert not getattr(m, "ALREADY_APPLIED", False), "the pristine tree read as applied"
        assert sorted(files) == sorted(_path(root, n) for n in NAMES)
        reg, page = files[_path(root, REG)], files[_path(root, PAGE)]
        assert _in_range(ch) == LISTED, "the patched change list's rows R-220 to R-245: %s" % _in_range(ch)
        assert ch == m.cons_changes(m.md_table(reg, "| ID | Kind |"))
        assert m.md_table(page, "| # | Step | Row |") == [["%d" % c[0]] + [str(x) for x in c[1:]] for c in ch], \
            "the patched page's table is not the patched change list"
        assert sum(l.startswith(NOTE_HEAD) for l in page.split("\n")) == 1, "the patched page does not carry the P0 note once"
        for rid in ("R-210", "R-211", "R-212"):
            assert [c[8] for c in ch if c[2] == rid][0].startswith("WITHDRAWN"), rid
        rc, out, err = _cli(draft, root, "--check")
        assert rc == 0 and "CHECK OK, nothing written" in out and "APPLIED BEFORE" not in out, (rc, out[-300:], err[-300:])
        assert _snap(root) == before, "--check wrote the pristine tree"


def p2_applied(draft):
    texts = _tree()
    assert "| R-220 |" in texts[REG], "this tree's register does not carry R-220 (the applied state this predicate judges)"
    assert [re.match(r"\| (R-\d+) \|", r).group(1) for _a, rows in _load(draft).REG_ADD for r in rows] == ADDED, \
        "the draft's added rows are not R-220 to R-239 and R-242 to R-245"
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, texts)
        before = _snap(root)
        got, ref = _patch_all(draft, root)
        assert ref is None, "the draft refused the applied tree: exit %s, %s" % (ref[0], ref[1][-300:])
        files, ch, m = got
        assert getattr(m, "ALREADY_APPLIED", False) is True, "the applied tree did not read as applied"
        assert files == {_path(root, n): texts[n] for n in NAMES}, "the reader did not return the tree's own texts"
        assert _snap(root) == before, "the reader wrote the applied tree"
        g = _load(_path(root, PY))      # the tree's own generator, loaded apart from the draft's module_of
        assert ch == g.cons_changes(g.md_table(texts[REG], "| ID | Kind |")), "the change list is not cons_changes of the tree's register"
        assert _in_range(ch) == LISTED, "the applied change list's rows R-220 to R-245: %s" % _in_range(ch)
        rc, out, err = _cli(draft, root, "--check")
        assert rc == 0 and "APPLIED BEFORE" in out and "CHECK OK" not in out, (rc, out[-300:], err[-300:])
        assert _snap(root) == before, "--check wrote the applied tree"


def p3_edited(draft):
    applied = _patched_pristine(draft)
    edited = dict(applied)
    edited[REG] = _edit_line(applied[REG], "| R-233 |", EDIT_OLD, EDIT_NEW)
    edited[PAGE] = _edit_line(applied[PAGE], NOTE_HEAD, NOTE_OLD, NOTE_NEW)
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, edited)
        before = _snap(root)
        got, ref = _patch_all(draft, root)
        assert ref is None, "the draft refused an applied tree whose row and note a later round restated: exit %s, %s" % (
            ref[0], ref[1][-300:])
        files, ch, m = got
        assert getattr(m, "ALREADY_APPLIED", False) is True
        assert files[_path(root, REG)] == edited[REG] and files[_path(root, PAGE)] == edited[PAGE], "the reader did not return the tree's texts"
        row = [c for c in ch if c[2] == "R-233"]
        assert len(row) == 1 and EDIT_NEW in row[0][7], "the change list is not read from the edited register"
        rc, out, err = _cli(draft, root, "--check")
        assert rc == 0 and "APPLIED BEFORE" in out, (rc, out[-300:], err[-300:])
        assert _snap(root) == before


def p4_half_applied(draft):
    texts = _tree()
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, texts)
        for rid in ADDED[1:]:        # every added row but R-220, the reader's marker (its loss is judged below)
            _write(root, {REG: _drop_line(texts[REG], "| %s |" % rid)})
            before = _snap(root)
            got, ref = _patch_all(draft, root)
            assert got is None, "%s removed: the half-applied tree read as applied" % rid
            assert ref[0] == 3 and rid in ref[1], "%s removed: exit %s, %s" % (rid, ref[0], ref[1][-300:])
            assert _snap(root) == before
        _write(root, {REG: _drop_line(texts[REG], "| R-233 |")})
        before = _snap(root)
        for flag in ("--check", "--write"):
            rc, out, err = _cli(draft, root, flag)
            assert rc == 3 and "R-233" in err and "WRITTEN" not in out, (flag, rc, out[-300:], err[-300:])
            assert _snap(root) == before
        _write(root, {REG: _drop_line(texts[REG], "| R-220 |")})
        before = _snap(root)
        for flag in ("--check", "--write"):
            rc, out, err = _cli(draft, root, flag)
            assert rc == 3 and "refusing" in err and "WRITTEN" not in out, ("R-220 removed", flag, rc, out[-300:], err[-300:])
            assert _snap(root) == before


def p5_no_note(draft):
    texts = _tree()
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, dict(texts, **{PAGE: _drop_line(texts[PAGE], NOTE_HEAD)}))
        before = _snap(root)
        got, ref = _patch_all(draft, root)
        assert got is None, "the applied tree without the page's P0 note read as applied"
        assert ref[0] == 3 and "P0 note" in ref[1], (ref[0], ref[1][-300:])
        for flag in ("--check", "--write"):
            rc, out, err = _cli(draft, root, flag)
            assert rc == 3 and "P0 note" in err and "WRITTEN" not in out, (flag, rc, out[-300:], err[-300:])
        assert _snap(root) == before


def p6_write_applied(draft):
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, _tree())
        before = _snap(root)
        rc, out, err = _cli(draft, root, "--write")
        assert rc == 3 and "applied before" in err and "WRITTEN" not in out, (rc, out[-300:], err[-300:])
        assert _snap(root) == before, "--write on the applied tree wrote a file"


def p7_write_pristine(draft):
    with tempfile.TemporaryDirectory() as td:
        root = _root(td, _at(PRISTINE))
        got, ref = _patch_all(draft, root)
        assert ref is None, "the draft refused the pristine tree: exit %s, %s" % (ref[0], ref[1][-300:])
        want = {n: got[0][_path(root, n)].encode("utf-8") for n in NAMES}
        rc, out, err = _cli(draft, root, "--write")
        assert rc == 0 and "WRITTEN, three files" in out, (rc, out[-300:], err[-300:])
        assert _read(root) == want, "the written files are not the patched texts"
        rc, out, err = _cli(draft, root, "--check")
        assert rc == 0 and "APPLIED BEFORE" in out, ("--check after --write", rc, out[-300:], err[-300:])
        before = _snap(root)
        rc, out, err = _cli(draft, root, "--write")
        assert rc == 3 and "applied before" in err, ("a second --write", rc, out[-300:], err[-300:])
        assert _snap(root) == before, "a second --write wrote a file"


def p8_binds_the_integration(draft):
    patched, applied = _patched_pristine(draft), _at(APPLIED_AT)
    assert patched[PY] == applied[PY], "the patched script is not the one 7070f106 committed"
    diffs = {}
    for n in (REG, PAGE):
        a, b = patched[n].split("\n"), applied[n].split("\n")
        assert len(a) == len(b), "%s: %d lines patched, %d committed at %s" % (n, len(a), len(b), APPLIED_AT)
        diffs[n] = [(x, y) for x, y in zip(a, b) if x != y]
    assert len(diffs[REG]) == 1 and all(s.startswith("| R-240 |") for s in diffs[REG][0]), \
        "the register differs from 7070f106's outside R-240: %r" % [x[:60] for x, _y in diffs[REG]]
    rx, ry = diffs[REG][0]
    assert "engineering item S1;" in rx and "engineering item E-1 (" in ry, "R-240's difference is not the E-1 naming 7070f106 classifies"
    assert len(diffs[PAGE]) == 1 and all(re.match(r"\| \d+ \| \w+ \| R-240 \|", s) for s in diffs[PAGE][0]), \
        "the page differs from 7070f106's outside R-240's change-list row: %r" % [x[:60] for x, _y in diffs[PAGE]]


# ---- the tests: the predicates on the draft as it is ----

def t_1_pristine_tree_patched_in_memory_and_checks_ok():
    """(1) The pristine tree (the three files at 3d2746c9, before integration 7070f106 applied the draft): patch_all() patches in
    memory and writes nothing, the change list carries every row R-220 to R-245 once with no R-241, is L4-E9's own cons_changes of
    the patched register and is the patched page's table, FAN_OK's R-210 to R-212 read WITHDRAWN; `--check` exits 0 with
    "CHECK OK". Evidence basis: commits 3d2746c9 and 7070f106 (the draft's rows as applied)."""
    _held(p1_pristine)


def t_2_applied_tree_read_from_the_tree():
    """(2) The applied tree (this tree's three files, applied by 7070f106 and restated by set 31): applied_state() returns the
    tree's own texts and sets ALREADY_APPLIED, the change list equals cons_changes of the tree's register computed by the tree's own
    generator loaded apart, every row R-220 to R-245 once and no R-241; `--check` exits 0 with "APPLIED BEFORE" and writes nothing.
    Evidence basis: commit bbba3e53 (the reader) and 53a68c7c (its presence test), the callers l9t5_connected.py and test_l9t5."""
    _held(p2_applied)


def t_3_applied_tree_with_a_restated_row_still_applied():
    """(3) Set 31's case: the applied texts (as the draft writes them on 3d2746c9) with R-233's item and the P0 note's body restated
    by a later round still read APPLIED (presence by id and by the note's opening, not the verbatim text), the change list carries
    the restated item, `--check` exits 0 with "APPLIED BEFORE". Evidence basis: commit 53a68c7c (integration 2c: the presence test,
    because set 31 edited the applied texts)."""
    _held(p3_edited)


def t_4_half_applied_tree_refused_naming_the_missing_row():
    """(4) A half-applied tree (this tree with one added row removed, each of R-221 to R-239 and R-242 to R-245 in turn): refused
    with exit 3 naming the missing id, nothing written (in process for every row; through the command line for R-233 with --check
    and --write). With R-220 removed, the reader's marker, the tree is refused with exit 3 and nothing written by the pristine path's
    own guard. Evidence basis: commits bbba3e53 and 53a68c7c (a half-applied tree is neither state)."""
    _held(p4_half_applied)


def t_5_applied_tree_without_the_page_note_refused():
    """(5) The applied tree without the page's P0 note: refused with exit 3 naming the note, in process and through the command
    line with --check and --write, nothing written. Evidence basis: commits bbba3e53 and 53a68c7c (the note is half the applied
    state's test)."""
    _held(p5_no_note)


def t_6_write_on_the_applied_tree_refused_nothing_written():
    """(6) `--write` on the applied tree refuses with exit 3 ("applied before"), and every file of the fixture keeps its bytes and
    its modification time. Evidence basis: commit bbba3e53 (--write still refuses twice) and 7070f106 (the tree it protects)."""
    _held(p6_write_applied)


def t_7_write_on_the_pristine_tree_writes_and_reads_back_applied():
    """(7) `--write` on the pristine fixture (3d2746c9) exits 0, writes the three files as patch_all() computes them, and the result
    reads APPLIED with `--check`; a second `--write` refuses with exit 3 and writes nothing. Evidence basis: commits 7070f106 (the
    application) and bbba3e53 (the reader that the written tree must satisfy)."""
    _held(p7_write_pristine)


def t_8_draft_reproduces_the_integration_commit_apart_from_its_classified_edit():
    """(8) The binding the owner's part 25 asks for between the draft and the integrated revision: the draft applied to 3d2746c9
    reproduces 7070f106's script byte for byte and its register and page line for line apart from R-240's register row and R-240's
    change-list row, whose one difference is the E-1 naming that 7070f106's subject classifies ("the applied R-240 row's item named
    E-1 as record l4e7 names it"). Evidence basis: commits 3d2746c9 and 7070f106, the owner's part 25."""
    _held(p8_binds_the_integration)


# ---- the mutations: each predicate fails on the regression it exists to catch ----

def t_m1_pristine_predicate_fails_when_the_reader_takes_every_tree_as_applied():
    """Mutant: applied_state() without its pristine test (no added row present), so the pristine tree enters the reader (and is
    refused as partially applied). Predicate (1) fails. Evidence basis: bbba3e53 (the reader returns None on the pristine tree);
    integration 2b's fix_applier_partial.py (W2's D1: the reader decides on ALL added ids; the anchor is its "not present" line)."""
    _fails(p1_pristine, '    if not present:\n        return None\n', '    if False:\n        return None\n')


def t_m2_applied_predicate_fails_without_the_reader():
    """Mutant: patch_all() without applied_state(), the draft as 7070f106 committed it, which refused the integrated tree
    ("already carries R-220"). Predicate (2) fails. Evidence basis: bbba3e53."""
    _fails(p2_applied, "    done = applied_state(root)\n", "    done = None\n")


def t_m3_restated_row_predicate_fails_on_the_verbatim_row_test():
    """Mutant: the reader's row test as bbba3e53 wrote it (every added row verbatim). Predicate (3) fails on the restated R-233.
    Evidence basis: 53a68c7c (integration 2c replaced that test by presence because set 31 edited the applied texts); integration 2b's
    fix_applier_partial.py (D1: the presence list is `present`, counted against every added id)."""
    _fails(p3_edited, '    present = [i for i in ids if "| %s |" % i in reg]\n',
           "    present = [i for i, r in zip(ids, [r for _a, rows in REG_ADD for r in rows]) if r in reg]\n")


def t_m3b_restated_row_predicate_fails_on_a_verbatim_note_test():
    """Mutant: the reader's note test made verbatim (the whole NOTE in the page). Predicate (3) fails on the restated note's body.
    Evidence basis: 53a68c7c (the note's presence, not its verbatim text)."""
    _fails(p3_edited, 'not any(l.startswith("**The P0 round (record l9t5") for l in page.split("\\n"))', "NOTE not in page")


def t_m4_half_applied_predicate_fails_without_the_presence_test():
    """Mutant: the reader without its presence test (no row counted missing). Predicate (4) fails: the half-applied tree is no
    longer refused by the reader with exit 3 naming the row (L4-E9's own cons_changes refuses it with exit 4 instead, naming no
    row). Evidence basis: 53a68c7c; integration 2b's fix_applier_partial.py (D1: every added id counted present = applied)."""
    _fails(p4_half_applied, '    present = [i for i in ids if "| %s |" % i in reg]\n', "    present = list(ids)\n")


def t_m5_no_note_predicate_fails_without_the_note_test():
    """Mutant: the reader without its test of the page's P0 note. Predicate (5) fails: the page without the note reads APPLIED.
    Evidence basis: bbba3e53 and 53a68c7c; integration 2b's fix_applier_partial.py (D1 moved the missing-row refusal ahead of the
    note test, so the note test stands alone)."""
    _fails(p5_no_note, '    if not any(l.startswith("**The P0 round (record l9t5") for l in page.split("\\n")):\n',
           "    if False:\n")


def t_m6_write_applied_predicate_fails_when_write_does_not_refuse():
    """Mutant: main() without the refusal of --write on the applied tree. Predicate (6) fails (exit 0). Evidence basis: bbba3e53
    (--write still refuses twice)."""
    _fails(p6_write_applied, '        if flags == ["--write"]:\n            refuse("the register already carries R-220: applied before")\n',
           '        if False:\n            refuse("the register already carries R-220: applied before")\n')


def t_m7_write_pristine_predicate_fails_when_the_writer_drops_the_note():
    """Mutant: patch_page() without the P0 note, so the writer and the reader disagree on the applied state. Predicate (7) fails:
    the written tree is refused by --check. Evidence basis: 7070f106 (the page's note written) and bbba3e53 (the reader's test)."""
    _fails(p7_write_pristine, 'lines[:i] + [NOTE, ""] + table + lines[j:]', "lines[:i] + table + lines[j:]")


def t_m8_binding_predicate_fails_on_a_changed_row_text():
    """Mutant: one added row's text changed in the draft (R-221's item). Predicate (8) fails: the register differs from 7070f106's
    outside R-240. Evidence basis: 7070f106 and the owner's part 25 (an intervening change is classified, never silent)."""
    _fails(p8_binds_the_integration, "over-voltage cut-off on VIN_RAW (R-48", "overvoltage cut-off on VIN_RAW (R-48")


# ---- the D1 correction of integration 2b (d83d9f2d): the reader decides on EVERY added id ----
# W16's independent review of 2b (REVIEW-2B finding 3): no predicate above discriminates D1 itself. Predicate (4) removes R-220 from
# the APPLIED tree, which the parent's reader refused as well; the case the fix exists for, a register carrying some of the added rows
# beside a page and script that may be pristine, was exercised nowhere. On it the parent's reader (6bc4424e: `"| R-220 |" not in reg`
# alone) took the pristine path, and its register guard (R-220 alone too) inserted every added row again.

PARENT_2B = "6bc4424e"     # the parent of 2b: the reader and the register guard both decided on R-220 alone
DRAFT_PATH = "v2/docs/records/l9t5/apply_l4e9_changelist_p0.py"
ROWS_AFTER = (("R-219", [r for r in ADDED if int(r[2:]) < 240]), ("R-240", [r for r in ADDED if int(r[2:]) > 240]))
#                            where 7070f106 put the added rows, typed here apart from the draft's REG_ADD
D1_OLD = ('    if not present:\n        return None\n    if len(present) != len(ids):\n'
          '        refuse("the register is PARTIALLY applied: it carries %d of the %d rows this draft adds; missing %r" % (\n'
          '            len(present), len(ids), [i for i in ids if i not in present][:6]))\n')
D1_PARENT = '    if "| R-220 |" not in reg:\n        return None\n'


def _row_ids(text):
    return re.findall(r"^\| (R-\d+) \|", text, re.M)


def _dups(text):
    """the row ids that open more than one line of a register text"""
    ids = _row_ids(text)
    return sorted({i for i in ids if ids.count(i) > 1})


def _with_rows(base, rows_from, keep):
    """`base` (a register without the added rows) with the added rows `keep` copied from `rows_from`, each in 7070f106's place"""
    src = {re.match(r"\| (R-\d+) \|", l).group(1): l for l in rows_from.split("\n") if re.match(r"\| R-\d+ \|", l)}
    lines = base.split("\n")
    for anchor, ids in ROWS_AFTER:
        k = [i for i, l in enumerate(lines) if l.startswith("| %s |" % anchor)]
        assert len(k) == 1, "%d rows %s in the base register" % (len(k), anchor)
        lines[k[0] + 1:k[0] + 1] = [src[r] for r in ids if r in keep]
    out = "\n".join(lines)
    back = out
    for r in keep:
        back = _drop_line(back, "| %s |" % r)
    assert back == base, "the fixture register is not the base with the kept rows inserted"
    return out


def _d1_registers():
    """the partially applied registers: (label, text, the added ids it lacks); the first is the parent's duplicating case"""
    pristine, applied, tree = _at(PRISTINE)[REG], _at(APPLIED_AT)[REG], _tree()[REG]
    assert not set(_row_ids(pristine)) & set(ADDED), "the pristine register carries an added row"
    out = []
    for label, keep in (("every added row but R-220", ADDED[1:]), ("R-220 alone of the added rows", ADDED[:1])):
        missing = [r for r in ADDED if r not in keep]
        out.append(("the pristine register (%s, FAN_OK rows unedited) with %s" % (PRISTINE, label), _with_rows(pristine, applied, keep),
                    missing))
        t = tree
        for r in missing:
            t = _drop_line(t, "| %s |" % r)
        out.append(("this tree's register with %s" % label, t, missing))
    for label, reg, missing in out:
        assert [r for r in ADDED if r in _row_ids(reg)] == [r for r in ADDED if r not in missing] and not _dups(reg), label
    return out


def pd1_partial(draft):
    pages = (("the pristine page and script (%s)" % PRISTINE, _at(PRISTINE)), ("this tree's page and script", _tree()))
    for rlabel, reg, missing in _d1_registers():
        named = ["'%s'" % r for r in missing[:6]]    # the refusal names the first six missing ids
        for plabel, texts in pages:
            case = "%s, %s" % (rlabel, plabel)
            with tempfile.TemporaryDirectory() as td:
                root = _root(td, {REG: reg, PY: texts[PY], PAGE: texts[PAGE]})
                before = _snap(root)
                got, ref = _patch_all(draft, root)
                if got is not None:
                    d = _dups(got[0][_path(root, REG)])
                    assert not d, "%s: the reader let it through and the register it would write duplicates %s" % (case, d[:6])
                assert got is None, "%s: read as %s" % (case, "applied" if getattr(got[2], "ALREADY_APPLIED", False) else "pristine")
                assert ref[0] == 3 and "PARTIALLY" in ref[1] and all(n in ref[1] for n in named), \
                    "%s: exit %s, %s" % (case, ref[0], ref[1][-300:])
                assert _snap(root) == before, "%s: patch_all wrote the fixture" % case
                for flag in ("--check", "--write"):
                    rc, out, err = _cli(draft, root, flag)
                    on_disk = _dups(open(_path(root, REG), encoding="utf-8").read())
                    assert not on_disk, "%s, %s: the register on disk duplicates %s" % (case, flag, on_disk[:6])
                    assert rc == 3 and "PARTIALLY" in err and all(n in err for n in named), (case, flag, rc, out[-300:], err[-300:])
                    assert "WRITTEN" not in out and "APPLIED BEFORE" not in out and "CHECK OK" not in out, (case, flag, out[-300:])
                    assert _snap(root) == before, "%s, %s: a file of the fixture changed" % (case, flag)


def _fails_at(pred, commit, must):
    """the predicate fails by its own assertion, with `must` in the assertion's text, on the draft as committed at `commit`"""
    r = _git("show", "%s:%s" % (commit, DRAFT_PATH))
    if r.returncode != 0:
        raise Skip("commit %s is not in this repository's history (the draft is read from it)" % commit)
    before = _repo_state()
    with tempfile.TemporaryDirectory() as td:
        old = os.path.join(td, "apply_l4e9_changelist_p0_at_%s.py" % commit)
        with open(old, "wb") as fh:
            fh.write(r.stdout)
        try:
            pred(old)
        except AssertionError as e:
            assert _repo_state() == before, "the draft at %s changed the repository" % commit
            assert must in str(e), "the predicate failed on the draft at %s, but not by %r: %s" % (commit, must, str(e)[:300])
            return
    raise AssertionError("the predicate passed on the draft as committed at %s" % commit)


def t_d1_partially_applied_register_refused_naming_the_missing_ids():
    """(D1) A PARTIALLY applied register, in four variants: the pristine register (3d2746c9, its FAN_OK rows unedited) and this
    tree's register, each carrying every added row but R-220, and each carrying R-220 alone of the added rows; each beside the
    pristine page and script (3d2746c9) and beside this tree's. On all eight: patch_all() refuses with exit 3 as PARTIALLY applied,
    naming the missing ids (the first six), and writes nothing; `--check` and `--write` exit 3 the same way and write nothing; no
    path leaves a register with a duplicated row (in memory or on disk). Evidence basis: commit d83d9f2d (integration 2b, W2's D1:
    the reader decides on the presence of every added id) and REVIEW-2B finding 3 (W16, 6 October 2026)."""
    _held(pd1_partial)


def t_d1_m_partial_predicate_fails_on_the_parents_r220_test():
    """Mutant: the reader with the parent's test restored (`if "| R-220 |" not in reg: return None` in place of the presence test,
    the count of present ids against every added id removed); the register guard of 2b kept. Predicate (D1) fails on its first
    variant: the pristine register lacking R-220 enters the pristine path and is refused there by 2b's register guard as "applied
    before", not by the reader as partially applied naming R-220. Evidence basis: 6bc4424e (the parent's reader) and REVIEW-2B
    finding 3. Anchor: applied_state()'s five lines from `if not present:` to the PARTIALLY refusal (D1_OLD, once in the draft)."""
    _fails(pd1_partial, D1_OLD, D1_PARENT)


def t_d1_parent_draft_fails_the_partial_predicate_by_duplicating_rows():
    """The parent's draft itself (6bc4424e, read from this repository's history: the reader and the register guard both decide on
    R-220 alone): predicate (D1) fails on its first variant by duplicating rows, the pristine register carrying every added row but
    R-220 beside the pristine page and script taking the pristine path and receiving every added row a second time. Evidence basis:
    6bc4424e and REVIEW-2B finding 3 ("on the parent's reader it duplicates rows")."""
    _fails_at(pd1_partial, PARENT_2B, "duplicates")
