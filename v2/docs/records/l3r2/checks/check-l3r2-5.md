accepted: yes

# CHECK-5: narrow confirmation of the Layer 3 handover L3-R2 (item C27), the six owner decisions pending

MESHSAT-1357, 30 September 2026, about 06:20 CEST. **An AI check, not a qualified review.** The checker wrote none of
L3-R2.

**Scope.**
* Branch `fnd/l3r2` at `028531e4` (confirmed), one commit on `9493847c`.
* Only `git diff 9493847c..028531e4`, judged against CHECK-4's blocking item B1, its minors 1 to 7 and its note on S-127.

**Verdict.** The blocking item is closed. S-127 is closed with the right authority. All seven minors are answered, and
every gate passes on the tip, on the tip merged with main, and on set 16 by the README's run order.

**Accepted for the handover as prepared, with the six decisions pending.** Four small minors remain, listed below. None
changes a decision row or a gate. Two of them are renderer sentences that CHECK-4 should have caught and did not.

## What was run (throwaway shared clone at `028531e4`, `int16-evidence-e5322674.tar` installed; removed afterwards)

**At the tip:**
* `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings.
* `rules_render.py --requirements --check`: current.
* `render_l3r2.py --check`: 3 pages, 0 out of date.
* `dryrun.py`: byte identical.
* `run.py test_requirements test_l3r2`: **91 passed, 0 failed, 0 skipped**.

**Merged with main (`6cd331ef`):**
* The merge is clean. `rules_lib` reads 0 errors and `rules_render --check` is current.
* `REQUIREMENTS-L3-R2.md` goes out of date by its header line only (the registry's sha256/16). After a re-render
  `--check` reads 0 out of date.
* `dryrun.py` byte identical; 91 of 91 tests pass.

**Set 16 (`fnd/int17` `72b91c91`), the README's run order as written:**
* Every apply script ran, including `apply_l3r2_s127.py` and `apply_layer_status_l3_r3d.py`, with validator 0 errors.
* `rules_lib` 0 errors; `render_l3r2.py --check` 0 out of date; 91 of 91 tests pass.
* `dryrun.out` equals the branch's. L3-RECONCILIATION.md and OWNER-DECISIONS-L3.md equal the branch's, and
  REQUIREMENTS-L3-R2.md differs only in the registry sha.
* The `records/l3plane`, `records/r11dep` and vendor files the run order checks out equal set 16's.

**Text rules on the 365 added lines:**
* 0 lines with U+2013 or U+2014; no host names or paths.
* CONOPS.md, PRODUCT-BRIEF.md and `v2/release/` are unchanged against `9493847c` and against main.

## CHECK-4 B1, the blocking item: closed

**Row L3-OD6's recommendation** is now the weather basis only: "the average-day benchmark, stated as a design benchmark
and not a weather promise".
* Its limitation stands beside it (17.5 to 22.0 percent of the past September windows at WE).
* Its reason is "capacity and fit, not the energy balance": 128 to 228 cells against the 84 of the largest store, in the
  fixed case.
* The as-drawn sentence is gone.
* "The array build is not recommended; it is the owner's, coupled with row L3-OD2."

**The owner test names REQ-002, REQ-067 and REQ-068 beside REQ-072**, with the consequence: "the WAB build leaves only
the QMX-out lid carrying M1, so HF leaves the kit ..., while the TYP build keeps both the 4S14P and 4S15P lids open". The
recommendation adds "unless `qmx-outside` finds a place".

**Row L3-OD2 states the coupling both ways**, in its owner test ("coupled with row L3-OD6's build (WAB: the QMX-out lid
only; TYP: either lid)") and in its recommendation ("with the WAB build only the QMX out (or outside, with a place)
carries M1's benchmark, so the tablet out is then an open conflict; with the TYP build both lids carry it").

**The pairing test**, `t_l3r2_the_wab_build_with_the_tablet_out_is_never_coherent_on_the_checked_table`, passes. It
asserts the following, and the script chains run on copies of the registry.

| Build | Lid | Coherent? | Conflict |
|---|---|---|---|
| WAB | tablet-out | incoherent | recorded |
| WAB | qmx-out | coherent | none |
| WAB | qmx-outside | coherent | none |
| TYP | tablet-out | coherent | none |
| TYP | qmx-out | coherent | none |
| TYP | both-kept | incoherent | recorded |

**My own pairings**, on copies, with the tree's filled and verified table (no fixture):

| Chain | Result |
|---|---|
| mean day WAB, then approve, then qmx-outside | written; `coherent()` ([], True) |
| approve, then tablet-out, then mean day WAB (row 2 before row 6) | CFL-019 recorded by `od_l3_6.py`; `coherent()` false ("tablet-out does not carry ... mean-day-WAB") |
| coverage 50 TYP, then approve, then qmx-out | CFL-019 recorded at row 6; no second conflict at row 2; incoherent |
| mean day TYP, then approve, then both-kept | CFL-019 recorded; incoherent |

## S-127: closed with the right authority

**`apply_l3r2_s127.py`:**
* It re-verifies both bindings (`basis_state` on `energy_basis` and `power_path_check`, byte identical to `cd8720a1`).
* It requires CHECK-5 as the named check and requires commit `9493847c` to exist.
* It reads the four cases from `three_cases.out` by exact keys.
* It changes only S-127 (moved to closed) and REQ-072 (waits, evidence, bindings); other changes refuse.
* The result validates.

**The closing evidence's shas** match the files in the tree:

| File | sha256/16 |
|---|---|
| ENERGY-BASIS.md | `7bbca138a02bd32f` |
| three_cases.out | `8119987a20fad08c` |
| CHECK-5.md | `bf3aace0457d19ee` |

**REQ-072:**
* It waits only on S-53 and M-02.
* Its status is DEFINED and its verdict stays FAIL.
* Its bindings add the three files at those shas.
* Its new evidence entry is true against `three_cases.out` 2:
  * as drawn: 326.6 to 522.4 Wh unserved at NOM and 422.1 to 616.7 Wh at WE;
  * derated at 4.00 A: 369.9 to 566.0 Wh;
  * resistor-only lower bound: 622.1 to 1079.9 Wh;
  * corrected NOM TYP: 93.7 Wh (4S14P) and 125.2 Wh (4S15P).

**L3-C31** renders CLOSED, and L3-C45 CLOSED.

**The authority is right.** S-127 is a SESSION item, and its closing condition (the basis filed with an accepted check,
REQ-072 re-read on it) is one the session verifies mechanically. No owner answer bears on it. The closure changes no
statement or acceptance.

## CHECK-4 minors 1 to 7: answered

1. **Stale fill text:**
   * no "PP-01 to PP-08" is left on the three pages or in LAYER-STATUS (one remains in a `l3r2.yaml` round-history
     comment, which is not rendered);
   * the "PROVISIONAL ... once power_path_check is filed" paragraph is replaced by "The findings case (c) assumes closed
     ... restated from stream r11dep's record at the tip cd8720a1ab6e its accepted check names";
   * L3-C34, L3-C45 and the classification row name A-1 to C-9 at L3-C37 to C44 and C46 to C53;
   * the "None is ACCEPTED yet" comment is gone.
2. **S-127** is closed (above).
3. **L3-OD3** `1s4p` and `keep` carry "NOT SHOWN: no M1 figure is computed for it ...; on the circuit as drawn it inherits
   row L3-OD1's CANNOT MEET".
4. **both-kept** reads "NOT MET by at least 165.7 Wh".
5. **L3-OD6's reasoning** now rests on capacity and fit only (B1 above).
6. **The hold test** runs on an unfilled copy of `l3r2.yaml`, with no skip; it passes.
7. **The binding refuses an unlisted relied-on file.** My own test used a stand-in check reading "accepted: yes" with tip
   cd8720a1, listing only ENERGY-BASIS.md:
   * with an entry that also relies on `weather_basis.out`, `basis_binding.verify` refuses ("its check lists files by
     sha256 but not ... weather_basis.out, which this entry relies on");
   * `set_energy_basis.py --check-only` refuses the same;
   * an entry relying on the listed record alone verifies.

## Minors (none blocks)

1. **Two renderer sentences still say the figures are held.** They are hard-coded in `render_l3r2.py`, predate this commit,
   and CHECK-4 missed them.
   * Both REQUIREMENTS-L3-R2.md and L3-RECONCILIATION.md, in the facts heading: "every M1 energy figure stays HELD for the
     checked second round (S-127)". The figures are filled from the checked basis and S-127 is closed.
   * L3-RECONCILIATION.md, in the open-items sentence: "the energy basis S-127 is layer 4's engineering input that rows
     L3-OD1, L3-OD2 and L3-OD4 wait on (D-22)". S-127 is closed and no row is held.
   * OWNER-DECISIONS-L3.md is free of both.
2. **L3-OD6's limitation names one lid only.** "17.5 to 22.0 percent ... (the QMX-out lid on the hypothetical path)"
   describes the 4S15P lid. With the build left to the owner, TYP also admits the tablet-out lid (14.0 to 19.2 percent at
   WE, `weather_basis.out` A), and the benchmark's own TYP store (4S13P) carries fewer still (ENERGY-BASIS.md section 8a).
   "14.0 to 22.0 percent across the lids the benchmark admits" would state it for both builds.
3. **S-127's closing commit on set 16.** Its `closed_by` names `9493847c`. On set 16, where the run order takes the
   branch's files instead of merging it, that commit is not in the set's history (checked: not an ancestor). Either merge
   `fnd/l3r2` or have the integrator name the integration commit, so the closure does not point outside main's history.
4. **Filing this chain.** CHECK-4 and this CHECK-5 are not yet filed under `records/l3r2/checks/` or named in
   `independent_check`. Condition 4 reads MET only once this check is filed byte for byte and named ACCEPTED.

## The delta scope after the owner's answers

1. **Minors 1 to 4** here, if not done before the owner reads the table.
2. **Each answer applied by its script with his words and date,** in an order the coherence rules allow:
   * row 6's build with row 2's lid, or the open conflict recorded;
   * row 6 before row 4's `adopt`;
   * the registry validating;
   * both renders passing `--check`;
   * the tests green on the decided state;
   * condition 1 reading MET only on a coherent set.
3. **L3-C26: the CONOPS and PRODUCT-BRIEF passages the decided rows change,** re-issued through layers 1 and 2 or as a
   change record, named in `definition_reissue`. It must differ from `baseline_definition` and be approved by an owner
   ruling that decides it, dated on or after the rows.
4. **The gates again on the integrated tree:**
   * `rules_lib` 0 errors;
   * the renders current;
   * `dryrun.py` byte identical;
   * no dashes, host names or paths;
   * H3 unchanged, with CONOPS and PRODUCT-BRIEF changed only by their own re-issue.
5. **A narrow independent check** of those deltas, named in `independent_check`.
