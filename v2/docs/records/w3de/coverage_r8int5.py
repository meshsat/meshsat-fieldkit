"""r8int5, stream w3de: pcb_rules_coverage.yaml's PWR-001 narrative, which lists boards D's and E's undeclared nets
(TRK_LSENSE among them, gone with S-47), gains the set 5 sentence for D and E as it did for A and B. Run from the root."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
COV = 'v2/ecad/tools/pcb_rules_coverage.yaml'
once(COV, """source and J_MON as its load (board A's writer). SET 5, BOARD B (stream w3b""",
"""source and J_MON as its load (board A's writer). SET 5, BOARDS D AND E (stream w3de, integrated in fnd/r8int5, 27
     September 2026, SC-57): gen_sch_d.py declares the PCM2912A's five regulator outputs, SAU_3V3 and the TPA6132A2's
     charge pump as nodes, gen_sch_e.py TRK_LDO33, E6_DVDD and E6_BST as nodes and SGP_VDD as a rail, and the nets the
     reading left undecided whose working voltage the circuit states are declared nodes; TRK_LSENSE is gone with S-47's
     bottom-leg sense (its successor TRK_CS is a node). In the stream's scratch PWR-001 read INCONCLUSIVE with 0 fails on
     both: RLY_K on D and FAN1_SW, FAN2_SW on E wait on their flyback diodes' sheets (S-76). SET 5, BOARD B (stream w3b""",
     marker="SET 5, BOARDS D AND E (stream w3de")
import yaml; yaml.safe_load(open(COV))
print("coverage_r8int5 (w3de): applied")
