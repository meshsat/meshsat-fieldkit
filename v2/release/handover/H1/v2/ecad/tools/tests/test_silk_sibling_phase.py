#!/usr/bin/env python3
"""A legend that points at another board names the BOARD, never one of its phases (17 September 2026).

THE DEFECT, on the tree this was written against, on three boards at once: board E's silk read "pack 14.4 V
and vehicle 9-36 V to the raised block -> A22" and "A22 dock pins land here", board E5's read "A22 pins land
here", and board C's read "B16 outline below". Board A has been through ten phases since A22 and board B four
since B16, so an assembler reading those boards is sent to a design that no longer exists. The deliverable's
own silk-phase gate cannot see it: it looks for stale tokens of THIS board's letter, because that is the
defect it was written for (a board stamped with its own previous phase).

A sibling's phase is not this board's to track. The board designation is stable and is what the legend means.
"""
import os, re, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# A phase token: a board letter and one or two digits, standing ALONE. A hyphen on either side makes it part
# of a part number and not a phase: Ebyte's E22-900M30S LoRa module is the reason this is not \b...\b, and a
# rule that renamed a part would be worse than the defect it is looking for.
PHASE = re.compile(r"(?<![\w-])(?:A|B|C|D|P|E|E1|E5)\d{1,2}(?![\w-])")
# The one place a phase token belongs in a legend is the board's OWN title, which the chain passes in as PHASE.
TITLE = re.compile(r"%s|PHASE")
# PART NUMBERS THAT LOOK LIKE PHASES, declared with the part each one is. A letter and two digits is the shape
# of both a phase stamp and half the module names in this kit, and a rule that renamed a part to protect a
# legend would be a worse defect than the one it looks for. This list is the `erc-allow.txt` idiom: an
# exemption is allowed and it must say what it is.
PARTS = {
    "E22": "Ebyte E22-900M30S, the 1 W LoRa module (ruled 6 September 2026)",
    "E72": "Ebyte E72-2G4M20S1E, the CC2652P Zigbee and Thread module",
    "P1":  "a connector designation on the pack board's own silk, not a phase",
}


def _silk_strings(path):
    """Every literal string handed to a text() call in a generator, with its line number."""
    out = []
    for i, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        if "text(" not in line or line.lstrip().startswith("#"): continue
        for m in re.finditer(r'text\(\s*"((?:[^"\\]|\\.)*)"', line):
            out.append((i, m.group(1), line))
    return out


def _letter_of(path):
    m = re.search(r"gen_pcb_([a-z][0-9a-z]?)", os.path.basename(path))
    return (m.group(1)[0].upper() if m else "")


def t_no_generator_stamps_another_boards_phase_on_the_silk():
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "gen_pcb_*.py"))):
        mine = _letter_of(p)
        for n, s, line in _silk_strings(p):
            for tok in PHASE.findall(s):
                if tok in PARTS: continue                  # a declared part number, with its part named above
                if tok.startswith(mine): continue          # this board's own phase, which the title carries
                if TITLE.search(line): continue            # a formatted title takes its phase from the chain
                bad.append("%s:%d names %s on the silk: %s" % (os.path.basename(p), n, tok, s[:70]))
    assert not bad, ("a legend pointing at another board must name the board, not a phase of it:\n  "
                     + "\n  ".join(sorted(set(bad))))


def t_the_rule_would_have_caught_the_three_legends_it_was_written_for():
    """The defective fixture, verbatim from the tree this was written against."""
    for s in ('text("RAISED BLOCK pcb-e5-block on 6 mm M3 standoffs: A22 dock pins land here", 0, 0)',
              'text("B16 outline below (330 x 200): the deep parts clear its tall parts", 0, 0)',
              'text("A22 pins land here", -76.5, -61.5)'):
        got = re.findall(r'text\(\s*"((?:[^"\\]|\\.)*)"', s)
        assert got and PHASE.search(got[0]), s


def t_a_boards_own_phase_in_its_title_is_not_a_finding():
    """The acceptable fixture: a board's own title carries its own phase, which the chain passes in."""
    line = 'text("MESHSAT PCB-E1 DOCK (%s)" % PHASE + "  -  eleven blind-mate clamps", 0, -46.3)'
    assert TITLE.search(line), "a formatted title must be recognised as the board's own phase"


def t_every_declared_part_token_says_which_part_it_is():
    """An exemption nobody can audit is how the four floors of 12 September came to have holes in them."""
    for tok, why in PARTS.items():
        assert len(why) > 20 and not why.lower().startswith("todo"), "%s is exempted with no reason: %r" % (tok, why)


def t_a_part_number_is_not_a_phase():
    """Ebyte's E22-900M30S is a LoRa module. A rule that renamed a part to protect a legend would be a worse
    defect than the one it is looking for."""
    assert not PHASE.search("E22-900M30S LoRa"), "a hyphenated part number reads as a phase"
    assert not PHASE.search("TPS23861"), "a part number that happens to contain digits is not a phase"
    assert PHASE.search("54 V from A22 J_54V"), "a bare sibling phase must still be found"
