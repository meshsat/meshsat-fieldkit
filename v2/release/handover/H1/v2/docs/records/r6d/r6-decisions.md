# Board D, round 6 (MESHSAT-1357, 26 September 2026): R4T-F9 and the RF-002 keying path, after two re-reviews

Base: main faf8c981 (board D's round-4 corrections merged). Only `v2/ecad/tools/gen_sch_d.py` and `drafts/` change.
Generator sha256 39c5713b (the second fix-up; its code lines are identical to 08a7c08f, only comments changed).
Nothing is committed or pushed. Prototype framing: nothing here is built or measured. Every level below is arithmetic
on held datasheet figures, and the bench rows at the end are owed.

## 0. The first re-review's items and what happened to each

| Item | Resolution |
|---|---|
| B1: R4T-F9 rested on TI sheets for U12 to U14 while the certified parts were MDD 74LVC1G04GV (no sheet) and TECH PUBLIC 74LVC1G08GV | Every logic part on the PTT and EMCON chain is now pinned in the generator to a part whose maker's sheet is held: U9, U10, U12, U14 to TECH PUBLIC C19829591 (sheet sha 37d1f4d4, cited page by page), U11 to TI SN74LVC1G04DBVR C7827 (SCES214AF), U13 to TI SN74LVC1G06DBVR C840103 (SCES295AB). R6D-6. |
| B2: the fault band held only with +3V3_D8 at 0 V, and the rail is back-fed when U1 is open | U13 is now an open-drain inverter (R6D-5), so SA_PTT_n's level no longer depends on +3V3_D8 whenever U13's output is off. That holds at 0 V (U13 in Ioff) and, with EMCON asserted, anywhere in the gates' 1.65 to 5.5 V operating range (TECH PUBLIC page 2, SCES295AB 5.3), which contains the back-fed rail's whole range: at most 5.23 V, the SA868's own supply, since its AUDIO_ON is the highest back-feed source. The band from 0 to 1.65 V is carried as an open item, with a bench row. The divider is stiffened tenfold (1.2k over 2.0k). Corrected in the second fix-up (section 0b). |
| B3: false provenance ("the code board C's U9 already carries") and "board A's interlock" | Both removed. The 74LVC1G34 is now proven on its own evidence: DS36108 held (sha efd2d797), plus JLC's readback of C526347 as Diodes 74LVC1G34W5-7. Why its 10 ns/V input condition is met is stated. TR_APRS is described only as what reaches it: A's R116 pull-down, and C's U3 pin 35. |
| m1: the tx_inhibit reading was stale | Re-run with the r4t copy at sha 0795c5de, in section 3. |
| m2: the first-run refusal was not kept | Reproduced on this round's generator with only the first run's drawing order restored. The output is kept: drafts/box/run/repro/gen_sch.log. |
| m5: a board C firmware pin fighting U18 through 100 Ohm could draw up to 33 mA | R48 is now 220 Ohm (C22962), which limits that current to 15.4 mA, inside U18's 24 mA. |
| m6: stock note and C's use of C526347 | Corrected. Board C no longer uses C526347. JLC-CERTIFIED row 303 and lcsc_fill.py:143 are stale, and are left for the integrator. |
| m8: the bench row should also cover EMCON released with PTT idle, and record VGG and K1 | Added to section 5. |
| m3, m4, m7, m9 | No change needed. m7's open items are carried in section 4. |

## 0b. The second re-review's items (text only; the netlist does not change)

| Item | Resolution |
|---|---|
| B2's written proof cited 1.65 to 3.6 V as the gates' operating range and bounded the back-fed rail at "about 3.3 V" with no basis | Corrected in the generator and below (R6D-T2, R6D-5). The range the sheets give is 1.65 to 5.5 V (TECH PUBLIC page 2; SCES295AB 5.3; SCES214AF 5.3 and DS36108 give the same). The rail's bound now has a stated basis: a logic output does not rise above the supply of the part that drives it. RTS is on the CP2102N's VDD, 3.1 to 3.6 V (Silabs CP2102N Table 3.6; Table 5.1 gives the QFN28 no VIO pin, and Table 3.1 note 3 then makes VIO = VDD). AUDIO_ON is on the SA868's only supply, +5V_SA, at most 5.23 V. So the rail is at most 5.23 V, inside 5.5 V. The sheets tabulate VIL in four rows and leave three gaps (1.95 to 2.3, 2.7 to 3.0 and 3.6 to 4.5 V; the review named the last one). With EMCON asserted, TX_INHIBIT_n is at ground through the EMCON contact, and KEY is at U12's VOL of 0.1 V or less (the 100 uA row, VCC 1.65 to 5.5 V). Both are under a fifth of the lowest VIL any row gives (0.35 x 1.65 V = 0.58 V), so the conclusion holds in the gaps too. "NOT PROVEN: above 0 and below 1.65 V" is kept as it was. |
| Found while correcting B2 (R6D-N2) | Raising the rail's bound from 3.3 to 5.23 V exposes the EMCON-released half of the old claim (ii), "or no PTT is asked for". Above 3.6 V, PTT_SW_n idles toward the CP2102N's VDD (3.1 to 3.6 V), not at the rail. The sheets give no VIH from 3.6 to 4.5 V, and from 4.5 V their 0.7 x VCC (3.15 V) is above the CP2102N's 3.1 V floor. So U10 is not shown to read an idle RTS as high there. That case is now a second NOT PROVEN line: EMCON released, so it is not a D-05 case. It is reachable only if the SA868's unstated AUDIO_ON high is above 3.6 V. It is covered by bench row 2 and not remedied in this round. |
| m-a: the tool change would read UNDECIDED for two reasons, and the band's leakage is a stand-in | Section 3 names both reasons. The generator and R6D-2 now call the +-10 uA a stand-in: it is Ioff, the VCC = 0 figure, used for the powered case. They also state that 100 uA would move the pin only 76 mV. |
| m-b: the U12 pin 2 observation | R6D-N1 in section 4 now records the route through U12's own slot (check_contracts.py:227 admits any part referenced U12 on TX_INHIBIT_n). It also records the assert case: during each open interval of a bouncing contact the line rises at about 74 us/V, so a held PTT can re-key KEY. That is a transient, not a steady-state bypass. |
| m-c: the integrator list | Added: SBVS351D (sha 4a86306d) and the JSCJ 2N7002 sheet (sha 7941fb42). Also added: JLC-CERTIFIED rows 297 and 298 (D's U11 and U13 as MDD C53185133, old values), row 296 (board C's retired 1G04) and row 303. The re-review reads CMP-002 and SUP-001 as failing on D until those rows are replaced; this author did not run them. |
| m-d: IEN is typical | R6D-3 and section 3 now say that the 0.11 V uses U15's typical 10 nA EN current, and that SBVS351D publishes no maximum. |
| m-e: the band's top corner | The generator and R6D-2 now state that 3.333 V is this design's own ceiling, not an SA868 limit. They also state that the band carries tolerance and TCR only, because no UNI-ROYAL sheet with a drift figure is held. |
| m-f: KEY hold with +3V3 down too | U19's input is then in IOFF: 50 uA, 0.51 V (f9_fail_safe.py now prints it: 0.508 V). U19 and U16 are then unpowered and read nothing. This is in the generator and in R6D-3. |
| m-g: conductor_census.py's docstring | Now names 0795c5de, the sha in tool_snapshot.sha256. |
| m-h, m-i, m-j | No change. The ERC warnings are cosmetic, and the netlist_board regex defect is carried in section 4. m-j is the reviewer's own verification. |

## 1. The two findings, traced

### R6D-T1: RF-002. Could X_KEY key the SA868 while EMCON is asserted? On main, yes, on the sheets. The tool's FAIL was real.

The path on main (committed netlist `pcb-d-aprs-d9/out/pcb-d-aprs.net`):

- EMCON asserted: `TX_INHIBIT_n` low -> U12 (74LVC1G08) holds `KEY` low -> U13 holds `SA_PTT_n` high (SA868 pin 5,
  "1" = receive) and U14 holds `PA_KEY` low.
- `KEY` also carried Q6 (2N7002, gate on +3V3_D8, source on KEY, drain on X_KEY) into U16 pin 7 (PCA9555 IO0_3). It
  also carried R48 (100 Ohm) to `TR_APRS`, which crosses A and B to board C's U3 pin 35 (RP2040 GPIO).
- `PA_KEY` carried Q7 into U16 pin 8 (IO0_4), which is the PA bias path (U15 EN, the relay drive).

With KEY low, Q6's channel is on. U16 pin 7, made an output by a firmware error and driven high, then fights U12's low
through it. Nothing held bounds that fight under the 0.8 V at which U13 and U14 are guaranteed to read low:

- U12, the fitted TECH PUBLIC 74LVC1G08GV (page 3), guarantees VOL only up to 24 mA: 0.55 V at 25 C, and 0.8 V over
  -40 to +125 C, which is the VIL itself.
- The PCA9555's P port sources about 43 mA at 0.7 V under VCC (SCPS131J Fig. 6-14, typical), limited only by its
  50 mA absolute maximum.
- Q6's RDS(on) is stated only at VGS 5 V and 10 V.
- The RP2040 sat behind 100 Ohm.

So the hardware gate was not proven.

### R6D-T2: R4T-F9. SA_PTT_n had no pull at all, and U1 failed open is not U1 at 0 V.

On main, `SA_PTT_n` has two nodes, U13.4 and U2.5. U13 runs on +3V3_D8 from U1, and the SA868 runs on +5V_SA. The
SA868 v1.3 sheet (sha 938ef5ef) gives pin 5 only as "Module Input", with "0" meaning TX and "1" meaning RX. It states no
pull, no input current and no levels.

The re-review was right that a failed U1 need not put its rail at 0 V. With U1's output open, +3V3_D8 is back-fed from
two sources:

- R5 (10k) from the CP2102N's RTS (U3 pin 24, on its own SAU_3V3), whenever RTS idles high;
- R66 (10k) from the SA868's AUDIO_ON output (pin 1, level not stated).

The rail's loads cannot bound the level it then sits at:

- LED1 through R1;
- LED6 through R51;
- LED2 and LED3 through R29 and R30, only while the codec drives REC and PLAY low;
- the gates' own supply currents.

The other nodes on +3V3_D8 are:

- the gates' supply pins;
- the level stages' gates;
- bypass capacitors;
- U7's G0 input (U7 runs on +5V_D8);
- the pull-ups R68, R70, R76 and R78. No source drives their far ends above the rail, because a level stage passes its
  far side only up to its gate voltage less a threshold.

The gates' inputs that other boards drive pass at most their IOFF of 10 uA each. The rail can therefore sit anywhere
from 0 V up to its highest back-feed source, and that source bounds it: a logic output does not rise above the supply of
the part that drives it.

| Source | Supply | Its top |
|---|---|---|
| RTS through R5 | the CP2102N's VDD; Table 5.1 gives the QFN28 no VIO pin, and Table 3.1 note 3 then makes VIO = VDD | 3.6 V (Silabs CP2102N Table 3.6) |
| AUDIO_ON through R66 | +5V_SA, the SA868's only supply (FB1 from +5V_D8) | 5.23 V (+5V_D8's v_work; FB1 drops nothing at rest) |

So the back-fed rail is at most 5.23 V. That is inside the 1.65 to 5.5 V operating range of every gate on it (TECH PUBLIC
74LVC1G08 page 2; SCES295AB 5.3; SCES214AF 5.3; DS36108, recommended operating conditions). A push-pull U13 drives
SA_PTT_n to that level, and no divider overrides an active output, so the first cut of round 6 was not a fix for this
state. Neither reading proves it, but the level could land between the SA868's unknown thresholds with EMCON asserted,
which would also make it a D-05 case.

The same failure, checked on the other gate nets: with only R52 and R53 (101k) and R74 to the dead rail, PA_KEY could
float to 1.24 V with U14 in IOFF. That is above U15's VEN(HI) of 1.0 V (SBVS351D 5.5), which would switch the PA gate
bias on.

## 2. Decisions

All taken by the session under the owner's standing rule of 26 September 2026. Authority for pcb_decisions.yaml: the
21 Sep 2026 19:21 ruling.

**R6D-1: only logic inputs and passive pulls on KEY and PA_KEY.** Three 74LVC1G34 buffers, Diodes 74LVC1G34W5-7:

- DS36108 Rev. 10-2 is held (sha efd2d797). SOT25 pinout: 1 NC, 2 A, 3 GND, 4 Y, 5 VCC. Inputs take up to 5.5 V,
  IOFF is +-10 uA, II is +-1 uA at 85 C and +-2 uA at 125 C, and IOH and IOL are 24 mA at 3 V.
- JLC's readback of C526347 (2026-09-26T12:01Z) is that part, SOT-25, with a stock of 1,944.
- Input transition limit: 10 ns/V at 3.3 V. It is met because the three buffers are driven only by the push-pull
  outputs of U12 and U14. The only slow edges on KEY and PA_KEY follow +3V3_D8 itself, as it ramps up (with a PTT held
  and EMCON released) and as it decays through R84 and R85. U18 runs on that same rail. U19 and U20, on +3V3, feed only
  U16 through 1k, so a slow edge can at most glitch an expander read.

How they are wired:

- U18, on +3V3_D8: KEY -> PTT_MIR -> R48 -> TR_APRS. TR_APRS reaches A's J_MEZZ1.7, J_AB1.14 and R116 (a 100k
  pull-down), and C's U3 pin 35.
- U19 and U20, on the harness +3V3: KEY and PA_KEY -> 1k (R86, R87) -> X_KEY and X_PA_KEY.
- Q6, Q7 and R72 to R75 are removed.

Rejected, with the reasons given in the first cut:

- a READER_TAPS series resistor;
- a NAND after KEY;
- 74LVC1G07 buffers with pull-ups on +3V3_D8.

**R6D-2 (amended by R6D-5): SA_PTT_n is held at "receive" from the exciter's own rail.**

- R88 1.2k from +5V_SA, and R89 2.0k to GND. UNI-ROYAL 0603WAF: C22765 and C22975, both BASIC, JLC 2026-09-26T12:01Z.
  Tolerance +-1 percent and +-100 ppm/C, taken as +-1.65 percent over 65 K.
- Why not a pull straight to +5V_SA: the sheet does not show that the module's pins take VBAT, and its H/L note forbids
  "VDD or high level of cmos output" on that pin.
- Band:

  | Case | Level |
  |---|---|
  | Top: 5.23 V x 0.6327 | 3.309 V |
  | Top, plus +-10 uA from U13's output x 0.76k (a stand-in, below) | 3.317 V |
  | Bottom: 4.35 V (both drop budgets spent) x 0.6172 | 2.685 V |
  | Bottom, with the same stand-in | 2.677 V |
  | Nominal | 3.18 V |

  - The leakage term is a stand-in. SCES295AB states no off-state output current with VCC applied. The +-10 uA is Ioff,
    its VCC = 0 figure, the only one held for this pin, and no sign is given. At 0.76k even 100 uA would move the pin
    only 76 mV.
  - The top stays 16 mV under 3.333 V, the level the pin has always been driven with. That ceiling is this design's own
    choice, not a limit the SA868 sheet states. The band carries tolerance and TCR only: no UNI-ROYAL sheet with an
    endurance drift figure is held.
- Costs:
  - transmit sink of at most 4.4 mA, where SCES295AB gives VOL 0.4 V at 16 mA and 3 V;
  - R88 dissipates 23 mW in transmit;
  - the divider draws 1.7 mA from +5V_SA;
  - counted the way tx_inhibit.py's census() counts a pull against a forced "1" (PULL_MA_MAX), R89 asks 1.7 mA,
    under its 4 mA. The tool's own walk no longer reaches this net (section 3), so this figure comes from
    conductor_census.py, which runs census() with U13 as the allowed driver.
- Why 1.2k over 2.0k, not 12k over 20k: the divider now sets the receive level in service, and the SA868 states no pin 5
  current. A 0.76k Thevenin moves 7.6 mV per 10 uA, where 7.5k moved 76 mV.

**R6D-3: KEY and PA_KEY hold low with their own gates at 0 V.**

- R84 10k on KEY. Worst-case leakage is 42 uA, made up of:
  - U12's output and U14's input, TECH PUBLIC IOFF;
  - U13's input, SCES295AB Ioff;
  - U18's input, DS36108 IOFF;
  - U19's input, powered, II 2 uA.

  That gives 0.43 V, under U19's VIL of 0.8 V.
- With the harness +3V3 down as well, U19's input is in IOFF (+-10 uA, DS36108) instead of II: 50 uA, 0.51 V (0.508 V in
  f9_fail_safe.txt), still under 0.8 V. U19 and U16 are then unpowered and read nothing.
- R85 10k on PA_KEY: 12.1 uA gives 0.11 V, under U15's VEN(LO) of 0.3 V. That total takes U15's EN current at its typical
  10 nA (SBVS351D 5.5 publishes no maximum). The margin, 0.19 V across 9.25k, is about 20 uA, so the conclusion does not
  rest on that figure. Without R85 the level would be 1.24 V.
- With the rail back-fed to 1.65 V or more, U12 and U14 drive KEY and PA_KEY by their logic. Under 1.65 V no sheet
  specifies them (see R6D-5).

**R6D-4 (drawing only).** R48 sits in the harness section, and R86 and R87 are written with the U16 side first.
schlayout's decap_row has no occupancy check. The refusal of the other order is reproduced and kept:

```
schlayout verify: SHORT ['+3V3_D8', 'TR_APRS']: pins [('R48', '2'), ('C66', '1')]
schlayout verify: SHORT ['+3V3', 'X_PA_KEY']: pins [('U16', '8'), ('R87', '2'), ('C68', '1')]
schlayout: the drawing does not carry the netlist it was given (2 defect(s) above)
```

That is drafts/box/run/repro/gen_sch.log, generator sha 2a9de884: this round's generator with only the drawing order
changed. The pin-to-net map is the same either way.

**R6D-5 (new): U13 is an open-drain inverter.** TI SN74LVC1G06DBVR, C840103 (JLC 2026-09-26T11:55Z, Texas Instruments,
SOT-23-5, stock 8,537). What SCES295AB, held, gives:

- Table 4-1: DBV 1 NC, 2 A, 3 GND, 4 Y, 5 VCC. This is the same land and pin map as the 74LVC1G04 it replaces.
- 6.3.1: the output sinks and never sources.
- Figure 6-2: the output has only a negative clamp diode.
- VO is 0 to 5.5 V at any VCC.
- Ioff is +-10 uA at VCC 0, and 6.3.4 gives a high-impedance output then.
- VIL is 0.8 V at 3 to 3.6 V.
- Table 6-1: an input L gives Hi-Z, and an input H gives L.

KEY high pulls SA_PTT_n low (transmit). KEY low releases it, and R88 and R89 alone set it (receive). While the output is
off, SA_PTT_n does not depend on +3V3_D8 at all. The output is off:

1. with +3V3_D8 at 0 V (U1's output shorted to ground, or nothing back-feeding), because U13 is in Ioff;
2. with +3V3_D8 anywhere in 1.65 to 5.5 V, whenever EMCON is asserted. That range is the operating range of U12 and U13
   (TECH PUBLIC page 2; SCES295AB 5.3), and it contains the back-fed rail's whole range, up to 5.23 V.
   - EMCON's contact holds TX_INHIBIT_n at ground.
   - U12 holds KEY at or under its VOL of 0.1 V. That is the 100 uA row, which TECH PUBLIC page 3 gives for VCC 1.65 to
     5.5 V. While KEY is low, U12 sinks only its readers' input leakage, since R84 and R49 lead to ground.
   - Both inputs are then under every VIL row the sheets tabulate, 0.3 x VCC at 4.5 to 5.5 V included.
   - The sheets tabulate no VIL between those rows: 1.95 to 2.3, 2.7 to 3.0 and 3.6 to 4.5 V. The EMCON-asserted inputs
     sit near 0 V there, under a fifth of the lowest VIL either sheet gives anywhere in 1.65 to 5.5 V
     (0.35 x 1.65 V = 0.58 V). So the conclusion holds there too;
3. with EMCON released and no PTT asked for, when U12 also drives KEY low. This is shown only with +3V3_D8 at 3.6 V or
   less.

- **NOT PROVEN:** +3V3_D8 above 0 and below 1.65 V, where no sheet specifies U9 to U14, and R84 holds KEY only against
  their leakage. This is a bench row (section 5).
- **NOT PROVEN EITHER (R6D-N2, found in the second fix-up):** EMCON released, no PTT asked for, and +3V3_D8 back-fed above
  3.6 V.
  - PTT_SW_n idles where the CP2102N's RTS holds it: toward that part's own VDD, 3.1 to 3.6 V (Silabs Table 3.6), not at
    the rail.
  - The sheets tabulate no VIH from 3.6 to 4.5 V. From 4.5 V their 0.7 x VCC (3.15 V at 4.5 V) is already above the
    CP2102N's 3.1 V floor.
  - So U10 is not shown to read an idle RTS as high there, and a software PTT could key the exciter.
  - EMCON is released, so this is not a D-05 case.
  - The rail reaches that band only if AUDIO_ON's high level, which the SA868 sheet does not state, is above 3.6 V.
  - Bench row 2 decides it. No circuit change is made for it in this round (section 4).
- **SA_PD** at a back-fed level (R76 to +3V3_D8), or pulled low through Q8's body diode when U16 drives X_SA_PD low,
  selects power-down or normal work. The pin table gives transmit to pin 5 at "0" only, so no level on pin 6 keys the
  module.
- **The back-feed paths are left as they are.**
  - Moving R5 to SAU_3V3, the re-review's example, removes one source. It also means that a dead CP2102N regulator,
    with +3V3_D8 up, pulls PTT_SW_n to ground and requests PTT (U10 -> U11 -> U12), which would key the transmitter
    whenever EMCON is released. That trade is not taken.
  - R66 is the level stage's own near-side pull-up.
  - Neither source can reach SA_PTT_n while U13's output is off.
- **Cost:** in service, the receive level is now the divider's, 2.68 to 3.32 V (3.18 V nominal). The push-pull U13
  gave 3.17 V or more. The SA868's "1" threshold is unknown in both designs, and one bench row now covers every state.
- **Rejected:**
  - keeping the push-pull U13, which is option (c) of the re-review. It leaves an EMCON-asserted state (U1 open, rail
    back-fed) in which the keying pin follows the rail anywhere from 0 to 5.23 V;
  - bounding the back-fed level, option (a). The only bound the held sheets give is the SA868's own supply, 5.23 V
    (R6D-T2), which a push-pull U13 would pass to pin 5 in full. The SA868 states no AUDIO_ON high level that would give
    a tighter one;
  - a series resistor after a push-pull U13. Any value large enough to let the divider win in receive also stops U13
    from pulling the pin to "0" in transmit.

**R6D-6 (new): the fitted gates are named.** U9, U10, U12 and U14 are pinned to C19829591, U11 to C7827 and U13 to
C840103. The TECH PUBLIC sheet (sha 37d1f4d4, image-only, read from the renders) gives:

| Page | Content |
|---|---|
| 1 | SOT-23-5: 1 A, 2 B, 3 GND, 4 Y, 5 VCC; "power down protection" |
| 2 | VCC 1.65 to 5.5 V; 10 ns/V at 3.3 V |
| 3, VCC 3.0 to 3.6 V | VIL 0.8 V, VIH 2 V |
| 3, VIL rows | 0.35 x VCC at 1.65 to 1.95 V, 0.7 V at 2.3 to 2.7 V, 0.8 V at 3.0 to 3.6 V, 0.3 x VCC at 4.5 to 5.5 V; none between |
| 3, VOL | 0.1 V at 100 uA (VCC 1.65 to 5.5 V); 0.55 V at 24 mA at 25 C, 0.8 V over temperature |
| 3, leakage | II +-5 uA; IOFF +-10 uA (VCC 0) |

**R6D-7 (new): R48 is 220 Ohm** (C22962, BASIC). A firmware pin that drives TR_APRS against U18 draws at most
3.333 V / 216 Ohm = 15.4 mA. That is inside U18's 24 mA at 3 V (DS36108). With 100 Ohm it could draw 34 mA.

## 3. What the tools read (evidence in drafts/box)

**tx_inhibit.py**, the r4t copy at sha 0795c5de (held, informational), was run on main's six committed netlists and then
with D swapped (rf002/tx_inhibit_main.txt, tx_inhibit_new.txt).

The TX_INHIBIT_n line reads PASS on both. The SA868 row:

| Netlists | Reading |
|---|---|
| main | FAIL [C,D]: U16 pin 7 through Q6, and C's U3 pin 35 through R48 |
| new | FAIL [D]: "EMCON does not reach it, it is driven by U13 (74LVC1G06 open-drain inverter)" |

Every other row is unchanged.

**Why the new FAIL is the tool's model, not the circuit:**

- The walk forces a net only through an element's output, and FORCE gives INV_OD an entry only for input 1. With KEY
  forced to 0, the walk stops at U13. It has no representation of an open-drain output that EMCON forces off onto a
  pull on the transmitter's own rail.
- The hardware gate is complete. The only element that can pull pin 5 to "0" is U13. EMCON forces U13's input low
  through U12, with nothing else left on KEY that can drive it, so U13's output is Hi-Z (Table 6-1). SA_PTT_n then
  carries only R88, R89 and U2.5. Its census reads FAIL 0 and UNDECIDED 0 (rf002/conductor_census_new.txt), and the pin
  sits at 2.68 to 3.32 V.
- Two things are left. One is the reason the push-pull design read UNDECIDED: the SA868 publishes no threshold for "1".
  The other is new with the open-drain part: SCES295AB gives no off-state output current with VCC applied, so the band's
  +-10 uA is a stand-in (R6D-2).
- Tool change owed (r4t): treat an open-drain output that EMCON forces off as forcing its net to the level of the
  passive pulls on it, when every such pull is fed from the anchor's own supply conductor, and judge that level against
  the anchor's pin model. For the SA868 that would likely read UNDECIDED, for two reasons:
  - the unpublished "1" threshold;
  - the unstated powered off-state current. tx_inhibit.py 0795c5de already treats "a powered open-drain output whose
    off-state current its sheet does not state" as unknown (line 943).

**Census per gate net** (rf002/conductor_census_*.txt):

| Net | main | new |
|---|---|---|
| KEY | FAIL 2 (U16 pin 7 through Q6; C U3 pin 35 through R48) | FAIL 0, UNDECIDED 0 |
| SA_PTT_n | 0 / 0 | 0 / 0 |
| PA_KEY | FAIL 1 (U16 pin 8 through Q7), UNDECIDED 1 | FAIL 0, UNDECIDED 1 (U15 EN: the tool does not know the TLV758P's EN as an enable) |

**f9_fail_safe.py** reads off the regenerated netlist (rf002/f9_fail_safe.txt):

| Net | Reading |
|---|---|
| SA_PTT_n | 2.677 to 3.317 V, 3.18 V nominal (leakage term a stand-in) |
| KEY, +3V3 up | at most 0.427 V |
| KEY, +3V3 down too | at most 0.508 V; nothing reads it then |
| PA_KEY | at most 0.112 V with U15's EN at its typical 10 nA; 1.24 V without R85 |

## 3b. Regeneration on the box

Run in /root/r6/d only (KiCad 9.0.9), rerun for the second fix-up at 2026-09-26T12:52Z to 12:53Z with generator
39c5713b. The logs are in drafts/box, replacing the first run's.

**Parity** (regen_compare.py in pair mode; see the parity/ folder):

| Comparison | Result |
|---|---|
| Base (main faf8c981, generator c4317b3f) against the committed files | Netlist PARITY_AFTER_NOISE, schematic PARITY, intent PARITY_AFTER_NOISE |
| New (generator 39c5713b) against new2 | PARITY or PARITY_AFTER_NOISE on all five kinds; netlist content hash c9ea1468d86c12e3 (committed and base: d550a3e3e5687237) |
| New (39c5713b) against the first fix-up's new (08a7c08f), prev_vs_new/ | Netlist PARITY_AFTER_NOISE (a raw diff shows only the export date), intent PARITY_AFTER_NOISE, BOM PARITY, ERC PARITY_AFTER_NOISE. The generator's code lines are identical; only comments changed |

**Gates, base -> new** (gates_r6d.json; every verdict and count is identical to the first fix-up's run on all three
variants):

| Gate | Base | New |
|---|---|---|
| ERC | clean, 386 warnings | clean, 413 warnings; the same three warning classes; 0 blocking |
| SCH-005 (pin_map_lands_d) | PASS 220 | PASS 226 |
| CMP-001 (derate) | PASS, 15 judged | PASS, 15 judged |
| TRN-001 (port_protect_d) | PASS | PASS |
| safe_lines | PASS 2 | PASS 2 |
| power_path, power_sequence, clock_check, ground_system | PASS | PASS |
| inhibit_chain_d | PASS 5/5 | PASS 5/5 |
| check_contracts_d | INCONCLUSIVE 6/11 | INCONCLUSIVE 6/11, unchanged (A and B are refused as UNKNOWN GENERATOR on main) |
| SCH-002 (netlist_board) | FAIL 32 | FAIL 52, layout lag only |
| netlist_parts | FAIL | FAIL, layout lag |

**Netlist diff**, committed D9 against the new one (drafts/box/netdiff_committed_vs_new.json; the committed copy is
byte-identical to main's tracked `pcb-d-aprs-d9/out/pcb-d-aprs.net`, and apart from its two file paths the diff is
identical to the first fix-up's): 221 -> 227 parts, 174 -> 180 nets.

- Removed: Q6, Q7, R72, R73, R74, R75 [RF-002, R6D-1].
- Added:
  - U18, C66, net PTT_MIR [RF-002, R6D-1];
  - U19, U20, C67, C68, R86, R87, nets X_KEY_B and X_PA_KEY_B [RF-002, R6D-1];
  - R84 and R85 [R4T-F9, R6D-3];
  - R88 1.2k and R89 2k [R4T-F9, R6D-2 and R6D-5];
  - unconnected-(U18/U19/U20-NC-Pad1), the buffers' NC pins [R6D-1].
- Pin moved: R48.1 KEY -> PTT_MIR [RF-002, R6D-1].
- Changed:
  - U13 value 74LVC1G04 -> 74LVC1G06 open-drain inverter, LCSC C840103 [R4T-F9 re-review B1 and B2, R6D-5];
  - U11 LCSC C7827 [re-review B1, R6D-6];
  - U9, U10, U12, U14 LCSC C19829591 [re-review B1, R6D-6];
  - R48 value 100 -> 220, LCSC C22962 [re-review m5, R6D-7].
- Node counts: +3V3_D8 36 -> 34, +3V3 12 -> 14, +5V_SA 4 -> 5, SA_PTT_n 2 -> 4, X_KEY 3 -> 2, X_PA_KEY 3 -> 2, GND 135
  -> 144. Each is accounted for by the parts above.

**Intent:**

- bypass gains C66 -> U18, C67 -> U19 and C68 -> U20;
- +3V3_D8 loses Q6 and Q7 and gains U18;
- +3V3 gains U19 and U20, and its note changes.

**Suite:** tests/run.py, one run at a time. suite_base.log is the base tree from the first fix-up's run; the base is
unchanged. suite_new.log is this run's new tree (generator 39c5713b). Each reads 1433 passed, 22 failed and 27 skipped,
with identical outcomes test by test for all 1482 tests. The 22 failures are files that the ecad-only archive does not
carry (OPERATING-ENVELOPE.md, TEST-PLAN.md, the v2/vendor transcriptions), and they fail on base too. The box scratch
/root/r6/d is deleted, and no process of this author's is left on the box.

## 4. Open items this author cannot close

**Layout (gen_pcb_d3.py):**

- EXP (Q3..Q9) and EXPB (R66..R79) still name Q6, Q7 and R72 to R75;
- seat U18, U19, U20, C66, C67, C68 and R84 to R89;
- R48 pin 1 moves to PTT_MIR, and R48 is now 220 Ohm;
- U13 keeps its SOT-23-5 land and pin map;
- SCH-002 is 52 of 997, and one of those is U15.5 (the netlist_board last-net defect, below).

**Tools (r4t):**

- tx_inhibit.py's model of an open-drain output released onto a pull fed from the anchor's own rail (section 3);
- the TLV758P EN as a known enable;
- netlist_board.py's regex drops the last net;
- schlayout decap_row needs an occupancy check (R6D-4).

**Integrator:**

- File these sheets under v2/vendor. Main holds none of them, and the generator's comments cite each one:
  - the TECH PUBLIC 74LVC1G08 sheet (sha 37d1f4d4);
  - TI SCES295AB (44dbca33) and SCES214AF (ac04a53d);
  - Diodes DS36108 (efd2d797);
  - TI SBVS351D, the TLV758P (4a86306d, from wt/r4d/drafts/datasheets), cited for U15's VEN(LO) and IEN in the R85 hold;
  - the JSCJ 2N7002 sheet, LCSC C8545 (7941fb42, from wt/r4t/drafts/datasheets), cited for Q2's IGSS and Q6's RDS(on).
- JLC-CERTIFIED rows (release/revA/order/JLC-CERTIFIED.tsv, line numbers with the header as line 1):
  - rows 297 and 298 still certify D's U11 and U13 as MDD C53185133 under their old values. Replace them with U11 ->
    C7827 and U13 -> C840103. The re-review reads CMP-002 and SUP-001 as failing on D until then; this author did not run
    them, because jlc_certify is the integrator's;
  - row 296 (board C's retired 74LVC1G04) is stale;
  - row 303 and lcsc_fill.py:143 still say C526347 is board C's EMCON buffer;
  - new rows: U18 to U20 on C526347; R48 on C22962, R84 and R85 on C25804, R86 and R87 on C21190, R88 on C22765, R89 on
    C22975.
- PCB-BRING-UP.md:145 still lists Q6 and Q7 as +3V3_D8 loads.
- Records R6D-1 to R6D-7 in pcb_decisions.yaml.

**New observations, not remedied in this round:**

R6D-N1, U12's input edge (pre-existing):

- U12 pin 2 (TX_INHIBIT_n) is a plain CMOS input with a 10 ns/V limit (TECH PUBLIC page 2).
- The line it reads is the one board C's generator measures at a 77 us time constant on release (R14 10k up, C24 10n,
  about 74 us/V). That measurement is why C's U9 became a Schmitt 74LVC1G17 in round 4.
- On release: U12 runs outside its input condition on every EMCON release, so KEY may chatter for tens of microseconds
  if a PTT is held.
- On assert: the switch closure is a fast edge, but the toggle's contact bounces. During each open interval the line
  rises at about 74 us/V, so with a PTT held KEY can re-key for the length of a bounce. That is a transient, not a
  steady-state bypass.
- Two routes for the next round:
  - a Schmitt-input gate fitted in U12's own slot. check_contracts.py:227 admits any part referenced U12 on
    TX_INHIBIT_n, so that passes the contract as written, subject to that part's sheet;
  - a Schmitt stage between J_HARN1.8 and U12, which would need that contract ("nothing but the harness, its pull-down,
    a test point and the KEY gate") widened.

R6D-N2, EMCON released with the rail back-fed above 3.6 V (found in the second fix-up; R6D-5, NOT PROVEN EITHER):

- With EMCON released and no PTT asked for, PTT_SW_n idles toward the CP2102N's VDD (3.1 to 3.6 V, Silabs Table 3.6), not
  at +3V3_D8. Above 3.6 V the sheets give no VIH until 4.5 V, and from there their 0.7 x VCC is above 3.1 V. So U10 is
  not shown to read an idle RTS as high, and a software PTT could key the exciter.
- EMCON asserted is unaffected (R6D-5 case 2), so this is not a D-05 case.
- The state needs U1 failed open and the SA868's AUDIO_ON high, whose level the sheet does not state, above 3.6 V. Bench
  row 2 measures it.
- For the next round: a remedy has to bound the back-fed rail at 3.6 V or less, for example with a clamp on +3V3_D8,
  with its own evidence. None is taken here. Configuring RTS open-drain does not settle it, because the CP2102N then
  pulls a high latch up to VIO through its on-chip resistor (Silabs 4.3.3), against R5. Moving R5 to SAU_3V3 was rejected
  in R6D-5 for its own failure mode.

**Stock:** C526347 had 1,944 at 12:01Z, and D uses 3 per board. C840103 had 8,537, and C7827 had 55,684.

## 5. Bench rows OWED to TEST-PLAN.md (not in it)

Each row runs with the SA868 on a dummy load and a carrier detector. Record +3V3_D8, KEY, PA_KEY, SA_PTT_n, SA_PD, VGG,
K1, and U16 IO0_3 and IO0_4.

1. U1 fitted, receive: SA_PTT_n 2.68 to 3.32 V, and no carrier.
2. U1 unfitted, +5V_D8 applied: four runs, with the codec playing and then idle, and with EMCON asserted and then
   released with PTT idle (the CP2102N enumerated and RTS idle high). Also record PTT_SW_n, SAU_3V3 and SA_AUDIO_ON_n.
   Pass: no carrier, VGG 0 V, K1 released, and U16 reads 0 on both bits. The +3V3_D8 reading is the number section 4's
   open bands need: under 1.65 V is the NOT PROVEN band, and above 3.6 V with EMCON released is R6D-N2.
3. U1's output shorted to ground: SA_PTT_n 2.68 V or more, KEY under 0.43 V, PA_KEY under 0.11 V, and no carrier.
4. EMCON asserted, U16 IO0_3 and IO0_4 set as outputs and driven high: KEY and PA_KEY under 0.1 V, and no carrier.
5. The SA868's "1" threshold on pin 5, and its input current. The design gives 2.68 V or more in every state, and the
   sheet publishes neither figure.
