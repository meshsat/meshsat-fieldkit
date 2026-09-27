# Stream w3t hand-offs (EQ-18, MESHSAT-1357, 27 September 2026)

Stream w3t wrote only `v2/ecad/tools/tx_inhibit.py` and `v2/ecad/tools/tests/test_tx_inhibit.py`. Everything below
belongs to another writer, and is drafted here with the reason it is not applied by w3t. Prototype framing throughout:
nothing is built; the readings are desk readings of main 38dcd764's committed netlists.

## 1. Integrator

- Merge the two files. Then run `drafts/w3t/apply_registry.py --dry-run` from the repository root, read it, run it, and
  `python3 rules_lib.py requirements` in `v2/ecad/tools` (it read 0 errors on a scratch copy with the change applied).
  The script pins tx_inhibit.py's sha256 as it finds it in the tree it runs in and refuses a file without limits (13)
  and (14), so run it after any other change to tx_inhibit.py lands. Then the integration recipe's order: commit the
  config inputs (pcb_rules_coverage.yaml, pcb_requirements.yaml) before rules_status and rules_render.
- Re-take RF-002 (`inhibit_chain_<letter>`) on the six committed netlists at the consolidated re-take. In the stream's
  scratch it reads A FAIL (1, 6, 2), B FAIL (11, 6, 3), C FAIL (1, 5, 0), D FAIL (2, 6, 0), E PASS, P PASS
  (fail, pass, undecided), where main's file read A INCONCLUSIVE (0, 5, 4), B FAIL (10, 3, 7), C INCONCLUSIVE (0, 4, 2),
  D INCONCLUSIVE (0, 6, 2), E PASS, P PASS (`readings/inhibit-chain-before-after.txt`).
- File this folder under `v2/docs/records/w3t/` if a committed page is to cite it (the open item S-48's text names it).

## 2. Board C's author (gen_sch_c.py, boards/c.json): finding W3T-F1

With board C unpowered, TX_INHIBIT_n rises to 1.09 V on its three 100 kOhm pull-downs (A R145, B R59, D R2) against
31 uA of stated pin current, of which board C's U9 and U14 pass 10 uA each (Ioff); the readers' VIL is 0.8 V. Before
U14 the same state read 0.74 V. Recommended remedy, taken by the session as a recommendation for the board C stream to
draw and regenerate with parity (the choice is theirs to record against their files):

- R14 10 k to **2.2 k 1 percent**, and a new **10 k 1 percent** pull-down from TX_INHIBIT_n to GND on board C, beside U9
  and U14. Failed safe: 10.1 k parallel 35 k = 7.84 k, times 31 uA = 0.24 V. With the A-B ribbon out, board B and C's
  fragment: 9.2 k times 20 uA = 0.18 V; board A and D's fragment is unchanged (52.5 k, 11 uA, 0.58 V). Idle HIGH with
  the toggle open: 3.3 V x 7.69 k / 9.89 k = 2.57 V nominal; at the adverse ends (+3V3 at 3.135 V, R14 at 2.222 k, the
  pull-downs low, 31 uA sunk) 2.37 V, above VIH 2.0 V and above the about 2.04 V (U14) and 2.15 V (U9, gen_sch_c.py line 181;
  corrected at integration) this tree reads for their VT+ at 3.3 V. The toggle then sinks 1.6 mA (3.465 V over 2.178 k), under the census's 4 mA pull limit, and C24 (10 nF) with
  R14 gives a 22 us rise into the Schmitt inputs.
- Alternatives checked the same way: (b) B's R59 to 10 k 1 percent with R14 2.2 k (0.26 V; idle 2.41 V adverse; boards B
  and C); (c) the three pull-downs to 47 k with R14 4.7 k (0.51 V; idle 2.27 V adverse; four boards). Each reads the line
  PASS in the walk on an in-memory copy of the netlists; board D's SA868 keying then returns to its own UNDECIDED (the
  released SA_PTT_n threshold its maker does not state).
- For reference, main's idle HIGH is 2.54 V nominal and 2.11 V at the adverse ends: every option widens that margin.

## 3. Engineering questions writer (v2/docs/handover/ENGINEERING-QUESTIONS.md)

EQ-18 is answered by option (a) (the LOGIC row conditioned on In1's wiring, with fixtures both ways and the transcribed
Table 1 as its independent check); its re-take shows a circuit question behind it. Suggested text:

- EQ-18 "Attempts and results": "Stream w3t (27 September 2026) added the SN74LVC1G57 row read only in Figure 7's wiring
  (In1 on its own GND pin), every other wiring UNDECIDED, with SCES414P's II, Ioff and input clamp rows. On main
  38dcd764 the EMCON_HW line reads PASS and TX_INHIBIT_n FAIL (1.09 V failed safe, finding W3T-F1, open item S-48)."
  Status: the tool part is closed; the question moves to W3T-F1.
- A new row (or EQ-18's successor): "TX_INHIBIT_n's pull-downs against round 8's lamp gate", group A (design work),
  layers 8 and 9, boards C (A, B, D), affected RF-002 on A to D and board D's SA868 keying; options (a) to (c) of
  section 2 above; recommended (a); desk work and one regeneration of board C.

## 4. EMCON.md writer (v2/docs/feasibility/EMCON.md)

- Section 4b's paragraph "RF-002's walk on board B's round 8 netlist" says U14 is "a SN74LVC1G57 the walk does not
  model either" and that no model was added: since stream w3t it is modelled, and on main 38dcd764 the TX_INHIBIT_n line
  FAILS on its fail-safe state (W3T-F1) while EMCON_HW PASSES.
- Section 8's tools hand-off "model U14's SN74LVC1G57 pin map (1 In1, 2 GND, 3 In0, 4 Y, 5 VCC, 6 In2)" and the counting
  of U14 pins 3 and 6 (II 1 uA, Ioff 10 uA) are done. Section 4b's L2 sum for EMCON_HW (111.2 uA into 3.23 k, 0.36 V)
  has a TX_INHIBIT_n counterpart now: 31 uA into 35 k, 1.09 V, which fails.

## 5. Registry writer (pcb_rules_coverage.yaml, pcb_requirements.yaml)

`apply_registry.py` (section 1): RF-002's row gets the family in _verdict_why, limits (13) and (14) in its note, a
reading sentence, the new pinned file in _gap_if_applied_alone, and the remediation for (13) and (14); a new SESSION
open item S-nn (S-48 in this tree) for W3T-F1. Why not applied by w3t: one owner per file.

## 6. Not done here, and why

- The 74LVC1G17's VT- is still read at its 3 V row over VCC 3 V to 3.6 V (as since round 6); limit (14) names it.
- Board B's SN74LVC2G06 (TI SCES307J), which EMCON.md section 8 also hands to the tools author, is outside EQ-18 and was
  not modelled; board B's Compute Module radios and cards still read "EMCON does not reach it" through it.
