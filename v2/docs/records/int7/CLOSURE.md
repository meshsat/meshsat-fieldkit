# The set 6 integration on `fnd/int7`: what changed, by kind (MESHSAT-1357, 28 September 2026)

Prototype design: no V2 board has been fabricated, ordered, assembled or measured. Every review named here is an AI
review or an AI check, labelled as such; none is a qualified engineering review. This record separates, as the
reassessment of handover H3 asks (direction 2), the circuit changes, the declaration changes, the checker corrections
and the evidence refreshes that this integration carries onto `main`, so that no reader takes a refreshed reading for a
closed defect or a checker repair for a circuit change. Its second edition answers the fresh check of the merge
(`CHECK.md`, finding B-3: the first edition listed a contract change among the circuit changes, said "none" under
declarations while set 6 carried several, and left out two of set 6's instrument corrections). The attribution of every
moved reading is the re-take's own, `v2/docs/records/retake6/RESULT.txt` section 5, quoted by row below.

## 1. Circuit changes (set 6, the wave 4 circuit round; generators regenerated on the KiCad host with parity)

| Commit | Board | Change | What the re-take read of it |
|---|---|---|---|
| `910da406` | B | EMCON forces the RockBLOCK 9704's ENABLE low in hardware (U536, R527, SC-64), holds the radio switches off in their gates' supply band and drives each card rail's enable; the two WiFi link cards | RF-002 on B: three of its eleven failed rows moved by circuit changes (the TX_INHIBIT_n line below and the two WiFi link cards). The other eight moved by an instrument correction, section 3 |
| `e28f91a6` | C | TX_INHIBIT_n fails safe with the panel unpowered: R14 10 k to 2.2 k and a new R50, 10 k, to ground (SC-67, which closes S-64, finding W3T-F1); R51, the bottom leg of the RAIL_SENSE divider (W4C-F1), to which the re-take attributes no moved reading | RF-002 on C FAIL to PASS (inhibit_chain_c PASS of 6); RF-002 on A and D FAIL to INCONCLUSIVE: the same line's check no longer fails, what stays is undecided (S-92, S-93) |
| `c4ad8350` | A, E | the hot stop line HOT-R1 drawn on boards A and E (SC-70, which closes S-57) | SCH-004: safe_lines_a PASS of 7, safe_lines_e PASS of 2. REQ-077 (a desk-review record with no rule) moved FAIL to INCONCLUSIVE in set 6 and reaches `main` with this promotion |

**Electrical state after them:** 0 boards ready for layout, 35 layout-entry reasons (A 7, B 7, C 3, D 7, E 4, P 5, E5
2), against 40 on `main` before this integration. Still FAIL on current-candidate evidence: INT-001 and SCH-003 on E5
(10 of 38 dock targets, S-74) and BAT-001 on P (3 of 63 checks, REQ-044 and S-85). SI-001 INCONCLUSIVE on every board
with a schematic (edge rates undeclared). REQ-030, REQ-032 and REQ-071 stand FAIL as before set 6 and are owed a re-read
(S-94). No electrical defect is closed by a document of this integration; the closures above are set 6's session
choices and are read, not claimed.

## 2. Declaration changes (set 6; this integration's own commits change none)

| Commit | Board | Declaration | What the re-take read of it |
|---|---|---|---|
| `e28f91a6` | C | the supplies declared, +3V3 covering EPD_VCC | PWR-001 on C FAIL to PASS (intent_rails PASS of 6) |
| `932cf9d7` | P | the supplies declared, the fuse gate bounded by TI's 6 V drive; BAT-001's table brought to the drawn circuit (SC-74, which closes S-45) | PWR-001 on P FAIL to PASS (of 11). BAT-001 on P stays FAIL on other grounds: 1 of 45 checks before, 3 of 63 now, three hardware-level limits (S-85) |
| `932cf9d7` | D | the flyback diode's order code and its maker's sheet filed (SC-72, which closes S-76 with board E's) | PWR-001 on D INCONCLUSIVE to PASS (of 7): RLY_K settled by the filed sheet |
| `c4ad8350` | E | the fan flyback sheet filed | PWR-001 on E INCONCLUSIVE to PASS (of 16): FAN1_SW and FAN2_SW settled by the filed sheet |

A declaration that lets a rule decide is not a circuit change: each PASS above says the declared figure is inside the
part's stated limits, and rests on the declaration being the circuit's. Owed, and not in this integration: board A's
external-port declaration (S-88, H3-02), corrected by stream d8dec31's `apply_port_declarations.py`, checked on 28
September (`checks/d8dec31-check-1.md`: mergeable; one regression owed before S-88 closes) and applied after this promotion with TRN-001 re-taken.

## 3. Checker, contract and instrument corrections

| Where | What | Effect on readings |
|---|---|---|
| `tx_inhibit.py` (`910da406`, set 6) | the walk learned the SN74LVC2G06 family board B has carried since its round 8 | **eight of board B's eleven failed RF-002 rows moved by this correction: an instrument defect closed, not a design finding.** RF-002 on B reads INCONCLUSIVE (16 pass, 0 failed, 4 undecided of 20) |
| `block_contract.py` (`d5e12880`, set 6) | E5's block contract is judged against board A's CURRENT netlist, and INT-001 reads that contract | **E5's INT-001 and SCH-003 now read FAIL** (check_contracts_e5, 10 failed of 38): board A carries SC-55 and E5's board file has not followed. A defect exposed, not introduced: it is open item S-74's expected reading |
| `reliability.py` (`760d7f41`, set 6) | judges a part's identity, not the description of what it does: three logic gates of board B whose description named a socket no longer wear | REL-001 re-taken; its population is still the tool's twelve words (S-89, LIMITED) until stream d6rel's repair is integrated |
| `rules_status.py`, `rules_render.py`, `retake_schematic_phase.py` (`d5e12880`, set 6) | the audit's own writers and the re-take's driver | re-taken by the three `rules_status` runs; the driver writes no reading |
| `check_pcb_b.py` (`910da406`, set 6) | MEC-001 on B asserts pads of parts set 6 added | NOT re-taken: it judges the placed board, and the phase's board file predates those parts (AWAITING_REVALIDATION, LAYOUT_NOT_CURRENT, as on `main`) |
| `rules_render.py` (`b3d66c70`, this integration) | the evidence page's head sentence is read from the registry (`baseline_state`, the feasibility records), the limit notices are generated from open items carrying `limits_reading`, and a limited reading is marked on its board page | pages only; no reading changes |
| `rules_lib.py` (`a4b157f0`, this integration) | the requirements validator refuses an open item that no record waits on and that carries no disposition | 26 of the 90 tracked readings name `rules_lib.py` in their code bundle and read TOOL_CHANGED until re-taken; the re-take of 28 September re-wrote all 90 (section 4) |
| `port_protect.py` (stream d8dec31, not in this integration) | refuses an entry naming no conductor, reports uncovered pins | after promotion |

## 4. Evidence refreshes

| Refresh | Where | What it read |
|---|---|---|
| the consolidated re-take on the set 6 netlists (worker retake6, 27 September, KiCad host, `50e3b60b` to `7f3a4956`) | 83 readings on seven boards | 71 PASS, 10 INCONCLUSIVE, 2 FAIL. Of the 90 tracked readings 58 carried the same result, counts and evidence, 23 the same result with other counts or evidence, 9 another result (the rows of sections 1 to 3) |
| the re-take of 28 September on this line's tools (KiCad host, `/root/int7`, commit `a4b157f0`, 14:52:52 to 14:55:01 UTC, driver 110.7 s, exit 0; run records under `box/`) | every schematic-phase reading, `reliability.py` per board, `claims_check.py` | the same 90 tracked readings re-written with the current code bundles and 252 gitignored files (240 verdict files, 6 ERC reports and their 6 provenance files); no verdict, count or evidence line changed against `7f3a4956` (the fresh check's item 6) |
| `rules_status` three times and `rules_render` on the merged tree | the pages | FAIL 40, INCONCLUSIVE 89, PASS 209 of 338 rule-board readings (the historical aggregate of mixed revisions, not readiness); 35 layout-entry reasons |

## 5. Registry changes (the writer's, this integration)

- `069a5d97`: the H3 line merged into the set 6 line; the registry's two conflicts resolved item by item (an item is open only where both sides hold it open): 59 open, 58 closed, 144 records. Closed on the set 6 side and carried: S-45 (SC-74), S-57 (SC-70), S-64 (SC-67), S-76 (SC-72); closed on `main`'s side: S-79.
- `f1dda804`: S-88 to S-91 opened (board A's port declaration, REL-001's population, the audit's absolute paths, H3's minor findings).
- `a4b157f0`: **CON-010 re-decided from the readings by a stated predicate** (`apply_con010_redecide.py`): FAIL to INCONCLUSIVE, because the check that set FAIL (W3T-F1) fails on no board since SC-67 while three rows stay undecided; S-92 opened; S-88 and S-89 carry `limits_reading`; every open item linked from a record or disposed (`apply_waits_on_dispositions.py`).
- `1c4235ec`: CON-010 and REQ-044 rebound to the final page (`apply_rebind_final_page.py`), results unchanged.
- the answers to the fresh check (`apply_check1_answers.py`, `CHECK-RESPONSE.md`): S-93 opened for the LM5176's gate drive in shutdown and CON-010 waits on S-92 and S-93; S-65 and S-86 linked instead of disposed; S-13 disposed instead of linked; S-81 closed on its own second condition; S-94 opened for the re-read of REQ-030, REQ-032 and REQ-071.
- the answers to the re-check (`apply_check2_answers.py`, `walk_grounds.py`, `walk-grounds.txt`): S-92 and S-93 rewritten to EVERY ground RF-002's walk names for the SA868's row (three) and for board A's two rows (one and three), read from the walk's own report, with the script asserting that each part those grounds name is in an item CON-010 waits on; REQ-032 waits on S-65; CFL-006 and FEA-005 wait on S-86.
- **After them:** 65 open items, 59 closed, 144 records. 54 open items have a record waiting on them (99 links on 60 distinct records, those that stood before this integration included; the figures are read from the parsed registry) and 11 carry a disposition with its reason; none has neither, none has both.

## 6. The fresh check of the merge

`CHECK.md` (an AI review, 28 September 17:15 to 17:34 CEST) read the first candidate `1c4235ec` NOT mergeable on three
findings, all in text this integration wrote; it found no reading, count or merge result wrong and recomputed CON-010's
predicate as INCONCLUSIVE. `CHECK-2.md` (an AI review by another checker, 18:00 to 18:16 CEST) read the corrected candidate
`85ad1193` NOT mergeable on one finding, R-1: B-2 and B-3 answered, B-1 answered for the QMX's row only, because S-92 and
S-93 each named one ground where the walk names up to three. That was the second failure on the same point, so the
method changed: the items are now written from the walk's own report and a script asserts their coverage (section 5).
`CHECK-3.md` (an AI review by a third checker, 18:26 to 18:42 CEST) read the third candidate `f2b8f98d` **mergeable**, with no
blocking finding and thirteen minor items: R-1 answered by the walk's own measure, nothing moved that should not have.
`CHECK-RESPONSE.md` answers each finding and each minor item of the three checks. The full suite on the KiCad host read
2019 passed, 0 failed, 3 skipped at each candidate (`box/suite-1c4235ec.txt`, `box/suite-85ad1193.txt`,
`box/suite-f2b8f98d.txt`). `main` was fast-forwarded to `f2b8f98d` on 28 September 2026 and pushed; this edition of the
record and the third check were filed in the commit after it.

## 7. What this integration does not do

It closes no layer and readies no board for layout. Layers 1 to 3 stay COMPLETE as H3 released them; H3 is untouched.
The reviews' P1 items stay open and are named: H3-01 (REL-001, stream d6rel, `checks/d6rel-check-1.md`, its follow-up
done on its branch), H3-02 (TRN-001 on A, stream d8dec31, `checks/d8dec31-check-1.md`, one regression owed), board E's
constraint sheet against its netlist (stream d5dock, not started).
