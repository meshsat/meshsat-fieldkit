accepted: no

# Layer 4, L4-E9: the focused check of the connected power architecture and its closure gate by the engineering collaborator (an AI review, read-only)

Collaborator job `cx28-l4e9-check`, run `20261002T004904Z-179094`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e9 at commit `6097922aa7a2`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E9: NOT YET. The reverse-input, fuse-rating and cutoff arithmetic reproduces. Q7's power-limit proof, the fault exemptions, U17's transient coverage and the completeness of the architecture-choice list need correction. The gate correctly remains NOT CLOSED. Read-only AI review of a prototype design.

## Blocking discrepancies

- B1, G1/G5: Q7's fault-power proof is incomplete. L4E9-ENTRY-PROPOSALS.md:43 and l4e9_power_path.py:897-901 calculate 20.4798 W nominal and multiply by 31/25 to claim 25.395 W. At 43.1795 V this is only 4.7429 mV nominal sense voltage. SNVS452G p.20 advises against less than 5 mV because power-limit accuracy degrades; the cited 19/25/31 mV limits are tested at 48 V and RPWR = 150 kohm, not this 20 kohm setting. The SOA comparison also uses 36 V for a fault evaluated at 43.18 V and assumes a 100 C case. Correct the setting or obtain applicable bounds, then compare the complete pulse at the same voltage and temperature. A 22 kohm, 1% R24 is a bounded candidate: its low corner gives 5.060 mV at 43.18 V, but its power spread and SOA still need checking. IF-05's MEETS at l4e9_power_path.out:171 must not imply this unresolved proof is complete. Also add the actual turn-on/light-load test: the cited R-80 currently specifies reverse input only, DOWNSTREAM-REGISTER.md:123.
- B2, G1/G2/G5: The single-fault exemptions are unsupported. L4E9-ENTRY-PROPOSALS.md:44,74 and L4-POWER-ARCHITECTURE.md:355-357 cite ASM-001 for the DC_P short and weak-source connector overload. Authoritative ASM-001, pcb_requirements.yaml:5441-5453, concerns LoRa/cellular failover exceptions only. It grants no power-fault exemption. The weak-source case is an unresolved protection-coordination limitation; continuous contact ratings alone neither prove damage nor establish acceptable 13.5-20 A exposure. Trace these faults against REQ-045/PWR-003 and the SHORE_INPUT stage, obtain contact/conductor time-current limits, and select coordinated protection or a suitable interconnect. Do not describe them as outside every requirement without that disposition.
- B3, G3/G5: The 14.33 A/72.38 mV/1.037 W calculation is not a complete bound for R227. The draft changes the helper's input rail, placing C81/C82 and the VIN/BIAS bypass capacitors behind R227: apply_gen_sch_a_u17.py:48-54; gen_sch_a.py:510,608-609,1195-1200. Their charging current bypasses U16's cycle-current control. Thus l4e9_power_path.out:272,477,483 cannot bound every transient drop by 72 mV. A nominal 20.2 uF bank already draws 20.2 A at a hypothetical 1 V/us slew; this is an illustrative counterexample, not an asserted waveform. Bound actual startup and clamp-pulse differential voltage, ringing and resistor pulse energy, distinguishing ADC saturation from absolute-limit damage. The buck-fault explanation also needs ripple and RMS current, not valley current times duty alone. Until then IF-13's blanket MEETS is incomplete.
- B4, G5: U-01 to U-03 are not demonstrated to be the complete architecture-level uncertainty set. L4-POWER-ARCHITECTURE.md:165-167 leaves source-only/dead-pack operation conditional on Q-TI-3/O-CHG-2, but DOWNSTREAM-REGISTER.md:128 treats it solely as later testing. No bounded alternative or consequence of a negative answer is supplied. Moreover, the acceptance asks a source to run PS-IDLE-SPEC without specifying source voltage, although the same architecture records insufficient 9 V power without pack supplementation at :147. Resolve the startup mode and source envelope from the charger behavior and boot sequence, or explicitly add this as an unresolved architecture question with alternatives. Assignment to a bench owner does not settle it.

## Classification

- **OWNER_REQUIREMENT**: REQ-015 operating and over-voltage ranges Evidence: pcb_requirements.yaml:7648-7654 requires operation at 9-36 V and damage-free reversed/over-voltage handling to 40 V. The selected cutoff does not contradict this.
- **MODELLING_ASSUMPTION**: Q7 power-limit scaling and hot SOA Evidence: l4e9_power_path.py:100-103,897-901 assumes the hot case and extrapolates power-limit spread; SNVS452G p.20 exposes the sub-5 mV condition.
- **MISSING_EVIDENCE**: Q1 threshold departure and missing applicable test Evidence: L4E9-ENTRY-PROPOSALS.md:46 names turn-on/light-load risk, but DOWNSTREAM-REGISTER.md:123 specifies reverse input only.
- **IMPLEMENTATION_DEFECT**: Power-fault exemption attributed to ASM-001 Evidence: The record's classification at L4E9-ENTRY-PROPOSALS.md:44,74 conflicts with the actual scope of ASM-001 at pcb_requirements.yaml:5441-5453.
- **COMPONENT_LIMITATION**: Fuse/contact coordination under weak-source faults Evidence: L4E9-ENTRY-PROPOSALS.md:74 records 13.5-20 A exposure beyond stated contact continuous ratings; no applicable contact transient-withstand evidence is supplied.
- **MISSING_EVIDENCE**: R227 transient and buck-fault bounds Evidence: L4E9-ENTRY-PROPOSALS.md:98-103 omits capacitor charging and a buck ripple/RMS derivation; the draft's capacitor connections follow gen_sch_a.py:510,608-609.
- **IMPLEMENTATION_DEFECT**: U17 firmware voltage meaning and accuracy budget Evidence: LAYER5-HANDOVER.md:16 calls POE_VIN a VBAT reading and repeats an accuracy budget omitting SBOS547C p.5 temperature drift.
- **MISSING_EVIDENCE**: Dead-pack startup categorized only as downstream testing Evidence: L4-POWER-ARCHITECTURE.md:165-167 and DOWNSTREAM-REGISTER.md:128 lack a supported startup envelope and adverse-outcome disposition.
- **COMPONENT_LIMITATION**: IF-11 temperature mismatch Evidence: L4-POWER-ARCHITECTURE.md:253 compares modeled E5 inside air of 75 C with +70 C parts under U-02. It is not a contradiction between requirements.
- **DESIGN_OBJECTIVE**: Runtime shortfall Evidence: L4-POWER-ARCHITECTURE.md:337-338 correctly retains the unmet 48-72 hour objective without converting it into a mandatory minimum.

## Smallest next action

Correct the fault-scope attribution and mark the unsupported Q7/U17 conclusions conditional; then add bounded calculations for Q7 at the selected cutoff, R227's capacitive transients, and source-only startup, with explicit dispositions for negative results.

## Closure criterion

B1-B4 each have an applicable source-backed bound or a clearly open engineering question with alternatives. Q7's complete pulse fits derated SOA at the same voltage and temperature; fuse/contact coordination has a traced disposition; U17 pin stresses and R227 pulse/RMS dissipation are bounded; startup has a supported source envelope or joins the unresolved-choice list. The gate and downstream acceptance criteria reflect those results without treating software tests as physical evidence.

## Owner decision required

no

No additional owner decision is established by this review. The existing U-01 owner items remain as recorded. These findings first require engineering corrections and bounded evidence gathering; a proposed change to approved requirements, functions, deployment conditions, enclosure constraints or resources would then require an owner decision.

## Next action (the collaborator's)

Return B1-B4 to the author for one bounded correction and evidence pass, keeping the architecture gate open.

## Checks

- Revision and read-only scope: PASS. HEAD matches the specified base commit; working tree remains clean. No verdict writer or repository test runner was executed.
- Held maker documents: PASS. The six principal TI and Littelfuse document hashes match L4E9-ENTRY-PROPOSALS.md:15-20, including the held 0997 sheet.
- G1 reverse input and hot-swap protection: INCONCLUSIVE. 66.15 V is below Q1's 100 V and the controller's 70 V recommended/75 V absolute limits. The calculated 25.395 W hot-swap bound is not established by the cited power-limit test condition; see B1.
- G2 fuse selection: PASS. For the stated harness: R20 = 0.089908 ohm, R(-20 C) = 0.075774 ohm, prospective current = 569.844 A. The 58 V DC/1000 A rating and 80 C column's 7.3 A exceed the stated demands. Startup I2t = 0.308632 A2s versus 93 A2s typical melting I2t. This does not establish connector fault coordination.
- G3 monitor proposal: INCONCLUSIVE. Steady calculations reproduce: 3.6818 A/18.593 mV; boost-limit calculation 14.333 A/72.383 mV/1.03749 W; Current_LSB 0.5 mA and CAL 2048. The proposal's capacitive transient path is outside that current-limit calculation; see B3.
- G4 cutoff window: PASS. 36 + 2*sqrt(2) = 38.8284 V. The selected window is 39.7085/41.4408/43.1795 V, leaving 0.8801 V above the stated CS101 peak and 1.2205 V below D10's 25 C minimum breakdown. REQ-015 requires operation through 36 V and damage-free over-voltage handling to 40 V, not continuous operation through 40 V.
- G5 gate and issue classification: FAIL. The overall open gate and IF-11 thermal attribution are appropriate. However, the fault exemptions are unsupported, IF-05/IF-13 omit consequential conditions, and R-85 lacks a bounded adverse-outcome disposition establishing that it is only downstream verification.

## Evidence and minors

- G1: The 60 V MOSFET guidance is not a prohibition on a 100 V FET. SNOSD17G p.17 explains it by controller voltage capability; p.5 supplies the applicable 70 V recommended/75 V absolute differential limits. The 3.2 V threshold does depart from TI's light-load regulation and turn-on guidance. It remains a real verification concern, not a demonstrated failure.
- G1: The 100.5 V negative clamp-pulse scenario exceeds Q1's rating, and the controller exceeds 75 V once its cathode exceeds 10.5 V with its anode at -64.5 V. Its classification as a capability scenario is supported by D-16 and CHO-003: pcb_requirements.yaml:601 and :9305. Neither the avalanche-energy comparison nor F1's interrupting rating proves Q1 survival.
- G3: The stated common-mode values, 16.884 V, 20.135 V and 29.2 V, are below INA226's 36 V measurement range and 40 V absolute limit. SBOS547C pp.4-6 separately specifies differential absolute limits of +/-40 V and requires each input pin to remain between -0.3 V and 40 V.
- G5: U-01, U-02 and U-03 are properly identified as unresolved choices. IF-11's NOT MET is attributable to the modeled 75 C E5 inside air against +70 C parts, not to the undocumented 8.4 W load: L4-POWER-ARCHITECTURE.md:253 and l4e9_power_path.out:255. This is conditional thermal evidence, not a measured temperature or a contradiction between owner requirements.
- MINOR: The cold D10 result is conditional. 44.4*(1-0.001*45) = 42.402 V uses a typical temperature coefficient, not a warranted bound. A-17 acknowledges this at L4-POWER-ARCHITECTURE.md:287; the MEETS/INFERRED presentation at l4e9_power_path.out:155 should retain that condition.
- MINOR: The firmware accuracy budget omits INA226 gain and offset temperature drift specified in SBOS547C p.5. L4E9-ENTRY-PROPOSALS.md:104 and DOWNSTREAM-REGISTER.md:77,127 should recompute the budget at stated IC and shunt temperatures. At an IC temperature of -20 C, the omitted terms alone are 0.225% gain and 0.9 mA offset.
- MINOR: U17's VBUS pin measures POE_VIN, not VBAT. Correct the firmware wording in L4E9-ENTRY-PROPOSALS.md:106 and LAYER5-HANDOVER.md:16, or explicitly reconstruct VBAT by adding the measured shunt drop.
- MINOR: 0.286 ms is an estimate from typical melting I2t, not maximum total clearing time: l4e9_power_path.out:451; 0997 sheet p.2 explicitly excludes arcing from that I2t. Retain it only as an illustration.
- MINOR: Changing R-29's internal lead to AWG16 changes the prospective-current calculation. With the same external cable and 1.31 mm2 internal conductors, it becomes approximately 623.9 A, still below 1000 A. Recalculate R-95 when the harness is selected: DOWNSTREAM-REGISTER.md:79,135.
- MINOR: Criteria 3 and 4 concern documentation and assignments, so software checks can support those limited claims. The unqualified statement that every mandatory function is delivered at L4-POWER-ARCHITECTURE.md:342 should instead describe intended behavior subject to the named open conditions.
