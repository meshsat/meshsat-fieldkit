#!/usr/bin/env python3
"""A reading's tool is its CODE BUNDLE (MESHSAT-1357, 26 September 2026; the review of the 22:35 progress report,
finding D2: "Tool provenance omits imported helpers ... Add focused regression checks for these actual failure modes:
... a changed helper invalidates an affected prior verdict").

Until that day a verdict recorded the entry script's hash alone (`writer`), and a reading was current while that file
was byte for byte the same, whatever changed in the modules it imports: board C to P's TRN-001 readings were taken
before `kisch.py`, the part-class helper port_protect walks, was committed with the one-way clamp symbol, and read
CURRENT_CANDIDATE. These are executed against fixtures, never against source text:

  * the bundle follows every import it can parse, at any depth, and a literal naming a script; a dictionary key naming
    a file is data, and a module nobody imports is not in it;
  * THE REGRESSION: a verdict written by a real `verdict.write` from a fixture entry script is CURRENT; a changed
    helper it imports makes it STALE by name, and rules_status reads the rule TOOL_CHANGED; a changed module it does
    not import leaves it CURRENT and the rule current;
  * a verdict older than the bundle (a writer and no bundle) is judged by the commit dates of the modules its writer
    imports: a helper committed after the reading makes it STALE, an unrelated commit does not, and the instants are
    compared as instants (a reading at 21:00Z is after a commit at 22:52+02:00);
  * a verdict with neither is judged by the whole bundle's commit dates;
  * the recording channel: verdict.py is in every bundle and its own lazy imports are not followed from it, while a
    gate that imports one of them itself has it;
  * the page names which rows changed class because of the bundle, with the count.
"""
import os, sys, json, subprocess, tempfile, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import verdict as V
import stale_readings as SR
import rules_status as S


def _write(d, name, body):
    p = os.path.join(d, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(textwrap.dedent(body))
    return p


def t_the_bundle_follows_every_parsed_import_and_nothing_else():
    d = tempfile.mkdtemp(prefix="bundle-")
    _write(d, "entry.py", '''
        import helper_top
        import pkg.inner
        from pkg import sub
        import importlib
        TABLE = {"table_key.py": 1}
        def run():
            import helper_lazy
            importlib.import_module("helper_dyn")
            return ["python3", "script_run.py"]
        ''')
    for n in ("helper_top.py", "helper_lazy.py", "helper_dyn.py", "script_run.py", "table_key.py", "unrelated.py",
              "pkg/__init__.py", "pkg/inner.py", "pkg/sub.py"):
        _write(d, n, "X = 1\n")
    b = V.code_bundle(os.path.join(d, "entry.py"), d)
    got = set(b["files"])
    want = {"entry.py", "helper_top.py", "helper_lazy.py", "helper_dyn.py", "script_run.py",
            "pkg/__init__.py", "pkg/inner.py", "pkg/sub.py"}
    assert got == want, (sorted(got - want), sorted(want - got))
    assert "table_key.py" not in got and "unrelated.py" not in got
    assert b["sha16"] == V.bundle_sha(b["files"]) and len(b["sha16"]) == 16
    # and transitively: a helper's own import is followed
    _write(d, "helper_top.py", "import deep\n")
    _write(d, "deep.py", "Y = 2\n")
    assert "deep.py" in V.code_bundle(os.path.join(d, "entry.py"), d)["files"]


def t_verdict_py_is_the_recording_channel_and_its_own_imports_are_not_followed():
    """verdict.py is in every gate's bundle; rules_lib, which it imports lazily to stamp the rule digests, is not
    followed from it (those digests are re-checked by rules_status when the verdict is read), and a gate that imports
    rules_lib itself carries it."""
    d = tempfile.mkdtemp(prefix="bundle-chan-")
    _write(d, "gate_plain.py", "import verdict\n")
    _write(d, "gate_rules.py", "import verdict\nimport rules_lib\n")
    _write(d, "verdict.py", "def f():\n    import rules_lib\n")
    _write(d, "rules_lib.py", "R = 1\n")
    a = V.code_bundle(os.path.join(d, "gate_plain.py"), d)["files"]
    b = V.code_bundle(os.path.join(d, "gate_rules.py"), d)["files"]
    assert "verdict.py" in a and "rules_lib.py" not in a, sorted(a)
    assert "verdict.py" in b and "rules_lib.py" in b, sorted(b)
    real = V.code_bundle(os.path.join(TOOLS, "stackup_gate.py"), TOOLS)["files"]
    assert "stackup_write.py" in real, "stackup_gate's STACKS table lives in stackup_write and is in its bundle now"


def _probe(d, extra=""):
    """A real verdict written by a fixture entry script that imports a fixture helper, through the real verdict.py."""
    _write(d, "probe_gate.py", '''
        import sys
        sys.path.insert(0, %r)
        sys.path.insert(0, %r)
        import probe_helper
        import verdict as v
        v.write("probe_gate", v.PASS, counts={"x": probe_helper.X}, denominator=1, out_dir=%r, quiet=True,
                inputs={"netlist": {"path": "out/pcb-x.net", "sha256_16": "aaaaaaaaaaaaaaaa"}})
        ''' % (d, TOOLS, d))
    _write(d, "probe_helper.py", "X = 1\n")
    _write(d, "probe_unrelated.py", "Z = 1\n")
    env = dict(os.environ); env.pop("VERDICT_DIR", None)
    subprocess.run([sys.executable, os.path.join(d, "probe_gate.py")], check=True, capture_output=True, env=env)
    return json.load(open(os.path.join(d, "probe_gate.verdict.json")))


def t_a_changed_helper_invalidates_an_affected_prior_verdict_and_an_unrelated_change_does_not():
    """THE REGRESSION CHECK the review asks for. The defective instrument is the entry-only one (`bundle=False`): it
    reads the reading CURRENT after the helper changed, which is the failure mode found on 26 September."""
    d = tempfile.mkdtemp(prefix="bundle-regress-")
    rec = _probe(d)
    cb = rec.get("code_bundle") or {}
    assert cb.get("sha16") and any(k.endswith("probe_helper.py") for k in cb["files"]), cb
    assert "verdict.py" in cb["files"], "the recording channel is in every bundle"
    assert SR.judge_one(rec)[0] == "CURRENT"
    import test_evidence_class as EC
    rule, cov = EC._rule(), EC._cov()
    config = {"probe_gate.py": ()}

    def cls(r):
        vs = {"gate_x": dict(r, tool="gate_x")}
        row = S.result_for(rule, "x", cov, vs, EC._manifest(), EC.FP, None, {"x", EC.BOARD})
        return S.evidence_class(rule, "x", cov, vs, EC._manifest(), EC.FP, {"x", EC.BOARD}, row, EC._cand(), EC.EMPTY,
                                config_inputs=config)
    rec["policy"] = {"rule_set_fingerprint": EC.FP}          # the fixture rule set, as the other fixtures carry
    assert cls(rec)["evidence_class"] == S.CURRENT_CANDIDATE, cls(rec)
    # an unrelated module changes: nothing the reading ran moved
    _write(d, "probe_unrelated.py", "Z = 2\n")
    assert SR.judge_one(rec)[0] == "CURRENT"
    assert cls(rec)["evidence_class"] == S.CURRENT_CANDIDATE
    # the helper changes: the entry script is byte for byte the same, and the reading is owed
    _write(d, "probe_helper.py", "X = 2  # the matching algorithm moved\n")
    st, said = SR.judge_one(rec)
    assert st == "STALE" and "probe_helper.py" in said, (st, said)
    assert SR.judge_one(dict(rec, code_bundle={}), root=d, bundle=False)[0] == "CURRENT", \
        "the entry-only instrument should miss exactly this, which is why it was replaced"
    k = cls(rec)
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "TOOL_CHANGED", k
    assert "probe_helper.py" in k["evidence_why"], k


def _git(d, *a, when=None):
    env = dict(os.environ)
    if when: env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    subprocess.run(["git", "-C", d, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid"] + list(a),
                   check=True, capture_output=True, env=env)


def t_an_older_reading_is_judged_by_its_imports_commit_dates_as_instants():
    """A verdict written before the bundle carries `writer` alone. Its entry is compared exactly and every module the
    entry imports today by its last commit date against the reading; a commit after the reading makes it STALE, an
    unrelated one does not, and the two clocks are compared as instants, never as text."""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except Exception:
        raise Skip("no git on this host, so no commit date can be read")
    d = tempfile.mkdtemp(prefix="bundle-git-")
    _git(d, "init", "-q")
    _write(d, "old_gate.py", "import old_helper\n")
    _write(d, "old_helper.py", "X = 1\n")
    _write(d, "old_unrelated.py", "Z = 1\n")
    _git(d, "add", "-A")
    _git(d, "commit", "-q", "-m", "one", when="2026-09-26T22:52:00+02:00")      # 20:52Z
    rec = {"tool": "old_gate", "ts": "2026-09-26T21:00:00Z",                    # after it, as an instant
           "writer": {"file": "old_gate.py", "sha16": SR.file_sha16(os.path.join(d, "old_gate.py"))}}
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()
    st, said = SR.judge_one(rec, root=d)
    assert st == "CURRENT", ("a reading at 21:00Z is after a commit at 22:52+02:00 (20:52Z)", st, said)
    _write(d, "old_unrelated.py", "Z = 2\n")
    _git(d, "commit", "-qam", "unrelated", when="2026-09-26T23:30:00+02:00")
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()
    assert SR.judge_one(rec, root=d)[0] == "CURRENT"
    _write(d, "old_helper.py", "X = 2\n")
    _git(d, "commit", "-qam", "helper", when="2026-09-26T23:40:00+02:00")
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()
    st, said = SR.judge_one(rec, root=d)
    assert st == "STALE" and said.startswith("BY PROXY") and "old_helper.py" in said, (st, said)
    # an uncommitted helper cannot be dated, and counts as changed
    _git(d, "commit", "-q", "--allow-empty", "-m", "x", when="2026-09-26T19:00:00+02:00")
    rec2 = dict(rec, ts="2026-09-27T00:00:00Z")
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()
    assert SR.judge_one(rec2, root=d)[0] == "CURRENT"
    _write(d, "old_helper.py", "X = 3\n")
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()
    st, said = SR.judge_one(rec2, root=d)
    assert st == "STALE" and "uncommitted" in said, (st, said)
    # a reading with no writer at all: the whole bundle of the tool its label names, by commit date
    rec3 = {"tool": "old_gate", "ts": "2026-09-26T21:00:00Z"}
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()
    st, said = SR.judge_one(rec3, root=d)
    assert st == "STALE" and "old_helper.py" in said, (st, said)
    SR._COMMIT_CACHE.clear(); SR._DIRTY_CACHE.clear()


def t_the_page_names_the_rows_that_changed_class_with_the_count():
    import rules_render as RR
    import test_evidence_class as EC
    A, C = S.AWAITING_REVALIDATION, S.CURRENT_CANDIDATE
    moved = dict(EC._row("TRN-001", "SCHEMATIC", "PASS", A, "TOOL_CHANGED"), board="x", writer_only_class=C,
                 writer_only_cause="BOUND", provenance_files=["kisch.py"])
    cause = dict(EC._row("SCH-001", "SCHEMATIC", "PASS", A, "TOOL_CHANGED"), board="x", writer_only_class=A,
                 writer_only_cause="NETLIST_MISMATCH")
    same = dict(EC._row("SCH-004", "SCHEMATIC", "PASS", A, "NETLIST_MISMATCH"), board="x", writer_only_class=A,
                writer_only_cause="NETLIST_MISMATCH")
    pc = S.provenance_changes([moved, cause, same])
    assert (pc["class_changed"], pc["cause_changed"], pc["rows_compared"]) == (1, 1, 3), pc
    body = RR.current_evidence_doc({"x": EC._audit("x", [moved, cause, same])}, holds={}, regs=EC.EMPTY, req={})
    sec = body.split("## Readings whose class changed when the tool identity became the code bundle")[1].split("\n## ")[0]
    assert "**1 of 3 required rows changed class; 1 more changed only their first failing cause.**" in sec, sec
    assert "TRN-001" in sec and "`kisch.py`" in sec and "SCH-001" not in sec, sec
