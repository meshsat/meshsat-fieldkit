"""candidate_guard.py (MESHSAT-1357, set 28, 3 October 2026; the owner's amendment after the first set 28 suite).

The guard refuses a release candidate before any suite runs when the candidate is not the frozen one: a frozen input changed
after the freeze (here the requirements registry, as on set 28's first suite), a tracked file differs from the commit, or a
required gitignored evidence file is missing or changed. The properties held here, each on a throwaway git repository built
in a temporary directory (never this tree), with no results cache and no solver:

- the valid unchanged candidate passes record, check and the evidence check;
- a registry edit committed after the freeze refuses, both as a new commit and when a manifest is recorded on it;
- a registry edit left uncommitted refuses;
- a missing or changed evidence file refuses, in check and in the evidence check before rendering;
- an output declared unbound must really be unbound, and an empty evidence list is refused.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.path.join(os.path.dirname(HERE), "candidate_guard.py")
IDENT = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid"]


def _run(*a, cwd):
    r = subprocess.run([sys.executable, "-B", GUARD] + list(a), cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _git(top, *a):
    subprocess.run(["git", "-C", top] + IDENT + list(a), check=True, capture_output=True)


def _sha(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _fixture():
    """A repository with a registry, an output that prints the registry's pin, an output that prints a stale pin (a historical
    snapshot), and one ignored evidence file; returns (top, manifest path, scratch dir)."""
    d = tempfile.mkdtemp(prefix="cg-")
    top = os.path.join(d, "repo"); os.makedirs(top)
    _git(top, "init", "-q")
    w = lambda rel, text: (os.makedirs(os.path.dirname(os.path.join(top, rel)), exist_ok=True),
                          open(os.path.join(top, rel), "w", encoding="utf-8").write(text))
    w(".gitignore", "v2/ecad/out/\n")
    w("v2/ecad/tools/pcb_requirements.yaml", "records: [REQ-001]\n")
    reg = _sha(os.path.join(top, "v2/ecad/tools/pcb_requirements.yaml"))
    w("v2/docs/records/x/x.out", "inputs\n   reqs  %s  v2/ecad/tools/pcb_requirements.yaml\n" % reg[:16])
    w("v2/docs/records/h/h.out", "historical\n   reqs  %s  v2/ecad/tools/pcb_requirements.yaml\n" % ("0" * 16))
    w("v2/ecad/out/rule-audit/a.json", "{\"verdict\": \"PASS\"}\n")
    _git(top, "add", "-A"); _git(top, "commit", "-q", "-m", "candidate")
    return top, os.path.join(d, "manifest.json"), d


def t_the_valid_unchanged_candidate_passes():
    top, man, d = _fixture()
    try:
        rc, out = _run("record", "--out", man, "--allow-unbound", "v2/docs/records/h/h.out", cwd=top)
        assert rc == 0, out
        m = json.load(open(man))
        assert m["evidence"] == [{"path": "v2/ecad/out/rule-audit/a.json", "sha256": _sha(os.path.join(top, "v2/ecad/out/rule-audit/a.json"))}]
        assert m["allow_unbound"] == ["v2/docs/records/h/h.out"]
        for cmd in ("check", "evidence"):
            rc, out = _run(cmd, "--manifest", man, "--dir", top, cwd=d)
            assert rc == 0 and "PASS" in out, out
    finally:
        shutil.rmtree(d)


def t_a_registry_edit_committed_after_the_freeze_refuses_before_the_suite():
    top, man, d = _fixture()
    try:
        assert _run("record", "--out", man, "--allow-unbound", "v2/docs/records/h/h.out", cwd=top)[0] == 0
        open(os.path.join(top, "v2/ecad/tools/pcb_requirements.yaml"), "a").write("# rebind after the freeze\n")
        _git(top, "commit", "-q", "-am", "rebind")
        rc, out = _run("check", "--manifest", man, "--dir", top, cwd=d)
        assert rc == 2 and "the manifest's candidate is" in out and "x.out does not bind" in out, out
        rc, out = _run("record", "--out", man + ".2", "--allow-unbound", "v2/docs/records/h/h.out", cwd=top)
        assert rc == 2 and "C2 v2/docs/records/x/x.out does not bind" in out and not os.path.exists(man + ".2"), out
    finally:
        shutil.rmtree(d)


def t_a_registry_edit_left_uncommitted_refuses():
    top, man, d = _fixture()
    try:
        assert _run("record", "--out", man, "--allow-unbound", "v2/docs/records/h/h.out", cwd=top)[0] == 0
        open(os.path.join(top, "v2/ecad/tools/pcb_requirements.yaml"), "a").write("# edited\n")
        rc, out = _run("check", "--manifest", man, "--dir", top, cwd=d)
        assert rc == 2 and "tracked file differs from HEAD" in out and "x.out does not bind" in out, out
    finally:
        shutil.rmtree(d)


def t_missing_or_changed_evidence_refuses_before_rendering_and_before_the_suite():
    top, man, d = _fixture()
    try:
        assert _run("record", "--out", man, "--allow-unbound", "v2/docs/records/h/h.out", cwd=top)[0] == 0
        ev = os.path.join(top, "v2/ecad/out/rule-audit/a.json")
        open(ev, "w").write("{\"verdict\": \"FAIL\"}\n")
        for cmd in ("evidence", "check"):
            rc, out = _run(cmd, "--manifest", man, "--dir", top, cwd=d)
            assert rc == 2 and "EVIDENCE changed: v2/ecad/out/rule-audit/a.json" in out, out
        os.remove(ev)
        for cmd in ("evidence", "check"):
            rc, out = _run(cmd, "--manifest", man, "--dir", top, cwd=d)
            assert rc == 2 and "EVIDENCE missing: v2/ecad/out/rule-audit/a.json" in out, out
    finally:
        shutil.rmtree(d)


def t_a_declared_unbound_output_must_be_unbound_and_no_evidence_is_refused():
    top, man, d = _fixture()
    try:
        rc, out = _run("record", "--out", man, "--allow-unbound", "v2/docs/records/h/h.out", "--allow-unbound",
                       "v2/docs/records/x/x.out", cwd=top)
        assert rc == 2 and "--allow-unbound v2/docs/records/x/x.out: it binds" in out, out
        rc, out = _run("record", "--out", man, cwd=top)
        assert rc == 2 and "C2 v2/docs/records/h/h.out does not bind" in out, out
        shutil.rmtree(os.path.join(top, "v2/ecad/out"))
        rc, out = _run("record", "--out", man, "--allow-unbound", "v2/docs/records/h/h.out", cwd=top)
        assert rc == 2 and "no evidence file" in out, out
    finally:
        shutil.rmtree(d)
