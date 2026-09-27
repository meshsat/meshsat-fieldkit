"""r8int5: S-47's progress sentence (written by stream w3de's registry script) called the pcb_sensitive.yaml and
gen_pcb_e3.py knock-ons still open, but the integration applied both drafts in the same commit (b7f96784). Run from the
worktree root."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edlib import once
P = 'v2/ecad/tools/pcb_requirements.yaml'
once(P, """      conductor as board A's LM5176 CS nodes are under F-PR-04). Still open: the drafted knock-ons in
      pcb_sensitive.yaml (board e's switch list, TRK_CS for TRK_LSENSE, and Kelvin rows) and gen_pcb_e3.py
      (PATTERNS, the TRKS region, v2/docs/records/w3de/), and item 10, the boost diodes (a silicon part with its
      sheet and order code, or the BAT54's own sheet read against 8705af p.29).""",
"""      conductor as board A's LM5176 CS nodes are under F-PR-04). The knock-ons landed in the same integration
      (fnd/r8int5, b7f96784): pcb_sensitive.yaml board e (TRK_CS in the switch list for TRK_LSENSE, the Kelvin rows
      TRK_CSP and TRK_CSN) and gen_pcb_e3.py (PATTERNS, C63 and C64 in the TRKS region, a marker that stops the
      placement until P_VR and P_VN are placed). Still open: item 10, the boost diodes (a silicon part with its
      sheet and order code, or the BAT54's own sheet read against 8705af p.29), and board E's next placement.""",
     marker="The knock-ons landed in the same integration")
print("s47_fix_r8int5: applied")
