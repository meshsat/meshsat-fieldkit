accepted: CONFIRMED AS CONDITIONAL

# Record l9stk: the independent checker's check 5, PROTECTION: CONFIRMED AS CONDITIONAL (B-R2 excluded) (filed as received)

MESHSAT-1357. An AI review by a fresh Claude session that authored none of the record (an independent checker, not a qualified engineering review, not an Astra check), read-only in a disposable scratch clone at `0d72880b34e337a6f2e26c1420507b813784b533` (branch `fnd/l9stk`). Time: 4 October 2026, begun 04:29 CEST, interrupted by the usage limit, finished 12:21 CEST. Nothing in the kit has been built, bought or measured.

Scope, from the coordinator's brief: the targeted recheck of B-R1's correction (one SOA criterion for both variants; C-1c, the restart inhibit on the breaker pad) and the minors, sections 15.4, 15.4b, 15.6, 15.7 and 15.8, `l9stk_protection.py` and its output; B-R2 (charging through a latched breaker) left out by the coordinator's brief, for L4-E11's round 9.

Filed by the integrator of set 29 from the checker's final message for the round, without edits to its content. The record's author answered it in the next round (`L9-STACKUPS.md` sections 14 and 15 name each revision); this note is the checker's own record of what it read and found.

## The checker's report, as received

**PROTECTION: CONFIRMED AS CONDITIONAL** (B-R2 excluded)

The B-R1 correction holds and every figure I recomputed matches the record. What remains open is how the inhibit's error budget is split; the record leaves it unallocated, and the comparator choice decides whether the window closes. I resumed the same scratch clone at 0d72880b with SLVA673A fetched: `test_l9stk` gave 41 passed, 0 failed, 0 skipped. The tree is unchanged and the clone is deleted.

**What reproduces**
- **One criterion for both variants.** For the worst resistive start (180 mJ, equivalent to 4.46 ms at 40.32 W), I get 0.545 from the inside air, 0.575 at the trip (0.639 with the 10 % reading allowance) and 0.600 at the block edge (0.667 with it). The -2 still fails. Without the inhibit, a restart at the held 101.0 °C case would be 0.82. My block edge with the reading allowance is 83.0 °C against the record's 83.20 °C, a difference that comes only from how the SOA figure is interpolated.
- **The NTC, from the held Murata sheet.** R25 10 kΩ ±1 %, B25/50 3380 K ±1 %, B25/85 3434 K (printed as a reference value), maximum current 0.12 mA, dissipation constant 1.5 mW/°C.
  - About 1653 Ω at the 80.2 °C trip; sensitivity 2.75 %/K.
  - Tolerance ±0.36 K from R25 and ±0.65 K from B, 1.02 K in all, leaving ±1.95 K.
  - Bridge current 0.111 mA at 16.8 V; self-heating about 0.01 K.
  - The NTC node sits at 116 mV at 10.6 V and 184 mV at 16.8 V, so 1 K is 3.19 mV and 5.05 mV.
- **PGD's thresholds.** It goes high below 0.67 to 1.85 V of VDS and low above 1.62 to 3.40 V. In each state:
  - **Starting:** PGD is low, so the inhibit can block a hot start.
  - **In a fault:** PGD goes low once VDS passes 1.62 to 3.40 V. An early current limit with a small VDS keeps PGD high and ends in the normal timer latch, which is the 0.57 case.
  - **Latched:** PGD is low if OUT has collapsed. If an input holds OUT up, PGD is high and the inhibit is inert, but then VDS is small and a restart's stress is low.
  - **Running:** PGD is high, because VDS at 23.93 A is about 21 mV.
  - So a running breaker cannot be turned off by the inhibit. One exception is in the minors.
- **A fault while hot** turns off through UVLO without latching. It restarts once at no more than 83.2 °C and then latches with the pad cool. That is bounded: the pad cannot reheat without current.
- **The diode path.** The C_U discharge peaks at 107 mA: 0.11 of the 1N4148W's 1 A one-millisecond surge and 0.71 of its 150 mA average rating. The undock turn-off is 2.5 µs + 16 µs + 395 µs = 0.41 ms, safe to 2.42 m/s (2.36 m/s with UVLODEL's 11 µs typical).
- **The hold and what follows from it.** 0.110 s (fast end) to 0.907 s (slow end). IF-1 leaves room for 0.81 A of load. DD-7 restarts within 0.948 s.
- **Every earlier minor is answered correctly:** IF-1 marked critical, the guard's restart limited to held-off loads, both readings of the UVLO edge, the duty marked conservative, and the undock path bypassing C_U.

**Blockers:** none.

**Conditions (owner: board P's generator, record l8p, for DD-8)**
1. **Allocate the ±1.95 K budget.** The record lists what it must cover (the comparator, the bridge, the hysteresis, the pad gradient) but splits it among none of them, and the part choice decides whether it closes. At 10.6 V:
   - an LM393 alone uses 2.2 K at its 25 °C maximum and 2.8 K over temperature, more than the whole budget;
   - a 5 mV-maximum precision comparator uses 1.57 K;
   - 1 % bridge resistors take 0.36 K and a 1 % reference pair another 0.73 K.

   One split that closes: a zero-drift amplifier or a comparator with at most about 1.5 mV over board P's temperature (0.47 K or less), 0.1 % resistors (0.07 K), hysteresis of 0.5 K or less, which leaves about 0.9 K for the pad-to-case gradient that E-15 must show. Write this into DD-8.
2. **The NTC's tolerance at 80 °C is assumed, not printed.** The held sheet is a product-search sheet with typical values and says to consult the approval sheet. The 1.02 K applies the 25/50 B tolerance to a reference B25/85. Confirm it from Murata's approval sheet or within E-15.
3. **A detached or open NTC reads cold.** That silently removes the inhibit (fails unsafe and latent), whereas a short reads hot and locks out, which shows at once. Add a commissioning check like E-12. The part has 10 mm leads, so its bond to the pad matters.

**Minors**
- **Interaction with the service at the worst air.** The breaker pad sits at 77.8 to 80.6 °C at 10 A, and 81 to 90 °C at 18 A on a steady bound. That is inside or above the window. The inhibit stays inert while PGD is high. But a current-limit excursion that pulls OUT down by more than 1.62 to 3.40 V while the pad is above the trip turns the breaker off at once, with no timer grace, and keeps it off, unlatched, until the pad cools. E-10 should require VDS below 1.62 V during excursions.
- **Lockout at the allow edge.** A unit whose trip sits at 77.25 °C needs the pad within 1 K of a 76.25 °C air before it will restart. At that air the cells' hot stop has already shut the kit down; state this.
- **The cooling time to the trip** after the held state is still not held (E-15).

**Smallest next action.** Write the budget allocation (condition 1) and the NTC checks (conditions 2 and 3) into DD-8 and E-15, add the PGD-excursion line to E-10, then board P's generator draws C-1c. B-R2 gets its own check when L4-E11's charge-inhibit round lands.

**Owner decision.** Nothing new. L9STK CU, the copper weight, is still his because it spends money. Q-TI-L9S-1 and Q-TI-17 still need sending to TI, an outside contact, by him or through the supplier.
