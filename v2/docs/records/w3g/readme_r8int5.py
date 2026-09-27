"""r8int5, stream w3g: the diagrams README brought to the rebuild at this integration (argv[1]: the tree it ran at).
The stream's text stays as the record of its rebuild at 38dcd764; the status paragraph, the counts, the findings and the
open items say what the rebuild on set 5's netlists found, and the integrator's adaptation of power_tree.py is recorded
as a session choice. Run from the worktree root."""
import os, sys, json, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
TREE = sys.argv[1]
P = 'v2/docs/diagrams/README.md'
def s16(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
NET = {L: s16(p) for L, p in (("A", "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"), ("B", "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"),
       ("C", "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net"), ("D", "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net"),
       ("E", "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net"), ("P", "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net"))}
CH = s16("v2/ecad/tools/pcb_energy_chain.yaml")
once(P, "**Status: drawn at `38dcd764`, with round 8 on all six boards.** Every diagram was rebuilt on 27 September 2026 from",
"""**Status: drawn at `%s`, with round 8 on all six boards and set 5 on boards A, B, D and E.** The r8int5 integration
(27 September 2026, branch `fnd/r8int5`) rebuilt every diagram again from the tree at `%s` (netlists A `%s`, B
`%s`, C `%s`, D `%s`, E `%s`, P `%s`; `pcb_energy_chain.yaml` `%s`), after set 5 changed
the netlists of A, B, D and E. `power_tree.py` refused them as stream w3g left it, and follows them now: board E's
tracker stage names Q3, U5 and Q6 (R5 senses in the bottom switches' leg since S-47, off the PV_P to TRK_OUT path),
the VIN_RAW lead runs from board E's P_VR to board A's J_VR1 to J_VR4 (EQ-16), and the legend calls board B's
coin-cell net VBAT_RTC (W3B-R1). The case drawings now read r8int4's case release (`c351115d`). The rest of this page
is stream w3g's record of its rebuild at `38dcd764`, with the counts and findings of `%s` given where they differ.
`build.py --check` reads 11 of 11 current against `MANIFEST.json`, whose `tree` is `%s`.

Stream w3g's rebuild: every diagram was rebuilt on 27 September 2026 from""" % (TREE, TREE, NET["A"], NET["B"], NET["C"], NET["D"], NET["E"], NET["P"], CH, TREE, TREE),
     marker="The r8int5 integration\n(27 September 2026, branch `fnd/r8int5`) rebuilt every diagram again")
once(P, "the power tree 6354 x 1476 pt, the control lines 4940 x 1202 pt;", "the power tree 6360 x 1476 pt, the control lines 4940 x 1202 pt;",
     marker="the power tree 6360 x 1476 pt")
once(P, """in their titles' document identities, the PDFs' page size and, on the case plan, a footer that now wraps inside the
page and one label set on white.""", """in their titles' document identities, the PDFs' page size and, on the case plan, a footer that now wraps inside the
page and one label set on white. At `%s` two Mermaid blocks differ from w3g's sources, the board interconnect's and the
power tree's dock edges (VIN_RAW on four 9 A pins at 14.10 A, EQ-16), and the case drawings read `c351115d`'s case
release (the plate's VHB lift 0.0, the as-coded plate and jacks moved; `case-drawings.md` names each input's commit).""" % TREE,
     marker="two Mermaid blocks differ from w3g's sources")
once(P, """Reading the netlists against the declared energy chain (`power-tree.md`, first sections) finds, at `38dcd764`, the""",
"""**At `%s`** the build prints three disagreements (items 1, 3 and 4 below) and no netlist finding: item 2 is gone
because r8int4 re-declared the chain's pack for D-06, item 5 because W3B-R1 renamed board B's coin-cell net VBAT_RTC,
and item 6 because set 5 (board A stream w3a) made R74 and R133 the top legs of U16's and U19's enable dividers
(POE_UVLO, PD_UVLO), as the stage table's Enable column shows. Item 4 still prints because the SHORE_INPUT note names
the SMCJ33A as the clamp corrected away at `faf8c981` (stream w3de's rewording), which the check reads as a claim.

At `38dcd764`, reading the netlists against the declared energy chain (`power-tree.md`, first sections) finds the""" % TREE,
     marker="the build prints three disagreements (items 1, 3 and 4 below)")
once(P, """rebuild); and every negative control must be refused (2841 at `38dcd764`,""", """rebuild); and every negative control must be refused (2823 at `%s`, 2841 at `38dcd764`,""" % TREE,
     marker="(2823 at `")
once(P, """stage cut down to one such part) and lists what it accepts: at `38dcd764`, 2665 entries tried, 17 accepted; 7 name""",
"""stage cut down to one such part) and lists what it accepts: at `%s`, 2656 entries tried, 15 accepted, 5 on the stage's
own path and the same 10 wrong attributions listed next; at `38dcd764`, 2665 entries tried, 17 accepted; 7 name""" % TREE,
     marker="2656 entries tried, 15 accepted, 5 on the stage's")
once(P, """Each rendered file was read back at `38dcd764` (`tools/readback.py`):""",
"""At `%s` the r8int5 integration read every rendered file back again (`tools/readback.py`: problems none, every PDF at
1.00 to 1.01 of its drawing's natural size) and looked at the case plan's raster and at the stages set 5 moved in
`power-tree.md` (board E's tracker, the VIN_RAW lead, U16's and U19's enables through R74 and R133): an AI check, not a
qualified review. Each rendered file was read back at `38dcd764` (`tools/readback.py`):""" % TREE,
     marker="the r8int5 integration read every rendered file back again")
once(P, """| SC-W3G-7 |""", """| SC-R8I5-1 | At the r8int5 integration, `power_tree.py`'s TREE and LEADS follow set 5's netlists: the tracker stage without R5, the VIN_RAW lead on P_VR and J_VR1, E5 routing for P_VR, the legend's VBAT_RTC and PWR-F12 sentences | the build refused set 5's netlists (R5 no longer on the path; J_BLK and J_DOCK pins 1 to 4 on GND) and writes nothing when it refuses | restore w3g's entries, which set 5's netlists refuse |
| SC-W3G-7 |""", marker="| SC-R8I5-1 |")
once(P, """- The power-tree legend's sentence "The chain file predates owner ruling D-06 and PWR-F12" is typed; it holds while
  findings 1 and 2 print, and must go when the chain owner re-declares the chain.""",
"""- The power-tree legend's sentence (since r8int5: "The chain file does not yet carry PWR-F12's F2 stage") is typed; it
  holds while finding 1 prints and must go when the chain owner adds the F2 stage.""", marker="does not yet carry PWR-F12's F2 stage\") is typed")
print("readme_r8int5: applied")
