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
    that fetches THAT sheet, re-derived from the fetch scripts' own document lists, and the refusal names it."""
import ast
import hashlib
import importlib.util
import json
import os
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
