#!/usr/bin/env python3
"""A net is a transmission line because of its EDGE and its length (rule SI-001, MESHSAT-862, 16 Sep 2026).

The registry's note read "no net in this project has ever been classified by edge rate", and half of that was
already wrong: every net is classified by spectral content. What was missing is the arithmetic that turns a
class into a length, and the number that arithmetic needs is a rise time, which belongs to a DRIVER and not to
a class name: board A's fast nets are gate drives and board B's are a memory bus."""
import os, sys, math

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
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
    assert "if not tr:" in SRC[i:i + 200], "a missing rise time falls through to a default"


def t_the_rise_time_comes_from_the_declaration_beside_the_class_entry():
    assert "def rise_for(" in SRC and "fnmatch" in SRC, "the per-entry rise time is not matched per net"
    assert "a property of the DRIVER" in SRC, "the tool does not say why a class name is not enough"
