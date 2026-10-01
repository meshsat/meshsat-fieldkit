# Draft corrections from L4-E8 (MESHSAT-1357, 1 October 2026): DRAFTS ONLY, nothing here is applied

Prototype design, desk arithmetic. These are proposed texts for the owners of `v2/ecad/tools/gen_sch_a.py` (board A's generator)
and `v2/docs/records/r11dep/r11_dep.py`. Neither file is edited by L4-E8. Every figure is `ripple_dense.out`'s; the reasons are
`L4E8-BANK.md`'s reconciliation table.

Applying either changes a pinned file. After that, `r11_dep.py`, the L4-E4 to L4-E6 records and `ripple_dense.py` refuse by
design. So the corrections belong in the same circuit round as the bank itself, with a regeneration.

## 1. `gen_sch_a.py`, the front end's output node comment (the third fix-up, about lines 716 to 721)

**Keep the existing sentences.** They are the record of 26 September 2026. `r11_dep.py` parses them with a pattern, so they must
stay word for word until it is retired.

**Add after "...that is 12 mW a part (INFERRED).":**

> L4-E8 (1 October 2026, v2/docs/records/l4e8): the same node and bands derived again, with the source frequencies converged.
> The charger is taken every 2 kHz, fSW every 0.5 kHz and VBAT every 0.05 V; the seven-point charger rows of the figures above
> fall between the node's resonance peaks. On those grids the worst can reads:
> - 2.114 / 2.125 / 2.431 A at 5.7 A, matched / 1.5:1 / 2:1;
> - 1.856 / 1.865 / 2.136 A at the declared 5 A.
>
> The worst VBUS20 ceramic reads 1.24 A, not 1.09 A. FE_OUT's stays at 1.55 A. No MLCC ripple rating is held.

**Replace "SIX EEHZK1V331P" in the call's comment when the bank draft is applied.** The applied line carries its own L4-E8
comment (`apply_gen_sch_a_bank.py`).

**No loop correction is needed.** The loop sentence ("PM 73.1 degrees, GM 15.7 dB ...") is the grid's figure. The derivation
interpolated at each crossing reads 73.02 deg and 15.68 dB.

## 2. `r11_dep.py`, the bank lines it carries (section 4's "VBUS20's bank, the worst can, scaled in proportion to the front end's current")

**What it does.** It scales the third fix-up's figures linearly with the current: the larger of the 5.7 A and 5.0 A points
per ampere, 0.370 / 0.372 / 0.428 A per A. L4-E6 takes these as B-4's figures: 2.69 / 2.70 / 3.11 A at 7.262 A, and 3.07 /
3.09 / 3.55 A at 8.300 A.

**Proposed note under that line:**

> SUPERSEDED for B-4 by v2/docs/records/l4e8/ripple_dense.out section 5. That record derives the node at each R11 with R11 in
> the network. At 7.262 A (R11 8 mOhm) the drawn bank reads 2.794 / 2.788 / 3.161 A (matched / 1.5:1 / 2:1). At 8.300 A (7 mOhm)
> it reads 3.278 / 3.251 / 3.667 A. The linear scaling held the 10 mOhm network: a lower R11 isolates FE_OUT from VBUS20 less
> and puts more of the front end's switch current into the cans (+4 % at 8 mOhm). It also took the record's under-sampled
> source grids (+0.5 %) and scaled the ripple term with the current, which it does not do (-0.3 %).

**The same note applies to L4-E6's B-4 lines** (`l4e6_fault_handling.out` section 6 and `L4E6-FAULT-HANDLING.md`, "The
closures"). Those are L4-E6's files, for the coordinator to re-point. Their decision is unchanged: B-4 is still not met on the
drawn bank, and by more than they read.
