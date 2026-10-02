# MeshSat V2 — review of the 22:30 Layer 4 decision checkpoint

**Reviewed:** 2 October 2026. **Scope:** engineering correctness, architecture, completion and efficient convergence.

## Decision

**Useful for an engineer handoff; CONDITIONAL as an architecture candidate; BLOCKED for power-design closure or fabrication release.**

This checkpoint makes real progress. It reproduces the previous review's solar-guard counterexamples, withdraws several unsupported battery-FET claims and introduces an actual eFuse for the previously unprotected board E feed. Its explicit separation of draft design, implementation and physical qualification is appropriate.

The power problem is nevertheless **not solved**. The solar guard has no corrected network in this packet. The battery switch remains subject to material qualification conditions. The new eFuse's sustained-overload calculation is useful, but its short-circuit closure claim is too broad. Enclosure thermal feasibility also remains open.

“Conditional candidate” and “closure gate blocked” describe different decisions. A mandatory-requirement contradiction is not necessary for a release gate to remain blocked: an unresolved material protection or feasibility condition is sufficient. The packet does not claim fabrication readiness, and this review does not recommend discarding its accepted corrections.

## 1. Provenance and verification boundary

Archive: `MESHSAT-L4-DECISION-CHECKPOINT-2026-10-02-2230.zip`, 704,882 bytes.

SHA-256: `f2030bd252e6293aed32c24d2ceab6752854320d2a2d4b2acfc66a4cc276c3d8`.

All **25 manifest entries match**. The previous external report included as `REVIEW-PROVISIONAL-FIXES-AS-RECEIVED.md` is byte-identical to my delivered report.

| Packet component | Named revision | What I reviewed |
|---|---|---|
| `frozen-candidate-694a8417/` | `694a8417` | Consolidation page, downstream register, findings ledger and original Astra review |
| `round-l4e11-d2a59468/` | `d2a59468` | Battery-switch analysis, eFuse proposal, draft generators, output, tests and diff; explicitly unintegrated |
| `checkpoint-l4e7-73a55580/` | `73a55580` | Solar-guard checkpoint, numerical function change and tests; explicitly unfinished and unintegrated |

This is not a complete repository checkout. These revisions identify the supplied snapshots; I did not independently verify their Git ancestry, current main, a later integration, or the reported 421/50 test results.

Checks performed:

- Parsed all **8 supplied Python files**: no syntax failures.
- Statically applied the board A draft's **16 edits in memory** to the earlier supplied generator: each old text occurred once, each replacement was absent, and the result parsed. No project file was modified and no schematic was generated.
- Inspected U42's proposed pin mapping against TI's HTSSOP pin table.
- Independently recomputed the eFuse current-setting arithmetic and the battery-switch thermal targets.
- Executed only the inspected, extracted pure numerical functions for the revised docking-pulse calculation, using rounded published-in-the-record inputs. This reproduced the calculation, not component qualification.
- Checked relevant electrical claims against official TI and Nexperia sources linked below.

No full project suite, KiCad generation, layout, hardware test or complete end-to-end replay was performed.

## 2. Previous findings: what actually changed

| Previous finding | Disposition in this review | Evidence and remaining work |
|---|---|---|
| **L4-F01 / B6 — solar guard** | **OPEN; diagnosis confirmed** | `L4E7-CONTROL-DECISION.md:594–616` reproduces the failing sensitivities and explicitly says the drafted network does not meet the intended margin. The code now accepts independent bank factors. It supplies no replacement circuit that passes. |
| **L4-F02 / B2 — battery FET** | **PARTIAL** | Section 16 withdraws the resistance “bound,” uses the selected device's thermal figure, includes mutual heating, keeps capacitance open and withdraws the unsupported I²t conversion. Resistance, installed thermal performance and pulse qualification are still conditional. CP-02 below tightens the remaining pulse criterion. |
| **L4-F03 — board E branch protection** | **PARTIAL; credible design improvement** | U42 now physically limits the branch in the draft. The sustained-overload sizing supports the correction. Full fault qualification is not closed; see CP-01. |
| **L4-F04 / B3 — thermal classification** | **PARTIAL** | The checkpoint and engineer handoff correctly distinguish modelled shortfall, missing storage qualification and demonstrated conflict. `BLOCKER-DISPOSITION.md:37` explicitly says consolidation is still in progress. This does not establish that the integrated thermal records were corrected. |
| **B1 topology; B4 heat balance; B5 qualification wording; B7 thermal/runtime distinction** | **Prior acceptance retained within its scope** | No evidence here requires reopening those accepted corrections. B1's startup and held-pack-current qualification remains separate. B5's cell proposal is still not adopted. |

The “0.1408 mA” held-pack current is now correctly described as a quantified subset, with the missing contributions and the 1 mA bench criterion retained.

## 3. Findings requiring a targeted correction

These findings refine the existing open items. They are not a request to start a new broad review round.

| ID | Priority / type | Confidence | Finding | Owner and acceptance |
|---|---|---|---|---|
| **L4-CP01** | P1 — confirmed analysis overclaim; qualification gap | High | The eFuse record uses a typical short-circuit threshold as a maximum and omits startup-into-short timing from its closure case. | L4-E11: distinguish operating overload, short applied while on, startup into short and retry. Bound or explicitly qualify each waveform and the protected path. |
| **L4-CP02** | P1 — unsupported qualification rule | High | The revised docking-pulse acceptance still treats junction temperature alone as sufficient beyond the published pulse-duration condition. | L4-E11 / board P: qualify the complete waveform with an applicable basis, or constrain inrush through a designed precharge/slew mechanism. |
| **L4-CP03** | P2 — confirmed propagation defect | High | The executable draft still emits battery-FET assertions that its new analysis withdraws. | L4-E11 / integrator: make generated design notes and release references use section 16's actual conditions. |

### L4-CP01 — Keep the eFuse, correct its fault envelope

Evidence: `round-l4e11-d2a59468/v2/docs/records/l4e11/`:

- `L4E11-SOURCE-ONLY-AND-ENTRY.md:1305–1326`;
- `l4e11_power.py:2710–2744, 2864–2896`;
- `v2/ecad/tools/tests/test_l4e11.py:873–890` under the same branch folder.

The proposed U42 placement is sensible: the protected feed crosses the dock after the eFuse. Under the record's selected error envelope, I independently obtain **1.471256–1.801802 A**, with the upper value **51.48%** of the stated 3.5 A contact rating. The original unprotected sustained-overload example is therefore addressed in the draft.

However, the document says the contact sees at most 1.802 A, then separately describes much higher fault pulses. Its soft-short calculation uses **45² × 4.5 µs = 0.0091125 A²s** as though this were a guaranteed upper bound.

TI lists 45 A as a **typical** short-circuit threshold. The current limiter has finite response; its steady setting is not an instantaneous current ceiling. TI also distinguishes startup into a short, with thermal-regulation timing up to **1.5 s**, from the operating-overload timer up to **202 ms**. See [TPS1663 Rev. G, §§6.5–6.6 and 8.3.4](https://www.ti.com/lit/ds/symlink/tps1663.pdf).

Consequently, the printed pulse-energy and universal fault-closure claims are not established. This is **not evidence that the eFuse or connector will fail**. The acknowledged hard-short bench condition is appropriate but must cover the complete fault envelope, not only one nominal case.

**Required correction:** retain the eFuse selection; state which figures are guaranteed, inferred or typical. Add startup into a pre-existing short and repeated retry to E11-38. Include source impedance, local capacitance, connector/wiring pulse capability, pin overshoot/undershoot, temperature and fan-start load. Provide concrete pass limits in addition to checking that contact resistance is unchanged. Until then, use **sustained-overload remedy drafted; fault qualification open**.

The test currently checks the record's steady-current equations, temperature assumptions and inrush arithmetic. It does not validate the claimed fault-current ceiling.

### L4-CP02 — A temperature calculation does not extend a published pulse rating

Evidence: `L4E11-SOURCE-ONLY-AND-ENTRY.md:1276–1291`, downstream row E11-30 at line 628, `l4e11_power.py:2828–2850, 3422`, and the corresponding test at `test_l4e11.py:860–871`.

With the record's rounded inputs, I reproduced **53.3078 K rise**, **123.3078 °C from 70 °C**, approximately **16.67 mJ** and **885 W peak**. This shows that the revised numerical result is reproducible.

The remaining problem is the acceptance logic: section 16d says the part is judged on junction temperature alone beyond the printed 10 µs pulse condition. The proposed pulse remains above the stated continuous diode current for about 37.6 µs. Its forward-voltage extrapolation is also inferred.

Nexperia specifies the body-diode pulse rating with duration and mounting-base conditions. Its explanation of limiting values does not make an absent longer-duration rating equivalent to permission to use temperature alone. See [BUK6Y10-30P, Table 5](https://assets.nexperia.com/documents/data-sheet/BUK6Y10-30P.pdf) and [AN11158, §2.4](https://assets.nexperia.com/documents/application-note/AN11158.pdf).

The record already labels this conditional; retain that honesty. **Rewrite E11-30 to require acceptance of the whole hot docking waveform**, including duration, initial state and relevant repetition, rather than just a hot peak-current value and a forward-voltage multiplier. Manufacturer confirmation or a defined prototype qualification can provide evidence within its stated scope. Alternatively, board P can bound the inrush through an explicit circuit change whose normal charging and fault turn-off are also checked.

Changing from an unsupported I²t comparison to a reproducible thermal calculation improves the analysis, but does not itself close the original qualification gap.

### L4-CP03 — The draft still writes the withdrawn claims into the circuit source

Evidence: `apply_gen_sch_a_charger.py:48–55`.

Its `_PAIR` text still writes three obsolete assertions:

- each FET is **bounded** at 21.1 mΩ;
- the installed target is **34.4 °C/W per FET**;
- E11-30 establishes the docking pulse's division between the two diodes.

Section 16 instead calls resistance an **allowance**, uses a **33.12 K/W self-plus-mutual target**, and credits **no diode sharing**. My in-memory application confirmed that the old claims survive into the resulting generator source.

These are comments rather than changed electrical connections, but they are instructions a later layout or implementation owner can rely on. Correct the draft at the same time as the record. A small check that withdrawn assertions are absent from the generated design text is sufficient; no broad suite expansion is needed for this wording change.

## 4. Avoid the next two loops

### The new solar margin is a target, not evidence

Choosing **0.240 V** before searching component values is a useful improvement. However, `L4E7-CONTROL-DECISION.md:611–616` says its 60 mV reserve covers omitted inductance, capacitor ESL and unguaranteed curves without quantifying those contributions.

Treat that reserve as a **design target** until an error/uncertainty budget shows what it covers. Otherwise a calculation at 0.239 V could recreate the same unsupported conclusion with a different threshold. Keep the source and fault-location envelope explicit; a controlled on-board element or suitable protection topology may remove a cable-dependent assumption. No particular limiter circuit is endorsed by this review without its own operating and fault checks.

### Separate prototype evidence from permission to construct the prototype

E11-29 is assigned to “pre-layout analysis” while requiring junction-temperature measurements on a built board; H3 says it blocks layout release. Without an explicit prototype path, that becomes a circular dependency.

Name the test specimen: evaluation hardware, a representative power-stage coupon, or a controlled first prototype. Specify which layout and operating conditions it represents and what results can transfer to the final board. Allow evidence-gathering prototype work under its own scope; retain the final design/production gate until the measurements pass.

The enclosure test can similarly proceed on a representative empty case, thermal structure, fans and dummy loads. Its purpose is to resolve a physical uncertainty; another documentary review cannot substitute for that measurement.

## 5. Bounded next actions

1. **Finish the existing solar-guard task.** Deliver one selected network with actual components, an explicit fault envelope and supported margin; otherwise hand the exact unresolved circuit question to the engineer. Do not restart architecture selection or reopen Layer 3.
2. **Close the battery-switch decision at the correct level.** Retain or replace the selected pair with an explicit qualification path. Resolve the docking waveform through applicable evidence or controlled inrush. Keep the mandatory service envelope unchanged.
3. **Complete the eFuse fault cases and fan-start check.** Preserve the useful protection addition. Correct the claims identified in CP-01 and propagate CP-03's wording change.
4. **Create one coherent integration.** Incorporate the thermal reclassification and qualification wording into the actual design records. Review only changed protection behaviour and affected interfaces on that revision; preserve the earlier accepted heat/runtime corrections unless their inputs change.
5. **Move unresolved physical questions to named experiments.** Identify the engineer or laboratory, test specimen and measurable decision. Do not mark them closed merely because an owner and future test exist.

The useful next milestone is **a coherent power-design package with a defined prototype qualification route**, not another completion percentage. This checkpoint is suitable to start an engineer's review now, provided its provisional status and omitted dependencies are clear. It is not a self-contained reproduction package: several linked design documents, held datasheets and full repository dependencies are absent.

## 6. Independent arithmetic results

| Check | Recomputed result | What it establishes |
|---|---:|---|
| U42 nominal current setting | 1.636364 A | Setting arithmetic |
| U42 selected low/high envelope | 1.471256 / 1.801802 A | Record arithmetic, including resistor tolerance; not a transient ceiling |
| Pair thermal target at stated resistance allowance | 33.11828 K/W | Required self-plus-mutual target, not measured performance |
| Junction at 10 A / 18 A under that target | 87.5 / 126.7 °C | Conditional thermal arithmetic |
| Junction at 20 A if resistance is 25 mΩ on that target | 152.7957 °C | Sensitivity demonstrating why the resistance allowance matters |
| Revised docking model from rounded inputs | 123.3078 °C from 70 °C | Numerical reproduction only |

**Final assessment:** the review process is now producing useful corrections and a much clearer handoff. The surviving work consists of identifiable engineering and qualification tasks. Keep their status explicit, complete the targeted electrical corrections, and give a hardware engineer a workable route to measure what software cannot establish.
