acceptable: yes
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026): acceptable, no blocking item; n1 to n3 answered by patch_od01l.py (wording, not re-checked). -->

# AI review: confirmation of check 10's items, fnd/od01b at 7d0871d1 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review (it wrote check
10, which the commit answers). It ran on 29 September 2026 from 12:29 to about 12:32 CEST (read from `date`) in the
read-only scratch clone, detached at `7d0871d1629c9aa2d21cf26cce61625f0f528a4f` (parent `dc45a87e`, author the owner's
identity, 8 files changed). `fnd/a1int` was fetched again: its tip is `637c9876`, the commit check 10 read.

Scope: the one commit `dc45a87e..7d0871d1` (`patch_od01k.py`). TEST-PROCEDURE section 1 and section 8 were read whole, and
the brief and the README searched for anything the new text touches. `patch_od01k.py` was replayed on a copy of the
`dc45a87e` tree in the session's scratch space. No box, agent or other model was used, and nothing was committed.

B1 is answered, and m1 to m8 are answered as asked. Three wording items remain. The first comes from check 10's own
suggested fix.

## Blocking

None.

## Check 10's items

| Item | Answered | Reading |
|---|---|---|
| B1 | yes | The preamble (lines 34 to 40) now describes both changes: the base pockets' 4S6P (a second 4S3P block in the west pocket) and a 4S14P or 4S15P lid pack. That matches `a1mech/README.md` lines 6 to 7 and `a1int/RECONCILE.md` lines 18 to 19 (4S20P and 4S21P in all). T5 is "partly": the east wall and the back wall are unchanged, and the west wall's holes wait on the re-plan (line 53). That agrees with `a1mech/README.md` lines 271 to 272 and 293 and with `ENERGY-RECONCILIATION.md` of this tree. C4-W has its own row (line 47; see n1). T4 names both missing stand-ins (line 54), matching a1mech section 6 (M4a west, M6w OPEN at T4). The lid-open row says the set-up measures the base without the west block (line 49). The lid-closed row asks for a twin of H3 as well as a lid dummy (line 50). The patch runs are independent of the pockets. |
| m1 | yes | Lines 416 to 418 now say that a warming step's reading is at most an upper bound on `G`, and that room drift, a cooling step (S4 after S3) and a point reading of stratified air remove even that. The conclusion that a stopped step yields no `G` is unchanged. |
| m2 | yes | Line 65: "the rise up to 0.33 K low, so `G` up to 1.1 % high" (3.3 % at 21 W). This agrees with the combined row and section 8. |
| m3 | yes | README lines 40 to 44 say the manifest verifies "the 50 files it lists, run inside `v2/release/case-2026-09-27/` of a complete clone (`sha256sum -c MANIFEST.sha256`)". The package carries 30 of them, and the two later folders carry their own manifests. All of this is true: all three manifests read OK where the README says to run them. |
| m4 | yes | The standing rule is cited "on main, commit `bf68ad9e`". Its lines 535 to 553 there hold the rule and Q1 to Q4. |
| m5 | yes | The pack size is cited from `a1int/RECONCILE.md` (4S14P or 4S15P). |
| m6 | yes | T6 is "yes, as a bound (INFERRED)", with the reason (line 55). The bound holds either way: if Peli's stop is short of 100 degrees, the stay is slack and the lid stops where T6 reads it. See n2 for the plate footprint. |
| m7 | yes | The "New" row (line 56) lists a1mech section 7 in full: T-A1-1 to T-A1-4, T9 with a dummy module, T8's pull test, E1 and E2 with an accelerometer, T10 and T5 at the west wall, and S-95. |
| m8 | yes | The C1 row names S-95 as older than A(i) and needed for the QMX leads. |
| m9 | noted | The LOG's 12:26 row says the README's scripts and checks rows are edited by hand. The replay confirms that these two rows are the only difference. |

Every row of the new table was checked against the procedure and the A(i) record:
- R1 to R8: the case is unchanged.
- H1 and C6: a1mech gives the west block alone 37.77 from the legs (M5w, MET), so C6 meets neither the lid nor the west block.
- C1: see m8.
- The shutdown: unchanged.
- The lid-open and lid-closed steps and the patch runs: as in B1 above.
- T1, T2 and T11: T11 uses the east plate or a coupon (section 7).
- T5, T4, T6 and the new row: as above.

Nothing in the table adopts A(i).

## Minor items

- **n1. C4-W's label (line 47).** The row calls C4-W "for the mock-up" and "a mock-up plate". The RFQ (line 29) makes
  C4-W a build part: stage "second (east plate only), rest at build", and T11 uses the east plate or a coupon. The row's
  verdict is right: C4-W as drawn is not A(i)'s plate, and C4-E is unchanged. Nothing cuts C4-W before the build. The
  label came from check 10's own suggested fix (B1 item 5), which was imprecise. Suggest: "C4-W (west entry plate), cut
  only at the build (RFQ line 29) | no, as the kit's plate under A(i) | ... C4-W as drawn waits on the re-plan".
- **n2. T6's other part (line 55).** T6 also offers each entry plate's footprint to its end wall, from the check prints.
  The west footprint is C4-W's, which the table says A(i) may change. a1mech names only T5 and T10 at the west wall, so
  "yes, as a bound" is consistent with the record for the lid. A clause would close the gap: "the west plate's
  footprint as drawn; if the re-plan changes C4-W's outline, that part waits too".
- **n3. "a second 4S3P block in the west pocket beside the east one" (line 36).** The pockets are at opposite ends, 240
  mm apart in X (`ENERGY-RECONCILIATION.md` 8b). "In addition to the east one" avoids reading "beside" as adjacent.

## Verified

- **Replay.** `patch_od01k.py` on the `dc45a87e` tree reproduces `TEST-PROCEDURE.md` and `TEST-BRIEF.md` byte for byte.
  `README.md` differs only in the checks row and the scripts row, which are edited by hand (m9). A second run is refused
  ("already applied"). The filed `checks/check-10.md` is the checker's file with one provenance comment added as line 2.
- **No contradiction elsewhere.** Section 1's opening sentence, the uncertainty table, section 5.4, section 6 step 1,
  section 7's checks, section 8 (the S6 note included) and section 9 agree with the new table and the new sentence.
  So do the brief (unchanged, sha256 `f62917ab`) and the README. Section 4's single pack pocket and D2's "the pack in
  its pocket" describe the current design; the table states the west block as A(i)'s difference.
- **Package.** From the clone root, `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` reads OK for all 78 files. The
  78 rows of `PACKAGE.md` match the files in bytes and sha256 and are the same set as the sha256 list. They total
  14,891,456 bytes (the page's "14.9 MB"), written at tree `dc45a87e`.
- **Hygiene.** No em or en dash, or any character from U+2010 to U+2015 or U+2212, in any `.md` of the folder. The only
  dashes in the commit's added lines are the new script's dash-detector constant. No user path: the only `/home/` hits
  are the words of checks 8 and 9 describing that search.
