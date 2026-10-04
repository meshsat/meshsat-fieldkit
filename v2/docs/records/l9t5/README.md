**ROUND 2 DONE (4 October 2026 evening, task T5 continued):** I-03's board A draft composes in L4-E9's order, reads DRAWN with three mutations failing and HOLDS on C-DEV rev 1 (U7 6.0359 A against 7.0957 A); board B's draft is UNCHECKED, its composition BLOCKED by T5b (GND's declared 21.0 A peak after l8r2's fans12), read alone and in a diagnostic composition with two mutations failing; one negative check (round 1's board B text, corrected); L9P-F01 restated on C-ALLTX rev 3 (record l9pwr round 5); the C-PROT gauge finding filed (L9T5-F04); A1's detector: no maker's sheet read prints a limit, so A1 stays a SELECTED DIRECTION with V-A1, P-A1 and D-A1 named, no board D draft. Not done: the full board B composition (waits on T5b), V3 (the coordinator's). Next: T5b lands, then `l9t5_drafts.py` again; V3 reads the completed correction. Round 1's checkpoint line is history: section 0 of `L9T5-CASES.md`.

# l9t5: task T5, C-ALLTX rev 2 and C-DEV rev 1 (Layer 9's power author, MESHSAT-1357)

4 October 2026, worktree `l9t5` on branch `fnd/l9t5` from set 29's line `dc99897f`. Prototype design, desk arithmetic: nothing
has been built, powered or measured. This folder takes the case row C-ALLTX rev 2 from record l9pwr's budget (round 4, out 7b),
bounds the uncertainties the row names, compares three service-neutral approaches to F01 / D-17, and selects a correction for I-03
(C-DEV rev 1) and L9P-F04. It edits no generator, registry, requirement or other record's file, and it drafts nothing yet.

| File | What it is |
|---|---|
| `L9T5-CASES.md` | The page: the budget defect corrected, the case row and its parts, the uncertainty table, the three approaches, C-DEV's two options, the selection, what stays open |
| `l9t5_case.py` | The script, from the repository root: `python3 v2/docs/records/l9t5/l9t5_case.py` (stdlib, PyYAML, pdftotext). It imports `v2/docs/records/l9pwr/l9pwr_budget.py` unchanged, pins every input by sha256, parses every maker's figure from its sheet and refuses when one is not found |
| `l9t5_case.out` | Its output, committed, regenerated only through `_bin/regen_out.py`, after `l9pwr_budget.out` (0 the pins; 1 the case row; 2 the uncertainties; 3 the labelled scenarios; 4 the approaches; 5 C-DEV and L9P-F04; 6 the selection; 7 the predicates) |
| `inputs/` | The coordinator's case rows (rev 2 and, round 2, rev 3) and the collaborator's challenge cx40, filed as received, and board B's round 1 draft text (the old defect), each with its sha256 in `inputs/SOURCES.txt` |
| `apply_gen_sch_a_iocbuck.py`, `apply_gen_sch_b_iocbuck.py` | I-03's drafts for boards A and B (NOT RELEASED: each refuses the tree's generator until a `RELEASE.md` names an accepted check) |
| `check_l9t5_netlist.py` | What the regenerated netlists must show (DRAWN, NOT DRAWN, FAIL), parsed with record l8p's reader |
| `l9t5_drafts.py`, `l9t5_drafts.out` | Round 2: each draft alone, the compositions in L4-E9's order, the regeneration (record l8p's `gen_netlist.py`), five mutations, the intent, the acceptance on C-DEV rev 1, the state and the findings |
| `fetch_held_back.py`, `l9t5_a1.py`, `l9t5_a1.out` | Round 2: A1's detector survey over four makers' sheets held back by their terms (fetched and sha256-checked, never committed) |

Test: `v2/ecad/tools/tests/test_l9t5.py` (`env -C v2/ecad/tools python3 tests/run.py test_l9t5`).

## The result in short

- **C-ALLTX rev 2 from its text needs 15.5162 V** at 18 A (241.039 W at VBAT against the 240.747 W allowance: **+0.292 W**). The
  row's quoted 16.214 V is D-11's basis, which keeps the non-transmit loads at HIGH: a revision of the row is the coordinator's.
- **The printed bounds dominate:** the gauge's uncalibrated error alone (0.7988 A) takes the need to 16.0512 V; combined with the
  dock contacts' printed maximum, 16.0684 V.
- **Selected for F01 / D-17: A1**, the VHF PA held to its 30 W service by a VGG loop on board D (the maker's own output control);
  with the loop at +-0.5 dB the case with the printed bounds needs 14.9585 V, at +-0.25 dB the 8 W modules and D-11's basis pass as
  well. CONDITIONAL on the PA's bench row and a detector with a printed accuracy; not drafted.
- **Selected for I-03: (b)**, the three supervisors' LDOs on their own TPS62933 buck: U7 at 6.0359 A against 7.0957 A. **L9P-F04
  closes with A1.**
- Reported for C-PROT: the gauge's uncalibrated error exceeds the 0.32 A between the service and the breaker's least limit.

## Round 2 in short

- **I-03:** board A's half checked (composition, netlist with three failing mutations, acceptance on C-DEV rev 1: HOLDS); board B's half
  UNCHECKED, blocked by T5b; I-03 OPEN until T5b lands and V3 reads it. T5b's input: the draft adds 0.00 A to board B's GND loads and a
  fifth source J_5V_IOC carrying 0.36 A typical, 1.4358 A at C-DEV.
- **L9P-F01:** restated on C-ALLTX rev 3 in record l9pwr round 5 (15.5162 V against 15.5 V; D-11's 16.214 V a labelled scenario).
- **L9T5-F04 for C-PROT:** the gauge's 0.7988 A uncalibrated error against the 0.32 A between 18 A and the breaker's 18.32 A.
- **A1:** no detector sheet prints its temperature deviation as a limit; A1 stays a selected direction (V-A1 drafted UNSENT, P-A1, D-A1).

## What other authors own (reported, nothing of theirs edited)

- The coordinator: the case row C-ALLTX rev 2's quoted figure (16.214 V) against its text (15.5162 V on the text).
- Board D's generator (A1's loop), board A's and board B's generators (I-03's buck, its lead and the LDOs' inputs), Layer 5 (the PA's
  output-control contract; the buck's enable with RAIL_EN).
- Record l9stk and C-PROT's consumers: the gauge's calibration against the breaker's 0.32 A gap.
- L4-E9: D-17's figures follow the case row once its revision is fixed; R-214 (U5) is its bench row.
