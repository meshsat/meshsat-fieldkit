#!/usr/bin/env python3
"""apply_gen_sch_p_intent.py: DRAFT for board P's generator owner (Layer 6 record l6r2 round 5, MESHSAT-1357, 3 October 2026).
NOT APPLIED. It inserts 2 intent declarations (intent.node) into v2/ecad/tools/gen_sch_p.py, before the intent is written:
the voltage of nets on which a capacitor's rated voltage was open (finding F3), each derived from the circuit with its basis
and operating case (l6r2_intent.py; the page's section 8.4). Rendered by `l6r2_passives.py --write-drafts`; test_l6r2.py holds
this file equal to the render and proves its composition with every other pending draft of the generator.
Usage:  apply_gen_sch_p_intent.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_intent  # noqa: E402

BOARD = 'p'
DECLARATIONS = [
    ('SRP_F', 0.2, -0.2,
     "SRP_F: the BQ4050's SRP input (pin 8) reached through R8 100R from GND, the coulomb counter's filtered side of the 2 mOhm shunt R10 between GND and PACK_N. TI SLUSC67B 6.3 (p.8) recommends SRP and SRN within -0.2 to +0.2 V (6.1, absolute maximum -0.3 to +0.3 V); the shunt drops 36 mV at the pack's declared 18 A peak (PACK_N's rail), and the AFE's short-circuit trips SCD1 and SCC are at most 200 mV across it (6.31, p.16, CONTROL[RSNS] = 0). Operating case: discharge or charge up to the short-circuit trip; round 5 of record l6r2"),
    ('SRN_F', 0.2, -0.2,
     "SRN_F: the BQ4050's SRN input (pin 6) reached through R9 100R from PACK_N, the coulomb counter's filtered side of the 2 mOhm shunt R10 between GND and PACK_N. TI SLUSC67B 6.3 (p.8) recommends SRP and SRN within -0.2 to +0.2 V (6.1, absolute maximum -0.3 to +0.3 V); the shunt drops 36 mV at the pack's declared 18 A peak (PACK_N's rail), and the AFE's short-circuit trips SCD1 and SCC are at most 200 mV across it (6.31, p.16, CONTROL[RSNS] = 0). Operating case: discharge or charge up to the short-circuit trip; round 5 of record l6r2"),
]


if __name__ == "__main__":
    sys.exit(l6r2_intent.main(BOARD, DECLARATIONS, sys.argv[1:]))
