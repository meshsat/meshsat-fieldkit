# Integration set 26 (MESHSAT-1357, branch `fnd/int26`, 2 October 2026): U-03, the solar panel, a conditional downstream unit selection

Prototype design, desk arithmetic: nothing is bought, built or measured, and no physical unit is accepted. The integrating
session's records, from set 25 at `50a44371` (main since its promotion).

| Step | Commit | What it did |
|---|---|---|
| 1 | `9640ad22` | merge of `fnd/l4e9` at `9b5b28d6`, which carries `fnd/l4e13` at `fae419d1`: **L4-E13** accepted, and **L4-E9's update round 3** bringing the gate in line with it |
| 2 | `bf7d6ade` | merge of `fnd/l4e9` at `6e380477`, which carries `fnd/l4e13` at `33b6b7be`: L4-E13 re-read on set 25's L4-E7R, and L4-E9's round 4 re-pinning it |
| 3 | this commit | this record |

**What the steps contain:**
- **L4-E13, U-03** (finding O-1: a solar panel inside REQ-016's window). The decision follows the owner's three separate checks and REQ-016's own split ("Protection is judged apart from the window, under rule TRN-001"), so no irradiance maximum is a decision input.
  - **The window, normal operation:** A-1 is Vm20 + U_V at or under 25.000 V, measured directly at -20 C and 1000 W/m2 (the makers' rated quantity). The margin is 0.8495 V on a unit at the typical rows. The route 2 window is Voc25 from 20.315 to 22.156 V.
  - **The disturbance check:** against D4's 28 V standoff. By junction physics (n at most 2, 32 cells, kT/q at 253.15 K), a unit at A-1's ceiling reaches 28 V only at 8574 W/m2, 6.09 times the extraterrestrial irradiance. SunPower's own 1.25 on Voc (guide 524958 Rev F, section 3.0) gives 26.75 V, under 28 V.
  - **A-2, useful charging:** measured on the conservative side of SC-37's noon corner. The lower bound is 27.0849 W against 1.365591 W; the coordinator's independent diode fit agrees within 0.02 %.
  - **A-3, the entry, in three cases:**
    - (a) normal operation, 3.987 A, on L4-E7R's regulation (at most 2.9337 A) and backstop (trip at most 3.7408 A);
    - (b) a sustained input fault, 8.1817 A with the maker's 1.25;
    - (c) an irradiance transient during an existing fault, 13.82 A, a COMPONENT_LIMITATION on J_SOLAR and PV_IN at Layer 5/6.
  - **A-4:** the 100 W rests on L4-E7R's regulation and backstop (93.5521 W, CONDITIONAL on G_CM and the VIN+ bias).
  - **Route 1** (a maker's warranted band) closes nothing today. **Route 2** (one identified SunPower SPR-E-Flex-100 measured against PANEL-ACC) is feasible on a unit equal to the typical rows.
  - **U-03 is a CONDITIONAL DOWNSTREAM UNIT SELECTION.** The purchase and the measurement are the owner's actions; REQ-016 is unchanged, so no owner question is raised.
  - Under the accepted stage, the nominal hold's day is 336.6 Wh (L4-E7R), where the replay's first-round basis is 350.0 Wh.
- **L4-E9, rounds 3 and 4.** The gate is **NOT CLOSED**, on U-01 (the cell's signed specification), U-02 (T-H1 at or above 2.159 W/K and the fans) and U-04 (TI's N1 answer or the bench's VSYS). U-03 has left the "could overturn" category for the downstream register as PANEL-ACC (R-35). The register holds 139 items: R-148 is A-3(c), R-149 is M3's n check, and R-29 is J_SOLAR's lead at AWG 16, read on JST VH's catalogue. LH-02 is amended, and OW-6 (the panel unit's purchase and measurement) joins the owner's items.
- **The checks:**
  - L4-E13: the collaborator's focused check and its recheck were not accepted; the coordinator's checks 3 and 4 accepted it.
  - L4-E9: the coordinator's checks 5 and 6.
- **For the owner to send:** the SunPower and Solbian clarification drafts in `records/l4e13/clarification/`.

**What step 1 showed:** at `9640ad22`, `test_l4e13` refused (17 tests). L4-E13 had been authored on main `8aec3020`, before set 25 appended L4-E7R's section 10 to `l4e7_stage_settings.out`, and its pin of that file had gone stale. The rows it reads were unchanged in place, but its 100 W wording cited the superseded first-round statement, so step 2 re-read it on L4-E7R rather than only re-pinning.

**Gates on the runner, at step 2:** the registry 145 records and 59 rules, 0 errors and 0 warnings; every page current, and the render order run twice with no page moved; the dry run byte for byte; `verify_l3am` 19 of 19, `verify_acceptance` 18 of 18, `l3n01_mutation` PASS; the modules (the Layer 3 and Layer 4 set with `test_l4e13` and `test_l4e_svg_readers`) 359 passed, 0 failed, 0 skipped.

The box suite on the set's tip, in two passes (`box_suite2.sh`, `test_l4e10` and `test_l4e12` on CPython 3.11, MESHSAT-1480), is the promotion gate. The evidence archive is set 25's (L4-E13's held sheets are in it).
