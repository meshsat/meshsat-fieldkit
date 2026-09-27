"""r8int5, stream w3g: two of its ARCHITECTURE.md reference lines state what the rebuild found, and the rebuild at this
integration found other things: the power tree's sweep counts and findings (set 5 closed R74/R133 and renamed board B's
coin-cell net; r8int4 corrected the chain's pack header), and the case drawings, which now read r8int4's case release
(c351115d) instead of being unchanged. argv[1]: the tree the rebuild ran at. Run from the worktree root."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
TREE = sys.argv[1]
P = 'v2/docs/ARCHITECTURE.md'
once(P, "(the build's own substitution sweep at `%s`: 2665 tried, 17 accepted, 10 of them wrong attributions)" % TREE,
        "(the build's own substitution sweep at `%s`: 2656 tried, 15 accepted, 10 of them wrong attributions)" % TREE,
     marker="2656 tried, 15 accepted, 10 of them wrong attributions")
once(P, "the stages, the leads, four disagreements between the energy chain and the netlists (F2 not a chain stage, the pre-D-06 pack, the U7 fault-current basis, the SMCJ33A note), board B's own VBAT net and board A's R74 and R133, each with both pins on one enable net (R4T-F3's open half), are in `diagrams/power-tree.md`.",
        "the stages, the leads and three disagreements between the energy chain and the netlists (F2 not a chain stage, the U7 fault-current basis, the SMCJ33A the SHORE_INPUT note names, now as the clamp corrected away) are in `diagrams/power-tree.md`; set 5 closed the netlist finding the rebuild at `38dcd764` printed (board A's R74 and R133, R4T-F3's open half, now enable dividers).",
     marker="set 5 closed the netlist finding the rebuild at `38dcd764` printed")
once(P, "re-drawn at `%s`: round 8 and set 5 changed none of the figures they read, and the plan's footer now wraps inside the page." % TREE,
        "re-drawn at `%s` from the case release of `c351115d` (its `frame_seat.py`, `panel1450.py`, `pcb_board_facts.yaml` and `CASE-MARGINS.md`, with the plate's VHB lift now 0.0 and the as-coded plate and jacks moved); round 8 and set 5 changed none of the figures they read, and the plan's footer wraps inside the page." % TREE,
     marker="from the case release of `c351115d`")
print("architecture_counts_r8int5: applied")
