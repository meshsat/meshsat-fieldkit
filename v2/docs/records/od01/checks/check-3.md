acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). Its blocking items B1 and B2 and the minor items are answered by patch_od01c.py, the H1 generator and this folder's README; see LOG-od01b.md. -->

# AI review: independent check of the OD-01 release corrections, branch fnd/od01b at b9b9b32a (MESHSAT-1357)

AI review by one Claude checker who wrote none of the work, 29 September 2026, about 02:00 to 02:40 CEST. Not a qualified
engineering review. Read-only: scratch clone `the checker scratch clone`
(`git clone --shared` of the main checkout, `fnd/od01b` fetched from the worktree `od01b`, detached at `b9b9b32a`); this
file is the only thing written outside the session scratchpad. Scope: the diff `40dd2690..b9b9b32a` (28 files) as the
brief names it. No box, no Agent, no Codex. Prototype framing throughout: nothing here has been built, bought or measured.

Two blocking items, both one-paragraph fixes. The H1 definition, the H2 finish, the case statement, the latch topology,
the uncertainty arithmetic, the prices and the package checksums hold.

## Blocking

**B1. The package states three different gate sets for cutting; the operator's procedure drops R6 from H1 and C1.**
- `TEST-PROCEDURE.md` section 2 item 1 (lines 78 to 81): "No fit-dependent part (H1, C1, C6, the entry plates, the
  connector plate) is released for cutting before R1 to R5 pass; the entry plates and the connector plate also wait for
  R7 and R8."
- `MACHINING-RFQ.md` section 1 table (lines 25 to 28), sheet H1-1 note 5 and the H1 folder README (line 83): H1 and C1
  after R1, R2, R3, R5 and R6; C6 after R1, R3, R4 and R5; C4 after R1, R7 and R8.
- `MACHINING-RFQ.md` section 6 table, row R3 (line 172): R3 also gates "the Z of C3 and C4", which the C4 row of section 1
  omits.
- `TEST-BRIEF.md` line 8: "nothing fit-dependent is cut before the receipt checks R1 to R8"; line 16: "only after the
  checks their row names".

The procedure is the document the person running the checks reads, and its gate set leaves out R6, the insert-pattern
check that decides whether the ten 4.6 holes of H1 and C1 take Peli's inserts (M8f), while adding R4 to parts R4 does not
gate. This is the class of defect the owner's R6 named for H2's finish (two documents saying different things about one
release condition). Fix: one gate table (RFQ section 6, with a "gates" row per part that also settles R3 for C4), and every
other document cites it by part instead of restating ranges of R numbers.

**B2. TS3's stated place puts the thermostat on the 1450PF ring under H1, so H1 cannot seat.**
`TEST-PROCEDURE.md` section 3 parts table (line 119): TS3 "taped cap-up to H1's underside 5 mm inside the frame window's
edge at X 0, Y -112". The 2455R body is 16.0 mm in diameter and 11.91 mm tall (Honeywell "Commercial Thermostats",
Figure 3, page 5, held as `v2/vendor/elmwood/honeywell-commercial-thermostats-2455r.pdf`; reichelt's 2455R 90 NC page,
re-read at about 02:05 CEST: "Height 12 mm, Ø 16 mm", "Assembly Screw mounting"). The window edge is Y -116.92
(`panel1450.WINDOW` 349.65 x 233.83; the H1 check itself treats the ring as lying under the plate beyond it, "2.92 mm to its
nearest edge (Y, the ring under the plate)"). A body centred at Y -112 reaches Y -120.0, 3.1 mm over the ring, before any
bracket. H1 would ride on the thermostat instead of on the frame and o-ring; the feeler check of section 4 item 8 would
catch it at set-up, but the procedure as written cannot be followed. Fix: place TS3's body wholly inside the window with
margin (for example the centre at Y -104 or further in, with its bracket and tabs inside Y -115), state that the coordinate
is the body's centre, and keep the reasoning of line 127 (the plate near the edge within a few kelvin, INFERRED).

## Minor

- **m1. PEM S-M3-2 is now verifiable, and the hole is drawn slightly under PEM's figure.** PEM bulletin CL, "Self-Clinching
  Nuts" (https://www.pemnet.com/wp-content/uploads/sites/2/2022/06/cldata.pdf, fetched 29 Sep 2026 about 02:05 CEST, sha256
  `8296128324e3954db753661ce257e5b01cbe98a364964af1d4f862e9cc04fe0e`), S/SS/CLS/CLSS/SP metric table, M3 x 0.5: shank code 2,
  A max 1.38, min sheet 1.4, hole in sheet 4.22 +0.08, C max 4.2, E 6.35, T 1.5, min hole C/L to edge 4.8; and "DON'T
  install steel or stainless steel fasteners in aluminum panels before anodizing or finishing". So S-M3-2 is the right code
  for 3.0 sheet and "after anodising" is right. Sheet H1-1 draws d4.2 at +0.10/-0.00 (4.20 to 4.30) against PEM's 4.22 to
  4.30, and anodising closes a hole further; the sheet's "unless the nut maker's installation data ask otherwise (tell us)"
  covers it, but the drawing should say 4.22 +0.08 after finish. File the bulletin under `v2/vendor/pem/` and replace
  INFERRED in the H1 README choice 1, the RFQ README line and the generator comment. (Optional: CLS, stainless, avoids
  zinc-plated steel in anodised aluminium; not needed for a test plate.)
- **m2. A welded K1 heater contact defeats all four thermostats for the rest of an unattended step** (disclosed at line
  173 as a residual). "Where possible" it can be removed: a second Finder 40.52 (K2) with its coil in parallel with K1's
  after the chain and its contact in series with K1 11-14; V4 then shows each contact opens. About EUR 9 at the list's
  reichelt prices (relay plus socket).
- **m3. No suppression across K1's coil**: the AC-rated thermostats and STOP/TEST break an inductive DC coil. A 1N4007 across
  A1-A2 (or Finder's coil module for the 95.05 socket) protects their contacts; not in the parts list.
- **m4. "the supply dips"** (TEST-PROCEDURE line 107, TEST-BRIEF line 84): the 40.52 drops out only at 0.1 UN (Finder 40
  series XI-2018, must drop-out voltage), so it is a supply loss, not a dip, that drops the latch. The fail-safe claim
  (off on loss, stays off on return) is correct; the word is not.
- **m5. V3 does not prove each thermostat as installed is in the chain**: a short across a pair inside the case passes V3.
  Add: with the link block open, open the chain at each thermostat in turn (lift one lead) and see K1 drop.
- **m6. Two fuses are both called F1** (parts table line 124, wiring lines 148 and 151), and the table puts the 7.5 A fuse
  "after K1" while wiring 1 puts it before K1. Name them F1 and F2 and use one position.
- **m7. The patch runs do not say how the HS100 gets onto H1's underside** (section 6 item 2): H1 has to come off its ten
  screws (with TS3 and the thermocouples on it and the leads under its edge) and go back; if the heaters stay on from a
  second supply, V3 should be repeated after the refit.
- **m8. TEST-BRIEF line 29 rounds the budget to "-2 to +4 %" and "-3 to +8 %"**; -3.2 rounded to -3 narrows the
  procedure's -3.2 to +7.5 %. Quote the procedure's figures or round outward.
- **m9. PACKAGE is not quite self-contained**: `MACHINING-RFQ.md` cites `READY-TO-ACT.md` (note 6) and
  `lid-tray-qmx-r2/README.md` (section 1), `CHECKOUT-LIST.md` cites `READY-TO-ACT.md` and `ASSEMBLY.md`; none is in
  `PACKAGE.sha256`. Add them or drop the references.
- **m10. Sheet H1-1 labels the underside relief's size but not its position** (X -110.9 to -66.9, Y -125.4 to -116.4,
  `panel1450.RELIEF_POCKET`); the DXF carries it. The README calls the sheet a "plan with every dimension" and the sheet
  governs; add the two coordinates.
- **m11. R2 quotes the rim-face value (382.58 x 268.28) for a reading taken 2 mm below the rim face**; on the draft of
  `CASE-MARGINS.md` section 2 (382.02 at Z 101.04 to 382.58 at Z 108.97) the nominal there is about 382.44 x 268.14. Inside the
  range either way; state the value at the reading's place.
- **m12. C1's request text still asks the shop "whether you insert the PEM hardware before or after anodising"** (pre-existing
  text); PEM says after. H1's line is right.
- **m13. `patch_rfq_od01b.py` and `patch_checkout_od01b.py` were edited in `fec1c564..b9b9b32a` after they had run** (the
  em-dash asserts rewritten as escapes). Harmless, but the committed script is not byte-for-byte the one that ran; say so in
  the log.

## What was verified, and how

1. **H1 definition.** Sheet H1-1 text extracted and a low-resolution render viewed (AI read-back): outline 377.2 x 263.0 x
   3.0 R16, rebate band outside 368.0 x 253.0 2.0 deep (1.0 left), relief 44.0 x 9.0 x 0.8 underside, ten d4.6 on the insert
   spans 358.14, 278.90, 242.32, 151.90, four d4.2 for PEM S-M3-2 on G 37.0 (X) by F 35.0 (Y) about (-45.0, 70.0), a nut
   section, material (EN AW-5754 H22/H32 or 6061-T6, 3.0 +-0.13), finish (Type II black, sealed, nuts after), positions
   +-0.10, holes +0.10/-0.00, flatness 0.5 reported, note 5 gating R1, R2, R3, R5, R6. Complete for a shop apart from m1 and
   m10. `python3 run.py test_h1_heat_test_plate`: 6 passed; `test_case_geometry`: 11 passed (this host, the scratch clone).
   The generator needs ezdxf and build123d, absent here, so its check was not re-run; its record reads PASS of 15 and its
   four input hashes equal the tree's (panel1450 `3bdb88df98260244`, generator `166d753f6354dd5a`, C1 DXF
   `19703fa5838f9e4a`, Arcol `ec17870c5a92d11e`). An independent group-code parse of both DXF files (no ezdxf): OUTLINE,
   REBATE_2MM_TOP and RELIEF_0.8MM_UNDERSIDE equal C1's point for point (40, 40 and 4 points, largest difference 0.0), the ten
   4.6 THROUGH circles equal C1's, PEM_S_M3 holds four 4.2 circles at X -63.5/-26.5, Y 52.5/87.5, INFO one text, nothing
   else. `sha256sum -c` of the folder's MANIFEST: 6 files OK. Arcol 12/14.08 page 2: HS100 A 47.5, B 88.0, F 35.0, G 37.0,
   K 3.7, L 4.4; G is across the width (HS50's G 21.4 is under its 28.0 width), so G along X with the long axis along Y is
   consistent. PEM data as m1.
2. **H2 and the RFQ.** H2's finish is one instruction in RFQ line H2, note 7, TEST-BRIEF line 21, TEST-PROCEDURE line 185 and
   CHECKOUT line 15 (paint); the only "anodised or painted" left is check-2's historical record. H1's finish agrees across the
   RFQ table, request text, note 1, sheet and README. The 24 upload hashes of RFQ section 2 are all in the package and equal
   the files.
3. **The case.** RFQ section 6 names drawing 1451-931 (title block read: "DATE 1.15.25", "1450 PROTECTOR"), D-08a (stated
   in `CASE-MARGINS.md` line 20), the 1450EU and the 1450PF, and states plainly that no Peli page ties the 1450EU to that
   drawing, with R1 and the 60-day return settling it. R1 to R8 each carry value, range, gauge and the parts gated; the
   figures match `CASE-MARGINS.md` section 2 (382.58 x 268.28; 101.04; 108.97; fillet tangents +-171.64 and +-114.49; ring
   9.39; outline 378.4 x 263.1; window 349.7 x 233.8; inserts +-0.38 per side, M8f; wall 5.34, 4.58 to 6.10) and
   `panel1450.FRAME_BOSSES`. Only B1 bears on "released without them".
4. **The shutdown.** Topology correct: STOP (NC) then START in parallel with K1 21-24, then TS1 to TS4 in series, then the
   coil; heaters through K1 11-14 (NO); a trip, STOP, a broken wire or a supply loss leaves the heaters off after reclosing
   until START. Finder 40 series XI-2018: 40.52 8 A, DC1 8 A at 30 V, coil 0.65 W (54 mA at 12 V), drop-out 0.1 UN.
   Honeywell 2455R: Table 1 bands (+-3 open for 60 C at a 15 K differential; +-4 to +-6 in 83 to 110 C; +-4 to +-7 in 111
   to 150 C), Table 2 0 to 150 C operating, Table 4 AC only. V1 bands (84 to 96, 57 to 63, 136 to 144) follow the seller's
   tolerances and reject rather than adjust. V1 to V4 are a real pre-heating verification, with m5. Unattended heating is
   allowed only behind V1 to V4, otherwise a person at the case reading every 10 minutes; patch runs always attended; the
   current limit is disclaimed. No unattended path without the shutdown was found. Placement: B2.
5. **The surrogate.** Budget reproduced: random terms by RSS 1.49 % (64 W) and 3.19 % (21 W); biases 1.1 + 1.0 and 3.3 + 1.0,
   both reading G high, giving -1.5 to +3.6 % and -3.2 to +7.5 %; 0.33 K = 50 min x 0.2 K per 30 min. D1's 29 % checks
   (205.75 x 140.09 against the plate). HS100 derating 85.7 W at 50 C, 80.0 W at 60 C, 45 W to 121 C correct. FEA-004's
   clause "the enclosure conductance measured" exists (`pcb_requirements.yaml` line 6257); `POWER-THERMAL.md` section 10
   names W4 T9 and the 2.3 x spread. The "May NOT close" column and the sentence "Its readings never close final thermal or
   sealing acceptance" are explicit; nothing claims either.
6. **The package.** `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` from the repository root: 66 files OK; 13.39 MB as
   stated. Prices recomputed: lines 10 to 14 are 10.50 + 22.26 + 19.58 + 4.12 + 3.91 = EUR 60.37 excl., 73.05 incl.; lines 1
   to 8 EUR 416.40 excl., 511.80 and 503.85 incl.; lines 1 to 14 EUR 476.77; shipping 6.95 + 20 / 0.85785 = 30.26, labelled a
   "from" price plus an exchange-rate ESTIMATE and not a delivered total. reichelt's 90 C page re-read: EUR 12.71 incl. 21 %,
   +-6 C. No personal data (the seller question carries "[owner's postcode]"; the only identifier is the seller's company VAT
   number). Every outward text is marked NOT SENT; no purchase, upload, account or contact is made or implied.

## Not done

The H1 generator and drawing were not re-run (no ezdxf or build123d on this host; no box by the brief). Only reichelt's
90 C page was re-read of the new price sources. The Arcol, Finder and Honeywell sheets were read from the tree's copies,
whose hashes equal their `sources.txt` lines.
