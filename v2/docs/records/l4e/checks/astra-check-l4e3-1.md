accepted: no

# Layer 4, L4-E3: the one check of the changed claims by the engineering collaborator (an AI review, read-only)

Collaborator job `cx11-l4e3-check`, run `20261001T001305Z-988756`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e at commit `fd82f4cc92ef`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E3: NOT YET. The panel model, runtime figures, load qualifications and L4-R01/L4-R04 revisions check out under their stated assumptions. One blocker remains: the nominal cold-Voc calculation does not substantiate the panel's compliance label against the electrical-characteristic variation stated in its held installation guide. The records support the kit's -20 C operating boundary; no owner decision is presently required.

## Blocking discrepancies

- B1, P1: The source is labelled compliant at v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:58-60, PACKET-POWER-ARCHITECTURE.md:116 and l4e_replay.out:362-369 on nominal Voc alone. The held SunPower installation guide 524958 Rev F, printed p.2, permits electrical-characteristic variation wider than the available cold-Voc margin. The performance caveat at L4-ENERGY-ARCHITECTURE.md:262-266 does not account for that held evidence. Qualify this as a nominally compatible candidate with source compliance INCONCLUSIVE, retain the trace as conditional, and carry the guide's voltage qualification into the source-selection closure.

## Classification

- **OWNER_REQUIREMENT**: P1: applicable temperature and solar window Evidence: v2/ecad/tools/pcb_requirements.yaml:8718, :7681 and :398 establish the kit's -20 C use boundary and the retained 25 V, 17.6 V and 100 W window. The panel's wider component rating creates no new owner requirement.
- **MISSING_EVIDENCE**: P1 B1: maximum cold Voc of the selected panel Evidence: v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:58-60 claims a compliant panel; the guide included at PACKET-FILES.txt:78, 524958 Rev F printed p.2, allows variation beyond the nominal margin. No tighter applicable maximum or unit-specific verification is supplied.
- **MODELLING_ASSUMPTION**: P2: diode fit, NOCT, lead and benchmark normalization Evidence: v2/docs/records/l4e/l4e_replay.py:1157-1193 and L4-ENERGY-ARCHITECTURE.md:262-266 disclose the method and missing NOCT/low-irradiance evidence. The independent arithmetic reproduces the published results.
- **COMPONENT_LIMITATION**: P2: parallel-panel entry current Evidence: v2/docs/records/l4e/l4e_replay.out:393-394 correctly restricts the two-panel result to energy: 12.834 A hot short-circuit current exceeds the 10 A entry specified at v2/ecad/tools/pcb_requirements.yaml:7687.
- **MODELLING_ASSUMPTION**: P3: runtime, storage additions and load sensitivities Evidence: v2/docs/records/l4e/l4e_replay.out:395-416 uses the stated hypothetical path and service ledger. Recomputed figures agree; lower-load cases remain labelled sensitivities.
- **MISSING_EVIDENCE**: P4: monitor, standby WiFi and beacon-average consumption Evidence: v2/docs/records/l4e/l4e_replay.out:420-436 gives each maker's supported figure and the measurement needed; none establishes the assumed operating average.
- **MISSING_EVIDENCE**: P5 L4-R01: guaranteed limiter performance Evidence: v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:233-258 correctly leaves component settings, typical-only limits and transient compliance open.
- **IMPLEMENTATION_DEFECT**: P5 L4-R04: source-dependent charger control Evidence: v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:141-155 describes the drawn fixed-demand problem and an unimplemented correction. The revised acceptance wording agrees with v2/docs/HW-FW-CONTRACT.md:94 and :155.
- **DESIGN_OBJECTIVE**: Runtime shortfall and DR-01 Evidence: v2/ecad/tools/pcb_requirements.yaml:7734-7765 identifies REQ-072 as the objective; D-28 at :866-881 requires honest reporting of the accepted runtime trade-off. No mandatory-requirement contradiction is demonstrated.
- **OWNER_REQUIREMENT**: A2 architecture selection Evidence: v2/ecad/tools/pcb_requirements.yaml:480 retains one 4S3P pack. v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:75-77 correctly treats A2 as a proposal requiring a D-06 change if selected.

## Smallest next action

For B1, replace unqualified compliant-panel labels with a nominally compatible candidate label, mark actual source compliance INCONCLUSIVE, and cite 524958 Rev F's electrical-characteristic qualification. Preserve the reproduced trace and runtime figures as conditional. Next gather a tighter applicable maximum-Voc specification or bounded verification of the selected panel.

## Closure criterion

B1's review correction closes when the page, packet and output consistently distinguish nominal compatibility from verified source compliance and account for the held guide. Actual source compliance closes only when the selected revision or controlled unit has a supported maximum Voc, including temperature and uncertainty allowances, at or below 25 V throughout the required use envelope. Otherwise select another panel within REQ-016 and rerun its trace. This does not require a passing 48-hour objective.

## Owner decision required

no

## Checks

- P1: panel figures and applicable temperature: PASS. 523809 Rev D p.1 states 100 W (+6/-3%), Vmpp 17.1 V, Impp 5.9 A, Voc 21.4 V, Isc 6.3 A and voltage coefficient -58.9 mV/K. Voc(-20 C) = 21.4 + 0.0589*45 = 24.0505 V; Voc(-40 C) = 25.2285 V. pcb_requirements.yaml:8718 (REQ-024), :398 (D-02a) and :7681 (REQ-016) support checking the panel in the kit's -20 C use envelope. The guide's -40 C component rating does not extend the kit's required operating range.
- P1: substantiation of the compliant-panel label: FAIL. SunPower 524958 Rev F, printed p.2, PDF p.3, Table 1 includes SPR-E-Flex-100 and states that rated electrical characteristics are within 10% of measured values at STC. The nominal cold-voltage margin allows only a 4.4369% increase in STC Voc if the stated coefficient is retained. For example, a 5% higher STC Voc, within that guide's band, gives 25.1205 V at -20 C. This establishes insufficient compliance evidence, not a measured panel failure.
- P2: independent operating-point and daily-energy calculation: PASS. Fit A = 1.067275084 V and Rs = 0.230117457 ohm. At 12 UTC: irradiance 520.720366 W/m2, ambient 18.08 C, inferred cells 35.654312 C, hold 17.593 V, current 2.609907 A, operating power 45.916097 W and model MPP 50.281107 W. Applying the documented PVGIS normalization gives 44.779297 W for that hour and 349.999084 Wh/day. Rs brackets reproduce 330.889267 and 346.078490 Wh/day; NOCT 57 C gives 331.260654 Wh/day. At the lower hold corner, maximum current is about 2.963 A versus the assumed minimum limit of 3.162 A: no limiting hour. Two parallel panels reproduce 580.653511 Wh/day and six limiting hours; hot Isc is 12.834 A, above the entry's 10 A.
- P3: targeted runtime and sizing recomputation: PASS. Reproduced all nominal-trace A1/A2 corrected, drawn-upper and collapse-bound interruption and unserved-energy rows at 48/72 h. A2 corrected unserved energy is 986.881942/1196.137377 Wh at 48 h and 1741.395793/1950.651228 Wh at 72 h. Least additional usable storage is 979.208767 Wh and 1719.740309 Wh, with the limiting combined store at the stated 4.2 Wh floor. Load thresholds are 21.079912 W and 17.486905 W. These match l4e_replay.out:397-416 after rounding.
- P4: undocumented loads: PASS. l4e_replay.out:418-439 correctly retains all three as INCONCLUSIVE. Xenarc manual v2 p.4 gives <=10 W, not the assumed 6.03 W battery-side value; measure DC consumption across the profile's brightness and temperature settings. AsiaRF AW7915-AED V1 p.4 gives active maximum 9.1 W and average 7 W, with no standby consumption; measure 3.3 V current in the actual firmware standby state. Mitsubishi RA30H1317M1, October 2011, p.2 supports the conditional 75 W input calculation at 30 W output and 40% efficiency, not a beacon average; specify the profile's beacon duty and measure supply energy per beacon. Their sum is 8.40 W. Even removing all of it leaves 34.4 W, above the computed 21.08 W threshold.
- P5: revised closure wording: PASS. L4-ENERGY-ARCHITECTURE.md:233-258 narrowly closes B2 arithmetic and keeps physical compliance OPEN. The stated assumptions and component selections agree with LT8705A 8705af pp.4-5 and 31. Independent arithmetic gives 99.9984244 W, or 100.0758831 W with EA2 gain 120 V/V. Lines 146-155 restore solar-specific acceptance, retain vehicle/shore operation down to 9 V, and cover startup, source changes, stale telemetry and separate transient testing. HW-FW-CONTRACT.md:94 and :155 support those distinctions. Lines 75-77 retain A2 as an unapproved D-06 change proposal.
- Read-only scope and revision: PASS. Working tree unchanged; HEAD matches the requested base commit. Full replay reproduction remains the coordinator's supplied evidence, separate from the targeted calculations performed here.

## Evidence and minors

- The SunPower sheet SHA-256 matches da06e5e2d9bca625f54a756105e009950a2352e4764868853cb26921372ff605. Installation guide 524958 Rev F matches b8ebdfb7019a399accd75e564a4a764eed565f7066dfd25b131fe65365ec6dd9, pinned at v2/docs/records/a1solar/array_calc.py:49 and included at v2/docs/records/l4e/PACKET-FILES.txt:78.
- The nominal hold is above the sheet's 17.1 V MPP voltage and costs approximately 28.0 Wh/day against the benchmark's 378.0 Wh MPP energy. This and the hold-corner results are conditional model outputs, not measured harvest.
- MINOR: Resolve the temperature-reading wording at v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md:265 and PACKET-POWER-ARCHITECTURE.md:179 by citing REQ-024, REQ-016 and D-02a. The records settle the required use envelope; this need not remain an owner question.
- MINOR: Older prose still says no panel is pinned or its trace remains owed at v2/docs/records/l4e/PACKET-POWER-ARCHITECTURE.md:72 and L4-ENERGY-ARCHITECTURE.md:67 and :329. Update those statements and explicitly label the screening-case headline at PACKET-POWER-ARCHITECTURE.md:122.
- A2's additional-storage gap is 3.51 times the screening gap at 48 h and 3.33 times at 72 h. Neither that shortfall nor the undocumented loads establish a contradiction between mandatory requirements. D-28 and REQ-016's updated notes explicitly retain this as DR-01: v2/ecad/tools/pcb_requirements.yaml:866-881 and :7727-7730.
