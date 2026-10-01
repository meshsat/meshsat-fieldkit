# L4-E6: fault handling of board A's front end (MESHSAT-1357, 1 October 2026)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and no generator, registry, rendered page
or record of L4-E4 or L4-E5 is edited. Implementable choice 4, FAULT HANDLING, of `../l4e/L4-ENERGY-ARCHITECTURE.md`
(findings B-1, B-2 and B-4 and their closures). Every figure is printed, with its basis, by `l4e6_fault_handling.py`
(`l4e6_fault_handling.out`, "out N" below).

Section 0 of the script re-runs `../l4e4/l4e4_limits.py`, `../l4e5/l4e5_source_control.py` and `../r11dep/r11_dep.py` in
child processes and reproduces their outputs byte for byte. It then runs `l4e4_limits.compute()` and `r11_dep.main()`
in-process, checks that both print their records, and takes from them L4-E4's `band()`, the two R11 outcomes, r11_dep.py's
stage relations, `peak_b()`, `fet_tj()`, Figure 8's readings and the VBUS20 bank's per-can scaling. r11_dep.py's FET loss
relations are restated once and reprint its nine section 4 FET lines byte for byte. L4-E5's figures (the pin path's 5.095 A,
V-A07's 0.071 A, H3's 9 V and 12 V maxima) are read from its reproduced output. Labels: MAKER, NETLIST, MODELED, INFERRED,
ASSUMPTION, SESSION (a choice this record makes), INCONCLUSIVE.

**Status.** No approved requirement changes and no owner decision is needed. B-1 and B-2 close at both R11 outcomes, B-1
at 25 C only. B-4 does not close on the drawn bank at either outcome: the bank is to be re-sized by the generator owner.

## The decision

**Bound L1 and the FETs with U2's own cycle-by-cycle limit, rate the VBUS20 bank, and leave hiccup off** (SESSION,
engineering).

- **R12, U2's cycle-by-cycle sense resistor, from 5 to 12 mOhm.** The part is Milliohm HoJLR2512-3W-12mR-1%, LCSC C2904242
  (stock 3,407 in L4-E4's catalogue reading). Its sheet is the held HoJLR2512 series sheet (±1 %, 50 ppm/K, 3 W).
  - Boost peak limit 8.06 / 10.00 / 11.99 A, buck valley limit 5.27 / 6.67 / 8.10 A (out 5).
  - MAKER SNVSAI1D rev. D, p.7, HTSSOP rows: VCS(BOOST) 100 / 120 / 140 mV and VCS(BUCK) 66 / 80 / 94 mV.
  - INFERRED: R12 is stacked at ±1 % and 50 ppm/K over r11_dep.py's 75 K envelope. The CSG offset, 1.9 mV, is p.7's
    IOFFSET(CS/CSG) 19 uA (MAX column) over one 100 Ohm filter resistor; it is added against each end of the limits.
- **C147 from 680 to 330 pF C0G** (lcsc_fill.py's C1664). SNVSAI1D Equation 26 (p.24) gives 333 pF at 12 mOhm, where it gave
  800 pF at 5 mOhm, so this is the generator's same at-or-below choice.
- **MODE stays at VCC** (R119 as drawn, no hiccup).
- **The VBUS20 bank is rated, not bounded.** The generator's dense node analysis is to be re-run with a re-sized bank at the
  chosen current (OWED).

**Why.**
- **Hiccup does not act on the highest permitted current.**
  - SNVSAI1D p.17 (7.3.5): hiccup shuts U2 down after 128 *consecutive cycle-by-cycle* limits. It releases SS after 4000
    clock cycles.
  - pp.16 and 17 (7.3.4, 7.3.6): the average limit acts by discharging SS through its gm amplifier.
  - So the current R11 permits, which is the average limit, never counts toward hiccup (INFERRED from the two).
- **The drawn R12 bounds nothing that matters here.** Its peak limit, 19.35 / 24.00 / 28.77 A (stacked), lies above L1's
  17.5 A typical Isat.
  - At 9 V, the average limit's own peak is 19.95 A at 8 mOhm and 22.54 A at 7 mOhm. Both lie between that limit's minimum
    and maximum, so hiccup is not guaranteed to engage (out 3).
  - p.24 (8.2.2.7) sizes the CS resistor from the application's own currents.
  - Under L4-E5's line (H3), the in-service boost peak is at most 6.50 A at 9 and 12 V, L at -20 % (7.28 A by r11_dep.py's
    note 5). That leaves room to bring the limit down under L1.
- **12 mOhm is the smallest catalogue value that closes B-1 and B-2 at both outcomes** (out 5's scan, 5 to 20 mOhm).
  - It gives the most service margin of the passing values.
  - 10 mOhm lets 13.80 A through L1 continuously at 9 V, which puts Q2 past 150 C.
  - 15 mOhm's peak limit minimum, 6.45 A, is under the 6.50 A service peak.
- **Hiccup stays off.** The closures below take no hiccup credit, so hiccup would add nothing to them, and it would cost
  service:
  - At 9 V the vehicle entry's 6.15 A, all through L1, peaks at 7.98 A. That is 0.08 A under the new peak limit's minimum.
  - With hiccup on, an entry at its limit could trip a 0.58 to 1.02 s soft-start restart with FE_PGOOD down, against V-A08.
  - Without hiccup, the limit only clips the current (SNVSAI1D p.13: "the controller remains in a cycle-by-cycle current
    limit condition until the overload is removed").
- **The bank cannot be protected by a bound.** Above 14.0 V (8 mOhm) or 15.7 V (7 mOhm) the average limit, not the peak
  limit, sets the fault current. In buck mode no valley limit that is compatible with service holds the current lower.

**The candidates not chosen** (out 3 and 4; L1's peak against 90 % of the 17.5 A typical Isat, 15.75 A; the FETs on the
maker's 50 C/W):

| Candidate | 8 mOhm, 7.262 A | 7 mOhm, 8.300 A | Why not |
|---|---|---|---|
| (a) hiccup alone: R119 to AGND at 93.1 kOhm, which gives MODE 1.567 to 2.163 V, inside p.3's 1.38 to 2.22 V | 9 V: hiccup not guaranteed; L1 peak 20.74 A (118.5 % of Isat); Q2 needs RthetaJA ≤ 23 C/W, Q4 ≤ 31 C/W | 9 V: not guaranteed; L1 23.32 A (133.3 %); Q2 ≤ 18 C/W, Q4 ≤ 25, Q5 ≤ 41 | The average limit sets the 9 V fault, and hiccup counts only cycle-by-cycle limits. Where hiccup does engage, it lowers the average only: each burst's peak is still the peak limit's, above Isat. Timing: it trips after 0.57 to 0.73 ms, stays off 17.8 to 22.9 ms, then soft-starts for 0.58 to 1.02 s |
| (b) rate L1 (XAL1510-103ME, Isat 26.3 A typical, Coilcraft Document 947-1 p.1), the FETs and the bank | L1 78.8 % of its Isat at 25 C; FETs need ≤ 23 C/W | L1 88.7 %; FETs need ≤ 18 C/W | No held 100 V FET has a lower RDS(on): CSD18510Q5B is 40 V (SLPS632 p.1), under VIN_RAW's 64.5 V clamp (L4-E5). L1 needs its 15.2 x 16.2 mm outline (Document 947-1 p.3) in place of the XAL1010's 10.0 x 11.3 mm (Document 804-1 p.4). The thermal figure the FETs need has no document or measurement behind it |
| **(c) chosen: R12 12 mOhm, C147 330 pF, no hiccup, the bank rated** | below | below | |

## The closures at both R11 outcomes (out 5 and 6)

Every case is taken as continuous, with no hiccup credit. L1 and VBUS20 are taken at r11_dep.py's 20.887 V and the
declared 0.93. The FETs use RDS(on) max times Figure 8 at TJ, with the maker's RthetaJA of 50 C/W on its 1 in2 2 oz pad
used for board A as an ASSUMPTION; board A's own figure is not known (C-3).

| Finding | R11 8 mOhm, highest permitted current 7.262 A | R11 7 mOhm, 8.300 A |
|---|---|---|
| **B-1**, L1's peak at most 90 % of Isat at its temperature | Peak bound over 9 to 36 V: 12.60 A (at 15.4 V), 72.0 % of 17.5 A. **MET at 25 C.** At temperature **INCONCLUSIVE**: it holds if Coilcraft's Isat at the qualifying 85 C is at least 14.00 A, 80.0 % of its 25 C value (L1 at most 84.99 C over 9 to 36 V, at 13.957 V) | 12.77 A (at 36 V), 73.0 %. **MET at 25 C.** At temperature INCONCLUSIVE: needs at least 14.19 A, 81.1 %, at the qualifying 86 C (L1 at most 85.74 C, at 15.680 V) |
| **B-2**, TJ at most 150 C at 9, 15.1 and 36 V in 62.1 C air | 9 V (peak limit): Q2 130, Q4 127, Q5 85 C. 15.1 V (average limit): Q2 120, Q4 103, Q5 100 C. 36 V (average limit): Q2 117, Q3 71, Q5 85 C. **MET on the ASSUMED 50 C/W** | 9 V: as at 8 mOhm. 15.1 V (peak limit): Q2 138, Q4 107, Q5 109 C. 36 V: Q2 124, Q3 74, Q5 93 C. **MET on the ASSUMED 50 C/W** |
| **B-4**, every bulk can at most 2.8 A over the ESR bands | 2.69 A matched, 2.70 A at 1.5:1, **3.11 A at 2:1: NOT MET**. The worst can per ampere must reach at most 0.901 of today's at 2:1 | 3.07 / 3.09 / **3.55 A: NOT MET** at every spread. It must reach 0.912 / 0.907 / 0.788 of today's |

- **What sets the current.** At 9 V the peak limit holds L1 to 11.40 A average (11.45 A rms) and the output to 4.57 A at
  both outcomes. Above 14.0 V (8 mOhm) or 15.7 V (7 mOhm) the average limit sets it.
- **B-1's bound.** It is the lower of r11_dep.py's note-5 peak at the average limit and the peak limit's maximum plus the
  CS filter's lag.
  - The lag is INFERRED at 222 ns: R150 + R151 at +1 %, and C123 at +10 %, an ASSUMPTION because the netlist prints "1n"
    only.
  - The comparator's own delay is not printed. The headroom to 15.75 A admits 0.84 us (8 mOhm) or 0.80 us (7 mOhm) at the
    top of boost.
- **L1's temperature** is r11_dep.py's method: the maker's 40 K at 15.5 A, scaled by the square. Its maximum is taken over
  9 to 36 V at 1 mV, not at the three B-2 voltages only (check 1, M1). The qualifying temperature rounds that maximum up to the
  degree: 85 C at 8 mOhm and 86 C at 7 mOhm.
- **R12's own load.** 0.90 W at 9 V and 0.28 to 0.37 W at 36 V, at most 92 C (the derating line's 33.3 K/W, as r11_dep.py).
  The CS pins see at most 0.155 V against p.5's 0.3 V absolute maximum.
- **B-4's method.** It is the generator's own VBUS20 node analysis as r11_dep.py carries it.
  - The figures are gen_sch_a.py's third fix-up figures at 5.7 and 5.0 A, with the worst can scaled in proportion to the
    front end's current (`can_k` from r11_dep.py's run).
  - The dense script itself (drafts/scripts/ripple_dense.py) is not in this tree, so the method is blind to VIN_RAW. It is
    applied at the current the fault can hold continuously.
  - For reference, at 9 V, where the peak limit holds the output to 4.57 A, the scaling reads 1.69 / 1.70 / 1.95 A.

## What stays INCONCLUSIVE

- **L1's Isat at its temperature (C-5).** The held XAL1010 sheet (Document 804-1, revised 02/25/26) prints Isat at 25 C only
  (note 5) and refers temperature derating to a link. Its "Typical L vs Current" (p.3) is one curve. B-1 needs Isat of at
  least 14.00 A at 85 C (8 mOhm; 80.0 % of the 25 C figure) or 14.19 A at 86 C (7 mOhm; 81.1 %).
- **The CS comparator's propagation delay.** It is not printed, and the headroom admits up to 0.80 us. The leading-edge
  behaviour is not printed either.
- **The limits with slope compensation in.** p.7 prints VCS(BOOST) and VCS(BUCK) at VSLOPE = 0 V. Taking them that way is
  conservative for B-1 (a slope can only end the cycle earlier). It is not conservative for the 1.56 A boost service margin,
  which the bench records.
- **The loop at 12 mOhm.**
  - The current loop's gain per ampere falls to 0.417 of the drawn value. gen_sch_a.py's crossover, 0.71 to 3.6 kHz, then
    moves toward 0.30 to 1.5 kHz to first order (INFERRED).
  - The compensation is re-verified by the generator's loop check (OWED).
- **Board A's thermal resistance for Q2 to Q5 (C-3).**
  - The closures use the maker's 50 C/W as an ASSUMPTION. The hottest case is Q2 at 138 C (7 mOhm, 15.1 V), 12 K under the
    limit.
  - The buck-boost transition region (about 19 to 23 V) is not evaluated, because the closure names three voltages.
- **The re-sized bank (B-4).** It waits on the dense node analysis, which is not in this tree. 8 mOhm needs a cut of 9.9 %
  at 2:1 only. 7 mOhm needs 8.8 %, 9.3 % and 21.2 % at the three spreads.
- **Candidate (a)'s drawn R12 band.** The LR2512D's own TCR is not held, so the HoJLR2512 series' 50 ppm/K is used (an
  ASSUMPTION; the conclusion holds unstacked too).

## The bench rows

- **7b.5, B-1.** R12 12 mOhm fitted, U3 held in HIZ by Q6 and an electronic load on VBUS20 in its place. A stiff supply on
  VIN_RAW at 9.0, 12 and 15.1 V, at 25 C and in 62 C air. The load is stepped past the average limit.
  - Recorded: L1's current by a current probe, the CS differential at U2 pins 16 and 15, and SW2.
  - Pass: L1's peak at most 12.6 A (12.8 A on the 7 mOhm build); the peak limit's onset at or above 8.06 A; no
    cycle-by-cycle limit at H3's in-service 9 and 12 V demand.
  - At 26.5 to 27.24 V with 5.1 A out, no valley-limit skip.
- **C-5, B-1 at temperature.** Either Coilcraft's temperature derating for the XAL1010 is filed and read at the qualifying
  temperature, or L1 is measured with an L-versus-current sweep (check 1, M2):
  - **The part.** An XAL1010-103ME from the build's lot, held at the qualifying temperature or above (85 C for the 8 mOhm
    build, 86 C for 7 mOhm) in a chamber, its temperature read at the part. The DC bias is pulsed or held short enough
    that the part stays at that temperature at every point.
  - **The reference.** L0, the zero-bias inductance at the qualifying temperature, measured at the maker's own condition
    (Document 804-1 note 2: 1 MHz, 0.1 Vrms, 0 Adc).
  - **The sweep.** DC bias from zero through at least 14.2 A, in steps of at most 0.5 A, with L read at each step.
  - **The definition.** Isat at temperature is the current where L has fallen by 30 % from L0, the maker's definition
    (note 5).
  - **Pass.** L at or above 0.70 x L0 at every step up to 14.00 A (8 mOhm build) or 14.19 A (7 mOhm build). Isat at
    temperature is then at least that current, and B-1's peak bound of 12.60 A (12.77 A) is at most 90 % of it.
  - A single reading at one current does not establish Isat and does not close C-5.
- **7b.4, B-2.** In 62.1 C air, with the load held past the limit to thermal steady state at 9 V (peak limit), 15.1 V and
  36 V (average limit at the build's R11):
  - Q2 to Q5 case temperatures by thermocouple, and TJ inferred from them by the maker's RthetaJC.
  - Pass: TJ at most 150 C; the figure replaces the ASSUMED 50 C/W (C-3).
- **7b.8, B-4.** Each can's ripple current (a sense loop on its lead) at the build's highest permitted current at 15.1 and
  36 V, U3 drawing as the load. Pass: each can at most 2.8 A, on the re-sized bank.
- **The loop.** Bode measurements at 9, 15.1 and 36 V with R12 12 mOhm, against the generator's phase and gain margin
  targets.
- **V-A08 (L4-E5) with R12 fitted.** No FE_PGOOD drop (unchanged), and a cycle-by-cycle limit at the vehicle entry's limit
  only clips.

## The check, and what changed

The collaborator's check `checks/astra-check-l4e6-1.md` ACCEPTS L4-E6 as a provisional engineering decision. It names no
blocking item and no owner decision. Its two minors are fixed here; no figure other than L1's temperature moves.

| Item | What changed |
|---|---|
| M1, L1's maximum temperature was taken at the three B-2 voltages only, while B-1's envelope covers 9 to 36 V | The script now takes L1's temperature over 9 to 36 V at 1 mV (`VIN_FINE`). The maximum is 84.99 C at 13.957 V (8 mOhm) and 85.74 C at 15.680 V (7 mOhm), against the first round's 83.92 and 85.46 C, which agrees with the collaborator's sweep. The qualifying temperatures are 85 and 86 C, rounded up, and the Isat each needs is 14.00 and 14.19 A. The peak bounds re-taken at 1 mV are the same to 0.01 A (12.60 and 12.77 A). Test `t_l1_temperature_over_the_full_vin_grid` |
| M2, C-5 offered one inductance reading at 12.6 A, which cannot establish Isat of at least 14.2 A | C-5 is now an L-versus-current sweep at the qualifying temperature, from zero bias (L0 at the maker's note 2 condition) through at least 14.2 A. It keeps the maker's 30 % drop definition (note 5) and B-1's 90 % margin, and it states that one reading does not close C-5. The script prints the sweep's figures for each outcome. Test `t_c5_is_a_sweep_that_can_demonstrate_the_isat` |

## The consequence for L4-E4

**This decision supports L4-E4's R11 of 8 mOhm (C2904240), with IIN_HOST at 4.70 A and L4-E5's line (H3). It does not
require 7 mOhm.**

- **B-1 and B-2.** They close at both outcomes with the same R12, because the peak limit does not depend on R11.
- **B-4.** It does not close on the drawn bank at either outcome. Its gap is 0.31 A, at 2:1 only, at 8 mOhm, against 0.75 A
  at every spread at 7 mOhm. So 8 mOhm needs the smaller bank change.
- **What V-A07 must show for 8 mOhm to stand.** The pin's error at 10 mOhm is at most 0.071 A between 26.50 and 27.24 V.
  That is L4-E5's figure, read from its reproduced output and unchanged here, because R12 is not in the ISNS path.
- **If V-A07 fails.** 7 mOhm (C2904239, 8.300 A) stands with the same R12 and C147, and with the larger bank re-size.
- **The order.** R12 goes in with L4-E5's line, never before it. With IIN_HOST fixed at 4.70 A and no line (4.964 A
  through R11), the in-service current would meet the new peak limit below 16.3 V.

## For board A's generator owner (OWED, nothing applied)

- **`apply_gen_sch_a_r12.py`.** It adds `rcs="12m"` and `cslope=("330p", "C1664")` to the front end's `lm5176()` call and
  leaves MODE as drawn.
- **`apply_lcsc_fill_r12.py`.** It adds the C2904242 line for "12mOhm 1% 2512".
- **How they run.** Both default to `--check`, write only with `--write`, and refuse a second application. They were run
  only on scratch copies. The gen_sch_a.py draft composes with L4-E4's `apply_gen_sch_a_r11.py` in either order.
- **The same circuit round owes:**
  - L4-E5's ILIM_HIZ network;
  - L4-E4's R11 8 mOhm;
  - the loop re-verified at 12 mOhm;
  - the VBUS20 bank re-sized by the dense node analysis at 7.262 A (8.300 A if V-A07 fails);
  - B-3's re-declarations at these currents;
  - the gates and evidence re-taken.

After regeneration r11_dep.py and the L4-E4 to L4-E6 records refuse by design, because they describe the circuit before the
change.
