# l8r2: the known engineering defects corrected at the desk (Layer 8 round 2, MESHSAT-1357)

Layer 8 record `l8r2`, 3 October 2026, branch `fnd/l8r2` from `f294dc13`. Prototype design, generator text, netlists and printed
figures: nothing is built, powered or measured, and **nothing here is applied to the tree**. Every apply script refuses the
repository's own generator until a `RELEASE.md` beside it names an accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8R2-KNOWN-DEFECTS.md` | the record: per defect the defect as found, the correction selected with its printed basis, the draft, the acceptance and the contract texts for Layer 5; the composition proof; findings; what stays owed. Item 1 board B's coolers (E11-40); item 2 VBUS20's single faults (S-111); item 3 Layer 5's L5R2-F03, F04 and F05. The solar guard and sense (P1-1) stay the supplier's |
| `apply_gen_sch_b_fans12.py` | DRAFT, board B: per slot a TPS61089 step-up to 12 V, a TPS259631 eFuse and two 2N7002 stages for the cooler fan |
| `apply_gen_sch_a_vbus20ov.py` | DRAFT, board A: a TPS48110-Q1 and a CSD19532Q5B cutting VIN_RAW when VBUS20 passes 24.25 to 25.31 V |
| `apply_gen_sch_b_panel5v.py` | DRAFT, board B: PANEL_5V behind a TPS259631 (1.375 to 1.614 A) ahead of F1 |
| `apply_gen_sch_a_d8v3.py` | DRAFT, board A: board D's 3.3 V behind a TPS259631 (0.224 to 0.269 A) |
| `apply_gen_sch_b_ph4.py` | DRAFT, board B: J_QMX and J_CAM on the JST PH 1x4 land |
| `apply_gen_sch_c_pibtn.py` | DRAFT, board C: the PI button on U1 P1.3 (PI_BTN_n) with R57 10 k and C27 as its debounce (the panel firmware's F-01) |
| `check_l8r2_netlist.py` | what the regenerated netlists must show, parsed; NOT DRAWN on the committed netlists |
| `l8r2_drafts.py`, `l8r2_drafts.out` | the figures with their classes, the composition on boards A and B, the designators, the netlist check; inputs pinned by sha256; regenerated with `_bin/regen_out.py` |
| `fetch_held_back.py` | TI's TPS4811-Q1 sheet (SLUSEE5E) into `v2/vendor/ti/held/`, checked by sha256 (held back by TI's terms) |
| `inputs/` | Layer 7's cooler identity (`fnd/l7pwr` at `2087060b`) and Layer 5's round 2 findings (`fnd/l5r2` at `6902db8f`), the panel firmware's F-01 (`fnd/fw-panel` at `42c27369`), Layer 6's board C draft with its helper (`fnd/l6r2` at `7633ae0a`), byte for byte, `inputs/SOURCES.txt` |

Tests: `v2/ecad/tools/tests/test_l8r2.py` (`python3 run.py test_l8r2 test_public_hygiene` from the tests folder).
