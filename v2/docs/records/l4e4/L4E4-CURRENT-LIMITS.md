# L4-E4: board A's current-limit coordination and the outlet's trip (MESHSAT-1357, 1 October 2026)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and no generator, registry or rendered
page is edited. Items 2 and 5 of "The next implementable power-path choices" on
`../l4e/L4-ENERGY-ARCHITECTURE.md`, turned into values. Every figure is printed, with its basis, by
`l4e4_limits.py` (`l4e4_limits.out`, sections named below). Section 0 re-runs `../r11dep/r11_dep.py` in a child
process and reproduces `r11_dep.out` byte for byte. It then runs the same `main()` in-process and takes its locals,
so VSNS, the ISNS offset, R11's tolerance and TCR stack, U3's accuracy, the 0.079 A and the stage relations come from
that run rather than being retyped. No owner requirement changes, and nothing blocks.

## The chosen values

| Item | Value | Reason | Closure criterion (the page's) |
|---|---|---|---|
| U3 IIN_HOST (A-1) | **4.65 A**: code 93, `REG0x0F/0E() = 0x5D00`, RSNS_RAC = 0b because R16 is 10 mOhm (MAKER SLUSE66A p.80 9.6.22, 50 mA resolution over 50 to 6350 mA; p.25 9.3.5). Maximum 4.766 A, the larger of nominal + 100 mA (p.80) and +2.5 % (p.1). Rewritten after every adapter removal (reset to 3.25 A, p.26) | The declared efficiencies are the only ones the tree holds (C-8 open). At them the window needs U3's minimum at 4.517 A at the 19.146 V bus (MODELED, `l4e_replay.out` 8), and 4.65 A less the records' INFERRED 0.1 A gives 4.55 A. A2's result is unchanged (286.3 / 516.5 Wh unserved, as at the drafted 6.2 A). The 0.97 bracket (5.05 A) rests on no document | A-1's stacked minimum (below); C-7 (below) |
| R11 (A-1, C-2) | **8 mOhm, Milliohm HoJLR2512-3W-8mR-1%, LCSC C2904240** (+-1 %, +-50 ppm/K, 3 W; LCSC's answer in `inputs/`). Its datasheet link returns the held series sheet byte for byte (sha256 3224518d...), so C-2's "its sheet filed" holds | It is the largest value in the held part's catalogue family whose stacked minimum clears U3's maximum + 0.079 A with a C-1 allowance no tighter than the 0.29 mOhm already accepted. Largest means the lowest highest-permitted current: 7.262 A, where the held 10 mOhm gives 5.810 A and the drafted 6.2 mOhm 9.370 A. 9 mOhm leaves a negative tap budget (`.out` 2) | The stacked minimum of the fitted R11 is at least U3's maximum plus the other loads, re-run through r11_dep.py's band; bench 7b.1 |
| C-1, R11's taps | **0.54 mOhm at 25 C** for both taps together (0.70 mOhm working; r11_dep.py's margin rule at 8 mOhm and 4.845 A). kelvin_check's own 1 % per tap (0.16 mOhm) is stricter | Recomputed by the same rule, so it can be no tighter than the accepted 0.29 mOhm | kelvin_check at or under 0.54 mOhm; bench 7b.3: at most 0.54 mOhm x I (2.63 mV at 4.845 A) |
| C-9 | 0.079 A carried (r11_dep.out 3: four FETs switching) | The page's sizing | A bench reading of R11's current less R16's |
| R138 (DR-03) | **5 mOhm, Milliohm HoJLR2512-3W-5mR-1%, LCSC C2903482**, TI's recommended value (SLVSDG8B 8.3.8.2 p.31; p.49 9.2.4.2.3, the 5/9/15 V at 3 A example: "5 mOhm, +-1 %"). Board A's other 5 mOhm part, C500739, is not named because its maker sheet is not held | **Trip 3.793 to 4.576 A** (VI(TRIP) 19.2 to 22.6 mV, p.11, +-1 %, 50 ppm/K over 45 K). Every PDO is 3.0 A: 5, 9 and 15 V by Table 2, Equation 2 and Table 5 (pp.28 and 29) from the netlist's straps, plus the non-PD 5 V at 15 W (8.3.6). Margin +0.793 A. As drawn, 10 mOhm trips at 1.897 to 2.288 A, which is DR-03 reproduced | The netlist carries 5 mOhm; the window lies above every PDO's current; a 3 A load on each PDO holds without a trip |

**R11 at the three temperatures** (`.out` 2). Stacked minimum = (VSNS minimum 43 mV less the 0.3 mV ISNS offset) /
(R11 x 1.01 x (1 + 50 ppm/K x the excursion) + the taps). R11's own temperature runs from the air to the air + 17.3 K
(INFERRED by r11_dep.py's derating line, 33.3 K/W, at the band minimum's current with the ripple). The margins are
over 4.845 A:

| Air | R11 alone | with kelvin_check's 1 % per tap | with C-1's full 0.54 mOhm |
|---|---|---|---|
| -20 C | 5.273 A, +0.427 A | 5.182 A, +0.336 A | 4.976 A, +0.130 A |
| 25 C | 5.280 A, +0.435 A | 5.171 A, +0.325 A | 4.927 A, +0.082 A |
| 62.1 C | 5.270 A, +0.425 A | 5.147 A, +0.302 A | 4.874 A, +0.029 A |

At r11_dep.py's own 75 K envelope (R11 up to the ASSUMED 100 C), R11 alone gives 5.265 A (+0.420 A). C-1's rule hands
that whole margin to the taps. The load-life drift of +1 % (p.4, not stacked by the rule) would leave +0.367 A.
**R11's dissipation** at 4.845 A is 0.190 W DC. With all the output ripple through it (an upper bound), it is 0.262 W at
15.1 V and 0.440 W at 9.0 V in. At 62.1 C air that puts R11 at 68.4 to 76.8 C, under the ASSUMED 100 C, against a rating
derated to 2.80 W (p.2).

**R138 against what it protects** (`.out` 3): the trip maximum is 4.576 A. That is below R138's own 24.5 A
(sqrt(P/R), HoJLR2512 p.3), Q27's 42 A (SLPS632 p.1) and the Bulgin PXP4043/C receptacle's 5 A (4000 series sheet p.3,
+0.424 A). R138 dissipates 0.045 W at 3 A. Its own taps (U18 pins 19 and 21) are allowed at most 1.15 mOhm at 25 C
(INFERRED, the same margin rule). pcb_sensitive.yaml declares no R138 tap today.

## What this task found beside the values

- **U3's maximum in the replay.** `l4e_replay.out` 8 prints 4.829 A through R11 using the 100 mA alone. r11_dep.py's
  own rule (p.1's 2.5 % is the larger above 4 A) gives 4.845 A, and this record uses the larger. No choice moves.
- **The 0.97 bracket is a hardware change, not a register write.** 5.05 A (5.255 A through R11) needs 7 mOhm (C2904239).
  Its highest permitted current is 8.300 A, 1.037 A above the chosen R11's. 8 mOhm would leave 0.011 mOhm for the taps.
- **TI's sheet labels its two trip rows inconsistently.** p.11 labels the 29 to 34 mV row "HIPWR = DVDD (5 A enabled)".
  Tables 4 and 5, Equation 2 and 8.3.6 make HIPWR to DVDD the 3 A configuration, and p.31 ties 3.8 to 4.5 A to it and to
  5 mOhm. The 19.2 to 22.6 mV row is taken (INFERRED). On the label's reading the window would be 5.730 to 6.884 A, above
  the receptacle's 5 A. So the bench must find the trip current itself.
- **Carried to item 4 (fault handling), not decided here** (INFERRED by r11_dep.py's relations). At the 7.262 A highest
  permitted current, L1's peak at 9 V is 20.74 A against the typical 17.5 A Isat (B-1). VBUS20's worst can is 2.69 A
  matched and 3.11 A at a 2:1 ESR spread, against 2.8 A (B-4). Hiccup (B-2) or rated parts close these.

## What stays INCONCLUSIVE, and why

- **C-7, U3's input-current minimum.** SLUSE66A p.10 prints IIN_DPM accuracy only for the 5 mOhm RAC (+-0.2 A at 0.8 to
  7.8 A, -40 to 105 C). Board A uses 10 mOhm. The records' INFERRED 0.1 A margin is carried (4.55 A). It is consistent
  with +-1 mV over 10 mOhm and with p.80's 100 / 200 mA pair. p.1's 2.5 % read as a minimum gives 4.534 A, still at or
  above 4.517 A.
- **J_USBC_OUT's pin rating.** Board A's 2.54 mm pigtail header has no part number and no maker sheet.
- **Which VI(TRIP) row board A's strap selects**, because of the maker's own label conflict (above).
- **R11's real temperature.** 100 C stays an ASSUMPTION; the rise is the derating line's (no thermal resistance is
  printed).
- **C-8, the three efficiencies.** They decide whether 5.05 A is ever worth its hardware.

## What the bench must still show

- **7b.1:** the front end's CC onset, with an electronic load past U3, lies above 4.845 A at -20, 25 and 62 C.
- **7b.3:** R11's Kelvin error is at most 0.54 mOhm x I at 25 C.
- **C-7:** U3's input current at the 4.65 A setting reads at or above 4.55 A.
- **The outlet:** a 3 A load on each PDO (5, 9 and 15 V, and the non-PD 5 V) holds without a trip. Then a slow ramp finds
  the trip current inside 3.79 to 4.58 A.

## For board A's generator owner

`apply_gen_sch_a_r11.py` and `apply_gen_sch_a_r138.py` are drafts, never applied to the tree. Each checks that its old
text occurs once, that the new text differs and has not been applied yet, and that the result parses. It writes only
with `--write`. R11 goes in a circuit round together with:

- the firmware setting and A-2's rule;
- B-3's re-declarations and B-4's node analysis at 7.262 A;
- B-1 and B-2;
- pcb_sensitive.yaml's FE_ISNS text.

R138 can go on its own, with its taps declared. After either regeneration, r11_dep.py (and with it this record's
section 0) refuses by design: both describe the circuit before the change.
