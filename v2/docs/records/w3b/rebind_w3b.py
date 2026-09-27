"""r8int5, stream w3b: FEA-006 is bound to DECOUPLING.md, whose section 10 board B row page_drafts_r8int5.py rewrote."""
import os, sys, yaml
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import rebind
REQ = 'v2/ecad/tools/pcb_requirements.yaml'
res = {r['id']: r.get('evidence_result') for r in yaml.safe_load(open(REQ))['records']}
note = ("v2/docs/feasibility/DECOUPLING.md re-read at the r8int5 integration of stream w3b (27 September 2026): one row "
        "changes, section 10's 'G4 to G7, G10' row, whose last sentences now say board B's generator writes class and basis "
        "on every declaration (the r8b map with C65, C66, C508 and C509 corrected, C72 to C74 added, 277 entries) where they "
        "said it did not yet; the seats still wait for board B's next placement, T1 to T10 and G1 to G14's other rows are "
        "byte-identical, and the blocker's closing evidence (the per-class requirement merged with DEC-001, each generator "
        "read back, the circuit gaps closed) is not met by a class being written, so it stays %s on the file at {NEW}" % res['FEA-006'])
print('FEA-006', rebind(REQ, 'FEA-006', 'v2/docs/feasibility/DECOUPLING.md', '.', note))
