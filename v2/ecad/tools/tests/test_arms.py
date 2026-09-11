#!/usr/bin/env python3
"""The arm runner: width, with a prediction on every arm and a judge that is not the proposer.

MESHSAT-862, 11 September 2026. The ladders of 32.97 and 32.98 ran serially at twenty minutes an arm. The
value of a wide box is only realised if the arms are independent, predicted and graded mechanically, and the
three failures this file tests for are the three the record has already paid for:

  * an arm with no prediction (a run nobody predicted cannot disappoint, so it cannot teach anything);
  * arms sharing a project directory (routeflow experiments overwrote each other's pre-route board and three
    hours of "B15" rows were B14 routes, 6 September);
  * a grader that trusts what the arm says about itself.
"""
import os, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import arms


def t_an_arm_without_a_prediction_is_refused():
    d = tempfile.mkdtemp(prefix="arm-")
    spec = {"board": "b", "letter": "b", "source_project": "x", "placed": "p", "passes": [],
            "arms": [{"name": "good", "env": {}, "predict": {"metric": "pairs", "op": ">=", "value": 10, "basis": "the baseline"}},
                     {"name": "bare", "env": {}}]}
    f = os.path.join(d, "s.json"); json.dump(spec, open(f, "w"))
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "arms.py"), f, "--out-dir", d],
                       capture_output=True, text=True, timeout=120, cwd=d)
    assert r.returncode == 1, (r.returncode, r.stdout)
    assert "bare" in r.stdout and "no prediction" in r.stdout, r.stdout
    assert "cannot teach anything" in r.stdout, r.stdout


def t_the_judge_reads_the_measurement_not_the_arm():
    """grade() takes the pair count and the written prediction and nothing else the arm produced."""
    row = {"pairs": 60, "of": 113, "predict": {"op": ">=", "value": 56, "basis": "the measured baseline"},
           "claim": "this arm is excellent"}
    v, note = arms.grade(row)
    assert v == "MET" and "60 >= 56" in note, (v, note)
    row["pairs"] = 55
    v, note = arms.grade(row)
    assert v == "MISSED", (v, note)


def t_a_crashed_arm_is_infra_fail_not_a_missed_prediction():
    """The distinction the benchmark lost for two days: a run that could not happen is not a result."""
    v, note = arms.grade({"error": "timed out", "predict": {"op": ">=", "value": 10}})
    assert v == "INFRA_FAIL", (v, note)


def t_an_arm_that_printed_no_count_is_unmeasurable():
    v, note = arms.grade({"predict": {"op": ">=", "value": 10}})
    assert v == "UNMEASURABLE", (v, note)
    v, note = arms.grade({"pairs": 5, "predict": {}})
    assert v == "UNMEASURABLE", (v, note)


def t_each_arm_gets_its_own_project_directory():
    """Lexical, because the alternative is running two arms to prove they collided. The directory name carries
    the arm's name, which is what makes them distinct."""
    src = open(os.path.join(TOOLS, "arms.py")).read()
    assert 'os.path.join(ecad, "arm-%s-%s" % (spec["letter"], name))' in src, \
        "an arm's directory must be named after the arm, or two arms share one board"
    assert "shutil.copytree(src, dst)" in src, "each arm copies the source project rather than working in it"
