#!/usr/bin/env python3
"""A netlist older than its schematic describes a board that no longer exists (MESHSAT-862, 13 Sep 2026).

Board B's netlist in the box clone was five hours older than its schematic and carried no `J_AB2` at all,
because every B run that day had been in an isolated tree. FOUR cross-board contracts then failed on every
board's finish, all of them naming the A-to-B ribbon, and the two generators had been identical all along:
the check was comparing a current A against a B from before the ribbon split. Regenerating B's netlist took
it to 42 of 42.

A comparison against stale data is not a result in either direction, so such a netlist is treated as missing,
which the tool already reads as INCONCLUSIVE and not as a pass.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def t_the_contract_check_refuses_a_netlist_older_than_its_schematic():
    src = open(os.path.join(TOOLS, "check_contracts.py")).read()
    assert "STALE netlist" in src, "the contract check reads a netlist without asking how old it is"
    assert "os.path.getmtime(path) < os.path.getmtime(_sch)" in src, "it does not compare the two times"
    i, j = src.find("STALE netlist"), src.find("txt = open(path")
    assert 0 < i < j, "the staleness check must come before the netlist is parsed"


def t_the_refusal_returns_nothing_so_the_board_reads_as_missing():
    """Returning a partial netlist would let contracts pass on stale data, which is the failure this
    prevents. The tool already treats a missing netlist as inconclusive and lists the board."""
    src = open(os.path.join(TOOLS, "check_contracts.py")).read()
    i = src.find("STALE netlist")
    blk = src[i:i + 700]
    assert "return None, None" in blk, "a stale netlist is not turned into a missing one"


def t_it_says_both_dates_so_the_reader_can_act():
    src = open(os.path.join(TOOLS, "check_contracts.py")).read()
    i = src.find("STALE netlist")
    blk = src[i:i + 700]
    assert "is from %s and its schematic is from %s" in blk, "the message does not carry the two dates"
    assert "gen_sch" in blk and "build_sch" in blk, "the message does not say how to fix it"
