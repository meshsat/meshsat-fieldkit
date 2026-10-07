"""The makers' PDF text as a committed verbatim input (MESHSAT-1357, Q-41 item 1, W34, 6 October 2026; v2/docs/records/_lib/).

The defect this guards: the records' generators ran pdftotext when they ran, so a host without poppler-data read 184 bytes of the
JST VH catalogue where the runner reads 39318, and a record's output changed with the host. The correction: the generators read the
text the re-take script took once on the runner (pdftext.py, retake_pdf_text.py), and never run pdftotext.

The predicates, each on a fixture in a temporary directory except the last two, which read this tree and never write it:
(a) with a fake pdftotext FIRST on PATH (shown to be the one a plain call reaches), the helper returns the committed text byte for byte
    and the fake is never called; (b) an absent text refuses with exit 2 and names the re-take command (and, for a held-back sheet,
    the fetch); an edited text, a text taken from another revision of the PDF and an undeclared extraction each refuse; (c) the re-take
    script writes the text and its sidecar for a two-page fixture PDF written here by hand (no reportlab needed), the page extraction
    holding only its page, the held-back sheet's text landing under held/ and reported held back, a second run writing nothing, and
    an absent declared PDF refused; (d) no converted generator calls pdftotext (parsed with ast, never grepped); (e) every extraction
    a converted record declares is present and current for every PDF present in this tree.

Added by W37 on 6 October 2026, each closing a finding of W36's review of W34's branch (`_runs/claude/w36rev/REPORT-AS-RECEIVED.md`):
(f) F-R1: three converted generators (efuse, l5r2, l9t5_case) run in a subprocess with a refusing pdftotext AND a refusing pdftocairo
    first on PATH, their output captured in a temporary file (never a tree's .out): exit 0, no call of either, every declared text's
    input line printed, the record's folder unchanged; and l4e9 and l4e11 run with a refusing pdftotext and a logging pdftocairo: no
    pdftotext call, the pdftocairo calls exactly the four pinned call sites' (1 and 5 per run); (d) widened (F-R1): a token named
    pdftotext anywhere in a string the code holds (a shell=True command, a command kept in a variable, /usr/bin/pdftotext, an f-string
    part), pdftocairo only at its four pinned call sites, and the record modules a converted generator reaches by path listed as KNOWN
    callers with their reason, every KNOWN entry still reached and still a caller; with the base commit present, all 25 sources of
    aed4bd23 caught; (g) F-R2: the re-take's CHANGED path on a fixture, and its refusal, with nothing written, of a held-back sheet's
    text that .gitignore would not exclude (and of a committed sheet's text it would); (h) F-R2: an orphan text, one no PDFTEXT table
    declares, detected on a fixture and absent from this tree; (i) F-P2: every held-back sheet a table declares names the fetch script
    that fetches THAT sheet, re-derived from the fetch scripts' own document lists, and the refusal names it.

Added by W55 on 6 October 2026, closing W53's finding (l8p_c4.py refused on this branch: its BZT52C read went through
l8p_guard.pdftext(), whose table did not declare it, and neither a test nor W36's run reached it):
(j) a static check, never a run: every helper call the converted generators and READERS reach (l8p_c4.py and the four scripts that
    call into a converted generator's reader), its PDF and options resolved with ast through the wrappers and every call reaching
    them (from another script too, as l8p_c4 called l8p_guard's), is declared in the PDFTEXT table the call names; every helper call
    of theirs is reached; no records script outside the two lists calls one of their reader functions; shown on fixtures first (a
    declared read passes; an undeclared sheet through another script's wrapper, an undeclared page and an unreadable argument fail;
    an outside caller is found); (k) the mutation: with l8p_c4.py as it was at 5b3153aa the check names l8p_guard.py:102 with the
    BZT52C sheet, and only that; (l) every extraction ANY PDFTEXT table under v2/docs/records declares has its text and sidecar from
    the present PDF, committed exactly when the sheet is; (m) l8p_c4.py runs with pdftotext and pdftocairo refused: exit 0, no call,
    its three text lines printed, its folder unchanged.

Added by W81 on 6 October 2026, closing W66's finding (set 32's full dry run stopped on a TEST: test_l8p.py:665 read TDK's held sheet
through l8p_drafts.pdftext(), whose table did not declare it; the check (j) walked the generators and never the tests):
(n) the walk of (j) with every test module as a caller (a test's name standing for a records script through the test's own loaders,
    its arguments carried into the wrappers, each pair recorded with the test line that asked; the helper called by a test with a
    table named PDFTEXT, X.PDFTEXT or PT.declared_in(<script>)), shown on fixtures: declared reads pass, an undeclared sheet through a
    wrapper and an undeclared mode through the helper fail naming the site and the test line, and W55's walk alone misses both;
(o) on this tree every pair a test asks for is declared and no helper call in a test is unreached (the tests' own reads are declared
    in their records' l8p_pdftext.py, l8r2_pdftext.py and l5r4_pdftext.py); the mutation without l8p_pdftext.py's TDK line names
    test_l8p's read of TDK's sheet; (p) the census of the test modules' other
    routes (their own process calls of pdftotext or pdftocairo, their calls of a v2/ecad/tools or records function that runs one) is
    KNOWN_DIRECT and KNOWN_TOOLVIA with reasons, and the records functions a test calls run only l4e9's and l4e11's pinned pdftocairo."""
import ast
import hashlib
import importlib.util
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
LIB = os.path.join(ROOT, "v2", "docs", "records", "_lib")
HELPER = os.path.join(LIB, "pdftext.py")
RETAKE = os.path.join(LIB, "retake_pdf_text.py")
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

# the generators converted by W34 (the brief's six records first, then the remaining run-time callers outside the l4e7 KEY's group
# and the accepted Layer 3 records); each record directory's PDFTEXT tables are what the re-take reads
CONVERTED = ("efuse/efuse_check.py", "l5r2/l5r2_interfaces.py", "l8r2/l8r2_drafts.py", "l8r2/l8r2_gndret.py", "l8r2/l8r2_p0.py",
             "l4e13/l4e13_panel.py", "l4e11/l4e11_power.py", "l4e9/l4e9_power_path.py",
             "l4e10/l4e10_cell_thermal.py", "l4e12/l4e12_thermal.py", "l7pwr/l7pwr_fans_th1.py", "l7r2/l7r2_items.py",
             "l8p/l8p_drafts.py", "l8p/l8p_guard.py", "l9pwr/l9pwr_budget.py", "l9stk/l9stk_copper.py", "l9stk/l9stk_protection.py",
             "l9t5/l9t5_a1.py", "l9t5/l9t5_case.py", "l9t5/l9t5_cm5.py", "l9t5/l9t5_drafts.py", "l9t5/l9t5_f01.py",
             "l9t5/l9t5_paloop.py", "l9t5/l9t5_t10.py", "l4e8/ripple_dense.py")
PDF = "v2/vendor/fix/fixture.pdf"
HELD = "v2/vendor/fix/held/sheet.pdf"
TEXT = "MESHSAT FIXTURE PAGE ONE  Current rating: 10 A\n\nline two, °C and Ω\n\f  PAGE TWO 7.5 A\n\f".encode("utf-8")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _pt():
    return _load("t_pdftext_helper", need(HELPER, "the helper"))


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _fixture(d, pdf_rel=PDF, text=TEXT, pdf_bytes=b"%PDF-1.4 a fixture, never parsed\n"):
    """A PDF (any bytes) and its committed text with a correct sidecar, as the re-take writes them."""
    PT = _pt()
    os.makedirs(os.path.join(d, os.path.dirname(pdf_rel)), exist_ok=True)
    open(os.path.join(d, pdf_rel), "wb").write(pdf_bytes)
    t = PT.text_path(pdf_rel, ["-layout"])
    os.makedirs(os.path.join(d, os.path.dirname(t)), exist_ok=True)
    open(os.path.join(d, t), "wb").write(text)
    meta = {"pdf": pdf_rel, "pdf_sha256": _sha(pdf_bytes), "text": t, "text_sha256": _sha(text), "text_bytes": len(text),
            "options": ["-layout"], "pdftotext": "pdftotext version 22.12.0"}
    open(os.path.join(d, PT.meta_path(t)), "w", encoding="utf-8").write(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    return os.path.join(d, t)


def _fake_bin(d):
    """A pdftotext that leaves a mark and prints something else: first on PATH."""
    b = os.path.join(d, "fakebin")
    os.makedirs(b)
    p = os.path.join(b, "pdftotext")
    open(p, "w").write("#!/bin/sh\necho called >> '%s'\necho FAKE PDFTOTEXT OUTPUT\n" % os.path.join(d, "CALLED"))
    os.chmod(p, 0o755)
    return dict(os.environ, PATH=b + os.pathsep + os.environ.get("PATH", ""))


READER = r"""
import importlib.util, sys
sp = importlib.util.spec_from_file_location("p", sys.argv[1]); PT = importlib.util.module_from_spec(sp); sp.loader.exec_module(PT)
decl = {sys.argv[3]: [["-layout"]]}
t = PT.pdf_text(sys.argv[2], sys.argv[3], sys.argv[4].split(), decl, sys.argv[5])
sys.stdout.buffer.write(t.encode("utf-8"))
"""


def _read(d, env, pdf_rel=PDF, options="-layout", record="v2/docs/records/fix"):
    return subprocess.run([sys.executable, "-B", "-c", READER, HELPER, d, pdf_rel, options, record], capture_output=True, env=env,
                          timeout=60)


def t_the_helper_returns_the_committed_text_and_never_runs_pdftotext():
    need(HELPER, "the helper")
    d = tempfile.mkdtemp(prefix="w34-a-")
    try:
        _fixture(d)
        env = _fake_bin(d)
        # the control: a plain call from that environment reaches the fake, so a helper that ran pdftotext would leave the mark
        ctl = subprocess.run(["pdftotext", "-v"], capture_output=True, env=env, timeout=30)
        assert b"FAKE PDFTOTEXT OUTPUT" in ctl.stdout and os.path.isfile(os.path.join(d, "CALLED")), "the fake is not first on PATH"
        os.remove(os.path.join(d, "CALLED"))
        r = _read(d, env)
        assert r.returncode == 0, r.stderr.decode()
        assert r.stdout == TEXT, "the helper did not return the committed text byte for byte"
        assert not os.path.exists(os.path.join(d, "CALLED")), "the helper ran pdftotext"
    finally:
        shutil.rmtree(d)


def t_an_absent_text_refuses_and_names_the_retake_command():
    need(HELPER, "the helper")
    d = tempfile.mkdtemp(prefix="w34-b-")
    try:
        t = _fixture(d)
        env = _fake_bin(d)
        os.remove(t)
        r = _read(d, env)
        err = r.stderr.decode()
        assert r.returncode == 2 and r.stdout == b"", (r.returncode, r.stdout[:80])
        assert "python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/fix" in err and "absent" in err, err
        assert "/tmp" not in err and d not in err, "the refusal prints a host path: %s" % err
        assert not os.path.exists(os.path.join(d, "CALLED")), "the helper ran pdftotext on the way to its refusal"
        h = _fixture(d, HELD)
        os.remove(h)
        err = _read(d, env, HELD).stderr.decode()
        # W37 (F-P2): the fixture's held sheet is in no fetch script, so the refusal says so instead of naming a script
        assert "no record's fetch_held_back.py fetches the held-back sheet" in err and "retake_pdf_text.py" in err, err
    finally:
        shutil.rmtree(d)


def t_an_edited_a_stale_or_an_undeclared_text_refuses():
    need(HELPER, "the helper")
    d = tempfile.mkdtemp(prefix="w34-b2-")
    try:
        t = _fixture(d)
        env = _fake_bin(d)
        assert _read(d, env).returncode == 0
        open(t, "ab").write(b"x")                                      # the text edited after the re-take
        r = _read(d, env)
        assert r.returncode == 2 and b"not the text its sidecar records" in r.stderr, r.stderr
        _fixture(d)
        open(os.path.join(d, PDF), "ab").write(b"another revision")   # the PDF changed under its text
        r = _read(d, env)
        assert r.returncode == 2 and b"taken from another file" in r.stderr, r.stderr
        _fixture(d)
        r = _read(d, env, options="-layout -f 2 -l 2")                # an extraction the table does not declare
        assert r.returncode == 2 and b"not declared" in r.stderr, r.stderr
        assert not os.path.exists(os.path.join(d, "CALLED"))
    finally:
        shutil.rmtree(d)


def _minimal_pdf(pages):
    """A valid PDF with one line of Helvetica text per page, its cross-reference table computed: no library needed."""
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", None, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    kids = []
    for s in pages:
        stream = "BT /F1 12 Tf 72 720 Td (%s) Tj ET" % s
        objs.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>"
                    % (len(objs)))
        kids.append("%d 0 R" % len(objs))
    objs[1] = "<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join(kids), len(kids))
    out, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += ("%d 0 obj\n%s\nendobj\n" % (i, o)).encode("latin-1")
    x = len(out)
    out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)).encode()
    out += b"".join(("%010d 00000 n \n" % o).encode() for o in offs)
    out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, x)).encode()
    return out


def t_the_retake_writes_the_text_and_its_sidecar_for_a_fixture_pdf():
    need(RETAKE, "the re-take script")
    if shutil.which("pdftotext") is None or shutil.which("git") is None:
        raise Skip("the re-take needs pdftotext and git on this host")
    PT = _pt()
    d = tempfile.mkdtemp(prefix="w34-c-")
    try:
        subprocess.run(["git", "init", "-q", d], check=True, timeout=30)
        open(os.path.join(d, ".gitignore"), "w").write("v2/vendor/fix/held/\n")
        pdf = _minimal_pdf(["MESHSAT FIXTURE PAGE ONE", "MESHSAT FIXTURE PAGE TWO"])
        for rel in (PDF, HELD):
            os.makedirs(os.path.join(d, os.path.dirname(rel)), exist_ok=True)
            open(os.path.join(d, rel), "wb").write(pdf)
        rec = os.path.join(d, "v2", "docs", "records", "fix")
        os.makedirs(rec)
        open(os.path.join(rec, "gen.py"), "w").write(
            "PDFTEXT = {%r: [['-layout'], ['-f', '2', '-l', '2', '-layout']], %r: [['-layout']]}\n" % (PDF, HELD))
        r = subprocess.run([sys.executable, "-B", RETAKE, rec], capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        assert "3 extraction(s): 0 unchanged, 3 written, 0 changed" in r.stdout, r.stdout
        full = open(os.path.join(d, PT.text_path(PDF, ["-layout"])), "rb").read()
        assert b"MESHSAT FIXTURE PAGE ONE" in full and b"MESHSAT FIXTURE PAGE TWO" in full, full
        direct = subprocess.run(["pdftotext", "-layout", os.path.join(d, PDF), "-"], capture_output=True).stdout
        assert full == direct, "the committed text is not the bytes pdftotext prints"
        p2 = open(os.path.join(d, PT.text_path(PDF, ["-layout", "-f", "2", "-l", "2"])), "rb").read()
        assert b"PAGE TWO" in p2 and b"PAGE ONE" not in p2, p2
        assert PT.text_path(PDF, ["-f", "2", "-l", "2", "-layout"]).endswith("/pdftext/fixture.layout.p2.txt")
        meta = json.load(open(os.path.join(d, PT.meta_path(PT.text_path(PDF, ["-layout", "-f", "2", "-l", "2"])))))
        v = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
        assert meta["pdf_sha256"] == _sha(pdf) and meta["text_sha256"] == _sha(p2) and meta["text_bytes"] == len(p2), meta
        assert meta["options"] == ["-layout", "-f", "2", "-l", "2"] and meta["pdf"] == PDF and meta["held_back"] is False, meta
        assert meta["pdftotext"] == (v.stderr or v.stdout).strip().splitlines()[0] and len(meta["taken"]) == 10, meta
        assert "poppler-data" in meta["poppler_data"] and "/tmp" not in json.dumps(meta), meta
        ht = PT.text_path(HELD, ["-layout"])
        assert ht == "v2/vendor/fix/held/pdftext/sheet.layout.txt" and os.path.isfile(os.path.join(d, ht)), ht
        assert "held back (ignored by .gitignore)" in r.stdout and "[to commit]" in r.stdout, r.stdout
        # the helper reads back what the re-take wrote
        env = _fake_bin(d)
        rb = _read(d, env)
        assert rb.returncode == 0 and rb.stdout == full and not os.path.exists(os.path.join(d, "CALLED")), rb.stderr
        # a second run writes nothing
        r2 = subprocess.run([sys.executable, "-B", RETAKE, rec], capture_output=True, text=True, timeout=120)
        assert r2.returncode == 0 and "3 unchanged, 0 written, 0 changed" in r2.stdout, r2.stdout
        # an absent declared PDF is refused, with the fetch named for a held-back one
        os.remove(os.path.join(d, HELD))
        r3 = subprocess.run([sys.executable, "-B", RETAKE, rec], capture_output=True, text=True, timeout=120)
        assert r3.returncode == 2 and "fetch_held_back.py" in r3.stderr, r3.stderr
    finally:
        shutil.rmtree(d)


# the tool names a converted generator must not hold in any string it runs or builds; pdftocairo is allowed only at its pinned sites.
# A token ends at white space or a shell character; a comma does not end one, so printed prose such as l4e9's "THE MAKERS' ROWS
# (pdftotext, the page cited)" (the text it reads was taken by pdftotext) is not read as a command.
TOKEN = re.compile(r"[\s;&|()`$<>=\"']+")
PDFTOCAIRO_SITES = {"l4e9/l4e9_power_path.py": 1, "l4e11/l4e11_power.py": 3}   # W36 F-P1: l4e9:2541; l4e11:348, :930, :1778 at 6dc69ad2
# record modules a converted generator reaches by path that still run pdftotext themselves, each with its reason (W36 F-R1; inventory
# section 5): the l4e7 KEY group, not converted because its KEY records the host's pdftotext and these sources are pinned by sha
KNOWN = {
    "l4e/l4e_replay.py": "the l4e7 KEY group: l4e13_panel.py runs l4e_replay.main() in-process (39 extractions per run, W36)",
    "l3plane/energy_basis.py": "the l4e7 KEY group (accepted Layer 3): imported by l4e_replay.py",
    "l3plane/vbus20_range.py": "the l4e7 KEY group (accepted Layer 3): imported by energy_basis.py",
    "r11dep/r11_dep.py": "the l4e7 KEY group: ripple_dense.py reaches it through L4-E4's compute()",
    "l4e5/l4e5_source_control.py": "the l4e7 KEY group: named (and re-run in a child process) by l4e6_fault_handling.py, which "
                                   "ripple_dense pins and parses without running it: the static walk's reach, not a run",
}
BASE = "aed4bd23"   # W34's base: every converted source there ran pdftotext, so the predicate must catch all 25 of them


def _strings(tree):
    """Every string constant the code holds, docstrings and other bare string statements left out (they never run)."""
    bare = {id(n.value) for n in ast.walk(tree) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    return [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in bare]


def _tool_calls(tree, tool="pdftotext"):
    """Lines holding a string with a token whose basename is the tool: an argument list's first element, a shell=True command, a
    command kept in a variable, os.popen/os.system, /usr/bin/pdftotext, an f-string's literal part. Parsed, never grepped; a tool
    name split across two literals ("pdf" + "totext") is the one form it cannot see."""
    return sorted({n.lineno for n in _strings(tree) if any(os.path.basename(t) == tool for t in TOKEN.split(n.value) if t)})


def _pdftotext_calls(tree):
    return _tool_calls(tree, "pdftotext")


def _reached(rel):
    """The record modules a records script names by path (a string constant resolving under v2/docs/records, against the repository,
    the script's folder or the records folder), followed transitively: imported, run in a child process or pinned by sha."""
    rec = os.path.join(ROOT, "v2", "docs", "records")
    seen, todo = set(), [rel]
    while todo:
        x = todo.pop()
        p = os.path.join(rec, x)
        for n in _strings(ast.parse(open(p, encoding="utf-8").read())):
            v = n.value
            if not v.endswith(".py") or any(c in v for c in " \n%<*"):
                continue
            for base in (ROOT, os.path.dirname(p), rec):
                q = os.path.normpath(os.path.join(base, v))
                if q.startswith(rec + os.sep) and os.path.isfile(q):
                    y = os.path.relpath(q, rec).replace(os.sep, "/")
                    if y not in seen and y != rel:
                        seen.add(y)
                        todo.append(y)
                    break
    return seen


def t_no_converted_generator_runs_pdftotext():
    """(d), widened by W37 for W36's F-R1: shell=True strings, a command in a variable, /usr/bin/pdftotext, f-strings; pdftocairo
    only at its four pinned sites; the reached record modules that still run pdftotext are KNOWN callers with a reason."""
    assert _pdftotext_calls(ast.parse("import subprocess\nsubprocess.run(['pdftotext', '-layout', p, '-'])\n")) == [2]
    assert _pdftotext_calls(ast.parse("import os\nos.popen('pdftotext -layout %s -' % p)\n")) == [2]
    assert _pdftotext_calls(ast.parse("import subprocess\nsubprocess.run('pdftotext -layout %s -' % p, shell=True)\n")) == [2]
    assert _pdftotext_calls(ast.parse("import subprocess\nTOOL = 'pdftotext'\nsubprocess.run([TOOL, p, '-'])\n")) == [2]
    assert _pdftotext_calls(ast.parse("import subprocess\nsubprocess.run(['/usr/bin/pdftotext', p, '-'])\n")) == [2]
    assert _pdftotext_calls(ast.parse("import os\nos.system(f'cd x && pdftotext -layout {p} -')\n")) == [2]
    assert _pdftotext_calls(ast.parse("import os\nos.system(\"sh -c 'cat a|pdftotext - -'\")\n")) == [2]
    assert _pdftotext_calls(ast.parse('"""pdftotext is never run here."""\n# pdftotext\nx = "the text pdftotextual"\n')) == []
    assert _tool_calls(ast.parse("import subprocess\nsubprocess.run(['pdftocairo', '-svg', p, '-'])\n"), "pdftocairo") == [2]
    reached_by = {}
    for rel in CONVERTED:
        p = need(os.path.join(ROOT, "v2", "docs", "records", rel), "a converted generator")
        tree = ast.parse(open(p, encoding="utf-8").read())
        assert not _pdftotext_calls(tree), "%s still runs pdftotext at line(s) %s" % (rel, _pdftotext_calls(tree))
        cairo = _tool_calls(tree, "pdftocairo")
        assert len(cairo) == PDFTOCAIRO_SITES.get(rel, 0), "%s holds pdftocairo at %s, pinned %d site(s)" % (
            rel, cairo, PDFTOCAIRO_SITES.get(rel, 0))
        tables = [n for n in tree.body if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "PDFTEXT" for t in n.targets)]
        assert len(tables) == 1 and isinstance(ast.literal_eval(tables[0].value), dict), "%s declares no PDFTEXT literal" % rel
        for m in _reached(rel):
            if m in CONVERTED or m.startswith("_lib/"):
                continue
            mt = ast.parse(open(os.path.join(ROOT, "v2", "docs", "records", m), encoding="utf-8").read())
            if _pdftotext_calls(mt):
                assert m in KNOWN, "%s reaches %s, which runs pdftotext and is not a KNOWN caller" % (rel, m)
                reached_by.setdefault(m, []).append(rel)
    stale = sorted(set(KNOWN) - set(reached_by))
    assert not stale, "KNOWN callers no converted generator reaches any more, or that no longer run pdftotext: %s" % stale
    # against the old defect: with W34's base present, every one of the 25 sources it converted is caught
    if subprocess.run(["git", "-C", ROOT, "cat-file", "-e", BASE + "^{commit}"], capture_output=True).returncode == 0:
        missed = []
        for rel in CONVERTED:
            r = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/records/%s" % (BASE, rel)], capture_output=True)
            if r.returncode != 0 or not _pdftotext_calls(ast.parse(r.stdout.decode("utf-8"))):
                missed.append(rel)
        assert not missed, "the predicate does not catch these sources of %s: %s" % (BASE, missed)


def t_every_declared_extraction_is_present_and_current():
    need(RETAKE, "the re-take script")
    PT = _pt()
    RT = _load("t_pdftext_retake", RETAKE)
    tracked = None
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "v2/vendor"], capture_output=True, text=True)
    if r.returncode == 0:
        tracked = set(r.stdout.splitlines())
    seen = 0
    for rec in sorted({os.path.dirname(c) for c in CONVERTED}):
        decl = RT.tables(os.path.join(ROOT, "v2", "docs", "records", rec))
        assert decl, "record %s declares nothing" % rec
        for pdf, opts in sorted(decl.items()):
            src = os.path.join(ROOT, pdf)
            if not os.path.isfile(src):
                assert PT.held(pdf), "%s (declared by %s) is a committed sheet and is absent" % (pdf, rec)
                continue                    # a held-back sheet not installed on this host: its readers refuse as before
            for o in opts:
                t = PT.text_path(pdf, o)
                tp = os.path.join(ROOT, t)
                assert os.path.isfile(tp) and os.path.isfile(PT.meta_path(tp)), "%s is absent: %s" % (t, PT.retake_command(
                    "v2/docs/records/" + rec))
                m = json.load(open(PT.meta_path(tp), encoding="utf-8"))
                assert m["pdf_sha256"] == _sha(open(src, "rb").read()), "%s was taken from another revision of %s" % (t, pdf)
                assert m["text_sha256"] == _sha(open(tp, "rb").read()) and m["pdf"] == pdf and m["text"] == t, t
                assert PT.tag(m["options"]) == PT.tag(o), (t, m["options"], o)
                if tracked is not None and not PT.held(pdf):
                    assert t in tracked and PT.meta_path(t) in tracked, "%s is not committed" % t
                if tracked is not None and PT.held(pdf):
                    assert t not in tracked, "%s, a held-back sheet's text, is committed" % t
                seen += 1
    assert seen, "no extraction checked"


# ---------------------------------------------------------------------------------------------- W37: the generators themselves
RUN_REFUSED = ("efuse/efuse_check.py", "l5r2/l5r2_interfaces.py", "l9t5/l9t5_case.py")
# the pdftocairo calls a run makes, as (options, repository-relative PDF): W36 logged 1 for l4e9 and 5 for l4e11 (F-P1), W37 the same
CAIRO_RUNS = {
    "l4e9/l4e9_power_path.py": [("-svg -f 6 -l 6", "v2/vendor/power/ti-csd19532q5b-n-fet.pdf")],
    "l4e11/l4e11_power.py": [("-svg -f 6 -l 6", "v2/vendor/power/ti-csd19532q5b-n-fet.pdf"),
                             ("-svg -f 6 -l 6", "v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf"),
                             ("-svg -f 6 -l 6", "v2/vendor/power/ti-csd19532q5b-n-fet.pdf"),
                             ("-svg -f 5 -l 5", "v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf"),
                             ("-svg -f 5 -l 5", "v2/vendor/power/held/aos-aons21357-rev2.1-2023-11.pdf")],
}


def _tools_bin(d, real_cairo=None):
    """pdftotext and pdftocairo first on PATH, each logging its arguments (one line, the unit separator 0x1f between them) to
    d/CALLS. pdftotext always refuses (exit 1); pdftocairo refuses too unless real_cairo is given: then it runs the real tool."""
    b = os.path.join(d, "toolbin")
    os.makedirs(b)
    log = os.path.join(d, "CALLS")
    for tool, tail in (("pdftotext", "exit 1"), ("pdftocairo", 'exec "%s" "$@"' % real_cairo if real_cairo else "exit 1")):
        open(os.path.join(b, tool), "w").write(
            "#!/bin/sh\n{ printf '%%s' '%s'; for a in \"$@\"; do printf '\\037%%s' \"$a\"; done; echo; } >> '%s'\n%s\n" % (tool, log, tail))
        os.chmod(os.path.join(b, tool), 0o755)
    return dict(os.environ, PATH=b + os.pathsep + os.environ.get("PATH", "")), log


def _calls(log):
    if not os.path.isfile(log):
        return []
    return [ln.split("\x1f") for ln in open(log, encoding="utf-8", errors="replace").read().splitlines() if ln]


def _held_ready(rel):
    """None when every held-back sheet the generator's table declares, and its held-back text, are on this host; else the reason."""
    PT = _pt()
    decl = PT.declared_in(os.path.join(ROOT, "v2", "docs", "records", rel))
    for pdf, opts in sorted(decl.items()):
        if not PT.held(pdf):
            continue
        if not os.path.isfile(os.path.join(ROOT, pdf)):
            return "%s is not on this host (%s)" % (pdf, PT.fetch_route(pdf, os.path.dirname(rel)))
        for o in opts:
            if not os.path.isfile(os.path.join(ROOT, PT.text_path(pdf, o))):
                return "%s is not on this host (%s)" % (PT.text_path(pdf, o), PT.retake_command("v2/docs/records/" + os.path.dirname(rel)))
    return None


def _status(rel):
    r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--untracked-files=all", "--", "v2/docs/records/" + os.path.dirname(rel)],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def _run_generator(rel, env, d):
    """The generator from the repository root (as its usage line says), stdout into a temporary file under d (never its .out)."""
    out = os.path.join(d, os.path.basename(rel) + ".stdout")
    with open(out, "wb") as f:
        r = subprocess.run([sys.executable, "-B", os.path.join("v2", "docs", "records", rel)], cwd=ROOT, env=env, stdout=f,
                           stderr=subprocess.PIPE, timeout=600)
    return r.returncode, open(out, encoding="utf-8", errors="replace").read(), r.stderr.decode("utf-8", "replace")


def _text_lines_printed(rel, stdout):
    """Every declared extraction's input line: its text path and the first 16 of its sha256 on one line of the output."""
    PT = _pt()
    lines = stdout.splitlines()
    missing = []
    for t, h, _held in PT.inputs(ROOT, PT.declared_in(os.path.join(ROOT, "v2", "docs", "records", rel))):
        if not h or not any(t in ln and h[:16] in ln for ln in lines):
            missing.append(t)
    return missing


def t_three_converted_generators_run_with_pdftotext_and_pdftocairo_refused():
    """W36's F-R1: no test ran a converted generator with the fake on PATH (a generator bypassing the helper, or reaching pdftotext
    through an import, passed). efuse, l5r2 and l9t5_case (which reads through l9t5_paloop) run here with both tools refusing."""
    for rel in RUN_REFUSED:
        need(os.path.join(ROOT, "v2", "docs", "records", rel), "a converted generator")
        why = _held_ready(rel)
        if why:
            raise Skip("%s: %s" % (rel, why))
    for rel in RUN_REFUSED:
        d = tempfile.mkdtemp(prefix="w37-f-")
        try:
            env, log = _tools_bin(d)
            before = _status(rel)
            rc, out, err = _run_generator(rel, env, d)
            assert rc == 0, "%s exited %d with both tools refused: %s" % (rel, rc, err.strip()[-400:])
            assert _calls(log) == [], "%s called %s" % (rel, _calls(log))
            assert out.strip(), "%s printed nothing" % rel
            missing = _text_lines_printed(rel, out)
            assert not missing, "%s does not print the input line of %s" % (rel, missing)
            assert _status(rel) == before, "%s changed its record folder: %r then %r" % (rel, before, _status(rel))
        finally:
            shutil.rmtree(d)


def t_l4e9_and_l4e11_run_pdftocairo_only_at_their_pinned_sites_and_never_pdftotext():
    """W36's F-P1 and F-R1: l4e9 and l4e11 still run pdftocairo -svg (one and three call sites); with pdftotext refused and pdftocairo
    logged, each exits 0, never calls pdftotext, and calls pdftocairo exactly as pinned (1 and 5 calls per run)."""
    real = shutil.which("pdftocairo")
    if real is None:
        raise Skip("pdftocairo is not on this host (poppler-utils): l4e9 and l4e11 read two plotted curves with it")
    for rel in sorted(CAIRO_RUNS):
        need(os.path.join(ROOT, "v2", "docs", "records", rel), "a converted generator")
        why = _held_ready(rel)
        if why:
            raise Skip("%s: %s" % (rel, why))
    for rel in sorted(CAIRO_RUNS):
        d = tempfile.mkdtemp(prefix="w37-f2-")
        try:
            env, log = _tools_bin(d, real)
            before = _status(rel)
            rc, out, err = _run_generator(rel, env, d)
            calls = _calls(log)
            assert rc == 0, "%s exited %d: %s" % (rel, rc, err.strip()[-400:])
            assert not [c for c in calls if c[0] == "pdftotext"], "%s called pdftotext: %s" % (rel, calls)
            got = [(" ".join(c[1:-2]), os.path.relpath(c[-2], ROOT).replace(os.sep, "/")) for c in calls if c[0] == "pdftocairo"]
            assert sorted(got) == sorted(CAIRO_RUNS[rel]) and all(c[-1] == "-" for c in calls), "%s: pdftocairo %s, pinned %s" % (
                rel, got, CAIRO_RUNS[rel])
            missing = _text_lines_printed(rel, out)
            assert not missing, "%s does not print the input line of %s" % (rel, missing)
            assert _status(rel) == before, "%s changed its record folder" % rel
        finally:
            shutil.rmtree(d)


# -------------------------------------------------------------------------------------------- W37: the re-take's other paths
def _fixture_repo(d, ignore):
    subprocess.run(["git", "init", "-q", d], check=True, timeout=30)
    open(os.path.join(d, ".gitignore"), "w").write(ignore)
    rec = os.path.join(d, "v2", "docs", "records", "fix")
    os.makedirs(rec)
    open(os.path.join(rec, "gen.py"), "w").write("PDFTEXT = {%r: [['-layout']], %r: [['-layout']]}\n" % (PDF, HELD))
    return rec


def _put(d, rel, data):
    os.makedirs(os.path.join(d, os.path.dirname(rel)), exist_ok=True)
    open(os.path.join(d, rel), "wb").write(data)


def t_the_retake_reports_a_changed_text_and_refuses_a_text_gitignore_disagrees_with():
    """W36's F-R2: the re-take's CHANGED path, and its refusal of a held-back sheet's text .gitignore would not exclude, were never
    exercised. Since W37 that refusal (and its mirror for a committed sheet's text) comes BEFORE anything is written."""
    need(RETAKE, "the re-take script")
    if shutil.which("pdftotext") is None or shutil.which("git") is None:
        raise Skip("the re-take needs pdftotext and git on this host")
    PT = _pt()
    d = tempfile.mkdtemp(prefix="w37-g-")
    try:
        rec = _fixture_repo(d, "v2/vendor/fix/held/\n")
        one, two = _minimal_pdf(["MESHSAT FIXTURE REVISION ONE"]), _minimal_pdf(["MESHSAT FIXTURE REVISION TWO, LONGER"])
        _put(d, PDF, one)
        _put(d, HELD, one)
        r = subprocess.run([sys.executable, "-B", RETAKE, rec], capture_output=True, text=True, timeout=120)
        assert r.returncode == 0 and "0 unchanged, 2 written, 0 changed" in r.stdout, (r.stdout, r.stderr)
        t = os.path.join(d, PT.text_path(PDF, ["-layout"]))
        old = open(t, "rb").read()
        _put(d, PDF, two)                                   # the maker's sheet changed under its text
        r = subprocess.run([sys.executable, "-B", RETAKE, rec], capture_output=True, text=True, timeout=120)
        assert r.returncode == 0 and "1 unchanged, 0 written, 1 changed" in r.stdout, (r.stdout, r.stderr)
        new = open(t, "rb").read()
        line = [ln for ln in r.stdout.splitlines() if ln.strip().startswith("CHANGED")]
        assert len(line) == 1 and "(was %s, %d bytes)" % (_sha(old)[:16], len(old)) in line[0] and _sha(new)[:16] in line[0], line
        assert b"REVISION TWO" in new and json.load(open(PT.meta_path(t)))["pdf_sha256"] == _sha(two)
        env = _fake_bin(d)
        rb = _read(d, env)
        assert rb.returncode == 0 and rb.stdout == new and not os.path.exists(os.path.join(d, "CALLED")), rb.stderr
        # a .gitignore that does not exclude the held-back sheet's text: refused, and the text is not written
        ht = os.path.join(d, PT.text_path(HELD, ["-layout"]))
        os.remove(ht)
        os.remove(PT.meta_path(ht))
        open(os.path.join(d, ".gitignore"), "w").write("v2/vendor/fix/held/*.pdf\n")
        r = subprocess.run([sys.executable, "-B", RETAKE, rec], capture_output=True, text=True, timeout=120)
        assert r.returncode == 2 and "held-back sheet's text but .gitignore does not exclude it (nothing written)" in r.stderr, r.stderr
        assert not os.path.exists(ht) and not os.path.exists(PT.meta_path(ht)), "the refused held-back text was written"
        # and its mirror: a committed sheet's text that .gitignore would exclude
        open(os.path.join(d, ".gitignore"), "w").write("v2/vendor/fix/held/\nv2/vendor/fix/pdftext/\n")
        os.remove(t)
        os.remove(PT.meta_path(t))
        r = subprocess.run([sys.executable, "-B", RETAKE, rec, PDF], capture_output=True, text=True, timeout=120)
        assert r.returncode == 2 and "committed sheet's text but .gitignore excludes it (nothing written)" in r.stderr, r.stderr
        assert not os.path.exists(t), "the refused committed text was written"
    finally:
        shutil.rmtree(d)


# ------------------------------------------------------------------------------------------------------ W37: orphan texts
def _declared_texts(root, record_dirs):
    """Every text path the PDFTEXT tables of these record folders declare (the re-take's own reading of them)."""
    RT = _load("t_pdftext_retake_o", RETAKE)
    PT = _pt()
    out = set()
    for rd in record_dirs:
        for pdf, opts in RT.tables(rd).items():
            out.update(PT.text_path(pdf, o) for o in opts)
    return out


def _orphans(root, declared):
    """Files in a pdftext/ folder under v2/vendor (committed or held back) that no declared extraction accounts for: a text, its
    sidecar, or anything else."""
    found = []
    base = os.path.join(root, "v2", "vendor")
    for dp, _dn, fn in os.walk(base):
        if os.path.basename(dp) != "pdftext":
            continue
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/")
            t = rel[:-len(".meta.json")] if rel.endswith(".txt.meta.json") else rel
            if t not in declared:
                found.append(rel)
    return sorted(found)


def t_an_orphan_text_is_detected_and_this_tree_has_none():
    """W36's F-R2: an orphan text, one no PDFTEXT table declares, went unnoticed. The detector on a fixture, then on this tree."""
    need(RETAKE, "the re-take script")
    PT = _pt()
    d = tempfile.mkdtemp(prefix="w37-h-")
    try:
        rec = os.path.join(d, "v2", "docs", "records", "fix")
        os.makedirs(rec)
        open(os.path.join(rec, "gen.py"), "w").write("PDFTEXT = {%r: [['-layout']]}\n" % PDF)
        _fixture(d)                                                      # the declared text and its sidecar
        orphan = PT.text_path(PDF, ["-raw"])                             # a text of the same sheet no table declares
        _put(d, orphan, b"orphan\n")
        _put(d, PT.meta_path(orphan), b"{}\n")
        _put(d, "v2/vendor/fix/held/pdftext/gone.layout.txt", b"orphan\n")  # a held-back text whose table entry is gone
        got = _orphans(d, _declared_texts(d, [rec]))
        assert got == sorted([orphan, PT.meta_path(orphan), "v2/vendor/fix/held/pdftext/gone.layout.txt"]), got
        assert PT.text_path(PDF, ["-layout"]) not in got
    finally:
        shutil.rmtree(d)
    rec_root = os.path.join(ROOT, "v2", "docs", "records")
    dirs = [os.path.join(rec_root, x) for x in sorted(os.listdir(rec_root)) if os.path.isdir(os.path.join(rec_root, x))
            and any(n.endswith(".py") for n in os.listdir(os.path.join(rec_root, x)))]
    got = _orphans(ROOT, _declared_texts(ROOT, dirs))
    assert not got, "texts no PDFTEXT table declares (%d): %s" % (len(got), got[:10])


# --------------------------------------------------------------------------------------- W37: the held sheets' fetch routes
def _fetched_by(script):
    """The repository-relative held-back PDFs a fetch_held_back.py lists (its document list, parsed, never run): full v2/ paths, or
    names under its default destination os.path.join(ROOT or REPO, "v2", "vendor", ..., "held")."""
    tree = ast.parse(open(script, encoding="utf-8").read())
    base = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "join" and len(n.args) > 1 \
                and isinstance(n.args[0], ast.Name) and n.args[0].id in ("ROOT", "REPO") \
                and all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in n.args[1:]):
            c = "/".join(a.value for a in n.args[1:])
            if c.startswith("v2/vendor/") and c.endswith("/held") and base is None:
                base = c
    out = set()
    for n in _strings(tree):
        v = n.value
        if v.endswith(".pdf") and "://" not in v and " " not in v:
            if v.startswith("v2/"):
                out.add(os.path.normpath(v).replace(os.sep, "/"))
            elif base:
                out.add(os.path.normpath(base + "/" + v).replace(os.sep, "/"))
    return out


def t_every_held_sheet_names_the_script_that_fetches_it():
    """W36's F-P2: the refusal named "the record's fetch_held_back.py" for every held-back sheet, the wrong script for 12 reads.
    pdftext.FETCH must equal, for every held-back sheet a PDFTEXT table declares, the records whose fetch script lists it; the refusal
    names the reader's own script when it is one of them, else the first; a sheet no script fetches is said to have no route."""
    need(HELPER, "the helper")
    PT = _pt()
    RT = _load("t_pdftext_retake_f", RETAKE)
    rec_root = os.path.join(ROOT, "v2", "docs", "records")
    fetchers = {}
    for x in sorted(os.listdir(rec_root)):
        f = os.path.join(rec_root, x, "fetch_held_back.py")
        if os.path.isfile(f):
            for pdf in _fetched_by(f):
                fetchers.setdefault(pdf, set()).add(x)
    declared = set()
    for x in sorted(os.listdir(rec_root)):
        if os.path.isdir(os.path.join(rec_root, x)) and any(n.endswith(".py") for n in os.listdir(os.path.join(rec_root, x))):
            declared.update(p for p in RT.tables(os.path.join(rec_root, x)) if PT.held(p))
    assert declared, "no held-back sheet declared"
    want = {p: tuple(sorted(fetchers.get(p, ()))) for p in declared}
    assert set(PT.FETCH) == declared, "FETCH lists %s and lacks %s" % (sorted(set(PT.FETCH) - declared), sorted(declared - set(PT.FETCH)))
    wrong = {p: (PT.FETCH[p], want[p]) for p in declared if tuple(sorted(PT.FETCH[p])) != want[p]}
    assert not wrong, "FETCH names other scripts than the fetch scripts' lists: %s" % wrong
    assert all(want[p] for p in declared), "held-back sheets with no fetch route: %s" % sorted(p for p in declared if not want[p])
    for p, recs in PT.FETCH.items():
        for r in recs:
            assert os.path.isfile(os.path.join(ROOT, PT.FETCH_SCRIPT % r)), "%s: %s is not a file" % (p, PT.FETCH_SCRIPT % r)
    # the words: the reader's own when listed, else the first; and no route for a sheet no script fetches
    assert PT.fetch_route("v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf", "v2/docs/records/l4e12").endswith(
        "python3 v2/docs/records/s117/fetch_held_back.py")
    assert PT.fetch_route("v2/vendor/power/held/littelfuse-997-mini58v-rev2025-11-18.pdf", "v2/docs/records/l4e9").endswith(
        "v2/docs/records/l4e9/fetch_held_back.py")
    assert PT.fetch_route("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "v2/docs/records/efuse").endswith(
        "v2/docs/records/l4e11/fetch_held_back.py")
    assert "no record's fetch_held_back.py fetches" in PT.fetch_route("v2/vendor/x/held/none.pdf", "v2/docs/records/efuse")
    # and through the helper's refusal, in a subprocess (it exits 2): l4e12's absent CSD17577 text names s117's script
    d = tempfile.mkdtemp(prefix="w37-i-")
    try:
        held = "v2/vendor/ti/held/ti-csd17577q5a-slps516.pdf"
        os.remove(_fixture(d, held))
        r = _read(d, _fake_bin(d), held, record="v2/docs/records/l4e12")
        err = r.stderr.decode()
        assert r.returncode == 2 and "fetch the held-back sheet with python3 v2/docs/records/s117/fetch_held_back.py, then python3 " \
            "v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l4e12" in err, err
    finally:
        shutil.rmtree(d)


# ----------------------------------------------------------------------- W55: every extraction site declared, read statically
# W53 found (6 October 2026, 18:09 CEST) that l8p_c4.py refused on this branch: it read the BZT52C sheet through l8p_guard.pdftext(),
# whose table did not declare it, and no test or run had reached that call (W36 ran 23 of the 25 converted generators; l8p_c4 is not
# one of them and names no pdftotext). The check below finds that class of gap without running anything: every call of the helper's
# pdf_text() that the converted generators and their readers reach, its PDF and options resolved with ast through the wrappers and
# the calls that reach them (also from another script, as l8p_c4 called l8p_guard's), against the PDFTEXT table the call names.
# READERS: the records scripts that are not converted generators but reach one's reader: l8p_c4.py (its own table since W55) and the
# four the scan below finds calling into a converted script (each also ran with both tools refused, W55's run of 6 October 2026).
READERS = ("l8p/l8p_c4.py", "l8r2/l8r2_dist.py", "l9t5/check_f01_netlist.py", "l9t5/l9t5_connected.py", "l9t5/l9t5_f01_drafts.py")
GAP_BASE = "5b3153aa"   # fnd/w34pdftext before W55: l8p_c4.py's BZT52C read was in no table (the mutation the check must catch)
_CAP = 400              # values one expression may take before it counts as unresolved
_STEPS = 20000          # function readings per walk


class _Unknown(Exception):
    pass


def _uniq(vals):
    out, seen = [], set()
    for v in vals:
        k = repr(v)
        if k not in seen:
            seen.add(k)
            out.append(v)
            if len(out) > _CAP:
                raise _Unknown("more than %d values" % _CAP)
    return out


def _product(lists):
    acc = [()]
    for lst in lists:
        acc = _uniq([a + (b,) for a in acc for b in lst])
    return acc


class _Script:
    """One records script read with ast (never imported or run): its module-level bindings, its functions, the scripts its names
    stand for (an import from its own folder, a spec_from_file_location loader, or a function of it that hands a parameter to one)."""

    def __init__(self, world, rel):
        self.world, self.rel = world, rel
        src = world.sources[rel] if rel in world.sources else open(os.path.join(world.records, rel), encoding="utf-8").read()
        self.tree = ast.parse(src, rel)
        self.assigns, self.funcs, self.imports = {}, {}, {}
        for n in self.tree.body:
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        self.assigns.setdefault(t.id, []).append(n.value)
            elif isinstance(n, ast.FunctionDef):
                self.funcs[n.name] = n
        for n in ast.walk(self.tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    self.imports[a.asname or a.name] = a.name
            elif isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                self.assigns.setdefault("\0" + n.targets[0].id, []).append(n.value)   # any level: the loaders' names
        self._mod, self._busy, self._alias = {}, set(), {}

    def value(self, name):
        if name in self._mod:
            return self._mod[name]
        if name in self._busy or name not in self.assigns:
            raise _Unknown("the name %s" % name)
        self._busy.add(name)
        try:
            vals = _uniq([v for e in self.assigns[name] for v in self.world.eval(self, e, {})])
        except _Unknown:
            if name not in ("TOP", "ROOT", "REPO"):
                raise
            vals = [""]          # the repository's root (git rev-parse or a dirname chain): paths stay relative to it
        finally:
            self._busy.discard(name)
        self._mod[name] = vals
        return vals

    def alias(self, name):
        if name not in self._alias:
            self._alias[name] = self._find(name)
        return self._alias[name]

    def _records_rel(self, expr):
        try:
            paths = self.world.eval(self, expr, {})
        except _Unknown:
            return None
        for p in paths:
            q = posixpath.normpath(p) if isinstance(p, str) else ""
            if q.startswith("v2/docs/records/"):
                return q[len("v2/docs/records/"):]
        return None

    def _find(self, name):
        if name in self.imports:
            cand = posixpath.join(posixpath.dirname(self.rel), self.imports[name] + ".py")
            if os.path.isfile(os.path.join(self.world.records, cand)) or cand in self.world.sources:
                return cand
        for e in self.assigns.get("\0" + name, []):
            if not isinstance(e, ast.Call):
                continue
            if isinstance(e.func, ast.Name) and e.func.id in self.funcs:          # NAME = load(PATH, ...)
                fd = self.funcs[e.func.id]
                params = [x.arg for x in fd.args.args]
                for s in ast.walk(fd):
                    if isinstance(s, ast.Call) and getattr(s.func, "attr", "") == "spec_from_file_location" and len(s.args) > 1 \
                            and isinstance(s.args[1], ast.Name) and s.args[1].id in params and params.index(s.args[1].id) < len(e.args):
                        r = self._records_rel(e.args[params.index(s.args[1].id)])
                        if r:
                            return r
            if getattr(e.func, "attr", "") == "module_from_spec" and e.args and isinstance(e.args[0], ast.Name):
                for s in self.assigns.get("\0" + e.args[0].id, []):
                    if isinstance(s, ast.Call) and getattr(s.func, "attr", "") == "spec_from_file_location" and len(s.args) > 1:
                        r = self._records_rel(s.args[1])
                        if r:
                            return r
        return None


class _World:
    """The extraction sites reached from some records scripts: {(script, line): {"table": script, "pairs": {(pdf, options)}, "why":
    {reason it is unresolved}}}. Arguments are read through the wrappers per call (a For loop per element, an If by its test where
    the test reads, both branches where it does not), so a site's candidates are the extractions its calls can ask for."""

    def __init__(self, records, sources=None):
        self.records, self.sources = records, dict(sources or {})
        self.mods, self.sites, self.todo, self.done, self.steps = {}, {}, [], set(), 0
        self.cur, self.edges, self.home = None, set(), {}

    def mod(self, rel):
        if rel not in self.mods:
            self.mods[rel] = _Script(self, rel)
        return self.mods[rel]

    def eval(self, m, e, env, depth=0):
        if depth > 16:
            raise _Unknown("too deep")
        ev = lambda x: self.eval(m, x, env, depth + 1)   # noqa: E731
        if isinstance(e, ast.Constant):
            return [e.value]
        if isinstance(e, ast.Name):
            if e.id in env:
                if env[e.id] is None:
                    raise _Unknown("the local %s" % e.id)
                return env[e.id]
            if e.id == "__file__":
                return ["v2/docs/records/" + m.rel]
            return m.value(e.id)
        if isinstance(e, (ast.List, ast.Tuple)):
            if any(isinstance(x, ast.Starred) for x in e.elts):
                raise _Unknown("a starred element")
            return _product([ev(x) for x in e.elts])
        if isinstance(e, ast.Dict):
            d = {}
            for k, v in zip(e.keys, e.values):
                if k is None:
                    raise _Unknown("a dict unpacking")
                ks, vs = ev(k), ev(v)
                if len(ks) != 1 or len(vs) != 1:
                    raise _Unknown("a dict entry of several values")
                d[ks[0]] = vs[0]
            return [d]
        if isinstance(e, ast.Attribute):
            if ast.unparse(e) == "os.sep":
                return ["/"]
            if isinstance(e.value, ast.Name):
                a = m.alias(e.value.id)
                if a and not a.startswith("_lib/"):
                    return self.mod(a).value(e.attr)
            raise _Unknown("the attribute %s" % ast.unparse(e))
        if isinstance(e, ast.Subscript):
            out = []
            for v in ev(e.value):
                for k in ev(e.slice):
                    try:
                        out.append(v[k])
                    except (KeyError, IndexError, TypeError):
                        pass
            return _uniq(out)
        if isinstance(e, ast.BoolOp):
            out = [None]
            for i, x in enumerate(e.values):
                nxt = []
                for v in (out if i else [None]):
                    if i and (bool(v) if isinstance(e.op, ast.Or) else not bool(v)):
                        nxt.append(v)
                    else:
                        nxt += ev(x)
                out = _uniq(nxt)
            return out
        if isinstance(e, ast.IfExp):
            tv = self.truth(m, e.test, env)
            return _uniq((ev(e.body) if True in tv else []) + (ev(e.orelse) if False in tv else []))
        if isinstance(e, ast.BinOp) and isinstance(e.op, (ast.Add, ast.Mod)):
            out = []
            for a in ev(e.left):
                for b in ev(e.right):
                    try:
                        out.append(a + b if isinstance(e.op, ast.Add) else a % b)
                    except TypeError:
                        raise _Unknown("the operands of %s" % ast.unparse(e))
            return _uniq(out)
        if isinstance(e, ast.Call):
            return self.call(m, e, env, depth)
        raise _Unknown("a %s" % type(e).__name__)

    def call(self, m, e, env, depth):
        ev = lambda x: self.eval(m, x, env, depth + 1)   # noqa: E731
        f, args = ast.unparse(e.func), e.args
        if f == "os.path.join":
            return _uniq([posixpath.join(*p) for p in _product([ev(a) for a in args])])
        if f in ("os.path.dirname", "os.path.basename", "os.path.normpath", "os.path.abspath", "os.path.realpath"):
            fn = {"os.path.dirname": posixpath.dirname, "os.path.basename": posixpath.basename}.get(f, posixpath.normpath)
            return _uniq([fn(v) for v in ev(args[0])])
        if f == "os.path.relpath":
            base = ev(args[1]) if len(args) > 1 else [""]
            return _uniq([posixpath.normpath(v) if b in ("", ".") else posixpath.relpath(v, b) for v in ev(args[0]) for b in base])
        if f == "str" and len(args) == 1:
            return _uniq([str(v) for v in ev(args[0])])
        if f == "range" and 1 <= len(args) <= 2:
            return _uniq([tuple(range(*p)) for p in _product([ev(x) for x in args])])
        if f in ("sorted", "list", "tuple") and len(args) == 1 and not e.keywords:
            out = []
            for v in ev(args[0]):
                try:
                    out.append(tuple(sorted(v)) if f == "sorted" else tuple(v))
                except TypeError:
                    raise _Unknown("the call %s" % ast.unparse(e))
            return _uniq(out)
        if isinstance(e.func, ast.Attribute) and e.func.attr in ("items", "keys", "values") and not args:
            out = []
            for v in ev(e.func.value):
                if not isinstance(v, dict):
                    raise _Unknown("%s of a %s" % (e.func.attr, type(v).__name__))
                out.append(tuple(getattr(v, e.func.attr)()))
            return _uniq(out)
        if isinstance(e.func, ast.Name) and e.func.id in m.funcs:      # a one-line function of the script (rel, path, ...)
            fd = m.funcs[e.func.id]
            body = [s for s in fd.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            if len(body) == 1 and isinstance(body[0], ast.Return) and body[0].value is not None:
                return _uniq([v for b in self.bindings(m, fd, e, m, env) for v in self.eval(m, body[0].value, b, depth + 1)])
        raise _Unknown("the call %s" % f)

    def truth(self, m, test, env):
        try:
            return {bool(v) for v in self.eval(m, test, env)}
        except _Unknown:
            return {True, False}

    def bindings(self, callee, fd, call, caller, env):
        """Each parameter read from one call (an argument in the caller's scope, a default in the callee's; None when unread)."""
        params = [a.arg for a in fd.args.args]
        defaults = dict(zip(params[len(params) - len(fd.args.defaults):], fd.args.defaults))
        kw = {k.arg: k.value for k in call.keywords if k.arg}
        vals = {}
        for i, p in enumerate(params):
            if i < len(call.args):
                x, where, scope = call.args[i], caller, env
            elif p in kw:
                x, where, scope = kw[p], caller, env
            else:
                x, where, scope = defaults.get(p), callee, {}
            try:
                vals[p] = None if x is None or isinstance(x, ast.Starred) else self.eval(where, x, scope)
            except _Unknown:
                vals[p] = None
        known = [p for p in params if vals[p] is not None]
        out = []
        for combo in _product([vals[p] for p in known]):
            b = {p: None for p in params}
            b.update({p: [v] for p, v in zip(known, combo)})
            out.append(b)
        return out

    def run(self, m, stmts, env):
        for s in stmts:
            env = self.step(m, s, env)
        return env

    def merge(self, *envs):
        out = {}
        for k in set().union(*envs):
            vs = [e.get(k) for e in envs if k in e]
            try:
                out[k] = None if any(v is None for v in vs) else _uniq([x for v in vs for x in v])
            except _Unknown:
                out[k] = None
        return out

    def bind(self, target, vals, env):
        if isinstance(target, ast.Name):
            env[target.id] = vals
        elif isinstance(target, (ast.Tuple, ast.List)):
            for i, t in enumerate(target.elts):
                try:
                    sub = None if vals is None else _uniq([v[i] for v in vals])
                except (TypeError, IndexError, KeyError, _Unknown):
                    sub = None
                self.bind(t, sub, env)

    def elements(self, m, it, env):
        out = []
        for v in self.eval(m, it, env):
            if not isinstance(v, (dict, list, tuple)):
                raise _Unknown("iteration over a %s" % type(v).__name__)
            out += list(v)
        return _uniq(out)

    def step(self, m, s, env):
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return env
        own = {ast.If: lambda: [s.test], ast.While: lambda: [s.test], ast.For: lambda: [s.iter],
               ast.With: lambda: [i.context_expr for i in s.items], ast.Try: lambda: []}.get(type(s))
        for x in (own() if own else [c for c in ast.iter_child_nodes(s) if isinstance(c, ast.expr)]):
            self.visit(m, x, env)
        env = dict(env)
        if isinstance(s, (ast.Assign, ast.AnnAssign)) and s.value is not None:
            try:
                vals = self.eval(m, s.value, env)
            except _Unknown:
                vals = None
            for t in (s.targets if isinstance(s, ast.Assign) else [s.target]):
                self.bind(t, vals, env)
        elif isinstance(s, ast.AugAssign) and isinstance(s.target, ast.Name):
            try:
                old = env[s.target.id] if s.target.id in env else m.value(s.target.id)
                env[s.target.id] = None if old is None else _uniq([a + b for a in old for b in self.eval(m, s.value, env)])
            except (_Unknown, TypeError):
                env[s.target.id] = None
        elif isinstance(s, ast.If):
            tv = self.truth(m, s.test, env)
            env = self.merge(*(([self.run(m, s.body, dict(env))] if True in tv else []) +
                               ([self.run(m, s.orelse, dict(env))] if False in tv else [])))
        elif isinstance(s, ast.For):
            try:
                items = self.elements(m, s.iter, env)
            except _Unknown:
                items = None
            outs = [env]
            for it in (items if items is not None else [None]):
                e2 = dict(env)
                self.bind(s.target, None if it is None else [it], e2)
                outs.append(self.run(m, s.body, e2))
            env = self.run(m, s.orelse, self.merge(*outs))
        elif isinstance(s, ast.While):
            env = self.merge(env, self.run(m, s.body, dict(env)))
        elif isinstance(s, ast.With):
            env = self.run(m, s.body, env)
        elif isinstance(s, ast.Try):
            outs = [self.run(m, s.body, dict(env))] + [self.run(m, h.body, dict(env)) for h in s.handlers]
            env = self.run(m, s.finalbody, self.run(m, s.orelse, self.merge(*outs)))
        return env

    def visit(self, m, x, env):
        """The calls in one expression: a helper call is a site; a call of a function (the script's own, or another records
        script's through a name standing for it) queues that function with the binding the call gives."""
        if isinstance(x, ast.Lambda):
            return
        if isinstance(x, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            envs = [env]
            for g in x.generators:
                nxt = []
                for e in envs:
                    self.visit(m, g.iter, e)
                    try:
                        items = self.elements(m, g.iter, e)
                    except _Unknown:
                        items = None
                    for it in (items if items is not None else [None]):
                        e2 = dict(e)
                        self.bind(g.target, None if it is None else [it], e2)
                        nxt.append(e2)
                envs = nxt[:_CAP]
            for e in envs:
                for part in ([x.key, x.value] if isinstance(x, ast.DictComp) else [x.elt]):
                    self.visit(m, part, e)
            return
        if isinstance(x, ast.Call) and self.call_site(m, x, env):
            return
        for c in ast.iter_child_nodes(x):
            if isinstance(c, ast.expr):
                self.visit(m, c, env)
            elif isinstance(c, ast.keyword):
                self.visit(m, c.value, env)

    def call_site(self, m, c, env):
        """True when c is a helper call (recorded as a site, its arguments not walked further)."""
        f = c.func
        base = m.alias(f.value.id) if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) else None
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Attribute) and f.value.attr == "PT" \
                and isinstance(f.value.value, ast.Name) and m.alias(f.value.value.id):
            base = "_lib/pdftext.py"                                   # G.PT.pdf_text: the helper another script loaded
        if isinstance(f, ast.Attribute) and f.attr == "pdf_text" and base in (None, "_lib/pdftext.py") and len(c.args) >= 4:
            self.site(m, c, env)
            return True
        if isinstance(f, ast.Name) and f.id in m.funcs:
            self.edges.add((self.cur, (m.rel, f.id)))
            self.queue(m, m.funcs[f.id], c, m, env)
        elif base and not base.startswith("_lib/") and isinstance(f, ast.Attribute):
            callee = self.mod(base)
            if f.attr in callee.funcs:
                self.edges.add((self.cur, (base, f.attr)))
                self.queue(callee, callee.funcs[f.attr], c, m, env)
        return False

    def queue(self, callee, fd, call, caller, env):
        for b in self.bindings(callee, fd, call, caller, env):
            key = (callee.rel, fd.name, repr(sorted(b.items(), key=lambda kv: kv[0])))
            if key not in self.done:
                self.done.add(key)
                self.todo.append((callee, fd, b))

    def site(self, m, c, env):
        rec = self.sites.setdefault((m.rel, c.lineno), {"table": None, "pairs": set(), "why": set()})
        self.home[(m.rel, c.lineno)] = self.cur
        t = c.args[3]
        if isinstance(t, ast.Name) and t.id == "PDFTEXT":
            rec["table"] = m.rel
        elif isinstance(t, ast.Attribute) and t.attr == "PDFTEXT" and isinstance(t.value, ast.Name) and m.alias(t.value.id):
            rec["table"] = m.alias(t.value.id)
        else:
            rec["why"].add("the table %s is not a script's PDFTEXT" % ast.unparse(t))
        try:
            pdfs, opts = self.eval(m, c.args[1], env), self.eval(m, c.args[2], env)
        except _Unknown as ex:
            rec["why"].add("unresolved: %s" % ex)
            return
        for p in pdfs:
            for o in opts:
                if isinstance(p, str) and isinstance(o, tuple):
                    rec["pairs"].add((posixpath.normpath(p), tuple(str(x) for x in o)))
                else:
                    rec["why"].add("not a path and an option list: %r %r" % (p, o))

    def walk(self, scripts):
        for rel in scripts:
            m = self.mod(rel)
            self.cur = (rel, "<module>")
            self.run(m, m.tree.body, {})
            for fd in m.funcs.values():
                if not fd.args.args and (rel, fd.name, "[]") not in self.done:
                    self.done.add((rel, fd.name, "[]"))
                    self.todo.append((m, fd, {}))
        while self.todo:
            self.steps += 1
            assert self.steps <= _STEPS, "the walk took more than %d function readings" % _STEPS
            m, fd, b = self.todo.pop()
            self.cur = (m.rel, fd.name)
            self.run(m, fd.body, dict(b))
        for rel, m in list(self.mods.items()):          # a helper call in a function no call reached is unresolved
            for fd in m.funcs.values():
                for n in ast.walk(fd):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pdf_text" \
                            and len(n.args) >= 4 and (rel, n.lineno) not in self.sites:
                        self.sites[(rel, n.lineno)] = {"table": None, "pairs": set(), "why": {"no call of %s() reaches it" % fd.name}}
        return self.sites

    def readers(self):
        """The functions that reach a site: those holding one and, transitively, those calling one of them."""
        out = {h for h in self.home.values() if h}
        grew = True
        while grew:
            grew = False
            for a, b in self.edges:
                if b in out and a and a not in out:
                    out.add(a)
                    grew = True
        return out


def _undeclared(world, PT):
    """[(site, reason)] for every site with a reason, no PDF candidate, or a candidate its table does not declare. A candidate
    that is not a .pdf is a branch the walk could not prune (l4e9's `pdf_text(key, 1, 2) if PINS[key][0].endswith(".pdf")`)."""
    bad = []
    for (rel, line), r in sorted(world.sites.items()):
        where = "%s:%d" % (rel, line)
        if r["why"]:
            bad.append((where, sorted(r["why"])))
            continue
        decl = PT.declared_in(os.path.join(world.records, r["table"])) if r["table"] not in world.sources else \
            ast.literal_eval(next(n.value for n in ast.parse(world.sources[r["table"]]).body if isinstance(n, ast.Assign)
                                  and any(getattr(t, "id", "") == "PDFTEXT" for t in n.targets)))
        pdfs = [(p, o) for p, o in sorted(r["pairs"]) if p.endswith(".pdf")]
        if not pdfs:
            bad.append((where, "no PDF reaches it"))
        for p, o in pdfs:
            if PT.tag(list(o)) not in {PT.tag(x) for x in decl.get(p, [])}:
                bad.append((where, "%s with %s is not declared in %s's PDFTEXT" % (p, " ".join(o) or "(no options)", r["table"])))
    return bad


def _outside_callers(world, listed):
    """{script: [calls]} for every records script outside `listed` that calls a reader function of a listed script through a name
    standing for it (the scripts naming a listed script's stem are parsed; the decision is by the parse)."""
    readers = world.readers()
    stems = {os.path.splitext(os.path.basename(x))[0] for x in listed}
    found = {}
    for dp, _dn, fn in os.walk(world.records):
        rd = os.path.relpath(dp, world.records).replace(os.sep, "/")
        if rd.split("/")[0] == "_lib" or "inputs" in rd.split("/"):
            continue
        for f in sorted(fn):
            rel = posixpath.normpath(posixpath.join(rd, f))
            if not f.endswith(".py") or rel in listed:
                continue
            src = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
            if not any(s in src for s in stems):
                continue
            try:
                m = _Script(world, rel)
            except SyntaxError:
                continue
            for n in ast.walk(m.tree):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name):
                    a = m.alias(n.func.value.id)
                    if a in listed and (a, n.func.attr) in readers:
                        found.setdefault(rel, []).append("%s.%s() at line %d" % (a, n.func.attr, n.lineno))
    return found


FIX_A = '''import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
PDFTEXT = {"v2/vendor/fx/one.pdf": [["-layout"]], "v2/vendor/fx/two.pdf": [["-layout", "-f", "4", "-l", "4"]]}
_S = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_S)
SHEETS = {"one": "v2/vendor/fx/one.pdf", "two": "v2/vendor/fx/two.pdf"}
def rel(p):
    return os.path.relpath(p, ROOT)
def pdftext(path):
    return PT.pdf_text(ROOT, rel(path), ["-layout"], PDFTEXT, "v2/docs/records/fa")
def page(key, n=None):
    cmd = ["-layout"]
    if n:
        cmd += ["-f", str(n), "-l", str(n)]
    return PT.pdf_text(ROOT, SHEETS[key], cmd, PDFTEXT, "v2/docs/records/fa")
def main():
    pdftext(os.path.join(ROOT, "v2", "vendor", "fx", "one.pdf"))
    for n in (4,):
        page("two", n)
'''
FIX_B = '''import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, HERE)
import a as G
def main():
    return G.pdftext(os.path.join(ROOT, "v2", "vendor", "fx", "%s.pdf"))
'''


def t_the_static_check_finds_an_undeclared_extraction_on_fixtures():
    """W55: the static check on a fixture records tree: a script whose own reads are declared passes; another script calling the
    first one's wrapper with a sheet its table lacks (l8p_c4's gap) fails, and so does a page its table lacks; a script outside the
    walked list calling that wrapper is found by the scan."""
    PT = _pt()
    d = tempfile.mkdtemp(prefix="w55-s-")
    try:
        rec = os.path.join(d, "v2", "docs", "records")
        _put(d, "v2/docs/records/fa/a.py", FIX_A.encode())
        w = _World(rec)
        w.walk(["fa/a.py"])
        assert sorted(w.sites) == [("fa/a.py", 11), ("fa/a.py", 16)], sorted(w.sites)
        assert _undeclared(w, PT) == [], _undeclared(w, PT)
        assert w.sites[("fa/a.py", 16)]["pairs"] == {("v2/vendor/fx/two.pdf", ("-layout", "-f", "4", "-l", "4"))}
        _put(d, "v2/docs/records/fa/b.py", (FIX_B % "one").encode())         # through a's wrapper, declared: passes
        w = _World(rec)
        w.walk(["fa/a.py", "fa/b.py"])
        assert _undeclared(w, PT) == [], _undeclared(w, PT)
        _put(d, "v2/docs/records/fa/b.py", (FIX_B % "three").encode())       # through a's wrapper, undeclared: l8p_c4's gap
        w = _World(rec)
        w.walk(["fa/a.py", "fa/b.py"])
        assert _undeclared(w, PT) == [("fa/a.py:11", "v2/vendor/fx/three.pdf with -layout is not declared in fa/a.py's PDFTEXT")], \
            _undeclared(w, PT)
        w = _World(rec)
        w.walk(["fa/a.py"])
        assert _outside_callers(w, ["fa/a.py"]) == {"fa/b.py": ["fa/a.py.pdftext() at line 7"]}, _outside_callers(w, ["fa/a.py"])
        os.remove(os.path.join(rec, "fa", "b.py"))
        w = _World(rec, {"fa/a.py": FIX_A.replace('page("two", n)', 'page("two", n + 1)')})
        w.walk(["fa/a.py"])                                                    # page 5 asked, page 4 declared
        assert _undeclared(w, PT) == [("fa/a.py:16", "v2/vendor/fx/two.pdf with -layout -f 5 -l 5 is not declared in fa/a.py's "
                                                     "PDFTEXT")], _undeclared(w, PT)
        w = _World(rec, {"fa/a.py": FIX_A.replace('page("two", n)', 'page("two", UNBOUND)')})
        w.walk(["fa/a.py"])                                                    # an argument the walk cannot read: unresolved
        assert [b[0] for b in _undeclared(w, PT)] == ["fa/a.py:16"], _undeclared(w, PT)
    finally:
        shutil.rmtree(d)


def t_every_extraction_site_the_converted_generators_reach_is_declared():
    """W55 (W53's finding): every helper call the converted generators and READERS reach, its PDF and options resolved statically,
    is declared in the PDFTEXT table it names; every helper call of theirs is reached; no records script outside the two lists calls
    a reader function of theirs; each READER still reaches one and runs neither tool itself."""
    need(HELPER, "the helper")
    PT = _pt()
    rec = os.path.join(ROOT, "v2", "docs", "records")
    listed = list(CONVERTED) + list(READERS)
    for rel in READERS:
        tree = ast.parse(open(need(os.path.join(rec, rel), "a reader"), encoding="utf-8").read())
        assert not _pdftotext_calls(tree) and not _tool_calls(tree, "pdftocairo"), "%s runs pdftotext or pdftocairo" % rel
    w = _World(rec)
    sites = w.walk(listed)
    bad = _undeclared(w, PT)
    assert not bad, "extraction sites not declared in the table they name (%d): %s" % (len(bad), bad[:6])
    holding = {r for (r, _l) in sites}
    assert set(CONVERTED) <= holding, "converted generators holding no extraction site: %s" % sorted(set(CONVERTED) - holding)
    assert len(sites) >= 37, "%d sites read (37 on 6 October 2026)" % len(sites)
    out = _outside_callers(w, listed)
    assert not out, "records scripts that reach a converted generator's reader and are in neither list: %s" % out
    readers = w.readers()
    for rel in READERS:
        assert any(r == rel for r, _f in readers), "%s no longer reaches a reader (drop it from READERS)" % rel


def t_the_static_check_catches_the_l8p_c4_gap_at_its_base():
    """W55: the mutation. With fnd/w34pdftext's l8p_c4.py before W55 (it read the BZT52C sheet through l8p_guard.pdftext()), the
    check names that site as undeclared in l8p_guard's table, as the run refused it (W53)."""
    PT = _pt()
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/docs/records/l8p/l8p_c4.py" % GAP_BASE], capture_output=True)
    if r.returncode != 0:
        raise Skip("the commit %s is not in this checkout" % GAP_BASE)
    w = _World(os.path.join(ROOT, "v2", "docs", "records"), {"l8p/l8p_c4.py": r.stdout.decode("utf-8")})
    w.walk(list(CONVERTED) + list(READERS))
    bad = _undeclared(w, PT)
    assert ("l8p/l8p_guard.py:102", "v2/vendor/diodes/diodes-bzt52c-ds18004.pdf with -layout is not declared in "
            "l8p/l8p_guard.py's PDFTEXT") in bad, bad
    assert len(bad) == 1, bad


def t_every_pdftext_declaration_has_its_text():
    """W55: every extraction any PDFTEXT table under v2/docs/records declares (not only the converted generators' folders) has its
    text and sidecar beside the PDF, taken from the PDF present: committed for a committed sheet; for a held-back sheet when the
    sheet is installed on this host (its text is ignored by .gitignore, as the sheet is)."""
    need(RETAKE, "the re-take script")
    PT = _pt()
    RT = _load("t_pdftext_retake_w55", RETAKE)
    rec_root = os.path.join(ROOT, "v2", "docs", "records")
    tracked = None
    r = subprocess.run(["git", "-C", ROOT, "ls-files", "v2/vendor"], capture_output=True, text=True)
    if r.returncode == 0:
        tracked = set(r.stdout.splitlines())
    seen = held_absent = 0
    for x in sorted(os.listdir(rec_root)):
        rd = os.path.join(rec_root, x)
        if not os.path.isdir(rd) or not any(n.endswith(".py") for n in os.listdir(rd)):
            continue
        for pdf, opts in sorted(RT.tables(rd).items()):
            if not os.path.isfile(os.path.join(ROOT, pdf)):
                assert PT.held(pdf), "%s (declared in %s) is a committed sheet and is absent" % (pdf, x)
                held_absent += 1
                continue
            for o in opts:
                t = PT.text_path(pdf, o)
                assert os.path.isfile(os.path.join(ROOT, t)) and os.path.isfile(os.path.join(ROOT, PT.meta_path(t))), \
                    "%s, declared in %s, is absent: %s" % (t, x, PT.retake_command("v2/docs/records/" + x))
                m = json.load(open(os.path.join(ROOT, PT.meta_path(t)), encoding="utf-8"))
                assert m["pdf_sha256"] == _sha(open(os.path.join(ROOT, pdf), "rb").read()), "%s is not from the present %s" % (t, pdf)
                if tracked is not None:
                    assert (t in tracked) == (not PT.held(pdf)), "%s: committed %s, held back %s" % (t, t in tracked, PT.held(pdf))
                seen += 1
    assert seen, "no declaration checked"


def t_l8p_c4_runs_with_pdftotext_and_pdftocairo_refused():
    """W55: the generator W53 saw refuse, run with both tools refusing first on PATH: exit 0, no call, its three text lines
    printed, its record folder unchanged (the output into a temporary file, never l8p_c4.out)."""
    rel = "l8p/l8p_c4.py"
    need(os.path.join(ROOT, "v2", "docs", "records", rel), "l8p_c4.py")
    why = _held_ready(rel)
    if why:
        raise Skip("%s: %s" % (rel, why))
    d = tempfile.mkdtemp(prefix="w55-r-")
    try:
        env, log = _tools_bin(d)
        before = _status(rel)
        rc, out, err = _run_generator(rel, env, d)
        assert rc == 0, "%s exited %d with both tools refused: %s" % (rel, rc, err.strip()[-400:])
        assert _calls(log) == [], "%s called %s" % (rel, _calls(log))
        assert not _text_lines_printed(rel, out) and len(_declared_inputs(rel)) == 3, "%s does not print its three text lines" % rel
        assert _status(rel) == before, "%s changed its record folder" % rel
    finally:
        shutil.rmtree(d)


def _declared_inputs(rel):
    PT = _pt()
    return PT.inputs(ROOT, PT.declared_in(os.path.join(ROOT, "v2", "docs", "records", rel)))


# ----------------------------------------------------------------------- W81: the test modules' extraction routes, read statically
# W66's full dry run of set 32 (6 October 2026, `_runs/int32/README.md` 9b) stopped on a TEST: test_l8p.py:665 read TDK's held sheet
# through l8p_drafts.pdftext(), whose table did not declare it, and the helper refused (exit 2). W55's check above walked the generators
# and their readers, never the tests. The check below walks the test modules too, as callers: a test's name standing for a records
# script (its own loader: a function holding spec_from_file_location, read with the call's arguments, or a function returning such a
# function's result) carries the test's arguments into the records script's wrappers, so each site records the pairs a test asks for
# and the test line that asked. A test calling the helper itself names its table (a script's PDFTEXT, or PT.declared_in(<script>)).
# Beside it, a census of the other extraction routes a test module holds: a process call of pdftotext or pdftocairo in its own code,
# and a call of a function of a v2/ecad/tools module or of a records script that runs one; each must be a KNOWN route with its reason.
TPFX = "@tests/"
PROC = ("subprocess.run", "subprocess.call", "subprocess.check_call", "subprocess.check_output", "subprocess.Popen", "os.system",
        "os.popen")
TOOLS_RUN = ("pdftotext", "pdftocairo")
# the test modules' own process calls of a tool, each module with its count and reason (W81's census of 6 October 2026, after W81
# moved test_l3r5's, test_l5r4's and test_l8r2's reads to committed extractions)
KNOWN_DIRECT = {
    "test_pdftext_input.py": (3, "the helper's and the re-take's own fixtures: the control call proving the fake pdftotext is first on "
                                 "PATH, and the fixture PDF read back against the re-take's text in a temporary directory (W34)"),
    "test_energy_chain.py": (1, "TOOL LAYER: energy_chain.py's transcription guard re-reads the ATOF table of v2/vendor/battery/"
                                "littelfuse-287-atof.pdf (-layout); v2/ecad/tools has no PDFTEXT table and the records' helper is not its "
                                "reader; it moves with the tools layer's own conversion (KNOWN_TOOLVIA)"),
    "test_rails_census.py": (1, "TOOL LAYER: the rails census reads intent_checks.PIN_ROLES' documents (-layout), as edge_length.py and "
                                "pack_protection.py read theirs; it moves with the tools layer's own conversion"),
    "test_l3r5.py": (1, "LAYER 3 AMENDMENT, BOUND: test_l3r5.py is a file of l3amlib.AMENDMENT_FILES, which "
                        "apply_l3am_findings_closed.py verifies byte for byte at the amendment's reviewed revision 8146b4cc (test_l3am); "
                        "its read of the two committed Samsung 35E sheets (v2/vendor/battery/samsung-35e-orbtronic.pdf and "
                        "samsung-35e-akkuzentrum.pdf, -layout, a skip without pdftotext) stays as reviewed: W81's move of it to l4e10's "
                        "declared texts (877d81c5) returned by W114 under the coordinator's ruling of 7 October 2026 on W110's N3; it "
                        "moves only with a new independent check of the amendment"),
}
# test modules calling a v2/ecad/tools module's function that runs a tool itself (the tools layer: outside W34's conversion of the
# records, PDFTEXT-INVENTORY.md section 1 covers v2/docs/records only)
KNOWN_TOOLVIA = {
    ("test_edge_length.py", "edge_length.py"): "TOOL LAYER: edge_length's held documents' words (pdftotext -layout, one page or all)",
    ("test_l6pwr.py", "part_identities.py"): "TOOL LAYER: part_identities' bound document page (pdftotext -f N -l N -layout), "
                                              "the inventory's DRY-RUN class for l6pwr_parts.py",
    ("test_l6r2.py", "part_identities.py"): "TOOL LAYER: part_identities' bound document page, the inventory's DRY-RUN class for "
                                             "l6r2_passives.py",
    ("test_part_identities.py", "part_identities.py"): "TOOL LAYER: part_identities' own tests, on fixture PDFs written in a temporary "
                                                       "directory and on the bound documents",
    ("test_pack_protection.py", "pack_protection.py"): "TOOL LAYER: pack_protection's judge reads the pack's held documents (-layout)",
}

# test modules calling a records function that runs a tool itself, beyond l4e9's and l4e11's pinned pdftocairo sites (PDFTOCAIRO_SITES)
KNOWN_RECVIA = {
    ("test_l4e7.py", "l4e7/l4e7_stage_settings.py"): "the l4e7 KEY group, not converted by design (PDFTEXT-INVENTORY.md: its KEY "
                                                      "records the host's pdftotext); the test reads results() in-process",
    ("test_l4e7_cachekey.py", "l4e7/l4e7_stage_settings.py"): "the l4e7 KEY group, not converted by design (PDFTEXT-INVENTORY.md: "
                                                               "its KEY records the host's pdftotext); set 32's test_l4e7_cachekey.py "
                                                               "(fnd/l4e7cache) calls main() in-process on scratch trees, never the "
                                                               "solver (W100's B4; inserted at chain.sh a6 by hook_a6.sh, W104)",
}


class _TestWorld(_World):
    """_World with the test modules as callers (`@tests/<name>` scripts, read from the tests folder; never imported or run)."""

    def __init__(self, records, tests, sources=None):
        super().__init__(records, sources)
        self.tests, self.origin, self.origin_of, self.calls, self._quiet, self._refs = tests, None, {}, [], 0, {}
        for n in sorted(os.listdir(tests)):
            if n.startswith("test_") and n.endswith(".py") and TPFX + n not in self.sources:
                self.sources[TPFX + n] = open(os.path.join(tests, n), encoding="utf-8").read()

    def test_scripts(self):
        return sorted(k for k in self.sources if k.startswith(TPFX))

    def mod(self, rel):
        new = rel not in self.mods
        m = super().mod(rel)
        if new and rel.startswith(TPFX):
            m.alias = lambda name: None          # a test's names are read by refs(), per function, never module-wide
        return m

    def is_test(self, m):
        return m.rel.startswith(TPFX)

    def _fn(self, m):
        return self.cur[1] if self.cur and self.cur[0] == m.rel and self.cur[1] in m.funcs else None

    def _assigned(self, m, name, fn):
        """The calls a name is assigned from in the function being read, else at the module's level."""
        calls = []
        if fn:
            calls = [a.value for a in ast.walk(m.funcs[fn]) if isinstance(a, ast.Assign) and isinstance(a.value, ast.Call)
                     and any(isinstance(t, ast.Name) and t.id == name for t in a.targets)]
        return calls or [v for v in m.assigns.get(name, []) if isinstance(v, ast.Call)]

    def eval(self, m, e, env, depth=0):
        if self.is_test(m):
            if isinstance(e, ast.Name) and e.id == "__file__" and e.id not in env:
                return ["v2/ecad/tools/tests/" + m.rel[len(TPFX):]]
            if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id == "need" and e.args:
                return self.eval(m, e.args[0], env, depth + 1)            # harness.need returns the path it checked
            if isinstance(e, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                return self._comprehension(m, e, env, depth)
            if isinstance(e, ast.Attribute) and isinstance(e.value, ast.Name) and env.get(e.value.id) is None:
                refs = [r for r in self.refs(m, e.value.id) if not r.startswith("_lib/")]
                if refs:
                    return _uniq([v for r in refs for v in self.mod(r).value(e.attr)])
        return super().eval(m, e, env, depth)

    def _comprehension(self, m, e, env, depth):
        """A test's comprehension as one value (a dict, or a tuple for the others), each element read per binding of its loops; a
        filter is not read, so the value holds every element a filter could keep (HELD_FAN, test_l8r2's pages, is one)."""
        envs = [dict(env)]
        for g in e.generators:
            nxt = []
            for en in envs:
                for it in self.elements(m, g.iter, en):
                    e2 = dict(en)
                    self.bind(g.target, [it], e2)
                    nxt.append(e2)
            envs = nxt[:_CAP]
        out = {} if isinstance(e, ast.DictComp) else []
        for en in envs:
            parts = [e.key, e.value] if isinstance(e, ast.DictComp) else [e.elt]
            vals = [self.eval(m, x, en, depth + 1) for x in parts]
            if any(len(v) != 1 for v in vals):
                raise _Unknown("a comprehension element of several values")
            if isinstance(e, ast.DictComp):
                out[vals[0][0]] = vals[1][0]
            else:
                out.append(vals[0][0])
        return [out if isinstance(e, ast.DictComp) else tuple(out)]

    def refs(self, m, name):
        """The records scripts a test's name stands for in the function being read."""
        fn = self._fn(m)
        key = (m.rel, fn, name)
        if key not in self._refs:
            self._refs[key] = ()
            out = set()
            for c in self._assigned(m, name, fn):
                out |= self.loaded(m, c, {}, 0, fn)
            self._refs[key] = tuple(sorted(out))
        return self._refs[key]

    def _spec_paths(self, m, s, env):
        try:
            vals = self.eval(m, s.args[1], env)
        except _Unknown:
            return set()
        out = set()
        for v in vals:
            q = posixpath.normpath(v) if isinstance(v, str) else ""
            if q.startswith("v2/docs/records/") and q.endswith(".py"):
                out.add(q[len("v2/docs/records/"):])
        return out

    def loaded(self, m, call, env, depth, fn=None):
        """The records scripts a test's loader call loads: spec_from_file_location's path under the call's binding, through a function
        returning another loader's result, or importlib.util.module_from_spec(<a spec assigned in the same function>)."""
        out = set()
        if depth > 6:
            return out
        if getattr(call.func, "attr", "") == "module_from_spec" and call.args and isinstance(call.args[0], ast.Name):
            for s in self._assigned(m, call.args[0].id, fn):
                if getattr(s.func, "attr", "") == "spec_from_file_location" and len(s.args) > 1:
                    out |= self._spec_paths(m, s, {})
            return out
        if not (isinstance(call.func, ast.Name) and call.func.id in m.funcs):
            return out
        fd = m.funcs[call.func.id]
        for b in self.bindings(m, fd, call, m, env):
            self._quiet += 1
            try:
                env2 = self.run(m, fd.body, dict(b))
            finally:
                self._quiet -= 1
            specs = [s for s in ast.walk(fd) if isinstance(s, ast.Call) and getattr(s.func, "attr", "") == "spec_from_file_location"
                     and len(s.args) > 1]
            for s in specs:
                out |= self._spec_paths(m, s, env2)
            if specs:
                continue
            for r in ast.walk(fd):
                if isinstance(r, ast.Return) and isinstance(r.value, ast.Call):
                    out |= self.loaded(m, r.value, env2, depth + 1, fd.name)
                elif isinstance(r, ast.Return) and isinstance(r.value, ast.Name):
                    for a in self._assigned(m, r.value.id, fd.name):
                        out |= self.loaded(m, a, env2, depth + 1, fd.name)
        return out

    def visit(self, m, x, env):
        if not self._quiet:
            super().visit(m, x, env)

    def call_site(self, m, c, env):
        f = c.func
        if self.is_test(m) and isinstance(f, ast.Attribute):
            recv = f.value
            if isinstance(recv, ast.Attribute) and recv.attr == "PT" and isinstance(recv.value, ast.Name) and \
                    self.refs(m, recv.value.id) and f.attr == "pdf_text" and len(c.args) >= 4:
                self.site(m, c, env)                                         # m.PT.pdf_text(...): the helper a records script loaded
                return True
            if isinstance(recv, ast.Name) and env.get(recv.id) is None and self.refs(m, recv.id):
                for r in self.refs(m, recv.id):
                    if r == "_lib/pdftext.py":
                        if f.attr == "pdf_text" and len(c.args) >= 4:
                            self.site(m, c, env)                              # PT.pdf_text(...) with the helper the test loaded
                            return True
                        continue
                    callee = self.mod(r)
                    if f.attr in callee.funcs:
                        self.calls.append((m.rel, c.lineno, r, f.attr))
                        self.edges.add((self.cur, (r, f.attr)))
                        self.queue(callee, callee.funcs[f.attr], c, m, env)
                return False
        return super().call_site(m, c, env)

    def _key(self, callee, fd, b):
        return (callee.rel, fd.name, repr(sorted(b.items(), key=lambda kv: kv[0])))

    def queue(self, callee, fd, call, caller, env):
        org = self.origin or ((caller.rel, call.lineno) if self.is_test(caller) else None)
        if org:
            for b in self.bindings(callee, fd, call, caller, env):
                self.origin_of.setdefault(self._key(callee, fd, b), org)
        super().queue(callee, fd, call, caller, env)

    def _table(self, m, t, depth=0):
        """The records script whose PDFTEXT a helper call's table argument is: PDFTEXT, X.PDFTEXT, PT.declared_in(<script>), or a
        name assigned from one of those in the function being read."""
        if depth > 3:
            return None
        if isinstance(t, ast.Name) and t.id == "PDFTEXT" and not self.is_test(m):
            return m.rel
        if isinstance(t, ast.Attribute) and t.attr == "PDFTEXT" and isinstance(t.value, ast.Name):
            r = self.refs(m, t.value.id) if self.is_test(m) else ((m.alias(t.value.id),) if m.alias(t.value.id) else ())
            return r[0] if len(r) == 1 else None
        if isinstance(t, ast.Call) and getattr(t.func, "attr", "") == "declared_in" and len(t.args) == 1:
            r = self._spec_paths(m, ast.Call(func=t.func, args=[t.args[0], t.args[0]], keywords=[]), {})
            return next(iter(r)) if len(r) == 1 else None
        if isinstance(t, ast.Name):
            vals = self._assigned(m, t.id, self._fn(m))
            return self._table(m, vals[0], depth + 1) if len(vals) == 1 else None
        return None

    def site(self, m, c, env):
        key = (m.rel, c.lineno)
        rec = self.sites.setdefault(key, {"table": None, "pairs": set(), "why": set()})
        rec.setdefault("from", {})
        self.home[key] = self.cur
        tab = self._table(m, c.args[3])
        if tab:
            rec["table"] = tab
        else:
            rec["why"].add("the table %s is not a script's PDFTEXT" % ast.unparse(c.args[3]))
        try:
            pdfs, opts = self.eval(m, c.args[1], env), self.eval(m, c.args[2], env)
        except _Unknown as ex:
            rec["why"].add("unresolved: %s" % ex)
            return
        org = self.origin or (key if self.is_test(m) else None)
        for p in pdfs:
            for o in opts:
                if isinstance(p, str) and isinstance(o, tuple):
                    pair = (posixpath.normpath(p), tuple(str(x) for x in o))
                    rec["pairs"].add(pair)
                    if org:
                        rec["from"].setdefault(pair, set()).add(org)
                else:
                    rec["why"].add("not a path and an option list: %r %r" % (p, o))

    def walk(self, scripts):
        """_World.walk with each reading's origin carried (the test line whose call queued it, through every call after it), then
        every helper call in a test module that no walk reached (a nested function, an unread call) recorded as unresolved."""
        for rel in scripts:
            m = self.mod(rel)
            self.cur, self.origin = (rel, "<module>"), None
            self.run(m, m.tree.body, {})
            for fd in m.funcs.values():
                if not fd.args.args and (rel, fd.name, "[]") not in self.done:
                    self.done.add((rel, fd.name, "[]"))
                    self.todo.append((m, fd, {}))
        while self.todo:
            self.steps += 1
            assert self.steps <= 4 * _STEPS, "the walk took more than %d function readings" % (4 * _STEPS)
            m, fd, b = self.todo.pop()
            self.cur, self.origin = (m.rel, fd.name), self.origin_of.get(self._key(m, fd, b))
            self.run(m, fd.body, dict(b))
        for rel, m in list(self.mods.items()):
            nodes = ast.walk(m.tree) if self.is_test(m) else (n for fd in m.funcs.values() for n in ast.walk(fd))
            for n in nodes:
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pdf_text" \
                        and len(n.args) >= 4 and (rel, n.lineno) not in self.sites:
                    self.sites[(rel, n.lineno)] = {"table": None, "pairs": set(), "why": {"no walk reaches this helper call"}}
        return self.sites


def _undeclared_with_origin(world, PT):
    """_undeclared's findings, each with the test lines whose calls asked for the undeclared pair (empty for a generator's own)."""
    out = []
    for where, why in _undeclared(world, PT):
        rel, line = where.rsplit(":", 1)
        r = world.sites[(rel, int(line))]
        fr = r.get("from", {})
        org = set()
        for pair, o in fr.items():
            if why == "%s with %s is not declared in %s's PDFTEXT" % (pair[0], " ".join(pair[1]) or "(no options)", r["table"]):
                org |= o
        if not isinstance(why, str) or why == "no PDF reaches it":
            org = set().union(*fr.values()) if fr else set()
        out.append((where, why, sorted("%s:%d" % (r[len(TPFX):] if r.startswith(TPFX) else r, l) for r, l in org)))
    return out


def _proc_tool_lines(tree):
    """{line: tool} for each process call (subprocess.*, os.system, os.popen) whose command names pdftotext or pdftocairo: an argument
    list's first element, a shell string, or a list kept in a variable. Parsed; shutil.which's argument and a message are not commands."""
    def tool_of(node):
        for n in ast.walk(node):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                for t in TOKEN.split(n.value):
                    if t and os.path.basename(t) in TOOLS_RUN:
                        return os.path.basename(t)
        return None
    named = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.List, ast.Tuple)):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    named.setdefault(t.id, []).append(n.value)
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and ast.unparse(n.func) in PROC and n.args:
            a = n.args[0]
            t = tool_of(a.elts[0] if isinstance(a, (ast.List, ast.Tuple)) and a.elts and not isinstance(a.elts[0], ast.Starred) else a)
            for x in ([] if t else [x for x in ast.walk(a) if isinstance(x, ast.Name)]):     # a list kept in a variable
                t = next((tool_of(v.elts[0]) for v in named.get(x.id, []) if v.elts and tool_of(v.elts[0])), None)
                if t:
                    break
            if t:
                out[n.lineno] = t
    return out


def _tool_functions(src):
    """{function: tools} of one module: the functions that run pdftotext or pdftocairo, directly or through another of its functions."""
    funcs = {n.name: n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}
    runs = {f: set(_proc_tool_lines(fd).values()) for f, fd in funcs.items()}
    runs = {f: t for f, t in runs.items() if t}
    grew = True
    while grew:
        grew = False
        for f, fd in funcs.items():
            got = set().union(*[runs[c.func.id] for c in ast.walk(fd) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                                and c.func.id in runs and c.func.id != f] or [set()])
            if got - runs.get(f, set()):
                runs[f] = runs.get(f, set()) | got
                grew = True
    return runs


def _test_routes(tests_dir, tools_dir, world=None):
    """The census: {"direct": {module: [(line, tool)]}, "toolvia": {(module, tools module): [(line, function, tools)]}, "recvia":
    [(module, line, records script, function, tools)]} (recvia from a walked _TestWorld's calls)."""
    out = {"direct": {}, "toolvia": {}, "recvia": []}
    for n in sorted(os.listdir(tests_dir)):
        if not (n.startswith("test_") and n.endswith(".py")):
            continue
        tree = ast.parse(open(os.path.join(tests_dir, n), encoding="utf-8").read())
        d = sorted(_proc_tool_lines(tree).items())
        if d:
            out["direct"][n] = d
        imps = {}
        for x in ast.walk(tree):
            if isinstance(x, ast.Import):
                for a in x.names:
                    if os.path.isfile(os.path.join(tools_dir, a.name + ".py")):
                        imps[a.asname or a.name] = a.name + ".py"
        tf = {k: _tool_functions(open(os.path.join(tools_dir, v), encoding="utf-8").read()) for k, v in imps.items()}
        for c in ast.walk(tree):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) \
                    and c.func.value.id in tf and c.func.attr in tf[c.func.value.id]:
                out["toolvia"].setdefault((n, imps[c.func.value.id]), []).append(
                    (c.lineno, c.func.attr, tuple(sorted(tf[c.func.value.id][c.func.attr]))))
    if world is not None:
        tf = {}
        for tm, line, r, f in sorted(set(world.calls)):
            if r not in tf:
                tf[r] = _tool_functions(open(os.path.join(world.records, r), encoding="utf-8").read()) \
                    if r not in world.sources else _tool_functions(world.sources[r])
            if f in tf[r]:
                out["recvia"].append((tm[len(TPFX):], line, r, f, tuple(sorted(tf[r][f]))))
    return out


FIX_T = '''import importlib.util, os, subprocess, shutil, sys
TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "fa")
sys.path.insert(0, TESTS)
from harness import need, Skip
_C = {}
def _mod(name, fname):
    if name not in _C:
        p = need(os.path.join(REC, fname), "a fixture record's script")
        sp = importlib.util.spec_from_file_location(name, p)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _C[name] = m
    return _C[name]
def _M():
    return _mod("a_under_test", "a.py")
def t_reads_through_the_records_wrapper():
    m = _M()
    t = m.pdftext(os.path.join(ROOT, "v2", "vendor", "fx", "%s.pdf"))
def t_reads_through_the_helper():
    sp = importlib.util.spec_from_file_location("fx_pt", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
    PT = importlib.util.module_from_spec(sp)
    table = PT.declared_in(os.path.join(ROOT, "v2", "docs", "records", "fa", "a.py"))
    t = PT.pdf_text(ROOT, "v2/vendor/fx/two.pdf", %s, table, "v2/docs/records/fa")
def t_the_host_tool():
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is needed")
    CMD = ["pdftotext", "-layout"]
    a = subprocess.run(["pdftotext", "-layout", "x.pdf", "-"], capture_output=True)
    b = subprocess.run("cd /tmp && /usr/bin/pdftotext x.pdf -", shell=True)
    c = subprocess.run(CMD + ["x.pdf", "-"])
'''


def _fixture_tests(d, sheet="one", opts='["-layout", "-f", "4", "-l", "4"]'):
    rec = os.path.join(d, "v2", "docs", "records")
    _put(d, "v2/docs/records/fa/a.py", FIX_A.encode())
    _put(d, "v2/ecad/tools/tests/test_fx.py", (FIX_T % (sheet, opts)).encode())
    return rec, os.path.join(d, "v2", "ecad", "tools", "tests")


def t_the_test_side_check_finds_an_undeclared_read_on_fixtures():
    """W81 (W66's finding): a fixture test module reading through a records script's wrapper and through the helper with a table named
    by PT.declared_in(): declared reads pass; an undeclared sheet through the wrapper (test_l8p.py:665's gap) and an undeclared mode
    through the helper fail, each naming the site and the test line that asked; the census finds the three process calls of
    pdftotext (an argument list, a shell string, a list kept in a variable) and not shutil.which's argument or the Skip message."""
    PT = _pt()
    d = tempfile.mkdtemp(prefix="w81-t-")
    try:
        rec, tests = _fixture_tests(d)
        w = _TestWorld(rec, tests)
        w.walk(["fa/a.py"] + w.test_scripts())
        assert _undeclared_with_origin(w, PT) == [], _undeclared_with_origin(w, PT)
        assert ("@tests/test_fx.py", 20, "fa/a.py", "pdftext") in w.calls, w.calls
        assert w.sites[("@tests/test_fx.py", 25)]["table"] == "fa/a.py"
        rec, tests = _fixture_tests(d, "three", '["-layout"]')
        w = _TestWorld(rec, tests)
        w.walk(["fa/a.py"] + w.test_scripts())
        got = _undeclared_with_origin(w, PT)
        assert got == [("@tests/test_fx.py:25", "v2/vendor/fx/two.pdf with -layout is not declared in fa/a.py's PDFTEXT",
                        ["test_fx.py:25"]),
                       ("fa/a.py:11", "v2/vendor/fx/three.pdf with -layout is not declared in fa/a.py's PDFTEXT", ["test_fx.py:20"])], got
        w = _World(rec)                                   # W55's walk alone does not see the test's reads: the gap W66 met
        w.walk(["fa/a.py"])
        assert _undeclared(w, PT) == [], _undeclared(w, PT)
        r = _test_routes(tests, os.path.join(d, "v2", "ecad", "tools"))
        assert r["direct"] == {"test_fx.py": [(30, "pdftotext"), (31, "pdftotext"), (32, "pdftotext")]}, r["direct"]
    finally:
        shutil.rmtree(d)


_TREE = {}


def _tree_world():
    """One walk of this tree's converted generators, READERS and test modules, shared by (o) and (p) (about 15 s on the runner)."""
    if "w" not in _TREE:
        w = _TestWorld(os.path.join(ROOT, "v2", "docs", "records"), TESTS)
        w.walk(list(CONVERTED) + list(READERS) + w.test_scripts())
        _TREE["w"] = w
    return _TREE["w"]


def t_every_extraction_a_test_reaches_is_declared():
    """W81: the converted generators, the READERS and every test module walked together: every pair a test asks for (through a
    records script's wrapper, its PT or the helper with a named table) is declared in the table its site names, and no helper call
    in a test is unreached; test_l8r2 reads its four San Ace pages through l8r2_pdftext.py's table. The mutation: without
    l8p_pdftext.py's TDK line the check names test_l8p's read of TDK's held sheet (W66's refusal at test_l8p.py:665)."""
    need(HELPER, "the helper")
    PT = _pt()
    rec = os.path.join(ROOT, "v2", "docs", "records")
    w = _tree_world()
    bad = _undeclared_with_origin(w, PT)
    assert not bad, "extraction sites a test reaches that their table does not declare (%d): %s" % (len(bad), bad[:6])
    readers = w.readers()
    asked = {(tm, line) for tm, line, r, f in w.calls if (r, f) in readers}
    assert len(asked) >= 50, "%d test calls of a reader function (54 on 6 October 2026)" % len(asked)
    # 40 since 7 October 2026 (W114, W110's N3): test_l3r5's read went back to its reviewed direct pdftotext call (KNOWN_DIRECT)
    assert len(w.sites) >= 40, "%d sites read (41 on 6 October 2026: section 8's 37 and the four test-side reads; 40 since test_l3r5's " \
                               "read returned to its reviewed direct call, W114)" % len(w.sites)
    fan = {pair for (r, _l), rec_ in w.sites.items() if r == TPFX + "test_l8r2.py" and rec_["table"] == "l8r2/l8r2_pdftext.py"
           for pair in rec_["pairs"] if "/held/sanyo-denki-san-ace-" in pair[0]}
    assert len(fan) == 4, "test_l8r2's four San Ace pages are not read through l8r2_pdftext.py's table: %s" % sorted(fan)
    tdk = "v2/vendor/battery/held/tdk-ptc-limit-sensors-smd-superior-2019-08.pdf"
    src = open(os.path.join(rec, "l8p", "l8p_pdftext.py"), encoding="utf-8").read()
    line = '    "%s": [["-layout"]],\n' % tdk
    assert src.count(line) == 1, "l8p_pdftext.py's TDK declaration is not one line as this test expects"
    w2 = _TestWorld(rec, TESTS, {"l8p/l8p_pdftext.py": src.replace(line, "")})
    w2.walk(list(CONVERTED) + list(READERS) + w2.test_scripts())
    got = _undeclared_with_origin(w2, PT)
    assert len(got) == 1 and got[0][0].startswith("@tests/test_l8p.py:") and got[0][1] == \
        "%s with -layout is not declared in l8p/l8p_pdftext.py's PDFTEXT" % tdk and got[0][2] == [got[0][0][len(TPFX):]], got


def t_every_other_extraction_route_of_a_test_module_is_known():
    """W81: the census of the test modules' other routes: their own process calls of pdftotext or pdftocairo are KNOWN_DIRECT (by
    module, with the count and the reason); their calls of a v2/ecad/tools function that runs one are KNOWN_TOOLVIA; their calls of a
    records function that runs one reach only the pinned pdftocairo sites of l4e9 and l4e11 (no pdftotext: W37's predicate (d)) or
    are KNOWN_RECVIA (the l4e7 KEY group)."""
    need(HELPER, "the helper")
    r = _test_routes(TESTS, TOOLS, _tree_world())
    direct = {n: len(v) for n, v in r["direct"].items()}
    want = {n: c for n, (c, _why) in KNOWN_DIRECT.items()}
    assert direct == want, "test modules' own tool calls differ from KNOWN_DIRECT: %s against %s (%s)" % (
        direct, want, {n: v for n, v in r["direct"].items() if direct.get(n) != want.get(n)})
    assert all(t == "pdftotext" for v in r["direct"].values() for _l, t in v), r["direct"]
    assert set(r["toolvia"]) == set(KNOWN_TOOLVIA), "tools-layer routes differ: new %s, gone %s" % (
        sorted(set(r["toolvia"]) - set(KNOWN_TOOLVIA)), sorted(set(KNOWN_TOOLVIA) - set(r["toolvia"])))
    seen = set()
    for tm, line, script, f, tools in r["recvia"]:
        if (tm, script) in KNOWN_RECVIA:
            seen.add((tm, script))
            continue
        assert tools == ("pdftocairo",) and script in PDFTOCAIRO_SITES, \
            "%s:%d calls %s.%s(), which runs %s" % (tm, line, script, f, "/".join(tools))
    assert seen == set(KNOWN_RECVIA), "KNOWN_RECVIA entries no test reaches any more: %s" % sorted(set(KNOWN_RECVIA) - seen)
