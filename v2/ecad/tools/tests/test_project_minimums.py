#!/usr/bin/env python3
"""The project file's minimum is the one KiCad enforces, so it may not disagree with the board's (17 September
2026, rules RTE-001 and IMP-002).

THE DEFECT, live in the tree this was written against: board P is two layers at 2 oz and the fabricator's own
capability for that combination is 0.16 mm of track and 0.16 mm of spacing. On 16 September the board's
minimums were moved to 0.16 in gen_pcb_p.py, and two lines in the PLACEMENT generator were missed: the SWIG
default net class at 0.127, and `board.design_settings.rules.min_clearance` at 0.127 in the project file. The
second is the one that decides: a board's minimums live in the project file and nothing set through the SWIG
design settings survives a save. So the board said 0.16 and was built to 0.127, and `fab_limits` reports five
items under the fabricator's capability on the board that was cut.
"""
import os, re, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_CLEAR = re.compile(r'\["min_clearance"\]\s*=\s*([0-9.]+)')
BOARD_MIN = re.compile(r'\("m_MinClearance",\s*([0-9.]+)\)')


def _num(pattern, text):
    m = pattern.search(text)
    return float(m.group(1)) if m else None


def t_no_generator_writes_a_project_minimum_below_the_board_s_own():
    """The two files are one statement and a generator that writes both must write the same number."""
    bad = []
    for letter in ("a", "b", "c", "d", "e", "p"):
        mech = os.path.join(TOOLS, "gen_pcb_%s.py" % letter)
        place = os.path.join(TOOLS, "gen_pcb_%s3.py" % letter)
        if not (os.path.isfile(mech) and os.path.isfile(place)): continue
        board_min = _num(BOARD_MIN, open(mech, encoding="utf-8", errors="replace").read())
        proj_min = _num(MIN_CLEAR, open(place, encoding="utf-8", errors="replace").read())
        if board_min is None or proj_min is None: continue
        if abs(board_min - proj_min) > 1e-9:
            bad.append("board %s: gen_pcb_%s.py sets the board minimum to %s and gen_pcb_%s3.py writes %s into "
                       "the project file, which is the one KiCad enforces"
                       % (letter.upper(), letter, board_min, letter, proj_min))
    assert not bad, "\n  ".join([""] + bad)


def t_board_p_is_at_the_fabricators_two_ounce_floor_everywhere():
    """The specific number, because this board is the one it was wrong on and 0.127 is a plausible-looking
    value that every gate in this project passed for a month."""
    place = open(os.path.join(TOOLS, "gen_pcb_p3.py"), encoding="utf-8", errors="replace").read()
    assert _num(MIN_CLEAR, place) == 0.16, _num(MIN_CLEAR, place)
    m = re.search(r"cls\(ns\.GetDefaultNetclass\(\),\s*([0-9.]+)", place)
    assert m and float(m.group(1)) >= 0.16, "the SWIG default class is %s" % (m.group(1) if m else "absent")
    for cl in re.finditer(r'C\("(\w+)",\s*\d+,\s*([0-9.]+)', place):
        assert float(cl.group(2)) >= 0.16, "class %s is written at %s in the project file" % (cl.group(1), cl.group(2))
