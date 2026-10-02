accepted: no

# Layer 4, L4-E8: the one check of the VBUS20 bank re-size by the engineering collaborator (an AI review, read-only)

Collaborator job `cx21-l4e8-check`, run `20261001T173655Z-3640468`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e8 at commit `5ff064743b74`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E8: NOT YET. AI review completed, read-only. The reported 2.739 A corner reproduces, but permitted coincident harmonics give 2.855 A at worst phase. Independent can ESL variation within the stated band gives 3.587 A. Eight cans do not establish B-4 closure. The loop, linear restart estimate and draft composition reproduce within their stated modelling limits.

## Blocking discrepancies

- B1, C1: ripple_dense.py:242, :252 and :372-390 discard complex phase and always add source mean squares. Unsynchronised converters can have coincident harmonics; independent worst-phase calculation gives 2.854635 A at 204/816 kHz, exceeding 2.8 A. Correct the combination and reselect or rebalance the bank using the corrected maximum.
- B2, C1/C3: ripple_dense.py:330-335 assigns identical intrinsic capacitance and ESL to every can. The proposed ESR-only screening and copper matching at L4E8-BANK.md:87-97 do not establish that correlation. Independent intrinsic ESL variation within the stated band gives 3.586976 A. The model also assumes a 6 mOhm ESR floor absent from the maker sheet, and pre-fit 2:1 screening does not establish the lifetime spread asserted at :90-91. Model independent component variations or establish measurable component-screening bounds, including absolute ESR and intrinsic impedance.
- B3, C1: ripple_dense.py:902-905 does not carry the LM5176's absolute frequency row consistently. SNVSAI1D p.6 specifies 175/200/225 kHz at RT=40 kOhm; the code recentres its ratios on Equation 5's 206.05 kHz prediction at 40.2 kOhm and declares 180.29 kHz as the minimum. Scaling the specified row by Equation 5's 40-to-40.2 kOhm ratio instead gives approximately 174.16 to 223.92 kHz, before resistor tolerance. Establish a defensible frequency envelope covering the specified low-frequency corner and rerun the affected checks.
- B4, C4: ripple_dense.py:1106-1116 and L4E8-BANK.md:127-132 do not establish the self-heating cancellation used for the lifetime lower bounds. The sheet's 20 mOhm is a maximum at +20 C, not the actual ESR or rated rise at +125 C. Comparing calculated loss with 157 mW cannot prove actual rise is below rated rise. Use the hybrid lifetime expression with bounded rated and actual temperature rises, or mark the lifetime figures explicitly conditional and assign the missing thermal evidence.

## Classification

- **IMPLEMENTATION_DEFECT**: B1: omitted coherent harmonic cross terms Evidence: v2/docs/records/l4e8/ripple_dense.py:242, :252, :390; independent 204/816 kHz result is 2.854635 A.
- **MODELLING_ASSUMPTION**: B2: identical intrinsic can impedances and maintained ESR spread Evidence: v2/docs/records/l4e8/ripple_dense.py:330-335; v2/docs/records/l4e8/L4E8-BANK.md:89-97. Neither the proposed measurements nor Panasonic pp.1-2 establish these conditions.
- **MODELLING_ASSUMPTION**: B3: LM5176 frequency envelope Evidence: v2/docs/records/l4e8/ripple_dense.py:902-905; held SNVSAI1D pp.6 and 17 do not establish the declared 180.3 kHz lower bound.
- **MISSING_EVIDENCE**: B4: rated and actual capacitor temperature rises Evidence: v2/docs/records/l4e8/ripple_dense.py:1106-1116; v2/docs/records/l4e8/L4E8-BANK.md:127-132; Panasonic ZK sheet pp.2, 5-6.
- **IMPLEMENTATION_DEFECT**: Minor historical attribution and convergence wording Evidence: v2/docs/records/l4e8/CORRECTIONS-DRAFT.md:41-43; v2/docs/records/l4e8/L4E8-BANK.md:47-50; v2/docs/records/l4e8/ripple_dense.py:990-1000.
- **MODELLING_ASSUMPTION**: Minor loop load-envelope scope Evidence: v2/docs/records/l4e8/ripple_dense.py:974 and :1147 retain the historical 5.7 A load for the resized banks.
- **COMPONENT_LIMITATION**: L1 restart qualification and fallback remedy Evidence: v2/docs/records/l4e8/L4E8-BANK.md:154-155; the held Coilcraft sheet p.1 gives a typical 25 C saturation characteristic, while the calculated ten-can restart reaches 18.1275 A.
- **OWNER_REQUIREMENT**: Owner escalation boundary Evidence: v2/ecad/tools/pcb_requirements.yaml:785-803, D-25: component and sensing corrections remain engineering work; owner decisions concern actual requirement or approved-resource changes.

## Smallest next action

B1: preserve complex harmonics and maximize relative phase at coincident frequencies. B2: allow independent can impedances and replace unsupported sharing claims with explicit, measurable qualification bounds. B3: establish the LM5176 frequency limits from the held row and RT tolerance. B4: retain the full hybrid lifetime temperature terms and make unsupported lifetime claims conditional. Then recompute the bank selection, margins and resulting restart obligation.

## Closure criterion

B1: reproduce the 2.854635 A counterexample and demonstrate every selected-bank can at or below 2.7745 A on the corrected worst-phase search. B2: include the 3.586976 A counterexample unless evidence-based component qualification excludes it; every build constraint must bound the corresponding model parameter. B3: document the frequency derivation and rerun ripple and loop checks across its complete bounds. B4: either substantiate rated/actual temperature-rise bounds and recompute lifetime using the maker's equation, or explicitly retain thermal/lifetime status as conditional with a measurable downstream verification. Update the record and correction draft without claiming B-4 closure before the electrical blockers pass.

## Owner decision required

no

## Checks

- Revision, inputs and read-only scope: PASS. HEAD matches the specified base; all pinned inputs match; worktree remains unchanged. Recovered scripts were read, never executed.
- C1 independent eight-can corner: PASS. At VIN 9 V, VBUS20 20 V, VBAT 10 V, Iout 7.2621 A, fFE 198.8 kHz and fCH 816 kHz: cans 396 uF, odd ESR/ESL 6 mOhm/1.5 nH, siblings 12.5 mOhm/2.0 nH including branch mismatch; ceramics 4 uF/2 mOhm/1.5 nH; L11 5 nH, L16 20 nH. Independent FE and charger contributions are 2.088849 and 1.771326 A, yielding 2.738774 A by RSS. The author's function gives 2.738722 A. Increasing 120 harmonics to 240 changes the independent result by less than 0.000001 A.
- C1 worst-phase combination: FAIL. With the preceding passive corner at fFE 204 kHz and fCH 816 kHz, both inside the stated bands, RSS is 2.737510 A but worst-phase RMS is 2.854635 A. Frequency-domain and time-domain results agree. Margin to 2.8 A is -0.054635 A. The 204/408 kHz pair also gives 2.813686 A.
- C3 independent can variation: FAIL. At the reproduced 198.8/816 kHz corner, keeping the odd can at 1.5 nH and assigning siblings 3.5 nH intrinsic ESL plus the allowed 0.5 nH path difference gives 3.586976 A by RSS alone. ESR remains 2:1 and copper mismatch remains within the proposed rule.
- C4 rating and temperature basis: INCONCLUSIVE. The 2.8 A rating at 100 kHz/+125 C and unity frequency correction above 100 kHz are correctly identified. The 62.1 C inside-air input is correctly read. The comparison against 2.8^2 times the 20 mOhm maximum at +20 C does not establish the actual rated-temperature rise needed for the claimed lifetime lower bounds.
- C5 loop and restart arithmetic: PASS. Historical six-can model: PM 73.0157 degrees, GM 15.6797 dB. Eight cans/R12 12 mOhm on the retained 5.7 A sweep: PM 77.4263 degrees, GM 25.6721 dB. Extending that model to 7.2621 A gives GM 23.8256 dB, or 22.0899 dB on the widened band, still above 10 dB. Linear lossless restart estimates at 0.792 V and L=8 uH are 16.3251 A for eight cans and 18.1275 A for ten.
- C6 draft scope and composition: PASS. Both bank options change only the FE bulk argument, preserve ceramics and compensation, refuse second application, and produce identical results in all 24 orders with the R11, R138 and R12 drafts. The release function refuses absent RELEASE.md. No file was written.
- Full six-minute replay: NOT_RUN. The full compute path invokes r11_dep.py, which creates temporary files for PDF rasterization at lines 118-120. It was not executed under this read-only job. Independent calculations and in-memory checks were used; byte-for-byte reproduction of the complete output is not claimed.

## Evidence and minors

- C1 topology and waveform construction agree with the parsed generator/netlist: FE_OUT, R11, VBUS20, R16, CH_ACN; see ripple_dense.py:619-698. Held sources are TI SNVSAI1D pp.17, 23 and 27, and SLUSE66A pp.16 and 85. The individual-source construction is sound; their combination is the blocking defect.
- C2: The source supports the qualitative reconciliation. r11_dep's fixed-network linear scaling omits R11's effect on sharing, while denser frequency sampling can resolve resonance peaks. No constant tuned to force the historical can figures was identified. CORRECTIONS-DRAFT.md:17-23 and :39-43 must nevertheless remain conditional because their replacement figures inherit the phase and sharing defects.
- MINOR C2: CORRECTIONS-DRAFT.md:41-43 presents approximately +4%, +0.5% and -0.3% without identifying the spread to which each applies. ripple_dense.out:149-150 shows different changes for matched and 2:1 cases. Replace these percentages with separate numerical contributions per spread, and label explanations of the lost script's exact grids as inference.
- C3: L4E8-BANK.md:151-155 openly reports the 2.881 A geometry sensitivity, 2.870 A widened-band sensitivity and L1 consequences. These are not hidden. The copper matching rule is measurable through extraction, but does not itself constrain intrinsic capacitor ESL or lifetime ESR spread.
- C4: Under the author's RSS assumptions, the independent corner has 0.061226 A, or 2.187%, margin to 2.8 A. Under the permitted worst-phase example that margin is negative. Unity frequency correction provides no additional allowance.
- MINOR C5: ripple_dense.py:974 retains Iout=[5.7,0.25] and a 114 W impedance bound for the new-bank loop runs at :1147-1148. Therefore 25.7 dB is correctly reproduced for that retained sweep, not a sweep to 7.262 A. Explicitly state this scope or update the load envelope. The independent extended sweep still passes the stated PM/GM thresholds.
- C5: The restart expression at ripple_dense.py:1172-1174 is a sound first-order, constant-inductance, lossless estimate. It is not a saturation-aware bound. The held Coilcraft XAL1010 sheet p.1 defines 17.5 A through a typical 30% inductance drop at 25 C. L4E8-BANK.md:154-155 correctly carries temperature qualification for eight cans and a separate remedy for the ten-can fallback.
- MINOR convergence: ripple_dense.py:990-1000 doubles harmonics and checks finer grids for historical drawn-bank cases. The claim at L4E8-BANK.md:47-50 that every reported maximum receives those checks is broader than the implementation. Narrow the statement or add those checks to the selected-bank cases.
- No genuine contradiction between owner requirements was found. The corrections concern engineering calculations, component qualification and implementation conditions.
