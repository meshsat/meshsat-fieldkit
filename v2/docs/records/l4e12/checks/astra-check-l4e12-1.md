accepted: no

# Layer 4, L4-E12: the one check of the electronics against the inside air at the margins by the engineering collaborator (an AI review, read-only)

Collaborator job `cx31-l4e12-check`, run `20261002T030625Z-344227`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l4e12 at commit `bcd2353230bc`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

L4-E12: NOT YET. The principal temperature calculations and cited component limits reproduce. The selected hold changes E3-O's configuration without recorded authority; the absolute-maximum rule does not establish survival and recovery; and the SGP41 shutdown occurs too late under the record's own model. Conductance and component qualification remain conditional feasibility dependencies. Read-only AI review completed.

## Blocking discrepancies

- B1, configuration change without authority: L4E12-ELECTRONICS-THERMAL.md:57-65 changes E3-O to 'started with' monitor and radios on, then permits additional shedding while rejecting EMCON for making radios dark. TEST-PLAN.md:26 contains no 'started with' qualification; :128-133 names only C1's inside-air shedding in this arrangement. C1's documented shedding is not blanket permission to turn off its surviving board D, PA, RockBLOCK, LoRa and E72 functions. D-02a relaxes the performance pass line, not the named configuration. Remove the session-permitted selection at record:245 or obtain an explicit owner-approved deviation. The script's phrase checks at :963-965 and per-part route test at :934-977 do not establish that authority.
- B2, unsupported survival rule: Record:67-70 and l4e12_thermal.py:395-409 call absolute maxima the maker's statement of no damage. TI PCM2912A SLES230A, revised August 2015, p.5 instead identifies stress-only limits, excludes implied functional operation and warns about extended exposure affecting reliability. Its +125 C under-bias figure is real, but does not establish the required four-hour or repeated-dwell recovery. The held TLV755P SBVS320A p.4 likewise distinguishes +150 C absolute junction from +125 C recommended operation; parts supporting logging cannot be cleared merely by staying below absolute maximum. Use these limits as exclusion screens, retain required-operation limits, and mark prolonged-exposure survival INCONCLUSIVE unless supported. Quectel RM520N hardware design V1.1 p.19 provides an actual extended-range recovery statement and can be used with its stated conditions.
- B3, SGP41 transition not protected: Record:148-169 switches the SGP41 off only at the TMP117's +64 C hold trigger. Under the record's own +5.64 K cooler-plume model, that permits mixed air to reach approximately 58.36 C before switching, already 3.36 K above the powered SGP41's absolute +55 C limit. The steady-state unpowered screen does not establish survival of entry into the hold. Specify independent shutdown before the sensor's local +55 C limit, including sensing error and lag, or establish a thermal path that keeps it below that limit. Preserve its required in-envelope function and verify genuinely unpowered storage conditions and the permitted duration before claiming this route closes.

## Classification

- **OWNER_REQUIREMENT**: D-02a, named test configurations, fixed device set and no vents Evidence: pcb_requirements.yaml:393-401,5145-5157,8604-8608,15570-15577; TEST-PLAN.md:26,28,128-133.
- **IMPLEMENTATION_DEFECT**: B1: replacing radios-on exposure with a start condition and additional shutdown Evidence: L4E12-ELECTRONICS-THERMAL.md:57-65,245 contradicts the scope of TEST-PLAN.md:26,128-133.
- **MODELLING_ASSUMPTION**: B2: treating absolute maxima as guaranteed prolonged survival Evidence: Record:67-70; l4e12_thermal.py:395-409; PCM2912A SLES230A p.5 and TLV755P SBVS320A p.4 explicitly qualify those stress ratings.
- **MODELLING_ASSUMPTION**: W4 conductance and local-temperature bounds Evidence: w4-scratch-thermal.py:7-30; l4e12_thermal.py:543-561. The 2.100244 W/K cap is conditional on the chosen geometry and coefficients.
- **MISSING_EVIDENCE**: Actual conductance sufficient for the selected heat load Evidence: Record:197-204,209-211; TEST-PLAN.md:187. No T-H1 measurement exists; the low modeled case cannot satisfy the hold's required conductance.
- **COMPONENT_LIMITATION**: Colliding component ratings and unavailable qualified replacements Evidence: Record:102-111,120-123,133-144,207-208; verified against the held maker documents. A missing qualified replacement does not establish contradictory requirements.
- **IMPLEMENTATION_DEFECT**: B3: SGP41 power-off threshold exceeds its powered temperature allowance Evidence: Record:148-169; l4e12_thermal.py:183,375-376,909-911; Sensirion SGP41 version 1.0 p.7.
- **MISSING_EVIDENCE**: Eleven unrated rows and missing exposure-duration/recovery statements Evidence: l4e12_thermal.out:460-484; record:169-170,207-211; clarification/sensirion-sgp41.txt:10-13 and clarification/pervasive-displays-e2370ks0c1.txt:9-13 are requests, not confirmations.

## Smallest next action

Withdraw the claim that approach (c) is permitted by the existing acceptance. Correct the rating rule and SGP41 transition analysis, retaining the verified arithmetic and explicit feasibility dependencies. Ask the owner only if retaining the proposed configuration deviation.

## Closure criterion

A revised record either conforms to the existing E3-O configuration or cites an explicit owner-approved deviation; makes no unsupported absolute-maximum survival claim; and bounds SGP41 temperature while powered to at most +55 C throughout entry and recovery. U-02 remains conditional until applicable maker evidence covers every fitted item and exposure duration, and thermal evidence supports G at least 2.1587 W/K for the proposed 21.587 W hold load, accounting for uncertainty and local hot spots. Actual E3-O/E5 qualification remains unperformed.

## Owner decision required

yes

Required to retain approach (c), not to conclude that the requirements are impossible: may E3-O include the proposed additional thermal shutdown of board D, PA, RockBLOCK, LoRa and both E72s? Option 1: preserve the existing E3-O configuration, withdraw this selection and leave U-02 open for a compliant engineering solution. Option 2: explicitly approve that additional shedding as a stated configuration deviation, retaining the full four-hour +55 C exposure, CM5 no-shutdown/logging, no-damage/data-preservation and recovery criteria. Approval of Option 2 would not resolve the thermal or component evidence gaps.

## Checks

- Revision and read-only state: PASS. HEAD matches the specified base; no changed files. No verdict writer, generator or test suite was run.
- Author input bindings: PASS. All 62 pinned inputs exist and match. Requirements registry SHA256: b624ac495650a3592c45a37610375fb05bf7b775042cf3de7ec8979bc46a6e50. Owner-instruction SHA256: f39c7f2b08dae370c68fa9e5ed189317722ff64c784423d246b3f17f1befee62.
- Independent steady-state arithmetic: PASS. With 2.09 W ballasts, E3-O/E5 temperatures are: G=1.6664, no hold 71.2542/76.2542 C, hold 67.9543/72.9543 C; G=2.159, no hold 67.5456/72.5456 C, hold 64.9986/69.9986 C. Without ballasts: respectively 70/75, 66.7001/71.7001, 66.5776/71.5776 and 64.0306/69.0306 C. E5 conductance needs are 2.7086 W/K without hold and 2.1587 W/K with hold.
- Held maker limits: PASS. The cited SGP41, ATP19, e-paper and five-member +70 C group temperature numbers are transcribed correctly. This verifies the numbers, not the author's blanket rule for using them.
- Acceptance and rating applicability: FAIL. B1 to B3 below prevent acceptance of the selected route.

## Evidence and minors

- T1: D-02a distinguishes operation to specification inside the envelope from survival and recovery at the margin (v2/ecad/tools/pcb_requirements.yaml:393-401). REQ-051 nevertheless requires the state named by each test row (:15570-15577). TEST-PLAN.md:26 requires four hours at +55 C deployed with monitor and radios on, no damage/deformation/lost data or keys, CM5 throttling logged without shutdown, and recovery. E5 (:28) requires logging throughout its stated cycle and the humidity/recovery pass conditions. E5 does not independently require all radios on. Neither pass line authorizes arbitrary configuration changes.
- T2: The 2.10 W/K result reproduces as 0.09119225*9.5 + 0.13734/(0.018+1/8) + 0.096089/(0.018+1/3) = 2.100244 W/K. This is an upper bound within W4's low-area, low-external-coefficient network after removing internal-film resistance; it still includes polypropylene conduction. W4 explicitly calls its coefficients an inferred sensitivity estimate, not a measured kit model (v2/docs/records/w4/w4-scratch-thermal.py:7-30). It is not a universal upper bound for the sealed case. The high case gives 3.858705 W/K with infinite internal conductance and 2.849602 W/K with the stated finite internal film; high areas with low external coefficients already give a 2.789662 W/K cap.
- T2: At the low-case cap, the hold still gives E5 air at 70.2783 C. Internal fins alone cannot meet 2.1587 W/K under those same assumptions. The author acknowledges this in L4E12-ELECTRONICS-THERMAL.md:197-204. CONDITIONAL is therefore appropriate only as an unresolved feasibility dependency, not evidence that U-02 is physically closed. T-H1 must resolve it in the relevant lid, fan, mounting and temperature conditions. At the selected rounded line the modeled margin is only 0.0014 K; 1 K headroom would require 2.3986 W/K.
- T3: Sensirion sgp41-datasheet.pdf, version 1.0 December 2021, p.7 Table 5 gives +55 C operating and +70 C short-term storage. C&K ck-atp19-series-datasheet.pdf, revision VL 02/05/25, p.1 gives +55 C operating. PDi pdi-e2370ks0c1-flyer.pdf p.1 gives +60 C operation and no storage range. At the modeled E5 air of 76.2542 C and favorable plate bound of 67.5601 C, the reported excesses reproduce: SGP41 21.2542 K at mixed air, ATP19 12.5601 to 21.2542 K, e-paper 7.5601 to 16.2542 K (record:107-109).
- T3: The +70 C group is correctly sourced: RockBLOCK held specification capture dated 20260927, operating; NiceRF SA868 Rev 1.3 p.4, working; LimeSDR held maker capture dated 20260925, storage; Omron G6K held sheet p.3, ambient operating; Pulse H5007NL held sheet p.1, operating. Their mixed-air E5 excess is 6.2542 K. These are different rating categories, not interchangeable guarantees (record:102-106).
- T3: The 11 INCONCLUSIVE rows remain present at the selected condition (l4e12_thermal.out:460-479): headers, HDMI connector, panel LEDs, CR2032, fans, coin-cell holder, fuse holders, QMX, headset jacks, pre-charge pin and grouped header modules. They can overturn feasibility. In particular, unqualified fans could invalidate the assumed heat transfer itself. Obtain exact part identities and applicable powered/storage ratings before all-part closure. PDi's recovery/storage statement and Sensirion's exposure-duration confirmation are also outstanding; the latter is explicitly requested in clarification/sensirion-sgp41.txt:10-13.
- MINOR: The claim that 2.709 W/K exceeds W4's 2.85 W/K top is false (record:27-29,135; l4e12_thermal.py:1145-1146). It exceeds the low-case cap, but is below the high-case finite conductance. Correct that comparison. Approach (a) remains incomplete because passive heat rejection cannot keep powered +55 C parts within rating at +60 C ambient.
- MINOR: Record:193 says ATP19 and e-paper are 'closed by the pick and by PDi's statement', although the replacement and statement are outstanding. Change this to conditional future closure, consistent with :172-174 and :207-208.
- T4: No unavoidable contradiction between mandatory owner requirements has been demonstrated. CHO-001 binds the device choices (v2/ecad/tools/pcb_requirements.yaml:5145-5157); unavailable qualified substitutes are component limitations. The low-case conductance estimate and unanswered maker requests do not prove that every compliant engineering route is impossible.
