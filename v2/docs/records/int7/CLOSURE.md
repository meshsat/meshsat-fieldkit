# The set 6 integration on `fnd/int7`: what changed, by kind (MESHSAT-1357, 28 September 2026)

Prototype design: no V2 board has been fabricated, ordered, assembled or measured. Every review named here is an AI
review or an AI check, labelled as such; none is a qualified engineering review. This record separates, as the
reassessment of handover H3 asks (direction 2), the circuit changes, the declaration changes, the checker corrections
and the evidence refreshes that this integration carries onto `main`, so that no reader takes a refreshed reading for a
closed defect or a checker repair for a circuit change.

## 1. Circuit changes (set 6, the wave 4 circuit round; on `fnd/r8int6` since 27 September)

Each is a generator change regenerated on the KiCad host with parity and read by the consolidated re-take:

| Commit | Board | Change |
|---|---|---|
| `d5e12880` | E5 | INT-001 reads E5's own dock contract, judged against board A's current netlist (a contract, not a copper change) |
| `910da406` | B | EMCON forces the RockBLOCK's ENABLE low, holds the radio switches off in their gates' supply band, drives each card rail's enable (SC-64) |
| `e28f91a6` | C | TX_INHIBIT_n fails safe with the panel unpowered: R14 10 k to 2.2 k, R50 10 k new (SC-67, closes S-64 / W3T-F1); PWR-001 declarations with +3V3 covering EPD_VCC |
| `c4ad8350` | A, E | the hot stop line HOT-R1 drawn on boards A and E; board E's fan flyback sheet filed |
| `932cf9d7` | D, P | board D's flyback diode ordered with its sheet; board P's supplies declared with the fuse gate bounded by TI's 6 V drive; BAT-001's table |

**Electrical state after them (the re-take of 27 September, re-run on 28 September on this line's tools):** 0 boards ready
for layout, 35 layout-entry reasons (A 7, B 7, C 3, D 7, E 4, P 5, E5 2), against 40 on `main` before this
integration. Still FAIL on current-candidate evidence: INT-001 on E5 (10 of 38 dock targets, S-74) and BAT-001 on P
(3 of 63 checks, REQ-044 and S-85). SI-001 INCONCLUSIVE on every board with a schematic (edge rates undeclared). No
electrical defect is closed by a document of this integration; the closures above are set 6's and are read, not claimed.

## 2. Declaration changes

None in this integration. Board A's external-port declaration (S-88, H3-02) is corrected by stream d8dec31's
`apply_port_declarations.py`, checked on 28 September (mergeable; one regression owed before S-88 closes) and applied after
this promotion, with TRN-001 re-taken on the KiCad host.

## 3. Checker and instrument corrections

| Where | What | Effect on readings |
|---|---|---|
| `reliability.py` (`760d7f41`, set 6) | judges a part's identity, not the description of what it does: three logic gates of board B whose description named a socket no longer wear | REL-001 re-taken; its population is still the tool's twelve words (S-89, LIMITED) |
| `rules_render.py` (`b3d66c70`) | the evidence page's head sentence is read from the registry (`baseline_state`, the feasibility records), the "Instrument limits" notices are generated from open items carrying `limits_reading`, and a limited reading is marked on its board page | pages only; no reading changes |
| `rules_lib.py` (`a4b157f0`) | the requirements validator refuses an open item that no record waits on and that carries no disposition | every gate that imports `rules_lib.py` read TOOL_CHANGED until the re-take of 28 September (section 4) |
| `port_protect.py` (stream d8dec31, not yet applied) | refuses an entry naming no conductor, reports uncovered pins | after promotion |

## 4. Evidence refreshes

| Refresh | Where | What it read |
|---|---|---|
| the consolidated re-take on the set 6 netlists (worker retake6, 27 September, box, `50e3b60b` to `7f3a4956`) | 83 readings on seven boards | 71 PASS, 10 INCONCLUSIVE, 2 FAIL |
| the re-take of 28 September on this line's tools (box, `/root/int7`, commit `a4b157f0`, 110.7 s, exit 0) | every schematic-phase reading, `reliability.py` per board, `claims_check.py` | the same results with the current code bundles: 90 tracked readings and 252 gitignored readings re-written, the page's layout-entry table unchanged row for row |
| `rules_status` x3 and `rules_render` on the merged tree | the pages | FAIL 40, INCONCLUSIVE 89, PASS 209 of 338 rule-board readings (the historical aggregate); 35 layout-entry reasons |

## 5. Registry changes (the writer's, this integration)

- `069a5d97`: the H3 line merged into the set 6 line; the registry's two conflicts resolved item by item (open only where both sides hold it open): 59 open, 58 closed, 144 records.
- `f1dda804`: S-88 to S-91 opened (board A's port declaration, REL-001's population, the audit's absolute paths, H3's minor findings).
- `a4b157f0`: **CON-010 re-decided from the readings by a stated predicate** (`apply_con010_redecide.py`): FAIL to INCONCLUSIVE, because the check that set FAIL (W3T-F1) fails on no board since SC-67 and the SA868 exciter's row stays undecided; S-92 opened for that threshold and CON-010 waits on it; S-88 and S-89 carry `limits_reading`; every open item has a record waiting on it or a disposition (`apply_waits_on_dispositions.py`: 17 items linked from 28 records, 13 disposed).
- the rebind of CON-010 and REQ-044 to the final page (`apply_rebind_final_page.py`), results unchanged.

## 6. What this integration does not do

It closes no layer and readies no board for layout. Layers 1 to 3 stay COMPLETE as H3 released them; H3 is untouched.
The reviews' P1 items stay open and are named: H3-01 (REL-001, stream d6rel), H3-02 (TRN-001 on A, stream d8dec31, one
regression owed), board E's constraint sheet against its netlist (stream d5dock).
