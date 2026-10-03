#!/usr/bin/env python3
"""apply_gen_sch_c_lcsc.py: DRAFT for board C's generator owner (Layer 6 record l6r2, MESHSAT-1357, 3 October 2026). NOT APPLIED.

It writes the LCSC field of board C's generic parts into v2/ecad/tools/gen_sch_c.py: 42 designators, each keyed by the value
the code was selected for; 2 of them correct a code the generator's call writes (the entry's third field is the code
replaced, finding F7) (v2/docs/records/l6r2/L6R2-PASSIVES.md and l6r2_passives.out; the logic in l6r2_apply.py). Rendered by
`l6r2_passives.py --write-drafts`; test_l6r2.py holds this file equal to the render and proves its composition with every other
pending draft of the generator.
Usage:  apply_gen_sch_c_lcsc.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_apply  # noqa: E402

BOARD = 'c'
ENTRIES = {
    'C1': ('10u', 'C326595', 'C15850'),
    'C2': ('10u', 'C326595', 'C15850'),
    'C3': ('1u', 'C559769'),
    'C4': ('1u', 'C559769'),
    'C5': ('15p NP0', 'C1548'),
    'C6': ('15p NP0', 'C1548'),
    'C7': ('100n', 'C113803'),
    'C8': ('100n', 'C113803'),
    'C9': ('100n', 'C113803'),
    'C10': ('100n', 'C113803'),
    'C11': ('100n', 'C113803'),
    'C12': ('100n', 'C113803'),
    'C13': ('100n', 'C113803'),
    'C14': ('1u', 'C559769'),
    'C15': ('100n', 'C113803'),
    'C16': ('1u', 'C559769'),
    'C25': ('100n', 'C113803'),
    'C28': ('4.7u', 'C354262'),
    'C29': ('100n', 'C113803'),
    'C30': ('1u 25V', 'C106858'),
    'C32': ('1u 25V', 'C106858'),
    'C33': ('1u 25V', 'C106858'),
    'C34': ('1u 25V', 'C106858'),
    'C35': ('1u 25V', 'C106858'),
    'C36': ('1u 25V', 'C106858'),
    'C37': ('1u 25V', 'C106858'),
    'C38': ('100n', 'C113803'),
    'D18': ('status (GPIO25)', 'C2986059'),
    'R1': ('1k', 'C21190'),
    'R2': ('27R', 'C25190'),
    'R3': ('27R', 'C25190'),
    'R4': ('10k', 'C25804'),
    'R5': ('1k (BOOTSEL)', 'C21190'),
    'R6': ('1k', 'C21190'),
    'R7': ('2.2k', 'C4190'),
    'R8': ('2.2k', 'C4190'),
    'R42': ('10k', 'C25804'),
    'R43': ('0.47R 1%', 'C414503'),
    'R53': ('27R', 'C25190'),
    'R54': ('27R', 'C25190'),
    'R55': ('27R', 'C25190'),
    'R56': ('27R', 'C25190'),
}


if __name__ == "__main__":
    sys.exit(l6r2_apply.main(BOARD, ENTRIES, sys.argv[1:]))
