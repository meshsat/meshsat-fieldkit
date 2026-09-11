#!/usr/bin/env python3
"""The verdict channel: every gate decides in a file, and no driver decides by reading prose.

This is stage 0a of the control-plane programme (MESHSAT-862, 11 September 2026, `v2/docs/CONTROL-PLANE.md`).
Before it, eighteen gates announced their decision on stdout and thirteen drivers recovered it with
`grep -q 'RESULT: ALL PASS'`, which meant:

  * every finish ran its board gate TWICE, the second time only to produce a string to match;
  * a gate that crashed before printing its last line was indistinguishable from a gate that failed;
  * a gate that checked nothing printed exactly what a gate that checked everything and passed printed.

The rules below are lexical on purpose. They hold without pcbnew, without a board and without a box, which is
what lets them run on every host; and a lexical rule catches the reintroduction of the old shape in a new file,
which is the failure mode a one-off repair always has.
"""
import os, re, json, glob, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import verdict

# The gates named by the programme: each decides something a driver or a human acts on.
GATES = ["check_pcb_a.py", "check_pcb_b.py", "check_pcb_c.py", "check_pcb_d.py", "check_pcb_e.py",
         "check_pcb_p.py", "hardset.py", "impedance_check.py", "dc_drop.py", "check_contracts.py",
         "check_zone_nets.py", "intent_checks.py", "place_audit.py", "erc_gate.py",
         "verify_deliverable.py", "pruned_gate.py", "lcsc_fill.py"]

WRITES = re.compile(r"\b(?:verdict|_v)\.write\s*\(")
IMPORTS = re.compile(r"^\s*import verdict(?: as _v)?\s*$", re.M)
GREP_PROSE = re.compile(r"grep\s+-q\S*\s+\S*RESULT: ALL PASS")


def _shell_lines():
    for p in sorted(glob.glob(os.path.join(TOOLS, "*.sh"))):
        for n, line in enumerate(open(p, errors="replace"), 1):
            yield os.path.basename(p), n, line


def t_every_gate_writes_a_verdict():
    missing = [g for g in GATES if not WRITES.search(open(os.path.join(TOOLS, g)).read())]
    assert not missing, "these gates still decide only on stdout: %s" % missing


def t_every_gate_that_writes_a_verdict_imports_the_writer():
    """Compiling proves nothing here: `verdict.write(...)` in a file with no import is a NameError at the
    moment the gate decides, which is the one moment nobody is watching. erc_gate.py shipped exactly that
    for the length of one test run on 11 September 2026."""
    bad = []
    for g in GATES:
        s = open(os.path.join(TOOLS, g)).read()
        if WRITES.search(s) and not IMPORTS.search(s): bad.append(g)
    assert not bad, "these call the verdict writer without importing it: %s" % bad


def t_no_driver_decides_by_grepping_a_gates_prose():
    """The rule, not the instance: no shell script may branch on a gate's human-readable summary line."""
    bad = ["%s:%d" % (f, n) for f, n, line in _shell_lines() if GREP_PROSE.search(line)]
    assert not bad, "a driver still reads a verdict out of prose: %s" % bad


def t_no_driver_runs_a_board_gate_twice_on_one_line():
    """Two invocations of one check_pcb_* on a single line is the double-run shape: one to print, one to test."""
    bad = ["%s:%d" % (f, n) for f, n, line in _shell_lines()
           if not line.lstrip().startswith("#") and len(re.findall(r"check_pcb_[a-z]\.py", line)) > 1]
    assert not bad, "a driver runs its board gate twice: %s" % bad


def t_every_hardset_judgement_is_labelled():
    """hardset writes one verdict file per label. A finish makes three judgements with it (after the stub
    router, after stub_accept, the routed-board gate) and a fourth in the deliverable; unlabelled, they all
    land on out/hardset.verdict.json and only the last one survives to be read."""
    bad = []
    for f, n, line in _shell_lines():
        if line.lstrip().startswith("#"): continue
        for call in re.findall(r"hardset\.py\s[^|;)]*", line):
            if "--label" in call: continue
            if any(k in call for k in ("--score", "--counts", "--gate", "--flag")):
                bad.append("%s:%d %s" % (f, n, call.strip()[:60]))
    assert not bad, "an unlabelled hardset judgement would overwrite another's verdict: %s" % bad


def t_an_unrecognised_verdict_is_never_a_pass():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    assert verdict.write("t", "ALL PASS", out_dir=d, quiet=True) == verdict.USAGE
    assert verdict.write("t", True, out_dir=d, quiet=True) == verdict.USAGE
    assert verdict.write("t", None, out_dir=d, quiet=True) == verdict.USAGE
    assert not os.path.exists(os.path.join(d, "t.verdict.json")), "a rejected verdict must write nothing"


def t_a_missing_verdict_reads_back_inconclusive():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    rec, code = verdict.read(os.path.join(d, "nothing.verdict.json"))
    assert rec["verdict"] == verdict.INCONCLUSIVE and code == 3, (rec, code)
    open(os.path.join(d, "junk.verdict.json"), "w").write("{not json")
    rec, code = verdict.read(os.path.join(d, "junk.verdict.json"))
    assert rec["verdict"] == verdict.INCONCLUSIVE and code == 3, (rec, code)
    json.dump({"verdict": "probably fine"}, open(os.path.join(d, "odd.verdict.json"), "w"))
    rec, code = verdict.read(os.path.join(d, "odd.verdict.json"))
    assert code == 3, (rec, code)


def t_the_denominator_travels_with_every_verdict():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    verdict.write("t", verdict.PASS, counts={"fail": 0}, denominator=0, out_dir=d, quiet=True)
    rec = json.load(open(os.path.join(d, "t.verdict.json")))
    assert "denominator" in rec and rec["denominator"] == 0, rec
    assert rec["version"] and rec["ts"], "a verdict names the code and the moment that produced it"


def t_the_exit_code_equals_the_verdict():
    d = tempfile.mkdtemp(prefix="verdict-test-")
    assert verdict.write("t", verdict.PASS, out_dir=d, quiet=True) == 0
    assert verdict.write("t", verdict.FAIL, out_dir=d, quiet=True) == 1
    assert verdict.write("t", verdict.INCONCLUSIVE, out_dir=d, quiet=True) == 3
