#!/usr/bin/env python3
"""apply_gen_sch_d_intent.py: DRAFT for board D's generator owner (Layer 6 record l6r2 round 5, MESHSAT-1357, 3 October 2026).
NOT APPLIED. It inserts 3 intent declarations (intent.node) into v2/ecad/tools/gen_sch_d.py, before the intent is written:
the voltage of nets on which a capacitor's rated voltage was open (finding F3), each derived from the circuit with its basis
and operating case (l6r2_intent.py; the page's section 8.4). Rendered by `l6r2_passives.py --write-drafts`; test_l6r2.py holds
this file equal to the render and proves its composition with every other pending draft of the generator.
Usage:  apply_gen_sch_d_intent.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_intent  # noqa: E402

BOARD = 'd'
DECLARATIONS = [
    ('MICAMP_AC', 2.615, -2.615,
     "the coupled side of C46: the TLV9062 (U8) output sits at VREF (R38/R39, half of +5V_D8's declared 5.23 V) and swings within its supply, so the side of C46 whose DC is ground through R45 and R47 moves at most 2.615 V either way. Operating case: full-scale transmit audio; round 5 of record l6r2"),
    ('PCM_R_AC', 3.6, -3.6,
     "the coupled side of C47: the PCM2912A's VOUTR (pin 22) swings within its R-channel supply PCM_VCCR (declared 3.6 V, TI SLES230A note 10), so the side of C47 whose DC is ground through R46 and R47 moves at most 3.6 V either way (the full regulator output, not half of it: the output's centre is not taken from the sheet). Operating case: full-scale codec playback; round 5 of record l6r2"),
    ('MIC_SUM', 3.6, -3.6,
     'the summing node of R45, R46 and R47 (10k each, R47 to ground): a resistive combination of MICAMP_AC, PCM_R_AC and ground cannot exceed the larger of the two (2.615 and 3.6 V). Operating case: both sources at full scale; round 5 of record l6r2'),
]


if __name__ == "__main__":
    sys.exit(l6r2_intent.main(BOARD, DECLARATIONS, sys.argv[1:]))
