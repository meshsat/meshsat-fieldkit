# cx44, Astra's advisory challenge of the F01 / D-17 selection (c) on fnd/p0pwr 8c7c335f: AS RECEIVED (saved 15:53 CEST, 5 Oct 2026)

An AI review (GPT-6 Astra at xhigh, read-only), the advisory challenge of P0-1's selection before drafting; it accepts nothing and is kept as given. Run dir: <worktrees>/_runs/codex/cx44-f01-selection/20261005T134057Z-1974083/

```json
{
 "job_id": "cx44-f01-selection",
 "base_commit": "8c7c335fb87d33167a3bc125d2116b4cf2774706",
 "outcome": "DONE",
 "summary": "F01 SELECTION: NOT SUPPORTED because the selected current cap has no established bound showing that it preserves the mandatory 30 W RF service across the operating envelope.",
 "changed_files": [],
 "artifacts": [],
 "checks": [
  {
   "name": "Candidate identity and read-only state",
   "method": "Checked HEAD and working-tree status before and after the AI review.",
   "command": "git rev-parse HEAD && git status --porcelain",
   "exit_code": 0,
   "outcome": "PASS",
   "evidence": "HEAD matches the named candidate; working tree remains clean. No files, verdict records or registries were written."
  },
  {
   "name": "Case and selection arithmetic",
   "method": "Imported calculation functions with bytecode disabled, compared rendered strings in memory, and independently evaluated the voltage equation and loop corners.",
   "command": "python3 -B - <<'PY' [read-only calculation and comparison] PY",
   "exit_code": 0,
   "outcome": "PASS",
   "evidence": "Both stored outputs reproduce byte-for-byte. Independent arithmetic agrees with 15.516213 V nominal, 16.071832 V bounded, and the selected correction's conditional 15.201897 V."
  },
  {
   "name": "Printed-limit and service claims",
   "method": "Read held manufacturer tables and application conditions against the selection's equations and conclusions.",
   "command": null,
   "exit_code": null,
   "outcome": "FAIL",
   "evidence": "The asserted complete printed-limit bound includes typical stress data, assumed residuals and unestablished service transfer. U13's current comparison omits its output-fed BIAS load."
  },
  {
   "name": "Closed-loop dynamics and physical feasibility",
   "method": "Inspected the proposed topology, existing generators, manufacturer response information and B-PA1/B-PA2.",
   "command": null,
   "exit_code": null,
   "outcome": "INCONCLUSIVE",
   "evidence": "No complete compensation design, bounded settling result or measurements establish simultaneous current limiting, rail regulation and 30 W service throughout the prescribed key-down."
  }
 ],
 "evidence": [
  "Q1: The reproduced case is C-ALLTX rev 3, retaining its specified typical non-transmit loads, running fans and disabled standby card. ASSUMPTION-based arithmetic: Vrest = P/I + I(Rpath + Rcells). Nominal: 241.0391276/18 + 18(0.0380639333 + 0.0800000) = 15.5162134 V. Allowance = 18[15.5 - 18(0.1180639333)] = 240.7472856 W; deficit = 0.2918420 W.",
  "Q1: The gauge terms sum to 0.8035665 A: 0.4860000 gain + 0.0413665 nonlinearity + 0.0050000 offset + 0.1800000 shunt tolerance + 0.0864000 gain drift + 0.0048000 offset drift. BQ4050 SLUSC67B, p.11, section 6.14 supplies PRINTED LIMIT coefficients: 0.8% FSR, 22.3 LSB, 10 uV post-calibration offset, 150 ppm/C and 0.3 uV/C post-calibration offset drift. Conversion uses the record's nominal/TYPICAL reference scale and nominal shunt. The 32 K temperature excursion and shunt tolerance treatment are ASSUMPTIONS. The selected reproduction does not add R10's temperature coefficient or establish board P's temperature from the cell limit. Thus 0.8036 A is reproducible, but is not a complete unconditional error limit.",
  "Q1: With I = 17.1964335 A, Rpath = 0.0390639333 ohm and Rcells = 0.0800000 ohm, the budget computes 241.1689171 W and 16.0718317 V. The rev 3 case file quotes 16.0684 V; l9t5_case.out:75 explicitly attributes the difference to the subsequently included offset-drift term. This changes the quoted calculation, not the case definition.",
  "Q1/Q2: Mill-Max's held rugged-power-pin document, catalogue p.28, prints contact resistance 20 milliohm maximum: PRINTED LIMIT. Four connected pins in parallel each way give an arithmetic ceiling of 10 milliohm round trip. This requires the specified power contacts and valid mating; it does not establish the resistance of the remaining leads, PCB bands or faulty/open contacts. Preci-Dip 813, catalogue p.31, prints 10 milliohm at static halfway position without a maximum designation and 3.5 A maximum operating current; those are signal contacts. Samsung 35E's 35 milliohm initial AC impedance does not establish the ASSUMPTION of 60 milliohm DC/pulse cell resistance.",
  "Q2: Mitsubishi RA30H1317M1, October 2011, p.2 prints 30 W minimum and 40% minimum efficiency at Tcase = 25 C, VDD = 12.5 V, VGG = 5 V, Pin = 50 mW and matched source/load: PRINTED LIMITS at those conditions. Page 8's 0.84 + 5.16 = 6.00 A is a heat-sink calculation example at 30 W and 40%, not a maximum-current specification over controlled VGG and temperature. Page 5's VGG response curves are TYPICAL. Carrying 6 A to the selected rail and hot flange using an ideal class-B model is an ASSUMPTION.",
  "Q2: Independent conditional corner arithmetic gives VSET = 3.299716 to 3.421657 V, U13 output = 13.482706 to 14.039692 V, and current cap = approximately 6.437573 to 7.011920 A. At the lower voltage/current corner, 40% efficiency would yield 34.718 W; therefore the arithmetic does not demonstrate service reduction if 40% actually applies there. The required efficiency is 30/(13.482706 × 6.437573) = 34.5638%, before PA-feed drops. No held limit establishes that efficiency or the corresponding maximum current at 30 W in this operating envelope. The existing maximum available VGG also remains below the sheet's 5 V service test condition.",
  "Q2: INA250 SBOS511C, pp.5-6: system gain error 0.75% over -40 to +125 C, A2 offset 50 mA at 25 C, offset drift 250 uA/C, PSR 1 mA/V and CMR 97 dB are PRINTED LIMITS. The offset drift contribution over -20 to +76.25 C is 12.8125 mA; the author's wider ambient allowance to +85 C uses 15 mA. The five stress figures total 0.425% but are TYPICAL, explicitly excluded from system gain error. Adding them to 0.75% does not establish a 1.175% maximum. The separate 0.03% nonlinearity entry is also TYPICAL and needs an explicit coverage treatment. Using 5.14 V alone for PSR omits the actual supply range. The 4.5 milliohm package resistance and thermal metric do not provide a maximum temperature-rise bound for this layout.",
  "Q2: TLV758P SBVS351D, pp.5-6: 1% accuracy through TJ = +85 C, 7.5 mV line regulation and 0.1 uA feedback current are PRINTED LIMITS under their table conditions. Accuracy is specified at 1 mA output; the proposed divider alone draws only 55 uA. Load regulation is TYPICAL, so the actual reference loading needs establishment, for example by a defined preload. The 1% choice requires a junction-temperature bound, not merely +85 C air; the printed accuracy through +125 C is 1.5%. An ASSUMPTION-based sensitivity using 1.5% gives a 6.4045 to 7.0461 A cap, leaving only 10.8 mA below the author's U13 minimum before other loads.",
  "Q2: TLV9062 SBOS839N, pp.13-14: 2 mV offset over temperature is a PRINTED LIMIT at the stated supply/common-mode conditions. The author's 1 nA bias-current allowance is an ASSUMPTION; the sheet prints 0.5 pA TYPICAL. Common-mode movement from the offset test point, finite gain, supply-corner applicability, leakage, compensation-capacitor leakage, inverter loading and output travel are not fully allocated. INA250 bandwidth/slew and TLV9062 bandwidth/settling entries are TYPICAL, not a guarantee for the complete loop.",
  "Q2: The conditional upper power is 14.039692 × 7.011920 = 98.445203 W. Substitution into the unchanged case model gives 226.209150 W at VBAT, 15.201897 V required and 0.298103 V margin. The 1% U13-divider scenario gives 15.3577 V and 0.1423 V margin. These are ASSUMPTION-based calculations, not an established pass: the PA converter uses an extrapolated TYPICAL efficiency, other conversion efficiencies are declarations, remaining path resistance and 60 s cell-voltage evolution are unresolved, and the added control-circuit consumption is absent. The available conditional headroom is 5.1263 W at VBAT, or 4.9910 W in the substituted PA-load quantity.",
  "Q2/Q4: U13's 7.056897 A figure is conditional on the declared shunt tolerance/TCR/temperature assumptions. gen_sch_a.py:501 and :517 place U13 BIAS and the feedback divider downstream of R55; :1147 selects that topology for the PA stage. The new INA250 is proposed only in the J_PA branch. LM5176 SNVSAI1D p.15 explains that BIAS supplies the gate-driver regulator. Consequently R55 carries more than the sensed PA current. The generator's TYPICAL gate-drive estimate is about 41 mA, already comparable to the claimed 44.98 mA margin. No complete worst-case branch-current sum establishes L9P-F04 closure.",
  "Q2: No compensation capacitor, plant-response bound, stability margin or maximum settling time is supplied. TLV758P SBVS351D p.13 enables its output pulldown when disabled; it does not establish active gate discharge while PA_KEY remains high and the feedback injection lowers the target. Gate capacitance, the proposed injection network, U15 dynamics, integrator saturation/reset, harness ground offset and U13's loops therefore matter. The 9.596 A value is an average current-regulation target, not an instantaneous transient ceiling. A 60 s duty allowance does not excuse rail collapse during acquisition.",
  "Q2: B-PA1 names three modules, plate heat path, board D drive, 144/145/146 MHz, two rail voltages and flange temperatures 25/+85 C, with current at 30 W at most 6.438 A. This is a feasibility measurement because its result determines whether the current cap preserves service. It lacks instrument uncertainty/guard bands, the cold endpoint, justified coverage between samples and endpoints, actual module-terminal voltage after drops, and enforcement of the available VGG band. B-PA2 separately requires dynamic evidence. Neither row has MEASURED results; three specimens alone establish no population guarantee.",
  "Q3: Rejection of (b) as a standalone correction is supported: even an ideal gauge gives 15.534213 V with maximum dock resistance, or 15.516213 V with the inferred original path. Its stated 0.293994 A calibrated residual and 15.724157 V remain conditional on reference accuracy, temperature and shunt self-heating assumptions. Inferring a thermal resistance from the resistor's power-derating graph is not a printed thermal-resistance limit.",
  "Q3: The held ADL5902 Rev. B p.3, ADL5513 Rev. B p.3, LMH2110 SNWS022D p.6 and LTC5582 Rev. D p.2 support the finding that the relevant temperature entries are TYPICAL and do not bound the intended 144-146 MHz calibration residual. The sampler and reference remain unqualified. Conditional RF-loop calculations offer more margin: 1.1506 V at ±0.25 dB and 0.5384 V at ±0.5 dB if 40% efficiency transfers. Without that assumption, the respective required efficiencies are 32.5423% and 36.5131%. Neither alternative is established as a simpler supported solution. However, rejecting (a) for unprinted PA efficiency while crediting (c)'s unprinted service-current transfer applies inconsistent evidence standards.",
  "Q4/Q5: The comparison names U13's divider, VGG injection, AB_SPARE, PA heat and keying transients, but does not complete the connected path. It must cover U41/+5V_D8IN's added loads; R55 and U13 BIAS; INA250 insertion drop and heat; J_PA and its 16 AWG lead; PA ground through its supply return, flange, RF shields and gate lead; harness-reference shifts; U15/EMCON behavior during power sequencing and signal faults; upstream pack current, protection coordination and thermal losses; and the complete 60 s/repeat thermal duty. IF-A-PA and IF-AD-HARNESS both require consequential updates. The original requirements, fans, 15.5 V floor and REQ-016 window are not explicitly changed; describing the service as preserved before establishing it would silently weaken the acceptance.",
  "Provenance: v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md is absent from this candidate. The review used the instruction supplied in the job prompt together with the held constitution and authoritative requirements. No result is claimed from reading that absent file."
 ],
 "blockers": [
  "v2/docs/records/l9t5/l9t5_f01.out:109 and :120; README.md:27: The 6 A example does not establish service at the cap's lower corner. Smallest correction: label the transfer ASSUMPTION, withdraw the service-preserving selection claim, and make B-PA1 a Layer 4 feasibility blocker with uncertainty-aware RF and current limits.",
  "v2/docs/records/l9t5/l9t5_f01.py:306; l9t5_f01.out:80 and :89: TYPICAL stress values plus an assumed bias-current bound do not yield a complete PRINTED LIMIT current band. Smallest correction: separate guaranteed terms from assumptions, resolve stress/nonlinearity coverage and component operating conditions, then recompute the cap and remaining margin.",
  "v2/docs/records/l9t5/l9t5_f01.py:295 and :307; l9t5_f01.out:78: Reference loading/junction temperature, actual supply range, amplifier common-mode and remaining loop errors are not fully established. Smallest correction: define the reference preload, component grades and thermal/supply envelope, and allocate all residuals before crediting the accuracy band.",
  "v2/docs/records/l9t5/l9t5_f01.out:91; README.md:26: L9P-F04 closure compares PA-branch current with a shunt limit that also carries U13 BIAS and other loads. Smallest correction: sum all R55 branch currents, including gate-drive demand, and recompute the service-compatible cap using a justified shunt-temperature bound.",
  "v2/docs/records/l9t5/l9t5_f01.out:117 and :141: The transient ceiling and loop confirmation lack a complete plant/compensation design and numerical acceptance. Smallest correction: specify compensation, gate discharge, saturation recovery and acquisition behavior, then bound or measure settling and rail/current excursions against the unchanged service case.",
  "v2/docs/records/l9t5/l9t5_f01.out:97 and :120; README.md:1: The 0.2981 V result is conditional model margin, not closure on printed limits. Smallest correction: retain the reproduced figure with its labels, add control loads and connected-path losses, and combine unresolved gauge, converter, cell, path and 60 s terms in one budget.",
  "v2/docs/records/l9t5/l9t5_f01.out:132; README.md:30: Raising the band has only 44.98 mA apparent room before omitted loads, and adding a lower-VGG-wins RF loop cannot restore output when the current limiter is binding. Smallest correction: remove the claimed fallback until a nonempty overlap between the service-current requirement and the corrected power/current ceiling is established.",
  "v2/docs/records/l9t5/l9t5_f01.out:138: B-PA1/B-PA2 are described as confirmation but decide feasibility and omit necessary envelope and uncertainty coverage. Smallest correction: extend the executable test definition to the cold/hot envelope, actual feed/return drops, available VGG, keying/repeat behavior and applicable load conditions; state specimen transfer limits and retain OPEN until evidence exists.",
  "v2/docs/records/l9t5/l9t5_f01.out:116: The connected consequences omit several loads, return paths and protection interactions; the claimed PA heat ceiling also assumes delivery of 30 W. Smallest correction: add the affected-path checklist and calculations to the correction scope before claiming electrical or thermal closure.",
  "v2/docs/records/l9t5/l9t5_f01.out:28 and :62: The reproduced gauge bounds remain conditional on temperature/reference/shunt assumptions; the calibrated estimate's inferred self-heating is not a printed thermal limit. Smallest correction: retain the reproduction, label these assumptions explicitly in the selection conclusion, and establish the applicable board/shunt envelope. This does not alter the supported rejection of (b) alone."
 ],
 "next_action": "Return the adverse selection finding to the author before further dependent drafting; retain (c) only as a conditional investigation and correct its service, current-budget and evidence claims.",
 "classification": [
  {
   "item": "Q1: Case reproduction and uncertainty labels",
   "class": "MODELLING_ASSUMPTION",
   "evidence": "The specified case reproduces exactly, but its gauge-temperature treatment, DC cell resistance, conversion efficiencies and remaining path/60 s behavior prevent interpreting the reproduced number as a complete printed-limit bound."
  },
  {
   "item": "Q2: Selected correction's power and service bounds",
   "class": "MISSING_EVIDENCE",
   "evidence": "No held limit or measurement establishes 30 W below the cap over the envelope; the claimed accuracy band includes typical stress data and unresolved operating-condition terms, and dynamics are unbounded."
  },
  {
   "item": "Q3: Alternatives and selection rationale",
   "class": "IMPLEMENTATION_DEFECT",
   "evidence": "The reasons for withholding credit from (a) and rejecting (b) alone are substantially supported, but the comparison credits (c) using the same kind of unprinted PA transfer it rejects for (a); the proposed two-loop fallback cannot ensure a service floor."
  },
  {
   "item": "Q4: Connected electrical and thermal consequences",
   "class": "IMPLEMENTATION_DEFECT",
   "evidence": "The U13 comparison omits its output-fed BIAS load, and the comparison does not fully trace new control loads, insertion drops, shared returns, transient protection or thermal duty."
  },
  {
   "item": "Q5: Preservation of requirements and case",
   "class": "OWNER_REQUIREMENT",
   "evidence": "REQ-018, C-ALLTX rev 3, mandatory 30 W service, running fans and REQ-016's window remain binding. No explicit case substitution or floor change was found, but service preservation is unproven. No contradiction between owner requirements is demonstrated."
  }
 ],
 "smallest_next_action": "Correct the selection record to make B-PA1 a feasibility blocker, then establish the overlap between the uncertainty-bounded current required for 30 W and the corrected allowable current/power ceiling, including U13 BIAS; prepare the bounded measurement specification without purchasing or contacting anyone.",
 "closure_criterion": "A supported selection requires an established upper bound on current needed for 30 W no greater than the corrected cap minimum at actual module-terminal conditions; the cap maximum plus every R55 load must remain below U13's minimum limit; the complete C-ALLTX rev 3 budget must satisfy 15.5 V and the indicated 18 A service limit throughout 60 s with fans running and rails regulated. Dynamic acceptance must bound settling and excursions. Physical evidence, if required, must include measurement uncertainty, envelope coverage and justified specimen transfer. Until then F01 and the dependent L9P-F04 closure claim remain OPEN.",
 "owner_decision_required": false,
 "owner_decision": null
}
```
