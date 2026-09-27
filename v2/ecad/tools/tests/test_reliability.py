#!/usr/bin/env python3
"""What carries load and what sees cycling (rule REL-001, 16 September 2026).

The kit is carried, so every connector mated in the field is a wear item and every board-mounted jack is a
lever with the case as its fulcrum. The rule asks for the list per board with the cycles, the load and the
measure; it read "no verification" on seven boards.

The check that makes it a gate is completeness: every part in the netlist whose value names a connector, a
socket, a holder or a jack must fall in exactly one declared class, because a list covering nine of a board's
eleven jacks reads as complete. 111 parts across six boards fall in 23 classes today.

It tests nothing, and says so: REL-001 is verified at the PROTOTYPE and no board has been built.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import reliability as REL


def _tree(comps):
    d = tempfile.mkdtemp(prefix="rel-")
    prj = os.path.join(d, "pcb-x-test"); os.makedirs(os.path.join(prj, "out"))
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    open(os.path.join(prj, "out", "pcb-x-test.net"), "w").write(
        "(export (version E)\n  (components\n%s  )\n  (nets\n  )\n)\n" % c)
    return d


def _run(sheet, comps):
    d = _tree(comps)
    p = os.path.join(d, "rel.yaml"); open(p, "w").write(sheet)
    import rules_lib as R
    keep = R.board_facts
    try:
        R.board_facts = lambda *a, **k: {"x": {"project": "pcb-x-test"}}
        return REL.judge(p, d, "x")["x"]
    finally:
        R.board_facts = keep


GOOD = """
schema_version: "1.0.0"
boards:
 x:
   classes:
    - {name: "the jacks", refs: ["J_RF*"], cycles: 500, basis: "the SMA standard", load: "a wrench", measure: "the case wall takes it"}
"""


def t_a_wear_part_in_no_class_is_refused():
    """THE DEFECTIVE FIXTURE: two jacks declared, a third connector on the board and nobody has looked at it."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "J_RF2": "SMA jack", "J_PWR1": "JST-VH socket"})
    assert any("J_PWR1" in f for f in r["fails"]), r["fails"]


def t_the_same_board_with_every_class_declared_passes():
    sheet = GOOD + '    - {name: "power", refs: ["J_PWR*"], cycles: 30, basis: "JST VH", load: "a lead", measure: "a tie"}\n'
    r = _run(sheet, {"J_RF1": "SMA jack", "J_PWR1": "JST-VH socket"})
    assert not r["fails"], r["fails"]


def t_a_class_with_no_cycle_figure_must_say_why():
    sheet = GOOD.replace("cycles: 500", "cycles: null")
    r = _run(sheet, {"J_RF1": "SMA jack"})
    assert any("does not say why" in f for f in r["fails"]), r["fails"]
    sheet2 = GOOD.replace("cycles: 500, basis: \"the SMA standard\"",
                          "cycles: null, basis: \"no mating-cycle figure is published for this part\"")
    r2 = _run(sheet2, {"J_RF1": "SMA jack"})
    assert not r2["fails"], r2["fails"]


def t_a_class_without_a_load_or_a_measure_is_refused():
    for k in ("load", "measure"):
        sheet = GOOD.replace('%s: "%s"' % (k, {"load": "a wrench", "measure": "the case wall takes it"}[k]), '%s: ""' % k)
        r = _run(sheet, {"J_RF1": "SMA jack"})
        assert any(("carries no %s" % k) in f for f in r["fails"]), (k, r["fails"])


def t_a_declared_count_that_does_not_match_the_board_is_refused():
    sheet = GOOD.replace('refs: ["J_RF*"]', 'refs: ["J_RF*"], count_expected: 3')
    r = _run(sheet, {"J_RF1": "SMA jack", "J_RF2": "SMA jack"})
    assert any("expects 3" in f for f in r["fails"]), r["fails"]


# THE PART'S IDENTITY DECIDES, NOT THE DESCRIPTION OF WHAT IT DOES (27 September 2026). A value is written
# `<the part and its properties>: <what it does in this circuit>`. The word list was searched in all of it, so
# three AND gates on board B whose description says they enable a card SOCKET's supply were refused as
# load-bearing parts in no declared class, and the set 6 candidate's suite read 2010 passed, 1 failed.
GATE = ("SN74LV1T08DBVR AND, 5 V supply, TTL-level inputs (1 A 2 B 3 GND 4 Y 5 VCC): slot 1's card-socket supply "
        "enable = EMCON AND PCIE_PWR_EN1, run from +5V_S1, that supply's own input (W4B-D3)")


def t_a_logic_gate_that_enables_a_sockets_supply_is_no_wear_part():
    """THE DEFECTIVE READING, on board B's own text: `U116` beside one declared jack. The board passes with no
    class for the gate, the jack is still counted, and the gate is NAMED as set aside rather than dropped in
    silence. The unfixed tool fails the first assertion with the refusal the box suite printed."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "U116": GATE})
    assert not r["fails"], r["fails"]
    assert r["covered"] == 1, r
    assert r["prose_only"] == ["U116"], r
    assert any("U116" in n and "description" in n for n in r["notes"]), r["notes"]


def t_a_real_socket_with_a_description_after_the_colon_is_still_a_wear_part():
    """THE ACCEPTABLE READING the change must not lose: the socket is named BEFORE the colon. It holds on the
    unfixed tool too, which is what makes it the control of the test above."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "J5": "M.2 key-E socket (TE 2199230-4): WiFi card"})
    assert any("J5" in f and "in no declared class" in f for f in r["fails"]), r["fails"]
    assert r["covered"] == 1, r


def t_a_module_receptacle_is_a_wear_part_though_its_reference_is_a_u():
    """Why a prefix cannot decide this: a receptacle drawn as `U30A` and a logic gate drawn as `U116` share
    theirs, and `U` must stay out of NOT_WEAR_PREFIX. It holds on the unfixed tool too."""
    r = _run(GOOD, {"J_RF1": "SMA jack", "U30A": "CM5 receptacle DF40HC(3.0)-100DS-0.4V: module connector A"})
    assert any("U30A" in f and "in no declared class" in f for f in r["fails"]), r["fails"]
    sheet = GOOD + '    - {name: "module", refs: ["U30*"], cycles: 30, basis: "Hirose DF40", load: "the module", measure: "four screws"}\n'
    r2 = _run(sheet, {"J_RF1": "SMA jack", "U30A": "CM5 receptacle DF40HC(3.0)-100DS-0.4V: module connector A"})
    assert not r2["fails"] and r2["covered"] == 2, r2


def t_a_colon_inside_a_bracket_does_not_end_the_identity():
    """89 of the 2630 values of the six netlists carry their first colon inside a bracket, which is a remark on
    the part. A plain split at the first colon would cut the identity there and DROP a connector named in the
    remark, in silence, which is the direction a completeness gate must never fail in."""
    v = "fan lead (mates: JST-SH socket of the cooler): 5V GND TACHO PWM"
    r = _run(GOOD, {"J_RF1": "SMA jack", "J_FAN1": v})
    assert any("J_FAN1" in f for f in r["fails"]), r["fails"]
    assert REL.identity(v) == "fan lead (mates: JST-SH socket of the cooler)", REL.identity(v)
    for value, want in (
            ("USB-C 2.0 receptacle", "USB-C 2.0 receptacle"),                        # no colon: all identity
            ("SMCJ40A (bus clamp: 40 V standoff on the bus)", "SMCJ40A (bus clamp: 40 V standoff on the bus)"),
            ("lead (JST-VH: + -", "lead (JST-VH: + -"),                              # a bracket that never closes
            ("ratio 1:1 transformer: the link", "ratio 1:1 transformer"),            # a colon with no space after it
            ("U.FL: MHF4 pigtail: chain A", "U.FL"),                                 # the FIRST such colon
            (GATE, "SN74LV1T08DBVR AND, 5 V supply, TTL-level inputs (1 A 2 B 3 GND 4 Y 5 VCC)"),
            ("", ""), (None, "")):
        assert REL.identity(value) == want, (value, REL.identity(value))


def t_the_committed_list_covers_every_wear_part_of_every_board():
    r = REL.judge()
    fails = [f for v in r.values() for f in v["fails"]]
    assert not fails, fails
    assert sum(v["covered"] for v in r.values()) >= 100, r
