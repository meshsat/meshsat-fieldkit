accepted: no

# Layer 4, L4-E4: the one check of board A's current-limit coordination and the outlet's R138 by the engineering collaborator (an AI review, read-only)

Collaborator job `cx13-l4e4-check`, run `20261001T031719Z-1760962`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e4 at commit `85505497dfb2`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E4: NOT YET. The stated arithmetic reproduces, but R16's omitted tolerance defeats the claimed coordination margin, and the outlet ramp test cannot reliably identify the trip threshold without excluding upstream limiting and voltage faults. These are engineering corrections, requiring no owner decision.

## Blocking discrepancies

- B1: The charger bounds omit R16's 1% tolerance. gen_sch_a.py:897 specifies 10 mOhm 1%; lcsc_fill.py:213 maps it to HoJLR2512 C2903468. l4e4_limits.py:172 and :185 treat nominal-resistor controller bounds as board-current bounds. Using the same upper-bound rule with R16 at -1% gives 4.76625/0.99=4.814394 A, or 4.893488 A including the exact 0.079094 A other load. This exceeds the reported hot full-tap minimum 4.874198 A by 19.290 mA, even before R16 TCR. At R16=+1%, the inferred lower bound becomes 4.55/1.01=4.504950 A, below the required 4.517 A. Recompute both bounds with R16 tolerance/TCR and revise the setting and Kelvin allowance together.
- B2: The proposed outlet ramp does not uniquely close the VI(TRIP) ambiguity. L4E4-CURRENT-LIMITS.md:74 specifies only a trip-current window, while l4e4_limits.out:115 acknowledges U19's 4.212 to 5.810 A limit. U19 limiting can collapse VBUS and produce a shutdown inside the accepted window even if U18 uses the higher threshold. SLVSDG8B p.31 explicitly provides voltage-fault shutdown paths. Specify a test that maintains the negotiated bus voltage and records U18's differential sense voltage and gate shutdown, independently of U19 limiting.

## Classification

- **IMPLEMENTATION_DEFECT**: B1: omitted R16 tolerance Evidence: l4e4_limits.py:172 and :185 omit the tolerance explicitly specified by gen_sch_a.py:897; including it reverses both relevant margins.
- **IMPLEMENTATION_DEFECT**: B2: outlet test cannot distinguish shutdown causes Evidence: L4E4-CURRENT-LIMITS.md:74 lacks voltage and differential-sense observations despite the upstream-limit overlap recorded at l4e4_limits.out:115.
- **MISSING_EVIDENCE**: TPS25740A threshold-row conflict Evidence: L4E4-CURRENT-LIMITS.md:49 records SLVSDG8B p.11 conflicting with pp.28 to 31. The intended 3 A row is supported, but confirmed device behaviour remains missing.
- **MODELLING_ASSUMPTION**: R11 temperature and inherited offset envelope Evidence: L4E4-CURRENT-LIMITS.md:21 and :65; r11_dep.py:326 uses typical ISNS bias for the offset, and :587 infers thermal resistance from derating.
- **MISSING_EVIDENCE**: C-7 and C-8 Evidence: L4E4-CURRENT-LIMITS.md:59 and :67 leave 10 mOhm charger accuracy and circuit efficiencies unverified.
- **COMPONENT_LIMITATION**: L1 and bulk-capacitor fault-current limits Evidence: L4E4-CURRENT-LIMITS.md:53 reports 20.74 A against 17.5 A typical Isat and 3.11 A against 2.8 A ripple rating; item 4 retains their closure.
- **MISSING_EVIDENCE**: J_USBC_OUT rating Evidence: L4E4-CURRENT-LIMITS.md:63 and gen_sch_a.py:1306 provide no selected header part or maker current rating.
- **IMPLEMENTATION_DEFECT**: MINOR: tolerance provenance claim Evidence: L4E4-CURRENT-LIMITS.md:7 claims reuse of the tolerance stack, but l4e4_limits.py:201, :239 and :316 repeat its tolerance literals.
- **OWNER_REQUIREMENT**: Preserved solar window and engineering authority Evidence: pcb_requirements.yaml:7688 retains REQ-016; D-24 at :762 and D-25 at :785 assign component selection and sensing implementation to engineering.
- **DESIGN_OBJECTIVE**: 48 to 72 hour endurance target Evidence: pcb_requirements.yaml:7766 identifies REQ-072 as the objective. This task neither changes it nor establishes runtime compliance.

## Smallest next action

B1: include R16 tolerance and TCR in U3's upper and lower bounds, then recompute IIN_HOST and C-1 while retaining 8 mOhm if it still qualifies. A bounded candidate is 4.70 A with a tap allowance below 0.3803 mOhm at 25 C, conditional on extending the same 100 C envelope to R16 and retaining the inferred controller bounds; it is not implemented or verified. B2: amend the ramp procedure to isolate U18's current comparator using a regulated test feed or an equivalent arrangement, while observing differential sense voltage, VBUS and gate shutdown.

## Closure criterion

B1: revised calculations and meaningful corner checks show the charger minimum at least 4.517 A and the front-end minimum above the corrected charger maximum plus 0.079094 A, including both shunts' tolerance/TCR and the declared tap budget; update the register, output and bench thresholds consistently, keeping C-7 conditional until supported or measured. B2: the revised procedure cannot pass on upstream limiting or a voltage fault; eventual measurements must demonstrate the selected differential threshold and corresponding trip current with VBUS regulated, plus sustained 3 A operation on each advertised voltage. Recheck reproduction after those corrections.

## Owner decision required

no

## Checks

- Q1: charger register and accuracy: FAIL. Code 93, 0x5D00, RSNS_RAC=0, 50 mA resolution and 50 to 6350 mA nominal range are correct. max(4.65+0.100, 4.65×1.025)=4.766250 A reproduces the controller-only rule. The p.10 accuracy rows are explicitly for 5 mOhm; the inferred 10 mOhm minimum remains C-7. R16's external 1% tolerance is omitted from both current bounds.
- Q2: R11 arithmetic under the stated model: PASS. Using the author's 4.845344 A demand, the working tap budget is 0.702284 mOhm, or 0.542409 mOhm at 25 C under the assumed 100 C copper envelope. Full-budget minima are 4.975763, 4.927107 and 4.874198 A at -20, 25 and 62.1 C air: margins +0.130419, +0.081763 and +0.028854 A. The 9 mOhm minimum is only 4.679920 A before taps, correctly excluding it. These reproduce the model, not a complete tolerance guarantee.
- Q3: outlet selection and discriminating bench test: FAIL. HIPWR=DVDD, EN9V=GND, PSEL=DVDD and PCTRL=VAUX select 5/9/15 V at 3 A. Tables 4/5, Equation 2 and section 8.3.8.2 support the 19.2 to 22.6 mV row as the intended row, while p.11's conflicting label prevents unconditional confirmation. The calculated window is 3.793445 to 4.575952 A. A shutdown during the proposed ramp need not be this current comparator's trip: U19 can limit first and trigger a voltage fault.
- Q4: unmodified reproduction: INCONCLUSIVE. r11_dep.py exited 1 because fig8_readings() requires a temporary directory and this read-only sandbox has none. This is an execution-environment limitation, not evidence of differing numerical output.
- Q4: reproduction with image I/O in memory: PASS. r11_dep.out reproduced byte for byte, SHA256 f9d2c6f23fab3edcb48ad0116366fe588a514f755aafe56ebd62a0fe9495a209. l4e4_limits.out reproduced byte for byte, SHA256 046ae7d9c620fd1d7f5e3aedad0e2233aabd9695875bcd4e883d4c9dcc489f99. No files were edited.
- Q4: draft script scope and repeat refusal: PASS. R11 changes only the front-end shunt value and order code, plus commentary. R138 changes only its value/order code, commentary and the corresponding PD_SW intent note. Both results parse and both second applications refuse with exit 3. Neither draft was applied to disk.
- Read-only scope: PASS. Worktree remained clean and HEAD remained 85505497dfb2319d58d9bdb6a975d5d6df6e1bc8. No verdict writers or gates were run.

## Evidence and minors

- Q1: Choosing from the declared 0.93×0.93 efficiencies rather than the unsupported 0.97 bracket is reasonable conditional modelling, with C-8 open. However, it does not establish that 4.65 A covers 4.517 A once R16 is included. See v2/docs/records/l4e4/L4E4-CURRENT-LIMITS.md:15 and l4e4_limits.py:172.
- Q2: At 25 C air, 0.0427/[0.008×1.01×(1+50e-6×17.32629)+0.0005424088×(1+0.00393×17.32629)]=4.927107 A. The C-1 budget follows r11_dep.py:434 exactly under its stated assumptions.
- Q2: The reported 0.190 W DC, approximately 0.262 to 0.441 W including the assumed ripple, and 68.44 to 76.81 C in 62.1 C air are internally consistent with the inferred 33.3 K/W. They do not establish actual thermal resistance or validate the assumed 100 C ceiling; this remains correctly disclosed at L4E4-CURRENT-LIMITS.md:65.
- Q3: The intended trip window exceeds every 3 A PDO by at least 0.793445 A and lies 0.424048 A below the Bulgin receptacle's held 5 A rating. The shunt's nominal sqrt(3 W/5 mOhm)=24.495 A and Q27's 42 A rating also exceed it. Q27's rating is conditional on the datasheet's 25 C ambient and specified copper, as the output records. These comparisons do not establish the unspecified header's rating.
- Q4: VSNS, offset, TCR, controller accuracy, auxiliary loads, temperature inputs and stage functions are obtained from the captured r11_dep.main() run at l4e4_limits.py:127. MINOR: the stronger claim that R11's tolerance is also taken from that run is inaccurate: 1.01 and 0.99 are repeated literals at lines 201, 239 and 316. Correct the provenance wording or expose and reuse the tolerance explicitly.
- Q4: No hardware is represented as built, measured or implemented. The drafts and remaining circuit work are explicitly identified at L4E4-CURRENT-LIMITS.md:79. The statement 'nothing blocks' at line 9 needs correction for B1 and B2 below.
- Q5: L1's modelled 20.735 A peak at the 7.262 A output limit exceeds its 17.5 A typical Isat. Item 4 must establish peak current at most 90% of temperature-appropriate Isat, with fault waveforms, or select suitable parts. The bulk estimate is 2.687 A matched and 3.108 A at 2:1 ESR spread against 2.8 A; close it with the actual node analysis over ESR bands and bench ripple measurements. References: L4E4-CURRENT-LIMITS.md:53; L4-ENERGY-ARCHITECTURE.md:165, :181 and :321.
- Q5: C-7 needs supported or measured charger bounds including R16, temperature and configuration. C-8 needs the stage, front-end and charge efficiencies measured or otherwise substantiated and entered into the replay. J_USBC_OUT needs an exact connector/contact selection with a maker rating covering the corrected trip maximum under its operating conditions. References: L4E4-CURRENT-LIMITS.md:59, :63 and :67.
- MINOR: 'Hiccup ... closes these' at L4E4-CURRENT-LIMITS.md:55 is too definite. Hiccup is a candidate remedy; its peak-current and ripple consequences must pass item 4's existing criteria.
