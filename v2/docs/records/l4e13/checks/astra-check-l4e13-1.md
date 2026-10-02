accepted: no

# Layer 4, L4-E13: the focused check of U-03's panel by the engineering collaborator (an AI review, read-only)

Collaborator job `cx34-l4e13-check`, run `20261002T051048Z-490882`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e13 at commit `b3e01e25924e`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E13: NOT YET. AI review completed. The arithmetic reproduces, but the proposed unit-acceptance windows need stronger bounds, and U-03's classification omits the valid controlled-unit route. No owner requirement change is needed.

## Blocking discrepancies

- B1: L4E13-PANEL.md:20-23 and :64-75; l4e13_panel.py:518 and :589-590. The proposed acceptance windows omit a justified maximum irradiance and bounded coefficient/model uncertainty. Their upper endpoints exceed 25 V under the record's own 1250 W/m2 sensitivity; SunPower's lower endpoint also fails under its printed absolute coefficient. Correct the acceptance contract using supported environmental and uncertainty bounds, or direct unit characterization covering those conditions.
- B2: L4E13-PANEL.md:27 and :181-183; l4e13_panel.py:568 and :587. The decision makes a maker-wide band the only route out of U-03, despite O-1 and this record admitting controlled-unit acceptance. Once B1's supported contract is established, classify U-03 as conditional downstream unit selection under PANEL-ACC. Keep the absence of an accepted physical unit explicit; do not require a production-wide guarantee to settle the prototype architecture.

## Classification

- **OWNER_REQUIREMENT**: REQ-016 limits and required cold boundary Evidence: pcb_requirements.yaml:7693-7702, :8769 and :398 establish 25 V, 17.6 V, 100 W, the 10 A entry, and -20 C use. D-34:984 preserves the solar window.
- **MODELLING_ASSUMPTION**: STC irradiance and relative coefficient used as acceptance bounds Evidence: L4E13-PANEL.md:137 and :147; l4e13_panel.py:73-75 and :481-482. These assumptions reproduce the calculations but do not establish worst-case unit behavior.
- **MISSING_EVIDENCE**: Supported unit voltage and useful-power envelope Evidence: L4E13-PANEL.md:64-68 and :200-203. No measured unit, coefficient limits or complete uncertainty budget exists. Obtain warranted bounds or characterize the identified unit.
- **IMPLEMENTATION_DEFECT**: U-03 excludes controlled-unit closure Evidence: l4e13_panel.py:568 and :587 decide solely from maker-band qualification; L4-ENERGY-ARCHITECTURE.md:221-225 permits a controlled unit. Revise the decision and downstream contract consistently.
- **MODELLING_ASSUMPTION**: Noon hold compatibility screen Evidence: L4E13-PANEL.md:158-160 and l4e13_panel.py:473-482. Correct as a necessary model screen; actual useful power needs the unit's I-V behavior and energy trace.
- **COMPONENT_LIMITATION**: Solbian current against the existing entry Evidence: L4E13-PANEL.md:45 and :76; pcb_requirements.yaml:7700. The 12.014375 A design scenario exceeds the existing 10 A rating, requiring coordination evidence before selecting Solbian.
- **MISSING_EVIDENCE**: Unheld screening documents Evidence: L4E13-PANEL.md:122-127 and inputs/screen-2026-10-02.json:2. Addresses and hashes alone do not permit independent verification of all screening claims.

## Smallest next action

Develop PANEL-ACC around one identified SunPower unit, with a supported cold-voltage envelope, coefficient uncertainty and measured I-V acceptance; then replace U-03's maker-only condition with the maker-bound or controlled-unit route.

## Closure criterion

The revised contract demonstrates maximum panel Voc plus uncertainty at or below 25.000 V over the justified temperature and irradiance envelope, and strictly positive useful charging power at the applicable hold corner with its energy trace quantified. It retains the 10 A entry and conditional 100 W stage obligations. The decision logic permits controlled-unit qualification, and architecture status distinguishes that downstream obligation from an actual measured compliance result.

## Owner decision required

no

## Checks

- Authority and input identity: PASS. HEAD matches the supplied base. All eleven hashes match. L4E13-PANEL.md:14 quotes pcb_requirements.yaml:7693 exactly after whitespace normalization. REQ-024:8769 and D-02a:398 support -20 C as the required operating boundary; the panel's -40 C component rating does not replace it. REQ-016 constrains the panel's own open circuit, so a downstream diode or clamp does not satisfy that clause.
- P1 cold voltage boundary: FAIL. Cold-soaked cells at -20 C under sudden illumination are a reasonable conservative temperature case. However, 1000 W/m2 is not established as maximum irradiance. SunPower 524958 Rev F, section 3.0, PDF p.2 explicitly allows voltage and current above STC. At the proposed acceptance ceilings, the same relative-coefficient model gives 25.2102 V for SunPower and 25.1818 V for Solbian at -20 C and 1250 W/m2.
- P2 voltage arithmetic: PASS. SunPower: (21.4 + 45*0.0589)/0.9 = 26.722778 V under the relative-coefficient assumption; 21.4/0.9 + 45*0.0589 = 26.428278 V with the printed absolute coefficient. Both exceed 25 V. Relative-model STC windows reproduce as 20.078577 to 22.244860 V and 20.094254 to 21.853147 V. These are conditional model windows, not warranted limits.
- P2 controlled-unit acceptance: FAIL. A measured, identified prototype unit is a valid compliance route: L4-ENERGY-ARCHITECTURE.md:221 explicitly permits it. Its uncertainty must cover the cold extrapolation and irradiance envelope, not merely correction of one measurement to STC. With SunPower's absolute -58.9 mV/K coefficient, the proposed lower endpoint gives only 18.774250 V at the modeled noon; the corresponding floor is 20.118679 V. A supported unit-acceptance contract can move selection downstream, while actual unit compliance remains unverified until tested.
- P3 hold screen: PASS. Noon reproduces at 520.720366 W/m2 and 35.654312 C cells. SunPower's modeled band bottom is 18.228302 V; BougeRV nominal/bottom are 18.420440/17.499418 V; Solbian nominal is 19.941865 V. The stated rejections against 18.813 V follow under those assumptions. Voc greater than the hold is a necessary condition for positive current at that condition, not sufficient evidence of useful power or operation over the full envelope. Equality gives zero current.
- P4 input current: PASS. 9.4*(1 + 0.0005*45) = 9.6115 A; multiplying by 1.25 gives 12.014375 A, exceeding 10 A by 2.014375 A. Flagging F2/J_SOLAR for reassessment is correct. The multiplier is a transferred design assumption, not a Solbian instruction; 9.6115 A is nominal because no Isc tolerance is established.
- Read-only completion: PASS. Working tree clean. No files edited, verdict writers run, or outside parties contacted. Full replay and test suite were not run; the reported calculations were independently performed in memory.

## Evidence and minors

- The held SunPower and Solbian documents support the extracted electrical rows. Solbian's positive power tolerance does not establish a Voc maximum.
- MINOR: L4E13-PANEL.md:37 and :86 should distinguish the conservative 26.723 V relative-coefficient scenario from the 26.428 V extrapolation using the printed absolute coefficient. Neither is a warranted maximum without coefficient limits; the rejection is unchanged.
- MINOR: l4e13_panel.out:104 says Solbian passes over its printed band although no band exists. Relabel this as nominal-model compatibility only.
- MINOR: l4e13_panel.out:178 calls Solbian's 9.61 A the band's top. Relabel it nominal at +70 C and keep the transferred 1.25 factor explicit.
- MINOR: L4E13-PANEL.md:122 records fourteen screened documents, but their underlying contents were not independently reviewed here. The screening log is search history, not proof that no other panel can qualify.
