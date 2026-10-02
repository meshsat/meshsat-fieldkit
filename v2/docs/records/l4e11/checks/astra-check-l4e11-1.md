accepted: no

# Layer 4, L4-E11: the focused check of source-only and dead-pack operation (U-04), the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09) by the engineering collaborator (an AI review, read-only)

Collaborator job `cx30-l4e11-check`, run `20261002T024127Z-317909`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e11 at commit `3f9cf2838e30`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E11: NOT YET. This read-only AI review reproduces the cable currents, nominal 9 V knee result and D-09 arithmetic. Blocking corrections remain in the UVLO equations, firmware rules, source-power comparison and weak-source protection envelope. No genuine owner decision is presently required.

## Blocking discrepancies

- B1, K4: l4e11_power.py:446–448 assigns the divider-only threshold to the rising edge and subtracts hysteresis for falling. TI specifies the opposite placement of hysteresis. Consequently the U4-F2 diagnosis is directionally right but its numbers and 42.2 kOhm remedy are wrong. Correct the equations and rederive the draft. Also include LM5069 POREN: SNVS452G p.5 permits a 9 V enable threshold at the IC, leaving no guaranteed allowance for upstream voltage loss from a 9.00 V plug. A divider correction alone cannot establish the claimed startup margin.
- B2, K1/K4: L4E11-SOURCE-ONLY-AND-ENTRY.md:195–199 and :319–321 assume that inability to discharge means the gauge already prevents charging. Its own :115 and SLUUAQ3A p.15 show a counterexample: warm CUV opens the discharge FET while charging remains possible. The drafted operator 'no charge' hold then does nothing. Additionally, :361 treats battery supply as an acceptable fallback for REQ-077, whereas pcb_requirements.yaml:13847 explicitly requires the charger to carry the kit. Rewrite R-a as a state table separating charge permission from discharge permission and retain N2 until the required charge hold preserves source supply.
- B3, K1: l4e11_power.py:523–528 and L4E11-SOURCE-ONLY-AND-ENTRY.md:214–218 omit the same cable and entry losses identified by U4-F3. The claimed 59.5/79.8/89.6 W are not delivered-power bounds at the plug. For example, using the selected 0.115511 Ohm model gives 53.90/69.79/76.96 W at 7.3/9.8/11 A before auxiliary loads. Recompute with applicable temperatures and losses. E11-09 at :347 also needs a functional cold-start/warm-up acceptance, since restoring 19.7 W alone demonstrates none of the listed heater states. This is missing engineering closure, not evidence that REQ-015 is impossible under every arrangement.
- B4, K2: l4e11_power.py:612–613 and L4E11-SOURCE-ONLY-AND-ENTRY.md:254–256 check only the fuse table's individual points. Under the record's monotone envelope, currents approaching 35 A can persist for 5 s and currents approaching 60 A for 0.5 s. E11-16 at :354 instead requests 35 A for 0.5 s and 60 A for 0.1 s. Correct the interval bounds and acceptance, including total clearing energy above 60 A through the declared prospective fault current. Also require installed continuous-current evidence for the selected contacts; the printed 23 A test current alone is insufficient.
- B5, K1: L4E11-SOURCE-ONLY-AND-ENTRY.md:149 and :200–203 turn nominal or commanded charge currents into guaranteed maxima. SLUSE66A p.10 lists 384 mA only in the typical column and gives +21.5% regulation error at the 1.024 A setting with 5 mOhm sensing. That setting with a -1% resistor can reach approximately 1.257 A. Specify R-b's register value and a supported actual-current bound, then recompute diode dissipation. Until then neither the asserted 1 W maximum nor the 4.22 W maximum charge allowance is established.

## Classification

- **OWNER_REQUIREMENT**: Mandatory source operation, cold start and charge holds Evidence: v2/ecad/tools/pcb_requirements.yaml:7648, :7653, :8776, :13756 and :13847.
- **DESIGN_OBJECTIVE**: PS-IDLE-SPEC endurance profile Evidence: v2/ecad/tools/pcb_requirements.yaml:7768 and :7778; v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md:18–22.
- **IMPLEMENTATION_DEFECT**: B1 incorrect UVLO equations and resistor draft Evidence: v2/docs/records/l4e11/l4e11_power.py:446–448; apply_gen_sch_e_uvlo.py:30–33; SNVS452G p.24 Equations 38–40.
- **COMPONENT_LIMITATION**: B1 independent LM5069 startup floor Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:154–155 omits POREN; v2/vendor/ti/ti-lm5069.pdf, SNVS452G p.5 specifies POREN up to 9 V.
- **IMPLEMENTATION_DEFECT**: B2 firmware charge/discharge-state conflation Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:195–199, :319–321 and :361; SLUUAQ3A p.15.
- **MISSING_EVIDENCE**: N1 and N2 charger behavior Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:124–127; the N2 avoidance claim at :361 is not established.
- **IMPLEMENTATION_DEFECT**: B3 source-power comparison Evidence: v2/docs/records/l4e11/l4e11_power.py:523–528 omits the resistance already calculated at :469–471.
- **MISSING_EVIDENCE**: B3 functional 9 V cold-start envelope Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:140–147 and :347 do not demonstrate cold-start/warm-up service at the proposed minimum power.
- **IMPLEMENTATION_DEFECT**: B4 incomplete weak-source pulse envelope Evidence: v2/docs/records/l4e11/l4e11_power.py:612–613; L4E11-SOURCE-ONLY-AND-ENTRY.md:354; held Littelfuse 0997 sheet, revised 2025-11-18, p.3.
- **MISSING_EVIDENCE**: D-06 installed component ratings and resistance floor Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:247–251 and :349–354.
- **IMPLEMENTATION_DEFECT**: B5 unsupported actual-current maxima Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:149 and :200–203; SLUSE66A p.10.
- **MODELLING_ASSUMPTION**: D-09 capacitor stacking and SOA extension Evidence: v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md:280–301 and :385–388. Arithmetic reproduces; extrapolation and installed thermal performance remain conditional.

## Smallest next action

First correct the UVLO model to TI Equations 38–40 and evaluate POREN at the actual IC supply from a 9.00 V plug. Then revise the firmware state table, current bounds and protection acceptances using B2–B5.

## Closure criterion

A corrected candidate must establish 9.00 V plug startup including internal enable thresholds and losses; preserve source supply during every required charge hold; bound actual diode current; demonstrate the required cold-start/warm-up sequence within the corrected source envelope; and cover every fuse-clearing interval with explicit component-evidence obligations. D-09 must retain its reproduced timing margin and conditional SOA status. Hypothetical corrections must remain labelled as drafts.

## Owner decision required

no

## Next action (the collaborator's)

Return the candidate to its author for one focused correction of B1–B5, retaining the reproduced D-09 calculation and its explicit SOA conditions.

## Checks

- Input binding and output reproduction: PASS. All hashes match. Computed stdout is byte-identical to l4e11_power.out. Reproduction does not validate the model's equations.
- K1 requirements and 9 V power: INCONCLUSIVE. REQ-015 is quoted accurately and names no load profile. The model gives 8.818536 V at VIN_RAW and 8.285981 W at VBAT; the selected cable gives 8.832920 V and 10.025025 W. These are hypothetical energized equilibria with the present knee, not proof of startup or arrangement-independent impossibility. Mandatory cold-start and charge-hold functions remain obligations.
- K2 cable fault-current arithmetic: PASS. AWG 14 at 2 m: 34.910793 mOhm, 1236.866780 A. At 3 m: 48.875110 mOhm, 883.476272 A. Required external cable length under these assumptions: 2.592167 m.
- K3 startup and timer: PASS. Startup: 1.587991 ms nominal, 3.062183 ms at the stated corners. Required 1.5× margin: 4.593274 ms. Capacitance: 157.248834–179.637892 nF. Timer: 4.927130–14.652816 ms, giving 0.333856 ms margin. SNVS452G p.21 Equation 13 supports the 1.5 factor. These results retain the record's capacitance and power-limit assumptions.
- K3 SOA: INCONCLUSIVE. The quoted curve coordinates and derating give approximately 0.710 A against 0.675 A at 14.653 ms. Extension beyond the 10 ms curve is 46.53%. The record correctly makes this conditional; arithmetic is not maker evidence for that extrapolation or the assumed case temperature.
- K4 UVLO electrical correction: FAIL. Rising threshold is VTH(1 + R20/R21) + IHYS×R20. Drawn rising corners are 9.908/11.127/12.372 V; drafted 42.2 kOhm corners are 9.329/10.524/11.745 V. Neither starts at 9 V.
- Draft composition and workspace preservation: PASS. Hot-swap then UVLO then timer composes successfully. Timer commutes with the hot-swap draft. Applying UVLO first causes the hot-swap draft's expected refusal. HEAD remains the supplied commit and git status is clean. No verdict writer or mutation was run.

## Evidence and minors

- K1: pcb_requirements.yaml:7648 and :7653 match the REQ-015 quotation. PS-IDLE-SPEC belongs to the objective at :7768 and :7778. However, :8776, :13756 and :13847 preserve cold operation, warming before charge and the charger carrying the kit during the shore charge hold. Absence of a named wattage does not waive those functions.
- K1: SLUSE66A, v2/vendor/ti/bq25731-datasheet.pdf, pp.24–26, 34, 89 and 92 supports the quoted power-up, CHRG_OK, HIZ, clamp and battery-free example statements. N1 remains open. Arrangement A is a reasonable conditional candidate, but the present rules do not dispose of N2.
- K2: A minimum resistance is a defensible engineered parameter for a specified kit cable, provided its minimum resistance over construction tolerances and temperature is controlled, and replacement cables satisfy it. A nominal AWG designation and length alone are not the complete protection specification.
- K2: The held Amphenol catalogue, PDF p.28, prints 23 A as a crimp-contact test current. Amass XT60-F V1.2 p.1 prints 30 A rated and 60 A instantaneous, with 12 AWG recommended. Neither establishes every proposed connector variant's installed continuous and pulse capability. The cable, holder and NATO-plug ratings remain explicitly outstanding.
- MINOR: L4E11-SOURCE-ONLY-AND-ENTRY.md:240 should expose the tolerance calculation behind rejecting the smaller fuse. A 5.1 A maximum entry limit implies approximately 3.942 A minimum using LM5069 threshold and 1% sense-resistor corners, below 4.629 A. The rejection is defensible for preserving that envelope, although the prose's direct comparison of 5.1 and 4.629 is misleading.
- MINOR: L4E11-SOURCE-ONLY-AND-ENTRY.md:382 incorrectly calls the copper assumption one-sided. Greater conductor area or lower resistivity can increase fault current. Replace that claim with a tolerance-bound resistance check.
- MINOR: The charge-disabled quotation at L4E11-SOURCE-ONLY-AND-ENTRY.md:99 comes from the BATOVP discussion. Preserve that context; it is not a specification of battery-free regulated voltage or transient performance.
