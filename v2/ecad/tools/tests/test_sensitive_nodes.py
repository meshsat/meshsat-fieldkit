#!/usr/bin/env python3
"""The nodes where a few millivolts change the answer (rule ANA-001, 16 September 2026).

The rule asks for the list per board with each node's filter, its clearance from switching nodes and the Kelvin
connections where the measurement demands one. It read "generation intends to comply and nothing verifies it"
on four boards.

Writing the list found a real defect on board A within the hour. The BQ25731's own pin table asks for an RC
filter between each sense resistor and its pin, 10 Ohm with 10 nF differential on the input pair (section
10.2.2.2, a 47 to 200 ns time constant) and a 10 Ohm contact resistor with 0.1 uF across the charge sense
resistor (pin 19). Both pairs went straight from the shunt to the pin, which is the case the datasheet warns
"overwhelms converter sensed inductor current information" and can push the average-current loop into
oscillation. Six parts were added at the source.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import sensitive_nodes as S

GOOD = """
schema_version: "1.0.0"
boards:
 x:
   switch_nets: ["*_SW"]
   nodes:
    - {net: A_SENSE, what: "a shunt sense", filter: "10 R and 10 nF", kelvin_with: B_SENSE, keep_mm: 0.5}
    - {net: B_SENSE, what: "the other half", filter: "10 R and 10 nF", kelvin_with: A_SENSE, keep_mm: 0.5}
"""


def _sheet(body):
    d = tempfile.mkdtemp(prefix="ana-")
    p = os.path.join(d, "s.yaml"); open(p, "w").write(body); return p


def t_a_one_sided_kelvin_declaration_is_refused():
    """A pair is a pair: if A names B, B must name A. This is what caught the board A list on its first run."""
    body = GOOD.replace('    - {net: B_SENSE, what: "the other half", filter: "10 R and 10 nF", kelvin_with: A_SENSE, keep_mm: 0.5}\n', "")
    r = S.judge(None, "x", _sheet(body))
    assert any("not declared" in f for f in r["fails"]), r["fails"]
    body2 = GOOD.replace("kelvin_with: A_SENSE", "kelvin_with: null")
    r2 = S.judge(None, "x", _sheet(body2))
    assert any("one-sided" in f for f in r2["fails"]), r2["fails"]


def t_a_node_with_no_filter_is_refused():
    r = S.judge(None, "x", _sheet(GOOD.replace('filter: "10 R and 10 nF"', 'filter: ""', 1)))
    assert any("carries no filter" in f for f in r["fails"]), r["fails"]


def t_the_acceptable_fixture_passes():
    r = S.judge(None, "x", _sheet(GOOD))
    assert not r["fails"], r["fails"]


def t_a_board_with_no_list_is_inconclusive_and_not_a_pass():
    r = S.judge(None, "zz", _sheet(GOOD))
    assert r["applicable"] is False, r


def t_board_a_carries_the_charger_sense_filters_the_datasheet_asks_for():
    """The finding itself, held as a rule: the BQ25731's sense pairs reach their pins through a filter, and the
    list names it. A regeneration that dropped those six parts would fail here."""
    src = open(os.path.join(TOOLS, "gen_sch_a.py"), encoding="utf-8").read()
    for net in ("CH_ACN_F", "CH_ACP_F", "CH_SRN_F", "CH_SRP_F"):
        assert net in src, "board A no longer filters %s" % net
    # The parts, by reference and by the nets they join, never by their value prose. The first version of this
    # rule asserted the strings "10R (SRN contact resistor" and "10n (CDIFF across the input sense", which is
    # the one thing about these six parts that had to change: a value is the BOM's Comment column, and a
    # comment no code rule matches is a blank BOM line the finish refuses. The reasoning lives in comments now.
    for call in ('r("R146", "10R", "CH_ACN", "CH_ACN_F")', 'r("R147", "10R", "VBUS20", "CH_ACP_F")',
                 'c("C121", "10n", "CH_ACP_F", "CH_ACN_F")', 'r("R148", "10R", "CELL+", "CH_SRN_F")',
                 'r("R149", "10R", "CH_SRP", "CH_SRP_F")', 'c("C122", "100n", "CH_SRP_F", "CH_SRN_F")'):
        assert call in src, "the charger sense filter lost %s" % call
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_sensitive.yaml"), encoding="utf-8"))
    nets = {n["net"] for n in d["boards"]["a"]["nodes"]}
    assert {"CH_ACN_F", "CH_ACP_F", "CH_SRN_F", "CH_SRP_F"} <= nets, sorted(nets)


def t_the_committed_lists_pass_the_netlist_half():
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_sensitive.yaml"), encoding="utf-8"))
    for letter in d["boards"]:
        r = S.judge(None, letter)
        assert not r["fails"], (letter, r["fails"])


def t_a_clearance_is_a_same_layer_question():
    """16 September 2026, from the first measured run: board A's FE_CS was reported as running -0.212 mm from
    the switch node, a negative gap, because the sense line runs UNDER it on another layer. Copper on two
    layers cannot be 0.2 mm apart in the plane and touching; the layer case is coupling through the
    dielectric, which is a different question and is reported rather than folded into a number that cannot
    mean what it says."""
    src = open(os.path.join(TOOLS, "sensitive_nodes.py"), encoding="utf-8").read()
    assert "m[3] is None or o[3] is None or m[3] == o[3]" in src, "the clearance test ignores the layer again"
    assert "runs under" in src, "a cross-layer overlap is no longer reported at all"
    i, j = src.index("def _copper"), src.index("def _seg_distance")
    assert "t.GetLayer()" in src[i:j], "the copper is collected without its layer"


# ---------------------------------------------------------------------------------------------------------
# WHERE THE APPROACH HAPPENS DECIDES WHAT IT IS (rule ANA-001, 17 September 2026).
#
# A current-sense line and the switching node it measures are adjacent BY CONSTRUCTION at the part that makes
# both: a FET's source is CS and its drain is SW, two pins of one package, and no router separates them. The
# gate reported the smallest gap and failed board A on six nodes, four of which were that geometry. The split
# is the part's own COURTYARD, which is published geometry and not a number this project invented: copper
# inside it is the package, copper outside it is a routing decision.

def t_a_point_inside_a_courtyard_box_is_inside_it():
    import sensitive_nodes as S
    box = (10.0, 20.0, 14.0, 23.0)
    assert S.inside_any((12.0, 21.0), [box]) is True
    assert S.inside_any((10.0, 20.0), [box]) is True, "a point on the edge is inside the part"
    assert S.inside_any((14.5, 21.0), [box]) is False
    assert S.inside_any((12.0, 21.0), []) is False, "no courtyard means nothing is inside one"
    assert S.inside_any((12.0, 21.0), [None]) is False, "a part that draws no courtyard contains nothing"


def t_a_box_given_in_either_corner_order_still_contains_its_points():
    import sensitive_nodes as S
    assert S.inside_any((12.0, 21.0), [(14.0, 23.0, 10.0, 20.0)]) is True


def t_the_reported_run_is_split_into_inside_and_outside():
    """The verdict has to carry both, because the two mean different things and a single number cannot say
    which one it is. This is the shape the measurement travels in."""
    import inspect, sensitive_nodes as S
    src = inspect.getsource(S.judge)
    for key in ("run_inside_the_shared_part_mm", "run_outside_it_mm"):
        assert key in src, "the measurement no longer reports %s" % key
    assert "_run_out > 1e-9" in src, "the failure is no longer decided by the copper outside the part"


def t_an_empty_switch_list_with_no_reason_is_not_a_pass():
    """THE DEFECTIVE FIXTURE. Board P declares seven sensitive nodes and `switch_nets: []`, so nothing is
    measured against anything and the verdict read PASS of 7 with 0 measured: STK-001's "PASS on a denominator
    of zero" of 18 September wearing different clothes, and this project's own law says an undeclared zero is
    INCONCLUSIVE. A board with no switching copper may be telling the truth, and saying so is one line."""
    body = GOOD.replace('   switch_nets: ["*_SW"]', "   switch_nets: []")
    r = S.judge(None, "x", _sheet(body))
    assert r.get("no_switch_undeclared") is True, r
    assert any("NO DECLARED REASON" in n for n in r["notes"]), r["notes"]


def t_an_empty_switch_list_with_its_reason_is_a_pass():
    """THE ACCEPTABLE FIXTURE, and the whole point: a declared zero is a PASS WITH ITS REASON. One line beside
    the empty list is all this asks, and it is the same shape board P's ground-via grid already uses."""
    body = GOOD.replace('   switch_nets: ["*_SW"]',
                        '   switch_nets: []\n   switch_nets_why: "this board has no converter: its only FETs are the pack protection pair"')
    r = S.judge(None, "x", _sheet(body))
    assert not r.get("no_switch_undeclared"), r
    assert any("no switching net, declared:" in n for n in r["notes"]), r["notes"]


def t_the_missing_input_is_named_in_the_verdict_and_not_only_in_a_note():
    """`rules_status` prefers a reading that HAD its input, and it can only do that if the verdict says so."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "sensitive_nodes.py"), encoding="utf-8").read()
    i = src.index("_no_switch = ")
    j = src.index('_v.write("sensitive_nodes"', i)
    assert "missing_input" in src[i:j] or "_missing" in src[i:j], "the empty switch list is not a declared missing input"
    assert "_no_copper or _no_switch" in src, "the empty switch list does not reach the verdict"
