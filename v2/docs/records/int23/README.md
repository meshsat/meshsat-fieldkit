# Integration set 23 (MESHSAT-1357, branch `fnd/int23`, 1 October 2026): Layer 4's solar stage settings

Prototype design: nothing is bought, built or measured. The integrating session's records, from set 22 (`cece7c1c`, main).

| Step | Commit | What it did |
|---|---|---|
| 1 | `93393226` | merge of `fnd/l4e7` at `9d42bee1`: **L4-E7, the solar stage's real settings** (the power review's implementable choice 3, finding O-2, review L4-R01). U5 the LT8705AI (the QFN land is offered only in E and I; only I is guaranteed below 0 C junction); a new input sense resistor RSENSE1 (R59) 15 mOhm on a new net TRK_VIN, since as drawn U5's input sense is tied off and no input limit acts; RIMON_IN 23.2k for 3.4713 A and CIMON_IN 100 nF; the 100 W corner at 25 V reads 96.2474 W cold and 96.2291 W hot under the printed limits and passes the design floor; the hold kept at REQ-016's 17.6 V point (102k over 7.50k as 0.1 % parts, band 16.970 to 18.221 V). Drafts for board E's generator owner, refused against the repository's generator until a `RELEASE.md`. The collaborator's check (`astra-check-l4e7-1`) not accepted (B1: the author's first hold, 16.340 V, changed REQ-016's approved operating point, retained by D-34); its recheck (`astra-check-l4e7-2`) accepted; the coordinator's check 3 recomputed the band in separate code and reproduced the output |
| 2 | this commit | this record |

**Not adopted:** the 16.340 V hold, about 25.0 Wh a day more on the design day, would change REQ-016 and needs the owner's
ruling; it is recorded as a proposal on the L4-E7 page, and nothing is drafted for it or depends on it.

**Open, carried:** the unprinted rows (EA2's gain, the line regulation while switching and at temperature, RSENSE1's TCR
below 25 C, EA3's gain and the FBIN bias, U5's junction) as bench rows 7b.9 to 7b.13; R59's Kelvin taps and placement; the
regeneration of board E with its gates; L4-E4 still PROVISIONAL (B-4, the bank's re-size).

**Gates on the runner, at `93393226`:** the registry 145 records and 59 rules, 0 errors and 0 warnings; every page current;
the render order twice with no page moved; the dry run byte for byte; `verify_l3am` 19 of 19, `verify_acceptance` 18 of 18,
`l3n01_mutation` PASS; the Layer 3, Layer 4 and hygiene modules with `test_l4e7` 202 passed, 0 failed, 0 skipped. The box
suite on the set's tip is the promotion gate; its evidence archive adds L4-E7's two held makers' sheets (YAGEO RT series,
Infineon BSC028N06NS).
