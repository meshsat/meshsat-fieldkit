#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026), for the integrator: adds the second issue's
note on the charger rows to v2/docs/records/energy/ENERGY-RECONCILIATION.md, directly after its title. It asserts the title occurs once, refuses a second run
(the page already carries the note's mark), writes, re-reads the page and checks it is its old text plus the note
(pagenote.py beside this script). --check validates and writes nothing. The page's own figures are left as the record
of the first issue; the note gives the second issue's beside them. Usage: python3 apply_note_energy_reconciliation.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pagenote as PN  # noqa: E402

PAGE = "v2/docs/records/energy/ENERGY-RECONCILIATION.md"
ANCHOR = '# M1 energy reconciliation: the pack, the panel, the night and the mission as written\n\n'
NOTE = PN.HEAD + (
    " **In this page:** section 4's chain into the node 0.930 x 0.930 x 0.979 = 0.8467 (was 0.93 x 0.93 x 0.98 = 0.8476), "
    'bracket 0.787 to 0.925 (was 0.782 to 0.926); 100 Wp gives 320 Wh a day at the node in September and 90 in December as '
    "before (320.1 and 89.9, were 320.4 and 90.0), the low brackets 253 and 71 (were 251 and 70); the window's 20 kWp "
    "ceiling 1355, 1023 and 623 Wh a day in June, September and December (were 1356, 1024 and 624; 9c's 1023.9 is the "
    "independent recompute's own sum, now 1022.8, `checks/recompute.out` second issue); a 100 Wp panel exceeds 42.8 W at "
    "the node only above about 537 W/m2 (was 536); section 5's September run from 06:00 leaves 1871 Wh unserved (was 1870, "
    "first stop unchanged at hour 8); the pack that would carry M1 alone 2121 Wh (was 2120); section 6f's vehicle entry "
    'chain 0.910 (was 0.911). Section 9 (`energy_architecture.out`, second issue): in the 100 W window 4S19P needs 1350 Wp '
    '(was 1300), 900 and 1300 Wp need one string more, and 4S16P no longer meets up to the 3 kWp swept (was from 2100 Wp); '
    'the 200 W window is unchanged (4S16P from 350 Wp, 4S15P from 650 Wp), but 300 Wp needs 4S21P (was 4S20P). 9d: 4S18P '
    'in the 100 W window 41.32, 42.17 and 42.74 W at 1000, 1300 and 1500 Wp (were 41.35, 42.20 and 42.77). 9e: 4S15P, 650 '
    'Wp, 3.5 Wh (was 3.6); 4S16P, 400 Wp, 18.1 Wh (was 18.2); 4S18P, 400 Wp, 200 W window, **90.9 Wh** at +20 C (was 91.0), '
    '26.8 Wh at +15 C and +12.9 C unchanged; with 650 Wp 112.7 and 48.5 Wh (were 112.8 and 48.6); inside the 100 W window '
    '4S19P with 1300 Wp **no longer meets at any cell temperature up to +40 C** (was about +19.9 C) and 4S18P with 1600 Wp '
    "needs about +19.0 C (was +18.9). Elsewhere: section 6's option table, set 1 in June 32.2 Wh (was 32.3) and set 3 in "
    "June 67.7 Wh (was 67.8); PS-IDLE-SPEC at its LOW of 33.1 W on two packs in September 607 Wh unserved (was 606); "
    "section 8's June row (`energy_4s6p.out`, re-pinned) 729 Wh unserved (was 728). REQ-072's verdict is unchanged: FAIL."
)

if __name__ == "__main__":
    sys.exit(PN.run(PAGE, ANCHOR, NOTE))
