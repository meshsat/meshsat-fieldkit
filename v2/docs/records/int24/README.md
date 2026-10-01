# Integration set 24 (MESHSAT-1357, branch `fnd/int24`, 1 October 2026): the qualification of L4-E7's 100 W bound

Prototype design: nothing is bought, built or measured. The integrating session's records, from main `3975e90b`.

| Step | Commit | What it did |
|---|---|---|
| 1 | `f23064f7` | merge of `fnd/l4e7` at `922c8a9f`: **the qualification of the 100 W bound** (`records/l4e7/L4E7-QUALIFICATION.md`), on the owner's instruction of 1 October 2026 |
| 2 | this commit | this record |

**What step 1 contains:**
- **The sheet.** The held `lt8705a.pdf` is byte for byte the sheet at the owner's URL; the Internet Archive record is filed.
- **The classification.** Each value with no printed guaranteed limit is classed by the outcome it affects: the 100 W bound, stability, protection or other.
- **The result.** 96.25 W stays a calculated result under its stated assumptions, **CONDITIONAL** on five values:
  - EA2's gain and VC's range;
  - A7's gain away from its 50 mV, 5.025 V test point;
  - the line regulation while switching and at temperature;
  - RSENSE1's TCR below +25 C;
  - U5's junction temperature, an inferred estimate.
- **The margin.** Every conservative assumption together, with the resistors' drifts, gives 99.8992 W: 0.1008 W of margin.
- **The range argument** covers the input voltage, every tolerance direction, both temperature ends with a mixed-temperature envelope, and the states outside the corners. Those states are bench row 7b.9t, which includes the cold-soaked irradiance step.
- **No part changed.**
- **For the owner to send:** clarification drafts for Analog Devices and Milliohm, asking for manufacturer-warranted limits.
- **The checks:**
  - the collaborator's focused check was not accepted (B1, A7's test point; B2, the TCR's small effects);
  - its recheck accepted the fixes;
  - the coordinator's check 3 recomputed stack A's corner and A7's break-even in separate arithmetic.

**Gates on the runner, at `f23064f7`:**
- the registry: 145 records and 59 rules, 0 errors and 0 warnings;
- every page current, and the render order run twice with no page moved;
- the dry run byte for byte;
- `verify_l3am` 19 of 19, `verify_acceptance` 18 of 18, `l3n01_mutation` PASS;
- the modules: 213 passed, 0 failed, 0 skipped.

The box suite on the set's tip is the promotion gate. Its evidence archive adds the held Vishay WSL sheet.
