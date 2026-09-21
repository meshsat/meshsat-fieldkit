#!/usr/bin/env python3
"""Decision 47: the 1 mm length rule is about a pair whose class declares an impedance target.

The defective fixture is board A's own case, a Kelvin tap named `_P`/`_N`, which the gates held to a
differential pair's rule and which `pair_match.sh` then refused the finish on. The acceptable fixture is a
real controlled pair, which must go on being judged. Both run where KiCad is not."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

import pair_gate as pg                                                  # noqa: E402

# board A as it stands: the ten ISNS taps are unassigned, the three USB pairs are in a class with a target
CLASSES = {"USB": {"z_diff": 90.0, "z_se": 50.0}, "SENSE": {}, "PWR": {}}
ASSIGN = {"USB_D8_P": "USB", "USB_D8_N": "USB", "PA_ISNS_P": "SENSE", "PA_ISNS_N": "SENSE"}


def _class_of(net):
    return ASSIGN.get(net)


def t_a_kelvin_tap_is_not_a_controlled_pair():
    """THE DEFECTIVE FIXTURE, and it is board A's own copper.

    `PA_ISNS_P` and `PA_ISNS_N` are the two legs of one current-sense tap. They are in the SENSE class, which
    declares no impedance target, because a Kelvin tap has none: its legs go to opposite ends of a shunt and
    the 58.38 mm between them is the shunt's own geometry. Held to the pair rule it can never pass, and every
    board A finish ended PAIRS NOT MATCHED."""
    ok, why = pg.judged("PA_ISNS", _class_of, CLASSES)
    assert ok is False, "a Kelvin tap is still held to the differential pair rule: %s" % why
    assert "impedance target" in why, why


def t_a_pair_whose_class_declares_a_target_is_still_judged():
    """THE ACCEPTABLE FIXTURE: the ruling must not switch the rule off for the pairs it is for."""
    ok, why = pg.judged("USB_D8", _class_of, CLASSES)
    assert ok is True, "a real controlled pair stopped being judged: %s" % why
    assert "USB" in why, why


def t_one_leg_in_a_class_with_a_target_is_enough():
    """A pair whose two legs were assigned to different classes is still a pair. The rule reads either leg,
    so a class table that has drifted on one net cannot switch the rule off for both."""
    ok, _ = pg.judged("USB_D8", lambda n: "USB" if n.endswith("_P") else None, CLASSES)
    assert ok is True


def t_a_declaration_that_cannot_be_read_judges_as_before():
    """FAIL CLOSED. A missing class table or a missing intent must never be the reason a rule stops applying:
    that is `sense_reach`'s PASS of 0 of this morning in another place, and STK-001's of 19 September."""
    for a, b in ((None, CLASSES), (_class_of, None), (None, None)):
        ok, why = pg.judged("PA_ISNS", a, b)
        assert ok is True, "an unreadable declaration switched the rule off"
        assert "could not be read" in why, why


def t_both_board_gates_ask_this_question():
    """The two gates that enumerate `_P`/`_N` pairs are the two that must ask. Proved to fail on the tree it
    was written against: on 21 September both printed WARN for every pair over 1.00 mm with no such call."""
    for f in ("check_pcb_a.py", "check_pcb_b.py"):
        src = open(os.path.join(TOOLS, f), encoding="utf-8").read()
        assert "pair_gate" in src and "judged(" in src, \
            "%s holds every _P/_N pair to the 1 mm rule without asking whether it is a controlled pair" % f


def t_the_ruling_is_recorded_with_its_reversal():
    """A session ruling carries the authority it claims and the way back, and it is read by PARSING the
    register rather than by slicing a byte window out of it: a fixed window is not a rule about the file, and
    two of this suite's rules have already broken when a comment pushed a literal past a slice."""
    import yaml
    reg = yaml.safe_load(open(os.path.join(TOOLS, "pcb_decisions.yaml"), encoding="utf-8"))
    e = [d for d in reg["decisions"] if d.get("n") == 47]
    assert e, "decision 47 is no longer in the register"
    e = e[0]
    assert e.get("status") == "ruled", "decision 47 is still open while both gates act on its ruling"
    assert e.get("ruled_by") == "SESSION", "a ruling with no author reads later as the owner's"
    assert e.get("authority") == "SESSION" and e.get("authority_why"), \
        "a session ruling must say why it is not the owner's"
    assert len(str(e.get("reversed_by") or "")) > 60 and ".py" in str(e.get("reversed_by")), \
        "a ruling with no named way back cannot be withdrawn on new evidence"
