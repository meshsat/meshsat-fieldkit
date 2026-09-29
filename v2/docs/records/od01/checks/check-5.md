acceptable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). Its blocking item B1 and minor items p1 to p9 are answered by patch_od01e.py, which replaces the whole verification block rather than single lines (a change of method, LOG-od01b.md); p10's box paths are generalised in the log and patch_od01d.py stays as it ran. -->
# AI review: focused re-check of the OD-01 corrections, fnd/od01b at d0a8d0eb (MESHSAT-1357)

This is an AI review, not a qualified engineering review. The checker wrote none of the work under review. It ran on 29
September 2026 from 03:48 to about 04:00 CEST (read from `date`), in the read-only scratch clone with `fnd/od01b` fetched and
detached at `d0a8d0eb2cd0`. Scope: the single commit `a6420c37..d0a8d0eb` (`patch_od01d.py`, the filed check 4, the package
list, the log, and H1's README and manifest), read against its sources, and whether it or the corrections before it
introduced anything new. No box, no agent, no other model, no commit.

N1 and N2 are answered correctly, and so are the minor items (one wrong page citation). One new blocking defect is left.
It arrived with check 3's m2 correction (`e0cd5ec1`), and n9 widened it in this commit. It is a text edit and needs no
regeneration.

## Blocking

**B1. V4 now contradicts section 5.1, and its STOP/TEST press tests nothing.** `TEST-PROCEDURE.md` lines 179 to 181 say:
supply off, the four contact readings, then "Supply on: press STOP/TEST once, the heater current falls to zero. START."
After the supply has been cycled, both relays are already out, because the hold path is open. The heater current is zero
before the press, so the press proves nothing. Line 250 (section 5.1) still says "Changing the power: STOP/TEST, change
the link block outside the case, START (V4 is that STOP/TEST)", and the lid change reads the same way. That was true of V4
at `b9b9b32a`, when V4 was only the STOP/TEST press. Now it leaves out the four contact readings that the residual risk
(lines 183 to 187: "V4 reads each contact on its own before every step") relies on. An operator who follows 5.1 runs S2 to
S6 unattended, believing V4 was done, with no contact read.
Fix, line 179: "**V4, at the start of every step and after each lid change.** With the heaters on (the previous step's,
or before S1 after START), press STOP/TEST: the heater current falls to zero and stays zero on release. Switch the supply
off: a continuity check across each relay's contacts 11-14 and 21-24 reads open on all four (none has welded). Supply on,
START. Record the time." Line 250: "Changing the power: V4 (section 3), the link block changed while the supply is off.
Changing the lid: V4's STOP/TEST, open or close it, check the leads still lie flat on a straight run of the gasket, then
the rest of V4."

## Check 4's items

| Item | Answered? | What I read |
|---|---|---|
| N1 | yes | CHECKOUT-LIST lines 105 to 107: 416.40 + 68.40 = 484.80. Section 3: 198.66 + 69.42 + 23.32 + 125.00 = 416.40. Lines 10 to 14: 68.40 excl. and 82.76 incl., recomputed. README line 18 agrees. |
| N2 | yes | RFQ line 81: "4.22 +0.08/-0.00 holes (PEM bulletin CL)". This equals sheet H1-1 (the Holes block and the tolerance box), the DXF (four 4.22 circles, parsed) and PEM's metric S table (M3 x 0.5, shank code 2, minimum sheet 1.4, hole 4.22 +0.08). |
| n1 | yes | Procedure lines 111 and 158 to 159, checkout line 94: 108 mA. See p2. |
| n2 | yes | Brief lines 24, 53, 67 and 83 to 84 name K1, K2 and the diodes. |
| n3 | yes | V2 (lines 167 to 172) reads after K2. V3 (lines 173 to 176) disconnects a lead with the link block open and heats nothing inside the case. See B1, p4 and p5. |
| n4 | yes | Checkout lines 101 and 102: "(K1, K2)" and "(X1, X2)". |
| n5 | yes | H1 README lines 63 to 82: `e0cd5ec1`, "about 02:18 CEST", which equals the PDF's CreationDate of 02:18:37 CEST. The generator hash 9e949f9e1b9237a2 and the drawing script hash 8e0d56a6a030240f equal the files; the manifest header and the sheet say `e0cd5ec1`. |
| n6 | carried; acceptable | Generator line 151 formats with `%.1f`. Line 150 compares PEM_HOLE = 4.22 to 1e-6. The check record is not an upload (RFQ section 2 lists only the sheet, STEP and DXF). README lines 84 to 86 state this truthfully. |
| n7 | partly | README lines 47 to 49 are closed, but they cite "page CL-4" (p3). |
| n8 | yes | Groups A to L, each once. The header names L. 72 files. |
| n9 | yes | Arrangement lines 105 to 107, wiring item 2, V4 and the residual risk agree. See the circuit trace below. |
| n10 | yes | RFQ G row (line 30), section 3 (line 77), R1 and R8 (lines 170 and 177), procedure lines 82 to 83, brief line 17. |
| n11 | yes | Honeywell page 19, Figure 18, B203S: 31.19 overall along the tabs, 23.80 between the holes, 17.55 across. -99 - 15.595 = -114.6, which is 2.32 inside -116.92 (`panel1450.WINDOW` 233.83 / 2). The body at Y -107 to -91 is right (Figure 3: 16.0 diameter, 11.91 tall). |
| n12 | yes | Procedure lines 79 to 81. Section 6's last column names the same parts, row by row. |
| n13 | yes | Brief lines 16 to 18 name C3 as quote only. |

**Circuit trace.** Heater path: F1, K1 11-14, K2 11-14, the link block, the heaters. Coil path: F2, STOP (NC),
[START parallel to K1 21-24 plus K2 21-24 in series], TS1 to TS4, the two coils in parallel, a diode on each (cathode to
A1, reverse-biased).
- START energises both coils, and both 21-24 contacts close the hold path.
- With one 11-14 welded, the other opens.
- With one 21-24 welded, the other opens the hold path.
- An open thermostat, STOP, supply loss, or a broken wire in either path or in one coil lead drops both relays: an open
  coil leaves its relay's 21-24 open, so the other drops too.
- Every case stays off after the cause clears, until START.
- A shorted diode blows F2.
- In circuit, each of the four contact readings of V4 is isolated: the node between the two contacts connects only to
  them.

## Minor

- **p1.** Line 254 (section 5.2) reads "the amps after K1" while wiring item 3 reads "after K2". The current is the same
  in the series loop, so this is wording only.
- **p2.** Finder's DC coil table (40 series, 12 V, 9.012) gives 220 ohm and 55 mA, so 110 mA for two coils. "54 mA each"
  is 0.65 W / 12 V. F2 (1 A) is unaffected.
- **p3.** od01 `README.md` line 48 cites PEM "page CL-4". The metric S table with S-M3-2 is on PDF page 5, printed CL-5.
- **p4.** V3's disconnect is sound. A lead lifted at the thermostat's own terminal also exposes a short across that
  thermostat's leads. Unlike the heating version, though, it no longer shows that each installed thermostat still opens
  on heat after mounting (TS1 is bolted through its bracket). Neither version shows the chain intact after H1 is screwed
  on. The flat pair lies under the seal, and a short between its two conductors would bypass all four thermostats while
  V3's START/STOP/START and V4 still pass (INFERRED fault). Fix: in V3's second part, warm H1's top face over TS3 (X 0,
  Y -99) until the meter reads 0; it stays 0 after cooling until START.
- **p5.** Line 277 (section 6): "Refit H1 ... and repeat V3". V3's first part needs H1 lifted, so write "repeat V3, its
  first part before H1 is refitted".
- **p6.** Two gaps in the tests:
  - START stuck closed makes the latch reset by itself (the same class as n9), and V4 does not read S1. Add "S1 reads
    open" to V4.
  - No test shows the two 11-14 contacts (or the two 21-24) wired in series rather than in parallel: V2 passes either
    way, because K1 and K2 always move together. In V2, with K2's A1 lead off, hold START: K1 pulls in, the meter reads
    0, and K1 drops on release. Repeat with K1's A1 lead off.
- **p7.** TS3: the text fixes the bracket's tabs along X but not the terminals. In Figure 18's photograph the terminals
  run across the tabs (INFERRED), and they span about 32 mm (32.26 on the 3455RC; Figure 3's 2455R scales the same,
  INFERRED). Across the tabs they reach Y -115.1. Their crimped receptacles, about 12 mm below H1, then run under the ring
  toward the skirt's inner face at Y -125.42 (`frame_seat.py`). State "terminals along X too".
- **p8.** RFQ line 21 still says H1's manifest was "verified on 29 September 2026 at 01:53 CEST". It has been rewritten
  twice since (it verifies OK now). H1's `MANIFEST.sha256` header still says "Written ... by v2/cad/case_manifest.py",
  though `patch_od01d.py` rewrote its README line.
- **p9.** The K2 row (line 126) does not mention its 21-24 in the hold path. od01 `README.md` lines 22 to 24 do not list
  checks 3 and 4 or `patch_od01c.py` and `patch_od01d.py`.
- **p10.** Two strings sit outside the corrections themselves:
  - LOG lines 13 and 32 carry the box path `/root/od01b`. This is older text, not a changed line.
  - `patch_od01d.py` line 14 holds the two dash characters as literals in its detector, by design; `"\u2014", "\u2013"`
    would keep the file free of dashes.
  - No host name, user path or address appears in any added line.

## Verified

- HEAD is `d0a8d0eb2cd03864e878ef275c05539bfc5f9f58`. The diff has 13 files. I read the whole of section 3, the gate text
  of all four documents, the brief, and H1's README.
- Checksums:
  - `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` from the tree root: 72 of 72 OK. The byte counts in PACKAGE.md
    equal the files: 14,816,515 bytes, "14.8 MB".
  - H1's `MANIFEST.sha256`: 6 of 6 OK.
  - All 24 RFQ upload hashes, and the three printed-part hashes, equal the files.
- Gate set: identical across RFQ section 1, the last column of section 6, procedure section 2 item 1, brief section 1,
  H1's README (R1, R2, R3, R5, R6) and sheet H1-1 note 5 (the same five). G1 to G3 are behind R1 and R8 everywhere.
- Brief length: 107 lines, 1699 words (1645 at `a6420c37`). Pandoc and xelatex, 10 pt, 2 cm margins, A4: **2 pages**. It
  still reads as a brief.
- TS3 at X 0, Y -99 collides with nothing:
  - Nothing on H1's underside lies within 15.6 mm. The nearest hole is (0, -121.16), 4.26 beyond the bracket bound, and
    it lies outside the window.
  - The HS100 phantom spans Y 26 to 114 and the relief X -110.9 to -66.9.
  - The frame's skirt stands outboard (|Y| 125.42); the legs stand at |X| 175 to 180.
- `test_h1_heat_test_plate`: 6 passed, 0 failed. `test_case_geometry`: 11 passed, 0 failed. Both ran on this host, in the
  scratch clone, which was unchanged afterwards (`git status`: only the untracked check files).
- No em dash or en dash appears in any changed document, only as the detector literals in `patch_od01d.py`.
