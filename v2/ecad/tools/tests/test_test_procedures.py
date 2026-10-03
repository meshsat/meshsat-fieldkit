"""The test procedures of v2/docs/test-procedures/ (MESHSAT-1357, 3 October 2026; the supplier handover's phase 2).

Each TP-<id>.md turns a specification the records already hold (L4-E9's section 5d route table, L4-E11's section 17d blocks
and section 8 rows, the downstream register's acceptances) into an executable procedure for a supplier's engineers. The
properties held here, on the tree and on broken copies:

- every procedure names its register row and the row exists in v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md;
- every pass condition is quoted from its source: each named register row's Acceptance, each named L4-E11 row's Acceptance and
  each named 5d row's Specimen, What transfers, Authorisation and What to buy cells are carried as quotes equal to the cell,
  and every other quote is found verbatim in its source;
- every procedure carries the mark "PROPOSED, for the supplier to review and agree before execution";
- no file of the folder carries an em or en dash;
- every TBD names the register or L4-E11 row that owes it, and every 5d route row is covered exactly once;
- the committed tp_check.out is what tp_check.py prints, and the checker refuses each kind of broken procedure.

Nothing here writes into the tree: the broken copies live in a temporary directory outside it.
"""
import glob
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
FOLDER = os.path.join(ROOT, "v2", "docs", "test-procedures")
SCRIPT = os.path.join(FOLDER, "tp_check.py")
OUT = os.path.join(FOLDER, "tp_check.out")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

_CACHE = {}


def _T():
    if "T" not in _CACHE:
        need(SCRIPT, "the test procedures' checker")
        sp = importlib.util.spec_from_file_location("tp_check_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _CACHE["T"] = m
    return _CACHE["T"]


def _procedures():
    files = sorted(glob.glob(os.path.join(FOLDER, "TP-*.md")))
    assert len(files) >= 10, "expected at least the ten procedures, found %d" % len(files)
    return [(os.path.basename(f), open(f, encoding="utf-8").read()) for f in files]


def t_the_checker_passes_on_the_tree():
    out, fails = _T().check()
    assert not fails, "tp_check fails on the tree: %s" % "; ".join(fails[:6])
    assert out[-1].startswith("RESULT: ALL PASS"), out[-1]


def t_every_procedure_names_its_register_row_and_the_row_exists():
    T = _T()
    src = T.Sources(ROOT)
    rows = set(src.first_cells(T.REG, "Acceptance"))
    assert "R-159" in rows and "R-185" in rows, "the register's table was not read"
    for name, text in _procedures():
        m = T.meta(text)
        assert m, "%s has no metadata block" % name
        regs = T.listed(m.get("register", ""))
        assert regs, "%s names no register row" % name
        for r in regs:
            assert re.match(r"R-\d+$", r), "%s names %r, not a register row id" % (name, r)
            assert r in rows, "%s names %s, which the register does not have" % (name, r)


def t_every_pass_condition_is_quoted_from_its_source():
    T = _T()
    src = T.Sources(ROOT)
    for name, text in _procedures():
        m = T.meta(text)
        tq, n_table, n_text, fails = T.verify_quotes(src, name, text)
        assert not fails, "%s: %s" % (name, "; ".join(fails[:4]))
        for r in T.listed(m["register"]):
            assert (T.REG, r, "Acceptance") in tq, "%s does not quote register row %s's Acceptance" % (name, r)
        for r in T.listed(m["e11"]):
            assert (T.E11, r, "Acceptance") in tq, "%s does not quote L4-E11 row %s's Acceptance" % (name, r)
        for r in T.listed(m["route5d"], ";;"):
            for c in T.COLS_5D:
                assert (T.ARCH, r, c) in tq, "%s does not quote 5d row %r's %s" % (name, r, c)
        assert n_table >= 6, "%s carries only %d table quotes" % (name, n_table)
    readme = open(os.path.join(FOLDER, "README.md"), encoding="utf-8").read()
    _, _, _, fails = T.verify_quotes(src, "README.md", readme)
    assert not fails, "README: %s" % "; ".join(fails[:4])


def t_every_procedure_carries_the_proposed_mark():
    T = _T()
    for name, text in _procedures() + [("README.md", open(os.path.join(FOLDER, "README.md"), encoding="utf-8").read())]:
        assert T.MARK in T.norm(text), "%s lacks the mark %r" % (name, T.MARK)


def t_no_long_dash_in_the_folder_or_this_test():
    long_dashes = (chr(0x2014), chr(0x2013))
    files = [f for f in glob.glob(os.path.join(FOLDER, "*")) if os.path.isfile(f)] + [os.path.abspath(__file__)]
    for f in files:
        t = open(f, encoding="utf-8").read()
        for d in long_dashes:
            assert d not in t, "%s carries U+%04X" % (os.path.relpath(f, ROOT), ord(d))


def t_every_tbd_names_an_owing_row_and_every_5d_row_is_covered_once():
    T = _T()
    out, fails = T.check()
    assert not [f for f in fails if ": C6 " in f or f.startswith("C9")], fails
    cov = out[out.index("3. Coverage of section 5d's route table") + 1:out.index("4. The TBDs by owing row") - 1]
    assert cov and all(not ln.endswith("NOT COVERED") for ln in cov), cov
    assert len(cov) == len(T.Sources(ROOT).route_rows()), "the coverage lists %d rows" % len(cov)


def t_the_committed_out_is_what_the_script_prints():
    need(OUT, "the checker's committed output")
    r = subprocess.run([sys.executable, "-B", os.path.relpath(SCRIPT, ROOT)], cwd=ROOT, capture_output=True)
    assert r.returncode == 0, "tp_check.py exited %d" % r.returncode
    assert r.stdout == open(OUT, "rb").read(), ("tp_check.out is not what tp_check.py prints: re-read the procedures, then "
                                               "regenerate it with _bin/regen_out.py")
    assert ROOT.encode() not in r.stdout, "the output names an absolute path"


def _broken(mutate):
    """A copy of the folder with one procedure (TP-E11-29.md) or the README mutated; the checker's failures on it."""
    T = _T()
    tmp = tempfile.mkdtemp(prefix="tp-fixture-")
    try:
        for f in glob.glob(os.path.join(FOLDER, "*.md")):
            shutil.copy(f, tmp)
        mutate(tmp)
        _, fails = T.check(root=ROOT, folder=tmp)
        return fails
    finally:
        shutil.rmtree(tmp)


def _edit(name, old, new, count=1):
    def m(tmp):
        p = os.path.join(tmp, name)
        t = open(p, encoding="utf-8").read()
        assert old in t, "the fixture's anchor %r is not in %s" % (old[:40], name)
        open(p, "w", encoding="utf-8").write(t.replace(old, new, count))
    return m


def t_the_checker_refuses_broken_procedures():
    T = _T()
    cases = [
        ("C3", _edit("TP-E11-29.md", "33.12 K/W steady and at 60 s", "34.12 K/W steady and at 60 s")),
        ("C7", _edit("TP-E11-29.md", T.MARK, "for the supplier to review")),
        ("C2", _edit("TP-E11-29.md", "register: R-159", "register: R-159, R-9999")),
        ("C8", _edit("TP-E11-29.md", "## 3. Safety", "## 3. Safety " + chr(0x2014))),
        ("C6", _edit("TP-E11-29.md", "## 3. Safety", "## 3. Safety\n\nTBD: a figure with no owner.")),
        ("C6", _edit("TP-E11-29.md", "TBD (owed by R-159)", "TBD (owed by R-9999)")),
        ("C5", _edit("TP-E11-29.md", "## 3. Safety", "## 3. Safety\n\nSee `v2/docs/no-such-file.md`.")),
        ("C4", _edit("TP-E11-29.md", 'row="R-159" col="Acceptance"', 'row="R-159" col="State"')),
        ("C9", lambda tmp: os.remove(os.path.join(tmp, "README.md"))),
        ("C9", _edit("README.md", "not-covered: The fit mock-up (R-167) |", "dropped: The fit mock-up (R-167) |")),
    ]
    for code, mutate in cases:
        fails = _broken(mutate)
        assert any((": %s " % code) in f or f.startswith(code) for f in fails), (
            "the checker did not report %s on its broken copy: %s" % (code, "; ".join(fails[:4]) or "no failure"))


# The bring-up page (3 October 2026): the supplier's first-prototype procedure written by hand above the renderer's marker in
# v2/docs/PCB-BRING-UP.md, the generated rail inventory below it, and the inputs copied from branches outside this history.
BRING = os.path.join(ROOT, "v2", "docs", "PCB-BRING-UP.md")


def _RR():
    if "RR" not in _CACHE:
        import rules_render as RR  # noqa: E402 (TOOLS is on sys.path)
        _CACHE["RR"] = RR
    return _CACHE["RR"]


def t_the_bring_up_page_carries_its_procedure_above_the_generated_block():
    T = _T()
    out, fails, tbds = T.check_bringup(T.Sources(ROOT))
    assert not fails, "the bring-up page fails: %s" % "; ".join(fails[:6])
    assert any(o.startswith("R-") for owners, _ in tbds for o in owners), "no TBD names a register row"


def t_the_inputs_are_the_bytes_their_sources_name():
    T = _T()
    lines, fails = T.check_inputs(T.Sources(ROOT))
    assert not fails, "; ".join(fails)
    assert len(lines) >= 5 and all(ln.endswith("verified") for ln in lines), lines


def t_the_renderer_keeps_the_procedure_above_its_marker_and_renders_as_before_without_it():
    RR, T = _RR(), _T()
    assert RR.BRINGUP_MARK.startswith(T.BRINGUP_MARK_PREFIX), "the checker's marker is not the renderer's"
    tmp = tempfile.mkdtemp(prefix="tp-render-")
    try:
        p = os.path.join(tmp, "page.md")
        open(p, "w", encoding="utf-8").write("PROCEDURE\n" + RR.BRINGUP_MARK + "\n\nOLD GENERATED\na hand edit below\n")
        assert RR._with_bringup_preface("NEW\n", page=p) == "PROCEDURE\n" + RR.BRINGUP_MARK + "\n\nNEW\n"
        open(p, "w", encoding="utf-8").write("a page with no marker\n")
        assert RR._with_bringup_preface("NEW\n", page=p) == "NEW\n", "a page without the marker must render as before"
        assert RR._with_bringup_preface("NEW\n", page=os.path.join(tmp, "absent.md")) == "NEW\n"
    finally:
        shutil.rmtree(tmp)


def t_the_committed_page_is_what_the_renderer_writes_for_its_generated_block():
    RR = _RR()
    page = open(BRING, encoding="utf-8").read()
    assert page.count(RR.BRINGUP_MARK) == 1, "the marker is missing or repeated"
    gen = page.split(RR.BRINGUP_MARK, 1)[1].lstrip("\n")
    assert gen.startswith(RR.HEAD) and "## Board A" in gen, "the block under the marker is not the generated inventory"
    assert RR._with_bringup_preface(gen) == page, "a render of the same generated block would change the page"


def t_the_bring_up_checker_refuses_broken_pages():
    T = _T()
    page = open(BRING, encoding="utf-8").read()
    cases = [
        ("B1", lambda s: s.replace(T.BRINGUP_MARK_PREFIX, "<!-- no marker here")),
        ("B2", lambda s: s.replace(T.MARK, "for the supplier")),
        ("B2", lambda s: s.replace("WITH the drafts applied", "with the drafts")),
        ("B3", lambda s: s.replace("on held evidence the start ends in VSYS_MIN", "on held evidence the start ends at VSYS_MIN")),
        ("B4", lambda s: s.replace("## Board A\n", "## Board A\n\nSee `v2/docs/no-such-page.md`.\n", 1)),
        ("B5", lambda s: s.replace("TBD (owed by R-13)", "TBD (owed by R-9999)")),
        ("B5", lambda s: s.replace("## Board A\n", "## Board A\n\nA figure is TBD here.\n", 1)),
        ("B6", lambda s: s.replace("### E54. Before the next board", "### E54. Before")),
        ("B7", lambda s: s.replace("| R-01 |", "| R-9999 |", 1)),
    ]
    for code, mutate in cases:
        bad = mutate(page)
        assert bad != page, "the fixture for %s changed nothing" % code
        src = T.Sources(ROOT)
        src.text[T.BRINGUP] = bad
        _, fails, _ = T.check_bringup(src)
        assert any(f.startswith(code) for f in fails), "the checker did not report %s: %s" % (code, "; ".join(fails[:3]))


def t_the_inputs_checker_refuses_a_changed_copy():
    T = _T()
    src = T.Sources(ROOT)
    t = src.read(T.INPUTS)
    src.text[T.INPUTS] = t.replace("1e92b0d8f66c2b6c", "0e92b0d8f66c2b6c")
    _, fails = T.check_inputs(src)
    assert any(f.startswith("C10") for f in fails), fails
