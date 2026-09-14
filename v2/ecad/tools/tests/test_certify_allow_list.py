#!/usr/bin/env python3
"""A blank BOM row is judged by BOTH declarations, and in the right order (MESHSAT-862, 14 September 2026).

A row with no LCSC code is answered by one of two files: `tools/jlc-handfit.txt`, which says where the part is
bought instead, and `<project>/lcsc-allow.txt`, which says JLCPCB never places it at all (a ribbon header, a
wire land, a solder jumper). `jlc_certify` read only the first, so B's declared rows came back NO_STOCK and
WRONG_MODEL against parts nobody is buying. `verify_deliverable` was corrected for exactly this on 11 September.

The ORDER matters as much as the reading: with the allow list first, 35 rows that carry a real purchase route
read as bench parts, which is a worse answer than the one it replaced. The purchase route is asked first.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "jlc_certify.py")).read()


def t_the_certifier_reads_the_projects_own_allow_lists():
    assert "lcsc-allow.txt" in SRC, "jlc_certify never looks at a board's own allow list"
    assert "def project_allow" in SRC, "there is no loader for them"


def t_the_purchase_route_is_asked_first():
    i = SRC.find("hf = hand_fit_route(comment, want, handfit)")
    j = SRC.find("PROJECT_ALLOW = project_allow()", i)
    assert i > 0 and j > i, "the allow list is consulted before the purchase route"


def t_an_allowed_row_carries_the_file_and_the_reason():
    i = SRC.find("declared in %s/lcsc-allow.txt")
    assert i > 0, "an allowed row does not say where it was declared"
    assert "why" in SRC[i:i + 200], "the reason from the allow line is dropped"


def t_only_a_row_with_no_code_can_be_allowed():
    i = SRC.find("PROJECT_ALLOW = project_allow()")
    blk = SRC[i:i + 400]
    assert "if not code" in blk, "a row that carries a code could be excused by the allow list"
