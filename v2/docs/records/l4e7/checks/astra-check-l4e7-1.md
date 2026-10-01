accepted: no

# Layer 4, L4-E7: the one check of the solar stage's component settings by the engineering collaborator (an AI review, read-only)

Collaborator job `cx18-l4e7-check`, run `20261001T140747Z-3274169`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e7 at commit `2d7e331e3b26`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E7: NOT YET. The current-limit arithmetic, hold calculation, energy figures and draft composition reproduce. One blocker: selecting a 16.340 V hold changes REQ-016's retained 17.6 V operating point without an owner ruling. This is a completed read-only AI review; physical compliance remains INCONCLUSIVE.

## Blocking discrepancies

- B1: The proposed 94.2k/7.5k hold and 16.3 V rail declaration change an approved operating point. pcb_requirements.yaml:7693-7702 explicitly requires a 17.6 V hold, retained by D-34 at :976-986. L4E7-STAGE-SETTINGS.md:25 and apply_gen_sch_e_hold.py:27-33 instead select 16.3398 V, 1.2602 V lower. No supplied owner ruling authorizes this change. Preserve the approved nominal ratio for the engineering correction, or identify the optimized hold as an unapproved requirement-change proposal.

## Classification

- **OWNER_REQUIREMENT**: REQ-016 solar operating point and ceiling Evidence: v2/ecad/tools/pcb_requirements.yaml:7693-7702 specifies 17.6 V, at most 25 V cold open circuit and at most 100 W; D-34 at :984 preserves the window.
- **IMPLEMENTATION_DEFECT**: B1: changed hold treated as an engineering selection Evidence: v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md:25 and apply_gen_sch_e_hold.py:27-33 select 16.340 V without reconciling REQ-016. This is a candidate-to-requirement mismatch, not contradictory owner requirements.
- **IMPLEMENTATION_DEFECT**: As-drawn input-current limit absent Evidence: v2/ecad/tools/gen_sch_e.py:484 ties off the input sense; :628 lacks the required IMON_IN filtering capacitor. The proposed correction remains unapplied.
- **COMPONENT_LIMITATION**: Grade and typical-only controller specifications Evidence: v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md:21 and :54-58 cite 8705af pp.3-6: QFN grade choices and guarantees differ; EA2/EA3 gains and FBIN bias lack guaranteed bounds.
- **MODELLING_ASSUMPTION**: Conditional electrical and thermal stacks Evidence: v2/docs/records/l4e7/l4e7_stage_settings.py:75-76, :239, :321-333 and :511-514 define the gain/line floor, inferred resistor heating and inferred U5 junction estimate; L4E7-STAGE-SETTINGS.md:56 discloses cold TCR extrapolation.
- **MISSING_EVIDENCE**: Physical closure and integration obligations Evidence: v2/docs/records/l4e7/L4E7-STAGE-SETTINGS.md:50-58 and :100-108 leave measurements, Kelvin implementation, regeneration and protection-text reconciliation outstanding.
- **DESIGN_OBJECTIVE**: Endurance shortfall Evidence: v2/ecad/tools/pcb_requirements.yaml:7771 identifies REQ-072 as an objective; L4E7-STAGE-SETTINGS.md:79-82 retains the substantial A1/A2 energy gaps.

## Smallest next action

For B1, retain the approved 102k/7.5k nominal hold ratio, update the hold draft and dependent energy/bench rows, and keep 94.2k as an explicitly unapproved optimization. If retaining 16.340 V is intended, obtain the single REQ-016 decision below before release.

## Closure criterion

The selected hold, generator draft, requirement trace and energy/bench tables must agree: either preserve the existing 17.6 V nominal operating point and reproduce the revised calculations, or cite a recorded owner ruling authorizing 16.340 V and reconcile REQ-016. In both cases retain the reproduced <=100 W conditional corner check and leave physical compliance open until the specified measurements pass.

## Owner decision required

yes

For the candidate as written: approve or reject replacing REQ-016's 17.6 V nominal hold with 16.340 V, retaining the 25 V and 100 W ceilings. The modeled nominal benefit is 25.0443 Wh/day. This decision is unnecessary if the requirement-preserving hold alternative is adopted; the I-grade and input-current-limit corrections themselves need no owner decision.

## Checks

- F1: circuit as drawn: PASS. gen_sch_e.py:484 ties CSPIN, CSNIN and VIN to PV_P; :628 gives IMON_IN R16 10k without a capacitor; :575 gives R8 102k/R9 7.50k, both 1%. inputs/lcsc-C674164-2026-10-01.json:8 identifies LT8705AEUHF#TRPBF. The reported legacy hold band reproduces, with the grade qualification noted under MINOR.
- F2: grade and junction estimate: PASS. 8705af p.3 offers QFN grades E and I; p.6 Note 3 guarantees E at 0 to 125 C and assures its colder operation by characterization, while I is guaranteed at -40 to 125 C. H and MP are TSSOP only. Infineon Rev.2.1 p.3 and Rev.2.4 p.4 support 49/32 nC. (4.2 mA + 235 kHz × 162 nC) × 30.15 V = 1.27444 W; 62.1 C + 34 C/W × 1.27444 W = 105.431 C. The method is sourced and labelled INFERRED at L4E7-STAGE-SETTINGS.md:21; it is not a demonstrated junction bound.
- F3: achieved current and power: PASS. Nominal current is 3.471264 A. At 25 V under stack A, cold minimum/maximum are 3.139195/3.849897 A; hot minimum/maximum are 3.139792/3.849164 A, using R59 at 70.142448 C and R16 at 62.1 C. Maximum powers are 96.247433/96.229094 W. The worst-power expression increases with voltage throughout the stated envelope. Stack C gives 99.673940/99.654948 W; 22.6k gives 102.320163 W cold. These reproduce l4e7_stage_settings.out:91-98.
- F4: input-sense topology and operating conditions: PASS. apply_gen_sch_e_input_limit.py:32-47 correctly inserts R59 between PV_P and TRK_VIN, leaves CSPIN upstream, and moves CSNIN, VIN, C11-C15, C64 and Q3's drain downstream. The stated stack-A conservative sense voltage is 57.490 mV, IMON current 60.940 uA, and maximum fault sense voltage 76.741 mV. Including stack-C R16 drift gives 58.190 mV at regulation and 77.514 mV at fault, still below 100 mV. Maximum regulation voltage is 1.253675 V under stack C, below the 1.55 V minimum fault threshold. C65's 100 nF exceeds the calculated 25.355 nF minimum.
- F5: hold and hourly energy: PASS. The proposed hold computes to 15.762911/16.339800/16.921141 V with the stated EA3 and bias assumptions. Half EA3 gain gives 15.537979/17.148223 V; adding resistor drifts gives 15.253097/17.469703 V. The nominal trace sums to 375.043397 Wh with no limited hours, reproducing 375.0 Wh. Arithmetic correctness does not resolve the REQ-016 mismatch.
- F6: unresolved evidence: INCONCLUSIVE. L4E7-STAGE-SETTINGS.md:50-58 identifies all requested uncertainties and measurements. Cold EA2 break-even is 25.0264 V/V under stack A and 55.1917 V/V with drifts and line ×2. The 61.5848× line and 882.027 ppm/K cold-TCR figures reproduce without drifts. EA3/bias receive a sensitivity band rather than explicit parameter break-even limits. No bench evidence is supplied or claimed; see MINOR qualifications.
- F7: draft scope, refusal and composition: PASS. All three drafts parse, reject second applications and unexpected input, and refuse writing the unreleased tree generator. All 24 permutations with R10 115k to 232k produce identical text. R10, C26 and C27 are otherwise untouched. Kelvin taps, regeneration and the 225 uF PV_P requirement texts are explicitly owed at L4E7-STAGE-SETTINGS.md:100-108.
- F8: energy consequences and L4-E5: PASS. Nominal least additions reproduce: A1 1319.3/2030.8 Wh and A2 936.7/1656.0 Wh for 48/72 h. Reductions against the previous nominal trace are 42.2/63.3 Wh and 42.5/63.7 Wh respectively. New upper-corner additions reproduce as A1 1326.9/2042.1 Wh and A2 944.3/1667.4 Wh. L4-E5's raised output and source-control line remain compatible; its combined energy consequences have not been rerun by this record, as :89 explicitly states.
- Revision and read-only integrity: PASS. All 12 non-null L4-E7 pins matched, including held maker documents. HEAD matches the requested base; the worktree is unchanged. No generator, gate or verdict writer was run.

## Evidence and minors

- MINOR M1: L4E7-STAGE-SETTINGS.md:15 calls 16.695 V the drawn lower hold corner, but l4e7_stage_settings.out:84 correctly identifies it as the legacy H/MP-minimum calculation. With the identified E-grade 1.184 V FBIN minimum and otherwise identical assumptions, the lower corner is 16.723678 V. Label the legacy band consistently or report the E-grade calculation.
- MINOR M2: L4E7-STAGE-SETTINGS.md:55-57 should state each break-even's stack explicitly. The 882 ppm/K cold-TCR allowance belongs to stack A; with EA2 65 V/V, line ×2 and drifts, it falls to 122.295 ppm/K. Give EA3 and FBIN bias explicit acceptance limits or identify their row as an energy sensitivity rather than a parameter break-even.
- MINOR M3: L4E7-STAGE-SETTINGS.md:93 starts the bench sweep at 15.763 V, although :35 admits 15.538 V and l4e7_stage_settings.out:83 reaches 15.253 V with hold-resistor drift. Align the eventual sweep and hold acceptance with the selected, explicitly conditioned envelope.
- A requirement-preserving alternative exists: retain the 102k/7.5k nominal ratio, 17.593 V. With the proposed precision resistor specifications, its calculated band is 16.970441 to 18.220502 V. The filed catalogue lists RT0603BRD07102KL, C861068. This alternative leaves the 25 V current-limit result unchanged; its nominal modelled harvest remains 349.9991 Wh/day.
