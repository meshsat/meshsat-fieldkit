accepted-so-far: no

# CHECK-3: narrow re-check of Layer 3 round 3b (item C27), the held energy figures excluded

MESHSAT-1357, 30 September 2026, about 04:25 CEST. **An AI check, not a qualified review.** The checker wrote none of
L3-R2.

**Scope.** Branch `fnd/l3r2` at `6b2e4035` (confirmed), one commit on `325859b5`. Judged, on `git diff 325859b5..6b2e4035`,
against:
* CHECK-2's B1 to B4 and m1 to m8;
* owner rulings D-24 and D-25.

The energy figures are HELD and out of scope.

**Why "no".** Round 3b closes all four of CHECK-2's blocking items and all eight minors. D-24 and D-25 are carried
faithfully. One new blocking item remains, found while dry-running the fill procedure: **the energy basis's accepted check
is not bound to the files filed.** With the checks that exist today, the prepared path fills figures that no accepted check
covered. This defeats the D-22 hold. The fix is small.

## What was run (throwaway shared clone at `6b2e4035`, `int16-evidence-e5322674.tar` installed; removed afterwards)

* **Gates:**
  * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings.
  * `rules_render.py --requirements --check`: current.
  * `render_l3r2.py --check`: 3 pages, 0 out of date.
  * `dryrun.py`: rerun byte identical.
  * `run.py test_requirements test_l3r2`: **87 passed**, 0 failed.
* **Merge with main:** clean (merge-tree).
* **Text rules** on the 3194 added lines:
  * 0 lines with U+2013 or U+2014;
  * 0 host names or paths;
  * CONOPS.md, PRODUCT-BRIEF.md and `v2/release/` unchanged against `325859b5` and against main.
* **Filed checks:** `checks/energy-basis-check-2/CHECK-2.md` is byte identical to its report ("accepted: yes", tip
  `ec415c09`).
* **Holds on the tree.** `od_l3_1 approve` is refused as "held (D-22, D-24)" and `od_l3_6 mean-day` as "held (D-23,
  D-24)".
* **My own paths on copies of the registry** (fixture tables, as `dryrun.py` does):
  * A: approve, qmx-out, 2s2p, then adopt **refused** ("L3-OD4 needs L3-OD6 decided first"). Then mean-day TYP and adopt
    are written.
  * A2: coverage 50 TYP, then adopt **refused** ("needs L3-OD6 answered mean-day; it was answered coverage").
  * B, row 6 first: coverage 50 WAB carried by qmx-out only, then tablet-out. **CFL-019 recorded.**
  * B, row 2 first: tablet-out, then coverage 50 WAB. **CFL-019 recorded.**
  * B3: the same target with qmx-out. No conflict.
  * B4: an unfilled fit. **REFUSED** ("its fits are not filled").
  * B5: qmx-outside with a qmx-out fit. No conflict.
* **Gate tests on the renderer's own functions:**
  * The B3 set with the tree's table unfilled: condition 1 **NOT MET** ("no filled fit").
  * With the table filled and a stand-in check reading "accepted: no": **NOT MET** ("its check reads 'accepted: no'").
  * With stand-ins reading "accepted: yes": MET.
  * The B1 set with the table filled: coherence **FAILS** (the tablet-out lid does not carry the target), and CFL-019
    stays open.
  * Re-issue of the baselined CONOPS approved by D-21: "no (it names the baselined text unchanged)".
  * A changed record approved by D-21: "no (D-21 does not decide the re-issue)".
  * A ruling that decides the re-issue, dated before the rows: "no (dated before the rulings ...)".
  * The same ruling dated after the rows: **yes**, condition 3 MET.
* **The fill procedure, on scratch copies of `l3r2.yaml`** (`--data`, `--root`) against `fnd/l3plane` `868c321f`:
  * `basis_reader.py` reads 868c321f: 8 sizing rows, 15 of 15 coverage rows, 27 reference-plane cases, 3 stores and 2
    allowances.
  * `set_energy_basis.py` refuses: CHECK-2 with `--tip 868c321f` ("does not name tip"); a stand-in "accepted: no"; a
    second run.
  * `fill_l3r2_from_basis.py` refuses with no basis named, and refuses a second run ("basis_figures is filled").
  * The B1 path below is written.

## Blocking items

### B1. The energy basis's accepted check is not bound to the files filed, so the D-22 hold can lift on figures no check accepted

* **The tip is taken on trust.** `set_energy_basis.py` checks that the check's head names "tip `<tip>`" for the `--tip`
  given. It never compares the record or the outputs with that tip's files. `basis_ok()` (renderer) and
  `cond.basis_state()` do not read the tip at all: they verify the shas of whatever files are named and a first line
  reading "accepted: yes".
* **Run on a copy.**
  * The files: 868c321f's `ENERGY-BASIS.md`, `weather_basis.out` and `energy_basis.out`.
  * The check: the filed energy CHECK-2, which reads "accepted: yes" and checked tip `ec415c09`.
  * The call: `set_energy_basis.py --tip ec415c09`, which **wrote** `energy_basis`.
  * Then `fill_l3r2_from_basis.py` **wrote** the 8 rows of L3-OD6 and `basis_figures` from 868c321f.
* **The figures differ from the checked issue.** `git diff ec415c09 868c321f` of `weather_basis.out` section B:
  * 50 % TYP: 4S27P and 132 cells at ec415c09, against 4S26P and 128 cells at 868c321f;
  * 80 % WAB: 4S42P and 192 cells, against 4S40P and 184 cells.
* **Why this is the live path.**
  * `basis_reader.py` refuses the checked issue's own format ("weather_basis.out B's sizing header occurs 0 times" on
    ec415c09's output).
  * The only accepted check today is of ec415c09.
  * The one check of 4e9fa869 (which carries 868c321f's minors), `_reports/chk-energy/CHECK-3.md`, reads "accepted: no".
  * So with the checks that exist, the only way through the prepared procedure files figures that no accepted check
    covered.
* **The same gap applies** to `power_path_check`.
* **Fix.**
  * `set_energy_basis.py` requires each named file to be byte identical to `git show <tip>:<path>`, and records the tip.
  * The hold and the gate re-verify that from the recorded tip.
  * The same for `power_path_check`.
  * A test with a mismatched tip.

## CHECK-2's items, as re-checked

| CHECK-2 | State |
|---|---|
| **B1** benchmark by row order | **Closed.** `od_l3_4 adopt` requires `L3-OD6:mean-day` (`cond.require`), and `coherent()` reads adopt without mean-day as incoherent. Paths A and A2 are refused |
| **B2** store against weather basis | **Closed.** The table has **eight rows** (mean-day, 50, 80, 95 by TYP and WAB), each with per-lid `fits`. `od_l3_2` and `od_l3_6` record an open conflict in either order when the lid is not listed. `coherent()` reads an unfilled fit, or a lid not carried, as incoherent. L3-C32 and LAYER-STATUS now state only the enforced rules and add "a combination these rules do not name is not claimed coherent". Residual wording: minor 4 |
| **B3** gate on filed files | **Closed as asked:** a stand-in reading "accepted: no" and D-21 both fail, and the re-issue must differ from `baseline_definition` and be approved by a ruling that decides `definition_reissue`, dated on or after the rows. New gap: B1 above |
| **B4** CF-01 | **Closed.** CF-01, F-01 and LAYER-STATUS give 19.146 / 20.000 / 20.887 V steady state and the three brackets beside it: 19.101 V (divider 20 K warmer, an ASSUMPTION), 18.782 V (endurance limits, a bound) and 18.738 V (both). "narrows" is limited to the steady state ("with the brackets the low end is below 19.080 V"). How an M1 claim accounts for them: "stating them beside its result" (WEL a case beside, the rise a sensitivity). Residual: minor 2 |
| **m1** | **Closed.** qmx-outside now "changes the ruled connector plate ... and the sealed case, an enclosure constraint the owner decides (D-23)", in the option, the owner test and (c), classed REQUIREMENT |
| **m2** | **Closed.** Holds cite each row's `held_by` |
| **m3** | **Closed.** The dry-run chains are "examples, not recommendations", and no test calls a set "recommended" |
| **m4** | **Closed.** A qualifying evidence entry on REQ-072 names the s119 words as model cases on the mean day |
| **m5** | **Closed.** L3-OD1's consequences name the pass-line change |
| **m6** | **Closed.** `exact_token`, `exact_phrase` and `evidence_path` (on the tree, only the filed basis or its outputs) |
| **m7** | **Closed.** Targets 50, 80 and 95; builds TYP and WAB defined exactly; cells-only mass; both volumes; per-lid fits |
| **m8** | **Closed.** REQ-054 names the gain in dBd, and the limits are ERP "referenced to a half-wave dipole: a gain in dBi less 2.15 dB". That is correct. The source (appendix line 2761 item 4) gives "14 dBm ERP, 27 dBm on the 869.4 to 869.65 MHz sub-band", and the history records "no limit added or removed" |

## D-24 and D-25

* **Word for word.** I compared all 18 quotations of D-22 to D-25 in the registry with the file's blockquotes, in order:
  identical.
* **The four-case table** is on OWNER-DECISIONS-L3.md for L3-OD1, L3-OD2, L3-OD4 and L3-OD6:
  * (a) as drawn;
  * (a') "DERATED VARIANT ... fixes current-limit coordination only, not the other findings and not M1";
  * (b) "CONDITIONAL, not a sufficient solution ... INCONCLUSIVE until power_path_check";
  * (c) "HYPOTHETICAL ... rests on PP-01 to PP-08".
* **The 0.378 A comparison** stays closed (CF-02).
* **PP-01 to PP-08** are closure items L3-C37 to L3-C44, each with a measurable criterion and a layer, and marked
  "PROVISIONAL ... the final list comes from the electrical check" (L3-C45).
* **PP-02 (Kelvin)** is an implementation requirement: "not a defect of the drawn circuit (D-25: the A32 layout reading is
  tied to that revision ...)".
* **The owner-test column is on every row.** Each names its requirements and quantifies:
  * L3-OD1: 12 cells to 80 or 84 cells, and Wh;
  * L3-OD4: 1 or 3 degrees, and the push in N;
  * L3-OD6: HELD figures.
* **The REQ-015 9 V floor** is flagged ("a higher service floor would change REQ-015 and is the owner's", PP-03 and
  L3-C39).
* **No option is recommended on its energy balance.** L3-OD1 reads "No option is recommended as feasible on its idealised
  energy balance". L3-OD2, L3-OD4 and L3-OD6 are HELD. L3-OD3's recommendation is electrical, not energy.
* **No completion claim:** the gate reads NOT MET.

## Minors

1. **"Not yet checked" is stale.** PP-01 to PP-08 and CF-02 cite R11-DEPENDENCY.md at `4e9fa869` as "not yet checked". A
   check of it (`_reports/chk-energy/CHECK-3.md`, 03:50, "accepted: no") predates `6b2e4035` (04:09). r11dep's second issue
   `3ef5987e` (04:10) answers it. The provisional status stands; the wording should say "checked once, not accepted".
2. **REQ-072's supply range is not defined.** The acceptance prepared in `od_l3_1.py` says "with the charge bus anywhere in
   its supply range" without saying which: the steady-state range, with the three brackets stated beside the result, as
   CF-01 puts it. An engineer reading only REQ-072 cannot tell.
3. **PP-02's bench line has no pass threshold.** "The voltage across R11's pads against that at U2's pins 14 and 13 at a
   known current" gives no tolerance.
4. **Residual wording:**
   * LAYER-STATUS's appendix A.3 integrator line still calls the rows "coherent by construction";
   * the impacts table's layer 8 entry for REQ-072 still reads "board A's entry re-rate (L3-C34)", where L3-C34 is now the
     whole power path (D-24).
5. **`basis_reader.coverage()` does not check completeness.** It stops at the first non-matching line after a row, while
   `sizing`, `stores` and `reference_plane` do check. All 15 of 15 rows read at 868c321f.
6. **The REQ-015 owner case is not yet quantified.** It is flagged, but the floor a remedy would set and its effect on
   REQ-015 are not stated. That is due when PP-03's remedy is chosen.

## What the final delta check must cover once the figures are filled

1. **B1's binding fix** (files byte identical to the checked tip, re-verified by the hold and the gate, for
   `energy_basis` and `power_path_check`) and its test.
2. **The basis filed with an accepted check of exactly that tip.**
   * At this writing no accepted check covers 868c321f (the reader's format) or 06b8ecea (the fourth issue).
   * 06b8ecea leaves `weather_basis.out` and `energy_basis.out` unchanged and adds `three_cases.out`.
3. **`power_path_check`:** r11dep's checked issue and its accepted check filed. PP-01 to PP-08 restated from it (L3-C45),
   with minor 1's wording.
4. **The four-case table's (a'), (b) and (c) energy cells.** No fill script reads `three_cases.out`, so each figure the
   session writes must be traced to its line there and labelled (DERATED, CONDITIONAL or INCONCLUSIVE, HYPOTHETICAL). No
   figure through (c) may appear as demonstrated capability.
5. **`fill_l3r2_from_basis.py` run once and read back.**
   * L3-OD6's per-lid fits flag every option a lid cannot meet (at 868c321f, for example, the mean day in WAB fits the
     QMX-out lid only, and no coverage target fits any lid).
   * The rows' recommendations restated from checked figures with the corrections beside them, never on the idealised
     energy balance alone, and the benchmark not preselected.
6. **`od_l3_4.py`'s `BAND` table** from the filed basis at the supply range's low end with U3's 6.0 A bracket.
7. **CF-01 to CF-04 and F-01** re-cited to the filed, checked issue. REQ-072's supply range defined (minor 2).
8. **Minors 2 to 6.**
9. **The gates again, on the tree the owner will read** (main merged and re-rendered):
   * `rules_lib` 0 errors;
   * both renders pass `--check`;
   * the tests pass;
   * `dryrun.py` byte identical;
   * no dashes, host names or paths;
   * CONOPS, PRODUCT-BRIEF and H3 unchanged.
10. **This check recorded** in `independent_check`.
