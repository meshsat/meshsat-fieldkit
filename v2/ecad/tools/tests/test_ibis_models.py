#!/usr/bin/env python3
"""The makers' IBIS models are pinned, not held (MESHSAT-1357, layer 9, stream w5si2, 28 September 2026).

The models are withheld from the repository; v2/vendor/ibis-manifest.yaml pins each and tools/ibis_fetch.py fetches
them. These tests hold the manifest, its reader and the fetch script's handling of what arrives. NOTHING HERE OPENS A
NETWORK CONNECTION: the fetch script's download is replaced by one that raises for the length of every test that
touches it, and its extraction is exercised on bytes made here. Every test passes in both states of the tree (models
present, models absent) except where it says it needs the models, and then it is skipped with the reason."""
import os, sys, io, re, ast, gzip, zipfile, hashlib, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip
import ibis_manifest as IM
import ibis_fetch as IF

REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
MODEL = b"[IBIS Ver] 3.2\n[File Name] fix.ibs\n[Disclaimer] a fixture\n[Copyright] Copyright 2026 a fixture.\n[Component] FIX\n[End]\n"


def _row(**more):
    return dict({"id": "fix", "maker": "fixture", "part": "FIX", "file": "v2/vendor/fix/ibis/fix.ibs",
                 "url": "https://example.invalid/fix.zip", "container": "zip", "member": "FIX_IBIS/fix.ibs",
                 "sha256": hashlib.sha256(MODEL).hexdigest(), "bytes": len(MODEL), "fetched": "never: a fixture",
                 "notice": {"kind": "COPYRIGHT_NO_GRANT", "says": "a fixture",
                            "quotes": [{"lines": "4", "text": "[Copyright] Copyright 2026 a fixture."}]}}, **more)


def _repo(rows, model=None):
    import yaml
    repo = tempfile.mkdtemp(prefix="ibis-models-")
    os.makedirs(os.path.join(repo, "v2", "vendor", "fix", "ibis"))
    yaml.safe_dump({"schema_version": 1, "models": rows}, open(os.path.join(repo, IM.MANIFEST_REL), "w"))
    if model is not None: open(os.path.join(repo, "v2", "vendor", "fix", "ibis", "fix.ibs"), "wb").write(model)
    return repo


def _zip(entries):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, data in entries: z.writestr(n, data)
    return b.getvalue()


class _NoNetwork:
    """For the length of a test, the fetch script's download raises: a test never fetches."""
    def __enter__(self):
        self.old = IF.download
        def refuse(url): raise AssertionError("a test opened a network connection to %s" % url)
        IF.download = refuse
        return self
    def __exit__(self, *a):
        IF.download = self.old


def t_the_manifest_is_read_and_a_row_that_cannot_stand_is_refused_and_pins_nothing():
    good = _row()
    bad = [dict(_row(id="short"), sha256="abc"), dict(_row(id="outside"), file="v2/vendor/fix/fix.ibs"),
           dict(_row(id="nomember"), member=""), dict(_row(id="http"), url="http://example.invalid/x"),
           dict(_row(id="nonotice"), notice={"kind": "COPYRIGHT_NO_GRANT", "quotes": []}),
           dict(_row(id="kind"), notice={"kind": "FREE", "quotes": [{"lines": "1", "text": "x"}]}),
           dict(_row(id="archive"), archive_url="https://example.invalid/copy.zip")]
    man = IM.load(_repo([good] + bad))
    assert man["why"] is None and list(man["models"]) == [good["file"]], man
    assert len(man["refusals"]) == len(bad) and all(any(b["id"] in r for r in man["refusals"]) for b in bad), man["refusals"]
    twice = IM.load(_repo([good, dict(_row(id="again"))]))
    assert len(twice["models"]) == 1 and any("pinned twice" in r for r in twice["refusals"]), twice["refusals"]
    none = IM.load(tempfile.mkdtemp(prefix="ibis-none-"))
    assert none["why"] and not none["models"], none
    broken = tempfile.mkdtemp(prefix="ibis-broken-")
    os.makedirs(os.path.join(broken, "v2", "vendor"))
    open(os.path.join(broken, IM.MANIFEST_REL), "w").write("models: [unclosed\n")
    assert IM.load(broken)["why"] and not IM.load(broken)["models"]


def t_a_model_is_present_absent_or_not_the_file_pinned_and_its_notice_is_held_to_its_header():
    row = _row()
    assert IM.state_of(_repo([row]), row) == (IM.ABSENT, None)
    assert IM.state_of(_repo([row], MODEL), row)[0] == IM.PRESENT
    assert IM.state_of(_repo([row], MODEL + b"| edited\n"), row)[0] == IM.DIFFERS
    assert IM.set_state([]) == "NOT_ASKED" and IM.set_state([IM.PRESENT, IM.PRESENT]) == IM.PRESENT
    assert IM.set_state([IM.ABSENT, IM.ABSENT]) == IM.ABSENT and IM.set_state([IM.PRESENT, IM.ABSENT]) == "PARTIAL"
    assert IM.set_state([IM.PRESENT, IM.DIFFERS, IM.ABSENT]) == IM.DIFFERS
    assert IM.notice_holds(_repo([row], MODEL), row) is None
    assert IM.notice_holds(_repo([row]), row) is None, "an absent model cannot be asked, and its state says so"
    forbids = MODEL.replace(b"a fixture\n[Copyright]", b"Unauthorized reproduction and/or distribution is strictly\n| prohibited.\n[Copyright]")
    r2 = dict(row, sha256=hashlib.sha256(forbids).hexdigest(), bytes=len(forbids))
    why = IM.notice_holds(_repo([r2], forbids), r2)
    assert why and "speaks of reproduction or distribution" in why, "a header that forbids distribution was filed as a copyright line only: %s" % why
    r3 = dict(r2, notice={"kind": "PROHIBITS_DISTRIBUTION", "says": "x", "quotes": [
        {"lines": "3 to 4", "text": "Unauthorized reproduction and/or distribution is strictly prohibited."}]})
    assert IM.notice_holds(_repo([r3], forbids), r3) is None, "a quote across a line break and a comment bar is found"
    r4 = dict(row, notice={"kind": "COPYRIGHT_NO_GRANT", "says": "x", "quotes": [{"lines": "4", "text": "All rights reserved."}]})
    assert "does not say" in IM.notice_holds(_repo([r4], MODEL), r4)


def t_what_arrives_is_unwrapped_by_what_it_is_and_only_the_file_pinned_is_written():
    row = _row()
    z = _zip([("readme.txt", b"x"), ("FIX_IBIS/fix.ibs", MODEL)])
    assert IF.extract(z, row) == (MODEL, "the zip's FIX_IBIS/fix.ibs")
    body, how = IF.extract(gzip.compress(z), row)
    assert body == MODEL and how.startswith("gzip-wrapped"), how
    body, how = IF.extract(_zip([("Other/Folder/FIX.IBS", MODEL)]), row)
    assert body == MODEL, "a member whose folder moved is found by its file name: %s" % how
    body, why = IF.extract(_zip([("a/fix.ibs", MODEL), ("b/fix.ibs", MODEL)]), row)
    assert body is None and "2 entries" in why, why
    body, why = IF.extract(_zip([("readme.txt", b"x")]), row)
    assert body is None and "0 entries" in why, why
    body, why = IF.extract(b"<html>Access Denied</html>", row)
    assert body is None and "not one" in why, "a refusal page was taken for a model: %s" % why
    assert IF.extract(MODEL, dict(row, container="ibs"))[0] == MODEL
    # the sources, in order: the maker, the capture the row names, the newest capture
    src = IF.sources(dict(row, archive_url="https://web.archive.org/web/20250911224858id_/https://example.invalid/fix.zip"))
    assert [u for _l, u in src] == ["https://example.invalid/fix.zip",
                                    "https://web.archive.org/web/20250911224858id_/https://example.invalid/fix.zip",
                                    "https://web.archive.org/web/2026id_/https://example.invalid/fix.zip"], src
    # fetch_one with the download replaced: a wrong file is never written, the right one is, from the second source
    dest = tempfile.mkdtemp(prefix="ibis-dest-")
    served = {"https://example.invalid/fix.zip": (None, "HTTP 403"),
              "https://web.archive.org/web/2026id_/https://example.invalid/fix.zip": (_zip([("FIX_IBIS/fix.ibs", MODEL + b"| revised\n")]), None)}
    old = IF.download
    IF.download = lambda url: served[url]
    try:
        ok, what = IF.fetch_one(row, dest)
        assert not ok and "NOT WRITTEN" in what and "HTTP 403" in what, what
        assert not os.path.exists(os.path.join(dest, row["file"])), "a file that is not the one pinned was written"
        served["https://web.archive.org/web/2026id_/https://example.invalid/fix.zip"] = (gzip.compress(z), None)
        ok, what = IF.fetch_one(row, dest)
        assert ok and "newest capture" in what and "HTTP 403" in what, what
        assert open(os.path.join(dest, row["file"]), "rb").read() == MODEL
    finally:
        IF.download = old


def t_the_check_mode_says_the_state_and_fetches_nothing():
    row = _row()
    with _NoNetwork():
        for model, state, rc in ((None, IM.ABSENT, 0), (MODEL, IM.PRESENT, 0), (MODEL + b"| edited\n", IM.DIFFERS, 1)):
            repo = _repo([row], model)
            states, bad = IF.check(repo, IM.load(repo), quiet=True)
            assert states == {"fix": state} and bool(bad) == bool(rc), (state, states, bad)
            old = sys.stdout
            sys.stdout = io.StringIO()
            try: got = IF.main(["--check", "--root", repo])
            finally: text, sys.stdout = sys.stdout.getvalue(), old
            assert got == rc and ("state %s" % state) in text, (state, got, text)
        old = sys.stdout
        sys.stdout = io.StringIO()
        try: got = IF.main([])
        finally: sys.stdout = old
        assert got == 2, "with neither --check nor --fetch the script must do nothing but say how it is used"


def t_no_tool_and_no_test_fetches_by_itself():
    """ibis_fetch is imported by this test file only, which replaces its download; no tool of the pipeline imports it
    (parsed, not searched for as text), and its own entry point does nothing without --fetch or --check."""
    users = []
    for d in (TOOLS, os.path.join(TOOLS, "tests")):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py") or f == "ibis_fetch.py": continue
            try: tree = ast.parse(open(os.path.join(d, f), encoding="utf-8").read())
            except SyntaxError: continue
            for n in ast.walk(tree):
                names = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] if isinstance(n, ast.ImportFrom) else [])
                if any(str(x).split(".")[0] == "ibis_fetch" for x in names): users.append(f)
    assert sorted(set(users)) == ["test_ibis_models.py"], "ibis_fetch is imported by %s" % sorted(set(users))
    tree = ast.parse(open(os.path.join(TOOLS, "ibis_manifest.py"), encoding="utf-8").read())
    mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    assert not (mods & {"urllib", "http", "socket", "requests", "subprocess"}), "the manifest reader can reach a network: %s" % mods


def t_the_real_manifest_stands_and_every_model_is_ignored_and_none_is_tracked():
    """In every state of the tree: the manifest reads with no refusal, every file it pins lies where the ignore rule
    reaches, the ignore rule is in .gitignore, and git tracks no model (a model added by force would be published with
    the next push). Where a model is present its header says what the manifest quotes."""
    man = IM.load(REPO)
    assert man["why"] is None and not man["refusals"] and man["models"], (man["why"], man["refusals"])
    gi = os.path.join(REPO, ".gitignore")
    if not os.path.exists(gi): raise Skip("no .gitignore in this tree (a snapshot, not a checkout): %s" % gi)
    rules = [l.strip() for l in open(gi, encoding="utf-8").read().splitlines() if l.strip() and not l.startswith("#")]
    assert "v2/vendor/*/ibis/*.ibs" in rules, "the ignore rule for the makers' models is gone from .gitignore"
    import fnmatch
    for f, row in man["models"].items():
        assert fnmatch.fnmatchcase(f, "v2/vendor/*/ibis/*.ibs"), f
        why = IM.notice_holds(REPO, row)
        assert why is None, why
        assert IM.state_of(REPO, row)[0] != IM.DIFFERS, "%s is present and is not the file pinned" % f
    try:
        r = subprocess.run(["git", "-C", REPO, "ls-files", "--", "v2/vendor"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        r = None
    if r is None or r.returncode != 0: raise Skip("git cannot list this tree's files (a snapshot, not a checkout)")
    tracked = [l for l in r.stdout.splitlines() if l.lower().endswith(".ibs")]
    assert not tracked, "a maker's model is TRACKED and would be published by a push: %s" % tracked
    kinds = [row["notice"]["kind"] for row in man["models"].values()]
    assert set(kinds) <= set(IM.KINDS)
