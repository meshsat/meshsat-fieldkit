#!/usr/bin/env python3
"""Widening a rail's copper is a TRIAL, and it respects the pads (MESHSAT-862, 16 September 2026).

Board A's +5V_D8 measures 2.68 percent of 5 V against the 1.5 percent share this board declared, on 0.4 mm
copper carrying 1 A for 63.9 mm. Widening the class re-routes the board and costs connections elsewhere (board
D's 1.2 mm ruling cost 27 of 416, measured); drawing a band after the placement has cost the router connections
three times in this record. Widening the tracks that are already there changes no topology.

The two properties that make it safe, and they are the two this project has had to learn twice each:

  * a track wider than the pad it lands on spills past the pad edges, so a segment touching a pad narrower than
    the target is left alone rather than widened (board D, 12 September, 191 of 230 pads on the PWR nets);
  * a fixer that hurts must revert: the hard set is measured before and after, the widening is kept only when
    it is no worse, the board is refilled BEFORE it is judged, and a width that fails is retried narrower.

This reads the tool rather than running it, because it needs pcbnew and a routed board; the board fixture for
it is board A's own, on the host where KiCad is.
"""
import os, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def t_it_measures_before_and_after_and_reverts_on_a_worse_board():
    src = open(os.path.join(TOOLS, "widen_net.py"), encoding="utf-8").read()
    assert "hard_count(board_path, \"before\")" in src, "nothing measures the board before the change"
    assert "after <= base" in src, "the keep test does not compare against the baseline"
    assert "shutil.copy(backup, board_path)" in src, "there is no revert"
    i, j = src.index("pcbnew.ZONE_FILLER"), src.index('after, drc = hard_count')
    assert i < j, "the board is judged before it is refilled, which is the 14 September defect"


def t_a_segment_at_a_narrow_pad_is_left_alone():
    src = open(os.path.join(TOOLS, "widen_net.py"), encoding="utf-8").read()
    assert "def pad_limit" in src and "def touches_pad" in src, "the pad width is not considered at all"
    assert "target > lim and touches_pad" in src, "a segment landing in a narrow pad is widened anyway"


def t_it_never_widens_a_via_or_another_net():
    src = open(os.path.join(TOOLS, "widen_net.py"), encoding="utf-8").read()
    assert 'GetClass() != "PCB_TRACK"' in src, "a via has no width to widen and must be skipped"
    assert 'GetNetname().lstrip("/") != net' in src, "the net filter is missing"
