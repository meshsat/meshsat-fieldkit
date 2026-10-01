accepted: no

# Layer 4, L4-E4: the targeted recheck of the author's fixes by the engineering collaborator (an AI review, read-only; the second and last run on this issue)

Collaborator job `cx14-l4e4-recheck`, run `20261001T033707Z-1842303`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e4 at commit `b9d01448807e`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E4: NOT YET. B1 and the three prior minors are corrected. B2 still permits a fast-overvoltage shutdown inside its 15 V acceptance window. Targeted read-only AI review complete.

## Blocking discrepancies

- B2 remains: L4E4-CURRENT-LIMITS.md:79 and l4e4_limits.out allow 12.2 to 16.3 V for the 15 V contract, but held v2/vendor/ti/ti-tps25740.pdf, SLVSDG8B p.8, specifies fast OVP minimum 16.2 V. Page 31 states that fast OVP disables GDNG. A 16.25 V excursion can therefore pass the written window while causing the observed gate edge. Selecting the differential reading at that edge does not establish which current comparator row caused shutdown. Use the smaller fast/slow OVP minimum and correct the regression that currently accepts 16.3 V.

## Classification

- **IMPLEMENTATION_DEFECT**: B1: omitted R16 tolerance and TCR Evidence: Resolved: independent corner calculations and the regression support the revised 4.70 A setting and +0.023 A hot margin.
- **IMPLEMENTATION_DEFECT**: B2: incomplete voltage-fault exclusion Evidence: The calculated 15 V window ignores SLVSDG8B p.8's 16.2 V fast-OVP minimum; the test encodes the same omission.
- **MISSING_EVIDENCE**: C-7's 10 mOhm minimum and actual outlet threshold row Evidence: The page correctly retains the inferred 0.1 A minimum and threshold-row measurement as conditional.
- **MODELLING_ASSUMPTION**: R16 envelope and R11 thermal rise Evidence: The calculation extends the assumed 100 C ceiling to R16 and inherits the inferred 33.3 K/W thermal model.

## Smallest next action

Set each hold-window upper boundary to min(V(FOVP)_min, V(SOVP)_min), require VBUS strictly inside the boundaries, and update the page, output and test. The 15 V interval becomes 12.2 < VBUS < 16.2 V.

## Closure criterion

The corrected regression rejects the present 16.3 V upper boundary and a 16.25 V excursion, accepts boundaries 5.5/10.0/16.2 V for 5/9/15 V with strict interior operation, and the regenerated output matches the page. Physical threshold-row closure remains conditional on a valid recorded bench run.

## Owner decision required

no

## Checks

- R1: R16 corners and hot full-tap margin: PASS. Over -20 to the assumed 100 C, R16 factors are 0.99*(1-50e-6*75)=0.9862875 and 1.01*(1+50e-6*75)=1.0137875. U3 maximum=max(4.70+0.100,4.70*1.025)/0.9862875=4.884478410 A; conditional minimum=4.60/1.0137875=4.537440045 A. Through R11, maximum plus 0.079094 A is 4.963572410 A. At 62.1 C air, the inherited rise is 17.326290 K. With the full 0.3803 mOhm allowance at 25 C, stacked minimum=4.986201760 A and margin=+0.022629350 A, matching +0.023 A.
- R1: conditional minimum and regression: PASS. The page's lines 91 to 104 explicitly retain C-7's inferred 0.1 A condition. The new minimum exceeds 4.517 A by 0.020440 A. The old 4.65 A choice gives 4.488120 A minimum and -0.037412 A hot margin with its old tap allowance. t_r16_tolerance_old_bounds_fail_new_bounds_pass passes with the corrected bounds and fails when the omitted-R16 bounds are restored in memory.
- R2: bench connections and observations: PASS. U19 pin 1 is PD_UVLO, shared only with R133 and R134; U18 does not use it. PD_VPWR reaches U18 pin 20 and Q27 drain; sense pins 19/21 are PD_SW/PD_VBUS and Q27 gate is PD_GDNG. The procedure records differential sense voltage, VBUS at U18 and the connector, gate, supply-limit flag and current, and rejects supply limiting or departure from its stated window.
- R2: exclusion of voltage-fault shutdown: FAIL. At 15 V, fast OVP has a 16.2 V minimum, below slow OVP's 16.3 V minimum. The page and output permit VBUS up to 16.3 V. l4e4_limits.py:402 selects only slow OVP, and test_l4e4.py:202 asserts that erroneous window. The existing bench test passes despite this omission. Strict interiors of the stated 5 V and 9 V windows exclude the cited voltage faults; the 15 V window does not.
- R3: prior minors: PASS. Tolerance is parsed from HoJLR2512 Ho-A0 page 1 and checked against the part readings and inherited band(). Hiccup is a candidate subject to peak-current and ripple criteria. Status explicitly awaits this recheck and retains conditional bench evidence.
- R4: register, output and R11 draft: PASS. 4.70 A / 0.05 A gives code 94 and 0x5E00 with RSNS_RAC=0b. r11_dep.out reproduces in child and in-process runs; l4e4_limits.out reproduces byte for byte, SHA256 6a47caa7f5dd9c48286f7a4059e0b2725c07ae661e638bcfaf72db3455db4509. Only temporary image-file I/O was replaced in memory. The R11 draft changes only FE isns='8m', isns_lcsc='C2904240' and commentary, parses, and refuses a second in-memory application with exit 3. Output reproduction does not validate the erroneous B2 window.
- Read-only scope: PASS. Worktree remains clean at the specified base commit. No files edited, drafts applied to disk, gates or verdict writers run.

## Evidence and minors

- MINOR 1 resolved: L4E4-CURRENT-LIMITS.md:10 accurately distinguishes read tolerance from r11_dep's internal literal, which is checked for agreement.
- MINOR 2 resolved: L4E4-CURRENT-LIMITS.md:58 makes hiccup a candidate remedy with explicit remaining criteria.
- MINOR 3 resolved: L4E4-CURRENT-LIMITS.md:14 replaces the prior status claim with pending recheck and conditional bench evidence.
- For a valid isolated run excluding voltage faults, 19.2 to 22.6 mV identifies the intended row; 29 to 34 mV identifies the higher row and requires R138 reselection. The current 15 V acceptance window prevents that conclusion from being unconditional.
- The temperature envelope and inferred thermal rise remain modelling assumptions; this review establishes no hardware measurements or implementation.
