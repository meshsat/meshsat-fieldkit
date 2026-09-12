#!/usr/bin/env python3
"""The pair report reads every shape of refusal the pre-router prints.

12 September 2026, MESHSAT-862. On B19's two contention arms the report's largest single bucket was
`(unparsed)`: 38 lines of 74 in one arm, 42 of 76 in the other. It only ever understood the per-SECTION shape
`FAIL <pair>: section A -> B (reason)`, so every whole-pair verdict fell through it, and the biggest failure
class on that board was one of those (a pair refused for its own two vias at an 0.8 mm fan pitch). The
arithmetic behind forty unlaid pairs was found by reading the raw log beside the report, which is the report
failing at the one job it has.

The rules: every shape the pre-router emits is counted under its reason, a reason bucket does not split on the
measurements inside it, and a line the tool cannot read is PRINTED rather than silently counted."""
import os, sys, subprocess, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG = """\
pair_preroute: LAID  /HDMI1_CK: 3 section(s), 41.2 mm
pair_preroute: FAIL  /ETH1_P1: section U1A -> C3 (the legs clear no smoothing of the centreline) on F.Cu,In2.Cu at w 0.13 s 0.127 (1 of 3 sections laid before it)
pair_preroute: FAIL  /ETH1_P1: section C3 -> U1A (the legs clear no smoothing of the centreline) on F.Cu,In2.Cu at w 0.13 s 0.127 (1 of 3 sections laid before it)
pair_preroute: FAIL  /SWP3_D: section C9 -> U4 (no stub path for /SWP3_D_P at U4) on F.Cu,In2.Cu at w 0.13 s 0.127 (0 of 2 sections laid before it)
pair_preroute:       0.800 mm of 0.822: the /HDMI3_D1_P via at (269.350, 22.350) against the /HDMI3_D1_N via at (269.250, 23.050)
pair_preroute: FAIL  /HDMI3_D1: its own two legs come within 0.800 mm of each other in 3 place(s) against the class clearance 0.127; rolled back, the router takes the pair
pair_preroute: FAIL  /HDMI2_D0: its own two legs come within 0.176 mm of each other in 1 place(s) against the class clearance 0.127; rolled back, the router takes the pair
pair_preroute: FAIL  /ETH2_P0: the two legs cross each other 2 time(s) on the laid path; rolled back, the router takes the pair
pair_preroute: SWAP  /SWP3_A: stations swapped
pair_preroute: TWIST /SWP3_B: the pair presents crossed at its station
pair_preroute: 1 of 8 pairs laid, 0 rip-up event(s) -> pcb-b-compute.kicad_pcb
"""


def _run(text, *args):
    d = tempfile.mkdtemp(prefix="pair-report-test-"); fn = os.path.join(d, "run.log")
    open(fn, "w").write(text)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "pair_report.py"), fn] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def t_no_failure_shape_is_unparsed():
    rc, out = _run(LOG)
    assert rc == 0, out
    assert "(unparsed)" not in out, "a shape the pre-router emits is not read by its own report:\n" + out


def t_a_whole_pair_refusal_is_counted_under_its_reason():
    rc, out = _run(LOG)
    assert "its own two legs come within N mm of each other in N place(s)" in out, out
    assert "the two legs cross each other N time(s)" in out, out


def t_one_reason_does_not_split_on_its_measurements():
    """0.800 mm and 0.176 mm are the same refusal for the same cause, and counting them apart hides the cause:
    the bucket that mattered on B19 was 36 lines of one reason with 36 different numbers in it."""
    rc, out = _run(LOG)
    line = [l for l in out.splitlines() if "own two legs come within" in l][0]
    assert line.strip().startswith("2 "), "the two own-legs refusals were counted as separate reasons: " + line


def t_a_section_failure_still_names_the_part_it_died_at():
    rc, out = _run(LOG)
    assert "U4" in out, out
    i = out.index("failures by the part")
    assert "(whole pair)" in out[i:], "a whole-pair refusal has no part, and saying so is the honest column"


def t_a_line_the_tool_cannot_read_is_printed():
    rc, out = _run(LOG + "pair_preroute: FAIL  something entirely new\n".replace("FAIL  something", "FAILX something"))
    assert rc == 0, out
    rc, out = _run("pair_preroute: FAIL  no colon here at all\n")
    assert "cannot read" in out and "no colon here" in out, \
        "an unreadable line is counted in silence, which is how the biggest bucket became (unparsed):\n" + out
