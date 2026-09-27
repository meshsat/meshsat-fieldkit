"""r8int5, stream w3g: power_tree.py follows set 5's netlists, which it refused as the stream left it (it was built on
38dcd764's): board E's tracker senses on its bottom leg since S-47 (R5 is off the PV_P to TRK_OUT path), VIN_RAW
crosses the dock on board E's P_VR and board A's J_VR1 to J_VR4 since EQ-16 (J_BLK and J_DOCK pins 1 to 4 are ground),
board B's coin-cell net is VBAT_RTC since W3B-R1. Run from the worktree root; idempotent by marker."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
P = 'v2/docs/diagrams/tools/power_tree.py'
once(P, '''    ("E", "PV_P", "TRK_OUT", ("Q3", "U5", "R5", "Q6"), "solar tracker (bench-fitted)"),''',
        '''    # set 5 (S-47, stream w3de): R5 senses in the bottom switches' leg (TRK_CS to GND), off the PV_P to TRK_OUT path
    ("E", "PV_P", "TRK_OUT", ("Q3", "U5", "Q6"), "solar tracker (bench-fitted)"),''', marker='("Q3", "U5", "Q6"), "solar tracker')
once(P, '''    ("E", "VIN_RAW", "J_BLK", "A", "VIN_RAW", "J_DOCK", "E5 targets 1 to 4, spring pins J_DOCK 1 to 4"),''',
        '''    # set 5 (EQ-16, stream w3de): VIN_RAW crosses on board E's 12 AWG pad P_VR to E5 and board A's four 9 A pins
    ("E", "VIN_RAW", "P_VR", "A", "VIN_RAW", "J_VR1", "12 AWG to E5, four 9 A spring pins J_VR1..4 (EQ-16)"),''',
     marker='"P_VR", "A", "VIN_RAW", "J_VR1"')
once(P, '''        if ra in ("P_CP", "J_BLK"):''', '''        if ra in ("P_CP", "P_VR", "J_BLK"):''', marker='("P_CP", "P_VR", "J_BLK")')
# (the census paragraph prints only while a netlist finding names R74 or R133; set 5 closed that finding, so no
# branch is added for it: the stage table's Enable column shows U16 and U19 through R74 and R133)

import re
t = open(P).read()
n = t.count("board B's VBAT is its CR2032 net")
if n:
    t = t.replace("board B's VBAT is its CR2032 net", "board B's VBAT_RTC is its CR2032 net, VBAT until W3B-R1")
    open(P, 'w').write(t)
print("power_tree_r8int5: applied (%d NOTE text)" % n)
# the legend's typed sentence: r8int4 re-declared the chain's pack (D-06); PWR-F12's F2 stage is what it still lacks
once(P, '''The chain file predates owner ruling "
          "D-06 and PWR-F12: see power-tree.md.''', '''The chain file does not yet carry "
          "PWR-F12's F2 stage (its pack follows D-06 since r8int4): see power-tree.md.''', marker="PWR-F12's F2 stage (its pack follows D-06 since r8int4)")
print("power_tree_r8int5: legend sentence")
