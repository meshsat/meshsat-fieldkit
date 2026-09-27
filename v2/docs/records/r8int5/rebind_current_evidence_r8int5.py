"""r8int5: CON-010 and REQ-044 are bound to v2/docs/CURRENT-EVIDENCE.md; after the render at the end of the r8int5
integration they are re-read and rebound (the r8int4 script's method, the note naming this integration). Usage: from
the worktree root, rebind_current_evidence_r8int5.py "<what moved>" "<CON-010 read>" "<REQ-044 read>"."""
import os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edlib import rebind
REQ = 'v2/ecad/tools/pcb_requirements.yaml'; CE = 'v2/docs/CURRENT-EVIDENCE.md'
moved, con010, req044 = sys.argv[1:4]
res = {r['id']: r.get('evidence_result') for r in yaml.safe_load(open(REQ))['records']}
for rid, why in (('CON-010', con010), ('REQ-044', req044)):
    note = ("v2/docs/CURRENT-EVIDENCE.md re-read at the r8int5 integration of 27 September 2026 (set 5 of the handover: "
            "streams w3t, w3a, w3b, w3de and w3g), rendered after rules_status ran three times on the committed integration: "
            "%s; %s, so it stands %s on the file at {NEW}" % (moved, why, res[rid]))
    print(rid, rebind(REQ, rid, CE, '.', note))
