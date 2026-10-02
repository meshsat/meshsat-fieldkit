accepted: no

# Layer 4, L4-E10: the targeted recheck of the cell and thermal design of the battery path by the engineering collaborator (an AI review, read-only)

Collaborator job `cx27-l4e10-recheck`, run `20261001T231603Z-57210`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e10 at commit `2316b107253e`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E10: NOT YET. The conductance thresholds and requested cold-storage arithmetic reproduce. R4's framing and R5's protection redesign are corrected. R2 still omits required sequence and recovery details, and R3 retains unsupported thermal-route rejections and overstates the heater-duration evidence. A1 is defensible as the next engineering investigation, with FEA-008 open and no owner decision forced.

## Blocking discrepancies

- R2: The screen is not yet a complete mapping of the requested profiles. C05 omits E3-H's +40 C hold up to 4 h, sensor-controller-reset repeat, TMP117 fallback thresholds and restart at or below 46.5 C after 30 minutes. E3-L's start with the lid already closed is absent. C17 omits OTD recovery at or below 52.5 C; C16/C18 do not retain E4-T's return to 25 C, full-function and provisional capacity-within-5-percent criteria. Add these explicit mappings and identify charge states that TEST-PLAN does not specify as missing inputs.
- R3, usable energy: l4e10_cell_thermal.py:775-783 computes capacity times nominal voltage, ageing, available SOC and an assumed cold factor. It does not establish terminal energy over the actual partial-SOC voltage curve, cutoff and temperature history. Samsung Ver. 1.1 section 7.5, PDF p.6, describes a full standard charge followed by a three-hour temperature transition and 3.4 A discharge to 2.65 V; it does not establish the claimed partial-SOC heater range. Label 11.9-28.9 Wh and 1.3-8.6 h as model sensitivities with these missing inputs, or supply the required discharge evidence. Retain the independently justified shutdown-path rejection.
- R3, passive storage: l4e10_cell_thermal.out:376 and :382 still reject 'passive insulation or thermal storage' with 'Missing: none'. The calculation varies conductance while retaining the existing heat capacities and assumed k=0.02 W/mK; it establishes the stated insulation mismatch, not a bound on added sensible or latent thermal storage. Narrow the rejection to that calculated insulation arrangement and leave added storage INCONCLUSIVE on material capacity, initial condition and available volume, unless those are explicitly bounded.
- R3, powered cooling: l4e10_cell_thermal.py:811-813 uses G_b*(1+1/COP)<G_enclosure for rejection into the inside air. Heat extracted from that air through the pack must also be subtracted, leaving net added heat Q_c/COP. For the stated operating corner, G_b/COP=0.888449 W/K is below 1.22 W/K, so a finite equilibrium exists at COP 0.5. Correct the balance before claiming non-convergence. The same simplified model gives approximately 121.7 C air for E3-O and 140.1 C for E5, which establishes no feasible cooler solution; assess the resulting temperatures and power against limits or retain INCONCLUSIVE.

## Classification

- **OWNER_REQUIREMENT**: Temperature limits, fitted-pack exposures and stored configuration Evidence: pcb_requirements.yaml D-02a, D-29, D-36 and REQ-025 preserve the requirements; missing component evidence does not create a contradiction.
- **MISSING_EVIDENCE**: R2 incomplete sequence and recovery mapping Evidence: C01-C19 omit the explicit TEST-PLAN details identified in the R2 blocker.
- **MODELLING_ASSUMPTION**: R3 heater energy and duration Evidence: The arithmetic reproduces, but nominal voltage and an extrapolated cold-capacity factor do not establish usable energy for the actual partial-SOC discharge.
- **IMPLEMENTATION_DEFECT**: R3 blanket thermal-storage rejection and cooler balance Evidence: The rejection exceeds the insulation model's scope; the cooler predicate counts extracted heat twice.
- **COMPONENT_LIMITATION**: Present cell, shutdown path and mat capacity Evidence: 35E Ver. 1.1 section 3.12; TI SLUUAQ3A section 5.4.2; RS PRO 245-556 sheet p.2.
- **MISSING_EVIDENCE**: A1 feasibility and alternative-cell protection Evidence: LO-01d to g remain open on named component, source, fit and thermal inputs. Option B correctly requires a coordinated protection redesign.

## Smallest next action

Complete the omitted test mappings, qualify the heater-duration range, narrow the passive rejection to the modelled insulation, and correct the internal cooler heat balance. No owner escalation is needed.

## Closure criterion

Every requested exposure explicitly maps its sequence, configuration, charge-state basis and recovery; heater-duration claims identify unsupported discharge inputs; passive rejections cover only calculated arrangements; and corrected cooler balances conserve energy. Retain all prototype verification obligations and FEA-008 OPEN.

## Owner decision required

no

## Checks

- Revision, inputs and read-only scope: PASS. HEAD matches the requested commit; all 31 hashes match; worktree remains clean. No verdict writer, author main program or file-writing test was run.
- R1: conductance thresholds and coupling: PASS. Pack heat 23.445748 W, cell heat 0.174116 W, block conductance 0.1480749 W/K and shore heat 24.996383 W give thresholds 1.245515, 1.315393, 1.529988, 1.604320 and 1.666426 W/K. Lid-open cells reach 60.393688 C on battery; shore air reaches 60.488839 C. The revised acceptance retains live bearers, F2, controls and the +59 C abort, with BANK-R1 and measurement dependencies open.
- R2: exposure mapping: FAIL. The added exposure names, main durations and supply sequences are present. The complete reset, restart and recovery mapping remains incomplete, as specified in the blocker.
- R3: independent thermal and energy arithmetic: PASS. Reproduced insulation thicknesses 24.5704/30.2773 mm; pack-fed demand 3.37003-9.29506 W; assumed available energy 11.86704-28.944 Wh; resulting hold duration 1.27670-8.58865 h; primary demand through the regulator 42.2341-116.5949 Wh; loss-of-heating times 0.301365-1.086551 h; and cell warming energy 0.133333-0.183333 Wh/K. These reproduce the stated assumptions, not qualified hardware performance.
- R3: rejection logic and evidence boundaries: FAIL. The shutdown-path rejection is supported by TI SLUUAQ3A section 5.4.2, PDF p.46. However, actual usable energy is not established, added thermal storage is rejected without being modelled, and the internal cooler balance double-counts recirculated heat.
- R4, R5 and original minors: PASS. FEA-008 remains open; the shortlist contains A1-A3; no requirement change or purchase is taken. TI SLUSEG7D p.3 supports the stated variant differences and coordinated redesign obligation. The 7.5 W mat allocation gives 12.43594/12.83693 C; two-node residuals are 0.351289/0.301105 K. The +71 C exposure correctly permits, rather than guarantees, a destructive trip.

## Evidence and minors

- The separate-primary route correctly remains INCONCLUSIVE on usable energy at -33 C, thermostat tolerance, gradient, placement, transport classification and F2. E5 correctly remains INCONCLUSIVE on its missing dwell/ramp profile. Heating an already out-of-range pack cannot undo the prior specification excursion; this does not establish irreversible cell damage.
- MINOR R1: The coupling passes the +59 C cell criterion only in the reported battery case. Independently recomputed shore values are 59.29935 C cells and 63.42406 C air. Qualify the general 'closes the cell criteria' wording in l4e10_cell_thermal.out:248 and l4e10_cell_thermal.py:919 accordingly. The complete conductance requirement remains necessary.
- MINOR R2: C17 equates a +58 C physical cell temperature with an OTD reading at or above 57.5 C. The documented reading error permits a lower gauge reading. Replace the guaranteed immediate refusal with the actual requirement: OTD must stop discharge before a cell exceeds +60 C and recover at or below +52.5 C.
- MINOR R3: The fast pack-fed corner requires 8.1973 W into the cells, exceeding the held mat's 7.5 W rating at 12 V. Identify this as an additional inability to maintain that setpoint with the present mat. The existing rejection is unchanged.
