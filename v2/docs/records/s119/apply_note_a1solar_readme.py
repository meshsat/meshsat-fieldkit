#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026), for the integrator: adds the second issue's
note on the charger rows to v2/docs/records/a1solar/README.md, directly after its title. It asserts the title occurs once, refuses a second run
(the page already carries the note's mark), writes, re-reads the page and checks it is its old text plus the note
(pagenote.py beside this script). --check validates and writes nothing. The page's own figures are left as the record
of the first issue; the note gives the second issue's beside them. Usage: python3 apply_note_a1solar_readme.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pagenote as PN  # noqa: E402

PAGE = "v2/docs/records/a1solar/README.md"
ANCHOR = "# a1solar: Option A(i)'s solar panel, the array's wiring and the entry it sets (MESHSAT-1357)\n\n"
NOTE = PN.HEAD + (
    " **In this page (`energy_runs.out`, third issue):** section 9's 4S18P at 40 degrees facing south MEETS with 90.6 Wh "
    'at +20 C and 26.4 Wh at +15 C in the typical case (was 90.6 and 26.5) and 87.8 and 23.6 Wh in the adverse case (was '
    "87.8 and 23.7), down to +12.9 and +13.2 C as before; a1elec's two-pack case (4S12P lid) MEETS with 30.7 Wh in the "
    'typical case (lid 0.5 Wh, down to +9.6 C, unchanged) and **26.7 Wh** in the adverse case (was 27.9; lid 0.0 Wh, down '
    'to +10.8 C, unchanged). **The planes (section 6, the 4S12P lid):** at 20 degrees only the south-facing plane now meets '
    'in both cases (was 15 degrees either side of south); at 30, 40 and 50 degrees the planes 15 degrees either side of '
    'south still meet in both, so the rule of section 7 (20 to 50 degrees within 15 degrees of south) no longer holds for '
    'the 4S12P lid at 20 degrees off south. For the two lid options the owner chooses between, 4S14P and 4S15P, every '
    'grid plane of the rule meets in both cases with U3 at its 6.1 A minimum (`records/s119/reconcile_s119.out` section 6); '
    'laid flat the 4S14P lid does not meet and the 4S15P lid meets in the typical case only.'
)

if __name__ == "__main__":
    sys.exit(PN.run(PAGE, ANCHOR, NOTE))
