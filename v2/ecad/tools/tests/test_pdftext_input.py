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
    a converted record declares is present and current for every PDF present in this tree."""
import ast
import hashlib
import importlib.util
import json
import os
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

# the generators converted by W34; each record directory's PDFTEXT tables are what the re-take reads
CONVERTED = ("efuse/efuse_check.py", "l5r2/l5r2_interfaces.py", "l8r2/l8r2_drafts.py", "l8r2/l8r2_gndret.py", "l8r2/l8r2_p0.py",
             "l4e13/l4e13_panel.py", "l4e11/l4e11_power.py", "l4e9/l4e9_power_path.py")
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
t = PT.pdf_text(sys.argv[2], sys.argv[3], sys.argv[4].split(), decl, "v2/docs/records/fix")
sys.stdout.buffer.write(t.encode("utf-8"))
"""


def _read(d, env, pdf_rel=PDF, options="-layout"):
    return subprocess.run([sys.executable, "-B", "-c", READER, HELPER, d, pdf_rel, options], capture_output=True, env=env, timeout=60)


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
        assert "fetch_held_back.py" in err and "retake_pdf_text.py" in err, err
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


def _pdftotext_calls(tree):
    """Calls that run pdftotext: an argument list whose first element is "pdftotext", or a string starting with it (os.popen)."""
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.List, ast.Tuple)) and node.elts and isinstance(node.elts[0], ast.Constant) \
                and node.elts[0].value == "pdftotext":
            hits.append(node.lineno)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("popen", "system"):
            for s in ast.walk(node):
                if isinstance(s, ast.Constant) and isinstance(s.value, str) and s.value.lstrip().startswith("pdftotext"):
                    hits.append(node.lineno)
    return hits


def t_no_converted_generator_runs_pdftotext():
    assert _pdftotext_calls(ast.parse("import subprocess\nsubprocess.run(['pdftotext', '-layout', p, '-'])\n")) == [2]
    assert _pdftotext_calls(ast.parse("import os\nos.popen('pdftotext -layout %s -' % p)\n")) == [2]
    for rel in CONVERTED:
        p = need(os.path.join(ROOT, "v2", "docs", "records", rel), "a converted generator")
        tree = ast.parse(open(p, encoding="utf-8").read())
        assert not _pdftotext_calls(tree), "%s still runs pdftotext at line(s) %s" % (rel, _pdftotext_calls(tree))
        tables = [n for n in tree.body if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "PDFTEXT" for t in n.targets)]
        assert len(tables) == 1 and isinstance(ast.literal_eval(tables[0].value), dict), "%s declares no PDFTEXT literal" % rel


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
