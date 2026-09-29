# Stream s120: S-120, board A's charge bus against the 30 V charger FETs (MESHSAT-1357)

29 September 2026, branch `fnd/s120` from `main` `e57a7365` (set 12: decision 57's FETs on board A); main `b874b744` (set 13)
merged in at `a757e840` for the second round. **AI engineering work (desk arithmetic on the makers' documents and the
committed netlists), not a qualified review. Prototype design: nothing is built, bought, powered or measured, nothing was
regenerated, no box was used.** The only files this stream commits are in this folder. Figures: `vbus20_bound.out`, from
`vbus20_bound.py` (stdlib plus the tree's netlist parser), byte for byte.

**Second issue** (after the independent check `_scratch/chk-s120/CHECK.md`: not mergeable, three blocking and eleven minor
items; section 12 answers each). What changed: Q7 carries Q8's body diode (B1); the bound is INFERRED wherever it is stated,
the registry included, with its sensitivity and a bench reading of the trip (B2); the new item closes only on a measurement
referred to both bus levels (B3); L1's largest current is buck mode at 60 V (m4), which moves the bound from 23.19 to
**23.20 V**; the fact gate reads 21 facts, VBUS20's whole membership among them (m9).

## 1. The item

S-120 (the independent re-check of stream s117, minor n1): decision 57 moved board A's charger switching FETs Q7 to Q10 from
the 40 V CSD18510Q5B to the 30 V CSD17578Q5A (Q7) and CSD17577Q5A (Q8 to Q10). They sit on the charger's input bus VBUS20,
which the front end U2 (LM5176) makes, and on the pack side. No item bounded the bus's worst case against the FETs' 30 V and
the BQ25731's own limits. S-120 closes "when that worst case is bounded from the front end's own protection or a clamp on
VBUS20, with its figures and pages, or the FETs' rating is restated with the reason."

**The answer is (a): the bound holds in service, from the front end's own protection, and it is INFERRED. VBUS20 stays at
or under 23.20 V while U2 is inside its ratings: at that bound Q8 has 6.80 V and Q7 5.80 V to their 30 V (Q7 holds the bus
plus Q8's body diode), and U3's VBUS pin 8.80 V to its 32 V. The bound rests on the LM5176's over-voltage threshold, which
TI gives only as a typical 10 percent over VREF; 30 V is reached only if the trip sat 37.7 percent over VREF (Q7) or 42.5
percent (Q8). No clamp or setting is added and decision 57 stands. The switch nodes' ringing is not bounded at desk: it is
carried as its own open item, which closes only on the prototype (section 7).**

## 2. The documents (printed page equals the PDF page in each)

| Document | What is read |
|---|---|
| TI SNVSAI1D, LM5176 (revised August 2021), `v2/vendor/ti/lm5176-datasheet.pdf` | 6.1 and 6.3 p.5 (VIN, VISNS, VOSNS 60 V absolute; BIAS 40 V; VIN recommended 55 V); 6.5 p.6 (VREF 0.788 / 0.800 / 0.812 V; IBIAS(FB) 25 nA; fSW(1) 175 / 200 / 225 kHz); p.7 (buck valley limit 66 / 80 / 94 mV, boost peak limit 100 / 120 / 140 mV, IOFFSET(CS/CSG) 19 uA); p.8 (VOVP 10 % typical only, hysteresis 2.5 %); 7.1 p.13, 7.3.1, 7.3.8 p.17 and 7.3.11 p.18 (valley current mode, CCM both ways, OVP's response; no response time given); 7.4.2 p.20 (MODE); 8.2.2.12 p.25 and p.26 (TI's own FET voltage practice) |
| TI SLUSE66A, BQ25731 (revised January 2021), `v2/vendor/ti/bq25731-datasheet.pdf` | pin table pp.5 and 6 (FRS on OTG/VAP/FRS); 8.1 p.8 (absolute: VBUS, ACP, ACN, SRN, SRP, VSYS 32 V; SW1, SW2 -2 to 32 V and -4 V for 25 ns; BTST, HIDRV 38 V; BTST-SW 7 V); 8.3 p.8 (recommended: VBUS, ACP, ACN 26 V; SRN, SRP, VSYS 23.15 V; SW 26 V; BTST 32 V; BTST-SW 6.5 V); 8.5 p.9 (charge voltage 16.8 V, 0.5 %), p.11 (REGN), p.14 (ACOV 26.0 / 26.8 / 27.7 V, 100 us; SYSOVP 4S 19.0 / 19.5 / 20.0 V; BATOVP 105 % max), p.16 (driver resistances), p.18 (CELL_BATPRESZ 4s window 68.4 / 75 / 81.5 % of VDDA); 9.3.9 p.27 (OTG needs the pin high) and Table 9-3 p.27; IN_VAP p.49; EN_OTG p.64; Figure 10-1 p.83; 10.2.2.1 and 10.2.2.2 p.84; Figure 10-3 p.85 (the ACP-ACN filter: RACP and RACN 4.99 Ohm, CDIFF 10 nF, CACP and CACN 33 nF); 10.2.2.4 and 10.2.2.6 p.86 ("30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage"; at most 10 nF + 1 nF after RAC) |
| TI SLPS526, CSD17578Q5A (March 2015) and SLPS516, CSD17577Q5A (August 2014), held back, `v2/vendor/ti/held/` | p.1 (VDS 30 V absolute; EAS 23 and 39 mJ single pulse); 5.1 p.3 (BVDSS 30 V minimum; VSD 0.8 typical, 1.0 V maximum at 18 A; Qgs, Qg(th), RG; Qrr 8.2 nC at 15 V, 18 A, 300 A/us). Pinned by sha256 in `v2/vendor/sources.txt` lines 454 and 455, fetched by `v2/docs/records/s117/fetch_held_back.py`; the copies read here match those sha256 |
| TI SNVS452G, LM5069, `v2/vendor/ti/ti-lm5069.pdf` | 6.5 p.5 (OVLOTH 2.4 / 2.5 / 2.6 V) |
| Littelfuse SMCJ series (revised 11/20/15), `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` | the table on page 2 of 6 (SMCJ18A, SMCJ22A, SMCJ40A) |
| The project's records | `gen_sch_a.py` (the front end's loop model: crossover 0.71 to 3.6 kHz, 89 mOhm, lines 722 to 724); `records/s117/charger_l_f.out` (L2's worst peaks and ripples: A2 15.71 and 4.72 A, G1 14.10 and 4.60 A, A1 10.70 and 3.70 A); `records/s117/efficiency.py` (Q7's plateau reading, INFERRED); `review-packets/battery/FUSE-INTERPRETATION.md` (the pack's 10.0 V CUV) |

No new maker's document was fetched. No TI application note that gives a layout-independent switch-node ringing bound is
held in the tree (searched `v2/vendor/` and `sources.txt`); none was fetched, because the brief asks for it only if held and
a ringing figure depends on a layout that does not exist yet.

## 3. The circuit as generated (`vbus20_bound.out` section 1, 21 of 21 facts)

Parsed from board A's committed netlist (sha256/16 `6c40250c47195ebb`, the same on main `b874b744`) and board E's
(`2ed95a0e8069ebf8`); each detail line prints what the netlist holds. R6 240k 1 % over R7 10k 1 % into U2's FB; VOSNS and
BIAS on VBUS20; MODE pulled to VCC (CCM, hiccup disabled); R11 10 mOhm (ISNS) between FE_OUT and VBUS20, R12 5 mOhm (CS),
with R150 and R151 100 Ohm in front of CS and CSG; L1 10 uH XAL1010-103ME; Q2 drain on VIN_RAW (an idle stage blocks
VIN_RAW). **VBUS20's whole membership, 39 pins**: the six EEHZK1V331P and eighteen 10 uF 50 V ceramics, C192 (U2's BIAS
bypass), R11, R147 and R161 (sense filters), R16 (the charger's RAC), R197 (U34's latch sense), R202 to R205 (the bleed), R6,
TP12, U2 pins 12 and 24 and U3 pin 1: **no diode of any kind, and nothing that drives the bus but U2 through R11**. U3's
OTG/VAP/FRS pin on GND: OTG needs it high (9.3.9 p.27, EN_OTG p.64), VAP too (IN_VAP p.49), FRS too (pin table p.6), so the
charger never drives VBUS20. U3's cell strap R26 13.3k over R27 40.2k puts CELL_BATPRESZ at 74.76 to 75.51 % of VDDA, inside
the 4s window 68.4 to 81.5 % (p.18), which sets SYSOVP at the 4S 19.0 to 20.0 V. Q7 to Q10 as decision 57 draws them. Only
C190 10 nF and C191 1 nF after R16 on CH_ACN, as p.86 allows; CH_ACN_F and CH_ACP_F carry R146 and R147 (10 Ohm) and C121
10 nF but **no capacitor to ground** (Figure 10-3's CACP and CACN, 33 nF, p.85, are not drawn). D1 SMCJ18A on VBAT; D2
SMCJ40A on VIN_RAW; board E's LM5069 OVLO divider (R22 100k, R23 6.65k) and its clamps D10 SMCJ40CA, D1 and D2 SMCJ40A.

## 4. The worst case on VBUS20, mechanism by mechanism

| Mechanism | Figure | Basis |
|---|---|---|
| Regulation, DC band | 19.08 to **20.96 V** (19.33 to 20.69 V with the printed 1 % alone) | VREF 0.788 to 0.812 V (SNVSAI1D p.6); 1 + R6 / R7 at 1 %; 100 ppm/K over 65 K on each resistor, taken in opposite directions (INFERRED: the codes carry no TCR; S-116 uses the same convention); IBIAS(FB) 25 nA through R6 both ways (6.1 mV) |
| Output over-voltage protection | trip 22.00 V nominal, **23.06 V** at VREF maximum and the worst ratio, **INFERRED** | VOVP = VREF + 10 %, TYPICAL only, hysteresis 2.5 % (p.8); it reads FB, so the bus trips at 1.10 x its own regulation. Response: "turns off the gate drives when the feedback voltage is above the output overvoltage threshold" (7.3.11 p.18; 7.1 p.13 says "the high-side drivers"); either stops the input's energy, since Q2 off blocks VIN_RAW. TI gives no response time, and none is needed at this scale: at L1's largest current into the bulk the bus rises at most 18.6 V per ms, so 0.37 ms of full current past the trip (65 cycles at 175 kHz) would be needed to reach 30 V |
| L1's energy after the trip | **+0.14 V to 23.20 V, INFERRED** | L1's largest current inside U2's ratings: buck mode at U2's 60 V, the valley limit (94 mV plus the 1.9 mV IOFFSET(CS/CSG) moves across R150 and R151) over R12 less 1 %, 19.37 A, plus the ripple at the trip with L1 at -20 % and 175 kHz: **29.51 A** (28.94 A at 55 V, 25.30 A at 36 V; the boost peak limit gives 28.67 A); L1 at +20 %: 5.23 mJ into the six bulk parts at -20 % (1.584 mF; the ceramics not counted). L1 saturates at 17.5 A, so the energy is overstated and the figure high |
| Load dump: the charger stops at its full input current | 22.02 V at Option A(i)'s 6.45 A, **22.24 V** at VBUS20's declared 8.0 A (MODEL) | the charger's L2 cannot feed the bus when it stops (Q7 off; its current returns through Q8's body diode, L2 and Q10 to VBAT). The front end sees a load step: dI / (2 pi fc C) with its slowest crossover 0.71 kHz (its loop model, `gen_sch_a.py` 722 to 724) into 1.584 mF, plus L1's 5.23 mJ at its largest current (which overstates what L1 carries at either step); the loop model's own 89 mOhm gives 0.57 to 0.71 V. The stage runs CCM and can sink current (7.3.8 p.17). Below the OVP trip, so OVP need not act; whatever the model's error, the row above caps it |
| The input (what board E delivers) | 9 to 36 V in service (REQ-015); lockout 37.78 / 40.09 / 42.49 V; clamps VBR 44.4 to 49.1 V, VC 64.5 V at 23.3 A | LM5069 OVLOTH 2.4 / 2.5 / 2.6 V over R22 / R23 at 1 % (SNVS452G p.5); four SMCJ40A class parts (board E D10, D1, D2; board A D2; Littelfuse page 2 of 6); the tracker's 15.1 V joins through an ideal diode. U2 regulates the bus for any VIN from 4.2 to 55 V (p.5); a line step from 36 V to U2's 60 V lifts the average inductor current by 1.74 A in valley current mode until the loop answers: **21.21 V** (MODEL). With U2 idle Q2 blocks VIN_RAW. Above 55 V U2 leaves its recommended range and above 60 V its absolute ratings: that is S-111's item, and this bound assumes U2 inside its ratings |
| Clamps | none on VBUS20 (its whole membership read); SMCJ40A class upstream; D1 SMCJ18A on VBAT | section 3 |
| Ringing at the switch nodes | INCONCLUSIVE at desk: a budget, section 7 | no layout; no TI note giving a layout-independent bound held |

**The bus's bound: 23.20 V, INFERRED**, whatever the load, the line or the loop model does, while U2 is inside its ratings.
It rests on a typical-only threshold, so the record states how far that typical would have to be wrong before each limit is
reached (VREF maximum, worst ratio, L1's energy): an OVP 13.8 % over VREF reaches 24 V (80 % of the FETs' 30 V), 23.4 %
reaches 26 V (U3's recommended maximum and ACOV's minimum), **37.7 % reaches Q7's 30 V** (the bus at 29.0 V plus Q8's VSD),
**42.5 % Q8's 30 V** and 52.0 % U3's absolute 32 V, against TI's typical 10 %. The load-dump and line models, which do not use
the OVP at all, read 22.24 and 21.21 V. A bench reading of the trip (FB driven through R6 and R7) replaces the INFERRED
figure; it is in the new item's closing condition (section 7).

## 5. The pack side (Q10's drain, and SW2, which sits at VBAT in buck mode, Table 9-3 p.27)

ChargeVoltage 16.8 V plus 0.5 % = 16.88 V (p.9); BATOVP at most 105 % = 17.64 V (p.14); SYSOVP for 4S (the strap of section
3) turns the converter off at 19.0 / 19.5 / 20.0 V (p.14). A pack that opens while the charger runs at Option A(i)'s 15.71 A:
SYSOVP stops the converter at 20.0 V and L2's 0.70 mJ goes into VBAT's own capacitance (its effective value under bias is not
held: INCONCLUSIVE); D1 SMCJ18A bounds the node at 24.27 V at 15.71 A (INFERRED: the straight line from its 22.10 V breakdown
maximum at 1 mA to its 29.2 V clamp at 51.4 A) and 29.2 V at its own IPP. No source on board A can drive D1's full IPP into
VBAT (the pack is a sink at its own voltage; the charger is limited as above).

## 6. The margins per part (`vbus20_bound.out` section 9; limit minus the figure; ringing comes on top)

| Limit | DC 20.96 V | load dump 22.24 V | bound 23.20 V (INFERRED) |
|---|---|---|---|
| Q8 VDS = SW1, 30 V (SLPS516 p.1) | 9.04 | 7.76 | **6.80** |
| **Q7 VDS = the bus plus Q8's VSD 1.0 V** (SLPS516 p.3), 30 V (SLPS526 p.1) | 8.04 | 6.76 | **5.80** |
| U3 VBUS pin 1, absolute 32 V (p.8) | 11.04 | 9.76 | **8.80** |
| U3 VBUS, ACP, ACN, recommended 26 V (p.8) | 5.04 | 3.76 | 2.80 |
| U3 ACOV rising minimum 26.0 V (p.14): never reached | 5.04 | 3.76 | 2.80 |
| U3 ACP, ACN absolute 32 V, before ringing | 11.04 | 9.76 | 8.80 |
| U3 SW1 absolute 32 V, before ringing | 11.04 | 9.76 | 8.80 |
| U3 SW1 recommended 26 V, before ringing | 5.04 | 3.76 | 2.80 |
| U3 BTST1 absolute 38 V (SW1 plus REGN's 6.3 V) | 10.74 | 9.46 | 8.50 |
| U3 BTST1 recommended 32 V (SW1 plus REGN's 6.3 V) | 4.74 | 3.46 | 2.50 |

Pack side, at the charger's cutoff SYSOVP 20.0 V and at D1 with A2's current 24.27 V: Q9 (VDS = SW2) and Q10 against 30 V
12.36 V at BATOVP, 10.00 at SYSOVP, 5.73 at D1, 0.80 at D1's IPP; **U3 SW2's worst is 7.73 V under its absolute 32 V** (at
D1; 12.00 at SYSOVP; 1.73 and 6.00 under the recommended 26 V), before ringing; U3's VSYS, SRP and SRN 7.73 V under 32 V and
**1.12 V over their RECOMMENDED 23.15 V** at D1 (3.15 V under it at SYSOVP), so in a pack that opens while charging at the
bound current VSYS passes its recommended maximum for the event, not its absolute one; BTST2 (SW2 plus REGN) 7.43 V under
38 V and 1.43 V under the recommended 32 V at D1. BTST to SW is REGN's own 6.3 V at most against 7 V absolute and 6.5 V
recommended, whatever the bus does.

## 7. The switch nodes: a budget, not a bound (INCONCLUSIVE at desk)

What TI states: "30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage" (SLUSE66A 10.2.2.6
p.86), in a topology whose input loop runs through RAC with at most 10 nF + 1 nF after it (p.86, Figure 10-3 p.85), which is
what board A draws; TI's LM5176 example takes 60 V FETs for a 50 V input and 20 V FETs for a 12 V output "and additional
transient spikes" (SNVSAI1D 8.2.2.12 pp.25 and 26). These are the makers' practice, not a bound. Board A's DC band tops out
0.96 V above TI's 20 V. Board A draws R146 and R147 at 10 Ohm with C121 10 nF and not Figure 10-3's CACP and CACN (33 nF to
ground, with 4.99 Ohm, p.85), so U3's ACN pin sees CH_ACN's ring through R146 and C121 alone; U3's VBUS pin 1 sits on VBUS20
itself.

Budget over the steady bus (20.96 V) and over the INFERRED bound (23.20 V): **Q7 8.04 / 5.80 V** (the bus, Q8's VSD in
every dead time, and SW1's ring below it), **Q8 9.04 / 6.80 V** (SW1's overshoot), U3's SW1 11.04 / 8.80 V to 32 V and
5.04 / 2.80 V to its recommended 26 V; below ground U3's SW1 takes -2 V, and -4 V for 25 ns.

A MODEL for the layout writer, not a bound (typical driver figures; the plateau INFERRED):
- **Q7's turn-off** (sets Q7's VDS): its current falls in (Qgs - Qg(th)) / (VPLT / (RDS_HI_OFF + RG)) = 1.4 nC / (2.7 V /
  3.1 Ohm) = 1.61 ns (SLPS526 p.3, SLUSE66A p.16). At Option A(i)'s bound (L2 peak 15.71 A) that is 9.8 A/ns: each nH of the
  loop C190 and C191, Q7, Q8 adds about 9.8 V to Q7, and Q7's budget allows about **0.82 nH** (0.92 nH at the as-generated
  bound G1, 1.21 nH at the energy model's peak A1; 0.52 to 0.76 nH for U3's recommended 26 V). 1 nH between the VBUS20 bank
  (C20 to C22), R16 and C190 lifts CH_ACN by about 4.7 V (I x sqrt(L / 11 nF), growing as the square root of L).
- **Q7's turn-on** (sets Q8's VDS): the current rises in 1.4 nC / ((6.0 - 2.7) V / (6 + 1.8) Ohm) = 3.31 ns (the 6 Ohm
  turn-on driver RDS_HI_ON_Q1, p.16) from the valley current (10.99 A at A2): 3.3 V per nH, so Q8's budget allows about
  2.7 nH at A2 (3.2 at G1, 4.3 at A1) BEFORE Q8's reverse recovery, whose charge TI states only at 300 A/us (Qrr 8.2 nC,
  SLPS516 p.3), about ten times slower than this edge: the recovery ring is INCONCLUSIVE.
- The FETs carry a single-pulse avalanche figure (EAS 23 and 39 mJ, p.1); no repetitive figure is stated, so no margin is
  taken from it.

**This is the one place the 30 V choice is tight**: the old 40 V parts had 10 V more for the same ringing. It is carried by a
new open item (opened by `apply_registry_s120.py`: **S-124** on the line that carries set 13), owned by board A's layout
writer (S-115's pass, where a routed-board reading of both loops' inductance is the layout step and **does not close the
item**) and the bench. It closes only on the prototype: CH_SW1, CH_ACN, CH_SW2 and U3's VBUS pin read at the charger's largest
current, each overshoot (the peak less the measured bus) added to 20.96 V for steady service and to 23.20 V for the
over-voltage excursion, Q7's VDS also carrying Q8's VSD, each result inside 30 V for the FETs and 32 V for U3's pins; and the
front end's OVP trip read on the prototype (FB driven through R6 and R7), which replaces the INFERRED 23.06 V and with it the
23.20 V reference. A snubber, a gate-drive change or FETs of a higher voltage, drawn and read back, are measured the same way.
REQ-015 waits on it in S-120's place.

## 8. Single faults outside every requirement (`vbus20_bound.out` section 11)

ASM-001 refuses "no single point of failure" about the kit and SC-39 sets NEED-03's failure set; no requirement asks board A
to hold the bus through a failed part. Recorded, not bounded. With the charger stopped Q7 and Q8 are off, L2 carries DC, and
Q10's body diode (source CH_SW2, drain VBAT) holds SW2, and SW1 through L2, near VBAT plus a diode: Q7 then holds VBUS20 less
VBAT less VSD, Q8 about VBAT plus VSD (INFERRED).
- **Q2 shorted**: VBUS20 = VIN_RAW less Q5's body diode (about 0.8 V, INFERRED): 35.2 V at 36 V in, 41.7 V at board E's
  lockout maximum. U3's ACOV (26.0 to 27.7 V, 100 us) stops the charger; above 32.8 V in, U3's VBUS, ACP and ACN pass their
  32 V absolute rating, while Q7 reaches 30 V only at VBUS20 = 30 V + VBAT + VSD (40.8 V with the pack at its 10.0 V CUV):
  for a Q2 short U3 is the first part past its rating while the pack is above about 1.2 V.
- **R6 open or FB shorted**: the OVP reads the same pin, so nothing on board A bounds the bus. The charger switches until ACOV
  trips (up to 27.7 V, after its 100 us deglitch), so Q7 holds at least 28.7 V while it still switches, before any rise inside
  the deglitch and before any ringing: **here the FETs may be first, and no order is claimed**. Beyond, the 35 V bulk parts
  and U3's 32 V are passed.

Options for the power review that S-111 names, not taken here: an independent over-voltage trip on VBUS20 (a second divider
into U34's channel 1, re-armed while the stage runs) for the FB faults; an SMCJ22A on VBUS20 (22 V standoff over the 20.96 V
band), which holds a Q2 short at about 28.2 V at board E's 6.15 A hot-swap limit (INFERRED straight line) until the LM5069's
fault timer opens, and clamps 35.5 V at its own IPP. `apply_registry_s120.py` adds this residual to S-111's title, since a
surge past U2's 60 V is one way such a failure could start.

## 9. The choice, and why

**(a), the bound holds, with every figure cited, and labelled INFERRED where it rests on TI's typical-only threshold.** The
bus is bounded by the front end's own protection at 23.20 V with 5.80 V to Q7's 30 V, and the models that do not use the OVP
read 22.24 V. A clamp on VBUS20 would not improve the in-service bound (the bus never reaches a 22 V standoff part's
breakdown) and cannot hold a rated pulse under 30 V (an SMCJ22A clamps 35.5 V at IPP); the LM5176 has no separate OVP input
(its OVP is the FB comparator), so no OVP divider setting exists to change. Restating the FETs to 40 V is not needed for the
bus; for the switch nodes it is one of the remedies the new item names if the bench cannot hold the ringing inside the
budget. No decision is drafted: the FETs' rating stands.

## 10. What the integrator runs

On the runner, on the line that carries set 13 (this branch merged `b874b744`), after merging this branch at `<commit>`:
1. `python3 v2/docs/records/s120/apply_registry_s120.py close <commit> --check`, then without `--check`. It refuses unless the
   four evidence files (README.md, LOG.md, vbus20_bound.py, vbus20_bound.out) are committed and identical at `<commit>` and
   HEAD, `vbus20_bound.py` re-reads 21 of 21 facts on the committed netlists and reprints the committed `.out` (the two sha
   lines aside), S-120 is open and REQ-015 waits on it. It closes S-120 (`closed_by` the full sha), opens the switch-node item
   (S-124 there; the next free S number wherever it runs) in S-120's place in REQ-015's waits_on, and adds the residual to
   S-111's title. A second run refuses.
2. `python3 v2/ecad/tools/rules_lib.py requirements`, then `rules_render.py --requirements` (the integrator's re-take).
No box run is owed: no generator changed, no netlist moves. `fetch_held_back.py` (stream s117) wherever the FET sheets are
wanted.

Dry run (`dryrun.out`, second issue, on the merged line): `--check` on the tree's registry writes nothing; on a scratch copy
the script writes once (S-120 closed with the full sha, S-124 opened, REQ-015 waiting on S-106, S-107, S-111, S-124, S-111's
title extended) and refuses a second run; it refuses a commit that does not carry the records, a missing commit and an
uncommitted change to an evidence file; `rules_lib.py requirements` reads the same errors and warnings on the unmodified and
the applied copy; and `vbus20_bound.py` reads FAIL (exit 1) on four netlist mutants of board A (R6 at 249k, U3's pin 5 off
GND, a diode on VBUS20, a new resistor from VBUS20 to a new net).

## 11. What remains open

- The switch-node item (section 7, S-124): the bench, after board A's layout (S-115).
- The OVP trip level, typical only: carried by the same item's closing condition.
- S-111 (U2 against the VIN_RAW clamps) and, with it, the single-fault residual of section 8: the power review.
- VBAT's effective capacitance under bias (section 5): INCONCLUSIVE; D1 bounds the event.
- Board A's ACP-ACN filter differs from TI's Figure 10-3 (10 Ohm, no CACP and CACN): recorded as a fact and in S-124's
  text; whether the charger's current sensing wants Figure 10-3's parts is board A's writer's to weigh, not this item's.

## 12. The check of stream s120, answered

| Item | Answer |
|---|---|
| B1 Q7's margin | Q7 and Q8 on separate rows everywhere; Q7 carries Q8's VSD 1.0 V (SLPS516 p.3) in the margins, the budgets and the allowances (0.82 / 0.92 / 1.21 nH). With m4's bound Q7 reads 5.80 V at the bound and 6.76 V in the dump (the check's 5.81 and 6.86 V were on 23.19 V and on the dump's first model) |
| B2 the INFERRED label | the `.out` (sections 3, 8, 12), this README and both registry texts write the bound INFERRED with its sensitivity (37.7 % for Q7, 42.5 % for Q8); the OVP trip's bench reading is in the new item's closing condition |
| B3 the item's closure | the routed-board reading is the layout step and does not close the item; it closes only on the prototype, each overshoot added to 20.96 V and to 23.20 V, Q7 carrying VSD, against 30 V for the FETs and 32 V for U3's pins |
| m1 single faults | section 8 rewritten: SW1 near VBAT through Q10's body diode; the order shown for a Q2 short (the pack above about 1.2 V), none claimed for the FB faults |
| m2 SW2 and BTST1 | SW2 is on the pack side, 7.73 V under 32 V at D1; SW1 and ACN "before ringing"; BTST1's 2.50 V is against the recommended 32 V (8.50 V against the absolute 38 V) |
| m3 closed_by | resolved with `git rev-parse` to the full sha |
| m4 L1's current | buck mode at 60 V sets it, 29.51 A with the 1.9 mV offset; the bound is 23.198 V, printed 23.20 V |
| m5 OVP delay | none given; none needed: 18.6 V per ms at most, 0.37 ms of full current past the trip to reach 30 V |
| m6 the dump's L1 energy | L1's energy at its largest current: 22.24 V at 8.0 A, 22.02 V at 6.45 A |
| m7 Q8 and U3's VBUS | Q7's turn-on modelled with the 6 Ohm driver from the valley current; Q8's recovery INCONCLUSIVE; U3's VBUS pin read in the closure; the missing CACP and CACN recorded |
| m8 pages | Figure 10-3 p.85; OTG 9.3.9 p.27 and EN_OTG p.64, VAP IN_VAP p.49, FRS the pin table p.6; ACOV, SYSOVP and BATOVP p.14 |
| m9 the fact gate | detail strings print the netlist; VBUS20's whole membership, the CELL_BATPRESZ strap and the CS filter are facts (21) |
| m10 the S number | main `b874b744` merged; the script opens S-124 on this line |
| m11 LOG.md | the escaped backticks removed |

## Files

`vbus20_bound.py` and `.out` (the figures), `apply_registry_s120.py` (the registry draft), `dryrun.out` (its dry run),
`LOG.md` (the running log), this README.
