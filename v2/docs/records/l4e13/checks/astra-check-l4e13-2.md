accepted: no

# Layer 4, L4-E13: the targeted recheck of U-03's panel by the engineering collaborator (an AI review, read-only)

Collaborator job `cx35-l4e13-recheck`, run `20261002T054411Z-593913`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e13 at commit `4fb7d2634ab0`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E13: NOT YET. The targeted AI review reproduces the principal arithmetic and confirms that B2 now permits both routes. B1 remains unresolved: the irradiance maximum and cold irradiance-slope extrapolation lack supported bounds, A-2 does not consume the specified unit measurements, and A-3 omits the enlarged irradiance envelope.

## Blocking discrepancies

- B1, irradiance bound: L4E13-PANEL.md:25-34 and l4e13_panel.py:388-396 convert an enhancement described as 'over 50 %' into a maximum. Multiplying extraterrestrial irradiance by 1.5 does not establish coverage of the combined altitude, cloud, albedo and panel-plane conditions. The paper discusses larger enhancements and separate albedo effects, but supplies no such global maximum. Obtain a supported plane-of-array envelope with its uncertainty and applicability; retain 2111.4 W/m2 as an assumption until then. Source: [Mol and van Heerwaarden 2025, abstract and section 5.3](https://acp.copernicus.org/articles/25/4419/2025/acp-25-4419-2025.pdf).
- B1, A-1 model uncertainty: L4E13-PANEL.md:83-95 specifies M3 only at 25 C and at most 500 W/m2. Its 10% slope measurement uncertainty does not establish constant slope up to G_MAX or the assumed 253.15/298.15 temperature scaling. Require direct cold/high-irradiance Voc characterization, or validated bounds on both extrapolations, with those contributions included in the acceptance uncertainty.
- B1, A-2 implementation: l4e13_panel.py:690-705 does not evaluate the promised measured unit curve. Make A-2 consume the unit's measured I-V data and irradiance response with a power uncertainty budget, or specify direct measurement at the noon hold corner. Acceptance must use a lower power bound strictly above 1.365591 W.
- B1, A-3 envelope mismatch: l4e13_panel.py:706-709 uses the STC current without G_MAX/1000. The nominal SunPower scenario already reaches 13.82 A at the declared hot/bright corner before an additional rating factor. Reconcile the irradiance envelope with F2/J_SOLAR fault-current and duration coordination, or identify a qualifying source within the retained entry contract. The present 8.18 A result cannot establish route-2 feasibility.

## Classification

- **OWNER_REQUIREMENT**: Solar window and operating envelope Evidence: REQ-016, REQ-024, D-02a, D-02c and D-34 retain the electrical limits and operating conditions.
- **MODELLING_ASSUMPTION**: 2111.4 W/m2 treated as a physical maximum Evidence: The cited enhancement is not an upper bound; L4E13-PANEL.md:25-34 supplies no joint environmental derivation.
- **MISSING_EVIDENCE**: Cold/high-irradiance slope and model-error bounds Evidence: M3 and its laboratory uncertainty cover room-temperature measurements, without demonstrated coverage of A-1's temperature and irradiance extrapolations.
- **IMPLEMENTATION_DEFECT**: A-2 omits specified measured inputs Evidence: l4e13_panel.py:690-705 reconstructs candidate curve data instead of applying all specified unit measurements and current uncertainty.
- **IMPLEMENTATION_DEFECT**: A-3 omits enlarged irradiance Evidence: l4e13_panel.py:706-709 calculates hot current at 1000 W/m2 while the revised envelope reaches 2111.433 W/m2.
- **MISSING_EVIDENCE**: Entry compatibility at enhanced irradiance Evidence: The computed source current exceeds 10 A; no corresponding duration-dependent F2/J_SOLAR coordination is established by this correction.

## Smallest next action

Prepare one corrected PANEL-ACC specification: substantiate the irradiance envelope, add direct cold/high-irradiance voltage acceptance, use measured unit data for the useful-power lower bound, and explicitly resolve entry current coordination.

## Closure criterion

The specification supports Voc plus total uncertainty at or below 25.000 V over a justified envelope, input power minus uncertainty strictly above 1.365591 W at the stated noon/18.813 V corner, and compatibility with the retained 10 A entry over the corresponding current and duration envelope. A qualifying candidate has a supported feasibility basis; both selection routes remain permitted, A-4 remains conditional, and physical acceptance remains downstream.

## Owner decision required

no

## Checks

- Revision, authority and input identity: PASS. HEAD matches the supplied base; all twelve input hashes match. REQ-016 retains 25 V, 17.6 V, 100 W and the 10 A entry. REQ-024 and D-02a support the -20 C operating boundary; D-02c retains 3000 m in-use altitude.
- R1 acceptance arithmetic: PASS. E0 = 1407.622003 W/m2; G_MAX = 2111.433005 W/m2; A-1 factor = 0.698022856. The typical-row fit gives A25 = 1.067275084 V and Vm20 = 24.050500 V, hence A-1 = 24.895482 V, with 0.104518 V margin. The same-shape upper limits reproduce as Voc25 = 21.490205 V and Vm20 = 24.151877 V. These are conditional model results.
- R1 irradiance and A-1 uncertainty coverage: FAIL. The source does not establish a 50% maximum enhancement. M3 measures a room-temperature secant below STC irradiance, whereas A-1 extrapolates it to -20 C and above STC. The specified measurement uncertainties do not explicitly bound either extrapolation's model error.
- R1 direct cold measurement: PASS. For the typical unit under the stated model, extrapolation with 10% coefficient uncertainty gives 25.174156 V. The allowable coefficient uncertainty is 3.459859%, reproducing 3.46%. Direct M2 is therefore justified for this chosen protocol. It is not universally necessary if a separately validated extrapolation has sufficient uncertainty margin, and it does not resolve the remaining irradiance extrapolation.
- R1 A-2 useful-power acceptance: FAIL. 1.27/0.93 = 1.365591 W is correct under the stated loss model, and the typical-shape noon calculation reproduces approximately 26.68 W and the 20.395 V floor. However, l4e13_panel.py:690-705 builds A-2 from candidate currents and scaled candidate voltages. It does not use unit['a25'], unit['isc'], or measured unit Vmp/Imp for A-2, and does not propagate current uncertainty into its power lower bound.
- R1 A-3 and A-4: FAIL. A-3's 8.181675 A reproduces at 1000 W/m2. Applying the record's own linear irradiance model at G_MAX gives 13.820047 A before any additional 1.25 factor, or 17.275059 A if that factor is retained. Thus 8.18 A does not establish entry compatibility over the new envelope. A-4 correctly remains conditional on L4-E7's implementation and verification.
- R2 classification correction: PASS. Both the maker-bound and controlled-unit routes are permitted, consistent with L4-ENERGY-ARCHITECTURE.md:221-225. The record explicitly accepts no physical unit and leaves purchase and measurement with the owner. The classification logic is corrected; its assertion that the controlled-unit route is feasible still depends on resolving R1. Maker-route scenarios reproduce as 27.475285 V for SunPower and 25.041823 V for BougeRV.
- Read-only completion: PASS. Working tree clean. No files edited, verdict writers run, or full replay/test suite executed.

## Evidence and minors

- MINOR, corrected: l4e13_panel.out:76-82 and L4E13-PANEL.md:137-139 distinguish 26.722778 V as the relative-coefficient scenario and 26.428278 V as the absolute-coefficient extrapolation; neither is warranted.
- MINOR, remaining wording: L4E13-PANEL.md:51 should associate 27.475 V specifically with 26.723 + 0.753. Its alternative 26.428 + 0.753 gives approximately 27.181 V. The detailed output already selects the larger scenario correctly.
- MINOR, corrected: Solbian's hold compatibility is explicitly nominal-model only, with no printed Voc band.
- MINOR, corrected: Solbian's +70 C, 1000 W/m2 short circuit is 9.6115 A nominal; the transferred 1.25 factor gives 12.014375 A. The output now labels both qualifications.
- No physical unit is accepted. The remaining evidence gaps do not demonstrate a contradiction between owner requirements.
