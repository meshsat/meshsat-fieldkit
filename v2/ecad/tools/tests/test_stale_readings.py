#!/usr/bin/env python3
"""Which readings were taken under a tool that has changed since (a report, MESHSAT-862, 20 September 2026).

Staleness has been asked rule by rule since 17 September, from the per-rule digests a verdict carries, and
that catches a change to `pcb_rules.yaml`. It cannot catch a change to the TOOL, because a tool change moves
no fingerprint. `check_pcb_b` was corrected on 19 September to REPORT a half-routed pair rather than fail it;
board B's MEC-001 went on reading FAIL on 21 of them for nineteen hours, with a current rule-set fingerprint
and current per-rule digests, and nothing on any page could say the reading predated the fix. These rules
hold the two halves of the answer: a verdict records the FILE that wrote it and that file's own hash, and the
report names a reading whose file has changed since. It decides nothing, because a tool change says a reading
is OWED and not that it would come out differently."""
import os, sys, json, tempfile, hashlib

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict as _v
import stale_readings as S


def t_a_verdict_records_the_file_that_wrote_it_and_its_hash():
    """THE MECHANISM. Proved to fail on the tree it was written against: before this change `verdict.write`
    recorded `tools`, the hash of the WHOLE tools tree, which moves whenever any tool changes and so cannot
    tell the deciding tool apart from any other."""
    src = open(os.path.join(TOOLS, "verdict.py"), encoding="utf-8").read()
    assert "def _writer(" in src, "verdict.py records no writer, so staleness can only be asked of the whole tree"
    assert '"writer": _writer()' in src, "the writer is computed and not written into the record"
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, "probe_tool.py")
        open(script, "w").write(
            "import sys, os\n"
            "sys.path.insert(0, %r)\n" % TOOLS +
            "import verdict as v\n"
            "v.write('probe', v.PASS, counts={'x': 1}, denominator=1, out_dir=%r, quiet=True)\n" % d)
        import subprocess
        subprocess.run([sys.executable, script], check=True, capture_output=True)
        rec = json.load(open(os.path.join(d, "probe.verdict.json")))
        w = rec.get("writer") or {}
        assert w.get("file") == "probe_tool.py", w
        assert w.get("sha16") == hashlib.sha256(open(script, "rb").read()).hexdigest()[:16], w


def t_a_reading_whose_tool_has_changed_is_named():
    """THE DEFECTIVE FIXTURE: the exact instrument, a writer hash that no longer matches the file."""
    name = os.path.basename(sorted(f for f in os.listdir(TOOLS) if f.endswith(".py"))[0])
    rec = {"tool": "anything", "ts": "2026-09-20T00:00:00Z",
           "writer": {"file": name, "sha16": "0000000000000000"}}
    state, said = S.judge_one(rec)
    assert state == "STALE", (state, said)
    assert name in said and "has changed since" in said, said


def t_a_reading_whose_tool_is_untouched_is_not_named():
    """THE ACCEPTABLE FIXTURE: the same shape with the file's real hash."""
    name = os.path.basename(sorted(f for f in os.listdir(TOOLS) if f.endswith(".py"))[0])
    rec = {"tool": "anything", "ts": "2026-09-20T00:00:00Z",
           "writer": {"file": name, "sha16": S.file_sha16(os.path.join(TOOLS, name))}}
    state, said = S.judge_one(rec)
    assert state == "CURRENT", (state, said)


def t_a_reading_that_names_no_writer_is_answered_by_a_proxy_that_says_it_is_one():
    """Every verdict written before 20 September carries no writer, so the fallback compares the reading's
    timestamp with the deciding tool's last COMMIT date. It is right about the order of events and silent
    about whether the change touched this measurement, and it must say so in its own sentence."""
    rec = {"tool": "verdict", "ts": "2020-01-01T00:00:00Z"}
    state, said = S.judge_one(rec)
    assert state in ("STALE", "UNKNOWN"), (state, said)
    if state == "STALE":
        assert said.startswith("BY PROXY"), said
        assert "not said" in said or "is not said" in said, said


def t_a_reading_the_report_cannot_name_a_file_for_is_UNKNOWN_and_never_current():
    """Absence is never a pass here either: a verdict whose deciding file cannot be named is not reported as
    up to date, it is reported as unaskable with the reason."""
    state, said = S.judge_one({"tool": "no_such_tool_exists_anywhere", "ts": "2026-09-20T00:00:00Z"})
    assert state == "UNKNOWN", (state, said)
    assert "cannot be named" in said, said


def t_it_decides_nothing():
    """A tool change is not evidence about a board. A gate here would refuse boards for the age of their
    paperwork, which is the opposite of what the finding asks for."""
    src = open(os.path.join(TOOLS, "stale_readings.py"), encoding="utf-8").read()
    assert "advisory=True" in src, "the report is not advisory, so it could decide a rule by accident"
    assert "_v.PASS" in src.split("return _v.write")[1][:120], "the report can return a non-PASS verdict"
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out"); os.makedirs(out)
        env = os.environ.get("VERDICT_DIR"); os.environ["VERDICT_DIR"] = out
        try:
            rc = S.main([d])
        finally:
            if env is None: os.environ.pop("VERDICT_DIR", None)
            else: os.environ["VERDICT_DIR"] = env
        assert rc == 0, rc
        v = json.load(open(os.path.join(out, "stale_readings.verdict.json")))
        assert v["verdict"] == "PASS" and v["advisory"] is True, v
