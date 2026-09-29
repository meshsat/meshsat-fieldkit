#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026), for the integrator: adds the second issue's
note on the charger rows to v2/docs/records/a1elec/TOPOLOGY.md, directly after its title. It asserts the title occurs once, refuses a second run
(the page already carries the note's mark), writes, re-reads the page and checks it is its old text plus the note
(pagenote.py beside this script). --check validates and writes nothing. The page's own figures are left as the record
of the first issue; the note gives the second issue's beside them. Usage: python3 apply_note_topology.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pagenote as PN  # noqa: E402

PAGE = "v2/docs/records/a1elec/TOPOLOGY.md"
ANCHOR = '# TOPOLOGY: two separately protected packs at the system node (Option A(i), stream a1elec, MESHSAT-1357)\n\n'
NOTE = PN.HEAD + (
    ' **In this page, the two-pack model (`energy_two_pack.out`, second issue):** the design case (E2, lid at 13.23 C) keeps '
    '30.3 Wh in the base and 0.7 Wh in the lid, **31.0 Wh together (was 31.1)**, down to a lid at +9.6 C (unchanged); the '
    'aggregate 4S18P 90.9 Wh (was 91.0); the base at +15 C as well 9.6 Wh (was 9.7). The entry requirement: at least '
    "**5.57 A (115.4 W)** into U3 held at the limit's minimum (was 5.56 A, 115.1 W) and 5.83 A (120.6 W) for the full "
    '31.0 Wh (was 5.81 A, 120.3 W, 31.1 Wh). As generated (E1, U3 at 4.15 A): NOT MET, 377.2 Wh unserved, stops at hours '
    '44 and 32 (was 374.5 Wh); the front end at its limits: 4.3 A 332.2 Wh unserved (was 329.4), 5.0 A 122.4 Wh (was '
    '119.1), 5.7 A MEETS with 17.1 Wh (was 18.6); E1 with 650 and 800 Wp 225.9 and 187.2 Wh unserved (were 222.8 and '
    "184.1). At E2's busiest hour U3 loses 2.7 W at 0.979 (was 2.6 W at 0.98) and U3B 1.5 W at 0.972 on 55.2 W in (was "
    "1.4 W at 0.975 on 55.3 W), each with its sense resistors inside, so board A's charging peak is about **13.9 W** (was "
    'about 14.2 W, which counted R16, R17, R16B and R17B twice); over 72 h U3B loses 25.1 to 35.6 Wh (was 22.3 to 31.7) and '
    "the charge loop, now 23 mOhm without U3B's RSR, 4.7 to 6.7 Wh (was 5.7 to 8.2). U3's L2 is drawn as 4.7 uH "
    "XAL1010-472ME at 400 kHz (decision 56): 2.31 A p-p ripple and a 9.82 A peak at that hour (the first issue's 3.3 uH "
    "figures describe the inductor board A no longer draws). **U3B** is drawn on U3's 400 kHz row by the session decision of "
    '`records/s119/apply_decision_s119.py` (TOPOLOGY.md 3b and CHARGER.md 2 carry it as their second issue): Q7B and Q9B '
    'CSD17578Q5A, Q8B and Q10B CSD17577Q5A, L2B XAL1010-472ME, 191 k, R16B 10 mOhm, IIN_HOST 6.2 A; REGN 32.6 mA at the '
    "makers' maxima against its 50 mA minimum limit; with the first-drafted CSD18510Q5B U3B read 0.802 and ratio C of both "
    'lid options was NOT MET (`records/s119/reconcile_s119.out` section 4).'
)

if __name__ == "__main__":
    sys.exit(PN.run(PAGE, ANCHOR, NOTE))
