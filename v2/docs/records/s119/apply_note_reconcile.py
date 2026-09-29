#!/usr/bin/env python3
"""DRAFT apply script (stream s119, S-119, MESHSAT-1357, 29 September 2026), for the integrator: adds the second issue's
note on the charger rows to v2/docs/records/a1int/RECONCILE.md, directly after its title. It asserts the title occurs once, refuses a second run
(the page already carries the note's mark), writes, re-reads the page and checks it is its old text plus the note
(pagenote.py beside this script). --check validates and writes nothing. The page's own figures are left as the record
of the first issue; the note gives the second issue's beside them. Usage: python3 apply_note_reconcile.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pagenote as PN  # noqa: E402

PAGE = "v2/docs/records/a1int/RECONCILE.md"
ANCHOR = '# Option A(i): the electrical and mechanical packages reconciled (MESHSAT-1357, 29 September 2026)\n\n'
NOTE = PN.HEAD + (
    ' **In this page:** the first table (`reconcile_lid.out`, second issue, pinned): 4S8P 259.0 Wh unserved (was 258.9); '
    '4S9P 164.9, 111.0 and 41.8 Wh unserved at 400, 650 and 1000 Wp (was 164.8, 110.9 and 41.7) and 1.9 Wh left at 650 Wp '
    'with the lid at +20 C (was 2.0; 29.4 Wh at 1000 Wp unchanged); 4S12P 30.3 and 0.7 Wh, 31.0 together (was 31.1), '
    "+9.6 C unchanged; 4S14P and 4S15P unchanged (94.0 and 125.5 Wh). The model's entry requirement: at least 5.61 A "
    '(116.2 W) into U3 (was 5.56 A, 115.1 W). The second table (`reconcile_lid_panel.out`, third issue): ratio B '
    'unchanged for every lid (4S14P 93.7 Wh, +3.8 C; 4S15P 125.2 Wh, +1.5 C); ratio C with U3 at its 6.1 A minimum: 4S14P '
    '**80.6 Wh, +6.0 C (was 87.4 Wh, +5.9 C)** and 4S15P **111.6 Wh, +3.9 C (was 118.5 Wh, +2.2 C)**; with U3 at 6.0 A '
    '71.4 Wh, +6.1 C (was 77.6) and 102.4 Wh, +4.0 C (was 108.7); 4S9P still NOT MET. The least current into U3 at ratio '
    "C: 5.62 A (4S14P) and 5.48 A (4S15P), was 5.57 and 5.43 A. U3B at its new bracket's low end, 0.947, costs 5.6 and "
    "5.7 Wh at C with U3 at 6.1 A (was 6.0 and 6.2 Wh at 0.96). On the deployment rule's grid (20 to 50 degrees, azimuth "
    '15 degrees either side of south) both lids meet in both cases; laid flat the 4S14P lid does not meet and the 4S15P lid '
    'meets in the typical case only (`records/s119/reconcile_s119.out` sections 2, 5 and 6). **The failing case:** at the '
    'FETs first drawn and drafted (U3 0.939, U3B 0.802) every case reads NOT MET, and with U3 as drawn but U3B as drafted '
    '(CSD18510Q5B, 0.802) ratio C reads NOT MET for both lids (section 3). The result therefore holds for the circuit only '
    "once U3B's draft carries FETs that support 0.961: `records/a1elec/TOPOLOGY.md` 3b still names CSD18510Q5B (open item "
    'that records/s119/apply_registry_s119.py opens). The notes of `reconcile_lid_panel.out` that the checks measured (the step and threshold stability, the clamp '
    "and the standby drain) were measured at the first issue's rows and are not re-measured."
)

if __name__ == "__main__":
    sys.exit(PN.run(PAGE, ANCHOR, NOTE))
