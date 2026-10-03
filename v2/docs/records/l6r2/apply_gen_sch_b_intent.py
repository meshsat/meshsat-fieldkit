#!/usr/bin/env python3
"""apply_gen_sch_b_intent.py: DRAFT for board B's generator owner (Layer 6 record l6r2 round 5, MESHSAT-1357, 3 October 2026).
NOT APPLIED. It inserts 14 intent declarations (intent.node) into v2/ecad/tools/gen_sch_b.py, before the intent is written:
the voltage of nets on which a capacitor's rated voltage was open (finding F3), each derived from the circuit with its basis
and operating case (l6r2_intent.py; the page's section 8.4). Rendered by `l6r2_passives.py --write-drafts`; test_l6r2.py holds
this file equal to the render and proves its composition with every other pending draft of the generator.
Usage:  apply_gen_sch_b_intent.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_intent  # noqa: E402

BOARD = 'b'
DECLARATIONS = [
    ('LIME_SSTX_P', 5.0, 0.0,
     "LIME_SSTX_P: J_LIME pin 9, the LimeSDR Mini 2.4's USB 3 receive pair through the receptacle. The LimeSDR in its bay has no supply but this receptacle's VBUS, +5V_LIME (declared 5.0 V), so its pins stay within 0 V and that supply (the premise rule V-1 applies to every active part, here to the module behind the connector; its USB 3.0 controller is an FTDI FT601, whose own sheet is not held). Operating case: the LimeSDR enumerated at USB 3 speed; round 5 of record l6r2"),
    ('LIME_SSTX_N', 5.0, 0.0,
     "LIME_SSTX_N: J_LIME pin 8, the LimeSDR Mini 2.4's USB 3 receive pair through the receptacle. The LimeSDR in its bay has no supply but this receptacle's VBUS, +5V_LIME (declared 5.0 V), so its pins stay within 0 V and that supply (the premise rule V-1 applies to every active part, here to the module behind the connector; its USB 3.0 controller is an FTDI FT601, whose own sheet is not held). Operating case: the LimeSDR enumerated at USB 3 speed; round 5 of record l6r2"),
    ('W1A_CARD', 10.62, -10.62,
     "the slot 1 card's antenna lead (J_W1A), chain A: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, datasheet V1.0 p.3), 24.5 dBm, which is 5.31 V peak into 50 Ohm and 10.62 V with the lead fully reflecting (an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('W3A_CARD', 10.62, -10.62,
     "the slot 3 card's antenna lead (J_W3A), chain A: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, datasheet V1.0 p.3), 24.5 dBm, which is 5.31 V peak into 50 Ohm and 10.62 V with the lead fully reflecting (an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('WA_ANT', 10.62, -10.62,
     "the lead to A22's P2P jack (J_WOA), chain A: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, datasheet V1.0 p.3), 24.5 dBm, which is 5.31 V peak into 50 Ohm and 10.62 V with the lead fully reflecting (an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('SWA_O1', 13.92, -10.62,
     "the SKY13351-378LF's OUTPUT1 port, chain A: the sheet requires every RF port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared 3.3 V), plus the card's RF peak with the lead fully reflecting, 10.62 V. Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('SWA_O2', 13.92, -10.62,
     "the SKY13351-378LF's OUTPUT2 port, chain A: the sheet requires every RF port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared 3.3 V), plus the card's RF peak with the lead fully reflecting, 10.62 V. Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('SWA_IN', 13.92, -10.62,
     "the SKY13351-378LF's INPUT port, chain A: the sheet requires every RF port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared 3.3 V), plus the card's RF peak with the lead fully reflecting, 10.62 V. Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('W1B_CARD', 10.62, -10.62,
     "the slot 1 card's antenna lead (J_W1B), chain B: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, datasheet V1.0 p.3), 24.5 dBm, which is 5.31 V peak into 50 Ohm and 10.62 V with the lead fully reflecting (an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('W3B_CARD', 10.62, -10.62,
     "the slot 3 card's antenna lead (J_W3B), chain B: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, datasheet V1.0 p.3), 24.5 dBm, which is 5.31 V peak into 50 Ohm and 10.62 V with the lead fully reflecting (an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('WB_ANT', 10.62, -10.62,
     "the lead to A22's P2P jack (J_WOB), chain B: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, datasheet V1.0 p.3), 24.5 dBm, which is 5.31 V peak into 50 Ohm and 10.62 V with the lead fully reflecting (an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('SWB_O1', 13.92, -10.62,
     "the SKY13351-378LF's OUTPUT1 port, chain B: the sheet requires every RF port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared 3.3 V), plus the card's RF peak with the lead fully reflecting, 10.62 V. Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('SWB_O2', 13.92, -10.62,
     "the SKY13351-378LF's OUTPUT2 port, chain B: the sheet requires every RF port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared 3.3 V), plus the card's RF peak with the lead fully reflecting, 10.62 V. Operating case: transmit at full power into any load; round 5 of record l6r2"),
    ('SWB_IN', 13.92, -10.62,
     "the SKY13351-378LF's INPUT port, chain B: the sheet requires every RF port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared 3.3 V), plus the card's RF peak with the lead fully reflecting, 10.62 V. Operating case: transmit at full power into any load; round 5 of record l6r2"),
]


if __name__ == "__main__":
    sys.exit(l6r2_intent.main(BOARD, DECLARATIONS, sys.argv[1:]))
