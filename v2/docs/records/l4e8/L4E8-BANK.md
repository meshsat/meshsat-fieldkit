# L4-E8: board A's VBUS20 bulk bank re-sized (MESHSAT-1357, 1 October 2026, the fix round)

Prototype design, desk arithmetic. Nothing is bought, built, powered or measured. No generator, registry, rendered page or record
of L4-E4 to L4-E7 is edited.

This record closes finding B-4 of `../l4e/L4-ENERGY-ARCHITECTURE.md` as L4-E6 left it ("the bank is to be re-sized by the
generator owner"). Every figure is printed, with its basis, by `ripple_dense.py` (`ripple_dense.out`, "out N" below).

Labels:
- MAKER, NETLIST, GENERATOR: read from a maker's sheet, the committed netlist or the generator.
- RECORD: the generator's own record, `gen_sch_a.py`'s comments and `../r4a/r4-decisions.md`.
- INFERRED, ASSUMPTION, SESSION (a choice this record makes), MODELED, CONDITIONAL, OPEN.

This is the fix round after the collaborator's check of `5ff06474` (`checks/astra-check-l4e8-1.md`, accepted: no). The first
round's eight-can bank is withdrawn. Section "The check, and what changed" maps each item.

## Status

**B-4 closes at both R11 outcomes with the six drawn EEHZK1V331P, each behind its own 38 mOhm ballast resistor** (R221 to R226,
Milliohm HoJLR2512-3W-38mR-1%, LCSC C2903481). The ceramics stay as drawn.
- **No screening is needed.** Each can is independent over the ZK sheet's whole printed range, with no ESR floor, down to its
  cold limit.
- **The two converters add at their worst relative phase** wherever their harmonics coincide.
- **The worst can reads 2.366 A at R11 8 mOhm (7.262 A) and 2.710 A at 7 mOhm (8.300 A).** The rule's limits are 2.7745 and
  2.7709 A against the 2.8 A rating. One value serves both outcomes, so bench V-A07 changes nothing in the bank.
- **No can is added.** The node's capacitance, the soft start, the bleed and the restart ring are as drawn.

**What remains, named exactly:**
1. **The rating's lifetime meaning is CONDITIONAL (B4).** The sheet does not print the rated temperature rise. The can's own
   rise must be measured (bench 7b.8, item 4).
2. **The ballast goes in with L4-E6's R12 12 mOhm, never on the drawn 5 mOhm (ORDER).** On 5 mOhm the widened gain margin falls
   to 8.5 dB. The draft refuses the repository's generator until R12 is in it.
3. **OPEN, a finding on the drawn front end, not created by this bank: the loop at the cans' cold ESR.** The record's loop
   corners stop at 40 mOhm, while the sheet allows 300 mOhm at -40 C after endurance.
   - As drawn, the loop holds every margin with the cans' ESR to 60 mOhm.
   - With this round's change (R12 12 mOhm and the ballast) it holds them to 80 mOhm.
   - It is settled by the cans' ESR measured at the in-use minimum, or by the generator owner's compensation check there.

**Unchanged:**
- No approved requirement, owner ruling or Layer 3 file changes, and no service is reduced.
- The compensation stays.

## The check, and what changed

| Item | What the check found | What this round does | Where |
|---|---|---|---|
| **B1** | The two sources were always added in mean square. Coincident harmonics give 2.854635 A at 204 / 816 kHz on the first round's corner | **A rule from what the rating is (SESSION):** <br>- The 2.8 A is a thermal rating (4000 h at 125 C with the ripple applied). Two harmonics heat as i squared, and their cross term beats at abs(f1 - f2). <br>- A beat slower than the can's thermal time constant heats as coherent at the worst phase. The sheet prints no constant; 1 s is taken (ASSUMPTION, 0.16 Hz). <br>- Both bands are continuous and the oscillators independent, so EXACT coincidence p fSW = q fCH is permitted, and the worst case sits on it whatever the constant is. <br>- Every ratio with p <= 20 is searched along its line every 0.5 kHz, at every VIN and VBAT, with one common time shift maximised. Higher orders are bounded by Cauchy-Schwarz. <br>- **Reproduced:** 2.7387 / 2.8547 / 2.8138 A against the check's 2.738774 / 2.854635 / 2.813686. The rule puts both coincidences inside, and that bank fails | out 5b, 5, 6 |
| **B2** | Identical intrinsic C and ESL on every can. ESR screening and copper matching do not bound them. A 6 mOhm ESR floor absent from the sheet. Lifetime spread not established. 3.586976 A at the ESL band's top | **Every can independent** over C 0.56 to 1.56 x 330 uF (+-20 % and +-30 % over endurance), ESR 0 to 300 mOhm with no floor, and ESL over the band. <br>- **No floor:** the unballasted bank is unbounded, 56.5 A on six cans and 59.2 A on eight. No count of cans and no screening fixes that. <br>- **The design:** a ballast resistor per can puts a printed floor in every branch. Its value is the smallest catalogue value that meets the rule at both outcomes over the whole box, cold limit included. <br>- **Reproduced:** 3.5869 A, a corner whose can parameters the box spans | out 5, 6, 6b |
| **B3** | fSW recentred on Equation 5's 206.05 kHz with the row's ratios, low end 180.29 kHz; the row scaled by 40 k / 40.2 k gives about 174.16 to 223.92 kHz | **The envelope** is SNVSAI1D p.6's 175 / 200 / 225 kHz at RT 40 k, scaled by Equation 5 to RT 40.2k at its 1 % (`lcsc_fill.py`: UNI-ROYAL 0603WAF4022T5E) and 100 ppm/K over 45 K (UNI-ROYAL p.6; -20 C in use to 62.1 C inside air): **171.76 / 199.04 / 227.08 kHz** (INFERRED: the row's spread kept, each end scaled). Ripple and loop re-run on it | out 5, 6, 7 |
| **B4** | The lifetime bounds took the can's rise as under the rated rise from a loss comparison with 20 mOhm at +20 C | **The lifetime is CONDITIONAL.** p.6's equation with the rated rise taken as zero gives a lower bound for a MEASURED rise dT, tabulated. The can's temperature at the worst ripple is a bench obligation | out 6b; bench 7b.8 |
| Minor, percentages | +4 / +0.5 / -0.3 % without their spread; the lost grids' explanation stated as fact | Per-spread contributions in amperes; the grids' explanation labelled INFERRED | `CORRECTIONS-DRAFT.md` section 2 |
| Minor, loop loads | The new banks' loop kept the 5.7 A load | Loads to the highest permitted current, 8.300 / 7.262 / 5.7 / 0.25 A, with the impedance bound at 166 W | out 7 |
| Minor, convergence | "Every reported maximum" was re-checked only on the drawn node | The selected bank's maxima are converged on the finer grids, with 120 harmonics and with the coincidence lines four times finer (2.621 and 2.710 A, unchanged). The claim is now narrowed to what is checked: 4b for the drawn node, 6 for the selection | out 4b, 6 |
| Minor, restart | A linear lossless estimate presented as the ring | Labelled first order, lossless, constant inductance, not saturation aware. The six cans keep it as drawn | out 8 |

## How each capacitor's current is derived (out 1 to 3, 5, 5b)

From engineering principles first:
- **Topology.** It is read from `gen_sch_a.py`'s syntax tree, and the committed netlist agrees part by part (out 1).
  - The front end injects at FE_OUT (C13 to C15), which reaches VBUS20 through R11.
  - VBUS20 carries the cans and eighteen ceramics.
  - R16 leads on to CH_ACN (C190, C191), where the charger draws.
- **Sources.** Each converter's switch current is built from its topology, then split harmonic by harmonic.
  - The front end in boost passes the inductor current during 1 - D (SNVSAI1D Equation 19, p.23); in buck it is the triangle.
  - The charger draws its inductor current during D (SLUSE66A Equation 4, p.85).
  - The model's totals agree with the equations: 6.30 against 6.30 A, and 5.73 against 5.70 A (the ripple's share).
- **Operating conditions.**
  - VIN 9 to 36 V (REQ-015).
  - fSW over B3's envelope, 171.76 to 227.08 kHz.
  - The charger over both of SLUSE66A's rows, 340 to 460 and 680 to 920 kHz (p.16; PWM_FREQ is R/W, p.43).
  - VBAT 10 to 16.8 V.
  - The current: L4-E6's highest permitted current at every VIN, B-4's fault case with U3 as the load. These are 7.2621 and
    8.2995 A, L4-E4's `band(r)[2]` run in-process, the expression L4-E6 takes as `o["hi"]`; they equal its printed 7.262 and
    8.300 A.
- **The combination.** Mean square where the harmonics do not coincide; coherent at the worst phase where they do (B1).
- **The parts.**
  - The cans are MAKER figures from the ZK sheet:
    - 330 uF +-20 %, and +-30 % after endurance;
    - ESR at most 20 mOhm at +20 C, 200 % of that after endurance;
    - at most 300 mOhm at -40 C after endurance for size G, which is the 331P's (pp.1 and 2).
  - That last figure is taken to bound the in-use minimum of -20 C. INFERRED: the hybrid's ESR rises as it cools.
  - INFERRED bands, the lost analysis's own (RECORD); no DC-bias curve or ESL figure is held:
    - the cans' ESL 1.5 to 3.5 nH;
    - the ceramics' 4 to 7 uF, ESR and ESL;
    - the copper's L11 and L16.
  - INFERRED from geometry: the ballast's ESL 0.5 to 1.5 nH.
  - The layout allowance between branches is 0.5 nH and 0.5 mOhm. It is a layout rule, and is now only one term among the
    independent ones.

**What is checked, and where.**
- **The drawn node (out 4b).** Its maxima are re-taken on source grids four to ten times finer, and those grids on finer ones
  still: the cans move by at most 0.013 A and the finer grids by 0.0000 A. 120 harmonics add at most 0.004 A.
- **The selected bank (out 6).** Its maxima are converged on the same finer grids. With 120 harmonics and with the coincidence
  lines sampled four times finer, the worst reads the same, 2.621 and 2.710 A.
- **The search's own limit.** On the second fix-up's node, enumerated in full (110,700 sets), the search finds the same maximum.

## Consistency with the history, and the reconciliation (out 4, 4b, 5)

The historical figures were checked, never targeted, and no constant was tuned. The tolerances were fixed before the check ran:
0.02 A on the dense figures, 0.0005 A on the re-review's point, half a printed digit or more on the loop.

| Historical figure | Derived | The assumption that differs | Which is right, and why | Correction (`CORRECTIONS-DRAFT.md`) |
|---|---|---|---|---|
| Drawn node, 5.7 A: 2.10 / 2.11 / 2.43 A | 2.101 / 2.113 / 2.431 on the record's grids; 2.114 / 2.125 / 2.431 converged | The source grids. The record gives counts and ends only; that its even seven-point charger rows miss the node's peaks (816 and 342 kHz) is INFERRED | Converged, on the record's rule. The rule itself is not a bound (B1, B2) | The converged figures, labelled as the record's rule |
| Drawn node, 5.0 A: 1.85 / 1.86 / 2.14 A | 1.845 / 1.855 / 2.136; 1.856 / 1.865 / 2.136 converged | The same | The same | The same |
| Second fix-up's node: 3.43 / 3.31 / 3.01 A, and 4,450 of 110,700 sets over 2.8 A | 3.427 / 3.305 / 3.008 A, 4,450 of 110,700 | None found | Agree | None |
| The re-review's point: 2.968 A | 2.9683 A | Its damping corners are not stated; one of 36 reproduces it, the least-damping corner of each band | Agree | None |
| Worst ceramic on VBUS20: 1.09 A | 1.15 on the record's grids; 1.24 A converged | The charger and VBAT grids | Converged | 1.24 A |
| Worst ceramic on FE_OUT: 1.55 A | 1.55 A | None | Agree | None |
| Loop: PM 73.1 deg, GM 15.7 dB, abs(1+T) 0.79, 0.71 to 3.6 kHz, 89 mOhm | 73.10, 15.65, 0.785, 0.712 to 3.59, 88.9 on the grid; 73.02 deg, 15.68 dB interpolated | Margins read at the grid point below each crossing | Interpolated | None needed |
| The loop's corners: cans' ESR x0.3 to x2.0 of 20 mOhm | The sheet allows 300 mOhm at -40 C after endurance | The record's corners stop at +20 C | The sheet's range | OPEN finding, a sentence drafted (out 7) |
| `r11_dep.py`, B-4 at 7.262 A: 2.69 / 2.70 / 3.11 A (and L4-E6's) | Record's rule: 2.794 / 2.788 / 3.161 A. Corrected: **3.037 / 3.022 / 3.392 A** | Per spread, in amperes: ripple not linear in the load -0.012 / -0.012 / -0.018; R11 in the network +0.107 / +0.086 / +0.073; grids +0.013 / +0.014 / +0.001; coincidences +0.243 / +0.233 / +0.231 | Derived: R11 is in that path (NETLIST); the coincidences are permitted | Superseded note, with the step table |
| `r11_dep.py` at 8.300 A: 3.07 / 3.09 / 3.55 A | Record's rule: 3.278 / 3.251 / 3.667 A. Corrected: **3.563 / 3.489 / 3.931 A** | The same | Derived | The same |
| The lost analysis's sharing (one can at a corner, siblings at s times it) | Every can independent, no ESR floor: unbounded without a ballast | The cans' match, which the sheet does not print | The sheet's range (B2) | The ballast |
| The first round's fSW band, 180.29 to 231.81 kHz | 171.76 to 227.08 kHz | The row recentred on Equation 5's prediction | The specified row carried to RT with its tolerance (B3) | The comment's band |

## The drawn bank on the corrected model (out 5)

| R11, current | Matched | 1.5:1 | 2:1 | Mean square (the record's rule) | 2.8 A |
|---|---|---|---|---|---|
| 8 mOhm, 7.262 A | 3.037 A | 3.022 A | 3.392 A | 2.794 / 2.788 / 3.161 A | NOT met |
| 7 mOhm, 8.300 A | 3.563 A | 3.489 A | 3.931 A | 3.278 / 3.251 / 3.667 A | NOT met |

- These figures use the record's sharing. With every can independent and no ESR floor, the drawn bank has no bound at all
  (56.5 A).
- The worst coincidence is fCH = 2 fSW, at 196 / 392 kHz, VIN 9 V. PWM_FREQ's power-on 400 kHz row is the one that binds.

## The decision (SESSION, engineering; out 6)

**Why a ballast, and why it is the smallest robust change.**
- The sheet prints the cans' ESR maxima only. Without a resistance floor, an unballasted can with a low ESR takes its siblings'
  share, so no count of cans is robust. Screening each can's ESR before fitting does not bound it over life (200 %) or in the
  cold (300 mOhm). So every can needs a floor, and a resistor gives one with a printed tolerance:
  - HoJLR2512, +-1 %, +-50 ppm/K, 3 W (MAKER);
  - taken at 1.38 % low on the target and high on its siblings (1 % plus 50 ppm/K over 75 K).
- With it the six drawn cans serve. Adding cans would add the same resistors and more parts, and move the soft start, the bleed
  and the restart ring.

**The rule.**
- Every can at most 2.8 A less the consistency tolerance scaled to the current: 2.7745 A at 7.262 A, 2.7709 A at 8.300 A.
- The figure is the worst of:
  - the search (target and sibling);
  - its maximum converged on the finer grids;
  - the coincidences at the worst phase, climbed;
  - the search plus the high-order bound.
- Values are taken ascending from L4-E4's catalogue reading (in stock, 10 to 100 mOhm), the 7 mOhm outcome screened first.
- The first value that meets the rule at BOTH outcomes is taken.

| Ballast | R11 7 mOhm (limit 2.7709 A) | R11 8 mOhm (limit 2.7745 A) | Outcome |
|---|---|---|---|
| 10 to 35 mOhm | screened over (35 mOhm: 2.826 A in mean square) | (33 mOhm: 2.692 A, meets) | fails 7 mOhm |
| 36 mOhm | 2.848 A with the coincidences | 2.487 A | fails 7 mOhm |
| **38 mOhm** | **2.710 A** | **2.366 A** | **meets both: taken** |

- At 8 mOhm alone, the smallest would be 33 mOhm (C2903495).
- What sets the value is the cold limit. On the +20 C box alone (ESR to 40 mOhm) the 38 mOhm bank reads 2.270 A at 7 mOhm.

## The selected bank: each can, the rating at frequency and temperature (out 6b)

| R11 | Current | The target can | Each sibling | With the coincidences | Margin to 2.8 A | Where |
|---|---|---|---|---|---|---|
| 8 mOhm | 7.262 A | 2.288 A | 1.558 A | **2.366 A** | 0.434 A | fCH = 2 fSW at 171.76 / 343.53 kHz, VIN 9 V, VBAT 10 V |
| 7 mOhm | 8.300 A | 2.621 A | 1.788 A | **2.710 A** | 0.090 A | the same |

The worst sits at the envelope's low corner, the point B3 adds.

**The ballast.** Its own loss is at most 0.28 W, against the sheet's 3 W.

**Frequency (MAKER, p.2).** Every harmonic lies at or above 171.8 kHz. The correction for 100 uF and more is 1.00 from 100 kHz
up, so the current referred to the rating is the rms itself, with no derating.

**Temperature and life: CONDITIONAL (B4).**
- The rating is the sheet's at 125 C, with no uplift taken.
- The sheet's 20 mOhm is a maximum at +20 C, not the can's ESR in service, and its rated rise is not printed, so the can's own
  rise is not established here.
- p.6: L2 = L1 x 2^((T1 - (T2 + dT)) / 10), with T1 the category temperature plus the rated rise. Taking the rated rise as zero
  bounds L2 from below for the can's MEASURED rise dT (capped at the sheet's 15 years):

| dT | At 62.1 C inside air | At 85 C (L1's temperature at the fault, a can beside it; ASSUMPTION) |
|---|---|---|
| 0 K | 131,400 h | 64,000 h |
| 10 K | 131,400 h | 32,000 h |
| 20 K | 78,249 h | 16,000 h |
| 30 K | 39,124 h | 8,000 h |

Both columns hold the fault current continuously, which is not the kit's service. The obligation is bench 7b.8, item 4.

**The ceramics.**
- They read 1.37 / 1.57 A on VBUS20 and 2.13 / 2.62 A on FE_OUT, at 8 / 7 mOhm.
- **No MLCC ripple rating is held for the 10u 50V X7R 1210, so no ceramic margin is stated.** Their loss at the band's 5 mOhm
  is at most 34 mW a part (INFERRED).

## The uncertainties that remain, and whether they block (out 6b, 7)

Each stress is taken at 7 mOhm, the binding outcome, against 2.7709 A. None flips the selection:

| Uncertainty | Range examined | Reads | What settles it |
|---|---|---|---|
| The layout's branch mismatch | twice the rule, 1.0 nH and 1.0 mOhm | 2.711 A, holds | The routed board's extracted branches (the generator owner's layout) |
| The ceramics' ESR | down to 0.5 mOhm | 2.721 A, holds | none needed |
| The cans' ESL below the INFERRED band | down to 1.0 nH | 2.736 A, holds | An impedance sweep of one mounted can, if ever wanted |
| The ballast's ESL | 0.2 to 2.5 nH | 2.704 A, holds | none needed |
| The siblings at two different corners | every pair of box corners | 2.621 A, holds | none needed |
| The rated temperature rise (B4) | not printed | lifetime CONDITIONAL | The can's temperature at the worst ripple, bench 7b.8 |
| The cans' ESR at the in-use minimum, for the LOOP | 40 to 300 mOhm | the loop holds every margin to 80 mOhm with this round's change, to 60 mOhm as drawn | The cans' ESR measured at the in-use minimum, or the generator owner's compensation check there (OPEN) |
| The ceramics' ripple rating | not held | none stated | The MLCC maker's rating for the 1210 part, or the hottest ceramic's temperature on the bench |

## The loop (out 4 and 7)

The rebuilt model is consistent with the record (above). The compensation is unchanged (Rc1 15 k, Cc1 220 nF, Cc2 680 pF).
- B3's envelope.
- The bank's corners: C 0.56 / 1.56 x 330 uF, branch R 37.5 / 78.5 mOhm (the ballast, plus the cans' ESR to 40 mOhm).
- Loads to the highest permitted current.
- Interpolated:

| R12 | Loads | PM | GM | abs(1+T) | Crossover | Zout peak / bound | Widened PM / GM |
|---|---|---|---|---|---|---|---|
| **12 mOhm (L4-E6)** | to 8.300 A | 79.0 deg | 15.6 dB | 0.83 | 0.23 to 2.11 kHz | 212 mOhm / 0.80 Ohm | 79.0 deg / 13.2 dB |
| 5 mOhm (drawn) | to 5.7 A | 72.5 | 10.8 | 0.71 | 0.56 to 5.27 kHz | 89 mOhm / 1.17 Ohm | 70.1 / **8.5** |

- **At R12 12 mOhm every row meets** PM >= 50 deg, GM >= 10 dB and abs(1+T) >= 0.5, every crossover under Fsw / 20 and
  fRHP / 3, and the impedance under its bound.
- **ORDER.** On the drawn 5 mOhm the ballast's resistance moves the bank's zero down and the widened GM falls to 8.5 dB. So the
  ballast goes in with L4-E6's R12, in the same round, and `apply_gen_sch_a_bank.py` refuses the repository's generator until
  the front end's call carries `rcs="12m"`.

**The cold limit (OPEN, a finding on the drawn front end).** Every can is taken at size G's 300 mOhm:

| Bank | R12 | GM / widened GM | The cans' ESR to which every margin holds |
|---|---|---|---|
| drawn, no ballast | 5 mOhm (as drawn) | 1.0 / -0.8 dB | 60 mOhm |
| drawn, no ballast | 12 mOhm | 5.8 / 3.9 dB | 110 mOhm |
| the ballast | 12 mOhm (this round) | 5.1 / 3.3 dB | 80 mOhm |

- The drawn circuit's own loop does not hold the sheet's cold limit; the record's corners never reached it.
- This round's change raises the ESR the loop tolerates from 60 to 80 mOhm. The ballast spends part of what R12 alone would
  gain (110 mOhm).
- Nothing here is MODELED as passing at the cold limit. The finding goes to the generator owner with its two ways to settle:
  - the cans' ESR measured at the in-use minimum (pass at 80 mOhm or less);
  - or a compensation re-check there.

This is MODELED throughout; the bench Bode row of L4-E6 is a downstream obligation.

## What else the bank moves (out 8; INFERRED, first order, reproduced from the record)

- **Nothing.** The six cans are kept, so the node's capacitance stays at 1.67 to 2.61 mF.
- **Unchanged as drawn:**
  - the soft start's own draw, 8.6 % of the entry's 4.80 A at 9 V;
  - the bleed, 0.64 to 1.17 s to release;
  - the restart ring, 14.3 A, 82 % of L1's 17.5 A typical Isat at 25 C.
- **The restart figure is first order:** lossless, constant inductance, not saturation aware. The ballasts' damping is not
  credited.
- The first round's eight- and ten-can rings (16.3 and 18.1 A) no longer arise.

## Bench row 7b.8, restated (a downstream obligation, not a blocker)

1. Record each fitted EEHZK1V331P's ESR at 100 kHz and room temperature, as data. The decision needs no screening.
2. Read one can's ESR at 100 kHz at the coldest the bench reaches toward the in-use minimum of -20 C. At 80 mOhm or less the
   loop item closes; above it, the generator owner re-checks the compensation.
3. Read each can's ripple current with a sense loop on its lead, U3 drawing as the load, at the build's highest permitted
   current:
   - at 15.1 and 36 V;
   - at 9 V at whatever current the build's limits hold there;
   - with the charger at both PWM_FREQ settings.

   **Pass:** each can at most 2.8 A less 0.03 A, the rule's margin.
4. Read each can's top temperature and each ballast's at the worst ripple. The can's rise dT goes into the lifetime table above.
5. Read the hottest ceramic's temperature.
6. L4-E6's loop Bode row on the regenerated board.

## The interaction with L4-E4 and L4-E6, and what L4-E4's release still needs

**L4-E4.**
- R11 8 mOhm stands with this bank, and so does 7 mOhm if V-A07 fails.
- Its lower resistance raises the cans' current (+0.107 / +0.086 / +0.073 A at 7.262 A on the drawn bank), a coupling
  `r11_dep.py` could not see. The ballast holds both outcomes.

**L4-E6.**
- B-1 and B-2 are unaffected.
- B-4's "OWED" closes on this derivation.
- R12 12 mOhm becomes a precondition of the ballast (ORDER).
- Its B-4 lines take the superseded note of `CORRECTIONS-DRAFT.md`.

**The drafts.**
- `apply_gen_sch_a_bank.py` gives the `lm5176()` helper a `bulk_ballast` argument, which the other stages do not use. It draws
  each of the front end's cans on its own node behind R221 to R226.
- It composes with L4-E4's R11 and R138 drafts and L4-E6's R12 draft in every order on disjoint lines, on a copy
  (`test_l4e8.py`).
- On the repository's generator it requires R12 first.

**L4-E4's release still needs:**
1. an accepted check of this record;
2. the ILIM_HIZ line on U3 (L4-E5's hardware line) drafted for `gen_sch_a.py`; it is not in this tree;
3. L4-E4's `RELEASE.md` and this folder's, each naming its accepted checks;
4. the circuit round applied together:
   - R12 before the ballast;
   - the six resistors seated, each beside its can;
   - a box regeneration;
   - the gates and evidence re-taken;
   - the loop re-verified on the regenerated board;
   - the drafted corrections applied with it;
5. bench V-A07 before 8 mOhm is committed (the bank serves either outcome);
6. the cold-ESR loop finding settled by its measurement or a compensation check.

## For board A's generator owner (OWED, nothing applied)

`apply_gen_sch_a_bank.py TARGET [--check | --write]`:
- **Mode.** `--check` by default, writing only with `--write`.
- **Refusals.** It refuses:
  - a second application;
  - a designator already in use;
  - the repository's own generator until `RELEASE.md` here reads "released: yes" and names an accepted check
    (`check: <path>`);
  - the repository's own generator until L4-E6's R12 12 mOhm is in the front end's call.
- **Testing.** It was run only on scratch copies.
- **Owed with it.** If the pipeline maps parts by value, `lcsc_fill.py` needs a line for "38mOhm 1% 2512".

**Placement is the generator owner's:** each ballast beside its can, within the layout rule.
