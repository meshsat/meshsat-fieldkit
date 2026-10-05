P0 ROUND (5 October 2026, Slot A, `l8r2_p0.py`): V6's findings on the dedicated return disposed of: V6-B1 PROVISIONAL for the service cases on the named layout condition L8R2-F33a (the return sockets within 17 to 36 mm of the 5 V entries at 0.5 oz), the declared upper bound's printed row and the least-rating rows STILL OPEN; V6-B2 PROVISIONAL (the indirect paths bounded, the U.FL and HDMI contacts' ratings vendor tasks); V6-m12 a SESSION decision; V6-m8 labelled; L8R2-F31 stays OPEN, CONDITIONAL. Earlier status: # l8r2: the known engineering defects corrected at the desk (Layer 8 round 2, MESHSAT-1357)

Layer 8 record `l8r2`, 3 October 2026, branch `fnd/l8r2` from `f294dc13`; rounds 3 and 4 on branch `fnd/l8r3` from set 28's `37bc2f1d`. Prototype design, generator text, netlists and printed
figures: nothing is built, powered or measured, and **nothing here is applied to the tree**. Every apply script refuses the
repository's own generator until a `RELEASE.md` beside it names an accepted check of this record; none exists.

| File | What it is |
|---|---|
| `l8r2_p0.py`, `l8r2_p0.out` | P0 round (5 October 2026): V6-B1 (the series plane term and its realisability), V6-B2 (the indirect paths), V6-m12, V6-m8, C-DEV rev 2 (section 3h of the page) |
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
| `apply_gen_sch_b_gndret.py` | DRAFT, board B (round 7, task T5b, the owner's review RSM-01): the return's typical and peak derived in the generator from the rails that arrive on its lead connectors (13.30 A and 26.40 A, an UPPER BOUND; 27.9108 A with Layer 9's round 3 draft; 22.23 A on the committed generator), `J_54V` and the PoE return at R12 added; composes with Layer 9's draft in either order |
| `apply_gen_sch_b_fandec.py` | DRAFT, board B (round 7, L8R2-F32), fans12's companion: the row in `_dec_rule` that gives the cooler step-ups' two capacitors the class board B's decision 42 block reads; without it the composed generator stops on C704 |
| `apply_gen_sch_b_gndrtn.py`, `apply_gen_sch_a_gndrtn.py` | DRAFTS, boards B and A (round 8, the correction drafted for L8R2-F31): the dedicated ground return, three Amass XT60-F sockets `J_GR1` to `J_GR3` a board with both contacts on GND (the leads: XT60-M both ends, two 12 AWG conductors, 150 mm); board B's requires gndret first and names the sockets among the return's sources; board A's adds the sockets and their schematic block and leaves its GND declaration alone; release-guarded like every draft here |
| `check_gndret_netlist.py` | rounds 7 and 8: what the regenerated netlists and intent must show for the return (the leads read from the netlist, the sums, the PoE return, the loads; the return sockets whole on GND and named, and the same sockets whole on both boards); NOT DRAWN on the committed boards |
| `l8r2_gndret.py`, `l8r2_gndret.out` | rounds 7 and 8: the stop reproduced stage by stage; the load basis and its three figures; the return divided by resistance with EVERY vertex of the contact-resistance box enumerated at both ends of the copper's temperature (the recheck's corner reproduced, 10.6376 A; as drawn the return does not hold, **L8R2-F31 OPEN**); three corrections compared; the four drafts composed on both boards, thirteen mutations; the acceptance with the dedicated return on the composed netlists' census, each branch against the rating its maker prints and its condition; what the rows rest on that no maker prints; the fault cases; what Layer 9's author and the independent check need; regenerated with `_bin/regen_out.py` |
| `checks/astra-check-t5-recheck-cx41.md` | the collaborator's targeted recheck V3 of round 7 with Layer 9's round 3 (cx41), filed as received: NOT CONFIRMED; answered in the page's section 3g (round 8) |
| `inputs/` | Layer 7's cooler identity (`fnd/l7pwr` at `2087060b`) and Layer 5's round 2 findings (`fnd/l5r2` at `6902db8f`), the panel firmware's F-01 (`fnd/fw-panel` at `42c27369`), Layer 6's board C draft with its helper (`fnd/l6r2` at `7633ae0a`); round 3: record l9pwr's output (`fnd/l9pwr` at `38ef774c`), record l9stk's output and page (`fnd/l9stk` at `7388a84b`); rounds 7 and 8: Layer 9's two round 3 drafts (boards A and B), its output and its budget (`fnd/l9t5` at `841e6c7e`) and the coordinator's case rows (revision 3); byte for byte, `inputs/SOURCES.txt` |

**Round 8's state (4 October 2026, 22:40 CEST).** The recheck V3 (`checks/astra-check-t5-recheck-cx41.md`, NOT CONFIRMED) found
round 7's return calculation sampled and not a maximum. **L8R2-F31 is OPEN: round 8's correction is drafted and has not been read
by an independent check; nothing is applied to the tree, nothing is built, bought or measured.** DONE: V3 filed as received;
Layer 9's round 3 drafts, output and budget copied at `841e6c7e`; Amass's XT60 specification 2021V1 filed
(`v2/vendor/battery/amass-xt60-spec-2021v1-lcsc-c98733.pdf`); the calculation corrected (every vertex enumerated, refused unless
it lands on the monotone vertex; the recheck's corner reproduced, 10.6376 A; as drawn on C-DEV rev 1 a lead's pin 2 reaches
12.092 A against the printed 10 A and a ribbon conductor 2.672 A against the printed 1 A); three corrections compared and the
dedicated return of three XT60 leads drafted on both boards (`apply_gen_sch_a_gndrtn.py`, `apply_gen_sch_b_gndrtn.py`); both
boards composed with every draft they carry (board B in four orders to one generator; board A with the return draft first or
last to one netlist); the netlist checks DRAWN and thirteen mutations stopping or failing; the acceptance on the composed
census at the declared upper bound 27.9108 A, over every vertex and both copper ends: a VH pin 2 at most 4.9277 A (JST prints
10 A with AWG 16 on the standard header), a ribbon conductor at most 0.6352 A (Wurth prints 1 A at 25 C), an XT60 contact at
most 11.0326 A (Amass prints 30 A, and 35 A MAX with 12 AWG at a rise under 85 C), the ground shift at most 11.43 mV against
0.9418 V; the fault cases (one return lead out, one XT60 contact open and one VH pin 2 open stay inside the printed ratings and
are LATENT; every source at its bound at once does not); the page's section 3g restated on the merged figures; `test_l8r2`
34 passed, 0 failed, 0 skipped. NOT DONE: an independent check of round 8; `J_54V`'s pin 2 has no printed rating until its lead is AWG 16 (a harness row
for Layer 7); the XT60's aged contact resistance, every derating curve and every minimum contact resistance are not printed
(the dependences are named in `l8r2_gndret.out` 6d; three questions to the makers are drafted and UNSENT); the XT60-F land is not
read on this host and no KiCad export exists; the harness, contract and change-list rows are their owners'. NEXT ACTION: the
coordinator's independent check of round 8 (the page's section 3g lists what it should read); the integrator adds the two
return drafts to L4-E9's change list (board B: after gndret; board A: before mainpb).

**Round 7's state (task T5b, 4 October 2026, 20:00 CEST; its return calculation and its comparison of corrections are
WITHDRAWN by round 8, above).** DONE: the stop reproduced; the load basis and the capacity basis
reconciled; the declaration corrected by a draft (`apply_gen_sch_b_gndret.py`) and the second stop by another
(`apply_gen_sch_b_fandec.py`); board B's composition runs to its end with Layer 9's I-03 draft in any order; the netlist and
intent check with eight mutations; `test_l8r2` 31 passed. NOT DONE: the return path itself. **L8R2-F31 is OPEN**: the return
divides between five lead contacts and seventeen signal-ribbon conductors by resistance, and on the makers' printed contact
maxima a ribbon conductor passes its 1 A; a dedicated return (A1) is selected as the direction and is not drafted. No independent check has read this round, and nothing is applied to the tree. NEXT ACTION:
the coordinator's focused check of the page's section 3g; then A1's draft on boards A and B with Layers 5 and 7, or the
harness measurement of `l8r2_gndret.out` 3e.

Tests: `v2/ecad/tools/tests/test_l8r2.py` (`env -C v2/ecad/tools/tests python3 run.py test_l8r2 test_l8gnd test_public_hygiene`).
