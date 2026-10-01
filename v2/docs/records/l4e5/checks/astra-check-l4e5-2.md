accepted: no

# Layer 4, L4-E5: the targeted recheck of the author's fixes by the engineering collaborator (an AI review, read-only; the second and last run on this issue)

Collaborator job `cx16-l4e5-recheck`, run `20261001T115956Z-2934193`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e5 at commit `03a520635d71`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E5: NOT YET. The revised arithmetic, fallback coverage, H3-specific conclusion and original minors check out. Two acceptance statements still need correction: guaranteed conversion after HIZ exit, and the prohibition on startup writes in V-A10. Read-only AI review complete.

## Blocking discrepancies

- B1: L4E5-SOURCE-CONTROL.md:29 and :192, apply_fw_a16.py:54 and :71, and the rendered output equate HIZ exit with guaranteed conversion above 8.713 V. The arithmetic establishes the pin's HIZ-release level, while conversion below the specified regulation range remains unproven. Replace this with 'out of HIZ', subject to EN_HIZ = 0, and record switching/current behaviour below the regulation range without asserting guaranteed conversion there.
- B2: L4E5-SOURCE-CONTROL.md:205-207 and apply_fw_a16.py:82-83 require telemetry absent from boot, no writes to IIN_HOST or InputVoltage, and IIN_HOST at 4.70 A throughout. This conflicts with the acknowledged POR value and FW-A16's required startup writes at apply_fw_a16.py:35-40. Permit and verify normal initialization first; then prohibit changes caused by missing telemetry, while retaining logging from POR and the ceiling on every write.

## Classification

- **IMPLEMENTATION_DEFECT**: B1: HIZ exit stated as guaranteed conversion Evidence: The revised acceptance exceeds SLUSE66A pp.6 and 27's HIZ statement and p.10's specified regulation range; the nominal target is zero at 8.720 V.
- **IMPLEMENTATION_DEFECT**: B2: Missing telemetry from boot prohibits required initialization Evidence: V-A10's no-write/4.70 A-throughout criteria contradict FW-A16's POR handling and initial IIN_HOST/InputVoltage writes.
- **MODELLING_ASSUMPTION**: Knee tolerance and counter-example envelopes Evidence: The reproduced figures depend on the stated +/-0.5% knee tolerance, +/-1% line tolerance, inferred pin error and existing efficiency model.
- **MISSING_EVIDENCE**: Conversion behaviour below the specified regulation range Evidence: SLUSE66A p.10 starts regulation at a 1.15 V pin voltage; the page already leaves lower-voltage behaviour INCONCLUSIVE.
- **OWNER_REQUIREMENT**: Preserved vehicle and solar functions Evidence: REQ-015 and REQ-016 remain unchanged; neither requires the selected 49.7 W boundary or a 12 V shared-bus minimum during solar operation.

## Smallest next action

Correct 'converting' to HIZ release in the affected statements, and split V-A10's boot case into permitted initialization followed by no telemetry-caused changes. Update the associated predicates to catch both distinctions.

## Closure criterion

The page, draft and output consistently distinguish HIZ release from verified conversion; V-A10 permits the specified POR-to-4.70 A initialization and then detects telemetry-caused changes, premature/missing fallback and every write above 4.70 A. In-memory scope and repeat-refusal checks still pass. Physical behaviour remains INCONCLUSIVE until measured.

## Owner decision required

no

## Checks

- R1: Knee thresholds and latch margin: FAIL. The full FW-A16 coefficient gives a knee slope of 2.484313043 V/V. VIN_RAW nominal and +/-0.5% bands: pin 1.0 V, 8.750000 [8.706250, 8.793750] V; falling 0.4 V, 8.508485 [8.465942, 8.551027] V; rising 0.8 V, 8.669495 [8.626147, 8.712842] V. The latch margin is 8.465942 - 8.31 = 0.155942 V, correctly printed as 0.156 V. These support the stated HIZ boundaries under the network assumption. However, TI p.6 says out of HIZ above 0.8 V, not guaranteed conversion. At VIN_RAW 8.720 V the nominal pin is 0.925471 V and the script's clipped current target is zero. Regulation is specified only from 1.15 V on p.10. See B1.
- R2: Telemetry and diagnostic fallback coverage: PASS. V-A10 covers reports stopped for 30 s and resumed, reports absent from boot, and a failed pin network. Logging every write with a 4.70 A ceiling catches an excessive write. No fallback on the first two over-band readings and mandatory fallback on the third catches premature or absent triggering. The calculated trip is 2.622815 A; fallback settings are 2.05 A at 12 V and 1.55 A after telemetry becomes older than 3 s. The new boot case has a separate acceptance contradiction, B2.
- R3: H3 boundary and counter-example: PASS. With k = 0.80*4.80*0.93/20.7 and R16 low factor 0.9862875, ((9*k*1.01+0.2)/0.9862875+0.079094)*20.7 = 38.748339675 W. H3 gives 49.719517957 W. At 40 W the example settles at least at 12.342258678 V, versus H3's 9.342258678 V. The page restricts its conclusion to H3 and explicitly withdraws the necessity of source identity. Keeping H3 is a sound stated engineering preference: it admits 10.3513 W more nominally at VBUS20 from a 12 V vehicle, while the example needs the higher tracker ceiling. R10 261 k gives 31.6606 to 33.7605 V, reaching 96.46% of the polymer's 35 V rating.
- R4: Original minors: PASS. POR annotations 2000h and 4100h are distinguished from the adapter-removal reset; V-A09 records raw IIN_HOST and RSNS_RAC before and after FW-A01. Nominal stored energy is 10.228187878 mJ, giving 10.228188, 3.409396 and 1.022819 ms for 1, 3 and 10 W deficits. The output now calls these nominal estimates. The author's t_collapse_times_are_nominal_estimates passed.
- R5: Draft, output and tests: FAIL. Draft scope is correct: the heading, FW-A16, FW-C01, FW-E04, added FW-A18, V-A06 through V-A10 and change-record row. Second application refuses with exit 3. All three changed Python files parse. The changed numerical output checked here reproduces. However, the draft and output repeat B1, and V-A10 introduces B2. The new tests check numerical identities and wording presence but do not detect those acceptance contradictions.
- Revision and read-only integrity: PASS. HEAD matches the requested base; working tree remains clean; all 17 script input hashes match. HW-FW-CONTRACT.md remains SHA-256 1c211e467d81b8b70546bc4435c65d4bd2dcd0d2fc3606714a746b4d8d0ac1fa. No verdict writer ran.
- Complete script and 15-test suite reproduction: NOT_RUN. The full paths create temporary images or scratch files. This read-only review used independent calculations and in-memory draft checks; full byte-for-byte script reproduction and a complete suite pass are not claimed.

## Evidence and minors

- MINOR M1 closed: the POR ambiguity remains explicitly INCONCLUSIVE, with raw-register capture prescribed separately from the removal reset.
- MINOR M2 closed: collapse times are labelled nominal estimates pending effective-capacitance evidence.
- The H3 choice and revised solar acceptance do not change REQ-015 or REQ-016. L4-ENERGY-ARCHITECTURE.md identifies the 12 V solar closure as engineering acceptance, not an owner requirement.
