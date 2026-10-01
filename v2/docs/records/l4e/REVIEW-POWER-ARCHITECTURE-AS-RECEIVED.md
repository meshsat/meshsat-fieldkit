<!-- The independent power-architecture review of 1 October 2026, relayed by the owner to the coordinating session;
     verbatim as received, its own dash characters and links kept. -->

# MeshSat V2 — independent power-architecture review

**Reviewed packet:** `MESHSAT-POWER-ARCHITECTURE-PACKET-eb3849d5.zip`, dated 1 October 2026.  
**Declared source:** `eb3849d5e9d7a8397ec977ecb6d80b779dcdd822`, branch `fnd/l4e`; the packet says this is not yet on main.  
**Scope:** engineering correctness, energy accounting, architecture decisions, reproducibility and usefulness to an electronics engineer. This is not a complete circuit, PCB or fabrication review.

## Verdict

**CONDITIONAL — useful for an electronics engineer to review now. Layer 4 power architecture is not complete or ready to freeze.**

This is a meaningful improvement. The packet identifies the power path, distinguishes drawn circuits from proposed corrections, preserves the owner's constraints, and asks eight focused engineering questions. It now explains both the solar-basis mismatch and the stopped-hour energy double count. Those corrections improve the decisions an engineer can make.

The remaining work is primarily selecting and substantiating a realizable design. Another general AI review of the same assumptions will not provide that evidence. Send this packet for engineering discussion with the limitations below; continue the targeted Layer 3 amendment and independent Layer 4 work.

There is no new reason here to restart the requirements process. Missing the 48–72-hour objective is an architecture trade-off, not by itself a reason to declare the requirements incomplete. Battery and solar, internal storage, HF and tablet retention, and the other mandatory requirements still apply.

## What I independently checked

- ZIP checksum matches the supplied checksum: `ea901308707e821df96c118d92ce17e6fdfea56bd310a345d99eb6534d4c2b18`. ZIP CRC is clean; all **59 manifest payloads** match.
- Read the comparison, engineer entry page, replay code and output, review records, relevant source-control contract and carried power-path findings.
- Recomputed the proposed high-corner power calculation independently: **99.9984244 W** under the script's assumptions. The numerical margin is **0.0015756 W**, approximately **0.001576%**.
- Cross-checked the relevant LT8705A specification conditions against the manufacturer's datasheet, including typical-only values and temperature qualification.
- Executed the new accounting function in three isolated, manually specified fixtures: stopped-hour solar charging, full-hour battery service, and partial service before stopping. All three produced the expected served/unserved energy and closed the energy balance.
- Attempted the complete replay in a disposable local assembly using this packet plus the earlier supplied Layer 3 export. It could not finish because a required board-A BOM is missing. **I have not independently reproduced every published runtime or sizing figure.**

The local assembly used a fresh review-only Git commit to satisfy `HEAD` file-equality checks; it did not recreate or impersonate the original project history. No project source was modified to bypass a failed check. No routing, layout generation, hardware testing or full repository test suite was performed.

## Findings and remaining closure obligations

Priorities describe what matters before architecture acceptance. Rows explicitly marked as disclosed gaps are not newly discovered circuit failures.

| ID | Priority / evidence | Finding | Required action |
|---|---|---|---|
| L4-R01 | P1 architecture closure; confirmed conditionality | The 100 W calculation is correct under its assumptions, but does not establish a guaranteed operating bound. | Keep the arithmetic correction closed narrowly; retain implementation/compliance as open. Select real parts and substantiate the missing limits. |
| L4-R02 | P1 design selection; already disclosed | Neither architecture has a compliant panel trace that substantiates its solar-assisted performance. | Select a compliant source and evaluate its operating point with the chosen limiter before selecting the energy architecture. |
| L4-R03 | P2 handover; confirmed | The supplied ZIP is a readable discussion packet, not a standalone calculation replay. | Provide the replay dependency set and verify it in a clean offline extraction. |
| L4-R04 | P2 acceptance clarity; confirmed wording mismatch | A solar-specific `VIN_RAW > 12 V` closure is summarized as applying to every source, despite the retained 9 V DC input floor. | Restore the solar qualifier and define separate per-source acceptance conditions. |

### L4-R01 — distinguish a conditional calculation from a guaranteed limit

Evidence: `v2/docs/records/l4e/l4e_replay.py`, particularly `EC_ROWS`, `R_TOL`, `T_ENDS` and section 11; `checks/check-l4e2-3.md`; engineer question 3.

The omitted line-regulation term is now present. I reproduce the coordinator's result:

```text
25 × 3.548 × [1.229 × (1 + 0.00005 × 13) + 1.5/130]
    ÷ 1.208 ÷ 0.93 ÷ 0.99²
= 99.9984244 W
```

The LT8705A datasheet gives EA2 gain as **130 V/V typical**, without a minimum; EA3 gain is also typical-only. The line-regulation specification is stated at 25 °C, not switching. The replay explicitly assumes those conditions can be extended to its operating envelope. It also assumes 1% covers all tolerance and drift of two resistors that have not been selected. Those assumptions are disclosed, which is good; enumerating corners does not turn them into guarantees. [Manufacturer datasheet, printed pages 4–5 and 31](https://www.analog.com/media/en/technical-documentation/data-sheets/8705af.pdf).

As an illustrative sensitivity check, changing only the assumed EA2 gain from 130 to 120 in the same equation gives **100.0758831 W**. This is not a prediction of an actual device or panel violation. It demonstrates why the calculation cannot establish an unconditional upper bound from the stated data.

Likewise, the two temperature labels in the loop repeat the same bounds. They do not constitute an independent temperature model. Using valid full-temperature limits this way is reasonable; applying typical-only or 25 °C values still requires an engineering basis.

**Close this efficiently:** retain “B2 arithmetic corrected under stated assumptions.” Keep “O-2 physical compliance” open. Have the engineer select the IC grade, actual resistor values and tolerance/drift budget, and justify the remaining allowances or choose a different limiting mechanism. Evaluate the achievable component settings, not an abstract 1 mA rounding grid. Define steady-state and transient acceptance separately. Do not spend another AI round merely making the printed result infinitesimally lower than 100 W.

### L4-R02 — use an actual compliant source to select the architecture

Evidence: `L4-ENERGY-ARCHITECTURE.md`, comparison and next-calculation sections; `l4e_replay.out`, sections 7 and 11; `PACKET-POWER-ARCHITECTURE.md`, sections 4–6.

The packet now correctly calls the 400 Wp 2S2P trace clipped to 100 W a **conditional screening stimulus**. Clipping that trace does not make its panel wiring compliant or show that a selected 100 W-class panel will provide the same daily energy.

The proposed fixed-current protection also changes the energy question: the packet reports about **62.4 W at the nominal hold point**, with a **52.8 W lower-corner scenario**. These are not demonstrated harvest levels. The panel's current–voltage curve and the controller's actual operating point determine the result.

The practical sequence is to select a compliant panel candidate, evaluate its curve across the relevant conditions with the candidate control scheme, then rerun storage and runtime. Compare a different limiting approach only if the result warrants it. Do this alongside substantiating the **8.4 W of undocumented loads**. Neither activity requires relaxing the owner's requirements.

A2 remains a proposal to change D-06. Its mechanical fit and thermal obligations remain open. Do not describe the larger store as an approved or realizable solution merely because its energy model performs better.

### L4-R03 — the engineer cannot reproduce this calculation from this ZIP alone

The ZIP omits five files explicitly required by `l4e_replay.py`'s initial pin checks:

```text
v2/docs/records/l3batt/runtime.py
v2/docs/records/l3plane/energy_basis.py
v2/docs/records/l3plane/three_cases.py
v2/docs/records/l3plane/three_cases.out
v2/docs/records/energy/energy_budget.out
```

These five are available in the earlier Layer 3 export and match the new replay's expected hashes. However, after supplementing the packet, the baseline replay still stops at:

```text
v2/release/revA/boards/meshsat-pcb-a-revA-A24/pcb-a-power-bom.csv
```

That is a required input to `vbus20_range.compute()`. The replay also depends on other imported models, input data and Git file reads.

This is a handover limitation, not evidence that Claude's full-repository run failed. The packet presents itself as an engineer discussion packet, and the separate Layer 3 export repair is not included here. I cannot assess that repair from this ZIP.

**Closure:** ship a bounded replay companion with the dependency files and the Git objects actually read, plus one documented command. Verify the command from a clean extraction without the original checkout, object store or network. Retain a separate compact entry document so the engineer need not read the entire dependency archive.

### L4-R04 — preserve the source-specific meaning of the brownout test

`R11-DEPENDENCY.md` A-2 explicitly specifies the **panel source or its simulator** for the test requiring `VIN_RAW` to settle above 12 V. The Layer 4 summary says the remedy is for every source but omits that qualifier from its closure. `HW-FW-CONTRACT.md` FW-A16 explicitly covers a 9 V vehicle input.

This does not prove that the circuit excludes 9 V operation. It is an acceptance-description ambiguity. Correct the summary and give vehicle/shore and solar their own valid voltage/current envelopes. The control decision should also address startup, source changes and missing/stale telemetry; FW-E04 currently reports voltage over USB at 1 s intervals, which by itself is not evidence of adequate transient response.

## What is improved, and what remains open

| Earlier issue | Assessment of this packet |
|---|---|
| Stopped-hour solar counted as both served load and stored energy | **Correction supported by code inspection and three targeted fixtures.** Full scenario replay remains unverified here. |
| P-03 200 W stage used for retained REQ-016 claims | **Explicitly identified and separated in Layer 4.** Compliant-panel performance remains open. |
| Omitted current-limit line regulation | **Present now; revised arithmetic independently reproduced.** Physical compliance remains conditional. |
| “Screening trace” presented as actual panel capability | **Label corrected.** It is no longer an undisclosed substitution in this packet. |
| TVS breakdown onset treated as protection of 35 V capacitors | **Question 7 now states the problem correctly.** Protection design remains unresolved; no circuit fix is claimed. |
| Layer 3 requirement wording, acceptance binding and export findings | **Not closed by this packet.** Review the separately amended Layer 3 files and repaired export when supplied. |

## What the endurance figures mean now

These are packet model results, not measured capability or a full independent replay:

| Case | Useful interpretation |
|---|---|
| A1, single ruled pack | 107.9 usable Wh / 42.8 W gives approximately **2.52 hours battery-only**. I checked that division. |
| A2, proposed larger internal store | Approximately **12.71 hours battery-only** at the packet's +20 °C assumptions. It is not yet an approved mechanical/electrical implementation. |
| A2, corrected path and 100 W screening stimulus | First interruption at **11 or 23 hours**, depending on start time. Later service can resume; this is not continuous 48-hour endurance. |
| 48–72 hours | Still the design objective. Neither studied architecture establishes it under the retained requirements. |

PS-IDLE-SPEC is a defined 42.8 W operating profile, not all processors and transmitters simultaneously at maximum. Optional tablet charging is excluded and would reduce runtime. Any lower-load case must preserve the approved service or be explicitly identified as a different operating profile.

## Bounded next steps

1. **Give the packet to the electronics engineer now**, with this review. Its questions are concrete enough to support useful work; do not wait for fictitious “100%” certainty.
2. **In parallel, resolve the two dominant inputs:** a compliant panel's performance with the proposed control, and the undocumented load estimates. Keep the existing owner constraints fixed.
3. **Make one implementable power-path choice:** source control, current-limit coordination, real component settings, fault handling and protection. Carry thermal and bench obligations with explicit acceptance criteria; do not require future physical testing to rewrite settled requirements.
4. **Supply the replay companion and a bounded Layer 3 amendment.** Run the affected calculations and checks, then the required integration gate. Re-review changed claims rather than reopening every accepted section.

No new owner decision is needed to perform those investigations. Selecting A2 would require the existing D-06 change decision at that point. The present evidence supports continued engineering and a useful human handover; it does not support an architecture-complete or fab-ready claim.
