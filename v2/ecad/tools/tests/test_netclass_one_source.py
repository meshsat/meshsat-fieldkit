#!/usr/bin/env python3
"""The board's net-class table and the project file's are ONE table (18 September 2026, MESHSAT-862).

Every placement generator sets its net classes twice: on the board through the API (which SaveBoard does not keep)
and in the project file it rewrites after the save, which is the copy KiCad, the DSN exporter and every gate read.
Board B found the two drifting on 8 September (USB and DIFF100 at 0.10 in the file against 0.127 in the table) and
fixed it for itself; nothing held the other generators to it, and on 18 September the second copy on D said PWR via
0.8/0.4 where the table said 1.2/0.6 (D13 was routed with the small via and the record said PI-003 was answered),
SENSE was absent from the file on D, E and P (its nets routed at Default geometry), P's file kept the 0.6/0.3 SENSE via
the E12 annular finding had moved to 0.7/0.3, and B's own loop named four classes by hand while its table had grown
PANEL, RF and SENSE (B22 routed its polyfuse rail at Default width). The rule: a generator names a class's geometry
ONCE, in a table, and both the API call and the project file iterate that table.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENS = ["gen_pcb_%s3.py" % L for L in "abcdep"]


def _src(name):
    return open(os.path.join(TOOLS, name), encoding="utf-8").read()


def t_no_generator_writes_a_class_geometry_into_the_project_file_by_hand():
    """A literal `C("PWR", 0, 0.127, ...)` or `Cc("HV", ...)` in the project block is a second copy of the table."""
    bad = []
    for g in GENS:
        for m in re.finditer(r'\bCc?\("(?!Default")([A-Z0-9_]+)",\s*\d', _src(g)):
            bad.append((g, m.group(1)))
    assert not bad, "class geometry written into the project file by hand, beside the table the board uses: %s" % bad


def t_no_generator_defines_a_class_on_the_board_by_hand():
    """`pcbnew.NETCLASS("PWR")` with a literal name is a class the project-file loop cannot see."""
    bad = []
    for g in GENS:
        for m in re.finditer(r'pcbnew\.NETCLASS\("([A-Za-z0-9_]+)"\)', _src(g)):
            bad.append((g, m.group(1)))
    assert not bad, "net classes defined on the board by name, outside the table both copies iterate: %s" % bad


def t_every_generator_iterates_one_table_for_both_copies():
    bad = []
    for g in GENS:
        s = _src(g)
        if "CLASSES" not in s: bad.append((g, "no CLASSES table")); continue
        i = s.find('["classes"] =')
        if i < 0 or "CLASSES" not in s[max(0, i - 700):i + 200]: bad.append((g, "the project file's classes are not built from CLASSES"))
        if not re.search(r'for .* in (CLASSES|CLASSES\.items\(\))', s): bad.append((g, "the API classes are not set from CLASSES"))
    assert not bad, bad


def t_the_rule_fails_on_the_shape_it_was_written_against():
    """The pre-fix D generator carried both copies by hand."""
    fixture = 'nc = pcbnew.NETCLASS("PWR"); cls(nc, 0.127, 0.5, 1.2, 0.6); ns.SetNetclass("PWR", nc)\n' \
              'd.setdefault("net_settings", {})["classes"] = [C("Default", 2147483647, 0.127, 0.25, 0.6, 0.3), C("PWR", 0, 0.127, 0.5, 0.8, 0.4)]\n'
    assert re.search(r'\bCc?\("(?!Default")([A-Z0-9_]+)",\s*\d', fixture) and re.search(r'pcbnew\.NETCLASS\("([A-Za-z0-9_]+)"\)', fixture)


def t_the_default_row_is_the_same_tuple_in_both_places():
    """`cls(ns.GetDefaultNetclass(), 0.127, ...)` beside `C("Default", 2147483647, 0.127, ...)` is the same two-copy shape
    for the Default class; both read one DEFAULT tuple."""
    bad = []
    for g in GENS:
        s = _src(g)
        if re.search(r'GetDefaultNetclass\(\),\s*[0-9.]', s): bad.append((g, "API default class set from literals"))
        if re.search(r'Cc?\("Default",\s*\d+,\s*[0-9.]', s): bad.append((g, "project Default row written from literals"))
        if "DEFAULT = (" not in s: bad.append((g, "no DEFAULT tuple"))
    assert not bad, bad
