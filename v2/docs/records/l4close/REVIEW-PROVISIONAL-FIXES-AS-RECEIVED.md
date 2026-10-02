# MeshSat Layer 4: review of the provisional power fixes

**Review date:** 2 October 2026  
**Reviewed:** rejected candidate `8fbb68b6`, correction packet at `516d43fe`, and separate B6 addendum at `11339ec7`.  
**Verdict:** useful corrections, but **B2 and B6 are not demonstrated closed**. B1's supply reroute also needs a branch-fault protection decision. This is an engineering review of supplied drafts, not fabrication approval.

The immediate work is now specific: qualify the battery switch, give the solar guard a defensible component and interconnect envelope, and protect the new auxiliary feed. The charging-loss correction is sound. The runtime correction properly separates energy-only endurance from service reduced by temperature. Preserve those results.

## 1. What I actually reviewed

| Input | Bytes | SHA-256 | Manifest result |
|---|---:|---|---|
| `MESHSAT-L4-POWER-PACKET-PREVIEW-8fbb68b6.zip` | 6,388,336 | `b2cf128e913e1f2eb3a4e03d6a041678c87d50ffa41035814af75c304b490786` | 340 entries, all match |
| `MESHSAT-L4-PROVISIONAL-FIX-REVIEW-8fbb68b6-to-516d43fe.zip` | 1,509,068 | `c1ac471462259596d76ec192a8b8ad8ea70ddec8f982546ccad8f8aa64fe8bb9` | 36 entries, all match |
| `MESHSAT-L4-PROVISIONAL-FIX-REVIEW-ADDENDUM-B6-11339ec7.zip` | 290,980 | `c2a8c77d89dbc4114d6599f73c34b80be776d459e4939d61a8de20dc0ae22f45` | 8 entries, all match |

I read Astra's seven-blocker report, the changed calculations, draft circuit edits, affected tests and consolidated claims. I independently recomputed selected electrical and thermal results and exercised the B6 numerical function in a separate sensitivity harness.

I applied the audited constant edit tables **in memory**, against the supplied generator text: board A's 16 edits, board E's 17 edits and the interface YAML's five edits apply and parse. The target `check_contracts.py` is absent, so its alias edit was not exercised. All **15 changed Python files** parse successfully. These checks establish neither circuit correctness nor a passing integrated suite.

The inspection overlay is not a real Git revision. I did not execute the complete project test suite, bypass source-hash gates, run KiCad, modify the design, or test hardware. Manufacturer PDFs are largely omitted. I separately retrieved the official Nexperia FET and TI charger documentation. The Saft portal's direct PDF open failed; the B5 assessment below therefore concerns the corrected qualification claim, not an independently completed cell qualification.

**Not reviewed:** subsequently reported integration `c0916a6c`, the final merged B6 candidate, and its targeted Astra recheck. A coordinator's status report is not evidence that those revisions pass this review.

## 2. Disposition of Astra's seven blockers

“Corrected” below means the identified error is corrected within this review's stated scope. It does not mean the proposed hardware has been implemented or qualified.

| Blocker | Disposition | Basis and remaining obligation |
|---|---|---|
| **B1 — E's auxiliary feed and startup claim** | **Topology corrected; qualification open** | U12, its input capacitor and the fans move to VSYS through coordinated A/E dock edits. The unsupported startup-time guarantee is withdrawn. Successful source-only startup and held-pack drain remain conditional. New branch protection gap: L4-F03 below. |
| **B2 — battery FET** | **Not closed** | Replacement is a candidate, but the proposed thermal and body-diode qualifications rely on assumptions not covered by the stated closing tests. See L4-F02. |
| **B3 — thermal modes and limits** | **Substantially corrected; classification needs correction** | Local limits and the SGP41 sensing limit are distinguished. However, the consolidation still turns model-dependent ceilings and missing e-paper storage evidence into physical impossibility and owner conflicts. See L4-F04. |
| **B4 — charging heat** | **Arithmetic correction accepted** | Independently obtained 50.04366 W, or 52.13366 W including the stated ballasts. This validates the correction under the stated inputs; it does not qualify those inputs or the enclosure. |
| **B5 — Saft current-versus-temperature claim** | **Overclaim corrected** | Current at temperature, dwell/recovery and fit now remain open explicitly. Approval to adopt the cell and physical qualification remain outstanding. |
| **B6 — guard already on during a fault** | **Not closed** | A real transient model now exists, but cable inductance alone is insufficient to qualify it. Capacitor assumptions and model uncertainty matter at the very small margin. See L4-F01. |
| **B7 — battery runtime versus thermal response** | **Original reasoning error corrected** | The 2.52 h value is labelled energy-only; the model now includes load shedding. I reproduced the constant-conductance counterexample. The nonlinear enclosure and actual hardware temperatures remain unqualified. |

## 3. Findings requiring action

### L4-F01 — P1: B6's stated cable condition does not establish a robust transient bound

**Evidence:** B6 version of `v2/docs/records/l4e7/l4e7_stage_settings.py`, lines 215–324, 1898, 2383, 2505–2519, 2527–2597 and 2671–2673; its output, lines 869–965; `test_l4e7.py`, lines 827–866.

The supplied result is **0.2991 V against U5's 0.3000 V absolute limit**, conditional on at least **2.47 µH** in the panel lead. That is approximately **0.9 mV, or 0.3%, headroom**.

The code uses one bias factor `k` for three capacitor banks: the ceramics on PV_P, those on TRK_VS, and C13/C14 on TRK_VIN. The banks' initial tolerances are treated separately, but their uncertain DC-bias behaviour is tied together. No manufacturer's part/curve establishes that correlation. Other assumptions include a 0.25 bias floor for the 100 V port capacitors and 10 mΩ ceramic ESR.

I reconstructed the worst reported operating case from printed values and formulas: 36 V source step, 7.46 V initial state, no initial load, 2.47 µH lead, aged cold bulk. This is a **rounded-input reconstruction, not an exact replay of the complete generator**.

| Numerical check | U5 positive sense differential |
|---|---:|
| Supplied function, reconstructed inputs, 20 ns timestep | 0.299128 V |
| Same inputs, 1 ns timestep | 0.299598 V |
| 20 ns, TRK_VS bias factor 0.99, downstream factor 1.00; other factors unchanged | **0.300218 V** |
| 20 ns, TRK_VS bias factor 0.95, downstream factor 1.00 | **0.304662 V** |

The finer timestep alone does **not** prove failure; it consumes about half the original margin. The independent-factor checks are sensitivities, not a claim that a particular purchased capacitor has these characteristics. Their significance is that the current evidence does not exclude them. **Meeting the lead-inductance condition therefore does not, by itself, establish the rating claim.**

The current numerical test usefully checks a simplified RLC response, but allows 1% peak error in that test. It does not establish error below this design's approximately 0.3% sense-voltage margin in the switched, loaded network.

**Required correction:** select actual capacitors and bound effective capacitance, ESR and relevant parasitics at their respective voltages and temperatures. Separate bank parameters unless correlation is supported. Include numerical error in the margin. Specify the complete permissible lead/source/fault-location envelope; a theoretical spacing calculation is not a measured harness specification. If protection requires minimum inductance, make it a controlled, toleranced part of the design or qualify the complete constrained harness. Do not assume every fault traverses five metres of lead.

**Closure:** the selected network must meet the ratings with explicit margin over its bounded uncertainties and the declared fault envelope. Reproduce the critical cases independently and confirm the subsequent bench waveforms at the IC pins. If this topology cannot provide margin, change the protection network rather than repeatedly searching for the smallest passing cable inductance. Preserve the valid corrections to CS115's interpretation.

### L4-F02 — P1: B2's replacement FET qualification still overstates what is established

**Evidence:** `v2/docs/records/l4e11/l4e11_power.py`, lines 2213–2226, 2305–2308, 2321–2339, 2350–2380 and 2468–2514; output rows E11-29/E11-30; `test_l4e11.py`, lines 762–786.

The two BUK6Y10-30P devices may be a workable selection. The supplied proof does not yet demonstrate that:

- `fet_bound()` assumes convex interpolation and a temperature-independent upper bound on the gate-voltage ratio. It produces **21.136 mΩ at 8.5 V and 150 °C**, explicitly through inference. That is not a printed maximum at the operating point.
- The transient thermal shape comes from **the previous AOS device**, scaled for the new devices. A case-rise measurement at 10 A cannot establish that borrowed transient shape for all the listed fault pulses. Adjacent devices' thermal coupling also needs an explicit treatment.
- The code treats **4.72 nF of typical capacitance** as meeting the 5 nF selection criterion without establishing the required margin over operating conditions and variation.
- The docking check converts a **320 A, ≤10 µs pulse rating** into **1.024 A²s**, then accepts an exponential pulse with a **33.8 µs time constant** because its calculated I²t is smaller. The source does not provide that I²t rating. Matching diode paths alone does not validate the conversion or the assumed hot derating.

The official [Nexperia BUK6Y10-30P sheet](https://assets.nexperia.com/documents/data-sheet/BUK6Y10-30P.pdf), pp. 2–6, gives resistance maxima at specified test points, a typical capacitance, and the stated short pulse condition. [TI's BQ25730 sheet](https://www.ti.com/lit/ds/symlink/bq25730.pdf), p. 92, recommends P-channel BATFET input capacitance below 5 nF. These support the distinction between a candidate selection and completed qualification. Nexperia's [thermal/current application note](https://assets.nexperia.com/documents/application-note/AN90016.pdf) also distinguishes steady thermal resistance from transient impedance and relates body-diode loss to voltage times current; it is not authorization for this pulse extrapolation.

**Required correction:** use a device-specific electrothermal/qualification basis with justified uncertainty and margin. Check the actual 18 A/60 s service and relevant fault histories from the hot initial state. Qualify the complete diode-inrush waveform and sharing, or constrain that waveform through precharge/current limiting. If a different switch gives a simpler supported design, choose it. Do not lower the required service to make the part pass.

**Closure:** updated analysis and tests address the assumptions actually used. E11-29's steady case-rise check and E11-30's sharing check alone are insufficient. This finding establishes a qualification gap, **not a demonstrated physical failure of the replacement FETs**.

### L4-F03 — P1: the new VSYS_E contact needs branch-fault protection

**Evidence:** `apply_gen_sch_a_charger.py`, lines 79–89; `apply_gen_sch_e_aux.py`, lines 35–66; `apply_pcb_interfaces_dock.py`, lines 31–50, all under `v2/docs/records/l4e11/`.

Moving E's auxiliary load to VSYS fixes the original supply-path error. The draft connects the high-current VSYS rail directly to **one dock contact rated in the record at 3.5 A**. The 1 A load declaration is bookkeeping, not a current limiter. No branch fuse or current-limiting element is introduced in these edits.

The common power path is designed for 10 A continuous and 18 A pulses, with much higher upstream protection thresholds. That does not establish protection of this smaller branch. A concrete analysis case is an overload drawing 5 A from 14.4 V—equivalent to 2.88 Ω—on VSYS_E: above the contact's stated rating but below the source path's declared continuous capability. This is an electrical counterexample to relying on the 1 A declaration, not a claim that the built connector has already failed.

**Required correction:** bound this branch's overload, short-circuit, inrush and recovery currents, including source-only and battery operation. Add coordinated branch protection or demonstrate another physical limiting mechanism that protects the contact, wiring and copper over temperature and the required pulse durations. Check the new feed's voltage drop against E's startup and fan requirements.

The old cross-board supply topology need not be reopened. Complete this local protection design as part of the coordinated A/E/interface patch.

**Related claim to correct:** `L4-POWER-ARCHITECTURE.md` around line 821 says the held-pack drains are bounded at 0.1408 mA. The underlying L4-E11 section 15a explicitly leaves hot clamp leakage and body-diode current unbounded. Describe 0.1408 mA as the quantified subset, and preserve the separate ≤1 mA bench acceptance.

### L4-F04 — P2: thermal screening is being promoted into proof of impossibility

**Evidence:** `v2/docs/records/l4e12/l4e12_thermal.py`, `govern()` around lines 539–565, `per_mode()` lines 1831–1882, and `caps()` lines 2027–2075; output section 12e; correction packet's `BLOCKER-DISPOSITION.md`, B3.

The corrected mode table is useful. The subsequent claim that four rows “exceed any measurable capacity” is too strong:

- The e-paper has no held unpowered-storage limit. Using its operating limit as a conservative screening assumption does not prove that an unpowered device cannot survive a higher temperature.
- The capacity comparison uses chosen convection/radiation coefficients and particular heat paths. An optimistic model endpoint is not automatically a demonstrated upper bound on every compliant physical implementation.
- The addendum itself identifies a local e-paper temperature measurement and a closed-lid conduction route that could change the outcome. That contradicts an unconditional “no measurement can pass” summary.

**Required correction:** distinguish **modelled failure of the analysed arrangement**, **missing storage qualification**, and **a demonstrated conflict with mandatory requirements**. Keep local part temperatures separate from mixed-air screens. Only the last category justifies asking the owner to weaken a requirement; the other two remain bounded engineering or evidence tasks.

This does not establish that the sealed case will work. T-H1 and the applicable local temperature/storage evidence remain necessary. It prevents an unsupported impossibility claim from forcing another owner-decision loop.

## 4. Results worth preserving

**B4 — charging heat.** With the supplied load 42.82355 W, 46.5 W into the pack, combined efficiency 0.95 × 0.98 and 0.6 W cell loss:

`P_input = (42.82355 + 46.5) / (0.95 × 0.98) = 95.943663 W`

`P_stored = 46.5 − 0.6 = 45.9 W`

`Q_case = 95.943663 − 45.9 = 50.043663 W`

Adding the stated 2.09 W ballast allowance gives **52.133663 W**. This agrees with the correction. The previously omitted load-supply loss is **3.173818 W**. Do not reopen this arithmetic unless the topology, loads, efficiency basis or thermal boundary changes.

**B7 — thermal response.** At 43.413 W case heat, 0.6711 W/K conductance, 8 kJ/K thermal mass and a +20 °C start, the closed-form model reaches +50 °C after **2.06349 h**. Without shedding it reaches **54.467 °C at 2.52 h**. A runtime shorter than the time constant was never sufficient to exempt thermal limits. The revised text fixes that reasoning. Its reported 2.52–2.95 h after shedding must remain distinguishable from uninterrupted operation at the original profile.

**B5 — cell selection.** The corrected report explicitly says the proposed Saft cell's temperature window does not prove simultaneous current/temperature capability, dwell recovery or fit. Keep that qualification. Its energy comparison borrows Samsung discharge-curve behaviour, so treat the Saft runtime numbers as sensitivities until cell-specific evidence replaces them. This neither authorizes a cell purchase nor changes the owner's approved pack arrangement.

**B1 — coordinated edits.** The A/E/interface changes address the original pack-side-feed mistake. Preserve that topology while resolving L4-F03, startup qualification, fan voltage rating and held-pack current.

## 5. A bounded path forward

Keep the accepted Layer 3 requirements baseline. The runtime objective remains a reported design shortfall; it is not a reason to restart requirements work.

Within the existing two-worker limit:

1. One electrical author closes **B2 and the new auxiliary-feed protection**, using the actual combined A/E draft.
2. One electrical author closes **B6's component, lead and transient envelope**, starting from the supplied sensitivity witnesses. Decide the intended margin before selecting values.
3. Correct the thermal classifications in the existing consolidation. Do not commission another broad thermal review merely to restate the same uncertainty.
4. Give Astra the resulting **exact integrated commit**, the four findings here, and the decision-critical calculations. Its check should challenge the selected assumptions and physical margins, not only reproduce script output. Preserve independently confirmed corrections.
5. Maintain separate outcomes: **reviewed architecture**, **implemented circuit**, and **prototype qualification**. A condition with a named owner and test is useful handover material; it is not evidence the condition has passed. Reviewer run limits also do not turn an unresolved finding into acceptance.

If a supported solution remains unavailable, deliver the connected design and these narrowly defined open items to the electronics engineer now. Do not delay that handover to polish every generated page. A useful engineer packet consists of the proposed circuit changes, operating/fault envelope, calculations, unresolved assumptions and exact acceptance tests.

**What this review does not justify:** “power solved,” “Layer 4 100% complete,” or a new completion ETA. It does justify retaining the corrected B4 arithmetic, B7 reasoning and B5 qualification language while directing the remaining work at specific electrical decisions.

## 6. Reproduction companion

`meshsat-layer4-review-checks-2026-10-02.zip` contains the extracted pure `guard_event` function, sensitivity probes, arithmetic/draft-check harness, machine-readable results and provenance. The B6 probes run independently of the repository; the draft checks require the supplied packet overlay. No acceptance guard is removed.

The numerical witness uses printed, sometimes rounded, input values. Its baseline agrees with the reported sense differential to the printed four decimal places. It demonstrates fragility and missing parameter coverage, not a completed SPICE/bench validation or an exact replay of the missing integrated candidate.
