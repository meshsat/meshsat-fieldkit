accepted: no

# Layer 4, L4-E5: the one check of the source-control decision by the engineering collaborator (an AI review, read-only)

Collaborator job `cx15-l4e5-check`, run `20261001T113719Z-2902583`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e5 at commit `0f894814c952`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E5: NOT YET. The core H3 mechanism, calculated current envelopes, R11 consequence and patch scope check hold conditionally. Correct the inconsistent startup acceptance, add telemetry verification, and restrict the 49.7 W conclusion to H3. Read-only AI review completed.

## Blocking discrepancies

- B1: Inconsistent startup acceptance. v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:166 and apply_fw_a16.py:63 require HIZ below VIN_RAW 8.75 V. The proposed knee instead reaches the 0.4 V falling threshold at 8.50848 V nominal and the 0.8 V rising threshold at 8.66949 V nominal. At VIN_RAW 8.70 V the pin is 0.87578 V, so HIZ is not the specified state. Correct V-A09 to distinguish zero-current target, HIZ entry and HIZ exit.
- B2: Missing telemetry verification. v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:121 and apply_fw_a16.py:37 define unchanged settings during stale telemetry and a three-reading diagnostic fallback, but V-A06 through V-A09 at apply_fw_a16.py:53 do not test either. Existing FW-A15 item 10 at v2/docs/HW-FW-CONTRACT.md:93 also does not cover them. Add one bounded fault-injection verification row.
- B3: Unsupported universal 49.7 W claim. v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:107 attributes H3's boundary to any source-blind mechanism. The calculation at l4e5_source_control.py:400 evaluates only the selected line. An illustrative source-blind target held at H3's 9 V current through 12 V, then increasing with the same slope, preserves that 9 V target and lowers vehicle demand; under the same error model its 12 V boundary is 38.74834 W and its 40 W lower-corner settling point is 12.34226 V. Restrict the numerical conclusion to H3 and remove the universal necessity claim for source identity.

## Classification

- **IMPLEMENTATION_DEFECT**: B1: Startup acceptance contradicts the proposed knee Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:166; apply_fw_a16.py:63; l4e5_source_control.py:346. The draft verification criterion disagrees with its own transfer function and SLUSE66A pp.6 and 17.
- **MISSING_EVIDENCE**: B2: Telemetry behavior lacks verification Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:121; apply_fw_a16.py:37 and :53; v2/docs/HW-FW-CONTRACT.md:93.
- **IMPLEMENTATION_DEFECT**: B3: H3-specific boundary generalized to all controls Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:107; l4e5_source_control.py:400. REQ-015 at v2/ecad/tools/pcb_requirements.yaml:7648 does not prescribe this current-versus-voltage line.
- **MISSING_EVIDENCE**: Pin accuracy, low-voltage behavior and dynamic response Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:145 explicitly leaves 10 mOhm accuracy, behavior below the specified regulation range, response and composite stability INCONCLUSIVE.
- **MODELLING_ASSUMPTION**: Efficiency and network tolerance assumptions Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:151; l4e5_source_control.py:74 and :81. The 0.93 efficiency and proposed tolerance bounds require engineering evidence.
- **IMPLEMENTATION_DEFECT**: Undrawn source identity and slow existing telemetry Evidence: v2/ecad/tools/gen_sch_e.py:362, :363 and :484; v2/docs/HW-FW-CONTRACT.md:155. The present circuit and reporting path cannot provide the required source-aware transient control.
- **COMPONENT_LIMITATION**: Inferred pin path exceeds R11's full-tap coordination Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:129. The conditional 5.094873 A path requires V-A07 evidence or the carried 7 mOhm remedy.
- **MISSING_EVIDENCE**: M1: POR interpretation Evidence: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:119; apply_fw_a16.py:27; held SLUSE66A p.80.
- **MODELLING_ASSUMPTION**: M2: Nominal capacitance described as an upper bound Evidence: v2/docs/records/l4e5/l4e5_source_control.out:54 supplies no effective-capacitance bound.
- **OWNER_REQUIREMENT**: Preserved vehicle and solar functions Evidence: v2/ecad/tools/pcb_requirements.yaml:7648 and :7693 define REQ-015 and REQ-016. Neither requires a 12 V minimum on the shared bus during solar operation.
- **DESIGN_OBJECTIVE**: Endurance objective remains unmet Evidence: v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md:11; v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:83.

## Smallest next action

B1: Correct V-A09's HIZ entry/exit criteria in the page and draft. B2: Add a telemetry fault-injection verification row. B3: Rewrite the 49.7 W finding as H3-specific, retaining the engineering restatement of bench 7b.7.

## Closure criterion

B1: The corrected criteria agree with the pin transfer function and TI's 0.4/0.8 V thresholds; prescribe rising and falling VIN_RAW sweeps, with actual behavior remaining INCONCLUSIVE until measured. B2: Specify tests for absent and older-than-3 s telemetry without setting changes, the three-reading diagnostic trigger, fallback capped at 4.70 A, and stale fallback at 1.55 A. B3: The text attributes 49.7195 W only to H3's stated model and makes no universal source-blind impossibility claim. Independently inspect the corrected draft and repeat its in-memory scope and second-application checks.

## Owner decision required

no

## Checks

- S1: ILIM_HIZ maker evidence: PASS. TI states continuous pin reading, the lower pin/register setting, EN_EXTILIM enabled at reset, the current-setting equation, HIZ below 0.4 V and exit above 0.8 V. Page 10 specifies regulation from 1.15 to 4 V and the accuracy rows for 5 mOhm only. The decision correctly lists the inferred ±0.2 A at 10 mOhm, behavior below 1.15 V, loop response and stability as INCONCLUSIVE at L4E5-SOURCE-CONTROL.md:143.
- S2: Independent envelope arithmetic: PASS. At 9 V: U3 maximum 1.792806 A and front-end input 4.629431 A. At 24 V: 4.442850 A and 4.193738 A. Both are below 4.80 A under the model. Required efficiency at 9 V is 0.896952; C-8 dependence is explicit at L4E5-SOURCE-CONTROL.md:100 and :151. At 50 W at VBUS20, nominal settling is 14.03247 V, with modeled corners 12.07670 to 16.20252 V. R10 232 k gives 28.27505/29.20940/30.14514 V.
- S3: Source identity and response times: PASS. Q7 permits back-feed from DC_HS to HS_S and DC_P, so PGD cannot establish vehicle presence; U5 pins 25-28 are unconnected. The named capacitors total 129 uF. Their nominal energy from 15.0875 to 8.31 V is 10.2282 mJ, giving 10.228/3.409/1.023 ms at 1/3/10 W deficits. The nominal 100 nF timer gives 3.133/4.706/8.157 ms. The drawn 1 s telemetry path cannot provide transient protection.
- S4: Startup, source changes and telemetry: FAIL. Source-change behavior and V-A08 are defined, with response explicitly INCONCLUSIVE. V-A09 contradicts the knee's HIZ thresholds. Stale telemetry and diagnostic fallback have behavior definitions but no corresponding verification procedure. See B1 and B2.
- S5: L4-E4 coordination consequence: PASS. Specified firmware writes remain at or below 4.70 A. The inferred crossover band is 26.49975 to 27.24294 V; pin-path maximum is 5.015779 A in board current and 5.094873 A through R11. Full-tap margins reproduce approximately -0.034/-0.067/-0.109 A. The allowable tap resistance becomes 0.209055 mOhm. At 7 mOhm it becomes 0.992054 mOhm, with highest permitted current 8.29952 A. L4E5-SOURCE-CONTROL.md:129 carries V-A07 or the resistor change into fault handling appropriately.
- S6: Solar acceptance and owner authority: FAIL. 49.7195 W is H3's modeled worst-case 12 V boundary, not a universal source-blind limit. A-2 explicitly calls its closure statements engineering acceptance, not new owner requirements, at L4-ENERGY-ARCHITECTURE.md:154. Rewording that bench acceptance needs engineering correction, not an owner requirement change. See B3.
- S7: Draft patch scope and repeat refusal: PASS. Only the named heading, FW-A16, FW-C01, FW-E04, added FW-A18, V-A06 through V-A09 and change-record row changed. Second application refused with SystemExit 3. The contract's SHA-256 remained 1c211e467d81b8b70546bc4435c65d4bd2dcd0d2fc3606714a746b4d8d0ac1fa.
- Revision and read-only checks: PASS. HEAD matches the requested base, the working tree is clean, and all 17 pinned input hashes match. No verdict writer ran.
- Full author-script and energy replay reproduction: NOT_RUN. The complete author-script and energy replay were not executed. Their full byte-for-byte reproduction is not claimed by this review.

## Evidence and minors

- MINOR M1: v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:119 and apply_fw_a16.py:27 present an unqualified 3.25 A POR value. Held SLUSE66A p.80 distinguishes the 5 mOhm-mode 3.2 A default and contains conflicting 2000h/4100h reset annotations. Record raw IIN_HOST and RSNS_RAC before and after FW-A01 in V-A09; distinguish POR from subsequent adapter-removal reset. This does not invalidate the 4.70 A firmware ceiling.
- MINOR M2: v2/docs/records/l4e5/l4e5_source_control.out:54 calls nominal capacitance an upper bound. Nominal values alone do not establish that bound. Call the collapse times nominal estimates pending effective capacitance evidence; the large mismatch against 1 s telemetry remains.
- The 25 V C26/C27 replacement and 35 V polymer derating obligation are explicitly carried at v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:33 and :155. The proposed hardware remains undrawn.
- REQ-072 remains a design objective, and its modeled shortfall is retained at v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md:83.
