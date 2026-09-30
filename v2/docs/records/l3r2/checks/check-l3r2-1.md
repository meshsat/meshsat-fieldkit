accepted: no

# CHECK-1: independent check of the Layer 3 handover L3-R2 (item C27), as prepared with the five owner decisions pending

MESHSAT-1357, 30 September 2026, about 01:40 CEST. **An AI check, not a qualified review.** The checker wrote none of
L3-R2. Branch `fnd/l3r2` at `9c26a641` (confirmed), four commits on `36bb1d12`, the merge base with `fnd/int16`. Integration
target `fnd/int16` at `845a4fd1` (confirmed; it carries S-122's closure). Plane grid `fnd/l3plane` at `7a0a9b73`.
While this check ran, `fnd/int16` moved to `4012429e` (one commit: set 15's integration check answered). Its only
registry change is three lines of S-125's title, which no L3-R2 script anchors on. The run below was not repeated on
`4012429e`.

Verdict for the handover as prepared: **not accepted.** Six blocking items follow. Most are small text or script fixes; B1
and B2 change what the owner is asked or shown. The owner's five questions are the right questions (each is needed to close
layer 3), F-01 is stated plainly, no row authorises a purchase, and the integration run is clean.

## What was run (throwaway shared clone, removed after this check)

* Shared clone of `fnd/int16` at `845a4fd1`; `int16-evidence-845a4fd1.tar` installed (tree clean after it); `fnd/l3plane`
  `7a0a9b73` merged (no conflict).
* The README's integrator commands, in order. The `( cd ... )` steps were run with the same working directory through
  `env -C` (no `cd`). One refusal, environmental: `apply_l3r2_session.py: REFUSED: branch fnd/e200c is not in this
  repository`. Cause: the script asserts that local refs `fnd/e200c`, `fnd/e200r`, `fnd/e200r2` exist (line 261); a shared
  clone carries them only as `origin/...`. With local refs made at the main repository's shas (`14c0c343`, `3fa7f4ff`,
  `e5e8a6ba`) every step ran:
  * `read_cfl006.out`: byte identical to the branch's; facts P1, E1, F1, C1 to C3 HOLD.
  * `apply_l3r2_session.py`: 16 entries, validator 0 errors; `apply_l3r2_sc76.py`: SC-76 added, 0 errors;
    `apply_layer_status_l3.py` and `apply_records_readme_row.py` written.
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings; `rules_render.py --requirements` written.
  * `render_l3r2.py` then `--check`: 3 pages, 0 out of date. On set 15 the render moves L3-C16 to CLOSED (CFL-016 PASS),
    drops S-122 from the open items and classifies S-126 (15 items with dispositions). No UNCLASSIFIED.
  * `dryrun.out`: byte identical to the branch's. `run.py test_requirements test_l3r2`: 75 passed, 0 failed.
* Conditional scripts on the integrated tree (a copy): the recommended chain (`od_l3_1 approve`, `od_l3_2 qmx-out`,
  `od_l3_3 2s2p`, `od_l3_4 adopt`, `od_l3_5 reading-c`) with placeholder `--words` and `--date 2026-10-01`: every script
  written, validator 147 records 0 errors, `rules_render.py` and `render_l3r2.py` written, `--check` 0 out of date. Then
  `run.py test_requirements test_l3r2`: **73 passed, 2 failed** (minor 2). A second chain with `od_l3_3 keep` (B1).
* `plane_grid.py` re-run: output byte identical to `plane_grid.out` (57 s, 22 MB).
* A probe of case V19 with U3's 6.0 A bracket and with U3B hour by hour (B2), in the session scratchpad, with the same
  imports and calls as `plane_grid.py`; its 6.1 A column reproduces `plane_grid.out`'s V19 figures. Nothing written to the
  tree.
* Text rules on everything the integration added (`git diff 845a4fd1` of the integrated state, l3plane included): 0 lines
  with U+2013 or U+2014; 0 lines with a host name, user path or `/tmp`. `v2/release/`, `CONOPS.md` and `PRODUCT-BRIEF.md`:
  no change on the branch, on the integrated state, or against `main`.

## Blocking items

### B1. Rows L3-OD1, L3-OD3 and L3-OD4 are not independent, and the prepared scripts let a combination through that leaves two contradictory owner rulings while the gate reads MET

* L3-OD1's question and the ruling `od_l3_1.py approve` writes fix "an array of 400 Wp at STC into a 200 W solar stage".
  L3-OD3 still offers `keep` (REQ-016's 100 W window, 1600 Wp) with `requires: L3-OD1:approve` only.
* Counter-example, run: `od_l3_1 approve`, `od_l3_2 qmx-out`, `od_l3_3 keep`, `od_l3_4 adopt`, `od_l3_5 reading-c`. The
  validator reads 0 errors. D-22 reads "an array of 400 Wp at STC into a 200 W solar stage"; D-24 reads "REQ-016's 100 W
  window is kept, and the kit's array grows to sixteen 100 W panels in parallel, 1600 Wp"; neither is reversed. REQ-072's
  acceptance then names "(1600 Wp at STC in parallel, D-24)" and the band "20 to 50 degrees of slope, facing between south
  and 15 degrees west of south", which `plane_grid.out` derived for 400 Wp in 2S2P into 200 W. REQ-016 keeps "F2 and
  J_SOLAR rated 10 A, above the 5.68 A the window's 100 W draws", against the keep option's own "fault current near 100 A".
  REQUIREMENTS-L3-R2.md section 2 then reads "Target unambiguous: MET" and "Contradictions and requirement-level TBDs
  closed: MET".
* Same class: `od_l3_4.py` requires only `L3-OD1:approve` and `L3-OD2:*`. With L3-OD3 answered `1s4p` it writes the 2S2P
  band; the grid ran only the 2S2P ratios.
* The keep path's 1600 Wp is ENERGY-RECONCILIATION.md 9i's figure for 4S18P. For the lids offered, the same section gives
  about 900 Wp (4S21P) and 1100 Wp (4S20P), "still not at +15 C". REQ-072 would therefore name an array sized for another
  pack.
* **Fix.** Take the array and the stage out of L3-OD1's question and ruling, so that L3-OD3 alone carries them. Or make
  `keep` supersede that clause of the L3-OD1 ruling and restate REQ-016's acceptance for the 1600 Wp array's fault
  current. Make `od_l3_4.py` require `L3-OD3:2s2p`, or carry a grid for each L3-OD3 answer. Have the gate's first condition
  check that the decided combination is one the evidence covers.

### B2. L3-OD4's recommended band rests on U3 at 6.1 A only, and F-01's credibility test is not applied to it

The band is 20 to 50 degrees, south to 15 degrees west, "at least 9.1 Wh". Stream l3plane's own conservative set takes
cases P, I and H together (I is U3 at the 6.0 A bracket). The recommendation takes V19 at 6.1 A alone.

Probe results, 4S15P (QMX out) at 19.08 V, adverse ratio C, lowest store in Wh:

| plane | V19, U3 6.1 A (= plane_grid.out) | V19, U3 6.0 A | V19, U3B hour by hour |
|---|---|---|---|
| 20/+0 | 9.1 | NOT MET | 9.4 |
| 20/+15 | 10.9 | NOT MET | 11.2 |
| 30/+0 | 34.0 | 13.4 | 34.5 |
| 30/+15 | 30.2 | 9.5 | 30.5 |
| 40/+0 | 40.1 | 19.5 | 40.6 |
| 40/+15 | 35.8 | 15.2 | 37.0 |
| 50/+0 | 33.1 | 12.5 | 33.6 |
| 50/+15 | 27.0 | 7.2 | 28.2 |

* With the bracket, the recommended band's 20 degree edge fails in the adverse case. What holds at the bus minimum is 30
  to 50 degrees, south to 15 W, least 7.2 Wh.
* The tablet-out lid (4S14P) at 19.08 V and 6.0 A meets the adverse case at none of the 24 planes probed (slopes 10 to 60,
  azimuths 15 E to 30 W), which include every plane where it meets at 6.1 A. F-01 is stronger than stated, and the L3-OD2
  recommendation is strengthened.
* The row does say "(the 6.0 A and hour by hour cases were run only at 20.7 V)", but not what follows from it.
* F-01 calls 9.4 and 5.2 Wh "margins the size of the model's own step error: not credible". The recommended band's 20
  degree edge carries 9.1 and 10.9 Wh at 6.1 A and fails at 6.0 A. Applying the same test to both lids would give the same
  answer for that edge, so the comparison shown to the owner is one-sided.
* The row's stated basis leaves out PLANES.md section 5's "The chargers' efficiencies exclude their inductors' core loss
  (s119), so they are high by it".
* **Fix.** Either recommend the band that holds with the bracket (30 to 50 degrees, south to 15 W on this probe, filed by
  the stream's own script), or state in SC-76 and in the row why the 6.0 A bracket is dropped and show the owner the 20
  degree edge at 6.0 A.

### B3. L3-R2 narrows M1 in a session closure, against the baselined CONOPS and the registry

* L3-C25 (whose SESSION, state CLOSED; `l3r2.yaml` line 388) and REQUIREMENTS-L3-R2.md section 4's "Mission M1's
  conditions, in one place" state "no M1 claim is made for a site, month or plane that gives less energy than the reference
  day". The section 4 text is hard-coded in `render_l3r2.py` line 417.
* CONOPS.md section 3 (baselined) says "September is the design month of that judgement, not a season M1 is limited to: M1
  keeps the setting this section gives it, with no season taken off it, and a month with less sun asks more of the panel".
* CONOPS.md line 1117 says "a season clause that the registry's first text carried would have narrowed M1 in a session
  choice alone, and is withdrawn".
* SC-37, printed in the same section 4 table, reads "M1 carries no season ... a month with less sun asks more of the
  panel". REQ-072's own notes in the registry repeat "M1 carries no season".
* This is a different operating condition presented as settled (the coordinator's item 2). D-20 and D-21 preserve M1's
  operating conditions.
* **Fix.** Remove the clause, or make it an explicit AWAITING proposal to the owner. L3-C25 can keep "a verification
  reference condition, not a restriction on where the kit is used" and SC-37's "a month with less sun asks more of the
  array".

### B4. SC-76 is framed as the author's choice and classed as a layer 3 requirement, while its 19.08 V is partly asserted and not established under load

This answers the coordinator's item 1.

* **Sourced from makers' pages or the netlist:**
  * VREF 0.788 to 0.812 V, SNVSAI1D 6.5 p.6, stated for -40 to 125 C;
  * IBIAS(FB) 25 nA, p.6;
  * R6 and R7 at 1 %, parsed from the netlist (s120 `vbus20_bound.out` sections 1 and 2).
* **Asserted:**
  * The temperature term. `vbus20_bound.py` line 91 reads "TCR_DRIFT = 100e-6 * 65 # INFERRED: 100 ppm/K over 65 K, the
    convention S-116 uses for the same class of part", and s120's README says "the codes carry no TCR".
  * The 65 K span has no source.
  * This asserted term alone moves the low end from 19.326 V (printed tolerances) to 19.080 V, the number every L3 claim
    uses.
* **Absent:**
  * any load or temperature measurement;
  * the loop's load regulation;
  * the drop from the regulated node to U3's input (R16, 10 mOhm, and copper).
  * Stream s120 was written to bound the bus's maximum against the 30 V FETs, not its minimum under load.
* **Applied selectively.** SC-76 says "every other limit that must hold a load at its minimum". The grid carries U3 at 6.1
  A, not its 6.0 A bracket (B2). U3 and U3B are at their carried 0.979 and 0.972, although their brackets reach 0.972 and
  0.963. Core loss is excluded.
* **Framing:**
  * P-22 carries status SESSION_CHOICE, which is outside the approved, rejected or awaiting that D-21 asks for.
  * L3-RECONCILIATION.md (c) classes "The charge bus voltage a requirement-level M1 claim rests on (19.08 V, the DC band
    minimum)" as REQUIREMENT (layer 3).
  * Section 4 and F-01 ("which the session takes as the basis of any requirement-level claim") state it as settled.
  * LAYER-STATUS lists it among "What the session closed".
  * Yet F-01, the reversal in L3-OD2 and the band in L3-OD4 all rest on it.
* **Fix.** Split SC-76 in two:
  * (a) the analysis rule: a requirement-level M1 claim uses the least power the design can deliver, every load-holding
    limit at its minimum. This is an engineering method.
  * (b) the bus band as an engineering INPUT, INFERRED, with its basis and what establishes it (the separate worker's range
    under load and temperature, then the bring-up measurement).
  * Show the L3-OD figures as conditional on (b). Do not class a design voltage as a layer 3 requirement.

### B5. REQ-054's restated acceptance changes the requirement

* The statement reads "14 dBm ERP generally, 27 dBm ERP on 869.4 to 869.65 MHz at 10 % duty".
* The new acceptance reads "give at most 14 dBm ERP on every configured channel and at most 27 dBm ERP at a duty cycle of
  at most 10 % on 869.4 to 869.65 MHz". Read as written, a channel configured inside 869.4 to 869.65 MHz must stay at or
  under 14 dBm, which removes the statement's 27 dBm allowance.
* L3-C21 and the history line ("with no limit added") say otherwise.
* **Fix.** "... on every configured channel outside 869.4 to 869.65 MHz ...".

### B6. The completion gate can read complete while the requirements contradict the baselined layer 1 and 2 documents

* `render_l3r2.py gate()` checks the four conditions only. L3-C26 (the CONOPS and PRODUCT-BRIEF passages the decisions
  change, re-issued through layers 1 and 2) and L3-C28 are not among them.
* On the recommended dry run, conditions 1 to 3 read MET. CONOPS would still say "a solar panel on the solar input", the
  one 4S3P pack and the QMX in the lid; the passage table lists the PRODUCT-BRIEF lines likewise. With this check's
  acceptance recorded, the page would read complete with L3-C26 OPEN.
* On the same dry run, section 3's static text (from `l3r2.yaml`) still reads "Approved today ... one 4S3P pack" and "Why it
  is not yet unambiguous", beside a gate that reads the target unambiguous.
* **Fix.** Include L3-C26 and L3-C28 in the third condition, or state that layer 3 completes only after the re-issue.
  Render the target text from the decided rows.

## The coordinator's added items

### Item 1: SC-76's basis

SC-76's basis is only partly established from makers' pages; the remainder is asserted. B4 has the detail.

### Item 2: requirement changes presented as accepted or settled

| Place | Text | How it is presented |
|---|---|---|
| REQUIREMENTS-L3-R2.md section 4, "Mission M1's conditions"; L3-RECONCILIATION.md L3-C25 | "no M1 claim is made for a site, month or plane that gives less energy" | **settled** (CLOSED, SESSION): B3 |
| L3-RECONCILIATION.md (c), P-22, section 4, F-01; LAYER-STATUS "What the session closed" | SC-76, 19.08 V as the basis of REQ-072's desk acceptance and of the deployment condition | **settled** (SESSION_CHOICE, classed REQUIREMENT): B4 |
| L3-RECONCILIATION.md (c) "Which approved lid function the kit keeps"; P-02 title; L3-C07 "which lid function leaves"; M-02's new title "which approved lid function leaves the lid"; L3-OD2's question | "leaves the lid" | pending, but it frames the QMX leaving the lid as HF leaving the kit: `od_l3_2 qmx-out` restates REQ-002 to "no HF bearer" and REQ-067 to "no HF transmitter", while `tablet-out` keeps the tablet's function outside the case. No option keeps HF outside the case; the row gives one clause of reason (the ruled connector plate). The option label and the recommendation do say "leaves the kit" |
| `od_l3_4.py` REQ-078 draft; P-20 | "With the lid open on its stay at 100 degrees ..."; the stay is NOT_A_REQUIREMENT_CHANGE | REQ-078 appears only as "(if decided)" and in L3-OD4's affected column, which is properly pending. The draft writes a session implementation (the 100 degree stay, SC-A1-08) into a requirement statement, and marks it `prototype_1: deferred` although L3-OD1 moves the lid pack into the core |
| The deployment band | "20 to 50 degrees ... south to 15 W", "at most 1 degree toward the hinge" | properly pending everywhere on the L3 pages (section 3 "(AWAITING)", L3-C08, section 4 "Pending (L3-OD4)"). LAYER-STATUS's F-01 paragraph gives the band as a model finding. Its support: B2 |
| REQ-011 narrowed to 8 inch under qmx-out | "an 8 inch tablet bracket" | pending, and shown in the recommendation and the impacts table |
| `records/a1solar/ARRAY.md` section 5 (a record, not an L3 page) | "Under Option A(i) the 100 W becomes 200 W in every arrangement (the owner's instruction)" | reads as the owner's. The owner's filed words (EXECUTION-PLAN.md line 506) are "move to engineering Option A(i), within existing authorizations", with "No purchases or requirement changes are authorized". L3-R2's P-03 correctly reads AWAITING |

### Item 3: "adverse"

The word appears in these L3 places:

* REQUIREMENTS-L3-R2.md lines 35 and 37;
* L3-RECONCILIATION.md lines 14, 16 and 20;
* OWNER-DECISIONS-L3.md line 10 (twice);
* the source `l3r2.yaml`, lines 74, 77, 95 and 310 (twice).

The registry text that L3-R2 adds does not use it.

* **No L3 page defines it.** The definition is in `records/a1solar/energy_runs.py` lines 17 to 20 and ARRAY.md section 7:
  * the worst of three panel fits, at the worse end of the set-point window (the FBIN range and 1 % resistors);
  * cells 10 K hotter than the NOCT model;
  * a 10 m lead;
  * the hotter cells' own loss.
* It is a component and installation worst case on the same September mean-day irradiance (PLANES.md section 1: each plane
  "on its own PVGIS DRcalc September mean day ... with that plane's own ratios B (typical) and C (adverse)").
* **No text says weather,** but none says "same day" next to the word either. The only hints are "MODELED on SC-37's
  September mean day" (F-01) and "one day" (L3-OD4's basis). "The adverse case" beside "typical" reads naturally as adverse
  weather.
* No run of cloudy days is modelled (PLANES.md section 5); the L3 pages say so only through "one day".
* **Recommendation.** Define the term once on each page, for example "the worst component and installation case on the
  same mean day".

### Item 4: where each displaced item goes, and whether its function stays in the kit

* **L3-OD1.** The pack moves from the east pocket into both base pockets. The row does not say what the west block
  displaces: a1mech README item 6 and section 6 record that "The west RF jumpers fail as assumed" (five of seven cables fall
  onto the block; the west RF entry is to be re-planned before the block is taken, OPEN). The row's cost list also does not
  say that approval forces one approved lid function out (that is left to L3-OD2).
* **L3-OD2, tablet out.** The tablet is "carried outside the case", and its function stays through the kit's WiFi and the
  USB-C outlet. REQ-017's USB-C outlet is `deferred` from prototype 1; the row does not say so.
* **L3-OD2, QMX out.** The row states that HF leaves the kit and why HF cannot stay outside the case. It does not say where
  the QMX set physically goes (it is simply not carried), and it offers no option that keeps HF outside the case.
* **L3-OD3.** No lid item is displaced. Where the four 1219 x 549 mm panels and the stand are stowed (outside the Peli
  1450) is not stated.
* **L3-OD4 and L3-OD5.** Nothing is displaced.

## Minors

1. **Run order precondition.** The README's run order does not state that `fnd/e200c`, `fnd/e200r` and `fnd/e200r2` must
   exist as local refs (the refusal above).
2. **test_l3r2 goes red after an answer.** On the decided state, `t_l3r2_the_recommended_answers_apply_in_order_on_a_copy`
   and `t_l3r2_the_other_answers_apply_on_a_copy` fail ("L3-OD1 is already decided"). The answer procedure does not retire
   or adapt them, so the suite goes red once a row is applied. Fix before the answers.
3. **Stale LAYER-STATUS text.** The status text written by `apply_layer_status_l3.py` says "CFL-016, closing with S-122 on
   integration set 15". On set 15, S-122 is closed and CFL-016 reads PASS.
4. **D-21's ruling text.** It drops the operative "do not make them prerequisites for completing the requirements
   document". Its title, "layer 3 finished for the current target configuration", reads as a completion claim; "finish
   layer 3 ..." would not. Within the filed partial quote, the three "in his words" sentences are faithful. The owner's
   full text is not in the tree, so fidelity was checked only against the filed quote and the coordinator's brief.
5. **L3-OD1's trade-off omits:**
   * the forced removal of one lid function;
   * the west RF re-plan (item 4);
   * each pack's size against the 160 Wh passenger figure that ENERGY-RECONCILIATION.md 8d names (289.4 Wh for the base
     pack; 723.6 Wh for a 4S15P lid pack by the same arithmetic);
   * that the second pack joins prototype 1's core (given only in the affected column).
6. **Changes `od_l3_1 approve` makes that the row does not name:**
   * It tightens REQ-072's pass line from "ends the 72 hours above the graceful shutdown threshold" to "serves the load at
     every hour of the 72 without the kit reaching its graceful shutdown". That is consistent with the statement, but a
     change.
   * REQ-014 gains a "base pack alone" runtime, while the ruling says "for each pack and for both together".
7. **"Keep both" is understated.** L3-OD2 says keeping both "does not meet M1 on the model at 400 Wp". The records say it
   is NOT MET at 400, 650 and 1000 Wp at the lid's 13.23 C basis, and meets only with the lid at +20 C and 650 Wp or more
   (a1mech README item 1).
8. **Figure mixing.** L3-OD1 quotes "85.8 and 116.9 Wh adverse" (case H) beside the carried typical figures. L3-OD2
   rounds 11.7 N up to "a 12 N push". L3-C14's "the lid adds about 3.5 kg" is arrangement B's pack; the recommended lid
   is 4.83 to 5.48 kg against about 1.4 kg (a1mech section 5).
9. **Older evidence without SC-76's qualification.** REQ-072's newest evidence entry (s119) still reads "Option A(i) ...
   meets M1 on the model with the tablet-out lid at 93.7 Wh typical and 85.5 Wh adverse". S-114's new closing evidence says
   "the architecture that meets the reference day on the model is two packs with a 200 W solar stage". Both are 20.7 V
   results; a note keeps a reader of REQUIREMENTS-TRACE.md from the opposite of F-01.
10. **TBD search patterns miss two cases.** REQ-045's acceptance carries a state sentence, "no coordination study exists
    yet". REQ-024's statement carries "the bound above about 3.6 W/K is open" and "open until the heat-balance test". Both
    look downstream (layer 4) and are classifiable. My own search for TBD, TBC, "to be", "owed" and "not yet stated" in
    statements and acceptances found only the author's classified mentions, plus two harmless uses of "to be" (CFL-004,
    REQ-063).
11. **Q1 to Q4 are not mapped.** The EXECUTION-PLAN's owner table (Q1 to Q4; Q1 recommended the tablet out) is not
    mapped to L3-OD1 to L3-OD4 on the L3 pages.
12. **REQ-078 draft.** It covers slope only. It does not cover the operator push the records find (6.1 N normal to the
    tablet at its far edge tips the C arrangement; a1mech section 5 "Operator loads").
13. **No floor under the graceful shutdown line.** REQ-072's pass line depends on the graceful shutdown line, which (c)
    classes as implementation with no requirement-level floor. A lower line (the rejected 2.80 V) would ease REQ-072.
14. **Smaller points.**
    * REQ-057 and REQ-068 add "or logged" to the statement's "falsely triggers", a slight extension.
    * The gate hard-codes CFL-006 as an exception.

## What holds

* **Branch, base and scope.** The branch, its base and its four commits are as stated. H3, CONOPS.md and PRODUCT-BRIEF.md
  are untouched. `h3_registry_digest.json` equals the released registry (its test passes). The added text carries no dash
  characters, hosts or paths.
* **Recomputed figures:**
  * base 4S6P;
  * lids 4S14P and 4S15P (RECONCILE.md, TOPOLOGY.md);
  * 21 x 3.35 Ah x 14.4 V = 1013.0 Wh and 964.8 Wh;
  * one 4S3P gives 9.11 W (energy_architecture.out section 6);
  * the lowest stores at 19.08 V: 95.9/40.1 Wh (4S15P) and 65.1/9.4 Wh (4S14P) at 40/0;
  * the tablet-out points above the 4.2 Wh floor are only 40/0 (9.4 Wh) and 40/+15 (5.2 Wh);
  * the QMX-out V19 rectangle is 20 to 50 degrees, south to 15 W, least 9.1 Wh; within 15 degrees of south, 30 to 40
    degrees, least 5.6 Wh;
  * flat: neither lid meets;
  * tilt: C 1.2 degrees interim, 7.0 at the edge, 6.1 N; B 3.6 and 9.5 degrees, 11.7 N (a1mech section 5);
  * REQ-016's 2S2P and 1S4P figures as in ARRAY.md section 5 (the scripts assert each one).
* **F-01** is stated plainly on all three pages and in LAYER-STATUS, and is true on the grid (stronger with the bracket,
  B2).
* **Each question is needed.**
  * L3-OD1: D-06 against REQ-072.
  * L3-OD2: an approved function changes (D-21).
  * L3-OD3: REQ-016 against REQ-072.
  * L3-OD4: M1's operating conditions (D-20).
  * L3-OD5: CFL-017.
* **No purchase is authorised.** The L3-OD1 ruling says "It authorises no purchase". The L3-OD5 `cells` option "asks for
  money".
* **Proposal statuses** follow the rule. APPROVED rests only on D-19, D-20 and D-21. REJECTED rests on D-20's and D-21's
  filed words; P-09 says honestly that the 29 September words are not filed. I found no requirement-changing proposal
  missing from the table apart from L3-R2's own B3 and B4. The streams since H3 (s117, s119, s120, s122, csi, w5si2,
  w5identc, d6rel, od01, energy, a1*) and the EXECUTION-PLAN's Q1 to Q4 map onto P-01 to P-22.
* **Session closures:**
  * S-114: its commit `1b9f543c` is an ancestor of `fnd/int16`, and its condition (study filed, REQ-072 re-read) holds.
  * M-02 and S-53 are restated accurately.
  * CFL-006's four facts hold.
  * CFL-002 is corrected.
  * All 86 open items are classified, and the 15 in no waits_on carry dispositions.
  * 144 of 144 records carry a method and a phase.
* **No planned test is shown passed.** Readings are PASS, FAIL or INCONCLUSIVE at SCHEMATIC, PLACED_BOARD or DESK_REVIEW only.
* **The consolidated specification** is generated from the registry. `--check` refuses a hand edit (its test passes).
  Records carry sources, applicability, acceptance, method, phase, allocation, rules, TEST-PLAN places, pending decisions
  inline, a change record since H3 and impacts by layer. Thirty-nine records whose final phase is PROTOTYPE have no
  TEST-PLAN row; the page says so, and REQ-072's own acceptance states its prototype run.

## What the delta check after the owner's answers must cover

1. The fixes for B1 to B6 and minor 2, on the tree that carries them.
2. Each new ruling: the owner's words verbatim (with the dash-to-comma note if one applies), the date, and `decides`; and a
   coherent row combination (B1).
3. REQ-072's deployment band and array are the ones the evidence covers for the answers given, on the adopted bus basis,
   with the 6.0 A bracket taken or its exclusion stated (B2, B4).
4. The registry validates, both renders pass `--check`, and `test_requirements` and `test_l3r2` are green on the decided
   state.
5. `l3r2.yaml`'s target text is restated to the decided target. L3-C26 is closed (CONOPS and PRODUCT-BRIEF re-issued) or
   the gate holds (B6).
6. `independent_check` in `l3r2.yaml` names this file by sha and verdict. H3, CONOPS and PRODUCT-BRIEF are unchanged
   except through their own re-issue. No dash characters.
