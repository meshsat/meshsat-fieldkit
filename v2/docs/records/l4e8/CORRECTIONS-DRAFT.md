# Draft corrections from L4-E8 (MESHSAT-1357, 1 October 2026, the fix rounds): DRAFTS ONLY, nothing here is applied

Prototype design, desk arithmetic. These are proposed texts for the owners of `v2/ecad/tools/gen_sch_a.py` (board A's generator)
and `v2/docs/records/r11dep/r11_dep.py`. Neither file is edited by L4-E8. Every figure is `ripple_dense.out`'s ("out N"); the
reasons are `L4E8-BANK.md`'s reconciliation table.

Applying either changes a pinned file. After that, `r11_dep.py`, the L4-E4 to L4-E6 records and `ripple_dense.py` refuse by
design. So the corrections belong in the same circuit round as the bank itself, with a regeneration.

**What the figures rest on.** Two kinds of figure appear below, and each is labelled:
- **The record's rule.** One can at a corner's ESR, its siblings at s times it, the two converters added in mean square.
  These figures are a refinement of the record's own, CONDITIONAL on that rule. The collaborator's check showed the rule is not
  a bound: B1, coincident harmonics; B2, cans that do not match.
- **The corrected model.** The coincidences at the worst phase (B1, out 5b) and B3's frequency envelope (out 5). Under B2's
  independent cans with no ESR floor, no count of unballasted cans has a bounded current (out 5), so the record's sharing
  figures cannot be made into a bound by correcting them. They are kept only as the record's own description.
- **The bound.** The chosen bank rests on section 6's conservative bound over arbitrary independent branches, not on any of
  the figures above.

## 1. `gen_sch_a.py`, the front end's output node comment (the third fix-up, about lines 716 to 721)

**Keep the existing sentences.** They are the record of 26 September 2026. `r11_dep.py` parses them with a pattern, so they must
stay word for word until it is retired.

**Add after "...that is 12 mW a part (INFERRED).":**

> L4-E8 (1 October 2026, v2/docs/records/l4e8): the same node and bands derived again.
>
> On the record's rule (one can at a corner, its siblings at s times its ESR, mean square), with the source frequencies
> converged (the charger every 2 kHz, fSW every 0.5 kHz, VBAT every 0.05 V), the worst can reads:
> - 2.114 / 2.125 / 2.431 A at 5.7 A, matched / 1.5:1 / 2:1;
> - 1.856 / 1.865 / 2.136 A at the declared 5 A.
>
> The worst VBUS20 ceramic reads 1.24 A, not 1.09 A; FE_OUT's stays at 1.55 A. No MLCC ripple rating is held.
>
> That rule is not a bound:
> - The two converters are not synchronised, so exact coincidences p fSW = q fCH are permitted. Coincident harmonics heat a
>   can at their worst relative phase (out 5b).
> - The ZK sheet prints the ESR's maxima only. With every can independent and no ESR floor, an unballasted can's current has no
>   bound (out 5).
> - The front end's frequency is SNVSAI1D p.6's row carried to RT with its tolerance: 171.76 to 227.08 kHz, not 180.3 to
>   231.8 kHz.
>
> The bank is therefore six EEHZK1V331P, each behind a 45 mOhm ballast (R221 to R226), with Cc2 at 3.3 nF and L4-E6's R12 at
> 12 mOhm (L4E8-BANK.md). A conservative bound over arbitrary independent cans and passives holds every can under 2.8 A at
> both R11 outcomes there.

**Replace "SIX EEHZK1V331P" in the call's comment when the bank draft is applied.** The applied line carries its own L4-E8
comment (`apply_gen_sch_a_bank.py`).

**No loop correction is needed for the drawn circuit's figures.** The loop sentence ("PM 73.1 degrees, GM 15.7 dB ...") is the
grid's figure; interpolated at each crossing it reads 73.02 deg and 15.68 dB (out 4).

**A loop sentence to add with the Cc2 change** (out 7). Proposed sentence:

> L4-E8: the loop's corners stopped at the cans' ESR after endurance at +20 C (40 mOhm). The ZK sheet allows 300 mOhm after
> endurance at -40 C (size G), which the record takes down to -20 C. With the drawn Cc2 (680 pF) the gain margin falls under
> 10 dB at that end. With Cc2 at 3.3 nF, R12 at 12 mOhm and the 45 mOhm ballasts, every margin holds over the cans' whole ESR
> envelope (0 to 300 mOhm), Cc2's tolerance and mixed banks (MODELED; the bench Bode row is owed).

## 2. `r11_dep.py`, the bank lines it carries (section 4's "VBUS20's bank, the worst can, scaled in proportion to the front end's current")

**What it does.** It scales the third fix-up's figures linearly with the current: the larger of the 5.7 A and 5.0 A points
per ampere, 0.370 / 0.372 / 0.428 A per A. L4-E6 takes these as B-4's figures: 2.69 / 2.70 / 3.11 A at 7.262 A, and 3.07 /
3.09 / 3.55 A at 8.300 A.

**Proposed note under that line:**

> SUPERSEDED for B-4 by v2/docs/records/l4e8/ripple_dense.out section 5. On the drawn bank at R11 8 mOhm and 7.262 A, the
> record's rule reads 2.794 / 2.788 / 3.161 A (matched / 1.5:1 / 2:1). With the coincidences at the worst phase it reads
> 3.037 / 3.022 / 3.392 A. At R11 7 mOhm and 8.300 A the two read 3.278 / 3.251 / 3.667 A and 3.563 / 3.489 / 3.931 A.
> With the cans independent and no ESR floor, no unballasted bank is bounded at all.

**The difference, step by step, per spread** (out 5, R11 8 mOhm, 7.262 A, the record's sharing). Each row is the change from
the row above it, in amperes:

| Step | Matched | 1.5:1 | 2:1 | Basis of the reason |
|---|---|---|---|---|
| `r11_dep.py`'s linear scaling | 2.687 | 2.701 | 3.108 | (the starting figures) |
| The record's network, re-derived at 7.262 A (L2 3.3 uH, R11 10 mOhm, the record's grids) | -0.012 | -0.012 | -0.018 | MODELED: the inductor ripple does not grow with the load current, so the linear scaling overstates its share |
| L2 4.7 uH, as drawn since S-117 | -0.001 | -0.000 | -0.004 | NETLIST |
| R11 8 mOhm in the network | +0.107 | +0.086 | +0.073 | NETLIST: R11 sits between FE_OUT and VBUS20. Lower, it isolates the front end's switch current from the cans less |
| The source grids converged | +0.013 | +0.014 | +0.001 | See the note below the table |
| B3's frequency envelope | +0.000 | +0.000 | +0.000 | MAKER row, Equation 5, RT's tolerance and TCR. The worst sits inside both bands |
| The coincidences at the worst phase (B1) | +0.243 | +0.233 | +0.231 | SESSION rule from the rating's thermal meaning (out 5b) |
| **The corrected figure** | **3.037** | **3.022** | **3.392** | |

**The grids, and what is inference.** The lost script's grids are not held. The record gives the counts and the ends only:
seven charger points a row, eleven fSW points and ten VBAT points. Even spacing is an ASSUMPTION of this rebuild. That those
grids under-sample the node's resonance peaks is INFERRED, not read from the lost script: the converged maxima sit at 816 and
342 kHz, which even seven-point rows over 680 to 920 and 340 to 460 kHz do not contain.

**The same note applies to L4-E6's B-4 lines** (`l4e6_fault_handling.out` section 6 and `L4E6-FAULT-HANDLING.md`, "The
closures"). Those are L4-E6's files, for the coordinator to re-point. Their decision is unchanged: B-4 is not met on the drawn
bank, and by more than they read. It is met by the ballasted bank of `L4E8-BANK.md`, on a conservative bound.
