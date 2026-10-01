# L4-E8: board A's VBUS20 bulk bank re-sized (MESHSAT-1357, 1 October 2026)

Prototype design, desk arithmetic: nothing is bought, built, powered or measured, and no generator, registry, rendered page or
record of L4-E4 to L4-E7 is edited. This closes finding B-4 of `../l4e/L4-ENERGY-ARCHITECTURE.md` as L4-E6 left it ("the bank is
to be re-sized by the generator owner"). Every figure is printed, with its basis, by `ripple_dense.py` (`ripple_dense.out`,
"out N" below). Labels: MAKER, NETLIST, GENERATOR, RECORD (the generator's own record: `gen_sch_a.py`'s comments and
`../r4a/r4-decisions.md`), INFERRED, ASSUMPTION, SESSION (a choice this record makes), MODELED, INCONCLUSIVE.

**Status.** B-4 closes at R11 8 mOhm with **two more EEHZK1V331P: eight cans, the ceramics as drawn** (eighteen on VBUS20, three
on FE_OUT). The worst can reads 2.578 / 2.478 / 2.739 A at the matched / 1.5:1 / 2:1 spreads against 2.8 A.
- **The sharing basis (SESSION).** Every can's ESR is read and held within 2:1 before fitting. Every can's branch is laid within
  0.5 nH and 0.5 mOhm of every other's: a layout rule.
- **The lumped node.** On an ideally symmetric layout one more can would serve (2.767 A); the layout basis is what takes the
  second.
- **If bench V-A07 fails (R11 7 mOhm).** The bank is ten cans (2.635 / 2.473 / 2.681 A). Its restart ring through L1 then
  exceeds L1's typical Isat, so that path also owes the ring's own remedy.
- **Unchanged.** No approved requirement, owner ruling or Layer 3 file changes, no service is reduced, and the compensation
  stays.

## How each capacitor's current is derived (out 1 to 3)

The derivation, from engineering principles first:
- **Topology.** Read from `gen_sch_a.py`'s syntax tree; the committed netlist agrees part by part (out 1). The front end
  injects at FE_OUT (C13 to C15), which reaches VBUS20 through R11. VBUS20 carries the cans and eighteen ceramics; R16 leads on
  to CH_ACN (C190, C191), where the charger draws.
- **Sources.** Each converter's switch current is built from its topology and then split harmonic by harmonic. The front end
  in boost passes the inductor current during 1 - D, the waveform of SNVSAI1D Equation 19 (p.23); in buck it is the triangle.
  The charger draws its inductor current during D, the waveform of SLUSE66A Equation 4 (p.85). The ripple of each comes from L,
  fSW and the duty. The model's own totals agree with the equations: 6.30 against 6.30 A, and 5.73 against 5.70 A (the
  ripple's share).
- **Operating conditions.**
  - VIN 9 to 36 V (REQ-015).
  - fSW 180.3 to 231.8 kHz: p.6's row carried to RT 40.2 k by Equation 5.
  - The charger: both of SLUSE66A's rows, 340 to 460 and 680 to 920 kHz (p.16). PWM_FREQ is R/W (p.43), so a host can write
    800 kHz.
  - VBAT 10 to 16.8 V.
  - The current: L4-E6's highest permitted current at every VIN, B-4's fault case with U3 as the load. These are 7.2621 A and
    8.2995 A, L4-E4's `band(r)[2]` run in-process, which is the expression L4-E6 takes as `o["hi"]`. They equal its printed
    7.262 and 8.300 A.
- **Parts.**
  - The cans are 330 uF +-20 %, ESR at most 20 mOhm, 200 % of it after endurance (MAKER, ZK sheet pp.1 and 2).
  - The ceramics' 4 to 7 uF effective C, the cans' ESL of 1.5 to 3.5 nH, the ceramics' ESR and ESL, and the copper's L11 and
    L16 are INFERRED bands: the lost analysis's own (RECORD). No DC-bias curve or ESL figure is held.
  - The worst case puts the source current at every VIN; the two sources add in mean square at each one's own worst corner,
    because they are not synchronised.
- **Its acceptance is convergence (out 4b).**
  - Every reported maximum is re-taken on source grids four to ten times finer, then climbed again there. The cans move by at
    most 0.013 A.
  - The finer grids are checked against finer ones still, and move by 0.0000 A.
  - 120 harmonics add at most 0.004 A.
- **The search is coarsened (SESSION, as the task requires on this host).**
  - The method: a bounded coarse grid, then climbs on the dense grid, then the dense slice. It is stated in out 3.
  - The check: on the second fix-up's node, enumerated in full (110,700 sets), the search finds the same maximum.

## Consistency with the history, and the reconciliation (out 4, 4b, 5)

The historical figures were checked, never targeted; no constant was tuned. The tolerances (0.02 A on the dense figures, 0.0005 A
on the re-review's point, half a printed digit or more on the loop) were fixed before the check ran. Draft corrections for
`gen_sch_a.py`'s comment and for `r11_dep.py`'s carried figures are in `CORRECTIONS-DRAFT.md`.

| Historical figure | Derived | The assumption that differs | Which is right, and why | Correction |
|---|---|---|---|---|
| Drawn node, 5.7 A: 2.10 / 2.11 / 2.43 A | 2.101 / 2.113 / 2.431 on the record's grids; **2.114 / 2.125 / 2.431 converged** | The source frequency grids: seven charger points a row and eleven fSW points fall between the node's resonance peaks (the converged worst sits at 816 kHz) | Converged: the frequencies are continuous bands, and the finer grids have themselves converged | Add the converged figures |
| Drawn node, 5.0 A: 1.85 / 1.86 / 2.14 A | 1.845 / 1.855 / 2.136; **1.856 / 1.865 / 2.136 converged** | The same grids; the record sits between the two, so its own grid points differed from the even ones assumed here | Converged | Add |
| Second fix-up's node: 3.43 / 3.31 / 3.01 A, and 4,450 of 110,700 sets over 2.8 A | 3.427 / 3.305 / 3.008 A, **4,450 of 110,700** | None found | Agree | None |
| The re-review's point: 2.968 A | 2.9683 A | Its damping corners are not stated; one of 36 reproduces it, the least-damping corner of each band | Agree | None |
| Worst ceramic on VBUS20: 1.09 A | 1.15 A on the record's grids; **1.24 A converged** | The charger and VBAT grids | Converged | 1.24 A |
| Worst ceramic on FE_OUT: 1.55 A | 1.55 A | None | Agree | None |
| Loop: PM 73.1 deg, GM 15.7 dB, abs(1+T) 0.79, 0.71 to 3.6 kHz, 89 mOhm | 73.10, 15.65, 0.785, 0.712 to 3.59, 88.9 on the grid; **73.02 deg, 15.68 dB interpolated** | Margins read at the grid point below each crossing | Interpolated | None needed |
| r11_dep.py, B-4 at 7.262 A: 2.69 / 2.70 / 3.11 A (and L4-E6's) | **2.794 / 2.788 / 3.161 A** | A linear scaling over a 10 mOhm network. R11 sits in the network: lower, it isolates FE_OUT from VBUS20 less (+4 %); also the grids (+0.5 %), and the ripple, which does not scale (-0.3 %) | Derived: R11 is in that path (NETLIST) | Superseded note |
| r11_dep.py at 8.300 A: 3.07 / 3.09 / 3.55 A | **3.278 / 3.251 / 3.667 A** | The same | Derived | The same |
| The lost analysis's lumped node (every can at one point) | Each can has its own branch | The layout | The layout basis below | The bank and the layout rule |

## The drawn bank at the highest permitted currents (out 5)

Converged figures, matched / 1.5:1 / 2:1:
- **R11 8 mOhm, 7.262 A:** 2.794 / 2.788 / **3.161 A**, so B-4 is NOT met at 2:1.
- **R11 7 mOhm, 8.300 A:** 3.278 / 3.251 / **3.667 A**, NOT met at any spread.

Where the worst sits:
- Every worst can sits at VIN 9 V. L4-E6's R12 (12 mOhm, drafted) would hold the output there to 4.57 A. No credit is taken for
  that; with VIN above L4-E6's boundaries only, the chosen bank reads 2.250 / 1.976 A (out 6).
- The 2:1 worst is on the 400 kHz row, PWM_FREQ's power-on value.

## The decision (SESSION, engineering; out 6)

**The sharing basis.** The sheet prints the ESR's maximum and its endurance limit only, with no minimum, and asks for "the same
part number" and no "partiality of cable impedances" (p.7). Two things decide how the cans share:
- **The ESR spread is kept at B-4's 2:1 and made a build property.** Each can's ESR is read at 100 kHz before fitting and the
  fitted set held within 2:1. A can that ages or runs hotter rises in ESR and takes less current, so the spread corrects itself
  in service. Uncontrolled, the record's 3.3:1 extreme reads 3.559 A.
- **The branch inductance is the larger effect, and it does not correct itself.** Each can's branch must lie within 0.5 nH and
  0.5 mOhm of every other's.
  - The basis: a 10 mm VBUS20 pour 0.2 mm over its plane is about 25 pH/mm (mu0 h / w), so 0.5 nH is a 20 mm path difference;
    0.5 mOhm is two squares of 2 oz copper.
  - It is held by a symmetric placement about one VBUS20 entry (the record's O-01). It is verified on the routed board's
    extracted branches.

**Both are stacked on one can**, the one with the lowest ESR and the shortest branch.

**The rule.**
- Every can at most 2.8 A less the consistency tolerance scaled to the current: 2.7745 A at 7.262 A, at every spread.
- The figure is the larger of a full search and its converged maximum. At the binding 2:1 spread the search runs on decision
  grids: the charger every 5 kHz, fSW every 2.5 kHz, VBAT every 0.2 V.
- Candidates are taken in groups by the change they make: added cans first, then added ceramics. A can-count is opened only
  after the same count with twelve more ceramics failed.

| Change (cans, ceramics), 8 mOhm, layout basis | Banks | At 2:1 (screen); decided where screened under the limit | Outcome |
|---|---|---|---|
| 0, +12 | six cans, 30 + 3 or 27 + 6 | 3.199 / 3.150 A | Ceramics alone cannot close B-4 |
| +1, +12 | seven cans, 30 + 3 or 27 + 6 | 2.846 / 2.791 A | One can cannot, on this basis |
| **+2, 0** | **eight cans, 18 + 3**: 2.578 / 2.478 / 2.739 A; eight cans, 15 + 6: 2.784 / 2.608 / 2.816 A | | **18 + 3 taken** |

**Chosen: eight EEHZK1V331P, C236 and C237 added, no ceramic change.**

| Spread | Can with the lowest ESR and the shortest branch | Each sibling | Margin to 2.8 A (converged) | Largest loss in a can, of the rated condition's |
|---|---|---|---|---|
| matched | 2.578 A | 2.265 A | 0.222 A | 75 mW, 48 % |
| 1.5:1 | 2.477 A | 1.896 A | 0.322 A | 97 mW, 62 % |
| 2:1 | 2.738 A | 1.666 A | **0.061 A** | 115 mW, 73 % |

**The rating at frequency and temperature (MAKER, the ZK sheet).**
- **Frequency.** Every harmonic of both sources lies at or above 180.3 kHz. The sheet's correction for 100 uF and more is 1.00
  from 100 kHz up (p.2), so the current referred to the rating is the rms itself.
- **Temperature.** The 2.8 A is the rating at 125 C, the category's top; no uplift is printed for a cooler can, so none is
  taken.
- **Self-heating.** Each can's loss stays at or below 73 % of the rated condition's (2.8 A squared times 20 mOhm, 157 mW), so
  its rise stays below the rated rise (INFERRED: the same can and the same thermal path).
- **Life (p.6's equation).** Expected life is at least 4000 x 2^((125 - T) / 10) h:
  - 15 years (the sheet's cap) at the worst inside air, 62.1 C (`pcb_envelope.yaml`);
  - 64,000 h at 85 C, L1's own temperature at the fault (ASSUMPTION: a can beside it);
  - both with the fault current held continuously, which is not the kit's service.

**The worst ceramic (matched, converged).**
- 1.60 A on VBUS20 and 2.11 A on FE_OUT, unchanged by the two cans.
- **No MLCC ripple rating is held for the 10u 50V X7R 1210, so no ceramic margin is stated.** Their loss at the band's 5 mOhm is
  13 and 22 mW a part (INFERRED).

**The 7 mOhm bank (only if V-A07 fails, 8.300 A, limit 2.7709 A).**
- The 8 mOhm bank reads 3.095 A at 2:1 there: not met.
- The rule's groups give **ten cans, 18 + 3** (C236 to C239): 2.635 / 2.473 / 2.681 A. This contingency was searched on the
  record's grids and converged.
- Nine cans with six more ceramics read 2.792 and 2.849 A.

## The uncertainties that remain, and whether they block

None blocks the 8 mOhm selection. Each is named with its range, what it would flip and what settles it.

| Uncertainty | Range examined | Selection it flips | What settles it |
|---|---|---|---|
| The layout's branch mismatch, should the routed board miss the rule | twice the rule, 1.0 nH and 1.0 mOhm | Eight cans read 2.813 / 2.881 A: fails. **Nine cans hold the rule there** (2.622 / 2.503 / 2.652 A), but ring L1 at 17.2 A, 99 % of its typical Isat | The routed board's extracted branch impedances (the generator owner's layout); bench 7b.8 |
| The cans' ESL below the INFERRED 1.5 nH, and the ceramics' C below 4 uF | to 1.0 nH and 3.0 uF | Eight cans read 2.743 / 2.870 A (at 1.0 nH, 3.0 uF): fails | An impedance sweep of one mounted EEHZK1V331P (its self-resonance gives the ESL), and the 10u 50V X7R 1210's C at 20 V; or 7b.8 |
| An ESR spread above 2:1 | the record's 3.3:1 | 3.559 A | Removed by the build rule: each can read before fitting |
| L1's Isat at temperature against the restart ring | the ring 16.3 A for eight cans (93 % of 17.5 A at 25 C) | not the bank; whether the restart ring saturates L1 | L4-E6's C-5 sweep, carried to 16.3 A |
| The 7 mOhm path's restart ring | ten cans ring L1 at 18.1 A, 104 % of its typical Isat | the 7 mOhm bank needs the ring's remedy as well (the guard's release level, or L4-E6's candidate (b), the XAL1510) | Owed with the 7 mOhm path, only if V-A07 fails |

**The robust choice.**
- No bank meets both the 1 nH stress and the restart ring under L1's typical Isat.
- So the layout rule is the design basis, and nine cans is the escalation if the routed board cannot hold it. Nine cans brings
  the ring with it.

## The loop (out 4 and 7)

The rebuilt model is consistent with the record (above). With the compensation unchanged (Rc1 15 k, Cc1 220 nF, Cc2 680 pF),
interpolated:

| Bank, R12 | PM | GM | abs(1+T) | Crossover | Widened PM / GM |
|---|---|---|---|---|---|
| drawn, 5 mOhm | 73.0 deg | 15.7 dB | 0.79 | 0.71 to 3.59 kHz | 72.8 deg / 14.0 dB |
| eight cans, 5 mOhm | 76.5 | 18.1 | 0.83 | 0.54 to 2.73 kHz | 76.5 / 16.3 |
| eight cans, 12 mOhm (L4-E6) | 77.4 | 25.7 | 0.93 | 0.23 to 1.14 kHz | 77.4 / 23.9 |
| ten cans, 12 mOhm | 75.1 | 27.5 | 0.94 | 0.19 to 0.92 kHz | 75.0 / 25.8 |

- Every row keeps PM >= 50 deg, GM >= 10 dB and abs(1+T) >= 0.5, with every crossover under Fsw / 20 and fRHP / 3.
- The output impedance peak, at most 213 mOhm, stays under its 1.17 Ohm bound.
- **The margins do not require a compensation change.**
- This is MODELED; the bench Bode row of L4-E6 is a downstream obligation.

## What else the bank's capacitance moves (out 8; INFERRED, first order, each reproduced on the drawn node first)

| Node | Largest | Soft-start draw at 9 V | Bleed to release | Restart ring in L1 |
|---|---|---|---|---|
| drawn, six cans | 2.61 mF | 8.6 % of the entry's 4.80 A | 0.64 to 1.17 s | 14.3 A (82 % of 17.5 A) |
| **eight cans** | 3.40 mF | 10.5 % | 0.84 to 1.53 s | 16.3 A (93 %) |
| nine cans (the escalation) | 3.79 mF | 11.4 % | 0.94 to 1.71 s | 17.2 A (99 %) |
| ten cans (7 mOhm) | 4.19 mF | 12.3 % | 1.04 to 1.89 s | 18.1 A (104 %) |

- **The soft start.** The ramp's own draw grows by two points. The start-up totals with the charger converting are re-taken
  under L4-E5's FW-A16 and its ILIM_HIZ line (bench V-A09).
- **The bleed.** A restart waits about 0.35 s longer.

## Bench row 7b.8, restated (a downstream obligation, not a blocker)

1. Before fitting, read each EEHZK1V331P's ESR at 100 kHz and fit a set within 2:1.
2. After layout, check each can's extracted branch against the 0.5 nH and 0.5 mOhm rule.
3. Read each can's ripple current with a sense loop on its lead, U3 drawing as the load, at the build's highest permitted
   current:
   - at 15.1 and 36 V;
   - at 9 V at whatever current the build's limits hold there;
   - with the charger at both PWM_FREQ settings.
4. Read the hottest ceramic's temperature.

**Pass:** each can at most 2.8 A less 0.03 A. That margin is the rule's.

## The interaction with L4-E4 and L4-E6, and what L4-E4's release still needs

**L4-E4.**
- R11 8 mOhm stands with the eight-can bank.
- Its own lower resistance raises the cans' current by about 4 %, a coupling r11_dep.py could not see.

**L4-E6.**
- B-1 and B-2 are unaffected.
- B-4's "OWED" closes on this derivation.
- R12 12 mOhm lowers the 9 V fault current, which the decision does not need.
- The loop at R12 12 mOhm is MODELED above.

**The drafts.** `apply_gen_sch_a_bank.py` edits only the front end's `bulk=` line. It composes with L4-E4's R11 and R138 drafts
and L4-E6's R12 draft in every order on disjoint lines (`test_l4e8.py`).

**L4-E4's release still needs:**
1. an accepted check of this record;
2. the ILIM_HIZ line on U3 (L4-E5's hardware line) drafted for `gen_sch_a.py`; it is not in this tree;
3. L4-E4's `RELEASE.md` and this folder's, each naming its accepted checks;
4. the circuit round applied together, with the bank seated symmetrically and its branches extracted against the layout rule,
   a box regeneration, the gates and evidence re-taken, the loop re-verified on the regenerated board, and the drafted
   corrections applied with it;
5. bench V-A07 before 8 mOhm is committed, or the 7 mOhm path with its ring remedy.

## For board A's generator owner (OWED, nothing applied)

`apply_gen_sch_a_bank.py --bank 8` (default), or `--bank 7`:
- **Mode.** `--check` by default, writing only with `--write`.
- **Refusals.** It refuses a second application and a designator already in use. It refuses the repository's own generator
  until `RELEASE.md` here reads "released: yes" and names an accepted check (`check: <path>`).
- **Testing.** It was run only on scratch copies.

**Placement is the generator owner's,** under the layout rule above.
