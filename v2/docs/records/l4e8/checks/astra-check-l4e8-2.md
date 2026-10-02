accepted: no

# Layer 4, L4-E8: the targeted recheck of the author's fixes by the engineering collaborator (an AI review, read-only; the second and last run on this issue)

Collaborator job `cx23-l4e8-recheck`, run `20261001T192113Z-3817800`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e8 at commit `cc95fe1f34b9`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E8: NOT YET. Read-only AI review completed. The reported 2.710 A corner, corrected frequency band, resistor dissipation and loop margins reproduce. B4 is correctly conditional. No failing ballasted corner was found, but the search does not establish the claimed fully independent bank bound, and the cold-loop closure criterion is insufficient.

## Blocking discrepancies

- R1/R2, incomplete whole-domain bound: ripple_dense.py:519-525 uses one target admittance plus five identical sibling admittances. The split check at :1523-1535 considers only two sibling groups at selected corners, with the target and other passives fixed, and uses RSS without coherent cross terms. Furthermore, full() at :1456-1462 evaluates the higher-order bound only at the RSS-winning passive set; this does not bound RSS plus the tail at other sets. The 120-harmonic check at :1506-1508 doubles only the RSS calculation. Consequently the claims 'every can independent' and 'every source combination and coincidence' exceed the evidence. Establish a conservative reduction that bounds arbitrary sibling impedances, or search independent branches with the coherent and higher-order objectives included.
- R4, insufficient cold-loop closure criterion: L4E8-BANK.md:258-259 allows the loop obligation to close from one can measured at the coldest temperature the bench reaches toward -20 C. That does not establish the entire bank's ESR envelope at -20 C over component variation and life. Keep the obligation open until a supported service envelope is at or below the modeled 80 mOhm threshold, or compensation is checked across the retained cold envelope. A warmer, fresh single-can measurement may inform the investigation but cannot close it.

## Classification

- **MISSING_EVIDENCE**: Whole-bank ripple bound Evidence: The verified 2.710191 A corner passes, but identical siblings, limited RSS split checks and a tail bound evaluated at one passive set do not establish the claimed full-domain maximum.
- **MODELLING_ASSUMPTION**: Thermal coincidence and component envelopes Evidence: The 1 s thermal constant, inferred ESL bands, cold-limit interpolation and 100 C ballast-temperature ceiling are not maker-guaranteed service bounds.
- **IMPLEMENTATION_DEFECT**: Cold-loop closure rule Evidence: Bench 7b.8 item 2 permits closure using evidence that does not cover the modeled temperature, population or life envelope.
- **MISSING_EVIDENCE**: Lifetime and cold-loop physical evidence Evidence: Can temperature rise and service ESR remain unmeasured; the record correctly retains conditional lifetime and an open loop finding.
- **DESIGN_OBJECTIVE**: Ballast energy accounting Evidence: REQ-072 requires honest endurance accounting; computed ballast loss varies with operating point and belongs in the active-front-end energy balance.
- **IMPLEMENTATION_DEFECT**: Initial-only transient figures Evidence: The unchanged 1.67 to 2.61 mF range does not include the newly adopted endurance capacitance extremes.

## Smallest next action

Retain 38 mOhm as the candidate. Add a conservative independent-sibling bound, including coherent harmonics and higher-order tails across the passive domain. Replace the single-can cold-loop closure rule with an explicit temperature, variation and life envelope; retain physical verification as an assigned open obligation.

## Closure criterion

Demonstrate every can at or below 2.7745 A for R11 8 mOhm and 2.7709 A for R11 7 mOhm over the stated independent parameter ranges, including coincident harmonics and bounded omitted orders. Update tests to exercise that coverage. Cold-loop closure must require a supported ESR envelope at -20 C over service life, or modeled and subsequently measured compensation margins across the retained envelope. Correct the energy and initial-only transient handoffs.

## Owner decision required

no

## Checks

- Revision and read-only scope: PASS. HEAD matches the supplied base. All pinned inputs matched. No files changed and no verdict writers ran.
- R1: coherent combination and frequency ratios: PASS. All 58 permitted ratios with p <= 20 are included. Coincident harmonics use one maximized relative time shift. The 204/816 and 204/408 kHz examples reproduce approximately 2.8547 and 2.8138 A, failing the former eight-can bank. The 1 s thermal constant remains an explicit assumption. Whole-domain higher-order coverage remains the blocker below.
- R2: independent ballasted-corner calculation: PASS. At VIN 9 V, VBAT 10 V, Iout 8.2995 A and 171.762953/343.525906 kHz, obtained 2.710191 A. All cans are 514.8 uF; target branch 37.4775 mOhm/5 nH; sibling branches 339.0225 mOhm/5.5 nH; ceramics 4 uF/2 mOhm/0.8 nH; L11/L16 5/20 nH. This verifies the reported corner, not the global maximum.
- R3: ballast power and temperature: PASS. The conservative per-resistor loss is 0.282953 W using 38 mOhm at +1.375%. The sheet gives 3 W through 70 C, decreasing to zero at 170 C: 2.55 W at 85 C and 2.10 W at 100 C. The code carries 1% tolerance plus 50 ppm/K over an assumed 75 K excursion. Actual resistor temperature remains a bench obligation.
- R4: frequency, lifetime and loop calculations: PASS. SNVSAI1D p.6's 175/200/225 kHz row, Equation 5 and RT tolerance/TCR give 171.762953/199.043930/227.078334 kHz. Ballast with R12 12 mOhm gives PM/GM 79.02 degrees/15.61 dB, widened 79.01 degrees/13.18 dB. With R12 5 mOhm, widened GM is 8.458 dB. At 300 mOhm can ESR, the drawn circuit gives GM 1.041 dB, widened -0.759 dB; ballast plus R12 12 mOhm gives 5.087/3.253 dB. The cold finding is numerically supported and explicitly OPEN. Panasonic p.6 supports the conditional lifetime expression with rated rise conservatively set to zero.
- R5: tests and draft: PASS. 15 of 16 test functions passed. The excluded function writes scratch copies. The draft preserves other stages, composes identically in all 24 orders, refuses missing R12 through order_ok(), and refuses release without RELEASE.md. These tests inherit the search coverage limitations.
- Full output replay: NOT_RUN. The full script calls L4-E4, which invokes r11_dep.py; its fig8_readings() creates temporary raster files. The full replay was therefore excluded under the read-only instruction. Byte-for-byte output reproduction is not claimed.

## Evidence and minors

- R2 sources: Panasonic ZK, 01-Apr-22, pp.1-2 supports C factors 0.8 x 0.7 = 0.56 and 1.2 x 1.3 = 1.56, no printed ESR floor, and size G's 0.3 Ohm limit at 100 kHz/-40 C after endurance. Applying that limit throughout service down to -20 C is a modelling inference, not a printed guarantee. The general low-temperature impedance-rise statement on p.6 explicitly excludes hybrids; it cannot independently prove that inference. ESL remains inferred.
- R2 selection: a positive ballast resistance supplies damping and removes the unsupported intrinsic ESR floor. The record identifies 38 mOhm as the smallest passing stocked value in its searched family; 36 mOhm reads 2.848 A. The full independence claim needs the additional evidence specified below.
- R3 energy: independent calculation gives 0.293786 W across all six ballasts at the reported worst-can corner. A different permitted high-load case, six matched 514.8 uF cans with zero intrinsic ESR, 5 nH branches and nominal 38 mOhm ballasts, gives 0.701539 W at the same operating point and worst common phase. Therefore six-bank loss cannot be represented by the single-resistor 0.28 W figure. Conditional on the reported per-can maximum being established globally, a conservative sum is 1.697718 W.
- R3 typical illustration, not a measured typical: VIN 13.8 V, VBUS20 20 V/3 A, VBAT 14.4 V, fFE 199.044 kHz, fCH 400 kHz, matched 330 uF/20 mOhm cans with 3.5 nH total branch ESL and nominal ballasts gives 0.010581 W total. REQ-072 should carry operating-point-dependent ballast loss whenever the front end runs, without double-counting it once measured converter efficiency includes it.
- MINOR: L4E8-BANK.md:167 and the energy handoff omit ballast derating and total operating loss. Add the temperature-dependent rating, the assumed resistor-temperature envelope and a loss term for the energy-model owner.
- MINOR: L4E8-BANK.md:244-253 retains initial-capacitance consequences while the new decision uses endurance extremes. With its existing ceramic allowances, that expanded range is 1.1928 to 3.3198 mF. The same first-order equations give 16.1338 A restart, 1.0412 mJ, 10.2748% soft-start draw at 9 V and approximately 0.455 to 1.494 s bleed time. Label the old figures initial-only and carry the expanded results into the restart obligation. These calculations do not establish saturation-aware performance.
- B4: the lifetime is explicitly CONDITIONAL and bench 7b.8 item 4 assigns can-temperature measurement. This resolves the previous unsupported self-heating cancellation. The measured temperature must represent the temperature rise used by the lifetime model.
- No contradiction between owner requirements was identified. REQ-072 remains a design objective; component selection, calculation corrections and qualification criteria remain engineering work under D-25.
