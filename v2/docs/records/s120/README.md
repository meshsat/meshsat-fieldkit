# Stream s120: S-120, board A's charge bus against the 30 V charger FETs (MESHSAT-1357)

29 September 2026, branch `fnd/s120` from `main` `e57a7365` (set 12: decision 57's FETs on board A); main `b874b744` (set 13)
merged in at `a757e840` for the second round. **AI engineering work (desk arithmetic on the makers' documents and the
committed netlists), not a qualified review. Prototype design: nothing is built, bought, powered or measured, nothing was
regenerated, no box was used.** The only files this stream commits are in this folder. Figures: `vbus20_bound.out`, from
`vbus20_bound.py` (stdlib plus the tree's netlist parser), byte for byte.

**Third issue** (after the re-check `_scratch/chk-s120/CHECK-2.md`: not mergeable, one blocking and seven minor items;
section 12 answers them with round 1's). What changed in this issue: the new item's closing test and rating list carry U3's
negative SW limits, -2 V and -4 V for at most 25 ns, and the `.out` models SW1's undershoot (B1); the Q2 short's order is
claimed only once the charger has stopped (n1); the bound takes a first on-time of a period after a valley crossing and moves
from 23.20 to **23.40 V** (n2); the 26 V allowance sits on Q7's turn-on edge (n3); the fact gate's lines print what they
read and U3's input sense filter leaves the gate for a record line (n4, n5); labels and wording (n6, n7).

## 1. The item

S-120 (the independent re-check of stream s117, minor n1): decision 57 moved board A's charger switching FETs Q7 to Q10 from
the 40 V CSD18510Q5B to the 30 V CSD17578Q5A (Q7) and CSD17577Q5A (Q8 to Q10). They sit on the charger's input bus VBUS20,
which the front end U2 (LM5176) makes, and on the pack side. No item bounded the bus's worst case against the FETs' 30 V and
the BQ25731's own limits. S-120 closes "when that worst case is bounded from the front end's own protection or a clamp on
VBUS20, with its figures and pages, or the FETs' rating is restated with the reason."

**The answer is (a): the bound holds in service, from the front end's own protection, and it is INFERRED. VBUS20 stays at
or under 23.40 V while U2 is inside its ratings: at that bound Q8 has 6.60 V and Q7 5.60 V to their 30 V (Q7 holds the bus
plus Q8's body diode), and U3's VBUS pin 8.60 V to its 32 V. The bound rests on the LM5176's over-voltage threshold, which
TI gives only as a typical 10 percent over VREF, plus a MODEL term for L1's energy; 30 V is reached only if the trip sat 36.7
percent over VREF (Q7) or 41.5 percent (Q8). No clamp or setting is added and decision 57 stands. The switch nodes (their
ringing, and SW1's undershoot against U3's -2 V and -4 V) are not bounded at desk: they are carried as their own open item,
which closes only on the prototype (section 7).**

## 2. The documents (printed page equals the PDF page in each)

| Document | What is read |
|---|---|
| TI SNVSAI1D, LM5176 (revised August 2021), `v2/vendor/ti/lm5176-datasheet.pdf` | 6.1 and 6.3 p.5 (VIN, VISNS, VOSNS 60 V absolute; BIAS 40 V; VIN recommended 55 V); 6.5 p.6 (VREF 0.788 / 0.800 / 0.812 V; IBIAS(FB) 25 nA; fSW(1) 175 / 200 / 225 kHz); p.7 (buck valley limit 66 / 80 / 94 mV, boost peak limit 100 / 120 / 140 mV, IOFFSET(CS/CSG) 19 uA); p.8 (VOVP 10 % typical only, hysteresis 2.5 %); 7.1 p.13; 7.3.1 p.14 (the buck high side "turned on by the PWM comparator at the valley of the inductor ripple current and turned off by the oscillator clock signal"); 7.3.5 p.16 ("The high-side buck switch skips a cycle if the sensed voltage does not fall below this threshold"); 7.3.8 p.17; 7.3.11 p.18 (OVP's response; no response time given); 7.4.2 p.20 (MODE); 8.2.2.12 p.25 and p.26 (TI's own FET voltage practice) |
| TI SLUSE66A, BQ25731 (revised January 2021), `v2/vendor/ti/bq25731-datasheet.pdf` | pin table pp.5 and 6 (FRS on OTG/VAP/FRS); 8.1 p.8 (absolute: VBUS, ACP, ACN, SRN, SRP, VSYS 32 V; SW1, SW2 -2 to 32 V and -4 V for 25 ns; BTST, HIDRV 38 V; BTST-SW 7 V); 8.3 p.8 (recommended: VBUS, ACP, ACN 26 V; SRN, SRP, VSYS 23.15 V; SW 26 V; BTST 32 V; BTST-SW 6.5 V); 8.5 p.9 (charge voltage 16.8 V, 0.5 %), p.11 (REGN), p.14 (ACOV 26.0 / 26.8 / 27.7 V, 100 us; SYSOVP 4S 19.0 / 19.5 / 20.0 V; BATOVP 105 % max), p.16 (driver resistances), p.18 (CELL_BATPRESZ 4s window 68.4 / 75 / 81.5 % of VDDA); 9.3.9 p.27 (OTG needs the pin high) and Table 9-3 p.27; IN_VAP p.49; EN_OTG p.64; Figure 10-1 p.83; 10.2.2.1 and 10.2.2.2 p.84; Figure 10-3 p.85 (the ACP-ACN filter: RACP and RACN 4.99 Ohm, CDIFF 10 nF, CACP and CACN 33 nF); 10.2.2.4 and 10.2.2.6 p.86 ("30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage"; at most 10 nF + 1 nF after RAC) |
| TI SLPS526, CSD17578Q5A (March 2015) and SLPS516, CSD17577Q5A (August 2014), held back, `v2/vendor/ti/held/` | p.1 (VDS 30 V absolute; EAS 23 and 39 mJ single pulse); 5.1 p.3 (BVDSS 30 V minimum; VSD 0.8 typical, 1.0 V maximum at 18 A; Qgs, Qg(th), RG; Qrr 8.2 nC at 15 V, 18 A, 300 A/us). Pinned by sha256 in `v2/vendor/sources.txt` lines 454 and 455, fetched by `v2/docs/records/s117/fetch_held_back.py`; the copies read here match those sha256 |
| TI SNVS452G, LM5069, `v2/vendor/ti/ti-lm5069.pdf` | 6.5 p.5 (OVLOTH 2.4 / 2.5 / 2.6 V) |
| Littelfuse SMCJ series (revised 11/20/15), `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` | the table on page 2 of 6 (SMCJ18A, SMCJ22A, SMCJ40A) |
| The project's records | `gen_sch_a.py` (the front end's loop model: crossover 0.71 to 3.6 kHz, 89 mOhm, lines 722 to 724; L1 16.2 A at the charger's largest draw, line 751); `records/s117/charger_l_f.out` (L2's worst peaks and ripples: A2 15.71 and 4.72 A, G1 14.10 and 4.60 A, A1 10.70 and 3.70 A); `records/s117/efficiency.py` (Q7's plateau reading, INFERRED); `review-packets/battery/FUSE-INTERPRETATION.md` (the pack's 10.0 V CUV) |

No new maker's document was fetched. No TI application note that gives a layout-independent switch-node ringing bound is
held in the tree (searched `v2/vendor/` and `sources.txt`); none was fetched, because the brief asks for it only if held and
a ringing figure depends on a layout that does not exist yet.

## 3. The circuit as generated (`vbus20_bound.out` section 1, 20 of 20 facts and two record lines)

Parsed from board A's committed netlist (sha256/16 `6c40250c47195ebb`, the same on main `b874b744`) and board E's
(`2ed95a0e8069ebf8`); each detail line prints what the netlist holds, and a figure in it is computed from the values read
(the cell strap's percentages from R26's and R27's parsed values and tolerances). The gate holds only what the bound rests on:
R6 240k 1 % over R7 10k 1 % into U2's FB; VOSNS and BIAS on VBUS20; MODE pulled to VCC (CCM, hiccup disabled); R11 10 mOhm
(ISNS) between FE_OUT and VBUS20, R12 5 mOhm (CS), with at most 100 Ohm in front of CS and CSG (R150, R151); L1 10 uH
XAL1010-103ME; Q2 drain on VIN_RAW (an idle stage blocks VIN_RAW). **VBUS20's whole membership, 39 pins**: the six
EEHZK1V331P and eighteen 10 uF 50 V ceramics, C192 (U2's BIAS bypass), R11, R147 and R161 (sense filters), R16 (the charger's
RAC), R197 (U34's latch sense), R202 to R205 (the bleed), R6, TP12, U2 pins 12 and 24 and U3 pin 1: **no diode of any kind,
and nothing that drives the bus but U2 through R11**. A new part on VBUS20 refuses the closure until the list is re-read,
since any member could source or clamp the bus. U3's OTG/VAP/FRS pin on GND: OTG needs it high (9.3.9 p.27, EN_OTG p.64),
VAP too (IN_VAP p.49), FRS too (pin table p.6), so the charger never drives VBUS20. U3's cell strap puts CELL_BATPRESZ at
74.76 to 75.51 % of VDDA, inside the 4s window 68.4 to 81.5 % (p.18), which sets SYSOVP at the 4S 19.0 to 20.0 V. Q7 to Q10
as decision 57 draws them. Only C190 10 nF and C191 1 nF after R16 on CH_ACN, as p.86 allows. D1 SMCJ18A on VBAT; D2 SMCJ40A
on VIN_RAW; board E's LM5069 OVLO divider (R22 100k, R23 6.65k) and its clamps D10 SMCJ40CA, D1 and D2 SMCJ40A.

**Record lines, not gated** (the re-check's n5: a gate on their absence would refuse the closure if board A's writer added
TI's parts): CH_ACN_F and CH_ACP_F hold R146 and R147 (10 Ohm), C121 10 nF and U3's pins, and no capacitor to GND
(Figure 10-3's CACP and CACN, 33 nF, p.85, are not drawn).

## 4. The worst case on VBUS20, mechanism by mechanism

| Mechanism | Figure | Basis |
|---|---|---|
| Regulation, DC band | 19.08 to **20.96 V** (19.33 to 20.69 V with the printed 1 % alone) | VREF 0.788 to 0.812 V (SNVSAI1D p.6); 1 + R6 / R7 at 1 %; 100 ppm/K over 65 K on each resistor, taken in opposite directions (INFERRED: the codes carry no TCR; S-116 uses the same convention); IBIAS(FB) 25 nA through R6 both ways (6.1 mV) |
| Output over-voltage protection | trip 22.00 V nominal, **23.06 V** at VREF maximum and the worst ratio, **INFERRED** | VOVP = VREF + 10 %, TYPICAL only, hysteresis 2.5 % (p.8); it reads FB, so the bus trips at 1.10 x its own regulation. Response: "turns off the gate drives when the feedback voltage is above the output overvoltage threshold" (7.3.11 p.18; 7.1 p.13 says "the high-side drivers"); either stops the input's energy, since Q2 off blocks VIN_RAW |
| L1's energy after the trip, steady current-limit cycle | 23.20 V | the steady cycle's peak inside U2's ratings: buck mode at U2's 60 V, the valley limit (94 mV plus the 1.9 mV IOFFSET(CS/CSG) moves across R150 and R151) over R12 less 1 %, 19.37 A, plus the ripple at the trip with L1 at -20 % and 175 kHz: 29.51 A (28.94 A at 55 V, 25.30 A at 36 V; the boost peak limit gives 28.67 A); L1 at +20 %: 5.23 mJ into the six bulk parts at -20 % (1.584 mF; ceramics not counted) |
| L1's energy after the trip, first on-time (the re-check's n2) | **23.40 V, the bound, INFERRED with a MODEL term** | the LM5176 limits the buck VALLEY only (7.3.5 p.16) and turns the high side off at the clock (7.3.1 p.14), so the first on-time after a valley crossing can last up to a period: from the 19.37 A valley at 60 V for a full period of 175 kHz with L1 at -20 %, 45.76 A; with 12 uH (unsaturated, where L1's Isat is 17.5 A) 12.57 mJ. The term weighs little: to put the bus at 29.0 V from the trip L1 would have to deliver 245 mJ, 20 times this. Response time: TI gives none, and none is needed at this scale: at 45.76 A into the bulk the bus rises at most 28.9 V per ms, so 0.24 ms of full current past the trip (42 cycles) would be needed to reach 30 V |
| Load dump: the charger stops at its full input current | 22.02 V at Option A(i)'s 6.45 A, **22.24 V** at VBUS20's declared 8.0 A (MODEL) | the charger's L2 cannot feed the bus when it stops (Q7 off; its current returns through Q8's body diode, L2 and Q10 to VBAT). The front end sees a load step: dI / (2 pi fc C) with its slowest crossover 0.71 kHz (its loop model, `gen_sch_a.py` 722 to 724) into 1.584 mF, plus L1's 5.23 mJ of the steady cycle, which overstates what L1 carries at either step (16.2 A at 9 V in, line 751); the loop model's own 89 mOhm gives 0.57 to 0.71 V. The stage runs CCM and can sink current (7.3.8 p.17). Below the OVP trip, so OVP need not act; whatever the model's error, the bound caps it |
| The input (what board E delivers) | 9 to 36 V in service (REQ-015); lockout 37.78 / 40.09 / 42.49 V; clamps VBR 44.4 to 49.1 V, VC 64.5 V at 23.3 A | LM5069 OVLOTH 2.4 / 2.5 / 2.6 V over R22 / R23 at 1 % (SNVS452G p.5); four SMCJ40A class parts (board E D10, D1, D2; board A D2; Littelfuse page 2 of 6); the tracker's 15.1 V joins through an ideal diode. U2 regulates the bus for any VIN from 4.2 to 55 V (p.5); a line step from 36 V to U2's 60 V lifts the average inductor current by 1.74 A in valley current mode until the loop answers: **21.21 V** (MODEL). With U2 idle Q2 blocks VIN_RAW. Above 55 V U2 leaves its recommended range and above 60 V its absolute ratings: that is S-111's item, and this bound assumes U2 inside its ratings |
| Clamps | none on VBUS20 (its whole membership read); SMCJ40A class upstream; D1 SMCJ18A on VBAT | section 3 |
| The switch nodes | INCONCLUSIVE at desk: a budget, section 7 | no layout; no TI note giving a layout-independent bound held |

**The bus's bound: 23.40 V, INFERRED**, whatever the load, the line or the loop model does, while U2 is inside its ratings.
It rests on a typical-only threshold, so the record states how far that typical would have to be wrong before each limit is
reached (VREF maximum, worst ratio, L1's first-on-time energy): an OVP 12.9 % over VREF reaches 24 V (80 % of the FETs' 30 V),
22.4 % reaches 26 V (U3's recommended maximum and ACOV's minimum), **36.7 % reaches Q7's 30 V** (the bus at 29.0 V plus Q8's
VSD), **41.5 % Q8's 30 V** and 51.1 % U3's absolute 32 V, against TI's typical 10 %. The load-dump and line models, which do
not use the OVP at all, read 22.24 and 21.21 V. A bench reading of the trip (FB driven through R6 and R7) replaces the
INFERRED figure; it is in the new item's closing condition (section 7).

## 5. The pack side (Q10's drain, and SW2, which sits at VBAT in buck mode, Table 9-3 p.27)

ChargeVoltage 16.8 V plus 0.5 % = 16.88 V (p.9); BATOVP at most 105 % = 17.64 V (p.14); SYSOVP for 4S (the strap of section
3) turns the converter off at 19.0 / 19.5 / 20.0 V (p.14). A pack that opens while the charger runs at Option A(i)'s 15.71 A:
SYSOVP stops the converter at 20.0 V and L2's 0.70 mJ goes into VBAT's own capacitance (its effective value under bias is not
held: INCONCLUSIVE); D1 SMCJ18A bounds the node at 24.27 V at 15.71 A (INFERRED: the straight line from its 22.10 V breakdown
maximum at 1 mA to its 29.2 V clamp at 51.4 A) and 29.2 V at its own IPP. No source on board A can drive D1's full IPP into
VBAT (the pack is a sink at its own voltage; the charger is limited as above).

## 6. The margins per part (`vbus20_bound.out` section 9; limit minus the figure; ringing comes on top)

| Limit | DC 20.96 V | load dump 22.24 V (MODEL) | bound 23.40 V (INFERRED) |
|---|---|---|---|
| Q8 VDS = SW1, 30 V (SLPS516 p.1) | 9.04 | 7.76 | **6.60** |
| **Q7 VDS = the bus plus Q8's VSD 1.0 V** (SLPS516 p.3), 30 V (SLPS526 p.1) | 8.04 | 6.76 | **5.60** |
| U3 VBUS pin 1, absolute 32 V (p.8) | 11.04 | 9.76 | **8.60** |
| U3 VBUS, ACP, ACN, recommended 26 V (p.8) | 5.04 | 3.76 | 2.60 |
| U3 ACOV rising minimum 26.0 V (p.14): not reached at the INFERRED bound | 5.04 | 3.76 | 2.60 |
| U3 ACP, ACN absolute 32 V, before ringing | 11.04 | 9.76 | 8.60 |
| U3 SW1 absolute 32 V, before ringing | 11.04 | 9.76 | 8.60 |
| U3 SW1 recommended 26 V, before ringing | 5.04 | 3.76 | 2.60 |
| U3 BTST1 absolute 38 V (SW1 plus REGN's 6.3 V) | 10.74 | 9.46 | 8.30 |
| U3 BTST1 recommended 32 V (SW1 plus REGN's 6.3 V) | 4.74 | 3.46 | 2.30 |

Pack side, at the charger's cutoff SYSOVP 20.0 V and at D1 with A2's current 24.27 V: Q9 (VDS = SW2) and Q10 against 30 V
12.36 V at BATOVP, 10.00 at SYSOVP, 5.73 at D1, 0.80 at D1's IPP; **U3 SW2's worst is 7.73 V under its absolute 32 V** (at
D1; 12.00 at SYSOVP; 1.73 and 6.00 under the recommended 26 V), before ringing; U3's VSYS, SRP and SRN 7.73 V under 32 V and
**1.12 V over their RECOMMENDED 23.15 V** at D1 (3.15 V under it at SYSOVP), so in a pack that opens while charging at the
bound current VSYS passes its recommended maximum for the event, not its absolute one; BTST2 (SW2 plus REGN) 7.43 V under
38 V and 1.43 V under the recommended 32 V at D1. BTST to SW is REGN's own 6.3 V at most against 7 V absolute and 6.5 V
recommended, whatever the bus does. Below ground, SW1 and SW2 take -2 V, and -4 V for at most 25 ns (p.8): section 7.

## 7. The switch nodes: a budget, not a bound (INCONCLUSIVE at desk)

What TI states: "30 V or higher voltage rating MOSFETs are preferred for 19-V to 20-V input voltage" (SLUSE66A 10.2.2.6
p.86), in a topology whose input loop runs through RAC with at most 10 nF + 1 nF after it (p.86, Figure 10-3 p.85), which is
what board A draws; TI's LM5176 example takes 60 V FETs for a 50 V input and 20 V FETs for a 12 V output "and additional
transient spikes" (SNVSAI1D 8.2.2.12 pp.25 and 26). These are the makers' practice, not a bound. Board A's DC band tops out
0.96 V above TI's 20 V. Board A as generated draws no capacitor from CH_ACN_F or CH_ACP_F to GND (the record lines of section
3), so U3's ACN pin sees CH_ACN's ring through R146 and C121 alone; U3's VBUS pin 1 sits on VBUS20 itself.

Budget over the steady bus (20.96 V) and over the INFERRED bound (23.40 V): **Q7 8.04 / 5.60 V** (the bus, Q8's VSD in
every dead time, and SW1's ring below it), **Q8 9.04 / 6.60 V** (SW1's overshoot), U3's SW1 11.04 / 8.60 V to 32 V and
5.04 / 2.60 V to its recommended 26 V. **Below PGND**: in every dead time SW1 sits at minus Q8's VSD (1.0 V maximum), inside
U3's -2 V; the ring below that has **3.0 V to -4 V, for at most 25 ns**.

A MODEL for the layout writer, not a bound (typical driver figures; the plateau INFERRED):
- **Q7's turn-off** (sets Q7's VDS and SW1's undershoot): its current falls in (Qgs - Qg(th)) / (VPLT / (RDS_HI_OFF + RG))
  = 1.4 nC / (2.7 V / 3.1 Ohm) = 1.61 ns (SLPS526 p.3, SLUSE66A p.16). At Option A(i)'s bound (L2 peak 15.71 A) that is
  9.8 A/ns: each nH of the loop C190 and C191, Q7, Q8 adds about 9.8 V to Q7, whose budget allows about **0.82 nH** (0.92 at
  the as-generated bound G1, 1.21 at the energy model's peak A1); each nH between Q8's source and U3's PGND takes SW1 as much
  further below minus VSD, which the -4 V limit allows for about **0.31 nH** (0.34 at G1, 0.45 at A1), **the tightest figure
  of the model** (the re-check's B1, its own arithmetic reproduced); 1 nH between the VBUS20 bank (C20 to C22), R16 and C190
  lifts CH_ACN by about 4.7 V (I x sqrt(L / 11 nF), growing as the square root of L).
- **Q7's turn-on** (sets Q8's VDS and SW1's overshoot): the current rises in 1.4 nC / ((6.0 - 2.7) V / (6 + 1.8) Ohm) =
  3.31 ns (the 6 Ohm turn-on driver RDS_HI_ON_Q1, p.16) from the valley current (10.99 A at A2): 3.3 V per nH, so Q8's 30 V
  budget allows about 2.72 nH and U3's SW1 recommended 26 V about 1.52 nH at A2 (3.15 and 1.76 at G1, 4.27 and 2.38 at A1),
  both BEFORE Q8's reverse recovery, whose charge TI states only at 300 A/us (Qrr 8.2 nC, SLPS516 p.3), about ten times
  slower than this edge: the recovery ring is INCONCLUSIVE.
- The FETs carry a single-pulse avalanche figure (EAS 23 and 39 mJ, p.1); no repetitive figure is stated, so no margin is
  taken from it.

**This is where the 30 V choice is tight**: the old 40 V parts had 10 V more for the same ringing (the negative SW limits are
U3's and do not depend on the FETs). It is carried by a new open item (opened by `apply_registry_s120.py`: **S-124** on the
line that carries set 13), owned by board A's layout writer (S-115's pass, where a routed-board reading of the loops'
inductance is the layout step and **does not close the item**) and the bench. Its closing condition, as the script writes it:

> Closed only on the prototype: CH_SW1, CH_ACN, CH_SW2 and U3's VBUS pin read against U3's PGND at the charger's largest
> current; Q7's VDS taken from CH_ACN to CH_SW1 (CH_ACN's peak less CH_SW1's lowest, which already holds Q8's body diode) and
> Q8's from CH_SW1's peak; each overshoot over the measured bus added to 20.96 V for steady service and to 23.40 V for the
> over-voltage excursion; each FET's VDS then inside 30 V, U3's VBUS, ACP, ACN, SW1 and SW2 inside 32 V, and CH_SW1 and
> CH_SW2 no lower than -2 V, or -4 V for at most 25 ns (SLUSE66A page 8); and the front end's OVP trip read on the prototype
> (FB driven through R6 and R7), which replaces the INFERRED 23.06 V and with it the 23.40 V reference. A snubber, a
> gate-drive change or FETs of a higher voltage, drawn and read back on the regenerated netlist, are measured the same way.

REQ-015 waits on it in S-120's place.

## 8. Single faults outside every requirement (`vbus20_bound.out` section 11)

ASM-001 refuses "no single point of failure" about the kit and SC-39 sets NEED-03's failure set; no requirement asks board A
to hold the bus through a failed part. Recorded, not bounded. With the charger stopped Q7 and Q8 are off, L2 carries DC, and
Q10's body diode (source CH_SW2, drain VBAT) holds SW2, and SW1 through L2, near VBAT plus a diode: Q7 then holds VBUS20 less
VBAT less VSD, Q8 about VBAT plus VSD (INFERRED).
- **Q2 shorted**: VBUS20 = VIN_RAW less Q5's body diode (about 0.8 V, INFERRED): 35.2 V at 36 V in, 41.7 V at board E's
  lockout maximum. On the way the bus passes ACOV's 26.0 to 27.7 V while the charger still switches (the 100 us deglitch,
  p.14), and Q7 then holds the bus plus Q8's VSD, 28.7 V or more before any ringing: **no order is claimed for that phase**.
  Once ACOV has stopped the charger, U3's VBUS, ACP and ACN pass their 32 V absolute rating above 32.8 V in, while Q7 reaches
  30 V only at VBUS20 = 30 V + VBAT + VSD (40.8 V with the pack at its 10.0 V CUV): from then on U3 is the first part past its
  rating while the pack is above about 1.2 V.
- **R6 open or FB shorted**: the OVP reads the same pin, so nothing on board A bounds the bus. The charger switches until ACOV
  trips (up to 27.7 V, after its 100 us deglitch), so Q7 holds at least 28.7 V while it still switches, before any rise
  inside the deglitch and before any ringing: **the FETs may be first, and no order is claimed**. Beyond, the 35 V bulk parts
  and U3's 32 V are passed.

Options for the power review that S-111 names, not taken here: an independent over-voltage trip on VBUS20 (a second divider
into U34's channel 1, re-armed while the stage runs) for the FB faults; an SMCJ22A on VBUS20 (22 V standoff over the 20.96 V
band), which holds a Q2 short at about 28.2 V at board E's 6.15 A hot-swap limit (INFERRED straight line) until the LM5069's
fault timer opens, and clamps 35.5 V at its own IPP. `apply_registry_s120.py` adds this residual to S-111's title, since a
surge past U2's 60 V is one way such a failure could start.

## 9. The choice, and why

**(a), the bound holds, with every figure cited, and labelled INFERRED where it rests on TI's typical-only threshold.** The
bus is bounded by the front end's own protection at 23.40 V with 5.60 V to Q7's 30 V, and the models that do not use the OVP
read 22.24 V. A clamp on VBUS20 would not improve the in-service bound (at the INFERRED bound the bus stays under a 22 V
standoff part's 24.4 V minimum breakdown) and cannot hold a rated pulse under 30 V (an SMCJ22A clamps 35.5 V at IPP); the
LM5176 has no separate OVP input (its OVP is the FB comparator), so no OVP divider setting exists to change. Restating the
FETs to 40 V is not needed for the bus; for the switch nodes it is one of the remedies the new item names if the bench cannot
hold the ringing inside the budget. No decision is drafted: the FETs' rating stands.

## 10. What the integrator runs

**Which commit:** pass the tip of `fnd/s120` or a merge that carries it. An earlier commit of this branch is refused (the
re-check found `a757e840` and `5078ee24` refused): the evidence gate asks that README.md, LOG.md, vbus20_bound.py and
vbus20_bound.out be byte for byte the same at `<commit>` and at HEAD.

On the runner, on the line that carries set 13 (this branch merged `b874b744`), after merging this branch at `<commit>`:
1. `python3 v2/docs/records/s120/apply_registry_s120.py close <commit> --check`, then without `--check`. It refuses unless
   the four evidence files are committed and identical at `<commit>` and HEAD, `vbus20_bound.py` re-reads 20 of 20 facts on the
   committed netlists and reprints the committed `.out` (the two sha lines aside), S-120 is open and REQ-015 waits on it. It
   closes S-120 (`closed_by` the full sha), opens the switch-node item (S-124 there; the next free S number wherever it runs)
   in S-120's place in REQ-015's waits_on, and adds the residual to S-111's title. A second run refuses.
2. `python3 v2/ecad/tools/rules_lib.py requirements`, then `rules_render.py --requirements` (the integrator's re-take).
No box run is owed: no generator changed, no netlist moves. `fetch_held_back.py` (stream s117) wherever the FET sheets are
wanted.

Dry run (`dryrun.out`, third issue, on the merged line): `--check` on the tree's registry writes nothing; on a scratch copy
the script writes once (S-120 closed with the full sha, S-124 opened, REQ-015 waiting on S-106, S-107, S-111, S-124, S-111's
title extended) and refuses a second run; it refuses a commit that does not carry the records, an earlier commit of this
branch, a missing commit and an uncommitted change to an evidence file; `rules_lib.py requirements` reads the same errors and
warnings on the unmodified and the applied copy; `vbus20_bound.py` reads FAIL (exit 1) on the gated mutants (R6 at 249k, U3's
pin 5 off GND, a diode on VBUS20, a new part on VBUS20, R27 at 20.0k) and PASS (exit 0) on TI's 33 nF CACN added, which its
record line shows.

## 11. What remains open

- The switch-node item (section 7, S-124): the bench, after board A's layout (S-115); SW1's undershoot is the tightest model
  figure.
- The OVP trip level, typical only: carried by the same item's closing condition.
- S-111 (U2 against the VIN_RAW clamps) and, with it, the single-fault residual of section 8: the power review.
- VBAT's effective capacitance under bias (section 5): INCONCLUSIVE; D1 bounds the event.
- Board A's ACP-ACN filter differs from TI's Figure 10-3 (10 Ohm, no CACP and CACN): recorded, not gated; whether the
  charger's current sensing wants Figure 10-3's parts is board A's writer's to weigh, not this item's.

## 12. The checks of stream s120, answered

The re-check `CHECK-2.md` (round 2):

| Item | Answer |
|---|---|
| B1 negative SW limits | S-124's rating list and closing test carry SW1 and SW2 no lower than -2 V, or -4 V for at most 25 ns, against U3's PGND (p.8); `.out` section 10 models SW1's undershoot at Q7's turn-off (MODEL): 0.31 / 0.34 / 0.45 nH between Q8's source and U3's PGND, the tightest figure |
| n1 the Q2 short's order | no order claimed while the charger still switches through ACOV's deglitch (Q7 at 28.7 V or more before ringing); the U3-first order only once ACOV has stopped it; in the `.out`, this README, the closing evidence and S-111's addition |
| n2 the first on-time | stated (7.3.1 p.14, 7.3.5 p.16): 45.76 A, 23.40 V; **the bound moves** to 23.40 V (the larger of the steady cycle's 23.20 V and this), and every figure at the bound with it |
| n3 the 26 V allowance | moved to Q7's turn-on edge: 1.52 / 1.76 / 2.38 nH; the turn-off edge carries the negative limit |
| n4 fixed text | the strap's percentages come from the parsed values; U3's pin line and the strap line print their conclusion only when the condition holds; the sense filter is a record line; this LOG's overstatement corrected |
| n5 the sense filter | out of the gate (the bound does not rest on it), printed as a record line |
| n6 labels | the dump column MODEL, the bound column INFERRED; "not reached at the INFERRED bound"; the 22 V standoff sentence qualified |
| n7 wording | Q7's VDS taken from CH_ACN to CH_SW1 (CH_ACN's peak less CH_SW1's lowest, which already holds Q8's body diode) |
| commit | section 10: the tip, or a merge that carries it |

The check `CHECK.md` (round 1): B1 (Q7 carries Q8's VSD), B2 (the INFERRED label and the trip's bench reading in the
registry), B3 (the item closes only on a measurement referred to both bus levels), m1 to m11: answered in the second issue
and carried here with the third issue's figures (the bound 23.40 V; Q7 5.60 V and Q8 6.60 V at it).

## Files

`vbus20_bound.py` and `.out` (the figures), `apply_registry_s120.py` (the registry draft), `dryrun.out` (its dry run),
`LOG.md` (the running log), this README.
