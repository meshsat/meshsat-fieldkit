#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026), for the integrator: adds the second issue's
note on the charger rows to v2/docs/records/a1elec/README.md, directly after its title. It asserts the title occurs once, refuses a second run
(the page already carries the note's mark), writes, re-reads the page and checks it is its old text plus the note
(pagenote.py beside this script). --check validates and writes nothing. The page's own figures are left as the record
of the first issue; the note gives the second issue's beside them. Usage: python3 apply_note_a1elec_readme.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pagenote as PN  # noqa: E402

PAGE = "v2/docs/records/a1elec/README.md"
ANCHOR = "# a1elec: Option A(i)'s electrical work package (MESHSAT-1357)\n\n"
NOTE = PN.HEAD + (
    ' **In this page, the two-pack model (`energy_two_pack.out`, second issue):** the design case (E2, lid at 13.23 C) keeps '
    '30.3 Wh in the base and 0.7 Wh in the lid, **31.0 Wh together (was 31.1)**, down to a lid at +9.6 C (unchanged); the '
    'aggregate 4S18P 90.9 Wh (was 91.0); the base at +15 C as well 9.6 Wh (was 9.7). The entry requirement: at least '
    "**5.61 A (116.2 W)** into U3 held at the limit's minimum (was 5.56 A, 115.1 W) and 5.88 A (121.7 W) for the full "
    '31.0 Wh (was 5.81 A, 120.3 W, 31.1 Wh). As generated (E1, U3 at 4.15 A): NOT MET, 382.7 Wh unserved, stops at hours '
    '43 and 32 (was 374.5 Wh, 44 and 32); the front end at its limits: 4.3 A 338.0 Wh unserved (was 329.4), 5.0 A 130.0 Wh '
    '(was 119.1), 5.7 A MEETS with 12.7 Wh (was 18.6); E1 with 650 and 800 Wp 232.1 and 193.4 Wh unserved (were 222.8 and '
    "184.1). At E2's busiest hour U3 loses 2.7 W at 0.979 (was 2.6 W at 0.98) and U3B 2.2 W at 0.961 on 55.2 W in (was "
    "1.4 W at 0.975 on 55.3 W), so board A's charging peak is about **15.1 W** (was about 14.2 W; the E1 and E3 columns "
    "of CHARGER.md's loss table are not re-derived and stay the first issue's); over 72 h U3B loses 34.9 to 50.0 Wh (was "
    "22.3 to 31.7) and the charge loop 5.6 to 8.1 Wh (was 5.7 to 8.2). U3's L2 is now drawn as 4.7 uH XAL1010-472ME at "
    "400 kHz (decision 56): 2.31 A p-p ripple and a 9.82 A peak at that hour (the first issue's 3.3 uH figures, 10.32 A at "
    "400 kHz and 9.50 A at 800 kHz, describe the inductor board A no longer draws). **U3B's FETs:** the carried 0.961 is "
    'U3B with CSD17578Q5A in all four positions on its drafted 800 kHz row (`records/s117/U3B-NOTE.md` way (a); REGN '
    "33.0 mA typical and 49.9 mA at the makers' maxima in buck-boost against its 50 mA minimum limit); TOPOLOGY.md 3b still "
    'names CSD18510Q5B, with which U3B reads 0.802 and ratio C of both lid options is NOT MET (`records/s119/reconcile_s119.out` '
    "section 3). Open item S-121 carries the draft's FET choice (way (a) or the 400 kHz row, way (b), 0.974)."
)

if __name__ == "__main__":
    sys.exit(PN.run(PAGE, ANCHOR, NOTE))
