acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). Its blocking items N1 and N2 and the minor items n1 to n5 and n7 to n13 are answered by patch_od01d.py; n6 is carried to H1's next box build; see LOG-od01b.md. -->

# AI review: focused re-check of the OD-01 corrections, fnd/od01b at a6420c37 (MESHSAT-1357)

AI review by the checker of check 3 (it wrote none of the work), 29 September 2026, 03:37 to about 03:50 CEST. Not a
qualified engineering review. Read-only scratch clone `the checker scratch clone`
(`git clone --shared` of the main checkout, `fnd/od01b` fetched from the worktree `od01b`, detached at `a6420c37`). Scope as
the brief sets it: whether check 3's B1, B2 and m1 to m13 are answered, and whether the corrections (`e0cd5ec1`,
`a6420c37`: `patch_od01c.py`, the H1 generator change, the regenerated H1 files, the manifest, the package list, the log)
introduced a new inconsistency. No box, no Agent, no Codex, no commit.

Both of check 3's blocking items are answered correctly. Two new blocking defects are left, both one-line text edits that
need no regeneration. After them, and the two package hashes they move, I see nothing further that blocks.

## Blocking (new)

**N1. The checkout list's total for lines 1 to 14 was not updated for the second relay.** `CHECKOUT-LIST.md` lines 105 to
107: the shutdown subtotal is now "EUR 68.40 excl. VAT, EUR 82.76 incl." (correct: 10.50 + 22.26 + 19.58 + 8.24 + 7.82 =
68.40; 12.71 + 26.94 + 23.69 + 9.96 + 9.46 = 82.76), but the next sentence still reads "with them, lines 1 to 14 would be
EUR 476.77 excl. VAT", which was 416.40 + 60.37. It is now 416.40 + 68.40 = **EUR 484.80**. A wrong total on the owner's
purchasing page is the defect class check 1 raised as blocking (B3).

**N2. The request text still orders H1's nut holes at 4.2, against sheet H1-1's 4.22 +0.08.** `MACHINING-RFQ.md` section 3,
line 81: "four PEM S-M3-2 self-clinching nuts in 4.2 holes". Sheet H1-1 (the Holes block and the tolerance box: "4 x d4.22
THRU (+0.08/-0.00, PEM bulletin CL)", "the four PEM holes 4.22 +0.08/-0.00"), the H1 DXF (four circles of 4.22) and the H1
README now say 4.22 +0.08. The shop receives both the request text and the sheet. This is a new contradiction between the
RFQ text and a drawing, which the owner's R6 excluded, and it leaves m1 half answered. Fix: "in 4.22 +0.08/-0.00 holes
(PEM bulletin CL)".

## Check 3's items

| Item | Answered? | What I read |
|---|---|---|
| B1 | yes | One gate set everywhere: RFQ section 1 (H1 and C1 R1, R2, R3, R5, R6; C6 R1, R3, R4, R5; C4 and C3 R1, R3, R7, R8), the RFQ section 6 table, TEST-PROCEDURE section 2 item 1, TEST-BRIEF lines 8 and 16, sheet H1-1 note 5 and the H1 README. Minor n12 and n13 below. |
| B2 | yes | TS3's centre is at X 0, Y -104; the 16.0 mm body spans Y -112 to -96, 4.92 mm inside the window edge at -116.92 (Honeywell Figure 3 cited). Minor n11 (its bracket). |
| m1 | partly | Bulletin filed (`v2/vendor/pem/`, sha256 `82961283...` equal to mine; registered in both `sources.txt`). The generator sets `PEM_HOLE = 4.22` with `+0.08/-0.00`, the DXF carries 4.22, sheet and H1 README choice 1 cite PEM. Still stale: the RFQ request text (N2) and `od01/README.md` lines 47 to 48 (n7). |
| m2 | yes | K2 and X2 added, K2's 11-14 in series with K1's, coils in parallel after the chain; V4 reads each 11-14 open with the supply off; residual risk rewritten; checkout lines 13 and 14 at two each. Minor n1, n2, n9. |
| m3 | yes | D1 and D2 are 1N4007s across each coil, cathode to A1. That polarity is right for the wiring (TS4 to A1, A2 to supply minus). |
| m4 | yes | "supply loss" and the 0.1 of rated voltage, in the procedure and the brief. |
| m5 | yes | V3 now trips each installed thermostat and sees the meter fall. Minor n3. |
| m6 | yes | F1 7.5 A at the supply plus before K1, F2 1 A at the start of the coil chain; table and wiring agree. |
| m7 | yes | Section 6 lifts H1, mounts the HS100, refits H1 and repeats V3 before any heating. |
| m8 | yes | "-2 to +4 %" and "-4 to +8 %", both bounds rounded outward from -1.5 to +3.6 and -3.2 to +7.5. |
| m9 | yes | READY-TO-ACT.md, ASSEMBLY.md, the lid tray README, the PEM bulletin and check-3 are in the package. Minor n8. |
| m10 | yes | Sheet: "relief 44.0 x 9.0 x 0.8 deep in the UNDERSIDE, X -110.9 to -66.9, Y -125.4 to -116.4", and "the relief's position +-0.5" in the tolerance box. |
| m11 | yes | R2 is now read at the rim face, where the quoted STEP figures are taken. |
| m12 | yes | C1's request text: "the PEM hardware is inserted after anodising (PEM's own instruction, bulletin CL)". |
| m13 | yes | LOG-od01b.md, 02:40 row. |

## Minor (new, introduced or left by the corrections)

- **n1. The coil current doubled but the text still says 54 mA.** With two coils in parallel, the thermostats and F2 now
  carry about 108 mA (1.3 W). TEST-PROCEDURE lines 110 and 158 and CHECKOUT-LIST line 94 still say 54 mA.
- **n2. The brief still describes one relay.** TEST-BRIEF's safety bullet says "the coil of a Finder 40.52 relay that
  switches the heaters and holds itself in", and its equipment list says "the relay and its socket". The brief omits K2 and
  the diodes.
- **n3. V2 and V3 still read "the load side of K1".** V2 (lines 166 to 168) puts the meter "at the link block's input (the
  load side of K1)" and names only K1 pulling in; with K2 in series that point is K2's load side. V3's new first part does
  not say the link block is open, so the heaters could be energised with H1 lifted. Its air gun also has to bring TS2 on the
  polypropylene floor to 60 C and TS4 to 140 C inside the case (Peli's body maximum is 88 C). Lifting one lead at each
  thermostat and seeing K1 drop proves chain membership without heating.
- **n4. The checkout part text still names one relay and one socket.** Lines 13 and 14 end "(K1)" and "(X1)" while the
  quantity column says "2 (K1, K2)" and "2 (X1, X2)".
- **n5. H1 README "Source revision" is stale.** It still says the files were generated at 01:53 CEST from `c5a95973`, that
  "the STL bytes are identical in all four", and gives `--base c5a95973`. The files now come from `e0cd5ec1`: the manifest
  header and the sheet's title block say so, and the STL differs from the previous build (byte 27797). The input list also
  omits the drawing script, whose hash `8e0d56a6a030` the sheet prints.
- **n6. The check record prints "four 4.2 holes".** `h1-heat-test-plate-check.out` line 17 does so because the check formats
  `PEM_HOLE` with `%.1f`; the compared value is 4.22. Use `%.2f`.
- **n7. `od01/README.md` lines 47 to 48 are stale.** They still say "PEM's S-type bulletin is not held" and that S-M3-2 is
  "the session's reading (INFERRED)".
- **n8. PACKAGE.md repeats group letters.** It carries a second "### A. Read first" and a "### D. Referenced records"
  after K, while D is already "Quote: C1 face plate". The header's "Groups A to G are what a shop needs" then also covers
  the records. The count (71 files) and the checksums are right.
- **n9. A welded K1 self-hold contact still lets the heaters cycle.** If K1 21-24 welds, the latch becomes auto-reset: the
  heaters cycle on the thermostats, which still limit temperature, so the claim "never cycle unattended" fails. V4 does not
  read 21-24. K2's spare 21-24 in series with K1's in the hold path, and V4 reading both, would close it.
- **n10. The gaskets have no gate row.** R8 names G1 to G3 among the parts it gates, but their RFQ line ("optional on this
  quote") and the procedure's gate sentence do not. This was there before; I missed it in check 3.
- **n11. TS3's bracket is not placed.** The 60 C part ships "with mounting bracket B203-S" (O20). TS3's placement covers
  the 16.0 mm body only; say how the bracket is oriented (for example its tabs along X) or removed.
- **n12. The procedure cites the wrong table for per-part rows.** Its B1 sentence says "every receipt check its row names in
  the table of MACHINING-RFQ.md section 6", but the section 6 table has one row per check; the per-part rows are in section
  1. The lists it then gives agree with both tables.
- **n13. The brief's gate sentence omits C3.** Line 16 names "H1, C6, C1 and the entry plates" and leaves out C3, which is
  quote only.

## Verified

- `sha256sum -c` of H1's MANIFEST: 6 files OK (header "from tree e0cd5ec1"). `sha256sum -c
  v2/docs/records/od01/PACKAGE.sha256` from the repository root: 71 files OK, 14.80 MB as stated. All 24 RFQ upload hashes,
  the three new H1 ones included, are in the package and equal the files.
- H1 DXF parsed without ezdxf: OUTLINE, REBATE_2MM_TOP and RELIEF_0.8MM_UNDERSIDE still equal C1's point for point
  (largest difference 0.0). The ten 4.6 holes equal C1's. PEM_S_M3 holds four 4.22 circles at X -63.5/-26.5, Y 52.5/87.5.
  There is one INFO text and nothing else.
- The check record's generator hash `9e949f9e1b9237a2` and the sheet's `9e949f9e1b92`, `8e0d56a6a030` and `3bdb88df9826`
  equal the tree's files. The check reads RESULT PASS, 15 checks (not re-run: no ezdxf or build123d on this host).
- `python3 run.py test_h1_heat_test_plate`: 6 passed; `test_case_geometry`: 11 passed (this host, the scratch clone).
- `checks/check-3.md` is my check 3 as returned, with a filing note and the scratch path generalised.
- Prices: the shutdown subtotal is right (N1 is the total after it). Line 13 = 2 x 4.12 = 8.24 excl. and 2 x 4.98 = 9.96
  incl.; line 14 = 2 x 3.91 = 7.82 and 2 x 4.73 = 9.46. "About EUR 9" for K2 with its socket matches 4.98 + 4.73 = 9.71
  incl.
