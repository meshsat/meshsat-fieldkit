accepted: no

# Layer 4, L4-E11: the targeted recheck of source-only and dead-pack operation (U-04), the vehicle-entry interconnect (D-06) and the hot swap's fault timer (D-09) by the engineering collaborator (an AI review, read-only)

Collaborator job `cx33-l4e11-recheck`, run `20261002T040500Z-397469`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e11 at commit `cbf8bcb91fd2`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E11: NOT YET. The corrected UVLO calculations, charge/discharge distinction, conditional power envelope and nominal charge-current calculation reproduce. Blocking discrepancies remain in the efficiency floor, protection timing, functional closure, prospective fault-current bound and charge-current specification coverage. Read-only AI review completed; no owner decision is required.

## Blocking discrepancies

- R1/B3, incorrect efficiency acceptance: l4e11_power.py:1064 scales current inversely with efficiency while holding the operating voltage implicitly fixed. With the declared loss model, the boundary is Pout/[Itrip × (9 − Itrip × Rloop)] = 0.908691. The stated 0.906 floor permits nuisance tripping even within that model. Correct the equation, output, C-8 condition and acceptance tests. The remaining static margin also requires bounded component temperatures, losses and transient current before it can be called defensible across tolerances.
- R1/R5, unsupported protection-time bounds: fault_scan at l4e11_power.py:845–867 stops conduction immediately at the SCP threshold or timer endpoint. SLUSEE5E p.10 separately specifies propagation delay and gives 370 us typical at CTMR = 22 nF, versus the model's 322 us. Line 1137 assumes 5 us + 3RC is a universal cutoff bound. It is not: even a simple first-order filter with the stated nominal RC and a 14 A step against the calculated 13.8746 A threshold takes approximately 14.19 us before propagation, approximately 19.19 us including 5 us. Reconcile timer and loaded turn-off timing, include the filter response in the fault scan, and revise E11-17/E11-20 to distinguish trip threshold from peak current. Also update L4-E5 V-A08: its old millisecond response allowance cannot stand against the new approximately 0.25 ms minimum timer.
- R3, functional closure remains unestablished: L4E11-SOURCE-ONLY-AND-ENTRY.md:23–27 and :217–223 support only a conditional comparison against the plan load. The larger load corner is unsupported, and cycling the heater or holding radios has no calculated retained functional/thermal bound. The 61 mW plan margin depends on an undrawn knee, inferred pin accuracy and unverified efficiencies. Replace 'met with drafts' with an explicitly conditional candidate status until a bounded load-shedding sequence demonstrates continued control, successful warm-up and subsequent permitted charging at 9.00 V at the plug.
- R4/B4, inconsistent prospective-current obligation: the specified 51.23398 mOhm floor at 20 C becomes 43.18 mOhm at −20 C and permits 1000 A on the record's voltage basis. E11-15/E11-16 and the final interval nevertheless stop at the nominal-construction result of 883.5 A. Carry the specified worst case through the clearing-I2t and withstand obligations for every protected element, or raise the controlled resistance floor to support the smaller bound. Include measurement and temperature uncertainty in the assembly acceptance.
- R4/B5, incomplete actual-current bound: SLUSE66A p.10 qualifies the 0x0200 accuracy row by VBAT above VSYS_MIN and 0 to 85 C. The record acknowledges the voltage limitation but omits the temperature limitation and extends the bound to '0x0200 or less' without a supported envelope for all permitted settings. Demonstrate the charger's applicable temperature range and current bounds, or keep the unsupported cases INCONCLUSIVE with explicit evidence acceptances. Q2's 124.9 C result remains conditional on those bounds and the installed thermal path.

## Classification

- **OWNER_REQUIREMENT**: Required source operation, cold warm-up and charger-powered charge holds Evidence: pcb_requirements.yaml REQ-015, REQ-024, REQ-046 and REQ-077 preserve these functions; REQ-072's profile does not replace them.
- **COMPONENT_LIMITATION**: LM5069 startup floor Evidence: SNVS452G pp.5 and 24: POREN can be 9.0 V at VIN, independently of divider selection.
- **IMPLEMENTATION_DEFECT**: Efficiency-floor equation and prospective-current propagation Evidence: Independent calculations contradict l4e11_power.py:1064 and the 883.5 A endpoint used by E11-15/E11-16.
- **MODELLING_ASSUMPTION**: Fault waveform and response-time model Evidence: The scan uses ideal slew and immediate threshold cutoff; 3RC is substituted for a justified filter-delay bound.
- **MISSING_EVIDENCE**: Nuisance-trip, source-change and functional warm-up closure Evidence: C-8, inferred pin error, the undrawn knee, new timer coordination and the retained function during R-c shedding are not established by held sources or measurements.
- **MISSING_EVIDENCE**: Charge-hold regulation in S2 Evidence: R-a correctly retains N2 and E11-05/E11-06; the revised permission logic does not supply the missing electrical evidence.
- **MISSING_EVIDENCE**: R-b current coverage and Q2 installed temperature Evidence: SLUSE66A p.10 limits the printed accuracy conditions; SLPS471D p.3 makes thermal performance dependent on the user's board.

## Smallest next action

First replace the efficiency-floor calculation with the coupled voltage/current equation and add a boundary check that reproduces 6.36376 A at efficiency 0.908691. Then propagate the specified cable floor and actual protection timing into the existing bounded acceptances.

## Closure criterion

The corrected record must use mutually consistent efficiency, loss and trip-current bounds; include response and loaded turn-off in the SOA calculation; coordinate L4-E5 transients with the new timer; cover clearing energy through the specified maximum prospective current; and either demonstrate the functional warm-up and permitted charge-current envelope or retain them explicitly as INCONCLUSIVE without claiming REQ-015 closure. Output and focused checks must reproduce the corrected results.

## Owner decision required

no

## Next action (the collaborator's)

The coordinator should correct the coupled loss calculation, protection timing and cable fault bound, then revise the affected acceptances and retain the functional and charge-current evidence gaps explicitly. No requirement change is presently justified.

## Checks

- R1: LM5069 startup: PASS. Drawn rising thresholds are 9.9082/11.1274/12.3725 V; withdrawn divider gives 9.3287/10.5242/11.7447 V. The stated regulated ideal-diode model gives at most 8.987 V at VIN against POREN's 9.0 V maximum. No divider guarantees startup across these limits. VIN is also the current-sense reference. Replacing the controller is the simplest defensible direction among the documented options.
- R1: TPS48110 static thresholds and nuisance-trip margin: FAIL. Under the declared tolerances, UVLO maxima 8.4421/7.9508 V, OV rising 39.5951 to 41.2195 V and OCP 6.36376 to 7.13626 A reproduce. At efficiency 0.93, service current is 6.20023 A, leaving 0.16353 A. The correct static efficiency floor is 0.908691, not 0.906102. At the claimed floor, current reaches 6.38423 A, above minimum OCP.
- R1: resistive-fault SOA and downstream timing: INCONCLUSIVE. The author's scan reproduces 3.038 and 0.685. The finer scan gives approximately 3.03824 and 0.68694. Adding 30 us as a sensitivity gives 3.19937 and 0.71606, still favouring CSD19536KTT. This sensitivity does not establish actual response bounds. E11-19 correctly identifies affected L4-E9 findings, and D-09 is correctly retained only for the LM5069 alternative.
- R2: charge-hold state table: PASS. The logical correction distinguishes charge permission from discharge permission, handles warm CUV explicitly and removes battery supply as REQ-077's substitute. Charge holds use the bit/register rather than either source-removal line. N2 remains explicitly open for S2; this passes the correction check, not electrical verification of source supply.
- R3: plug envelope and functional warm-up: INCONCLUSIVE. The declared 141.525 mOhm model gives 30.3710 to 43.9721 W at 9 V. Warm-up is 21.03/30.31/50.58 W. The plan margin is only 0.0610 W; an additional 0.00331 A of adverse pin-current error consumes it. The knee and guard are statically consistent with L4-E5's mechanism, but its stability, source-change and startup acceptances need the new thresholds and timer.
- R4: weak-source intervals and cable resistance: FAIL. The corrected monotone intervals and 240000/6125/1800 A2s reproduce. Installed contact ratings and total clearing I2t correctly remain evidence obligations. However, the specified resistance floor permits 1000 A at the retained 43.18 V basis, not 883.5 A. Even using the new OV maximum gives approximately 954.6 A.
- R4: R-b and Q2: INCONCLUSIVE. At the specified 0x0200 point, 1.024 × 1.215 / 0.99 = 1.256727 A. With assumed 1 V diode drop and installed 50 C/W, dissipation is 1.256727 W and TJ is 124.936 C. The charger accuracy row applies above VSYS_MIN at 0 to 85 C; the record does not establish that temperature coverage. The below-VSYS_MIN maximum and installed thermal resistance remain unverified.
- R5: output, tests, draft ordering and preservation: PASS. Output is byte-identical and all 20 invoked tests pass. The two tests that write temporary files were not run. In-memory checks confirm hot-swap then entry ordering, timer/hot-swap commutation, entry/timer mutual refusal and guard transformation. These tests do not detect the blocking discrepancies below. Final HEAD is unchanged and git status is clean. No verdict writer was run.

## Evidence and minors

- Requirements register SHA256: b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50. Owner instruction SHA256: f39c7f2b08dae370c68fa9e5ed189317722ff64c784423d246b3f17f1befee62.
- The TPS1663 rejection is supported by its held 5.58 A minimum limit versus the modelled 6.20 A service demand. The replacement architecture remains a reasonable candidate; this review establishes neither a component failure nor a requirement contradiction.
- MINOR: l4e11_power.py:472–482 still computes and asserts the obsolete, incorrect UVLO model before the corrected calculation overwrites its use. Remove that obsolete predicate so future changes are judged only against the corrected equations.
- MINOR: l4e11_power.out:255 says both 63 W and 71.06 W exceed every listed 9 V ceiling, although the listed ceilings include 69.73 W and 72.5 W. Correct the comparison.
- MINOR: The 17.59 W charge allowance is not a general R-b maximum. R-b also remains active above 14 V when XDSG or PRECHARGE is reported. At the record's 16.884 V ceiling, the same current bound gives 21.219 W. DPM still allocates only the available surplus.
- MINOR: R-a's S4 exception says no bit is set, whereas the following paragraph says every hold sets the bit or zero current. Make the exception and hold persistence across state transitions explicit.
