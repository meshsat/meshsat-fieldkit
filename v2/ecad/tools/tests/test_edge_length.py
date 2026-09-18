#!/usr/bin/env python3
"""A net is a transmission line because of its EDGE and its length (rule SI-001, MESHSAT-862, 16 Sep 2026).

The registry's note read "no net in this project has ever been classified by edge rate", and half of that was
already wrong: every net is classified by spectral content. What was missing is the arithmetic that turns a
class into a length, and the number that arithmetic needs is a rise time, which belongs to a DRIVER and not to
a class name: board A's fast nets are gate drives and board B's are a memory bus."""
import os, sys, math

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import rest
import edge_length as E
SRC = open(os.path.join(TOOLS, "edge_length.py"), encoding="utf-8").read()


def t_the_propagation_delay_lands_on_the_textbook_numbers():
    """About 5.5 ps/mm on an outer layer and 6.9 on an inner one, for FR-4 at er 4.3: roughly 6 inches per
    nanosecond, which is the figure every transmission-line table starts from. A formula that disagreed with it
    would have a unit error in it."""
    micro = E.t_pd_ps_per_mm(4.3, True); strip = E.t_pd_ps_per_mm(4.3, False)
    assert 5.2 < micro < 5.8, micro
    assert 6.6 < strip < 7.2, strip
    assert strip > micro, "a stripline's field is all laminate, so it must be the slower of the two"


def t_a_one_nanosecond_edge_is_about_thirty_millimetres_at_the_sixth_criterion():
    crit = 1000.0 / (6 * E.t_pd_ps_per_mm(4.3, True))
    assert 28 < crit < 32, crit


def t_a_net_with_no_declared_edge_is_named_and_never_estimated():
    assert "undeclared.append" in SRC, "a net with no declared edge is silently skipped"
    assert "no_declared_edge" in SRC, "the verdict does not carry how many nets have no edge"
    i = SRC.index("tr, _why = rise_for")
    assert "if not tr:" in rest(SRC, i), "a missing rise time falls through to a default"


def t_the_rise_time_comes_from_the_declaration_beside_the_class_entry():
    assert "def rise_for(" in SRC and "fnmatch" in SRC, "the per-entry rise time is not matched per net"
    assert "a property of the DRIVER" in SRC, "the tool does not say why a class name is not enough"


def t_being_a_transmission_line_is_not_by_itself_a_defect():
    """The first version failed every net past its critical length. At a 200 ps edge that is every net on a
    285 mm board, and a verdict that fails all of them reports physics rather than a defect. A net past its
    critical length is asked what it HAS first: an impedance target, a series resistor, or a declaration."""
    assert "def mitigation(" in SRC, "nothing asks a long net what it has"
    i = SRC.index("if L > crit:")
    w = SRC[i:i + 700]
    assert "mitigation(" in w, "the length test does not consult the mitigation"
    assert "mitigated.append" in w and "over.append" in w, "a long net has only one outcome"
    assert "long_and_answered" in SRC, "the verdict does not separate the answered from the unanswered"


def t_a_pull_up_is_not_a_series_termination():
    """A resistor to a rail damps nothing on the line: it sets a level. Only a resistor between two SIGNAL
    nets is the shape of a source termination, and the value has to be in the range one is built from."""
    i = SRC.index("for fp in b.GetFootprints():")
    w = SRC[i:i + 900]
    assert "_is_rail(a_) or _is_rail(b_)" in w, "a resistor to a rail counts as a termination"
    assert "10.0 <= ohm <= 150.0" in w, "any resistance counts as a termination"
    assert "a_ == b_" in w, "a resistor with both ends on one net counts"


def t_the_series_reading_declares_itself_a_screen():
    """The board file knows neither which end drives nor what sits at the far end, so this reading can accept
    a damping resistor in a filter. It says so where it is written down, because a screen presented as a proof
    is how a rule stops finding anything."""
    assert "SCREEN and says so" in SRC or "This is a SCREEN" in SRC, "the limitation is not written down"


def t_the_criterion_carries_the_calibration_it_was_chosen_against():
    assert "ECSS-E-HB-20-07A" in SRC, "the criterion cites no document at all"
    assert "35 mm" in SRC and "200 ps" in SRC, "the handbook's worked case is not the calibration point"
