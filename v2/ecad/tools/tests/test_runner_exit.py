"""tests/run.py lets no test end the run (MESHSAT-1357, set 31, stream W31; item 2 of the integrator's row Q-41, 6 October 2026).

On 6 October 2026 the first box pass of set 30 died at record l8r2's refusal: a record's generator called `sys.exit(2)` under a
test, `run.py` caught only `Exception` around each test, the `SystemExit` left `main` and the interpreter, and 126 of 236 modules
never ran, so the promotion gate had no totals line to judge. The properties held here, each on a COPY of this directory's
`run.py` (with `harness.py`, which it imports) run in a subprocess inside a temporary directory, never this tree: the real runner
globs `test_*.py` beside itself and would load the fixtures. The copy sits at `<tmp>/tools/tests/` so that the evidence check of
`run.py` (it reads `<tests>/../../out`) looks inside the temporary directory and nowhere else.

- a test that calls `sys.exit(2)` reads `FAIL SystemExit(2)` with its traceback, a module that sorts AFTER it still runs and
  reads PASS, the totals read `1 passed, 1 failed`, and the exit status is 1;
- a module whose IMPORT calls `sys.exit(3)` reads `LOAD FAILED SystemExit(3)` and the run continues the same way;
- a `KeyboardInterrupt` still interrupts the run (the correction catches `SystemExit`, never `BaseException`).

The fixture that runs after the exiting one is `test_zzz_after.py`, not the `test_zz_after.py` of the stream's brief: that name
sorts BEFORE `test_zz_exits.py` ('a' before 'e'), so it would run before the exit and prove nothing about the run continuing
(taken by the stream under the owner's standing rule of 26 September 2026; the first test asserts the order).

OBSERVED AGAINST THE OLD run.py (base dd1aed00), this module run through `tests/run.py` itself on the runner on 6 October 2026
at 11:41 CEST, its result lines verbatim (the old copy printed NOTHING, not even a totals line, and exited with the test's own
code; the KeyboardInterrupt property passed there too, as it must: it guards the correction, not the defect):

    tests: test_runner_exit.t_a_keyboard_interrupt_still_interrupts_the_run PASS
    tests: test_runner_exit.t_a_module_whose_import_calls_sys_exit_is_a_load_failure_and_the_run_continues FAIL exit status 3; stdout []; stderr ''
    tests: test_runner_exit.t_a_test_that_calls_sys_exit_is_a_failure_and_the_run_continues FAIL exit status 2; stdout []; stderr ''
    tests: 1 passed, 2 failed, 0 skipped; failed: test_runner_exit.t_a_module_whose_import_calls_sys_exit_is_a_load_failure_and_the_run_continues, test_runner_exit.t_a_test_that_calls_sys_exit_is_a_failure_and_the_run_continues
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

EXITS = "import sys\n\n\ndef t_exits():\n    sys.exit(2)\n"
IMPORT_EXITS = "import sys\n\nsys.exit(3)\n\n\ndef t_never_reached():\n    pass\n"
INTERRUPTS = "def t_interrupts():\n    raise KeyboardInterrupt\n"
AFTER = "def t_runs_after():\n    pass\n"


def _run_copy(fixtures):
    """Copy run.py and harness.py beside the fixture modules {name: source} in a temporary directory, run the copy there in a
    subprocess and return (exit status, stdout lines, stderr); the directory is removed afterwards."""
    d = tempfile.mkdtemp(prefix="runexit-")
    try:
        t = os.path.join(d, "tools", "tests")
        os.makedirs(t)
        for name in ("run.py", "harness.py"):
            shutil.copyfile(os.path.join(HERE, name), os.path.join(t, name))
        for name, src in fixtures.items():
            with open(os.path.join(t, name), "w", encoding="utf-8") as f:
                f.write(src)
        r = subprocess.run([sys.executable, "-B", "-u", os.path.join(t, "run.py")], cwd=t, capture_output=True, text=True,
                           timeout=120)
        return r.returncode, r.stdout.splitlines(), r.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _index(lines, prefix, word):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix) and word in l]
    return hits[0] if hits else -1


def t_a_test_that_calls_sys_exit_is_a_failure_and_the_run_continues():
    assert sorted(["test_zz_exits.py", "test_zzz_after.py"])[0] == "test_zz_exits.py"
    rc, out, err = _run_copy({"test_zz_exits.py": EXITS, "test_zzz_after.py": AFTER})
    seen = "exit status %r; stdout %r; stderr %r" % (rc, out, err[-600:])
    assert rc == 1, seen
    i_fail = _index(out, "tests: test_zz_exits.t_exits", "FAIL SystemExit(2)")
    assert i_fail >= 0, seen
    i_pass = _index(out, "tests: test_zzz_after.t_runs_after", "PASS")
    assert i_pass > i_fail, seen
    tot = [l for l in out if l.startswith("tests: ") and " passed, " in l]
    assert tot and tot[-1].startswith("tests: 1 passed, 1 failed, 0 skipped") and "test_zz_exits.t_exits" in tot[-1], seen
    assert "Traceback (most recent call last)" in err and "SystemExit: 2" in err, seen


def t_a_module_whose_import_calls_sys_exit_is_a_load_failure_and_the_run_continues():
    rc, out, err = _run_copy({"test_zz_import_exits.py": IMPORT_EXITS, "test_zzz_after.py": AFTER})
    seen = "exit status %r; stdout %r; stderr %r" % (rc, out, err[-600:])
    assert rc == 1, seen
    i_fail = _index(out, "tests: test_zz_import_exits.py", "LOAD FAILED SystemExit(3)")
    assert i_fail >= 0, seen
    assert _index(out, "tests: test_zz_import_exits.t_", "") < 0, seen
    i_pass = _index(out, "tests: test_zzz_after.t_runs_after", "PASS")
    assert i_pass > i_fail, seen
    tot = [l for l in out if l.startswith("tests: ") and " passed, " in l]
    assert tot and tot[-1].startswith("tests: 1 passed, 1 failed, 0 skipped") and "test_zz_import_exits.py" in tot[-1], seen


def t_a_keyboard_interrupt_still_interrupts_the_run():
    rc, out, err = _run_copy({"test_zz_interrupts.py": INTERRUPTS, "test_zzz_after.py": AFTER})
    seen = "exit status %r; stdout %r; stderr %r" % (rc, out, err[-600:])
    assert rc not in (0, 1), seen
    assert _index(out, "tests: test_zzz_after.", "") < 0, seen
    assert not [l for l in out if l.startswith("tests: ") and " passed, " in l], seen
    assert "KeyboardInterrupt" in err, seen
