#!/usr/bin/env python3
"""apply_gen_sch_e_lcsc.py: DRAFT for board E's generator owner (Layer 6 record l6r2, MESHSAT-1357, 3 October 2026). NOT APPLIED.

It writes the LCSC field of board E's generic parts into v2/ecad/tools/gen_sch_e.py: 91 designators, each keyed by the value
the code was selected for; 4 of them correct a code the generator's call writes (the entry's third field is the code
replaced, finding F7) (v2/docs/records/l6r2/L6R2-PASSIVES.md and l6r2_passives.out; the logic in l6r2_apply.py). Rendered by
`l6r2_passives.py --write-drafts`; test_l6r2.py holds this file equal to the render and proves its composition with every other
pending draft of the generator.
Usage:  apply_gen_sch_e_lcsc.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_apply  # noqa: E402

BOARD = 'e'
ENTRIES = {
    'C1': ('10u 25V 1210', 'C2918497'),
    'C2': ('100n 100V', 'C106243'),
    'C5': ('100n (TIMER)', 'C113803'),
    'C6': ('1u 100V 1210 (X, input side)', 'C382212'),
    'C7': ('1u 100V 1210 (X, bus side)', 'C382212'),
    'C8': ('10u 100V X7R 1210', 'C5156756'),
    'C13': ('10u 50V', 'C89632'),
    'C14': ('10u 50V', 'C89632'),
    'C15': ('4.7u 50V', 'C132170'),
    'C16': ('1n', 'C113793'),
    'C17': ('470n 25V', 'C1623'),
    'C18': ('470n 25V', 'C1623'),
    'C19': ('4.7u 25V', 'C132170'),
    'C20': ('1u', 'C559769'),
    'C21': ('4.7n', 'C53987'),
    'C22': ('100p', 'C14858'),
    'C23': ('100n', 'C113803'),
    'C26': ('10u 25V', 'C89632'),
    'C27': ('10u 25V', 'C89632'),
    'C30': ('100n', 'C113803'),
    'C31': ('10u 25V 1210', 'C2918497'),
    'C32': ('22u 10V X7R 1210', 'C2918511'),
    'C33': ('22u 10V X7R 1210', 'C2918511'),
    'C34': ('1u', 'C559769'),
    'C35': ('1u', 'C559769'),
    'C36': ('15p', 'C1644'),
    'C37': ('15p', 'C1644'),
    'C38': ('100n', 'C113803'),
    'C39': ('100n', 'C113803'),
    'C40': ('100n', 'C113803'),
    'C41': ('100n', 'C113803'),
    'C42': ('100n', 'C113803'),
    'C43': ('100n', 'C113803'),
    'C44': ('100n', 'C113803'),
    'C45': ('1u', 'C559769'),
    'C47': ('1u', 'C559769'),
    'C48': ('100n', 'C113803'),
    'C49': ('100n', 'C113803'),
    'C50': ('100n', 'C113803'),
    'C51': ('100n', 'C113803'),
    'C53': ('1n', 'C113793', 'C1588'),
    'C56': ('1u', 'C559769', 'C15849'),
    'C57': ('1u', 'C559769', 'C15849'),
    'C58': ('1u', 'C559769', 'C15849'),
    'C63': ('4.7u 25V', 'C132170'),
    'D5': ('BAT54 boost diode INTVCC -> BOOST1', 'C7502705'),
    'D6': ('BAT54 boost diode INTVCC -> BOOST2', 'C7502705'),
    'LED1': ('green: vehicle input present', 'C2986059'),
    'LED2': ('status (GPIO25)', 'C2986059'),
    'R8': ('102k 1% (RFBIN1: panel point 17.6 V)', 'C2933126'),
    'R9': ('7.50k 1% (RFBIN2)', 'C23234'),
    'R10': ('115k 1% (RFBOUT1: 15.1 V)', 'C22783'),
    'R11': ('10.0k 1% (RFBOUT2)', 'C25804'),
    'R12': ('215k 1% (RT: 202 kHz)', 'C5713280'),
    'R13': ('10k', 'C25804'),
    'R14': ('100k 1%', 'C25803'),
    'R15': ('15.0k 1% (SHDN: enable above about 9.5 V)', 'C22809'),
    'R16': ('10k', 'C25804'),
    'R17': ('10k', 'C25804'),
    'R19': ('10mOhm 1% 2512 (hot-swap sense)', 'C2903468'),
    'R20': ('100k 1%', 'C25803'),
    'R21': ('38.3k 1% (UVLO: 9 V)', 'C23034'),
    'R22': ('100k 1%', 'C25803'),
    'R23': ('6.65k 1% (OVLO: 40 V)', 'C60344'),
    'R24': ('20k (PWR: power limit)', 'C4184'),
    'R25': ('10k', 'C25804'),
    'R26': ('100k', 'C25803'),
    'R28': ('1k', 'C21190'),
    'R29': ('27R', 'C25190'),
    'R30': ('27R', 'C25190'),
    'R31': ('10k', 'C25804'),
    'R32': ('1k (BOOTSEL)', 'C21190'),
    'R33': ('1k', 'C21190'),
    'R34': ('4.7k', 'C23162'),
    'R35': ('4.7k', 'C23162'),
    'R36': ('4.7k', 'C23162'),
    'R37': ('4.7k', 'C23162'),
    'R38': ('1M', 'C22935'),
    'R39': ('1M', 'C22935'),
    'R40': ('100k 1%', 'C25803'),
    'R41': ('10k 1% (ADC1: 0.091 x bus)', 'C25804'),
    'R42': ('100k 1%', 'C25803'),
    'R43': ('22k 1% (ADC2: 0.18 x pack)', 'C31850'),
    'R44': ('100R', 'C22775'),
    'R45': ('100R', 'C22775'),
    'R46': ('10k', 'C25804'),
    'R47': ('10k', 'C25804'),
    'R48': ('22R (pulse input series)', 'C23345'),
    'R49': ('10k', 'C25804'),
    'R50': ('10k', 'C25804'),
    'R51': ('0R (CSB high: I2C mode; its own net keeps the pin joiner off the diagonal)', 'C21189'),
}


if __name__ == "__main__":
    sys.exit(l6r2_apply.main(BOARD, ENTRIES, sys.argv[1:]))
