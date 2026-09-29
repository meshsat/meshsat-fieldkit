# Stream s120: S-120, board A's charge bus against the 30 V charger FETs (MESHSAT-1357)

29 September 2026, branch `fnd/s120` from `main` `e57a7365` (set 12: decision 57's FETs on board A). **AI engineering work
(desk arithmetic on the makers' documents and the committed netlists), not a qualified review. Prototype design: nothing is
built, bought, powered or measured, nothing was regenerated, no box was used.** The only files this stream commits are in
this folder. Figures: `vbus20_bound.out`, from `vbus20_bound.py` (stdlib plus the tree's netlist parser), byte for byte.

## 1. The item

S-120 (the independent re-check of stream s117, minor n1): decision 57 moved board A's charger switching FETs Q7 to Q10 from
the 40 V CSD18510Q5B to the 30 V CSD17578Q5A (Q7) and CSD17577Q5A (Q8 to Q10). They sit on the charger's input bus VBUS20,
which the front end U2 (LM5176) makes, and on the pack side. No item bounded the bus's worst case against the FETs' 30 V and
the BQ25731's own limits. S-120 closes "when that worst case is bounded from the front end's own protection or a clamp on
VBUS20, with its figures and pages, or the FETs' rating is restated with the reason."

**The answer is (a): the bound holds in service, from the front end's own protection. VBUS20 stays at or under 23.19 V,
6.81 V under the FETs' 30 V and 8.81 V under the BQ25731's 32 V. No clamp or setting is added and decision 57 stands. The
switch nodes' ringing is not bounded at desk; it is carried as its own open item with its budget (section 7).**

## 2. The documents (printed page equals the PDF page in each)

| Document | What is read |
|---|---|
| TI SNVSAI1D, LM5176 (revised August 2021), `v2/vendor/ti/lm5176-datasheet.pdf` | 6.1 and 6.3 p.5 (ratings: VIN, VISNS, VOSNS 60 V; BIAS 40 V; VIN recommended 55 V); 6.5 p.6 (VREF 0.788 / 0.800 / 0.812 V; IBIAS(FB) 25 nA; fSW(1)); p.7 (current limits: buck valley 66 / 80 / 94 mV, boost peak 100 / 120 / 140 mV); p.8 (VOVP 10 % typical, hysteresis 2.5 %); 7.1 p.13 and 7.3.11 p.18 (OVP's response); 7.4.2 p.20 (MODE); 8.2.2.12 p.25 and p.26 (TI's own FET voltage practice) |
| TI SLUSE66A, BQ25731 (revised January 2021), `v2/vendor/ti/bq25731-datasheet.pdf` | pin table pp.5 and 6 (OTG/VAP/FRS); 8.1 p.8 (absolute: VBUS, ACP, ACN, SRN, SRP, VSYS 32 V; SW1, SW2 -2 to 32 V and -4 V for 25 ns; BTST, HIDRV 38 V; BTST-SW 7 V); 8.3 p.8 (recommended: VBUS, ACP, ACN 26 V; SRN, SRP, VSYS 23.15 V; SW 26 V; BTST 32 V); 8.5 p.9 (charge voltage 16.8 V, 0.5 %), p.11 (REGN), pp.13 and 14 (ACOV 26.0 / 26.8 / 27.7 V, 100 us; SYSOVP 4S 19.0 / 19.5 / 20.0 V; BATOVP 105 % max), p.16 (driver resistances); 10.1 and Figure 10-1 p.83; 10.2.2.1 p.84; 10.2.2.4 and 10.2.2.6 p.86 ("30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage"; at most 10 nF + 1 nF after RAC) |
| TI SLPS526, CSD17578Q5A (March 2015) and SLPS516, CSD17577Q5A (August 2014), held back, `v2/vendor/ti/held/` | p.1 (VDS 30 V absolute; EAS 23 and 39 mJ single pulse); 5.1 p.3 (BVDSS 30 V minimum; Coss, Qgs, Qg(th), RG, VSD). Pinned by sha256 in `v2/vendor/sources.txt` lines 454 and 455, fetched by `v2/docs/records/s117/fetch_held_back.py`; this stream checked the copies it read against those sha256 |
| TI SNVS452G, LM5069, `v2/vendor/ti/ti-lm5069.pdf` | 6.5 p.5 (OVLOTH 2.4 / 2.5 / 2.6 V) |
| Littelfuse SMCJ series (revised 11/20/15), `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` | the table on page 2 of 6 (SMCJ18A, SMCJ22A, SMCJ40A: standoff, breakdown, clamp at IPP) |
| The project's records | `gen_sch_a.py` (the front end's loop model: crossover 0.71 to 3.6 kHz, 89 mOhm, lines 722 to 724; L1 16.2 A at the charger's largest draw, line 751); `records/s117/charger_l_f.out` (L2's worst peaks: A2 15.71 A, G1 14.10 A, A1 10.70 A); `records/s117/efficiency.py` (Q7's plateau reading, INFERRED) |

No new maker's document was fetched. No TI application note that gives a layout-independent switch-node ringing bound is
held in the tree (searched `v2/vendor/` and `sources.txt`); none was fetched, because the brief asks for it only if held and
a ringing figure depends on the layout that does not exist yet.

## 3. The circuit as generated (`vbus20_bound.out` section 1, 18 of 18 facts)

Parsed from board A's committed netlist (sha256/16 `6c40250c47195ebb`) and board E's (`2ed95a0e8069ebf8`): R6 240k 1 % over
R7 10k 1 % into U2's FB; VOSNS and BIAS on VBUS20; MODE pulled to VCC (CCM, hiccup disabled); R11 10 mOhm (ISNS) between
FE_OUT and VBUS20, R12 5 mOhm (CS); L1 10 uH XAL1010-103ME; Q2 drain on VIN_RAW (its body diode points from FE_SW1 to
VIN_RAW, so an idle stage blocks VIN_RAW); six EEHZK1V331P and eighteen 10 uF 50 V ceramics on VBUS20; **no diode of any kind
on VBUS20**; U3's OTG/VAP/FRS pin on GND (OTG, VAP and FRS each need it pulled high, pin table p.6, so the charger never
drives VBUS20); Q7 to Q10 as decision 57 draws them; only C190 10 nF and C191 1 nF after R16 on CH_ACN, as SLUSE66A p.86
allows; D1 SMCJ18A on VBAT; D2 SMCJ40A on VIN_RAW; board E's LM5069 OVLO divider (R22 100k, R23 6.65k) and its clamps D10
SMCJ40CA, D1 and D2 SMCJ40A.

## 4. The worst case on VBUS20, mechanism by mechanism

| Mechanism | Figure | Basis |
|---|---|---|
| Regulation, DC band | 19.08 to **20.96 V** (19.33 to 20.69 V with the printed 1 % alone) | VREF 0.788 to 0.812 V (SNVSAI1D p.6); 1 + R6 / R7 at 1 %; 100 ppm/K over 65 K on each resistor, taken in opposite directions (INFERRED: the codes carry no TCR; S-116 uses the same convention); IBIAS(FB) 25 nA through R6 both ways (6.1 mV) |
| Output over-voltage protection | trip 22.00 V nominal, **23.06 V** at VREF maximum and the worst ratio (INFERRED) | VOVP = VREF + 10 %, TYPICAL only, hysteresis 2.5 % (p.8); it reads FB, so the bus trips at 1.10 x its own regulation. Response: "turns off the gate drives when the feedback voltage is above the output overvoltage threshold" (7.3.11 p.18; 7.1 p.13 says "the high-side drivers"); either stops the input's energy, since Q2 off blocks VIN_RAW. Switching resumes under the threshold less the hysteresis |
| L1's energy after the trip | **+0.13 V to 23.19 V** | the boost peak limit 140 mV over 5 mOhm less 1 % = 28.3 A (p.7), L1 at +20 % (12 uH): 4.80 mJ into the six bulk parts at -20 % (1.584 mF; the ceramics are not counted). L1 saturates at 17.5 A, so the energy is overstated and the figure high |
| Load dump: the charger stops at its full input current | 21.92 V at Option A(i)'s 6.45 A, **22.14 V** at VBUS20's declared 8.0 A (MODEL) | the charger's L2 cannot feed the bus when it stops (Q7 off; its current returns through Q8 and Q10's body diode to VBAT). The front end sees a load step: dI / (2 pi fc C) with its slowest crossover 0.71 kHz (its loop model, `gen_sch_a.py` 722 to 724) into 1.584 mF, plus L1's 1.57 mJ at 16.2 A (line 751); the loop model's own 89 mOhm gives 0.57 to 0.71 V. The stage runs CCM and can sink current (SNVSAI1D 7.3.8). Below the OVP trip, so OVP need not act; whatever the model's error, the row above caps it. While the charger is stopped Q7 and Q8 are not switching |
| The input (what board E delivers) | 9 to 36 V in service (REQ-015); lockout 37.78 / 40.09 / 42.49 V; clamps VBR 44.4 to 49.1 V, VC 64.5 V at 23.3 A | LM5069 OVLOTH 2.4 / 2.5 / 2.6 V over R22 / R23 at 1 % (SNVS452G p.5); four SMCJ40A class parts (board E D10, D1, D2; board A D2; Littelfuse page 2 of 6); the tracker's 15.1 V joins through an ideal diode. U2 regulates the bus for any VIN from 4.2 to 55 V (p.5); a line step from 36 V to U2's 60 V lifts the average inductor current by 1.74 A in valley current mode until the loop answers: **21.21 V** (MODEL). With U2 idle Q2 blocks VIN_RAW. Above 55 V U2 leaves its recommended range and above 60 V its absolute ratings: that is S-111's item, and this bound assumes U2 inside its ratings |
| Clamps | none on VBUS20; SMCJ40A class upstream; D1 SMCJ18A on VBAT | section 3 |
| Ringing at the switch nodes | INCONCLUSIVE at desk: a budget, section 7 | no layout; no TI note giving a layout-independent bound held |

**The bus's bound: 23.19 V**, whatever the load, the line or the loop model does, while U2 is inside its ratings. It rests on
a typical-only threshold, so the record states how far that typical would have to be wrong before each limit is reached
(VREF maximum, worst ratio, L1's energy): an OVP 13.9 % over VREF reaches 24 V (80 % of the FETs' 30 V), 23.4 % reaches 26 V
(U3's recommended maximum and ACOV's minimum), **42.5 % reaches the FETs' 30 V** and 52.1 % U3's absolute 32 V, against TI's
typical 10 %. The load-dump and line models, which do not use the OVP at all, read 22.14 and 21.21 V.

## 5. The pack side (Q10's drain; Q9's drain through Q10 in buck mode)

ChargeVoltage 16.8 V plus 0.5 % = 16.88 V (p.9); BATOVP at most 105 % = 17.64 V (p.14); SYSOVP for 4S turns the converter off
at 19.0 / 19.5 / 20.0 V (p.14). A pack that opens while the charger runs at Option A(i)'s 15.71 A: SYSOVP stops the converter
at 20.0 V and L2's 0.70 mJ goes into VBAT's own capacitance (its effective value under bias is not held: INCONCLUSIVE); D1
SMCJ18A bounds the node at 24.27 V at 15.71 A (INFERRED: the straight line from its 22.10 V breakdown maximum at 1 mA to its
29.2 V clamp at 51.4 A) and 29.2 V at its own IPP. No source on board A can drive D1's full IPP into VBAT (the pack is a sink
at its own voltage; the charger is limited as above).

## 6. The margins (`vbus20_bound.out` section 9; limit minus the figure)

| Limit | DC 20.96 V | load dump 22.14 V | bound 23.19 V |
|---|---|---|---|
| Q7, Q8 VDS 30 V (SLPS526, SLPS516 p.1) | 9.04 | 7.86 | **6.81** |
| U3 VBUS, ACP, ACN absolute 32 V (p.8) | 11.04 | 9.86 | **8.81** |
| U3 VBUS, ACP, ACN recommended 26 V (p.8) | 5.04 | 3.86 | 2.81 |
| U3 ACOV rising minimum 26.0 V (p.14): never reached | 5.04 | 3.86 | 2.81 |
| U3 SW1 absolute 32 V, before ringing | 11.04 | 9.86 | 8.81 |
| U3 SW1 recommended 26 V, before ringing | 5.04 | 3.86 | 2.81 |
| U3 BTST1 absolute 38 V (bus plus REGN's 6.3 V) | 10.74 | 9.56 | 8.51 |
| U3 BTST1 recommended 32 V | 4.74 | 3.56 | 2.51 |

BTST to SW is REGN's own 6.3 V at most against 7 V absolute and 6.5 V recommended, whatever the bus does. Pack side against
30 V: Q9 and Q10 12.36 V at BATOVP, 10.00 V at SYSOVP, 5.73 V at D1 with A2's current, 0.80 V at D1's IPP. U3's VSYS, SRP and
SRN (32 V absolute, 23.15 V recommended): 12.00 / 3.15 V at SYSOVP and 7.73 / -1.12 V at D1 with A2's current, so in a pack
that opens while charging at the bound current VSYS can pass its RECOMMENDED maximum for the event (not its absolute one).
BTST2 rides SW2, which sits at VBAT in buck mode: 26.30 V at SYSOVP plus REGN, 5.70 V under 32 V.

## 7. The switch nodes: a budget, not a bound (INCONCLUSIVE at desk)

What TI states: "30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage" (SLUSE66A 10.2.2.6
p.86), in a topology whose input loop runs through RAC with at most 10 nF + 1 nF after it (p.86; Figure 10-1 p.83), which is
what board A draws; TI's LM5176 example takes 60 V FETs for a 50 V input and 20 V FETs for a 12 V output "and additional
transient spikes" (SNVSAI1D 8.2.2.12 pp.25 and 26). These are the makers' practice, not a bound. Board A's DC band tops out
0.96 V above TI's 20 V.

Budget over the steady bus (20.96 V) and over the bound (23.19 V): **9.04 / 6.81 V to the FETs' 30 V**, 11.04 / 8.81 V to
U3's SW1 absolute 32 V, 5.04 / 2.81 V to its recommended 26 V; below ground U3's SW1 takes -2 V, and -4 V for 25 ns.

A MODEL for the layout writer, not a bound: Q7's current falls in (Qgs - Qg(th)) / (VPLT / (RDS_HI_OFF + RG)) = 1.4 nC /
(2.7 V / 3.1 Ohm) = 1.61 ns (SLPS526 p.3, SLUSE66A p.16 typical, the plateau INFERRED). At Option A(i)'s bound (L2 peak
15.71 A) that is 9.8 A/ns: each nH of the loop C190 and C191, Q7, Q8 adds about 9.8 V, and 1 nH between the VBUS20 bank (C20
to C22), R16 and C190 lifts CH_ACN by about 4.7 V (I x sqrt(L / 11 nF), growing as the square root of L). The 30 V budget
allows about 0.92 nH of the first loop at A2, 1.03 nH at the as-generated bound G1 and 1.36 nH at the energy model's peak A1
(0.52 to 0.76 nH for U3's recommended 26 V). The FETs carry a single-pulse avalanche figure (EAS 23 and 39 mJ, p.1); no
repetitive figure is stated, so no margin is taken from it.

**This is the one place the 30 V choice is tight.** The old 40 V parts had 10 V more for the same ringing. It is carried by a
new open item (opened by `apply_registry_s120.py`, the next free S number), owned by board A's layout writer (S-115's pass)
and the bench, closed by a routed-board reading of both loops' inductance or a prototype measurement of CH_SW1, CH_ACN and
CH_SW2 at the charger's largest current inside the absolute ratings, or by a snubber, a gate-drive change or FETs of a higher
voltage drawn and read back. REQ-015 waits on it in S-120's place.

## 8. Single faults outside every requirement (`vbus20_bound.out` section 11)

ASM-001 refuses "no single point of failure" about the kit and SC-39 sets NEED-03's failure set; no requirement asks board A
to hold the bus through a failed part. Recorded, not bounded:
- **Q2 shorted**: VBUS20 = VIN_RAW less Q5's body diode (about 0.8 V, INFERRED): 35.2 V at 36 V in, 41.7 V at board E's
  lockout maximum. U3's ACOV (26.0 to 27.7 V, 100 us) stops the charger; above 32.8 V in, U3's VBUS, ACP and ACN pass their
  32 V absolute rating. With the charger stopped Q7 and Q8 are both off and share the bus through their leakage and L2 to VBAT
  (INFERRED), so U3 is the first part past its rating, not the FETs.
- **R6 open or FB shorted**: the OVP reads the same pin, so nothing on board A bounds the bus; the 35 V bulk parts and U3's
  32 V are passed.
Neither fault is bounded by the FETs' rating: 40 V parts would not keep U3 inside 32 V. Options for the power review that
S-111 names, not taken here: an independent over-voltage trip on VBUS20 (a second divider into U34's channel 1, re-armed while
the stage runs) for the FB faults; an SMCJ22A on VBUS20 (22 V standoff over the 20.96 V band), which holds a Q2 short at about
28.2 V at board E's 6.15 A hot-swap limit (INFERRED straight line) until the LM5069's fault timer opens, and clamps 35.5 V at
its own IPP. `apply_registry_s120.py` adds this residual to S-111's title, since a surge past U2's 60 V is one way such a
failure could start.

## 9. The choice, and why

**(a), the bound holds, with every figure cited.** The bus is bounded by the front end's own protection at 23.19 V with 6.81 V
to 30 V, and the models that do not use the OVP read 22.14 V. A clamp on VBUS20 would not improve the in-service bound (the
bus never reaches a 22 V standoff part's breakdown) and cannot hold a rated pulse under 30 V (an SMCJ22A clamps 35.5 V at
IPP); the LM5176 has no separate OVP input (its OVP is the FB comparator), so no OVP divider setting exists to change.
Restating the FETs to 40 V is not needed for the bus; for the switch nodes it is one of the remedies the new item names if
the layout or the bench cannot hold the ringing inside the budget. No decision is drafted: the FETs' rating stands.

## 10. What the integrator runs

On the runner, after merging this branch at `<commit>`:
1. `python3 v2/docs/records/s120/apply_registry_s120.py close <commit> --check`, then without `--check`. It refuses unless the
   four evidence files are committed and identical at `<commit>` and HEAD, `vbus20_bound.py` re-reads 18 of 18 facts on the
   committed netlists and reprints the committed `.out` (the two sha lines aside), S-120 is open and REQ-015 waits on it. It
   closes S-120, opens the switch-node item (the next free S number) in S-120's place in REQ-015's waits_on, and adds the
   residual to S-111's title. A second run refuses.
2. `python3 v2/ecad/tools/rules_lib.py requirements`, then `rules_render.py --requirements` (the integrator's re-take).
No box run is owed: no generator changed, no netlist moves. `fetch_held_back.py` (stream s117) wherever the FET sheets are
wanted.

Dry run (`dryrun.out`, at `3ca20d5a`): `--check` on the tree's registry wrote nothing; on a scratch copy the script wrote
once (S-120 closed, S-123 opened on today's registry, REQ-015 waiting on S-106, S-107, S-111, S-123, S-111's title extended)
and refused a second run; it refused a commit that does not carry the records, a missing commit and an uncommitted change
to an evidence file; `rules_lib.py requirements` read 0 errors and 0 warnings on both the unmodified and the applied copy;
and `vbus20_bound.py` read FAIL (exit 1) on three netlist mutants of board A (R6 at 249k, U3's pin 5 off GND, a diode on
VBUS20). The S number is computed at the apply, so it may differ from S-123 if another item lands first.

## 11. What remains open

- The switch-node item (section 7): board A's layout (S-115) and the bench.
- S-111 (U2 against the VIN_RAW clamps) and, with it, the single-fault residual of section 8: the power review.
- The OVP threshold's spread is not published; the conclusion does not depend on it inside 42 %, but a bench reading of the
  trip level (FB driven through the divider) would replace the INFERRED 23.06 V.
- VBAT's effective capacitance under bias (section 5): INCONCLUSIVE; D1 bounds the event.

## Files

`vbus20_bound.py` and `.out` (the figures), `apply_registry_s120.py` (the registry draft), `dryrun.out` (its dry run),
`LOG.md` (the running log), this README.
