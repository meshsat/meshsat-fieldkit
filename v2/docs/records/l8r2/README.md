# l8r2: the known engineering defects corrected at the desk (Layer 8 round 2, MESHSAT-1357)

Layer 8 record `l8r2`, 3 October 2026, branch `fnd/l8r2` from `f294dc13`; rounds 3 and 4 on branch `fnd/l8r3` from set 28's `37bc2f1d`. Prototype design, generator text, netlists and printed
figures: nothing is built, powered or measured, and **nothing here is applied to the tree**. Every apply script refuses the
repository's own generator until a `RELEASE.md` beside it names an accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8R2-KNOWN-DEFECTS.md` | the record: per defect the defect as found, the correction selected with its printed basis, the draft, the acceptance and the contract texts for Layer 5; the composition proof; findings; what stays owed. Item 1 board B's coolers (E11-40), re-decided in round 3 on record l9pwr's L9P-F02 (section 1r: the step-up kept, the modules' Fan_PWM at no more than 70 %), and in round 4's focused check (section 1s: the maximum withdrawn, slots 1 and 3 on slot 2's LM5176 stage, the fan at full speed); item 2 VBUS20's single faults (S-111); item 3 Layer 5's L5R2-F03, F04 and F05; item 4 board C's PI button; round 3's item 5, the pack path's return on boards A and E, and item 6, the energy chain's board E texts (record l9stk's findings). The solar guard and sense (P1-1) stay the supplier's |
| `apply_gen_sch_b_fans12.py` | DRAFT, board B: per slot a TPS61089 step-up to 12 V, a TPS259631 eFuse and two 2N7002 stages for the cooler fan |
| `apply_gen_sch_a_vbus20ov.py` | DRAFT, board A: a TPS48110-Q1 and a CSD19532Q5B cutting VIN_RAW when VBUS20 passes 24.25 to 25.31 V |
| `apply_gen_sch_b_panel5v.py` | DRAFT, board B: PANEL_5V behind a TPS259631 (1.375 to 1.614 A) ahead of F1 |
| `apply_gen_sch_a_d8v3.py` | DRAFT, board A: board D's 3.3 V behind a TPS259631 (0.224 to 0.269 A) |
| `apply_gen_sch_b_ph4.py` | DRAFT, board B: J_QMX and J_CAM on the JST PH 1x4 land |
| `apply_gen_sch_c_pibtn.py` | DRAFT, board C: the PI button on U1 P1.3 (PI_BTN_n) with R57 10 k and C27 as its debounce (the panel firmware's F-01) |
| `apply_gen_sch_a_packrtn.py`, `apply_gen_sch_e_packrtn.py` | DRAFT, boards A and E (round 3): GND declared as a rail returning CELL+ (A) and CELL_F (E) at the pack's 18 A, in each generator's intent table |
| `apply_gen_sch_a_slotlm.py` | DRAFT, board A (round 4, L9P-F02): slots 1 and 3 on slot 2's LM5176 stage (7.096 A loop at least), the AP64500s U4 and U6 retired; designators in the 500 block; after L4-E11's charger |
| `apply_energy_chain_e1oz.py` | round 3: `pcb_energy_chain.yaml`'s DOCK_ENTRY and SHORE_INPUT conductors at 1 oz with the widths their ratings need, for the integrator after l9stk's decision; idempotent, asserts each old text once, re-parses the YAML |
| `check_l8r2_netlist.py` | what the regenerated netlists must show, parsed; NOT DRAWN on the committed netlists |
| `l8r2_drafts.py`, `l8r2_drafts.out` | the figures with their classes, the composition on boards A, B and E, the designators, the netlist check; round 3's sections 2b (item 1 on record l9pwr's parsed figures), 6b (board E), 9 (the pack returns) and 10 (the energy chain); round 4's section 2c (L9P-F02's focused check); inputs pinned by sha256; regenerated with `_bin/regen_out.py` |
| `fetch_held_back.py` | TI's TPS4811-Q1 sheet (SLUSEE5E) into `v2/vendor/ti/held/`, and round 4's four San Ace catalogue pages into `v2/vendor/fans/held/`, each checked by sha256 (held back by their terms) |
| `inputs/` | Layer 7's cooler identity (`fnd/l7pwr` at `2087060b`) and Layer 5's round 2 findings (`fnd/l5r2` at `6902db8f`), the panel firmware's F-01 (`fnd/fw-panel` at `42c27369`), Layer 6's board C draft with its helper (`fnd/l6r2` at `7633ae0a`); round 3: record l9pwr's output (`fnd/l9pwr` at `38ef774c`), record l9stk's output and page (`fnd/l9stk` at `7388a84b`); byte for byte, `inputs/SOURCES.txt` |

Tests: `v2/ecad/tools/tests/test_l8r2.py` (`env -C v2/ecad/tools/tests python3 run.py test_l8r2 test_l8gnd test_public_hygiene`).
