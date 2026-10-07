"""Record l4k (MESHSAT-1357, worker W131, branch fnd/l4k from main be07863b, 7 October 2026): the DESK-gate assessment's K table
(K-01 to K-28) re-read on main be07863b, held as predicates on record text and on the files it cites:

- every evidence line of v2/docs/records/l4k/K-TABLE-be07863b.md, of its README and of its apply scripts' docstrings, written as
  `be07863b:<path>:<line>` followed by quoted words, reads those words on those lines at be07863b (git show; whitespace, `*` and
  backtick marks aside); a changed word is refused;
- the table has K-01 to K-28 once each, each with one of STANDING, RESOLVED, SUPERSEDED, and its stated counts agree with its rows;
  the STANDING rows are the seven this record names, each with its resolution or its owner task; a changed state is refused;
- the assessment's section 11 restates the same 28 states with the same counts, and section 5's table reads byte for byte as on
  be07863b (the history is not rewritten); the assessment's other lines keep their numbers;
- each apply script is PENDING or APPLIED on this tree, never partial; on a scratch copy of its target files it writes, a second
  run exits 3, and a duplicated old text or a half-applied state is refused (exit 2) with nothing written;
- the digests and counts the table names: record efuse's page identical at cx45's and cx46's revisions and on be07863b; the
  stability digest of l9t5_f01.out and the connected output's pin at the candidate and on be07863b; L4-E9's four cascade pins equal
  their files on be07863b; 235 register rows;
- record efuse's page keeps its line count and its round 2 sentence, with the dated note beside it; no em or en dash.

These are software predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
Without git or without be07863b in the object store the rules that read it skip with their reason."""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

MAIN = "be07863bbca206a81ab42b9f96a7684c5c10a746"
CAND = "6bc4424ec64592e1a501af5db2246f3391c525a0"
REC = os.path.join(ROOT, "v2", "docs", "records", "l4k")
KT = os.path.join(REC, "K-TABLE-be07863b.md")
ASSESS = "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.md"
EFS = "v2/docs/records/efuse/EFUSE-SETTINGS.md"
SCRIPTS = ("lh12", "p0sol", "p0list", "remeng", "changelist")
STATES = ("STANDING", "RESOLVED", "SUPERSEDED")
STANDING = {"K-03", "K-13", "K-16", "K-17", "K-22", "K-23", "K-24"}
EV = re.compile(r'`?be07863b:(v2/[^\s:`]+):(\d+)(?:-(\d+))?`?\s*"([^"]*)"')
HEAD = re.compile(r"^### (K-\d\d): (STANDING|RESOLVED|SUPERSEDED)\b", re.M)
DASHES = (chr(0x2013), chr(0x2014))
_C = {}


def _norm(t):
    return " ".join(t.replace("*", "").replace("`", "").split())


def _rc(*a):
    try:
        return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True).returncode
    except OSError:
        return -1


def _need_main():
    if _rc("cat-file", "-e", MAIN + "^{commit}") != 0:
        raise Skip("main %s is not in this clone's object store" % MAIN[:8])


def _show(rev, path):
    k = (rev, path)
    if k not in _C:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, path)], capture_output=True)
        _C[k] = r.stdout if r.returncode == 0 else None
    return _C[k]


def _read(p):
    return open(need(p, os.path.basename(p)), encoding="utf-8").read()


def p_evidence(text):
    """(evidence lines read, problems): each `be07863b:path:a[-b]` "words" against the lines at be07863b."""
    bad, n = [], 0
    for m in EV.finditer(text):
        path, a, b, q = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2)), m.group(4)
        n += 1
        f = _show(MAIN, path)
        if f is None:
            bad.append("%s: no file at be07863b" % path)
            continue
        L = f.decode("utf-8", "replace").split("\n")
        if not (1 <= a <= b <= len(L)):
            bad.append("%s:%d-%d outside %d lines" % (path, a, b, len(L)))
            continue
        if _norm(q) not in _norm(" ".join(L[a - 1:b])):
            bad.append("%s:%d-%d does not read %r" % (path, a, b, q[:50]))
    return n, bad


def p_rows(text):
    """(state by id, problems): the K headings and the stated counts."""
    rows = HEAD.findall(text)
    st = dict(rows)
    bad = []
    if [r[0] for r in rows] != ["K-%02d" % i for i in range(1, 29)]:
        bad.append("K headings: %s" % [r[0] for r in rows])
    c = {s: sum(1 for v in st.values() if v == s) for s in STATES}
    m = re.search(r"\*\*Counts on `be07863b`:\*\* (\d+) rows; (\d+) STANDING, (\d+) RESOLVED, (\d+) SUPERSEDED\.", text)
    if not m or tuple(int(x) for x in m.groups()) != (len(rows), c["STANDING"], c["RESOLVED"], c["SUPERSEDED"]):
        bad.append("the stated counts %s disagree with the rows %s" % (m and m.groups(), c))
    if {k for k, v in st.items() if v == "STANDING"} != STANDING:
        bad.append("STANDING rows %s" % sorted(k for k, v in st.items() if v == "STANDING"))
    return st, bad


def _section(t, n):
    i = t.find("\n## %d. " % n)
    if i < 0:
        return None
    j = t.find("\n## ", i + 4)
    return t[i:] if j < 0 else t[i:j]


def p_block(t, st, old):
    """Problems of the assessment t against the table's states st and the assessment at be07863b, old."""
    bad = []
    s11 = _section(t, 11)
    if s11 is None:
        return ["no section 11"]
    rows = re.findall(r"^\| (K-\d\d) \| (yes|no) \| (STANDING|RESOLVED|SUPERSEDED) \|", s11, re.M)
    if [r[0] for r in rows] != ["K-%02d" % i for i in range(1, 29)]:
        bad.append("section 11's ids: %s" % [r[0] for r in rows])
    if {r[0]: r[2] for r in rows} != st:
        bad.append("section 11's states differ from the K table's")
    cand = dict(re.findall(r"^\| (K-\d\d) \| [^|]* \| [^|]* \| (yes|no)\b", _section(old, 5), re.M))
    if {r[0]: r[1] for r in rows} != cand:
        bad.append("section 11's candidate column differs from section 5's")
    c = {s: sum(1 for v in st.values() if v == s) for s in STATES}
    flat = " ".join(s11.split())
    if "28 rows, %d STANDING, %d RESOLVED, %d SUPERSEDED" % (c["STANDING"], c["RESOLVED"], c["SUPERSEDED"]) not in flat:
        bad.append("section 11's counts")
    t5, o5 = _section(t, 5), _section(old, 5)
    tl, ol = t5.split("\n"), o5.split("\n")
    if [l for l in tl if l.startswith("| ")] != [l for l in ol if l.startswith("| ")]:
        bad.append("section 5's tables differ from be07863b's")
    tt, oo = t.split("\n"), old.split("\n")
    moved = [i + 1 for i, l in enumerate(oo) if i >= len(tt) or not tt[i].startswith(l)]
    if moved:
        bad.append("lines of be07863b's assessment changed or moved: %s" % moved[:5])
    changed = [i + 1 for i, l in enumerate(oo) if i < len(tt) and tt[i] != l]
    if len(changed) > 1:
        bad.append("more than the one pointer line extended: %s" % changed[:5])
    return bad


def _one_insertion(old, new):
    """new is old with one inserted span that names record l4k (nothing of old removed or changed)."""
    i = 0
    while i < min(len(old), len(new)) and old[i] == new[i]:
        i += 1
    j = 0
    while j < min(len(old), len(new)) - i and old[len(old) - 1 - j] == new[len(new) - 1 - j]:
        j += 1
    return i + j == len(old) and "record l4k" in new[i:len(new) - j]


def _kt():
    return _read(KT)


def t_every_evidence_line_reads_at_main():
    _need_main()
    t = _kt()
    n, bad = p_evidence(t)
    assert n >= 65, "the K table's evidence lines read: %d" % n
    assert not bad, bad[:6]
    for nm in ["README.md"] + ["apply_l4k_%s.py" % s for s in SCRIPTS]:
        n2, bad2 = p_evidence(_read(os.path.join(REC, nm)))
        assert not bad2, (nm, bad2[:4])
    mut = t.replace('"round 2 has none"', '"round 2 has one"', 1)
    assert mut != t and p_evidence(mut)[1], "a changed quotation passed"
    mut = t.replace("DOWNSTREAM-REGISTER.md:134", "DOWNSTREAM-REGISTER.md:135", 1)
    assert mut != t and p_evidence(mut)[1], "a moved citation passed"


def t_the_k_rows_states_and_counts():
    t = _kt()
    st, bad = p_rows(t)
    assert not bad, bad
    for k in STANDING:
        body = t.split("### %s: " % k, 1)[1].split("\n### ", 1)[0]
        assert re.search(r"apply_l4k_\w+\.py|RESOLVED on `fnd/l4k`|register task L4A-\d+", body), "%s names no resolution or owner" % k
    assert "register task L4A-61" in t.split("### K-22: ", 1)[1].split("\n### ", 1)[0], "K-22's owner"
    for mut in (t.replace("### K-18: RESOLVED", "### K-18: STANDING", 1), t.replace("1 SUPERSEDED.", "2 SUPERSEDED.", 1),
                t.replace("### K-28: RESOLVED", "### K-28: CLOSED", 1)):
        assert mut != t and p_rows(mut)[1], "a changed state or count passed"


def t_the_assessment_restates_without_rewriting():
    _need_main()
    st, _ = p_rows(_kt())
    old = _show(MAIN, ASSESS)
    assert old is not None, "the assessment at be07863b"
    old = old.decode("utf-8")
    t = _read(os.path.join(ROOT, ASSESS))
    bad = p_block(t, st, old)
    assert not bad, bad
    assert p_block(t.replace("| K-03 | yes | STANDING |", "| K-03 | yes | RESOLVED |", 1), st, old), "a changed state passed"
    mut = t.replace("CLAIM CHANGE [H31:32] | NO |", "CLAIM CHANGE [H31:32] | YES |", 1)
    assert mut != t and p_block(mut, st, old), "a rewritten section 5 row passed"


def _scratch_tree(edits):
    td = tempfile.mkdtemp(prefix="l4k-")
    for rel in {e[0] for e in edits}:
        os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, rel), os.path.join(td, rel))
    return td


def _load(name):
    import importlib.util
    p = os.path.join(REC, "apply_l4k_%s.py" % name)
    sp = importlib.util.spec_from_file_location("l4k_apply_%s" % name, p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return p, m


def _cli(p, *a):
    return subprocess.run([sys.executable, "-B", p] + list(a), capture_output=True).returncode


def t_each_apply_script_is_pending_or_applied_and_refuses_a_bad_tree():
    for name in SCRIPTS:
        p, m = _load(name)
        rc = _cli(p, "--check")
        assert rc in (0, 3), "%s --check on this tree: exit %d" % (name, rc)
        td = _scratch_tree(m.EDITS)
        try:
            before = {rel: open(os.path.join(td, rel), "rb").read() for rel, _, _ in m.EDITS}
            if rc == 0:
                assert _cli(p, "--root", td) == 0, "%s did not write on a copy" % name
                for rel, old, new in m.EDITS:
                    t = open(os.path.join(td, rel), encoding="utf-8").read()
                    assert t.count(new) == 1 and t.count(old) == 0 and t.count("\n") == before[rel].decode("utf-8").count("\n"), name
                assert _cli(p, "--root", td) == 3, "%s: a second run did not exit 3" % name
                # a half-applied tree: the first edit only, on fresh copies
                shutil.rmtree(td)
                td = _scratch_tree(m.EDITS)
                rel, old, new = m.EDITS[0]
                fp = os.path.join(td, rel)
                t = open(fp, encoding="utf-8").read()
                if len(m.EDITS) > 1:
                    open(fp, "w", encoding="utf-8").write(t.replace(old, new, 1))
                    snap = {r: open(os.path.join(td, r), "rb").read() for r, _, _ in m.EDITS}
                    assert _cli(p, "--root", td) == 2, "%s: a partial state was not refused" % name
                    assert snap == {r: open(os.path.join(td, r), "rb").read() for r, _, _ in m.EDITS}, "%s wrote on a refusal" % name
                    open(fp, "w", encoding="utf-8").write(t)
                # an old text found twice
                open(fp, "w", encoding="utf-8").write(t + "\n" + old)
                assert _cli(p, "--root", td) == 2, "%s: a duplicated old text was not refused" % name
        finally:
            shutil.rmtree(td, ignore_errors=True)


def t_the_digests_and_counts_the_table_names():
    _need_main()
    for rev in ("06077cee85d0ed44c74c2a06c9fbb2030a0dedbc", "4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e", MAIN):
        b = _show(rev, EFS)
        if b is None and rev != MAIN:
            raise Skip("%s is not in this clone" % rev[:8])
        assert hashlib.sha256(b).hexdigest()[:16] == "d7f48ef5009684f9", "record efuse's page at %s" % rev[:8]
    f01 = "v2/docs/records/l9t5/l9t5_f01.out"
    con = "v2/docs/records/l9t5/l9t5_connected.out"
    for rev, want in ((CAND, "2aa78a957e497677"), (MAIN, "f1aa6ae62223e936")):
        if _show(rev, f01) is None:
            raise Skip("%s is not in this clone" % rev[:8])
        assert hashlib.sha256(_show(rev, f01)).hexdigest()[:16] == want, "l9t5_f01.out at %s" % rev[:8]
        pins = re.findall(r"^\s+([0-9a-f]{16}) v2/docs/records/l9t5/l9t5_f01\.out$", _show(rev, con).decode("utf-8"), re.M)
        assert pins == [want], "the connected output's pin of l9t5_f01.out at %s: %s" % (rev[:8], pins)
    stab = _show(MAIN, "v2/docs/records/l9t5/stability/DIGESTS-cr3.txt").decode("utf-8").split("\n")
    assert stab[14].startswith("v2/docs/records/l9t5/l9t5_f01.out pass 1: sha256=2aa78a957e497677"), "DIGESTS-cr3 line 15"
    l4o = _show(MAIN, "v2/docs/records/l4e9/l4e9_power_path.out").decode("utf-8").split("\n")
    for n in (55, 64, 67, 106):
        mm = re.match(r"^\s+\w+\s+([0-9a-f]{16})\s+(v2/\S+)$", l4o[n - 1])
        assert mm, "line %d is not a pin" % n
        assert hashlib.sha256(_show(MAIN, mm.group(2))).hexdigest()[:16] == mm.group(1), "L4-E9's pin at line %d" % n
    reg = _show(MAIN, "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md").decode("utf-8")
    assert len(re.findall(r"^\| R-\d+ \|", reg, re.M)) == 235, "the register's rows on be07863b"


def t_the_efuse_page_keeps_its_lines_and_its_history():
    _need_main()
    old = _show(MAIN, EFS).decode("utf-8")
    t = _read(os.path.join(ROOT, EFS))
    assert t.count("\n") == old.count("\n"), "record efuse's page moved lines"
    assert "round 2 has none" in t and "Round 2 is not\nreviewed.**" in t, "the round 2 sentences are kept as written"
    assert t.count("record l4k, the DESK-gate assessment's K-16") == 2, "the two dated notes"
    flat = " ".join(t.split())
    for w in ("P0-4: CONFIRMED AS CONDITIONAL on connector thermal qualification and the RockBLOCK build condition",
              "16. P0-4 eFuse conditions retained: CLOSED AS CONDITIONAL", "EF-F03 DESIGN DEFECT, OPEN"):
        assert w in flat, w
    tt, oo = t.split("\n"), old.split("\n")
    changed = [(a, b) for a, b in zip(tt, oo) if a != b]
    assert len(changed) == 2 and all(_one_insertion(b, a) for a, b in changed), "a line of be07863b's page was rewritten, not extended"
    a, b = changed[0]
    assert not _one_insertion(b, a.replace("Round 2 in one paragraph", "Round two in one paragraph", 1)), "a rewritten line passed"


def t_no_em_or_en_dash():
    files = [KT, os.path.join(REC, "README.md"), os.path.join(REC, "_l4k_apply.py"), os.path.abspath(__file__)]
    files += [os.path.join(REC, "apply_l4k_%s.py" % s) for s in SCRIPTS]
    for p in files:
        s = open(p, encoding="utf-8").read()
        assert not any(d in s for d in DASHES), "a dash in %s" % os.path.basename(p)
