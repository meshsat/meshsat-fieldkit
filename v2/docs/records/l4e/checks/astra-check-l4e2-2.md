accepted: no

# Layer 4, L4-E2: the targeted recheck by the engineering collaborator (an AI review, read-only; the one follow-up)

Collaborator job `cx9-l4e2-recheck`, run `20260930T224030Z-833954`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e at commit `21a9a6fea182`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E2: NOT YET. B1, M1 and L3 pass this targeted AI review. B2's mechanism is appropriate, but its claimed conservative 100 W bound omits the maker's line-regulation tolerance.

## Blocking discrepancies

- B2: v2/docs/records/l4e/l4e_replay.py:801-805 and L4-ENERGY-ARCHITECTURE.md:188-192 omit IMON reference line regulation from the all-voltage tolerance bound. Held v2/vendor/power/lt8705a.pdf, 8705af p.4, specifies 0.005%/V maximum. The existing setting therefore permits approximately 100.065 W at the conservative 25 V corner, exceeding the asserted 100 W ceiling.

## Classification

- **IMPLEMENTATION_DEFECT**: B2: omitted reference line-regulation term Evidence: l4e_replay.py:801-805 includes reference, gain and resistor tolerances but omits the additional VIN-dependent term in held 8705af p.4; L4-ENERGY-ARCHITECTURE.md:188-192 consequently overstates the bound.
- **IMPLEMENTATION_DEFECT**: MINOR B2: sweep lower endpoint Evidence: L4-ENERGY-ARCHITECTURE.md:201-203 specifies 17.6 V rather than the tolerance-adjusted lower hold corner derived at lines 193-194.

## Smallest next action

Add the p.4 maximum line-regulation term to O-2's tolerance stack and round the nominal setting downward. Under the other stated assumptions, that correction alone reduces the nominal ceiling to approximately 3.619854 A. Update dependent power and storage rows, and specify the tolerance-adjusted lower bench-sweep endpoint.

## Closure criterion

The corrected calculation must show VIN × IIN,max ≤ 100 W throughout the stated voltage and tolerance envelope, including line regulation and setting rounding. Dependent replay rows must reproduce the revised settings. The planned bench sweep must cover the actual lower hold corner through the maximum permitted loaded voltage at the temperature ends, retaining separate steady-state and transient records. Hardware compliance remains unproven until that evidence exists.

## Owner decision required

no

## Checks

- B1: independent service ledger: PASS. All 24 balances closed within 3.5e-13 Wh. A2 corrected unserved energy reproduced as 270.132086/286.306461 Wh at 48 h and 500.372955/516.547330 Wh at 72 h. Accounting at v2/docs/records/l4e/l4e_replay.py:249-309 includes cutoff losses and assigns stopped-hour solar once.
- B1: legacy labels and unchanged thresholds: PASS. Legacy counters are labelled at l4e_replay.out:9-17,119,161,276-285. First-interruption entries and the entire storage-addition section are unchanged. A2 additions independently reproduced as 278.782921 and 515.775987 Wh.
- B2: maker mechanism and tolerance bound: FAIL. The stated factors 0.908730641/1.104299068 and nominal ceiling 3.622207167 A reproduce the implemented formula. However, p.4 specifies up to 0.005%/V IMON reference line regulation, with the reference limits specified at VIN=12 V. This term is absent from l4e_replay.py:801-805. Applying it conservatively over 12-25 V permits approximately 100.065 W, so the asserted bound is not conservative across the stated envelope.
- B2: consequence, closure and compliance labels: PASS. The existing assumptions give 55.850537 W at the lower corner. L4-ENERGY-ARCHITECTURE.md:72 separately reports A2 additions of 576.9/1109.9 Wh, apart from the ideal 100 W screening case. Lines 200-204 specify a loaded-voltage and temperature bench sweep. Lines 47-53,208-225 and l4e_replay.out:320-322 retain conditional prototype framing; no demonstrated compliance claim was found.
- M1: efficiency sensitivity label: PASS. l4e_replay.out:219,222 now explicitly retains U3, U3B and lid-path losses, matching l4e_replay.py:146-163.
- L3: preserved originals and independent recomputation: PASS. DRAWN gives 301.202822/547.354336 Wh; corrected NOM gives 136.648944/218.246336 Wh. These match L4-ENERGY-ARCHITECTURE.md:251-254 beside the preserved originals 266.7/494.7 and 102.2/165.7 Wh. Changes from b45d1705 are confined to l4e records; no Layer 3 file changed. Worktree remains clean.

## Evidence and minors

- Independent A2 corrected, 72 h, 06 UTC ledger: node 2481.364043065 Wh + initial storage 502.639656686 Wh = served 2583.027044693 + spill 326.076098300 + charge losses 69.794862478 + discharge losses 5.105694280 + final storage 0 Wh. Discharge losses include 0.107581512 Wh at cutoff. Stopped-hour solar and charge both total 36.103262938 Wh, with no service credit.
- B2's 25 V upper bound follows REQ-016 at v2/ecad/tools/pcb_requirements.yaml:7680-7682. The input-current mechanism and FBIN's lower-voltage action are supported by held 8705af pp.29,31.
- MINOR B2: L4-ENERGY-ARCHITECTURE.md:201-203 starts the proposed sweep at nominal 17.6 V, although lines 193-194 derive a lower hold corner of 16.968 V. Specify the actual tolerance-adjusted lower endpoint in the sweep.
- Full runtime.out and l4e_replay.out reproduction was not repeated; the coordinator's stated reproduction was retained. Only targeted calculations were executed. No verdict writer ran.
