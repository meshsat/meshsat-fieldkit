acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026); paths generalised on filing. Its blocking item C1 and minor items s1 and s2 are answered by patch_od01h.py; see LOG-od01b.md. -->

# AI review: re-check of the OD-01 package, fnd/od01b at 71407a46 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review. It ran on 29
September 2026 from 04:40 to about 04:50 CEST (read from `date`) in the read-only scratch clone at `71407a460671`.

Scope: the changed text read against sheet H1-1's DXF and the circuit; TEST-PROCEDURE sections 3, 4 and 6 and the
brief's section 5 read end to end again; section 8; `patch_od01g.py` replayed on a copy of the `28f7a990` tree in the
session's scratch space. No box, no agent, no other model, no commit.

All of check 7's items are answered: B1, B2 and r1 to r14. One inconsistency remains, and it is the one the coordinator
asked about. Section 6 now says, correctly, that the shutdown switches nothing in the patch runs. Section 8 still names TS3
as the automatic guard of CH4's 70 C limit, and CH4 stays at the far end of H1 during the patch runs.

## Blocking

**C1. In the patch runs, no one reads H1's edge over the o-ring nearest the patch, yet section 8 says TS3 guards it.**
- The claim. TEST-PROCEDURE line 374 names TS3 as the automatic guard of CH4's 70 C limit, with no step qualifier. The
  CH7 rows, lines 376 and 377, do carry one. Line 131 ("TS3 holds H1 at or under 63 C, and so its edge over the o-ring")
  is unqualified in the same way.
- Why it is false in the patch runs. Section 6 keeps CH4 with its 70 C limit ("keep CH1, CH2 and CH4", line 328). But
  step 2 (lines 325 to 327) says truly that the shutdown switches nothing there: the heaters are off, the link block is
  open, and the supply feeds the HS100 alone. So TS3 opening drops K1 and K2 and stops nothing.
- Where the heat actually reaches the edge. CH4 stays at X +186, Y 0, about 240 mm from the resistor. The band nearest
  the patch (X -45, Y +126.5 to 131.5) is about 24 mm from the end of the HS100's body (Arcol E 65.2, centred on Y 70).
- How hot it gets. A rough conduction estimate (INFERRED) makes that band reach about 68 C at 30 s, 74 C at 43 s and 79
  C at 60 s. The estimate uses a 3 mm plate from 50 C, 83 W into the foot, 10 W/m2K per face, adiabatic edges, and
  ignores the resistor's own heat capacity. CH4's place stays under 49 C in the same run. So the 83 W pulses can pass the
  procedure's own 70 C limit where nothing reads it, while section 8 tells the operator that limit is enforced
  automatically.
- The brief (line 92) names only the 110 C stop for the patch runs.

Fix:
1. Patch map (line 328 and the table): "keep CH1 and CH2; move CH4 to the band nearest the resistor". Add the row "CH4 |
   H1's rebated band at X -45.0, Y +129.0 (the band's middle nearest the resistor, over the o-ring) | **70 C**". Sheet
   H1-1's nearest face screws are at X 0 and X -139.45 on Y +121.16, 45 mm and more away.
2. Step 5: "Switch off at once if CH7 reaches 110 C or CH4 reaches 70 C".
3. Step 2's last clause: "section 8's limits for the patch runs (110 C on the HS100, 70 C at CH4) are the operator's".
4. Section 8: qualify the CH5, CH4 and CH6 rows "(steady-state steps)". Add the row "H1's edge over the o-ring nearest the
   patch (CH4, patch runs) | 70 C | the attending operator".
5. Line 131: "TS3 holds H1 at or under 63 C in the steady-state steps".
6. Brief line 92: "stopped at once at 110 C on the resistor's body or 70 C on H1's band nearest it".

## Check 7's items

| Item | Answered | Reading |
|---|---|---|
| B1 | yes | CH4 is now at X 0, Y -129 (lines 188 to 189). The DXF's REBATE_2MM_TOP line is at |Y| 126.5 and the outline at 131.5, so -129 is the band's middle. The o-ring channel runs outside the frame's 252.88 flange (|Y| 126.44 outward). The face screw's head, at most 6.86 across on the hole at Y -121.16, ends at Y -124.6, 4.4 mm clear. |
| B2 | yes | Step 2 (lines 322 to 324) frees CH5, CH6 and CH8 with CH7 before H1 is refitted. Step 3 then tapes CH3, CH5, CH6 and CH8 on top. No spare thermocouple is needed. |
| r1 | yes | Lines 209 to 211 now say what a heater-lead short shows with the link block open, and call it a fail. That matches the circuit (INFERRED as to how fast F2 blows). |
| r2, r3, r8, r9, r10, r11, r12, r13 | yes | Lines 120 and 122 keep the tape 3 mm clear of the tabs. Line 151 makes the coil chain silicone wire. Line 185 lifts H2 to reach TS2. Lines 191 to 192 set the gun and aim it. VD1 and VD2 appear at lines 127 and 156 and checkout line 15; no "D1, D2" is left. Line 248 puts V1 before the in-case wiring. Line 240 and checkout line 15 add H2's M4 screws. Line 57 (D5) names every lead. |
| r4, r5 | yes | V4 (a) (lines 197 to 198) now covers the case after a trip. Step 1 (line 317) covers an S6 that stopped at a limit. |
| r6 | yes, and true as wired | Line 338 moves the supply to the HS100 (or uses a second supply), and the link block stays open. K1 and K2 switch only the heater path, so the shutdown stops nothing in the patch runs. Sections 3 and 8 still say otherwise for CH4: C1. |
| r7 | partly | "No gap except over the leads" is fixed. The 10 mm clearance from the ten screws sits only in item 8, after H1 has clamped the leads (s1). |
| r14 | partly | `patch_od01f.py` now builds its literal from parts, and check-5 line 96 is generalised. But the box path has come back in two other files (s2). |

## Sections 3, 4 and 6 and brief section 5, read again

- Section 3: the circuit, V1 to V4, "what it shows" and the residual risk agree with one another and with the circuit.
  The one exception is line 131 (C1).
- Section 4: the order holds. V1 and V2 come before item 4, V3 (a) after item 7, V3 (b) after item 8, and V4 before S1.
- Section 6: the order holds once C1 is fixed. There is no V3 repeat, and the thermocouples move before the refit.
- Brief section 5: it claims no shutdown cover for the patch runs, but lists only the 110 C stop for them (C1).

## Minor

- **s1.** Line 275: "every lead at least 10 mm from the ten screws" is checked after H1 is screwed down. Move it into
  item 7 (and wiring item 2), where the leads are laid.
- **s2.** The box path `the box's work directory` is back in two places:
  - The filed `checks/check-7.md`, line 124, quotes it, and check-7 is a package file.
  - `patch_od01g.py`, line 102, carries it as a search literal, the pattern r14 named.

  In addition, `patch_od01e.py` line 150 holds the path in a regex, and `patch_od01f.py` line 205 holds the account name
  the runner's account name as a detector literal. Fix: generalise check-7's quote in its filing note, as was done for check 5, and
  build the literals from parts.

## Verified

- **Replay.** `git archive 28f7a990` of the od01 folder, the filed `patch_od01g.py` beside it, and `git init` in the
  session's scratch space. The run printed "B1, B2 and r1 to r14 answered", exit 0. TEST-PROCEDURE.md, CHECKOUT-LIST.md,
  `checks/check-5.md` and `patch_od01f.py` then equal the files at `71407a46` byte for byte. So the tree is what the
  script's edits describe. The filed script differs from the one that ran only in the split literal, as the 04:39 LOG
  row says.
- **Other changed files.** The filed check-7.md equals the returned CHECK-7.md plus one filing-note line. The README,
  PACKAGE.md and `make_package.py` changes add check 7 and `patch_od01g.py`. The brief is unchanged.
- **User paths.** No file in the od01 folder or in the package holds `/home/` joined to the account name, a host name
  or an address. Box path and account-name literals: s2.
- **Checksums and tests.** HEAD is `71407a46`; the only untracked files are check files.
  `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` from the root gives 75 of 75 OK. H1's `MANIFEST.sha256` gives 6 of
  6 OK, and the case release manifest 50 of 50 OK. `run.py test_h1_heat_test_plate`: 6 passed, 0 failed.
  `test_case_geometry`: 11 passed, 0 failed.
- **Brief and dashes.** The brief built with pandoc and xelatex (A4, 10 pt, 2 cm margins) is 2 pages. No package document
  has an em or en dash; dash literals appear only in the detectors of the patch scripts.
