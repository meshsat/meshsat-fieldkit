#!/usr/bin/env python3
"""apply_gen_sch_p_lcsc.py: DRAFT for board P's generator owner (Layer 6 record l6r2, MESHSAT-1357, 3 October 2026). NOT APPLIED.

It writes the LCSC field of board P's generic parts into v2/ecad/tools/gen_sch_p.py: 44 designators, each keyed by the value
the code was selected for (v2/docs/records/l6r2/L6R2-PASSIVES.md and l6r2_passives.out; the logic in l6r2_apply.py). Rendered by
`l6r2_passives.py --write-drafts`; test_l6r2.py holds this file equal to the render and proves its composition with every other
pending draft of the generator.
Usage:  apply_gen_sch_p_lcsc.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_apply  # noqa: E402

BOARD = 'p'
ENTRIES = {
    'C1': ('2.2u', 'C19110'),
    'C2': ('100n', 'C113803'),
    'C3': ('100n', 'C113803'),
    'C4': ('100n', 'C113803'),
    'C5': ('100n', 'C113803'),
    'C6': ('100n', 'C113803'),
    'C7': ('100n', 'C113803'),
    'C8': ('100n', 'C113803'),
    'C9': ('100n', 'C113803'),
    'C11': ('100n 50V', 'C113803'),
    'C12': ('100n 50V', 'C24497'),
    'C13': ('100n', 'C113803'),
    'C14': ('100n', 'C113803'),
    'C15': ('100n', 'C113803'),
    'C16': ('100n', 'C113803'),
    'C17': ('100n', 'C113803'),
    'C18': ('100n', 'C113803'),
    'C19': ('100n', 'C113803'),
    'R1': ('100R', 'C22775'),
    'R2': ('100R', 'C22775'),
    'R3': ('100R', 'C22775'),
    'R4': ('100R', 'C22775'),
    'R5': ('100R', 'C22775'),
    'R6': ('1k', 'C21190'),
    'R7': ('1k', 'C21190'),
    'R8': ('100R', 'C22775'),
    'R9': ('100R', 'C22775'),
    'R10': ('2m 2512 2W (sense)', 'C154685'),
    'R14': ('10k', 'C25804'),
    'R15': ('10k', 'C25804'),
    'R16': ('5.1k', 'C23186'),
    'R17': ('10M', 'C7250'),
    'R18': ('5.1k', 'C23186'),
    'R19': ('10M', 'C7250'),
    'R20': ('100R', 'C22775'),
    'R21': ('100R', 'C22775'),
    'R22': ('1k', 'C21190'),
    'R24': ('1k', 'C21190'),
    'R25': ('1k', 'C21190'),
    'R26': ('1k', 'C21190'),
    'R27': ('1k', 'C21190'),
    'R28': ('100k', 'C25803'),
    'R30': ('5.1k', 'C23186'),
    'R32': ('1M', 'C22935'),
}


if __name__ == "__main__":
    sys.exit(l6r2_apply.main(BOARD, ENTRIES, sys.argv[1:]))
