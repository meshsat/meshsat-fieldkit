# Integration set 25 (MESHSAT-1357, branch `fnd/int25`, 2 October 2026): Layer 4's connected power architecture and its closure gate

Prototype design: nothing is bought, built or measured, and every circuit change below is a release-guarded draft (nothing
is applied to a generator). The integrating session's records, from main `8aec3020`.

| Step | Commit | What it did |
|---|---|---|
| 1 | `0918d797` | merge of `fnd/l4e8` at `3c8f7a1f`: **L4-E8**, board A's VBUS20 bank re-sized |
| 2 | `1c09420b` | merge of `fnd/l4e7` at `91e9a4b5`: **L4-E7R**, the 100 W control on board E and its CS101 correction |
| 3 | `7c839b7a` | merge of `fnd/l4e10` at `573c8b8f`: **L4-E10**, FEA-008's cell and thermal comparison |
| 4 | `4fd8e9de` | merge of `fnd/l4e11` at `a15ab384`: **L4-E11**, U-04 source-only operation and the D-06 vehicle entry |
| 5 | `38bd0004` | merge of `fnd/l4e12` at `db41c95d`: **L4-E12** (MESHSAT-1478), the electronics against the inside air |
| 6 | `b2cb0c0a` | merge of `fnd/l4e9` at `caefa02f`: **L4-E9**, the connected architecture A1 under D-06 and the closure gate |
| 7 | `915406fd` | L4-E9's output regenerated: its pinned inputs from the five other tasks now read from the tree, with the same sha256 each; 32 lines change only their provenance wording (from a branch commit to the tree), checked line by line |
| 8 | `948b4079` | this record, first issue |
| 9 | `bab8d460` | the safe-operating-area readers of L4-E9 and L4-E11 take either poppler SVG serialisation; both outputs unchanged byte for byte; `test_l4e_svg_readers` pins both forms |
| 10 | this commit | this record, second issue (the box's first run) |

**What the steps contain:**
- **L4-E8.** The bank is derived from a dense node analysis, with a conservative bound over independent cans (hull and Minkowski sum). Six cans, each behind a 45 mOhm ballast; Cc2 3.3 nF for the cold-ESR loop. B-4 closes at R11 8 mOhm; the 7 mOhm fallback stays CONDITIONAL.
- **L4-E7R.** Approach C: a WSL sense bank, INA169, TPS3701 and a TPS3808 holding SWEN low, off by default. The static bound is 93.55 W, CONDITIONAL on two named INA169 terms. The CS101 correction puts the bulk ahead of the bank, with a 4 ms trip filter (five 100 nF C0G across R66). The worst immunity ripple is 0.0585 A against a 0.1130 A margin.
- **L4-E10.** A feasibility screen and a bounded comparison of three complete approaches. The recommendation is a wide-temperature 18650 in D-06's 4S3P, CONDITIONAL on the maker's signed specification and the owner's approval. FEA-008 is **not** closed.
- **L4-E11.** The LM5069 is replaced by a TPS48110-Q1 with a CSD19536KTT, which starts from a 9.00 V plug (REQ-015 a CONDITIONAL CANDIDATE). D-06's vehicle entry is rated at 20 A or more with a controlled DC-loop floor (56.93 mOhm, 900 A against F1's 1000 A).
- **L4-E12.** E3-O holds as stated from 1.806 W/K. E5 with the margin hold is CONDITIONAL on T-H1 at 2.159 W/K. The SGP41 is the owner question CFL-002 (options A, B, C).
- **L4-E9.** The connected architecture A1 under D-06, with no material power-path defect open. The five-criterion gate is **NOT CLOSED**, held by U-01 (the cell's signed specification), U-02 (T-H1 and the fans), U-04 (TI's N1 answer or the bench's VSYS) and U-03 (the panel; L4-E13 in its fix round). Its register holds 137 downstream items, and LH-01 to LH-11 form the Layer 5 handover.
- **For the owner to send:** the makers' clarification drafts filed with each task.
- **The checks:** in every task, the collaborator's focused check and its recheck were not accepted; the coordinator's closing checks accepted the fixed versions (L4-E8 check 3; L4-E7R checks 3 and 4; L4-E10, L4-E11 and L4-E12 check 3; L4-E9 checks 3 and 4).

**Gates on the runner, at `b2cb0c0a` and after step 7:**
- the registry: 145 records and 59 rules, 0 errors and 0 warnings;
- every page current, and the render order run twice with no page moved;
- the dry run byte for byte;
- `verify_l3am` 19 of 19, `verify_acceptance` 18 of 18, `l3n01_mutation` PASS;
- the modules at `b2cb0c0a`: 337 passed and 1 failed (`test_l4e9`'s byte-for-byte reproduction, the provenance wording of step 7); after step 7, `test_l4e9` and `test_public_hygiene` 41 of 41.

The box suite on the set's tip is the promotion gate. Its evidence archive adds the 21 held makers' sheets of these tasks (ignored files, never committed).

**The box's first run, at `948b4079`: 2493 passed, 82 failed, 3 skipped.** Every failure was in `test_l4e9` to `test_l4e12`, where the record scripts refused (exit 3 or 4) before printing. Three causes, all in the environment or the checking instruments, none in an engineering figure:
- **The box had no `poppler-data`**, so pdftotext could not read the JST VH catalogue (its Japanese font mapping), and L4-E9 and L4-E11 refused on "the VH rating not found". Installed on the box.
- **The box's poppler 24 writes `pdftocairo -svg` differently from the runner's poppler 22:** stroke attributes instead of a style property, and a space after each comma. The path coordinates are the same. L4-E9's and L4-E11's readers matched the poppler 22 text literally and refused on "Figure 10's frame". This was an instrument defect: it failed closed, so no wrong figure was printed. Step 9 fixes it, and both scripts now reproduce byte for byte on the box under Python 3.12 and 3.11.
- **The interpreter.** CPython 3.12's `sum()` of floats is compensated, so `rv-pwr/pwr_budget.py` writes one load as 36.8 W where the runner's CPython 3.11 writes 36.81 W. L4-E10 and L4-E12 re-run it and compare its JSON byte for byte (their step 0a), so they refused on 3.12. On CPython 3.11 (3.11.17 on the box), both reproduce byte for byte.
  - The box suite therefore runs in two passes (`box_suite2.sh`): every module except `test_l4e10` and `test_l4e12` on the box's Python 3.12 (with KiCad's `pcbnew`), then those two on CPython 3.11. Every test runs once, each pass has its own log, and both are gated.
  - Open, a checking-tool maintenance item: `pwr_budget.py`'s rounding depends on the interpreter's float summation. Making it interpreter-independent changes its committed JSON, which other records pin, so it waits for that record's next re-issue.
