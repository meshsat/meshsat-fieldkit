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
    assert "10R (SRN contact resistor" in src, "the SRN contact resistor the datasheet asks for is gone"
    assert '"10n (CDIFF across the input sense' in src, "the differential capacitor on the input pair is gone"
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
