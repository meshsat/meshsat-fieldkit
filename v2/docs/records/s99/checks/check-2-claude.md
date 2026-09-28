# Check of the S-99 correction (commit e7d7f288, branch fnd/s99c): independent AI review (Claude), 28 September 2026

AI review, not a qualified review. Prototype design: nothing built, ordered or measured. Read-only on the worktree; all runs on scratch copies under this folder.

correction accepted: yes (the analysis record), with ONE blocking item before application on fnd/int9: S99-DEV's old text (below)
recommendation supported: yes (option B, the D8 split, as the next circuit candidate; S-99 stays open)

## Per finding

- F1 TPS2596 sign: CLOSED. SLVSET8A (May 2019, rev. August 2019) printed p.28 eq. 7 worked example "903/(1 - 0.0112) = 913.2" proves the minus sign independent of glyph rendering; eq. 7 also reproduces the p.6 typicals (909 ohm 1.0046 A, 453 ohm 2.0046 A). 0.9142 A, 0.956044 / 0.965583 A, P 9.761220 / 9.770759 and 8.171220 / 8.180759 A all reproduce and are propagated through dev_stage, ANALYSIS, RAILS, REGISTRY and the draft comments.
- F2 5.0 mOhm re-rating: CLOSED. 8.514851 / 10.000000 / 11.515152 A initial, 8.468276 / 11.578835 A hot; 5.6 mOhm 7.602546 / 8.928571 / 10.281385, hot max 10.338246 A: all reproduce; "D PASS" is gone, both failures stated (SNVSAI1D p.7, Vishay 30100 pp.1-2 checked).
- F3 timing: CLOSED. 47 us labelled a dimensional ratio; 64.233 / 5.668 / 1.853 ms and 40.6 / 460.1 / 1407.3 V/s labelled illustrative with assumptions and sign; "2 to 60 ms", "far inside" and onset-bound claims removed everywhere; the deciding measurement (simultaneous SS, rail voltage, branch current) named.
- F4 LDO model: CLOSED. IIN = IOUT + IGND stated (DS39724 Rev.2-2 p.8: IQ 55/80 uA at 4.3 V, no load, confirmed); constant power limited to regulating bucks; collapse INCONCLUSIVE with the deciding measurements.
- F5 S2 capacitors: CLOSED. Quectel RM520N HD v1.1 printed p.29 confirmed (3 A / 4 A, two 220 uF, 3.135 V, 100 mV, no duration); 44 uC / 44 us labelled illustrative; no support claim remains.
- F6 S3 shutdown: CLOSED. DS41979 Rev.5-2 p.6 ISHDN 1 / 3 uA at VEN = 0 V with its conditions confirmed; 4.201349 A, margin 0.798651 A, labelled conditional; branch and back-power left to board B.
- F7 PoE off state: CLOSED. SLUSBX9I (rev. July 2019) p.7 IVPWR 3.5 / 7 mA at 57 V confirmed and relabelled; REQ-017 kept; A/B circuit owners added; "plausible rating" removed.
- F8 thermal: CLOSED. SLPS414B p.3 conditions confirmed (tr/tf 6 ns at VDS 50 V, VGS 10 V, 17 A, RG 0; RDS 5.7 mOhm max at 6 V; RthJA on the 1 in2 pad); 112 C labelled a scenario; PT-4 now carries the temperature and switching-waveform measurements.
- F9 stale draft note: PARTLY. On the held line: closed (the new block drops U23, states D8 supplied separately and 7.056897 A; --check and AST pass). For fnd/int9: CORRECTION.md lines 179-183 give an "expected s98" line that occurs 0 times in fnd/int9's gen_sch_a.py (the integrated note is longer and five INTERIM I-03 comment lines precede it). Exact texts below.
- F10 arithmetic, counts, authority: CLOSED. 0.321691 / 0.324908 W, 2.670648 A (5.088 V, 15.5 V, 0.90), ten references, five replacements, both B and B plus the interlock named, SESSION choice not justified by uniqueness.

## Blocking item

1. v2/docs/records/s99/apply_d8_split_draft.py line 69 (S99-DEV "old") and CORRECTION.md lines 179-183: on fnd/int9 (da844ef2) the committed draft's --check fails: "AssertionError: ('S99-DEV', 'old text must occur exactly once in the original')", and CORRECTION.md's expected s98 line also occurs 0 times. Replace S99-DEV "old" with the exact fnd/int9 block below (gen_sch_a.py lines 125 to 135, sha256 of the block plus a trailing newline e25c6e47...). Keep "new" as committed (it is CORRECTION.md's new block verbatim). With that one change, --check on a copy of fnd/int9's gen_sch_a.py passes all five entries (the other four anchors occur once there; the ten new references and +5V_D8IN are unused), and the AST of the result gives +5V_DEV 4.1 / 6.9 A, loads {J_5V_DEV 3.8, U32 0.3} (S-98's 3.8 A kept, typical recomputed without D8), +5V_D8IN 1.0 / 2.0 A from VBAT via U41, U23 on +5V_D8IN, VBAT gains U41 0.4 A.

Exact old text for fnd/int9 (lines 125 to 135 of v2/ecad/tools/gen_sch_a.py at da844ef2):

```python
# F-PR-04, 26 September 2026: the device rail's converter is an LM5176 stage now, not an AP64500. W2 found this
# rail declared at 6.0 A peak on a 5 A part (VERIFIED) and summed its loads to the same 6.0 A (INFERRED); D-12 adds
# the Glenair host port's own eFuse U32 (0.9 A limit) behind it, so the peak is 6.9 A. The LM5176 stage's average
# current loop holds 43 to 57 mV across its 6 mOhm ISNS shunt R43 (SNVSAI1D, VSNS), 7.2 to 9.5 A, above the 6.9 A
# peak and below the JST-VH lead's 10 A. The loads now name board A's own two eFuses as well as the lead to B.
# INTERIM I-03 (S-98, 28 September 2026): typical 5.1 A = board B's 3.8 A arriving at J_5V_DEV + the D8 mezzanine's 1.0 A
# behind U23 + the wall port's 0.3 A allocation behind U32; the PS-ALLTX mode current is INCONCLUSIVE (records/cx1).
# The 6.9 A peak is HELD AS IS: open item S-99 (stream s99) decides it. It is board B's 6.0 A plus the wall port's 0.9 A
# with the D8 mezzanine at zero; the coincident figures are 7.9 A (D8 at its 1.0 A typical) and 8.9 A (every declared
# limit), both above the LM5176 average loop's 7.10 A minimum (the ISNS shunt at +1 percent), which is S-99's question.
_intent.rail("+5V_DEV", 5.0, 5.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U23": 1.0, "U32": 0.3}, budget=0.02, share=0.005, switch="U7", efficiency=0.90, fed_from="VBAT", note="the USB devices, the LimeSDR bay and the RockBLOCK behind their switches, the D8 mezzanine behind U23 and the wall host port behind U32; the net starts at the ISNS shunt R43. 9 September 2026 (ARCH-PCB-B-IOHA): +0.8 A because B16's three hub banks had to leave the slot rails. 26 September 2026 (F-PR-04, D-12): the converter is an LM5176 stage with a 7.2 A minimum average limit (7.10 A with the ISNS shunt at +1 percent, 7.17 A nominal: SNVSAI1D VSNS 43 mV over 6 mOhm), and the declared peak became 6.9 A, board B's 6.0 A plus the Glenair port's 0.9 A with the D8 mezzanine at zero. 28 September 2026 (S-98, finding I-03, INTERIM): the typical is 5.1 A, board B's 3.8 A at J_5V_DEV plus the D8 mezzanine's 1.0 A behind U23 plus the wall port's 0.3 A allocation behind U32; the PS-ALLTX mode current is INCONCLUSIVE (v2/docs/records/cx1/CORRECTION.md B2). The 6.9 A peak is held pending S-99: the coincident figures are 7.9 A with D8 at its typical and 8.9 A at every declared limit, both above the loop's minimum.")
```

Exact new text (unchanged from the committed draft and CORRECTION.md lines 187-195):

```python
# S-99 (28 September 2026): D8 leaves +5V_DEV for its own buck U41 and eFuse U23 on +5V_D8IN.
# The remaining loads are board B and the wall port: 4.1 A typical, 6.9 A declared peak (B 6.0 + wall 0.9).
# R43 6 mOhm gives 7.095710 to 9.595960 A at initial +/-1 percent; with assumed 50 K and +/-110 ppm/K
# it gives 7.056897 to 9.649029 A (SNVSAI1D p.7, Vishay 30100 pp.1-2). The declared margin is 0.156897 A.
# Conditional M-tier 5.942235 A passes by 1.114661 A; P-tier 8.171220 A (8.180759 A with R186 tolerance)
# fails the minimum. S-98 reconciliation and prototype current, timing, collapse/recovery and thermal tests remain.
_intent.rail("+5V_DEV", 5.0, 4.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U32": 0.3}, budget=0.02, share=0.005, switch="U7", efficiency=0.90, fed_from="VBAT", note="the USB devices, LimeSDR bay and RockBLOCK behind board B's switches, plus the wall host port behind U32; D8 is supplied separately by U41 through U23 from +5V_D8IN. The net starts at the output ISNS shunt R43. LM5176 minimum average limit is 7.095710 A with initial +/-1 percent, or 7.056897 A with the assumed 50 K shunt temperature change and +/-110 ppm/K TCR. The 6.9 A declared peak (B 6.0 + wall 0.9) has 0.156897 A conditional margin; actual mode current, M/P reconciliation, timing, collapse/recovery and temperatures remain unverified (S-99).")
```

(The same two blocks are filed byte for byte as int9_old_block.txt and int9_new_block.txt beside this file.) Optional wording nit for int9: S-98 is closed there (31d5edfe, declaration consistency only), so the new comment's "S-98 reconciliation" reads better as "I-03's M/P adequacy"; this does not change any figure.

## Non-blocking items for the integrator (found here, outside the ten findings)

- The wrong sign also lives in the generator: fnd/int9 gen_sch_a.py line 1255 (efuse helper comment "RILM = 903 / (ILIM + 0.0112)"), and R186's label and notes at lines 1544, 1548, 1552 ("0.89 A"). The correction names the stale label but no draft entry corrects it. Its consequence: the declared wall peak 0.9 A (and so +5V_DEV's 6.9 A) rests on 0.89 A; at the corrected 0.9142 A nominal the declared-tier margin is 0.142697 A (0.100853 A at the 909 row high estimate, 0.091314 A with R186 at minus 1 percent), still under the 7.056897 A minimum, so the recommendation stands.
- The layout generator is not touched or named: fnd/int9 gen_pcb_a3.py line 312 refuses a board with unplaced parts (U41, L13, C227 to C232, R217, R218 have no placement) and lines 583 to 586 build a +5V_DEV copper island from U23, R100 and C103, which move to +5V_D8IN. Needed before board A's layout phase; the schematic-phase regeneration is not affected.
- New buck check (item 4b): SLUSEA4D confirms IOUT 3 A (p.5), IHS_LIMIT 4.2 / 5 / 5.8 A (p.6), ILS_LIMIT 2.9 / 3.8 / 4.5 A (p.7, not cited in the record), Table 10-2 p.32: 5 V at 500 kHz 6.8 uH, 20 uF typical and 10 uF minimum effective COUT, SS at least 6.8 nF. At 2.0 A, 16.8 V: ripple 1.043 A, peak 2.52 A (2.65 A with L at minus 20 percent), valley 1.48 A: margins hold; XAL6060-682ME Isat 9.2 A, Irms 7.0 A (887-1 p.1). Not established: the "about 30 uF effective" of two 22 uF 10 V 1210 at 5 V (no DC-bias source cited), U41's own loss and temperature (RthJA_EVM 60.2 C/W is EVM-only, p.6), the 0.90 efficiency of the new rail (project figure). U41's output worst case 4.90 to 5.28 V (VFB 784 to 816 mV over TJ, 1 percent resistors) stays under U23's OVLO 5.87 V; board D declares v_work 5.23 V, which the upper corner exceeds by 0.05 V.
- VBAT (item 4c): the draft adds U41 0.4 A (1.0 A x 5.088 / (0.9 x 14.4) = 0.393 A) but keeps Q32 at 2.0 A, sized for the pre-split typical (5.1 A gives 2.00 A; 4.1 A gives 1.61 A): D8's input is counted twice, about 0.39 A, conservative. The 2.0 A peak draws 0.912 A at 12.4 V.
- IF-AB-POWER (item 4a): the split changes only board A's converter side; J_5V_DEV stays 3.8 A typical and B's 6.0 A peak. REGISTRY-DRAFT.md section 3 cites gen_sch_b.py:97 (line 111 on int9) and calls the child-peak tier "S-98's reconciliation"; S-99 condition (c) (REGISTRY-DRAFT.md line 47) quotes the LDO parents at 0.05 A, which fnd/int9 already sets to 0.12 A. IF-AD-HARNESS needs no change (U23 stays the source; D's 1.0 / 2.0 A unchanged).
- Wording: ANALYSIS.md line 288 "regulated at the load's end" is not accurate (U41 regulates on board A, before U23 and the lead); the draft's docstring line 23 says no XAL6060 is fitted on board A, but XAL6060-472ME is (the slot rails), only -682ME is new. VSNS 43 / 50 / 57 mV is specified at VISNS(-) = 24 V; the stage senses at 5.088 V, so holding the band there is an assumption the record does not name.

## Items 2 and 3

Operating points: every figure changed by the correction names its point (loop limits with tolerance and the assumed 50 K; VBAT current at 5.088 V, 15.5 V, 0.90; R43 loss at the M-tier current; new buck at 16.8 V and 500 kHz), and every timing and thermal figure is labelled an estimate or scenario with the measurement that decides it (PT-2, PT-4). Small gaps: "+0.4 A typical" for U41 omits its VBAT (14.4 V) and efficiency.

Recommendation: after correction the split holds: declared 6.900 A under 7.056897 A by 0.156897 A (thin, named so), M 5.942235 A by 1.114661 A; P 8.171220 A (8.180759 A) still fails and is stated open with what decides it (reconciliation, a guaranteed 1 kOhm limit, measured coincident current); collapse, timing and thermal stay open with their measurements. B plus the wall-port interlock is named standing. The two-part test is applied correctly: for B the first half fails (no reserved.json class names gen_sch_a.py, no purchase, no kit claim changed, the P-tier left open rather than accepted), so it is the session's; the standing rule of 26 September is cited for choosing between the two standing configurations.

## What I ran (all on scratch copies)

- apply_d8_split_draft.py --check on the held gen_sch_a.py (sha 9684e7a9...): exit 0, last line "CHECK ONLY: 5 entries, 1 generator; no writes, no marker."; file hash unchanged, no marker.
- The same on fnd/int9's gen_sch_a.py (sha ebb5c0f2...): exit 1, last line "AssertionError: ('S99-DEV', 'old text must occur exactly once in the original')"; no write.
- A scratch variant with only S99-DEV "old" replaced by the int9 block: exit 0, last line "CHECK ONLY: 5 entries, 1 generator; no writes, no marker."; AST of the result as stated above.
- dev_stage.py in a scratch tree with the four pinned inputs: exit 0 twice, output byte identical to dev_stage.out (sha256 9113fdbf2f9d8e951f3b21d86ca30e6c112154e59bc2ab1991670b5f826bddde). One byte appended to the B intent: exit 1, empty stdout, "Refused: input v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json: sha256 mismatch; expected 96ee391b..., got f886d707...". R43 renamed in the netlist copy: exit 1, "Refused: input v2/ecad/pcb-a-power-a23/out/pcb-a-power.net: sha256 mismatch ...". Restored run identical.
- A probe (not a reproduction: a re-pinned copy) on fnd/int9's four inputs: every D, M, P, split and margin figure is unchanged; only B's declared load sum (5.49 A), A's declaration line and the LDO parent entries (0.12 A, so the "S-98 M7" label is stale there) differ.
- Independent arithmetic (Python fractions and floats) for every key number in the brief: all reproduce.
- pdftotext on SLVSET8A pp.6, 28; SNVSAI1D p.7; Vishay 30100 pp.1-2; SLUSEA4D pp.5-7, 32; Coilcraft 887-1 p.1; DS39724 p.8; DS41979 p.6; SLUSBX9I p.7; SLPS414B p.3; Quectel RM520N HD v1.1 p.29.

## Not checked

correction_checks.py was not run (it creates a scratch folder inside the worktree); its parts (a) and (b) were reproduced above. No suite, no KiCad, no regeneration, no gen_pcb_a3.py run. U41's thermal and the output capacitors' DC-bias derating have no held source. One shell call used "cd /" by mistake (read-only grep, nothing written).
