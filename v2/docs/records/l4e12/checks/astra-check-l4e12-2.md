accepted: no

# Layer 4, L4-E12: the targeted recheck of the electronics against the inside air at the margins by the engineering collaborator (an AI review, read-only)

Collaborator job `cx32-l4e12-recheck`, run `20261002T033409Z-367504`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e12 at commit `39fe74c4bf5b`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E12: NOT YET. The revised E3-O radio configuration and conductance calculations check out conditionally. The rating correction remains incomplete, and the SGP41 shutdown does not establish bounded protection or full in-envelope operation and recovery. Read-only AI review completed; no owner decision is currently forced.

## Blocking discrepancies

- B2 remains incomplete: l4e12_thermal.py:392-393,423 treats SGP41 Table 5's +55 C as its powered operating range and calls it the only powered statement. Sensirion version 1.0, December 2021, p.6 Table 4 instead guarantees gas specifications only under recommended conditions ending at +50 C; p.7 Table 5 is explicitly absolute ratings. The claimed function at 52.55 C therefore lacks maker support. The all-part claim is also unsupported by P11, which checks only selected PARTS keys and misses sgp_op and the general screen. For example, CSD17577Q5A's +150 C comes from Absolute Maximum Ratings, yet script:807-825 gives it an ordinary NOT REACHED result. Correct the rating provenance throughout and distinguish exclusion-screen clearance from supported operation or survival.
- B3 protection bound is unsupported: record:182-186 treats BME688 ±0.5 C as a bounding error. Bosch BST-BME688-DS000-03 revision 1.3, February 2024, p.14 Table 10 places it in the Typ column, with no maximum specified; footnote 19 also identifies PCB temperature and self-heating effects. The proposed 53.75 C threshold therefore does not establish shutdown before the SGP41's local +55 C. Obtain a defensible maximum reference-error bound, or use a reference with one, and bound placement error and local thermal response before claiming protection.
- B3 in-envelope recovery fails under the stated model: record:184-187 requires the SGP41 to remain off after every start or shutdown until the reference reads at most 50 C, but predicts 52.55 C bay air at +40 C ambient. Even with zero reference error and zero gradient, a warm restart or return from the margin leaves the sensor off. With the same heat and conductance, cooling below approximately +37.45 C ambient is needed to reach the nominal restart threshold. Provide a local thermal/control solution that preserves specified sensing throughout the use envelope, including startup and recovery; do not claim closure from the positive shutdown-only margin.

## Classification

- **OWNER_REQUIREMENT**: In-envelope sensing, recovery and named margin configurations Evidence: D-02a; pcb_requirements.yaml REQ-041, REQ-042 and REQ-051; TEST-PLAN.md:26,28. CHO-001 binds the SGP41 device selection.
- **IMPLEMENTATION_DEFECT**: Incomplete application of the corrected rating rule Evidence: l4e12_thermal.py:392-393,423,807-825,1037-1038; Sensirion Tables 4-5 and TI CSD17577Q5A absolute-rating table.
- **COMPONENT_LIMITATION**: SGP41 gas-performance range Evidence: Sensirion version 1.0 p.6 guarantees gas specifications only within recommended conditions, including temperature at most +50 C.
- **MODELLING_ASSUMPTION**: Treating BME688 typical accuracy as a worst-case bound Evidence: Bosch revision 1.3 p.14 Table 10 lists ±0.5 C as typical; the shutdown calculation consumes it as a maximum.
- **IMPLEMENTATION_DEFECT**: SGP41 startup and recovery deadband inside the use envelope Evidence: The 50 C enable condition conflicts with the record's own 52.55 C bay prediction at +40 C ambient.
- **COMPONENT_LIMITATION**: PCM2912A and TLV75533 operating limits Evidence: Held TI sheets support +70 C PCM2912A operation and +125 C TLV755P recommended junction with 500 mA output.
- **MISSING_EVIDENCE**: Conductance, reference placement, fans and exposure recovery Evidence: No T-H1 measurement, bounded reference calibration, fitted-fan qualification or Sensirion duration/recovery confirmation exists.

## Smallest next action

Withdraw the SGP41 function-preserved and bounded-shutdown claims. Correct its recommended-versus-absolute rating treatment, add startup and cooling-recovery cases, and specify the reference-error and local-temperature evidence needed for a compliant sensor path.

## Closure criterion

Every screened limit identifies its rating category, with unsupported operation or survival remaining INCONCLUSIVE. The revised SGP41 path must support specified sensing at every in-envelope state, including warm startup and recovery, using local temperature within the maker-supported functional range; demonstrate cutoff before +55 C with bounded error, gradient, response and conservative rounding; and retain duration/recovery evidence as an explicit dependency. The E5-only hold must have a verified nonempty trigger interval under its stated loads and placement. Proposed regulator changes must retain their thermal and peak-current obligations. Physical qualification remains unperformed.

## Owner decision required

no

## Checks

- Revision and read-only state: PASS. HEAD matches the specified base; worktree unchanged. No verdict writer, generator or test suite was run.
- Pinned inputs: PASS. All 63 inputs match. Requirements SHA256 b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50; owner-instruction SHA256 f39c7f2b08dae370c68fa9e5ed189317722ff64c784423d246b3f17f1befee62.
- R1 heat and conductance: PASS. Including ballasts: E3-O 27.086383 W requires 1.805759 W/K; E5 hold 21.586842 W requires 2.158684 W/K. At G=2.159, air temperatures are 67.545800 C and 69.998537 C. W4's low-case cap is 2.100244 W/K, leaving a 0.058440 W/K gap.
- R1 temperature-based hold restriction: INCONCLUSIVE. At the exact modeled conductance line, the window is 2.452364 K. With TMP117 maximum error ±0.2 C and the assumed 61-second response, the permitted symmetric offset is ±0.899099 K. The approximately -3.84 K window across the existing exhaust spread does not work. Restriction to E5 is therefore conditional on measured temperature separation, reference placement/calibration, load and response bounds.
- R2 rating-rule application: FAIL. PCM2912A and regulator corrections are supported, but the SGP41 still uses an absolute rating as its powered operating criterion. Other absolute-only rows also remain indistinguishable from operating clearance.
- R3 SGP41 protection and recovery: FAIL. BME688 ±0.5 C is typical, not a maximum bound. At +40 C ambient the modeled bay is 52.545800 C, above both the 50 C restart threshold and the SGP41 recommended operating maximum.

## Evidence and minors

- R1: L4E12-ELECTRONICS-THERMAL.md:61-71 withdraws the extra radio shedding in E3-O and retains C1's documented action. A separate SGP41 protective cutoff does not itself change the explicitly named monitor/radio configuration. Its unavailable channel must be recorded consistently with TEST-PLAN.md:17 instrumentation, while required logging continues.
- R1: The thermal results use the stated plan loads, no charging, a kit initially stabilized at +55 C, and parts outside the cooler exhaust. They do not prove the hold cannot activate during every actual E3-O transient. These remain explicit model and verification conditions.
- R2: PCM2912A SLES230A, revised August 2015, p.5 supports +70 C recommended free-air operation. Keeping it at 67.55 C in E3-O, outside the exhaust, addresses that collision. Turning it off in E5 is a credible proposal, but its absolute storage rating alone is not a prolonged-survival guarantee.
- R2: TLV755P SBVS320A, revised May 2018, p.4 supports +125 C recommended junction, 231.1 C/W DBV, 100.2 C/W DRV and 500 mA output. U13 and U5 thermal collisions reproduce. U13 at declared 0.35 A reaches about 129.6 C in DRV at 70 C air; the corresponding current ceiling is 0.322884 A. A buck or justified load reduction is needed. U5's DRV change addresses typical-load heating, while its separately identified 0.72 A peak still needs resolution.
- R3: Default-off supply switching and a separately isolated bus address the previous late-shutdown and back-powering concerns in principle. The circuit remains proposed. Sensirion's short-term exposure duration and subsequent recovery remain unconfirmed.
- R4: Treating the fans as architecture-level is justified because their operation underpins the assumed conductance. The other ten unrated lines are appropriately assigned downstream evidence work; that assignment does not establish their feasibility.
- R4: No immediate owner decision is forced. The outstanding issues support engineering correction and bounded evidence gathering, not a demonstrated contradiction between owner requirements.
- MINOR: The exclusive owner-question condition at record:231-237 is too strong. Record:213-216 itself proposes an owner-controlled SGP41 replacement when conductance lies between 1.806 and 2.159 W/K. For example, G=2 gives E3-O air 68.543 C but E5 hold air 70.793 C. Replace 'only if' with a non-exclusive escalation condition after compliant engineering routes are assessed.
- MINOR: Round protection settings conservatively. The assumed 61 seconds at 15 K/h gives 0.254167 K, so 53.75+0.5+0.5+0.254167=55.004167 C. The unrounded shutdown value is 53.745833 C. Likewise, ±0.90 K slightly exceeds the exact-line hold offset allowance of ±0.899099 K.
