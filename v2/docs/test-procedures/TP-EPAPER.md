# TP-EPAPER: the e-paper's unpowered storage soak at +70 C at the glass (R-185)

<!-- tp
id: TP-EPAPER
title: The e-paper's unpowered storage soak at +70 C at the glass (R-185)
register: R-185
e11: none
route5d: The e-paper's storage soak (R-185)
-->

**Status: PROPOSED, for the supplier to review and agree before execution.** MESHSAT-1357, 3 October 2026. Prototype design:
nothing here has been built, bought, powered or measured. Common rules: `v2/docs/test-procedures/README.md`.

## 1. Purpose and the decision it settles

The kit's front-panel e-paper (Pervasive Displays E2370KS0C1, 3.7 inch, wide temperature) is unpowered in two of the required
thermal modes, E3-O at +55 C and E5's +60 C dwell, and its maker publishes an operating range only. The record's classification:

<!-- q src="v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md" -->
> **MISSING STORAGE QUALIFICATION: (2) E3-O at +55 C (M6) and (3) E5's +60 C dwell (M7).** The unpowered e-paper is judged on its
> +60 C operating row read to cover it (INFERRED); no storage row is held, so the shortfall is against an inferred limit, not a
> demonstrated one. At E3-O it lies over the route's modelled capacity; at E5 the ambient equals that row, so no modelled capacity
> and no plate fraction carries it.
<!-- /q -->

What a storage range at or over +70 C would change (L4-E12 17.9, the option of PDi's statement; a passing soak serves the same
lines for the tested lot):

<!-- q src="v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md" row="PDi's storage statement" col="Effect" -->
> with a range at or over +70 C M6's line becomes the +70 C class, 1.806 W/K, class (i), and M7's the LimeSDR's +70 C storage row,
> 2.159 W/K, class (i) at the optimistic ends
<!-- /q -->

This procedure is the storage soak the record specifies as the bench alternative to PDi's statement. It settles **U-02's MISSING
STORAGE QUALIFICATION (M6, M7)** for the lot tested (register row R-185); it blocks M6's and M7's lines and nothing of the boards.

## 2. The specimen and what transfers

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The e-paper's storage soak (R-185)" col="Specimen" -->
> one PDi E2370KS0C1 sample held unpowered at the CLAIMED maximum local part temperature, +70 C at its glass (the proposed
> replacement storage line), the chamber's setpoint raised by its and the glass thermocouple's stated uncertainty so the glass
> never sits under +70 C, for E5's 6 h dwell and E3-O's 4 h (each soak separately), mounted behind the window in a 3 mm plate
> section as in the kit (the T-H1 mock-up's blank serves); its function read back after recovery to +25 C at 1 h and at 24 h (an
> image written, refreshed and read against the pre-soak image: no missing or stuck segment, no new ghosting); an ambient-only +55
> or +60 C soak establishes nothing above the ambient (the recheck)
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The e-paper's storage soak (R-185)" col="What transfers to the final board" -->
> to the kit as evidence for that lot only; PDi's storage statement governs once filed
<!-- /q -->

The record's own definition of the soak (L4-E12 17.9):

<!-- q src="v2/docs/records/l4e12/L4E12-ELECTRONICS-THERMAL.md" -->
> a storage soak of a sample at the CLAIMED maximum local part temperature, +70 C at its glass (the proposed replacement storage
> line; an ambient-only +55 or +60 C soak establishes nothing above the ambient), the setpoint raised by the chamber's and the
> glass thermocouple's stated uncertainty so the glass never sits under +70 C, for the required durations (E5's 6 h dwell and
> E3-O's 4 h, each soak separately), the sample unpowered behind the window in a 3 mm plate section as in the kit, its function
> read back after recovery to +25 C at 1 h and at 24 h (an image written, refreshed and read against the pre-soak image: no
> missing or stuck segment, no new ghosting), with the glass temperature trace, its uncertainty and the durations filed
<!-- /q -->

**Consequences for this procedure.** The result is evidence for the tested lot only; PDi's storage statement, once filed, governs
instead. The soak is set on the glass, not on the chamber air: an ambient-only soak at +55 or +60 C establishes nothing above the
ambient. L4-E11's 17d has no block for this row.

## 3. Safety

- **Chamber at +70 C and above:** burns; the plate section is aluminium and holds heat.
- **The panel:** glass; handled by its edges, never flexed; the flexible cable never bent at its root.
- **Humidity:** the soak and the recovery are non-condensing (PDi's question in the drafted request asks about exactly this); the
  chamber cools closed so no condensation forms on the cold glass.
- Low voltage only (the panel's driver, at +25 C, outside the soak).

## 4. Equipment, and the accuracy each measurement needs

| Item | Class | Accuracy and capability needed |
|---|---|---|
| Climatic chamber | a temperature chamber reaching at least +75 C (proposal), with humidity logging | its uncertainty at the sample's place stated (it raises the setpoint, so a smaller one over-tests less) |
| Glass thermocouple | fine-gauge type T or K, bonded to the glass's inactive border with a thin conductive adhesive (proposal) | expanded uncertainty at most 1 K (proposal); calibrated at +70 C against a reference |
| Data logger | a thermocouple logger | the glass, the plate section and the chamber air, sampled at least once a minute (proposal) |
| Display host | the panel driven over its interface by board C's drafted connection or PDi's evaluation kit, at +25 C only | the same image file written before and after |
| Image capture | a camera on a copy stand with fixed lighting and fixed settings | the pre-soak and post-soak images comparable pixel for pixel (proposal: the same exposure, white balance and geometry, recorded) |
| Plate section | a 3 mm aluminium plate section with the window cut (the T-H1 mock-up's blank serves) | the window, the lens and the tape as the kit's drawing has them, recorded |

## 5. Setup and measurement points

1. **The sample** mounted behind the window in the plate section, its glass to the window, as in the kit.
2. **Thermocouples:** one on the glass (the controlling reading), one on the plate section beside the window, one in the chamber air
   (information).
3. **Unpowered:** the panel's flexible cable disconnected from any host during the soak (recorded).

## 6. Steps

1. **Identity:** the sample's part number, lot and date code.
2. **Pre-soak function at +25 C:** write the test image (proposal: solid black and solid white areas, checkerboards at 1 and 8 pixel
   pitch, and text), refresh it, photograph it; this is the pre-soak image. Then write the inverse image and back, photographing each
   (the ghosting reference).
3. **The setpoint:** +70 C plus the chamber's and the glass thermocouple's stated uncertainties, so the glass never sits under +70 C;
   record the setpoint and its derivation. The glass is not driven above that setpoint plus the chamber's stability (proposal: so the
   part is not over-tested; a soak whose glass trace exceeds it is INCONCLUSIVE if the part then fails).
4. **Soak 1, E3-O's 4 h:** heat until the glass reaches +70 C plus its U; hold for 4 h counted from that moment; cool in the closed
   chamber to +25 C (proposal: at most 1 K per minute).
5. **Recovery reads after soak 1:** at 1 h and at 24 h after reaching +25 C: write the pre-soak image, refresh, photograph; then the
   inverse and back. Compare with the pre-soak photographs.
6. **Soak 2, E5's 6 h:** as step 4 with 6 h (TEST-PLAN E5's dwell, 60 C from 0200 to 0800 of Table 507.6-IX, L4-E12 13.1). The two soaks
   run separately, each with its own recovery, on the same sample (5d's specimen is one sample); a failure in soak 2 is a failure of
   the sequence and does not separate the two durations (a second sample would; proposal).
7. **Recovery reads after soak 2:** as step 5.

## 7. Data to record

| Soak | Setpoint (C) | Glass, least during the duration (C) and U | Glass, greatest (C) | Duration at or over +70 C plus U (h) | Humidity, greatest (%RH) | Recovery time to +25 C (min) |
|---|---|---|---|---|---|---|
| 1 (E3-O, 4 h) | | | | | | |
| 2 (E5, 6 h) | | | | | | |

| Read | Missing segment or pixel (yes / no, where) | Stuck segment or pixel (yes / no, where) | New ghosting (yes / no, description) | Photographs (file names) |
|---|---|---|---|---|
| pre-soak | | | | |
| soak 1, 1 h | | | | |
| soak 1, 24 h | | | | |
| soak 2, 1 h | | | | |
| soak 2, 24 h | | | | |

## 8. Pass, fail and inconclusive

The register's acceptance, quoted:

<!-- q src="v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md" row="R-185" col="Acceptance" -->
> The sample's function unchanged after each soak at or over +70 C at the glass for the full duration, the glass temperature trace
> with its uncertainty and the durations filed as evidence for that lot only, never as a maker's range; PDi's storage statement
> (OW-4), once filed, governs instead; a failed soak bounds the part's storage limit below +70 C: M6 or M7 then stays a MISSING
> STORAGE QUALIFICATION against that bound (the part's measured local temperature at the window, R-104, against it), and becomes a
> DEMONSTRATED CONFLICT (OW-10) only when every admitted arrangement has failed with the part over that limit, or a bound shows
> none can meet it
<!-- /q -->

- **Validity of a soak:** the glass reading less its U is at or over +70 C for the whole duration (4 h, then 6 h); otherwise the soak
  is INCONCLUSIVE and repeated.
- **PASS** for a soak when, at both recovery reads, the image written, refreshed and read against the pre-soak image shows no missing
  or stuck segment and no new ghosting.
- **FAIL** when either read shows a missing or stuck segment or new ghosting. "No new ghosting" has no stated measure: TBD (owed by
  R-185): the comparison that decides new ghosting (a visual judgement under the fixed capture, or an optical-density difference with a
  threshold); until it is stated, two reviewers judge the photographs independently and both judgements are filed (proposal).
- **INCONCLUSIVE:** the glass below +70 C less its U at any time in the duration; condensation seen on the glass; the panel powered
  during the soak; the glass far above the setpoint before a failure (step 3).

## 9. The uncertainty budget

| Term | Source | Value |
|---|---|---|
| Glass thermocouple | its calibration at +70 C | at most 1 K expanded (proposal) |
| Chamber at the sample | the chamber's stated uniformity and stability | stated; added to the setpoint |
| The bond between the thermocouple and the glass | the adhesive's thickness | included in the thermocouple's calibration on a glass coupon (proposal) |
| Durations | the logger's clock | 1 minute (proposal) |
| Image comparison | the fixed capture | the camera settings and lighting recorded; no numerical term until the ghosting measure is stated |

## 10. Consequence of a fail, and the re-test triggers

- **A failed soak** bounds the part's storage limit below +70 C: M6 or M7 stays a MISSING STORAGE QUALIFICATION against that bound
  and becomes a DEMONSTRATED CONFLICT only by the corrected rule (R-185, quoted in section 8; L4-E12 17.9).
- **PDi's statement** (the drafted request, OW-4) governs once filed:

<!-- q src="v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt" -->
> 1. The storage (non-operating) temperature range of the E2370KS0C1, and any limit on its duration or on humidity. 2. Whether a
> module that is not driven (no image update) may sit at up to +70 C for 4 hours, and at up to +70 C for about 6 hours a day on 10
> consecutive days, at a non-condensing humidity, and then work to specification once back inside -15 to +60 C.
<!-- /q -->

- **Re-test triggers** (proposal): another lot; a change of the window, the lens or the tape in front of the glass; a measured local
  temperature at the window (T-H1, R-104) above the tested +70 C; a required duration longer than the tested 4 h and 6 h.

## 11. Authorisation and purchases (nothing has been bought)

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The e-paper's storage soak (R-185)" col="Authorisation" -->
> the owner's: the sample; PDi's request
<!-- /q -->

<!-- q src="v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md" row="The e-paper's storage soak (R-185)" col="What to buy" -->
> price not read: E2370KS0C1, Pervasive Displays, one sample; a chamber to at least +70 C with a thermocouple on the glass; a 3 mm
> plate section with the window cut (the T-H1 mock-up's blank serves)
<!-- /q -->

What to send (5d): `v2/docs/records/l4e12/clarification/pervasive-displays-e2370ks0c1.txt` (OW-4; the owner sends it).
