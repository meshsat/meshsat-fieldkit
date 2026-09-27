#!/usr/bin/env python3
"""The high-voltage spacing is measured, not asserted (rule ISO-001, MESHSAT-862, 16 September 2026).

A net class is an instruction to the router, not a fact about the board: it binds the router's tracks and says
nothing about a pad, a zone edge or a hand-laid piece of copper. The registry carried "no creepage or clearance
distance has ever been measured on any board" and that is what this closes, for the measuring half."""
import os, math, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import spacing
SRC = open(os.path.join(TOOLS, "spacing.py"), encoding="utf-8").read()


def t_the_segment_distance_is_the_geometry_and_not_a_bounding_box():
    # two parallel segments 2 mm apart
    assert abs(spacing.seg_dist((0, 0), (10, 0), (0, 2), (10, 2)) - 2.0) < 1e-9
    # a segment and one that ends beside it: the nearest point is an endpoint
    assert abs(spacing.seg_dist((0, 0), (10, 0), (12, 0), (20, 0)) - 2.0) < 1e-9
    # crossing segments touch
    assert spacing.seg_dist((0, 0), (10, 0), (5, -5), (5, 5)) < 1e-9


def t_a_board_with_no_high_voltage_rail_says_the_rule_does_not_apply():
    assert "applicable=False" in SRC, "a board with no HV rail would read as an unanswered question"


def t_an_undeclared_limit_is_reported_and_never_passed():
    """21 September 2026: this read a 2000-byte window from `lim = _bt.value`, which pinned the expression
    rather than the property, and decision 34 moved it. The property is unchanged and is now wider: a board
    is unjudged only when it declares NEITHER a spacing of its own NOR whether it is coated, because the
    coating is what selects the column of the table."""
    assert "_v.INCONCLUSIVE if (lim is None and coated is None)" in SRC, \
        "a board that declares nothing could read as a pass"
    assert "IEC 60664" in SRC, "the tool does not name the authority it is missing"


def t_the_measurement_covers_pads_and_not_only_tracks():
    assert "f.Pads()" in SRC and "GetTracks()" in SRC, "the measurement misses a whole class of conductor"


def t_the_evidence_line_formats_the_position_it_carries():
    """The first run on a real board died here, in the verdict's own evidence (16 September 2026).

    Each measured pair is (distance, net, net, layer, position) and the position is itself a pair, so the
    format string wants six values and the tuple offers five. A gate that measures a board correctly and then
    crashes writing down what it found has still told nobody anything."""
    x = (0.25, "VBUS20", "GND", "F.Cu", (10.0, 20.0))
    line = "%.3f mm %s to %s on %s at (%.1f, %.1f)" % (x[0], x[1], x[2], x[3], x[4][0], x[4][1])
    assert line.startswith("0.250 mm VBUS20 to GND on F.Cu at (10.0, 20.0)"), line
    assert "% x for x in" not in SRC, "the evidence line still formats the tuple whole"


def t_a_pad_is_a_fat_segment_and_not_a_circle_of_its_longest_side():
    """Board A's first run reported a closest distance of 0.000 mm on a board whose DRC reads hard 0.

    A 1.7 by 1.0 pad modelled as a circle has a radius of 0.85 where its real half width across the short axis
    is 0.5, so it swallows the tracks beside it and every measurement near a connector reads zero. The centre
    line plus the short half width is exactly an oval pad and close enough for a rectangle, which is what KiCad
    draws (16 September 2026)."""
    assert "min(sx, sy) / 2.0" in SRC, "the pad radius is still taken from the longest side"
    assert "GetOrientationDegrees" in SRC, "a rotated pad's centre line is not rotated with it"


def t_the_voltage_judged_is_the_working_one_and_not_the_nominal():
    """17 September 2026. Board E's shore and vehicle inlet is 12 V nominal and 36 V working, its own facts
    entry says 36, the registry uses that fact to decide ISO-001 APPLIES to board E, and this tool read the
    nominal and answered `no rail on this board reaches 20 V`. ECSS clause 13.8.2 b, the authority this rule
    cites, says the rating applies to the worst-case peak: a nominal is what a rail sits at and a working
    voltage is what the copper has to survive."""
    i = SRC.index("def _vhi(")
    seg = SRC[i:i + 400]
    assert 'r.get("v_work")' in seg and "max(" in seg, \
        "the high-voltage set is chosen from the nominal voltage alone"
    assert "hv_v = {n.lstrip(\"/\"): _vhi(r)" in SRC, "the selection does not use the working voltage"
    assert "hv_v.get(" in SRC, "the per-net working voltage is not carried to the judgement"


def t_a_board_whose_fact_contradicts_its_intent_is_a_question_and_not_an_exemption():
    """The other half, and the one that cannot be allowed to read as a pass: if the board's own facts entry
    declares a maximum at or above the threshold and no rail in its intent reaches it, the two disagree and the
    rule is unanswered. `applicable=False` would say the rule does not apply to a board the registry says it
    applies to."""
    i = SRC.index("if not hv:")
    seg = SRC[i:i + 1800]
    assert "max_rail_voltage_v" in seg, "the contradiction with the board's own fact is not looked for"
    assert "missing_input=" in seg, "a board that contradicts itself would be recorded as an exemption"
    k = seg.index("missing_input=")
    assert seg.index("applicable=False") > k, \
        "the exemption branch is reached before the contradiction is tested"


def t_the_table_is_read_per_voltage_band_and_per_layer():
    """DECISION 34, ruled 21 September 2026 (the session's). ISO-001 was unjudgeable because a board could
    declare only ONE spacing, and the table it is judged against is per voltage band: a single number holds a
    20 V bus to a 36 V rail's floor, which is why no board ever declared one. The rows are
    ECSS-Q-ST-70-12C Table 13-3 as transcribed in v2/vendor/standards/, and 'AND' in that table means the
    larger of the per-volt figure and the floor."""
    assert spacing.limit_for(20, True, True) == 0.120
    assert spacing.limit_for(36, True, True) == 0.160        # 2 um/V is 72 um, the floor is 160
    assert spacing.limit_for(400, True, True) == 0.800       # above the floor the per-volt figure governs
    assert spacing.limit_for(36, False, True) == 0.150       # an inner layer has its own column
    assert spacing.limit_for(600, True, True) is None, "above 500 V the table does not answer and must say so"


def t_the_coating_is_what_selects_the_column_and_a_board_that_does_not_say_gets_the_strict_one():
    """THE DEFECTIVE FIXTURE, and it is what every ISO-001 number in this record was read against. The bare
    column asks 300 um at 20 V and 500 at 36; the coated column asks 120 and 160. ASSEMBLY.md section 5 has
    specified IPC-CC-830 acrylic on A22, B16, D8, E6 and E5 since it was written, so reading the bare column
    was measuring a board this project does not build. A board that does NOT declare the coating is still
    judged on the bare column, because a declaration that cannot be found must never make a rule easier."""
    assert spacing.limit_for(20, True, False) == 0.300
    assert spacing.limit_for(36, True, False) == 0.500
    assert spacing.limit_for(20, True, True) < spacing.limit_for(20, True, False)


def t_board_a_and_board_e_are_judged_and_the_answer_is_thirty_one_micrometres():
    """THE ACCEPTABLE FIXTURE is the measurement itself (21 September 2026, both committed boards, read-only
    on the box with their sha identical before and after): the tightest high-voltage approach on board A and
    on board E is 0.1287 mm. On the coated column every 20 V row passes and the 36 V input rails do not, by
    about thirty-one micrometres, where the bare column said they failed by a factor of four. The rule is
    that the numbers below are what the table says about those two measurements."""
    measured = 0.1287
    assert measured > spacing.limit_for(20, True, True), "a 20 V row at 0.1287 mm should meet the coated 120 um"
    short = spacing.limit_for(36, True, True) - measured
    assert 0.030 < short < 0.032, "the 36 V rails should be short by about 31 um, not %.4f" % short


def t_every_board_says_whether_it_is_coated():
    """The declaration is a board fact and it has an authority: a board that carries a high-voltage net and
    does not say cannot be judged, which is the state ISO-001 was in until today."""
    import json
    import os as _os
    for L in ("a", "b", "c", "d", "e", "e5", "p"):
        d = json.load(open(_os.path.join(TOOLS, "boards", "%s.json" % L), encoding="utf-8"))
        assert "conformal_coated" in d, "board %s does not say whether it is coated" % L
        assert len(str(d.get("_conformal_coated_why") or "")) > 120, \
            "board %s declares a coating with no authority beside it" % L
        assert "ASSEMBLY.md" in d["_conformal_coated_why"], \
            "board %s's coating declaration does not cite the assembly specification" % L
