#!/usr/bin/env python3
"""The handover snapshot is built from one commit, the same way every time (MESHSAT-1357, 27 September 2026).

handover_pack.py promises four things a recipient relies on without being able to check them by eye: two builds of
one commit are the same bytes; nothing edited, staged or created after the commit travels with it; a path the spec
excludes stays out even where a later rule would include it; and the manifest names every file of the ZIP with its
bytes. Each is held here on a throwaway repository built in a temporary directory, never on this tree's own files,
so no fixture can write into the tree's evidence."""
import atexit, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip  # noqa: E402

SPEC = """schema: 1
title: fixture
max_zip_bytes: 1000000
sources_yaml: v2/vendor/SOURCES.yaml
pages: [v2/docs/handover/START-HERE.md, v2/docs/handover/ABSENT.md]
boards: {manifest: v2/ecad/tools/readiness_manifest.json, profiles: "v2/ecad/tools/routeflow/*.json", ecad: v2/ecad}
groups: {H0: handover, L8: schematics, L1: product, T: tools, L6: parts}
rules:
  - {action: include, group: H0, glob: "v2/docs/handover/**", role: pages}
  - {action: include, group: L8, glob: "v2/ecad/{phase}/{stem}.kicad_sch", role: schematic}
  - {action: include, group: L8, glob: "v2/ecad/{phase}/out/{stem}.net", role: netlist}
  - {action: exclude, kind: stale-layout, glob: "v2/ecad/{phase}/{stem}.kicad_pcb", reason: "an earlier layout"}
  - {action: exclude, kind: superseded-phase, glob: ["v2/ecad/pcb-q/**", "v2/ecad/pcb-q-q9/**"], reason: "an earlier phase"}
  - {action: exclude, kind: history, glob: "v2/docs/secret/**", reason: "superseded, kept out"}
  - {action: include, group: L1, glob: ["README.md", "run.sh", "v2/docs/**"], role: docs}
  - {action: include, group: L6, glob: "v2/vendor/**/*.yaml", role: index}
  - {action: reference, glob: "v2/vendor/**", reason: "size"}
  - {action: include, group: T, glob: "v2/ecad/tools/**", role: tools}
"""
DOC = b"%PDF-1.4 a maker document\n"
FILES = {
    "README.md": b"fixture readme\n",
    "run.sh": b"#!/bin/sh\necho hi\n",
    "v2/docs/handover/pack.yaml": SPEC.encode(),
    "v2/docs/handover/START-HERE.md": b"# start here\n",
    "v2/docs/A.md": b"# a committed document\n",
    "v2/docs/secret/old.md": b"# excluded by the rule above the include that also matches it\n",
    "v2/vendor/SOURCES.yaml": ("parts:\n  - id: fitted-part\n    function: a part on a schematic\n    identity: MATCH\n"
                               "    documents:\n      - path: v2/vendor/x/doc.pdf\n        sha256: %s\n        url: https://example.invalid/doc.pdf\n"
                               "  - id: not-fitted\n    function: a part on no schematic\n    identity: NOT_FITTED\n"
                               "    documents:\n      - path: v2/vendor/x/gone.pdf\n        sha256: 00\n"
                               % hashlib.sha256(DOC).hexdigest()).encode(),
    "v2/vendor/x/doc.pdf": DOC,
    "v2/vendor/x/ünïcode.pdf": b"%PDF-1.4 a file whose name git would quote\n",
    "v2/ecad/tools/readiness_manifest.json": json.dumps({"boards": {"q": {"project": "pcb-q"}}}).encode(),
    "v2/ecad/tools/routeflow/q.json": json.dumps({"board": "pcb-q", "project": "v2/ecad/pcb-q-q2"}).encode(),
    "v2/ecad/tools/gen_sch_q.py": b"import os\nprint(os.getcwd())\n",
    "v2/ecad/pcb-q-q2/pcb-q.kicad_sch": b"(kicad_sch committed)\n",
    "v2/ecad/pcb-q-q2/pcb-q.kicad_pcb": b"(kicad_pcb stale)\n",
    "v2/ecad/pcb-q-q2/out/pcb-q.net": b"(export committed)\n",
    "v2/ecad/pcb-q/pcb-q.kicad_sch": b"(kicad_sch of an earlier phase)\n",
    "v2/ecad/pcb-q-q9/pcb-q.kicad_sch": b"(a decoy directory no profile names)\n",
}


_TEMP = []
atexit.register(lambda: [shutil.rmtree(t, ignore_errors=True) for t in _TEMP])


def _tmp(prefix):
    t = tempfile.mkdtemp(prefix=prefix); _TEMP.append(t); return t


def _git(d, *a):
    r = subprocess.run(["git", "-C", d, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(a),
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, "git %s: %s" % (a, r.stderr)
    return r.stdout.strip()


def _repo(extra=None):
    if not shutil.which("git"): raise Skip("git is not on this host")
    d = _tmp("hpack-fixture-")
    _git(d, "init", "-q")
    for p, data in dict(FILES, **(extra or {})).items():
        full = os.path.join(d, *p.split("/")); os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "wb").write(data)
    os.chmod(os.path.join(d, "run.sh"), 0o755)
    _git(d, "add", "-A"); _git(d, "commit", "-q", "-m", "fixture")
    return d, _git(d, "rev-parse", "HEAD")


def _hp():
    import handover_pack
    return handover_pack


def _build(repo, commit, version="V1", out=None):
    hp = _hp()
    out = out or _tmp("hpack-out-")
    g = hp.Git(repo)
    try: r = hp.build(g, commit, version, out)
    finally: g.close()
    return r


def _manifest(snap):
    rows = open(os.path.join(snap, "MANIFEST.tsv"), encoding="utf-8").read().splitlines()
    return {r.split("\t")[0]: r.split("\t") for r in rows[1:]}


def t_two_builds_of_one_commit_are_byte_identical():
    d, c = _repo()
    a, b = _build(d, c), _build(d, c)
    assert open(os.path.join(a["snapshot"], "MANIFEST.tsv"), "rb").read() == \
        open(os.path.join(b["snapshot"], "MANIFEST.tsv"), "rb").read(), "two builds wrote different manifests"
    assert a["zip_sha256"] == b["zip_sha256"], "two builds of one commit wrote different ZIPs"
    assert hashlib.sha256(open(a["zip"], "rb").read()).hexdigest() == a["zip_sha256"]
    assert open(a["zip"] + ".sha256").read().split()[0] == a["zip_sha256"]


def t_a_file_changed_after_the_commit_is_not_picked_up():
    d, c = _repo()
    open(os.path.join(d, "v2", "docs", "A.md"), "wb").write(b"# edited after the commit\n")          # modified
    open(os.path.join(d, "README.md"), "wb").write(b"staged after the commit\n"); _git(d, "add", "README.md")  # staged
    open(os.path.join(d, "v2", "docs", "new.md"), "wb").write(b"# untracked\n")                        # untracked
    r = _build(d, c)
    snap = r["snapshot"]
    assert open(os.path.join(snap, "v2", "docs", "A.md"), "rb").read() == FILES["v2/docs/A.md"], "a working-tree edit travelled"
    assert open(os.path.join(snap, "README.md"), "rb").read() == FILES["README.md"], "a staged change travelled"
    assert not os.path.exists(os.path.join(snap, "v2", "docs", "new.md")), "an untracked file travelled"
    with zipfile.ZipFile(r["zip"]) as z:
        assert z.read("V1/v2/docs/A.md") == FILES["v2/docs/A.md"]
        assert "V1/v2/docs/new.md" not in z.namelist()


def t_an_excluded_path_stays_out_even_where_a_later_include_matches():
    d, c = _repo()
    r = _build(d, c)
    m = _manifest(r["snapshot"])
    for p in ("v2/docs/secret/old.md", "v2/ecad/pcb-q-q2/pcb-q.kicad_pcb", "v2/ecad/pcb-q/pcb-q.kicad_sch"):
        assert p not in m, "%s is excluded and still in the manifest" % p
        assert not os.path.exists(os.path.join(r["snapshot"], *p.split("/"))), "%s is excluded and still written" % p
    with zipfile.ZipFile(r["zip"]) as z:
        assert "V1/v2/docs/secret/old.md" not in z.namelist()
    ex = open(os.path.join(r["snapshot"], "EXCLUDED.tsv"), encoding="utf-8").read()
    assert "v2/docs/secret/old.md\t" in ex and "superseded, kept out" in ex, "the exclusion is not listed with its reason"


def t_the_manifest_covers_every_zipped_file_with_its_bytes():
    d, c = _repo()
    r = _build(d, c)
    m = _manifest(r["snapshot"])
    with zipfile.ZipFile(r["zip"]) as z:
        names = [n.split("/", 1)[1] for n in z.namelist()]
        assert set(names) - {"MANIFEST.tsv"} == set(m), "zip and manifest differ: %s" % (set(names) ^ set(m))
        for n in names:
            if n == "MANIFEST.tsv": continue
            data = z.read("V1/" + n)
            assert hashlib.sha256(data).hexdigest() == m[n][2] and len(data) == int(m[n][3]), "%s does not match its row" % n
    assert _hp().verify(r["zip"]) == [] and _hp().verify(r["snapshot"]) == []
    for meta in ("SOURCE.txt", "EXCLUDED.tsv", "REFERENCED-SOURCES.tsv", "START-HERE.md"):
        assert meta in m, "%s is not in the manifest" % meta


def t_verify_finds_a_changed_or_an_added_file():
    d, c = _repo()
    r = _build(d, c)
    open(os.path.join(r["snapshot"], "README.md"), "ab").write(b"tampered\n")
    open(os.path.join(r["snapshot"], "extra.txt"), "wb").write(b"added\n")
    probs = _hp().verify(r["snapshot"])
    assert any(p.startswith("README.md:") for p in probs) and any(p.startswith("extra.txt:") for p in probs), probs


def t_an_unclassified_file_refuses_the_build():
    d, c = _repo({"stray/file.bin": b"no rule names this\n"})
    hp = _hp()
    try:
        _build(d, c)
    except hp.SpecError as e:
        assert "stray/file.bin" in str(e), e
    else:
        raise AssertionError("a file no rule classifies was packed without a word")


def t_the_zip_is_sorted_with_fixed_times_and_git_modes():
    d, c = _repo()
    r = _build(d, c)
    with zipfile.ZipFile(r["zip"]) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        assert names == sorted(names), "entries are not sorted"
        assert {i.date_time for i in infos} == {(1980, 1, 1, 0, 0, 0)}, "a timestamp is not the fixed one"
        modes = {i.filename: (i.external_attr >> 16) & 0o777 for i in infos}
        assert modes["V1/run.sh"] == 0o755 and modes["V1/README.md"] == 0o644, modes


def t_referenced_sources_name_the_citing_entry_and_check_the_sha256():
    d, c = _repo()
    r = _build(d, c)
    rows = [ln.split("\t") for ln in open(os.path.join(r["snapshot"], "REFERENCED-SOURCES.tsv"), encoding="utf-8").read().splitlines()]
    head, body = rows[0], {x[0]: dict(zip(rows[0], x)) for x in rows[1:]}
    doc = body["v2/vendor/x/doc.pdf"]
    assert doc["cited_by_sources_yaml"] == "fitted-part" and doc["a_citing_entry_is_fitted"] == "yes"
    assert doc["check"] == "MATCH" and doc["url"] == "https://example.invalid/doc.pdf", doc
    assert body["v2/vendor/x/ünïcode.pdf"]["check"] == "NOT_CITED_BY_SOURCES_YAML"
    gone = body["v2/vendor/x/gone.pdf"]
    assert gone["check"] == "NOT_IN_COMMIT" and gone["a_citing_entry_is_fitted"] == "no", gone
    assert "v2/vendor/x/doc.pdf" not in _manifest(r["snapshot"]), "a referenced document was bundled"


def t_the_phase_tokens_follow_the_profile_not_the_directory_listing():
    d, c = _repo()
    r = _build(d, c)
    m = _manifest(r["snapshot"])
    assert "v2/ecad/pcb-q-q2/pcb-q.kicad_sch" in m and "v2/ecad/pcb-q-q2/out/pcb-q.net" in m
    assert "v2/ecad/pcb-q-q9/pcb-q.kicad_sch" not in m, "a directory no profile names was taken as the phase"
    assert "q pcb-q -> v2/ecad/pcb-q-q2" in open(os.path.join(r["snapshot"], "SOURCE.txt"), encoding="utf-8").read()


def t_pages_are_copied_to_the_root_and_an_absent_page_is_said():
    d, c = _repo()
    r = _build(d, c)
    assert open(os.path.join(r["snapshot"], "START-HERE.md"), "rb").read() == FILES["v2/docs/handover/START-HERE.md"]
    assert "ABSENT.md: ABSENT at this commit" in open(os.path.join(r["snapshot"], "SOURCE.txt"), encoding="utf-8").read()


def t_a_snapshot_is_never_overwritten():
    d, c = _repo()
    out = _tmp("hpack-out-")
    _build(d, c, out=out)
    hp = _hp()
    try:
        _build(d, c, out=out)
    except hp.SpecError as e:
        assert "immutable" in str(e), e
    else:
        raise AssertionError("a second build overwrote an existing snapshot")


def t_the_committed_spec_classifies_every_file_of_this_tree():
    """The spec in this tree, applied to this tree's HEAD, leaves no file unclassified. Skipped where the tree is not a
    git checkout (a code-only archive or an extracted snapshot)."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
    spec = os.path.join(root, "v2", "docs", "handover", "pack.yaml")
    if not os.path.exists(spec): raise Skip("no v2/docs/handover/pack.yaml in this tree")
    if not shutil.which("git") or subprocess.run(["git", "-C", root, "rev-parse", "HEAD"], capture_output=True,
                                                   timeout=30).returncode != 0:
        raise Skip("this tree is not a git checkout")
    hp = _hp()
    g = hp.Git(root)
    try:
        pl = hp.plan(g, g.commit("HEAD"), open(spec, encoding="utf-8").read())
    finally:
        g.close()
    assert not pl["loose"], "%d file(s) at HEAD are classified by no rule, first: %s" % (len(pl["loose"]), pl["loose"][:5])
    assert pl["boards"], "the spec resolved no board phase directory"
