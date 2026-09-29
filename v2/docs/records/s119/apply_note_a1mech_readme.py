#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026), for the integrator: adds the second issue's
note on the charger rows to v2/docs/records/a1mech/README.md, directly after its title. It asserts the title occurs once, refuses a second run
(the page already carries the note's mark), writes, re-reads the page and checks it is its old text plus the note
(pagenote.py beside this script). --check validates and writes nothing. The page's own figures are left as the record
of the first issue; the note gives the second issue's beside them. Usage: python3 apply_note_a1mech_readme.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pagenote as PN  # noqa: E402

PAGE = "v2/docs/records/a1mech/README.md"
ANCHOR = "# Option A(i) mechanical work package: the lid pack, its harness, the open case's stability, the base pockets\n\n"
NOTE = PN.HEAD + (
    " **In this page:** section 9e's 4S18P case leaves 90.9 Wh at +20 C (was 91.0; down to about +12.9 C, unchanged); "
    '`records/a1int/reconcile_lid.out` second issue: the 4S9P lid at its 13.23 C basis leaves 164.9, 111.0 and 41.8 Wh '
    'unserved at 400, 650 and 1000 Wp (was 164.8, 110.9 and 41.7). The lid options with the chosen array, U3 at its 6.1 A '
    'minimum: tablet out (4S14P) 93.7 Wh typical and 85.5 Wh adverse (was 87.4; 85.8 Wh with U3B hour by hour), QMX out '
    '(4S15P) 125.2 and 116.6 Wh (was 118.5; 116.9 Wh hour by hour); both functions kept (4S9P) still NOT MET '
    '(`records/a1int/reconcile_lid_panel.out` third issue, `records/s119/reconcile_s119.out`).'
)

if __name__ == "__main__":
    sys.exit(PN.run(PAGE, ANCHOR, NOTE))
