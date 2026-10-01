accepted: no

# Layer 4, L4-E7: the focused check of the qualification of the 100 W bound by the engineering collaborator (an AI review, read-only)

Collaborator job `cx20-l4e7q-check`, run `20261001T171330Z-3616813`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e7 at commit `ee9909a88286`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E7Q: NOT YET. The numerical results reproduce. The qualification omits A7's test-condition extrapolation, and the TCR row incorrectly claims no effect on stability or protection. These need bounded documentation and predicate corrections. Read-only AI review; nothing changed.

## Blocking discrepancies

- B1: Missing bound condition and manufacturer question. L4E7-QUALIFICATION.md:50-51 treats A7's 0.94/1.06 mmho limits as covering the operating envelope. Held 8705af p.5 guarantees that row over temperature at 50 mV differential and CSPIN=5.025 V; the design uses common-mode voltages up to 25 V and approximately 57.5 mV at the reported limiting corner. No held guaranteed transfer-error or offset bound was found extending those limits across that range. The combined result tolerates only another 0.100779% loss of effective gain before reaching 100 W, equivalent to 0.939052673 mmho with other terms fixed. Explicitly condition this extrapolation, add its sensitivity, and ask AD for guaranteed transfer-error coverage over the actual voltage, temperature and switching conditions. Keep the existing calculated results conditional while that evidence is unresolved.
- B2: Incorrect no-effect classification. L4E7-QUALIFICATION.md:22 and l4e7_stage_settings.py:782-785 mark TCR as affecting neither stability nor protection. The sheet's p.31 equations give I_fault proportional to 1/RSENSE1; cancellation in I_fault/I_limit does not cancel the absolute trip-current change. Changing cold TCR from 50 to 100 ppm/K increases trip current by 0.226017% and changes sense-path loop gain by -0.225507%. These are small effects, not zero effects. The stated minimum ratio 1.55/1.229 also omits line and EA2 allowances: the combined regulation voltage is 1.253674623 V, giving 1.236365 instead of 1.261188. Correct the classification, distinguish unchanged comparator threshold from changed current threshold, and make the predicates check the corrected claims. Similarly qualify LINE's 'no gain' wording because VIN-dependent reference movement is a coupling path when the source voltage moves.

## Classification

- **OWNER_REQUIREMENT**: Solar window and operating ambient Evidence: pcb_requirements.yaml REQ-016, D-34 and REQ-024 retain the existing limits; this review proposes no requirement change.
- **MISSING_EVIDENCE**: A7 applicability outside its specified test point Evidence: 8705af p.5 specifies 50 mV differential and CSPIN=5.025 V; full-temperature coverage does not establish the omitted voltage-range accuracy.
- **IMPLEMENTATION_DEFECT**: TCR and protection/stability classification Evidence: The qualification confuses invariant fault-to-limit ratio with invariant absolute fault current and describes a nonzero loop-gain change as no effect.
- **MODELLING_ASSUMPTION**: Half gains, doubled coefficients and thermal estimates Evidence: The arithmetic reproduces, but the stated sensitivities and thermal extrapolations are not production guarantees.
- **COMPONENT_LIMITATION**: Unprinted gain, bias and cold-TCR limits Evidence: 8705af pp.4-5 gives typical-only amplifier gains and bias; HoJLR Ho-A0 p.4 specifies TCR testing only from +25 to +125 C.
- **MISSING_EVIDENCE**: Board behavior and production qualification Evidence: Manufacturer responses and bench rows remain outstanding; no prototype has been measured.

## Smallest next action

Add the A7 operating-range assumption, break-even and AD clarification question; correct the TCR stability/protection entries and fault ratio; update the corresponding predicates and range wording. No part substitution is required by this review.

## Closure criterion

The revised qualification explicitly carries every unsupported bound assumption, including A7 applicability; the AD draft requests the missing guaranteed coverage; classification and predicates reflect absolute trip-current and loop-gain dependence; matching-stack arithmetic reproduces 99.899220557 W and its 0.100779443 W margin. Manufacturer characterization alone cannot clear a production-guarantee condition. Physical qualification remains downstream.

## Owner decision required

no

## Checks

- Q1: datasheet identity: PASS. The held PDF hashes to 8f552a0b57677bfa7e4a5d5d0fac56d56fbbd1a6f65a9ee7aaaf8743cd534ec3, matching inputs/ia-8705af-20250322064938.json. All 44 pages carry 8705af; no revision table was found. The [official URL](https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf) also returns the 44-page 8705af document. The archive could not be retrieved independently during this review, so archive byte identity rests on the filed acquisition record and matching held hash.
- Q2: limits and classification: FAIL. No missed guaranteed EA2/EA3 gain, VC operating-range or FBIN-bias limit was found. IMON regulation is full-temperature at VC=1.2 V and default VIN=12 V; line regulation has no bullet and specifies not switching. EA2 affects the bound and stability; HOLD affects stability and energy without independently raising the settled current-limit bound; TJ correctly remains a condition. However, TCR changes loop gain and absolute fault current. Also, A7's full-temperature gain row specifies 50 mV differential and CSPIN=5.025 V, conditions absent from the qualification's claimed guaranteed operating-range coverage.
- Q3: independent power arithmetic: PASS. Recomputed stack A cold/hot: 96.247433497/96.229093908 W. EA2 alone: 97.142071320 W; LINE alone: 96.309372554 W; TCR alone: 96.464969133 W. Stack C cold: 99.673940430 W. Combined: 25*[1.229*(1+0.0001*13)+1.5/65]/[0.00094*0.015*0.99*0.9955*0.99*0.995*23200*0.999*0.998875*(1-0.005-0.05/23200)^2] = 99.899220557 W, margin 0.100779443 W. Half-gain and doubled coefficients are adverse sensitivities relative to printed figures, not established production bounds.
- Q4: voltage and temperature range: PASS. Minimum voltage-derivative brackets reproduce as 1.173206238 V for A and 1.159412477 V for C. Voltage monotonicity therefore holds throughout the stated interval under the model. Temperature is not globally monotonic because resistance envelopes contain |T-25|. The independent sweep from -20 to 62.1 C, including zero and maximum modeled shunt heating, retains cold maxima 96.247433497, 99.673940430 and 99.899220557 W for A, C and combined. This verifies the model, not the omitted A7 coverage or actual board temperatures.
- Q5: HoJLR versus WSL: PASS. WSL component TCR is +/-75 ppm/K from -55 to +155 C. Its solder and life allowances become 3.833333% and 4.333333% at 15 mOhm. Recomputed WSL A/C at 23.2k: 96.476313378/106.975971737 W. C remains 100.865033699 W at 24.6k and falls to 99.645442201 W at 24.9k. The latter gives 3.234270415 A and a 6.827309% setting reduction. Keeping HoJLR is supported as a conditional engineering choice under this selection rule.
- Q6: clarification drafts: FAIL. The existing EA2, VC, line-regulation and cold-TCR questions are relevant manufacturer questions. The AD draft does not request A7 transfer-error coverage over the actual common-mode and differential-voltage range. Production characterization can support qualification, but neither draft should allow characterization data alone to be treated automatically as a guaranteed production limit.
- Qualification predicates: PASS. Both Python files parse. The conditional-status truth table correctly handles the five supplied rows, including HOLD alone remaining unconditional. That verifies bookkeeping only: classification predicates check field presence/types, not the disputed physical claims, and the five-row set does not capture A7's omitted condition.
- Full test_l4e7 execution: NOT_RUN. The compute dependency r11_dep.py creates a temporary directory and PNG in fig8_readings. Full execution was not attempted under this job's no-write constraint. Independent calculations and the isolated status-function check above were performed instead.
- Revision and read-only integrity: PASS. HEAD matches the requested base and the worktree remains clean. No gate, verdict writer or generator was run.

## Evidence and minors

- REQ-016 and D-34 retain the 25 V, 17.6 V operating point and 100 W window. REQ-024 starts at -20 C ambient. Treating -40 C as information outside the permitted ambient range is correct.
- MINOR M1: L4E7-QUALIFICATION.md:71-77 does not fully justify pairing both resistor temperatures only at the cold and hot endpoints. Their individual worst temperature distances occur at different ends. A conservative independent-temperature combination gives 96.248120559 W for A and 99.674651953 W for C, still below 100 W. State the thermal coupling assumption and retain a dense check, or use the mixed-temperature envelope.
- MINOR M2: The 63.7897 W hold-floor calculation in l4e7_stage_settings.py omits resistor life and solder drifts while being compared with stack C. At 16.419845 V, the cold C and combined calculations give approximately 65.4102 and 65.5580 W. Correct the stack label or use matching stacks; HOLD's bound classification is unaffected.
- MINOR M3: The 105.430977 C junction estimate reproduces, but 8705af p.3's 4.2 mA quiescent maximum is specified at 25 C, not switching, EXTVCC=0. Along with board-dependent thermal resistance, this remains an extrapolation within the existing TJ condition. Call it an inferred estimate, not a demonstrated upper bound. Bench 7b.13 correctly reserves the CLKOUT method's 10 C uncertainty.
- MINOR M4: The 110.2 W irradiance-step figure uses an already-warmed 13.8 C cell temperature. The same stated panel model at a cold-soaked -20 C cell and 1000 W/m2 gives 122.695 W. Label 110.2 W as a scenario, and include the cold-soaked step in 7b.9t. Source steps, hold transitions and instability appropriately remain unverified bench obligations.
- MINOR M5: Tighten the clarification closure wording: lot characterization is supporting evidence, not automatically a production guarantee. Request a manufacturer-warranted limit and its applicability; otherwise retain CONDITIONAL. Milliohm's -40 to +25 C option covers the needed cold range without requesting operation below its -50 C rating.
