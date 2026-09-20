"""A pour born without a via refuses the placement (21 September 2026).

place_audit's island line was a WARN and it named board A's defect on every chain from A87 to A92: each rail's
In3 run ended in a column KiCad had renamed to GND (it sat in the load capacitor's ground pad), so the six load
bank islands carried no via of their own net before any route and the run dead-ended a layer below them. The
WARN was printed six times and read by nobody. Measured across the set before the bar moved: zero on every clean
chain (A85, A86, A93, B23, C24, D27, D30, E30, P9), 6 to 9 on exactly the defective arms, one VBAT In2 piece on
A69 and A70. So the line is a refusal now, with the erc-allow idiom (`pour-island-allow.txt` beside the board
names a net and says why).
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(os.path.dirname(HERE), "place_audit.py"), encoding="utf-8").read()


def t_an_islanded_pour_before_the_route_is_a_refusal_and_not_a_warning():
    body = SRC[SRC.index("    if _isl:"):SRC.index("    elif _zones and not _unfilled:")]
    assert "WARN  %d pour island(s) already carry no via" not in body, "the islanded pour is still a warning nobody reads"
    assert 'lines.append("FAIL  %d pour island(s) already carry no via or plated pad of their own net BEFORE any' in body, \
        "the islanded pour does not fail the placement"
    assert "coll += 1" in body, "the refusal does not reach the verdict: coll is what decides place_audit's exit"


def t_a_known_island_is_declared_beside_the_board_and_still_counted():
    body = SRC[SRC.index("    if _isl:"):SRC.index("    elif _zones and not _unfilled:")]
    assert 'pour-island-allow.txt' in body, "there is no way to declare a known islanded pour"
    assert 'lines.append("ALLOW %d pour island(s)' in body, "an allowed island is not reported"
    # the allow line names the NET, matched against the island's own "<net> on <layer>" prose, never a substring of a reason
    assert 'i.split(" on ")[0] == l.split()[0].lstrip("/")' in body, "an allow line does not match on the net name"
    # and no board of the set declares one today: the count is zero on every clean chain, which is the measurement
    for L in "abcdep":
        for d in os.listdir(os.path.join(os.path.dirname(HERE), "..")):
            if d.startswith("pcb-") and os.path.isfile(os.path.join(os.path.dirname(HERE), "..", d, "pour-island-allow.txt")):
                raise AssertionError("%s declares an islanded pour; the set read zero when the bar moved, so say why in the file and here" % d)
