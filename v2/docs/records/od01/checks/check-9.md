acceptable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). Acceptable, no blocking item; its wording items t1 to t5 are answered by patch_od01i.py (text only, not re-checked); see LOG-od01b.md. -->

# AI review: confirmation of check 8's items, fnd/od01b at e5425cd5 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review. It ran on 29
September 2026 from 04:45 to about 04:50 CEST (read from `date`) in the read-only scratch clone at `e5425cd5b2d0`.

Scope:
- The changed text, read against sheet H1-1's DXF.
- TEST-PROCEDURE sections 3, 6 and 8 read whole, with section 9's records.
- The brief's section 5 and the README.
- `patch_od01h.py` replayed on a copy of the `71407a46` tree in the session's scratch space.

No box, agent or other model was used, and nothing was committed.

C1, s1 and s2 are answered. The edit leaves three places that still name only the 110 C patch stop, and one table
qualifier short. All are wording; none lets an operator reach an unread or unguarded heating state.

## Blocking

None.

## Check 8's items

| Item | Answered | Reading |
|---|---|---|
| C1 | yes | See the six points below. |
| s1 | yes | Item 7 now reads "Lay every lead at least 10 mm from the ten screw holes (sheet H1-1)", before H1 clamps the leads. Item 8 checks it again. |
| s2 | yes, as stated | check-7 line 124 is generalised. The patch scripts keep their box-path literals as records of their runs, by the policy that `patch_od01h.py`'s docstring and the 04:45 LOG row state; that includes `patch_od01h.py` line 66. No file in the folder holds a user path: a grep for `/home/claude` finds nothing. |

C1, point by point:
1. **Position.** The patch map's CH4 is at X -45.0, Y +129.0 (line 334). On the DXF the band runs from |Y| 126.5 to 131.5,
   so -45, +129 is its middle, over the o-ring channel (|Y| 126.44 outward).
2. **Clearance.** The nearest face screw hole is at X 0, Y +121.16, 45.7 mm away; its head is at most 6.86 across, which
   leaves 42.3 mm clear. The next hole, at X -139.45, is 94.8 mm away. The top-face PEM nuts at X -26.5 and -63.5, Y
   87.5 are at least 45 mm away.
3. **The stop.** Step 5 (line 344) stops at "CH7 reaches 110 C or CH4 reaches 70 C". Brief lines 92 to 93 say the same.
4. **Section 3.** Lines 131 to 132 limit TS3's cover to the steady-state steps.
5. **Section 8.** The CH4 row (line 376) names TS3 in the steady-state steps and the operator in the patch runs. The new
   sentence (lines 382 to 383) is true of the circuit: the heaters are off, and the supply feeds the HS100 alone.
6. **The steady-state steps are unchanged.** CH4 stays at X +186, Y 0 (line 262), V3 (b) still returns CH3 and CH4 to the
   map in use, and TS3's cover is unchanged.

## Minor

- **t1.** Section 6 step 2, line 328: "section 8's 110 C limit on the HS100 is the operator's" names one of the two
  patch limits. Write "section 8's limits for the patch runs (110 C at CH7, 70 C at CH4) are the operator's".
- **t2.** Section 3, line 148: "stop at the patch stop of 110 C". Write "stop at the patch stops (110 C at CH7, 70 C at
  CH4)".
- **t3.** Section 9, line 399: the patch columns give only `time_to_110C_s`, so a CH4 stop has no column. Write
  `time_to_stop_s, stopped_by` (CH7 or CH4).
- **t4.** Section 8, lines 375 and 377: the CH5 and CH6 rows carry no step qualifier. In the patch map, CH5 and CH6 sit on
  H1's top face with no limit, so an operator might apply 70 C and 100 C to them there. That would cost only a premature
  stop. Write "(CH5, steady-state steps)" and "(CH6, steady-state steps)", as the CH7 rows already do.
- **t5.** The filed `checks/check-8.md` line 76 quotes the runner's account name in my own wording. It is not a user
  path. If the account name should stay out of the package, write "the runner's account name" there on filing.

## Verified

- **Replay.** `git archive 71407a46` of the od01 folder, the filed `patch_od01h.py` beside it, and `git init` in the
  session's scratch space. The run printed "C1, s1 and s2 answered", exit 0. TEST-PROCEDURE.md, TEST-BRIEF.md and
  `checks/check-7.md` then equal the files at `e5425cd5` byte for byte.
- **Other changed files.** The filed check-8 equals the returned CHECK-8.md plus one filing-note line and the box path
  generalised. README, PACKAGE.md, `make_package.py` and the LOG add check 8 and `patch_od01h.py`. PACKAGE.md states 76
  files at tree `71407a46` plus its working files.
- **Checksums and tests.**
  - HEAD is `e5425cd5`; the only untracked files are check files.
  - `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` from the root: 76 of 76 OK.
  - H1's `MANIFEST.sha256`: 6 of 6 OK. The case release manifest: 50 of 50 OK.
  - `run.py test_h1_heat_test_plate`: 6 passed, 0 failed. `test_case_geometry`: 11 passed, 0 failed.
- **Brief.** Built with pandoc and xelatex (A4, 10 pt, 2 cm margins), it is 2 pages.
- **Dashes.** No document in the folder has an em or en dash; dash literals appear only in the detectors of the patch
  scripts.
