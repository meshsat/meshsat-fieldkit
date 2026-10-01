# L4-E4: board A's current-limit coordination and the outlet's trip (MESHSAT-1357, 1 October 2026)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and no generator, registry or rendered
page is edited. Items 2 and 5 of "The next implementable power-path choices" on
`../l4e/L4-ENERGY-ARCHITECTURE.md`, turned into values. This is the second round, after check `checks/astra-check-l4e4-1.md`
(not accepted). Every figure is printed, with its basis, by `l4e4_limits.py` (`l4e4_limits.out`, sections named below).

Section 0 re-runs `../r11dep/r11_dep.py` in a child process and reproduces `r11_dep.out` byte for byte. It then runs the
same `main()` in-process and takes from that run: VSNS, the ISNS offset, the TCR, U3's accuracy, the 0.079 A, the stage
relations, `band()`, lcsc_fill.py's map and the C2903468 reading. The resistors' tolerance is read from the HoJLR2512 sheet
(p.1, F = ±1 %) and from each part's LCSC answer. r11_dep.py's `band()` types its 1 % inside, so it is checked to equal the
band at that read tolerance.

**Status.** No owner requirement changes, and no owner decision is needed (neither check found one). The targeted
recheck (`checks/astra-check-l4e4-2.md`) accepted B1 and the three minors. Its one remaining B2 item, the 15 V hold
window, is fixed here for the coordinator's own verification. Two things stay conditional on the bench: the setting
depends on C-7, and the outlet's VI(TRIP) row on bench (a).

## The chosen values

| Item | Value | Reason | Closure criterion (the page's) |
|---|---|---|---|
| U3 IIN_HOST (A-1) | **4.70 A**: code 94, `REG0x0F/0E() = 0x5E00`, RSNS_RAC = 0b because R16 is 10 mOhm (MAKER SLUSE66A p.80 9.6.22; p.25 9.3.5). U3's own maximum is 4.817 A, the larger of nominal + 100 mA (p.80) and +2.5 % (p.1). Rewritten after every adapter removal (reset to 3.25 A, p.26) | U3 regulates the voltage across R16. R16 is C2903468, HoJLR2512-3W-10mR-1% (±1 %, ±50 ppm/K), with its temperature in r11_dep.py's envelope (-20 C to the ASSUMED 100 C). So U3's board current runs from (setting less the INFERRED 0.1 A) / 1.01379 to 4.817 A / 0.98629. 4.70 A is the smallest code whose minimum, **4.537 A**, covers the 4.517 A the window needs at the declared efficiencies (MODELED, `l4e_replay.out` 8; C-8 open) | A-1's stacked minimum (below); C-7 (below) |
| R11 (A-1, C-2) | **8 mOhm, Milliohm HoJLR2512-3W-8mR-1%, LCSC C2904240: still qualifies.** Its datasheet link returns the held series sheet byte for byte, so C-2's "its sheet filed" holds | Chosen with the setting. It is the largest catalogue value whose stacked minimum clears U3's maximum board current plus 0.079 A, **4.964 A**, with a C-1 allowance no tighter than the 0.29 mOhm accepted. Largest means the lowest highest-permitted current, 7.262 A. 9 mOhm leaves a negative tap budget (`.out` 2) | The stacked minimum of the fitted R11 is at least U3's maximum plus the other loads, re-run through r11_dep.py's band; bench 7b.1 |
| C-1, R11's taps | **0.38 mOhm at 25 C** for both taps together: 0.4924 mOhm working and 0.3803 mOhm at 25 C by r11_dep.py's margin rule, rounded down. The first round's 0.54 mOhm is withdrawn. kelvin_check's own 1 % per tap (0.16 mOhm) is stricter | Recomputed at 4.964 A by the same rule | kelvin_check at or under 0.38 mOhm; bench 7b.3 |
| C-9 | 0.079094 A carried (r11_dep.out 3: four FETs switching) | The page's sizing | A bench reading of R11's current less R16's |
| R138 (DR-03) | **5 mOhm, Milliohm HoJLR2512-3W-5mR-1%, LCSC C2903482**, TI's recommended value (SLVSDG8B 8.3.8.2 p.31; p.49 9.2.4.2.3, the 5/9/15 V at 3 A example: "5 mOhm, ±1 %") | **Trip 3.793 to 4.576 A** (VI(TRIP) 19.2 to 22.6 mV, p.11, ±1 %, 50 ppm/K over 45 K). Every PDO is 3.0 A: 5, 9 and 15 V from the netlist's straps by Table 2, Equation 2 and Table 5 (pp.28 and 29), plus the non-PD 5 V. Margin +0.793 A. The trip maximum is below R138's 24.5 A, Q27's 42 A and the Bulgin PXP4043/C receptacle's 5 A (+0.424 A). As drawn, 10 mOhm trips at 1.897 to 2.288 A | The netlist carries 5 mOhm; the window lies above every PDO's current; bench (a) and (b) below |

**R11 at the three temperatures, R16 included** (`.out` 2). The stacked minimum is (43 mV less the 0.3 mV ISNS offset)
divided by (R11 × 1.01 × (1 + 50 ppm/K × the excursion) + the taps). R11's own temperature runs from the air to the
air + 17.3 K (INFERRED, r11_dep.py's 33.3 K/W). U3's bound uses R16's envelope in every row. The margins are over
4.964 A:

| Air | R11 alone | with kelvin_check's 1 % per tap | with C-1's 0.3803 mOhm |
|---|---|---|---|
| -20 C | 5.273 A, +0.309 A | 5.182 A, +0.218 A | 5.061 A, +0.097 A |
| 25 C | 5.280 A, +0.317 A | 5.171 A, +0.207 A | 5.028 A, +0.064 A |
| 62.1 C | 5.270 A, +0.307 A | 5.147 A, +0.183 A | 4.986 A, +0.023 A |

At r11_dep.py's own 75 K envelope, R11 alone gives 5.265 A (+0.301 A), and C-1's rule hands that whole margin to the
taps. The load-life drift of +1 % (p.4, not stacked by the rule) would leave +0.249 A.

**R11's dissipation** at 4.964 A is 0.199 W DC. With all the output ripple through it (an upper bound), it is 0.275 W at
15.1 V in and 0.462 W at 9.0 V in. At 62.1 C air that puts R11 at 68.8 to 77.5 C, under the ASSUMED 100 C, against a
rating derated to 2.77 W.

## What this task found beside the values

- **U3's maximum in the replay.** `l4e_replay.out` 8 prints its current through R11 using U3's 100 mA alone. The larger
  of p.80's 100 mA and p.1's 2.5 % is used here, and then divided by R16's low corner.
- **The 0.97 bracket is a hardware change, not a register write.** With R16 in, the bracket needs 5.10 A (5.379 A through
  R11). That needs 7 mOhm (C2904239), whose highest permitted current is 8.300 A, 1.037 A above the chosen R11's.
- **TI's sheet labels its two trip rows inconsistently.** p.11 labels the 29 to 34 mV row "HIPWR = DVDD (5 A enabled)".
  Tables 4 and 5, Equation 2 and 8.3.6 make HIPWR to DVDD the 3 A configuration. The 19.2 to 22.6 mV row is taken
  (INFERRED), and bench (a) must demonstrate it. On the label's reading the window would be 5.730 to 6.884 A, above the
  receptacle's 5 A.
- **Carried to item 4 (fault handling), not decided here** (INFERRED). At the 7.262 A highest permitted current, L1's peak
  at 9 V is 20.74 A against the typical 17.5 A Isat (B-1). VBUS20's worst can is 2.69 A matched and 3.11 A at a 2:1 ESR
  spread, against 2.8 A (B-4). The candidate remedies are hiccup (B-2) or a rated L1 and bank. None is chosen here.
  Hiccup's own peak current and ripple must pass item 4's criteria: L1 at most 90 % of Isat at its temperature, and every
  can at most 2.8 A over the ESR bands.

## The outlet's bench procedure (it cannot pass on U19's limit or a voltage fault)

U19's own average limit (R81 10 mOhm) is INFERRED at 4.212 to 5.810 A. That overlaps both trip windows: under load U19
can limit first, VBUS then falls, and p.31 treats that as an OCP event. So a shutdown seen with U19 in the path does not
identify U18's comparator.

**(a) U18's comparator.**
- **Set-up.** Hold U19 in shutdown by pulling its EN/UVLO, PD_UVLO, to GND; U18 does not use that net. Put a regulated
  laboratory supply on PD_VPWR (U18's VPWR and Q27's drain), with its current limit set above 6.884 A. Read its no-load
  current first, to show nothing feeds back. A PD sink on J_USBC_OUT takes the 5 V contract. 9 and 15 V likewise if the
  supply follows CTL1 and CTL2.
- **Ramp.** An electronic load steps up from 3.0 A in 10 mA steps, each held at least 1 ms (tOCP is 15 us, p.11).
- **Recorded together:** U18's differential sense voltage V(pin 19) - V(pin 21) by a Kelvin differential probe; VBUS at
  pin 21 and at the connector; Q27's gate PD_GDNG; the supply's current-limit flag; the load current; R138 measured
  four-wire.
- **When a run counts.** Only if the supply never limits, and VBUS stays **strictly** inside the contract's hold window
  up to the GDNG falling edge.
  - **Lower bound:** above the larger of the slow UVP maximum and V(VBUS_FTH)'s maximum, 3.9 V (MAKER SLVSDG8B p.8, 7.5).
  - **Upper bound:** below the smaller of the fast OVP and slow OVP minima, because a fast OVP also disables GDNG (p.31).
  - **The windows** (p.8, TPS25740A rows, min / typ / max):

    | Contract | V(FOVP) | V(SOVP) | V(SUVP) | Window |
    |---|---|---|---|---|
    | 5 V | 5.8 / 6.05 / 6.3 V | 5.5 / 5.65 / 5.8 V | 3.5 / 3.65 / 3.8 V | 3.9 V < VBUS < 5.5 V (slow OVP) |
    | 9 V | 10.1 / 10.55 / 11.0 V | 10.0 / 10.2 / 10.4 V | 6.8 / 6.95 / 7.1 V | 7.1 V < VBUS < 10.0 V (slow OVP) |
    | 15 V | 16.2 / 16.95 / 17.7 V | 16.3 / 16.5 / 17.0 V | 11.7 / 11.95 / 12.2 V | 12.2 V < VBUS < 16.2 V (fast OVP) |
- **Closure.** Take the last differential reading before the GDNG edge as the demonstrated threshold.
  - In 19.2 to 22.6 mV, it demonstrates the 3 A row, and the trip current with R138 as measured lies in 3.79 to 4.58 A.
  - In 29 to 34 mV, it demonstrates the label's row, and R138 is re-chosen (that window exceeds the receptacle's 5 A).
  - Anything else is no result.

**(b) The delivered configuration, U19 in the path.** Hold 3.0 A on each advertised voltage (5, 9 and 15 V, and the
non-PD 5 V) for at least one hour or to thermal steady state. There must be no GDNG edge, and VBUS must stay strictly
inside its hold window.

## What stays INCONCLUSIVE, and why

- **C-7, U3's input-current minimum.** SLUSE66A p.10 prints accuracy only for the 5 mOhm RAC (±0.2 A, -40 to 105 C), and
  board A uses 10 mOhm. The choice is CONDITIONAL on the records' INFERRED 0.1 A: 4.60 A at U3, 4.537 A in board current.
  p.1's 2.5 % read as a minimum gives 4.520 A, +0.003 A.
- **J_USBC_OUT's pin rating.** The header has no part number.
- **Which VI(TRIP) row the strap selects.** Bench (a) decides it.
- **R11's and R16's real temperatures.** 100 C stays an ASSUMPTION.
- **C-8, the efficiencies.**

## What the bench must still show

- **7b.1:** the front end's CC onset, with an electronic load past U3, lies above 4.964 A at -20, 25 and 62 C.
- **7b.3:** R11's Kelvin error is at most 0.38 mOhm × I at 25 C (1.89 mV at 4.964 A).
- **C-7:** at the 4.70 A setting, the input current by a reference meter reads at or above 4.60 A × 10 mOhm / R16 measured
  four-wire, which is at least 4.537 A, and at or above 4.517 A.
- **The outlet:** bench (a) and (b) above.

## The check, and what changed

| Check item | What changed |
|---|---|
| B1, R16 left out of U3's bounds | U3's board-current bounds now divide by R16's factor at ±1 % and ±50 ppm/K, with R16 in r11_dep.py's envelope. The first round's 4.65 A fails with R16 in: minimum 4.488 A, and 4.912 A through R11, which gives a full-tap margin of -0.037 A at 62.1 C. The setting and C-1 were chosen together: 4.70 A (code 94, 0x5E00) and 0.38 mOhm at 25 C. 8 mOhm still qualifies. The collaborator's bounded candidate (4.70 A, below 0.3803 mOhm) was verified by the script, not adopted on its word. 7b.1 is now 4.964 A, 7b.3 is now 0.38 mOhm. C-7 stays conditional. Test `t_r16_tolerance_old_bounds_fail_new_bounds_pass` passes the old choice under the old bounds and fails it under the new |
| B2, the ramp could not isolate U18 | Bench (a) takes U19 out of the path and holds VBUS inside the maker's windows. It records the differential threshold, VBUS and PD_GDNG, and closes on the demonstrated VI(TRIP) row. Bench (b) holds 3 A on each advertised voltage. Test `t_outlet_bench_isolates_u18` |
| Minor 1, typed tolerance | The tolerance is read from the sheet and the LCSC answers, and r11_dep.py's `band()` is checked against it. `l4e4_limits.py` holds no 1.01 or 0.99 literal. Test `t_tolerance_is_read_not_typed` |
| Minor 2, "hiccup closes these" | Hiccup is now a candidate remedy whose peak current and ripple must pass item 4's criteria |
| Minor 3, "nothing blocks" | Restated under **Status**: no owner decision, the recheck owed, two items conditional on the bench |
| Recheck (`checks/astra-check-l4e4-2.md`), B2: the 15 V window reached 16.3 V, past the fast OVP's 16.2 V minimum | Each window's upper bound is now the smaller of the V(FOVP) and V(SOVP) minima, read from p.8 for every contract, with VBUS strictly inside. The 15 V window becomes 12.2 V < VBUS < 16.2 V. The 5 V and 9 V upper bounds do not move: their slow OVP minima, 5.5 V and 10.0 V, are below their fast OVP minima, 5.8 V and 10.1 V. Test `t_outlet_bench_isolates_u18` now refuses a 16.25 V and a 16.3 V excursion at 15 V, accepts 16.15 V, and refuses each boundary itself |

## For board A's generator owner

`apply_gen_sch_a_r11.py` and `apply_gen_sch_a_r138.py` are drafts, never applied to the tree. They write only with
`--write` and refuse a second application. R11 goes in a circuit round together with:

- the firmware setting, 4.70 A (0x5E00) with RSNS_RAC = 0b, and A-2's rule;
- B-3 and B-4 at 7.262 A;
- B-1 and B-2;
- pcb_sensitive.yaml's FE_ISNS text.

R138 can go on its own, with its taps declared (at most 1.15 mOhm at 25 C, INFERRED). After regeneration, r11_dep.py (and
with it this record's section 0) refuses by design: both describe the circuit before the change.
