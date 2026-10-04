# l8r2: the known engineering defects corrected at the desk (Layer 8 round 2, MESHSAT-1357)

Layer 8 record `l8r2`, 3 October 2026, branch `fnd/l8r2` from `f294dc13`; rounds 3 and 4 on branch `fnd/l8r3` from set 28's `37bc2f1d`. Prototype design, generator text, netlists and printed
figures: nothing is built, powered or measured, and **nothing here is applied to the tree**. Every apply script refuses the
repository's own generator until a `RELEASE.md` beside it names an accepted check of this record; none exists.

| File | What it is |
|---|---|
| `L8R2-KNOWN-DEFECTS.md` | the record: per defect the defect as found, the correction selected with its printed basis, the draft, the acceptance and the contract texts for Layer 5; the composition proof; findings; what stays owed. Item 1 board B's coolers (E11-40), re-decided in round 3 on record l9pwr's L9P-F02 (section 1r: the step-up kept, the modules' Fan_PWM at no more than 70 %), and in round 4's focused check (section 1s: the maximum withdrawn, slots 1 and 3 on slot 2's LM5176 stage, the fan at full speed), corrected in round 5 on the collaborator's check (section 1t) and in round 6 on its recheck (section 1u: the AP64500's Figure 24 a CONDITIONAL screen, the 0.1 % dividers, the slot leads at 6.6 A over the bounded start-up and fault envelope, the thermal acceptance over C4-1's whole matrix); item 2 VBUS20's single faults (S-111); item 3 Layer 5's L5R2-F03, F04 and F05; item 4 board C's PI button; round 7's item 7, board B's ground return (section 3g: the declaration corrected by a draft, the return's division OPEN as L8R2-F31); round 3's item 5, the pack path's return on boards A and E, and item 6, the energy chain's board E texts (record l9stk's findings). The solar guard and sense (P1-1) stay the supplier's |
| `apply_gen_sch_b_fans12.py` | DRAFT, board B: per slot a TPS61089 step-up to 12 V, a TPS259631 eFuse and two 2N7002 stages for the cooler fan |
| `apply_gen_sch_a_vbus20ov.py` | DRAFT, board A: a TPS48110-Q1 and a CSD19532Q5B cutting VIN_RAW when VBUS20 passes 24.25 to 25.31 V |
| `apply_gen_sch_b_panel5v.py` | DRAFT, board B: PANEL_5V behind a TPS259631 (1.375 to 1.614 A) ahead of F1 |
| `apply_gen_sch_a_d8v3.py` | DRAFT, board A: board D's 3.3 V behind a TPS259631 (0.224 to 0.269 A) |
| `apply_gen_sch_b_ph4.py` | DRAFT, board B: J_QMX and J_CAM on the JST PH 1x4 land |
| `apply_gen_sch_c_pibtn.py` | DRAFT, board C: the PI button on U1 P1.3 (PI_BTN_n) with R57 10 k and C27 as its debounce (the panel firmware's F-01) |
| `apply_gen_sch_a_packrtn.py`, `apply_gen_sch_e_packrtn.py` | DRAFT, boards A and E (round 3): GND declared as a rail returning CELL+ (A) and CELL_F (E) at the pack's 18 A, in each generator's intent table |
| `apply_gen_sch_a_slotlm.py` | DRAFT, board A (round 4, L9P-F02): slots 1 and 3 on slot 2's LM5176 stage (7.096 A loop at least), the AP64500s U4 and U6 retired; designators in the 500 block; after L4-E11's charger |
| `apply_gen_sch_b_rt500.py` | DRAFT, board B (round 5, O-20): the six AP64500 slot bucks' RT 68 k to 200 k 1 %, the maker's 500 kHz |
| `checks/astra-check-l9pf02-1.md` | the collaborator's focused check of round 4 (cx38), filed as received; answered in the page's section 1t |
| `checks/astra-check-l9pf02-2.md` | the collaborator's targeted recheck of round 5 (cx39, the last run), filed as received; answered in the page's section 1u |
| `apply_gen_sch_a_fb01.py` | DRAFT, board A (round 6, F5-03): both divider resistors of every LM5176 5.1 V stage at 0.1 %, 5.0019 to 5.1744 V |
| `apply_energy_chain_e1oz.py` | round 3: `pcb_energy_chain.yaml`'s DOCK_ENTRY and SHORE_INPUT conductors at 1 oz with the widths their ratings need, for the integrator after l9stk's decision; idempotent, asserts each old text once, re-parses the YAML |
| `check_l8r2_netlist.py` | what the regenerated netlists must show, parsed; NOT DRAWN on the committed netlists |
| `l8r2_drafts.py`, `l8r2_drafts.out` | the figures with their classes, the composition on boards A, B and E, the designators, the netlist check; round 3's sections 2b (item 1 on record l9pwr's parsed figures), 6b (board E), 9 (the pack returns) and 10 (the energy chain); round 4's section 2c (L9P-F02's focused check); inputs pinned by sha256; regenerated with `_bin/regen_out.py` |
| `fetch_held_back.py` | TI's TPS4811-Q1 sheet (SLUSEE5E) into `v2/vendor/ti/held/`, and round 4's four San Ace catalogue pages into `v2/vendor/fans/held/`, each checked by sha256 (held back by their terms) |
| `apply_gen_sch_b_gndret.py` | DRAFT, board B (round 7, task T5b, the owner's review RSM-01): the return's typical and peak derived in the generator from the rails that arrive on its lead connectors (13.30 A and 26.40 A, an UPPER BOUND; 27.78 A with Layer 9's I-03 draft; 22.23 A on the committed generator), `J_54V` and the PoE return at R12 added; composes with Layer 9's draft in either order |
| `apply_gen_sch_b_fandec.py` | DRAFT, board B (round 7, L8R2-F32), fans12's companion: the row in `_dec_rule` that gives the cooler step-ups' two capacitors the class board B's decision 42 block reads; without it the composed generator stops on C704 |
| `check_gndret_netlist.py` | round 7: what the regenerated netlist and intent must show for the return (the leads read from the netlist, the sums, the PoE return, the loads); NOT DRAWN on the committed board |
| `l8r2_gndret.py`, `l8r2_gndret.out` | round 7: the stop reproduced stage by stage, the load basis and its three figures, the return divided between the five lead contacts and the seventeen ribbon conductors by resistance on the makers' printed figures, the judgment (the declaration corrected; the return path not holding on the makers' printed figures, **L8R2-F31 OPEN**), four corrections compared, the composition in four orders, eight mutations, what Layer 9's author needs; regenerated with `_bin/regen_out.py` |
| `inputs/` | Layer 7's cooler identity (`fnd/l7pwr` at `2087060b`) and Layer 5's round 2 findings (`fnd/l5r2` at `6902db8f`), the panel firmware's F-01 (`fnd/fw-panel` at `42c27369`), Layer 6's board C draft with its helper (`fnd/l6r2` at `7633ae0a`); round 3: record l9pwr's output (`fnd/l9pwr` at `38ef774c`), record l9stk's output and page (`fnd/l9stk` at `7388a84b`); round 7: Layer 9's board B draft, its output and its budget (`fnd/l9t5` at `f70d3085`) and the coordinator's case rows; byte for byte, `inputs/SOURCES.txt` |

**Round 8's state (4 October 2026, 21:45 CEST): CHECKPOINT, INCOMPLETE, stopped at the session's usage limit.** The recheck V3
(`checks/astra-check-t5-recheck-cx41.md`, NOT CONFIRMED) found round 7's return calculation sampled and not a maximum; **L8R2-F31
is OPEN and nothing of round 8 is accepted or checked.** DONE: V3 filed as received; Layer 9's round 3 drafts, output and budget
copied at `841e6c7e` (the `f70d3085` copies replaced); Amass's XT60 specification 2021V1 filed
(`v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`); the two drafts of the dedicated ground return
(`apply_gen_sch_a_gndrtn.py`, `apply_gen_sch_b_gndrtn.py`: three XT60-F sockets a board, both contacts on GND; they apply, refuse
twice and refuse the tree, and both boards' generators ran with them on scratch copies); `check_gndret_netlist.py` reads the
return sockets on both boards; in `l8r2_gndret.py` the header, the inputs, `figures()` and the capacity model are rewritten (every
vertex of the contact-resistance box enumerated, refused unless it agrees with the monotone argument). A scratch run of that
model reproduced V3's corner (10.6376 A in a 5 V lead's pin 2 on C-DEV rev 1 at 76.25 C; 12.09 A at -20 C; a ribbon conductor
2.07 to 2.67 A) and, with three return leads, gave at most 4.93 A in a VH pin 2, 0.635 A in a ribbon conductor and 11.03 A in an
XT60 contact at the declared upper bound: scratch figures, NOT in a committed output. NOT DONE, and BROKEN AT THIS COMMIT:
`l8r2_gndret.py`'s `main()` still has round 7's body and does not run, `l8r2_gndret.out` is round 7's, and `test_l8r2`'s round 7
tests fail on the replaced input copies. NEXT ACTION: assemble `main()` from `wip-round8/` (its `NOTE.md` says how), add
section 6 (the acceptance from the composed netlists' census) and sections 7 to 9, regenerate the output with `_bin/regen_out.py`,
rewrite the round 7 tests and add round 8's, restate the page's section 3g on the merged figures, and run `test_l8r2`,
`test_l8gnd` and `test_public_hygiene`.

**Round 7's state (task T5b, 4 October 2026, 20:00 CEST).** DONE: the stop reproduced; the load basis and the capacity basis
reconciled; the declaration corrected by a draft (`apply_gen_sch_b_gndret.py`) and the second stop by another
(`apply_gen_sch_b_fandec.py`); board B's composition runs to its end with Layer 9's I-03 draft in any order; the netlist and
intent check with eight mutations; `test_l8r2` 31 passed. NOT DONE: the return path itself. **L8R2-F31 is OPEN**: the return
divides between five lead contacts and seventeen signal-ribbon conductors by resistance, and on the makers' printed contact
maxima a ribbon conductor passes its 1 A; a dedicated return (A1) is selected as the direction and is not drafted. No independent check has read this round, and nothing is applied to the tree. NEXT ACTION:
the coordinator's focused check of the page's section 3g; then A1's draft on boards A and B with Layers 5 and 7, or the
harness measurement of `l8r2_gndret.out` 3e.

Tests: `v2/ecad/tools/tests/test_l8r2.py` (`env -C v2/ecad/tools/tests python3 run.py test_l8r2 test_l8gnd test_public_hygiene`).
