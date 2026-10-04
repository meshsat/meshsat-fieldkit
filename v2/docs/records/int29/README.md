# int29: integration set 29 (Layers 4, 5, 8, 9 and 12's rounds onto set 28; MESHSAT-1357)

Prototype design: nothing here has been built, bought, powered or measured. This folder is the record of integration set 29 of
4 October 2026, branch `fnd/int29` from main `64cd25ee` (set 28, `d834e6a7`, with its record). The owner's instructions bind it:
the instruction of 2 October 2026, the supplier amendment of 3 October and the integration-order correction of 4 October (finish
every intended change, regenerate until stable, commit the candidate, bind its manifest, check that commit, promote that commit).
`RESULT.md`, written after the gate, holds the candidate, the gate's lines and the promotion.

## What this set changes nothing about

**Promotion of this set closes no power item, is not power-design closure and releases nothing for fabrication.** The states it
carries, each as its record gives it:

| Item | State in this set |
|---|---|
| F01 (D-17, Layer 9's L9P-F01: the all-transmit basis needs 16.214 V rest against REQ-018's 15.5 V) | **OPEN.** REQ-018's 15.5 V is unchanged; the 16.1 V floor is withdrawn |
| FAN_OK (every fan supply off while the PA keys) | **REJECTED, never implemented.** The collaborator's advisory challenge of 4 October 2026 (an AI review, advisory; filed with set 30) found it not supported as proposed: its electrical argument held the compute modules at a typical figure no drawn control enforces, and its 0.126 V margin has no guaranteed basis against the cells' resistance and the gauge's current error. The owner kept it rejected. Its drafts R-210 to R-212 are not written; L4-E9's Part B (its reconciliation) stays on its branch, NOT in this set. D-17's correction is the plan's T5 |
| The device rail (I-03, L9P-F03: 7.472 A against the stage's 7.0957 A at the least load voltage) | OPEN |
| The solar entry (B6: D-10 and D-16) | OPEN, a supplier correction scope |
| The pack path's protection (W4DP-F2) | a latch-off breaker selected and drafted (record l8p, record l9stk section 15); the independent check read CONFIRMED AS CONDITIONAL for the breaker, the selection and the restart inhibit. OPEN: B-R2's remainder (board P's route R1 is on a branch, NOT in this set), DD-3, DD-5, E11-37 |
| The slot stages (L9P-F02) | CONDITIONAL on C4-1 to C4-6. The collaborator's check read NOT CONFIRMED and its recheck NOT CLOSED; the coordinator's later check does not replace those verdicts |
| The outer copper weight of boards A and E | the owner's decision, not taken |

## What the set holds (first-parent order)

| Commit | What |
|---|---|
| `82aafa70`, `9dbab93b` | Layer 5's round 4 (`fnd/l5r4` at `a694b279`): the slot-fault rule; CFL-001, 005, 014, 015 and 016 rebound to its PANEL.md |
| `91b053a6` | the panel firmware's round 4 (`fnd/fw-r4` at `8d396dfd`) |
| `778f82e5` | L4-E7's round 6 (`fnd/l4e7r6` at `914a2f5a`): the backstop draft's decoupling classes (L8P-F01) |
| `ad61c505` | Layer 9's power budget, round 2 (`fnd/l9pwr2` at `51821143`) |
| `763e73d5` | Layer 9's stackups, the pack path's copper and its protection (`fnd/l9stk` at `0d72880b`) |
| `d9b9092a` | Layer 8's round 3 (`fnd/l8r3` at `89924e40`): slots 1 and 3 drafted onto the LM5176 stage |
| `c56d9de3` | Layer 8's breaker drafts (`fnd/l8p` at `e1bc3cba`) |
| `e03c7d2c` | L4-E9's round 8 (`fnd/l4e9r8` at `5eb6e74f`): D-17 OPEN, the raised floor withdrawn |
| `2855802e` | L4-E11's round 9 (`fnd/l4e11r9` at `e60a94a8`) |
| `f1eec19e`, `6937ba73`, `715d4f5e`, `e58e906a` | the reviews of the supplier package and its addendum filed as received and designated in `ARCHIVED-REVIEWS.yaml`; the addendum's revisions 1 to 3 |
| `966ce983`, `1dd6c6a4` | `LAYER-STATUS.md` brought to sets 28 and 29 (`apply_layer_status_set29.py`); then L9P-F02's verdicts stated as read and FAN_OK as rejected (`apply_layer_status_set29b.py`) |
| `d57e6e37` | the pages rendered with the full evidence archive installed (984 files); CURRENT-EVIDENCE did not move, no rebind |
| `99a59252` | L4-E11 re-pinned (`apply_set29_repins.py --stage pins`) |
| `63680242` | L4-E9's set 29 rows A to A3 (`fnd/l4e9s29` at `1efaf66a`) |
| `69921ce8` | the freeze (`_bin/freeze_l4_chain.sh`): stable in its second pass; L4-E7's results cache rekeyed by one recompute, output byte-identical |
| `c6857c68` | the test procedures refreshed to L4-E11's round 9 (`fnd/tp29` at `b367a77d`); TP-E11-29 marked not executable while E-1's limit is under correction |
| `c824e918` | Layer 5's row LH-04b restated after L4-E9's rounds 7 and 8 corrected LH-04's pointer (`apply_l5pwr_lh04b.py`); finding L5-F13 for the contract text |
| `589b4980` | the later stage, part 1: the outputs of Layers 5 to 8 regenerated through regen_out |
| `ab1f67e1` | three readers brought to the merged tree (`apply_set29_readers.py`: test_l8p, l6r2's change chain, l8r2's board E round) |
| `0534f61e`, `6292b5e4` | Layer 7's page on its regenerated figures, then finding F-L7-12 corrected: the fans' heat on one basis per use (`apply_l7pwr_set29.py`, `apply_l7pwr_f12.py`) |
| `541f1e9a` | Layer 9's two records brought to the merged tree (`fnd/l9r3` at `0d1818f6`) |
| `dc99897f` | the panel firmware's contract test read as Layer 5's F-15 follow-up words FW-C05 (`apply_set29_fw_test.py`) |

After the last merge: the freeze helper's stability pass as the freshness check (no file a Layer 4 reader pins changed after `69921ce8`: the readers take Layer 7's and Layer 9's records by commit or by copied input), the later stage (`apply_set29_repins.py --stage later`,
`scan_printed_pins.py`), the candidate commit, `candidate_guard.py record`, the targeted modules, then the three suite passes and
`suite_gate.py`.

## Known residues, carried to set 30 by name (found on 4 October after the freeze; S29-R5 corrected here, the rest carried)

| Id | Residue | Owner in set 30 |
|---|---|---|
| S29-R1 | E-1's acceptance (L4-E11 round 9: each battery FET's installed path at most 45.88 K/W, 1.345 W a FET) assumes the current splits evenly between the three FETs. With unequal on-resistance one FET can dissipate up to 9/8 of the even-split power (the maximum of r/(R+2r)^2 over r is at r = R/2). The limit is under correction; TP-E11-29 is marked not executable | L4-E11's author |
| S29-R2 | L4-E11's 17d row for E11-37, L4-E9's 5d "What transfers" cell for E11-37 and its VBAT settings cell still describe the pair of battery FETs; the selection is three | L4-E11's and L4-E9's authors |
| S29-R3 | L4-E9's register rows R-206 to R-209 and its copied inputs read record l8p at `515f6cf2`, which named the automatic-retry LM5069MM-2. The selection is the latch-off LM5069MM-1 (record l8p at `e1bc3cba`, record l9stk 15.4b, both in this set). The sense pair and the FETs are the same in both revisions (read by diff); the part's name and the copies' revision are stale. (Layer 9's budget no longer reads a copy: since `541f1e9a` it reads the tree's protection output and names the -1.) | L4-E9's author |
| S29-R4 | three of the bring-up page's six quotes of record l8r2 are of its older round (the page's pinned input copies still match their own commits) | the procedures' author |
| S29-R5 | CORRECTED in this set (`1dd6c6a4`): `LAYER-STATUS.md` had printed the coordinator's check of L9P-F02 alone as "CLOSED AS CONDITIONAL"; it now states the collaborator's NOT CONFIRMED and NOT CLOSED beside it and the corrections as UNVERIFIED | done |
| S29-R6 | L5-F13: the `service` strings of IF-AE-DOCK `pack_pins` and IF-PE-PACK `power` in `pcb_interfaces.yaml` still carry the pointer L4-E9's round 7 withdrew; restating them is a registry change for set 30 | Layer 5's contract owner |
| S29-R7 | F-L7-12's remainder: the mixers have no stated envelope (their rated 2.04 W at 12 V is used in both bases against U22's 12.431 V top); R-150 restates E5's line on one named basis | Layer 7's next round, L4-E12 |
| S29-R8 | The thermal guard RT1 (PRF15BB103): L4-E11's round 10 (on a branch) reports no printed resistance between 25 C and 110 C, so the guard's no-trip side in the 18 A service rests on no printed point; under the focused check V1 | record l9stk, record l8p |

## Files

| File | What it is |
|---|---|
| `apply_set29_repins.py` | `--stage pins` (before the freeze) and `--stage later` (after it): the readers' pins and every output of Layers 5 to 9 and the procedures whose printed pins are not the tree's |
| `apply_layer_status_set29.py`, `apply_layer_status_set29b.py` | the "After set 29" tables of `LAYER-STATUS.md`; the two rows restated |
| `apply_l5pwr_lh04b.py`, `apply_set29_readers.py`, `apply_l7pwr_set29.py`, `apply_l7pwr_f12.py`, `apply_set29_fw_test.py` | the integration corrections named in the table above, each asserting its old text once and refusing a second run |
| `scan_printed_pins.py` | lists every committed output under `v2/docs` whose printed pins are not the tree's |
| `stage_held_sheets.py` | stages the makers' held-back sheets from sibling checkouts, each verified by a record's pin |
