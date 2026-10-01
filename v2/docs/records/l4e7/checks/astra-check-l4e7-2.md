accepted: yes

# Layer 4, L4-E7: the targeted recheck of the author's fixes by the engineering collaborator (an AI review, read-only; the second and last run on this issue)

Collaborator job `cx19-l4e7-recheck`, run `20261001T144407Z-3391302`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e7 at commit `379ea32f57d8`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E7: ACCEPT. B1 is resolved and the targeted calculations, drafts and output reproduce. One nonblocking M2 wording residue remains. This is a read-only AI review of a prototype candidate; physical compliance remains INCONCLUSIVE.

## Blocking discrepancies

- none

## Classification

- **OWNER_REQUIREMENT**: REQ-016 operating point Evidence: pcb_requirements.yaml REQ-016 requires the 17.6 V operating point; D-34 retains it. The revised candidate preserves it.
- **IMPLEMENTATION_DEFECT**: B1 candidate mismatch Evidence: Resolved: the hold draft retains 102k/7.5k and the 17.6 V declaration; 16.340 V is only a proposal.
- **IMPLEMENTATION_DEFECT**: Residual M2 threshold wording Evidence: The unqualified 25 V/V sentence at L4E7-STAGE-SETTINGS.md:80 disagrees slightly with the computed threshold and omits its stack; this is a documentation minor.
- **MODELLING_ASSUMPTION**: Conditioned bands and power floor Evidence: Half-typical gains, doubled line regulation, stacked drifts and cold shunt-TCR extrapolation remain explicitly conditioned calculations.
- **COMPONENT_LIMITATION**: Typical-only specifications Evidence: 8705af pp.4–5 provides typical-only EA2/EA3 gains and FBIN bias; HoJLR Ho-A0 p.4 tests TCR only from +25 to +125 C.
- **MISSING_EVIDENCE**: Physical compliance Evidence: The drafts remain unapplied and bench rows remain planned. This targeted review supplies no physical measurements.
- **DESIGN_OBJECTIVE**: Energy shortfall Evidence: The reproduced A1/A2 additions retain the stated endurance shortfall against REQ-072; no requirement is relaxed.

## Smallest next action

Replace the residual M2 sentence with the stack-A threshold 25.0264 V/V and the threshold 55.1917 V/V under stack C's other terms, retaining acceptance at or above 65 V/V.

## Closure criterion

The prose names the same stacks and thresholds as the reproduced calculation. B1's targeted closure is already evidenced by the retained ratio, unchanged declaration, matching bands, energy rows and draft checks; physical closure remains subject to the specified bench measurements.

## Owner decision required

no

No owner decision is needed for this retained candidate or the wording correction. Only adopting the separate 16.340 V proposal would require an explicit REQ-016 ruling; nothing else in this targeted recheck needs the owner.

## Checks

- R1: requirement-preserving hold: PASS. R8 is RT0603BRD07102KL/C861068, 102k; R9 is RT0603BRD077K5L/C728597, 7.5k; both 0.1%, 25 ppm/K. Nominal remains 17.593 V and the panel declaration remains 17.6 V. Recomputed bands: typical EA3 16.970441–18.220502 V; typical EA3 plus drifts 16.657544–18.564035 V; half EA3 16.728277–18.465020 V; half EA3 plus drifts 16.419845–18.813164 V. Sources: 8705af pp.2,4; YAGEO RT V.16 pp.2,7,8. The 16.340 V proposal supplies no selected setting or draft.
- R2: power corners and RIMON_IN selection: PASS. Cold stacks A/B/C/D reproduce as 96.247433/95.290857/99.673940/98.693057 W; hot results are 96.229094/95.272699/99.654948/98.674252 W. Each power expression increases across 16.419845–25 V, so 25 V remains the maximum. RIMON_IN 23.2k gives 3.471264 A nominal and passes stack C; the next larger current setting, 22.6k, reaches 102.320163 W.
- R3: M1, M2 and M3 corrections: PASS. The drawn E-grade lower corner is 16.723678449 V; 16.695 V is labelled legacy H/MP. Cold TCR break-evens reproduce as 882.027384 ppm/K for stack A and 122.294652 ppm/K for stack C. EA3 and FBIN bias have explicit energy-sensitivity rows. Bench 7b.9 starts at 16.420 V; 7b.12 accepts 16.420–18.813 V under the stated conditions. The residual M2 prose issue is listed as MINOR.
- R4: energy and executable record: PASS. All ten predicates pass and l4e7_stage_settings.out reproduces byte for byte. Nominal harvest is 349.999084 Wh/day. A2 least additions are 979.208768/1719.740309 Wh; A1 additions are 1361.497906/2094.078896 Wh, matching the replay. Upper-corner harvest is 307.864122 Wh/day; conditioned upper-end harvest is 240.012507 Wh/day. The adapter preserves pixel analysis and calculations; the dependency's complete 27,918-byte output also matches.
- Draft scope, refusal and composition: PASS. The hold draft changes one R8/R9 line only: tolerance/TCR annotations, part fields and explanatory comment. Values, connections and panel declaration remain unchanged. All drafts parse, reject repeated application and unexpected input, retain their release guard and compose identically. No draft carries 94.2k or C861602. Two scratch-file fixture tests were not run; their relevant patch/refusal/composition behavior was checked in memory.
- Unmodified replay in this sandbox: INCONCLUSIVE. The unchanged r11_dep.py dependency requires a temporary PNG and fails because no writable temporary directory exists. This is an execution-environment limitation; the subsequent memory-adapted run reproduces the records without changing files or calculation results.
- Revision and read-only integrity: PASS. HEAD matches the requested base; all 12 non-null L4-E7 pins match; the worktree remains clean. No generator, gate or verdict writer was run.

## Evidence and minors

- B1 is resolved by preserving REQ-016 and D-34. L4E7-STAGE-SETTINGS.md:29 and apply_gen_sch_e_hold.py:24 agree on the retained ratio and precision parts.
- MINOR M2 residual: L4E7-STAGE-SETTINGS.md:80 still says the corner passes for any EA2 gain at or above 25 V/V without naming its stack. The cold threshold is 25.026426 V/V under stack A and 55.191656 V/V with stack C's other terms; exactly 25 V/V gives 100.004912 W under stack A. Replace that sentence with the stack-specific thresholds and retain the 65 V/V bench acceptance. The selected design floor is unaffected.
- The 16.3398 V proposal remains explicitly unadopted at L4E7-STAGE-SETTINGS.md:107. Its modeled nominal benefit is 25.044313 Wh/day; no selected circuit or energy claim relies on adopting it.
