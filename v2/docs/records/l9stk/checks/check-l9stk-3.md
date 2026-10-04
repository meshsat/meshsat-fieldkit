accepted: CONFIRMED AS CONDITIONAL

# Record l9stk: the independent checker's check 3, PROTECTION: CONFIRMED AS CONDITIONAL (filed as received)

MESHSAT-1357. An AI review by a fresh Claude session that authored none of the record (an independent checker, not a qualified engineering review, not an Astra check), read-only in a disposable scratch clone at `474e6bcea42cb591ff4b4bfd6ec54641d5910d6f` (branch `fnd/l9stk`). Time: 4 October 2026, 02:20 to 02:25 CEST. Nothing in the kit has been built, bought or measured.

Scope, from the coordinator's brief: the targeted recheck of section 15's revision (B-P1, the make-last dock enable into UVLO; B-P2, the battery FETs' junction limit and the third FET), `l9stk_protection.py` and its output, `l9stk_copper.out` section 8 (option 4) and findings L9C-F20 to F22.

Filed by the integrator of set 29 from the checker's final message for the round, without edits to its content. The record's author answered it in the next round (`L9-STACKUPS.md` sections 14 and 15 name each revision); this note is the checker's own record of what it read and found.

## The checker's report, as received

**PROTECTION: CONFIRMED AS CONDITIONAL**

At 474e6bce both former blockers are corrected and every figure reproduces at its source. Five things in section 15 need correcting as text, and three conditions have to be bounded by their owners.

In a scratch clone at 474e6bce, with SLVA673A fetched (sha matched), `test_l9stk` and `test_energy_chain` gave 66 passed, 0 failed, 0 skipped. The three drafts ran with `--check` only: the decisions draft checks clean, the energy chain draft refuses until the decisions are in the register, and the plating draft passes. The tree is unchanged and the clone is deleted.

**Blockers:** none.

**Corrections required (the record is wrong, but no decision flips)**

1. **The docking timing misreads the LM5069 sheet.** The insertion time runs only when VIN rises past PORIT. The sheet says the gate is held low during it "regardless of the voltage at VIN or UVLO", and on releasing UVLO "the LM5069 switches on the load current". The delay to gate-high is UVLODEL, 55 us typical, with no maximum printed.
   - So a docking starts about 55 us after the enable mates, not 4.23 to 15.25 ms later.
   - The 4.23 to 15.25 ms figure is right only for a start caused by the gauge's own FET turning on.
   - With the correct mating order this changes nothing. It does remove the grace interval the page implies (see condition 1).
2. **Q41 is already taken on board A.** Record l8r2's VIN_RAW cut-off FET (CSD19532Q5B, `check_l8r2_netlist.py`, L8R2-KNOWN-DEFECTS row Q41) uses it, so the composed board A would carry two Q41s. Name the third battery FET by a free designator, or leave the designator to L4-E11.
3. **The 10 A and 18 A rows under BAT-F20.** At the table's own 76.25 °C air, above T3, CHGIN = 1 holds Q1 off. Q1's body diode then carries the discharge: about 7 to 10 W at 10 A and up to 18 W at 18 A (VSD 1 V maximum at 50 A).
   - Those rows' limiting part is therefore Q1, over its limit, not "the XT60 at 0.33" or "Q39 to Q41 at 32 K".
   - DD-5 belongs on those rows, not only on the overload row.
4. **D1's basis contradicts the record.** It is sized against "the 50.59 A the lead can carry at turn-off", while the record itself says a hot short passes 116.8 A before the gate is low. It still passes on I²t (about 240 A for about 14 us is about 0.4 A²s, against the 41.5 A²s of its 100 A 8.3 ms rating). Restate it that way.
5. **The not-taken reason for the PTC thermal trip is stale.** It is argued against the pair's 133.0 °C service. With the selected three FETs the service is 118.0 °C, so a trip at 127 to 133 °C would sit 9 to 15 K above the service and under 150 °C. That is a guard against the 45.88 K/W path never being met, and should be reconsidered as one.

**Conditions (each needs an owner)**

1. **Mating order (Layer 7).** C-1b protects only if every power pin mates before the enable at any angle the dock's guides allow. The page states only the 1 mm length difference.
   - Since UVLO gives no delay, a reversed order of more than about 1.9 ms lets OUT ramp past 2.09 V (at most 1.111 V/ms). The surge at mate then exceeds the breaker's least 30.21 A threshold (2.09 V / 69 mΩ). A reversal longer than the 15 to 40 ms ramp reproduces the uncorrected docking.
   - An RC hold on the enable (board P's generator) would restore a grace interval.
2. **A short to ground on the enable line** (J_SMB's fifth contact, board E, the dock) is a latent single fault. It silently brings back DD-6 at every docking. The page covers an open line (fail-safe) but not a short; detection or tolerance has to be stated.
3. **The third FET exceeds TI's selection guidance.** Three BUK6Y10-30P put 7.08 nF typical (about 8.61 nF near 0 V) on CH_BATDRV, against TI's 5 nF. E11-37's bench tests samples only; production-wide conformance needs TI's answer to Q-TI-17. The pair at 20.39 K/W remains the fallback.

**Minors**

- The 2N7002 that holds UVLO low needs its gate drive bounded under VIN's 29.2 V clamp (its VGS limit is ±20 V), and a series resistor from VIN to UVLO.
- The clamp-short row covers only a hard short. A resistive failure of the SMCJ18A in the 33.75 to 150 A range, with board P's FETs welded, leaves board P's loop on F1's 600 s and 5 s rows, which the breaker cannot cover.

**Points (a) to (e)**

- **(a) C-1b: CONFIRMED AS CONDITIONAL.**
  - Reproduced: insertion 4.23 to 15.25 ms (right for a VIN-rise start only), withdrawal 1 mm / 395 us = 2.53 m/s, inrush 0.659 A, sense 1.72 mV, start SOA 0.58.
  - Covered: a first mate with board P's FETs welded (UVLO does not depend on Q1/Q2), and bounce (benign at this slew).
  - Not covered: a tilted mate (condition 1) and an enable shorted to ground (condition 2). The timing needs correction 1.
- **(b) B-P2 and the third FET: CONFIRMED AS CONDITIONAL.**
  - Reproduced: the 64.59 K budget; 1.345 W each; 48.01, 45.88 and 15.34 K/W; the pair at 21.34, 20.39 and 10.96 K/W; the service at 118.0 °C and 89.4 °C.
  - The bound on R17's coupling holds: in a passive network the coupling is at most the FET's own self-impedance.
  - The drive (shared CH_BATDRV) matches L4-E11's draft. The designator does not (correction 2), and the gate charge is condition 3.
- **(c) DD-5: CONFIRMED.** It is a design defect in normal service, owned by the battery stream (BAT-F20, EQ-15). It does not change whether the breaker is adequate: no current limit can protect a part already over its limit inside the service current. It must also go on the 10 A and 18 A rows (correction 3).
- **(d) The table: CONFIRMED AS CONDITIONAL.** Trips, clearing times and margins reproduce: 23.93 A, 1.29 ms, 0.57 and 0.58, the docking without the enable at 2.64× and 1.66× with 2.11× of 0.3 V, reverse charging at 126.2 °C. Corrections 1, 3 and 4 apply, and the supported envelope should name conditions 1 and 2.
- **(e) Earlier minors:** answered correctly except D1's basis (correction 4) and the clamp short (resistive case). Answered correctly:
  - E-4 now gives 0.593 and 0.553, each at its current;
  - E-5's 0.28 % split and its fallback spread of 1.270 against the LM5069's 1.307;
  - E-9, E-10 (1.03 %) and E-11;
  - the limits printed at 48 V;
  - the charge direction;
  - IF-2's area (2084 − 1290 = 794 mm²);
  - option 4 for the copper (22.01 mm each, a gap of up to 23.98 mm, not credited until a coupon).

**Smallest next action:** one text revision of section 15 with corrections 1 to 5 and the minors, with conditions 1 and 2 written into DD-6's owners (Layer 7 and board P's generator). Then board P's generator drafts DD-1 and DD-6, as the record already names.

**Owner decision:** L9STK CU, the outer copper weight, is genuinely his because it spends money; option 4 is now listed as the zero-cost route waiting on a coupon. Q-TI-L9S-1 and Q-TI-17 are outside contacts, so they are his to send unless the supplier carries them. Nothing else needs him.
