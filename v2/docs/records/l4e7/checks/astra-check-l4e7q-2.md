accepted: yes

# Layer 4, L4-E7: the targeted recheck of the qualification's fixes by the engineering collaborator (an AI review, read-only; the second and last run on this issue)

Collaborator job `cx22-l4e7q-recheck`, run `20261001T174539Z-3651228`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e7 at commit `fac796e42f96`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E7Q: ACCEPT. B1 and B2 are corrected; the requested calculations and focused predicates reproduce. M1 to M5 are substantively addressed, with two residual wording minors below. The prototype bound remains CONDITIONAL. Read-only AI review; nothing changed.

## Blocking discrepancies

- none

## Classification

- **OWNER_REQUIREMENT**: Solar window and operating ambient Evidence: REQ-016, D-34 and REQ-024 retain the existing voltage, power, hold-point and ambient requirements; no change is proposed.
- **MISSING_EVIDENCE**: A7 applicability and other unresolved manufacturer limits Evidence: 8705af p.5 specifies A7 gain at 50 mV differential and CSPIN=5.025 V. The revised qualification explicitly retains the operating-range extrapolation and requests warranted coverage.
- **MODELLING_ASSUMPTION**: Conditional electrical and thermal envelopes Evidence: Half gain, doubled coefficients, thermal coupling/self-heating and panel-temperature scenarios reproduce mathematically but remain stated assumptions or inferred estimates.
- **IMPLEMENTATION_DEFECT**: B2 classification and arithmetic corrections Evidence: The previous zero-effect flags and incomplete fault ratio are corrected; focused predicates reject their reintroduction.
- **IMPLEMENTATION_DEFECT**: Residual junction and LINE wording Evidence: Two phrases remain inconsistent with the corrected qualifications; both are bounded editorial minors with corrections identified above.

## Smallest next action

Correct the earlier junction upper-bound wording and remove LINE's 'no gain of its own' phrase; update the corresponding output and wording assertion.

## Closure criterion

The qualification and output consistently describe junction temperature as an inferred estimate and LINE coupling as nonzero, while retaining the reproduced numbers, five unresolved bound conditions and warranted-limit requirements. Clearing CONDITIONAL requires applicable manufacturer limits and the stated thermal verification; lot characterization alone is insufficient.

## Owner decision required

no

## Checks

- R1: A7 condition and sensitivity: PASS. A7 applicability is explicitly assumed, unresolved and included in CONDITIONAL status. The draft requests warranted transfer-error coverage over common mode, differential, temperature and switching; p.8 is TYPICAL only. Cold break-evens reproduce as 0.904725874873, 0.936935040046 and 0.939052673236 mmho. For the combined case, 0.94 × 99.899220556999 / 100 = 0.939052673236 mmho; substitution returns 100 W.
- R2: TCR, fault ratio and line coupling: PASS. At -20 C, changing the adverse TCR from 50 to 100 ppm/K gives trip-current change +0.226017076846% and sense-path loop-gain change -0.225507391631%. Comparator threshold voltage is distinguished from trip current. Including line and EA2 allowances gives regulation voltages 1.241337311538/1.253674623077 V and fault ratios 1.248653356016/1.236365458364. Line coupling over 8.580154982584 V reproduces 0.042900774913% printed and 0.085801549826% assumed.
- R3: M1 to M5: PASS. Mixed envelopes reproduce 96.248120559153/99.674651952608/99.899220556999 W for A/C/combined. The 0.1 C air sweep remains below those envelopes. At the independently calculated 16.419845017416 V hold floor, matching powers are 63.188318650865/65.410628449798/65.557999654568 W. The qualification labels 105.430977 C an inferred estimate with its extrapolations. Panel scenarios reproduce 110.173750 W at 13.75 C and 122.695000 W at -20 C; both appear in 7b.9t. Both drafts require warranted limits and treat lot data as supporting evidence only.
- Corrected qualification predicates and targeted rendering: PASS. Classification, assumption/qualification/margin, clarification, conditional-status, A7, TCR/LINE and thermal/panel predicates passed. Mutations restoring false TCR stability/protection flags, the old fault ratio or false LINE stability were rejected. Rendered 7b.9t and conditional-result passages match the filed output. This is isolated verification, not full-suite execution.
- Full test_l4e7 and complete output reproduction: NOT_RUN. The replay dependency r11_dep.py:116-121 creates a temporary directory and PNG. Full execution was excluded by this job's no-write constraint. Complete output byte identity was not established in this run.
- R4: Changed claims and read-only integrity: PASS. No blocking numerical or classification regression found. HEAD matches the requested base and the worktree is clean. No verdict writer ran. Residual wording issues are recorded as minors.

## Evidence and minors

- The combined conditional result is 99.899220556999 W, leaving 0.100779443001 W. Manufacturer applicability and physical qualification remain unresolved evidence conditions.
- MINOR M3 residual: l4e7_stage_settings.py:980 still renders 'TJ at most 105.4 C' in l4e7_stage_settings.out:48, although section 9 correctly says inferred estimate, not a demonstrated upper bound. Replace that earlier wording with 'TJ estimated about 105.4 C' and extend the predicate to catch contradictory wording elsewhere in the output.
- MINOR B2 wording residual: L4E7-QUALIFICATION.md:25 and l4e7_stage_settings.py:854 retain 'no gain of its own' beside the correctly quantified nonzero LINE coupling. Remove that phrase and retain the stated VIN-to-setpoint sensitivity; the explicit small/nonzero classification already resolves the blocking issue.
