"""Record l4e11 round 19 (Layer 4 AI-scope register row (c), tasks L4A-67 and L4A-68; MESHSAT-1357, 7 October 2026;
v2/docs/records/l4e11/l4e11_rowc.py, l4e11_rowc.out, L4E11-ROUND-ROWC.md).

The predicates: the committed .out is what the script prints and every predicate it prints reads yes; the replay of 28a reproduces
section 28's printed rows from the record's own formula; the replay reads the record's windows from its own output (a window moved in
the record's text is refused, not silently replaced); a draw large enough to pull the closed loop under the powered reading makes the
20f predicate fail (the test exercises the failure mode it guards); the page carries the output's numbers and its first line states
DONE, NOT DONE and NEXT; no em or en dash in the round's files."""
import importlib.util
import math
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e11")
SCRIPT = os.path.join(REC, "l4e11_rowc.py")
OUT = os.path.join(REC, "l4e11_rowc.out")
PAGE = os.path.join(REC, "L4E11-ROUND-ROWC.md")
README = os.path.join(REC, "README.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

_C = {}


def _M():
    if "M" not in _C:
        need(SCRIPT, "record l4e11's round 19")
        sp = importlib.util.spec_from_file_location("l4e11_rowc_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C["M"] = m
    return _C["M"]


def _R():
    if "R" not in _C:
        m = _M()
        try:
            _C["R"] = m.compute()
        except m.Refused as e:
            raise AssertionError("l4e11_rowc.py refused: %s" % e)
    return _C["R"]


def t_the_committed_output_is_what_the_script_prints():
    _M()
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout.decode("utf-8") == open(OUT, encoding="utf-8").read(), "l4e11_rowc.out is stale: regenerate with _bin/regen_out.py"
    preds = r.stdout.decode().split("6. PREDICATES")[1].strip().splitlines()
    # 12 since record l8p's round 12 (the focused check's F8: the hold's stretch read from record l8p, DD-7's timeline an affected output)
    assert len(preds) == 12 and all(l.rstrip().endswith("yes") for l in preds), preds


def t_28a_reproduces_section_28s_rows_and_the_allowance_is_10cs():
    R = _R()
    assert [round(v, 3) for _x, v in R["pulled"]] == [round(v, 3) for v in R["R28"]], (R["pulled"], R["R28"])
    assert abs(R["COLD"] - 40e-6) < 1e-12 and abs(R["TRIP"] - 50e-6) < 1e-12, (R["COLD"], R["TRIP"])
    assert R["HELD"] < 0.7755 and R["DARK"][0] < 1.789 and not R["touched"]


def t_a_moved_window_in_the_record_is_refused():
    m = _M()
    real = m.read

    def fake(rel):
        t = real(rel)
        return t.replace("read powered over 1.981 V at most", "read powered over 2.981 V at most") if rel == m.RECS["e11"] else t
    m.read = fake
    try:
        try:
            m.compute()
            raise AssertionError("a moved window was not refused")
        except m.Refused as e:
            assert "powered readings" in str(e)
    finally:
        m.read = real


def t_a_draw_that_pulls_the_closed_loop_under_the_powered_reading_fails_20f():
    R = _R()
    rf = R["RF"] * 1.01
    rret = R["PAIR"] * 0.99 + R["R107"] * 0.99
    g = 1 / rf + 1 / R["R_OLOAD"] + 1 / rret
    # the draw at which the settled loop at 7.6 V reads exactly 1.981 V: any larger fails the predicate the script prints
    i_break = 7.6 / rf - 1.981 * g
    v_at = lambda i: (7.6 / rf - i) / g
    assert abs(v_at(R["COLD"]) - R["closed"][0][1]) < 1e-9
    assert v_at(i_break * 1.01) < 1.981 < v_at(R["COLD"])
    # and the rise: at a draw whose settled value is just over 1.981 V the earliest start reads under it
    v_set = 1.981 * 1.05
    assert v_set * (1 - math.exp(-0.110 / R["tau"])) < 1.981


def t_the_page_carries_the_numbers_and_states_its_status():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    first = page.splitlines()[0]
    assert first.startswith("**ROUND 19") and all(w in first for w in ("DONE", "NOT DONE", "NEXT"))
    for s in ("4.224", "5.999", "9.666", "50.8 mV", "30.4 mV", "59.5 ms", "0.404 V", "5.596", "7.928", "12.750", "4.713", "6.678",
              "10.739", "26.0 ms", "17.1 ms", "10.1 ms", "1.218 s", "1.341 s", "434.8", "520.7", "0.123 s", "85.9"):
        assert s in page, s
        assert s.split(" ")[0] in out, s
    paras = open(README, encoding="utf-8").read().rstrip("\n").split("\n\n")
    assert paras[-1].startswith("**ROUND 19") and "NEXT" in paras[-1]   # at the end: other records cite this README by line


def t_no_dashes_in_the_rounds_files():
    for p in (SCRIPT, OUT, PAGE, os.path.abspath(__file__)):
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, p
