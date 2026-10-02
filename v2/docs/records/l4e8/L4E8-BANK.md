# L4-E8: board A's VBUS20 bulk bank re-sized (MESHSAT-1357, 1 October 2026, the second fix round)

Prototype design, desk arithmetic. Nothing is bought, built, powered or measured. No generator, registry, rendered page or record
of L4-E4 to L4-E7 is edited.

This record closes finding B-4 of `../l4e/L4-ENERGY-ARCHITECTURE.md` as L4-E6 left it ("the bank is to be re-sized by the
generator owner"). Every figure is printed, with its basis, by `ripple_dense.py` (`ripple_dense.out`, "out N" below).

Labels:
- MAKER, NETLIST, GENERATOR: read from a maker's sheet, the committed netlist or the generator.
- RECORD: the generator's own record, `gen_sch_a.py`'s comments and `../r4a/r4-decisions.md`.
- INFERRED, ASSUMPTION, SESSION (a choice this record makes), MODELED, CONDITIONAL, OPEN.

The collaborator checked `5ff06474` (`checks/astra-check-l4e8-1.md`, accepted: no) and rechecked `cc95fe1f`
(`checks/astra-check-l4e8-2.md`, accepted: no). After two failures on the same issue the method changed: the bank now rests on a
conservative bound over arbitrary independent branches, not on any search.

## Status

**B-4 closes at both R11 outcomes on the bound.** The bank is the six drawn EEHZK1V331P, each behind its own 45 mOhm ballast
resistor (R221 to R226, Milliohm HoJLR2512-3W-45mR-1%, LCSC C2903491). The front end's Cc2 (C6) goes from 680 pF to 3.3 nF
(C1613), and both go in with L4-E6's R12 at 12 mOhm.

| R11 outcome | Highest permitted current | Every can at most (the bound) | The rule's limit | One feasible configuration |
|---|---|---|---|---|
| 8 mOhm | 7.262 A | **2.4096 A** | 2.7745 A | 2.0239 A |
| 7 mOhm (only if bench V-A07 fails) | 8.300 A | **2.7661 A** | 2.7709 A | 2.3179 A |

The 7 mOhm figure meets the limit by 0.005 A. At both outcomes the front end's worst interval sits at VIN 9 V and fSW 172.3 kHz,
and the charger's at fCH 894 to 896 kHz. One ballast value serves both outcomes, so V-A07 changes nothing in the bank.

**What the bound covers.**
- Every can is taken independently over the ZK sheet's whole printed range: C from 0.56 to 1.56 x 330 uF, ESR from 0 to size
  G's cold limit, and the ESL band.
- Every ceramic, link and half-bridge part is taken over its own region.
- The two converters are taken at every switching frequency of their bands, with every exact coincidence added coherently.

**What stays CONDITIONAL or OPEN, named exactly:**
1. **CONDITIONAL, the lifetime (B4).** The sheet does not print the rated temperature rise, so the can's own rise must be
   measured (bench 7b.8, item 4).
2. **CONDITIONAL, the cold-ESR envelope.** The loop is verified with every can's intrinsic ESR anywhere from 0 to 300 mOhm.
   That is the sheet's limit at -40 C after endurance, taken down to -20 C (INFERRED). The bench confirms the envelope: the
   bank's ESR envelope at -20 C over service life at or below the modelled envelope, never a single can.
3. **ASSUMPTION, C190 and C191.** No maker figure is held for C57112 or C1588. Their regions are assumed (C 0.8 to 1.1 x
   nominal, ESR 1 to 4 x the predecessor's figure, ESL 0.5 to 1.0 nH). The L16 and C190 series resonance is a large term of the
   bound.
4. **Sampled, not bounded: VIN and VBAT.** The bound takes VIN on 26 points and VBAT every 0.05 V. It bounds the passives
   and the two switching frequencies continuously.
5. **OPEN, the restart ring over endurance.** First order, it reaches 16.13 A, 92 % of L1's typical Isat at 25 C. It belongs
   to L4-E6's saturation-aware C-5 sweep.

**Unchanged:**
- No approved requirement, owner ruling or Layer 3 file changes, and no service is reduced.
- No can is added.

## The recheck, and what changed

| Item | What the recheck found | What this round does | Where |
|---|---|---|---|
| **R1/R2** | The search took one target and five identical siblings. The split check had two sibling groups only. The coherent and higher-order terms were taken at the search's winning set only. So "every can independent" exceeded the evidence | **A conservative bound replaces the search** (the next section). <br>- Every branch is independent and every passive is in its region. <br>- Coherent coincidences and the omitted orders are bounded at the same conservative level. <br>- The bound is checked against brute-force sampling, in the script and in the tests. <br>- The ballast is re-selected on it: **45 mOhm**, where 38 and 40 mOhm are not shown to close | out 6 |
| **R4** | One can measured cold cannot close the loop obligation | **The loop is checked over the whole cold envelope**: <br>- every can's intrinsic ESR from 0 to 300 mOhm in 20 mOhm steps; <br>- with the ballast, R12 12 mOhm, B3's frequency band and the loads to 8.300 A, both bands; <br>- Cc2 at x0.75 and x1.25; <br>- twenty mixed banks. <br>The drawn compensation misses GM 10 dB at the cold end, so **Cc2 becomes 3.3 nF**: the smallest change, one part. The measurement only confirms the envelope, worded as above | out 7 |
| Minor, the ballast's derating | Not carried | The sheet's curve: 3 W to 70 C, zero at 170 C. Each resistor dissipates at most 0.349 W against 3.00 / 2.55 / 2.10 W at 62.1 / 85 / 100 C. Its temperature envelope runs from -20 C to its own surface temperature, a bench reading | out 6b |
| Minor, the energy term | Not handed to the energy-model owner | An operating-point-dependent loss term for REQ-072's owner, not to be counted twice once measured efficiency includes it: <br>- 2.09 W upper sum at the bound's worst corner; <br>- 0.0093 W at a nominal-parts illustration (VIN 13.8 V, 3 A) | out 6b |
| Minor, transient figures | Initial capacitance only | Labelled initial-only. The endurance range is carried: 1.1928 to 3.3198 mF, 16.1338 A restart, 1.0412 mJ, 10.2748 % soft-start draw at 9 V, and 0.455 to 1.494 s bleed. These are the recheck's own figures, reproduced | out 8 |

The first check's items stand as the first fix round resolved them:
- **B1:** coincidences are added coherently (out 5b).
- **B3:** the frequency envelope runs 171.76 to 227.08 kHz (out 5).
- **B4:** the lifetime is CONDITIONAL (out 6b).

Its B2 is now answered by the bound.

## The bound, and why it is conservative (out 6)

**The regions.** Every branch is independent of every other:
- **Each can.** R 44.38 to 346.12 mOhm: the ballast at either end of its 1.38 %, the can's ESR 0 to 300 mOhm, the layout's
  0.5 mOhm. L 2.0 to 5.5 nH (the can's INFERRED band, the ballast's and the layout's). C 184.8 to 514.8 uF (MAKER).
- **Each ceramic**, 18 on VBUS20 and 3 on FE_OUT: 4 to 7 uF, 2 to 5 mOhm, 0.8 to 1.5 nH (RECORD, INFERRED).
- **C190 and C191** as in item 3 of the status (ASSUMPTION).
- **L11 and L16:** 1 to 5 nH and 5 to 20 nH (RECORD, INFERRED).
- **R11 and R16:** at +-1.38 %.

**The argument, step by step.**
1. **One branch, one bin.** For a bin of frequency [f1, f2], a branch's reactance X = wL - 1/(wC) rises with w, L and C.
   Taking each over its own interval puts its impedance in a rectangle. This also lets each branch see its own w in the bin,
   which only enlarges the set.
2. **Its admittance.** The admittance lies in the rectangle's image under 1/z. Each edge maps onto an arc of a circle through
   the origin. Samples along each arc at equal angles have chords whose sagitta is at most 1e-4 of the image's largest modulus.
   Every boundary point lies within that sagitta of a chord, so the samples' hull grown by the largest sagitta holds the
   image's hull.
3. **Sums.** A sum of independent branches lies in the Minkowski sum of their enclosures, which is exact for convex polygons.
   n branches of one region give n times its enclosure.
4. **The source sides.**
   - Each source sits behind a link (R11 + L11 or R16 + L16) with its own shunt (the FE_OUT ceramics, or C190 and C191).
     Its Norton factor is k = 1/(1 + Z_link Y_shunt).
   - min |1 + Z_link Y_shunt| is bounded from below by a branch and bound over the link's rectangle. For a sub-rectangle with
     disk (c, r), the minimum over the shunt's polygon is exact (|c| times a point-to-polygon distance), less r times the
     polygon's largest modulus.
   - The shunt's admittance seen from VBUS20, 1/(Z_link + 1/Y_shunt), lies in the hull of the inverted sum (steps 2 and 3
     applied to the inverted polygon).
5. **The can's share.** The can's current per ampere of a source is k Y / (Y + Y_rest). |Y| / |Y + Y_rest| is bounded from
   above by a branch and bound over the can's own rectangle. Each sub-rectangle's disk inverts exactly to a disk (c, r), and
   then |Y| / |Y + q| <= (|c| + r) / (dist(-c, Q) - r).
6. **Decoupling only overstates.** k and Y_rest are taken separately, and each harmonic takes its own worst set.
   - Two exceptions are kept physical, because one physical part sets each: L11 is cut into 21 cells, and L16 with C190 into
     105 cells.
   - Each cell is bounded on its own and the worst cell is taken.
   - Without the cells, every charger harmonic in the resonance's range would sit on the L16 and C190 series resonance at once,
     which no single L16 and C190 can produce.
7. **The sources.**
   - Fourier coefficients are in closed form to the 120th harmonic.
   - A harmonic's amplitude is convex in the ripple, which is 1/f, so over a frequency interval (0.5 kHz for fSW, 2 kHz for
     fCH) it is at most the larger of its ends.
   - Each harmonic takes the largest bin bound over its frequency interval.
8. **Coincidences.**
   - Every exact coincidence fch / fsw = p / q with p <= 20 is added coherently: |a| + |c| at each coincident frequency,
     whatever the phase.
   - Every higher order is bounded by Cauchy-Schwarz.
9. **Above the 120th harmonic.**
   - |c_m| <= J / (2 pi m) + K / (2 pi m)^2, with J the waveform's jumps and K its slope jumps (integration by parts over a
     period). This is taken at the bins' bound up to 3.2 GHz.
   - Above 3.2 GHz every branch is past its series resonance and inductive. No sum of such branches is smaller than one of
     them, and |k| <= 1, so |T| <= 1.

**Checked against brute force (SESSION seeds).**
- **Per bin.** 4,800 fully independent configurations over 8 bins, each parameter at an end of its interval with probability
  0.7, read at most 0.8443 of the bin's bound. The tests repeat this with a seed of their own.
- **End to end.** 240 configurations with operating points read at most 0.4426 of the figure. Half had the L16 and C190
  resonance placed on a charger harmonic; half sat at an exact coincidence. The tests repeat this with 120 more.

**Where it is loose.** The bound is not claimed tight: at 45 mOhm it reads 2.7661 A where one feasible configuration reads
2.3179 A. The gap comes from:
- each harmonic taking its own worst passive set (the can's own parameters, its siblings', the ceramics');
- each source harmonic taking the larger end of its frequency interval.

## The decision (SESSION; out 6)

**The rule.** Every can must be at most 2.8 A less the consistency tolerance scaled to the current: 2.7745 A at 7.262 A, and
2.7709 A at 8.300 A.

**The search order.**
- Ballast values are taken ascending from L4-E4's catalogue reading (in stock).
- The scan starts at the first round's 38 mOhm, with the binding 7 mOhm outcome first.
- The first value whose BOUND meets the rule at both outcomes is taken.

**Why nothing smaller.** Below 38 mOhm, one feasible configuration exceeds the limit at 7 mOhm, so no bound can meet it. That
configuration is:
- the target can at the ballast's low end, with no ESR, the shortest branch and the largest C;
- the five siblings at the region's top;
- the coincidence fch = 2 fsw at the envelope's low corner, VIN 9 V, VBAT 10 V.

| Ballast | 7 mOhm: bound | Feasible | 8 mOhm: bound | Feasible | Outcome |
|---|---|---|---|---|---|
| 10 to 36 mOhm | not needed | 7.64 down to 2.8296 A | not needed | | excluded: a feasible configuration is over 2.7709 A |
| 38 mOhm | 3.1249 A | 2.6970 A | | 2.3546 A | not shown to close |
| 40 mOhm | 3.0037 A | 2.5765 A | | 2.2494 A | not shown to close |
| **45 mOhm** | **2.7661 A** | 2.3179 A | **2.4096 A** | 2.0239 A | **taken** |

**Reading the table.**
- 38 and 40 mOhm are not shown to fail either: their feasible worst is under the limit and their bound over it.
- 45 mOhm is the smallest catalogue value this method can show.
- Between 40 and 45 mOhm the catalogue holds nothing.

**Why a ballast, and not more cans, is still the smallest robust change.**
- Without a resistance floor no count of cans is bounded: 56.5 A on six cans and 59.2 A on eight (out 5). Screening does not
  bound the ESR over life or in the cold.
- The ballast is one printed floor per branch, it keeps the six cans, and the node's capacitance stays as drawn.

## The chosen bank: rating, ballast, energy (out 6b)

**Frequency (MAKER, ZK p.2).** Every harmonic is at or above 171.8 kHz. The correction for 100 uF and more is 1.00 from
100 kHz up, so no derating applies.

**Temperature and life: CONDITIONAL (B4).**
- The rating is the sheet's at 125 C, with no uplift taken.
- p.6's equation with the rated rise taken as zero bounds the life from below for the can's MEASURED rise dT:

| dT | At 62.1 C inside air | At 85 C (L1's temperature at the fault, a can beside it; ASSUMPTION) |
|---|---|---|
| 0 K | 131,400 h (the sheet's 15-year cap) | 64,000 h |
| 10 K | 131,400 h | 32,000 h |
| 20 K | 78,249 h | 16,000 h |
| 30 K | 39,124 h | 8,000 h |

**The ballast (MAKER, HoJLR2512 p.2).**
- Its rating is 3 W, derated from 70 C to zero at 170 C; the operating range is -50 to +170 C.
- At the bound's worst can, each resistor dissipates at most 0.349 W, against 3.00 W at 62.1 C, 2.55 W at 85 C and 2.10 W at
  100 C.
- Its temperature envelope runs from -20 C in use up to its own surface temperature, which the sheet does not give: a bench
  reading, 7b.8.
- Its tolerance carries 50 ppm/K over 75 K from 25 C (ASSUMPTION: up to 100 C).

**The energy model's term (for REQ-072's owner).**
- The six ballasts dissipate sum I_k^2 R_k, which depends on the operating point.
- At the bound's worst corner, the upper sum is **2.09 W** (six resistors at the worst can's bound).
- An illustration at nominal parts reads **0.0093 W**. The parts: cans 330 uF, 20 mOhm, 3.5 nH; ceramics 5.5 uF; L11 3 nH;
  L16 12.5 nH. The point: VIN 13.8 V, 3 A, VBAT 14.4 V, fSW 199.04 kHz, fCH 400 kHz. It is not a measurement.
- It must not be counted twice once a measured converter efficiency includes it.

**The ceramics.** No MLCC ripple rating is held for the 10u 50V X7R 1210, so no ceramic current is judged. The first round's
sampled ceramic figures are not carried.

## The loop over the cold envelope (out 7)

**The setup.**
- B3's frequency band, L4-E6's R12 at 12 mOhm, and loads 8.300 / 7.262 / 5.700 / 0.250 A.
- The bank's C corners and each branch's ballast at either end of its tolerance.
- Every can's intrinsic ESR e from 0 to 300 mOhm.

| Compensation | e | PM | GM | Widened GM | Every margin |
|---|---|---|---|---|---|
| drawn (15 k, 220 nF, 680 pF) | 0 | 79.3 deg | 18.2 dB | 16.7 dB | yes |
| drawn | 300 mOhm | 92.3 deg | 5.0 dB | 3.1 dB | **no** |
| Cc2 1 nF | ends | | | | fails at the cold end |
| **Cc2 3.3 nF (C1613)**, over 0 to 300 mOhm in 20 mOhm steps | worst | 61.4 deg (e 0) | 15.8 dB (e 300) | 14.4 dB (e 300) | **yes, every step** |
| Cc2 3.3 nF x1.25 (X7R tolerance and temperature) | 0 / 300 | 57.0 / 81.5 deg | 19.8 / 17.4 dB | 18.1 / 16.0 dB | yes |
| Cc2 3.3 nF x0.75 | 0 / 300 | 66.9 / 88.7 deg | 19.5 / 13.7 dB | 17.8 / 12.3 dB | yes |
| Cc2 3.3 nF, twenty mixed banks | | 64.5 deg | 17.2 dB | 15.7 dB | yes |

**Across every Cc2 3.3 nF row.**
- abs(1+T) stays at or above 0.74.
- Every crossover stays under Fsw / 20 and fRHP / 3.
- The output impedance stays under its bound.

**The mixed banks.** One to five cans sit at the ballast's low end with no ESR; the rest sit at its high end and 300 mOhm; C
is at either extreme.

**The choice (SESSION).** Cc2 was taken ascending through `lcsc_fill.py`'s 0603 capacitors, with Rc1 and Cc1 kept. 3.3 nF is
the first that meets every margin at both ends and then over the whole envelope: the smallest change, one part.

**ORDER.**
- On the drawn R12 (5 mOhm) at the record's loads, the ballast with Cc2 3.3 nF reads PM 46.3 deg at e = 0, and widened GM
  9.5 dB at e = 300 mOhm.
- So the ballast and Cc2 go in with L4-E6's R12, where the loop is verified.
- The draft refuses the repository's generator until the front end's call carries rcs="12m".

This is MODELED; L4-E6's bench Bode row is owed.

**The acceptance of the cold reading.** The bank's ESR envelope at -20 C over service life must be at or below the modelled
envelope: every can at most 300 mOhm at 100 kHz. A single can's reading cannot close it; it only confirms the envelope.

## What the bank's capacitance moves (out 8; INFERRED, first order: lossless, constant inductance, not saturation aware)

| | Node capacitance | Soft-start draw at 9 V | Bleed to release | Restart ring in L1 |
|---|---|---|---|---|
| Initial capacitance only (the cans at +-20 %, as recorded) | 1.67 to 2.61 mF | 8.6 % of 4.80 A | 0.64 to 1.17 s | 14.3 A (82 % of 17.5 A), 0.82 mJ |
| Over endurance (0.56 to 1.56 x 330 uF, the bound's range) | 1.1928 to 3.3198 mF | 10.2748 % | 0.455 to 1.494 s | 16.1338 A (92 %), 1.0412 mJ |

- No can is added, so nothing changes from the drawn bank.
- The endurance row carries the restart obligation into L4-E6's saturation-aware C-5 sweep, to 16.1 A. The ballasts' damping
  is not credited.

## Consistency with the history, and the reconciliation (out 4, 4b, 5)

The historical figures were checked, never targeted. Draft corrections are in `CORRECTIONS-DRAFT.md`.

| Historical figure | Derived | The assumption that differs | Which is right, and why |
|---|---|---|---|
| Drawn node, 5.7 A: 2.10 / 2.11 / 2.43 A | 2.101 / 2.113 / 2.431 on the record's grids; 2.114 / 2.125 / 2.431 converged | The source grids (the record gives counts and ends only; INFERRED that its rows miss the peaks) | Converged, on the record's rule, which is not a bound |
| Second fix-up's node, 3.43 / 3.31 / 3.01 A, 4,450 of 110,700 sets | 3.427 / 3.305 / 3.008 A, 4,450 | None | Agree |
| The re-review's point, 2.968 A | 2.9683 A | Damping corners not stated; one of 36 reproduces it | Agree |
| Worst VBUS20 ceramic, 1.09 A | 1.24 A converged | The charger and VBAT grids | Converged |
| Loop: PM 73.1 deg, GM 15.7 dB | 73.10 / 15.65 on the grid; 73.02 / 15.68 interpolated | Grid point below each crossing | Interpolated |
| `r11_dep.py`, B-4 at 7.262 A: 2.69 / 2.70 / 3.11 A | Record's rule 2.794 / 2.788 / 3.161 A; with coincidences 3.037 / 3.022 / 3.392 A | Per spread in `CORRECTIONS-DRAFT.md`: R11 in the network, the grids, the coincidences | Derived |
| The record's sharing (one can at a corner, siblings at s times its ESR) | Unbounded without a floor; bounded with the ballast | The cans' match, which the sheet does not print | The bound |
| The loop's corners (cans' ESR to 40 mOhm) | The sheet allows 300 mOhm cold | +20 C only | The cold envelope; Cc2 3.3 nF |

## Bench row 7b.8, restated (downstream obligations, not blockers)

1. **The ESR envelope.**
   - Read a sample of EEHZK1V331P at 100 kHz at the coldest the bench reaches toward -20 C, and carry the maker's endurance.
   - Accept when the bank's ESR envelope at -20 C over service life is at or below the modelled 300 mOhm per can.
2. **Each can's ripple current.** Read it with a sense loop on its lead, U3 drawing as the load, at the build's highest
   permitted current:
   - at 15.1 and 36 V;
   - at 9 V, at whatever current the build's limits hold there;
   - with the charger at both PWM_FREQ settings.

   **Pass:** each can at most 2.8 A less 0.03 A.
3. **Temperatures.** Read each can's top temperature and each ballast's surface temperature at the worst ripple. The can's rise
   dT enters the lifetime table above; the ballast's temperature enters its derating.
4. **The ceramics.** Read the hottest ceramic's temperature.
5. **The loop.** Run L4-E6's Bode row on the regenerated board, cold and warm.

## The uncertainties that remain

| Uncertainty | How it enters | What settles it |
|---|---|---|
| C190 and C191 (no maker figure held) | Assumed regions. The charger's part, 1.969 A^2 of the 7.651 A^2 at 7 mOhm, includes the L16 and C190 series resonance | The parts' impedance curves, or a sweep of the mounted parts |
| The cans' ESL band and the ceramics' bands (INFERRED) | Regions of the bound | An impedance sweep of one mounted can and the 1210's C at 20 V |
| VIN and VBAT between their grid points | Sampled | The FE's worst interval sits at VIN 9 V, the grid's end; a finer grid in the script, if wanted |
| The cans' cold ESR | The loop's envelope | Bench item 1 |
| The rated temperature rise | The lifetime | Bench item 3 |
| L1's Isat at temperature against the restart ring | 16.13 A over endurance | L4-E6's C-5 sweep |

## The interaction with L4-E4 and L4-E6, and what L4-E4's release still needs

**L4-E4.**
- R11 8 mOhm stands, and so does 7 mOhm if V-A07 fails. The bank holds both outcomes.
- R11's lower resistance raises the cans' current on the drawn bank (`CORRECTIONS-DRAFT.md`, per spread).

**L4-E6.**
- B-1 and B-2 are unaffected.
- B-4's "OWED" closes on the bound.
- R12 12 mOhm becomes a precondition of the ballast and of Cc2 (ORDER).
- Its B-4 lines take the superseded note of `CORRECTIONS-DRAFT.md`.

**The draft, `apply_gen_sch_a_bank.py`.**
- It gives `lm5176()` a `bulk_ballast` argument, which the other stages do not use. It draws each of the front end's cans on its
  own node behind R221 to R226.
- It changes the front end's Cc2 to ("3.3n", "C1613").
- It composes with L4-E4's R11 and R138 drafts and L4-E6's R12 draft in every order on disjoint lines (`test_l4e8.py`).

**L4-E4's release still needs:**
1. an accepted check of this record;
2. L4-E5's ILIM_HIZ line drafted for `gen_sch_a.py`;
3. the `RELEASE.md` files naming their accepted checks;
4. the circuit round applied together:
   - R12 before the ballast and Cc2;
   - the six resistors seated, each beside its can;
   - a box regeneration, with the gates and evidence re-taken;
   - the loop re-verified on the regenerated board;
   - the drafted corrections applied with it;
5. bench V-A07, which no longer moves the bank.

## For board A's generator owner (OWED, nothing applied)

`apply_gen_sch_a_bank.py TARGET [--check | --write]`:
- **Mode.** `--check` by default, writing only with `--write`.
- **Refusals.** It refuses:
  - a second application;
  - a designator already in use;
  - the repository's own generator until `RELEASE.md` here reads "released: yes" and names an accepted check;
  - the repository's own generator until L4-E6's R12 12 mOhm is in the front end's call.
- **Testing.** It was run only on scratch copies.
- **Owed with it.** If the pipeline maps parts by value, `lcsc_fill.py` needs a line for "45mOhm 1% 2512". Each ballast is
  placed beside its can, within the layout rule.
