#!/usr/bin/env python3
"""No board may SILKSCREEN a part the design has retired (MESHSAT-862, 13 September 2026).

Found by reading a 3D render before sending it to an outside reviewer. A24 and E7 both still carried
"BB-2590/U PACK IN ITS CRADLE WEST OF THIS BOARD" on their front silk, and owner ruling 7 September 2026
13:10 withdrew that pack: it does not fit beside this board set and the design took a built 4S smart pack
instead (appendix 32.62). Silk only, no copper, and it would have been read by a reviewer as the design.

The list is short and declared rather than inferred, because a retired part usually keeps appearing in
HISTORY (a comment saying why a region moved, an appendix paragraph) and that is correct. What must not
happen is the retired name reaching a `text(` call, which is what a generator writes onto the board.
"""
import os, re, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (name as it appears, what replaced it, the ruling that retired it)
RETIRED = [
    ("BB-2590", "a built 4S smart pack", "owner ruling 7 September 2026 13:10, appendix 32.62"),
    ("DMR858M", "the SA868 exciter with a 30 W PA stage", "the V2 device set, 6 September 2026, appendix 32.49"),
    ("X1202", "the boards' own charger, gauge and power control", "appendix 32.17, 4 September 2026"),
    ("Touch Display 2", "the Xenarc 709GNK on the face plate", "the V2 device set, 6 September 2026"),
]

# A generator writes silk with text(...). Only the literal strings inside such a call are judged.
TEXT_CALL = re.compile(r'\btext\s*\(\s*(?:f?")([^"]*)"', re.S)


def t_no_generator_silkscreens_a_retired_part():
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "gen_pcb_*.py")) + glob.glob(os.path.join(TOOLS, "gen_footprints_*.py"))):
        src = open(f).read()
        for m in TEXT_CALL.finditer(src):
            s = m.group(1)
            for name, replacement, ruling in RETIRED:
                if name.lower() in s.lower():
                    line = src[:m.start()].count("\n") + 1
                    bad.append("%s:%d silkscreens %r, retired by %s in favour of %s\n      %s"
                               % (os.path.basename(f), line, name, ruling, replacement, s[:110]))
    assert not bad, ("a retired part reaches a board's silkscreen, where a reader takes it for the design:\n  "
                     + "\n  ".join(bad))


def t_the_retired_list_is_declared_with_its_ruling():
    """A list of forbidden words with no reason beside each is a list nobody can maintain."""
    for name, replacement, ruling in RETIRED:
        assert name and replacement and ruling, (name, replacement, ruling)
        assert any(c.isdigit() for c in ruling), "%s is retired without a dated ruling: %r" % (name, ruling)


def t_history_in_comments_is_not_touched():
    """The rule must judge silk, not prose, or it forces the record to forget why a thing changed.

    `gen_pcb_e.py` still explains in a comment that its west end stops short of the cradle, and that sentence
    is true and useful. Only a `text(` call puts a string on the board.
    """
    src = "# the west end stops 1 mm short of the BB-2590/U cradle\nBOARD = 1\n"
    assert not TEXT_CALL.findall(src), "the rule reads comments, which would make it refuse the record"
    src2 = 'text("BB-2590/U PACK IN ITS CRADLE", 0, 0)\n'
    assert TEXT_CALL.findall(src2), "the rule does not read a silk call, so it protects nothing"
