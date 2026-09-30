accepted: no

# Layer 4, L4-E2: the focused check by the engineering collaborator (an AI review, read-only)

Collaborator job `cx8-l4e2-check`, run `20260930T221538Z-809994`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e at commit `0e641bd35bf5`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E2: NOT YET. This read-only AI review reproduced the headline calculations but found two blocking discrepancies: the reported kit energy account double-counts solar during stopped hours, and O-2's current-limit proposal does not establish the required 100 W ceiling across input voltage. Both need engineering corrections, not an owner decision.

## Blocking discrepancies

- B1: The kit service-energy account does not conserve energy. v2/docs/records/a1elec/energy_two_pack.py:257-280 sets actual load to zero while stopped, subtracts available solar from the unserved-energy counter, and also charges with that solar. l4e_replay.py:251-255 converts this inherited counter into 'served' energy and checks only storage closure. Thus l4e_replay.out:128-135 and L4-ENERGY-ARCHITECTURE.md:25-26,56 understate unserved service energy. This misses the explicit kit-balance closure at ASTRA-L4E1.md:37. Smallest correction: preserve the pinned model and legacy reproduction rows, but derive a separate service ledger from traced load flows, including cutoff losses; use it for the new served/unserved claims and label inherited shortfall values as legacy model metrics.
- B2: O-2's proposed fixed input-current limit is insufficient to establish its claimed power ceiling. L4-ENERGY-ARCHITECTURE.md:162-168 sizes approximately 5.68 A at 17.6 V, while 8705af p.29 permits input voltage to rise when another control loop limits current. At a loaded 20 V, that current corresponds to 113.6 W; this is an illustrative electrical point, not a claimed panel measurement. Smallest correction: specify a voltage-aware power bound, or a conservative current bound using the maximum permitted loaded voltage and all tolerances. Keep the ideal 100 W replay explicitly conditional until the selected mechanism and panel establish it, and expand closure beyond the single 17.6 V point.

## Classification

- **IMPLEMENTATION_DEFECT**: B1: inherited stopped-hour double counting propagated into the new kit account Evidence: v2/docs/records/a1elec/energy_two_pack.py:257-280; v2/docs/records/l4e/l4e_replay.py:251-255; v2/docs/records/l4e/l4e_replay.out:128-135. The 72 h, 06 UTC account overstates traced service by 36.103263 Wh.
- **COMPONENT_LIMITATION**: B2: input-current regulation does not independently regulate input power Evidence: v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:162-168; v2/vendor/power/lt8705a.pdf, 8705af pp.29-31. FBIN provides a lower-voltage regulation action; IMON_IN limits current.
- **OWNER_REQUIREMENT**: Retained solar window and pack authority Evidence: v2/ecad/tools/pcb_requirements.yaml:7675-7689 requires at most 25 V open circuit, the 17.6 V operating point and at most 100 W input; D-34 preserves this at lines 976-986. D-06 specifies one 4S3P pack at lines 475-484; the comparison labels A2 a proposal at L4-ENERGY-ARCHITECTURE.md:57.
- **DESIGN_OBJECTIVE**: Unmet 48-72 hour endurance target Evidence: v2/ecad/tools/pcb_requirements.yaml:7732-7764 identifies REQ-072 as an objective. L4-ENERGY-ARCHITECTURE.md:54-56 quantifies the missed target; its storage additions independently reproduce.
- **MISSING_EVIDENCE**: Conditional stimulus and remaining source evidence Evidence: v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:33-39,172-189 identifies the missing compliant panel trace, efficiencies, thermal evidence and fault-current derivation. These remain engineering obligations, not demonstrated contradictions.
- **MODELLING_ASSUMPTION**: M1 and the efficiency sensitivity's actual scope Evidence: v2/docs/records/l4e/l4e_replay.py:134-150 retains U3/U3B and path losses while setting only eta_st, eta_fe and chg_eta to 1.00; l4e_replay.out:157,160 overstates that scope in its parenthetical.

## Smallest next action

B1: add flow-derived served/unserved energy and cutoff-loss accounting to the L4 harness, preserving legacy outputs solely for reproduction and historical comparison. B2: amend O-2 to require a power bound across loaded input voltage, with a tolerance derivation and voltage-sweep closure. Correct M1's label alongside these edits.

## Closure criterion

B1: for both architectures, both starts and both horizons, independently summed node energy plus initial storage equals served energy plus spill, charge/discharge losses and final storage within 1e-6 Wh; stopped-hour solar is counted once. The current A2 corrected trace must yield 270.132086/286.306461 Wh unserved at 48 h and 500.372955/516.547330 Wh at 72 h, while preserving the original reproduction rows and uninterrupted-service thresholds. B2: the revised architecture states and derives V_in times I_in,max <= 100 W across the selected source's permitted loaded-voltage and tolerance envelope, and specifies matching later bench sweeps. If the mechanism reduces available power, show that consequence separately from the ideal 100 W screening case. No Layer 3 or registry change is needed.

## Owner decision required

no

## Checks

- Reproduction order and common assumptions: PASS. v2/docs/records/l4e/l4e_replay.py:98 checks runtime.out before proceeding; lines 288-366 compare the claimed runtime, three_cases and energy_budget rows. Lines 171-204 and 438-464 apply the same model and named assumptions while changing the stage clip. Full scripts were not rerun.
- Independent headline calculations: PASS. A2 corrected least additions reproduced as 278.782921 Wh at 48 h and 515.775986 Wh at 72 h, with lid counts 17.828301P and 25.333230P. Setting the three undocumented efficiencies to 1.00 reproduced the legacy 48 h shortfall metric, 111.373747 Wh. Printed battery arithmetic gives A1 107.9/42.8 = 2.52103 h and A2 544.4/42.825 = 12.71220 h. These match l4e_replay.out:36-37,84-86,160; the shortfall metric has the accounting defect described in B1.
- Kit energy conservation: FAIL. At 72 h from 06 UTC, A2 reports 2619.130308 Wh served, but its traced load flows total 2583.027045 Wh. The 36.103263 Wh difference is solar credited to service during stopped hours while also offered to charging. Flow-derived unserved energy is 270.132086/286.306461 Wh at 48 h and 500.372955/516.547330 Wh at 72 h, for 06/18 UTC starts. The independently assembled kit balances close within 1.6e-12 Wh. See l4e_replay.out:128-135 and l4e_replay.py:251-255.
- Maker source: R138: PASS. Section 8.3.8.2 explicitly recommends a 5 mOhm sense resistor and gives approximately 3.8-4.5 A OCP thresholds for the 3 A configuration. It supports the proposed remedy at L4-ENERGY-ARCHITECTURE.md:151-155, without establishing implementation or bench performance.
- Maker source: LM5176 hiccup: PASS. The pages support selectable hiccup protection after 128 consecutive cycle-by-cycle current-limit events and restart after 4000 oscillator cycles. This supports B-2 at L4-ENERGY-ARCHITECTURE.md:114-118. It does not itself establish the proposed FET/copper thermal performance.
- Maker source: LT8705A input limit: FAIL. Page 31 supports the input-current limiter and its typical 1.208 V IMON_IN threshold. Page 29 describes FBIN as reducing current when input voltage falls below its set point, not clamping input voltage above it. Consequently the source supports the limiter mechanism but not O-2's inference that approximately 5.68 A guarantees at most 100 W throughout the permitted input range.
- Scope, labels and Layer 3 carry-forward: PASS. Only the five l4e record files differ from the branch's stated base; the worktree remains clean. The 100 W solar results are globally identified as conditional screening stimuli at L4-ENERGY-ARCHITECTURE.md:33-39,172-173 and l4e_replay.out:233-235. Corrected hardware remains hypothetical. The Layer 3 figures and their 200 W P-03 basis are accurately quoted at L4-ENERGY-ARCHITECTURE.md:206-218. No compliance or implemented-hardware claim was found.

## Evidence and minors

- All 19 requested correction identifiers appear at v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:94-168 with remedies and closure references. O-2 requires the correction in B2.
- The first-interruption and uninterrupted-service storage thresholds remain useful despite B1: the double-counting occurs after service has stopped. The independently reproduced least additions therefore remain +278.8/+515.8 Wh.
- MINOR M1: v2/docs/records/l4e/l4e_replay.out:157,160 says 'no conversion or charge loss at all'. Only the three undocumented efficiencies are set to 1.00; U3, U3B and lid-path losses remain, as l4e_replay.py:134-150 shows. Replace that parenthetical with 'the three undocumented efficiencies set to 1.00; other losses retained'.
- The next discriminating source evidence is correctly identified at v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:193-200: a pinned REQ-016-compliant panel, its hourly trace and entry-current ratings. Its absence is explicitly disclosed and is not independently a blocker to this conditional screening task.
- No mandatory-requirement contradiction has been demonstrated. REQ-072 remains a design objective; A2 remains an explicit D-06 proposal. Neither correcting this report nor obtaining the next engineering evidence requires approving A2 or changing REQ-016.
