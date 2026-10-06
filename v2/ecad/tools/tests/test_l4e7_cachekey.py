"""Record L4-E7's results cache KEY at the L4-E11 boundary (MESHSAT-1357, W61, 6 October 2026; the owner's workflow request
MESHSAT-WORKFLOW-IMPROVE-20261006-1829-01, item 2, and the constitution's section 8: a cache key covers the model code, the
relevant inputs and the material tool versions; a changed numerical input invalidates its dependent results, unrelated prose
need not).

l4e7_stage_settings.py reads sixteen numbers of L4-E11's printed output l4e11_power.out (six sentences: the UVLO's rise and fall,
the start's slew, INP's turn-on, the short-circuit and the overcurrent thresholds), now through one strict extractor,
l4e11_numbers(). The cache's KEY holds the sha256 of their canonical JSON as its part l4e11_numbers in place of the file's whole
digest, which the cache keeps beside the KEY as evidence. These tests never run the solver and never write into the tree: every
KEY is computed by the record's own key_parts() on a scratch tree whose inputs are links to this tree's files and whose
l4e11_power.out is the text under test. (a) a prose-only change (the two printed pin lines that moved on 6 October 2026, the whole
file re-wrapped, a number this record does not read) leaves the KEY; (b) a change of any consumed number moves it, and only its
l4e11_numbers part; (c) a missing, unreadable or truncated file, and a consumed value removed, duplicated, unparsable or out of
its declared form, refuse with exit 3 naming the value, at the extractor, at the KEY, at the cache reader and in a run before the
solver; (d) a code change in the record still moves the KEY's source part, and compute() reads the file only through the
extractor; (e) the evidence digest is the file's sha256, written beside the KEY by a run; (f) the file at d83d9f2d and at 31928583
(whose whole digests differ, a2089b3f6682 against 36141414a1b6) reads to equal canonical JSON and an equal KEY, so the re-key of
6 October 2026 would not have been owed under this boundary.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e7")
SCRIPT = os.path.join(REC, "l4e7_stage_settings.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}


def _m():
    """The record's module (its solver never called) and the committed cache's recorded inputs."""
    if "m" not in _C:
        need(SCRIPT, "the L4-E7 record")
        need(os.path.join(ROOT, ".git"), "a git checkout (the record finds its tree by git)")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed (its version is a KEY part)")
        sp = importlib.util.spec_from_file_location("l4e7_stage_settings_cachekey", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        data = json.load(open(m.CACHE, encoding="utf-8"))
        _C["m"] = m
        _C["files"] = sorted(set(data["parts"]["files"]) | set(m.EVIDENCE_ONLY))
        _C["text"] = open(os.path.join(ROOT, m.L4E11_OUT), encoding="utf-8").read()
    return _C["m"]


def _git_status():
    return subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def _tree(td, m, text):
    """A scratch tree: every input the cache records and a1solar's array_calc.py linked read-only to this tree, and L4E11_OUT a
    real file holding text (str or bytes; None: absent). Only files are linked, so nothing written under td reaches the tree."""
    for rel in _C["files"] + [m.A1_CALC]:
        dst = os.path.join(td, rel)
        if rel in m.EVIDENCE_ONLY or os.path.lexists(dst):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        os.symlink(os.path.join(ROOT, rel), dst)
    p = os.path.join(td, m.L4E11_OUT)
    if os.path.lexists(p):
        os.remove(p)
    if text is not None:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(text if isinstance(text, bytes) else text.encode("utf-8"))
    assert not os.path.islink(os.path.dirname(p))


@contextlib.contextmanager
def _top(m, td):
    """The record pointed at the scratch tree td; its solver made to fail if reached."""
    def no_compute():
        raise AssertionError("the run reached the solver")
    top0, rr0 = m.TOP, m.run_recorded
    m.TOP, m.run_recorded = td, no_compute
    try:
        yield
    finally:
        m.TOP, m.run_recorded = top0, rr0


def _key(m, text):
    """(KEY, parts, the whole-file KEY of before this boundary) of the cache's recorded inputs on a scratch tree whose
    l4e11_power.out is text."""
    with tempfile.TemporaryDirectory() as td:
        _tree(td, m, text)
        with _top(m, td):
            parts = m.key_parts(_C["files"])
        raw = text if isinstance(text, bytes) else text.encode("utf-8")
        old = {k: v for k, v in parts.items() if k != "l4e11_numbers"}
        old["files"] = dict(parts["files"], **{m.L4E11_OUT: hashlib.sha256(raw).hexdigest()})
        return m.key_of(parts), parts, m.key_of(old)


def _refusal(fn):
    """(exit code, stderr) of a call that must refuse."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            fn()
    except SystemExit as e:
        return e.code, err.getvalue()
    raise AssertionError("no refusal: %s" % err.getvalue())


def _digest(m, nums):
    return hashlib.sha256(m.l4e11_canonical(nums).encode("utf-8")).hexdigest()


def _wide(pat):
    return pat.replace(r"([\d.]+)", r"(\S+)").replace(r"[\d.]+", r"\S+")


def _with_token(m, name, i, new, text=None):
    """The flattened file with token i of the sentence name replaced by new."""
    t = m.flat(_C["text"] if text is None else text)
    pat = {n: p for n, p, _k, _w in m.L4E11_NUMBERS}[name]
    mm = re.search(_wide(pat), t)
    s, e = mm.span(i + 1)
    return t[:s] + new + t[e:]


def t_a_prose_only_change_of_l4e11_power_out_leaves_the_key():
    """The two printed input-digest lines that moved on 6 October 2026 (hwfw, arch), the whole file re-wrapped onto one line, and a
    number printed in a consumed sentence that this record does not read (the OV cut-off on the UVLO line) each leave the KEY
    equal, while the KEY of before this boundary (the file's whole digest) moves for each."""
    m = _m()
    before = _git_status()
    text = _C["text"]
    k0, p0, w0 = _key(m, text)
    assert m.L4E11_OUT not in p0["files"] and p0["l4e11_numbers"] == _digest(m, m.l4e11_numbers(text=text))
    lines = text.split("\n")
    pins = [i for i, ln in enumerate(lines) if re.fullmatch(r"\s+(hwfw|arch)\s+[0-9a-f]{16}\s+\S+", ln)]
    assert len(pins) == 2, "the hwfw and arch pin lines of l4e11_power.out"
    for i in pins:
        lines[i] = re.sub(r"[0-9a-f]{16}", "0123456789abcdef", lines[i])
    pinned = "\n".join(lines)
    ov = "OV: off above 39.6 / 40.36 / 41.22 V"
    assert text.count(ov) == 1
    for prose in (pinned, " ".join(text.split()), text.replace(ov, "OV: off above 39.7 / 40.46 / 41.32 V")):
        assert prose != text
        k1, p1, w1 = _key(m, prose)
        assert k1 == k0 and p1 == p0, "a prose-only change of l4e11_power.out moved the KEY"
        assert w1 != w0, "the whole-file KEY of before this boundary would not have moved (the fixture changed nothing)"
    assert _git_status() == before, "the repository's git status changed during the test"


def t_b_a_changed_consumed_number_moves_the_key():
    """Each of the sixteen consumed numbers, moved inside its triple's order, is read back by the extractor and moves the
    l4e11_numbers digest; one (the overcurrent threshold's least, the figure the breaker's margin is taken from) moves the KEY on a
    scratch tree, and only its l4e11_numbers part."""
    m = _m()
    base = m.l4e11_numbers(text=_C["text"])
    assert {n: len(v) for n, v in base.items()} == {"uv": 3, "uvf": 3, "slew": 3, "inp": 1, "scp": 3, "ocp": 3}
    d0 = _digest(m, base)
    n_moved = 0
    for name, vals in sorted(base.items()):
        for i, v in enumerate(vals):
            new = v + 0.01 if (len(vals) == 1 or i == 2) else (v - 0.01 if i == 0 else (vals[0] + v) / 2.0)
            tok = "%.3f" % new
            got = m.l4e11_numbers(text=_with_token(m, name, i, tok))
            assert got[name][i] == float(tok) != v and all(got[n] == base[n] for n in base if n != name), (name, i, got)
            assert _digest(m, got) != d0, (name, i)
            n_moved += 1
    assert n_moved == 16
    k0, p0, _w0 = _key(m, _C["text"])
    k1, p1, _w1 = _key(m, _with_token(m, "ocp", 0, "6.363"))
    assert k1 != k0 and [p for p in p0 if p0[p] != p1[p]] == ["l4e11_numbers"]


def t_c_a_missing_or_corrupt_l4e11_power_out_fails_closed():
    """A missing, unreadable (not UTF-8) or truncated l4e11_power.out, and a consumed value removed, duplicated, unparsable or out
    of its declared form (not a plain decimal; a triple that descends), refuse with exit 3 and a message naming the value and the
    file; never a default. On a scratch tree the refusal holds at the KEY (key_parts), at the cache reader (load_cache refuses
    rather than return None and leave a recompute to run on it) and in a run, before the cache is read or the solver reached."""
    m = _m()
    before = _git_status()
    text = _C["text"]
    flat = m.flat(text)
    ocp = re.search(_wide(dict((n, p) for n, p, _k, _w in m.L4E11_NUMBERS)["ocp"]), flat).group(0)
    cases = [
        ("missing file", None, "is missing"),
        ("not UTF-8", b"\xff\xfe" + text.encode("utf-8"), "is unreadable (UnicodeDecodeError)"),
        ("truncated", text[:len(text) // 10], "missing in v2/docs/records/l4e11/l4e11_power.out"),
        ("INP removed", flat.replace("INP high from DC_P 7.23 V", "INP high from DC_P V"), "L4-E11's INP (inp) missing in"),
        ("overcurrent duplicated", flat + " " + ocp, "L4-E11's overcurrent threshold (ocp) duplicated in"),
        ("slew unparsable", _with_token(m, "slew", 1, "20.7.1"), "L4-E11's slew (slew) unparsable in"),
        ("slew exponent", _with_token(m, "slew", 1, "2.071e1"), "L4-E11's slew (slew) out of its declared form in"),
        ("short circuit descending", _with_token(m, "scp", 2, "11.00"), "L4-E11's short-circuit threshold (scp) out of its declared form in"),
    ]
    for label, bad, words in cases:
        if isinstance(bad, str):
            code, err = _refusal(lambda: m.l4e11_numbers(text=bad))
            assert code == 3 and words in err and "refusing" in err, (label, err)
        with tempfile.TemporaryDirectory() as td:
            _tree(td, m, bad)
            with _top(m, td):
                for where, fn in (("extractor", lambda: m.l4e11_numbers()), ("KEY", lambda: m.key_parts(_C["files"])),
                                  ("cache reader", lambda: m.load_cache())):
                    code, err = _refusal(fn)
                    assert code == 3 and words in err and "l4e11_numbers:" in err, (label, where, err)
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code, err = _refusal(lambda: m.main([]))
                assert code == 3 and words in err and out.getvalue() == "", (label, "run", err)
                with contextlib.redirect_stdout(out):
                    code, err = _refusal(lambda: m.main(["--recompute"]))
                assert code == 3 and words in err, (label, "run --recompute", err)
    assert _git_status() == before, "the repository's git status changed during the test"


def t_d_a_code_change_in_the_record_still_moves_the_key():
    """The KEY's source part follows compute() into the extractor: a changed pattern, a changed declared form and a changed use of
    a consumed number each move it (and so the KEY), a comment above the extractor does not; and compute() reads l4e11_power.out only through
    l4e11_numbers() (no other mention of the file or its path in compute()), so the KEY part covers everything it reads there."""
    import ast
    m = _m()
    text = open(SCRIPT, encoding="utf-8").read()
    base = m.src_part(text)
    assert {"compute", "l4e11_numbers", "L4E11_NUMBERS", "NUM_FORM", "L4E11_OUT", "flat", "refuse"} <= set(base)
    k0, p0, _w = _key(m, _C["text"])
    assert p0["src"] == base
    edits = (('("inp", r"INP high from DC_P ([\\d.]+) V", 1, "L4-E11\'s INP")', '("inp", r"INP high from DC_P ([\\d.]+) V,", 1, "L4-E11\'s INP")'),
             ('NUM_FORM = r"\\d+(?:\\.\\d+)?"', 'NUM_FORM = r"\\d+(?:\\.\\d*)?"'),
             ('ocp11 = tuple(nums11["ocp"])', 'ocp11 = tuple(sorted(nums11["ocp"]))'),
             ('inp=nums11["inp"][0]', 'inp=nums11["inp"][-1]'))
    for a, b in edits:
        assert text.count(a) == 1, a
        moved = m.src_part(text.replace(a, b))
        assert moved != base and m.key_of(dict(p0, src=moved)) != k0, a
    c = "# What compute() reads of L4-E11's printed output, and nothing else of that file"
    assert text.count(c) == 1 and m.src_part(text.replace(c, c + " (a comment)")) == base
    tree = ast.parse(text)
    comp = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "compute"][0]
    seg = ast.get_source_segment(text, comp)
    assert "l4e11_power" not in seg and "L4E11_OUT" not in seg and "l4e11/" not in seg.replace("l4e11/apply_gen_sch_e_entry.py", "")
    calls = [n for n in ast.walk(comp) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "l4e11_numbers"]
    assert len(calls) == 1 and not calls[0].args and not calls[0].keywords


def t_e_the_evidence_digest_is_the_files_sha256():
    """evidence_part() gives L4E11_OUT's sha256 (the file's bytes) and the numbers read of it; a run that writes the cache (its
    solver stubbed with a two-figure result, on a scratch tree, the cache file a temporary one) writes the KEY of key_parts(), the
    parts without the file's whole digest, and the evidence beside them; a prose change then keeps that cache's KEY while the
    evidence still names the bytes it was computed on, and a cache stripped of its evidence is never rendered from."""
    m = _m()
    before = _git_status()
    raw = open(os.path.join(ROOT, m.L4E11_OUT), "rb").read()
    ev = m.evidence_part()
    assert ev == dict(files={m.L4E11_OUT: hashlib.sha256(raw).hexdigest()}, l4e11_numbers=m.l4e11_numbers())
    with tempfile.TemporaryDirectory() as td:
        _tree(td, m, raw)
        cache = os.path.join(td, "scratch.results.json")
        R0 = dict(fig=(1.5, 2.5))
        render0, cache0 = m.render, m.CACHE
        out = io.StringIO()
        try:
            m.render, m.CACHE = (lambda R: ["rendered %r" % (R,)]), cache
            with _top(m, td):
                m.run_recorded = lambda: (R0, list(_C["files"]))
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    assert m.main(["--recompute"]) == 0
                data = json.load(open(cache, encoding="utf-8"))
                assert set(data) == {"key", "parts", "evidence", "R"} and "l4e11_numbers" in data["parts"]
                assert m.L4E11_OUT not in data["parts"]["files"] and data["key"] == m.key_of(data["parts"])
                assert data["evidence"] == json.loads(json.dumps(ev)) and data["evidence"]["files"][m.L4E11_OUT] == hashlib.sha256(raw).hexdigest()
                assert m.load_cache(cache) == R0
                prose = re.sub(rb"(\n\s+hwfw\s+)[0-9a-f]{16}", rb"\g<1>0123456789abcdef", raw, count=1)
                assert prose != raw
                _tree(td, m, prose)
                assert m.load_cache(cache) == R0, "a prose change of l4e11_power.out invalidated the cache"
                assert m.evidence_part()["files"][m.L4E11_OUT] != data["evidence"]["files"][m.L4E11_OUT]
                stripped = os.path.join(td, "stripped.results.json")
                open(stripped, "w", encoding="utf-8").write(json.dumps({k: v for k, v in data.items() if k != "evidence"}))
                assert m.load_cache(stripped) is None
        finally:
            m.render, m.CACHE = render0, cache0
        assert out.getvalue() == "rendered %r\n" % (R0,)
    assert _git_status() == before, "the repository's git status changed during the test"


def t_f_d83d9f2d_and_31928583_read_to_equal_numbers():
    """l4e11_power.out at d83d9f2d (the whole digest the committed cache holds, a2089b3f6682) and at 31928583 (36141414a1b6; only
    the hwfw and arch pin lines differ) reads to the same canonical JSON and the same KEY under this boundary, while the KEY of
    before this boundary differs: the box re-key spent on that move would not have been owed."""
    m = _m()
    shown = {}
    for c in ("d83d9f2d", "31928583"):
        r = subprocess.run(["git", "show", "%s:%s" % (c, m.L4E11_OUT)], cwd=ROOT, capture_output=True)
        assert r.returncode == 0, "%s is not in this branch's history: %s" % (c, r.stderr.decode())
        shown[c] = r.stdout
    assert hashlib.sha256(shown["d83d9f2d"]).hexdigest().startswith("a2089b3f6682")
    assert hashlib.sha256(shown["31928583"]).hexdigest().startswith("36141414a1b6")
    j = {c: m.l4e11_canonical(m.l4e11_numbers(text=b.decode("utf-8"))) for c, b in shown.items()}
    assert j["d83d9f2d"] == j["31928583"], j
    assert json.loads(j["d83d9f2d"]) == {"inp": [7.23], "ocp": [6.364, 6.8, 7.136], "scp": [10.36, 12.04, 13.87],
                                         "slew": [17.28, 20.71, 24.65], "uv": [7.87, 8.14, 8.44], "uvf": [7.46, 7.66, 7.95]}
    ka, pa, wa = _key(m, shown["d83d9f2d"])
    kb, pb, wb = _key(m, shown["31928583"])
    assert ka == kb and pa == pb and wa != wb


def t_g_a_unicode_digit_refuses_as_malformed():
    """W64's F-4 (W67, 6 October 2026): the declared form is a plain ASCII decimal. A consumed number printed in fullwidth digits
    (U+FF10 to U+FF19), in Arabic-Indic digits (U+0660 to U+0669) or with one fullwidth digit among ASCII ones is read by float()
    as 7.23, and a Unicode \\d accepted it before; each now refuses with exit 3 as out of its declared form, naming the value and
    the file. Every regular expression call of l4e11_numbers() passes re.ASCII (read with ast), so no \\d of the extractor reads
    a non-ASCII digit."""
    import ast
    m = _m()
    for tok in ("\uff17.\uff12\uff13", "\u0667.\u0662\u0663", "7.2\uff13"):
        assert float(tok) == 7.23
        bad = _with_token(m, "inp", 0, tok)
        code, err = _refusal(lambda: m.l4e11_numbers(text=bad))
        assert code == 3 and "L4-E11's INP (inp) out of its declared form in %s: %r is not a plain decimal" % (m.L4E11_OUT, tok) in err, (tok, err)
    assert m.l4e11_numbers(text=_C["text"])["inp"] == [7.23]
    text = open(SCRIPT, encoding="utf-8").read()
    fn = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == "l4e11_numbers"][0]
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and isinstance(n.func.value, ast.Name) and n.func.value.id == "re" and n.func.attr in ("compile", "search", "match", "fullmatch", "finditer", "findall")]
    assert len(calls) >= 5, ast.dump(fn)[:300]

    def ascii_flag(c):
        args = list(c.args[2:] if c.func.attr != "compile" else c.args[1:]) + [k.value for k in c.keywords if k.arg == "flags"]
        return any(isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) and a.value.id == "re" and a.attr in ("ASCII", "A") for a in args)
    assert all(ascii_flag(c) for c in calls), [ast.get_source_segment(text, c) for c in calls if not ascii_flag(c)]
