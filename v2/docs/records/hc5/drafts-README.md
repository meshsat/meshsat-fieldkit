# Layer 5 closer hc5 (MESHSAT-1357, 27 September 2026): drafts for the integrator

Branch `fnd/hc5` from `e3aedb25`. Nothing is committed or pushed. Prototype framing throughout: nothing built, ordered,
powered or measured. The KiCad box was not used: no generator or netlist changes here.

**Pass 2 (after review, 27 September 2026).** `main` moved to `84e52461` meanwhile (round 8 integrated for A, C, D, E, P
and the battery packet; B still a candidate). Every script below was re-run on a scratch copy of `84e52461` and applies
there; the reading patch is `hc5-shared-files.on-84e52461.patch` (the `e3aedb25` one is withdrawn). Review items closed:
(1) every one of the eighteen contracts now carries harness, levels, current, default state, sequencing, mating,
hot-plug, judged_by and a tbd list, each a value, "n/a: reason" or "TBD: ... effect", asserted by the new
`records/hc5/check_contract_fields.py` (18 of 18); IF-MON's touch USB has a board end by the session's choice SC-HF-06
(board D's spare hub port J_USB3), and section 12 says what the contracts carry and that the first twelve do not carry
those fields yet; (2) IF-EXT-ETH's judged_by says INT-001 judges SWP4_* and nothing judges MDI_A..D, with the MDI side an
open item (HF-F08); (3) FW-A02 cites session item S-20 under D-06 and FW-A05 the session's thresholds under D-11
(PROVISIONAL); the same reading applied to every row found three more (FW-A07 had narrowed D-12's port uses, FW-A13's K4,
FW-C04, FW-C10 and FW-E05's scope of the owner's words).

**Fixes after the second review (targeted fixer c5, 27 September 2026).** `main` is `a8652172` (H1) now; its registry
already holds S-47 (HC9-E1) and SC-13 to SC-16, and the layer 6 closer (`99cde56b`) had already rewritten S-41 and three
of the IOHA sentences this closer corrects. Only the review's two blocking items were fixed, and the drafts re-checked on
`a8652172`: (1) SC-HF-06's board end for the monitor's touch lead, board D's `J_USB3`, is carried the same way in
IF-MON, `ARCHITECTURE.md` section 12 (`J_USB3` left the "not given a contract" list), `ASSEMBLY.md` section 4's row and
build step 9, `PANEL.md` section 1's Pass-throughs row and `HW-FW-CONTRACT.md` SC-HF-06 (the two page edits are new
outside-ownership lines in `apply_docs.py`, with the readings bound to those pages rebound); (2) IF-BA-RF's D-07 note,
its tbd entry, a comment over its findings and section 12's IF-BA-RF row say that board A's site at X +46 is in no
generator and board E's cavity at X 46 is drawn since `45f6d83f`. `apply_registry.py` skips the S-41 edit when S-41
already carries 0x34 to 0x36; `apply_docs.py` skips an IOHA edit when the layer 6 closer's wording of the same fact is
there and puts the SC-HF-02 and FW-B08 sentences after its "CORRECTED at `458b2873`" heading. The review's minor items
are not in this fixer's list and are unchanged (`drafts/c5-response.md`).

## New files in the worktree (the closer's own; commit them first)

| file | what |
|---|---|
| `v2/docs/HW-FW-CONTRACT.md` | the hardware and firmware contract, version 1: FW-A01 to A16 re-read at `e3aedb25`, FW-B, C, D, E, P and K rows, round 8's changes, V-nn checks, the heartbeat resolved, the kit I2C budget, findings HF-F01 to F05, session choices SC-HF-01 to 05 |
| `v2/docs/records/hc5/kit_i2c_budget.py` and its two outputs | the kit I2C budget (stdlib, read-only; reads the four netlists and the committed layouts) |
| `v2/docs/records/w5/w5-hw-fw-contract.md`, `v2/docs/records/r4a/r4-hwfw-contract.md` | the two worktree drafts the tree cited, filed byte for byte as records |
| `v2/vendor/standards/nxp-um10204-rev6-i2c-bus-specification.pdf` | NXP UM10204 Rev. 6 via the Internet Archive (nxp.com serves a 3-page stub now), sha256 b7619700e8bb9dd4 |
| `v2/vendor/connectors/3m-3365-flat-cable-ts0080.pdf` | 3M TS-0080-B, the flat cable the ribbon capacitance is taken from, sha256 1dc900fe684bd6c2 |
| `v2/docs/records/hc5/usb-2-0-clauses-cited.md` | pass 2: the USB 2.0 clauses SC-HF-06 and HF-F06 cite (Chapter 7's opening, Table 7-1's RPU row, 7.2.1), word for word from the same `usb_20.pdf`; a new record rather than an edit of `v2/vendor/standards/usb-2-0-specification-2024-09-27.md`, which `rules_status.py` records by sha as an input of SI-001's `edge_length.py` |
| `v2/docs/records/hc5/check_contract_fields.py` and `check_contract_fields.out.txt` | pass 2: the field check of the eighteen contracts (stdlib plus PyYAML, read-only) and its output on `a8652172` (re-run by c5; the body is byte-identical to the pass 2 run on `84e52461`) after `apply_interfaces.py` |

## Edits to shared files (scripts; each idempotent, each anchor asserted once; run from the repository root in this order)

1. `python3 drafts/hc5/apply_registry.py`: `pcb_requirements.yaml`. CON-020 and S-41 to the 0x34 to 0x36 block (owned
   action); new open items (next free S numbers: SC-HF-02 to draw, HF-F02; pass 2: SC-HF-06 with HF-F06 on board D, HF-F07
   on board E; on `a8652172` they take S-48 to S-51, S-47 being HC9-E1 there, and on `84e52461` S-47 to S-50) and a new
   constraint (next free CON number, CON-023 on `a8652172` and on `84e52461`,
   the kit bus rise-time constraint, FAIL at desk, bound to the budget's script and output). Needs the records/hc5
   files in the tree first (it hashes them).
2. `python3 drafts/hc5/apply_interfaces.py`: `pcb_interfaces.yaml`. Eighteen new contracts appended after the last
   one (`pcb_interfaces-new-contracts.yaml`); the five "(proposed)" hot-plug rules as SC-HF-04; IF-PE-PACK's SMBus judged
   by section 15c; IF-EXT-USB's stale text retired; every judged_by by check_contracts section number instead of line;
   IF-BC-PANEL's bus text and findings carry HF-F01 and SC-HF-02. Owned (drafts for pcb_interfaces.yaml).
3. `python3 drafts/hc5/apply_docs.py`: ASSEMBLY.md section 4's Monitor touch USB row and build step 9's clause on the
   monitor's leads (outside; reason: SC-HF-06 names the touch lead's board end, and the row named "a B16 slot hub header"
   with no designator, which step 9 repeated), PANEL.md section 1's Pass-throughs row (outside; reason: it sent the touch
   lead to B16, against SC-HF-06), PANEL.md section 7 (owned), PANEL.md section 3's GPIO10 to 12 row (outside;
   reason: the heartbeat source is the layer 5 goal and the row states it wrongly), ARCH-PCB-B-IOHA.md sections 6 and
   10a (owned), ZEROIZE.md Z-C3 (owned) and the three places that repeat its address block (sections 2, 4 row E17, 9
   item 8; same fact) plus section 3.4's "the kit bus clock is not declared anywhere" (outside; reason: FW-K01 declares
   it and the budget re-run at 90 kHz holds). **It then rebinds the requirement readings bound to those three pages at the
   sha it edited** (REQ-005, CFL-001, CFL-005, CFL-014, CFL-015, CFL-016, ASM-005, FEA-001; CFL-015 also on ASSEMBLY.md), each with a note judged
   record by record (CFL-001 and CFL-016 now also say that section 1 changed only in its Pass-throughs row, which they do
   not cite); a reading bound to any other sha is left and printed. Board B round 8's identical wording for the
   supervisors' row, the S-07 finding and IOHA line 99 is detected and not applied twice, and so is the layer 6 closer's
   wording on `a8652172` of the supervisors' part in IOHA section 6 and of 10a's two H743 sentences.
4. `python3 drafts/hc5/apply_architecture.py`: ARCHITECTURE.md section 12 replaced whole (owned) from
   `ARCHITECTURE-section-12.md`; section 5.5 (outside; reason: its "still name 0x30 to 0x32" becomes false with step 3,
   and the bus speed and budget belong beside the address table) and one sentence at the head of section 10 (outside;
   reason: the summary points at the itemised contract). Board E round 8's docs patch is on `main` since `45f6d83f`;
   the replacement carries its two section 12 rows' facts (the clamp bar at `45f6d83f`, R8E-N01, 14.10 A), and section
   12 is byte-identical from `84e52461` to `a8652172`, so nothing is left to drop.
5. `python3 drafts/hc5/apply_index.py`: `v2/vendor/sources.txt` (two lines) and `v2/docs/records/README.md` (two folder
   rows, five file rows). Outside; reason: a filed document without its index line cannot be traced.
6. Re-render: `(cd v2/ecad/tools && python3 rules_lib.py requirements && python3 rules_render.py --requirements)`, then
   the usual status and page renders of the integration recipe.

`hc5-shared-files.on-a8652172.patch` is the result of steps 1 to 5 on `a8652172`, for reading (`git apply --check`
passes on a pristine export of `a8652172`); the scripts are authoritative, and the `84e52461` patch is withdrawn. Checked
on a scratch clone of `a8652172` (c5): each script applies, a second run edits nothing, `rules_lib.py requirements` reads
133 records with 0 errors before and after `rules_render.py --requirements`, `rules_render.py --requirements --check`
reads current after the render, `check_contract_fields.py --all` exits 0 with the filed body, and `tests/run.py
test_interfaces test_requirements test_review_packet test_artefact_recording` reads 103 passed, 0 failed, 1 skipped (the
skip is `out/rule-audit`, gitignored and absent from a clone; with it present the same set read 104 passed) and
`test_certify_identity test_order_codes test_safe_lines test_spacing test_handover_pack test_decision_register
test_stale_readings` 90 passed, 0 failed, 3 skipped (the same gitignored evidence). The five scripts also still apply,
twice, on `84e52461` and on `e3aedb25`, with 0 registry errors on each.

## What was run (scratch copies only; nothing written in the main tree or this worktree's shared files)

- The five scripts on a copy of this worktree, each run twice (the second run edits nothing); `rules_lib.py
  requirements`: 0 errors; `rules_render.py --requirements`: rendered; `tests/run.py test_interfaces test_requirements
  test_review_packet`: 84 passed, 0 failed, 2 skipped. `rules_render.py --check` reports PCB-ETA.md out of date on a
  pristine `e3aedb25` copy as well (no `out/` evidence in a scratch copy), so it is not caused by these drafts.
- `kit_i2c_budget.py` on `e3aedb25` and with board D's netlist from `fnd/r8int1`.
- `records/rv-zer/zeroize/zer_budget.py` with `F_I2C = 90_000` (`zer/zer_budget.py`, outputs `zer/run-90kHz.txt` and
  `zer/run-100kHz.txt`): every pass line holds, 10 of 10 planted defects caught.
- c5 (after the second review): the five scripts on a scratch clone of `a8652172`, twice (the second run edits
  nothing), then `rules_lib.py requirements`, `rules_render.py --requirements` and `--requirements --check`,
  `check_contract_fields.py --all` and the two test sets named above; the same five scripts on scratch checkouts of
  `84e52461` and `e3aedb25`, twice each, with `rules_lib.py requirements` at 0 errors on each. `main` moved to `84d0a527` (H1.1) during the pass;
  of the files the scripts edit only `v2/docs/records/README.md` changed (one `handover/` folder row), and
  `apply_index.py` applies to that file, twice, on an export of `84d0a527`.
- Not run: the full suite (the integrator's), any gate on a board, anything on the KiCad box.

## Hand-offs

- Board A's author: SC-HF-02's U_A (HW-FW-CONTRACT.md 6.7); HF-F02 (INA226 U17 on the 54 V rail, over its 40 V absolute
  maximum).
- Board D's author: HF-F06 (a current limit on J_USB3's VBUS, and its 0.05 A budget line set from the touch's measured
  draw, V-B19), the cost of SC-HF-06.
- Board E's author: HF-F07 (the Geiger pulse level into GPIO7; discrete gate pull-downs on Q9 and Q10).
- Board B's next phase: HF-F08 (the MDI side, MDI_A..D, is judged by no rule).
- The integrator: the first twelve contracts carry none of the pass 2 field list (check_contract_fields.out.txt lists
  what each has no key for); bringing them to it belongs with the re-anchor of `pcb_interfaces.yaml`. In that re-anchor,
  IF-AE-RF still says what `45f6d83f` changed on board E: its board E end cites the float clamps at
  `gen_pcb_e.py:16-30`, `nests` says the one clamp bar is owed (R4E-07), `five_g_ports` says board A's site at X +46
  and board E's clamp are "neither in a generator yet" and `judged_by` says nothing judges the twelfth site; since
  `45f6d83f` the bar with its cavity at X 46 is drawn and `check_pcb_e.py` judges it, and only board A's site is in no
  generator (as IF-BA-RF and section 12 now say). `ARCHITECTURE.md` section 13's W4-F10 row ("wiring on A and E
  owed") reads the same stale way. Neither is in this closer's list (hc5 review 2, minor items).
- The integrator, at the merge: the H1 handover pages describe the monitor's touch USB as having no board end
  (`v2/docs/handover/LAYER-STATUS.md` lines 694, 719, 735, 742, 754, 783 and 809 and `CONTINUATION-BRIEF.md` line 203 at
  H1.1, `84d0a527`; lines 680 to 795 and 186 at `a8652172`); after
  this closer merges they cite SC-HF-06 (board D's `J_USB3`) and HF-F06, at the next handover snapshot. The frozen
  `v2/release/handover/H1/` copy is not edited.
- Board B's author: SC-HF-02's U_S with the EN delay (6.7). The monitor's touch USB needs no board B change under
  SC-HF-06; reversing SC-HF-06 means a port reallocation or added downstream capacity on B.
- Board E's author: HF-F04 and HF-F05 (fan and camera housings; the fans' rating at 16.8 V).
- Parts stream: TCA9517A and 74LVC1G17 codes and certification rows for the new parts; the D38999 receptacle, sealed
  RJ45, M8 and camera parts named TBD in the contracts.
- Layout: the per-segment copper allowances of HW-FW-CONTRACT.md 6.6, read with the field solver.
- TEST-PLAN.md's owner: the V-nn rows of HW-FW-CONTRACT.md section 5.
- ASSEMBLY.md's writer: HF-F04; the RF jumper and connector plate rows the audit names (not in this closer's actions).
