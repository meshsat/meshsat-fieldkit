# MeshSat field kit V2: current-state addendum to the supplier package d834e6a7

Dated 4 October 2026 (Europe/Amsterdam); revision 2 of 12:50 the same day, which withdraws the 16.1 V floor revision 1 carried,
separates committed files from gitignored evidence and brings the protection row to its current selection; revision 3 of 13:02
states the device rail I-03 at its current figure in every row (the owner's reviewer's L4-RD04). This addendum accompanies, and does not change, the package
`MESHSAT-SUPPLIER-HANDOVER-RELEASE-CANDIDATE-d834e6a7.zip` (12,894,538 bytes, sha256
29ed399ae8f7cb29801b9f6080725cc44cf06957430b8642440faf032e76cb7d), cut from commit
`d834e6a7be211d1cdd1b18ded54bec1c427048fd` of https://github.com/meshsat/meshsat-fieldkit. Where it and the package's entry page
(`SUPPLIER-HANDOVER.md`) disagree, this addendum is the current statement; the rows it supersedes are listed in section 2. It
answers the owner's reviewer's finding L4-RD01 of the same day (the entry page described superseded work as current and pointed
to branch material the package does not contain).

Power-design closure and fabrication release remain BLOCKED. Nothing has been built, bought or measured. The corrections named
below as later candidates are AI-produced drafts with AI checks; they are not technically accepted by the owner's reviewer and
are not implemented.

## 1. Four states, kept apart

| State | What it is | Where a supplier can read it now |
|---|---|---|
| A. The tested baseline | Commit `d834e6a7`: the project's release suite ran at this exact commit (project-reported: 2845 passed, 0 failed, 14 skipped on three passes; the raw logs are not in the package and can be supplied on request) | the package, and the public repository at that commit |
| B1. Committed in the tested commit, left out of the compact package | `v2/docs/records/l8r2/` (18 files: Layer 8 round 2's drafts, board B's fan feed and the VBUS20 cut-off) and `v2/docs/records/ARCHIVED-REVIEWS.yaml`, among others the package's `SOURCES-HELD-BACK.md` lists as in the repository. Layer 5's records (`records/l5pwr/`, `records/l5r2/`) and Layer 8's `records/l8gnd/` ARE in the package | a public clone of https://github.com/meshsat/meshsat-fieldkit at `d834e6a7` supplies them |
| B2. Gitignored evidence, not in any public copy | the readings and rule audits the checks and the suite read (the project's evidence archive: 984 files at `d834e6a7`) and the makers' documents whose terms forbid redistribution | NOT supplied by a clone. The makers' documents are fetched from the makers' sites by each record's own fetch script, which checks each sha256 (`SOURCES-HELD-BACK.md` lists them); the evidence archive is available from the project on request |
| C. Later candidates, not in the tested commit | Corrections made after `d834e6a7` (section 3), on the project's integration branches, which are not published | not readable now; they are delivered in the next supplier delta, with their drafts, calculations and check reports |
| D. Still to be delivered | Work not yet produced (section 4) | the next supplier delta or later |

## 2. Entry-page rows this addendum supersedes

| Entry page, as written | Current statement |
|---|---|
| Section 3, interfaces row: "Layer 5's power pass and its second pass are on branches (section 4, the delta)" | Both are integrated in the tested commit and included in the package: `records/l5pwr/` (the power contracts, with the restatements that leave no withdrawn Layer 4 claim in `pcb_interfaces.yaml` or `HW-FW-CONTRACT.md`) and `records/l5r2/` (the pass-2 fields of every contract, and round 3's panel decisions F-04 to F-13). |
| Section 4, Layer 5 row: "the eight older contracts' full fields (running)" | Done in `records/l5r2/` (in the package). Still open at Layer 5: board B's partition (5.1), the remaining sequencing and line states, the kit I2C bus's three segments, the rows the later candidates owe (section 4). |
| P8, board B's fans: "DRAFTED as a per-slot step-up (TPS61089 with a TPS259631 per slot; record l8r2, in the package's `branches/`, integrating in the next set)" | The package carries no `branches/` folder (`SOURCE.txt`: branches none). The round 2 draft is in the tested commit at `v2/docs/records/l8r2/apply_gen_sch_b_fans12.py` (state B). It is superseded by a later candidate (state C): a 70 percent firmware cap on the cooler fans' PWM was proposed and is WITHDRAWN (it held in no operating state, and the AP64500 slot converter was over its 5 A rating with the coolers on its rail); the selected direction moves compute slots 1 and 3 from the AP64500 to the LM5176 stage slot 2 already uses, keeps the per-slot 12 V step-up with the coolers at FULL speed, sets every LM5176 5.1 V divider to 0.1 percent (output 5.0019 to 5.1744 V, inside the CM5's 4.75 to 5.25 V) and declares 6.6 A on each slot lead. Status: a drafted, unimplemented, CONDITIONAL correction; the collaborator's (AI) focused check read NOT CONFIRMED and its targeted recheck NOT CLOSED, each item was corrected, and the coordinator's own closing check reads CLOSED AS CONDITIONAL on six proposed bench tests C4-1 to C4-6 (section 5). |
| P10, VBUS20: "record l8r2 in the package's `branches/`" | The draft is in the tested commit at `v2/docs/records/l8r2/` (state B); otherwise unchanged. |
| Section 7, item 3: "Work carried in the package's `branches/` folders is NOT on that commit ..." | This package carries no branch material. Later candidates (state C) are not in the package or in the public repository. |
| Section 9, last bullet: "the package's README names those branches and their tips" | The package's README names the later findings (state C), not branches; the branches are not published. |
| Section 10, the L9P-F02 row ("the per-slot step-up stays with each cooler fan's PWM capped at 70 % by a firmware rule") | Superseded as in row P8 above: the cap is withdrawn; the LM5176 direction is the current candidate, CONDITIONAL. |
| Section 10, the L9P-F01 row (its 16.1 V floor) | WITHDRAWN: that floor is not a current instruction anywhere, including FW-A05. REQ-018 stands: all-transmit through a 60 s key-down begun at a pack rest voltage of 15.5 V or more. On the final drafts that basis needs 16.214 V (Layer 9's power budget), so L9P-F01 is an OPEN design defect. The one design-out attempt, FAN_OK (every fan supply off while the PA keys), is CONDITIONAL on a thermal test (R-213) and UNIMPLEMENTED; its calculated need of at most 15.374 V is a design result, not a new requirement, and it changes no threshold. |

## 3. Later candidates (state C), with their state

| Item | Candidate | Check state | Open |
|---|---|---|---|
| L9P-F02, compute slots 1 and 3 | as in section 2, row P8 | AI collaborator NOT CONFIRMED, then NOT CLOSED; corrected; the coordinator's closing check CLOSED AS CONDITIONAL | C4-1 to C4-6; I-03 OPEN (the device rail at 7.472 A against its 7.0957 A loop minimum at the least load voltage, Layer 9's re-run on the final drafts; the earlier 7.181 A was the same case at the nominal 5.1 V) |
| The pack path's copper, boards A and E | the stacked outer faces and the adjacent return rated as one conductor: about 39 mm a face at 1 oz or about 19.6 mm at 2 oz; at 1 oz board E's 68 mm strip cannot carry a pack band and its return side by side | independent AI check: corrections confirmed | the outer copper weight is an OWNER DECISION (money): 2 oz on A and E, 1 oz with a layout change, or the returns laid apart (no copper cost, not credited until a coupon test). The fabricator's feasible stackups and price difference are needed before any option is treated as chosen |
| W4DP-F2, the pack path's protection with board P's FETs failed short | a LATCH-OFF LM5069-1 breaker on board P (two CSD18510Q5B, 2.6087 mOhm sense, trip band 18.32 to 23.93 A, cleared within 1.29 ms above it; the automatic-retry LM5069-2 was REJECTED because its repeated restarts overheat its own FET), a restart inhibit on the breaker pad (an NTC and a zero-drift comparator; restarts only below about 80 C case), a make-last enable loop at the dock with an RC hold so that every docking is a soft start, a third battery FET on board A (Q42) with R17 placed apart, a PTC trip on the battery FETs' copper, and on board A a hold of the loads during the breaker's start and a hardware charge inhibit while the pack terminal is dead | independent AI check: CONFIRMED AS CONDITIONAL for the breaker, the latch-off selection and the restart inhibit; board A's parts drafted, not yet checked | OPEN: DD-3 (the shore input's choke L2 over its rating; one design-out attempt failed), DD-5 (board P's Q1 body diode over its limit at 10 A and 18 A in hot air), B-R2's remainder (a breaker latched into a resistive fault with a source present is invisible to board A's charge inhibit; a correction on board P in progress), E11-37 (the gate drive of three FETs) |
| L9P-F01, the all-transmit basis | FAN_OK: every fan supply off while the PA keys (hardware lines on boards A, B and E) | not checked; CONDITIONAL on R-213; UNIMPLEMENTED (its drafts are not written) | OPEN; REQ-018's 15.5 V unchanged |
| Layer 9's power budget | the board-level budget with margins and sensitivities, re-run on the final drafts (the all-transmit basis needs 16.214 V; the device rail 7.472 A against 7.0957 A at the least load voltage) | not independently checked | the device rail (I-03) OPEN |
| Layer 9's stackups | one decision per board with its measurement; costs NOT READ at real outlines | the copper part as above | EQ-14 for the fabricator |
| Layer 5's slot-fault rule and the panel firmware's round 4 | one power-cycle rule for a lost compute module; a power-on reset read as HAD_POR set and the watchdog's REASON zero | coordinator only | the pico-sdk target build owed |

The two checks the owner's reviewer retained are answered on branches: the retry heating was shown for every protected part, and it is why the automatic-retry -2 is rejected and the latch-off -1 selected; E11-37 is rebound to the three-FET network (L4-E11's round 9) and stays OPEN on TI's answer (Q-TI-17) or a bench run with all three FETs.

## 4. Still to be delivered (state D)

Board P's correction for B-R2's remainder (in progress); FAN_OK's drafts and its thermal test R-213, only if the design-out is adopted; DD-3's choke (rated at least 8.42 A at a 40 K rise); the device rail I-03; Layer 5's contract rows the candidates owe (FW-A05 keeps REQ-018's 15.5 V and gains the FAN_OK key-down rule only if FAN_OK is adopted; the cooler fan PWM; the current monitors' recalibration; the slot leads' 6.6 A; the 7-way J_SMB and the dock enable contacts); Layer 7's dock contact and its mating order; Layer 6's part codes (the LM5069-1, the OPA187, the NTC, the 0.1 percent dividers, the 7-way connector). The next supplier delta carries these with the state C material.

## 5. Qualification proposals: how the later tests relate to the 14 experiments

The entry page's 14 experiments (`records/l4e9/L4-POWER-ARCHITECTURE.md` section 5d, in the tested commit) remain the baseline route. The later candidates propose further tests: C4-1 to C4-6 for the slot stages, and E-1 to E-13 for the protection candidate. They do not simply add to the 14, because some overlap:

| Later proposal | Relation to the 14 |
|---|---|
| E-1, the battery FETs' installed thermal path as a junction limit (at most 150 C at 23.93 A held from 76.25 C, with the band and R17 carrying the current) | supersedes E11-29's acceptance if the protection candidate is adopted (same specimen region, stricter limit) |
| E-3, the breaker's hot-short and docking tests | replaces E11-30's purpose for docking if the make-last enable is adopted (the 242.9 A docking waveform no longer arises); E11-30 stays as written for the pair's own pulse rating until then |
| E11-37 rebound to three battery FETs | modifies an existing experiment, as section 3 says |
| C4-3, the cooler fan's start in a fully loaded slot | additional (E11-35 covers the mixer fans, a different part and rail) |
| C4-1, C4-2, C4-4 to C4-6; E-2, E-4 to E-13 | additional |

All are PROPOSED, for the supplier to review and agree before execution; none is agreed or run.

## 6. Binding

This addendum is a separate file. Its sha256 is given in its companion file `CURRENT-STATE-ADDENDUM-d834e6a7.md.sha256`. It changes nothing in the package or in the tested commit.
